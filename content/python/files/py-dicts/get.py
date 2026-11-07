# 3.4 Dictionaries: keys, values and hash tables
# Example "get" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

prices = {"tea": 10, "coffee": 25}
try:
    print(prices["juice"])
except KeyError as err:
    print("KeyError:", err)

print(prices.get("juice"))          # None, no error
print(prices.get("juice", 0))       # your own default
print(prices.setdefault("juice", 15), prices)   # adds it if missing
print(prices.setdefault("tea", 99), prices)     # keeps the old value
