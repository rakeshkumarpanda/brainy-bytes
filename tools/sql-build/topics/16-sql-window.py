# Chapter 6.1: window functions: OVER, PARTITION BY, ORDER BY inside OVER, ranking (ROW_NUMBER, RANK, DENSE_RANK, NTILE,
# PERCENT_RANK, CUME_DIST), offset functions (LAG, LEAD, FIRST_VALUE, LAST_VALUE, NTH_VALUE), aggregates as windows,
# frames (ROWS, RANGE, GROUPS, default frame), named WINDOW clause, and why they cannot go in WHERE.
# Sources: sqlite.org windowfunctions.html (added in 3.25.0, 2018, default frame RANGE BETWEEN UNBOUNDED PRECEDING AND
# CURRENT ROW, GROUPS and EXCLUDE), postgresql.org tutorial-window.html and functions-window.html, MySQL 8.0 window functions.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('over', 'OVER: an answer for every row', f'''
<p>GROUP BY folds many rows into one. Sometimes you want a group answer <b>next to each row</b>: each employee with their department’s average, or each order with a running total. A <b>window function</b> does that. The word <code>OVER</code> turns an ordinary function into a window function.</p>
{fxs(fx('Window function', '<code>function(...) OVER (PARTITION BY a ORDER BY b)</code>', 'PARTITION BY makes groups, ORDER BY sorts inside each group. Both are optional.', key=True),
     fx('Whole table', '<code>AVG(salary) OVER ()</code>', 'Empty brackets: the window is every row of the result.'))}
{K.sql('avg', """SELECT name, dept_id, salary,
       AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg,
       salary - AVG(salary) OVER (PARTITION BY dept_id) AS diff
FROM employees
WHERE dept_id IS NOT NULL
ORDER BY dept_id, salary DESC;""", db='company', title='Each employee beside their department’s average', notes={2: 'One average per department, repeated on every row of that department.', 3: 'Compare each person with their own group, impossible with plain GROUP BY.'})}
{table(['', 'GROUP BY', 'Window function'], [
    ['Rows in the result', 'one per group', 'one per input row'],
    ['Can show row details', 'only grouped columns', 'yes, every column'],
    ['Written', 'GROUP BY dept_id', 'OVER (PARTITION BY dept_id)']])}
{K.lab('l-share', 'e', 'Share of the company payroll', 'From the company database, show each employee’s <code>name</code>, <code>salary</code> and <code>total</code>, the sum of all salaries, on every row.',
"""SELECT name, salary, SUM(salary) OVER () AS total FROM employees;""", db='company', hint='SUM(salary) OVER () with empty brackets.', why='Empty OVER () makes the whole table one window.')}
''', kw=['window function', 'OVER', 'PARTITION BY', 'analytic function', 'group answer per row'])
K.talk('over', '''GROUP BY folds many rows into one answer per group. Sometimes you want the group answer next to every row instead, such as each employee beside
the average salary of their department. That is what a window function does. You write an ordinary function, like AVG, and add the word OVER with
brackets. Inside the brackets, PARTITION BY says how to split the rows into groups, and every row keeps its own line. With empty brackets the window
is the whole table. Now you can compare each person with their own group in a single query, which plain GROUP BY cannot do. Think of a class photo
where each child's height is written next to the class average.''')

K.lesson('rank', 'Ranking: ROW_NUMBER, RANK and DENSE_RANK', f'''
<p>Add <code>ORDER BY</code> inside OVER and the function can number or rank rows. The three ranking functions differ only in how they treat ties.</p>
{pk('sqwin')}
{K.sql('ranks', """SELECT name, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
       RANK()       OVER (ORDER BY salary DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS dense
FROM employees
WHERE dept_id = 2;""", db='company', title='Joseph and Kiran earn the same', notes={2: 'Ties get different numbers, in no promised order.', 3: 'Ties share 2, and the next rank is 4: a gap.', 4: 'Ties share 2, and the next rank is 3: no gap.'})}
{table(['Function', 'Salaries 140, 70, 70, 60', 'Use it for'], [
    ['ROW_NUMBER()', '1, 2, 3, 4', 'picking exactly one row per group, paging'],
    ['RANK()', '1, 2, 2, 4', 'sports style positions'],
    ['DENSE_RANK()', '1, 2, 2, 3', 'the second highest distinct value'],
    ['NTILE(4)', 'splits rows into 4 nearly equal buckets', 'quartiles'],
    ['PERCENT_RANK(), CUME_DIST()', 'relative position from 0 to 1', 'percentiles']])}
{K.sql('perdept', """SELECT name, dept_id, salary,
       RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rank_in_dept
FROM employees
WHERE dept_id IS NOT NULL
ORDER BY dept_id, rank_in_dept;""", db='company', title='Rank inside each department', notes={2: 'Ranking restarts at 1 in every partition.'})}
{note('ROW_NUMBER breaks ties in no guaranteed order. Add a tie breaker such as id to the ORDER BY when the result must be the same every time.', 'warn')}
{K.lab('l-rank', 'm', 'Rank the marks', 'From the school database, show <code>student_id</code>, <code>score</code> and <code>pos</code>, the DENSE_RANK of the score from highest to lowest, for course 1.',
"""SELECT student_id, score, DENSE_RANK() OVER (ORDER BY score DESC) AS pos FROM marks WHERE course_id = 1;""", db='school', hint='DENSE_RANK() OVER (ORDER BY score DESC), with WHERE course_id = 1.', why='WHERE runs first, then the ranking runs over the four Algebra marks.')}
''', kw=['ROW_NUMBER', 'RANK', 'DENSE_RANK', 'NTILE', 'PERCENT_RANK', 'CUME_DIST', 'ties', 'ranking'])
K.talk('rank', '''Put ORDER BY inside the OVER brackets and the function can number or rank rows. ROW_NUMBER gives one, two, three, four, even when two salaries
tie. RANK gives tied rows the same rank and then skips, so you get one, two, two, four, like positions in a race. DENSE_RANK also shares the rank but
does not skip, giving one, two, two, three. Add PARTITION BY and the numbering restarts in each department. In the animation, pick each function and
watch Pip light up the rows it compares for every employee. Joseph and Kiran earn the same, so watch what happens to them. Think of a sports day where
two runners cross the line together.''')

K.lesson('offset', 'Running totals, LAG and LEAD', f'''
<p>With ORDER BY, an aggregate such as SUM becomes a <b>running</b> aggregate: it adds rows from the start of the partition up to the current row. LAG and LEAD reach back or forward to a neighbouring row.</p>
{K.sql('running', """WITH daily AS (
  SELECT o.order_date, SUM(oi.qty * p.price) AS sales
  FROM orders o JOIN order_items oi ON oi.order_id = o.id
  JOIN products p ON p.id = oi.product_id
  WHERE o.status <> 'cancelled'
  GROUP BY o.order_date
)
SELECT order_date, sales,
       SUM(sales) OVER (ORDER BY order_date) AS running_total,
       sales - LAG(sales) OVER (ORDER BY order_date) AS change
FROM daily;""", title='Sales per day with a running total and the change from the day before', notes={9: 'Adds every day up to this one.', 10: 'LAG gives the previous day’s sales, NULL on the first day.'})}
{table(['Function', 'Returns'], [
    ['LAG(x) and LAG(x, n, default)', 'x from the row n places before, default when there is none'],
    ['LEAD(x)', 'x from the next row'],
    ['FIRST_VALUE(x), LAST_VALUE(x)', 'x from the first or last row of the frame'],
    ['NTH_VALUE(x, n)', 'x from row n of the frame']])}
{K.sql('lead', """SELECT name, hired,
       LEAD(name) OVER (ORDER BY hired) AS next_hire,
       FIRST_VALUE(name) OVER (ORDER BY hired) AS first_hire
FROM employees ORDER BY hired;""", db='company', title='Who joined next, and who was first', notes={2: 'The next person by hire date, NULL for the newest.', 3: 'The first row of the frame is always the earliest hire.'})}
{K.lab('l-running', 'm', 'Running count of customers', 'Show each customer’s <code>name</code>, <code>joined</code> date and <code>so_far</code>, the number of customers who had joined up to that date, ordered by joined.',
"""SELECT name, joined, COUNT(*) OVER (ORDER BY joined) AS so_far FROM customers ORDER BY joined;""", hint='COUNT(*) OVER (ORDER BY joined).', why='With ORDER BY, COUNT counts from the first row up to the current one.', ordered=True)}
{K.lab('l-lag', 'h', 'Days between orders', 'For customer 1, show each order <code>id</code>, <code>order_date</code> and <code>gap</code>, the number of days since that customer’s previous order (NULL for the first). Use julianday.',
"""SELECT id, order_date, julianday(order_date) - julianday(LAG(order_date) OVER (ORDER BY order_date)) AS gap FROM orders WHERE customer_id = 1;""", hint='julianday(order_date) - julianday(LAG(order_date) OVER (ORDER BY order_date))', why='LAG fetches the previous date, julianday turns both dates into day numbers.')}
''', kw=['running total', 'cumulative sum', 'LAG', 'LEAD', 'FIRST_VALUE', 'LAST_VALUE', 'NTH_VALUE', 'previous row'])
K.talk('offset', '''With ORDER BY inside OVER, SUM turns into a running total. For each row it adds everything from the start of the group up to that row, which is how
bank statements show a balance after every transaction. LAG reaches back to the row before, and LEAD looks ahead to the row after, so you can work out
the change from yesterday or the time until the next order. The first row has nothing before it, so LAG gives NULL there unless you pass a default.
FIRST VALUE and LAST VALUE pick values from the ends of the window. Think of a cricket scoreboard that shows the runs of each over and the total so far.''')

K.lesson('frames', 'Frames, named windows and the WHERE trap', f'''
<p>The <b>frame</b> is the exact set of rows an aggregate sees for the current row. You can set it yourself.</p>
{table(['Frame', 'Meaning'], [
    ['no ORDER BY', 'the whole partition'],
    ['ORDER BY only (default)', 'RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW: start to here, tied rows included'],
    ['ROWS BETWEEN 2 PRECEDING AND CURRENT ROW', 'this row and the 2 before it: a 3 row moving window'],
    ['ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING', 'the whole partition, needed for LAST_VALUE to mean the true last row'],
    ['GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW', 'this group of tied rows and the group before (SQLite, PostgreSQL)']])}
{K.sql('moving', """SELECT student_id, score,
       ROUND(AVG(score) OVER (ORDER BY student_id
             ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING), 1) AS smooth
FROM marks WHERE course_id = 1;""", db='school', title='A moving average over three rows', notes={3: 'The row before, this row and the row after.'})}
{K.sql('named', """SELECT name, salary,
       RANK() OVER w AS rnk,
       SUM(salary) OVER w AS running
FROM employees
WHERE dept_id = 1
WINDOW w AS (ORDER BY salary DESC);""", db='company', title='WINDOW names a window once', notes={6: 'Both functions reuse w.'})}
{K.sql('trap', """SELECT name, RANK() OVER (ORDER BY salary DESC) AS rnk
FROM employees
WHERE RANK() OVER (ORDER BY salary DESC) <= 3;""", db='company', title='Window functions are not allowed in WHERE', err=True, notes={3: 'WHERE runs before window functions are computed, so SQLite refuses.'})}
{K.sql('fix', """SELECT name, salary FROM (
  SELECT name, salary, RANK() OVER (ORDER BY salary DESC) AS rnk
  FROM employees
) WHERE rnk <= 3;""", db='company', title='The fix: rank in a subquery, filter outside', notes={4: 'The outer WHERE can read the finished ranks.'})}
{note('In the logical order of a query, window functions run after WHERE, GROUP BY and HAVING, and before ORDER BY and LIMIT. That is why they can use aggregates but cannot be filtered by WHERE in the same SELECT.', 'tip')}
''', kw=['window frame', 'ROWS BETWEEN', 'RANGE', 'GROUPS', 'moving average', 'WINDOW clause', 'window in WHERE', 'QUALIFY'])
K.talk('frames', '''The frame is the exact set of rows an aggregate looks at for the current row. With no ORDER BY, it is the whole group. With ORDER BY, the default
frame runs from the start of the group to the current row, including any rows tied with it. You can set your own, such as ROWS BETWEEN one preceding
and one following, which gives a three row moving average that smooths out jumps. The WINDOW clause lets you name a window once and reuse it. One trap
catches everyone. Window functions are computed after WHERE, so you cannot filter on them there. Rank inside a subquery or CTE, then filter outside.
Think of a magnifying glass that slides along a line of numbers.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A window function writes a group answer, such as a rank or an average, next to every row without hiding any rows.</p>',
    '<p>OVER (PARTITION BY ... ORDER BY ... frame) defines the window. Ranking, offset and aggregate functions all work over it. They run after GROUP BY and HAVING.</p>',
    '<p>Frames come in ROWS, RANGE and GROUPS units with EXCLUDE options. Engines sort once per distinct window and sweep the rows, keeping running state, so a running SUM costs about one pass after sorting.</p>',
    '<p>Efficient evaluation of arbitrary frames uses segment trees and similar structures (Leis et al., VLDB 2015, "Efficient Processing of Window Functions in Analytical SQL Queries"). Some engines add QUALIFY, a WHERE for window results, found in Snowflake, BigQuery, Teradata and DuckDB.</p>')}
{deep('Where window functions came from', '<p>They entered the SQL standard in SQL:2003 (first as OLAP functions in an amendment to SQL:1999). PostgreSQL added them in 8.4 (2009), SQL Server in 2005 with fuller frame support in 2012, MySQL in 8.0 (2018), and SQLite in 3.25.0 (2018).</p>')}
''', kw=['SQL:2003', 'segment tree', 'QUALIFY', 'window evaluation', 'OLAP functions'])
K.talk('levels', '''Here is the ladder for window functions. For a beginner, a window function writes a group answer next to every row without hiding any rows. At
college level, the OVER clause defines the window with partition, order and frame, and these functions run after grouping. At masters level, frames
come in rows, range and groups, and an engine sorts once and sweeps through the rows keeping a running state. At research level, clever structures
such as segment trees compute any frame quickly, and some engines add a QUALIFY clause to filter window results directly. Think of a teacher who
writes each student's rank on their own report card.''')

K.quiz('e', 'What turns SUM into a window function?', ['GROUP BY', 'OVER', 'WINDOW only', 'HAVING'], 1, 'Over.', 'SUM(...) OVER (...) is a window function.')
K.quiz('e', 'A window function returns', ['One row per group', 'One value per input row', 'One row total', 'Nothing'], 1, 'Every row stays.', 'Rows are not folded.')
K.quiz('e', 'Salaries 90, 80, 80, 70. RANK gives', ['1, 2, 3, 4', '1, 2, 2, 4', '1, 2, 2, 3', '1, 1, 2, 3'], 1, 'Gap after a tie.', 'Ties share 2, then 4.')
K.quiz('e', 'Same salaries. DENSE_RANK gives', ['1, 2, 3, 4', '1, 2, 2, 4', '1, 2, 2, 3', '2, 2, 3, 4'], 2, 'No gap.', 'Ties share 2, then 3.')
K.quiz('m', 'PARTITION BY dept_id makes ranking', ['Global', 'Restart in each department', 'Skip NULLs', 'Fail'], 1, 'Restart.', 'Each partition is ranked separately.')
K.quiz('m', 'LAG(x) on the first row of a partition returns', ['0', 'x', 'NULL', 'An error'], 2, 'Nothing before.', 'NULL unless a default is given.')
K.quiz('m', 'SUM(x) OVER (ORDER BY d) computes', ['The grand total', 'A running total', 'An average', 'A count'], 1, 'Up to here.', 'The default frame runs from the start to the current row.')
K.quiz('m', 'Why does WHERE RANK() OVER (...) <= 3 fail?', ['RANK is not real', 'WHERE runs before window functions', 'Needs GROUP BY', 'Too many brackets'], 1, 'Order of steps.', 'Filter in an outer query instead.')
K.quiz('m', 'ROWS BETWEEN 2 PRECEDING AND CURRENT ROW covers', ['2 rows', '3 rows', 'All rows', '1 row'], 1, 'Two plus this.', 'The current row and the two before.')
K.quiz('h', 'LAST_VALUE(x) OVER (ORDER BY d) often returns the current row’s x because', ['A bug', 'The default frame ends at the current row', 'NULLs', 'Sorting is random'], 1, 'Frame.', 'Use ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING.')
K.quiz('x', 'Which clause filters window results directly in Snowflake and DuckDB?', ['HAVING', 'QUALIFY', 'FILTER', 'LIMIT'], 1, 'Qualify.', 'QUALIFY is a WHERE for window functions.')

avg1 = value('company', 'SELECT AVG(salary) FROM employees WHERE dept_id = 1')
K.calc('e', 'What is the average salary in Engineering (dept 1)?', f'{avg1:g}', 'Four salaries.',
       ['250000 + 150000 + 90000 + 95000 = 585000.', 'There are 4 engineers.', eq(f'585000 ÷ 4 = {avg1:g}')], check=avg1)
r4 = value('company', "SELECT r FROM (SELECT name, RANK() OVER (ORDER BY salary DESC) AS r FROM employees) WHERE name = 'Joseph'")
K.calc('e', 'Across the whole company, what is Joseph’s RANK by salary, highest first?', str(r4), 'Count higher salaries.',
       ['Higher salaries: 250000, 150000, 140000, 95000, 90000, 85000.', 'That is 6 people above him.', eq(f'6 + 1 = {r4}')], check=r4)
d4 = value('company', "SELECT r FROM (SELECT name, DENSE_RANK() OVER (ORDER BY salary DESC) AS r FROM employees) WHERE name = 'Zoya'")
K.calc('m', 'What is Zoya’s DENSE_RANK by salary across the company?', str(d4), 'Distinct higher salaries plus 1.',
       ['Distinct salaries above 60000: 250000, 150000, 140000, 95000, 90000, 85000, 70000.', 'That is 7 distinct values.', eq(f'7 + 1 = {d4}')], check=d4)
rt = value('shop', "WITH daily AS (SELECT o.order_date, SUM(oi.qty * p.price) AS sales FROM orders o JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE o.status <> 'cancelled' GROUP BY o.order_date) SELECT rt FROM (SELECT order_date, SUM(sales) OVER (ORDER BY order_date) AS rt FROM daily) WHERE order_date = '2025-06-03'")
K.calc('m', 'In the running sales total, what is the value on 2025-06-03?', str(rt), 'Two days so far.',
       ['2025-06-01: order 101 = 2 × 120 + 5 × 60 = 540.', '2025-06-03: order 102 = 1 × 1499.', eq(f'540 + 1499 = {rt}')], check=rt)
K.calc('m', 'Ten rows are split by NTILE(4). How many rows does the first bucket get?', str(value('', 'SELECT count(*) FROM (SELECT NTILE(4) OVER (ORDER BY x) AS b FROM (WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n WHERE x < 10) SELECT x FROM n)) WHERE b = 1')), 'Larger buckets come first.',
       ['10 ÷ 4 = 2 remainder 2.', 'The first 2 buckets get one extra row.', eq('2 + 1 = 3 rows')], check=value('', 'SELECT count(*) FROM (SELECT NTILE(4) OVER (ORDER BY x) AS b FROM (WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n WHERE x < 10) SELECT x FROM n)) WHERE b = 1'))
gap = value('shop', "SELECT g FROM (SELECT id, julianday(order_date) - julianday(LAG(order_date) OVER (ORDER BY order_date)) AS g FROM orders WHERE customer_id = 1) WHERE id = 103")
K.calc('m', 'Customer 1 ordered on 2025-06-01 and 2025-06-10. What does the LAG gap give for order 103?', f'{gap:g}', 'Day numbers.',
       ['LAG gives 2025-06-01 for order 103.', 'Subtract the day numbers.', eq(f'10 − 1 = {gap:g} days')], check=gap)
mv = value('school', 'SELECT s FROM (SELECT student_id, AVG(score) OVER (ORDER BY student_id ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS s FROM marks WHERE course_id = 1) WHERE student_id = 2')
K.calc('h', 'Algebra scores by student id are 92, 64, 88, 99. What is the 3 row moving average for student 2?', f'{mv:.2f}', 'One before, this, one after.',
       ['Student 2 sits between students 1 and 3.', 'Average of 92, 64 and 88.', eq(f'(92 + 64 + 88) ÷ 3 = 244 ÷ 3 ≈ {mv:.2f}')], check=mv, tol=0.01)
K.calc('h', 'Salaries in Sales sorted high to low are 140000, 70000, 70000. With the default RANGE frame, what is the running SUM on the first 70000 row?', '280000', 'Tied rows are in the frame.',
       ['RANGE includes all peers of the current row.', 'Both 70000 rows are peers.', eq('140000 + 70000 + 70000 = 280000')], check=value('company', "SELECT max(s) FROM (SELECT SUM(salary) OVER (ORDER BY salary DESC) AS s, salary FROM employees WHERE dept_id = 2) WHERE salary = 70000"))

K.must('OVER', 'function(...) OVER (PARTITION BY ... ORDER BY ...) gives a group answer on every row. Rows are not folded.')
K.must('Ranking', 'ROW_NUMBER never ties, RANK ties with gaps, DENSE_RANK ties without gaps. Add a tie breaker for stable results.')
K.must('Running and neighbours', 'An aggregate with ORDER BY is a running aggregate. LAG and LEAD read the previous and next rows.')
K.must('Frames', 'No ORDER BY means the whole partition. ORDER BY means start to current row with peers. ROWS BETWEEN sets your own.')
K.must('Filtering', 'Window functions run after WHERE, GROUP BY and HAVING. Filter on them in an outer query or CTE.')

T = K.topic(
    slug='sql-window', topic='sql-window', step=(6, 'Advanced queries', 'sql-advanced', 'Window functions, recursive queries and the patterns that solve real reporting problems.', 'Advanced'),
    title='Window functions: ranks, running totals and more', short='Window functions', badge='6.1', minutes=45, added='2026-11-23',
    lead='Put a group answer beside every row with OVER, rank with ROW_NUMBER, RANK and DENSE_RANK, build running totals, look at neighbouring rows with LAG and LEAD, and control frames.',
    desc='OVER and PARTITION BY, ROW_NUMBER, RANK, DENSE_RANK, NTILE, PERCENT_RANK, CUME_DIST, running totals, LAG, LEAD, FIRST_VALUE, LAST_VALUE, frames with ROWS, RANGE and GROUPS, named WINDOW, filtering in an outer query.',
    summary='OVER, ranking, running totals, LAG and LEAD, frames.',
    keywords=['window functions', 'OVER', 'PARTITION BY', 'ROW_NUMBER', 'RANK', 'LAG', 'running total'],
    recap='<p>Window functions keep every row and add a group answer: ranks, running totals, neighbours, all over a frame you control.</p>')
