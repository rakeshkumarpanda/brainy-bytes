# Unsupervised 2.1: principal component analysis. Checked against Pearson, On Lines and Planes of Closest Fit (1901),
# Hotelling, Analysis of a Complex of Statistical Variables into Principal Components (1933), Jolliffe, Principal
# Component Analysis (2nd edition, 2002), Scholkopf, Smola and Muller, Kernel PCA (1998), Halko, Martinsson and Tropp,
# randomized SVD (SIAM Review 2011), The Elements of Statistical Learning section 14.5, and the scikit-learn 1.8 user
# guide section 2.5.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-pca')
K = Kit()

K.code('pca_by_hand', r'''
import numpy as np

# Six students: hours studied and exam score move together
X = np.array([[2.0, 50], [3, 58], [4, 61], [5, 70], [6, 74], [7, 81]])
Xc = X - X.mean(axis=0)                          # 1. centre every feature at 0
C = Xc.T @ Xc / (len(X) - 1)                     # 2. covariance matrix
values, vectors = np.linalg.eigh(C)              # 3. eigenvalues come out smallest first
order = np.argsort(values)[::-1]
values, vectors = values[order], vectors[:, order]
vectors = vectors * np.sign(vectors[0])          # fix the sign so the output is stable
print("covariance matrix:", np.round(C, 2).tolist())
print("eigenvalues (variance along each component):", np.round(values, 3).tolist())
print("first component direction:", np.round(vectors[:, 0], 4).tolist())
print("share of variance kept by component 1:", round(float(values[0] / values.sum()), 4))
Z = Xc @ vectors[:, :1]                          # 4. project onto the first component
print("each student as one number:", np.round(Z[:, 0], 2).tolist())
''')

K.code('pca_sklearn', r'''
import numpy as np
from sklearn.decomposition import PCA

X = np.array([[2.0, 50], [3, 58], [4, 61], [5, 70], [6, 74], [7, 81]])
pca = PCA(n_components=2).fit(X)
print("explained variance:", np.round(pca.explained_variance_, 3).tolist())
print("explained variance ratio:", np.round(pca.explained_variance_ratio_, 4).tolist())
print("component 1 (up to sign):", np.round(np.abs(pca.components_[0]), 4).tolist())

U, S, Vt = np.linalg.svd(X - X.mean(axis=0), full_matrices=False)   # PCA through the SVD
print("from the SVD, S squared / (n - 1):", np.round(S ** 2 / (len(X) - 1), 3).tolist())
one = PCA(n_components=1).fit(X)
approx = one.inverse_transform(one.transform(X))
print("rebuilt from 1 number each:", np.round(approx, 1).tolist())
''')

K.code('digits_variance', r'''
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X, y = load_digits(return_X_y=True)              # 1,797 images of 8 x 8 pixels = 64 features
pca = PCA().fit(X)
cum = np.cumsum(pca.explained_variance_ratio_)
for k in [1, 2, 5, 10, 20, 30, 40]:
    print("components", str(k).rjust(2), " variance kept", round(float(cum[k - 1]), 3))
print("components needed for 90%:", int(np.argmax(cum >= 0.90)) + 1, " for 95%:", int(np.argmax(cum >= 0.95)) + 1)
print("PCA(0.95) picks", PCA(n_components=0.95).fit(X).n_components_, "components by itself")
''', long=True)

K.code('reconstruct', r'''
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X, _ = load_digits(return_X_y=True)
for k in [2, 5, 10, 20, 40, 64]:
    pca = PCA(n_components=k).fit(X)
    back = pca.inverse_transform(pca.transform(X))
    err = np.mean((X - back) ** 2)
    print("keep", str(k).rjust(2), "of 64 numbers  mean squared error", round(float(err), 3) + 0.0)
''', long=True)

K.code('scaling_pca', r'''
import numpy as np
from sklearn.datasets import load_wine
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

data = load_wine()
X, names = data.data, data.feature_names
for label, Z in [("raw", X), ("scaled", StandardScaler().fit_transform(X))]:
    pca = PCA(n_components=2).fit(Z)
    top = np.argsort(np.abs(pca.components_[0]))[::-1][:2]
    print(label.ljust(6), " variance in PC1", round(float(pca.explained_variance_ratio_[0]), 3),
          " biggest weights:", [names[i] for i in top])
print("proline ranges up to", int(X[:, 12].max()), "while hue stays below", round(float(X[:, 10].max()), 2))
''', long=True)

K.code('pca_pipeline', r'''
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_digits(return_X_y=True)
for k in [5, 10, 20, 30, None]:
    steps = [StandardScaler()] + ([PCA(n_components=k)] if k else []) + [LogisticRegression(max_iter=2000)]
    score = cross_val_score(make_pipeline(*steps), X, y, cv=5).mean()
    print(("PCA " + str(k) if k else "no PCA (64)").ljust(12), " accuracy", round(float(score), 3))
''', long=True)

K.code('kernel_pca', r'''
from sklearn.datasets import make_circles
from sklearn.decomposition import PCA, KernelPCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

X, y = make_circles(n_samples=400, factor=0.3, noise=0.05, random_state=0)
for name, model in [("PCA", PCA(n_components=1)),
                    ("kernel PCA gamma 2", KernelPCA(n_components=1, kernel="rbf", gamma=2)),
                    ("kernel PCA gamma 15", KernelPCA(n_components=1, kernel="rbf", gamma=15))]:
    Z = model.fit_transform(X)                     # keep only one number per point
    acc = cross_val_score(LogisticRegression(), Z, y, cv=5).mean()
    print(name.ljust(19), " accuracy from one component", round(float(acc), 3))
''', long=True)

K.lesson('idea', 'The idea: keep the directions where data spreads most', f'''
{src('Pearson (1901), Hotelling (1933), Jolliffe, Principal Component Analysis (2002), and The Elements of Statistical Learning section 14.5.')}
{viz('mlpca')}
{wwh('<b>Principal component analysis</b> (PCA) finds new axes, called <b>principal components</b>, that point along the directions where the data varies most. The first component has the most variance, the second has the most of what is left and is at right angles to the first, and so on. Keeping only the first few components describes each point with fewer numbers.',
     'Many datasets have dozens or thousands of features that move together. PCA removes that overlap: it compresses data, speeds up later models, removes some noise, and lets you plot high dimensional data in 2D. It is the most used dimensionality reduction method.',
     'Centre each feature at 0. Compute the covariance matrix. Its eigenvectors are the components and its eigenvalues are the variances along them. Sort by eigenvalue, keep the top k eigenvectors, and project the data onto them.')}
{run('pca_by_hand')}
{note('Hours and scores rise together, so almost all the variation lies along one line. The first component keeps 99.97% of the variance, so each student can be described by one number instead of two with almost no loss. The direction (0.16, 0.99) is mostly along the score axis, because scores vary in tens of points and hours only in single hours. The scaling lesson comes back to this.', 'exam')}
{fxs(fx('Covariance matrix', 'C = X<sub>c</sub><sup>T</sup> X<sub>c</sub> / (n &minus; 1)', 'X<sub>c</sub> is the centred data, n rows.', key=True),
     fx('Eigen equation', 'C v = &lambda; v', 'v is a component direction, &lambda; the variance along it.', key=True),
     fx('Projection', 'Z = X<sub>c</sub> V<sub>k</sub>', 'V<sub>k</sub> holds the top k eigenvectors as columns.', key=True))}
{scene('taking the best photo of a statue', '<p>A photo turns a 3D statue into a 2D picture, so something is always lost. A good photographer walks around until the statue looks widest and most recognisable. PCA does the same with data: among all the ways to flatten it, it picks the view that keeps the points as spread out as possible.</p>')}
''', kw=['PCA', 'principal component analysis', 'principal components', 'covariance matrix', 'eigenvector', 'eigenvalue', 'projection', 'dimensionality reduction'])

K.lesson('sklearn', 'PCA in scikit-learn and the SVD', f'''
{wwh('scikit-learn’s PCA centres the data and computes the components with the <b>singular value decomposition</b> (SVD) of the centred data, which is more accurate than forming the covariance matrix. It stores the directions in components_, the variances in explained_variance_ and their shares in explained_variance_ratio_.',
     'The SVD X<sub>c</sub> = U S V<sup>T</sup> gives the components directly as the rows of V<sup>T</sup>, and the variances as S<sup>2</sup> / (n &minus; 1). inverse_transform maps the reduced data back to the original features, so you can see exactly what was lost.',
     'PCA(n_components=2).fit(X), then transform(X) for the new coordinates and inverse_transform for the reconstruction. Signs of components are arbitrary: a component and its negative describe the same axis.')}
{run('pca_sklearn')}
{note('The SVD gives the same variances as the eigenvalues of the covariance matrix (133.328 and 0.038). Rebuilt from one number each, the points move only slightly onto the line: 4 hours becomes 3.7 and 6 hours becomes 5.9, while the scores stay almost exactly as they were.', 'tip')}
''', kw=['PCA scikit-learn', 'SVD', 'singular value decomposition', 'explained_variance_ratio_', 'components_', 'inverse_transform'])

K.lesson('howmany', 'How many components to keep', f'''
{viz('mlscree')}
{wwh('The <b>explained variance ratio</b> of a component is its eigenvalue divided by the sum of all eigenvalues. A <b>scree plot</b> shows these ratios in order, and the cumulative sum shows how much the first k components keep together.',
     'Too few components lose real structure, and too many keep noise and save little. The choice depends on the purpose: 2 or 3 for a picture, a variance target such as 95% for compression, or whatever gives the best score for a model that follows.',
     'Look for the elbow where the bars flatten, or pass a fraction: PCA(n_components=0.95) keeps the fewest components that reach 95%. When PCA feeds a model, tune n_components with cross validation like any other setting.')}
{run('digits_variance')}
{note('Each digit image has 64 pixel values. The first 2 components keep only 28.5% of the variance, which is enough for a rough picture but not for detail. 21 components keep 90% and 29 keep 95%, so more than half of the 64 numbers are close to redundant.', 'exam')}
{run('reconstruct')}
{note('The reconstruction error falls quickly at first and then slowly. With 20 of the 64 numbers the average squared pixel error is about 2, on a pixel scale of 0 to 16, and the digits are easy to read again. The error with k components equals the sum of the variances that were dropped.', 'tip')}
''', kw=['explained variance ratio', 'scree plot', 'cumulative variance', 'choosing components', 'reconstruction error', 'n_components'])

K.lesson('practice', 'Scaling, pipelines and pitfalls', f'''
{wwh('PCA looks for the largest variance, so a feature measured in big units wins even when it is not important. <b>Standardise</b> features first unless they share units. Inside a model, put PCA in a <b>pipeline</b> so that it is fitted only on the training folds.',
     'Unscaled PCA on mixed units mostly rediscovers the feature with the biggest numbers. Fitting PCA on all the data before splitting leaks information from the test set. Both mistakes are common in exams and in practice.',
     'make_pipeline(StandardScaler(), PCA(n_components=k), model). Remember that PCA ignores the labels: the directions of most variance are not always the ones that separate the classes best.')}
{run('scaling_pca')}
{note('In the wine data, proline goes up to 1680 while hue stays below 1.71. Unscaled, the first component explains 99.8% of the variance, but almost all of that is proline, which tells you nothing new. After scaling, the first component explains 36.2% and is led by flavanoids and total phenols, a real combination of related features.', 'exam')}
{run('pca_pipeline')}
{note('With the full 64 features, logistic regression scores 0.92. With 30 components it scores 0.907 using half the features, and with 10 it still scores 0.84. PCA here trades a little accuracy for a smaller, faster model. It does not always help accuracy, because the label is not used to choose the directions.', 'tip')}
''', kw=['PCA scaling', 'StandardScaler', 'pipeline', 'data leakage', 'PCA before classification', 'unsupervised'])

K.lesson('kernel', 'Kernel PCA and PCA at scale', f'''
{src('Scholkopf, Smola and Muller, Nonlinear Component Analysis as a Kernel Eigenvalue Problem (1998), Halko, Martinsson and Tropp, Finding Structure with Randomness (SIAM Review 2011), and the scikit-learn 1.8 decomposition documentation.')}
{wwh('PCA finds only straight directions. <b>Kernel PCA</b> first maps the data into a richer space through a kernel, as an SVM does, and runs PCA there, so it can unfold curved structure. For very large data, <b>randomized PCA</b> finds the top components quickly and <b>IncrementalPCA</b> fits in batches that fit in memory.',
     'Data on circles, spirals or curved surfaces has no good straight direction. Kernel PCA can turn such structure into a few useful numbers. On millions of rows or features, the exact SVD is too slow, and the approximate methods are almost as accurate.',
     'KernelPCA(n_components=2, kernel="rbf", gamma=...) with gamma tuned. PCA(svd_solver="randomized") for big dense data, IncrementalPCA(batch_size=...) for data that does not fit in memory, and TruncatedSVD for sparse matrices such as text.')}
{run('kernel_pca')}
{note('Two circles, one inside the other, cannot be separated by any straight direction, so one PCA component gives 45% accuracy, no better than guessing. Kernel PCA with gamma 2 turns them into one number that separates them perfectly. With gamma 15 the kernel is too narrow and accuracy drops to 71%, so gamma needs tuning.', 'exam')}
''', kw=['kernel PCA', 'randomized PCA', 'IncrementalPCA', 'TruncatedSVD', 'nonlinear dimensionality reduction', 'gamma'])

K.lesson('versus', 'PCA compared', f'''
{versus('PCA and related methods', ['', 'PCA', 'Feature selection', 'LDA', 't-SNE and UMAP', 'Autoencoder'], [
    ['Uses labels', 'No', 'Sometimes', 'Yes', 'No', 'No'],
    ['New features', 'Linear mixes of all features', 'A subset of the originals', 'Linear mixes', 'Nonlinear map', 'Nonlinear mixes'],
    ['Keeps', 'Most variance', 'Most useful features', 'Best class separation', 'Local neighbours', 'What rebuilds the input best'],
    ['Transform new data', 'Yes', 'Yes', 'Yes', 'No for t-SNE, yes for UMAP', 'Yes'],
    ['Interpretable', 'Partly (loadings)', 'Yes', 'Partly', 'No', 'No'],
    ['Speed', 'Fast', 'Varies', 'Fast', 'Slow on big data', 'Needs training']],
    'use PCA first for compression, noise reduction and a quick look, LDA when you have labels and want separation, and t-SNE or UMAP (next chapter) for pictures of clusters.')}
{note('A linear autoencoder with a squared error loss and k hidden units learns the same subspace as PCA with k components, though not necessarily the same axes. So PCA is the simplest autoencoder.', 'exam')}
''', kw=['PCA vs LDA', 'PCA vs feature selection', 'PCA vs t-SNE', 'PCA vs autoencoder'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('First component', 'v<sub>1</sub> = argmax<sub>|v| = 1</sub> v<sup>T</sup> C v', 'The unit direction with the largest variance.', key=True),
     fx('Solution', 'C v<sub>1</sub> = &lambda;<sub>1</sub> v<sub>1</sub>, variance = &lambda;<sub>1</sub>', 'The top eigenvector and its eigenvalue.', key=True),
     fx('Explained variance ratio', '&lambda;<sub>j</sub> / &Sigma;<sub>i</sub> &lambda;<sub>i</sub>', 'Share of the total variance.', key=True),
     fx('SVD route', 'X<sub>c</sub> = U S V<sup>T</sup>, &lambda;<sub>j</sub> = s<sub>j</sub><sup>2</sup> / (n &minus; 1)', 'Components are the rows of V<sup>T</sup>.', key=True),
     fx('Reconstruction', 'X&#770; = Z V<sub>k</sub><sup>T</sup> + mean', 'Map back to the original features.'),
     fx('Reconstruction error', '(1/(n &minus; 1)) |X<sub>c</sub> &minus; X<sub>c</sub> V<sub>k</sub> V<sub>k</sub><sup>T</sup>|<sup>2</sup> = &Sigma;<sub>j &gt; k</sub> &lambda;<sub>j</sub>', 'The dropped variance.', key=True))}
{steps('Worked example: PCA of a 2 by 2 covariance matrix', [
    'C = [[3, 1], [1, 3]].',
    'Eigenvalues solve (3 &minus; &lambda;)<sup>2</sup> &minus; 1 = 0, so 3 &minus; &lambda; = &plusmn;1.',
    eq('&lambda;<sub>1</sub> = 4, &lambda;<sub>2</sub> = 2'),
    'For &lambda; = 4 the eigenvector is (1, 1) / &radic;2, the diagonal direction.',
    'Component 1 keeps 4 / (4 + 2) = 2/3 of the variance.'])}
{deep('Two views that give the same answer', '<p>Pearson in 1901 asked for the line that is closest to the points, minimising the sum of squared perpendicular distances. Hotelling in 1933 asked for the direction of largest variance. For centred data they are the same: each point’s squared distance from the origin splits into the squared length of its projection plus its squared distance to the line, and the total is fixed. So maximising the projected variance is the same as minimising the squared distances. The Eckart and Young theorem (1936) goes further: keeping the top k singular values gives the best rank k approximation of the data in squared error. PCA is optimal among linear projections, and only among those.</p>')}
''', kw=['PCA objective', 'eigen decomposition', 'SVD', 'Eckart Young', 'reconstruction error formula', 'Rayleigh quotient'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>PCA finds the directions in which the data spreads most and describes each point with fewer numbers along those directions.</p>',
    '<p>Scale the features, fit PCA, read explained_variance_ratio_, choose k with a scree plot or a variance target, and put PCA in a pipeline.</p>',
    '<p>Derive PCA as an eigenvalue problem, connect it to the SVD, show that the reconstruction error equals the dropped eigenvalues, and know when kernel PCA is needed.</p>',
    '<p>Study the Eckart and Young theorem, probabilistic PCA and factor analysis, sparse and robust PCA, randomized numerical linear algebra, and random matrix limits that separate signal eigenvalues from noise.</p>')}
{grow('Explain directions of largest spread.',
      'Reduce, compress and model with PCA in practice.',
      'Derive and analyse PCA and its variants.')}
''', kw=['beginner', 'expert', 'probabilistic PCA', 'robust PCA', 'random matrix theory'])

lc(867, 'Transpose Matrix', 'transpose-matrix', 'e', 'Swap rows and columns', 'Row i of the answer is column i of the input. The transpose appears in every PCA formula, starting with the covariance matrix X<sup>T</sup> X.', r"""
def transpose(matrix):
    return [list(col) for col in zip(*matrix)]
""", [('transpose([[1, 2, 3], [4, 5, 6]])', [[1, 4], [2, 5], [3, 6]]), ('transpose([[1]])', [[1]])])
lc(48, 'Rotate Image', 'rotate-image', 'm', 'Transpose, then reverse every row', 'A quarter turn clockwise is a transpose followed by flipping each row. PCA is also a rotation: it turns the axes to line up with the directions of most variance. LeetCode changes the matrix in place, and ours also returns it so it can be checked.', r"""
def rotate(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()
    return matrix
""", [('rotate([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', [[7, 4, 1], [8, 5, 2], [9, 6, 3]]), ('rotate([[1, 2], [3, 4]])', [[3, 1], [4, 2]])])
lc(2482, 'Difference Between Ones and Zeros in Row and Column', 'difference-between-ones-and-zeros-in-row-and-column', 'm', 'Count once per row and once per column', 'Precompute the number of ones in each row and each column. Then each cell is 2 &times; ones in its row + 2 &times; ones in its column &minus; rows &minus; columns. Row and column totals are also the first step of centring data.', r"""
def ones_minus_zeros(grid):
    m, n = len(grid), len(grid[0])
    row = [sum(r) for r in grid]
    col = [sum(grid[i][j] for i in range(m)) for j in range(n)]
    return [[2 * row[i] + 2 * col[j] - m - n for j in range(n)] for i in range(m)]
""", [('ones_minus_zeros([[0, 1, 1], [1, 0, 1], [0, 0, 1]])', [[0, 0, 4], [0, 0, 4], [-2, -2, 2]]), ('ones_minus_zeros([[1, 1, 1], [1, 1, 1]])', [[5, 5, 5], [5, 5, 5]])])
lc(1329, 'Sort the Matrix Diagonally', 'sort-the-matrix-diagonally', 'm', 'Group cells by i minus j', 'Cells on the same diagonal share the value i &minus; j. Collect each diagonal, sort it, and write it back in order. The diagonal of a covariance matrix holds the variances, and an eigen decomposition turns the whole matrix diagonal.', r"""
def diagonal_sort(mat):
    m, n = len(mat), len(mat[0])
    diag = {}
    for i in range(m):
        for j in range(n):
            diag.setdefault(i - j, []).append(mat[i][j])
    for key in diag:
        diag[key].sort(reverse=True)
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            out[i][j] = diag[i - j].pop()
    return out
""", [('diagonal_sort([[3, 3, 1, 1], [2, 2, 1, 2], [1, 1, 1, 2]])', [[1, 1, 1, 1], [1, 2, 2, 2], [1, 2, 3, 3]])])
lc(1314, 'Matrix Block Sum', 'matrix-block-sum', 'm', 'Two dimensional prefix sums', 'Build P where P[i][j] is the sum of the top left i by j block. Any rectangle sum is then four lookups. The same trick computes many means and covariances over windows quickly.', r"""
def matrix_block_sum(mat, k):
    m, n = len(mat), len(mat[0])
    P = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            P[i + 1][j + 1] = mat[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            r1, c1, r2, c2 = max(0, i - k), max(0, j - k), min(m, i + k + 1), min(n, j + k + 1)
            out[i][j] = P[r2][c2] - P[r1][c2] - P[r2][c1] + P[r1][c1]
    return out
""", [('matrix_block_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1)', [[12, 21, 16], [27, 45, 33], [24, 39, 28]])])
lc(1074, 'Number of Submatrices That Sum to Target', 'number-of-submatrices-that-sum-to-target', 'h', 'Fix two rows, then count subarrays with a hash map', 'For every pair of top and bottom rows, add the columns between them into one array. Then count subarrays of that array with the target sum using running sums and a dictionary. It reduces a two dimensional problem to many one dimensional ones, much as PCA reduces dimensions.', r"""
def num_submatrix_sum_target(matrix, target):
    m, n = len(matrix), len(matrix[0])
    count = 0
    for top in range(m):
        cols = [0] * n
        for bottom in range(top, m):
            for j in range(n):
                cols[j] += matrix[bottom][j]
            seen = {0: 1}
            running = 0
            for v in cols:
                running = running + v
                count = count + seen.get(running - target, 0)
                seen[running] = seen.get(running, 0) + 1
    return count
""", [('num_submatrix_sum_target([[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0)', 4), ('num_submatrix_sum_target([[1, -1], [-1, 1]], 0)', 5)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>PCA is matrix work. These problems practise transposing and rotating matrices, row and column totals, working along diagonals, two dimensional prefix sums for fast block statistics, and reducing a two dimensional search to one dimension. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'matrix', 'transpose', 'rotation', 'prefix sums', 'hash map'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>PCA</b> finds orthogonal directions of decreasing variance: the eigenvectors of the covariance matrix, with the eigenvalues as their variances.',
    'Centre the data, and <b>standardise</b> it when the features have different units.',
    'scikit-learn uses the <b>SVD</b>: &lambda; = s<sup>2</sup> / (n &minus; 1). Signs of components are arbitrary.',
    'Choose k with the scree plot, a variance target such as PCA(0.95), or cross validation of the next model.',
    'The reconstruction error equals the sum of the dropped eigenvalues. PCA is the best linear projection for squared error.',
    'PCA ignores labels and sees only straight directions. Kernel PCA handles curves, and randomized or incremental PCA handles big data.'],
    'Unsupervised 2.2 covers manifold learning: t-SNE, UMAP, MDS and Isomap for nonlinear pictures of data.')}
{files('Three tasks: centring columns, a 2 by 2 covariance matrix, and the share of variance in the first component.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'The first principal component points in the direction of', ['The smallest variance', 'The largest variance', 'The first feature', 'The labels'], 1, 'Most spread.', 'Each next component takes the most of what is left.')
K.quiz('e', 'Before PCA the data must be', ['Sorted', 'Centred at 0', 'Rounded', 'Labelled'], 1, 'Subtract the mean.', 'scikit-learn does this for you.')
K.quiz('e', 'Principal components are', ['Parallel', 'Orthogonal (at right angles)', 'Random', 'Always the original axes'], 1, 'Eigenvectors of a symmetric matrix.', 'They never overlap.')
K.quiz('e', 'explained_variance_ratio_ gives', ['The accuracy', 'The share of total variance in each component', 'The number of rows', 'The loss'], 1, 'Shares add to 1 over all components.', 'Use it to choose k.')
K.quiz('m', 'Why standardise features before PCA when units differ?', ['To make it faster', 'Otherwise the feature with the largest units dominates the variance', 'PCA needs integers', 'To add labels'], 1, 'Variance depends on units.', 'Proline dominated the wine data.')
K.quiz('m', 'PCA(n_components=0.95) means', ['Keep 95 components', 'Keep the fewest components that explain at least 95% of the variance', 'Drop 5% of rows', 'Use 95% of the data'], 1, 'A fraction, not a count.', 'scikit-learn picks k for you.')
K.quiz('m', 'The variance along a component equals', ['Its eigenvector length', 'Its eigenvalue', 'The trace', 'Zero'], 1, 'C v = &lambda; v.', 'And the eigenvalues add up to the total variance.')
K.quiz('m', 'Fitting PCA on the whole dataset before a train test split', ['Is always fine', 'Leaks test information into the training step', 'Is required', 'Removes noise only'], 1, 'Fit on training data only.', 'Use a pipeline.')
K.quiz('m', 'PCA can fail to help classification because', ['It is too slow', 'It ignores labels, so the top variance directions may not separate the classes', 'It needs many components', 'It only works on images'], 1, 'Unsupervised.', 'LDA uses the labels.')
K.quiz('h', 'scikit-learn computes PCA through', ['Gradient descent', 'The SVD of the centred data', 'k-means', 'A decision tree'], 1, 'More stable than forming X<sup>T</sup>X.', '&lambda; = s<sup>2</sup>/(n &minus; 1).')
K.quiz('h', 'The reconstruction error when keeping k components equals', ['Zero', 'The sum of the dropped eigenvalues', 'The largest eigenvalue', 'k'], 1, 'Dropped variance.', 'A clean exam result.')
K.quiz('h', 'Two circles, one inside the other, are best reduced to one useful number by', ['PCA', 'Kernel PCA with a suitable rbf gamma', 'Dropping a feature', 'Sorting'], 1, 'Nonlinear.', 'Plain PCA gave 45% accuracy.')
K.quiz('x', 'In the style of a Stanford CS229 exam: maximising projected variance for centred data is equivalent to', ['Maximising the reconstruction error', 'Minimising the sum of squared perpendicular distances to the subspace', 'Minimising the number of features', 'Maximising the likelihood of the labels'], 1, 'Pythagoras.', 'Projected length squared plus distance squared is fixed.')
K.quiz('x', 'In the style of an MIT 18.065 exam: the best rank k approximation of a matrix in squared error comes from', ['Its first k rows', 'Its top k singular values and vectors (Eckart and Young)', 'Random projection', 'Its diagonal'], 1, 'Eckart and Young (1936).', 'That is exactly what PCA keeps.')

K.calc('e', 'A feature has values 2, 4, 6. After centring, the first value is?', '-2', 'Subtract the mean.', ['Mean = 12 / 3 = 4.', 'First value 2.', eq('2 &minus; 4 = &minus;2')], check=-2)
K.calc('e', 'Eigenvalues 6, 3, 1. Share of variance in component 1?', '0.6', '&lambda;<sub>1</sub> / total.', ['Total 6 + 3 + 1 = 10.', 'Component 1: 6.', eq('6 / 10 = 0.6')], check=0.6)
K.calc('e', 'Same eigenvalues. Share kept by the first two components?', '0.9', 'Cumulative.', ['6 + 3 = 9.', 'Total 10.', eq('9 / 10 = 0.9')], check=0.9)
K.calc('m', 'Covariance [[4, 0], [0, 1]]. Share of variance in component 1?', '0.8', 'Diagonal matrix: the eigenvalues are on the diagonal.', ['Eigenvalues 4 and 1.', 'Total 5.', eq('4 / 5 = 0.8')], check=0.8)
K.calc('m', 'Largest eigenvalue of [[3, 1], [1, 3]]?', '4', 'Solve (3 &minus; &lambda;)<sup>2</sup> = 1.', ['3 &minus; &lambda; = &plusmn;1.', '&lambda; = 2 or 4.', eq('&lambda;<sub>1</sub> = 4')], check=4)
K.calc('m', 'Project the centred point (3, 4) onto the unit direction (0.6, 0.8). Coordinate?', '5', 'Dot product.', ['3 &times; 0.6 = 1.8.', '4 &times; 0.8 = 3.2.', eq('1.8 + 3.2 = 5')], check=5)
K.calc('m', 'Images with 64 pixels kept as 20 components. How many times fewer numbers per image?', '3.2', '64 / 20.', ['64 numbers before.', '20 after.', eq('64 / 20 = 3.2')], check=3.2)
K.calc('h', 'Eigenvalues 5, 3, 1, 1. Keep 2 components. Share of variance lost?', '0.2', 'Dropped eigenvalues over total.', ['Total 10.', 'Dropped 1 + 1 = 2.', eq('2 / 10 = 0.2')], check=0.2)
K.calc('h', 'n = 26 rows, top singular value 10. Variance of component 1?', '4', 's<sup>2</sup> / (n &minus; 1).', ['s<sup>2</sup> = 100.', 'n &minus; 1 = 25.', eq('100 / 25 = 4')], check=4)
K.calc('x', 'In the style of an MIT 6.036 problem: how many distinct numbers are in the covariance matrix of 1,000 features?', '500500', 'Symmetric: d(d + 1)/2.', ['d = 1,000.', 'd(d + 1) = 1,001,000.', eq('1,001,000 / 2 = 500,500')], check=500500)

K.assign('centre', 'e', 'Centre the columns',
         '<p>Write <code>centre_columns(rows)</code> that subtracts each column’s mean from every value in that column. Return the new rows with values rounded to 4 decimals.</p>',
         """
def centre_columns(rows):
    # your code here
    pass
""", [('centre_columns([[1, 2], [3, 4]])', [[-1.0, -1.0], [1.0, 1.0]]), ('centre_columns([[2, 0], [4, 0], [6, 3]])', [[-2.0, -1.0], [0.0, -1.0], [2.0, 2.0]])],
         """
def centre_columns(rows):
    n, d = len(rows), len(rows[0])
    means = [sum(r[j] for r in rows) / n for j in range(d)]
    return [[round(r[j] - means[j], 4) + 0.0 for j in range(d)] for r in rows]
""", 'Compute the mean of every column first, then subtract.', '<p>Adding 0.0 turns a possible &minus;0.0 into 0.0, which keeps printed answers clean.</p>')
K.assign('cov2', 'm', 'A 2 by 2 covariance matrix',
         '<p>Write <code>covariance_2d(points)</code> for a list of [x, y]. Return [[var x, cov], [cov, var y]] using n &minus; 1 in the denominator, rounded to 4 decimals.</p>',
         """
def covariance_2d(points):
    # your code here
    pass
""", [('covariance_2d([[1, 2], [2, 4], [3, 6]])', [[1.0, 2.0], [2.0, 4.0]]), ('covariance_2d([[0, 0], [2, 0]])', [[2.0, 0.0], [0.0, 0.0]])],
         """
def covariance_2d(points):
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points) / (n - 1)
    syy = sum((p[1] - my) ** 2 for p in points) / (n - 1)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points) / (n - 1)
    return [[round(sxx, 4), round(sxy, 4)], [round(sxy, 4), round(syy, 4)]]
""", 'Centre, then average the products of deviations.', '<p>In the first test y = 2x exactly, so the covariance matrix has one zero eigenvalue: all the variance lies on one line.</p>')
K.assign('pc1_share', 'h', 'Share of the first component',
         '<p>Write <code>pc1_share(cov)</code> for a symmetric 2 by 2 covariance matrix [[a, b], [b, d]]. Use the formula &lambda; = (a + d)/2 &plusmn; &radic;(((a &minus; d)/2)<sup>2</sup> + b<sup>2</sup>) and return the larger eigenvalue divided by the sum of both, rounded to 4 decimals.</p>',
         """
import math


def pc1_share(cov):
    # your code here
    pass
""", [('pc1_share([[1, 2], [2, 4]])', 1.0), ('pc1_share([[2, 0], [0, 2]])', 0.5), ('pc1_share([[3, 1], [1, 3]])', 0.6667)],
         """
import math


def pc1_share(cov):
    a, b, d = cov[0][0], cov[0][1], cov[1][1]
    mid = (a + d) / 2
    rad = math.sqrt(((a - d) / 2) ** 2 + b ** 2)
    big, small = mid + rad, mid - rad
    return round(big / (big + small), 4)
""", 'Use the closed form for the eigenvalues of a symmetric 2 by 2 matrix.', '<p>The sum of the eigenvalues is the trace a + d, the total variance, so the answer is also &lambda;<sub>1</sub> / (a + d).</p>')

K.must('Idea', 'Orthogonal directions of decreasing variance. Eigenvectors of the covariance matrix, eigenvalues are their variances.')
K.must('Steps', 'Centre (and scale if units differ), covariance or SVD, sort by eigenvalue, keep top k, project Z = X<sub>c</sub> V<sub>k</sub>.')
K.must('Choosing k', 'explained_variance_ratio_, scree elbow, PCA(0.95), or cross validation of the next model.')
K.must('Facts', '&lambda; = s<sup>2</sup>/(n &minus; 1). Reconstruction error = sum of dropped eigenvalues. Max variance = min squared distance.')
K.must('Pitfalls', 'Unscaled mixed units, fitting before the split, ignoring labels, sign flips, only straight directions.')
K.must('Variants', 'Kernel PCA for curves, randomized and IncrementalPCA for big data, TruncatedSVD for sparse text.')

T = K.topic(
    slug='ml-pca', topic='ml-pca', step=(2, 'Dimensionality reduction', 'ml-u2', 'Squeeze many features into a few that keep what matters, to see, compress and speed up later models.', 'Intermediate'),
    title='Principal component analysis (PCA)', short='PCA', badge='2.1', minutes=50,
    lead='Reduce many features to a few: find the directions of most variance with eigenvectors and the SVD, choose how many to keep, scale and pipeline correctly, rebuild data from components, and unfold curves with kernel PCA.',
    desc='principal component analysis, PCA, principal components, covariance matrix, eigenvectors, eigenvalues, SVD, explained variance ratio, scree plot, reconstruction error, standardisation, pipeline, kernel PCA, randomized PCA, IncrementalPCA, TruncatedSVD, Eckart Young.',
    summary='Directions of most variance, eigenvalues and the SVD, choosing k, scaling, reconstruction, and kernel PCA.',
    keywords=['PCA', 'principal components', 'eigenvalues', 'SVD', 'explained variance', 'scree plot', 'dimensionality reduction', 'kernel PCA', 'reconstruction error', 'covariance matrix'],
    recap='<p>PCA rotates the axes to follow the spread of the data and keeps the few that matter. It is fast, linear and unsupervised, and it is the first tool for compressing or picturing many features.</p>',
    added='2026-11-13', leet=leet_items())
