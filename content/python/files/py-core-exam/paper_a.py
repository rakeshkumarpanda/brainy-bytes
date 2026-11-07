# 7.1 Exam practice: PCEP and PCAP style papers
# Example "paper_a" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

print("Q1", -2 ** 2, 2 ** 3 ** 2)
print("Q2", 7 // -2, -7 % 3, 7 % -3)
print("Q3", 0.1 + 0.2 == 0.3, round(2.5), round(3.5))
print("Q4", 1 < 2 < 3, 3 > 2 > 1 == 1)

x = 0
while x < 10:
    x += 3
else:
    print("Q5 done", x)

for i in range(3):
    if i == 1:
        break
else:
    print("no break")
print("Q6 i is", i)

print("Q7", int("1F", 16), 0o17, 0b101, 1_000)
print("Q8", bool("False"), bool(""), bool([0]), bool(0.0))
print("Q9", "ab" * 3, "5" + "5", 5 + 5)
print("Q10", end=" ")
print("a", "b", sep="-", end="!\n")
