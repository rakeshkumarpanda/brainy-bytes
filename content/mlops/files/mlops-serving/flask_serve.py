# 2.2 Serving models with Flask, FastAPI and Django
# Example "flask_serve" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

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
