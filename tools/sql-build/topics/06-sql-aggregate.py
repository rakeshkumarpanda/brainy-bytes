# Chapter 2.3: aggregates, GROUP BY, HAVING and the logical order of a query. Sources: sqlite.org lang_aggfunc.html
# (count, sum, total, avg, min, max, group_concat, string_agg since 3.44.0, DISTINCT in aggregates, FILTER clause),
# lang_select.html (aggregate without GROUP BY gives one row, bare columns, processing order), PostgreSQL SELECT docs.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('agg', 'Squeezing many rows into one answer', f'''
<p>"How many orders did we get?" "What is our average price?" These questions take many rows and squeeze them into one number. The functions that do it are called <b>aggregate functions</b>.</p>
{table(['Function', 'Gives', 'NULLs'], [
    ['<code>COUNT(*)</code>', 'number of rows', 'counted'],
    ['<code>COUNT(col)</code>', 'number of values that are not NULL', 'skipped'],
    ['<code>COUNT(DISTINCT col)</code>', 'number of different values', 'skipped'],
    ['<code>SUM(col)</code>', 'total', 'skipped, and SUM of no values is NULL'],
    ['<code>AVG(col)</code>', 'average (mean)', 'skipped'],
    ['<code>MIN(col)</code>, <code>MAX(col)</code>', 'smallest, biggest', 'skipped'],
    ['<code>group_concat(col, sep)</code>', 'all values joined into one text', 'skipped (string_agg in PostgreSQL and SQLite 3.44+)']])}
{K.sql('totals', """SELECT COUNT(*)              AS products,
       COUNT(DISTINCT category) AS categories,
       SUM(stock)            AS items_in_store,
       ROUND(AVG(price), 2)  AS average_price,
       MIN(price)            AS cheapest,
       MAX(price)            AS dearest
FROM products;""", title='The whole shop in one row', notes={1: 'With no GROUP BY, the whole table is one group, so exactly one row comes back.', 2: 'Each different category counted once.'})}
{note('An aggregate query with no GROUP BY always returns exactly one row, even when the table is empty. COUNT then gives 0 and SUM gives NULL.', 'exam')}
{K.lab('l-stats', 'e', 'Order statistics', 'Return one row with two columns: <code>orders</code>, the number of orders, and <code>first_day</code>, the earliest <code>order_date</code>.', 'SELECT COUNT(*) AS orders, MIN(order_date) AS first_day FROM orders;', hint='COUNT(*) and MIN(order_date).', why='MIN works on text too, and ISO dates compare correctly.')}
''', kw=['aggregate', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'COUNT DISTINCT', 'group_concat', 'string_agg'])
K.talk('agg', '''Aggregate functions take many rows and give back one answer. COUNT star counts rows, COUNT of a column counts known values, and COUNT
DISTINCT counts different values. SUM adds, AVG finds the mean, and MIN and MAX find the smallest and biggest. group_concat joins many values
into one piece of text. All of them except COUNT star skip NULLs. When a query has an aggregate but no GROUP BY, the whole table becomes one
big group, so exactly one row comes back, even from an empty table. In that case COUNT gives zero and SUM gives NULL. Think of a teacher
reading out only the class total and the class average, instead of every single mark.''')

K.lesson('groupby', 'GROUP BY: one answer per group', f'''
<p>A shop owner wants "how many products in each category", not one number for the whole shop. <code>GROUP BY</code> splits the rows into groups that share a value, then runs the aggregate once per group. One group becomes one result row.</p>
{pk('sqgroup')}
{K.sql('grp', """SELECT category,
       COUNT(*)   AS products,
       SUM(stock) AS items,
       MAX(price) AS dearest
FROM products
GROUP BY category
ORDER BY products DESC, category;""", title='Products per category', notes={6: 'One group for each different category.', 1: 'category can be shown because it is the grouping column, the same for every row in the group.'})}
{steps('The golden rule of GROUP BY', [
    'After grouping, each result row stands for a whole group of rows.',
    'A column in the SELECT list must be either in GROUP BY or inside an aggregate.',
    'Otherwise the engine does not know which row’s value to show. PostgreSQL, SQL Server and MySQL (by default) refuse such a query.',
    eq('SQLite allows these bare columns and takes the value from some row of the group. Avoid relying on it')])}
{K.sql('multi', """SELECT o.customer_id, o.status, COUNT(*) AS orders
FROM orders AS o
GROUP BY o.customer_id, o.status
ORDER BY o.customer_id, o.status;""", title='Group by two columns', notes={3: 'A group is now each different pair of customer and status.'})}
{K.lab('l-percat', 'm', 'Stock per category', 'Show each <code>category</code> with the column <code>total_stock</code>, the sum of stock in that category.', 'SELECT category, SUM(stock) AS total_stock FROM products GROUP BY category;', hint='GROUP BY category and SUM(stock).', why='GROUP BY makes one row per category and SUM adds the stock inside each.')}
''', kw=['GROUP BY', 'group', 'bare column', 'grouping columns', 'one row per group'])
K.talk('groupby', '''GROUP BY is how you get one answer per group instead of one for the whole table. The engine puts rows that share a value into the same
bucket, and then runs the aggregate once in each bucket, so every bucket becomes one row of the result. Watch the animation drop each product
into its category bucket. There is one golden rule. Every column you show must either be a grouping column or sit inside an aggregate, because
a group has many rows and the engine must know which value to show. Most engines refuse to break this rule, while SQLite allows it and picks
a value from some row. Think of sorting laundry into piles by colour, then counting each pile.''')

K.lesson('having', 'HAVING filters groups, WHERE filters rows', f'''
<p>"Categories with at least 3 products" is a test on a <b>group</b>, not on a single row. <code>WHERE</code> cannot do it, because WHERE runs before the groups exist. <code>HAVING</code> runs after grouping, so it can use aggregates.</p>
{K.sql('having', """SELECT category, COUNT(*) AS products
FROM products
WHERE stock > 0
GROUP BY category
HAVING COUNT(*) >= 2;""", title='WHERE first, HAVING later', notes={3: 'Rows first: products that are sold out never join a group.', 5: 'Groups next: only categories with 2 or more in stock products survive.'})}
{K.sql('bad', """SELECT category, COUNT(*)
FROM products
WHERE COUNT(*) >= 2
GROUP BY category;""", title='This fails, try it', err=True, notes={3: 'WHERE cannot use an aggregate, because the groups do not exist yet.'})}
{table(['', 'WHERE', 'HAVING'], [
    ['Filters', 'single rows', 'whole groups'],
    ['Runs', 'before GROUP BY', 'after GROUP BY'],
    ['Can use aggregates', 'no', 'yes'],
    ['Example', '<code>WHERE stock &gt; 0</code>', '<code>HAVING SUM(stock) &gt; 100</code>']])}
{fxs(fx('Grouped query', '<code>SELECT g, agg(x) FROM t WHERE row_test GROUP BY g HAVING group_test ORDER BY ...;</code>', 'Clauses must be written in this order.', key=True),
     fx('Conditional count', '<code>COUNT(*) FILTER (WHERE cond)</code> or <code>SUM(CASE WHEN cond THEN 1 ELSE 0 END)</code>', 'Counts only some rows of each group. FILTER works in PostgreSQL and SQLite 3.30+.'))}
{K.lab('l-busy', 'm', 'Loyal customers', 'Show the <code>customer_id</code> and the number of orders (<code>orders</code>) for every customer with 2 or more orders.', 'SELECT customer_id, COUNT(*) AS orders FROM orders GROUP BY customer_id HAVING COUNT(*) >= 2;', hint='GROUP BY customer_id, then HAVING COUNT(*) &gt;= 2.', why='The test is on the number of orders in a group, so it belongs in HAVING.')}
''', kw=['HAVING', 'WHERE vs HAVING', 'filter groups', 'FILTER clause', 'conditional aggregation'])
K.talk('having', '''WHERE and HAVING both filter, but they filter different things at different times. WHERE tests single rows before any groups are made,
so it can never use COUNT or SUM. HAVING tests whole groups after they are made, so it can use aggregates freely. In the example, WHERE first
throws away sold out products, then the groups form, then HAVING keeps only categories with at least two products left. Try the second block,
it fails because WHERE cannot use COUNT. A neat trick is the FILTER clause or a SUM of CASE, which counts only some rows inside each group.
Think of a school picking only students who passed, then keeping only classes with ten or more of them.''')

K.lesson('order', 'The order SQL really runs in', f'''
<p>You write a query starting with SELECT, but the engine logically starts with FROM. Knowing the real order explains most beginner errors.</p>
{pk('sqpipe')}
{table(['Step', 'Clause', 'What it does', 'So you can'], [
    ['1', 'FROM (and JOIN)', 'picks and combines tables', 'refer to their columns'],
    ['2', 'WHERE', 'keeps rows', 'not use aggregates or SELECT aliases yet'],
    ['3', 'GROUP BY', 'makes groups', 'only group columns survive as plain values'],
    ['4', 'HAVING', 'keeps groups', 'use aggregates'],
    ['5', 'SELECT', 'works out the result columns and aliases', 'name things with AS'],
    ['6', 'DISTINCT', 'removes duplicate rows', ''],
    ['7', 'ORDER BY', 'sorts', 'use aliases from SELECT'],
    ['8', 'LIMIT / OFFSET', 'cuts the list', '']])}
{note('This is the logical order, which defines what a query means. The engine may physically do things in another order, for example use an index to avoid sorting, as long as the answer is the same.', 'tip')}
{scene('the monthly sales report', '<p>A manager asks for "the top 3 cities by revenue last month, only cities with more than 10 orders". Read it in the logical order: FROM orders joined to customers, WHERE the date is in last month, GROUP BY city, HAVING COUNT(*) &gt; 10, SELECT city and SUM of the amounts as revenue, ORDER BY revenue DESC, LIMIT 3. Each phrase of the request lands in exactly one clause.</p>')}
{K.lab('l-top', 'h', 'Busiest status', 'Show the <code>status</code> and number of orders (<code>n</code>) for the single most common order status.', 'SELECT status, COUNT(*) AS n FROM orders GROUP BY status ORDER BY n DESC LIMIT 1;', hint='Group by status, order by the count descending, keep 1.', why='ORDER BY can use the alias n because it runs after SELECT.')}
''', kw=['logical query processing', 'order of execution', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'SELECT', 'ORDER BY', 'LIMIT'])
K.talk('order', '''You write SELECT first, but the engine thinks about FROM first. The logical order is FROM, then WHERE, then GROUP BY, then HAVING, then
SELECT, then DISTINCT, then ORDER BY, and finally LIMIT. Knowing this order explains the classic errors. WHERE cannot see a column alias,
because the select list has not been worked out yet. ORDER BY can use the alias, because it comes after. HAVING can use aggregates, because
the groups already exist. In the animation, change the parts and watch the table shrink at each stage. Real engines may do the work in a
cleverer physical order, but the answer must match this logical order. Think of making tea, boil, add leaves, strain, then pour.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>GROUP BY sorts things into piles, the aggregate counts or adds each pile, and HAVING throws away piles you do not want.</p>',
    '<p>Grouping is done with a sort or a hash table. Engines also support ROLLUP, CUBE and GROUPING SETS (PostgreSQL, SQL Server, Oracle, MySQL has WITH ROLLUP) to get subtotals and a grand total in one query.</p>',
    '<p>Aggregates can be split for parallel work: SUM and COUNT combine easily, AVG is computed as SUM and COUNT combined at the end. MEDIAN cannot be combined so simply, which is why exact medians on huge data are expensive.</p>',
    '<p>Analytics engines use approximate aggregates such as HyperLogLog for COUNT DISTINCT on billions of rows, trading a small, known error for huge speed. Column stores keep each column separately, so SUM(price) reads only the price column.</p>')}
{deep('ROLLUP in action', '<p>In PostgreSQL, <code>SELECT category, status, SUM(qty) FROM sales GROUP BY ROLLUP (category, status)</code> returns one row per category and status, one subtotal row per category (status shown as NULL) and one grand total row. SQLite has no ROLLUP, but a UNION ALL of three grouped queries gives the same result.</p>')}
''', kw=['ROLLUP', 'CUBE', 'GROUPING SETS', 'hash aggregation', 'HyperLogLog', 'column store'])
K.talk('levels', '''For a child, GROUP BY makes piles, the aggregate counts each pile, and HAVING throws away the piles you do not want. At college level,
engines group using sorting or hash tables, and features like ROLLUP add subtotals and a grand total in one query. At masters level, sums
and counts can be split across many workers and joined later, and an average is just a sum and a count combined at the end, but a median
cannot be split so easily. At research level, analytics systems use clever approximate counting to handle billions of rows quickly. Think
of a census, where every district counts its people and the country simply adds the district totals.''')

K.quiz('e', 'Which function counts rows?', ['SUM(*)', 'COUNT(*)', 'TOTAL(*)', 'ROWS()'], 1, 'Count.', 'COUNT(*) counts rows.')
K.quiz('e', 'What does GROUP BY category do?', ['Sorts by category', 'Makes one group per different category', 'Removes categories', 'Counts categories'], 1, 'Buckets.', 'Rows with the same category form one group.')
K.quiz('e', 'Which clause filters groups?', ['WHERE', 'HAVING', 'ORDER BY', 'LIMIT'], 1, 'After grouping.', 'HAVING tests groups.')
K.quiz('e', 'An aggregate query with no GROUP BY returns how many rows?', ['One', 'None', 'One per row', 'It fails'], 0, 'Whole table is one group.', 'Exactly one row.')
K.quiz('m', 'Why does WHERE COUNT(*) &gt; 2 fail?', ['COUNT needs a column', 'WHERE runs before groups exist', 'Wrong spelling', 'It does not fail'], 1, 'Order.', 'Aggregates belong in HAVING.')
K.quiz('m', 'COUNT(DISTINCT city) counts', ['All rows', 'Different known cities', 'Cities including NULL', 'Rows with NULL city'], 1, 'Distinct, no NULL.', 'Different values, NULL skipped.')
K.quiz('m', 'Which runs first logically?', ['SELECT', 'WHERE', 'ORDER BY', 'HAVING'], 1, 'FROM, WHERE, ...', 'WHERE comes right after FROM.')
K.quiz('m', 'Can ORDER BY use an alias defined in SELECT?', ['Yes', 'No', 'Only in SQLite', 'Only with quotes'], 0, 'Runs after SELECT.', 'ORDER BY sees the result columns.')
K.quiz('h', 'SELECT category, name, COUNT(*) FROM products GROUP BY category is a problem because', ['name is not grouped or aggregated', 'COUNT needs a column', 'category is a keyword', 'It has no WHERE'], 0, 'Golden rule.', 'Which name of the group should be shown is undefined.')
K.quiz('h', 'SUM over zero rows returns', ['0', 'NULL', 'An error', '1'], 1, 'Nothing to add.', 'SUM of no values is NULL. COUNT gives 0.')
K.quiz('x', 'Why is an exact MEDIAN harder to parallelise than AVG?', ['MEDIAN is not standard', 'AVG combines from partial sums and counts, a median needs the whole order', 'MEDIAN skips NULLs', 'AVG is approximate'], 1, 'Combinable.', 'Partial results for AVG merge easily, a median needs all values ordered.')

K.calc('e', 'How many products are in the Electronics category?', str(value('shop', "SELECT count(*) FROM products WHERE category = 'Electronics'")), 'Count the group.',
       ['Electronics: Headphones, Phone charger, Desk lamp.', 'Count them.', eq('3')], check=value('shop', "SELECT count(*) FROM products WHERE category = 'Electronics'"))
K.calc('e', 'What is SUM(stock) over all products?', str(value('shop', 'SELECT sum(stock) FROM products')), 'Add the stock column.',
       ['40 + 150 + 25 + 0 + 12 = 227.', '30 + 60 + 8 + 0 + 70 = 168.', eq(f"227 + 168 = {value('shop', 'SELECT sum(stock) FROM products')}")], check=value('shop', 'SELECT sum(stock) FROM products'))
K.calc('m', 'What is the average price of Stationery products, to 2 decimals?', f"{value('shop', "SELECT round(avg(price), 2) FROM products WHERE category = 'Stationery'"):.2f}", 'Three products.',
       ['Prices: 120, 60, 95.', 'Sum = 275.', eq('275 / 3 ≈ 91.67')], check=value('shop', "SELECT round(avg(price), 2) FROM products WHERE category = 'Stationery'"), tol=0.005)
K.calc('m', 'How many rows does SELECT category FROM products GROUP BY category HAVING COUNT(*) &gt;= 3 return?', str(value('shop', 'SELECT count(*) FROM (SELECT category FROM products GROUP BY category HAVING count(*) >= 3)')), 'Count per category first.',
       ['Stationery 3, Kitchen 2, Electronics 3, Sports 2.', 'Keep groups with 3 or more.', eq('2 rows')], check=value('shop', 'SELECT count(*) FROM (SELECT category FROM products GROUP BY category HAVING count(*) >= 3)'))
K.calc('m', 'How many different customers have placed an order?', str(value('shop', 'SELECT count(DISTINCT customer_id) FROM orders')), 'COUNT(DISTINCT customer_id).',
       ['Customer ids in orders: 1, 2, 1, 3, 5, 7, 2, 3, 5, 1.', 'Different ones: 1, 2, 3, 5, 7.', eq('5 customers')], check=value('shop', 'SELECT count(DISTINCT customer_id) FROM orders'))
K.calc('m', 'Total quantity of items in order 101?', str(value('shop', 'SELECT sum(qty) FROM order_items WHERE order_id = 101')), 'SUM(qty) for that order.',
       ['Order 101 has 2 pencil boxes and 5 notebooks.', 'Add the quantities.', eq('2 + 5 = 7')], check=value('shop', 'SELECT sum(qty) FROM order_items WHERE order_id = 101'))
K.calc('h', 'Using WHERE stock &gt; 0, GROUP BY category, HAVING COUNT(*) &gt;= 2: how many categories remain?', str(value('shop', 'SELECT count(*) FROM (SELECT category FROM products WHERE stock > 0 GROUP BY category HAVING count(*) >= 2)')), 'Remove sold out rows first.',
       ['Sold out: Lunch box (Kitchen) and Desk lamp (Electronics).', 'In stock counts: Stationery 3, Kitchen 1, Electronics 2, Sports 2.', eq('Kitchen drops out: 3 categories')], check=value('shop', 'SELECT count(*) FROM (SELECT category FROM products WHERE stock > 0 GROUP BY category HAVING count(*) >= 2)'))
K.calc('h', 'What is SELECT SUM(price) FROM products WHERE price &gt; 5000? Answer 0 if you think 0, or type -1 for NULL.', '-1', 'No rows match.',
       ['No product costs more than 5000.', 'SUM of no values is NULL, not 0.', eq('NULL, typed -1')], check=-1 if value('shop', 'SELECT sum(price) FROM products WHERE price > 5000') is None else 0)

K.must('Aggregates', 'COUNT(*), COUNT(col), COUNT(DISTINCT col), SUM, AVG, MIN, MAX. All but COUNT(*) skip NULLs.')
K.must('No GROUP BY', 'An aggregate query without GROUP BY returns exactly one row. COUNT of nothing is 0, SUM of nothing is NULL.')
K.must('GROUP BY', 'One result row per group. Show only grouping columns or aggregates.')
K.must('WHERE vs HAVING', 'WHERE filters rows before grouping, HAVING filters groups after, and only HAVING can use aggregates.')
K.must('Logical order', 'FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT.')

T = K.topic(
    slug='sql-aggregate', topic='sql-aggregate', step=(2, 'Shaping results', 'sql-shape', 'Functions and CASE, the truth about NULL, and squeezing many rows into answers with GROUP BY.', 'Beginner'),
    title='Aggregates, GROUP BY and HAVING', short='GROUP BY and HAVING', badge='2.3', minutes=45, added='2026-11-23',
    lead='Count, add and average many rows at once, split them into groups, keep only the groups you want, and learn the real order in which SQL runs a query.',
    desc='COUNT, SUM, AVG, MIN, MAX, COUNT DISTINCT and group_concat, aggregates without GROUP BY, GROUP BY with one and two columns, the bare column rule, HAVING versus WHERE, FILTER, the logical processing order, ROLLUP.',
    summary='Aggregate functions, GROUP BY, HAVING versus WHERE, and the logical order of a query.',
    keywords=['aggregate', 'COUNT', 'SUM', 'AVG', 'GROUP BY', 'HAVING', 'order of execution'],
    recap='<p>Aggregates squeeze rows into one value, GROUP BY gives one value per group, HAVING filters the groups, and the logical order FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT explains every rule.</p>')
