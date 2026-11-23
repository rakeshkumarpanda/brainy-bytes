# Chapter 4.2: changing data: INSERT (VALUES, several rows, INSERT ... SELECT), UPDATE with WHERE and UPDATE ... FROM,
# DELETE, UPSERT (ON CONFLICT DO UPDATE / DO NOTHING), INSERT OR REPLACE / OR IGNORE, RETURNING, foreign key actions.
# Sources: sqlite.org lang_insert.html, lang_update.html (UPDATE FROM since 3.33.0), lang_delete.html (truncate
# optimization), lang_upsert.html (since 3.24.0, excluded. prefix), lang_returning.html (since 3.35.0),
# foreignkeys.html (ON DELETE / ON UPDATE actions), postgresql.org sql-merge.html (MERGE since 15), MySQL insert-on-duplicate.html.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('insert', 'INSERT: adding rows', f'''
<p>Tables start empty and grow one INSERT at a time. You name the columns you are filling, then give the values in the same order. Columns you leave out get their DEFAULT, or NULL.</p>
{fxs(fx('One or more rows', '<code>INSERT INTO t (a, b) VALUES (1, \'x\'), (2, \'y\');</code>', 'Always list the columns. The statement keeps working even if someone later adds a column.', key=True),
     fx('Copy from a query', '<code>INSERT INTO t (a, b) SELECT ... ;</code>', 'Every row the SELECT returns becomes a new row.'))}
{K.sql('ins', """INSERT INTO customers (name, city, email, joined)
VALUES ('Tara', 'Mumbai', 'tara@mail.in', '2025-07-10'),
       ('Dev', NULL, NULL, '2025-07-11');
SELECT id, name, city FROM customers WHERE id > 7;""", title='Two new customers in one statement', notes={1: 'id is left out, so SQLite gives the next numbers, 9 and 10.', 3: 'NULL for what we do not know yet.'})}
{K.sql('inssel', """CREATE TABLE restock (product_id INTEGER, name TEXT);
INSERT INTO restock (product_id, name)
SELECT id, name FROM products WHERE stock = 0;
SELECT * FROM restock;""", title='INSERT ... SELECT copies query results into a table', notes={3: 'Every out of stock product becomes a row of the restock list.'})}
{note('Writing INSERT INTO t VALUES (...) without a column list depends on the exact column order. It breaks quietly the day a column is added. List the columns.', 'warn')}
{K.lab('l-ins', 'e', 'A new product', "Add a product named <code>Sketch pens</code> in category <code>Stationery</code> with price 80 and stock 25. Then show <code>name</code>, <code>price</code> and <code>stock</code> of every Stationery product.",
"""INSERT INTO products (name, category, price, stock) VALUES ('Sketch pens', 'Stationery', 80, 25);
SELECT name, price, stock FROM products WHERE category = 'Stationery';""", hint='INSERT INTO products (name, category, price, stock) VALUES (...), then a SELECT.', why='The new row joins the three existing Stationery products.')}
''', kw=['INSERT', 'VALUES', 'INSERT SELECT', 'multi row insert', 'column list', 'add rows'])
K.talk('insert', '''Tables start empty and grow one insert at a time. You write INSERT INTO, the table name, the list of columns you are filling, and then the values
in the same order. Columns you leave out get their default value, or NULL. One statement can add many rows, each in its own pair of brackets.
INSERT can also take its rows from a SELECT, which is how people copy or archive data, for example building a restock list from every product that
has run out. Always write the list of columns, because a statement without it breaks quietly the day someone adds a new column. Think of filling a
new row in a register, writing each value under the right heading.''')

K.lesson('update', 'UPDATE and DELETE: changing and removing rows', f'''
<p><code>UPDATE</code> changes values in rows that already exist. <code>DELETE</code> removes rows. Both use WHERE to pick the rows, and both change <b>every</b> row when WHERE is missing.</p>
{pk('sqdml')}
{K.sql('upd', """UPDATE products
SET price = price + 20, stock = stock + 10
WHERE category = 'Kitchen';
SELECT name, price, stock FROM products WHERE category = 'Kitchen';""", title='Change two columns in the picked rows', notes={2: 'The right side uses the old values. Several columns are separated by commas.', 3: 'Only the two Kitchen products change.'})}
{K.sql('del', """DELETE FROM order_items WHERE order_id = 105;
DELETE FROM orders WHERE status = 'cancelled';
SELECT count(*) AS orders_left FROM orders;""", title='Delete children first, then the parent', notes={1: 'Order 105 has an order line. With foreign keys on, the order cannot go while its lines still point at it.', 2: 'Now the cancelled order can be deleted.'})}
{K.sql('updfrom', """UPDATE products
SET stock = stock - s.sold
FROM (SELECT product_id, SUM(qty) AS sold
      FROM order_items GROUP BY product_id) AS s
WHERE s.product_id = products.id;
SELECT name, stock FROM products ORDER BY id LIMIT 4;""", title='UPDATE ... FROM: change rows using another table', notes={3: 'A derived table with the quantity sold of each product.', 5: 'Join it to products. SQLite has supported UPDATE FROM since 3.33, PostgreSQL has it too, SQL Server writes it slightly differently.'})}
{steps('The safe way to change data', [
    'Write the WHERE as a SELECT first: <code>SELECT * FROM products WHERE category = \'Kitchen\';</code>',
    'Check the rows. Are these exactly the rows you mean.',
    'Change SELECT * into UPDATE ... SET or DELETE, keeping the same WHERE.',
    'On a real server, do it inside a transaction (chapter 7.3), so a mistake can be rolled back.'])}
{K.lab('l-upd', 'm', 'A sale on electronics', 'Lower the price of every Electronics product by 100, then show <code>name</code> and <code>price</code> of the Electronics products.',
"""UPDATE products SET price = price - 100 WHERE category = 'Electronics';
SELECT name, price FROM products WHERE category = 'Electronics';""", hint="UPDATE ... SET price = price - 100 WHERE category = 'Electronics'.", why='Each Electronics price drops by 100, the rest are untouched.')}
{K.lab('l-del', 'm', 'Clear old pending orders', 'Delete the order lines and then the orders whose status is <code>pending</code>. Show <code>id</code> and <code>status</code> of the orders that remain.',
"""DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE status = 'pending');
DELETE FROM orders WHERE status = 'pending';
SELECT id, status FROM orders;""", hint='Order lines point at orders, so delete the lines first, with IN and a subquery.', why='Deleting the children first keeps every foreign key satisfied.')}
''', kw=['UPDATE', 'DELETE', 'SET', 'UPDATE FROM', 'missing WHERE', 'change rows', 'remove rows'])
K.talk('update', '''UPDATE changes values in rows that already exist, and DELETE removes rows. Both use WHERE to choose the rows, and here is the most important
warning in this course. Without WHERE, they change or remove every row in the table. In the animation, choose a change and a WHERE test, and watch
which rows are marked before anything happens. Then clear the WHERE box and see the whole table change. The safe habit is to write the WHERE as a
SELECT first, check the rows, and only then turn it into an update or delete. When rows have children, such as orders with order lines, delete the
children first. Think of a teacher who reads out the names on a list before striking any of them off.''')

K.lesson('upsert', 'UPSERT and RETURNING', f'''
<p>A common job: "add this row, but if it already exists, update it". That is an <b>UPSERT</b> (update or insert). It needs a UNIQUE or PRIMARY KEY column so the engine can detect the clash.</p>
{K.sql('upsert', """CREATE TABLE stock_count (product TEXT PRIMARY KEY, qty INTEGER NOT NULL);
INSERT INTO stock_count VALUES ('Notebook', 150);
INSERT INTO stock_count (product, qty) VALUES ('Notebook', 20), ('Ruler', 30)
ON CONFLICT (product) DO UPDATE SET qty = qty + excluded.qty;
SELECT * FROM stock_count;""", db='', title='Add new rows, top up existing ones', notes={3: 'Notebook clashes with the primary key. Ruler is new.', 4: 'excluded.qty is the value we tried to insert. Notebook becomes 150 + 20, Ruler is inserted.'})}
{table(['Engine', 'How to write an upsert'], [
    ['SQLite (3.24+) and PostgreSQL (9.5+)', 'INSERT ... ON CONFLICT (key) DO UPDATE SET ... or DO NOTHING'],
    ['MySQL', 'INSERT ... ON DUPLICATE KEY UPDATE ...'],
    ['SQL Server, Oracle, PostgreSQL 15+', 'MERGE INTO target USING source ON ... WHEN MATCHED ... WHEN NOT MATCHED ...'],
    ['SQLite shortcuts', 'INSERT OR IGNORE skips a clashing row, INSERT OR REPLACE deletes the old row and inserts the new one']])}
<p><code>RETURNING</code> hands back the rows a statement just changed, so the app gets new ids or new values without a second query. SQLite has it since 3.35, PostgreSQL for much longer. SQL Server uses OUTPUT instead.</p>
{K.sql('returning', """INSERT INTO orders (customer_id, order_date, status)
VALUES (4, '2025-07-12', 'pending')
RETURNING id, status;
UPDATE products SET stock = stock - 1 WHERE id = 8
RETURNING name, stock;""", title='Get the new values straight back', notes={3: 'The id SQLite just gave the order comes back at once.', 5: 'The football stock after the change.'})}
{note('INSERT OR REPLACE is not the same as an upsert. It deletes the old row, so columns you did not supply go back to their defaults, and ON DELETE actions on child rows can fire.', 'warn')}
{K.lab('l-upsert', 'h', 'Count the visits', "The table <code>visits (page TEXT PRIMARY KEY, n INTEGER)</code> holds <code>('home', 5)</code>. In one statement, record one visit to <code>home</code> and one to <code>cart</code>, adding 1 to existing pages. Then show every row ordered by page.",
"""INSERT INTO visits (page, n) VALUES ('home', 1), ('cart', 1)
ON CONFLICT (page) DO UPDATE SET n = n + excluded.n;
SELECT * FROM visits ORDER BY page;""", db='', setup="CREATE TABLE visits (page TEXT PRIMARY KEY, n INTEGER); INSERT INTO visits VALUES ('home', 5);", hint='ON CONFLICT (page) DO UPDATE SET n = n + excluded.n', why='home becomes 6, cart is new with 1.', ordered=True)}
''', kw=['UPSERT', 'ON CONFLICT', 'excluded', 'MERGE', 'ON DUPLICATE KEY UPDATE', 'INSERT OR REPLACE', 'INSERT OR IGNORE', 'RETURNING'])
K.talk('upsert', '''A very common job is to add a row, but update it if it already exists. That is called an upsert, update or insert. The engine needs a unique
or primary key column to notice the clash. In SQLite and PostgreSQL you write INSERT, then ON CONFLICT, then DO UPDATE or DO NOTHING. Inside the
update, the word excluded means the row you tried to insert. MySQL writes ON DUPLICATE KEY UPDATE, and SQL Server and Oracle use MERGE. RETURNING
hands back the rows a statement just changed, so an app gets the new id without asking again. Think of a shop counter where a known customer gets
points added to their card, and a new customer gets a fresh card.''')

K.lesson('fkact', 'Foreign key actions: what happens to the children', f'''
<p>When a parent row is deleted or its key changes, the foreign key decides what happens to the child rows. You choose with <code>ON DELETE</code> and <code>ON UPDATE</code>.</p>
{table(['Action', 'When the parent is deleted', 'Good for'], [
    ['NO ACTION (default) or RESTRICT', 'the delete is refused while children exist', 'orders that must never lose their customer'],
    ['CASCADE', 'the children are deleted too', 'order lines that mean nothing without their order'],
    ['SET NULL', 'the child column becomes NULL', 'an employee whose department is closed'],
    ['SET DEFAULT', 'the child column takes its default', 'moving items to a general bucket']])}
{K.sql('cascade', """CREATE TABLE albums (id INTEGER PRIMARY KEY, title TEXT);
CREATE TABLE photos (
  id INTEGER PRIMARY KEY,
  album_id INTEGER REFERENCES albums(id) ON DELETE CASCADE,
  file TEXT);
INSERT INTO albums VALUES (1, 'Goa trip'), (2, 'Diwali');
INSERT INTO photos VALUES (1, 1, 'beach.jpg'), (2, 1, 'fort.jpg'), (3, 2, 'lamps.jpg');
DELETE FROM albums WHERE id = 1;
SELECT * FROM photos;""", db='', title='CASCADE: delete an album, its photos go too', notes={4: 'The action is written on the child column.', 8: 'Deleting album 1 also deletes its two photos.'})}
{K.sql('setnull', """CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE players (name TEXT, team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL);
INSERT INTO teams VALUES (1, 'Red'), (2, 'Blue');
INSERT INTO players VALUES ('Anu', 1), ('Bilal', 2);
DELETE FROM teams WHERE id = 1;
SELECT * FROM players;""", db='', title='SET NULL: the child stays, its link is cleared', notes={5: 'Anu keeps her row, but team_id becomes NULL.'})}
{scene('closing an account', '<p>When a user deletes their account in a photo app, the company must remove their photos, comments and likes too. Writing ON DELETE CASCADE on each child table makes the database do it in one step, and no orphan photo is left behind pointing at a user who no longer exists.</p>')}
{note('In SQLite, foreign keys and their actions only work when PRAGMA foreign_keys = ON. Every SQL block on this site turns it on for you.', 'tip')}
{K.lab('l-cascade', 'h', 'Delete a playlist and its songs', 'Tables <code>playlists</code> and <code>songs</code> already exist, with <code>songs.list_id</code> declared <code>ON DELETE CASCADE</code>. Delete the playlist called <code>Old</code>, then show the <code>title</code> of every song left.',
"""DELETE FROM playlists WHERE name = 'Old';
SELECT title FROM songs;""", db='', setup="""CREATE TABLE playlists (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE songs (title TEXT, list_id INTEGER REFERENCES playlists(id) ON DELETE CASCADE);
INSERT INTO playlists VALUES (1, 'Old'), (2, 'New');
INSERT INTO songs VALUES ('Yesterday', 1), ('Imagine', 1), ('Shape of You', 2), ('Believer', 2);""", hint="Only one statement changes data: DELETE FROM playlists WHERE name = 'Old'.", why='CASCADE removes the two songs of the Old playlist for you.')}
''', kw=['ON DELETE CASCADE', 'SET NULL', 'RESTRICT', 'NO ACTION', 'referential action', 'orphan rows'])
K.talk('fkact', '''When a parent row is deleted, the foreign key decides what happens to its children. The default, no action, simply refuses the delete while
children still point at the parent. CASCADE deletes the children too, which suits order lines or photos that mean nothing on their own. SET NULL
keeps the children but clears their link, like players whose team was disbanded. You write the action on the child column, after REFERENCES. In
SQLite these rules only work when foreign keys are switched on, and every block on this site switches them on for you. Think of deleting a photo
album on your phone, and every photo inside it going with it.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>INSERT adds rows, UPDATE changes them, DELETE removes them. WHERE says which rows, and forgetting it touches all of them.</p>',
    '<p>These statements are DML, data manipulation language. Each statement is atomic: if one row breaks a constraint, the whole statement is undone, not just that row.</p>',
    '<p>UPSERT and MERGE need a unique index to detect conflicts safely under concurrency. Foreign key actions are declarative triggers, and statement level RETURNING removes a round trip between app and database.</p>',
    '<p>Inside the engine, an UPDATE is often a delete plus an insert. PostgreSQL keeps old row versions for MVCC (chapter 7.3), which VACUUM later cleans up, while InnoDB keeps undo logs. Bulk loading tools such as PostgreSQL COPY and SQLite’s .import skip much per statement work.</p>')}
{deep('Soft delete', '<p>Many apps never really DELETE. They add a column such as <code>deleted_at</code> and set it instead, then filter <code>WHERE deleted_at IS NULL</code> everywhere. This allows undo and audits, at the cost of every query remembering the filter. Views (chapter 4.3) can hide that filter.</p>')}
''', kw=['DML', 'atomic statement', 'MVCC', 'bulk load', 'COPY', 'soft delete'])
K.talk('levels', '''Here is the ladder for this chapter. For a beginner, insert adds, update changes and delete removes, and WHERE says which rows. At college level,
these statements are called data manipulation language, and each statement is atomic, so if one row breaks a rule, the whole statement is undone.
At masters level, upserts depend on unique indexes to stay correct when many users write at once. At research level, an update inside the engine is
often a delete plus an insert, and PostgreSQL keeps old row versions until a cleaner called VACUUM removes them. Think of a librarian who keeps the
old card in a drawer until nobody needs it.''')

K.quiz('e', 'Which statement adds rows?', ['ADD', 'INSERT', 'UPDATE', 'APPEND'], 1, 'Insert.', 'INSERT INTO adds rows.')
K.quiz('e', 'UPDATE products SET price = 0 with no WHERE changes', ['No rows', 'One row', 'Every row', 'Only NULL rows'], 2, 'No filter.', 'Without WHERE every row is changed.')
K.quiz('e', 'A column left out of INSERT with no DEFAULT gets', ['0', 'An empty string', 'NULL', 'An error always'], 2, 'Unknown.', 'It becomes NULL, unless NOT NULL refuses it.')
K.quiz('e', 'Which removes rows but keeps the table?', ['DROP TABLE', 'DELETE', 'ALTER TABLE', 'REMOVE'], 1, 'Rows only.', 'DELETE removes rows, DROP removes the table.')
K.quiz('m', 'In SET price = price + 20, the price on the right is', ['The new value', 'The old value', 'Always 0', 'An error'], 1, 'Before the change.', 'Expressions read the old row.')
K.quiz('m', 'In ON CONFLICT DO UPDATE, excluded.qty means', ['The old value', 'The value you tried to insert', 'A deleted row', 'NULL'], 1, 'The new attempt.', 'excluded holds the row that clashed.')
K.quiz('m', 'MySQL’s upsert is written', ['ON CONFLICT', 'ON DUPLICATE KEY UPDATE', 'MERGE ONLY', 'UPSERT INTO'], 1, 'Duplicate key.', 'MySQL uses ON DUPLICATE KEY UPDATE.')
K.quiz('m', 'ON DELETE CASCADE on a child column means deleting the parent', ['Is refused', 'Deletes the children too', 'Sets children to NULL', 'Does nothing'], 1, 'Cascade.', 'The children are deleted as well.')
K.quiz('m', 'What does RETURNING give back?', ['The old table', 'The rows the statement changed', 'The query plan', 'Nothing'], 1, 'Changed rows.', 'It returns the affected rows.')
K.quiz('h', 'INSERT OR REPLACE on a clashing key', ['Updates only the given columns', 'Deletes the old row and inserts the new one', 'Skips the row', 'Fails'], 1, 'Replace.', 'The old row is deleted, so unlisted columns lose their values.')
K.quiz('x', 'One row in a multi row INSERT breaks a CHECK. What is stored?', ['The rows before it', 'All rows except it', 'No rows from that statement', 'All rows'], 2, 'Atomic.', 'The whole statement is undone.')

ins2 = value('shop', 'SELECT max(id) FROM customers', setup="INSERT INTO customers (name, joined) VALUES ('Tara', '2025-07-10'), ('Dev', '2025-07-11');")
K.calc('e', 'Two customers are inserted without ids into a table whose largest id is 8. What id does the second one get?', str(ins2), 'Next numbers.',
       ['The first new row gets 8 + 1 = 9.', 'The second gets 9 + 1.', eq(f'{ins2}')], check=ins2)
kit = value('shop', "SELECT sum(price) FROM products WHERE category = 'Kitchen'", setup="UPDATE products SET price = price + 20 WHERE category = 'Kitchen';")
K.calc('e', 'After raising both Kitchen prices by 20 (250 and 399), what is their total?', str(kit), 'Add 20 to each.',
       ['250 + 20 = 270.', '399 + 20 = 419.', eq(f'270 + 419 = {kit}')], check=kit)
nz = value('shop', 'SELECT count(*) FROM products WHERE stock = 0')
K.calc('e', 'How many rows does INSERT INTO restock SELECT ... FROM products WHERE stock = 0 add?', str(nz), 'Out of stock products.',
       ['Lunch box has stock 0.', 'Desk lamp has stock 0.', eq(f'{nz} rows')], check=nz)
left = value('shop', 'SELECT count(*) FROM orders', setup="DELETE FROM order_items WHERE order_id = 105; DELETE FROM orders WHERE status = 'cancelled';")
K.calc('m', 'How many orders remain after deleting the cancelled ones?', str(left), 'One is cancelled.',
       ['There are 10 orders.', 'Only order 105 is cancelled.', eq(f'10 − 1 = {left}')], check=left)
up = value('', "SELECT qty FROM s WHERE product = 'Notebook'", setup="CREATE TABLE s (product TEXT PRIMARY KEY, qty INTEGER); INSERT INTO s VALUES ('Notebook', 150); INSERT INTO s VALUES ('Notebook', 20) ON CONFLICT (product) DO UPDATE SET qty = qty + excluded.qty;")
K.calc('m', 'Notebook holds 150. An upsert inserts Notebook 20 with DO UPDATE SET qty = qty + excluded.qty. What is the new qty?', str(up), 'Old plus attempted.',
       ['qty is the old value, 150.', 'excluded.qty is the attempted value, 20.', eq(f'150 + 20 = {up}')], check=up)
el = value('shop', "SELECT sum(price) FROM products WHERE category = 'Electronics'", setup="UPDATE products SET price = price - 100 WHERE category = 'Electronics';")
K.calc('m', 'After every Electronics price drops by 100 (1499, 699, 1250), what is their total?', str(el), 'Subtract 300 in all.',
       ['Before: 1499 + 699 + 1250 = 3448.', 'Three products, each 100 less.', eq(f'3448 − 300 = {el}')], check=el)
ph = value('', 'SELECT count(*) FROM photos', setup="""CREATE TABLE albums (id INTEGER PRIMARY KEY); CREATE TABLE photos (id INTEGER PRIMARY KEY, album_id INTEGER REFERENCES albums(id) ON DELETE CASCADE);
INSERT INTO albums VALUES (1), (2); INSERT INTO photos VALUES (1, 1), (2, 1), (3, 2); PRAGMA foreign_keys = ON; DELETE FROM albums WHERE id = 1;""")
K.calc('h', 'Album 1 has 2 photos and album 2 has 1, with ON DELETE CASCADE. After deleting album 1, how many photos remain?', '1', 'The children go with the parent.',
       ['Album 1 is deleted.', 'CASCADE deletes its 2 photos.', eq('3 − 2 = 1')], check=1)
sold = value('shop', 'SELECT stock FROM products WHERE id = 2', setup='UPDATE products SET stock = stock - s.sold FROM (SELECT product_id, SUM(qty) AS sold FROM order_items GROUP BY product_id) AS s WHERE s.product_id = products.id;')
K.calc('h', 'Notebook (stock 150) appears in order lines with qty 5, 10 and 3. After the UPDATE ... FROM that subtracts sold quantities, what is its stock?', str(sold), 'Subtract the total sold.',
       ['Sold: 5 + 10 + 3 = 18.', 'Stock before: 150.', eq(f'150 − 18 = {sold}')], check=sold)

K.must('INSERT', 'List the columns, then the values in the same order. Several rows or a SELECT can supply them.')
K.must('UPDATE and DELETE', 'WHERE picks the rows. No WHERE means every row. Test the WHERE with a SELECT first.')
K.must('UPSERT', 'ON CONFLICT DO UPDATE or DO NOTHING in SQLite and PostgreSQL, ON DUPLICATE KEY UPDATE in MySQL, MERGE elsewhere. excluded is the attempted row.')
K.must('RETURNING', 'Gives back the changed rows, such as new ids, without a second query.')
K.must('Foreign key actions', 'NO ACTION refuses, CASCADE deletes children, SET NULL clears the link. Delete children before parents otherwise.')

T = K.topic(
    slug='sql-modify', topic='sql-modify', step=(4, 'Building and changing data', 'sql-make', 'Create your own tables with types and rules, change rows safely, and name steps with views and CTEs.', 'Intermediate'),
    title='Changing data: INSERT, UPDATE, DELETE and UPSERT', short='Changing data', badge='4.2', minutes=40, added='2026-11-23',
    lead='Add, change and remove rows safely, combine insert and update in one UPSERT, get changed rows back with RETURNING, and decide what happens to child rows.',
    desc='INSERT with VALUES and SELECT, UPDATE with WHERE and FROM, DELETE, the missing WHERE trap, UPSERT with ON CONFLICT, MERGE and ON DUPLICATE KEY, INSERT OR REPLACE, RETURNING, ON DELETE CASCADE and SET NULL.',
    summary='INSERT, UPDATE, DELETE, UPSERT, RETURNING and foreign key actions.',
    keywords=['INSERT', 'UPDATE', 'DELETE', 'UPSERT', 'RETURNING', 'ON DELETE CASCADE'],
    recap='<p>INSERT adds, UPDATE changes, DELETE removes, WHERE picks the rows, UPSERT handles clashes, and foreign key actions look after the children.</p>')
