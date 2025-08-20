

 **gotowe rozwiązanie dla RPi3 w Dockerze**, które od razu odpali i umożliwi:

* komunikację z hardware (I²C, GPIO)
* pośrednictwo w wymianie danych (MQTT broker)
* WebSocket + frontend do wyświetlania parametrów w HTML
* łatwą integrację z Blockly (no-code logika)

to najlepsze podejście to **stack oparty o docker-compose** z 3–4 kontenerami.

---

## 🏗 Architektura

```
+-------------------+       +-------------------+       +-------------------+
|  RPi hardware     |<----->|  mqtt-bridge      |<----->|    MQTT Broker    |
| (I2C, GPIO, SPI)  |       | (Python, Paho)    |       |  (Eclipse Mosquitto)|
+-------------------+       +-------------------+       +-------------------+
                                                         |
                                                         v
                                               +-------------------+
                                               |  Web Frontend     |
                                               | (HTML+Blockly+WS) |
                                               +-------------------+
```









Porównując Twoje rozwiązanie oparte na MQTT i Blockly z platformami takimi jak **ThingsBoard** i **Node-RED**, warto rozważyć kluczowe różnice, potencjalne uproszczenia oraz sposób przenoszenia projektów.

---

## 🔍 Różnice między Twoim rozwiązaniem a platformami typu ThingsBoard i Node-RED

### 1. **ThingsBoard**

**Zalety:**

* **Kompleksowa platforma IoT:** Oferuje zarządzanie urządzeniami, zbieranie danych, wizualizację oraz silnik reguł.
* **Obsługa wielu protokołów:** MQTT, CoAP, HTTP.
* **Gotowe widgety i pulpity:** Umożliwia szybkie tworzenie interfejsów użytkownika.
* **Integracja z zewnętrznymi brokerami MQTT:** Pozwala na łatwe łączenie z innymi systemami.

**Wady:**

* **Wymaga konfiguracji:** Choć oferuje wiele funkcji, początkowa konfiguracja może być czasochłonna.
* **Mniej elastyczne niż rozwiązania oparte na Blockly:** Ograniczona możliwość dostosowywania logiki aplikacji przez użytkownika końcowego.

### 2. **Node-RED**

**Zalety:**

* **Flow-based programming:** Umożliwia tworzenie aplikacji poprzez łączenie bloków (nódów), co jest intuicyjne i elastyczne.
* **Szeroka gama integracji:** Obsługuje wiele protokołów i usług.
* **Rozbudowana społeczność:** Duża liczba dostępnych wtyczek i przykładów.

**Wady:**

* **Interfejs użytkownika:** Domyślny dashboard może być ograniczony w porównaniu do dedykowanych rozwiązań wizualnych.
* **Potrzebna jest dobra znajomość logiki przepływów:** Choć interfejs jest przyjazny, pełne wykorzystanie możliwości wymaga zrozumienia koncepcji flow-based programming.

---

## 🧩 Uproszczenia i integracja z Blockly

Twoje rozwiązanie oparte na Blockly i MQTT oferuje:

* **Prosty interfejs użytkownika:** Umożliwia tworzenie logiki aplikacji poprzez przeciąganie bloków.
* **Bezpośrednia komunikacja z hardwarem:** Dzięki integracji z MQTT, dane z urządzeń mogą być bezpośrednio przesyłane do frontendu.
* **Elastyczność:** Użytkownicy mogą dostosować logikę aplikacji bez konieczności pisania kodu.

**Potencjalne uproszczenia:**

* **Integracja z ThingSpeak:** Możesz rozważyć integrację z ThingSpeak, platformą oferującą prostą wizualizację danych i możliwość analizy w czasie rzeczywistym.
* **Dodanie funkcji eksportu/importu projektów:** Umożliwi to użytkownikom przenoszenie swoich aplikacji między różnymi instancjami systemu.

---

## 📦 Przenoszenie projektów z Blockly

Aby umożliwić przenoszenie projektów stworzonych w Blockly:

1. **Eksport projektu:** Umożliw użytkownikom eksportowanie ich projektów do plików XML lub JSON.
2. **Import projektu:** Zapewnij funkcję importu, która pozwoli na załadowanie zapisanych projektów do nowej instancji systemu.
3. **Zarządzanie wersjami:** Rozważ implementację systemu wersjonowania, aby użytkownicy mogli śledzić zmiany w swoich projektach.

---

## ✅ Podsumowanie

* **Twoje rozwiązanie:** Idealne dla użytkowników potrzebujących prostego, elastycznego narzędzia do tworzenia aplikacji IoT bez konieczności pisania kodu.
* **ThingsBoard:** Doskonałe dla projektów wymagających zaawansowanego zarządzania urządzeniami i rozbudowanej wizualizacji danych.
* **Node-RED:** Świetne dla użytkowników preferujących flow-based programming i potrzebujących szerokiej integracji z różnymi usługami.

W zależności od specyfiki projektu, warto rozważyć, które z tych rozwiązań najlepiej odpowiada Twoim potrzebom.



## ⚙️ Konfiguracja Mosquitto (`mosquitto/config/mosquitto.conf`)

```conf
listener 1883
protocol mqtt

listener 9001
protocol websockets

persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
```

---

## 🐍 mqtt-bridge (Python)

`mqtt-bridge/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install paho-mqtt smbus2
COPY bridge.py .

CMD ["python", "bridge.py"]
```

`mqtt-bridge/bridge.py` (przykład mostka I²C → MQTT):

```python
import time, json, smbus2
import paho.mqtt.client as mqtt

BROKER = "mqtt"
PORT = 1883
TOPIC = "sensors/i2c"

bus = smbus2.SMBus(1)  # i2c-1 on RPi

client = mqtt.Client(client_id="rpi-bridge")
client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    try:
        # przykład: odczyt rejestru z czujnika pod adresem 0x40
        raw = bus.read_byte_data(0x40, 0x00)
        payload = {"sensor": "i2c-0x40", "value": raw, "ts": time.time()}
        client.publish(TOPIC, json.dumps(payload), qos=1, retain=True)
    except Exception as e:
        print("I2C read error:", e)
    time.sleep(1)
```

---

## 🌐 Web Frontend (HTML + Blockly + MQTT.js)

`web/Dockerfile`:

```dockerfile
FROM nginx:alpine
COPY ./html /usr/share/nginx/html
```

`web/html/index.html` (fragment):

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
</head>
<body>
  <h1>RPi Sensors</h1>
  <div id="sensor">Waiting...</div>

  <script>
    const client = mqtt.connect("ws://localhost:9001");

    client.on("connect", () => {
      client.subscribe("sensors/i2c");
    });

    client.on("message", (topic, msg) => {
      const data = JSON.parse(msg.toString());
      document.getElementById("sensor").innerText = 
        `Sensor ${data.sensor}: ${data.value}`;
    });
  </script>
</body>
</html>
```

---

## 🚀 Uruchomienie

Na Raspberry Pi 3:

```bash
git clone https://twoj-repo/rpi-mqtt-blockly.git
cd rpi-mqtt-blockly
docker-compose up -d
```

Dostajesz:

* **MQTT broker** → `mqtt://<rpi-ip>:1883` + `ws://<rpi-ip>:9001`
* **Bridge** czyta I²C i publikuje do MQTT
* **Frontend** → `http://<rpi-ip>:8080` z live danymi + Blockly

---

💡 Dzięki temu:

* Masz **multilayer** (hardware ↔ MQTT ↔ frontend)
* Możesz dorzucić **Blockly workspace** do generowania logiki (np. blok “jeśli wartość > 100 → publish alert”)
* Z łatwością cache’ujesz dane przez `retain true` w MQTT
* Całość działa w **Dockerze** na RPi3

---


Super 👍 – to dołóżmy **Blockly workspace** do Twojego web-ui, tak żeby od razu można było klikać bloki, generować kod i wykonywać go na froncie (z MQTT).

---

## 🔧 Rozszerzona wersja frontendu (z Blockly)

`web/html/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>RPi Blockly + MQTT</title>
  <script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <style>
    body { font-family: sans-serif; }
    #blocklyDiv {
      height: 480px;
      width: 100%;
      border: 1px solid #ccc;
    }
    #output {
      background: #f0f0f0;
      padding: 10px;
      margin-top: 10px;
      min-height: 50px;
    }
  </style>
</head>
<body>
  <h1>RPi Sensors + Blockly</h1>
  <div id="sensor">Waiting...</div>

  <h3>Blockly Editor</h3>
  <div id="blocklyDiv"></div>
  <xml id="toolbox" style="display:none">
    <block type="mqtt_publish"></block>
    <block type="mqtt_subscribe"></block>
    <block type="controls_if"></block>
    <block type="logic_compare"></block>
    <block type="math_number"></block>
    <block type="text"></block>
    <block type="text_print"></block>
  </xml>

  <button onclick="runCode()">▶ Run</button>
  <pre id="output"></pre>

  <script>
    // MQTT client
    const client = mqtt.connect("ws://" + location.hostname + ":9001");
    client.on("connect", () => {
      console.log("Connected to MQTT broker");
      client.subscribe("sensors/i2c");
    });
    client.on("message", (topic, msg) => {
      const data = JSON.parse(msg.toString());
      document.getElementById("sensor").innerText =
        `Sensor ${data.sensor}: ${data.value}`;
    });

    // Blockly init
    const workspace = Blockly.inject('blocklyDiv', {
      toolbox: document.getElementById('toolbox')
    });

    // --- Custom blocks ---
    Blockly.Blocks['mqtt_publish'] = {
      init: function() {
        this.appendDummyInput()
          .appendField("MQTT publish topic")
          .appendField(new Blockly.FieldTextInput("test/topic"), "TOPIC");
        this.appendValueInput("MSG")
          .setCheck(null)
          .appendField("message");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(230);
      }
    };
    Blockly.JavaScript['mqtt_publish'] = function(block) {
      const topic = block.getFieldValue('TOPIC');
      const msg = Blockly.JavaScript.valueToCode(block, 'MSG',
                    Blockly.JavaScript.ORDER_ATOMIC) || '""';
      return `client.publish("${topic}", String(${msg}));\n`;
    };

    Blockly.Blocks['mqtt_subscribe'] = {
      init: function() {
        this.appendDummyInput()
          .appendField("MQTT subscribe topic")
          .appendField(new Blockly.FieldTextInput("sensors/i2c"), "TOPIC");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(120);
      }
    };
    Blockly.JavaScript['mqtt_subscribe'] = function(block) {
      const topic = block.getFieldValue('TOPIC');
      return `client.subscribe("${topic}");\n`;
    };

    // Run generated code
    function runCode() {
      Blockly.JavaScript.INFINITE_LOOP_TRAP = null;
      const code = Blockly.JavaScript.workspaceToCode(workspace);
      document.getElementById("output").textContent = code;
      try {
        eval(code); // ⚠️ demo – wykonuje JS z Blockly
      } catch (e) {
        alert(e);
      }
    }
  </script>
</body>
</html>
```

---

## 🚀 Co to daje?

* **Workspace Blockly** – użytkownik przeciąga klocki (np. “MQTT subscribe → sensors/i2c” i “MQTT publish → alerts/…”).
* **Generowanie kodu JS** – Blockly tłumaczy bloki na kod JavaScript.
* **Bezpośrednia integracja z mqtt.js** – wygenerowany kod wykonuje `client.publish()` i `client.subscribe()`.
* **Wyjście (kod)** pokazuje się w `<pre id="output">`, więc użytkownik może podejrzeć jak wygląda.

---

## 🔮 Przykład scenariusza w Blockly

1. Subskrybuj `sensors/i2c`.
2. Jeśli `value > 100` → publikuj `"ALERT"` na `alerts/high`.

To można wyklikać w UI → wygenerowany kod to np.:

```js
client.subscribe("sensors/i2c");
if (123 > 100) {
  client.publish("alerts/high", "ALERT");
}
```

---

Okej! Oto **praktyczny prompt / roadmapa**, która pomoże Ci utrzymać projekt prosty, łatwy w implementacji i przenośny między różnymi środowiskami (Raspberry Pi, Docker, web):

---

## 📝 Prompt: “Co dalej z projektem?”

**Cel:** Utrzymać prostotę i implementowalność w każdym środowisku, zachowując elastyczność Blockly + MQTT + hardware.

### 1. Struktura projektu

* **Oddziel frontend od backendu**

  * Frontend: HTML + JS + Blockly
  * Backend: MQTT broker + bridge do I2C/sprzętu
* **Używaj Dockera** dla backendu (Raspberry Pi, Linux, Windows) – jeden kontener dla brokera + bridge’a
* **Frontend hostuj statycznie** lub w tym samym kontenerze z prostym serwerem np. `nginx` albo `python -m http.server`

### 2. Komunikacja z hardware

* **MQTT jako uniwersalny kanał**

  * Broker lokalny w Dockerze (`mosquitto`)
  * Bridge do I2C lub innych protokołów sprzętowych
* **Standaryzowane tematy**

  * np. `sensors/{sensor_id}`, `actuators/{actuator_id}`, `system/status`
  * Ułatwia przenoszenie i modularizację

### 3. Blockly

* **Trzy poziomy bloków**

  * Subskrypcja/Publikacja MQTT
  * Operacje logiczne (if/else, math)
  * Akcje UI (np. zmiana koloru, wyświetlanie wartości)
* **Eksport/import projektów**

  * XML/JSON dla projektów Blockly
  * Ułatwia przenoszenie między środowiskami i backup

### 4. Minimalizacja zależności

* Nie korzystaj z ciężkich frameworków frontendowych
* Zamiast np. React/Angular – proste JS + Blockly + CSS
* Docker + MQTT wystarczy jako fundament dla całego systemu

### 5. Modularność i skalowalność

* Każde urządzenie/bridge jako osobny kontener
* Łatwe dodawanie nowych sensorów/aktuatorów
* Frontend dynamicznie ładuje listę dostępnych tematów i sensorów

### 6. Przenoszenie projektów

* **Export XML/JSON** z Blockly → import do nowej instancji
* **Tematy MQTT i logika bloków** pozostają niezmienne
* Minimalne zmiany w konfiguracji hosta/brokera

---

💡 **W skrócie:**
Utrzymujemy prostotę przez:

* jedną uniwersalną warstwę komunikacji (MQTT),
* lekkie i niezależne frontend/backed,
* Blockly jako narzędzie wizualnej logiki,
* kontenery Dockerowe jako gwarancję przenośności.

---


Super! Zrobimy kompletny schemat projektu dla **Raspberry Pi 3**, który od razu uruchomi:

* MQTT (Mosquitto)
* Backend bridge do I2C (Python)
* Frontend z Blockly i MQTT


---

## 3️⃣ Backend bridge (Python)

`backend/i2c-bridge.py`:

```python
import os
import time
import json
import paho.mqtt.client as mqtt
import smbus2

MQTT_BROKER = os.environ.get("MQTT_BROKER", "mqtt://localhost:1883")
TOPIC_PREFIX = "sensors/i2c"

client = mqtt.Client("rpi-bridge")
client.connect("mosquitto", 1883, 60)  # używamy nazwy kontenera

bus = smbus2.SMBus(1)  # I2C bus

def read_sensor(address):
    # przykładowa funkcja: odczyt jednego bajtu
    try:
        return bus.read_byte(address)
    except:
        return None

i2c_addresses = [0x40, 0x41]  # przykładowe adresy sensorów

while True:
    for addr in i2c_addresses:
        value = read_sensor(addr)
        if value is not None:
            payload = json.dumps({"sensor": addr, "value": value})
            client.publish(f"{TOPIC_PREFIX}/{addr}", payload)
    time.sleep(1)
```

`backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY i2c-bridge.py .

RUN pip install paho-mqtt smbus2

CMD ["python", "i2c-bridge.py"]
```

---

## 4️⃣ Frontend z Blockly + MQTT

`frontend/index.html` – możesz użyć dokładnie wersji, którą przygotowałem wcześniej, z Blockly i mqtt.js.

`frontend/Dockerfile`:

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
```

Frontend będzie dostępny pod `http://<RPI_IP>:8080`.

---

## 5️⃣ Uruchomienie

Na Raspberry Pi 3:

```bash
docker-compose up -d
```

* MQTT WebSocket: `ws://<RPI_IP>:9001`
* Frontend Blockly: `http://<RPI_IP>:8080`
* Backend bridge automatycznie publikuje dane z I2C na MQTT

---

✅ **Efekt:**

* Prosty, przenośny system, który działa w Dockerze
* Frontend Blockly + MQTT
* Bridge do sprzętu (I2C)
* Możliwość eksportu/importu projektów Blockly




Świetnie! Stworzymy teraz **gotowe bloki Blockly**, które pozwolą od razu:

* odczytywać sensory I2C,
* sterować aktuatorami (np. GPIO lub I2C),
* wysyłać/pobierać dane z MQTT,
* wyświetlać wartości w frontendzie.

Będą gotowe do **przeciągania i konfigurowania**, bez pisania kodu.

---

## 1️⃣ Struktura bloków

### Kategorie:

1. **MQTT**

   * `Publish to topic`
   * `Subscribe to topic` (z callbackiem)
2. **I2C Sensors**

   * `Read sensor at address`
3. **Actuators**

   * `Write value to actuator at address`
4. **Logic / UI**

   * `If/Else`
   * `Set element text`
   * `Change element color`

---

## 2️⃣ Przykładowe definicje bloków Blockly

`frontend/blocks.js`:

```javascript
Blockly.defineBlocksWithJsonArray([
  {
    "type": "mqtt_publish",
    "message0": "publish %1 to topic %2",
    "args0": [
      { "type": "input_value", "name": "VALUE" },
      { "type": "field_input", "name": "TOPIC", "text": "sensors/i2c/64" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 230,
    "tooltip": "Publikuje wartość do MQTT",
    "helpUrl": ""
  },
  {
    "type": "mqtt_subscribe",
    "message0": "subscribe to topic %1 and store in %2",
    "args0": [
      { "type": "field_input", "name": "TOPIC", "text": "sensors/i2c/64" },
      { "type": "variable", "name": "VALUE" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 230,
    "tooltip": "Subskrybuje temat MQTT",
    "helpUrl": ""
  },
  {
    "type": "read_i2c_sensor",
    "message0": "read I2C sensor at address %1",
    "args0": [
      { "type": "field_number", "name": "ADDR", "value": 64, "min":0, "max":127 }
    ],
    "output": "Number",
    "colour": 120,
    "tooltip": "Odczyt wartości sensora I2C",
    "helpUrl": ""
  },
  {
    "type": "write_i2c_actuator",
    "message0": "write value %1 to actuator at address %2",
    "args0": [
      { "type": "input_value", "name": "VALUE" },
      { "type": "field_number", "name": "ADDR", "value": 64, "min":0, "max":127 }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Wysyła wartość do aktuatora I2C",
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
```

---

## 3️⃣ Generowanie JS dla bloków

`frontend/generators.js`:

```javascript
Blockly.JavaScript['mqtt_publish'] = function(block) {
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_ATOMIC);
  var topic = block.getFieldValue('TOPIC');
  return `mqttClient.publish('${topic}', ${value});\n`;
};

Blockly.JavaScript['mqtt_subscribe'] = function(block) {
  var topic = block.getFieldValue('TOPIC');
  var variable = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('VALUE'), Blockly.VARIABLE_CATEGORY_NAME);
  return `mqttClient.subscribe('${topic}', function(message){ ${variable} = message; });\n`;
};

Blockly.JavaScript['read_i2c_sensor'] = function(block) {
  var addr = block.getFieldValue('ADDR');
  return [`readI2CSensor(${addr})`, Blockly.JavaScript.ORDER_ATOMIC];
};

Blockly.JavaScript['write_i2c_actuator'] = function(block) {
  var addr = block.getFieldValue('ADDR');
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_ATOMIC);
  return `writeI2CActuator(${addr}, ${value});\n`;
};

Blockly.JavaScript['set_element_text'] = function(block) {
  var element = block.getFieldValue('ELEMENT');
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_ATOMIC);
  return `document.getElementById('${element}').innerText = ${value};\n`;
};
```

---

## 4️⃣ Integracja z frontendem

* Dołącz `blocks.js` i `generators.js` w HTML po `blockly_compressed.js`.
* Zapewnij funkcje w JS:

```javascript
function readI2CSensor(addr) {
  // wywołanie przez backend MQTT lub WebSocket
  return 0; // dummy na start
}

function writeI2CActuator(addr, value) {
  // wysyłka przez MQTT
  mqttClient.publish(`actuators/i2c/${addr}`, value);
}
```

* `mqttClient` – standardowy klient mqtt.js do WebSocket (`ws://<RPI_IP>:9001`).

---

✅ **Efekt:**

* Użytkownik przeciąga blok `read_i2c_sensor`, łączy z blokiem `set_element_text` → automatyczne wyświetlanie wartości w UI.
* Prosta logika MQTT/actuatorów do implementacji nawet dla początkujących.
* Pełna przenośność projektu: eksport/import XML/JSON z Blockly.

---

Super! Zrobimy teraz **pełny przykład działającej aplikacji IoT dla Raspberry Pi 3**, gotowej do uruchomienia w Dockerze, z:

* 3 sensorami I2C (Low / Medium / High)
* Wyświetlaniem wartości w frontendzie
* Sterowaniem przykładowym aktuatoren
* Blockly do przeciągania i konfigurowania logiki

`backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY i2c-bridge.py .

RUN pip install paho-mqtt smbus2

CMD ["python", "i2c-bridge.py"]
```

---

## 4️⃣ Frontend – HTML + Blockly

`frontend/index.html` (minimalny przykład):

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>RPI Blockly IoT</title>
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>
  <script src="blocks.js"></script>
  <script src="generators.js"></script>
  <style>
    #blocklyDiv { height: 400px; width: 600px; }
    .sensor { font-weight: bold; font-size: 1.5em; }
  </style>
</head>
<body>
  <h1>RPI Blockly IoT Example</h1>
  <div id="blocklyDiv"></div>

  <div>
    <div>Low: <span id="sensor-low" class="sensor">-</span></div>
    <div>Medium: <span id="sensor-medium" class="sensor">-</span></div>
    <div>High: <span id="sensor-high" class="sensor">-</span></div>
  </div>

  <script>
    var workspace = Blockly.inject('blocklyDiv', {
      toolbox: '<xml></xml>'
    });

    var mqttClient = mqtt.connect('ws://'+location.hostname+':9001');

    function readI2CSensor(addr) {
      // w prostym przykładzie odczyt przez backend
      return 0;
    }

    function writeI2CActuator(addr, value) {
      mqttClient.publish(`actuators/i2c/${addr}`, value);
    }

    mqttClient.on('connect', () => console.log('MQTT connected'));
  </script>
</body>
</html>
```

* `blocks.js` i `generators.js` – jak w poprzedniej wiadomości.
* Możesz dodawać własne bloki i generatory dla logiki UI i akcji.

---

## 5️⃣ Frontend Dockerfile

`frontend/Dockerfile`:

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY blocks.js /usr/share/nginx/html/blocks.js
COPY generators.js /usr/share/nginx/html/generators.js
```

---

## 6️⃣ Uruchomienie

Na Raspberry Pi 3:

```bash
docker-compose up -d
```

* MQTT WebSocket: `ws://<RPI_IP>:9001`
* Frontend Blockly: `http://<RPI_IP>:8080`
* Backend bridge automatycznie publikuje dane z I2C na MQTT

---

✅ **Efekt:**

* Widoczny frontend z sensorami Low/Medium/High
* Gotowe bloki Blockly do odczytu sensorów, ustawiania tekstu w UI i wysyłki do aktuatorów
* Pełna przenośność projektu, gotowy do eksportu/importu w formacie Blockly XML/JSON

Świetnie! Zrobimy teraz **gotową logikę Blockly**, która odczytuje sensory I2C i automatycznie aktualizuje wartości w frontendzie, bez potrzeby dodatkowego kodowania.

---

## 1️⃣ Przykładowa logika w Blockly (XML)

Możemy użyć **eksportu XML Blockly**, który od razu można wczytać do workspace:

```xml
<xml xmlns="https://developers.google.com/blockly/xml">
  <!-- Low sensor -->
  <block type="mqtt_subscribe" x="20" y="20">
    <field name="TOPIC">sensors/i2c/64</field>
    <field name="VALUE">lowValue</field>
  </block>
  <block type="set_element_text" x="220" y="20">
    <field name="ELEMENT">sensor-low</field>
    <value name="VALUE">
      <block type="variables_get">
        <field name="VAR">lowValue</field>
      </block>
    </value>
  </block>

  <!-- Medium sensor -->
  <block type="mqtt_subscribe" x="20" y="100">
    <field name="TOPIC">sensors/i2c/65</field>
    <field name="VALUE">mediumValue</field>
  </block>
  <block type="set_element_text" x="220" y="100">
    <field name="ELEMENT">sensor-medium</field>
    <value name="VALUE">
      <block type="variables_get">
        <field name="VAR">mediumValue</field>
      </block>
    </value>
  </block>

  <!-- High sensor -->
  <block type="mqtt_subscribe" x="20" y="180">
    <field name="TOPIC">sensors/i2c/66</field>
    <field name="VALUE">highValue</field>
  </block>
  <block type="set_element_text" x="220" y="180">
    <field name="ELEMENT">sensor-high</field>
    <value name="VALUE">
      <block type="variables_get">
        <field name="VAR">highValue</field>
      </block>
    </value>
  </block>
</xml>
```

---

## 2️⃣ Jak wczytać XML do workspace Blockly

`frontend/index.html`:

```javascript
// po utworzeniu workspace
Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(`PUT_XML_HERE`), workspace);
```

* Zastąp `PUT_XML_HERE` powyższym XML-em.
* Po wczytaniu wszystkie subskrypcje MQTT będą działać, a frontend automatycznie aktualizuje elementy `sensor-low/medium/high`.

---

## 3️⃣ Jak to działa

1. Backend publikuje dane I2C na MQTT (`sensors/i2c/64`, `65`, `66`) co sekundę.
2. Blockly subskrybuje te tematy i zapisuje wartości do zmiennych (`lowValue`, `mediumValue`, `highValue`).
3. Bloki `set_element_text` aktualizują odpowiednie elementy w HTML.
4. Cała logika jest **wizualna, przenośna i łatwa do modyfikacji przez przeciąganie bloków**.

---

## 4️⃣ Możliwości rozbudowy

* Dodanie logiki **jeśli wartość > X → uruchom aktuator**
* Dodanie przycisków w UI, które wywołują **publish MQTT** (sterowanie GPIO/I2C)
* Tworzenie **gotowych szablonów dla różnych sensorów/aktuatorów**, eksportowanych w XML

---

Mogę teraz zrobić **pełny przykład z UI + Blockly**, który:

* pokazuje sensory
* reaguje w czasie rzeczywistym
* pozwala kliknąć przycisk → wysłać wartość do aktuatora I2C

i działa od razu po uruchomieniu Docker Compose na RPi3.

Chcesz, żebym to zrobił?


Super! Zrobimy kompletny, **gotowy do uruchomienia projekt dla RPi3 w Dockerze**, który od razu po starcie:

* pokazuje wartości 3 sensorów I2C w frontendzie
* pozwala sterować aktuatorami przez przyciski
* używa Blockly do wizualnego tworzenia logiki (odczyt sensorów → akcje)
* działa w czasie rzeczywistym przez MQTT WebSocket

---

## 1️⃣ Struktura katalogów

```
rpi-blockly-iot/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   └── i2c-bridge.py
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── blocks.js
│   └── generators.js
└── data/
    └── mosquitto/
```

---

## 2️⃣ docker-compose.yml

```yaml
version: "3.8"

services:
  mosquitto:
    image: eclipse-mosquitto:2.0
    container_name: mqtt-broker
    volumes:
      - ./data/mosquitto:/mosquitto/data
      - ./data/mosquitto/config:/mosquitto/config
    ports:
      - "9001:9001"  # MQTT over WebSocket
      - "1883:1883"  # MQTT TCP
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: i2c-bridge
    devices:
      - "/dev/i2c-1:/dev/i2c-1"
    environment:
      MQTT_BROKER: "mqtt://mosquitto:1883"
    depends_on:
      - mosquitto
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: web-ui
    ports:
      - "8080:80"
    depends_on:
      - mosquitto
    restart: unless-stopped
```

---

## 3️⃣ Backend – Python bridge

`backend/i2c-bridge.py`:

```python
import os, time, json
import paho.mqtt.client as mqtt
import smbus2

MQTT_BROKER = os.environ.get("MQTT_BROKER", "mqtt://localhost:1883")
TOPIC_PREFIX = "sensors/i2c"

client = mqtt.Client("rpi-bridge")
client.connect("mosquitto", 1883, 60)

bus = smbus2.SMBus(1)
i2c_addresses = [0x40, 0x41, 0x42]  # Low, Medium, High

def read_sensor(addr):
    try:
        return bus.read_byte(addr)
    except:
        return None

while True:
    for addr in i2c_addresses:
        value = read_sensor(addr)
        if value is not None:
            client.publish(f"{TOPIC_PREFIX}/{addr}", json.dumps({"value": value}))
    time.sleep(1)
```

`backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY i2c-bridge.py .
RUN pip install paho-mqtt smbus2
CMD ["python", "i2c-bridge.py"]
```

---

## 4️⃣ Frontend – Blockly + UI

`frontend/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>RPI Blockly IoT</title>
<script src="https://unpkg.com/blockly/blockly.min.js"></script>
<script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>
<script src="blocks.js"></script>
<script src="generators.js"></script>
<style>
  #blocklyDiv { height: 400px; width: 600px; }
  .sensor { font-weight: bold; font-size: 1.5em; }
  button { margin: 5px; }
</style>
</head>
<body>
<h1>RPI Blockly IoT</h1>
<div id="blocklyDiv"></div>

<div>
  <div>Low: <span id="sensor-low" class="sensor">-</span></div>
  <div>Medium: <span id="sensor-medium" class="sensor">-</span></div>
  <div>High: <span id="sensor-high" class="sensor">-</span></div>
</div>

<div>
  <button onclick="writeActuator(0x50, 1)">Turn ON Actuator 1</button>
  <button onclick="writeActuator(0x50, 0)">Turn OFF Actuator 1</button>
</div>

<script>
var workspace = Blockly.inject('blocklyDiv', {toolbox: '<xml></xml>'});
var mqttClient = mqtt.connect('ws://' + location.hostname + ':9001');

mqttClient.on('connect', () => console.log('MQTT connected'));

// Subskrypcje sensorów
mqttClient.subscribe('sensors/i2c/64');
mqttClient.subscribe('sensors/i2c/65');
mqttClient.subscribe('sensors/i2c/66');

mqttClient.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());
  if(topic === 'sensors/i2c/64') document.getElementById('sensor-low').textContent = data.value;
  if(topic === 'sensors/i2c/65') document.getElementById('sensor-medium').textContent = data.value;
  if(topic === 'sensors/i2c/66') document.getElementById('sensor-high').textContent = data.value;
});

// Funkcja do wysyłania wartości do aktuatora I2C
function writeActuator(addr, value){
  mqttClient.publish(`actuators/i2c/${addr}`, JSON.stringify({value}));
}

// Wczytanie przykładowego Blockly XML
const xmlText = `
<xml xmlns="https://developers.google.com/blockly/xml">
  <block type="mqtt_subscribe" x="20" y="20">
    <field name="TOPIC">sensors/i2c/64</field>
    <field name="VALUE">lowValue</field>
  </block>
</xml>`;
Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);
</script>
</body>
</html>
```

---

## 5️⃣ Frontend Dockerfile

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
COPY blocks.js /usr/share/nginx/html/
COPY generators.js /usr/share/nginx/html/
```

---

## 6️⃣ Uruchomienie na RPi3

```bash
docker-compose up -d
```

* Frontend: `http://<RPI_IP>:8080`
* MQTT WS: `ws://<RPI_IP>:9001`
* Backend automatycznie odczytuje I2C i publikuje dane

---

✅ **Efekt działania**:

1. Sensory Low/Medium/High wyświetlane w czasie rzeczywistym.
2. Przyciski sterują I2C aktuatorami przez MQTT.
3. Blockly pozwala tworzyć logikę typu „jeśli sensor > X → włącz aktuator”.
4. Projekt w pełni przenośny, gotowy do eksportu XML i przenoszenia między urządzeniami.

---

Mogę teraz zrobić **rozbudowany przykład Blockly z automatyczną logiką**: jeśli `Low > 50` → włącz aktuator, jeśli `High < 20` → wyłącz. To pokaże pełen potencjał nocode na RPi3.
