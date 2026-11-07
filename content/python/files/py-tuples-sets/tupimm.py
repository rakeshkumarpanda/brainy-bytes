# 3.3 Tuples and sets: fixed records and unique items
# Example "tupimm" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

days = ("Mon", "Tue", "Wed")
try:
    days[0] = "Sun"
except TypeError as err:
    print("TypeError:", err)

# A tuple cannot change, but a list inside it can
record = ("Asha", [80, 90])
record[1].append(75)
print(record)

days = days + ("Thu",)     # this builds a new tuple and moves the name
print(days)
