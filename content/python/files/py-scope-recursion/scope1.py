# 4.2 Scope and recursion: LEGB, closures and the call stack
# Example "scope1" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

tax_rate = 0.18                 # global: made at the top level of the file

def price_with_tax(price):
    tax = price * tax_rate      # tax is local: it exists only during this call
    return price + tax

print(price_with_tax(100))
print(tax_rate)                 # the global is visible everywhere
try:
    print(tax)                  # the local is gone after the call
except NameError as err:
    print("NameError:", err)
