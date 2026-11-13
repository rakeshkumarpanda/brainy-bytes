# Supervised 4.3: tuning and calibration. Checked against Bergstra and Bengio, Random Search for Hyper-Parameter
# Optimization (JMLR 2012), Jamieson and Talwalkar (2016) and Li and others, Hyperband (JMLR 2018) for successive
# halving, Cawley and Talbot (JMLR 2010) for nested cross validation, Platt (1999), Zadrozny and Elkan (2002) and
# Niculescu-Mizil and Caruana, Predicting Good Probabilities with Supervised Learning (ICML 2005), Guo and others,
# On Calibration of Modern Neural Networks (ICML 2017), and the scikit-learn 1.8 user guide sections 3.2, 3.3 and 1.16.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-tuning')
K = Kit()

K.code('validation_curve', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import validation_curve
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
depths = [1, 2, 3, 4, 6, 10]
train, val = validation_curve(DecisionTreeClassifier(random_state=0), X, y, param_name="max_depth", param_range=depths, cv=5)
for d, t, v in zip(depths, train.mean(axis=1), val.mean(axis=1)):
    print("max_depth", str(d).rjust(2), " train", round(float(t), 3), " validation", round(float(v), 3))
''')

K.code('grid_search', r'''
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
pipe = make_pipeline(StandardScaler(), SVC())
grid = {"svc__C": [0.1, 1, 10, 100], "svc__gamma": [0.001, 0.01, 0.1]}
search = GridSearchCV(pipe, grid, cv=5).fit(X, y)
print("settings tried:", len(search.cv_results_["params"]), " fits:", len(search.cv_results_["params"]) * 5)
print("best:", search.best_params_, " score", round(search.best_score_, 3))
table = pd.DataFrame(search.cv_results_)[["param_svc__C", "param_svc__gamma", "mean_test_score", "rank_test_score"]]
print(table.sort_values("rank_test_score", kind="stable").head(4).round(3).to_string(index=False))
''')

K.code('random_search', r'''
from scipy.stats import loguniform
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
pipe = make_pipeline(StandardScaler(), SVC())
space = {"svc__C": loguniform(0.01, 1000), "svc__gamma": loguniform(0.0001, 1)}
search = RandomizedSearchCV(pipe, space, n_iter=12, cv=5, random_state=0).fit(X, y)
best = search.best_params_
print("12 random settings, best C =", round(best["svc__C"], 2), " gamma =", round(best["svc__gamma"], 5))
print("best cross validated accuracy:", round(search.best_score_, 3))
''')

K.code('nested_cv', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
X, y = X[:150], y[:150]                              # a small dataset makes the optimism visible
pipe = make_pipeline(StandardScaler(), SVC())
grid = {"svc__C": [0.01, 0.1, 1, 10, 100, 1000], "svc__gamma": [0.0001, 0.001, 0.01, 0.1, 1]}
inner = KFold(5, shuffle=True, random_state=1)
outer = KFold(5, shuffle=True, random_state=2)
search = GridSearchCV(pipe, grid, cv=inner).fit(X, y)
print("best inner score (used to choose):", round(search.best_score_, 3))
nested = cross_val_score(GridSearchCV(pipe, grid, cv=inner), X, y, cv=outer)
print("nested cross validation score:   ", round(nested.mean(), 3))
''')

K.code('calibration', r'''
import numpy as np
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.datasets import make_classification
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

X, y = make_classification(n_samples=6000, n_features=20, n_informative=4, n_redundant=10, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0)
raw = GaussianNB().fit(X_train, y_train)
cal = CalibratedClassifierCV(GaussianNB(), method="isotonic", cv=5).fit(X_train, y_train)
for name, model in [("naive Bayes", raw), ("calibrated", cal)]:
    p = model.predict_proba(X_test)[:, 1]
    frac, mean = calibration_curve(y_test, p, n_bins=5)
    print(name.ljust(11), "Brier", round(brier_score_loss(y_test, p), 4))
    print("   predicted", np.round(mean, 2).tolist())
    print("   observed ", np.round(frac, 2).tolist())
''')

K.code('class_weight', r'''
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=5000, n_features=10, n_informative=3, weights=[0.95], flip_y=0.01, random_state=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0, stratify=y)
for cw in [None, "balanced"]:
    pred = LogisticRegression(class_weight=cw, max_iter=1000).fit(X_train, y_train).predict(X_test)
    print("class_weight", str(cw).ljust(8), " recall", round(recall_score(y_test, pred), 3), " precision", round(precision_score(y_test, pred), 3))
''', long=True)

K.code('tuned_threshold', r'''
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import TunedThresholdClassifierCV, train_test_split

X, y = make_classification(n_samples=5000, n_features=10, n_informative=3, weights=[0.95], flip_y=0.01, random_state=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0, stratify=y)
base = LogisticRegression(max_iter=1000).fit(X_train, y_train)
tuned = TunedThresholdClassifierCV(LogisticRegression(max_iter=1000), scoring="f1", cv=5).fit(X_train, y_train)
print("threshold 0.5:", " F1", round(f1_score(y_test, base.predict(X_test)), 3))
print("tuned threshold", round(float(tuned.best_threshold_), 3), " F1", round(f1_score(y_test, tuned.predict(X_test)), 3))
''')

K.lesson('idea', 'Parameters and hyperparameters', f'''
{src('Bergstra and Bengio (2012), Li and others, Hyperband (2018), Cawley and Talbot (2010), Platt (1999), Zadrozny and Elkan (2002), Niculescu-Mizil and Caruana (2005), Guo and others (2017), and the scikit-learn 1.8 user guide sections 3.2, 3.3 and 1.16.')}
{wwh('<b>Parameters</b> are learned from the data during fit, such as the weights of a linear model or the splits of a tree. <b>Hyperparameters</b> are chosen by you before training, such as C and gamma for an SVM, max_depth for a tree, or the learning rate for boosting.',
     'The same algorithm can underfit or overfit badly depending on its hyperparameters. Tuning them with validation, not by guessing or by looking at the test set, is often worth more accuracy than switching algorithms.',
     'Sweep one hyperparameter and plot the training and validation scores (a <b>validation curve</b>) to see where underfitting turns into overfitting. Then search several at once with GridSearchCV or RandomizedSearchCV, always inside cross validation.')}
{run('validation_curve')}
{note('Training accuracy climbs to 1.0 as the tree deepens, but validation accuracy peaks at depth 2 (0.928) and then slips. To the left of the peak the tree underfits, to the right it overfits. The validation curve shows exactly where to stop.', 'tip')}
{scene('tuning a guitar', '<p>The strings of a guitar are its parameters: they vibrate on their own when played. The tuning pegs are the hyperparameters: you set them before you play, by ear, and a small turn changes everything that follows. You tune by listening to how it sounds, not by reading the notes off the sheet music you will perform.</p>')}
''', kw=['hyperparameter', 'parameter', 'validation curve', 'underfitting', 'overfitting', 'model complexity'])

K.lesson('search', 'Grid search and random search', f'''
{viz('mlgridrandom')}
{wwh('<b>Grid search</b> tries every combination of listed values. <b>Random search</b> draws a fixed number of combinations at random from ranges or distributions you give.',
     'A grid grows exponentially: 5 values for each of 4 hyperparameters is 625 settings, times the number of folds. Usually only one or two hyperparameters really matter, and random search tests many more distinct values of each for the same budget (Bergstra and Bengio, 2012).',
     'GridSearchCV(pipe, param_grid, cv=5) and RandomizedSearchCV(pipe, distributions, n_iter=50, cv=5). Name pipeline steps with a double underscore, such as svc__C. Search scale parameters like C, gamma, alpha and learning rate on a log scale with scipy.stats.loguniform.')}
{run('grid_search')}
{run('random_search')}
{note('The grid tried 12 settings (60 fits) and found 0.979. Random search with the same number of settings over wide log ranges found C = 10.3 and gamma = 0.015, scoring 0.981, values a coarse grid could never hit. After the search, best_estimator_ is already refitted on all the data you passed.', 'exam')}
''', kw=['GridSearchCV', 'RandomizedSearchCV', 'param_grid', 'loguniform', 'log scale', 'random search', 'Bergstra Bengio'])

K.lesson('smart', 'Smarter searches: halving and Bayesian optimisation', f'''
{wwh('<b>Successive halving</b> starts many candidates on a small budget (few rows or few trees), keeps the best third, gives them more budget, and repeats. <b>Bayesian optimisation</b> fits a model of the score as a function of the hyperparameters and picks the next setting where it expects the most improvement.',
     'Most candidates are obviously bad after a little training, so spending the full budget on each is wasteful. These methods reach the same quality with far fewer full fits, which matters for big data and deep learning.',
     'scikit-learn offers HalvingGridSearchCV and HalvingRandomSearchCV (import sklearn.experimental.enable_halving_search_cv first). Optuna and scikit-optimize provide Bayesian optimisation with tree structured Parzen estimators or Gaussian processes, plus pruning of bad trials.')}
{table(['Method', 'Idea', 'Best when'], [
    ['Grid search', 'Every combination', '1 or 2 hyperparameters, few values'],
    ['Random search', 'Random combinations', 'Several hyperparameters, a fixed budget'],
    ['Successive halving, Hyperband', 'Small budget for many, big budget for the best', 'Expensive models where early results predict final ones'],
    ['Bayesian optimisation (Optuna)', 'A model of score versus settings picks the next try', 'Each fit is expensive, up to about 20 hyperparameters']])}
{fx('Successive halving', 'n candidates &rarr; n/&eta; &rarr; n/&eta;<sup>2</sup> ..., budget &times; &eta; each round', 'With &eta; = 3, 81 candidates need 5 rounds to reach 1.', key=True)}
''', kw=['successive halving', 'Hyperband', 'HalvingRandomSearchCV', 'Bayesian optimisation', 'Optuna', 'TPE'])

K.lesson('nested', 'Nested cross validation', f'''
{wwh('<b>Nested cross validation</b> wraps the whole tuning procedure inside an outer cross validation. The inner loop chooses the hyperparameters, and the outer loop scores that choice on folds it never saw.',
     'The best inner score is optimistic: you picked the maximum of many noisy scores, so part of its height is luck. If you report it as your expected performance, you will be disappointed later. Nested cross validation measures the whole recipe "tune, then train" honestly.',
     'cross_val_score(GridSearchCV(pipe, grid, cv=inner), X, y, cv=outer). It costs outer folds &times; inner folds &times; settings fits. Use it to report performance, then run the plain search once on all data to get the final model.')}
{run('nested_cv')}
{note('On 150 rows with 30 settings, the best inner score is 0.953 but the nested estimate is 0.933. Two points of the inner score were the luck of picking the best of 30. With a locked test set you would see the same drop.', 'exam')}
''', kw=['nested cross validation', 'optimistic bias', 'winner curse', 'inner loop', 'outer loop', 'model selection'])

K.lesson('calib', 'Calibrating probabilities', f'''
{viz('mlcalib')}
{wwh('A classifier is <b>calibrated</b> when its probabilities mean what they say: among all cases given 0.7, about 70% are really positive. A <b>reliability diagram</b> plots predicted probability against observed frequency, and <b>CalibratedClassifierCV</b> fixes a miscalibrated model.',
     'Many models rank well but give distorted probabilities. Naive Bayes and boosted trees push them towards 0 and 1, random forests and SVM scores pull them towards the middle. Risk scores, expected costs, pricing and thresholds chosen from costs all need honest probabilities.',
     'Fit a calibrator on held out predictions: <b>Platt scaling</b> (method="sigmoid") fits a logistic curve to the scores and suits small data. <b>Isotonic regression</b> (method="isotonic") fits any increasing step function and needs more data. calibration_curve gives the points of the reliability diagram.')}
{run('calibration')}
{note('Naive Bayes says 0.97 for its most confident bin, yet only 83% of those are positive, and says 0.03 where 24% are positive. After isotonic calibration the predicted and observed values match within about 0.04 and the Brier score falls from 0.203 to 0.168. This is the fix promised in the naive Bayes chapter.', 'tip')}
{fxs(fx('Platt scaling', 'p&prime; = 1 / (1 + exp(&minus;(A s + B)))', 's is the model score, A and B fitted on held out data.', key=True),
     fx('Expected calibration error', 'ECE = &Sigma;<sub>b</sub> (n<sub>b</sub>/n) |mean predicted<sub>b</sub> &minus; observed<sub>b</sub>|', 'Weighted gap between the curve and the diagonal.', key=True))}
''', kw=['calibration', 'reliability diagram', 'CalibratedClassifierCV', 'Platt scaling', 'isotonic regression', 'calibration_curve', 'ECE'])

K.lesson('imbalance', 'Imbalanced classes: weights and thresholds', f'''
{wwh('With a rare positive class, a default model often predicts the majority class too often. Two simple fixes: <b>class weights</b> make mistakes on the rare class cost more during training, and a <b>tuned threshold</b> moves the decision point after training.',
     'They target the metric you care about (recall, F1, cost) instead of accuracy. Both are simpler and usually as effective as generating synthetic examples (SMOTE), which can add noise and must be done inside the folds.',
     'class_weight="balanced" in most scikit-learn classifiers weights each class by n / (classes &times; n<sub>class</sub>). TunedThresholdClassifierCV(model, scoring="f1") picks the threshold by cross validation. Evaluate with recall, precision and PR AUC, never accuracy alone.')}
{run('class_weight')}
{note('With 5% positives the default logistic regression finds only half of them (recall 0.5). Balanced weights find 92%, but precision drops to 0.28: more catches, many more false alarms. Whether that trade is right depends on the costs, which is why the threshold should be tuned for the metric you care about.', 'exam')}
{run('tuned_threshold')}
{note('Tuning the threshold for F1 moves it from 0.5 to 0.25 and lifts F1 a little, from 0.625 to 0.632. With a different metric, such as a cost per missed case, the best threshold would be different again.', 'tip')}
''', kw=['class imbalance', 'class_weight', 'balanced', 'TunedThresholdClassifierCV', 'threshold tuning', 'SMOTE'])

K.lesson('versus', 'Tuning tools compared', f'''
{versus('Which tool for which job', ['Goal', 'Tool', 'Remember'], [
    ['See over and underfitting for one knob', 'validation_curve', 'Plot train and validation together'],
    ['Search a small space', 'GridSearchCV', 'Cost = settings &times; folds'],
    ['Search a big space on a budget', 'RandomizedSearchCV, loguniform', 'n_iter sets the cost'],
    ['Expensive models', 'HalvingRandomSearchCV, Optuna', 'Early results must predict final ones'],
    ['Honest score after tuning', 'Nested cross validation', 'Report it, then refit once'],
    ['Honest probabilities', 'CalibratedClassifierCV', 'Sigmoid for small data, isotonic for large'],
    ['Rare classes', 'class_weight, TunedThresholdClassifierCV', 'Pick the metric first']],
    'tune inside cross validation, report with a test set or nested CV, and calibrate when probabilities matter.')}
''', kw=['tuning tools', 'grid vs random search', 'calibration methods', 'imbalance methods'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Grid size', '|grid| = &Pi;<sub>j</sub> (number of values for hyperparameter j)', 'Grows exponentially.', key=True),
     fx('Random search coverage', 'P(at least one try in the top q share) = 1 &minus; (1 &minus; q)<sup>n</sup>', '60 tries: 95% chance of the top 5%.', key=True),
     fx('Balanced class weight', 'w<sub>c</sub> = n / (K &times; n<sub>c</sub>)', 'K classes, n<sub>c</sub> rows in class c.', key=True),
     fx('Platt scaling', 'p&prime; = sigmoid(A s + B)', 'Two numbers fitted by log loss.', key=True),
     fx('Nested CV cost', 'k<sub>outer</sub> &times; k<sub>inner</sub> &times; |grid| fits', 'Plus refits.'))}
{steps('Worked example: why 60 random tries are enough', [
    'Suppose any setting in the best 5% of the space is good enough.',
    'One random try misses that region with probability 0.95.',
    'Sixty independent tries all miss with probability 0.95<sup>60</sup>.',
    eq('0.95<sup>60</sup> = 0.046, so P(hit) = 1 &minus; 0.046 = 0.954'),
    'This holds however many hyperparameters there are, which is why random search scales where grids do not (Bergstra and Bengio, 2012).'])}
{deep('Calibration in theory and in deep networks', '<p>A proper scoring rule such as log loss is minimised in expectation by the true probabilities, so a model trained by log loss with enough data and capacity tends to be calibrated. Margin based methods (SVMs, boosting with exponential loss) are not trained that way, which is why Niculescu-Mizil and Caruana (2005) found boosted trees and SVMs need calibration while logistic regression and bagged trees often do not. Guo and others (2017) showed that modern deep networks are overconfident, and that temperature scaling, dividing all logits by one learned number T, fixes most of it. Calibration is also only on average: a model can be calibrated overall and badly miscalibrated for a subgroup, which matters for fairness.</p>')}
''', kw=['grid size', 'random search probability', 'class weight formula', 'Platt formula', 'temperature scaling', 'proper scoring rule'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Hyperparameters are the settings you pick before training. Try several and keep the one that scores best on validation data.</p>',
    '<p>Use validation curves, GridSearchCV and RandomizedSearchCV on pipelines with log scale ranges, calibrate with CalibratedClassifierCV, and handle rare classes with weights and thresholds.</p>',
    '<p>Explain why random search beats grids, run nested cross validation for honest scores, read reliability diagrams, and choose between Platt and isotonic calibration.</p>',
    '<p>Study Bayesian optimisation with Gaussian processes and TPE, Hyperband and BOHB, multi fidelity and population based training, temperature scaling and conformal prediction, and the overfitting of model selection itself.</p>')}
{grow('Try settings and keep the best on validation data.',
      'Search, calibrate and handle imbalance in pipelines.',
      'Analyse search efficiency, selection bias and calibration.')}
''', kw=['beginner', 'expert', 'BOHB', 'population based training', 'conformal prediction'])

lc(875, 'Koko Eating Bananas', 'koko-eating-bananas', 'm', 'Binary search on the setting', 'The eating speed is a setting you tune. Faster always works if slower works, so binary search the smallest speed that finishes within h hours. Hours at speed k is the sum of the ceilings of pile / k.', r'''
def min_eating_speed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        k = (lo + hi) // 2
        hours = sum((p + k - 1) // k for p in piles)
        if hours <= h:
            hi = k
        else:
            lo = k + 1
    return lo
''', [('min_eating_speed([3, 6, 7, 11], 8)', 4), ('min_eating_speed([30, 11, 23, 4, 20], 5)', 30)])
lc(69, 'Sqrt(x)', 'sqrtx', 'e', 'Binary search for the largest square below x', 'Search the largest whole number whose square is at most x. Each guess halves the range, like halving the candidates in successive halving.', r'''
def my_sqrt(x):
    lo, hi = 0, x
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo
''', [('my_sqrt(4)', 2), ('my_sqrt(8)', 2)])
lc(35, 'Search Insert Position', 'search-insert-position', 'e', 'First position not smaller than the target', 'Binary search for the first index whose value is at least the target. That is where it is or where it would go.', r'''
def search_insert(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
''', [('search_insert([1, 3, 5, 6], 5)', 2), ('search_insert([1, 3, 5, 6], 2)', 1)])
lc(162, 'Find Peak Element', 'find-peak-element', 'm', 'Walk uphill with binary search', 'Compare the middle with its right neighbour. If the right is higher, a peak lies to the right, otherwise at or to the left. Finding the top of a validation curve is the same search.', r'''
def find_peak_element(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo
''', [('find_peak_element([1, 2, 3, 1])', 2), ('find_peak_element([1, 2, 1, 3, 5, 6, 4])', 5)])
lc(1482, 'Minimum Number of Days to Make m Bouquets', 'minimum-number-of-days-to-make-m-bouquets', 'm', 'Binary search the day, check greedily', 'If m bouquets are possible by day d, they are possible on any later day. Binary search the first such day. To check a day, count runs of k adjacent bloomed flowers.', r'''
def min_days(bloom_day, m, k):
    if m * k > len(bloom_day):
        return -1

    def bouquets(day):
        made = run = 0
        for b in bloom_day:
            run = run + 1 if b <= day else 0
            if run == k:
                made = made + 1
                run = 0
        return made

    lo, hi = min(bloom_day), max(bloom_day)
    while lo < hi:
        mid = (lo + hi) // 2
        if bouquets(mid) >= m:
            hi = mid
        else:
            lo = mid + 1
    return lo
''', [('min_days([1, 10, 3, 10, 2], 3, 1)', 3), ('min_days([1, 10, 3, 10, 2], 3, 2)', -1)])
lc(2187, 'Minimum Time to Complete Trips', 'minimum-time-to-complete-trips', 'm', 'Binary search the time', 'In time t, a bus with trip time b makes t // b trips. More time never means fewer trips, so binary search the least t that reaches the total.', r'''
def minimum_time(time, total_trips):
    lo, hi = 1, min(time) * total_trips
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(mid // t for t in time) >= total_trips:
            hi = mid
        else:
            lo = mid + 1
    return lo
''', [('minimum_time([1, 2, 3], 5)', 3), ('minimum_time([2], 1)', 2)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Tuning is searching for the best setting. These problems practise binary search over a setting: the slowest eating speed that still finishes, a square root, an insert position, the peak of a curve, the first day that works, and the least time for enough trips. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'binary search', 'binary search on the answer', 'peak finding'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Hyperparameters</b> are chosen before training. A <b>validation curve</b> shows where underfitting turns into overfitting.',
    '<b>GridSearchCV</b> tries every combination, <b>RandomizedSearchCV</b> samples them. Random search covers important settings better.',
    'Search scale parameters on a <b>log scale</b>. Successive halving and Bayesian optimisation save time on expensive models.',
    'The best inner CV score is optimistic. <b>Nested cross validation</b> or a locked test set gives the honest number.',
    '<b>Calibration</b> makes probabilities honest: Platt (sigmoid) for small data, isotonic for large. Check with a reliability diagram.',
    'For rare classes use <b>class_weight</b> and a <b>tuned threshold</b>, judged by the metric you care about.'],
    'The Supervised section is complete. The Unsupervised section starts with clustering: finding groups in data that has no labels.')}
{files('Three tasks: the size of a grid, Platt scaling, and the expected calibration error.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which of these is a hyperparameter?', ['The weights of a fitted linear model', 'max_depth of a decision tree', 'The splits a tree learned', 'The support vectors'], 1, 'Set before training.', 'max_depth is chosen by you, not learned.')
K.quiz('e', 'GridSearchCV tries', ['Random combinations', 'Every combination in the grid', 'Only the defaults', 'One value per parameter'], 1, 'Exhaustive.', 'All combinations, each with cross validation.')
K.quiz('e', 'For C in an SVM, values should usually be tried on', ['A linear scale like 1, 2, 3', 'A log scale like 0.01, 0.1, 1, 10', 'Only 1', 'Negative values'], 1, 'Orders of magnitude.', 'Effects change by factors, not by steps.')
K.quiz('e', 'A calibrated model that says 0.8 on 100 cases should be right about', ['50 times', '80 times', '100 times', '8 times'], 1, 'That is what 0.8 means.', 'Predicted probability equals observed frequency.')
K.quiz('m', 'Random search often beats grid search with the same budget because', ['It is deterministic', 'Only a few hyperparameters matter, and it tries more distinct values of each', 'It uses the test set', 'It needs no cross validation'], 1, 'Bergstra and Bengio.', 'A grid repeats the same few values of each important setting.')
K.quiz('m', 'The pipeline step is named "svc". The grid key for C is', ['C', 'svc.C', 'svc__C', 'SVC_C'], 2, 'Double underscore.', 'step name, two underscores, parameter.')
K.quiz('m', 'Why is the best_score_ of a big search optimistic?', ['It uses less data', 'It is the maximum of many noisy estimates', 'It is computed on training data', 'It ignores folds'], 1, 'Winner’s curse.', 'Nested CV or a test set corrects it.')
K.quiz('m', 'Which models usually need calibration most?', ['Logistic regression', 'Naive Bayes and boosted trees', 'Linear regression', 'Nearest centroid'], 1, 'Pushed to the extremes.', 'Their probabilities are too close to 0 and 1.')
K.quiz('m', 'class_weight="balanced" on a rare positive class usually', ['Lowers recall', 'Raises recall and lowers precision', 'Changes nothing', 'Raises both always'], 1, 'Misses cost more.', 'The model flags more positives.')
K.quiz('h', 'Isotonic calibration differs from Platt scaling because it', ['Fits a straight line', 'Fits any increasing step function, so it needs more data', 'Changes the ranking', 'Only works for SVMs'], 1, 'Non parametric.', 'With little data it overfits, so Platt is safer.')
K.quiz('h', 'Successive halving with &eta; = 3 starting from 81 candidates keeps, after two rounds,', ['27', '9', '3', '1'], 1, '81 &rarr; 27 &rarr; 9.', 'Each round keeps one third.')
K.quiz('h', 'Calibration changes', ['The ranking and the AUC', 'The probabilities but not the ranking or AUC', 'Only the threshold', 'The training data'], 1, 'A monotone map.', 'An increasing transform keeps the order.')
K.quiz('x', 'In the style of a Stanford CS229 exam: temperature scaling for a neural network divides the logits by T &gt; 1 to', ['Make predictions sharper', 'Soften overconfident probabilities without changing the predicted class', 'Speed up training', 'Change the argmax'], 1, 'Guo and others (2017).', 'Dividing by T keeps the order of logits.')
K.quiz('x', 'In the style of a CMU 10-701 exam: you tune 30 settings with 5 fold CV on 150 rows and report best_score_. The bias of this estimate is', ['Zero', 'Upward (optimistic)', 'Downward always', 'Undefined'], 1, 'Selection on noise.', 'Expected maximum of noisy scores exceeds the true score of the chosen model.')

K.calc('e', 'Grid: 4 values of C and 3 values of gamma. Settings?', '12', 'Multiply.', ['4 values.', '3 values.', eq('4 &times; 3 = 12')], check=12)
K.calc('e', 'That grid with 5 fold CV. Fits before the refit?', '60', 'settings &times; folds.', ['12 settings.', '5 folds.', eq('60')], check=60)
K.calc('e', 'Add a third hyperparameter with 5 values. Settings now?', '60', 'Multiply again.', ['Previous grid 12.', '5 new values.', eq('12 &times; 5 = 60')], check=60)
K.calc('m', '60 random tries. Chance at least one lands in the top 5%, 3 decimals?', '0.954', '1 &minus; 0.95<sup>n</sup>.', ['0.95<sup>60</sup> = 0.046.', '1 &minus; 0.046.', eq('0.954')], check=0.954)
K.calc('m', 'Log scale between 0.01 and 100. The middle value?', '1', 'Geometric mean.', ['log10 0.01 = &minus;2, log10 100 = 2.', 'Middle in log space is 0.', eq('10<sup>0</sup> = 1')], check=1)
K.calc('m', 'Successive halving, &eta; = 3, 81 candidates. Rounds until 1 is left (counting the first)?', '5', '81, 27, 9, 3, 1.', ['Each round divides by 3.', 'Count the stages.', eq('5 rounds')], check=5)
K.calc('m', 'Platt scaling with A = 0.5, B = 0 on p = 0.9 (s = logit p). Calibrated p?', '0.75', 'sigmoid(A logit p + B).', ['logit 0.9 = ln 9 = 2.197.', '0.5 &times; 2.197 = 1.099.', eq('sigmoid(1.099) = 0.75')], check=0.75)
K.calc('h', '1,000 rows, 50 positives, 2 classes, class_weight balanced. Weight of a positive?', '10', 'n / (K n<sub>c</sub>).', ['K n<sub>c</sub> = 2 &times; 50 = 100.', '1,000 / 100.', eq('10')], check=10)
K.calc('h', 'Nested CV: 5 outer folds, 5 inner folds, 12 settings. Inner fits (no refits)?', '300', 'Multiply all three.', ['5 &times; 5 = 25.', 'Times 12 settings.', eq('300')], check=300)
K.calc('x', 'In the style of an MIT 6.867 problem: 60% of cases predict 0.8 and are positive 70% of the time, 40% predict 0.3 and are positive 35% of the time. ECE?', '0.08', 'Weighted gaps.', ['0.6 &times; |0.8 &minus; 0.7| = 0.06.', '0.4 &times; |0.3 &minus; 0.35| = 0.02.', eq('0.06 + 0.02 = 0.08')], check=0.08)

K.assign('gridsize', 'e', 'Size of a grid',
         '<p>Write <code>grid_size(param_grid)</code> where param_grid maps each hyperparameter name to a list of values. Return the number of combinations.</p>',
         '''
def grid_size(param_grid):
    # your code here
    pass
''', [('grid_size({"C": [0.1, 1, 10, 100], "gamma": [0.001, 0.01, 0.1]})', 12), ('grid_size({"max_depth": [2, 4, 8]})', 3), ('grid_size({})', 1)],
         '''
def grid_size(param_grid):
    total = 1
    for values in param_grid.values():
        total = total * len(values)
    return total
''', 'Multiply the lengths of the lists.', '<p>An empty grid has one combination: the defaults.</p>')
K.assign('platt', 'm', 'Platt scaling',
         '<p>Write <code>platt(p, a, b)</code> that returns sigmoid(a &times; logit(p) + b), where logit(p) = ln(p / (1 &minus; p)) and sigmoid(t) = 1 / (1 + e<sup>&minus;t</sup>), rounded to 4 decimals.</p>',
         '''
import math


def platt(p, a, b):
    # your code here
    pass
''', [('platt(0.9, 0.5, 0)', 0.75), ('platt(0.5, 2, 0)', 0.5), ('platt(0.2, 1, 0)', 0.2)],
         '''
import math


def platt(p, a, b):
    t = a * math.log(p / (1 - p)) + b
    return round(1 / (1 + math.exp(-t)), 4)
''', 'Turn p into a logit, scale and shift it, then apply the sigmoid.', '<p>With a = 1 and b = 0 the probability is unchanged. With a &lt; 1 it moves towards 0.5, softening an overconfident model.</p>')
K.assign('ece', 'h', 'Expected calibration error',
         '<p>Write <code>ece(pred, labels, n_bins)</code>. Put each prediction in bin min(int(p &times; n_bins), n_bins &minus; 1). For each non empty bin take |mean prediction &minus; mean label| weighted by the share of examples in the bin. Return the sum rounded to 4 decimals.</p>',
         '''
def ece(pred, labels, n_bins):
    # your code here
    pass
''', [('ece([0.9, 0.9, 0.1, 0.1], [1, 0, 0, 0], 2)', 0.25), ('ece([0.8, 0.8, 0.8, 0.8, 0.8], [1, 1, 1, 1, 0], 5)', 0.0), ('ece([0.25, 0.75], [0, 1], 2)', 0.25)],
         '''
def ece(pred, labels, n_bins):
    bins = {}
    for p, y in zip(pred, labels):
        b = min(int(p * n_bins), n_bins - 1)
        bins.setdefault(b, []).append((p, y))
    total = 0.0
    for items in bins.values():
        mean_p = sum(p for p, _ in items) / len(items)
        mean_y = sum(y for _, y in items) / len(items)
        total = total + len(items) / len(pred) * abs(mean_p - mean_y)
    return round(total, 4)
''', 'Group by bin, compare the mean prediction with the mean label, weight by bin size.', '<p>The second test is perfectly calibrated: 0.8 predicted and 4 of 5 positive.</p>')

K.must('Hyperparameters', 'Chosen before fit (C, gamma, max_depth, learning rate). validation_curve shows under and overfitting.')
K.must('Search', 'GridSearchCV (all combinations), RandomizedSearchCV (n_iter, loguniform). Keys like svc__C. best_estimator_ is refitted.')
K.must('Smarter', 'Successive halving and Hyperband, Bayesian optimisation (Optuna). Log scales for C, gamma, alpha, learning rate.')
K.must('Honest scores', 'best_score_ is optimistic. Nested CV: cross_val_score(GridSearchCV(...), cv=outer). Or a locked test set.')
K.must('Calibration', 'CalibratedClassifierCV: sigmoid (Platt, small data) or isotonic (more data). calibration_curve, Brier, ECE. Ranking unchanged.')
K.must('Imbalance', 'class_weight="balanced" (n / (K n<sub>c</sub>)), TunedThresholdClassifierCV for the chosen metric. Judge by recall, precision, PR AUC.')

T = K.topic(
    slug='ml-tuning', topic='ml-tuning', step=(4, 'Evaluate and improve', 'ml-s4', 'Measure models honestly, estimate how they will do on new data, and tune them without fooling yourself.', 'Intermediate'),
    title='Tuning and calibration', short='Tuning', badge='4.3', minutes=55,
    lead='Learn to tune models without fooling yourself: validation curves, grid and random search on log scales, successive halving and Bayesian optimisation, nested cross validation, calibrating probabilities, and handling rare classes with weights and thresholds.',
    desc='hyperparameter, validation curve, GridSearchCV, RandomizedSearchCV, loguniform, successive halving, Hyperband, Bayesian optimisation, Optuna, nested cross validation, optimistic bias, calibration, reliability diagram, Platt scaling, isotonic regression, CalibratedClassifierCV, ECE, class_weight, TunedThresholdClassifierCV.',
    summary='Validation curves, grid and random search, halving and Bayesian search, nested CV, calibration, and class imbalance.',
    keywords=['hyperparameter tuning', 'GridSearchCV', 'RandomizedSearchCV', 'nested cross validation', 'calibration', 'Platt scaling', 'isotonic regression', 'class_weight', 'threshold tuning', 'Optuna'],
    recap='<p>Tune inside cross validation on log scales, report with nested CV or a test set, and calibrate whenever the probabilities themselves matter.</p>',
    added='2026-11-13', leet=leet_items())
