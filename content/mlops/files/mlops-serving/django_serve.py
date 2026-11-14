# 2.2 Serving models with Flask, FastAPI and Django
# Example "django_serve" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

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
