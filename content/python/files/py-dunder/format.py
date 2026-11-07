# 1.1 Special methods and operator overloading
# Example "format" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Money:
    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):                        # for developers
        return f"Money({self.amount!r})"

    def __str__(self):                         # for users
        return f"Rs {self.amount:,.2f}"

    def __format__(self, spec):                # f"{m:...}" and format(m, ...)
        if spec == "words":
            return f"{self.amount} rupees"
        return "Rs " + format(self.amount, spec)


m = Money(1234567.5)
print(repr(m))
print(str(m))
print(f"{m:,.0f} | {m:words} | {m:>12.1f}")
print([m])
