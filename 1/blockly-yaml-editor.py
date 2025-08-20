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

# Globalne zmienne
current_file = None
current_content = None
last_saved_content = None
auto_save_thread = None
stop_auto_save = threading.Event()
backup_dir = Path(".blocked")

# HTML template z Blockly
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Blockly YAML Editor - {{ filename }}</title>
    <script src="https://unpkg.com/blockly/blockly.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            margin: 0;
            font-size: 20px;
        }
        .buttons {
            display: flex;
            gap: 10px;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background: #2980b9;
        }
        .save-status {
            color: #2ecc71;
            font-size: 12px;
            margin-left: 10px;
        }
        .container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        #blocklyDiv {
            flex: 1;
            height: 100%;
        }
        .preview {
            width: 400px;
            background: #f5f5f5;
            padding: 20px;
            overflow-y: auto;
            border-left: 2px solid #ddd;
        }
        .preview h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .preview pre {
            background: white;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            line-height: 1.4;
        }
        .error {
            background: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; align-items: center;">
            <h1>Editing: {{ filename }}</h1>
            <span class="save-status" id="saveStatus"></span>
        </div>
        <div class="buttons">
            <button onclick="generateYAML()">Generate YAML</button>
            <button onclick="saveFile()">Save File</button>
            <button onclick="testDocker()" {{ 'style="display:none;"' if not is_docker else '' }}>Test Docker</button>
            <button onclick="loadBackup()">Load Backup</button>
            <button onclick="window.close()">Close</button>
        </div>
    </div>
    
    <div class="container">
        <div id="blocklyDiv"></div>
        <div class="preview">
            <h3>Preview</h3>
            <div id="errorDiv"></div>
            <pre id="yamlOutput">{{ initial_content }}</pre>
        </div>
    </div>

    <xml id="toolbox" style="display: none">
        {% if file_type == 'docker-compose' %}
        <category name="Docker Compose" colour="230">
            <block type="compose_root"></block>
            <block type="compose_service"></block>
            <block type="compose_image"></block>
            <block type="compose_ports"></block>
            <block type="compose_environment"></block>
            <block type="compose_volumes"></block>
            <block type="compose_networks"></block>
            <block type="compose_depends_on"></block>
            <block type="compose_restart"></block>
            <block type="compose_command"></block>
        </category>
        {% elif file_type == 'dockerfile' %}
        <category name="Dockerfile" colour="120">
            <block type="dockerfile_from"></block>
            <block type="dockerfile_run"></block>
            <block type="dockerfile_cmd"></block>
            <block type="dockerfile_expose"></block>
            <block type="dockerfile_env"></block>
            <block type="dockerfile_copy"></block>
            <block type="dockerfile_add"></block>
            <block type="dockerfile_workdir"></block>
            <block type="dockerfile_user"></block>
            <block type="dockerfile_arg"></block>
            <block type="dockerfile_entrypoint"></block>
            <block type="dockerfile_volume"></block>
            <block type="dockerfile_label"></block>
        </category>
        {% else %}
        <category name="YAML" colour="290">
            <block type="yaml_object"></block>
            <block type="yaml_array"></block>
            <block type="yaml_key_value"></block>
            <block type="yaml_string"></block>
            <block type="yaml_number"></block>
            <block type="yaml_boolean"></block>
        </category>
        {% endif %}
        <category name="Text" colour="160">
            <block type="text"></block>
            <block type="text_multiline"></block>
        </category>
        <category name="Logic" colour="210">
            <block type="logic_boolean"></block>
        </category>
        <category name="Math" colour="230">
            <block type="math_number"></block>
        </category>
    </xml>

    <script>
        // Definicje bloków dla Docker Compose
        Blockly.Blocks['compose_root'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("Docker Compose");
                this.appendStatementInput("SERVICES")
                    .setCheck("Service")
                    .appendField("services:");
                this.appendStatementInput("VOLUMES")
                    .setCheck("Volume")
                    .appendField("volumes:");
                this.appendStatementInput("NETWORKS")
                    .setCheck("Network")
                    .appendField("networks:");
                this.setColour(230);
                this.setTooltip("Root element of docker-compose.yaml");
            }
        };

        Blockly.Blocks['compose_service'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("Service")
                    .appendField(new Blockly.FieldTextInput("service_name"), "NAME");
                this.appendStatementInput("CONFIG")
                    .setCheck(null);
                this.setPreviousStatement(true, "Service");
                this.setNextStatement(true, "Service");
                this.setColour(230);
                this.setTooltip("Define a service");
            }
        };

        Blockly.Blocks['compose_image'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("image:")
                    .appendField(new Blockly.FieldTextInput("nginx:latest"), "IMAGE");
                this.setPreviousStatement(true, null);
                this.setNextStatement(true, null);
                this.setColour(230);
            }
        };

        Blockly.Blocks['compose_ports'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("ports:")
                    .appendField(new Blockly.FieldTextInput("8080:80"), "PORTS");
                this.setPreviousStatement(true, null);
                this.setNextStatement(true, null);
                this.setColour(230);
            }
        };

        Blockly.Blocks['compose_environment'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("environment:");
                this.appendDummyInput()
                    .appendField("  ")
                    .appendField(new Blockly.FieldTextInput("KEY"), "KEY")
                    .appendField(":")
                    .appendField(new Blockly.FieldTextInput("value"), "VALUE");
                this.setPreviousStatement(true, null);
                this.setNextStatement(true, null);
                this.setColour(230);
            }
        };

        Blockly.Blocks['compose_volumes'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("volume:")
                    .appendField(new Blockly.FieldTextInput("./data:/data"), "VOLUME");
                this.setPreviousStatement(true, null);
                this.setNextStatement(true, null);
                this.setColour(230);
            }
        };

        // Definicje bloków dla Dockerfile
        Blockly.Blocks['dockerfile_from'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("FROM")
                    .appendField(new Blockly.FieldTextInput("ubuntu:latest"), "IMAGE");
                this.setPreviousStatement(true, null);
                this.setNextStatement(true, null);
                this.setColour(120);
            }
        };

        Blockly.Blocks['dockerfile_run'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("RUN")
                    .appendField(new Blockly.FieldTextInput("apt-get update"), "COMMAND");
                this.setPreviousStatement(true, null);
                this.setNextStatement(true, null);
                this.setColour(120);
            }
        };

        Blockly.Blocks['dockerfile_cmd'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("CMD")
                    .appendField(new Blockly.FieldTextInput('["nginx", "-g", "daemon off;"]'), "COMMAND");
                this.setPreviousStatement(true, null);
                this.setNextStatement(true, null);
                this.setColour(120);
            }
        };

        // Generatory kodu
        Blockly.JavaScript['compose_root'] = function(block) {
            var services = Blockly.JavaScript.statementToCode(block, 'SERVICES');
            var volumes = Blockly.JavaScript.statementToCode(block, 'VOLUMES');
            var networks = Blockly.JavaScript.statementToCode(block, 'NETWORKS');
            
            var yaml = 'version: "3.8"\\n';
            if (services) {
                yaml += 'services:\\n' + services;
            }
            if (volumes) {
                yaml += 'volumes:\\n' + volumes;
            }
            if (networks) {
                yaml += 'networks:\\n' + networks;
            }
            return yaml;
        };

        Blockly.JavaScript['compose_service'] = function(block) {
            var name = block.getFieldValue('NAME');
            var config = Blockly.JavaScript.statementToCode(block, 'CONFIG');
            return '  ' + name + ':\\n' + config;
        };

        Blockly.JavaScript['compose_image'] = function(block) {
            var image = block.getFieldValue('IMAGE');
            return '    image: ' + image + '\\n';
        };

        Blockly.JavaScript['compose_ports'] = function(block) {
            var ports = block.getFieldValue('PORTS');
            return '    ports:\\n      - "' + ports + '"\\n';
        };

        // Inicjalizacja Blockly
        var workspace = Blockly.inject('blocklyDiv', {
            toolbox: document.getElementById('toolbox'),
            grid: {
                spacing: 20,
                length: 3,
                colour: '#ccc',
                snap: true
            },
            trashcan: true,
            zoom: {
                controls: true,
                wheel: true,
                startScale: 1.0,
                maxScale: 3,
                minScale: 0.3,
                scaleSpeed: 1.2
            }
        });

        // Auto-save co 10 sekund
        var autoSaveInterval = setInterval(function() {
            if (workspace.isDirty()) {
                saveFile(true);
            }
        }, 10000);

        function generateYAML() {
            try {
                var code = Blockly.JavaScript.workspaceToCode(workspace);
                document.getElementById('yamlOutput').textContent = code || '# Empty configuration';
                document.getElementById('errorDiv').innerHTML = '';
            } catch (e) {
                showError('Error generating YAML: ' + e.message);
            }
        }

        function saveFile(isAutoSave = false) {
            var code = Blockly.JavaScript.workspaceToCode(workspace);
            fetch('/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    content: code,
                    auto_save: isAutoSave
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    var status = document.getElementById('saveStatus');
                    status.textContent = isAutoSave ? '✓ Auto-saved' : '✓ Saved';
                    setTimeout(() => { status.textContent = ''; }, 3000);
                } else {
                    showError('Save failed: ' + data.error);
                }
            })
            .catch(error => {
                showError('Save error: ' + error);
            });
        }

        function testDocker() {
            fetch('/test-docker', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Docker test successful!\\n' + data.output);
                } else {
                    showError('Docker test failed: ' + data.error);
                }
            });
        }

        function loadBackup() {
            fetch('/list-backups')
            .then(response => response.json())
            .then(data => {
                if (data.backups && data.backups.length > 0) {
                    var backup = prompt('Available backups:\\n' + 
                        data.backups.join('\\n') + 
                        '\\n\\nEnter backup filename to restore:');
                    if (backup) {
                        fetch('/restore-backup', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({backup: backup})
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                location.reload();
                            } else {
                                showError('Restore failed: ' + data.error);
                            }
                        });
                    }
                } else {
                    alert('No backups available');
                }
            });
        }

        function showError(message) {
            document.getElementById('errorDiv').innerHTML = 
                '<div class="error">' + message + '</div>';
        }

        // Listener dla zmian w workspace
        workspace.addChangeListener(function(event) {
            if (event.type == Blockly.Events.BLOCK_CHANGE ||
                event.type == Blockly.Events.BLOCK_CREATE ||
                event.type == Blockly.Events.BLOCK_DELETE ||
                event.type == Blockly.Events.BLOCK_MOVE) {
                generateYAML();
            }
        });

        // Cleanup on window close
        window.addEventListener('beforeunload', function(e) {
            if (workspace.isDirty()) {
                saveFile(false);
            }
        });
    </script>
</body>
</html>
'''

def create_backup(filepath):
    """Tworzy backup pliku przed edycją"""
    if not os.path.exists(filepath):
        return
    
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(filepath)}.{timestamp}"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(filepath, backup_path)
    print(f"Backup created: {backup_path}")

def auto_save_worker():
    """Worker thread dla auto-save"""
    global current_content, last_saved_content, current_file
    
    while not stop_auto_save.is_set():
        time.sleep(10)
        if current_content and current_content != last_saved_content:
            try:
                with open(current_file, 'w') as f:
                    f.write(current_content)
                last_saved_content = current_content
                print(f"Auto-saved: {current_file}")
            except Exception as e:
                print(f"Auto-save error: {e}")

def detect_file_type(filename):
    """Wykrywa typ pliku na podstawie nazwy"""
    filename_lower = filename.lower()
    if 'docker-compose' in filename_lower:
        return 'docker-compose'
    elif 'dockerfile' in filename_lower:
        return 'dockerfile'
    else:
        return 'yaml'

@app.route('/')
def index():
    """Główna strona z edytorem Blockly"""
    global current_file
    
    initial_content = ""
    if os.path.exists(current_file):
        with open(current_file, 'r') as f:
            initial_content = f.read()
    
    file_type = detect_file_type(current_file)
    is_docker = file_type in ['docker-compose', 'dockerfile']
    
    return render_template_string(
        HTML_TEMPLATE, 
        filename=os.path.basename(current_file),
        initial_content=initial_content,
        file_type=file_type,
        is_docker=is_docker
    )

@app.route('/save', methods=['POST'])
def save():
    """Zapisuje plik"""
    global current_content, last_saved_content, current_file
    
    try:
        data = request.json
        content = data.get('content', '')
        is_auto_save = data.get('auto_save', False)
        
        current_content = content
        
        if not is_auto_save or content != last_saved_content:
            with open(current_file, 'w') as f:
                f.write(content)
            last_saved_content = content
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test-docker', methods=['POST'])
def test_docker():
    """Testuje konfigurację Docker"""
    global current_file
    
    try:
        import subprocess
        
        if 'docker-compose' in current_file.lower():
            result = subprocess.run(
                ['docker-compose', '-f', current_file, 'config'],
                capture_output=True,
                text=True
            )
        else:  # Dockerfile
            result = subprocess.run(
                ['docker', 'build', '-f', current_file, '--no-cache', '--dry-run', '.'],
                capture_output=True,
                text=True
            )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'output': result.stdout[:500]  # Pierwsze 500 znaków
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/list-backups')
def list_backups():
    """Lista dostępnych backupów"""
    try:
        if backup_dir.exists():
            backups = [f.name for f in backup_dir.iterdir() 
                      if f.name.startswith(os.path.basename(current_file))]
            backups.sort(reverse=True)
            return jsonify({'backups': backups[:10]})  # Ostatnie 10 backupów
        return jsonify({'backups': []})
    except Exception as e:
        return jsonify({'error': str(e), 'backups': []})

@app.route('/restore-backup', methods=['POST'])
def restore_backup():
    """Przywraca backup"""
    global current_file
    
    try:
        data = request.json
        backup_name = data.get('backup')
        backup_path = backup_dir / backup_name
        
        if backup_path.exists():
            shutil.copy2(backup_path, current_file)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Backup not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def cleanup():
    """Cleanup przy zamknięciu"""
    global stop_auto_save
    stop_auto_save.set()
    if auto_save_thread:
        auto_save_thread.join(timeout=2)

def signal_handler(sig, frame):
    """Handler dla Ctrl+C"""
    print("\\nSaving and closing...")
    cleanup()
    sys.exit(0)

def main():
    global current_file, auto_save_thread
    
    parser = argparse.ArgumentParser(description='Blockly YAML/Dockerfile Editor')
    parser.add_argument('file', help='File to edit (e.g., docker-compose.yaml)')
    parser.add_argument('--port', type=int, default=5000, help='Port for web server')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    
    args = parser.parse_args()
    
    current_file = os.path.abspath(args.file)
    
    # Tworzenie backupu
    create_backup(current_file)
    
    # Start auto-save thread
    auto_save_thread = threading.Thread(target=auto_save_worker, daemon=True)
    auto_save_thread.start()
    
    # Signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    # Otwieranie przeglądarki
    if not args.no_browser:
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(f'http://localhost:{args.port}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    print(f"Starting Blockly YAML Editor on http://localhost:{args.port}")
    print(f"Editing: {current_file}")
    print("Press Ctrl+C to save and exit")
    
    # Start Flask
    app.run(host='0.0.0.0', port=args.port, debug=False)

if __name__ == '__main__':
    main()
