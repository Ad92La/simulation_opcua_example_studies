from dataclasses import dataclass
from enum import Enum
import random
from datetime import datetime
from typing import Optional

class MachineStatus(Enum):
    IDLE = 0
    RUNNING = 1
    ERROR = 2
    MAINTENANCE = 3
    SETUP = 4

@dataclass
class MachineMetrics:
    total_produced: int = 0
    total_downtime: float = 0
    total_runtime: float = 0
    errors_count: int = 0
    quality_rate: float = 100.0

    @property
    def availability(self) -> float:
        total_time = self.total_runtime + self.total_downtime
        return (self.total_runtime / total_time * 100) if total_time > 0 else 100

    @property
    def performance(self) -> float:
        return min(100, (self.total_produced / max(1, self.total_runtime / 60)) * 100)

class Machine:
    def __init__(self, name: str, cycle_time: float, error_rate: float):
        self.name = name
        self.cycle_time = cycle_time
        self.error_rate = error_rate
        self.status = MachineStatus.IDLE
        self.metrics = MachineMetrics()
        self.current_product_id: Optional[str] = None
        self.energy_consumption = 0.0
        self.last_status_change = datetime.now()
        # Neu: verbleibende Zeit für den aktuellen Zyklus in Sekunden
        self.current_cycle_remaining: float = 0.0

    def update(self, dt: float):
        """Update machine state based on time delta"""
        if self.status == MachineStatus.RUNNING:
            # Laufzeit / Energie akkumulieren
            self.metrics.total_runtime += dt
            self.energy_consumption += dt * random.uniform(2.0, 5.0)  # kW

            # Zyklusfortschritt reduzieren
            self.current_cycle_remaining = max(0.0, self.current_cycle_remaining - dt)

            # Quality degradation over time
            self.metrics.quality_rate -= dt * 0.01  # slow degradation
            self.metrics.quality_rate = max(80, self.metrics.quality_rate)

    def can_produce(self) -> bool:
        return self.status == MachineStatus.IDLE

    def start_production(self) -> bool:
        if self.can_produce():
            self.status = MachineStatus.RUNNING
            self.last_status_change = datetime.now()
            # Setze die verbleibende Zeit für den Zyklus
            self.current_cycle_remaining = float(self.cycle_time)
            return True
        return False

    def complete_cycle(self) -> bool:
        """
        Gibt True zurück, wenn ein Zyklus abgeschlossen wurde (Produkt fertig).
        Jetzt wird erst abgeschlossen, wenn current_cycle_remaining == 0.
        """
        if self.status == MachineStatus.RUNNING:
            # Wenn noch Restzeit vorhanden, noch nicht fertig
            if self.current_cycle_remaining > 0:
                return False

            # Error simulation beim Abschluss des Zyklus
            if random.random() < self.error_rate:
                self.status = MachineStatus.ERROR
                self.metrics.errors_count += 1
                self.last_status_change = datetime.now()
                return False

            # Zyklus abgeschlossen
            self.metrics.total_produced += 1
            self.status = MachineStatus.IDLE
            self.last_status_change = datetime.now()
            # Reset remaining just in case
            self.current_cycle_remaining = 0.0
            return True
        return False

    def repair(self):
        if self.status == MachineStatus.ERROR:
            self.status = MachineStatus.IDLE
            self.last_status_change = datetime.now()
            self.metrics.quality_rate = min(100, self.metrics.quality_rate + 5)

    @property
    def oee_component(self) -> dict:
        return {
            "availability": self.metrics.availability,
            "performance": self.metrics.performance,
            "quality": self.metrics.quality_rate,
            "oee": (self.metrics.availability * self.metrics.performance * self.metrics.quality_rate) / 10000
        }