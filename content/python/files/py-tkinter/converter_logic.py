# 6.4 Desktop windows with tkinter
# Example "converter_logic" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def celsius_to_fahrenheit(text):
    """The logic of a converter window, kept apart from tkinter so it is easy to test."""
    text = text.strip().replace(",", ".")
    try:
        celsius = float(text)
    except ValueError:
        return "Please type a number"
    if celsius < -273.15:
        return "Colder than absolute zero is not possible"
    fahrenheit = celsius * 9 / 5 + 32
    return f"{fahrenheit:.1f} degrees Fahrenheit"


for typed in ["100", "-40", " 36,6 ", "hot", "", "-300"]:
    print(repr(typed), "gives", celsius_to_fahrenheit(typed))

assert celsius_to_fahrenheit("0") == "32.0 degrees Fahrenheit"
assert celsius_to_fahrenheit("abc") == "Please type a number"
print("tests pass")

# In the window, the button only connects the two worlds:
#   def convert():
#       result.config(text=celsius_to_fahrenheit(entry.get()))
