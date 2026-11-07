# 1.1 Special methods and operator overloading
# Example "call" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self, step=1):                # lets the object be called like a function
        self.count += step
        return self.count


clicks = Counter()
clicks()
clicks()
print(clicks(5), clicks.count)
print(callable(clicks), callable(5), callable(len))
