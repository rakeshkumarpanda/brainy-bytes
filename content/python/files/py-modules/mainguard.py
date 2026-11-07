# 5.2 Modules and packages: import, the standard library and pip
# Example "mainguard" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def main():
    for c in [0, 37, 100]:
        print(c, "C is", celsius_to_fahrenheit(c), "F")

print("__name__ is", repr(__name__))
if __name__ == "__main__":     # True when this file is run, False when it is imported
    main()
