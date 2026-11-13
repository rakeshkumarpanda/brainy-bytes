# 2.3 Probability and statistics for ML
# Example "dice_counting" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import random
random.seed(7)
rolls = [random.randint(1, 6) for i in range(6000)]
sixes = rolls.count(6)
print("rolls:", len(rolls), " sixes:", sixes)
print("share of sixes:", round(sixes / len(rolls), 4), " theory 1/6 =", round(1 / 6, 4))
both = 0
for i in range(0, 6000, 2):
    if rolls[i] == 6 and rolls[i + 1] == 6:
        both = both + 1
print("two sixes in a row:", round(both / 3000, 4), " theory 1/36 =", round(1 / 36, 4))
even_or_big = 0
for r in rolls:
    if r % 2 == 0 or r >= 5:
        even_or_big = even_or_big + 1
print("even or at least 5:", round(even_or_big / 6000, 4), " theory 4/6 =", round(4 / 6, 4))
