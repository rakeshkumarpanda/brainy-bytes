# 4.3 Tuning and calibration
# Example "validation_curve" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import validation_curve
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
depths = [1, 2, 3, 4, 6, 10]
train, val = validation_curve(DecisionTreeClassifier(random_state=0), X, y, param_name="max_depth", param_range=depths, cv=5)
for d, t, v in zip(depths, train.mean(axis=1), val.mean(axis=1)):
    print("max_depth", str(d).rjust(2), " train", round(float(t), 3), " validation", round(float(v), 3))
