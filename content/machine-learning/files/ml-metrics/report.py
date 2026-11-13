# 4.1 Metrics: measuring a model properly
# Example "report" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)          # 0 = malignant, 1 = benign
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
pred = model.predict(X_test)
print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred, target_names=["malignant", "benign"], digits=3))
