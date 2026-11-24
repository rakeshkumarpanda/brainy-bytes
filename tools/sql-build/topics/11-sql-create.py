# Chapter 4.1: building tables: CREATE TABLE, column types in common engines, SQLite type affinity, STRICT tables,
# constraints (NOT NULL, UNIQUE, CHECK, DEFAULT, PRIMARY KEY, FOREIGN KEY), ALTER TABLE and DROP TABLE.
# Sources: sqlite.org lang_createtable.html (constraints, CHECK passes when NULL, INTEGER PRIMARY KEY), datatype3.html
# (five affinities and the rules that pick them), stricttables.html (INT, INTEGER, REAL, TEXT, BLOB, ANY),
# lang_altertable.html (RENAME, ADD COLUMN, DROP COLUMN), postgresql.org datatype.html, MySQL data-types.html.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('create', 'CREATE TABLE: drawing the empty form', f'''
<p>Until now every table already existed. Now you build your own. <code>CREATE TABLE</code> describes an empty table: its name, its columns, the kind of data each column holds, and the rules every row must follow. Think of printing a blank admission form before any student fills it in.</p>
{fxs(fx('Create a table', '<code>CREATE TABLE name (column type constraints, ...);</code>', 'One line per column. Constraints can follow each column, or come at the end for rules that cover several columns.', key=True),
     fx('Only if missing', '<code>CREATE TABLE IF NOT EXISTS name (...);</code>', 'Does nothing, without an error, when the table is already there. Handy in setup scripts that run more than once.'))}
{K.sql('first', """CREATE TABLE books (
  id      INTEGER PRIMARY KEY,
  title   TEXT NOT NULL,
  author  TEXT,
  pages   INTEGER,
  price   REAL
);
INSERT INTO books (title, author, pages, price)
VALUES ('Malgudi Days', 'R. K. Narayan', 256, 199.0),
       ('Wings of Fire', 'A. P. J. Abdul Kalam', 180, 250.0);
SELECT * FROM books;""", db='', title='Your first table, from nothing', notes={2: 'INTEGER PRIMARY KEY in SQLite numbers rows by itself: 1, 2, 3.', 3: 'NOT NULL: every book must have a title.', 8: 'We leave out id, and SQLite fills it in.'})}
{table(['Kind of data', 'SQLite', 'PostgreSQL', 'MySQL', 'SQL Server'], [
    ['Whole numbers', 'INTEGER', 'integer, bigint', 'INT, BIGINT', 'int, bigint'],
    ['Exact money', 'INTEGER (store paise)', 'numeric(10,2)', 'DECIMAL(10,2)', 'decimal(10,2)'],
    ['Decimals, approximate', 'REAL', 'double precision', 'DOUBLE', 'float'],
    ['Text', 'TEXT', 'text, varchar(n)', 'VARCHAR(n)', 'nvarchar(n)'],
    ['Dates and times', 'TEXT in ISO 8601 form', 'date, timestamp', 'DATE, DATETIME', 'date, datetime2'],
    ['True or false', 'INTEGER 0 or 1', 'boolean', 'BOOLEAN (TINYINT(1))', 'bit'],
    ['Raw bytes', 'BLOB', 'bytea', 'BLOB', 'varbinary']])}
{note('Never store money in a floating point column. 0.1 + 0.2 is not exactly 0.3 in binary. Use a DECIMAL type, or store whole paise or cents as an integer, as our products table does with prices in rupees.', 'warn')}
{K.lab('l-pets', 'e', 'A table for pets', 'Create a table <code>pets</code> with <code>id INTEGER PRIMARY KEY</code>, <code>name TEXT NOT NULL</code> and <code>kind TEXT</code>. Add Bruno the dog and Mitthu the parrot, then show <code>name</code> and <code>kind</code> of every pet.',
"""CREATE TABLE pets (id INTEGER PRIMARY KEY, name TEXT NOT NULL, kind TEXT);
INSERT INTO pets (name, kind) VALUES ('Bruno', 'dog'), ('Mitthu', 'parrot');
SELECT name, kind FROM pets;""", db='', hint='Three statements: CREATE TABLE, INSERT with two rows, then SELECT.', why='The final SELECT returns the two rows you stored.')}
''', kw=['CREATE TABLE', 'data types', 'IF NOT EXISTS', 'INTEGER PRIMARY KEY', 'VARCHAR', 'DECIMAL', 'money type'])
K.talk('create', '''Until now every table already existed, and now you learn to build your own. CREATE TABLE describes an empty table, with a name, the columns,
the kind of data each column holds, and the rules each row must follow. It is like printing a blank admission form before any student fills it in.
Each engine has its own type names, integer, text, decimal, date and boolean, and the table on this page lines them up side by side. One rule matters
everywhere. Never keep money in a floating point column, because one tenth cannot be stored exactly in binary. Use a decimal type, or store whole
paise as an integer. Think of a shopkeeper who counts coins rather than guessing the weight of a coin bag.''')

K.lesson('constraints', 'Constraints: rules every row must obey', f'''
<p>A <b>constraint</b> is a rule stored with the table. The database checks it on every INSERT and UPDATE, from every app, so bad data cannot sneak in through a program that forgot to check.</p>
{table(['Constraint', 'Rule', 'Example'], [
    ['NOT NULL', 'the column must have a value', 'name TEXT NOT NULL'],
    ['UNIQUE', 'no two rows share this value (NULLs are allowed, and do not clash)', 'email TEXT UNIQUE'],
    ['PRIMARY KEY', 'unique and identifies the row', 'id INTEGER PRIMARY KEY'],
    ['CHECK (test)', 'the test must not be false', 'CHECK (price > 0)'],
    ['DEFAULT value', 'used when the INSERT leaves the column out', "status TEXT DEFAULT 'new'"],
    ['REFERENCES t(c)', 'the value must exist in another table', 'customer_id INTEGER REFERENCES customers(id)']])}
{pk('sqcheck')}
{K.sql('checkfail', """CREATE TABLE members (
  id    INTEGER PRIMARY KEY,
  name  TEXT NOT NULL,
  email TEXT UNIQUE,
  age   INTEGER CHECK (age >= 18)
);
INSERT INTO members (name, email, age) VALUES ('Asha', 'asha@mail.in', 30);
INSERT INTO members (name, email, age) VALUES ('Tara', 'tara@mail.in', 15);""", db='', title='A CHECK rule stops a bad row', err=True, notes={5: 'The rule written once, inside the table.', 8: 'Age 15 makes the CHECK false, so SQLite refuses the row.'})}
{K.sql('default', """CREATE TABLE tickets (
  id      INTEGER PRIMARY KEY,
  title   TEXT NOT NULL,
  status  TEXT NOT NULL DEFAULT 'open',
  made_on TEXT DEFAULT (date('2025-07-01'))
);
INSERT INTO tickets (title) VALUES ('Printer jam');
SELECT * FROM tickets;""", db='', title='DEFAULT fills in what you leave out', notes={4: 'A plain value as the default.', 5: 'An expression in brackets can be a default too. Real systems often use CURRENT_TIMESTAMP.'})}
{steps('A CHECK rule and NULL', [
    'CHECK refuses a row only when its test is <b>false</b>.',
    'With age NULL, <code>age >= 18</code> is unknown, not false.',
    'So the row is accepted. Add NOT NULL as well if the age must be known.',
    eq('CHECK passes on TRUE and on UNKNOWN, it fails only on FALSE')])}
{K.lab('l-check', 'm', 'Prices must be positive', 'Create <code>items</code> with <code>name TEXT NOT NULL</code> and <code>price INTEGER CHECK (price > 0)</code>. Insert Pen at 10 and Eraser at 5, then show every row ordered by name.',
"""CREATE TABLE items (name TEXT NOT NULL, price INTEGER CHECK (price > 0));
INSERT INTO items VALUES ('Pen', 10), ('Eraser', 5);
SELECT * FROM items ORDER BY name;""", db='', hint='Put the CHECK right after the price type.', why='Both prices pass the CHECK, so both rows are stored.', ordered=True)}
''', kw=['constraint', 'NOT NULL', 'UNIQUE', 'CHECK', 'DEFAULT', 'data integrity', 'CHECK and NULL'])
K.talk('constraints', '''A constraint is a rule stored with the table itself, so the database checks it on every insert and update, no matter which program sends the
data. NOT NULL means a value must be present. UNIQUE means no two rows may share the value. CHECK runs a test and refuses the row only when the test
is false. DEFAULT fills in a value when the insert leaves the column out. In the animation, type a new member and watch each rule test the row in turn.
Try an empty name, the email asha at mail dot in, or an age of fifteen, and see which rule stops it. One surprise is that a CHECK passes when the
value is NULL, because unknown is not false. Think of a security guard at a gate who checks every visitor against the same list.''')

K.lesson('affinity', 'How SQLite treats types, and STRICT tables', f'''
<p>Most engines refuse text in an integer column. SQLite is more relaxed: a column’s type gives it an <b>affinity</b>, a preference, and SQLite converts values to that preference when it can. When it cannot, it stores the value as it is.</p>
{table(['Declared type contains', 'Affinity', 'Example'], [
    ['INT', 'INTEGER', 'INT, INTEGER, BIGINT'],
    ['CHAR, CLOB or TEXT', 'TEXT', 'VARCHAR(20), TEXT'],
    ['BLOB, or no type at all', 'BLOB', 'BLOB'],
    ['REAL, FLOA or DOUB', 'REAL', 'REAL, DOUBLE, FLOAT'],
    ['anything else', 'NUMERIC', 'DECIMAL(10,2), BOOLEAN, DATE']])}
{K.sql('affinity', """CREATE TABLE loose (n INTEGER, t TEXT);
INSERT INTO loose VALUES ('42', 42), ('hello', 7);
SELECT n, typeof(n), t, typeof(t) FROM loose;""", db='', title='Affinity converts when it can', notes={2: "'42' becomes the integer 42. 'hello' cannot become a number, so it stays text even in an INTEGER column.", 3: 'typeof shows what was really stored.'})}
<p>Since version 3.37 (2021) SQLite also offers <b>STRICT</b> tables. A STRICT table allows only the types INT, INTEGER, REAL, TEXT, BLOB and ANY, and refuses a value that cannot be converted losslessly, the way other engines do.</p>
{K.sql('strict', """CREATE TABLE tight (n INTEGER, t TEXT) STRICT;
INSERT INTO tight VALUES ('42', 42);
SELECT n, typeof(n), t, typeof(t) FROM tight;
INSERT INTO tight VALUES ('hello', 7);""", db='', title='STRICT refuses what does not fit', err=True, notes={2: "'42' still converts cleanly to 42, so it is accepted.", 4: "'hello' cannot be an integer, and a STRICT table says no."})}
{note('When you move a design from SQLite to PostgreSQL or MySQL, a STRICT table behaves much closer to what you will meet there.', 'tip')}
{K.lab('l-typeof', 'm', 'What really got stored', 'Create <code>t (a INTEGER, b TEXT)</code>, insert the row <code>(\'7\', 7)</code>, then show <code>typeof(a)</code> and <code>typeof(b)</code>.',
"""CREATE TABLE t (a INTEGER, b TEXT);
INSERT INTO t VALUES ('7', 7);
SELECT typeof(a), typeof(b) FROM t;""", db='', hint='typeof(column) names the storage class of each value.', why="The text '7' becomes integer 7 in a, and the number 7 becomes text '7' in b.")}
''', kw=['type affinity', 'STRICT', 'typeof', 'storage class', 'NUMERIC affinity', 'dynamic typing'])
K.talk('affinity', '''Most engines refuse text in an integer column, but SQLite is more relaxed. A column type gives it an affinity, which is a preference, and SQLite
converts values to that preference when it can. The text forty two becomes the number forty two in an integer column, but the word hello stays text
because it cannot become a number. The affinity comes from the type name, anything containing INT is integer, anything with CHAR or TEXT is text,
and so on. Since version three point thirty seven, a STRICT table refuses values that do not fit, the way PostgreSQL and MySQL do. Use typeof to see
what was really stored. Think of a sorting tray that gently moves each coin to the right slot, and a strict tray that rejects foreign coins.''')

K.lesson('alter', 'ALTER TABLE and DROP TABLE', f'''
<p>Designs change. <code>ALTER TABLE</code> changes a table that already holds data, and <code>DROP TABLE</code> removes a table and every row in it.</p>
{fxs(fx('Add a column', '<code>ALTER TABLE t ADD COLUMN c type DEFAULT v;</code>', 'Existing rows get the default, or NULL when there is none.', key=True),
     fx('Rename', '<code>ALTER TABLE t RENAME TO t2;</code> and <code>ALTER TABLE t RENAME COLUMN a TO b;</code>', 'Names change, data stays.'),
     fx('Drop a column', '<code>ALTER TABLE t DROP COLUMN c;</code>', 'SQLite 3.35 and later. It refuses a column used by an index, a key or a CHECK.'),
     fx('Remove a table', '<code>DROP TABLE IF EXISTS t;</code>', 'Gone with all its rows. There is no undo outside a transaction.'))}
{K.sql('alter', """ALTER TABLE products ADD COLUMN rating INTEGER DEFAULT 3;
ALTER TABLE products RENAME COLUMN stock TO in_stock;
SELECT name, in_stock, rating FROM products LIMIT 3;""", title='Grow a table that already has data', notes={1: 'All ten existing products get rating 3 at once.', 2: 'The column is renamed, its values stay.'})}
{K.sql('drop', """CREATE TABLE scratch (x INTEGER);
DROP TABLE scratch;
DROP TABLE IF EXISTS scratch;
SELECT count(*) AS tables_named_scratch FROM sqlite_schema WHERE name = 'scratch';""", db='', title='DROP, and the safe IF EXISTS form', notes={3: 'The table is already gone. IF EXISTS turns the error into a quiet no operation.', 4: 'sqlite_schema is SQLite’s own list of tables.'})}
{table(['Engine', 'Where to see the tables'], [
    ['SQLite', 'SELECT name FROM sqlite_schema WHERE type = \'table\''],
    ['PostgreSQL, MySQL, SQL Server', 'SELECT table_name FROM information_schema.tables'],
    ['Oracle', 'SELECT table_name FROM user_tables']])}
{scene('a migration on a live app', '<p>A food delivery app wants to show a rating for each restaurant. The team writes a <b>migration</b>: a small script with <code>ALTER TABLE restaurants ADD COLUMN rating REAL</code>. Tools such as Flyway, Liquibase, Alembic or Rails migrations number these scripts and record which ones ran, so every copy of the database, on every laptop and server, ends up with the same shape.</p>')}
{K.lab('l-alter', 'm', 'Rate the sports products', 'Add a column <code>rating INTEGER DEFAULT 4</code> to <code>products</code>, then show <code>name</code> and <code>rating</code> of the Sports products.',
"""ALTER TABLE products ADD COLUMN rating INTEGER DEFAULT 4;
SELECT name, rating FROM products WHERE category = 'Sports';""", hint='ALTER TABLE ... ADD COLUMN ... DEFAULT 4, then a SELECT with WHERE.', why='Existing rows take the default value 4.')}
''', kw=['ALTER TABLE', 'ADD COLUMN', 'RENAME COLUMN', 'DROP COLUMN', 'DROP TABLE', 'migration', 'information_schema', 'sqlite_schema'])
K.talk('alter', '''Designs change as an app grows. ALTER TABLE changes a table that already holds data. You can add a column, and every existing row gets its default
value or NULL. You can rename a table or a column, and the data stays. Newer SQLite versions can drop a column too. DROP TABLE removes a table and
every row in it, with no undo, so write IF EXISTS in scripts that might run twice. Real teams keep these changes in numbered migration scripts, so
every laptop and every server ends up with the same table shapes. Think of adding a new column to a printed register by ruling one more line down
every page.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>CREATE TABLE draws a blank form with labelled boxes, and constraints are the rules printed on the form, such as "this box must not be empty".</p>',
    '<p>A schema is the set of table definitions. Types and constraints together keep the data valid. DDL (data definition language) is the part of SQL that creates and changes structure: CREATE, ALTER, DROP.</p>',
    '<p>Constraints are declarative integrity rules: domain constraints (types, CHECK), entity integrity (primary keys) and referential integrity (foreign keys). The engine enforces them, which is stronger than checking in every application.</p>',
    '<p>Schema change on huge live tables is a research and engineering topic of its own. Some ALTERs rewrite every row. Tools such as gh-ost and pt-online-schema-change for MySQL copy the table in the background and swap it in, and PostgreSQL can add a column with a constant default without rewriting the table (since version 11).</p>')}
{deep('Why SQLite chose flexible typing', '<p>SQLite’s author describes flexible typing as a feature: a value has a type, and a column only prefers one. This matches scripting languages and lets old files keep working. STRICT tables were added later for people who want rigid columns. Both are documented on sqlite.org under datatype3 and stricttables.</p>')}
''', kw=['schema', 'DDL', 'domain constraint', 'entity integrity', 'online schema change', 'flexible typing'])
K.talk('levels', '''Time to climb the ladder. For a beginner, a table is a blank form and constraints are the rules printed on it. At college level, the set of table
definitions is the schema, and the statements that build it, CREATE, ALTER and DROP, are called data definition language. At masters level,
constraints are integrity rules enforced by the engine, which is safer than trusting every program to check. At research level, changing the shape
of a huge live table is hard, and special tools copy the table quietly in the background and swap it in. Think of renovating a busy railway station
while trains keep running.''')

K.quiz('e', 'Which statement makes a new table?', ['NEW TABLE', 'CREATE TABLE', 'MAKE TABLE', 'ADD TABLE'], 1, 'Create.', 'CREATE TABLE defines a table.')
K.quiz('e', 'NOT NULL means', ['The value must be zero', 'A value must be present', 'The value is unique', 'The column is hidden'], 1, 'Present.', 'NULL is not allowed.')
K.quiz('e', 'Which constraint stops two members sharing an email?', ['CHECK', 'DEFAULT', 'UNIQUE', 'NOT NULL'], 2, 'No repeats.', 'UNIQUE forbids duplicate values.')
K.quiz('e', 'What happens to a column left out of an INSERT when it has a DEFAULT?', ['Error', 'It gets the default', 'It gets 0', 'The row is skipped'], 1, 'Fill in.', 'The default value is used.')
K.quiz('m', 'A CHECK (age >= 18) meets age NULL. The row is', ['Refused', 'Accepted', 'Changed to 18', 'Deleted'], 1, 'Unknown is not false.', 'CHECK fails only on false.')
K.quiz('m', 'Best type for money in PostgreSQL', ['real', 'double precision', 'numeric(10,2)', 'text'], 2, 'Exact.', 'numeric is exact decimal arithmetic.')
K.quiz('m', 'In SQLite, a column declared VARCHAR(30) has which affinity?', ['INTEGER', 'TEXT', 'REAL', 'BLOB'], 1, 'Contains CHAR.', 'Any type name containing CHAR gets TEXT affinity.')
K.quiz('m', 'In SQLite, inserting \'hello\' into a plain INTEGER column', ['Fails', 'Stores the text hello', 'Stores 0', 'Stores NULL'], 1, 'Affinity, not a rule.', 'It cannot convert, so it stores the text.')
K.quiz('m', 'What does ADD COLUMN give existing rows?', ['Nothing, they are deleted', 'The default, or NULL', 'An error', 'Random values'], 1, 'Default.', 'Existing rows take the default value.')
K.quiz('h', 'Which types does a STRICT table allow?', ['Any name at all', 'INT, INTEGER, REAL, TEXT, BLOB, ANY', 'Only TEXT', 'VARCHAR and DECIMAL'], 1, 'Six names.', 'Those six are the only ones allowed.')
K.quiz('x', 'In SQLite, DECIMAL(10,2) gets which affinity?', ['TEXT', 'REAL', 'NUMERIC', 'INTEGER'], 2, 'Anything else.', 'It matches none of the earlier rules, so it is NUMERIC.')

K.calc('e', 'Two books are inserted into a new table with id INTEGER PRIMARY KEY and no id given. What id does the second book get?', '2', 'Counts from 1.',
       ['An empty table starts at 1.', 'The next row gets the largest id plus one.', eq('2')], check=value('', 'SELECT max(id) FROM books', setup="CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT); INSERT INTO books (title) VALUES ('a'), ('b');"))
K.calc('e', 'How many columns does CREATE TABLE books (id, title, author, pages, price) define?', '5', 'Count the names.',
       ['Each column is a name followed by its type.', 'The names are id, title, author, pages and price.', eq('5 columns')], check=value('', "SELECT count(*) FROM pragma_table_info('books')", setup='CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author TEXT, pages INTEGER, price REAL);'))
K.calc('m', 'Three members are inserted with ages 30, 15 and NULL into a table with CHECK (age >= 18), one INSERT each. How many are stored?', '2', '15 fails, NULL passes.',
       ['30 >= 18 is true: stored.', '15 >= 18 is false: refused.', 'NULL >= 18 is unknown: stored.', eq('2 rows')], check=2)
K.calc('m', 'A price of 1499 rupees is stored as whole paise. What integer is stored?', '149900', '100 paise in a rupee.',
       ['One rupee is 100 paise.', 'Multiply the rupees by 100.', eq('1499 × 100 = 149900')], check=1499 * 100)
K.calc('m', 'After ALTER TABLE products ADD COLUMN rating INTEGER DEFAULT 3, what is the sum of rating over all products?', str(value('shop', 'SELECT sum(rating) FROM products', setup='ALTER TABLE products ADD COLUMN rating INTEGER DEFAULT 3;')), 'Every row gets 3.',
       ['There are 10 products.', 'ADD COLUMN gives every existing row the default 3.', eq('10 × 3 = 30')], check=value('shop', 'SELECT sum(rating) FROM products', setup='ALTER TABLE products ADD COLUMN rating INTEGER DEFAULT 3;'))
K.calc('m', 'A UNIQUE email column holds asha@mail.in, NULL, NULL and ravi@mail.in. How many rows can it hold without error?', '4', 'NULLs do not clash.',
       ['The two real emails differ.', 'In SQLite, PostgreSQL and MySQL two NULLs do not break UNIQUE.', eq('4 rows')], check=value('', 'SELECT count(*) FROM u', setup="CREATE TABLE u (e TEXT UNIQUE); INSERT INTO u VALUES ('asha@mail.in'), (NULL), (NULL), ('ravi@mail.in');"))
K.calc('h', 'How many of the declared types INT, VARCHAR(9), DOUBLE, DATE, BLOB get NUMERIC affinity in SQLite?', '1', 'Only the one that matches no rule.',
       ['INT: INTEGER. VARCHAR: TEXT. DOUBLE: REAL. BLOB: BLOB.', 'DATE matches none, so NUMERIC.', eq('1')], check=1)
K.calc('h', 'In a plain table with a TEXT column t, you insert the number 7 and then compute length(t). What is the length?', '1', 'Stored as the text 7.',
       ['The column has TEXT affinity.', 'So the number 7 is stored as the text 7, one character.', eq('length = 1')], check=value('', 'SELECT length(t) FROM x', setup='CREATE TABLE x (t TEXT); INSERT INTO x VALUES (7);'))

K.must('CREATE TABLE', 'Names the table, its columns, their types and the rules. IF NOT EXISTS makes it safe to run twice.')
K.must('Constraints', 'NOT NULL, UNIQUE, PRIMARY KEY, CHECK, DEFAULT and REFERENCES are checked by the engine on every write.')
K.must('CHECK and NULL', 'CHECK refuses a row only when its test is false. NULL makes it unknown, which passes.')
K.must('Types', 'Use exact types for money. SQLite uses affinity, a preference, unless the table is STRICT.')
K.must('ALTER and DROP', 'ADD COLUMN, RENAME and DROP COLUMN change a live table. DROP TABLE deletes the table and its rows.')

T = K.topic(
    slug='sql-create', topic='sql-create', step=(4, 'Building and changing data', 'sql-make', 'Create your own tables with types and rules, change rows safely, and name steps with views and CTEs.', 'Intermediate'),
    title='Building tables: CREATE, types and constraints', short='Building tables', badge='4.1', minutes=40, added='2026-11-23',
    lead='Design your own tables with CREATE TABLE, choose the right data types, protect the data with constraints, and change tables later with ALTER and DROP.',
    desc='CREATE TABLE, data types across SQLite, PostgreSQL, MySQL and SQL Server, money types, NOT NULL, UNIQUE, CHECK, DEFAULT, type affinity, STRICT tables, ALTER TABLE, DROP TABLE, migrations.',
    summary='CREATE TABLE, types, constraints, SQLite affinity and STRICT, ALTER and DROP.',
    keywords=['CREATE TABLE', 'data types', 'constraints', 'CHECK', 'STRICT', 'ALTER TABLE', 'DROP TABLE'],
    recap='<p>CREATE TABLE draws the form, constraints are its rules, affinity or STRICT decides how types are kept, and ALTER or DROP change it later.</p>')
