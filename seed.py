from database import SessionLocal
from db_models import MenuItemDB, InventoryDB
from models import load_from_json

db = SessionLocal()

menu, inventory = load_from_json("menu.json")

for item in menu:
    db_item = MenuItemDB(name=item.name, price=item.price, category=item.category)
    db.add(db_item)

for item in inventory:
    db_inv = InventoryDB(
        name=item.name,
        quantity=item.quantity,
        low_stock_threshold=item.low_stock_threshold
    )
    db.add(db_inv)

db.commit()
db.close()

print("Database seeded successfully!")