# 3.2 Lists: storing, changing, sorting and copying
# Example "search" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

colours = ["red", "green", "blue", "green"]
print(colours.index("green"))      # first position
print(colours.count("green"))      # how many times
print("pink" in colours)
try:
    colours.index("pink")
except ValueError as err:
    print("ValueError:", err)
