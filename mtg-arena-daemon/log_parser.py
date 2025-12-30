"""
MTG Arena Player.log Parser

This module parses the MTG Arena Player.log file to extract deck information.
The log file contains JSON blocks with deck data that can be extracted and exported.
"""

import json
import re
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime


class LogParser:
    """Parser for MTG Arena Player.log files."""
    
    def __init__(self):
        """Initialize the log parser."""
        self.logger = logging.getLogger(__name__)
        self.last_position = 0
        
        # Common patterns for deck-related JSON blocks
        self.deck_patterns = [
            r'"GetDeckLists',
            r'"Deck\.GetDeckListsV3',
            r'"PlayerInventory\.GetPlayerDecks',
            r'"mainDeck"',
            r'"sideboard"',
        ]
    
    def extract_json_blocks(self, log_content: str) -> List[Dict[str, Any]]:
        """
        Extract JSON blocks from log content.
        
        Args:
            log_content: The raw log file content
            
        Returns:
            List of parsed JSON objects
        """
        json_blocks = []
        
        # Find all potential JSON blocks (objects starting with { and ending with })
        # This regex finds balanced braces
        brace_level = 0
        start_idx = -1
        
        for i, char in enumerate(log_content):
            if char == '{':
                if brace_level == 0:
                    start_idx = i
                brace_level += 1
            elif char == '}':
                brace_level -= 1
                if brace_level == 0 and start_idx != -1:
                    json_str = log_content[start_idx:i+1]
                    try:
                        # Try to parse as JSON
                        json_obj = json.loads(json_str)
                        json_blocks.append(json_obj)
                    except json.JSONDecodeError:
                        # Not valid JSON, skip
                        pass
                    start_idx = -1
        
        return json_blocks
    
    def is_deck_data(self, json_obj: Dict[str, Any]) -> bool:
        """
        Check if a JSON object contains deck data.
        
        Args:
            json_obj: Parsed JSON object
            
        Returns:
            True if the object contains deck data
        """
        # Check for common deck-related keys
        deck_keys = [
            'mainDeck', 'sideboard', 'deckId', 'name', 
            'decks', 'deckList', 'mainBoard'
        ]
        
        return any(key in json_obj for key in deck_keys)
    
    def extract_decks(self, json_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract deck information from a JSON object.
        
        Args:
            json_obj: Parsed JSON object potentially containing deck data
            
        Returns:
            List of deck dictionaries
        """
        decks = []
        
        # Handle different JSON structures
        if 'decks' in json_obj:
            # Multiple decks in one object
            decks_data = json_obj['decks']
            if isinstance(decks_data, list):
                decks.extend(decks_data)
            elif isinstance(decks_data, dict):
                decks.append(decks_data)
        elif 'mainDeck' in json_obj or 'mainBoard' in json_obj:
            # Single deck object
            decks.append(json_obj)
        
        return decks
    
    def parse_deck_list(self, deck_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a deck list into a standardized format.
        
        Args:
            deck_data: Raw deck data from log
            
        Returns:
            Standardized deck dictionary or None if invalid
        """
        try:
            deck = {
                'id': deck_data.get('id') or deck_data.get('deckId') or deck_data.get('deckID'),
                'name': deck_data.get('name') or deck_data.get('deckName') or 'Unnamed Deck',
                'format': deck_data.get('format') or 'unknown',
                'description': deck_data.get('description', ''),
                'main_deck': [],
                'sideboard': [],
                'commander': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # Parse main deck
            main_key = 'mainDeck' if 'mainDeck' in deck_data else 'mainBoard'
            if main_key in deck_data:
                main_deck = deck_data[main_key]
                if isinstance(main_deck, list):
                    for card in main_deck:
                        if isinstance(card, dict):
                            deck['main_deck'].append({
                                'card_id': card.get('cardId') or card.get('id'),
                                'quantity': card.get('quantity', 1),
                                'name': card.get('name', 'Unknown')
                            })
            
            # Parse sideboard
            if 'sideboard' in deck_data:
                sideboard = deck_data['sideboard']
                if isinstance(sideboard, list):
                    for card in sideboard:
                        if isinstance(card, dict):
                            deck['sideboard'].append({
                                'card_id': card.get('cardId') or card.get('id'),
                                'quantity': card.get('quantity', 1),
                                'name': card.get('name', 'Unknown')
                            })
            
            # Parse commander (for Commander format)
            if 'commandZoneGRPIds' in deck_data:
                commanders = deck_data['commandZoneGRPIds']
                if isinstance(commanders, list):
                    for card_id in commanders:
                        deck['commander'].append({
                            'card_id': card_id,
                            'quantity': 1,
                            'name': 'Unknown'
                        })
            
            return deck
            
        except Exception as e:
            self.logger.error(f"Error parsing deck: {e}")
            return None
    
    def parse_log_chunk(self, log_content: str, start_pos: int = 0) -> List[Dict[str, Any]]:
        """
        Parse a chunk of log content starting from a specific position.
        
        Args:
            log_content: The log file content
            start_pos: Starting position to parse from
            
        Returns:
            List of parsed decks
        """
        decks = []
        
        # Get the content from start_pos onwards
        chunk = log_content[start_pos:]
        
        # Extract JSON blocks
        json_blocks = self.extract_json_blocks(chunk)
        
        # Process each JSON block
        for json_obj in json_blocks:
            if self.is_deck_data(json_obj):
                # Extract deck(s) from this JSON object
                deck_list = self.extract_decks(json_obj)
                for deck_data in deck_list:
                    deck = self.parse_deck_list(deck_data)
                    if deck:
                        decks.append(deck)
        
        return decks
    
    def parse_file(self, file_path: str, from_position: int = 0) -> tuple[List[Dict[str, Any]], int]:
        """
        Parse the log file and extract decks.
        
        Args:
            file_path: Path to the Player.log file
            from_position: Position to start reading from (for incremental parsing)
            
        Returns:
            Tuple of (list of decks, new file position)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Seek to the last position
                f.seek(from_position)
                content = f.read()
                new_position = f.tell()
                
                # Parse the content
                decks = self.parse_log_chunk(content)
                
                self.logger.info(f"Parsed {len(decks)} deck(s) from log file")
                return decks, new_position
                
        except FileNotFoundError:
            self.logger.error(f"Log file not found: {file_path}")
            return [], from_position
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            return [], from_position
