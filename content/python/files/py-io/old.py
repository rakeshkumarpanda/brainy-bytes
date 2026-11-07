# 1.4 Input, output and formatting text
# Example "old" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

name, score = "Ravi", 92.456
print("Name: %s, score: %.1f" % (name, score))            # printf style (oldest)
print("Name: {}, score: {:.1f}".format(name, score))      # str.format (Python 2.6+)
print("Name: {0}, again {0}, score {1:.2f}".format(name, score))
print(f"Name: {name}, score: {score:.1f}")                # f-string (Python 3.6+), the best choice
