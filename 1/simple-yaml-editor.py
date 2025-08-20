#!/usr/bin/env python3
"""
Simple YAML Editor - Minimal Offline Version
No external CDN dependencies - fully functional offline
"""

import os
import sys
import json
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

# No-op service worker endpoints to silence noisy 404s from some browsers/devtools
@app.route('/_static/out/browser/serviceWorker.js')
def service_worker_js():
    return app.response_class('/* offline noop service worker */', mimetype='application/javascript')

@app.route('/_static/out/browser/serviceWorker.js.map')
def service_worker_map():
    return app.response_class('{"version":3,"file":"serviceWorker.js","sources":[],"mappings":""}', mimetype='application/json')

# Global variables
current_file = None
current_content = None
last_saved_content = None
auto_save_thread = None
stop_auto_save = threading.Event()
backup_dir = Path(".blocked")

# Minimal HTML template - no external dependencies
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>YAML Editor - {{ filename }}</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: #f5f5f5;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
            transition: background 0.2s;
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
        .editor-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
            margin: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .editor-header {
            background: #34495e;
            color: white;
            padding: 10px 20px;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
        }
        #textEditor {
            flex: 1;
            padding: 0;
        }
        #textEditor textarea {
            width: 100%;
            height: 100%;
            border: none;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: none;
            outline: none;
            border-radius: 0 0 8px 8px;
        }
        .preview-panel {
            width: 400px;
            display: flex;
            flex-direction: column;
            background: white;
            margin: 10px 10px 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .preview-header {
            background: #27ae60;
            color: white;
            padding: 10px 20px;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
        }
        .preview-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .preview-content pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            line-height: 1.4;
            border: 1px solid #e9ecef;
            margin: 0;
        }
        .error {
            background: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .success {
            background: #27ae60;
            color: white;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .info {
            background: #3498db;
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
            <h1>{{ filename }} ({{ file_type }})</h1>
            <span class="save-status" id="saveStatus"></span>
        </div>
        <div class="buttons">
            <button onclick="saveFile()">💾 Save</button>
            <button onclick="validateContent()">✓ Validate</button>
            <label {{ 'style="display:none;"' if not is_docker else '' }}>
                <input type="checkbox" id="staticOnly"> Static only
            </label>
            <button onclick="testDocker()" {{ 'style="display:none;"' if not is_docker else '' }}>🐳 Test</button>
            <button onclick="loadBackup()">📁 Backup</button>
            <button onclick="formatContent()">🎨 Format</button>
        </div>
    </div>
    
    <div class="container">
        <div class="editor-panel">
            <div class="editor-header">
                📝 Editor - {{ file_type|upper }}
            </div>
            <div id="textEditor">
                <textarea id="textContent" placeholder="Edit your {{ file_type }} content here...">{{ initial_content }}</textarea>
            </div>
        </div>
        
        <div class="preview-panel">
            <div class="preview-header">
                👁️ Live Preview
            </div>
            <div class="preview-content">
                <div id="errorDiv"></div>
                <pre id="yamlOutput">{{ initial_content }}</pre>
            </div>
        </div>
    </div>

    <script>
        // Simple offline editor - no external dependencies
        var FILE_TYPE = '{{ file_type }}';
        var dirty = false;
        
        // Initialize editor
        window.addEventListener('load', function() {
            const textarea = document.getElementById('textContent');
            textarea.addEventListener('input', function() {
                dirty = true;
                updatePreview();
            });
            
            // Auto-save every 10 seconds
            setInterval(function() {
                if (dirty) {
                    saveFile(true);
                }
            }, 10000);
            
            updatePreview();
        });
        
        function updatePreview() {
            const content = document.getElementById('textContent').value;
            document.getElementById('yamlOutput').textContent = content || '# Empty file';
            validateContent();
        }
        
        function validateContent() {
            const content = document.getElementById('textContent').value;
            const errorDiv = document.getElementById('errorDiv');
            
            if (!content.trim()) {
                errorDiv.innerHTML = '<div class="info">File is empty</div>';
                return;
            }
            
            try {
                if (FILE_TYPE !== 'dockerfile') {
                    // Basic YAML validation
                    const lines = content.split('\\n');
                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i];
                        if (line.trim() && !line.trim().startsWith('#')) {
                            if (line.includes(':') && line.indexOf(':') > 0) {
                                const key = line.substring(0, line.indexOf(':')).trim();
                                if (!key || (key.includes(' ') && !key.startsWith('"') && !key.startsWith("'"))) {
                                    throw new Error(`Invalid key at line ${i + 1}: "${key}"`);
                                }
                            }
                        }
                    }
                }
                errorDiv.innerHTML = '<div class="success">✓ Syntax looks good</div>';
            } catch (e) {
                errorDiv.innerHTML = '<div class="error">Error: ' + e.message + '</div>';
            }
        }
        
        function saveFile(isAutoSave = false) {
            const content = document.getElementById('textContent').value;
            fetch('/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    content: content,
                    auto_save: isAutoSave
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const status = document.getElementById('saveStatus');
                    status.textContent = isAutoSave ? '✓ Auto-saved' : '✓ Saved';
                    dirty = false;
                    setTimeout(() => { status.textContent = ''; }, 3000);
                } else {
                    showError('Save failed: ' + data.error);
                }
            })
            .catch(err => showError('Save failed: ' + err.message));
        }
        
        function testDocker() {
            const staticOnlyEl = document.getElementById('staticOnly');
            const staticOnly = staticOnlyEl ? staticOnlyEl.checked : false;
            fetch('/test-docker', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ static_only: staticOnly })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Docker test successful!\n' + data.output);
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
                    const backup = prompt('Available backups:\\n' + 
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
        
        function formatContent() {
            const content = document.getElementById('textContent').value;
            if (FILE_TYPE === 'dockerfile') {
                // Simple Dockerfile formatting
                const formatted = content.split('\\n')
                    .map(line => line.trim())
                    .filter(line => line)
                    .join('\\n');
                document.getElementById('textContent').value = formatted;
            } else {
                // Simple YAML formatting
                const lines = content.split('\\n');
                let formatted = '';
                let indent = 0;
                
                for (const line of lines) {
                    const trimmed = line.trim();
                    if (trimmed) {
                        if (trimmed.includes(':') && !trimmed.startsWith('-')) {
                            formatted += '  '.repeat(indent) + trimmed + '\\n';
                        } else {
                            formatted += '  '.repeat(indent) + trimmed + '\\n';
                        }
                    }
                }
                document.getElementById('textContent').value = formatted;
            }
            updatePreview();
            dirty = true;
        }
        
        function showError(message) {
            document.getElementById('errorDiv').innerHTML = 
                '<div class="error">' + message + '</div>';
        }
        
        // Cleanup on window close
        window.addEventListener('beforeunload', function(e) {
            if (dirty) {
                saveFile(false);
            }
        });
    </script>
</body>
</html>
'''

def create_backup(filepath):
    """Creates backup of file before editing"""
    if not os.path.exists(filepath):
        return
    
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(filepath)}.{timestamp}"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(filepath, backup_path)
    print(f"Backup created: {backup_path}")

def detect_file_type(filename):
    """Detects file type based on filename"""
    filename_lower = filename.lower()
    if 'docker-compose' in filename_lower:
        return 'docker-compose'
    elif 'dockerfile' in filename_lower:
        return 'dockerfile'
    else:
        return 'yaml'

@app.route('/')
def index():
    """Main page with editor"""
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
    """Saves file"""
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
    """Tests Docker configuration"""
    global current_file
    
    try:
        import subprocess
        data = request.get_json(silent=True) or {}
        static_only = bool(data.get('static_only'))

        path_lower = current_file.lower()
        # Compose files can be validated offline via 'config'
        if 'docker-compose' in path_lower:
            attempts = [
                ['docker', 'compose', '-f', current_file, 'config'],
                ['docker-compose', '-f', current_file, 'config']
            ]
            result = None
            for cmd in attempts:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    break
            if result and result.returncode == 0:
                return jsonify({'success': True, 'output': result.stdout[:800]})
            err = (result.stderr if result else 'docker compose not available')
            return jsonify({'success': False, 'error': err[:1200]})

        # Dockerfile: provide offline-friendly checks before building
        base_image = None
        try:
            with open(current_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith('#'):
                        continue
                    if s.upper().startswith('FROM '):
                        # FROM <image> [AS name]
                        parts = s.split()
                        if len(parts) >= 2:
                            base_image = parts[1]
                        break
        except Exception:
            base_image = None

        inspect = None
        if base_image:
            inspect = subprocess.run(['docker', 'image', 'inspect', base_image], capture_output=True, text=True)
            if static_only:
                if inspect.returncode != 0:
                    return jsonify({'success': False, 'error': f"Static check: base image '{base_image}' not present locally."})
                else:
                    return jsonify({'success': True, 'output': f"Static check OK. Base image '{base_image}' present locally. No build executed."})
        else:
            if static_only:
                return jsonify({'success': True, 'output': 'Static check OK. No base image detected. No build executed.'})

        # Attempt a quiet build without pulling new layers
        cmd = ['docker', 'build', '--pull=false', '-q', '-f', current_file, '.']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({'success': True, 'output': result.stdout[:800]})

        # Provide a clearer hint on common offline failures
        err = (result.stderr or '').strip()
        hint_lines = []
        if 'npm install' in err or 'failed to fetch' in err or 'temporary failure in name resolution' in err:
            hint_lines.append('This build step seems to require internet access (e.g., npm install).')
        if base_image and ('pull access denied' in err or 'not found' in err or 'manifest unknown' in err):
            hint_lines.append(f"The base image '{base_image}' may not be available locally while offline.")
        if hint_lines:
            err = ("\n".join(hint_lines) + "\n\n" + err)[:2000]
        return jsonify({'success': False, 'error': err})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/list-backups')
def list_backups():
    """Lists available backups"""
    try:
        if backup_dir.exists():
            backups = [f.name for f in backup_dir.iterdir() 
                      if f.name.startswith(os.path.basename(current_file))]
            backups.sort(reverse=True)
            return jsonify({'backups': backups[:10]})
        return jsonify({'backups': []})
    except Exception as e:
        return jsonify({'error': str(e), 'backups': []})

@app.route('/restore-backup', methods=['POST'])
def restore_backup():
    """Restores backup"""
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

def main():
    global current_file
    
    parser = argparse.ArgumentParser(description='Simple YAML/Dockerfile Editor')
    parser.add_argument('file', help='File to edit')
    parser.add_argument('--port', type=int, default=5000, help='Port for web server')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser')
    
    args = parser.parse_args()
    
    current_file = os.path.abspath(args.file)
    
    # Create backup
    create_backup(current_file)
    
    # Open browser
    if not args.no_browser:
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(f'http://localhost:{args.port}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    print(f"Starting Simple YAML Editor on http://localhost:{args.port}")
    print(f"Editing: {current_file}")
    print("Press Ctrl+C to save and exit")
    
    # Start Flask
    app.run(host='0.0.0.0', port=args.port, debug=False)

if __name__ == '__main__':
    main()
