# 4.1 Functions: def, return and every kind of argument
# Example "doc" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def bmi(weight_kg: float, height_m: float) -> float:
    """Return the body mass index: weight divided by height squared.

    weight_kg is in kilograms and height_m in metres.
    """
    return round(weight_kg / height_m ** 2, 1)

print(bmi(70, 1.75))
print(bmi.__doc__.splitlines()[0])
print(bmi.__annotations__)           # hints are stored, but never checked when the program runs
