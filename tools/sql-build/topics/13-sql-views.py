# Chapter 4.3: views and common table expressions: CREATE VIEW, using and dropping views, read only views in SQLite,
# materialized views, WITH clauses with several steps, CTE versus subquery versus view versus temporary table.
# Sources: sqlite.org lang_createview.html (views are read only unless INSTEAD OF triggers exist), lang_with.html
# (ordinary CTEs, MATERIALIZED and NOT MATERIALIZED hints since 3.35.0), lang_createtable.html (TEMP tables),
# postgresql.org sql-createview.html (simple views are automatically updatable), sql-creatematerializedview.html.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

SPEND = """SELECT o.customer_id, SUM(oi.qty * p.price) AS total
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status <> 'cancelled'
GROUP BY o.customer_id"""

K.lesson('views', 'Views: a saved query with a name', f'''
<p>Some queries get written again and again, such as "money spent by each customer". A <b>view</b> stores that query under a name. After that you can SELECT from the view as if it were a table, and the engine runs the saved query each time, so the answer is always up to date.</p>
{fxs(fx('Make a view', '<code>CREATE VIEW name AS SELECT ... ;</code>', 'Only the query is stored, not the rows.', key=True),
     fx('Remove a view', '<code>DROP VIEW IF EXISTS name;</code>', 'The underlying tables are untouched.'))}
{K.sql('view', f"""CREATE VIEW customer_spend AS
{SPEND};

SELECT c.name, s.total
FROM customer_spend s JOIN customers c ON c.id = s.customer_id
ORDER BY s.total DESC;""", title='Save the spending query once, use it like a table', notes={1: 'The view stores this SELECT, not its result.', 10: 'Now the view joins like any table.'})}
{K.sql('viewlive', f"""CREATE VIEW low_stock AS
SELECT name, stock FROM products WHERE stock < 20;

SELECT * FROM low_stock;
UPDATE products SET stock = 5 WHERE name = 'Notebook';
SELECT * FROM low_stock;""", title='A view always shows the current data', notes={4: 'Lunch box, Desk lamp, Headphones and Football.', 6: 'Notebook now has stock 5, and the view includes it straight away.'})}
{table(['Why people use views', 'Example'], [
    ['Hide a long query behind a short name', 'SELECT * FROM customer_spend'],
    ['Give each team only the columns it needs', 'a view of employees without the salary column'],
    ['Keep one definition of a business rule', 'what counts as an active customer, written once'],
    ['Keep old programs working after a table changes', 'a view with the old table name and old column names']])}
{note('In SQLite a view is read only: you cannot INSERT, UPDATE or DELETE through it unless you add INSTEAD OF triggers (chapter 8.1). PostgreSQL and MySQL allow changes through simple views on one table.', 'tip')}
{K.lab('l-view', 'e', 'A view of cheap products', 'Create a view <code>cheap</code> holding the <code>name</code> and <code>price</code> of products under 200. Then select every row from the view.',
"""CREATE VIEW cheap AS SELECT name, price FROM products WHERE price < 200;
SELECT * FROM cheap;""", hint='CREATE VIEW cheap AS SELECT ..., then SELECT * FROM cheap.', why='The view runs its saved query when you select from it.')}
''', kw=['view', 'CREATE VIEW', 'DROP VIEW', 'saved query', 'virtual table', 'read only view', 'updatable view'])
K.talk('views', '''Some questions get asked again and again, like how much money each customer has spent. A view stores that query under a name, so afterwards you
can select from it as if it were a table. Only the query is saved, not the rows, so each time you use the view the engine runs the query again on
the current data. Change a product's stock and the low stock view shows the change at once. Teams use views to hide long queries, to show each
group only the columns it may see, and to keep one agreed definition of a business rule. In SQLite a view is read only. Think of a saved search in
your email app, which shows the latest matching messages each time you open it.''')

K.lesson('cte', 'WITH: common table expressions', f'''
<p>A <b>CTE</b> (common table expression) is a view that lives for one statement only. You write <code>WITH name AS (query)</code> before the main SELECT, and the main query, or later CTEs, can read it by name. Long queries become a list of small named steps you can read top to bottom.</p>
{pk('sqcte')}
{K.sql('cte', f"""WITH spend AS (
  {SPEND.replace(chr(10), chr(10) + '  ')}
),
big AS (
  SELECT customer_id, total FROM spend WHERE total >= 2000
)
SELECT c.name, b.total
FROM big b JOIN customers c ON c.id = b.customer_id
ORDER BY b.total DESC;""", title='Two named steps, then the answer', notes={1: 'Step 1: total per customer.', 10: 'Step 2 reads step 1 by its name.', 12: 'The final query reads step 2.'})}
{K.sql('cteavg', """WITH cat AS (
  SELECT category, AVG(price) AS avg_price
  FROM products GROUP BY category
)
SELECT p.name, p.category, p.price, ROUND(cat.avg_price) AS category_avg
FROM products p JOIN cat ON cat.category = p.category
WHERE p.price > cat.avg_price
ORDER BY p.category;""", title='Products priced above their own category’s average', notes={2: 'One average per category.', 7: 'Each product is compared with the average of its own category.'})}
{steps('Turning a nested subquery into a CTE', [
    'Find the innermost subquery in FROM.',
    'Move it to the top: <code>WITH step1 AS ( that subquery )</code>.',
    'Replace it in the main query with the name step1.',
    'Repeat for the next level. The query now reads top to bottom instead of inside out.'])}
{K.lab('l-cte', 'm', 'Busy customers by name', 'Using a CTE named <code>n</code> that counts orders per <code>customer_id</code>, show the <code>name</code> and order count <code>orders</code> of customers with 2 or more orders.',
"""WITH n AS (SELECT customer_id, COUNT(*) AS orders FROM orders GROUP BY customer_id)
SELECT c.name, n.orders FROM n JOIN customers c ON c.id = n.customer_id WHERE n.orders >= 2;""", hint='WITH n AS (SELECT customer_id, COUNT(*) AS orders FROM orders GROUP BY customer_id) then join customers.', why='The CTE does the counting, the main query adds names and filters.')}
''', kw=['CTE', 'WITH', 'common table expression', 'named step', 'readability', 'nested subquery'])
K.talk('cte', '''A common table expression, or CTE, is like a view that lives for just one statement. You write WITH, a name, and a query in brackets, before the
main SELECT. The main query, and any later CTE, can read it by that name. This turns a long, nested query into a short list of named steps that you
read from top to bottom. In the animation, the first step adds up spending per customer, the second keeps the big spenders, and the last step adds
their names. Change the spending limit and watch each step work again. Think of a recipe that says first boil the rice, then fry the onions, then
mix them, instead of one long sentence.''')

K.lesson('compare', 'CTE, subquery, view or temporary table', f'''
<p>All four give a name or a place to an intermediate result. They differ in how long they live and whether the rows are stored.</p>
{table(['Tool', 'Lives for', 'Stores rows', 'Use it when'], [
    ['Subquery', 'one spot in one query', 'no', 'a small inner step used once'],
    ['CTE (WITH)', 'one statement', 'usually no', 'a long query reads better as named steps'],
    ['View', 'until dropped', 'no', 'many queries or people need the same logic'],
    ['Temporary table', 'until the connection closes', 'yes', 'a big result is reused by several statements'],
    ['Materialized view', 'until dropped, refreshed on demand', 'yes', 'a slow report that may be a little out of date']])}
{K.sql('temp', """CREATE TEMP TABLE june AS
SELECT * FROM orders WHERE order_date LIKE '2025-06%';

SELECT status, COUNT(*) AS n FROM june GROUP BY status;
SELECT COUNT(DISTINCT customer_id) AS buyers FROM june;""", title='A temporary table reused by two queries', notes={1: 'The rows are copied once into a table that disappears when the connection closes.', 4: 'Both queries read the stored copy.'})}
<p>A <b>materialized view</b> stores the result of its query like a table. Reading it is fast, but it is only as fresh as its last refresh. PostgreSQL writes <code>CREATE MATERIALIZED VIEW</code> and <code>REFRESH MATERIALIZED VIEW</code>, Oracle has them too, SQL Server uses indexed views. SQLite has none, a table filled by INSERT ... SELECT plays the same part.</p>
{scene('the morning sales dashboard', '<p>A retail chain shows managers yesterday’s sales by store on a dashboard. The query scans millions of rows and takes a minute. The team stores it as a materialized view and refreshes it at 6 every morning. Opening the dashboard now takes a fraction of a second, and nobody minds that it ignores sales from the last few hours.</p>')}
{note('SQLite and PostgreSQL 12+ accept <code>WITH x AS MATERIALIZED (...)</code> or <code>NOT MATERIALIZED</code> to ask the planner to compute a CTE once or to fold it into the main query. Without the hint the planner decides.', 'tip')}
{K.lab('l-temp', 'm', 'A temporary list of big orders', 'Create a temporary table <code>big_lines</code> with every row of <code>order_items</code> whose <code>qty</code> is at least 3. Then show how many rows it has, as <code>n</code>.',
"""CREATE TEMP TABLE big_lines AS SELECT * FROM order_items WHERE qty >= 3;
SELECT COUNT(*) AS n FROM big_lines;""", hint='CREATE TEMP TABLE big_lines AS SELECT ... WHERE qty >= 3', why='The temporary table stores the copied rows, and COUNT(*) counts them.')}
''', kw=['temporary table', 'TEMP TABLE', 'materialized view', 'REFRESH', 'CTE vs view', 'MATERIALIZED hint'])
K.talk('compare', '''Subqueries, CTEs, views and temporary tables all give a name or a home to an in between result, and they differ in how long they live. A
subquery lives in one spot of one query. A CTE lives for one statement. A view lives until you drop it, but stores only the query. A temporary table
really stores rows, and disappears when your connection closes, which is useful when several statements reuse the same big result. A materialized
view stores the result too, and is refreshed when you ask, which makes slow reports fast at the cost of being a little out of date. Think of the
difference between a sticky note, a page in a notebook, and a printed report on the notice board.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A view is a saved question with a name. A CTE is a named step inside one big question.</p>',
    '<p>Views give logical data independence: programs read the view, and the tables behind it can change. CTEs make long queries readable and let one step be reused several times in the same statement.</p>',
    '<p>The planner usually inlines views and CTEs into the main query, as if you had typed the subquery. Updatable views need a clear mapping from each view row to one base row. CTEs may be computed once and reused when that is cheaper.</p>',
    '<p>Keeping materialized views fresh without recomputing them from scratch is incremental view maintenance, a long running research area. Systems such as Materialize and features like Oracle fast refresh update only the rows affected by each change.</p>')}
{deep('Security through views', '<p>In server databases you can GRANT SELECT on a view without granting it on the table behind it. An analyst can then read <code>employees_public</code>, which leaves out salary and phone number, but cannot read the full employees table. Chapter 8.2 covers GRANT and row level security.</p>')}
''', kw=['logical data independence', 'view inlining', 'incremental view maintenance', 'GRANT on view', 'materialize'])
K.talk('levels', '''Time for the ladder. For a beginner, a view is a saved question and a CTE is a named step in one big question. At college level, views give data
independence, so programs read the view while the tables behind it can change. At masters level, the planner usually folds views and CTEs into the
main query as if you had typed the subquery yourself. At research level, people study how to keep materialized views fresh by updating only the rows
that changed, called incremental view maintenance. Think of a newspaper that prints a corrections box instead of reprinting the whole paper.''')

K.quiz('e', 'A view stores', ['A copy of the rows', 'A saved query', 'An index', 'A backup'], 1, 'Only the query.', 'The rows are computed when you read it.')
K.quiz('e', 'A CTE starts with the word', ['VIEW', 'WITH', 'TEMP', 'USING'], 1, 'With.', 'WITH name AS (query).')
K.quiz('e', 'After a base table changes, a normal view shows', ['The old data', 'The current data', 'An error', 'Nothing'], 1, 'Runs again.', 'The saved query runs on current data.')
K.quiz('e', 'How long does a CTE live?', ['Forever', 'One statement', 'One day', 'Until DROP'], 1, 'One statement.', 'It vanishes when the statement ends.')
K.quiz('m', 'Which really stores rows?', ['View', 'CTE', 'Temporary table', 'Subquery'], 2, 'A table.', 'A temporary table stores rows until the connection closes.')
K.quiz('m', 'Can a later CTE read an earlier one in the same WITH?', ['No', 'Yes', 'Only in PostgreSQL', 'Only with RECURSIVE'], 1, 'Chain.', 'Each CTE can use those defined before it.')
K.quiz('m', 'In SQLite, UPDATE on a view without INSTEAD OF triggers', ['Works', 'Fails, views are read only', 'Updates the view only', 'Drops the view'], 1, 'Read only.', 'SQLite views are read only.')
K.quiz('m', 'A materialized view is fresh', ['Always', 'As of its last refresh', 'Never', 'Only on Mondays'], 1, 'Refresh.', 'It stores a result that must be refreshed.')
K.quiz('m', 'Which gives a team access to some columns only?', ['A view of those columns', 'A CTE', 'A temporary table', 'An index'], 0, 'Lasting and shareable.', 'Grant access on a view that lists only those columns.')
K.quiz('h', 'What does NOT MATERIALIZED ask the planner to do with a CTE?', ['Store it on disk', 'Fold it into the main query', 'Drop it', 'Refresh it'], 1, 'Inline.', 'It asks for the CTE to be inlined.')
K.quiz('x', 'Updating a materialized view by touching only changed rows is called', ['Vacuum', 'Incremental view maintenance', 'Normalization', 'Sharding'], 1, 'Incremental.', 'Incremental view maintenance avoids a full recompute.')

spend = SPEND.replace('\n', ' ')
nbig = value('shop', f'SELECT count(*) FROM ({spend}) WHERE total >= 2000')
top = value('shop', f'SELECT max(total) FROM ({spend})')
asha = value('shop', f'SELECT total FROM ({spend}) WHERE customer_id = 1')
K.calc('e', 'How many customers have spent at least 2000 (cancelled orders left out)?', str(nbig), 'Read the spend step.',
       ['Work out the total per customer.', 'Keep totals of 2000 or more.', eq(f'{nbig} customers')], check=nbig)
K.calc('e', 'What is Asha’s total spend (orders 101, 103, 110)?', str(asha), 'qty × price for each line.',
       ['101: 2 × 120 + 5 × 60 = 540.', '103: 1 × 250 + 3 × 180 = 790. 110: 1 × 850 = 850.', eq(f'540 + 790 + 850 = {asha}')], check=asha)
K.calc('m', 'What is the largest total in customer_spend?', str(top), 'The top row.',
       ['Compute every customer total.', 'Take the biggest.', eq(f'{top}')], check=top)
nlow = value('shop', 'SELECT count(*) FROM products WHERE stock < 20')
nlow2 = value('shop', 'SELECT count(*) FROM products WHERE stock < 20', setup="UPDATE products SET stock = 5 WHERE name = 'Notebook';")
K.calc('m', 'The view low_stock shows products with stock under 20. How many rows does it show before and after Notebook drops to 5? Give the after count.', str(nlow2), 'The view reruns.',
       [f'Before: {nlow} rows.', 'Notebook now has stock 5, under 20.', eq(f'{nlow} + 1 = {nlow2}')], check=nlow2)
nabove = value('shop', 'WITH cat AS (SELECT category, AVG(price) AS a FROM products GROUP BY category) SELECT count(*) FROM products p JOIN cat ON cat.category = p.category WHERE p.price > cat.a')
K.calc('m', 'How many products cost more than the average of their own category?', str(nabove), 'Compare each with its category.',
       ['Stationery average 91.67: Pencil box, Geometry set. Kitchen 324.5: Lunch box.', 'Electronics 1149.33: Headphones, Desk lamp. Sports 515: Football.', eq(f'{nabove} products')], check=nabove)
june = value('shop', "SELECT COUNT(DISTINCT customer_id) FROM orders WHERE order_date LIKE '2025-06%'")
K.calc('m', 'How many different customers ordered in June 2025?', str(june), 'Distinct customer ids.',
       ['June orders are 101 to 108.', 'Their customers: 1, 2, 3, 5, 7.', eq(f'{june} customers')], check=june)
big3 = value('shop', 'SELECT count(*) FROM order_items WHERE qty >= 3')
K.calc('h', 'How many order lines have qty of at least 3?', str(big3), 'Scan the qty column.',
       ['Lines with qty 5, 3, 10, 4 and 3.', 'Count them.', eq(f'{big3} lines')], check=big3)
K.calc('h', 'A report reads a materialized view refreshed at 06:00. A sale happens at 09:30. At 10:00, how many hours of sales is the view missing?', '4', 'Since the refresh.',
       ['The view holds data up to 06:00.', 'From 06:00 to 10:00 is 4 hours.', eq('4 hours')], check=4)

K.must('View', 'CREATE VIEW stores a query under a name. It shows current data each time. Read only in SQLite.')
K.must('CTE', 'WITH name AS (query) names a step for one statement. Later steps and the main query can read it.')
K.must('Temporary table', 'CREATE TEMP TABLE stores rows until the connection closes, good for reuse.')
K.must('Materialized view', 'Stores the result, fast to read, as fresh as its last REFRESH. PostgreSQL, Oracle, SQL Server indexed views.')
K.must('Choosing', 'Subquery for once, CTE for readable steps, view for shared logic, temp table or materialized view for reused heavy results.')

T = K.topic(
    slug='sql-views', topic='sql-views', step=(4, 'Building and changing data', 'sql-make', 'Create your own tables with types and rules, change rows safely, and name steps with views and CTEs.', 'Intermediate'),
    title='Views and CTEs: naming your queries', short='Views and CTEs', badge='4.3', minutes=35, added='2026-11-23',
    lead='Save a query as a view, break a long query into named WITH steps, and choose between subqueries, CTEs, views, temporary tables and materialized views.',
    desc='CREATE VIEW and DROP VIEW, live views, read only views in SQLite, WITH and several CTEs, rewriting nested subqueries, temporary tables, materialized views and refresh, MATERIALIZED hints.',
    summary='Views, CTEs, temporary tables and materialized views.',
    keywords=['view', 'CTE', 'WITH', 'temporary table', 'materialized view'],
    recap='<p>A view is a saved query, a CTE is a named step for one statement, a temporary table stores rows for one connection, and a materialized view stores a result until refreshed.</p>')
