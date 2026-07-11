"""
Publisher for QoS 2 -- "Exactly once" (Task 1).

QoS 2 is the highest and safest level: every message is delivered EXACTLY once,
using a four-way handshake (PUBLISH -> PUBREC -> PUBREL -> PUBCOMP). No message
is lost and no duplicate is delivered. This is the slowest level because of the
additional round trips.

Observe: `on_publish` fires only after the full handshake completes (PUBCOMP),
so `wait_for_publish()` blocks the longest of all three levels.
"""

import time

import paho.mqtt.client as mqtt

from mqtt_config import BROKER, PORT, TOPIC, COUNT

QOS = 2


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[pub qos2] connected (rc={reason_code})")


def on_publish(client, userdata, mid, reason_code, properties):
    # For QoS 2 this fires after the complete handshake (PUBCOMP).
    print(f"[pub qos2] handshake complete, PUBCOMP received (mid={mid})")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pub-qos2")
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    for i in range(1, COUNT + 1):
        payload = f"QoS2 message {i}"
        info = client.publish(TOPIC, payload, qos=QOS)
        print(f"[pub qos2] sent '{payload}' (mid={info.mid}, rc={info.rc})")
        info.wait_for_publish()  # blocks until the QoS 2 handshake finished
        time.sleep(0.5)

    client.loop_stop()
    client.disconnect()
    print("[pub qos2] done")


if __name__ == "__main__":
    main()
