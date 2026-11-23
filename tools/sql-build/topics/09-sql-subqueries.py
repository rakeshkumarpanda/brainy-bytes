# Chapter 3.3: subqueries: scalar, IN and NOT IN, EXISTS and NOT EXISTS, correlated subqueries, derived tables in
# FROM, subqueries in SELECT, ANY and ALL in other engines. Sources: sqlite.org lang_expr.html (scalar subquery takes
# the first row, EXISTS, IN with subquery), lang_select.html (subqueries in FROM), PostgreSQL docs 9.23 (ANY, ALL).
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('scalar', 'A query inside a query', f'''
<p>"Which products cost more than the average price?" has two steps: first work out the average, then compare each product with it. A <b>subquery</b> lets you write both steps in one statement. The inner query, in brackets, runs first and hands its answer to the outer query.</p>
{K.sql('above', """SELECT name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price;""", title='Products above the average price', notes={3: f"The subquery returns one value, the average ({value('shop', 'SELECT round(avg(price), 1) FROM products')}). The outer WHERE compares every price with it."})}
<p>A subquery that returns exactly one value is called a <b>scalar subquery</b>. You can use it anywhere a single value fits: in WHERE, in the SELECT list, even inside a calculation.</p>
{K.sql('inselect', """SELECT name, price,
       price - (SELECT AVG(price) FROM products) AS above_average
FROM products
ORDER BY above_average DESC
LIMIT 3;""", title='A subquery in the SELECT list', notes={2: 'The same average is subtracted from every price.'})}
{note('If a scalar subquery returns more than one row, SQLite quietly uses the first row, while PostgreSQL and SQL Server raise an error. Make sure a scalar subquery can only return one row, for example with an aggregate or a key lookup.', 'warn')}
{K.lab('l-max', 'e', 'The most expensive product', 'Show the <code>name</code> of the product whose price equals the highest price, using a subquery.', 'SELECT name FROM products WHERE price = (SELECT MAX(price) FROM products);', hint='WHERE price = (SELECT MAX(price) FROM products).', why='The inner query finds the top price, the outer query finds who has it. Ties would all be returned.')}
''', kw=['subquery', 'nested query', 'scalar subquery', 'inner query', 'outer query', 'above average'])
K.talk('scalar', '''A subquery is a query inside brackets inside another query. It lets you answer two step questions in one go. To find products that cost more
than the average, the inner query works out the average, and the outer query compares every product with it. When a subquery gives back exactly
one value, it is called a scalar subquery, and you can use it anywhere a single value fits, in WHERE, in the select list, or inside a sum. Be
careful that it really returns one row. SQLite quietly takes the first row if there are more, while PostgreSQL raises an error. Think of asking
a friend for the class average before deciding who scored above it.''')

K.lesson('in', 'IN and NOT IN with a list from a query', f'''
<p>A subquery can also return a whole column of values. <code>IN</code> then checks whether a value is in that list. "Customers who placed an order" is "customers whose id is in the list of customer ids in orders".</p>
{K.sql('in', """SELECT name
FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE status = 'pending');""", title='Customers with a pending order', notes={3: 'The inner query returns a list of ids. IN keeps customers whose id is in that list.'})}
{K.sql('notin', """SELECT name
FROM customers
WHERE id NOT IN (SELECT customer_id FROM orders);""", title='Customers who never ordered', notes={3: 'Safe here only because orders.customer_id never holds NULL in this data.'})}
{note('Remember the NULL trap from chapter 2.2: if the subquery list contains even one NULL, NOT IN returns no rows at all. NOT EXISTS, in the next lesson, does not have this problem.', 'warn')}
{table(['Operator', 'True when', 'Engines'], [
    ['<code>x IN (subquery)</code>', 'x equals some value in the list', 'all'],
    ['<code>x NOT IN (subquery)</code>', 'x equals no value, and the list has no NULL', 'all'],
    ['<code>x &gt; ANY (subquery)</code>', 'x is bigger than at least one value', 'PostgreSQL, MySQL, SQL Server, Oracle (not SQLite)'],
    ['<code>x &gt; ALL (subquery)</code>', 'x is bigger than every value', 'PostgreSQL, MySQL, SQL Server, Oracle (not SQLite)']])}
{K.lab('l-in', 'm', 'Products someone bought', 'Show the <code>name</code> of every product that appears in at least one order line, using IN.', 'SELECT name FROM products WHERE id IN (SELECT product_id FROM order_items);', hint='id IN (SELECT product_id FROM order_items).', why='IN checks membership in the list the subquery returns. Duplicates in the list do not repeat rows.')}
''', kw=['IN subquery', 'NOT IN subquery', 'ANY', 'ALL', 'membership', 'list subquery'])
K.talk('in', '''A subquery can return a whole column, a list of values, and IN checks whether a value is in that list. Customers with a pending order are customers
whose id appears in the list of customer ids from pending orders. NOT IN finds the opposite, such as customers who never ordered. Remember the trap
from the NULL chapter, if the list holds even one NULL, NOT IN returns nothing at all, so be careful when the inner column can be empty. Other engines
also offer ANY and ALL, for tests like bigger than every value in a list, but SQLite does not have them. Think of a guest list at a wedding gate,
IN means your name is on the list.''')

K.lesson('exists', 'EXISTS and correlated subqueries', f'''
<p>A <b>correlated subquery</b> refers to a column of the outer query, so it runs again for every outer row, like a question asked about each person in turn. <code>EXISTS</code> is true when the subquery returns at least one row. It does not care what the row contains, which is why people write <code>SELECT 1</code> inside it.</p>
{pk('sqexists')}
{K.sql('exists', """SELECT c.name
FROM customers AS c
WHERE NOT EXISTS (
  SELECT 1 FROM orders AS o
  WHERE o.customer_id = c.id
);""", title='NOT EXISTS: never ordered, NULL safe', notes={5: 'c.id comes from the outer row, so the inner query is asked once per customer.'})}
{K.sql('corr', """SELECT p.name, p.category, p.price
FROM products AS p
WHERE p.price = (
  SELECT MAX(p2.price) FROM products AS p2
  WHERE p2.category = p.category
)
ORDER BY p.category;""", title='The most expensive product in each category', notes={5: 'For each product, the inner query finds the top price of that product’s own category.'})}
{table(['', 'IN', 'EXISTS'], [
    ['Looks at', 'the values the subquery returns', 'only whether any row comes back'],
    ['NULL in the subquery', 'NOT IN breaks', 'NOT EXISTS works'],
    ['Stops early', 'engine dependent', 'yes, at the first matching row'],
    ['Typical use', 'short lists, readable filters', 'anti joins, correlated checks']])}
{K.lab('l-exists', 'm', 'Customers with a delivered order', 'Show the <code>name</code> of every customer who has at least one order with status delivered. Use EXISTS.', "SELECT c.name FROM customers AS c WHERE EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id AND o.status = 'delivered');", hint='Correlate on o.customer_id = c.id and add the status test inside.', why='EXISTS is true for a customer as soon as one delivered order is found.')}
''', kw=['EXISTS', 'NOT EXISTS', 'correlated subquery', 'SELECT 1', 'semi join', 'per row subquery', 'greatest per group'])
K.talk('exists', '''A correlated subquery mentions a column from the outer query, so it is asked again for every outer row. EXISTS is true when the inner query finds
at least one row, and it does not care what the row holds, which is why people write SELECT one inside it. Watch the animation ask the question
once per customer. NOT EXISTS finds customers who never ordered, and unlike NOT IN it is safe when NULLs appear. The second example finds the most
expensive product in each category, by comparing each product with the top price of its own category. Engines also stop EXISTS at the first match.
Think of a teacher asking each student in turn, did you bring your homework.''')

K.lesson('derived', 'Subqueries in FROM: derived tables', f'''
<p>A subquery in the FROM clause builds a temporary table that the outer query reads like any other table. It is called a <b>derived table</b> and it must have an alias. It is perfect for "aggregate first, then filter or join the aggregate".</p>
{K.sql('derived', """SELECT t.customer_id, t.items
FROM (
  SELECT o.customer_id, SUM(oi.qty) AS items
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.id
  GROUP BY o.customer_id
) AS t
WHERE t.items > (SELECT AVG(items) FROM (
  SELECT SUM(oi.qty) AS items
  FROM orders AS o JOIN order_items AS oi ON oi.order_id = o.id
  GROUP BY o.customer_id))
ORDER BY t.items DESC;""", title='Customers who bought more items than the average customer', notes={3: 'Inner step: items bought per customer.', 7: 'The derived table is named t.', 8: 'Compare each customer with the average of those totals.'})}
<p>That query repeats the same inner query twice. Chapter 4.3 introduces <code>WITH</code> (common table expressions), which names a subquery once and reuses it, making such queries much easier to read.</p>
{scene('the loyalty programme', '<p>A shop wants to send a gift to customers who spend more than the average customer. The analyst first builds "spend per customer" as a derived table, then compares each row with the average of that table. Two clear steps, one query, and the marketing team gets the list in seconds.</p>')}
{K.lab('l-derived', 'h', 'Average order size', 'Return one column <code>avg_items</code>: the average number of items (sum of qty) per order, rounded to 2 decimals.', 'SELECT ROUND(AVG(items), 2) AS avg_items FROM (SELECT order_id, SUM(qty) AS items FROM order_items GROUP BY order_id) AS t;', hint='First SUM(qty) per order in a derived table, then AVG over it.', why='You cannot nest aggregates such as AVG(SUM(qty)) directly, so the derived table computes the inner step first.')}
''', kw=['derived table', 'subquery in FROM', 'inline view', 'aggregate then filter', 'nested aggregate'])
K.talk('derived', '''A subquery can also sit in the FROM clause, where it builds a temporary table for the outer query to read. This is called a derived table, and it
must have a name. It shines when you need to aggregate first and then work with the aggregate, for example items per customer, then compare each
customer with the average. You cannot write AVG of SUM directly, so the derived table does the first step. The example repeats one inner query twice,
which works but is hard to read, and that is exactly the problem the WITH clause solves in a later chapter. Think of making a rough draft on a
separate sheet of paper before writing the final answer.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A subquery is a small question you answer first, so the big question can use the answer.</p>',
    '<p>Scalar subqueries return one value, IN subqueries one column, derived tables a whole table. Correlated subqueries are evaluated per outer row, at least logically.</p>',
    '<p>Optimizers unnest subqueries: an IN or EXISTS subquery becomes a semi join, NOT EXISTS an anti join, and a correlated scalar subquery a join with a grouped derived table. After unnesting, the join algorithms from chapter 3.2 apply.</p>',
    '<p>Decorrelation of arbitrary nested queries is an active research topic. A 2015 paper by Neumann and Kemper, Unnesting Arbitrary Queries, showed a general method that removes correlation from any subquery, and systems such as Umbra and DuckDB build on it.</p>')}
{deep('Rewriting a correlated subquery as a join', '<p>The "most expensive product per category" query can be written as a join to a derived table: <code>JOIN (SELECT category, MAX(price) AS top FROM products GROUP BY category) AS m ON m.category = p.category AND p.price = m.top</code>. Window functions in chapter 6.1 give a third way.</p>')}
''', kw=['unnesting', 'decorrelation', 'semi join', 'anti join', 'Neumann and Kemper'])
K.talk('levels', '''Climbing the ladder again. For a beginner, a subquery is a small question you answer first. At college level, scalar subqueries give one value, IN
subqueries give one column, and derived tables give a whole table, while correlated subqueries are asked once per outer row. At masters level,
optimizers unnest subqueries into joins, so EXISTS becomes a semi join and NOT EXISTS an anti join. At research level, a 2015 paper by Neumann and
Kemper showed how to remove correlation from any nested query, and modern engines build on that. Think of a good cook who reads a recipe with many
sub steps and reorganises the kitchen work to finish faster.''')

avg_price = value('shop', 'SELECT avg(price) FROM products')
K.quiz('e', 'Which part of a query with a subquery runs first, logically?', ['The outer query', 'The inner query in brackets', 'Both at once', 'ORDER BY'], 1, 'Inside out.', 'The inner query provides a value or list for the outer one.')
K.quiz('e', 'A subquery that returns exactly one value is', ['A derived table', 'A scalar subquery', 'A join', 'A view'], 1, 'One value.', 'Scalar means a single value.')
K.quiz('e', 'A subquery in FROM must have', ['An ORDER BY', 'An alias', 'A WHERE', 'A LIMIT'], 1, 'Name it.', 'Derived tables need a name.')
K.quiz('e', 'EXISTS is true when', ['The subquery returns at least one row', 'The subquery returns TRUE', 'A column is not NULL', 'The table exists'], 0, 'Any row.', 'EXISTS only checks for rows.')
K.quiz('m', 'A correlated subquery', ['Runs once', 'Refers to a column of the outer query', 'Must be in FROM', 'Cannot use WHERE'], 1, 'Depends on outer row.', 'It is evaluated per outer row.')
K.quiz('m', 'Why is NOT EXISTS safer than NOT IN?', ['It is faster always', 'It is not broken by NULLs in the subquery', 'It is shorter', 'It sorts'], 1, 'NULL trap.', 'NOT IN returns nothing if the list holds NULL.')
K.quiz('m', 'Why write SELECT 1 inside EXISTS?', ['It is required', 'The selected values are ignored, only rows matter', 'It returns 1', 'Speed only'], 1, 'Ignored.', 'EXISTS only checks whether rows exist.')
K.quiz('m', 'AVG(SUM(qty)) written directly', ['Works', 'Is an error, nest via a derived table', 'Returns NULL', 'Returns SUM'], 1, 'Nested aggregate.', 'Compute SUM per group first in a subquery.')
K.quiz('h', 'If a scalar subquery returns 3 rows, SQLite', ['Raises an error', 'Uses the first row', 'Uses the last row', 'Returns NULL'], 1, 'Quietly.', 'SQLite takes the first row, PostgreSQL raises an error.')
K.quiz('h', 'x &gt; ALL (subquery) is supported in', ['SQLite', 'PostgreSQL', 'Neither', 'Only SQL Server'], 1, 'Not SQLite.', 'SQLite has no ANY or ALL.')
K.quiz('x', 'An optimizer turning EXISTS into a join produces a', ['Cross join', 'Semi join', 'Full join', 'Self join'], 1, 'Keep left rows with a match.', 'Semi joins keep left rows that have a partner, without duplicates.')

K.calc('e', 'What is the average product price, to 1 decimal?', f"{round(avg_price, 1)}", 'Sum of prices over 10.',
       [f"Sum of prices = {value('shop', 'SELECT sum(price) FROM products')}.", '10 products.', eq(f"{value('shop', 'SELECT sum(price) FROM products')} / 10 = {avg_price}")], check=round(avg_price, 1))
K.calc('e', 'How many products cost more than the average price?', str(value('shop', 'SELECT count(*) FROM products WHERE price > (SELECT avg(price) FROM products)')), f'Average is {avg_price}.',
       [f'The average is {avg_price}.', 'Above it: Headphones 1499, Desk lamp 1250, Football 850, Phone charger 699.', eq('4 products')], check=value('shop', 'SELECT count(*) FROM products WHERE price > (SELECT avg(price) FROM products)'))
K.calc('m', 'How many customers have a pending order?', str(value('shop', "SELECT count(*) FROM customers WHERE id IN (SELECT customer_id FROM orders WHERE status = 'pending')")), 'Pending orders 107 and 110.',
       ['Order 107 is Ravi’s, order 110 is Asha’s.', 'Two different customers.', eq('2')], check=value('shop', "SELECT count(*) FROM customers WHERE id IN (SELECT customer_id FROM orders WHERE status = 'pending')"))
K.calc('m', 'How many rows does the "most expensive product per category" query return?', str(value('shop', 'SELECT count(*) FROM products p WHERE p.price = (SELECT max(p2.price) FROM products p2 WHERE p2.category = p.category)')), 'One per category unless there is a tie.',
       ['Four categories.', 'No ties at the top price.', eq('4 rows')], check=value('shop', 'SELECT count(*) FROM products p WHERE p.price = (SELECT max(p2.price) FROM products p2 WHERE p2.category = p.category)'))
K.calc('m', 'How many customers have at least one delivered order?', str(value('shop', "SELECT count(*) FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'delivered')")), 'EXISTS per customer.',
       ['Delivered orders: 101 (1), 102 (2), 104 (3), 106 (7), 109 (5).', 'Different customers: 1, 2, 3, 5, 7.', eq('5')], check=value('shop', "SELECT count(*) FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'delivered')"))
K.calc('h', 'Average items per order (sum of qty per order, averaged), to 2 decimals?', f"{value('shop', 'SELECT round(avg(items), 2) FROM (SELECT sum(qty) AS items FROM order_items GROUP BY order_id)'):.2f}", 'Derived table first.',
       [f"Total items = {value('shop', 'SELECT sum(qty) FROM order_items')}.", '10 orders.', eq(f"{value('shop', 'SELECT sum(qty) FROM order_items')} / 10 = {value('shop', 'SELECT round(avg(items), 2) FROM (SELECT sum(qty) AS items FROM order_items GROUP BY order_id)'):.2f}")],
       check=value('shop', 'SELECT round(avg(items), 2) FROM (SELECT sum(qty) AS items FROM order_items GROUP BY order_id)'), tol=0.005)
K.calc('h', 'How many employees earn more than the average salary of their own department? (company database, employees with a department only)', str(value('company', 'SELECT count(*) FROM employees e WHERE e.salary > (SELECT avg(salary) FROM employees x WHERE x.dept_id = e.dept_id)')), 'Correlated on dept_id.',
       ['Engineering average 146250: Priya and Rahul are above.', 'Sales average 93333: Lata above. Support average 65000: Mohan above.', eq('4 employees')], check=value('company', 'SELECT count(*) FROM employees e WHERE e.salary > (SELECT avg(salary) FROM employees x WHERE x.dept_id = e.dept_id)'))
K.calc('h', 'How many students scored above 80 in at least one course? Use EXISTS on the school database.', str(value('school', 'SELECT count(*) FROM students s WHERE EXISTS (SELECT 1 FROM marks m WHERE m.student_id = s.id AND m.score > 80)')), 'Any score above 80.',
       ['Anu 92, 85. Chitra 88, 95, 81. Esha 99, 90, 87.', 'Others have no score above 80.', eq('3 students')], check=value('school', 'SELECT count(*) FROM students s WHERE EXISTS (SELECT 1 FROM marks m WHERE m.student_id = s.id AND m.score > 80)'))

K.must('Subquery', 'A query in brackets inside another. Scalar (one value), list (one column, used with IN), or table (in FROM, needs an alias).')
K.must('IN and NOT IN', 'IN tests membership. NOT IN returns nothing if the list holds a NULL.')
K.must('EXISTS', 'True when the subquery returns any row. NOT EXISTS is the NULL safe anti join.')
K.must('Correlated', 'Refers to the outer row, so it is evaluated per outer row. Great for per group comparisons.')
K.must('Derived tables', 'Aggregate first, then filter or join. AVG(SUM(x)) needs a derived table.')

T = K.topic(
    slug='sql-subqueries', topic='sql-subqueries', step=(3, 'Many tables', 'sql-many', 'Keys and relationships, every kind of join, subqueries and set operations.', 'Intermediate'),
    title='Subqueries: questions inside questions', short='Subqueries', badge='3.3', minutes=45, added='2026-11-23',
    lead='Answer two step questions in one statement with scalar subqueries, IN and NOT IN, EXISTS and correlated subqueries, and derived tables in FROM.',
    desc='Scalar subqueries in WHERE and SELECT, IN and NOT IN with subqueries, ANY and ALL, EXISTS and NOT EXISTS, correlated subqueries, greatest per group, derived tables, nested aggregates and unnesting.',
    summary='Scalar, list and table subqueries, EXISTS and correlated subqueries, and derived tables.',
    keywords=['subquery', 'scalar subquery', 'IN', 'EXISTS', 'NOT EXISTS', 'correlated subquery', 'derived table'],
    recap='<p>Subqueries answer the small question first: one value, a list for IN, a row check for EXISTS, or a whole table in FROM.</p>')
