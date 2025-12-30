#!/bin/bash
# Quick Start Script for MTG Arena Daemon (Linux/macOS)

echo "MTG Arena Deck Monitor Daemon - Quick Start"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Check if we're in the right directory
if [ ! -f "daemon.py" ]; then
    echo "Error: daemon.py not found"
    echo "Please run this script from the mtg-arena-daemon directory"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Dependencies installed successfully"
echo ""

# Check if config exists
if [ ! -f "config/daemon.yaml" ]; then
    echo "Creating default configuration..."
    mkdir -p config
    
    # Check if example config exists
    if [ -f "config/daemon.yaml.example" ]; then
        cp config/daemon.yaml.example config/daemon.yaml
    else
        echo "Error: config/daemon.yaml.example not found"
        exit 1
    fi
    
    echo ""
    echo "⚠️  IMPORTANT: Please edit config/daemon.yaml and update the log_file_path"
    echo "   with your actual MTG Arena Player.log location"
    echo ""
    echo "Default Windows path:"
    echo "   C:\\Users\\<YourUsername>\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log"
    echo ""
    read -p "Press Enter to open the config file in the default editor..."
    ${EDITOR:-nano} config/daemon.yaml
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the daemon, run:"
echo "   python3 daemon.py"
echo ""
echo "For more information, see README.md"
echo ""
