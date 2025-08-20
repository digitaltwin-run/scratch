// Generators for custom blocks

Blockly.JavaScript['mqtt_publish'] = function(block) {
  const value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_ATOMIC) || '""';
  const topic = block.getFieldValue('TOPIC');
  return `client.publish("${topic}", String(${value}));\n`;
};

// Webgen: HTML/CSS generators (emit calls to a collector API __WEB__)
Blockly.JavaScript['web_set_title'] = function(block){
  const t = Blockly.JavaScript.valueToCode(block, 'TITLE', Blockly.JavaScript.ORDER_ATOMIC) || '"Projekt"';
  return `__WEB__.setTitle(String(${t}));\n`;
};
Blockly.JavaScript['web_add_element'] = function(block){
  const tag = block.getFieldValue('TAG');
  const id = block.getFieldValue('ID') || '';
  const txt = Blockly.JavaScript.valueToCode(block, 'TEXT', Blockly.JavaScript.ORDER_ATOMIC) || '""';
  return `__WEB__.addElement("${tag}", ${JSON.stringify(id)}, String(${txt}));\n`;
};
Blockly.JavaScript['css_add_rule'] = function(block){
  const sel = block.getFieldValue('SEL') || 'body';
  const prop = block.getFieldValue('PROP') || 'color';
  const val = Blockly.JavaScript.valueToCode(block, 'VAL', Blockly.JavaScript.ORDER_ATOMIC) || '"black"';
  return `__WEB__.addCssRule(${JSON.stringify(sel)}, ${JSON.stringify(prop)}, String(${val}));\n`;
};

Blockly.JavaScript['mqtt_subscribe'] = function(block) {
  const topic = block.getFieldValue('TOPIC');
  return `client.subscribe("${topic}");\n`;
};

Blockly.JavaScript['set_element_text'] = function(block) {
  const element = block.getFieldValue('ELEMENT');
  const value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_ATOMIC) || '""';
  return `document.getElementById('${element}').innerText = ${value};\n`;
};
 
// Handle incoming MQTT message with topic filter and DO statements
Blockly.JavaScript['mqtt_on_message'] = function(block) {
  const filter = block.getFieldValue('TOPIC');
  const statements_do = Blockly.JavaScript.statementToCode(block, 'DO');
  const matcher = Blockly.JavaScript.provideFunction_('mqttTopicMatches', [
    'function ' + Blockly.JavaScript.FUNCTION_NAME_PLACEHOLDER_ + '(filter, topic) {',
    '  if (!filter) return false;',
    '  if (filter === topic) return true;',
    '  const f = String(filter).split("/");',
    '  const t = String(topic).split("/");',
    '  for (let i = 0, j = 0; i < f.length; i++, j++) {',
    '    const seg = f[i];',
    '    if (seg === "#") return true; // multi-level wildcard',
    '    if (seg === "+") { if (t[j] === undefined) return false; continue; } // single-level wildcard',
    '    if (seg !== t[j]) return false;',
    '  }',
    '  return f.length === t.length;',
    '}'
  ]);
  let code = '';
  code += `client.subscribe("${filter}");\n`;
  code += `client.on('message', (topic, message) => {\n`;
  code += `  if (${matcher}("${filter}", topic)) {\n`;
  // indent DO statements by two spaces
  code += (statements_do || '').split('\n').map(l => l ? '    ' + l : l).join('\n') + '\n';
  code += `  }\n`;
  code += `});\n`;
  return code;
};
