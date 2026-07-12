"""
Subscriber for QoS 1 -- "At least once" (Task 1).

Subscribes at QoS 1 with a PERSISTENT session (clean_session=False and a fixed
client_id). The broker keeps a session for this client, so messages published at
QoS 1 while the subscriber is offline are queued and delivered on reconnect.
Because QoS 1 only guarantees "at least once", duplicates may appear.

Try it: start this subscriber once (creates the session), stop it, run
publisher_qos1.py, then start the subscriber again -- the queued messages arrive.
"""

import paho.mqtt.client as mqtt

from mqtt_config import BROKER, PORT, TOPIC

QOS = 1


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[sub qos1] connected (rc={reason_code}), subscribing to '{TOPIC}'")
    client.subscribe(TOPIC, qos=QOS)


def on_message(client, userdata, msg):
    print(f"[sub qos1] received '{msg.payload.decode()}' (qos={msg.qos})")


def main():
    # clean_session=False + stable client_id: broker queues messages while offline.
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id="sub-qos1", clean_session=False
    )
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    print("[sub qos1] waiting for messages (Ctrl+C to stop)...")
    client.loop_forever()


if __name__ == "__main__":
    main()
