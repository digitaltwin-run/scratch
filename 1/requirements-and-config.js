// Extended Blockly Block Definitions for YAML/Docker Editor
// This file contains additional block definitions for comprehensive YAML editing

// === DOCKER COMPOSE BLOCKS ===

// Networks block
Blockly.Blocks['compose_networks'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("network:")
            .appendField(new Blockly.FieldTextInput("frontend"), "NAME");
        this.appendStatementInput("CONFIG")
            .setCheck(null)
            .appendField("config:");
        this.setPreviousStatement(true, "Network");
        this.setNextStatement(true, "Network");
        this.setColour(230);
        this.setTooltip("Define a network");
    }
};

Blockly.Blocks['compose_depends_on'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("depends_on:")
            .appendField(new Blockly.FieldTextInput("db"), "SERVICE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
        this.setTooltip("Service dependency");
    }
};

Blockly.Blocks['compose_restart'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("restart:")
            .appendField(new Blockly.FieldDropdown([
                ["always", "always"],
                ["unless-stopped", "unless-stopped"],
                ["on-failure", "on-failure"],
                ["no", "no"]
            ]), "POLICY");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
    }
};

Blockly.Blocks['compose_command'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("command:")
            .appendField(new Blockly.FieldTextInput("npm start"), "CMD");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
    }
};

Blockly.Blocks['compose_healthcheck'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("healthcheck:");
        this.appendDummyInput()
            .appendField("  test:")
            .appendField(new Blockly.FieldTextInput("curl -f http://localhost/ || exit 1"), "TEST");
        this.appendDummyInput()
            .appendField("  interval:")
            .appendField(new Blockly.FieldTextInput("30s"), "INTERVAL");
        this.appendDummyInput()
            .appendField("  timeout:")
            .appendField(new Blockly.FieldTextInput("10s"), "TIMEOUT");
        this.appendDummyInput()
            .appendField("  retries:")
            .appendField(new Blockly.FieldNumber(3, 1), "RETRIES");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
    }
};

// === DOCKERFILE BLOCKS ===

Blockly.Blocks['dockerfile_expose'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("EXPOSE")
            .appendField(new Blockly.FieldTextInput("80"), "PORT");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_env'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("ENV")
            .appendField(new Blockly.FieldTextInput("NODE_ENV"), "KEY")
            .appendField("=")
            .appendField(new Blockly.FieldTextInput("production"), "VALUE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_copy'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("COPY")
            .appendField(new Blockly.FieldTextInput("./src"), "SOURCE")
            .appendField(new Blockly.FieldTextInput("/app/src"), "DEST");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_add'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("ADD")
            .appendField(new Blockly.FieldTextInput("./app.tar.gz"), "SOURCE")
            .appendField(new Blockly.FieldTextInput("/app/"), "DEST");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_workdir'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("WORKDIR")
            .appendField(new Blockly.FieldTextInput("/app"), "DIR");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_user'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("USER")
            .appendField(new Blockly.FieldTextInput("node"), "USER");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_arg'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("ARG")
            .appendField(new Blockly.FieldTextInput("VERSION"), "NAME")
            .appendField("=")
            .appendField(new Blockly.FieldTextInput("latest"), "DEFAULT");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_entrypoint'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("ENTRYPOINT")
            .appendField(new Blockly.FieldTextInput('["docker-entrypoint.sh"]'), "COMMAND");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_volume'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("VOLUME")
            .appendField(new Blockly.FieldTextInput("/data"), "PATH");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

Blockly.Blocks['dockerfile_label'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("LABEL")
            .appendField(new Blockly.FieldTextInput("version"), "KEY")
            .appendField("=")
            .appendField(new Blockly.FieldTextInput("1.0"), "VALUE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
    }
};

// === GENERIC YAML BLOCKS ===

Blockly.Blocks['yaml_object'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Object")
            .appendField(new Blockly.FieldTextInput("name"), "KEY");
        this.appendStatementInput("PROPERTIES")
            .setCheck(null)
            .appendField("properties:");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(290);
        this.setTooltip("YAML object/mapping");
    }
};

Blockly.Blocks['yaml_array'] = {
    init: function() {
        this.appendDummyInput()
            .appendField("Array")
            .appendField(new Blockly.FieldTextInput("items"), "KEY");
        this.appendStatementInput("ITEMS")
            .setCheck(null)
            .appendField("items:");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(290);
        this.setTooltip("YAML array/list");
    }
};

Blockly.Blocks['yaml_key_value'] = {
    init: function() {
        this.appendDummyInput()
            .appendField(new Blockly.FieldTextInput("key"), "KEY")
            .appendField(":")
            .appendField(new Blockly.FieldTextInput("value"), "VALUE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(290);
        this.setTooltip("Simple key-value pair");
    }
};

// === CODE GENERATORS ===

// Docker Compose Generators
Blockly.JavaScript['compose_networks'] = function(block) {
    var name = block.getFieldValue('NAME');
    var config = Blockly.JavaScript.statementToCode(block, 'CONFIG');
    return '  ' + name + ':\n' + (config || '    driver: bridge\n');
};

Blockly.JavaScript['compose_depends_on'] = function(block) {
    var service = block.getFieldValue('SERVICE');
    return '    depends_on:\n      - ' + service + '\n';
};

Blockly.JavaScript['compose_restart'] = function(block) {
    var policy = block.getFieldValue('POLICY');
    return '    restart: ' + policy + '\n';
};

Blockly.JavaScript['compose_command'] = function(block) {
    var cmd = block.getFieldValue('CMD');
    return '    command: ' + cmd + '\n';
};

Blockly.JavaScript['compose_healthcheck'] = function(block) {
    var test = block.getFieldValue('TEST');
    var interval = block.getFieldValue('INTERVAL');
    var timeout = block.getFieldValue('TIMEOUT');
    var retries = block.getFieldValue('RETRIES');
    return '    healthcheck:\n' +
           '      test: ["CMD", "' + test + '"]\n' +
           '      interval: ' + interval + '\n' +
           '      timeout: ' + timeout + '\n' +
           '      retries: ' + retries + '\n';
};

// Dockerfile Generators
Blockly.JavaScript['dockerfile_expose'] = function(block) {
    var port = block.getFieldValue('PORT');
    return 'EXPOSE ' + port + '\n';
};

Blockly.JavaScript['dockerfile_env'] = function(block) {
    var key = block.getFieldValue('KEY');
    var value = block.getFieldValue('VALUE');
    return 'ENV ' + key + '=' + value + '\n';
};

Blockly.JavaScript['dockerfile_copy'] = function(block) {
    var source = block.getFieldValue('SOURCE');
    var dest = block.getFieldValue('DEST');
    return 'COPY ' + source + ' ' + dest + '\n';
};

Blockly.JavaScript['dockerfile_add'] = function(block) {
    var source = block.getFieldValue('SOURCE');
    var dest = block.getFieldValue('DEST');
    return 'ADD ' + source + ' ' + dest + '\n';
};

Blockly.JavaScript['dockerfile_workdir'] = function(block) {
    var dir = block.getFieldValue('DIR');
    return 'WORKDIR ' + dir + '\n';
};

Blockly.JavaScript['dockerfile_user'] = function(block) {
    var user = block.getFieldValue('USER');
    return 'USER ' + user + '\n';
};

Blockly.JavaScript['dockerfile_arg'] = function(block) {
    var name = block.getFieldValue('NAME');
    var defaultValue = block.getFieldValue('DEFAULT');
    return 'ARG ' + name + '=' + defaultValue + '\n';
};

Blockly.JavaScript['dockerfile_entrypoint'] = function(block) {
    var command = block.getFieldValue('COMMAND');
    return 'ENTRYPOINT ' + command + '\n';
};

Blockly.JavaScript['dockerfile_volume'] = function(block) {
    var path = block.getFieldValue('PATH');
    return 'VOLUME [' + '"' + path + '"]\n';
};

Blockly.JavaScript['dockerfile_label'] = function(block) {
    var key = block.getFieldValue('KEY');
    var value = block.getFieldValue('VALUE');
    return 'LABEL ' + key + '="' + value + '"\n';
};

// Generic YAML Generators
Blockly.JavaScript['yaml_object'] = function(block) {
    var key = block.getFieldValue('KEY');
    var properties = Blockly.JavaScript.statementToCode(block, 'PROPERTIES');
    var indent = block.getIndent ? block.getIndent() : '';
    return indent + key + ':\n' + properties;
};

Blockly.JavaScript['yaml_array'] = function(block) {
    var key = block.getFieldValue('KEY');
    var items = Blockly.JavaScript.statementToCode(block, 'ITEMS');
    var indent = block.getIndent ? block.getIndent() : '';
    return indent + key + ':\n' + items;
};

Blockly.JavaScript['yaml_key_value'] = function(block) {
    var key = block.getFieldValue('KEY');
    var value = block.getFieldValue('VALUE');
    var indent = block.getIndent ? block.getIndent() : '  ';
    return indent + key + ': ' + value + '\n';
};

// === REQUIREMENTS.TXT ===
/*
Requirements for Python environment:

flask==2.3.2
flask-cors==4.0.0
PyYAML==6.0.1
watchdog==3.0.0

Optional for Docker testing:
docker==6.1.3
docker-compose==1.29.2
*/

// === PACKAGE.JSON for Node.js alternative ===
/*
{
  "name": "blockly-yaml-editor",
  "version": "1.0.0",
  "description": "Visual YAML/Dockerfile editor using Blockly",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "js-yaml": "^4.1.0",
    "chokidar": "^3.5.3",
    "open": "^9.1.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
*/