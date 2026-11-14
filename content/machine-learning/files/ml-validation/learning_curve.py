# 4.2 Validation: honest estimates of performance
# Example "learning_curve" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_digits
from sklearn.model_selection import learning_curve
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

X, y = load_digits(return_X_y=True)
for name, model in [("naive Bayes", GaussianNB()), ("RBF SVM", SVC(gamma=0.001))]:
    sizes, train, val = learning_curve(model, X, y, train_sizes=[0.05, 0.2, 0.5, 1.0], cv=5, shuffle=True, random_state=0)
    print(name)
    for n, t, v in zip(sizes, train.mean(axis=1), val.mean(axis=1)):
        print("   training rows", str(n).rjust(4), " train", round(float(t), 3), " validation", round(float(v), 3))
