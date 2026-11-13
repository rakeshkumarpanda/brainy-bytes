# 3.1 Decision trees: a chain of yes or no questions
# Example "tree_iris" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, export_text

iris = load_iris()
tree = DecisionTreeClassifier(max_depth=2, random_state=0).fit(iris.data, iris.target)
names = [n.replace(" (cm)", "") for n in iris.feature_names]
print(export_text(tree, feature_names=names, class_names=list(iris.target_names)))
print("training accuracy:", round(tree.score(iris.data, iris.target), 3))
print("a flower 5.0, 3.4, 1.5, 0.2 is:", str(iris.target_names[tree.predict([[5.0, 3.4, 1.5, 0.2]])[0]]))
