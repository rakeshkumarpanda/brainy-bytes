# 2.1 Convolutional neural networks
# Example "conv2d" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A 2D convolution written by hand, used to find edges in a tiny image.
import numpy as np


def conv2d(image, kernel, stride=1, padding=0):
    if padding:
        image = np.pad(image, padding)
    k = kernel.shape[0]
    out_size = (image.shape[0] - k) // stride + 1
    out = np.zeros((out_size, out_size))
    for i in range(out_size):
        for j in range(out_size):
            patch = image[i * stride:i * stride + k, j * stride:j * stride + k]
            out[i, j] = np.sum(patch * kernel)      # multiply and add
    return out


# a 6 x 6 image: dark on the left, bright on the right
image = np.array([[0, 0, 0, 9, 9, 9]] * 6, dtype=float)
vertical_edge = np.array([[-1, 0, 1],
                          [-1, 0, 1],
                          [-1, 0, 1]], dtype=float)
horizontal_edge = vertical_edge.T

print('vertical edge filter output:')
print(conv2d(image, vertical_edge))
print('horizontal edge filter output (no horizontal edges):')
print(conv2d(image, horizontal_edge))

# output size = (n + 2p - k) // s + 1
for n, k, p, s in [(6, 3, 0, 1), (6, 3, 1, 1), (7, 3, 0, 2), (32, 5, 2, 1), (224, 7, 3, 2)]:
    size = (n + 2 * p - k) // s + 1
    print(f'n={n}, k={k}, padding={p}, stride={s}: output {size} x {size}')

out = conv2d(image, vertical_edge, stride=2, padding=1)
print('stride 2 with padding 1 gives shape', out.shape)
