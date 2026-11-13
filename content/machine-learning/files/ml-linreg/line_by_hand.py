# 1.1 Linear regression: fit the best straight line
# Example "line_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

hours = [1, 2, 3, 4, 5, 6]
score = [52, 55, 61, 64, 70, 72]

n = len(hours)
mean_x = sum(hours) / n
mean_y = sum(score) / n

top = 0
bottom = 0
for x, y in zip(hours, score):
    top = top + (x - mean_x) * (y - mean_y)
    bottom = bottom + (x - mean_x) ** 2
slope = top / bottom
intercept = mean_y - slope * mean_x
print("slope:", round(slope, 3), " intercept:", round(intercept, 3))
print("predicted score after 7 hours:", round(intercept + slope * 7, 2))

sse = 0
for x, y in zip(hours, score):
    error = y - (intercept + slope * x)
    sse = sse + error ** 2
print("sum of squared errors:", round(sse, 3))
