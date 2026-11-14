# Unsupervised 1.2: hierarchical clustering and DBSCAN. Checked against Ward, Hierarchical Grouping to Optimize an
# Objective Function (JASA 1963), Sibson, SLINK (1973), Ester, Kriegel, Sander and Xu, A Density Based Algorithm for
# Discovering Clusters (KDD 1996), Ankerst and others, OPTICS (SIGMOD 1999), Campello, Moulavi and Sander, HDBSCAN
# (PAKDD 2013), Schubert and others, DBSCAN Revisited, Revisited (ACM TODS 2017), The Elements of Statistical Learning
# section 14.3.12, and the scikit-learn 1.8 and SciPy 1.18 documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-hierarchical')
K = Kit()

K.code('merge_by_hand', r'''
import numpy as np

# Six points on a line: two tight pairs, one loose pair
x = np.array([1.0, 2.0, 6.0, 7.0, 15.0, 18.0])
clusters = [[i] for i in range(len(x))]

def single_link(a, b):
    return min(abs(x[i] - x[j]) for i in a for j in b)

while len(clusters) > 1:
    best = None
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            d = single_link(clusters[i], clusters[j])
            if best is None or d < best[0]:
                best = (d, i, j)
    d, i, j = best
    merged = clusters[i] + clusters[j]
    print("merge", [x[k].item() for k in clusters[i]], "and", [x[k].item() for k in clusters[j]], "at distance", d.item())
    clusters = [c for k, c in enumerate(clusters) if k not in (i, j)] + [merged]
print("one cluster left with", len(clusters[0]), "points")
''', long=True)

K.code('scipy_tree', r'''
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster

x = np.array([[1.0], [2.0], [6.0], [7.0], [15.0], [18.0]])
Z = linkage(x, method="single")
print("each row: cluster a, cluster b, merge distance, size")
for row in Z:
    print([int(row[0]), int(row[1]), float(row[2]), int(row[3])])
print("cut the tree at height 3.5:", fcluster(Z, t=3.5, criterion="distance").tolist())
print("ask for exactly 2 clusters:", fcluster(Z, t=2, criterion="maxclust").tolist())
''')

K.code('linkages', r'''
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import make_blobs, make_moons
from sklearn.metrics import adjusted_rand_score

moons, ym = make_moons(n_samples=300, noise=0.05, random_state=0)
blobs, yb = make_blobs(n_samples=300, centers=3, cluster_std=[1.0, 2.5, 0.5], random_state=170)
for method in ["single", "complete", "average", "ward"]:
    a = AgglomerativeClustering(n_clusters=2, linkage=method).fit_predict(moons)
    b = AgglomerativeClustering(n_clusters=3, linkage=method).fit_predict(blobs)
    print(method.ljust(8), " moons ARI", round(adjusted_rand_score(ym, a), 3), "  uneven blobs ARI", round(adjusted_rand_score(yb, b), 3), " blob sizes", sorted(np.bincount(b).tolist(), reverse=True))
''', long=True)

K.code('dbscan_by_hand', r'''
import numpy as np

X = np.array([[1, 1], [1.5, 1], [1, 1.5], [1.5, 1.5], [2, 1.2],
              [6, 6], [6.5, 6], [6, 6.5], [6.4, 6.6],
              [4, 9], [9, 1]])
eps, min_pts = 0.8, 3
n = len(X)
near = [[j for j in range(n) if np.linalg.norm(X[i] - X[j]) <= eps] for i in range(n)]
core = [len(near[i]) >= min_pts for i in range(n)]       # neighbours include the point itself
print("core points:", [i for i in range(n) if core[i]])

label = [-1] * n
cluster = 0
for i in range(n):
    if not core[i] or label[i] != -1:
        continue
    label[i] = cluster
    queue = [i]
    while queue:                                         # grow the cluster through core points
        p = queue.pop()
        for q in near[p]:
            if label[q] == -1:
                label[q] = cluster
                if core[q]:
                    queue.append(q)
    cluster = cluster + 1
print("labels:", label)
print("clusters found:", cluster, " noise points:", [i for i in range(n) if label[i] == -1])
''', long=True)

K.code('sklearn_dbscan', r'''
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.datasets import make_moons
from sklearn.metrics import adjusted_rand_score

X, y = make_moons(n_samples=300, noise=0.06, random_state=1)
rng = np.random.default_rng(0)
X = np.vstack([X, rng.uniform(-1.5, 2.5, size=(15, 2))])   # add 15 random noise points
y = np.concatenate([y, -np.ones(15, dtype=int)])

db = DBSCAN(eps=0.2, min_samples=5).fit(X)
lab = db.labels_
print("clusters:", len(set(lab)) - (1 if -1 in lab else 0), " points marked noise:", int((lab == -1).sum()))
print("core points:", len(db.core_sample_indices_))
real = y != -1
print("DBSCAN ARI on the moons:", round(adjusted_rand_score(y[real], lab[real]), 3))
km = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X)
print("k-means ARI on the moons:", round(adjusted_rand_score(y[real], km[real]), 3))
''')

K.code('choose_eps', r'''
import numpy as np
from sklearn.datasets import make_moons
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN

X, _ = make_moons(n_samples=300, noise=0.06, random_state=1)
k = 5                                                   # same as min_samples
dist, _ = NearestNeighbors(n_neighbors=k).fit(X).kneighbors(X)
kth = np.sort(dist[:, -1])                              # distance to the 5th neighbour (itself counts as one)
for q in [50, 75, 90, 95, 99, 100]:
    print("percentile", str(q).rjust(3), " 5th neighbour distance", round(float(np.percentile(kth, q)), 3))
for eps in [0.05, 0.1, 0.2, 0.4, 1.0]:
    lab = DBSCAN(eps=eps, min_samples=k).fit_predict(X)
    print("eps", str(eps).ljust(4), " clusters", len(set(lab)) - (1 if -1 in lab else 0), " noise", int((lab == -1).sum()))
''', long=True)

K.code('densities', r'''
from sklearn.cluster import DBSCAN, HDBSCAN, OPTICS
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score

# A tight group, a wide group and a medium group
X, y = make_blobs(n_samples=[200, 200, 100], centers=[[0, 0], [7, 0], [3, 6]], cluster_std=[0.25, 1.8, 0.5], random_state=4)
for name, model in [("DBSCAN eps 0.3", DBSCAN(eps=0.3, min_samples=5)),
                    ("DBSCAN eps 1.0", DBSCAN(eps=1.0, min_samples=5)),
                    ("DBSCAN eps 1.5", DBSCAN(eps=1.5, min_samples=5)),
                    ("HDBSCAN", HDBSCAN(min_cluster_size=20, copy=True)),
                    ("OPTICS", OPTICS(min_samples=20, xi=0.05, min_cluster_size=0.1))]:
    lab = model.fit_predict(X)
    k = len(set(lab)) - (1 if -1 in lab else 0)
    print(name.ljust(15), " clusters", k, " noise", str(int((lab == -1).sum())).rjust(3), " ARI", round(adjusted_rand_score(y, lab), 3))
''', long=True)

K.lesson('idea', 'Hierarchical clustering: a tree of merges', f'''
{src('Ward (1963), Sibson, SLINK (1973), The Elements of Statistical Learning section 14.3.12, and the SciPy 1.18 cluster.hierarchy and scikit-learn 1.8 AgglomerativeClustering documentation.')}
{viz('mldendro')}
{wwh('<b>Agglomerative hierarchical clustering</b> starts with every point as its own cluster and repeatedly merges the two closest clusters until one is left. The full history of merges is a tree called a <b>dendrogram</b>. Cutting the tree at some height gives a flat clustering.',
     'It needs no k in advance: one run holds every clustering from n clusters down to 1, and the dendrogram shows how strongly the groups are separated. Many real groupings are nested (species inside a genus inside a family, or cities inside regions inside countries), and a tree shows that directly.',
     'Compute all pairwise distances. Merge the closest pair of clusters, then update the distances from the new cluster to the others using a <b>linkage</b> rule. Repeat n &minus; 1 times. Cut where the jump in merge height is largest, or where you get the number of clusters you need.')}
{run('merge_by_hand')}
{note('Six points need exactly five merges. The first three merges join close pairs at distance 1 or 3. Then the jumps grow: 4 and finally 8. The big jump from 4 to 8 says the data has two natural groups at the top level, and the gap from 1 to 3 says three groups also make sense.', 'exam')}
{run('scipy_tree')}
{note('SciPy writes the tree as a table Z with one row per merge. Original points are numbered 0 to 5, and the cluster made by row r gets the number 6 + r. fcluster cuts the tree, either at a height or to get a chosen number of clusters.', 'tip')}
{scene('a family tree read backwards', '<p>Picture everyone at a big family reunion. First, siblings stand together. Then sibling groups join their cousins, then cousins join the wider family, until everyone is one family. A photo taken at any moment of that process is one clustering. The dendrogram is the whole album.</p>')}
''', kw=['hierarchical clustering', 'agglomerative clustering', 'dendrogram', 'linkage matrix', 'fcluster', 'cutting the tree'])

K.lesson('linkage', 'Linkage: how far apart are two clusters?', f'''
{wwh('The <b>linkage</b> decides the distance between two clusters. <b>Single</b> uses the closest pair of points, <b>complete</b> the farthest pair, <b>average</b> the mean over all pairs, and <b>Ward</b> the increase in total squared error caused by the merge.',
     'The linkage changes the result more than anything else. Single linkage follows chains and finds long, curved shapes, but one stray point can bridge two groups. Complete and Ward prefer compact, round groups of similar size. Ward is the default in scikit-learn.',
     'AgglomerativeClustering(n_clusters=3, linkage="ward") or scipy.cluster.hierarchy.linkage(X, method="ward"). Ward needs Euclidean distances. The others accept any distance, so you can cluster with cosine or edit distance through a precomputed matrix.')}
{run('linkages')}
{note('Single linkage follows the two moons perfectly (ARI 1.0) because each moon is a chain of close points. On the blobs it fails completely: it leaves 296 points in one cluster and makes two tiny clusters from 4 stray points. Ward does the opposite: worst on the moons, best on the blobs (0.808). There is no best linkage, only a best linkage for the shape of your data.', 'exam')}
{table(['Linkage', 'Distance between clusters A and B', 'Good at', 'Weak at'], [
    ['Single', 'min over pairs d(a, b)', 'Long chains, curved shapes', 'Chaining through noise, unequal splits'],
    ['Complete', 'max over pairs d(a, b)', 'Compact groups', 'Sensitive to outliers, splits big groups'],
    ['Average', 'mean over pairs d(a, b)', 'A balance of the two', 'Still prefers round shapes'],
    ['Ward', 'rise in within cluster squared error', 'Round groups of similar size', 'Curved shapes, needs Euclidean distance']])}
{fx('Ward merge cost', '&Delta;(A, B) = (|A||B| / (|A| + |B|)) |&mu;<sub>A</sub> &minus; &mu;<sub>B</sub>|<sup>2</sup>', 'The rise in total squared error when A and B merge. It is the k-means objective, grown one merge at a time.', key=True)}
''', kw=['single linkage', 'complete linkage', 'average linkage', 'Ward linkage', 'chaining', 'AgglomerativeClustering'])

K.lesson('dbscan', 'DBSCAN: clusters are dense regions', f'''
{src('Ester, Kriegel, Sander and Xu, A Density Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise (KDD 1996), Schubert and others, DBSCAN Revisited, Revisited (ACM TODS 2017), and the scikit-learn 1.8 user guide section 2.3.7.')}
{viz('mldbscan')}
{wwh('<b>DBSCAN</b> (density based spatial clustering of applications with noise) defines a cluster as a dense region. A <b>core point</b> has at least minPts points within distance eps, counting itself. Core points within eps of each other join the same cluster. A non core point within eps of a core point is a <b>border point</b>. Every other point is <b>noise</b>.',
     'DBSCAN needs no k, finds clusters of any shape, and labels outliers as noise instead of forcing them into a cluster. That makes it a strong choice for maps and GPS points, sensor readings, and any data with odd shapes and stray points.',
     'Find the neighbours of every point within eps. Mark the core points. Start a cluster at any unvisited core point and keep adding the neighbours of every core point it reaches. Repeat until every core point has a cluster. Points left over are noise and get the label &minus;1.')}
{run('dbscan_by_hand')}
{note('Points 0 to 4 form one dense group and points 5 to 8 another, so all nine are core points and make two clusters. Points 9 and 10 have nobody within 0.8, so they are noise. Nobody asked for 2 clusters: the density alone decided it.', 'exam')}
{run('sklearn_dbscan')}
{note('DBSCAN recovers both moons perfectly (ARI 1.0 on the real points) and labels 12 of the 15 random points as noise. The other 3 landed close to a moon and joined it as border points. k-means on the same data cuts straight across the moons (ARI 0.241).', 'tip')}
{scene('finding towns on a night satellite photo', '<p>From space at night, a town is a bright patch where many lights are close together. A lone farmhouse is a single light with nobody nearby. DBSCAN finds towns the same way: a patch of points that are each close to several others is a cluster, whatever its shape, and a lonely light is noise.</p>')}
''', kw=['DBSCAN', 'density based clustering', 'core point', 'border point', 'noise', 'eps', 'min_samples'])

K.lesson('eps', 'Choosing eps and minPts', f'''
{wwh('DBSCAN has two settings. <b>minPts</b> (min_samples in scikit-learn) is how many points make a region dense. <b>eps</b> is the radius of the neighbourhood. The <b>k distance plot</b> helps choose eps: sort every point’s distance to its k-th nearest neighbour and look for the knee where the curve shoots up.',
     'eps decides almost everything. Too small and most points become noise, with real clusters shattered into pieces. Too large and separate clusters merge into one. A good eps sits just above the distances inside clusters.',
     'Choose minPts first: a common rule is 2 &times; the number of features, and at least 4 or 5. Then compute each point’s distance to its minPts-th neighbour (counting itself, as scikit-learn does), sort, and set eps near the knee. Scale the features first, because eps is one radius for every direction.')}
{run('choose_eps')}
{note('Half the points have their 5th neighbour within 0.079 and 99% within 0.179, then the largest is 0.285. That knee suggests eps around 0.2, which gives exactly 2 clusters and no noise. At 0.1 the moons break into 8 pieces with 16 noise points, at 0.05 almost everything is noise, and from 0.4 the two moons merge into one cluster.', 'exam')}
{steps('A quick recipe for DBSCAN settings', [
    'Scale the features, for example with StandardScaler.',
    'Set minPts to about 2 &times; the number of features (at least 4).',
    'Plot the sorted distance to the minPts-th neighbour.',
    'Set eps at the knee of that curve.',
    'Check the number of clusters and the share of noise. More than a few percent of noise in clean data usually means eps is too small.'])}
''', kw=['choosing eps', 'k distance plot', 'minPts', 'min_samples', 'knee', 'NearestNeighbors'])

K.lesson('hdbscan', 'Clusters of different density: HDBSCAN and OPTICS', f'''
{src('Campello, Moulavi and Sander, Density Based Clustering Based on Hierarchical Density Estimates (PAKDD 2013), Ankerst and others, OPTICS (SIGMOD 1999), and the scikit-learn 1.8 HDBSCAN and OPTICS documentation.')}
{wwh('DBSCAN uses one eps for the whole dataset, so it struggles when clusters have different densities. <b>HDBSCAN</b> runs DBSCAN for every eps at once, builds a tree of the dense regions, and keeps the clusters that stay stable across many eps values. <b>OPTICS</b> orders the points so that a single <b>reachability plot</b> shows the clusters at every density as valleys.',
     'Real data rarely has one density: a city centre is much denser than its suburbs. HDBSCAN needs only one easy setting, the smallest cluster size you care about, and it is often the best first choice for density based clustering.',
     'HDBSCAN(min_cluster_size=20).fit_predict(X), available in scikit-learn since version 1.3. OPTICS(min_samples=20, xi=0.05) extracts clusters from steep drops in the reachability plot.')}
{run('densities')}
{note('With one tight, one wide and one medium group, eps 0.3 suits the tight group but shatters the wide one into pieces (8 clusters, 161 noise points). eps 1.5 suits the wide group but merges two groups (2 clusters). eps 1.0 happens to work here, but you only know that because the true labels are known. HDBSCAN finds the 3 groups (ARI 0.952) without any eps, and OPTICS also finds 3 (ARI 0.94).', 'exam')}
{deep('How HDBSCAN builds its tree', '<p>HDBSCAN replaces the plain distance with the <b>mutual reachability distance</b> d<sub>mreach</sub>(a, b) = max(core(a), core(b), d(a, b)), where core(a) is the distance from a to its k-th neighbour. Points in sparse areas are pushed further from everything. It builds the minimum spanning tree of this distance, which is single linkage clustering, and turns it into a tree of clusters by removing edges from the longest down. Each cluster gets a <b>stability</b> score: how long its points stay in it as the density threshold rises. It then picks the set of non overlapping clusters with the highest total stability. Clusters smaller than min_cluster_size are treated as points falling out of a cluster, not as new clusters.</p>')}
''', kw=['HDBSCAN', 'OPTICS', 'varying density', 'reachability plot', 'mutual reachability distance', 'cluster stability'])

K.lesson('versus', 'Hierarchical and density methods compared', f'''
{versus('Choosing among clustering methods', ['', 'k-means', 'Agglomerative (Ward)', 'Agglomerative (single)', 'DBSCAN', 'HDBSCAN'], [
    ['Needs k', 'Yes', 'No (cut later)', 'No (cut later)', 'No', 'No'],
    ['Main settings', 'k', 'linkage, cut', 'cut', 'eps, minPts', 'min_cluster_size'],
    ['Cluster shape', 'Round', 'Round', 'Any, chains', 'Any', 'Any'],
    ['Marks noise', 'No', 'No', 'No', 'Yes', 'Yes'],
    ['Different densities', 'Poor', 'Fair', 'Poor', 'Poor', 'Good'],
    ['Cost for n points', 'About n &times; k per round', 'n<sup>2</sup> memory, up to n<sup>3</sup> time', 'n<sup>2</sup> (SLINK)', 'About n log n with an index', 'About n log n']],
    'use k-means or Ward for round groups, DBSCAN or HDBSCAN for odd shapes and noise, and a dendrogram when you want to see nested structure.')}
{table(['Question', 'Answer'], [
    ['Is k-means a special case of agglomerative clustering?', 'No. Ward uses the same squared error objective, but merges greedily and never moves a point back. The two can give different answers.'],
    ['Is single linkage related to DBSCAN?', 'Yes. Single linkage cut at height eps gives the connected groups of DBSCAN with minPts = 1 or 2, and HDBSCAN is single linkage on a density aware distance.'],
    ['Can DBSCAN predict a new point?', 'Not directly. scikit-learn DBSCAN has no predict. Assign a new point to the cluster of its nearest core point within eps, or noise otherwise.']])}
''', kw=['k-means vs DBSCAN', 'Ward vs single linkage', 'DBSCAN vs HDBSCAN', 'clustering comparison'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Single linkage', 'd(A, B) = min<sub>a&isin;A, b&isin;B</sub> d(a, b)', 'Closest pair.', key=True),
     fx('Complete linkage', 'd(A, B) = max<sub>a&isin;A, b&isin;B</sub> d(a, b)', 'Farthest pair.', key=True),
     fx('Average linkage', 'd(A, B) = (1 / |A||B|) &Sigma;<sub>a, b</sub> d(a, b)', 'Mean of all pairs.'),
     fx('Ward merge cost', '&Delta;(A, B) = |A||B| / (|A| + |B|) &middot; |&mu;<sub>A</sub> &minus; &mu;<sub>B</sub>|<sup>2</sup>', 'Rise in total squared error.', key=True),
     fx('eps neighbourhood', 'N<sub>&epsilon;</sub>(p) = {{ q : d(p, q) &le; &epsilon; }}', 'Includes p itself.', key=True),
     fx('Core point', '|N<sub>&epsilon;</sub>(p)| &ge; minPts', 'Dense enough to grow a cluster.', key=True),
     fx('Mutual reachability (HDBSCAN)', 'd<sub>m</sub>(a, b) = max(core<sub>k</sub>(a), core<sub>k</sub>(b), d(a, b))', 'Pushes sparse points apart.'))}
{steps('Worked example: one Ward merge cost', [
    'Cluster A has 2 points with mean (0, 0). Cluster B has 3 points with mean (3, 4).',
    'The squared distance between the means is 3<sup>2</sup> + 4<sup>2</sup> = 25.',
    'The size factor is (2 &times; 3) / (2 + 3) = 6 / 5 = 1.2.',
    eq('&Delta;(A, B) = 1.2 &times; 25 = 30'),
    'Merging A and B raises the total within cluster squared error by 30. Ward merges the pair with the smallest such rise.'])}
{deep('Single linkage is the minimum spanning tree', '<p>Build the minimum spanning tree (MST) of the points, with edge weights equal to distances. Kruskal’s algorithm adds edges from shortest to longest, joining two components each time, and that is exactly the sequence of single linkage merges with the same heights. So the single linkage clustering with k clusters is the MST with its k &minus; 1 longest edges removed. This also explains chaining: one short edge through a stray point is enough to join two groups. The <b>cophenetic distance</b> between two points is the height at which they first share a cluster, and the correlation between cophenetic and original distances measures how faithfully a dendrogram represents the data.</p>')}
''', kw=['linkage formulas', 'Ward formula', 'eps neighbourhood', 'core point definition', 'minimum spanning tree', 'cophenetic distance'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Hierarchical clustering joins the closest groups again and again and draws the joins as a tree. DBSCAN finds groups as crowded areas and leaves lonely points out as noise.</p>',
    '<p>Draw and cut a dendrogram, pick a linkage for the shape of your data, run DBSCAN with eps from the k distance plot, and use HDBSCAN when densities differ.</p>',
    '<p>Explain the four linkages and their failure modes, the link between single linkage and the MST, the definitions of core, border and noise points, and the complexity of each method.</p>',
    '<p>Study the Lance and Williams update formula that covers every linkage, the stability based cluster extraction of HDBSCAN, OPTICS reachability theory, density level set estimation, and why DBSCAN worst case cost is quadratic.</p>')}
{grow('Explain trees of merges and dense regions.',
      'Cluster odd shaped and noisy data with sensible settings.',
      'Analyse linkages, density definitions and costs.')}
''', kw=['beginner', 'expert', 'Lance Williams', 'density level sets'])

lc(1971, 'Find if Path Exists in Graph', 'find-if-path-exists-in-graph', 'e', 'Union find or a flood fill from the source', 'Join the two ends of every edge with union find, then check whether source and destination have the same root. Being in the same connected group is how DBSCAN decides that two core points share a cluster.', r"""
def valid_path(n, edges, source, destination):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        parent[find(a)] = find(b)
    return find(source) == find(destination)
""", [('valid_path(3, [[0, 1], [1, 2], [2, 0]], 0, 2)', True), ('valid_path(6, [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], 0, 5)', False)])
lc(990, 'Satisfiability of Equality Equations', 'satisfiability-of-equality-equations', 'm', 'Merge all equalities first, then test the inequalities', 'Put every pair joined by == into the same group with union find. Then each != must link two different groups, or the equations contradict each other.', r"""
def equations_possible(equations):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for e in equations:
        if e[1] == "=":
            parent[find(e[0])] = find(e[3])
    return all(find(e[0]) != find(e[3]) for e in equations if e[1] == "!")
""", [('equations_possible(["a==b", "b!=a"])', False), ('equations_possible(["a==b", "b==c", "a==c"])', True), ('equations_possible(["a==b", "b!=c", "c==a"])', False)])
lc(684, 'Redundant Connection', 'redundant-connection', 'm', 'The first edge that joins two nodes already in one group', 'Add the edges in order with union find. An edge whose two ends already share a root closes a cycle, so it is the answer. Kruskal’s minimum spanning tree, and so single linkage clustering, skip exactly these edges.', r"""
def find_redundant_connection(edges):
    parent = list(range(len(edges) + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return [a, b]
        parent[ra] = rb
    return []
""", [('find_redundant_connection([[1, 2], [1, 3], [2, 3]])', [2, 3]), ('find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]])', [1, 4])])
lc(1319, 'Number of Operations to Make Network Connected', 'number-of-operations-to-make-network-connected', 'm', 'Count the groups, then count the spare cables', 'n computers need at least n &minus; 1 cables, otherwise the answer is &minus;1. With enough cables, joining g separate groups takes g &minus; 1 moves.', r"""
def make_connected(n, connections):
    if len(connections) < n - 1:
        return -1
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    groups = n
    for a, b in connections:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            groups = groups - 1
    return groups - 1
""", [('make_connected(4, [[0, 1], [0, 2], [1, 2]])', 1), ('make_connected(6, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]])', 2), ('make_connected(6, [[0, 1], [0, 2], [0, 3], [1, 2]])', -1)])
lc(721, 'Accounts Merge', 'accounts-merge', 'm', 'Union the emails inside each account', 'Every email is a node. Join all emails of one account. Emails that end up with the same root belong to one person. This is clustering by shared links, just as DBSCAN joins clusters through shared core points.', r"""
def accounts_merge(accounts):
    parent, owner = {}, {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for acc in accounts:
        name, first = acc[0], acc[1]
        for email in acc[1:]:
            owner[email] = name
            parent[find(email)] = find(first)
    groups = {}
    for email in owner:
        groups.setdefault(find(email), []).append(email)
    return sorted([owner[g[0]]] + sorted(g) for g in groups.values())
""", [('accounts_merge([["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"], ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]])', [['John', 'john00@mail.com', 'john_newyork@mail.com', 'johnsmith@mail.com'], ['John', 'johnnybravo@mail.com'], ['Mary', 'mary@mail.com']])])
lc(827, 'Making A Large Island', 'making-a-large-island', 'h', 'Label every island with its size, then try each water cell', 'Flood fill each island and store its size under a new id. For each water cell, add 1 to the sizes of the distinct islands around it. One changed cell can bridge two groups, which is exactly how single linkage chains clusters together.', r"""
def largest_island(grid):
    n = len(grid)
    size = {}
    label = [[0] * n for _ in range(n)]
    next_id = 2
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1 and label[r][c] == 0:
                stack = [(r, c)]
                label[r][c] = next_id
                count = 0
                while stack:
                    i, j = stack.pop()
                    count = count + 1
                    for a, b in [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]:
                        if 0 <= a < n and 0 <= b < n and grid[a][b] == 1 and label[a][b] == 0:
                            label[a][b] = next_id
                            stack.append((a, b))
                size[next_id] = count
                next_id = next_id + 1
    best = max(size.values(), default=0)
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                ids = set()
                for a, b in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
                    if 0 <= a < n and 0 <= b < n and label[a][b]:
                        ids.add(label[a][b])
                best = max(best, 1 + sum(size[i] for i in ids))
    return best
""", [('largest_island([[1, 0], [0, 1]])', 3), ('largest_island([[1, 1], [1, 0]])', 4), ('largest_island([[1, 1], [1, 1]])', 4)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Both methods in this chapter join points into connected groups. These problems practise union find (the data structure behind single linkage and DBSCAN cluster growth), detecting the edge that closes a cycle as Kruskal’s algorithm does, merging records through shared links, and how one bridging cell joins two groups. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'union find', 'connected components', 'Kruskal', 'flood fill'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Agglomerative clustering</b> merges the two closest clusters n &minus; 1 times. The <b>dendrogram</b> records every merge, and a cut gives any number of clusters.',
    'The <b>linkage</b> matters most: single follows chains but bridges through noise, complete and Ward prefer compact round groups, Ward is the default.',
    '<b>DBSCAN</b>: core points have at least minPts neighbours within eps. Clusters grow through core points, border points join, the rest is <b>noise</b> (label &minus;1).',
    'Choose minPts around 2 &times; the number of features and eps at the knee of the k distance plot. Scale the features first.',
    'One eps cannot fit clusters of very different density. <b>HDBSCAN</b> handles that with a single setting, min_cluster_size.',
    'Agglomerative clustering costs n<sup>2</sup> memory, so it suits thousands of points, while DBSCAN and HDBSCAN scale much further.'],
    'Unsupervised 1.3 covers Gaussian mixture models and the EM algorithm: soft clustering with probabilities.')}
{files('Three tasks: single linkage distance, finding the core points, and a full DBSCAN.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Agglomerative clustering starts with', ['One big cluster', 'Every point as its own cluster', 'k random centres', 'Only the core points'], 1, 'Bottom up.', 'It merges upwards until one cluster is left.')
K.quiz('e', 'A dendrogram shows', ['The loss per epoch', 'Every merge and the distance at which it happened', 'Feature importances', 'The decision boundary'], 1, 'A tree.', 'Cut it to get a flat clustering.')
K.quiz('e', 'In DBSCAN a point with label &minus;1 is', ['The first cluster', 'Noise', 'A core point', 'A centre'], 1, 'Left out.', 'It belongs to no cluster.')
K.quiz('e', 'Which method needs the number of clusters in advance?', ['DBSCAN', 'k-means', 'HDBSCAN', 'Agglomerative with a distance cut'], 1, 'Only one.', 'The others find it from the data or from the cut.')
K.quiz('m', 'Single linkage measures the distance between two clusters by', ['Their farthest pair', 'Their closest pair', 'Their means', 'Their sizes'], 1, 'Single link.', 'One close pair is enough.')
K.quiz('m', 'Which linkage is most likely to chain two groups through a few stray points?', ['Ward', 'Complete', 'Single', 'Average'], 2, 'Closest pair.', 'One short bridge joins everything.')
K.quiz('m', 'A DBSCAN border point is', ['A point with no neighbours', 'A non core point within eps of a core point', 'Any core point', 'The farthest point of a cluster'], 1, 'Reached but not dense.', 'It joins the cluster but cannot grow it.')
K.quiz('m', 'If eps is far too large, DBSCAN tends to', ['Mark everything as noise', 'Merge separate clusters into one', 'Need more memory only', 'Become k-means'], 1, 'Neighbourhoods everywhere.', 'Every point reaches every other.')
K.quiz('m', 'The k distance plot is used to choose', ['k for k-means', 'eps for DBSCAN', 'The linkage', 'The learning rate'], 1, 'Knee.', 'Set eps where the sorted distances shoot up.')
K.quiz('h', 'Why does DBSCAN struggle when clusters have very different densities?', ['It needs k', 'One eps cannot suit both the dense and the sparse clusters', 'It is too slow', 'It only finds round clusters'], 1, 'One radius.', 'HDBSCAN removes the single eps.')
K.quiz('h', 'Single linkage clustering with k clusters equals', ['k-means with k centres', 'The minimum spanning tree with its k &minus; 1 longest edges removed', 'Ward with k clusters', 'DBSCAN with minPts = k'], 1, 'Kruskal.', 'The merge order is the MST edge order.')
K.quiz('h', 'Why does Ward need Euclidean distances?', ['It is faster', 'Its cost is a rise in squared error around means, which assumes Euclidean geometry', 'scikit-learn forbids others', 'It sorts the points'], 1, 'Means and variance.', 'Other linkages accept any distance.')
K.quiz('x', 'In the style of a CMU 10-701 exam: the memory needed by standard agglomerative clustering on n points grows like', ['n', 'n log n', 'n<sup>2</sup>', 'n<sup>3</sup>'], 2, 'The distance matrix.', 'n(n &minus; 1)/2 pairwise distances.')
K.quiz('x', 'In the style of a Stanford CS246 exam: which part of DBSCAN’s output can change with the order in which points are visited?', ['The core points', 'The noise points', 'Which cluster a border point near two clusters joins', 'The number of core points'], 2, 'Ester and others (1996).', 'Core points and noise do not depend on order.')

K.calc('e', 'Points on a line: A = {1, 2}, B = {6, 7}. Single linkage distance?', '4', 'Closest pair.', ['Pairs: 1 to 6 is 5, 1 to 7 is 6, 2 to 6 is 4, 2 to 7 is 5.', 'The smallest is 2 to 6.', eq('d = 4')], check=4)
K.calc('e', 'Same clusters. Complete linkage distance?', '6', 'Farthest pair.', ['Pair distances 5, 6, 4, 5.', 'The largest is 1 to 7.', eq('d = 6')], check=6)
K.calc('e', 'Same clusters. Average linkage distance?', '5', 'Mean of all pairs.', ['Pair distances 5, 6, 4, 5.', 'Sum 20 over 4 pairs.', eq('20 / 4 = 5')], check=5)
K.calc('m', 'How many merges does agglomerative clustering make on 10 points?', '9', 'Each merge removes one cluster.', ['Start with 10 clusters.', 'End with 1.', eq('10 &minus; 1 = 9')], check=9)
K.calc('m', 'How many pairwise distances for 20,000 points?', '199990000', 'n(n &minus; 1)/2.', ['n = 20,000.', '20,000 &times; 19,999 = 399,980,000.', eq('399,980,000 / 2 = 199,990,000')], check=199990000)
K.calc('m', 'A point has 4 other points within eps. Counting itself, how many points are in its neighbourhood?', '5', 'scikit-learn counts the point itself.', ['4 neighbours.', 'Add the point itself.', eq('5, so it is core when minPts &le; 5')], check=5)
K.calc('m', 'Ward merge cost of two single points (0, 0) and (3, 4)?', '12.5', '|A||B|/(|A| + |B|) times the squared distance.', ['Size factor 1 &times; 1 / 2 = 0.5.', 'Squared distance 9 + 16 = 25.', eq('0.5 &times; 25 = 12.5')], check=12.5)
K.calc('h', 'Ward merge cost: |A| = 2, |B| = 3, the means are 5 apart.', '30', 'Size factor times squared distance.', ['Size factor 6 / 5 = 1.2.', 'Squared distance 25.', eq('1.2 &times; 25 = 30')], check=30)
K.calc('h', 'Rule of thumb minPts = 2 &times; features. Data with 6 features?', '12', '2 &times; dimensions.', ['6 features.', 'Double it.', eq('minPts = 12')], check=12)
K.calc('x', 'In the style of a Stanford CS246 problem: 7 points, single linkage cut to 3 clusters. How many MST edges are kept?', '4', 'MST of n points has n &minus; 1 edges.', ['The MST has 7 &minus; 1 = 6 edges.', '3 clusters need the 2 longest edges removed.', eq('6 &minus; 2 = 4')], check=4)

K.assign('single_link', 'e', 'Single linkage distance',
         '<p>Write <code>single_link_distance(a, b)</code> where a and b are lists of [x, y] points. Return the smallest Euclidean distance between a point of a and a point of b, rounded to 4 decimals.</p>',
         """
def single_link_distance(a, b):
    # your code here
    pass
""", [('single_link_distance([[0, 0], [1, 0]], [[4, 0], [5, 0]])', 3.0), ('single_link_distance([[0, 0]], [[3, 4]])', 5.0), ('single_link_distance([[0, 0], [0, 2]], [[1, 1]])', 1.4142)],
         """
def single_link_distance(a, b):
    best = None
    for p in a:
        for q in b:
            d = ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5
            if best is None or d < best:
                best = d
    return round(best, 4)
""", 'Try every pair and keep the smallest distance.', '<p>Change min to max and you have complete linkage.</p>')
K.assign('core_points', 'm', 'Find the core points',
         '<p>Write <code>core_points(points, eps, min_pts)</code>. A point is core when at least min_pts points (counting itself) lie within distance eps (less than or equal). Return the indices of the core points in increasing order.</p>',
         """
def core_points(points, eps, min_pts):
    # your code here
    pass
""", [('core_points([[0, 0], [0, 1], [0, 2], [5, 5]], 1, 3)', [1]), ('core_points([[0, 0], [0, 1], [0, 2], [5, 5]], 1, 2)', [0, 1, 2]), ('core_points([[0, 0], [10, 10]], 1, 1)', [0, 1])],
         """
def core_points(points, eps, min_pts):
    result = []
    for i, p in enumerate(points):
        count = 0
        for q in points:
            if ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 <= eps:
                count = count + 1
        if count >= min_pts:
            result.append(i)
    return result
""", 'Count the neighbours of each point, itself included.', '<p>With min_pts = 1 every point is core, so every point starts its own cluster or joins one: there is no noise.</p>')
K.assign('dbscan_labels', 'h', 'DBSCAN from scratch',
         '<p>Write <code>dbscan_labels(points, eps, min_pts)</code> that returns a label for every point: &minus;1 for noise, and 0, 1, 2 and so on for clusters. Visit points in index order and start a new cluster at each unlabelled core point. A border point takes the label of the first cluster that reaches it.</p>',
         """
def dbscan_labels(points, eps, min_pts):
    # your code here
    pass
""", [('dbscan_labels([[0, 0], [0, 1], [0, 2], [5, 5], [5, 6], [5, 7], [9, 0]], 1.0, 2)', [0, 0, 0, 1, 1, 1, -1]), ('dbscan_labels([[0, 0], [0, 1], [0, 2], [3, 0]], 1, 3)', [0, 0, 0, -1]), ('dbscan_labels([[0, 0], [4, 4]], 1, 2)', [-1, -1])],
         """
def dbscan_labels(points, eps, min_pts):
    n = len(points)
    near = []
    for p in points:
        near.append([j for j, q in enumerate(points) if ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 <= eps])
    is_core = [len(nb) >= min_pts for nb in near]
    labels = [-1] * n
    cluster = 0
    for i in range(n):
        if not is_core[i] or labels[i] != -1:
            continue
        labels[i] = cluster
        queue = [i]
        while queue:
            p = queue.pop()
            for q in near[p]:
                if labels[q] == -1:
                    labels[q] = cluster
                    if is_core[q]:
                        queue.append(q)
        cluster = cluster + 1
    return labels
""", 'Find neighbours, mark core points, then grow each cluster with a queue of core points.', '<p>In the second test, only [0, 1] has 3 points within 1, so it is the only core point. [0, 0] and [0, 2] are border points, and [3, 0] is noise.</p>')

K.must('Agglomerative', 'Start with n clusters, merge the closest two n &minus; 1 times. Dendrogram of merge heights, cut at the biggest jump or at the k you need.')
K.must('Linkages', 'Single min (chains), complete max (compact), average mean, Ward rise in squared error (round, default, Euclidean only).')
K.must('DBSCAN', 'Core: at least minPts within eps (self included). Clusters grow through core points. Border joins, rest is noise &minus;1. No k, any shape.')
K.must('Settings', 'minPts about 2 &times; features. eps at the knee of the sorted k distance plot. Scale first.')
K.must('HDBSCAN and OPTICS', 'Handle different densities. HDBSCAN needs only min_cluster_size. OPTICS reachability plot valleys.')
K.must('Costs and theory', 'Agglomerative n<sup>2</sup> memory. Single linkage = MST. DBSCAN about n log n with an index, n<sup>2</sup> worst case.')

T = K.topic(
    slug='ml-hierarchical', topic='ml-hierarchical', step=(1, 'Clustering', 'ml-u1', 'Find groups in data that has no labels: by centres, by trees of merges, by density and by probability.', 'Intermediate'),
    title='Hierarchical clustering and DBSCAN', short='Hierarchical and DBSCAN', badge='1.2', minutes=50,
    lead='Cluster without choosing k: build a dendrogram of merges and cut it, compare single, complete, average and Ward linkage, find dense regions of any shape with DBSCAN, choose eps and minPts, and handle different densities with HDBSCAN and OPTICS.',
    desc='hierarchical clustering, agglomerative clustering, dendrogram, linkage matrix, single linkage, complete linkage, average linkage, Ward, chaining, DBSCAN, core point, border point, noise, eps, minPts, k distance plot, HDBSCAN, OPTICS, minimum spanning tree.',
    summary='Dendrograms and linkages, DBSCAN core, border and noise points, choosing eps, and HDBSCAN for different densities.',
    keywords=['hierarchical clustering', 'dendrogram', 'Ward linkage', 'single linkage', 'DBSCAN', 'HDBSCAN', 'OPTICS', 'eps', 'core point', 'density based clustering'],
    recap='<p>Agglomerative clustering builds a tree of merges you can cut anywhere. DBSCAN finds dense regions of any shape and leaves noise out, and HDBSCAN copes with different densities.</p>',
    added='2026-11-13', leet=leet_items())
