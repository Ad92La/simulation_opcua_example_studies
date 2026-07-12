import time
import threading
import paho.mqtt.client as mqtt

published = threading.Event()

def on_publish(client, userdata, mid):
    print(f"QoS 1: PUBACK für mid {mid} empfangen – Zustellung bestätigt")
    published.set()

client = mqtt.Client()
client.on_publish = on_publish
client.connect("localhost", 1883)
client.loop_start()

payload = f"QoS 1 Nachricht {time.time()}"
info = client.publish("test/qos1", payload, qos=1)

# Warten auf PUBACK (on_publish)
if not published.wait(timeout=5):
    print("Warnung: PUBACK nach 5s nicht erhalten")
else:
    print("QoS 1: PUBACK empfangen, sauber beenden")

client.loop_stop()
client.disconnect()
