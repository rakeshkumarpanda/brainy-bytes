# 3.3 Diffusion models
# Example "schedules" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Noise schedules: how fast the signal fades. Linear (Ho and colleagues, 2020) against cosine (Nichol and Dhariwal, 2021).
import numpy as np

T = 1000
t = np.arange(1, T + 1)
linear = np.cumprod(1 - np.linspace(1e-4, 0.02, T))
s = 0.008
f = np.cos((t / T + s) / (1 + s) * np.pi / 2) ** 2
cosine = f / np.cos(s / (1 + s) * np.pi / 2) ** 2              # alpha_bar_t of the cosine schedule

print('   t    linear alpha_bar   cosine alpha_bar')
for k in (100, 250, 500, 750, 900, 1000):
    print(f'{k:4d}   {linear[k - 1]:16.4f}   {cosine[k - 1]:16.4f}')

for name, ab in [('linear', linear), ('cosine', cosine)]:
    snr = ab / (1 - ab)                                        # signal to noise ratio
    half = t[np.argmax(snr < 1)]                               # first step where noise outweighs signal
    useless = np.mean(ab < 0.001)                              # steps where almost nothing of x0 is left
    print(f'{name}: signal and noise are equal at step {half}, and {useless:.0%} of the steps have alpha_bar below 0.001')
