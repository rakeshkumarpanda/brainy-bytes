# Unsupervised 1.3: Gaussian mixture models and the EM algorithm. Checked against Dempster, Laird and Rubin, Maximum
# Likelihood from Incomplete Data via the EM Algorithm (JRSS B 1977), Bishop, Pattern Recognition and Machine Learning
# chapter 9, The Elements of Statistical Learning section 8.5, Murphy, Probabilistic Machine Learning section 8.7,
# Schwarz, Estimating the Dimension of a Model (1978), the Stanford CS229 notes on EM, and the scikit-learn 1.8 user
# guide section 2.1.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-gmm')
K = Kit()

K.code('em_by_hand', r'''
import numpy as np

# Heights of ten people (cm): a mix of two groups, but nobody tells us who is in which
x = np.array([150.0, 152, 155, 157, 160, 170, 174, 176, 179, 182])
mu = np.array([155.0, 165.0])        # first guesses for the two means
sd = np.array([10.0, 10.0])
w = np.array([0.5, 0.5])             # mixing weights

def normal(v, m, s):
    return np.exp(-0.5 * ((v - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))

for it in range(1, 11):
    dens = w * normal(x[:, None], mu, sd)              # 10 x 2 table: weight times density
    loglik = np.log(dens.sum(axis=1)).sum()
    r = dens / dens.sum(axis=1, keepdims=True)         # E step: responsibilities
    nk = r.sum(axis=0)                                 # M step: effective counts
    w = nk / len(x)
    mu = (r * x[:, None]).sum(axis=0) / nk
    sd = np.sqrt((r * (x[:, None] - mu) ** 2).sum(axis=0) / nk)
    print("round", it, " log likelihood", round(float(loglik), 3), " means", np.round(mu, 1).tolist(),
          " sds", np.round(sd, 1).tolist(), " weights", np.round(w, 2).tolist())
print("chance that 165 cm belongs to group 2:", round(float((w * normal(165, mu, sd))[1] / (w * normal(165, mu, sd)).sum()), 3))
''', long=True)

K.code('sklearn_gmm', r'''
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score

rng = np.random.default_rng(0)
a = rng.multivariate_normal([0, 0], [[6, 0], [0, 0.3]], size=200)     # long, flat cluster
b = rng.multivariate_normal([0, 2.5], [[6, 0], [0, 0.3]], size=200)   # another one just above it
X, y = np.vstack([a, b]), np.repeat([0, 1], 200)

km = KMeans(n_clusters=2, n_init=10, random_state=0).fit(X)
one = GaussianMixture(n_components=2, covariance_type="full", n_init=1, random_state=0).fit(X)
gm = GaussianMixture(n_components=2, covariance_type="full", n_init=5, random_state=0).fit(X)
print("k-means ARI", round(adjusted_rand_score(y, km.labels_), 3))
print("GMM, 1 start  ARI", round(adjusted_rand_score(y, one.predict(X)), 3), " average log likelihood", round(float(one.score(X)), 3))
print("GMM, 5 starts ARI", round(adjusted_rand_score(y, gm.predict(X)), 3), " average log likelihood", round(float(gm.score(X)), 3))
print("weights", np.round(gm.weights_, 2).tolist())
print("means", np.round(gm.means_, 2).tolist())
print("probabilities for point [0, 1.25]:", np.round(gm.predict_proba([[0, 1.25]]), 3).tolist())
print("probabilities for point [4, 0]:", np.round(gm.predict_proba([[4, 0]]), 3).tolist())
''')

K.code('covariance_types', r'''
import numpy as np
from sklearn.mixture import GaussianMixture

rng = np.random.default_rng(1)
X = np.vstack([rng.multivariate_normal([0, 0], [[3, 2.4], [2.4, 3]], 250),     # tilted
               rng.multivariate_normal([6, 0], [[0.4, 0], [0, 2.5]], 250)])    # tall
for cov in ["spherical", "diag", "tied", "full"]:
    gm = GaussianMixture(n_components=2, covariance_type=cov, random_state=0).fit(X)
    params = gm._n_parameters()                    # the same count that bic() uses
    print(cov.ljust(9), " parameters", str(params).rjust(2), " BIC", round(float(gm.bic(X)), 1))
''', long=True)

K.code('choose_components', r'''
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.mixture import GaussianMixture

X, _ = make_blobs(n_samples=500, centers=4, cluster_std=[0.6, 1.0, 0.8, 1.4], random_state=3)
for k in range(1, 8):
    gm = GaussianMixture(n_components=k, random_state=0, n_init=3).fit(X)
    print("components", k, " BIC", str(round(float(gm.bic(X)), 1)).rjust(7), " AIC", str(round(float(gm.aic(X)), 1)).rjust(7))
''', long=True)

K.code('density_uses', r'''
import numpy as np
from sklearn.mixture import GaussianMixture

rng = np.random.default_rng(2)
normal_days = rng.normal([50, 200], [5, 20], size=(500, 2))     # temperature and power use of a machine
gm = GaussianMixture(n_components=3, random_state=0).fit(normal_days)
threshold = np.percentile(gm.score_samples(normal_days), 1)       # lowest 1% of log density
new = np.array([[51, 205], [49, 190], [70, 210], [50, 320]])
for p, s in zip(new.tolist(), gm.score_samples(new)):
    print(p, " log density", round(float(s), 2), " unusual" if s < threshold else " normal")
fake, _ = gm.sample(3)                                            # a GMM can also generate new data
print("three generated days:", np.round(fake, 1).tolist())
''', long=True)

K.code('bayesian_gmm', r'''
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.mixture import BayesianGaussianMixture

X, _ = make_blobs(n_samples=400, centers=3, cluster_std=0.8, random_state=5)
bgm = BayesianGaussianMixture(n_components=8, weight_concentration_prior=0.01, max_iter=500, random_state=0).fit(X)
print("weights of the 8 allowed components:", np.round(np.sort(bgm.weights_)[::-1], 3).tolist())
print("components really used (weight above 1%):", int((bgm.weights_ > 0.01).sum()))
''')

K.lesson('idea', 'Mixtures of bell curves and the EM algorithm', f'''
{src('Dempster, Laird and Rubin, the EM algorithm (1977), Bishop, Pattern Recognition and Machine Learning chapter 9, The Elements of Statistical Learning section 8.5, and the Stanford CS229 notes on EM.')}
{viz('mlem')}
{wwh('A <b>Gaussian mixture model</b> (GMM) says each data point came from one of K bell curves (Gaussians), chosen with probabilities called <b>weights</b>. We see the points but not which curve made each one. The <b>EM algorithm</b> (expectation maximisation) finds the means, spreads and weights that make the data most likely.',
     'A GMM gives <b>soft</b> clustering: every point gets a probability for every cluster, which is more honest for points between groups. It also gives a full density, so you can score how unusual a point is and even generate new data.',
     'Start with a guess. <b>E step</b>: for every point, compute the probability (the <b>responsibility</b>) that each curve produced it. <b>M step</b>: refit each curve as a weighted mean and spread, with the responsibilities as weights, and set each weight to its share of the responsibility. Repeat until the log likelihood stops rising.')}
{run('em_by_hand')}
{note('The first guess puts both means near the middle. Round by round the curves separate, and by round 9 they sit at 154.8 and 176.2, which are exactly the means of the shorter five and the taller five. The log likelihood rises every round, from &minus;39.65 to &minus;34.52, and then stays put. A height of 165 cm sits between the groups, so it gets a probability of 0.575 for the taller group instead of a hard label.', 'exam')}
{fxs(fx('Mixture density', 'p(x) = &Sigma;<sub>k</sub> &pi;<sub>k</sub> N(x | &mu;<sub>k</sub>, &sigma;<sub>k</sub><sup>2</sup>)', 'Weights &pi;<sub>k</sub> add up to 1.', key=True),
     fx('Responsibility (E step)', 'r<sub>ik</sub> = &pi;<sub>k</sub> N(x<sub>i</sub> | &mu;<sub>k</sub>, &sigma;<sub>k</sub><sup>2</sup>) / &Sigma;<sub>j</sub> &pi;<sub>j</sub> N(x<sub>i</sub> | &mu;<sub>j</sub>, &sigma;<sub>j</sub><sup>2</sup>)', 'Bayes rule for which curve made x<sub>i</sub>.', key=True))}
{scene('sorting a bag of mixed apples by weight', '<p>A bag holds apples from two orchards, one with small apples and one with big ones, but nobody marked which is which. You guess an average weight for each orchard. For each apple you say how likely it came from each orchard. Then you recompute each orchard’s average, letting each apple count in proportion to how likely it is to belong there. After a few rounds the two averages stop changing.</p>')}
''', kw=['Gaussian mixture model', 'GMM', 'EM algorithm', 'E step', 'M step', 'responsibility', 'soft clustering', 'log likelihood'])

K.lesson('sklearn', 'Gaussian mixtures in scikit-learn', f'''
{viz('mlgmm2d')}
{wwh('In more than one dimension each component has a mean vector and a <b>covariance matrix</b>, which sets its shape and tilt. So the clusters are ellipses, not circles. scikit-learn’s GaussianMixture fits them with EM and gives predict for the most likely component and predict_proba for the probabilities.',
     'k-means always draws straight boundaries halfway between centres and treats every cluster as a round ball of the same size. A GMM learns long, flat or tilted clusters of different sizes, which is much closer to many real datasets.',
     'GaussianMixture(n_components=2, covariance_type="full", n_init=5, random_state=0).fit(X). EM finds a local maximum, so use n_init above 1, just as with k-means. Scale the features when their units differ.')}
{run('sklearn_gmm')}
{note('The two clusters are long and flat, one above the other. k-means splits them left and right (ARI about 0), because that gives the smaller squared distances. A GMM with one start falls into the same trap. With 5 starts it finds the higher log likelihood (&minus;3.787 against &minus;4.045) and the right answer (ARI 0.941). A point halfway between the clusters gets about 50% for each, and a point inside the lower cluster gets 100%.', 'exam')}
''', kw=['GaussianMixture', 'covariance matrix', 'predict_proba', 'n_init', 'GMM vs k-means', 'elliptical clusters'])

K.lesson('covariance', 'Covariance types and choosing K', f'''
{wwh('The <b>covariance type</b> limits the shape of each ellipse: <b>spherical</b> (round, one spread each), <b>diag</b> (stretched along the axes), <b>tied</b> (all components share one tilted shape), or <b>full</b> (each its own tilted shape). The <b>BIC</b> (Bayesian information criterion) balances fit against the number of parameters, and lower is better.',
     'More flexible shapes always fit the training data better, so the likelihood alone always prefers more components and full covariances. BIC adds a penalty for every parameter, so you can choose both the covariance type and the number of components without a test set.',
     'Fit each candidate and call gm.bic(X). BIC = p ln n &minus; 2 ln L, where p is the number of parameters, n the number of points and L the likelihood. AIC = 2p &minus; 2 ln L penalises less and tends to choose more components.')}
{run('covariance_types')}
{note('One cluster is tilted and one is tall. Full covariance needs the most parameters (11) but fits so much better that its BIC is the lowest by far (3835 against 4062 for tied). Spherical is the cheapest at 7 parameters but cannot follow either shape, so its BIC is the worst.', 'tip')}
{run('choose_components')}
{note('The data was made from 4 blobs. BIC falls steeply up to 4 components (4169) and then rises again, so it picks 4. AIC also has its lowest value at 4 here, but its rise after that is much flatter, because its penalty per parameter is smaller.', 'exam')}
{table(['covariance_type', 'Shape of each cluster', 'Parameters per component in d dimensions'], [
    ['spherical', 'Round, own size', 'd means + 1 variance'],
    ['diag', 'Ellipse along the axes', 'd means + d variances'],
    ['tied', 'Same tilted ellipse for all', 'd means (plus one shared d(d + 1)/2)'],
    ['full', 'Own tilted ellipse', 'd means + d(d + 1)/2 covariances']])}
''', kw=['covariance_type', 'spherical', 'diag', 'tied', 'full', 'BIC', 'AIC', 'model selection'])

K.lesson('uses', 'Densities, anomalies, new samples and automatic K', f'''
{wwh('A fitted GMM is a full probability density. score_samples gives the log density of any point, so very low values flag <b>anomalies</b>. sample draws new points from the model. <b>BayesianGaussianMixture</b> puts a prior on the weights so that unneeded components shrink towards zero weight.',
     'Anomaly detection on sensor data, fraud checks and quality control all need "how normal is this point". A GMM answers that with a number. The Bayesian version saves you from choosing K exactly: give it more components than you need and it switches the extra ones off.',
     'Fit on normal data, set a threshold at a low percentile of the training log densities, and flag new points below it. For automatic K, use BayesianGaussianMixture(n_components=8, weight_concentration_prior=0.01) and count the components with real weight.')}
{run('density_uses')}
{note('The threshold is the lowest 1% of the training log densities. A day with normal temperature and power use scores about &minus;6.3. A day at 70 degrees scores &minus;13.2 and a day with 320 units of power scores &minus;25.5, both far below the threshold, so both are flagged. The model can also generate realistic new days.', 'tip')}
{run('bayesian_gmm')}
{note('make_blobs made 3 blobs, but two of them overlap so much that they look like one long cluster. Of the 8 components allowed, only 2 keep a weight above 1%, and the others shrink to almost nothing. The prior chose K by itself and judged two overlapping blobs to be one group, which shows that automatic K still needs a check.', 'exam')}
''', kw=['score_samples', 'density estimation', 'anomaly detection', 'sample', 'BayesianGaussianMixture', 'Dirichlet process'])

K.lesson('versus', 'GMM compared with k-means and the others', f'''
{versus('k-means and Gaussian mixtures', ['', 'k-means', 'Gaussian mixture'], [
    ['Assignment', 'Hard: one cluster per point', 'Soft: a probability for every cluster'],
    ['Cluster shape', 'Round, same size', 'Ellipses of any size and tilt (full covariance)'],
    ['What it optimises', 'Sum of squared distances (inertia)', 'Log likelihood of the data'],
    ['Algorithm', 'Lloyd: assign, update', 'EM: E step, M step'],
    ['Output', 'Centres and labels', 'Means, covariances, weights and a density'],
    ['Choosing K', 'Elbow, silhouette', 'BIC, AIC, Bayesian prior'],
    ['Speed', 'Faster', 'Slower, more parameters'],
    ['Can fail by', 'Wrong shapes, local minima', 'Local maxima, a component collapsing onto one point']],
    'use k-means for speed and round groups, and a GMM when clusters are elliptical, overlap, or when you need probabilities or a density.')}
{note('k-means is the limit of EM for a GMM whose components all share one round covariance &sigma;<sup>2</sup>I, with &sigma; shrinking to 0. Then each responsibility becomes 0 or 1, the E step becomes "nearest centre", and the M step becomes "mean of the points".', 'exam')}
''', kw=['k-means vs GMM', 'hard vs soft clustering', 'EM vs Lloyd'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Log likelihood', 'ln L = &Sigma;<sub>i</sub> ln &Sigma;<sub>k</sub> &pi;<sub>k</sub> N(x<sub>i</sub> | &mu;<sub>k</sub>, &Sigma;<sub>k</sub>)', 'The sum inside the log makes direct maximisation hard.', key=True),
     fx('E step', 'r<sub>ik</sub> = &pi;<sub>k</sub> N(x<sub>i</sub> | &mu;<sub>k</sub>, &Sigma;<sub>k</sub>) / &Sigma;<sub>j</sub> &pi;<sub>j</sub> N(x<sub>i</sub> | &mu;<sub>j</sub>, &Sigma;<sub>j</sub>)', 'Responsibilities.', key=True),
     fx('M step: weights and means', 'N<sub>k</sub> = &Sigma;<sub>i</sub> r<sub>ik</sub>, &pi;<sub>k</sub> = N<sub>k</sub> / n, &mu;<sub>k</sub> = (1/N<sub>k</sub>) &Sigma;<sub>i</sub> r<sub>ik</sub> x<sub>i</sub>', 'Weighted counts and means.', key=True),
     fx('M step: covariances', '&Sigma;<sub>k</sub> = (1/N<sub>k</sub>) &Sigma;<sub>i</sub> r<sub>ik</sub> (x<sub>i</sub> &minus; &mu;<sub>k</sub>)(x<sub>i</sub> &minus; &mu;<sub>k</sub>)<sup>T</sup>', 'Weighted spread.', key=True),
     fx('1D normal density', 'N(x | &mu;, &sigma;<sup>2</sup>) = exp(&minus;(x &minus; &mu;)<sup>2</sup> / 2&sigma;<sup>2</sup>) / (&sigma; &radic;(2&pi;))', 'The bell curve.'),
     fx('BIC and AIC', 'BIC = p ln n &minus; 2 ln L, AIC = 2p &minus; 2 ln L', 'Lower is better.', key=True))}
{steps('Worked example: one E step for one point', [
    'Two components with weights 0.5 and 0.5. At the point x, their densities are 0.3 and 0.1.',
    'Weighted densities: 0.5 &times; 0.3 = 0.15 and 0.5 &times; 0.1 = 0.05.',
    'Mixture density at x: 0.15 + 0.05 = 0.2.',
    eq('r<sub>1</sub> = 0.15 / 0.2 = 0.75, r<sub>2</sub> = 0.05 / 0.2 = 0.25'),
    'The point counts as three quarters of a point for component 1 in the next M step.'])}
{deep('Why EM never lowers the likelihood', '<p>For any distribution q over the hidden labels, Jensen’s inequality gives ln p(x | &theta;) &ge; &Sigma;<sub>z</sub> q(z) ln (p(x, z | &theta;) / q(z)), a lower bound called the ELBO. The gap is the KL divergence between q and the true posterior p(z | x, &theta;). The E step sets q to that posterior, so the gap is zero and the bound touches ln p. The M step raises the bound by changing &theta;, and since the bound sits below ln p, ln p rises at least as much. So the likelihood never falls, and EM converges to a stationary point, usually a local maximum. A danger peculiar to GMMs is a component that shrinks onto a single point: its variance goes to 0 and the likelihood to infinity. scikit-learn prevents this by adding reg_covar (1e&minus;6 by default) to the diagonal of every covariance.</p>')}
''', kw=['EM derivation', 'ELBO', 'Jensen inequality', 'covariance update', 'BIC formula', 'singular covariance'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A Gaussian mixture says the data came from a few bell curves, and EM finds them by guessing, checking which curve each point fits, and refitting.</p>',
    '<p>Fit GaussianMixture with n_init above 1, read predict_proba, choose the covariance type and K with BIC, and flag anomalies with score_samples.</p>',
    '<p>Derive the E and M steps, prove that EM never lowers the likelihood using the ELBO, count parameters for each covariance type, and explain k-means as a limit of EM.</p>',
    '<p>Study EM for general latent variable models (hidden Markov models, factor analysis), variational inference and the Dirichlet process mixture behind BayesianGaussianMixture, identifiability and label switching, and convergence rates of EM.</p>')}
{grow('Explain soft clustering with bell curves.',
      'Fit, select and use Gaussian mixtures in practice.',
      'Derive and analyse EM.')}
''', kw=['beginner', 'expert', 'latent variable models', 'variational inference', 'hidden Markov model'])

lc(1854, 'Maximum Population Year', 'maximum-population-year', 'e', 'Add 1 at each birth, subtract 1 at each death, and sweep', 'Mark +1 at each birth year and &minus;1 at each death year, then take running totals. The year with the highest total is the densest point on the time line, the same idea as finding where a density is highest.', r"""
def maximum_population(logs):
    change = [0] * 101
    for birth, death in logs:
        change[birth - 1950] += 1
        change[death - 1950] -= 1
    best_year, best, alive = 1950, 0, 0
    for i in range(101):
        alive = alive + change[i]
        if alive > best:
            best, best_year = alive, 1950 + i
    return best_year
""", [('maximum_population([[1993, 1999], [2000, 2010]])', 1993), ('maximum_population([[1950, 1961], [1960, 1971], [1970, 1981]])', 1960)])
lc(2848, 'Points That Intersect With Cars', 'points-that-intersect-with-cars', 'e', 'Mark every covered point in a set', 'Put every integer from start to end of each car into a set and count the set. Overlaps count once, just as a mixture covers a point whichever component it came from.', r"""
def number_of_points(nums):
    covered = set()
    for start, end in nums:
        for p in range(start, end + 1):
            covered.add(p)
    return len(covered)
""", [('number_of_points([[3, 6], [1, 5], [4, 7]])', 7), ('number_of_points([[1, 3], [5, 8]])', 7)])
lc(2028, 'Find Missing Observations', 'find-missing-observations', 'm', 'Work out the missing total from the mean', 'The full mean fixes the total sum, so the missing n rolls must add up to mean &times; (m + n) minus the known sum. If that total is outside n to 6n, it is impossible. Otherwise share it out as evenly as possible. Our answer puts the extra 1s first, and LeetCode accepts any valid answer.', r"""
def missing_rolls(rolls, mean, n):
    total = mean * (len(rolls) + n) - sum(rolls)
    if total < n or total > 6 * n:
        return []
    base, extra = divmod(total, n)
    return [base + 1] * extra + [base] * (n - extra)
""", [('missing_rolls([3, 2, 4, 3], 4, 2)', [6, 6]), ('missing_rolls([1, 5, 6], 3, 4)', [3, 2, 2, 2]), ('missing_rolls([1, 2, 3, 4], 6, 4)', [])])
lc(1109, 'Corporate Flight Bookings', 'corporate-flight-bookings', 'm', 'Difference array, then running sums', 'Add the seats at the first flight of each booking and subtract them after the last flight. A running sum then gives every flight’s total in one pass, the same sweep used to build a histogram of overlapping ranges.', r"""
def corp_flight_bookings(bookings, n):
    diff = [0] * (n + 1)
    for first, last, seats in bookings:
        diff[first - 1] += seats
        diff[last] -= seats
    answer, running = [], 0
    for i in range(n):
        running = running + diff[i]
        answer.append(running)
    return answer
""", [('corp_flight_bookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5)', [10, 55, 45, 25, 25]), ('corp_flight_bookings([[1, 2, 10], [2, 2, 15]], 2)', [10, 25])])
lc(1094, 'Car Pooling', 'car-pooling', 'm', 'Sweep the stops and track the load', 'Add passengers where they get on and remove them where they get off, then sweep the stops in order. If the load ever goes above the capacity, the answer is no.', r"""
def car_pooling(trips, capacity):
    change = {}
    for people, start, end in trips:
        change[start] = change.get(start, 0) + people
        change[end] = change.get(end, 0) - people
    load = 0
    for stop in sorted(change):
        load = load + change[stop]
        if load > capacity:
            return False
    return True
""", [('car_pooling([[2, 1, 5], [3, 3, 7]], 4)', False), ('car_pooling([[2, 1, 5], [3, 3, 7]], 5)', True)])
lc(4, 'Median of Two Sorted Arrays', 'median-of-two-sorted-arrays', 'h', 'Binary search for the split of the shorter array', 'Cut both arrays so that the left parts hold half of all the values and every left value is at most every right value. Binary search the cut in the shorter array. The median then comes from the values next to the cut. It finds the middle of two combined groups without merging them.', r"""
def find_median_sorted_arrays(a, b):
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < m else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1
        else:
            lo = i + 1
    return 0.0
""", [('find_median_sorted_arrays([1, 3], [2])', 2.0), ('find_median_sorted_arrays([1, 2], [3, 4])', 2.5)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>A mixture model is about how densely values cover a line and how groups combine. These problems practise sweeping a line to find the densest point, counting covered points, recovering missing values from a mean, building totals over overlapping ranges, tracking a running load, and finding the median of two groups combined. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'sweep line', 'difference array', 'mean', 'median', 'binary search'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>Gaussian mixture</b> models the data as K Gaussians with weights &pi;<sub>k</sub>, means &mu;<sub>k</sub> and covariances &Sigma;<sub>k</sub>.',
    '<b>EM</b> alternates the <b>E step</b> (responsibilities r<sub>ik</sub> by Bayes rule) and the <b>M step</b> (weighted counts, means and covariances). The log likelihood never falls.',
    'GMMs give <b>soft</b> assignments and elliptical clusters. k-means is the hard, round limit.',
    'EM finds local maxima: use n_init above 1. Choose K and covariance_type with <b>BIC</b>.',
    'A GMM is a density: score_samples flags anomalies and sample generates new data.',
    'BayesianGaussianMixture switches off unneeded components, but check its choice.'],
    'Unsupervised 2.1 starts dimensionality reduction with principal component analysis (PCA).')}
{files('Three tasks: the normal density, the E step responsibilities, and the M step weights and means.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A Gaussian mixture assumes each point comes from', ['A decision tree', 'One of K bell curves, chosen with some probability', 'The nearest centre only', 'A uniform distribution'], 1, 'Mixture.', 'The weights are the probabilities of each curve.')
K.quiz('e', 'The E step computes', ['New means', 'Each point’s probability of belonging to each component', 'The number of components', 'The BIC'], 1, 'Expectation.', 'Those probabilities are the responsibilities.')
K.quiz('e', 'The M step updates', ['The data', 'The weights, means and covariances', 'Only the labels', 'The learning rate'], 1, 'Maximisation.', 'Weighted by the responsibilities.')
K.quiz('e', 'GMM gives soft clustering, which means', ['Clusters are blurry pictures', 'Each point gets a probability for every cluster', 'It uses less memory', 'It needs no K'], 1, 'Not hard labels.', 'predict_proba returns those probabilities.')
K.quiz('m', 'In EM the log likelihood', ['Can go up or down', 'Never decreases from one round to the next', 'Always reaches the global maximum', 'Is not used'], 1, 'Monotone.', 'But it may end in a local maximum.')
K.quiz('m', 'Compared with k-means, a full covariance GMM can model', ['Only round clusters', 'Elliptical, tilted clusters of different sizes', 'Only one cluster', 'Only categorical data'], 1, 'Covariance.', 'Each component has its own shape.')
K.quiz('m', 'Lower BIC means', ['A worse model', 'A better trade off between fit and number of parameters', 'More components always', 'Overfitting'], 1, 'p ln n &minus; 2 ln L.', 'Pick the model with the lowest BIC.')
K.quiz('m', 'Which covariance_type has the fewest parameters?', ['full', 'tied', 'diag', 'spherical'], 3, 'Round.', 'One variance per component.')
K.quiz('m', 'To flag unusual points with a fitted GMM you use', ['predict', 'score_samples with a low threshold', 'n_init', 'means_'], 1, 'Log density.', 'Low density means unusual.')
K.quiz('h', 'k-means is the limit of EM for a GMM with', ['Full covariances', 'Shared spherical covariance shrinking to zero', 'Unequal weights', 'One component'], 1, 'Hard assignments.', 'Responsibilities become 0 or 1.')
K.quiz('h', 'Why can the GMM likelihood go to infinity?', ['Too many points', 'A component can collapse onto one point with variance going to 0', 'BIC is negative', 'The weights add to 1'], 1, 'Singular covariance.', 'reg_covar prevents it.')
K.quiz('h', 'AIC compared with BIC usually', ['Penalises parameters more', 'Penalises parameters less, so it can choose more components', 'Is identical', 'Ignores the likelihood'], 1, '2p against p ln n.', 'For n above about 8, ln n &gt; 2.')
K.quiz('x', 'In the style of a Stanford CS229 exam: EM maximises a lower bound on ln p(x). After the E step the gap between them equals', ['Zero', 'The KL divergence between q and the posterior, which the E step makes zero', 'The entropy of the data', 'The BIC'], 1, 'ELBO.', 'q is set to the exact posterior.')
K.quiz('x', 'In the style of a CMU 10-708 exam: swapping the labels of two components of a fitted GMM', ['Changes the likelihood', 'Leaves the likelihood unchanged (label switching)', 'Makes it invalid', 'Doubles K'], 1, 'Identifiability.', 'The likelihood has K! equal maxima.')

K.calc('e', 'Weights 0.3 and 0.7. At x the densities are 0.2 and 0.1. Mixture density at x?', '0.13', '&Sigma; &pi;<sub>k</sub> N<sub>k</sub>.', ['0.3 &times; 0.2 = 0.06.', '0.7 &times; 0.1 = 0.07.', eq('0.06 + 0.07 = 0.13')], check=0.13)
K.calc('e', 'Weights 0.5 and 0.5, densities 0.3 and 0.1 at x. Responsibility of component 1?', '0.75', 'Weighted density over the total.', ['0.5 &times; 0.3 = 0.15.', '0.5 &times; 0.1 = 0.05, total 0.2.', eq('0.15 / 0.2 = 0.75')], check=0.75)
K.calc('e', 'Responsibilities for component 1 over four points: 0.9, 0.8, 0.2, 0.1. New weight?', '0.5', 'N<sub>1</sub> / n.', ['N<sub>1</sub> = 0.9 + 0.8 + 0.2 + 0.1 = 2.0.', 'n = 4.', eq('2.0 / 4 = 0.5')], check=0.5)
K.calc('m', 'Values 0, 6, 12 with responsibilities 1, 0.5, 0.5 for a component. New mean?', '4.5', '&Sigma; r x / &Sigma; r.', ['&Sigma; r x = 0 + 3 + 6 = 9.', '&Sigma; r = 2.', eq('9 / 2 = 4.5')], check=4.5)
K.calc('m', 'Full covariance GMM, 2 features, K = 3. Number of parameters?', '17', 'Means, covariances, weights.', ['Each component: 2 means + 3 covariance entries = 5.', '3 components: 15.', eq('15 + (3 &minus; 1) weights = 17')], check=17)
K.calc('m', 'Diagonal covariance GMM, 2 features, K = 3. Number of parameters?', '14', 'd means + d variances each.', ['Each component: 2 + 2 = 4.', '3 components: 12.', eq('12 + 2 weights = 14')], check=14)
K.calc('m', 'p = 5 parameters, ln L = &minus;200. AIC?', '410', '2p &minus; 2 ln L.', ['2p = 10.', '&minus;2 ln L = 400.', eq('10 + 400 = 410')], check=410)
K.calc('h', 'p = 5, ln L = &minus;200, and ln n = 5. BIC?', '425', 'p ln n &minus; 2 ln L.', ['p ln n = 25.', '&minus;2 ln L = 400.', eq('25 + 400 = 425')], check=425)
K.calc('h', 'Model A: ln L = &minus;1000, p = 11. Model B: ln L = &minus;990, p = 17. ln n = 6. BIC of B minus BIC of A?', '16', 'Compute both BICs.', ['BIC A = 66 + 2000 = 2066.', 'BIC B = 102 + 1980 = 2082.', eq('2082 &minus; 2066 = 16, so A is preferred')], check=16)
K.calc('x', 'In the style of a Stanford CS229 problem: 1D, equal weights, both variances 1, means 0 and 2. Responsibility of the second component for x = 1?', '0.5', 'Symmetry.', ['x = 1 is 1 away from both means.', 'Equal variances give equal densities, and the weights are equal.', eq('r = 0.5')], check=0.5)

K.assign('normal_pdf', 'e', 'The bell curve',
         '<p>Write <code>normal_pdf(x, mean, sd)</code> that returns the normal density exp(&minus;(x &minus; mean)<sup>2</sup> / (2 sd<sup>2</sup>)) / (sd &radic;(2&pi;)), rounded to 4 decimals.</p>',
         """
import math


def normal_pdf(x, mean, sd):
    # your code here
    pass
""", [('normal_pdf(0, 0, 1)', 0.3989), ('normal_pdf(1, 0, 1)', 0.242), ('normal_pdf(5, 5, 2)', 0.1995)],
         """
import math


def normal_pdf(x, mean, sd):
    return round(math.exp(-((x - mean) ** 2) / (2 * sd ** 2)) / (sd * math.sqrt(2 * math.pi)), 4)
""", 'Translate the formula directly with math.exp, math.sqrt and math.pi.', '<p>At the mean of a standard normal the density is 1 / &radic;(2&pi;), about 0.3989.</p>')
K.assign('responsibilities', 'm', 'The E step for one value',
         '<p>Write <code>responsibilities(x, means, sds, weights)</code> for a 1D mixture. Return the list of probabilities that each component produced x, each rounded to 4 decimals.</p>',
         """
import math


def responsibilities(x, means, sds, weights):
    # your code here
    pass
""", [('responsibilities(0, [0, 0], [1, 1], [0.5, 0.5])', [0.5, 0.5]), ('responsibilities(0, [0, 4], [1, 1], [0.5, 0.5])', [0.9997, 0.0003]), ('responsibilities(2, [0, 4], [1, 1], [0.25, 0.75])', [0.25, 0.75])],
         """
import math


def responsibilities(x, means, sds, weights):
    parts = []
    for m, s, w in zip(means, sds, weights):
        parts.append(w * math.exp(-((x - m) ** 2) / (2 * s ** 2)) / (s * math.sqrt(2 * math.pi)))
    total = sum(parts)
    return [round(p / total, 4) for p in parts]
""", 'Weight times density for each component, then divide by the sum.', '<p>In the last test x = 2 is the same distance from both means, so the densities are equal and the responsibilities are just the weights.</p>')
K.assign('m_step', 'h', 'The M step for weights and means',
         '<p>Write <code>m_step(xs, resp)</code>. xs is a list of values and resp[i] is the list of responsibilities of value i for each component. Return [weights, means], two lists rounded to 4 decimals, where weight k = N<sub>k</sub> / n and mean k = &Sigma; r<sub>ik</sub> x<sub>i</sub> / N<sub>k</sub>.</p>',
         """
def m_step(xs, resp):
    # your code here
    pass
""", [('m_step([1, 2, 9, 10], [[1, 0], [1, 0], [0, 1], [0, 1]])', [[0.5, 0.5], [1.5, 9.5]]), ('m_step([0, 10], [[0.5, 0.5], [0.5, 0.5]])', [[0.5, 0.5], [5.0, 5.0]]), ('m_step([0, 4], [[0.75, 0.25], [0.25, 0.75]])', [[0.5, 0.5], [1.0, 3.0]])],
         """
def m_step(xs, resp):
    k = len(resp[0])
    weights, means = [], []
    for j in range(k):
        nk = sum(r[j] for r in resp)
        weights.append(round(nk / len(xs), 4))
        means.append(round(sum(r[j] * x for r, x in zip(resp, xs)) / nk, 4))
    return [weights, means]
""", 'For each component add up its responsibilities, then take the weighted mean.', '<p>With hard 0 or 1 responsibilities, as in the first test, the M step is exactly the k-means update step.</p>')

K.must('Model', 'p(x) = &Sigma; &pi;<sub>k</sub> N(x | &mu;<sub>k</sub>, &Sigma;<sub>k</sub>). Weights add to 1. Each component has its own mean and covariance.')
K.must('EM', 'E step: r<sub>ik</sub> by Bayes rule. M step: N<sub>k</sub> = &Sigma; r, &pi; = N<sub>k</sub>/n, weighted means and covariances. Likelihood never falls, local maxima.')
K.must('Practice', 'GaussianMixture(n_components, covariance_type, n_init). predict_proba for soft labels. Scale features.')
K.must('Choosing', 'BIC = p ln n &minus; 2 ln L (lower is better) for K and covariance_type. AIC penalises less.')
K.must('Uses', 'Soft clustering, density estimation, anomaly scores with score_samples, sampling, BayesianGaussianMixture for automatic K.')
K.must('Theory', 'ELBO and Jensen, k-means as the hard spherical limit, collapse to a point prevented by reg_covar, label switching.')

T = K.topic(
    slug='ml-gmm', topic='ml-gmm', step=(1, 'Clustering', 'ml-u1', 'Find groups in data that has no labels: by centres, by trees of merges, by density and by probability.', 'Intermediate'),
    title='Gaussian mixture models and EM', short='Gaussian mixtures', badge='1.3', minutes=50,
    lead='Cluster with probabilities: model data as a mixture of bell curves, fit it with the EM algorithm, compare it with k-means, choose the covariance type and the number of components with BIC, and use the fitted density for anomalies and new samples.',
    desc='Gaussian mixture model, GMM, EM algorithm, E step, M step, responsibility, soft clustering, covariance matrix, covariance_type, BIC, AIC, log likelihood, predict_proba, score_samples, anomaly detection, BayesianGaussianMixture, ELBO, k-means limit.',
    summary='Mixtures of Gaussians, the E and M steps, soft clusters, covariance types, BIC, and density based anomaly scores.',
    keywords=['Gaussian mixture model', 'EM algorithm', 'responsibility', 'soft clustering', 'BIC', 'covariance type', 'GaussianMixture', 'BayesianGaussianMixture', 'density estimation', 'ELBO'],
    recap='<p>A Gaussian mixture explains the data as a few bell curves. EM fits them by alternating soft assignments and weighted refits, and the result is both a clustering and a density.</p>',
    added='2026-11-13', leet=leet_items())
