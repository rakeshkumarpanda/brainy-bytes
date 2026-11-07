# 6.2 CSV, JSON, XML and settings files
# Example "pickle_data" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import pickle


class Player:
    def __init__(self, name, scores):
        self.name = name
        self.scores = scores


p = Player("Ann", {3, 1})
data = pickle.dumps(p)                         # bytes in Python's own format
print(type(data).__name__, data[:2])
copy = pickle.loads(data)
print(copy.name, sorted(copy.scores), copy is p)


class Evil:
    def __reduce__(self):
        return (print, ("this ran while loading!",))


pickle.loads(pickle.dumps(Evil()))             # loading runs code chosen by whoever made the data
