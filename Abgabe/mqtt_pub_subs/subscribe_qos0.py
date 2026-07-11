import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"QoS 0 Subscriber connected with rc={rc}")
    client.subscribe("test/qos0", qos=0)

def on_message(client, userdata, msg):
    ts = time.time()
    dup = getattr(msg, 'dup', False)
    print(f"[{ts}] QoS 0 Subscriber: '{msg.payload.decode()}' qos={msg.qos} dup={dup}")

client = mqtt.Client(client_id="subscriber-qos0")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883)
print("QoS 0 Subscriber gestartet – Nachrichten gehen verloren, wenn nicht verbunden")
client.loop_forever()