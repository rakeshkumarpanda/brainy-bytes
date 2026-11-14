# MLOps 1.2: the MLOps lifecycle and reproducible projects. Checked against Google Cloud, MLOps: Continuous delivery
# and automation pipelines in machine learning (maturity levels 0, 1 and 2), Sculley and colleagues, Hidden technical
# debt in machine learning systems (NeurIPS 2015), Breck and colleagues, The ML test score (IEEE Big Data 2017),
# Kreuzberger, Kuhl and Hirschl, Machine learning operations (MLOps): overview, definition, and architecture (IEEE
# Access 2023), Huyen, Designing machine learning systems (O'Reilly 2022), and the DVC and MLflow documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, term, leet_items
from mlkit import link

chapter('mlops-lifecycle')
K = Kit()
K.code('seeds', r'''
# Same code, same data, different results? Randomness hides in the data split and in the model.
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)


def experiment(seed):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=seed)
    model = RandomForestClassifier(n_estimators=50, random_state=seed).fit(X_tr, y_tr)
    return model.score(X_te, y_te)


print('No seed (a fresh random seed each run):')
rng = np.random.default_rng()
scores = [experiment(int(rng.integers(1_000_000))) for _ in range(5)]
print('  accuracies', [round(s, 3) for s in scores], ' spread', round(max(scores) - min(scores), 3))
print('Fixed seed 42, run 5 times:')
scores = [experiment(42) for _ in range(5)]
print('  accuracies', [round(s, 3) for s in scores], ' spread', round(max(scores) - min(scores), 3))
print('Ten different fixed seeds, to see the honest uncertainty:')
scores = np.array([experiment(s) for s in range(10)])
print(f'  mean {scores.mean():.3f}, standard deviation {scores.std():.3f}, min {scores.min():.3f}, max {scores.max():.3f}')
''', long=True)

K.code('run_record', r'''
# A run record: everything needed to explain, repeat or roll back one training run.
import hashlib
import json
import platform
from importlib.metadata import version

import numpy as np
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_wine(return_X_y=True)
params = {'C': 0.5, 'max_iter': 500, 'test_size': 0.25, 'seed': 7}


def fingerprint(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:12]


X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=params['test_size'], random_state=params['seed'], stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(C=params['C'], max_iter=params['max_iter']))
model.fit(X_tr, y_tr)

record = {
    'data': {'rows': len(X), 'features': X.shape[1], 'fingerprint': fingerprint(X, y)},
    'params': params,
    'metrics': {'train_accuracy': round(model.score(X_tr, y_tr), 4), 'test_accuracy': round(model.score(X_te, y_te), 4)},
    'environment': {'python': platform.python_version(), 'numpy': version('numpy'), 'scikit-learn': version('scikit-learn')},
}
print(json.dumps(record, indent=2))
''', long=True)

K.code('data_versions', r'''
# Data changes too. Version it by fingerprint, and record which data each model was trained on.
import hashlib

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)


def fingerprint(X, y):
    return hashlib.sha256(np.ascontiguousarray(X).tobytes() + np.ascontiguousarray(y).tobytes()).hexdigest()[:12]


rng = np.random.default_rng(3)
versions = {'v1 original': (X, y)}
y2 = y.copy()
flip = rng.choice(len(y), size=40, replace=False)        # v2: a labelling mistake flips 40 labels
y2[flip] = 1 - y2[flip]
versions['v2 with 40 wrong labels'] = (X, y2)
keep = rng.random(len(y)) > 0.3                           # v3: a new export loses about 30 percent of rows
versions['v3 missing rows'] = (X[keep], y[keep])

model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
for name, (Xv, yv) in versions.items():
    acc = cross_val_score(model, Xv, yv, cv=5).mean()
    print(f'{name:24s} rows {len(yv):3d}  fingerprint {fingerprint(Xv, yv)}  5 fold accuracy {acc:.3f}')
print('Same code, three data versions, three different models. Only the fingerprint tells you which one you have.')
''', long=True)


K.lesson('what', 'What MLOps is', f'''
{src('Google Cloud, MLOps: Continuous delivery and automation pipelines in machine learning, Sculley and colleagues, Hidden technical debt in machine learning systems (NeurIPS 2015), and Kreuzberger, Kuhl and Hirschl (IEEE Access 2023).')}
{viz('mllifecycle')}
{wwh('<b>MLOps</b> (machine learning operations) is the set of practices that take a model from an experiment to a product and keep it working: versioning data, code and models, automated training pipelines, testing, deployment, monitoring and retraining. It extends <b>DevOps</b>, which does this for ordinary software, with the parts that are special to ML.',
     'In ML the behaviour comes from data as much as from code. A model can be correct on launch day and wrong a month later because the world changed, with no code change at all. Sculley and colleagues (2015) showed that the model code is a small box in a real ML system, surrounded by data collection, feature pipelines, serving and monitoring, and that most of the long term cost lives there.',
     'Treat the loop as the product: define the problem and metric, version the data, train in a repeatable pipeline that logs everything, evaluate against the current model, register the winner, deploy it, monitor it, and retrain when monitoring says so. Automate one stage at a time, starting with training.')}
{table(['Level', 'What is automated', 'Typical sign'], [
    ['0: manual', 'Nothing. Notebooks, files copied by hand', 'A model is retrained a few times a year'],
    ['1: ML pipeline automation', 'Data, training, evaluation and registration run as one pipeline, retraining is triggered', 'Continuous training (CT) on new data'],
    ['2: CI/CD pipeline automation', 'The pipeline itself is tested, built and deployed by CI/CD', 'Many models updated safely every week']])}
{fxs(fx('An ML system', 'behaviour = code + data + model + configuration', 'All four need versions.', key=True),
     fx('Continuous training', 'new data &rarr; retrain &rarr; evaluate &rarr; register &rarr; deploy', 'The loop of level 1.', key=True),
     fx('Automation share', 'automated stages / all stages', 'A rough maturity measure.'))}
{scene('A churn model that went stale', 'A telecom company launched a model that predicted which customers would leave, with 90 percent precision. Six months later a competitor launched a cheap plan, customer behaviour changed and precision fell to 60 percent, but nobody noticed because nothing watched the model. With MLOps, a monitor would have flagged the change in input data within days and triggered retraining on recent customers.')}
''', kw=['MLOps', 'DevOps', 'lifecycle', 'maturity levels', 'continuous training', 'technical debt', 'pipeline'])

K.lesson('repro', 'Reproducibility: seeds and run records', f'''
{src('Pineau and colleagues, Improving reproducibility in machine learning research (JMLR 2021), the scikit-learn glossary entry for random_state, and the MLflow tracking documentation.')}
{viz('mlseeds')}
{wwh('A run is <b>reproducible</b> when the same code, data, configuration and environment give the same result. Randomness hides in data splits, model initialisation, bagging and shuffling, and a <b>random seed</b> fixes it. A <b>run record</b> stores everything about one run: data version, parameters, metrics and package versions.',
     'Without reproducibility you cannot tell whether a change helped, debug a model that misbehaves in production, or prove to an auditor how a decision was made. With it you can rerun any past model exactly and roll back to it.',
     'Set <code>random_state</code> (or seed NumPy, Python and PyTorch) and keep the seed in the configuration. Report the spread over several seeds, not one lucky number. Save a run record for every training run, which tools such as MLflow do for you.')}
{run('seeds')}
{note('The first block changes every time you run it, which is the point. With the seed fixed at 42, five runs give exactly the same accuracy, 0.972, five times. Over ten different seeds the accuracy has mean 0.956 and standard deviation 0.014, ranging from 0.937 to 0.972, so a difference of 0.01 between two models trained once means nothing.', 'exam')}
{run('run_record')}
{note('The record says the wine data had 178 rows and 13 features with fingerprint 3a28849ef236, lists the parameters (C = 0.5, seed 7), the metrics (test accuracy 0.9778) and the Python, NumPy and scikit-learn versions. With this one JSON file, anyone can rebuild and check the model.', 'tip')}
''', kw=['reproducibility', 'random seed', 'random_state', 'run record', 'experiment tracking', 'variance across seeds'])

K.lesson('versions', 'Versioning data and models', f'''
{src('The DVC documentation (Data Version Control), Google, Rules of machine learning (rule 4 onwards), and the MLflow model registry documentation.')}
{wwh('<b>Data versioning</b> gives every dataset a fixed identity, usually a content <b>fingerprint</b> (a hash), so you always know which data trained which model. Tools such as <b>DVC</b> keep large files outside Git and store their hashes in Git. A <b>model registry</b> stores each trained model with its version, metrics, data version and stage (for example staging or production). <b>Lineage</b> is the chain from raw data to deployed model.',
     'Data changes silently: a new export drops rows, a labelling mistake flips classes, a column changes its units. The code stays the same but the model changes, and without versions nobody can explain why accuracy moved or go back to the last good model.',
     'Hash the data at every pipeline step and save the hash in the run record. Commit small data and DVC pointer files to Git. Register every model that passes evaluation, with tags for the code commit and the data fingerprint, and promote or roll back by changing the registry stage, not by copying files.')}
{run('data_versions')}
{note('The original breast cancer data gives a 5 fold accuracy of 0.981. Flipping 40 labels (7 percent) drops it to 0.882 with the same number of rows. Losing about 30 percent of the rows (399 left) gives 0.975. Each version has a different fingerprint, so the run record shows exactly which one a model saw.', 'exam')}
{term(['pip install dvc', 'git init && dvc init', 'dvc add data/customers.csv          # writes data/customers.csv.dvc with the hash', 'git add data/customers.csv.dvc data/.gitignore', 'git commit -m "Data version 1"', 'dvc push                             # uploads the file to remote storage (S3, GCS, Azure, a drive)'], 'Versioning a dataset with DVC (every system)')}
{table(['What', 'Versioned with', 'Example'], [
    ['Code and configs', 'Git', 'Commit a1b2c3d'],
    ['Data', 'Fingerprint, DVC or lakeFS', 'customers.csv, hash 25e2eb7b7a87'],
    ['Environment', 'requirements.txt, lock file, Docker image tag', 'ml-api:1.4.0'],
    ['Model', 'Model registry', 'churn-model version 7, stage production'],
    ['Experiments', 'Tracking server', 'MLflow run 3f9e, accuracy 0.981']])}
''', kw=['data versioning', 'fingerprint', 'hash', 'DVC', 'model registry', 'lineage', 'rollback'])

K.lesson('project', 'A project layout that grows into production', f'''
{src('Cookiecutter Data Science (DrivenData), Breck and colleagues, The ML test score: a rubric for ML production readiness (2017), and Huyen, Designing machine learning systems (2022) chapter 10.')}
{wwh('A good ML project separates <b>data</b>, <b>notebooks</b> for exploring, <b>source code</b> for anything that must run again, <b>configs</b> for parameters, <b>tests</b>, and <b>models</b> or reports produced by runs. Settings live in config files, not inside the code.',
     'Notebooks are perfect for exploring and terrible for production: cells run out of order, results hide in outputs, and they are hard to test or review. Moving reusable steps into small functions in src makes them testable and lets a pipeline call them.',
     'Start from a standard layout, keep raw data read only, put every step (load, clean, features, train, evaluate) in its own function, and test data and model as well as code. The ML test score asks for tests of features, data, the model and the infrastructure.')}
{term(['ml-project/', '  data/raw/            # never edited, versioned with DVC', '  data/processed/', '  notebooks/           # exploring only', '  src/', '    data.py            # load and clean', '    features.py', '    train.py           # reads configs/train.yaml, writes a run record', '    evaluate.py', '  configs/train.yaml', '  tests/', '    test_data.py       # schema, ranges, missing values', '    test_model.py      # accuracy above a floor, invariance checks', '  models/              # outputs, not in Git', '  requirements.txt', '  README.md'], 'A layout that works on every system')}
{table(['Test type', 'Checks', 'Example'], [
    ['Data tests', 'Schema, ranges, missing values, label balance', 'age between 0 and 120'],
    ['Feature tests', 'Transformations do what they claim', 'Scaled column has mean near 0 on training data'],
    ['Model tests', 'Quality floor, behaviour on known cases', 'Accuracy at least 0.9, prediction unchanged when the name changes'],
    ['Infrastructure tests', 'Pipeline runs end to end, model loads and serves', 'Training on 100 rows finishes, API returns a valid answer']])}
''', kw=['project structure', 'cookiecutter', 'configs', 'notebooks vs scripts', 'ML test score', 'data tests', 'model tests'])

K.lesson('versus', 'DevOps, MLOps and DataOps compared', f'''
{versus('Three operations disciplines', ['', 'DevOps', 'MLOps', 'DataOps'], [
    ['What it ships', 'Software', 'Models and the pipelines that make them', 'Data products and pipelines'],
    ['What changes behaviour', 'Code', 'Code, data and model', 'Data and transformations'],
    ['Testing', 'Unit and integration tests', 'Plus data tests and model quality gates', 'Data quality checks'],
    ['After release', 'Uptime and errors', 'Plus drift, accuracy and fairness', 'Freshness and quality of data'],
    ['Typical tools', 'Git, CI/CD, Docker, Kubernetes', 'Plus MLflow, DVC, feature stores, registries', 'Airflow, dbt, data contracts']],
    'MLOps reuses everything from DevOps and adds versioning of data and models, training pipelines and model monitoring.')}
''', kw=['DevOps vs MLOps', 'DataOps', 'comparison'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A model is not finished when it scores well once. It needs to be rebuilt, shipped, watched and improved, again and again.</p>',
    '<p>Fix seeds, write run records, version data by fingerprint, keep code in a clean layout with tests, and explain the three maturity levels.</p>',
    '<p>Build level 1 training pipelines with tracking and a registry, version data with DVC, and add data, model and infrastructure tests to CI.</p>',
    '<p>Design level 2 platforms: CI/CD for pipelines, feature stores, lineage across teams, governance and audit, and the cost of ML technical debt.</p>')}
{grow('Explain the MLOps loop.',
      'Make experiments reproducible and versioned.',
      'Design automated ML platforms.')}
''', kw=['beginner', 'expert', 'ML platform'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>MLOps</b> versions, tests, deploys, monitors and retrains ML systems. It adds data and model concerns to DevOps.',
    'The lifecycle loops: problem, data, train, evaluate, register, deploy, monitor, retrain. <b>Levels 0, 1 and 2</b> automate more of it.',
    'Fix <b>random seeds</b>, report the spread over several seeds, and save a <b>run record</b> with data fingerprint, parameters, metrics and versions.',
    'Version <b>data</b> by hash (DVC), <b>models</b> in a registry, code in Git and the environment in requirements or images, so every model has a <b>lineage</b>.',
    'Keep a clean project layout, move notebook code into tested functions, and test data, features, model and infrastructure.'],
    'MLOps 2.1 builds a full scikit-learn pipeline and saves it as one file ready to serve.')}
{files('Three tasks: a data fingerprint, picking the best run, and the spread of scores over seeds.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'MLOps is mainly about', ['Writing faster models', 'Taking models to production and keeping them working', 'Drawing charts', 'Collecting labels'], 1, 'Operations.', 'Versioning, deployment, monitoring, retraining.')
K.quiz('e', 'Setting random_state in scikit-learn makes a run', ['More accurate', 'Repeatable', 'Faster', 'Smaller'], 1, 'Same seed, same result.', 'Not better, just repeatable.')
K.quiz('e', 'A model registry stores', ['Raw data', 'Trained models with versions, metrics and stage', 'Passwords', 'Notebooks'], 1, 'Versions of models.', 'Promote or roll back there.')
K.quiz('e', 'At MLOps maturity level 0', ['Everything is automated', 'Every step is done by hand', 'Only deployment is manual', 'There is no model'], 1, 'Manual.', 'Most teams start here.')
K.quiz('m', 'Why can a deployed model get worse with no code change?', ['Python slows down', 'The data in the world changes, so the patterns it learned no longer hold', 'Files decay', 'The model forgets'], 1, 'Data drift.', 'Monitoring catches it.')
K.quiz('m', 'A data fingerprint is', ['The file name', 'A hash of the data content that changes if any value changes', 'The number of rows', 'The upload date'], 1, 'Content hash.', 'Stored in the run record.')
K.quiz('m', 'DVC keeps large data files', ['Inside Git', 'Outside Git, with small pointer files holding their hashes in Git', 'Only on your laptop', 'In the model'], 1, 'Pointer files.', 'dvc push sends data to remote storage.')
K.quiz('m', 'Ten seeds give accuracies with standard deviation 0.014. Model B beats A by 0.004 on one seed. You should', ['Ship B at once', 'Treat it as noise until it holds across many seeds', 'Delete A', 'Lower the seed'], 1, 'Smaller than the spread.', 'Compare means over seeds.')
K.quiz('m', 'Level 1 MLOps adds', ['Nothing', 'An automated training pipeline with continuous training', 'Only a new UI', 'Manual email of models'], 1, 'Pipeline automation.', 'Level 2 adds CI/CD for the pipeline.')
K.quiz('h', 'Sculley and colleagues (2015) argued that in real ML systems', ['The model code is most of the work', 'The model code is a small part, and the surrounding data and serving code holds most of the debt', 'Data never changes', 'Testing is unnecessary'], 1, 'Hidden technical debt.', 'Glue code, pipeline jungles, entanglement.')
K.quiz('h', 'Which is a model test rather than a code test?', ['A function returns a list', 'Accuracy on a held out set stays above 0.9 and predictions do not change when only the name changes', 'The file exists', 'Linting passes'], 1, 'Quality and behaviour.', 'From the ML test score.')
K.quiz('h', 'Lineage lets you answer', ['Which colour the dashboard is', 'Which code, data and parameters produced the model in production', 'How fast the GPU is', 'Who wrote Python'], 1, 'Data to model chain.', 'Needed for audits and rollbacks.')
K.quiz('x', 'In the style of a Google Cloud ML engineer exam: new labelled data arrives weekly and the pipeline code changes rarely. The most useful first investment is', ['Manual retraining every quarter', 'Continuous training: an automated pipeline triggered by new data, with evaluation gates', 'A bigger model', 'Turning monitoring off'], 1, 'Level 1.', 'CI/CD for code can come later.')
K.quiz('x', 'In the style of an AWS ML specialty question: an auditor asks how a loan decision from March was made. You need', ['The current model only', 'The registered model version, its training data fingerprint, code commit and parameters', 'The newest data', 'A new model'], 1, 'Lineage and run records.', 'Versions of everything.')

K.calc('e', 'A loop has 8 stages and 6 run automatically. Fraction automated?', '0.75', 'Automated over all.', ['Automated stages: 6.', 'All stages: 8.', eq('6 / 8 = 0.75')], check=0.75)
K.calc('e', 'Five runs without a seed scored 0.9, 0.8, 1.0, 0.8 and 0.9. Spread (highest minus lowest)?', '0.2', 'Max minus min.', ['Highest 1.0.', 'Lowest 0.8.', eq('1.0 &minus; 0.8 = 0.2')], check=0.2)
K.calc('m', 'Mean of those five scores?', '0.88', 'Add and divide by 5.', ['0.9 + 0.8 + 1.0 + 0.8 + 0.9 = 4.4.', 'There are 5 runs.', eq('4.4 / 5 = 0.88')], check=0.88)
K.calc('m', 'Population standard deviation of those five scores?', '0.0748', 'Square root of the average squared gap.', ['Gaps from 0.88: 0.02, &minus;0.08, 0.12, &minus;0.08, 0.02.', 'Squares add to 0.028, and 0.028 / 5 = 0.0056.', eq('&radic;0.0056 = 0.0748')], check=0.0748, tol=0.0005)
K.calc('m', 'Ten seeds give a standard deviation of 0.014. Standard error of the mean accuracy?', '0.0044', '&sigma; / &radic;n.', ['n = 10, &radic;10 = 3.162.', 'Divide.', eq('0.014 / 3.162 = 0.0044')], check=0.0044, tol=0.0001)
K.calc('m', 'A fingerprint keeps 12 hexadecimal characters. How many bits is that?', '48', 'Each hex character is 4 bits.', ['One hex digit has 16 values = 4 bits.', '12 digits.', eq('12 &times; 4 = 48 bits')], check=48)
K.calc('h', 'Three versions of a 2 GB dataset. Full copies cost 6 GB. A content store keeps v1 fully plus changes of 0.1 GB and 0.3 GB. GB saved?', '3.6', 'Full copies minus deduplicated size.', ['Deduplicated: 2 + 0.1 + 0.3 = 2.4 GB.', 'Full copies: 3 &times; 2 = 6 GB.', eq('6 &minus; 2.4 = 3.6 GB')], check=3.6)
K.calc('h', 'Accuracy starts at 92 and drops 0.5 points per week. With retraining every 8 weeks, accuracy just before a retrain?', '88', 'Linear decay.', ['8 weeks &times; 0.5 = 4 points lost.', 'Start at 92.', eq('92 &minus; 4 = 88')], check=88)
K.calc('h', 'A labelling mistake flips 40 of 569 labels. Percentage of wrong labels?', '7.03', 'Part over whole times 100.', ['40 / 569 = 0.0703.', 'Times 100.', eq('7.03 percent')], check=7.03, tol=0.005)
K.calc('x', 'In the style of an experiment design question: model A has mean accuracy 0.956 and B 0.962 over seeds, each with standard deviation 0.014 for one run. z score of one run each, using &sigma;&radic;2 for the difference?', '0.303', 'Difference over its standard deviation.', ['Difference 0.962 &minus; 0.956 = 0.006.', 'Its standard deviation: 0.014 &times; &radic;2 = 0.0198.', eq('0.006 / 0.0198 = 0.303, far below 2, so not significant')], check=0.303, tol=0.002)

K.assign('data_fingerprint', 'e', 'A data fingerprint',
         '<p>Write <code>data_fingerprint(rows)</code> that returns the first 12 characters of the SHA-256 hash of <code>repr(rows)</code> encoded as UTF-8. Use <code>hashlib</code>.</p>',
         """
import hashlib


def data_fingerprint(rows):
    # your code here
    pass
""", [('data_fingerprint([[1, 2], [3, 4]])', '1e258794ed04'), ('data_fingerprint([[1, 2], [3, 5]])', '23f12147ee03'), ('data_fingerprint([])', '4f53cda18c2b')],
         """
import hashlib


def data_fingerprint(rows):
    return hashlib.sha256(repr(rows).encode('utf-8')).hexdigest()[:12]
""", 'hashlib.sha256 takes bytes, so encode the repr text, then take hexdigest()[:12].', '<p>Change one value (4 to 5 in the second test) and the whole fingerprint changes, which is what makes it a reliable version id.</p>')
K.assign('best_run', 'm', 'Pick the best run',
         '<p>Write <code>best_run(runs, metric, higher_is_better)</code>. <code>runs</code> is a list of dictionaries with a <code>\'name\'</code> and metric values. Return the name of the run with the best value of <code>metric</code>. If two are equal, keep the first.</p>',
         """
def best_run(runs, metric, higher_is_better):
    # your code here
    pass
""", [("best_run([{'name': 'a', 'acc': 0.95}, {'name': 'b', 'acc': 0.97}], 'acc', True)", 'b'),
      ("best_run([{'name': 'a', 'rmse': 3.1}, {'name': 'b', 'rmse': 2.4}, {'name': 'c', 'rmse': 2.4}], 'rmse', False)", 'b'),
      ("best_run([{'name': 'x', 'acc': 0.9}], 'acc', True)", 'x')],
         """
def best_run(runs, metric, higher_is_better):
    best = runs[0]
    for r in runs[1:]:
        better = r[metric] > best[metric] if higher_is_better else r[metric] < best[metric]
        if better:
            best = r
    return best['name']
""", 'Keep the best so far and replace it only when a later run is strictly better in the right direction.', '<p>Accuracy is better when higher, errors such as RMSE when lower. Tracking tools ask the same question when you sort runs.</p>')
K.assign('seed_spread', 'm', 'Mean and spread over seeds',
         '<p>Write <code>seed_spread(scores)</code> that returns <code>[mean, std]</code> of the scores, using the population standard deviation (divide by n), both rounded to 4 decimals.</p>',
         """
def seed_spread(scores):
    # your code here
    pass
""", [('seed_spread([0.9, 0.8, 1.0, 0.8, 0.9])', [0.88, 0.0748]), ('seed_spread([0.5, 0.5])', [0.5, 0.0]), ('seed_spread([1.0, 0.0])', [0.5, 0.5])],
         """
import math


def seed_spread(scores):
    n = len(scores)
    mean = sum(scores) / n
    std = math.sqrt(sum((s - mean) ** 2 for s in scores) / n)
    return [round(mean, 4), round(std + 0.0, 4)]
""", 'Average the scores, then take the square root of the average squared distance from that mean.', '<p>Report a model as mean plus or minus standard deviation over seeds, for example 0.956 &plusmn; 0.014.</p>')

K.must('MLOps', 'Version, test, deploy, monitor and retrain ML. DevOps plus data and models.')
K.must('Levels', '0 manual, 1 automated training pipeline (continuous training), 2 CI/CD for the pipeline.')
K.must('Reproducible', 'Fix seeds, report spread over seeds, save run records: data fingerprint, params, metrics, versions.')
K.must('Versions', 'Code in Git, data by hash (DVC), models in a registry, environment in requirements or images. Lineage.')
K.must('Tests', 'Data, features, model quality and behaviour, infrastructure. Notebooks to tested functions.')
K.must('Why it matters', 'Models decay as data changes. Hidden technical debt lives outside the model code.')

T = K.topic(
    slug='mlops-lifecycle', topic='mlops-lifecycle', step=(1, 'Set up and plan', 'mlops-s1', 'Get your computer ready on macOS, Windows, Linux or ChromeOS, and learn what MLOps is and how to make a project reproducible.', 'Beginner'),
    title='The MLOps lifecycle and reproducible projects', short='MLOps lifecycle', badge='1.2', minutes=45,
    lead='See the whole loop from data to monitoring at three levels of automation, then make runs repeatable with seeds and run records, version data and models, and lay out a project that can grow into production.',
    desc='MLOps, DevOps, lifecycle, maturity levels, continuous training, technical debt, reproducibility, random seed, run record, data versioning, fingerprint, DVC, model registry, lineage, project structure, ML test score, data tests, model tests.',
    summary='The MLOps loop and maturity levels, seeds and run records, data and model versioning, and project layout.',
    keywords=['MLOps', 'lifecycle', 'maturity levels', 'reproducibility', 'random seed', 'run record', 'data versioning', 'DVC', 'model registry', 'lineage'],
    recap='<p>A model is a loop, not a file. Make every run repeatable, give data and models versions, and automate the loop one stage at a time.</p>',
    added='2026-11-14', leet=leet_items())
