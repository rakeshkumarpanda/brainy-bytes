# 2.1 Convolutional neural networks
# Model solutions. Try practice.py first.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: The output size formula
# Write conv_output_size(n, k, p, s) that returns the output size of a convolution on an n × n input
# with a k × k filter, padding p and stride s.
# Why it works: If (n + 2p − k) is not divisible by s, the last pixels are simply skipped, which is
# why the formula uses floor division.

def conv_output_size(n, k, p, s):
    return (n + 2 * p - k) // s + 1


# ================================================================== task 2: A valid convolution
# Write conv2d_valid(image, kernel) for lists of lists: slide the square kernel over the image with
# stride 1 and no padding, and return the output grid of sums of products (no flipping, as in deep
# learning).
# Why it works: Libraries do the same work much faster by turning patches into rows of a matrix
# (im2col) or with fast Fourier transforms for large filters.

def conv2d_valid(image, kernel):
    n, k = len(image), len(kernel)
    out = []
    for i in range(n - k + 1):
        row = []
        for j in range(len(image[0]) - k + 1):
            row.append(sum(image[i + a][j + b] * kernel[a][b] for a in range(k) for b in range(k)))
        out.append(row)
    return out


# ================================================================== task 3: 2 &times; 2 max pooling
# Write max_pool_2x2(fmap) that takes a square list of lists with an even size and returns the 2 × 2
# max pooled grid with stride 2.
# Why it works: Average pooling would take the mean of the four values instead. Global average
# pooling takes the mean over the whole map.

def max_pool_2x2(fmap):
    n = len(fmap)
    return [[max(fmap[i][j], fmap[i][j + 1], fmap[i + 1][j], fmap[i + 1][j + 1])
             for j in range(0, n, 2)] for i in range(0, n, 2)]


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The output size formula", [('conv_output_size(6, 3, 0, 1)', 4), ('conv_output_size(224, 7, 3, 2)', 112), ('conv_output_size(7, 3, 0, 2)', 3)]))
    results.append(check("Task 2: A valid convolution", [('conv2d_valid([[0, 0, 9, 9]] * 4, [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])', [[27, 27], [27, 27]]), ('conv2d_valid([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 0], [0, -1]])', [[-4, -4], [-4, -4]])]))
    results.append(check("Task 3: 2 &times; 2 max pooling", [('max_pool_2x2([[1, 3, 2, 1], [4, 6, 5, 0], [7, 2, 9, 8], [1, 0, 3, 4]])', [[6, 5], [7, 9]]), ('max_pool_2x2([[1, 2], [3, 4]])', [[4]])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
