# MLOps 2.3: Docker and CI/CD for a model. Checked against the Docker documentation (Dockerfile reference, Build cache,
# Best practices for writing Dockerfiles, Compose file reference, Docker Desktop install guides for Mac and Windows with
# WSL 2, Docker Engine install guides for Ubuntu, Debian and Fedora), the GitHub Actions documentation (workflow syntax,
# setup-python, publishing images to GitHub Packages), Breck and colleagues, The ML Test Score (IEEE Big Data 2017),
# Ribeiro and colleagues, Beyond Accuracy: Behavioral Testing of NLP Models with CheckList (ACL 2020), and Humble and
# Farley, Continuous Delivery (2010). Every command and output on the page comes from a real run of the project.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, term, show, leet_items
from mlkit import link, ossteps

chapter('mlops-docker')
K = Kit()
K.code('make_project', r'''
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
''', long=True)

K.code('model_tests', r'''
# Tests for a model, not only for code. Four kinds that CI can run on every push:
# a quality gate, known examples, invariance and a directional check. Run: python model_tests.py
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)


def train(labels):
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X_train, labels)


def run_tests(model):
    results = {}
    results['accuracy gate (at least 0.90)'] = model.score(X_test, y_test) >= 0.90
    known = [([5.0, 3.4, 1.5, 0.2], 0), ([6.9, 3.1, 5.4, 2.1], 2)]             # flowers everyone agrees on
    results['known examples'] = all(model.predict([x])[0] == want for x, want in known)
    rng = np.random.default_rng(0)
    noisy = X_test + rng.normal(0, 0.02, X_test.shape)                          # tiny measuring noise
    results['invariance to tiny noise'] = (model.predict(noisy) == model.predict(X_test)).mean() >= 0.95
    small, large = [6.0, 3.0, 4.0, 1.2], [6.0, 3.0, 6.0, 2.2]
    results['longer petals raise P(virginica)'] = model.predict_proba([large])[0][2] > model.predict_proba([small])[0][2]
    return results


good = train(y_train)
print('Good model, test accuracy', round(good.score(X_test, y_test), 4))
for name, ok in run_tests(good).items():
    print(f'  {"PASS" if ok else "FAIL"}  {name}')

shuffled = np.random.default_rng(1).permutation(y_train)                       # a broken training run
bad = train(shuffled)
print('Broken model (shuffled labels), test accuracy', round(bad.score(X_test, y_test), 4))
for name, ok in run_tests(bad).items():
    print(f'  {"PASS" if ok else "FAIL"}  {name}')
print('CI would block the broken model:', not all(run_tests(bad).values()))
''', long=True)

K.code('layer_cache', r'''
# Which Dockerfile steps run again after a change? A small model of Docker's layer cache.
# A step runs again if the files it copies changed, or if any step before it ran again.
# Step times are seconds from real builds of the chapter's project.
GOOD = [('FROM python:3.14-slim', [], 0), ('WORKDIR /app', [], 0),
        ('COPY requirements.txt .', ['requirements.txt'], 0), ('RUN pip install -r requirements.txt', [], 18),
        ('COPY train.py app.py ./', ['train.py', 'app.py'], 0), ('RUN python train.py', [], 1.6),
        ('RUN useradd appuser', [], 0.1)]
BAD = [('FROM python:3.14-slim', [], 0), ('WORKDIR /app', [], 0),
       ('COPY . .', ['requirements.txt', 'train.py', 'app.py'], 0.4), ('RUN pip install -r requirements.txt', [], 18.6),
       ('RUN python train.py', [], 1.2)]


def rebuild(steps, changed):
    again, total = False, 0.0
    for instruction, files, seconds in steps:
        if any(f in changed for f in files):
            again = True
        if again:
            total += seconds
        print(f'    {"runs again" if again else "CACHED    "}  {instruction}')
    return total


for name, steps in [('Good order', GOOD), ('Bad order', BAD)]:
    for changed in [{'app.py'}, {'requirements.txt'}]:
        print(f'{name}, changed {sorted(changed)[0]}:')
        print(f'    about {rebuild(steps, changed):.1f} s of steps ran again')
''', long=True)

PROJECT = {}
PROJECT['tests/test_app.py'] = r"""# Tests that CI runs on every push: python -m pytest -q
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
PROJECT['Dockerfile'] = r"""# A small image for the model API
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
PROJECT['compose.yaml'] = r"""services:
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
PROJECT['.github/workflows/ci.yml'] = r"""name: model-ci

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

REAL_RUN = term(['$ docker build -t iris-api:1.0.0 .', '#8 [4/7] RUN pip install --no-cache-dir -r requirements.txt', '#8 DONE 17.9s', '#10 [6/7] RUN python train.py', '#10 1.396 saved model/iris.joblib, test accuracy 0.9111', '#12 naming to docker.io/library/iris-api:1.0.0 done', '',
       '$ docker images iris-api', 'IMAGE            ID             DISK USAGE   CONTENT SIZE', 'iris-api:1.0.0   8ee36f3e2459        555MB          129MB', '',
       '$ curl http://127.0.0.1:8000/health', '{"status":"ok","model_version":"1.0.0"}', '$ curl -X POST http://127.0.0.1:8000/predict ...', '{"species":"virginica","probability":0.653,"model_version":"1.0.0"}', '',
       '$ docker exec api whoami', 'appuser', '$ docker ps --format "{{.Names}} {{.Status}}"', 'api Up 34 seconds (healthy)'], 'Real run (Linux, Docker 29)')
RUN_LINES = ['python3 make_project.py          # creates the folder iris-api', 'cd iris-api',
             'docker build -t iris-api:1.0.0 .', 'docker run -d --name api -p 8000:8000 iris-api:1.0.0']
STOP_LINES = ['docker logs api                  # what the server printed', 'docker stop api', 'docker rm api']
FLOWER = '{"sepal_length": 5.9, "sepal_width": 3.0, "petal_length": 5.1, "petal_width": 1.8}'

BUILD_MAC = ('<ol><li>Start <b>Docker Desktop</b> (installed in MLOps 1.1) and wait until the whale icon in the menu bar says it is running.</li>'
             '<li>Download <code>make_project.py</code> from this lesson into your project folder and run the commands below in Terminal.</li>'
             '<li>Open <code>http://127.0.0.1:8000/docs</code> in the browser to try the API by clicking.</li></ol>'
             + term(RUN_LINES + ['curl http://127.0.0.1:8000/health',
                                 f"curl -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{FLOWER}'"] + STOP_LINES, 'Terminal (macOS)')
             + '<p>A Mac with Apple silicon (M1 and later) builds <b>arm64</b> images. Most cloud servers run <b>amd64</b>. To build for them, add a platform. It runs slower on a Mac because Docker emulates the other processor.</p>'
             + term(['docker buildx build --platform linux/amd64 -t iris-api:1.0.0-amd64 .'], 'Terminal (macOS, Apple silicon)'))
BUILD_WIN = ('<ol><li>Start <b>Docker Desktop</b> and check that it uses the <b>WSL 2</b> engine (Settings, General). The whale icon in the taskbar must say Engine running.</li>'
             '<li>Run the commands in PowerShell. The Docker commands are the same as on macOS and Linux.</li>'
             '<li>The files that <code>make_project.py</code> writes use Unix line endings, which containers need. If you later add a shell script, keep it at LF in VS Code (bottom right corner), because a script saved with Windows CRLF endings fails inside a Linux container with a confusing not found error.</li></ol>'
             + term(['python make_project.py', 'cd iris-api', 'docker build -t iris-api:1.0.0 .', 'docker run -d --name api -p 8000:8000 iris-api:1.0.0',
                     'Invoke-RestMethod http://127.0.0.1:8000/health',
                     f"Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -ContentType 'application/json' -Body '{FLOWER}'"] + STOP_LINES, 'PowerShell (Windows)')
             + '<p>Builds are faster when the project folder lives inside the WSL Linux file system (open Ubuntu from the Start menu and work in your Linux home folder) instead of on drive C, because Docker then reads the files without crossing between Windows and Linux.</p>')
BUILD_LINUX = ('<p>Docker Engine runs as a system service. Add yourself to the <code>docker</code> group once so you do not need <code>sudo</code> before every command, then log out and back in.</p>'
               + term(['sudo usermod -aG docker $USER                # once, then log out and in', 'sudo systemctl enable --now docker            # Fedora: start the service (Ubuntu starts it already)', ''] + RUN_LINES
                      + ['curl http://127.0.0.1:8000/health', f"curl -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{FLOWER}'"] + STOP_LINES, 'Terminal (Linux)')
               + '<p>Being in the docker group gives the same power as root on that machine, so only add trusted users. Rootless Docker is an option on shared machines.</p>')
BUILD_CHROME = ('<p>Use Docker Engine inside the Linux development environment (installed in MLOps 1.1 with Docker&rsquo;s Debian steps). An ARM Chromebook builds arm64 images, an Intel or AMD one builds amd64. Chrome opens <code>http://localhost:8000/docs</code> because ChromeOS forwards the port from Linux.</p>'
                + term(['sudo usermod -aG docker $USER                # once, then restart the Linux environment'] + RUN_LINES + ['curl http://127.0.0.1:8000/health'] + STOP_LINES, 'Terminal (ChromeOS Linux)')
                + '<p>Building images uses a lot of disk space. If the build stops with no space left on device, raise the Linux disk size in Settings (search for Linux development environment, then Disk size) and run <code>docker system prune</code> to delete old layers.</p>')

CHECK_MAC = term(['cd iris-api', 'python3 -m venv .venv && source .venv/bin/activate', 'pip install -r requirements-dev.txt', 'python train.py', 'python -m pytest -q'], 'Terminal (macOS)')
CHECK_WIN = term(['cd iris-api', 'py -3.14 -m venv .venv', '.venv\\Scripts\\Activate.ps1', 'pip install -r requirements-dev.txt', 'python train.py', 'python -m pytest -q'], 'PowerShell (Windows)')
CHECK_LINUX = term(['cd iris-api', 'python3 -m venv .venv && source .venv/bin/activate', 'pip install -r requirements-dev.txt', 'python train.py', 'python -m pytest -q'], 'Terminal (Linux)')
CHECK_CHROME = term(['cd iris-api', 'uv venv --python 3.14 && source .venv/bin/activate', 'uv pip install -r requirements-dev.txt', 'python train.py', 'python -m pytest -q'], 'Terminal (ChromeOS Linux)')

K.lesson('docker', 'Containers, images and the Dockerfile', f'''
{src('Docker documentation: Dockerfile reference, Build cache, and Best practices for writing Dockerfiles.')}
{wwh('A <b>Docker image</b> is a sealed package with an operating system layer, Python, the pinned packages, your code and the trained model. A <b>container</b> is a running copy of an image. A <b>Dockerfile</b> is the recipe that builds the image, one instruction per line, and a <b>registry</b> such as Docker Hub or GitHub Container Registry stores images so servers can pull them.',
     'A virtual environment pins Python packages, but not the operating system, the system libraries or the Python build. An image pins all of it, so the model runs the same on your laptop, in CI and on the server, and on macOS, Windows, Linux and ChromeOS alike.',
     'Start from a small official base image, copy and install the requirements first, then copy the code. Train or copy the model, switch to a user that is not root, open the port, add a health check and say which command starts the server.')}
{table(['Word', 'What it is', 'Command'], [
    ['Image', 'A read only package built from a Dockerfile, made of layers', '<code>docker build -t iris-api:1.0.0 .</code>'],
    ['Container', 'A running copy of an image, with its own file system and network', '<code>docker run -p 8000:8000 iris-api:1.0.0</code>'],
    ['Tag', 'A name and version for an image', '<code>iris-api:1.0.0</code>'],
    ['Registry', 'A store for images that servers pull from', '<code>docker push ghcr.io/owner/iris-api:1.0.0</code>'],
    ['Port mapping', 'Connects a port on your computer to a port in the container', '<code>-p 8000:8000</code> means computer 8000 to container 8000']])}
{show('Dockerfile', PROJECT['Dockerfile'], {2: 'The official slim Python image: Debian with Python 3.14 and little else. Alpine is smaller but uses musl instead of glibc, so scientific packages may need compiling.', 5: 'Do not write .pyc files, and send print output straight to the logs.', 6: 'Every later path is inside /app.', 9: 'Only requirements.txt first. This layer changes rarely.', 10: 'The slow step. Because it comes before the code, Docker reuses it from the cache after a code change.', 13: 'A value you can pass at build time with --build-arg, here the model version.', 15: 'The code comes after the packages.', 16: 'Train inside the image, so the model and the library versions always match. Bigger models are trained elsewhere and copied in.', 19: 'Create a normal user.', 20: 'Run the server as that user, not as root, so a bug in the app cannot take over the container.', 22: 'Documents the port the app listens on.', 23: 'Docker calls /health every 30 seconds and marks the container healthy or unhealthy. The slim image has no curl, so Python does the call.', 24: 'The command that starts when the container starts: Uvicorn with 2 workers on all network interfaces inside the container.'}, lang='dockerfile')}
{viz('mllayers')}
{run('layer_cache')}
{note('Real timings of this project: with the good order, a one line change in app.py rebuilt in 2.2 seconds in total, because pip install came from the cache. With <code>COPY . .</code> before pip install, the same change took 32 seconds, because the 18 second install ran again.', 'exam')}
''', kw=['Docker', 'image', 'container', 'Dockerfile', 'layer', 'build cache', 'registry', 'tag', 'port mapping', 'non root user', 'HEALTHCHECK'])

K.lesson('build', 'Build and run the model container on your computer', f'''
{src('Docker documentation: Docker Desktop for Mac and for Windows (WSL 2 backend), Docker Engine for Ubuntu, Debian and Fedora, Post installation steps for Linux, and the Compose file reference.')}
{wwh('One download, <code>make_project.py</code>, creates the whole project of this chapter: the training script, the FastAPI app, the tests, the requirements, the Dockerfile, the Compose file and the GitHub Actions workflow.',
     'Running the real thing once on your own computer makes every later idea concrete: images, containers, ports, health checks and logs.',
     'Run make_project.py, build the image, start a container in the background, call it, read its logs, and stop it. Then do the same with one Compose command.')}
{run('make_project')}
{ossteps('Build the image and run the container', BUILD_MAC, BUILD_WIN, BUILD_LINUX, BUILD_CHROME)}
<p>This is the real output of those commands for this project:</p>
{REAL_RUN}
{note('The probability here is 0.653, not the 0.703 of MLOps 2.2, because train.py holds back 30 percent of the flowers for testing and trains on the rest. The image takes 555 MB on disk but only 129 MB is downloaded, because layers are stored compressed.', 'tip')}
{show('compose.yaml', PROJECT['compose.yaml'], {2: 'One service called api. A bigger project adds a database or a monitoring service next to it.', 4: 'Build from the Dockerfile in this folder.', 6: 'Passed to the ARG line of the Dockerfile.', 9: 'Computer port 8000 to container port 8000.', 10: 'Start again after a crash or a reboot, unless you stopped it yourself.'}, lang='yaml')}
{term(['docker compose up -d --build      # build if needed, then start in the background', 'docker compose ps', 'docker compose logs -f api         # follow the logs, Control and C to stop following', 'docker compose down                # stop and remove'], 'Terminal or PowerShell (every system)')}
''', kw=['make_project', 'docker build', 'docker run', 'docker logs', 'docker compose', 'Docker Desktop', 'WSL 2', 'Apple silicon', 'arm64', 'amd64', 'docker group'])

K.lesson('tests', 'Testing a model, not only the code', f'''
{src('Breck, Cai, Nielsen, Salib and Sculley, The ML Test Score: A Rubric for ML Production Readiness (2017), and Ribeiro, Wu, Guestrin and Singh, Beyond Accuracy: Behavioral Testing of NLP Models with CheckList (2020).')}
{wwh('Normal tests check that code does what it should. A model also needs <b>behaviour tests</b>: a <b>quality gate</b> (accuracy must stay above a line), <b>known examples</b> that any good model gets right, <b>invariance</b> (tiny changes that should not change the answer) and <b>directional</b> checks (a change that should push the answer one way).',
     'A training run can finish without any error and still produce a useless model, for example after a data bug shuffles the labels. Without behaviour tests, CI stays green and the bad model ships.',
     'Write the tests with pytest next to the app. Keep them fast, so they run on every push. Choose the gate from the current model&rsquo;s score and its uncertainty, not from a wish.')}
{table(['Test', 'Question it answers', 'In this project'], [
    ['API test', 'Do the routes answer correctly?', 'test_health, test_known_flower'],
    ['Input test', 'Is bad input rejected?', 'test_bad_input_is_rejected (422)'],
    ['Quality gate', 'Is the model good enough to ship?', 'test_accuracy_gate (at least 0.90)'],
    ['Invariance', 'Does tiny noise leave the answer alone?', 'test_small_noise_keeps_the_class'],
    ['Directional', 'Does a change push the answer the right way?', 'test_longer_petals_mean_virginica'],
    ['Latency', 'Is it fast enough?', 'test_latency_budget (under 50 ms)']])}
{run('model_tests')}
{note('The broken model scored 0.2 and failed three of the four checks, so CI blocks it. Look closely: it still passed the invariance test, because a model that ignores its input is perfectly stable. One kind of test is never enough.', 'warn')}
{show('tests/test_app.py', PROJECT['tests/test_app.py'], {4: 'TestClient calls the app in the same process, no server needed.', 6: 'Importing app also loads the model, exactly as the server does.', 9: 'A flower that every good model calls setosa.', 28: 'The quality gate. A model below 0.90 fails CI and cannot be merged.', 31: 'Invariance: a change of a few hundredths of a centimetre must not change the class.', 37: 'Directional: longer, wider petals should make virginica more likely.', 43: 'A rough latency budget. Real load tests use tools such as Locust on the running container.'})}
{fxs(fx('Chance a suite of flaky tests is green', 'P(green) = (1 &minus; p)<sup>n</sup>', 'n independent tests that each fail at random with probability p. Ten tests at 2 percent: 0.98<sup>10</sup> = 0.817.', key=True),
     fx('Uncertainty of a test accuracy', 'SE = &radic;(p(1 &minus; p) / n)', 'With p = 0.9111 on n = 45 test rows, SE = 0.042, so a gate at 0.90 is less than one standard error away.', key=True))}
''', kw=['model testing', 'quality gate', 'invariance test', 'directional test', 'pytest', 'TestClient', 'ML Test Score', 'CheckList', 'flaky test'])

K.lesson('ci', 'CI/CD with GitHub Actions', f'''
{src('GitHub Actions documentation: Workflow syntax, Building and testing Python, and Publishing Docker images. Humble and Farley, Continuous Delivery (2010).')}
{viz('mlcipipe')}
{wwh('<b>Continuous integration</b> (CI) runs the same checks on a clean machine for every push and pull request. <b>Continuous delivery</b> (CD) turns every green change on main into a released artefact, here a container image in a registry, ready to deploy. <b>GitHub Actions</b> runs both from a YAML file in <code>.github/workflows</code>.',
     'Checks that only run on your laptop get skipped on a busy day, and a laptop has packages a clean server does not. CI catches a broken model or a missing file before anyone merges it, and CD makes every release the same few steps.',
     'Commit the workflow file. Make the pull request wait for the green check (branch protection). Tag each image with the commit id, keep passwords in repository secrets, and roll back by running the previous tag.')}
{show('.github/workflows/ci.yml', PROJECT['.github/workflows/ci.yml'], {3: 'When to run: every push to main and every pull request.', 9: 'The first job installs, trains and tests.', 10: 'A fresh Ubuntu machine for every run.', 16: 'Cache downloaded packages between runs to save time.', 17: 'The same pinned versions as on your computer.', 19: 'Any failing test turns the run red.', 22: 'The image job only starts when the test job passed.', 26: 'Allows this job to push to GitHub Container Registry with the built in token.', 30: 'The commit id becomes the model version inside the image.', 34: 'Wait up to 20 seconds for the container to answer /health.', 35: 'curl -f fails on any 4xx or 5xx status, so a broken /predict also turns the run red.', 38: 'Only main publishes an image. Pull requests stop after the smoke test.', 40: 'GITHUB_TOKEN is created for every run. Never write a password in the file itself.', 41: 'Image names in ghcr.io must be lower case, so use a lower case repository name.'}, lang='yaml')}
<p>Run exactly what CI runs on your own computer before you push. This is the real result for this project: <code>7 passed in 1.57s</code>.</p>
{ossteps('Run the CI checks on your computer', CHECK_MAC, CHECK_WIN, CHECK_LINUX, CHECK_CHROME)}
{steps('Turn it on for your repository', [
    'Create a repository on GitHub and push the iris-api folder, including <code>.github/workflows/ci.yml</code>.',
    'Open the <b>Actions</b> tab. The workflow named model-ci starts on its own for the push.',
    'In Settings, Branches, add a rule for main that requires the test and image checks to pass before merging.',
    'Open a pull request that lowers the gate or breaks the model, and watch the check turn red.',
    'After a merge to main, find the new image under Packages on the repository page.'])}
{deep('Continuous training, canary releases and rollbacks', '<p>CI/CD for ML often adds a third loop, <b>continuous training</b>: a schedule or a drift alarm retrains the model on fresh data, and the new model goes through the same gate. Releases are safer as a <b>canary</b>: send 5 percent of traffic to the new image, compare its errors with the old one, and only then move everyone over. Because every image is tagged with its commit id, a rollback is one command that runs the previous tag.</p>')}
''', kw=['CI/CD', 'continuous integration', 'continuous delivery', 'GitHub Actions', 'workflow', 'smoke test', 'branch protection', 'GHCR', 'secrets', 'canary', 'rollback'])

K.lesson('versus', 'Virtual environment, container or virtual machine', f'''
{versus('Ways to package a model service', ['', 'Virtual environment', 'Docker container', 'Virtual machine'], [
    ['Pins', 'Python packages only', 'Packages, Python, system libraries and OS files', 'A whole operating system and kernel'],
    ['Start time', 'Instant', 'About a second', 'Tens of seconds'],
    ['Size', 'Hundreds of MB', 'Hundreds of MB, shared layers', 'Many GB'],
    ['Same on every computer', 'No: OS and Python can differ', 'Yes, for the same processor type', 'Yes'],
    ['Isolation', 'None', 'Process level, shares the host kernel', 'Strong, own kernel'],
    ['Best for', 'Writing and testing code', 'Shipping services, CI, Kubernetes', 'Strict isolation or a different OS']],
    'Develop in a virtual environment, ship in a container, and leave virtual machines to the platform that runs your containers.')}
''', kw=['venv vs Docker', 'container vs virtual machine'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Pack the model and everything it needs into one box that runs the same on any computer, and let a robot test every change before it goes out.</p>',
    '<p>Write a Dockerfile with good layer order, run it with Compose, test the model with a quality gate and behaviour tests, and run them in GitHub Actions.</p>',
    '<p>Build multi stage and multi platform images, publish them to a registry tagged by commit, protect branches, and choose gates from the uncertainty of the score.</p>',
    '<p>Run continuous training with canary releases and automatic rollback, sign images and scan them for vulnerabilities, and deploy to Kubernetes with GitOps.</p>')}
{grow('Build and run the model container.',
      'Test and ship every change automatically.',
      'Release models safely at scale.')}
''', kw=['beginner', 'expert', 'Kubernetes', 'continuous training', 'image signing'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An <b>image</b> packs the OS layer, Python, the pinned packages, the code and the model. A <b>container</b> is a running copy. The same image runs the same on every system.',
    'Order the Dockerfile for the <b>layer cache</b>: requirements and pip install first, code later. A code change then rebuilt in 2.2 s instead of 32 s.',
    'Run as a user that is not root, add a HEALTHCHECK, and start with <code>docker run -p 8000:8000</code> or <code>docker compose up</code>.',
    'Test the model, not only the code: a <b>quality gate</b>, known examples, <b>invariance</b> and <b>directional</b> checks. The broken model still passed invariance, so use several kinds.',
    '<b>GitHub Actions</b> runs install, train, test, build, smoke test and push on every change, and the first failure blocks the release.'],
    'Coming next: tracking experiments and keeping a registry of model versions.')}
{files('Three tasks: bump a model version, check a quality gate, and work out which Docker layers rebuild.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A Docker container is', ['A Python package', 'A running copy of an image', 'A Git branch', 'A cloud account'], 1, 'Image runs, container exists.', 'Many containers can run from one image.')
K.quiz('e', 'The file that tells Docker how to build an image is the', ['requirements.txt', 'Dockerfile', 'compose.yaml', 'ci.yml'], 1, 'The recipe.', 'One instruction per line.')
K.quiz('e', 'docker run -p 8000:8000 iris-api:1.0.0 means', ['Use 8000 MB of memory', 'Connect port 8000 on your computer to port 8000 in the container', 'Run 8000 copies', 'Wait 8000 seconds'], 1, 'Port mapping.', 'Host port first, container port second.')
K.quiz('e', 'CI runs the tests', ['Once a year', 'On a clean machine for every push and pull request', 'Only on the developer&rsquo;s laptop', 'After users complain'], 1, 'Continuous.', 'Every change is checked the same way.')
K.quiz('m', 'Why copy requirements.txt and run pip install before copying the code?', ['Pip needs it', 'So a code change reuses the cached pip install layer', 'Smaller image', 'Security'], 1, 'Layer cache.', '2.2 s instead of 32 s in this project.')
K.quiz('m', 'Why add USER appuser to the Dockerfile?', ['Faster startup', 'So the server does not run as root inside the container', 'Required by FastAPI', 'To save disk'], 1, 'Least privilege.', 'A bug then has less power.')
K.quiz('m', 'An invariance test checks that', ['Accuracy is high', 'Tiny changes that should not matter leave the prediction alone', 'The API is fast', 'Labels are balanced'], 1, 'Stable answers.', 'CheckList calls it INV.')
K.quiz('m', 'On Linux you get permission denied on the Docker socket. The usual fix is', ['Reinstall Python', 'Add your user to the docker group and log in again', 'Use port 80', 'Delete the image'], 1, 'Group membership.', 'Or prefix commands with sudo.')
K.quiz('m', 'A Mac with Apple silicon builds an image that fails on an amd64 server. Fix:', ['Use Alpine', 'Build with docker buildx build --platform linux/amd64', 'Use a newer Python', 'Rename the tag'], 1, 'Processor type.', 'Images are built per platform.')
K.quiz('h', 'All pytest tests pass but the container never answers /health. Which CI step catches it?', ['Install', 'The smoke test that starts the container and calls it', 'Checkout', 'None'], 1, 'Test the real artefact.', 'Unit tests do not run the image.')
K.quiz('h', 'A broken model that ignores its input will usually still pass', ['The accuracy gate', 'An invariance test', 'Known examples', 'A directional test'], 1, 'Constant output is stable.', 'Use several kinds of tests.')
K.quiz('h', 'Test accuracy 0.9111 on 45 rows with a gate at 0.90. The main risk is', ['Too strict', 'The gate is within one standard error, so a good model can fail by chance', 'No risk', 'Overfitting the gate'], 1, 'SE about 0.042.', 'Use more test data or a lower, justified gate.')
K.quiz('x', 'In the style of a Google MLOps exam: which practice makes a rollback fastest?', ['Retraining from scratch', 'Tagging each image with its commit id and redeploying the previous tag', 'Editing the server by hand', 'Deleting the registry'], 1, 'Immutable versions.', 'The old image is still there.')
K.quiz('x', 'In the style of an ML engineering interview: new model error 7 percent against old 5 percent. A canary needs roughly how many requests to see a 2 point gap at two standard errors?', ['About 65', 'About 650', 'About 65,000', 'About 6.5 million'], 1, 'n = 4p(1&minus;p) / d<sup>2</sup>.', '4 &times; 0.0651 / 0.0004 = 651.')

K.calc('e', 'After a code change, the steps that ran again took 20.2 s with the bad order and 1.7 s with the good order. How many times faster is the good order?', '11.9', 'Divide.', ['Bad: 20.2 s.', 'Good: 1.7 s.', eq('20.2 / 1.7 = 11.9')], check=11.9, tol=0.05)
K.calc('e', 'Test accuracy is 0.9111 on 45 test flowers. How many were predicted correctly?', '41', 'Accuracy times rows.', ['Correct = accuracy &times; rows.', '0.9111 &times; 45 = 41.0.', eq('41 correct, 4 wrong')], check=41)
K.calc('e', 'A team pushes 20 times a day and each CI run takes 7 minutes. CI minutes per day?', '140', 'Runs times minutes.', ['20 runs.', '7 minutes each.', eq('20 &times; 7 = 140 minutes')], check=140)
K.calc('m', 'A lint job (1 min) and a test job (3 min) run side by side, and an image job (4 min) needs both. Minutes until the image is ready?', '7', 'Longest parallel job, then the next.', ['Parallel jobs end when the slower one ends: max(1, 3) = 3.', 'Then the image job runs.', eq('3 + 4 = 7 minutes')], check=7)
K.calc('m', 'A monthly budget of 3000 CI minutes and 7 minute runs. Full runs that fit?', '428', 'Divide and round down.', ['3000 / 7 = 428.57.', 'Only whole runs count.', eq('428 runs')], check=428)
K.calc('m', 'The gate needs accuracy of at least 0.90 on 45 test rows. Most wrong predictions allowed?', '4', 'Allowed error times rows, rounded down.', ['Allowed error: 1 &minus; 0.90 = 0.10.', '0.10 &times; 45 = 4.5.', eq('At most 4 wrong (5 wrong gives 0.889)')], check=4)
K.calc('m', 'Each server downloads 129 MB of compressed layers. MB pulled by 10 new servers?', '1290', 'Size times servers.', ['129 MB each.', '10 servers.', eq('129 &times; 10 = 1290 MB')], check=1290)
K.calc('h', 'Ten independent tests each fail at random 2 percent of the time. Chance a run is fully green?', '0.8171', '(1 &minus; p)<sup>n</sup>.', ['Each passes with 0.98.', 'All ten must pass.', eq('0.98<sup>10</sup> = 0.8171')], check=0.8171, tol=0.0005)
K.calc('h', 'Accuracy 0.9111 on 45 test rows. Standard error of that accuracy?', '0.0424', '&radic;(p(1 &minus; p) / n).', ['p(1 &minus; p) = 0.9111 &times; 0.0889 = 0.0810.', '0.0810 / 45 = 0.0018.', eq('&radic;0.0018 = 0.0424')], check=0.0424, tol=0.0005)
K.calc('x', 'In the style of an A/B testing exam: to see a 2 point error gap (0.02) at two standard errors when the error is about 0.07, use n = 4p(1 &minus; p) / d<sup>2</sup>. Requests needed?', '651', 'Plug in p = 0.07 and d = 0.02.', ['p(1 &minus; p) = 0.07 &times; 0.93 = 0.0651.', '4 &times; 0.0651 = 0.2604, and d<sup>2</sup> = 0.0004.', eq('0.2604 / 0.0004 = 651')], check=651)

K.assign('next_version', 'e', 'Bump a model version',
         '<p>Model images are tagged with versions like <code>1.4.2</code> (major.minor.patch). Write <code>next_version(version, change)</code> where change is <code>\'major\'</code>, <code>\'minor\'</code> or <code>\'patch\'</code>. A bump sets the parts to its right to 0.</p>',
         """
def next_version(version, change):
    # your code here
    pass
""", [("next_version('1.4.2', 'patch')", '1.4.3'), ("next_version('1.4.2', 'minor')", '1.5.0'), ("next_version('1.4.2', 'major')", '2.0.0'), ("next_version('0.9.9', 'patch')", '0.9.10')],
         """
def next_version(version, change):
    major, minor, patch = (int(p) for p in version.split('.'))
    if change == 'major':
        return f'{major + 1}.0.0'
    if change == 'minor':
        return f'{major}.{minor + 1}.0'
    return f'{major}.{minor}.{patch + 1}'
""", 'Split on dots, turn the parts into numbers, add one to the chosen part and reset the parts after it.', '<p>Compare the parts as numbers, not text: 0.9.10 comes after 0.9.9.</p>')
K.assign('passes_gate', 'e', 'A quality gate',
         '<p>Write <code>passes_gate(y_true, y_pred, gate=0.9)</code> that returns True when the share of matching labels is at least <code>gate</code>.</p>',
         """
def passes_gate(y_true, y_pred, gate=0.9):
    # your code here
    pass
""", [('passes_gate([0, 1, 2, 2], [0, 1, 2, 1], 0.75)', True), ('passes_gate([0, 1, 2, 2], [0, 1, 2, 1], 0.8)', False), ('passes_gate([1] * 10, [1] * 9 + [0])', True), ('passes_gate([0, 0], [1, 1])', False)],
         """
def passes_gate(y_true, y_pred, gate=0.9):
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return correct / len(y_true) >= gate
""", 'Count the matches, divide by the number of labels and compare with the gate.', '<p>In CI this is one assert, and a failing assert blocks the merge.</p>')
K.assign('rebuilt_steps', 'm', 'Which Docker layers rebuild?',
         '<p>Each Dockerfile step is given as the list of files it copies (empty for steps that copy nothing). Write <code>rebuilt_steps(steps, changed)</code> that returns the indices of the steps that run again. A step runs again if it copies a changed file or any earlier step ran again.</p>',
         """
def rebuilt_steps(steps, changed):
    # your code here
    pass
""", [("rebuilt_steps([[], [], ['requirements.txt'], [], ['app.py'], []], ['app.py'])", [4, 5]), ("rebuilt_steps([[], [], ['requirements.txt'], [], ['app.py'], []], ['requirements.txt'])", [2, 3, 4, 5]), ("rebuilt_steps([[], ['.'], []], [])", []), ("rebuilt_steps([['a', 'b'], []], ['b'])", [0, 1])],
         """
def rebuilt_steps(steps, changed):
    out, again = [], False
    for i, files in enumerate(steps):
        if any(f in changed for f in files):
            again = True
        if again:
            out.append(i)
    return out
""", 'Walk the steps in order with a flag that turns on at the first step that copies a changed file and stays on.', '<p>This is why the slow, rarely changing steps belong near the top of the Dockerfile.</p>')

K.must('Image and container', 'Image = OS layer, Python, packages, code, model. Container = running copy. Registry stores images. -p host:container.')
K.must('Dockerfile order', 'Base, requirements, pip install, then code. Code change: 2.2 s instead of 32 s. Non root USER, HEALTHCHECK, CMD.')
K.must('Per system', 'Docker Desktop on macOS and Windows (WSL 2), Engine plus docker group on Linux, Engine in the Linux environment on ChromeOS. Apple silicon: --platform linux/amd64.')
K.must('Model tests', 'Quality gate, known examples, invariance, directional, latency. A constant model passes invariance, so use several kinds.')
K.must('CI/CD', 'GitHub Actions: install, train, pytest, build, smoke test, push on main. First failure stops. Tag images by commit, secrets never in files.')
K.must('Numbers', 'Flaky suite (1 &minus; p)<sup>n</sup>. Accuracy SE &radic;(p(1 &minus; p)/n). Canary n = 4p(1 &minus; p)/d<sup>2</sup>.')

T = K.topic(
    slug='mlops-docker', topic='mlops-docker', step=(2, 'Build and ship', 'mlops-s2', 'Package a model as one pipeline, serve it as a web API with Flask, FastAPI and Django, put it in a Docker container and ship it with CI/CD.', 'Intermediate'),
    title='Docker and CI/CD for models', short='Docker and CI/CD', badge='2.3', minutes=60,
    lead='Package the model API in a Docker image that runs the same on macOS, Windows, Linux and ChromeOS, test the model itself with a quality gate and behaviour tests, and run everything in GitHub Actions on every push.',
    desc='Docker, image, container, Dockerfile, layer cache, registry, port mapping, non root user, HEALTHCHECK, Docker Compose, Docker Desktop, WSL 2, Apple silicon, buildx, model testing, quality gate, invariance, directional tests, pytest, CI/CD, GitHub Actions, smoke test, GHCR, canary, rollback.',
    summary='A real Dockerfile and Compose file for a model API, per OS build steps, model behaviour tests and a GitHub Actions pipeline.',
    keywords=['Docker', 'Dockerfile', 'container', 'docker compose', 'CI/CD', 'GitHub Actions', 'model testing', 'quality gate', 'smoke test', 'container registry'],
    recap='<p>Seal the model, its code and its packages in one image, guard it with tests that check the model and not just the code, and let a pipeline build, test and ship every change the same way.</p>',
    added='2026-11-14', leet=leet_items())
