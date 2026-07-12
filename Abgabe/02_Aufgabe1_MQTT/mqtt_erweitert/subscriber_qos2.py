"""
Subscriber for QoS 2 -- "Exactly once" (Task 1).

Subscribes at QoS 2 with a PERSISTENT session (clean_session=False and a fixed
client_id). QoS 2 guarantees each message is delivered exactly once, even across
reconnects: no loss and no duplicates. This is the strongest guarantee and the
right choice when every message matters and duplicates are unacceptable.

Try it: start this subscriber once (creates the session), stop it, run
publisher_qos2.py, then start the subscriber again -- every queued message
arrives exactly once.
"""

import paho.mqtt.client as mqtt

from mqtt_config import BROKER, PORT, TOPIC

QOS = 2


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[sub qos2] connected (rc={reason_code}), subscribing to '{TOPIC}'")
    client.subscribe(TOPIC, qos=QOS)


def on_message(client, userdata, msg):
    print(f"[sub qos2] received '{msg.payload.decode()}' (qos={msg.qos})")


def main():
    # clean_session=False + stable client_id: guaranteed exactly-once delivery.
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id="sub-qos2", clean_session=False
    )
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    print("[sub qos2] waiting for messages (Ctrl+C to stop)...")
    client.loop_forever()


if __name__ == "__main__":
    main()
