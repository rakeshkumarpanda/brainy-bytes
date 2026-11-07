# 1.3 Operators, expressions and the order Python works them out
# Example "logic" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

age, has_ticket = 20, False
print(age >= 18 and has_ticket)      # both must be True
print(age >= 18 or has_ticket)       # one is enough
print(not has_ticket)

# and / or return one of their operands, not always True or False
print(0 or "default")                # first truthy value
print("Asha" and "Ravi")             # last value if all are truthy
print([] and 1 / 0)                  # short circuit: 1 / 0 never runs
name = ""
print(name or "Guest")               # a common pattern for a default
