# Manuelle Testanleitung – alle Aufgaben

Diese Anleitung beschreibt Schritt für Schritt, wie du jede Aufgabe lokal testen
und die geforderte Funktionalität nachweisen kannst. Getestet unter Windows
(PowerShell); Befehle für macOS/Linux in Klammern, wo abweichend.

> **Kontext:** Dieser Abgabeordner enthält die Deliverables als Kopie. Das
> lauffähige Projekt (Aufgaben 2–4) liegt im Paket `src/` im Repository-
> Wurzelverzeichnis; die Befehle mit `python -m src.main` bzw.
> `python -m src.opcua_client.rw_tool` werden **vom Repo-Wurzelverzeichnis**
> ausgeführt. Die MQTT-Programme (Aufgabe 1) sind eigenständig und liegen hier
> unter `Abgabe/02_Aufgabe1_MQTT/` (zwei Varianten, siehe `00_Vergleich_Versionen.md`).

**Voraussetzungen allgemein:** Python 3.11+, Docker Desktop, Git, Visual Studio
(mit „Python-Entwicklung"-Workload) oder VS Code.

---

## 0 – Umgebung vorbereiten: venv in Visual Studio anlegen

Für **Aufgabe 2–4 genügt eine venv im Ordner `Repo`** (deren `requirements.txt`
deckt Simulation, OPC UA und LLM ab). Aufgabe 1 (MQTT) hat eine eigene
`requirements.txt` im Ordner `Aufgabe1_MQTT`. Empfehlung: je eine venv pro
`requirements.txt`, damit sich die Abhängigkeiten nicht mischen.

### Variante A – Visual Studio (GUI)

1. **Ordner öffnen:** *Datei → Öffnen → Ordner…* und den jeweiligen Aufgabenordner
   wählen (z. B. `Aufgabe1_MQTT` oder `Repo`).
2. **Python-Umgebungen öffnen:** Menü *Ansicht → Weitere Fenster → Python-Umgebungen*
   (oder *Python Environments*).
3. **Umgebung hinzufügen:** Auf *Umgebung hinzufügen…* klicken →
   Typ **„Virtuelle Umgebung"** wählen → Basis-Interpreter (Python 3.11+) auswählen →
   Speicherort standardmäßig `.venv` im Projekt belassen.
4. **requirements angeben:** Im Dialog kann direkt die passende `requirements.txt`
   ausgewählt werden – dann installiert Visual Studio die Pakete automatisch.
   Anschließend *Erstellen* klicken.
5. **Aktivieren:** Die neue Umgebung im Fenster als aktiv markieren (Häkchen /
   *Diese Umgebung aktivieren*). Neue Terminals nutzen sie dann automatisch.

### Variante B – Terminal (funktioniert in Visual Studio und VS Code)

Im integrierten Terminal (in VS: *Ansicht → Terminal*), im jeweiligen Ordner:

```powershell
# venv anlegen
python -m venv .venv

# aktivieren (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
#   (Eingabeaufforderung/cmd:  .\.venv\Scripts\activate.bat)
#   (macOS/Linux:              source .venv/bin/activate)

# Abhängigkeiten installieren
pip install -r requirements.txt
```

> Hinweis: Falls PowerShell die Aktivierung wegen der Ausführungsrichtlinie
> blockiert, einmalig ausführen:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

Ist die venv aktiv (Präfix `(.venv)` im Prompt), gelten die `pip install`-Schritte
in den folgenden Abschnitten als erledigt. Die Repo-`requirements.txt` enthält
bereits `asyncua` (OPC UA), `python-dotenv`, `openai` und `requests` (MCI) – für
Aufgabe 2–4 ist damit alles abgedeckt.

---

## Aufgabe 1 – MQTT QoS

**Ziel:** Nachweis der drei QoS-Stufen (0/1/2).

1. Abhängigkeit installieren (eine der beiden Varianten wählen):
   ```powershell
   cd Abgabe\02_Aufgabe1_MQTT\mqtt_erweitert   # oder: ...\mqtt_pub_subs
   pip install -r requirements.txt
   ```
2. Broker starten (empfohlen: lokaler Mosquitto via Docker):
   ```powershell
   docker run -it -p 1883:1883 eclipse-mosquitto
   ```
   (Alternativ öffentlich: `$env:MQTT_BROKER="test.mosquitto.org"`)
3. **Grundtest – Zustellung:** zwei Terminals, Subscriber zuerst.
   ```powershell
   python subscriber_qos1.py      # Terminal A
   python publisher_qos1.py       # Terminal B
   ```
   **Erwartung:** Subscriber empfängt 5 Nachrichten. Publisher meldet für QoS 1
   die Broker-Bestätigung (PUBACK), für QoS 2 den Abschluss des Handshakes
   (PUBCOMP), für QoS 0 nur die lokale Übergabe.
4. **Nachweis der Unterschiede – Offline-Test:**
   - **QoS 0 (Verlust):** `subscriber_qos0.py` starten, dann stoppen (Ctrl+C).
     `publisher_qos0.py` laufen lassen. Subscriber neu starten.
     **Erwartung:** die zwischenzeitlichen Nachrichten **fehlen**.
   - **QoS 1/2 (Nachlieferung):** `subscriber_qos1.py` einmal starten (legt die
     persistente Session an), stoppen, `publisher_qos1.py` laufen lassen,
     Subscriber neu starten.
     **Erwartung:** die Nachrichten werden **nachgeliefert** (QoS 2 genau einmal).
   > Tipp: eindeutiges Topic setzen, um Fremdverkehr auszuschließen:
   > `$env:MQTT_TOPIC="isr/<dein-name>/demo"`.

---

## Aufgabe 2 – Produktionslinien-Simulation

**Ziel:** Fertigungsprozess mit Puffer- und Stau-Logik läuft.

> **Wichtig – Projektstruktur:** Der gesamte Quellcode liegt im Paket `src/`
> (`src/simulation/`, `src/opcua_client/`, `src/llm_integration/`). Die
> Hauptanwendung wird deshalb als **Modul** vom Repo-Wurzelverzeichnis aus
> gestartet: `python -m src.main` (siehe Repo-`README.md`).

1. Abhängigkeiten installieren (in der venv aus Abschnitt 0):
   ```powershell
   cd Repo
   pip install -r requirements.txt
   ```
   Hinweis: Die Simulation selbst (`src/simulation/`) nutzt nur die
   Standardbibliothek; die Pakete werden erst für OPC UA / LLM benötigt.
2. `.env` anlegen (`copy .env.example .env`). Für einen reinen Simulationstest
   kann `OPENAI_API_KEY` leer bleiben und der OPC-UA-Server muss nicht laufen.
3. Simulation starten (vom Repo-Wurzelverzeichnis):
   ```powershell
   python -m src.main
   ```
4. **Erwartung:** Konsolen-Ausgabe mit Maschinen-, Puffer- und Lagerzuständen;
   Füllstände ändern sich, bei vollem Puffer stoppt die vorgelagerte Stufe
   (Stau-Logik). Logs landen in `production.log`. Beenden mit `Ctrl+C`.
5. Optional Parameter in `.env` variieren (z. B. `BUFFER2_CAPACITY`,
   `MACHINE_SCHLEIF_CYCLE_TIME`, `INITIAL_RAW_STOCK`) und Effekt beobachten.

### Einzeltests aus `test_scripts/` ausführen

Die Testskripte fügen `src` automatisch zum Suchpfad hinzu und laufen daher
**direkt** vom Repo-Wurzelverzeichnis – ohne zusätzliche Umgebungsvariablen:

```powershell
python test_scripts/test_simulation_only.py   # 10 Zyklen der Linie
python test_scripts/test_buffers.py           # Puffer-/Stau-Logik isoliert
```

**Erwartung:** beide Skripte laufen ohne `ModuleNotFoundError` durch und geben
Zyklus- bzw. Pufferzustände aus.

> Hinweis: Früher trat hier `ModuleNotFoundError: No module named 'simulation'`
> auf, weil die Skripte mit `from simulation ...` importieren, die Pakete aber
> unter `src/` liegen. Das ist behoben – die Skripte ergänzen `src` nun selbst.

Weitere Skripte: `test_llm_analyzer.py` und `test_full_optimization.py`
(brauchen LLM-Zugangsdaten), `test_simulation_to_opcua.py` sowie die reinen
OPC-UA-Tests (`test_opcua_connection.py`, `test_opcua_read.py`,
`test_nodes_exist.py`) benötigen einen laufenden OPC-UA-Server (siehe Aufgabe 4).

---

## Aufgabe 3 – KI-Integration (MCI)

**Ziel:** Prozessdaten der laufenden Simulation werden per API-Call an ein LLM
geschickt; die Empfehlung wird angezeigt (nicht automatisch angewandt). Die
Anbindung ist ins Repo integriert und über das Flag `--llm mci` wählbar
(Default bleibt OpenAI).

**A) Schnelltest ohne Zugangsdaten (Offline-Unit-Test):**

```powershell
cd Repo
python test_scripts/test_mci_analyzer.py
```

**Erwartung:** `ALL TESTS PASSED`. Der Test prüft mit gestubbtem `requests` den
korrekten MCI-Request (URL `…/api/v1/llm/chat`, Header `X-Client-ID`/
`X-Client-Secret`, `maxTokens`) und das Parsen der Antwort – ohne Netzwerk/Key.

**B) Echter Lauf gegen die MCI-API:**

1. `.env` im Repo füllen: `MCI_API_KEY`, `MCI_API_SECRET`, `MCI_BASE_URL` und
   **`MCI_MODEL=gpt-4o`** (siehe `.env.example`). Wichtig: für MCI die eigene
   Variable `MCI_MODEL` nutzen – `LLM_MODEL` (z. B. `gpt-4-turbo-preview`) gilt
   nur für OpenAI und würde bei MCI zu `HTTP 400` führen.
2. Simulation mit MCI starten (Repo-Wurzelverzeichnis):
   ```powershell
   python -m src.main --llm mci
   ```
   Zum Vergleich der Default (OpenAI): `python -m src.main` (nutzt `OPENAI_API_KEY`).
3. **Erwartung:** Im Log erscheint `LLM integration enabled (MCI)`. Nach
   `SIMULATION_CYCLES_PER_LLM` Zyklen läuft ein Optimierungszyklus:
   `Running LLM optimization cycle...` plus Engpass und Top-Maßnahmen.
   Tipp: für schnelleres Feedback `SIMULATION_CYCLES_PER_LLM` klein setzen (z. B. 20).
4. Fehlerfälle:
   - `No MCI credentials ...` → `MCI_API_KEY`/`MCI_API_SECRET` fehlen in `.env`.
   - `MCI analysis failed: MCI API 400: ...` → der genaue Grund steht im Log
     (Server-Antworttext). Häufig: falsches Modell → `MCI_MODEL` auf ein
     erlaubtes Modell setzen (`gpt-4o`, `gpt-5.2`, `gpt-5-nano`, `o3`,
     `Mistral-Large-3`). Hinweis: MCI erlaubt nur die Rollen `user`/`assistant`,
     daher wird die Systemanweisung direkt in die `user`-Nachricht eingebettet
     (keine `system`-Rolle).
   - `401/403` → `MCI_API_KEY`/`MCI_API_SECRET` (bzw. `CLIENT_ID`/`CLIENT_SECRET`) prüfen.

---

## Aufgabe 4 – OPC UA (Boiler 3 + Read/Write)

**Ziel:** OPC-UA-Server stellt Fertigungslinien- und Boiler-3-Nodes bereit; Werte
lassen sich lesen und schreiben.

1. OPC-UA-Testserver starten:
   ```powershell
   cd Repo/docker
   docker-compose up -d
   ```
   Der Server (`opc-plc`) lädt **eine** Datei `init-nodes.json`; diese enthält
   sowohl die Produktionslinien-Nodes als auch die Boiler-3-Nodes (als
   `FolderList`-Unterordner). Hinweis: `--nodesfile` akzeptiert nur eine Datei –
   eine zweite würde die erste überschreiben.
2. Abhängigkeiten für den Client (im Repo-Wurzelverzeichnis, falls noch nicht
   aus Aufgabe 2 geschehen):
   ```powershell
   pip install -r requirements.txt
   ```
3. **4A – Boiler 3 lesen/schreiben:**
   ```powershell
   cd Repo
   python -m src.opcua_client.rw_tool read-boiler
   python -m src.opcua_client.rw_tool write-boiler TemperatureTop 68.5
   python -m src.opcua_client.rw_tool write-boiler HeaterState true
   python -m src.opcua_client.rw_tool read-boiler
   ```
   **Erwartung:** Nach dem Schreiben zeigt `read-boiler` die neuen Werte
   (`TemperatureTop = 68.5`, `HeaterState = True`).
4. **4B – Fertigungslinie Start/Stopp & Zähler:**
   ```powershell
   python -m src.opcua_client.rw_tool start-machine Fraese1
   python -m src.opcua_client.rw_tool read machine Fraese1 Status
   python -m src.opcua_client.rw_tool stop-machine Fraese1
   python -m src.opcua_client.rw_tool read machine Fraese1 Counter
   ```
   **Erwartung:** `Status` wechselt zwischen `1` (RUNNING) und `0` (IDLE).
5. **Zusammenspiel mit der Simulation:** In einem zweiten Terminal
   `python -m src.main` starten – die Simulation schreibt laufend Werte, die per
   `rw_tool read ...` abgefragt werden können.
6. Server stoppen:
   ```powershell
   docker-compose down
   ```

---

## Schnell-Checkliste

| Aufgabe | Erfolgskriterium |
|---------|------------------|
| 1 MQTT | QoS 0 verliert Offline-Nachrichten, QoS 1/2 liefern sie nach |
| 2 Simulation | Prozess läuft, Stau bei vollem Puffer, Logs entstehen |
| 3 KI | `test_mci_analyzer.py` grün; `--llm mci` zeigt LLM-Empfehlung im Log |
| 4 OPC UA | Boiler-3- und Maschinen-Nodes les-/schreibbar |
