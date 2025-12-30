#!/usr/bin/env python3
"""
Example test/demo file for the MTG Arena Daemon

This file demonstrates the basic functionality of the daemon components.
"""

import json
from pathlib import Path
from log_parser import LogParser
from deck_exporter import DeckExporter


def create_sample_log():
    """Create a sample log file for testing."""
    sample_log = """
[2024-12-30 12:34:56] Game started
{"mainDeck":[{"cardId":70001,"quantity":4,"name":"Llanowar Elves"},{"cardId":70002,"quantity":4,"name":"Forest"},{"cardId":70003,"quantity":3,"name":"Elvish Archdruid"}],"sideboard":[{"cardId":70100,"quantity":2,"name":"Heroic Intervention"}],"id":"test-deck-001","name":"Mono Green Elves","format":"standard"}
[2024-12-30 12:35:00] Deck loaded
{"mainDeck":[{"cardId":80001,"quantity":4,"name":"Lightning Bolt"},{"cardId":80002,"quantity":4,"name":"Mountain"},{"cardId":80003,"quantity":3,"name":"Goblin Guide"}],"sideboard":[{"cardId":80100,"quantity":2,"name":"Rending Volley"}],"id":"test-deck-002","name":"Red Deck Wins","format":"standard"}
[2024-12-30 12:36:00] Game ended
"""
    return sample_log


def test_log_parser():
    """Test the log parser functionality."""
    print("=" * 60)
    print("Testing Log Parser")
    print("=" * 60)
    
    # Create parser
    parser = LogParser()
    
    # Create sample log content
    log_content = create_sample_log()
    
    # Parse the log
    decks = parser.parse_log_chunk(log_content)
    
    print(f"\nFound {len(decks)} deck(s):")
    for i, deck in enumerate(decks, 1):
        print(f"\n--- Deck {i} ---")
        print(f"Name: {deck['name']}")
        print(f"Format: {deck['format']}")
        print(f"Main Deck Cards: {len(deck['main_deck'])}")
        print(f"Sideboard Cards: {len(deck['sideboard'])}")
        
        print("\nMain Deck:")
        for card in deck['main_deck']:
            print(f"  {card['quantity']}x {card['name']}")
        
        if deck['sideboard']:
            print("\nSideboard:")
            for card in deck['sideboard']:
                print(f"  {card['quantity']}x {card['name']}")
    
    return decks


def test_deck_exporter(decks):
    """Test the deck exporter functionality."""
    print("\n" + "=" * 60)
    print("Testing Deck Exporter")
    print("=" * 60)
    
    # Create exporter
    export_dir = Path("/tmp/mtg-arena-test-exports")
    exporter = DeckExporter(str(export_dir))
    
    print(f"\nExport directory: {export_dir}")
    
    # Export each deck
    for deck in decks:
        print(f"\nExporting deck: {deck['name']}")
        
        # Export in all formats
        exported_files = exporter.export_deck(deck, {
            'json': True,
            'text': True,
            'mtga': True
        })
        
        print(f"Exported {len(exported_files)} file(s):")
        for file_path in exported_files:
            print(f"  - {file_path.name}")
    
    # List all exported files
    print("\n" + "=" * 60)
    print("Exported Files:")
    print("=" * 60)
    
    if export_dir.exists():
        for file_path in sorted(export_dir.iterdir()):
            if file_path.is_file():
                print(f"  {file_path.name} ({file_path.stat().st_size} bytes)")


def main():
    """Main test function."""
    print("\nMTG Arena Daemon - Component Test\n")
    
    # Test log parser
    decks = test_log_parser()
    
    # Test deck exporter
    if decks:
        test_deck_exporter(decks)
    else:
        print("\nNo decks found to export")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
