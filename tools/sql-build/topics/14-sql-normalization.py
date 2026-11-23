# Chapter 5.1: normalization: anomalies, functional dependencies, 1NF, 2NF, 3NF, BCNF, a look at 4NF and 5NF,
# lossless decomposition, denormalization and when it is worth it.
# Sources: Codd 1970 (relational model, first normal form), Codd 1971 "Further Normalization of the Data Base Relational
# Model" (2NF, 3NF), Codd 1974 (Boyce Codd normal form), Fagin 1977 (4NF, multivalued dependencies), Fagin 1979 (5NF,
# join dependencies). Standard textbook definitions as in Silberschatz, Korth and Sudarshan, Database System Concepts.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

SHEET = """CREATE TABLE sheet (student_id INTEGER, student_name TEXT, course TEXT, title TEXT, teacher TEXT, room TEXT, grade TEXT);
INSERT INTO sheet VALUES
 (1, 'Asha', 'C1', 'Databases', 'Rao', 'R12', 'A'),
 (1, 'Asha', 'C2', 'Networks', 'Iyer', 'R7', 'B'),
 (2, 'Ravi', 'C1', 'Databases', 'Rao', 'R12', 'B'),
 (3, 'Meera', 'C3', 'Security', 'Rao', 'R12', 'A');"""

K.lesson('anomaly', 'Why repeated data hurts', f'''
<p>Chapter 3.1 showed the problem: when one fact is written in many rows, the copies can drift apart. <b>Normalization</b> is the step by step method for splitting tables so that each fact is stored exactly once. It was set out by E. F. Codd between 1970 and 1974.</p>
{K.sql('sheet', SHEET + """
SELECT * FROM sheet;""", db='', title='The teacher’s enrolment sheet', notes={3: 'Asha’s name is stored in two rows.', 5: 'Rao’s room R12 is stored in three rows.'})}
{K.sql('drift', SHEET + """
UPDATE sheet SET room = 'R15' WHERE course = 'C1' AND student_id = 1;
SELECT DISTINCT teacher, room FROM sheet WHERE teacher = 'Rao';""", db='', title='An update anomaly in action', notes={7: 'Someone fixes Rao’s room in only one row.', 8: 'Now the sheet claims Rao sits in two rooms at once.'})}
{table(['Anomaly', 'In the sheet'], [
    ['Update', 'Rao moves room, and every row with Rao must change, or the data contradicts itself'],
    ['Insert', 'A new course with no students yet cannot be recorded, because every row needs a student'],
    ['Delete', 'If Meera drops Security, the only row saying Security exists disappears too']])}
{note('Normalization is about the meaning of the data, not about saving disk space. The space saving is a side effect.', 'tip')}
{K.lab('l-drift', 'e', 'Find the contradiction', 'The <code>sheet</code> table has been edited badly. Show each <code>teacher</code> that appears with more than one room.',
"""SELECT teacher FROM sheet GROUP BY teacher HAVING COUNT(DISTINCT room) > 1;""", db='', setup=SHEET + "\nUPDATE sheet SET room = 'R15' WHERE course = 'C1' AND student_id = 1;", hint='GROUP BY teacher, then HAVING COUNT(DISTINCT room) > 1.', why='A teacher with two different rooms is exactly the drift that normalization prevents.')}
''', kw=['normalization', 'update anomaly', 'insert anomaly', 'delete anomaly', 'redundancy', 'Codd'])
K.talk('anomaly', '''Normalization is the method for splitting tables so that every fact is stored once. Look at the teacher's enrolment sheet. Asha's name is stored
twice, and teacher Rao's room is stored three times. If Rao moves and someone fixes only one row, the sheet now says Rao sits in two rooms at once.
That is an update anomaly. There are two more. A new course with no students cannot be recorded at all, and if the only student of a course leaves,
the course disappears with her row. Normalization fixes all three by giving each kind of fact its own table. Think of a school that keeps one
master list of teachers, instead of writing the staff room on every class register.''')

K.lesson('fd', 'Functional dependencies: what decides what', f'''
<p>A <b>functional dependency</b> X → Y means: once you know X, there is only one possible Y. Knowing a roll number tells you the student’s name, so <code>student_id → student_name</code>. Knowing a teacher tells you their room, so <code>teacher → room</code>.</p>
{table(['Dependency in the sheet', 'Read it as'], [
    ['student_id → student_name', 'a roll number decides the name'],
    ['course → title, teacher', 'a course code decides its title and teacher'],
    ['teacher → room', 'a teacher decides the room'],
    ['(student_id, course) → grade', 'a student and a course together decide the grade']])}
<p>The <b>key</b> of the sheet is <code>(student_id, course)</code>, because together they decide every other column. The trouble comes from columns that depend on only <b>part</b> of the key, or on a column that is <b>not</b> a key.</p>
{K.sql('fdcheck', SHEET + """
SELECT teacher, COUNT(DISTINCT room) AS rooms
FROM sheet GROUP BY teacher;""", db='', title='Testing teacher → room on the data', notes={7: 'If any teacher had 2 or more rooms, the dependency would not hold in this data.'})}
{steps('How to spot a dependency', [
    'Ask the business, not only the data: can one teacher ever have two rooms.',
    'Check the data: GROUP BY the left side and count distinct values of the right side.',
    'A count above 1 means the dependency does not hold, or the data is already broken.',
    eq('X → Y holds when COUNT(DISTINCT Y) = 1 for every X')])}
{K.lab('l-fd', 'm', 'Does course decide title', 'Show each <code>course</code> with the number of distinct titles it has, as <code>titles</code>.',
"""SELECT course, COUNT(DISTINCT title) AS titles FROM sheet GROUP BY course;""", db='', setup=SHEET, hint='GROUP BY course and count distinct title.', why='Every course has exactly one title, so course → title holds here.')}
''', kw=['functional dependency', 'determinant', 'candidate key', 'partial dependency', 'transitive dependency'])
K.talk('fd', '''A functional dependency says that once you know one thing, another thing is decided. Knowing a roll number tells you the student's name, and knowing
a teacher tells you their room. We write this with an arrow, roll number arrow name. The key of the enrolment sheet is the pair of student and course,
because together they decide every other column. Problems appear when a column depends on only part of the key, like the name depending on the student
alone, or on a column that is not a key at all, like the room depending on the teacher. You can test a dependency by grouping on the left side and
counting distinct values on the right side. Think of how a pin code decides the post office.''')

K.lesson('forms', '1NF, 2NF, 3NF and BCNF', f'''
<p>Each <b>normal form</b> removes one kind of bad dependency. Each one includes the rules of the forms before it.</p>
{pk('sqnorm')}
{table(['Form', 'Rule', 'Fix in the sheet'], [
    ['1NF', 'every cell holds one value, no lists or repeating groups', 'phones "98111, 98222" become one row per phone'],
    ['2NF', 'no column depends on only part of the key', 'student_name moves to students, course details to courses'],
    ['3NF', 'no column depends on another non key column', 'room moves to teachers, because teacher → room'],
    ['BCNF', 'every determinant is a candidate key', 'stricter 3NF, rarely different in practice']])}
{K.sql('split', SHEET + """
CREATE TABLE students AS SELECT DISTINCT student_id, student_name FROM sheet;
CREATE TABLE courses AS SELECT DISTINCT course, title, teacher FROM sheet;
CREATE TABLE teachers AS SELECT DISTINCT teacher, room FROM sheet;
CREATE TABLE enrolments AS SELECT student_id, course, grade FROM sheet;
SELECT * FROM teachers;""", db='', title='Splitting the sheet into 3NF tables', notes={7: 'One row per student.', 9: 'Rao’s room is now stored once.', 10: 'What remains depends on the whole key.'})}
{K.sql('rejoin', SHEET + """
CREATE TABLE students AS SELECT DISTINCT student_id, student_name FROM sheet;
CREATE TABLE courses AS SELECT DISTINCT course, title, teacher FROM sheet;
CREATE TABLE teachers AS SELECT DISTINCT teacher, room FROM sheet;
CREATE TABLE enrolments AS SELECT student_id, course, grade FROM sheet;
SELECT COUNT(*) AS rows_back FROM enrolments
JOIN students USING (student_id) JOIN courses USING (course) JOIN teachers USING (teacher);""", db='', title='Lossless: the join gives back every row', notes={11: 'The original sheet had 4 rows, and the join rebuilds all 4.'})}
{note('A memory line used by students: every non key column must depend on the key (1NF), the whole key (2NF), and nothing but the key (3NF).', 'tip')}
{K.lab('l-split', 'm', 'Pull out the students', 'From <code>sheet</code>, create a table <code>students</code> with one row per <code>student_id</code> and <code>student_name</code>. Then show every row of it.',
"""CREATE TABLE students AS SELECT DISTINCT student_id, student_name FROM sheet;
SELECT * FROM students;""", db='', setup=SHEET, hint='CREATE TABLE students AS SELECT DISTINCT ...', why='DISTINCT keeps one row for Asha even though she appears twice in the sheet.')}
''', kw=['1NF', '2NF', '3NF', 'BCNF', 'normal forms', 'atomic values', 'lossless decomposition'])
K.talk('forms', '''Each normal form removes one kind of bad dependency. First normal form says every cell holds one value, so a list of phone numbers becomes one row
per phone. Second normal form says no column may depend on only part of the key, so the student's name moves to a students table. Third normal form
says no column may depend on another column that is not a key, so the room moves to a teachers table. Boyce Codd normal form is a slightly stricter
third form. In the animation, choose how far to go and watch the sheet split, and at the end a join rebuilds the original rows, so nothing is lost.
A popular memory line says every column depends on the key, the whole key, and nothing but the key.''')

K.lesson('denorm', 'Higher forms and denormalization', f'''
<p>Most business databases stop at 3NF or BCNF. Two higher forms exist for rarer cases.</p>
{table(['Form', 'Problem it removes', 'Example'], [
    ['4NF (Fagin 1977)', 'two independent lists stored in one table', 'a teacher’s subjects and languages in one table make every combination appear'],
    ['5NF (Fagin 1979)', 'a table that can only be rebuilt from three or more pieces', 'supplier, part and project rules that hold only in combination']])}
<p><b>Denormalization</b> means deliberately storing a copy of data to make reading faster, accepting the work of keeping the copies in step. It is a decision you make after normalizing, not instead of it.</p>
{K.sql('denorm', """ALTER TABLE orders ADD COLUMN item_count INTEGER DEFAULT 0;
UPDATE orders SET item_count = (SELECT SUM(qty) FROM order_items WHERE order_id = orders.id);
SELECT id, status, item_count FROM orders LIMIT 4;""", title='A stored total: faster to read, more to maintain', notes={1: 'A copy of information that already lives in order_items.', 2: 'Every later change to order_items must also update this column, often with a trigger.'})}
{table(['Normalize when', 'Denormalize when'], [
    ['data is written and changed often (OLTP apps)', 'data is mostly read, such as reports (OLAP)'],
    ['correctness matters most', 'a measured query is too slow even with good indexes'],
    ['you are not sure yet', 'you can keep copies in step with triggers or batch jobs']])}
{scene('the star schema of a sales warehouse', '<p>A supermarket’s reporting database keeps one big fact table of sales and small dimension tables for date, store and product. The product table repeats the category and brand names in every row, which breaks 3NF on purpose. Reports become simple joins of one fact table to a few dimensions, and nobody updates these rows during the day, so the copies cannot drift.</p>')}
{K.lab('l-count', 'h', 'Store the item count', 'Add a column <code>item_count INTEGER</code> to <code>orders</code>, fill it with the total <code>qty</code> of each order’s lines, and show <code>id</code> and <code>item_count</code> of orders with more than 5 items.',
"""ALTER TABLE orders ADD COLUMN item_count INTEGER;
UPDATE orders SET item_count = (SELECT SUM(qty) FROM order_items WHERE order_id = orders.id);
SELECT id, item_count FROM orders WHERE item_count > 5;""", hint='ALTER TABLE, then UPDATE with a correlated subquery, then SELECT.', why='Orders 101 (7 items) and 104 (12 items) have more than 5.')}
''', kw=['4NF', '5NF', 'multivalued dependency', 'denormalization', 'star schema', 'OLTP', 'OLAP'])
K.talk('denorm', '''Most business databases stop at third normal form. Fourth and fifth normal forms exist for rarer cases, such as two independent lists squeezed
into one table. Denormalization is the opposite move, made on purpose. You store a copy of some data, such as an item count on each order, so that
reading is faster, and you accept the extra work of keeping the copy correct. Do it only after normalizing, and only when a measured query is too
slow even with good indexes. Reporting databases use it a lot, because their data is loaded in batches and rarely edited. Think of a shop that keeps
a running total on the till instead of adding every receipt again.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Store each fact once. If you would have to fix the same thing in two places, split the table.</p>',
    '<p>Find the key and the functional dependencies, then remove partial dependencies (2NF) and transitive dependencies (3NF). Check that a join rebuilds the original rows.</p>',
    '<p>A decomposition is lossless when the common columns form a key of at least one part. Armstrong’s axioms (reflexivity, augmentation, transitivity) derive every dependency that follows from a given set. 3NF can always be reached while keeping all dependencies checkable, BCNF sometimes cannot.</p>',
    '<p>Research looks at discovering dependencies automatically from data (algorithms such as TANE), at normal forms for nested and JSON data, and at schema design for distributed systems, where joins across machines are expensive and some redundancy is often the right trade.</p>')}
{deep('Armstrong’s axioms', '<p>From a set of dependencies you can derive others: reflexivity (if Y is part of X, then X → Y), augmentation (if X → Y, then XZ → YZ) and transitivity (if X → Y and Y → Z, then X → Z). From course → teacher and teacher → room, transitivity gives course → room, the chain that 3NF removes.</p>')}
''', kw=['Armstrong axioms', 'lossless join', 'dependency preservation', 'closure', 'dependency discovery'])
K.talk('levels', '''Let us climb the ladder. For a beginner, store each fact once, and if you would have to fix something in two places, split the table. At college level,
find the key and the dependencies, remove partial ones for second normal form and transitive ones for third, and check that a join rebuilds the rows.
At masters level, a split is lossless when the shared columns form a key of one part, and Armstrong's axioms derive every dependency that follows
from the ones you know. At research level, algorithms discover dependencies from data automatically. Think of a detective who works out who is related
to whom from a family album.''')

K.quiz('e', 'Normalization mainly aims to', ['Make queries longer', 'Store each fact once', 'Remove all NULLs', 'Add indexes'], 1, 'Once.', 'It removes harmful repetition.')
K.quiz('e', '1NF requires', ['One table only', 'One value per cell', 'No NULLs', 'A surrogate key'], 1, 'Atomic.', 'No lists or repeating groups in a cell.')
K.quiz('e', 'Changing a fact in one row but not its copies is', ['An insert anomaly', 'An update anomaly', 'A delete anomaly', 'A join'], 1, 'Update.', 'The copies now disagree.')
K.quiz('e', 'student_id → student_name means', ['The name decides the id', 'The id decides the name', 'They are equal', 'Both are keys'], 1, 'Left decides right.', 'Knowing the id gives exactly one name.')
K.quiz('m', '2NF removes dependencies on', ['The whole key', 'Part of a composite key', 'NULL', 'Foreign keys'], 1, 'Partial.', 'A partial dependency breaks 2NF.')
K.quiz('m', 'course → teacher → room breaks', ['1NF', '2NF', '3NF only', 'Nothing'], 2, 'Transitive.', 'A non key column deciding another non key column breaks 3NF.')
K.quiz('m', 'A decomposition is lossless when', ['It has fewer rows', 'A join rebuilds exactly the original rows', 'It uses views', 'It has no keys'], 1, 'Nothing lost.', 'No missing and no extra rows after the join.')
K.quiz('m', 'Denormalization is chosen to', ['Fix anomalies', 'Make reading faster', 'Save disk', 'Remove keys'], 1, 'Reads.', 'Copies trade write effort for faster reads.')
K.quiz('m', 'Who introduced 2NF and 3NF?', ['Chen', 'Codd', 'Fagin', 'Gray'], 1, '1971.', 'Codd, in 1971.')
K.quiz('h', 'BCNF requires every determinant to be', ['A foreign key', 'A candidate key', 'NULL', 'Indexed'], 1, 'Determinant.', 'Anything that decides another column must be a candidate key.')
K.quiz('x', 'From A → B and B → C, which axiom gives A → C?', ['Reflexivity', 'Augmentation', 'Transitivity', 'Union'], 2, 'Chain.', 'Transitivity.')

K.calc('e', 'In the sheet, how many times is Rao’s room stored before normalizing?', str(value('', "SELECT count(*) FROM sheet WHERE teacher = 'Rao'", setup=SHEET)), 'Count Rao rows.',
       ['Rao teaches C1 and C3.', 'C1 has 2 enrolments and C3 has 1.', eq('3 copies')], check=value('', "SELECT count(*) FROM sheet WHERE teacher = 'Rao'", setup=SHEET))
K.calc('e', 'And after moving rooms to a teachers table?', '1', 'One row per teacher.',
       ['teachers has one row per teacher.', 'Rao has one row there.', eq('1 copy')], check=value('', "SELECT count(*) FROM (SELECT DISTINCT teacher, room FROM sheet) WHERE teacher = 'Rao'", setup=SHEET))
nst = value('', 'SELECT count(*) FROM (SELECT DISTINCT student_id, student_name FROM sheet)', setup=SHEET)
K.calc('m', 'How many rows does the students table get from the sheet?', str(nst), 'Distinct students.',
       ['The sheet has 4 rows.', 'Asha appears twice.', eq(f'4 − 1 = {nst}')], check=nst)
ncells = 4 * 7
n3 = value('', 'SELECT (SELECT count(*) FROM (SELECT DISTINCT student_id, student_name FROM sheet)) * 2 + (SELECT count(*) FROM (SELECT DISTINCT course, title, teacher FROM sheet)) * 3 + (SELECT count(*) FROM (SELECT DISTINCT teacher, room FROM sheet)) * 2 + (SELECT count(*) FROM sheet) * 3', setup=SHEET)
K.calc('m', 'The sheet has 4 rows of 7 columns. How many cells do the four 3NF tables hold in total?', str(n3), 'Rows × columns for each table.',
       ['students 3 × 2 = 6, courses 3 × 3 = 9.', 'teachers 2 × 2 = 4, enrolments 4 × 3 = 12.', eq(f'6 + 9 + 4 + 12 = {n3}, compared with {ncells}')], check=n3)
K.calc('m', 'A composite key (student_id, course) has 3 students and 3 courses. At most how many enrolment rows can exist?', '9', 'Every pair once.',
       ['Each pair is unique.', 'Pairs = students × courses.', eq('3 × 3 = 9')], check=9)
K.calc('m', 'A teacher teaches 3 subjects and speaks 2 languages, stored in one table (teacher, subject, language). How many rows must it hold to avoid false gaps?', '6', 'Every combination, the 4NF problem.',
       ['The two lists are independent.', 'Each subject is paired with each language.', eq('3 × 2 = 6 rows, against 3 + 2 = 5 in two separate tables')], check=6)
ic = value('shop', 'SELECT SUM(qty) FROM order_items WHERE order_id = 104')
K.calc('h', 'What is the stored item_count of order 104?', str(ic), 'Sum of its quantities.',
       ['Order 104 has lines with qty 2 and 10.', 'item_count is their sum.', eq(f'2 + 10 = {ic}')], check=ic)
K.calc('h', 'After the 3NF split, how many rows does the rebuilding join return?', str(value('', 'SELECT count(*) FROM sheet', setup=SHEET)), 'Lossless.',
       ['Each enrolment matches one student, one course and one teacher.', 'There are 4 enrolments.', eq('4 rows, the same as the sheet')], check=value('', 'SELECT count(*) FROM sheet', setup=SHEET))

K.must('Anomalies', 'Repeated facts cause update, insert and delete anomalies. Normalization stores each fact once.')
K.must('Dependencies', 'X → Y means X decides Y. The key decides every column.')
K.must('1NF, 2NF, 3NF', 'One value per cell, no dependency on part of the key, no dependency on a non key column.')
K.must('Lossless', 'A good split can be joined back into exactly the original rows.')
K.must('Denormalize on purpose', 'Store copies only for measured read speed, and keep them in step.')

T = K.topic(
    slug='sql-normalization', topic='sql-normalization', step=(5, 'Designing databases', 'sql-design', 'Normalize tables and design a schema from real requirements.', 'Intermediate'),
    title='Normalization: storing each fact once', short='Normalization', badge='5.1', minutes=40, added='2026-11-23',
    lead='Find the anomalies in a messy table, read functional dependencies, split tables through 1NF, 2NF, 3NF and BCNF, and know when to denormalize on purpose.',
    desc='Update, insert and delete anomalies, functional dependencies, keys, 1NF, 2NF, 3NF, BCNF, 4NF and 5NF, lossless decomposition, denormalization, star schema, Armstrong axioms.',
    summary='Anomalies, functional dependencies, normal forms and denormalization.',
    keywords=['normalization', '1NF', '2NF', '3NF', 'BCNF', 'functional dependency', 'denormalization'],
    recap='<p>Each fact lives in one place: 1NF for atomic cells, 2NF for the whole key, 3NF for nothing but the key, and denormalize only on purpose.</p>')
