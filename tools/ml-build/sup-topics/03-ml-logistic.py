# Supervised 2.1: logistic regression. Checked against James, Witten, Hastie and Tibshirani, An Introduction to
# Statistical Learning (2nd edition) chapter 4.3, Hastie, Tibshirani and Friedman, The Elements of Statistical
# Learning chapter 4.4, Bishop, Pattern Recognition and Machine Learning chapter 4.3, the Stanford CS229 notes on
# logistic regression and softmax, and the scikit-learn 1.8 user guide section 1.1.11 (LogisticRegression, C, solvers).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-logistic')
K = Kit()

K.code('sigmoid_odds', r'''
import math

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

for z in [-4, -2, 0, 2, 4]:
    p = sigmoid(z)
    odds = p / (1 - p)
    print("z =", str(z).rjust(2), " probability", round(p, 3), " odds", round(odds, 3), " log odds", round(math.log(odds), 3))
''')

K.code('logistic_by_hand', r'''
import math

hours = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
passed = [0, 0, 0, 0, 1, 0, 1, 1, 1, 1]

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

w = 0.0
b = 0.0
rate = 0.5
n = len(hours)
for epoch in range(2001):
    grad_w = 0.0
    grad_b = 0.0
    loss = 0.0
    for x, y in zip(hours, passed):
        p = sigmoid(w * x + b)
        grad_w = grad_w + (p - y) * x / n
        grad_b = grad_b + (p - y) / n
        loss = loss - (y * math.log(p) + (1 - y) * math.log(1 - p)) / n
    if epoch in (0, 100, 500, 2000):
        print("epoch", str(epoch).rjust(4), " w", round(w, 3), " b", round(b, 3), " log loss", round(loss, 4))
    w = w - rate * grad_w
    b = b - rate * grad_b

print("chance to pass after 3.2 hours:", round(sigmoid(w * 3.2 + b), 3))
print("50% point (decision boundary): x =", round(-b / w, 2), "hours")
''', long=True)

K.code('cancer_logistic', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.25, random_state=0, stratify=data.target)

model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
print("classes:", data.target_names.tolist(), " (1 means benign)")
print("test accuracy:", round(model.score(X_test, y_test), 3))
print("first 3 test rows, P(benign):", np.round(model.predict_proba(X_test[:3])[:, 1], 3).tolist())
print("predicted labels:", model.predict(X_test[:3]).tolist(), " true labels:", y_test[:3].tolist())
coef = model[-1].coef_[0]
order = np.argsort(np.abs(coef))[::-1][:3]
print("strongest features:", [(str(data.feature_names[i]), round(float(coef[i]), 2)) for i in order])
''')

K.code('threshold_choice', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
y = 1 - data.target                      # now 1 means malignant (the case we must not miss)
X_train, X_test, y_train, y_test = train_test_split(data.data, y, test_size=0.25, random_state=0, stratify=y)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X_train, y_train)
prob = model.predict_proba(X_test)[:, 1]

for threshold in [0.2, 0.5, 0.8]:
    pred = (prob >= threshold).astype(int)
    missed = int(((pred == 0) & (y_test == 1)).sum())
    print("threshold", threshold, " precision", round(precision_score(y_test, pred), 3),
          " recall", round(recall_score(y_test, pred), 3), " missed cancers", missed)
''')

K.code('softmax_iris', r'''
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

def softmax(scores):
    exps = [np.exp(s - max(scores)) for s in scores]
    total = sum(exps)
    return [round(float(e / total), 3) for e in exps]

print("softmax of scores [2.0, 1.0, 0.1]:", softmax([2.0, 1.0, 0.1]))

X, y = load_iris(return_X_y=True)
model = LogisticRegression(max_iter=1000)
print("iris 3 classes, cross validated accuracy:", round(cross_val_score(model, X, y, cv=5).mean(), 3))
model.fit(X, y)
print("one flower, class probabilities:", np.round(model.predict_proba(X[[60]]), 3).tolist())
print("weights shape (classes x features):", model.coef_.shape)
''')

K.code('odds_ratio', r'''
import numpy as np
from sklearn.linear_model import LogisticRegression

rng = np.random.default_rng(0)
n = 2000
smoker = rng.integers(0, 2, n)
age = rng.uniform(30, 70, n)
true_logit = -6 + 1.2 * smoker + 0.08 * age
sick = (rng.uniform(size=n) < 1 / (1 + np.exp(-true_logit))).astype(int)

X = np.column_stack([smoker, age])
model = LogisticRegression(C=1e6, max_iter=5000).fit(X, sick)     # almost no penalty
w_smoker, w_age = model.coef_[0]
print("weights: smoker", round(w_smoker, 3), " age", round(w_age, 3))
print("odds ratio for smoking:", round(np.exp(w_smoker), 2), " (true", round(np.exp(1.2), 2), ")")
print("odds ratio for 10 more years:", round(np.exp(10 * w_age), 2), " (true", round(np.exp(0.8), 2), ")")
''')

K.code('curved_boundary', r'''
from sklearn.datasets import make_circles
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

X, y = make_circles(n_samples=400, noise=0.1, factor=0.5, random_state=0)
straight = LogisticRegression()
curved = make_pipeline(PolynomialFeatures(2), StandardScaler(), LogisticRegression())
print("straight boundary accuracy:", round(cross_val_score(straight, X, y, cv=5).mean(), 3))
print("with squared features:     ", round(cross_val_score(curved, X, y, cv=5).mean(), 3))
curved.fit(X, y)
names = curved[0].get_feature_names_out(["x1", "x2"])
weights = curved[-1].coef_[0]
print("biggest weights:", sorted([(n, round(float(w), 2)) for n, w in zip(names, weights)], key=lambda t: -abs(t[1]))[:2])
''')

K.code('penalty_c', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
for C in [0.001, 0.01, 0.1, 1, 100]:
    model = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=5000))
    score = cross_val_score(model, X, y, cv=5).mean()
    size = abs(model.fit(X, y)[-1].coef_).sum()
    print("C =", str(C).ljust(5), " accuracy", round(score, 3), " total weight size", round(size, 1))
''')

K.lesson('idea', 'From a score to a probability', f'''
{src('James, Witten, Hastie and Tibshirani, An Introduction to Statistical Learning chapter 4.3, Hastie, Tibshirani and Friedman, The Elements of Statistical Learning chapter 4.4, Bishop, Pattern Recognition and Machine Learning chapter 4.3, the Stanford CS229 notes, and the scikit-learn 1.8 user guide.')}
{viz('mlsigmoid')}
{wwh('<b>Logistic regression</b> is a <b>classification</b> model: it predicts the probability that an example belongs to the positive class (spam, sick, will buy). It computes a linear score z = w&middot;x + b and squashes it with the <b>sigmoid</b> &sigma;(z) = 1 / (1 + e<sup>&minus;z</sup>) into a number between 0 and 1.',
     'Linear regression gives any number, even &minus;3 or 1.7, which makes no sense as a probability. Logistic regression gives a real probability, so you can rank cases, choose your own threshold, and combine it with costs. It is fast, explainable, and the standard baseline for every yes or no problem.',
     'The score z is the <b>log odds</b>: ln(p / (1 &minus; p)) = w&middot;x + b. Each weight says how much one unit of a feature changes the log odds. Predict class 1 when p &ge; 0.5, which is the same as z &ge; 0, so the decision boundary is the straight line (or plane) w&middot;x + b = 0.')}
{run('sigmoid_odds')}
{fxs(fx('Sigmoid', '&sigma;(z) = 1 / (1 + e<sup>&minus;z</sup>)', 'Maps any number to 0 to 1. &sigma;(0) = 0.5.', key=True),
     fx('Logistic model', 'P(y = 1 | x) = &sigma;(w&middot;x + b)', 'A linear score inside a sigmoid.', key=True),
     fx('Log odds (logit)', 'ln(p / (1 &minus; p)) = w&middot;x + b', 'Linear in the features.', key=True))}
{scene('a credit score', '<p>A bank adds points for income and years at the same job and takes points away for missed payments: that total is the score z. A table then turns the score into "chance of paying back". Logistic regression learns both the points (the weights) and the table (the sigmoid) from past customers.</p>')}
''', kw=['logistic regression', 'classification', 'sigmoid', 'probability', 'log odds', 'logit', 'decision boundary'])

K.lesson('train', 'Training with log loss', f'''
{viz('mllogfit')}
{wwh('Logistic regression is trained by minimising <b>log loss</b> (binary cross entropy): &minus;[y ln p + (1 &minus; y) ln(1 &minus; p)], averaged over the examples. There is no closed form answer, so we use gradient descent or a faster solver.',
     'Squared error with a sigmoid gives a bumpy, non convex loss and weak gradients when the model is confidently wrong. Log loss is convex, punishes confident mistakes heavily, and comes straight from maximum likelihood for yes or no data (Foundations 2.3).',
     'The gradient is surprisingly simple: &part;L/&part;w = (1/n) &Sigma; (p<sub>i</sub> &minus; y<sub>i</sub>) x<sub>i</sub>, the same shape as linear regression with p in place of ŷ. Repeat w &larr; w &minus; &eta; &times; gradient until the loss stops falling.')}
{run('logistic_by_hand')}
{fxs(fx('Log loss', 'L = &minus;(1/n) &Sigma; [y<sub>i</sub> ln p<sub>i</sub> + (1 &minus; y<sub>i</sub>) ln(1 &minus; p<sub>i</sub>)]', 'Convex in w and b.', key=True),
     fx('Gradient', '&part;L/&part;w = (1/n) &Sigma; (p<sub>i</sub> &minus; y<sub>i</sub>) x<sub>i</sub>', 'Prediction minus label, times the input.', key=True))}
{note('The program learns w = 2.59 and b = &minus;7.11, so the 50% point is 7.11 / 2.59 = 2.75 hours. Students who study more than 2.75 hours are predicted to pass.', 'tip')}
''', kw=['log loss', 'binary cross entropy', 'gradient', 'maximum likelihood', 'convex', 'gradient descent', 'lbfgs'])

K.lesson('sklearn', 'Logistic regression in scikit-learn', f'''
{wwh('LogisticRegression in scikit-learn gives <b>predict</b> (the class), <b>predict_proba</b> (the probabilities) and <b>coef_</b> (the weights). Put a StandardScaler before it so the solver converges and the weights are comparable.',
     'This is the version you will use in real projects. It handles many features, regularisation and several classes, and it is fast enough for millions of rows.',
     'Fit on the training data. Use predict_proba when you need a ranking or your own threshold, and predict for the default 0.5 threshold. After scaling, a larger |weight| means a feature with more influence on the log odds.')}
{run('cancer_logistic')}
{note('LogisticRegression adds an L2 penalty by default (C = 1.0). If you see a ConvergenceWarning, scale the features or raise max_iter. Do not just ignore it.', 'warn')}
''', kw=['LogisticRegression', 'predict_proba', 'predict', 'coef_', 'StandardScaler', 'convergence warning', 'breast cancer dataset'])

K.lesson('threshold', 'Choosing the threshold', f'''
{wwh('The model gives a probability. The <b>threshold</b> turns it into a decision: class 1 if p &ge; threshold. 0.5 is only the default.',
     'Mistakes have different costs. Missing a cancer (a false negative) is far worse than an extra check (a false positive). A spam filter is the opposite: losing a real email is worse than letting one spam through.',
     'Lower the threshold to catch more positives (higher <b>recall</b>) at the cost of more false alarms (lower <b>precision</b>). Raise it for the reverse. Pick the threshold on validation data using the real costs. Supervised 4.1 covers precision, recall and ROC curves in detail.')}
{run('threshold_choice')}
{note('Here 1 means malignant. Moving the threshold from 0.5 down to 0.2 cuts the missed cancers from 2 to 1, and the price is a precision drop from 1.0 to 0.852 (more healthy people sent for extra tests).', 'exam')}
''', kw=['threshold', 'precision', 'recall', 'false negative', 'false positive', 'cost sensitive'])

K.lesson('multi', 'More than two classes: softmax', f'''
{wwh('For k classes, <b>multinomial logistic regression</b> (softmax regression) computes one score per class and turns the scores into probabilities with the <b>softmax</b>: p<sub>j</sub> = e<sup>z<sub>j</sub></sup> / &Sigma; e<sup>z<sub>m</sub></sup>.',
     'Many problems have more than two answers: which flower species, which digit, which product category. Softmax gives one probability per class, and they add up to 1.',
     'Learn one weight vector per class (coef_ has shape classes &times; features). The class with the largest score has the largest probability. The loss is categorical cross entropy, &minus;ln of the probability given to the true class. scikit-learn uses softmax automatically when there are more than two classes.')}
{run('softmax_iris')}
{fx('Softmax', 'p<sub>j</sub> = e<sup>z<sub>j</sub></sup> / &Sigma;<sub>m</sub> e<sup>z<sub>m</sub></sup>', 'Subtract the largest score first so e<sup>z</sup> never overflows. The answer does not change.', key=True)}
{note('One versus rest (OvR) is the other way to do multi class: train k separate yes or no models and pick the most confident. Softmax trains them together and gives probabilities that add up to 1, so it is usually preferred.', 'tip')}
''', kw=['multiclass', 'softmax', 'multinomial logistic regression', 'categorical cross entropy', 'one versus rest', 'iris'])

K.lesson('odds', 'Reading the weights: odds ratios', f'''
{wwh('e<sup>w</sup> is the <b>odds ratio</b>: how many times the odds of class 1 are multiplied when that feature goes up by 1, holding the others fixed.',
     'Doctors, banks and policy makers want answers like "smokers have three times the odds of the disease". Odds ratios give exactly that from a fitted model.',
     'Fit the model on unscaled features if you want the answer in natural units (per year, per smoker). Take e to the power of each weight. An odds ratio above 1 raises the chance, below 1 lowers it, and 1 means no effect.')}
{run('odds_ratio')}
{note('Odds are not probabilities. Tripling the odds from 0.1 to 0.3 moves the probability from 9% to 23%, not to 27%. Near 50% the effect on probability is largest.', 'warn')}
''', kw=['odds ratio', 'odds', 'interpretation', 'e to the w', 'effect size'])

K.lesson('boundary', 'Curved boundaries and the penalty C', f'''
{wwh('The decision boundary of logistic regression is a straight line (a plane in more dimensions). Adding polynomial features (x<sub>1</sub><sup>2</sup>, x<sub>2</sub><sup>2</sup>, x<sub>1</sub>x<sub>2</sub>) lets it draw curves. The parameter <b>C</b> controls the penalty: C is 1/&alpha;, so a <b>small C means a strong penalty</b>.',
     'Real classes are often not split by a straight line, like an inner ring of one class inside a ring of the other. And with many features, an unpenalised model overfits or, if the classes are perfectly separable, its weights grow without limit.',
     'Put PolynomialFeatures, StandardScaler and LogisticRegression in one pipeline. Tune C on a log scale with cross validation (LogisticRegressionCV does it for you).')}
{run('curved_boundary')}
{run('penalty_c')}
{note('In scikit-learn, C is the inverse of the penalty strength. C = 0.001 shrinks the weights a lot (underfits, 0.891), C = 1 is best here (0.981), and C = 100 hardly penalises (0.963, slightly overfit). Ridge uses &alpha;, where a bigger number means a stronger penalty, so do not mix them up.', 'exam')}
''', kw=['decision boundary', 'nonlinear boundary', 'polynomial features', 'C parameter', 'inverse regularisation', 'LogisticRegressionCV', 'separable data'])

K.lesson('versus', 'Logistic regression compared', f'''
{versus('Logistic regression against other approaches', ['', 'Linear regression on 0 and 1', 'Logistic regression', 'Naive Bayes', 'Tree models'], [
    ['Output', 'Any number', 'A probability', 'A probability', 'Class or probability'],
    ['Boundary', 'Straight', 'Straight (curved with extra features)', 'Depends on the distributions', 'Boxes, very flexible'],
    ['Loss', 'Squared error', 'Log loss (convex)', 'Counts and likelihoods', 'Impurity'],
    ['Calibrated probabilities', 'No', 'Usually good', 'Often too extreme', 'Often need calibration'],
    ['Explainable', 'Yes', 'Yes: odds ratios', 'Yes', 'Single tree yes, forests less'],
    ['Needs scaling', 'Helpful', 'Yes for the solver and penalty', 'No', 'No']],
    'logistic regression is the first classifier to try. Move to trees or boosting when the boundary is clearly not linear.')}
{deep('Generative vs discriminative', '<p>Logistic regression is <b>discriminative</b>: it models P(y | x) directly. Naive Bayes and LDA are <b>generative</b>: they model P(x | y) and P(y) and use Bayes rule. If the classes are Gaussian with a shared covariance, the posterior of LDA has exactly the logistic form, but logistic regression makes fewer assumptions. Ng and Jordan (2002) showed generative models can reach their (higher) error faster with little data, while logistic regression reaches a lower error with more data.</p>')}
''', kw=['logistic vs linear regression', 'discriminative', 'generative', 'LDA', 'calibration', 'model comparison'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Model', 'p = &sigma;(w&middot;x + b), &sigma;(z) = 1 / (1 + e<sup>&minus;z</sup>)', 'Probability of class 1.', key=True),
     fx('Sigmoid derivative', '&sigma;&prime;(z) = &sigma;(z)(1 &minus; &sigma;(z))', 'Used to derive the gradient.', key=True),
     fx('Log loss and gradient', 'L = &minus;(1/n)&Sigma;[y ln p + (1 &minus; y) ln(1 &minus; p)], &nabla;<sub>w</sub>L = (1/n) X<sup>T</sup>(p &minus; y)', 'The derivative of the sigmoid cancels nicely.', key=True),
     fx('Softmax and its loss', 'p<sub>j</sub> = e<sup>z<sub>j</sub></sup> / &Sigma;e<sup>z<sub>m</sub></sup>, L = &minus;ln p<sub>true</sub>', 'Gradient for class j: p<sub>j</sub> &minus; 1[j = true].', key=True),
     fx('Odds ratio', 'OR = e<sup>w</sup>', 'Multiplier on the odds per unit of the feature.'))}
{steps('Worked example: one prediction and its loss', [
    'w = 2, b = &minus;5, a student studied x = 3 hours and passed (y = 1).',
    'Score z = 2 &times; 3 &minus; 5 = 1.',
    'p = &sigma;(1) = 1 / (1 + e<sup>&minus;1</sup>) = 1 / 1.368 = 0.731.',
    eq('loss = &minus;ln(0.731) = 0.313'),
    'Gradient for w on this row: (p &minus; y) x = (0.731 &minus; 1) &times; 3 = &minus;0.807, so w goes up and the next prediction is higher.'])}
{deep('Why the gradient is so clean', '<p>For one example, L = &minus;[y ln &sigma;(z) + (1 &minus; y) ln(1 &minus; &sigma;(z))]. Using &sigma;&prime; = &sigma;(1 &minus; &sigma;), dL/dz = &minus;y(1 &minus; &sigma;) + (1 &minus; y)&sigma; = &sigma; &minus; y. Then by the chain rule dL/dw = (&sigma; &minus; y)x. The Hessian is X<sup>T</sup>SX with S = diag(p(1 &minus; p)), which is positive semi definite, so the loss is convex. Newton’s method on this loss is called iteratively reweighted least squares (IRLS).</p>')}
''', kw=['sigmoid derivative', 'log loss gradient', 'softmax gradient', 'Hessian', 'IRLS', 'Newton method'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Logistic regression gives the chance that something is a yes. It adds up weighted features into a score and squashes the score into 0 to 1 with an S shaped curve.</p>',
    '<p>Train LogisticRegression with scaling, use predict_proba, pick a threshold for the real costs, handle many classes with softmax, and read weights as odds ratios.</p>',
    '<p>Derive the log loss gradient, explain convexity, use polynomial features for curved boundaries, tune C, and know what happens with perfectly separable data.</p>',
    '<p>Connect logistic regression to generalised linear models and exponential families, IRLS, the generative vs discriminative trade off (Ng and Jordan, 2002), calibration theory, and the softmax layer at the end of every neural network classifier.</p>')}
{grow('Turn a score into a probability with the sigmoid and pick a class.',
      'Build, threshold and interpret a logistic regression in scikit-learn.',
      'Derive its training rule and reason about convexity, separability and regularisation.')}
''', kw=['beginner', 'expert', 'GLM', 'exponential family', 'calibration'])

lc(1822, 'Sign of the Product of an Array', 'sign-of-the-product-of-an-array', 'e', 'Decide the sign without the big number', 'A 0 makes the product 0. Otherwise only the count of negative numbers matters: odd gives &minus;1, even gives 1. A classifier also only needs the sign of its score.', r'''
def array_sign(nums):
    negatives = 0
    for x in nums:
        if x == 0:
            return 0
        if x < 0:
            negatives = negatives + 1
    if negatives % 2 == 1:
        return -1
    return 1
''', [('array_sign([-1, -2, -3, -4, 3, 2, 1])', 1), ('array_sign([1, 5, 0, 2, -3])', 0), ('array_sign([-1, 1, -1, 1, -1])', -1)])
lc(1608, 'Special Array With X Elements Greater Than or Equal X', 'special-array-with-x-elements-greater-than-or-equal-x', 'e', 'Search for a threshold', 'Try every threshold x from 0 to n and count how many numbers are at least x. Exactly x of them means x is the answer.', r'''
def special_array(nums):
    for x in range(len(nums) + 1):
        count = 0
        for v in nums:
            if v >= x:
                count = count + 1
        if count == x:
            return x
    return -1
''', [('special_array([3, 5])', 2), ('special_array([0, 0])', -1), ('special_array([0, 4, 3, 0, 4])', 3)])
lc(2389, 'Longest Subsequence With Limited Sum', 'longest-subsequence-with-limited-sum', 'e', 'Prefix sums and a threshold per query', 'Take the smallest numbers first. Sort, build prefix sums, and for each query binary search how many prefix sums stay at or under it.', r'''
from bisect import bisect_right


def answer_queries(nums, queries):
    s = sorted(nums)
    prefix = []
    total = 0
    for x in s:
        total = total + x
        prefix.append(total)
    return [bisect_right(prefix, q) for q in queries]
''', [('answer_queries([4, 5, 2, 1], [3, 10, 21])', [2, 3, 4]), ('answer_queries([2, 3, 4, 5], [1])', [0])])
lc(1385, 'Find the Distance Value Between Two Arrays', 'find-the-distance-value-between-two-arrays', 'e', 'Nearest neighbour check with a threshold', 'Sort arr2. For each x in arr1, binary search the closest values in arr2. Count x when even the closest one is more than d away.', r'''
from bisect import bisect_left


def find_the_distance_value(arr1, arr2, d):
    s = sorted(arr2)
    count = 0
    for x in arr1:
        i = bisect_left(s, x)
        ok = True
        if i < len(s) and s[i] - x <= d:
            ok = False
        if i > 0 and x - s[i - 1] <= d:
            ok = False
        if ok:
            count = count + 1
    return count
''', [('find_the_distance_value([4, 5, 8], [10, 9, 1, 8], 2)', 2), ('find_the_distance_value([1, 4, 2, 3], [-4, -3, 6, 10, 20, 30], 3)', 2)])
lc(2300, 'Successful Pairs of Spells and Potions', 'successful-pairs-of-spells-and-potions', 'm', 'Binary search for the decision boundary', 'Sort the potions. For a spell s, a potion works when s &times; potion &ge; success, so find the first potion at least ceil(success / s). Everything to its right succeeds, like points past a decision boundary.', r'''
from bisect import bisect_left


def successful_pairs(spells, potions, success):
    s = sorted(potions)
    result = []
    for spell in spells:
        need = (success + spell - 1) // spell
        i = bisect_left(s, need)
        result.append(len(s) - i)
    return result
''', [('successful_pairs([5, 1, 3], [1, 2, 3, 4, 5], 7)', [4, 0, 3]), ('successful_pairs([3, 1, 2], [8, 5, 8], 16)', [2, 0, 2])])
lc(1300, 'Sum of Mutated Array Closest to Target', 'sum-of-mutated-array-closest-to-target', 'm', 'Choose a threshold that minimises an error', 'Capping every number at v gives a sum that grows with v. Binary search the largest v whose capped sum is at most the target, then compare v and v + 1 and keep the one with the smaller error (smaller v on a tie).', r'''
def capped_sum(arr, v):
    total = 0
    for x in arr:
        total = total + min(x, v)
    return total


def find_best_value(arr, target):
    low = 0
    high = max(arr)
    while low < high:
        mid = (low + high + 1) // 2
        if capped_sum(arr, mid) <= target:
            low = mid
        else:
            high = mid - 1
    if abs(capped_sum(arr, low + 1) - target) < abs(capped_sum(arr, low) - target):
        return low + 1
    return low
''', [('find_best_value([4, 9, 3], 10)', 3), ('find_best_value([2, 3, 5], 10)', 5), ('find_best_value([60864, 25176, 27249, 21296, 20204], 56803)', 11361)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>A classifier makes a decision by comparing a score with a threshold. These problems practise that move: decide a sign without computing the big number, search for a threshold, find the boundary with binary search, and choose the cut off that gives the smallest error. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'threshold', 'binary search', 'decision boundary', 'prefix sum', 'sign'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Logistic regression</b> predicts P(y = 1 | x) = &sigma;(w&middot;x + b). The score is the log odds.',
    'The <b>sigmoid</b> maps any score to 0 to 1, with &sigma;(0) = 0.5. The boundary w&middot;x + b = 0 is a straight line.',
    'Train by minimising <b>log loss</b>. It is convex, and its gradient is (1/n)&Sigma;(p &minus; y)x.',
    'predict_proba gives probabilities. Choose the <b>threshold</b> from the costs of false negatives and false positives.',
    '<b>Softmax</b> handles k classes: one score per class, probabilities add up to 1, loss = &minus;ln p<sub>true</sub>.',
    '<b>Odds ratio</b> e<sup>w</sup>: how the odds multiply per unit of a feature.',
    'Polynomial features give curved boundaries. <b>C</b> = 1/&alpha;: small C means a strong penalty.'],
    'Supervised 2.2 is a very different classifier with no training at all: k nearest neighbours.')}
{files('Three tasks: the sigmoid, the log loss of one prediction, and a softmax.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Logistic regression is used for', ['Predicting prices', 'Classification', 'Clustering', 'Dimensionality reduction'], 1, 'Despite its name.', 'It predicts class probabilities.')
K.quiz('e', '&sigma;(0) equals', ['0', '0.5', '1', 'e'], 1, '1 / (1 + 1).', '1 / (1 + e<sup>0</sup>) = 0.5.')
K.quiz('e', 'Which method gives probabilities in scikit-learn?', ['predict', 'predict_proba', 'score', 'fit'], 1, 'proba.', 'predict_proba returns one probability per class.')
K.quiz('e', 'With the default threshold, class 1 is predicted when', ['p &gt; 0.9', 'p &ge; 0.5', 'z &lt; 0', 'p = 1'], 1, 'Halfway.', 'p &ge; 0.5, which is z &ge; 0.')
K.quiz('m', 'The decision boundary of plain logistic regression is', ['A circle', 'A straight line or plane', 'A step', 'Any curve'], 1, 'Where z = 0.', 'w&middot;x + b = 0 is linear.')
K.quiz('m', 'Lowering the threshold from 0.5 to 0.2 usually', ['Raises precision', 'Raises recall', 'Changes the weights', 'Has no effect'], 1, 'More positives predicted.', 'More true positives are caught, with more false alarms.')
K.quiz('m', 'In scikit-learn, a smaller C means', ['A weaker penalty', 'A stronger penalty', 'No penalty', 'More classes'], 1, 'C = 1/&alpha;.', 'C is the inverse of the regularisation strength.')
K.quiz('m', 'A weight of 0.7 means the odds multiply by', ['0.7', 'e<sup>0.7</sup> &asymp; 2.01', '1.7', '0.5'], 1, 'Odds ratio.', 'e<sup>0.7</sup> &asymp; 2.01.')
K.quiz('m', 'Softmax outputs for 3 classes always', ['Add up to 1', 'Are all 0.33', 'Are 0 or 1', 'Can be negative'], 0, 'They are probabilities.', 'The sum is divided out, so they add up to 1.')
K.quiz('h', 'Why is log loss used instead of squared error for logistic regression?', ['It is faster to type', 'It is convex in w and punishes confident mistakes', 'Squared error cannot be computed', 'It gives exact zeros'], 1, 'Convexity.', 'Log loss with a sigmoid is convex, squared error with a sigmoid is not.')
K.quiz('h', 'The training data is perfectly separable and C is huge. What happens?', ['The model fails to fit', 'The weights grow very large and probabilities become 0 or 1', 'Accuracy drops', 'It becomes linear regression'], 1, 'Nothing stops the loss from shrinking.', 'Scaling w up always lowers the loss, so a penalty is needed.')
K.quiz('h', 'An inner ring of class A sits inside a ring of class B. Plain logistic regression gets about 50%. The fix is', ['More iterations', 'Add squared features x<sub>1</sub><sup>2</sup> and x<sub>2</sub><sup>2</sup>', 'Raise the threshold', 'Remove scaling'], 1, 'A circle is x<sub>1</sub><sup>2</sup> + x<sub>2</sub><sup>2</sup> = r<sup>2</sup>.', 'With squared features the boundary can be a circle (0.997 in the program).')
K.quiz('x', 'In the style of a Stanford CS229 exam: for logistic regression, the gradient of the log loss with respect to w for one example is', ['(y &minus; p)x<sup>2</sup>', '(p &minus; y)x', 'p(1 &minus; p)x', '&minus;y ln p'], 1, 'dL/dz = p &minus; y.', 'Chain rule with &sigma;&prime; = &sigma;(1 &minus; &sigma;).')
K.quiz('x', 'In the style of a CMU 10-701 exam: Gaussian class conditionals with a shared covariance make P(y | x)', ['Quadratic in x inside a sigmoid', 'A logistic function of a linear score', 'Uniform', 'Independent of x'], 1, 'LDA.', 'The quadratic terms cancel, leaving a linear log odds.')

K.calc('e', '&sigma;(0)?', '0.5', '1 / (1 + e<sup>0</sup>).', ['e<sup>0</sup> = 1.', '1 / (1 + 1).', eq('0.5')], check=0.5)
K.calc('e', 'w = 2, b = &minus;4, x = 3. Score z?', '2', 'w x + b.', ['2 &times; 3 = 6.', 'Add b.', eq('6 &minus; 4 = 2')], check=2)
K.calc('e', 'p = 0.8. Odds?', '4', 'p / (1 &minus; p).', ['1 &minus; 0.8 = 0.2.', '0.8 / 0.2.', eq('4')], check=4)
K.calc('m', '&sigma;(2), 3 decimals?', '0.881', '1 / (1 + e<sup>&minus;2</sup>).', ['e<sup>&minus;2</sup> = 0.1353.', '1 / 1.1353.', eq('0.881')], check=0.881)
K.calc('m', 'Log loss for y = 1, p = 0.9, 4 decimals?', '0.1054', '&minus;ln p.', ['Positive label, so use &minus;ln p.', '&minus;ln 0.9.', eq('0.1054')], check=0.1054)
K.calc('m', 'Log loss for y = 0, p = 0.9, 4 decimals?', '2.3026', '&minus;ln(1 &minus; p).', ['Negative label, so use &minus;ln(1 &minus; p).', '&minus;ln 0.1.', eq('2.3026')], check=2.3026)
K.calc('m', 'Boundary for w = 2.5, b = &minus;10 (one feature)?', '4', 'w x + b = 0.', ['2.5x = 10.', 'Divide.', eq('x = 4')], check=4)
K.calc('h', 'Odds ratio for w = ln 3?', '3', 'e<sup>w</sup>.', ['e<sup>ln 3</sup>.', 'e and ln cancel.', eq('3')], check=3)
K.calc('h', 'Softmax of scores [0, ln 3]. Probability of the second class?', '0.75', 'e<sup>z</sup> / &Sigma;.', ['e<sup>0</sup> = 1 and e<sup>ln 3</sup> = 3.', 'Sum 4.', eq('3 / 4 = 0.75')], check=0.75)
K.calc('x', 'In the style of an MIT 6.867 problem: one gradient step, w = 0, b = 0, single example x = 2, y = 1, learning rate 0.5. New w?', '0.5', 'p = 0.5 at the start.', ['Gradient (p &minus; y)x = (0.5 &minus; 1) &times; 2 = &minus;1.', 'w &minus; 0.5 &times; (&minus;1).', eq('w = 0.5')], check=0.5)

K.assign('sigmoid', 'e', 'The sigmoid',
         '<p>Write <code>sigmoid(z)</code> that returns 1 / (1 + e<sup>&minus;z</sup>) rounded to 4 decimals. Use math.exp.</p>',
         '''
import math


def sigmoid(z):
    # your code here
    pass
''', [('sigmoid(0)', 0.5), ('sigmoid(2)', 0.8808), ('sigmoid(-3)', 0.0474)],
         '''
import math


def sigmoid(z):
    return round(1 / (1 + math.exp(-z)), 4)
''', 'One line with math.exp(-z).', '<p>For very negative z, math.exp(-z) can overflow. Libraries use the equivalent form e<sup>z</sup> / (1 + e<sup>z</sup>) when z &lt; 0.</p>')
K.assign('logloss1', 'e', 'Log loss of a set of predictions',
         '<p>Write <code>log_loss(labels, probs)</code> that returns the average of &minus;[y ln p + (1 &minus; y) ln(1 &minus; p)], rounded to 4 decimals.</p>',
         '''
import math


def log_loss(labels, probs):
    # your code here
    pass
''', [('log_loss([1, 0], [0.9, 0.1])', 0.1054), ('log_loss([1], [0.5])', 0.6931), ('log_loss([0, 0, 1], [0.2, 0.4, 0.7])', 0.3635)],
         '''
import math


def log_loss(labels, probs):
    total = 0
    for y, p in zip(labels, probs):
        total = total - (y * math.log(p) + (1 - y) * math.log(1 - p))
    return round(total / len(labels), 4)
''', 'Add the two terms for each example. Only one of them is non zero because y is 0 or 1.', '<p>This matches sklearn.metrics.log_loss.</p>')
K.assign('softmax', 'm', 'Softmax',
         '<p>Write <code>softmax(scores)</code> that returns the list of probabilities e<sup>z<sub>j</sub></sup> / &Sigma; e<sup>z</sup>, each rounded to 3 decimals. Subtract the largest score first so very large scores do not overflow.</p>',
         '''
import math


def softmax(scores):
    # your code here
    pass
''', [('softmax([2.0, 1.0, 0.1])', [0.659, 0.242, 0.099]), ('softmax([1000, 1000])', [0.5, 0.5]), ('softmax([0, 0, 0, 0])', [0.25, 0.25, 0.25, 0.25])],
         '''
import math


def softmax(scores):
    top = max(scores)
    exps = []
    for s in scores:
        exps.append(math.exp(s - top))
    total = sum(exps)
    return [round(e / total, 3) for e in exps]
''', 'Find the largest score, subtract it from every score, take exp, and divide by the sum.', '<p>Without subtracting the maximum, math.exp(1000) overflows. Subtracting a constant from every score does not change the softmax.</p>')

K.must('Model', 'P(y = 1 | x) = &sigma;(w&middot;x + b), &sigma;(z) = 1/(1 + e<sup>&minus;z</sup>). Score = log odds. Boundary w&middot;x + b = 0.')
K.must('Training', 'Minimise log loss (convex). Gradient (1/n)&Sigma;(p &minus; y)x. No closed form, use lbfgs or gradient descent.')
K.must('Threshold', 'Default 0.5. Lower it for higher recall, raise it for higher precision. Choose from costs on validation data.')
K.must('Multi class', 'Softmax p<sub>j</sub> = e<sup>z<sub>j</sub></sup>/&Sigma;e<sup>z</sup>, loss &minus;ln p<sub>true</sub>. Or one versus rest.')
K.must('Interpretation', 'Odds ratio e<sup>w</sup> per unit. Scale features for comparable weights.')
K.must('Penalty', 'C = 1/&alpha;, small C = strong L2 penalty. Needed for separable data. Polynomial features give curved boundaries.')

T = K.topic(
    slug='ml-logistic', topic='ml-logistic', step=(2, 'Classification', 'ml-s2', 'Predict categories: yes or no, spam or not, or which of many classes, with four very different families of models.', 'Intermediate'),
    title='Logistic regression: probabilities for classification', short='Logistic regression', badge='2.1', minutes=65,
    lead='Learn the standard classifier: the sigmoid, log odds and decision boundaries, training with log loss and gradient descent, scikit-learn with predict_proba, choosing a threshold, softmax for many classes, odds ratios, curved boundaries and the penalty C.',
    desc='classification, sigmoid, probability, odds and log odds, decision boundary, log loss, binary cross entropy, gradient of log loss, LogisticRegression, predict_proba, threshold, precision and recall trade off, multinomial softmax regression, one versus rest, odds ratios, polynomial features, C and regularisation, separable data, generative vs discriminative, IRLS.',
    summary='the sigmoid, log loss training, thresholds, softmax for many classes, odds ratios and the penalty C.',
    keywords=['logistic regression', 'sigmoid', 'log loss', 'classification', 'softmax', 'odds ratio', 'threshold', 'decision boundary', 'predict_proba', 'C'],
    recap='<p>Logistic regression is a straight line score inside a sigmoid. It gives probabilities you can trust and explain.</p>',
    added='2026-11-13', leet=leet_items())
