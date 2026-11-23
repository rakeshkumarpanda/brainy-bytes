# Chapter 6.2: recursive queries: WITH RECURSIVE, anchor and recursive member, stop conditions, generating series and
# calendars, walking hierarchies (org charts, category trees), paths and depth, graphs and cycles, UNION versus UNION ALL.
# Sources: sqlite.org lang_with.html (recursive CTE rules, queue processing, UNION discards duplicates, LIMIT stops runaway
# queries, no aggregates or window functions in the recursive select), postgresql.org queries-with.html (SEARCH and CYCLE
# since 14), learn.microsoft.com MAXRECURSION (default 100), Oracle CONNECT BY documentation.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('basics', 'A query that calls itself', f'''
<p>Some questions have no fixed number of steps: "everyone who reports to Priya, directly or through others", "every date in June". A <b>recursive CTE</b> answers them by running a query again and again on its own latest results until nothing new appears.</p>
{fxs(fx('Recursive CTE', '<code>WITH RECURSIVE name(cols) AS ( anchor UNION ALL recursive_part ) SELECT ... FROM name;</code>', 'The anchor runs once. The recursive part reads name, but only sees the rows from the round before.', key=True))}
{pk('sqrec')}
{K.sql('count', """WITH RECURSIVE n(x) AS (
  SELECT 1
  UNION ALL
  SELECT x + 1 FROM n WHERE x < 10
)
SELECT x FROM n;""", db='', title='Counting from 1 to 10 with no table at all', notes={2: 'The anchor: the first row, 1.', 4: 'Each round adds 1 to the last row. The WHERE is the stop rule.'})}
{steps('How the engine runs it', [
    'Run the anchor and put its rows in the result and in a queue.',
    'Take rows from the queue and run the recursive part on them.',
    'Add any new rows to the result and to the queue.',
    'Stop when the queue is empty. No stop rule means it never empties.'])}
{note('Always write a stop rule, such as WHERE x < 10, a depth limit, or a LIMIT on the outer query. SQL Server stops after 100 rounds by default (MAXRECURSION), SQLite has no such limit.', 'warn')}
{K.lab('l-sum', 'e', 'Add up 1 to 100', 'Use a recursive CTE to produce the numbers 1 to 100 and return their sum as <code>total</code>.',
"""WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n WHERE x < 100)
SELECT SUM(x) AS total FROM n;""", db='', hint='Count to 100 as in the example, then SELECT SUM(x) FROM n.', why='The CTE makes 100 rows, and SUM adds them: 5050.')}
''', kw=['WITH RECURSIVE', 'recursive CTE', 'anchor member', 'recursive member', 'stop condition', 'MAXRECURSION'])
K.talk('basics', '''Some questions have no fixed number of steps, like everyone who reports to Priya, directly or through others. A recursive CTE answers them. You write
WITH RECURSIVE, a name, and two queries joined by UNION ALL. The first is the anchor, which runs once and makes the starting rows. The second is the
recursive part, which reads the CTE's own name and sees only the rows found in the round before. Round after round, new rows appear, until a round
finds nothing. In the animation, count to a number of your choice, or walk down the org chart, and watch each round add its rows. Always include a stop
rule. Think of a chain of phone calls where each person rings the next.''')

K.lesson('series', 'Generating series and calendars', f'''
<p>SQLite has no built in series generator in this build, so a recursive CTE is the usual way to make a run of numbers or dates. A calendar of days is handy for reports that must show days with zero sales too.</p>
{K.sql('calendar', """WITH RECURSIVE days(d) AS (
  SELECT '2025-06-01'
  UNION ALL
  SELECT date(d, '+1 day') FROM days WHERE d < '2025-06-10'
)
SELECT d, COUNT(o.id) AS orders
FROM days LEFT JOIN orders o ON o.order_date = d
GROUP BY d;""", title='Every day from 1 to 10 June, with zero for quiet days', notes={4: "date(d, '+1 day') moves to the next date.", 7: 'LEFT JOIN keeps days that have no orders, so they show 0.'})}
{K.sql('powers', """WITH RECURSIVE p(n, val) AS (
  SELECT 0, 1
  UNION ALL
  SELECT n + 1, val * 2 FROM p WHERE n < 10
)
SELECT n, val FROM p;""", db='', title='Powers of two, carrying two columns along', notes={4: 'Every column can change from round to round.'})}
{table(['Engine', 'Built in series'], [
    ['PostgreSQL', 'generate_series(1, 10) and generate_series(date, date, interval)'],
    ['SQL Server 2022+', 'GENERATE_SERIES(1, 10)'],
    ['SQLite', 'a generate_series table valued function exists as an extension, otherwise a recursive CTE'],
    ['MySQL 8', 'recursive CTE']])}
{K.lab('l-cal', 'm', 'Orders per day in early July', 'Make a calendar from <code>2025-07-01</code> to <code>2025-07-07</code> and show each day <code>d</code> with its number of orders as <code>orders</code>, zero included.',
"""WITH RECURSIVE days(d) AS (SELECT '2025-07-01' UNION ALL SELECT date(d, '+1 day') FROM days WHERE d < '2025-07-07')
SELECT d, COUNT(o.id) AS orders FROM days LEFT JOIN orders o ON o.order_date = d GROUP BY d;""", hint="Change the dates of the June example. COUNT(o.id) gives 0 when nothing matches.", why='Only 2 and 5 July have orders, the other five days show 0.')}
''', kw=['generate series', 'calendar table', 'date series', 'missing dates', 'zero rows', 'generate_series'])
K.talk('series', '''A recursive CTE is also a factory for numbers and dates. Start with the first of June, and each round add one day, until you reach the tenth. Then
left join the orders, and every day appears in the report, even quiet days with zero orders, which a plain GROUP BY would leave out. A CTE can carry
several columns from round to round, such as a counter and a running power of two. PostgreSQL and newer SQL Server have a built in generate series
function, and elsewhere the recursive CTE does the job. Think of a desk calendar where every page is there, even for days with no appointments.''')

K.lesson('tree', 'Walking hierarchies', f'''
<p>A table that points at itself, like employees.manager_id, stores a <b>tree</b>. A recursive CTE walks the tree one level per round, and can carry the depth and the path along.</p>
{K.sql('org', """WITH RECURSIVE chain(id, name, level, path) AS (
  SELECT id, name, 0, name FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.name, c.level + 1, c.path || ' > ' || e.name
  FROM employees e JOIN chain c ON e.manager_id = c.id
)
SELECT substr('            ', 1, level * 3) || name AS org_chart, level, path
FROM chain ORDER BY path;""", db='company', title='The whole org chart with depth and path', notes={2: 'Start at the top: the person with no manager.', 4: 'Each round goes one level down and extends the path text.', 7: 'Indent by level to draw the tree.'})}
{K.sql('up', """WITH RECURSIVE up(id, name, manager_id) AS (
  SELECT id, name, manager_id FROM employees WHERE name = 'Tara'
  UNION ALL
  SELECT e.id, e.name, e.manager_id FROM employees e JOIN up ON e.id = up.manager_id
)
SELECT name FROM up;""", db='company', title='Walking up: Tara’s chain of managers', notes={4: 'Follow manager_id upwards instead of downwards.'})}
{table(['Real tree', 'Self reference'], [
    ['Org chart', 'employee.manager_id → employee.id'],
    ['Category menu in a shop', 'category.parent_id → category.id'],
    ['Comment threads', 'comment.reply_to → comment.id'],
    ['Folders on a disk', 'folder.parent_id → folder.id'],
    ['Bill of materials', 'part made of other parts, with quantities']])}
{K.lab('l-team', 'm', 'Rahul’s whole team', 'From the company database, list the <code>name</code> of everyone who reports to Rahul (id 2), directly or indirectly. Do not include Rahul.',
"""WITH RECURSIVE t(id, name) AS (SELECT id, name FROM employees WHERE manager_id = 2 UNION ALL SELECT e.id, e.name FROM employees e JOIN t ON e.manager_id = t.id)
SELECT name FROM t;""", db='company', hint='Start the anchor with the people whose manager_id = 2.', why='Sneha and Imran report to Rahul, and nobody reports to them.')}
''', kw=['hierarchy', 'tree', 'org chart', 'self reference', 'path', 'depth', 'bill of materials', 'parent child'])
K.talk('tree', '''When a table points at itself, such as an employee's manager id pointing at another employee, it stores a tree. A recursive CTE walks that tree one
level per round. The anchor starts at the top, the person with no manager, and each round joins the employees whose manager was found in the last
round. Carry a level number and a path of names along, and you can draw the whole org chart with indents. Walk the other way, following the manager id
upwards, and you get anyone's chain of bosses. The same pattern serves shop category menus, comment threads and folders. Think of a family tree traced
down from the grandparents.''')

K.lesson('graph', 'Graphs, cycles and UNION', f'''
<p>A tree has one parent per node. A <b>graph</b> can have many links and even loops, such as train routes. A naive recursive walk around a loop never ends, so you must stop it.</p>
{K.sql('routes', """CREATE TABLE routes (src TEXT, dst TEXT, km INTEGER);
INSERT INTO routes VALUES ('Pune', 'Mumbai', 150), ('Mumbai', 'Surat', 280),
  ('Pune', 'Hyderabad', 560), ('Hyderabad', 'Chennai', 630), ('Surat', 'Pune', 420);
WITH RECURSIVE trip(city, path, km) AS (
  SELECT 'Pune', 'Pune', 0
  UNION ALL
  SELECT r.dst, t.path || ' > ' || r.dst, t.km + r.km
  FROM trip t JOIN routes r ON r.src = t.city
  WHERE instr(t.path, r.dst) = 0
)
SELECT path, km FROM trip WHERE city <> 'Pune' ORDER BY km;""", db='', title='Every trip from Pune that never revisits a city', notes={3: 'Surat to Pune closes a loop.', 9: 'Skip a city already in the path. This is the cycle guard.'})}
{table(['Way to stop a cycle', 'How'], [
    ['Path check', 'keep the path as text or JSON and skip nodes already in it'],
    ['UNION instead of UNION ALL', 'drops rows that are exact repeats, which ends simple loops where the whole row repeats'],
    ['Depth limit', 'carry a level column and add WHERE level < 10'],
    ['LIMIT', 'a LIMIT on the outer query stops the recursion early in SQLite'],
    ['CYCLE clause', 'PostgreSQL 14+: CYCLE id SET is_cycle USING path']])}
{K.sql('unionstop', """CREATE TABLE edge (a INTEGER, b INTEGER);
INSERT INTO edge VALUES (1, 2), (2, 3), (3, 1);
WITH RECURSIVE reach(n) AS (
  SELECT 1
  UNION
  SELECT b FROM edge JOIN reach ON a = n
)
SELECT n FROM reach;""", db='', title='UNION ends a simple loop', notes={2: '1 > 2 > 3 > 1 is a loop.', 5: 'UNION ALL would run forever here. UNION refuses the repeated row 1 and stops.'})}
{scene('friend suggestions', '<p>A social app suggests "people you may know": friends of your friends who are not already your friends. That is a two step walk on the friendship graph. Graph databases such as Neo4j are built for long walks, but for a few hops a recursive CTE with a depth limit works in any SQL engine.</p>')}
{K.lab('l-path', 'h', 'Shortest trip to Chennai', 'Using the <code>routes</code> table from the example, find the trip from Pune to Chennai with the fewest kilometres. Show its <code>path</code> and <code>km</code>.',
"""WITH RECURSIVE trip(city, path, km) AS (SELECT 'Pune', 'Pune', 0 UNION ALL SELECT r.dst, t.path || ' > ' || r.dst, t.km + r.km FROM trip t JOIN routes r ON r.src = t.city WHERE instr(t.path, r.dst) = 0)
SELECT path, km FROM trip WHERE city = 'Chennai' ORDER BY km LIMIT 1;""", db='', setup="""CREATE TABLE routes (src TEXT, dst TEXT, km INTEGER);
INSERT INTO routes VALUES ('Pune', 'Mumbai', 150), ('Mumbai', 'Surat', 280), ('Pune', 'Hyderabad', 560), ('Hyderabad', 'Chennai', 630), ('Surat', 'Pune', 420);""", hint='Reuse the trip CTE, then keep rows where city = Chennai, ORDER BY km and LIMIT 1.', why='The only route is through Hyderabad: 560 + 630 = 1190 km.')}
''', kw=['graph', 'cycle', 'cycle detection', 'UNION vs UNION ALL', 'path', 'shortest path', 'CYCLE clause'])
K.talk('graph', '''A tree has one parent per node, but a graph can have many links and even loops, like train routes that come back to where they started. A naive
recursive walk around a loop never ends, so you must guard against it. The common trick is to carry the path as text and skip any city that is already
in it. UNION instead of UNION ALL also ends simple loops, because it refuses a row it has already produced. A depth limit or an outer LIMIT are extra
safety nets, and PostgreSQL has a CYCLE clause that does the bookkeeping for you. Think of a traveller who ticks off each city on a map so they never go
round in circles.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A recursive query starts with some rows and keeps finding more rows from the ones it just found, until no new ones appear.</p>',
    '<p>Anchor UNION ALL recursive part, with a stop rule. Use it for series, hierarchies and graph walks. Guard against cycles with a path, UNION or a depth limit.</p>',
    '<p>Semantically it computes a least fixed point. Engines run it as semi naive evaluation: each round joins only the new rows (the delta) from the previous round, which is why the recursive part sees only last round’s rows. Linear recursion, where the CTE appears once, is what the SQL standard allows.</p>',
    '<p>Recursive SQL comes from Datalog research on deductive databases. Modern work studies graph query languages, including the ISO GQL standard (2024) and SQL/PGQ (SQL:2023 part 16), which adds property graph queries to SQL itself.</p>')}
{deep('Other ways to store trees', '<p>Besides parent pointers (the adjacency list used here) there are nested sets (left and right numbers per node), materialized paths (a column such as /1/2/4/), and closure tables (one row per ancestor and descendant pair). They make some reads faster and writes slower. PostgreSQL’s ltree extension stores materialized paths.</p>')}
''', kw=['fixed point', 'semi naive evaluation', 'Datalog', 'GQL', 'SQL/PGQ', 'nested sets', 'closure table', 'materialized path'])
K.talk('levels', '''Up the ladder we go. For a beginner, a recursive query keeps finding new rows from the rows it just found. At college level, it is an anchor joined to
a recursive part by UNION ALL, with a stop rule, used for series, trees and graphs. At masters level, the engine runs semi naive evaluation, joining
only the newest rows each round, and the answer is a least fixed point. At research level, these ideas come from Datalog, and new standards such as
GQL and SQL property graph queries bring graph matching into databases. Think of ripples spreading from a stone dropped in a pond.''')

K.quiz('e', 'A recursive CTE starts with the words', ['WITH LOOP', 'WITH RECURSIVE', 'REPEAT', 'RECURSE'], 1, 'Recursive.', 'WITH RECURSIVE name AS (...).')
K.quiz('e', 'The part that runs once is the', ['Anchor', 'Loop', 'Frame', 'Index'], 0, 'Start.', 'The anchor makes the starting rows.')
K.quiz('e', 'Without a stop rule the query', ['Returns nothing', 'May run forever', 'Fails at once', 'Returns one row'], 1, 'No end.', 'Always add a stop rule.')
K.quiz('e', 'Which table design stores a tree?', ['A table pointing at itself', 'Two unrelated tables', 'A view', 'An index'], 0, 'Self reference.', 'employees.manager_id points at employees.id.')
K.quiz('m', 'In each round, the recursive part sees', ['All rows so far', 'Only the rows from the previous round', 'Only the anchor', 'The whole table'], 1, 'Delta.', 'It works on the newest rows.')
K.quiz('m', 'Why LEFT JOIN a calendar to orders?', ['Speed', 'To keep days with zero orders', 'To remove NULLs', 'To sort'], 1, 'Quiet days.', 'Days without orders still appear.')
K.quiz('m', 'UNION instead of UNION ALL in a recursive CTE', ['Is not allowed', 'Drops repeated rows, which can end loops', 'Doubles rows', 'Sorts rows'], 1, 'No repeats.', 'A repeated row is not queued again.')
K.quiz('m', 'SQL Server’s default recursion limit is', ['10', '100', '1000', 'none'], 1, 'MAXRECURSION.', 'The default is 100 rounds.')
K.quiz('m', 'Oracle’s older syntax for hierarchies is', ['CONNECT BY', 'TREE BY', 'LINK BY', 'WALK'], 0, 'Connect.', 'START WITH ... CONNECT BY PRIOR.')
K.quiz('h', 'A path column like Pune > Mumbai is used to', ['Sort only', 'Detect and skip cycles', 'Make indexes', 'Group rows'], 1, 'Visited set.', 'Skip nodes already in the path.')
K.quiz('x', 'Evaluating only the new rows each round is called', ['Naive evaluation', 'Semi naive evaluation', 'Lazy loading', 'Sharding'], 1, 'Delta rounds.', 'Semi naive evaluation.')

K.calc('e', 'How many rows does the counting CTE from 1 while x < 10 produce?', '10', 'Stops after 10.',
       ['The anchor gives 1.', 'Each round adds one until x = 10 fails the rule x < 10.', eq('10 rows')], check=value('', 'WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n WHERE x < 10) SELECT count(*) FROM n'))
K.calc('e', 'What is the sum of 1 to 100?', '5050', 'Gauss.',
       ['Pair 1 with 100, 2 with 99, and so on.', 'There are 50 pairs of 101.', eq('50 × 101 = 5050')], check=value('', 'WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n WHERE x < 100) SELECT SUM(x) FROM n'))
pw = value('', 'WITH RECURSIVE p(n, v) AS (SELECT 0, 1 UNION ALL SELECT n + 1, v * 2 FROM p WHERE n < 10) SELECT max(v) FROM p')
K.calc('m', 'In the powers of two CTE, what is the last value?', str(pw), '2 to the 10.',
       ['The rounds go n = 0 to 10.', 'val doubles each round.', eq(f'2¹⁰ = {pw}')], check=pw)
deep_ = value('company', 'WITH RECURSIVE c(id, lv) AS (SELECT id, 0 FROM employees WHERE manager_id IS NULL UNION ALL SELECT e.id, c.lv + 1 FROM employees e JOIN c ON e.manager_id = c.id) SELECT max(lv) FROM c')
K.calc('m', 'How deep is the Orbit Tech org chart (Priya is level 0)?', str(deep_), 'Longest chain.',
       ['Priya > Rahul > Sneha.', 'Priya is 0, Rahul 1, Sneha 2.', eq(f'deepest level = {deep_}')], check=deep_)
under = value('company', 'WITH RECURSIVE c(id) AS (SELECT id FROM employees WHERE manager_id = 1 UNION ALL SELECT e.id FROM employees e JOIN c ON e.manager_id = c.id) SELECT count(*) FROM c')
K.calc('m', 'How many people report to Priya, directly or indirectly?', str(under), 'Everyone else.',
       ['Priya is at the top.', 'All other employees are below her.', eq(f'10 − 1 = {under}')], check=under)
quiet = value('shop', "WITH RECURSIVE d(x) AS (SELECT '2025-06-01' UNION ALL SELECT date(x, '+1 day') FROM d WHERE x < '2025-06-10') SELECT count(*) FROM d WHERE x NOT IN (SELECT order_date FROM orders)")
K.calc('m', 'In the 1 to 10 June calendar, how many days have zero orders?', str(quiet), 'Ten days minus busy days.',
       ['Orders fell on 1, 3 and 10 June.', 'That is 3 busy days out of 10.', eq(f'10 − 3 = {quiet}')], check=quiet)
up = value('company', "WITH RECURSIVE u(id, m) AS (SELECT id, manager_id FROM employees WHERE name = 'Tara' UNION ALL SELECT e.id, e.manager_id FROM employees e JOIN u ON e.id = u.m) SELECT count(*) FROM u")
K.calc('h', 'How many rows does the walk up from Tara return, Tara included?', str(up), 'Tara, Mohan, Priya.',
       ['Tara’s manager is Mohan.', 'Mohan’s manager is Priya, who has none.', eq(f'{up} rows')], check=up)
trips = value('', "WITH RECURSIVE trip(city, path, km) AS (SELECT 'Pune', 'Pune', 0 UNION ALL SELECT r.dst, t.path || ' > ' || r.dst, t.km + r.km FROM trip t JOIN routes r ON r.src = t.city WHERE instr(t.path, r.dst) = 0) SELECT count(*) FROM trip WHERE city <> 'Pune'",
              setup="CREATE TABLE routes (src TEXT, dst TEXT, km INTEGER); INSERT INTO routes VALUES ('Pune', 'Mumbai', 150), ('Mumbai', 'Surat', 280), ('Pune', 'Hyderabad', 560), ('Hyderabad', 'Chennai', 630), ('Surat', 'Pune', 420);")
K.calc('h', 'How many trips from Pune that never revisit a city does the routes example find?', str(trips), 'List them.',
       ['Pune > Mumbai, then Pune > Mumbai > Surat.', 'Pune > Hyderabad, then Pune > Hyderabad > Chennai.', eq(f'{trips} trips')], check=trips)

K.must('Shape', 'WITH RECURSIVE name AS (anchor UNION ALL recursive part). The recursive part reads name and sees last round’s rows.')
K.must('Stop rule', 'Always stop: a WHERE condition, a depth limit, a cycle guard or an outer LIMIT.')
K.must('Series', 'Generate numbers and dates, then LEFT JOIN to show zero rows.')
K.must('Trees', 'Self referencing tables are walked one level per round. Carry level and path along.')
K.must('Graphs', 'Loops need a path check, UNION, or a depth limit. PostgreSQL has CYCLE.')

T = K.topic(
    slug='sql-recursive', topic='sql-recursive', step=(6, 'Advanced queries', 'sql-advanced', 'Window functions, recursive queries and the patterns that solve real reporting problems.', 'Advanced'),
    title='Recursive queries: trees, graphs and series', short='Recursive queries', badge='6.2', minutes=40, added='2026-11-23',
    lead='Write queries that call themselves with WITH RECURSIVE to generate number and date series, walk org charts and category trees, and explore graphs without getting stuck in loops.',
    desc='WITH RECURSIVE, anchor and recursive parts, stop rules, number and date series, calendar tables, hierarchies with level and path, walking up and down, graphs, cycle guards, UNION versus UNION ALL, CYCLE, other tree models.',
    summary='WITH RECURSIVE for series, hierarchies and graphs.',
    keywords=['WITH RECURSIVE', 'recursive CTE', 'hierarchy', 'org chart', 'graph', 'cycle'],
    recap='<p>A recursive CTE grows round by round from an anchor until no new rows appear, which walks trees, graphs and series.</p>')
