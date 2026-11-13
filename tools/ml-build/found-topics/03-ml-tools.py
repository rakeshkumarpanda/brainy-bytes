# Foundations 1.3: the Python tools for machine learning. Checked against the NumPy 2.4 user guide (array creation,
# indexing, broadcasting rules, axis), the pandas 3.0 user guide (DataFrame, selection with loc and iloc, groupby
# split-apply-combine, merge, the default string dtype in 3.0), and the scikit-learn 1.8 user guide "Getting started"
# (estimators, transformers, fit, transform, predict, Pipeline). LeetCode problems come from the "Introduction to
# Pandas" study plan.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-tools')
K = Kit()

K.code('numpy_basics', r'''
import numpy as np

marks = np.array([72, 45, 91, 38, 66])        # a 1D array (a vector)
print(marks, marks.dtype, marks.shape)
print("mean:", marks.mean(), "max:", marks.max(), "std:", round(marks.std(), 2))
print("plus 5 to everyone:", marks + 5)         # works on every item at once
print("passed?", marks >= 50)                   # a True or False for every item
print("only passed:", marks[marks >= 50])       # keep items where the test is True

table = np.array([[1, 2, 3],
                  [4, 5, 6]])                    # a 2D array (a matrix)
print(table.shape)                               # (rows, columns)
print("row 1:", table[1], "column 2:", table[:, 2])
print("zeros:", np.zeros(3), "range:", np.arange(0, 10, 3), "line:", np.linspace(0, 1, 5))
''')

K.code('why_vectorise', r'''
import time
import numpy as np

n = 200_000
prices = list(range(n))

start = time.perf_counter()
doubled = []
for p in prices:                  # plain Python: one item at a time
    doubled.append(p * 2)
loop_time = time.perf_counter() - start

arr = np.arange(n)
start = time.perf_counter()
doubled_np = arr * 2              # NumPy: the loop runs in fast compiled code
numpy_time = time.perf_counter() - start

print("same answer:", doubled[-1] == doubled_np[-1])
print("NumPy was faster:", numpy_time < loop_time)
print("a Python int uses about", 28, "bytes, a NumPy int64 uses", arr.itemsize, "bytes")
''', long=True)

K.code('shapes_and_axis', r'''
import numpy as np

# 4 students (rows) x 3 tests (columns)
scores = np.array([[70, 80, 90],
                   [60, 65, 70],
                   [90, 85, 95],
                   [50, 55, 60]])
print("shape:", scores.shape, "number of values:", scores.size)
print("average of each test (down the rows, axis=0):", scores.mean(axis=0))
print("average of each student (across, axis=1):", scores.mean(axis=1))
print("reshape to 2 x 6:")
print(scores.reshape(2, 6))
print("transpose shape:", scores.T.shape)

# broadcasting: subtract each column's mean from that column
centred = scores - scores.mean(axis=0)
print("centred column means:", centred.mean(axis=0))
''')

K.code('numpy_maths', r'''
import numpy as np

w = np.array([0.5, -1.0, 2.0])      # weights of a model
x = np.array([4.0, 1.0, 3.0])       # one example with 3 features
print("dot product w . x =", np.dot(w, x))           # 0.5*4 - 1*1 + 2*3

X = np.array([[4.0, 1.0, 3.0],
              [1.0, 0.0, 2.0]])     # two examples
print("predictions for both rows:", X @ w)           # matrix times vector

rng = np.random.default_rng(seed=0)                  # repeatable random numbers
noise = rng.normal(loc=0, scale=1, size=3)
print("random normal numbers:", noise.round(3))
print("square roots:", np.sqrt([4, 9, 16]), "exp(0) =", np.exp(0))
''')

K.code('pandas_basics', r'''
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Meera", "John", "Sara"],
    "city": ["Pune", "Delhi", "Pune", "Chennai", "Delhi"],
    "age": [21, 25, 22, 30, 28],
    "score": [88, 72, 95, 64, 81],
})
print(df.shape)
print(df.head(3))
print(df.dtypes)
print("one column:", df["score"].tolist())
print("rows where score > 80:")
print(df[df["score"] > 80])
print("row with label 2 using loc:", df.loc[2, "name"], "| first row using iloc:", df.iloc[0]["name"])
''')

K.code('pandas_groupby', r'''
import pandas as pd

df = pd.DataFrame({
    "city": ["Pune", "Delhi", "Pune", "Chennai", "Delhi", "Chennai", "Pune"],
    "temp": [31, 38, 29, 34, 41, 33, 30],
    "rain_mm": [0, 0, 12, 5, 0, 20, 3],
})
print(df.groupby("city")["temp"].mean().round(2))
print(df.groupby("city").agg(avg_temp=("temp", "mean"), total_rain=("rain_mm", "sum"), days=("temp", "count")))

# add a new feature: each row's temperature minus its city's average
df["temp_vs_city"] = df["temp"] - df.groupby("city")["temp"].transform("mean")
print(df.round(2))
''')

K.code('pandas_clean_merge', r'''
import pandas as pd
import numpy as np

orders = pd.DataFrame({"order_id": [1, 2, 3, 4], "customer_id": [10, 11, 10, 12], "amount": [250.0, np.nan, 120.0, 90.0]})
customers = pd.DataFrame({"customer_id": [10, 11, 12], "name": ["Asha", "Ravi", "Meera"]})

print("missing per column:")
print(orders.isna().sum())
orders["amount"] = orders["amount"].fillna(orders["amount"].median())   # fill the hole
joined = orders.merge(customers, on="customer_id", how="left")         # like a SQL join
print(joined)
print(joined.sort_values("amount", ascending=False)[["name", "amount"]])
''')

K.code('sklearn_api', r'''
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

# hours studied, hours slept -> passed (1) or not (0)
X = [[1, 4], [2, 8], [3, 5], [5, 7], [6, 6], [8, 8]]
y = [0, 0, 0, 1, 1, 1]

scaler = StandardScaler()            # a transformer: fit learns the mean and std
scaler.fit(X)
print("learned means:", scaler.mean_.round(2))
print("first row scaled:", scaler.transform([X[0]]).round(2))

model = LogisticRegression()         # an estimator: fit learns the weights
model.fit(scaler.transform(X), y)
print("predict 4 hours study, 7 sleep:", model.predict(scaler.transform([[4, 7]])))

pipe = make_pipeline(StandardScaler(), LogisticRegression())   # both steps in one object
pipe.fit(X, y)
print("pipeline predicts:", pipe.predict([[4, 7]]), "| accuracy on training data:", pipe.score(X, y))
''')

K.lesson('stack', 'The ML toolbox at a glance', f'''
{src('NumPy 2.4 user guide, pandas 3.0 user guide and scikit-learn 1.8 "Getting started".')}
{wwh('Almost every Python ML project uses the same small set of libraries: <b>NumPy</b> for fast arrays of numbers, <b>pandas</b> for tables, <b>scikit-learn</b> for classic models, and later <b>PyTorch</b> or TensorFlow for deep learning.',
     'Plain Python lists are flexible but slow for millions of numbers, and they have no idea of rows, columns or models. These libraries give you fast maths, easy tables and ready, tested models, so you can focus on the problem.',
     'pandas is built on NumPy, and scikit-learn takes NumPy arrays or pandas tables as input. You load and clean data with pandas, turn it into arrays, and pass them to a scikit-learn model.')}
{table(['Library', 'Main object', 'Use it for'], [
    ['NumPy', 'ndarray (an n dimensional array)', 'Fast maths on vectors and matrices, random numbers'],
    ['pandas', 'DataFrame (a table) and Series (one column)', 'Loading, cleaning, joining and summarising tables'],
    ['scikit-learn', 'Estimator (a model) and transformer', 'Preprocessing, classic ML models, metrics, splits'],
    ['matplotlib, seaborn', 'Figure and axes', 'Charts for exploring data and showing results'],
    ['PyTorch, TensorFlow', 'Tensor', 'Neural networks on GPUs (Deep Learning section)']])}
{link('python', 'New to Python itself?', 'The Complete Python subject teaches the whole language from your first program, plus Django, Flask, FastAPI and API handling. This chapter assumes you know lists, loops, functions and dictionaries.', 'Open Complete Python')}
''', kw=['NumPy', 'pandas', 'scikit-learn', 'matplotlib', 'PyTorch', 'ML libraries', 'Python for ML'])

K.lesson('numpy', 'NumPy arrays', f'''
{run('numpy_basics')}
{wwh('A NumPy <b>array</b> is a grid of numbers that all have the same type, stored side by side in memory. It can be 1D (a vector), 2D (a matrix) or more.',
     'ML is mostly maths on big tables of numbers. Arrays let you write that maths in one line (marks + 5) and run it in fast compiled code instead of a slow Python loop.',
     'Operations act on every item at once. This is called <b>vectorisation</b>. A test such as marks &gt;= 50 makes a True or False array (a <b>mask</b>), and marks[mask] keeps only the matching items.')}
{run('why_vectorise')}
{note('A NumPy array holds one type. np.array([1, 2.5]) turns everything into floats, and np.array([1, "a"]) turns everything into text. Check .dtype when results look strange.', 'warn')}
''', kw=['ndarray', 'np.array', 'dtype', 'shape', 'vectorisation', 'boolean mask', 'arange', 'linspace'])

K.lesson('shapes', 'Shapes, axes and broadcasting', f'''
{viz('mlbroadcast')}
{run('shapes_and_axis')}
{table(['Idea', 'Meaning', 'Example'], [
    ['shape', 'Size along each axis', '(4, 3) means 4 rows and 3 columns'],
    ['axis=0', 'Go down the rows, one answer per column', 'scores.mean(axis=0): average of each test'],
    ['axis=1', 'Go across the columns, one answer per row', 'scores.mean(axis=1): average of each student'],
    ['reshape', 'Same numbers, new shape', 'a.reshape(2, 6), a.reshape(-1, 1) for one column'],
    ['.T', 'Swap rows and columns', '(4, 3) becomes (3, 4)'],
    ['Broadcasting', 'Stretch size 1 axes to match', '(4, 3) minus (3,) subtracts a row from every row']])}
{note('axis=0 "collapses" the rows. A tip to remember: the axis you name is the one that disappears from the shape. (4, 3).mean(axis=0) has shape (3,).', 'exam')}
''', kw=['shape', 'axis', 'axis 0 vs axis 1', 'reshape', 'transpose', 'broadcasting', 'centring'])

K.lesson('nmaths', 'NumPy maths for models', f'''
<p>Most models turn an input into a prediction with a <b>dot product</b>: multiply each feature by its weight and add the results. With many examples at once this becomes a matrix times a vector. NumPy writes both in one symbol, @.</p>
{run('numpy_maths')}
{fxs(fx('Dot product', 'w &middot; x = w<sub>1</sub>x<sub>1</sub> + w<sub>2</sub>x<sub>2</sub> + ... + w<sub>d</sub>x<sub>d</sub>', 'np.dot(w, x) or w @ x. The core of linear models and neurons.', key=True),
     fx('Predictions for many rows', 'ŷ = X w', 'X is n &times; d, w is d long, ŷ is n long. In NumPy: X @ w.', key=True),
     fx('Shape rule for matrix product', '(n &times; d) @ (d &times; k) = (n &times; k)', 'The inner sizes must match.'))}
{note('Use np.random.default_rng(seed) for random numbers. The seed makes your results repeatable, which matters when you compare models.', 'tip')}
''', kw=['dot product', 'matrix multiplication', '@ operator', 'np.random.default_rng', 'seed'])

K.lesson('pandas', 'pandas DataFrames', f'''
{run('pandas_basics')}
{wwh('A <b>DataFrame</b> is a table with named columns and a row label (the <b>index</b>). Each column is a <b>Series</b> and can have its own type: numbers, text, dates.',
     'Real data arrives as CSV files, Excel sheets and database tables with mixed types and missing values. pandas reads all of them and lets you filter, fix and summarise in a few readable lines.',
     'Select a column with df["col"], filter rows with a mask df[df["score"] &gt; 80], pick by label with df.loc[row, col] and by position with df.iloc[i, j]. Read files with pd.read_csv("file.csv").')}
{table(['Task', 'pandas code'], [
    ['Read a CSV file', 'pd.read_csv("orders.csv")'],
    ['Size and column types', 'df.shape, df.dtypes, df.info()'],
    ['Summary numbers', 'df.describe()'],
    ['Select columns', 'df["a"], df[["a", "b"]]'],
    ['Filter rows', 'df[df["age"] &gt; 25], df.query("age &gt; 25")'],
    ['New column', 'df["bmi"] = df["kg"] / df["m"] ** 2'],
    ['Sort', 'df.sort_values("score", ascending=False)'],
    ['Count values', 'df["city"].value_counts()']])}
{note('loc uses labels and includes the end: df.loc[0:2] gives 3 rows. iloc uses positions and stops before the end: df.iloc[0:2] gives 2 rows.', 'exam')}
''', kw=['DataFrame', 'Series', 'index', 'loc', 'iloc', 'read_csv', 'filter rows', 'describe'])

K.lesson('groupby', 'groupby, merge and missing values', f'''
{viz('mlgroupby')}
{run('pandas_groupby')}
{run('pandas_clean_merge')}
{table(['Task', 'pandas code', 'SQL idea'], [
    ['Summary per group', 'df.groupby("city")["temp"].mean()', 'GROUP BY'],
    ['Many summaries', 'df.groupby("city").agg(avg=("temp", "mean"))', 'GROUP BY with several aggregates'],
    ['Group value on every row', 'df.groupby("city")["temp"].transform("mean")', 'Window function'],
    ['Join two tables', 'a.merge(b, on="id", how="left")', 'LEFT JOIN'],
    ['Find missing values', 'df.isna().sum()', 'IS NULL'],
    ['Fill missing values', 'df["x"].fillna(df["x"].median())', 'COALESCE'],
    ['Drop missing rows', 'df.dropna()', 'WHERE x IS NOT NULL']])}
{note('transform keeps one value per original row, so you can put it back into the table as a feature. agg gives one row per group. Mixing them up is a common mistake.', 'warn')}
''', kw=['groupby', 'agg', 'transform', 'merge', 'join', 'isna', 'fillna', 'dropna', 'split apply combine'])

K.lesson('sklearn', 'The scikit-learn API: estimators and transformers', f'''
{run('sklearn_api')}
{wwh('Every scikit-learn object follows one pattern. An <b>estimator</b> learns from data with fit. A <b>transformer</b> (such as a scaler) also has transform, which changes data. A <b>predictor</b> (a model) has predict.',
     'One shared pattern means you can swap a logistic regression for a random forest by changing one line, and you can chain steps safely in a <b>Pipeline</b>.',
     'fit(X, y) learns and stores results in attributes that end with an underscore (mean_, coef_). transform(X) applies them. fit_transform does both on training data. A Pipeline runs every step in order and fits each one only on the data you train it on, which prevents leakage.')}
{table(['Method', 'Who has it', 'What it does'], [
    ['fit(X, y)', 'Every estimator', 'Learn from training data. Learned values end with _'],
    ['transform(X)', 'Transformers (scalers, encoders)', 'Change data using what fit learned'],
    ['fit_transform(X)', 'Transformers', 'fit, then transform the same data (training data only)'],
    ['predict(X)', 'Models', 'Give predictions for new rows'],
    ['predict_proba(X)', 'Most classifiers', 'Give the probability of each class'],
    ['score(X, y)', 'Models', 'Accuracy for classifiers, R<sup>2</sup> for regressors'],
    ['get_params(), set_params()', 'Every estimator', 'Read or change hyperparameters']])}
{note('Call fit_transform on the training set and only transform on the test set. Calling fit on the test set too is a form of data leakage.', 'exam')}
''', kw=['estimator', 'transformer', 'predictor', 'fit', 'transform', 'fit_transform', 'predict_proba', 'Pipeline', 'make_pipeline'])

K.lesson('versus', 'Lists, arrays and DataFrames compared', f'''
{versus('Which container to use', ['', 'Python list', 'NumPy array', 'pandas DataFrame'], [
    ['Holds', 'Anything, mixed types', 'Numbers of one type', 'Columns of different types'],
    ['Speed for maths', 'Slow (Python loop)', 'Very fast (compiled)', 'Fast (NumPy inside)'],
    ['Names for columns', 'No', 'No (just positions)', 'Yes'],
    ['Missing values', 'Use None by hand', 'np.nan for floats', 'Built in: isna, fillna, dropna'],
    ['Best for', 'Small, general data', 'Maths, models, images', 'Real world tables, cleaning, joining']],
    'clean and explore with pandas, compute with NumPy, and pass either one to scikit-learn.')}
{versus('Where to train', ['', 'scikit-learn', 'PyTorch or TensorFlow'], [
    ['Models', 'Classic ML: linear, trees, SVM, clustering', 'Neural networks of any shape'],
    ['Hardware', 'CPU', 'CPU and GPU'],
    ['Code needed', 'A few lines per model', 'You write the network and often the training loop'],
    ['Best data', 'Tables up to millions of rows', 'Images, sound, text, very large data']],
    'start with scikit-learn on tables. Move to a deep learning library for images, text and very large data.')}
''', kw=['list vs array', 'array vs DataFrame', 'scikit-learn vs PyTorch', 'comparison'])

K.lesson('maths', 'The maths behind the tools', f'''
{fxs(fx('Mean along an axis', 'mean<sub>j</sub> = (1/n) &Sigma;<sub>i</sub> X<sub>ij</sub>', 'axis=0 gives one mean per column j.', key=True),
     fx('Standard deviation', 'std = &radic;( (1/n) &Sigma; (x<sub>i</sub> &minus; mean)<sup>2</sup> )', 'NumPy uses 1/n by default (ddof=0). pandas uses 1/(n &minus; 1) (ddof=1).', key=True),
     fx('Standard scaling', 'z = (x &minus; mean) / std', 'What StandardScaler does to each column.', key=True),
     fx('Memory of an array', 'bytes = number of values &times; bytes per value', 'A 1,000 &times; 1,000 float64 array uses 8,000,000 bytes, about 8 MB.'),
     fx('Broadcast result size', 'size<sub>k</sub> = max(a<sub>k</sub>, b<sub>k</sub>) when a<sub>k</sub> = b<sub>k</sub> or one of them is 1', 'Checked from the right end of the shapes.'))}
{steps('Worked example: scale one column by hand', [
    'Values 2, 4, 6. Mean = (2 + 4 + 6) / 3 = 4.',
    'Squared gaps: 4, 0, 4. Average = 8 / 3 &asymp; 2.667.',
    'std = &radic;2.667 &asymp; 1.633 (NumPy style, dividing by n).',
    eq('z = (2 &minus; 4)/1.633, 0, (6 &minus; 4)/1.633 = &minus;1.225, 0, 1.225'),
    'After scaling, the column has mean 0 and standard deviation 1. StandardScaler gives exactly these numbers.'])}
{deep('Why NumPy is fast', '<p>A Python list holds pointers to separate objects spread around memory, and every + goes through Python’s type checks. A NumPy array is one block of raw numbers, so the loop can run in C, use CPU vector instructions (SIMD) that add several numbers per cycle, and read memory in order, which keeps the CPU cache full. That is why the same sum can be 10 to 100 times faster.</p>')}
''', kw=['mean axis', 'standard deviation', 'ddof', 'standard scaling', 'z score', 'memory', 'SIMD'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>NumPy holds numbers in fast arrays, pandas holds tables, scikit-learn holds ready models. Together they are the everyday tools of ML in Python.</p>',
    '<p>Use vectorised NumPy maths and masks, mind shapes and axes, clean and summarise tables with pandas (groupby, merge, fillna), and use fit, transform and predict in scikit-learn, chained with a Pipeline.</p>',
    '<p>Know the broadcasting rules, views against copies, dtype pitfalls (int overflow, float precision), pandas index alignment, and why fitting transformers inside a pipeline per cross validation fold prevents leakage.</p>',
    '<p>NumPy arrays are strided views over a memory buffer, so slicing and transposing change only strides, not data. Libraries share memory through the buffer protocol and Apache Arrow, which pandas 3.0 uses for its default string type. scikit-learn follows the estimator contract (Buitinck and others, 2013) that keeps all state in fit and hyperparameters in __init__.</p>')}
{grow('Make arrays and DataFrames, select rows and columns, and call fit and predict.',
      'Use axis and broadcasting with confidence, build features with groupby and merge, and use Pipelines.',
      'Reason about memory layout, views and copies, and write your own scikit-learn compatible transformer.')}
''', kw=['beginner', 'expert', 'views and copies', 'strides', 'Arrow', 'estimator contract'])

lc(2877, 'Create a DataFrame from List', 'create-a-dataframe-from-list', 'e', 'pandas: build a DataFrame', 'Pass the list of rows and the column names student_id and age to pd.DataFrame.', r'''
import pandas as pd


def createDataframe(student_data):
    return pd.DataFrame(student_data, columns=["student_id", "age"])
''', [('createDataframe([[1, 15], [2, 11]]).values.tolist()', [[1, 15], [2, 11]]), ('list(createDataframe([[1, 15]]).columns)', ['student_id', 'age'])])
lc(2878, 'Get the Size of a DataFrame', 'get-the-size-of-a-dataframe', 'e', 'pandas: shape', 'df.shape is (rows, columns). Return it as a list.', r'''
def getDataframeSize(players):
    return [players.shape[0], players.shape[1]]
''', [('getDataframeSize(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))', [3, 2])])
lc(2879, 'Display the First Three Rows', 'display-the-first-three-rows', 'e', 'pandas: head', 'head(3) returns the first three rows.', r'''
def selectFirstRows(employees):
    return employees.head(3)
''', [('selectFirstRows(pd.DataFrame({"x": [1, 2, 3, 4, 5]}))["x"].tolist()', [1, 2, 3])])
lc(2880, 'Select Data', 'select-data', 'e', 'pandas: filter rows, pick columns', 'Keep rows where student_id is 101, then keep only the name and age columns.', r'''
def selectData(students):
    return students[students["student_id"] == 101][["name", "age"]]
''', [('selectData(pd.DataFrame({"student_id": [101, 53], "name": ["Ulysses", "William"], "age": [13, 10]})).values.tolist()', [['Ulysses', 13]])])
lc(2881, 'Create a New Column', 'create-a-new-column', 'e', 'pandas: a computed column', 'A new column is made by assigning to df["bonus"]. The maths runs on the whole column at once.', r'''
def createBonusColumn(employees):
    employees["bonus"] = employees["salary"] * 2
    return employees
''', [('createBonusColumn(pd.DataFrame({"name": ["Piper"], "salary": [4548]}))["bonus"].tolist()', [9096])])
lc(2884, 'Modify Columns', 'modify-columns', 'e', 'pandas: change a column in place', 'Multiply the salary column by 2 and store it back.', r'''
def modifySalaryColumn(employees):
    employees["salary"] = employees["salary"] * 2
    return employees
''', [('modifySalaryColumn(pd.DataFrame({"name": ["Jack", "Piper"], "salary": [19666, 74754]}))["salary"].tolist()', [39332, 149508])])
lc(2888, 'Reshape Data: Concatenate', 'reshape-data-concatenate', 'e', 'pandas: stack tables', 'pd.concat puts the second table under the first.', r'''
def concatenateTables(df1, df2):
    return pd.concat([df1, df2])
''', [('concatenateTables(pd.DataFrame({"id": [1, 2]}), pd.DataFrame({"id": [3]}))["id"].tolist()', [1, 2, 3])])
lc(2889, 'Reshape Data: Pivot', 'reshape-data-pivot', 'e', 'pandas: pivot long data into a wide table', 'pivot(index="month", columns="city", values="temperature") makes one row per month and one column per city.', r'''
def pivotTable(weather):
    return weather.pivot(index="month", columns="city", values="temperature")
''', [('pivotTable(pd.DataFrame({"city": ["A", "B", "A", "B"], "month": ["Jan", "Jan", "Feb", "Feb"], "temperature": [1, 2, 3, 4]})).loc["Feb"].tolist()', [3, 4])])
lc(2891, 'Method Chaining', 'method-chaining', 'e', 'pandas: chain filter, sort and select', 'Filter weight &gt; 100, sort by weight from heavy to light, keep the name column. Writing it as one chain reads like a sentence.', r'''
def findHeavyAnimals(animals):
    return animals[animals["weight"] > 100].sort_values("weight", ascending=False)[["name"]]
''', [('findHeavyAnimals(pd.DataFrame({"name": ["Tatiana", "Khaled", "Alex", "Jonathan"], "weight": [464, 41, 328, 463]}))["name"].tolist()', ['Tatiana', 'Jonathan', 'Alex'])])
lc(1572, 'Matrix Diagonal Sum', 'matrix-diagonal-sum', 'e', '2D indexing (NumPy style rows and columns)', 'Add mat[i][i] and mat[i][n &minus; 1 &minus; i] for every row. When n is odd, the centre was added twice, so take it away once.', r'''
def diagonal_sum(mat):
    n = len(mat)
    total = 0
    for i in range(n):
        total = total + mat[i][i] + mat[i][n - 1 - i]
    if n % 2 == 1:
        total = total - mat[n // 2][n // 2]
    return total
''', [('diagonal_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', 25), ('diagonal_sum([[5]])', 5)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>LeetCode’s "Introduction to Pandas" study plan practises exactly the table skills of this chapter, and one array problem practises 2D indexing. Each solution is a real pandas function you can paste into LeetCode. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable file.</p>'),
         kw=['LeetCode', 'pandas', 'DataFrame', 'pivot', 'concat', 'method chaining'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>NumPy</b> arrays hold numbers of one type in one block of memory. Maths on them is vectorised and fast.',
    'Shape is the size along each axis. axis=0 works down the rows (one answer per column), axis=1 across.',
    '<b>Broadcasting</b> compares shapes from the right and stretches sizes of 1. Unequal sizes that are not 1 raise an error.',
    'Predictions of linear models are dot products: X @ w.',
    '<b>pandas</b> DataFrames are tables with named columns. Use df["col"], masks, loc (labels) and iloc (positions).',
    'groupby splits, applies and combines. merge joins tables. isna, fillna and dropna handle missing values.',
    '<b>scikit-learn</b>: fit learns, transform changes data, predict answers. fit_transform on train, transform on test. Pipelines keep it safe.'],
    'Foundations 2.1 starts the maths you need: vectors, matrices and distances, with NumPy.')}
{files('Three tasks: column averages with NumPy, standard scaling of a list, and a per city average with pandas.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which library gives you DataFrames?', ['NumPy', 'pandas', 'scikit-learn', 'matplotlib'], 1, 'Tables.', 'pandas provides DataFrame and Series.')
K.quiz('e', 'What does np.array([1, 2, 3]) * 2 give?', ['[1, 2, 3, 1, 2, 3]', '[2, 4, 6]', 'An error', '[1, 2, 3, 2]'], 1, 'Vectorised maths.', 'NumPy multiplies every item. A list would repeat instead.')
K.quiz('e', 'An array has shape (5, 3). How many rows does it have?', ['3', '5', '15', '8'], 1, '(rows, columns).', 'The first number is the number of rows.')
K.quiz('e', 'Which method gives the first 5 rows of a DataFrame?', ['df.top()', 'df.head()', 'df.first()', 'df.start()'], 1, 'Its opposite is tail.', 'head() shows the first rows, 5 by default.')
K.quiz('m', 'scores has shape (4, 3). What is the shape of scores.mean(axis=0)?', ['(4,)', '(3,)', '(1,)', '(4, 3)'], 1, 'The named axis disappears.', 'axis=0 collapses the 4 rows, leaving one value per column.')
K.quiz('m', 'Can shapes (4, 3) and (4,) be broadcast together?', ['Yes, the result is (4, 3)', 'No, 3 and 4 do not match and neither is 1', 'Yes, the result is (4, 4)', 'Only with np.dot'], 1, 'Compare from the right.', 'Right ends: 3 against 4. Reshape the second one to (4, 1).')
K.quiz('m', 'Which call is correct on a test set?', ['scaler.fit_transform(X_test)', 'scaler.transform(X_test)', 'scaler.fit(X_test)', 'scaler.predict(X_test)'], 1, 'Learn only from training data.', 'Use what was learned on training data. Fitting on test data leaks.')
K.quiz('m', 'df.loc[0:2] on a default index returns how many rows?', ['2', '3', '1', 'An error'], 1, 'loc includes the end label.', 'Labels 0, 1 and 2 are all included.')
K.quiz('m', 'What does groupby("city")["temp"].transform("mean") return?', ['One row per city', 'One value per original row: its city’s mean', 'The overall mean', 'A sorted table'], 1, 'Same length as the table.', 'transform broadcasts the group result back to every row.')
K.quiz('h', 'In scikit-learn, what do attributes such as coef_ and mean_ have in common?', ['They are hyperparameters', 'They are learned during fit (trailing underscore)', 'They are set in __init__', 'They are private'], 1, 'The underscore rule.', 'By convention, values learned by fit end with an underscore.')
K.quiz('h', 'np.std([2, 4, 6]) and pd.Series([2, 4, 6]).std() differ because', ['pandas rounds', 'NumPy divides by n and pandas by n &minus; 1', 'NumPy uses the median', 'They do not differ'], 1, 'ddof.', 'NumPy ddof=0, pandas ddof=1 (the sample standard deviation).')
K.quiz('h', 'A (1000, 1000) float64 array uses about how much memory?', ['8 KB', '8 MB', '8 GB', '1 MB'], 1, '10<sup>6</sup> values &times; 8 bytes.', '8,000,000 bytes is about 8 MB.')
K.quiz('x', 'In the style of a Stanford CS231n assignment check: X has shape (N, D) and W has shape (D, C). What shape is X @ W + b if b has shape (C,)?', ['(N, D)', '(N, C)', '(D, C)', 'Error'], 1, 'Matrix product, then broadcast.', '(N, D) @ (D, C) = (N, C). b of shape (C,) broadcasts across the N rows.')
K.quiz('x', 'In the style of a CMU 11-785 quiz: a = np.arange(6).reshape(2, 3), b = a.T, then b[0, 1] = 99. What is a[1, 0]?', ['3', '99', '0', 'Error'], 1, 'Is .T a copy?', 'A transpose is a view on the same memory. b[0, 1] is a[1, 0], so a changes to 99.')

K.calc('e', 'An array has shape (20, 5). How many numbers does it hold?', '100', 'Rows &times; columns.', ['20 rows.', '5 columns.', eq('20 &times; 5 = 100')], check=20 * 5)
K.calc('e', 'Dot product of [1, 2, 3] and [4, 5, 6]?', '32', 'Multiply pairs and add.', ['1 &times; 4 = 4.', '2 &times; 5 = 10 and 3 &times; 6 = 18.', eq('4 + 10 + 18 = 32')], check=1 * 4 + 2 * 5 + 3 * 6)
K.calc('e', 'Mean of the column [10, 20, 30, 40]?', '25', 'Sum and divide.', ['Sum 100.', '4 values.', eq('100 / 4 = 25')], check=25)
K.calc('m', 'Standard scaling of x = 8 when the mean is 5 and std is 2. What is z?', '1.5', 'z = (x &minus; mean)/std.', ['x &minus; mean = 3.', 'Divide by 2.', eq('z = 1.5')], check=(8 - 5) / 2)
K.calc('m', 'Shapes (3, 1) and (1, 4) are broadcast. How many numbers are in the result?', '12', 'Result shape (3, 4).', ['Right: 1 and 4 give 4.', 'Left: 3 and 1 give 3.', eq('3 &times; 4 = 12')], check=12)
K.calc('m', 'Bytes used by a float64 array of shape (500, 200)?', '800000', 'Values &times; 8.', ['500 &times; 200 = 100,000 values.', '8 bytes each.', eq('800,000 bytes')], check=500 * 200 * 8)
K.calc('m', 'X is (100, 3), w is (3,). How many predictions does X @ w give?', '100', 'One per row.', ['(100 &times; 3) @ (3) gives (100).', 'One number per example.', eq('100')], check=100)
K.calc('h', 'NumPy std (divide by n) of [2, 4, 6]? Round to 3 decimals.', '1.633', '&radic;(8/3).', ['Mean 4.', 'Squared gaps 4, 0, 4 sum to 8.', eq('&radic;(8/3) &asymp; 1.633')], check=round((8 / 3) ** 0.5, 3))
K.calc('h', 'pandas std (divide by n &minus; 1) of [2, 4, 6]?', '2', '&radic;(8/2).', ['Sum of squared gaps 8.', 'n &minus; 1 = 2.', eq('&radic;4 = 2')], check=(8 / 2) ** 0.5)
K.calc('x', 'In the style of a Stanford CS229 problem: X is (n, d) with n = 10,000 and d = 50. How many multiply operations does X @ w need?', '500000', 'One multiply per value of X.', ['Each of the n rows needs d multiplies.', 'n &times; d = 10,000 &times; 50.', eq('500,000 multiplies (and about as many additions)')], check=10000 * 50)

K.assign('colmean', 'e', 'Column averages with NumPy',
         '<p>Write <code>column_means(table)</code> that takes a list of rows (all the same length) and returns a list with the average of each column. Use NumPy with axis=0 and convert the answer back with .tolist().</p>',
         '''
import numpy as np


def column_means(table):
    # your code here
    pass
''', [('column_means([[1, 2], [3, 4]])', [2.0, 3.0]), ('column_means([[10, 0, 5]])', [10.0, 0.0, 5.0]), ('column_means([[1], [2], [6]])', [3.0])],
         '''
import numpy as np


def column_means(table):
    arr = np.array(table, dtype=float)
    return arr.mean(axis=0).tolist()
''', 'np.array(table) makes the 2D array. mean(axis=0) goes down the rows. .tolist() turns the result into a plain list.', '<p>axis=0 is "one answer per column". Returning .tolist() matters: tests and JSON understand plain lists, not NumPy arrays.</p>')
K.assign('zscore', 'm', 'Standard scaling of a list',
         '<p>Write <code>standardise(values)</code> that returns each value as (x &minus; mean) / std, rounded to 3 decimals, using the NumPy standard deviation (divide by n). If std is 0, return a list of zeros.</p>',
         '''
import numpy as np


def standardise(values):
    # your code here
    pass
''', [('standardise([2, 4, 6])', [-1.225, 0.0, 1.225]), ('standardise([5, 5, 5])', [0.0, 0.0, 0.0]), ('standardise([0, 10])', [-1.0, 1.0])],
         '''
import numpy as np


def standardise(values):
    arr = np.array(values, dtype=float)
    std = arr.std()
    if std == 0:
        return [0.0] * len(values)
    z = (arr - arr.mean()) / std
    return [round(float(v), 3) for v in z]
''', 'Make an array, find mean() and std(). Guard against std = 0. Subtract and divide on the whole array at once.', '<p>This is what StandardScaler does for one column. The std = 0 guard matters: a constant column would otherwise give a division by zero and fill the table with NaN.</p>')
K.assign('citymean', 'm', 'Average per city with pandas',
         '<p>Write <code>city_average(rows)</code>. rows is a list of dictionaries such as {"city": "Pune", "temp": 31}. Return a dictionary from each city to its average temperature rounded to 1 decimal. Use pandas groupby.</p>',
         '''
import pandas as pd


def city_average(rows):
    # your code here
    pass
''', [('city_average([{"city": "Pune", "temp": 31}, {"city": "Pune", "temp": 29}, {"city": "Delhi", "temp": 40}])', {'Delhi': 40.0, 'Pune': 30.0}), ('city_average([{"city": "A", "temp": 1}, {"city": "A", "temp": 2}])', {'A': 1.5})],
         '''
import pandas as pd


def city_average(rows):
    df = pd.DataFrame(rows)
    means = df.groupby("city")["temp"].mean()
    result = {}
    for city, value in means.items():
        result[city] = round(float(value), 1)
    return result
''', 'pd.DataFrame(rows) turns a list of dicts into a table. groupby("city")["temp"].mean() gives a Series. Loop over .items() to build the dict.', '<p>The float() call turns NumPy numbers into plain Python floats, so the dictionary prints and compares cleanly.</p>')

K.must('NumPy', 'Arrays of one dtype, vectorised maths, masks (a[a &gt; 0]), shape, reshape, .T, np.random.default_rng(seed).')
K.must('Axis', 'axis=0 goes down rows (one value per column), axis=1 across columns (one per row). The named axis disappears.')
K.must('Broadcasting', 'Compare shapes from the right. Sizes must be equal or 1. (n, d) minus (d,) centres every column.')
K.must('pandas', 'DataFrame and Series. df["c"], masks, loc (labels, end included), iloc (positions). groupby with agg or transform, merge, isna, fillna.')
K.must('scikit-learn', 'fit learns (attributes end in _), transform changes, predict answers. fit_transform on train, transform on test, Pipelines.')

T = K.topic(
    slug='ml-tools', topic='ml-tools', step=(1, 'Start here', 'ml-f1', 'What machine learning is, how a project runs from raw data to a working model, and the Python tools every ML engineer uses.', 'Beginner'),
    title='Python tools for ML: NumPy, pandas and scikit-learn', short='NumPy, pandas, sklearn', badge='1.3', minutes=60,
    lead='Learn the three libraries you will use in every chapter: NumPy for fast arrays and maths, pandas for tables, and the scikit-learn pattern of fit, transform and predict.',
    desc='NumPy arrays, dtype, shape, vectorisation, boolean masks, axis, reshape, transpose, broadcasting rules, dot product and matrix multiplication, random generators, pandas DataFrame and Series, loc and iloc, filtering, groupby agg and transform, merge, missing values, scikit-learn estimators, transformers, fit transform predict, Pipeline, memory of arrays, views and copies.',
    summary='NumPy arrays and broadcasting, pandas tables and groupby, and the scikit-learn estimator API.',
    keywords=['NumPy', 'pandas', 'scikit-learn', 'broadcasting', 'axis', 'DataFrame', 'groupby', 'fit transform', 'Pipeline'],
    recap='<p>NumPy computes, pandas organises, scikit-learn models. Master shapes, axes and the fit, transform, predict pattern and every later chapter becomes easier.</p>',
    added='2026-11-13', leet=leet_items())
