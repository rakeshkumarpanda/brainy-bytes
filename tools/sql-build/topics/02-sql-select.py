# Chapter 1.2: SELECT in depth: columns, expressions, aliases, concatenation, DISTINCT, LIMIT and OFFSET, comments,
# quoting. Sources: sqlite.org lang_select.html and lang_expr.html (|| concatenation, string literals in single quotes,
# identifiers in double quotes, DISTINCT treats NULLs as equal), PostgreSQL docs for LIMIT/OFFSET and FETCH FIRST.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('columns', 'Choosing columns and doing sums', f'''
<p>SELECT does more than copy columns. Every item in the SELECT list is an <b>expression</b>: a column, a fixed value, or a little calculation worked out once for every row. A shopkeeper checking "how much stock money sits on each shelf" multiplies price by stock for each product. SQL does it in one line.</p>
{pk('sqselect', c='name, price, stock, price * stock')}
{K.sql('calc', """SELECT name,
       price,
       stock,
       price * stock AS stock_value
FROM products;""", title='A calculated column', notes={4: 'price * stock is worked out for every row. AS gives the new column a name.'})}
{table(['Operator', 'Meaning', 'Example', 'Result'], [
    ['<code>+ - * /</code>', 'add, subtract, multiply, divide', '<code>price * 2</code>', 'double the price'],
    ['<code>%</code>', 'remainder after division', '<code>stock % 10</code>', '40 gives 0, 25 gives 5'],
    ['<code>||</code>', 'join two pieces of text', "<code>name || ' (' || category || ')'</code>", 'Notebook (Stationery)'],
    ['<code>/</code> on whole numbers', 'integer division drops the fraction', '<code>7 / 2</code>', '3, but <code>7 / 2.0</code> gives 3.5']])}
{note('In SQLite and PostgreSQL, dividing two whole numbers gives a whole number. 7 / 2 is 3. Write 7 / 2.0 or CAST(7 AS REAL) / 2 when you want 3.5. MySQL is different: its / always gives a decimal.', 'warn')}
''', kw=['SELECT list', 'expression', 'calculated column', 'arithmetic', 'integer division', 'concatenation', '||'])
K.talk('columns', '''A SELECT list is a list of expressions, and each one is worked out again for every row. It can be a plain column, a fixed value
or a small calculation. A shopkeeper who wants to know how much money is sitting on each shelf multiplies price by stock, and SQL does
that in one line with price times stock. You can add, subtract, multiply, divide and take the remainder, and two vertical bars join pieces
of text together. Watch out for division. In SQLite and PostgreSQL, seven divided by two gives three, because both numbers are whole.
Write two point zero to get three and a half. Think of each row passing a calculator that applies the same formula.''')

K.lesson('alias', 'Aliases, text and quoting', f'''
<p>An <b>alias</b> gives a column or a table a nickname with <code>AS</code>. It makes results readable, and later it saves typing when many tables meet in one query.</p>
{K.sql('alias', """SELECT name AS product,
       'Rs ' || price AS label,
       price * 0.9 AS sale_price
FROM products
LIMIT 4;""", title='Aliases and text', notes={1: 'The column comes back named product instead of name.', 2: "Text in single quotes is a fixed value. || glues it in front of the price.", 3: 'A 10 percent discount, worked out for every row.'})}
{table(['You write', 'It means', 'Example'], [
    ["<code>'Pune'</code>", 'single quotes: a piece of text (a string literal)', "<code>WHERE city = 'Pune'</code>"],
    ['<code>"order"</code>', 'double quotes: a name (an identifier), useful when it clashes with a keyword', '<code>SELECT "order" FROM t</code>'],
    ["<code>'Kabir''s'</code>", 'two single quotes inside text stand for one', "Kabir's"],
    ['<code>-- note</code>', 'a comment to the end of the line', '<code>-- why this query exists</code>'],
    ['<code>/* note */</code>', 'a comment that can span lines', '<code>/* draft */</code>']])}
{note("Use single quotes for text. MySQL also accepts double quotes for text, but in standard SQL, SQLite and PostgreSQL double quotes mean a name. Single quotes work everywhere.", 'tip')}
{K.sql('nofrom', """SELECT 2 + 3 AS answer,
       10 / 4 AS whole_division,
       10 / 4.0 AS real_division,
       'Hello' || ' ' || 'SQL' AS greeting;""", db='', title='SELECT works without a table too', notes={2: 'Both numbers are whole, so the answer is 2.', 3: 'One number has a decimal point, so the answer is 2.5.'})}
{K.lab('l-label', 'e', 'Price labels', 'Show each product <code>name</code> and a column named <code>with_tax</code> holding the price plus 18 percent GST (price times 1.18).', 'SELECT name, price * 1.18 AS with_tax FROM products;', hint='Multiply price by 1.18 and name the column with AS.', why='An expression in the SELECT list is worked out once for each row, and AS names the result column.')}
''', kw=['alias', 'AS', 'string literal', 'single quotes', 'double quotes', 'identifier', 'comment', 'SELECT without FROM'])
K.talk('alias', '''An alias is a nickname. Writing AS after a column gives the result column a friendlier name, and later we will give whole tables short
nicknames too. Text values always go in single quotes, such as the word Pune. Double quotes mean a name, like a column or table name,
and they let you use a name that clashes with a keyword. If your text contains an apostrophe, write two single quotes in a row. Two
dashes start a comment that runs to the end of the line. SELECT even works with no table at all, which makes it a handy calculator.
Think of an alias as the name card on a lunch box, it does not change the food, only how you find it.''')

K.lesson('distinct', 'DISTINCT, LIMIT and OFFSET', f'''
<p>Ask "which cities do our customers live in" and you do not want Pune printed twice. <code>DISTINCT</code> removes repeated rows from the result. <code>LIMIT</code> keeps only the first few rows, and <code>OFFSET</code> skips some rows first, which is how page 2 of search results works.</p>
{K.sql('distinct', """SELECT DISTINCT city
FROM customers;""", title='Every city once', notes={1: 'DISTINCT looks at the whole result row. Two NULL cities count as the same value here.'})}
{K.sql('limit', """SELECT name, price
FROM products
ORDER BY price DESC
LIMIT 3 OFFSET 0;""", title='The three most expensive products', notes={3: 'Sort first, or "the first three" means nothing.', 4: 'OFFSET 3 would give the next page of three.'})}
{fxs(
    fx('Remove repeats', '<code>SELECT DISTINCT col, col FROM t;</code>', 'Repeats are judged on the whole row of chosen columns, not on the first column alone.', key=True),
    fx('Page of results', '<code>... ORDER BY col LIMIT n OFFSET k;</code>', 'Skip k rows, then return n. Page p of size n uses OFFSET (p − 1) × n.', key=True),
    fx('Standard spelling', '<code>OFFSET k ROWS FETCH FIRST n ROWS ONLY</code>', 'The SQL standard form, used by PostgreSQL, Oracle 12c and later, and SQL Server (with ORDER BY). SQL Server also has SELECT TOP n.'))}
{scene('page 2 of a shopping site', '<p>You search "school bag" and see 20 results. You click page 2. The site runs the same query with <code>ORDER BY</code> on relevance, <code>LIMIT 20 OFFSET 20</code>. If the query had no ORDER BY, the database could return rows in any order, and the same bag might appear on both pages while another never shows up.</p>')}
{note('LIMIT without ORDER BY gives "some" rows, not "the first" rows. Always sort before you limit.', 'warn')}
{K.lab('l-cities', 'e', 'Cities without repeats', 'List each <code>category</code> of product once.', 'SELECT DISTINCT category FROM products;', hint='DISTINCT goes right after SELECT.', why='DISTINCT removes duplicate result rows.')}
{K.lab('l-cheap', 'm', 'Two cheapest products', 'Show the <code>name</code> and <code>price</code> of the two cheapest products, cheapest first.', 'SELECT name, price FROM products ORDER BY price LIMIT 2;', hint='Sort by price ascending, then LIMIT 2.', why='ORDER BY price puts the cheapest first, and LIMIT keeps two.', ordered=True)}
''', kw=['DISTINCT', 'LIMIT', 'OFFSET', 'pagination', 'FETCH FIRST', 'TOP', 'duplicates'])
K.talk('distinct', '''Sometimes the same value appears many times, like Pune for several customers. DISTINCT removes repeated rows so each one appears once,
and it judges the whole row of chosen columns. LIMIT keeps only the first few rows, and OFFSET skips some rows before that. This is
exactly how page two of a shopping site works, with limit twenty and offset twenty. One rule matters a lot here. Without ORDER BY, the
database gives rows in any order it likes, so the first three means nothing. Sort first, then limit. Other engines spell it differently,
such as FETCH FIRST in the standard and TOP in SQL Server. Think of a queue, you must line people up before you can say who is first.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>SELECT is like telling a photocopier which columns of a page to copy, with a little calculator for each line.</p>',
    '<p>The SELECT list is evaluated per row after FROM and WHERE. DISTINCT then removes duplicate result rows, ORDER BY sorts, and LIMIT and OFFSET cut the sorted list.</p>',
    '<p>In relational algebra the SELECT list is projection (π). Pure projection removes duplicates, but SQL keeps them unless you write DISTINCT, because SQL works on multisets. DISTINCT costs a sort or a hash table over the result.</p>',
    '<p>Large OFFSET values are slow because the engine still produces and throws away the skipped rows. Production systems use keyset pagination instead: remember the last key seen and ask for <code>WHERE id &gt; last_id ORDER BY id LIMIT 20</code>, which an index answers directly.</p>')}
{deep('Why SELECT * is risky in real programs', '<p>If someone adds a column to the table later, SELECT * suddenly returns more data, which can break code that reads columns by position and sends more data over the network. Naming columns keeps the result stable and lets the engine use a covering index.</p>')}
''', kw=['projection', 'multiset', 'keyset pagination', 'SELECT *'])
K.talk('levels', '''Here is the same idea at four depths. For a child, SELECT is a photocopier that copies only the columns you point at, with a tiny calculator
for each line. At college level, the select list is worked out for each row, then DISTINCT, ORDER BY and LIMIT shape the final list. At
masters level, the select list is projection in relational algebra, and SQL keeps duplicates unless you ask for DISTINCT. At research
and production level, big offsets are slow because skipped rows are still built and thrown away, so real systems remember the last key
they showed. Think of reading a long book by remembering your page number instead of counting pages from the start every time.''')

np_ = value('shop', 'SELECT count(*) FROM products')
ncity = value('shop', 'SELECT count(*) FROM (SELECT DISTINCT city FROM customers)')
ncat = value('shop', 'SELECT count(DISTINCT category) FROM products')
K.quiz('e', 'What does AS do in SELECT price * 2 AS double_price?', ['Filters rows', 'Names the result column', 'Sorts the result', 'Creates a table'], 1, 'Nickname.', 'AS gives an alias.')
K.quiz('e', 'Which quotes mark a piece of text in standard SQL?', ['Double quotes', 'Single quotes', 'Back ticks', 'Square brackets'], 1, 'Pune.', "Text literals use single quotes, such as 'Pune'.")
K.quiz('e', 'What does DISTINCT do?', ['Sorts rows', 'Removes repeated result rows', 'Removes NULL rows', 'Counts rows'], 1, 'Once each.', 'It drops duplicate rows from the result.')
K.quiz('e', 'What does LIMIT 5 do?', ['Returns at most 5 rows', 'Returns rows with id up to 5', 'Skips 5 rows', 'Returns 5 columns'], 0, 'Cap.', 'LIMIT caps the number of rows.')
K.quiz('m', 'In SQLite, what is 7 / 2?', ['3.5', '3', '4', 'An error'], 1, 'Whole numbers.', 'Integer division drops the fraction.')
K.quiz('m', 'How do you join the text a and b in SQLite?', ["'a' + 'b'", "'a' || 'b'", "'a' & 'b'", "'a'.'b'"], 1, 'Two bars.', '|| is the standard concatenation operator.')
K.quiz('m', 'Why add ORDER BY before LIMIT?', ['It is required syntax', 'Without it the rows come in no promised order', 'It makes LIMIT faster', 'LIMIT needs a number'], 1, 'Which first?', 'Only a sort defines which rows are first.')
K.quiz('m', 'Which OFFSET shows page 3 when each page has 10 rows?', ['10', '20', '30', '3'], 1, '(p − 1) × n.', 'Skip pages 1 and 2: 20 rows.')
K.quiz('h', 'SELECT DISTINCT city, name FROM customers removes rows where', ['The city repeats', 'Both city and name repeat together', 'The name repeats', 'Either repeats'], 1, 'Whole row.', 'DISTINCT compares the whole result row.')
K.quiz('h', 'How do you write the text Kabir\'s as a literal?', ["'Kabir's'", "'Kabir''s'", '"Kabir\'s"', "Kabir s"], 1, 'Double it.', 'Two single quotes stand for one inside a literal.')
K.quiz('x', 'Why is keyset pagination faster than a large OFFSET?', ['It caches pages', 'An index jumps straight to rows after the last key', 'It skips ORDER BY', 'It uses DISTINCT'], 1, 'No throwing away.', 'OFFSET still builds and discards the skipped rows.')

K.calc('e', 'What does SELECT 10 / 4 return in SQLite?', '2', 'Both numbers are whole.',
       ['10 and 4 are integers.', 'Integer division drops the fraction.', eq('10 / 4 = 2')], check=value('', 'SELECT 10 / 4'))
K.calc('e', 'What does SELECT 10 / 4.0 return?', '2.5', 'One number has a decimal point.',
       ['4.0 is a real number.', 'So the division keeps the fraction.', eq('10 / 4.0 = 2.5')], check=value('', 'SELECT 10 / 4.0'))
K.calc('e', 'What does SELECT 17 % 5 return?', '2', 'Remainder.',
       ['5 goes into 17 three times.', '3 × 5 = 15.', eq('17 − 15 = 2')], check=value('', 'SELECT 17 % 5'))
K.calc('m', 'How many rows does SELECT DISTINCT city FROM customers return? Remember NULL counts as one value.', str(ncity), 'Pune, Delhi, Chennai, Bhubaneswar and NULL.',
       ['List the cities: Pune, Delhi, Chennai, Pune, Bhubaneswar, NULL, Delhi, Chennai.', 'Keep each once: Pune, Delhi, Chennai, Bhubaneswar, NULL.', eq(f'{ncity} rows')], check=ncity)
K.calc('m', 'How many rows does SELECT DISTINCT category FROM products return?', str(ncat), 'Count the different categories.',
       ['Stationery, Kitchen, Electronics and Sports.', 'Each appears once in the result.', eq(f'{ncat} rows')], check=ncat)
K.calc('m', 'What is the stock_value (price × stock) of the Headphones?', str(value('shop', "SELECT price * stock FROM products WHERE name = 'Headphones'")), 'Price 1499, stock 12.',
       ['Headphones cost 1499.', 'There are 12 in stock.', eq(f'1499 × 12 = {1499 * 12}')], check=value('shop', "SELECT price * stock FROM products WHERE name = 'Headphones'"))
K.calc('h', 'A site shows 25 rows per page. Which OFFSET gives page 4?', '75', '(p − 1) × n.',
       ['Pages 1 to 3 come before page 4.', '3 pages × 25 rows.', eq('OFFSET 75')], check=3 * 25)
K.calc('h', f'products has {np_} rows. How many rows does SELECT name FROM products LIMIT 4 OFFSET 8 return?', str(value('shop', 'SELECT count(*) FROM (SELECT name FROM products LIMIT 4 OFFSET 8)')), 'Only what is left after skipping.',
       [f'Skip 8 of the {np_} rows.', f'{np_ - 8} rows are left.', eq(f'LIMIT 4 can only return {np_ - 8}')], check=value('shop', 'SELECT count(*) FROM (SELECT name FROM products LIMIT 4 OFFSET 8)'))

K.must('Expressions', 'Every SELECT item is an expression worked out per row: columns, literals, arithmetic and || for text.')
K.must('Integer division', 'In SQLite and PostgreSQL 7 / 2 is 3. Use 7 / 2.0 for 3.5.')
K.must('Aliases', 'AS names a result column or a table. Single quotes mean text, double quotes mean a name.')
K.must('DISTINCT', 'Removes duplicate result rows, comparing the whole row. NULLs count as equal here.')
K.must('LIMIT and OFFSET', 'Sort first, then LIMIT n OFFSET k. Page p uses OFFSET (p − 1) × n. Standard form: FETCH FIRST n ROWS ONLY.')

T = K.topic(
    slug='sql-select', topic='sql-select', step=(1, 'Start here', 'sql-start', 'What a database is, tables and keys, what SQL is, and your first queries, filters and sorting.', 'Beginner'),
    title='SELECT in depth: columns, sums, aliases and paging', short='SELECT in depth', badge='1.2', minutes=35, added='2026-11-23',
    lead='Turn SELECT into a calculator, rename columns with aliases, glue text together, remove repeats with DISTINCT and show results one page at a time.',
    desc='The SELECT list as expressions, arithmetic and integer division, concatenation, aliases, quoting rules, comments, SELECT without FROM, DISTINCT, LIMIT, OFFSET and FETCH FIRST.',
    summary='Calculated columns, aliases, text and quoting, DISTINCT, LIMIT and OFFSET paging.',
    keywords=['SELECT', 'alias', 'AS', 'DISTINCT', 'LIMIT', 'OFFSET', 'concatenation', 'integer division'],
    recap='<p>SELECT works out an expression per row, AS names it, DISTINCT removes repeats, and LIMIT with OFFSET pages through sorted results.</p>')
