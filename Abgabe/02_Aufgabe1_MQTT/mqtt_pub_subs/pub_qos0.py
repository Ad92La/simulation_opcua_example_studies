import time
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883)
client.loop_start()

payload = f"QoS 0 Nachricht {time.time()}"
info = client.publish("test/qos0", payload, qos=0)
# Bei QoS 0 stellt wait_for_publish sicher, dass die Nachricht in den Outgoing-Buffer
# geschrieben wurde; trotzdem gibt es keine Garantie für die Zustellung am Broker.
info.wait_for_publish()
time.sleep(0.1)  # kurzer Puffer, um wirklich Daten zu senden
print("QoS 0: Nachricht in Outgoing-Buffer geschrieben (keine Bestätigung vom Broker)")

client.loop_stop()
client.disconnect()