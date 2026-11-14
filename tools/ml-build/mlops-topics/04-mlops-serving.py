# MLOps 2.2: serving models with Flask, FastAPI and Django. Checked against the Flask documentation (Quickstart,
# Testing Flask Applications, Deploying to Production), the FastAPI documentation (Request Body, Testing, Deployment
# concepts, Server Workers), the Django documentation (settings.configure, the test client, How to deploy with WSGI),
# the Gunicorn, Waitress and Uvicorn docs, RFC 9110 (HTTP semantics and status codes), Chip Huyen, Designing Machine
# Learning Systems (2022) chapter 7 (batch prediction against online prediction), and Little's law (Little, 1961).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, term, leet_items
from mlkit import link, ossteps

chapter('mlops-serving')
K = Kit()
K.code('flask_serve', r'''
# Serve a model with Flask (pip install flask scikit-learn).
#   python flask_serve.py         tries the API in this process with Flask's test client
#   python flask_serve.py serve   starts the server on http://127.0.0.1:8000, call it with curl (see the lesson)
import sys

from flask import Flask, jsonify, request
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# In a real service: model = joblib.load('models/iris.joblib'), done once when the app starts
X, y = load_iris(return_X_y=True)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X, y)
CLASSES = ['setosa', 'versicolor', 'virginica']

app = Flask(__name__)


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/predict')
def predict():
    body = request.get_json(silent=True) or {}
    features = body.get('features')
    if not isinstance(features, list) or len(features) != 4 or not all(isinstance(v, (int, float)) for v in features):
        return jsonify(error='send {"features": [four numbers]}'), 422
    probs = model.predict_proba([features])[0]
    best = int(probs.argmax())
    return {'class': CLASSES[best], 'probability': round(float(probs[best]), 3)}


if __name__ == '__main__':
    if 'serve' in sys.argv:
        app.run(port=8000)                 # development server only, see the lesson for production
    else:                                  # try the API with Flask's test client, no network needed
        client = app.test_client()
        print('GET  /health  ', client.get('/health').get_json())
        r = client.post('/predict', json={'features': [5.9, 3.0, 5.1, 1.8]})
        print('POST /predict ', r.status_code, r.get_json())
        r = client.post('/predict', json={'features': [5.9, 'wide']})
        print('POST /predict ', r.status_code, r.get_json())
''', long=True)

K.code('fastapi_serve', r'''
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
''', long=True)

K.code('django_serve', r'''
# Serve a model with Django, in one file (pip install django scikit-learn).
#   python django_serve.py                  tries the API in this process with Django's test client
#   python django_serve.py runserver 8000   starts the development server on http://127.0.0.1:8000
# A real project keeps the same pieces in settings.py, urls.py and views.py (django-admin startproject).
import json
import sys

import django
from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

settings.configure(DEBUG=False, ALLOWED_HOSTS=['127.0.0.1', 'localhost', 'testserver'], ROOT_URLCONF=__name__,
                   SECRET_KEY='change-me-in-production', MIDDLEWARE=['django.middleware.common.CommonMiddleware'])
django.setup()

from sklearn.datasets import load_iris                     # noqa: E402
from sklearn.linear_model import LogisticRegression        # noqa: E402
from sklearn.pipeline import make_pipeline                 # noqa: E402
from sklearn.preprocessing import StandardScaler           # noqa: E402

X, y = load_iris(return_X_y=True)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X, y)
CLASSES = ['setosa', 'versicolor', 'virginica']


def health(request):
    return JsonResponse({'status': 'ok'})


@csrf_exempt                     # an API called by programs, not a form in a browser
@require_POST
def predict(request):
    try:
        features = json.loads(request.body)['features']
        assert isinstance(features, list) and len(features) == 4
        row = [[float(v) for v in features]]
    except (ValueError, KeyError, TypeError, AssertionError):
        return JsonResponse({'error': 'send {"features": [four numbers]}'}, status=422)
    probs = model.predict_proba(row)[0]
    best = int(probs.argmax())
    return JsonResponse({'class': CLASSES[best], 'probability': round(float(probs[best]), 3)})


urlpatterns = [path('health', health), path('predict', predict)]

from django.core.wsgi import get_wsgi_application   # noqa: E402
application = get_wsgi_application()                 # for production servers: gunicorn django_serve:application

if __name__ == '__main__':
    if len(sys.argv) > 1:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
    else:
        from django.test import Client
        client = Client()
        print('GET  /health ', client.get('/health').json())
        r = client.post('/predict', data=json.dumps({'features': [5.9, 3.0, 5.1, 1.8]}), content_type='application/json')
        print('POST /predict', r.status_code, r.json())
        r = client.post('/predict', data='not json', content_type='application/json')
        print('POST /predict', r.status_code, r.json())
        print('GET  /predict', client.get('/predict').status_code, '(only POST is allowed)')
''', long=True)

K.code('batch_predict', r'''
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
''', long=True)

WHY_SERVE = 'It needs Flask, FastAPI or Django, which the browser version of Python cannot install or run as a web server.'

BODY = '{"features": [5.9, 3.0, 5.1, 1.8]}'
CURL = f"curl -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{BODY}'"

CALL_MAC = ('<ol><li>Open <b>Terminal</b>, go to your project folder and activate its environment (MLOps 1.1).</li>'
            '<li>Install the packages and start the Flask server. It keeps running and prints each request it receives.</li>'
            '<li>Open a <b>second</b> Terminal window (Command and N) and call the API with curl, which macOS already has.</li>'
            '<li>Stop the server with Control and C in the first window.</li></ol>'
            + term(['cd ml-project && source .venv/bin/activate', 'pip install flask scikit-learn', 'python flask_serve.py serve        # Running on http://127.0.0.1:8000'], 'Terminal 1 (macOS)')
            + term(['curl http://127.0.0.1:8000/health', CURL], 'Terminal 2 (macOS)')
            + '<p>The examples use port 8000 on purpose. On macOS 12 and later the <b>AirPlay Receiver</b> already listens on port 5000, the old Flask default, and answers 403 Forbidden. If you ever need port 5000, turn AirPlay Receiver off in System Settings, General, AirDrop and Handoff. To see what holds a port, run <code>lsof -i :8000</code>.</p>')
CALL_WIN = ('<ol><li>Open <b>PowerShell</b>, go to your project folder and activate its environment (MLOps 1.1).</li>'
            '<li>Install the packages and start the server. If Windows Defender Firewall asks about Python, allow it on <b>private</b> networks only. The server listens on 127.0.0.1, so nothing outside your computer can reach it.</li>'
            '<li>Open a <b>second</b> PowerShell window and call the API. <code>Invoke-RestMethod</code> is built in and turns the JSON answer into an object.</li>'
            '<li>Stop the server with Control and C.</li></ol>'
            + term(['cd ml-project', '.venv\\Scripts\\Activate.ps1', 'pip install flask scikit-learn', 'python flask_serve.py serve'], 'PowerShell 1 (Windows)')
            + term(['Invoke-RestMethod http://127.0.0.1:8000/health',
                    f"Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -ContentType 'application/json' -Body '{BODY}'", '',
                    '# curl also ships with Windows 10 and 11. Type curl.exe, because in Windows PowerShell 5.1',
                    '# the word curl is a different command (an alias of Invoke-WebRequest).',
                    'curl.exe http://127.0.0.1:8000/health'], 'PowerShell 2 (Windows)')
            + '<p>To see what holds a port, run <code>netstat -ano | findstr :8000</code>. The last column is the process id, which Task Manager shows on its Details tab.</p>')
CALL_LINUX = ('<p>The same steps as macOS. Most distributions include curl. If not, install it with <code>sudo apt install curl</code> (Ubuntu, Debian) or <code>sudo dnf install curl</code> (Fedora).</p>'
              + term(['cd ml-project && source .venv/bin/activate', 'pip install flask scikit-learn', 'python flask_serve.py serve'], 'Terminal 1 (Linux)')
              + term(['curl http://127.0.0.1:8000/health', CURL, '', '# what holds port 8000', 'ss -ltnp | grep 8000'], 'Terminal 2 (Linux)'))
CALL_CHROME = ('<p>Run both terminals inside the Linux development environment (open the <b>Terminal</b> app, then the penguin tab, and press Control, Shift and T for a second tab). The commands are the Debian ones.</p>'
               + term(['sudo apt install curl                 # once, if curl is missing', 'cd ml-project && source .venv/bin/activate', 'pip install flask scikit-learn', 'python flask_serve.py serve'], 'Terminal tab 1 (ChromeOS Linux)')
               + term(['curl http://127.0.0.1:8000/health', CURL], 'Terminal tab 2 (ChromeOS Linux)')
               + '<p>ChromeOS forwards localhost ports from Linux to the Chrome browser, so <code>http://localhost:8000/health</code> opens in a normal Chrome tab. The Port forwarding page in the Linux development environment settings (search Settings for Port forwarding) is only needed when another device on your network should reach the server.</p>')

PROD_MAC = ('<p>Gunicorn runs Flask and Django with several worker processes. Uvicorn runs FastAPI and has its own <code>--workers</code> option. Both work on macOS and Linux.</p>'
            + term(['pip install gunicorn "uvicorn[standard]"', '',
                    'gunicorn -w 2 -b 127.0.0.1:8000 flask_serve:app            # Flask: file flask_serve.py, object app',
                    'gunicorn -w 2 -b 127.0.0.1:8000 django_serve:application   # Django: the WSGI application object',
                    'uvicorn fastapi_serve:app --host 127.0.0.1 --port 8000 --workers 2   # FastAPI'], 'Terminal (macOS)'))
PROD_WIN = ('<p><b>Gunicorn does not run on Windows</b>, because it depends on Unix process features. Use <b>Waitress</b>, a pure Python production server, for Flask and Django. Uvicorn works on Windows as it is. A second choice is to run the Linux commands inside WSL (MLOps 1.1), or inside Docker (MLOps 2.3).</p>'
            + term(['pip install waitress "uvicorn[standard]"', '',
                    'waitress-serve --listen=127.0.0.1:8000 flask_serve:app            # Flask',
                    'waitress-serve --listen=127.0.0.1:8000 django_serve:application   # Django',
                    'uvicorn fastapi_serve:app --host 127.0.0.1 --port 8000 --workers 2   # FastAPI'], 'PowerShell (Windows)')
            + '<p>Waitress uses threads instead of processes (4 by default, change it with <code>--threads=8</code>).</p>')
PROD_LINUX = ('<p>The same commands as macOS. On a Linux server, a <b>systemd</b> service keeps the command running and restarts it after a crash or a reboot. MLOps 2.3 shows the more common choice today, a Docker container.</p>'
              + term(['pip install gunicorn "uvicorn[standard]"', '',
                      'gunicorn -w 2 -b 127.0.0.1:8000 flask_serve:app',
                      'gunicorn -w 2 -b 127.0.0.1:8000 django_serve:application',
                      'uvicorn fastapi_serve:app --host 127.0.0.1 --port 8000 --workers 2'], 'Terminal (Linux)'))
PROD_CHROME = ('<p>Use the Linux commands inside the Linux development environment. A Chromebook is fine for learning and testing, but a real service runs on a server or in the cloud, usually in a Docker container (MLOps 2.3).</p>'
               + term(['pip install gunicorn "uvicorn[standard]"', 'gunicorn -w 2 -b 127.0.0.1:8000 flask_serve:app'], 'Terminal (ChromeOS Linux)'))

K.lesson('api', 'A model behind a web API', f'''
{src('Flask documentation (Quickstart and Testing), RFC 9110 HTTP Semantics (methods and status codes), and Chip Huyen, Designing Machine Learning Systems (2022) chapter 7.')}
{viz('mlrequest')}
{wwh('A <b>model API</b> is a small web service. A client sends an HTTP <b>request</b> with JSON, the service checks it, runs the saved pipeline and sends back a JSON <b>response</b> with a <b>status code</b>. A <b>route</b> such as <code>POST /predict</code> connects a URL and a method to one Python function.',
     'A model inside a notebook helps one person. Behind an API, any website, phone app or other service can use it in any programming language, and you can update the model without touching those clients.',
     'Load the pipeline once when the server starts. Add a <code>/health</code> route that says the service is alive, and a <code>/predict</code> route that validates the input, predicts and returns JSON. Test it in the same process with the framework&rsquo;s <b>test client</b> before starting a real server.')}
{table(['Status', 'Meaning', 'When a model API sends it'], [
    ['200 OK', 'Success', 'The prediction is in the body'],
    ['400 Bad Request', 'The request itself is broken', 'The body is not valid JSON at all'],
    ['405 Method Not Allowed', 'Wrong method for this route', 'GET sent to a POST only route'],
    ['422 Unprocessable Content', 'Valid JSON but the content fails the checks', 'A word instead of a number, a missing field'],
    ['500 Internal Server Error', 'A bug or crash inside the service', 'Never on purpose. Log it and fix it.']])}
{local('flask_serve', WHY_SERVE)}
{note('The test client sends real requests to the app inside one Python process, so no port or network is needed. The good request gets 200 with virginica at 0.703. The broken one gets 422 and an error that tells the caller what to send. The model never sees bad data.', 'tip')}
{ossteps('Start the server and call it from a second terminal', CALL_MAC, CALL_WIN, CALL_LINUX, CALL_CHROME)}
{fxs(fx('Latency', 'time from request sent to response received', 'Report the median and the 95th or 99th percentile, not only the average.', key=True),
     fx('Throughput of one worker', 'requests per second = 1000 / latency in ms', 'A worker that needs 20 ms serves at most 50 requests per second.', key=True))}
{link('python', 'New to Flask, Django or web APIs?', 'The Complete Python subject teaches Flask, Django and building REST APIs step by step, from routes and templates to JSON and testing.', 'Open Complete Python')}
''', kw=['model API', 'HTTP', 'JSON', 'route', 'status code', '422', 'Flask', 'test client', 'curl', 'Invoke-RestMethod', 'port'])

K.lesson('fastapi', 'FastAPI: the input contract written as a class', f'''
{src('FastAPI documentation: Request Body, Testing, and the automatic interactive docs. Pydantic documentation: Fields and validation errors.')}
{wwh('<b>FastAPI</b> is a web framework built on type hints. You describe the input as a <b>Pydantic</b> class, for example four floats that must be above 0 and below 20, and FastAPI checks every request against it, converts the types, and writes the error messages for you. It also builds interactive documentation at <code>/docs</code>.',
     'The input contract from MLOps 2.1 becomes a few lines instead of a page of if statements. The documentation always matches the code, because it is generated from the same class. FastAPI also supports async code for services that wait on databases or other APIs.',
     'Write one class for the input and one for the output, and use them as the type of the function argument and as <code>response_model</code>. Accept a list for a batch route so many rows go through the model in one call. Run it with Uvicorn.')}
{local('fastapi_serve', WHY_SERVE)}
{note('One bad request produced three precise errors at once: sepal_length must be greater than 0, sepal_width is not a number, and petal_width is missing. The batch route scored two flowers in a single predict_proba call, virginica at 0.703 and setosa at 0.981.', 'exam')}
{term(['pip install "fastapi[standard]" scikit-learn', 'uvicorn fastapi_serve:app --port 8000', '# then open http://127.0.0.1:8000/docs in the browser and press Try it out'], 'Terminal (macOS, Linux, ChromeOS and PowerShell on Windows)')}
<p>The JSON body for FastAPI uses named fields: <code>{{"sepal_length": 5.9, "sepal_width": 3.0, "petal_length": 5.1, "petal_width": 1.8}}</code>. The same curl and Invoke-RestMethod commands from the Flask lesson work with this body.</p>
{deep('Sync or async route functions', '<p>A plain <code>def</code> route runs in a thread pool, which suits scikit-learn because predict is ordinary CPU work. An <code>async def</code> route runs on the event loop, so a slow predict inside it blocks every other request on that worker. Use <code>async def</code> only when the function awaits network or database calls, and keep heavy CPU work in plain <code>def</code> routes or in separate worker processes.</p>')}
''', kw=['FastAPI', 'Pydantic', 'BaseModel', 'Field', 'response_model', '/docs', 'TestClient', 'batch route', 'async'])

K.lesson('django', 'Django: when the model joins a full web application', f'''
{src('Django documentation: Using settings without DJANGO_SETTINGS_MODULE (settings.configure), the test client, CSRF protection, and How to deploy with WSGI.')}
{wwh('<b>Django</b> is a full web framework with a database layer, an admin site, user accounts, forms and security features. A JSON view returns a <code>JsonResponse</code>. The program here fits a whole Django service in one file by calling <code>settings.configure</code> instead of creating a project with many files.',
     'Choose Django when the model is one feature of a larger site that already needs logins, a database and an admin, for example a clinic portal that shows a risk score next to each patient. For a model that only answers predictions, Flask or FastAPI is smaller.',
     'Write a view that reads <code>request.body</code>, validates it, predicts and returns JsonResponse. Mark it <code>@require_POST</code> so other methods get 405. Mark it <code>@csrf_exempt</code> only because programs, not browser forms, call it, and protect it with an API key or token instead.')}
{local('django_serve', WHY_SERVE)}
{note('Django gives the same answers as Flask (200 with virginica at 0.703, 422 for bad JSON), and @require_POST turns a GET into 405 without running the view. In a real project the view lives in an app inside <code>django-admin startproject</code>, and the settings come from environment variables, never a SECRET_KEY written in the code.', 'warn')}
{term(['pip install django scikit-learn', 'python django_serve.py runserver 8000      # development server only'], 'Terminal (every system, use PowerShell on Windows)')}
''', kw=['Django', 'JsonResponse', 'settings.configure', 'require_POST', 'csrf_exempt', 'WSGI', 'runserver'])

K.lesson('modes', 'Online against batch prediction', f'''
{src('Chip Huyen, Designing Machine Learning Systems (2022) chapter 7, Model deployment and prediction service, and the pandas documentation for read_csv with chunksize.')}
{viz('mlservemodes')}
{wwh('<b>Online</b> (real time) prediction answers each request the moment it arrives, through an API like the ones above. <b>Batch</b> prediction runs on a schedule, scores a whole table at once and stores the answers for the application to look up later.',
     'Online gives fresh answers during the user&rsquo;s visit but needs a server running all the time and fast features. Batch is cheaper and simpler, and one predict call on many rows is far faster than many calls on one row each, but the answers are only as fresh as the last run.',
     'Ask how soon the answer is needed. During the visit (fraud checks, search ranking) means online. By tomorrow (churn lists, weekly demand forecasts, email campaigns) means batch. Read big files in chunks so memory stays small.')}
{run('batch_predict')}
{note('20,000 rows are scored in 4 chunks of 5,000. The last line times both styles on your own device, so the numbers change from run to run, but one call per row is always many times slower because each call pays the same fixed overhead.', 'tip')}
{scene('A bank fraud check and a churn list', '<p>A card payment must be approved or stopped within about 100 ms, so the fraud model runs online behind an API. The same bank also wants a list of customers likely to close their accounts. Nobody needs that list within 100 ms, so a batch job scores every customer at 2 am and writes the result to a table that the retention team reads in the morning.</p>')}
''', kw=['online prediction', 'batch prediction', 'real time', 'chunksize', 'latency', 'freshness'])

K.lesson('production', 'From the development server to production', f'''
{src('Flask documentation, Deploying to Production. FastAPI documentation, Deployment concepts and Server Workers. Gunicorn, Waitress and Uvicorn documentation. Little, A proof for the queuing formula L = &lambda;W (1961).')}
{wwh('<code>app.run()</code> and <code>runserver</code> are <b>development servers</b>: one process, made for debugging, and the docs say not to use them in production. A <b>production server</b> (Gunicorn or Waitress for Flask and Django, which speak WSGI, and Uvicorn for FastAPI, which speaks ASGI) runs several <b>workers</b> and restarts any that crash.',
     'One development server handles requests slowly and stops at the first crash. Workers serve requests in parallel, and a reverse proxy in front adds HTTPS, timeouts and limits on request size.',
     'Pick the server for your system below. Start with 2 workers per CPU core as a first guess, then measure. Each worker loads its own copy of the model, so memory grows with the number of workers.')}
{ossteps('Run a production server', PROD_MAC, PROD_WIN, PROD_LINUX, PROD_CHROME)}
{steps('A checklist before real users call the API', [
    'Load the model once at start up and keep it in memory.',
    'Keep a /health route for the load balancer, and return the model version in each response.',
    'Validate every input and cap the request size.',
    'Require an API key or token, and rate limit each caller.',
    'Put HTTPS in front with a reverse proxy such as nginx or Caddy, or the cloud&rsquo;s load balancer.',
    'Log each request with its latency and status code, without personal data.',
    'Set a timeout so one slow request cannot hold a worker forever.'])}
{fxs(fx('Little&rsquo;s law', 'L = &lambda; &times; W', 'L requests in progress, &lambda; arrivals per second, W seconds each request spends in the system.', key=True),
     fx('Workers needed', 'workers = &lambda; &times; latency / target use', 'Aim for about 70 to 80 percent use so short bursts do not build a queue.', key=True),
     fx('Waiting time for one worker (M/M/1 queue)', 'W = 1 / (&mu; &minus; &lambda;)', '&mu; requests per second the worker can serve. W shoots up as &lambda; nears &mu;.'))}
{note('A queue does not grow in a straight line. One worker that can serve 50 requests per second answers in 25 ms at 10 per second, 100 ms at 40 per second, and 1 full second at 49 per second. That is why services keep spare capacity.', 'exam')}
''', kw=['development server', 'production server', 'Gunicorn', 'Waitress', 'Uvicorn', 'WSGI', 'ASGI', 'workers', 'reverse proxy', 'HTTPS', "Little's law", 'rate limit'])

K.lesson('versus', 'Flask, FastAPI, Django and model servers compared', f'''
{versus('Ways to serve a model', ['', 'Flask', 'FastAPI', 'Django', 'Model servers (BentoML, TorchServe, KServe)'], [
    ['Size', 'Small and simple', 'Small, typed', 'Large, everything included', 'A platform'],
    ['Input checks', 'Write them yourself', 'Automatic from Pydantic classes', 'Forms or Django REST framework serializers', 'Built in per model'],
    ['API docs', 'Add a package', 'Automatic at /docs', 'Add a package', 'Usually automatic'],
    ['Production server', 'Gunicorn, Waitress', 'Uvicorn', 'Gunicorn, Waitress', 'Included'],
    ['Extras', 'Many plugins', 'Async, dependency injection', 'Database, admin, users', 'Batching requests, GPUs, scaling, model versions'],
    ['Best for', 'Learning, small services', 'New model APIs', 'A model inside a larger web app', 'Many models or heavy deep learning traffic']],
    'Start with FastAPI for a new model API, use Django when the model joins an existing Django site, and move to a model server when you run many models or need GPUs and request batching.')}
''', kw=['Flask vs FastAPI', 'Django', 'BentoML', 'TorchServe', 'KServe', 'model server'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Put the model in a small program that waits for questions over the internet and answers each one with a prediction.</p>',
    '<p>Build /health and /predict routes in Flask, FastAPI or Django, validate inputs, return the right status codes, and test with the test client.</p>',
    '<p>Run production servers with workers, size them with Little&rsquo;s law, choose online or batch prediction, and secure the API with keys, rate limits and HTTPS.</p>',
    '<p>Design serving systems with dynamic request batching, model servers on GPUs, canary releases, tail latency targets and autoscaling from queue length.</p>')}
{grow('Serve a model and call it with curl.',
      'Ship a validated API on a production server.',
      'Plan capacity and latency for real traffic.')}
''', kw=['beginner', 'expert', 'capacity planning', 'tail latency'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>model API</b> loads the saved pipeline once and answers <code>POST /predict</code> with JSON and a status code: 200 for success, 422 for bad content, 405 for the wrong method.',
    '<b>Flask</b> is small and simple. <b>FastAPI</b> checks inputs from Pydantic classes and writes docs at /docs. <b>Django</b> fits when the model joins a full web app.',
    'Test with the framework&rsquo;s test client, then call the running server with curl, or with Invoke-RestMethod in Windows PowerShell.',
    '<b>Online</b> prediction answers during the visit. <b>Batch</b> prediction scores everything on a schedule, cheaper but less fresh.',
    'Production uses Gunicorn (macOS, Linux), Waitress (Windows, any system) or Uvicorn (FastAPI, any system) with several workers, sized with <b>Little&rsquo;s law</b>.'],
    'MLOps 2.3 puts this service in a Docker container and tests and ships it with CI/CD.')}
{files('Three tasks: validate a request body, size a pool of workers, and split a big file into chunks.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'POST /predict in a model API is', ['A database table', 'A route: a method and a URL connected to one function', 'A model type', 'A file format'], 1, 'Method plus path.', 'The framework calls the matching function.')
K.quiz('e', 'A request with a word where a number belongs should get status', ['200', '422', '500', '301'], 1, 'Unprocessable content.', 'The client must fix the input.')
K.quiz('e', 'The /health route is used to', ['Train the model', 'Tell a load balancer or monitor that the service is alive', 'Delete old models', 'Show charts'], 1, 'Alive check.', 'It should be fast and simple.')
K.quiz('e', 'Where should a model API load the saved pipeline?', ['On every request', 'Once, when the server starts', 'Never', 'In the browser'], 1, 'Load once.', 'Reading the file each time wastes time.')
K.quiz('m', 'FastAPI checks request bodies automatically because', ['It guesses', 'The input is described as a Pydantic class with types and limits', 'Uvicorn checks them', 'JSON is always valid'], 1, 'Type hints.', 'Errors name each bad field.')
K.quiz('m', 'Gunicorn on Windows', ['Works the same', 'Does not run, so use Waitress, WSL or Docker', 'Needs a GPU', 'Is built in'], 1, 'Unix only.', 'Waitress is pure Python.')
K.quiz('m', 'A GET request to a route marked @require_POST in Django gets', ['200', '405 Method Not Allowed', '404', '422'], 1, 'Wrong method.', 'The view does not run.')
K.quiz('m', 'A weekly email campaign that targets customers likely to churn should use', ['Online prediction', 'Batch prediction', 'No model', 'A GPU server'], 1, 'Nobody waits for it.', 'Score everyone on a schedule.')
K.quiz('m', 'On macOS 12 and later, a Flask server on port 5000 may answer 403 because', ['Flask is broken', 'AirPlay Receiver already uses port 5000', 'macOS blocks Python', 'curl is missing'], 1, 'Port taken.', 'Use port 8000 or turn AirPlay Receiver off.')
K.quiz('h', 'In Windows PowerShell 5.1, typing curl runs', ['curl.exe', 'An alias of Invoke-WebRequest', 'Nothing', 'Python'], 1, 'An alias.', 'Type curl.exe or use Invoke-RestMethod.')
K.quiz('h', 'A scikit-learn predict inside an async def FastAPI route', ['Is faster', 'Blocks the event loop, delaying every other request on that worker', 'Runs on a GPU', 'Is not allowed'], 1, 'CPU work blocks.', 'Use a plain def route.')
K.quiz('h', 'Why is one predict call on 5000 rows faster than 5000 calls on one row?', ['Bigger rows', 'Each call pays a fixed overhead, and vectorised maths handles many rows at once', 'It skips rows', 'Caching the answers'], 1, 'Fixed cost per call.', 'This is why batch routes exist.')
K.quiz('x', 'In the style of a systems design interview: one worker serves 50 requests per second and traffic rises from 40 to 49 per second. Mean time in the system', ['Rises a little', 'Rises from 0.1 s to 1 s', 'Falls', 'Stays the same'], 1, 'W = 1 / (&mu; &minus; &lambda;).', '1/10 then 1/1.')
K.quiz('x', 'In the style of a Google ML engineering exam: a model must answer in 50 ms for 2000 requests per second with a 30 ms model. The first fix to consider is', ['A bigger model', 'More workers or replicas sized with Little&rsquo;s law, plus request batching on the server', 'Batch prediction at night', 'Removing validation'], 1, 'Capacity, not accuracy.', '2000 &times; 0.03 = 60 busy workers at full use.')

K.calc('e', 'A model needs 20 ms per request on one worker. Most requests per second that worker can serve?', '50', '1000 / latency in ms.', ['One second is 1000 ms.', 'Each request takes 20 ms.', eq('1000 / 20 = 50 requests per second')], check=50)
K.calc('e', 'Four such workers run side by side. Most requests per second in total?', '200', 'Workers times rate.', ['One worker: 50 per second.', 'Workers run in parallel.', eq('4 &times; 50 = 200 requests per second')], check=200)
K.calc('e', '1200 requests arrive and 30 are rejected with 422. Percent of requests that reached the model?', '97.5', 'Valid over total.', ['Valid: 1200 &minus; 30 = 1170.', 'Divide by 1200.', eq('1170 / 1200 &times; 100 = 97.5 percent')], check=97.5)
K.calc('m', '150 requests per second arrive and each spends 0.04 s in the service. Average requests in progress (Little&rsquo;s law)?', '6', 'L = &lambda; &times; W.', ['&lambda; = 150 per second.', 'W = 0.04 s.', eq('L = 150 &times; 0.04 = 6')], check=6)
K.calc('m', '300 requests per second at 25 ms each, with workers kept at 75 percent use. Workers needed?', '10', 'Busy workers over target use.', ['Busy workers: 300 &times; 0.025 = 7.5.', 'Keep 25 percent spare.', eq('7.5 / 0.75 = 10 workers')], check=10)
K.calc('m', 'A nightly batch job runs at 2:00. An event at 8:30 the day before waits how many hours for its answer?', '17.5', 'Count to midnight, then add.', ['8:30 to 24:00 is 15.5 hours.', 'Midnight to 2:00 is 2 hours.', eq('15.5 + 2 = 17.5 hours')], check=17.5)
K.calc('m', 'A page has a 200 ms budget. The network takes 60 ms and fetching features takes 70 ms. Milliseconds left for the model?', '70', 'Subtract each part.', ['200 &minus; 60 = 140.', 'Then subtract the features.', eq('140 &minus; 70 = 70 ms')], check=70)
K.calc('h', 'A model outputs the scores 2.0, 1.0 and 0.1 for three classes. Softmax probability of the first class?', '0.659', 'e<sup>z</sup> over the sum.', ['e<sup>2</sup> = 7.389, e<sup>1</sup> = 2.718, e<sup>0.1</sup> = 1.105.', 'Sum: 11.212.', eq('7.389 / 11.212 = 0.659')], check=0.659, tol=0.0005)
K.calc('h', 'An always on server costs 0.10 dollars per hour. A batch job runs 15 minutes each night on a 0.40 dollar per hour machine. How many times more does the server cost over 30 days?', '24', 'Monthly cost of each.', ['Server: 0.10 &times; 24 &times; 30 = 72 dollars.', 'Batch: 0.40 &times; 0.25 &times; 30 = 3 dollars.', eq('72 / 3 = 24 times')], check=24)
K.calc('x', 'In the style of a queueing exam: one worker serves &mu; = 50 requests per second and &lambda; = 40 arrive per second. Mean time in the system in ms (M/M/1)?', '100', 'W = 1 / (&mu; &minus; &lambda;).', ['&mu; &minus; &lambda; = 50 &minus; 40 = 10 per second.', 'W = 1 / 10 = 0.1 s.', eq('0.1 s &times; 1000 = 100 ms')], check=100)

K.assign('validate_features', 'e', 'Validate a request body',
         '<p>Write <code>validate_features(body)</code> for a /predict route. Return <code>200</code> when <code>body</code> is a dict whose <code>features</code> value is a list of exactly 4 numbers (int or float, but not True or False). Return <code>422</code> otherwise.</p>',
         """
def validate_features(body):
    # your code here
    pass
""", [("validate_features({'features': [5.9, 3.0, 5.1, 1.8]})", 200), ("validate_features({'features': [5.9, 'wide']})", 422), ("validate_features({'features': [1, 2, 3, True]})", 422), ('validate_features([1, 2, 3, 4])', 422), ('validate_features({})', 422)],
         """
def validate_features(body):
    if not isinstance(body, dict):
        return 422
    features = body.get('features')
    if not isinstance(features, list) or len(features) != 4:
        return 422
    for v in features:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return 422
    return 200
""", 'Check the type of body, then the list and its length, then each value. bool is a subclass of int in Python, so test for it first.', '<p>FastAPI does all of this from a Pydantic class. Writing it once by hand shows what the framework saves you.</p>')
K.assign('workers_needed', 'm', 'Size a pool of workers',
         '<p>Write <code>workers_needed(rps, latency_ms, target=0.75)</code> that returns the smallest whole number of workers that keeps each one at or below the <code>target</code> share of its time busy. Use Little&rsquo;s law: busy workers = rps &times; latency in seconds.</p>',
         """
def workers_needed(rps, latency_ms, target=0.75):
    # your code here
    pass
""", [('workers_needed(300, 25)', 10), ('workers_needed(50, 20)', 2), ('workers_needed(100, 10, 1.0)', 1), ('workers_needed(2000, 30, 0.8)', 75)],
         """
import math


def workers_needed(rps, latency_ms, target=0.75):
    busy = rps * latency_ms / 1000
    return math.ceil(round(busy / target, 9))
""", 'Busy workers is rps times latency in seconds. Divide by the target use and round up.', '<p>The round before ceil stops a float such as 10.000000000000002 from becoming 11.</p>')
K.assign('chunk_sizes', 'm', 'Split a big file into chunks',
         '<p>Write <code>chunk_sizes(n_rows, size)</code> that returns the list of chunk lengths a batch job reads, as <code>pd.read_csv(chunksize=size)</code> would: full chunks of <code>size</code> and a smaller last one if rows remain.</p>',
         """
def chunk_sizes(n_rows, size):
    # your code here
    pass
""", [('chunk_sizes(20000, 5000)', [5000, 5000, 5000, 5000]), ('chunk_sizes(12, 5)', [5, 5, 2]), ('chunk_sizes(0, 5)', []), ('chunk_sizes(3, 10)', [3])],
         """
def chunk_sizes(n_rows, size):
    return [min(size, n_rows - start) for start in range(0, n_rows, size)]
""", 'Step through the rows in jumps of size. The last chunk holds whatever is left.', '<p>Chunks keep memory flat however big the file is, because only one chunk is in memory at a time.</p>')

K.must('Model API', 'Load once. /health plus POST /predict. JSON in and out. 200 success, 422 bad content, 405 wrong method, 500 is a bug.')
K.must('Frameworks', 'Flask small. FastAPI checks Pydantic classes, docs at /docs. Django for a model inside a full web app.')
K.must('Test then call', 'Test client in one process. Then curl (macOS, Linux, ChromeOS) or Invoke-RestMethod and curl.exe (Windows).')
K.must('Online or batch', 'Online answers during the visit. Batch scores on a schedule, cheaper, less fresh. Read big files in chunks.')
K.must('Production servers', 'Gunicorn on macOS and Linux, Waitress on Windows, Uvicorn for FastAPI everywhere. Several workers. Never app.run in production.')
K.must('Capacity', 'L = &lambda;W. Workers = &lambda; &times; latency / target use. M/M/1: W = 1/(&mu; &minus; &lambda;) explodes near capacity.')

T = K.topic(
    slug='mlops-serving', topic='mlops-serving', step=(2, 'Build and ship', 'mlops-s2', 'Package a model as one pipeline, serve it as a web API with Flask, FastAPI and Django, put it in a Docker container and ship it with CI/CD.', 'Intermediate'),
    title='Serving models with Flask, FastAPI and Django', short='Serving models', badge='2.2', minutes=55,
    lead='Turn a saved pipeline into a web API with Flask, FastAPI and Django, call it from every operating system, choose between online and batch prediction, and run it on a production server with enough workers.',
    desc='Model API, HTTP, JSON, routes, status codes 200 405 422, Flask, FastAPI, Pydantic, Django, JsonResponse, test client, curl, Invoke-RestMethod, online prediction, batch prediction, Gunicorn, Waitress, Uvicorn, WSGI, ASGI, workers, Little\'s law, M/M/1 queue.',
    summary='Model APIs in Flask, FastAPI and Django, calling them on each OS, online against batch, and production servers sized with Little\'s law.',
    keywords=['model serving', 'Flask', 'FastAPI', 'Django', 'REST API', 'batch prediction', 'online prediction', 'Gunicorn', 'Waitress', 'Uvicorn', "Little's law"],
    recap='<p>Wrap the saved pipeline in a small API that checks its inputs, test it in process, call it from any system, and run it on a real server with enough workers for the traffic.</p>',
    added='2026-11-14', leet=leet_items())
