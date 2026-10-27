from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    price: str


# The products the tests use, with the ids the API expects
GEL_PEN = Product(1, "Gel pen", "₹20")
COFFEE_MUG = Product(2, "Coffee mug", "₹199")
DESK_LAMP = Product(3, "Desk lamp", "₹1,299")
NOTEBOOK = Product(4, "Notebook", "₹60")
WATER_BOTTLE = Product(5, "Water bottle", "₹349")
