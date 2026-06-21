simulation_opcua_example_studies
=================================

Kurzanleitung
------------

Dieses Projekt simuliert eine kleine Produktionslinie und kann optional über OPC-UA mit einer externen SPS/OPC-UA-Server verbunden werden. Es gibt außerdem eine optionale Integration mit einem LLM (z. B. OpenAI), das Optimierungsvorschläge liefert.

Starten (lokal mit Docker Compose)
---------------------------------

1. Stelle sicher, dass Docker und docker-compose auf deinem System installiert sind.
2. Im Projektverzeichnis befindet sich ein Docker-Compose-Setup unter `docker/docker-compose.yml`. Du kannst den OPC-UA-Server (opc-plc) starten mit:

```powershell
docker-compose up -d
```

Konfiguration
-------------

Konfiguration erfolgt über Umgebungsvariablen (z. B. in einer `.env` Datei):

- `OPCUA_SERVER_URL` (Standard: `opc.tcp://localhost:50000`)
- `OPENAI_API_KEY` (optional, für LLM-Integration)
- `SIMULATION_SPEED`, `SIMULATION_CYCLES_PER_LLM`, `INITIAL_RAW_STOCK`, `BUFFER1_CAPACITY`, uvm. — siehe `src/simulation/production_line.py` für die verwendeten Variablen.

Wo landen welche Informationen?
------------------------------

- Laufende Log-Ausgaben erscheinen im Terminal (konfigurierter Console-Handler). Zusätzlich werden sie in `production.log` (UTF-8) geschrieben.
- Die Simulation sammelt historische Daten in `self.production_history` (im Speicher). Es gibt Methoden wie `get_machine_data()`, `get_buffer_data()` und `get_kpi_data()` für externen Zugriff (z. B. OPC-UA oder LLM).
- Wenn Docker Compose gestartet wird, initialisiert `docker/opc-plc/init-nodes.json` die Knoten des OPC-UA-Testservers.

Terminalausgaben
---------------------

Die Simulation gibt nun alle 10 Zyklen eine detaillierte Übersicht der aktuellen Maschinen-, Puffer- und Lagerzustände auf die Konsole aus (Füllstände, Fehler, Fortschritt etc.). Die regulären KPI-Statusmeldungen erscheinen weiterhin in größeren Intervallen.

UML-Diagramm der Produktionslinie
---------------------------------

Die PlantUML-Quelle befindet sich in `docs/`.


