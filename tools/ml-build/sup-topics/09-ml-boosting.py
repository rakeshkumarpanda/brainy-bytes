# Supervised 3.3: boosting. Checked against Freund and Schapire, A Decision-Theoretic Generalization of On-Line
# Learning and an Application to Boosting (1997), Friedman, Greedy Function Approximation: A Gradient Boosting Machine
# (Annals of Statistics, 2001), Chen and Guestrin, XGBoost (KDD 2016), Ke and others, LightGBM (NeurIPS 2017),
# Prokhorenkova and others, CatBoost (NeurIPS 2018), The Elements of Statistical Learning chapter 10, and the
# scikit-learn 1.8 user guide section 1.11.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-boosting')
K = Kit()

K.code('boost_by_hand', r'''
import numpy as np
from sklearn.tree import DecisionTreeRegressor

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 6, 80)).reshape(-1, 1)
y = np.sin(x).ravel() + rng.normal(0, 0.15, 80)

lr = 0.3
pred = np.full(len(y), y.mean())                  # round 0: predict the average
print("round  0  mean squared error", round(float(np.mean((y - pred) ** 2)), 4))
for m in range(1, 31):
    residual = y - pred                            # what is still wrong
    stump = DecisionTreeRegressor(max_depth=1).fit(x, residual)
    pred = pred + lr * stump.predict(x)            # take a small step towards it
    if m in (1, 2, 5, 10, 30):
        print("round", str(m).rjust(2), " mean squared error", round(float(np.mean((y - pred) ** 2)), 4))
''', long=True)

K.code('adaboost_by_hand', r'''
import math

x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [1, 1, -1, -1, 1, 1, -1, -1]
w = [1 / len(x)] * len(x)

def best_stump(w):
    best = None
    for cut in [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]:
        for sign in [1, -1]:
            pred = [sign if xi < cut else -sign for xi in x]
            err = sum(wi for wi, p, t in zip(w, pred, y) if p != t)
            if best is None or err < best[0] - 1e-12:
                best = (err, cut, sign, pred)
    return best

total = [0.0] * len(x)
for m in range(1, 4):
    err, cut, sign, pred = best_stump(w)
    alpha = 0.5 * math.log((1 - err) / err)
    print("round", m, " stump: x <", cut, "gives", sign, " weighted error", round(err, 3), " alpha", round(alpha, 3))
    w = [wi * math.exp(-alpha * t * p) for wi, t, p in zip(w, y, pred)]
    s = sum(w)
    w = [wi / s for wi in w]
    total = [tt + alpha * p for tt, p in zip(total, pred)]
    print("   new weights", [round(wi, 3) for wi in w])
final = [1 if t > 0 else -1 for t in total]
print("final predictions", final, " correct", sum(f == t for f, t in zip(final, y)), "of", len(y))
''', long=True)

K.code('learning_rate', r'''
from sklearn.datasets import load_diabetes
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
for lr in [1.0, 0.1, 0.01]:
    model = GradientBoostingRegressor(learning_rate=lr, n_estimators=500, max_depth=2, random_state=0).fit(X_train, y_train)
    test_err = [mean_squared_error(y_test, p) for p in model.staged_predict(X_test)]
    best = min(range(len(test_err)), key=lambda i: test_err[i])
    print("learning rate", str(lr).ljust(4), " best test MSE", round(test_err[best]), "after", best + 1, "trees",
          " MSE after 500 trees", round(test_err[-1]))
''', long=True)

K.code('early_stopping', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
model = HistGradientBoostingClassifier(max_iter=1000, learning_rate=0.1, early_stopping=True,
                                       validation_fraction=0.2, n_iter_no_change=20, random_state=0)
model.fit(X_train, y_train)
print("trees actually built:", model.n_iter_, "of 1000 allowed")
print("test accuracy:", round(model.score(X_test, y_test), 3))
''')

K.code('libraries', r'''
import lightgbm as lgb
import xgboost as xgb
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True, as_frame=True)     # a DataFrame keeps the column names
models = {
    "sklearn HistGB": HistGradientBoostingClassifier(random_state=0),
    "XGBoost": xgb.XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.1, random_state=0, n_jobs=1),
    "LightGBM": lgb.LGBMClassifier(n_estimators=200, num_leaves=15, learning_rate=0.1, random_state=0, verbose=-1, n_jobs=1),
}
for name, model in models.items():
    print(name.ljust(15), "accuracy", round(cross_val_score(model, X, y, cv=5).mean(), 3))
''', long=True)

K.code('compare_all', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
models = {
    "logistic regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "one tree": DecisionTreeClassifier(random_state=0),
    "random forest": RandomForestClassifier(n_estimators=200, random_state=0),
    "AdaBoost": AdaBoostClassifier(n_estimators=200, random_state=0),
    "gradient boosting": GradientBoostingClassifier(random_state=0),
}
for name, model in models.items():
    print(name.ljust(20), "accuracy", round(cross_val_score(model, X, y, cv=5).mean(), 3))
''', long=True)

K.lesson('idea', 'Small trees that fix each other’s mistakes', f'''
{src('Freund and Schapire (1997), Friedman, Greedy Function Approximation (2001), Chen and Guestrin, XGBoost (2016), Ke and others, LightGBM (2017), Prokhorenkova and others, CatBoost (2018), The Elements of Statistical Learning chapter 10, and the scikit-learn 1.8 user guide section 1.11.')}
{viz('mlboostres')}
{wwh('<b>Boosting</b> builds a strong model from many weak ones, added <b>one after another</b>. Each new small tree is trained to fix what the model so far still gets wrong. The final model is the sum of all the trees.',
     'A random forest averages independent deep trees and mainly cuts variance. Boosting adds shallow trees in sequence and mainly cuts bias, so it can reach higher accuracy. Gradient boosted trees (XGBoost, LightGBM, CatBoost, HistGradientBoosting) win most competitions on tabular data.',
     'Start from a constant (the average). Each round: compute the residuals y &minus; F(x), fit a small tree to them, and add a fraction of it (the <b>learning rate</b>) to F. Repeat for hundreds of rounds, and stop when a validation score stops improving.')}
{run('boost_by_hand')}
{note('Ten lines of code are a complete gradient boosting regressor. The error falls from 0.503 (just the average) to 0.019 after 30 stumps, each of which asks a single question about x.', 'tip')}
{scene('a student marking their own practice tests', '<p>A student takes a practice test, marks it, and spends the next session only on the questions they got wrong. Then they test again and repeat. Each session is short, but each one targets what is still weak. Boosting trains its trees the same way, and like the student it can over practise the same few odd questions if it never stops.</p>')}
''', kw=['boosting', 'gradient boosting', 'residuals', 'weak learner', 'additive model', 'sequential ensemble'])

K.lesson('adaboost', 'AdaBoost: reweight the hard examples', f'''
{viz('mladaboost')}
{wwh('<b>AdaBoost</b> (adaptive boosting, Freund and Schapire) was the first practical boosting method. Each round trains a weak classifier on <b>weighted</b> data, gives it a say &alpha; based on its weighted error, and increases the weights of the examples it got wrong.',
     'It showed that many classifiers barely better than guessing can be combined into a very accurate one. It is still a good, simple method, and it explains the idea behind all boosting: focus the next learner on the current mistakes.',
     'With weighted error &epsilon;, the say is &alpha; = &frac12; ln((1 &minus; &epsilon;)/&epsilon;). Wrong points are multiplied by e<sup>&alpha;</sup>, right points by e<sup>&minus;&alpha;</sup>, then all weights are rescaled to sum to 1. The final classifier is sign(&Sigma; &alpha;<sub>m</sub> h<sub>m</sub>(x)).')}
{run('adaboost_by_hand')}
{note('The labels + + &minus; &minus; + + &minus; &minus; cannot be split by any single cut. After round 1 the two points it got wrong (x = 5 and 6) carry 0.25 each instead of 0.125, so round 2 picks a stump that gets them right. Three stumps together classify all 8 points. AdaBoost is gradient boosting with the exponential loss e<sup>&minus;yF(x)</sup>.', 'exam')}
{fxs(fx('Say of a weak learner', '&alpha;<sub>m</sub> = &frac12; ln((1 &minus; &epsilon;<sub>m</sub>)/&epsilon;<sub>m</sub>)', 'Zero when &epsilon; = 0.5 (guessing), large when &epsilon; is small.', key=True),
     fx('Weight update', 'w<sub>i</sub> &larr; w<sub>i</sub> e<sup>&minus;&alpha;<sub>m</sub> y<sub>i</sub> h<sub>m</sub>(x<sub>i</sub>)</sup>, then normalise', 'Wrong points grow, right points shrink.', key=True))}
''', kw=['AdaBoost', 'sample weights', 'weak learner', 'alpha', 'exponential loss', 'decision stump'])

K.lesson('gradient', 'Gradient boosting: descent in function space', f'''
{wwh('<b>Gradient boosting</b> (Friedman, 2001) generalises the residual idea to any loss. Each new tree is fitted to the <b>negative gradient</b> of the loss with respect to the current predictions, the direction that lowers the loss fastest.',
     'With squared error the negative gradient is just the residual y &minus; F(x), which is why the hand made version works. With log loss for classification it is y &minus; p, the gap between label and predicted probability. The same algorithm then handles regression, classification, ranking and custom losses.',
     'F<sub>0</sub> = best constant. For m = 1 to M: compute pseudo residuals r<sub>i</sub> = &minus;&part;L/&part;F(x<sub>i</sub>), fit a small tree to them, set each leaf value to the best step for the loss, and update F<sub>m</sub> = F<sub>m&minus;1</sub> + &eta; &times; tree.')}
{table(['Loss', 'Task', 'Pseudo residual &minus;&part;L/&part;F'], [
    ['Squared error &frac12;(y &minus; F)<sup>2</sup>', 'Regression', 'y &minus; F'],
    ['Absolute error |y &minus; F|', 'Robust regression', 'sign(y &minus; F)'],
    ['Log loss', 'Classification', 'y &minus; p, with p = sigmoid(F)'],
    ['Exponential e<sup>&minus;yF</sup>', 'Classification (AdaBoost)', 'y e<sup>&minus;yF</sup>']])}
{fx('Gradient boosting update', 'F<sub>m</sub>(x) = F<sub>m&minus;1</sub>(x) + &eta; h<sub>m</sub>(x), h<sub>m</sub> fitted to &minus;&part;L/&part;F<sub>m&minus;1</sub>', 'Gradient descent where each step is a tree.', key=True)}
''', kw=['gradient boosting', 'pseudo residuals', 'negative gradient', 'loss functions', 'function space', 'Friedman'])

K.lesson('tune', 'Learning rate, number of trees and early stopping', f'''
{wwh('The key settings are the <b>learning rate</b> &eta; (shrinkage), the <b>number of trees</b>, and the <b>size of each tree</b> (max_depth or num_leaves). Unlike a forest, boosting <b>does overfit</b> if you add too many trees.',
     'A smaller learning rate needs more trees but usually reaches a better test score, because many careful steps generalise better than a few big ones. <b>Early stopping</b> picks the number of trees for you by watching a validation set.',
     'Set a small learning rate (0.05 to 0.1), allow many trees, and turn on early stopping. Keep trees shallow (depth 3 to 6). Add subsampling of rows (subsample 0.8) and features for extra regularisation.')}
{run('learning_rate')}
{note('With learning rate 1.0 the best test error comes after just 1 tree and then gets much worse (6,489 after 500 trees). With 0.1 the best is after 15 trees. With 0.01 it is after 180 trees, the lowest error of the three (3,180), and still close to it after 500. Smaller steps are slower but safer.', 'exam')}
{run('early_stopping')}
{note('HistGradientBoostingClassifier was allowed 1,000 trees but stopped after 59, when the validation score had not improved for 20 rounds. Early stopping turns the number of trees from a guess into something measured.', 'tip')}
''', kw=['learning rate', 'shrinkage', 'n_estimators', 'early stopping', 'max_depth', 'subsample', 'HistGradientBoosting'])

K.lesson('libraries', 'XGBoost, LightGBM, CatBoost and HistGradientBoosting', f'''
{wwh('Modern libraries add speed and regularisation to gradient boosting. <b>XGBoost</b> uses second order gradients and a penalty on leaf values. <b>LightGBM</b> bins features into histograms and grows trees leaf by leaf. <b>CatBoost</b> handles categorical features natively. scikit-learn’s <b>HistGradientBoosting</b> follows the LightGBM design.',
     'They train on millions of rows in minutes, handle missing values, and are the standard choice for tabular data in industry and competitions.',
     'All four share the same core ideas, so the settings carry over: learning rate, number of trees with early stopping, tree size (max_depth or num_leaves), row and column subsampling, and L1 or L2 penalties.')}
{run('libraries')}
{note('All three reach about 97% on this small dataset, so the choice rarely matters for accuracy. It matters for speed, memory, categorical handling and deployment. HistGradientBoosting needs no extra install and is a good default inside scikit-learn.', 'tip')}
{table(['Library', 'Signature idea', 'Tree growth', 'Categorical features'], [
    ['XGBoost', 'Second order Taylor expansion, regularised leaf weights', 'Level by level (depth wise) by default', 'Supported (enable_categorical)'],
    ['LightGBM', 'Histogram bins, GOSS sampling, feature bundling', 'Leaf wise (best leaf first)', 'Native'],
    ['CatBoost', 'Ordered boosting, symmetric trees', 'Symmetric (same split per level)', 'Native, target statistics'],
    ['sklearn HistGB', 'Histogram bins, LightGBM style', 'Leaf wise', 'Native (categorical_features)']])}
''', kw=['XGBoost', 'LightGBM', 'CatBoost', 'HistGradientBoostingClassifier', 'histogram binning', 'leaf wise growth'])

K.lesson('versus', 'Boosting compared', f'''
{run('compare_all')}
{note('On this dataset scaled logistic regression is best (0.981) and AdaBoost close behind (0.977). The breast cancer features are mostly linearly related to the label, so a linear model is hard to beat. Boosting shines on larger tables with nonlinear effects and interactions. Always include a simple baseline.', 'exam')}
{versus('Bagging and boosting side by side', ['', 'Random forest (bagging)', 'Gradient boosting'], [
    ['Trees built', 'Independently, in parallel', 'In sequence, each fixing the last'],
    ['Tree size', 'Deep (low bias, high variance)', 'Shallow (high bias, low variance)'],
    ['Reduces mostly', 'Variance', 'Bias'],
    ['More trees', 'Never overfits', 'Overfits without early stopping'],
    ['Tuning effort', 'Low', 'Medium to high'],
    ['Sensitive to noisy labels', 'Less', 'More (it chases hard points)']],
    'start with a random forest for a quick strong baseline, then tune gradient boosting for the best score.')}
''', kw=['bagging vs boosting', 'random forest vs gradient boosting', 'AdaBoost vs gradient boosting', 'baseline'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Additive model', 'F<sub>M</sub>(x) = F<sub>0</sub> + &eta; &Sigma;<sub>m=1</sub><sup>M</sup> h<sub>m</sub>(x)', 'A sum of small trees.', key=True),
     fx('Pseudo residuals', 'r<sub>im</sub> = &minus;&part;L(y<sub>i</sub>, F)/&part;F at F = F<sub>m&minus;1</sub>(x<sub>i</sub>)', 'Squared error gives y &minus; F.', key=True),
     fx('AdaBoost say', '&alpha; = &frac12; ln((1 &minus; &epsilon;)/&epsilon;)', 'From minimising the exponential loss.', key=True),
     fx('XGBoost leaf weight', 'w* = &minus;G / (H + &lambda;)', 'G and H are the sums of first and second derivatives in the leaf.', key=True),
     fx('XGBoost split gain', 'Gain = &frac12;[G<sub>L</sub><sup>2</sup>/(H<sub>L</sub> + &lambda;) + G<sub>R</sub><sup>2</sup>/(H<sub>R</sub> + &lambda;) &minus; G<sup>2</sup>/(H + &lambda;)] &minus; &gamma;', 'Split only if the gain is positive.'))}
{steps('Worked example: one AdaBoost round', [
    'Eight points, each weight 0.125. The best stump misclassifies 2 points.',
    'Weighted error &epsilon; = 2 &times; 0.125 = 0.25.',
    '&alpha; = &frac12; ln(0.75 / 0.25) = &frac12; ln 3 = 0.549.',
    eq('wrong: 0.125 e<sup>0.549</sup> = 0.2165, right: 0.125 e<sup>&minus;0.549</sup> = 0.0722'),
    'The sum is 2 &times; 0.2165 + 6 &times; 0.0722 = 0.866. Dividing gives 0.25 and 0.083, as the program prints.'])}
{deep('Why boosting works, and when it fails', '<p>Schapire (1990) proved that weak learnability implies strong learnability: any learner slightly better than chance can be boosted to arbitrary accuracy. AdaBoost’s training error falls exponentially, at most exp(&minus;2&Sigma;&gamma;<sub>m</sub><sup>2</sup>) where &gamma;<sub>m</sub> = 0.5 &minus; &epsilon;<sub>m</sub>. Its test error often keeps improving after training error reaches zero, explained by the growth of the voting margins (Schapire and others, 1998). Friedman, Hastie and Tibshirani (2000) showed AdaBoost is forward stagewise fitting of an additive model under exponential loss. The exponential loss punishes wrong points heavily, so AdaBoost is sensitive to label noise, and Long and Servedio (2010) proved that any convex potential booster can be defeated by random label noise. Gradient boosting with log loss and shrinkage is more robust.</p>')}
''', kw=['additive model formula', 'pseudo residuals', 'AdaBoost alpha', 'XGBoost leaf weight', 'split gain', 'weak learnability', 'margin theory'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Boosting adds small trees one after another. Each new tree learns to fix the mistakes of the trees before it.</p>',
    '<p>Train AdaBoost, GradientBoosting and HistGradientBoosting in scikit-learn, and XGBoost or LightGBM, with a small learning rate and early stopping.</p>',
    '<p>Derive the pseudo residuals for squared and log loss, compute AdaBoost weights by hand, explain shrinkage, and compare bagging with boosting by bias and variance.</p>',
    '<p>Study XGBoost’s second order objective and split gain, LightGBM’s GOSS and exclusive feature bundling, CatBoost’s ordered boosting against target leakage, margin theory for AdaBoost, and boosting’s sensitivity to label noise.</p>')}
{grow('Explain how each tree fixes the last ones’ mistakes.',
      'Train and tune boosted trees with early stopping.',
      'Derive gradient boosting and the XGBoost objective.')}
''', kw=['beginner', 'expert', 'GOSS', 'ordered boosting', 'margin theory'])

lc(1480, 'Running Sum of 1d Array', 'running-sum-of-1d-array', 'e', 'Keep adding to a total', 'Each answer is the previous answer plus the next number. A boosted model is built the same way: each round adds one more tree to the running total.', r'''
def running_sum(nums):
    out = []
    total = 0
    for x in nums:
        total = total + x
        out.append(total)
    return out
''', [('running_sum([1, 2, 3, 4])', [1, 3, 6, 10]), ('running_sum([3, 1, 2, 10, 1])', [3, 4, 6, 16, 17])])
lc(1732, 'Find the Highest Altitude', 'find-the-highest-altitude', 'e', 'Running total and its maximum', 'Start at altitude 0, add each gain, and remember the highest altitude seen, including the start.', r'''
def largest_altitude(gain):
    altitude = 0
    best = 0
    for g in gain:
        altitude = altitude + g
        best = max(best, altitude)
    return best
''', [('largest_altitude([-5, 1, 5, 0, -7])', 1), ('largest_altitude([-4, -3, -2, -1, 4, 3, 2])', 0)])
lc(1413, 'Minimum Value to Get Positive Step by Step Sum', 'minimum-value-to-get-positive-step-by-step-sum', 'e', 'Fix the lowest point of the running sum', 'Track the lowest running sum. The start value must lift that lowest point to at least 1, so the answer is 1 minus the lowest running sum, but never less than 1.', r'''
def min_start_value(nums):
    total = 0
    lowest = 0
    for x in nums:
        total = total + x
        lowest = min(lowest, total)
    return 1 - lowest
''', [('min_start_value([-3, 2, -3, 4, 2])', 5), ('min_start_value([1, 2])', 1)])
lc(724, 'Find Pivot Index', 'find-pivot-index', 'e', 'Left sum against right sum', 'Compute the total once. Walk left to right keeping the left sum. The right sum is total minus left sum minus the current value. The first index where they match is the answer.', r'''
def pivot_index(nums):
    total = sum(nums)
    left = 0
    for i, x in enumerate(nums):
        if left == total - left - x:
            return i
        left = left + x
    return -1
''', [('pivot_index([1, 7, 3, 6, 5, 6])', 3), ('pivot_index([1, 2, 3])', -1)])
lc(238, 'Product of Array Except Self', 'product-of-array-except-self', 'm', 'Prefix products times suffix products', 'For each position multiply the product of everything before it by the product of everything after it. Two passes, no division.', r'''
def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    left = 1
    for i in range(n):
        out[i] = left
        left = left * nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        out[i] = out[i] * right
        right = right * nums[i]
    return out
''', [('product_except_self([1, 2, 3, 4])', [24, 12, 8, 6]), ('product_except_self([-1, 1, 0, -3, 3])', [0, 0, 9, 0, 0])])
lc(134, 'Gas Station', 'gas-station', 'm', 'Restart after the running total goes negative', 'If the total gas is less than the total cost, no start works. Otherwise walk once, keeping a running tank. When it goes below zero, no station so far can be the start, so restart from the next one. Like boosting, every failure tells you where to look next.', r'''
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = 0
    tank = 0
    for i in range(len(gas)):
        tank = tank + gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    return start
''', [('can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])', 3), ('can_complete_circuit([2, 3, 4], [3, 4, 3])', -1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>A boosted model is a running total of small corrections. These problems practise running totals and corrections: a running sum, the highest point of a running total, the start value that fixes the lowest point, left against right sums, prefix and suffix products, and restarting after a failure. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'prefix sum', 'running total', 'greedy', 'prefix product'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Boosting</b> adds small trees in sequence, each fixing what the model still gets wrong. It mainly reduces bias.',
    '<b>AdaBoost</b> reweights wrong examples by e<sup>&alpha;</sup>, with &alpha; = &frac12; ln((1 &minus; &epsilon;)/&epsilon;).',
    '<b>Gradient boosting</b> fits each tree to the negative gradient of the loss: the residual y &minus; F for squared error, y &minus; p for log loss.',
    'A small <b>learning rate</b> with many trees generalises better. Boosting overfits with too many trees, so use <b>early stopping</b>.',
    'Keep trees shallow, subsample rows and features, and add L1 or L2 penalties.',
    'XGBoost, LightGBM, CatBoost and HistGradientBoosting are fast implementations of the same idea.',
    'Compare with a forest and a linear baseline: boosting is often, not always, the best.'],
    'Supervised 4.1 shows how to measure models properly: accuracy, precision, recall, ROC AUC and regression metrics.')}
{files('Three tasks: a boosted prediction, an AdaBoost say, and an XGBoost leaf weight.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In boosting, trees are built', ['Independently in parallel', 'One after another, each fixing earlier mistakes', 'All at once from one sample', 'Only one tree'], 1, 'Sequential.', 'Each tree targets what the current model gets wrong.')
K.quiz('e', 'With squared error, each new tree in gradient boosting fits', ['The original targets', 'The residuals y &minus; F(x)', 'Random noise', 'The features'], 1, 'Negative gradient.', 'For &frac12;(y &minus; F)<sup>2</sup> it is y &minus; F.')
K.quiz('e', 'A smaller learning rate usually needs', ['Fewer trees', 'More trees', 'No trees', 'Deeper trees only'], 1, 'Smaller steps.', 'Each tree contributes less, so more are needed.')
K.quiz('e', 'Boosted trees are usually', ['Very deep', 'Shallow (depth 3 to 6)', 'Exactly one leaf', 'Linear'], 1, 'Weak learners.', 'Shallow trees keep each step simple.')
K.quiz('m', 'AdaBoost increases the weights of', ['Correctly classified points', 'Misclassified points', 'All points equally', 'Only the first point'], 1, 'Focus on mistakes.', 'Wrong points are multiplied by e<sup>&alpha;</sup>.')
K.quiz('m', 'A weak learner with weighted error 0.5 gets AdaBoost say &alpha; =', ['1', '0', '&infin;', '&minus;1'], 1, 'ln(1) = 0.', 'Guessing adds nothing to the vote.')
K.quiz('m', 'Unlike a random forest, gradient boosting with too many trees', ['Cannot overfit', 'Can overfit, so use early stopping', 'Always underfits', 'Stops automatically by default'], 1, 'It keeps chasing residuals.', 'Monitor a validation set.')
K.quiz('m', 'For log loss classification, the pseudo residual is', ['y &minus; F', 'y &minus; p', 'p<sup>2</sup>', 'log p'], 1, 'Derivative of log loss.', 'Gap between label and predicted probability.')
K.quiz('m', 'LightGBM’s main speed idea is', ['Deeper trees', 'Histogram binning of features and leaf wise growth', 'No gradients', 'Random labels'], 1, 'Bins instead of every value.', 'Few candidate splits per feature make training fast.')
K.quiz('h', 'Boosting mainly reduces ___, bagging mainly reduces ___', ['variance, bias', 'bias, variance', 'bias, bias', 'variance, variance'], 1, 'Shallow vs deep trees.', 'Sequential correction lowers bias, averaging lowers variance.')
K.quiz('h', 'Why is AdaBoost sensitive to label noise?', ['It ignores weights', 'The exponential loss gives mislabelled points ever larger weights', 'It uses deep trees', 'It cannot use stumps'], 1, 'e<sup>&minus;yF</sup> grows fast.', 'Mislabelled points dominate later rounds.')
K.quiz('h', 'XGBoost’s optimal leaf weight is', ['G/H', '&minus;G/(H + &lambda;)', 'Mean of y', '&lambda;/G'], 1, 'Second order Taylor expansion.', 'Minimising G w + &frac12;(H + &lambda;)w<sup>2</sup> gives w* = &minus;G/(H + &lambda;).')
K.quiz('x', 'In the style of a Stanford CS229 exam: AdaBoost corresponds to forward stagewise additive modelling with which loss?', ['Squared error', 'Hinge', 'Exponential e<sup>&minus;yF(x)</sup>', 'Absolute error'], 2, 'Friedman, Hastie and Tibshirani (2000).', 'Minimising exponential loss stage by stage gives the AdaBoost updates.')
K.quiz('x', 'In the style of a CMU 10-701 exam: if every weak learner has error at most 0.5 &minus; &gamma;, AdaBoost’s training error after M rounds is bounded by', ['M&gamma;', 'exp(&minus;2M&gamma;<sup>2</sup>)', '1/M', '&gamma;<sup>M</sup>'], 1, 'Exponential decrease.', 'Each round multiplies the bound by at most &radic;(1 &minus; 4&gamma;<sup>2</sup>) &le; e<sup>&minus;2&gamma;<sup>2</sup></sup>.')

K.calc('e', 'Target y = 7, current prediction F = 5. Residual?', '2', 'y &minus; F.', ['y = 7.', 'F = 5.', eq('7 &minus; 5 = 2')], check=2)
K.calc('e', 'F<sub>0</sub> = 10, two trees predict 4 and &minus;2, learning rate 0.5. Prediction?', '11', 'F<sub>0</sub> + &eta;&Sigma;h.', ['Sum of trees 4 + (&minus;2) = 2.', 'Times 0.5 = 1.', eq('10 + 1 = 11')], check=11)
K.calc('e', 'Log loss, label y = 1, predicted p = 0.8. Pseudo residual?', '0.2', 'y &minus; p.', ['y = 1.', 'p = 0.8.', eq('1 &minus; 0.8 = 0.2')], check=0.2)
K.calc('m', 'AdaBoost weighted error 0.25. Say &alpha;, 3 decimals?', '0.549', '&frac12; ln((1 &minus; &epsilon;)/&epsilon;).', ['(1 &minus; 0.25)/0.25 = 3.', 'ln 3 = 1.099.', eq('&frac12; &times; 1.099 = 0.549')], check=0.549)
K.calc('m', 'Weight 0.125 on a wrong point, &alpha; = 0.549. Weight before normalising, 3 decimals?', '0.217', 'Multiply by e<sup>&alpha;</sup>.', ['e<sup>0.549</sup> = 1.732.', '0.125 &times; 1.732.', eq('0.2165 &asymp; 0.217')], check=0.217)
K.calc('m', 'AdaBoost weighted error 0.5. Say &alpha;?', '0', 'ln 1.', ['(1 &minus; 0.5)/0.5 = 1.', 'ln 1 = 0.', eq('&alpha; = 0')], check=0)
K.calc('m', 'Squared loss &frac12;(y &minus; F)<sup>2</sup> with y = 3, F = 1. Negative gradient?', '2', '&minus;&part;L/&part;F = y &minus; F.', ['&part;L/&part;F = &minus;(y &minus; F) = &minus;2.', 'Negate it.', eq('2')], check=2)
K.calc('h', '100 boosted trees of depth 3. Maximum total number of leaves?', '800', '2<sup>3</sup> per tree.', ['One tree: 8 leaves.', '100 trees.', eq('800')], check=800)
K.calc('h', 'Learning rate 0.1 works best with 300 trees. Halving it to 0.05, roughly how many trees to keep &eta; &times; trees the same?', '600', 'Keep the product.', ['0.1 &times; 300 = 30.', '30 / 0.05.', eq('600')], check=600)
K.calc('x', 'In the style of a Stanford CS229 problem: an XGBoost leaf has gradient sum G = &minus;4, hessian sum H = 6 and &lambda; = 2. Leaf weight?', '0.5', '&minus;G/(H + &lambda;).', ['&minus;G = 4.', 'H + &lambda; = 8.', eq('4 / 8 = 0.5')], check=0.5)

K.assign('boostpred', 'e', 'A boosted prediction',
         '<p>Write <code>boost_predict(base, tree_preds, lr)</code>. base is the starting constant, tree_preds the predictions of each tree for one example. Return base + lr &times; sum(tree_preds), rounded to 4 decimals.</p>',
         '''
def boost_predict(base, tree_preds, lr):
    # your code here
    pass
''', [('boost_predict(10, [4, -2], 0.5)', 11.0), ('boost_predict(0, [1, 1, 1], 0.1)', 0.3), ('boost_predict(2.5, [], 0.3)', 2.5)],
         '''
def boost_predict(base, tree_preds, lr):
    total = base
    for p in tree_preds:
        total = total + lr * p
    return round(total, 4)
''', 'Start from base and add lr times each tree.', '<p>This is the whole prediction step of every gradient boosting library.</p>')
K.assign('alpha', 'm', 'AdaBoost say',
         '<p>Write <code>ada_alpha(err)</code> that returns &frac12; ln((1 &minus; err)/err), rounded to 4 decimals, for 0 &lt; err &lt; 1.</p>',
         '''
import math


def ada_alpha(err):
    # your code here
    pass
''', [('ada_alpha(0.25)', 0.5493), ('ada_alpha(0.5)', 0.0), ('ada_alpha(0.1)', 1.0986)],
         '''
import math


def ada_alpha(err):
    return round(0.5 * math.log((1 - err) / err), 4) + 0.0
''', 'One line with math.log.', '<p>Error 0.1 gives a big say, error 0.5 gives none.</p>')
K.assign('leafw', 'h', 'XGBoost leaf weight',
         '<p>Write <code>leaf_weight(grads, hessians, lam)</code> for the gradients and hessians of the examples in one leaf. Return &minus;sum(grads) / (sum(hessians) + lam), rounded to 4 decimals.</p>',
         '''
def leaf_weight(grads, hessians, lam):
    # your code here
    pass
''', [('leaf_weight([-1, -3], [3, 3], 2)', 0.5), ('leaf_weight([2, 2], [1, 1], 0)', -2.0), ('leaf_weight([0.5, -0.5], [1, 1], 1)', 0.0)],
         '''
def leaf_weight(grads, hessians, lam):
    return round(-sum(grads) / (sum(hessians) + lam), 4) + 0.0
''', 'Sum the gradients and hessians, then apply the formula.', '<p>A larger &lambda; pulls every leaf weight towards 0, which is XGBoost’s L2 regularisation.</p>')

K.must('Idea', 'Add shallow trees in sequence. Each fits the current mistakes. F = F<sub>0</sub> + &eta;&Sigma;h<sub>m</sub>. Reduces bias.')
K.must('AdaBoost', '&alpha; = &frac12;ln((1 &minus; &epsilon;)/&epsilon;). Wrong points &times; e<sup>&alpha;</sup>, right &times; e<sup>&minus;&alpha;</sup>. Exponential loss, noise sensitive.')
K.must('Gradient', 'Fit trees to &minus;&part;L/&part;F: y &minus; F (squared), y &minus; p (log loss), sign(y &minus; F) (absolute).')
K.must('Tuning', 'Small learning rate (0.05 to 0.1), many trees with early stopping, depth 3 to 6, subsample 0.8, L2 penalty.')
K.must('Libraries', 'XGBoost (2nd order, w* = &minus;G/(H + &lambda;)), LightGBM (histograms, leaf wise), CatBoost (categories), sklearn HistGB.')
K.must('Versus', 'Forest: parallel deep trees, variance, never overfits with more trees. Boosting: sequential shallow trees, bias, overfits.')

T = K.topic(
    slug='ml-boosting', topic='ml-boosting', step=(3, 'Trees and ensembles', 'ml-s3', 'Ask the data a chain of yes or no questions, then combine hundreds of such trees into the strongest models for tables.', 'Intermediate'),
    title='Boosting: small trees that fix each other', short='Boosting', badge='3.3', minutes=60,
    lead='Learn boosting from the ground up: gradient boosting as fitting residuals, AdaBoost and sample weights, pseudo residuals for any loss, learning rate and early stopping, and the XGBoost, LightGBM, CatBoost and HistGradientBoosting libraries.',
    desc='boosting, gradient boosting, residuals, AdaBoost, sample weights, alpha, exponential loss, pseudo residuals, negative gradient, learning rate, shrinkage, early stopping, n_estimators, XGBoost, LightGBM, CatBoost, HistGradientBoosting, leaf weight, split gain, bagging vs boosting.',
    summary='Fitting residuals, AdaBoost weights, gradient boosting for any loss, learning rate and early stopping, and the modern libraries.',
    keywords=['boosting', 'gradient boosting', 'AdaBoost', 'XGBoost', 'LightGBM', 'CatBoost', 'learning rate', 'early stopping', 'residuals', 'HistGradientBoosting'],
    recap='<p>Boosting adds shallow trees one by one, each fitting what is still wrong. Use a small learning rate and early stopping, and compare with a forest and a linear baseline.</p>',
    added='2026-11-13', leet=leet_items())
