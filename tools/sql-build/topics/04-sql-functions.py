# Chapter 2.1: built in functions: text, numbers, CASE, COALESCE, NULLIF, IIF, CAST, typeof, dates and times.
# Sources: sqlite.org lang_corefunc.html, lang_datefunc.html (date, time, datetime, julianday, unixepoch, strftime
# and modifiers), lang_expr.html (CASE, CAST), lang_mathfunc.html, datatype3.html (no date storage class).
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('text', 'Text functions', f'''
<p>A function takes values in and gives one value back, like a juicer: fruit in, juice out. SQL has dozens of them. Text functions clean and reshape words, which matters because real data is messy: extra spaces, mixed capitals, codes hidden inside longer strings.</p>
{table(['Function', 'What it gives', 'Example', 'Result'], [
    ['<code>upper(x)</code>, <code>lower(x)</code>', 'capitals or small letters', "<code>upper('pune')</code>", 'PUNE'],
    ['<code>length(x)</code>', 'number of characters', "<code>length('Notebook')</code>", '8'],
    ['<code>substr(x, start, n)</code>', 'n characters from position start (first is 1)', "<code>substr('Bhubaneswar', 1, 4)</code>", 'Bhub'],
    ['<code>trim(x)</code>', 'removes spaces at both ends', "<code>trim('  hi  ')</code>", 'hi'],
    ['<code>replace(x, a, b)</code>', 'swaps every a for b', "<code>replace('a-b-c', '-', '/')</code>", 'a/b/c'],
    ['<code>instr(x, y)</code>', 'position of y inside x, 0 if absent', "<code>instr('asha@mail.in', '@')</code>", '5']])}
{K.sql('txt', """SELECT name,
       upper(name) AS shout,
       length(name) AS letters,
       substr(email, instr(email, '@') + 1) AS domain
FROM customers
WHERE email IS NOT NULL;""", title='Cleaning and cutting text', notes={4: "instr finds the @, substr takes everything after it. With no length given, substr runs to the end."})}
{note('Function names differ between engines. SQLite and PostgreSQL use substr and length. SQL Server uses SUBSTRING and LEN. MySQL has both SUBSTR and SUBSTRING. The idea is the same everywhere.', 'tip')}
{K.lab('l-initial', 'e', 'Initials', 'Show each customer <code>name</code> and a column <code>initial</code> holding the first letter of the name.', 'SELECT name, substr(name, 1, 1) AS initial FROM customers;', hint='substr(name, 1, 1) takes one character from position 1.', why='Positions in SQL strings start at 1, not 0.')}
''', kw=['function', 'upper', 'lower', 'length', 'substr', 'trim', 'replace', 'instr', 'text functions'])
K.talk('text', '''A function takes some values in and gives one value back, a bit like a juicer that takes fruit and gives juice. Text functions are
the ones you will use to clean messy data. Upper and lower change capital letters, length counts characters, trim removes spaces at the
ends, replace swaps one piece of text for another, and substr cuts out a piece. In SQL, positions start at one, not zero, so substr of
name from one for one character gives the first letter. In the example, instr finds the at sign in an email and substr keeps the part
after it, which is the domain. Think of these functions as the scissors, glue and eraser in your pencil box.''')

K.lesson('numbers', 'Numbers and CASE', f'''
{table(['Function', 'What it gives', 'Example', 'Result'], [
    ['<code>round(x, d)</code>', 'x rounded to d decimal places', '<code>round(1499 * 0.9, 1)</code>', '1349.1'],
    ['<code>abs(x)</code>', 'distance from zero', '<code>abs(-7)</code>', '7'],
    ['<code>max(a, b)</code>, <code>min(a, b)</code>', 'with two or more arguments, the biggest or smallest of them', '<code>max(3, 9, 4)</code>', '9'],
    ['<code>ceil(x)</code>, <code>floor(x)</code>', 'round up or down to a whole number (SQLite math functions)', '<code>ceil(2.1)</code>', '3.0'],
    ['<code>x % y</code>', 'remainder', '<code>17 % 5</code>', '2']])}
<p><code>CASE</code> is how SQL says "if this, then that, otherwise something else". It checks each <code>WHEN</code> from top to bottom and returns the <code>THEN</code> of the first true one. If none is true it returns the <code>ELSE</code> value, or NULL when there is no ELSE.</p>
{pk('sqcase')}
{K.sql('case', """SELECT name, stock,
  CASE
    WHEN stock = 0 THEN 'Sold out'
    WHEN stock < 20 THEN 'Hurry, few left'
    ELSE 'In stock'
  END AS badge
FROM products
ORDER BY stock;""", title='Shop badges with CASE', notes={3: 'Checked first. A stock of 0 stops here.', 4: 'Only reached when stock is not 0.', 5: 'Used when no WHEN is true.'})}
{fxs(fx('Searched CASE', "<code>CASE WHEN cond THEN a WHEN cond2 THEN b ELSE c END</code>", 'The first true WHEN wins. A NULL test counts as not true.', key=True),
     fx('Simple CASE', "<code>CASE status WHEN 'pending' THEN 1 WHEN 'shipped' THEN 2 ELSE 3 END</code>", 'Compares one value with each WHEN using =.'),
     fx('IIF', "<code>iif(cond, a, b)</code>", 'A short CASE with one test. In SQLite since 3.32.0 and in SQL Server.'))}
{K.lab('l-case', 'm', 'Pass or fail', 'From the school database, show <code>student_id</code>, <code>course_id</code>, <code>score</code> and a column <code>result</code> that says <code>pass</code> when score is 50 or more and <code>fail</code> otherwise. Only include rows where score is not NULL.', "SELECT student_id, course_id, score, CASE WHEN score >= 50 THEN 'pass' ELSE 'fail' END AS result FROM marks WHERE score IS NOT NULL;", db='school', hint='CASE WHEN score &gt;= 50 THEN ... ELSE ... END AS result.', why='CASE turns a number into a label, one row at a time.')}
''', kw=['round', 'abs', 'ceil', 'floor', 'CASE', 'WHEN', 'THEN', 'ELSE', 'IIF', 'searched case', 'simple case'])
K.talk('numbers', '''Number functions round, take absolute values and find the bigger or smaller of a few values. Round of x with one decimal place keeps
one digit after the point. Then comes CASE, which is the if and else of SQL. It checks its WHEN tests from top to bottom and returns
the answer of the first one that is true. If none is true, it returns the ELSE value, and with no ELSE it returns NULL. The order of the
tests matters. In the badge example, a stock of zero is caught by the first test, so it never reaches the hurry test below it. IIF is a
short form with one test. Think of CASE as a school grading chart, check the top band first and stop at the first band that fits.''')

K.lesson('nulls', 'COALESCE, NULLIF, CAST and typeof', f'''
<p>Missing values are common. <code>COALESCE</code> returns the first argument that is not NULL, which is perfect for a fallback: "show the email, or if there is none, show the word unknown". <code>NULLIF(a, b)</code> does the opposite job: it returns NULL when a equals b, which is a classic trick to avoid dividing by zero.</p>
{K.sql('coal', """SELECT name,
       COALESCE(email, 'no email') AS contact,
       COALESCE(city, 'unknown city') AS place
FROM customers;""", title='Fallback values with COALESCE', notes={2: 'If email is NULL, the text no email is used instead.'})}
{K.sql('cast', """SELECT typeof(42), typeof(4.2), typeof('42'), typeof(NULL),
       CAST('42' AS INTEGER) + 1 AS from_text,
       100 / NULLIF(0, 0) AS safe_divide;""", db='', title='Types, CAST and a safe division', notes={1: 'typeof shows the storage class SQLite chose for a value.', 3: 'NULLIF(0, 0) is NULL, and dividing by NULL gives NULL instead of a failure.'})}
{table(['Storage class in SQLite', 'Holds', 'Example'], [
    ['NULL', 'a missing value', '<code>NULL</code>'],
    ['INTEGER', 'a whole number, stored in 0 to 8 bytes', '<code>42</code>'],
    ['REAL', 'an 8 byte floating point number', '<code>4.2</code>'],
    ['TEXT', 'a string', "<code>'Pune'</code>"],
    ['BLOB', 'raw bytes, stored exactly as given', "<code>x'CAFE'</code>"]])}
{note('SQLite is flexible about types: a column declared INTEGER can still hold text unless the table is STRICT. PostgreSQL, MySQL and SQL Server are strict and will reject or convert the value. Chapter 4.1 covers this in depth.', 'exam')}
{K.lab('l-coal', 'e', 'Fill the gaps', 'Show every customer <code>name</code> and their <code>city</code>, but show the text <code>Online</code> when the city is missing. Call the second column <code>city</code>.', "SELECT name, COALESCE(city, 'Online') AS city FROM customers;", hint="COALESCE(city, 'Online').", why='COALESCE returns the first value that is not NULL.')}
''', kw=['COALESCE', 'NULLIF', 'IFNULL', 'CAST', 'typeof', 'storage class', 'divide by zero'])
K.talk('nulls', '''Missing values are everywhere in real data, so SQL gives you tools for them. COALESCE takes a list and returns the first value that is
not NULL, which makes it perfect for fallbacks, like showing the words no email when the email is missing. NULLIF does the opposite. It
returns NULL when its two values are equal, and a famous use is dividing by NULLIF of a count and zero, so a zero becomes NULL and the
query does not fail. CAST changes a value from one type to another, and typeof tells you how SQLite stored a value. SQLite has five
storage classes: NULL, integer, real, text and blob. Think of COALESCE as a spare tyre, used only when the main one is missing.''')

K.lesson('dates', 'Dates and times', f'''
<p>SQLite has no special date type. It stores dates as <b>TEXT</b> in the ISO 8601 form <code>YYYY-MM-DD HH:MM:SS</code>, as a REAL Julian day number, or as an INTEGER count of seconds since 1970 (Unix time). Its date functions understand all three. Text in ISO form has a big bonus: sorting the text sorts the dates correctly.</p>
{table(['Function', 'Gives', 'Example', 'Result'], [
    ['<code>date(x, modifiers)</code>', 'YYYY-MM-DD', "<code>date('2025-06-01', '+7 days')</code>", '2025-06-08'],
    ['<code>datetime(x)</code>', 'YYYY-MM-DD HH:MM:SS', "<code>datetime('2025-06-01 10:00', '+90 minutes')</code>", '2025-06-01 11:30:00'],
    ['<code>strftime(format, x)</code>', 'any format', "<code>strftime('%m', '2025-06-01')</code>", '06'],
    ['<code>julianday(x)</code>', 'days as a real number', "<code>julianday('2025-06-10') - julianday('2025-06-01')</code>", '9.0'],
    ['<code>unixepoch(x)</code>', 'seconds since 1970-01-01', "<code>unixepoch('1970-01-02')</code>", '86400']])}
{K.sql('dates', """SELECT id, order_date,
       strftime('%Y-%m', order_date) AS month,
       date(order_date, '+5 days') AS deliver_by,
       julianday('2025-07-10') - julianday(order_date) AS days_ago
FROM orders
ORDER BY order_date;""", title='Months, deadlines and day counts', notes={3: "%Y is the 4 digit year, %m the 2 digit month.", 4: "A modifier such as '+5 days' moves the date.", 5: 'Subtracting Julian day numbers gives the gap in days.'})}
{table(['Task', 'SQLite', 'PostgreSQL', 'MySQL', 'SQL Server'], [
    ['Today', "<code>date('now')</code>", '<code>CURRENT_DATE</code>', '<code>CURDATE()</code>', '<code>CAST(GETDATE() AS date)</code>'],
    ['Add 7 days', "<code>date(d, '+7 days')</code>", "<code>d + INTERVAL '7 days'</code>", '<code>DATE_ADD(d, INTERVAL 7 DAY)</code>', '<code>DATEADD(day, 7, d)</code>'],
    ['Year of a date', "<code>strftime('%Y', d)</code>", '<code>EXTRACT(YEAR FROM d)</code>', '<code>YEAR(d)</code>', '<code>YEAR(d)</code>']])}
{scene('the delivery promise', "<p>An app promises delivery within 5 days. Each night a report runs <code>WHERE status &lt;&gt; 'delivered' AND date(order_date, '+5 days') &lt; date('now')</code> to list late orders, so the support team can call those customers before they complain.</p>")}
{K.lab('l-june', 'm', 'Orders in June 2025', "Show the <code>id</code> and <code>order_date</code> of every order placed in June 2025.", "SELECT id, order_date FROM orders WHERE strftime('%Y-%m', order_date) = '2025-06';", hint="strftime('%Y-%m', order_date) gives text such as 2025-06. A BETWEEN on the dates works too.", why="Either strftime or order_date BETWEEN '2025-06-01' AND '2025-06-30' works, because ISO dates compare correctly as text.")}
''', kw=['date', 'datetime', 'strftime', 'julianday', 'unixepoch', 'ISO 8601', 'modifiers', 'date arithmetic'])
K.talk('dates', '''SQLite has no separate date type. It stores dates as text in the ISO form, year then month then day, or as numbers, and its date
functions understand all of them. The ISO text form has a lovely side effect, sorting the text sorts the dates correctly, because the
biggest unit comes first. The date function can move a date with modifiers such as plus five days. strftime formats a date any way you
like, for example percent Y for the year. julianday turns a date into a count of days, so subtracting two of them gives the gap. Each
engine spells these differently, so check the table for PostgreSQL, MySQL and SQL Server. Think of a calendar where every page has a number.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Functions are little machines: put a value in, get a changed value out. CASE is a decision box.</p>',
    '<p>Scalar functions work on one row at a time and return one value. Aggregate functions such as COUNT and SUM, in the next chapters, work on many rows and return one value.</p>',
    '<p>Functions on a column inside WHERE can stop an index from being used. Many engines let you index an expression, for example <code>CREATE INDEX ON customers(lower(email))</code>, so the same expression in WHERE can use it.</p>',
    '<p>Time zones and calendars are hard: daylight saving changes, leap seconds and historical calendar reforms. Systems store times in UTC and convert only for display. PostgreSQL offers timestamp with time zone, which stores an absolute instant and shows it in the session time zone.</p>')}
{deep('Deterministic functions', "<p>A function is deterministic when the same input always gives the same output, such as upper(). random() and date('now') are not. Engines only allow deterministic functions in places such as expression indexes and generated columns, because the stored value must stay correct.</p>")}
''', kw=['scalar function', 'aggregate function', 'expression index', 'UTC', 'time zone', 'deterministic'])
K.talk('levels', '''One last climb. For a beginner, functions are small machines and CASE is a decision box. At college level, scalar functions work on one
row and give one value, while aggregate functions, coming next, squeeze many rows into one value. At masters level, wrapping a column in
a function inside WHERE can stop an index from helping, unless you build an index on that exact expression. At research level, time is
truly hard, with time zones, daylight saving and calendar changes, so real systems store times in UTC and convert only when showing them.
Think of a railway clock in Delhi and one in London, both right, each showing its own local time.''')

K.quiz('e', "What does upper('pune') return?", ['pune', 'Pune', 'PUNE', 'NULL'], 2, 'Capitals.', 'upper turns letters into capitals.')
K.quiz('e', 'COALESCE(NULL, NULL, 5, 7) returns', ['NULL', '5', '7', '12'], 1, 'First not NULL.', 'It returns the first argument that is not NULL.')
K.quiz('e', "What does length('SQL') return?", ['2', '3', '4', 'NULL'], 1, 'Count letters.', 'Three characters.')
K.quiz('e', 'Which keyword ends a CASE expression?', ['STOP', 'END', 'DONE', 'ELSE'], 1, 'End.', 'CASE ... END.')
K.quiz('m', 'A CASE has no ELSE and no WHEN is true. It returns', ['0', 'An error', 'NULL', 'The first THEN'], 2, 'Missing ELSE.', 'Without ELSE the result is NULL.')
K.quiz('m', 'NULLIF(10, 10) returns', ['10', '0', 'NULL', '20'], 2, 'Equal means NULL.', 'NULLIF returns NULL when both arguments are equal.')
K.quiz('m', "substr('Bhubaneswar', 1, 4) returns", ['Bhub', 'hube', 'Bhu', 'swar'], 0, 'Start at 1.', 'Positions start at 1.')
K.quiz('m', 'Why do ISO dates (YYYY-MM-DD) sort correctly as text?', ['SQLite converts them', 'The biggest unit comes first', 'Dates are numbers', 'They do not'], 1, 'Year, month, day.', 'Comparing left to right compares year, then month, then day.')
K.quiz('h', "typeof('42') in SQLite is", ['integer', 'text', 'real', 'numeric'], 1, 'Quotes.', 'A quoted value is text.')
K.quiz('h', 'Which avoids a division by zero in a ratio a / b?', ['a / COALESCE(b, 0)', 'a / NULLIF(b, 0)', 'a / abs(b)', 'a / (b + 0)'], 1, 'Zero becomes NULL.', 'Dividing by NULL gives NULL instead of a failure.')
K.quiz('x', 'Why should times be stored in UTC?', ['UTC is shorter', 'It avoids time zone and daylight saving confusion', 'SQL requires it', 'Indexes need it'], 1, 'One clock.', 'A single absolute clock makes comparisons correct, local time is only for display.')

K.calc('e', "What does length('Geometry set') return? Spaces count.", str(value('', "SELECT length('Geometry set')")), 'Count every character.',
       ['Geometry has 8 letters.', 'A space is 1, set is 3.', eq('8 + 1 + 3 = 12')], check=value('', "SELECT length('Geometry set')"))
K.calc('e', 'What does round(1499 * 0.9, 1) return?', str(value('', 'SELECT round(1499 * 0.9, 1)')), 'Work out, then round.',
       ['1499 × 0.9 = 1349.1.', 'Rounding to 1 decimal keeps 1349.1.', eq('1349.1')], check=value('', 'SELECT round(1499 * 0.9, 1)'))
K.calc('m', "What does instr('asha@mail.in', '@') return?", '5', 'Position of the @.',
       ['a is 1, s is 2, h is 3, a is 4.', 'The @ is next.', eq('5')], check=value('', "SELECT instr('asha@mail.in', '@')"))
K.calc('m', "How many days lie between 2025-06-01 and 2025-07-05? Use julianday.", str(int(value('', "SELECT julianday('2025-07-05') - julianday('2025-06-01')"))), 'June has 30 days.',
       ['From 1 June to 1 July is 30 days.', 'Then 4 more days to 5 July.', eq('30 + 4 = 34 days')], check=value('', "SELECT julianday('2025-07-05') - julianday('2025-06-01')"))
K.calc('m', "What does date('2025-06-28', '+5 days') return? Type it as YYYYMMDD with no dashes.", '20250703', 'June has 30 days.',
       ['28 June + 2 days = 30 June.', '3 more days = 3 July.', eq('2025-07-03, typed 20250703')], check=int(value('', "SELECT replace(date('2025-06-28', '+5 days'), '-', '')")))
K.calc('m', 'How many products get the badge Hurry, few left (stock above 0 and below 20)?', str(value('shop', 'SELECT count(*) FROM products WHERE stock > 0 AND stock < 20')), 'Zero goes to Sold out first.',
       ['Stocks: 40, 150, 25, 0, 12, 30, 60, 8, 0, 70.', 'Above 0 and below 20: 12 and 8.', eq('2 products')], check=value('shop', 'SELECT count(*) FROM products WHERE stock > 0 AND stock < 20'))
K.calc('h', 'How many marks rows give result pass (score 50 or more)? NULL scores are not passes.', str(value('school', 'SELECT count(*) FROM marks WHERE score >= 50')), 'NULL is not 50 or more.',
       ['There are 15 marks rows.', 'One is NULL, and scores below 50: 47.', eq(f'{value("school", "SELECT count(*) FROM marks WHERE score >= 50")} passes')], check=value('school', 'SELECT count(*) FROM marks WHERE score >= 50'))
K.calc('h', "What is unixepoch('1970-01-01 01:00:00')?", '3600', 'Seconds since midnight 1 January 1970.',
       ['One hour after the start of Unix time.', '1 hour = 60 × 60 seconds.', eq('3600')], check=value('', "SELECT unixepoch('1970-01-01 01:00:00')"))

K.must('Text', 'upper, lower, length, substr (positions start at 1), trim, replace, instr and || for joining.')
K.must('CASE', 'CASE WHEN ... THEN ... ELSE ... END. The first true WHEN wins, no ELSE gives NULL.')
K.must('NULL helpers', 'COALESCE returns the first non NULL value. NULLIF(a, b) gives NULL when a = b, handy for safe division.')
K.must('Types', 'SQLite storage classes: NULL, INTEGER, REAL, TEXT, BLOB. typeof shows them, CAST converts.')
K.must('Dates', 'SQLite stores dates as ISO text, Julian day or Unix time. date, datetime, strftime, julianday, unixepoch and modifiers such as +7 days.')

T = K.topic(
    slug='sql-functions', topic='sql-functions', step=(2, 'Shaping results', 'sql-shape', 'Functions and CASE, the truth about NULL, and squeezing many rows into answers with GROUP BY.', 'Beginner'),
    title='Functions, CASE and dates', short='Functions and CASE', badge='2.1', minutes=40, added='2026-11-23',
    lead='Clean text, round numbers, label rows with CASE, give missing values a fallback, check types and work with dates the way an online shop does.',
    desc='Text functions, number functions, searched and simple CASE, IIF, COALESCE, NULLIF, CAST and typeof, SQLite storage classes, and date and time functions with modifiers across engines.',
    summary='Text and number functions, CASE, COALESCE and NULLIF, CAST and types, dates and times.',
    keywords=['functions', 'CASE', 'COALESCE', 'NULLIF', 'CAST', 'typeof', 'date', 'strftime', 'substr'],
    recap='<p>Functions reshape one value at a time, CASE chooses a label, COALESCE fills gaps, and date functions turn ISO text into deadlines and day counts.</p>')
