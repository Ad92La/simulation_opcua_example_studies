License / Miscellaneous / Disclaimer
------------------------------------
- This README describes the current state of the example implementation. If you change configuration variables or startup sequences, please verify that the documentation still matches the code.
- **Disclaimer**: The author assumes no responsibility for any further use, modification, or damages arising from the use of this code. The code is provided for example and demonstration purposes only and is provided without warranty.

This is an example implementation of a small production line simulation. It is not a production-ready solution and is intended only for educational and demonstration purposes in the context of a university exercise.

Note: This project was optimized and extended with the help of AI / LLM tools (for example OpenAI) for code generation, refactoring, and documentation. The LLM integration is experimental and not fully tested. It is provided as an example of how AI can assist in software development and simulation analysis.

Important language note:
- Most parts of this project, including documentation, comments, and some identifiers, are written in German.

Quick Start
-----------

This project simulates a small production line and can optionally be connected via OPC UA to an external PLC / OPC UA test server. It also includes an example integration with an LLM (for example OpenAI), which is not fully tested and is intended only as an example implementation.

0) Install dependencies
-----------------------

Install the required Python packages (ideally into a virtual environment):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Note: the pure production-line simulation (`src/simulation/`) uses only the
Python standard library. The packages in `requirements.txt` (`asyncua`,
`python-dotenv`, `openai`) are needed to run the full application
(`python -m src.main`) with OPC UA and LLM analysis.

1) Configuration (`.env`)
-------------------------

Before starting anything, create a `.env` file in the projet root directory.

- Additional configuration variables and defaults are documented in `src/simulation/production_line.py`.
- If `OPENAI_API_KEY` is empty, the LLM integration is not used.

2) Start the OPC UA test server (`opc-plc`)
-------------------------------------------

The OPC UA test server is included in the Docker setup (`docker/opc-plc`).

Start:
- Change to the `docker` directory and start it with docker-compose:
```powershell
cd docker
docker-compose up -d
```

Stop:
- Stop and remove the container:
```powershell
cd docker
docker-compose down
```
- Alternatively, you can stop the container directly:
```powershell
docker ps      # find the container ID
docker stop <container-id>
```

3) Start the client / simulation (`main.py`)
--------------------------------------------

After the `.env` file is in place and (optionally) the OPC UA server is running, start the client simulation:

- From the project root:
```powershell
# with Python / venv installed
python -m src.main
# or
python src\main.py
```

### Choosing the LLM provider (`--llm`)

The optimization LLM (Task 3) can be selected at startup. The default is OpenAI
(unchanged behavior); pass `--llm mci` to use the MCI account's REST API instead:

```powershell
python -m src.main            # default: OpenAI  (uses OPENAI_API_KEY)
python -m src.main --llm mci  # MCI REST API     (uses MCI_API_KEY / MCI_API_SECRET)
```

For `--llm mci`, set `MCI_BASE_URL`, `MCI_API_KEY`, `MCI_API_SECRET` and
`MCI_MODEL=gpt-4o` in `.env` (see `.env.example`). Use `MCI_MODEL` (not
`LLM_MODEL`) for the MCI provider — sending an OpenAI-only model such as
`gpt-4-turbo-preview` to MCI results in `HTTP 400 Bad Request`. Valid MCI models:
`gpt-4o`, `gpt-5.2`, `gpt-5-nano`, `o3`, `Mistral-Large-3`. If the credentials for
the selected provider are missing, the simulation still runs, only the LLM
optimization is disabled.

- Stop: press CTRL+C in the console. The program usually handles SIGINT and shuts down running loops cleanly; it writes log entries to `production.log` before exiting.

Startup flow / order of operations
----------------------------------

1. Environment variables are loaded from `.env` when `main.py` starts.
2. If `OPCUA_SERVER_URL` is configured and reachable, a connection to the OPC UA server is established (optional). If no server is reachable, the simulation may still run without an external OPC UA connection, depending on the implementation.
3. The production line is initialized: machines, buffers, and warehouse are set up with initial values such as `INITIAL_RAW_STOCK` and `BUFFER1_CAPACITY`.
4. The main simulation loop starts and performs cyclic work steps (processing, transfers, error handling).
5. Periodically (configurable), KPI values and states are collected and stored in `self.production_history`; read access is also provided for OPC UA or LLM integration.
6. Optional: the LLM integration can be called cyclically (for example every `SIMULATION_CYCLES_PER_LLM` cycles) to provide suggestions. Note: the LLM integration is demonstrative and has not been comprehensively tested — so far, a manual prompt has been used against `production.log` (see `manual_prompt.md`).

How to stop the programs correctly
-----------------------------------
- OPC UA server (Docker): run `docker-compose down` in the `docker` directory or use `docker stop <id>`.
- Client / simulation (`main.py`): press CTRL+C in the console. The program should shut down cleanly and flush logs. If it does not respond, terminate the process (Task Manager / `Stop-Process -Id <PID>` in PowerShell).

Where does which information go?
--------------------------------
- Log file: `production.log` (UTF-8) in the project root — contains continuous simulation logs, KPI values, events, and errors.
- Runtime console: important status messages and periodic overviews are printed to the console by default.
- In-memory history: the simulation stores detailed historical data in `self.production_history`. There are access methods such as `get_machine_data()`, `get_buffer_data()`, and `get_kpi_data()` (see `src/simulation/production_line.py`) — these are used, for example, by the OPC UA adapter or LLM generators.

Terminal output
---------------
- The simulation prints a detailed overview of machine, buffer, and warehouse states regularly, including fill levels, errors, and progress.
- KPI status messages appear at larger intervals as well.
- When using Docker, container logs can additionally be viewed with `docker logs <container-id>`.

OPC UA: Boiler 3 exercise & read/write access (Task 4)
------------------------------------------------------

In addition to the production-line nodes, the OPC UA server also exposes the
**"Boiler 3"** exercise object required by Task 4A. The standalone node
definition lives in `docker/opc-plc/boiler3-nodes.json` (the Task 4A deliverable).

Important: opc-plc's `--nodesfile` accepts only **one** file (unlike `--ns2` /
`--uanodesfile`, a second `--nodesfile` would override the first). The Boiler 3
nodes are therefore also included inside `docker/opc-plc/init-nodes.json` as a
`FolderList` child folder, so the single loaded `init-nodes.json` provides both
the production-line nodes and the Boiler 3 nodes. All Boiler 3 nodes are readable
and writable (`AccessLevel: CurrentReadOrWrite`, scalar `ValueRank: -1`) and
follow the NodeId schema `Boiler3_<Identifier>`:

| Variable            | DataType | NodeId                              |
|---------------------|----------|-------------------------------------|
| `TemperatureBottom` | Double   | `ns=3;s=Boiler3_Temperature_Bottom` |
| `TemperatureTop`    | Double   | `ns=3;s=Boiler3_Temperature_Top`    |
| `Pressure`          | Double   | `ns=3;s=Boiler3_Pressure`           |
| `HeaterState`       | Boolean  | `ns=3;s=Boiler3_HeaterState`        |

### Reading and writing process values (`rw_tool.py`)

While `main.py` continuously *writes* simulation data to the server, the small
CLI `src/opcua_client/rw_tool.py` demonstrates explicit **read and write**
access to individual process values (Task 4B). The OPC UA server must be running
first (see step 2 above).

```powershell
# Read a machine production counter
python -m src.opcua_client.rw_tool read machine Fraese1 Counter

# Start / stop a machine (writes the Status node: RUNNING=1 / IDLE=0)
python -m src.opcua_client.rw_tool start-machine Fraese1
python -m src.opcua_client.rw_tool stop-machine Fraese1

# Read all Boiler 3 values
python -m src.opcua_client.rw_tool read-boiler

# Write Boiler 3 values (Double, or true/false for HeaterState)
python -m src.opcua_client.rw_tool write-boiler TemperatureTop 68.5
python -m src.opcua_client.rw_tool write-boiler HeaterState true

# Generic access by raw NodeId
python -m src.opcua_client.rw_tool read-raw "ns=3;s=Boiler3_Pressure"
python -m src.opcua_client.rw_tool write-raw "ns=3;s=Boiler3_Pressure" 1.8 --type Double
```

The server URL defaults to `opc.tcp://localhost:50000` and can be overridden with
the `OPCUA_SERVER_URL` environment variable or the `--server` flag.

Diagrams and documentation
--------------------------
The UML and architecture diagrams are located in the `docs/` directory. Currently included:
- `docs/classes.png` and `docs/classes.puml` — class diagram
- `docs/components.png` and `docs/components.puml` — component overview
- `docs/production_flow-Produktionslinie___Flow_Diagram.png` and `docs/production_flow.puml` — production flow diagram

These PNG files can be used as a quick reference; the `.puml` files are the PlantUML sources.

LLM / AI integration (note)
---------------------------
- The LLM integration in `src/llm_integration/` is provided as an example implementation and has not been fully tested.
- So far, LLM behavior has only been checked manually using a prompt and `production.log`. This is not a production-ready solution.
- If you want to use the LLM integration, set `OPENAI_API_KEY` in your `.env` file and review the implementation in `src/llm_integration/`, especially `analyzer.py`, `optimizer.py`, and `prompts.py`.
- For a reproducible test path, `manual_prompt.md` contains an example prompt that was used when passing `production.log` to an LLM.

Tests and debugging
-------------------
- There are test scripts under `src/test_scripts/`, for example `test_opcua_connection.py`, `test_simulation_only.py`, and others. Use them as a starting point to verify functionality locally.
