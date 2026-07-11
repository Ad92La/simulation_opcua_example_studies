"""
Shared connection settings for the MQTT QoS demo (Task 1).

All six programs read the broker address, port and topic from environment
variables so you can point them at any broker (local Mosquitto, HiveMQ,
test.mosquitto.org, ...) without editing the code:

    MQTT_BROKER   default: localhost
    MQTT_PORT     default: 1883
    MQTT_TOPIC    default: isr/qos_demo
    MQTT_COUNT    default: 5      (number of messages a publisher sends)
"""

import os

BROKER = os.environ.get("MQTT_BROKER", "localhost")
PORT = int(os.environ.get("MQTT_PORT", "1883"))
TOPIC = os.environ.get("MQTT_TOPIC", "isr/qos_demo")
COUNT = int(os.environ.get("MQTT_COUNT", "5"))
