# Unsupervised 1.1: k-means. Checked against Lloyd, Least Squares Quantization in PCM (1957, published 1982), MacQueen
# (1967), Arthur and Vassilvitskii, k-means++: The Advantages of Careful Seeding (SODA 2007), Sculley, Web-Scale
# K-Means Clustering (WWW 2010), Rousseeuw, Silhouettes (1987), Hastie, Tibshirani and Friedman, The Elements of
# Statistical Learning section 14.3, and the scikit-learn 1.8 user guide section 2.3.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-kmeans')
K = Kit()

K.code('kmeans_by_hand', r'''
import numpy as np

X = np.array([[1, 1], [1.5, 2], [2, 1], [6, 6], [7, 6.5], [6.5, 7], [1, 7], [2, 6.5], [1.5, 7.5]])
centres = X[[0, 1, 2]].astype(float)                 # a poor start: three points from the same group

for step in range(1, 5):
    dist = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)     # squared distance to each centre
    labels = dist.argmin(axis=1)                                        # assign: nearest centre
    inertia = dist.min(axis=1).sum()
    print("step", step, " labels", labels.tolist(), " inertia", round(float(inertia), 2))
    centres = np.array([X[labels == k].mean(axis=0) for k in range(3)])  # update: mean of each group
    print("   new centres", np.round(centres, 2).tolist())
''', long=True)

K.code('sklearn_kmeans', r'''
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

X, true = make_blobs(n_samples=300, centers=4, cluster_std=0.9, random_state=2)
km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(X)
print("points per cluster:", np.bincount(km.labels_).tolist())
print("centres:", np.round(km.cluster_centers_, 2).tolist())
print("inertia (sum of squared distances):", round(float(km.inertia_), 1))
print("new point [0, 0] goes to cluster", int(km.predict([[0, 0]])[0]))
''')

K.code('choose_k', r'''
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score

X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.9, random_state=2)
for k in range(2, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    print("k", k, " inertia", str(round(float(km.inertia_))).rjust(5), " silhouette", round(float(silhouette_score(X, km.labels_)), 3))
''', long=True)

K.code('init_matters', r'''
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

X, _ = make_blobs(n_samples=500, centers=8, cluster_std=0.6, random_state=5)
for init in ["random", "k-means++"]:
    results = [round(float(KMeans(n_clusters=8, init=init, n_init=1, random_state=s).fit(X).inertia_)) for s in range(6)]
    print(init.ljust(9), "inertia over 6 starts:", results)
best = KMeans(n_clusters=8, n_init=10, random_state=0).fit(X)
print("k-means++ with n_init=10 keeps the best:", round(float(best.inertia_)))
''', long=True)

K.code('scaling', r'''
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(0)
group = np.repeat([0, 1], 100)
age = np.where(group == 0, 30, 50) + rng.normal(0, 4, 200)              # the real difference
income = rng.normal(50000, 15000, 200)                                  # big numbers, no group information
X = np.column_stack([age, income])
for name, data in [("raw", X), ("scaled", StandardScaler().fit_transform(X))]:
    labels = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(data)
    print(name.ljust(6), "agreement with the true groups (ARI):", round(adjusted_rand_score(group, labels), 3))
''', long=True)

K.code('shapes', r'''
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs, make_moons
from sklearn.metrics import adjusted_rand_score

X1, y1 = make_moons(n_samples=300, noise=0.05, random_state=0)
X2, y2 = make_blobs(n_samples=300, centers=[[0, 0], [3, 0]], cluster_std=[0.3, 1.5], random_state=0)
for name, X, y in [("two moons", X1, y1), ("blobs of very different size", X2, y2)]:
    labels = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X)
    print(name.ljust(28), "ARI", round(adjusted_rand_score(y, labels), 3))
''', long=True)

K.code('minibatch', r'''
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.datasets import make_blobs

X, _ = make_blobs(n_samples=20000, centers=5, cluster_std=1.0, random_state=1)
full = KMeans(n_clusters=5, n_init=3, random_state=0).fit(X)
mini = MiniBatchKMeans(n_clusters=5, batch_size=1024, n_init=3, random_state=0).fit(X)
print("KMeans inertia:         ", round(float(full.inertia_)))
print("MiniBatchKMeans inertia:", round(float(mini.inertia_)))
print("difference:", round(100 * (mini.inertia_ - full.inertia_) / full.inertia_, 2), "%")
''')

K.lesson('idea', 'Finding groups without labels', f'''
{src('Lloyd (1957), MacQueen (1967), Arthur and Vassilvitskii, k-means++ (2007), Sculley, Web-Scale K-Means (2010), Rousseeuw, Silhouettes (1987), The Elements of Statistical Learning section 14.3, and the scikit-learn 1.8 user guide section 2.3.')}
{viz('mlkmeans')}
{wwh('<b>Clustering</b> splits data into groups of similar points without any labels. <b>k-means</b> is the simplest and most used method: it finds k centres and gives every point to its nearest centre, so that the total squared distance from points to their centres (the <b>inertia</b>) is as small as possible.',
     'Most data has no labels. Clustering finds structure on its own: customer segments for marketing, groups of similar documents, colours for image compression, or a first look at a new dataset. k-means is fast, simple and scales to millions of points.',
     'Lloyd’s algorithm: choose k starting centres, then repeat two steps until nothing changes. <b>Assign</b> each point to its nearest centre. <b>Update</b> each centre to the mean of its points. Each step can only lower the inertia, so it always stops, but possibly in a local minimum.')}
{run('kmeans_by_hand')}
{note('The start is deliberately bad: all three centres begin in the bottom left group. k-means still converges in three rounds, but to a poor answer with inertia 40.5, because the two groups on the right share one centre. It found a local minimum, not the best clustering. Good starting centres matter.', 'exam')}
{fxs(fx('k-means objective (inertia)', 'J = &Sigma;<sub>i</sub> |x<sub>i</sub> &minus; &mu;<sub>c(i)</sub>|<sup>2</sup>', 'Sum of squared distances to the assigned centre.', key=True),
     fx('Update step', '&mu;<sub>k</sub> = (1/|C<sub>k</sub>|) &Sigma;<sub>i&isin;C<sub>k</sub></sub> x<sub>i</sub>', 'The mean minimises the squared distances.', key=True))}
{scene('placing ice cream vans on a beach', '<p>Three ice cream vans want to park so that every sunbather walks as little as possible. Each sunbather goes to the nearest van. Then each van moves to the middle of its own customers. After a few rounds of walking and moving, nobody changes van any more. That is k-means.</p>')}
''', kw=['clustering', 'k-means', 'Lloyd algorithm', 'inertia', 'centroid', 'unsupervised learning', 'local minimum'])

K.lesson('sklearn', 'k-means in scikit-learn', f'''
{wwh('<b>KMeans</b> in scikit-learn runs Lloyd’s algorithm several times from different starts (n_init) and keeps the run with the lowest inertia. It stores the centres in cluster_centers_, the labels in labels_, and can assign new points with predict.',
     'Clustering is often a step in a bigger system: segment customers once, then put each new customer into a segment. predict does exactly that, using the nearest centre.',
     'KMeans(n_clusters=4, n_init=10, random_state=0).fit(X). Scale features first (StandardScaler) so that each feature counts equally in the distance.')}
{run('sklearn_kmeans')}
{run('scaling')}
{note('Age holds the real groups (30 against 50) and income is pure noise, but income is measured in tens of thousands. Unscaled, the distance is almost all income, so k-means splits by income and agrees with the true groups no better than chance (ARI 0.007). After StandardScaler it finds the groups perfectly (ARI 1.0).', 'tip')}
''', kw=['KMeans', 'n_init', 'cluster_centers_', 'labels_', 'predict', 'feature scaling', 'adjusted Rand index'])

K.lesson('choosek', 'Choosing k: elbow and silhouette', f'''
{viz('mlelbow')}
{wwh('k-means needs k in advance. The <b>elbow method</b> plots inertia against k and looks for the bend after which extra clusters help little. The <b>silhouette score</b> compares, for each point, the mean distance to its own cluster (a) with the mean distance to the nearest other cluster (b).',
     'Inertia always falls as k grows (with k = n it is zero), so the lowest inertia is never the answer. The silhouette rewards tight, well separated clusters and has a clear best value.',
     'Silhouette of a point = (b &minus; a) / max(a, b), between &minus;1 and 1. silhouette_score(X, labels) averages it. Try a range of k, look at both measures, then check the clusters make sense for the purpose.')}
{run('choose_k')}
{note('The data was made with 4 groups, but two of them are close together. The elbow is around k = 3 or 4 and the silhouette prefers k = 3 (0.696 against 0.634). Neither is wrong: at a coarse level there are 3 groups. The final choice depends on what the clusters are for.', 'exam')}
{fx('Silhouette of a point', 's = (b &minus; a) / max(a, b)', 'a = mean distance inside its cluster, b = to the nearest other cluster.', key=True)}
''', kw=['choosing k', 'elbow method', 'silhouette score', 'silhouette_score', 'cluster validation'])

K.lesson('init', 'Starting centres and k-means++', f'''
{wwh('<b>k-means++</b> chooses starting centres that are spread out: the first at random, then each next one with probability proportional to its squared distance from the nearest centre already chosen.',
     'Random starts often place two centres in the same group and leave another group with none, giving a bad local minimum. k-means++ makes that much less likely and comes with a guarantee: its expected inertia is within a factor of O(log k) of the best possible.',
     'k-means++ is the default in scikit-learn (init="k-means++"). Keep n_init above 1 so several starts are tried. MiniBatchKMeans updates the centres from small random batches and is much faster on large data, for a tiny loss in inertia.')}
{run('init_matters')}
{note('With purely random starts, the six runs end anywhere from 329 to 1461. With k-means++ every run ends between 329 and 351, and keeping the best of 10 gives 329. That is why the default is k-means++ with several starts.', 'tip')}
{run('minibatch')}
''', kw=['k-means++', 'initialisation', 'n_init', 'MiniBatchKMeans', 'local minima', 'seeding'])

K.lesson('limits', 'When k-means fails', f'''
{wwh('k-means assumes clusters are round blobs of similar size, separated by straight boundaries halfway between centres. It fails on long, curved or nested shapes, on clusters of very different sizes or densities, and it is pulled around by outliers.',
     'Knowing the assumptions tells you when to switch method. Because every point goes to its nearest centre, the boundaries between clusters are always straight lines (a Voronoi diagram), whatever the true shape.',
     'Check the clusters visually (after PCA if there are many features), compare with other methods, and switch to DBSCAN for odd shapes and noise, hierarchical clustering for nested groups, or Gaussian mixtures for elliptical clusters of different sizes. These are the next two chapters.')}
{run('shapes')}
{note('On the two moons k-means cuts straight across both shapes (ARI 0.24). On a tight blob next to a wide one, it moves the boundary into the wide blob and steals its edge points (ARI 0.61), because it always splits halfway between centres.', 'exam')}
{table(['Assumption', 'Breaks when', 'Try instead'], [
    ['Round clusters', 'Long or curved shapes', 'DBSCAN, spectral clustering'],
    ['Similar sizes and spreads', 'One tight and one wide cluster', 'Gaussian mixture'],
    ['No outliers', 'Extreme points drag centres', 'k-medoids, DBSCAN'],
    ['Known k', 'No idea how many groups', 'DBSCAN, hierarchical with a dendrogram'],
    ['Numeric features, scaled', 'Categories, different units', 'k-modes, scaling, other distances']])}
''', kw=['k-means assumptions', 'Voronoi', 'non convex clusters', 'outliers', 'cluster sizes', 'limitations'])

K.lesson('versus', 'k-means compared', f'''
{versus('Clustering methods at a glance (the next chapters cover the others)', ['', 'k-means', 'Hierarchical', 'DBSCAN', 'Gaussian mixture'], [
    ['Needs k', 'Yes', 'No (cut the tree later)', 'No', 'Yes'],
    ['Cluster shape', 'Round', 'Depends on linkage', 'Any', 'Elliptical'],
    ['Handles noise', 'No', 'No', 'Yes (marks it)', 'Partly'],
    ['Soft assignment', 'No', 'No', 'No', 'Yes (probabilities)'],
    ['Speed on large data', 'Very fast', 'Slow (n<sup>2</sup> memory)', 'Fast with an index', 'Moderate']],
    'start with k-means for speed and simplicity, and switch when the shapes or the noise tell you to.')}
''', kw=['k-means vs DBSCAN', 'k-means vs hierarchical', 'k-means vs GMM', 'choosing a clustering method'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Objective', 'J(c, &mu;) = &Sigma;<sub>i</sub> |x<sub>i</sub> &minus; &mu;<sub>c(i)</sub>|<sup>2</sup>', 'Minimised over assignments c and centres &mu;.', key=True),
     fx('Assign step', 'c(i) = argmin<sub>k</sub> |x<sub>i</sub> &minus; &mu;<sub>k</sub>|<sup>2</sup>', 'Best c for fixed &mu;.', key=True),
     fx('Update step', '&mu;<sub>k</sub> = mean of the points with c(i) = k', 'Best &mu; for fixed c.', key=True),
     fx('k-means++ seeding', 'P(choose x) = D(x)<sup>2</sup> / &Sigma; D(x&prime;)<sup>2</sup>', 'D(x) = distance to the nearest chosen centre.', key=True),
     fx('Silhouette', 's = (b &minus; a)/max(a, b)', 'Average over points.'))}
{steps('Worked example: one k-means++ choice', [
    'One centre is already chosen. Three remaining points have squared distances 1, 4 and 5 to it.',
    'The total is 1 + 4 + 5 = 10.',
    'Each point is chosen with probability D<sup>2</sup> / 10.',
    eq('P(third point) = 5 / 10 = 0.5'),
    'Far points are likely, so the next centre usually lands in a group that has none yet.'])}
{deep('Why k-means always stops, and how hard it really is', '<p>Each assign step chooses the best c for the current centres and each update step the best centres for the current c, so J never increases. There are finitely many ways to assign n points to k clusters, so the algorithm must stop. This is coordinate descent, and it is also the limit of EM for a Gaussian mixture with equal, shrinking variances (next but one chapter). Finding the global minimum is NP hard, even for k = 2 in general dimension (Aloise and others, 2009), and in the worst case Lloyd’s algorithm can need exponentially many rounds (Vattani, 2011), although on real data it converges in a few dozen. k-means++ guarantees an expected J within 8(ln k + 2) of the optimum.</p>')}
''', kw=['k-means objective', 'assign step', 'update step', 'k-means++ formula', 'coordinate descent', 'NP hard'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>k-means puts similar points into k groups by moving k centres until every point is near its own centre.</p>',
    '<p>Run KMeans on scaled data, choose k with the elbow and silhouette, use predict for new points, and use MiniBatchKMeans for big data.</p>',
    '<p>Explain the two step algorithm as coordinate descent, why it finds local minima, why k-means++ helps, and which data shapes break it.</p>',
    '<p>Study the NP hardness of k-means, the k-means++ approximation bound, kernel k-means and its link to spectral clustering, k-medoids (PAM), and coresets for clustering huge data.</p>')}
{grow('Explain how centres and points settle into groups.',
      'Cluster scaled data and pick k sensibly.',
      'Analyse convergence, seeding and failure modes.')}
''', kw=['beginner', 'expert', 'kernel k-means', 'k-medoids', 'coresets'])

lc(200, 'Number of Islands', 'number-of-islands', 'm', 'Flood fill each new piece of land', 'Scan the grid. Each time you meet unvisited land, count an island and visit all land connected to it. Each island is a cluster of touching cells.', r'''
def num_islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen = set()
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                count = count + 1
                stack = [(r, c)]
                seen.add((r, c))
                while stack:
                    i, j = stack.pop()
                    for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        a, b = i + di, j + dj
                        if 0 <= a < rows and 0 <= b < cols and grid[a][b] == "1" and (a, b) not in seen:
                            seen.add((a, b))
                            stack.append((a, b))
    return count
''', [('num_islands([["1", "1", "0", "0"], ["1", "1", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"]])', 3), ('num_islands([["1", "1", "1"], ["0", "1", "0"], ["1", "1", "1"]])', 1)])
lc(695, 'Max Area of Island', 'max-area-of-island', 'm', 'Flood fill and count the cells', 'Visit each island as in the last problem, counting its cells, and keep the largest count. The size of each cluster is often the first thing you check after clustering.', r'''
def max_area_of_island(grid):
    rows, cols = len(grid), len(grid[0])
    seen = set()
    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and (r, c) not in seen:
                size = 0
                stack = [(r, c)]
                seen.add((r, c))
                while stack:
                    i, j = stack.pop()
                    size = size + 1
                    for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        a, b = i + di, j + dj
                        if 0 <= a < rows and 0 <= b < cols and grid[a][b] == 1 and (a, b) not in seen:
                            seen.add((a, b))
                            stack.append((a, b))
                best = max(best, size)
    return best
''', [('max_area_of_island([[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 1, 1, 0]])', 4), ('max_area_of_island([[0, 0, 0]])', 0)])
lc(547, 'Number of Provinces', 'number-of-provinces', 'm', 'Union find over the connections', 'Every city starts as its own group. For each connection, merge the two groups. The number of groups left is the answer. Single linkage clustering merges groups the same way.', r'''
def find_circle_num(is_connected):
    n = len(is_connected)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    groups = n
    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j]:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
                    groups = groups - 1
    return groups
''', [('find_circle_num([[1, 1, 0], [1, 1, 0], [0, 0, 1]])', 2), ('find_circle_num([[1, 0, 0], [0, 1, 0], [0, 0, 1]])', 3)])
lc(1029, 'Two City Scheduling', 'two-city-scheduling', 'm', 'Sort by how much city A saves', 'Send everyone to city B, then move the half for whom going to A instead saves the most. Sort by cost A minus cost B and send the first half to A. It is an assignment of points to two groups at the lowest total cost.', r'''
def two_city_sched_cost(costs):
    order = sorted(costs, key=lambda c: c[0] - c[1])
    n = len(costs) // 2
    return sum(c[0] for c in order[:n]) + sum(c[1] for c in order[n:])
''', [('two_city_sched_cost([[10, 20], [30, 200], [400, 50], [30, 20]])', 110), ('two_city_sched_cost([[259, 770], [448, 54], [926, 667], [184, 139], [840, 118], [577, 469]])', 1859)])
lc(2033, 'Minimum Operations to Make a Uni-Value Grid', 'minimum-operations-to-make-a-uni-value-grid', 'm', 'Move everything to the median', 'All values must share the same remainder when divided by x, or it is impossible. Then the cheapest common value is the median, because the median minimises the total absolute distance, just as the mean minimises the squared distance in k-means.', r'''
def min_operations(grid, x):
    values = sorted(v for row in grid for v in row)
    if any((v - values[0]) % x for v in values):
        return -1
    median = values[len(values) // 2]
    return sum(abs(v - median) // x for v in values)
''', [('min_operations([[2, 4], [6, 8]], 2)', 4), ('min_operations([[1, 2], [3, 4]], 2)', -1)])
lc(1478, 'Allocate Mailboxes', 'allocate-mailboxes', 'h', 'One dimensional k medians by dynamic programming', 'Sort the houses. The best single mailbox for a run of houses sits at their median. Then dp[j][i] is the least distance for the first i houses with j mailboxes: try every last run. This is exact clustering in one dimension, something k-means can only approximate.', r'''
def min_distance(houses, k):
    h = sorted(houses)
    n = len(h)
    cost = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            m = h[(i + j) // 2]
            cost[i][j] = sum(abs(h[t] - m) for t in range(i, j + 1))
    INF = float("inf")
    dp = [[INF] * (n + 1) for _ in range(k + 1)]
    dp[0][0] = 0
    for j in range(1, k + 1):
        for i in range(1, n + 1):
            for s in range(i):
                if dp[j - 1][s] < INF:
                    dp[j][i] = min(dp[j][i], dp[j - 1][s] + cost[s][i - 1])
    return dp[k][n]
''', [('min_distance([1, 4, 8, 10, 20], 3)', 5), ('min_distance([2, 3, 5, 12, 18], 2)', 9)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Clustering is grouping. These problems practise finding groups of connected cells, the size of the biggest group, merging connected items with union find, splitting people into two groups at the least cost, moving values to a common centre (the median), and exact one dimensional clustering with dynamic programming. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'flood fill', 'union find', 'connected components', 'median', 'dynamic programming'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>k-means</b> minimises the inertia &Sigma;|x &minus; &mu;<sub>c(x)</sub>|<sup>2</sup> by repeating <b>assign</b> (nearest centre) and <b>update</b> (mean of the points).',
    'It always converges, but to a <b>local minimum</b>. Use <b>k-means++</b> starts and n_init &gt; 1.',
    'Scale the features first, or the feature with the biggest units decides everything.',
    'Choose k with the <b>elbow</b> of the inertia curve and the <b>silhouette score</b>, then check the purpose.',
    'k-means expects round clusters of similar size and is hurt by outliers. Boundaries are always straight.',
    'MiniBatchKMeans is much faster on big data with almost the same inertia.'],
    'Unsupervised 1.2 covers hierarchical clustering and DBSCAN, which need no k and handle odd shapes and noise.')}
{files('Three tasks: the assign step, the update step, and the silhouette of one point.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'k-means needs you to choose', ['The labels', 'The number of clusters k', 'A learning rate', 'A tree depth'], 1, 'The k.', 'k is given before running.')
K.quiz('e', 'In the update step each centre moves to', ['A random point', 'The mean of the points assigned to it', 'The farthest point', 'The origin'], 1, 'Centroid.', 'The mean minimises the squared distances.')
K.quiz('e', 'Inertia is', ['The number of clusters', 'The sum of squared distances from points to their centres', 'The silhouette', 'The accuracy'], 1, 'What k-means minimises.', 'Lower means tighter clusters.')
K.quiz('e', 'Before k-means on features in different units you should', ['Do nothing', 'Scale them', 'Square them', 'Sort them'], 1, 'Distances.', 'Otherwise the biggest units dominate.')
K.quiz('m', 'As k increases, inertia', ['Always increases', 'Never increases (with the best clustering for each k)', 'Stays the same', 'Becomes negative'], 1, 'More centres, shorter distances.', 'So the minimum inertia cannot pick k.')
K.quiz('m', 'A silhouette near 1 for a point means', ['It sits between clusters', 'It is much closer to its own cluster than to others', 'It is an outlier', 'It is misassigned'], 1, '(b &minus; a)/max(a, b).', 'a is small compared with b.')
K.quiz('m', 'Why run k-means with n_init &gt; 1?', ['To use more clusters', 'Different starts reach different local minima, keep the best', 'To scale features', 'To compute silhouette'], 1, 'Local minima.', 'The run with the lowest inertia is kept.')
K.quiz('m', 'k-means++ chooses the next starting centre', ['Uniformly at random', 'With probability proportional to squared distance from chosen centres', 'Always the farthest point', 'At the mean'], 1, 'Spread out, but random.', 'P &prop; D(x)<sup>2</sup>.')
K.quiz('m', 'On two interleaved half moons, k-means', ['Finds them perfectly', 'Cuts straight across them', 'Refuses to run', 'Finds three clusters'], 1, 'Straight boundaries.', 'It assumes round clusters.')
K.quiz('h', 'The boundary between two k-means clusters is', ['A circle', 'The perpendicular bisector of the two centres (a straight line)', 'A curve fitted to the data', 'Random'], 1, 'Nearest centre.', 'Points equidistant from both centres form a straight line.')
K.quiz('h', 'k-means is a special case of EM for a Gaussian mixture with', ['Full covariances', 'Equal spherical variances shrinking to zero (hard assignments)', 'One component', 'Different priors'], 1, 'Hard instead of soft.', 'Soft responsibilities become 0 or 1.')
K.quiz('h', 'One extreme outlier in a cluster', ['Has no effect', 'Pulls that cluster’s mean towards it', 'Is ignored by k-means', 'Creates a new cluster automatically'], 1, 'Squared distance.', 'The mean is sensitive to outliers. k-medoids is more robust.')
K.quiz('x', 'In the style of a Stanford CS229 exam: why does Lloyd’s algorithm terminate?', ['It uses gradient descent with a small step', 'J never increases and there are finitely many assignments', 'k is small', 'It stops after 300 rounds only'], 1, 'Coordinate descent.', 'A strictly decreasing J cannot revisit an assignment.')
K.quiz('x', 'In the style of a CMU 10-701 exam: the global minimum of the k-means objective is', ['Found by Lloyd’s algorithm', 'NP hard to find in general', 'Always the k-means++ start', 'Zero'], 1, 'Aloise and others (2009).', 'Hard even for k = 2 in general dimension.')

K.calc('e', 'Points (0, 0) and (2, 0) with centre (1, 0). Inertia?', '2', 'Squared distances.', ['First point: 1<sup>2</sup> = 1.', 'Second point: 1<sup>2</sup> = 1.', eq('1 + 1 = 2')], check=2)
K.calc('e', 'Centre of (1, 2), (3, 4), (5, 6). Its x coordinate?', '3', 'Mean of x.', ['x values 1, 3, 5.', 'Sum 9.', eq('9 / 3 = 3')], check=3)
K.calc('e', 'Squared distance from (1, 1) to (4, 5)?', '25', '&Delta;x<sup>2</sup> + &Delta;y<sup>2</sup>.', ['&Delta;x = 3, &Delta;y = 4.', '9 + 16.', eq('25')], check=25)
K.calc('m', 'a = 2, b = 5. Silhouette of the point?', '0.6', '(b &minus; a)/max(a, b).', ['b &minus; a = 3.', 'max = 5.', eq('3 / 5 = 0.6')], check=0.6)
K.calc('m', 'a = 4, b = 3. Silhouette?', '-0.25', 'Negative means probably misassigned.', ['b &minus; a = &minus;1.', 'max = 4.', eq('&minus;1 / 4 = &minus;0.25')], check=-0.25)
K.calc('m', '1,000 points, k = 5. Distances computed in one assign step?', '5000', 'n &times; k.', ['Each point to each centre.', '1,000 &times; 5.', eq('5,000')], check=5000)
K.calc('m', 'Inertia falls from 1,000 to 400 when k goes from 2 to 3. Percentage drop?', '60', '(old &minus; new)/old.', ['Drop 600.', '600 / 1,000 = 0.6.', eq('60%')], check=60)
K.calc('h', 'k-means++: remaining points have D<sup>2</sup> = 1, 4, 5. Chance the last one is chosen?', '0.5', 'D<sup>2</sup> / total.', ['Total 10.', 'Its weight 5.', eq('5 / 10 = 0.5')], check=0.5)
K.calc('h', '20,000 rows, MiniBatchKMeans batch size 1,000. Batches to see every row once?', '20', 'n / batch.', ['20,000 rows.', '1,000 per batch.', eq('20')], check=20)
K.calc('x', 'In the style of an MIT 6.036 problem: how many ways can 10 distinct points be split into 2 non empty unlabelled clusters?', '511', '(2<sup>n</sup> &minus; 2)/2.', ['2<sup>10</sup> = 1,024 labelled assignments.', 'Remove the 2 with an empty cluster: 1,022.', eq('Divide by 2 for unlabelled: 511')], check=511)

K.assign('assign', 'e', 'The assign step',
         '<p>Write <code>assign(points, centres)</code> where both are lists of [x, y]. Return a list with the index of the nearest centre (smallest squared distance) for each point. On a tie take the lower index.</p>',
         '''
def assign(points, centres):
    # your code here
    pass
''', [('assign([[1, 1], [6, 6], [1, 7]], [[1, 1], [6, 6]])', [0, 1, 1]), ('assign([[0, 0]], [[1, 0], [-1, 0]])', [0]), ('assign([[5, 5], [0, 1]], [[0, 0], [5, 4], [9, 9]])', [1, 0])],
         '''
def assign(points, centres):
    labels = []
    for px, py in points:
        best = 0
        best_d = None
        for k, (cx, cy) in enumerate(centres):
            d = (px - cx) ** 2 + (py - cy) ** 2
            if best_d is None or d < best_d:
                best, best_d = k, d
        labels.append(best)
    return labels
''', 'For each point, compute the squared distance to every centre and keep the smallest.', '<p>[1, 7] is 36 from [1, 1] but 26 from [6, 6], so it joins centre 1 even though it looks closer to the left group.</p>')
K.assign('update', 'm', 'The update step',
         '<p>Write <code>update(points, labels, k)</code> that returns the k centres, each the mean [x, y] of its points, rounded to 4 decimals. A cluster with no points keeps [0.0, 0.0].</p>',
         '''
def update(points, labels, k):
    # your code here
    pass
''', [('update([[1, 1], [3, 3], [10, 10]], [0, 0, 1], 2)', [[2.0, 2.0], [10.0, 10.0]]), ('update([[0, 0], [1, 2]], [1, 1], 2)', [[0.0, 0.0], [0.5, 1.0]]), ('update([[1, 2], [2, 4], [3, 6]], [0, 0, 0], 1)', [[2.0, 4.0]])],
         '''
def update(points, labels, k):
    centres = []
    for j in range(k):
        mine = [p for p, l in zip(points, labels) if l == j]
        if not mine:
            centres.append([0.0, 0.0])
        else:
            centres.append([round(sum(p[0] for p in mine) / len(mine), 4), round(sum(p[1] for p in mine) / len(mine), 4)])
    return centres
''', 'Collect the points of each cluster and average each coordinate.', '<p>scikit-learn instead moves an empty cluster’s centre to a far point, so that no cluster stays empty.</p>')
K.assign('silhouette', 'e', 'Silhouette of one point',
         '<p>Write <code>silhouette(a, b)</code> where a is the mean distance to the point’s own cluster and b to the nearest other cluster. Return (b &minus; a) / max(a, b), rounded to 4 decimals, or 0.0 if both are 0.</p>',
         '''
def silhouette(a, b):
    # your code here
    pass
''', [('silhouette(2, 5)', 0.6), ('silhouette(4, 3)', -0.25), ('silhouette(0, 0)', 0.0)],
         '''
def silhouette(a, b):
    if a == 0 and b == 0:
        return 0.0
    return round((b - a) / max(a, b), 4)
''', 'One formula with a guard for zero.', '<p>A negative value suggests the point would fit better in the other cluster.</p>')

K.must('Algorithm', 'Choose k centres. Repeat: assign each point to the nearest centre, move each centre to its points’ mean. Minimises inertia &Sigma;|x &minus; &mu;|<sup>2</sup>.')
K.must('Local minima', 'Always converges, not always to the best. k-means++ starts (P &prop; D<sup>2</sup>) and n_init &gt; 1.')
K.must('Choosing k', 'Elbow of inertia vs k, silhouette (b &minus; a)/max(a, b) in [&minus;1, 1], plus the purpose of the clusters.')
K.must('Practice', 'Scale features. KMeans(n_clusters, n_init, random_state). predict for new points. MiniBatchKMeans for big data.')
K.must('Limits', 'Round, similar sized clusters. Straight boundaries. Outliers pull centres. Switch to DBSCAN, hierarchical or GMM.')
K.must('Theory', 'Coordinate descent, NP hard globally, hard assignment limit of EM for spherical Gaussians.')

T = K.topic(
    slug='ml-kmeans', topic='ml-kmeans', step=(1, 'Clustering', 'ml-u1', 'Find groups in data that has no labels: by centres, by trees of merges, by density and by probability.', 'Intermediate'),
    title='k-means: grouping points around centres', short='k-means', badge='1.1', minutes=50,
    lead='Learn the most used clustering method: Lloyd’s assign and update steps, inertia and local minima, k-means++ starts, choosing k with the elbow and silhouette, scaling, MiniBatchKMeans, and the data shapes where k-means fails.',
    desc='clustering, k-means, Lloyd algorithm, inertia, centroid, assign step, update step, local minimum, k-means++, n_init, elbow method, silhouette score, feature scaling, MiniBatchKMeans, adjusted Rand index, Voronoi, limitations.',
    summary='Assign and update, inertia and local minima, k-means++, choosing k, scaling, and when k-means fails.',
    keywords=['k-means', 'clustering', 'inertia', 'k-means++', 'elbow method', 'silhouette score', 'KMeans', 'MiniBatchKMeans', 'centroid', 'unsupervised learning'],
    recap='<p>k-means moves k centres until every point sits near its own. It is fast and simple, but needs k, scaled features and roughly round clusters.</p>',
    added='2026-11-13', leet=leet_items())
