# Minimal Offline YAML/Dockerfile Editor (Blockly – deprecated)

Ten katalog (`scratch/1/`) zawiera minimalny, całkowicie offline edytor YAML/Dockerfile oraz zdeprecjonowany legacy edytor Blockly.

- Co powinien robić projekt:
  - Edytować i testować pliki YAML/Dockerfile w 100% offline (bez CDN).
  - Udostępnić prosty UI: zapis/auto‑zapis, kopie zapasowe, przywracanie, walidację i formatowanie.
  - Test Docker: offline‑friendly sprawdzenie `docker compose config` oraz build Dockerfile bez pobierania (`--pull=false`) z jasnymi komunikatami.
  - Serwować lokalne zasoby frontendowe (Blockly/mqtt.js/CodeMirror) z katalogu `frontend/vendor/`.

- Co jest zrobione (2025-08-21):
  - Minimalny edytor offline: `simple-yaml-editor.py` (brak zależności CDN).
  - No‑op service worker route – brak 404 w logach.
  - Ulepszone komunikaty testu Docker w trybie offline (sprawdzanie obrazu bazowego, `--pull=false`, lepsze hinty).
  - Zdeprecjonowany `blocked.py` (legacy Blockly) – pokazuje stronę o przeniesieniu na edytor offline.
  - Frontend zvendorowany: `frontend/vendor/` kopiowany w Dockerfile frontendu; `frontend/index.html` używa plików lokalnych.
  - Dokumentacja uaktualniona.

- TODO (bieżące):
  1) Tryb „offline static check only” dla Dockerfile (pomiń build, tylko lint/weryfikacja FROM) – plan.
  2) Testy E2E dla edytora offline (save/restore/test-docker) – plan.
  3) Pakietowanie (np. `pipx`/`pyinstaller`) – plan.
  4) Bardziej szczegółowa walidacja YAML/Dockerfile – plan.

Szybki start (offline):

```bash
python3 1/simple-yaml-editor.py path/to/file.yaml --port 8082
# Dockerfile lub docker-compose.yaml też działa
```

Frontend (Nginx) offline: patrz `scratch/frontend/` – vendor libs w `frontend/vendor/`, port domyślnie 8080.

---

## Legacy: Blockly YAML Editor (oryginalna dokumentacja)

Visual editor for YAML files (docker-compose.yaml, etc.) and Dockerfiles using Google Blockly.

## Features

- 🎨 **Visual Block-Based Editing** - Drag and drop blocks to build configurations
- 🐳 **Docker Support** - Specialized blocks for docker-compose.yaml and Dockerfile
- 💾 **Auto-Save** - Automatically saves changes every 10 seconds
- 📂 **Backup System** - Creates backups before editing, stores in `.blocked/` directory
- ✅ **Validation** - Real-time YAML syntax validation
- 🧪 **Docker Testing** - Test Docker configurations directly from the editor
- 🔄 **Live Preview** - See generated YAML/Dockerfile in real-time

## Installation

### Python Version (Recommended)

1. **Clone or download the files:**
```bash
# Create directory
mkdir blockly-yaml-editor
cd blockly-yaml-editor

# Save the Python script as blocked.py
```

2. **Install dependencies:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install flask flask-cors pyyaml
```

3. **Make executable:**
```bash
chmod +x blocked.py
```

4. **Optional - Install globally:**
```bash
sudo ln -s $(pwd)/blocked.py /usr/local/bin/blocked
```

### Node.js Version (Alternative)

1. **Install dependencies:**
```bash
npm init -y
npm install express cors js-yaml open
```

2. **Save the Node.js script as `blocked.js`**

3. **Make executable:**
```bash
chmod +x blocked.js
```

## Usage

### Basic Usage

```bash
# Edit docker-compose.yaml
./blocked.py docker-compose.yaml

# Edit Dockerfile
./blocked.py Dockerfile

# Edit any YAML file
./blocked.py config.yaml
```

### Command Line Options

```bash
./blocked.py <file> [options]

Options:
  --port PORT       Server port (default: 5000)
  --no-browser     Don't open browser automatically
```

### Examples

```bash
# Use custom port
./blocked.py docker-compose.yaml --port 8080

# Don't auto-open browser
./blocked.py config.yaml --no-browser
```

## Editor Interface

### Main Areas

1. **Header Bar**
   - File name display
   - Save status indicator
   - Action buttons

2. **Blockly Workspace** (Left)
   - Drag blocks from toolbox
   - Connect blocks to build configuration
   - Right-click for block options

3. **Preview Panel** (Right)
   - Real-time YAML/Dockerfile preview
   - Syntax validation status
   - Error messages

### Available Blocks

#### Docker Compose Blocks
- **Service** - Define a service with name
- **Image** - Specify Docker image
- **Ports** - Map container ports
- **Environment** - Set environment variables
- **Volumes** - Mount volumes
- **Networks** - Configure networks
- **Depends On** - Service dependencies
- **Restart** - Restart policy
- **Command** - Override default command

#### Dockerfile Blocks
- **FROM** - Base image
- **RUN** - Execute commands
- **COPY/ADD** - Copy files
- **WORKDIR** - Set working directory
- **EXPOSE** - Expose ports
- **ENV** - Environment variables
- **CMD** - Default command
- **ENTRYPOINT** - Container entrypoint
- **USER** - Set user
- **VOLUME** - Define volumes
- **LABEL** - Add metadata

#### Generic YAML Blocks
- **Object** - YAML object/mapping
- **Array** - YAML list/sequence
- **Key-Value** - Simple key-value pair

### Keyboard Shortcuts

- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Delete` - Delete selected block
- `Ctrl+C` - Copy block
- `Ctrl+V` - Paste block

## Features in Detail

### Auto-Save
- Saves automatically every 10 seconds if changes detected
- Manual save with "Save" button
- Saves on browser/tab close

### Backup System
- Creates backup before opening file
- Backups stored in `.blocked/` directory
- Format: `filename.yaml.YYYYMMDD_HHMMSS`
- Load previous versions with "Backups" button

### Docker Testing
- **Docker Compose**: Validates configuration syntax
- **Dockerfile**: Performs dry-run build
- Results shown in preview panel

### YAML Validation
- Real-time syntax checking
- Visual indicators (✓ Valid / ✗ Invalid)
- Error messages with details

## Workflow Example

1. **Start editing:**
```bash
./blocked.py docker-compose.yaml
```

2. **Browser opens with editor**

3. **Drag blocks from toolbox:**
   - Drag "Service" block to workspace
   - Set service name to "web"
   - Add "Image" block inside service
   - Set image to "nginx:latest"
   - Add "Ports" block
   - Set ports to "80:80"

4. **Preview shows:**
```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
```

5. **Save and test:**
   - Click "Save" or wait for auto-save
   - Click "Test Docker" to validate
   - Click "Close" when done

## Troubleshooting

### Port Already in Use
```bash
# Use different port
./blocked.py file.yaml --port 8080
```

### Browser Doesn't Open
```bash
# Check default browser settings
# Or use --no-browser and open manually
```

### Docker Test Fails
- Ensure Docker is installed and running
- Check file syntax in preview
- Verify Docker daemon is accessible

### Can't Find Backups
- Check `.blocked/` directory exists
- Ensure write permissions in current directory

## File Structure

```
project/
├── blocked.py          # Main Python script
├── blocked.js          # Node.js alternative
├── .blocked/           # Backup directory
│   ├── docker-compose.yaml.20240120_143022
│   └── docker-compose.yaml.20240120_150534
├── docker-compose.yaml # Your file being edited
└── venv/              # Python virtual environment
```

## Requirements

### System Requirements
- Python 3.6+ OR Node.js 14+
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Docker (optional, for testing features)

### Python Dependencies
- Flask 2.3+
- Flask-CORS 4.0+
- PyYAML 6.0+

### Node.js Dependencies
- Express 4.18+
- cors 2.8+
- js-yaml 4.1+
- open 9.1+

## Security Notes

- Editor runs on localhost only by default
- No authentication (designed for local use)
- Backups are local only
- Files are saved with original permissions

## Contributing

Feel free to extend with:
- Additional block types
- More file format support
- Enhanced validation rules
- Custom themes
- Export/import workspace configurations

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues or questions:
1. Check this README
2. Verify all dependencies are installed
3. Ensure proper file permissions
4. Test with simple YAML file first

---

**Quick Start:**
```bash
# Install and run in 3 commands
pip install flask flask-cors pyyaml
wget [script_url] -O blocked.py
./blocked.py docker-compose.yaml
```

Enjoy visual YAML editing! 🎨🚀