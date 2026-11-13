# 2.2 Calculus for ML: derivatives, gradients and gradient descent
# Example "fit_line_gd" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Fit price = w * size + b with gradient descent on the mean squared error
sizes = [1.0, 2.0, 3.0, 4.0]        # in 100 m2
prices = [30.0, 50.0, 70.0, 90.0]   # in lakh (true rule: 20 * size + 10)
n = len(sizes)

w = 0.0
b = 0.0
learning_rate = 0.05
for epoch in range(301):
    d_w = 0.0
    d_b = 0.0
    for x, y in zip(sizes, prices):
        error = (w * x + b) - y
        d_w = d_w + 2 * error * x / n      # partial derivative of MSE with respect to w
        d_b = d_b + 2 * error / n          # partial derivative of MSE with respect to b
    w = w - learning_rate * d_w
    b = b - learning_rate * d_b
    if epoch % 100 == 0:
        mse = sum(((w * x + b) - y) ** 2 for x, y in zip(sizes, prices)) / n
        print("epoch", epoch, "w =", round(w, 3), "b =", round(b, 3), "mse =", round(mse, 4))
print("learned: price =", round(w, 2), "x size +", round(b, 2))
