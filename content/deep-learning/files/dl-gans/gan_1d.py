# 3.2 Generative adversarial networks
# Example "gan_1d" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A tiny GAN in NumPy. Real data: numbers from N(4, 0.5 squared).
# Generator: x = a * z + b with z from N(0, 1), so it can only shift and stretch the noise.
# Discriminator: logistic regression on the features 1, x/4, (x/4)^2 and, optionally, the spread of the whole batch.
import numpy as np


def sigmoid(t):
    return 1 / (1 + np.exp(-t))


def features(x, use_batch_std):
    batch_std = np.full_like(x, x.std()) if use_batch_std else np.zeros_like(x)
    return np.stack([np.ones_like(x), x / 4, (x / 4) ** 2, batch_std])


def train(generator_loss, use_batch_std=False, steps=3000, d_steps=5, d_lr=1.0, g_lr=0.05, batch=256, seed=0):
    rng = np.random.default_rng(seed)
    a, b = 1.0, 0.0                     # the generator starts as N(0, 1), far from the data
    w = np.zeros(4)                     # discriminator weights
    for step in range(steps + 1):
        # 1. Discriminator: a few steps of logistic regression with real = 1 and fake = 0
        for _ in range(d_steps):
            real = rng.normal(4, 0.5, batch)
            fake = a * rng.normal(0, 1, batch) + b
            fr, ff = features(real, use_batch_std), features(fake, use_batch_std)
            w -= d_lr * (fr @ (sigmoid(w @ fr) - 1) + ff @ sigmoid(w @ ff)) / batch
        # 2. Generator: one step that makes the discriminator score the fakes higher
        z = rng.normal(0, 1, batch)
        fake = a * z + b
        d_fake = sigmoid(w @ features(fake, use_batch_std))
        if generator_loss == 'non-saturating':     # minimise -log D(G(z))
            dloss_dlogit = -(1 - d_fake)
        else:                                      # minimise log(1 - D(G(z))), the original minimax loss
            dloss_dlogit = -d_fake
        dlogit_dx = (w[1] + 2 * w[2] * fake / 4) / 4
        grad_a = np.mean(dloss_dlogit * dlogit_dx * z) + np.mean(dloss_dlogit) * w[3] * np.sign(a) * z.std()
        grad_b = np.mean(dloss_dlogit * dlogit_dx)
        a, b = a - g_lr * grad_a, b - g_lr * grad_b
        if step in (0, 100, 300, 1000, 3000):
            print(f'  step {step:4d}: fake mean {b:5.2f}, fake std {abs(a):4.2f}')


print('Real data: mean 4.00, std 0.50')
for loss, mb in (('saturating', False), ('non-saturating', False), ('non-saturating', True)):
    print(f'Generator loss {loss}' + (', discriminator also sees the batch spread' if mb else ''))
    train(loss, mb)
