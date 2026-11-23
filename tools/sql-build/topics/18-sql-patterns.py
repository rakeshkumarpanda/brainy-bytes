# Chapter 6.3: query patterns that solve real problems: top N per group, gaps and islands, pivoting with conditional
# aggregation and FILTER, finding and removing duplicates, percent of total, and working with JSON columns.
# Sources: sqlite.org windowfunctions.html, lang_aggfunc.html (FILTER clause on aggregates since 3.30.0), json1.html
# (json_extract, -> and ->> operators since 3.38.0, json_each, json_group_array, json_object), lang_corefunc.html,
# postgresql.org functions-json.html, Itzik Ben-Gan's writing on gaps and islands (the row number difference method).
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('topn', 'Top N per group', f'''
<p>"The two most expensive products in each category", "each customer’s latest order". LIMIT works on the whole result, not per group. The standard pattern ranks inside each group with a window function, then filters outside.</p>
{K.sql('top2', """WITH ranked AS (
  SELECT name, category, price,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC, id) AS rn
  FROM products
)
SELECT category, name, price FROM ranked
WHERE rn <= 2
ORDER BY category, rn;""", title='The two dearest products in each category', notes={3: 'Number the rows inside each category, dearest first. id breaks ties.', 7: 'Keep the first two of every category.'})}
{K.sql('latest', """SELECT c.name, o.id, o.order_date
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.order_date = (SELECT MAX(o2.order_date) FROM orders o2
                      WHERE o2.customer_id = c.id);""", title='The same idea with a correlated subquery', notes={4: 'Works in every engine, even without window functions. Ties on the date would return both rows.'})}
{table(['Want', 'Use'], [
    ['exactly N rows per group', 'ROW_NUMBER() ... WHERE rn <= N'],
    ['N, plus anyone tied with the Nth', 'RANK() ... WHERE rnk <= N'],
    ['the top N distinct values', 'DENSE_RANK() ... WHERE dr <= N'],
    ['one row per group, PostgreSQL only', 'SELECT DISTINCT ON (group) ... ORDER BY group, value DESC']])}
{K.lab('l-top1', 'm', 'Top earner per department', 'From the company database, show the <code>dept_id</code>, <code>name</code> and <code>salary</code> of the highest paid employee in each department. Leave out Zoya, who has no department.',
"""WITH r AS (SELECT dept_id, name, salary, ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn FROM employees WHERE dept_id IS NOT NULL)
SELECT dept_id, name, salary FROM r WHERE rn = 1;""", db='company', hint='ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC), then WHERE rn = 1 outside.', why='Each department has a single top earner here, so ROW_NUMBER and RANK agree.')}
''', kw=['top N per group', 'greatest per group', 'ROW_NUMBER filter', 'latest row per group', 'DISTINCT ON'])
K.talk('topn', '''A classic interview question is to find the top few rows in each group, such as the two most expensive products in every category. LIMIT works on
the whole result, not per group, so it cannot do this alone. The standard pattern ranks rows inside each group with ROW_NUMBER and PARTITION BY, in a
CTE, then keeps rows numbered two or less in the outer query. Use RANK instead if anyone tied with the last place should also appear. A correlated
subquery with MAX does the same job in engines without window functions. Think of picking the two tallest children from each class for the front row
of a school photo.''')

K.lesson('islands', 'Gaps and islands: finding streaks', f'''
<p>Streaks of consecutive days, runs of the same status, ranges of free seats: these are <b>islands</b>, and the holes between them are <b>gaps</b>. The neat trick: subtract a row number from the value. Within a streak the difference stays constant.</p>
{pk('sqisland')}
{K.sql('streak', """CREATE TABLE logins (day INTEGER);
INSERT INTO logins VALUES (1), (2), (3), (6), (7), (9), (10), (11), (12);
SELECT MIN(day) AS first_day, MAX(day) AS last_day, COUNT(*) AS streak
FROM (SELECT day, day - ROW_NUMBER() OVER (ORDER BY day) AS grp FROM logins)
GROUP BY grp ORDER BY first_day;""", db='', title='Three streaks of logins', notes={4: 'Same grp value means same streak.', 5: 'One row per island.'})}
{K.sql('gaps', """CREATE TABLE seats (no INTEGER);
INSERT INTO seats VALUES (1), (2), (3), (6), (7), (9), (10), (11), (12);
SELECT no + 1 AS gap_from, next_no - 1 AS gap_to
FROM (SELECT no, LEAD(no) OVER (ORDER BY no) AS next_no FROM seats)
WHERE next_no - no > 1;""", db='', title='The gaps: missing seat numbers', notes={4: 'LEAD looks at the next booked seat.', 5: 'A jump of more than 1 means seats are missing in between.'})}
{steps('The row number trick with dates', [
    'Convert each date to a day number with julianday(d).',
    'Subtract ROW_NUMBER() OVER (ORDER BY d).',
    'GROUP BY the difference. Each group is one unbroken run of dates.',
    eq('day − row number is constant inside an island')])}
{K.lab('l-island', 'h', 'Longest streak', 'The table <code>logins (day INTEGER)</code> holds days 1, 2, 3, 6, 7, 9, 10, 11, 12. Return one value <code>best</code>: the length of the longest streak.',
"""SELECT MAX(n) AS best FROM (SELECT COUNT(*) AS n FROM (SELECT day - ROW_NUMBER() OVER (ORDER BY day) AS g FROM logins) GROUP BY g);""", db='', setup="CREATE TABLE logins (day INTEGER); INSERT INTO logins VALUES (1), (2), (3), (6), (7), (9), (10), (11), (12);", hint='Count the rows of each island, then take MAX of those counts.', why='Days 9 to 12 make the longest streak, 4 days.')}
''', kw=['gaps and islands', 'streak', 'consecutive days', 'row number difference', 'LEAD gap', 'missing numbers'])
K.talk('islands', '''Streaks of consecutive days and runs of the same value are called islands, and the holes between them are gaps. Here is a neat trick. Number the
rows in order with ROW_NUMBER, then subtract that number from the day. Inside a streak, both go up by one each row, so the difference stays the same.
After a gap, the day jumps but the row number does not, so the difference changes. Group by the difference and each group is one streak. In the
animation, type your own login days and watch the colours split into islands. LEAD finds the gaps by comparing each value with the next. Think of a
fitness app counting your longest run of workout days.''')

K.lesson('pivot', 'Pivoting rows into columns', f'''
<p>A <b>pivot</b> turns values in rows into columns: one row per customer with a column per status, or one row per student with a column per subject. Standard SQL does it with <b>conditional aggregation</b>.</p>
{K.sql('pivot', """SELECT c.name,
       COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) AS delivered,
       COUNT(CASE WHEN o.status = 'pending'   THEN 1 END) AS pending,
       COUNT(*) FILTER (WHERE o.status = 'shipped')      AS shipped
FROM customers c JOIN orders o ON o.customer_id = c.id
GROUP BY c.id ORDER BY c.name;""", title='Orders per customer, one column per status', notes={2: 'CASE gives 1 for matching rows and NULL otherwise, and COUNT skips NULLs.', 4: 'FILTER is the tidier standard form, in SQLite 3.30+ and PostgreSQL.'})}
{K.sql('report', """SELECT s.name,
       MAX(CASE WHEN m.course_id = 1 THEN m.score END) AS algebra,
       MAX(CASE WHEN m.course_id = 2 THEN m.score END) AS physics,
       MAX(CASE WHEN m.course_id = 3 THEN m.score END) AS poetry
FROM students s LEFT JOIN marks m ON m.student_id = s.id
GROUP BY s.id ORDER BY s.id;""", db='school', title='A report card: one row per student', notes={2: 'MAX picks the single score, or NULL when the student has none.'})}
{table(['Engine', 'Pivot syntax'], [
    ['Every engine', 'conditional aggregation with CASE, as above'],
    ['SQL Server, Oracle', 'PIVOT ( aggregate FOR column IN (values) )'],
    ['PostgreSQL', 'FILTER, or crosstab() from the tablefunc extension'],
    ['DuckDB, Snowflake', 'PIVOT and UNPIVOT statements']])}
{note('The columns of a pivot must be known when you write the query. A pivot with columns decided by the data needs dynamic SQL built by a program.', 'tip')}
{K.lab('l-pivot', 'm', 'Stock by category', 'Return one row with three columns: <code>stationery</code>, <code>kitchen</code> and <code>sports</code>, each the total stock of that category.',
"""SELECT SUM(CASE WHEN category = 'Stationery' THEN stock END) AS stationery,
       SUM(CASE WHEN category = 'Kitchen' THEN stock END) AS kitchen,
       SUM(CASE WHEN category = 'Sports' THEN stock END) AS sports
FROM products;""", hint='One SUM(CASE WHEN category = ... THEN stock END) per column, no GROUP BY.', why='Without GROUP BY the whole table is one group, and each SUM picks its own category.')}
''', kw=['pivot', 'conditional aggregation', 'CASE WHEN', 'FILTER', 'crosstab', 'PIVOT', 'report card'])
K.talk('pivot', '''A pivot turns values in rows into columns, such as one row per customer with a column for each order status. The portable way is conditional
aggregation. For each column, write COUNT or SUM around a CASE that keeps only the rows for that column, and group by the customer. COUNT skips the
NULLs that CASE gives for other rows. Newer engines accept a FILTER clause, which reads more cleanly, and SQL Server and Oracle have a PIVOT keyword.
The column names must be known when you write the query. Think of a teacher copying marks from a long list into a grid with one column per subject.''')

K.lesson('dupes', 'Duplicates and percent of total', f'''
<p>Real data arrives with duplicates: the same customer typed twice, a form submitted two times. First find them, then keep one copy of each.</p>
{K.sql('finddup', """CREATE TABLE signups (email TEXT, name TEXT, signed_on TEXT);
INSERT INTO signups VALUES ('asha@mail.in', 'Asha', '2025-06-01'), ('ravi@mail.in', 'Ravi', '2025-06-02'),
  ('asha@mail.in', 'Asha P', '2025-06-03'), ('meera@mail.in', 'Meera', '2025-06-03'), ('ravi@mail.in', 'Ravi', '2025-06-05');
SELECT email, COUNT(*) AS copies FROM signups
GROUP BY email HAVING COUNT(*) > 1;""", db='', title='Find emails that appear more than once', notes={5: 'GROUP BY the column that should be unique, HAVING COUNT > 1.'})}
{K.sql('dedupe', """CREATE TABLE signups (email TEXT, name TEXT, signed_on TEXT);
INSERT INTO signups VALUES ('asha@mail.in', 'Asha', '2025-06-01'), ('ravi@mail.in', 'Ravi', '2025-06-02'),
  ('asha@mail.in', 'Asha P', '2025-06-03'), ('meera@mail.in', 'Meera', '2025-06-03'), ('ravi@mail.in', 'Ravi', '2025-06-05');
DELETE FROM signups WHERE rowid IN (
  SELECT rowid FROM (
    SELECT rowid, ROW_NUMBER() OVER (PARTITION BY email ORDER BY signed_on) AS rn FROM signups)
  WHERE rn > 1);
SELECT * FROM signups ORDER BY email;""", db='', title='Keep the earliest signup of each email', notes={6: 'Number the copies of each email, oldest first.', 7: 'Delete every copy after the first.', 8: 'Then add UNIQUE on email so it cannot happen again.'})}
{K.sql('pct', """SELECT category, SUM(stock) AS stock,
       ROUND(100.0 * SUM(stock) / SUM(SUM(stock)) OVER (), 1) AS pct
FROM products GROUP BY category ORDER BY pct DESC;""", title='Percent of total: a window over a GROUP BY', notes={2: 'SUM(SUM(stock)) OVER (): the inner SUM is per group, the outer window adds all groups. 100.0 avoids integer division.'})}
{note('rowid is SQLite’s hidden row number. PostgreSQL has ctid, and elsewhere you use the primary key. The pattern is the same: number the copies, delete all but number 1.', 'tip')}
{K.lab('l-dupes', 'm', 'Count the duplicate copies', 'In <code>signups</code>, return one value <code>extra</code>: how many rows would be deleted if you kept only one row per email.',
"""SELECT COUNT(*) - COUNT(DISTINCT email) AS extra FROM signups;""", db='', setup="""CREATE TABLE signups (email TEXT, name TEXT, signed_on TEXT);
INSERT INTO signups VALUES ('asha@mail.in', 'Asha', '2025-06-01'), ('ravi@mail.in', 'Ravi', '2025-06-02'), ('asha@mail.in', 'Asha P', '2025-06-03'), ('meera@mail.in', 'Meera', '2025-06-03'), ('ravi@mail.in', 'Ravi', '2025-06-05');""", hint='All rows minus the number of distinct emails.', why='5 rows, 3 distinct emails, so 2 extra copies.')}
''', kw=['duplicates', 'dedupe', 'remove duplicates', 'rowid', 'percent of total', 'ratio to total', 'HAVING COUNT > 1'])
K.talk('dupes', '''Real data often arrives with duplicates, like the same person signing up twice. To find them, group by the column that should be unique and keep groups
with a count above one. To remove them, number the copies of each email with ROW_NUMBER, oldest first, and delete every row numbered two or more. Then
add a unique rule so it cannot happen again. Another everyday pattern is percent of total. A window SUM over a grouped SUM gives the grand total on
every row, and multiplying by one hundred point zero avoids integer division. Think of a teacher who finds two copies of the same admission form and
keeps the first.''')

K.lesson('json', 'JSON inside a database', f'''
<p>Many apps store flexible data as <b>JSON</b> text in a column: settings, tags, event details. Modern engines can read inside it with SQL. SQLite’s JSON functions are built in (since 3.38 by default).</p>
{K.sql('jsonread', """CREATE TABLE events (id INTEGER PRIMARY KEY, data TEXT);
INSERT INTO events (data) VALUES
 ('{"user": "asha", "action": "buy", "items": ["pen", "book"], "amount": 180}'),
 ('{"user": "ravi", "action": "view", "items": ["lamp"]}'),
 ('{"user": "asha", "action": "buy", "items": ["lamp"], "amount": 1250}');
SELECT id, data ->> '$.user' AS user, json_extract(data, '$.amount') AS amount,
       json_array_length(data, '$.items') AS n_items
FROM events;""", db='', title='Read fields out of JSON text', notes={6: "->> returns a plain SQL value. json_extract does the same with a function call.", 7: 'Length of the items array.'})}
{K.sql('jsoneach', """CREATE TABLE events (id INTEGER PRIMARY KEY, data TEXT);
INSERT INTO events (data) VALUES
 ('{"user": "asha", "items": ["pen", "book"]}'), ('{"user": "ravi", "items": ["lamp"]}'),
 ('{"user": "asha", "items": ["lamp"]}');
SELECT j.value AS item, COUNT(*) AS times
FROM events, json_each(events.data, '$.items') AS j
GROUP BY j.value ORDER BY times DESC;""", db='', title='json_each turns an array into rows', notes={6: 'One output row per array element, joined to its event.'})}
{K.sql('jsonbuild', """SELECT category, json_group_array(name) AS names,
       json_object('count', COUNT(*), 'max_price', MAX(price)) AS info
FROM products GROUP BY category;""", title='Build JSON from rows', notes={1: 'Aggregate names into a JSON array.', 2: 'Make a JSON object from values.'})}
{table(['Engine', 'Read a field', 'Notes'], [
    ['SQLite', "data ->> '$.user'", 'JSON stored as text, functions json_extract, json_each'],
    ['PostgreSQL', "data ->> 'user'", 'jsonb type is binary and can be indexed with GIN'],
    ['MySQL', "data ->> '$.user'", 'JSON type, generated columns for indexing'],
    ['SQL Server', "JSON_VALUE(data, '$.user')", 'OPENJSON turns arrays into rows']])}
{note('JSON is handy for data whose shape varies. Fields you filter or join on every day usually deserve real columns, which get types, constraints and simple indexes.', 'tip')}
{K.lab('l-json', 'h', 'Total spend from events', 'The table <code>events (data TEXT)</code> holds JSON like <code>{{"user": "asha", "amount": 180}}</code>. Show each <code>user</code> and their total <code>amount</code> as <code>spent</code>, counting only events that have an amount.',
"""SELECT data ->> '$.user' AS user, SUM(data ->> '$.amount') AS spent FROM events WHERE data ->> '$.amount' IS NOT NULL GROUP BY user;""", db='', setup="""CREATE TABLE events (data TEXT);
INSERT INTO events VALUES ('{"user": "asha", "amount": 180}'), ('{"user": "ravi"}'), ('{"user": "asha", "amount": 1250}'), ('{"user": "ravi", "amount": 60}');""", hint="data ->> '$.user' and data ->> '$.amount', with WHERE ... IS NOT NULL and GROUP BY.", why='asha spent 180 + 1250 = 1430, ravi 60.')}
''', kw=['JSON', 'json_extract', '->>', 'json_each', 'json_group_array', 'json_object', 'jsonb', 'semi structured data'])
K.talk('json', '''Many apps store flexible data as JSON text in a column, such as settings, tags or the details of an event. Modern engines can look inside it with SQL.
In SQLite the arrow arrow operator, or json extract, pulls out a field as a normal value. json each turns an array into rows, so you can count how often
each item appears. json group array and json object go the other way and build JSON from rows, which is handy for sending data to a web page. JSON is
great for data whose shape varies, but fields you filter on every day usually deserve real columns. Think of a parcel with a packing list inside, which
you can read without unpacking everything.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Many hard looking questions are known patterns: rank and filter for top N, row number tricks for streaks, CASE inside SUM for pivots.</p>',
    '<p>Learn to recognise the pattern behind a question. Window functions, CTEs and conditional aggregation solve most reporting tasks in a single statement.</p>',
    '<p>Each pattern has trade offs: correlated subqueries versus window functions, JSON versus columns, deleting duplicates versus preventing them with constraints. Read the query plan (chapter 7.2) to choose.</p>',
    '<p>Semi structured data in relational engines is an active field: binary JSON formats, JSON path standards (SQL:2016 added SQL/JSON), and automatic shredding of JSON into hidden columns for speed in systems such as Snowflake and SingleStore.</p>')}
{deep('Unpivot', '<p>The reverse of a pivot turns columns back into rows. Portable SQL uses UNION ALL: <code>SELECT name, \'algebra\' AS subject, algebra AS score FROM report UNION ALL SELECT name, \'physics\', physics FROM report</code>. SQL Server, Oracle and DuckDB also have an UNPIVOT keyword.</p>')}
''', kw=['SQL patterns', 'SQL/JSON', 'unpivot', 'semi structured', 'pattern recognition'])
K.talk('levels', '''Here is the ladder for patterns. For a beginner, many hard looking questions are known patterns with known answers. At college level, learn to spot
the pattern behind a question, such as top N per group, streaks or pivots. At masters level, every pattern has trade offs, and the query plan helps you
choose between a subquery and a window function. At research level, people study how to store and search JSON quickly inside relational engines. Think
of a chess player who recognises an opening and already knows good replies.''')

K.quiz('e', 'Why can LIMIT 2 not give the top 2 per category?', ['It is slow', 'It limits the whole result, not each group', 'It needs ORDER BY', 'It removes NULLs'], 1, 'Whole result.', 'Rank per group, then filter.')
K.quiz('e', 'A pivot turns', ['Columns into tables', 'Row values into columns', 'Tables into views', 'NULLs into zeros'], 1, 'Rows to columns.', 'One column per value.')
K.quiz('e', 'Which finds duplicate emails?', ['GROUP BY email HAVING COUNT(*) > 1', 'WHERE email = email', 'DISTINCT email', 'ORDER BY email'], 0, 'Count per value.', 'Groups with more than one row are duplicates.')
K.quiz('e', 'In SQLite, data ->> \'$.user\' returns', ['JSON text', 'A plain SQL value', 'An error', 'The whole row'], 1, 'Double arrow.', '->> gives an SQL value, -> gives JSON.')
K.quiz('m', 'In the islands trick, inside one streak day − row_number is', ['Increasing', 'Constant', 'Zero', 'NULL'], 1, 'Same.', 'Both go up by 1 together.')
K.quiz('m', 'COUNT(CASE WHEN status = \'pending\' THEN 1 END) counts', ['All rows', 'Pending rows', 'NULL rows', 'Nothing'], 1, 'CASE gives NULL otherwise.', 'COUNT skips the NULLs.')
K.quiz('m', 'Top N with anyone tied for Nth place uses', ['ROW_NUMBER', 'RANK', 'COUNT', 'LAG'], 1, 'Ties included.', 'RANK keeps ties.')
K.quiz('m', 'json_each is used to', ['Validate JSON', 'Turn a JSON array into rows', 'Index JSON', 'Delete JSON'], 1, 'Array to rows.', 'One row per element.')
K.quiz('m', 'Why 100.0 instead of 100 in a percentage?', ['Style', 'To avoid integer division', 'Required by SQLite', 'Rounding'], 1, 'Real numbers.', 'Integer division would drop the fraction.')
K.quiz('h', 'After removing duplicates, what stops them coming back?', ['An index only', 'A UNIQUE constraint', 'A view', 'A trigger only'], 1, 'Prevention.', 'UNIQUE refuses future duplicates.')
K.quiz('x', 'Which standard added SQL/JSON functions?', ['SQL:1999', 'SQL:2003', 'SQL:2016', 'SQL:2023'], 2, '2016.', 'SQL:2016 added SQL/JSON.')

isl = value('', 'SELECT count(DISTINCT g) FROM (SELECT day - ROW_NUMBER() OVER (ORDER BY day) AS g FROM logins)', setup='CREATE TABLE logins (day INTEGER); INSERT INTO logins VALUES (1), (2), (3), (6), (7), (9), (10), (11), (12);')
K.calc('e', 'Login days 1, 2, 3, 6, 7, 9, 10, 11, 12. How many streaks are there?', str(isl), 'Count the runs.',
       ['1 to 3 is one run.', '6 to 7 is another, 9 to 12 a third.', eq(f'{isl} streaks')], check=isl)
K.calc('e', 'For day 6 (the 4th row), what is day − row_number?', '2', 'Subtract.',
       ['Day 6 is row 4.', 'Subtract the row number from the day.', eq('6 − 4 = 2')], check=2)
gaps = value('', 'SELECT SUM(nx - no - 1) FROM (SELECT no, LEAD(no) OVER (ORDER BY no) AS nx FROM seats) WHERE nx - no > 1', setup='CREATE TABLE seats (no INTEGER); INSERT INTO seats VALUES (1), (2), (3), (6), (7), (9), (10), (11), (12);')
K.calc('m', 'With seats 1, 2, 3, 6, 7, 9, 10, 11, 12 booked, how many seat numbers are missing between 1 and 12?', str(gaps), 'Count the holes.',
       ['Seats 4 and 5 are missing.', 'Seat 8 is missing.', eq(f'2 + 1 = {gaps}')], check=gaps)
dl = value('shop', "SELECT COUNT(*) FILTER (WHERE status = 'delivered') FROM orders WHERE customer_id = 1")
K.calc('m', 'In the pivot, how many delivered orders does Asha (customer 1) have?', str(dl), 'Her orders are 101, 103, 110.',
       ['101 is delivered.', '103 is shipped and 110 pending.', eq(f'{dl}')], check=dl)
st = value('shop', "SELECT SUM(CASE WHEN category = 'Stationery' THEN stock END) FROM products")
K.calc('m', 'What is the total stock of Stationery?', str(st), 'Three products.',
       ['Pencil box 40, Notebook 150.', 'Geometry set 70.', eq(f'40 + 150 + 70 = {st}')], check=st)
pct = value('shop', "SELECT ROUND(100.0 * SUM(stock) / (SELECT SUM(stock) FROM products), 1) FROM products WHERE category = 'Stationery'")
K.calc('m', 'What percent of all stock is Stationery, to one decimal place?', f'{pct}', 'Part over whole.',
       ['Stationery stock is 260.', 'All stock: 40 + 150 + 25 + 0 + 12 + 30 + 60 + 8 + 0 + 70 = 395.', eq(f'100 × 260 ÷ 395 ≈ {pct}')], check=pct, tol=0.05)
K.calc('h', 'Five signups with three distinct emails. How many rows does the dedupe DELETE remove?', '2', 'Rows minus distinct.',
       ['Keep one row per email.', 'Delete the rest.', eq('5 − 3 = 2')], check=2)
sp = value('', "SELECT SUM(data ->> '$.amount') FROM events WHERE data ->> '$.user' = 'asha'", setup="""CREATE TABLE events (data TEXT); INSERT INTO events VALUES ('{"user": "asha", "amount": 180}'), ('{"user": "ravi"}'), ('{"user": "asha", "amount": 1250}'), ('{"user": "ravi", "amount": 60}');""")
K.calc('h', 'In the JSON events lab, what is asha’s total amount?', str(sp), 'Add her amounts.',
       ['Her events have amounts 180 and 1250.', 'Add them.', eq(f'180 + 1250 = {sp}')], check=sp)

K.must('Top N per group', 'ROW_NUMBER or RANK with PARTITION BY in a CTE, then WHERE rn <= N outside.')
K.must('Gaps and islands', 'value − ROW_NUMBER is constant within a run. LEAD finds the gaps.')
K.must('Pivot', 'SUM or COUNT around CASE, or FILTER, one column per value. Columns must be known in advance.')
K.must('Duplicates', 'Find with GROUP BY ... HAVING COUNT(*) > 1, remove with ROW_NUMBER > 1, prevent with UNIQUE.')
K.must('JSON', '->> and json_extract read fields, json_each makes rows, json_group_array and json_object build JSON.')

T = K.topic(
    slug='sql-patterns', topic='sql-patterns', step=(6, 'Advanced queries', 'sql-advanced', 'Window functions, recursive queries and the patterns that solve real reporting problems.', 'Advanced'),
    title='Query patterns: top N, streaks, pivots and JSON', short='Query patterns', badge='6.3', minutes=45, added='2026-11-23',
    lead='Solve the questions that come up in every job and interview: top N per group, gaps and islands, pivots, duplicates, percent of total, and reading JSON with SQL.',
    desc='Top N per group with ROW_NUMBER, RANK and DISTINCT ON, gaps and islands with the row number difference and LEAD, pivoting with CASE and FILTER, finding and deleting duplicates, percent of total, JSON with ->>, json_each and json_group_array, unpivot.',
    summary='Top N per group, gaps and islands, pivots, duplicates, percent of total and JSON.',
    keywords=['top N per group', 'gaps and islands', 'pivot', 'duplicates', 'JSON', 'percent of total'],
    recap='<p>Rank and filter for top N, subtract row numbers for streaks, CASE inside aggregates for pivots, ROW_NUMBER for duplicates, and JSON functions for flexible data.</p>')
