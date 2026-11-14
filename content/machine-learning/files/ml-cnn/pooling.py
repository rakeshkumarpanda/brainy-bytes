# 2.1 Convolutional neural networks
# Example "pooling" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Max pooling, weight sharing and how far each unit can see.
import numpy as np


def max_pool(x, size=2):
    h, w = x.shape[0] // size, x.shape[1] // size
    return x[:h * size, :w * size].reshape(h, size, w, size).max(axis=(1, 3))


fmap = np.array([[1, 3, 2, 1],
                 [4, 6, 5, 0],
                 [7, 2, 9, 8],
                 [1, 0, 3, 4]], dtype=float)
print('2 x 2 max pooling:')
print(max_pool(fmap))

# shifting the input by one pixel inside a pooling window often leaves the pooled output unchanged
x = np.zeros((4, 4))
x[0, 0] = 5
shifted = np.zeros((4, 4))
shifted[1, 1] = 5
print('pooled before shift:', max_pool(x).ravel(), ' after shift:', max_pool(shifted).ravel())

# weights: a dense layer against a convolution on a 32 x 32 x 3 image
dense = (32 * 32 * 3) * (32 * 32 * 16) + 32 * 32 * 16
conv = 3 * 3 * 3 * 16 + 16
print(f'dense layer to 32x32x16: {dense:,} weights')
print(f'3x3 conv with 16 filters: {conv:,} weights ({dense // conv:,} times fewer)')

# receptive field: r grows by (k - 1) * jump, jump multiplies by the stride
layers = [('conv 3x3', 3, 1), ('conv 3x3', 3, 1), ('pool 2x2', 2, 2), ('conv 3x3', 3, 1), ('pool 2x2', 2, 2), ('conv 3x3', 3, 1)]
r, jump = 1, 1
for name, k, s in layers:
    r += (k - 1) * jump
    jump *= s
    print(f'after {name}: each unit sees {r} x {r} input pixels')
