# 1.2 Attacks on machine learning and their defences
# Example "extract_linear" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Model extraction (Tramer et al. 2016): a prediction API that returns probabilities can leak a linear model exactly
import math

SECRET_W, SECRET_B = [1.7, -0.6, 2.3], -1.1          # the company's private model

def api(x):
    """What the public API returns: a probability."""
    z = sum(w * v for w, v in zip(SECRET_W, x)) + SECRET_B
    return 1 / (1 + math.exp(-z))

def logit(p):
    return math.log(p / (1 - p))                      # undo the sigmoid to get z back

# d + 1 = 4 queries: the zero vector gives b, each unit vector gives b + w_i
queries = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
z = [logit(api(q)) for q in queries]
b = z[0]
w = [zi - b for zi in z[1:]]
print("queries used:", len(queries))
print("recovered w:", [round(v, 6) for v in w], " b:", round(b, 6))

# defences, from the defender's side
def api_label_only(x):
    return 1 if api(x) >= 0.5 else 0                  # labels leak far less than probabilities

def api_rounded(x):
    return round(api(x), 1)                           # coarse scores make the equations inexact

zr = [logit(min(max(api_rounded(q), 0.01), 0.99)) for q in queries]
print("from rounded scores:", [round(v - zr[0], 2) for v in zr[1:]], " (now only roughly right)")
print("label only answers:", [api_label_only(q) for q in queries], " (needs many more queries to learn the boundary)")
