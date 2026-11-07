# 5.1 Exceptions: try, except, else, finally and raise
# Example "multi" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "cannot divide by zero"
    except TypeError as err:          # as err gives you the exception object
        return f"wrong types: {err}"

print(safe_divide(10, 4))
print(safe_divide(10, 0))
print(safe_divide(10, "2"))

prices = {"tea": 10}
for item in ["tea", "cake", 5]:
    try:
        print(item, prices[item] * 2)
    except (KeyError, TypeError) as err:      # one handler, two kinds
        print("problem:", type(err).__name__, err.args)
