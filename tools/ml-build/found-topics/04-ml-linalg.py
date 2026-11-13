# Foundations 2.1: linear algebra for machine learning. Checked against Gilbert Strang, Introduction to Linear Algebra
# (5th edition) chapters 1 to 4 and 6, Deisenroth, Faisal and Ong, Mathematics for Machine Learning (2020) chapters 2
# and 3, the Stanford CS229 linear algebra review (Kolter and Do), and the NumPy 2.4 linalg reference.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq, mat
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-linalg')
K = Kit()

K.code('vectors_by_hand', r'''
# A vector is a list of numbers. Each example in ML is one vector of features.
asha = [21, 160, 55]      # age, height_cm, weight_kg
ravi = [25, 175, 70]

def add(u, v):
    result = []
    for a, b in zip(u, v):
        result.append(a + b)
    return result

def scale(c, v):
    result = []
    for a in v:
        result.append(c * a)
    return result

def dot(u, v):
    total = 0
    for a, b in zip(u, v):
        total = total + a * b
    return total

print("asha + ravi =", add(asha, ravi))
print("half of ravi =", scale(0.5, ravi))
print("average person =", scale(0.5, add(asha, ravi)))
print("dot(asha, ravi) =", dot(asha, ravi))
''')

K.code('norms_and_distances', r'''
import math

def euclidean(u, v):
    total = 0
    for a, b in zip(u, v):
        total = total + (a - b) ** 2
    return math.sqrt(total)

def manhattan(u, v):
    total = 0
    for a, b in zip(u, v):
        total = total + abs(a - b)
    return total

def cosine_similarity(u, v):
    dot = 0
    size_u = 0
    size_v = 0
    for a, b in zip(u, v):
        dot = dot + a * b
        size_u = size_u + a * a
        size_v = size_v + b * b
    return dot / (math.sqrt(size_u) * math.sqrt(size_v))

a = [1, 2]
b = [4, 6]
print("Euclidean:", euclidean(a, b))
print("Manhattan:", manhattan(a, b))
print("length of b (L2 norm):", round(euclidean(b, [0, 0]), 4))
print("cosine(a, b):", round(cosine_similarity(a, b), 4))
print("cosine([1, 2], [2, 4]):", round(cosine_similarity([1, 2], [2, 4]), 4), "same direction")
''')

K.code('word_counts_cosine', r'''
import math

# Two short reviews turned into word count vectors over the same word list
words = ["good", "great", "bad", "food", "service"]
review_1 = [2, 1, 0, 1, 1]       # "good good great food service"
review_2 = [1, 0, 0, 1, 0]       # "good food"
review_3 = [0, 0, 3, 1, 1]       # "bad bad bad food service"

def cosine(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    return dot / (math.sqrt(sum(a * a for a in u)) * math.sqrt(sum(b * b for b in v)))

print("review 1 vs 2:", round(cosine(review_1, review_2), 3))
print("review 1 vs 3:", round(cosine(review_1, review_3), 3))
print("The short review 2 is closer to review 1 even though it is much shorter.")
''')

K.code('matrix_by_hand', r'''
def mat_vec(M, v):
    result = []
    for row in M:                     # one dot product per row
        total = 0
        for a, b in zip(row, v):
            total = total + a * b
        result.append(total)
    return result

def mat_mul(A, B):
    rows = len(A)
    cols = len(B[0])
    inner = len(B)
    C = []
    for i in range(rows):
        new_row = []
        for j in range(cols):
            total = 0
            for k in range(inner):
                total = total + A[i][k] * B[k][j]
            new_row.append(total)
        C.append(new_row)
    return C

M = [[2, 1],
     [0, 1]]
print("M x (1, 2) =", mat_vec(M, [1, 2]))
print("M x M =", mat_mul(M, M))
I = [[1, 0], [0, 1]]
print("M x I =", mat_mul(M, I), "(the identity changes nothing)")
''')

K.code('linear_model_as_matrix', r'''
import numpy as np

# 3 houses, features: size in 100 m2, rooms, age in 10 years
X = np.array([[0.5, 1, 1.0],
              [0.8, 2, 0.5],
              [1.2, 3, 0.2]])
w = np.array([40.0, 5.0, -3.0])     # price change per unit of each feature
b = 4.0                              # base price

prices = X @ w + b                   # all predictions in one line
print("predicted prices:", prices)
print("shape of X:", X.shape, "shape of w:", w.shape, "shape of result:", prices.shape)
''')

K.code('solve_system', r'''
import numpy as np

# Find w1, w2 so that  2*w1 + 1*w2 = 5  and  1*w1 + 3*w2 = 10
A = np.array([[2.0, 1.0],
              [1.0, 3.0]])
y = np.array([5.0, 10.0])

w = np.linalg.solve(A, y)          # better than computing the inverse
print("w =", w)
print("check A @ w =", A @ w)
print("determinant:", round(np.linalg.det(A), 6))
print("inverse:")
print(np.linalg.inv(A).round(4))
print("rank:", np.linalg.matrix_rank(A))
''')

K.code('projection_and_eigen', r'''
import numpy as np

# Project a point onto a direction (the idea behind PCA and least squares)
x = np.array([3.0, 4.0])
d = np.array([1.0, 0.0])            # the direction of the x axis
shadow = (x @ d) / (d @ d) * d
print("projection of (3, 4) on the x axis:", shadow)

# Eigenvectors: directions a matrix only stretches, never turns
S = np.array([[2.0, 1.0],
              [1.0, 2.0]])
values, vectors = np.linalg.eigh(S)  # eigh is for symmetric matrices
print("eigenvalues:", values.round(4))
print("eigenvectors (columns):")
print(vectors.round(4))
v = vectors[:, 1]
print("S @ v =", (S @ v).round(4), " = 3 x v =", (3 * v).round(4))
''')

K.lesson('vectors', 'Vectors: every example is a list of numbers', f'''
{src('Strang, Introduction to Linear Algebra (5th edition), Deisenroth, Faisal and Ong, Mathematics for Machine Learning (2020), and the Stanford CS229 linear algebra review.')}
{wwh('A <b>vector</b> is an ordered list of numbers, such as [21, 160, 55] for age, height and weight. Each number is one <b>component</b>. A vector with d numbers lives in d dimensional space.',
     'ML models only understand numbers. Every example, whether a house, a photo or a sentence, is first turned into a vector of features. Then "similar examples" means "nearby vectors", and models can do maths on them.',
     'Vectors add component by component, can be multiplied by a number (scaled), and two vectors give one number with the <b>dot product</b>: multiply matching components and add.')}
{run('vectors_by_hand')}
{scene('a song on a music app', '<p>A music app can describe every song with numbers: tempo, loudness, how much it sounds like dance music, how acoustic it is, and so on. Each song becomes a vector. When you like a song, the app looks for songs whose vectors are close to it. "Songs like this one" is really "nearby vectors".</p>')}
{note('The order of components matters. [age, height] and [height, age] are different vectors. Every example must use the same feature order.', 'warn')}
''', kw=['vector', 'component', 'dimension', 'vector addition', 'scalar multiplication', 'dot product', 'feature vector'])

K.lesson('distance', 'Length, distance and similarity', f'''
{viz('mldist')}
{run('norms_and_distances')}
{fxs(fx('Euclidean distance (L2)', 'd(a, b) = &radic;( &Sigma; (a<sub>i</sub> &minus; b<sub>i</sub>)<sup>2</sup> )', 'The straight line distance. Used by k nearest neighbours and k means.', key=True),
     fx('Manhattan distance (L1)', 'd(a, b) = &Sigma; |a<sub>i</sub> &minus; b<sub>i</sub>|', 'The city block distance. Less hurt by one huge gap.'),
     fx('Length (norm) of a vector', '||v||<sub>2</sub> = &radic;(v<sub>1</sub><sup>2</sup> + ... + v<sub>d</sub><sup>2</sup>), ||v||<sub>1</sub> = &Sigma; |v<sub>i</sub>|', 'The distance from the origin. Ridge regression punishes L2, lasso punishes L1.', key=True),
     fx('Cosine similarity', 'cos &theta; = a &middot; b / (||a|| ||b||)', '1 for the same direction, 0 for a right angle, &minus;1 for opposite. Used for text and embeddings.', key=True))}
{run('word_counts_cosine')}
{note('Distances only make sense when features are on similar scales. Height in centimetres (around 170) would swamp age in years (around 25). Scale features first (Foundations 3.2).', 'exam')}
''', kw=['Euclidean distance', 'Manhattan distance', 'L1 norm', 'L2 norm', 'cosine similarity', 'distance metric', 'feature scaling'])

K.lesson('matrices', 'Matrices: tables of numbers that transform vectors', f'''
{viz('mlmatvec')}
{wwh('A <b>matrix</b> is a rectangle of numbers with rows and columns. An n &times; d matrix has n rows and d columns. Your whole dataset is a matrix X: one row per example, one column per feature.',
     'A matrix lets us do many dot products at once. Multiplying the data matrix by a weight vector gives every prediction in one step. In a neural network, each layer is a matrix.',
     'Matrix times vector: each row of the matrix is dotted with the vector. Matrix times matrix: entry (i, j) is row i of the first dotted with column j of the second. The inner sizes must match.')}
{run('matrix_by_hand')}
{table(['Name', 'What it is', 'Why ML cares'], [
    ['Square matrix', 'Same number of rows and columns', 'Covariance matrices, systems of equations'],
    ['Identity I', '1 on the diagonal, 0 elsewhere', 'I v = v, the "do nothing" matrix'],
    ['Transpose A<sup>T</sup>', 'Rows become columns', 'X<sup>T</sup>X appears in linear regression'],
    ['Symmetric', 'A = A<sup>T</sup>', 'Covariance matrices are symmetric, which makes PCA work'],
    ['Diagonal', 'Non zero numbers only on the diagonal', 'Scaling each feature separately'],
    ['Inverse A<sup>&minus;1</sup>', 'A A<sup>&minus;1</sup> = I, exists only if det(A) &ne; 0', 'Solving equations, the normal equation']])}
{note('Matrix multiplication is not commutative: A B is usually not B A, and B A may not even exist when the shapes do not match.', 'exam')}
''', kw=['matrix', 'matrix vector product', 'matrix multiplication', 'identity', 'transpose', 'symmetric', 'inverse', 'shape rule'])

K.lesson('model', 'A linear model is a matrix product', f'''
{run('linear_model_as_matrix')}
{fxs(fx('Linear model for all examples', 'ŷ = X w + b', 'X is n &times; d, w has d weights, b is one number added to every prediction.', key=True),
     fx('One prediction', 'ŷ<sub>i</sub> = w &middot; x<sub>i</sub> + b = w<sub>1</sub>x<sub>i1</sub> + ... + w<sub>d</sub>x<sub>id</sub> + b', 'Each weight says how much the prediction changes when its feature grows by 1.'),
     fx('Bias trick', 'add a column of 1s to X, then ŷ = X w', 'b becomes just another weight, which makes the maths shorter.'))}
<p>Linear regression, logistic regression, support vector machines and every layer of a neural network start with this same product. Learning means finding good numbers for w and b.</p>
''', kw=['linear model', 'X w + b', 'weights', 'bias', 'bias trick', 'prediction as matrix product'])

K.lesson('systems', 'Systems of equations, inverse, determinant and rank', f'''
{run('solve_system')}
{wwh('A <b>system of linear equations</b> asks for the unknowns w that make A w = y true. The <b>determinant</b> tells if a square system has exactly one answer, and the <b>rank</b> counts how many rows (or columns) give truly new information.',
     'Fitting a line to data leads to such a system (the normal equation in Supervised 1.1). When two features say the same thing, for example size in m<sup>2</sup> and size in square feet, the matrix loses rank and the answer becomes unstable.',
     'If det(A) &ne; 0, A has an inverse and w = A<sup>&minus;1</sup> y. In code use np.linalg.solve, which is faster and more accurate than computing the inverse. If det(A) = 0, the columns are linearly dependent.')}
{fxs(fx('2 &times; 2 determinant', 'det [[a, b], [c, d]] = a d &minus; b c', 'How much the matrix scales areas. 0 means it squashes the plane to a line.', key=True),
     fx('2 &times; 2 inverse', '[[a, b], [c, d]]<sup>&minus;1</sup> = (1 / (a d &minus; b c)) [[d, &minus;b], [&minus;c, a]]', 'Swap a and d, change the signs of b and c, divide by the determinant.'),
     fx('Rank', 'rank(A) = number of linearly independent columns', 'Full rank means no column is a mix of the others.'))}
{note('Perfectly correlated features (one column is a multiple of another) make X<sup>T</sup>X impossible to invert. This is called multicollinearity. Drop one of the features or use ridge regression.', 'warn')}
''', kw=['system of equations', 'np.linalg.solve', 'determinant', 'inverse', 'rank', 'linear independence', 'multicollinearity'])

K.lesson('eigen', 'Projections and eigenvectors: a first look', f'''
{run('projection_and_eigen')}
{wwh('A <b>projection</b> is the shadow of a vector on a direction. An <b>eigenvector</b> of a matrix is a direction the matrix only stretches, by a number called the <b>eigenvalue</b>, without turning it.',
     'Least squares regression projects the label vector onto the space of the features. PCA (Unsupervised 2.1) finds the eigenvectors of the covariance matrix, which are the directions where the data spreads the most.',
     'Projection of x on direction d: ((x &middot; d) / (d &middot; d)) d. Eigenvectors solve A v = &lambda; v. NumPy finds them with np.linalg.eig, or np.linalg.eigh for symmetric matrices.')}
{fxs(fx('Projection', 'proj<sub>d</sub>(x) = ((x &middot; d) / (d &middot; d)) d', 'The closest point to x on the line through d.', key=True),
     fx('Eigen equation', 'A v = &lambda; v', 'v keeps its direction, its length is multiplied by &lambda;.', key=True),
     fx('Eigenvalues of a 2 &times; 2 matrix', '&lambda;<sup>2</sup> &minus; (a + d) &lambda; + (a d &minus; b c) = 0', 'Sum of eigenvalues = a + d (the trace), product = the determinant.'))}
{link('ml-maths', 'Want more practice with the maths?', 'The Maths for Machine Learning subject has full chapters on vectors, matrices, eigenvalues, SVD and PCA with animations and code in four languages.', 'Open Maths for ML')}
''', kw=['projection', 'eigenvector', 'eigenvalue', 'eigh', 'trace', 'PCA preview', 'least squares geometry'])

K.lesson('versus', 'Which distance to use', f'''
{versus('Distances compared', ['', 'Euclidean (L2)', 'Manhattan (L1)', 'Cosine', 'Chebyshev (L&infin;)'], [
    ['Measures', 'Straight line', 'Sum of gaps along axes', 'Angle between directions', 'Largest single gap'],
    ['Cares about length', 'Yes', 'Yes', 'No', 'Yes'],
    ['Effect of one huge gap', 'Strong (squared)', 'Milder', 'Depends on direction', 'Only that gap counts'],
    ['Good for', 'Dense numeric features of similar scale', 'Grids, high dimensions, outliers', 'Text, word counts, embeddings', 'King moves in chess, tolerances'],
    ['scikit-learn name', 'euclidean', 'manhattan', 'cosine', 'chebyshev']],
    'start with Euclidean on scaled numeric features, use cosine for text and embeddings, and try Manhattan when there are outliers or many dimensions.')}
{versus('Loops, lists or NumPy for linear algebra', ['', 'Plain loops', 'NumPy'], [
    ['Readable for learning', 'Yes, every step visible', 'One line hides the steps'],
    ['Speed', 'Slow', 'Very fast (BLAS libraries)'],
    ['Numerical care', 'You handle it', 'solve, lstsq and eigh are carefully tuned'],
    ['Use it when', 'Learning how it works', 'Real work']],
    'learn with loops once, then always use NumPy.')}
''', kw=['distance comparison', 'Chebyshev', 'L infinity', 'NumPy vs loops', 'BLAS'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Dot product and angle', 'a &middot; b = ||a|| ||b|| cos &theta;', 'Dot product 0 means the vectors are at a right angle (orthogonal).', key=True),
     fx('Shape of a product', '(n &times; k)(k &times; m) = (n &times; m)', 'The inner k must match. Each entry needs k multiplies.'),
     fx('Transpose of a product', '(A B)<sup>T</sup> = B<sup>T</sup> A<sup>T</sup>', 'The order flips.'),
     fx('Squared distance expanded', '||a &minus; b||<sup>2</sup> = ||a||<sup>2</sup> + ||b||<sup>2</sup> &minus; 2 a &middot; b', 'Lets libraries compute all pairwise distances with one matrix product.', key=True),
     fx('Cauchy Schwarz', '|a &middot; b| &le; ||a|| ||b||', 'Why cosine similarity is always between &minus;1 and 1.'))}
{steps('Worked example: invert a 2 &times; 2 matrix', [
    'A = [[2, 1], [1, 3]].',
    'det = 2 &times; 3 &minus; 1 &times; 1 = 5.',
    'Swap 2 and 3, change the signs of the 1s: [[3, &minus;1], [&minus;1, 2]].',
    eq('A<sup>&minus;1</sup> = (1/5) [[3, &minus;1], [&minus;1, 2]] = [[0.6, &minus;0.2], [&minus;0.2, 0.4]]'),
    'Check: A A<sup>&minus;1</sup> = [[2 &times; 0.6 + 1 &times; (&minus;0.2), ...]] = [[1, 0], [0, 1]]. Then w = A<sup>&minus;1</sup> (5, 10) = (1, 3).'])}
{deep('Why the expanded distance formula matters', '<p>To find the nearest neighbours of m query points among n stored points, the naive way computes m &times; n distances with d subtractions each. Using ||a &minus; b||<sup>2</sup> = ||a||<sup>2</sup> + ||b||<sup>2</sup> &minus; 2 a &middot; b, all the dot products come from one matrix product Q X<sup>T</sup>, which BLAS libraries run at near peak hardware speed. scikit-learn’s pairwise_distances and FAISS do this. The cost is some floating point error for nearly equal points, so results are clipped at 0.</p>')}
''', kw=['dot product angle', 'orthogonal', 'transpose of product', 'pairwise distance', 'Cauchy Schwarz'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A vector is a list of numbers that describes one thing. Close vectors mean similar things. A matrix is a table that can turn many vectors into predictions at once.</p>',
    '<p>Know dot products, L1 and L2 norms, Euclidean and cosine distances, matrix products and their shape rule, transposes, inverses, determinants and rank, and that ŷ = X w + b is the heart of linear models.</p>',
    '<p>Think of X w as a combination of the columns of X, so least squares projects y onto the column space. Rank deficiency and ill conditioning (a large ratio of largest to smallest singular value) make solutions unstable, which regularisation fixes.</p>',
    '<p>The spectral theorem says every real symmetric matrix is Q &Lambda; Q<sup>T</sup> with orthonormal Q. The singular value decomposition X = U &Sigma; V<sup>T</sup> generalises this to any matrix and gives the best low rank approximation (Eckart Young theorem), the base of PCA, latent semantic analysis and low rank adapters such as LoRA.</p>')}
{grow('Add and scale vectors, compute dot products and distances, multiply a matrix by a vector.',
      'Write a linear model as X w + b, check shapes, solve systems with NumPy, explain determinant and rank.',
      'Use projections, eigenvectors and the SVD, and reason about conditioning and multicollinearity.')}
''', kw=['beginner', 'expert', 'column space', 'condition number', 'spectral theorem', 'SVD', 'Eckart Young', 'LoRA'])

lc(1266, 'Minimum Time Visiting All Points', 'minimum-time-visiting-all-points', 'e', 'Chebyshev distance', 'Moving diagonally covers one step on both axes at once, so the time between two points is the larger of the two gaps, max(|dx|, |dy|). Add it for each pair of neighbours.', r'''
def min_time_to_visit_all_points(points):
    total = 0
    for i in range(1, len(points)):
        dx = abs(points[i][0] - points[i - 1][0])
        dy = abs(points[i][1] - points[i - 1][1])
        total = total + max(dx, dy)
    return total
''', [('min_time_to_visit_all_points([[1, 1], [3, 4], [-1, 0]])', 7), ('min_time_to_visit_all_points([[3, 2], [-2, 2]])', 5)])
lc(1779, 'Find Nearest Point That Has the Same X or Y Coordinate', 'find-nearest-point-that-has-the-same-x-or-y-coordinate', 'e', 'Manhattan distance with a filter', 'Skip points that share neither x nor y. For the rest, compute the Manhattan distance and keep the smallest, earliest index on ties.', r'''
def nearest_valid_point(x, y, points):
    best_index = -1
    best_distance = None
    for i in range(len(points)):
        px = points[i][0]
        py = points[i][1]
        if px == x or py == y:
            d = abs(px - x) + abs(py - y)
            if best_distance is None or d < best_distance:
                best_distance = d
                best_index = i
    return best_index
''', [('nearest_valid_point(3, 4, [[1, 2], [3, 1], [2, 4], [2, 3], [4, 4]])', 2), ('nearest_valid_point(3, 4, [[3, 4]])', 0), ('nearest_valid_point(3, 4, [[2, 3]])', -1)])
lc(566, 'Reshape the Matrix', 'reshape-the-matrix', 'e', 'Reshape by flattening (NumPy reshape by hand)', 'If r &times; c does not equal the number of values, return the original. Otherwise read the values row by row and fill the new shape row by row.', r'''
def matrix_reshape(mat, r, c):
    values = []
    for row in mat:
        for v in row:
            values.append(v)
    if len(values) != r * c:
        return mat
    result = []
    for i in range(r):
        result.append(values[i * c:(i + 1) * c])
    return result
''', [('matrix_reshape([[1, 2], [3, 4]], 1, 4)', [[1, 2, 3, 4]]), ('matrix_reshape([[1, 2], [3, 4]], 2, 4)', [[1, 2], [3, 4]])])
lc(1828, 'Queries on Number of Points Inside a Circle', 'queries-on-number-of-points-inside-a-circle', 'm', 'Euclidean distance without the square root', 'A point is inside when dx<sup>2</sup> + dy<sup>2</sup> &le; r<sup>2</sup>. Comparing squared distances avoids the square root and gives the same answer.', r'''
def count_points(points, queries):
    answer = []
    for qx, qy, r in queries:
        inside = 0
        for px, py in points:
            if (px - qx) ** 2 + (py - qy) ** 2 <= r * r:
                inside = inside + 1
        answer.append(inside)
    return answer
''', [('count_points([[1, 3], [3, 3], [5, 3], [2, 2]], [[2, 3, 1], [4, 3, 1], [1, 1, 2]])', [3, 2, 2])])
lc(1037, 'Valid Boomerang', 'valid-boomerang', 'e', 'Determinant (cross product) for collinearity', 'Three points lie on one line exactly when the 2 &times; 2 determinant of the two difference vectors is 0. If it is not 0, they form a boomerang.', r'''
def is_boomerang(points):
    ax = points[1][0] - points[0][0]
    ay = points[1][1] - points[0][1]
    bx = points[2][0] - points[0][0]
    by = points[2][1] - points[0][1]
    return ax * by - ay * bx != 0
''', [('is_boomerang([[1, 1], [2, 3], [3, 2]])', True), ('is_boomerang([[1, 1], [2, 2], [3, 3]])', False)])
lc(1886, 'Determine Whether Matrix Can Be Obtained By Rotation', 'determine-whether-matrix-can-be-obtained-by-rotation', 'e', 'Rotation as transpose plus reverse', 'A quarter turn is the transpose with each row reversed. Try up to four turns and compare with the target each time.', r'''
def rotate_quarter(mat):
    n = len(mat)
    turned = []
    for c in range(n):
        new_row = []
        for r in range(n - 1, -1, -1):
            new_row.append(mat[r][c])
        turned.append(new_row)
    return turned


def find_rotation(mat, target):
    for turn in range(4):
        if mat == target:
            return True
        mat = rotate_quarter(mat)
    return False
''', [('find_rotation([[0, 1], [1, 0]], [[1, 0], [0, 1]])', True), ('find_rotation([[0, 1], [1, 1]], [[1, 0], [0, 1]])', False)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>These problems practise distances (Chebyshev, Manhattan and Euclidean without the square root), reshaping, a determinant test and matrix rotation. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'Manhattan distance', 'Chebyshev distance', 'Euclidean distance', 'reshape', 'determinant', 'rotation'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>vector</b> is a list of numbers. Every example becomes a feature vector, and similar examples are close vectors.',
    'Dot product: multiply matching components and add. a &middot; b = ||a|| ||b|| cos &theta;.',
    'Euclidean (L2) distance is the straight line, Manhattan (L1) the sum of gaps, cosine compares directions. Scale features first.',
    'A <b>matrix</b> is a table. Matrix times vector is one dot product per row. Shapes: (n &times; k)(k &times; m) = (n &times; m).',
    'A linear model for all examples is ŷ = X w + b.',
    'det(A) &ne; 0 means A has an inverse. Use np.linalg.solve. Rank counts independent columns. Dependent features cause multicollinearity.',
    'Projections and eigenvectors (A v = &lambda; v) are the base of least squares and PCA.'],
    'Foundations 2.2 adds calculus: derivatives, gradients and how gradient descent uses them.')}
{files('Three tasks: Euclidean distance, cosine similarity, and a matrix times vector product, all by hand.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is the dot product of [1, 0] and [0, 1]?', ['1', '0', '2', '&minus;1'], 1, 'Multiply and add.', '1 &times; 0 + 0 &times; 1 = 0. The vectors are at a right angle.')
K.quiz('e', 'A dataset matrix has shape (100, 4). What do the 4 columns usually stand for?', ['Examples', 'Features', 'Labels', 'Models'], 1, 'Rows are examples.', 'Rows are examples, columns are features.')
K.quiz('e', 'Euclidean distance between (0, 0) and (3, 4)?', ['7', '5', '25', '12'], 1, 'Pythagoras.', '&radic;(9 + 16) = 5.')
K.quiz('e', 'Manhattan distance between (0, 0) and (3, 4)?', ['5', '7', '12', '25'], 1, 'Add the gaps.', '3 + 4 = 7.')
K.quiz('m', 'Cosine similarity of [1, 2] and [3, 6]?', ['0.5', '1', '0', '3'], 1, 'Same direction.', '[3, 6] is 3 &times; [1, 2], so the angle is 0 and cosine is 1.')
K.quiz('m', 'A is 3 &times; 2 and B is 2 &times; 5. What is the shape of A B?', ['2 &times; 2', '3 &times; 5', '5 &times; 3', 'Not defined'], 1, 'Outer sizes.', '(3 &times; 2)(2 &times; 5) = 3 &times; 5.')
K.quiz('m', 'det [[4, 2], [2, 1]] is', ['8', '0', '4', '&minus;4'], 1, 'a d &minus; b c.', '4 &times; 1 &minus; 2 &times; 2 = 0. The rows are multiples of each other.')
K.quiz('m', 'Why is cosine similarity popular for comparing documents?', ['It is faster than addition', 'It ignores document length and compares word mix', 'It is always positive', 'It needs no vectors'], 1, 'Long and short reviews.', 'Cosine looks at direction only, so a long review and a short one with the same word mix are similar.')
K.quiz('m', 'Which NumPy call solves A w = y best?', ['np.linalg.inv(A) @ y', 'np.linalg.solve(A, y)', 'A / y', 'np.dot(A, y)'], 1, 'Avoid the explicit inverse.', 'solve is faster and more accurate than forming the inverse.')
K.quiz('h', 'Features "size in m2" and "size in square feet" are both in X. What problem appears?', ['Underfitting', 'Multicollinearity: X has dependent columns', 'Class imbalance', 'Nothing'], 1, 'One column is a multiple of the other.', 'Dependent columns make X<sup>T</sup>X singular or nearly singular.')
K.quiz('h', 'A matrix has eigenvalues 2 and 3. What is its determinant?', ['5', '6', '1', '9'], 1, 'Product of eigenvalues.', 'det = 2 &times; 3 = 6.')
K.quiz('h', '||a &minus; b||<sup>2</sup> equals', ['||a||<sup>2</sup> &minus; ||b||<sup>2</sup>', '||a||<sup>2</sup> + ||b||<sup>2</sup> &minus; 2 a &middot; b', '(a &minus; b)<sup>2</sup> &middot; 2', 'a &middot; b'], 1, 'Expand (a &minus; b)&middot;(a &minus; b).', 'a&middot;a &minus; 2 a&middot;b + b&middot;b.')
K.quiz('x', 'In the style of an MIT 18.06 exam: A is 5 &times; 3 with rank 3. What is the rank of A<sup>T</sup>A?', ['5', '3', '15', '1'], 1, 'Same null space.', 'A<sup>T</sup>A is 3 &times; 3 with the same null space as A, so its rank is 3 and it is invertible.')
K.quiz('x', 'In the style of a Stanford CS229 exam: for symmetric S = [[2, 1], [1, 2]], which vector is an eigenvector with eigenvalue 3?', ['(1, 0)', '(1, 1)', '(1, &minus;1)', '(2, 1)'], 1, 'Try S v.', 'S (1, 1) = (3, 3) = 3 (1, 1). (1, &minus;1) has eigenvalue 1.')

K.calc('e', 'Dot product of [2, 3] and [4, 1]?', '11', 'Multiply pairs and add.', ['2 &times; 4 = 8.', '3 &times; 1 = 3.', eq('8 + 3 = 11')], check=2 * 4 + 3 * 1)
K.calc('e', 'L2 length of [6, 8]?', '10', '&radic;(36 + 64).', ['Squares 36 and 64.', 'Sum 100.', eq('&radic;100 = 10')], check=10)
K.calc('e', 'L1 length of [3, &minus;4, 2]?', '9', 'Add absolute values.', ['|3| = 3, |&minus;4| = 4, |2| = 2.', 'Add them.', eq('3 + 4 + 2 = 9')], check=9)
K.calc('m', 'Euclidean distance between (1, 2, 2) and (3, 5, 8)?', '7', 'Gaps 2, 3, 6.', ['Squares 4, 9, 36.', 'Sum 49.', eq('&radic;49 = 7')], check=7)
K.calc('m', 'Cosine similarity of [1, 0] and [1, 1]? Round to 3 decimals.', '0.707', '1 / (1 &times; &radic;2).', ['Dot = 1.', 'Lengths 1 and &radic;2.', eq('1 / 1.414 &asymp; 0.707')], check=round(1 / 2 ** 0.5, 3))
K.calc('m', 'det [[3, 1], [2, 4]]?', '10', 'a d &minus; b c.', ['3 &times; 4 = 12.', '1 &times; 2 = 2.', eq('12 &minus; 2 = 10')], check=3 * 4 - 1 * 2)
K.calc('m', 'Predict with w = [2, &minus;1], b = 3 for x = [4, 5].', '6', 'w &middot; x + b.', ['2 &times; 4 = 8.', '&minus;1 &times; 5 = &minus;5.', eq('8 &minus; 5 + 3 = 6')], check=2 * 4 - 5 + 3)
K.calc('h', 'Solve 2 w<sub>1</sub> + w<sub>2</sub> = 5 and w<sub>1</sub> + 3 w<sub>2</sub> = 10. What is w<sub>2</sub>?', '3', 'Use the inverse from the maths lesson.', ['A<sup>&minus;1</sup> = [[0.6, &minus;0.2], [&minus;0.2, 0.4]].', 'w<sub>2</sub> = &minus;0.2 &times; 5 + 0.4 &times; 10.', eq('&minus;1 + 4 = 3')], check=3)
K.calc('h', 'Projection of (3, 4) onto direction (1, 1). What is its first component?', '3.5', '((x&middot;d)/(d&middot;d)) d.', ['x &middot; d = 7.', 'd &middot; d = 2.', eq('(7/2) (1, 1) = (3.5, 3.5)')], check=3.5)
K.calc('x', 'In the style of an MIT 18.065 problem: the eigenvalues of [[4, 1], [2, 3]] solve &lambda;<sup>2</sup> &minus; 7&lambda; + 10 = 0. What is the larger eigenvalue?', '5', 'Factor the quadratic.', ['Trace 7, determinant 12 &minus; 2 = 10.', '(&lambda; &minus; 5)(&lambda; &minus; 2) = 0.', eq('&lambda; = 5 or 2, so the larger is 5')], check=5)

K.assign('euc', 'e', 'Euclidean distance by hand',
         '<p>Write <code>euclidean(u, v)</code> that returns the straight line distance between two lists of numbers of the same length, rounded to 3 decimals. Do not use NumPy.</p>',
         '''
def euclidean(u, v):
    # your code here
    pass
''', [('euclidean([0, 0], [3, 4])', 5.0), ('euclidean([1, 2, 2], [3, 5, 8])', 7.0), ('euclidean([1, 1], [2, 2])', 1.414)],
         '''
def euclidean(u, v):
    total = 0
    for a, b in zip(u, v):
        total = total + (a - b) ** 2
    return round(total ** 0.5, 3)
''', 'Add up the squared gaps with zip, then take ** 0.5 for the square root.', '<p>k nearest neighbours calls this function for every stored example. NumPy does the same with np.linalg.norm(u - v).</p>')
K.assign('cos', 'm', 'Cosine similarity by hand',
         '<p>Write <code>cosine(u, v)</code> that returns the cosine similarity of two non zero lists of the same length, rounded to 3 decimals.</p>',
         '''
def cosine(u, v):
    # your code here
    pass
''', [('cosine([1, 2], [2, 4])', 1.0), ('cosine([1, 0], [0, 1])', 0.0), ('cosine([1, 0], [1, 1])', 0.707), ('cosine([1, 1], [-1, -1])', -1.0)],
         '''
def cosine(u, v):
    dot = 0
    size_u = 0
    size_v = 0
    for a, b in zip(u, v):
        dot = dot + a * b
        size_u = size_u + a * a
        size_v = size_v + b * b
    return round(dot / (size_u ** 0.5 * size_v ** 0.5), 3)
''', 'In one loop add up the dot product and both squared lengths. Divide the dot product by the product of the two lengths.', '<p>Search engines and recommendation systems compare embedding vectors with exactly this formula.</p>')
K.assign('matvec', 'm', 'Matrix times vector',
         '<p>Write <code>mat_vec(M, v)</code> that returns M times v as a list: one dot product of each row of M with v.</p>',
         '''
def mat_vec(M, v):
    # your code here
    pass
''', [('mat_vec([[2, 1], [0, 1]], [1, 2])', [4, 2]), ('mat_vec([[1, 0], [0, 1]], [7, 9])', [7, 9]), ('mat_vec([[1, 2, 3]], [1, 1, 1])', [6])],
         '''
def mat_vec(M, v):
    result = []
    for row in M:
        total = 0
        for a, b in zip(row, v):
            total = total + a * b
        result.append(total)
    return result
''', 'Loop over the rows. For each row, compute its dot product with v and append it.', '<p>A linear model applied to a whole dataset is this function with M = X and v = w. NumPy writes it as M @ v.</p>')

K.must('Vectors', 'An example is a feature vector. Dot product a&middot;b = &Sigma; a<sub>i</sub>b<sub>i</sub> = ||a|| ||b|| cos &theta;. 0 means orthogonal.')
K.must('Distances', 'Euclidean &radic;&Sigma;(a<sub>i</sub>&minus;b<sub>i</sub>)<sup>2</sup>, Manhattan &Sigma;|a<sub>i</sub>&minus;b<sub>i</sub>|, cosine a&middot;b/(||a|| ||b||). Scale features first.')
K.must('Matrices', 'Matrix times vector: one dot product per row. (n&times;k)(k&times;m) = n&times;m. AB &ne; BA. (AB)<sup>T</sup> = B<sup>T</sup>A<sup>T</sup>.')
K.must('Linear model', 'ŷ = X w + b. Each weight is the change in prediction per unit of its feature.')
K.must('Inverse', 'det [[a,b],[c,d]] = ad &minus; bc. Inverse exists only if det &ne; 0. Use np.linalg.solve. Dependent columns mean multicollinearity.')
K.must('Eigen', 'A v = &lambda; v. Sum of eigenvalues = trace, product = determinant. Base of PCA.')

T = K.topic(
    slug='ml-linalg', topic='ml-linalg', step=(2, 'Maths you need', 'ml-f2', 'The linear algebra, calculus and probability that every model uses, explained with simple words, pictures and code.', 'Beginner'),
    title='Linear algebra for ML: vectors, distances and matrices', short='Linear algebra', badge='2.1', minutes=60,
    lead='See data the way a model sees it: every example is a vector, similarity is distance, a dataset is a matrix and a linear model is one matrix product. Then meet inverses, determinants, rank, projections and eigenvectors.',
    desc='vectors, dot product, L1 and L2 norms, Euclidean, Manhattan, cosine and Chebyshev distance, matrices, matrix vector and matrix matrix products, shape rule, identity, transpose, symmetric matrices, linear model X w + b, bias trick, systems of equations, np.linalg.solve, determinant, inverse, rank, multicollinearity, projection, eigenvalues and eigenvectors, SVD preview.',
    summary='vectors and distances, matrices and products, the linear model, inverses, rank, projections and eigenvectors.',
    keywords=['linear algebra', 'vector', 'dot product', 'Euclidean distance', 'cosine similarity', 'matrix multiplication', 'determinant', 'inverse', 'rank', 'eigenvalues'],
    recap='<p>Linear algebra is the language of data: examples are vectors, datasets are matrices, and models are matrix products.</p>',
    added='2026-11-13', leet=leet_items())
