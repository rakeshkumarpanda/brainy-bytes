import os
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    email: str
    password: str
    name: str


# Test accounts. Real projects read passwords from CI secrets, never from the repository.
ASHA = User("asha@shop.example", os.getenv("ASHA_PASSWORD") or "s3cret", "Asha")
RAVI = User("ravi@shop.example", os.getenv("RAVI_PASSWORD") or "admin123", "Ravi")
