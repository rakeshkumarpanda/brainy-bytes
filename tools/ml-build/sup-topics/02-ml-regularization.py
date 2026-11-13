# Supervised 1.2: polynomial regression, overfitting and regularisation. Checked against James, Witten, Hastie and
# Tibshirani, An Introduction to Statistical Learning (2nd edition) chapters 6.2 and 7.1, Hastie, Tibshirani and
# Friedman, The Elements of Statistical Learning (2nd edition) chapter 3.4, Tibshirani, Regression Shrinkage and
# Selection via the Lasso (JRSS B, 1996), Zou and Hastie, Regularization and Variable Selection via the Elastic Net
# (JRSS B, 2005), and the scikit-learn 1.8 user guide sections 1.1.2 to 1.1.5.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-regularization')
K = Kit()

K.code('poly_overfit', r'''
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 1, 15)).reshape(-1, 1)
y = np.sin(2 * np.pi * x.ravel()) + rng.normal(0, 0.2, 15)
x_test = rng.uniform(0, 1, 200).reshape(-1, 1)
y_test = np.sin(2 * np.pi * x_test.ravel()) + rng.normal(0, 0.2, 200)

for degree in [1, 3, 6, 9, 12]:
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression()).fit(x, y)
    train = mean_squared_error(y, model.predict(x))
    test = mean_squared_error(y_test, model.predict(x_test))
    print("degree", str(degree).rjust(2), " train MSE", round(train, 3), " test MSE", round(test, 2))
''')

K.code('ridge_shrink', r'''
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge

rng = np.random.default_rng(1)
n = 40
size = rng.normal(0, 1, n)
rooms = size + rng.normal(0, 0.05, n)          # almost a copy of size
y = 3 * size + rng.normal(0, 1, n)
X = np.column_stack([size, rooms])

print("plain least squares:", np.round(LinearRegression().fit(X, y).coef_, 2).tolist())
for alpha in [0.1, 1, 10, 100]:
    print("ridge alpha", str(alpha).rjust(5), ":", np.round(Ridge(alpha=alpha).fit(X, y).coef_, 2).tolist())
''')

K.code('lasso_sparse', r'''
import numpy as np
from sklearn.linear_model import Lasso, Ridge

rng = np.random.default_rng(2)
X = rng.normal(0, 1, (100, 10))
true_w = np.array([4, -3, 2, 0, 0, 0, 0, 0, 0, 0])
y = X @ true_w + rng.normal(0, 1, 100)

for alpha in [0.01, 0.1, 0.5, 1.0]:
    w = Lasso(alpha=alpha).fit(X, y).coef_
    print("lasso alpha", str(alpha).ljust(4), " non zero:", int(np.sum(w != 0)), " weights:", (np.round(w, 1) + 0.0).tolist())
print("ridge alpha 10   non zero:", int(np.sum(Ridge(alpha=10).fit(X, y).coef_ != 0)))
''')

K.code('elastic_net', r'''
import numpy as np
from sklearn.linear_model import ElasticNet, Lasso

rng = np.random.default_rng(3)
n = 100
base = rng.normal(0, 1, n)
a = base + rng.normal(0, 0.1, n)               # three almost identical features
b = base + rng.normal(0, 0.1, n)
c = base + rng.normal(0, 0.1, n)
noise = rng.normal(0, 1, (n, 2))
X = np.column_stack([a, b, c, noise])
y = 3 * base + rng.normal(0, 0.5, n)

print("lasso:      ", (np.round(Lasso(alpha=0.1).fit(X, y).coef_, 2) + 0.0).tolist())
print("elastic net:", (np.round(ElasticNet(alpha=0.1, l1_ratio=0.3).fit(X, y).coef_, 2) + 0.0).tolist())
''')

K.code('choose_alpha', r'''
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

def poly(model):
    return make_pipeline(PolynomialFeatures(2), StandardScaler(), model)

plain = poly(LinearRegression()).fit(X_train, y_train)
ridge = poly(RidgeCV(alphas=[0.1, 1, 10, 100, 1000])).fit(X_train, y_train)
lasso = poly(LassoCV(cv=5, random_state=0, max_iter=20000)).fit(X_train, y_train)
print("65 polynomial features")
print("plain    test R2:", round(plain.score(X_test, y_test), 3))
print("RidgeCV  test R2:", round(ridge.score(X_test, y_test), 3), " best alpha:", ridge[-1].alpha_)
print("LassoCV  test R2:", round(lasso.score(X_test, y_test), 3), " best alpha:", round(lasso[-1].alpha_, 3),
      " features kept:", int((lasso[-1].coef_ != 0).sum()))
''')

K.code('ridge_formula', r'''
import numpy as np
from sklearn.linear_model import Ridge

rng = np.random.default_rng(4)
X = rng.normal(0, 1, (20, 3))
y = X @ np.array([1.0, 2.0, -1.0]) + rng.normal(0, 0.3, 20)
lam = 5.0

w = np.linalg.solve(X.T @ X + lam * np.eye(3), X.T @ y)       # ridge closed form
print("by formula:", np.round(w, 4).tolist())
print("sklearn:   ", np.round(Ridge(alpha=lam, fit_intercept=False).fit(X, y).coef_, 4).tolist())
''')

K.lesson('overfit', 'Curves, underfitting and overfitting', f'''
{src('James, Witten, Hastie and Tibshirani, An Introduction to Statistical Learning chapters 6.2 and 7.1, Hastie, Tibshirani and Friedman, The Elements of Statistical Learning chapter 3.4, Tibshirani (1996), Zou and Hastie (2005), and the scikit-learn 1.8 user guide.')}
{viz('mlpolyfit')}
{wwh('<b>Polynomial regression</b> is linear regression on x, x<sup>2</sup>, x<sup>3</sup> and so on, so it can fit curves. A model that is too simple <b>underfits</b>: it misses the pattern. A model that is too flexible <b>overfits</b>: it memorises the noise in the training data and fails on new data.',
     'Every model has to find the right amount of flexibility. Overfitting is the most common reason a model that looked great in a notebook fails in real use.',
     'Fit models of growing complexity and compare training error with test (or validation) error. Training error keeps falling. Test error falls, then rises again once the model starts fitting noise. Pick the complexity at the bottom of the test curve, or keep a flexible model and add a penalty (regularisation).')}
{run('poly_overfit')}
{table(['', 'Underfitting', 'Good fit', 'Overfitting'], [
    ['Training error', 'High', 'Low', 'Very low'],
    ['Test error', 'High', 'Low', 'High'],
    ['Also called', 'High bias', 'Balanced', 'High variance'],
    ['Fixes', 'More features, a more flexible model, less penalty', 'Keep it', 'More data, fewer features, simpler model, more penalty']])}
{scene('learning for an exam', '<p>One student only reads the chapter titles and fails (underfitting). Another memorises last year’s answers word for word and fails too, because this year’s questions are different (overfitting). The student who learns the ideas does well on new questions. That is the model we want.</p>')}
''', kw=['polynomial regression', 'underfitting', 'overfitting', 'bias', 'variance', 'model complexity', 'train vs test error'])

K.lesson('ridge', 'Ridge regression (L2): keep weights small', f'''
{viz('mlreg')}
{wwh('<b>Ridge regression</b> adds a penalty &alpha; &Sigma; w<sub>j</sub><sup>2</sup> to the squared error. The model now has to balance fitting the data with keeping its weights small.',
     'Huge weights are a sign of overfitting: the curve bends wildly to pass through every point. Ridge also fixes multicollinearity: when two features are almost copies, plain least squares gives unstable, opposite weights, while ridge shares the weight between them.',
     'Minimise ||y &minus; Xw||<sup>2</sup> + &alpha;||w||<sup>2</sup>. The solution is w = (X<sup>T</sup>X + &alpha;I)<sup>&minus;1</sup>X<sup>T</sup>y, which always exists. Larger &alpha; means stronger shrinking. &alpha; = 0 is plain least squares. Scale the features first, because the penalty treats all weights the same.')}
{run('ridge_shrink')}
{note('In the program, size and rooms are almost the same feature. Least squares gives them 2.55 and 0.44, an arbitrary split. Ridge with &alpha; = 1 gives 1.49 and 1.45: a fair share, and much more stable if the data changes a little.', 'tip')}
{run('ridge_formula')}
''', kw=['ridge regression', 'L2 penalty', 'shrinkage', 'alpha', 'multicollinearity', 'Ridge', 'closed form'])

K.lesson('lasso', 'Lasso (L1): weights that become exactly zero', f'''
{wwh('<b>Lasso</b> adds the penalty &alpha; &Sigma; |w<sub>j</sub>| instead of squares. It shrinks weights too, but it pushes many of them all the way to <b>exactly 0</b>, so it also selects features.',
     'When you have many features and suspect that only a few matter, lasso gives a smaller model that is easier to explain and cheaper to run, and it often predicts better because it ignores the noise features.',
     'The absolute value has a sharp corner at 0. For a weak feature, the penalty’s pull towards 0 is stronger than what the data gains from a small weight, so the best weight is exactly 0. scikit-learn solves lasso with coordinate descent, updating one weight at a time with a "soft threshold".')}
{run('lasso_sparse')}
{fx('Soft threshold (one lasso update)', 'w<sub>j</sub> = sign(&rho;) max(|&rho;| &minus; &alpha;, 0) / z<sub>j</sub>', '&rho; is how much feature j explains the remaining error. If |&rho;| &le; &alpha; the weight becomes 0.', key=True)}
{note('In the program the true model uses 3 of 10 features. At &alpha; = 0.5, lasso keeps exactly those 3 and sets the other 7 to 0. Ridge with &alpha; = 10 keeps all 10 with small weights.', 'exam')}
''', kw=['lasso', 'L1 penalty', 'sparsity', 'feature selection', 'soft thresholding', 'coordinate descent', 'Lasso'])

K.lesson('enet', 'Elastic net: the best of both', f'''
{wwh('<b>Elastic net</b> uses both penalties: &alpha; (r &Sigma;|w| + (1 &minus; r)/2 &Sigma;w<sup>2</sup>), where r is l1_ratio. r = 1 is lasso and r = 0 is ridge.',
     'When several features are strongly correlated, lasso tends to pick one at random and drop the others. Elastic net keeps the group together and still sets truly useless features to 0. It is a safe default when you are not sure which penalty suits the data.',
     'Choose l1_ratio (often 0.1 to 0.9) and &alpha; with cross validation (ElasticNetCV). The L2 part makes the problem behave well with correlated features and the L1 part gives sparsity.')}
{run('elastic_net')}
{note('The three features a, b and c are almost the same. Lasso gives them 0.91, 0.24 and 1.74 (an uneven, arbitrary split), while elastic net gives 0.94, 0.88 and 1.07, closer to an even share of the true weight 3.', 'tip')}
''', kw=['elastic net', 'ElasticNet', 'l1_ratio', 'correlated features', 'grouping effect'])

K.lesson('cv', 'Choosing alpha with cross validation', f'''
{wwh('&alpha; is a <b>hyperparameter</b>: you choose it, the training does not learn it. <b>RidgeCV</b>, <b>LassoCV</b> and <b>ElasticNetCV</b> try many values and keep the one with the best cross validated score.',
     'Too small an &alpha; leaves the overfitting in place. Too large an &alpha; shrinks the real signal away (underfitting). The right value depends on the data, so it must be measured, not guessed.',
     'Give a list of &alpha; values (usually spaced by factors of 10). For each one, cross validation trains on part of the training data and scores on the rest. The best &alpha; is then used to fit on all the training data. The test set is touched only once at the end.')}
{run('choose_alpha')}
{note('With 65 polynomial features on 309 training rows, plain least squares overfits (test R&sup2; 0.225). Ridge and lasso both lift it to about 0.37, and lasso does it with only 14 of the 65 features.', 'tip')}
{steps('Recipe for a regularised linear model', [
    'Put StandardScaler before the model in a Pipeline, so every weight is penalised fairly.',
    'Use RidgeCV for a quick, stable model, LassoCV when you want fewer features, ElasticNetCV for correlated groups.',
    'Search &alpha; on a log scale, for example 0.001, 0.01, ..., 1000.',
    'If the best &alpha; is at the edge of your list, extend the list.',
    'Report the test score of the final model once.'])}
''', kw=['hyperparameter', 'RidgeCV', 'LassoCV', 'ElasticNetCV', 'cross validation', 'alpha search', 'log scale'])

K.lesson('versus', 'Penalties compared', f'''
{versus('Linear models with and without penalties', ['', 'Least squares', 'Ridge (L2)', 'Lasso (L1)', 'Elastic net'], [
    ['Penalty', 'None', '&alpha;&Sigma;w<sup>2</sup>', '&alpha;&Sigma;|w|', 'Both'],
    ['Weights exactly 0', 'No', 'No', 'Yes', 'Yes'],
    ['Correlated features', 'Unstable weights', 'Shares weight evenly', 'Picks one, drops others', 'Keeps the group'],
    ['Closed form', 'Yes', 'Yes', 'No (coordinate descent)', 'No'],
    ['More features than rows', 'Fails (no unique answer)', 'Works', 'Keeps at most n features', 'Works'],
    ['Best for', 'Few, clean features', 'Many useful features', 'Few useful among many', 'Correlated groups, safe default']],
    'start with ridge, use lasso or elastic net when you want a smaller model.')}
{deep('Why L1 makes zeros: the geometry', '<p>Penalised regression is the same as least squares under a budget: minimise the error while &Sigma;w<sup>2</sup> &le; t (ridge) or &Sigma;|w| &le; t (lasso). The ridge budget is a circle (a sphere in more dimensions) and the lasso budget is a diamond with corners on the axes. The error contours are ellipses around the least squares answer, and the best point is where the first ellipse touches the budget. A round ball is usually touched at a point with every weight non zero, while a diamond is usually touched at a corner, where some weights are exactly 0.</p>')}
''', kw=['ridge vs lasso', 'L1 vs L2', 'constraint form', 'geometry of lasso', 'diamond', 'penalty comparison'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Ridge', 'min ||y &minus; Xw||<sup>2</sup> + &alpha;||w||<sub>2</sub><sup>2</sup>, w = (X<sup>T</sup>X + &alpha;I)<sup>&minus;1</sup>X<sup>T</sup>y', 'Always solvable because X<sup>T</sup>X + &alpha;I can be inverted for &alpha; &gt; 0.', key=True),
     fx('Lasso', 'min (1/2n)||y &minus; Xw||<sup>2</sup> + &alpha;||w||<sub>1</sub>', 'This is the exact scaling scikit-learn uses.', key=True),
     fx('Elastic net', 'min (1/2n)||y &minus; Xw||<sup>2</sup> + &alpha;r||w||<sub>1</sub> + (&alpha;(1 &minus; r)/2)||w||<sub>2</sub><sup>2</sup>', 'r is l1_ratio.', key=True),
     fx('Ridge on one scaled feature', 'w<sub>ridge</sub> = w<sub>ols</sub> &times; s / (s + &alpha;)', 's = &Sigma;x<sup>2</sup>. Shrinks by a factor, never to 0.'),
     fx('Lasso on one scaled feature', 'w<sub>lasso</sub> = sign(w<sub>ols</sub>) max(|w<sub>ols</sub>| &minus; &alpha;&prime;, 0)', 'Moves by a fixed amount and stops at 0.'))}
{steps('Worked example: ridge on one feature by hand', [
    'Data x = 1, 2, 3 and y = 2, 4, 6 (no intercept). &Sigma;xy = 2 + 8 + 18 = 28, &Sigma;x<sup>2</sup> = 14.',
    'Least squares: w = 28 / 14 = 2.',
    'Ridge with &alpha; = 7: w = &Sigma;xy / (&Sigma;x<sup>2</sup> + &alpha;) = 28 / 21.',
    eq('w = 1.333'),
    'The penalty pulled the weight from 2 down to 1.333. With &alpha; = 0 we get 2 back.'])}
{deep('Regularisation as a prior, and the bias variance view', '<p>Ridge is the MAP estimate under a normal prior w ~ N(0, (&sigma;<sup>2</sup>/&alpha;)I), and lasso under a Laplace prior (Foundations 2.3). Ridge adds bias (the weights are pulled towards 0) but cuts variance by a larger amount when features are correlated or n is small, so the expected test error drops. In terms of the singular values d<sub>j</sub> of X, ridge multiplies each component of the least squares fit by d<sub>j</sub><sup>2</sup>/(d<sub>j</sub><sup>2</sup> + &alpha;), shrinking most the directions the data supports least. The effective degrees of freedom are &Sigma; d<sub>j</sub><sup>2</sup>/(d<sub>j</sub><sup>2</sup> + &alpha;).</p>')}
''', kw=['ridge formula', 'lasso objective', 'elastic net objective', 'MAP', 'Laplace prior', 'effective degrees of freedom', 'SVD shrinkage'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A model that is too simple misses the pattern, and one that is too flexible memorises noise. A penalty on big weights keeps a flexible model calm.</p>',
    '<p>Fit polynomial features, spot overfitting from train and test errors, use Ridge, Lasso and ElasticNet after scaling, and pick &alpha; with RidgeCV or LassoCV.</p>',
    '<p>Explain why L1 gives zeros (diamond geometry, soft thresholding), why ridge handles multicollinearity, the ridge closed form, and when elastic net beats lasso.</p>',
    '<p>Study regularisation paths (LARS), the lasso’s selection consistency conditions (irrepresentable condition), effective degrees of freedom, the group lasso, and how weight decay in neural networks is ridge in disguise.</p>')}
{grow('Recognise underfitting and overfitting from two numbers.',
      'Build a scaled, regularised pipeline and tune &alpha; with cross validation.',
      'Reason about penalties through geometry, priors and the bias variance trade off.')}
''', kw=['beginner', 'expert', 'LARS', 'regularisation path', 'group lasso', 'weight decay'])

lc(2333, 'Minimum Sum of Squared Difference', 'minimum-sum-of-squared-difference', 'm', 'Shrink the largest values first (like an L2 penalty)', 'Only the gaps |a &minus; b| matter, and you have k1 + k2 unit decreases. A squared sum falls fastest when you cut the biggest gaps, so bring every gap above some level down to that level (binary search the level), then spend what is left one by one.', r'''
def min_sum_square_diff(nums1, nums2, k1, k2):
    diffs = [abs(a - b) for a, b in zip(nums1, nums2)]
    k = k1 + k2
    if sum(diffs) <= k:
        return 0
    low = 0
    high = max(diffs)
    while low < high:
        mid = (low + high) // 2
        need = sum(d - mid for d in diffs if d > mid)
        if need <= k:
            high = mid
        else:
            low = mid + 1
    level = low
    left = k - sum(d - level for d in diffs if d > level)
    total = 0
    for d in diffs:
        v = min(d, level)
        if v == level and left > 0 and level > 0:
            v = v - 1
            left = left - 1
        total = total + v * v
    return total
''', [('min_sum_square_diff([1, 2, 3, 4], [2, 10, 20, 19], 0, 0)', 579), ('min_sum_square_diff([1, 4, 10, 12], [5, 8, 6, 9], 1, 1)', 43)])
lc(1685, 'Sum of Absolute Differences in a Sorted Array', 'sum-of-absolute-differences-in-a-sorted-array', 'm', 'L1 distances with prefix sums', 'For position i, numbers on the left are smaller and numbers on the right are larger. With prefix sums, the left part is i &times; x minus their sum and the right part is their sum minus count &times; x.', r'''
def get_sum_absolute_differences(nums):
    n = len(nums)
    total = sum(nums)
    left_sum = 0
    result = []
    for i in range(n):
        x = nums[i]
        right_sum = total - left_sum - x
        result.append(i * x - left_sum + right_sum - (n - 1 - i) * x)
        left_sum = left_sum + x
    return result
''', [('get_sum_absolute_differences([2, 3, 5])', [4, 3, 5]), ('get_sum_absolute_differences([1, 4, 6, 8, 10])', [24, 15, 13, 15, 21])])
lc(2602, 'Minimum Operations to Make All Array Elements Equal', 'minimum-operations-to-make-all-array-elements-equal', 'm', 'L1 cost per query with prefix sums and binary search', 'Sort once and build prefix sums. For a query q, binary search how many numbers are below q. The cost is (count below &times; q &minus; their sum) plus (sum above &minus; count above &times; q).', r'''
from bisect import bisect_left


def min_operations(nums, queries):
    s = sorted(nums)
    prefix = [0]
    for x in s:
        prefix.append(prefix[-1] + x)
    n = len(s)
    answer = []
    for q in queries:
        i = bisect_left(s, q)
        below = q * i - prefix[i]
        above = (prefix[n] - prefix[i]) - q * (n - i)
        answer.append(below + above)
    return answer
''', [('min_operations([3, 1, 6, 8], [1, 5])', [14, 10]), ('min_operations([2, 9, 6, 3], [10])', [20])])
lc(1838, 'Frequency of the Most Frequent Element', 'frequency-of-the-most-frequent-element', 'm', 'A budget constraint with a sliding window', 'Sort. For a window ending at nums[r], raising every number to nums[r] costs nums[r] &times; size &minus; window sum. Shrink the window from the left while the cost is over the budget k. Like a penalty budget, k limits how far the values may move.', r'''
def max_frequency(nums, k):
    s = sorted(nums)
    left = 0
    window = 0
    best = 0
    for right in range(len(s)):
        window = window + s[right]
        while s[right] * (right - left + 1) - window > k:
            window = window - s[left]
            left = left + 1
        best = max(best, right - left + 1)
    return best
''', [('max_frequency([1, 2, 4], 5)', 3), ('max_frequency([1, 4, 8, 13], 5)', 2), ('max_frequency([3, 9, 6], 2)', 1)])
lc(1802, 'Maximum Value at a Given Index in a Bounded Array', 'maximum-value-at-a-given-index-in-a-bounded-array', 'm', 'Binary search under a sum budget', 'The cheapest array with value v at index falls by 1 per step on both sides and never goes below 1. Its sum grows with v, so binary search the largest v whose minimum sum fits in maxSum.', r'''
def side_sum(peak, length):
    # sum of peak - 1, peak - 2, ... over length cells, never below 1
    if peak - 1 >= length:
        top = peak - 1
        bottom = peak - length
        return (top + bottom) * length // 2
    ones = length - (peak - 1)
    return (peak - 1) * peak // 2 + ones


def max_value(n, index, max_sum):
    low = 1
    high = max_sum
    while low < high:
        mid = (low + high + 1) // 2
        total = mid + side_sum(mid, index) + side_sum(mid, n - index - 1)
        if total <= max_sum:
            low = mid
        else:
            high = mid - 1
    return low
''', [('max_value(4, 2, 6)', 2), ('max_value(6, 1, 10)', 3)])
lc(1049, 'Last Stone Weight II', 'last-stone-weight-ii', 'm', 'Pick signs to make a sum as close to 0 as possible', 'Smashing stones is the same as giving each stone a + or &minus; sign. Split them into two groups with sums as equal as possible: find all reachable subset sums up to half the total.', r'''
def last_stone_weight_ii(stones):
    total = sum(stones)
    reachable = {0}
    for s in stones:
        reachable = reachable | {r + s for r in reachable if r + s <= total // 2}
    return total - 2 * max(reachable)
''', [('last_stone_weight_ii([2, 7, 4, 1, 8, 1])', 1), ('last_stone_weight_ii([31, 26, 33, 21, 40])', 5)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Regularisation is about keeping values small under a budget and about the difference between squared (L2) and absolute (L1) costs. These problems practise exactly that: shrink the biggest gaps first to lower a squared sum, compute L1 distances fast with prefix sums, and find the best answer that fits inside a budget. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'squared difference', 'absolute difference', 'prefix sum', 'budget', 'binary search', 'subset sum'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Polynomial features</b> let a linear model fit curves. Too low a degree underfits, too high overfits.',
    '<b>Underfitting</b>: both errors high (high bias). <b>Overfitting</b>: training error low, test error high (high variance).',
    '<b>Ridge</b> adds &alpha;&Sigma;w<sup>2</sup>: shrinks all weights, never to 0, shares weight among correlated features. Closed form (X<sup>T</sup>X + &alpha;I)<sup>&minus;1</sup>X<sup>T</sup>y.',
    '<b>Lasso</b> adds &alpha;&Sigma;|w|: sets weak weights to exactly 0, so it selects features.',
    '<b>Elastic net</b> mixes both and keeps correlated groups together.',
    'Always scale features before a penalty. Pick &alpha; with RidgeCV, LassoCV or ElasticNetCV on a log scale.',
    'L1 makes zeros because its budget is a diamond with corners on the axes.'],
    'Supervised 2.1 moves from numbers to categories with logistic regression, the classification cousin of linear regression.')}
{files('Three tasks: polynomial features of a list, ridge for one feature, and the lasso soft threshold.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Training error is very low and test error is high. The model is', ['Underfitting', 'Overfitting', 'Perfect', 'Not trained'], 1, 'It memorised.', 'A big gap between training and test error means overfitting.')
K.quiz('e', 'Ridge regression adds a penalty on', ['The number of rows', 'The sum of squared weights', 'The intercept only', 'The test error'], 1, 'L2.', '&alpha;&Sigma;w<sup>2</sup>.')
K.quiz('e', 'Which penalty can set weights to exactly zero?', ['Ridge', 'Lasso', 'Neither', 'Only plain least squares'], 1, 'L1.', 'Lasso’s absolute value penalty creates zeros.')
K.quiz('e', 'Increasing &alpha; in ridge makes the weights', ['Larger', 'Smaller', 'Exactly zero', 'Random'], 1, 'Stronger penalty.', 'More shrinkage towards 0.')
K.quiz('m', 'Why scale features before ridge or lasso?', ['To make training slower', 'The penalty treats all weights the same, so units must be comparable', 'Scaling removes outliers', 'It is not needed'], 1, 'A weight on km vs metres.', 'Without scaling, features in small units get unfairly large weights and penalties.')
K.quiz('m', 'Two features are almost identical. Ridge will usually', ['Drop both', 'Give them similar weights', 'Give one a huge positive and one a huge negative weight', 'Fail'], 1, 'Sharing.', 'Ridge spreads the weight between correlated features.')
K.quiz('m', 'A degree 1 model on wave shaped data has high training and test error. Fix by', ['Adding a stronger penalty', 'Using a more flexible model (higher degree)', 'Using less data', 'Removing features'], 1, 'Underfitting.', 'Increase flexibility.')
K.quiz('m', 'elastic net with l1_ratio = 1 is the same as', ['Ridge', 'Lasso', 'Least squares', 'Logistic regression'], 1, 'All L1.', 'r = 1 keeps only the L1 penalty.')
K.quiz('m', 'You have 500 features and 100 rows. Plain least squares', ['Works best', 'Has no unique solution, so use a penalty', 'Selects 100 features', 'Is the same as lasso'], 1, 'More unknowns than equations.', 'X<sup>T</sup>X cannot be inverted. Ridge or lasso fixes it.')
K.quiz('h', 'Why does the lasso give exact zeros while ridge does not?', ['Lasso uses more data', 'The L1 penalty has a corner at 0, so small weights are pulled all the way', 'Ridge has no penalty', 'Lasso uses gradient descent'], 1, 'Soft threshold.', 'The diamond shaped budget is touched at its corners.')
K.quiz('h', 'LassoCV picks the largest &alpha; in your list. You should', ['Accept it', 'Extend the list to larger values and search again', 'Switch to plain least squares', 'Use the smallest &alpha;'], 1, 'The best may be beyond the edge.', 'An edge value means the search range was too narrow.')
K.quiz('h', 'Ridge adds bias. Why can it still lower test error?', ['Bias is always good', 'It cuts variance by more than the bias it adds', 'It removes noise from y', 'It increases training error to 0'], 1, 'Bias variance trade off.', 'Expected error = bias<sup>2</sup> + variance + noise.')
K.quiz('x', 'In the style of a Stanford CS229 exam: ridge regression is the MAP estimate when the prior on w is', ['Laplace', 'Normal with mean 0', 'Uniform', 'Bernoulli'], 1, 'log of a Gaussian gives a square.', 'A zero mean Gaussian prior gives the L2 penalty.')
K.quiz('x', 'In the style of a Berkeley CS189 exam: for ridge with singular values d<sub>j</sub> of X, the component along direction j is multiplied by', ['d<sub>j</sub>/(d<sub>j</sub> + &alpha;)', 'd<sub>j</sub><sup>2</sup>/(d<sub>j</sub><sup>2</sup> + &alpha;)', '1/(1 + &alpha;)', '&alpha;/d<sub>j</sub>'], 1, 'Shrinkage factor from the SVD.', 'Directions with small singular values are shrunk the most.')

K.calc('e', 'Weights 3 and &minus;4. L2 penalty &Sigma;w<sup>2</sup>?', '25', 'Square and add.', ['3<sup>2</sup> = 9.', '(&minus;4)<sup>2</sup> = 16.', eq('9 + 16 = 25')], check=25)
K.calc('e', 'Weights 3 and &minus;4. L1 penalty &Sigma;|w|?', '7', 'Absolute values.', ['|3| = 3.', '|&minus;4| = 4.', eq('3 + 4 = 7')], check=7)
K.calc('e', 'Training MSE 0.01, test MSE 0.40. Gap?', '0.39', 'Test minus train.', ['A big gap points to overfitting.', 'Subtract.', eq('0.40 &minus; 0.01 = 0.39')], check=0.39)
K.calc('m', 'Ridge loss: SSE 12, weights 1 and 2, &alpha; = 0.5. Total?', '14.5', 'SSE + &alpha;&Sigma;w<sup>2</sup>.', ['&Sigma;w<sup>2</sup> = 1 + 4 = 5.', '&alpha; &times; 5 = 2.5.', eq('12 + 2.5 = 14.5')], check=14.5)
K.calc('m', 'One feature, no intercept: &Sigma;xy = 28, &Sigma;x<sup>2</sup> = 14, &alpha; = 7. Ridge weight, 3 decimals?', '1.333', '&Sigma;xy / (&Sigma;x<sup>2</sup> + &alpha;).', ['Denominator 14 + 7 = 21.', '28 / 21.', eq('1.333')], check=round(28 / 21, 3))
K.calc('m', 'Soft threshold: &rho; = 0.8, &alpha; = 0.3, z = 1. Lasso weight?', '0.5', 'sign(&rho;) max(|&rho;| &minus; &alpha;, 0) / z.', ['|&rho;| &minus; &alpha; = 0.5.', 'Positive, divide by 1.', eq('0.5')], check=0.5)
K.calc('m', 'Soft threshold: &rho; = &minus;0.2, &alpha; = 0.3. Lasso weight?', '0', '|&rho;| &le; &alpha;.', ['|&minus;0.2| = 0.2.', '0.2 is below 0.3.', eq('weight = 0')], check=0)
K.calc('h', 'Elastic net penalty with &alpha; = 1, l1_ratio 0.5, weights 2 and &minus;2. Use &alpha;(r&Sigma;|w| + (1 &minus; r)/2 &Sigma;w<sup>2</sup>).', '4', 'Both parts.', ['&Sigma;|w| = 4, times 0.5 = 2.', '&Sigma;w<sup>2</sup> = 8, times 0.25 = 2.', eq('2 + 2 = 4')], check=4)
K.calc('h', 'Polynomial features of degree 3 from 1 feature, with the constant column. How many columns?', '4', '1, x, x<sup>2</sup>, x<sup>3</sup>.', ['Constant: 1.', 'Powers 1 to 3: 3.', eq('4')], check=4)
K.calc('x', 'In the style of an MIT 6.867 problem: singular value d = 2, &alpha; = 4. Ridge shrinkage factor d<sup>2</sup>/(d<sup>2</sup> + &alpha;)?', '0.5', 'Plug in.', ['d<sup>2</sup> = 4.', '4 / (4 + 4).', eq('0.5')], check=0.5)

K.assign('polyfeat', 'e', 'Polynomial features of a list',
         '<p>Write <code>poly_features(xs, degree)</code> that returns, for every x, the row [x, x<sup>2</sup>, ..., x<sup>degree</sup>] (no constant column).</p>',
         '''
def poly_features(xs, degree):
    # your code here
    pass
''', [('poly_features([2, 3], 3)', [[2, 4, 8], [3, 9, 27]]), ('poly_features([1, -1], 2)', [[1, 1], [-1, 1]])],
         '''
def poly_features(xs, degree):
    rows = []
    for x in xs:
        row = []
        for p in range(1, degree + 1):
            row.append(x ** p)
        rows.append(row)
    return rows
''', 'Loop over the values, and inside, over the powers 1 to degree.', '<p>PolynomialFeatures(degree, include_bias=False) makes the same columns, plus all products when there are several features.</p>')
K.assign('ridge1', 'e', 'Ridge for one feature',
         '<p>Write <code>ridge_one(xs, ys, alpha)</code> for a model ŷ = w x with no intercept. Return w = &Sigma;xy / (&Sigma;x<sup>2</sup> + alpha), rounded to 3 decimals.</p>',
         '''
def ridge_one(xs, ys, alpha):
    # your code here
    pass
''', [('ridge_one([1, 2, 3], [2, 4, 6], 0)', 2.0), ('ridge_one([1, 2, 3], [2, 4, 6], 7)', 1.333), ('ridge_one([1, 1], [5, 5], 2)', 2.5)],
         '''
def ridge_one(xs, ys, alpha):
    top = 0
    bottom = 0
    for x, y in zip(xs, ys):
        top = top + x * y
        bottom = bottom + x * x
    return round(top / (bottom + alpha), 3)
''', 'Add up x times y and x squared, then divide with alpha added below.', '<p>This is the one dimensional version of (X<sup>T</sup>X + &alpha;I)<sup>&minus;1</sup>X<sup>T</sup>y.</p>')
K.assign('softth', 'm', 'The lasso soft threshold',
         '<p>Write <code>soft_threshold(rho, alpha)</code>: return rho &minus; alpha if rho &gt; alpha, rho + alpha if rho &lt; &minus;alpha, and 0 otherwise, rounded to 3 decimals. Then write <code>lasso_weights(rhos, alpha)</code> that applies it to a list.</p>',
         '''
def soft_threshold(rho, alpha):
    # your code here
    pass


def lasso_weights(rhos, alpha):
    # your code here
    pass
''', [('soft_threshold(0.8, 0.3)', 0.5), ('soft_threshold(-0.2, 0.3)', 0), ('lasso_weights([2.0, -1.0, 0.1, -0.05], 0.5)', [1.5, -0.5, 0, 0])],
         '''
def soft_threshold(rho, alpha):
    if rho > alpha:
        return round(rho - alpha, 3)
    if rho < -alpha:
        return round(rho + alpha, 3)
    return 0


def lasso_weights(rhos, alpha):
    result = []
    for r in rhos:
        result.append(soft_threshold(r, alpha))
    return result
''', 'Three cases: above alpha, below minus alpha, and in between (which gives 0).', '<p>For scaled, uncorrelated features the lasso solution is exactly this soft threshold of the least squares weights. That is why weak features become 0.</p>')

K.must('Fit diagnosis', 'Underfit: both errors high (bias). Overfit: train low, test high (variance). Choose complexity on validation data.')
K.must('Ridge', 'Penalty &alpha;&Sigma;w<sup>2</sup>. w = (X<sup>T</sup>X + &alpha;I)<sup>&minus;1</sup>X<sup>T</sup>y. Shrinks, never zeros. Fixes multicollinearity.')
K.must('Lasso', 'Penalty &alpha;&Sigma;|w|. Soft threshold sets weak weights to 0, so it selects features. Coordinate descent.')
K.must('Elastic net', 'Mix with l1_ratio. Keeps correlated groups together. Safe default.')
K.must('Practice', 'Scale first (Pipeline). Tune &alpha; with RidgeCV, LassoCV, ElasticNetCV on a log grid. Extend the grid if the best is at the edge.')
K.must('Theory', 'L1 diamond vs L2 ball. Ridge = Gaussian prior, lasso = Laplace prior. Ridge shrinks along SVD directions by d<sup>2</sup>/(d<sup>2</sup> + &alpha;).')

T = K.topic(
    slug='ml-regularization', topic='ml-regularization', step=(1, 'Regression', 'ml-s1', 'Predict numbers: straight lines, curves, and how to stop a model from memorising the training data.', 'Beginner'),
    title='Polynomial regression and regularisation: ridge, lasso, elastic net', short='Regularisation', badge='1.2', minutes=60,
    lead='Learn to bend a line into a curve with polynomial features, recognise underfitting and overfitting, and control flexibility with ridge (L2), lasso (L1) and elastic net, choosing the penalty with cross validation.',
    desc='polynomial regression, underfitting, overfitting, bias and variance, ridge regression, L2 penalty, closed form, multicollinearity, lasso, L1 penalty, sparsity, soft thresholding, coordinate descent, elastic net, l1_ratio, RidgeCV, LassoCV, ElasticNetCV, hyperparameters, constraint geometry, priors, SVD shrinkage.',
    summary='polynomial features, underfitting and overfitting, ridge, lasso, elastic net, and choosing alpha with cross validation.',
    keywords=['polynomial regression', 'overfitting', 'underfitting', 'ridge', 'lasso', 'elastic net', 'regularisation', 'L1', 'L2', 'RidgeCV'],
    recap='<p>Give a model enough flexibility to learn the pattern, then a penalty so it cannot learn the noise.</p>',
    added='2026-11-13', leet=leet_items())
