# 1.1 Special methods and operator overloading
# Example "hashing" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self):                        # equal objects MUST have equal hashes
        return hash((self.x, self.y))


points = {Point(1, 2), Point(1, 2), Point(3, 4)}
print(len(points), Point(1, 2) in points)
seen = {Point(0, 0): "origin"}
print(seen[Point(0, 0)])

p = Point(5, 5)
box = {p}
p.x = 6                                        # changing a key after it is in a set
print(p in box, Point(6, 5) in box)            # it can no longer be found
