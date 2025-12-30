# MTG Arena Deck Monitor Daemon

A Python daemon that monitors the MTG Arena Player.log file and automatically exports deck information in multiple formats.

## Features

- **Automatic Monitoring**: Watches the MTG Arena Player.log file for changes
- **Multiple Export Formats**: 
  - JSON (structured data)
  - Plain text deck lists
  - MTGA import format
- **Incremental Parsing**: Only processes new log entries
- **Duplicate Detection**: Avoids re-exporting the same deck
- **Configurable**: YAML-based configuration
- **Flexible Monitoring**: Supports both file system events (watchdog) and polling modes

## Prerequisites

- Python 3.7+
- MTG Arena installed with "Detailed Logs" enabled

## Installation

1. **Navigate to the daemon directory**:
   ```bash
   cd mtg-arena-daemon
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the daemon**:
   ```bash
   cp config/daemon.yaml.example config/daemon.yaml
   ```

4. **Edit the configuration**:
   Open `config/daemon.yaml` and update the `log_file_path` to match your MTG Arena installation:
   
   **Windows default**:
   ```yaml
   log_file_path: "C:\\Users\\<YourUsername>\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log"
   ```

## Enable Detailed Logs in MTG Arena

For the daemon to work properly, you need to enable detailed logging in MTG Arena:

1. Open MTG Arena
2. Click the gear icon (⚙️) at the top right
3. Click "View Account"
4. Check "Detailed Logs (Plugin Support)"
5. Restart MTG Arena

## Usage

### Basic Usage

Run the daemon with the default configuration:

```bash
python daemon.py
```

### Custom Configuration

Run with a specific configuration file:

```bash
python daemon.py /path/to/config.yaml
```

### Running as a Background Service

**Linux/macOS**:
```bash
nohup python daemon.py > daemon.log 2>&1 &
```

**Windows**:
Use Task Scheduler or create a batch script to run the daemon on startup.

## Configuration

The daemon uses a YAML configuration file. Here are the main configuration options:

### Log File Path
```yaml
log_file_path: "C:\\Users\\<Username>\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log"
```

### Export Settings
```yaml
export_directory: "./exports"
export_format:
  json: true      # Export as JSON
  text: true      # Export as plain text
  mtga: true      # Export as MTGA import format
```

### Monitoring Options
```yaml
monitor:
  poll_interval: 2           # Seconds between polling (if not using watchdog)
  watch_enabled: true        # Use file system events if available
  parse_on_startup: true     # Parse existing log on startup
```

### Logging Options
```yaml
logging:
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "./logs/daemon.log"  # Log file path
  console: true              # Output to console
  max_size_mb: 10           # Max log file size before rotation
  backup_count: 5           # Number of backup log files
```

## Exported Files

Exported decks are saved in the configured export directory (default: `./exports`). Files are named using the pattern:

```
DeckName_DeckID_TIMESTAMP.extension
```

### Example Exports

- `Mono-Green-Ramp_abc123_20231215_143022.json`
- `Mono-Green-Ramp_abc123_20231215_143022.txt`
- `Mono-Green-Ramp_abc123_20231215_143022.mtga.txt`

## File Formats

### JSON Format
Structured data with full deck information:
```json
{
  "id": "abc123",
  "name": "Mono Green Ramp",
  "format": "standard",
  "main_deck": [
    {"card_id": 12345, "quantity": 4, "name": "Llanowar Elves"}
  ],
  "sideboard": [
    {"card_id": 67890, "quantity": 2, "name": "Heroic Intervention"}
  ]
}
```

### Text Format
Human-readable deck list:
```
Deck: Mono Green Ramp
Format: standard

Main Deck:
4 Llanowar Elves
4 Forest

Sideboard:
2 Heroic Intervention
```

### MTGA Format
Can be imported directly into MTG Arena:
```
Deck
4 Llanowar Elves
4 Forest

Sideboard
2 Heroic Intervention
```

## Troubleshooting

### Daemon doesn't detect decks

1. **Check log file path**: Ensure the path in your configuration matches your MTG Arena installation
2. **Enable detailed logs**: Make sure "Detailed Logs" is enabled in MTG Arena
3. **Check daemon logs**: Look at `logs/daemon.log` for error messages
4. **Test log file access**: Ensure the daemon has read access to the Player.log file

### "Watchdog not installed" warning

This is not an error. The daemon will fall back to polling mode, which works fine but is slightly less efficient.

To use file system events instead:
```bash
pip install watchdog
```

### File not found errors

- Verify the log file path in your configuration
- Make sure MTG Arena is installed and has been run at least once
- On Windows, ensure you're using the correct username in the path

### No decks exported

- Play a game or view decks in MTG Arena to generate log entries
- Check that `auto_export` is set to `true` in the configuration
- Look for errors in the daemon log file

## Integration with ManaScanner

This daemon is designed to work with the ManaScanner project. Exported deck files can be:

- Imported into ManaScanner's collection manager
- Used for deck analysis and tracking
- Shared with other deck-building tools
- Archived for historical tracking

## Development

### Project Structure
```
mtg-arena-daemon/
├── daemon.py           # Main daemon script
├── log_parser.py       # Log file parsing logic
├── deck_exporter.py    # Deck export functionality
├── requirements.txt    # Python dependencies
├── config/
│   └── daemon.yaml.example  # Example configuration
├── logs/               # Daemon logs (created at runtime)
└── exports/            # Exported decks (created at runtime)
```

### Running Tests

(Tests to be added in future updates)

```bash
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is part of ManaScanner and is available under the MIT License.

## Acknowledgments

- MTG Arena log format inspired by existing community tools
- Built to complement the ManaScanner ecosystem

## Support

For issues and questions:
- Open an issue on the [ManaScanner GitHub repository](https://github.com/WandWeb2/ManaScanner/issues)
- Check the [ManaScanner discussions](https://github.com/WandWeb2/ManaScanner/discussions)

---

**Note**: This daemon is not affiliated with or endorsed by Wizards of the Coast. MTG Arena and Magic: The Gathering are trademarks of Wizards of the Coast LLC.
