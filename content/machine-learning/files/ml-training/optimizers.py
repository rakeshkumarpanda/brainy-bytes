# 1.3 Training deep networks: optimisers, normalisation and regularisation
# Example "optimizers" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Four optimisers on a long, narrow valley: f(x, y) = 0.5 * (x**2 + K * y**2) with K = 100.
# The minimum is at (0, 0). The valley is 100 times more curved across y than along x.
import numpy as np

K = 100


def grad(p):
    return np.array([p[0], K * p[1]])


def loss(p):
    return 0.5 * (p[0] ** 2 + K * p[1] ** 2)


def run(name, lr, steps=60):
    p = np.array([-4.0, 1.5])
    v = np.zeros(2)          # momentum, or the first moment in Adam
    s = np.zeros(2)          # running average of squared gradients
    for t in range(1, steps + 1):
        g = grad(p)
        if name == 'SGD':
            p = p - lr * g
        elif name == 'Momentum':
            v = 0.9 * v + g
            p = p - lr * v
        elif name == 'RMSprop':
            s = 0.9 * s + 0.1 * g * g
            p = p - lr * g / (np.sqrt(s) + 1e-8)
        elif name == 'Adam':
            v = 0.9 * v + 0.1 * g
            s = 0.999 * s + 0.001 * g * g
            v_hat = v / (1 - 0.9 ** t)
            s_hat = s / (1 - 0.999 ** t)
            p = p - lr * v_hat / (np.sqrt(s_hat) + 1e-8)
    return loss(p)


settings = [('SGD', 0.019), ('Momentum', 0.01), ('RMSprop', 0.1), ('Adam', 0.1)]
print('loss after 60 steps, starting from', loss(np.array([-4.0, 1.5])))
for name, lr in settings:
    print(f'  {name:8s} lr {lr:<5} {run(name, lr):.6f}')

print('plain SGD: it is stable only while lr < 2 / K = 0.02')
for lr in [0.01, 0.019, 0.021, 0.03]:
    print(f'  lr {lr:<6} loss {run("SGD", lr):.4g}')
