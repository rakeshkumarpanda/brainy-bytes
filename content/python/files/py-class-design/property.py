# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Example "property" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius                 # goes through the setter below

    @property
    def celsius(self):                         # getter: t.celsius
        return self._celsius

    @celsius.setter
    def celsius(self, value):                  # setter: t.celsius = value
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):                      # read only, computed each time
        return self._celsius * 9 / 5 + 32


t = Temperature(25)
print(t.celsius, t.fahrenheit)
t.celsius = 100
print(t.fahrenheit, vars(t))
for bad in [-300]:
    try:
        t.celsius = bad
    except ValueError as err:
        print("ValueError:", err)
try:
    t.fahrenheit = 0
except AttributeError as err:
    print("AttributeError:", err)
