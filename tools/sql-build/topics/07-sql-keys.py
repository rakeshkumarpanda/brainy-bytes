# Chapter 3.1: keys and relationships: primary, candidate, natural and surrogate keys, composite keys, foreign keys,
# one to one, one to many and many to many with a junction table, ER diagrams and crow's foot notation.
# Sources: sqlite.org foreignkeys.html (off by default, PRAGMA foreign_keys, actions), lang_createtable.html
# (INTEGER PRIMARY KEY is the rowid alias), Codd 1970 (primary and foreign keys), Chen 1976 (entity relationship model).
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('why', 'Why one table is not enough', f'''
<p>Imagine writing every order in one big table: order id, date, customer name, customer city, customer email, product name, product price. Asha orders three times, so her email is typed three times. If she changes her email, someone must find and fix all three rows. Miss one and the database now holds two different emails for the same person.</p>
{table(['Problem', 'What goes wrong in one big table'], [
    ['Repeated data', 'Asha’s city and email are stored again in every order she makes'],
    ['Update problem', 'Change the email in one row but not the others, and the data disagrees with itself'],
    ['Insert problem', 'A new customer who has not ordered yet has nowhere to live'],
    ['Delete problem', 'Delete a customer’s only order and you lose the customer too']])}
<p>The fix is to give each kind of thing its own table, customers, products and orders, and link them with <b>keys</b>. Each fact is stored once. This idea is called <b>normalization</b>, and chapter 5.1 covers it formally.</p>
{pk('sqlink')}
{note('A relational database is a set of small, focused tables plus the keys that connect them. Joins put the pieces back together when you ask a question.', 'tip')}
''', kw=['redundancy', 'update anomaly', 'insert anomaly', 'delete anomaly', 'separate tables', 'link with keys'])
K.talk('why', '''Picture one giant table with every order, and the customer details typed again in each row. Asha orders three times, so her email
appears three times. If she changes it, someone must fix all three rows, and if one is missed, the database disagrees with itself. A
new customer with no orders has nowhere to live, and deleting someone's only order deletes the customer too. The cure is to give each
kind of thing its own table, customers, products and orders, and connect them with keys, so each fact lives in exactly one place. In
the animation, an order stores only a customer number, and following it leads to one customer. Think of a school register and a fee book that share roll numbers.''')

K.lesson('keys', 'Primary keys, natural and surrogate', f'''
<p>A <b>primary key</b> is the column, or set of columns, that picks out exactly one row. It must be <b>unique</b> and <b>never NULL</b>. A table has at most one primary key.</p>
{table(['Kind of key', 'Meaning', 'Example'], [
    ['Candidate key', 'any column set that could be the primary key', 'customers.id, also customers.email if every customer had one'],
    ['Primary key', 'the candidate chosen to identify rows', 'customers.id'],
    ['Natural key', 'a real world value', 'Aadhaar number, ISBN, vehicle number plate'],
    ['Surrogate key', 'a made up number with no outside meaning', 'id 1, 2, 3 assigned by the database'],
    ['Composite key', 'two or more columns together', 'order_items (order_id, product_id)'],
    ['Alternate key', 'a candidate key not chosen, usually given a UNIQUE rule', 'customers.email UNIQUE']])}
{K.sql('pk', """SELECT order_id, product_id, qty
FROM order_items
WHERE order_id = 101;""", title='A composite primary key', notes={1: 'Neither order_id nor product_id is unique alone. The pair is: one line per product in each order.'})}
{note('In SQLite, a column declared exactly INTEGER PRIMARY KEY becomes the rowid, the table’s hidden row number. Insert NULL into it and SQLite picks the next number for you. In PostgreSQL use GENERATED ALWAYS AS IDENTITY, in MySQL AUTO_INCREMENT, in SQL Server IDENTITY(1,1).', 'exam')}
{scene('why banks do not key on your name', '<p>A bank has thousands of customers called Rahul Sharma. Even phone numbers change and get reused. So the bank gives each customer a customer id that never changes, a surrogate key, and stores the PAN or phone number as ordinary columns with UNIQUE rules where needed.</p>')}
{K.lab('l-pk', 'e', 'One line of an order', 'Show the <code>qty</code> for the line of order 104 that is for product 2.', 'SELECT qty FROM order_items WHERE order_id = 104 AND product_id = 2;', hint='Both key columns are needed to pick one row.', why='The composite key (order_id, product_id) identifies exactly one line.')}
''', kw=['primary key', 'candidate key', 'natural key', 'surrogate key', 'composite key', 'alternate key', 'rowid', 'IDENTITY', 'AUTO_INCREMENT'])
K.talk('keys', '''A primary key is the column, or group of columns, that picks out exactly one row. It must be unique and must never be NULL, and a table
has only one. Any column that could do the job is a candidate key. A natural key comes from the real world, like an ISBN. A surrogate key is a
plain number the database makes up, like id one, two, three, and most designers prefer it because real world values change. A composite key uses
two columns together, like order id and product id in the order items table. In SQLite, a column declared exactly INTEGER PRIMARY KEY becomes the
hidden row number. Think of a roll number that stays the same even if a student changes their name.''')

K.lesson('fk', 'Foreign keys keep links honest', f'''
<p>A <b>foreign key</b> is a column whose value must match a primary key in another table, the <b>parent</b>. <code>orders.customer_id</code> must be an existing <code>customers.id</code>. The database checks this on every insert, update and delete, so you can never have an order for a customer who does not exist.</p>
{K.sql('fkfail', """-- Customer 99 does not exist
INSERT INTO orders (id, customer_id, order_date, status)
VALUES (200, 99, '2025-07-10', 'pending');""", title='The database refuses an orphan', err=True, notes={3: 'customer_id 99 has no parent row, so the FOREIGN KEY rule stops the insert.'})}
{K.sql('fkdel', """-- Asha (id 1) still has orders
DELETE FROM customers WHERE id = 1;""", title='You cannot delete a parent with children', err=True, notes={2: 'The default action is NO ACTION: the delete fails while orders still point at Asha.'})}
{table(['ON DELETE action', 'When the parent row is deleted'], [
    ['NO ACTION (default)', 'the delete fails if children exist (checked at the end of the statement)'],
    ['RESTRICT', 'the delete fails at once if children exist'],
    ['CASCADE', 'the children are deleted too'],
    ['SET NULL', 'the children’s foreign key becomes NULL'],
    ['SET DEFAULT', 'the children’s foreign key gets its default value']])}
{note('SQLite has foreign keys switched off by default for backwards compatibility. Each connection must run PRAGMA foreign_keys = ON. Every SQL block and the playground on these pages do that for you. PostgreSQL, SQL Server and MySQL (InnoDB) always enforce them.', 'warn')}
{K.lab('l-fk', 'm', 'Orders that point at real customers', 'Count the orders whose <code>customer_id</code> matches a customer living in Delhi. Return one column named <code>n</code>.', "SELECT COUNT(*) AS n FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE city = 'Delhi');", hint='Find Delhi customer ids first, then count orders with those ids.', why='The foreign key customer_id is what lets us connect an order to a city.')}
''', kw=['foreign key', 'parent', 'child', 'referential integrity', 'ON DELETE', 'CASCADE', 'SET NULL', 'RESTRICT', 'PRAGMA foreign_keys'])
K.talk('fk', '''A foreign key is a promise that a value in one table matches a real row in another. Every order's customer id must be the id of an existing
customer. The database checks this promise on every change. Try the first block, inserting an order for customer ninety nine fails, because that
customer does not exist. Try the second, deleting Asha fails, because her orders still point at her. You choose what happens on delete: refuse,
cascade the delete to the children, or set their link to NULL. One SQLite detail, foreign keys are off by default, and every connection must
switch them on with a pragma, which these pages already do. Think of a library that will not lend a book to a card number nobody owns.''')

K.lesson('rel', 'One to one, one to many, many to many', f'''
<p>Tables relate in three shapes. Spotting the shape tells you where the foreign key goes.</p>
{table(['Shape', 'Real life', 'How to build it'], [
    ['One to many', 'one customer, many orders', 'foreign key on the many side: orders.customer_id'],
    ['Many to many', 'an order has many products, a product is in many orders', 'a junction table with two foreign keys: order_items(order_id, product_id)'],
    ['One to one', 'one person, one passport', 'foreign key that is also UNIQUE, or share the same primary key']])}
{K.sql('m2m', """SELECT order_id, product_id, qty
FROM order_items
WHERE product_id = 2;""", title='Many to many through a junction table', notes={3: 'Notebook (product 2) appears in several orders, and each of those orders has other products too.'})}
<h3>Reading an ER diagram</h3>
<p>An <b>entity relationship (ER) diagram</b> draws tables as boxes and relationships as lines. Peter Chen introduced the ER model in 1976. Most tools today draw <b>crow’s foot</b> notation: a three pronged foot means "many", a bar means "one", a circle means "zero allowed".</p>
{table(['Line end', 'Means'], [['|| (two bars)', 'exactly one'], ['o| (circle, bar)', 'zero or one'], ['|< (bar, crow’s foot)', 'one or many'], ['o< (circle, crow’s foot)', 'zero or many']])}
{steps('The shop as an ER diagram', [
    'customers (|| to o&lt;) orders: a customer has zero or many orders, each order belongs to exactly one customer.',
    'orders (|| to |&lt;) order_items: an order has one or many lines.',
    'products (|| to o&lt;) order_items: a product appears in zero or many lines.',
    eq('orders and products are many to many, through order_items')])}
{K.lab('l-m2m', 'm', 'Which orders bought a notebook', 'Show the <code>order_id</code> of every order that contains product 2 (Notebook), smallest id first.', 'SELECT order_id FROM order_items WHERE product_id = 2 ORDER BY order_id;', hint='The junction table holds the pairs.', why='Each row of order_items is one product in one order.', ordered=True)}
''', kw=['one to many', 'many to many', 'one to one', 'junction table', 'bridge table', 'ER diagram', 'crow’s foot', 'Chen 1976', 'cardinality'])
K.talk('rel', '''Tables relate in three shapes. One to many is the most common, one customer has many orders, and the foreign key goes on the many side.
Many to many, like orders and products, needs a junction table in the middle that holds pairs, here order items with an order id and a product
id. One to one, like a person and a passport, uses a foreign key that is also unique. Designers draw all this as an entity relationship
diagram, an idea Peter Chen introduced in 1976. In crow's foot notation, a three pronged foot means many and a bar means one. Think of a school
where one class has many students, and students and clubs meet through a club membership list.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Each table is one kind of thing. Keys are the name tags and the arrows that point from one table to another.</p>',
    '<p>Referential integrity means every foreign key value matches a parent key or is NULL. Actions such as CASCADE decide what happens to children when a parent changes.</p>',
    '<p>Foreign keys can be deferred: DEFERRABLE INITIALLY DEFERRED checks them at COMMIT instead of after each statement, which lets you insert two rows that point at each other inside one transaction. Child key columns should be indexed, or every parent delete scans the whole child table.</p>',
    '<p>Distributed and sharded databases often drop foreign key enforcement across machines because checking a parent on another server is slow. They move the check into application code or background jobs, trading safety for speed.</p>')}
{deep('UUIDs as keys', '<p>Some systems use UUIDs (128 bit random identifiers) instead of 1, 2, 3, so that many servers can create ids without talking to each other. The cost is bigger keys and indexes. Time ordered UUIDs (version 7, RFC 9562, 2024) keep new ids near each other in the index.</p>')}
''', kw=['referential integrity', 'deferred constraint', 'index foreign keys', 'UUID', 'sharding'])
K.talk('levels', '''Up the ladder. For a child, tables are boxes of one kind of thing, and keys are name tags and arrows. At college level, referential integrity
means every foreign key points at a real parent or is NULL, and actions like cascade decide what happens to children. At masters level, a foreign
key can be deferred, so it is checked only at commit, and you should index the child column so deleting a parent stays fast. At research level,
huge databases spread over many servers sometimes skip foreign key checks across machines, because asking another server is slow. Think of a postal
address, it only works if the house really exists at the end of it.''')

K.quiz('e', 'A primary key must be', ['Unique and not NULL', 'A number', 'The first column', 'Text'], 0, 'Names one row.', 'Uniqueness and no NULLs.')
K.quiz('e', 'orders.customer_id is a', ['Primary key', 'Foreign key', 'Index', 'View'], 1, 'Points elsewhere.', 'It references customers.id.')
K.quiz('e', 'Which relationship needs a junction table?', ['One to one', 'One to many', 'Many to many', 'None'], 2, 'Pairs.', 'Many to many is split into two one to many links.')
K.quiz('e', 'A surrogate key is', ['A real world code', 'A made up id with no outside meaning', 'A foreign key', 'A NULL key'], 1, 'Invented.', 'For example an auto increment id.')
K.quiz('m', 'In one to many, where does the foreign key go?', ['The one side', 'The many side', 'Both', 'A new table'], 1, 'Each order names its customer.', 'The many side stores the parent id.')
K.quiz('m', 'ON DELETE CASCADE means', ['Deleting a parent fails', 'Deleting a parent deletes its children', 'Children get NULL', 'Nothing'], 1, 'Waterfall.', 'Child rows are removed with the parent.')
K.quiz('m', 'SQLite enforces foreign keys', ['Always', 'Only after PRAGMA foreign_keys = ON', 'Never', 'Only for INTEGER keys'], 1, 'Off by default.', 'It is a per connection setting.')
K.quiz('m', 'order_items has primary key (order_id, product_id). This is a', ['Surrogate key', 'Composite key', 'Foreign key only', 'Candidate key that is NULL'], 1, 'Two columns.', 'A key made of two columns.')
K.quiz('h', 'Which anomaly: a new customer cannot be stored until they order?', ['Update', 'Insert', 'Delete', 'None'], 1, 'Nowhere to live.', 'Insert anomaly.')
K.quiz('h', 'A crow’s foot at the end of a line means', ['One', 'Many', 'Zero', 'Optional'], 1, 'Three prongs.', 'It marks the many side.')
K.quiz('x', 'Why index a foreign key column?', ['It is required', 'Parent deletes and joins would scan the child table', 'To make it unique', 'To allow NULL'], 1, 'Lookups by parent id.', 'Checking children of a parent needs a fast lookup.')

K.calc('e', 'How many orders has Asha (customer 1) placed?', str(value('shop', 'SELECT count(*) FROM orders WHERE customer_id = 1')), 'Count rows with customer_id 1.',
       ['Look at orders.customer_id.', 'Orders 101, 103 and 110 have customer_id 1.', eq('3 orders')], check=value('shop', 'SELECT count(*) FROM orders WHERE customer_id = 1'))
K.calc('e', 'How many lines (rows) does order 104 have in order_items?', str(value('shop', 'SELECT count(*) FROM order_items WHERE order_id = 104')), 'Rows with order_id 104.',
       ['Order 104 bought product 6 and product 2.', 'Each product is one line.', eq('2 lines')], check=value('shop', 'SELECT count(*) FROM order_items WHERE order_id = 104'))
K.calc('m', 'In how many different orders does the Notebook (product 2) appear?', str(value('shop', 'SELECT count(*) FROM order_items WHERE product_id = 2')), 'Junction rows for product 2.',
       ['Find product_id 2 in order_items.', 'Orders 101, 104 and 109.', eq('3 orders')], check=value('shop', 'SELECT count(*) FROM order_items WHERE product_id = 2'))
K.calc('m', 'How many customers have never placed an order?', str(value('shop', 'SELECT count(*) FROM customers WHERE id NOT IN (SELECT customer_id FROM orders)')), 'Customers missing from orders.customer_id.',
       ['Customers who ordered: 1, 2, 3, 5, 7.', 'All customers: 1 to 8.', eq('4, 6 and 8 never ordered: 3')], check=value('shop', 'SELECT count(*) FROM customers WHERE id NOT IN (SELECT customer_id FROM orders)'))
K.calc('m', 'How many products have never been ordered?', str(value('shop', 'SELECT count(*) FROM products WHERE id NOT IN (SELECT product_id FROM order_items)')), 'Products missing from order_items.',
       ['Products in order_items: 1, 2, 3, 5, 6, 7, 8, 10.', 'Missing: 4 (Lunch box) and 9 (Desk lamp).', eq('2 products')], check=value('shop', 'SELECT count(*) FROM products WHERE id NOT IN (SELECT product_id FROM order_items)'))
K.calc('h', 'A one big table design repeats the customer city on every order row. With 10 orders, how many city values are stored? (Count the NULL as stored.)', '10', 'One per order row.',
       ['Each order row carries its customer’s city.', 'There are 10 orders.', eq('10 values instead of 8 in a customers table')], check=10)
K.calc('h', 'How many customers does a many to many junction need to link 3 students to 4 clubs if every student joins every club? Answer the number of junction rows.', '12', 'Every pair.',
       ['Each pair is one row.', '3 students × 4 clubs.', eq('12 rows')], check=12)
K.calc('h', 'If Asha (id 1) were deleted with ON DELETE CASCADE on orders, how many orders would also go?', str(value('shop', 'SELECT count(*) FROM orders WHERE customer_id = 1')), 'Her children.',
       ['CASCADE deletes every child row.', 'Asha has 3 orders.', eq('3 orders (and their order_items would need their own rule)')], check=value('shop', 'SELECT count(*) FROM orders WHERE customer_id = 1'))

K.must('Why many tables', 'One big table repeats data and causes update, insert and delete anomalies. Store each fact once and link with keys.')
K.must('Primary key', 'Unique, never NULL, one per table. Surrogate (made up id) or natural (real world). Composite keys use several columns.')
K.must('Foreign key', 'Must match a parent key or be NULL. Actions: NO ACTION, RESTRICT, CASCADE, SET NULL, SET DEFAULT. SQLite needs PRAGMA foreign_keys = ON.')
K.must('Relationship shapes', 'One to many: FK on the many side. Many to many: junction table. One to one: FK plus UNIQUE.')
K.must('ER diagrams', 'Boxes for tables, lines for relationships. Crow’s foot means many, bar means one, circle means zero allowed.')

T = K.topic(
    slug='sql-keys', topic='sql-keys', step=(3, 'Many tables', 'sql-many', 'Keys and relationships, every kind of join, subqueries and set operations.', 'Intermediate'),
    title='Keys and relationships between tables', short='Keys and relations', badge='3.1', minutes=40, added='2026-11-23',
    lead='See why one big table goes wrong, choose good primary keys, let foreign keys guard every link, and recognise one to one, one to many and many to many in an ER diagram.',
    desc='Anomalies of one big table, candidate, primary, natural, surrogate and composite keys, foreign keys and ON DELETE actions, PRAGMA foreign_keys, relationship shapes, junction tables, ER diagrams and crow’s foot notation.',
    summary='Why tables are split, primary and foreign keys, delete actions, and one to many and many to many relationships.',
    keywords=['primary key', 'foreign key', 'surrogate key', 'composite key', 'one to many', 'many to many', 'ER diagram', 'CASCADE'],
    recap='<p>Each fact lives in one table, a primary key names each row, a foreign key points at a parent, and junction tables carry many to many links.</p>')
