# 2.1 Making decisions: if, elif, else and match
# Example "combine" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

age, member, day = 67, False, "Tue"
if age >= 60 or member:
    print("Discount")
if 13 <= age <= 19:
    print("Teenager")
if day in ("Sat", "Sun"):
    print("Weekend")
elif day == "Tue" and not member:
    print("Tuesday offer for new customers")
