import asyncio
import logging
from typing import Dict, Optional, List
from .analyzer import ProductionLLMAnalyzer
from ..simulation.production_line import ProductionLine

logger = logging.getLogger(__name__)


class LLMOptimizer:
    """Wendet LLM-Vorschläge auf die Simulation an"""

    def __init__(self, production_line: ProductionLine, analyzer: ProductionLLMAnalyzer):
        self.production_line = production_line
        self.analyzer = analyzer
        self.applied_optimizations = []

    async def optimize_cycle(self) -> Optional[Dict]:
        """Ein Optimierungszyklus - sammelt Daten, analysiert und wendet an"""

        # Aktuelle Daten sammeln
        simulation_data = self._collect_data()

        # LLM-Analyse durchführen (nur wenn sinnvoll)
        analysis = await self.analyzer.analyze(simulation_data)

        if analysis is None:
            return None

        # Optimierungen anwenden
        applied = await self._apply_suggestions(analysis)

        return {
            "analysis": analysis,
            "applied": applied,
            "timestamp": simulation_data["simulation_time"]
        }

    def _collect_data(self) -> Dict:
        """Sammelt alle relevanten Daten für die LLM-Analyse"""
        return {
            "machines": self.production_line.get_machine_data(),
            "buffers": self.production_line.get_buffer_data(),
            "kpis": self.production_line.get_kpi_data(),
            "raw_stock": self.production_line.raw_material.stock_level,
            "finished_stock": self.production_line.finished_goods.stock_level,
            "simulation_time": self.production_line.simulation_time
        }

    async def _apply_suggestions(self, analysis: Dict) -> List[Dict]:
        """Wendet die LLM-Vorschläge auf die Simulation an"""
        applied = []

        # Parametersvorschläge anwenden
        param_suggestions = analysis.get("parameter_suggestions", {})

        # Maschinenparameter anpassen
        for adj in param_suggestions.get("machine_adjustments", []):
            machine_name = adj.get("machine")
            parameter = adj.get("parameter")
            suggested_value = adj.get("suggested_value")

            if machine_name and parameter and suggested_value:
                success = self._adjust_machine(machine_name, parameter, suggested_value)
                if success:
                    applied.append({
                        "type": "machine_adjustment",
                        "machine": machine_name,
                        "parameter": parameter,
                        "value": suggested_value
                    })

        # Pufferkapazitäten anpassen
        for adj in param_suggestions.get("buffer_adjustments", []):
            buffer_name = adj.get("buffer")
            suggested_capacity = adj.get("suggested_capacity")

            if buffer_name and suggested_capacity:
                success = self._adjust_buffer(buffer_name, suggested_capacity)
                if success:
                    applied.append({
                        "type": "buffer_adjustment",
                        "buffer": buffer_name,
                        "capacity": suggested_capacity
                    })

        self.applied_optimizations.extend(applied)
        logger.info(f"Applied {len(applied)} optimizations")
        return applied

    def _adjust_machine(self, name: str, parameter: str, value: float) -> bool:
        """Passt Maschinenparameter an"""
        for machine in self.production_line.machines:
            if machine.name == name:
                if parameter == "taktzeit":
                    machine.cycle_time = max(0.5, value)  # Minimum 0.5s
                    return True
                elif parameter == "fehlerrate":
                    machine.error_rate = max(0.001, min(0.5, value))  # 0.1% - 50%
                    return True
        return False

    def _adjust_buffer(self, name: str, capacity: int) -> bool:
        """Passt Pufferkapazität an"""
        for buffer in self.production_line.buffers:
            if buffer.name == name:
                buffer.capacity = max(1, min(100, int(capacity)))
                return True
        return False