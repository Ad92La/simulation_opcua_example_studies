# Aufgabe 1 – MQTT Quality of Service (QoS) Levels

Sechs kleine Programme, die die drei MQTT-QoS-Stufen demonstrieren: je ein
Publisher/Subscriber-Paar für QoS 0, 1 und 2.

| Datei | Rolle | QoS | Kernaussage |
|-------|-------|-----|-------------|
| `publisher_qos0.py` / `subscriber_qos0.py` | Pub/Sub | 0 | *Fire and forget* – höchstens einmal, keine Zustellgarantie |
| `publisher_qos1.py` / `subscriber_qos1.py` | Pub/Sub | 1 | *At least once* – garantierte Zustellung, aber Duplikate möglich |
| `publisher_qos2.py` / `subscriber_qos2.py` | Pub/Sub | 2 | *Exactly once* – garantiert genau einmal, kein Verlust, keine Duplikate |

## Voraussetzungen

```powershell
pip install -r requirements.txt
```

Ein MQTT-Broker wird benötigt. Zwei einfache Optionen:

- **Lokal (empfohlen):** Eclipse Mosquitto über Docker
  ```powershell
  docker run -it -p 1883:1883 eclipse-mosquitto
  ```
- **Öffentlich zum Testen:** `test.mosquitto.org` (Port 1883)
  ```powershell
  $env:MQTT_BROKER="test.mosquitto.org"
  ```

Konfiguration über Umgebungsvariablen (siehe `mqtt_config.py`): `MQTT_BROKER`
(Standard `localhost`), `MQTT_PORT` (`1883`), `MQTT_TOPIC` (`isr/qos_demo`),
`MQTT_COUNT` (`5`).

## Grundtest (Zustellung sichtbar machen)

Jeweils in einem eigenen Terminal, Subscriber zuerst starten:

```powershell
python subscriber_qos1.py     # Terminal A
python publisher_qos1.py      # Terminal B
```

Der Publisher zeigt für QoS 1/2 die Broker-Bestätigung (PUBACK bzw. PUBCOMP), für
QoS 0 nur die lokale Übergabe – so wird der Unterschied im Programmverhalten sichtbar.

## Unterschiede der Level nachweisen (Offline-Test)

Der deutlichste Nachweis ist das Verhalten, wenn Nachrichten gesendet werden,
während der Subscriber offline ist:

1. **QoS 0** – Subscriber (clean session) läuft nicht → Nachrichten sind verloren.
   `subscriber_qos0.py` starten, stoppen, `publisher_qos0.py` laufen lassen,
   Subscriber neu starten → die zwischenzeitlichen Nachrichten **fehlen**.
2. **QoS 1** – persistente Session (`clean_session=False`, fester `client_id`).
   Subscriber einmal starten (legt Session an), stoppen, `publisher_qos1.py`
   laufen lassen, Subscriber neu starten → die Nachrichten werden **nachgeliefert**
   (ggf. mit Duplikaten).
3. **QoS 2** – wie QoS 1, aber die Nachrichten kommen **genau einmal** an.

> Hinweis: Der Offline-Nachweis für QoS 1/2 erfordert einen Broker, der Sessions
> persistiert (Mosquitto tut das). Auf `test.mosquitto.org` funktioniert es
> ebenfalls, kann aber durch Fremdverkehr auf dem Topic „verrauscht" sein –
> daher ggf. ein eindeutiges `MQTT_TOPIC` setzen.
