from models import load_from_json

menu, inventory = load_from_json("menu.json")

print("=== Menu ===")
for item in menu:
    print(item)

print("\n=== Inventory Status ===")
for item in inventory:
    print(item)

print("\n=== Low Stock Warnings ===")
low = [i for i in inventory if i.is_low()]
if low:
    for item in low:
        print(f"  Restock needed: {item.name} ({item.quantity} left)")
else:
    print("  All good!")