# Foundations 1.2: the machine learning project workflow. Checked against the CRISP-DM 1.0 guide (Chapman and others,
# 2000), Aurelien Geron, Hands-On Machine Learning (3rd edition) chapter 2 "End-to-End Machine Learning Project", Google's
# "Rules of Machine Learning" (Martin Zinkevich), the Google ML Crash Course on data splitting, and the scikit-learn 1.8
# user guide for train_test_split, DummyRegressor and DummyClassifier.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('ml-workflow')
K = Kit()

K.code('frame_the_problem', r'''
# Write the problem down before touching any model
project = {
    "goal": "Show customers a delivery time they can trust",
    "prediction": "minutes until the food arrives",
    "task type": "regression (the answer is a number)",
    "data": "past orders with distance, hour, weather and real minutes",
    "metric": "mean absolute error in minutes",
    "success": "average error under 5 minutes",
    "baseline": "3 minutes per km plus 10 minutes",
}
for key, value in project.items():
    print(key.ljust(11), ":", value)

# A quick check that the baseline gives sensible numbers
for km in [1, 4, 8]:
    print(km, "km ->", 3 * km + 10, "minutes")
''')

K.code('look_at_data', r'''
import pandas as pd

orders = pd.DataFrame({
    "distance_km": [1.2, 3.5, 5.0, 2.2, 8.1, 4.4, 0.9, 6.3],
    "hour": [12, 13, 20, 9, 21, 19, 15, 13],
    "raining": [0, 0, 1, 0, 1, 0, 0, 1],
    "minutes": [14, 22, 38, 17, 51, 29, 12, 41],
})
print(orders.shape)                 # (rows, columns)
print(orders.head(3))               # the first rows
print(orders["minutes"].describe().round(1))
print("average minutes when raining:", round(orders[orders["raining"] == 1]["minutes"].mean(), 1))
print("average minutes when dry:    ", round(orders[orders["raining"] == 0]["minutes"].mean(), 1))
''')

K.code('split_by_hand', r'''
import random

rows = list(range(20))        # pretend these are 20 examples, numbered 0 to 19
random.seed(42)
random.shuffle(rows)          # shuffle so every part is a fair sample

n = len(rows)
n_test = int(n * 0.2)         # 20% for the final test
n_val = int(n * 0.2)          # 20% to compare models

test_rows = rows[:n_test]
val_rows = rows[n_test:n_test + n_val]
train_rows = rows[n_test + n_val:]

print("train:", len(train_rows), sorted(train_rows))
print("val:  ", len(val_rows), sorted(val_rows))
print("test: ", len(test_rows), sorted(test_rows))
print("no overlap:", set(train_rows).isdisjoint(test_rows) and set(val_rows).isdisjoint(test_rows))
''')

K.code('split_sklearn', r'''
from sklearn.model_selection import train_test_split

X = [[i] for i in range(20)]
y = [1, 0, 0, 0, 0] * 4          # 4 of 20 examples are the rare class 1

# plain split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=3)
print("plain     : rare in test =", sum(y_test), "of", len(y_test), "<- no rare examples to test on!")

# stratified split keeps the same share of class 1 in both parts
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=3, stratify=y)
print("stratified: rare in test =", sum(y_test), "of", len(y_test))
print("stratified: rare in train =", sum(y_train), "of", len(y_train))
''')

K.code('baseline_first', r'''
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

X_train = [[1.2], [3.5], [5.0], [2.2], [8.1], [4.4]]   # distance in km
y_train = [14, 22, 38, 17, 51, 29]                     # minutes
X_test = [[0.9], [6.3]]
y_test = [12, 41]

baseline = DummyRegressor(strategy="mean")    # always predicts the training average
baseline.fit(X_train, y_train)
print("baseline predicts:", baseline.predict(X_test))
print("baseline error:", round(mean_absolute_error(y_test, baseline.predict(X_test)), 2), "minutes")

model = LinearRegression()
model.fit(X_train, y_train)
print("model predicts:", model.predict(X_test).round(1))
print("model error:", round(mean_absolute_error(y_test, model.predict(X_test)), 2), "minutes")
''')

K.code('error_analysis', r'''
# After training, look at WHERE the model is wrong, not only how much
orders = [
    # distance, raining, true minutes, predicted minutes
    (2.0, 0, 16, 15),
    (5.0, 0, 27, 28),
    (3.0, 1, 30, 20),
    (6.0, 1, 45, 32),
    (1.0, 0, 11, 12),
    (4.0, 1, 36, 24),
]
dry_errors = []
rain_errors = []
for distance, raining, true_minutes, predicted in orders:
    error = abs(true_minutes - predicted)
    if raining:
        rain_errors.append(error)
    else:
        dry_errors.append(error)

print("average error when dry: ", round(sum(dry_errors) / len(dry_errors), 1), "minutes")
print("average error when rain:", round(sum(rain_errors) / len(rain_errors), 1), "minutes")
print("idea: add a 'raining' feature, the model does not know about rain yet")
''')

K.code('leakage_demo', r'''
from sklearn.tree import DecisionTreeClassifier

# Predict if a loan will be repaid (1) or not (0).
# Columns: income_k, debt_k, late_fee_paid. The last one is filled in AFTER the loan ends!
X_train = [[30, 10, 0], [50, 5, 0], [20, 15, 1], [60, 2, 0], [25, 12, 1], [40, 8, 0], [35, 6, 1], [28, 9, 0]]
y_train = [1, 1, 0, 1, 0, 1, 0, 1]
X_test = [[45, 7, 0], [22, 14, 1], [33, 11, 1], [52, 3, 0]]     # old loans, so the column is filled in
y_test = [1, 0, 0, 1]

leaky = DecisionTreeClassifier(random_state=0).fit(X_train, y_train)
print("test accuracy with the leaky column:", leaky.score(X_test, y_test))

# Real use: a NEW applicant. Nobody has paid a late fee yet, so the column is always 0.
X_real = [[row[0], row[1], 0] for row in X_test]
print("accuracy on the same people at decision time:", leaky.score(X_real, y_test))

fair = DecisionTreeClassifier(random_state=0).fit([r[:2] for r in X_train], y_train)
print("fair model (income and debt only):", fair.score([r[:2] for r in X_test], y_test))
''')

K.lesson('frame', 'Step 1: frame the problem before any code', f'''
{src('CRISP-DM 1.0 (2000), Geron, Hands-On Machine Learning chapter 2, Zinkevich, Rules of Machine Learning, and the scikit-learn 1.8 user guide.')}
{wwh('<b>Framing</b> means writing down, in plain words, what decision the model will help with, what exactly it predicts, how we will measure success, and what simple rule it must beat.',
     'The most common reason ML projects fail is not a weak model. It is solving the wrong problem, measuring the wrong thing, or building a model nobody can use. Ten minutes of framing saves months.',
     'Answer six questions: What is the business goal? What is the output (number, category, ranking)? What data exists at the moment we must predict? Which metric shows success? What is the simplest baseline? How will the prediction be used?')}
{scene('the delivery time on your food app', '<p>When you order food, the app says "arrives in 32 minutes". Before any model, the team agreed: the output is minutes, the data is past orders, the metric is the average error in minutes, and "3 minutes per km plus 10" is the baseline to beat. They also agreed the model may only use facts known when you press Order. The rider’s real route is not known yet, so it cannot be a feature.</p>')}
{run('frame_the_problem')}
{note('Ask "do we even need ML?" first. If a simple rule or a lookup table is good enough, ship that. Google’s Rules of ML put it as rule number one: do not be afraid to launch a product without machine learning.', 'tip')}
''', kw=['problem framing', 'business goal', 'metric', 'baseline', 'success criteria', 'do we need ML'])

K.lesson('stages', 'The stages of an ML project', f'''
{viz('mlflow')}
{table(['Stage', 'Main question', 'Typical output'], [
    ['1. Frame', 'What decision, what output, what metric?', 'A one page problem statement'],
    ['2. Get data', 'Which data exists and may we use it?', 'Raw tables, files, logs'],
    ['3. Explore and clean', 'What is in the data, what is broken?', 'Clean table, charts, notes'],
    ['4. Split', 'How do we test fairly?', 'Train, validation and test sets'],
    ['5. Baseline', 'What does a simple rule score?', 'A number to beat'],
    ['6. Train and tune', 'Which model and settings work best?', 'A trained model'],
    ['7. Evaluate', 'How good is it on unseen data?', 'Test score and error analysis'],
    ['8. Deploy', 'How do users get predictions?', 'An API, an app feature, a nightly job'],
    ['9. Monitor', 'Is it still good next month?', 'Dashboards, alerts, retraining']])}
<p>This loop matches <b>CRISP-DM</b> (Cross Industry Standard Process for Data Mining), published in 2000 and still the most used project model. Its six phases are business understanding, data understanding, data preparation, modelling, evaluation and deployment. Modern teams add monitoring, which the MLOps section covers.</p>
{note('In real projects most time goes to data: finding it, cleaning it and understanding it. Training the model is often the shortest stage.', 'tip')}
''', kw=['ML lifecycle', 'CRISP-DM', 'stages', 'deployment', 'monitoring', 'project workflow'])

K.lesson('data', 'Step 2 and 3: get the data and look at it', f'''
<p>Before modelling, look at the data the way a doctor looks at a patient: size, a few rows, averages, ranges and anything odd. The pandas library (Foundations 1.3) makes this quick.</p>
{run('look_at_data')}
{table(['Check', 'Why', 'pandas'], [
    ['Shape', 'How many examples and features', 'df.shape'],
    ['First rows', 'See real values and types', 'df.head()'],
    ['Summary statistics', 'Spot impossible values (negative minutes)', 'df.describe()'],
    ['Missing values', 'Holes must be filled or removed', 'df.isna().sum()'],
    ['Group averages', 'First ideas for features (rain is slower)', 'df.groupby("raining")["minutes"].mean()']])}
{note('Look at the data, but do the deep exploration on the training part only, after splitting. If you study the test set too, you start choosing features that fit it, and your final score becomes too optimistic.', 'warn')}
''', kw=['exploratory data analysis', 'EDA', 'pandas', 'describe', 'shape', 'head', 'data quality'])

K.lesson('split', 'Step 4: train, validation and test sets', f'''
{viz('mlsplit')}
{wwh('We cut the data into a <b>training set</b> (to learn parameters), a <b>validation set</b> (to compare models and settings) and a <b>test set</b> (one final honest score).',
     'A model always looks good on the data it learned from. We need data it has never seen to know how it will do for real users. If we also chose settings using the test set, the test set would stop being "unseen".',
     'Shuffle, then cut, for example 60 / 20 / 20 or 70 / 15 / 15. With a rare class, <b>stratify</b> so every part keeps the same class share. With time data, do not shuffle: train on the past and test on the most recent period.')}
{run('split_by_hand')}
{run('split_sklearn')}
{table(['Data type', 'How to split', 'Why'], [
    ['Normal rows (independent)', 'Shuffle, then cut', 'Every part is a fair sample'],
    ['Imbalanced classes', 'Stratified split', 'Each part keeps the rare class share'],
    ['Time series (sales, prices)', 'By time: past for train, latest for test', 'In real use we always predict the future'],
    ['Many rows per person or patient', 'Group split: all rows of one person in one part', 'Otherwise the model meets the same person in train and test']])}
{note('Fix random_state (the seed) so the split is the same every time you run the program. Otherwise your scores change from run to run and you cannot compare models.', 'exam')}
''', kw=['train test split', 'validation set', 'test set', 'stratify', 'random_state', 'time split', 'group split'])

K.lesson('baseline', 'Step 5: always start with a baseline', f'''
{wwh('A <b>baseline</b> is the score of a very simple method: always predict the average, always predict the most common class, or a one line rule from common sense.',
     'Without a baseline a number like "error 6.2" means nothing. If the baseline gets 6.5, the fancy model barely helps. If it gets 15, the model is a big win.',
     'scikit-learn has DummyRegressor and DummyClassifier for this. Train them like any model, then compare every real model against them on the same validation data.')}
{run('baseline_first')}
{note('A model that cannot beat the baseline usually means a bug, leakage the other way, or features that carry no signal. Check the data before trying a bigger model.', 'warn')}
''', kw=['baseline', 'DummyRegressor', 'DummyClassifier', 'mean absolute error', 'majority class'])

K.lesson('iterate', 'Step 6 and 7: train, look at errors, improve', f'''
<p>Training is a loop of its own: train a model, measure it on the validation set, study the mistakes, change one thing, and repeat. Looking at <b>where</b> the model fails tells you what to try next far better than guessing.</p>
{run('error_analysis')}
{steps('How an expert reads errors', [
    'Sort validation examples by error, largest first, and read the worst 20.',
    'Group them: are they all at night, in rain, from one city, from one data source?',
    'Ask what information would have helped a person guess right in those cases.',
    'Add that information as a feature, collect more data of that kind, or fix wrong labels.',
    'Retrain and compare on the same validation set. Keep a written log of every try.'])}
{note('Change one thing at a time and keep notes. If you change the features, the model and the settings together, you never learn which change helped.', 'tip')}
''', kw=['error analysis', 'iteration', 'validation', 'experiment log', 'model improvement'])

K.lesson('leakage', 'The silent killer: data leakage', f'''
{wwh('<b>Data leakage</b> happens when information that would not be available at prediction time sneaks into training. The model looks brilliant in testing and fails in real use.',
     'Leakage produces false confidence. Teams ship a model with "99% accuracy" that falls to a coin flip on real users, which costs money and trust.',
     'Ask for every feature: "Would I know this value at the exact moment I make the prediction?" Also fit every preprocessing step (scaling, filling missing values) on the training set only, then apply it to validation and test.')}
{run('leakage_demo')}
{table(['Kind of leak', 'Example', 'Fix'], [
    ['Future information', 'late_fee_paid used to predict loan repayment', 'Use only facts known at decision time'],
    ['Target in disguise', 'Hospital stay length used to predict if a patient was admitted', 'Remove features caused by the label'],
    ['Preprocessing on all data', 'Scaling with the mean of train and test together', 'Fit the scaler on train only, use a Pipeline'],
    ['Duplicates across sets', 'The same customer in train and test', 'Remove duplicates, use a group split'],
    ['Time order broken', 'Shuffling stock prices, so the model sees the future', 'Split by time']])}
{note('If a score looks too good to be true, it usually is. Hunt for leakage before you celebrate.', 'exam')}
''', kw=['data leakage', 'target leakage', 'train test contamination', 'pipeline', 'future information'])

K.lesson('deploy', 'Step 8 and 9: deploy and monitor', f'''
{table(['Way to deploy', 'How it works', 'Good for'], [
    ['Batch', 'Run the model on all rows every night and store the answers', 'Churn lists, daily forecasts, email campaigns'],
    ['Online (real time) API', 'The app sends one request and gets an answer in milliseconds', 'Delivery times, fraud checks, search'],
    ['On device', 'The model runs inside the phone or camera', 'Face unlock, keyboard suggestions, offline apps'],
    ['Streaming', 'The model reads events as they arrive', 'Sensor alarms, live recommendations']])}
<p>After launch, the world keeps changing. Prices rise, new cities open, user habits shift. When the data a model sees drifts away from the data it learned from, its accuracy drops quietly. Monitoring the input data and the errors, and retraining when needed, keeps it useful. The MLOps section builds a real API with Flask and FastAPI and shows how to watch for this <b>drift</b>.</p>
''', kw=['deployment', 'batch prediction', 'online prediction', 'API', 'monitoring', 'data drift', 'retraining'])

K.lesson('versus', 'Ways of working compared', f'''
{versus('Project styles', ['', 'Quick notebook experiment', 'CRISP-DM project', 'MLOps lifecycle'], [
    ['Goal', 'Try an idea fast', 'Deliver a working model for a business question', 'Keep many models healthy in production'],
    ['Steps', 'Load, train, print a score', 'Six phases from business to deployment', 'CRISP-DM plus automation, monitoring and retraining'],
    ['Testing', 'Often a single split', 'Train, validation and test', 'Automated tests for data, code and model'],
    ['Repeatable', 'Rarely', 'Mostly, with notes', 'Yes: versioned data, code and models'],
    ['Best for', 'Learning and first ideas', 'One off analysis and first models', 'Products used every day']],
    'learn with notebooks, deliver with a CRISP-DM style plan, and run products with MLOps.')}
{versus('Batch or online prediction', ['', 'Batch', 'Online'], [
    ['When answers are made', 'In advance, on a schedule', 'At the moment of the request'],
    ['Speed needed', 'Minutes or hours are fine', 'Milliseconds'],
    ['Cost and complexity', 'Lower', 'Higher (servers always on)'],
    ['Fresh data', 'As old as the last run', 'Uses the latest input']],
    'pick batch when answers can wait, online when the user is waiting.')}
''', kw=['CRISP-DM vs MLOps', 'batch vs online', 'notebook', 'comparison'])

K.lesson('maths', 'The maths of splitting and testing', f'''
{fxs(fx('Split sizes', 'n<sub>train</sub> = n &minus; n<sub>val</sub> &minus; n<sub>test</sub>, with n<sub>test</sub> = round(n &times; test share)', 'For n = 1,000 with 20% test and 20% validation: 600, 200, 200.'),
     fx('Uncertainty of a test accuracy', 'SE = &radic;(p(1 &minus; p) / n)', 'p is the measured accuracy, n the number of test examples. Smaller n means a shakier score.', key=True),
     fx('Rough 95% range', 'p &plusmn; 2 &times; SE', 'With p = 0.9 and n = 100: SE = 0.03, so the true accuracy is likely between 0.84 and 0.96.', key=True),
     fx('Test size for a target precision', 'n &asymp; 4 p(1 &minus; p) / m<sup>2</sup>', 'm is the half width you want. For p = 0.9 and m = 0.02, n &asymp; 900.'),
     fx('Mean absolute error', 'MAE = (1/n) &Sigma; |y<sub>i</sub> &minus; ŷ<sub>i</sub>|', 'The average size of the mistakes, in the same unit as y.', key=True))}
{steps('Worked example: is model B really better?', [
    'Model A: 85% accuracy on 200 test examples. Model B: 88% on the same 200.',
    'SE for A = &radic;(0.85 &times; 0.15 / 200) = &radic;0.0006375 &asymp; 0.025.',
    'So A’s 95% range is about 0.80 to 0.90. B’s 0.88 is inside it.',
    eq('The 3 point gap is within the noise of 200 examples'),
    'To be sure, use more test data or a paired test (McNemar) on the examples where A and B disagree. Cross validation (Supervised 4.2) also helps.'])}
{deep('Why the test set must be used once', '<p>Every time you look at the test score and then change the model, you leak a little information from the test set into your choices. After many rounds you have "fit" the test set, and its score is too optimistic. This is called adaptive overfitting. Kaggle competitions show it clearly: the public leaderboard score is often higher than the hidden private score. Keep a validation set (or cross validation) for choices and touch the test set once.</p>')}
''', kw=['split sizes', 'standard error', 'confidence interval', 'MAE', 'test set size', 'McNemar'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>An ML project starts with a clear question, gathers data, keeps some data aside for testing, tries a simple method first, then a real model, and keeps checking it after launch.</p>',
    '<p>Frame the output and metric, explore and clean on training data, split into train, validation and test (stratified or by time when needed), beat a baseline, study errors, avoid leakage, deploy as batch or online, monitor for drift.</p>',
    '<p>Choose the split to match how the model is used (random, grouped, time based). Quantify uncertainty of scores with standard errors or the bootstrap, compare models with paired tests, and build every preprocessing step into a pipeline fitted on training folds only.</p>',
    '<p>Research on adaptive data analysis (Dwork and others, 2015) shows that reusing a holdout set for many decisions breaks its guarantees, and methods such as the reusable holdout limit what each query reveals. Production systems face distribution shift (covariate, label and concept shift), studied under domain adaptation, with tools such as importance weighting and drift detection tests.</p>')}
{grow('List the nine stages of a project and explain why we keep a test set.',
      'Frame a real problem, build stratified and time based splits, beat a baseline, and spot leakage.',
      'Put error bars on scores, choose splits that match deployment, and design monitoring for drift.')}
''', kw=['beginner', 'expert', 'adaptive overfitting', 'distribution shift', 'reusable holdout'])

lc(905, 'Sort Array By Parity', 'sort-array-by-parity', 'e', 'Partition into two groups', 'Walk once and put even numbers in one list and odd numbers in another, then join them. Splitting rows into groups by a rule is what a data split does.', r'''
def sort_array_by_parity(nums):
    evens = []
    odds = []
    for x in nums:
        if x % 2 == 0:
            evens.append(x)
        else:
            odds.append(x)
    return evens + odds
''', [('sort_array_by_parity([3, 1, 2, 4])', [2, 4, 3, 1]), ('sort_array_by_parity([0])', [0])])
lc(2161, 'Partition Array According to Given Pivot', 'partition-array-according-to-given-pivot', 'm', 'Stable three way partition', 'Make three lists: smaller than the pivot, equal, and larger, keeping the original order inside each. Then join them.', r'''
def pivot_array(nums, pivot):
    smaller = []
    equal = []
    larger = []
    for x in nums:
        if x < pivot:
            smaller.append(x)
        elif x == pivot:
            equal.append(x)
        else:
            larger.append(x)
    return smaller + equal + larger
''', [('pivot_array([9, 12, 5, 10, 14, 3, 10], 10)', [9, 5, 3, 10, 10, 12, 14]), ('pivot_array([-3, 4, 3, 2], 2)', [-3, 2, 4, 3])])
lc(2270, 'Number of Ways to Split Array', 'number-of-ways-to-split-array', 'm', 'Prefix sums', 'Keep the sum of the left part as you move the cut. The right sum is the total minus the left sum. Count cuts where left is at least right.', r'''
def ways_to_split_array(nums):
    total = sum(nums)
    left = 0
    count = 0
    for i in range(len(nums) - 1):
        left = left + nums[i]
        if left >= total - left:
            count = count + 1
    return count
''', [('ways_to_split_array([10, 4, -8, 7])', 2), ('ways_to_split_array([2, 3, 1, 0])', 2)])
lc(2780, 'Minimum Index of a Valid Split', 'minimum-index-of-a-valid-split', 'm', 'Count the dominant value on both sides', 'Find the value that is more than half of the list. Move the cut from left to right and check that it is more than half on both sides. This is the idea behind a stratified split: both parts keep the same majority.', r'''
def minimum_index(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    dominant = nums[0]
    for x in counts:
        if counts[x] > counts[dominant]:
            dominant = x
    total = counts[dominant]
    left = 0
    n = len(nums)
    for i in range(n - 1):
        if nums[i] == dominant:
            left = left + 1
        right = total - left
        if left * 2 > i + 1 and right * 2 > n - i - 1:
            return i
    return -1
''', [('minimum_index([1, 2, 2, 2])', 2), ('minimum_index([2, 1, 3, 1, 1, 1, 7, 1, 2, 1])', 4), ('minimum_index([3, 3, 3, 3, 7, 2, 2])', -1)])
lc(915, 'Partition Array into Disjoint Intervals', 'partition-array-into-disjoint-intervals', 'm', 'Running max on the left, running min on the right', 'Build the smallest value of every suffix first. Then walk from the left keeping the largest value so far. The first cut where left max is at most right min is the answer.', r'''
def partition_disjoint(nums):
    n = len(nums)
    right_min = [0] * n
    right_min[n - 1] = nums[n - 1]
    for i in range(n - 2, -1, -1):
        right_min[i] = min(nums[i], right_min[i + 1])
    left_max = nums[0]
    for i in range(n - 1):
        left_max = max(left_max, nums[i])
        if left_max <= right_min[i + 1]:
            return i + 1
    return n
''', [('partition_disjoint([5, 0, 3, 8, 6])', 3), ('partition_disjoint([1, 1, 1, 0, 6, 12])', 4)])
lc(384, 'Shuffle an Array', 'shuffle-an-array', 'm', 'Fisher Yates shuffle', 'Go from the last position down. Swap each position with a random position at or before it. Every order is equally likely, which is what a fair train and test split needs.', r'''
import random


class Solution:
    def __init__(self, nums):
        self.original = nums[:]
        self.nums = nums[:]

    def reset(self):
        self.nums = self.original[:]
        return self.nums

    def shuffle(self):
        items = self.nums[:]
        for i in range(len(items) - 1, 0, -1):
            j = random.randint(0, i)
            items[i], items[j] = items[j], items[i]
        self.nums = items
        return items


def shuffle_check(nums):
    random.seed(1)
    s = Solution(nums)
    mixed = s.shuffle()
    return sorted(mixed) == sorted(nums) and s.reset() == nums
''', [('shuffle_check([1, 2, 3])', True), ('shuffle_check([5, 5, 9, 1])', True)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Splitting data is really partitioning a list. These problems train the same thinking: put items into groups by a rule, choose a cut point with prefix sums, keep the majority on both sides like a stratified split, and shuffle fairly. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'partition', 'prefix sum', 'shuffle', 'Fisher Yates', 'split'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Frame first: goal, output, data available at prediction time, metric, success level and baseline.',
    'The project loop: frame, get data, explore and clean, split, baseline, train and tune, evaluate, deploy, monitor. CRISP-DM describes the same loop.',
    'Split into <b>train</b> (learn), <b>validation</b> (choose) and <b>test</b> (final score, used once). Stratify rare classes, split time data by time, keep groups together.',
    'Always compare against a <b>baseline</b> such as DummyRegressor or DummyClassifier.',
    'Study errors to decide what to try next, and change one thing at a time.',
    '<b>Leakage</b> means training on information not available at prediction time. Fit preprocessing on training data only.',
    'Deploy as batch, online API, on device or streaming, then monitor for drift and retrain.',
    'A test score is uncertain: SE = &radic;(p(1 &minus; p)/n).'],
    'Foundations 1.3 teaches NumPy, pandas and the scikit-learn API, the three tools you will use in every chapter.')}
{files('Three tasks: split a list into train and test, a stratified split by hand, and the standard error of an accuracy.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which set is used only once, at the very end?', ['Training set', 'Validation set', 'Test set', 'All of them'], 2, 'The honest final score.', 'The test set gives one final, unbiased estimate.')
K.quiz('e', 'What is a baseline?', ['The best possible model', 'A very simple method to compare against', 'The test set', 'A type of neural network'], 1, 'Something to beat.', 'A baseline, such as predicting the average, sets the minimum bar.')
K.quiz('e', 'Which set do we use to compare models and settings?', ['Test set', 'Validation set', 'Training set', 'Production data'], 1, 'Not the test set.', 'The validation set is for choices, so the test stays unseen.')
K.quiz('e', 'Predicting next month’s sales: how should you split?', ['Shuffle randomly', 'Train on past months, test on the latest months', 'Test on the oldest months', 'Do not split'], 1, 'In real use we predict the future.', 'Time data is split by time so the model never sees the future.')
K.quiz('m', 'Only 2% of transactions are fraud. Which split keeps 2% fraud in every part?', ['Random split', 'Stratified split', 'Time split', 'No split'], 1, 'Keeps class shares.', 'stratify=y keeps the class proportions the same.')
K.quiz('m', 'Using the hospital stay length to predict whether a patient was admitted is', ['Feature engineering', 'Data leakage', 'Regularisation', 'Stratification'], 1, 'Is it known before the decision?', 'The stay length only exists after admission, so it leaks the answer.')
K.quiz('m', 'You scale features using the mean of the whole dataset before splitting. What is wrong?', ['Nothing', 'Test information leaks into training', 'Scaling is never needed', 'The model becomes linear'], 1, 'The mean includes test rows.', 'Fit the scaler on training data only, then apply it to test.')
K.quiz('m', 'Why fix random_state in train_test_split?', ['To make the model faster', 'So the split is the same every run and results can be compared', 'To stratify automatically', 'To remove leakage'], 1, 'Repeatable.', 'The same seed gives the same shuffle.')
K.quiz('m', 'A patient has 10 scans in the data. Some scans are in train and some in test. The problem is', ['Too little data', 'The model meets the same patient twice, so the test score is too high', 'Class imbalance', 'Underfitting'], 1, 'Same person, both sides.', 'Use a group split so all of a patient’s rows land in one part.')
K.quiz('h', 'Accuracy 0.9 on 100 test examples. What is the standard error?', ['0.09', '0.03', '0.3', '0.009'], 1, '&radic;(p(1 &minus; p)/n).', '&radic;(0.9 &times; 0.1 / 100) = &radic;0.0009 = 0.03.')
K.quiz('h', 'Which deployment fits "send a list of customers to call every morning"?', ['Online API', 'Batch prediction', 'On device', 'Streaming'], 1, 'Answers can wait.', 'A nightly batch job fits a daily list.')
K.quiz('h', 'CRISP-DM’s first phase is', ['Modelling', 'Business understanding', 'Deployment', 'Data preparation'], 1, 'Start with the why.', 'CRISP-DM starts with business understanding.')
K.quiz('x', 'In the style of a Stanford CS329S (ML systems) exam: you tune 50 models and pick the one with the best test score. What is the main risk?', ['Underfitting', 'The chosen score is optimistically biased because the test set was used for selection', 'The models become linear', 'Class imbalance'], 1, 'Selection on the test set.', 'Choosing on the test set turns it into a validation set. Its score is no longer an unbiased estimate.')
K.quiz('x', 'In the style of a CMU 10-701 question: to halve the standard error of a test accuracy, the test set must be', ['2 times larger', '4 times larger', '&radic;2 times larger', '8 times larger'], 1, 'SE grows like 1/&radic;n.', 'SE &prop; 1/&radic;n, so halving it needs 4 times the examples.')

K.calc('e', 'A dataset has 1,000 rows. Test share 20%. How many test rows?', '200', 'Multiply.', ['n = 1,000.', 'Share 0.2.', eq('1,000 &times; 0.2 = 200')], check=1000 * 0.2)
K.calc('e', '1,000 rows, 20% test and 20% validation. How many training rows?', '600', 'What is left.', ['Test 200.', 'Validation 200.', eq('1,000 &minus; 200 &minus; 200 = 600')], check=1000 - 200 - 200)
K.calc('e', 'True minutes 10 and 20, predictions 12 and 17. What is the MAE?', '2.5', 'Average of absolute gaps.', ['Gaps 2 and 3.', 'Sum 5.', eq('5 / 2 = 2.5')], check=(2 + 3) / 2)
K.calc('m', 'Accuracy 0.8 on 400 test examples. What is the standard error?', '0.02', '&radic;(p(1 &minus; p)/n).', ['p(1 &minus; p) = 0.16.', '0.16 / 400 = 0.0004.', eq('&radic;0.0004 = 0.02')], check=(0.8 * 0.2 / 400) ** 0.5, tol=1e-9)
K.calc('m', 'With that SE of 0.02, what is the upper end of the rough 95% range p + 2 SE?', '0.84', 'Add two SEs.', ['p = 0.8.', '2 &times; 0.02 = 0.04.', eq('0.8 + 0.04 = 0.84')], check=0.8 + 2 * 0.02, tol=1e-9)
K.calc('m', 'A dataset has 500 rows, 10% of them fraud. A stratified 20% test set has how many fraud rows?', '10', '20% of the 50 fraud rows.', ['Fraud rows = 50.', 'Test share 0.2.', eq('50 &times; 0.2 = 10')], check=50 * 0.2)
K.calc('m', 'A baseline has MAE 9 minutes, the model 6. By what percent did the error drop?', '33.33', '(9 &minus; 6)/9.', ['Drop = 3.', '3 / 9 = 0.3333.', eq('about 33.33%')], check=round(3 / 9 * 100, 2), tol=0.01)
K.calc('h', 'How many test examples give a 95% half width of 0.03 when p is about 0.5? Use n = 4 p(1 &minus; p)/m<sup>2</sup>.', '1111', 'Plug in.', ['4 &times; 0.25 = 1.', 'm<sup>2</sup> = 0.0009.', eq('1 / 0.0009 &asymp; 1,111')], check=int(4 * 0.25 / 0.0009))
K.calc('h', 'Accuracy p = 0.95 measured on n = 19 examples. What is p(1 &minus; p)/n? (Round to 4 decimals.)', '0.0025', 'Then the SE is its root.', ['0.95 &times; 0.05 = 0.0475.', '0.0475 / 19 = 0.0025.', eq('SE = 0.05')], check=round(0.95 * 0.05 / 19, 4))
K.calc('x', 'In the style of an MIT 6.S897 question: models A and B are tested on the same 300 examples. They disagree on 30. A is right on 20 of those, B on 10. McNemar’s statistic is (b &minus; c)<sup>2</sup> / (b + c). What is it?', '3.33', 'b = 20, c = 10.', ['b &minus; c = 10.', '(10)<sup>2</sup> = 100.', eq('100 / 30 &asymp; 3.33, below 3.84, so not significant at 5%')], check=round(100 / 30, 2), tol=0.01)

K.assign('split', 'e', 'Split a list into train and test',
         '<p>Write <code>split_list(items, test_fraction)</code> that returns a pair <code>(train, test)</code>. The test part is the LAST round(len(items) &times; test_fraction) items, and the train part is everything before it. Do not shuffle.</p>',
         '''
def split_list(items, test_fraction):
    # your code here
    pass
''', [('split_list([1, 2, 3, 4, 5], 0.4)', [[1, 2, 3], [4, 5]]), ('split_list(list(range(10)), 0.2)', [[0, 1, 2, 3, 4, 5, 6, 7], [8, 9]]), ('split_list(["a", "b"], 0.5)', [['a'], ['b']])],
         '''
def split_list(items, test_fraction):
    n_test = round(len(items) * test_fraction)
    cut = len(items) - n_test
    return (items[:cut], items[cut:])
''', 'Work out how many test items there are with round(), then slice the list at len(items) minus that number.', '<p>Taking the last part without shuffling is exactly how a time based split works: the most recent rows become the test set. A tuple and a list look the same to the checker, because both become a JSON list.</p>')
K.assign('strat', 'm', 'A stratified split by hand',
         '<p>Write <code>stratified_test_indices(labels, test_fraction)</code>. For each different label, take the positions (indices) of that label in order and put the LAST round(count &times; test_fraction) of them in the test set. Return the sorted list of test indices.</p>',
         '''
def stratified_test_indices(labels, test_fraction):
    # your code here
    pass
''', [('stratified_test_indices([0, 0, 0, 0, 1, 1], 0.5)', [2, 3, 5]), ('stratified_test_indices(["a", "b", "a", "b", "a", "b", "a", "b"], 0.25)', [6, 7]), ('stratified_test_indices([1, 1, 1], 0.0)', [])],
         '''
def stratified_test_indices(labels, test_fraction):
    positions = {}
    for i, label in enumerate(labels):
        if label not in positions:
            positions[label] = []
        positions[label].append(i)
    test = []
    for label in positions:
        places = positions[label]
        n_test = round(len(places) * test_fraction)
        if n_test > 0:
            test = test + places[-n_test:]
    return sorted(test)
''', 'Group the indices by label in a dict of lists. For each group, slice off the last part. Watch out: places[-0:] is the whole list, so skip groups with n_test = 0.', '<p>Splitting each class separately keeps its share the same in train and test. scikit-learn does the same with stratify=y, but it shuffles inside each class first.</p>')
K.assign('se', 'm', 'How sure is a test accuracy?',
         '<p>Write <code>accuracy_range(correct, total)</code> that returns a list <code>[low, high]</code>: the accuracy p = correct / total minus and plus two standard errors, where SE = &radic;(p(1 &minus; p) / total). Round both numbers to 3 decimals.</p>',
         '''
def accuracy_range(correct, total):
    # your code here
    pass
''', [('accuracy_range(90, 100)', [0.84, 0.96]), ('accuracy_range(160, 200)', [0.743, 0.857]), ('accuracy_range(50, 50)', [1.0, 1.0])],
         '''
def accuracy_range(correct, total):
    p = correct / total
    se = (p * (1 - p) / total) ** 0.5
    return [round(p - 2 * se, 3), round(p + 2 * se, 3)]
''', 'Find p first, then the standard error with ** 0.5 for the square root, then subtract and add 2 &times; SE.', '<p>When p is 1.0 the formula says there is no uncertainty, which is too confident for a small test set. Better intervals such as the Wilson interval fix this edge case.</p>')

K.must('Frame first', 'Goal, output type, data known at prediction time, metric, success level, baseline. Ask if ML is needed at all.')
K.must('Project loop', 'Frame, get data, explore and clean, split, baseline, train and tune, evaluate, deploy, monitor (CRISP-DM plus monitoring).')
K.must('Three sets', 'Train learns, validation chooses, test scores once. Stratify rare classes, split time by time, keep groups together. Fix random_state.')
K.must('Baseline', 'DummyRegressor (mean) and DummyClassifier (most frequent) set the bar every model must beat.')
K.must('Leakage', 'Never train on information unavailable at prediction time. Fit preprocessing on training data only.')
K.must('Uncertainty', 'SE of an accuracy = &radic;(p(1 &minus; p)/n). Range about p &plusmn; 2 SE. Four times the data halves the SE.')

T = K.topic(
    slug='ml-workflow', topic='ml-workflow', step=(1, 'Start here', 'ml-f1', 'What machine learning is, how a project runs from raw data to a working model, and the Python tools every ML engineer uses.', 'Beginner'),
    title='The machine learning project: from a question to a working model', short='ML project workflow', badge='1.2', minutes=55,
    lead='Walk through a whole ML project the way professionals run it: frame the problem, explore the data, split it fairly into train, validation and test sets, beat a baseline, study errors, avoid data leakage, deploy and monitor.',
    desc='problem framing, CRISP-DM, ML lifecycle, exploratory data analysis, train validation test split, stratified split, time based split, group split, random_state, baselines with DummyRegressor and DummyClassifier, error analysis, data leakage, batch and online deployment, monitoring and drift, standard error of accuracy, McNemar test.',
    summary='framing, the project stages, fair data splits, baselines, error analysis, leakage, deployment and monitoring.',
    keywords=['ML workflow', 'CRISP-DM', 'train test split', 'validation set', 'stratify', 'baseline', 'data leakage', 'deployment', 'monitoring'],
    recap='<p>Good ML work is mostly good process: a clear problem, fair splits, a baseline to beat, honest testing and watching the model after launch.</p>',
    added='2026-11-13', leet=leet_items())
