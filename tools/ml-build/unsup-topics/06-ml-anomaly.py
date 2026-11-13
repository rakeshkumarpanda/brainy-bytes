# Unsupervised 3.1: anomaly detection. Checked against Liu, Ting and Zhou, Isolation Forest (ICDM 2008), Breunig,
# Kriegel, Ng and Sander, LOF: Identifying Density-Based Local Outliers (SIGMOD 2000), Scholkopf and others, Estimating
# the Support of a High-Dimensional Distribution (Neural Computation 2001), Rousseeuw and Van Driessen, the minimum
# covariance determinant (1999), Iglewicz and Hoaglin, How to Detect and Handle Outliers (1993), Chandola, Banerjee and
# Kumar, Anomaly Detection: A Survey (ACM Computing Surveys 2009), and the scikit-learn 1.8 user guide section 2.7.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-anomaly')
K = Kit()

K.code('robust_stats', r'''
import numpy as np

# Daily orders for a small shop, with two very bad data entry days
x = np.array([52, 48, 50, 55, 47, 51, 49, 53, 50, 46, 54, 900, 950], dtype=float)
z = (x - x.mean()) / x.std()
print("mean", round(float(x.mean()), 1), " sd", round(float(x.std()), 1))
print("z scores of the two bad days:", np.round(z[-2:], 2).tolist(), " flagged with |z| > 3:", int((np.abs(z) > 3).sum()))

med = np.median(x)
mad = np.median(np.abs(x - med)) * 1.4826             # scaled so it matches the sd for normal data
robust = (x - med) / mad
print("median", med, " MAD", round(float(mad), 2))
print("robust scores of the two bad days:", np.round(robust[-2:], 1).tolist(), " flagged with |score| > 3.5:", int((np.abs(robust) > 3.5).sum()))

q1, q3 = np.percentile(x, [25, 75])
lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
print("IQR fences", lo, "to", hi, " flagged:", x[(x < lo) | (x > hi)].tolist())
''')

K.code('isolation_by_hand', r'''
import numpy as np

rng = np.random.default_rng(0)
x = np.concatenate([rng.normal(50, 5, 99), [95.0]])    # 99 normal values and one far away
def depth(target, values, rng):
    steps = 0
    while len(values) > 1:
        cut = rng.uniform(values.min(), values.max())   # a random split between min and max
        values = values[values < cut] if target < cut else values[values >= cut]
        steps = steps + 1
    return steps
outlier = [depth(95.0, x, rng) for _ in range(200)]
normal = [depth(x[0], x, rng) for _ in range(200)]
print("average splits to isolate the far value 95:", round(float(np.mean(outlier)), 2))
print("average splits to isolate a normal value", round(float(x[0]), 1), ":", round(float(np.mean(normal)), 2))
n = len(x)
c = 2 * (np.log(n - 1) + 0.5772156649) - 2 * (n - 1) / n  # average depth of an unsuccessful search in a random tree
for name, h in [("far value", np.mean(outlier)), ("normal value", np.mean(normal))]:
    print(name.ljust(12), " anomaly score 2^(-h/c) =", round(float(2 ** (-h / c)), 3))
''', long=True)

K.code('isolation_forest', r'''
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, roc_auc_score

rng = np.random.default_rng(1)
normal = rng.normal(0, 1, size=(980, 2))
odd = rng.uniform(-6, 6, size=(20, 2))
odd = odd[np.abs(odd).max(axis=1) > 3]                 # keep only points well outside the normal cloud
X = np.vstack([normal, odd])
y = np.r_[np.zeros(len(normal)), np.ones(len(odd))]   # 1 = anomaly, used only to check the result
iso = IsolationForest(n_estimators=200, contamination=len(odd) / len(X), random_state=0).fit(X)
flag = iso.predict(X) == -1                            # scikit-learn marks anomalies with -1
print("anomalies planted:", len(odd), " flagged:", int(flag.sum()))
print("precision", round(float(precision_score(y, flag)), 3), " recall", round(float(recall_score(y, flag)), 3))
print("ROC AUC of the anomaly score:", round(float(roc_auc_score(y, -iso.score_samples(X))), 3))
''')

K.code('lof_density', r'''
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

rng = np.random.default_rng(2)
dense = rng.normal([0, 0], 0.2, size=(200, 2))         # a very tight group
sparse = rng.normal([5, 5], 1.5, size=(200, 2))        # a loose group
local = np.array([[1.2, 0.0]])                         # just outside the tight group
X = np.vstack([dense, sparse, local])
lof = LocalOutlierFactor(n_neighbors=20).fit(X)
lof_score = -lof.negative_outlier_factor_
iso_score = -IsolationForest(random_state=0).fit(X).score_samples(X)
for name, s in [("LOF", lof_score), ("Isolation Forest", iso_score)]:
    rank = int((s > s[-1]).sum()) + 1
    print(name.ljust(16), " rank of the point next to the tight group:", rank, "of", len(X))
print("LOF of that point:", round(float(lof_score[-1]), 2), " typical LOF inside a group:", round(float(np.median(lof_score)), 2))
''')

K.code('compare_methods', r'''
import numpy as np
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

rng = np.random.default_rng(3)
train = np.vstack([rng.normal([0, 0], 1, (500, 2)), rng.normal([6, 6], 1, (500, 2))])   # clean normal data
test_ok = np.vstack([rng.normal([0, 0], 1, (200, 2)), rng.normal([6, 6], 1, (200, 2))])
test_bad = rng.uniform(-4, 10, (60, 2))
test_bad = test_bad[np.minimum(np.linalg.norm(test_bad, axis=1), np.linalg.norm(test_bad - 6, axis=1)) > 3.5]
X_test = np.vstack([test_ok, test_bad])
y_test = np.r_[np.zeros(len(test_ok)), np.ones(len(test_bad))]
sc = StandardScaler().fit(train)
A, B = sc.transform(train), sc.transform(X_test)
models = {"Isolation Forest": IsolationForest(random_state=0),
          "LOF (novelty)": LocalOutlierFactor(n_neighbors=20, novelty=True),
          "One class SVM": OneClassSVM(nu=0.05, gamma=0.5),
          "Elliptic envelope": EllipticEnvelope(random_state=0),
          "Gaussian mixture": GaussianMixture(n_components=2, random_state=0)}
for name, m in models.items():
    m.fit(A)
    score = -m.score_samples(B)                         # higher = more unusual
    print(name.ljust(17), " ROC AUC", round(float(roc_auc_score(y_test, score)), 3), "  PR AUC", round(float(average_precision_score(y_test, score)), 3))
print("anomalies in the test set:", len(test_bad), "of", len(X_test))
''', long=True)

K.code('evaluate', r'''
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

rng = np.random.default_rng(4)
y = np.r_[np.zeros(9900), np.ones(100)]                 # 1% anomalies
score = np.r_[rng.normal(0, 1, 9900), rng.normal(2.5, 1, 100)]
print("ROC AUC", round(float(roc_auc_score(y, score)), 3), "  PR AUC", round(float(average_precision_score(y, score)), 3), "  (PR AUC of random guessing = 0.01)")
order = np.argsort(-score)
for k in [50, 100, 500]:
    print("precision at top", str(k).rjust(3), round(float(y[order[:k]].mean()), 2), "  recall", round(float(y[order[:k]].sum() / 100), 2))
''', long=True)

K.lesson('idea', 'What makes a point an anomaly', f'''
{src('Chandola, Banerjee and Kumar, Anomaly Detection: A Survey (ACM Computing Surveys 2009), Iglewicz and Hoaglin, How to Detect and Handle Outliers (1993), and the scikit-learn 1.8 user guide section 2.7.')}
{wwh('An <b>anomaly</b> (or outlier) is a data point that does not fit the pattern of the rest. <b>Anomaly detection</b> finds such points, usually without labels, by learning what normal looks like and scoring how far each point is from it. Simple rules use <b>robust statistics</b>: the median and the median absolute deviation (MAD), or the interquartile range (IQR).',
     'Fraud, machine faults, network attacks, data entry errors and rare diseases are all anomalies. They are rare, so there are few or no labelled examples, and they cost a lot when missed. Cleaning anomalies out of training data also makes other models better.',
     'For one feature, flag values more than 3.5 robust units from the median, or outside Q1 &minus; 1.5 IQR and Q3 + 1.5 IQR. The mean and standard deviation are themselves pulled by outliers, so z scores can hide the very points you want to find. For many features, use the model based methods in the next lessons.')}
{run('robust_stats')}
{note('Two typing mistakes (900 and 950 orders on days that usually see about 50) drag the mean to 185 and the standard deviation to 316. Their z scores are only 2.26 and 2.42, so a |z| &gt; 3 rule misses both. This is called <b>masking</b>. The median (51) and MAD (4.45) barely move, so the robust scores are about 190 and 200 and both days are flagged, as they are by the IQR fences 41.5 to 61.5.', 'exam')}
{fxs(fx('Robust score', '(x &minus; median) / (1.4826 &times; MAD)', 'MAD = median of |x &minus; median|. Flag above 3.5.', key=True),
     fx('IQR fences', 'Q1 &minus; 1.5 IQR and Q3 + 1.5 IQR', 'IQR = Q3 &minus; Q1. The box plot rule.', key=True))}
{table(['Kind of anomaly', 'Example', 'Typical method'], [
    ['Point', 'One payment of 50,000 on a card that usually spends 50', 'Robust scores, Isolation Forest'],
    ['Contextual', '30 degrees is normal in July but odd in January', 'Model the context, then score the residual'],
    ['Collective', 'A run of normal looking packets that together form an attack', 'Sequence and time series models']])}
''', kw=['anomaly detection', 'outlier', 'robust statistics', 'median absolute deviation', 'MAD', 'IQR', 'masking', 'z score'])

K.lesson('iforest', 'Isolation Forest', f'''
{src('Liu, Ting and Zhou, Isolation Forest (ICDM 2008), and the scikit-learn 1.8 IsolationForest documentation.')}
{viz('mliforest')}
{wwh('<b>Isolation Forest</b> builds many random trees. Each tree picks a random feature and a random cut between its smallest and largest value, again and again. Anomalies are few and far away, so they get isolated in few cuts. The average path length over the trees becomes an <b>anomaly score</b>.',
     'It needs no distances or densities, so it is fast (linear in the number of points), works in many dimensions, and scales to millions of rows. It is often the first method to try on tabular data.',
     'IsolationForest(n_estimators=200, contamination=..., random_state=0).fit(X). score_samples gives a score where lower is more anomalous, and predict returns &minus;1 for anomalies using the contamination share as the cut off. Each tree sees a small sample (256 rows by default), which actually helps.')}
{run('isolation_by_hand')}
{note('With 100 values, the far value 95 is isolated after 1.39 random cuts on average, while a normal value needs about 10. Turning path length into a score with s = 2<sup>&minus;h/c(n)</sup> gives 0.89 for the far value and 0.44 for the normal one. Scores near 1 are anomalies, and scores below 0.5 are normal.', 'exam')}
{run('isolation_forest')}
{note('The forest separates the planted points very well: ROC AUC 0.998. With contamination set to the true share it flags 14 points, of which 11 are planted anomalies (precision and recall 0.786). The misses are planted points that happened to land close to the normal cloud.', 'tip')}
{fx('Isolation score', 's(x, n) = 2<sup>&minus;E[h(x)] / c(n)</sup>, c(n) = 2(ln(n &minus; 1) + 0.5772) &minus; 2(n &minus; 1)/n', 'h = path length, c(n) = average path length in a random tree.', key=True)}
''', kw=['Isolation Forest', 'IsolationForest', 'path length', 'anomaly score', 'contamination', 'random trees'])

K.lesson('lof', 'Local outlier factor: anomalies relative to their neighbourhood', f'''
{src('Breunig, Kriegel, Ng and Sander, LOF: Identifying Density-Based Local Outliers (SIGMOD 2000).')}
{viz('mllof')}
{wwh('The <b>local outlier factor</b> (LOF) compares how crowded a point’s neighbourhood is with how crowded its neighbours’ neighbourhoods are. A point in a loose group is fine if its neighbours are just as loose. A point a little outside a very tight group is flagged, because its neighbours are much more crowded than it is.',
     'Real data mixes dense and sparse regions. A single global distance or density threshold either flags the whole sparse region or misses points just outside dense ones. LOF adapts to the local density.',
     'LocalOutlierFactor(n_neighbors=20).fit_predict(X) labels the training points. To score new points, create it with novelty=True and use score_samples or predict. LOF near 1 is normal and well above 1 is an outlier.')}
{run('lof_density')}
{note('A point at distance 1.2 from a group of spread 0.2 is very unusual locally, but it is still much closer to the other points than the edges of the loose group are. LOF ranks it as the single most unusual of 401 points, with an LOF of 4.77 against a typical 1.04. Isolation Forest, which looks at global isolation, ranks it only 13th.', 'exam')}
{fxs(fx('Reachability distance', 'reach<sub>k</sub>(p, o) = max(k-distance(o), d(p, o))', 'Smooths tiny distances inside dense groups.'),
     fx('Local reachability density', 'lrd(p) = 1 / mean<sub>o &isin; N<sub>k</sub>(p)</sub> reach<sub>k</sub>(p, o)', 'How crowded p’s neighbourhood is.', key=True),
     fx('LOF', 'LOF(p) = mean<sub>o &isin; N<sub>k</sub>(p)</sub> lrd(o) / lrd(p)', 'About 1 normal, above 1 outlier.', key=True))}
''', kw=['local outlier factor', 'LOF', 'local reachability density', 'k-distance', 'novelty detection', 'varying density'])

K.lesson('others', 'One class SVM, robust covariance and a fair comparison', f'''
{src('Scholkopf and others, Estimating the Support of a High-Dimensional Distribution (2001), Rousseeuw and Van Driessen, A Fast Algorithm for the Minimum Covariance Determinant Estimator (1999), and the scikit-learn 1.8 novelty and outlier detection guide.')}
{wwh('A <b>one class SVM</b> draws a boundary around the normal data in a kernel space, with nu as the upper bound on the share of training points left outside. The <b>elliptic envelope</b> fits one robust Gaussian (minimum covariance determinant) and flags points with a large Mahalanobis distance. A <b>Gaussian mixture</b> scores points by their log density.',
     'Different methods assume different shapes of normal data. Knowing them lets you choose: one ellipse, several blobs, any shape. <b>Outlier detection</b> fits on data that already contains anomalies, while <b>novelty detection</b> fits on clean normal data and scores new points.',
     'Scale the features first. Fit on normal data where you can, score a labelled test set, and compare methods with ROC AUC and especially PR AUC, which is honest when anomalies are rare.')}
{run('compare_methods')}
{note('The normal data is two round blobs. The Gaussian mixture, one class SVM and LOF all score almost perfectly, because they can model two groups. The elliptic envelope assumes one ellipse around everything, so the empty space between the blobs looks normal to it and its PR AUC drops to 0.92. Isolation Forest is close behind at 0.91. Match the method to the shape of normal.', 'exam')}
''', kw=['one class SVM', 'nu', 'elliptic envelope', 'minimum covariance determinant', 'Mahalanobis distance', 'novelty detection', 'outlier detection'])

K.lesson('evaluate', 'Evaluating detectors when anomalies are rare', f'''
{wwh('With 1% anomalies, a detector that flags nothing is 99% accurate, so accuracy is useless. Use the <b>precision recall curve</b> and its area (PR AUC, also called average precision), <b>precision at k</b> (how many of the top k flagged are real), and recall at a fixed review budget.',
     'In practice a team can review only so many alerts a day. Precision at that number of alerts is what decides whether the detector is useful. ROC AUC can look excellent while most alerts are still false.',
     'Collect even a small labelled set of anomalies for evaluation. Choose the alert threshold from the review budget or the cost of a miss against a false alarm, not from a default. Watch out for drift: normal behaviour changes over time, so refit regularly.')}
{run('evaluate')}
{note('ROC AUC is 0.957, which sounds excellent. But PR AUC is 0.496, and of the top 100 alerts only half are real. With a budget of 500 alerts the team catches 81% of anomalies but 84% of its work is false alarms. PR AUC and precision at k tell that story, and ROC AUC hides it.', 'exam')}
''', kw=['PR AUC', 'average precision', 'precision at k', 'rare events', 'alert budget', 'concept drift'])

K.lesson('versus', 'Anomaly detection methods compared', f'''
{versus('Choosing an anomaly detector', ['', 'Robust stats', 'Isolation Forest', 'LOF', 'One class SVM', 'Elliptic envelope', 'GMM'], [
    ['Features', 'One at a time', 'Many', 'Many', 'Many', 'Many', 'Many'],
    ['Shape of normal', 'One centre', 'Any', 'Any, varying density', 'Any (kernel)', 'One ellipse', 'Several ellipses'],
    ['Speed on big data', 'Very fast', 'Fast', 'Slow (neighbours)', 'Slow (kernel)', 'Fast', 'Moderate'],
    ['Main setting', 'Threshold', 'contamination', 'n_neighbors', 'nu, gamma', 'contamination', 'n_components'],
    ['New points', 'Yes', 'Yes', 'novelty=True', 'Yes', 'Yes', 'Yes']],
    'start with robust statistics for single features and Isolation Forest for tables, use LOF when density varies, and a GMM or one class SVM when normal data has a clear multi part shape.')}
{note('Supervised classification beats all of these when you have enough labelled anomalies of every kind you care about. Anomaly detection is for when you do not, or when new kinds of anomalies keep appearing.', 'tip')}
''', kw=['choosing an anomaly detector', 'supervised vs unsupervised anomaly detection'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('z score', 'z = (x &minus; &mu;) / &sigma;', 'Sensitive to the outliers it seeks.'),
     fx('Robust score', '(x &minus; median) / (1.4826 MAD)', '1.4826 makes MAD match &sigma; for normal data.', key=True),
     fx('Mahalanobis distance', 'd<sub>M</sub>(x) = &radic;((x &minus; &mu;)<sup>T</sup> &Sigma;<sup>&minus;1</sup> (x &minus; &mu;))', 'Distance measured in units of the spread.', key=True),
     fx('Isolation score', 's = 2<sup>&minus;E[h]/c(n)</sup>', '1 anomalous, 0.5 nothing special, lower normal.', key=True),
     fx('LOF', 'mean lrd(neighbours) / lrd(p)', 'Relative density.', key=True),
     fx('Precision at k', '(true anomalies in the top k) / k', 'Matches the review budget.'))}
{steps('Worked example: the Isolation Forest normaliser for 256 points', [
    'c(n) = 2(ln(n &minus; 1) + &gamma;) &minus; 2(n &minus; 1)/n with &gamma; = 0.5772.',
    'ln 255 = 5.541, so 2(5.541 + 0.577) = 12.237.',
    '2 &times; 255 / 256 = 1.992.',
    eq('c(256) = 12.237 &minus; 1.992 = 10.245'),
    'A point isolated in 5 cuts on average scores 2<sup>&minus;5/10.245</sup> = 0.71, so it looks anomalous.'])}
{deep('Why 1.4826, and why isolation works', '<p>For normally distributed data, the median absolute deviation equals &sigma; &times; &Phi;<sup>&minus;1</sup>(0.75) = 0.6745 &sigma;, so dividing by 0.6745 (multiplying by 1.4826) makes MAD an estimate of &sigma; that ignores up to half the data being outliers: a breakdown point of 50%, against 0% for the standard deviation. Isolation Forest relies on two facts: anomalies are few, and they have unusual values on some feature. A random cut between min and max lands in the large empty space next to an isolated point with high probability, so its expected depth grows much more slowly than the log n depth of typical points. c(n) is the average depth of an unsuccessful search in a binary search tree, which normalises scores across sample sizes. Subsampling (256 rows) reduces masking and swamping, where groups of anomalies hide each other or make normal points look odd.</p>')}
''', kw=['z score', 'robust score formula', 'Mahalanobis distance', 'c(n)', 'breakdown point', 'masking and swamping'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Anomaly detection finds the records that do not fit the rest, such as fraud or broken sensors, by learning what normal looks like.</p>',
    '<p>Use median and MAD or IQR for single features, Isolation Forest and LOF for tables, scale features, and judge detectors with PR AUC and precision at k.</p>',
    '<p>Explain masking, derive the isolation score and LOF, choose between outlier and novelty detection, and match the method to the shape of normal data.</p>',
    '<p>Study robust covariance estimation and breakdown points, extended and deep isolation forests, deep one class methods and autoencoder reconstruction scores, and time series and graph anomaly detection.</p>')}
{grow('Explain what makes a point unusual.',
      'Detect and evaluate anomalies on real tables.',
      'Derive scores and choose methods by their assumptions.')}
''', kw=['beginner', 'expert', 'deep anomaly detection', 'robust covariance'])

lc(136, 'Single Number', 'single-number', 'e', 'XOR cancels every pair', 'XOR all the numbers. Each pair cancels to 0, so the number that appears once is what is left. The odd one out stands out because everything else matches.', r"""
def single_number(nums):
    result = 0
    for v in nums:
        result = result ^ v
    return result
""", [('single_number([4, 1, 2, 1, 2])', 4), ('single_number([2, 2, 1])', 1)])
lc(268, 'Missing Number', 'missing-number', 'e', 'Compare the expected sum with the actual sum', 'The numbers 0 to n add up to n(n + 1)/2. Subtract the actual sum and the gap is the missing number. Comparing what you expect with what you see is the core of anomaly detection.', r"""
def missing_number(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)
""", [('missing_number([3, 0, 1])', 2), ('missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1])', 8)])
lc(219, 'Contains Duplicate II', 'contains-duplicate-ii', 'e', 'Remember where each value was last seen', 'Keep the last index of each value in a dictionary. If a value comes back within k positions, answer true. It is the same pattern as flagging a repeated event inside a time window.', r"""
def contains_nearby_duplicate(nums, k):
    last = {}
    for i, v in enumerate(nums):
        if v in last and i - last[v] <= k:
            return True
        last[v] = i
    return False
""", [('contains_nearby_duplicate([1, 2, 3, 1], 3)', True), ('contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)', False)])
lc(287, 'Find the Duplicate Number', 'find-the-duplicate-number', 'm', 'Treat values as next pointers and find the cycle', 'Read nums as a linked list where i points to nums[i]. The duplicate value is where a cycle starts. Floyd’s tortoise and hare finds it in O(1) extra memory.', r"""
def find_duplicate(nums):
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
""", [('find_duplicate([1, 3, 4, 2, 2])', 2), ('find_duplicate([3, 1, 3, 4, 2])', 3)])
lc(442, 'Find All Duplicates in an Array', 'find-all-duplicates-in-an-array', 'm', 'Mark seen values by flipping signs in place', 'Values are 1 to n, so value v can mark position v &minus; 1 by making it negative. Meeting an already negative mark means v is a duplicate. Ours sorts the answer so it can be checked, and LeetCode accepts any order.', r"""
def find_duplicates(nums):
    nums = list(nums)
    found = []
    for v in nums:
        i = abs(v) - 1
        if nums[i] < 0:
            found.append(abs(v))
        else:
            nums[i] = -nums[i]
    return sorted(found)
""", [('find_duplicates([4, 3, 2, 7, 8, 2, 3, 1])', [2, 3]), ('find_duplicates([1, 1, 2])', [1])])
lc(41, 'First Missing Positive', 'first-missing-positive', 'h', 'Place each value at its own index, then scan', 'Swap each value v in 1 to n into position v &minus; 1. Afterwards the first position i that does not hold i + 1 gives the answer. It runs in O(n) time with O(1) extra memory.', r"""
def first_missing_positive(nums):
    nums = list(nums)
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            j = nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1
""", [('first_missing_positive([1, 2, 0])', 3), ('first_missing_positive([3, 4, -1, 1])', 2), ('first_missing_positive([7, 8, 9, 11, 12])', 1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Anomaly detection is about finding what does not fit. These problems practise finding the one value without a partner, the gap between expected and actual, a repeat inside a window, a duplicate hidden as a cycle, all repeated values, and the first missing value, each in linear time. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'XOR', 'cycle detection', 'hash map', 'in place marking', 'missing values'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Anomalies are rare points that do not fit. Detection learns normal and scores distance from it, usually without labels.',
    'The mean and standard deviation are pulled by outliers (masking). Use the <b>median and MAD</b> or <b>IQR fences</b> for single features.',
    '<b>Isolation Forest</b>: random cuts isolate anomalies quickly. Score 2<sup>&minus;E[h]/c(n)</sup>, near 1 is anomalous. Fast and a good default.',
    '<b>LOF</b> compares a point’s local density with its neighbours’, so it handles regions of different density.',
    'One class SVM, elliptic envelope and GMMs assume different shapes of normal. Outlier detection fits on dirty data, novelty detection on clean data.',
    'Evaluate with PR AUC and precision at k, not accuracy, and choose the threshold from the alert budget.'],
    'Unsupervised 3.2 covers association rules: support, confidence, lift, Apriori and FP-Growth.')}
{files('Three tasks: robust scores, IQR outliers, and the local outlier factor of one point.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why can z scores miss big outliers?', ['They are too slow', 'The outliers inflate the mean and standard deviation (masking)', 'They need labels', 'They only work on images'], 1, 'Mean and sd move.', 'Robust statistics avoid this.')
K.quiz('e', 'The IQR rule flags values', ['Above the mean', 'Below Q1 &minus; 1.5 IQR or above Q3 + 1.5 IQR', 'In the middle 50%', 'Equal to the median'], 1, 'Box plot.', 'IQR = Q3 &minus; Q1.')
K.quiz('e', 'In scikit-learn, predict on an outlier detector returns', ['0 and 1', '&minus;1 for anomalies and 1 for normal points', 'Probabilities', 'Cluster numbers'], 1, 'Sign.', 'score_samples gives the continuous score.')
K.quiz('e', 'Isolation Forest finds anomalies because they', ['Have labels', 'Get isolated by random cuts in fewer steps', 'Have the largest values only', 'Are in the biggest cluster'], 1, 'Short paths.', 'Few and different.')
K.quiz('m', 'An Isolation Forest score near 0.5 for all points means', ['All are anomalies', 'Nothing stands out clearly', 'The model failed to fit', 'Half are anomalies'], 1, '2<sup>&minus;1</sup>.', 'Paths are all about average.')
K.quiz('m', 'LOF is better than a global distance threshold when', ['There is one cluster', 'Clusters have very different densities', 'There are no neighbours', 'Data is one dimensional'], 1, 'Local.', 'It compares each point with its own neighbourhood.')
K.quiz('m', 'To score new points with LocalOutlierFactor you need', ['Nothing special', 'novelty=True', 'contamination=0', 'A label column'], 1, 'Novelty detection.', 'Then score_samples and predict work on new data.')
K.quiz('m', 'With 1% anomalies, which metric best shows how useful the alerts are?', ['Accuracy', 'PR AUC or precision at k', 'R squared', 'Inertia'], 1, 'Rare positives.', 'Accuracy rewards flagging nothing.')
K.quiz('m', 'contamination in IsolationForest sets', ['The number of trees', 'The share of points labelled anomalies by predict', 'The tree depth', 'The sample size'], 1, 'Threshold.', 'It does not change the scores.')
K.quiz('h', 'The elliptic envelope struggled on two separate blobs because', ['It is too slow', 'It assumes one ellipse, so the space between the blobs looks normal', 'It needs labels', 'It ignores scaling'], 1, 'One Gaussian.', 'A GMM fits several.')
K.quiz('h', 'The MAD is multiplied by 1.4826 so that', ['It becomes larger', 'It estimates &sigma; for normal data', 'It equals the IQR', 'It is always 1'], 1, '1 / 0.6745.', '&Phi;<sup>&minus;1</sup>(0.75) = 0.6745.')
K.quiz('h', 'Novelty detection differs from outlier detection in that', ['It uses labels', 'It trains on clean normal data and scores new data', 'It uses deep learning', 'It needs more trees'], 1, 'Training data.', 'Outlier detection trains on data that already has anomalies.')
K.quiz('x', 'In the style of a CMU 10-701 exam: the breakdown point of the median is', ['0%', '50%', '100%', '1 / n'], 1, 'Robustness.', 'Up to half the data can be wild before it moves arbitrarily.')
K.quiz('x', 'In the style of a Stanford CS246 exam: why does Isolation Forest subsample about 256 rows per tree?', ['To save memory only', 'Smaller samples reduce masking and swamping and still isolate anomalies', 'Because trees cannot be deeper', 'To make it supervised'], 1, 'Liu and others (2008).', 'Dense groups of anomalies are thinned out.')

K.calc('e', 'Mean 50, standard deviation 5. z score of 65?', '3', '(x &minus; mean)/sd.', ['65 &minus; 50 = 15.', '15 / 5.', eq('z = 3')], check=3)
K.calc('e', 'Q1 = 20, Q3 = 30. Upper IQR fence?', '45', 'Q3 + 1.5 IQR.', ['IQR = 10.', '1.5 &times; 10 = 15.', eq('30 + 15 = 45')], check=45)
K.calc('e', 'Values 1, 2, 3, 4, 100. MAD (unscaled)?', '1', 'Median of absolute deviations.', ['Median = 3.', 'Deviations 2, 1, 0, 1, 97.', eq('Median of those = 1')], check=1)
K.calc('m', 'Same values. Robust score of 100 with scale 1.4826?', '65.43', '(x &minus; median)/(1.4826 MAD).', ['100 &minus; 3 = 97.', '1.4826 &times; 1 = 1.4826.', eq('97 / 1.4826 = 65.43')], check=97 / 1.4826, tol=0.01)
K.calc('m', 'Isolation Forest c(n) for n = 256?', '10.24', '2(ln(n &minus; 1) + 0.5772) &minus; 2(n &minus; 1)/n.', ['ln 255 = 5.541.', '2(5.541 + 0.577) = 12.237.', eq('12.237 &minus; 1.992 = 10.24')], check=10.2448, tol=0.01)
K.calc('m', 'Average path length equals c(n). Anomaly score?', '0.5', '2<sup>&minus;h/c</sup>.', ['h / c = 1.', '2<sup>&minus;1</sup>.', eq('0.5')], check=0.5)
K.calc('m', '50 points flagged, 30 of them real anomalies. Precision?', '0.6', 'True flags / all flags.', ['30 real.', '50 flagged.', eq('30 / 50 = 0.6')], check=0.6)
K.calc('h', 'Average path length is twice c(n). Anomaly score?', '0.25', '2<sup>&minus;h/c</sup>.', ['h / c = 2.', '2<sup>&minus;2</sup>.', eq('0.25, clearly normal')], check=0.25)
K.calc('h', 'A point has lrd 0.2. Its neighbours have mean lrd 1.0. LOF?', '5', 'Neighbours’ lrd / own lrd.', ['Own lrd 0.2.', 'Neighbours 1.0.', eq('1.0 / 0.2 = 5')], check=5)
K.calc('x', 'In the style of a Stanford CS246 problem: 10,000 rows with 1% anomalies. The top 100 alerts have recall 0.8. Precision at 100?', '0.8', 'Count the caught anomalies.', ['1% of 10,000 = 100 anomalies.', 'Recall 0.8 means 80 caught.', eq('80 / 100 = 0.8')], check=0.8)

K.assign('robust_z', 'e', 'Robust scores',
         '<p>Write <code>robust_scores(values)</code> that returns (x &minus; median) / (1.4826 &times; MAD) for every value, rounded to 2 decimals, where MAD is the median of |x &minus; median|. Use statistics.median.</p>',
         """
import statistics


def robust_scores(values):
    # your code here
    pass
""", [('robust_scores([1, 2, 3, 4, 100])', [-1.35, -0.67, 0.0, 0.67, 65.43]), ('robust_scores([10, 12, 14])', [-0.67, 0.0, 0.67])],
         """
import statistics


def robust_scores(values):
    med = statistics.median(values)
    mad = statistics.median([abs(v - med) for v in values]) * 1.4826
    return [round((v - med) / mad, 2) + 0.0 for v in values]
""", 'Find the median, then the median of the absolute deviations, then scale.', '<p>Even with 100 in the data the other scores stay small, because one wild value cannot move the median or the MAD much.</p>')
K.assign('iqr_outliers', 'm', 'IQR outliers',
         '<p>Write <code>iqr_outliers(values)</code> that returns the sorted values below Q1 &minus; 1.5 IQR or above Q3 + 1.5 IQR. Compute quartiles by linear interpolation on the sorted values, as numpy does: the p-th quantile sits at position p &times; (n &minus; 1).</p>',
         """
def iqr_outliers(values):
    # your code here
    pass
""", [('iqr_outliers([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])', [100]), ('iqr_outliers([10, 10, 10, 10])', []), ('iqr_outliers([-50, 1, 2, 3, 4])', [-50])],
         """
def iqr_outliers(values):
    s = sorted(values)
    n = len(s)

    def quantile(p):
        pos = p * (n - 1)
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        return s[lo] + (s[hi] - s[lo]) * (pos - lo)

    q1, q3 = quantile(0.25), quantile(0.75)
    iqr = q3 - q1
    return [v for v in s if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr]
""", 'Sort, interpolate the quartiles, then compare with the fences.', '<p>In the first test Q1 = 3.25 and Q3 = 7.75, so the upper fence is 14.5 and only 100 is beyond it.</p>')
K.assign('lof_1d', 'h', 'Local outlier factor in one dimension',
         '<p>Write <code>lof_1d(values, k, i)</code> that returns the LOF of values[i], rounded to 3 decimals. Neighbours are the k closest other values. k-distance(o) is the distance to o’s k-th neighbour, reach(p, o) = max(k-distance(o), |p &minus; o|), lrd(p) = 1 / mean reach(p, o) over p’s neighbours, and LOF(p) = mean lrd(o) over p’s neighbours divided by lrd(p).</p>',
         """
def lof_1d(values, k, i):
    # your code here
    pass
""", [('lof_1d([1, 2, 4.4, 7, 15], 2, 4)', 2.48), ('lof_1d([1, 2, 4.4, 7, 15], 2, 1)', 0.923), ('lof_1d([0, 1, 3, 6, 10, 30], 3, 5)', 3.998)],
         """
def lof_1d(values, k, i):
    n = len(values)

    def neighbours(a):
        return sorted((j for j in range(n) if j != a), key=lambda j: abs(values[a] - values[j]))[:k]

    nb = [neighbours(a) for a in range(n)]
    kdist = [abs(values[a] - values[nb[a][-1]]) for a in range(n)]

    def lrd(a):
        mean_reach = sum(max(kdist[o], abs(values[a] - values[o])) for o in nb[a]) / k
        return 1 / mean_reach

    return round(sum(lrd(o) for o in nb[i]) / k / lrd(i), 3)
""", 'Build every point’s neighbours and k-distance first, then lrd, then the ratio.', '<p>These answers match scikit-learn’s LocalOutlierFactor on the same values. 15 is far beyond its neighbours 7 and 4.4, so its LOF is about 2.5, while 2 sits inside a tight pair and scores below 1.</p>')

K.must('Robust rules', 'Median and MAD score (x &minus; med)/(1.4826 MAD), flag above 3.5. IQR fences Q1 &minus; 1.5 IQR, Q3 + 1.5 IQR. z scores suffer masking.')
K.must('Isolation Forest', 'Random feature, random cut. Anomalies isolate fast. s = 2<sup>&minus;E[h]/c(n)</sup>, near 1 anomalous. 256 row samples. contamination sets the cut off.')
K.must('LOF', 'lrd = 1 / mean reachability distance. LOF = mean neighbour lrd / own lrd. Handles varying density. novelty=True for new points.')
K.must('Other models', 'One class SVM (nu, gamma), elliptic envelope (one robust Gaussian, Mahalanobis), GMM log density. Match the shape of normal.')
K.must('Evaluation', 'PR AUC, precision at k, recall at a budget. Not accuracy. Threshold from costs. Refit for drift.')
K.must('Modes', 'Outlier detection on dirty data, novelty detection on clean data, supervised models when labelled anomalies are plentiful.')

T = K.topic(
    slug='ml-anomaly', topic='ml-anomaly', step=(3, 'Patterns, anomalies and recommendations', 'ml-u3', 'Spot unusual records, find items that go together, and recommend what a person may like next.', 'Intermediate'),
    title='Anomaly detection', short='Anomaly detection', badge='3.1', minutes=50,
    lead='Find what does not fit: robust statistics that avoid masking, Isolation Forest and its random cuts, the local outlier factor for regions of different density, one class SVM and robust covariance, and how to judge detectors when anomalies are rare.',
    desc='anomaly detection, outlier detection, novelty detection, robust statistics, median absolute deviation, IQR, masking, Isolation Forest, path length, anomaly score, local outlier factor, local reachability density, one class SVM, elliptic envelope, Mahalanobis distance, PR AUC, precision at k.',
    summary='Robust scores, Isolation Forest, LOF, one class SVM and elliptic envelope, and evaluation for rare events.',
    keywords=['anomaly detection', 'outlier', 'Isolation Forest', 'local outlier factor', 'LOF', 'one class SVM', 'MAD', 'IQR', 'novelty detection', 'precision at k'],
    recap='<p>Anomaly detection learns what normal looks like and scores how far each record is from it. Use robust statistics for single features, Isolation Forest or LOF for tables, and judge detectors by the alerts a team can actually review.</p>',
    added='2026-11-13', leet=leet_items())
