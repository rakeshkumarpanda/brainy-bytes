# 1.4 Input, output and formatting text
# Example "robust" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

# Ask again until the user types a whole number
answers = iter(["ten", "-3", "12"])   # what the user types, one try at a time

def ask(prompt):
    text = next(answers)              # in a real program: text = input(prompt)
    print(prompt + text)
    return text

while True:
    text = ask("Quantity: ")
    try:
        qty = int(text)
    except ValueError:
        print("  Please type digits only.")
        continue
    if qty <= 0:
        print("  It must be more than zero.")
        continue
    break
print("You ordered", qty)
