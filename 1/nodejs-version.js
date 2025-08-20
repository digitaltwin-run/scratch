#!/usr/bin/env node

/**
 * Blockly YAML Editor - Node.js Version
 * Visual editor for YAML/Dockerfile files using Blockly
 */

const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const { exec } = require('child_process');
const open = require('open');

const app = express();
app.use(cors());
app.use(express.json());

// Global variables
let currentFile = null;
let currentContent = null;
let lastSavedContent = null;
let autoSaveInterval = null;

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length === 0) {
    console.error('Usage: blocked <file.yaml>');
    console.error('Example: blocked docker-compose.yaml');
    process.exit(1);
}

currentFile = path.resolve(args[0]);
const port = args.includes('--port') ? 
    parseInt(args[args.indexOf('--port') + 1]) : 5000;
const noBrowser = args.includes('--no-browser');

// Create backup directory
const backupDir = path.join(process.cwd(), '.blocked');
if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true });
}

// HTML Template
const getHTMLTemplate = (filename, initialContent, fileType, isDocker) => `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Blockly YAML Editor - ${filename}</title>
    <script src="https://unpkg.com/blockly/blockly.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: #f0f2f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 20px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .file-icon {
            width: 24px;
            height: 24px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .buttons {
            display: flex;
            gap: 10px;
        }
        button {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
            backdrop-filter: blur(10px);
        }
        button:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-1px);
        }
        .save-status {
            color: #4ade80;
            font-size: 12px;
            margin-left: 10px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .save-status.visible {
            opacity: 1;
        }
        .container {
            display: flex;
            flex: 1;
            overflow: hidden;
            gap: 2px;
            background: #ddd;
        }
        #blocklyDiv {
            flex: 1;
            background: white;
        }
        .preview {
            width: 450px;
            background: white;
            display: flex;
            flex-direction: column;
        }
        .preview-header {
            background: #f8f9fa;
            padding: 12px 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .preview-header h3 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
            color: #495057;
        }
        .preview-content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .preview pre {
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            border: 1px solid #e9ecef;
        }
        .error {
            background: #dc2626;
            color: white;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 12px;
            font-size: 14px;
        }
        .info {
            background: #3b82f6;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 12px;
        }
        .syntax-valid {
            background: #10b981;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
        }
        .syntax-invalid {
            background: #ef4444;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; align-items: center;">
            <h1>
                <div class="file-icon">📄</div>
                ${filename}
            </h1>
            <span class="save-status" id="saveStatus">✓ Saved</span>
        </div>
        <div class="buttons">
            <button onclick="generateYAML()">🔄 Generate</button>
            <button onclick="saveFile()">💾 Save</button>
            <button onclick="validateYAML()">✓ Validate</button>
            ${isDocker ? '<button onclick="testDocker()">🐳 Test Docker</button>' : ''}
            <button onclick="loadBackup()">📂 Backups</button>
            <button onclick="if(confirm('Save and close?')) { saveFile(); setTimeout(() => window.close(), 500); }">✕ Close</button>
        </div>
    </div>
    
    <div class="container">
        <div id="blocklyDiv"></div>
        <div class="preview">
            <div class="preview-header">
                <h3>Output Preview</h3>
                <div id="syntaxStatus"></div>
            </div>
            <div class="preview-content">
                <div id="errorDiv"></div>
                <pre id="yamlOutput">${initialContent || '# Start building your configuration'}</pre>
            </div>
        </div>
    </div>

    <xml id="toolbox" style="display: none">
        ${getToolboxXML(fileType)}
    </xml>

    <script>
        ${getBlockDefinitions()}
        ${getCodeGenerators()}
        
        // Initialize Blockly
        var workspace = Blockly.inject('blocklyDiv', {
            toolbox: document.getElementById('toolbox'),
            grid: {
                spacing: 20,
                length: 3,
                colour: '#e0e0e0',
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
            },
            theme: {
                'componentStyles': {
                    'workspaceBackgroundColour': '#ffffff',
                    'toolboxBackgroundColour': '#f8f9fa',
                    'toolboxForegroundColour': '#495057',
                    'flyoutBackgroundColour': '#f8f9fa',
                    'flyoutForegroundColour': '#495057',
                    'flyoutOpacity': 0.95,
                    'scrollbarColour': '#c0c0c0',
                    'scrollbarOpacity': 0.7
                }
            }
        });

        // Auto-save every 10 seconds
        setInterval(function() {
            if (workspace.isDirty()) {
                saveFile(true);
            }
        }, 10000);

        function generateYAML() {
            try {
                var code = Blockly.JavaScript.workspaceToCode(workspace);
                document.getElementById('yamlOutput').textContent = code || '# Empty configuration';
                document.getElementById('errorDiv').innerHTML = '';
                validateYAML();
            } catch (e) {
                showError('Error generating: ' + e.message);
            }
        }

        function validateYAML() {
            var content = document.getElementById('yamlOutput').textContent;
            fetch('/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ content: content })
            })
            .then(response => response.json())
            .then(data => {
                var status = document.getElementById('syntaxStatus');
                if (data.valid) {
                    status.innerHTML = '<span class="syntax-valid">✓ Valid</span>';
                } else {
                    status.innerHTML = '<span class="syntax-invalid">✗ Invalid</span>';
                    if (data.error) {
                        showError('Validation error: ' + data.error);
                    }
                }
            });
        }

        function saveFile(isAutoSave = false) {
            var code = document.getElementById('yamlOutput').textContent;
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
                    status.classList.add('visible');
                    setTimeout(() => { status.classList.remove('visible'); }, 3000);
                } else {
                    showError('Save failed: ' + data.error);
                }
            })
            .catch(error => {
                showError('Save error: ' + error);
            });
        }

        function testDocker() {
            showInfo('Testing Docker configuration...');
            fetch('/test-docker', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('errorDiv').innerHTML = '';
                if (data.success) {
                    showInfo('✓ Docker test passed!\\n' + (data.output || ''));
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
                    var list = data.backups.map((b, i) => (i+1) + '. ' + b).join('\\n');
                    var choice = prompt('Available backups:\\n' + list + '\\n\\nEnter number to restore:');
                    if (choice && !isNaN(choice)) {
                        var backup = data.backups[parseInt(choice) - 1];
                        if (backup) {
                            restoreBackup(backup);
                        }
                    }
                } else {
                    alert('No backups available');
                }
            });
        }

        function restoreBackup(backup) {
            fetch('/restore-backup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ backup: backup })
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

        function showError(message) {
            document.getElementById('errorDiv').innerHTML = 
                '<div class="error">' + message + '</div>';
        }

        function showInfo(message) {
            document.getElementById('errorDiv').innerHTML = 
                '<div class="info">' + message + '</div>';
        }

        // Listen for workspace changes
        workspace.addChangeListener(function(event) {
            if (event.type !== Blockly.Events.UI) {
                generateYAML();
            }
        });

        // Save before closing
        window.addEventListener('beforeunload', function(e) {
            if (workspace.isDirty()) {
                saveFile(false);
                e.preventDefault();
                e.returnValue = '';
            }
        });

        // Initial generation
        generateYAML();
    </script>
</body>
</html>
`;

// Get toolbox XML based on file type
function getToolboxXML(fileType) {
    if (fileType === 'docker-compose') {
        return `
            <category name="Services" colour="230">
                <block type="compose_service"></block>
                <block type="compose_image"></block>
                <block type="compose_ports"></block>
                <block type="compose_environment"></block>
                <block type="compose_volumes"></block>
                <block type="compose_depends_on"></block>
                <block type="compose_restart"></block>
                <block type="compose_command"></block>
            </category>
            <category name="Networks & Volumes" colour="200">
                <block type="compose_network"></block>
                <block type="compose_volume_def"></block>
            </category>`;
    } else if (fileType === 'dockerfile') {
        return `
            <category name="Dockerfile" colour="120">
                <block type="dockerfile_from"></block>
                <block type="dockerfile_run"></block>
                <block type="dockerfile_copy"></block>
                <block type="dockerfile_workdir"></block>
                <block type="dockerfile_expose"></block>
                <block type="dockerfile_env"></block>
                <block type="dockerfile_cmd"></block>
                <block type="dockerfile_entrypoint"></block>
            </category>`;
    } else {
        return `
            <category name="YAML" colour="290">
                <block type="yaml_key_value"></block>
                <block type="yaml_object"></block>
                <block type="yaml_array"></block>
            </category>`;
    }
}

// Get block definitions JavaScript
function getBlockDefinitions() {
    return `
        // Docker Compose blocks
        Blockly.Blocks['compose_service'] = {
            init: function() {
                this.appendDummyInput()
                    .appendField("Service:")
                    .appendField(new Blockly.FieldTextInput("app"), "NAME");
                this.appendStatementInput("CONFIG")
                    .setCheck(null);
                this.setPreviousStatement(true, null);
                this.setNextStatement(true, null);
                this.setColour(230);
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
        
        // Add more block definitions here...
    `;
}

// Get code generators JavaScript
function getCodeGenerators() {
    return `
        Blockly.JavaScript['compose_service'] = function(block) {
            var name = block.getFieldValue('NAME');
            var config = Blockly.JavaScript.statementToCode(block, 'CONFIG');
            return '  ' + name + ':\\n' + config;
        };
        
        Blockly.JavaScript['compose_image'] = function(block) {
            var image = block.getFieldValue('IMAGE');
            return '    image: ' + image + '\\n';
        };
        
        // Add more generators here...
    `;
}

// Create backup
function createBackup() {
    if (!fs.existsSync(currentFile)) return;
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const backupName = `${path.basename(currentFile)}.${timestamp}`;
    const backupPath = path.join(backupDir, backupName);
    
    fs.copyFileSync(currentFile, backupPath);
    console.log(`Backup created: ${backupPath}`);
}

// Detect file type
function detectFileType(filename) {
    const lower = filename.toLowerCase();
    if (lower.includes('docker-compose')) return 'docker-compose';
    if (lower.includes('dockerfile')) return 'dockerfile';
    return 'yaml';
}

// Routes
app.get('/', (req, res) => {
    let initialContent = '';
    if (fs.existsSync(currentFile)) {
        initialContent = fs.readFileSync(currentFile, 'utf8');
    }
    
    const fileType = detectFileType(currentFile);
    const isDocker = fileType === 'docker-compose' || fileType === 'dockerfile';
    
    res.send(getHTMLTemplate(
        path.basename(currentFile),
        initialContent,
        fileType,
        isDocker
    ));
});

app.post('/save', (req, res) => {
    try {
        const { content, auto_save } = req.body;
        currentContent = content;
        
        if (!auto_save || content !== lastSavedContent) {
            fs.writeFileSync(currentFile, content);
            lastSavedContent = content;
        }
        
        res.json({ success: true });
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});

app.post('/validate', (req, res) => {
    try {
        const { content } = req.body;
        yaml.load(content);
        res.json({ valid: true });
    } catch (error) {
        res.json({ valid: false, error: error.message });
    }
});

app.post('/test-docker', (req, res) => {
    const cmd = currentFile.toLowerCase().includes('docker-compose')
        ? `docker-compose -f "${currentFile}" config`
        : `docker build -f "${currentFile}" --no-cache .`;
    
    exec(cmd, (error, stdout, stderr) => {
        if (error) {
            res.json({ success: false, error: stderr || error.message });
        } else {
            res.json({ success: true, output: stdout.slice(0, 500) });
        }
    });
});

app.get('/list-backups', (req, res) => {
    try {
        const files = fs.readdirSync(backupDir)
            .filter(f => f.startsWith(path.basename(currentFile)))
            .sort()
            .reverse()
            .slice(0, 10);
        res.json({ backups: files });
    } catch (error) {
        res.json({ backups: [], error: error.message });
    }
});

app.post('/restore-backup', (req, res) => {
    try {
        const { backup } = req.body;
        const backupPath = path.join(backupDir, backup);
        
        if (fs.existsSync(backupPath)) {
            fs.copyFileSync(backupPath, currentFile);
            res.json({ success: true });
        } else {
            res.json({ success: false, error: 'Backup not found' });
        }
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\\nSaving and closing...');
    if (currentContent && currentContent !== lastSavedContent) {
        fs.writeFileSync(currentFile, currentContent);
    }
    process.exit(0);
});

// Start server
createBackup();

app.listen(port, () => {
    console.log(`Blockly YAML Editor running on http://localhost:${port}`);
    console.log(`Editing: ${currentFile}`);
    console.log('Press Ctrl+C to save and exit');
    
    if (!noBrowser) {
        setTimeout(() => {
            open(`http://localhost:${port}`);
        }, 1000);
    }
});
