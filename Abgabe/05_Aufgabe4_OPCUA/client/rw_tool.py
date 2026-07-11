"""
OPC UA Read/Write command line tool (Task 4B).

The existing ``ProductionOPCUAClient`` only *writes* simulation data to the
OPC UA server. Task 4 additionally requires small programs that explicitly
*read* and *write* process values (e.g. start/stop a machine or query
counters). This module provides exactly that as a small, self-contained CLI.

It also covers the "Boiler 3" exercise nodes (Task 4A), so the read/write
capability can be demonstrated without the full simulation running.

Examples
--------
Read a machine production counter::

    python -m src.opcua_client.rw_tool read machine Fraese1 Counter

Start / stop a machine (writes the Status node)::

    python -m src.opcua_client.rw_tool start-machine Fraese1
    python -m src.opcua_client.rw_tool stop-machine Fraese1

Read all Boiler 3 values::

    python -m src.opcua_client.rw_tool read-boiler

Write a Boiler 3 value::

    python -m src.opcua_client.rw_tool write-boiler TemperatureTop 68.5
    python -m src.opcua_client.rw_tool write-boiler HeaterState true

Read / write any node by its raw NodeId::

    python -m src.opcua_client.rw_tool read-raw "ns=3;s=Boiler3_Pressure"
    python -m src.opcua_client.rw_tool write-raw "ns=3;s=Boiler3_Pressure" 1.8 --type Double
"""

import argparse
import asyncio
import os

from asyncua import Client, ua

from .node_manager import NodeMapping

DEFAULT_SERVER_URL = os.environ.get("OPCUA_SERVER_URL", "opc.tcp://localhost:50000")


class PatchedClient(Client):
    """Client that blanks the ServerUri during session creation.

    The Microsoft opc-plc Docker server advertises a ServerUri that does not
    match its endpoint URL, which makes a plain asyncua session fail. This patch
    (taken from the lecture example 19b) strips the ServerUri so the session is
    accepted. Combined with ``endpoint_must_exist = False`` it connects reliably
    to the Docker test server.
    """

    async def create_session(self):
        original = self.uaclient.create_session

        async def _stripped(params: ua.CreateSessionParameters):
            params.ServerUri = ""
            return await original(params)

        self.uaclient.create_session = _stripped
        try:
            return await super().create_session()
        finally:
            self.uaclient.create_session = original

# Machine status enum (mirrors ProductionOPCUAClient.update_machine_data).
MACHINE_STATUS = {
    "IDLE": 0,
    "RUNNING": 1,
    "ERROR": 2,
    "MAINTENANCE": 3,
    "SETUP": 4,
}

# Variant type per Boiler 3 variable (matches boiler3-nodes.json).
BOILER_TYPES = {
    "TemperatureBottom": ua.VariantType.Double,
    "TemperatureTop": ua.VariantType.Double,
    "Pressure": ua.VariantType.Double,
    "HeaterState": ua.VariantType.Boolean,
}


def _parse_value(raw: str, variant_type: ua.VariantType):
    """Convert a CLI string into a correctly typed Python value."""
    if variant_type == ua.VariantType.Boolean:
        return raw.strip().lower() in ("1", "true", "on", "yes", "ja")
    if variant_type in (ua.VariantType.Double, ua.VariantType.Float):
        return float(raw)
    if variant_type in (ua.VariantType.Int32, ua.VariantType.Int16, ua.VariantType.Int64):
        return int(raw)
    return raw


async def _read(client: Client, node_id: str):
    value = await client.get_node(node_id).read_value()
    return value


async def _write(client: Client, node_id: str, value, variant_type: ua.VariantType):
    await client.get_node(node_id).write_value(
        ua.DataValue(ua.Variant(value, variant_type))
    )


async def run(args) -> int:
    nodes = NodeMapping()
    client = PatchedClient(url=args.server)
    client.uaclient.endpoint_must_exist = False
    try:
        await client.connect()
    except Exception as exc:  # noqa: BLE001 - CLI wants a friendly message
        print(f"[ERROR] Could not connect to OPC UA server at {args.server}: {exc}")
        print("        Is the opc-plc Docker container running? (see README)")
        return 2

    try:
        if args.command == "read":
            group = getattr(nodes, f"{args.group}_nodes")
            node_id = group[args.name][args.variable]
            value = await _read(client, node_id)
            print(f"{args.group}/{args.name}/{args.variable} = {value}")

        elif args.command in ("start-machine", "stop-machine"):
            status_value = MACHINE_STATUS["RUNNING" if args.command == "start-machine" else "IDLE"]
            node_id = nodes.machine_nodes[args.name]["Status"]
            await _write(client, node_id, status_value, ua.VariantType.Int32)
            print(f"{args.name} status set to "
                  f"{'RUNNING (1)' if status_value == 1 else 'IDLE (0)'}")

        elif args.command == "read-boiler":
            print("Boiler 3 process values:")
            for variable, node_id in nodes.boiler_nodes.items():
                value = await _read(client, node_id)
                print(f"  {variable:18s} = {value}")

        elif args.command == "write-boiler":
            variant_type = BOILER_TYPES[args.variable]
            value = _parse_value(args.value, variant_type)
            await _write(client, nodes.boiler_nodes[args.variable], value, variant_type)
            print(f"Boiler3/{args.variable} written = {value}")

        elif args.command == "read-raw":
            value = await _read(client, args.node_id)
            print(f"{args.node_id} = {value}")

        elif args.command == "write-raw":
            variant_type = getattr(ua.VariantType, args.type)
            value = _parse_value(args.value, variant_type)
            await _write(client, args.node_id, value, variant_type)
            print(f"{args.node_id} written = {value} ({args.type})")

        else:  # pragma: no cover - argparse prevents this
            print("Unknown command")
            return 1
    except KeyError as exc:
        print(f"[ERROR] Unknown node/name: {exc}")
        return 1
    finally:
        await client.disconnect()

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read and write OPC UA process values (Task 4B)."
    )
    parser.add_argument(
        "--server", default=DEFAULT_SERVER_URL,
        help=f"OPC UA server URL (default: {DEFAULT_SERVER_URL})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_read = sub.add_parser("read", help="Read a mapped node value")
    p_read.add_argument("group", choices=["machine", "buffer", "warehouse", "kpi"])
    p_read.add_argument("name", help="e.g. Fraese1, Buffer1, RawMaterial")
    p_read.add_argument("variable", help="e.g. Counter, Status, Level")

    p_start = sub.add_parser("start-machine", help="Set a machine Status to RUNNING")
    p_start.add_argument("name", help="e.g. Fraese1")

    p_stop = sub.add_parser("stop-machine", help="Set a machine Status to IDLE")
    p_stop.add_argument("name", help="e.g. Fraese1")

    sub.add_parser("read-boiler", help="Read all Boiler 3 values")

    p_wb = sub.add_parser("write-boiler", help="Write a Boiler 3 value")
    p_wb.add_argument("variable", choices=list(BOILER_TYPES.keys()))
    p_wb.add_argument("value", help="Numeric value, or true/false for HeaterState")

    p_rr = sub.add_parser("read-raw", help="Read any node by NodeId")
    p_rr.add_argument("node_id", help='e.g. "ns=3;s=Boiler3_Pressure"')

    p_wr = sub.add_parser("write-raw", help="Write any node by NodeId")
    p_wr.add_argument("node_id")
    p_wr.add_argument("value")
    p_wr.add_argument("--type", default="Double",
                      help="Variant type: Double, Int32, Boolean, ... (default: Double)")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
