"""
Subscriber for QoS 0 -- "Fire and forget" (Task 1).

Subscribes at QoS 0 with a clean session. Messages are received at most once and
there is no session persistence: anything published while this subscriber is
offline is lost forever.

Try it: stop this subscriber, run publisher_qos0.py, then start the subscriber
again -- the messages sent in the meantime will NOT arrive.
"""

import paho.mqtt.client as mqtt

from mqtt_config import BROKER, PORT, TOPIC

QOS = 0


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[sub qos0] connected (rc={reason_code}), subscribing to '{TOPIC}'")
    client.subscribe(TOPIC, qos=QOS)


def on_message(client, userdata, msg):
    print(f"[sub qos0] received '{msg.payload.decode()}' (qos={msg.qos})")


def main():
    # clean_session=True (default): no server-side session, no offline queue.
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id="sub-qos0", clean_session=True
    )
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    print("[sub qos0] waiting for messages (Ctrl+C to stop)...")
    client.loop_forever()


if __name__ == "__main__":
    main()
