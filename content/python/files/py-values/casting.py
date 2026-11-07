# 1.2 Variables, values, types and numeral systems
# Example "casting" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

print(int("42") + 1)        # text to whole number
print(float("3.5") * 2)     # text to decimal number
print(int(3.99))            # int() cuts off the decimals, it does not round
print(int(-3.99))           # cuts towards zero: -3
print(round(3.99), round(2.5), round(3.5))   # round() goes to the even number on a tie
print(str(7) + "7")         # number to text, then join
print(bool(0), bool(7), bool(""), bool("0"), bool([]))
print(float("inf") > 10**100)
try:
    int("3.5")
except ValueError as error:
    print("ValueError:", error)
