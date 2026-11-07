# 3.3 Logging and debugging
# Example "debugging" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

scores = [70, 80, 90]
total = 0
for s in scores:
    total = s                                  # the bug: it should be total += s
    print(f"{s=} {total=}")                    # = prints the name AND the value
print(f"{total / len(scores)=:.1f}")


def apply_discount(price, percent):
    assert 0 <= percent <= 100, f"bad percent: {percent}"
    return price * (100 - percent) / 100


print(apply_discount(200, 10))
try:
    apply_discount(200, 150)
except AssertionError as err:
    print("AssertionError:", err)
print("asserts are on:", __debug__)            # python -O turns them off
