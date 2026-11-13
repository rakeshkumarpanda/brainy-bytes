# 1.1 What machine learning is: learning from examples
# Example "regression_or_classification" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Regression: the answer is a number
sizes = [50, 80, 120]
prices = [30, 52, 80]
price_per_m2 = sum(prices) / sum(sizes)            # a very simple model with one parameter
print("predicted price for 100 m2:", round(price_per_m2 * 100, 1), "lakh")

# Classification: the answer is a category
fruits = [
    (150, "smooth", "apple"),
    (170, "smooth", "apple"),
    (130, "bumpy", "orange"),
    (140, "bumpy", "orange"),
]

def guess_fruit(weight, skin):
    # copy the label of the most similar example (fewest differences)
    best_label = None
    best_distance = None
    for w, s, label in fruits:
        distance = abs(w - weight) / 10
        if s != skin:
            distance = distance + 5
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_label = label
    return best_label

print("160 g, smooth skin ->", guess_fruit(160, "smooth"))
print("135 g, bumpy skin  ->", guess_fruit(135, "bumpy"))
