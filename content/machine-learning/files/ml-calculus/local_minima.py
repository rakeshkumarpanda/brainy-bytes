# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Example "local_minima" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# f(x) = x^4 - 3x^2 + x has two valleys
def slope(x):
    return 4 * x ** 3 - 6 * x + 1

def f(x):
    return x ** 4 - 3 * x ** 2 + x

for start in [-2.0, -0.5, 0.5, 2.0]:
    x = start
    for step in range(200):
        x = x - 0.01 * slope(x)
    print("start", start, "-> ends at x =", round(x, 3), "with f =", round(f(x), 3))
print("Where you start decides which valley you reach.")
