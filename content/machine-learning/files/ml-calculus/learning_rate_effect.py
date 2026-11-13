# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Example "learning_rate_effect" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Minimise f(x) = x^2 (slope 2x) from x = 5 with different learning rates
for lr in [0.01, 0.1, 0.5, 0.9, 1.1]:
    x = 5.0
    for step in range(10):
        x = x - lr * 2 * x
    print("learning rate", lr, "-> x after 10 steps =", round(x, 4))
