from datetime import datetime
import zoneinfo
from models import MenuItem
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()
TAX_RATE = float(os.getenv("TAX_RATE", 0.0))

class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int):
        self.menu_item = menu_item
        self.quantity = quantity

    @property
    def line_total(self) -> float:
        return round(self.menu_item.price * self.quantity, 2)

    def __repr__(self):
        return f"{self.quantity}x {self.menu_item.name} @ ${self.menu_item.price:.2f} = ${self.line_total:.2f}"


class Order:
    def __init__(self):
        self.items: list[OrderItem] = []
        self.payment_method: str = ""
        self.cash_received: float = 0.0
        tz = zoneinfo.ZoneInfo("America/Los_Angeles")
        self.created_at: str = datetime.now(tz).strftime("%b %d, %Y %I:%M %p")

    def add_item(self, menu_item: MenuItem, quantity: int):
        for order_item in self.items:
            if order_item.menu_item.name == menu_item.name:
                order_item.quantity += quantity
                return
        self.items.append(OrderItem(menu_item, quantity))

    def remove_item(self, item_name: str):
        self.items = [i for i in self.items if i.menu_item.name != item_name]

    @property
    def subtotal(self) -> float:
        return round(sum(item.line_total for item in self.items), 2)

    @property
    def tax(self) -> float:
        return round(self.subtotal * TAX_RATE, 2)

    @property
    def total(self) -> float:
        return round(self.subtotal + self.tax, 2)

    @property
    def change_due(self) -> float:
        if self.payment_method == "cash":
            return round(self.cash_received - self.total, 2)
        return 0.0

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def to_dict(self) -> dict:
        return {
            "created_at": self.created_at,
            "items": [
                {
                    "name": i.menu_item.name,
                    "price": i.menu_item.price,
                    "quantity": i.quantity,
                    "line_total": i.line_total
                }
                for i in self.items
            ],
            "subtotal": self.subtotal,
            "tax": self.tax,
            "total": self.total,
            "payment_method": self.payment_method,
            "cash_received": self.cash_received,
            "change_due": self.change_due
        }

    def save(self):
        try:
            with open("orders.json", "r") as f:
                orders = json.load(f)
        except FileNotFoundError:
            orders = []

        order_data = self.to_dict()
        order_data["id"] = len(orders) + 1
        orders.append(order_data)

        with open("orders.json", "w") as f:
            json.dump(orders, f, indent=2)

        return order_data["id"]

    def __repr__(self):
        lines = [str(item) for item in self.items]
        lines.append(f"Subtotal: ${self.subtotal:.2f}")
        lines.append(f"Tax:      ${self.tax:.2f}")
        lines.append(f"Total:    ${self.total:.2f}")
        return "\n".join(lines)


