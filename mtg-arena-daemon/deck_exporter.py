"""
Deck Exporter Module

This module handles exporting deck data to various formats (JSON, text, MTGA format).
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class DeckExporter:
    """Handles exporting deck data to various formats."""
    
    def __init__(self, export_dir: str):
        """
        Initialize the deck exporter.
        
        Args:
            export_dir: Directory to export decks to
        """
        self.logger = logging.getLogger(__name__)
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string for use as a filename.
        
        Args:
            name: The string to sanitize
            
        Returns:
            Sanitized filename string
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limit length
        if len(name) > 100:
            name = name[:100]
        
        return name
    
    def generate_filename(self, deck: Dict[str, Any], extension: str, 
                         timestamp_format: str = "%Y%m%d_%H%M%S") -> str:
        """
        Generate a filename for a deck export.
        
        Args:
            deck: Deck dictionary
            extension: File extension (without dot)
            timestamp_format: Format string for timestamp
            
        Returns:
            Generated filename
        """
        deck_name = self.sanitize_filename(deck.get('name', 'deck'))
        deck_id = deck.get('id', '')
        timestamp = datetime.now().strftime(timestamp_format)
        
        if deck_id:
            filename = f"{deck_name}_{deck_id}_{timestamp}.{extension}"
        else:
            filename = f"{deck_name}_{timestamp}.{extension}"
        
        return filename
    
    def export_json(self, deck: Dict[str, Any], filename: str = None) -> Path:
        """
        Export deck as JSON.
        
        Args:
            deck: Deck dictionary to export
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            filename = self.generate_filename(deck, 'json')
        
        file_path = self.export_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(deck, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported deck to JSON: {file_path}")
            return file_path
        
        except Exception as e:
            self.logger.error(f"Error exporting deck to JSON: {e}")
            raise
    
    def export_text(self, deck: Dict[str, Any], filename: str = None) -> Path:
        """
        Export deck as plain text decklist.
        
        Args:
            deck: Deck dictionary to export
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            filename = self.generate_filename(deck, 'txt')
        
        file_path = self.export_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"Deck: {deck['name']}\n")
                if deck.get('format'):
                    f.write(f"Format: {deck['format']}\n")
                if deck.get('description'):
                    f.write(f"Description: {deck['description']}\n")
                f.write(f"Exported: {deck.get('timestamp', '')}\n")
                f.write("\n")
                
                # Write commander (if any)
                if deck.get('commander'):
                    f.write("Commander:\n")
                    for card in deck['commander']:
                        card_name = card.get('name', f"Card ID: {card['card_id']}")
                        f.write(f"{card['quantity']} {card_name}\n")
                    f.write("\n")
                
                # Write main deck
                f.write("Main Deck:\n")
                for card in deck.get('main_deck', []):
                    card_name = card.get('name', f"Card ID: {card['card_id']}")
                    f.write(f"{card['quantity']} {card_name}\n")
                
                # Write sideboard
                if deck.get('sideboard'):
                    f.write("\nSideboard:\n")
                    for card in deck['sideboard']:
                        card_name = card.get('name', f"Card ID: {card['card_id']}")
                        f.write(f"{card['quantity']} {card_name}\n")
            
            self.logger.info(f"Exported deck to text: {file_path}")
            return file_path
        
        except Exception as e:
            self.logger.error(f"Error exporting deck to text: {e}")
            raise
    
    def export_mtga(self, deck: Dict[str, Any], filename: str = None) -> Path:
        """
        Export deck in MTGA import format.
        
        Args:
            deck: Deck dictionary to export
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            filename = self.generate_filename(deck, 'mtga.txt')
        
        file_path = self.export_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # MTGA format is simple: quantity cardname per line
                # Commander first (if any)
                if deck.get('commander'):
                    f.write("Commander\n")
                    for card in deck['commander']:
                        card_name = card.get('name', f"Card ID: {card['card_id']}")
                        f.write(f"{card['quantity']} {card_name}\n")
                    f.write("\n")
                
                # Main deck
                f.write("Deck\n")
                for card in deck.get('main_deck', []):
                    card_name = card.get('name', f"Card ID: {card['card_id']}")
                    f.write(f"{card['quantity']} {card_name}\n")
                
                # Sideboard
                if deck.get('sideboard'):
                    f.write("\nSideboard\n")
                    for card in deck['sideboard']:
                        card_name = card.get('name', f"Card ID: {card['card_id']}")
                        f.write(f"{card['quantity']} {card_name}\n")
            
            self.logger.info(f"Exported deck to MTGA format: {file_path}")
            return file_path
        
        except Exception as e:
            self.logger.error(f"Error exporting deck to MTGA format: {e}")
            raise
    
    def export_deck(self, deck: Dict[str, Any], 
                   formats: Dict[str, bool] = None) -> List[Path]:
        """
        Export deck in specified formats.
        
        Args:
            deck: Deck dictionary to export
            formats: Dictionary of format names and whether to export them
                    (e.g., {'json': True, 'text': True, 'mtga': False})
            
        Returns:
            List of paths to exported files
        """
        if formats is None:
            formats = {'json': True, 'text': True, 'mtga': True}
        
        exported_files = []
        
        if formats.get('json', False):
            try:
                path = self.export_json(deck)
                exported_files.append(path)
            except Exception as e:
                self.logger.error(f"Failed to export JSON: {e}")
        
        if formats.get('text', False):
            try:
                path = self.export_text(deck)
                exported_files.append(path)
            except Exception as e:
                self.logger.error(f"Failed to export text: {e}")
        
        if formats.get('mtga', False):
            try:
                path = self.export_mtga(deck)
                exported_files.append(path)
            except Exception as e:
                self.logger.error(f"Failed to export MTGA format: {e}")
        
        return exported_files
