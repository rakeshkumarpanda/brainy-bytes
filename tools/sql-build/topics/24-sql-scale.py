# Chapter 8.3: databases at scale: vertical and horizontal scaling, partitioning (range, list, hash), replication (primary
# and replicas, synchronous and asynchronous, replication lag), sharding and shard keys, the CAP theorem, OLTP versus OLAP,
# row and column storage, data warehouses and star schemas, and where NoSQL and NewSQL systems fit.
# Sources: postgresql.org ddl-partitioning.html (declarative partitioning since 10, partition pruning), high-availability.html
# (streaming replication), MySQL replication docs, Brewer 2000 (CAP conjecture), Gilbert and Lynch 2002 (CAP proof),
# Stonebraker et al. 2005 "C-Store: A Column-oriented DBMS", Kimball and Ross "The Data Warehouse Toolkit" (star schema),
# Corbett et al. 2012 "Spanner".
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

SALES = """CREATE TABLE sales_2024 (id INTEGER, sold_on TEXT CHECK (sold_on LIKE '2024-%'), amount INTEGER);
CREATE TABLE sales_2025 (id INTEGER, sold_on TEXT CHECK (sold_on LIKE '2025-%'), amount INTEGER);
INSERT INTO sales_2024 VALUES (1, '2024-11-02', 500), (2, '2024-12-15', 700);
INSERT INTO sales_2025 VALUES (3, '2025-01-09', 300), (4, '2025-03-21', 900), (5, '2025-06-30', 400);
CREATE VIEW sales AS SELECT * FROM sales_2024 UNION ALL SELECT * FROM sales_2025;"""

K.lesson('grow', 'When one server is not enough', f'''
<p>A database on one machine can serve a surprising amount: SQLite runs countless phone apps, and one well tuned PostgreSQL server can handle thousands of queries a second. When it is not enough, there are two directions.</p>
{table(['Direction', 'What it means', 'Limits'], [
    ['Scale up (vertical)', 'a bigger machine: more CPU, memory, faster disks', 'one machine has a ceiling, and it is a single point of failure'],
    ['Scale out (horizontal)', 'more machines sharing the work', 'harder: data must be copied or split, and kept consistent']])}
{steps('The usual order of fixes', [
    'Fix the queries and indexes first (chapters 7.1 and 7.2). It is the cheapest win.',
    'Add caching for repeated reads, for example Redis in front of the database.',
    'Add read replicas for read heavy traffic.',
    'Partition very large tables inside one server.',
    'Shard across servers only when one primary cannot take the writes.'])}
{note('Most apps never need sharding. Each step above adds moving parts, so take the next step only when measurements say the current one is not enough.', 'tip')}
''', kw=['scalability', 'scale up', 'scale out', 'vertical scaling', 'horizontal scaling', 'caching', 'read replica'])
K.talk('grow', '''A single database server can do a surprising amount of work, and SQLite alone runs inside countless phone apps. When one server is no longer enough,
you can scale up, buying a bigger machine, or scale out, spreading the work over many machines. Scaling out is much harder, because data must be copied
or split and still stay correct. The sensible order is to fix queries and indexes first, then cache repeated reads, then add read replicas, then partition
big tables, and only then shard across servers. Most apps never need the last step. Think of a busy restaurant that first speeds up its kitchen before
opening a second branch.''')

K.lesson('partition', 'Partitioning a big table', f'''
<p><b>Partitioning</b> splits one big table into smaller pieces on the same server, by a rule such as the year. Queries that name the year read only the matching piece, which is called <b>partition pruning</b>. Old pieces can be dropped in a moment instead of deleting millions of rows.</p>
<pre class="sq-code">-- PostgreSQL declarative partitioning (version 10+)
CREATE TABLE sales (id bigint, sold_on date, amount int) PARTITION BY RANGE (sold_on);
CREATE TABLE sales_2024 PARTITION OF sales FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE sales_2025 PARTITION OF sales FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');</pre>
{K.sql('part', SALES + """
SELECT strftime('%Y', sold_on) AS year, SUM(amount) AS total FROM sales GROUP BY year;""", db='', title='The same idea in SQLite: one table per year behind a UNION ALL view', notes={1: 'CHECK rules say which rows belong in each piece.', 5: 'Queries use the view as if it were one table.'})}
{table(['Partition type', 'Rule', 'Example'], [
    ['Range', 'a range of values per piece', 'one piece per month or year'],
    ['List', 'a list of values per piece', 'one piece per country'],
    ['Hash', 'hash of the key mod N', 'spread customers evenly over 8 pieces']])}
{K.lab('l-part', 'm', 'Sales in 2025', 'The pieces <code>sales_2024</code> and <code>sales_2025</code> and the view <code>sales</code> exist. Return one value <code>total</code>: the sum of amounts sold in 2025, reading only the 2025 piece.',
"""SELECT SUM(amount) AS total FROM sales_2025;""", db='', setup=SALES, hint='Read sales_2025 directly, which is what partition pruning does for you in PostgreSQL.', why='300 + 900 + 400 = 1600.')}
''', kw=['partitioning', 'partition pruning', 'range partition', 'list partition', 'hash partition', 'PARTITION BY'])
K.talk('partition', '''Partitioning splits one huge table into smaller pieces on the same server, using a rule such as the year of each sale. When a query asks for 2025,
the engine reads only the 2025 piece and skips the rest, which is called partition pruning. Dropping a whole old year becomes instant, instead of deleting
millions of rows one by one. Pieces can follow ranges such as months, lists such as countries, or a hash that spreads keys evenly. PostgreSQL has this built
in, and in SQLite you can imitate it with one table per year behind a UNION ALL view. Think of a filing cabinet with one drawer per year.''')

K.lesson('replicate', 'Replication: copies of the whole database', f'''
<p><b>Replication</b> keeps copies of the database on other servers. The <b>primary</b> takes all writes and streams its change log to <b>replicas</b>, which serve reads and can take over if the primary fails.</p>
{table(['Mode', 'How a write is confirmed', 'Trade off'], [
    ['Asynchronous', 'as soon as the primary has it', 'fast, but a crash can lose the last few changes, and replicas lag behind'],
    ['Synchronous', 'only when at least one replica also has it', 'no loss on failover, but every write waits for the network'],
    ['Semi synchronous (MySQL)', 'when a replica has received it', 'a middle ground']])}
{scene('the vanishing comment', '<p>You post a comment on a social site and the page reloads without it. The write went to the primary, but the reload read from a replica a second behind. That gap is <b>replication lag</b>. Apps fix it by reading your own recent writes from the primary for a short time, called read your writes consistency.</p>')}
{steps('Failover', [
    'The primary stops answering.',
    'Monitoring notices after a few missed heartbeats.',
    'The most up to date replica is promoted to primary.',
    'Apps reconnect to the new primary. With asynchronous replication, the newest changes may be lost.'])}
{K.sql('lag', """CREATE TABLE heartbeat (server TEXT, last_change TEXT);
INSERT INTO heartbeat VALUES ('primary', '2025-07-15 10:00:05'), ('replica1', '2025-07-15 10:00:04'), ('replica2', '2025-07-15 09:59:35');
SELECT server, CAST((julianday((SELECT last_change FROM heartbeat WHERE server = 'primary')) - julianday(last_change)) * 86400 AS INTEGER) AS lag_seconds
FROM heartbeat;""", db='', title='Measuring replication lag', notes={3: 'How many seconds each copy is behind the primary. replica2 is 30 seconds behind.'})}
''', kw=['replication', 'primary', 'replica', 'read replica', 'replication lag', 'synchronous replication', 'failover', 'read your writes'])
K.talk('replicate', '''Replication keeps full copies of the database on other servers. The primary takes every write and streams its change log to replicas, which answer
read queries and can take over if the primary fails. With asynchronous replication, a write is confirmed as soon as the primary has it, which is fast,
but replicas run a little behind, and a crash can lose the newest changes. Synchronous replication waits for a replica too, so nothing is lost, but every
write is slower. The delay is called replication lag, and it is why a comment you just posted can seem to vanish on reload. Think of a teacher's notes
being copied by students who write a little slower.''')

K.lesson('shard', 'Sharding and the CAP theorem', f'''
<p><b>Sharding</b> splits the rows of a table across several servers, each holding a <b>shard</b>. It spreads writes, which replication cannot do. The choice of <b>shard key</b> decides almost everything.</p>
{pk('sqshard')}
{K.sql('shardkey', """SELECT id, name, id % 3 AS shard FROM customers ORDER BY shard, id;""", title='Hash sharding customers over 3 servers', notes={1: 'Each customer and all of their orders would live on server id mod 3.'})}
{table(['Good shard key', 'Bad shard key'], [
    ['spreads data and traffic evenly (customer id)', 'creates hot spots (today’s date sends all new writes to one server)'],
    ['most queries include it', 'most queries must ask every shard'],
    ['keeps related rows together', 'splits rows that are always read together']])}
<p>The <b>CAP theorem</b> (Brewer 2000, proved by Gilbert and Lynch 2002) says that when the network between servers breaks (a <b>partition</b>), a distributed database must choose: stay <b>consistent</b> and refuse some requests, or stay <b>available</b> and risk returning old data.</p>
{table(['Choice during a network split', 'Behaviour', 'Examples'], [
    ['Consistency (CP)', 'some requests fail until the split heals', 'Spanner, CockroachDB, etcd'],
    ['Availability (AP)', 'every server answers, copies may disagree for a while', 'Cassandra and DynamoDB in default modes']])}
{K.lab('l-shard', 'e', 'Which server holds each customer', 'Show each customer’s <code>name</code> and <code>server</code>, their id mod 4, for 4 servers, ordered by id.',
"""SELECT name, id % 4 AS server FROM customers ORDER BY id;""", hint='id % 4', why='Ids 4 and 8 go to server 0, ids 1 and 5 to server 1, and so on.', ordered=True)}
''', kw=['sharding', 'shard key', 'hot spot', 'hash sharding', 'CAP theorem', 'consistency', 'availability', 'network partition'])
K.talk('shard', '''Sharding splits the rows of a table across several servers, so writes are shared out, which replication alone cannot do. The shard key decides where
each row lives. A good key, such as customer id, spreads data evenly and appears in most queries. A bad key, such as today's date, sends every new write to
one server. In the animation, choose a key and the number of servers, and see which servers a query must visit. The CAP theorem says that when the network
between servers breaks, a database must choose between staying consistent and refusing some requests, or staying available and risking old answers.
Think of a library split across several buildings.''')

K.lesson('olap', 'OLTP, OLAP and column stores', f'''
<p>Not all databases do the same job. <b>OLTP</b> (online transaction processing) runs the app: many small reads and writes. <b>OLAP</b> (online analytical processing) answers big questions over history: few huge queries.</p>
{table(['', 'OLTP', 'OLAP'], [
    ['Typical query', 'fetch order 105, insert one row', 'total sales by region by month for 5 years'],
    ['Rows touched', 'a few', 'millions or billions'],
    ['Design', 'normalized (3NF)', 'star schema, denormalized dimensions'],
    ['Storage', 'row store', 'column store'],
    ['Examples', 'PostgreSQL, MySQL, SQL Server, SQLite', 'Snowflake, BigQuery, Redshift, ClickHouse, DuckDB']])}
<p>A <b>column store</b> keeps each column together on disk. A query that sums one column reads only that column, and similar values compress very well (C-Store, Stonebraker and others, 2005).</p>
{K.sql('star', """CREATE TABLE dim_product (product_key INTEGER PRIMARY KEY, name TEXT, category TEXT);
CREATE TABLE dim_date (date_key TEXT PRIMARY KEY, month TEXT);
CREATE TABLE fact_sales (date_key TEXT, product_key INTEGER, qty INTEGER, amount INTEGER);
INSERT INTO dim_product SELECT id, name, category FROM products;
INSERT INTO dim_date SELECT DISTINCT order_date, substr(order_date, 1, 7) FROM orders;
INSERT INTO fact_sales SELECT o.order_date, oi.product_id, oi.qty, oi.qty * p.price
  FROM orders o JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE o.status <> 'cancelled';
SELECT d.month, p.category, SUM(f.amount) AS sales
FROM fact_sales f JOIN dim_date d USING (date_key) JOIN dim_product p USING (product_key)
GROUP BY d.month, p.category ORDER BY d.month, sales DESC;""", title='A tiny star schema built from the shop', notes={3: 'The fact table holds the numbers, one row per sale line.', 9: 'Reports join the facts to a few dimensions and group.'})}
{note('Many companies copy data from OLTP databases into a warehouse every night or continuously (ETL or ELT), so heavy reports never slow down the app.', 'tip')}
{K.lab('l-star', 'h', 'Sales by category', 'Using the shop data, show each product <code>category</code> and <code>sales</code>, the total of qty × price over order lines of orders that were not cancelled, highest first.',
"""SELECT p.category, SUM(oi.qty * p.price) AS sales FROM orders o JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE o.status <> 'cancelled' GROUP BY p.category ORDER BY sales DESC;""", hint='Join orders, order_items and products, filter cancelled, GROUP BY category.', why='This is the shape of almost every analytics query: join, filter, group, sum.', ordered=True)}
''', kw=['OLTP', 'OLAP', 'column store', 'row store', 'data warehouse', 'star schema', 'fact table', 'dimension table', 'ETL'])
K.talk('olap', '''Databases do two different jobs. OLTP, online transaction processing, runs the app with many small reads and writes, like placing an order. OLAP,
online analytical processing, answers big questions over years of history, like total sales by region by month. OLAP systems often store data by column
instead of by row, so a query that sums one column reads only that column, and similar values compress well. Warehouses use a star schema, with one big
fact table of numbers joined to small dimension tables such as date and product. Data is copied from the app database into the warehouse so reports never
slow down the shop. Think of a shop's till receipts versus the yearly accounts book.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>When one server is too small, copy the data to more servers for reading, or split it so each server holds a part.</p>',
    '<p>Partitioning splits a table on one server, replication copies the whole database, sharding splits rows across servers. OLTP and OLAP need different designs.</p>',
    '<p>Consensus protocols (Paxos, Raft) keep replicas in agreement. Consistency models range from linearizable to eventual. Distributed SQL engines combine sharding, replication and transactions: Spanner, CockroachDB, YugabyteDB, TiDB.</p>',
    '<p>Research explores disaggregated storage (Amazon Aurora, 2017, ships only the log to a shared storage layer), serverless databases that scale to zero, and lakehouse formats such as Apache Iceberg and Delta Lake that bring tables and transactions to files in object storage.</p>')}
{deep('NoSQL and NewSQL', '<p>Around 2009 many systems dropped SQL and joins to scale out more easily: key value stores, document stores (MongoDB), wide column stores (Cassandra) and graph databases (Neo4j). Later, NewSQL and distributed SQL systems showed that SQL and transactions can also scale out, and many NoSQL systems added SQL like query languages. Choose by data shape and access pattern, not by fashion.</p>')}
''', kw=['Raft', 'Paxos', 'eventual consistency', 'distributed SQL', 'Aurora', 'lakehouse', 'NoSQL', 'NewSQL'])
K.talk('levels', '''Let us climb the ladder. For a beginner, when one server is too small, copy the data for reading or split it into parts. At college level, know
partitioning, replication and sharding, and that OLTP and OLAP need different designs. At masters level, consensus protocols such as Raft keep copies in
agreement, and distributed SQL engines combine all of these with transactions. At research level, storage is separated from compute, and table formats
bring transactions to files in cloud storage. Think of a newspaper printed in many cities from the same master copy.''')

K.quiz('e', 'Buying a bigger server is', ['Scaling out', 'Scaling up', 'Sharding', 'Replication'], 1, 'Vertical.', 'Scale up means a bigger machine.')
K.quiz('e', 'A read replica', ['Takes all writes', 'Serves reads from a copy', 'Deletes old data', 'Is an index'], 1, 'Copy.', 'It copies the primary and answers reads.')
K.quiz('e', 'Partitioning splits a table', ['Across the internet', 'Into pieces on the same server', 'Into views', 'Into columns only'], 1, 'Same server.', 'Sharding splits across servers.')
K.quiz('e', 'OLTP systems mostly run', ['Huge reports', 'Many small reads and writes', 'Backups', 'Machine learning'], 1, 'Transactions.', 'They run the live app.')
K.quiz('m', 'Partition pruning means', ['Deleting partitions', 'Reading only the partitions a query needs', 'Compressing data', 'Sorting'], 1, 'Skip pieces.', 'Matching pieces only.')
K.quiz('m', 'Replication lag causes', ['Lost tables', 'Replicas showing slightly old data', 'Syntax errors', 'Deadlocks'], 1, 'Behind.', 'Replicas may be a moment behind.')
K.quiz('m', 'A shard key of today’s date tends to create', ['Even load', 'A hot spot', 'Fewer servers', 'Smaller indexes'], 1, 'All new writes together.', 'Every new write hits one shard.')
K.quiz('m', 'A column store is fastest for', ['Fetching one whole row', 'Summing one column over many rows', 'Single row inserts', 'Locks'], 1, 'Columns together.', 'It reads only the needed columns.')
K.quiz('m', 'In a star schema, the big central table is the', ['Dimension table', 'Fact table', 'Lookup table', 'View'], 1, 'Facts.', 'Numbers live in the fact table.')
K.quiz('h', 'CAP says that during a network partition a system must choose between', ['Speed and size', 'Consistency and availability', 'SQL and NoSQL', 'Rows and columns'], 1, 'C or A.', 'It cannot guarantee both while the split lasts.')
K.quiz('x', 'Which protocol is used by etcd and CockroachDB to keep replicas in agreement?', ['TCP', 'Raft', 'HTTP', 'SMTP'], 1, 'Consensus.', 'Raft.')

y25 = value('', 'SELECT SUM(amount) FROM sales_2025', setup=SALES)
K.calc('e', 'What is the total amount in the 2025 partition?', str(y25), 'Add three sales.',
       ['Sales of 300, 900 and 400.', 'Add them.', eq(f'300 + 900 + 400 = {y25}')], check=y25)
K.calc('e', 'A query for 2025 reads only the 2025 piece. Of 5 rows in total, how many does it skip?', '2', 'The 2024 rows.',
       ['sales_2024 has 2 rows.', 'Pruning skips that whole piece.', eq('2 rows skipped')], check=value('', 'SELECT count(*) FROM sales_2024', setup=SALES))
lag2 = value('', "SELECT CAST((julianday('2025-07-15 10:00:05') - julianday('2025-07-15 09:59:35')) * 86400 AS INTEGER)")
K.calc('m', 'The primary’s last change was at 10:00:05 and replica2’s at 09:59:35. How many seconds is replica2 behind?', str(lag2), 'Subtract the times.',
       ['From 09:59:35 to 10:00:00 is 25 seconds.', 'Then 5 more seconds.', eq(f'25 + 5 = {lag2} seconds')], check=lag2)
s0 = value('shop', 'SELECT count(*) FROM customers WHERE id % 3 = 0')
K.calc('m', 'With 8 customers hashed by id mod 3, how many land on server 0?', str(s0), 'Ids divisible by 3.',
       ['Ids 1 to 8.', 'Divisible by 3: 3 and 6.', eq(f'{s0} customers')], check=s0)
K.calc('m', 'A table of 100 million rows is hash partitioned into 16 pieces. About how many rows per piece?', '6250000', 'Divide.',
       ['Hash spreads rows evenly.', '100,000,000 ÷ 16.', eq('6,250,000 rows')], check=100_000_000 // 16)
K.calc('m', 'One primary and 3 read replicas each handle 2,000 reads per second. What is the total read capacity?', '8000', 'Add all servers that serve reads.',
       ['The primary also serves reads here.', '4 servers × 2,000.', eq('8,000 reads per second')], check=8000)
K.calc('h', 'A column store reads 1 of 20 equal size columns for a SUM. What fraction of the data does it read compared with a row store?', '0.05', 'One twentieth.',
       ['A row store reads whole rows, all 20 columns.', 'The column store reads 1 column.', eq('1 ÷ 20 = 0.05')], check=0.05)
cat = value('shop', "SELECT SUM(oi.qty * p.price) FROM orders o JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE o.status <> 'cancelled' AND p.category = 'Electronics'")
K.calc('h', 'In the star schema, what are total Electronics sales (cancelled orders left out)?', str(cat), 'Electronics lines.',
       ['Headphones 1499 twice (orders 102, 107).', 'Phone chargers: 2 in order 104, 1 in order 107, at 699.', eq(f'2 × 1499 + 3 × 699 = {cat}')], check=cat)

K.must('Order of fixes', 'Tune queries and indexes, cache, add read replicas, partition, and shard last.')
K.must('Partitioning', 'Range, list or hash pieces of one table on one server. Pruning reads only the pieces needed.')
K.must('Replication', 'Primary takes writes, replicas copy the log and serve reads. Async is fast but lags, sync waits but loses nothing.')
K.must('Sharding and CAP', 'Rows spread across servers by a shard key. During a network split, choose consistency or availability.')
K.must('OLTP and OLAP', 'Small transactions in normalized row stores, big analytics in star schemas and column stores.')

T = K.topic(
    slug='sql-scale', topic='sql-scale', step=(8, 'Professional SQL', 'sql-pro', 'Logic inside the database, security, scaling to many machines, and the differences between engines.', 'Advanced'),
    title='Databases at scale', short='Scaling databases', badge='8.3', minutes=40, added='2026-11-23',
    lead='Learn what happens when one server is not enough: partitioning big tables, replicating to read replicas, sharding across servers, the CAP theorem, and the difference between OLTP apps and OLAP warehouses.',
    desc='Scale up and scale out, caching, partitioning with pruning, replication modes and lag, failover, sharding and shard keys, the CAP theorem, OLTP and OLAP, column stores, star schemas, NoSQL and distributed SQL.',
    summary='Partitioning, replication, sharding, CAP, OLTP versus OLAP and column stores.',
    keywords=['scaling', 'partitioning', 'replication', 'sharding', 'CAP theorem', 'OLAP', 'column store'],
    recap='<p>Tune first, then cache, replicate for reads, partition big tables and shard for writes, and use column stores for analytics.</p>')
