# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Example "gradient_of_two" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# f(w1, w2) = (w1 - 3)^2 + 2 * (w2 + 1)^2   has its lowest point at (3, -1)
def f(w1, w2):
    return (w1 - 3) ** 2 + 2 * (w2 + 1) ** 2

def gradient(w1, w2):
    d_w1 = 2 * (w1 - 3)          # partial derivative: treat w2 as a fixed number
    d_w2 = 4 * (w2 + 1)          # partial derivative: treat w1 as a fixed number
    return [d_w1, d_w2]

w1, w2 = 0.0, 0.0
print("gradient at (0, 0):", gradient(w1, w2))
for step in range(5):
    g = gradient(w1, w2)
    w1 = w1 - 0.2 * g[0]
    w2 = w2 - 0.2 * g[1]
    print("step", step + 1, "w =", [round(w1, 3), round(w2, 3)], "f =", round(f(w1, w2), 4))
