# Chapter 9.1: exam and interview revision for the whole SQL course: a map of the chapters, school board style questions,
# the classic interview queries (second highest salary, employees earning more than their manager, customers with no
# orders, department top earners, duplicates, running totals), a university style design question, and a mock paper of
# hands on tasks checked by the real SQLite engine.
# Sources: the earlier chapters of this course and their sources (sqlite.org, postgresql.org, MySQL and SQL Server docs).
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('map', 'The whole course on one page', f'''
<p>Use this map to find where each kind of exam or interview question is taught, then revise that chapter’s Summary tab.</p>
{table(['Question asks you to', 'Key idea', 'Chapter'], [
    ['pick columns, filter, sort', 'SELECT, WHERE, ORDER BY, LIMIT', '1.2, 1.3'],
    ['handle missing values', 'IS NULL, COALESCE, three valued logic', '2.2'],
    ['count, total, average per group', 'GROUP BY, HAVING', '2.3'],
    ['combine tables', 'INNER, LEFT, self and anti joins', '3.1, 3.2'],
    ['answer a question inside a question', 'subqueries, EXISTS, IN', '3.3'],
    ['create and change tables and rows', 'CREATE, ALTER, INSERT, UPDATE, DELETE, UPSERT', '4.1, 4.2'],
    ['simplify long queries', 'views and CTEs', '4.3'],
    ['design or normalize a schema', 'keys, functional dependencies, 1NF to BCNF, ER diagrams', '5.1, 5.2'],
    ['rank, running totals, previous row', 'window functions', '6.1'],
    ['hierarchies and series', 'recursive CTEs', '6.2'],
    ['top N per group, streaks, pivots', 'query patterns', '6.3'],
    ['make it faster', 'indexes, plans, sargable conditions', '7.1, 7.2'],
    ['keep data correct with many users', 'ACID, isolation, locks', '7.3'],
    ['triggers, security, scale, engines', 'triggers, injection, sharding, dialects', '8.1 to 8.4']])}
{pk('sqpipe')}
{note('In almost every written exam, first say the logical order: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT. It explains half of the tricky questions on aliases, WHERE versus HAVING and window functions.', 'tip')}
''', kw=['revision map', 'syllabus', 'exam topics', 'logical order', 'course summary'])
K.talk('map', '''This last chapter is for revision before an exam or an interview. The table maps each kind of question to the chapter that teaches it, from simple
filters and sorting, through grouping, joins and subqueries, to design, window functions, performance, transactions and security. The animation replays
the logical order of a query, FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY and LIMIT, because that single idea explains so many tricky questions.
Revise one row of the table at a time, and use the Summary tab of each chapter as your quick notes. Think of a train map that shows every station on one
page before a long journey.''')

K.lesson('school', 'School and first year questions', f'''
<p>School boards and first year courses ask short, precise questions. Here are typical ones with model answers on the school database.</p>
{K.sql('q1', """-- Q1. Display the names of students of class 9, in alphabetical order.
SELECT name FROM students WHERE class = 9 ORDER BY name;""", db='school', title='Filter and sort', notes={2: 'WHERE for the condition, ORDER BY for alphabetical order.'})}
{K.sql('q2', """-- Q2. Display each class and the number of students in it.
SELECT class, COUNT(*) AS students FROM students GROUP BY class;""", db='school', title='Count per group', notes={2: 'One row per class.'})}
{K.sql('q3', """-- Q3. Display the average score of each course, rounded to 1 decimal, only where it is above 80.
SELECT course_id, ROUND(AVG(score), 1) AS avg_score
FROM marks GROUP BY course_id HAVING AVG(score) > 80;""", db='school', title='HAVING filters groups', notes={3: 'The NULL score is ignored by AVG.'})}
{K.sql('q4', """-- Q4. Display the names of students who live in a city starting with P.
SELECT name, city FROM students WHERE city LIKE 'P%';""", db='school', title='Patterns with LIKE', notes={2: '% matches any run of characters.'})}
{table(['Short answer question', 'Model answer'], [
    ['Difference between WHERE and HAVING', 'WHERE filters rows before grouping, HAVING filters groups after grouping, and only HAVING can use aggregates'],
    ['Difference between DELETE, DROP and TRUNCATE', 'DELETE removes chosen rows, DROP removes the table itself, TRUNCATE removes all rows quickly (SQLite uses DELETE without WHERE)'],
    ['Primary key versus unique key', 'both refuse duplicates, a table has one primary key and it cannot be NULL, it may have many unique keys'],
    ['What is a foreign key', 'a column whose values must exist in the primary key of another table'],
    ['DDL versus DML', 'DDL defines structure (CREATE, ALTER, DROP), DML changes data (INSERT, UPDATE, DELETE)'],
    ['What does COUNT(column) skip', 'NULL values, while COUNT(*) counts every row']])}
{K.lab('l-s1', 'e', 'Students without a city', 'From the school database, display the <code>name</code> of every student whose city is not recorded.',
"""SELECT name FROM students WHERE city IS NULL;""", db='school', hint='IS NULL, never = NULL.', why='Farhan is the only student with no city.')}
''', kw=['school SQL questions', 'CBSE', 'board exam', 'WHERE vs HAVING', 'DELETE vs DROP', 'DDL vs DML', 'short answers'])
K.talk('school', '''School boards and first year courses ask short, exact questions. Show the names of class nine students in alphabetical order. Count the students in
each class. Show courses whose average is above eighty, which needs HAVING because the condition uses an aggregate. Find students whose city starts with P
using LIKE. Short answer questions come up every year too, such as the difference between WHERE and HAVING, between DELETE, DROP and TRUNCATE, and between
a primary key and a unique key. The table on this page gives a model answer for each. Think of practising the past papers your teachers hand out before
the board exam.''')

K.lesson('interview', 'Classic interview queries', f'''
<p>These questions appear again and again in data and developer interviews. Each one tests a pattern from the course. They run on the company database.</p>
{K.sql('second', """-- Second highest salary
SELECT MAX(salary) AS second_highest FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);""", db='company', title='Second highest salary', notes={3: 'The highest salary below the overall highest. DENSE_RANK = 2 also works, and generalises to N.'})}
{K.sql('nth', """-- Nth highest distinct salary, here N = 3
SELECT DISTINCT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS r FROM employees
) WHERE r = 3;""", db='company', title='Nth highest with DENSE_RANK', notes={3: 'DENSE_RANK gives ties the same number without gaps, which is what "Nth highest distinct" means.'})}
{K.sql('mgr', """-- Employees who earn more than their manager
SELECT e.name, e.salary, m.name AS manager, m.salary AS manager_salary
FROM employees e JOIN employees m ON m.id = e.manager_id
WHERE e.salary > m.salary;""", db='company', title='Self join: earning more than the manager', notes={3: 'The same table twice: e for the employee, m for the manager.'})}
{K.sql('nodept', """-- Departments with no employees
SELECT d.name FROM departments d
WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.dept_id = d.id);""", db='company', title='Anti join with NOT EXISTS', notes={3: 'Research has nobody yet. NOT EXISTS is safe even when dept_id has NULLs, unlike NOT IN.'})}
{K.sql('deptmax', """-- Highest paid employee in each department, ties included
SELECT dept_id, name, salary FROM (
  SELECT dept_id, name, salary, RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS r
  FROM employees WHERE dept_id IS NOT NULL
) WHERE r = 1;""", db='company', title='Top earner per department', notes={3: 'RANK keeps ties. ROW_NUMBER would pick exactly one.'})}
{table(['Question', 'Pattern', 'Trap to mention'], [
    ['Second or Nth highest', 'MAX below MAX, or DENSE_RANK', 'ties and NULLs'],
    ['Earn more than manager', 'self join', 'the top boss has no manager'],
    ['Customers with no orders', 'LEFT JOIN ... IS NULL or NOT EXISTS', 'NOT IN with a NULL returns nothing'],
    ['Duplicate emails', 'GROUP BY ... HAVING COUNT(*) > 1', 'case and spaces in emails'],
    ['Running total', 'SUM() OVER (ORDER BY ...)', 'ties under the default RANGE frame'],
    ['Top N per group', 'ROW_NUMBER or RANK in a CTE', 'which one when ties exist']])}
{K.lab('l-i1', 'm', 'Second highest salary', 'From the company database, return one value <code>second_highest</code>: the second highest distinct salary.',
"""SELECT MAX(salary) AS second_highest FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);""", db='company', hint='The MAX of salaries below the overall MAX.', why='250000 is the highest, so the answer is 150000.')}
{K.lab('l-i2', 'm', 'Earns more than their manager', 'Imran has just been promoted to a salary of 160000. Show the <code>name</code> of every employee who now earns more than their manager.',
"""SELECT e.name FROM employees e JOIN employees m ON m.id = e.manager_id WHERE e.salary > m.salary;""", db='company', setup="UPDATE employees SET salary = 160000 WHERE name = 'Imran';", hint='Join employees to itself on m.id = e.manager_id, then compare salaries.', why='Imran (160000) now earns more than his manager Rahul (150000).')}
{K.lab('l-i3', 'h', 'Department payroll share', 'Show each department <code>name</code> and <code>pct</code>, its share of total salaries (employees with a department only), as a percentage rounded to 1 decimal.',
"""SELECT d.name, ROUND(100.0 * SUM(e.salary) / SUM(SUM(e.salary)) OVER (), 1) AS pct FROM employees e JOIN departments d ON d.id = e.dept_id GROUP BY d.id;""", db='company', hint='SUM per department divided by SUM(SUM(salary)) OVER ().', why='A window over a GROUP BY gives the grand total on every row.')}
''', kw=['SQL interview questions', 'second highest salary', 'Nth highest', 'self join', 'anti join', 'top per group', 'interview traps'])
K.talk('interview', '''These questions come up in interview after interview. Find the second highest salary, which is the largest salary below the largest, or the row
with dense rank two. Find employees who earn more than their manager, which needs a self join of employees to employees. Find departments or customers
with nothing linked, which needs NOT EXISTS or a LEFT JOIN with IS NULL, never NOT IN when NULLs are possible. Find the top earner in each department
with RANK in a subquery. Interviewers love to hear you mention the traps, such as ties, NULLs and the boss with no manager. Think of a driving test where
the examiner checks the same few manoeuvres every time.''')

K.lesson('design', 'A design question, answered', f'''
<p>University papers often ask you to design a schema from a story, then normalize it and write queries. Here is a full answer.</p>
{scene('the question', '<p>"A college runs clubs. Each club has a name and a faculty adviser. Students can join many clubs, and each membership records the joining date and the student’s role (member, secretary, president). Each club has at most one president. Design the tables, state the keys, show the schema is in 3NF, and write a query listing each club with its president."</p>')}
{K.sql('clubs', """CREATE TABLE advisers (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE clubs (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, adviser_id INTEGER NOT NULL REFERENCES advisers(id));
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE memberships (
  student_id INTEGER REFERENCES students(id),
  club_id INTEGER REFERENCES clubs(id),
  joined_on TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('member', 'secretary', 'president')),
  PRIMARY KEY (student_id, club_id));
CREATE UNIQUE INDEX one_president ON memberships(club_id) WHERE role = 'president';
INSERT INTO advisers VALUES (1, 'Dr Rao'), (2, 'Dr Iyer');
INSERT INTO clubs VALUES (1, 'Chess', 1), (2, 'Music', 2);
INSERT INTO students VALUES (1, 'Anu'), (2, 'Bala'), (3, 'Chitra');
INSERT INTO memberships VALUES (1, 1, '2025-07-01', 'president'), (2, 1, '2025-07-03', 'member'), (2, 2, '2025-07-05', 'president'), (3, 2, '2025-07-06', 'secretary');
SELECT c.name AS club, a.name AS adviser, s.name AS president
FROM clubs c JOIN advisers a ON a.id = c.adviser_id
LEFT JOIN memberships m ON m.club_id = c.id AND m.role = 'president'
LEFT JOIN students s ON s.id = m.student_id;""", db='', title='The model answer, runnable', notes={4: 'Many to many between students and clubs, with its own facts.', 10: 'A partial unique index enforces "at most one president per club".', 16: 'LEFT JOIN keeps a club even if it has no president yet.'})}
{steps('Why the schema is in 3NF', [
    'Every cell holds one value, so it is in 1NF.',
    'memberships has key (student_id, club_id), and joined_on and role depend on the whole pair, so it is in 2NF.',
    'The adviser’s name depends on the adviser, so it lives in advisers, not in clubs. No non key column depends on another non key column, so it is in 3NF.',
    'Business rules are constraints: role is checked, one president per club is a partial unique index.'])}
''', kw=['schema design question', 'model answer', 'partial unique index', '3NF proof', 'university exam'])
K.talk('design', '''University papers often give a story and ask for a schema. Here the college has clubs, advisers and students, and students join many clubs with a
date and a role. So there are four tables, and memberships links students to clubs with a composite primary key. A check limits the role to three words,
and a partial unique index makes sure each club has at most one president. To show third normal form, say that every cell holds one value, every column
depends on the whole key, and nothing depends on a column that is not a key. Then write the query, with LEFT JOIN so clubs without a president still
appear. Think of an architect presenting a plan and explaining every room.''')

K.lesson('mock', 'Mock paper: hands on tasks', f'''
<p>Ten minutes each. Every task is checked by the real SQLite engine, just like the labs in each chapter. Try them without looking back, then use Show answer.</p>
{K.lab('l-m1', 'e', 'Task 1: products to reorder', 'Show the <code>name</code> and <code>stock</code> of products with fewer than 20 in stock, lowest stock first, then by name.',
"""SELECT name, stock FROM products WHERE stock < 20 ORDER BY stock, name;""", hint='WHERE stock < 20 ORDER BY stock, name', why='Two products have 0 stock, so name breaks the tie.', ordered=True)}
{K.lab('l-m2', 'm', 'Task 2: revenue per order', 'Show each order <code>id</code> and <code>revenue</code> (sum of qty × price), for orders that are not cancelled, highest revenue first.',
"""SELECT o.id, SUM(oi.qty * p.price) AS revenue FROM orders o JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE o.status <> 'cancelled' GROUP BY o.id ORDER BY revenue DESC, o.id;""", hint='Join three tables, filter, GROUP BY o.id, ORDER BY revenue DESC.', why='A three table join and a group by, the backbone of most reports.', ordered=True)}
{K.lab('l-m3', 'm', 'Task 3: customers who never ordered', 'Show the <code>name</code> of every customer with no orders.',
"""SELECT name FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);""", hint='NOT EXISTS, or LEFT JOIN with IS NULL.', why='Kabir, Arjun and Vikram have never ordered.')}
{K.lab('l-m4', 'h', 'Task 4: each customer’s latest order', 'Show each customer’s <code>name</code> with the <code>id</code> and <code>order_date</code> of their most recent order. Leave out customers without orders.',
"""WITH r AS (SELECT customer_id, id, order_date, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn FROM orders)
SELECT c.name, r.id, r.order_date FROM r JOIN customers c ON c.id = r.customer_id WHERE r.rn = 1;""", hint='ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC), keep rn = 1.', why='Top 1 per group with a window function.')}
{K.lab('l-m5', 'h', 'Task 5: the whole reporting chain', 'From the company database, show every employee’s <code>name</code> and <code>level</code> in the org chart, where Priya (no manager) is level 0.',
"""WITH RECURSIVE c(id, name, level) AS (SELECT id, name, 0 FROM employees WHERE manager_id IS NULL UNION ALL SELECT e.id, e.name, c.level + 1 FROM employees e JOIN c ON e.manager_id = c.id)
SELECT name, level FROM c;""", db='company', hint='A recursive CTE starting from manager_id IS NULL.', why='Each round goes one level down the chart.')}
''', kw=['mock test', 'practice paper', 'hands on SQL', 'timed tasks', 'exam practice'])
K.talk('mock', '''Here is a mock paper of hands on tasks, each checked by the real SQLite engine. They climb from easy to hard. Find products to reorder and sort them.
Work out revenue per order with a three table join. List customers who never ordered with NOT EXISTS. Find each customer's latest order with a window
function, and finally list the whole org chart with a recursive query. Give yourself about ten minutes per task, try without looking back, and only then
press Show answer. If a task beats you, the hint names the chapter idea to revise. Think of a sports practice match played under real match rules.''')

K.lesson('levels', 'Where to go next', f'''
{ladder(
    '<p>You can ask a database clear questions: filter, sort, group and join. Keep practising on real data you care about, such as your expenses or a sports table.</p>',
    '<p>You can design schemas, write window functions and recursive queries, read plans and use transactions. Build a small app with PostgreSQL or SQLite and write its queries by hand.</p>',
    '<p>Go deeper into internals: read the SQLite architecture pages, PostgreSQL’s planner and MVCC documentation, and Database System Concepts or the CMU database course lectures by Andy Pavlo.</p>',
    '<p>Research directions: query optimization, transaction processing at scale, learned database components, and natural language to SQL. Read papers from SIGMOD, VLDB and CIDR, starting with the classics cited in each chapter here.</p>')}
{deep('Practice sites and datasets', '<p>Practise with public datasets such as the Chinook music store or Northwind sample databases, government open data portals, and interview practice sites that offer SQL problems. Run everything in a local SQLite or PostgreSQL, so you also learn to load data and create indexes.</p>')}
''', kw=['next steps', 'practice', 'Chinook', 'Northwind', 'CMU database course', 'SIGMOD', 'VLDB'])
K.talk('levels', '''You have reached the end of the course. If you are a beginner, keep asking real questions of data you care about, like your expenses or a cricket
table. If you are at college level, build a small app and write its queries by hand. To go deeper, read how SQLite and PostgreSQL work inside, and follow
a university database course. For research, read the classic papers cited in each chapter, then new ones from the big database conferences. Keep the
playground open and practise a little every day. Think of learning to swim, where a few lengths each day beat one long swim a month.''')

for q in [
    ('e', 'Which clause filters groups after GROUP BY?', ['WHERE', 'HAVING', 'ORDER BY', 'LIMIT'], 1, 'Groups.', 'HAVING filters groups.'),
    ('e', 'COUNT(*) versus COUNT(email)', ['Same always', 'COUNT(email) skips NULL emails', 'COUNT(*) skips NULLs', 'Both skip duplicates'], 1, 'NULLs.', 'COUNT(column) ignores NULL.'),
    ('e', 'Which join keeps every row of the left table?', ['INNER', 'LEFT', 'CROSS', 'NATURAL'], 1, 'Left.', 'Unmatched left rows get NULLs.'),
    ('e', 'DROP TABLE removes', ['Some rows', 'The table and all its rows', 'Only the index', 'Nothing'], 1, 'Gone.', 'The whole table.'),
    ('m', 'Which runs first in the logical order?', ['SELECT', 'WHERE', 'ORDER BY', 'HAVING'], 1, 'Before grouping.', 'FROM, then WHERE.'),
    ('m', 'NOT IN (subquery) returns no rows when the subquery', ['Is empty', 'Contains a NULL', 'Has duplicates', 'Is sorted'], 1, 'Unknown.', 'Use NOT EXISTS.'),
    ('m', 'Salaries 9, 8, 8, 7. The 2nd highest distinct salary is', ['9', '8', '7', '8 and 8'], 1, 'Distinct.', 'DENSE_RANK = 2 gives 8.'),
    ('m', 'A covering index helps because', ['It is unique', 'The table is not read', 'It sorts randomly', 'It locks rows'], 1, 'Index only.', 'All needed columns are in the index.'),
    ('m', '3NF removes', ['Repeating groups', 'Partial dependencies', 'Transitive dependencies', 'Foreign keys'], 2, 'Non key to non key.', 'Transitive dependencies.'),
    ('m', 'A lost update is prevented by', ['SET balance = 600', 'SET balance = balance + 100', 'A view', 'An index'], 1, 'Atomic.', 'Let the database do the arithmetic.'),
    ('h', 'Which keeps ties for top N per group?', ['ROW_NUMBER', 'RANK', 'NTILE', 'LAG'], 1, 'Ties.', 'RANK shares ranks.'),
    ('h', 'The main defence against SQL injection', ['Escaping by hand', 'Parameterized queries', 'Long table names', 'Views'], 1, 'Parameters.', 'Values never become code.'),
    ('x', 'Snapshot isolation can still allow', ['Dirty reads', 'Write skew', 'Lost commits', 'Syntax errors'], 1, 'Disjoint writes.', 'Write skew.')]:
    K.quiz(*q)

sec = value('company', 'SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees)')
K.calc('e', 'What is the second highest salary at Orbit Tech?', str(sec), 'Below the maximum.',
       ['The highest is 250000 (Priya).', 'The next is 150000 (Rahul).', eq(f'{sec}')], check=sec)
c9 = value('school', 'SELECT count(*) FROM students WHERE class = 9')
K.calc('e', 'How many students are in class 9?', str(c9), 'Count the rows.',
       ['Chitra, Dev and Hari are in class 9.', 'Count them.', eq(f'{c9} students')], check=c9)
th = value('company', 'SELECT DISTINCT salary FROM (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS r FROM employees) WHERE r = 3')
K.calc('m', 'What is the 3rd highest distinct salary?', str(th), 'DENSE_RANK = 3.',
       ['Distinct salaries from the top: 250000, 150000, 140000.', 'The third is 140000.', eq(f'{th}')], check=th)
nm = value('company', 'SELECT count(*) FROM employees e JOIN employees m ON m.id = e.manager_id WHERE e.salary > m.salary')
K.calc('m', 'How many employees earn more than their manager?', str(nm), 'Self join and compare.',
       ['Compare each salary with the manager’s salary.', 'Every manager here earns more than each of their reports.', eq(f'{nm}')], check=nm)
nod = value('shop', 'SELECT count(*) FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)')
K.calc('m', 'How many customers have never ordered?', str(nod), 'Anti join.',
       ['Customers 4, 6 and 8 have no orders.', 'Count them.', eq(f'{nod} customers')], check=nod)
rv = value('shop', "SELECT MAX(r) FROM (SELECT SUM(oi.qty * p.price) AS r FROM orders o JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE o.status <> 'cancelled' GROUP BY o.id)")
K.calc('m', 'What is the highest revenue of a single order (cancelled left out)?', str(rv), 'Compute per order.',
       ['Order 107: 1499 + 699 = 2198.', 'Order 104: 2 × 699 + 10 × 60 = 1998, order 102: 1499.', eq(f'highest = {rv}')], check=rv)
av = value('school', 'SELECT ROUND(AVG(score), 1) FROM marks WHERE course_id = 4')
K.calc('h', 'What is the average Chemistry (course 4) score, rounded to 1 decimal?', str(av), 'NULL is skipped.',
       ['Scores 81, NULL and 87.', 'AVG skips NULL: (81 + 87) ÷ 2.', eq(f'{av}')], check=av)
K.calc('h', 'A 3 table schema has tables of 10, 1,000 and 1,000,000 rows, joined by indexed keys starting from the 10 row table. About how many index lookups does a nested loop need if each row matches one row in the next table?', '20', 'One lookup per row per step.',
       ['10 rows look up 10 rows in the second table.', 'Those 10 rows look up 10 rows in the third.', eq('10 + 10 = 20 lookups')], check=20)

K.must('Logical order', 'FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT explains aliases, HAVING and window function rules.')
K.must('Interview patterns', 'Second highest, self join, anti join, top N per group, duplicates, running totals, recursive chains.')
K.must('Traps', 'NULLs in NOT IN, ties in ranking, COUNT(column) skipping NULLs, missing WHERE in UPDATE and DELETE.')
K.must('Design answers', 'Entities, keys, relationships, constraints for rules, then argue 1NF, 2NF and 3NF.')
K.must('Keep practising', 'Use the playground daily and real datasets. Revise each chapter’s Summary tab before an exam.')

T = K.topic(
    slug='sql-exam', topic='sql-exam', kind='revision',
    step=(9, 'Exam and interview revision', 'sql-revision', 'Revise the whole course with school questions, classic interview queries, a design answer and a mock paper.', 'All levels'),
    title='Exam and interview revision', short='Exam revision', badge='9.1', minutes=60, added='2026-11-23',
    lead='Revise the whole course: a chapter map, school board questions with model answers, the classic interview queries and their traps, a full design answer, and a mock paper checked by SQLite.',
    desc='Course map, logical order, school and first year SQL questions, WHERE versus HAVING, DELETE versus DROP, second and Nth highest salary, self join, anti join, top per group, schema design model answer, mock paper with hands on tasks.',
    summary='A chapter map, school questions, interview queries, a design answer and a mock paper.',
    keywords=['SQL exam', 'SQL interview', 'second highest salary', 'mock test', 'revision', 'model answers'],
    recap='<p>Map each question to its pattern, mention the traps, and practise with the engine until the patterns feel natural.</p>')
