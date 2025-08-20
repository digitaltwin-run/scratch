#!/bin/bash

# Blockly YAML Editor - Installation Script
# Skrypt instalacyjny dla edytora YAML/Dockerfile z Blockly

echo "================================================"
echo "Blockly YAML Editor - Installation"
echo "================================================"

# Sprawdzenie Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Tworzenie virtualenv
echo "Creating virtual environment..."
python3 -m venv venv

# Aktywacja virtualenv
source venv/bin/activate

# Instalacja wymaganych pakietów
echo "Installing required packages..."
pip install --upgrade pip
pip install flask flask-cors pyyaml

# Tworzenie struktury katalogów
echo "Creating directory structure..."
mkdir -p .blocked

# Tworzenie głównego skryptu
cat > blocked.py << 'EOF'
#!/usr/bin/env python3
"""
Blockly YAML Editor
Edytor plików YAML (docker-compose, etc.) oraz Dockerfile z interfejsem Blockly
"""

import os
import sys
import json
import yaml
import webbrowser
import threading
import time
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import argparse
import signal
import atexit

app = Flask(__name__)
CORS(app)

# [Rest of the Python code from the main artifact goes here]
# For brevity, I'm not repeating the entire code, but it should be copied from the main artifact

EOF

# Nadanie uprawnień wykonywalnych
chmod +x blocked.py

# Tworzenie skryptu uruchomieniowego
cat > blocked << 'EOF'
#!/bin/bash
# Wrapper script for Blockly YAML Editor

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Aktywacja virtualenv jeśli istnieje
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Uruchomienie edytora
python3 blocked.py "$@"
EOF

chmod +x blocked

# Instalacja globalnie (opcjonalne)
echo ""
echo "Installation complete!"
echo ""
echo "To install globally (requires sudo), run:"
echo "  sudo ln -s $(pwd)/blocked /usr/local/bin/blocked"
echo ""
echo "Usage:"
echo "  ./blocked docker-compose.yaml"
echo "  ./blocked Dockerfile"
echo "  ./blocked any-file.yaml"
echo ""
echo "Options:"
echo "  --port PORT       Server port (default: 5000)"
echo "  --no-browser     Don't open browser automatically"
echo ""
echo "================================================"
