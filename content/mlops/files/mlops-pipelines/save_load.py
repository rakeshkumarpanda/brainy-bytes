# 2.1 Pipelines and saving models
# Example "save_load" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Save the fitted pipeline as one file, load it back, and store the facts needed to trust it later.
import json
import os
import platform
import tempfile
from importlib.metadata import version

import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X, y)

folder = tempfile.mkdtemp()
model_path = os.path.join(folder, 'iris_model.joblib')
joblib.dump(model, model_path)
meta = {'model_file': 'iris_model.joblib', 'trained_on_rows': len(X),
        'features': ['sepal length', 'sepal width', 'petal length', 'petal width'],
        'classes': ['setosa', 'versicolor', 'virginica'],
        'python': platform.python_version(), 'scikit-learn': version('scikit-learn'), 'joblib': version('joblib')}
with open(os.path.join(folder, 'iris_model.json'), 'w') as f:
    json.dump(meta, f, indent=2)
print('Saved', sorted(os.listdir(folder)), 'model size', os.path.getsize(model_path), 'bytes')

loaded = joblib.load(model_path)                      # in the serving code, possibly on another computer
same = (loaded.predict(X) == model.predict(X)).all()
print('Loaded model gives identical predictions:', bool(same))
flower = [[5.9, 3.0, 5.1, 1.8]]
print('Prediction for', flower[0], '->', meta['classes'][loaded.predict(flower)[0]])
print('Load it with the same scikit-learn version:', meta['scikit-learn'])
