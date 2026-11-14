# MLOps 2.1: pipelines and saving models. Checked against the scikit-learn user guide (6.1 Pipelines and composite
# estimators, 6.3 Preprocessing data, 11 Common pitfalls and recommended practices, and 10 Model persistence), Kaufman
# and colleagues, Leakage in data mining (ACM TKDD 2012), Hastie, Tibshirani and Friedman, The Elements of Statistical
# Learning section 7.10.2 (the wrong and right way to do cross validation), and the joblib, skops and ONNX docs.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, term, leet_items
from mlkit import link

chapter('mlops-pipelines')
K = Kit()
K.code('column_pipeline', r'''
# One object for the whole recipe: fill gaps, scale numbers, one hot encode categories, then the model.
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

rng = np.random.default_rng(1)
n = 1000
df = pd.DataFrame({
    'tenure_months': rng.integers(1, 72, n).astype(float),
    'monthly_bill': rng.normal(60, 20, n).round(2),
    'support_calls': rng.poisson(1.5, n).astype(float),
    'plan': rng.choice(['basic', 'plus', 'premium'], n),
    'payment': rng.choice(['card', 'bank', 'cash'], n),
})
risk = -0.04 * df.tenure_months + 0.5 * df.support_calls + 0.8 * (df.plan == 'basic') + 0.02 * df.monthly_bill - 1
df['churned'] = (rng.random(n) < 1 / (1 + np.exp(-risk))).astype(int)
df.loc[rng.random(n) < 0.05, 'monthly_bill'] = np.nan       # 5 percent of bills are missing

numeric = ['tenure_months', 'monthly_bill', 'support_calls']
categorical = ['plan', 'payment']
prep = ColumnTransformer([
    ('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), numeric),
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical),
])
model = Pipeline([('prep', prep), ('clf', HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=0))])

X, y = df[numeric + categorical], df['churned']
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
print('5 fold ROC AUC on training data:', round(cross_val_score(model, X_tr, y_tr, cv=5, scoring='roc_auc').mean(), 3))
model.fit(X_tr, y_tr)
print('Test accuracy:', round(model.score(X_te, y_te), 3))
print('Columns after preprocessing:', list(model.named_steps['prep'].get_feature_names_out()))

new = pd.DataFrame([{'tenure_months': 3, 'monthly_bill': np.nan, 'support_calls': 4, 'plan': 'student', 'payment': 'card'}])
print('A new customer with a missing bill and an unseen plan "student":')
print('  churn probability', round(model.predict_proba(new)[0, 1], 3))
''', long=True)

K.code('leakage_pipeline', r'''
# Data leakage: choosing features with ALL the data before cross validation makes pure noise look predictive.
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 5000))          # 100 rows of pure noise, 5000 columns
y = rng.integers(0, 2, size=100)          # random labels: the honest accuracy is 50 percent

# Wrong: pick the 20 columns most related to y using every row, then cross validate
X_picked = SelectKBest(f_classif, k=20).fit_transform(X, y)
wrong = cross_val_score(LogisticRegression(max_iter=1000), X_picked, y, cv=5).mean()

# Right: the selection is a step of the pipeline, so each fold picks columns from its own training rows only
pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))
right = cross_val_score(pipe, X, y, cv=5).mean()

print(f'Selection before cross validation (leak): accuracy {wrong:.2f}')
print(f'Selection inside the pipeline (honest):   accuracy {right:.2f}')
''', long=True)

K.code('save_load', r'''
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
''', long=True)

K.code('input_check', r'''
# Check every request before it reaches the model: missing fields, wrong types and impossible values.
SCHEMA = {
    'tenure_months': (float, 0, 600),
    'monthly_bill': (float, 0, 10000),
    'support_calls': (int, 0, 1000),
    'plan': (str, None, None),
}
PLANS = {'basic', 'plus', 'premium'}


def check(request):
    errors = []
    for field, (kind, low, high) in SCHEMA.items():
        if field not in request:
            errors.append(f'{field}: missing')
            continue
        value = request[field]
        if kind is float and isinstance(value, int) and not isinstance(value, bool):
            value = float(value)
        if not isinstance(value, kind) or isinstance(value, bool):
            errors.append(f'{field}: expected {kind.__name__}, got {type(value).__name__}')
            continue
        if low is not None and not low <= value <= high:
            errors.append(f'{field}: {value} is outside {low} to {high}')
    if request.get('plan') not in PLANS and isinstance(request.get('plan'), str):
        errors.append(f"plan: '{request['plan']}' is not one of {sorted(PLANS)} (the model will treat it as unknown)")
    extra = set(request) - set(SCHEMA)
    if extra:
        errors.append(f'unexpected fields: {sorted(extra)}')
    return errors


requests = [
    {'tenure_months': 12, 'monthly_bill': 55.5, 'support_calls': 1, 'plan': 'plus'},
    {'tenure_months': -3, 'monthly_bill': '55', 'support_calls': 1, 'plan': 'plus'},
    {'tenure_months': 12, 'support_calls': 2.5, 'plan': 'student', 'coupon': 'X1'},
]
for r in requests:
    errs = check(r)
    print('OK, send to the model' if not errs else 'Reject with status 422:')
    for e in errs:
        print('   ', e)
''', long=True)


K.lesson('pipe', 'One pipeline from raw columns to prediction', f'''
{src('scikit-learn user guide, 6.1 Pipelines and composite estimators (Pipeline, ColumnTransformer) and 6.3 Preprocessing data.')}
{viz('mlpipeflow')}
{wwh('A <b>Pipeline</b> chains preprocessing steps and a model into one object with <code>fit</code> and <code>predict</code>. A <b>ColumnTransformer</b> sends different columns to different steps, for example imputing and scaling the numbers while one hot encoding the categories. Each step <b>fits</b> on training data (learns a median, a mean, a list of categories) and then <b>transforms</b> any data with what it learned.',
     'Without a pipeline, the same preprocessing is written twice: once in the training notebook and again in the serving code, and the two copies drift apart. A pipeline keeps the whole recipe in one object that is trained, saved, loaded and served together, and it makes cross validation honest because every step refits inside each fold.',
     'List the numeric and categorical columns, build one small pipeline for each kind, combine them in a ColumnTransformer, and put the model last. Set <code>handle_unknown=\'ignore\'</code> on the encoder so a category never seen in training does not crash the service. Call fit once on the training data, and only predict afterwards.')}
{run('column_pipeline')}
{note('The churn pipeline reaches a 5 fold ROC AUC of 0.751 and a test accuracy of 0.69. After preprocessing, 5 raw columns have become 9 (3 scaled numbers and 6 one hot columns, with names such as cat__plan_basic). A new customer with a missing bill and a plan called student, which the model never saw, still gets a churn probability of 0.782 instead of an error.', 'exam')}
{fxs(fx('Standard scaling', 'z = (x &minus; &mu;<sub>train</sub>) / &sigma;<sub>train</sub>', 'Statistics from the training data only.', key=True),
     fx('Median imputation', 'missing x &rarr; median of training x', 'Robust to outliers.', key=True),
     fx('One hot columns', 'one column per category seen in training', 'Unknown category &rarr; all zeros with ignore.', key=True))}
{link('machine-learning', 'Want the preprocessing steps in depth?', 'The Machine Learning subject, Foundations 3.1 and 3.2, explains cleaning, imputing, scaling and encoding with animations.', 'Open Machine Learning')}
''', kw=['Pipeline', 'ColumnTransformer', 'fit', 'transform', 'SimpleImputer', 'StandardScaler', 'OneHotEncoder', 'handle_unknown'])

K.lesson('leak', 'Leakage: why every learning step belongs inside the pipeline', f'''
{src('Hastie, Tibshirani and Friedman, The Elements of Statistical Learning (2009) section 7.10.2, Kaufman and colleagues, Leakage in data mining (2012), and scikit-learn user guide section 11.2, Data leakage.')}
{viz('mlleak')}
{wwh('<b>Data leakage</b> is when information that will not be available at prediction time gets into training or evaluation. A common form is preprocessing or feature selection fitted on <b>all</b> the rows before splitting, so the test rows influence the model that is then tested on them.',
     'Leakage gives scores that look excellent in the notebook and collapse in production. It is one of the most common reasons ML projects fail, because nothing crashes: the numbers are simply wrong.',
     'Split first. Put every step that learns from data (imputers, scalers, encoders, feature selection, resampling) inside the pipeline, and cross validate the whole pipeline. Also check features for values recorded after the event you predict, such as a cancellation date in a churn model.')}
{run('leakage_pipeline')}
{note('On 100 rows of random noise with random labels, choosing the 20 best of 5000 columns before cross validation reports an accuracy of 0.85. Doing the same selection inside the pipeline reports 0.48, the honest answer for labels that are pure chance.', 'exam')}
{table(['Kind of leakage', 'Example', 'Fix'], [
    ['Preprocessing on all rows', 'Scaler fitted before the split', 'Scaler inside the pipeline'],
    ['Selection on all rows', 'Top correlated columns chosen with test rows', 'SelectKBest inside the pipeline'],
    ['Target leakage', 'A column filled in after the outcome is known', 'Remove it, check the time each column becomes available'],
    ['Time leakage', 'Random split of time ordered data', 'Split by time: train on the past, test on the future'],
    ['Group leakage', 'The same patient in train and test', 'GroupKFold by patient']])}
''', kw=['data leakage', 'target leakage', 'cross validation', 'feature selection', 'time split', 'GroupKFold'])

K.lesson('save', 'Saving and loading a trained pipeline', f'''
{src('scikit-learn user guide, 10 Model persistence, the joblib documentation, the skops documentation, and the ONNX and sklearn-onnx documentation.')}
{wwh('<b>Serialising</b> a model writes the fitted object to a file so another program can load it and predict. scikit-learn models are usually saved with <b>joblib</b>, which uses Python&rsquo;s pickle format and handles NumPy arrays efficiently. A small <b>metadata</b> file next to it records the features, classes and library versions.',
     'Training happens once, prediction happens millions of times in another process, often on another machine. The file is the hand over between the two. The metadata makes sure the loading side uses compatible versions and sends the features in the right order.',
     'Save the whole pipeline, never just the model, with <code>joblib.dump</code>, and load it with <code>joblib.load</code> in the serving code. Load only files you trust, because loading a pickle can run code. Use the same scikit-learn version to load. For safer or cross language formats, use <b>skops</b> or convert to <b>ONNX</b>.')}
{run('save_load')}
{note('The fitted iris pipeline takes about 1.5 KB on disk. After loading, its predictions match the original on every row, and the flower [5.9, 3.0, 5.1, 1.8] is predicted as virginica. The JSON file records scikit-learn 1.8.0, which the serving side should match.', 'exam')}
{term(['pip install joblib skops skl2onnx onnxruntime', 'python train.py            # writes models/churn.joblib and models/churn.json', 'git add models/churn.json  # metadata in Git, the binary in a model registry or DVC'], 'Every system, inside the activated .venv')}
''', kw=['model persistence', 'joblib', 'pickle', 'metadata', 'skops', 'ONNX', 'version match', 'security'])

K.lesson('contract', 'An input contract for the model', f'''
{src('Breck and colleagues, The ML test score (2017), data and feature tests, Google, Rules of machine learning rule 10, and the pydantic documentation.')}
{wwh('An <b>input contract</b> (or schema) says which fields a request must have, their types and their allowed ranges. Requests that break it are rejected with a clear message, in a web API usually with status code 422 (unprocessable content), before they reach the model.',
     'A model will happily return a number for nonsense input: a negative age, a price sent as text, a missing field silently filled with a default. Those wrong answers flow into decisions. Checking inputs turns silent errors into loud, fixable ones.',
     'Write the schema once, check every field for presence, type and range, warn about unknown categories, and reject extra fields. In FastAPI, a pydantic model does this automatically, as chapter 2.2 shows.')}
{run('input_check')}
{note('The first request passes. The second is rejected because tenure is &minus;3 and the bill was sent as text. The third has four problems: a missing bill, 2.5 support calls where a whole number is required, an unknown plan, and an unexpected coupon field.', 'tip')}
''', kw=['input validation', 'schema', 'contract', 'status 422', 'pydantic', 'data tests'])

K.lesson('versus', 'Ways to save a model compared', f'''
{versus('Model file formats', ['', 'joblib (pickle)', 'skops', 'ONNX', 'Framework format'], [
    ['What it stores', 'Any Python object', 'scikit-learn objects', 'A computation graph', 'PyTorch state_dict, Keras .keras'],
    ['Safe to load from strangers', 'No, can run code', 'Yes, checks types first', 'Yes', 'Mostly (PyTorch weights_only loading)'],
    ['Needs Python to serve', 'Yes, same versions', 'Yes', 'No: C++, C#, Java, JavaScript runtimes', 'Usually'],
    ['Speed of serving', 'Normal', 'Normal', 'Often faster with ONNX Runtime', 'Normal'],
    ['Best for', 'Your own models, quick start', 'Sharing scikit-learn models', 'Serving across languages and devices', 'Deep learning models']],
    'joblib for your own Python services, skops when files come from elsewhere, ONNX when the serving side is not Python.')}
''', kw=['joblib vs ONNX', 'skops', 'pickle security'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Put all the cleaning steps and the model into one box, train the box, and save it as one file.</p>',
    '<p>Build Pipelines with ColumnTransformer, avoid leakage, save with joblib plus metadata, and validate every input.</p>',
    '<p>Write custom transformers, tune whole pipelines with grid search, handle time and group splits, and export to skops or ONNX.</p>',
    '<p>Design feature stores that share one feature definition between training and serving, detect training serving skew, and secure the model supply chain.</p>')}
{grow('Train and save a pipeline.',
      'Build leak free pipelines that serve safely.',
      'Keep features identical in training and production.')}
''', kw=['beginner', 'expert', 'feature store', 'training serving skew'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>Pipeline</b> plus a <b>ColumnTransformer</b> holds imputing, scaling, encoding and the model in one object with fit and predict.',
    'Steps <b>fit</b> on training data only and <b>transform</b> new rows with what they learned. handle_unknown=\'ignore\' keeps unseen categories from crashing.',
    '<b>Leakage</b>: any step fitted on all rows (scaling, selection) lets test rows shape the model. Selection outside cross validation scored 0.85 on noise, inside it scored 0.48.',
    'Save the whole pipeline with <b>joblib</b> plus a metadata file with features, classes and versions. Load only trusted files, with the same library versions.',
    'Check every request against an <b>input contract</b> and reject bad ones with status 422.'],
    'MLOps 2.2 serves the saved pipeline as a web API with Flask, FastAPI and Django.')}
{files('Three tasks: median imputation, z scores with training statistics, and one hot encoding with unknown categories.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A scikit-learn Pipeline', ['Downloads data', 'Chains preprocessing steps and a model into one object', 'Plots charts', 'Replaces the model'], 1, 'One object, many steps.', 'fit and predict call every step.')
K.quiz('e', 'A StandardScaler inside a pipeline uses the mean and spread of', ['Each new row', 'The training data', 'The test data', 'All data ever'], 1, 'Learned during fit.', 'Reused at predict time.')
K.quiz('e', 'joblib.dump is used to', ['Train a model', 'Save a fitted object to a file', 'Clean data', 'Delete a model'], 1, 'Persistence.', 'joblib.load reads it back.')
K.quiz('e', 'OneHotEncoder(handle_unknown=\'ignore\') turns an unseen category into', ['An error', 'All zeros in the one hot columns', 'The most common category', 'A new column'], 1, 'Ignore means zeros.', 'The service keeps running.')
K.quiz('m', 'Fitting a scaler on all rows before cross validation is a problem because', ['It is slow', 'Test rows influence the preprocessing, which leaks information', 'Scaling is not allowed', 'It changes the labels'], 1, 'Leakage.', 'Put the scaler in the pipeline.')
K.quiz('m', 'A ColumnTransformer is needed when', ['There is one column', 'Different columns need different preprocessing', 'The model is a tree', 'Data is an image'], 1, 'Numbers and categories.', 'Each gets its own small pipeline.')
K.quiz('m', 'Why save the whole pipeline instead of just the model?', ['Smaller file', 'So serving applies exactly the same preprocessing as training', 'Faster training', 'Required by Python'], 1, 'No drift between copies.', 'One object to load.')
K.quiz('m', 'Loading a pickle or joblib file from an unknown source is risky because', ['It may be large', 'Loading can execute arbitrary code', 'It changes Python', 'It deletes data'], 1, 'Pickle runs code.', 'Use skops or trusted sources.')
K.quiz('m', 'A web API should answer a request with a missing required field with', ['200 and a guess', '422 and a clear error message', '500', 'No answer'], 1, 'Unprocessable content.', 'Reject before the model.')
K.quiz('h', 'Feature selection on 5000 noise columns before cross validation reported 0.85 accuracy. The honest value is near', ['0.85', '0.5', '1.0', '0.0'], 1, 'Labels are random.', 'Inside the pipeline it reported 0.48.')
K.quiz('h', 'Time ordered data such as daily sales should be split', ['Randomly', 'By time: train on earlier days, test on later days', 'By row number backwards', 'Not at all'], 1, 'No peeking at the future.', 'TimeSeriesSplit does this.')
K.quiz('h', 'ONNX is most useful when', ['You need Python 2', 'The serving side is not Python, or needs a fast runtime', 'You want to retrain', 'The model is tiny'], 1, 'Cross language graph.', 'ONNX Runtime runs it.')
K.quiz('x', 'In the style of a Stanford CS229 project review: a churn model scores 0.99 AUC because one feature is days since cancellation. This is', ['Overfitting', 'Target leakage: the feature is only known after the outcome', 'Underfitting', 'Class imbalance'], 1, 'Available only afterwards.', 'Remove features recorded after the event.')
K.quiz('x', 'In the style of an ML engineer interview: training serving skew means', ['Two models disagree', 'Features are computed differently in training and in production', 'The server is slow', 'Labels are skewed'], 1, 'Same feature, two codes.', 'A saved pipeline or feature store prevents it.')

K.calc('e', 'Known tenures are 2, 10, 18 and 30. Median used to fill a missing one?', '14', 'Middle of the sorted values.', ['Sorted: 2, 10, 18, 30.', 'Even count: average the middle two.', eq('(10 + 18) / 2 = 14')], check=14)
K.calc('e', 'Training mean 14.8 and spread 9.26. z score of a tenure of 4?', '−1.17', '(x &minus; &mu;) / &sigma;.', ['4 &minus; 14.8 = &minus;10.8.', 'Divide by 9.26.', eq('&minus;10.8 / 9.26 = &minus;1.17')], check=-1.17, tol=0.005)
K.calc('e', 'A plan column with 3 values and a payment column with 3 values are one hot encoded. How many columns?', '6', 'One per category.', ['Plan: 3 columns.', 'Payment: 3 columns.', eq('3 + 3 = 6')], check=6)
K.calc('m', '3 numeric columns are scaled and the 2 categorical columns above are one hot encoded. Columns after the ColumnTransformer?', '9', 'Numbers stay one column each.', ['Numeric: 3.', 'One hot: 6.', eq('3 + 6 = 9')], check=9)
K.calc('m', '800 training rows and 5 fold cross validation. Rows used to fit in each fold?', '640', '4 folds of 5 train.', ['Each fold holds 800 / 5 = 160 rows.', 'Training uses 4 folds.', eq('4 &times; 160 = 640')], check=640)
K.calc('m', 'A grid search tries 4 values of C and 3 of class_weight with 5 fold cross validation, then refits the best once. Total fits?', '61', 'Combinations times folds, plus one.', ['4 &times; 3 = 12 combinations.', '12 &times; 5 = 60 fits.', eq('60 + 1 refit = 61')], check=61)
K.calc('m', 'Leaky selection scored 0.85 and the honest pipeline 0.48. Size of the illusion?', '0.37', 'Subtract.', ['Leaky: 0.85.', 'Honest: 0.48.', eq('0.85 &minus; 0.48 = 0.37')], check=0.37)
K.calc('h', 'The pipeline&rsquo;s logit for a customer is 2.48. Churn probability?', '0.9227', 'Sigmoid.', ['p = 1 / (1 + e<sup>&minus;2.48</sup>).', 'e<sup>&minus;2.48</sup> = 0.0837.', eq('1 / 1.0837 = 0.9227')], check=0.9227, tol=0.0005)
K.calc('h', '5000 columns of pure noise are tested for a link with the labels at the 1 percent level. Expected number that look significant by chance?', '50', 'Expected false positives.', ['Each noise column passes with probability 0.01.', 'There are 5000 columns.', eq('5000 &times; 0.01 = 50')], check=50)
K.calc('x', 'In the style of a systems question: a 1,569 byte model file is loaded on every request instead of once at start up. Bytes read for 1 million requests, in GB (10<sup>9</sup> bytes)?', '1.569', 'Size times requests.', ['1,569 &times; 1,000,000 = 1.569 &times; 10<sup>9</sup> bytes.', 'Divide by 10<sup>9</sup>.', eq('1.569 GB, for a file read once is enough')], check=1.569, tol=0.0005)

K.assign('impute_median', 'e', 'Median imputation',
         '<p>Write <code>impute_median(values)</code> that replaces each <code>None</code> in the list with the median of the other values and returns the new list. For an even count, the median is the average of the two middle values.</p>',
         """
def impute_median(values):
    # your code here
    pass
""", [('impute_median([2, 10, None, 30, 18])', [2, 10, 14.0, 30, 18]), ('impute_median([None, 5, 1, 3])', [3, 5, 1, 3]), ('impute_median([7, None])', [7, 7])],
         """
def impute_median(values):
    known = sorted(v for v in values if v is not None)
    n = len(known)
    mid = known[n // 2] if n % 2 else (known[n // 2 - 1] + known[n // 2]) / 2
    return [mid if v is None else v for v in values]
""", 'Sort the known values, take the middle one (or the average of the middle two), and put it where each None was.', '<p>SimpleImputer(strategy=\'median\') does exactly this, and remembers the median from fit so new rows get the training median.</p>')
K.assign('scale_with', 'm', 'Scale new values with training statistics',
         '<p>Write <code>scale_with(train, new)</code> that computes the mean and population standard deviation of <code>train</code> and returns the z scores of the values in <code>new</code>, each rounded to 4 decimals.</p>',
         """
def scale_with(train, new):
    # your code here
    pass
""", [('scale_with([2, 10, 14, 30, 18], [4, 14.8])', [-1.1662, 0.0]), ('scale_with([0, 2], [1, 3])', [0.0, 2.0])],
         """
import math


def scale_with(train, new):
    mean = sum(train) / len(train)
    std = math.sqrt(sum((v - mean) ** 2 for v in train) / len(train))
    return [round((v - mean) / std + 0.0, 4) for v in new]
""", 'Compute the mean and spread from train only, then apply (v &minus; mean) / spread to each new value.', '<p>Using the statistics of the new values instead would make the same customer get a different z score depending on who else is in the batch.</p>')
K.assign('one_hot', 'm', 'One hot encoding with unknown categories',
         '<p>Write <code>one_hot(value, categories)</code> that returns a list with a 1 in the position of <code>value</code> in <code>categories</code> and 0 elsewhere. An unknown value gives all zeros.</p>',
         """
def one_hot(value, categories):
    # your code here
    pass
""", [("one_hot('plus', ['basic', 'plus', 'premium'])", [0, 1, 0]), ("one_hot('student', ['basic', 'plus', 'premium'])", [0, 0, 0]), ("one_hot('a', ['a'])", [1])],
         """
def one_hot(value, categories):
    return [1 if c == value else 0 for c in categories]
""", 'Compare the value with each category in order.', '<p>This is OneHotEncoder with handle_unknown=\'ignore\': the category list comes from training, and anything else becomes zeros.</p>')

K.must('Pipeline', 'Preprocessing plus model in one object. ColumnTransformer: numbers impute and scale, categories one hot.')
K.must('fit and transform', 'Steps learn on training rows only, reuse at predict. handle_unknown=\'ignore\' for unseen categories.')
K.must('Leakage', 'No step may see test rows. Selection outside CV: 0.85 on noise, inside: 0.48. Split by time and group too.')
K.must('Saving', 'joblib.dump the whole pipeline plus JSON metadata (features, classes, versions). Load trusted files only.')
K.must('Formats', 'joblib for own Python services, skops for safe sharing, ONNX for other languages.')
K.must('Input contract', 'Check presence, type, range, unknown categories, extra fields. Reject with 422.')

T = K.topic(
    slug='mlops-pipelines', topic='mlops-pipelines', step=(2, 'Build and ship', 'mlops-s2', 'Package a model as one pipeline, serve it as a web API with Flask, FastAPI and Django, and run it on a production server.', 'Intermediate'),
    title='Pipelines and saving models', short='Pipelines and saving', badge='2.1', minutes=45,
    lead='Put every preprocessing step and the model into one scikit-learn pipeline, keep it free of leakage, save it with its metadata, and check every input against a contract before it reaches the model.',
    desc='Pipeline, ColumnTransformer, fit, transform, SimpleImputer, StandardScaler, OneHotEncoder, handle_unknown, data leakage, target leakage, time split, joblib, pickle, metadata, skops, ONNX, input validation, status 422.',
    summary='Leak free scikit-learn pipelines, saving with joblib and metadata, file formats, and input contracts.',
    keywords=['Pipeline', 'ColumnTransformer', 'data leakage', 'joblib', 'model persistence', 'ONNX', 'skops', 'input validation', 'handle_unknown', 'metadata'],
    recap='<p>Train one object that holds the whole recipe, test it honestly, save it with the facts needed to trust it, and guard its door with an input contract.</p>',
    added='2026-11-14', leet=leet_items())
