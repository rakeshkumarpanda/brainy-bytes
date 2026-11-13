# 1.2 The machine learning project: from a question to a working model
# Example "frame_the_problem" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Write the problem down before touching any model
project = {
    "goal": "Show customers a delivery time they can trust",
    "prediction": "minutes until the food arrives",
    "task type": "regression (the answer is a number)",
    "data": "past orders with distance, hour, weather and real minutes",
    "metric": "mean absolute error in minutes",
    "success": "average error under 5 minutes",
    "baseline": "3 minutes per km plus 10 minutes",
}
for key, value in project.items():
    print(key.ljust(11), ":", value)

# A quick check that the baseline gives sensible numbers
for km in [1, 4, 8]:
    print(km, "km ->", 3 * km + 10, "minutes")
