# 3.3 Explainability and fairness
# Example "importance" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Which features does the model really use? Impurity importance against permutation importance.
# We add a column of random ID numbers that has nothing to do with the label.
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

data = load_breast_cancer()
keep = ['worst radius', 'worst concave points', 'mean texture', 'worst smoothness']
X = data.data[:, [list(data.feature_names).index(k) for k in keep]]
rng = np.random.default_rng(0)
X = np.column_stack([X, rng.integers(0, 100000, len(X))])            # random_id: pure noise, many values
names = keep + ['random_id']
X_train, X_test, y_train, y_test = train_test_split(X, data.target, test_size=0.3, random_state=0, stratify=data.target)

forest = RandomForestClassifier(n_estimators=300, random_state=0).fit(X_train, y_train)
print('test accuracy', round(forest.score(X_test, y_test), 3))
perm = permutation_importance(forest, X_test, y_test, n_repeats=20, random_state=0)
print(f'{"feature":22s} {"impurity":>9s} {"permutation (test)":>19s}')
for i in np.argsort(-perm.importances_mean):
    print(f'{names[i]:22s} {forest.feature_importances_[i]:9.3f} {perm.importances_mean[i]:12.3f} +- {perm.importances_std[i]:.3f}')
print('Impurity importance gives the random ID a share because it offers many split points on training data.')
print('Permutation importance on test data shows that shuffling it changes nothing.')
