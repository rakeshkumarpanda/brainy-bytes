# 3.2 Features: encoding, scaling, engineering and selection
# Example "column_transformer" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

rng = np.random.default_rng(5)
n = 300
people = pd.DataFrame({
    "age": rng.integers(18, 70, n).astype(float),
    "income": rng.normal(50, 15, n),
    "city": rng.choice(["Delhi", "Pune", "Mumbai"], n),
    "plan": rng.choice(["basic", "pro"], n),
})
people.loc[rng.choice(n, 20, replace=False), "income"] = np.nan
bought = ((people["income"].fillna(50) > 55) | (people["plan"] == "pro")).astype(int)

numbers = ["age", "income"]
labels = ["city", "plan"]
prep = ColumnTransformer([
    ("num", Pipeline([("fill", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numbers),
    ("cat", OneHotEncoder(handle_unknown="ignore"), labels),
])
model = Pipeline([("prep", prep), ("clf", LogisticRegression())])
print("cross validated accuracy:", round(cross_val_score(model, people, bought, cv=5).mean(), 3))
model.fit(people, bought)
print("columns the model sees:", model.named_steps["prep"].get_feature_names_out().tolist())
