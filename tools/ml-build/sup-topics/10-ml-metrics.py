# Supervised 4.1: evaluation metrics. Checked against Fawcett, An Introduction to ROC Analysis (Pattern Recognition
# Letters, 2006), Davis and Goadrich, The Relationship Between Precision-Recall and ROC Curves (ICML 2006), Saito and
# Rehmsmeier, The Precision-Recall Plot Is More Informative than the ROC Plot (PLOS ONE, 2015), Hand, Measuring
# classifier performance: a coherent alternative to the AUC (2009), Google's Machine Learning Crash Course
# (classification module), and the scikit-learn 1.8 user guide section 3.4.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-metrics')
K = Kit()

K.code('confusion_by_hand', r'''
actual    = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
predicted = [1, 1, 1, 0, 1, 0, 0, 0, 0, 0]

tp = fp = fn = tn = 0
for a, p in zip(actual, predicted):
    if a == 1 and p == 1:
        tp = tp + 1
    elif a == 0 and p == 1:
        fp = fp + 1
    elif a == 1 and p == 0:
        fn = fn + 1
    else:
        tn = tn + 1
print("TP", tp, " FP", fp, " FN", fn, " TN", tn)
precision = tp / (tp + fp)
recall = tp / (tp + fn)
print("accuracy ", (tp + tn) / len(actual))
print("precision", precision, " (of the predicted positives, how many are real)")
print("recall   ", recall, " (of the real positives, how many we found)")
print("F1       ", round(2 * precision * recall / (precision + recall), 3))
''')

K.code('accuracy_trap', r'''
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score

rng = np.random.default_rng(0)
y = (rng.random(10000) < 0.01).astype(int)          # 1% fraud
X = rng.normal(size=(10000, 3))
lazy = DummyClassifier(strategy="most_frequent").fit(X, y)
pred = lazy.predict(X)
print("fraud cases:", int(y.sum()), "of", len(y))
print("accuracy of 'never fraud':", round(accuracy_score(y, pred), 3))
print("recall:", recall_score(y, pred), " balanced accuracy:", balanced_accuracy_score(y, pred))
''')

K.code('report', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)          # 0 = malignant, 1 = benign
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
pred = model.predict(X_test)
print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred, target_names=["malignant", "benign"], digits=3))
''')

K.code('thresholds', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
y = 1 - y                                            # now 1 = malignant, the case we must not miss
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(C=0.05, max_iter=1000)).fit(X_train, y_train)
prob = model.predict_proba(X_test)[:, 1]
for t in [0.1, 0.3, 0.5, 0.7, 0.9]:
    pred = (prob >= t).astype(int)
    print("threshold", t, " precision", round(precision_score(y_test, pred), 3), " recall", round(recall_score(y_test, pred), 3),
          " missed cancers", int(((pred == 0) & (y_test == 1)).sum()))
''', long=True)

K.code('roc_auc', r'''
from sklearn.metrics import roc_auc_score

y = [0, 0, 1, 0, 1, 1, 0, 1]
score = [0.1, 0.3, 0.35, 0.4, 0.6, 0.7, 0.8, 0.9]

pos = [s for s, t in zip(score, y) if t == 1]
neg = [s for s, t in zip(score, y) if t == 0]
wins = 0.0
for p in pos:
    for n in neg:
        if p > n:
            wins = wins + 1
        elif p == n:
            wins = wins + 0.5
print("pairs where the positive scores higher:", wins, "of", len(pos) * len(neg))
print("AUC by counting pairs:", wins / (len(pos) * len(neg)))
print("AUC from sklearn:     ", roc_auc_score(y, score))
''', long=True)

K.code('pr_vs_roc', r'''
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split

for share in [0.5, 0.05, 0.01]:
    X, y = make_classification(n_samples=20000, n_features=10, n_informative=4, weights=[1 - share], flip_y=0.01, random_state=0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0, stratify=y)
    prob = LogisticRegression(max_iter=1000).fit(X_train, y_train).predict_proba(X_test)[:, 1]
    print("positives", str(share).ljust(4), " ROC AUC", round(roc_auc_score(y_test, prob), 3),
          " average precision (PR AUC)", round(average_precision_score(y_test, prob), 3))
''', long=True)

K.code('regression_metrics', r'''
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score

y_true = np.array([100, 150, 200, 250, 300])
y_pred = np.array([110, 140, 210, 240, 400])        # the last prediction is far off
print("MAE ", mean_absolute_error(y_true, y_pred))
print("MSE ", mean_squared_error(y_true, y_pred))
print("RMSE", round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2))
print("MAPE", round(mean_absolute_percentage_error(y_true, y_pred), 3))
print("R2  ", round(r2_score(y_true, y_pred), 3))
''')

K.code('prob_metrics', r'''
from sklearn.metrics import brier_score_loss, log_loss

y = [1, 1, 0, 0]
careful = [0.7, 0.6, 0.4, 0.3]
bold = [0.99, 0.99, 0.01, 0.99]                     # sure about everything, wrong once
for name, p in [("careful", careful), ("bold", bold)]:
    acc = sum((pi >= 0.5) == yi for pi, yi in zip(p, y)) / len(y)
    print(name.ljust(8), "accuracy", acc, " log loss", round(log_loss(y, p), 3), " Brier", round(brier_score_loss(y, p), 3))
''', long=True)

K.lesson('idea', 'The confusion matrix', f'''
{src('Fawcett, An Introduction to ROC Analysis (2006), Davis and Goadrich (2006), Saito and Rehmsmeier (2015), Hand (2009), Google’s Machine Learning Crash Course classification module, and the scikit-learn 1.8 user guide section 3.4.')}
{viz('mlconfusion')}
{wwh('A <b>confusion matrix</b> counts the four possible outcomes of a yes or no prediction: <b>true positives</b> (TP), <b>false positives</b> (FP, false alarms), <b>false negatives</b> (FN, misses) and <b>true negatives</b> (TN). Every classification metric is built from these four numbers.',
     'A single accuracy number hides which mistakes the model makes, and the two kinds of mistake rarely cost the same. Missing a cancer (FN) is far worse than an extra test (FP). Flagging an honest customer as fraud (FP) loses business. The confusion matrix shows both.',
     'Count them by comparing the true labels with the predictions, or call sklearn.metrics.confusion_matrix(y_true, y_pred). In scikit-learn the rows are the true classes and the columns the predicted classes, sorted by label.')}
{run('confusion_by_hand')}
{fxs(fx('Precision', 'precision = TP / (TP + FP)', 'Of the predicted positives, the share that are real.', key=True),
     fx('Recall (sensitivity, TPR)', 'recall = TP / (TP + FN)', 'Of the real positives, the share we found.', key=True),
     fx('F1 score', 'F1 = 2PR / (P + R)', 'Harmonic mean, low if either is low.', key=True))}
{scene('a smoke alarm', '<p>A smoke alarm that goes off at every slice of toast has perfect recall and terrible precision: it never misses a fire but most alarms are false. An alarm that only sounds when the room is full of smoke has great precision but poor recall. Where you set the sensitivity depends on what a missed fire costs compared with a false alarm.</p>')}
''', kw=['confusion matrix', 'true positive', 'false positive', 'false negative', 'precision', 'recall', 'F1 score'])

K.lesson('trap', 'Why accuracy can lie', f'''
{wwh('<b>Accuracy</b> is the share of correct predictions. On <b>imbalanced</b> data, where one class is rare, a model that always predicts the common class gets a high accuracy and is useless.',
     'Fraud, disease, defects and clicks are all rare events. A fraud model with 99% accuracy may catch no fraud at all. You need metrics that look at the rare class directly.',
     'Report recall and precision for the rare class, the <b>balanced accuracy</b> (the mean of the recall of each class), or the F1 score. Compare every model with a dummy baseline such as DummyClassifier(strategy="most_frequent").')}
{run('accuracy_trap')}
{note('Predicting "never fraud" scores 99.1% accuracy and catches none of the 89 frauds: recall 0 and balanced accuracy 0.5, the same as guessing. Always look at the class you care about.', 'exam')}
{run('report')}
{note('classification_report gives precision, recall and F1 for every class. The macro average treats each class equally, the weighted average weights by the number of examples (support). For a rare class, the macro average shows problems that the weighted average hides.', 'tip')}
''', kw=['accuracy', 'imbalanced data', 'balanced accuracy', 'classification_report', 'DummyClassifier', 'macro average', 'weighted average'])

K.lesson('threshold', 'Thresholds and the precision recall trade off', f'''
{wwh('Most classifiers output a score or probability. The <b>threshold</b> turns it into a yes or no. Lowering the threshold catches more positives (higher recall) but adds false alarms (lower precision). Raising it does the opposite.',
     'The default threshold of 0.5 is rarely the right one. In medicine you lower it so no cancer is missed, in spam filtering you raise it so no real email is lost. Choosing the threshold is a business decision, made after training.',
     'Get probabilities with predict_proba, then compare them with your own threshold. precision_recall_curve gives precision and recall at every threshold, and TunedThresholdClassifierCV (scikit-learn 1.5 and later) picks one by cross validation.')}
{run('thresholds')}
{note('At the default 0.5 the model misses 4 of 64 cancers. At 0.1 it misses none, at the cost of precision falling from 0.984 to 0.653, so about one in three alarms is a healthy patient sent for more tests. Here that trade is usually worth it.', 'tip')}
{fx('F beta score', 'F<sub>&beta;</sub> = (1 + &beta;<sup>2</sup>) PR / (&beta;<sup>2</sup>P + R)', '&beta; &gt; 1 weights recall more, &beta; &lt; 1 weights precision more.', key=True)}
''', kw=['threshold', 'precision recall trade off', 'predict_proba', 'precision_recall_curve', 'TunedThresholdClassifierCV', 'F beta'])

K.lesson('roc', 'ROC curves and AUC', f'''
{viz('mlroc')}
{wwh('The <b>ROC curve</b> plots the true positive rate (recall) against the false positive rate FP / (FP + TN) for every threshold. The <b>AUC</b> (area under it) sums up the whole curve in one number between 0 and 1.',
     'AUC measures how well the model <b>ranks</b> positives above negatives, independent of any threshold. It lets you compare models before you choose a threshold. 0.5 means random ranking and 1.0 means perfect ranking.',
     'roc_curve(y, scores) gives the points and roc_auc_score(y, scores) the area. Pass scores or probabilities, never the 0 or 1 predictions, or the curve collapses to a single point.')}
{run('roc_auc')}
{note('AUC equals the share of (positive, negative) pairs where the positive gets the higher score. Here 12 of 16 pairs are ordered correctly, so AUC = 0.75, exactly what scikit-learn reports. This ranking view is the Mann and Whitney U statistic.', 'exam')}
{fx('False positive rate', 'FPR = FP / (FP + TN) = 1 &minus; specificity', 'Share of negatives wrongly flagged.', key=True)}
''', kw=['ROC curve', 'AUC', 'true positive rate', 'false positive rate', 'specificity', 'roc_auc_score', 'ranking'])

K.lesson('pr', 'Precision recall curves for rare positives', f'''
{wwh('The <b>precision recall (PR) curve</b> plots precision against recall for every threshold. Its area, the <b>average precision</b>, focuses on how well the model finds the rare positives.',
     'ROC AUC uses the false positive rate, whose denominator is the huge number of negatives, so many false alarms barely move it. On very imbalanced data ROC AUC can look good while precision is poor. The PR curve shows the problem.',
     'Use average_precision_score(y, scores). The baseline for a random model is the share of positives, not 0.5.')}
{run('pr_vs_roc')}
{note('As positives become rare (50%, 5%, 1%), ROC AUC stays between 0.69 and 0.79, while average precision collapses from 0.82 to 0.12. With 1% positives a random model would have average precision 0.01, so 0.12 is better than random but means most alarms are false. Saito and Rehmsmeier (2015) recommend PR curves for such data.', 'tip')}
''', kw=['precision recall curve', 'average precision', 'PR AUC', 'imbalanced classification', 'ROC vs PR'])

K.lesson('regression', 'Metrics for regression', f'''
{wwh('Regression metrics measure the size of the errors y &minus; ŷ. <b>MAE</b> averages their absolute values, <b>MSE</b> averages their squares, <b>RMSE</b> is the square root of MSE in the original units, <b>MAPE</b> averages percentage errors, and <b>R&sup2;</b> compares the model with always predicting the mean.',
     'Each answers a different question. MAE is easy to explain and robust to outliers. RMSE punishes big errors much more. R&sup2; is unit free. MAPE is intuitive for business but breaks near zero targets.',
     'Use the metric that matches the cost of errors. If one big miss is much worse than several small ones, use RMSE. Report the metric on held out data, next to a baseline such as DummyRegressor.')}
{run('regression_metrics')}
{note('Four predictions are off by 10 and one by 100. MAE is 28, but RMSE is 45.6, pulled up by the single big miss because it is squared. If that miss matters, RMSE tells you. If it is a rare outlier you can live with, MAE is fairer.', 'exam')}
{fxs(fx('MAE', 'MAE = (1/n) &Sigma;|y<sub>i</sub> &minus; ŷ<sub>i</sub>|', 'Average absolute error.', key=True),
     fx('RMSE', 'RMSE = &radic;((1/n) &Sigma;(y<sub>i</sub> &minus; ŷ<sub>i</sub>)<sup>2</sup>)', 'Big errors count more.', key=True),
     fx('R&sup2;', 'R&sup2; = 1 &minus; SSE / SST', 'Share of variance explained. Can be negative.', key=True))}
''', kw=['MAE', 'MSE', 'RMSE', 'MAPE', 'R squared', 'regression metrics', 'outliers'])

K.lesson('proba', 'Metrics for probabilities', f'''
{wwh('When the probabilities themselves matter, use <b>log loss</b> (cross entropy) or the <b>Brier score</b> (mean squared error of the probabilities). Both punish confident wrong answers.',
     'Two models with the same accuracy can give very different probabilities. A risk score, a price or a medical decision depends on the probability being right, not just on which side of 0.5 it falls.',
     'log_loss(y, p) and brier_score_loss(y, p) in scikit-learn. Lower is better for both. Calibration (Supervised 4.3) improves them without changing the ranking.')}
{run('prob_metrics')}
{note('The careful model is right every time with modest confidence. The bold model says 99% for everything and is wrong once: its log loss is almost three times worse (1.159 against 0.434), because that one confident mistake costs &minus;ln(0.01) = 4.6 on its own.', 'tip')}
{fx('Log loss', 'L = &minus;(1/n) &Sigma;[y ln p + (1 &minus; y) ln(1 &minus; p)]', 'Confident mistakes cost a lot.', key=True)}
''', kw=['log loss', 'cross entropy', 'Brier score', 'probability metrics', 'confident mistakes'])

K.lesson('versus', 'Which metric when', f'''
{versus('Picking a classification metric', ['Situation', 'Use', 'Avoid'], [
    ['Balanced classes, equal costs', 'Accuracy, F1', 'Nothing special'],
    ['Rare positives you must find', 'Recall, PR curve, average precision', 'Accuracy, ROC AUC alone'],
    ['False alarms are expensive', 'Precision, precision at k', 'Recall alone'],
    ['Compare rankers before picking a threshold', 'ROC AUC', 'Accuracy at 0.5'],
    ['Probabilities feed a decision', 'Log loss, Brier, calibration plot', 'Accuracy'],
    ['Many classes', 'Macro F1, per class report, confusion matrix', 'Micro averages alone']],
    'decide which mistake costs more first, then pick the metric that measures it.')}
''', kw=['choosing a metric', 'metric selection', 'costs of errors'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Accuracy', '(TP + TN) / (TP + FP + FN + TN)', 'Share correct.', key=True),
     fx('Precision, recall', 'P = TP/(TP + FP), R = TP/(TP + FN)', 'Alarms that are real, positives found.', key=True),
     fx('Specificity', 'TN / (TN + FP)', 'Negatives correctly rejected.'),
     fx('F<sub>&beta;</sub>', '(1 + &beta;<sup>2</sup>)PR / (&beta;<sup>2</sup>P + R)', 'F1 when &beta; = 1.', key=True),
     fx('AUC as ranking', 'AUC = P(score of random positive &gt; score of random negative)', 'Ties count one half.', key=True),
     fx('Balanced accuracy', '(TPR + TNR) / 2', '0.5 for a constant prediction.'))}
{steps('Worked example: the confusion matrix by hand', [
    'Ten examples: 4 real positives, 6 real negatives.',
    'The model predicts 4 positives: 3 are real (TP = 3), 1 is not (FP = 1). It misses one positive (FN = 1), and TN = 5.',
    'Precision = 3 / (3 + 1) = 0.75. Recall = 3 / (3 + 1) = 0.75.',
    eq('F1 = 2 &times; 0.75 &times; 0.75 / (0.75 + 0.75) = 0.75'),
    'Accuracy = (3 + 5) / 10 = 0.8, as the program prints.'])}
{deep('Why F1 is a harmonic mean, and the limits of AUC', '<p>The harmonic mean 2PR/(P + R) is dominated by the smaller value: precision 1.0 with recall 0.01 gives F1 = 0.02, while the ordinary mean would say 0.5. That stops a model from looking good by maximising only one of the two. F1 ignores true negatives entirely, so it suits problems where negatives are plentiful and uninteresting. ROC AUC has its own limits: it averages over all thresholds, including ones you would never use, and Hand (2009) showed it implicitly uses different misclassification cost ratios for different classifiers, which can make comparisons incoherent. Partial AUC over a useful range of FPR, or expected cost at your real cost ratio, are more honest when costs are known.</p>')}
''', kw=['accuracy formula', 'precision formula', 'specificity', 'F beta', 'AUC ranking', 'balanced accuracy', 'harmonic mean'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Count what the model got right and wrong in a table. Precision asks how many alarms were real, recall asks how many real cases were caught.</p>',
    '<p>Read confusion matrices and classification reports, choose thresholds from predict_proba, and use ROC AUC, average precision, MAE, RMSE and R&sup2; correctly.</p>',
    '<p>Explain why accuracy fails on imbalanced data, why PR curves beat ROC curves for rare positives, and pick metrics from the real costs of each mistake.</p>',
    '<p>Study cost sensitive evaluation and expected cost curves, Hand’s H measure, proper scoring rules (log loss and Brier are proper, accuracy is not), metrics for ranking (NDCG, MAP), and confidence intervals for metrics with the bootstrap.</p>')}
{grow('Build and read a confusion matrix.',
      'Pick thresholds and metrics for real problems.',
      'Analyse metric properties and cost based evaluation.')}
''', kw=['beginner', 'expert', 'proper scoring rules', 'H measure', 'NDCG'])

lc(1512, 'Number of Good Pairs', 'number-of-good-pairs', 'e', 'Count pairs with a running tally', 'Each new value forms a good pair with every earlier equal value. Keep a count per value and add it before increasing it. AUC is also a count of pairs.', r'''
def num_identical_pairs(nums):
    seen = {}
    pairs = 0
    for x in nums:
        pairs = pairs + seen.get(x, 0)
        seen[x] = seen.get(x, 0) + 1
    return pairs
''', [('num_identical_pairs([1, 2, 3, 1, 1, 3])', 4), ('num_identical_pairs([1, 2, 3])', 0)])
lc(1365, 'How Many Numbers Are Smaller Than the Current Number', 'how-many-numbers-are-smaller-than-the-current-number', 'e', 'Sort once, read the first position', 'After sorting, the first position of a value equals how many values are smaller. That rank is exactly what AUC compares between positives and negatives.', r'''
def smaller_numbers_than_current(nums):
    order = sorted(nums)
    first = {}
    for i, v in enumerate(order):
        if v not in first:
            first[v] = i
    return [first[v] for v in nums]
''', [('smaller_numbers_than_current([8, 1, 2, 2, 3])', [4, 0, 1, 1, 3]), ('smaller_numbers_than_current([7, 7, 7, 7])', [0, 0, 0, 0])])
lc(1051, 'Height Checker', 'height-checker', 'e', 'Compare with the sorted order', 'Sort a copy and count the positions where the original differs. It is an error count between what is and what should be, like comparing predictions with labels.', r'''
def height_checker(heights):
    expected = sorted(heights)
    wrong = 0
    for a, b in zip(heights, expected):
        if a != b:
            wrong = wrong + 1
    return wrong
''', [('height_checker([1, 1, 4, 2, 1, 3])', 3), ('height_checker([5, 1, 2, 3, 4])', 5)])
lc(2006, 'Count Number of Pairs With Absolute Difference K', 'count-number-of-pairs-with-absolute-difference-k', 'e', 'Look back for x minus k and x plus k', 'Keep counts of values seen so far. Each new value pairs with every earlier value equal to x &minus; k or x + k.', r'''
def count_k_difference(nums, k):
    seen = {}
    pairs = 0
    for x in nums:
        pairs = pairs + seen.get(x - k, 0) + seen.get(x + k, 0)
        seen[x] = seen.get(x, 0) + 1
    return pairs
''', [('count_k_difference([1, 2, 2, 1], 1)', 4), ('count_k_difference([3, 2, 1, 5, 4], 2)', 3)])
lc(977, 'Squares of a Sorted Array', 'squares-of-a-sorted-array', 'e', 'Two pointers from both ends', 'The largest square is at one of the two ends. Compare the ends, place the bigger square at the back of the answer, and move that pointer inward. Squared errors are why RMSE punishes large misses.', r'''
def sorted_squares(nums):
    out = [0] * len(nums)
    left = 0
    right = len(nums) - 1
    for pos in range(len(nums) - 1, -1, -1):
        if abs(nums[left]) > abs(nums[right]):
            out[pos] = nums[left] ** 2
            left = left + 1
        else:
            out[pos] = nums[right] ** 2
            right = right - 1
    return out
''', [('sorted_squares([-4, -1, 0, 3, 10])', [0, 1, 9, 16, 100]), ('sorted_squares([-7, -3, 2, 3, 11])', [4, 9, 9, 49, 121])])
lc(1200, 'Minimum Absolute Difference', 'minimum-absolute-difference', 'e', 'Sort, then look at neighbours', 'After sorting, the smallest absolute difference is between neighbours. Find it, then collect every neighbouring pair with that difference.', r'''
def minimum_abs_difference(arr):
    s = sorted(arr)
    best = min(s[i] - s[i - 1] for i in range(1, len(s)))
    return [[s[i - 1], s[i]] for i in range(1, len(s)) if s[i] - s[i - 1] == best]
''', [('minimum_abs_difference([4, 2, 1, 3])', [[1, 2], [2, 3], [3, 4]]), ('minimum_abs_difference([1, 3, 6, 10, 15])', [[1, 3]])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Metrics are counting. These problems practise counting pairs (the idea behind AUC), ranks, mismatches against the right answer, pairs at a given distance, squares of errors, and the smallest absolute difference. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'counting pairs', 'ranking', 'sorting', 'two pointers'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'The <b>confusion matrix</b> counts TP, FP, FN and TN. Every classification metric comes from it.',
    '<b>Precision</b> TP/(TP + FP) asks how many alarms are real. <b>Recall</b> TP/(TP + FN) asks how many positives were found. F1 combines them.',
    '<b>Accuracy</b> misleads on imbalanced data. Compare with a dummy baseline and use balanced accuracy or per class metrics.',
    'The <b>threshold</b> trades precision against recall. Choose it from the costs, not by default 0.5.',
    '<b>ROC AUC</b> measures ranking. For rare positives prefer the <b>PR curve</b> and average precision.',
    'Regression: MAE (robust), RMSE (punishes big errors), R&sup2; (versus the mean).',
    'Probabilities: log loss and Brier punish confident mistakes.'],
    'Supervised 4.2 shows how to estimate these metrics honestly with train, validation and test splits and cross validation.')}
{files('Three tasks: precision and recall, the F beta score, and AUC by counting pairs.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A false positive is', ['A real positive the model missed', 'A real negative the model flagged as positive', 'A correct positive', 'A correct negative'], 1, 'False alarm.', 'Predicted positive, actually negative.')
K.quiz('e', 'Recall answers', ['Of the alarms, how many were real?', 'Of the real positives, how many did we catch?', 'How many negatives were right?', 'How fast is the model?'], 1, 'TP/(TP + FN).', 'It is the share of real positives found.')
K.quiz('e', 'On data with 1% positives, a model that always says negative has accuracy about', ['1%', '50%', '99%', '0%'], 2, 'It is right on every negative.', 'High accuracy, zero recall.')
K.quiz('e', 'Which metric is in the original units of the target?', ['MSE', 'RMSE', 'R&sup2;', 'Log loss'], 1, 'Square root.', 'RMSE undoes the squaring.')
K.quiz('m', 'Lowering the classification threshold usually', ['Raises precision and lowers recall', 'Raises recall and lowers precision', 'Changes nothing', 'Raises both'], 1, 'More predicted positives.', 'More catches, more false alarms.')
K.quiz('m', 'ROC AUC of 0.5 means', ['Perfect ranking', 'Ranking no better than random', 'Always wrong', '50% accuracy for sure'], 1, 'The diagonal.', 'Positives and negatives are mixed randomly by score.')
K.quiz('m', 'To compute ROC AUC you should pass', ['The 0 or 1 predictions', 'Scores or probabilities', 'The confusion matrix', 'The features'], 1, 'Curves need many thresholds.', 'Hard predictions give a single point.')
K.quiz('m', 'One prediction is off by 100 and four by 10. Which metric reacts most?', ['MAE', 'RMSE', 'Median absolute error', 'Accuracy'], 1, 'Squares.', 'Squaring makes the big error dominate.')
K.quiz('m', 'For fraud with 0.5% positives, the most informative single number is usually', ['Accuracy', 'Average precision (PR AUC)', 'R&sup2;', 'Training loss'], 1, 'Focus on the rare class.', 'PR curves show precision on the positives.')
K.quiz('h', 'F1 = 0.02 with precision 1.0 means recall is about', ['1.0', '0.5', '0.01', '0.98'], 2, 'Harmonic mean.', '2 &times; 1 &times; 0.01 / 1.01 &asymp; 0.02.')
K.quiz('h', 'Why can ROC AUC look good on very imbalanced data while precision is poor?', ['ROC ignores positives', 'FPR divides by the huge number of negatives, so many false alarms barely raise it', 'AUC is always 1', 'Precision is undefined'], 1, 'Look at the denominator.', 'PR curves use precision, which counts false alarms directly.')
K.quiz('h', 'A model’s log loss is huge but its accuracy is fine. The likely cause is', ['Too few features', 'A few confident wrong predictions', 'Too much data', 'Wrong threshold only'], 1, '&minus;ln p explodes as p &rarr; 0.', 'Calibrate or cap the probabilities.')
K.quiz('x', 'In the style of a Stanford CS229 exam: AUC equals', ['Accuracy at threshold 0.5', 'The probability a random positive is scored above a random negative', 'Precision times recall', 'The F1 score at the best threshold'], 1, 'Mann and Whitney.', 'The Wilcoxon and Mann and Whitney statistic divided by n<sub>+</sub>n<sub>&minus;</sub>.')
K.quiz('x', 'In the style of a CMU 10-601 exam: which of these is a proper scoring rule, rewarding honest probabilities?', ['Accuracy', 'Log loss', 'F1', 'Precision'], 1, 'Expected score best at the true probability.', 'Log loss and the Brier score are strictly proper.')

K.calc('e', 'TP = 40, FP = 10. Precision?', '0.8', 'TP/(TP + FP).', ['TP + FP = 50.', '40 / 50.', eq('0.8')], check=0.8)
K.calc('e', 'TP = 40, FN = 20. Recall, 3 decimals?', '0.667', 'TP/(TP + FN).', ['TP + FN = 60.', '40 / 60.', eq('0.667')], check=0.667)
K.calc('e', 'Errors 2, &minus;4, 6. MAE?', '4', 'Mean of absolute values.', ['|2| + |&minus;4| + |6| = 12.', '3 errors.', eq('12 / 3 = 4')], check=4)
K.calc('m', 'Precision 0.8, recall 0.5. F1, 3 decimals?', '0.615', '2PR/(P + R).', ['2 &times; 0.8 &times; 0.5 = 0.8.', 'P + R = 1.3.', eq('0.8 / 1.3 = 0.615')], check=0.615)
K.calc('m', 'TP 40, TN 900, FP 10, FN 50. Accuracy?', '0.94', '(TP + TN)/all.', ['TP + TN = 940.', 'All = 1,000.', eq('0.94')], check=0.94)
K.calc('m', 'TN 900, FP 10. Specificity, 3 decimals?', '0.989', 'TN/(TN + FP).', ['TN + FP = 910.', '900 / 910.', eq('0.989')], check=0.989)
K.calc('m', 'Errors 3 and 4. RMSE, 3 decimals?', '3.536', '&radic;mean of squares.', ['9 + 16 = 25.', 'Mean 12.5.', eq('&radic;12.5 = 3.536')], check=3.536)
K.calc('h', 'SSE = 20, SST = 100. R&sup2;?', '0.8', '1 &minus; SSE/SST.', ['20 / 100 = 0.2.', '1 &minus; 0.2.', eq('0.8')], check=0.8)
K.calc('h', 'Log loss for one example with y = 1 and p = 0.9, 3 decimals?', '0.105', '&minus;ln p.', ['y = 1, so only the ln p term.', 'ln 0.9 = &minus;0.105.', eq('0.105')], check=0.105)
K.calc('x', 'In the style of an MIT 6.036 problem: 3 positives and 4 negatives. In 10 of the pairs the positive scores higher, no ties. AUC, 3 decimals?', '0.833', 'Correct pairs / all pairs.', ['All pairs: 3 &times; 4 = 12.', 'Correct: 10.', eq('10 / 12 = 0.833')], check=0.833)

K.assign('precrec', 'e', 'Precision and recall',
         '<p>Write <code>precision_recall(actual, predicted)</code> for two lists of 0 and 1. Return a tuple (precision, recall), each rounded to 4 decimals. Use 0.0 when a denominator is 0.</p>',
         '''
def precision_recall(actual, predicted):
    # your code here
    pass
''', [('precision_recall([1, 1, 1, 1, 0, 0, 0, 0, 0, 0], [1, 1, 1, 0, 1, 0, 0, 0, 0, 0])', (0.75, 0.75)), ('precision_recall([1, 0, 1], [0, 0, 0])', (0.0, 0.0)), ('precision_recall([1, 1, 0], [1, 1, 1])', (0.6667, 1.0))],
         '''
def precision_recall(actual, predicted):
    tp = fp = fn = 0
    for a, p in zip(actual, predicted):
        if a == 1 and p == 1:
            tp = tp + 1
        elif a == 0 and p == 1:
            fp = fp + 1
        elif a == 1 and p == 0:
            fn = fn + 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return (round(precision, 4), round(recall, 4))
''', 'Count TP, FP and FN, then divide, guarding against zero.', '<p>The second test predicts nothing positive, so precision is undefined and we report 0.0, as scikit-learn does with zero_division=0.</p>')
K.assign('fbeta', 'm', 'The F beta score',
         '<p>Write <code>f_beta(precision, recall, beta)</code> that returns (1 + beta<sup>2</sup>) &times; P &times; R / (beta<sup>2</sup> &times; P + R), rounded to 4 decimals, and 0.0 when P and R are both 0.</p>',
         '''
def f_beta(precision, recall, beta):
    # your code here
    pass
''', [('f_beta(0.8, 0.5, 1)', 0.6154), ('f_beta(0.8, 0.5, 2)', 0.5405), ('f_beta(0, 0, 1)', 0.0)],
         '''
def f_beta(precision, recall, beta):
    if precision == 0 and recall == 0:
        return 0.0
    b2 = beta * beta
    return round((1 + b2) * precision * recall / (b2 * precision + recall), 4)
''', 'Square beta once, then type the formula.', '<p>With beta = 2 the low recall (0.5) pulls the score down more than in F1.</p>')
K.assign('aucpairs', 'h', 'AUC by counting pairs',
         '<p>Write <code>auc_pairs(labels, scores)</code>. For every pair of one positive and one negative, count 1 if the positive scores higher and 0.5 for a tie. Return the count divided by the number of pairs, rounded to 4 decimals.</p>',
         '''
def auc_pairs(labels, scores):
    # your code here
    pass
''', [('auc_pairs([0, 0, 1, 0, 1, 1, 0, 1], [0.1, 0.3, 0.35, 0.4, 0.6, 0.7, 0.8, 0.9])', 0.75), ('auc_pairs([1, 0], [0.9, 0.1])', 1.0), ('auc_pairs([1, 0, 1, 0], [0.5, 0.5, 0.2, 0.8])', 0.125)],
         '''
def auc_pairs(labels, scores):
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    wins = 0.0
    for p in pos:
        for n in neg:
            if p > n:
                wins = wins + 1
            elif p == n:
                wins = wins + 0.5
    return round(wins / (len(pos) * len(neg)), 4)
''', 'Split scores by label, compare every positive with every negative.', '<p>The third test shows a model that ranks worse than random: AUC below 0.5 means flipping its scores would help.</p>')

K.must('Confusion', 'TP, FP (false alarm), FN (miss), TN. sklearn rows = true, columns = predicted.')
K.must('Rates', 'Precision TP/(TP+FP), recall TP/(TP+FN), specificity TN/(TN+FP), F1 = 2PR/(P+R), F<sub>&beta;</sub>.')
K.must('Imbalance', 'Accuracy misleads. Use recall, precision, balanced accuracy, PR AUC. Compare with DummyClassifier.')
K.must('Threshold', 'Choose from costs with predict_proba. Lower threshold = more recall, less precision.')
K.must('Curves', 'ROC: TPR vs FPR, AUC = ranking probability. PR curve for rare positives (baseline = positive share).')
K.must('Regression and probabilities', 'MAE robust, RMSE punishes big errors, R&sup2; vs mean. Log loss and Brier for probabilities.')

T = K.topic(
    slug='ml-metrics', topic='ml-metrics', step=(4, 'Evaluate and improve', 'ml-s4', 'Measure models honestly, estimate how they will do on new data, and tune them without fooling yourself.', 'Intermediate'),
    title='Metrics: measuring a model properly', short='Metrics', badge='4.1', minutes=55,
    lead='Learn to measure models the right way: the confusion matrix, precision, recall and F1, why accuracy lies on imbalanced data, thresholds, ROC and PR curves, regression metrics, and log loss for probabilities.',
    desc='confusion matrix, true positive, false positive, false negative, precision, recall, F1, F beta, accuracy, imbalanced data, balanced accuracy, threshold, ROC curve, AUC, precision recall curve, average precision, MAE, MSE, RMSE, MAPE, R squared, log loss, Brier score.',
    summary='Confusion matrix, precision and recall, the accuracy trap, thresholds, ROC and PR curves, regression and probability metrics.',
    keywords=['confusion matrix', 'precision', 'recall', 'F1 score', 'ROC AUC', 'precision recall curve', 'RMSE', 'MAE', 'log loss', 'imbalanced data'],
    recap='<p>Decide which mistake costs more, then measure that mistake. Accuracy alone hides almost everything that matters.</p>',
    added='2026-11-13', leet=leet_items())
