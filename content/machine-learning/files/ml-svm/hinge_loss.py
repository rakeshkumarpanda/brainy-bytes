# 2.4 Support vector machines: the widest street
# Example "hinge_loss" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

w = [1.0, 1.0]
b = -5.0
points = [([1, 1], -1), ([2, 2], -1), ([2, 3], -1), ([3, 3], 1), ([4, 4], 1), ([2, 2], 1)]
total = 0.0
for x, label in points:
    score = w[0] * x[0] + w[1] * x[1] + b
    loss = max(0.0, 1 - label * score)
    total = total + loss
    print("x", x, " label", str(label).rjust(2), " score", str(score).rjust(4), " hinge loss", loss)
print("total hinge loss:", total)
