// Generators for custom blocks

Blockly.JavaScript['mqtt_publish'] = function(block) {
  const value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_ATOMIC) || '""';
  const topic = block.getFieldValue('TOPIC');
  return `client.publish("${topic}", String(${value}));\n`;
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
