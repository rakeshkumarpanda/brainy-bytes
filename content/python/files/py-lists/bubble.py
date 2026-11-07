# 3.2 Lists: storing, changing, sorting and copying
# Example "bubble" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def bubble_sort(items):
    items = items[:]                 # work on a copy
    n = len(items)
    for done in range(n - 1):
        swapped = False
        for i in range(n - 1 - done):
            if items[i] > items[i + 1]:
                items[i], items[i + 1] = items[i + 1], items[i]
                swapped = True
        print("after pass", done + 1, items)
        if not swapped:              # already sorted, stop early
            break
    return items

print(bubble_sort([5, 1, 4, 2, 8]))
