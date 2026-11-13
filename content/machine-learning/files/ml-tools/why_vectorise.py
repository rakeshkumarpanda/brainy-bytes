# 1.3 Python tools for ML: NumPy, pandas and scikit-learn
# Example "why_vectorise" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import time
import numpy as np

n = 200_000
prices = list(range(n))

start = time.perf_counter()
doubled = []
for p in prices:                  # plain Python: one item at a time
    doubled.append(p * 2)
loop_time = time.perf_counter() - start

arr = np.arange(n)
start = time.perf_counter()
doubled_np = arr * 2              # NumPy: the loop runs in fast compiled code
numpy_time = time.perf_counter() - start

print("same answer:", doubled[-1] == doubled_np[-1])
print("NumPy was faster:", numpy_time < loop_time)
print("a Python int uses about", 28, "bytes, a NumPy int64 uses", arr.itemsize, "bytes")
