# Supervised 4.2: validation. Checked against Hastie, Tibshirani and Friedman, The Elements of Statistical Learning
# chapter 7 (7.10 cross validation, including "the wrong and the right way"), An Introduction to Statistical Learning
# chapter 5, Kohavi, A Study of Cross-Validation and Bootstrap for Accuracy Estimation and Model Selection (IJCAI 1995),
# Kaufman and others, Leakage in Data Mining (2012), Cawley and Talbot, On Over-fitting in Model Selection (JMLR 2010),
# and the scikit-learn 1.8 user guide sections 3.1 and 3.5.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-validation')
K = Kit()

K.code('three_way', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_rest, y_rest, test_size=0.25, random_state=0, stratify=y_rest)
print("train", len(X_train), " validation", len(X_val), " test", len(X_test))

best_k, best_score = None, 0.0
for k in [1, 3, 5, 9, 15, 25]:
    model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k)).fit(X_train, y_train)
    score = model.score(X_val, y_val)
    print("k", str(k).rjust(2), " validation accuracy", round(score, 3))
    if score > best_score:
        best_k, best_score = k, score
final = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=best_k)).fit(X_rest, y_rest)
print("chosen k =", best_k, " test accuracy, measured once:", round(final.score(X_test, y_test), 3))
''', long=True)

K.code('split_luck', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
single = []
for seed in range(10):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)
    single.append(DecisionTreeClassifier(random_state=0).fit(X_tr, y_tr).score(X_te, y_te))
print("10 different single splits:", [round(s, 3) for s in single])
print("lowest", round(min(single), 3), " highest", round(max(single), 3))
cv = cross_val_score(DecisionTreeClassifier(random_state=0), X, y, cv=10)
print("10 fold cross validation: mean", round(cv.mean(), 3), " standard deviation", round(cv.std(), 3))
''', long=True)

K.code('kfold_by_hand', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
folds = KFold(n_splits=5, shuffle=True, random_state=0)
scores = []
for i, (train_idx, val_idx) in enumerate(folds.split(X)):
    model.fit(X[train_idx], y[train_idx])
    s = model.score(X[val_idx], y[val_idx])
    scores.append(s)
    print("fold", i + 1, " train rows", len(train_idx), " validation rows", len(val_idx), " accuracy", round(s, 3))
print("mean", round(float(np.mean(scores)), 3), " standard deviation", round(float(np.std(scores)), 3))
print("cross_val_score gives the same:", round(cross_val_score(model, X, y, cv=folds).mean(), 3))
''', long=True)

K.code('stratified', r'''
import numpy as np
from sklearn.model_selection import KFold, StratifiedKFold

y = np.array([0] * 90 + [1] * 10)                   # sorted labels, 10% positives
X = np.zeros((100, 1))
for name, cv in [("KFold", KFold(n_splits=5)), ("StratifiedKFold", StratifiedKFold(n_splits=5))]:
    shares = [int(y[val].sum()) for _, val in cv.split(X, y)]
    print(name.ljust(16), "positives in each validation fold:", shares)
''')

K.code('groups', r'''
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, KFold, cross_val_score

rng = np.random.default_rng(1)
patients, rows_each = 40, 10
groups = np.repeat(np.arange(patients), rows_each)
person = rng.normal(size=(patients, 5))              # each patient has their own typical values
X = person[groups] + rng.normal(0, 0.3, (patients * rows_each, 5))
y = rng.integers(0, 2, patients)[groups]             # the label belongs to the patient and is random

model = RandomForestClassifier(n_estimators=100, random_state=0)
mixed = cross_val_score(model, X, y, cv=KFold(5, shuffle=True, random_state=0)).mean()
grouped = cross_val_score(model, X, y, cv=GroupKFold(5), groups=groups).mean()
print("KFold, same patient in train and validation:", round(mixed, 3))
print("GroupKFold, each patient in one fold only:   ", round(grouped, 3))
''')

K.code('time_split', r'''
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

days = np.arange(12)
for i, (train, val) in enumerate(TimeSeriesSplit(n_splits=4).split(days)):
    print("split", i + 1, " train on days", train.tolist(), " validate on days", val.tolist())
''')

K.code('leakage', r'''
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 5000))                    # pure noise
y = rng.integers(0, 2, 100)                         # random labels: nothing to learn

X_leaky = SelectKBest(f_classif, k=20).fit_transform(X, y)      # chose features using ALL rows
wrong = cross_val_score(LogisticRegression(max_iter=1000), X_leaky, y, cv=5).mean()
pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))
right = cross_val_score(pipe, X, y, cv=5).mean()
print("selection before cross validation (leak):", round(wrong, 3))
print("selection inside a pipeline (honest):   ", round(right, 3))
''')

K.code('learning_curve', r'''
from sklearn.datasets import load_digits
from sklearn.model_selection import learning_curve
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

X, y = load_digits(return_X_y=True)
for name, model in [("naive Bayes", GaussianNB()), ("RBF SVM", SVC(gamma=0.001))]:
    sizes, train, val = learning_curve(model, X, y, train_sizes=[0.05, 0.2, 0.5, 1.0], cv=5, shuffle=True, random_state=0)
    print(name)
    for n, t, v in zip(sizes, train.mean(axis=1), val.mean(axis=1)):
        print("   training rows", str(n).rjust(4), " train", round(float(t), 3), " validation", round(float(v), 3))
''', long=True)

K.lesson('idea', 'Train, validation and test sets', f'''
{src('The Elements of Statistical Learning chapter 7, An Introduction to Statistical Learning chapter 5, Kohavi (1995), Kaufman and others, Leakage in Data Mining (2012), Cawley and Talbot (2010), and the scikit-learn 1.8 user guide sections 3.1 and 3.5.')}
{wwh('Split the data into three parts with three jobs. The <b>training set</b> fits the model. The <b>validation set</b> compares models and settings. The <b>test set</b> is touched once, at the very end, to report how the chosen model will do on new data.',
     'Every time you look at a score and change something, that data starts to shape the model. A test set used for choices is no longer an honest estimate, and the reported score will be too good. Keeping one set locked away is the only way to know how the model will really perform.',
     'Use train_test_split twice: first split off the test set (often 20%), then split the rest into training and validation. Stratify by the label for classification. After choosing, retrain on training plus validation and score the test set once.')}
{run('three_way')}
{note('Three different values of k tie at 0.982 on just 114 validation rows, and the rule "take the first best" picks k = 1, the most fragile choice. A single small validation set is too noisy to choose reliably. Cross validation, next, uses every row for validation once.', 'exam')}
{scene('a driving test', '<p>A learner driver practises on many roads (training), takes mock tests with an instructor to decide whether they are ready (validation), and then sits the real test on a route they have never driven (test). If the learner practised on the exact test route, passing it would prove very little.</p>')}
''', kw=['train test split', 'validation set', 'test set', 'holdout', 'model selection', 'stratify'])

K.lesson('cv', 'K fold cross validation', f'''
{viz('mlkfold')}
{wwh('<b>K fold cross validation</b> splits the data into k equal folds. Each fold takes one turn as the validation set while the other k &minus; 1 folds train the model. The k scores are averaged.',
     'One split gives one noisy number that depends on which rows happened to land in the test set. Cross validation uses every row for validation once, so the mean is more stable, and the spread of the fold scores shows how much to trust it.',
     'cross_val_score(model, X, y, cv=5) does it in one line. Use 5 or 10 folds. For classifiers an integer cv uses StratifiedKFold automatically. Shuffle with KFold(shuffle=True, random_state=0) when rows are sorted.')}
{run('split_luck')}
{note('The same decision tree scores anywhere from 0.904 to 0.956 depending only on the random split. Reporting one of those numbers could flatter or punish the model by 5 points. Ten fold cross validation gives 0.917 with a standard deviation of 0.033, an honest picture of both the level and the uncertainty.', 'tip')}
{run('kfold_by_hand')}
{fx('Cross validation estimate', 'CV = (1/k) &Sigma;<sub>i=1</sub><sup>k</sup> score(model trained without fold i, fold i)', 'Report the mean and the standard deviation.', key=True)}
''', kw=['k fold cross validation', 'cross_val_score', 'KFold', 'fold', 'variance of the estimate', 'shuffle'])

K.lesson('splitters', 'Stratified, grouped and time ordered splits', f'''
{wwh('The right splitter depends on how the data was collected. <b>StratifiedKFold</b> keeps the class balance in every fold. <b>GroupKFold</b> keeps all rows of one group (a patient, a user, a device) in the same fold. <b>TimeSeriesSplit</b> always trains on the past and validates on the future.',
     'Cross validation must copy the situation the model will face. A new patient has never been seen, so no row of theirs may be in training. Tomorrow’s data comes after today’s, so validating on the past with a model trained on the future is cheating.',
     'Pick the splitter by asking: will new data contain new groups? Is there an order in time? Is one class rare? Then pass it as cv=, and pass groups= for group splitters.')}
{run('stratified')}
{run('groups')}
{note('Each patient’s label is random, so there is nothing real to learn. With plain KFold the forest scores 0.88 because it recognises the patients from their other rows. GroupKFold reveals the truth: 0.535, close to guessing. This mistake appears in published medical studies.', 'exam')}
{run('time_split')}
''', kw=['StratifiedKFold', 'GroupKFold', 'TimeSeriesSplit', 'grouped data', 'time series validation', 'class balance'])

K.lesson('leakage', 'Data leakage: the silent killer', f'''
{wwh('<b>Data leakage</b> happens when information that will not be available at prediction time, or information from the validation rows, sneaks into training. The scores look great and the model fails in real use.',
     'Leakage is the most common reason a model that scored well in the lab fails in production. Typical causes: scaling or selecting features on all the data before splitting, a feature computed from the target, duplicates across splits, and future information in time series.',
     'Put every step that learns from data (imputation, scaling, encoding, feature selection, resampling) inside a Pipeline, and cross validate the whole pipeline. Then each fold learns those steps from its own training rows only.')}
{run('leakage')}
{note('The data is pure noise with random labels, so the honest answer is about 0.5. Choosing the 20 best of 5,000 features on all rows, and only then cross validating, reports 0.85. Doing the same selection inside a pipeline gives 0.48. This exact error is the "wrong way" to do cross validation in The Elements of Statistical Learning, section 7.10.2.', 'exam')}
{table(['Leak', 'Example', 'Fix'], [
    ['Preprocessing on all data', 'StandardScaler or SelectKBest fit before the split', 'Put it in a Pipeline'],
    ['Target leakage', 'A "refund issued" column when predicting fraud', 'Drop features not known at prediction time'],
    ['Group leakage', 'Same patient in train and test', 'GroupKFold'],
    ['Time leakage', 'Using next month’s values', 'TimeSeriesSplit, features from the past only'],
    ['Duplicates', 'The same row in train and test', 'Remove duplicates before splitting']])}
''', kw=['data leakage', 'target leakage', 'Pipeline', 'feature selection leak', 'preprocessing inside cross validation'])

K.lesson('curves', 'Learning curves: will more data help?', f'''
{viz('mllearncurve')}
{wwh('A <b>learning curve</b> plots training and validation scores against the number of training rows.',
     'Collecting data is expensive. The learning curve tells you whether it is worth it. If both curves have flattened at a poor score (high bias), more data will not help, but a more flexible model will. If there is a big gap that is still closing (high variance), more data or more regularisation will help.',
     'sklearn.model_selection.learning_curve(model, X, y, train_sizes=..., cv=5) returns the sizes and the train and validation scores for each fold.')}
{run('learning_curve')}
{note('Naive Bayes stops improving at about 0.81 on validation and its training score falls to 0.87: the curves meet at a low level, a high bias model, so more digits will not help. The RBF SVM still gains from 0.961 to 0.972 as the data doubles, with training at 1.0: more data keeps paying off.', 'tip')}
''', kw=['learning curve', 'high bias', 'high variance', 'more data', 'learning_curve', 'diagnosis'])

K.lesson('versus', 'Validation methods compared', f'''
{versus('How to estimate performance', ['Method', 'Good for', 'Watch out'], [
    ['Single holdout split', 'Big data, quick checks', 'Noisy on small data'],
    ['K fold (k = 5 or 10)', 'Most tabular problems', 'Shuffle sorted data, k times the cost'],
    ['Stratified k fold', 'Classification, rare classes', 'Default for classifiers'],
    ['Group k fold', 'Repeated rows per person or device', 'Needs a groups array'],
    ['Time series split', 'Forecasting, anything ordered in time', 'Fewer, smaller early training sets'],
    ['Leave one out', 'Very small data', 'n fits, high variance estimate'],
    ['Nested cross validation', 'Honest score after tuning', 'k<sub>outer</sub> &times; k<sub>inner</sub> &times; grid fits']],
    'use stratified 5 fold by default, and switch splitter whenever groups or time order exist.')}
''', kw=['holdout vs cross validation', 'leave one out', 'nested cross validation', 'choosing a validation method'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('K fold estimate', 'CV<sub>k</sub> = (1/k) &Sigma;<sub>i</sub> E<sub>i</sub>', 'E<sub>i</sub> is the score on fold i.', key=True),
     fx('Standard error of the mean', 'SE = s / &radic;k', 'Rough, since folds share training rows.', key=True),
     fx('Fold size', 'n / k rows validate, n(k &minus; 1)/k train', '5 fold: 80% train, 20% validate.', key=True),
     fx('Fits for a grid search', 'k &times; (number of settings) + 1 refit', 'Grows fast with every new parameter.', key=True))}
{steps('Worked example: mean and spread of five folds', [
    'Fold accuracies: 0.90, 0.80, 0.85, 0.95, 0.90.',
    'Mean = 4.40 / 5 = 0.88.',
    'Deviations: 0.02, &minus;0.08, &minus;0.03, 0.07, 0.02. Squares add to 0.013.',
    eq('standard deviation = &radic;(0.013 / 5) = 0.051'),
    'Report 0.88 &plusmn; 0.05. A rival at 0.89 is not clearly better.'])}
{deep('The bias and variance of cross validation itself', '<p>Each fold model trains on only (k &minus; 1)/k of the data, so cross validation slightly underestimates the performance of the final model trained on everything: a pessimistic bias that shrinks as k grows. Leave one out (k = n) has almost no bias, but its n training sets overlap almost completely, so the fold errors are highly correlated and the estimate has high variance (Kohavi, 1995, recommends stratified 10 fold). There is no unbiased estimator of the variance of k fold cross validation (Bengio and Grandvalet, 2004), so the &plusmn; from the fold standard deviation is only a guide. Finally, if you pick the best of many models by their cross validation scores, the winning score is optimistically biased, the winner’s curse described by Cawley and Talbot (2010). Nested cross validation, in the next chapter, fixes that.</p>')}
''', kw=['cross validation formula', 'standard error', 'fold size', 'grid search cost', 'bias of cross validation', 'winner curse'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Hide some data from the model and test on it, because a model always looks better on the data it learned from.</p>',
    '<p>Use train, validation and test splits, run cross_val_score with the right splitter, put preprocessing inside a Pipeline, and read learning curves.</p>',
    '<p>Spot leakage of every kind, choose between stratified, grouped and time series splits, and explain the bias and variance of cross validation estimates.</p>',
    '<p>Study nested cross validation, corrected resampled t tests for comparing models (Nadeau and Bengio, 2003), blocked and purged splits for financial time series, adversarial validation for train and test drift, and conformal prediction for honest prediction intervals.</p>')}
{grow('Keep a test set the model never sees.',
      'Cross validate pipelines with the right splitter.',
      'Analyse estimator bias, variance and leakage.')}
''', kw=['beginner', 'expert', 'nested cross validation', 'corrected t test', 'adversarial validation'])

lc(1013, 'Partition Array Into Three Parts With Equal Sum', 'partition-array-into-three-parts-with-equal-sum', 'e', 'Cut whenever a third of the total is reached', 'The total must split into three equal thirds. Walk through, adding to a running sum, and cut each time it reaches one third. Like making folds, you split the data into equal parts in order.', r'''
def can_three_parts_equal_sum(arr):
    total = sum(arr)
    if total % 3 != 0:
        return False
    target = total // 3
    running = 0
    parts = 0
    for x in arr:
        running = running + x
        if running == target:
            parts = parts + 1
            running = 0
    return parts >= 3
''', [('can_three_parts_equal_sum([0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1])', True), ('can_three_parts_equal_sum([0, 2, 1, -6, 6, 7, 9, -1, 2, 0, 1])', False)])
lc(189, 'Rotate Array', 'rotate-array', 'm', 'Slice the last k to the front', 'Rotating right by k moves the last k values to the front. Take k modulo the length first. Rotating which fold is held out is the heart of cross validation.', r'''
def rotate(nums, k):
    k = k % len(nums)
    nums[:] = nums[-k:] + nums[:-k] if k else nums
    return nums
''', [('rotate([1, 2, 3, 4, 5, 6, 7], 3)', [5, 6, 7, 1, 2, 3, 4]), ('rotate([-1, -100, 3, 99], 2)', [3, 99, -1, -100])])
lc(1652, 'Defuse the Bomb', 'defuse-the-bomb', 'e', 'A window that wraps around', 'For k &gt; 0 sum the next k values, for k &lt; 0 the previous |k|, wrapping around the end with the modulo operator, and 0 for k = 0.', r'''
def decrypt(code, k):
    n = len(code)
    out = []
    for i in range(n):
        if k > 0:
            out.append(sum(code[(i + j) % n] for j in range(1, k + 1)))
        elif k < 0:
            out.append(sum(code[(i - j) % n] for j in range(1, -k + 1)))
        else:
            out.append(0)
    return out
''', [('decrypt([5, 7, 1, 4], 3)', [12, 10, 16, 13]), ('decrypt([2, 4, 9, 3], -2)', [12, 5, 6, 13])])
lc(1343, 'Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold', 'number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold', 'm', 'Slide a fixed window', 'Keep the sum of the current window of k values. Slide it one step by adding the new value and removing the oldest. Compare the sum with k times the threshold.', r'''
def num_of_subarrays(arr, k, threshold):
    window = sum(arr[:k])
    count = 1 if window >= k * threshold else 0
    for i in range(k, len(arr)):
        window = window + arr[i] - arr[i - k]
        if window >= k * threshold:
            count = count + 1
    return count
''', [('num_of_subarrays([2, 2, 2, 2, 5, 5, 5, 8], 3, 4)', 3), ('num_of_subarrays([11, 13, 17, 23, 29, 31, 7, 5, 2, 3], 3, 5)', 6)])
lc(2090, 'K Radius Subarray Averages', 'k-radius-subarray-averages', 'm', 'A centred sliding window', 'Each answer is the average of the 2k + 1 values centred on that position, or &minus;1 if the window does not fit. Slide the window sum as in the last problem and use integer division.', r'''
def get_averages(nums, k):
    n = len(nums)
    size = 2 * k + 1
    out = [-1] * n
    if size > n:
        return out
    window = sum(nums[:size])
    out[k] = window // size
    for i in range(size, n):
        window = window + nums[i] - nums[i - size]
        out[i - k] = window // size
    return out
''', [('get_averages([7, 4, 3, 9, 1, 8, 5, 2, 6], 3)', [-1, -1, -1, 5, 4, 4, -1, -1, -1]), ('get_averages([100000], 0)', [100000])])
lc(1876, 'Substrings of Size Three with Distinct Characters', 'substrings-of-size-three-with-distinct-characters', 'e', 'Check every window of three', 'Look at every window of three letters and count those whose three letters are all different.', r'''
def count_good_substrings(s):
    count = 0
    for i in range(len(s) - 2):
        if len(set(s[i:i + 3])) == 3:
            count = count + 1
    return count
''', [('count_good_substrings("xyzzaz")', 1), ('count_good_substrings("aababcabc")', 4)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Cross validation is careful slicing of data. These problems practise splitting an array into equal parts, rotating which part comes first, windows that wrap around, fixed sliding windows, centred windows, and checking every window. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'sliding window', 'partition', 'rotation', 'prefix sum'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Train</b> fits, <b>validation</b> chooses, <b>test</b> reports once at the end.',
    'One split is noisy. <b>K fold cross validation</b> averages k scores and shows their spread.',
    'Pick the splitter from the data: <b>StratifiedKFold</b> for classes, <b>GroupKFold</b> for repeated groups, <b>TimeSeriesSplit</b> for time.',
    '<b>Leakage</b> makes scores too good. Fit every preprocessing step inside a <b>Pipeline</b>.',
    '<b>Learning curves</b> tell whether more data (high variance) or a better model (high bias) will help.',
    'Choosing the best of many models by CV score is itself optimistic. Nested CV fixes it.'],
    'Supervised 4.3 tunes hyperparameters with grid and random search, uses nested cross validation, and calibrates probabilities.')}
{files('Three tasks: k fold indices, the mean and spread of fold scores, and time series splits.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'The test set should be used', ['To choose hyperparameters', 'Once, at the end, to report performance', 'For training', 'Every time you change the model'], 1, 'Locked away.', 'Using it for choices makes the estimate optimistic.')
K.quiz('e', 'In 5 fold cross validation each row is used for validation', ['Never', 'Once', 'Five times', 'Twice'], 1, 'Each fold takes one turn.', 'Every row lands in exactly one validation fold.')
K.quiz('e', 'Which splitter keeps the class balance in every fold?', ['KFold', 'StratifiedKFold', 'TimeSeriesSplit', 'GroupKFold'], 1, 'Strata.', 'It preserves the label proportions.')
K.quiz('e', 'For a forecasting model you should use', ['Shuffled KFold', 'TimeSeriesSplit', 'Leave one out', 'Random split'], 1, 'No peeking at the future.', 'Train on the past, validate on the future.')
K.quiz('m', 'Fitting StandardScaler on all data before cross validation is', ['Fine', 'A form of leakage', 'Required', 'Faster and more accurate'], 1, 'Validation rows influence training.', 'Put the scaler in a Pipeline.')
K.quiz('m', 'Several rows per patient. To estimate performance on new patients use', ['KFold', 'GroupKFold with patient ids', 'StratifiedKFold', 'A single split by row'], 1, 'Groups.', 'All rows of a patient must stay in one fold.')
K.quiz('m', 'Both training and validation errors are high and close. More data will', ['Help a lot', 'Help little: the model has high bias', 'Cause overfitting', 'Lower the training error'], 1, 'Curves have met.', 'Use a more flexible model or better features.')
K.quiz('m', 'Training error is low, validation error high, and the gap shrinks as data grows. Best next step', ['A simpler model always', 'Get more data or regularise', 'Remove the validation set', 'Raise the learning rate'], 1, 'High variance.', 'More data narrows the gap.')
K.quiz('m', 'cross_val_score with cv=5 on a classifier uses', ['KFold without shuffling', 'StratifiedKFold', 'TimeSeriesSplit', 'Leave one out'], 1, 'scikit-learn default.', 'An integer cv gives StratifiedKFold for classifiers.')
K.quiz('h', 'Selecting the top features on all rows, then cross validating, on random data gives', ['About 50%', 'Far above 50%, a leak', 'Exactly 0%', 'An error'], 1, 'The selection saw the labels.', 'The wrong way of ESL 7.10.2.')
K.quiz('h', 'Compared with 10 fold, leave one out cross validation has', ['Higher bias, lower variance', 'Lower bias, higher variance', 'Both lower', 'Both higher'], 1, 'Nearly identical training sets.', 'Highly correlated fold errors raise the variance.')
K.quiz('h', 'Reporting the best of 50 models’ CV scores as the final score is', ['Unbiased', 'Optimistic (winner’s curse)', 'Pessimistic', 'Required'], 1, 'Selection on noise.', 'Use a test set or nested cross validation.')
K.quiz('x', 'In the style of a Stanford CS229 exam: k fold CV slightly underestimates the final model’s accuracy because', ['Folds are too small to validate', 'Each fold model trains on only (k &minus; 1)/k of the data', 'It uses the test set', 'Shuffling adds noise'], 1, 'Less training data.', 'The bias shrinks as k grows.')
K.quiz('x', 'In the style of a CMU 10-701 exam: what can make k fold CV give too optimistic a score even with a Pipeline?', ['Using k = 10', 'Rows that are near duplicates or from the same group split across folds', 'Stratification', 'Standard scaling'], 1, 'Hidden dependence.', 'Independence between folds is assumed. Group or time structure breaks it.')

K.calc('e', '1,000 rows, 5 fold CV. Rows in each validation fold?', '200', 'n / k.', ['n = 1,000.', 'k = 5.', eq('1,000 / 5 = 200')], check=200)
K.calc('e', 'Same setup. Rows used for training in each fold?', '800', 'n &minus; n/k.', ['Validation 200.', '1,000 &minus; 200.', eq('800')], check=800)
K.calc('e', '5,000 rows split 60/20/20. Test rows?', '1000', '20%.', ['0.2 &times; 5,000.', '= 1,000.', eq('1,000')], check=1000)
K.calc('m', 'Fold scores 0.90, 0.80, 0.85, 0.95, 0.90. Mean?', '0.88', 'Average.', ['Sum 4.40.', '5 folds.', eq('0.88')], check=0.88)
K.calc('m', 'Same scores. Standard deviation (divide by 5), 3 decimals?', '0.051', '&radic;(mean squared deviation).', ['Squared deviations add to 0.013.', '0.013 / 5 = 0.0026.', eq('&radic;0.0026 = 0.051')], check=0.051)
K.calc('m', 'Leave one out on 100 rows. Number of model fits?', '100', 'One per row.', ['Each row is held out once.', '100 rows.', eq('100 fits')], check=100)
K.calc('m', '5 fold CV repeated 3 times. Number of fits?', '15', 'k &times; repeats.', ['5 per repeat.', '3 repeats.', eq('15')], check=15)
K.calc('h', 'Grid of 4 &times; 5 settings with 5 fold CV. Fits before the final refit?', '100', 'settings &times; k.', ['20 settings.', '5 folds each.', eq('100')], check=100)
K.calc('h', '10 folds with standard deviation 0.03. Standard error of the mean, 4 decimals?', '0.0095', 's / &radic;k.', ['&radic;10 = 3.162.', '0.03 / 3.162.', eq('0.0095')], check=0.0095)
K.calc('x', 'In the style of an MIT 6.036 problem: TimeSeriesSplit with 12 rows and 4 splits uses test blocks of 12 // 5 = 2 rows. Size of the first training block?', '4', 'n &minus; splits &times; block.', ['4 &times; 2 = 8 rows are test blocks.', '12 &minus; 8.', eq('4')], check=4)

K.assign('kfold', 'm', 'K fold indices',
         '<p>Write <code>kfold_indices(n, k)</code> that returns the validation indices of each fold, in order, without shuffling. The first n % k folds get one extra row, as in scikit-learn.</p>',
         '''
def kfold_indices(n, k):
    # your code here
    pass
''', [('kfold_indices(10, 3)', [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]), ('kfold_indices(4, 4)', [[0], [1], [2], [3]]), ('kfold_indices(7, 2)', [[0, 1, 2, 3], [4, 5, 6]])],
         '''
def kfold_indices(n, k):
    folds = []
    start = 0
    for i in range(k):
        size = n // k + (1 if i < n % k else 0)
        folds.append(list(range(start, start + size)))
        start = start + size
    return folds
''', 'Each fold has n // k rows, plus one for the first n % k folds.', '<p>Shuffle the rows first when they are sorted, or the folds will be lopsided.</p>')
K.assign('cvstats', 'e', 'Mean and spread of fold scores',
         '<p>Write <code>cv_summary(scores)</code> that returns (mean, standard deviation) of the fold scores, dividing by the number of folds, each rounded to 4 decimals.</p>',
         '''
import math


def cv_summary(scores):
    # your code here
    pass
''', [('cv_summary([0.9, 0.8, 0.85, 0.95, 0.9])', (0.88, 0.051)), ('cv_summary([1.0, 1.0])', (1.0, 0.0)), ('cv_summary([0.5, 0.7])', (0.6, 0.1))],
         '''
import math


def cv_summary(scores):
    k = len(scores)
    mean = sum(scores) / k
    var = sum((s - mean) ** 2 for s in scores) / k
    return (round(mean, 4), round(math.sqrt(var), 4))
''', 'Mean first, then the average squared deviation, then its square root.', '<p>This matches numpy.std, which divides by k by default.</p>')
K.assign('tsplit', 'h', 'Time series splits',
         '<p>Write <code>time_splits(n, n_splits)</code> that returns a list of (train_end, val_end) pairs like TimeSeriesSplit. Each validation block has n // (n_splits + 1) rows. Split i (from 1) trains on rows 0 to train_end and validates on train_end to val_end, with train_end = n &minus; (n_splits &minus; i + 1) &times; block.</p>',
         '''
def time_splits(n, n_splits):
    # your code here
    pass
''', [('time_splits(12, 4)', [(4, 6), (6, 8), (8, 10), (10, 12)]), ('time_splits(10, 4)', [(2, 4), (4, 6), (6, 8), (8, 10)]), ('time_splits(6, 2)', [(2, 4), (4, 6)])],
         '''
def time_splits(n, n_splits):
    block = n // (n_splits + 1)
    out = []
    for i in range(1, n_splits + 1):
        train_end = n - (n_splits - i + 1) * block
        out.append((train_end, train_end + block))
    return out
''', 'Compute the block size once, then the end of each training part.', '<p>The first test matches the program’s TimeSeriesSplit output: train on days 0 to 3, validate on days 4 and 5.</p>')

K.must('Splits', 'Train fits, validation chooses, test reports once. Stratify classes. Retrain on train + validation at the end.')
K.must('Cross validation', 'k folds, each validates once. cross_val_score(model, X, y, cv=5). Report mean &plusmn; std. Shuffle sorted rows.')
K.must('Splitters', 'StratifiedKFold (classes), GroupKFold (groups=), TimeSeriesSplit (time), LeaveOneOut (tiny data).')
K.must('Leakage', 'Preprocessing on all data, target leaks, group and time leaks, duplicates. Fix: Pipeline, right splitter, drop future features.')
K.must('Learning curves', 'High bias: curves meet low, get a better model. High variance: gap closing, get more data or regularise.')
K.must('Selection bias', 'Best of many CV scores is optimistic. Use a locked test set or nested CV.')

T = K.topic(
    slug='ml-validation', topic='ml-validation', step=(4, 'Evaluate and improve', 'ml-s4', 'Measure models honestly, estimate how they will do on new data, and tune them without fooling yourself.', 'Intermediate'),
    title='Validation: honest estimates of performance', short='Validation', badge='4.2', minutes=55,
    lead='Learn to estimate how a model will do on new data: train, validation and test sets, k fold cross validation, stratified, grouped and time series splits, data leakage and pipelines, and learning curves.',
    desc='train test split, validation set, test set, holdout, k fold cross validation, cross_val_score, KFold, StratifiedKFold, GroupKFold, TimeSeriesSplit, leave one out, data leakage, target leakage, Pipeline, learning curve, high bias, high variance, winner curse.',
    summary='Three way splits, k fold cross validation, the right splitter for groups and time, leakage, and learning curves.',
    keywords=['cross validation', 'k fold', 'train test split', 'StratifiedKFold', 'GroupKFold', 'TimeSeriesSplit', 'data leakage', 'learning curve', 'Pipeline', 'validation set'],
    recap='<p>Score the model the way it will be used: on rows, people and time it has never seen, with every learning step inside the folds.</p>',
    added='2026-11-13', leet=leet_items())
