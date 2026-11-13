# 1.1 What machine learning is: learning from examples
# Example "words_of_ml" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# A tiny dataset: each row is one example (one house)
houses = [
    # size_m2, rooms, age_years -> price in lakh
    {"size_m2": 50, "rooms": 1, "age_years": 10, "price": 30},
    {"size_m2": 80, "rooms": 2, "age_years": 5, "price": 52},
    {"size_m2": 120, "rooms": 3, "age_years": 2, "price": 80},
    {"size_m2": 65, "rooms": 2, "age_years": 20, "price": 35},
]

feature_names = ["size_m2", "rooms", "age_years"]   # the inputs (features)
label_name = "price"                                 # the answer we want (label or target)

X = []   # features of every example
y = []   # label of every example
for house in houses:
    row = []
    for name in feature_names:
        row.append(house[name])
    X.append(row)
    y.append(house[label_name])

print("number of examples:", len(X))
print("number of features:", len(feature_names))
print("X =", X)
print("y =", y)
print("first example: features", X[0], "label", y[0])
