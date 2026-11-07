# 4.2 collections, heapq and bisect
# Example "queues" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from collections import deque

line = deque(["Ann", "Ben"])
line.append("Cat")                             # join at the back
line.appendleft("VIP")                         # go straight to the front
print(line)
print(line.popleft(), line.pop(), line)        # O(1) at both ends
line.rotate(1)                                 # move the last item to the front
print(line)

recent = deque(maxlen=3)                       # keeps only the last 3 items
for page in ["home", "shop", "cart", "pay", "done"]:
    recent.append(page)
print(list(recent))


def shortest_path(graph, start, goal):
    """Breadth first search: visit places in order of distance, with a deque as the queue."""
    queue = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        place = path[-1]
        if place == goal:
            return path
        for next_place in graph[place]:
            if next_place not in seen:
                seen.add(next_place)
                queue.append(path + [next_place])
    return None


roads = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": ["F"], "F": []}
print(shortest_path(roads, "A", "F"))
