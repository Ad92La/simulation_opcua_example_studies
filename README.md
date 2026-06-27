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
