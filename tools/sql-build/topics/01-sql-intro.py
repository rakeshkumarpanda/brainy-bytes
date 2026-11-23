# Chapter 1.1: data, databases, the relational model, what SQL is, database engines and how a query travels.
# Sources: E. F. Codd, "A Relational Model of Data for Large Shared Data Banks", CACM 13(6), June 1970.
# D. Chamberlin and R. Boyce, "SEQUEL: A Structured English Query Language", 1974. ISO/IEC 9075 (SQL:2023).
# sqlite.org (most widely deployed database engine, serverless, in every phone), see tools/sql-build/SOURCES.md.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('data', 'Data is everywhere, and it needs a home', f'''
<p>Every time you order food on an app, top up a phone, or get your marks on a school portal, a computer somewhere writes down a few small facts. Who ordered. What they ordered. When. How much it cost. Those small facts are called <b>data</b>.</p>
<p>A notebook works for ten facts. A spreadsheet works for a few thousand. But a train booking site has millions of seats, thousands of people booking at the same second, and no room for mistakes such as selling one seat twice. For that we need a <b>database</b>: an organised store of data, looked after by a program called a <b>database management system</b> (DBMS).</p>
{table(['What you need', 'Notebook or spreadsheet', 'Database'], [
    ['Many people changing data at the same time', 'Copies clash, last save wins', 'Built in, each change is safe'],
    ['Rules such as "price must be above zero"', 'Easy to break by accident', 'The database refuses bad data'],
    ['Millions of rows', 'Slow or crashes', 'Indexes find one row in a blink'],
    ['A power cut in the middle of a change', 'File may be half written', 'Changes are all or nothing'],
    ['Asking questions of the data', 'Formulas and filters by hand', 'One SQL query']])}
{pk('sqanatomy')}
{note('A database is not one file or one table. It is the whole collection of tables plus the rules that tie them together, kept by a DBMS.', 'tip')}
''', kw=['data', 'database', 'DBMS', 'spreadsheet vs database', 'table', 'row', 'column'])
K.talk('data', '''Look around you and you will find data almost everywhere. A food order, a bus ticket, a hospital visit and a school mark all
become a few small facts saved by a computer. A notebook is fine for ten facts, and a spreadsheet is fine for a few thousand. But a train
booking site handles millions of seats while thousands of people press Book at the same second, and it must never sell one seat twice.
That is the job of a database, looked after by a program called a database management system. It keeps the data safe, checks the rules,
and answers questions quickly. Think of a database as a very careful librarian who never loses a page.''')

K.lesson('relational', 'Tables, rows, columns and keys', f'''
<p>In 1970 Edgar F. Codd, a researcher at IBM, published a paper called <i>A Relational Model of Data for Large Shared Data Banks</i>. His idea was simple and powerful: keep all data in <b>tables</b>, and let people ask questions about what they want, without caring how the computer stores it on disk. Almost every business database today follows his idea.</p>
{table(['Everyday word', 'Database word', "Codd’s maths word", 'Example in the shop'], [
    ['Table', 'table', 'relation', 'customers'],
    ['Line or record', 'row', 'tuple', 'Asha from Pune'],
    ['Heading', 'column', 'attribute', 'city'],
    ['Allowed values', 'data type', 'domain', 'whole numbers for stock'],
    ['Name tag', 'primary key', 'key', 'id 1 means Asha and nobody else']])}
<p>Here is the real <code>customers</code> table of the Bytes Bazaar shop that this subject uses. It was printed by SQLite when this page was built.</p>
{grid('shop', 'SELECT * FROM customers', 'customers (Bytes Bazaar)')}
{steps('Read the table like a database does', [
    'The table has a name, customers. Names let SQL find it.',
    'There are 5 columns: id, name, city, email and joined.',
    'Each row is one customer. Row order has no meaning in the relational model, so SQL never promises an order unless you ask for one.',
    'id is the primary key. It is unique and never empty, so it picks out exactly one row.',
    eq('Kabir has no email. The cell holds NULL, which means unknown or missing')])}
{note('A primary key must be unique and must never be missing. Names are bad keys because two customers can both be called Asha.', 'warn')}
''', kw=['relational model', 'Codd', '1970', 'relation', 'tuple', 'attribute', 'primary key', 'NULL'])
K.talk('relational', '''In 1970 a researcher at IBM called Edgar Codd wrote a paper that changed computing. He said that all data can live in simple
tables, and that people should ask for what they want without worrying how the computer stores it. A table has a name, columns
across the top, and rows going down. Each row is one thing, such as one customer. Each column is one kind of fact, such as the city.
One special column, the primary key, gives every row its own number so it can never be mixed up with another row. A missing
value is written as NULL. Think of a table as a class register where every child has a roll number nobody else shares.''')

K.lesson('sql-lang', 'What SQL is and your first query', f'''
<p><b>SQL</b> stands for Structured Query Language. People say it as the letters S Q L or as the word "sequel". It began at IBM in 1974, when Donald Chamberlin and Raymond Boyce described a language called SEQUEL for asking questions of Codd style tables. The name was later shortened to SQL. It became an ANSI standard in 1986 and an ISO standard in 1987, and the standard is still updated: the current edition is SQL:2023 (ISO/IEC 9075).</p>
<p>SQL is <b>declarative</b>. You describe the answer you want, and the database works out the steps. Compare asking a waiter for "one masala dosa" with walking into the kitchen and giving the cook a recipe.</p>
{K.sql('first', """SELECT name, city
FROM customers;""", title='Your first query: names and cities of all customers', notes={1: 'SELECT lists the columns you want back, separated by commas.', 2: 'FROM names the table to read. The semicolon ends the statement.'})}
{table(['Family', 'Stands for', 'Commands', 'Used to'], [
    ['DQL', 'Data Query Language', '<code>SELECT</code>', 'ask questions and read data'],
    ['DML', 'Data Manipulation Language', '<code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code>', 'add, change and remove rows'],
    ['DDL', 'Data Definition Language', '<code>CREATE</code>, <code>ALTER</code>, <code>DROP</code>', 'build and change tables'],
    ['DCL', 'Data Control Language', '<code>GRANT</code>, <code>REVOKE</code>', 'give and take away permissions'],
    ['TCL', 'Transaction Control Language', '<code>BEGIN</code>, <code>COMMIT</code>, <code>ROLLBACK</code>', 'group changes so they happen all or nothing']])}
{fxs(
    fx('The smallest query', '<code>SELECT column, column FROM table;</code>', 'SELECT says which columns, FROM says which table. Keywords are not case sensitive, so select works too, but capitals make queries easier to read.', key=True),
    fx('Every column', '<code>SELECT * FROM table;</code>', 'The star means all columns. Handy for a quick look, but real programs should name the columns they need.'))}
{K.lab('l-products', 'e', 'Look at every product', 'Show <b>every column</b> of the <code>products</code> table.', 'SELECT * FROM products;', hint='The star means every column.', why='SELECT * returns every column, and with no WHERE clause every row comes back too.')}
{K.lab('l-names', 'e', 'Just the names and prices', 'Show only the <code>name</code> and <code>price</code> of every product, in that column order.', 'SELECT name, price FROM products;', hint='List two columns after SELECT with a comma between them.', why='The result has the columns in the order you list them after SELECT.')}
''', kw=['SQL', 'SEQUEL', 'Chamberlin', 'Boyce', 'declarative', 'SELECT', 'FROM', 'DDL', 'DML', 'DCL', 'TCL', 'SQL:2023'])
K.talk('sql-lang', '''SQL means Structured Query Language, and it was born at IBM in 1974 when Donald Chamberlin and Raymond Boyce designed a language
called SEQUEL to talk to tables. The name was later shortened to SQL. It became an American standard in 1986 and a world ISO standard in 1987,
and the latest edition is SQL 2023. The most important thing about SQL is that it is declarative. You say what you want, not how to
get it. Your first query uses two words: SELECT lists the columns, and FROM names the table. Press Run on the block and the real
SQLite answers you. Think of SQL as ordering at a restaurant: you name the dish, and the kitchen decides how to cook it.''')

K.lesson('engines', 'Database engines and the journey of a query', f'''
<p>SQL is the language. A <b>database engine</b> is the program that understands it. Each engine follows the SQL standard closely but adds its own extras, called a <b>dialect</b>.</p>
{table(['Engine', 'Kind', 'Where you meet it'], [
    ['SQLite', 'Embedded, a library inside the app, no server', 'Every Android and iPhone, browsers, and this page'],
    ['PostgreSQL', 'Client and server, open source', 'Web apps, maps, banking and analytics'],
    ['MySQL and MariaDB', 'Client and server, open source', 'Many websites and online shops'],
    ['Microsoft SQL Server', 'Client and server, commercial', 'Company systems on Windows and Azure'],
    ['Oracle Database', 'Client and server, commercial', 'Large banks, telecom and governments']])}
<p>The SQL on these pages runs on <b>SQLite</b>, compiled to WebAssembly so it works inside your browser (the sql.js project). It is the real SQLite, so every answer you see is the true answer, not a guess. The SQLite team describes it as the most widely deployed database engine in the world.</p>
{pk('sqtrip')}
{steps('What happens after you press Run', [
    'The <b>parser</b> checks the grammar and that every table and column exists. A spelling mistake stops here with a syntax error.',
    'The <b>planner</b>, also called the optimizer, chooses a plan: read the whole table, or jump in using an index.',
    'The <b>executor</b> follows the plan and reads the rows.',
    eq('The result goes back to you as a new table, even if it has one row or none')])}
{scene('two people book the last seat', '<p>Two friends in different cities press Book on the last train seat at the same moment. A client and server engine such as PostgreSQL receives both requests. It lets the first booking finish, then the second one sees the seat is gone and gets a friendly "sold out". Without the database keeping order, both might get a ticket for one seat.</p>')}
{K.lab('l-orders', 'e', 'The order list', 'Show the <code>id</code>, <code>order_date</code> and <code>status</code> of every order.', 'SELECT id, order_date, status FROM orders;', hint='Three column names after SELECT, the table orders after FROM.', why='Naming columns makes the result smaller and clearer than SELECT *.')}
''', kw=['SQLite', 'PostgreSQL', 'MySQL', 'SQL Server', 'Oracle', 'dialect', 'parser', 'planner', 'optimizer', 'executor', 'WebAssembly', 'sql.js'])
K.talk('engines', '''SQL is a language, and a database engine is the program that speaks it. SQLite is a small library that lives inside an app,
with no separate server, which is why it sits in every smartphone and in this very page. PostgreSQL, MySQL, SQL Server and Oracle
are servers. Many apps connect to one server over the network. Each engine adds small extras to standard SQL, which we call a dialect.
When you press Run, your query passes three helpers. The parser checks the grammar. The planner picks the fastest way to find the rows.
The executor does the work and hands back a result table. Think of a parcel going from the counter to sorting to delivery.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A database is a big, careful cupboard of tables. SQL is the polite way to ask the cupboard keeper for exactly what you need.</p>',
    '<p>A DBMS gives you a data model (tables), a language (SQL), integrity rules (keys and constraints), safe sharing (transactions) and fast access (indexes). The relational model treats a table as a set of rows, which is why row order is not part of the data.</p>',
    "<p>Codd’s model rests on relational algebra: selection (WHERE), projection (the SELECT list), join, union, difference and rename. SQL is close to it but not identical. SQL tables can hold duplicate rows (a multiset or bag) and use NULL with three valued logic, two points Codd himself debated.</p>",
    '<p>Research engines explore learned query optimizers, column stores for analytics, and distributed SQL that keeps one logical database across many machines. The core idea of saying what you want and letting the system choose how is still the centre of all of them.</p>')}
{deep('Why SQL is called declarative', '<p>In a language such as Python you write a loop: open the file, read each line, check the city, keep matching lines. In SQL you write one sentence, and the planner may pick a different method each day as the data grows, for example an index instead of a full scan, without you changing the query.</p>')}
''', kw=['relational algebra', 'selection', 'projection', 'multiset', 'declarative', 'optimizer'])
K.talk('levels', '''This lesson shows the same idea at four depths. At school level, a database is a careful cupboard and SQL is the polite way to ask for
things. At college level, a database system gives you tables, a language, rules, safe sharing and speed. At masters level, SQL rests on
relational algebra, with selection, projection and joins, though SQL allows duplicate rows and uses NULL, which pure theory does not.
At research level, people build optimizers that learn, column stores for analytics and databases spread over many machines. Think of
it as one tree seen from the ground, from a window, from a hill and from a plane.''')

nc = value('shop', 'SELECT count(*) FROM customers')
np_ = value('shop', 'SELECT count(*) FROM products')
K.quiz('e', 'What is one row of a table?', ['One kind of fact for every record', 'One record, everything about one thing', 'The name of the table', 'A rule on the data'], 1, 'Left to right.', 'A row is one record, for example one customer.')
K.quiz('e', 'Which keyword names the table a query reads from?', ['SELECT', 'WHERE', 'FROM', 'TABLE'], 2, 'Read from.', 'FROM names the table.')
K.quiz('e', 'What does SELECT * mean?', ['Select the first row', 'Select every column', 'Select nothing', 'Select a random row'], 1, 'The star.', 'The star means every column of the table.')
K.quiz('e', 'Who proposed the relational model in 1970?', ['Edgar F. Codd', 'Alan Turing', 'Tim Berners-Lee', 'Linus Torvalds'], 0, 'An IBM researcher.', 'Codd published the relational model in 1970.')
K.quiz('m', 'SQL is called declarative because', ['It declares variables', 'You say what you want, the engine decides how', 'It only reads data', 'It is written in capitals'], 1, 'What, not how.', 'The planner chooses the steps.')
K.quiz('m', 'Which family do CREATE and DROP belong to?', ['DML', 'DQL', 'DDL', 'TCL'], 2, 'Definition.', 'Data Definition Language builds and removes structures.')
K.quiz('m', 'What does NULL in a cell mean?', ['Zero', 'An empty word', 'The value is missing or unknown', 'An error'], 2, 'Not zero.', 'NULL marks a missing or unknown value.')
K.quiz('m', 'Which engine runs inside the app with no separate server?', ['PostgreSQL', 'SQLite', 'SQL Server', 'Oracle'], 1, 'Embedded.', 'SQLite is a library linked into the app.')
K.quiz('h', 'Why is a name a poor primary key?', ['Names are too long', 'Two people can share a name', 'Names cannot be stored', 'Keys must be numbers'], 1, 'Unique.', 'A key must be unique, names repeat.')
K.quiz('h', 'Which part of the engine chooses between a full scan and an index?', ['Parser', 'Planner (optimizer)', 'Executor', 'Client'], 1, 'Plans.', 'The planner picks the plan, the executor runs it.')
K.quiz('x', 'In what way do SQL tables differ from relations in pure relational theory?', ['SQL tables cannot have keys', 'SQL tables may hold duplicate rows and NULLs', 'SQL tables must be sorted', 'There is no difference'], 1, 'Bags and NULL.', 'A relation is a set with no duplicates and no NULL, SQL allows both.')

K.calc('e', 'How many rows does the customers table of the shop have? Run SELECT * FROM customers in the playground and count.', str(nc), 'One row per customer.',
       ['Open the playground or look at the table in lesson 2.', 'Count the rows from id 1 down.', eq(f'{nc} rows')], check=nc)
K.calc('e', 'How many columns does the customers table have?', '5', 'Count the headings.',
       ['The headings are id, name, city, email and joined.', 'Count them.', eq('5 columns')], check=len(['id', 'name', 'city', 'email', 'joined']))
K.calc('e', 'How many cells does the customers table hold in total?', str(nc * 5), 'Rows times columns.',
       [f'There are {nc} rows.', 'There are 5 columns.', eq(f'{nc} × 5 = {nc * 5} cells')], check=nc * 5)
K.calc('m', 'How many customers have a NULL email?', str(value('shop', 'SELECT count(*) FROM customers WHERE email IS NULL')), 'Look for NULL in the email column.',
       ['Read the email column top to bottom.', 'Kabir and Vikram have no email.', eq('2 customers')], check=value('shop', 'SELECT count(*) FROM customers WHERE email IS NULL'))
K.calc('m', 'How many rows does SELECT name, price FROM products return?', str(np_), 'No WHERE means every row.',
       ['SELECT with no WHERE keeps every row.', f'products has {np_} rows.', eq(f'{np_} rows, each with 2 columns')], check=np_)
K.calc('m', 'SQL became an ANSI standard in 1986. How many years after Codd\'s 1970 paper was that?', '16', 'Subtract.',
       ['Codd published in 1970.', 'ANSI standardised SQL in 1986.', eq('1986 − 1970 = 16 years')], check=1986 - 1970)
K.calc('h', 'A query returns 3 columns and 10 rows. How many values does it send back?', '30', 'Each row has every column.',
       ['Each row holds 3 values.', 'There are 10 rows.', eq('3 × 10 = 30 values')], check=30)
K.calc('h', 'The orders table has 10 rows. You run SELECT id, status FROM orders. How many cells are in the result?', str(2 * value('shop', 'SELECT count(*) FROM orders')), 'Two columns.',
       ['No WHERE, so every order comes back.', 'Each row has 2 columns.', eq(f'{value("shop", "SELECT count(*) FROM orders")} × 2 = {2 * value("shop", "SELECT count(*) FROM orders")} cells')], check=2 * value('shop', 'SELECT count(*) FROM orders'))

K.must('Database and DBMS', 'A database is an organised collection of data. A DBMS is the program that stores it, checks rules, shares it safely and answers queries.')
K.must('Tables', 'Data lives in tables of rows (records) and columns (kinds of fact). A primary key is unique and never missing, so it names one row.')
K.must('NULL', 'NULL means missing or unknown. It is not zero and not an empty string.')
K.must('SQL', 'Structured Query Language, from IBM SEQUEL (1974), ANSI 1986, ISO 1987, current edition SQL:2023. Declarative: say what, not how.')
K.must('First query', 'SELECT columns FROM table. SELECT * means every column. Statements end with a semicolon.')
K.must('Engines', 'SQLite is embedded. PostgreSQL, MySQL, SQL Server and Oracle are servers. Each has its own dialect of SQL.')

T = K.topic(
    slug='sql-intro', topic='sql-intro', step=(1, 'Start here', 'sql-start', 'What a database is, tables and keys, what SQL is, and your first queries, filters and sorting.', 'Beginner'),
    title='Databases and SQL: where data lives', short='What SQL is', badge='1.1', minutes=35, added='2026-11-23',
    lead='Learn why apps keep data in databases, read a real table cell by cell, run your first SQL query in the browser, and follow a query through the parser, planner and executor.',
    desc='Data and databases, the relational model of Codd, tables, rows, columns, primary keys and NULL, the history and families of SQL, database engines and the journey of a query.',
    summary='Data, databases and the DBMS, the relational model, tables, keys and NULL, what SQL is, engines and how a query runs.',
    keywords=['database', 'DBMS', 'relational model', 'table', 'primary key', 'SQL', 'SELECT', 'SQLite', 'PostgreSQL'],
    recap='<p>Data lives in tables of rows and columns, a primary key names each row, and SQL lets you ask for what you want while the engine decides how.</p>')
