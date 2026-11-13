# 1.2 Multi armed bandits
# Example "thompson" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np

click_rates = np.array([0.04, 0.05, 0.07])                # three web page designs, true click rates unknown
visitors, repeats = 5000, 200                            # 200 separate experiments, run side by side
rng = np.random.default_rng(2)
rows = np.arange(repeats)

def ab_test(test_share=0.5):
    shown, clicks = np.zeros((repeats, 3)), np.zeros((repeats, 3))
    for v in range(visitors):
        if v < visitors * test_share:
            a = np.full(repeats, v % 3)                  # split traffic evenly during the test
        else:
            a = (clicks / np.maximum(shown, 1)).argmax(axis=1)   # then show the winner to everyone
        shown[rows, a] += 1
        clicks[rows, a] += rng.random(repeats) < click_rates[a]
    return clicks.sum(axis=1), shown

def thompson():
    wins, losses = np.ones((repeats, 3)), np.ones((repeats, 3))   # Beta(1, 1) prior for each design
    for v in range(visitors):
        a = rng.beta(wins, losses).argmax(axis=1)        # sample a plausible rate for each design, show the best
        click = rng.random(repeats) < click_rates[a]
        wins[rows, a] += click
        losses[rows, a] += 1 - click
    return wins.sum(axis=1) - 3, wins + losses - 2

for name, f in [("A/B test, then winner", ab_test), ("Thompson sampling", thompson)]:
    clicks, shown = f()
    print(name.ljust(22), " average clicks", round(clicks.mean(), 1), " visitors per design", shown.mean(axis=0).round(0))
print("best possible on average:", round(visitors * click_rates.max()))
