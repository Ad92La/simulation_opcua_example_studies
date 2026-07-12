# Versionsvergleich – Aufgabe 1 (MQTT QoS)

Für Aufgabe 1 liegen **zwei Varianten** bei, damit die unterschiedlichen
Herangehensweisen im Team nachvollziehbar sind:

| | `mqtt_pub_subs/` (Variante Ladner) | `mqtt_erweitert/` (erweiterte Variante) |
|---|---|---|
| **paho-mqtt API** | v1 (`mqtt.Client()`), `requirements: paho-mqtt>=1.5.1` | v2 (`CallbackAPIVersion.VERSION2`), `paho-mqtt>=2.0` |
| **Callback-Signaturen** | v1: `on_connect(c,u,flags,rc)`, `on_publish(c,u,mid)` | v2: zusätzlich `reason_code`/`properties` |
| **Nachrichten pro Lauf** | genau **eine** Nachricht (mit Zeitstempel) | konfigurierbare **Anzahl** (`MQTT_COUNT`, Standard 5) |
| **Konfiguration** | fest verdrahtet (`localhost:1883`, Topics `test/qos0..2`) | zentral über Umgebungsvariablen (`mqtt_config.py`: `MQTT_BROKER/PORT/TOPIC/COUNT`) |
| **Publisher-Ende** | `threading.Event` + `wait()` auf PUBACK/PUBCOMP (mit Timeout) | `wait_for_publish()` pro Nachricht |
| **Subscriber (QoS 1/2)** | persistente Session (`clean_session=False`, feste `client_id`) | persistente Session (`clean_session=False`, feste `client_id`) |
| **Subscriber (QoS 0)** | clean session, Verlust bei Offline | clean session, Verlust bei Offline |
| **Ausgabe** | Zeitstempel, `qos`, `dup` sichtbar | pro QoS erläuternde Meldung (lokale Übergabe vs. PUBACK vs. PUBCOMP) |
| **Topics** | `test/qos0`, `test/qos1`, `test/qos2` | `isr/qos_demo` (per `MQTT_TOPIC` änderbar) |

## Gemeinsamkeiten

Beide Varianten demonstrieren die Kernaussagen der QoS-Stufen identisch:

- **QoS 0** – *fire and forget*: keine Broker-Bestätigung, Offline-Nachrichten gehen verloren.
- **QoS 1** – *at least once*: PUBACK, garantierte Zustellung, Duplikate möglich.
- **QoS 2** – *exactly once*: vollständiger Handshake (PUBREC/PUBREL/PUBCOMP), genau einmal.
- **Offline-Nachweis** über persistente Session (`clean_session=False`) für QoS 1/2.

## Bewertung / Empfehlung

- Die **Variante Ladner** ist bewusst minimal und gut lesbar; sie zeigt die QoS-Bestätigungen
  (PUBACK/PUBCOMP) explizit über ein `threading.Event`.
- Die **erweiterte Variante** ist robuster für wiederholte Tests (mehrere Nachrichten,
  konfigurierbarer Broker/Topic ohne Codeänderung) und nutzt die aktuelle paho-v2-API.

Beide erfüllen die Anforderung „sechs kleine Programme (3 Publisher / 3 Subscriber)".
Für die Abgabe können beide beigelegt werden; für eine einzelne Referenzlösung empfiehlt
sich die erweiterte Variante (aktuelle API, reproduzierbarere Tests).

---

## Aufgaben 2–4

Die Simulation (Aufgabe 2), die KI-Optimierung (Aufgabe 3) und die OPC-UA-Anbindung
(Aufgabe 4) liegen als gemeinsame Projektfassung im Repository (`src/`, `docker/`) und
sind hier unter `03_`, `04_`, `05_` kopiert. Hier gibt es keine konkurrierenden
Doppelversionen; Erweiterungen (MCI-Anbindung mit `--llm mci`, OPC-UA Read/Write inkl.
Boiler 3, Fix der Nodesdatei) sind in der jeweiligen Datei bzw. der Testanleitung dokumentiert.
