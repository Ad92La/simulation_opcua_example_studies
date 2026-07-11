import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"QoS 2 Subscriber connected with rc={rc}")
    client.subscribe("test/qos2", qos=2)

def on_message(client, userdata, msg):
    ts = time.time()
    dup = getattr(msg, 'dup', False)
    print(f"[{ts}] QoS 2 Subscriber: '{msg.payload.decode()}' qos={msg.qos} dup={dup}")

# persistent session to demonstrate offline-queueing and exactly-once behavior
client = mqtt.Client(client_id="subscriber-qos2", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883)
print("QoS 2 Subscriber gestartet – Nachrichten sollten genau einmal geliefert werden (persistent session)")
client.loop_forever()