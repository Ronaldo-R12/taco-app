import json 
class MenuItem:
    def __init__(self, name: str, price: float, category: str):
        self.name = name
        self.price = price
        self.category = category

    def __repr__(self):
        return f"{self.name} ({self.category}) - ${self.price:.2f}"


class InventoryItem:
    def __init__(self, name: str, quantity: int, low_stock_threshold: int = 5):
        self.name = name
        self.quantity = quantity
        self.low_stock_threshold = low_stock_threshold

    def is_low(self) -> bool:
        return self.quantity <= self.low_stock_threshold

    def restock(self, amount: int):
        self.quantity += amount

    def use(self, amount: int = 1):
        if amount > self.quantity:
            raise ValueError(f"Not enough {self.name} in stock")
        self.quantity -= amount

    def __repr__(self):
        status = " [LOW]" if self.is_low() else ""
        return f"{self.name}: {self.quantity} units{status}"

def load_from_json(filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)

    menu = [
        MenuItem(
            name=item["name"],
            price=item["price"],
            category=item["category"]
        )
        for item in data["menu"]
    ]

    inventory = [
        InventoryItem(
            name=item["name"],
            quantity=item["quantity"],
            low_stock_threshold=item.get("low_stock_threshold", 5)
        )
        for item in data["inventory"]
    ]

    return menu, inventory