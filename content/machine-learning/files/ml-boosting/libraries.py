# 3.3 Boosting: small trees that fix each other
# Example "libraries" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import lightgbm as lgb
import xgboost as xgb
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True, as_frame=True)     # a DataFrame keeps the column names
models = {
    "sklearn HistGB": HistGradientBoostingClassifier(random_state=0),
    "XGBoost": xgb.XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.1, random_state=0, n_jobs=1),
    "LightGBM": lgb.LGBMClassifier(n_estimators=200, num_leaves=15, learning_rate=0.1, random_state=0, verbose=-1, n_jobs=1),
}
for name, model in models.items():
    print(name.ljust(15), "accuracy", round(cross_val_score(model, X, y, cv=5).mean(), 3))
