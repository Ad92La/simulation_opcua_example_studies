import asyncio
from asyncua import Client, ua
from typing import Dict, Any, List
from .node_manager import NodeMapping
import logging

logger = logging.getLogger(__name__)


class ProductionOPCUAClient:
    def __init__(self, server_url: str = "opc.tcp://localhost:50000"):
        self.server_url = server_url
        self.client = Client(url=server_url)
        self.nodes = NodeMapping()
        self.connected = False

    async def connect(self):
        """Verbindung zum OPC-PLC Server herstellen"""
        try:
            await self.client.connect()
            self.connected = True
            logger.info(f"✅ Connected to OPC-UA Server at {self.server_url}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to OPC-UA Server: {e}")
            raise

    async def disconnect(self):
        """Verbindung trennen"""
        if self.connected:
            await self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from OPC-UA Server")

    async def update_machine_data(self, machine_data: List[Dict]):
        """Maschinendaten auf OPC-UA Server schreiben"""
        if not self.connected:
            return

        for machine in machine_data:
            machine_name = machine["name"]
            if machine_name in self.nodes.machine_nodes:
                node_map = self.nodes.machine_nodes[machine_name]

                try:
                    # Status schreiben (Enum-Wert)
                    status_value = {
                        "IDLE": 0, "RUNNING": 1, "ERROR": 2,
                        "MAINTENANCE": 3, "SETUP": 4
                    }.get(machine["status"], 0)

                    await self.client.get_node(node_map["Status"]).write_value(
                        ua.DataValue(ua.Variant(status_value, ua.VariantType.Int32))
                    )

                    # Produktionszähler
                    await self.client.get_node(node_map["Counter"]).write_value(
                        ua.DataValue(ua.Variant(machine["produced"], ua.VariantType.Int32))
                    )

                    # Taktzeit
                    await self.client.get_node(node_map["CycleTime"]).write_value(
                        ua.DataValue(ua.Variant(machine["cycle_time"], ua.VariantType.Double))
                    )

                    # Fehlerrate
                    await self.client.get_node(node_map["ErrorRate"]).write_value(
                        ua.DataValue(ua.Variant(machine["error_rate"], ua.VariantType.Double))
                    )

                    # Energieverbrauch
                    await self.client.get_node(node_map["Energy"]).write_value(
                        ua.DataValue(ua.Variant(machine["energy"], ua.VariantType.Double))
                    )

                    # Qualität
                    await self.client.get_node(node_map["Quality"]).write_value(
                        ua.DataValue(ua.Variant(machine["quality"], ua.VariantType.Double))
                    )

                    # Produktionsrate (OEE)
                    await self.client.get_node(node_map["ProductionRate"]).write_value(
                        ua.DataValue(ua.Variant(machine["oee"], ua.VariantType.Double))
                    )

                except Exception as e:
                    logger.error(f"Failed to update {machine_name}: {e}")

    async def update_buffer_data(self, buffer_data: List[Dict]):
        """Pufferdaten auf OPC-UA Server schreiben"""
        if not self.connected:
            return

        for buffer in buffer_data:
            buffer_name = buffer["name"]
            if buffer_name in self.nodes.buffer_nodes:
                node_map = self.nodes.buffer_nodes[buffer_name]

                try:
                    # Füllstand
                    await self.client.get_node(node_map["Level"]).write_value(
                        ua.DataValue(ua.Variant(buffer["fill_level"], ua.VariantType.Double))
                    )

                    # Kapazität (nur bei Änderung)
                    capacity_node = self.client.get_node(node_map["Capacity"])
                    current_capacity = await capacity_node.read_value()
                    if current_capacity != buffer["capacity"]:
                        await capacity_node.write_value(
                            ua.DataValue(ua.Variant(buffer["capacity"], ua.VariantType.Int32))
                        )

                except Exception as e:
                    logger.error(f"Failed to update {buffer_name}: {e}")

    async def update_warehouse_data(self, warehouses: Dict[str, Any]):
        """Lagerdaten auf OPC-UA Server schreiben"""
        if not self.connected:
            return

        for warehouse_name, stock in warehouses.items():
            if warehouse_name in self.nodes.warehouse_nodes:
                node_id = self.nodes.warehouse_nodes[warehouse_name]

                try:
                    await self.client.get_node(node_id).write_value(
                        ua.DataValue(ua.Variant(stock, ua.VariantType.Int32))
                    )
                except Exception as e:
                    logger.error(f"Failed to update {warehouse_name}: {e}")

    async def update_kpi_data(self, kpis: Dict):
        """KPI-Daten auf OPC-UA Server schreiben"""
        if not self.connected:
            return

        for kpi_name, value in kpis.items():
            if kpi_name in self.nodes.kpi_nodes:
                node_id = self.nodes.kpi_nodes[kpi_name]

                try:
                    await self.client.get_node(node_id).write_value(
                        ua.DataValue(ua.Variant(value, ua.VariantType.Double))
                    )
                except Exception as e:
                    logger.error(f"Failed to update KPI {kpi_name}: {e}")

    async def update_all(self, production_line):
        """Alle Daten auf einmal aktualisieren"""
        if not self.connected:
            return

        # Maschinendaten
        machine_data = production_line.get_machine_data()
        await self.update_machine_data(machine_data)

        # Pufferdaten
        buffer_data = production_line.get_buffer_data()
        await self.update_buffer_data(buffer_data)

        # Lagerdaten
        warehouse_data = {
            "RawMaterial": production_line.raw_material.stock_level,
            "FinishedGoods": production_line.finished_goods.stock_level
        }
        await self.update_warehouse_data(warehouse_data)

        # KPIs
        kpi_data = production_line.get_kpi_data()
        await self.update_kpi_data(kpi_data)