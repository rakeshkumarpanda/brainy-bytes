# 1.1 Linear regression: fit the best straight line
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


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


# ================================================================== 1232. Check If It Is a Straight Line (Easy)
# https://leetcode.com/problems/check-if-it-is-a-straight-line/
# Pattern: Same slope everywhere (cross multiply)
# Idea: Compare the slope from the first point to every other point with the first slope. Cross
# multiply instead of dividing so a vertical line does not divide by zero.

def check_straight_line(coordinates):
    x0, y0 = coordinates[0]
    x1, y1 = coordinates[1]
    dx = x1 - x0
    dy = y1 - y0
    for x, y in coordinates[2:]:
        if dy * (x - x0) != dx * (y - y0):
            return False
    return True


# ================================================================== 2280. Minimum Lines to Represent a Line Chart (Medium)
# https://leetcode.com/problems/minimum-lines-to-represent-a-line-chart/
# Pattern: Sort, then count slope changes
# Idea: Sort the points by day. A new line starts whenever the slope between neighbours changes.
# Compare slopes by cross multiplying to avoid float errors.

def minimum_lines(stock_prices):
    points = sorted(stock_prices)
    if len(points) < 2:
        return 0
    lines = 1
    for i in range(2, len(points)):
        x0, y0 = points[i - 2]
        x1, y1 = points[i - 1]
        x2, y2 = points[i]
        if (y1 - y0) * (x2 - x1) != (y2 - y1) * (x1 - x0):
            lines = lines + 1
    return lines


# ================================================================== 149. Max Points on a Line (Hard)
# https://leetcode.com/problems/max-points-on-a-line/
# Pattern: Count slopes from each point
# Idea: Fix one point. Every other point gives a slope, stored as a reduced fraction (dy, dx) with
# gcd so equal slopes match exactly. The most common slope plus the fixed point is a line.

from math import gcd


def max_points(points):
    best = 1
    for i in range(len(points)):
        counts = {}
        for j in range(i + 1, len(points)):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            g = gcd(dx, dy)
            dx = dx // g
            dy = dy // g
            if dx < 0 or (dx == 0 and dy < 0):
                dx = -dx
                dy = -dy
            counts[(dy, dx)] = counts.get((dy, dx), 0) + 1
            best = max(best, counts[(dy, dx)] + 1)
    return best


# ================================================================== 462. Minimum Moves to Equal Array Elements II (Medium)
# https://leetcode.com/problems/minimum-moves-to-equal-array-elements-ii/
# Pattern: The median minimises absolute error
# Idea: Moving every number to one value c costs the sum of |x − c|. That sum is smallest at the
# median, the same reason MAE is minimised by the median while MSE is minimised by the mean.

def min_moves2(nums):
    s = sorted(nums)
    median = s[len(s) // 2]
    total = 0
    for x in s:
        total = total + abs(x - median)
    return total


# ================================================================== 2448. Minimum Cost to Make Array Equal (Hard)
# https://leetcode.com/problems/minimum-cost-to-make-array-equal/
# Pattern: Weighted median of a convex cost
# Idea: The total cost is a convex function of the target value. Its minimum is at the weighted
# median: sort by value and walk until the running cost weight reaches half of the total weight.

def min_cost(nums, cost):
    pairs = sorted(zip(nums, cost))
    total_weight = sum(cost)
    running = 0
    target = pairs[0][0]
    for value, weight in pairs:
        running = running + weight
        if running * 2 >= total_weight:
            target = value
            break
    answer = 0
    for value, weight in pairs:
        answer = answer + abs(value - target) * weight
    return answer


# ================================================================== 1515. Best Position for a Service Centre (Hard)
# https://leetcode.com/problems/best-position-for-a-service-centre/
# Pattern: Gradient descent on a convex loss
# Idea: The sum of distances is convex, so gradient descent works. Step against the gradient and
# halve the step size whenever a step does not help, until the step is tiny. (The Weiszfeld update
# is a faster version.)

def total_distance(points, x, y):
    total = 0
    for px, py in points:
        total = total + ((px - x) ** 2 + (py - y) ** 2) ** 0.5
    return total


def get_min_dist_sum(positions):
    x = sum(p[0] for p in positions) / len(positions)
    y = sum(p[1] for p in positions) / len(positions)
    step = 1.0
    best = total_distance(positions, x, y)
    while step > 1e-7:
        gx = 0
        gy = 0
        for px, py in positions:
            d = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
            if d > 1e-12:
                gx = gx + (x - px) / d
                gy = gy + (y - py) / d
        size = (gx * gx + gy * gy) ** 0.5
        if size < 1e-12:
            break
        nx = x - step * gx / size
        ny = y - step * gy / size
        value = total_distance(positions, nx, ny)
        if value < best:
            x, y, best = nx, ny, value
        else:
            step = step / 2
    return round(best, 5)


if __name__ == "__main__":
    results = []
    results.append(check("1232. Check If It Is a Straight Line", [('check_straight_line([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]])', True), ('check_straight_line([[1, 1], [2, 2], [3, 4], [4, 5], [5, 6], [7, 7]])', False)]))
    results.append(check("2280. Minimum Lines to Represent a Line Chart", [('minimum_lines([[1, 7], [2, 6], [3, 5], [4, 4], [5, 4], [6, 3], [7, 2], [8, 1]])', 3), ('minimum_lines([[3, 4], [1, 2], [7, 8], [2, 3]])', 1)]))
    results.append(check("149. Max Points on a Line", [('max_points([[1, 1], [2, 2], [3, 3]])', 3), ('max_points([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]])', 4)]))
    results.append(check("462. Minimum Moves to Equal Array Elements II", [('min_moves2([1, 2, 3])', 2), ('min_moves2([1, 10, 2, 9])', 16)]))
    results.append(check("2448. Minimum Cost to Make Array Equal", [('min_cost([1, 3, 5, 2], [2, 3, 1, 14])', 8), ('min_cost([2, 2, 2, 2, 2], [4, 2, 8, 1, 3])', 0)]))
    results.append(check("1515. Best Position for a Service Centre", [('get_min_dist_sum([[0, 1], [1, 0], [1, 2], [2, 1]])', 4.0), ('get_min_dist_sum([[1, 1], [3, 3]])', 2.82843)]))
    if all(results):
        print("Every solution passes its tests.")
