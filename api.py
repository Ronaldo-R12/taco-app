from fastapi import FastAPI
from models import load_from_json
from order import Order, OrderItem
from pydantic import BaseModel

app = FastAPI()

menu, inventory = load_from_json("menu.json")

class OrderRequest(BaseModel):
    items: list[dict]
    payment_method: str
    cash_received: float = 0.0

@app.get("/menu")
def get_menu():
    return [
        {"name": item.name, "price": item.price, "category": item.category}
        for item in menu
    ]

@app.get("/inventory")
def get_inventory():
    return [
        {"name": item.name, "quantity": item.quantity, "low_stock": item.is_low()}
        for item in inventory
    ]

@app.post("/orders")
def create_order(request: OrderRequest):
    order = Order()

    for entry in request.items:
        menu_item = next((m for m in menu if m.name == entry["name"]), None)
        if not menu_item:
            return {"error": f"Item '{entry['name']}' not found"}
        order.add_item(menu_item, entry["quantity"])

    if order.is_empty():
        return {"error": "Order is empty"}

    order.payment_method = request.payment_method
    order.cash_received = request.cash_received
    order_id = order.save()

    return {
        "order_id": order_id,
        "subtotal": order.subtotal,
        "tax": order.tax,
        "total": order.total,
        "change_due": order.change_due
    }