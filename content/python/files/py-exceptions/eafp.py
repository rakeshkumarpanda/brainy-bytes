# 5.1 Exceptions: try, except, else, finally and raise
# Example "eafp" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

stock = {"pen": 12, "ink": 0}

# LBYL: look before you leap
if "cap" in stock:
    print(stock["cap"])
else:
    print("no cap (checked first)")

# EAFP: easier to ask forgiveness than permission
try:
    print(stock["cap"])
except KeyError:
    print("no cap (caught the error)")

# For this simple case the dict already has a tool
print(stock.get("cap", 0))
