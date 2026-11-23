# Chapter 7.1: indexes: full scans, B-trees and B+trees, CREATE INDEX, unique, composite (leftmost prefix), covering,
# partial and expression indexes, what stops an index being used, the cost of indexes on writes, clustered tables, other
# index types (hash, GIN, GiST, BRIN, full text).
# Sources: sqlite.org queryplanner.html (how SQLite uses indexes, covering indexes), optoverview.html, partialindex.html
# (since 3.8.0), expridx.html, withoutrowid.html, fileformat2.html (tables and indexes are B-trees), Bayer and McCreight 1972
# "Organization and Maintenance of Large Ordered Indexes", postgresql.org indexes-types.html, MySQL InnoDB clustered index docs.
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

K.lesson('why', 'Why queries slow down, and what an index is', f'''
<p>With 10 products any query is instant. With 10 million, a query that reads every row, a <b>full table scan</b>, can take seconds. An <b>index</b> is a separate, sorted copy of one or more columns, each entry pointing at its row. It works like the index at the back of a textbook: look up a word, jump to the page.</p>
{pk('sqindex')}
{K.sql('plan', """EXPLAIN QUERY PLAN
SELECT name FROM products WHERE price = 850;

CREATE INDEX idx_products_price ON products(price);

EXPLAIN QUERY PLAN
SELECT name FROM products WHERE price = 850;""", title='The same query before and after an index', notes={2: 'SCAN products: read every row.', 4: 'Build the index once. SQLite keeps it up to date from then on.', 7: 'SEARCH products USING INDEX: jump to matching rows.'})}
{table(['Rows', 'Full scan reads', 'Index search reads about'], [
    ['1,000', '1,000 rows', '10 comparisons'],
    ['1,000,000', '1,000,000 rows', '20 comparisons'],
    ['1,000,000,000', '1,000,000,000 rows', '30 comparisons']])}
{note('The numbers in the right column are log₂ of the row count, the steps of a binary search. Real B-tree indexes need even fewer disk reads, because each page holds hundreds of keys.', 'tip')}
''', kw=['index', 'full table scan', 'CREATE INDEX', 'binary search', 'log n', 'EXPLAIN QUERY PLAN', 'slow query'])
K.talk('why', '''With ten products every query is instant, but with ten million, a query that reads every row can take seconds. Reading every row is called a full
table scan. An index fixes this. It is a separate, sorted copy of one or more columns, where each entry points at its row, just like the index at the
back of a textbook. In the animation, watch SQLite scan every product to find a price, then build an index on price and find it again by halving the
search each step. A million rows need only about twenty steps. The EXPLAIN QUERY PLAN lines show SQLite switching from SCAN to SEARCH. Think of
finding a name in a phone book by opening it in the middle, not reading from page one.''')

K.lesson('btree', 'Inside an index: the B-tree', f'''
<p>Almost every relational engine stores indexes as <b>B-trees</b> (Rudolf Bayer and Edward McCreight, 1972), usually the B+tree variant. In SQLite, tables themselves are B-trees too, keyed by rowid.</p>
{steps('How a B+tree finds price 850', [
    'The <b>root page</b> holds a few separator keys, for example 200 and 700, splitting prices into three ranges.',
    '850 is above 700, so follow the third pointer to an <b>internal page</b> for that range.',
    'Repeat until a <b>leaf page</b>, which holds the actual keys in order, each with the rowid of its row.',
    'Read the row by rowid. Leaves are linked in order, so a range such as price BETWEEN 800 AND 1500 walks along the leaves.',
    eq('depth ≈ log_fanout(rows): with 300 keys per page, 3 levels cover 27 million rows')])}
{table(['Property', 'Why it matters'], [
    ['Always balanced', 'every leaf is at the same depth, so every lookup costs the same'],
    ['Wide pages (thousands of bytes)', 'few levels, so few disk reads'],
    ['Sorted leaves linked together', 'fast ranges, ORDER BY and MIN or MAX without sorting'],
    ['Updated on every write', 'inserts may split pages, which costs time']])}
{K.sql('range', """CREATE INDEX idx_products_price ON products(price);
EXPLAIN QUERY PLAN
SELECT name, price FROM products WHERE price BETWEEN 200 AND 900 ORDER BY price;""", title='One index serves a range and the sort', notes={3: 'SEARCH with price>? AND price<?, and no temporary B-tree for ORDER BY, because the leaves are already in price order.'})}
{deep('Why not a binary tree', '<p>A binary tree node holds one key, so a million keys need about 20 levels, each possibly a separate disk read. A B-tree page holds hundreds of keys, so the same million fit in 3 levels. Disks and SSDs read whole pages at a time, so wide nodes waste nothing.</p>')}
''', kw=['B-tree', 'B+tree', 'root page', 'leaf page', 'fanout', 'balanced tree', 'range scan', 'Bayer McCreight'])
K.talk('btree', '''Almost every database stores its indexes as B trees, invented by Rudolf Bayer and Edward McCreight in nineteen seventy two. A B tree is a wide,
balanced tree. The top page holds a few separator keys that split the values into ranges. You follow the right range down, page by page, until you reach
a leaf, which holds the keys in order with a pointer to each row. Because each page holds hundreds of keys, three levels can cover millions of rows. The
leaves are linked in order, so a range or an ORDER BY simply walks along them. Think of a library with signs for floors, then aisles, then shelves.''')

K.lesson('kinds', 'Unique, composite, covering, partial and expression indexes', f'''
<p>One column is only the start. The shape of an index decides which queries it can help.</p>
{table(['Kind', 'Example', 'Helps'], [
    ['Unique', 'CREATE UNIQUE INDEX ... ON customers(email)', 'lookups, and refuses duplicates. UNIQUE and PRIMARY KEY create one for you'],
    ['Composite', 'ON orders(customer_id, order_date)', 'filters on customer_id, or on customer_id and order_date, in that order'],
    ['Covering', 'ON products(category, price, name)', 'queries that need only these columns never touch the table'],
    ['Partial', 'ON products(name) WHERE stock = 0', 'a small index for one common filter'],
    ['Expression', 'ON customers(lower(email))', 'WHERE lower(email) = ...']])}
{K.sql('composite', """CREATE INDEX idx_orders_cust_date ON orders(customer_id, order_date);
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 1 AND order_date > '2025-06-05';
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 1;
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE order_date > '2025-06-05';""", title='The leftmost prefix rule', notes={2: 'Both columns, in index order: SEARCH using both.', 3: 'The first column alone: still a SEARCH.', 4: 'Only the second column: the index is sorted by customer first, so SQLite scans.'})}
{K.sql('covering', """CREATE INDEX idx_cat_price ON products(category, price);
EXPLAIN QUERY PLAN
SELECT category, MAX(price) FROM products GROUP BY category;""", title='A covering index answers from the index alone', notes={3: 'USING COVERING INDEX: every column needed is in the index, so the table is never read.'})}
{K.sql('partial', """CREATE INDEX idx_out ON products(name) WHERE stock = 0;
CREATE INDEX idx_email_lower ON customers(lower(email));
EXPLAIN QUERY PLAN SELECT name FROM products WHERE stock = 0;
EXPLAIN QUERY PLAN SELECT name FROM customers WHERE lower(email) = 'asha@mail.in';""", title='Partial and expression indexes', notes={1: 'Holds only out of stock products: tiny, and still useful.', 4: 'The query must use the same expression, lower(email), to match.'})}
{note('Think of a composite index like a phone book sorted by surname, then first name. You can find every Sharma, or Priya Sharma, but not every Priya.', 'tip')}
{K.lab('l-idx', 'e', 'Index the categories', 'Create an index named <code>idx_cat</code> on <code>products(category)</code>. Then list the <code>name</code> of every index on products using <code>pragma_index_list(\'products\')</code>, ordered by name.',
"""CREATE INDEX idx_cat ON products(category);
SELECT name FROM pragma_index_list('products') ORDER BY name;""", hint="CREATE INDEX idx_cat ON products(category), then SELECT name FROM pragma_index_list('products').", why='Your index is listed. products has no UNIQUE column, so it is the only one.', ordered=True)}
{K.lab('l-comp', 'm', 'Columns of a composite index', 'Create <code>idx_oc</code> on <code>orders(customer_id, order_date)</code>, then show <code>seqno</code> and <code>name</code> from <code>pragma_index_info(\'idx_oc\')</code>.',
"""CREATE INDEX idx_oc ON orders(customer_id, order_date);
SELECT seqno, name FROM pragma_index_info('idx_oc');""", hint="SELECT seqno, name FROM pragma_index_info('idx_oc')", why='seqno 0 is customer_id, the leftmost column, and seqno 1 is order_date.', ordered=True)}
''', kw=['unique index', 'composite index', 'leftmost prefix', 'covering index', 'partial index', 'expression index', 'functional index'])
K.talk('kinds', '''The shape of an index decides which queries it can help. A unique index also refuses duplicates, and SQLite builds one for every UNIQUE and primary
key column. A composite index covers several columns in a fixed order, like a phone book sorted by surname and then first name. It can find all the
Sharmas, or Priya Sharma, but not every Priya, and this is called the leftmost prefix rule. A covering index holds every column a query needs, so the
table is never read. A partial index stores only rows matching a condition, and an expression index stores something like the lower case email. Think
of different indexes at the back of a cookbook, one by dish and one by ingredient.''')

K.lesson('costs', 'When indexes do not help, and what they cost', f'''
<p>An index is not free, and the planner does not always use it.</p>
{table(['Situation', 'Why the index is skipped'], [
    ['A function on the column: WHERE upper(name) = ...', 'the index is sorted by name, not upper(name). Use an expression index'],
    ['Leading wildcard: LIKE \'%box\'', 'sorted order cannot find words by their ending'],
    ['Only a later column of a composite index', 'leftmost prefix rule'],
    ['A tiny table, or a filter matching most rows', 'reading everything is cheaper than jumping around'],
    ['Different types: comparing a TEXT column with a number', 'conversions can stop the index matching']])}
{K.sql('func', """CREATE INDEX idx_name ON products(name);
EXPLAIN QUERY PLAN SELECT * FROM products WHERE name = 'Football';
EXPLAIN QUERY PLAN SELECT * FROM products WHERE upper(name) = 'FOOTBALL';""", title='Wrapping the column in a function hides the index', notes={2: 'SEARCH using idx_name.', 3: 'SCAN: the planner cannot use an index sorted by name for upper(name).'})}
{table(['Cost', 'Details'], [
    ['Slower writes', 'every INSERT, UPDATE of an indexed column and DELETE must update every index too'],
    ['Disk and memory', 'each index is another B-tree, often a big share of the database size'],
    ['Planner work', 'more choices to consider, and occasionally a wrong one'],
    ['Maintenance', 'statistics go stale. ANALYZE refreshes them, PostgreSQL also needs VACUUM']])}
{steps('A sensible indexing routine', [
    'Find the slow or frequent queries from logs or monitoring.',
    'Read their plans with EXPLAIN QUERY PLAN or EXPLAIN ANALYZE.',
    'Index the columns in WHERE, JOIN ... ON and ORDER BY, equality columns first in a composite index.',
    'Check the plan again, then measure. Drop indexes that no query uses.'])}
{K.lab('l-expr', 'h', 'Case insensitive lookups', 'Create an expression index <code>idx_lname</code> on <code>products(lower(name))</code>, then find the <code>id</code> and <code>name</code> of the product whose lower case name is <code>desk lamp</code>.',
"""CREATE INDEX idx_lname ON products(lower(name));
SELECT id, name FROM products WHERE lower(name) = 'desk lamp';""", hint="CREATE INDEX idx_lname ON products(lower(name)), then WHERE lower(name) = 'desk lamp'.", why='The WHERE uses exactly the indexed expression, so SQLite can use idx_lname.')}
''', kw=['index not used', 'sargable', 'leading wildcard', 'write amplification', 'ANALYZE', 'index maintenance', 'selectivity'])
K.talk('costs', '''An index is not free, and it is not always used. Wrap the column in a function, such as upper of name, and the index sorted by name no longer matches.
A search for words ending in box cannot use sorted order either. For a tiny table, or a filter that matches most rows, reading everything is cheaper
than jumping around. On the cost side, every insert, update and delete must also update every index, and each index takes disk space. So index the
columns your important queries filter, join and sort on, check the plan, measure, and drop indexes nobody uses. Think of a shop that labels every shelf
but must relabel them each time stock moves.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>An index is a sorted list with page numbers, so the database can jump instead of reading everything.</p>',
    '<p>B+tree indexes give O(log n) lookups and ordered ranges. Composite indexes follow the leftmost prefix rule, covering indexes avoid table reads, and every index slows writes.</p>',
    '<p>Clustered storage keeps rows in key order: InnoDB and SQL Server clustered indexes, SQLite WITHOUT ROWID tables. Other structures suit other data: hash indexes for equality, GIN for arrays and JSON, GiST and R-trees for geometry, BRIN for huge naturally ordered tables.</p>',
    '<p>Write heavy systems use log structured merge trees (O’Neil et al., 1996) in RocksDB and Cassandra, trading read cost for fast writes. Learned indexes (Kraska et al., SIGMOD 2018) replace B-tree search with a model that predicts a key’s position.</p>')}
{deep('Clustered versus secondary', '<p>In MySQL InnoDB the table is stored inside its primary key B-tree, and every secondary index stores the primary key instead of a row address. A lookup through a secondary index therefore does two B-tree searches. That is one reason short primary keys are preferred there. SQLite ordinary tables are clustered by rowid in the same way.</p>')}
''', kw=['clustered index', 'WITHOUT ROWID', 'hash index', 'GIN', 'GiST', 'BRIN', 'LSM tree', 'learned index'])
K.talk('levels', '''Here is the ladder. For a beginner, an index is a sorted list with page numbers. At college level, B plus tree indexes give fast lookups that grow
with the logarithm of the row count, follow the leftmost prefix rule, and slow down writes. At masters level, some engines store the whole table in key
order as a clustered index, and other index types suit equality, arrays, JSON, maps and huge logs. At research level, write heavy systems use log
structured merge trees, and learned indexes use a model to predict where a key lives. Think of a librarian who remembers roughly where each book sits.''')

K.quiz('e', 'An index is like', ['A backup', 'The index at the back of a book', 'A view', 'A trigger'], 1, 'Look up, jump.', 'A sorted list pointing at rows.')
K.quiz('e', 'Reading every row of a table is a', ['Seek', 'Full table scan', 'Join', 'Commit'], 1, 'Every row.', 'SCAN in the SQLite plan.')
K.quiz('e', 'Which statement builds an index?', ['MAKE INDEX', 'CREATE INDEX', 'ADD INDEX ONLY', 'INDEX TABLE'], 1, 'Create.', 'CREATE INDEX name ON table(columns).')
K.quiz('e', 'Indexes make writes', ['Faster', 'Slower', 'No different', 'Impossible'], 1, 'More to update.', 'Every index must be updated too.')
K.quiz('m', 'An index on (customer_id, order_date) helps WHERE order_date = ... alone', ['Fully', 'Usually not, leftmost prefix', 'Always better than a scan', 'Only for NULLs'], 1, 'Leftmost.', 'The index is sorted by customer_id first.')
K.quiz('m', 'A covering index means', ['It covers all tables', 'It holds every column the query needs', 'It is unique', 'It is partial'], 1, 'No table read.', 'The query is answered from the index.')
K.quiz('m', 'WHERE upper(name) = \'X\' with an index on name', ['Uses the index', 'Usually scans', 'Fails', 'Uses a hash'], 1, 'Function hides it.', 'Use an expression index on upper(name).')
K.quiz('m', 'Which LIKE can use a normal sorted index?', ["LIKE '%box'", "LIKE 'Pen%' (with suitable collation)", "LIKE '%en%'", 'None'], 1, 'Prefix.', 'A fixed prefix matches sorted order.')
K.quiz('m', 'B-trees keep every leaf', ['At random depth', 'At the same depth', 'In memory only', 'Unsorted'], 1, 'Balanced.', 'Every lookup costs the same.')
K.quiz('h', 'A partial index is built with', ['CREATE INDEX ... WHERE condition', 'CREATE PART INDEX', 'PARTITION BY', 'LIMIT'], 0, 'Where.', 'Only rows matching the WHERE are indexed.')
K.quiz('x', 'Which structure trades read speed for very fast writes?', ['B-tree', 'LSM tree', 'Hash index', 'Bitmap'], 1, 'Log structured.', 'LSM trees batch writes into sorted runs.')

import math
K.calc('e', 'About how many binary search steps find a key among 1,000,000 sorted values?', '20', 'log₂.',
       ['Each step halves the range.', '2²⁰ = 1,048,576, just over a million.', eq('about 20 steps')], check=math.ceil(math.log2(1_000_000)))
K.calc('e', 'A full scan of 1,000,000 rows compared with 20 index steps. How many times more comparisons does the scan make?', '50000', 'Divide.',
       ['The scan reads every row.', 'The index needs about 20 steps.', eq('1,000,000 ÷ 20 = 50,000')], check=50000)
K.calc('m', 'A B+tree page holds 300 keys. How many keys can 3 levels address?', '27000000', 'Fanout cubed.',
       ['Each level multiplies by 300.', 'Three levels give 300³.', eq('300 × 300 × 300 = 27,000,000')], check=300 ** 3)
K.calc('m', 'How many binary search steps does the animation need to find 850 among the 10 sorted prices?', '2', 'Halve each time.',
       ['Sorted: 60, 95, 120, 180, 250, 399, 699, 850, 1250, 1499 at positions 0 to 9.', 'Step 1: middle position 4 holds 250, too small, so keep positions 5 to 9.', eq('Step 2: middle position 7 holds 850. Found in 2 steps')], check=2)
nidx = value('shop', "SELECT count(*) FROM pragma_index_list('customers')")
K.calc('m', 'How many indexes does SQLite create by itself on customers (id INTEGER PRIMARY KEY, email UNIQUE)?', str(nidx), 'UNIQUE makes one.',
       ['INTEGER PRIMARY KEY is the rowid itself, no extra index.', 'email UNIQUE gets an automatic index.', eq(f'{nidx} index')], check=nidx)
K.calc('m', 'A table has 4 indexes. One INSERT changes how many B-trees in SQLite?', '5', 'Table plus indexes.',
       ['The table itself is a B-tree.', 'Each of the 4 indexes is another B-tree.', eq('1 + 4 = 5')], check=5)
K.calc('h', 'A query filters 1,000,000 rows down to 900,000. Is an index likely to help? Answer 1 for yes, 0 for no.', '0', 'Selectivity.',
       ['90 percent of rows match.', 'Jumping through an index for most rows costs more than one sequential scan.', eq('0, a scan is better')], check=0)
K.calc('h', 'With 300 keys per page, how many levels does a B+tree need for 50,000 rows?', '2', 'Smallest k with 300^k ≥ rows.',
       ['300¹ = 300, too few.', '300² = 90,000, enough.', eq('2 levels')], check=math.ceil(math.log(50000, 300)))

K.must('Scan versus search', 'Without an index a filter reads every row (SCAN). An index lets the engine jump (SEARCH). Check with EXPLAIN QUERY PLAN.')
K.must('B-trees', 'Balanced, wide, sorted. About log n steps, ranges and ORDER BY come almost free.')
K.must('Index shapes', 'Composite indexes follow the leftmost prefix rule. Covering indexes avoid the table. Partial and expression indexes exist.')
K.must('When not used', 'Functions on the column, leading wildcards, later composite columns only, tiny tables, filters matching most rows.')
K.must('Costs', 'Every index slows writes and takes space. Index what important queries filter, join and sort on, then measure.')

T = K.topic(
    slug='sql-indexes', topic='sql-indexes', step=(7, 'Performance and transactions', 'sql-perf', 'How indexes and query plans make queries fast, and how transactions keep data correct when many people work at once.', 'Advanced'),
    title='Indexes: making queries fast', short='Indexes', badge='7.1', minutes=45, added='2026-11-23',
    lead='See why big tables get slow, how a B-tree index turns a full scan into a quick search, which index shapes help which queries, and what every index costs.',
    desc='Full table scans, CREATE INDEX, B-trees and B+trees, EXPLAIN QUERY PLAN, unique, composite, covering, partial and expression indexes, the leftmost prefix rule, why indexes are skipped, write costs, clustered tables, LSM trees, learned indexes.',
    summary='Full scans, B-tree indexes, index shapes, when they are skipped and what they cost.',
    keywords=['index', 'B-tree', 'composite index', 'covering index', 'EXPLAIN QUERY PLAN', 'performance'],
    recap='<p>An index is a sorted B-tree that turns a scan into a search. Shape it to the query, check the plan, and remember every index slows writes.</p>')
