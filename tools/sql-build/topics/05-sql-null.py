# Chapter 2.2: NULL and three valued logic. Sources: sqlite.org nulls.html and lang_expr.html (operators give NULL
# when an operand is NULL, AND false wins, OR true wins, IS and IS NOT never give NULL, IS DISTINCT FROM, IN with
# NULL, CASE treats NULL as untrue), lang_aggfunc.html (aggregates skip NULL, count(*) counts rows),
# datatype3.html (NULL sorts first). ISO SQL three valued logic.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('unknown', 'NULL means unknown', f'''
<p>A form asks for your phone number and you leave it blank. The database does not know your number. It is not zero, not an empty string, simply <b>unknown</b>. SQL writes that as <code>NULL</code>. Because NULL is unknown, almost every operation on it gives unknown too: unknown plus 5 is still unknown.</p>
{K.sql('arith', """SELECT 5 + NULL      AS plus,
       NULL * 0      AS times_zero,
       'Hi ' || NULL AS joined,
       NULL = NULL   AS equal,
       NULL IS NULL  AS is_null;""", db='', title='Almost everything with NULL becomes NULL', notes={2: 'Even zero times unknown is unknown in SQL.', 4: 'Two unknowns are not known to be equal.', 5: 'IS NULL is the one test that answers yes or no.'})}
{table(['Value', 'Means', 'length() of it'], [
    ['<code>NULL</code>', 'unknown or missing', 'NULL'],
    ["<code>''</code>", 'a known, empty piece of text', '0'],
    ['<code>0</code>', 'the known number zero', '1 (the text 0)']])}
{K.lab('l-noemail', 'e', 'Who has no email', 'Show the <code>name</code> of every customer whose <code>email</code> is missing.', 'SELECT name FROM customers WHERE email IS NULL;', hint='IS NULL, not = NULL.', why='Only IS NULL can find a missing value.')}
{note("Oracle treats an empty string '' as NULL. SQLite, PostgreSQL, MySQL and SQL Server keep them different. This is a common surprise when moving data between engines.", 'exam')}
''', kw=['NULL', 'unknown', 'missing value', 'empty string', 'NULL arithmetic'])
K.talk('unknown', '''NULL is the way SQL says I do not know. If you leave your phone number blank on a form, the database stores NULL, which is not zero and
not an empty piece of text. Because it is unknown, nearly every operation with NULL also gives NULL. Five plus unknown is unknown, and
even zero times unknown is unknown in SQL. Most surprising of all, NULL equals NULL is not true, it is NULL, because two unknown things
are not known to be the same. The only test that gives a clear yes or no is IS NULL. Oracle is special, it treats empty text as NULL,
while other engines keep them apart. Think of two sealed gift boxes, you cannot say they hold the same thing.''')

K.lesson('three', 'Three valued logic: TRUE, FALSE and UNKNOWN', f'''
<p>Because of NULL, SQL logic has three answers: TRUE, FALSE and UNKNOWN (written as NULL). The rules follow common sense. If you know one side of an AND is false, the whole AND is false, whatever the unknown side is. If you know one side of an OR is true, the whole OR is true.</p>
{pk('sqnull')}
{table(['A', 'B', 'A AND B', 'A OR B'], [
    ['TRUE', 'NULL', 'NULL', 'TRUE'],
    ['FALSE', 'NULL', 'FALSE', 'NULL'],
    ['NULL', 'NULL', 'NULL', 'NULL']])}
<p>The big rule for queries: <b>WHERE keeps a row only when the condition is TRUE</b>. FALSE and UNKNOWN rows are both dropped. This is why a test such as <code>city &lt;&gt; 'Pune'</code> silently leaves out customers whose city is NULL.</p>
{K.sql('lost', """-- Customers not in Pune?
SELECT name, city FROM customers WHERE city <> 'Pune';

-- Arjun (city NULL) is missing above. Add him back explicitly:
SELECT name, city FROM customers WHERE city <> 'Pune' OR city IS NULL;""", title='The row that vanishes', notes={2: "For Arjun, NULL <> 'Pune' is UNKNOWN, so WHERE drops him.", 5: 'IS NULL catches the unknown city.'})}
{steps('Why the count does not add up', [
    f"8 customers in total.",
    f"city = 'Pune' keeps {value('shop', "SELECT count(*) FROM customers WHERE city = 'Pune'")} rows (Asha, Kabir).",
    f"city &lt;&gt; 'Pune' keeps {value('shop', "SELECT count(*) FROM customers WHERE city <> 'Pune'")} rows.",
    eq(f"2 + 5 = 7, not 8. Arjun, with a NULL city, is in neither answer")])}
{K.lab('l-notpune', 'm', 'Everyone outside Pune, really', 'Show the <code>name</code> of every customer who does not live in Pune, including customers whose city is unknown.', "SELECT name FROM customers WHERE city <> 'Pune' OR city IS NULL;", hint='Add OR city IS NULL.', why='A NULL city makes the not equal test UNKNOWN, so it needs its own test.')}
''', kw=['three valued logic', 'UNKNOWN', 'truth table', 'AND', 'OR', 'NOT', 'WHERE drops unknown'])
K.talk('three', '''Because of NULL, SQL logic has three answers, true, false and unknown. The rules follow common sense. For AND, if you already know one side
is false, the whole thing is false, no matter what the unknown side is. For OR, if you know one side is true, the whole thing is true.
Everything else with an unknown stays unknown. The rule that bites people is this. WHERE keeps a row only when the test is true. Unknown
is thrown away just like false. So asking for customers not in Pune quietly leaves out Arjun, whose city is unknown, and the two counts add
up to seven instead of eight. Think of a teacher who only lets in students with a yes on their permission slip, a blank slip stays outside.''')

K.lesson('traps', 'NULL traps: NOT IN, aggregates and DISTINCT', f'''
<p>Three places where NULL changes answers in ways that surprise even experienced developers.</p>
<h3>1. NOT IN with a NULL in the list</h3>
{K.sql('notin', """SELECT name FROM products WHERE id NOT IN (1, 2);
SELECT name FROM products WHERE id NOT IN (1, 2, NULL);""", title='One NULL empties the whole answer', notes={2: 'id NOT IN (1, 2, NULL) means id &lt;&gt; 1 AND id &lt;&gt; 2 AND id &lt;&gt; NULL. The last part is UNKNOWN, so no row is ever TRUE.'})}
<h3>2. Aggregates skip NULLs</h3>
{K.sql('agg', """SELECT COUNT(*)      AS all_rows,
       COUNT(score)  AS scores_known,
       AVG(score)    AS average,
       SUM(score) * 1.0 / COUNT(*) AS average_if_null_were_zero
FROM marks;""", db='school', title='COUNT(*) counts rows, COUNT(column) counts known values', notes={1: 'Counts every row, NULL or not.', 2: 'Counts only rows where score is not NULL.', 3: 'AVG divides by the count of known scores, not by every row.'})}
<h3>3. Grouping and DISTINCT treat NULLs as one group</h3>
<p>For <code>GROUP BY</code>, <code>DISTINCT</code> and <code>UNION</code>, all NULLs are put together as if they were equal. But a <code>UNIQUE</code> column may hold many NULLs, because two unknowns are not known to be the same. The SQLite documentation lists exactly these rules.</p>
{fxs(fx('Safe NULL comparison', '<code>a IS b</code>, <code>a IS NOT b</code>', 'Like = and &lt;&gt;, but NULL IS NULL is TRUE. Never returns NULL. Standard SQL spells it IS NOT DISTINCT FROM.', key=True),
     fx('Fallback', '<code>COALESCE(x, default)</code>', 'Replace NULL with a value before comparing or adding.'),
     fx('Safe NOT IN', '<code>WHERE NOT EXISTS (...)</code>', 'NOT EXISTS is not fooled by NULLs in the subquery. Chapter 3.3 explains it.'))}
{K.lab('l-countnull', 'm', 'Known and unknown scores', 'From the school database, return one row with two columns: <code>total</code>, the number of rows in <code>marks</code>, and <code>missing</code>, the number of rows whose score is NULL.', 'SELECT COUNT(*) AS total, COUNT(*) - COUNT(score) AS missing FROM marks;', db='school', hint='COUNT(*) minus COUNT(score) counts the NULLs.', why='COUNT(column) skips NULLs, so the difference is the number of NULL scores. SUM(score IS NULL) works too.')}
''', kw=['NOT IN', 'NULL in subquery', 'COUNT(*)', 'COUNT(column)', 'AVG ignores NULL', 'IS NOT DISTINCT FROM', 'UNIQUE and NULL'])
K.talk('traps', '''Here are three NULL traps worth remembering. First, NOT IN with a NULL anywhere in the list returns nothing at all, because one of its hidden
not equal tests becomes unknown for every row. Second, aggregate functions skip NULLs. COUNT star counts rows, but COUNT of a column counts
only known values, and AVG divides by the number of known values, which can make an average look higher than you expect. Third, GROUP BY
and DISTINCT put all NULLs into one group, while a UNIQUE column still allows many NULLs. The IS operator compares safely and never gives
unknown. Think of a class attendance sheet where blank boxes are ignored, not counted as absent.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>NULL is a question mark. Sums with a question mark are question marks, and a question mark never passes a strict test.</p>',
    '<p>SQL uses three valued logic. WHERE, HAVING and ON keep only TRUE. CHECK constraints are the opposite: they reject only FALSE, so a NULL passes a CHECK.</p>',
    '<p>NULL breaks some algebra rules people rely on. x = x is not always TRUE, and NOT (a = b) is not the same as a &lt;&gt; b plus the NULL rows. Query rewrites in optimizers must respect this, which is why NOT IN and NOT EXISTS are not always interchangeable.</p>',
    '<p>Codd later proposed two different kinds of missing value: applicable but unknown, and not applicable. Researchers such as Date and Darwen argued against NULL entirely and for designs that avoid it. Modern database theory studies certain answers: results that are true for every possible value the NULLs might take.</p>')}
{deep('CHECK and NULL', "<p>The shop table has <code>CHECK (price &gt; 0)</code>. Inserting a price of NULL would pass that check, because NULL &gt; 0 is UNKNOWN, not FALSE. That is why the column also says NOT NULL. Use both together when a value must exist and follow a rule.</p>")}
''', kw=['CHECK and NULL', 'certain answers', 'Codd', 'Date and Darwen', 'three valued logic'])
K.talk('levels', '''Up the ladder again. For a child, NULL is a question mark, and a question mark never passes a strict test. At college level, WHERE, HAVING
and join conditions keep only true, while a CHECK rule rejects only false, so NULL slips through a CHECK unless the column is also NOT NULL.
At masters level, NULL breaks familiar algebra, x equals x is not always true, so optimizers must be careful when they rewrite queries. At
research level, Codd suggested two kinds of missing value, and other experts argued for designs with no NULL at all. Think of a jury that
can say guilty, not guilty, or we cannot decide.''')

K.quiz('e', 'What is 5 + NULL?', ['5', '0', 'NULL', 'An error'], 2, 'Unknown.', 'Arithmetic with NULL gives NULL.')
K.quiz('e', 'Which test finds missing emails?', ['email = NULL', 'email IS NULL', "email = ''", 'email = 0'], 1, 'IS.', 'Only IS NULL works.')
K.quiz('e', 'What is NULL = NULL?', ['TRUE', 'FALSE', 'NULL', 'An error'], 2, 'Unknown.', 'Two unknowns are not known to be equal.')
K.quiz('e', 'WHERE keeps rows where the condition is', ['TRUE', 'TRUE or NULL', 'not FALSE', 'anything'], 0, 'Strict.', 'Only TRUE passes.')
K.quiz('m', 'FALSE AND NULL is', ['TRUE', 'FALSE', 'NULL', 'An error'], 1, 'False wins in AND.', 'One false side makes AND false.')
K.quiz('m', 'TRUE OR NULL is', ['TRUE', 'FALSE', 'NULL', 'An error'], 0, 'True wins in OR.', 'One true side makes OR true.')
K.quiz('m', 'COUNT(score) counts', ['Every row', 'Rows where score is not NULL', 'Distinct scores', 'NULL scores'], 1, 'Known values.', 'COUNT(column) skips NULLs.')
K.quiz('m', 'A CHECK (price &gt; 0) constraint and a NULL price', ['Rejects it', 'Accepts it', 'Turns it into 0', 'Depends on the engine'], 1, 'CHECK rejects only FALSE.', 'NULL &gt; 0 is UNKNOWN, so the CHECK passes.')
K.quiz('h', 'id NOT IN (1, 2, NULL) returns', ['All rows except 1 and 2', 'No rows', 'Only NULL ids', 'An error'], 1, 'One unknown spoils it.', 'The AND chain always contains an UNKNOWN.')
K.quiz('h', 'Which is TRUE in SQLite?', ['NULL = NULL', 'NULL IS NULL', 'NULL &lt;&gt; NULL', 'NOT NULL'], 1, 'IS never gives NULL.', 'IS treats two NULLs as the same.')
K.quiz('x', 'GROUP BY city with three NULL cities makes', ['Three groups of NULL', 'One NULL group', 'No NULL group', 'An error'], 1, 'Grouping treats NULLs as equal.', 'GROUP BY puts all NULLs in one group.')

total_m = value('school', 'SELECT count(*) FROM marks')
known_m = value('school', 'SELECT count(score) FROM marks')
K.calc('e', 'How many rows are in the marks table?', str(total_m), 'COUNT(*).',
       ['COUNT(*) counts every row.', 'Including the row with a NULL score.', eq(f'{total_m} rows')], check=total_m)
K.calc('e', 'How many marks rows have a known score?', str(known_m), 'COUNT(score).',
       [f'{total_m} rows in total.', '1 score is NULL.', eq(f'{total_m} − 1 = {known_m}')], check=known_m)
K.calc('m', 'What is AVG(score) over marks, to 2 decimal places?', f"{value('school', 'SELECT round(avg(score), 2) FROM marks'):.2f}", 'Divide by known scores only.',
       [f"SUM(score) = {value('school', 'SELECT sum(score) FROM marks')}.", f'Known scores: {known_m}.', eq(f"{value('school', 'SELECT sum(score) FROM marks')} / {known_m} ≈ {value('school', 'SELECT round(avg(score), 2) FROM marks'):.2f}")],
       check=value('school', 'SELECT round(avg(score), 2) FROM marks'), tol=0.005)
K.calc('m', 'If the NULL score counted as 0, what would the average be, to 2 decimals?', f"{value('school', 'SELECT round(sum(score) * 1.0 / count(*), 2) FROM marks'):.2f}", 'Divide by all rows.',
       [f"SUM(score) = {value('school', 'SELECT sum(score) FROM marks')}.", f'All rows: {total_m}.', eq(f"{value('school', 'SELECT sum(score) FROM marks')} / {total_m} ≈ {value('school', 'SELECT round(sum(score) * 1.0 / count(*), 2) FROM marks'):.2f}")],
       check=value('school', 'SELECT round(sum(score) * 1.0 / count(*), 2) FROM marks'), tol=0.005)
K.calc('m', "How many customers does WHERE city &lt;&gt; 'Pune' return?", str(value('shop', "SELECT count(*) FROM customers WHERE city <> 'Pune'")), 'NULL city is dropped.',
       ['8 customers, 2 in Pune.', 'Arjun has a NULL city, which gives UNKNOWN.', eq('8 − 2 − 1 = 5')], check=value('shop', "SELECT count(*) FROM customers WHERE city <> 'Pune'"))
K.calc('h', 'How many rows does SELECT name FROM products WHERE id NOT IN (1, 2, NULL) return?', '0', 'The NULL spoils every row.',
       ['For each row the test includes id &lt;&gt; NULL.', 'That part is UNKNOWN, so the AND is never TRUE.', eq('0 rows')], check=value('shop', 'SELECT count(*) FROM products WHERE id NOT IN (1, 2, NULL)'))
K.calc('h', 'How many groups does SELECT house FROM students GROUP BY house give? (One student has no house.)', str(value('school', 'SELECT count(*) FROM (SELECT house FROM students GROUP BY house)')), 'NULLs form one group.',
       ['Houses: Red, Blue, Green.', 'Plus one NULL group for Gauri.', eq('3 + 1 = 4 groups')], check=value('school', 'SELECT count(*) FROM (SELECT house FROM students GROUP BY house)'))
K.calc('h', 'What does SELECT (NULL IS NULL) + (NULL = NULL IS NULL) return?', '2', 'Both parts are TRUE, which is 1.',
       ['NULL IS NULL is TRUE, stored as 1.', 'NULL = NULL is NULL, and NULL IS NULL is TRUE, so 1.', eq('1 + 1 = 2')], check=value('', 'SELECT (NULL IS NULL) + (NULL = NULL IS NULL)'))

K.must('NULL is unknown', 'Not zero, not empty text. Arithmetic and comparisons with NULL give NULL. NULL = NULL is NULL.')
K.must('Three values', 'TRUE, FALSE, UNKNOWN. FALSE wins in AND, TRUE wins in OR.')
K.must('Filters keep TRUE', 'WHERE, HAVING and ON drop FALSE and UNKNOWN. CHECK rejects only FALSE, so NULL passes a CHECK.')
K.must('Tests', 'IS NULL, IS NOT NULL, a IS b (never NULL). COALESCE gives a fallback.')
K.must('Traps', 'NOT IN with a NULL returns nothing. COUNT(col), SUM, AVG skip NULLs. GROUP BY and DISTINCT treat NULLs as one value.')

T = K.topic(
    slug='sql-null', topic='sql-null', step=(2, 'Shaping results', 'sql-shape', 'Functions and CASE, the truth about NULL, and squeezing many rows into answers with GROUP BY.', 'Beginner'),
    title='NULL and three valued logic', short='NULL explained', badge='2.2', minutes=35, added='2026-11-23',
    lead='Understand the value that means "I do not know", why NULL = NULL is not true, how rows quietly vanish from filters, and the NOT IN and AVG traps that catch professionals.',
    desc='NULL as unknown, NULL arithmetic, three valued logic with truth tables, WHERE keeping only TRUE, IS NULL and IS DISTINCT FROM, NOT IN with NULL, aggregates skipping NULL, grouping NULLs, CHECK and NULL.',
    summary='NULL as unknown, three valued logic, vanishing rows, NOT IN and aggregate traps.',
    keywords=['NULL', 'three valued logic', 'IS NULL', 'NOT IN', 'COUNT(*)', 'unknown'],
    recap='<p>NULL means unknown, logic gains a third value, filters keep only TRUE, and NOT IN, COUNT and AVG each treat NULL in their own way.</p>')
