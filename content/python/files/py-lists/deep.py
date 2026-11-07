# 3.2 Lists: storing, changing, sorting and copying
# Example "deep" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import copy

grid = [[1, 2], [3, 4]]
shallow = grid.copy()          # new outer list, same inner lists
deep = copy.deepcopy(grid)     # copies everything
grid[0][0] = 99
print(shallow)                 # changed too
print(deep)                    # safe

bad = [[0] * 3] * 3            # three names for one inner list
bad[0][0] = 1
print(bad)
good = [[0] * 3 for _ in range(3)]
good[0][0] = 1
print(good)
