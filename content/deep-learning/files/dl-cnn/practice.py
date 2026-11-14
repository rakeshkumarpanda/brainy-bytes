# 2.1 Convolutional neural networks
# Practice tasks. Fill in each function, then run this file.
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
# Hint: Add the padding on both sides, subtract the filter size, divide by the stride with floor
# division, and add 1.

def conv_output_size(n, k, p, s):
    # your code here
    pass


# ================================================================== task 2: A valid convolution
# Write conv2d_valid(image, kernel) for lists of lists: slide the square kernel over the image with
# stride 1 and no padding, and return the output grid of sums of products (no flipping, as in deep
# learning).
# Hint: For each top left position, multiply the k × k patch by the kernel element by element and
# add up.

def conv2d_valid(image, kernel):
    # your code here
    pass


# ================================================================== task 3: 2 &times; 2 max pooling
# Write max_pool_2x2(fmap) that takes a square list of lists with an even size and returns the 2 × 2
# max pooled grid with stride 2.
# Hint: Step through the grid two at a time in both directions and keep the largest of the four
# values.

def max_pool_2x2(fmap):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: The output size formula", [('conv_output_size(6, 3, 0, 1)', 4), ('conv_output_size(224, 7, 3, 2)', 112), ('conv_output_size(7, 3, 0, 2)', 3)]))
    results.append(check("Task 2: A valid convolution", [('conv2d_valid([[0, 0, 9, 9]] * 4, [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])', [[27, 27], [27, 27]]), ('conv2d_valid([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 0], [0, -1]])', [[-4, -4], [-4, -4]])]))
    results.append(check("Task 3: 2 &times; 2 max pooling", [('max_pool_2x2([[1, 3, 2, 1], [4, 6, 5, 0], [7, 2, 9, 8], [1, 0, 3, 4]])', [[6, 5], [7, 9]]), ('max_pool_2x2([[1, 2], [3, 4]])', [[4]])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
