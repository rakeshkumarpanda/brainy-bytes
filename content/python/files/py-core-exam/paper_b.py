# 7.1 Exam practice: PCEP and PCAP style papers
# Example "paper_b" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

a = [1, 2, 3]
b = a
b += [4]
print("Q1", a)

t = (1, 2, 3)
u = t
u += (4,)
print("Q2", t, u)

grid = [[0] * 3] * 3
grid[0][0] = 1
print("Q3", grid)

nums = [1, 2, 3, 4]
print("Q4", nums[::-2], nums[-1:0:-1], nums[10:])

d = {"a": 1, "b": 2}
d["a"] = 3
print("Q5", list(d), d.get("z", 0), len(d))

s = "python"
print("Q6", s[1:4], s[-3:], s.find("z"), s.upper()[0])

one = (1,)
two = (1)
print("Q7", type(one).__name__, type(two).__name__)
print("Q8", {1, 2, 2, 3} | {3, 4}, {1, 2} & {2, 3})

x = [3, 1, 2]
y = x.sort()
print("Q9", x, y)

keys = {True: "a", 1: "b", 1.0: "c"}
print("Q10", len(keys), keys)
