import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"QoS 1 Subscriber connected with rc={rc}")
    client.subscribe("test/qos1", qos=1)

def on_message(client, userdata, msg):
    ts = time.time()
    dup = getattr(msg, 'dup', False)
    print(f"[{ts}] QoS 1 Subscriber: '{msg.payload.decode()}' qos={msg.qos} dup={dup}")

# persistent session to demonstrate offline-queueing for QoS1
client = mqtt.Client(client_id="subscriber-qos1", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883)
print("QoS 1 Subscriber gestartet – Nachrichten kommen mindestens einmal an (persistent session)")
client.loop_forever()