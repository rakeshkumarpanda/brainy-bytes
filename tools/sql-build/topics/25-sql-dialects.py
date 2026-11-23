# Chapter 8.4: SQL standards and dialects: the ISO SQL standard and its versions, how SQLite, PostgreSQL, MySQL, SQL Server
# and Oracle differ (quoting, strings, booleans, dates, limits, ids, upserts, LIKE case), choosing an engine, and writing
# portable SQL.
# Sources: ISO/IEC 9075 history (SQL-86, SQL-92, SQL:1999, SQL:2003, SQL:2011, SQL:2016, SQL:2023), sqlite.org
# lang_keywords.html (identifier quoting), quirks.html, postgresql.org features.html (standard conformance), MySQL
# sql-mode.html (ANSI_QUOTES, PIPES_AS_CONCAT), learn.microsoft.com T-SQL docs, Oracle SQL Language Reference.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('standard', 'One language, one standard, many dialects', f'''
<p>SQL is an international standard, ISO/IEC 9075. Every engine follows its core, then adds its own extras and spellings. Those local versions are called <b>dialects</b>. The SELECT, JOIN, GROUP BY and window functions you learned work almost everywhere.</p>
{table(['Version', 'Notable additions'], [
    ['SQL-86 and SQL-89', 'the first standard: SELECT, INSERT, UPDATE, DELETE, basic constraints'],
    ['SQL-92', 'explicit JOIN syntax, CASE, CAST, more data types, schema changes'],
    ['SQL:1999', 'recursive CTEs (WITH RECURSIVE), triggers, roles, boolean type'],
    ['SQL:2003', 'window functions, MERGE, sequences and identity columns'],
    ['SQL:2008 and SQL:2011', 'FETCH FIRST, TRUNCATE, temporal (system versioned) tables'],
    ['SQL:2016', 'JSON functions, row pattern recognition (MATCH_RECOGNIZE)'],
    ['SQL:2023', 'property graph queries (SQL/PGQ), a JSON data type']])}
{K.sql('portable', """SELECT c.name,
       COALESCE(c.city, 'unknown') AS city,
       CASE WHEN COUNT(o.id) >= 2 THEN 'regular' ELSE 'new' END AS kind,
       CAST(COUNT(o.id) AS REAL) / 2 AS half
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name, c.city
ORDER BY c.name;""", title='A query that runs unchanged in all five big engines', notes={2: 'COALESCE, CASE and CAST are standard.', 6: 'Listing every selected column in GROUP BY keeps strict engines happy.'})}
{note('Each engine documents how closely it follows the standard. PostgreSQL publishes a feature by feature list, and SQLite lists its quirks on one page. When in doubt, read the engine’s own documentation.', 'tip')}
''', kw=['SQL standard', 'ISO 9075', 'dialect', 'SQL-92', 'SQL:1999', 'SQL:2003', 'SQL:2016', 'SQL:2023', 'portable SQL'])
K.talk('standard', '''SQL is an international standard, numbered ISO nine zero seven five, first published in nineteen eighty six. Every engine follows its core and then adds
its own extras and spellings, which are called dialects. Each new version of the standard added features you have met in this course. Nineteen ninety two
brought the JOIN keyword and CASE, nineteen ninety nine brought recursive queries and triggers, two thousand three brought window functions and MERGE, and
twenty sixteen brought JSON. The query on this page uses only standard pieces and runs unchanged in all five big engines. Think of English spoken in
different countries, with the same grammar and a few different words.''')

K.lesson('diffs', 'Everyday differences between engines', f'''
<p>The same small task is often spelled differently. These are the differences you will meet first.</p>
{pk('sqdialect')}
{table(['Task', 'SQLite', 'PostgreSQL', 'MySQL', 'SQL Server', 'Oracle'], [
    ['Quote a name', '"order"', '"order"', '`order`', '[order]', '"ORDER"'],
    ['First 3 rows', 'LIMIT 3', 'LIMIT 3', 'LIMIT 3', 'TOP 3', 'FETCH FIRST 3 ROWS ONLY'],
    ['Join text', "a || b", "a || b", 'CONCAT(a, b)', 'a + b', "a || b"],
    ['True or false', '1 and 0', 'true and false', 'TRUE (= 1)', 'bit 1 and 0', 'BOOLEAN in 23ai, else 1 and 0'],
    ['Today', "date('now')", 'CURRENT_DATE', 'CURDATE()', 'CAST(GETDATE() AS date)', 'TRUNC(SYSDATE)'],
    ['Auto id', 'INTEGER PRIMARY KEY', 'GENERATED AS IDENTITY', 'AUTO_INCREMENT', 'IDENTITY(1,1)', 'GENERATED AS IDENTITY'],
    ['Upsert', 'ON CONFLICT', 'ON CONFLICT, MERGE', 'ON DUPLICATE KEY UPDATE', 'MERGE', 'MERGE'],
    ['LIKE and case', 'ignores case for ASCII', 'case sensitive, ILIKE ignores', 'depends on collation, often ignores', 'depends on collation', 'case sensitive']])}
{K.sql('quote', """CREATE TABLE "order" ("group" TEXT, "select" INTEGER);
INSERT INTO "order" VALUES ('a', 1);
SELECT "group", "select" FROM "order";""", db='', title='Reserved words as names need quoting', notes={1: 'order, group and select are keywords. Double quotes are the standard way to use them as names, but it is simpler to avoid them.'})}
{K.sql('likecase', """SELECT name FROM products WHERE name LIKE 'pen%';
SELECT 'Pen' = 'pen' AS equal_text;""", title='A SQLite quirk: LIKE ignores case, = does not', notes={1: 'Finds Pencil box, even though the pattern starts with a small p.', 2: '0: plain comparison is case sensitive.'})}
{note('Moving a database between engines usually breaks on dates, booleans, auto ids and string concatenation, not on SELECT or JOIN. Test those first.', 'warn')}
{K.lab('l-coalesce', 'e', 'The portable way to fill NULLs', 'Show every customer <code>name</code> and <code>email</code>, using the standard COALESCE to show <code>no email</code> when it is missing.',
"""SELECT name, COALESCE(email, 'no email') AS email FROM customers;""", hint="COALESCE(email, 'no email') AS email", why='COALESCE works in every engine, while IFNULL, ISNULL and NVL are each local spellings.')}
''', kw=['dialect differences', 'identifier quoting', 'LIMIT vs TOP', 'string concatenation', 'boolean', 'ILIKE', 'collation'])
K.talk('diffs', '''The same small task is often spelled differently. SQLite and PostgreSQL quote names with double quotes, MySQL uses backticks, and SQL Server uses square
brackets. LIMIT gives the first few rows in SQLite, PostgreSQL and MySQL, while SQL Server writes TOP and the standard says FETCH FIRST. Joining text uses
two bars in most engines, but CONCAT in MySQL and a plus sign in SQL Server. In the animation, pick a task and see five spellings side by side, then the
SQLite one runs for real. One SQLite quirk stands out, LIKE ignores letter case for plain English letters, while equals does not. Think of the word for
lift in British English and elevator in American English.''')

K.lesson('choose', 'Choosing an engine', f'''
<p>There is no best database, only a best fit. These are the engines you are most likely to meet.</p>
{table(['Engine', 'Strengths', 'Typical home'], [
    ['SQLite', 'a single file, no server, zero setup, extremely widely deployed', 'phones, browsers, desktop apps, small sites, tests'],
    ['PostgreSQL', 'rich features, strict standards, extensions (PostGIS, pgvector), open source', 'web apps, analytics, geospatial'],
    ['MySQL and MariaDB', 'simple to run, fast reads, huge hosting support', 'web apps, content management systems'],
    ['SQL Server', 'deep Windows and .NET integration, strong tools', 'enterprise apps, reporting'],
    ['Oracle', 'very large enterprise workloads, many advanced features', 'banks, telecom, large enterprises'],
    ['DuckDB', 'in process analytics on files such as CSV and Parquet', 'data science notebooks, local analytics']])}
{steps('Questions that decide', [
    'Is there one user on one device, or many users over a network. One device points to SQLite.',
    'How much data, and is it mostly small transactions or big reports. Reports point to a column store.',
    'Which features are needed: JSON, full text search, geospatial, vectors.',
    'What does the team already know, and what can it run and back up reliably.'])}
{K.sql('version', """SELECT sqlite_version() AS engine_version;""", db='', title='Which engine is this page running', notes={1: 'Every query on this site runs on SQLite compiled to WebAssembly, inside your browser.'})}
{scene('one app, three databases', '<p>A food delivery startup keeps orders and payments in PostgreSQL, caches menus in Redis, and copies everything nightly into BigQuery for reports. Each phone app also keeps a small SQLite database for offline use. Using the right engine for each job is normal in real systems.</p>')}
''', kw=['SQLite', 'PostgreSQL', 'MySQL', 'MariaDB', 'SQL Server', 'Oracle', 'DuckDB', 'choose a database'])
K.talk('choose', '''There is no best database, only the best fit for a job. SQLite is a single file with no server, perfect inside phones, browsers and desktop apps.
PostgreSQL is rich in features and extensions, and strict about the standard. MySQL and MariaDB are simple to run and supported by almost every web host.
SQL Server fits companies built on Microsoft tools, Oracle serves very large enterprises, and DuckDB runs fast analytics on files right inside a notebook.
Choose by asking how many users there are, how much data, which features you need, and what your team can run and back up safely. Real systems often use
several engines at once. Think of choosing a bicycle, a car or a lorry depending on the load.''')

K.lesson('portable', 'Writing SQL that travels', f'''
<p>If your SQL may run on more than one engine, a few habits save a lot of rewriting.</p>
{table(['Prefer', 'Instead of'], [
    ['COALESCE(x, d)', 'IFNULL, ISNULL, NVL'],
    ['CASE WHEN ... END', 'IIF, IF(), DECODE'],
    ['CAST(x AS INTEGER)', 'implicit conversions and engine specific functions'],
    ['explicit JOIN ... ON', 'commas in FROM with join conditions in WHERE'],
    ['ISO dates as text: \'2025-07-15\'', 'local formats such as 15/07/25'],
    ['every non aggregated column in GROUP BY', 'relying on MySQL or SQLite letting you skip them'],
    ['names without spaces or keywords', 'quoted names that each engine quotes differently']])}
{K.sql('groupby', """SELECT category, name, MAX(price)
FROM products GROUP BY category;""", title='A query SQLite accepts but strict engines refuse', notes={1: 'name is neither grouped nor aggregated. SQLite returns the name from the row holding the MAX, PostgreSQL and SQL Server report an error.'})}
{K.sql('cast', """SELECT '10' + 5 AS sqlite_adds, CAST('10' AS INTEGER) + 5 AS portable,
       10 / 4 AS integer_division, 10 / 4.0 AS real_division;""", db='', title='Conversions and division behave differently', notes={1: 'SQLite quietly turns text into a number. Write CAST so the intent is clear everywhere.', 2: 'Integer division gives 2 in SQLite, PostgreSQL and SQL Server, but 2.5000 in MySQL.'})}
{K.lab('l-case', 'm', 'CASE instead of IIF', 'Show every product <code>name</code> and <code>level</code>: <code>high</code> when price is at least 1000, otherwise <code>normal</code>, using standard CASE.',
"""SELECT name, CASE WHEN price >= 1000 THEN 'high' ELSE 'normal' END AS level FROM products;""", hint="CASE WHEN price >= 1000 THEN 'high' ELSE 'normal' END", why='CASE is standard SQL and works in every engine.')}
{K.lab('l-strict', 'h', 'A GROUP BY strict engines accept', 'Show each <code>category</code> and the <code>name</code> of its most expensive product, written so that PostgreSQL would accept it (no ungrouped columns).',
"""SELECT p.category, p.name FROM products p JOIN (SELECT category, MAX(price) AS mx FROM products GROUP BY category) m ON m.category = p.category AND m.mx = p.price;""", hint='Find MAX(price) per category in a derived table, then join back to products.', why='Every selected column is either grouped inside the subquery or comes from a real row through the join.')}
{K.lab('l-cast', 'm', 'Sum numbers stored as text', 'A table <code>raw (amount TEXT)</code> holds <code>\'10\'</code>, <code>\'25\'</code> and <code>\'5\'</code>. Return <code>total</code>, their sum, using CAST.',
"""SELECT SUM(CAST(amount AS INTEGER)) AS total FROM raw;""", db='', setup="CREATE TABLE raw (amount TEXT); INSERT INTO raw VALUES ('10'), ('25'), ('5');", hint='SUM(CAST(amount AS INTEGER))', why='CAST makes the conversion explicit, so every engine gives 40.')}
''', kw=['portable SQL', 'CAST', 'COALESCE', 'CASE', 'GROUP BY strict', 'integer division', 'ISO date'])
K.talk('portable', '''If your SQL may run on more than one engine, a few habits help. Use COALESCE instead of local names such as IFNULL or NVL, CASE instead of IIF, and
CAST instead of hidden conversions. Write joins with JOIN and ON, keep dates in the ISO year month day form, and list every non aggregated column in GROUP
BY, because SQLite and older MySQL let you skip them while PostgreSQL refuses. Watch division too, ten divided by four gives two in most engines but two
point five in MySQL. Think of writing a letter in plain words so readers from any region understand it.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>SQL is one language with local accents. The core you learned works everywhere, and small things such as dates and quoting differ.</p>',
    '<p>Know the standard versions and the common differences, prefer standard functions, and test on the engine you deploy to.</p>',
    '<p>Dialect gaps are handled by ORMs, query builders and transpilers such as SQLGlot, which parse one dialect and print another. Conformance is measured feature by feature against ISO/IEC 9075 parts, such as Foundation (part 2) and SQL/JSON.</p>',
    '<p>Research looks at automatically translating and verifying SQL across engines, at formal semantics of SQL (proving two queries always return the same rows), and at natural language to SQL with large language models, measured on benchmarks such as Spider and BIRD.</p>')}
{deep('Why SQL has lasted', '<p>SQL started as SEQUEL at IBM in 1974 (Chamberlin and Boyce), built on Codd’s relational model. Many languages tried to replace it, yet it remains the common language of data, because it describes what to find and leaves the how to the engine, so each new engine can be faster without changing your queries.</p>')}
''', kw=['SQLGlot', 'transpiler', 'ISO conformance', 'SQL semantics', 'text to SQL', 'SEQUEL', 'Chamberlin Boyce'])
K.talk('levels', '''Here is the last ladder of this step. For a beginner, SQL is one language with local accents. At college level, know the standard versions and the common
differences, and test on the engine you will really use. At masters level, tools such as SQLGlot translate queries between dialects. At research level,
people prove when two queries always give the same rows, and build systems that turn plain questions into SQL. SQL began as SEQUEL at IBM in nineteen
seventy four, and it has lasted because it says what you want and lets each engine find the fastest way. Think of a recipe that any kitchen can cook.''')

K.quiz('e', 'The SQL standard is published by', ['Google', 'ISO and IEC', 'Microsoft only', 'Oracle only'], 1, 'International.', 'ISO/IEC 9075.')
K.quiz('e', 'A dialect is', ['A bug', 'An engine’s own version of SQL', 'A table', 'A backup format'], 1, 'Local version.', 'Standard core plus local extras.')
K.quiz('e', 'SQL Server writes the first 3 rows as', ['LIMIT 3', 'TOP 3', 'FIRST 3', 'ROWNUM 3'], 1, 'Top.', 'SELECT TOP 3 ...')
K.quiz('e', 'Which function works in every big engine?', ['IFNULL', 'NVL', 'COALESCE', 'ISNULL'], 2, 'Standard.', 'COALESCE is standard SQL.')
K.quiz('m', 'MySQL quotes a column name with', ['Double quotes by default', 'Backticks', 'Square brackets', 'Braces'], 1, 'Backtick.', 'Unless ANSI_QUOTES mode is on.')
K.quiz('m', 'Window functions entered the standard in', ['SQL-92', 'SQL:1999', 'SQL:2003', 'SQL:2016'], 2, '2003.', 'SQL:2003.')
K.quiz('m', 'In SQLite, \'Pen\' LIKE \'pen\' is', ['False', 'True', 'An error', 'NULL'], 1, 'Case insensitive for ASCII.', 'LIKE ignores ASCII case by default.')
K.quiz('m', 'PostgreSQL’s case insensitive LIKE is', ['ILIKE', 'NLIKE', 'LIKE CASE', 'SIMILAR'], 0, 'I for insensitive.', 'ILIKE.')
K.quiz('m', 'SELECT 10 / 4 in MySQL gives', ['2', '2.5000', 'An error', '3'], 1, 'Decimal division.', 'MySQL / always returns a decimal.')
K.quiz('h', 'SELECT category, name, MAX(price) ... GROUP BY category is refused by', ['SQLite', 'PostgreSQL', 'Neither', 'Both'], 1, 'Strict grouping.', 'PostgreSQL requires name to be grouped or aggregated.')
K.quiz('x', 'Which standard added property graph queries to SQL?', ['SQL:2011', 'SQL:2016', 'SQL:2023', 'SQL-92'], 2, 'Newest.', 'SQL:2023 part 16, SQL/PGQ.')

K.calc('e', 'How many years passed between SQL-86 and SQL:2023?', '37', 'Subtract.',
       ['The first standard was 1986.', 'The latest here is 2023.', eq('2023 − 1986 = 37 years')], check=37)
K.calc('e', 'What does SQLite return for 10 / 4?', str(value('', 'SELECT 10 / 4')), 'Integer division.',
       ['Both numbers are integers.', 'The fraction is dropped.', eq('10 / 4 = 2')], check=value('', 'SELECT 10 / 4'))
K.calc('m', 'And for 10 / 4.0?', str(value('', 'SELECT 10 / 4.0')), 'One real operand.',
       ['4.0 is a real number.', 'So the division keeps the fraction.', eq('2.5')], check=value('', 'SELECT 10 / 4.0'))
K.calc('m', "What does SQLite return for '10' + 5?", str(value('', "SELECT '10' + 5")), 'Text becomes a number.',
       ["SQLite converts '10' to 10.", 'Then adds.', eq('10 + 5 = 15')], check=value('', "SELECT '10' + 5"))
nl = value('shop', "SELECT count(*) FROM products WHERE name LIKE 'pen%'")
K.calc('m', "How many products does WHERE name LIKE 'pen%' find in SQLite?", str(nl), 'Case is ignored.',
       ['Pencil box starts with Pen.', 'LIKE ignores ASCII case in SQLite.', eq(f'{nl} product')], check=nl)
K.calc('m', 'In PostgreSQL, the same LIKE \'pen%\' would find how many?', '0', 'Case sensitive.',
       ['PostgreSQL LIKE is case sensitive.', 'No name starts with a small p.', eq('0, use ILIKE to get 1')], check=0)
K.calc('h', 'In the portable query, how many customers are labelled regular (2 or more orders)?', str(value('shop', 'SELECT count(*) FROM (SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) >= 2)')), 'Count customers with 2+ orders.',
       ['Asha has 3 orders, Ravi 2, Meera 2, Sara 2.', 'Nisha has 1.', eq(f"{value('shop', 'SELECT count(*) FROM (SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) >= 2)')} customers")], check=value('shop', 'SELECT count(*) FROM (SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) >= 2)'))
K.calc('h', 'In the raw table, what is SUM(CAST(amount AS INTEGER)) for \'10\', \'25\', \'5\'?', '40', 'Add.',
       ['CAST turns each text into a number.', '10 + 25 + 5.', eq('40')], check=value('', 'SELECT SUM(CAST(amount AS INTEGER)) FROM raw', setup="CREATE TABLE raw (amount TEXT); INSERT INTO raw VALUES ('10'), ('25'), ('5');"))

K.must('Standard', 'ISO/IEC 9075. Key versions: SQL-92 joins and CASE, 1999 recursion and triggers, 2003 window functions, 2016 JSON, 2023 graphs.')
K.must('Differences', 'Quoting, LIMIT or TOP, text joining, booleans, dates, auto ids, upserts and LIKE case differ between engines.')
K.must('Choosing', 'SQLite for one device, PostgreSQL or MySQL for web apps, SQL Server and Oracle in enterprises, column stores for analytics.')
K.must('Portable habits', 'COALESCE, CASE, CAST, explicit JOIN, ISO dates, full GROUP BY lists, plain names.')
K.must('Test where you deploy', 'Run your SQL on the engine you will use. Dates, division and conversions differ most.')

T = K.topic(
    slug='sql-dialects', topic='sql-dialects', step=(8, 'Professional SQL', 'sql-pro', 'Logic inside the database, security, scaling to many machines, and the differences between engines.', 'Advanced'),
    title='SQL standards and dialects', short='Standards and dialects', badge='8.4', minutes=30, added='2026-11-23',
    lead='See how the ISO SQL standard grew, how SQLite, PostgreSQL, MySQL, SQL Server and Oracle differ in everyday tasks, how to choose an engine, and how to write SQL that travels.',
    desc='ISO/IEC 9075 and its versions, quoting, LIMIT, TOP and FETCH FIRST, string concatenation, booleans, dates, identity columns, upserts, LIKE and case, choosing between SQLite, PostgreSQL, MySQL, SQL Server, Oracle and DuckDB, portable SQL habits, SQLGlot.',
    summary='The SQL standard, dialect differences, choosing an engine and portable SQL.',
    keywords=['SQL standard', 'dialect', 'PostgreSQL', 'MySQL', 'SQL Server', 'Oracle', 'portable SQL'],
    recap='<p>One standard, many accents: learn the core, know the common differences, and test on the engine you deploy.</p>')
