# Supervised 2.4: support vector machines. Checked against Cortes and Vapnik, Support-Vector Networks (Machine
# Learning, 1995), Hastie, Tibshirani and Friedman, The Elements of Statistical Learning chapter 12, Bishop, Pattern
# Recognition and Machine Learning chapter 7, Stanford CS229 lecture notes on SVMs (Andrew Ng), Shalev-Shwartz and
# others, Pegasos (ICML 2007), Platt, Sequential Minimal Optimization (1998), and the scikit-learn 1.8 user guide section 1.4.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-svm')
K = Kit()

K.code('margin_by_hand', r'''
import numpy as np
from sklearn.svm import SVC

X = np.array([[1, 1], [2, 1], [1, 2], [4, 4], [5, 4], [4, 5]])
y = np.array([0, 0, 0, 1, 1, 1])
model = SVC(kernel="linear", C=1000).fit(X, y)
w = model.coef_[0]
b = model.intercept_[0]
print("w =", np.round(w, 3).tolist(), " b =", round(float(b), 3))
print("support vectors:", model.support_vectors_.tolist())
print("margin width 2 / |w| =", round(float(2 / np.linalg.norm(w)), 3))
for point in X:
    print(point.tolist(), " w.x + b =", round(float(w @ point + b), 3))
''')

K.code('hinge_loss', r'''
w = [1.0, 1.0]
b = -5.0
points = [([1, 1], -1), ([2, 2], -1), ([2, 3], -1), ([3, 3], 1), ([4, 4], 1), ([2, 2], 1)]
total = 0.0
for x, label in points:
    score = w[0] * x[0] + w[1] * x[1] + b
    loss = max(0.0, 1 - label * score)
    total = total + loss
    print("x", x, " label", str(label).rjust(2), " score", str(score).rjust(4), " hinge loss", loss)
print("total hinge loss:", total)
''')

K.code('c_tradeoff', r'''
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

X, y = make_blobs(n_samples=300, centers=2, cluster_std=2.2, random_state=4)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
for C in [0.001, 0.01, 0.1, 1, 100]:
    model = SVC(kernel="linear", C=C).fit(X_train, y_train)
    width = 2 / np.linalg.norm(model.coef_[0])
    print("C", str(C).rjust(5), " margin", str(round(float(width), 2)).rjust(5), " support vectors", str(len(model.support_)).rjust(3),
          " train", round(model.score(X_train, y_train), 3), " test", round(model.score(X_test, y_test), 3))
''')

K.code('kernel_trick', r'''
import numpy as np
from sklearn.datasets import make_circles
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC

X, y = make_circles(n_samples=300, noise=0.1, factor=0.4, random_state=0)
for kernel in ["linear", "poly", "rbf"]:
    model = SVC(kernel=kernel, degree=2)
    print(kernel.ljust(6), "accuracy", round(cross_val_score(model, X, y, cv=5).mean(), 3))

# the same idea by hand: add the feature x1^2 + x2^2, then a straight line works
X_lifted = np.column_stack([X, X[:, 0] ** 2 + X[:, 1] ** 2])
print("linear on lifted data", round(cross_val_score(SVC(kernel="linear"), X_lifted, y, cv=5).mean(), 3))
''')

K.code('gamma_effect', r'''
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

X, y = make_moons(n_samples=300, noise=0.3, random_state=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
for gamma in [0.01, 0.1, 1, 10, 100]:
    model = SVC(kernel="rbf", C=1, gamma=gamma).fit(X_train, y_train)
    print("gamma", str(gamma).rjust(5), " train", round(model.score(X_train, y_train), 3),
          " test", round(model.score(X_test, y_test), 3), " support vectors", len(model.support_))
''')

K.code('scaling_matters', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
print("feature maximums go from", round(float(X.max(axis=0).min()), 3), "to", round(float(X.max(axis=0).max()), 1))
raw = cross_val_score(SVC(kernel="rbf"), X, y, cv=5).mean()
scaled = cross_val_score(make_pipeline(StandardScaler(), SVC(kernel="rbf")), X, y, cv=5).mean()
print("without scaling:", round(raw, 3))
print("with StandardScaler:", round(scaled, 3))
''')

K.code('grid_search', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
pipe = make_pipeline(StandardScaler(), SVC(kernel="rbf"))
grid = {"svc__C": [0.1, 1, 10, 100], "svc__gamma": [0.001, 0.01, 0.1, 1]}
search = GridSearchCV(pipe, grid, cv=5).fit(X_train, y_train)
print("best settings:", search.best_params_)
print("cross validated accuracy:", round(search.best_score_, 3))
print("test accuracy:", round(search.score(X_test, y_test), 3))
''')

K.code('pegasos', r'''
import numpy as np

rng = np.random.default_rng(0)
X = np.vstack([rng.normal([1, 1], 0.6, (40, 2)), rng.normal([3, 3], 0.6, (40, 2))])
y = np.array([-1] * 40 + [1] * 40)

w = np.zeros(2)
b = 0.0
lam = 0.01
for epoch in range(1, 31):
    lr = 0.1 / epoch
    for i in rng.permutation(len(X)):
        if y[i] * (X[i] @ w + b) < 1:          # inside the margin or wrong: push
            w = w - lr * (lam * w - y[i] * X[i])
            b = b + lr * y[i]
        else:                                  # safely outside: only shrink w
            w = w - lr * lam * w
    if epoch in (1, 10, 30):
        hinge = np.maximum(0, 1 - y * (X @ w + b)).mean()
        acc = np.mean(np.sign(X @ w + b) == y)
        print("epoch", str(epoch).rjust(2), " mean hinge loss", round(float(hinge), 3), " accuracy", round(float(acc), 3))
print("w =", np.round(w, 3).tolist(), " b =", round(float(b), 3))
''', long=True)

K.code('svr_tube', r'''
import numpy as np
from sklearn.svm import SVR

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 6, 60)).reshape(-1, 1)
y = np.sin(x).ravel() + rng.normal(0, 0.1, 60)
for eps in [0.01, 0.1, 0.3]:
    model = SVR(kernel="rbf", C=10, epsilon=eps).fit(x, y)
    err = np.abs(model.predict(x) - y).mean()
    print("epsilon", str(eps).ljust(4), " support vectors", str(len(model.support_)).rjust(2), " mean error", round(float(err), 3))
''')

K.lesson('idea', 'The widest street', f'''
{src('Cortes and Vapnik (1995), Hastie, Tibshirani and Friedman, The Elements of Statistical Learning chapter 12, Bishop, Pattern Recognition and Machine Learning chapter 7, the Stanford CS229 SVM notes, Pegasos (2007), Platt (1998), and the scikit-learn 1.8 user guide section 1.4.')}
{viz('mlsvm')}
{wwh('A <b>support vector machine</b> (SVM) is a classifier that draws the boundary with the <b>widest margin</b>: the widest empty street between the two classes. The training points on the edges of the street are the <b>support vectors</b>.',
     'When many lines separate the training data, logistic regression and the perceptron just pick one of them. The SVM picks the one that stays furthest from both classes, which tends to classify new points better. Only a few points decide the boundary, so the model is compact, and with kernels it can draw curved boundaries too.',
     'Write the boundary as w&middot;x + b = 0 and scale w so the street edges are w&middot;x + b = +1 and &minus;1. The width of the street is then 2 / |w|. Training finds the smallest |w| for which every point is on the correct side of its edge.')}
{run('margin_by_hand')}
{note('Three of the six points have w&middot;x + b equal to exactly +1 or &minus;1: those are the support vectors. The other three are further away (&plusmn;1.4) and could move freely without changing the line.', 'tip')}
{fxs(fx('Decision rule', 'ŷ = sign(w&middot;x + b)', 'Which side of the line the point is on.', key=True),
     fx('Margin width', 'width = 2 / |w|', 'A smaller |w| means a wider street.', key=True))}
{scene('a road between two villages', '<p>Engineers must build a straight road between two villages and want it as wide as possible without knocking down any house. The houses closest to the road on each side fix where its edges go. Houses further back do not matter at all. Those closest houses are the support vectors.</p>')}
''', kw=['support vector machine', 'SVM', 'maximum margin', 'margin width', 'support vectors', 'hyperplane', 'linear classifier'])

K.lesson('soft', 'Soft margin, hinge loss and C', f'''
{wwh('Real data overlaps, so no street is perfectly empty. The <b>soft margin</b> SVM lets some points sit inside the street or on the wrong side, and charges each one a <b>hinge loss</b>. The setting <b>C</b> says how much each violation costs.',
     'Without the soft margin, one mislabelled point could make the problem impossible or force a tiny street. C lets you trade a wide, simple street (small C) against getting more training points right (large C), the same bias and variance trade off as in regularisation.',
     'The hinge loss of a point is max(0, 1 &minus; y(w&middot;x + b)): zero when the point is on its side beyond the edge, growing linearly once it enters the street. Training minimises &frac12;|w|<sup>2</sup> + C &times; (sum of hinge losses).')}
{run('hinge_loss')}
{run('c_tradeoff')}
{note('As C grows the street shrinks from 8.73 to 3.43 and the number of support vectors drops from 162 to 83, because fewer points are allowed inside the street. Test accuracy improves a little and then stops changing. Small C means strong regularisation. Note that C works the opposite way to the ridge penalty &lambda;: C is roughly 1 / &lambda;.', 'exam')}
{fx('Soft margin objective', 'min<sub>w,b</sub> &frac12;|w|<sup>2</sup> + C &Sigma;<sub>i</sub> max(0, 1 &minus; y<sub>i</sub>(w&middot;x<sub>i</sub> + b))', 'Wide street plus a hinge penalty for every violation.', key=True)}
''', kw=['soft margin', 'hinge loss', 'C parameter', 'slack variables', 'regularisation', 'margin violation'])

K.lesson('kernel', 'Kernels: curved boundaries', f'''
{viz('mlkernel')}
{wwh('A <b>kernel</b> is a function K(x, z) that measures how similar two points are. Swapping the plain dot product for a kernel lets the SVM draw curved boundaries, as if it had added many new features, without ever building them.',
     'Many datasets, like a ring of one class around another, cannot be split by any straight line. Adding features such as x<sup>2</sup> makes them separable, but building thousands of such features by hand is slow. The kernel trick gets the same result at the cost of computing K for pairs of points.',
     'The SVM solution only uses the data through dot products x<sub>i</sub>&middot;x<sub>j</sub>. Replace each one with K(x<sub>i</sub>, x<sub>j</sub>). In scikit-learn, choose SVC(kernel="rbf"), "poly" or "linear".')}
{run('kernel_trick')}
{note('The linear SVM is no better than guessing on the two rings (0.557). The degree 2 polynomial kernel scores 1.0 because (x&middot;z)<sup>2</sup> contains the features x<sub>1</sub><sup>2</sup> and x<sub>2</sub><sup>2</sup>, which is exactly what describes a circle. Adding x<sub>1</sub><sup>2</sup> + x<sub>2</sub><sup>2</sup> by hand and using a linear SVM also scores 1.0.', 'tip')}
{table(['Kernel', 'K(x, z)', 'Boundary', 'Settings'], [
    ['Linear', 'x&middot;z', 'Straight line or flat plane', 'C'],
    ['Polynomial', '(&gamma; x&middot;z + r)<sup>d</sup>', 'Curves of degree d', 'C, degree d, &gamma;, r (coef0)'],
    ['RBF (Gaussian)', 'exp(&minus;&gamma;|x &minus; z|<sup>2</sup>)', 'Any smooth shape', 'C, &gamma;'],
    ['Sigmoid', 'tanh(&gamma; x&middot;z + r)', 'Like a small neural network, not always valid', 'C, &gamma;, r']])}
''', kw=['kernel trick', 'RBF kernel', 'polynomial kernel', 'feature map', 'nonlinear SVM', 'Gram matrix'])

K.lesson('tune', 'Tuning C and gamma, and scaling', f'''
{wwh('An RBF SVM has two knobs. <b>C</b> controls how hard it tries to get every training point right. <b>&gamma;</b> (gamma) controls how far the influence of one training point reaches: large &gamma; means a short reach and a wiggly boundary.',
     'With bad settings the same model ranges from badly underfitting to badly overfitting. SVMs also measure distances, so a feature in thousands drowns a feature in fractions unless you scale them first.',
     'Always put a StandardScaler in a pipeline before the SVM. Then search C and &gamma; on a log scale (0.001, 0.01, 0.1, 1, 10, 100) with cross validation, using GridSearchCV.')}
{run('gamma_effect')}
{note('Small &gamma; (0.01) gives a nearly straight boundary. &gamma; = 1 is best here (test 0.917). At &gamma; = 100 every point gets its own little bubble: training accuracy 0.983 but test only 0.775, classic overfitting, and the number of support vectors jumps to 170.', 'tip')}
{run('scaling_matters')}
{run('grid_search')}
{note('Scaling alone lifts accuracy from 0.912 to 0.974. The grid search picks C = 100 with &gamma; = 0.001: a wide reach with a high penalty. Both knobs interact, so search them together, never one at a time.', 'exam')}
''', kw=['gamma', 'C', 'RBF SVM tuning', 'GridSearchCV', 'feature scaling', 'StandardScaler', 'overfitting'])

K.lesson('train', 'How an SVM is trained', f'''
{wwh('The SVM objective is <b>convex</b>, so it has one best answer and no bad local minima. Libraries solve it either in the <b>dual</b> form (libsvm, used by SVC) or directly in the <b>primal</b> form with gradient style methods (liblinear, SGD, Pegasos).',
     'Knowing how training works explains the practical rules: SVC gets slow beyond tens of thousands of rows because the dual works with every pair of points, while LinearSVC and SGDClassifier scale to millions of rows but only draw straight boundaries.',
     'Pegasos, below, is stochastic subgradient descent on the soft margin objective: for each point inside the street, step w towards y x, and always shrink w a little. That is all a linear SVM needs.')}
{run('pegasos')}
{note('Twenty lines of NumPy reach 97.5% accuracy, and the mean hinge loss falls from 0.257 to 0.086 over 30 passes. The learned w = (0.86, 0.87) points from class &minus;1 towards class +1, as expected.', 'tip')}
{deep('The dual problem and SMO', '<p>With Lagrange multipliers &alpha;<sub>i</sub> &ge; 0 the soft margin problem becomes: maximise &Sigma;&alpha;<sub>i</sub> &minus; &frac12;&Sigma;<sub>i,j</sub> &alpha;<sub>i</sub>&alpha;<sub>j</sub>y<sub>i</sub>y<sub>j</sub> x<sub>i</sub>&middot;x<sub>j</sub> subject to 0 &le; &alpha;<sub>i</sub> &le; C and &Sigma;&alpha;<sub>i</sub>y<sub>i</sub> = 0. Then w = &Sigma;&alpha;<sub>i</sub>y<sub>i</sub>x<sub>i</sub>. Only support vectors have &alpha;<sub>i</sub> &gt; 0, and the data appears only through dot products, which is why the kernel trick works. Platt’s SMO algorithm (1998) solves the dual by updating two &alpha; values at a time, each update in closed form. libsvm, behind scikit-learn’s SVC, uses an improved SMO, and its time grows between n<sup>2</sup> and n<sup>3</sup> in the number of rows.</p>')}
''', kw=['convex optimisation', 'dual problem', 'Lagrange multipliers', 'SMO', 'Pegasos', 'subgradient descent', 'LinearSVC', 'libsvm'])

K.lesson('svr', 'Support vector regression', f'''
{wwh('<b>Support vector regression</b> (SVR) predicts numbers. It fits a tube of half width &epsilon; (epsilon) around the curve and ignores every error smaller than &epsilon;. Only points on or outside the tube become support vectors.',
     'Ignoring small errors makes SVR robust to noise and gives a compact model. With an RBF kernel it fits smooth curves.',
     'The loss is max(0, |y &minus; f(x)| &minus; &epsilon;), the epsilon insensitive loss. A bigger &epsilon; means a wider tube, fewer support vectors and a rougher fit.')}
{run('svr_tube')}
{note('With &epsilon; = 0.01 nearly every point (57 of 60) is a support vector. With &epsilon; = 0.3 only 5 are, and the mean error rises from 0.077 to 0.12. Pick &epsilon; close to the noise level you are willing to ignore.', 'tip')}
{fx('Epsilon insensitive loss', 'L = max(0, |y &minus; f(x)| &minus; &epsilon;)', 'Errors inside the tube cost nothing.', key=True)}
''', kw=['SVR', 'support vector regression', 'epsilon tube', 'epsilon insensitive loss', 'regression with kernels'])

K.lesson('versus', 'SVMs compared', f'''
{versus('Three linear and nonlinear classifiers side by side', ['', 'SVM', 'Logistic regression', 'KNN'], [
    ['Loss', 'Hinge (zero beyond the margin)', 'Log loss (never exactly zero)', 'None'],
    ['Which points matter', 'Only support vectors', 'All points, a little each', 'The k nearest at prediction time'],
    ['Probabilities', 'Not built in (Platt scaling adds them)', 'Built in and well calibrated', 'Share of votes'],
    ['Curved boundaries', 'Kernels', 'Only with added features', 'Naturally'],
    ['Large data (millions of rows)', 'Only the linear version', 'Yes', 'Slow at prediction'],
    ['Needs scaling', 'Yes', 'Yes with a penalty', 'Yes']],
    'an RBF SVM is a strong choice for small and medium tabular data. For very large data use a linear model or gradient boosting.')}
{note('SVC(probability=True) fits an extra logistic curve to the SVM scores with internal cross validation (Platt scaling). It is slower and its probabilities can disagree with predict. Use decision_function for ranking.', 'exam')}
''', kw=['SVM vs logistic regression', 'SVM vs KNN', 'hinge vs log loss', 'Platt scaling', 'decision_function'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Hard margin primal', 'min &frac12;|w|<sup>2</sup> subject to y<sub>i</sub>(w&middot;x<sub>i</sub> + b) &ge; 1', 'Widest street with every point outside it.', key=True),
     fx('Soft margin primal', 'min &frac12;|w|<sup>2</sup> + C&Sigma;&xi;<sub>i</sub>, y<sub>i</sub>(w&middot;x<sub>i</sub> + b) &ge; 1 &minus; &xi;<sub>i</sub>, &xi;<sub>i</sub> &ge; 0', 'Slack &xi; is the hinge loss.', key=True),
     fx('Dual', 'max &Sigma;&alpha;<sub>i</sub> &minus; &frac12;&Sigma;&alpha;<sub>i</sub>&alpha;<sub>j</sub>y<sub>i</sub>y<sub>j</sub>K(x<sub>i</sub>, x<sub>j</sub>), 0 &le; &alpha;<sub>i</sub> &le; C, &Sigma;&alpha;<sub>i</sub>y<sub>i</sub> = 0', 'Only dot products appear.'),
     fx('Kernel prediction', 'f(x) = &Sigma;<sub>i&isin;SV</sub> &alpha;<sub>i</sub>y<sub>i</sub>K(x<sub>i</sub>, x) + b', 'A weighted vote of the support vectors.', key=True),
     fx('RBF kernel', 'K(x, z) = exp(&minus;&gamma;|x &minus; z|<sup>2</sup>)', '1 for identical points, near 0 for far ones.', key=True))}
{steps('Worked example: why the width is 2 / |w|', [
    'Take a point x<sub>+</sub> on the edge w&middot;x + b = +1 and walk straight across the street to x<sub>&minus;</sub> on the edge w&middot;x + b = &minus;1.',
    'Walking straight across means moving along the unit normal w / |w|: x<sub>+</sub> = x<sub>&minus;</sub> + m &times; w / |w|, where m is the width.',
    'Put it into the edge equation: w&middot;x<sub>&minus;</sub> + m |w| + b = 1, and w&middot;x<sub>&minus;</sub> + b = &minus;1.',
    eq('&minus;1 + m|w| = 1, so m = 2 / |w|'),
    'For the program’s data, w = (0.4, 0.4), |w| = 0.566, width = 3.536, as printed.'])}
{deep('Why the hinge loss is a good stand in', '<p>The loss we really care about is the 0 or 1 error, which is flat almost everywhere and impossible to optimise directly. The hinge loss max(0, 1 &minus; yf) is the tightest convex upper bound on it that also asks for a margin. Logistic regression uses log(1 + e<sup>&minus;yf</sup>), another convex bound that never reaches zero, which is why every point influences it. Both are consistent: with enough data and a rich enough model, minimising either gives the Bayes optimal classifier (Bartlett, Jordan and McAuliffe, 2006).</p>')}
''', kw=['primal', 'dual', 'slack variables', 'kernel prediction', 'RBF formula', 'margin derivation', 'hinge loss surrogate'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>An SVM draws the line that leaves the widest gap between two classes. The points closest to the line, the support vectors, decide where it goes.</p>',
    '<p>Use SVC in a pipeline with StandardScaler, tune C and gamma with GridSearchCV, choose between linear and RBF kernels, and use SVR for numbers.</p>',
    '<p>Derive the margin, write the primal and dual problems, explain the kernel trick and the hinge loss, and know when to use LinearSVC or SGDClassifier for big data.</p>',
    '<p>Study Mercer’s theorem and reproducing kernel Hilbert spaces, the representer theorem, VC dimension and margin based generalisation bounds, multiple kernel learning, and random Fourier features (Rahimi and Recht, 2007) that approximate the RBF kernel for large data.</p>')}
{grow('Find the widest street and its support vectors.',
      'Train, scale and tune kernel SVMs for real data.',
      'Analyse the dual, kernels and generalisation bounds.')}
''', kw=['beginner', 'expert', 'Mercer theorem', 'RKHS', 'representer theorem', 'random Fourier features'])

lc(164, 'Maximum Gap', 'maximum-gap', 'm', 'Sort, then find the widest gap', 'The widest gap between neighbouring values appears only after sorting. Sort, then compare each pair of neighbours. An SVM in one dimension puts its boundary in the middle of exactly such a gap.', r'''
def maximum_gap(nums):
    if len(nums) < 2:
        return 0
    s = sorted(nums)
    best = 0
    for i in range(1, len(s)):
        best = max(best, s[i] - s[i - 1])
    return best
''', [('maximum_gap([3, 6, 9, 1])', 3), ('maximum_gap([10])', 0)])
lc(2078, 'Two Furthest Houses With Different Colors', 'two-furthest-houses-with-different-colors', 'e', 'The answer uses an end', 'The furthest pair with different colours always includes the first or the last house. Scan from each end for the furthest house with a different colour.', r'''
def max_distance(colors):
    n = len(colors)
    best = 0
    for j in range(n):
        if colors[j] != colors[0]:
            best = max(best, j)
        if colors[j] != colors[n - 1]:
            best = max(best, n - 1 - j)
    return best
''', [('max_distance([1, 1, 1, 6, 1, 1, 1])', 3), ('max_distance([1, 8, 3, 8, 3])', 4)])
lc(836, 'Rectangle Overlap', 'rectangle-overlap', 'e', 'Separated on one axis means no overlap', 'Two boxes do not overlap exactly when one is completely to the left, right, above or below the other. That is the separating axis idea: if a straight line splits them, they are separable.', r'''
def is_rectangle_overlap(rec1, rec2):
    left = rec1[2] <= rec2[0]
    right = rec2[2] <= rec1[0]
    below = rec1[3] <= rec2[1]
    above = rec2[3] <= rec1[1]
    return not (left or right or below or above)
''', [('is_rectangle_overlap([0, 0, 2, 2], [1, 1, 3, 3])', True), ('is_rectangle_overlap([0, 0, 1, 1], [1, 0, 2, 1])', False)])
lc(593, 'Valid Square', 'valid-square', 'm', 'Count squared distances', 'Compute the 6 squared distances between the 4 points. A square has exactly two different values, 4 equal sides and 2 equal diagonals, and none of them is zero. Squared distances are what the RBF kernel uses.', r'''
def valid_square(p1, p2, p3, p4):
    pts = [p1, p2, p3, p4]
    d = []
    for i in range(4):
        for j in range(i + 1, 4):
            d.append((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2)
    d.sort()
    return d[0] > 0 and d[0] == d[3] and d[4] == d[5] and d[4] == 2 * d[0]
''', [('valid_square([0, 0], [1, 1], [1, 0], [0, 1])', True), ('valid_square([0, 0], [1, 1], [1, 0], [0, 12])', False)])
lc(2249, 'Count Lattice Points Inside a Circle', 'count-lattice-points-inside-a-circle', 'm', 'Check each grid point against each circle', 'Look at every integer point in the box that holds all circles. A point counts when its squared distance to some centre is at most r squared. A circle boundary is what the x squared feature lets a linear SVM draw.', r'''
def count_lattice_points(circles):
    hits = set()
    for x0, y0, r in circles:
        for x in range(x0 - r, x0 + r + 1):
            for y in range(y0 - r, y0 + r + 1):
                if (x - x0) ** 2 + (y - y0) ** 2 <= r * r:
                    hits.add((x, y))
    return len(hits)
''', [('count_lattice_points([[2, 2, 1]])', 5), ('count_lattice_points([[2, 2, 2], [3, 4, 1]])', 16)])
lc(812, 'Largest Triangle Area', 'largest-triangle-area', 'e', 'Try every triple with the cross product', 'Try every choice of three points and compute the area with the cross product formula, half the absolute value of (x2 &minus; x1)(y3 &minus; y1) &minus; (x3 &minus; x1)(y2 &minus; y1). The sign of the same cross product tells which side of a line a point lies on, the core test of any linear classifier.', r'''
def largest_triangle_area(points):
    best = 0.0
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                (x1, y1), (x2, y2), (x3, y3) = points[i], points[j], points[k]
                area = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2
                best = max(best, area)
    return best
''', [('largest_triangle_area([[0, 0], [0, 1], [1, 0], [0, 2], [2, 0]])', 2.0), ('largest_triangle_area([[1, 0], [0, 0], [0, 1]])', 0.5)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>SVMs are about gaps, distances and which side of a line a point is on. These problems practise exactly that: the widest gap between sorted values, the furthest pair of different classes, separating boxes, squared distances, points inside circles, and the cross product side test. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'geometry', 'maximum gap', 'cross product', 'squared distance'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An <b>SVM</b> picks the boundary with the <b>widest margin</b>. Width = 2 / |w|, so it minimises |w|.',
    'Only the <b>support vectors</b>, the points on or inside the margin, decide the boundary.',
    'The <b>soft margin</b> allows violations with the <b>hinge loss</b> max(0, 1 &minus; y f(x)). Small C means a wider street and more regularisation.',
    'The <b>kernel trick</b> replaces dot products with K(x, z) to draw curved boundaries. RBF is the default kernel.',
    'Tune C and &gamma; together on a log grid, and always scale the features first.',
    'SVC (libsvm) suits up to tens of thousands of rows. Use LinearSVC or SGDClassifier for more.',
    'SVR fits an &epsilon; tube and ignores small errors.'],
    'Supervised 3.1 starts the trees family: decision trees that ask yes or no questions about the features.')}
{files('Three tasks: a hinge loss, a margin width, and an RBF kernel value.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'An SVM chooses the boundary that', ['Passes through the most points', 'Leaves the widest margin between the classes', 'Has the most parameters', 'Minimises squared error'], 1, 'The street.', 'It maximises the margin.')
K.quiz('e', 'Support vectors are', ['All training points', 'The points on or inside the margin', 'The misclassified test points', 'The cluster centres'], 1, 'They touch the street.', 'Only they get &alpha; &gt; 0 and decide the boundary.')
K.quiz('e', 'Which kernel gives a straight boundary?', ['RBF', 'Polynomial of degree 3', 'Linear', 'Sigmoid'], 2, 'Plain dot product.', 'The linear kernel is x&middot;z.')
K.quiz('e', 'Before an RBF SVM you should', ['Shuffle the columns', 'Scale the features', 'Remove the labels', 'Square the target'], 1, 'Distances.', 'Unscaled large features dominate the distance.')
K.quiz('m', 'A smaller C in a soft margin SVM gives', ['A narrower margin and fewer violations', 'A wider margin and more violations allowed', 'No change', 'A nonlinear boundary'], 1, 'C is the price of a violation.', 'Cheap violations let the street widen. Small C means strong regularisation.')
K.quiz('m', 'The hinge loss of a correctly classified point beyond the margin is', ['1', '0', 'Negative', 'Its distance'], 1, 'max(0, 1 &minus; yf) with yf &ge; 1.', 'It contributes nothing.')
K.quiz('m', 'A very large &gamma; in an RBF SVM tends to', ['Underfit', 'Overfit with bubbles around points', 'Make the boundary straight', 'Speed up training a lot'], 1, 'Short reach.', 'Each point only influences a tiny area.')
K.quiz('m', 'The kernel trick works because the SVM solution uses the data only through', ['Labels', 'Dot products between points', 'Means', 'Gradients of the labels'], 1, 'Look at the dual.', 'Replace x<sub>i</sub>&middot;x<sub>j</sub> with K(x<sub>i</sub>, x<sub>j</sub>).')
K.quiz('m', 'Removing a training point that is not a support vector and retraining', ['Changes the boundary a lot', 'Leaves the boundary unchanged', 'Makes training impossible', 'Doubles the margin'], 1, 'Only support vectors matter.', 'Its &alpha; was 0, so it had no effect.')
K.quiz('h', 'For one million rows and many features, the practical SVM choice is', ['SVC with an RBF kernel', 'LinearSVC or SGDClassifier with hinge loss', 'SVC with a degree 10 polynomial', 'KNN'], 1, 'libsvm grows between n<sup>2</sup> and n<sup>3</sup>.', 'Linear solvers scale roughly linearly in n.')
K.quiz('h', 'In the dual, a point with 0 &lt; &alpha;<sub>i</sub> &lt; C lies', ['Far outside the margin', 'Exactly on the margin edge', 'On the wrong side always', 'At the centre'], 1, 'KKT conditions.', '&alpha; = 0 outside, 0 &lt; &alpha; &lt; C on the edge, &alpha; = C inside or wrong.')
K.quiz('h', 'Compared with logistic regression, the SVM', ['Gives calibrated probabilities directly', 'Ignores points beyond the margin', 'Cannot be regularised', 'Only works in 2D'], 1, 'Hinge is zero there.', 'Log loss is never exactly zero, so every point counts a little.')
K.quiz('x', 'In the style of a Stanford CS229 exam: the hard margin SVM is infeasible when', ['There are more features than rows', 'The training data is not linearly separable in the feature space', 'C is too big', 'The kernel is RBF'], 1, 'Constraints y(w&middot;x + b) &ge; 1 for all points.', 'No w satisfies them all, so the soft margin is needed.')
K.quiz('x', 'In the style of an MIT 6.867 exam: the RBF kernel corresponds to a feature space of dimension', ['2', 'Equal to the number of features', 'Infinite', 'Equal to the number of classes'], 2, 'Expand exp as a series.', 'The Taylor series of exp gives monomials of every degree.')

K.calc('e', 'w = (3, 4). Margin width 2 / |w|?', '0.4', '|w| = 5.', ['|w| = &radic;(9 + 16).', '= 5.', eq('2 / 5 = 0.4')], check=0.4)
K.calc('e', 'w = (1, 1), b = &minus;3, point (2, 2). Score w&middot;x + b?', '1', 'Dot product plus b.', ['1&times;2 + 1&times;2 = 4.', 'Add b = &minus;3.', eq('4 &minus; 3 = 1')], check=1)
K.calc('e', 'Label y = +1, score 0.3. Hinge loss?', '0.7', 'max(0, 1 &minus; yf).', ['yf = 0.3.', '1 &minus; 0.3 = 0.7.', eq('max(0, 0.7) = 0.7')], check=0.7)
K.calc('m', 'Label y = &minus;1, score 0.5. Hinge loss?', '1.5', 'Wrong side.', ['yf = &minus;0.5.', '1 &minus; (&minus;0.5) = 1.5.', eq('max(0, 1.5) = 1.5')], check=1.5)
K.calc('m', 'Label y = +1, score 2. Hinge loss?', '0', 'Beyond the margin.', ['yf = 2.', '1 &minus; 2 = &minus;1.', eq('max(0, &minus;1) = 0')], check=0)
K.calc('m', 'RBF kernel, &gamma; = 0.5, x = (0, 0), z = (1, 1). K, 3 decimals?', '0.368', 'exp(&minus;&gamma;|x &minus; z|<sup>2</sup>).', ['|x &minus; z|<sup>2</sup> = 1 + 1 = 2.', '&minus;0.5 &times; 2 = &minus;1.', eq('e<sup>&minus;1</sup> = 0.368')], check=0.368)
K.calc('m', 'Polynomial kernel (x&middot;z + 1)<sup>2</sup> with x = (1, 2), z = (3, 1)?', '36', 'Dot product first.', ['x&middot;z = 3 + 2 = 5.', 'Add 1 to get 6.', eq('6<sup>2</sup> = 36')], check=36)
K.calc('h', 'Soft margin objective with w = (1, 1), C = 1, hinge losses adding to 0.5?', '1.5', '&frac12;|w|<sup>2</sup> + C&Sigma;.', ['|w|<sup>2</sup> = 2, half is 1.', 'C &times; 0.5 = 0.5.', eq('1 + 0.5 = 1.5')], check=1.5)
K.calc('h', 'How many distinct degree 2 products x<sub>i</sub>x<sub>j</sub> (i &le; j) do 10 features make?', '55', 'Pairs with repetition.', ['Squares: 10.', 'Cross products: 10 &times; 9 / 2 = 45.', eq('10 + 45 = 55')], check=55)
K.calc('x', 'In the style of a CMU 10-701 problem: two support vectors with &alpha; = 0.5, labels +1 and &minus;1, kernel values with x of 0.8 and 0.2, b = 0.1. f(x)?', '0.4', '&Sigma;&alpha;yK + b.', ['0.5 &times; 1 &times; 0.8 = 0.4.', '0.5 &times; (&minus;1) &times; 0.2 = &minus;0.1.', eq('0.4 &minus; 0.1 + 0.1 = 0.4')], check=0.4)

K.assign('hinge', 'e', 'Hinge loss',
         '<p>Write <code>hinge(y, score)</code> where y is +1 or &minus;1. Return max(0, 1 &minus; y &times; score), rounded to 4 decimals.</p>',
         '''
def hinge(y, score):
    # your code here
    pass
''', [('hinge(1, 0.3)', 0.7), ('hinge(-1, 0.5)', 1.5), ('hinge(1, 2)', 0.0)],
         '''
def hinge(y, score):
    return round(max(0.0, 1 - y * score), 4)
''', 'One line with max.', '<p>Zero for points safely on their side, growing linearly as they enter the street or cross it.</p>')
K.assign('margin', 'm', 'Margin width from w',
         '<p>Write <code>margin_width(w)</code> where w is a list of numbers. Return 2 / |w|, rounded to 4 decimals, where |w| is the square root of the sum of squares.</p>',
         '''
import math


def margin_width(w):
    # your code here
    pass
''', [('margin_width([3, 4])', 0.4), ('margin_width([0.4, 0.4])', 3.5355), ('margin_width([1, 0, 0])', 2.0)],
         '''
import math


def margin_width(w):
    norm = math.sqrt(sum(v * v for v in w))
    return round(2 / norm, 4)
''', 'Compute the length of w, then divide 2 by it.', '<p>The second test is the program’s answer, 3.536 rounded to 4 decimals.</p>')
K.assign('rbf', 'm', 'RBF kernel value',
         '<p>Write <code>rbf(x, z, gamma)</code> that returns exp(&minus;gamma &times; |x &minus; z|<sup>2</sup>) for two lists of the same length, rounded to 4 decimals.</p>',
         '''
import math


def rbf(x, z, gamma):
    # your code here
    pass
''', [('rbf([0, 0], [1, 1], 0.5)', 0.3679), ('rbf([1, 2], [1, 2], 3)', 1.0), ('rbf([0], [3], 0.1)', 0.4066)],
         '''
import math


def rbf(x, z, gamma):
    sq = 0.0
    for a, b in zip(x, z):
        sq = sq + (a - b) ** 2
    return round(math.exp(-gamma * sq), 4)
''', 'Add up the squared differences, multiply by &minus;gamma and take exp.', '<p>Identical points give 1. The value falls towards 0 as the points move apart, faster for a larger gamma.</p>')

K.must('Margin', 'Boundary w&middot;x + b = 0, edges &plusmn;1, width 2/|w|. Hard margin: min &frac12;|w|<sup>2</sup> with y(w&middot;x + b) &ge; 1.')
K.must('Soft margin', 'min &frac12;|w|<sup>2</sup> + C&Sigma;max(0, 1 &minus; y f(x)). Small C: wide street, strong regularisation.')
K.must('Support vectors', 'Points on or inside the margin (&alpha; &gt; 0). Others can move without changing the model.')
K.must('Kernels', 'Linear x&middot;z, poly (&gamma;x&middot;z + r)<sup>d</sup>, RBF exp(&minus;&gamma;|x &minus; z|<sup>2</sup>). Kernel trick: dot products only.')
K.must('Practice', 'Scale first. Grid search C and &gamma; on a log scale. Big &gamma; overfits. SVC up to about 10<sup>4</sup> to 10<sup>5</sup> rows, else LinearSVC or SGD.')
K.must('Extras', 'SVR uses an &epsilon; tube. No built in probabilities (Platt scaling). Dual solved by SMO in libsvm.')

T = K.topic(
    slug='ml-svm', topic='ml-svm', step=(2, 'Classification', 'ml-s2', 'Predict categories: yes or no, spam or not, or which of many classes, with four very different families of models.', 'Intermediate'),
    title='Support vector machines: the widest street', short='SVM', badge='2.4', minutes=55,
    lead='Learn the maximum margin classifier: support vectors, the soft margin and hinge loss, the kernel trick for curved boundaries, tuning C and gamma, how SVMs are trained, and support vector regression.',
    desc='support vector machine, SVM, maximum margin, support vectors, hinge loss, soft margin, C, kernel trick, RBF kernel, polynomial kernel, gamma, feature scaling, GridSearchCV, dual problem, SMO, Pegasos, LinearSVC, SVR, epsilon tube, Platt scaling.',
    summary='The widest margin classifier, soft margins and hinge loss, kernels, tuning C and gamma, training, and SVR.',
    keywords=['SVM', 'support vector machine', 'maximum margin', 'hinge loss', 'kernel trick', 'RBF kernel', 'C and gamma', 'SVR', 'support vectors', 'SVC'],
    recap='<p>An SVM leaves the widest street between the classes. Kernels bend the street, C and gamma control how closely it follows the data.</p>',
    added='2026-11-13', leet=leet_items())
