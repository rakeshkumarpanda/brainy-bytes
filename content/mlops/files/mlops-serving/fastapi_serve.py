# 2.2 Serving models with Flask, FastAPI and Django
# Example "fastapi_serve" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Serve a model with FastAPI (pip install "fastapi[standard]" scikit-learn).
#   python fastapi_serve.py                      tries the API in this process with FastAPI's TestClient
#   uvicorn fastapi_serve:app --port 8000        starts the server, docs at http://127.0.0.1:8000/docs
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X, y)
CLASSES = ['setosa', 'versicolor', 'virginica']


class Flower(BaseModel):                      # the input contract, checked automatically
    sepal_length: float = Field(gt=0, lt=20)
    sepal_width: float = Field(gt=0, lt=20)
    petal_length: float = Field(gt=0, lt=20)
    petal_width: float = Field(gt=0, lt=20)


class Prediction(BaseModel):
    species: str
    probability: float


app = FastAPI(title='Iris model', version='1.0.0')


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/predict', response_model=Prediction)
def predict(flower: Flower):
    row = [[flower.sepal_length, flower.sepal_width, flower.petal_length, flower.petal_width]]
    probs = model.predict_proba(row)[0]
    best = int(probs.argmax())
    return Prediction(species=CLASSES[best], probability=round(float(probs[best]), 3))


@app.post('/predict_batch', response_model=list[Prediction])
def predict_batch(flowers: list[Flower]):
    rows = [[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width] for f in flowers]
    probs = model.predict_proba(rows)                 # one call for the whole batch is much faster
    return [Prediction(species=CLASSES[int(p.argmax())], probability=round(float(p.max()), 3)) for p in probs]


if __name__ == '__main__':
    client = TestClient(app)
    print('GET  /health ', client.get('/health').json())
    good = {'sepal_length': 5.9, 'sepal_width': 3.0, 'petal_length': 5.1, 'petal_width': 1.8}
    r = client.post('/predict', json=good)
    print('POST /predict', r.status_code, r.json())
    r = client.post('/predict', json={'sepal_length': -1, 'sepal_width': 'wide', 'petal_length': 1.4})
    print('POST /predict', r.status_code, [(e['loc'][-1], e['msg']) for e in r.json()['detail']])
    r = client.post('/predict_batch', json=[good, {'sepal_length': 5.0, 'sepal_width': 3.4, 'petal_length': 1.5, 'petal_width': 0.2}])
    print('POST /predict_batch', r.status_code, r.json())
    print('Routes:', sorted(r.path for r in app.routes if r.path.startswith('/p') or r.path == '/health'))
