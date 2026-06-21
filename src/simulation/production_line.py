import random
import os
from typing import List, Dict, Optional
from .machines import Machine, MachineStatus
from .buffers import Product, Buffer
from .warehouse import Warehouse


class ProductionLine:
    def __init__(self):

        self.scrap_chance = float(os.getenv("SCRAP_CHANCE", 0.05))
        # Maschinen mit Umgebungsvariablen initialisieren
        self.machines = [
            Machine(
                "Fraese1",
                float(os.getenv("MACHINE_FRAESE_CYCLE_TIME", 2.0)),
                float(os.getenv("MACHINE_FRAESE_ERROR_RATE", 0.02))
            ),
            Machine(
                "Drehbank1",
                float(os.getenv("MACHINE_DREHBANK_CYCLE_TIME", 1.5)),
                float(os.getenv("MACHINE_DREHBANK_ERROR_RATE", 0.01))
            ),
            Machine(
                "Bohrmaschine1",
                float(os.getenv("MACHINE_BOHR_CYCLE_TIME", 1.0)),
                float(os.getenv("MACHINE_BOHR_ERROR_RATE", 0.03))
            ),
            Machine(
                "Schleifmaschine1",
                float(os.getenv("MACHINE_SCHLEIF_CYCLE_TIME", 2.5)),
                float(os.getenv("MACHINE_SCHLEIF_ERROR_RATE", 0.02))
            )
        ]

        # Puffer mit Umgebungsvariablen
        self.buffers = [
            Buffer("Buffer1", int(os.getenv("BUFFER1_CAPACITY", 10))),
            Buffer("Buffer2", int(os.getenv("BUFFER2_CAPACITY", 15))),
            Buffer("Buffer3", int(os.getenv("BUFFER3_CAPACITY", 12)))
        ]

        # Lager
        # Wareneingangslager (Input-Lager) - wird nicht nachgefüllt
        self.input_warehouse = Warehouse(
            "Wareneingangslager",
            int(os.getenv("INPUT_WAREHOUSE_CAPACITY", 1000))
        )

        # Recyclinglager - unbegrenzte Kapazität (99999)
        self.recycling_warehouse = Warehouse(
            "Recyclinglager",
            int(os.getenv("RECYCLING_WAREHOUSE_CAPACITY", 99999))
        )

        # Fertigwarenlager - unbegrenzte Kapazität (99999)
        self.finished_goods = Warehouse(
            "Fertigwarenlager",
            int(os.getenv("FINISHED_GOODS_CAPACITY", 99999))
        )

        # Legacy: raw_material (jetzt alias zum input_warehouse)
        self.raw_material = self.input_warehouse

        # Initial Rohmaterial befüllen
        initial_stock = int(os.getenv("INITIAL_RAW_STOCK", 100))
        for i in range(initial_stock):
            self.input_warehouse.stock.append(
                Product(f"RAW_{i:06d}", "raw_material")
            )

        # Intervall für Materialtransport vom Wareneingangslager zum 1. Puffer
        self.input_interval = float(os.getenv("INPUT_WAREHOUSE_INTERVAL", 1.0))  # Sekunden
        self.time_since_last_input_transport = 0.0

        # Produktionsdaten mit History für Tracking
        self.total_produced = 0
        self.total_scrap = 0
        self.simulation_time = 0.0
        self.cycle_count = 0
        self.production_history: List[Dict] = []
        self.machine_history: Dict[str, List] = {m.name: [] for m in self.machines}

        # Qualitätsparameter aus .env
        self.quality_degradation = float(os.getenv("QUALITY_DEGRADATION_RATE", 0.01))
        self.quality_repair_bonus = float(os.getenv("QUALITY_REPAIR_BONUS", 5))
        self.max_quality = float(os.getenv("MAX_QUALITY", 100))
        self.min_quality = float(os.getenv("MIN_QUALITY", 80))

        # Fehlerparameter
        self.error_repair_chance = float(os.getenv("ERROR_REPAIR_CHANCE", 0.3))

    async def run_cycle(self) -> Dict:
        """Ein vollständiger Produktionszyklus mit Tracking"""
        events = []
        products_processed = {}
        dt = float(os.getenv("SIMULATION_SPEED", 0.1))

        # Maschinen updaten
        for machine in self.machines:
            machine.update(dt)

            # Fehlerbehandlung mit Repair-Chance
            if machine.status == MachineStatus.ERROR:
                if random.random() < self.error_repair_chance:
                    machine.repair()
                    events.append(f"✅ {machine.name} repariert")

        # Intervall-Timer für Materialtransport vom Wareneingangslager zum 1. Puffer
        self.time_since_last_input_transport += dt
        if self.time_since_last_input_transport >= self.input_interval:
            self.time_since_last_input_transport = 0.0
            # Versuche Material vom Wareneingangslager in den 1. Puffer zu transportieren
            # (nur wenn Kapazität nicht überschritten wird)
            if self.input_warehouse.stock_level > 0 and len(self.buffers[0].products) < self.buffers[0].capacity:
                raw_products = self.input_warehouse.retrieve(1)
                if raw_products:
                    product = raw_products[0]
                    if self.buffers[0].add_product(product):
                        events.append(f"📦 Rohmaterial von {self.input_warehouse.name} → {self.buffers[0].name}")
                        products_processed['input_to_buffer'] = products_processed.get('input_to_buffer', 0) + 1
                    else:
                        # Wenn Puffer voll, Material zurück ins Wareneingangslager
                        self.input_warehouse.stock.append(product)
                        events.append(f"⚠️ {self.buffers[0].name} voll - Material bleibt im Wareneingangslager")

        # Materialfluss: Buffer1 -> Maschine 1
        if self.machines[0].can_produce() and not self.buffers[0].is_empty:
            product = self.buffers[0].remove_product()
            if product:
                self.machines[0].start_production()
                events.append(f"🚀 {self.machines[0].name} startet mit Produkt aus {self.buffers[0].name}")
                products_processed['buffer_to_machine'] = products_processed.get('buffer_to_machine', 0) + 1

        # Materialfluss zwischen Maschinen über Puffer
        for i in range(len(self.machines) - 1):
            current_machine = self.machines[i]
            next_machine = self.machines[i + 1]
            buffer = self.buffers[i]

            # Wenn aktuelle Maschine fertig ist, Produkt in Puffer
            if current_machine.complete_cycle():
                product = Product(
                    f"P_{current_machine.name}_{current_machine.metrics.total_produced}",
                    f"semi_finished_{i}",
                    quality=current_machine.metrics.quality_rate
                )
                if buffer.add_product(product):
                    events.append(f"📦 Produkt von {current_machine.name} → {buffer.name}")
                    products_processed[f'{current_machine.name}_output'] = products_processed.get(
                        f'{current_machine.name}_output', 0) + 1
                else:
                    events.append(f"⚠️ {buffer.name} voll - Produktion gestoppt")
                    current_machine.status = MachineStatus.IDLE

            # Wenn nächste Maschine bereit und Puffer nicht leer
            if next_machine.can_produce() and not buffer.is_empty:
                product = buffer.remove_product()
                if product:
                    next_machine.start_production()
                    events.append(f"🚀 {next_machine.name} startet mit Produkt aus {buffer.name}")

        # Last Machine -> Fertigwarenlager
        last_machine = self.machines[-1]
        if last_machine.complete_cycle():
            product = Product(
                f"FINISHED_{self.total_produced:06d}",
                "finished_product",
                quality=last_machine.metrics.quality_rate
            )
            stored = self.finished_goods.store([product])
            if stored > 0:
                self.total_produced += 1
                events.append(f"✨ Fertigprodukt #{self.total_produced} eingelagert (Qualität: {product.quality:.1f}%)")
                products_processed['finished_goods'] = products_processed.get('finished_goods', 0) + 1
            else:
                events.append("⚠️ Fertigwarenlager voll!")

        # Qualitycheck mit Killrate
        if random.random() < self.scrap_chance:  # Ausschuss
            self.total_scrap += 1
            # Ausschuss ins Recyclinglager
            scrap_product = Product(
                f"SCRAP_{self.total_scrap:06d}",
                "scrap",
                quality=0.0
            )
            self.recycling_warehouse.store([scrap_product])
            events.append(f"⚠️ Ausschuss erzeugt und ins Recyclinglager (Total: {self.total_scrap})")

        # Simulation-Time update
        self.simulation_time += dt
        self.cycle_count += 1

        # History speichern
        cycle_data = {
            "cycle": self.cycle_count,
            "time": self.simulation_time,
            "produced": self.total_produced,
            "scrap": self.total_scrap,
            "events": events,
            "products": products_processed,
            "machines": self.get_machine_data(),
            "buffers": self.get_buffer_data(),
            "kpis": self.get_kpi_data()
        }
        self.production_history.append(cycle_data)

        # Maschinen-History aktualisieren
        for machine in self.machines:
            if machine.name not in self.machine_history:
                self.machine_history[machine.name] = []
            self.machine_history[machine.name].append({
                "time": self.simulation_time,
                "oee": machine.oee_component["oee"],
                "quality": machine.metrics.quality_rate,
                "status": machine.status.value,
                "produced": machine.metrics.total_produced
            })

        # Nur die letzten 1000 Einträge behalten
        if len(self.production_history) > 1000:
            self.production_history = self.production_history[-1000:]

        return cycle_data

    def get_machine_data(self) -> List[Dict]:
        """Machinedata for OPC-UA and LLM"""
        return [
            {
                "name": m.name,
                "status": m.status.name,
                "cycle_time": m.cycle_time,
                "error_rate": m.error_rate,
                "produced": m.metrics.total_produced,
                "errors": m.metrics.errors_count,
                "availability": m.metrics.availability,
                "performance": m.metrics.performance,
                "quality": m.metrics.quality_rate,
                "oee": m.oee_component["oee"],
                # expose remaining cycle time and progress for debugging/visualization
                "current_cycle_remaining": getattr(m, "current_cycle_remaining", 0.0),
                "progress": (max(0.0, min(1.0, 1.0 - getattr(m, "current_cycle_remaining", 0.0) / (m.cycle_time if m.cycle_time > 0 else 1.0)))) if m.status.name == "RUNNING" else 0.0,
                "energy": m.energy_consumption,
                "downtime": m.metrics.total_downtime,
                "runtime": m.metrics.total_runtime
            }
            for m in self.machines
        ]

    def get_buffer_data(self) -> List[Dict]:
        """Bufferdata for OPC-UA and LLM"""
        return [
            {
                "name": b.name,
                "fill_level": b.fill_level,
                "capacity": b.capacity,
                "current_count": len(b.products),
                "overflow": b.overflow_count,
                "starvation": b.starvation_count,
                "throughput": b.total_through
            }
            for b in self.buffers
        ]

    def get_kpi_data(self) -> Dict:
        """KPI-Data"""
        # OEE über alle Maschinen
        oee_values = [m.oee_component["oee"] for m in self.machines]
        avg_oee = sum(oee_values) / len(oee_values) if oee_values else 0

        # Stück pro Stunde
        hours = self.simulation_time / 3600 if self.simulation_time > 0 else 1
        throughput = self.total_produced / hours

        # Ausschussrate
        total_processed = self.total_produced + self.total_scrap
        scrap_rate = (self.total_scrap / total_processed * 100) if total_processed > 0 else 0

        # Auslastung
        running_machines = sum(1 for m in self.machines if m.status == MachineStatus.RUNNING)
        utilization = (running_machines / len(self.machines)) * 100

        return {
            "oee": avg_oee,
            "throughput": throughput,
            "scrap_rate": scrap_rate,
            "utilization": utilization,
            "total_produced": self.total_produced,
            "total_scrap": self.total_scrap,
            "simulation_time": self.simulation_time,
            "cycle_count": self.cycle_count
        }

    def get_machine_by_name(self, name: str) -> Optional[Machine]:
        """Holt eine Maschine anhand des Namens"""
        for machine in self.machines:
            if machine.name == name:
                return machine
        return None

    def get_buffer_by_name(self, name: str) -> Optional[Buffer]:
        """Holt einen Puffer anhand des Namens"""
        for buffer in self.buffers:
            if buffer.name == name:
                return buffer
        return None

    def get_production_flow(self) -> Dict:
        """Gibt den aktuellen Produktionsfluss zurück"""
        return {
            "input_warehouse_stock": self.input_warehouse.stock_level,
            "buffer_levels": [b.fill_level for b in self.buffers],
            "recycling_stock": self.recycling_warehouse.stock_level,
            "finished_stock": self.finished_goods.stock_level,
            "machine_status": [m.status.name for m in self.machines],
            "throughput": self.get_kpi_data()["throughput"]
        }