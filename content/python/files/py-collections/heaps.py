# 4.2 collections, heapq and bisect
# Example "heaps" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import heapq

heap = []
for x in [5, 3, 8, 1, 9, 2]:
    heapq.heappush(heap, x)
print(heap)                                    # heap order, not sorted order
print(heapq.heappop(heap), heap)

numbers = [7, 2, 9, 4, 1]
heapq.heapify(numbers)                         # turn a list into a heap in O(n)
print(numbers[0])

scores = {"ana": 88, "bo": 95, "cy": 70, "di": 91}
print(heapq.nlargest(2, scores, key=scores.get))
print(heapq.nsmallest(2, [5, 1, 4, 2]))

tasks = []
heapq.heappush(tasks, (2, "write report"))
heapq.heappush(tasks, (1, "fix the server"))
heapq.heappush(tasks, (3, "lunch"))
while tasks:
    priority, task = heapq.heappop(tasks)      # tuples compare by their first item first
    print(priority, task)

print(list(heapq.merge([1, 4, 9], [2, 3, 10])))   # merge sorted lists lazily

biggest = [3, 8, 5]
heapq.heapify_max(biggest)                     # a max-heap (Python 3.14+)
print(heapq.heappop_max(biggest))
old_way = [-x for x in [3, 8, 5]]              # before 3.14: store negative numbers
heapq.heapify(old_way)
print(-heapq.heappop(old_way))
