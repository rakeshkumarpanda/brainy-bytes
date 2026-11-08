# 5.2 FastAPI: fast, typed APIs with automatic docs
# Example "pydantic_models" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


class Address(BaseModel):
    city: str
    zip_code: str = Field(pattern=r"^[0-9]{6}$")          # exactly 6 digits


class Order(BaseModel):
    customer: str = Field(min_length=2, max_length=50)
    quantity: int = Field(gt=0, le=10)                      # 1 to 10
    size: Literal["S", "M", "L"] = "M"                      # only these values, M by default
    delivery: date
    address: Address                                        # a model inside a model
    tags: list[str] = []

    @field_validator("customer")
    @classmethod
    def tidy_name(cls, value):
        return value.strip().title()

    @model_validator(mode="after")
    def not_in_the_past(self):
        if self.delivery < date(2026, 11, 8):
            raise ValueError("delivery must not be in the past")
        return self


# 1. Good data: strings are converted to the declared types
order = Order(customer="  ann lee ", quantity="3", delivery="2026-12-01",
              address={"city": "Pune", "zip_code": "411001"})
print(order)
print("quantity is", type(order.quantity).__name__, "| delivery is", type(order.delivery).__name__)
print(order.model_dump_json())

# 2. Bad data: every problem is listed with where it is and why
try:
    Order(customer="A", quantity=0, size="XL", delivery="2026-13-01", address={"city": "Pune", "zip_code": "41"})
except ValidationError as error:
    print(error.error_count(), "errors:")
    for problem in error.errors():
        print("  ", ".".join(str(part) for part in problem["loc"]), "->", problem["msg"])

# 3. A rule across fields, from the model validator
try:
    Order(customer="Bob", quantity=1, delivery="2020-01-01", address={"city": "Goa", "zip_code": "403001"})
except ValidationError as error:
    print("model rule:", error.errors()[0]["msg"])

# 4. The JSON Schema that FastAPI puts into the API docs
schema = Order.model_json_schema()
print("required:", schema["required"])
print("quantity schema:", schema["properties"]["quantity"])
