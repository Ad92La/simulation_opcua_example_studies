"""
Publisher for QoS 1 -- "At least once" (Task 1).

QoS 1 guarantees that a message is delivered at least once. The broker confirms
every message with a PUBACK; if the publisher does not receive it, the message
is re-sent. As a consequence the subscriber may occasionally receive DUPLICATES.

Observe: `on_publish` fires only AFTER the broker acknowledged the message with
a PUBACK -- `wait_for_publish()` therefore blocks until that confirmation.
"""

import time

import paho.mqtt.client as mqtt

from mqtt_config import BROKER, PORT, TOPIC, COUNT

QOS = 1


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[pub qos1] connected (rc={reason_code})")


def on_publish(client, userdata, mid, reason_code, properties):
    # For QoS 1 this fires when the broker confirmed the message (PUBACK).
    print(f"[pub qos1] broker confirmed via PUBACK (mid={mid})")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pub-qos1")
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    for i in range(1, COUNT + 1):
        payload = f"QoS1 message {i}"
        info = client.publish(TOPIC, payload, qos=QOS)
        print(f"[pub qos1] sent '{payload}' (mid={info.mid}, rc={info.rc})")
        info.wait_for_publish()  # blocks until the broker PUBACK arrives
        time.sleep(0.5)

    client.loop_stop()
    client.disconnect()
    print("[pub qos1] done")


if __name__ == "__main__":
    main()
