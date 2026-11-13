# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Example "derivative_rules" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

def numeric_derivative(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)     # central difference: more accurate

x = 2.0
print("power rule   d/dx x^3 = 3x^2 :", round(numeric_derivative(lambda t: t ** 3, x), 4), "vs", 3 * x ** 2)
print("constant     d/dx 5x = 5     :", round(numeric_derivative(lambda t: 5 * t, x), 4))
print("sum rule     d/dx x^2 + 4x   :", round(numeric_derivative(lambda t: t ** 2 + 4 * t, x), 4), "vs", 2 * x + 4)
print("product rule d/dx x^2 * x    :", round(numeric_derivative(lambda t: (t ** 2) * t, x), 4), "vs", 2 * x * x + x ** 2)
