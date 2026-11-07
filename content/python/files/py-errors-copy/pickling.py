# 1.4 Exceptions in depth, copying and serialisation
# Example "pickling" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import pickle, os, tempfile
from dataclasses import dataclass


@dataclass
class Player:
    name: str
    level: int
    items: list


hero = Player("Asha", 7, ["sword", "map"])
data = pickle.dumps(hero)                      # object -> bytes
print(type(data).__name__, len(data), data[:2])
back = pickle.loads(data)                      # bytes -> a NEW equal object
print(back, back == hero, back is hero)

path = os.path.join(tempfile.mkdtemp(), "save.pkl")
with open(path, "wb") as f:                    # binary mode
    pickle.dump({"hero": hero, "score": 980}, f)
with open(path, "rb") as f:
    game = pickle.load(f)
print(game["score"], game["hero"].items)

try:
    pickle.dumps(lambda x: x)                  # lambdas cannot be pickled
except (pickle.PicklingError, AttributeError) as err:
    print(type(err).__name__)
print(pickle.HIGHEST_PROTOCOL, pickle.DEFAULT_PROTOCOL)
