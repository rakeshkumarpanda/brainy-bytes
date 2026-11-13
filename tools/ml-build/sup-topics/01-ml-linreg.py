# Supervised 1.1: linear regression. Checked against James, Witten, Hastie and Tibshirani, An Introduction to
# Statistical Learning (2nd edition) chapter 3, Hastie, Tibshirani and Friedman, The Elements of Statistical Learning
# (2nd edition) chapter 3.2, the Stanford CS229 notes on linear regression and the normal equation, the scikit-learn
# 1.8 user guide section 1.1 (ordinary least squares, SGD and Huber), and the statsmodels 0.14 OLS reference.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-linreg')
K = Kit()

K.code('line_by_hand', r'''
hours = [1, 2, 3, 4, 5, 6]
score = [52, 55, 61, 64, 70, 72]

n = len(hours)
mean_x = sum(hours) / n
mean_y = sum(score) / n

top = 0
bottom = 0
for x, y in zip(hours, score):
    top = top + (x - mean_x) * (y - mean_y)
    bottom = bottom + (x - mean_x) ** 2
slope = top / bottom
intercept = mean_y - slope * mean_x
print("slope:", round(slope, 3), " intercept:", round(intercept, 3))
print("predicted score after 7 hours:", round(intercept + slope * 7, 2))

sse = 0
for x, y in zip(hours, score):
    error = y - (intercept + slope * x)
    sse = sse + error ** 2
print("sum of squared errors:", round(sse, 3))
''')

K.code('normal_equation', r'''
import numpy as np
from sklearn.linear_model import LinearRegression

# size_m2, rooms, age_years  ->  price (lakh)
X = np.array([[50, 1, 10], [70, 2, 5], [80, 2, 20], [100, 3, 2], [120, 3, 15], [150, 4, 8]])
y = np.array([40, 62, 60, 95, 98, 135])

ones = np.ones((len(X), 1))
Xb = np.hstack([ones, X])                         # add a column of 1s for the intercept
w = np.linalg.solve(Xb.T @ Xb, Xb.T @ y)           # normal equation
print("normal equation weights:", np.round(w, 3).tolist())

model = LinearRegression().fit(X, y)
print("sklearn intercept:", round(model.intercept_, 3), " coefficients:", np.round(model.coef_, 3).tolist())
print("predict a 90 m2, 2 room, 10 year old flat:", round(model.predict([[90, 2, 10]])[0], 2))
''')

K.code('diabetes_regression', r'''
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True, as_frame=True)
print("rows:", X.shape[0], " features:", list(X.columns))
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

model = LinearRegression().fit(X_train, y_train)
pred = model.predict(X_test)
print("test MAE: ", round(mean_absolute_error(y_test, pred), 2))
print("test RMSE:", round(mean_squared_error(y_test, pred) ** 0.5, 2))
print("test R2:  ", round(r2_score(y_test, pred), 3))
top = sorted(zip(model.coef_, X.columns), key=lambda t: -abs(t[0]))[:3]
print("largest weights:", [(name, round(float(c), 1)) for c, name in top])
''')

K.code('regression_metrics', r'''
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

y_true = np.array([3.0, 5.0, 7.0, 9.0])
y_pred = np.array([2.5, 5.5, 6.0, 9.5])

errors = y_true - y_pred
mae = np.mean(np.abs(errors))
mse = np.mean(errors ** 2)
rmse = np.sqrt(mse)
r2 = 1 - np.sum(errors ** 2) / np.sum((y_true - y_true.mean()) ** 2)
print("by hand  MAE", mae, " MSE", mse, " RMSE", round(rmse, 4), " R2", round(r2, 4))
print("sklearn  MAE", mean_absolute_error(y_true, y_pred), " MSE", mean_squared_error(y_true, y_pred),
      " R2", round(r2_score(y_true, y_pred), 4))
print("always predicting the mean gives R2 =", r2_score(y_true, np.full(4, y_true.mean())))
''')

K.code('sgd_vs_exact', r'''
import numpy as np
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(3)
X = rng.uniform(0, 10, size=(200, 2))
y = 4 * X[:, 0] - 2 * X[:, 1] + 7 + rng.normal(0, 1, 200)

Xs = StandardScaler().fit_transform(X)
exact = LinearRegression().fit(Xs, y)
sgd = SGDRegressor(max_iter=1000, tol=1e-6, random_state=0).fit(Xs, y)
print("closed form:", round(exact.intercept_, 3), np.round(exact.coef_, 3).tolist())
print("SGD:        ", round(sgd.intercept_[0], 3), np.round(sgd.coef_, 3).tolist())
print("SGD needed", sgd.n_iter_, "passes over the data")
''')

K.code('residual_check', r'''
import numpy as np
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(1)
x = rng.uniform(1, 10, size=200)
fair = 3 * x + rng.normal(0, 1, 200)                 # same noise everywhere
growing = 3 * x + rng.normal(0, 1, 200) * x          # noise grows with x

for name, y in [("same noise", fair), ("growing noise", growing)]:
    model = LinearRegression().fit(x.reshape(-1, 1), y)
    resid = y - model.predict(x.reshape(-1, 1))
    small = resid[x < 4].std()
    big = resid[x > 7].std()
    print(name.ljust(14), "mean residual", round(resid.mean(), 3), " spread for small x", round(small, 2), " for big x", round(big, 2))
''')

K.code('outlier_huber', r'''
import numpy as np
from sklearn.linear_model import HuberRegressor, LinearRegression

x = np.arange(1, 11).reshape(-1, 1).astype(float)
y = 2 * x.ravel() + 1
y[9] = 60                                            # one bad value (should be 21)

ols = LinearRegression().fit(x, y)
huber = HuberRegressor().fit(x, y)
print("true line:   slope 2, intercept 1")
print("least squares slope", round(ols.coef_[0], 2), " intercept", round(ols.intercept_, 2))
print("Huber        slope", round(huber.coef_[0], 2), " intercept", round(huber.intercept_, 2))
''')

K.code('statsmodels_ols', r'''
import numpy as np
import statsmodels.api as sm

rng = np.random.default_rng(7)
n = 100
ads = rng.uniform(0, 10, n)
noise_feature = rng.uniform(0, 10, n)              # has nothing to do with sales
sales = 5 + 2.5 * ads + rng.normal(0, 3, n)

X = sm.add_constant(np.column_stack([ads, noise_feature]))
result = sm.OLS(sales, X).fit()
print("weights:      ", np.round(result.params, 3).tolist())
print("p values:     ", np.round(result.pvalues, 4).tolist())
low, high = result.conf_int()[1]
print("95% interval for the ads weight:", round(low, 3), "to", round(high, 3))
print("R2:", round(result.rsquared, 3), " adjusted R2:", round(result.rsquared_adj, 3))
''')

K.lesson('idea', 'Linear regression: predict a number with a straight line', f'''
{src('James, Witten, Hastie and Tibshirani, An Introduction to Statistical Learning chapter 3, Hastie, Tibshirani and Friedman, The Elements of Statistical Learning chapter 3.2, the Stanford CS229 notes, and the scikit-learn 1.8 and statsmodels 0.14 references.')}
{viz('mlols')}
{wwh('<b>Linear regression</b> predicts a number (house price, exam score, sales) as a weighted sum of the features plus a constant: ŷ = b<sub>0</sub> + b<sub>1</sub>x<sub>1</sub> + ... + b<sub>d</sub>x<sub>d</sub>. With one feature it is a straight line. <b>Least squares</b> chooses the weights that make the sum of squared errors as small as possible.',
     'It is the first model to try for any number prediction. It trains in a blink, it is easy to explain ("each extra square metre adds 0.82 lakh"), and it is the base of logistic regression, neural networks and much of statistics. A fancier model must beat it to be worth the trouble.',
     'For one feature, the best slope is the covariance of x and y divided by the variance of x, and the line passes through the mean point. For many features, the normal equation solves for all weights at once, or gradient descent walks to them step by step. The animation above shows the one feature case, and the program below does it by hand.')}
{run('line_by_hand')}
{fxs(fx('Simple linear regression', 'b<sub>1</sub> = &Sigma;(x<sub>i</sub> &minus; x&#772;)(y<sub>i</sub> &minus; y&#772;) / &Sigma;(x<sub>i</sub> &minus; x&#772;)<sup>2</sup>, b<sub>0</sub> = y&#772; &minus; b<sub>1</sub>x&#772;', 'The slope is cov(x, y) / var(x).', key=True),
     fx('Least squares loss', 'L(b) = &Sigma; (y<sub>i</sub> &minus; ŷ<sub>i</sub>)<sup>2</sup>', 'Squaring makes every error positive and punishes big errors more.', key=True))}
{scene('a taxi fare', '<p>A taxi charges a fixed 50 rupees plus 15 rupees per kilometre. Fare = 50 + 15 &times; km is a linear model: 50 is the intercept and 15 the slope. Linear regression does the reverse. It looks at many past trips and their fares, and works out the 50 and the 15.</p>')}
''', kw=['linear regression', 'least squares', 'slope', 'intercept', 'residual', 'simple linear regression', 'covariance'])

K.lesson('many', 'Many features and the normal equation', f'''
{wwh('With several features, the model is ŷ = Xw, where X has one row per example (plus a column of 1s for the intercept) and w holds the weights. The <b>normal equation</b> w = (X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>y gives the exact least squares weights in one step.',
     'Real targets depend on many things at once. Each weight then says how much ŷ changes when that one feature goes up by 1 while the others stay fixed, which is very useful for explaining a model.',
     'Set the gradient of the squared error to zero: X<sup>T</sup>(Xw &minus; y) = 0. Rearranging gives the normal equation. In code, solve the linear system with np.linalg.solve (or lstsq) instead of computing the inverse, which is slower and less accurate. scikit-learn’s LinearRegression does this for you.')}
{run('normal_equation')}
{fx('Normal equation', 'w = (X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>y', 'Exact answer. Costs about O(nd<sup>2</sup> + d<sup>3</sup>), so fine up to a few thousand features.', key=True)}
{note('Read a weight as "holding the other features fixed". Above, the rooms weight is 3.7 lakh per extra room for a flat of the same size and age. If two features are strongly correlated (size and rooms), their separate weights become unstable and hard to read. This is called multicollinearity, and ridge regression (next chapter) fixes it.', 'tip')}
''', kw=['multiple linear regression', 'normal equation', 'design matrix', 'np.linalg.solve', 'LinearRegression', 'coefficients', 'multicollinearity'])

K.lesson('fit', 'Fit, predict and measure on real data', f'''
{wwh('The scikit-learn workflow is always the same: split the data, <b>fit</b> on the training part, <b>predict</b> on the test part, and measure the error with <b>MAE</b>, <b>RMSE</b> and <b>R&sup2;</b>.',
     'The training error always looks better than reality, because the model has seen those rows. Only the test error tells you how the model will do on new data.',
     'MAE is the average size of the errors, in the same unit as y. RMSE squares the errors before averaging, so big misses count more. R&sup2; says what share of the variation in y the model explains: 1 is perfect, 0 is no better than always predicting the mean, and it can even be negative on test data.')}
{run('diabetes_regression')}
{run('regression_metrics')}
{table(['Metric', 'Formula', 'Unit', 'Notes'], [
    ['MAE', '(1/n) &Sigma; |y &minus; ŷ|', 'Same as y', 'Easy to explain. Treats all errors the same'],
    ['MSE', '(1/n) &Sigma; (y &minus; ŷ)<sup>2</sup>', 'y squared', 'The training loss. Hard to read'],
    ['RMSE', '&radic;MSE', 'Same as y', 'Punishes big errors more than MAE'],
    ['R&sup2;', '1 &minus; SSE / SST', 'No unit', 'Share of variation explained. Compare models on the same data'],
    ['MAPE', '(1/n) &Sigma; |y &minus; ŷ| / |y|', 'Percent', 'Breaks when y is near 0']])}
{note('An R&sup2; of 0.36 on the diabetes data sounds low, but medical data is noisy. Judge a score against a simple baseline (always the mean, R&sup2; = 0) and against what is possible in that field, not against 1.', 'tip')}
''', kw=['fit', 'predict', 'MAE', 'MSE', 'RMSE', 'R2', 'MAPE', 'train test split', 'load_diabetes'])

K.lesson('gd', 'Gradient descent for linear regression', f'''
{viz('mlgdline')}
{wwh('Instead of the normal equation, you can find the weights with <b>gradient descent</b>: start somewhere, compute the slope of the mean squared error for each weight, and step downhill. <b>SGDRegressor</b> does this with mini-batches of one row.',
     'The normal equation becomes slow with very many features (it needs a d &times; d system) and needs all the data in memory. Gradient descent works on huge or streaming data, and it is exactly how neural networks are trained, so it is worth seeing on the simplest model first.',
     'For the MSE loss the gradients are &part;L/&part;w = (2/n) &Sigma;(ŷ &minus; y)x and &part;L/&part;b = (2/n) &Sigma;(ŷ &minus; y). Scale the features first so one learning rate suits every weight. The MSE of a linear model is a convex bowl, so gradient descent reaches the same answer as the normal equation.')}
{run('sgd_vs_exact')}
{versus('Two ways to fit linear regression', ['', 'Normal equation (LinearRegression)', 'Gradient descent (SGDRegressor)'], [
    ['Answer', 'Exact, in one step', 'Close, after many steps'],
    ['Needs scaling', 'No', 'Yes'],
    ['Learning rate to choose', 'No', 'Yes'],
    ['Many features (100,000+)', 'Slow: d<sup>3</sup> work', 'Fine'],
    ['Data larger than memory', 'No', 'Yes, with partial_fit'],
    ['Use when', 'Most tabular problems', 'Huge or streaming data']],
    'use LinearRegression unless the data is too big for it.')}
''', kw=['gradient descent', 'SGDRegressor', 'MSE gradient', 'convex', 'normal equation vs gradient descent', 'partial_fit'])

K.lesson('assume', 'Assumptions and residual checks', f'''
{wwh('Linear regression assumes: the relation is roughly a straight line (<b>linearity</b>), the errors are independent, the spread of the errors is the same everywhere (<b>homoscedasticity</b>), and, for p values and intervals, the errors are roughly normal.',
     'If the assumptions break, predictions can still be fine, but the weights, p values and confidence intervals can mislead you. Residuals (y &minus; ŷ) show which assumption is broken.',
     'After fitting, look at the residuals. Their mean should be 0. Their spread should not grow with x or with ŷ. A curve in the residuals means the relation is not linear, so add polynomial terms or a log. Growing spread (heteroscedasticity) suggests a log of y or robust standard errors.')}
{run('residual_check')}
{table(['What you see in the residuals', 'Meaning', 'Fix'], [
    ['A curve (U shape)', 'The relation is not linear', 'Add x<sup>2</sup>, a log, or use a tree model'],
    ['A funnel (spread grows)', 'Heteroscedasticity', 'Log transform y, weighted least squares, robust errors'],
    ['A pattern over time', 'Errors are not independent', 'Time series models (MLOps 2.1)'],
    ['A few huge residuals', 'Outliers or data errors', 'Check the rows, use Huber regression']])}
''', kw=['assumptions', 'linearity', 'homoscedasticity', 'heteroscedasticity', 'residual analysis', 'independence', 'normal errors'])

K.lesson('robust', 'Outliers and robust regression', f'''
{wwh('Because errors are squared, one far point can pull the least squares line badly. <b>Huber regression</b> uses squared error for small errors and absolute error for big ones, so outliers count much less.',
     'Real data has typing mistakes and rare events. A model fitted mostly to one bad row predicts badly for everyone else.',
     'Huber loss is (1/2)e<sup>2</sup> when |e| &le; &delta; and &delta;(|e| &minus; &delta;/2) when |e| &gt; &delta;. Small errors behave like least squares, big ones grow only linearly. In the program one wrong value moves the least squares slope from 2 to 4.13, while Huber stays at 2.')}
{run('outlier_huber')}
{fxs(fx('Huber loss', 'L<sub>&delta;</sub>(e) = e<sup>2</sup>/2 if |e| &le; &delta;, otherwise &delta;|e| &minus; &delta;<sup>2</sup>/2', 'Quadratic near 0, linear far away.', key=True),
     fx('Absolute error loss', 'L(e) = |e|', 'The best constant under it is the median, not the mean.'))}
''', kw=['outliers', 'robust regression', 'Huber loss', 'HuberRegressor', 'absolute error', 'median'])

K.lesson('stats', 'Reading weights like a statistician', f'''
{wwh('statsmodels fits the same least squares line but also reports, for each weight, a <b>standard error</b>, a <b>p value</b> and a <b>confidence interval</b>, plus <b>adjusted R&sup2;</b>.',
     'In science, business and medicine you often need to know whether a feature really matters, not just a prediction. A p value tests "is this weight really zero?", and the interval gives the range of believable values.',
     'Fit sm.OLS on X with a constant column. A small p value (below 0.05) means the weight is unlikely to be zero. In the program the ads weight is clearly real (interval 2.36 to 2.79, true value 2.5), while the random feature has p = 0.09, so we cannot say it matters.')}
{run('statsmodels_ols')}
{fx('Adjusted R&sup2;', 'R&sup2;<sub>adj</sub> = 1 &minus; (1 &minus; R&sup2;)(n &minus; 1)/(n &minus; d &minus; 1)', 'Plain R&sup2; never falls when you add a feature. The adjusted version does if the feature does not help enough.', key=True)}
{note('A feature can be statistically significant and still useless for prediction, or very useful for prediction while its p value is unclear because it is correlated with another feature. Prediction (machine learning) and inference (statistics) answer different questions.', 'exam')}
''', kw=['statsmodels', 'p value', 'standard error', 'confidence interval', 'adjusted R2', 'inference vs prediction'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Model', 'ŷ = Xw (X has a first column of 1s)', 'A weighted sum of the features.', key=True),
     fx('Loss', 'L(w) = ||y &minus; Xw||<sup>2</sup>', 'Sum of squared errors.', key=True),
     fx('Gradient', '&nabla;L = &minus;2X<sup>T</sup>(y &minus; Xw)', 'Set to 0 for the minimum.', key=True),
     fx('Normal equation', 'w = (X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>y', 'Exact solution when X<sup>T</sup>X can be inverted.', key=True),
     fx('R&sup2;', 'R&sup2; = 1 &minus; SSE/SST, SST = &Sigma;(y &minus; y&#772;)<sup>2</sup>', 'Share of variation explained.', key=True),
     fx('Simple regression slope', 'b<sub>1</sub> = r &times; s<sub>y</sub> / s<sub>x</sub>', 'r is the correlation of x and y.'))}
{steps('Worked example: the line by hand', [
    'x = 1 to 6 (hours), y = 52, 55, 61, 64, 70, 72. x&#772; = 3.5, y&#772; = 62.333.',
    'x &minus; x&#772; = &minus;2.5, &minus;1.5, &minus;0.5, 0.5, 1.5, 2.5. Their squares add to 17.5.',
    '&Sigma;(x &minus; x&#772;)(y &minus; y&#772;) = 74.0. So b<sub>1</sub> = 74.0 / 17.5 = 4.229.',
    eq('b<sub>0</sub> = 62.333 &minus; 4.229 &times; 3.5 = 47.533'),
    'Prediction for 7 hours: 47.533 + 4.229 &times; 7 = 77.13, as the program prints.'])}
{deep('Least squares as a projection, and maximum likelihood', '<p>Xw can only reach the column space of X. Least squares picks the point in that space closest to y, the orthogonal projection ŷ = X(X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>y = Hy, so the residual vector is perpendicular to every column of X (that is the normal equation). If the errors are independent and normal with constant variance, least squares is also the maximum likelihood estimate (Foundations 2.3), and by the Gauss Markov theorem it has the smallest variance among all unbiased linear estimators even without normality.</p>')}
''', kw=['matrix form', 'gradient', 'normal equation derivation', 'projection', 'hat matrix', 'Gauss Markov', 'maximum likelihood'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Linear regression draws the straight line that best fits the points, then uses it to predict new numbers. "Best" means the smallest total of squared errors.</p>',
    '<p>Fit LinearRegression on several features, read the weights, evaluate on a test set with MAE, RMSE and R&sup2;, and know the normal equation and the gradient descent version.</p>',
    '<p>Check assumptions with residuals, handle outliers with Huber, read p values and intervals with statsmodels, use adjusted R&sup2;, and spot multicollinearity.</p>',
    '<p>Understand least squares as a projection with the hat matrix, the Gauss Markov theorem, the bias and variance of the estimator (variance &sigma;<sup>2</sup>(X<sup>T</sup>X)<sup>&minus;1</sup>), leverage and Cook’s distance, and generalised linear models that extend the idea to counts and probabilities.</p>')}
{grow('Fit a line to points and use it to predict.',
      'Train and evaluate a multi feature regression and explain its weights.',
      'Diagnose residuals, choose robust losses, and reason about the estimator with linear algebra.')}
''', kw=['beginner', 'expert', 'hat matrix', 'leverage', 'Cook distance', 'GLM'])

lc(1232, 'Check If It Is a Straight Line', 'check-if-it-is-a-straight-line', 'e', 'Same slope everywhere (cross multiply)', 'Compare the slope from the first point to every other point with the first slope. Cross multiply instead of dividing so a vertical line does not divide by zero.', r'''
def check_straight_line(coordinates):
    x0, y0 = coordinates[0]
    x1, y1 = coordinates[1]
    dx = x1 - x0
    dy = y1 - y0
    for x, y in coordinates[2:]:
        if dy * (x - x0) != dx * (y - y0):
            return False
    return True
''', [('check_straight_line([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]])', True), ('check_straight_line([[1, 1], [2, 2], [3, 4], [4, 5], [5, 6], [7, 7]])', False)])
lc(2280, 'Minimum Lines to Represent a Line Chart', 'minimum-lines-to-represent-a-line-chart', 'm', 'Sort, then count slope changes', 'Sort the points by day. A new line starts whenever the slope between neighbours changes. Compare slopes by cross multiplying to avoid float errors.', r'''
def minimum_lines(stock_prices):
    points = sorted(stock_prices)
    if len(points) < 2:
        return 0
    lines = 1
    for i in range(2, len(points)):
        x0, y0 = points[i - 2]
        x1, y1 = points[i - 1]
        x2, y2 = points[i]
        if (y1 - y0) * (x2 - x1) != (y2 - y1) * (x1 - x0):
            lines = lines + 1
    return lines
''', [('minimum_lines([[1, 7], [2, 6], [3, 5], [4, 4], [5, 4], [6, 3], [7, 2], [8, 1]])', 3), ('minimum_lines([[3, 4], [1, 2], [7, 8], [2, 3]])', 1)])
lc(149, 'Max Points on a Line', 'max-points-on-a-line', 'h', 'Count slopes from each point', 'Fix one point. Every other point gives a slope, stored as a reduced fraction (dy, dx) with gcd so equal slopes match exactly. The most common slope plus the fixed point is a line.', r'''
from math import gcd


def max_points(points):
    best = 1
    for i in range(len(points)):
        counts = {}
        for j in range(i + 1, len(points)):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            g = gcd(dx, dy)
            dx = dx // g
            dy = dy // g
            if dx < 0 or (dx == 0 and dy < 0):
                dx = -dx
                dy = -dy
            counts[(dy, dx)] = counts.get((dy, dx), 0) + 1
            best = max(best, counts[(dy, dx)] + 1)
    return best
''', [('max_points([[1, 1], [2, 2], [3, 3]])', 3), ('max_points([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]])', 4)])
lc(462, 'Minimum Moves to Equal Array Elements II', 'minimum-moves-to-equal-array-elements-ii', 'm', 'The median minimises absolute error', 'Moving every number to one value c costs the sum of |x &minus; c|. That sum is smallest at the median, the same reason MAE is minimised by the median while MSE is minimised by the mean.', r'''
def min_moves2(nums):
    s = sorted(nums)
    median = s[len(s) // 2]
    total = 0
    for x in s:
        total = total + abs(x - median)
    return total
''', [('min_moves2([1, 2, 3])', 2), ('min_moves2([1, 10, 2, 9])', 16)])
lc(2448, 'Minimum Cost to Make Array Equal', 'minimum-cost-to-make-array-equal', 'h', 'Weighted median of a convex cost', 'The total cost is a convex function of the target value. Its minimum is at the weighted median: sort by value and walk until the running cost weight reaches half of the total weight.', r'''
def min_cost(nums, cost):
    pairs = sorted(zip(nums, cost))
    total_weight = sum(cost)
    running = 0
    target = pairs[0][0]
    for value, weight in pairs:
        running = running + weight
        if running * 2 >= total_weight:
            target = value
            break
    answer = 0
    for value, weight in pairs:
        answer = answer + abs(value - target) * weight
    return answer
''', [('min_cost([1, 3, 5, 2], [2, 3, 1, 14])', 8), ('min_cost([2, 2, 2, 2, 2], [4, 2, 8, 1, 3])', 0)])
lc(1515, 'Best Position for a Service Centre', 'best-position-for-a-service-centre', 'h', 'Gradient descent on a convex loss', 'The sum of distances is convex, so gradient descent works. Step against the gradient and halve the step size whenever a step does not help, until the step is tiny. (The Weiszfeld update is a faster version.)', r'''
def total_distance(points, x, y):
    total = 0
    for px, py in points:
        total = total + ((px - x) ** 2 + (py - y) ** 2) ** 0.5
    return total


def get_min_dist_sum(positions):
    x = sum(p[0] for p in positions) / len(positions)
    y = sum(p[1] for p in positions) / len(positions)
    step = 1.0
    best = total_distance(positions, x, y)
    while step > 1e-7:
        gx = 0
        gy = 0
        for px, py in positions:
            d = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
            if d > 1e-12:
                gx = gx + (x - px) / d
                gy = gy + (y - py) / d
        size = (gx * gx + gy * gy) ** 0.5
        if size < 1e-12:
            break
        nx = x - step * gx / size
        ny = y - step * gy / size
        value = total_distance(positions, nx, ny)
        if value < best:
            x, y, best = nx, ny, value
        else:
            step = step / 2
    return round(best, 5)
''', [('get_min_dist_sum([[0, 1], [1, 0], [1, 2], [2, 1]])', 4.0), ('get_min_dist_sum([[1, 1], [3, 3]])', 2.82843)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>These problems use the ideas behind regression: slopes and straight lines (checked exactly with cross multiplication), the fact that the median minimises absolute error while the mean minimises squared error, and gradient descent on a convex loss. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'slope', 'straight line', 'median', 'weighted median', 'gradient descent', 'convex'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Linear regression</b> predicts ŷ = b<sub>0</sub> + b<sub>1</sub>x<sub>1</sub> + ... and picks the weights with the smallest sum of squared errors.',
    'One feature: b<sub>1</sub> = cov(x, y) / var(x), and the line passes through (x&#772;, y&#772;).',
    'Many features: the normal equation w = (X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>y, or gradient descent on scaled features.',
    'Measure on test data: MAE (average miss), RMSE (punishes big misses), R&sup2; = 1 &minus; SSE/SST.',
    'Check residuals for curves (not linear) and funnels (heteroscedasticity).',
    'One outlier can pull the line. Huber regression is robust.',
    'statsmodels gives p values and confidence intervals for each weight. Adjusted R&sup2; punishes useless features.'],
    'Supervised 1.2 bends the line with polynomial features and controls overfitting with ridge, lasso and elastic net.')}
{files('Three tasks: fit a simple regression by hand, compute R&sup2;, and run gradient descent for a line.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Linear regression is used to predict', ['A category', 'A number', 'A cluster', 'A ranking only'], 1, 'Regression.', 'Regression predicts continuous numbers.')
K.quiz('e', 'In ŷ = 50 + 15x, the number 15 is the', ['Intercept', 'Slope', 'Residual', 'R&sup2;'], 1, 'How much ŷ changes per unit of x.', 'The slope multiplies x.')
K.quiz('e', 'A residual is', ['The predicted value', 'Actual minus predicted', 'The slope', 'The mean of y'], 1, 'The leftover.', 'Residual = y &minus; ŷ.')
K.quiz('e', 'R&sup2; = 0 means the model is', ['Perfect', 'No better than always predicting the mean', 'Always wrong by 0', 'Overfitting'], 1, 'Compare with the flat line.', 'SSE equals SST.')
K.quiz('m', 'The least squares line always passes through', ['The origin', 'The point (x&#772;, y&#772;)', 'The first point', 'The largest y'], 1, 'b<sub>0</sub> = y&#772; &minus; b<sub>1</sub>x&#772;.', 'Put x = x&#772; into the line and you get y&#772;.')
K.quiz('m', 'Which metric punishes one huge error the most?', ['MAE', 'RMSE', 'Median absolute error', 'R&sup2; only'], 1, 'Squares grow fast.', 'RMSE squares the errors before averaging.')
K.quiz('m', 'Gradient descent for linear regression needs feature scaling because', ['The loss is not convex', 'One learning rate must suit every weight', 'sklearn requires it', 'It changes the answer'], 1, 'Long narrow valleys.', 'Different scales make the loss bowl stretched.')
K.quiz('m', 'Residual spread grows as x grows. This is', ['Multicollinearity', 'Heteroscedasticity', 'Underfitting', 'Leakage'], 1, 'Unequal spread.', 'Non constant error variance.')
K.quiz('m', 'Adding a useless random feature to a linear regression will make training R&sup2;', ['Go down', 'Stay the same or go up a little', 'Become negative', 'Equal 1'], 1, 'Least squares can always ignore it.', 'Plain R&sup2; never decreases. Adjusted R&sup2; can.')
K.quiz('h', 'Why use np.linalg.solve(X.T @ X, X.T @ y) instead of inv(X.T @ X) @ X.T @ y?', ['It gives a different answer', 'It is faster and numerically more accurate', 'inv does not exist in numpy', 'solve adds regularisation'], 1, 'Avoid explicit inverses.', 'Solving the system is cheaper and more stable.')
K.quiz('h', 'Huber regression is less affected by outliers because its loss', ['Is always 0 for outliers', 'Grows only linearly for large errors', 'Ignores small errors', 'Uses the mean'], 1, 'Quadratic near 0, linear far away.', 'Big errors are not squared.')
K.quiz('h', 'Size and rooms are highly correlated features. What happens to their weights?', ['They become exactly 0', 'They become unstable with large standard errors', 'R&sup2; drops to 0', 'Nothing'], 1, 'Multicollinearity.', 'X<sup>T</sup>X is nearly singular, so small data changes swing the weights.')
K.quiz('x', 'In the style of a Stanford CS229 exam: with the hat matrix H = X(X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>, what is X<sup>T</sup>(y &minus; Hy)?', ['y', 'The zero vector', 'X', 'H'], 1, 'Residuals are perpendicular to the columns of X.', 'X<sup>T</sup>y &minus; X<sup>T</sup>X(X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>y = 0.')
K.quiz('x', 'In the style of an MIT 18.650 exam: under the Gauss Markov assumptions, the OLS estimator is', ['Biased but low variance', 'The best (minimum variance) linear unbiased estimator', 'The maximum a posteriori estimate', 'Always normal'], 1, 'BLUE.', 'Gauss Markov: OLS is BLUE without needing normal errors.')

K.calc('e', 'ŷ = 10 + 3x. Predict at x = 4.', '22', 'Plug in.', ['3 &times; 4 = 12.', 'Add the intercept 10.', eq('22')], check=22)
K.calc('e', 'Actual 50, predicted 46. Residual?', '4', 'y &minus; ŷ.', ['Actual minus predicted.', '50 &minus; 46.', eq('4')], check=4)
K.calc('e', 'Errors 2, &minus;1, &minus;3, 2. MAE?', '2', 'Average of absolute values.', ['|errors| = 2, 1, 3, 2.', 'Sum 8.', eq('8 / 4 = 2')], check=2)
K.calc('m', 'Errors 2, &minus;1, &minus;3, 2. RMSE, 3 decimals?', '2.121', '&radic;mean of squares.', ['Squares 4, 1, 9, 4, sum 18.', 'MSE = 18 / 4 = 4.5.', eq('&radic;4.5 = 2.121')], check=round(4.5 ** 0.5, 3))
K.calc('m', 'SSE = 20, SST = 80. R&sup2;?', '0.75', '1 &minus; SSE/SST.', ['20 / 80 = 0.25.', '1 &minus; 0.25.', eq('0.75')], check=0.75)
K.calc('m', 'x&#772; = 4, y&#772; = 20, slope 3. Intercept?', '8', 'b<sub>0</sub> = y&#772; &minus; b<sub>1</sub>x&#772;.', ['3 &times; 4 = 12.', '20 &minus; 12.', eq('8')], check=8)
K.calc('m', 'Points (1, 2), (2, 4), (3, 5). Least squares slope, 2 decimals?', '1.5', 'x&#772; = 2, y&#772; = 3.667.', ['&Sigma;(x &minus; x&#772;)(y &minus; y&#772;) = (&minus;1)(&minus;1.667) + 0 + (1)(1.333) = 3.', '&Sigma;(x &minus; x&#772;)<sup>2</sup> = 2.', eq('3 / 2 = 1.5')], check=1.5)
K.calc('h', 'Correlation 0.8, std of y 10, std of x 4. Slope?', '2', 'b<sub>1</sub> = r s<sub>y</sub> / s<sub>x</sub>.', ['0.8 &times; 10 = 8.', 'Divide by 4.', eq('2')], check=2)
K.calc('h', 'R&sup2; = 0.6 with n = 51 rows and d = 10 features. Adjusted R&sup2;?', '0.5', '1 &minus; (1 &minus; R&sup2;)(n &minus; 1)/(n &minus; d &minus; 1).', ['1 &minus; R&sup2; = 0.4.', '(n &minus; 1)/(n &minus; d &minus; 1) = 50 / 40 = 1.25.', eq('1 &minus; 0.4 &times; 1.25 = 0.5')], check=0.5)
K.calc('x', 'In the style of a CMU 10-701 problem: one gradient descent step on MSE for points (1, 2) and (2, 4), starting w = 0, b = 0, learning rate 0.1. New w?', '1', '&part;L/&part;w = (2/n) &Sigma;(ŷ &minus; y)x.', ['ŷ = 0, so errors are &minus;2 and &minus;4.', 'Gradient = (2/2)(&minus;2 &times; 1 + &minus;4 &times; 2) = &minus;10.', eq('w = 0 &minus; 0.1 &times; (&minus;10) = 1')], check=1)

K.assign('fitline', 'e', 'Fit a simple regression by hand',
         '<p>Write <code>fit_line(xs, ys)</code> that returns [intercept, slope] of the least squares line, each rounded to 3 decimals. Do not use numpy.</p>',
         '''
def fit_line(xs, ys):
    # your code here
    pass
''', [('fit_line([1, 2, 3, 4, 5, 6], [52, 55, 61, 64, 70, 72])', [47.533, 4.229]), ('fit_line([1, 2, 3], [2, 4, 5])', [0.667, 1.5]), ('fit_line([0, 1], [1, 3])', [1.0, 2.0])],
         '''
def fit_line(xs, ys):
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    top = 0
    bottom = 0
    for x, y in zip(xs, ys):
        top = top + (x - mean_x) * (y - mean_y)
        bottom = bottom + (x - mean_x) ** 2
    slope = top / bottom
    intercept = mean_y - slope * mean_x
    return [round(intercept, 3), round(slope, 3)]
''', 'Compute both means, then the two sums. The slope is their ratio, and the intercept is mean_y minus slope times mean_x.', '<p>LinearRegression().fit(x.reshape(-1, 1), y) returns the same intercept_ and coef_.</p>')
K.assign('rsquared', 'e', 'Compute R squared',
         '<p>Write <code>r_squared(y_true, y_pred)</code> that returns 1 &minus; SSE / SST rounded to 4 decimals.</p>',
         '''
def r_squared(y_true, y_pred):
    # your code here
    pass
''', [('r_squared([3, 5, 7, 9], [2.5, 5.5, 6, 9.5])', 0.9125), ('r_squared([1, 2, 3], [2, 2, 2])', 0.0), ('r_squared([1, 2, 3], [1, 2, 3])', 1.0)],
         '''
def r_squared(y_true, y_pred):
    mean = sum(y_true) / len(y_true)
    sse = 0
    sst = 0
    for t, p in zip(y_true, y_pred):
        sse = sse + (t - p) ** 2
        sst = sst + (t - mean) ** 2
    return round(1 - sse / sst, 4)
''', 'SSE adds (actual &minus; predicted)<sup>2</sup>. SST adds (actual &minus; mean)<sup>2</sup>.', '<p>Predicting the mean every time gives exactly 0, as the second test shows.</p>')
K.assign('gdline', 'm', 'Gradient descent for a line',
         '<p>Write <code>gd_line(xs, ys, rate, steps)</code>. Start at w = 0 and b = 0. Each step, compute the MSE gradients (2/n) &Sigma;(ŷ &minus; y)x and (2/n) &Sigma;(ŷ &minus; y), then update both. Return [w, b] rounded to 3 decimals.</p>',
         '''
def gd_line(xs, ys, rate, steps):
    # your code here
    pass
''', [('gd_line([1, 2], [2, 4], 0.1, 1)', [1.0, 0.6]), ('gd_line([1, 2, 3, 4], [3, 5, 7, 9], 0.05, 2000)', [2.0, 1.0])],
         '''
def gd_line(xs, ys, rate, steps):
    n = len(xs)
    w = 0.0
    b = 0.0
    for i in range(steps):
        grad_w = 0.0
        grad_b = 0.0
        for x, y in zip(xs, ys):
            error = w * x + b - y
            grad_w = grad_w + 2 * error * x / n
            grad_b = grad_b + 2 * error / n
        w = w - rate * grad_w
        b = b - rate * grad_b
    return [round(w, 3), round(b, 3)]
''', 'Compute both gradients using the old w and b, then update both together.', '<p>Updating w first and then using the new w to compute the b gradient is a different (and slightly wrong) algorithm. Always compute every gradient before changing any weight.</p>')

K.must('Model and loss', 'ŷ = b<sub>0</sub> + &Sigma;b<sub>j</sub>x<sub>j</sub>. Minimise &Sigma;(y &minus; ŷ)<sup>2</sup>. Slope = cov(x, y)/var(x), line through (x&#772;, y&#772;).')
K.must('Solving', 'Normal equation w = (X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>y (use solve), or gradient descent with scaled features.')
K.must('Metrics', 'MAE, MSE, RMSE, R&sup2; = 1 &minus; SSE/SST, adjusted R&sup2;. Always on test data.')
K.must('Assumptions', 'Linear, independent errors, equal spread, normal errors for p values. Check residuals for curves and funnels.')
K.must('Outliers', 'Squared loss is pulled by outliers. Huber or absolute loss is robust. Median minimises absolute error.')
K.must('Inference', 'statsmodels OLS gives standard errors, p values and confidence intervals. Correlated features make weights unstable.')

T = K.topic(
    slug='ml-linreg', topic='ml-linreg', step=(1, 'Regression', 'ml-s1', 'Predict numbers: straight lines, curves, and how to stop a model from memorising the training data.', 'Beginner'),
    title='Linear regression: fit the best straight line', short='Linear regression', badge='1.1', minutes=65,
    lead='Learn the first real model: least squares lines by hand, many features and the normal equation, fitting and measuring with MAE, RMSE and R&sup2;, gradient descent, residual checks, robust Huber regression, and p values with statsmodels.',
    desc='simple and multiple linear regression, least squares, slope and intercept formulas, normal equation, LinearRegression, MAE, MSE, RMSE, R2, adjusted R2, MAPE, gradient descent and SGDRegressor, assumptions, residual analysis, heteroscedasticity, outliers and Huber regression, statsmodels OLS, p values and confidence intervals, projection view and Gauss Markov.',
    summary='least squares, the normal equation, regression metrics, gradient descent, residual checks, robust regression and statistical inference.',
    keywords=['linear regression', 'least squares', 'normal equation', 'R2', 'RMSE', 'MAE', 'residuals', 'Huber', 'statsmodels', 'gradient descent'],
    recap='<p>Linear regression finds the line with the smallest squared errors. Check it on test data and read its residuals.</p>',
    added='2026-11-13', leet=leet_items())
