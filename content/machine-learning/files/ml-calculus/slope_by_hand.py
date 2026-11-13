# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Example "slope_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

def f(x):
    return x * x

x = 3
for h in [1, 0.1, 0.01, 0.001]:
    slope = (f(x + h) - f(x)) / h      # rise over run between two close points
    print("h =", h, "slope =", round(slope, 4))
print("the slopes settle on 6, and the rule f'(x) = 2x gives 2 x 3 = 6")
