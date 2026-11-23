# Chapter 7.2: query plans and tuning: the query optimizer, EXPLAIN QUERY PLAN in SQLite and EXPLAIN / EXPLAIN ANALYZE
# elsewhere, join algorithms (nested loop, hash, merge), join order, statistics and ANALYZE, sargable predicates, keyset
# pagination versus OFFSET, the N+1 query problem, and a tuning routine.
# Sources: sqlite.org eqp.html (EXPLAIN QUERY PLAN output: SCAN, SEARCH, COVERING INDEX, USE TEMP B-TREE, AUTOMATIC
# INDEX), optoverview.html (nested loop joins, automatic indexes), queryplanner-ng.html (NGQP), lang_analyze.html
# (sqlite_stat1), postgresql.org using-explain.html (cost, rows, EXPLAIN ANALYZE, hash and merge joins),
# Selinger et al. 1979 "Access Path Selection in a Relational Database Management System" (System R optimizer).
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('explain', 'Asking the optimizer: EXPLAIN QUERY PLAN', f'''
<p>SQL says <b>what</b> you want, not <b>how</b> to get it. The <b>query optimizer</b> (also called the planner) picks the how: which index, which table first, whether to sort. <code>EXPLAIN QUERY PLAN</code> shows its choice without running the query.</p>
{pk('sqplan')}
{table(['Plan line in SQLite', 'Meaning'], [
    ['SCAN t', 'read every row of t'],
    ['SCAN t USING COVERING INDEX i', 'read all of index i, which is smaller than the table'],
    ['SEARCH t USING INDEX i (col=?)', 'jump into index i, then fetch matching rows'],
    ['SEARCH t USING INTEGER PRIMARY KEY (rowid=?)', 'jump straight to rows by their key'],
    ['USE TEMP B-TREE FOR ORDER BY', 'sort the result in a temporary structure'],
    ['AUTOMATIC COVERING INDEX', 'build a throwaway index for this one query'],
    ['SCALAR SUBQUERY, CORRELATED SCALAR SUBQUERY', 'an inner query run once, or once per outer row']])}
{K.sql('eqp', """EXPLAIN QUERY PLAN
SELECT c.name, COUNT(*) AS orders
FROM customers c JOIN orders o ON o.customer_id = c.id
GROUP BY c.id
ORDER BY orders DESC;""", title='Read a plan from the top', notes={3: 'One table is scanned, the other is reached by key or a temporary index.', 5: 'Sorting by a computed count always needs a temporary B-tree.'})}
{note('PostgreSQL and MySQL write EXPLAIN, and EXPLAIN ANALYZE also runs the query and reports real row counts and times. SQL Server shows graphical execution plans. The ideas are the same.', 'tip')}
''', kw=['query optimizer', 'query planner', 'EXPLAIN QUERY PLAN', 'EXPLAIN ANALYZE', 'SCAN', 'SEARCH', 'TEMP B-TREE'])
K.talk('explain', '''SQL says what you want, not how to get it. A part of the engine called the query optimizer decides how, choosing which index to use, which table to
read first and whether to sort. EXPLAIN QUERY PLAN shows that choice without running the query. Each line names a step. SCAN means read every row,
SEARCH means jump in through an index, and USE TEMP B TREE means sort the result. In the animation, type a query or pick one, switch indexes on and off,
and read the real plan SQLite chooses. PostgreSQL and MySQL have EXPLAIN and EXPLAIN ANALYZE, which also shows real timings. Think of a taxi app that
plans the route before the driver sets off.''')

K.lesson('joins', 'How joins are executed', f'''
<p>A join is a question, and engines have several algorithms to answer it. The optimizer also picks the <b>join order</b>: which table drives the loop.</p>
{table(['Algorithm', 'How it works', 'Good when'], [
    ['Nested loop', 'for each row of the outer table, look up matching rows in the inner table', 'the inner table has an index on the join column'],
    ['Hash join', 'build a hash table of the smaller input, then probe it with each row of the other', 'big unsorted inputs, equality joins (PostgreSQL, MySQL 8, SQL Server)'],
    ['Merge join', 'sort both inputs on the key, then walk them side by side', 'inputs already sorted, for example by an index']])}
{K.sql('nl', """EXPLAIN QUERY PLAN
SELECT p.name, oi.qty
FROM order_items oi JOIN products p ON p.id = oi.product_id;""", title='SQLite uses nested loops', notes={3: 'Scan order_items, and for each line jump to its product by primary key.'})}
{K.sql('auto', """CREATE TABLE visits (customer_id INTEGER, page TEXT);
INSERT INTO visits VALUES (1, 'home'), (2, 'cart'), (1, 'cart');
EXPLAIN QUERY PLAN
SELECT c.name, v.page FROM customers c JOIN visits v ON v.customer_id = c.id;""", title='No useful index: the plan still finds a way', notes={4: 'The plan either scans visits and looks up customers by key, or builds an automatic index when that is cheaper. Either way, an index on visits(customer_id) would remove the guesswork.'})}
{steps('Cost of a nested loop join', [
    'Outer table with N rows, inner table with M rows.',
    'Without an index: each outer row scans the inner table.',
    'With an index on the inner join column: each outer row does about log M steps.',
    eq('N × M without an index, about N × log M with one')])}
''', kw=['nested loop join', 'hash join', 'merge join', 'join order', 'automatic index', 'join algorithm'])
K.talk('joins', '''A join is a question, and the engine has several ways to answer it. A nested loop join takes each row of one table and looks up matches in the
other, which is fast when the inner table has an index on the join column. A hash join builds a hash table from the smaller input and probes it with the
other, which suits big unsorted tables. A merge join sorts both sides and walks them together. SQLite uses nested loops and can build a temporary index
when none exists, which is a hint that you should create one. The optimizer also chooses which table drives the loop. Think of matching socks, by
picking one and searching the pile, or by sorting both piles first.''')

K.lesson('stats', 'Statistics and the cost based optimizer', f'''
<p>Most optimizers are <b>cost based</b>: they estimate how many rows each step returns and pick the plan with the lowest estimated cost. The idea goes back to IBM’s System R (Selinger and colleagues, 1979). Estimates come from <b>statistics</b> about the data.</p>
{K.sql('analyze', """CREATE INDEX idx_status ON orders(status);
ANALYZE;
SELECT tbl, idx, stat FROM sqlite_stat1 WHERE tbl = 'orders';""", title='ANALYZE gathers statistics', notes={2: 'Reads the tables and indexes and stores summaries.', 3: 'stat holds the row count and the average rows per distinct key, for example 10 3.'})}
{table(['Engine', 'Gather statistics', 'See estimates and reality'], [
    ['SQLite', 'ANALYZE, or PRAGMA optimize', 'EXPLAIN QUERY PLAN'],
    ['PostgreSQL', 'ANALYZE (autovacuum runs it automatically)', 'EXPLAIN ANALYZE: estimated rows versus actual rows'],
    ['MySQL', 'ANALYZE TABLE', 'EXPLAIN ANALYZE (8.0.18+)'],
    ['SQL Server', 'UPDATE STATISTICS, automatic by default', 'actual execution plan']])}
{scene('the report that got slow overnight', '<p>A sales report ran in one second for months, then suddenly took two minutes. A bulk import had added millions of rows, but the statistics still described the old, small table. The optimizer kept choosing a nested loop that was perfect for a few rows. Running ANALYZE gave it fresh numbers, it switched to a hash join, and the report was fast again.</p>')}
{note('When estimated and actual row counts in EXPLAIN ANALYZE differ by a factor of 10 or more, look at statistics first. Bad estimates are the most common cause of bad plans.', 'tip')}
''', kw=['cost based optimizer', 'statistics', 'ANALYZE', 'sqlite_stat1', 'cardinality estimate', 'System R', 'Selinger'])
K.talk('stats', '''Most optimizers are cost based. For each possible plan they estimate how many rows every step will return, add up a cost, and pick the cheapest. The
idea comes from IBM's System R research in nineteen seventy nine. Those estimates rely on statistics about the data, such as how many rows a table has
and how many rows share each value. ANALYZE gathers these statistics. If they go stale, for example after a big import, the optimizer can choose a plan
that was right for a small table and terrible for a large one. Think of a delivery company planning routes with last year's traffic map.''')

K.lesson('tuning', 'Writing queries the optimizer can help', f'''
<p>Many slow queries are fixed by small rewrites. A condition the engine can answer with an index is called <b>sargable</b> (search argument able).</p>
{table(['Slow pattern', 'Faster rewrite'], [
    ["WHERE substr(order_date, 1, 7) = '2025-06'", "WHERE order_date >= '2025-06-01' AND order_date < '2025-07-01'"],
    ['WHERE price * 1.18 > 1000', 'WHERE price > 1000 / 1.18'],
    ['SELECT * when you need two columns', 'name the columns, which may allow a covering index'],
    ['LIMIT 10 OFFSET 100000', 'keyset paging: WHERE id > last_seen_id ORDER BY id LIMIT 10'],
    ['one query per customer inside a loop in the app', 'one query with a JOIN or IN for all customers']])}
{K.sql('sarg', """CREATE INDEX idx_date ON orders(order_date);
EXPLAIN QUERY PLAN SELECT id FROM orders WHERE substr(order_date, 1, 7) = '2025-06';
EXPLAIN QUERY PLAN SELECT id FROM orders WHERE order_date >= '2025-06-01' AND order_date < '2025-07-01';""", title='Same rows, different plans', notes={2: 'A function on the column: the index cannot be searched.', 3: 'A plain range on the column: SEARCH using idx_date.'})}
{K.sql('keyset', """SELECT id, order_date FROM orders ORDER BY id LIMIT 3 OFFSET 6;
SELECT id, order_date FROM orders WHERE id > 106 ORDER BY id LIMIT 3;""", title='OFFSET paging versus keyset paging', notes={1: 'OFFSET still walks past the first 6 rows. On page 10,000 that is a lot of wasted reading.', 2: 'Keyset paging remembers the last id shown and jumps straight there.'})}
{scene('the N+1 problem', '<p>A web page lists 50 customers with their order counts. The code runs one query for the customers, then one more query per customer: 51 queries, each with network delay. Rewriting it as one query with a JOIN and GROUP BY returns the same page in a single round trip. ORM tools make this mistake easy, and most offer eager loading to avoid it.</p>')}
{K.lab('l-sarg', 'm', 'June orders, the sargable way', 'Show the <code>id</code> of every order placed in June 2025 using a range on <code>order_date</code>, not a function.',
"""SELECT id FROM orders WHERE order_date >= '2025-06-01' AND order_date < '2025-07-01';""", hint="order_date >= '2025-06-01' AND order_date < '2025-07-01'", why='ISO dates sort as text in date order, so a range works and an index on order_date can be searched.')}
{K.lab('l-keyset', 'm', 'The next page', 'Orders are shown 3 per page in id order. The last id on the current page was 104. Show the <code>id</code> and <code>status</code> of the next page using keyset paging.',
"""SELECT id, status FROM orders WHERE id > 104 ORDER BY id LIMIT 3;""", hint='WHERE id > 104 ORDER BY id LIMIT 3', why='The next page starts right after the last id seen.', ordered=True)}
{K.lab('l-nplus', 'h', 'Fix the N+1', 'Replace one query per customer with one query: show every customer’s <code>name</code> and number of orders as <code>orders</code>, including customers with none.',
"""SELECT c.name, COUNT(o.id) AS orders FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id;""", hint='LEFT JOIN orders and GROUP BY the customer.', why='One round trip replaces nine.')}
''', kw=['sargable', 'query tuning', 'keyset pagination', 'OFFSET', 'N+1 problem', 'SELECT star', 'rewrite'])
K.talk('tuning', '''Many slow queries are fixed with small rewrites. A condition the engine can answer through an index is called sargable. Wrapping the column in a
function, such as taking the first seven characters of a date, hides it from the index, while a plain date range lets the engine search. Name only the
columns you need. For paging, OFFSET still walks past every skipped row, so on deep pages remember the last id and ask for ids after it. And watch for
the N plus one problem, where an app runs one query per item in a loop instead of one join for all of them. Think of buying all your groceries in one trip
instead of one trip per item.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>The database decides how to run your query. EXPLAIN shows its plan, and you can help with indexes and simple conditions.</p>',
    '<p>Read plans for scans, searches and sorts. Know nested loop, hash and merge joins. Keep statistics fresh. Write sargable predicates and avoid N+1 query patterns.</p>',
    '<p>Optimizers enumerate join orders with dynamic programming (System R) or rule based search spaces (Volcano and Cascades, Graefe 1993 to 1995). Cardinality estimation errors grow with each join and are the main source of bad plans (Leis et al., "How Good Are Query Optimizers, Really", VLDB 2015).</p>',
    '<p>Research explores learned optimizers and learned cardinality estimators, adaptive query processing that changes plan mid flight, and worst case optimal join algorithms for many way joins.</p>')}
{deep('Why join order matters so much', '<p>Joining 3 tables of 1,000, 1,000,000 and 10 rows: starting with the 10 row table and reaching the others by index touches a few thousand rows. Starting with the million row table and nesting the others without indexes can touch billions. For n tables there are n! orders, so optimizers prune the search with dynamic programming and heuristics.</p>')}
''', kw=['join ordering', 'dynamic programming', 'Cascades', 'cardinality estimation', 'learned optimizer', 'adaptive query processing'])
K.talk('levels', '''Here is the ladder. For a beginner, the database decides how to run your query, and EXPLAIN shows the plan. At college level, read plans for scans and
sorts, know the three join algorithms, keep statistics fresh and write sargable conditions. At masters level, optimizers search join orders with dynamic
programming, and errors in row estimates grow with every join. At research level, people build optimizers that learn from past queries and adapt plans
while they run. Think of a sat nav that learns which roads are busy at which hour.''')

K.quiz('e', 'Which part of the engine chooses how to run a query?', ['The parser', 'The optimizer', 'The disk', 'The client'], 1, 'Planner.', 'The query optimizer picks the plan.')
K.quiz('e', 'In a SQLite plan, SCAN means', ['Jump through an index', 'Read every row', 'Sort', 'Join'], 1, 'Every row.', 'A full scan.')
K.quiz('e', 'EXPLAIN QUERY PLAN', ['Runs the query twice', 'Shows the plan without running it', 'Deletes the plan', 'Creates indexes'], 1, 'Shows.', 'It only describes the plan.')
K.quiz('e', 'USE TEMP B-TREE FOR ORDER BY means', ['An index sorted it', 'A temporary sort was needed', 'An error', 'No sorting'], 1, 'Temporary.', 'No index gave the order, so it sorts.')
K.quiz('m', 'A hash join suits', ['Tiny tables with indexes', 'Big unsorted inputs with equality conditions', 'Range conditions only', 'No joins'], 1, 'Hash.', 'Build a hash table of one input, probe with the other.')
K.quiz('m', 'Which join algorithm does SQLite use?', ['Hash join', 'Merge join', 'Nested loop', 'All three'], 2, 'Loops.', 'SQLite uses nested loops, with automatic indexes when useful.')
K.quiz('m', 'ANALYZE', ['Runs every query', 'Gathers statistics for the optimizer', 'Checks syntax', 'Backs up data'], 1, 'Statistics.', 'Fresh numbers give better estimates.')
K.quiz('m', "WHERE substr(order_date, 1, 7) = '2025-06' is", ['Sargable', 'Not sargable', 'Invalid', 'A join'], 1, 'Function on column.', 'Rewrite as a date range.')
K.quiz('m', 'Keyset paging uses', ['OFFSET', 'WHERE id > last_id ORDER BY id LIMIT n', 'RANDOM()', 'GROUP BY'], 1, 'Remember the last key.', 'It jumps straight to the next page.')
K.quiz('h', 'The N+1 problem is', ['A math error', 'One query per item instead of one query for all', 'A missing index', 'A NULL bug'], 1, 'Many round trips.', 'Replace the loop with one join.')
K.quiz('x', 'Which 1979 system introduced cost based join ordering?', ['Ingres', 'System R', 'Oracle 2', 'PostgreSQL'], 1, 'IBM.', 'Selinger et al., System R.')

K.calc('e', 'Outer table 1,000 rows, inner table 1,000 rows, no index. How many row pairs does a nested loop compare?', '1000000', 'N × M.',
       ['Each outer row scans the inner table.', 'That is 1,000 comparisons per outer row.', eq('1,000 × 1,000 = 1,000,000')], check=1000 * 1000)
K.calc('e', 'Same tables, with an index on the inner join column (about 10 steps per lookup). About how many steps?', '10000', 'N × log M.',
       ['Each outer row does one index lookup.', 'log₂ 1,000 ≈ 10.', eq('1,000 × 10 = 10,000')], check=10000)
K.calc('m', 'A page shows 20 rows. Page 500 with LIMIT 20 OFFSET n. What is n?', '9980', '(page − 1) × size.',
       ['Pages before page 500: 499.', 'Each page has 20 rows.', eq('499 × 20 = 9,980')], check=499 * 20)
K.calc('m', 'With OFFSET 9980 LIMIT 20, how many rows does the engine walk past before returning results?', '9980', 'It reads and discards them.',
       ['OFFSET does not jump.', 'It produces and throws away the skipped rows.', eq('9,980 rows wasted')], check=9980)
K.calc('m', 'A page lists 50 customers and runs one extra query per customer. How many queries in total?', '51', 'N + 1.',
       ['1 query for the list.', '50 queries, one per customer.', eq('1 + 50 = 51')], check=51)
K.calc('m', 'Each query costs 2 ms of network delay. How much delay does fixing the N+1 above save?', '100', 'Queries saved × delay.',
       ['Before: 51 queries. After: 1 query.', '50 queries saved.', eq('50 × 2 = 100 ms')], check=100)
st = value('shop', "SELECT stat FROM sqlite_stat1 WHERE idx = 'idx_status'", setup='CREATE INDEX idx_status ON orders(status); ANALYZE;')
K.calc('h', f'After ANALYZE, sqlite_stat1 says "{st}" for idx_status. The first number is the row count. What is the average number of rows per status, the second number?', st.split()[1], 'Rows ÷ distinct statuses, rounded up.',
       ['10 orders.', '4 distinct statuses: delivered, shipped, cancelled, pending.', eq(f'10 ÷ 4 = 2.5, stored as {st.split()[1]}')], check=int(st.split()[1]))
K.calc('h', 'How many possible join orders exist for 5 tables (left deep, any order)?', '120', 'n factorial.',
       ['Choose the first of 5, then 4, and so on.', 'Multiply.', eq('5! = 5 × 4 × 3 × 2 × 1 = 120')], check=120)

K.must('Optimizer', 'SQL says what, the optimizer decides how. EXPLAIN QUERY PLAN or EXPLAIN shows its choice.')
K.must('Plan words', 'SCAN reads all rows, SEARCH jumps by index, COVERING INDEX skips the table, TEMP B-TREE sorts.')
K.must('Joins', 'Nested loop wants an index on the inner column, hash join suits big equality joins, merge join suits sorted inputs.')
K.must('Statistics', 'Cost based optimizers need fresh statistics. Run ANALYZE after big changes.')
K.must('Rewrites', 'Sargable ranges instead of functions on columns, keyset instead of deep OFFSET, one join instead of N+1 queries.')

T = K.topic(
    slug='sql-plans', topic='sql-plans', step=(7, 'Performance and transactions', 'sql-perf', 'How indexes and query plans make queries fast, and how transactions keep data correct when many people work at once.', 'Advanced'),
    title='Query plans and tuning', short='Query plans', badge='7.2', minutes=40, added='2026-11-23',
    lead='Read what the optimizer plans to do with EXPLAIN, understand join algorithms and statistics, and rewrite slow queries so indexes can help.',
    desc='The query optimizer, EXPLAIN QUERY PLAN and EXPLAIN ANALYZE, SCAN, SEARCH, covering index and temp B-tree, nested loop, hash and merge joins, join order, ANALYZE and statistics, sargable conditions, keyset pagination, the N+1 problem.',
    summary='Reading query plans, join algorithms, statistics and rewriting slow queries.',
    keywords=['query plan', 'EXPLAIN', 'optimizer', 'hash join', 'ANALYZE', 'sargable', 'N+1'],
    recap='<p>The optimizer picks the plan, EXPLAIN shows it, statistics guide it, and sargable conditions let indexes do their job.</p>')
