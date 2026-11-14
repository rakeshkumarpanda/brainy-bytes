# 2.3 Docker and CI/CD for models
# Example "make_project" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Create the whole iris-api project of MLOps 2.3 in a new folder, with every file the chapter explains.
# Run: python make_project.py   then follow the steps in the lesson (train, test, docker build, docker run).
import os

FILES = {}

FILES['train.py'] = r"""# Train the model and save it with its metadata. Run: python train.py
import json
import os
import platform

import joblib
import sklearn
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X_train, y_train)
accuracy = round(float(model.score(X_test, y_test)), 4)

os.makedirs('model', exist_ok=True)
joblib.dump(model, 'model/iris.joblib')
meta = {'version': os.environ.get('MODEL_VERSION', '1.0.0'), 'test_accuracy': accuracy,
        'classes': ['setosa', 'versicolor', 'virginica'],
        'python': platform.python_version(), 'scikit-learn': sklearn.__version__}
with open('model/metadata.json', 'w') as f:
    json.dump(meta, f, indent=2)
print('saved model/iris.joblib, test accuracy', accuracy)
"""

FILES['app.py'] = r"""# The model API. Run: uvicorn app:app --host 0.0.0.0 --port 8000
import json

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

model = joblib.load('model/iris.joblib')           # loaded once, when the container starts
meta = json.load(open('model/metadata.json'))


class Flower(BaseModel):
    sepal_length: float = Field(gt=0, lt=20)
    sepal_width: float = Field(gt=0, lt=20)
    petal_length: float = Field(gt=0, lt=20)
    petal_width: float = Field(gt=0, lt=20)


app = FastAPI(title='Iris model', version=meta['version'])


@app.get('/health')
def health():
    return {'status': 'ok', 'model_version': meta['version']}


@app.post('/predict')
def predict(flower: Flower):
    row = [[flower.sepal_length, flower.sepal_width, flower.petal_length, flower.petal_width]]
    probs = model.predict_proba(row)[0]
    best = int(probs.argmax())
    return {'species': meta['classes'][best], 'probability': round(float(probs[best]), 3), 'model_version': meta['version']}
"""

FILES['tests/test_app.py'] = r"""# Tests that CI runs on every push: python -m pytest -q
import time

from fastapi.testclient import TestClient

from app import app, meta, model

client = TestClient(app)
SETOSA = {'sepal_length': 5.0, 'sepal_width': 3.4, 'petal_length': 1.5, 'petal_width': 0.2}


def test_health():
    r = client.get('/health')
    assert r.status_code == 200 and r.json()['status'] == 'ok'


def test_known_flower():
    r = client.post('/predict', json=SETOSA)
    assert r.status_code == 200 and r.json()['species'] == 'setosa'


def test_bad_input_is_rejected():
    r = client.post('/predict', json={'sepal_length': -1})
    assert r.status_code == 422


def test_accuracy_gate():
    assert meta['test_accuracy'] >= 0.90            # a worse model must not ship


def test_small_noise_keeps_the_class():
    a = model.predict([[5.0, 3.4, 1.5, 0.2]])[0]
    b = model.predict([[5.02, 3.38, 1.51, 0.2]])[0]
    assert a == b


def test_longer_petals_mean_virginica():
    p_small = model.predict_proba([[6.0, 3.0, 4.0, 1.2]])[0][2]
    p_large = model.predict_proba([[6.0, 3.0, 6.0, 2.2]])[0][2]
    assert p_large > p_small


def test_latency_budget():
    start = time.perf_counter()
    for _ in range(100):
        client.post('/predict', json=SETOSA)
    assert (time.perf_counter() - start) / 100 < 0.05     # under 50 ms per request
"""

FILES['requirements.txt'] = r"""fastapi==0.162.6
uvicorn==0.54.0
scikit-learn==1.8.0
numpy==2.4.6
joblib==1.6.0
"""

FILES['requirements-dev.txt'] = r"""-r requirements.txt
pytest==9.2.0
httpx==0.28.1
"""

FILES['Dockerfile'] = r"""# A small image for the model API
FROM python:3.14-slim

# No .pyc files, and print logs straight away
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Dependencies first, so this slow layer is reused while only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then the code, and train the model inside the image
ARG MODEL_VERSION=1.0.0
ENV MODEL_VERSION=$MODEL_VERSION
COPY train.py app.py ./
RUN python train.py

# Do not run as root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
"""

FILES['.dockerignore'] = r""".venv
.git
__pycache__
model
tests
*.ipynb
"""

FILES['compose.yaml'] = r"""services:
  api:
    build:
      context: .
      args:
        MODEL_VERSION: "1.0.0"
    image: iris-api:1.0.0
    ports:
      - "8000:8000"
    restart: unless-stopped
"""

FILES['.github/workflows/ci.yml'] = r"""name: model-ci

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
          cache: pip
      - run: pip install -r requirements-dev.txt
      - run: python train.py
      - run: python -m pytest -q

  image:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: Build the image
        run: docker build --build-arg MODEL_VERSION=${{ github.sha }} -t iris-api:ci .
      - name: Smoke test the container
        run: |
          docker run -d --name api -p 8000:8000 iris-api:ci
          for i in $(seq 1 20); do curl -fs http://127.0.0.1:8000/health && break || sleep 1; done
          curl -fs -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' \
            -d '{"sepal_length": 5.0, "sepal_width": 3.4, "petal_length": 1.5, "petal_width": 0.2}'
      - name: Push to GitHub Container Registry
        if: github.ref == 'refs/heads/main'
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          IMAGE=ghcr.io/${{ github.repository }}:${{ github.sha }}
          docker tag iris-api:ci $IMAGE
          docker push $IMAGE
"""

os.makedirs('iris-api', exist_ok=True)
for name, text in FILES.items():
    path = os.path.join('iris-api', name)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', newline='\n') as f:      # Unix line endings on every system, also inside the container
        f.write(text)
    print(f'{name:28s} {len(text.splitlines()):3d} lines')
print('Created the folder iris-api with', len(FILES), 'files.')
print('Next: cd iris-api, then python train.py and python -m pytest -q')
