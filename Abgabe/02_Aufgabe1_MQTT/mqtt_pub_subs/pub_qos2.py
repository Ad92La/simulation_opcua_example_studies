import time
import threading
import paho.mqtt.client as mqtt

published = threading.Event()

def on_publish(client, userdata, mid):
    print(f"QoS 2: PUBCOMP/PUBACK Sequenz abgeschlossen für mid {mid} – genau einmal")
    published.set()

client = mqtt.Client()
client.on_publish = on_publish
client.connect("localhost", 1883)
client.loop_start()

payload = f"QoS 2 Nachricht {time.time()}"
info = client.publish("test/qos2", payload, qos=2)

if not published.wait(timeout=10):
    print("Warnung: QoS2 PUBCOMP nicht innerhalb 10s erhalten")
else:
    print("QoS 2: PUBCOMP empfangen, sauber beenden")

client.loop_stop()
client.disconnect()
