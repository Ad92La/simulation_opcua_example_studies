from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Product:
    id: str
    type: str
    quality: float = 100.0
    processing_time: float = 0.0


class Buffer:
    def __init__(self, name: str, capacity: int):
        self.name = name
        self.capacity = capacity
        self.products: List[Product] = []
        self.total_through = 0
        self.overflow_count = 0
        self.starvation_count = 0

    def add_product(self, product: Product) -> bool:
        if len(self.products) < self.capacity:
            self.products.append(product)
            return True
        self.overflow_count += 1
        return False

    def remove_product(self) -> Optional[Product]:
        if self.products:
            self.total_through += 1
            return self.products.pop(0)
        self.starvation_count += 1
        return None

    @property
    def fill_level(self) -> float:
        return (len(self.products) / self.capacity) * 100

    @property
    def is_empty(self) -> bool:
        return len(self.products) == 0

    @property
    def is_full(self) -> bool:
        return len(self.products) >= self.capacity

    @property
    def metrics(self) -> dict:
        return {
            "fill_level": self.fill_level,
            "current_count": len(self.products),
            "overflow_count": self.overflow_count,
            "starvation_count": self.starvation_count,
            "total_through": self.total_through
        }