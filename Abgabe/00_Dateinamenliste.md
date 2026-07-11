# Liste der Dateinamen (Abgabe)

Dieser Ordner ist die eigenständige Abgabe. Er enthält alle laut Aufgabenstellung
geforderten Dokumente: Systemarchitektur (Diagramm), Quellcode (MQTT, Simulation,
OPC-UA-Client), OPC-UA-Definitionen, KI-/API-Code, Deckblatt und diese Dateinamenliste.

## 00 – Deckblatt & Dokumentation
| Datei | Inhalt |
|-------|--------|
| `00_Deckblatt.md` | Deckblatt (Kurs, Team, Aufgaben) |
| `00_Dateinamenliste.md` | Diese Liste |
| `00_Testanleitung.md` | Manuelle Testanleitung (Aufgabe 1–4, inkl. venv) |
| `00_Vergleich_Versionen.md` | Vergleich der beiden MQTT-Varianten (Ladner vs. erweitert) |

## 01 – Systemarchitektur (Diagramm)
| Datei | Inhalt |
|-------|--------|
| `01_Diagramm/architecture.svg` | UML-Komponentendiagramm (Export, alle 4 Aufgaben) |
| `01_Diagramm/architecture.drawio` | Editierbare draw.io-Quelldatei |
| `01_Diagramm/architecture.puml` | PlantUML-Quelle (alternativ) |

## 02 – Aufgabe 1: MQTT QoS (zwei Varianten)
| Datei | Inhalt |
|-------|--------|
| `02_Aufgabe1_MQTT/README.md` | Übersicht beider Varianten |
| `02_Aufgabe1_MQTT/mqtt_pub_subs/…` | Variante Ladner: `pub_qos0/1/2.py`, `subscribe_qos0/1/2.py`, `requirements.txt`, `README.md` |
| `02_Aufgabe1_MQTT/mqtt_erweitert/…` | Erweiterte Variante: `publisher_qos0/1/2.py`, `subscriber_qos0/1/2.py`, `mqtt_config.py`, `requirements.txt`, `README.md` |

## 03 – Aufgabe 2: Produktionslinien-Simulation (Quellcode)
| Datei | Inhalt |
|-------|--------|
| `03_Aufgabe2_Simulation/main.py` | Einstiegspunkt (orchestriert Aufgabe 2–4, LLM-Flag `--llm`) |
| `03_Aufgabe2_Simulation/production_line.py` | Prozessfluss, Takt, Stau-Logik |
| `03_Aufgabe2_Simulation/machines.py` | Maschinen & Zykluszeiten |
| `03_Aufgabe2_Simulation/buffers.py` | Puffer mit Kapazität/Stau |
| `03_Aufgabe2_Simulation/warehouse.py` | Eingangs-, Recycling-, Fertigwarenlager |
| `03_Aufgabe2_Simulation/__init__.py` | Paket-Init |
| `03_Aufgabe2_Simulation/requirements.txt` | Abhängigkeiten (Simulation selbst: nur Standardbibliothek) |

## 04 – Aufgabe 3: KI-Integration (Programm-Code für API-Aufrufe)
| Datei | Inhalt |
|-------|--------|
| `04_Aufgabe3_KI_API/mci_analyzer.py` | LLM-Analyzer über MCI-REST-API (`--llm mci`) |
| `04_Aufgabe3_KI_API/analyzer.py` | LLM-Analyzer über OpenAI (Standard-Provider) |
| `04_Aufgabe3_KI_API/optimizer.py` | Wendet die LLM-Vorschläge auf die Simulation an |
| `04_Aufgabe3_KI_API/prompts.py` | System- & Analyse-Prompt |
| `04_Aufgabe3_KI_API/__init__.py` | Paket-Init |

## 05 – Aufgabe 4: OPC UA (Definitionen + Client)
| Datei | Inhalt |
|-------|--------|
| `05_Aufgabe4_OPCUA/definitions/boiler3-nodes.json` | **4A:** Boiler-3-Knotendefinition (JSON) |
| `05_Aufgabe4_OPCUA/definitions/init-nodes.json` | **4B:** Fertigungslinien-Nodes **+ Boiler3** (FolderList) – die vom Server geladene Datei |
| `05_Aufgabe4_OPCUA/definitions/docker-compose.yml` | OPC-UA-Testserver (opc-plc) |
| `05_Aufgabe4_OPCUA/client/rw_tool.py` | **4B:** Lesen/Schreiben (Start/Stopp, Zähler, Boiler) |
| `05_Aufgabe4_OPCUA/client/client.py` | OPC-UA-Client (schreibt Simulationsdaten) |
| `05_Aufgabe4_OPCUA/client/node_manager.py` | Node-Mapping (inkl. Boiler 3) |
| `05_Aufgabe4_OPCUA/client/__init__.py` | Paket-Init |

---

Zuordnung zu den erwarteten Abgabedokumenten laut Aufgabenstellung:
Systemarchitektur (01), Quellcode inkl. MQTT & OPC-UA-Client (02/03/05),
OPC-UA-Definitionen (05), KI-Implementierung/API-Aufrufe (04), Deckblatt und
Dateinamenliste (00).

> Hinweis zur Ausführung: Die Aufgaben 2–4 bilden ein zusammenhängendes Python-
> Projekt (Paket `src/` im Repository). Die Dateien hier sind die Abgabe-Kopien;
> zum Ausführen dient das Repository-Wurzelverzeichnis (siehe `00_Testanleitung.md`).
