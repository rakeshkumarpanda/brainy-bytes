# 2.3 Differential privacy
# Example "gaussian_mean" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The Gaussian mechanism and a private average with clipping
import math
import random

random.seed(8)
def gaussian_sigma(sensitivity, eps, delta):
    # classic bound (Dwork and Roth 2014), valid for eps below 1
    return sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / eps

salaries = [random.gauss(60, 15) for _ in range(4999)] + [2500]   # thousands of rupees a month, one huge outlier
L, U = 0, 200                                                      # clip every value into a known range
clipped = [min(U, max(L, s)) for s in salaries]
n = len(clipped)
sens = (U - L) / n                                                  # one person can move the mean by at most this

eps, delta = 0.5, 1e-5
sigma = gaussian_sigma(sens, eps, delta)
noisy_mean = sum(clipped) / n + random.gauss(0, sigma)
print(f"true mean (with outlier) {sum(salaries) / n:.3f}, clipped mean {sum(clipped) / n:.3f}")
print(f"sensitivity {sens:.4f}, sigma {sigma:.4f}, private mean {noisy_mean:.3f}")
print(f"Laplace scale for the same eps would be {sens / eps:.4f} (std {math.sqrt(2) * sens / eps:.4f})")
print("Clipping bounds the sensitivity: without it, one billionaire could move the mean without limit.")
