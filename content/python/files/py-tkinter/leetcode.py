# 6.4 Desktop windows with tkinter
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== 657. Robot Return to Origin (Easy)
# https://leetcode.com/problems/robot-return-to-origin/
# Pattern: Count the moves in each direction
# Idea: Like moving an item on a canvas: R adds to x, L takes away. Back at the start means x and y
# are both 0.

def judge_circle(moves):
    x = 0
    y = 0
    for move in moves:
        if move == "R":
            x += 1
        elif move == "L":
            x -= 1
        elif move == "U":
            y -= 1
        else:
            y += 1
    return x == 0 and y == 0


# ================================================================== 733. Flood Fill (Easy)
# https://leetcode.com/problems/flood-fill/
# Pattern: The paint bucket tool: breadth first search
# Idea: Start at the clicked pixel and paint every neighbour (up, down, left, right) that has the
# old colour. Stop at once if the new colour equals the old one.

from collections import deque


def flood_fill(image, sr, sc, color):
    old = image[sr][sc]
    if old == color:
        return image
    rows = len(image)
    cols = len(image[0])
    todo = deque([(sr, sc)])
    image[sr][sc] = color
    while todo:
        r, c = todo.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and image[nr][nc] == old:
                image[nr][nc] = color
                todo.append((nr, nc))
    return image


# ================================================================== 836. Rectangle Overlap (Easy)
# https://leetcode.com/problems/rectangle-overlap/
# Pattern: Overlap on both axes
# Idea: Two boxes overlap when the left edge of each is before the right edge of the other, on x AND
# on y. Touching edges do not count. Games use this for collisions.

def is_rectangle_overlap(rec1, rec2):
    overlap_x = min(rec1[2], rec2[2]) > max(rec1[0], rec2[0])
    overlap_y = min(rec1[3], rec2[3]) > max(rec1[1], rec2[1])
    return overlap_x and overlap_y


# ================================================================== 1232. Check If It Is a Straight Line (Easy)
# https://leetcode.com/problems/check-if-it-is-a-straight-line/
# Pattern: Compare slopes with a cross product
# Idea: Points are on one line when (y - y0) × (x1 - x0) equals (y1 - y0) × (x - x0) for every
# point. Multiplying avoids dividing by zero for vertical lines.

def check_straight_line(coordinates):
    x0, y0 = coordinates[0]
    x1, y1 = coordinates[1]
    for x, y in coordinates[2:]:
        if (y - y0) * (x1 - x0) != (y1 - y0) * (x - x0):
            return False
    return True


# ================================================================== 223. Rectangle Area (Medium)
# https://leetcode.com/problems/rectangle-area/
# Pattern: Both areas minus the overlap
# Idea: Add the two areas and take away the overlap. The overlap width is max(0, min of right edges
# minus max of left edges), the same for the height.

def compute_area(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    width = max(0, min(ax2, bx2) - max(ax1, bx1))
    height = max(0, min(ay2, by2) - max(ay1, by1))
    return area_a + area_b - width * height


# ================================================================== 593. Valid Square (Medium)
# https://leetcode.com/problems/valid-square/
# Pattern: Six distances between four points
# Idea: A square has 4 equal sides and 2 equal, longer diagonals. Use squared distances to stay with
# whole numbers, and reject a length of 0.

def valid_square(p1, p2, p3, p4):
    points = [p1, p2, p3, p4]
    distances = []
    for i in range(4):
        for j in range(i + 1, 4):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            distances.append(dx * dx + dy * dy)
    distances.sort()
    return distances[0] > 0 and distances[0] == distances[3] and distances[4] == distances[5] and distances[4] == 2 * distances[0]


# ================================================================== 874. Walking Robot Simulation (Medium)
# https://leetcode.com/problems/walking-robot-simulation/
# Pattern: Directions as a list, obstacles as a set
# Idea: Keep the four directions in a list and turn by moving the index. Store obstacles as a set of
# tuples so each step is checked in O(1).

def robot_sim(commands, obstacles):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    blocked = {(x, y) for x, y in obstacles}
    x = 0
    y = 0
    facing = 0
    best = 0
    for command in commands:
        if command == -2:
            facing = (facing + 3) % 4
        elif command == -1:
            facing = (facing + 1) % 4
        else:
            dx, dy = directions[facing]
            for step in range(command):
                if (x + dx, y + dy) in blocked:
                    break
                x += dx
                y += dy
                best = max(best, x * x + y * y)
    return best


# ================================================================== 1041. Robot Bounded In Circle (Medium)
# https://leetcode.com/problems/robot-bounded-in-circle/
# Pattern: Run the instructions once and look at the result
# Idea: After one run the robot is either back at the start or facing a new direction. In both cases
# it stays in a circle. Only "away and still facing north" escapes.

def is_robot_bounded(instructions):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    x = 0
    y = 0
    facing = 0
    for letter in instructions:
        if letter == "G":
            x += directions[facing][0]
            y += directions[facing][1]
        elif letter == "R":
            facing = (facing + 1) % 4
        else:
            facing = (facing + 3) % 4
    return (x == 0 and y == 0) or facing != 0


# ================================================================== 391. Perfect Rectangle (Hard)
# https://leetcode.com/problems/perfect-rectangle/
# Pattern: Areas add up and only four corners stay
# Idea: The small areas must add up to the big box. Toggle every corner in a set: inner corners
# appear an even number of times and cancel out, so exactly the four outer corners must be left.

def is_rectangle_cover(rectangles):
    area = 0
    corners = set()
    for x1, y1, x2, y2 in rectangles:
        area += (x2 - x1) * (y2 - y1)
        for corner in ((x1, y1), (x1, y2), (x2, y1), (x2, y2)):
            if corner in corners:
                corners.remove(corner)
            else:
                corners.add(corner)
    left = min(r[0] for r in rectangles)
    bottom = min(r[1] for r in rectangles)
    right = max(r[2] for r in rectangles)
    top = max(r[3] for r in rectangles)
    outer = {(left, bottom), (left, top), (right, bottom), (right, top)}
    return corners == outer and area == (right - left) * (top - bottom)


# ================================================================== 850. Rectangle Area II (Hard)
# https://leetcode.com/problems/rectangle-area-ii/
# Pattern: Coordinate compression on a grid
# Idea: Collect every x and y edge, sort them and mark which small cells between them are covered.
# Add up the covered cells and take the result modulo 109 + 7.

def rectangle_area(rectangles):
    xs = sorted({x for r in rectangles for x in (r[0], r[2])})
    ys = sorted({y for r in rectangles for y in (r[1], r[3])})
    x_index = {x: i for i, x in enumerate(xs)}
    y_index = {y: i for i, y in enumerate(ys)}
    covered = [[False] * len(ys) for _ in xs]
    for x1, y1, x2, y2 in rectangles:
        for i in range(x_index[x1], x_index[x2]):
            for j in range(y_index[y1], y_index[y2]):
                covered[i][j] = True
    total = 0
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            if covered[i][j]:
                total += (xs[i + 1] - xs[i]) * (ys[j + 1] - ys[j])
    return total % (10 ** 9 + 7)


if __name__ == "__main__":
    results = []
    results.append(check("657. Robot Return to Origin", [('judge_circle("UD")', True), ('judge_circle("LL")', False), ('judge_circle("RRDDLLUU")', True)]))
    results.append(check("733. Flood Fill", [('flood_fill([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2)', [[2, 2, 2], [2, 2, 0], [2, 0, 1]]), ('flood_fill([[0, 0, 0], [0, 0, 0]], 0, 0, 0)', [[0, 0, 0], [0, 0, 0]])]))
    results.append(check("836. Rectangle Overlap", [('is_rectangle_overlap([0, 0, 2, 2], [1, 1, 3, 3])', True), ('is_rectangle_overlap([0, 0, 1, 1], [1, 0, 2, 1])', False), ('is_rectangle_overlap([0, 0, 1, 1], [2, 2, 3, 3])', False)]))
    results.append(check("1232. Check If It Is a Straight Line", [('check_straight_line([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]])', True), ('check_straight_line([[1, 1], [2, 2], [3, 4], [4, 5], [5, 6], [7, 7]])', False), ('check_straight_line([[0, 0], [0, 1], [0, -1]])', True)]))
    results.append(check("223. Rectangle Area", [('compute_area(-3, 0, 3, 4, 0, -1, 9, 2)', 45), ('compute_area(-2, -2, 2, 2, -2, -2, 2, 2)', 16)]))
    results.append(check("593. Valid Square", [('valid_square([0, 0], [1, 1], [1, 0], [0, 1])', True), ('valid_square([0, 0], [1, 1], [1, 0], [0, 12])', False), ('valid_square([1, 0], [-1, 0], [0, 1], [0, -1])', True)]))
    results.append(check("874. Walking Robot Simulation", [('robot_sim([4, -1, 3], [])', 25), ('robot_sim([4, -1, 4, -2, 4], [[2, 4]])', 65), ('robot_sim([6, -1, -1, 6], [[0, 0]])', 36)]))
    results.append(check("1041. Robot Bounded In Circle", [('is_robot_bounded("GGLLGG")', True), ('is_robot_bounded("GG")', False), ('is_robot_bounded("GL")', True)]))
    results.append(check("391. Perfect Rectangle", [('is_rectangle_cover([[1, 1, 3, 3], [3, 1, 4, 2], [3, 2, 4, 4], [1, 3, 2, 4], [2, 3, 3, 4]])', True), ('is_rectangle_cover([[1, 1, 2, 3], [1, 3, 2, 4], [3, 1, 4, 2], [3, 2, 4, 4]])', False), ('is_rectangle_cover([[1, 1, 3, 3], [3, 1, 4, 2], [1, 3, 2, 4], [2, 2, 4, 4]])', False)]))
    results.append(check("850. Rectangle Area II", [('rectangle_area([[0, 0, 2, 2], [1, 0, 2, 3], [1, 0, 3, 1]])', 6), ('rectangle_area([[0, 0, 1000000000, 1000000000]])', 49)]))
    if all(results):
        print("Every solution passes its tests.")
