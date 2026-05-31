from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from db_models import MenuItemDB, InventoryDB, OrderDB, OrderItemDB
from order import Order
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
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
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/orders/history")
def get_order_history(db: Session = Depends(get_db)):
    orders = db.query(OrderDB).order_by(OrderDB.id.desc()).all()
    result = []
    for o in orders:
        items = db.query(OrderItemDB).filter(OrderItemDB.order_id == o.id).all()
        result.append({
            "id": o.id,
            "created_at": o.created_at,
            "items": [
                {
                    "name": i.menu_item_name,
                    "price": i.price,
                    "quantity": i.quantity,
                    "line_total": i.line_total
                }
                for i in items
            ],
            "subtotal": o.subtotal,
            "total": o.total,
            "payment_method": o.payment_method,
            "cash_received": o.cash_received,
            "change_due": o.change_due
        })
    return result

@app.get("/history")
def read_history():
    return FileResponse("static/history.html")

@app.get("/sales/summary")
def get_sales_summary(db: Session = Depends(get_db)):
    items = db.query(OrderItemDB).all()
    summary = {}
    for item in items:
        if item.menu_item_name not in summary:
            summary[item.menu_item_name] = {"quantity": 0, "revenue": 0.0}
        summary[item.menu_item_name]["quantity"] += item.quantity
        summary[item.menu_item_name]["revenue"] += item.line_total

    return [
        {"name": name, "quantity": data["quantity"], "revenue": round(data["revenue"], 2)}
        for name, data in sorted(summary.items(), key=lambda x: x[1]["quantity"], reverse=True)
    ]

@app.get("/sales")
def read_sales():
    return FileResponse("static/sales.html")