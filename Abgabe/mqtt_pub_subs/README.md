# MQTT QoS Demo (ladner_adrian_mqtt)

Dieses Verzeichnis enthält je ein Publisher- und Subscriber-Skript für die drei MQTT-QoS-Level (0, 1, 2). Die Skripte sind so angepasst, dass sie die Effekte der QoS-Level reproduzierbar und sauberer demonstrieren:

- `pub_qos0.py`, `pub_qos1.py`, `pub_qos2.py` – Publisher für QoS 0/1/2
- `subscribe_qos0.py`, `subscribe_qos1.py`, `subscribe_qos2.py` – Subscriber für QoS 0/1/2

Voraussetzungen
- Ein laufender MQTT-Broker (z. B. Mosquitto) auf `localhost:1883` oder passe die Skripte an.
- Python 3.6+ und `paho-mqtt` installiert:

```powershell
python -m pip install -r requirements.txt
```

Kurzanleitung / Tests

1) QoS 0 — Verlust sichtbar machen
   - Starte den Subscriber:
     ```powershell
     python .\subscribe_qos0.py
     ```
   - Stoppe den Subscriber (STRG+C).
   - Sende eine Nachricht:
     ```powershell
     python .\pub_qos0.py
     ```
   - Starte den Subscriber erneut: die Nachricht ist verloren (QoS 0 wird nicht vom Broker gequeued).

2) QoS 1 — mindestens einmal (Duplikate möglich)
   - Starte `subscribe_qos1.py`.
   - Simuliere Instabilität: starte `pub_qos1.py` und trenne die Verbindung des Publishers (z. B. kill/Stoppen) bevor PUBACK eintrifft oder schalte Broker kurz aus.
   - Beobachte in der Subscriber-Ausgabe, ob Nachrichten mehrfach (dup=True) empfangen werden.

3) QoS 2 — genau einmal
   - Starte `subscribe_qos2.py` (persistent session).
   - Sende mit `pub_qos2.py` und simuliere Verbindungsprobleme; der QoS2-Handshake (PUBREC/PUBREL/PUBCOMP) sorgt dafür, dass die Nachricht genau einmal zugestellt wird.

Hinweise zu den Skripten
- Publisher verwenden `loop_start()` und warten auf `wait_for_publish()` oder ein `on_publish`-Event; dadurch beenden sie sich sauber, nachdem der Broker bestätigt hat (oder ein Timeout eintrat).
- Subscriber haben einen `on_connect`-Handler und verwenden `client_id` + `clean_session=False` (für QoS 1/2), um persistente Sessions/Offline-Queueing zu demonstrieren.
- Nachrichten enthalten Zeitstempel; Subscriber zeigen `dup` und `qos` an, damit Duplikate und QoS leicht erkennbar sind.

