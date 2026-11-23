# Chapter 1.3: filtering and sorting: WHERE, comparisons, AND OR NOT and precedence, BETWEEN, IN, LIKE and GLOB,
# IS NULL, ORDER BY with several columns and NULLS FIRST/LAST. Sources: sqlite.org lang_expr.html (LIKE case
# insensitive for ASCII by default, GLOB case sensitive, operator precedence), datatype3.html (NULL sorts first),
# lang_select.html (NULLS FIRST and NULLS LAST, added in SQLite 3.30.0).
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('where', 'WHERE keeps only the rows you want', f'''
<p>A library has thousands of books, but you only want the ones about cricket. <code>WHERE</code> is the librarian's filter. It tests every row with a condition, keeps the rows where the condition is <b>true</b>, and throws the rest away.</p>
{pk('sqwhere')}
{table(['Operator', 'Meaning', 'Example'], [
    ['<code>=</code>', 'equal to', "<code>city = 'Pune'</code>"],
    ['<code>&lt;&gt;</code> or <code>!=</code>', 'not equal to', "<code>status &lt;&gt; 'cancelled'</code>"],
    ['<code>&lt; &lt;= &gt; &gt;=</code>', 'smaller, bigger', '<code>price &gt;= 500</code>'],
    ['<code>BETWEEN a AND b</code>', 'from a to b, both ends included', '<code>price BETWEEN 100 AND 300</code>'],
    ['<code>IN (...)</code>', 'equal to any value in the list', "<code>category IN ('Sports', 'Kitchen')</code>"],
    ['<code>IS NULL</code>', 'the value is missing', '<code>email IS NULL</code>']])}
{K.sql('w1', """SELECT name, price, stock
FROM products
WHERE price BETWEEN 100 AND 300;""", title='Products from Rs 100 to Rs 300', notes={3: 'BETWEEN includes both ends, so a price of exactly 100 or 300 would count.'})}
{note("Text comparisons are exact in SQLite with = : 'pune' is not equal to 'Pune'. Dates stored as text in the ISO form YYYY-MM-DD sort and compare correctly as text.", 'tip')}
{K.lab('l-pune', 'e', 'Customers from Pune', 'Show the <code>name</code> of every customer who lives in Pune.', "SELECT name FROM customers WHERE city = 'Pune';", hint="city = 'Pune' with single quotes.", why='WHERE keeps the rows where the test is true.')}
''', kw=['WHERE', 'filter', 'comparison', 'BETWEEN', 'IN', 'not equal', 'condition'])
K.talk('where', '''WHERE is the filter of SQL. The database takes each row, tests it with your condition, keeps it when the answer is true, and drops it
otherwise. You can compare with equals, not equals, smaller and bigger. BETWEEN checks a range and includes both ends, so between one
hundred and three hundred includes three hundred. IN checks against a short list of values, which is shorter than writing many equals
signs joined by OR. Text must match exactly, including capital letters. Dates written as year, month, day compare correctly as text,
which is why the sample shop stores them that way. Think of a security guard at a gate checking every person against one rule.''')

K.lesson('logic', 'AND, OR, NOT and brackets', f'''
<p>Real questions have more than one condition. "Sports items under Rs 500" needs both tests to be true, so it uses <code>AND</code>. "Kitchen or Sports items" needs either one, so it uses <code>OR</code>. <code>NOT</code> flips true and false.</p>
{table(['A', 'B', 'A AND B', 'A OR B', 'NOT A'], [
    ['true', 'true', 'true', 'true', 'false'],
    ['true', 'false', 'false', 'true', 'false'],
    ['false', 'true', 'false', 'true', 'true'],
    ['false', 'false', 'false', 'false', 'true']])}
<p><b>AND is done before OR</b>, just as multiplication is done before addition in maths. Forgetting this is one of the most common SQL bugs.</p>
{K.sql('prec', """-- Without brackets: AND binds first
SELECT name, category, price
FROM products
WHERE category = 'Sports' OR category = 'Kitchen' AND price < 300;

-- With brackets: what we usually mean
SELECT name, category, price
FROM products
WHERE (category = 'Sports' OR category = 'Kitchen') AND price < 300;""", title='Brackets change the answer', notes={4: 'Read as Sports OR (Kitchen AND under 300). The Football at 850 sneaks in.', 9: 'Now the price test applies to both categories.'})}
{steps('Read the first query the way SQLite does', [
    'AND binds tighter than OR, so the condition is Sports OR (Kitchen AND price &lt; 300).',
    'Every Sports product passes, whatever its price: Cricket ball and Football.',
    'Kitchen products pass only under 300: Water bottle at 250 passes, Lunch box at 399 fails.',
    eq('With brackets the price rule covers both, so only Cricket ball and Water bottle remain')])}
{note('When AND and OR appear together, add brackets even if you know the rule. The next reader may not.', 'warn')}
{K.lab('l-andor', 'm', 'Cheap stationery or any sports item', 'Show the <code>name</code> of products that are either Stationery costing under 100, or in the Sports category.', "SELECT name FROM products WHERE (category = 'Stationery' AND price < 100) OR category = 'Sports';", hint='Group the two Stationery tests in brackets, then OR the Sports test.', why='Brackets make the meaning clear: (Stationery and cheap) or Sports.')}
''', kw=['AND', 'OR', 'NOT', 'precedence', 'brackets', 'truth table', 'operator precedence'])
K.talk('logic', '''Real questions often need more than one test. AND means both tests must be true, OR means at least one must be true, and NOT flips true
into false. Here is the trap. SQL does AND before OR, the same way maths does multiplication before addition. So category equals sports
OR category equals kitchen AND price below three hundred really means sports items of any price, plus cheap kitchen items. That is why
the football at eight hundred and fifty sneaks into the first answer. Brackets fix it. Whenever AND and OR meet in one condition, add
brackets so every reader sees the same meaning. Think of brackets in maths, two plus three times four is fourteen, not twenty.''')

K.lesson('patterns', 'LIKE, GLOB and IS NULL', f'''
<p>Sometimes you know only part of a value, like "a product with box in its name". <code>LIKE</code> matches patterns. A <code>%</code> stands for any run of characters, even none. An <code>_</code> stands for exactly one character.</p>
{pk('sqlike')}
{table(['Pattern', 'Matches', 'Does not match'], [
    ["<code>'P%'</code>", 'Pencil box, Phone charger', 'Notebook'],
    ["<code>'%box'</code>", 'Pencil box, Lunch box', 'Boxing gloves (box is not at the end)'],
    ["<code>'_o%'</code>", 'Notebook, Football (o is the second letter)', 'Pencil box'],
    ["<code>'%a_e%'</code>", 'Water bottle (a, any letter, e)', 'Cricket ball']])}
{note('In SQLite, LIKE ignores the difference between capital and small letters for plain English letters. GLOB is the case sensitive cousin and uses * and ? instead of % and _. PostgreSQL LIKE is case sensitive, and it has ILIKE for case insensitive matching.', 'exam')}
<p>Missing values need special care. <code>email = NULL</code> never finds anything, because comparing with an unknown value gives unknown, not true. Use <code>IS NULL</code> and <code>IS NOT NULL</code>. The next step of this subject has a whole chapter on NULL.</p>
{K.sql('isnull', """SELECT name, email
FROM customers
WHERE email IS NULL;

SELECT name, email
FROM customers
WHERE email = NULL;""", title='IS NULL works, = NULL finds nothing', notes={3: 'IS NULL is true when the value is missing.', 7: 'This compares with unknown, the answer is unknown, so no row passes.'})}
{K.lab('l-like', 'm', 'Products with a two word name', "Show the <code>name</code> of products whose name contains a space.", "SELECT name FROM products WHERE name LIKE '% %';", hint="A space between two % signs.", why="'% %' means anything, a space, anything.")}
''', kw=['LIKE', 'wildcard', '%', '_', 'GLOB', 'ILIKE', 'case sensitive', 'IS NULL', 'IS NOT NULL'])
K.talk('patterns', '''LIKE finds values that match a pattern. The percent sign stands for any number of characters, even zero, and the underscore stands
for exactly one character. So P percent finds every name starting with P, and percent box finds every name ending with box. In SQLite,
LIKE ignores upper and lower case for plain English letters, while GLOB is case sensitive and uses star and question mark instead.
PostgreSQL is the other way round, its LIKE is case sensitive and ILIKE ignores case. Missing values need IS NULL. Writing equals NULL
finds nothing at all, because comparing with an unknown gives unknown. Think of LIKE as a crossword clue with blank squares.''')

K.lesson('order', 'ORDER BY: sorting the result', f'''
<p>A cricket scoreboard lists batters by runs, highest first. <code>ORDER BY</code> sorts the result. <code>ASC</code> (the default) puts small values first, <code>DESC</code> puts big values first. You can sort by several columns: the second one only breaks ties in the first.</p>
{pk('sqorder')}
{K.sql('order2', """SELECT name, category, price
FROM products
ORDER BY category ASC, price DESC;""", title='Sort by category, then by price inside each category', notes={3: 'Rows are grouped A to Z by category. Inside one category the most expensive comes first.'})}
{table(['Rule', 'In SQLite'], [
    ['Where do NULLs go in ASC order', 'First, because SQLite treats NULL as smaller than every other value'],
    ['Choose yourself', '<code>ORDER BY city NULLS LAST</code> (supported since SQLite 3.30.0, also in PostgreSQL and Oracle)'],
    ['Sort by an alias', '<code>SELECT price * stock AS v ... ORDER BY v DESC</code> works'],
    ['Sort by position', '<code>ORDER BY 2</code> means the 2nd column of the SELECT list, allowed but hard to read'],
    ['Text order', 'By character codes (BINARY collation): capital letters come before small ones. <code>COLLATE NOCASE</code> ignores case for English letters']])}
{K.sql('nulls', """SELECT name, city
FROM customers
ORDER BY city NULLS LAST, name;""", title='Missing cities at the end', notes={3: 'Without NULLS LAST, Arjun (no city) would be first.'})}
{scene('the cricket points table', '<p>A league table sorts teams by points, highest first. Two teams on equal points are split by net run rate. In SQL that is <code>ORDER BY points DESC, net_run_rate DESC</code>. The second column only matters when the first one ties.</p>')}
{K.lab('l-sort', 'm', 'Newest customers first', 'Show <code>name</code> and <code>joined</code> for every customer, newest join date first.', 'SELECT name, joined FROM customers ORDER BY joined DESC;', hint='Dates in YYYY-MM-DD form sort correctly as text. Use DESC.', why='DESC puts the biggest date, the newest, first.', ordered=True)}
''', kw=['ORDER BY', 'ASC', 'DESC', 'NULLS FIRST', 'NULLS LAST', 'collation', 'NOCASE', 'multiple sort keys'])
K.talk('order', '''ORDER BY sorts your result. ASC, which is the default, puts small values first, and DESC puts big values first. You can list several
columns, and each later column only breaks ties in the earlier ones, just like a cricket points table that sorts by points and then by
net run rate. In SQLite, NULL counts as smaller than everything, so missing values come first in ascending order. Since SQLite version
three point thirty you can write NULLS LAST to move them to the end. Text sorts by character codes, so capital letters come before small
letters unless you ask for COLLATE NOCASE. Think of lining up children by height and then by name when two are the same height.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>WHERE is a sieve that keeps the rows you want, and ORDER BY lines them up neatly.</p>',
    '<p>WHERE runs before SELECT and ORDER BY runs after it. That is why WHERE cannot use a column alias from the SELECT list but ORDER BY can.</p>',
    '<p>A WHERE condition is selection (σ) in relational algebra. The planner can use an index when a condition compares a column directly with a value, such as <code>price &lt; 300</code>. Wrapping the column in a function, such as <code>lower(name) = ...</code>, usually stops a plain index from being used.</p>',
    '<p>Optimizers estimate how many rows each condition keeps (its selectivity) from statistics such as histograms, then order the work so the most selective, cheapest tests run first. Bad estimates are a top cause of slow queries in real systems.</p>')}
{deep('LIKE and indexes', "<p>A pattern that starts with a fixed prefix, such as 'Pen%', can use an index in many engines, because the matching values sit together in sorted order. A pattern that starts with %, such as '%box', must check every row. Full text search features exist for searching words inside long text.</p>")}
''', kw=['logical order', 'selection', 'sargable', 'selectivity', 'histogram', 'index'])
K.talk('levels', '''Let us climb the ladder once more. At the bottom, WHERE is a sieve and ORDER BY lines rows up. At college level, WHERE runs before the
select list and ORDER BY runs after it, which is why ORDER BY can use an alias but WHERE cannot. At masters level, WHERE is selection
in relational algebra, and a plain comparison on a column lets the planner use an index, while wrapping the column in a function often
stops that. At research level, optimizers guess how many rows each test keeps, using statistics, and a bad guess makes a query slow.
Think of a cook who checks the cheapest test first, like looking at the colour of a mango before cutting it open.''')

K.quiz('e', 'Which rows does WHERE keep?', ['Rows where the condition is true', 'Rows where it is false', 'Rows where it is NULL', 'All rows'], 0, 'True only.', 'False and unknown rows are dropped.')
K.quiz('e', 'Does BETWEEN 100 AND 300 include 300?', ['Yes', 'No', 'Only for whole numbers', 'Only in MySQL'], 0, 'Both ends.', 'BETWEEN includes both end values.')
K.quiz('e', 'Which finds customers with no email?', ['email = NULL', 'email IS NULL', "email = ''", 'email == NULL'], 1, 'IS.', 'Only IS NULL tests for a missing value.')
K.quiz('e', 'Which keyword sorts biggest first?', ['ASC', 'DESC', 'UP', 'DOWN'], 1, 'Descending.', 'DESC means descending.')
K.quiz('m', 'Which is evaluated first without brackets?', ['OR', 'AND', 'Left to right always', 'NOT never'], 1, 'Like × before +.', 'AND binds tighter than OR.')
K.quiz('m', "What does '_a%' match?", ['Names starting with a', 'Names whose second letter is a', 'Names ending with a', 'Names with exactly 2 letters'], 1, 'One character, then a.', '_ is one character, then a, then anything.')
K.quiz('m', 'In SQLite ascending order, where do NULLs go?', ['First', 'Last', 'They are removed', 'Random'], 0, 'Smallest.', 'SQLite treats NULL as smaller than any value.')
K.quiz('m', "category IN ('Sports', 'Kitchen') is the same as", ["category = 'Sports' AND category = 'Kitchen'", "category = 'Sports' OR category = 'Kitchen'", "category LIKE 'Sports%Kitchen'", 'NOT category'], 1, 'Any of.', 'IN is a short form of several ORs.')
K.quiz('h', 'ORDER BY category, price DESC sorts price descending', ['For the whole table', 'Inside each category', 'Only for NULLs', 'Never, DESC applies to category'], 1, 'Tie breaker.', 'DESC applies only to price, which breaks ties within a category.')
K.quiz('h', 'Which pattern matching is case sensitive in SQLite by default?', ['LIKE', 'GLOB', 'Both', 'Neither'], 1, 'Unix style.', 'GLOB is case sensitive, LIKE is not for ASCII letters.')
K.quiz('x', 'Why can ORDER BY use a SELECT alias while WHERE cannot?', ['A rule of SQLite only', 'WHERE runs before SELECT, ORDER BY after it', 'Aliases need quotes', 'WHERE is faster'], 1, 'Logical order.', 'The alias does not exist yet when WHERE runs.')

c_between = value('shop', 'SELECT count(*) FROM products WHERE price BETWEEN 100 AND 300')
c_noprec = value('shop', "SELECT count(*) FROM products WHERE category = 'Sports' OR category = 'Kitchen' AND price < 300")
c_prec = value('shop', "SELECT count(*) FROM products WHERE (category = 'Sports' OR category = 'Kitchen') AND price < 300")
K.calc('e', 'How many products cost from 100 to 300, both included?', str(c_between), 'BETWEEN includes both ends.',
       ['Prices: 120, 60, 250, 399, 1499, 699, 180, 850, 1250, 95.', 'In range: 120, 250, 180.', eq(f'{c_between} products')], check=c_between)
K.calc('e', 'How many customers live in Delhi?', str(value('shop', "SELECT count(*) FROM customers WHERE city = 'Delhi'")), "city = 'Delhi'.",
       ['Read the city column.', 'Ravi and Nisha live in Delhi.', eq('2 customers')], check=value('shop', "SELECT count(*) FROM customers WHERE city = 'Delhi'"))
K.calc('m', "How many rows does WHERE category = 'Sports' OR category = 'Kitchen' AND price < 300 keep?", str(c_noprec), 'AND first.',
       ['It means Sports OR (Kitchen AND price &lt; 300).', 'Sports: Cricket ball, Football. Cheap Kitchen: Water bottle.', eq(f'{c_noprec} rows')], check=c_noprec)
K.calc('m', 'And with brackets, (Sports OR Kitchen) AND price &lt; 300?', str(c_prec), 'Price applies to both.',
       ['Sports under 300: Cricket ball.', 'Kitchen under 300: Water bottle.', eq(f'{c_prec} rows')], check=c_prec)
K.calc('m', "How many product names match LIKE '%o%'? (LIKE ignores case)", str(value('shop', "SELECT count(*) FROM products WHERE name LIKE '%o%'")), 'Any o anywhere.',
       ['Check each name for the letter o.', 'Pencil box, Notebook, Water bottle, Lunch box, Headphones, Phone charger, Football, Geometry set.', eq(f'{value("shop", "SELECT count(*) FROM products WHERE name LIKE %s" % repr("%o%"))} names')], check=value('shop', "SELECT count(*) FROM products WHERE name LIKE '%o%'"))
K.calc('m', 'How many orders are not delivered? Use status &lt;&gt; delivered.', str(value('shop', "SELECT count(*) FROM orders WHERE status <> 'delivered'")), 'Count the rest.',
       ['There are 10 orders.', f'{value("shop", "SELECT count(*) FROM orders WHERE status = %s" % repr("delivered"))} are delivered.', eq(f'10 − {value("shop", "SELECT count(*) FROM orders WHERE status = %s" % repr("delivered"))} = {value("shop", "SELECT count(*) FROM orders WHERE status <> %s" % repr("delivered"))}')], check=value('shop', "SELECT count(*) FROM orders WHERE status <> 'delivered'"))
K.calc('h', 'How many rows does WHERE email = NULL return?', '0', 'Comparing with unknown.',
       ['email = NULL gives NULL for every row.', 'WHERE keeps only true rows.', eq('0 rows')], check=value('shop', 'SELECT count(*) FROM customers WHERE email = NULL'))
K.calc('h', 'Products with stock 0 or price over 1000: how many rows?', str(value('shop', 'SELECT count(*) FROM products WHERE stock = 0 OR price > 1000')), 'Either test.',
       ['Stock 0: Lunch box, Desk lamp.', 'Price over 1000: Headphones, Desk lamp.', eq('Desk lamp counts once: 3 rows')], check=value('shop', 'SELECT count(*) FROM products WHERE stock = 0 OR price > 1000'))

K.must('WHERE', 'Tests every row and keeps only rows where the condition is true. False and unknown rows are dropped.')
K.must('Precedence', 'NOT, then AND, then OR. Add brackets whenever AND and OR are mixed.')
K.must('Ranges and lists', 'BETWEEN a AND b includes both ends. IN (...) is a short form of several ORs.')
K.must('Patterns', 'LIKE: % any run, _ one character, case insensitive for ASCII in SQLite. GLOB is case sensitive.')
K.must('NULL tests', 'Use IS NULL and IS NOT NULL. = NULL never matches.')
K.must('ORDER BY', 'ASC default, DESC for big first, later columns break ties. NULLs sort first in SQLite, NULLS LAST moves them.')

T = K.topic(
    slug='sql-where', topic='sql-where', step=(1, 'Start here', 'sql-start', 'What a database is, tables and keys, what SQL is, and your first queries, filters and sorting.', 'Beginner'),
    title='Filtering and sorting: WHERE and ORDER BY', short='WHERE and ORDER BY', badge='1.3', minutes=40, added='2026-11-23',
    lead='Keep only the rows you need with WHERE, combine tests with AND, OR and brackets, match patterns with LIKE, find missing values, and sort results the way a scoreboard does.',
    desc='WHERE and comparison operators, BETWEEN and IN, AND, OR, NOT and precedence, LIKE, GLOB, IS NULL, ORDER BY with several columns, NULLS FIRST and LAST and collations.',
    summary='WHERE and comparisons, AND OR NOT with brackets, LIKE patterns, IS NULL and ORDER BY.',
    keywords=['WHERE', 'AND', 'OR', 'BETWEEN', 'IN', 'LIKE', 'IS NULL', 'ORDER BY', 'NULLS LAST'],
    recap='<p>WHERE keeps the rows where a test is true, brackets make AND and OR mean what you want, LIKE matches patterns, IS NULL finds gaps, and ORDER BY sorts.</p>')
