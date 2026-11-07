# 1.1 What a program is and your first Python program
# Example "count" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# How many characters does a print() write? Count them, then check with len()
values = ["Total", 3, "apples"]
sep = " "
end = "\n"

text = sep.join(str(v) for v in values) + end
by_formula = sum(len(str(v)) for v in values) + (len(values) - 1) * len(sep) + len(end)
print(repr(text))
print("len(text) =", len(text))
print("formula   =", by_formula)
