# 3.2 Features: encoding, scaling, engineering and selection
# Example "select_features" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
X, y, names = data.data, data.target, data.feature_names
print("features:", X.shape[1])

best = SelectKBest(f_classif, k=5).fit(X, y)
print("filter (F test) top 5:", names[best.get_support()].tolist())

rfe = RFE(LogisticRegression(max_iter=5000), n_features_to_select=5).fit(StandardScaler().fit_transform(X), y)
print("wrapper (RFE) top 5:", names[rfe.support_].tolist())

lasso = LogisticRegression(l1_ratio=1.0, solver="liblinear", C=0.05).fit(StandardScaler().fit_transform(X), y)
print("embedded (L1) keeps:", int((lasso.coef_ != 0).sum()), "features")

for k in [2, 5, 30]:
    model = make_pipeline(StandardScaler(), SelectKBest(f_classif, k=k), LogisticRegression(max_iter=5000))
    print("k =", k, " cross validated accuracy:", round(cross_val_score(model, X, y, cv=5).mean(), 3))
