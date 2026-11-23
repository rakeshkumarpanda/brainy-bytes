# Chapter 7.3: transactions and concurrency: ACID, BEGIN, COMMIT, ROLLBACK, autocommit, SAVEPOINT, isolation levels and the
# anomalies they prevent (dirty read, non repeatable read, phantom, lost update, write skew), locking, MVCC, deadlocks,
# SQLite journal and WAL modes, and default isolation levels across engines.
# Sources: sqlite.org lang_transaction.html (DEFERRED, IMMEDIATE, EXCLUSIVE), lang_savepoint.html, isolation.html
# (SQLite transactions are serializable), wal.html, atomiccommit.html, postgresql.org transaction-iso.html (default READ
# COMMITTED, SSI for SERIALIZABLE), MySQL innodb-transaction-isolation-levels.html (default REPEATABLE READ), Microsoft
# SET TRANSACTION ISOLATION LEVEL docs (default READ COMMITTED), Haerder and Reuter 1983 (the term ACID), Berenson et al.
# 1995 "A Critique of ANSI SQL Isolation Levels".
from cvkit import fx, fxs, ladder, scene, note, deep, table, steps, eq
from sqlkit import SKit, pk, value, grid

K = SKit()

ACC = "CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0)); INSERT INTO accounts VALUES ('Asha', 500), ('Ravi', 200);"

K.lesson('acid', 'All or nothing: transactions and ACID', f'''
<p>Moving 300 rupees from Asha to Ravi takes two UPDATEs. If the power fails between them, money vanishes. A <b>transaction</b> groups statements so they succeed together or not at all.</p>
{fxs(fx('Transaction', '<code>BEGIN; ... ; COMMIT;</code>', 'COMMIT makes every change permanent at once.', key=True),
     fx('Undo', '<code>ROLLBACK;</code>', 'Throws away every change since BEGIN.'))}
{K.sql('commit', ACC + """
BEGIN;
UPDATE accounts SET balance = balance - 300 WHERE name = 'Asha';
UPDATE accounts SET balance = balance + 300 WHERE name = 'Ravi';
COMMIT;
SELECT name, balance, (SELECT SUM(balance) FROM accounts) AS total FROM accounts;""", db='', title='A transfer that commits', notes={2: 'Start the transaction.', 5: 'Both changes become permanent together. The total stays 700.'})}
{K.sql('rollback', ACC + """
BEGIN;
UPDATE accounts SET balance = balance - 300 WHERE name = 'Asha';
ROLLBACK;
SELECT * FROM accounts;""", db='', title='Changed your mind: ROLLBACK', notes={4: 'Asha’s 300 comes back. Nothing since BEGIN is kept.'})}
{table(['Letter', 'Promise', 'In the transfer'], [
    ['A, atomicity', 'all statements happen, or none', 'never only one of the two UPDATEs'],
    ['C, consistency', 'every rule holds after the transaction', 'CHECK (balance >= 0) is never broken'],
    ['I, isolation', 'running transactions do not see each other’s half done work', 'nobody sees the money in mid air'],
    ['D, durability', 'once committed, the change survives a crash', 'after COMMIT returns, a power cut cannot undo it']])}
{note('Without BEGIN, each statement is its own transaction (autocommit). Many small INSERTs inside one BEGIN ... COMMIT also run far faster, because the engine syncs to disk once instead of once per row.', 'tip')}
{K.lab('l-transfer', 'e', 'Transfer 150', 'Inside one transaction, move 150 from Asha to Ravi and commit. Then show every account ordered by name.',
"""BEGIN;
UPDATE accounts SET balance = balance - 150 WHERE name = 'Asha';
UPDATE accounts SET balance = balance + 150 WHERE name = 'Ravi';
COMMIT;
SELECT * FROM accounts ORDER BY name;""", db='', setup=ACC, hint='BEGIN, two UPDATEs, COMMIT, then SELECT.', why='Asha 350, Ravi 350, total still 700.', ordered=True)}
''', kw=['transaction', 'BEGIN', 'COMMIT', 'ROLLBACK', 'ACID', 'atomicity', 'durability', 'autocommit'])
K.talk('acid', '''Moving money from Asha to Ravi takes two updates, and if the power fails in between, money vanishes. A transaction groups statements so they all
happen or none do. You write BEGIN, the statements, and COMMIT to make everything permanent at once, or ROLLBACK to throw it all away. Databases promise
four things, called ACID. Atomicity means all or nothing. Consistency means every rule still holds afterwards. Isolation means others never see your
half done work. Durability means a committed change survives a crash. Without BEGIN, each statement is its own small transaction. Think of a shop
till where the sale only counts once the receipt prints.''')

K.lesson('failure', 'Errors, savepoints and failed transfers', f'''
<p>When a statement inside a transaction fails, you decide: roll back everything, or go back to a <b>savepoint</b> and carry on.</p>
{pk('sqtx')}
{K.sql('fail', ACC + """
BEGIN;
UPDATE accounts SET balance = balance + 700 WHERE name = 'Ravi';
UPDATE accounts SET balance = balance - 700 WHERE name = 'Asha';""", db='', title='The second step breaks a rule', err=True, notes={3: 'Ravi gets 700 inside the transaction.', 4: 'Asha only has 500: the CHECK refuses. The app must now ROLLBACK, so Ravi’s extra 700 disappears too.'})}
{K.sql('savepoint', ACC + """
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE name = 'Asha';
SAVEPOINT bonus;
UPDATE accounts SET balance = balance + 999 WHERE name = 'Ravi';
ROLLBACK TO bonus;
UPDATE accounts SET balance = balance + 100 WHERE name = 'Ravi';
COMMIT;
SELECT * FROM accounts;""", db='', title='SAVEPOINT undoes part of a transaction', notes={4: 'A named point inside the transaction.', 6: 'Undo only what came after the savepoint. The first UPDATE stays.'})}
{steps('What an app does around a transaction', [
    'BEGIN.',
    'Run each statement and check for an error.',
    'On any error, ROLLBACK and report the problem.',
    'If every statement worked, COMMIT. Most database libraries wrap this in a "with transaction" block.'])}
{note('In SQLite a failed statement inside a transaction undoes only that statement by default. The transaction stays open, and it is the program’s job to ROLLBACK. PostgreSQL marks the whole transaction as failed until you ROLLBACK.', 'warn')}
{K.lab('l-save', 'm', 'Keep the first change only', 'In one transaction: take 50 from Asha, set a savepoint <code>s1</code>, add 5000 to Ravi by mistake, roll back to s1, and commit. Show every account ordered by name.',
"""BEGIN;
UPDATE accounts SET balance = balance - 50 WHERE name = 'Asha';
SAVEPOINT s1;
UPDATE accounts SET balance = balance + 5000 WHERE name = 'Ravi';
ROLLBACK TO s1;
COMMIT;
SELECT * FROM accounts ORDER BY name;""", db='', setup=ACC, hint='BEGIN, UPDATE, SAVEPOINT s1, UPDATE, ROLLBACK TO s1, COMMIT, SELECT.', why='Only the change before the savepoint survives: Asha 450, Ravi 200.', ordered=True)}
''', kw=['SAVEPOINT', 'ROLLBACK TO', 'error handling', 'failed transaction', 'nested transaction'])
K.talk('failure', '''When a statement inside a transaction fails, the program decides what happens next. Usually it rolls everything back, so a transfer that cannot finish
leaves both accounts as they were. In the animation, pick the failing transfer and watch Ravi receive money, Asha's check fail, and the rollback put
everything back. A savepoint is a named marker inside a transaction. ROLLBACK TO that name undoes only what came after it, and the earlier work stays.
Most database libraries wrap begin, commit and rollback in one block, so you rarely forget. Think of the undo button in a drawing app that goes back to a
checkpoint.''')

K.lesson('isolation', 'Isolation levels and anomalies', f'''
<p>Many users run transactions at the same time. Full isolation is expensive, so the SQL standard defines four <b>isolation levels</b>, each preventing more <b>anomalies</b>.</p>
{table(['Anomaly', 'What goes wrong'], [
    ['Dirty read', 'you read another transaction’s change before it commits, and it later rolls back'],
    ['Non repeatable read', 'you read a row twice and get different values, because someone committed in between'],
    ['Phantom', 'you run the same WHERE twice and new rows appear'],
    ['Lost update', 'two transactions read the same value and both write, so one change is overwritten'],
    ['Write skew', 'two transactions each check a rule, then write different rows, and together break the rule']])}
{table(['Level', 'Dirty read', 'Non repeatable read', 'Phantom'], [
    ['READ UNCOMMITTED', 'possible', 'possible', 'possible'],
    ['READ COMMITTED', 'prevented', 'possible', 'possible'],
    ['REPEATABLE READ', 'prevented', 'prevented', 'possible in the standard'],
    ['SERIALIZABLE', 'prevented', 'prevented', 'prevented']])}
{table(['Engine', 'Default level'], [
    ['PostgreSQL', 'READ COMMITTED'],
    ['MySQL InnoDB', 'REPEATABLE READ'],
    ['SQL Server, Oracle', 'READ COMMITTED'],
    ['SQLite', 'SERIALIZABLE in effect: one writer at a time']])}
{K.sql('atomicupd', ACC + """
UPDATE accounts SET balance = balance + 100 WHERE name = 'Asha';
UPDATE accounts SET balance = balance + 1000 WHERE name = 'Asha';
SELECT * FROM accounts WHERE name = 'Asha';""", db='', title='Let the database do the arithmetic', notes={2: 'balance = balance + 100 reads and writes in one step, so no other update can slip in between.', 3: 'Both changes count: 1600.'})}
{note('The lost update in the animation happens because the app read a value, computed in its own memory, and wrote a fixed number back. Writing balance = balance + 100, or locking with SELECT ... FOR UPDATE, prevents it.', 'tip')}
''', kw=['isolation level', 'dirty read', 'non repeatable read', 'phantom read', 'lost update', 'write skew', 'READ COMMITTED', 'SERIALIZABLE'])
K.talk('isolation', '''Many people use a database at the same moment, and full isolation is expensive, so the SQL standard offers four isolation levels. Each prevents
more problems. A dirty read sees someone's change before it commits. A non repeatable read gets a different value the second time. A phantom is a new
row that appears when you repeat a search. A lost update happens when two people read the same balance and both write, so one change is overwritten.
PostgreSQL and SQL Server default to read committed, MySQL to repeatable read, and SQLite allows one writer at a time. Letting the database do the
arithmetic, as in balance equals balance plus one hundred, avoids lost updates. Think of two cashiers updating the same paper ledger.''')

K.lesson('locks', 'Locks, MVCC, deadlocks and the journal', f'''
<p>How do engines keep the promises? Two main tools: <b>locks</b>, which make others wait, and <b>MVCC</b> (multi version concurrency control), which lets readers see an older version while a writer works.</p>
{table(['Tool', 'How it works', 'Used by'], [
    ['Row locks', 'a writer locks the rows it changes until commit, other writers wait', 'PostgreSQL, MySQL InnoDB, SQL Server, Oracle'],
    ['MVCC', 'each change creates a new row version, readers see the versions committed before they started', 'PostgreSQL, Oracle, InnoDB, SQL Server snapshot isolation'],
    ['Database lock', 'one writer for the whole database at a time', 'SQLite'],
    ['Write ahead log', 'changes go to a log first, so a crash can replay or undo them', 'almost every engine, SQLite in WAL mode']])}
{steps('A deadlock', [
    'Transaction 1 locks Asha’s row, then asks for Ravi’s.',
    'Transaction 2 locked Ravi’s row first, and now asks for Asha’s.',
    'Each waits for the other forever.',
    'The engine detects the cycle and aborts one of them with a deadlock error. The app should retry it.',
    'Prevention: always lock rows in the same order, for example by account id.'])}
{K.sql('modes', """PRAGMA journal_mode;
BEGIN IMMEDIATE;
CREATE TABLE t (x INTEGER);
COMMIT;
SELECT name FROM sqlite_schema WHERE name = 't';""", db='', title='SQLite transaction modes', notes={1: 'In memory databases report memory. Files default to delete, and many apps switch to wal for better concurrency.', 2: 'IMMEDIATE takes the write lock at BEGIN. DEFERRED (the default) waits until the first write.'})}
{scene('booking the last train seat', '<p>Two people press Book on the last seat at the same moment. With SELECT ... FOR UPDATE on the seat row (PostgreSQL, MySQL), the second request waits until the first commits, then sees the seat is taken and gets a polite "sold out". Without a lock, both could read "free" and both get tickets for the same seat, a classic race condition.</p>')}
{K.lab('l-fail', 'h', 'Roll back a failed transfer', 'Start a transaction, add 700 to Ravi, then roll back (the matching withdrawal from Asha would fail). Show every account ordered by name.',
"""BEGIN;
UPDATE accounts SET balance = balance + 700 WHERE name = 'Ravi';
ROLLBACK;
SELECT * FROM accounts ORDER BY name;""", db='', setup=ACC, hint='BEGIN, the UPDATE, ROLLBACK, SELECT.', why='Nothing changed: Asha 500, Ravi 200.', ordered=True)}
''', kw=['lock', 'row lock', 'MVCC', 'deadlock', 'write ahead log', 'WAL', 'BEGIN IMMEDIATE', 'SELECT FOR UPDATE', 'race condition'])
K.talk('locks', '''Engines keep their promises with two main tools. Locks make other writers wait until a transaction commits. MVCC, multi version concurrency control,
keeps old versions of rows, so readers see a consistent snapshot while a writer works, and readers never block writers. SQLite takes a simpler path,
with one writer for the whole database at a time. A deadlock happens when two transactions each hold a lock the other needs, and the engine breaks it by
cancelling one, which the app should retry. Locking rows in the same order prevents most deadlocks. A write ahead log records changes first, so a crash
can be repaired. Think of two people at a narrow door, each waiting for the other to go first.''')

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A transaction is all or nothing. COMMIT keeps the changes, ROLLBACK throws them away.</p>',
    '<p>ACID, isolation levels and their anomalies, autocommit, savepoints. Use atomic UPDATEs or row locks to avoid lost updates, and retry on deadlock or serialization errors.</p>',
    '<p>Serializability means the result equals some one at a time order. Two phase locking guarantees it with locks. Snapshot isolation, used by many MVCC engines, still allows write skew (Berenson et al., 1995), and PostgreSQL’s SERIALIZABLE adds Serializable Snapshot Isolation to catch it (Cahill et al., 2008).</p>',
    '<p>Distributed transactions across machines use two phase commit, and consensus protocols such as Paxos and Raft replicate the log. Systems such as Google Spanner (2012) use synchronized clocks to give global ordering, and CockroachDB and TiDB follow similar ideas.</p>')}
{deep('Where ACID came from', '<p>Jim Gray described the transaction concept in 1981, and Theo Haerder and Andreas Reuter named the four properties ACID in 1983. Gray received the Turing Award in 1998 largely for this work.</p>')}
''', kw=['serializability', 'two phase locking', 'snapshot isolation', 'SSI', 'two phase commit', 'Spanner', 'Jim Gray'])
K.talk('levels', '''Here is the ladder. For a beginner, a transaction is all or nothing. At college level, know ACID, the isolation levels and their problems, savepoints,
and how to avoid lost updates. At masters level, serializable means the result matches some one at a time order, two phase locking guarantees it, and
snapshot isolation can still allow write skew. At research level, transactions span many machines with two phase commit and consensus, and Google
Spanner even uses synchronized clocks. Think of a relay race where the baton is never in two hands at once.''')

K.quiz('e', 'Which statement makes a transaction’s changes permanent?', ['SAVE', 'COMMIT', 'END ONLY', 'STORE'], 1, 'Commit.', 'COMMIT ends the transaction and keeps the changes.')
K.quiz('e', 'ROLLBACK', ['Repeats the transaction', 'Undoes changes since BEGIN', 'Deletes the table', 'Commits twice'], 1, 'Undo.', 'Everything since BEGIN is thrown away.')
K.quiz('e', 'The A in ACID stands for', ['Accuracy', 'Atomicity', 'Availability', 'Access'], 1, 'All or nothing.', 'Atomicity.')
K.quiz('e', 'Without BEGIN, each statement', ['Fails', 'Is its own transaction', 'Waits forever', 'Is ignored'], 1, 'Autocommit.', 'Each statement commits by itself.')
K.quiz('m', 'Reading another transaction’s uncommitted change is a', ['Phantom', 'Dirty read', 'Lost update', 'Deadlock'], 1, 'Not yet committed.', 'A dirty read.')
K.quiz('m', 'PostgreSQL’s default isolation level is', ['READ UNCOMMITTED', 'READ COMMITTED', 'REPEATABLE READ', 'SERIALIZABLE'], 1, 'Committed.', 'READ COMMITTED.')
K.quiz('m', 'MySQL InnoDB’s default isolation level is', ['READ COMMITTED', 'REPEATABLE READ', 'SERIALIZABLE', 'READ UNCOMMITTED'], 1, 'Repeatable.', 'REPEATABLE READ.')
K.quiz('m', 'ROLLBACK TO sp undoes', ['Everything', 'Only changes after savepoint sp', 'Only the last statement', 'Nothing'], 1, 'Partial.', 'Work before the savepoint stays.')
K.quiz('m', 'Which update avoids a lost update?', ['SET balance = 600', 'SET balance = balance + 100', 'DELETE then INSERT', 'SELECT then SET'], 1, 'Atomic arithmetic.', 'The read and write happen in one step.')
K.quiz('h', 'Two transactions wait for each other’s locks. This is a', ['Phantom', 'Deadlock', 'Dirty read', 'Savepoint'], 1, 'Cycle of waits.', 'The engine aborts one of them.')
K.quiz('x', 'Which anomaly can snapshot isolation still allow?', ['Dirty read', 'Write skew', 'Non repeatable read', 'Lost commit'], 1, 'Disjoint writes.', 'Write skew, caught by SSI.')

K.calc('e', 'Asha 500, Ravi 200. After a committed transfer of 300 from Asha to Ravi, what is Ravi’s balance?', '500', 'Add 300.',
       ['Asha drops to 200.', 'Ravi gains 300.', eq('200 + 300 = 500')], check=value('', "SELECT balance FROM accounts WHERE name = 'Ravi'", setup=ACC + " UPDATE accounts SET balance = balance - 300 WHERE name = 'Asha'; UPDATE accounts SET balance = balance + 300 WHERE name = 'Ravi';"))
K.calc('e', 'What is the total of both balances after that transfer?', '700', 'Money is conserved.',
       ['Asha 200 and Ravi 500.', 'Add them.', eq('200 + 500 = 700, unchanged')], check=700)
K.calc('m', 'In the lost update story, Asha has 500. A refund of 100 and a salary of 1000 both read 500 first. What balance is left at the end?', '1500', 'The second write wins.',
       ['A writes 500 + 100 = 600.', 'B writes 500 + 1000 = 1500 over it.', eq('1500, while 1600 was correct')], check=1500)
K.calc('m', 'How much money did the lost update make disappear?', '100', 'Correct minus actual.',
       ['Correct: 500 + 100 + 1000 = 1600.', 'Actual: 1500.', eq('1600 − 1500 = 100')], check=100)
K.calc('m', 'In the savepoint example, Asha pays 100, Ravi gets +999 which is rolled back to the savepoint, then Ravi gets 100. What is Ravi’s final balance?', '300', 'The 999 is undone.',
       ['ROLLBACK TO removes the +999.', 'Then Ravi gets 100.', eq('200 + 100 = 300')], check=value('', "SELECT balance FROM accounts WHERE name = 'Ravi'", setup=ACC + " BEGIN; UPDATE accounts SET balance = balance - 100 WHERE name = 'Asha'; SAVEPOINT b; UPDATE accounts SET balance = balance + 999 WHERE name = 'Ravi'; ROLLBACK TO b; UPDATE accounts SET balance = balance + 100 WHERE name = 'Ravi'; COMMIT;"))
K.calc('m', '10,000 INSERTs in autocommit mode, each needing a 5 ms disk sync. How long do the syncs take?', '50', 'Seconds.',
       ['Each INSERT is its own transaction.', '10,000 × 5 ms = 50,000 ms.', eq('50 seconds')], check=50)
K.calc('h', 'The same 10,000 INSERTs inside one BEGIN ... COMMIT need one sync. How many times fewer syncs is that?', '10000', 'Divide.',
       ['Before: 10,000 syncs.', 'After: 1 sync.', eq('10,000 ÷ 1 = 10,000 times fewer')], check=10000)
K.calc('h', 'Two transactions lock rows in opposite orders. How many locks does each one hold when the deadlock starts?', '1', 'Each holds one and waits for one.',
       ['T1 holds Asha and waits for Ravi.', 'T2 holds Ravi and waits for Asha.', eq('1 lock each')], check=1)

K.must('Transactions', 'BEGIN ... COMMIT groups statements, ROLLBACK undoes them. Autocommit makes each statement its own transaction.')
K.must('ACID', 'Atomicity, consistency, isolation, durability.')
K.must('Savepoints', 'SAVEPOINT name, ROLLBACK TO name undoes part of a transaction.')
K.must('Isolation', 'READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE prevent more anomalies in turn. Know your engine’s default.')
K.must('Concurrency', 'Use balance = balance + x or SELECT ... FOR UPDATE against lost updates. Lock in a fixed order and retry on deadlock.')

T = K.topic(
    slug='sql-transactions', topic='sql-transactions', step=(7, 'Performance and transactions', 'sql-perf', 'How indexes and query plans make queries fast, and how transactions keep data correct when many people work at once.', 'Advanced'),
    title='Transactions and concurrency', short='Transactions', badge='7.3', minutes=45, added='2026-11-23',
    lead='Keep data correct with all or nothing transactions, undo safely with ROLLBACK and savepoints, and understand isolation levels, locks, MVCC and deadlocks when many users write at once.',
    desc='BEGIN, COMMIT, ROLLBACK, autocommit, ACID, SAVEPOINT, error handling, isolation levels, dirty reads, non repeatable reads, phantoms, lost updates, write skew, engine defaults, locks, MVCC, deadlocks, WAL, SELECT FOR UPDATE, distributed transactions.',
    summary='ACID transactions, savepoints, isolation levels, locks, MVCC and deadlocks.',
    keywords=['transaction', 'ACID', 'COMMIT', 'ROLLBACK', 'isolation level', 'MVCC', 'deadlock'],
    recap='<p>Transactions are all or nothing, isolation levels decide what concurrent users can see, and locks or MVCC keep the promises.</p>')
