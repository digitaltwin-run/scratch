#!/bin/bash

# Quick fix for missing dependencies
echo "====================================="
echo "Blockly YAML Editor - Dependency Fix"
echo "====================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3 first:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "✅ Python $(python3 --version) found"
echo ""

# Function to check module
check_module() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

# Check what's missing
echo "Checking installed modules..."
MISSING=()

if check_module "flask"; then
    echo "✅ Flask is installed"
else
    echo "❌ Flask is missing"
    MISSING+=("flask")
fi

if check_module "flask_cors"; then
    echo "✅ Flask-CORS is installed"
else
    echo "❌ Flask-CORS is missing"
    MISSING+=("flask-cors")
fi

if check_module "yaml"; then
    echo "✅ PyYAML is installed"
else
    echo "❌ PyYAML is missing"
    MISSING+=("pyyaml")
fi

echo ""

# If all installed
if [ ${#MISSING[@]} -eq 0 ]; then
    echo "🎉 All dependencies are installed!"
    echo ""
    echo "You can now run:"
    echo "  ./blocked docker-compose.yml"
    echo "  ./blocked.py docker-compose.yml"
    echo "  python3 blocked.py docker-compose.yml"
    exit 0
fi

# Installation options
echo "Missing packages: ${MISSING[*]}"
echo ""
echo "Choose installation method:"
echo "1) Quick install (pip install --user)"
echo "2) Virtual environment (recommended)"
echo "3) System-wide (requires sudo)"
echo "4) Show manual commands and exit"
echo ""

read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Installing for current user..."
        pip3 install --user flask flask-cors pyyaml || pip install --user flask flask-cors pyyaml
        echo ""
        echo "✅ Installation complete!"
        ;;
        
    2)
        echo ""
        if [ -d "venv" ]; then
            echo "Virtual environment already exists, activating..."
            source venv/bin/activate
        else
            echo "Creating virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
        fi
        
        echo "Installing packages in venv..."
        pip install flask flask-cors pyyaml
        
        echo ""
        echo "✅ Installation complete!"
        echo ""
        echo "To use with venv:"
        echo "  source venv/bin/activate"
        echo "  python3 blocked.py docker-compose.yml"
        echo ""
        echo "Or use the wrapper script (auto-activates venv):"
        echo "  ./blocked docker-compose.yml"
        ;;
        
    3)
        echo ""
        echo "Installing system-wide (requires sudo)..."
        
        # Detect OS and use appropriate method
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            if command -v apt-get &> /dev/null; then
                # Debian/Ubuntu
                echo "Detected Debian/Ubuntu system"
                sudo apt-get update
                sudo apt-get install -y python3-flask python3-yaml python3-pip
                sudo pip3 install flask-cors
            elif command -v dnf &> /dev/null; then
                # Fedora/RHEL
                echo "Detected Fedora/RHEL system"
                sudo dnf install -y python3-flask python3-pyyaml python3-pip
                sudo pip3 install flask-cors
            elif command -v pacman &> /dev/null; then
                # Arch Linux
                echo "Detected Arch Linux system"
                sudo pacman -S python-flask python-yaml
                sudo pip3 install flask-cors
            else
                # Generic pip install
                sudo pip3 install flask flask-cors pyyaml || sudo pip install flask flask-cors pyyaml
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            echo "Detected macOS"
            pip3 install flask flask-cors pyyaml
        else
            # Other
            sudo pip3 install flask flask-cors pyyaml || sudo pip install flask flask-cors pyyaml
        fi
        
        echo ""
        echo "✅ Installation complete!"
        ;;
        
    4)
        echo ""
        echo "Manual installation commands:"
        echo ""
        echo "Option 1 - User install:"
        echo "  pip3 install --user flask flask-cors pyyaml"
        echo ""
        echo "Option 2 - Virtual environment:"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install flask flask-cors pyyaml"
        echo ""
        echo "Option 3 - System-wide:"
        echo "  sudo pip3 install flask flask-cors pyyaml"
        echo ""
        echo "Option 4 - Using apt (Debian/Ubuntu):"
        echo "  sudo apt-get install python3-flask python3-yaml python3-pip"
        echo "  pip3 install --user flask-cors"
        echo ""
        exit 0
        ;;
        
    *)
        echo "Invalid choice, exiting..."
        exit 1
        ;;
esac

# Final test
echo ""
echo "Testing installation..."
python3 -c "
try:
    import flask
    import yaml
    import flask_cors
    print('✅ All modules imported successfully!')
    print('')
    print('You can now run:')
    print('  ./blocked docker-compose.yml')
    print('  python3 blocked.py docker-compose.yml')
except ImportError as e:
    print(f'❌ Error: {e}')
    print('Please try running this script again or install manually')
"

echo ""
echo "====================================="