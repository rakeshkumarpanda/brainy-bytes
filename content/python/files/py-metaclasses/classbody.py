# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "classbody" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

print("before the class")


class Shop:
    print("  the class body runs now, only once")
    tax = 0.18
    price = 100
    total = price * (1 + tax)                  # the body is normal code
    snapshot = dict(locals())                  # the namespace filled so far


print("after the class:", Shop.total)
print([k for k in Shop.snapshot if not k.startswith("__")])
print(Shop.__qualname__, Shop.__module__)
