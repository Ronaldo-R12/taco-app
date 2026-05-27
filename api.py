from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from db_models import MenuItemDB, InventoryDB, OrderDB, OrderItemDB
from order import Order
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class OrderRequest(BaseModel):
    items: list[dict]
    payment_method: str
    cash_received: float = 0.0

@app.get("/menu")
def get_menu(db: Session = Depends(get_db)):
    items = db.query(MenuItemDB).all()
    return [
        {"id": item.id, "name": item.name, "price": item.price, "category": item.category}
        for item in items
    ]

@app.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    items = db.query(InventoryDB).all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "low_stock": item.quantity <= item.low_stock_threshold
        }
        for item in items
    ]

@app.post("/orders")
def create_order(request: OrderRequest, db: Session = Depends(get_db)):
    print("Order received:", request)
    order = Order()

    for entry in request.items:
        menu_item = db.query(MenuItemDB).filter(MenuItemDB.name == entry["name"]).first()
        if not menu_item:
            return {"error": f"Item '{entry['name']}' not found"}
        from models import MenuItem
        item = MenuItem(name=menu_item.name, price=menu_item.price, category=menu_item.category)
        order.add_item(item, entry["quantity"])

    print("Order empty?", order.is_empty())
    print("Order total:", order.total)
    if order.is_empty():
        return {"error": "Order is empty"}

    order.payment_method = request.payment_method
    order.cash_received = request.cash_received

    db_order = OrderDB(
        created_at=datetime.now().strftime("%b %d, %Y %I:%M %p"),
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
        payment_method=order.payment_method,
        cash_received=order.cash_received,
        change_due=order.change_due
    )
    db.add(db_order)
    db.flush()
    print("Order saved to DB with id:", db_order.id)

    for order_item in order.items:
        db_item = OrderItemDB(
            order_id=db_order.id,
            menu_item_name=order_item.menu_item.name,
            price=order_item.menu_item.price,
            quantity=order_item.quantity,
            line_total=order_item.line_total
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return {
        "order_id": db_order.id,
        "subtotal": order.subtotal,
        "tax": order.tax,
        "total": order.total,
        "change_due": order.change_due
    }