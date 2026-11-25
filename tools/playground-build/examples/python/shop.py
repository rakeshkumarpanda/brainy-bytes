def line_total(price, qty):
    return price * qty

items = ["Notebook", "Pencil", "Water bottle"]
prices = [45, 10, 120]
qty = [3, 5, 1]

bill = 0
for i in range(len(items)):
    cost = line_total(prices[i], qty[i])
    print(items[i], "x", qty[i], "=", cost)
    bill += cost

if bill > 200:
    bill = bill - bill // 10    # 10% off on big bills
print("You pay:", bill, "rupees")
