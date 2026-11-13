# Supervised 3.1: decision trees. Checked against Breiman, Friedman, Olshen and Stone, Classification and Regression
# Trees (1984), Quinlan, C4.5: Programs for Machine Learning (1993), Hastie, Tibshirani and Friedman, The Elements of
# Statistical Learning section 9.2, James and others, An Introduction to Statistical Learning chapter 8, Strobl and
# others, Bias in random forest variable importance measures (2007), and the scikit-learn 1.8 user guide section 1.10.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-trees')
K = Kit()

K.code('tree_iris', r'''
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, export_text

iris = load_iris()
tree = DecisionTreeClassifier(max_depth=2, random_state=0).fit(iris.data, iris.target)
names = [n.replace(" (cm)", "") for n in iris.feature_names]
print(export_text(tree, feature_names=names, class_names=list(iris.target_names)))
print("training accuracy:", round(tree.score(iris.data, iris.target), 3))
print("a flower 5.0, 3.4, 1.5, 0.2 is:", str(iris.target_names[tree.predict([[5.0, 3.4, 1.5, 0.2]])[0]]))
''')

K.code('gini_by_hand', r'''
hours = [1, 2, 3, 4, 5, 6, 7, 8]
passed = ["no", "no", "no", "no", "yes", "no", "yes", "yes"]

def gini(labels):
    if not labels:
        return 0.0
    p = labels.count("yes") / len(labels)
    return 1 - p ** 2 - (1 - p) ** 2

print("Gini before any split:", round(gini(passed), 3))
best = None
for i in range(1, len(hours)):
    cut = (hours[i - 1] + hours[i]) / 2
    left = [passed[j] for j in range(len(hours)) if hours[j] < cut]
    right = [passed[j] for j in range(len(hours)) if hours[j] >= cut]
    weighted = (len(left) * gini(left) + len(right) * gini(right)) / len(hours)
    print("cut at", cut, " left", len(left), " right", len(right), " weighted Gini", round(weighted, 3))
    if best is None or weighted < best[1]:
        best = (cut, weighted)
print("best cut:", best[0], " Gini drops by", round(gini(passed) - best[1], 3))
''')

K.code('entropy_gain', r'''
import math

def entropy(counts):
    total = sum(counts)
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h = h - p * math.log2(p)
    return h

parent = [9, 5]                       # 9 play, 5 do not play
children = {"sunny": [2, 3], "overcast": [4, 0], "rain": [3, 2]}
print("parent entropy:", round(entropy(parent), 3))
after = 0.0
for name, counts in children.items():
    share = sum(counts) / sum(parent)
    after = after + share * entropy(counts)
    print(name.ljust(8), counts, " entropy", round(entropy(counts), 3))
print("weighted entropy after the split:", round(after, 3))
print("information gain:", round(entropy(parent) - after, 3))
''')

K.code('depth_overfit', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for depth in [1, 2, 3, 5, 8, None]:
    tree = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_train, y_train)
    print("max_depth", str(depth).rjust(4), " leaves", str(tree.get_n_leaves()).rjust(2),
          " train", round(tree.score(X_train, y_train), 3), " test", round(tree.score(X_test, y_test), 3))
''')

K.code('pruning', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
path = DecisionTreeClassifier(random_state=0).cost_complexity_pruning_path(X_train, y_train)
alphas = path.ccp_alphas[:-1]
print("candidate alphas:", len(alphas), " from", round(float(alphas[0]), 4), "to", round(float(alphas[-1]), 4))
scores = [cross_val_score(DecisionTreeClassifier(ccp_alpha=a, random_state=0), X_train, y_train, cv=5).mean() for a in alphas]
best = float(alphas[int(np.argmax(scores))])
tree = DecisionTreeClassifier(ccp_alpha=best, random_state=0).fit(X_train, y_train)
print("best alpha:", round(best, 4), " leaves", tree.get_n_leaves(), " test accuracy", round(tree.score(X_test, y_test), 3))
''')

K.code('regression_tree', r'''
import numpy as np
from sklearn.tree import DecisionTreeRegressor

rng = np.random.default_rng(0)
x = np.sort(rng.uniform(0, 6, 80)).reshape(-1, 1)
y = np.sin(x).ravel() + rng.normal(0, 0.15, 80)
for depth in [1, 2, 5]:
    tree = DecisionTreeRegressor(max_depth=depth, random_state=0).fit(x, y)
    preds = tree.predict([[0.5], [1.5], [3.0], [4.7]])
    print("depth", depth, " leaves", str(tree.get_n_leaves()).rjust(2), " predictions", np.round(preds, 2).tolist())
''')

K.code('importance', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

data = load_breast_cancer()
rng = np.random.default_rng(0)
X = np.column_stack([data.data, rng.normal(size=len(data.data))])   # last column is pure noise
names = list(data.feature_names) + ["random noise"]
X_train, X_test, y_train, y_test = train_test_split(X, data.target, test_size=0.3, random_state=0)
tree = DecisionTreeClassifier(random_state=0).fit(X_train, y_train)
top = np.argsort(tree.feature_importances_)[::-1][:3]
print("top impurity importances:", [(str(names[i]), round(float(tree.feature_importances_[i]), 3)) for i in top])
print("impurity importance of noise:", round(float(tree.feature_importances_[-1]), 3))
perm = permutation_importance(tree, X_test, y_test, n_repeats=10, random_state=0)
print("permutation importance of noise:", round(float(perm.importances_mean[-1]), 3))
''')

K.code('instability', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier

data = load_breast_cancer()
X, y = data.data, data.target
rng = np.random.default_rng(1)
for trial in range(5):
    idx = rng.choice(len(X), len(X), replace=True)       # a bootstrap sample
    tree = DecisionTreeClassifier(random_state=0).fit(X[idx], y[idx])
    root = tree.tree_.feature[0]
    print("sample", trial + 1, " root question:", str(data.feature_names[root]), "<=", round(float(tree.tree_.threshold[0]), 2),
          " leaves", tree.get_n_leaves())
''')

TREE = r"""
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values):
    # build a tree from a LeetCode style level order list, None means no child
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i = i + 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i = i + 1
    return root
"""

K.lesson('idea', 'A model made of yes or no questions', f'''
{src('Breiman and others, Classification and Regression Trees (1984), Quinlan, C4.5 (1993), The Elements of Statistical Learning section 9.2, An Introduction to Statistical Learning chapter 8, Strobl and others (2007), and the scikit-learn 1.8 user guide section 1.10.')}
{viz('mltreegrow')}
{wwh('A <b>decision tree</b> predicts by asking a chain of yes or no questions about the features, such as "petal width &le; 0.8?". Each answer leads to another question until a <b>leaf</b> gives the prediction: a class for classification or a number for regression.',
     'Trees are easy to read and explain, need no feature scaling, handle numbers and categories, and capture interactions such as "only large and old houses are expensive" on their own. They are also the building block of random forests and gradient boosting, the strongest models for tabular data.',
     'Training is greedy: at the root, try every feature and every cut point, keep the question that makes the two groups purest, then repeat inside each group. Stop when a group is pure, too small, or the tree reaches its maximum depth.')}
{run('tree_iris')}
{note('Two questions about one feature already classify 96% of the iris flowers. The tree never looked at sepal length or petal length because petal width was always the best question. You can print any tree with export_text or draw it with plot_tree.', 'tip')}
{scene('the twenty questions game', '<p>In twenty questions a good player first asks "is it alive?" rather than "is it a giraffe?", because the first question splits the possibilities roughly in half whatever the answer. A decision tree plays the same game with the data: at every step it asks the question that tells it the most.</p>')}
''', kw=['decision tree', 'CART', 'leaf', 'root', 'split', 'export_text', 'interpretable model'])

K.lesson('split', 'Choosing a split: Gini and entropy', f'''
{viz('mlgini')}
{wwh('A split is good when each side is <b>pure</b>, mostly one class. Two common measures of impurity are the <b>Gini impurity</b> 1 &minus; &Sigma;p<sub>k</sub><sup>2</sup> and the <b>entropy</b> &minus;&Sigma;p<sub>k</sub> log<sub>2</sub> p<sub>k</sub>. Both are 0 for a pure group and largest for an even mix.',
     'The tree needs a single number to compare thousands of candidate questions. Weighting each side’s impurity by its size gives exactly that, and the drop in impurity is called the <b>information gain</b> when entropy is used.',
     'For each feature, sort the values and try the midpoint between every pair of neighbours. Compute the weighted impurity of the two sides and keep the lowest. scikit-learn uses criterion="gini" by default, criterion="entropy" or "log_loss" for entropy.')}
{run('gini_by_hand')}
{run('entropy_gain')}
{note('The weather example is the classic one from Quinlan: splitting 14 days by outlook gives an information gain of 0.247 bits, because overcast days are all "play". In practice Gini and entropy choose the same split most of the time, and Gini is a little faster since it needs no logarithm.', 'exam')}
{fxs(fx('Gini impurity', 'G = 1 &minus; &Sigma;<sub>k</sub> p<sub>k</sub><sup>2</sup>', 'Chance two random picks have different classes.', key=True),
     fx('Entropy', 'H = &minus;&Sigma;<sub>k</sub> p<sub>k</sub> log<sub>2</sub> p<sub>k</sub>', 'Bits needed to say the class.', key=True),
     fx('Information gain', 'IG = H(parent) &minus; &Sigma;<sub>child</sub> (n<sub>child</sub>/n) H(child)', 'How much a split reduces impurity.', key=True))}
''', kw=['Gini impurity', 'entropy', 'information gain', 'best split', 'impurity', 'criterion'])

K.lesson('depth', 'Overfitting, depth and pruning', f'''
{wwh('A tree that keeps splitting will end with one training point per leaf: 100% training accuracy and poor test accuracy. You control this by stopping early (<b>pre pruning</b>) or by growing a full tree and cutting it back (<b>post pruning</b>).',
     'Trees have very high variance. Without limits they memorise noise, as the depth table shows: training accuracy reaches 1.0 while test accuracy stalls.',
     'Pre pruning settings: max_depth, min_samples_leaf, min_samples_split, max_leaf_nodes. Post pruning: cost complexity pruning with ccp_alpha, chosen by cross validation from cost_complexity_pruning_path.')}
{run('depth_overfit')}
{run('pruning')}
{note('The full tree has 16 leaves and 0.906 test accuracy. Cost complexity pruning picks &alpha; = 0.0088, keeps only 6 leaves and scores 0.918: a smaller tree that is also more accurate on new data.', 'tip')}
{fx('Cost complexity', 'R<sub>&alpha;</sub>(T) = R(T) + &alpha; |T|', 'Training error plus a price &alpha; per leaf. Larger &alpha; gives a smaller tree.', key=True)}
''', kw=['overfitting', 'max_depth', 'min_samples_leaf', 'pruning', 'cost complexity pruning', 'ccp_alpha'])

K.lesson('regress', 'Regression trees', f'''
{wwh('A <b>regression tree</b> predicts a number: each leaf predicts the <b>mean</b> of the training targets that land in it. Splits are chosen to reduce the squared error instead of the Gini impurity.',
     'Regression trees capture jumps and thresholds, such as "price rises sharply above 100 square metres", that a straight line cannot. They are also the trees inside gradient boosting.',
     'Use DecisionTreeRegressor. The prediction is a <b>step function</b>: flat inside each leaf, jumping at each cut. A deeper tree gives more, smaller steps.')}
{run('regression_tree')}
{note('With depth 1 the tree knows only two numbers (0.59 and &minus;0.7), so 0.5, 1.5 and 3.0 all get the same prediction. Depth 5 has 23 steps and follows the sine curve closely, including some of its noise. A tree can never predict outside the range of the training targets, so it cannot extrapolate a trend.', 'exam')}
{fx('Leaf prediction (regression)', 'ŷ<sub>leaf</sub> = mean of y<sub>i</sub> in the leaf', 'Splits minimise &Sigma;(y &minus; ŷ<sub>leaf</sub>)<sup>2</sup>.', key=True)}
''', kw=['regression tree', 'DecisionTreeRegressor', 'step function', 'squared error split', 'extrapolation'])

K.lesson('importance', 'Feature importance', f'''
{wwh('Trees report a <b>feature importance</b> for each feature: the total impurity drop from all splits on that feature, scaled to add up to 1. <b>Permutation importance</b> instead measures how much the test score falls when one feature’s values are shuffled.',
     'Importances help explain a model and spot leaks. But impurity importance is measured on the training data and favours features with many distinct values, even pure noise.',
     'Read feature_importances_ for a quick look. For decisions, use sklearn.inspection.permutation_importance on held out data.')}
{run('importance')}
{note('One feature (worst concave points) carries 73% of the impurity importance. A column of pure random noise still gets 0.009 impurity importance because the full tree used it to split a few training points, while its permutation importance on test data is about 0 (&minus;0.005). Strobl and others (2007) documented this bias.', 'tip')}
''', kw=['feature importance', 'impurity importance', 'permutation importance', 'MDI', 'bias towards high cardinality'])

K.lesson('instability', 'Why one tree is not enough', f'''
{wwh('Trees are <b>unstable</b>: a small change in the training data can change the very first question, and with it the whole tree.',
     'High variance means a single tree’s predictions are noisy. This weakness is the reason ensembles exist: averaging many different trees cancels much of the noise.',
     'Train a tree on several bootstrap samples (rows drawn with replacement) and look at the root question. Supervised 3.2 averages such trees into a random forest.')}
{run('instability')}
{note('Five bootstrap samples of the same data give three different root features and between 12 and 19 leaves. Each tree is a reasonable model, but they disagree. That disagreement is variance, and averaging removes it.', 'exam')}
{table(['Strength', 'Weakness'], [
    ['Easy to read and explain', 'High variance, unstable'],
    ['No scaling, handles mixed feature types', 'Axis parallel cuts, staircase for slanted boundaries'],
    ['Captures interactions and thresholds', 'Cannot extrapolate beyond the training targets'],
    ['Fast to train and predict', 'Greedy, so not the best possible tree'],
    ['Handles missing values (scikit-learn 1.3 and later)', 'Biased impurity importance']])}
''', kw=['instability', 'variance', 'bootstrap', 'ensembles', 'strengths and weaknesses'])

K.lesson('versus', 'Trees compared', f'''
{versus('A decision tree next to models you know', ['', 'Decision tree', 'Logistic regression', 'KNN'], [
    ['Boundary', 'Axis parallel boxes', 'One straight line', 'Any shape'],
    ['Feature scaling', 'Not needed', 'Needed with a penalty', 'Needed'],
    ['Interactions', 'Found automatically', 'Only if added', 'Automatic'],
    ['Explaining a prediction', 'Follow the path of questions', 'Read the weights', 'Show the neighbours'],
    ['Variance', 'High', 'Low', 'High for small k'],
    ['Extrapolation', 'No', 'Yes', 'No']],
    'a single tree is the most readable model, and an ensemble of trees is usually the most accurate on tables.')}
''', kw=['tree vs logistic regression', 'tree vs KNN', 'interpretability', 'axis parallel'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Gini impurity', 'G = 1 &minus; &Sigma;<sub>k</sub> p<sub>k</sub><sup>2</sup>', 'Two classes: G = 2p(1 &minus; p), maximum 0.5.', key=True),
     fx('Entropy', 'H = &minus;&Sigma;<sub>k</sub> p<sub>k</sub> log<sub>2</sub> p<sub>k</sub>', 'Two classes: maximum 1 bit at p = 0.5.', key=True),
     fx('Weighted impurity of a split', 'I<sub>split</sub> = (n<sub>L</sub>/n) I(L) + (n<sub>R</sub>/n) I(R)', 'Pick the split with the smallest value.', key=True),
     fx('Regression split', 'min &Sigma;<sub>i&isin;L</sub>(y<sub>i</sub> &minus; ȳ<sub>L</sub>)<sup>2</sup> + &Sigma;<sub>i&isin;R</sub>(y<sub>i</sub> &minus; ȳ<sub>R</sub>)<sup>2</sup>', 'Squared error around each side’s mean.'),
     fx('Cost complexity', 'R<sub>&alpha;</sub>(T) = R(T) + &alpha;|T|', 'Prune leaves until the price outweighs the gain.', key=True))}
{steps('Worked example: the best cut for hours studied', [
    'Eight students, 3 passed. Before splitting: p = 3/8, G = 1 &minus; 0.375<sup>2</sup> &minus; 0.625<sup>2</sup> = 0.469.',
    'Cut at 4.5: the left 4 students all failed, so G<sub>L</sub> = 0.',
    'The right 4 have 3 passes: G<sub>R</sub> = 1 &minus; 0.75<sup>2</sup> &minus; 0.25<sup>2</sup> = 0.375.',
    eq('weighted G = (4 &times; 0 + 4 &times; 0.375) / 8 = 0.1875'),
    'No other cut is lower, so the drop is 0.469 &minus; 0.188 = 0.281, as the program prints.'])}
{deep('Why greedy, and what it costs', '<p>Finding the smallest tree that fits the data exactly is NP complete (Hyafil and Rivest, 1976), so every practical algorithm is greedy: it picks the best split now without looking ahead. Sometimes no single split helps but two together would, as in the XOR pattern, where the greedy tree can stop too early or choose a poor first split. CART (Breiman and others, 1984) builds binary trees with Gini or squared error and prunes with cost complexity. ID3 and C4.5 (Quinlan) use entropy, allow multiway splits on categories, and C4.5 uses the gain ratio to avoid favouring features with many values. Newer work such as optimal sparse trees (GOSDT, 2020) finds provably optimal small trees for modest data sizes.</p>')}
''', kw=['Gini formula', 'entropy formula', 'weighted impurity', 'regression split', 'cost complexity', 'CART', 'C4.5', 'NP complete'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A decision tree asks yes or no questions about the features until it reaches an answer. It picks each question so the groups become as pure as possible.</p>',
    '<p>Train and read trees with scikit-learn, compute Gini and entropy by hand, control depth and leaf size, prune with ccp_alpha, and use regression trees.</p>',
    '<p>Explain the bias of impurity importance, the instability and variance of trees, why greedy search is used, and how CART differs from C4.5.</p>',
    '<p>Study optimal decision trees, oblique trees that split on combinations of features, model trees with linear leaves, conditional inference trees that remove selection bias, and the theory linking tree depth to interaction order.</p>')}
{grow('Read a tree and follow a prediction down its questions.',
      'Train, limit and prune trees, and compute impurity by hand.',
      'Analyse greedy search, importance bias and variance.')}
''', kw=['beginner', 'expert', 'optimal trees', 'oblique trees', 'model trees'])

lc(104, 'Maximum Depth of Binary Tree', 'maximum-depth-of-binary-tree', 'e', 'Depth is one more than the deeper child', 'An empty tree has depth 0. Otherwise the depth is 1 plus the larger depth of the two children. This is what max_depth limits in a decision tree.', TREE + r'''

def max_depth(root):
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
''', [('max_depth(build([3, 9, 20, None, None, 15, 7]))', 3), ('max_depth(build([1, None, 2]))', 2)])
lc(112, 'Path Sum', 'path-sum', 'e', 'Subtract as you go down', 'Walk from the root, subtracting each value from the target. At a leaf, check whether what is left equals the leaf value. A decision tree prediction is also one root to leaf path.', TREE + r'''

def has_path_sum(root, target):
    if root is None:
        return False
    if root.left is None and root.right is None:
        return root.val == target
    rest = target - root.val
    return has_path_sum(root.left, rest) or has_path_sum(root.right, rest)
''', [('has_path_sum(build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]), 22)', True), ('has_path_sum(build([1, 2, 3]), 5)', False)])
lc(102, 'Binary Tree Level Order Traversal', 'binary-tree-level-order-traversal', 'm', 'A queue, one level at a time', 'Keep a queue of the nodes on the current level. Record their values, then replace the queue with all their children. This breadth first order is how the animation grows the tree.', TREE + r'''

def level_order(root):
    if root is None:
        return []
    result = []
    level = [root]
    while level:
        result.append([node.val for node in level])
        nxt = []
        for node in level:
            if node.left:
                nxt.append(node.left)
            if node.right:
                nxt.append(node.right)
        level = nxt
    return result
''', [('level_order(build([3, 9, 20, None, None, 15, 7]))', [[3], [9, 20], [15, 7]]), ('level_order(build([]))', [])])
lc(700, 'Search in a Binary Search Tree', 'search-in-a-binary-search-tree', 'e', 'Go left or right by one comparison', 'At each node compare the value: smaller goes left, larger goes right. Each comparison is one yes or no question, exactly like a decision tree prediction.', TREE + r'''

def search_bst(root, val):
    node = root
    while node is not None and node.val != val:
        if val < node.val:
            node = node.left
        else:
            node = node.right
    return node
''', [('search_bst(build([4, 2, 7, 1, 3]), 2).val', 2), ('search_bst(build([4, 2, 7, 1, 3]), 5) is None', True)])
lc(108, 'Convert Sorted Array to Binary Search Tree', 'convert-sorted-array-to-binary-search-tree', 'e', 'Split at the middle', 'Make the middle value the root, then build the left half and the right half the same way. Splitting into two balanced halves is what a good first question does.', TREE + r'''

def sorted_array_to_bst(nums):
    if not nums:
        return None
    mid = len(nums) // 2
    root = TreeNode(nums[mid])
    root.left = sorted_array_to_bst(nums[:mid])
    root.right = sorted_array_to_bst(nums[mid + 1:])
    return root


def inorder(root):
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)
''', [('inorder(sorted_array_to_bst([-10, -3, 0, 5, 9]))', [-10, -3, 0, 5, 9]), ('sorted_array_to_bst([1, 3]).val', 3)])
lc(257, 'Binary Tree Paths', 'binary-tree-paths', 'e', 'Carry the path down', 'Walk down carrying the path so far. At a leaf, save it. Every root to leaf path of a decision tree is one readable rule, such as "petal width &gt; 0.8 and petal width &le; 1.75 means versicolor".', TREE + r'''

def binary_tree_paths(root):
    paths = []

    def walk(node, path):
        if node is None:
            return
        path = path + [str(node.val)]
        if node.left is None and node.right is None:
            paths.append("->".join(path))
        walk(node.left, path)
        walk(node.right, path)

    walk(root, [])
    return paths
''', [('binary_tree_paths(build([1, 2, 3, None, 5]))', ['1->2->5', '1->3']), ('binary_tree_paths(build([1]))', ['1'])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>A decision tree is a binary tree. These problems practise walking trees: depth, root to leaf paths, level by level traversal, searching with one comparison per level, building a balanced tree by splitting at the middle, and listing every path as a rule. Each solution includes a small helper that builds a tree from a LeetCode style list. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'binary tree', 'depth', 'paths', 'breadth first search', 'binary search tree'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>decision tree</b> predicts with a chain of yes or no questions. Leaves hold a class or the mean target.',
    'Each split minimises the weighted <b>Gini impurity</b> or <b>entropy</b>. The drop in entropy is the information gain.',
    'Training is greedy: best split at the root, then repeat in each branch.',
    'Unlimited trees overfit. Limit max_depth or min_samples_leaf, or prune with ccp_alpha chosen by cross validation.',
    'Regression trees give step functions and cannot extrapolate.',
    'Impurity importance is biased towards noisy, many valued features. Prefer permutation importance on test data.',
    'Trees are unstable (high variance). Averaging many trees fixes that.'],
    'Supervised 3.2 builds random forests: many trees on bootstrap samples with random features, averaged.')}
{files('Three tasks: Gini impurity, entropy, and the best cut point on one feature.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A leaf of a classification tree predicts', ['The mean of all data', 'The majority class of its training points', 'A random class', 'The root feature'], 1, 'Vote inside the leaf.', 'Each leaf predicts its majority class.')
K.quiz('e', 'The Gini impurity of a group with only one class is', ['1', '0.5', '0', 'Undefined'], 2, 'Pure.', '1 &minus; 1<sup>2</sup> = 0.')
K.quiz('e', 'Decision trees need feature scaling', ['Always', 'Never, splits only compare values', 'Only for regression', 'Only with entropy'], 1, 'Thresholds.', 'Scaling does not change the order of values.')
K.quiz('e', 'A regression tree leaf predicts', ['The median always', 'The mean of the targets in the leaf', 'A straight line', 'The largest target'], 1, 'Squared error.', 'The mean minimises the squared error.')
K.quiz('m', 'Growing a tree until every leaf is pure usually gives', ['Underfitting', 'Overfitting', 'Perfect test accuracy', 'A linear model'], 1, 'Memorising.', 'Training accuracy 1.0, worse test accuracy.')
K.quiz('m', 'Information gain is', ['The parent entropy minus the weighted child entropy', 'The number of leaves', 'The depth', 'The Gini of the root'], 0, 'Drop in impurity.', 'IG = H(parent) &minus; &Sigma;(n<sub>c</sub>/n)H(c).')
K.quiz('m', 'Increasing ccp_alpha makes the pruned tree', ['Larger', 'Smaller', 'Unchanged', 'Deeper'], 1, 'Price per leaf.', 'Each leaf costs &alpha;, so fewer leaves survive.')
K.quiz('m', 'Why do trees struggle with a diagonal boundary?', ['They cannot use two features', 'Splits are parallel to the axes, so they need a staircase', 'They need scaling', 'They are linear'], 1, 'Look at the cuts.', 'Many small axis parallel steps approximate the slanted line.')
K.quiz('m', 'A random noise column gets some impurity importance because', ['sklearn adds it on purpose', 'Deep trees split on it to fit a few training points', 'Noise is always useful', 'Importance is random'], 1, 'Measured on training data.', 'Permutation importance on test data shows it is useless.')
K.quiz('h', 'Two bootstrap samples give trees with different root splits. This shows trees have', ['High bias', 'High variance', 'No parameters', 'Calibrated outputs'], 1, 'Sensitivity to data.', 'Averaging many trees reduces this variance.')
K.quiz('h', 'A regression tree trained on house prices from 100k to 900k predicts for a huge new house', ['Above 900k if the trend continues', 'At most 900k, a leaf mean', 'A negative value', 'An error'], 1, 'Leaves are means.', 'Trees cannot extrapolate beyond the training targets.')
K.quiz('h', 'Why are practical tree learners greedy?', ['Greedy trees are always optimal', 'Finding the optimal tree is NP complete', 'Greedy uses less memory only', 'Because of Gini'], 1, 'Hyafil and Rivest.', 'Exhaustive search over trees is infeasible.')
K.quiz('x', 'In the style of a CMU 10-601 exam: on the XOR pattern (class 1 when exactly one of two binary features is 1), the first greedy split gives an information gain of', ['1 bit', '0 bits', '0.5 bits', '2 bits'], 1, 'Each feature alone tells nothing.', 'Each child is still 50/50, so the gain is 0 even though depth 2 solves it.')
K.quiz('x', 'In the style of a Stanford CS229 exam: for two classes, Gini and entropy as functions of p are both', ['Linear', 'Concave and maximal at p = 0.5', 'Convex', 'Increasing'], 1, 'Peak in the middle.', 'Concavity ensures any split never increases the weighted impurity.')

K.calc('e', '5 yes and 5 no. Gini impurity?', '0.5', '1 &minus; &Sigma;p<sup>2</sup>.', ['p = 0.5 for each.', '0.25 + 0.25 = 0.5.', eq('1 &minus; 0.5 = 0.5')], check=0.5)
K.calc('e', '8 yes and 2 no. Gini impurity?', '0.32', 'Shares 0.8 and 0.2.', ['0.8<sup>2</sup> = 0.64.', '0.2<sup>2</sup> = 0.04.', eq('1 &minus; 0.68 = 0.32')], check=0.32)
K.calc('e', 'Entropy (bits) of a 50/50 group?', '1', '&minus;&Sigma;p log<sub>2</sub>p.', ['Each term: 0.5 &times; log<sub>2</sub> 0.5 = &minus;0.5.', 'Two terms add to &minus;1.', eq('H = 1')], check=1)
K.calc('m', 'Entropy (bits) with p = 0.25, 3 decimals?', '0.811', 'Two terms.', ['&minus;0.25 log<sub>2</sub> 0.25 = 0.5.', '&minus;0.75 log<sub>2</sub> 0.75 = 0.311.', eq('0.5 + 0.311 = 0.811')], check=0.811)
K.calc('m', 'Split of 8: left 4 pure, right 4 with Gini 0.375. Weighted Gini?', '0.1875', 'Weight by size.', ['Left: 4 &times; 0 = 0.', 'Right: 4 &times; 0.375 = 1.5.', eq('1.5 / 8 = 0.1875')], check=0.1875)
K.calc('m', 'Parent entropy 1. Two equal halves each with entropy 0.811. Information gain, 3 decimals?', '0.189', 'Parent minus weighted children.', ['Weighted children: 0.5 &times; 0.811 + 0.5 &times; 0.811 = 0.811.', '1 &minus; 0.811.', eq('0.189')], check=0.189)
K.calc('m', 'A full binary tree of depth 3. Number of leaves?', '8', '2<sup>depth</sup>.', ['Depth 1: 2 leaves.', 'Each level doubles.', eq('2<sup>3</sup> = 8')], check=8)
K.calc('h', 'A regression leaf holds targets 3, 5 and 10. Prediction?', '6', 'Mean.', ['Sum 18.', '3 targets.', eq('18 / 3 = 6')], check=6)
K.calc('h', 'Cost complexity with training error 0.1, &alpha; = 0.01 and 6 leaves?', '0.16', 'R + &alpha;|T|.', ['&alpha;|T| = 0.06.', 'Add R = 0.1.', eq('0.16')], check=0.16)
K.calc('x', 'In the style of an MIT 6.036 problem: 100 rows with distinct values and 5 numeric features. How many candidate splits does the root search check?', '495', 'n &minus; 1 per feature.', ['99 midpoints per feature.', '5 features.', eq('5 &times; 99 = 495')], check=495)

K.assign('gini', 'e', 'Gini impurity',
         '<p>Write <code>gini(labels)</code> for a list of class labels. Return 1 &minus; &Sigma;p<sub>k</sub><sup>2</sup>, rounded to 4 decimals, and 0.0 for an empty list.</p>',
         '''
def gini(labels):
    # your code here
    pass
''', [('gini(["a", "a", "b", "b"])', 0.5), ('gini(["a", "a", "a"])', 0.0), ('gini(["a", "b", "c"])', 0.6667)],
         '''
def gini(labels):
    if not labels:
        return 0.0
    counts = {}
    for c in labels:
        counts[c] = counts.get(c, 0) + 1
    total = 0.0
    for k in counts.values():
        total = total + (k / len(labels)) ** 2
    return round(1 - total, 4)
''', 'Count each class, then subtract the squared shares from 1.', '<p>Three equal classes give 1 &minus; 3 &times; (1/3)<sup>2</sup> = 0.667.</p>')
K.assign('entropy', 'm', 'Entropy in bits',
         '<p>Write <code>entropy(labels)</code> that returns &minus;&Sigma;p<sub>k</sub> log<sub>2</sub> p<sub>k</sub>, rounded to 4 decimals.</p>',
         '''
import math


def entropy(labels):
    # your code here
    pass
''', [('entropy(["y", "y", "n", "n"])', 1.0), ('entropy(["y", "y", "y", "n"])', 0.8113), ('entropy(["a", "a"])', 0.0)],
         '''
import math


def entropy(labels):
    counts = {}
    for c in labels:
        counts[c] = counts.get(c, 0) + 1
    h = 0.0
    for k in counts.values():
        p = k / len(labels)
        h = h - p * math.log2(p)
    return round(h, 4) + 0.0
''', 'Count, turn counts into shares, add &minus;p log<sub>2</sub> p.', '<p>A pure group has entropy 0 and a 50/50 group 1 bit.</p>')
K.assign('bestcut', 'h', 'The best cut on one feature',
         '<p>Write <code>best_cut(xs, ys)</code>. xs are numbers, ys are their class labels. Try the midpoint between every pair of neighbouring distinct sorted values. Return the cut with the lowest weighted Gini impurity (left is x &lt; cut). If two cuts tie, return the smaller one.</p>',
         '''
def best_cut(xs, ys):
    # your code here
    pass
''', [('best_cut([1, 2, 3, 4, 5, 6, 7, 8], ["n", "n", "n", "n", "y", "n", "y", "y"])', 4.5), ('best_cut([1, 2, 6, 7], ["a", "a", "b", "b"])', 4.0), ('best_cut([3, 1, 2], ["b", "a", "b"])', 1.5)],
         '''
def impurity(labels):
    if not labels:
        return 0.0
    counts = {}
    for c in labels:
        counts[c] = counts.get(c, 0) + 1
    return 1 - sum((k / len(labels)) ** 2 for k in counts.values())


def best_cut(xs, ys):
    values = sorted(set(xs))
    best = None
    best_score = None
    for i in range(1, len(values)):
        cut = (values[i - 1] + values[i]) / 2
        left = [ys[j] for j in range(len(xs)) if xs[j] < cut]
        right = [ys[j] for j in range(len(xs)) if xs[j] >= cut]
        score = (len(left) * impurity(left) + len(right) * impurity(right)) / len(xs)
        if best_score is None or score < best_score - 1e-12:
            best = cut
            best_score = score
    return best
''', 'Sort the distinct values, try each midpoint, and keep the lowest weighted Gini.', '<p>The first test is the chapter’s hours studied example. The third shows the values do not need to be sorted.</p>')

K.must('Model', 'A chain of yes or no questions. Leaf = majority class (classification) or mean (regression). No scaling needed.')
K.must('Impurity', 'Gini 1 &minus; &Sigma;p<sup>2</sup>, entropy &minus;&Sigma;p log<sub>2</sub>p. Split minimises (n<sub>L</sub>/n)I(L) + (n<sub>R</sub>/n)I(R). IG = drop in entropy.')
K.must('Overfitting', 'Full trees memorise. Use max_depth, min_samples_leaf, max_leaf_nodes, or ccp_alpha from cost_complexity_pruning_path with CV.')
K.must('Regression', 'Step function, minimises squared error, cannot extrapolate.')
K.must('Importance', 'feature_importances_ (impurity, biased to many valued features). permutation_importance on test data is safer.')
K.must('Weakness', 'High variance, axis parallel cuts, greedy. Fixed by ensembles: forests (3.2) and boosting (3.3).')

T = K.topic(
    slug='ml-trees', topic='ml-trees', step=(3, 'Trees and ensembles', 'ml-s3', 'Ask the data a chain of yes or no questions, then combine hundreds of such trees into the strongest models for tables.', 'Intermediate'),
    title='Decision trees: a chain of yes or no questions', short='Decision trees', badge='3.1', minutes=55,
    lead='Learn how a decision tree chooses its questions with Gini impurity and entropy, why full trees overfit and how pruning helps, regression trees, feature importance and its traps, and why one tree is unstable.',
    desc='decision tree, CART, Gini impurity, entropy, information gain, best split, greedy algorithm, max_depth, min_samples_leaf, cost complexity pruning, ccp_alpha, regression tree, step function, feature importance, permutation importance, instability, variance, export_text.',
    summary='Questions chosen by Gini and entropy, overfitting and pruning, regression trees, feature importance, and instability.',
    keywords=['decision tree', 'Gini impurity', 'entropy', 'information gain', 'pruning', 'ccp_alpha', 'regression tree', 'feature importance', 'CART', 'DecisionTreeClassifier'],
    recap='<p>A tree asks the most informative question first and repeats. It is readable and needs no scaling, but it overfits and wobbles unless you limit or average it.</p>',
    added='2026-11-13', leet=leet_items())
