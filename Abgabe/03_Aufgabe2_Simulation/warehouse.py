from typing import List, Dict
from .buffers import Product


class Warehouse:
    def __init__(self, name: str, capacity: int):
        self.name = name
        self.capacity = capacity
        self.stock: List[Product] = []
        self.stock_history: List[int] = []

    def store(self, products: List[Product]) -> int:
        available_space = self.capacity - len(self.stock)
        to_store = min(available_space, len(products))
        self.stock.extend(products[:to_store])
        return to_store

    def retrieve(self, quantity: int) -> List[Product]:
        to_retrieve = min(quantity, len(self.stock))
        products = self.stock[:to_retrieve]
        self.stock = self.stock[to_retrieve:]
        return products

    @property
    def stock_level(self) -> int:
        return len(self.stock)

    @property
    def utilization(self) -> float:
        return (len(self.stock) / self.capacity) * 100 if self.capacity > 0 else 0