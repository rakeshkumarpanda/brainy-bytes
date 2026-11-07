# 1.1 Special methods and operator overloading
# Example "inplace" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Bag:
    def __init__(self):
        self.items = []

    def __iadd__(self, item):                  # bag += item changes the bag itself
        self.items.append(item)
        return self                            # += assigns whatever comes back

    def __repr__(self):
        return f"Bag({self.items})"


bag = Bag()
same = bag
bag += "pen"
bag += "book"
print(bag, same is bag)

nums = [1, 2]
alias = nums
nums += [3]                                    # list has __iadd__: changes in place
print(alias)
tup = (1, 2)
alias = tup
tup += (3,)                                    # tuple has no __iadd__: falls back to __add__, a new tuple
print(alias, tup)
