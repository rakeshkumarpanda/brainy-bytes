# 3.4 Dictionaries: keys, values and hash tables
# Example "change" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

stock = {"apple": 10, "mango": 4}
stock["kiwi"] = 7            # a new key is added
stock["apple"] = 12          # an old key gets a new value
stock["mango"] += 1
print(stock)

del stock["kiwi"]            # remove, KeyError if missing
sold = stock.pop("apple")    # remove and return the value
print(sold, stock)
print(stock.pop("grape", 0)) # a default stops the KeyError
stock.update({"fig": 3, "mango": 9})
print(stock)
print(stock.popitem())       # removes the last added pair
print(stock)
