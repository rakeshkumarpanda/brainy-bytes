# Chapter 5.2: database design in practice: from requirements to entities, attributes and relationships, ER diagrams
# (Chen 1976, crow's foot notation), mapping 1:1, 1:N and M:N to tables, naming conventions, lookup tables versus CHECK,
# audit columns, and a full worked design of a small library system.
# Sources: Chen 1976 "The Entity Relationship Model", sqlite.org lang_createtable.html and foreignkeys.html,
# postgresql.org ddl-constraints.html. Conventions are common practice and are presented as advice, not rules.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

LIB = """CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT UNIQUE, joined_on TEXT NOT NULL);
CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, year INTEGER CHECK (year > 1400));
CREATE TABLE book_authors (book_id INTEGER NOT NULL REFERENCES books(id), author_id INTEGER NOT NULL REFERENCES authors(id), PRIMARY KEY (book_id, author_id));
CREATE TABLE copies (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL REFERENCES books(id), shelf TEXT NOT NULL);
CREATE TABLE loans (id INTEGER PRIMARY KEY, copy_id INTEGER NOT NULL REFERENCES copies(id), member_id INTEGER NOT NULL REFERENCES members(id),
  loaned_on TEXT NOT NULL, due_on TEXT NOT NULL, returned_on TEXT, CHECK (due_on > loaned_on));
INSERT INTO members VALUES (1, 'Asha', '98111', '2025-01-05'), (2, 'Ravi', '97333', '2025-02-11'), (3, 'Meera', NULL, '2025-03-20');
INSERT INTO authors VALUES (1, 'R. K. Narayan'), (2, 'Ruskin Bond'), (3, 'Sudha Murty'), (4, 'Jerry Pinto');
INSERT INTO books VALUES (1, 'Malgudi Days', 1943), (2, 'The Blue Umbrella', 1980), (3, 'Wise and Otherwise', 2002), (4, 'A Book of Bombay', 2003);
INSERT INTO book_authors VALUES (1, 1), (2, 2), (3, 3), (4, 4), (4, 2);
INSERT INTO copies VALUES (1, 1, 'A1'), (2, 1, 'A1'), (3, 2, 'B2'), (4, 3, 'C3'), (5, 4, 'C3');
INSERT INTO loans VALUES (1, 1, 1, '2025-06-01', '2025-06-15', '2025-06-12'), (2, 3, 1, '2025-06-20', '2025-07-04', NULL),
  (3, 4, 2, '2025-06-25', '2025-07-09', NULL), (4, 2, 3, '2025-07-01', '2025-07-15', '2025-07-10');"""

N = len(LIB.split('\n'))

K.lesson('process', 'From a story to tables', f'''
<p>Good schemas start with words, not SQL. Read how the business talks about its work, then turn the <b>nouns</b> into tables and the <b>verbs</b> into relationships.</p>
{scene('the neighbourhood library', '<p>"Members borrow copies of books. A book can have several authors, and an author writes many books. The library may own several copies of a popular book, each on a shelf. A loan records who borrowed which copy, when, when it is due, and when it came back."</p>')}
{steps('Five design steps', [
    '<b>Entities</b>: underline the nouns that have their own facts: member, book, author, copy, loan.',
    '<b>Attributes</b>: list the facts of each: a member has a name and phone, a copy has a shelf.',
    '<b>Relationships</b>: a member borrows copies (through loans), a book has copies, books and authors are many to many.',
    '<b>Keys</b>: give every table a primary key, and turn each relationship into foreign keys or a junction table.',
    '<b>Rules</b>: write NOT NULL, UNIQUE and CHECK for every fact the business promises, such as due date after loan date.'])}
{table(['Word in the story', 'Becomes'], [
    ['member, book, author, copy', 'tables'],
    ['name, phone, title, shelf', 'columns'],
    ['"has several authors" and "writes many books"', 'a junction table book_authors'],
    ['"a copy of a book"', 'copies.book_id references books'],
    ['"who borrowed which copy, when"', 'a loans table with two foreign keys and dates']])}
{note('A loan is an event, and events usually become their own table with a date. Do not squeeze it into members as columns like book1, book2, book3, which breaks 1NF.', 'tip')}
''', kw=['requirements', 'entity', 'attribute', 'relationship', 'nouns and verbs', 'schema design'])
K.talk('process', '''Good database design starts with words, not with SQL. Read how the business describes its work, then the nouns become tables and the verbs become
relationships. Take a neighbourhood library. Members borrow copies of books, a book can have several authors, and the library may own several copies
of one book. So member, book, author, copy and loan become tables. Each gets a primary key, each relationship becomes a foreign key or a junction
table, and every promise the business makes, such as a due date after the loan date, becomes a constraint. A loan is an event, so it gets its own table
with dates. Think of an architect who listens to the family before drawing the house.''')

K.lesson('er', 'ER diagrams and the three kinds of relationship', f'''
<p>An <b>entity relationship diagram</b> (Peter Chen, 1976) draws entities as boxes and relationships as lines. Most tools today use <b>crow’s foot</b> notation: the three pronged end means "many", a bar means "one", and a circle means "optional".</p>
{pk('sqer')}
{table(['Relationship', 'Example', 'Tables'], [
    ['One to one', 'person and passport', 'foreign key with UNIQUE on one side'],
    ['One to many', 'book and its copies', 'foreign key on the many side: copies.book_id'],
    ['Many to many', 'books and authors', 'junction table with two foreign keys and a composite primary key']])}
{K.sql('m2m', LIB + """
SELECT b.title, group_concat(a.name, ' and ') AS authors
FROM books b
JOIN book_authors ba ON ba.book_id = b.id
JOIN authors a ON a.id = ba.author_id
GROUP BY b.id ORDER BY b.title;""", db='', title='The junction table in use', notes={N + 3: 'Two joins pass through book_authors.', N + 1: 'group_concat puts both authors of A Book of Bombay into one cell.'})}
{table(['Optional or required', 'How to say it in SQL'], [
    ['every copy must belong to a book', 'copies.book_id NOT NULL REFERENCES books(id)'],
    ['a member may have no phone', 'phone TEXT, allowing NULL'],
    ['a loan may not be returned yet', 'returned_on TEXT, NULL until it comes back']])}
{K.lab('l-junction', 'm', 'Who wrote what', 'Using the library tables, show each author’s <code>name</code> and the number of books they wrote, as <code>books</code>, for every author.',
"""SELECT a.name, COUNT(ba.book_id) AS books FROM authors a LEFT JOIN book_authors ba ON ba.author_id = a.id GROUP BY a.id;""", db='', setup=LIB, hint='Join authors to book_authors and GROUP BY the author.', why='Ruskin Bond has 2 books because he shares A Book of Bombay with Jerry Pinto in this sample.')}
''', kw=['ER diagram', 'crow foot notation', 'Chen', 'one to one', 'one to many', 'many to many', 'junction table', 'optional relationship'])
K.talk('er', '''An entity relationship diagram draws each entity as a box and each relationship as a line between boxes. Most tools use crow's foot notation,
where a three pronged end means many, a bar means one, and a small circle means optional. There are three kinds of relationship. One to one, like a
person and a passport, uses a foreign key with a unique rule. One to many, like a book and its copies, puts the foreign key on the many side. Many to
many, like books and authors, needs a junction table with two foreign keys. In the animation, pick each kind and watch Pip place the keys and run a
join. Think of a family tree drawn on a chart before anyone writes the names into a register.''')

K.lesson('conventions', 'Habits that keep a schema healthy', f'''
<p>These are widely used conventions, not laws. Pick a style and use it everywhere in one database.</p>
{table(['Habit', 'Example', 'Why'], [
    ['Plural or singular table names, but always the same', 'customers, orders, products', 'nobody has to guess'],
    ['snake_case, no spaces, no reserved words', 'order_date, not "Order Date" or date', 'no quoting needed'],
    ['A surrogate id plus UNIQUE on the natural key', 'id INTEGER PRIMARY KEY, email UNIQUE', 'ids never change, emails can'],
    ['Foreign key named after the table', 'customer_id references customers(id)', 'joins read naturally'],
    ['Created and updated times', 'created_at, updated_at', 'debugging and audits'],
    ['Money as exact numbers', 'price_paise INTEGER or DECIMAL(10,2)', 'no rounding errors']])}
<p>When a column takes one of a few values, you can use a CHECK list or a small <b>lookup table</b>.</p>
{K.sql('lookup', """CREATE TABLE statuses (code TEXT PRIMARY KEY, label TEXT NOT NULL, is_open INTEGER NOT NULL);
INSERT INTO statuses VALUES ('pending', 'Waiting to ship', 1), ('shipped', 'On the way', 1),
  ('delivered', 'Delivered', 0), ('cancelled', 'Cancelled', 0);
SELECT s.label, COUNT(*) AS orders
FROM orders o JOIN statuses s ON s.code = o.status
WHERE s.is_open = 1 GROUP BY s.label;""", title='A lookup table can carry extra facts', notes={1: 'Each status has a label for screens and a flag for open or closed.', 6: 'Queries ask is_open instead of listing statuses by hand.'})}
{table(['CHECK list', 'Lookup table'], [
    ["CHECK (status IN ('pending', 'shipped'))", 'status REFERENCES statuses(code)'],
    ['quick for a short fixed list', 'better when values change or carry their own facts'],
    ['adding a value needs ALTER or a table rebuild in SQLite', 'adding a value is one INSERT']])}
{K.lab('l-lookup', 'm', 'Closed orders by label', 'Create a <code>statuses</code> table with <code>code</code> and <code>is_open</code>: pending 1, shipped 1, delivered 0, cancelled 0. Then show the <code>id</code> of every order whose status is closed.',
"""CREATE TABLE statuses (code TEXT PRIMARY KEY, is_open INTEGER);
INSERT INTO statuses VALUES ('pending', 1), ('shipped', 1), ('delivered', 0), ('cancelled', 0);
SELECT o.id FROM orders o JOIN statuses s ON s.code = o.status WHERE s.is_open = 0;""", hint='Create, insert four rows, then join orders to statuses.', why='Delivered and cancelled orders are the closed ones.')}
''', kw=['naming convention', 'snake_case', 'lookup table', 'enum', 'created_at', 'audit columns', 'surrogate key'])
K.talk('conventions', '''A few habits keep a schema easy to live with. Pick one naming style, such as plural table names in snake case, and use it everywhere. Avoid spaces and
reserved words in names, so nothing needs quoting. Give each table a surrogate id that never changes, and put a unique rule on the natural key, such as
email. Name foreign keys after the table they point to, like customer id. Add created and updated times for debugging. When a column holds one of a few
values, use a CHECK list for a short fixed list, or a small lookup table when values change or carry facts of their own. Think of a well labelled
kitchen where every jar sits in the same place each day.''')

K.lesson('case', 'A worked design: the library', f'''
<p>Here is the whole library schema, built from the story in the first lesson. Read each line and match it to a sentence of the story.</p>
{K.sql('libschema', LIB + """
SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name;""", db='', title='The complete library schema with sample rows', notes={4: 'The junction table for the many to many between books and authors.', 6: 'returned_on stays NULL until the copy comes back, and CHECK keeps the dates sensible.'})}
{K.sql('overdue', LIB + """
SELECT m.name, b.title, l.due_on
FROM loans l
JOIN copies c ON c.id = l.copy_id
JOIN books b ON b.id = c.book_id
JOIN members m ON m.id = l.member_id
WHERE l.returned_on IS NULL AND l.due_on < '2025-07-08';""", db='', title='Which loans are overdue on 8 July 2025', notes={N + 6: 'Not returned, and the due date has passed.'})}
{K.sql('avail', LIB + """
SELECT b.title, COUNT(c.id) AS copies,
       COUNT(c.id) - COUNT(l.id) AS on_shelf
FROM books b
JOIN copies c ON c.book_id = b.id
LEFT JOIN loans l ON l.copy_id = c.id AND l.returned_on IS NULL
GROUP BY b.id ORDER BY b.title;""", db='', title='How many copies of each book are on the shelf', notes={N + 5: 'Only open loans count as out.'})}
{table(['Requirement', 'Where the schema guarantees it'], [
    ['A copy belongs to exactly one book', 'copies.book_id NOT NULL REFERENCES books'],
    ['Two members cannot share a phone', 'members.phone UNIQUE'],
    ['A book is listed once per author', 'PRIMARY KEY (book_id, author_id)'],
    ['A loan is due after it starts', 'CHECK (due_on > loaned_on)']])}
{K.lab('l-loans', 'h', 'Busy readers', 'Using the library tables, show each member’s <code>name</code> and how many loans they have ever made, as <code>loans</code>, including members with none.',
"""SELECT m.name, COUNT(l.id) AS loans FROM members m LEFT JOIN loans l ON l.member_id = m.id GROUP BY m.id;""", db='', setup=LIB, hint='LEFT JOIN members to loans so members with no loans stay, and COUNT(l.id).', why='COUNT(l.id) gives 0 for a member with no loans, while COUNT(*) would give 1.')}
''', kw=['library schema', 'worked design', 'overdue query', 'availability', 'requirements to constraints'])
K.talk('case', '''Here is the whole library schema, built from the story in the first lesson. Members, authors and books each get a table. Book authors is the junction
table for the many to many between books and authors. Copies point at their book, and loans point at a copy and a member, with dates. A loan's
returned date stays NULL until the copy comes back, and a CHECK makes sure the due date is after the loan date. Two queries show the design paying off,
one finds overdue loans and one counts copies still on the shelf. Each requirement in the story is guaranteed by a line of the schema. Think of a
blueprint where every room matches something the family asked for.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Turn nouns into tables and verbs into links. Give everything a key, and write the rules down in the table.</p>',
    '<p>Draw an ER diagram, map each relationship to foreign keys or a junction table, normalize to 3NF, and add constraints for every business rule.</p>',
    '<p>Conceptual, logical and physical models are separate stages: the ER model, the relational schema, then types, indexes and storage. Subtypes (a member who is a student or staff) can map to one table with a type column, one table per subtype, or a shared parent table.</p>',
    '<p>Schema evolution, keeping years of data valid while the design changes, is an active research and tooling area. So is modelling for distributed and document databases, where data is often shaped around the queries rather than the entities.</p>')}
{deep('Modelling inheritance', '<p>Suppose some members are students with a roll number and some are staff with an employee code. Option 1: one members table with nullable roll_no and emp_code plus a kind column. Option 2: separate student_members and staff_members tables. Option 3: a members parent table plus child tables sharing its id. Option 3 keeps NOT NULL rules honest and is the usual relational choice.</p>')}
''', kw=['conceptual model', 'logical model', 'physical model', 'subtype', 'inheritance mapping', 'schema evolution'])
K.talk('levels', '''Here is the ladder. For a beginner, nouns become tables, verbs become links, and rules live in the table. At college level, draw an ER diagram, map
each relationship, normalize to third normal form and add constraints. At masters level, design goes through conceptual, logical and physical models,
and subtypes such as student members and staff members can be mapped in three standard ways. At research level, people study how to change a design
over years without breaking old data, and how to model for document and distributed databases. Think of a town planner who designs roads that can
grow when the town grows.''')

K.quiz('e', 'Nouns in a requirement usually become', ['Columns only', 'Tables', 'Indexes', 'Views'], 1, 'Things.', 'Entities become tables.')
K.quiz('e', 'A many to many relationship needs', ['One foreign key', 'A junction table', 'A view', 'No keys'], 1, 'In between.', 'A junction table holds one row per pair.')
K.quiz('e', 'In one to many, the foreign key goes on', ['The one side', 'The many side', 'Both', 'Neither'], 1, 'Many.', 'Each copy stores its book_id.')
K.quiz('e', 'Who introduced the ER model?', ['Codd', 'Chen', 'Gray', 'Stonebraker'], 1, '1976.', 'Peter Chen in 1976.')
K.quiz('m', 'In crow’s foot notation, a circle means', ['Many', 'One', 'Optional', 'Primary key'], 2, 'Zero allowed.', 'A circle marks an optional side.')
K.quiz('m', 'One to one is usually built with', ['A junction table', 'A foreign key plus UNIQUE', 'Two primary keys', 'A CHECK'], 1, 'Unique link.', 'UNIQUE stops two rows pointing at the same parent.')
K.quiz('m', 'What is wrong with columns book1, book2, book3 in members?', ['Too slow', 'It breaks 1NF and limits loans', 'Names too long', 'SQLite forbids it'], 1, 'Repeating group.', 'A repeating group belongs in its own table.')
K.quiz('m', 'A lookup table beats a CHECK list when', ['The list never changes', 'Values change or carry extra facts', 'There are two values', 'Never'], 1, 'Changing lists.', 'Adding a value is one INSERT.')
K.quiz('m', 'A loan not yet returned should have returned_on', ['0', 'An empty string', 'NULL', 'The due date'], 2, 'Unknown yet.', 'NULL means it has not happened.')
K.quiz('h', 'The junction table book_authors should have which primary key?', ['book_id', 'author_id', '(book_id, author_id)', 'none'], 2, 'Pair.', 'Each pair once.')
K.quiz('x', 'Mapping subtypes with a parent table plus child tables sharing its id mainly helps', ['Speed', 'Keeping NOT NULL rules honest per subtype', 'Fewer tables', 'Avoiding joins'], 1, 'Honest nulls.', 'Each child table can require its own columns.')

def L(sql):
    return value('', sql, setup=LIB)
K.calc('e', 'How many tables does the library schema have?', str(L("SELECT count(*) FROM sqlite_schema WHERE type = 'table'")), 'Count them.',
       ['members, authors, books.', 'book_authors, copies, loans.', eq('6 tables')], check=L("SELECT count(*) FROM sqlite_schema WHERE type = 'table'"))
K.calc('e', 'How many copies of Malgudi Days does the library own?', str(L('SELECT count(*) FROM copies WHERE book_id = 1')), 'copies with book_id 1.',
       ['Look at copies.', 'Copies 1 and 2 have book_id 1.', eq('2 copies')], check=L('SELECT count(*) FROM copies WHERE book_id = 1'))
K.calc('m', 'How many loans are still open (not returned)?', str(L('SELECT count(*) FROM loans WHERE returned_on IS NULL')), 'returned_on IS NULL.',
       ['Loan 2 and loan 3 have no return date.', 'Loans 1 and 4 came back.', eq('2 open loans')], check=L('SELECT count(*) FROM loans WHERE returned_on IS NULL'))
K.calc('m', 'How many copies are on the shelf right now?', str(L('SELECT count(*) FROM copies WHERE id NOT IN (SELECT copy_id FROM loans WHERE returned_on IS NULL)')), 'All copies minus open loans.',
       ['There are 5 copies.', '2 are out on open loans.', eq('5 − 2 = 3')], check=L('SELECT count(*) FROM copies WHERE id NOT IN (SELECT copy_id FROM loans WHERE returned_on IS NULL)'))
K.calc('m', 'How many rows are in book_authors?', str(L('SELECT count(*) FROM book_authors')), 'One per pair.',
       ['Books 1, 2 and 3 have one author each.', 'Book 4 has two authors.', eq('3 + 2 = 5 rows')], check=L('SELECT count(*) FROM book_authors'))
K.calc('m', 'A school has 400 students and 12 clubs. If every student joins exactly 2 clubs, how many rows does the membership junction table hold?', '800', 'One row per membership.',
       ['Each student has 2 rows.', 'There are 400 students.', eq('400 × 2 = 800')], check=800)
K.calc('h', 'Loan 3 was due on 2025-07-09. On 2025-07-15, how many days late is it?', str(value('', "SELECT CAST(julianday('2025-07-15') - julianday('2025-07-09') AS INTEGER)")), 'Subtract the dates.',
       ['julianday turns each date into a day number.', 'Subtract the due date from today.', eq('15 − 9 = 6 days')], check=value('', "SELECT CAST(julianday('2025-07-15') - julianday('2025-07-09') AS INTEGER)"))
K.calc('h', 'The fine is 2 rupees per late day. What does loan 3 owe on 2025-07-15?', '12', 'Days times rate.',
       ['It is 6 days late.', 'Each day costs 2 rupees.', eq('6 × 2 = 12 rupees')], check=12)

K.must('Process', 'Story first: nouns to tables, facts to columns, verbs to relationships, then keys and rules.')
K.must('Relationships', 'One to one: foreign key plus UNIQUE. One to many: foreign key on the many side. Many to many: junction table.')
K.must('ER diagrams', 'Boxes and lines. Crow’s foot: three prongs many, bar one, circle optional.')
K.must('Conventions', 'One naming style, surrogate ids with UNIQUE natural keys, foreign keys named after tables, exact money.')
K.must('Rules in the schema', 'Every business promise becomes NOT NULL, UNIQUE, CHECK or a foreign key.')

T = K.topic(
    slug='sql-design', topic='sql-design', step=(5, 'Designing databases', 'sql-design', 'Normalize tables and design a schema from real requirements.', 'Intermediate'),
    title='Database design in practice', short='Design in practice', badge='5.2', minutes=40, added='2026-11-23',
    lead='Turn a plain story into a schema: find entities and relationships, draw an ER diagram, map each relationship to keys, follow healthy conventions and build a full library database.',
    desc='Requirements to entities, attributes and relationships, ER diagrams and crow foot notation, one to one, one to many and many to many mapping, junction tables, naming conventions, lookup tables, a full library schema with queries, subtypes.',
    summary='From requirements to a schema, ER diagrams, relationship mapping and a full library design.',
    keywords=['database design', 'ER diagram', 'junction table', 'crow foot', 'lookup table', 'schema'],
    recap='<p>Start from the story, map each relationship to keys, write every rule into the schema, and keep one consistent style.</p>')
