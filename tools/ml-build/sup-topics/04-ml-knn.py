# Supervised 2.2: k nearest neighbours. Checked against James, Witten, Hastie and Tibshirani, An Introduction to
# Statistical Learning (2nd edition) chapters 2.2.3 and 4.7.6, Hastie, Tibshirani and Friedman, The Elements of
# Statistical Learning chapter 13.3, Cover and Hart, Nearest Neighbor Pattern Classification (IEEE Trans. Information
# Theory, 1967), Beyer and others, When Is Nearest Neighbor Meaningful? (ICDT 1999), and the scikit-learn 1.8 user
# guide section 1.6 (nearest neighbours).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-knn')
K = Kit()

K.code('knn_by_hand', r'''
import math

# (height_cm, weight_kg) -> T-shirt size
people = [((158, 58), "M"), ((160, 59), "M"), ((163, 61), "M"), ((165, 64), "L"),
          ((168, 66), "L"), ((170, 68), "L"), ((160, 64), "L"), ((163, 59), "M")]
new = (161, 61)

distances = []
for (h, w), size in people:
    d = math.sqrt((h - new[0]) ** 2 + (w - new[1]) ** 2)
    distances.append((round(d, 2), size))
distances.sort()
print("sorted distances:", distances)

k = 3
votes = {}
for d, size in distances[:k]:
    votes[size] = votes.get(size, 0) + 1
print("votes of the", k, "nearest:", votes)
print("prediction:", max(votes, key=votes.get))
''')

K.code('choose_k', r'''
from sklearn.datasets import make_moons
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

X, y = make_moons(n_samples=300, noise=0.35, random_state=0)
for k in [1, 3, 7, 15, 31, 101]:
    model = KNeighborsClassifier(n_neighbors=k)
    train = model.fit(X, y).score(X, y)
    cv = cross_val_score(model, X, y, cv=5).mean()
    print("k =", str(k).rjust(3), " training accuracy", round(train, 3), " cross validated", round(cv, 3))
''')

K.code('distance_metrics', r'''
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

a = np.array([1.0, 2.0, 3.0])
b = np.array([2.0, 4.0, 6.5])

print("Euclidean (L2):", round(np.sqrt(np.sum((a - b) ** 2)), 3))
print("Manhattan (L1):", round(np.sum(np.abs(a - b)), 3))
print("Chebyshev (max):", round(np.max(np.abs(a - b)), 3))
for p in [1, 2, 3]:
    print("Minkowski p =", p, ":", round(np.sum(np.abs(a - b) ** p) ** (1 / p), 3))
print("cosine similarity:", round(cosine_similarity([a], [b])[0, 0], 4), " (same direction, so close to 1)")
''')

K.code('knn_regression', r'''
import numpy as np
from sklearn.model_selection import KFold, cross_val_score
from sklearn.neighbors import KNeighborsRegressor

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 10, 80)).reshape(-1, 1)
y = np.sin(x.ravel()) + rng.normal(0, 0.2, 80)

for weights in ["uniform", "distance"]:
    model = KNeighborsRegressor(n_neighbors=7, weights=weights)
    score = cross_val_score(model, x, y, cv=KFold(5, shuffle=True, random_state=0), scoring="r2").mean()
    print(weights.ljust(8), "weights, cross validated R2:", round(score, 3))
model = KNeighborsRegressor(n_neighbors=7).fit(x, y)
print("prediction at x = 1.6:", round(model.predict([[1.6]])[0], 3), " true sin(1.6) =", round(np.sin(1.6), 3))
''')

K.code('curse_of_dimensions', r'''
import numpy as np

rng = np.random.default_rng(1)
for dims in [2, 10, 100, 1000]:
    points = rng.uniform(0, 1, (500, dims))
    query = rng.uniform(0, 1, dims)
    d = np.sqrt(((points - query) ** 2).sum(axis=1))
    print("dimensions", str(dims).rjust(4), " nearest", round(d.min(), 2), " farthest", round(d.max(), 2),
          " ratio", round(d.min() / d.max(), 3))
''')

K.code('similar_items', r'''
import numpy as np
from sklearn.neighbors import NearestNeighbors

movies = np.array([[9, 1, 0], [8, 2, 1], [1, 9, 8], [0, 8, 9], [5, 5, 5]])   # action, romance, drama scores
names = ["Fast Cars", "Big Chase", "Love Letters", "Rainy Days", "Mixed Bag"]

nn = NearestNeighbors(n_neighbors=3).fit(movies)
dist, idx = nn.kneighbors([movies[0]])
print("most similar to", names[0], ":", [names[i] for i in idx[0][1:]], " distances", np.round(dist[0][1:], 2).tolist())
''')

K.code('knn_grid_search', r'''
from sklearn.datasets import load_wine
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_wine(return_X_y=True)
pipe = Pipeline([("scale", StandardScaler()), ("knn", KNeighborsClassifier())])
grid = GridSearchCV(pipe, {"knn__n_neighbors": [1, 3, 5, 7, 9, 15], "knn__weights": ["uniform", "distance"], "knn__p": [1, 2]}, cv=5)
grid.fit(X, y)
print("best settings:", grid.best_params_)
print("best cross validated accuracy:", round(grid.best_score_, 3))
''')

K.lesson('idea', 'Ask the neighbours', f'''
{src('James, Witten, Hastie and Tibshirani, An Introduction to Statistical Learning chapters 2.2.3 and 4.7.6, Hastie, Tibshirani and Friedman, The Elements of Statistical Learning chapter 13.3, Cover and Hart (1967), Beyer and others (1999), and the scikit-learn 1.8 user guide section 1.6.')}
{viz('mlknn')}
{wwh('<b>k nearest neighbours</b> (KNN) predicts the class of a new example by finding the k training examples closest to it and taking a majority vote. For numbers, it averages their values instead.',
     'It needs no training and makes no assumption about the shape of the boundary, so it can follow any pattern if there is enough data. It is easy to explain ("these 5 similar customers all left") and it is the idea behind recommendation ("people similar to you liked...") and similarity search.',
     'Store all the training examples. For a new point, compute its distance to every stored example, sort, keep the k smallest, and vote. The two choices that matter are k and the distance measure, and the features must be scaled so that no feature dominates the distance.')}
{run('knn_by_hand')}
{scene('choosing a restaurant in a new town', '<p>You do not know the town, so you ask the five people standing closest to you which restaurant is good. If four say "the dosa place", you go there. You did not build any theory of food, you just trusted the nearest opinions. KNN works exactly like that.</p>')}
''', kw=['k nearest neighbours', 'KNN', 'majority vote', 'lazy learning', 'instance based learning', 'distance'])

K.lesson('k', 'Choosing k', f'''
{viz('mlkregions')}
{wwh('<b>k</b> is the number of neighbours that vote. Small k follows the training data closely, large k smooths it.',
     'k = 1 always gets 100% on the training data, because every point is its own nearest neighbour, but it copies every noisy point (overfitting). A very large k ignores local patterns and predicts the majority class everywhere (underfitting).',
     'Try a range of k values with cross validation and pick the best. For two classes use an odd k to avoid ties. A rule of thumb starting point is k &asymp; &radic;n, but always check with cross validation.')}
{run('choose_k')}
{note('In the program, k = 1 scores 1.0 on training data but only 0.86 in cross validation. The best is around k = 7 (0.913), and k = 101 underfits (0.82). Training accuracy is useless for choosing k.', 'exam')}
''', kw=['choosing k', 'k = 1', 'overfitting', 'underfitting', 'bias variance', 'odd k', 'cross validation'])

K.lesson('distance', 'Distance measures and scaling', f'''
{wwh('KNN needs a <b>distance</b>. <b>Euclidean</b> is the straight line, <b>Manhattan</b> adds the differences along each axis (city blocks), <b>Minkowski</b> with power p covers both, and <b>cosine</b> compares directions and ignores length.',
     'The distance decides who counts as a neighbour. Euclidean suits measurements in comparable units, Manhattan is less sensitive to one big difference, and cosine suits text and other count vectors where length means "longer document", not "different topic".',
     'Pick the metric that matches what "similar" means for your data. Always scale numeric features first (StandardScaler): income in thousands would swamp age in years. In scikit-learn, set metric and p in KNeighborsClassifier.')}
{run('distance_metrics')}
{fxs(fx('Minkowski distance', 'd(a, b) = (&Sigma; |a<sub>i</sub> &minus; b<sub>i</sub>|<sup>p</sup>)<sup>1/p</sup>', 'p = 1 Manhattan, p = 2 Euclidean, p &rarr; &infin; Chebyshev (largest difference).', key=True),
     fx('Cosine similarity', 'cos(a, b) = a&middot;b / (||a|| ||b||)', '1 means the same direction. Cosine distance = 1 &minus; cos.', key=True))}
{note('Foundations 3.2 showed scaling raise KNN accuracy on the wine data from 0.691 to 0.949. Scaling is not optional for KNN.', 'warn')}
''', kw=['Euclidean distance', 'Manhattan distance', 'Minkowski', 'Chebyshev', 'cosine similarity', 'feature scaling', 'metric'])

K.lesson('regress', 'KNN for numbers and weighted votes', f'''
{wwh('<b>KNeighborsRegressor</b> predicts a number as the average of the k nearest targets. With <b>weights="distance"</b>, closer neighbours count more (weight 1/d) in both classification and regression.',
     'Many targets are numbers (price, temperature). Distance weighting also helps when the k neighbours are at very different distances: the one right next to the new point should matter more than one far away.',
     'Find the k nearest, then average their targets, optionally weighted by 1/distance. The prediction curve is a smooth staircase that follows the data without any formula.')}
{run('knn_regression')}
{fx('Weighted KNN prediction', 'ŷ = &Sigma; (1/d<sub>i</sub>) y<sub>i</sub> / &Sigma; (1/d<sub>i</sub>) over the k nearest', 'If some d<sub>i</sub> = 0, that point’s value is used directly.', key=True)}
''', kw=['KNN regression', 'KNeighborsRegressor', 'distance weighting', 'weights distance', 'local average'])

K.lesson('curse', 'The curse of dimensionality', f'''
{wwh('In many dimensions, all points end up at almost the same distance from each other. The nearest neighbour is then hardly nearer than the farthest point, so "nearest" stops meaning "similar".',
     'KNN depends completely on distances. With hundreds of features, most of them noise, KNN gets slow and inaccurate.',
     'The program puts 500 random points in a cube and measures the nearest and farthest distance from a query point. In 2 dimensions the nearest is 30 times closer than the farthest. In 1,000 dimensions the ratio is 0.9: everything is about equally far. Fix it by selecting features or reducing dimensions (PCA, Unsupervised 2.1) before KNN.')}
{run('curse_of_dimensions')}
{deep('How fast the data must grow', '<p>To keep a neighbourhood that holds a fraction r of uniform data in d dimensions, its side must be r<sup>1/d</sup> of the whole range. For r = 1% and d = 10 that is 0.63, so the "local" neighbourhood spans 63% of every feature’s range, which is not local at all. Keeping the same density needs data that grows exponentially in d. Beyer and others (1999) proved that for many distributions the ratio of farthest to nearest distance goes to 1 as d grows.</p>')}
''', kw=['curse of dimensionality', 'high dimensions', 'distance concentration', 'PCA before KNN', 'feature selection'])

K.lesson('search', 'Similarity search and tuning', f'''
{wwh('<b>NearestNeighbors</b> finds the k most similar items without predicting anything. It is the core of "more like this" features. Fast search structures (k-d tree, ball tree) and approximate methods (used in vector databases) avoid comparing against every item.',
     'Brute force KNN compares a query with all n items, which is too slow for millions of items or for answering many queries per second.',
     'k-d trees split the space into boxes so whole boxes can be skipped, and work well up to about 20 dimensions. For embeddings with hundreds of dimensions, approximate nearest neighbour indexes (HNSW, IVF) trade a tiny bit of accuracy for huge speed. For tuning, put the scaler and KNN in a Pipeline and search k, weights and p together with GridSearchCV.')}
{run('similar_items')}
{run('knn_grid_search')}
''', kw=['NearestNeighbors', 'similarity search', 'k-d tree', 'ball tree', 'approximate nearest neighbour', 'HNSW', 'vector database', 'GridSearchCV'])

K.lesson('versus', 'KNN compared', f'''
{versus('KNN against a trained model', ['', 'KNN', 'Logistic regression', 'Decision tree'], [
    ['Training time', 'None (just store)', 'Fast', 'Fast'],
    ['Prediction time', 'Slow: compare with all n examples', 'Very fast', 'Very fast'],
    ['Memory', 'Keeps the whole training set', 'One weight per feature', 'The tree'],
    ['Boundary', 'Any shape', 'Straight', 'Boxes'],
    ['Needs scaling', 'Yes, essential', 'Yes', 'No'],
    ['Many features', 'Suffers badly (curse of dimensionality)', 'Fine with a penalty', 'Fine'],
    ['Explanation', 'Shows similar examples', 'Weights and odds ratios', 'Rules']],
    'KNN is a great baseline and similarity tool for small, low dimensional, scaled data.')}
''', kw=['KNN vs logistic regression', 'lazy vs eager learning', 'prediction cost', 'memory'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('KNN classification', 'ŷ = most common class among the k nearest N<sub>k</sub>(x)', 'Majority vote.', key=True),
     fx('KNN regression', 'ŷ = (1/k) &Sigma;<sub>i &isin; N<sub>k</sub>(x)</sub> y<sub>i</sub>', 'Local average.', key=True),
     fx('Euclidean distance', 'd = &radic;&Sigma;(a<sub>i</sub> &minus; b<sub>i</sub>)<sup>2</sup>', 'The default.', key=True),
     fx('Cost of brute force prediction', 'O(n &times; d) per query', 'n stored examples, d features.', key=True),
     fx('Cover and Hart bound', 'R* &le; R<sub>1NN</sub> &le; 2R*(1 &minus; R*) as n &rarr; &infin;', 'With endless data, 1-NN errs at most twice the best possible error R* (two classes).'))}
{steps('Worked example: KNN by hand', [
    'New person (161, 61). Distances to the 8 people, sorted: 2.0 M, 2.24 M, 2.83 M, 3.16 L, 4.24 M, ...',
    'k = 3: the three nearest are M, M, M.',
    eq('Votes M = 3, L = 0, so the prediction is M'),
    'k = 4 would add an L: votes M = 3, L = 1, still M. The distance 2.0 comes from (163, 61): &radic;((163 &minus; 161)<sup>2</sup> + 0) = &radic;4 = 2.'])}
{deep('Why KNN works in the limit', '<p>As n grows and k grows but k/n shrinks, the k nearest neighbours of x crowd into a tiny ball around x, and their labels become a sample from P(y | x). A majority vote over a growing sample estimates the most likely class, so KNN approaches the Bayes optimal classifier (Stone, 1977). The catch is the rate: in d dimensions the error shrinks like n<sup>&minus;2/(d + 2)</sup> for smooth problems, which is painfully slow when d is large.</p>')}
''', kw=['KNN formula', 'Cover Hart', 'Bayes error', 'consistency', 'convergence rate', 'complexity'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>To label something new, find the most similar examples you already know and copy their most common label.</p>',
    '<p>Scale features, choose k with cross validation, pick Euclidean, Manhattan or cosine distance, use distance weights, and run KNN for both classes and numbers.</p>',
    '<p>Explain the bias and variance effect of k, the curse of dimensionality, the cost of prediction, and when to use k-d trees, ball trees or approximate search.</p>',
    '<p>Know the Cover and Hart bound, consistency of KNN, metric learning (learning the distance itself, for example large margin nearest neighbour), and approximate nearest neighbour indexes such as HNSW behind vector databases.</p>')}
{grow('Predict a class by asking the nearest examples.',
      'Tune k, the metric and weights in a scaled pipeline.',
      'Reason about high dimensions, search structures and the theory of nearest neighbour rules.')}
''', kw=['beginner', 'expert', 'metric learning', 'HNSW', 'consistency'])

lc(973, 'K Closest Points to Origin', 'k-closest-points-to-origin', 'm', 'Nearest neighbours with a heap', 'Keep a max heap of the k closest points seen so far (store negative squared distances). Push each point and pop when the heap grows past k. Squared distance is enough, no square root needed.', r'''
import heapq


def k_closest(points, k):
    heap = []
    for x, y in points:
        d = x * x + y * y
        heapq.heappush(heap, (-d, x, y))
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted([[x, y] for d, x, y in heap])
''', [('k_closest([[1, 3], [-2, 2]], 1)', [[-2, 2]]), ('k_closest([[3, 3], [5, -1], [-2, 4]], 2)', [[-2, 4], [3, 3]])])
lc(658, 'Find K Closest Elements', 'find-k-closest-elements', 'm', 'Binary search for the start of the window', 'The answer is a window of k neighbours in the sorted list. Binary search its left edge: if x is closer to arr[mid + k] than to arr[mid], move right.', r'''
def find_closest_elements(arr, k, x):
    low = 0
    high = len(arr) - k
    while low < high:
        mid = (low + high) // 2
        if x - arr[mid] > arr[mid + k] - x:
            low = mid + 1
        else:
            high = mid
    return arr[low:low + k]
''', [('find_closest_elements([1, 2, 3, 4, 5], 4, 3)', [1, 2, 3, 4]), ('find_closest_elements([1, 1, 2, 3, 4, 5], 4, -1)', [1, 1, 2, 3])])
lc(1637, 'Widest Vertical Area Between Two Points Containing No Points', 'widest-vertical-area-between-two-points-containing-no-points', 'e', 'Sort along one axis, then look at neighbours', 'Only x matters. Sort the x values and take the largest gap between neighbouring values. Sorting first is also how a k-d tree splits points along one axis.', r'''
def max_width_of_vertical_area(points):
    xs = sorted(p[0] for p in points)
    best = 0
    for i in range(1, len(xs)):
        best = max(best, xs[i] - xs[i - 1])
    return best
''', [('max_width_of_vertical_area([[8, 7], [9, 9], [7, 4], [9, 7]])', 1), ('max_width_of_vertical_area([[3, 1], [9, 0], [1, 0], [1, 4], [5, 3], [8, 8]])', 3)])
lc(1030, 'Matrix Cells in Distance Order', 'matrix-cells-in-distance-order', 'e', 'Sort by Manhattan distance', 'List every cell and sort by |r &minus; r0| + |c &minus; c0|. This is exactly how KNN orders candidates before taking the first k.', r'''
def all_cells_dist_order(rows, cols, r_center, c_center):
    cells = []
    for r in range(rows):
        for c in range(cols):
            cells.append([r, c])
    cells.sort(key=lambda cell: abs(cell[0] - r_center) + abs(cell[1] - c_center))
    return cells
''', [('all_cells_dist_order(1, 2, 0, 0)', [[0, 0], [0, 1]]), ('all_cells_dist_order(2, 2, 0, 1)', [[0, 1], [0, 0], [1, 1], [1, 0]])])
lc(1584, 'Min Cost to Connect All Points', 'min-cost-to-connect-all-points', 'm', 'Manhattan distances and a minimum spanning tree', 'Grow a tree from point 0. Keep, for every point outside the tree, its cheapest Manhattan distance to the tree, and add the cheapest point each round (Prim’s algorithm, O(n<sup>2</sup>)).', r'''
def min_cost_connect_points(points):
    n = len(points)
    in_tree = [False] * n
    cheapest = [float("inf")] * n
    cheapest[0] = 0
    total = 0
    for step in range(n):
        best = -1
        for i in range(n):
            if not in_tree[i] and (best == -1 or cheapest[i] < cheapest[best]):
                best = i
        in_tree[best] = True
        total = total + cheapest[best]
        bx, by = points[best]
        for i in range(n):
            if not in_tree[i]:
                d = abs(points[i][0] - bx) + abs(points[i][1] - by)
                if d < cheapest[i]:
                    cheapest[i] = d
    return total
''', [('min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]])', 20), ('min_cost_connect_points([[3, 12], [-2, 5], [-4, 1]])', 18)])
lc(719, 'Find K-th Smallest Pair Distance', 'find-k-th-smallest-pair-distance', 'h', 'Binary search on the distance, count with two pointers', 'Sort. For a guess distance g, count pairs with difference at most g using a sliding window. The answer is the smallest g with at least k such pairs.', r'''
def smallest_distance_pair(nums, k):
    s = sorted(nums)
    low = 0
    high = s[-1] - s[0]
    while low < high:
        mid = (low + high) // 2
        count = 0
        left = 0
        for right in range(len(s)):
            while s[right] - s[left] > mid:
                left = left + 1
            count = count + right - left
        if count >= k:
            high = mid
        else:
            low = mid + 1
    return low
''', [('smallest_distance_pair([1, 3, 1], 1)', 0), ('smallest_distance_pair([1, 1, 1], 2)', 0), ('smallest_distance_pair([1, 6, 1], 3)', 5)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>KNN is "measure distances, sort, take the k smallest". These problems practise each part: keep the k closest with a heap, find a window of k nearest values with binary search, sort along one axis, order cells by distance, connect points by their distances, and find the k-th smallest distance. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'k closest', 'heap', 'Manhattan distance', 'binary search', 'minimum spanning tree'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>KNN</b> stores the training data and predicts by a majority vote (classes) or an average (numbers) of the k nearest examples.',
    'Small k overfits (k = 1 is 100% on training data), large k underfits. Choose k by cross validation, odd for two classes.',
    '<b>Scale features</b> first. Pick the distance: Euclidean, Manhattan, Minkowski p, or cosine for text and counts.',
    'weights="distance" lets closer neighbours count more.',
    'The <b>curse of dimensionality</b>: in many dimensions all distances look alike. Reduce features first.',
    'No training cost but slow predictions, O(n d) per query. k-d trees and approximate search speed it up.'],
    'Supervised 2.3 is naive Bayes, a classifier built straight from Bayes rule and counting.')}
{files('Three tasks: Euclidean distance, a KNN vote, and KNN regression.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'How does KNN classify a new point?', ['Fits a line', 'Majority vote of the k closest training points', 'Picks a random class', 'Uses a tree'], 1, 'Neighbours.', 'It votes among the k nearest.')
K.quiz('e', 'With k = 1, training accuracy is', ['0%', '100%', '50%', 'Random'], 1, 'Each point is its own neighbour.', 'Every training point finds itself at distance 0.')
K.quiz('e', 'KNN training time is', ['Very long', 'Almost none, it only stores the data', 'Exponential', 'Same as prediction'], 1, 'Lazy learner.', 'All the work happens at prediction time.')
K.quiz('e', 'Before KNN you should', ['Remove the labels', 'Scale the features', 'Square the target', 'Shuffle the columns'], 1, 'Distances.', 'Features in large units would dominate the distance.')
K.quiz('m', 'Manhattan distance between (1, 2) and (4, 6) is', ['5', '7', '25', '3'], 1, '|Δx| + |Δy|.', '3 + 4 = 7.')
K.quiz('m', 'Why choose an odd k for two classes?', ['It is faster', 'To avoid tied votes', 'Even k is not allowed', 'It increases accuracy always'], 1, 'Ties.', 'An odd number of votes cannot split evenly between two classes.')
K.quiz('m', 'Increasing k makes the decision boundary', ['More jagged', 'Smoother', 'Exactly linear', 'Disappear'], 1, 'More voters.', 'Averaging more neighbours smooths the regions.')
K.quiz('m', 'Cosine similarity is a good choice for', ['Heights and weights', 'Word count vectors of documents', 'Binary labels', 'Time stamps'], 1, 'Direction, not length.', 'A long and a short document on the same topic point the same way.')
K.quiz('m', 'weights="distance" means', ['All neighbours count the same', 'Closer neighbours count more', 'Only the farthest neighbour counts', 'Distances are squared'], 1, '1/d.', 'Votes are weighted by inverse distance.')
K.quiz('h', 'Why does KNN degrade with hundreds of noisy features?', ['It cannot store them', 'Distances become nearly equal, so neighbours are not really similar', 'k must be larger than d', 'Scaling stops working'], 1, 'Curse of dimensionality.', 'The ratio of nearest to farthest distance approaches 1.')
K.quiz('h', 'The cost of one brute force KNN prediction with n examples and d features is', ['O(1)', 'O(n d)', 'O(d<sup>3</sup>)', 'O(log n)'], 1, 'Compare with every example.', 'n distances, each over d features.')
K.quiz('h', 'A k-d tree speeds up KNN most when', ['d is around 1,000', 'd is small, say under 20', 'k is very large', 'Data is categorical'], 1, 'Splitting space into boxes.', 'In high dimensions most boxes must be searched anyway.')
K.quiz('x', 'In the style of a Stanford CS229 exam: Cover and Hart (1967) showed that with infinite data, the 1-NN error for two classes is at most', ['The Bayes error', 'Twice the Bayes error', 'Half the Bayes error', '0.5'], 1, 'R &le; 2R*(1 &minus; R*).', 'So 1-NN is at most about twice as bad as the best possible classifier.')
K.quiz('x', 'In the style of a CMU 10-701 exam: to hold 1% of uniform data in a cube neighbourhood in 10 dimensions, each side must cover about', ['1% of the range', '10% of the range', '63% of the range', '100% of the range'], 2, 'Side = 0.01<sup>1/10</sup>.', '0.01<sup>0.1</sup> &asymp; 0.63, which is hardly local.')

K.calc('e', 'Euclidean distance from (0, 0) to (3, 4)?', '5', '&radic;(3<sup>2</sup> + 4<sup>2</sup>).', ['9 + 16 = 25.', 'Square root.', eq('5')], check=5)
K.calc('e', 'k = 5 neighbours: A, B, A, A, B. Prediction?', 'A', 'Count.', ['A appears 3 times.', 'B appears 2 times.', eq('A wins')], check='A')
K.calc('e', 'Manhattan distance from (1, 1) to (4, 5)?', '7', '|Δx| + |Δy|.', ['|4 &minus; 1| = 3.', '|5 &minus; 1| = 4.', eq('7')], check=7)
K.calc('m', 'KNN regression, k = 3 neighbours with targets 10, 12, 17. Prediction?', '13', 'Average.', ['Sum 39.', '3 neighbours.', eq('13')], check=13)
K.calc('m', 'Distance weighted vote: A at distance 1, B at 2, B at 2. Weight of A vs total B weight?', '1', 'Weights 1/d.', ['A: 1/1 = 1.', 'B: 1/2 + 1/2 = 1.', eq('A 1 vs B 1, a tie')], check=1)
K.calc('m', 'Minkowski p = 3 distance between (0, 0) and (1, 2), 3 decimals?', '2.08', '(1<sup>3</sup> + 2<sup>3</sup>)<sup>1/3</sup>.', ['1 + 8 = 9.', 'Cube root of 9.', eq('2.080')], check=round(9 ** (1 / 3), 2))
K.calc('m', 'Cosine similarity of (1, 0) and (1, 1), 3 decimals?', '0.707', 'a&middot;b / (|a||b|).', ['a&middot;b = 1.', '|a| = 1, |b| = &radic;2.', eq('1 / 1.414 = 0.707')], check=0.707)
K.calc('h', 'Brute force KNN: 1,000,000 examples, 100 features. Roughly how many subtractions for one query (in millions)?', '100', 'n &times; d.', ['One subtraction per feature per example.', '10<sup>6</sup> &times; 100 = 10<sup>8</sup>.', eq('100 million')], check=100)
K.calc('h', 'Rule of thumb k &asymp; &radic;n for n = 400. k?', '20', 'Square root.', ['&radic;400 = 20.', 'For two classes you would try 19 or 21.', eq('k &asymp; 20')], check=20)
K.calc('x', 'In the style of an MIT 6.867 problem: side length of a cube neighbourhood holding 10% of uniform data in 2 dimensions, 3 decimals?', '0.316', 'r<sup>1/d</sup>.', ['r = 0.1, d = 2.', '0.1<sup>1/2</sup>.', eq('0.316')], check=0.316)

K.assign('euclid', 'e', 'Euclidean distance',
         '<p>Write <code>euclidean(a, b)</code> for two lists of the same length. Return the distance rounded to 3 decimals.</p>',
         '''
import math


def euclidean(a, b):
    # your code here
    pass
''', [('euclidean([0, 0], [3, 4])', 5.0), ('euclidean([1, 2, 3], [1, 2, 3])', 0.0), ('euclidean([1, 1], [2, 3])', 2.236)],
         '''
import math


def euclidean(a, b):
    total = 0
    for x, y in zip(a, b):
        total = total + (x - y) ** 2
    return round(math.sqrt(total), 3)
''', 'Add up the squared differences, then take the square root.', '<p>For KNN you can skip the square root when you only compare distances, because it does not change the order.</p>')
K.assign('knnvote', 'm', 'A KNN vote',
         '<p>Write <code>knn_predict(train, labels, point, k)</code>. train is a list of points (lists), labels their classes. Return the majority class of the k nearest points by Euclidean distance. On a tie, return the class of the single nearest point.</p>',
         '''
import math


def knn_predict(train, labels, point, k):
    # your code here
    pass
''', [('knn_predict([[1, 1], [2, 2], [8, 8], [9, 9]], ["A", "A", "B", "B"], [1.5, 1.5], 3)', 'A'), ('knn_predict([[1, 1], [2, 2], [8, 8], [9, 9]], ["A", "A", "B", "B"], [7, 7], 1)', 'B'), ('knn_predict([[0, 0], [10, 10]], ["A", "B"], [4, 4], 2)', 'A')],
         '''
import math


def knn_predict(train, labels, point, k):
    pairs = []
    for p, lab in zip(train, labels):
        d = math.sqrt(sum((a - b) ** 2 for a, b in zip(p, point)))
        pairs.append((d, lab))
    pairs.sort(key=lambda t: t[0])
    votes = {}
    for d, lab in pairs[:k]:
        votes[lab] = votes.get(lab, 0) + 1
    top = max(votes.values())
    winners = [lab for lab in votes if votes[lab] == top]
    if len(winners) > 1:
        return pairs[0][1]
    return winners[0]
''', 'Compute every distance, sort, count the labels of the first k, and handle ties with the nearest point.', '<p>This is KNeighborsClassifier with algorithm="brute", written by hand.</p>')
K.assign('knnreg', 'm', 'KNN regression',
         '<p>Write <code>knn_regress(xs, ys, x, k)</code> for one feature: return the average y of the k values in xs closest to x, rounded to 3 decimals.</p>',
         '''
def knn_regress(xs, ys, x, k):
    # your code here
    pass
''', [('knn_regress([1, 2, 3, 10], [10, 12, 17, 50], 2.2, 3)', 13.0), ('knn_regress([0, 5, 10], [0, 50, 100], 9, 1)', 100.0)],
         '''
def knn_regress(xs, ys, x, k):
    pairs = sorted(zip([abs(v - x) for v in xs], ys))
    total = 0
    for d, y in pairs[:k]:
        total = total + y
    return round(total / k, 3)
''', 'Sort the (distance, y) pairs and average the first k values of y.', '<p>KNeighborsRegressor does this. With weights="distance" each y would be weighted by 1/distance.</p>')

K.must('Algorithm', 'Store data. For a query: distances to all, sort, k nearest, majority vote (or average for numbers). No training, slow prediction O(nd).')
K.must('Choosing k', 'Small k overfits, large k underfits. k = 1 gives 100% training accuracy. Cross validate, odd k for two classes.')
K.must('Distance', 'Euclidean, Manhattan, Minkowski p, cosine for text. Scale features first, always.')
K.must('Variants', 'weights="distance" (1/d). KNeighborsRegressor. NearestNeighbors for similarity search.')
K.must('High dimensions', 'Distances concentrate, nearest is barely nearer than farthest. Select features or use PCA first.')
K.must('Speed and theory', 'k-d tree and ball tree for low d, approximate search (HNSW) for embeddings. 1-NN error at most twice Bayes error.')

T = K.topic(
    slug='ml-knn', topic='ml-knn', step=(2, 'Classification', 'ml-s2', 'Predict categories: yes or no, spam or not, or which of many classes, with four very different families of models.', 'Intermediate'),
    title='k nearest neighbours: learn from similar examples', short='k nearest neighbours', badge='2.2', minutes=55,
    lead='Learn the simplest classifier of all: find the k closest examples and let them vote. Choose k, pick a distance, scale features, use KNN for numbers, see the curse of dimensionality, and speed up similarity search.',
    desc='k nearest neighbours, majority vote, lazy learning, choosing k, bias and variance, Euclidean, Manhattan, Minkowski and cosine distances, feature scaling, distance weighting, KNN regression, curse of dimensionality, NearestNeighbors, k-d tree, ball tree, approximate nearest neighbours, GridSearchCV, Cover and Hart bound.',
    summary='the KNN vote, choosing k, distance measures, scaling, KNN regression, the curse of dimensionality and fast similarity search.',
    keywords=['KNN', 'k nearest neighbours', 'distance', 'Euclidean', 'Manhattan', 'cosine similarity', 'choosing k', 'curse of dimensionality', 'scaling', 'similarity search'],
    recap='<p>KNN trusts the closest examples. Scale the features, pick k by cross validation, and keep the number of features modest.</p>',
    added='2026-11-13', leet=leet_items())
