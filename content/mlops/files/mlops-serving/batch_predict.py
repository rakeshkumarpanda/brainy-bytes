# 2.2 Serving models with Flask, FastAPI and Django
# Example "batch_predict" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Batch prediction: score a whole file at once, for example every night, instead of one request at a time.
import io
import time

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X, y)
classes = np.array(['setosa', 'versicolor', 'virginica'])

rng = np.random.default_rng(0)
rows = X[rng.integers(0, len(X), 20000)] + rng.normal(0, 0.1, (20000, 4))
csv_in = io.StringIO()
pd.DataFrame(rows.round(2), columns=['sl', 'sw', 'pl', 'pw']).to_csv(csv_in, index=False)
csv_in.seek(0)

out = io.StringIO()
start, total = time.perf_counter(), 0
for i, chunk in enumerate(pd.read_csv(csv_in, chunksize=5000)):     # chunks keep memory small for huge files
    chunk['species'] = classes[model.predict(chunk[['sl', 'sw', 'pl', 'pw']].to_numpy())]
    chunk.to_csv(out, index=False, header=(i == 0))
    total += len(chunk)
batch_seconds = time.perf_counter() - start

start = time.perf_counter()
for r in rows[:200]:                                                  # the same work, one row per call
    model.predict([r])
one_by_one = (time.perf_counter() - start) / 200 * len(rows)

result = pd.read_csv(io.StringIO(out.getvalue()))
print('Scored', total, 'rows in 4 chunks of 5000')
print(result['species'].value_counts().to_string())
print(f'Batch took about {batch_seconds:.2f} s. One call per row would take about {one_by_one:.1f} s ({one_by_one / batch_seconds:.0f} times longer).')
