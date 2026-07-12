"""
Publisher for QoS 0 -- "Fire and forget" (Task 1).

QoS 0 delivers a message at most once. The publisher hands the message to the
network and does NOT wait for any acknowledgement from the broker. If the
message is lost in transit, it is simply gone -- there is no retry. This is the
fastest but least reliable level.

Observe: `on_publish` fires as soon as the message leaves the client locally,
there is no broker-side PUBACK involved.
"""

import time

import paho.mqtt.client as mqtt

from mqtt_config import BROKER, PORT, TOPIC, COUNT

QOS = 0


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[pub qos0] connected (rc={reason_code})")


def on_publish(client, userdata, mid, reason_code, properties):
    # For QoS 0 this only means the message left the client, NOT that the
    # broker received it.
    print(f"[pub qos0] handed off locally (mid={mid})")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pub-qos0")
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    for i in range(1, COUNT + 1):
        payload = f"QoS0 message {i}"
        info = client.publish(TOPIC, payload, qos=QOS)
        print(f"[pub qos0] sent '{payload}' (mid={info.mid}, rc={info.rc})")
        info.wait_for_publish()  # returns immediately for QoS 0 (no broker ack)
        time.sleep(0.5)

    client.loop_stop()
    client.disconnect()
    print("[pub qos0] done")


if __name__ == "__main__":
    main()
