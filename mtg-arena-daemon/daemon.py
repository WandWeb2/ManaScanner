#!/usr/bin/env python3
"""
MTG Arena Deck Monitor Daemon

This daemon monitors the MTG Arena Player.log file for deck changes
and automatically exports deck information in various formats.
"""

import sys
import time
import logging
import signal
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Try to import watchdog for file monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Falling back to polling mode.")
    # Create dummy base class if watchdog is not available
    class FileSystemEventHandler:
        """Dummy base class when watchdog is not available."""
        pass

from log_parser import LogParser
from deck_exporter import DeckExporter


class LogFileHandler(FileSystemEventHandler):
    """Handler for file system events on the log file."""
    
    def __init__(self, daemon):
        """
        Initialize the handler.
        
        Args:
            daemon: Reference to the daemon instance
        """
        self.daemon = daemon
    
    def on_modified(self, event):
        """Handle file modification event."""
        if not event.is_directory and event.src_path == str(self.daemon.log_file_path):
            self.daemon.logger.debug(f"Log file modified: {event.src_path}")
            self.daemon.process_log_file()


class MTGArenaDaemon:
    """Main daemon class for monitoring MTG Arena logs."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the daemon.
        
        Args:
            config_path: Path to configuration file
        """
        self.running = False
        self.observer = None
        self.config = self.load_config(config_path)
        self.setup_logging()
        
        self.logger.info("Initializing MTG Arena Deck Monitor Daemon")
        
        # Initialize components
        self.log_file_path = Path(self.config['log_file_path'])
        self.parser = LogParser()
        self.exporter = DeckExporter(self.config['export_directory'])
        
        # Track last file position for incremental parsing
        self.last_position = 0
        
        # Track exported decks to avoid duplicates
        self.exported_decks = set()
    
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if config_path is None:
            # Look for config in standard locations
            possible_paths = [
                Path("config/daemon.yaml"),
                Path("config/daemon.yml"),
                Path("daemon.yaml"),
                Path("daemon.yml"),
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                print(f"Loaded configuration from: {config_path}")
                return config
        else:
            # Return default configuration
            print("Using default configuration")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'log_file_path': str(Path.home() / "AppData/LocalLow/Wizards Of The Coast/MTGA/Player.log"),
            'export_directory': './exports',
            'export_format': {
                'json': True,
                'text': True,
                'mtga': True
            },
            'monitor': {
                'poll_interval': 2,
                'watch_enabled': True,
                'parse_on_startup': True
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/daemon.log',
                'console': True,
                'max_size_mb': 10,
                'backup_count': 5
            },
            'deck_export': {
                'auto_export': True,
                'include_sideboard': True,
                'include_metadata': True,
                'timestamp_format': '%Y%m%d_%H%M%S'
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        # Create logs directory
        log_file_path = Path(log_config.get('file', './logs/daemon.log'))
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        handlers = []
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=log_config.get('max_size_mb', 10) * 1024 * 1024,
            backupCount=log_config.get('backup_count', 5)
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)
        
        # Console handler
        if log_config.get('console', True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            handlers.append(console_handler)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            handlers=handlers
        )
        
        self.logger = logging.getLogger(__name__)
    
    def get_deck_id(self, deck: Dict[str, Any]) -> str:
        """
        Generate a unique identifier for a deck.
        
        Args:
            deck: Deck dictionary
            
        Returns:
            Unique deck identifier
        """
        deck_id = deck.get('id', '')
        deck_name = deck.get('name', '')
        main_count = len(deck.get('main_deck', []))
        
        # Create a simple hash based on deck id, name, and card count
        return f"{deck_id}_{deck_name}_{main_count}"
    
    def process_log_file(self):
        """Process the log file for new deck data."""
        try:
            # Parse log file from last position
            decks, new_position = self.parser.parse_file(
                str(self.log_file_path), 
                self.last_position
            )
            
            # Update position
            self.last_position = new_position
            
            # Export new decks
            if self.config['deck_export']['auto_export']:
                for deck in decks:
                    deck_id = self.get_deck_id(deck)
                    
                    # Check if we've already exported this deck
                    if deck_id not in self.exported_decks:
                        self.logger.info(f"New deck detected: {deck['name']}")
                        
                        # Export in configured formats
                        exported_files = self.exporter.export_deck(
                            deck, 
                            self.config['export_format']
                        )
                        
                        # Track exported deck
                        self.exported_decks.add(deck_id)
                        
                        self.logger.info(f"Exported {len(exported_files)} file(s) for deck: {deck['name']}")
                    else:
                        self.logger.debug(f"Deck already exported: {deck['name']}")
            
        except Exception as e:
            self.logger.error(f"Error processing log file: {e}", exc_info=True)
    
    def start_watchdog_monitor(self):
        """Start monitoring using watchdog (file system events)."""
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("Watchdog not available, cannot use file system monitoring")
            return False
        
        try:
            # Create observer
            self.observer = Observer()
            event_handler = LogFileHandler(self)
            
            # Watch the directory containing the log file
            watch_path = self.log_file_path.parent
            self.observer.schedule(event_handler, str(watch_path), recursive=False)
            self.observer.start()
            
            self.logger.info(f"Started file system monitoring on: {watch_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error starting watchdog monitor: {e}")
            return False
    
    def start_polling_monitor(self):
        """Start monitoring using polling (checking file periodically)."""
        poll_interval = self.config['monitor']['poll_interval']
        self.logger.info(f"Started polling mode (interval: {poll_interval}s)")
        
        while self.running:
            try:
                if self.log_file_path.exists():
                    self.process_log_file()
                else:
                    self.logger.warning(f"Log file not found: {self.log_file_path}")
                
                time.sleep(poll_interval)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in polling loop: {e}", exc_info=True)
                time.sleep(poll_interval)
    
    def start(self):
        """Start the daemon."""
        self.running = True
        
        self.logger.info("=" * 60)
        self.logger.info("MTG Arena Deck Monitor Daemon Started")
        self.logger.info(f"Log file: {self.log_file_path}")
        self.logger.info(f"Export directory: {self.config['export_directory']}")
        self.logger.info("=" * 60)
        
        # Check if log file exists
        if not self.log_file_path.exists():
            self.logger.warning(f"Log file not found: {self.log_file_path}")
            self.logger.warning("Daemon will continue to monitor for file creation...")
        
        # Parse existing log on startup if configured
        if self.config['monitor']['parse_on_startup'] and self.log_file_path.exists():
            self.logger.info("Parsing existing log file...")
            self.process_log_file()
        
        # Start monitoring
        use_watchdog = self.config['monitor']['watch_enabled'] and WATCHDOG_AVAILABLE
        
        if use_watchdog:
            if self.start_watchdog_monitor():
                # Keep the daemon running
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.logger.info("Received interrupt signal")
            else:
                # Fall back to polling
                self.start_polling_monitor()
        else:
            # Use polling mode
            self.start_polling_monitor()
    
    def stop(self):
        """Stop the daemon."""
        self.logger.info("Stopping MTG Arena Deck Monitor Daemon...")
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.logger.info("Daemon stopped")
    
    def signal_handler(self, signum, frame):
        """Handle system signals."""
        self.logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point."""
    # Parse command line arguments
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    # Create daemon
    daemon = MTGArenaDaemon(config_path)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, daemon.signal_handler)
    signal.signal(signal.SIGTERM, daemon.signal_handler)
    
    # Start daemon
    try:
        daemon.start()
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
