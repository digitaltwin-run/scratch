import os
import time
import json
import logging

import paho.mqtt.client as mqtt  # type: ignore
from smbus2 import SMBus  # type: ignore

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "sensors/i2c")
ACT_TOPIC_PREFIX = os.getenv("ACT_TOPIC_PREFIX", "actuators/i2c")
I2C_BUS_ID = int(os.getenv("I2C_BUS_ID", "1"))
I2C_ADDRESSES = [0x40, 0x41, 0x42]  # example addresses
PUBLISH_INTERVAL_SEC = float(os.getenv("PUBLISH_INTERVAL_SEC", "1.0"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("i2c-bridge")

# Initialize I2C bus early (for use in callbacks)
bus = SMBus(I2C_BUS_ID)

client = mqtt.Client(client_id="rpi-i2c-bridge")

# Optional: last will
client.will_set(
    "system/bridge/status",
    payload="offline",
    qos=1,
    retain=True,
)


def _parse_addr(segment: str) -> int:
    """Parse address segment as int, supports decimal or 0x-prefixed hex."""
    try:
        if segment.lower().startswith("0x"):
            return int(segment, 16)
        return int(segment)
    except Exception:
        return -1


def _handle_actuator(addr: int, value: int) -> None:
    try:
        value = int(value) & 0xFF
        bus.write_byte(addr, value)
        logger.info("I2C write 0x%02X <= %d", addr, value)
    except Exception as e:
        logger.warning("I2C write failed for 0x%02X: %s", addr, e)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        topic = f"{ACT_TOPIC_PREFIX}/#"
        client.subscribe(topic, qos=1)
        logger.info("Connected to MQTT, subscribed: %s", topic)
    else:
        logger.warning("MQTT connect returned code %s", rc)



def on_message(client, userdata, msg):
    try:
        # Expect topic like: actuators/i2c/<addr>
        parts = msg.topic.split("/")
        addr = _parse_addr(parts[-1]) if parts else -1
        payload = json.loads(msg.payload.decode("utf-8"))
        value = payload.get("value", 0)
        if addr >= 0:
            _handle_actuator(addr, value)
    except Exception as e:
        logger.warning("Actuator msg handling failed: %s", e)


client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        logger.info("Connecting to MQTT %s:%s", MQTT_HOST, MQTT_PORT)
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
        client.publish(
            "system/bridge/status",
            payload="online",
            qos=1,
            retain=True,
        )
        break
    except Exception as e:
        logger.warning("MQTT connect failed: %s. Retrying in 2s...", e)
        time.sleep(2)



def read_sensor(addr: int):
    try:
        # Example: read a single byte value
        value = bus.read_byte(addr)
        return value
    except Exception as e:
        logger.debug("I2C read failed for 0x%02X: %s", addr, e)
        return None


try:
    while True:
        ts = time.time()
        for addr in I2C_ADDRESSES:
            value = read_sensor(addr)
            if value is not None:
                payload = {
                    "addr": addr,
                    "value": value,
                    "ts": ts,
                }
                topic = f"{TOPIC_PREFIX}/{addr}"
                client.publish(
                    topic,
                    json.dumps(payload),
                    qos=1,
                    retain=True,
                )
        time.sleep(PUBLISH_INTERVAL_SEC)
except KeyboardInterrupt:
    pass
finally:
    try:
        bus.close()
    except Exception:
        pass
    try:
        client.publish(
            "system/bridge/status",
            payload="offline",
            qos=1,
            retain=True,
        )
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
