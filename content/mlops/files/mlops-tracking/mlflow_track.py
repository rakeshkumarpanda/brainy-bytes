# 3.1 Experiment tracking and the model registry
# Example "mlflow_track" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Track experiments and register models with MLflow (pip install mlflow scikit-learn).
# Every run is stored in mlflow.db and the folder mlruns next to this file. See them with:
#   mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
import logging
import warnings

import mlflow
from mlflow import MlflowClient
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')
logging.getLogger('mlflow').setLevel(logging.ERROR)

mlflow.set_tracking_uri('sqlite:///mlflow.db')
mlflow.set_experiment('breast-cancer')

X, y = load_breast_cancer(return_X_y=True)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)

for C in [0.01, 0.1, 1.0, 10.0]:
    with mlflow.start_run(run_name=f'logreg C={C}'):
        model = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000)).fit(X_train, y_train)
        auc = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])
        mlflow.log_params({'model': 'logistic regression', 'C': C})
        mlflow.log_metrics({'val_auc': auc, 'val_accuracy': accuracy_score(y_val, model.predict(X_val))})
        mlflow.set_tag('data', 'sklearn breast cancer, 25 percent validation, seed 0')
        mlflow.sklearn.log_model(model, name='model', input_example=X_val[:2])

runs = mlflow.search_runs(order_by=['metrics.val_auc DESC'])
print(runs[['tags.mlflow.runName', 'params.C', 'metrics.val_auc', 'metrics.val_accuracy']].round(4).to_string(index=False))

best = runs.iloc[0]
version = mlflow.register_model(f'runs:/{best.run_id}/model', 'breast-cancer-classifier')
client = MlflowClient()
client.set_registered_model_alias('breast-cancer-classifier', 'champion', version.version)
print('Registered version', version.version, 'from run', best['tags.mlflow.runName'], 'with alias champion')

served = mlflow.sklearn.load_model('models:/breast-cancer-classifier@champion')     # what a service would load
print('Loaded models:/breast-cancer-classifier@champion, validation AUC', round(roc_auc_score(y_val, served.predict_proba(X_val)[:, 1]), 4))
