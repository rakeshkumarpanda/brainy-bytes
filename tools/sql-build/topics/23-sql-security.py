# Chapter 8.2: database security: SQL injection and parameterized queries, users, roles, GRANT and REVOKE, least privilege,
# views as a security layer, row level security, masking personal data, password storage, encryption, backups and audits.
# Sources: OWASP SQL Injection Prevention Cheat Sheet (parameterized queries first, allow lists for identifiers),
# OWASP Password Storage Cheat Sheet (Argon2id, bcrypt), sqlite.org c3ref/bind_blob.html (bound parameters ?, ?NNN, :name),
# postgresql.org sql-grant.html, ddl-rowsecurity.html (CREATE POLICY, since 9.5), MySQL account management docs,
# learn.microsoft.com row-level-security.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

USERS = "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, pin TEXT, role TEXT); INSERT INTO users (name, pin, role) VALUES ('asha', '4821', 'admin'), ('ravi', '1937', 'staff'), ('meera', '5560', 'staff');"

K.lesson('injection', 'SQL injection: when input becomes code', f'''
<p>SQL injection has been one of the most common and damaging web security flaws for over twenty years. It happens when a program builds SQL by gluing user input into the text, so specially crafted input changes what the SQL means.</p>
{pk('sqinject')}
{K.sql('glued', USERS + """
SELECT name, role FROM users WHERE name = 'x' OR '1'='1' --' AND pin = '0000';""", db='', title='What the database receives after gluing the attack text', notes={2: "The typed quote closed the string. OR '1'='1' is always true, and -- turns the PIN check into a comment. Every user comes back."})}
{table(['Typed into the name box', 'Effect when glued into SQL'], [
    ["x' OR '1'='1' --", 'every row matches, the login check is skipped'],
    ["x' followed by a second statement such as DROP TABLE users", 'a second statement, on engines and drivers that allow several statements per call'],
    ["x' UNION SELECT pin, role FROM users --", 'other data is pulled into the page']])}
{note('This page shows attacks only so you can recognise and prevent them, on a throwaway table in your own browser. Testing systems you do not own or have no permission to test is illegal in most countries.', 'warn')}
''', kw=['SQL injection', 'injection attack', 'string concatenation', 'login bypass', 'OWASP', 'UNION injection'])
K.talk('injection', '''SQL injection is one of the oldest and most damaging security flaws on the web. It happens when a program builds SQL by gluing the user's typed text
into the query. If someone types a quote, they can close the string early and add their own SQL. The classic example types a quote, then OR one equals
one, then two dashes. The OR makes every row match, and the dashes turn the PIN check into a comment, so the login lets them in as anyone. In the animation,
type normal names and the attack text, and watch what the database really receives. We show this only so you can recognise and prevent it. Think of a form
where someone writes extra instructions in the name box.''')

K.lesson('params', 'The fix: parameterized queries', f'''
<p>The reliable fix is a <b>parameterized query</b> (also called a prepared statement with bound parameters). The SQL text has placeholders, and the values travel separately. The database parses the SQL first, so a value can never become code.</p>
{K.sql('param', USERS + """
SELECT name, role FROM users WHERE name = 'x'' OR ''1''=''1'' --' AND pin = '0000';""", db='', title='What a bound parameter amounts to: the whole input is one plain value', notes={2: "Every quote in the input is treated as part of the name. No user is called that, so 0 rows."})}
<pre class="sq-code"># Python (sqlite3)
cur.execute("SELECT name, role FROM users WHERE name = ? AND pin = ?", (name, pin))

// JavaScript (node-postgres)
await client.query("SELECT name, role FROM users WHERE name = $1 AND pin = $2", [name, pin]);

// Java (JDBC)
PreparedStatement ps = conn.prepareStatement("SELECT name, role FROM users WHERE name = ? AND pin = ?");
ps.setString(1, name); ps.setString(2, pin);</pre>
{table(['Defence', 'Notes'], [
    ['Parameterized queries', 'the main defence, use them for every value'],
    ['ORMs and query builders', 'parameterize for you, but raw SQL inside them still needs care'],
    ['Allow lists for names', 'table and column names cannot be parameters, so pick them from a fixed list in code'],
    ['Least privilege', 'the app account cannot DROP tables, so a mistake does less damage'],
    ['Escaping by hand', 'a last resort, easy to get wrong']])}
{steps('Sorting by a column the user picks, safely', [
    'The user picks "price" from a menu.',
    'The code checks it against a fixed list: name, price, stock.',
    'Only then is the column name written into the SQL text.',
    'Values, such as a search word, still go in as parameters.'])}
''', kw=['parameterized query', 'prepared statement', 'bind parameter', 'placeholder', 'allow list', 'ORM'])
K.talk('params', '''The reliable fix is a parameterized query, also called a prepared statement. You write the SQL with question marks or numbered placeholders where
the values go, and the values are sent separately. The database reads the SQL first and only then plugs in the values, so a value can never turn into code.
The attack text becomes a strange name that matches nobody. Every language has this, Python, JavaScript, Java and the rest. Table and column names cannot
be parameters, so choose them from a fixed list in your code. Think of a bank form with separate boxes, where writing in the amount box can never change
the account number.''')

K.lesson('access', 'Users, roles and GRANT', f'''
<p>Server databases have accounts. Each account gets only the rights it needs, the <b>principle of least privilege</b>. SQLite has no accounts: whoever can open the file can read it, so it relies on the operating system’s file permissions.</p>
<pre class="sq-code">-- PostgreSQL
CREATE ROLE reporting;
GRANT SELECT ON orders, customers TO reporting;
CREATE USER analyst WITH PASSWORD '...' IN ROLE reporting;
REVOKE SELECT ON customers FROM reporting;

-- MySQL
CREATE USER 'shop_app'@'%' IDENTIFIED BY '...';
GRANT SELECT, INSERT, UPDATE ON shop.* TO 'shop_app'@'%';</pre>
{table(['Account', 'Needs', 'Should not have'], [
    ['Web app', 'SELECT, INSERT, UPDATE on its tables', 'DROP, ALTER, access to other databases'],
    ['Reporting', 'SELECT on a few tables or views', 'any write'],
    ['Migrations tool', 'CREATE, ALTER, DROP', 'to be used by the running app'],
    ['Administrator', 'everything', 'to be used for daily work']])}
{K.sql('viewsec', """CREATE VIEW customers_public AS
SELECT id, name, city FROM customers;
SELECT * FROM customers_public LIMIT 4;""", title='A view that leaves out personal columns', notes={2: 'No email, no join date. In a server engine you GRANT SELECT on this view and not on the table.'})}
{K.lab('l-public', 'e', 'A safe view for the support team', 'Create a view <code>orders_public</code> with only <code>id</code>, <code>order_date</code> and <code>status</code> of orders. Then select the rows of the view whose status is pending.',
"""CREATE VIEW orders_public AS SELECT id, order_date, status FROM orders;
SELECT * FROM orders_public WHERE status = 'pending';""", hint='CREATE VIEW orders_public AS SELECT id, order_date, status FROM orders', why='The view hides customer_id, so the support team cannot link orders to people.')}
''', kw=['least privilege', 'GRANT', 'REVOKE', 'role', 'user account', 'permissions', 'security view'])
K.talk('access', '''Server databases have accounts, and each account should get only the rights it needs, which is called the principle of least privilege. GRANT gives
a right, such as SELECT on a table, and REVOKE takes it away. Roles group rights so you grant them once to many people. The web app can read and write its
own tables but never drop them, and the reporting account can only read. A view that leaves out personal columns, granted instead of the table, is a simple
privacy shield. SQLite has no accounts, so it relies on file permissions. Think of an office where each key card opens only the rooms that person needs.''')

K.lesson('rls', 'Row level security and personal data', f'''
<p>Sometimes users may see the same table but only their own rows: each customer sees only their orders. <b>Row level security</b> makes the database add that filter automatically.</p>
<pre class="sq-code">-- PostgreSQL (9.5+)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY own_orders ON orders
  USING (customer_id = current_setting('app.customer_id')::int);</pre>
{K.sql('rlsview', """CREATE TABLE session (customer_id INTEGER);
INSERT INTO session VALUES (1);
CREATE VIEW my_orders AS
SELECT id, order_date, status FROM orders
WHERE customer_id = (SELECT customer_id FROM session);
SELECT * FROM my_orders;""", title='The same idea with a view in SQLite', notes={2: 'The app records who is logged in.', 5: 'The view filters every query by that customer.'})}
{table(['Protect', 'How'], [
    ['Passwords', 'never store them. Store a slow salted hash (Argon2id or bcrypt) computed in the app'],
    ['Personal data on screens', 'mask it: a***@mail.in, last 4 digits of a card'],
    ['Data on disk', 'encryption at rest: TDE in SQL Server and Oracle, disk encryption, SQLCipher for SQLite'],
    ['Data on the network', 'TLS between app and database'],
    ['Mistakes and attacks', 'backups you have tested restoring, and audit logs of who changed what']])}
{K.sql('mask', """SELECT name,
       substr(email, 1, 1) || '***' || substr(email, instr(email, '@')) AS masked
FROM customers WHERE email IS NOT NULL LIMIT 4;""", title='Masking emails for display', notes={2: 'First letter, three stars, then everything from the @.'})}
{K.lab('l-mask', 'm', 'Mask the emails', 'Show each customer <code>name</code> and <code>masked</code>, the email with only its first letter kept, then <code>***</code>, then the part from <code>@</code>. Leave out customers without an email.',
"""SELECT name, substr(email, 1, 1) || '***' || substr(email, instr(email, '@')) AS masked FROM customers WHERE email IS NOT NULL;""", hint="substr(email, 1, 1) || '***' || substr(email, instr(email, '@'))", why='instr finds the @, and substr from there keeps the domain.')}
{K.lab('l-rls', 'h', 'Only my orders', 'A table <code>session (customer_id)</code> holds 2. Create a view <code>my_orders</code> that shows <code>id</code> and <code>status</code> of the logged in customer’s orders, then select from it.',
"""CREATE VIEW my_orders AS SELECT id, status FROM orders WHERE customer_id = (SELECT customer_id FROM session);
SELECT * FROM my_orders;""", setup='CREATE TABLE session (customer_id INTEGER); INSERT INTO session VALUES (2);', hint='WHERE customer_id = (SELECT customer_id FROM session)', why='Customer 2 is Ravi, with orders 102 and 107.')}
''', kw=['row level security', 'CREATE POLICY', 'data masking', 'password hashing', 'Argon2', 'bcrypt', 'encryption at rest', 'TLS', 'backup', 'PII'])
K.talk('rls', '''Sometimes many users share one table but each may see only their own rows, like customers and their orders. Row level security makes the database
add that filter to every query automatically. PostgreSQL does this with a policy, and in SQLite a view that reads the logged in customer from a session
table gives the same effect. Personal data needs more care. Never store passwords, store a slow salted hash made in the app. Mask emails and card numbers
on screens. Encrypt data on disk and on the network, keep backups you have actually restored, and log who changed what. Think of a hotel where every key
opens only its own room.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Never glue typed text into SQL. Give every account only the rights it needs. Protect personal data.</p>',
    '<p>Parameterized queries everywhere, allow lists for identifiers, roles with GRANT and REVOKE, views and row level security, hashing for passwords, TLS and backups.</p>',
    '<p>Defence in depth: assume one layer fails. Second order injection stores harmful text that is later glued into SQL by another part of the system. Audit logging, separation of duties and key management complete the picture.</p>',
    '<p>Research covers differential privacy (adding calibrated noise so aggregate queries reveal little about any one person), encrypted query processing such as CryptDB (2011), and automatic detection of injection with static analysis and taint tracking.</p>')}
{deep('Differential privacy in one paragraph', '<p>A query is differentially private when its answer barely changes whether or not any single person is in the data. Systems add random noise sized to the query, for example to a COUNT. The US Census Bureau used differential privacy for its 2020 census results.</p>')}
''', kw=['defence in depth', 'second order injection', 'differential privacy', 'encrypted database', 'taint tracking'])
K.talk('levels', '''Here is the ladder. For a beginner, never glue typed text into SQL, give accounts only what they need, and protect personal data. At college level, use
parameters everywhere, roles and grants, views and row level security, hashed passwords and backups. At masters level, plan defence in depth, and watch for
second order injection, where stored text is later glued into SQL. At research level, differential privacy adds careful noise so totals reveal little about
any one person. Think of a castle with a moat, walls and guards, so one broken defence is not the end.''')

K.quiz('e', 'SQL injection happens when', ['A query is slow', 'User input is glued into SQL text', 'An index is missing', 'A table is empty'], 1, 'Input becomes code.', 'Typed text changes the SQL.')
K.quiz('e', 'The main defence against SQL injection is', ['Longer passwords', 'Parameterized queries', 'More indexes', 'Views'], 1, 'Placeholders.', 'Values are sent separately from the SQL.')
K.quiz('e', 'Least privilege means', ['Everyone is admin', 'Each account gets only what it needs', 'No passwords', 'Read only databases'], 1, 'Minimum rights.', 'Limit the damage of mistakes and attacks.')
K.quiz('e', 'Passwords should be stored as', ['Plain text', 'A slow salted hash', 'An encrypted column anyone can decrypt', 'A view'], 1, 'Hash.', 'Argon2id or bcrypt.')
K.quiz('m', "In x' OR '1'='1' --, what does -- do?", ['Subtracts', 'Starts a comment, hiding the rest', 'Ends the database', 'Nothing'], 1, 'Comment.', 'The PIN check is commented out.')
K.quiz('m', 'Which can NOT be a bound parameter?', ['A name value', 'A number value', 'A table name', 'A date value'], 2, 'Identifiers.', 'Use an allow list for table and column names.')
K.quiz('m', 'GRANT SELECT ON orders TO reporting', ['Deletes orders', 'Lets reporting read orders', 'Creates a table', 'Revokes access'], 1, 'Give a right.', 'reporting may now SELECT from orders.')
K.quiz('m', 'Row level security', ['Hides columns', 'Filters rows per user automatically', 'Encrypts rows', 'Sorts rows'], 1, 'Per user rows.', 'A policy adds a WHERE for each user.')
K.quiz('m', 'How does SQLite control who can read a database?', ['GRANT', 'Roles', 'Operating system file permissions', 'Passwords in SQL'], 2, 'A file.', 'Anyone who can open the file can read it.')
K.quiz('h', 'Second order injection is', ['Injection twice in a row', 'Stored text later glued into SQL elsewhere', 'Injection in ORDER BY only', 'A typo'], 1, 'Delayed.', 'The harmful text is stored first and used later.')
K.quiz('x', 'Adding calibrated noise to aggregate answers to protect individuals is', ['Hashing', 'Differential privacy', 'Sharding', 'Masking'], 1, 'Noise.', 'Differential privacy.')

n_all = value('', "SELECT count(*) FROM users WHERE name = 'x' OR '1'='1'", setup=USERS)
K.calc('e', 'How many users does the glued attack query return from the 3 user table?', str(n_all), 'The OR is always true.',
       ["'1'='1' is true for every row.", 'So every row matches.', eq(f'{n_all} users')], check=n_all)
K.calc('e', 'And with a parameterized query using the same text as the name?', '0', 'Nobody has that name.',
       ['The whole text is one value.', 'No user is called that.', eq('0 users')], check=value('', "SELECT count(*) FROM users WHERE name = ? AND pin = ?".replace('?', "'x'' OR ''1''=''1'' --'", 1).replace('?', "'0000'"), setup=USERS))
K.calc('m', 'A 4 digit PIN has how many possible values?', '10000', '10 choices per digit.',
       ['Each digit is 0 to 9.', 'Four digits.', eq('10⁴ = 10,000')], check=10 ** 4)
K.calc('m', 'If a login allows 5 tries per hour, how many hours to try every 4 digit PIN?', '2000', 'Values ÷ tries per hour.',
       ['10,000 PINs.', '5 tries per hour.', eq('10,000 ÷ 5 = 2,000 hours')], check=2000)
mk = value('shop', "SELECT substr(email, 1, 1) || '***' || substr(email, instr(email, '@')) FROM customers WHERE id = 1")
K.calc('m', f'What does the masking expression give for asha@mail.in? Count its characters.', str(len(mk)), f'It gives {mk}.',
       ['First letter a, then ***.', 'Then @mail.in, 8 characters.', eq(f'1 + 3 + 8 = {len(mk)}')], check=len(mk))
mine = value('shop', 'SELECT count(*) FROM orders WHERE customer_id = 1')
K.calc('m', 'With session customer_id = 1, how many rows does my_orders show?', str(mine), 'Asha’s orders.',
       ['Asha placed orders 101, 103 and 110.', 'The view keeps only those.', eq(f'{mine} rows')], check=mine)
K.calc('h', 'A bcrypt hash with cost 12 does 2¹² rounds of work. How many rounds is that?', '4096', 'Powers of two.',
       ['Cost 12 means 2 to the power 12.', '2¹⁰ = 1024, times 4.', eq('2¹² = 4,096')], check=2 ** 12)
K.calc('h', 'Raising the bcrypt cost from 12 to 13 multiplies the work by what factor?', '2', 'One more power of two.',
       ['2¹³ ÷ 2¹².', 'Each step doubles the work.', eq('2')], check=2)

K.must('Injection', 'Gluing user text into SQL lets input become code. It bypasses logins and leaks data.')
K.must('Parameters', 'Use placeholders (?, $1, :name) for every value. Pick table and column names from an allow list.')
K.must('Least privilege', 'Accounts and roles get only the rights they need. GRANT gives, REVOKE takes away.')
K.must('Rows and columns', 'Views hide columns, row level security hides rows. SQLite relies on file permissions.')
K.must('Personal data', 'Hash passwords with Argon2id or bcrypt, mask on screen, encrypt at rest and in transit, test your backups.')

T = K.topic(
    slug='sql-security', topic='sql-security', step=(8, 'Professional SQL', 'sql-pro', 'Logic inside the database, security, scaling to many machines, and the differences between engines.', 'Advanced'),
    title='Database security', short='Security', badge='8.2', minutes=40, added='2026-11-23',
    lead='See how SQL injection works and stop it with parameterized queries, give accounts only the rights they need, and protect personal data with views, row level security, hashing and encryption.',
    desc='SQL injection and login bypass, parameterized queries in Python, JavaScript and Java, allow lists, least privilege, users, roles, GRANT and REVOKE, security views, row level security, masking, password hashing, encryption, backups, differential privacy.',
    summary='SQL injection, parameterized queries, least privilege, row level security and protecting personal data.',
    keywords=['SQL injection', 'parameterized query', 'GRANT', 'least privilege', 'row level security', 'password hashing'],
    recap='<p>Parameters stop injection, least privilege limits damage, views and policies hide what users should not see, and personal data is hashed, masked and encrypted.</p>')
