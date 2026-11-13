# Foundations 3.1: loading, exploring and cleaning data. Checked against Wes McKinney, Python for Data Analysis (3rd
# edition) chapters 6 to 8 and 10, the pandas 3.0 user guide (missing data, text data, merge, reshaping, the new
# default string dtype), the scikit-learn 1.8 user guide section 7.4 (imputation of missing values), Little and Rubin,
# Statistical Analysis with Missing Data (3rd edition) chapter 1 for MCAR, MAR and MNAR, and Tukey, Exploratory Data
# Analysis (1977) for the box plot fences.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-data-cleaning')
K = Kit()

K.code('inspect_data', r'''
import io
import pandas as pd

raw = """id,city,size_m2,price,built,rooms
1,Delhi,80,52,2015-03-01,2
2, mumbai ,65,71,2018-07-15,2
3,DELHI,,48,2012-11-30,3
4,Pune,120,unknown,2020-01-10,4
5,Mumbai,70,75,2019-05-20,
5,Mumbai,70,75,2019-05-20,
6,pune,95,40,2016-08-08,3
7,Delhi,2000,60,2014-02-14,3
"""
houses = pd.read_csv(io.StringIO(raw))
print("shape:", houses.shape)
print(houses.dtypes.to_string())
print("missing per column:")
print(houses.isna().sum().to_string())
print("duplicate rows:", houses.duplicated().sum())
print("city values:", sorted(houses["city"].unique()))
''')

K.code('fill_missing', r'''
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

df = pd.DataFrame({
    "age": [25, np.nan, 35, 40, np.nan, 29],
    "city": ["Delhi", "Pune", None, "Delhi", "Delhi", "Pune"],
})
print("rows before dropna:", len(df), " after:", len(df.dropna()))

filled = df.copy()
filled["age_was_missing"] = filled["age"].isna().astype(int)
filled["age"] = filled["age"].fillna(filled["age"].median())
filled["city"] = filled["city"].fillna(filled["city"].mode()[0])
print(filled.to_string())

imp = SimpleImputer(strategy="mean")
print("SimpleImputer mean fill:", imp.fit_transform(df[["age"]]).ravel().tolist())
''')

K.code('fix_types_text', r'''
import pandas as pd

df = pd.DataFrame({
    "city": [" Delhi", "DELHI", "delhi ", "Mumbai", "Bombay", "pune"],
    "price": ["52", "48", "unknown", "71", "75", "40"],
    "listed": ["2024-01-05", "2024-02-11", "2024-02-30", "2024-03-01", "2024-03-09", "2024-04-15"],
})
df["city"] = df["city"].str.strip().str.lower()
df["city"] = df["city"].replace({"bombay": "mumbai"})
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["listed"] = pd.to_datetime(df["listed"], errors="coerce")
print(df.to_string())
print(df.dtypes.to_string())
print("city counts:", df["city"].value_counts().to_dict())
''')

K.code('find_outliers', r'''
import numpy as np
import pandas as pd

salary = pd.Series([32, 35, 36, 38, 40, 41, 43, 45, 47, 150])   # thousands per month

q1 = salary.quantile(0.25)
q3 = salary.quantile(0.75)
iqr = q3 - q1
low = q1 - 1.5 * iqr
high = q3 + 1.5 * iqr
print("Q1", q1, " Q3", q3, " IQR", iqr, " fences", low, "to", high)
print("IQR outliers:", salary[(salary < low) | (salary > high)].tolist())

z = (salary - salary.mean()) / salary.std(ddof=0)
print("z scores:", z.round(2).tolist())
print("z above 3:", salary[z.abs() > 3].tolist(), " (the outlier itself pulls the mean and std)")
print("mean with outlier:", salary.mean(), " median:", salary.median())
print("clipped to fences:", salary.clip(low, high).tolist())
''')

K.code('merge_reshape', r'''
import pandas as pd

customers = pd.DataFrame({"cust_id": [1, 2, 3], "name": ["Asha", "Ravi", "Meena"]})
orders = pd.DataFrame({"order_id": [10, 11, 12, 13], "cust_id": [1, 1, 3, 4], "amount": [250, 100, 400, 90]})

inner = customers.merge(orders, on="cust_id", how="inner")
left = customers.merge(orders, on="cust_id", how="left")
print("inner join rows:", len(inner), " left join rows:", len(left))
print(left.to_string())

wide = pd.DataFrame({"student": ["Asha", "Ravi"], "maths": [90, 72], "physics": [85, 80]})
long = wide.melt(id_vars="student", var_name="subject", value_name="marks")
print(long.to_string())
back = long.pivot(index="student", columns="subject", values="marks")
print(back.to_string())
''')

K.code('knn_vs_mean', r'''
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer

rng = np.random.default_rng(4)
size = rng.uniform(40, 150, size=60)
price = 0.8 * size + rng.normal(0, 5, size=60)       # price follows size
data = pd.DataFrame({"size": size, "price": price})

hidden = rng.choice(60, size=12, replace=False)       # hide 12 prices
truth = data.loc[hidden, "price"].copy()
holes = data.copy()
holes.loc[hidden, "price"] = np.nan

mean_fill = holes["price"].fillna(holes["price"].mean())
knn_fill = KNNImputer(n_neighbors=3).fit_transform(holes)[:, 1]

mean_error = np.mean(np.abs(mean_fill[hidden] - truth))
knn_error = np.mean(np.abs(knn_fill[hidden] - truth))
print("average error, mean fill:", round(mean_error, 2))
print("average error, KNN fill: ", round(knn_error, 2))
''')

K.code('clean_function', r'''
import io
import numpy as np
import pandas as pd

raw = """id,city,size_m2,price,rooms
1,Delhi,80,52,2
2, mumbai ,65,71,2
3,DELHI,,48,3
4,Pune,120,unknown,4
5,Mumbai,70,75,
5,Mumbai,70,75,
6,pune,95,40,3
7,Delhi,2000,60,3
"""

def clean(df):
    df = df.drop_duplicates().copy()
    df["city"] = df["city"].str.strip().str.title()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df.loc[df["size_m2"] > 1000, "size_m2"] = np.nan          # 2000 m2 flat is a typing mistake
    for col in ["size_m2", "price", "rooms"]:
        df[col] = df[col].fillna(df.groupby("city")[col].transform("median"))
    df["rooms"] = df["rooms"].astype(int)
    return df

houses = clean(pd.read_csv(io.StringIO(raw)))
print(houses.to_string(index=False))

assert houses["id"].is_unique, "ids must be unique"
assert houses.isna().sum().sum() == 0, "no missing values left"
assert houses["size_m2"].between(10, 1000).all(), "sizes must be sensible"
print("all checks pass")
''')

K.lesson('inspect', 'Load the data and look before you touch it', f'''
{src('McKinney, Python for Data Analysis chapters 6 to 8 and 10, the pandas 3.0 user guide, the scikit-learn 1.8 imputation guide, Little and Rubin, Statistical Analysis with Missing Data chapter 1, and Tukey, Exploratory Data Analysis.')}
{wwh('<b>Data cleaning</b> means finding and fixing the problems in raw data: missing values, repeated rows, wrong types, messy text, impossible numbers and outliers. It starts with <b>inspecting</b> the data: its size, column types, missing counts and unusual values.',
     'A model learns whatever the data says, including its mistakes. "Garbage in, garbage out" is the first rule of machine learning. In real projects, cleaning and preparing data often takes more time than training the model.',
     'Load the file with pandas, then ask a fixed list of questions: how many rows and columns (shape), what type each column has (dtypes), how many values are missing (isna().sum()), are there repeated rows (duplicated()), and what values does each text column hold (unique()). Write down every problem before fixing anything.')}
{run('inspect_data')}
{table(['What the output shows', 'The problem', 'The fix (next lessons)'], [
    ['price has type str, not a number', 'One value is the word "unknown"', 'pd.to_numeric(errors="coerce")'],
    ['size_m2 has 1 missing, rooms has 2', 'Holes in the data', 'Drop or fill (impute)'],
    ['1 duplicated row', 'House 5 appears twice', 'drop_duplicates()'],
    ['Six different city spellings', 'Spaces and upper and lower case', 'str.strip().str.title()'],
    ['size_m2 of 2000 for a flat', 'Almost surely a typing mistake', 'Outlier check, then fix or remove']])}
{note('pandas 3.0 stores text in a new string type, shown as <code>str</code>, instead of the old <code>object</code>. Older tutorials show object for text columns. Both work the same way for cleaning.', 'tip')}
{scene('cooking with fresh ingredients', '<p>A chef checks every vegetable before cooking: throws out the rotten ones, washes the dirty ones and cuts them to the same size. Nobody blames the recipe when the ingredients were bad. Data cleaning is that check, and the model is the recipe.</p>')}
''', kw=['data cleaning', 'inspect data', 'shape', 'dtypes', 'isna', 'duplicated', 'unique', 'read_csv', 'garbage in garbage out'])

K.lesson('missing', 'Missing values: drop or fill', f'''
{viz('mlimpute')}
{wwh('A <b>missing value</b> is a hole in the table, shown by pandas as NaN (or None, or NaT for dates). You can <b>drop</b> rows or columns with holes, or <b>impute</b> (fill) them with a sensible value such as the mean, the median or the most common value.',
     'Most scikit-learn models refuse to train on NaN. Dropping is simple but throws away good information in the other columns: in the program below, dropping keeps only 3 of 6 rows. Filling keeps every row.',
     'For numbers use the median (safe with outliers) or the mean. For categories use the mode. Add a 0 or 1 column that says "this value was missing", because missingness itself can carry information. Compute the fill value on the training rows only, then use that same value for the test rows.')}
{run('fill_missing')}
{table(['Why the value is missing', 'Name', 'Example', 'What to do'], [
    ['Pure chance', 'MCAR (missing completely at random)', 'A sensor glitch loses some readings', 'Dropping or simple filling is fine'],
    ['Depends on other columns you have', 'MAR (missing at random)', 'Older people skip the "app usage" question', 'Fill using the other columns (KNN or iterative imputer)'],
    ['Depends on the missing value itself', 'MNAR (missing not at random)', 'People with high income hide their income', 'Add a missing flag. Any fill is biased']])}
{note('Fitting the imputer on the whole dataset before splitting lets test rows influence the fill value. That is data leakage (Foundations 1.2). Put the imputer inside a Pipeline so it is fitted on the training part only.', 'warn')}
''', kw=['missing values', 'NaN', 'dropna', 'fillna', 'imputation', 'SimpleImputer', 'missing indicator', 'MCAR', 'MAR', 'MNAR'])

K.lesson('types', 'Fix types, text, dates and duplicates', f'''
{wwh('Raw columns often have the wrong <b>type</b> (numbers stored as text), <b>messy text</b> (extra spaces, mixed case, different names for the same thing), dates stored as plain strings, and <b>duplicate</b> rows.',
     'A model sees "Delhi", " delhi" and "DELHI" as three different cities, and a price stored as text cannot be averaged at all. Duplicate rows count some examples twice and can leak the same row into both the training and the test set.',
     'Use the .str methods to strip spaces and fix case, replace to merge synonyms ("Bombay" into "mumbai"), pd.to_numeric and pd.to_datetime with errors="coerce" to turn bad values into NaN instead of crashing, and drop_duplicates to remove repeated rows.')}
{run('fix_types_text')}
{table(['Problem', 'pandas tool', 'Example'], [
    ['Extra spaces', 'str.strip()', '" Delhi " to "Delhi"'],
    ['Mixed case', 'str.lower(), str.title()', '"DELHI" to "delhi"'],
    ['Synonyms or typos', 'replace(dict)', '{{"bombay": "mumbai"}}'],
    ['Numbers as text', 'pd.to_numeric(errors="coerce")', '"unknown" becomes NaN'],
    ['Dates as text', 'pd.to_datetime(errors="coerce")', '"2024-02-30" becomes NaT'],
    ['Repeated rows', 'drop_duplicates(subset=...)', 'Keep the first copy'],
    ['Wrong integer type', 'astype(int)', 'After all holes are filled']])}
{note('errors="coerce" hides problems quietly. After using it, count the new NaN values and look at the original text of those rows, so you know what you turned into missing values.', 'tip')}
''', kw=['data types', 'astype', 'to_numeric', 'to_datetime', 'errors coerce', 'str strip', 'str lower', 'replace', 'drop_duplicates'])

K.lesson('outliers', 'Outliers: find them, then decide', f'''
{viz('mliqr')}
{wwh('An <b>outlier</b> is a value far away from the rest. The <b>IQR rule</b> flags values below Q1 &minus; 1.5 IQR or above Q3 + 1.5 IQR, where the IQR is the width of the middle half of the data. The <b>z score rule</b> flags values more than 3 standard deviations from the mean.',
     'Outliers can be mistakes (a 2,000 m<sup>2</sup> flat) that pull a linear model badly off course, or real rare events (fraud, a machine about to fail) that are exactly what you want to find. Either way you must know they are there.',
     'Compute the quartiles, the IQR and the fences, and list the values outside them. Then look at each one. Fix or remove clear mistakes. For real but extreme values, keep them, clip them to the fences (winsorising), use a log transform, or use a robust model such as a tree.')}
{run('find_outliers')}
{note('The z score rule missed the 150 in the program: z = 2.97, just under 3. The outlier itself raised the mean and the standard deviation, which hid it. This is called <b>masking</b>. The IQR rule uses quartiles, which one extreme value cannot move, so it is more robust.', 'exam')}
{fxs(fx('IQR fences', 'low = Q1 &minus; 1.5 &times; IQR, high = Q3 + 1.5 &times; IQR, IQR = Q3 &minus; Q1', 'Tukey’s box plot rule. Use 3 instead of 1.5 for far outliers.', key=True),
     fx('z score', 'z = (x &minus; mean) / std', 'Flag |z| &gt; 3. Easily fooled by the outliers themselves.', key=True),
     fx('Robust z score', 'z = 0.6745 (x &minus; median) / MAD', 'MAD is the median of |x &minus; median|. Flag |z| &gt; 3.5.'))}
''', kw=['outlier', 'IQR', 'quartile', 'box plot', 'z score', 'masking', 'winsorising', 'clip', 'robust statistics', 'MAD'])

K.lesson('combine', 'Combine and reshape tables', f'''
{wwh('Data often lives in several tables. <b>merge</b> joins two tables on a shared key, like SQL JOIN. <b>melt</b> turns wide tables (one column per subject) into long tables (one row per student and subject), and <b>pivot</b> turns them back.',
     'A model needs one row per example with all its features. Customer details and their orders are in different tables, so you join them. Many plotting and grouping tools want long data, while models want wide data, so you reshape.',
     'Pick the key column and the join type. An inner join keeps only keys found in both tables. A left join keeps every row of the left table and fills NaN where the right table has no match. After a merge, always check the row count, because a key that repeats multiplies rows.')}
{run('merge_reshape')}
{table(['Join', 'Keeps', 'In the program'], [
    ['inner', 'Only keys in both tables', '3 rows: customer 4 has no name and Ravi has no order'],
    ['left', 'Every left row', '4 rows: Ravi appears with NaN order'],
    ['right', 'Every right row', 'Would keep the order from customer 4'],
    ['outer', 'Every key from both', 'Ravi and customer 4 both appear']])}
{note('Asha has two orders, so she appears twice after the join. If you wanted one row per customer, group the orders first (for example total amount per customer) and then merge. Use merge(..., validate="one_to_one") to make pandas check this for you.', 'tip')}
''', kw=['merge', 'join', 'inner join', 'left join', 'melt', 'pivot', 'wide and long data', 'key'])

K.lesson('smart', 'Smarter filling compared', f'''
{run('knn_vs_mean')}
{versus('Ways to handle missing values', ['', 'Drop rows', 'Mean or median fill', 'KNN imputer', 'Iterative imputer', 'Model handles NaN'], [
    ['Idea', 'Remove rows with holes', 'One number for every hole', 'Average of the k most similar rows', 'Predict each column from the others, repeat', 'Trees learn which way NaN goes'],
    ['Keeps rows', 'No', 'Yes', 'Yes', 'Yes', 'Yes'],
    ['Uses other columns', 'No', 'No', 'Yes', 'Yes', 'Yes'],
    ['Speed', 'Fast', 'Fast', 'Slow on big data (needs distances)', 'Slowest', 'Fast'],
    ['Best when', 'Few holes, lots of data', 'MCAR, quick baseline', 'Similar rows have similar values', 'Columns are strongly related', 'HistGradientBoosting, XGBoost, LightGBM']],
    'start with median fill plus a missing flag, then try KNN or a model that handles NaN if the score matters.')}
{note('In the program, price depends on size. Mean filling ignores that and puts the same price on a small and a large flat, so its average error is 23.75. KNN looks at the 3 flats with the most similar size and is off by only 4.09. Scale the columns first in real data, because KNN uses distances.', 'tip')}
''', kw=['KNN imputer', 'IterativeImputer', 'mean imputation', 'HistGradientBoosting missing values', 'imputation comparison'])

K.lesson('pipeline', 'A cleaning function you can trust', f'''
{wwh('Put all the cleaning steps into one <b>function</b> that takes raw data and returns clean data, and finish it with <b>checks</b> (assert statements) that fail loudly if something is still wrong.',
     'New data arrives every week. If the cleaning lives in scattered notebook cells, someone will forget a step and the model will quietly get worse. A function gives the same result every time, and checks catch new kinds of mess the moment they appear.',
     'Write the steps in a fixed order: drop duplicates, fix text, fix types, mark impossible values as missing, fill holes, set final types. Then assert the rules your data must follow: ids are unique, nothing is missing, values sit in sensible ranges.')}
{run('clean_function')}
{steps('The cleaning checklist', [
    'Inspect: shape, dtypes, isna().sum(), duplicated().sum(), unique values of text columns, describe().',
    'Remove exact duplicates, then fix text (strip, case, synonyms).',
    'Convert types with errors="coerce" and count the new NaN values.',
    'Mark impossible values (negative ages, 2,000 m<sup>2</sup> flats) as NaN.',
    'Fill or drop the holes, with fill values learned from training data only.',
    'Validate with asserts, then save the clean data and the code that made it.'])}
{link('python', 'Need more pandas?', 'The Complete Python subject teaches pandas, files, CSV and JSON handling, and testing in more depth.', 'Open Complete Python')}
''', kw=['cleaning function', 'assert', 'data validation', 'reproducible cleaning', 'groupby transform', 'checklist'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Quantile position (pandas linear method)', 'position = (n &minus; 1) &times; q, then interpolate between the two nearest sorted values', 'Q1 is q = 0.25, the median q = 0.5, Q3 q = 0.75.', key=True),
     fx('IQR fences', 'Q1 &minus; 1.5 IQR and Q3 + 1.5 IQR', 'Values outside are outliers.', key=True),
     fx('Mean after mean filling', 'mean stays the same, variance shrinks by the factor (n<sub>known</sub> &minus; 1)/(n &minus; 1) or so', 'Every filled value sits exactly at the mean, adding no spread.', key=True),
     fx('z score', 'z = (x &minus; x&#772;) / s', 'Distance from the mean in standard deviations.'))}
{steps('Worked example: quartiles and fences by hand', [
    'Sorted values: 32, 35, 36, 38, 40, 41, 43, 45, 47, 150 (n = 10).',
    'Q1 position = 9 &times; 0.25 = 2.25, so Q1 = 36 + 0.25 &times; (38 &minus; 36) = 36.5.',
    'Q3 position = 9 &times; 0.75 = 6.75, so Q3 = 43 + 0.75 &times; (45 &minus; 43) = 44.5.',
    eq('IQR = 8, fences = 36.5 &minus; 12 = 24.5 and 44.5 + 12 = 56.5'),
    'Only 150 is above 56.5, so it is the only outlier. This matches the program.'])}
{deep('Why single imputation makes models too confident', '<p>Filling a hole with one value treats a guess as if it were measured, so the variance of the column and the standard errors of anything estimated from it come out too small. Multiple imputation (Rubin, 1987) fills each hole several times with random draws from a model, analyses each completed dataset, and combines the results so the uncertainty of the guesses is included. scikit-learn’s IterativeImputer with sample_posterior=True can produce such draws.</p>')}
''', kw=['quantile', 'IQR', 'fences', 'variance shrink', 'multiple imputation', 'z score'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Real data has holes, repeats, typing mistakes and strange values. Look at the data first, then fix each problem, and check the result.</p>',
    '<p>Inspect with shape, dtypes, isna and duplicated. Drop or fill missing values with mean, median or mode plus a missing flag, fix text and types with .str, to_numeric and to_datetime, find outliers with the IQR rule, and join tables with merge.</p>',
    '<p>Know MCAR, MAR and MNAR, use KNN or iterative imputers and models that accept NaN, avoid leakage by fitting imputers inside a Pipeline, use robust outlier rules, and write a validated cleaning function.</p>',
    '<p>Use multiple imputation for honest uncertainty, model the missingness mechanism, build data contracts and schema checks (for example with pandera or Great Expectations) into production pipelines, and monitor data quality over time (MLOps 1.3).</p>')}
{grow('Load a CSV, find missing values and duplicates, and fill holes with the median.',
      'Clean text, types and dates, flag outliers with the IQR rule, and merge tables safely.',
      'Pick an imputation method from the missingness mechanism and turn cleaning into a tested, validated pipeline.')}
''', kw=['beginner', 'expert', 'data contracts', 'schema validation', 'missingness mechanism'])

lc(2882, 'Drop Duplicate Rows', 'drop-duplicate-rows', 'e', 'pandas: drop_duplicates on one column', 'Keep the first row for each email. drop_duplicates with subset set to the email column does exactly that.', r'''
import pandas as pd


def dropDuplicateEmails(customers):
    return customers.drop_duplicates(subset=["email"], keep="first")
''', [('dropDuplicateEmails(pd.DataFrame({"customer_id": [1, 2, 3], "email": ["a@x.com", "b@x.com", "a@x.com"]}))["customer_id"].tolist()', [1, 2])])
lc(2883, 'Drop Missing Data', 'drop-missing-data', 'e', 'pandas: dropna on one column', 'Remove rows where the name is missing. dropna with subset set to the name column keeps rows with holes elsewhere.', r'''
def dropMissingData(students):
    return students.dropna(subset=["name"])
''', [('dropMissingData(pd.DataFrame({"student_id": [32, 217, 779], "name": ["Piper", None, "Georgia"], "age": [5, 19, 20]}))["student_id"].tolist()', [32, 779])])
lc(2885, 'Rename Columns', 'rename-columns', 'e', 'pandas: rename', 'Give rename a dictionary from old names to new names.', r'''
def renameColumns(students):
    return students.rename(columns={"id": "student_id", "first": "first_name", "last": "last_name", "age": "age_in_years"})
''', [('list(renameColumns(pd.DataFrame({"id": [1], "first": ["Mason"], "last": ["King"], "age": [6]})).columns)', ['student_id', 'first_name', 'last_name', 'age_in_years'])])
lc(2886, 'Change Data Type', 'change-data-type', 'e', 'pandas: astype', 'The grade column holds floats like 73.0. astype(int) turns them into whole numbers.', r'''
def changeDatatype(students):
    students["grade"] = students["grade"].astype(int)
    return students
''', [('changeDatatype(pd.DataFrame({"student_id": [1, 2], "grade": [73.0, 87.0]}))["grade"].tolist()', [73, 87])])
lc(2887, 'Fill Missing Data', 'fill-missing-data', 'e', 'pandas: fillna with a constant', 'A missing quantity here means none in stock, so fill it with 0.', r'''
def fillMissingValues(products):
    products["quantity"] = products["quantity"].fillna(0)
    return products
''', [('fillMissingValues(pd.DataFrame({"name": ["Wristwatch", "WirelessEarbuds"], "quantity": [None, 32]}))["quantity"].tolist()', [0.0, 32.0])])
lc(2890, 'Reshape Data: Melt', 'reshape-data-melt', 'e', 'pandas: melt wide to long', 'Keep product as the id column. Every quarter column becomes rows with a quarter name and a sales value.', r'''
def meltTable(report):
    return report.melt(id_vars=["product"], var_name="quarter", value_name="sales")
''', [('meltTable(pd.DataFrame({"product": ["Umbrella"], "quarter_1": [417], "quarter_2": [224]})).values.tolist()', [['Umbrella', 'quarter_1', 417], ['Umbrella', 'quarter_2', 224]])])
lc(1667, 'Fix Names in a Table', 'fix-names-in-a-table', 'e', 'pandas: string cleaning', 'str.capitalize makes the first letter upper case and the rest lower case. Then sort by user_id.', r'''
def fix_names(users):
    users["name"] = users["name"].str.capitalize()
    return users.sort_values("user_id")
''', [('fix_names(pd.DataFrame({"user_id": [2, 1], "name": ["bOB", "aLice"]}))["name"].tolist()', ['Alice', 'Bob'])])
lc(1517, 'Find Users With Valid E-Mails', 'find-users-with-valid-e-mails', 'e', 'pandas: str.match with a pattern', 'The name must start with a letter and use only letters, digits, underscore, dot or dash, followed by exactly @leetcode.com.', r'''
def valid_emails(users):
    pattern = "^[A-Za-z][A-Za-z0-9_.-]*@leetcode[.]com$"
    return users[users["mail"].str.match(pattern)]
''', [('valid_emails(pd.DataFrame({"user_id": [1, 2, 3, 4], "mail": ["winston@leetcode.com", "jonathanisgreat", "_annabelle@leetcode.com", "sally.come@leetcode.com"]}))["user_id"].tolist()', [1, 4])])
lc(196, 'Delete Duplicate Emails', 'delete-duplicate-emails', 'e', 'pandas: sort, then drop duplicates in place', 'Sort by id so the smallest id comes first, then drop later copies of each email. LeetCode checks the same table, so change it in place.', r'''
def delete_duplicate_emails(person):
    person.sort_values(by="id", inplace=True)
    person.drop_duplicates(subset="email", keep="first", inplace=True)


def after_delete(person):
    delete_duplicate_emails(person)
    return person["id"].tolist()
''', [('after_delete(pd.DataFrame({"id": [3, 1, 2], "email": ["john@x.com", "john@x.com", "bob@x.com"]}))', [1, 2])])
lc(183, 'Customers Who Never Order', 'customers-who-never-order', 'e', 'pandas: anti join with isin', 'Keep customers whose id is not in the customerId column of orders. The tilde sign means "not".', r'''
def find_customers(customers, orders):
    never = customers[~customers["id"].isin(orders["customerId"])]
    return never[["name"]].rename(columns={"name": "Customers"})
''', [('find_customers(pd.DataFrame({"id": [1, 2, 3, 4], "name": ["Joe", "Henry", "Sam", "Max"]}), pd.DataFrame({"id": [1, 2], "customerId": [3, 1]}))["Customers"].tolist()', ['Henry', 'Max'])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>LeetCode has a pandas track (the 30 Days of Pandas study plan) with exactly the cleaning moves from this chapter: drop duplicates, drop or fill missing values, rename, change types, reshape, clean text, validate emails with a pattern, and find rows with no match in another table. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'pandas', '30 Days of Pandas', 'drop_duplicates', 'dropna', 'fillna', 'melt', 'isin'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Inspect first</b>: shape, dtypes, isna().sum(), duplicated().sum(), unique values, describe().',
    '<b>Missing values</b>: drop, or fill with median (numbers) or mode (categories), and add a missing flag. Learn fill values on training data only.',
    'MCAR is pure chance, MAR depends on other columns, MNAR depends on the missing value itself.',
    'Fix text with .str.strip() and .str.lower(), merge synonyms with replace, convert with to_numeric and to_datetime (errors="coerce").',
    '<b>Outliers</b>: the IQR rule (Q1 &minus; 1.5 IQR, Q3 + 1.5 IQR) is robust. z scores can be masked. Decide: fix, remove, clip, or keep.',
    'merge joins tables (inner, left, right, outer). Check row counts after every merge. melt and pivot reshape.',
    'KNN and iterative imputers use the other columns and usually beat a single fill value.',
    'Wrap cleaning in a function and finish with assert checks.'],
    'Foundations 3.2 turns clean data into good features: encoding categories, scaling, new features and feature selection.')}
{files('Three tasks: count missing values per column, fill holes with the median, and find outliers with the IQR rule.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which pandas call counts missing values in each column?', ['df.count()', 'df.isna().sum()', 'df.unique()', 'df.shape'], 1, 'isna gives True for holes.', 'True counts as 1, so the sum per column counts the holes.')
K.quiz('e', 'Which fill value is safest for a numeric column with a few huge outliers?', ['Mean', 'Median', 'Maximum', 'Zero'], 1, 'Which one ignores extreme values?', 'The median hardly moves when a few values are extreme.')
K.quiz('e', 'For a city column with missing values, a simple fill is', ['The mean', 'The most common city (mode)', 'The median', 'The number 0'], 1, 'Categories have no average.', 'Use the mode for categorical columns.')
K.quiz('e', 'What does drop_duplicates() remove?', ['Missing values', 'Rows that repeat an earlier row', 'Outliers', 'Text columns'], 1, 'Repeated.', 'It keeps the first copy of each repeated row.')
K.quiz('m', 'pd.to_numeric(s, errors="coerce") turns the text "unknown" into', ['0', 'NaN', 'An error', '"unknown"'], 1, 'coerce means force.', 'Values that cannot be converted become NaN.')
K.quiz('m', 'A left join of customers (3 rows, keys 1 to 3) with orders whose keys are 1, 1, 3, 4 gives how many rows?', ['3', '4', '5', '2'], 1, 'Customer 1 has two orders and customer 2 has none.', 'Rows: 1, 1, 2 (with NaN), 3. Key 4 is dropped. 4 rows.')
K.quiz('m', 'People with high incomes often leave the income question blank. This is', ['MCAR', 'MAR', 'MNAR', 'Not missing'], 2, 'Missingness depends on the hidden value itself.', 'Missing not at random.')
K.quiz('m', 'Why add an "age_was_missing" column when filling ages?', ['To make the table bigger', 'Missingness may itself predict the target', 'Because sklearn requires it', 'To undo the filling'], 1, 'Holes can carry signal.', 'The model can learn whether a missing value matters.')
K.quiz('m', 'Q1 = 20 and Q3 = 30. With the 1.5 IQR rule, the high fence is', ['30', '45', '35', '40'], 1, 'IQR = 10.', '30 + 1.5 &times; 10 = 45.')
K.quiz('h', 'Fitting a SimpleImputer on the full dataset before the train and test split is wrong because', ['It is slower', 'Test values leak into the fill value', 'It changes the column type', 'It drops rows'], 1, 'Leakage.', 'Fit on training rows only, inside a Pipeline.')
K.quiz('h', 'Why can the z score rule miss a single huge outlier in a small sample?', ['z scores ignore large values', 'The outlier raises the mean and std, which shrinks its own z score', 'z scores only work for categories', 'It always finds it'], 1, 'Masking.', 'The extreme value inflates the very statistics used to judge it.')
K.quiz('h', 'Filling 40% of a column with its mean will', ['Increase its variance', 'Reduce its variance and weaken its correlation with other columns', 'Change its mean', 'Have no effect'], 1, 'All filled values sit at one point.', 'Spread shrinks and relations with other columns get diluted.')
K.quiz('x', 'In the style of a Stanford CS229 project review: a model uses "days_since_last_login", which is missing for users who never logged in. The best fix is', ['Fill with the mean', 'Fill with a large value or 0 and add a "never_logged_in" flag', 'Drop those users', 'Fill with the median'], 1, 'The hole has a meaning.', 'The value is structurally missing. A flag keeps that meaning and the fill keeps the column usable.')
K.quiz('x', 'In the style of a CMU 10-601 exam: Little and Rubin say listwise deletion (dropping rows) gives unbiased estimates when data is', ['MNAR', 'MCAR', 'MAR only', 'Never'], 1, 'Only pure chance keeps the remaining rows representative.', 'Under MCAR the complete rows are a random sample of all rows.')

K.calc('e', 'Values 4, ?, 8, 6. Mean of the known values?', '6', 'Ignore the hole.', ['Known: 4, 8, 6.', 'Sum 18.', eq('18 / 3 = 6')], check=6)
K.calc('e', 'Values 3, 9, ?, 5, 100. Median of the known values?', '7', 'Sort first.', ['Known sorted: 3, 5, 9, 100.', 'Even count, so average the middle two.', eq('(5 + 9) / 2 = 7')], check=7)
K.calc('e', 'A table has 1,000 rows. 50 have a missing price. What percent is missing?', '5', 'Part over whole.', ['50 / 1,000 = 0.05.', 'Times 100.', eq('5%')], check=5)
K.calc('m', 'Q1 = 12, Q3 = 20. Low fence with the 1.5 rule?', '0', 'Q1 &minus; 1.5 IQR.', ['IQR = 8.', '1.5 &times; 8 = 12.', eq('12 &minus; 12 = 0')], check=12 - 1.5 * 8)
K.calc('m', 'Mean 50, std 10. z score of 85?', '3.5', '(x &minus; mean) / std.', ['85 &minus; 50 = 35.', 'Divide by 10.', eq('z = 3.5')], check=(85 - 50) / 10)
K.calc('m', 'Sorted 2, 4, 6, 8, 10 (n = 5). Q1 by the pandas linear method?', '4', 'Position (n &minus; 1) &times; 0.25.', ['Position 4 &times; 0.25 = 1.', 'Value at position 1 (counting from 0).', eq('Q1 = 4')], check=4)
K.calc('m', 'Left table 5 rows, each key once. Right table has 2 rows for one key and 1 row for two other keys. Rows after a left join?', '6', 'Keys with no match stay once.', ['One key matches 2 rows: 2.', 'Two keys match 1 row each: 2. Two keys match nothing: 2.', eq('2 + 2 + 2 = 6')], check=6)
K.calc('h', 'Sorted 10, 20, 30, 40 (n = 4). Q3 by the pandas linear method?', '32.5', 'Position 3 &times; 0.75 = 2.25.', ['Between positions 2 (30) and 3 (40).', 'Go 0.25 of the way.', eq('30 + 0.25 &times; 10 = 32.5')], check=32.5)
K.calc('h', 'Known values 2, 4, 6 (population std 1.633). Two holes are filled with the mean 4. New population std, 3 decimals?', '1.265', 'Squared distances 4, 0, 4, 0, 0.', ['Sum of squares = 8.', 'Now n = 5, so variance = 1.6.', eq('&radic;1.6 = 1.265')], check=round((8 / 5) ** 0.5, 3))
K.calc('x', 'In the style of a Berkeley Data 100 exam: data 1, 2, 3, 4, 100. Median absolute deviation (MAD)?', '1', 'Median is 3.', ['|x &minus; 3| = 2, 1, 0, 1, 97.', 'Sorted: 0, 1, 1, 2, 97.', eq('MAD = median = 1')], check=1)

K.assign('countmiss', 'e', 'Count missing values per column',
         '<p>A table is a dictionary of column name to list of values, where None means missing. Write <code>count_missing(table)</code> that returns a dictionary of column name to the number of None values.</p>',
         '''
def count_missing(table):
    # your code here
    pass
''', [('count_missing({"age": [25, None, 30], "city": ["Delhi", None, None]})', {'age': 1, 'city': 2}), ('count_missing({"x": [1, 2]})', {'x': 0})],
         '''
def count_missing(table):
    result = {}
    for name in table:
        count = 0
        for value in table[name]:
            if value is None:
                count = count + 1
        result[name] = count
    return result
''', 'Loop over the columns. Inside, loop over the values and count the ones that are None.', '<p>This is what df.isna().sum() does, written by hand.</p>')
K.assign('medianfill', 'e', 'Fill holes with the median',
         '<p>Write <code>fill_median(values)</code> that replaces every None in a list of numbers with the median of the known numbers. Return the new list. Do not use statistics or numpy.</p>',
         '''
def fill_median(values):
    # your code here
    pass
''', [('fill_median([4, None, 8, 6])', [4, 6, 8, 6]), ('fill_median([3, 9, None, 5, 100])', [3, 9, 7.0, 5, 100]), ('fill_median([None, 2])', [2, 2])],
         '''
def fill_median(values):
    known = sorted([v for v in values if v is not None])
    n = len(known)
    if n % 2 == 1:
        median = known[n // 2]
    else:
        median = (known[n // 2 - 1] + known[n // 2]) / 2
    result = []
    for v in values:
        if v is None:
            result.append(median)
        else:
            result.append(v)
    return result
''', 'Sort the known values. Odd count: take the middle one. Even count: average the two middle ones. Then rebuild the list.', '<p>In a real project you would compute the median on the training rows and reuse it for the test rows.</p>')
K.assign('iqrout', 'm', 'Find outliers with the IQR rule',
         '<p>Write <code>iqr_outliers(values)</code> that returns the sorted list of outliers using the 1.5 IQR rule. Compute Q1 and Q3 with the pandas linear method: position = (n &minus; 1) &times; q, then move between the two nearest sorted values.</p>',
         '''
def iqr_outliers(values):
    # your code here
    pass
''', [('iqr_outliers([32, 35, 36, 38, 40, 41, 43, 45, 47, 150])', [150]), ('iqr_outliers([1, 2, 3, 4, 5])', []), ('iqr_outliers([2, 5, 30, 32, 33, 35, 36, 38, 40, 90])', [2, 5, 90])],
         '''
def quantile(sorted_values, q):
    position = (len(sorted_values) - 1) * q
    low = int(position)
    high = min(low + 1, len(sorted_values) - 1)
    part = position - low
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * part


def iqr_outliers(values):
    s = sorted(values)
    q1 = quantile(s, 0.25)
    q3 = quantile(s, 0.75)
    iqr = q3 - q1
    low_fence = q1 - 1.5 * iqr
    high_fence = q3 + 1.5 * iqr
    result = []
    for v in s:
        if v < low_fence or v > high_fence:
            result.append(v)
    return result
''', 'Write a small quantile helper first. Then compute the fences and keep the values outside them.', '<p>Check your helper against pandas: pd.Series(values).quantile(0.25) uses the same linear method.</p>')

K.must('Inspect', 'shape, dtypes, isna().sum(), duplicated().sum(), unique(), describe(). Write down problems before fixing.')
K.must('Missing values', 'dropna or fillna. Median for numbers, mode for categories, plus a missing flag. Fit the imputer on training data only.')
K.must('MCAR, MAR, MNAR', 'Pure chance, depends on other columns, depends on the missing value. Dropping is only unbiased under MCAR.')
K.must('Types and text', 'str.strip, str.lower, replace, to_numeric and to_datetime with errors="coerce", astype, drop_duplicates.')
K.must('Outliers', 'IQR fences Q1 &minus; 1.5 IQR and Q3 + 1.5 IQR (robust). |z| &gt; 3 can be masked. Fix, remove, clip or keep.')
K.must('Combine', 'merge on a key: inner, left, right, outer. Check row counts. melt makes long data, pivot makes wide data.')

T = K.topic(
    slug='ml-data-cleaning', topic='ml-data-cleaning', step=(3, 'Working with data', 'ml-f3', 'Real data is messy. Load it, clean it, and turn it into features a model can learn from.', 'Beginner'),
    title='Data cleaning: missing values, types, outliers and joins', short='Data cleaning', badge='3.1', minutes=60,
    lead='Learn to turn messy raw data into a clean table: inspect it, drop or fill missing values, fix types, text and dates, remove duplicates, find outliers with the IQR rule, join and reshape tables, and wrap it all in a checked cleaning function.',
    desc='inspecting data with shape, dtypes, isna and duplicated, missing values, dropna, fillna, SimpleImputer, KNNImputer, missing indicators, MCAR, MAR and MNAR, string cleaning, to_numeric and to_datetime with coerce, duplicates, outliers with IQR and z scores, masking, clipping, merge and join types, melt and pivot, cleaning functions with asserts, pandas LeetCode problems.',
    summary='inspecting data, missing values and imputation, types and text, outliers, joins and reshaping, and a validated cleaning function.',
    keywords=['data cleaning', 'missing values', 'imputation', 'fillna', 'outliers', 'IQR', 'merge', 'melt', 'duplicates', 'pandas'],
    recap='<p>Clean data first. A simple model on clean data beats a clever model on messy data.</p>',
    added='2026-11-13', leet=leet_items())
