# Chapter 3.2: joins: INNER, LEFT, RIGHT, FULL OUTER, CROSS, self joins, joining three tables, ON versus WHERE with
# outer joins, USING and NATURAL. Sources: sqlite.org lang_select.html (join operators, RIGHT and FULL OUTER JOIN
# supported since 3.39.0, 2022-07-21), PostgreSQL docs 7.2.1 (joined tables), sql.js 1.16.0 run checks.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('inner', 'INNER JOIN: rows that match', f'''
<p>An order row says customer_id 3. To print "Meera ordered on 11 June" we must put the order row and the customer row side by side. A <b>join</b> does that: it pairs rows from two tables whenever a condition, written after <code>ON</code>, is true.</p>
{pk('sqjoin')}
{K.sql('inner', """SELECT o.id AS order_id, o.order_date, c.name, c.city
FROM orders AS o
INNER JOIN customers AS c ON c.id = o.customer_id
ORDER BY o.id;""", title='Every order with its customer', notes={2: 'o is a short alias for orders.', 3: 'Pair each order with the customer whose id equals the order’s customer_id. INNER keeps only matching pairs.'})}
{fxs(fx('Inner join', '<code>SELECT ... FROM a JOIN b ON b.a_id = a.id;</code>', 'JOIN alone means INNER JOIN. Only pairs that satisfy ON are kept.', key=True),
     fx('Qualify columns', '<code>o.id</code>, <code>c.id</code>', 'When both tables have a column called id, write the table or alias in front, or the engine reports an ambiguous column.'))}
{note('An inner join loses rows that have no partner. Kabir, Arjun and Vikram never ordered, so they do not appear in the result above.', 'warn')}
{K.lab('l-inner', 'e', 'Who bought what', 'Show each <code>order_id</code> from order_items with the product <code>name</code>, for every line of every order.', 'SELECT oi.order_id, p.name FROM order_items AS oi JOIN products AS p ON p.id = oi.product_id;', hint='Join order_items to products on product_id.', why='Each line points at one product, so the join adds the product name.')}
''', kw=['JOIN', 'INNER JOIN', 'ON', 'table alias', 'ambiguous column', 'matching rows'])
K.talk('inner', '''A join puts rows from two tables side by side. An order stores only a customer number, so to show the customer's name we pair each order with
the customer whose id matches. The pairing rule goes after the word ON. An inner join, which is what plain JOIN means, keeps only the pairs where
the rule is true, so customers who never ordered simply disappear from the result. Watch the animation pair each customer with their orders. Short
aliases like o and c save typing, and when both tables have a column called id, you must say which one you mean. Think of matching left shoes with
right shoes, only complete pairs go into the box.''')

K.lesson('outer', 'LEFT, RIGHT and FULL joins: keeping the unmatched', f'''
<p>"List <b>every</b> customer with their number of orders, even zero" needs the customers who have no orders. A <code>LEFT JOIN</code> keeps every row of the left table. Where no partner exists, the right side columns are filled with NULL.</p>
{K.sql('left', """SELECT c.name, COUNT(o.id) AS orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
GROUP BY c.id
ORDER BY orders DESC, c.name;""", title='Every customer, even with zero orders', notes={1: 'COUNT(o.id) counts only real orders. For a customer with none, o.id is NULL, so the count is 0. COUNT(*) would wrongly give 1.', 3: 'LEFT keeps every customer.'})}
{table(['Join', 'Keeps', 'Unmatched side gets'], [
    ['INNER', 'only matching pairs', 'nothing, rows dropped'],
    ['LEFT (OUTER)', 'every left row', 'NULLs in the right columns'],
    ['RIGHT (OUTER)', 'every right row', 'NULLs in the left columns'],
    ['FULL (OUTER)', 'every row from both sides', 'NULLs on whichever side is missing'],
    ['CROSS', 'every possible pair, no ON', 'not applicable']])}
{K.sql('anti', """SELECT c.name
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE o.id IS NULL;""", title='The anti join: customers who never ordered', notes={4: 'After a LEFT JOIN, a NULL order id means no partner was found.'})}
{note('SQLite supports RIGHT JOIN and FULL OUTER JOIN since version 3.39.0 (July 2022). MySQL still has no FULL OUTER JOIN: people write a LEFT JOIN UNION a RIGHT JOIN instead.', 'exam')}
{K.lab('l-noorder', 'm', 'Products nobody ordered', 'Show the <code>name</code> of every product that appears in no order line.', 'SELECT p.name FROM products AS p LEFT JOIN order_items AS oi ON oi.product_id = p.id WHERE oi.order_id IS NULL;', hint='LEFT JOIN products to order_items, then keep rows where the order_items side is NULL.', why='This anti join pattern finds rows with no partner. NOT EXISTS works too.')}
''', kw=['LEFT JOIN', 'RIGHT JOIN', 'FULL OUTER JOIN', 'outer join', 'anti join', 'COUNT with LEFT JOIN', 'NULL padding'])
K.talk('outer', '''An inner join drops rows with no partner, but often you want them. LEFT JOIN keeps every row of the left table, and fills the right side with NULL when
there is no match. That is how you list every customer with their order count, including zero. Use COUNT of the order id, not COUNT star, because COUNT
star would count the padded row as one. RIGHT JOIN keeps every row of the right table, and FULL JOIN keeps everything from both sides. A neat trick
called the anti join keeps only the NULL padded rows, which finds customers who never ordered. SQLite added RIGHT and FULL joins in 2022, while MySQL
still lacks FULL. Think of a class photo where absent students still get an empty chair with their name on it.''')

K.lesson('more', 'Three tables, self joins and CROSS JOIN', f'''
<p>Real questions often cross three or four tables. Each JOIN adds one more table and one more ON condition. "Which customer bought which product" needs customers, orders, order_items and products.</p>
{K.sql('three', """SELECT c.name AS customer, p.name AS product, oi.qty
FROM customers AS c
JOIN orders      AS o  ON o.customer_id = c.id
JOIN order_items AS oi ON oi.order_id   = o.id
JOIN products    AS p  ON p.id          = oi.product_id
WHERE c.name = 'Asha'
ORDER BY o.id, p.name;""", title='Four tables in one query', notes={3: 'Customer to order.', 4: 'Order to its lines.', 5: 'Line to product.'})}
<p>A <b>self join</b> joins a table to itself. In the company database each employee has a <code>manager_id</code> that points at another employee. Two aliases of the same table let us show each person next to their manager.</p>
{K.sql('self', """SELECT e.name AS employee, m.name AS manager
FROM employees AS e
LEFT JOIN employees AS m ON m.id = e.manager_id
ORDER BY e.id;""", db='company', title='Who reports to whom', notes={3: 'm is a second copy of employees, used for the manager. LEFT keeps Priya, who has no manager.'})}
{K.sql('cross', """SELECT s.size, c.colour
FROM (SELECT 'S' AS size UNION ALL SELECT 'M' UNION ALL SELECT 'L') AS s
CROSS JOIN (SELECT 'red' AS colour UNION ALL SELECT 'blue') AS c;""", db='', title='CROSS JOIN makes every pair', notes={3: '3 sizes × 2 colours = 6 rows, every combination of T shirt.'})}
{note('A join with a missing or wrong ON condition can turn into an accidental cross join: 10 000 rows times 10 000 rows is 100 million rows. If a result is suddenly huge, check the ON clauses first.', 'warn')}
{K.lab('l-self', 'm', 'Managers and their teams', 'From the company database, show each manager’s <code>name</code> as <code>manager</code> and the number of people reporting to them as <code>team</code>.', 'SELECT m.name AS manager, COUNT(*) AS team FROM employees AS e JOIN employees AS m ON m.id = e.manager_id GROUP BY m.id;', db='company', hint='Self join employees e to employees m on m.id = e.manager_id, then group by the manager.', why='Each employee row joins to its manager, and grouping by manager counts the reports.')}
''', kw=['multiple joins', 'self join', 'manager hierarchy', 'CROSS JOIN', 'Cartesian product', 'accidental cross join'])
K.talk('more', '''Real questions cross several tables, and each extra JOIN adds one table and one ON rule. To see which product each customer bought, you walk from
customers to orders, then to order items, then to products. A self join joins a table to itself, which sounds odd but is very useful. Every
employee has a manager id pointing at another employee, so two aliases of the same table show each person next to their boss. A cross join pairs
every row with every row, which is handy for making every size and colour of a T shirt. But a forgotten ON rule can create a cross join by mistake,
and the result explodes. Think of a family tree, where each person points at a parent in the same tree.''')

K.lesson('onwhere', 'ON versus WHERE, USING and NATURAL', f'''
<p>For an inner join it makes no difference whether a filter sits in ON or WHERE. For an outer join it changes everything. A condition in <b>ON</b> decides which rows match. A condition in <b>WHERE</b> runs after the join and can throw away the NULL padded rows you wanted to keep.</p>
{K.sql('onwhere', """-- Filter in ON: every customer stays, only delivered orders are counted
SELECT c.name, COUNT(o.id) AS delivered
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id AND o.status = 'delivered'
GROUP BY c.id ORDER BY c.id;

-- Filter in WHERE: customers without a delivered order vanish
SELECT c.name, COUNT(o.id) AS delivered
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE o.status = 'delivered'
GROUP BY c.id ORDER BY c.id;""", title='Same words, different place, different answer', notes={4: 'The status test is part of matching. Unmatched customers still appear with 0.', 11: 'NULL status is not delivered, so the padded rows are removed and the LEFT JOIN acts like an INNER JOIN.'})}
{table(['Shortcut', 'Means', 'Advice'], [
    ['<code>JOIN t USING (id)</code>', 'ON a.id = t.id, and the id column appears once', 'fine when both columns share a name'],
    ['<code>NATURAL JOIN t</code>', 'join on every column with the same name', 'avoid: adding a column later can silently change the join'],
    ['<code>FROM a, b WHERE a.x = b.x</code>', 'old comma style inner join', 'works, but explicit JOIN ... ON is clearer']])}
{K.lab('l-onwhere', 'h', 'Customers and their pending orders', 'Show every customer’s <code>name</code> and the number of their orders with status pending as <code>pending</code>, including customers with 0.', "SELECT c.name, COUNT(o.id) AS pending FROM customers AS c LEFT JOIN orders AS o ON o.customer_id = c.id AND o.status = 'pending' GROUP BY c.id;", hint='Put the status test in ON, not in WHERE.', why='A filter in ON keeps unmatched customers. In WHERE it would drop them.')}
''', kw=['ON vs WHERE', 'outer join filter', 'USING', 'NATURAL JOIN', 'comma join', 'implicit join'])
K.talk('onwhere', '''Here is a subtle rule that catches many people. With an inner join, a filter can sit in ON or in WHERE with the same result. With an outer join,
the place matters. A test in ON is part of the matching, so unmatched rows still survive with NULLs. A test in WHERE runs after the join, and since
NULL never equals delivered, the padded rows are thrown away and your left join quietly becomes an inner join. Compare the two queries in the block.
USING is a tidy shortcut when the join columns share a name. NATURAL JOIN guesses the columns for you, which is risky when tables change later.
Think of choosing team members first by sport, then removing everyone without a jersey.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A join is matching cards from two piles. Inner keeps pairs, left keeps every card from the left pile.</p>',
    '<p>Logically a join is a cross product followed by a filter on the ON condition. Outer joins then add back unmatched rows padded with NULL.</p>',
    '<p>Engines run joins with three main algorithms: nested loop (for each left row look up the right side, fast with an index), hash join (build a hash table of the smaller side, best for big equality joins) and merge join (walk two sorted inputs together). SQLite uses nested loops, often with an automatic temporary index.</p>',
    '<p>Choosing the order of many joins is hard: the number of possible orders grows faster than exponentially. Optimizers use dynamic programming for a handful of tables and heuristics or genetic search beyond that (PostgreSQL switches to its genetic optimizer at 12 tables by default).</p>')}
{deep('Semi join and anti join', '<p>A semi join keeps left rows that have at least one match, without repeating them: that is what EXISTS and IN do. An anti join keeps left rows with no match: NOT EXISTS or LEFT JOIN ... WHERE right.key IS NULL. Optimizers often turn subqueries into these joins.</p>')}
''', kw=['nested loop join', 'hash join', 'merge join', 'join order', 'genetic optimizer', 'semi join', 'anti join'])
K.talk('levels', '''One more climb. For a child, a join matches cards from two piles. At college level, a join is every possible pair filtered by the ON rule, and outer
joins add back the lonely rows with NULLs. At masters level, engines use three main methods. A nested loop looks up partners for each row, a hash
join builds a lookup table from the smaller side, and a merge join walks two sorted lists together. At research level, choosing the order of many
joins is a hard puzzle, and PostgreSQL switches to a genetic search when a query joins twelve or more tables. Think of a wedding planner deciding
which families to seat first.''')

K.quiz('e', 'JOIN with no other word means', ['LEFT JOIN', 'INNER JOIN', 'CROSS JOIN', 'FULL JOIN'], 1, 'Default.', 'JOIN is INNER JOIN.')
K.quiz('e', 'Which join keeps every row of the left table?', ['INNER', 'LEFT', 'RIGHT', 'CROSS'], 1, 'Left.', 'LEFT JOIN keeps all left rows.')
K.quiz('e', 'Unmatched rows in an outer join get', ['0', 'NULL', 'Empty text', 'They are removed'], 1, 'Padding.', 'Missing side columns are NULL.')
K.quiz('e', 'A table joined to itself is a', ['Cross join', 'Self join', 'Natural join', 'Union'], 1, 'Itself.', 'Self join with two aliases.')
K.quiz('m', 'CROSS JOIN of 4 rows and 5 rows gives', ['9 rows', '20 rows', '5 rows', '4 rows'], 1, 'Every pair.', '4 × 5 = 20.')
K.quiz('m', 'To list customers with zero orders counted as 0, use', ['INNER JOIN and COUNT(*)', 'LEFT JOIN and COUNT(o.id)', 'LEFT JOIN and COUNT(*)', 'CROSS JOIN'], 1, 'Count the right side.', 'COUNT(o.id) ignores the NULL padding.')
K.quiz('m', 'Which finds customers with no orders?', ['INNER JOIN ... WHERE o.id IS NULL', 'LEFT JOIN ... WHERE o.id IS NULL', 'RIGHT JOIN ... WHERE c.id IS NULL', 'CROSS JOIN ... WHERE o.id = 0'], 1, 'Anti join.', 'NULL after a LEFT JOIN means no partner.')
K.quiz('m', 'Why write o.id instead of id?', ['Speed', 'Both tables have id, so it is ambiguous', 'Style only', 'It is required in WHERE only'], 1, 'Which id?', 'The alias says which table.')
K.quiz('h', 'A LEFT JOIN with WHERE right.col = … on the right table usually behaves like', ['A FULL JOIN', 'An INNER JOIN', 'A CROSS JOIN', 'A RIGHT JOIN'], 1, 'Padding removed.', 'The WHERE test drops NULL padded rows.')
K.quiz('h', 'Why avoid NATURAL JOIN?', ['It is slow', 'It joins on every same named column, which can change when tables change', 'It is not supported', 'It returns NULLs'], 1, 'Hidden columns.', 'A new same named column silently changes the join.')
K.quiz('x', 'Which join algorithm builds a lookup table from the smaller input?', ['Nested loop', 'Hash join', 'Merge join', 'Cross join'], 1, 'Hash table.', 'Hash join builds on the smaller side and probes with the other.')

n_inner = value('shop', 'SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id')
n_left = value('shop', 'SELECT count(*) FROM customers c LEFT JOIN orders o ON o.customer_id = c.id')
K.calc('e', 'How many rows does orders INNER JOIN customers return?', str(n_inner), 'Every order has a customer.',
       ['Each of the 10 orders has a valid customer_id.', 'Each order matches exactly one customer.', eq(f'{n_inner} rows')], check=n_inner)
K.calc('m', 'How many rows does customers LEFT JOIN orders return?', str(n_left), 'Matched pairs plus unmatched customers.',
       ['10 matched pairs (one per order).', '3 customers with no orders add one padded row each.', eq(f'10 + 3 = {n_left}')], check=n_left)
K.calc('e', 'A CROSS JOIN of customers and products returns how many rows?', str(value('shop', 'SELECT count(*) FROM customers CROSS JOIN products')), 'Rows times rows.',
       ['8 customers.', '10 products.', eq('8 × 10 = 80')], check=value('shop', 'SELECT count(*) FROM customers CROSS JOIN products'))
K.calc('m', 'How many order lines did Asha buy in total? (rows of order_items in her orders)', str(value('shop', "SELECT count(*) FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id WHERE c.name = 'Asha'")), 'Three joins.',
       ['Asha’s orders: 101, 103, 110.', 'Lines: 101 has 2, 103 has 2, 110 has 1.', eq('2 + 2 + 1 = 5')], check=value('shop', "SELECT count(*) FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id WHERE c.name = 'Asha'"))
K.calc('m', 'How many employees in the company database report directly to Priya (id 1)?', str(value('company', 'SELECT count(*) FROM employees WHERE manager_id = 1')), 'manager_id = 1.',
       ['Rahul, Lata, Mohan and Zoya have manager_id 1.', 'Count them.', eq('4')], check=value('company', 'SELECT count(*) FROM employees WHERE manager_id = 1'))
K.calc('h', 'In the ON versus WHERE example, how many rows does the WHERE version return?', str(value('shop', "SELECT count(*) FROM (SELECT c.id FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE o.status = 'delivered' GROUP BY c.id)")), 'Only customers with a delivered order.',
       ['Delivered orders belong to customers 1, 2, 3, 7 and 5.', 'Others are removed by WHERE.', eq('5 rows')], check=value('shop', "SELECT count(*) FROM (SELECT c.id FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE o.status = 'delivered' GROUP BY c.id)"))
K.calc('h', 'And the ON version?', str(value('shop', "SELECT count(*) FROM (SELECT c.id FROM customers c LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'delivered' GROUP BY c.id)")), 'Every customer stays.',
       ['A LEFT JOIN keeps every customer.', 'The status test only affects matching.', eq('8 rows')], check=value('shop', "SELECT count(*) FROM (SELECT c.id FROM customers c LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'delivered' GROUP BY c.id)"))
K.calc('h', 'How many total items (sum of qty) were bought in the Stationery category?', str(value('shop', "SELECT sum(oi.qty) FROM order_items oi JOIN products p ON p.id = oi.product_id WHERE p.category = 'Stationery'")), 'Join lines to products.',
       ['Stationery products are 1, 2 and 10.', 'Their quantities: 2, 5, 10, 4, 1, 3.', eq('2 + 5 + 10 + 4 + 1 + 3 = 25')], check=value('shop', "SELECT sum(oi.qty) FROM order_items oi JOIN products p ON p.id = oi.product_id WHERE p.category = 'Stationery'"))

K.must('Inner join', 'JOIN ... ON pairs rows where the condition is true. Unmatched rows are dropped.')
K.must('Outer joins', 'LEFT keeps all left rows, RIGHT all right rows, FULL both. Missing side becomes NULL. Count with COUNT(right.col).')
K.must('Anti join', 'LEFT JOIN ... WHERE right.key IS NULL finds rows with no partner.')
K.must('Self and cross', 'A self join uses two aliases of one table. CROSS JOIN makes every pair. A missing ON can cause a huge accidental cross join.')
K.must('ON vs WHERE', 'In outer joins, filters on the optional side belong in ON. In WHERE they remove the NULL rows.')
K.must('Algorithms', 'Nested loop, hash join, merge join. SQLite uses nested loops with indexes.')

T = K.topic(
    slug='sql-joins', topic='sql-joins', step=(3, 'Many tables', 'sql-many', 'Keys and relationships, every kind of join, subqueries and set operations.', 'Intermediate'),
    title='Joins: putting tables back together', short='Joins', badge='3.2', minutes=50, added='2026-11-23',
    lead='Pair rows from two or more tables with INNER, LEFT, RIGHT, FULL and CROSS joins, join a table to itself, find rows with no partner, and avoid the ON versus WHERE trap.',
    desc='INNER JOIN, LEFT, RIGHT and FULL OUTER JOIN, NULL padding, COUNT with outer joins, anti joins, joining four tables, self joins on a manager hierarchy, CROSS JOIN, ON versus WHERE, USING and NATURAL, join algorithms.',
    summary='Inner and outer joins, anti joins, self and cross joins, ON versus WHERE, and how engines run joins.',
    keywords=['JOIN', 'INNER JOIN', 'LEFT JOIN', 'FULL OUTER JOIN', 'self join', 'CROSS JOIN', 'anti join', 'hash join'],
    recap='<p>Joins pair rows by a condition, outer joins keep the unmatched with NULLs, self joins read hierarchies, and filters on the optional side belong in ON.</p>')
