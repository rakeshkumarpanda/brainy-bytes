# 1.1 Neural networks: from perceptrons to MLPs
# Example "activations" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

# Common activation functions and their slopes. The slope matters because backpropagation multiplies by it.
z = np.array([-5.0, -1.0, 0.0, 1.0, 5.0])
sig = 1 / (1 + np.exp(-z))
funcs = {
    "sigmoid": (sig, sig * (1 - sig)),
    "tanh": (np.tanh(z), 1 - np.tanh(z) ** 2),
    "ReLU": (np.maximum(0, z), (z > 0).astype(float)),
    "leaky ReLU": (np.where(z > 0, z, 0.01 * z), np.where(z > 0, 1.0, 0.01)),
}
gelu = 0.5 * z * (1 + np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * z ** 3)))   # the tanh approximation used in GPT-2
funcs["GELU"] = (gelu, None)
print("z:".ljust(12), z)
for name, (f, df) in funcs.items():
    print(f"{name:11s} value {np.round(f, 3) + 0.0}")
    if df is not None:
        print(f"{'':11s} slope {np.round(df, 3)}")
print("sigmoid's largest slope is", round(float(sig[2] * (1 - sig[2])), 3), "so ten sigmoid layers can shrink a gradient by", 0.25 ** 10)
