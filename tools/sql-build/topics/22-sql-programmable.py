# Chapter 8.1: logic inside the database: triggers (BEFORE, AFTER, INSTEAD OF, OLD and NEW, WHEN, RAISE), audit logs,
# keeping derived data in step, generated columns, stored procedures and functions in server engines, and when to keep
# logic in the database versus the application.
# Sources: sqlite.org lang_createtrigger.html (BEFORE, AFTER, INSTEAD OF on views, FOR EACH ROW only, RAISE),
# gencol.html (generated columns since 3.31.0, VIRTUAL and STORED), postgresql.org plpgsql.html and sql-createprocedure.html
# (procedures since 11), learn.microsoft.com CREATE PROCEDURE (T-SQL), MySQL stored-programs-views.html.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('triggers', 'Triggers: code that runs on every change', f'''
<p>A <b>trigger</b> is a small program stored in the database that runs by itself when rows are inserted, updated or deleted. Inside it, <code>NEW</code> is the row after the change and <code>OLD</code> is the row before.</p>
{fxs(fx('Trigger', '<code>CREATE TRIGGER name AFTER UPDATE OF col ON t WHEN condition BEGIN ... ; END;</code>', 'BEFORE or AFTER, INSERT, UPDATE or DELETE. WHEN is optional.', key=True),
     fx('Refuse a change', "<code>SELECT RAISE(ABORT, 'message');</code>", 'Inside a trigger, stops the statement with an error (SQLite).'))}
{pk('sqtrig')}
{K.sql('audit', """CREATE TABLE price_log (product_id INTEGER, old_price INTEGER, new_price INTEGER, changed_at TEXT);
CREATE TRIGGER log_price AFTER UPDATE OF price ON products
WHEN NEW.price <> OLD.price
BEGIN
  INSERT INTO price_log VALUES (OLD.id, OLD.price, NEW.price, '2025-07-15');
END;
UPDATE products SET price = price + 50 WHERE category = 'Sports';
SELECT * FROM price_log;""", title='An audit log that fills itself', notes={2: 'Fires after any UPDATE that touches the price column.', 3: 'Skip updates that set the same price.', 7: 'One UPDATE of two rows fires the trigger twice: once per row.'})}
{table(['Timing', 'NEW', 'OLD', 'Typical use'], [
    ['BEFORE INSERT', 'the row about to be inserted', 'none', 'check or refuse values'],
    ['AFTER INSERT', 'the inserted row', 'none', 'write a log, update a total'],
    ['BEFORE or AFTER UPDATE', 'new values', 'old values', 'audit trails, history tables'],
    ['BEFORE or AFTER DELETE', 'none', 'the deleted row', 'archive the row before it goes'],
    ['INSTEAD OF (on a view)', 'values written to the view', 'old view row', 'make a view writable']])}
{K.lab('l-trig', 'm', 'Log new customers', 'Create a table <code>signup_log (customer_name TEXT)</code> and a trigger that adds the name of every newly inserted customer to it. Then insert customer Tara (joined 2025-07-20) and show every row of signup_log.',
"""CREATE TABLE signup_log (customer_name TEXT);
CREATE TRIGGER log_signup AFTER INSERT ON customers BEGIN INSERT INTO signup_log VALUES (NEW.name); END;
INSERT INTO customers (name, joined) VALUES ('Tara', '2025-07-20');
SELECT * FROM signup_log;""", hint='AFTER INSERT ON customers ... INSERT INTO signup_log VALUES (NEW.name)', why='The trigger fired once, for Tara.')}
''', kw=['trigger', 'CREATE TRIGGER', 'BEFORE', 'AFTER', 'NEW', 'OLD', 'RAISE', 'audit log'])
K.talk('triggers', '''A trigger is a small program stored inside the database that runs by itself whenever rows are inserted, updated or deleted. Inside the trigger,
NEW means the row after the change, and OLD means the row before. A BEFORE trigger can check values and refuse a change with an error. An AFTER
trigger is perfect for writing an audit log, so every price change is recorded without any app having to remember. In the animation, raise a price
and watch the log fill, then try a negative stock and watch the guard trigger refuse it. Triggers fire once for every changed row. Think of a door
that rings a bell every time it opens.''')

K.lesson('uses', 'Keeping data in step, and writable views', f'''
<p>Triggers can keep a stored total correct, or let people write through a view.</p>
{K.sql('total', """ALTER TABLE orders ADD COLUMN item_count INTEGER NOT NULL DEFAULT 0;
UPDATE orders SET item_count = (SELECT COALESCE(SUM(qty), 0) FROM order_items WHERE order_id = orders.id);
CREATE TRIGGER add_item AFTER INSERT ON order_items
BEGIN
  UPDATE orders SET item_count = item_count + NEW.qty WHERE id = NEW.order_id;
END;
INSERT INTO order_items VALUES (110, 2, 4);
SELECT id, item_count FROM orders WHERE id = 110;""", title='A stored total that can never drift', notes={2: 'Fill the column once.', 5: 'Every new order line adds its qty to its order.', 8: 'Order 110 had 1 item, now 5.'})}
{K.sql('instead', """CREATE VIEW cheap AS SELECT id, name, price FROM products WHERE price < 200;
CREATE TRIGGER cheap_update INSTEAD OF UPDATE ON cheap
BEGIN
  UPDATE products SET price = NEW.price WHERE id = OLD.id;
END;
UPDATE cheap SET price = 99 WHERE name = 'Notebook';
SELECT name, price FROM products WHERE id = 2;""", title='INSTEAD OF makes a view writable', notes={2: 'SQLite views are read only, so we say what an UPDATE on the view should really do.', 6: 'The change lands in products.'})}
{table(['Good use of a trigger', 'Risky use of a trigger'], [
    ['audit logs and history tables', 'business rules that hide surprising side effects'],
    ['keeping a denormalized total in step', 'triggers that fire other triggers several levels deep'],
    ['refusing values a CHECK cannot express', 'slow work inside a trigger on a busy table']])}
{note('Triggers are invisible from the app code. Document them, keep them short, and remember that bulk loads fire them once per row.', 'warn')}
{K.lab('l-instead', 'h', 'Delete through a view', 'Create a view <code>sports</code> of <code>id</code> and <code>name</code> of Sports products, and an INSTEAD OF DELETE trigger that sets the product’s stock to 0 instead of deleting it. Delete Football from the view, then show <code>name</code> and <code>stock</code> of the Sports products.',
"""CREATE VIEW sports AS SELECT id, name FROM products WHERE category = 'Sports';
CREATE TRIGGER sports_del INSTEAD OF DELETE ON sports BEGIN UPDATE products SET stock = 0 WHERE id = OLD.id; END;
DELETE FROM sports WHERE name = 'Football';
SELECT name, stock FROM products WHERE category = 'Sports';""", hint='Inside the INSTEAD OF DELETE trigger, run UPDATE products SET stock = 0 WHERE id = OLD.id.', why='The product stays, with stock 0, which is a kind of soft delete.')}
''', kw=['derived data', 'stored total', 'INSTEAD OF trigger', 'writable view', 'trigger risks', 'side effects'])
K.talk('uses', '''Triggers are good at keeping copies of data correct. Store an item count on each order, and an AFTER INSERT trigger on order lines adds each new
quantity, so the total can never drift. An INSTEAD OF trigger tells SQLite what an update or delete on a view should really do, which makes a read only
view writable. Use triggers for audit logs, history and stored totals, but keep them short and documented, because the app code cannot see them, and a
trigger that fires another trigger becomes hard to follow. Think of an automatic counter at a stadium gate that clicks once for every person.''')

K.lesson('generated', 'Generated columns', f'''
<p>A <b>generated column</b> is worked out from other columns of the same row. You never write it, and it can never be wrong. SQLite has them since 3.31 (2020), PostgreSQL since 12, MySQL since 5.7.</p>
{K.sql('gen', """CREATE TABLE lines (
  product TEXT, qty INTEGER, price INTEGER,
  total INTEGER GENERATED ALWAYS AS (qty * price) VIRTUAL,
  is_bulk INTEGER GENERATED ALWAYS AS (qty >= 10) STORED
);
INSERT INTO lines (product, qty, price) VALUES ('Notebook', 12, 60), ('Lamp', 1, 1250);
SELECT * FROM lines;""", db='', title='total and is_bulk fill themselves', notes={3: 'VIRTUAL: worked out each time the row is read.', 4: 'STORED: worked out on write and saved on disk, so it can be indexed cheaply.'})}
{K.sql('generr', """CREATE TABLE lines (qty INTEGER, price INTEGER,
  total INTEGER GENERATED ALWAYS AS (qty * price));
INSERT INTO lines (qty, price, total) VALUES (2, 50, 999);""", db='', title='You cannot write a generated column', err=True, notes={3: 'The engine refuses any attempt to set total directly.'})}
{table(['Option', 'Computed', 'Disk', 'Indexable'], [
    ['VIRTUAL (SQLite default)', 'on every read', 'none', 'yes, through an index on the column'],
    ['STORED', 'on every write', 'yes', 'yes']])}
{K.lab('l-gen', 'm', 'A full name that cannot drift', 'Create <code>people (first TEXT, last TEXT, full TEXT GENERATED ALWAYS AS (first || \' \' || last))</code>, insert Asha Rao and Ravi Iyer, and show <code>full</code> for every row.',
"""CREATE TABLE people (first TEXT, last TEXT, full TEXT GENERATED ALWAYS AS (first || ' ' || last));
INSERT INTO people (first, last) VALUES ('Asha', 'Rao'), ('Ravi', 'Iyer');
SELECT full FROM people;""", db='', hint='Insert only first and last. full fills itself.', why='The generated column joins the two names on every read.')}
''', kw=['generated column', 'computed column', 'VIRTUAL', 'STORED', 'GENERATED ALWAYS AS'])
K.talk('generated', '''A generated column is worked out from other columns of the same row, such as a line total from quantity times price. You never write it yourself,
so it can never be wrong. A VIRTUAL generated column is computed each time the row is read and takes no disk space. A STORED one is computed when the
row is written and saved, which makes it cheap to read and index. If you try to write a value into a generated column, the database refuses. SQLite,
PostgreSQL and MySQL all support them. Think of a spreadsheet cell holding a formula, which updates whenever its inputs change.''')

K.lesson('procs', 'Stored procedures and functions', f'''
<p>Server databases can store whole programs: <b>stored procedures</b> (run with CALL or EXEC) and <b>user defined functions</b> (used inside queries). SQLite has neither in SQL, because it runs inside your app, so the app registers functions in its own language instead.</p>
<pre class="sq-code">-- PostgreSQL (PL/pgSQL)
CREATE PROCEDURE transfer(src TEXT, dst TEXT, amt INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE accounts SET balance = balance - amt WHERE name = src;
  UPDATE accounts SET balance = balance + amt WHERE name = dst;
END $$;
CALL transfer('Asha', 'Ravi', 300);

-- SQL Server (T-SQL)
CREATE PROCEDURE transfer @src NVARCHAR(50), @dst NVARCHAR(50), @amt INT AS
BEGIN
  UPDATE accounts SET balance = balance - @amt WHERE name = @src;
  UPDATE accounts SET balance = balance + @amt WHERE name = @dst;
END;
EXEC transfer 'Asha', 'Ravi', 300;</pre>
{table(['Engine', 'Procedural language', 'Run with'], [
    ['PostgreSQL', 'PL/pgSQL, also PL/Python and others', 'CALL proc(...), SELECT func(...)'],
    ['SQL Server', 'T-SQL', 'EXEC proc ...'],
    ['MySQL', 'SQL/PSM style', 'CALL proc(...)'],
    ['Oracle', 'PL/SQL', 'EXEC proc, or a BEGIN ... END block'],
    ['SQLite', 'none in SQL, functions registered by the host app', 'used inside queries']])}
{table(['Logic in the database', 'Logic in the application'], [
    ['one place guards the data for every app', 'easier to test, version and debug'],
    ['fewer round trips for multi step work', 'scales out by adding app servers'],
    ['tied to one engine’s language', 'portable across databases']])}
{K.sql('udf', """SELECT name, price, ROUND(price * 1.18) AS with_gst,
       printf('%,d', price * 100) AS paise
FROM products LIMIT 3;""", title='SQLite’s built in functions cover a lot', notes={2: 'printf formats numbers. Apps can add their own functions too, for example in Python with create_function.'})}
''', kw=['stored procedure', 'user defined function', 'PL/pgSQL', 'T-SQL', 'PL/SQL', 'CALL', 'EXEC', 'business logic'])
K.talk('procs', '''Server databases can store whole programs. A stored procedure runs a sequence of statements, such as a transfer, when called with CALL or EXEC. A
user defined function returns a value and can be used inside a query. PostgreSQL uses PL pg SQL, SQL Server uses T SQL, and Oracle uses PL SQL. SQLite
runs inside your app, so it has no procedures in SQL, and the app registers extra functions in its own language. Keeping logic in the database guards
the data for every app and saves round trips, while keeping it in the app is easier to test and move between engines. Think of a recipe card kept in
the kitchen versus one each cook carries in their pocket.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Triggers are automatic reactions to changes. Generated columns are formulas. Procedures are saved programs.</p>',
    '<p>BEFORE triggers check, AFTER triggers log or update totals, INSTEAD OF triggers make views writable. Generated columns are VIRTUAL or STORED. Procedures and functions live in server engines.</p>',
    '<p>Triggers run inside the same transaction as the statement, so a failing trigger rolls the statement back. Statement level triggers (PostgreSQL, SQL Server) fire once per statement with transition tables, while SQLite only has row level triggers.</p>',
    '<p>Active databases, which react to events with rules, were studied in the 1990s (the HiPAC and Starburst projects). Today change data capture streams every change from the log to other systems, using tools such as Debezium, instead of triggers.</p>')}
{deep('Temporal tables', '<p>SQL:2011 added system versioned tables, which keep every past version of each row automatically, so you can query the data AS OF a past time. SQL Server and MariaDB support them. In SQLite and PostgreSQL the same effect is built with an AFTER UPDATE trigger that copies the old row to a history table.</p>')}
''', kw=['row level trigger', 'statement level trigger', 'active database', 'change data capture', 'Debezium', 'temporal table'])
K.talk('levels', '''Up the ladder once more. For a beginner, triggers react to changes, generated columns are formulas, and procedures are saved programs. At college
level, know when BEFORE, AFTER and INSTEAD OF triggers fire, and the difference between virtual and stored columns. At masters level, triggers run inside
the same transaction as the statement, so a failing trigger undoes it, and some engines have statement level triggers. At research level, active
databases and change data capture stream every change to other systems. Think of a smoke alarm wired to call the fire station.''')

K.quiz('e', 'A trigger runs', ['When a user clicks it', 'Automatically on INSERT, UPDATE or DELETE', 'Once a day', 'Only on SELECT'], 1, 'By itself.', 'It reacts to data changes.')
K.quiz('e', 'Inside an UPDATE trigger, OLD.price is', ['The new price', 'The price before the change', 'Always NULL', 'An error'], 1, 'Before.', 'OLD is the row before, NEW the row after.')
K.quiz('e', 'A generated column is', ['Typed by the user', 'Computed from other columns', 'A primary key', 'A view'], 1, 'Formula.', 'It is derived from the row.')
K.quiz('e', 'An audit log is best written by', ['A BEFORE trigger that refuses', 'An AFTER trigger', 'A view', 'An index'], 1, 'After the change.', 'Log what really happened.')
K.quiz('m', 'How many times does a row level trigger fire for an UPDATE of 5 rows?', ['Once', '5 times', 'Never', '10 times'], 1, 'Per row.', 'FOR EACH ROW.')
K.quiz('m', 'INSTEAD OF triggers are attached to', ['Indexes', 'Views', 'Columns', 'Databases'], 1, 'Views.', 'They say what a write to a view should do.')
K.quiz('m', 'A STORED generated column', ['Is computed on read', 'Is computed on write and saved', 'Cannot be indexed', 'Can be written directly'], 1, 'Saved.', 'Computed on write.')
K.quiz('m', 'SELECT RAISE(ABORT, \'msg\') in a SQLite trigger', ['Logs a message', 'Stops the statement with an error', 'Commits', 'Retries'], 1, 'Abort.', 'The change is refused.')
K.quiz('m', 'SQL Server runs a stored procedure with', ['CALL', 'EXEC', 'RUN', 'DO'], 1, 'Execute.', 'EXEC proc_name.')
K.quiz('h', 'Why does SQLite have no stored procedures in SQL?', ['It is too old', 'It runs inside the app, which supplies its own code', 'A bug', 'Licence limits'], 1, 'Embedded.', 'The host app registers functions.')
K.quiz('x', 'Streaming every committed change from the log to other systems is called', ['Sharding', 'Change data capture', 'Vacuum', 'Normalization'], 1, 'CDC.', 'Change data capture, for example with Debezium.')

lg = value('shop', 'SELECT count(*) FROM price_log', setup="CREATE TABLE price_log (a, b, c, d); CREATE TRIGGER t AFTER UPDATE OF price ON products WHEN NEW.price <> OLD.price BEGIN INSERT INTO price_log VALUES (OLD.id, OLD.price, NEW.price, 'x'); END; UPDATE products SET price = price + 50 WHERE category = 'Sports';")
K.calc('e', 'An UPDATE raises the price of both Sports products. How many rows does the price log get?', str(lg), 'Once per changed row.',
       ['Two Sports products: Cricket ball and Football.', 'The trigger fires once per row.', eq(f'{lg} log rows')], check=lg)
K.calc('e', 'Football was 850 and rose by 50. What are OLD.price and NEW.price? Give NEW.price.', '900', 'Old plus 50.',
       ['OLD.price = 850.', 'NEW.price = OLD.price + 50.', eq('850 + 50 = 900')], check=900)
ic = value('shop', 'SELECT item_count FROM orders WHERE id = 110', setup="ALTER TABLE orders ADD COLUMN item_count INTEGER NOT NULL DEFAULT 0; UPDATE orders SET item_count = (SELECT COALESCE(SUM(qty), 0) FROM order_items WHERE order_id = orders.id); CREATE TRIGGER a AFTER INSERT ON order_items BEGIN UPDATE orders SET item_count = item_count + NEW.qty WHERE id = NEW.order_id; END; INSERT INTO order_items VALUES (110, 2, 4);")
K.calc('m', 'Order 110 had 1 item. A line with qty 4 is inserted and the trigger adds it. What is item_count now?', str(ic), 'Add qty.',
       ['Before: 1 item (one football).', 'The trigger adds NEW.qty = 4.', eq(f'1 + 4 = {ic}')], check=ic)
K.calc('m', 'A generated total is qty × price. What is it for 12 notebooks at 60?', '720', 'Multiply.',
       ['qty = 12, price = 60.', 'The column multiplies them.', eq('12 × 60 = 720')], check=value('', 'SELECT total FROM l', setup='CREATE TABLE l (qty INTEGER, price INTEGER, total INTEGER GENERATED ALWAYS AS (qty * price)); INSERT INTO l (qty, price) VALUES (12, 60);'))
K.calc('m', 'is_bulk is (qty >= 10). How many of the lines Notebook 12 and Lamp 1 are bulk?', '1', 'Test each.',
       ['12 >= 10 is true, 1.', '1 >= 10 is false, 0.', eq('1 bulk line')], check=1)
K.calc('m', 'A bulk import inserts 50,000 rows into a table with one row level trigger. How many times does it fire?', '50000', 'Once per row.',
       ['Row level triggers fire for each row.', 'There are 50,000 rows.', eq('50,000 times')], check=50000)
K.calc('h', 'Each trigger run adds 0.02 ms. How many milliseconds do the 50,000 runs add?', '1000', 'Multiply.',
       ['50,000 runs.', '0.02 ms each.', eq('50,000 × 0.02 = 1,000 ms, one second')], check=1000, tol=0.001)
K.calc('h', 'A procedure replaces 4 separate statements sent from the app, each with 3 ms of network delay. How many ms of delay are saved?', '9', 'One call instead of four.',
       ['Before: 4 round trips, 12 ms.', 'After: 1 round trip, 3 ms.', eq('12 − 3 = 9 ms')], check=9)

K.must('Triggers', 'CREATE TRIGGER ... BEFORE or AFTER INSERT, UPDATE or DELETE. NEW is the new row, OLD the old one. Fires once per row in SQLite.')
K.must('Uses', 'Audit logs, history tables, stored totals, refusing bad values, INSTEAD OF to make views writable.')
K.must('Generated columns', 'GENERATED ALWAYS AS (expr) VIRTUAL or STORED. Computed, never written by hand.')
K.must('Procedures', 'Server engines store programs: PL/pgSQL, T-SQL, PL/SQL. SQLite uses functions from the host app.')
K.must('Judgement', 'Keep triggers short and documented. Choose database or app logic by who must be guarded and how it will be tested.')

T = K.topic(
    slug='sql-programmable', topic='sql-programmable', step=(8, 'Professional SQL', 'sql-pro', 'Logic inside the database, security, scaling to many machines, and the differences between engines.', 'Advanced'),
    title='Triggers, generated columns and procedures', short='Triggers and procedures', badge='8.1', minutes=40, added='2026-11-23',
    lead='Put logic inside the database: triggers that react to every change, generated columns that compute themselves, and stored procedures in server engines.',
    desc='CREATE TRIGGER, BEFORE, AFTER and INSTEAD OF, NEW and OLD, WHEN and RAISE, audit logs, stored totals, writable views, generated columns VIRTUAL and STORED, stored procedures and functions in PostgreSQL, SQL Server, MySQL and Oracle, database versus application logic.',
    summary='Triggers, generated columns and stored procedures.',
    keywords=['trigger', 'generated column', 'stored procedure', 'audit log', 'INSTEAD OF', 'PL/pgSQL'],
    recap='<p>Triggers react to changes, generated columns compute themselves, and procedures store programs in server engines.</p>')
