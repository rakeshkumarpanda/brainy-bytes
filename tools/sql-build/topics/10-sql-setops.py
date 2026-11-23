# Chapter 3.4: set operations: UNION, UNION ALL, INTERSECT, EXCEPT (MINUS in Oracle), rules for column counts and
# types, ORDER BY on a compound select, NULLs treated as equal. Sources: sqlite.org lang_select.html (compound select
# operators, ORDER BY and LIMIT apply to the whole compound), nulls.html (NULLs indistinct for UNION).
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('union', 'UNION and UNION ALL: stacking results', f'''
<p>Joins put tables side by side. <b>Set operations</b> stack results on top of each other. "Every city where we have a customer or a warehouse" is the customer cities stacked on the warehouse cities.</p>
{pk('sqset')}
{K.sql('union', """SELECT city FROM customers WHERE city IS NOT NULL
UNION
SELECT city FROM warehouses
ORDER BY city;""", title='All cities we deal with, each once', notes={2: 'UNION removes duplicate rows, so Pune appears once.', 4: 'ORDER BY at the end sorts the whole combined result.'})}
{K.sql('unionall', """SELECT 'customer' AS kind, name FROM customers
UNION ALL
SELECT 'employee', name FROM employees
LIMIT 5;""", db='', setup="""CREATE TABLE customers (name TEXT); INSERT INTO customers VALUES ('Asha'), ('Ravi');
CREATE TABLE employees (name TEXT); INSERT INTO employees VALUES ('Asha'), ('Priya'), ('Rahul');""", title='UNION ALL keeps every row, and is faster', notes={2: 'No duplicate removal: two different Ashas both stay, which is right here.'})}
{table(['Rule', 'Why'], [
    ['Both queries must return the same number of columns', 'rows are stacked column by column'],
    ['Matching columns should hold the same kind of data', 'a name on top of a price makes no sense, and strict engines refuse it'],
    ['Column names come from the first query', 'so put aliases there'],
    ['ORDER BY and LIMIT go once, at the very end', 'they apply to the whole combined result']])}
{note('UNION has to find and remove duplicates, which costs a sort or hash. When you know there are no duplicates, or you want them, use UNION ALL.', 'tip')}
{K.lab('l-union', 'e', 'Every place we know', 'List every city that appears either as a customer city or a warehouse city, each once, and leave out NULL.', 'SELECT city FROM customers WHERE city IS NOT NULL UNION SELECT city FROM warehouses;', hint='Two SELECTs joined by UNION.', why='UNION stacks the results and removes duplicates.')}
''', kw=['UNION', 'UNION ALL', 'set operation', 'compound select', 'stack results', 'duplicates'])
K.talk('union', '''Joins put tables side by side, but set operations stack results on top of each other. UNION takes the rows of two queries and removes duplicates,
so every city where we have a customer or a warehouse appears once. UNION ALL keeps every row, duplicates included, and is faster because it does
not need to search for repeats. Both queries must return the same number of columns, and the column names come from the first query. ORDER BY and
LIMIT are written once at the very end, and they apply to the whole stacked result. Watch the animation light up which cities survive each operator.
Think of pouring two bags of marbles into one jar.''')

K.lesson('intersect', 'INTERSECT and EXCEPT', f'''
<p><code>INTERSECT</code> keeps rows that appear in <b>both</b> results. <code>EXCEPT</code> keeps rows of the first result that do <b>not</b> appear in the second. Oracle calls EXCEPT <code>MINUS</code>.</p>
{K.sql('inter', """-- Cities with both customers and a warehouse
SELECT city FROM customers
INTERSECT
SELECT city FROM warehouses;

-- Customer cities with no warehouse yet
SELECT city FROM customers WHERE city IS NOT NULL
EXCEPT
SELECT city FROM warehouses;""", title='Both, and only the first', notes={3: 'Only Pune and Chennai are in both lists.', 8: 'Delhi and Bhubaneswar have customers but no warehouse: a planning question.'})}
{table(['Operator', 'Venn diagram idea', 'Duplicates', 'Also written'], [
    ['UNION', 'everything in A or B', 'removed', ''],
    ['UNION ALL', 'everything, counted twice if in both', 'kept', ''],
    ['INTERSECT', 'the overlap of A and B', 'removed', 'INTERSECT ALL in PostgreSQL'],
    ['EXCEPT', 'A without B', 'removed', 'MINUS in Oracle, EXCEPT ALL in PostgreSQL']])}
{steps('Order matters for EXCEPT', [
    'A EXCEPT B keeps what is in A and missing from B.',
    'B EXCEPT A keeps what is in B and missing from A.',
    'Warehouse cities EXCEPT customer cities gives Mumbai and Kolkata: warehouses with no local customers.',
    eq('UNION and INTERSECT give the same rows either way round, EXCEPT does not')])}
{K.lab('l-except', 'm', 'Warehouses without local customers', 'List warehouse cities where no customer lives.', 'SELECT city FROM warehouses EXCEPT SELECT city FROM customers;', hint='Warehouses first, then EXCEPT the customer cities.', why='EXCEPT keeps rows of the first query that the second query does not return.')}
''', kw=['INTERSECT', 'EXCEPT', 'MINUS', 'Venn diagram', 'set difference', 'intersection'])
K.talk('intersect', '''INTERSECT keeps only rows that appear in both results, like the overlap in the middle of a Venn diagram. EXCEPT keeps rows from the first result that
do not appear in the second, and Oracle calls it MINUS. The order matters for EXCEPT, warehouse cities except customer cities gives warehouses with
no local customers, while the other way round gives customer cities with no warehouse. UNION and INTERSECT give the same rows whichever way round
you write them. These operators answer planning questions quickly, such as where should the next warehouse go. Think of two friends comparing
sticker albums to see which stickers both have, and which only one has.''')

K.lesson('rules', 'Set operations versus joins and NULLs', f'''
<p>Set operations compare <b>whole rows</b>, and here NULLs count as equal, unlike in a WHERE test. That makes INTERSECT and EXCEPT a neat, NULL safe way to compare two tables row by row, for example to check that a copy of a table matches the original.</p>
{K.sql('nullset', """SELECT NULL AS city
INTERSECT
SELECT NULL;

SELECT CASE WHEN NULL = NULL THEN 'equal' ELSE 'not known' END;""", db='', title='NULL meets NULL in a set operation', notes={1: 'INTERSECT returns one row holding NULL: the two NULLs were treated as the same row.', 5: 'But = still says unknown.'})}
{table(['Question', 'Set operation', 'Join or subquery form'], [
    ['In A or B', 'A UNION B', 'FULL OUTER JOIN (with COALESCE)'],
    ['In both', 'A INTERSECT B', 'JOIN, or WHERE EXISTS'],
    ['In A, not in B', 'A EXCEPT B', 'LEFT JOIN ... WHERE b.key IS NULL, or NOT EXISTS']])}
{scene('checking a data migration', '<p>A company copies its customers table from an old system to a new one. To prove nothing was lost or changed, an engineer runs <code>SELECT * FROM old_customers EXCEPT SELECT * FROM new_customers</code> and then the same the other way round. Two empty results mean the tables hold exactly the same rows, including rows with NULLs.</p>')}
{K.lab('l-both', 'm', 'Cities with customers and a warehouse', 'List the cities that appear in both <code>customers</code> and <code>warehouses</code>.', 'SELECT city FROM customers INTERSECT SELECT city FROM warehouses;', hint='INTERSECT keeps the overlap.', why='Only rows present in both results survive INTERSECT.')}
''', kw=['NULL in set operations', 'compare tables', 'data migration check', 'EXCEPT vs NOT EXISTS'])
K.talk('rules', '''Set operations compare whole rows, and in this one place NULLs count as equal. So INTERSECT of NULL and NULL gives back one NULL row, even though
NULL equals NULL is still unknown in a WHERE test. That makes EXCEPT a neat tool for checking that two tables hold exactly the same rows. Engineers
moving data to a new system run old except new, and new except old, and two empty answers prove the copy is perfect. Every set operation also has
a join or subquery twin, for example EXCEPT behaves like NOT EXISTS. Think of comparing two class lists side by side, line by line, to make sure
no child was left out.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>UNION pours two lists together, INTERSECT keeps what both share, EXCEPT takes one list away from the other.</p>',
    '<p>Set operations need union compatible inputs: the same number of columns with compatible types. Duplicates are removed unless you write ALL.</p>',
    '<p>In relational algebra these are union (∪), intersection (∩) and difference (−). SQL’s bag versions with ALL follow multiset rules: UNION ALL adds counts, INTERSECT ALL takes the smaller count, EXCEPT ALL subtracts counts.</p>',
    '<p>Engines implement duplicate removing set operations with sorting or hashing, much like GROUP BY. In SQLite, EXPLAIN QUERY PLAN shows a line such as COMPOUND QUERY with a temporary B-tree for UNION.</p>')}
{deep('UNION ALL as a view over partitions', '<p>Before native partitioning existed, people split a big table by year into sales_2024, sales_2025 and so on, then made one view: <code>SELECT * FROM sales_2024 UNION ALL SELECT * FROM sales_2025</code>. Queries on the view read every part, and some engines can skip parts whose CHECK rules exclude the requested dates.</p>')}
''', kw=['union compatible', 'multiset', 'bag semantics', 'INTERSECT ALL', 'EXCEPT ALL', 'partition view'])
K.talk('levels', '''One more climb. For a beginner, UNION pours lists together, INTERSECT keeps what both share, and EXCEPT takes one list away from another. At college
level, the inputs must be union compatible, with the same number of columns and similar types. At masters level, these are union, intersection and
difference from relational algebra, and the ALL versions follow multiset rules, adding, taking the smaller count, or subtracting counts. At research
level, engines remove duplicates with sorting or hashing, just like GROUP BY. Think of a shop that merges stock lists from two branches at the end
of the day.''')

K.quiz('e', 'UNION removes', ['Nothing', 'Duplicate rows', 'NULL rows', 'The second query'], 1, 'Each once.', 'UNION removes duplicates, UNION ALL keeps them.')
K.quiz('e', 'Which keeps rows in both results?', ['UNION', 'INTERSECT', 'EXCEPT', 'UNION ALL'], 1, 'Overlap.', 'INTERSECT is the overlap.')
K.quiz('e', 'Oracle’s name for EXCEPT is', ['DIFF', 'MINUS', 'REMOVE', 'WITHOUT'], 1, 'Subtract.', 'Oracle uses MINUS.')
K.quiz('e', 'Two queries in a UNION must have the same', ['Table', 'Number of columns', 'WHERE', 'Row count'], 1, 'Stacked.', 'Rows are stacked column by column.')
K.quiz('m', 'Where does ORDER BY go in a UNION?', ['After each SELECT', 'Once at the end', 'Before UNION', 'It is not allowed'], 1, 'Whole result.', 'It sorts the combined result.')
K.quiz('m', 'Which is faster when duplicates do not matter?', ['UNION', 'UNION ALL', 'Same speed', 'INTERSECT'], 1, 'No dedupe.', 'UNION ALL skips the duplicate removal.')
K.quiz('m', 'A EXCEPT B equals B EXCEPT A', ['Always', 'Never in general', 'Only with ALL', 'Only for numbers'], 1, 'Order matters.', 'Difference is not symmetric.')
K.quiz('m', 'The result column names of a UNION come from', ['The second query', 'The first query', 'Both', 'They are numbered'], 1, 'First.', 'Put aliases in the first query.')
K.quiz('h', 'In a set operation, two NULLs are treated as', ['Different', 'Equal', 'An error', 'Removed'], 1, 'Indistinct.', 'Set operations treat NULLs as the same value.')
K.quiz('h', 'Which join form matches A EXCEPT B on a key?', ['INNER JOIN', 'LEFT JOIN ... WHERE b.key IS NULL', 'CROSS JOIN', 'RIGHT JOIN'], 1, 'Anti join.', 'Keep A rows with no B partner.')
K.quiz('x', 'Under bag semantics, a row appears 3 times in A and 1 time in B. How many times in A EXCEPT ALL B?', ['0', '1', '2', '3'], 2, 'Subtract counts.', '3 − 1 = 2.')

n_union = value('shop', 'SELECT count(*) FROM (SELECT city FROM customers WHERE city IS NOT NULL UNION SELECT city FROM warehouses)')
n_all = value('shop', 'SELECT count(*) FROM (SELECT city FROM customers WHERE city IS NOT NULL UNION ALL SELECT city FROM warehouses)')
n_int = value('shop', 'SELECT count(*) FROM (SELECT city FROM customers INTERSECT SELECT city FROM warehouses)')
n_exc = value('shop', 'SELECT count(*) FROM (SELECT city FROM customers WHERE city IS NOT NULL EXCEPT SELECT city FROM warehouses)')
K.calc('e', 'How many rows does the customer cities UNION warehouse cities query return (NULL left out)?', str(n_union), 'Each city once.',
       ['Customer cities: Pune, Delhi, Chennai, Bhubaneswar.', 'Warehouses add Mumbai and Kolkata.', eq(f'{n_union} cities')], check=n_union)
K.calc('e', 'And with UNION ALL?', str(n_all), 'Every row kept.',
       ['7 customers have a city.', '4 warehouses.', eq(f'7 + 4 = {n_all}')], check=n_all)
K.calc('m', 'How many cities are in both lists (INTERSECT)?', str(n_int), 'The overlap.',
       ['Customer cities: Pune, Delhi, Chennai, Bhubaneswar.', 'Warehouse cities: Pune, Mumbai, Chennai, Kolkata.', eq('Pune and Chennai: 2')], check=n_int)
K.calc('m', 'How many customer cities have no warehouse (EXCEPT)?', str(n_exc), 'First minus second.',
       ['Customer cities: Pune, Delhi, Chennai, Bhubaneswar.', 'Remove Pune and Chennai.', eq('Delhi and Bhubaneswar: 2')], check=n_exc)
K.calc('m', 'Check: |A ∪ B| = |A| + |B| − |A ∩ B| for the distinct city sets. What is |A| + |B| − |A ∩ B|?', str(4 + 4 - n_int), '4 distinct customer cities, 4 warehouse cities.',
       ['|A| = 4, |B| = 4.', f'|A ∩ B| = {n_int}.', eq(f'4 + 4 − {n_int} = {8 - n_int}, the same as the UNION count')], check=8 - n_int)
K.calc('h', 'Total warehouse capacity in cities where we also have customers?', str(value('shop', 'SELECT sum(capacity) FROM warehouses WHERE city IN (SELECT city FROM customers)')), 'Pune and Chennai.',
       ['Pune 5000.', 'Chennai 4000.', eq('9000')], check=value('shop', 'SELECT sum(capacity) FROM warehouses WHERE city IN (SELECT city FROM customers)'))
K.calc('h', 'A row is in A 3 times and in B 1 time. How many times is it in A UNION ALL B?', '4', 'Add counts.',
       ['UNION ALL keeps every row.', '3 from A and 1 from B.', eq('3 + 1 = 4')], check=4)
K.calc('h', 'How many rows does SELECT NULL INTERSECT SELECT NULL return?', '1', 'NULLs are equal here.',
       ['Set operations treat NULLs as the same value.', 'So the NULL row is in both inputs.', eq('1 row')], check=value('', 'SELECT count(*) FROM (SELECT NULL INTERSECT SELECT NULL)'))

K.must('Stacking', 'UNION, UNION ALL, INTERSECT and EXCEPT stack results. Same number of columns, names from the first query, ORDER BY once at the end.')
K.must('Duplicates', 'UNION, INTERSECT and EXCEPT remove duplicates. UNION ALL keeps them and is faster.')
K.must('EXCEPT', 'Rows of the first query missing from the second. Order matters. MINUS in Oracle.')
K.must('NULLs', 'Set operations treat NULLs as equal, so EXCEPT compares tables safely.')
K.must('Twins', 'INTERSECT is like EXISTS, EXCEPT like NOT EXISTS or an anti join.')

T = K.topic(
    slug='sql-setops', topic='sql-setops', step=(3, 'Many tables', 'sql-many', 'Keys and relationships, every kind of join, subqueries and set operations.', 'Intermediate'),
    title='Set operations: UNION, INTERSECT and EXCEPT', short='Set operations', badge='3.4', minutes=30, added='2026-11-23',
    lead='Stack query results with UNION and UNION ALL, find overlaps with INTERSECT and differences with EXCEPT, and use them to compare whole tables safely.',
    desc='UNION and UNION ALL, INTERSECT, EXCEPT and MINUS, column count and naming rules, ORDER BY on a compound select, NULLs in set operations, comparing tables, bag semantics.',
    summary='UNION, UNION ALL, INTERSECT and EXCEPT, their rules, and comparing tables.',
    keywords=['UNION', 'UNION ALL', 'INTERSECT', 'EXCEPT', 'MINUS', 'set operations'],
    recap='<p>Set operations stack whole rows: UNION for either, INTERSECT for both, EXCEPT for first only, with NULLs treated as equal.</p>')
