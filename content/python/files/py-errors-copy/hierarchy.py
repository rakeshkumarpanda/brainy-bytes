# 1.4 Exceptions in depth, copying and serialisation
# Example "hierarchy" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class ShopError(Exception):
    """The parent of every error this shop raises."""


class OutOfStock(ShopError):
    def __init__(self, item, wanted, left):
        super().__init__(f"{item}: wanted {wanted}, only {left} left")
        self.item = item
        self.left = left


class PaymentFailed(ShopError):
    pass


def buy(item, wanted):
    stock = {"pen": 3, "book": 0}
    if stock[item] < wanted:
        raise OutOfStock(item, wanted, stock[item])
    return "bought"


for item, n in [("pen", 2), ("pen", 5), ("book", 1)]:
    try:
        print(buy(item, n))
    except OutOfStock as err:
        print("OutOfStock:", err, "| left:", err.left, "| args:", err.args)
    except ShopError:
        print("some other shop problem")
