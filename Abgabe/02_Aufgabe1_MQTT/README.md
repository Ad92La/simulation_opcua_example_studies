# Aufgabe 1 – MQTT QoS (zwei Varianten)

Dieses Verzeichnis enthält zwei eigenständige Lösungen für Aufgabe 1 (je 3 Publisher
+ 3 Subscriber für QoS 0/1/2):

- `mqtt_pub_subs/` – Variante Ladner (paho-mqtt v1, minimal, eine Nachricht pro Lauf)
- `mqtt_erweitert/` – erweiterte Variante (paho-mqtt v2, konfigurierbar, mehrere Nachrichten)

Ein detaillierter Vergleich der Unterschiede steht in `../00_Vergleich_Versionen.md`.

Beide benötigen einen laufenden MQTT-Broker (z. B. Mosquitto) auf `localhost:1883`.
Test-Schritte (Grundtest und Offline-Nachweis der QoS-Unterschiede) stehen in der
jeweiligen `README.md` der Variante sowie in `../00_Testanleitung.md`.
