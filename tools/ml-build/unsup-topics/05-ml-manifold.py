# Unsupervised 2.2: manifold learning. Checked against Torgerson, Multidimensional Scaling (1952), Tenenbaum, de Silva
# and Langford, Isomap (Science 2000), Roweis and Saul, Locally Linear Embedding (Science 2000), Belkin and Niyogi,
# Laplacian Eigenmaps (2003), van der Maaten and Hinton, Visualizing Data using t-SNE (JMLR 2008), van der Maaten,
# Barnes-Hut t-SNE (JMLR 2014), Wattenberg, Viegas and Johnson, How to Use t-SNE Effectively (Distill 2016), McInnes,
# Healy and Melville, UMAP (2018), Venna and Kaski, trustworthiness (2001), and the scikit-learn 1.8 user guide 2.2.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-manifold')
K = Kit()

K.code('swiss_roll', r'''
from scipy.stats import spearmanr
from sklearn.datasets import make_swiss_roll
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap, LocallyLinearEmbedding, SpectralEmbedding

X, t = make_swiss_roll(n_samples=800, noise=0.05, random_state=0)   # a rolled up sheet in 3D, t = position along the roll
for name, model in [("PCA", PCA(n_components=2)),
                    ("Isomap", Isomap(n_neighbors=10, n_components=2)),
                    ("LLE", LocallyLinearEmbedding(n_neighbors=12, n_components=2, random_state=0)),
                    ("Spectral", SpectralEmbedding(n_neighbors=10, n_components=2, random_state=0))]:
    Z = model.fit_transform(X)
    rho = max(abs(spearmanr(Z[:, 0], t)[0]), abs(spearmanr(Z[:, 1], t)[0]))
    print(name.ljust(8), " how well one new axis follows the roll (rank correlation):", round(float(rho), 3))
''', long=True)

K.code('mds_map', r'''
import numpy as np
from sklearn.manifold import MDS

# Five towns: we only know the road distances between them, not where they are
names = ["A", "B", "C", "D", "E"]
true = np.array([[0, 0], [4, 0], [4, 3], [0, 3], [2, 6]], dtype=float)
D = np.sqrt(((true[:, None] - true[None]) ** 2).sum(axis=2))
print("distance matrix:", np.round(D, 1).tolist())
mds = MDS(n_components=2, metric="precomputed", metric_mds=True, init="classical_mds", n_init=1, random_state=0)
Z = mds.fit_transform(D)
Dz = np.sqrt(((Z[:, None] - Z[None]) ** 2).sum(axis=2))
print("largest error in any rebuilt distance:", round(float(np.abs(D - Dz).max()), 3))
print("A to E: true", round(float(D[0, 4]), 2), " rebuilt", round(float(Dz[0, 4]), 2))
''')

K.code('perplexity_sigma', r'''
import numpy as np

# How t-SNE turns one point's distances into neighbour probabilities with a chosen perplexity
d2 = np.array([1.0, 1.2, 1.5, 4.0, 9.0, 16.0, 25.0])     # squared distances to 7 other points
target = 3.0                                              # "about 3 effective neighbours"
lo, hi = 1e-3, 1e3
for step in range(50):                                    # binary search for the width sigma
    sigma = (lo + hi) / 2
    p = np.exp(-d2 / (2 * sigma ** 2))
    p = p / p.sum()
    perp = 2 ** (-(p * np.log2(p + 1e-300)).sum())        # perplexity = 2 to the entropy
    if perp > target:
        hi = sigma
    else:
        lo = sigma
print("sigma", round(float(sigma), 3), " perplexity", round(float(perp), 3))
print("neighbour probabilities:", np.round(p, 3).tolist())
''', long=True)

K.code('tsne_digits', r'''
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, trustworthiness
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

X, y = load_digits(return_X_y=True)
X, y = X[:600], y[:600]                                  # 600 images keep it quick in the browser
for name, Z in [("PCA", PCA(n_components=2).fit_transform(X)),
                ("t-SNE", TSNE(n_components=2, perplexity=30, init="pca", random_state=0).fit_transform(X))]:
    acc = cross_val_score(KNeighborsClassifier(5), Z, y, cv=5).mean()
    print(name.ljust(5), " 5 nearest neighbours accuracy in 2D", round(float(acc), 3), "  trustworthiness", round(float(trustworthiness(X, Z, n_neighbors=5)), 3))
''', long=True)

K.code('perplexity', r'''
from sklearn.datasets import load_digits
from sklearn.manifold import TSNE, trustworthiness
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

X, y = load_digits(return_X_y=True)
X, y = X[:400], y[:400]
for perp in [2, 10, 30, 100]:
    Z = TSNE(n_components=2, perplexity=perp, init="pca", random_state=0).fit_transform(X)
    acc = cross_val_score(KNeighborsClassifier(5), Z, y, cv=5).mean()
    print("perplexity", str(perp).rjust(3), " kNN accuracy", round(float(acc), 3), " trustworthiness", round(float(trustworthiness(X, Z, n_neighbors=10)), 3))
''', long=True)

K.code('tsne_pitfalls', r'''
import numpy as np
from sklearn.manifold import TSNE

rng = np.random.default_rng(0)
tight = rng.normal(0, 0.5, size=(150, 10))               # a tight cluster
wide = rng.normal(0, 5.0, size=(150, 10)) + 40           # a wide cluster far away
far = rng.normal(0, 0.5, size=(150, 10)) + 400           # a tight cluster very far away
X = np.vstack([tight, wide, far])
Z = TSNE(n_components=2, perplexity=30, init="pca", random_state=0).fit_transform(X)
spread = lambda A: float(np.sqrt(((A - A.mean(axis=0)) ** 2).sum(axis=1)).mean())
print("spread in 10D:  tight", round(spread(X[:150]), 1), "  wide", round(spread(X[150:300]), 1))
print("spread in 2D:   tight", round(spread(Z[:150]), 1), "  wide", round(spread(Z[150:300]), 1))
gap = lambda A, B: float(np.linalg.norm(A.mean(axis=0) - B.mean(axis=0)))
print("gap in 10D:  tight to wide", round(gap(X[:150], X[150:300]), 0), "  tight to far", round(gap(X[:150], X[300:]), 0))
print("gap in 2D:   tight to wide", round(gap(Z[:150], Z[150:300]), 0), "  tight to far", round(gap(Z[:150], Z[300:]), 0))
''')

K.lesson('idea', 'Manifolds, and distance along the data', f'''
{src('Tenenbaum, de Silva and Langford, Isomap (Science 2000), Roweis and Saul, Locally Linear Embedding (Science 2000), Belkin and Niyogi, Laplacian Eigenmaps (2003), and the scikit-learn 1.8 user guide section 2.2.')}
{viz('mlgeodesic')}
{wwh('A <b>manifold</b> is a low dimensional surface curled up inside a high dimensional space, like a sheet of paper rolled into a tube. <b>Manifold learning</b> finds coordinates on that surface. <b>Isomap</b> measures distance along the surface (the <b>geodesic distance</b>) as the shortest path through a nearest neighbour graph, then lays the points out so those distances are kept.',
     'Real data often has few true degrees of freedom: photos of a face turning have thousands of pixels but are controlled by a couple of angles. PCA only finds flat directions, so it cannot unroll curved structure. Manifold methods can, which makes them strong for pictures of complex data.',
     'Build a k nearest neighbour graph. Isomap computes shortest paths between all pairs and runs classical MDS on them. <b>LLE</b> rebuilds each point from its neighbours and keeps those weights in low dimensions. <b>Spectral embedding</b> (Laplacian eigenmaps) uses eigenvectors of the graph Laplacian so that linked points stay close.')}
{run('swiss_roll')}
{note('The swiss roll is a flat sheet rolled up in 3D. PCA squashes it flat and mixes the layers, so its best axis follows the position along the roll with a rank correlation of only 0.19. Isomap unrolls it almost perfectly (1.0), spectral embedding nearly so (0.998), and LLE reaches 0.916. All three need a sensible number of neighbours.', 'exam')}
{scene('walking around a mountain lake', '<p>Two villages sit on opposite shores of a lake. As the crow flies they are 2 km apart, but by the road around the shore it is 15 km. If you can only walk, the road distance is the one that matters. Isomap measures the road distance through the data instead of the straight line.</p>')}
''', kw=['manifold learning', 'manifold', 'geodesic distance', 'Isomap', 'LLE', 'spectral embedding', 'nearest neighbour graph', 'swiss roll'])

K.lesson('mds', 'Multidimensional scaling: a map from distances', f'''
{wwh('<b>Multidimensional scaling</b> (MDS) takes only a table of distances between items and finds positions in 2D (or any dimension) whose distances match the table as closely as possible. <b>Classical MDS</b> solves this exactly with an eigen decomposition, and <b>metric MDS</b> minimises the <b>stress</b>, the sum of squared differences between the given and the map distances.',
     'Sometimes you have distances but no features: how similar two products are, travel times between towns, or how often two words appear together. MDS turns those into a picture. Classical MDS on Euclidean distances gives exactly the same result as PCA.',
     'MDS(n_components=2, metric="precomputed", metric_mds=True, init="classical_mds") in scikit-learn 1.8, then fit_transform(D) on a square distance matrix. The map can come out rotated or mirrored, because distances do not change under those moves.')}
{run('mds_map')}
{note('From the 10 distances alone, MDS rebuilds the five towns so well that no distance is off by even 0.001, and A to E is 6.32 both ways. The rebuilt map may be turned or flipped compared with the true one, since nothing in a distance table fixes north.', 'tip')}
{fx('Stress', 'stress = &Sigma;<sub>i &lt; j</sub> (d<sub>ij</sub> &minus; |z<sub>i</sub> &minus; z<sub>j</sub>|)<sup>2</sup>', 'Given distances against map distances.', key=True)}
''', kw=['MDS', 'multidimensional scaling', 'classical MDS', 'stress', 'distance matrix', 'precomputed'])

K.lesson('tsne', 't-SNE: maps that keep neighbours together', f'''
{src('van der Maaten and Hinton, Visualizing Data using t-SNE (JMLR 2008), van der Maaten, Accelerating t-SNE using Tree-Based Algorithms (JMLR 2014), and the scikit-learn 1.8 TSNE documentation.')}
{viz('mltsne')}
{wwh('<b>t-SNE</b> (t-distributed stochastic neighbour embedding) makes 2D or 3D maps in which points that are neighbours in the original space stay neighbours. It turns distances into neighbour probabilities, with a Gaussian in high dimensions and a heavy tailed <b>Student t</b> curve in the map, and moves the map points to make the two sets of probabilities match.',
     't-SNE gives the clearest pictures of clusters in images, text embeddings, gene data and neural network features. It is a tool for looking and exploring, not for feeding a model.',
     'For each point, choose a Gaussian width so that the <b>perplexity</b> (the effective number of neighbours) equals the setting, often 5 to 50. Place the map points at random or from PCA, then run gradient descent on the KL divergence. Early steps exaggerate the pull between neighbours so clusters form first.')}
{run('perplexity_sigma')}
{note('The binary search finds the width 0.607 that gives a perplexity of exactly 3. The three nearest points share almost all the probability (0.437, 0.333, 0.222) and the far points get none. A larger perplexity would widen the Gaussian and spread the probability over more neighbours.', 'exam')}
{run('tsne_digits')}
{note('In a 2D PCA map of 600 digit images, the 5 nearest neighbours of a point share its digit only 57.7% of the time. In the t-SNE map they do 94.2% of the time, and the trustworthiness (how many map neighbours were real neighbours) is 0.995 against 0.834. t-SNE keeps local structure far better.', 'tip')}
{fxs(fx('High dimensional affinity', 'p<sub>j|i</sub> = exp(&minus;|x<sub>i</sub> &minus; x<sub>j</sub>|<sup>2</sup> / 2&sigma;<sub>i</sub><sup>2</sup>) / &Sigma;<sub>k&ne;i</sub> exp(&minus;|x<sub>i</sub> &minus; x<sub>k</sub>|<sup>2</sup> / 2&sigma;<sub>i</sub><sup>2</sup>)', 'p<sub>ij</sub> = (p<sub>j|i</sub> + p<sub>i|j</sub>) / 2n.', key=True),
     fx('Map affinity (Student t)', 'q<sub>ij</sub> = (1 + |y<sub>i</sub> &minus; y<sub>j</sub>|<sup>2</sup>)<sup>&minus;1</sup> / &Sigma;<sub>k&ne;l</sub> (1 + |y<sub>k</sub> &minus; y<sub>l</sub>|<sup>2</sup>)<sup>&minus;1</sup>', 'Heavy tails let far points sit far apart.', key=True),
     fx('Perplexity', 'Perp(P<sub>i</sub>) = 2<sup>H(P<sub>i</sub>)</sup>', 'H is the entropy in bits.', key=True))}
''', kw=['t-SNE', 'TSNE', 'perplexity', 'Student t distribution', 'KL divergence', 'early exaggeration', 'trustworthiness'])

K.lesson('pitfalls', 'Reading t-SNE maps without being fooled', f'''
{src('Wattenberg, Viegas and Johnson, How to Use t-SNE Effectively (Distill 2016).')}
{wwh('t-SNE keeps neighbours but deliberately distorts everything else. <b>Cluster sizes</b> and <b>distances between clusters</b> in the map carry little meaning. Different perplexities and random starts give different looking maps, and random noise can show apparent clusters at low perplexity.',
     'People often read a t-SNE map like a scatter plot of real coordinates and draw wrong conclusions, such as "this group is more varied" or "these two groups are related". Knowing what is and is not kept avoids that.',
     'Try several perplexities, use init="pca" for more stable global layout, run more than one seed, check clusters with a method that works in the original space, and never use t-SNE coordinates as features for a model. t-SNE has no transform for new points.')}
{run('perplexity')}
{note('On these 400 digits, neighbour accuracy stays between 0.985 and 0.992 for every perplexity from 2 to 100, and trustworthiness between 0.981 and 0.992. The local structure is robust. What changes is the look of the map: the size, shape and spacing of the clusters.', 'tip')}
{run('tsne_pitfalls')}
{note('In 10 dimensions the wide cluster is 10 times as spread as the tight one, but in the t-SNE map both have spread 4.3. The far cluster is 10 times farther than the wide one in 10D, but only about twice as far in the map. So the map tells you which points belong together, not how big groups are or how far apart.', 'exam')}
{table(['You see in the map', 'Can you trust it?'], [
    ['Points close together', 'Usually yes: they are close in the original space'],
    ['Separate islands', 'Often, but check at a few perplexities and seeds'],
    ['Big or small clusters', 'No: t-SNE evens out densities'],
    ['Distance between clusters', 'Only roughly, if at all'],
    ['Clusters in pure noise', 'Possible at low perplexity, so check']])}
''', kw=['t-SNE pitfalls', 'cluster size', 'global structure', 'perplexity choice', 'random seed', 'How to Use t-SNE Effectively'])

K.lesson('umap', 'UMAP and choosing a method', f'''
{src('McInnes, Healy and Melville, UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction (2018), and the umap-learn documentation.')}
{wwh('<b>UMAP</b> also builds a k nearest neighbour graph with fuzzy edge weights and then finds a low dimensional layout whose graph matches it, by minimising a cross entropy with stochastic gradient descent. Its two main settings are n_neighbors (default 15, local against global balance) and min_dist (default 0.1, how tightly points may pack).',
     'UMAP is usually much faster than t-SNE on large data, often keeps more of the global arrangement of clusters, and can transform new points after fitting. It has become the default for large single cell biology and embedding datasets.',
     'In Python it comes from the separate umap-learn package (umap.UMAP(n_neighbors=15, min_dist=0.1).fit_transform(X)). It is not part of scikit-learn and does not run in this browser page, so the programs here use t-SNE, Isomap and MDS. The same reading rules apply: trust neighbours, be careful with sizes and gaps.')}
{table(['Method', 'Keeps', 'New points', 'Scales to', 'Use it for'], [
    ['PCA', 'Global variance, linear', 'Yes', 'Millions', 'Compression, first look, preprocessing'],
    ['Classical MDS', 'All pairwise distances', 'No', 'Thousands', 'Maps from a distance table'],
    ['Isomap', 'Geodesic distances', 'Yes (approximate)', 'Thousands', 'Unrolling one smooth manifold'],
    ['LLE, spectral', 'Local neighbourhoods', 'Partly', 'Thousands', 'Smooth manifolds, clustering prep'],
    ['t-SNE', 'Local neighbours', 'No', 'Tens of thousands (Barnes-Hut)', 'Pictures of clusters'],
    ['UMAP', 'Local and some global', 'Yes', 'Millions', 'Pictures of large data, some preprocessing']])}
''', kw=['UMAP', 'n_neighbors', 'min_dist', 'umap-learn', 'choosing a dimensionality reduction method'])

K.lesson('versus', 'Manifold learning compared with PCA', f'''
{versus('PCA against nonlinear embeddings', ['', 'PCA', 'Isomap', 't-SNE', 'UMAP'], [
    ['Linear', 'Yes', 'No', 'No', 'No'],
    ['What it keeps', 'Variance', 'Path distances', 'Neighbours', 'Neighbour graph'],
    ['Deterministic', 'Yes', 'Yes', 'No (random start)', 'No (random start)'],
    ['Main setting', 'n_components', 'n_neighbors', 'perplexity', 'n_neighbors, min_dist'],
    ['Distances in output meaningful', 'Yes', 'Roughly', 'Only locally', 'Only locally'],
    ['Good as model input', 'Yes', 'Sometimes', 'No', 'Sometimes']],
    'start with PCA, then use t-SNE or UMAP for a picture of clusters, and Isomap when the data clearly lies on one smooth curved surface.')}
{note('A common pipeline is PCA to 50 dimensions first and then t-SNE or UMAP to 2. PCA removes noise and makes the neighbour search much faster, and the picture usually looks the same or better.', 'tip')}
''', kw=['PCA vs t-SNE', 'PCA vs UMAP', 'Isomap vs t-SNE', 'PCA then t-SNE'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Classical MDS', 'B = &minus;&frac12; J D<sup>(2)</sup> J, J = I &minus; (1/n) 1 1<sup>T</sup>, Z = V<sub>k</sub> &Lambda;<sub>k</sub><sup>1/2</sup>', 'Double centre the squared distances, then take the top eigenvectors.', key=True),
     fx('Isomap', 'D<sub>geo</sub> = shortest paths in the k neighbour graph, then classical MDS on D<sub>geo</sub>', 'Geodesic distances.', key=True),
     fx('t-SNE cost', 'KL(P | Q) = &Sigma;<sub>i&ne;j</sub> p<sub>ij</sub> log(p<sub>ij</sub> / q<sub>ij</sub>)', 'Big penalty for neighbours placed far apart.', key=True),
     fx('t-SNE gradient', '&part;C/&part;y<sub>i</sub> = 4 &Sigma;<sub>j</sub> (p<sub>ij</sub> &minus; q<sub>ij</sub>)(y<sub>i</sub> &minus; y<sub>j</sub>)(1 + |y<sub>i</sub> &minus; y<sub>j</sub>|<sup>2</sup>)<sup>&minus;1</sup>', 'Attraction minus repulsion.', key=True),
     fx('Stress (metric MDS)', '&Sigma;<sub>i&lt;j</sub> (d<sub>ij</sub> &minus; |z<sub>i</sub> &minus; z<sub>j</sub>|)<sup>2</sup>', 'Lower is better.'))}
{steps('Worked example: classical MDS for two points', [
    'Two points 2 apart: squared distance matrix D<sup>(2)</sup> = [[0, 4], [4, 0]].',
    'Double centring gives B = &minus;&frac12; J D<sup>(2)</sup> J = [[1, &minus;1], [&minus;1, 1]].',
    'The eigenvalues of B are 2 and 0. The top eigenvector is (1, &minus;1) / &radic;2.',
    eq('Coordinates = &radic;2 &times; (1, &minus;1)/&radic;2 = (1, &minus;1)'),
    'The two points sit at 1 and &minus;1, exactly 2 apart, centred at 0.'])}
{deep('Why t-SNE uses a Student t in the map', '<p>In 10 dimensions a point can have many neighbours all at about the same distance, but in 2D there is not enough room to place them all equally close: this is the <b>crowding problem</b>. With a Gaussian in both spaces, moderately distant points get squashed together in the middle of the map. The Student t curve with one degree of freedom has heavy tails, so a moderate high dimensional distance can become a large map distance at little cost. That opens gaps between clusters. KL(P | Q) is asymmetric: placing true neighbours far apart (large p, small q) costs a lot, while placing non neighbours close (small p, large q) costs little. That is exactly why t-SNE keeps local structure and is loose with global structure. Barnes-Hut t-SNE approximates the repulsion with a quadtree and runs in O(n log n) instead of O(n<sup>2</sup>).</p>')}
''', kw=['classical MDS formula', 'double centring', 't-SNE gradient', 'crowding problem', 'KL asymmetry', 'Barnes-Hut'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Manifold learning makes a flat map of data that is curled up in many dimensions, keeping points that are close together close on the map.</p>',
    '<p>Run t-SNE with a few perplexities, read the map with care, use Isomap or spectral embedding for smooth surfaces, MDS for distance tables, and UMAP for large data.</p>',
    '<p>Explain geodesic distance and the neighbour graph, derive classical MDS by double centring, write the t-SNE cost and gradient, and explain the crowding problem and KL asymmetry.</p>',
    '<p>Study the theory of graph Laplacians and diffusion maps, the fuzzy simplicial sets behind UMAP, the attraction and repulsion view that links t-SNE and UMAP, and the limits of what any 2D embedding can preserve.</p>')}
{grow('Explain flattening curved data while keeping neighbours.',
      'Make and read t-SNE, Isomap and MDS maps correctly.',
      'Derive the algorithms and their trade offs.')}
''', kw=['beginner', 'expert', 'diffusion maps', 'graph Laplacian', 'fuzzy simplicial sets'])

lc(1791, 'Find Center of Star Graph', 'find-center-of-star-graph', 'e', 'The centre appears in the first two edges', 'Every edge touches the centre, so the node shared by the first two edges is the answer. Reading structure from a list of edges is the first step of every neighbour graph method.', r"""
def find_center(edges):
    a, b = edges[0]
    return a if a in edges[1] else b
""", [('find_center([[1, 2], [2, 3], [4, 2]])', 2), ('find_center([[1, 2], [5, 1], [1, 3], [1, 4]])', 1)])
lc(743, 'Network Delay Time', 'network-delay-time', 'm', 'Dijkstra from the source, answer is the largest distance', 'Run Dijkstra’s algorithm with a heap from node k. If some node is never reached the answer is &minus;1, otherwise it is the largest shortest path distance. Isomap runs this same search from every point.', r"""
import heapq


def network_delay_time(times, n, k):
    graph = {}
    for u, v, w in times:
        graph.setdefault(u, []).append((v, w))
    dist = {}
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        for v, w in graph.get(u, []):
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return max(dist.values()) if len(dist) == n else -1
""", [('network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2)', 2), ('network_delay_time([[1, 2, 1]], 2, 2)', -1)])
lc(1334, 'Find the City With the Smallest Number of Neighbors at a Threshold Distance', 'find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance', 'm', 'All pairs shortest paths with Floyd and Warshall', 'Fill a distance table, then for every middle city m relax d[i][j] with d[i][m] + d[m][j]. Count reachable cities within the threshold for each city and keep the smallest count, breaking ties by the larger index. Isomap needs exactly this table of all pairs distances.', r"""
def find_the_city(n, edges, distance_threshold):
    INF = float("inf")
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
        d[v][u] = min(d[v][u], w)
    for m in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][m] + d[m][j] < d[i][j]:
                    d[i][j] = d[i][m] + d[m][j]
    best, answer = None, -1
    for i in range(n):
        count = sum(1 for j in range(n) if j != i and d[i][j] <= distance_threshold)
        if best is None or count <= best:
            best, answer = count, i
    return answer
""", [('find_the_city(4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], 4)', 3), ('find_the_city(5, [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]], 2)', 0)])
lc(1514, 'Path with Maximum Probability', 'path-with-maximum-probability', 'm', 'Dijkstra that multiplies probabilities and keeps the largest', 'Use a max heap on probability. Moving along an edge multiplies the probability, which can only shrink it, so the first time you pop the end node you have the best path. t-SNE also works with neighbour probabilities on a graph.', r"""
import heapq


def max_probability(n, edges, succ_prob, start, end):
    graph = [[] for _ in range(n)]
    for (u, v), p in zip(edges, succ_prob):
        graph[u].append((v, p))
        graph[v].append((u, p))
    best = [0.0] * n
    best[start] = 1.0
    heap = [(-1.0, start)]
    while heap:
        neg, u = heapq.heappop(heap)
        if u == end:
            return -neg
        if -neg < best[u]:
            continue
        for v, p in graph[u]:
            if -neg * p > best[v]:
                best[v] = -neg * p
                heapq.heappush(heap, (-best[v], v))
    return 0.0
""", [('max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2)', 0.25), ('max_probability(3, [[0, 1]], [0.5], 0, 2)', 0.0)])
lc(1631, 'Path With Minimum Effort', 'path-with-minimum-effort', 'm', 'Dijkstra where a path costs its biggest step', 'The effort of a path is its largest height difference. Run Dijkstra with that cost: moving to a neighbour costs max(current effort, height difference). Paths through a surface that avoid big jumps are what manifold methods look for.', r"""
import heapq


def minimum_effort_path(heights):
    rows, cols = len(heights), len(heights[0])
    best = [[float("inf")] * cols for _ in range(rows)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        e, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return e
        if e > best[r][c]:
            continue
        for a, b in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
            if 0 <= a < rows and 0 <= b < cols:
                ne = max(e, abs(heights[a][b] - heights[r][c]))
                if ne < best[a][b]:
                    best[a][b] = ne
                    heapq.heappush(heap, (ne, a, b))
    return 0
""", [('minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]])', 2), ('minimum_effort_path([[1, 2, 3], [3, 8, 4], [5, 3, 5]])', 1)])
lc(882, 'Reachable Nodes In Subdivided Graph', 'reachable-nodes-in-subdivided-graph', 'h', 'Dijkstra on the original nodes, then count partial edges', 'An edge with cnt new nodes has length cnt + 1. Run Dijkstra on the original nodes. Count every original node within maxMoves. For each edge, the new nodes reached from each end are the moves left there, and together they cannot exceed cnt.', r"""
import heapq


def reachable_nodes(edges, max_moves, n):
    graph = [[] for _ in range(n)]
    for u, v, cnt in edges:
        graph[u].append((v, cnt + 1))
        graph[v].append((u, cnt + 1))
    dist = [float("inf")] * n
    dist[0] = 0
    heap = [(0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    total = sum(1 for d in dist if d <= max_moves)
    for u, v, cnt in edges:
        a = max(0, max_moves - dist[u])
        b = max(0, max_moves - dist[v])
        total = total + min(cnt, a + b)
    return total
""", [('reachable_nodes([[0, 1, 10], [0, 2, 1], [1, 2, 2]], 6, 3)', 13), ('reachable_nodes([[0, 1, 4], [1, 2, 6], [0, 2, 8], [1, 3, 1]], 10, 4)', 23)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Manifold methods run on neighbour graphs and shortest paths. These problems practise reading graph structure, Dijkstra from one source, all pairs shortest paths with Floyd and Warshall (exactly what Isomap needs), paths that multiply probabilities, paths that avoid big jumps, and counting what is reachable within a budget. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'Dijkstra', 'Floyd Warshall', 'shortest path', 'graphs', 'heap'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>manifold</b> is a low dimensional surface inside a high dimensional space. PCA cannot unroll curved ones.',
    '<b>Isomap</b> uses shortest paths in a k neighbour graph (geodesic distances) and then classical MDS. LLE and spectral embedding keep local neighbourhoods.',
    '<b>MDS</b> makes a map from a distance table. Classical MDS on Euclidean distances equals PCA.',
    '<b>t-SNE</b> matches Gaussian neighbour probabilities with Student t map probabilities by minimising KL. Perplexity sets the effective number of neighbours.',
    'In t-SNE maps trust neighbours, not cluster sizes or gaps. Try several perplexities and seeds. There is no transform for new points.',
    '<b>UMAP</b> is faster, scales to millions and can transform new points, but lives in the separate umap-learn package.'],
    'Unsupervised 3.1 covers anomaly detection: Isolation Forest, local outlier factor, one class SVM and robust statistics.')}
{files('Three tasks: the stress of a map, a geodesic distance through a neighbour graph, and the perplexity of a distribution.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A manifold in machine learning is', ['A kind of neural network', 'A low dimensional surface curled inside a higher dimensional space', 'A loss function', 'A clustering result'], 1, 'Rolled up sheet.', 'Data often lies near one.')
K.quiz('e', 'The main use of t-SNE is', ['Training classifiers', 'Making 2D pictures that keep neighbours together', 'Compressing files', 'Choosing k for k-means'], 1, 'Visualisation.', 'It is a tool for looking.')
K.quiz('e', 'MDS needs as input', ['Labels', 'A table of distances or dissimilarities between items', 'Images only', 'A learning rate'], 1, 'Distances.', 'Features are optional.')
K.quiz('e', 'Geodesic distance means', ['The straight line distance', 'The distance along the surface of the data', 'The number of features', 'The cosine similarity'], 1, 'Road, not crow.', 'Isomap measures it with shortest paths.')
K.quiz('m', 'Perplexity in t-SNE is roughly', ['The number of clusters', 'The effective number of neighbours each point considers', 'The number of iterations', 'The output dimension'], 1, '2<sup>entropy</sup>.', 'Typical values are 5 to 50.')
K.quiz('m', 'In a t-SNE map, the size of a cluster', ['Shows its true spread', 'Carries little meaning, because t-SNE evens out densities', 'Shows its number of points exactly', 'Is always the same as in PCA'], 1, 'Distill 2016.', 'Both clusters had spread 4.3.')
K.quiz('m', 'If Isomap uses too many neighbours,', ['It runs faster with no change', 'Links can short circuit across folds of the manifold', 'It becomes t-SNE', 'It needs labels'], 1, 'Jumps across the gap.', 'Then geodesic distances become straight lines.')
K.quiz('m', 'Which method can transform new points after fitting?', ['scikit-learn TSNE', 'UMAP', 'Classical MDS', 'None of them'], 1, 'transform.', 'scikit-learn TSNE has only fit_transform.')
K.quiz('m', 'Classical MDS on Euclidean distances gives the same result as', ['k-means', 'PCA', 't-SNE', 'Isomap'], 1, 'Double centring.', 'Up to rotation or reflection.')
K.quiz('h', 't-SNE uses a Student t distribution in the map to', ['Make it faster', 'Ease the crowding problem with heavy tails', 'Handle labels', 'Make it deterministic'], 1, 'Room in 2D.', 'Moderate distances can become large map distances.')
K.quiz('h', 'KL(P | Q) in t-SNE punishes most', ['Non neighbours placed close together', 'True neighbours placed far apart', 'Large maps', 'Many iterations'], 1, 'Large p, small q.', 'So local structure is kept.')
K.quiz('h', 'Barnes-Hut t-SNE reduces the cost per iteration from', ['O(n) to O(1)', 'O(n<sup>2</sup>) to O(n log n)', 'O(n<sup>3</sup>) to O(n<sup>2</sup>)', 'O(log n) to O(1)'], 1, 'Quadtree.', 'Far groups of points are treated as one.')
K.quiz('x', 'In the style of a Stanford CS229 exam: Isomap’s all pairs geodesic step with Floyd and Warshall costs', ['O(n)', 'O(n log n)', 'O(n<sup>3</sup>)', 'O(k)'], 2, 'Three nested loops.', 'Dijkstra from every node is O(n<sup>2</sup> log n) on a sparse graph.')
K.quiz('x', 'In the style of a CMU 10-715 exam: why can t-SNE show clusters in pure Gaussian noise?', ['It adds labels', 'At low perplexity it fits tiny random neighbourhoods and the optimisation forms clumps', 'It uses k-means inside', 'It cannot'], 1, 'Distill 2016.', 'Always check clusters in the original space.')

K.calc('e', 'A point spreads its neighbour probability evenly over 8 points. Perplexity?', '8', 'Uniform over k gives perplexity k.', ['Entropy = log<sub>2</sub> 8 = 3 bits.', 'Perplexity = 2<sup>3</sup>.', eq('8')], check=8)
K.calc('e', 'Student t similarity (1 + d<sup>2</sup>)<sup>&minus;1</sup> for map distance d = 2?', '0.2', 'Plug in.', ['d<sup>2</sup> = 4.', '1 + 4 = 5.', eq('1 / 5 = 0.2')], check=0.2)
K.calc('e', 'True distances 3, 4, 5. Map distances 3, 4, 4. Raw stress?', '1', 'Sum of squared differences.', ['Differences 0, 0, 1.', 'Squares 0, 0, 1.', eq('stress = 1')], check=1)
K.calc('m', '100 points, each linked to its 10 nearest neighbours. How many directed links?', '1000', 'n &times; k.', ['100 points.', '10 links each.', eq('1,000 (fewer once duplicates are merged)')], check=1000)
K.calc('m', 'Floyd and Warshall on 1,000 points. Basic steps n<sup>3</sup>?', '1000000000', 'Three nested loops.', ['n = 1,000.', 'n<sup>3</sup> = 1,000 &times; 1,000 &times; 1,000.', eq('10<sup>9</sup>')], check=1000000000)
K.calc('m', 'Exact t-SNE on 10,000 points. Number of point pairs?', '49995000', 'n(n &minus; 1)/2.', ['10,000 &times; 9,999 = 99,990,000.', 'Divide by 2.', eq('49,995,000')], check=49995000)
K.calc('m', 'A path of 5 links, each 0.5 long, joins two points 1 apart in a straight line. Path length?', '2.5', 'Add the links.', ['5 &times; 0.5.', 'Straight line is 1.', eq('2.5, which is 2.5 times the straight line')], check=2.5)
K.calc('h', 'Student t similarity for map distance d = 3?', '0.1', '(1 + d<sup>2</sup>)<sup>&minus;1</sup>.', ['d<sup>2</sup> = 9.', '1 + 9 = 10.', eq('0.1, while a Gaussian exp(&minus;9/2) gives about 0.011')], check=0.1)
K.calc('h', 'KL(P | Q) in nats for P = (0.5, 0.5), Q = (0.25, 0.75)?', '0.144', '&Sigma; p ln(p/q).', ['0.5 ln(2) = 0.3466.', '0.5 ln(2/3) = &minus;0.2027.', eq('0.3466 &minus; 0.2027 = 0.144')], check=0.1438, tol=0.001)
K.calc('x', 'In the style of a Stanford CS229 problem: two points 2 apart. In classical MDS, the double centred matrix B = &minus;&frac12; J D<sup>(2)</sup> J has B[0][0] equal to?', '1', 'Double centre [[0, 4], [4, 0]].', ['J = [[0.5, &minus;0.5], [&minus;0.5, 0.5]].', 'J D<sup>(2)</sup> J = [[&minus;2, 2], [2, &minus;2]].', eq('B = &minus;&frac12; of that, so B[0][0] = 1')], check=1)

K.assign('stress', 'e', 'Stress of a map',
         '<p>Write <code>raw_stress(d, dz)</code> where d and dz are square distance tables (given and map). Return the sum over pairs i &lt; j of (d[i][j] &minus; dz[i][j])<sup>2</sup>, rounded to 4 decimals.</p>',
         """
def raw_stress(d, dz):
    # your code here
    pass
""", [('raw_stress([[0, 3], [3, 0]], [[0, 2], [2, 0]])', 1.0), ('raw_stress([[0, 1, 2], [1, 0, 1], [2, 1, 0]], [[0, 1, 1], [1, 0, 1], [1, 1, 0]])', 1.0), ('raw_stress([[0, 5], [5, 0]], [[0, 5], [5, 0]])', 0.0)],
         """
def raw_stress(d, dz):
    n = len(d)
    total = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            total = total + (d[i][j] - dz[i][j]) ** 2
    return round(total, 4)
""", 'Loop over the upper triangle only, so each pair counts once.', '<p>scikit-learn reports the same raw stress, or a normalised version that divides by the sum of squared distances.</p>')
K.assign('geodesic', 'm', 'Distance through a neighbour graph',
         '<p>Write <code>geodesic(points, k, a, b)</code>. Link every point to its k nearest other points (break distance ties by lower index), treat links as two way with Euclidean lengths, and return the shortest path length from point a to point b rounded to 4 decimals, or &minus;1 if b cannot be reached.</p>',
         """
def geodesic(points, k, a, b):
    # your code here
    pass
""", [('geodesic([[0, 0], [1, 0], [2, 0], [3, 0]], 1, 0, 3)', 3.0), ('geodesic([[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]], 1, 0, 4)', 4.0), ('geodesic([[0, 0], [0, 1], [5, 5], [5, 6]], 1, 0, 3)', -1)],
         """
import heapq


def geodesic(points, k, a, b):
    n = len(points)
    dist = lambda i, j: ((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2) ** 0.5
    graph = [dict() for _ in range(n)]
    for i in range(n):
        near = sorted((dist(i, j), j) for j in range(n) if j != i)[:k]
        for d, j in near:
            graph[i][j] = d
            graph[j][i] = d
    best = [float("inf")] * n
    best[a] = 0.0
    heap = [(0.0, a)]
    while heap:
        d, u = heapq.heappop(heap)
        if u == b:
            return round(d, 4)
        if d > best[u]:
            continue
        for v, w in graph[u].items():
            if d + w < best[v]:
                best[v] = d + w
                heapq.heappush(heap, (best[v], v))
    return -1
""", 'Build the k neighbour graph, make it two way, then run Dijkstra.', '<p>In the second test the points turn a corner, so the straight line from the first to the last is about 2.83 but the path along the points is 4.</p>')
K.assign('perplexity', 'm', 'Perplexity of a distribution',
         '<p>Write <code>perplexity(probs)</code> that returns 2<sup>H</sup>, where H = &minus;&Sigma; p log<sub>2</sub> p over the non zero probabilities, rounded to 4 decimals.</p>',
         """
import math


def perplexity(probs):
    # your code here
    pass
""", [('perplexity([0.5, 0.5])', 2.0), ('perplexity([0.25, 0.25, 0.25, 0.25])', 4.0), ('perplexity([1.0])', 1.0), ('perplexity([0.5, 0.25, 0.25])', 2.8284)],
         """
import math


def perplexity(probs):
    h = -sum(p * math.log2(p) for p in probs if p > 0)
    return round(2 ** h, 4)
""", 'Compute the entropy in bits, then raise 2 to it.', '<p>Perplexity is an effective count: an uneven spread over 3 neighbours acts like about 2.83 equally likely ones.</p>')

K.must('Manifolds', 'Low dimensional surface in high dimensions. PCA flattens, manifold methods unroll. Isomap: k neighbour graph, shortest paths, classical MDS.')
K.must('MDS', 'Map from a distance table. Classical MDS: B = &minus;&frac12; J D<sup>(2)</sup> J, top eigenvectors. Metric MDS minimises stress.')
K.must('t-SNE', 'Gaussian p<sub>j|i</sub> with perplexity 2<sup>H</sup>, Student t q<sub>ij</sub>, minimise KL(P | Q), early exaggeration, init="pca".')
K.must('Reading maps', 'Trust neighbours. Not sizes, not gaps. Try several perplexities and seeds. No transform. Not for model input.')
K.must('UMAP', 'Fuzzy neighbour graph, cross entropy, n_neighbors and min_dist, fast, transforms new points, umap-learn package.')
K.must('Costs', 'Exact t-SNE O(n<sup>2</sup>), Barnes-Hut O(n log n). Floyd and Warshall O(n<sup>3</sup>). PCA to 50 first speeds things up.')

T = K.topic(
    slug='ml-manifold', topic='ml-manifold', step=(2, 'Dimensionality reduction', 'ml-u2', 'Squeeze many features into a few that keep what matters, to see, compress and speed up later models.', 'Intermediate'),
    title='Manifold learning: t-SNE, UMAP, MDS and Isomap', short='Manifold learning', badge='2.2', minutes=50,
    lead='Make pictures of curved, high dimensional data: geodesic distances and Isomap, maps from distance tables with MDS, neighbour preserving maps with t-SNE and its perplexity, how to read those maps without being fooled, and where UMAP fits.',
    desc='manifold learning, manifold, geodesic distance, Isomap, LLE, spectral embedding, MDS, classical MDS, stress, t-SNE, perplexity, Student t, KL divergence, crowding problem, trustworthiness, UMAP, n_neighbors, min_dist, Barnes-Hut.',
    summary='Isomap and geodesic distance, MDS from distances, t-SNE and perplexity, reading maps safely, and UMAP.',
    keywords=['t-SNE', 'UMAP', 'Isomap', 'MDS', 'manifold learning', 'perplexity', 'geodesic distance', 'LLE', 'spectral embedding', 'visualisation'],
    recap='<p>Manifold methods flatten curved data into pictures that keep neighbours together. Use them to look and explore, and read sizes and gaps in the maps with care.</p>',
    added='2026-11-13', leet=leet_items())
