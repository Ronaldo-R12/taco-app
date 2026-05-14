from models import load_from_json
from order import Order

menu, inventory = load_from_json("menu.json")

#simulate an order 
order = Order()
order.add_item(menu[0], 2) #2 tacos de carne 
order.add_item(menu[3], 1) #1 coke 
order.add_item(menu[0], 1) #1 more taco de carne (should combine to 3)

print("=== Order ===")
print(order)

#simulate cash payment 
order.payment_method = "cash"
order.cash_received = 20.0 
print(f"\nCash received: ${order.cash_received:.2f}")
print(f"Change due:    ${order.change_due:.2f}")

#save it
order_id = order.save()
print(f"\nOrder #{order_id} saved to orders.json")