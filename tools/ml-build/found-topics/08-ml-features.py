# Foundations 3.2: feature engineering, encoding, scaling and feature selection. Checked against Zheng and Casari,
# Feature Engineering for Machine Learning (2018), Kuhn and Johnson, Feature Engineering and Selection (2019) chapters
# 5, 6 and 10 to 12, the scikit-learn 1.8 user guide sections 6.3 (preprocessing, including TargetEncoder), 6.2
# (feature extraction for text), 1.13 (feature selection) and 6.1 (ColumnTransformer and pipelines), and Guyon and
# Elisseeff, An Introduction to Variable and Feature Selection, JMLR 2003.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-features')
K = Kit()

K.code('encode_categories', r'''
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

df = pd.DataFrame({"city": ["Delhi", "Pune", "Delhi", "Mumbai"],
                   "size": ["small", "large", "medium", "small"]})

print(pd.get_dummies(df["city"], dtype=int).to_string())

enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
enc.fit(df[["city"]])
print("columns:", enc.get_feature_names_out().tolist())
print("a new city, Chennai:", enc.transform(pd.DataFrame({"city": ["Chennai"]})).tolist())

order = OrdinalEncoder(categories=[["small", "medium", "large"]])
print("size as numbers:", order.fit_transform(df[["size"]]).ravel().tolist())
''')

K.code('scalers_compared', r'''
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

income = np.array([[30], [35], [40], [45], [50], [400]])   # thousands, one very rich person

for scaler in [StandardScaler(), MinMaxScaler(), RobustScaler()]:
    scaled = scaler.fit_transform(income).ravel()
    print(type(scaler).__name__.ljust(15), np.round(scaled, 2).tolist())

print("log1p:", np.round(np.log1p(income.ravel()), 2).tolist())
''')

K.code('scaling_matters', r'''
from sklearn.datasets import load_wine
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_wine(return_X_y=True)
print("feature ranges: smallest max", round(X.max(axis=0).min(), 2), " largest max", round(X.max(axis=0).max(), 1))

raw = cross_val_score(KNeighborsClassifier(), X, y, cv=5).mean()
scaled = cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier()), X, y, cv=5).mean()
print("KNN accuracy without scaling:", round(raw, 3))
print("KNN accuracy with scaling:   ", round(scaled, 3))
''')

K.code('new_features', r'''
import numpy as np
import pandas as pd

sales = pd.DataFrame({
    "date": pd.to_datetime(["2024-01-06", "2024-01-08", "2024-03-15", "2024-12-25"]),
    "price": [5200000, 7100000, 4800000, 9900000],
    "size_m2": [80, 65, 60, 150],
    "age_years": [3, 12, 25, 1],
})
sales["month"] = sales["date"].dt.month
sales["weekday"] = sales["date"].dt.day_name()
sales["is_weekend"] = (sales["date"].dt.dayofweek >= 5).astype(int)
sales["price_per_m2"] = (sales["price"] / sales["size_m2"]).round()
sales["age_group"] = pd.cut(sales["age_years"], bins=[0, 5, 15, 100], labels=["new", "mid", "old"])
sales["log_price"] = np.log(sales["price"]).round(3)
print(sales.drop(columns=["date"]).to_string(index=False))
''')

K.code('polynomial_features', r'''
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

rng = np.random.default_rng(2)
x = rng.uniform(-3, 3, size=(80, 1))
y = 2 * x[:, 0] ** 2 - x[:, 0] + rng.normal(0, 1, size=80)    # a curve, not a line

line = LinearRegression().fit(x, y)
print("straight line R2:", round(line.score(x, y), 3))

poly = PolynomialFeatures(degree=2, include_bias=False)
x2 = poly.fit_transform(x)
print("new columns:", poly.get_feature_names_out(["x"]).tolist())
curve = LinearRegression().fit(x2, y)
print("with x squared R2:", round(curve.score(x2, y), 3))
print("learned weights:", np.round(curve.coef_, 2).tolist(), " true: [-1, 2]")

two = PolynomialFeatures(degree=2, include_bias=False).fit(np.zeros((1, 2)))
print("two features become:", two.get_feature_names_out(["a", "b"]).tolist())
''')

K.code('text_features', r'''
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

reviews = ["great phone great camera", "bad battery", "great battery life"]

count = CountVectorizer()
counts = count.fit_transform(reviews)
print("words:", count.get_feature_names_out().tolist())
print(counts.toarray().tolist())

tfidf = TfidfVectorizer()
weights = tfidf.fit_transform(reviews).toarray()
words = tfidf.get_feature_names_out().tolist()
first = {w: round(float(v), 2) for w, v in zip(words, weights[0]) if v > 0}
print("tf-idf of review 1:", first)
''')

K.code('select_features', r'''
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
X, y, names = data.data, data.target, data.feature_names
print("features:", X.shape[1])

best = SelectKBest(f_classif, k=5).fit(X, y)
print("filter (F test) top 5:", names[best.get_support()].tolist())

rfe = RFE(LogisticRegression(max_iter=5000), n_features_to_select=5).fit(StandardScaler().fit_transform(X), y)
print("wrapper (RFE) top 5:", names[rfe.support_].tolist())

lasso = LogisticRegression(l1_ratio=1.0, solver="liblinear", C=0.05).fit(StandardScaler().fit_transform(X), y)
print("embedded (L1) keeps:", int((lasso.coef_ != 0).sum()), "features")

for k in [2, 5, 30]:
    model = make_pipeline(StandardScaler(), SelectKBest(f_classif, k=k), LogisticRegression(max_iter=5000))
    print("k =", k, " cross validated accuracy:", round(cross_val_score(model, X, y, cv=5).mean(), 3))
''')

K.code('column_transformer', r'''
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

rng = np.random.default_rng(5)
n = 300
people = pd.DataFrame({
    "age": rng.integers(18, 70, n).astype(float),
    "income": rng.normal(50, 15, n),
    "city": rng.choice(["Delhi", "Pune", "Mumbai"], n),
    "plan": rng.choice(["basic", "pro"], n),
})
people.loc[rng.choice(n, 20, replace=False), "income"] = np.nan
bought = ((people["income"].fillna(50) > 55) | (people["plan"] == "pro")).astype(int)

numbers = ["age", "income"]
labels = ["city", "plan"]
prep = ColumnTransformer([
    ("num", Pipeline([("fill", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numbers),
    ("cat", OneHotEncoder(handle_unknown="ignore"), labels),
])
model = Pipeline([("prep", prep), ("clf", LogisticRegression())])
print("cross validated accuracy:", round(cross_val_score(model, people, bought, cv=5).mean(), 3))
model.fit(people, bought)
print("columns the model sees:", model.named_steps["prep"].get_feature_names_out().tolist())
''')

K.code('target_encoding', r'''
import numpy as np
import pandas as pd
from sklearn.preprocessing import TargetEncoder

rng = np.random.default_rng(0)
shops = np.array(["shop" + str(i) for i in range(50)])
shop = rng.choice(shops, 1000)
rate = {s: rng.uniform(0.1, 0.9) for s in shops}           # each shop has its own buy rate
bought = (rng.uniform(size=1000) < np.array([rate[s] for s in shop])).astype(int)

df = pd.DataFrame({"shop": shop, "bought": bought})
print("one hot would make", df["shop"].nunique(), "columns")

enc = TargetEncoder(target_type="binary", random_state=0)
encoded = enc.fit_transform(df[["shop"]], df["bought"])
print("target encoding makes 1 column. First 3 rows:", np.round(encoded[:3, 0], 3).tolist())
means = df.groupby("shop")["bought"].mean()
print("plain shop means for those rows:", [round(float(means[s]), 3) for s in df["shop"][:3]])
''', long=True)

K.lesson('encode', 'Encoding categories as numbers', f'''
{src('Zheng and Casari, Feature Engineering for Machine Learning, Kuhn and Johnson, Feature Engineering and Selection chapters 5, 6 and 10 to 12, the scikit-learn 1.8 user guide sections 6.1 to 6.3 and 1.13, and Guyon and Elisseeff, JMLR 2003.')}
{viz('mlonehot')}
{wwh('A <b>feature</b> is one input column the model learns from. <b>Encoding</b> turns text categories (city, colour, plan) into numbers. <b>One hot encoding</b> makes one 0 or 1 column per category. <b>Ordinal encoding</b> gives each category one number.',
     'Models do maths, and maths needs numbers. But the way you turn text into numbers matters: if Delhi = 0, Mumbai = 1 and Pune = 2, a linear model thinks Pune is "twice Mumbai", which is nonsense. One hot avoids any fake order.',
     'Use one hot for categories with no order and only a few values. Use ordinal, with the order given by you, for categories with a real order (small, medium, large). In scikit-learn set handle_unknown="ignore" so a city never seen in training becomes all zeros instead of crashing.')}
{run('encode_categories')}
{note('pd.get_dummies is handy for a quick look, but use OneHotEncoder in real projects. It remembers the categories it saw during training, so the test data always gets exactly the same columns in the same order.', 'tip')}
''', kw=['feature', 'encoding', 'one hot encoding', 'OneHotEncoder', 'ordinal encoding', 'OrdinalEncoder', 'get_dummies', 'handle_unknown', 'dummy variable trap'])

K.lesson('scale', 'Scaling numbers', f'''
{viz('mlscale')}
{wwh('<b>Feature scaling</b> changes the range of numeric features so they are comparable. <b>Standardisation</b> gives mean 0 and standard deviation 1, <b>min max scaling</b> squeezes values into 0 to 1, <b>robust scaling</b> uses the median and IQR, and a <b>log transform</b> pulls in long right tails.',
     'Models that use distances (KNN, k means, SVM) or gradient descent (linear and logistic regression, neural networks) treat a feature measured in thousands as far more important than one measured in units. In the program below, scaling raises KNN accuracy on the wine data from 0.691 to 0.949.',
     'Fit the scaler on the training data (it learns the mean and std, or the min and max), then use the same numbers to transform the test data. Put it in a Pipeline so cross validation does this correctly.')}
{run('scalers_compared')}
{run('scaling_matters')}
{table(['Scaler', 'Formula', 'Outliers', 'Use it for'], [
    ['StandardScaler', '(x &minus; mean) / std', 'Pull the mean and inflate the std', 'The default for linear models, SVM, PCA, neural networks'],
    ['MinMaxScaler', '(x &minus; min) / (max &minus; min)', 'One outlier squeezes every other value', 'Pixel values, inputs that must be in 0 to 1'],
    ['RobustScaler', '(x &minus; median) / IQR', 'Barely affected', 'Data with outliers you want to keep'],
    ['Log transform', 'log(1 + x)', 'Shrinks big values a lot', 'Skewed data: prices, incomes, counts'],
    ['No scaling', '', '', 'Decision trees, random forests, gradient boosting']])}
{note('Trees split on one feature at a time with thresholds like "income &gt; 52". Multiplying a feature by 1,000 moves the threshold but not the split, so tree models do not need scaling.', 'exam')}
''', kw=['feature scaling', 'standardisation', 'StandardScaler', 'MinMaxScaler', 'RobustScaler', 'normalisation', 'log transform', 'KNN scaling'])

K.lesson('create', 'Creating new features', f'''
{wwh('<b>Feature engineering</b> means building new columns from the ones you have: parts of a date, ratios, groups (bins), log values, and combinations of features.',
     'A model only sees the columns you give it. "Price per square metre" or "is it a weekend" may be what really drives the target, but a simple model cannot invent it. Good features often help more than a fancier model.',
     'Use domain knowledge. Split dates into month, weekday and weekend flags. Divide related numbers (price by size). Group ages into bins with pd.cut. Take logs of skewed amounts. Then check whether each new feature improves the cross validated score.')}
{run('new_features')}
{table(['Kind', 'Example', 'pandas or sklearn'], [
    ['Date parts', 'month, weekday, is_weekend, hour', '.dt.month, .dt.dayofweek'],
    ['Ratios', 'price per m<sup>2</sup>, debt to income', 'a / b'],
    ['Binning', 'age groups new, mid, old', 'pd.cut, KBinsDiscretizer'],
    ['Log or power', 'log of price', 'np.log1p, PowerTransformer'],
    ['Aggregates', 'average spend per customer', 'groupby().transform("mean")'],
    ['Cyclical', 'hour 23 is close to hour 0', 'sin and cos of 2&pi; &times; hour / 24']])}
{note('Only build features from information you would have at prediction time. "Number of support calls in the month after cancelling" predicts cancelling perfectly, and is useless (and leaky) for a real prediction.', 'warn')}
''', kw=['feature engineering', 'date features', 'ratio features', 'binning', 'pd.cut', 'log transform', 'aggregates', 'cyclical encoding', 'domain knowledge'])

K.lesson('poly', 'Polynomial and interaction features', f'''
{wwh('<b>Polynomial features</b> add powers of a feature (x<sup>2</sup>, x<sup>3</sup>). <b>Interaction features</b> multiply two features (a &times; b). PolynomialFeatures in scikit-learn makes all of them for you.',
     'A linear model can only draw straight lines. If the target follows a curve, a straight line fits badly. Adding x<sup>2</sup> lets the same simple linear model fit a curve, while it stays easy to train and explain.',
     'Create the new columns, then fit an ordinary linear model on them. The model is still linear in its weights, which is why the usual training works, but it is curved in the original x.')}
{run('polynomial_features')}
{note('The number of columns grows fast. With d features and degree p there are C(d + p, p) &minus; 1 columns: 10 features at degree 3 gives 285 columns. Use regularisation (Supervised 1.2) to stop the extra columns from overfitting.', 'warn')}
''', kw=['polynomial features', 'interaction features', 'PolynomialFeatures', 'nonlinear features', 'R2'])

K.lesson('text', 'Features from text', f'''
{wwh('<b>Bag of words</b> turns each text into counts of the words it contains. <b>TF-IDF</b> (term frequency times inverse document frequency) gives a higher weight to words that are common in this text but rare in the others.',
     'Reviews, emails and tickets are text, and a model needs numbers. Bag of words with a linear model is still a strong, fast baseline for spam filtering and sentiment.',
     'Build a vocabulary of all words, then make one column per word. CountVectorizer stores counts. TfidfVectorizer multiplies each count by log(N / df), where df is how many texts contain the word, so words found everywhere (like "the") count for less.')}
{run('text_features')}
{fx('TF-IDF (scikit-learn smooth version)', 'tfidf(t, d) = tf(t, d) &times; (ln((1 + N) / (1 + df(t))) + 1), then each row is scaled to length 1', 'N is the number of texts, df(t) the number of texts containing t.', key=True)}
{link('nlp', 'Text is a whole subject', 'The Natural Language Processing subject covers tokenising, n grams, TF-IDF, word embeddings and transformers in depth.', 'Open NLP')}
''', kw=['bag of words', 'CountVectorizer', 'TF-IDF', 'TfidfVectorizer', 'vocabulary', 'text features'])

K.lesson('select', 'Feature selection: keep what helps', f'''
{wwh('<b>Feature selection</b> keeps the most useful features and drops the rest. There are three families: <b>filter</b> methods score each feature on its own, <b>wrapper</b> methods try subsets with a model (RFE), and <b>embedded</b> methods select while training (L1 regularisation, tree importance).',
     'Fewer features mean faster training, simpler explanations, less overfitting when data is small, and fewer columns to collect and clean in production. Useless or noisy features can hurt distance based models a lot.',
     'Filter: compute a score such as the F test or mutual information and keep the top k. Wrapper: RFE trains a model, removes the weakest feature, and repeats. Embedded: an L1 penalty pushes the weights of weak features to exactly 0. Always choose k with cross validation, inside a Pipeline.')}
{run('select_features')}
{note('In this program the full 30 features give the best accuracy (0.981). Selection does not always raise the score. Here its value is a much simpler model: 5 features keep 0.949. Different methods also choose different features when features are correlated, as the radius, perimeter and area columns are.', 'tip')}
{note('Selecting features on the whole dataset and then cross validating is leakage: the test folds helped choose the features, so the score is too optimistic. Put the selector inside the Pipeline, as the k loop in the program does.', 'warn')}
''', kw=['feature selection', 'filter method', 'wrapper method', 'embedded method', 'SelectKBest', 'f_classif', 'mutual information', 'RFE', 'L1 regularisation', 'feature importance'])

K.lesson('pipeline', 'One pipeline for every column', f'''
{wwh('A <b>ColumnTransformer</b> applies different preparation to different columns (fill and scale the numbers, one hot encode the categories) and joins the results. Put it in a <b>Pipeline</b> with the model.',
     'Real tables mix numbers and text. Preparing them by hand in separate steps is easy to get wrong and easy to leak. One pipeline object does every step in the right order, fits only on training folds during cross validation, and can be saved and used in production as one piece.',
     'List the numeric columns and the categorical columns. Give each list its own small pipeline. Pass the ColumnTransformer and the model to Pipeline. Then call fit, predict and cross_val_score on the raw DataFrame.')}
{run('column_transformer')}
{steps('The standard tabular pipeline', [
    'Numbers: SimpleImputer(strategy="median") then StandardScaler().',
    'Categories: SimpleImputer(strategy="most_frequent") if needed, then OneHotEncoder(handle_unknown="ignore").',
    'Join them with ColumnTransformer and add the model at the end of a Pipeline.',
    'Evaluate with cross_val_score on the raw data. No step ever sees a test fold while fitting.',
    'Save the fitted pipeline with joblib and load it in the serving code (MLOps 1.2).'])}
''', kw=['ColumnTransformer', 'Pipeline', 'mixed data types', 'get_feature_names_out', 'preprocessing pipeline'])

K.lesson('versus', 'Encodings compared, including target encoding', f'''
{run('target_encoding')}
{versus('Ways to encode a category column', ['', 'One hot', 'Ordinal', 'Target encoding', 'Hashing', 'Learned embedding'], [
    ['Columns made', 'k', '1', '1 (per class)', 'A fixed number you choose', 'A small fixed number'],
    ['Many categories (1,000+)', 'Too wide', 'Fine but fake order', 'Good', 'Good', 'Good'],
    ['Leakage risk', 'None', 'None', 'High unless cross fitted', 'None', 'Low'],
    ['Unseen categories', 'All zeros', 'Needs a rule', 'Overall mean', 'Hashed like any value', 'Unknown token'],
    ['Best with', 'Linear models, few categories', 'Trees, real order', 'High cardinality, boosting', 'Huge, streaming data', 'Neural networks (Deep Learning)']],
    'one hot for few categories, target encoding for many.')}
{note('Target encoding replaces a category by the average target for that category. Using a row’s own target to encode it leaks the answer. scikit-learn’s TargetEncoder avoids this with cross fitting: each row is encoded with means from the other folds, and rare categories are pulled towards the overall mean. That is why its numbers in the program differ a little from the plain shop means.', 'exam')}
''', kw=['target encoding', 'TargetEncoder', 'cross fitting', 'high cardinality', 'feature hashing', 'embedding', 'encoding comparison'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Standardisation', 'z = (x &minus; &mu;) / &sigma;', 'Mean 0, standard deviation 1.', key=True),
     fx('Min max', 'x′ = (x &minus; min) / (max &minus; min)', 'Range 0 to 1.', key=True),
     fx('Robust', 'x′ = (x &minus; median) / IQR', 'Ignores outliers when choosing the scale.', key=True),
     fx('Number of polynomial columns', 'C(d + p, p) &minus; 1', 'd features, degree p, without the constant column.', key=True),
     fx('Mutual information', 'I(X, Y) = &Sigma; p(x, y) log(p(x, y) / (p(x) p(y)))', '0 when X and Y are independent. Catches non linear links.'),
     fx('Smoothed target encoding', 'enc(c) = (n<sub>c</sub> &times; mean<sub>c</sub> + m &times; mean<sub>all</sub>) / (n<sub>c</sub> + m)', 'Rare categories move towards the overall mean.'))}
{steps('Worked example: scaling one value three ways', [
    'Values 30, 35, 40, 45, 50, 400. Scale the value 40.',
    'Standard: mean = 600 / 6 = 100, population std = &radic;(108,250 / 6) = 134.3. (40 &minus; 100) / 134.3 = &minus;0.45.',
    'Min max: (40 &minus; 30) / (400 &minus; 30) = 10 / 370 = 0.03.',
    eq('Robust: median 42.5, IQR 48.75 &minus; 36.25 = 12.5, so (40 &minus; 42.5) / 12.5 = &minus;0.2'),
    'Only robust scaling keeps 40 at a sensible distance from its neighbours.'])}
{deep('The curse of dimensionality', '<p>As the number of features d grows, the volume of the space grows like (side length)<sup>d</sup>, so a fixed amount of data covers it ever more thinly. In high dimensions the distance to the nearest neighbour and to the farthest point become almost equal, which hurts KNN and clustering. The amount of data needed to keep the same density grows exponentially with d. Feature selection, dimensionality reduction (Unsupervised 2.1) and regularisation are the main defences.</p>')}
''', kw=['standardisation formula', 'min max formula', 'robust scaling', 'polynomial column count', 'mutual information', 'curse of dimensionality'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Models need numbers on similar scales. Turn categories into 0 or 1 columns, scale numbers, and add helpful new columns like "price per square metre".</p>',
    '<p>Use OneHotEncoder and OrdinalEncoder correctly, choose between standard, min max and robust scaling, build date, ratio, bin and log features, add polynomial terms, and use CountVectorizer and TF-IDF for text.</p>',
    '<p>Select features with filter, wrapper and embedded methods inside a Pipeline, use target encoding with cross fitting for high cardinality, build a ColumnTransformer for mixed data, and avoid leaky features.</p>',
    '<p>Learn representations instead of hand crafting them (embeddings, autoencoders), use feature stores for consistent training and serving features, and study stability of selection under correlated features (stability selection, Meinshausen and B&uuml;hlmann, 2010).</p>')}
{grow('One hot encode a category and standardise a number column.',
      'Engineer date, ratio and text features and select the best ones with cross validation.',
      'Design a leak free ColumnTransformer pipeline and pick encodings for high cardinality data.')}
''', kw=['beginner', 'expert', 'feature store', 'stability selection', 'representation learning'])

lc(1873, 'Calculate Special Bonus', 'calculate-special-bonus', 'e', 'pandas: a feature from a rule', 'The bonus is the full salary when the id is odd and the name does not start with M, otherwise 0. Build the column with a boolean mask, then sort by id.', r'''
import pandas as pd


def calculate_special_bonus(employees):
    rule = (employees["employee_id"] % 2 == 1) & (~employees["name"].str.startswith("M"))
    employees["bonus"] = employees["salary"].where(rule, 0)
    return employees[["employee_id", "bonus"]].sort_values("employee_id")
''', [('calculate_special_bonus(pd.DataFrame({"employee_id": [2, 3, 7, 8, 9], "name": ["Meir", "Michael", "Addilyn", "Juan", "Kannon"], "salary": [3000, 3800, 7400, 6100, 7700]}))["bonus"].tolist()', [0, 0, 7400, 0, 7700])])
lc(1757, 'Recyclable and Low Fat Products', 'recyclable-and-low-fat-products', 'e', 'pandas: combine two masks', 'Keep rows where both flags are "Y". Use &amp; between the two conditions and wrap each in brackets.', r'''
def find_products(products):
    keep = (products["low_fats"] == "Y") & (products["recyclable"] == "Y")
    return products[keep][["product_id"]]
''', [('find_products(pd.DataFrame({"product_id": [0, 1, 2, 3, 4], "low_fats": ["Y", "Y", "N", "Y", "N"], "recyclable": ["N", "Y", "Y", "Y", "N"]}))["product_id"].tolist()', [1, 3])])
lc(595, 'Big Countries', 'big-countries', 'e', 'pandas: an "or" mask', 'A country is big if its area is at least 3,000,000 or its population is at least 25,000,000. Use | for "or".', r'''
def big_countries(world):
    big = (world["area"] >= 3000000) | (world["population"] >= 25000000)
    return world[big][["name", "population", "area"]]
''', [('big_countries(pd.DataFrame({"name": ["Afghanistan", "Albania", "Algeria"], "population": [25500100, 2831741, 37100000], "area": [652230, 28748, 2381741]}))["name"].tolist()', ['Afghanistan', 'Algeria'])])
lc(178, 'Rank Scores', 'rank-scores', 'm', 'pandas: dense rank as a feature', 'rank(method="dense", ascending=False) gives equal scores the same rank with no gaps. Sort by score from high to low.', r'''
def order_scores(scores):
    scores["rank"] = scores["score"].rank(method="dense", ascending=False).astype(int)
    return scores[["score", "rank"]].sort_values("score", ascending=False)
''', [('order_scores(pd.DataFrame({"id": [1, 2, 3, 4, 5, 6], "score": [3.5, 3.65, 4.0, 3.85, 4.0, 3.65]}))["rank"].tolist()', [1, 1, 2, 3, 3, 4])])
lc(2356, 'Number of Unique Subjects Taught by Each Teacher', 'number-of-unique-subjects-taught-by-each-teacher', 'e', 'pandas: groupby with nunique', 'Group by teacher and count the different subject ids. reset_index turns the result back into a table.', r'''
def count_unique_subjects(teacher):
    result = teacher.groupby("teacher_id")["subject_id"].nunique().reset_index()
    return result.rename(columns={"subject_id": "cnt"})
''', [('count_unique_subjects(pd.DataFrame({"teacher_id": [1, 1, 1, 2, 2, 2, 2], "subject_id": [2, 2, 3, 1, 2, 3, 4], "dept_id": [3, 4, 3, 1, 1, 1, 1]}))["cnt"].tolist()', [2, 4])])
lc(1741, 'Find Total Time Spent by Each Employee', 'find-total-time-spent-by-each-employee', 'e', 'pandas: a computed column, then groupby sum', 'Make a column out_time minus in_time, then add it up for each day and employee.', r'''
def total_time(employees):
    employees["total_time"] = employees["out_time"] - employees["in_time"]
    result = employees.groupby(["event_day", "emp_id"])["total_time"].sum().reset_index()
    return result.rename(columns={"event_day": "day"})
''', [('total_time(pd.DataFrame({"emp_id": [1, 1, 1, 2, 2], "event_day": ["2020-11-28", "2020-11-28", "2020-12-03", "2020-11-28", "2020-12-09"], "in_time": [4, 55, 1, 3, 47], "out_time": [32, 200, 42, 33, 74]}))["total_time"].tolist()', [173, 30, 41, 27])])
lc(1484, 'Group Sold Products By The Date', 'group-sold-products-by-the-date', 'e', 'pandas: groupby with two aggregates', 'For each date, count the different products and join their sorted names with commas.', r'''
def categorize_products(activities):
    rows = []
    for day, group in activities.groupby("sell_date"):
        names = sorted(group["product"].unique())
        rows.append([day, len(names), ",".join(names)])
    return pd.DataFrame(rows, columns=["sell_date", "num_sold", "products"])
''', [('categorize_products(pd.DataFrame({"sell_date": ["2020-05-30", "2020-06-01", "2020-06-02", "2020-05-30", "2020-06-01", "2020-06-02", "2020-05-30"], "product": ["Headphone", "Pencil", "Mask", "Basketball", "Bible", "Mask", "T-Shirt"]})).values.tolist()', [['2020-05-30', 3, 'Basketball,Headphone,T-Shirt'], ['2020-06-01', 2, 'Bible,Pencil'], ['2020-06-02', 1, 'Mask']])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Building features in pandas means masks, computed columns, ranks and group aggregates. These problems from the pandas track practise exactly that: a rule based column, combined filters, a dense rank, counts of unique values per group, sums per group, and two aggregates at once. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'pandas', 'groupby', 'rank', 'nunique', 'boolean mask', 'computed column'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>One hot</b> for unordered categories (handle_unknown="ignore"), <b>ordinal</b> only for a real order, <b>target encoding</b> with cross fitting for many categories.',
    '<b>Scale</b> for distance and gradient based models: standard (default), min max (0 to 1), robust (outliers), log (skewed). Trees do not need it.',
    'Fit every scaler and encoder on training data only, inside a Pipeline.',
    '<b>Engineer</b> features: date parts, ratios, bins, logs, aggregates, cyclical sin and cos. Only use what is known at prediction time.',
    '<b>Polynomial and interaction</b> features let linear models fit curves. Columns grow as C(d + p, p) &minus; 1.',
    'Text: bag of words counts, TF-IDF down weights common words.',
    '<b>Selection</b>: filter (scores), wrapper (RFE), embedded (L1, trees). Choose k by cross validation.',
    '<b>ColumnTransformer</b> prepares numbers and categories differently in one pipeline.'],
    'The Supervised section starts with linear regression, the first real model, and uses every preparation step from Foundations.')}
{files('Three tasks: one hot encode a list, standardise a list, and min max scale a list.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which encoding is best for a "city" column with 5 cities and no order?', ['Ordinal', 'One hot', 'Leave as text', 'Min max'], 1, 'No city is bigger than another.', 'One hot creates no fake order.')
K.quiz('e', 'StandardScaler makes a feature have', ['Range 0 to 1', 'Mean 0 and standard deviation 1', 'Median 0', 'Only positive values'], 1, 'z score.', '(x &minus; mean) / std.')
K.quiz('e', 'Which model does NOT need feature scaling?', ['KNN', 'Decision tree', 'SVM', 'Logistic regression trained with gradient descent'], 1, 'Thresholds on one feature at a time.', 'Trees split on thresholds, which scaling does not change.')
K.quiz('e', 'A good new feature from "price" and "size_m2" is', ['price + size', 'price per square metre', 'price &times; 0', 'size squared minus price'], 1, 'A ratio with meaning.', 'price / size compares homes of different sizes fairly.')
K.quiz('m', 'Data has a few huge outliers you want to keep. Which scaler suits it best?', ['MinMaxScaler', 'RobustScaler', 'StandardScaler', 'No scaling ever'], 1, 'Median and IQR.', 'Quartiles are barely moved by outliers.')
K.quiz('m', 'OneHotEncoder(handle_unknown="ignore") turns a category never seen in training into', ['An error', 'All zeros', 'The most common category', 'NaN'], 1, 'Ignore means no column fires.', 'Every one hot column is 0.')
K.quiz('m', 'PolynomialFeatures(degree=2) on two features a and b creates', ['a, b', 'a, b, a<sup>2</sup>, ab, b<sup>2</sup>', 'a<sup>2</sup>, b<sup>2</sup>', 'ab only'], 1, 'All terms up to degree 2.', 'The program prints [a, b, a^2, a b, b^2].')
K.quiz('m', 'In TF-IDF, a word that appears in every document gets', ['The highest weight', 'A low weight', 'A negative weight', 'Removed always'], 1, 'Inverse document frequency.', 'It does not help tell documents apart, so its idf is the smallest.')
K.quiz('m', 'RFE (recursive feature elimination) is which kind of selection?', ['Filter', 'Wrapper', 'Embedded', 'Unsupervised'], 1, 'It trains a model again and again.', 'Wrapper methods search subsets using a model.')
K.quiz('h', 'Why can plain target encoding (category mean of the target, computed on all rows) overfit?', ['It makes too many columns', 'Each row’s own target leaks into its feature, especially for rare categories', 'It cannot handle numbers', 'It ignores the target'], 1, 'A category seen once encodes its own answer.', 'Use cross fitting and smoothing, as TargetEncoder does.')
K.quiz('h', 'You choose the top 10 features with SelectKBest on the full data and then run cross validation. The score is', ['Correct', 'Too optimistic because test folds influenced the choice', 'Too pessimistic', 'Impossible to compute'], 1, 'Leakage.', 'Put the selector inside the Pipeline.')
K.quiz('h', 'Encoding hour of day as sin(2&pi; h/24) and cos(2&pi; h/24) helps because', ['It removes noise', 'Hour 23 and hour 0 end up close together', 'It makes fewer columns', 'Trees require it'], 1, 'A clock is a circle.', 'The two values place each hour on a circle.')
K.quiz('x', 'In the style of a Stanford CS229 exam: one hot encoding k categories plus an intercept in plain linear regression (no regularisation) causes', ['Underfitting', 'Perfect multicollinearity, so the weights are not unique', 'A convex loss', 'Faster training'], 1, 'The k columns always add up to 1.', 'They equal the intercept column, so drop one (dummy encoding) or regularise.')
K.quiz('x', 'In the style of an MIT 6.867 exam: how many columns does PolynomialFeatures(degree=3, include_bias=False) make from 4 features?', ['12', '34', '35', '64'], 1, 'C(d + p, p) &minus; 1.', 'C(7, 3) &minus; 1 = 35 &minus; 1 = 34.')

K.calc('e', 'Min max scale 15 when min is 10 and max is 30.', '0.25', '(x &minus; min) / (max &minus; min).', ['15 &minus; 10 = 5.', '30 &minus; 10 = 20.', eq('5 / 20 = 0.25')], check=0.25)
K.calc('e', 'Standardise 70 when mean is 50 and std is 10.', '2', '(x &minus; mean) / std.', ['70 &minus; 50 = 20.', 'Divide by 10.', eq('2')], check=2)
K.calc('e', 'How many one hot columns for a colour column with red, green, blue, yellow?', '4', 'One per category.', ['Count the different colours.', 'Red, green, blue, yellow.', eq('4 columns')], check=4)
K.calc('m', 'How many dummy columns (drop first) for 6 categories?', '5', 'k &minus; 1.', ['One category becomes the all zero row.', '6 &minus; 1.', eq('5')], check=5)
K.calc('m', 'Robust scale 60 when median is 40 and IQR is 16.', '1.25', '(x &minus; median) / IQR.', ['60 &minus; 40 = 20.', 'Divide by 16.', eq('1.25')], check=1.25)
K.calc('m', 'A house costs 6,000,000 for 120 m<sup>2</sup>. Price per m<sup>2</sup>?', '50000', 'Divide.', ['6,000,000 / 120.', '= 50,000.', eq('50,000 per m<sup>2</sup>')], check=6000000 / 120)
K.calc('m', 'Polynomial columns for d = 3 features, degree 2, no constant?', '9', 'C(5, 2) &minus; 1.', ['C(5, 2) = 10.', 'Remove the constant.', eq('10 &minus; 1 = 9')], check=9)
K.calc('h', 'idf (plain version ln(N / df)) of a word in 2 of 8 documents, 3 decimals?', '1.386', 'ln(8 / 2).', ['N / df = 4.', 'ln 4.', eq('1.386')], check=1.386)
K.calc('h', 'Smoothed target encoding: category seen 4 times with mean 1.0, overall mean 0.2, smoothing m = 4. Encoded value?', '0.6', '(n mean<sub>c</sub> + m mean<sub>all</sub>) / (n + m).', ['4 &times; 1.0 = 4.', '4 &times; 0.2 = 0.8.', eq('(4 + 0.8) / 8 = 0.6')], check=(4 * 1.0 + 4 * 0.2) / 8)
K.calc('x', 'In the style of a CMU 10-601 problem: sin and cos encoding of hour 6 on a 24 hour clock. What is the cos value?', '0', 'cos(2&pi; &times; 6 / 24).', ['6 / 24 = 0.25 of the circle.', '2&pi; &times; 0.25 = &pi;/2.', eq('cos(&pi;/2) = 0')], check=0)

K.assign('onehot', 'e', 'One hot encode a list',
         '<p>Write <code>one_hot(values)</code> that returns a list of rows. The columns are the different values in sorted order, and each row has 1 in the column of its value and 0 elsewhere.</p>',
         '''
def one_hot(values):
    # your code here
    pass
''', [('one_hot(["b", "a", "b"])', [[0, 1], [1, 0], [0, 1]]), ('one_hot(["Pune", "Delhi", "Mumbai"])', [[0, 0, 1], [1, 0, 0], [0, 1, 0]])],
         '''
def one_hot(values):
    categories = sorted(set(values))
    rows = []
    for v in values:
        row = []
        for c in categories:
            if v == c:
                row.append(1)
            else:
                row.append(0)
        rows.append(row)
    return rows
''', 'First find the sorted categories with sorted(set(values)). Then, for each value, make a row of 0s with a 1 where the category matches.', '<p>OneHotEncoder does the same and also remembers the categories, so new data gets the same columns.</p>')
K.assign('standardise', 'e', 'Standardise a list',
         '<p>Write <code>standardise(values)</code> that returns (x &minus; mean) / std for every value, rounded to 2 decimals. Use the population std (divide by n). If the std is 0, return a list of zeros.</p>',
         '''
def standardise(values):
    # your code here
    pass
''', [('standardise([2, 4, 6])', [-1.22, 0.0, 1.22]), ('standardise([5, 5])', [0, 0]), ('standardise([10, 20])', [-1.0, 1.0])],
         '''
def standardise(values):
    n = len(values)
    mean = sum(values) / n
    total = 0
    for x in values:
        total = total + (x - mean) ** 2
    std = (total / n) ** 0.5
    if std == 0:
        return [0] * n
    return [round((x - mean) / std, 2) for x in values]
''', 'Compute the mean, then the std, then transform each value. Guard against a std of 0.', '<p>StandardScaler gives the same numbers. Remember to learn the mean and std on training data only.</p>')
K.assign('minmax', 'm', 'Min max scale with training values',
         '<p>Write <code>minmax_scale(train, test)</code>. Learn the min and max from train only, then return the scaled test values (x &minus; min) / (max &minus; min), rounded to 2 decimals. Test values may fall outside 0 to 1.</p>',
         '''
def minmax_scale(train, test):
    # your code here
    pass
''', [('minmax_scale([10, 20, 30], [15, 30])', [0.25, 1.0]), ('minmax_scale([0, 100], [50, 120, -10])', [0.5, 1.2, -0.1])],
         '''
def minmax_scale(train, test):
    low = min(train)
    high = max(train)
    result = []
    for x in test:
        result.append(round((x - low) / (high - low), 2))
    return result
''', 'Use min(train) and max(train). Never look at the test values when you learn the scale.', '<p>A test value of 1.2 is fine: it means this value is larger than anything seen in training. That is how a fitted scaler behaves in production too.</p>')

K.must('Encoding', 'One hot for unordered (handle_unknown="ignore"), ordinal for a real order, target encoding with cross fitting for many categories.')
K.must('Scaling', 'Standard (x &minus; &mu;)/&sigma;, min max to 0 to 1, robust (x &minus; median)/IQR, log1p for skew. Trees need none.')
K.must('No leakage', 'Fit scalers, encoders, imputers and selectors on training data only, inside a Pipeline and ColumnTransformer.')
K.must('New features', 'Date parts, ratios, bins (pd.cut), logs, group aggregates, sin and cos for cycles, polynomial and interaction terms.')
K.must('Text', 'CountVectorizer counts words. TF-IDF = tf &times; idf, idf high for rare words.')
K.must('Selection', 'Filter (F test, mutual information), wrapper (RFE), embedded (L1, tree importance). Choose k with cross validation.')

T = K.topic(
    slug='ml-features', topic='ml-features', step=(3, 'Working with data', 'ml-f3', 'Real data is messy. Load it, clean it, and turn it into features a model can learn from.', 'Beginner'),
    title='Features: encoding, scaling, engineering and selection', short='Feature engineering', badge='3.2', minutes=65,
    lead='Learn to turn a clean table into features a model can use well: one hot, ordinal and target encoding, standard, min max, robust and log scaling, new features from dates, ratios and text, polynomial terms, feature selection, and one ColumnTransformer pipeline for everything.',
    desc='features, one hot encoding, ordinal encoding, dummy variables, target encoding with cross fitting, hashing, StandardScaler, MinMaxScaler, RobustScaler, log transform, why scaling matters for KNN, date features, ratios, binning, cyclical encoding, polynomial and interaction features, bag of words, TF-IDF, filter wrapper and embedded feature selection, SelectKBest, RFE, L1, ColumnTransformer, Pipeline, curse of dimensionality.',
    summary='encoding categories, scaling numbers, engineering new features, text features, feature selection and ColumnTransformer pipelines.',
    keywords=['feature engineering', 'one hot encoding', 'scaling', 'StandardScaler', 'target encoding', 'polynomial features', 'TF-IDF', 'feature selection', 'ColumnTransformer', 'Pipeline'],
    recap='<p>Good features make simple models strong. Encode, scale, engineer and select, all inside one pipeline.</p>',
    added='2026-11-13', leet=leet_items())
