# 5.1 Exceptions: try, except, else, finally and raise
# Example "order" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def check(value):
    try:
        return 10 / value
    except ZeroDivisionError:                  # the most specific first
        return "zero"
    except ArithmeticError:                    # its parent class
        return "some other arithmetic problem"
    except Exception as err:                   # almost everything
        return "other: " + type(err).__name__

print(check(0))
print(check(10 ** 400))        # too big for a float: OverflowError, a child of ArithmeticError
print(check("x"))
print(issubclass(ZeroDivisionError, ArithmeticError), issubclass(KeyError, LookupError))
print([c.__name__ for c in ZeroDivisionError.__mro__])
