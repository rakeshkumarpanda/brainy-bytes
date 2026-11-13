# 2.1 Linear algebra for ML: vectors, distances and matrices
# Example "vectors_by_hand" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A vector is a list of numbers. Each example in ML is one vector of features.
asha = [21, 160, 55]      # age, height_cm, weight_kg
ravi = [25, 175, 70]

def add(u, v):
    result = []
    for a, b in zip(u, v):
        result.append(a + b)
    return result

def scale(c, v):
    result = []
    for a in v:
        result.append(c * a)
    return result

def dot(u, v):
    total = 0
    for a, b in zip(u, v):
        total = total + a * b
    return total

print("asha + ravi =", add(asha, ravi))
print("half of ravi =", scale(0.5, ravi))
print("average person =", scale(0.5, add(asha, ravi)))
print("dot(asha, ravi) =", dot(asha, ravi))
