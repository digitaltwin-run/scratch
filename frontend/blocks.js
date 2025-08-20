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
,
  {
    "type": "mqtt_on_message",
    "message0": "on MQTT message(topic %1) do %2",
    "args0": [
      { "type": "field_input", "name": "TOPIC", "text": "sensors/#" },
      { "type": "input_statement", "name": "DO" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 290,
    "tooltip": "Handler dla wiadomości MQTT z filtrem tematu (+, #)",
    "helpUrl": ""
  }
]);

// Additional Webgen blocks for nested elements
Blockly.defineBlocksWithJsonArray([
  {
    "type": "web_element_with_children",
    "message0": "element %1 id %2 text %3 class %4 style %5 children %6",
    "args0": [
      { "type": "field_dropdown", "name": "TAG", "options": [["div","div"],["section","section"],["h1","h1"],["p","p"],["span","span"]] },
      { "type": "field_input", "name": "ID", "text": "" },
      { "type": "input_value", "name": "TEXT" },
      { "type": "input_value", "name": "CLASS" },
      { "type": "input_value", "name": "STYLE" },
      { "type": "input_statement", "name": "CHILDREN" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 60,
    "tooltip": "Dodaje element z zagnieżdżonymi dziećmi (HTML)",
    "helpUrl": ""
  }
]);

// Webgen blocks (HTML/CSS project generation)
Blockly.defineBlocksWithJsonArray([
  {
    "type": "web_set_title",
    "message0": "set page title %1",
    "args0": [
      { "type": "input_value", "name": "TITLE" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 20,
    "tooltip": "Ustawia tytuł strony (HTML <title>)",
    "helpUrl": ""
  },
  {
    "type": "web_add_element",
    "message0": "add element %1 id %2 text %3 class %4 style %5",
    "args0": [
      { "type": "field_dropdown", "name": "TAG", "options": [["h1","h1"],["p","p"],["div","div"],["span","span"]] },
      { "type": "field_input", "name": "ID", "text": "" },
      { "type": "input_value", "name": "TEXT" },
      { "type": "input_value", "name": "CLASS" },
      { "type": "input_value", "name": "STYLE" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 45,
    "tooltip": "Dodaje element do <body> w generowanym HTML",
    "helpUrl": ""
  },
  {
    "type": "css_add_rule",
    "message0": "CSS rule selector %1 property %2 value %3",
    "args0": [
      { "type": "field_input", "name": "SEL", "text": "body" },
      { "type": "field_input", "name": "PROP", "text": "color" },
      { "type": "input_value", "name": "VAL" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Dodaje prostą regułę CSS",
    "helpUrl": ""
  },
  {
    "type": "css_rule_group",
    "message0": "CSS rule selector %1 declarations %2",
    "args0": [
      { "type": "field_input", "name": "SEL", "text": "body" },
      { "type": "input_statement", "name": "DECLS" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Reguła CSS z wieloma deklaracjami",
    "helpUrl": ""
  },
  {
    "type": "css_decl",
    "message0": "property %1 value %2",
    "args0": [
      { "type": "field_input", "name": "PROP", "text": "color" },
      { "type": "input_value", "name": "VAL" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 120,
    "tooltip": "Deklaracja CSS (własność: wartość)",
    "helpUrl": ""
  }
]);
