# Supervised 3.2: bagging and random forests. Checked against Breiman, Bagging Predictors (1996) and Random Forests
# (Machine Learning, 2001), Geurts, Ernst and Wehenkel, Extremely Randomized Trees (2006), Hastie, Tibshirani and
# Friedman, The Elements of Statistical Learning chapters 8.7 and 15, An Introduction to Statistical Learning
# chapter 8.2, and the scikit-learn 1.8 user guide section 1.11.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-forest')
K = Kit()

K.code('bootstrap_by_hand', r'''
import random

random.seed(3)
rows = list(range(1, 11))
for b in range(3):
    sample = [random.choice(rows) for _ in rows]           # draw 10 rows with replacement
    out_of_bag = [r for r in rows if r not in sample]
    print("sample", b + 1, sorted(sample), " unique", len(set(sample)), " out of bag", out_of_bag)

shares = []
for b in range(300):
    sample = [random.randrange(1000) for _ in range(1000)]
    shares.append(len(set(sample)) / 1000)
print("average share of unique rows (n = 1000):", round(sum(shares) / len(shares), 3))
print("theory 1 - 1/e =", round(1 - 2.718281828 ** -1, 3))
''', long=True)

K.code('tree_vs_forest', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
models = {
    "one decision tree": DecisionTreeClassifier(random_state=0),
    "bagging 200 trees": BaggingClassifier(DecisionTreeClassifier(), n_estimators=200, random_state=0),
    "random forest 200": RandomForestClassifier(n_estimators=200, random_state=0),
}
for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5)
    print(name.ljust(18), "accuracy", round(scores.mean(), 3), " spread", round(scores.std(), 3))
''', long=True)

K.code('averaging', r'''
import numpy as np

rng = np.random.default_rng(0)
sigma = 1.0
for rho in [0.0, 0.3, 0.7]:
    for B in [1, 10, 100]:
        shared = rng.normal(0, 1, 20000)                      # the part all trees share
        own = rng.normal(0, 1, (B, 20000))                    # each tree's own noise
        preds = np.sqrt(rho) * shared + np.sqrt(1 - rho) * own
        var = preds.mean(axis=0).var()
        theory = rho * sigma ** 2 + (1 - rho) * sigma ** 2 / B
        print("correlation", rho, " trees", str(B).rjust(3), " variance of the average", round(float(var), 3), " theory", round(theory, 3))
''', long=True)

K.code('n_trees', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for n in [1, 5, 20, 100, 300]:
    forest = RandomForestClassifier(n_estimators=n, random_state=0).fit(X_train, y_train)
    print("trees", str(n).rjust(3), " train", round(forest.score(X_train, y_train), 3), " test", round(forest.score(X_test, y_test), 3))
''', long=True)

K.code('oob', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
forest = RandomForestClassifier(n_estimators=300, oob_score=True, random_state=0).fit(X_train, y_train)
print("out of bag accuracy:", round(forest.oob_score_, 3))
print("test accuracy:", round(forest.score(X_test, y_test), 3))
''')

K.code('max_features', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for mf in [1, "sqrt", 0.5, None]:
    forest = RandomForestClassifier(n_estimators=200, max_features=mf, random_state=0).fit(X_train, y_train)
    votes = np.array([tree.predict(X_test) for tree in forest.estimators_])
    agree = np.mean([np.mean(votes[i] == votes[j]) for i in range(20) for j in range(i + 1, 20)])
    print("max_features", str(mf).ljust(5), " trees agree", round(float(agree), 3), " test", round(forest.score(X_test, y_test), 3))
''', long=True)

K.code('forest_regression', r'''
from sklearn.datasets import load_diabetes
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeRegressor

X, y = load_diabetes(return_X_y=True)
models = {
    "linear regression": LinearRegression(),
    "one tree": DecisionTreeRegressor(random_state=0),
    "random forest": RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=0),
    "extra trees": ExtraTreesRegressor(n_estimators=200, min_samples_leaf=5, random_state=0),
}
for name, model in models.items():
    print(name.ljust(17), "R2", round(cross_val_score(model, X, y, cv=5, scoring="r2").mean(), 3))
''', long=True)

K.lesson('idea', 'Many trees are wiser than one', f'''
{src('Breiman, Bagging Predictors (1996) and Random Forests (2001), Geurts, Ernst and Wehenkel (2006), The Elements of Statistical Learning chapters 8.7 and 15, An Introduction to Statistical Learning chapter 8.2, and the scikit-learn 1.8 user guide section 1.11.')}
{viz('mlforestvote')}
{wwh('A <b>random forest</b> trains many decision trees, each on a different random version of the data, and combines them: a majority vote for classification, an average for regression.',
     'A single deep tree has low bias but very high variance: it changes a lot when the data changes. Averaging many such trees keeps the low bias and removes much of the variance, so a forest is far more accurate and stable than one tree, with almost no tuning.',
     'Two sources of randomness make the trees differ. Each tree trains on a <b>bootstrap sample</b> of the rows (bagging), and at every split it may only look at a random subset of the features (max_features). Then predictions are averaged.')}
{run('tree_vs_forest')}
{note('One tree scores 0.917. Bagging 200 trees lifts that to 0.96, and the random forest also reaches 0.96. On this dataset the extra feature randomness adds little over bagging, but on data with a few dominant features it usually helps more, as the max_features lesson shows.', 'tip')}
{scene('guessing the weight of an ox', '<p>At a country fair in 1906, Francis Galton collected about 800 guesses of an ox’s weight. Single guesses were often far off, but the middle of all the guesses was within 1% of the true weight. The errors pointed in different directions and cancelled. A forest relies on the same effect, which only works when the guesses are independent enough.</p>')}
''', kw=['random forest', 'ensemble', 'bagging', 'majority vote', 'variance reduction', 'RandomForestClassifier'])

K.lesson('bagging', 'Bootstrap samples and bagging', f'''
{viz('mlbootstrap')}
{wwh('<b>Bagging</b> (bootstrap aggregating) trains each model on a <b>bootstrap sample</b>: n rows drawn at random with replacement from the n training rows. Then it averages the models.',
     'Bootstrap samples are different from each other but each looks like the original data, so every tree is a reasonable model with its own mistakes. On average a sample contains 63.2% of the distinct rows, and the remaining 36.8% (out of bag) can test that tree for free.',
     'BaggingClassifier(DecisionTreeClassifier(), n_estimators=200) does bagging with any model. RandomForestClassifier does it for trees and adds random features at each split.')}
{run('bootstrap_by_hand')}
{fx('Chance a row is left out', 'P(out of bag) = (1 &minus; 1/n)<sup>n</sup> &rarr; 1/e &asymp; 0.368', 'So about 63.2% of the rows are in each sample.', key=True)}
''', kw=['bootstrap sample', 'bagging', 'sampling with replacement', 'out of bag', '63.2 percent', 'BaggingClassifier'])

K.lesson('why', 'Why averaging works, and why trees must differ', f'''
{wwh('Averaging B predictions that each have variance &sigma;<sup>2</sup> and pairwise correlation &rho; gives variance &rho;&sigma;<sup>2</sup> + (1 &minus; &rho;)&sigma;<sup>2</sup>/B.',
     'The second part shrinks as you add trees, but the first part, &rho;&sigma;<sup>2</sup>, never does. So adding trees helps only up to a point, and the real gain comes from making the trees <b>less correlated</b>. That is exactly what the random feature choice at each split does.',
     'The program simulates averaging with correlation 0, 0.3 and 0.7. With no correlation, 100 trees cut the variance to 1%. With correlation 0.7 the variance stays near 0.7 however many trees you add.')}
{run('averaging')}
{fx('Variance of an average', 'Var = &rho;&sigma;<sup>2</sup> + (1 &minus; &rho;)&sigma;<sup>2</sup> / B', 'More trees shrink the second term, less correlation shrinks the first.', key=True)}
{note('This formula is the heart of random forests and appears in The Elements of Statistical Learning, equation 15.1. Lower correlation between trees matters more than more trees.', 'exam')}
''', kw=['variance of an average', 'correlation between trees', 'decorrelation', 'bias variance', 'ensemble theory'])

K.lesson('tune', 'Number of trees, out of bag score and max_features', f'''
{wwh('The main settings are <b>n_estimators</b> (number of trees), <b>max_features</b> (features tried at each split) and the tree size limits such as min_samples_leaf. The <b>out of bag (OOB) score</b> estimates test accuracy without a separate validation set.',
     'More trees never overfit, they only cost time, so the question is when the curve flattens. max_features controls the trade off between strong individual trees and diverse trees. OOB scoring saves data when it is scarce.',
     'Start with 200 to 500 trees, max_features="sqrt" for classification (the scikit-learn default) and 1.0 for regression, then tune max_features and min_samples_leaf with cross validation. Set oob_score=True to get forest.oob_score_.')}
{run('n_trees')}
{note('Test accuracy rises from 0.889 with one tree to 0.953 with 100 trees, then stays flat at 300. Training accuracy is 1.0 from 20 trees on, but that is not overfitting: each tree memorises its own sample and the vote still generalises.', 'tip')}
{run('oob')}
{run('max_features')}
{note('With one random feature per split the trees agree least (0.864) but each is weak. With all features (None) the forest is just bagging: the trees agree more (0.919) and test accuracy drops to 0.924. sqrt, here 5 of 30 features, balances the two and scores best (0.953).', 'exam')}
''', kw=['n_estimators', 'max_features', 'out of bag score', 'oob_score', 'min_samples_leaf', 'tuning random forests'])

K.lesson('regress', 'Forests for regression, and extra trees', f'''
{wwh('<b>RandomForestRegressor</b> averages the predictions of regression trees. <b>Extra trees</b> (extremely randomized trees) go further and choose the cut points at random too, instead of searching for the best one.',
     'Forests give strong regression models with little tuning. Extra trees are faster to train and the extra randomness often lowers variance a little more. But no model wins everywhere: on small, mostly linear data a linear model can beat any forest.',
     'Use the same settings as for classification. Averaging trees gives smoother predictions than one tree, but still flat beyond the range of the training targets.')}
{run('forest_regression')}
{note('On the diabetes data (442 rows, 10 features, mostly linear effects) one tree has a negative R&sup2;, worse than predicting the mean. The forest lifts it to 0.442 and extra trees to 0.479, yet plain linear regression still scores 0.482. Always compare with a simple baseline.', 'tip')}
''', kw=['RandomForestRegressor', 'ExtraTreesRegressor', 'extremely randomized trees', 'regression forest', 'baseline comparison'])

K.lesson('versus', 'Forests compared', f'''
{versus('One tree, a forest and boosting (next chapter)', ['', 'One tree', 'Random forest', 'Gradient boosting'], [
    ['How trees are built', 'One deep tree', 'Many deep trees, in parallel, independent', 'Many shallow trees, in sequence, each fixing the last'],
    ['Main error reduced', 'None', 'Variance', 'Bias (and variance with care)'],
    ['Tuning needed', 'Depth or pruning', 'Little (works well with defaults)', 'More (learning rate, depth, number of trees)'],
    ['Overfits with more trees', 'Not applicable', 'No', 'Yes, without early stopping'],
    ['Interpretability', 'High', 'Lower (importances)', 'Lower (importances, SHAP)'],
    ['Typical accuracy on tables', 'Fair', 'Very good', 'Often the best']],
    'a random forest is the safest strong default for tabular data, and gradient boosting usually wins once tuned.')}
''', kw=['random forest vs decision tree', 'random forest vs gradient boosting', 'bagging vs boosting'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Bagged prediction (regression)', 'f̂(x) = (1/B) &Sigma;<sub>b</sub> f̂<sub>b</sub>(x)', 'Average of B trees.', key=True),
     fx('Bagged prediction (classification)', 'ŷ = majority vote of ŷ<sub>b</sub>, or argmax of the mean class probabilities', 'scikit-learn averages probabilities.', key=True),
     fx('Out of bag share', '(1 &minus; 1/n)<sup>n</sup> &rarr; e<sup>&minus;1</sup> &asymp; 0.368', 'Rows a tree never saw.', key=True),
     fx('Variance of the forest', '&rho;&sigma;<sup>2</sup> + (1 &minus; &rho;)&sigma;<sup>2</sup>/B', 'Decorrelate the trees.', key=True),
     fx('Default max_features', 'classification &radic;p, regression p (all)', 'p is the number of features.'))}
{steps('Worked example: majority vote of three independent classifiers', [
    'Each of three classifiers is right 70% of the time, independently.',
    'The vote is right when at least 2 of 3 are right.',
    'Exactly 2 right: 3 &times; 0.7<sup>2</sup> &times; 0.3 = 0.441. All 3 right: 0.7<sup>3</sup> = 0.343.',
    eq('P(vote right) = 0.441 + 0.343 = 0.784'),
    'The vote beats each member (0.70). With correlated members the gain is smaller, which is why forests decorrelate their trees.'])}
{deep('Breiman’s strength and correlation bound', '<p>Breiman (2001) proved that the generalisation error of a random forest is at most &rho;&#772;(1 &minus; s<sup>2</sup>)/s<sup>2</sup>, where s is the strength (the average margin by which the trees vote for the right class) and &rho;&#772; is the mean correlation between the trees. Error falls when the trees are stronger and less correlated, and max_features trades one against the other. He also showed by the strong law of large numbers that the forest error converges as trees are added, which is why more trees never overfit. Later work (Wager and Athey, 2018) built honest forests with valid confidence intervals, used for estimating treatment effects.</p>')}
''', kw=['bagging formula', 'majority vote', 'out of bag', 'forest variance', 'strength and correlation', 'Breiman bound'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A random forest asks hundreds of slightly different decision trees and goes with the majority. Their mistakes cancel out.</p>',
    '<p>Train forests in scikit-learn, set n_estimators, max_features and min_samples_leaf, read the OOB score and compare with a single tree and a linear baseline.</p>',
    '<p>Explain bootstrap sampling and the 63.2% rule, derive the variance of an average of correlated trees, and explain why more trees never overfit.</p>',
    '<p>Study Breiman’s strength and correlation bound, consistency results for forests, quantile regression forests, isolation forests for anomalies, and generalised random forests for causal effects (Athey, Tibshirani and Wager, 2019).</p>')}
{grow('Explain why many voting trees beat one.',
      'Train, tune and validate forests with OOB scores.',
      'Analyse forest variance, correlation and theory.')}
''', kw=['beginner', 'expert', 'quantile regression forest', 'isolation forest', 'causal forest'])

lc(169, 'Majority Element', 'majority-element', 'e', 'One pass vote counting', 'Boyer and Moore voting: keep a candidate and a count. A matching value adds 1, a different value takes 1 away, and at 0 the next value becomes the candidate. The majority always survives, just as a forest’s majority survives the noisy trees.', r'''
def majority_element(nums):
    candidate = None
    count = 0
    for x in nums:
        if count == 0:
            candidate = x
        if x == candidate:
            count = count + 1
        else:
            count = count - 1
    return candidate
''', [('majority_element([3, 2, 3])', 3), ('majority_element([2, 2, 1, 1, 1, 2, 2])', 2)])
lc(229, 'Majority Element II', 'majority-element-ii', 'm', 'Count, then keep values above n/3', 'Count every value and keep those that appear more than n/3 times. At most two values can do that. (Boyer and Moore with two candidates does it in constant memory.)', r'''
def majority_element_ii(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    return sorted([x for x in counts if counts[x] > len(nums) // 3])
''', [('majority_element_ii([3, 2, 3])', [3]), ('majority_element_ii([1, 2])', [1, 2])])
lc(1287, 'Element Appearing More Than 25% In Sorted Array', 'element-appearing-more-than-25-in-sorted-array', 'e', 'Compare with the value a quarter further on', 'In a sorted array a value that fills more than a quarter must equal the value n/4 positions later. Check each position against that one.', r'''
def find_special_integer(arr):
    step = len(arr) // 4
    for i in range(len(arr) - step):
        if arr[i] == arr[i + step]:
            return arr[i]
    return arr[0]
''', [('find_special_integer([1, 2, 2, 6, 6, 6, 6, 7, 10])', 6), ('find_special_integer([1, 1])', 1)])
lc(347, 'Top K Frequent Elements', 'top-k-frequent-elements', 'm', 'Count, then sort by count', 'Count each value and return the k values with the largest counts. Sorting by count is the simple way. Buckets by count make it linear.', r'''
def top_k_frequent(nums, k):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    ordered = sorted(counts, key=lambda v: (-counts[v], v))
    return ordered[:k]
''', [('top_k_frequent([1, 1, 1, 2, 2, 3], 2)', [1, 2]), ('top_k_frequent([1], 1)', [1])])
lc(2404, 'Most Frequent Even Element', 'most-frequent-even-element', 'e', 'Count only the even values', 'Count the even values. Return the one with the largest count, the smallest value when counts tie, or &minus;1 when there are no even values.', r'''
def most_frequent_even(nums):
    counts = {}
    for x in nums:
        if x % 2 == 0:
            counts[x] = counts.get(x, 0) + 1
    if not counts:
        return -1
    return min(counts, key=lambda v: (-counts[v], v))
''', [('most_frequent_even([0, 1, 2, 2, 4, 4, 1])', 2), ('most_frequent_even([29, 47, 21, 41, 13, 37, 25, 7])', -1)])
lc(1394, 'Find Lucky Integer in an Array', 'find-lucky-integer-in-an-array', 'e', 'A value whose count equals itself', 'Count every value. A lucky integer appears exactly as many times as its value. Return the largest one, or &minus;1.', r'''
def find_lucky(arr):
    counts = {}
    for x in arr:
        counts[x] = counts.get(x, 0) + 1
    best = -1
    for x in counts:
        if counts[x] == x and x > best:
            best = x
    return best
''', [('find_lucky([2, 2, 3, 4])', 2), ('find_lucky([1, 2, 2, 3, 3, 3])', 3)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>A forest decides by vote. These problems practise counting votes: the majority element with Boyer and Moore voting, values above a third, a value filling a quarter of a sorted array, the top k most frequent values, the most frequent even value, and values whose count equals themselves. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'majority vote', 'Boyer Moore', 'counting', 'frequency'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>random forest</b> averages many decision trees: majority vote (or mean probability) for classes, mean for numbers.',
    '<b>Bagging</b>: each tree trains on a bootstrap sample. About 63.2% of rows are in each sample, the rest are <b>out of bag</b>.',
    'Random <b>max_features</b> at each split makes the trees less correlated.',
    'Variance of the average = &rho;&sigma;<sup>2</sup> + (1 &minus; &rho;)&sigma;<sup>2</sup>/B: decorrelation matters more than more trees.',
    'More trees never overfit. Use 200 to 500, tune max_features and min_samples_leaf, read oob_score_.',
    'Extra trees also randomise the cut points. Always compare with a simple baseline.'],
    'Supervised 3.3 is boosting: shallow trees built one after another, each fixing the errors of the ones before.')}
{files('Three tasks: out of bag rows, a majority vote, and the variance of a forest.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A random forest combines trees by', ['Picking the deepest tree', 'Voting or averaging', 'Multiplying predictions', 'Using only the first tree'], 1, 'Wisdom of crowds.', 'Classification votes (or averages probabilities), regression averages.')
K.quiz('e', 'A bootstrap sample is drawn', ['Without replacement', 'With replacement', 'Only from the test set', 'From the features'], 1, 'Rows can repeat.', 'n rows drawn with replacement.')
K.quiz('e', 'Adding more trees to a random forest', ['Causes overfitting', 'Does not cause overfitting, only costs time', 'Always lowers training accuracy', 'Removes the need for data'], 1, 'Averages converge.', 'The forest error settles as trees are added.')
K.quiz('e', 'Out of bag rows are', ['Rows with missing values', 'Rows a given tree did not train on', 'Test rows only', 'Duplicated rows'], 1, 'Left out of the sample.', 'They test that tree for free.')
K.quiz('m', 'Random forests mainly reduce', ['Bias', 'Variance', 'Training time', 'The number of features'], 1, 'Deep trees are low bias, high variance.', 'Averaging removes much of the variance.')
K.quiz('m', 'max_features="sqrt" with 100 features tries how many at each split?', ['100', '50', '10', '1'], 2, '&radic;100.', 'A random 10 features at every split.')
K.quiz('m', 'Why limit features at each split?', ['To speed up prediction only', 'To make trees less correlated', 'To increase bias on purpose only', 'To avoid scaling'], 1, '&rho;&sigma;<sup>2</sup> term.', 'Less correlated trees average better.')
K.quiz('m', 'About what share of distinct rows does a bootstrap sample contain?', ['50%', '63%', '90%', '100%'], 1, '1 &minus; 1/e.', '63.2% on average for large n.')
K.quiz('m', 'Extra trees differ from random forests because they', ['Use no bootstrap and pick random cut points', 'Use deeper trees only', 'Use linear models', 'Need scaling'], 0, 'Extremely randomised.', 'By default ExtraTrees uses the whole data and random thresholds.')
K.quiz('h', 'With correlation &rho; between trees, as B grows the variance of the forest tends to', ['0', '&rho;&sigma;<sup>2</sup>', '&sigma;<sup>2</sup>', '&sigma;<sup>2</sup>/B'], 1, 'The shared part stays.', 'The (1 &minus; &rho;)&sigma;<sup>2</sup>/B term vanishes.')
K.quiz('h', 'Bagging linear regression models helps', ['A lot', 'Very little, because linear models are low variance', 'Only with scaling', 'It is impossible'], 1, 'Bagging cuts variance.', 'Stable models gain little from averaging.')
K.quiz('h', 'A forest scores 1.0 on training data and 0.95 on test data. This most likely means', ['Severe overfitting that more trees will worsen', 'Normal behaviour: trees fit their samples but the vote generalises', 'A data leak for sure', 'Too few features'], 1, 'Compare with OOB.', 'Check the OOB score, which is a fair estimate.')
K.quiz('x', 'In the style of a Stanford CS229 exam: for i.i.d. bootstrap draws from n rows, the probability that a given row appears at least once tends to', ['0.5', '1 &minus; 1/e &asymp; 0.632', '1/e', '1'], 1, '1 &minus; (1 &minus; 1/n)<sup>n</sup>.', 'The limit of (1 &minus; 1/n)<sup>n</sup> is 1/e.')
K.quiz('x', 'In the style of a CMU 10-701 exam: Breiman’s bound says forest error falls when', ['Trees are weaker and more correlated', 'Trees are stronger and less correlated', 'Trees are shallower always', 'There are fewer trees'], 1, 'Strength s and correlation &rho;.', 'Error &le; &rho;(1 &minus; s<sup>2</sup>)/s<sup>2</sup>.')

K.calc('e', 'Five trees vote 1, 1, 0, 1, 0. Share of votes for class 1?', '0.6', 'Count the ones.', ['Three votes for 1.', 'Five trees.', eq('3 / 5 = 0.6')], check=0.6)
K.calc('e', 'Three regression trees predict 10, 12 and 17. Forest prediction?', '13', 'Average.', ['Sum 39.', '3 trees.', eq('39 / 3 = 13')], check=13)
K.calc('e', '36 features, max_features = sqrt. Features tried per split?', '6', '&radic;36.', ['p = 36.', 'Square root.', eq('6')], check=6)
K.calc('m', 'n = 10 rows. Chance a given row is out of bag, 3 decimals?', '0.349', '(1 &minus; 1/n)<sup>n</sup>.', ['1 &minus; 1/10 = 0.9.', 'Raise to the power 10.', eq('0.9<sup>10</sup> = 0.349')], check=0.349)
K.calc('m', 'Limit of the share of distinct rows in a bootstrap sample, 3 decimals?', '0.632', '1 &minus; 1/e.', ['1/e = 0.368.', '1 &minus; 0.368.', eq('0.632')], check=0.632)
K.calc('m', 'Uncorrelated trees, &sigma;<sup>2</sup> = 4, B = 100. Variance of the average?', '0.04', '&sigma;<sup>2</sup>/B.', ['&rho; = 0, so only the second term.', '4 / 100.', eq('0.04')], check=0.04)
K.calc('m', '&rho; = 0.5, &sigma;<sup>2</sup> = 1, B = 10. Variance of the average?', '0.55', 'Both terms.', ['&rho;&sigma;<sup>2</sup> = 0.5.', '(1 &minus; 0.5) &times; 1 / 10 = 0.05.', eq('0.5 + 0.05 = 0.55')], check=0.55)
K.calc('h', 'Three independent classifiers, each right 70% of the time. Majority vote accuracy, 3 decimals?', '0.784', 'At least 2 of 3.', ['Exactly 2: 3 &times; 0.49 &times; 0.3 = 0.441.', 'All 3: 0.343.', eq('0.441 + 0.343 = 0.784')], check=0.784)
K.calc('h', 'n = 1,000 rows. Expected number of out of bag rows for one tree, nearest whole number?', '368', 'n &times; (1 &minus; 1/n)<sup>n</sup>.', ['(0.999)<sup>1000</sup> &asymp; 0.3677.', 'Times 1,000.', eq('&asymp; 368')], check=368)
K.calc('x', 'In the style of an MIT 6.867 problem: &rho; = 0.3, &sigma;<sup>2</sup> = 2. Variance of the forest as B &rarr; &infin;?', '0.6', 'Only &rho;&sigma;<sup>2</sup> is left.', ['The second term goes to 0.', '&rho;&sigma;<sup>2</sup> = 0.3 &times; 2.', eq('0.6')], check=0.6)

K.assign('oob', 'e', 'Out of bag rows',
         '<p>Write <code>oob_rows(n, draws)</code>. Rows are numbered 1 to n and draws is the list of rows in a bootstrap sample. Return the sorted list of rows that were never drawn.</p>',
         '''
def oob_rows(n, draws):
    # your code here
    pass
''', [('oob_rows(5, [1, 1, 3, 5, 5])', [2, 4]), ('oob_rows(3, [1, 2, 3])', []), ('oob_rows(4, [2, 2, 2, 2])', [1, 3, 4])],
         '''
def oob_rows(n, draws):
    seen = set(draws)
    return [r for r in range(1, n + 1) if r not in seen]
''', 'Put the draws in a set, then keep every row from 1 to n that is not in it.', '<p>These rows can score the tree without a separate validation set.</p>')
K.assign('vote', 'm', 'Majority vote',
         '<p>Write <code>majority_vote(predictions)</code> for a list of class labels from the trees. Return the label with the most votes. If several tie, return the smallest label.</p>',
         '''
def majority_vote(predictions):
    # your code here
    pass
''', [('majority_vote(["cat", "dog", "cat"])', 'cat'), ('majority_vote([1, 0, 1, 0])', 0), ('majority_vote([2, 2, 3, 3, 3])', 3)],
         '''
def majority_vote(predictions):
    counts = {}
    for p in predictions:
        counts[p] = counts.get(p, 0) + 1
    return min(counts, key=lambda label: (-counts[label], label))
''', 'Count each label, then pick the largest count and the smallest label on ties.', '<p>scikit-learn actually averages the class probabilities of the trees, which breaks most ties naturally.</p>')
K.assign('forestvar', 'm', 'Variance of a forest',
         '<p>Write <code>forest_variance(rho, sigma2, trees)</code> that returns rho &times; sigma2 + (1 &minus; rho) &times; sigma2 / trees, rounded to 4 decimals.</p>',
         '''
def forest_variance(rho, sigma2, trees):
    # your code here
    pass
''', [('forest_variance(0, 4, 100)', 0.04), ('forest_variance(0.5, 1, 10)', 0.55), ('forest_variance(0.3, 2, 1)', 2.0)],
         '''
def forest_variance(rho, sigma2, trees):
    return round(rho * sigma2 + (1 - rho) * sigma2 / trees, 4)
''', 'Type the formula and round.', '<p>One tree keeps the full variance. Many uncorrelated trees remove almost all of it.</p>')

K.must('Idea', 'Average many trees: vote or mean probability for classes, mean for numbers. Reduces variance, keeps low bias.')
K.must('Bagging', 'Bootstrap sample of n rows with replacement. About 63.2% distinct rows, 36.8% out of bag (OOB score).')
K.must('Randomness', 'max_features at each split: sqrt(p) for classification, all for regression. Decorrelates trees.')
K.must('Variance', '&rho;&sigma;<sup>2</sup> + (1 &minus; &rho;)&sigma;<sup>2</sup>/B. Lower &rho; beats more B.')
K.must('Settings', 'n_estimators 200 to 500 (more never overfits), max_features, min_samples_leaf, oob_score=True, n_jobs=-1.')
K.must('Variants', 'BaggingClassifier for any model, ExtraTrees (random cuts, no bootstrap). Compare with a linear baseline.')

T = K.topic(
    slug='ml-forest', topic='ml-forest', step=(3, 'Trees and ensembles', 'ml-s3', 'Ask the data a chain of yes or no questions, then combine hundreds of such trees into the strongest models for tables.', 'Intermediate'),
    title='Random forests: many trees vote', short='Random forests', badge='3.2', minutes=50,
    lead='Learn bagging and random forests: bootstrap samples and out of bag rows, why averaging reduces variance and why the trees must differ, tuning the number of trees and max_features, regression forests and extra trees.',
    desc='random forest, bagging, bootstrap sample, sampling with replacement, out of bag score, majority vote, variance reduction, correlation between trees, max_features, n_estimators, min_samples_leaf, RandomForestRegressor, ExtraTrees, Breiman, strength and correlation.',
    summary='Bagging and bootstrap samples, why averaging works, tuning trees and features, OOB scores, regression forests and extra trees.',
    keywords=['random forest', 'bagging', 'bootstrap', 'out of bag', 'max_features', 'n_estimators', 'ensemble', 'variance reduction', 'extra trees', 'RandomForestClassifier'],
    recap='<p>A forest trains many different trees on bootstrap samples with random features and lets them vote. It reduces variance and works well with defaults.</p>',
    added='2026-11-13', leet=leet_items())
