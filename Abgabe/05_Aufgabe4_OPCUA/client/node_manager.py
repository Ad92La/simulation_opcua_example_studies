from asyncua import Client, ua
from typing import Dict, Any, List


class NodeMapping:
    """Mapping zwischen Simulationsobjekten und OPC-UA Nodes"""

    def __init__(self):
        self.machine_nodes = {
            "Fraese1": {
                "Status": "ns=3;s=ProductionLine_Machines_Fraese1_Status",
                "Counter": "ns=3;s=ProductionLine_Machines_Fraese1_Counter",
                "CycleTime": "ns=3;s=ProductionLine_Machines_Fraese1_CycleTime",
                "ErrorRate": "ns=3;s=ProductionLine_Machines_Fraese1_ErrorRate",
                "ProductionRate": "ns=3;s=ProductionLine_Machines_Fraese1_ProductionRate",
                "Energy": "ns=3;s=ProductionLine_Machines_Fraese1_EnergyConsumption",
                "Quality": "ns=3;s=ProductionLine_Machines_Fraese1_Quality"
            },
            "Drehbank1": {
                "Status": "ns=3;s=ProductionLine_Machines_Drehbank1_Status",
                "Counter": "ns=3;s=ProductionLine_Machines_Drehbank1_Counter",
                "CycleTime": "ns=3;s=ProductionLine_Machines_Drehbank1_CycleTime",
                "ErrorRate": "ns=3;s=ProductionLine_Machines_Drehbank1_ErrorRate",
                "ProductionRate": "ns=3;s=ProductionLine_Machines_Drehbank1_ProductionRate",
                "Energy": "ns=3;s=ProductionLine_Machines_Drehbank1_EnergyConsumption",
                "Quality": "ns=3;s=ProductionLine_Machines_Drehbank1_Quality"
            },
            "Bohrmaschine1": {
                "Status": "ns=3;s=ProductionLine_Machines_Bohrmaschine1_Status",
                "Counter": "ns=3;s=ProductionLine_Machines_Bohrmaschine1_Counter",
                "CycleTime": "ns=3;s=ProductionLine_Machines_Bohrmaschine1_CycleTime",
                "ErrorRate": "ns=3;s=ProductionLine_Machines_Bohrmaschine1_ErrorRate",
                "ProductionRate": "ns=3;s=ProductionLine_Machines_Bohrmaschine1_ProductionRate",
                "Energy": "ns=3;s=ProductionLine_Machines_Bohrmaschine1_EnergyConsumption",
                "Quality": "ns=3;s=ProductionLine_Machines_Bohrmaschine1_Quality"
            },
            "Schleifmaschine1": {
                "Status": "ns=3;s=ProductionLine_Machines_Schleifmaschine1_Status",
                "Counter": "ns=3;s=ProductionLine_Machines_Schleifmaschine1_Counter",
                "CycleTime": "ns=3;s=ProductionLine_Machines_Schleifmaschine1_CycleTime",
                "ErrorRate": "ns=3;s=ProductionLine_Machines_Schleifmaschine1_ErrorRate",
                "ProductionRate": "ns=3;s=ProductionLine_Machines_Schleifmaschine1_ProductionRate",
                "Energy": "ns=3;s=ProductionLine_Machines_Schleifmaschine1_EnergyConsumption",
                "Quality": "ns=3;s=ProductionLine_Machines_Schleifmaschine1_Quality"
            }
        }

        self.buffer_nodes = {
            "Buffer1": {
                "Level": "ns=3;s=ProductionLine_Buffers_Buffer1_Level",
                "Capacity": "ns=3;s=ProductionLine_Buffers_Buffer1_Capacity"
            },
            "Buffer2": {
                "Level": "ns=3;s=ProductionLine_Buffers_Buffer2_Level",
                "Capacity": "ns=3;s=ProductionLine_Buffers_Buffer2_Capacity"
            },
            "Buffer3": {
                "Level": "ns=3;s=ProductionLine_Buffers_Buffer3_Level",
                "Capacity": "ns=3;s=ProductionLine_Buffers_Buffer3_Capacity"
            }
        }

        self.warehouse_nodes = {
            "RawMaterial": "ns=3;s=ProductionLine_Warehouses_RawMaterial_Stock",
            "FinishedGoods": "ns=3;s=ProductionLine_Warehouses_FinishedGoods_Stock"
        }

        self.kpi_nodes = {
            "OEE": "ns=3;s=ProductionLine_KPIs_OEE",
            "Throughput": "ns=3;s=ProductionLine_KPIs_Throughput",
            "ScrapRate": "ns=3;s=ProductionLine_KPIs_ScrapRate",
            "Utilization": "ns=3;s=ProductionLine_KPIs_Utilization"
        }

        # Task 4A: "Boiler 3" exercise nodes (defined in docker/opc-plc/boiler3-nodes.json).
        # NodeIds follow the schema Boiler3_<Identifier> and are read- and writable.
        self.boiler_nodes = {
            "TemperatureBottom": "ns=3;s=Boiler3_Temperature_Bottom",
            "TemperatureTop": "ns=3;s=Boiler3_Temperature_Top",
            "Pressure": "ns=3;s=Boiler3_Pressure",
            "HeaterState": "ns=3;s=Boiler3_HeaterState",
        }