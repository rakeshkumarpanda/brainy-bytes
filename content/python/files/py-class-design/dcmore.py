# 1.3 Class design: methods, properties, abstract classes and dataclasses
# Example "dcmore" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from dataclasses import dataclass, field, FrozenInstanceError


@dataclass(frozen=True, order=True)            # read only, and comparable with < >
class Version:
    major: int
    minor: int
    patch: int = 0


print(sorted([Version(3, 14), Version(3, 9, 7), Version(3, 10, 2)]))
print(Version(3, 14) > Version(3, 9, 7), hash(Version(1, 0)) == hash(Version(1, 0)))
v = Version(3, 14)
try:
    v.major = 4
except FrozenInstanceError as err:
    print("FrozenInstanceError:", err)


@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)            # not an __init__ argument

    def __post_init__(self):                   # runs after the generated __init__
        if self.width <= 0 or self.height <= 0:
            raise ValueError("sides must be positive")
        self.area = self.width * self.height


print(Rectangle(3, 4))


@dataclass(kw_only=True, slots=True)           # keyword only arguments, and __slots__
class Settings:
    host: str = "localhost"
    port: int = 8000


print(Settings(port=9000), hasattr(Settings(), "__dict__"))
