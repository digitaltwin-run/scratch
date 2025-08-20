#!/bin/bash

echo "====================================="
echo "Blockly YAML Editor - Update Script"
echo "====================================="
echo ""

# Backup existing files
echo "Creating backup of existing files..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup existing files if they exist
[ -f "blocked.py" ] && cp blocked.py "$BACKUP_DIR/"
[ -f "blockly-yaml-editor.py" ] && cp blockly-yaml-editor.py "$BACKUP_DIR/"
[ -f "blocked" ] && cp blocked "$BACKUP_DIR/"

echo "Backup created in: $BACKUP_DIR"
echo ""

# Update the wrapper script
echo "Updating wrapper script..."
cat > blocked << 'EOF'
#!/bin/bash
# Wrapper script for Blockly YAML Editor

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Aktywacja virtualenv jeśli istnieje
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Sprawdź który plik Python istnieje i użyj go
if [ -f "blocked.py" ]; then
    python3 blocked.py "$@"
elif [ -f "blockly-yaml-editor.py" ]; then
    python3 blockly-yaml-editor.py "$@"
else
    echo "Error: No Python script found (blocked.py or blockly-yaml-editor.py)"
    exit 1
fi
EOF

chmod +x blocked

# Since blockly-yaml-editor.py seems complete, let's copy it to blocked.py
echo "Updating Python scripts..."
if [ -f "blockly-yaml-editor.py" ]; then
    # blockly-yaml-editor.py exists and seems complete, copy it to blocked.py
    cp blockly-yaml-editor.py blocked.py
    echo "✓ blocked.py updated from blockly-yaml-editor.py"
else
    echo "⚠ blockly-yaml-editor.py not found, blocked.py needs manual update"
fi

# Make sure both Python scripts are executable
chmod +x blocked.py 2>/dev/null
chmod +x blockly-yaml-editor.py 2>/dev/null

# Check/Install dependencies
echo ""
echo "Checking Python dependencies..."

# Function to check if a Python module is installed
check_module() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

MISSING_DEPS=()

if ! check_module "flask"; then
    MISSING_DEPS+=("flask")
fi

if ! check_module "flask_cors"; then
    MISSING_DEPS+=("flask-cors")
fi

if ! check_module "yaml"; then
    MISSING_DEPS+=("pyyaml")
fi

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo "✅ All dependencies are installed"
else
    echo "Missing dependencies: ${MISSING_DEPS[*]}"
    echo ""
    read -p "Do you want to install missing dependencies? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "venv" ]; then
            source venv/bin/activate
            pip install flask flask-cors pyyaml
        else
            echo "Choose installation method:"
            echo "1) Install for current user (--user)"
            echo "2) Create virtual environment"
            echo "3) Skip installation"
            read -p "Enter choice [1-3]: " install_choice
            
            case $install_choice in
                1)
                    pip3 install --user flask flask-cors pyyaml
                    ;;
                2)
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install flask flask-cors pyyaml
                    echo "✅ Virtual environment created and packages installed"
                    echo "Note: The wrapper script will auto-activate venv"
                    ;;
                3)
                    echo "Skipping installation..."
                    ;;
            esac
        fi
    fi
fi

# Create .blocked directory for backups
mkdir -p .blocked

# Final check
echo ""
echo "====================================="
echo "Update Complete!"
echo "====================================="
echo ""
echo "Files updated:"
echo "  - blocked (wrapper script)"
echo "  - blocked.py (main Python script)"
if [ -f "blockly-yaml-editor.py" ]; then
    echo "  - blockly-yaml-editor.py (kept as backup)"
fi
echo ""
echo "To use the editor:"
echo "  ./blocked docker-compose.yml"
echo "  ./blocked Dockerfile"
echo "  ./blocked any-file.yaml"
echo ""
echo "Options:"
echo "  --port PORT      Use custom port (default: 5000)"
echo "  --no-browser     Don't auto-open browser"
echo ""

# Test if everything works
echo "Testing installation..."
if python3 -c "import flask, yaml, flask_cors" 2>/dev/null; then
    echo "✅ All modules import successfully"
else
    echo "⚠ Some modules may be missing. Run: pip install flask flask-cors pyyaml"
fi

echo ""
echo "Backup of old files saved in: $BACKUP_DIR"
echo "====================================="
