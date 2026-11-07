# 1.4 Input, output and formatting text
# Example "table" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

items = [("Pen", 2, 10.0), ("Notebook", 3, 45.5), ("Bag", 1, 799.0)]
print(f"{'Item':<10}{'Qty':>5}{'Price':>10}{'Total':>10}")
print("-" * 35)
grand = 0
for name, qty, price in items:
    total = qty * price
    grand += total
    print(f"{name:<10}{qty:>5}{price:>10.2f}{total:>10.2f}")
print("-" * 35)
print(f"{'Grand total':<25}{grand:>10.2f}")
