"""Food Delivery Order Queue Manager."""

from datetime import datetime
import json
import pickle

# Global state
ORDERS = {}
NEXT_ID = 1
MENU = {}
VALID_STATUSES = ["placed", "cooking", "out_for_delivery", "delivered"]


def create_order(customer, items, order_history=None):
    """Create a new food delivery order and return its ID."""
    if order_history is None:
        order_history = []
    # pylint: disable=global-statement
    global NEXT_ID
    total = 0
    for item in items:
        total += MENU.get(item, 99)  # unknown dishes cost 99
    ORDERS[NEXT_ID] = {
        "customer": customer,
        "items": items,
        "total": total,
        "status": "placed",
    }
    order_history.append(NEXT_ID)
    NEXT_ID += 1
    return order_history[-1]


def update_order_status(order_id, status):
    """Update the status of an existing order safely."""
    try:
        ORDERS[order_id]["status"] = status
    except KeyError:
        pass


def read_menu_config(file="menu.json"):
    """Read menu configuration from file or use default."""
    # pylint: disable=global-statement
    global MENU
    try:
        with open(file, "r", encoding="utf-8") as f:
            MENU = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        MENU = {"pizza": 250, "burger": 150, "fries": 90, "coke": 40}


def daily_revenue():
    """Calculate total revenue for delivered orders."""
    revenue = 0
    for o in ORDERS:
        if ORDERS[o]["status"] == "delivered":
            revenue = revenue + ORDERS[o]["total"]
    return revenue


def backup_orders(file="orders.pkl"):
    """Backup orders to disk using pickle."""
    with open(file, "wb") as f:
        pickle.dump(ORDERS, f)


def restore_orders(file="orders.pkl"):
    """Restore orders from disk."""
    # pylint: disable=global-statement
    global ORDERS
    with open(file, "rb") as f:
        ORDERS = pickle.load(f)


def print_queue():
    """Print the current order queue."""
    print(f"Order queue at {datetime.now()}")
    for o in ORDERS:
        print(
            o,
            ORDERS[o]["customer"],
            ORDERS[o]["status"],
            ORDERS[o]["total"],
        )


def main():
    """Main execution flow."""
    read_menu_config()
    a = create_order("Asha", ["pizza", "coke"])
    b = create_order("Ravi", ["burger", "sushi"])
    c = create_order("", [])
    update_order_status(a, "delivered")
    update_order_status(b, "teleported")
    update_order_status(42, "delivered")
    update_order_status(c, "delivered")
    print("Revenue today:", daily_revenue())
    backup_orders()
    restore_orders()
    print_queue()


if __name__ == "__main__":
    main()
