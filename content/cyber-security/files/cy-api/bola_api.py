# 4.4 API security: BOLA, rate limits, mass assignment and the OWASP API Top 10
# Example "bola_api" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A tiny orders API, first without and then with an owner check (all data made up)
ORDERS = {
    1001: {"owner": "mallory", "item": "2 phone cases"},
    1002: {"owner": "asha", "item": "laptop", "address": "14 Lake Rd"},
    1003: {"owner": "ravi", "item": "headphones", "address": "7 Hill St"},
}

def get_order_unsafe(caller, order_id):
    # checks only that the caller is logged in
    if caller is None:
        return 401, "log in first"
    order = ORDERS.get(order_id)
    return (200, order) if order else (404, "not found")

def get_order_safe(caller, order_id):
    if caller is None:
        return 401, "log in first"
    order = ORDERS.get(order_id)
    if order is None or order["owner"] != caller:
        # answer 404 for both cases so an attacker cannot even learn which IDs exist
        return 404, "not found"
    return 200, order

for fn in (get_order_unsafe, get_order_safe):
    print(fn.__name__)
    for oid in (1001, 1002, 1003):
        code, body = fn("mallory", oid)
        print(f"  mallory asks for {oid}: {code} {body}")
