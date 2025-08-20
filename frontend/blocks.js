// Custom Blockly blocks (MQTT + UI)

Blockly.defineBlocksWithJsonArray([
  {
    "type": "mqtt_publish",
    "message0": "publish %1 to topic %2",
    "args0": [
      { "type": "input_value", "name": "VALUE" },
      { "type": "field_input", "name": "TOPIC", "text": "test/topic" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 230,
    "tooltip": "Publikuje wartość do MQTT",
    "helpUrl": ""
  },
  {
    "type": "mqtt_subscribe",
    "message0": "subscribe to topic %1",
    "args0": [
      { "type": "field_input", "name": "TOPIC", "text": "sensors/i2c/64" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 210,
    "tooltip": "Subskrybuje temat MQTT",
    "helpUrl": ""
  },
  {
    "type": "set_element_text",
    "message0": "set element %1 text to %2",
    "args0": [
      { "type": "field_input", "name": "ELEMENT", "text": "sensor-low" },
      { "type": "input_value", "name": "VALUE" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 65,
    "tooltip": "Zmienia tekst elementu w UI",
    "helpUrl": ""
  }
]);
