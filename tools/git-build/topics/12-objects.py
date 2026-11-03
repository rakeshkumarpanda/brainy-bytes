# Chapter 5.1: the object database. blob, tree, commit and annotated tag objects, the header plus content hash,
# zlib storage in .git/objects, git hash-object and cat-file, tree entry modes, the Merkle structure, SHA-1, the 2017
# SHAttered collision, SHA-1DC, and the SHA-256 object format. Sources: Pro Git 10.2, git-hash-object, git-cat-file,
# gitformat-signature, hash-function-transition docs, shattered.io, Git 3.0 breaking changes (Documentation/
# BreakingChanges.adoc). Every id and every output below was produced by real runs with Git 2.43.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from gitkit import sh, flow, file

K = Kit()

K.code('blobid', r'''
# Git names a file by hashing "blob <size>\0" followed by the content
import hashlib, zlib

content = b"hello\n"
store = b"blob " + str(len(content)).encode() + b"\0" + content
oid = hashlib.sha1(store).hexdigest()
print("stored bytes:", store)
print("object id   :", oid)
print("file path   : .git/objects/" + oid[:2] + "/" + oid[2:])
print("zlib size   :", len(zlib.compress(store)), "bytes on disk")
print("SHA-256 id  :", hashlib.sha256(store).hexdigest())
''')

K.lesson('kinds', 'Four kinds of objects', f'''
<p>Under every command you have learned sits a simple database. Git stores everything as <b>objects</b>, and each object is named by the hash of its content. There are only four kinds.</p>
{table(['Object', 'Holds', 'Points to'], [
    ['<b>blob</b>', 'the bytes of one file, with no name and no permissions', 'nothing'],
    ['<b>tree</b>', 'one folder: a list of names, each with a mode and an object id', 'blobs and other trees'],
    ['<b>commit</b>', 'one tree id, parent ids, author, committer, dates and the message', 'one tree and zero or more parent commits'],
    ['<b>tag</b> (annotated)', 'object id, type, tag name, tagger, date and message', 'usually a commit']])}
{viz('objgraph')}
{sh('Look inside a commit with plumbing', """git cat-file -p HEAD
git cat-file -p HEAD^{tree}""", """tree aaa96ced2d9a1c8e72c56b253a0e2fe78393feb7
author Asha Rao <asha@example.com> 1793593800 +0530
committer Asha Rao <asha@example.com> 1793593800 +0530

First commit
100644 blob ce013625030ba8dba906f756967f9e9ca394464a	hello.txt""", 'Real output')}
{table(['Mode in a tree', 'Means'], [
    ['<code>100644</code>', 'normal file'], ['<code>100755</code>', 'executable file'], ['<code>120000</code>', 'symbolic link'],
    ['<code>040000</code>', 'a subfolder (another tree)'], ['<code>160000</code>', 'a submodule commit (gitlink)']])}
{note('A blob has no file name. The name lives in the tree. That is why renaming a file creates a new tree but reuses the same blob, and why Git detects renames by comparing contents.', 'tip')}
''', kw=['git objects', 'blob', 'tree', 'commit object', 'tag object', 'cat-file', 'file mode', '100644', '100755', '160000', 'gitlink'])

K.lesson('hash', 'How an object gets its name', f'''
<p>To name an object, Git writes a small header, the type, a space, the size in bytes and a zero byte, puts the content after it and hashes the whole thing with SHA-1. The 40 hex digits are the object id. Type your own content in the animation and watch the id change.</p>
{viz('hashobj')}
{sh('The same id three ways', """echo hello > hello.txt
git hash-object hello.txt
printf 'blob 6\\0hello\\n' | sha1sum
git add hello.txt && find .git/objects -type f""", """ce013625030ba8dba906f756967f9e9ca394464a
ce013625030ba8dba906f756967f9e9ca394464a  -
.git/objects/ce/013625030ba8dba906f756967f9e9ca394464a""", 'Real output: every computer in the world gets this id for hello')}
{code('blobid')}
{fxs(
    fx('Hash without storing', '<code>git hash-object &lt;file&gt;</code>', 'Add -w to also write the object into .git/objects.', key=True),
    fx('Read any object', '<code>git cat-file -t &lt;id&gt;</code>, <code>-s</code>, <code>-p</code>', '-t prints the type, -s the size, -p the content in readable form.', key=True),
    fx('Where it is stored', '<code>.git/objects/ce/013625...</code>', 'First 2 hex digits are the folder, the other 38 the file name. The file is zlib compressed.'),
    fx('Short ids', '<code>git rev-parse --short HEAD</code>', 'Any unique prefix works, usually 7 or more digits.'))}
{note('The id depends only on the content, never on the file name, date or computer. Ten copies of the same file in a repository are stored once.', 'exam')}
''', kw=['hash-object', 'object id', 'SHA-1', 'header', 'zlib', '.git/objects', 'content addressable', 'short id', 'rev-parse', 'deduplication'])

K.lesson('merkle', 'Why history cannot be changed quietly', f'''
<p>A commit holds the id of its tree and the ids of its parents. A tree holds the ids of its blobs and subtrees. So the id of a commit depends on every file and every earlier commit. Change one byte in an old file and every id above it changes, all the way to the newest commit. This structure is a <b>Merkle tree</b>, the same idea used in blockchains and certificate transparency logs.</p>
{steps('One byte changes everything above it', [
    'You change hello.txt from "hello" to "hallo". The blob id changes.',
    'The tree lists that blob, so the tree content changes and the tree id changes.',
    'The commit lists that tree, so the commit id changes.',
    'Every later commit lists its parent id, so every later commit id changes too.',
    'Anyone comparing the newest commit id with their own copy sees at once that history was changed. This is why rebase and amend always create new ids.'])}
{scene('SHAttered, 2017', '<p>In February 2017 researchers from CWI Amsterdam and Google published two different PDF files with the same SHA-1 hash, the first practical SHA-1 collision. Git reacted the same year: since Git 2.13 it uses a hardened SHA-1 implementation (SHA-1DC) that detects the known collision attack and refuses such objects. Git 2.29 added an experimental SHA-256 object format, and the plans for Git 3.0 make SHA-256 the default for new repositories.</p>')}
{sh('A SHA-256 repository', """git init --object-format=sha256 demo
cd demo && echo hello > hello.txt
git hash-object hello.txt""", """2cf8d83d9ee29543b34a87727421fdecb7e3f3a183d337639025de576db9ebb4""", 'Real output: 64 hex digits')}
{note('SHA-1 and SHA-256 repositories cannot simply push to each other yet, and some hosting services do not accept SHA-256 repositories. Check your server before you switch.', 'warn')}
''', kw=['Merkle tree', 'integrity', 'tamper evident', 'SHAttered', 'collision', 'SHA-1DC', 'SHA-256', 'object-format', 'Git 3.0'])

K.lesson('tagobj', 'Annotated tags as objects, and the full picture', f'''
{sh('An annotated tag is its own object', """git tag -a v1.0 -m "Release 1.0"
git cat-file -t v1.0
git cat-file -p v1.0""", """tag
object aa1cc961b5f90c399a85465ec3ca67ad215a0b47
type commit
tag v1.0
tagger Asha Rao <asha@example.com> 1793593800 +0530

Release 1.0""", 'Real output')}
<p>A lightweight tag is only a ref file that holds a commit id. An annotated tag is an object with its own id that points to the commit, which is why it can carry a message and a signature.</p>
{ladder(
    '<p>Git keeps every version of every file as an object, named by a fingerprint of its content. Folders are lists of names and fingerprints, and a commit is a note that points at a folder and at the commit before it.</p>',
    '<p>Four object types: blob, tree, commit, tag. Ids are SHA-1 of the type, the size, a zero byte and the content. Objects are zlib compressed in .git/objects/xx/ and are immutable. Identical content is stored once.</p>',
    '<p>The commit graph is a Merkle DAG, so one id authenticates the whole history below it. A signature on a commit or tag signs exactly that content, so it covers every file through the tree id.</p>',
    '<p>The hash function transition keeps a translation table between SHA-1 and SHA-256 ids so that repositories can interoperate during the change. Research on version control as content addressed storage influenced systems such as IPFS and Nix.</p>')}
''', kw=['annotated tag object', 'lightweight tag', 'tagger', 'immutable objects', 'Merkle DAG'])

K.quiz('e', 'Which object stores the content of a file?', ['tree', 'blob', 'commit', 'tag'], 1, 'Binary large object.', 'A blob has only bytes, no name.')
K.quiz('e', 'Where is the file name stored?', ['In the blob', 'In the tree that lists the blob', 'In the commit message', 'In .gitignore'], 1, 'Folders hold names.', 'Each tree entry has mode, type, id and name.')
K.quiz('e', 'How many hex digits does a SHA-1 object id have?', ['20', '32', '40', '64'], 2, '160 bits.', '160 bits / 4 bits per hex digit = 40. SHA-256 ids have 64.')
K.quiz('m', 'Two files in different folders have exactly the same content. How many blobs are stored?', ['Two', 'One', 'None', 'Depends on the names'], 1, 'Content address.', 'Same content gives the same id, stored once.')
K.quiz('m', 'Which command prints the type of an object?', ['git cat-file -p', 'git cat-file -t', 'git show --type', 'git ls-files'], 1, 't for type.', '-s prints the size, -p the content.')
K.quiz('m', 'What does a commit object NOT contain?', ['A tree id', 'Parent ids', 'The full content of every file', 'The author'], 2, 'Pointers only.', 'Files are reached through the tree.')
K.quiz('m', 'Which tree mode marks an executable file?', ['100644', '100755', '040000', '120000'], 1, 'Like chmod 755.', '120000 is a symlink, 040000 a subtree.')
K.quiz('h', 'You change one byte in a file from three commits ago and rewrite history. How many of those commit ids change?', ['Only the old commit', 'The old commit and every later commit', 'None', 'Only the newest'], 1, 'Chain of ids.', 'Each commit holds its parent id.')
K.quiz('h', 'What did Git do after the 2017 SHAttered collision?', ['Nothing', 'Switched to MD5', 'Adopted a collision detecting SHA-1 (SHA-1DC) and started the move to SHA-256', 'Removed hashes'], 2, 'Two steps.', 'SHA-1DC in 2.13, SHA-256 format later.')
K.quiz('x', 'A file holds hi and a newline. What exactly is hashed to get its blob id?', ['Only the content', 'blob 3, a zero byte, then the content', 'The file name', 'The content plus the date'], 1, 'Header first.', 'type, space, decimal size, NUL, content.')

K.calc('e', 'A SHA-1 id is stored as .git/objects/ce/0136... How many characters long is the file name inside the ce folder?', '38', '40 minus the folder.',
       ['The id has 40 hex digits.', 'The first 2 name the folder.', eq('40 - 2 = 38')], check=38)
K.calc('e', 'What is the size field in the header of a blob holding "hello" plus a newline?', '6', 'Count bytes.',
       ['h e l l o is 5 bytes.', 'The newline is 1 byte.', eq('5 + 1 = 6, header "blob 6"')], check=6)
K.calc('m', 'How many bits does a SHA-256 id have, and how many hex digits? Give the number of hex digits.', '64', '4 bits per hex digit.',
       ['SHA-256 produces 256 bits.', 'Each hex digit carries 4 bits.', eq('256 / 4 = 64 digits')], check=64)
K.calc('m', 'Total length in bytes of what Git hashes for a blob with content hello plus a newline: "blob 6", a zero byte, then the content.', '13', 'Header plus NUL plus content.',
       ['"blob 6" is 6 bytes.', 'The zero byte is 1.', eq('6 + 1 + 6 = 13 bytes')], check=13)
K.calc('h', 'A repository has 3 commits. Each commit has 1 tree with 2 files. Commit 2 changed one file, commit 3 changed nothing but the message. How many distinct blobs exist?', '3', 'Unchanged files reuse blobs.',
       ['Commit 1: 2 new blobs.', 'Commit 2: 1 changed file gives 1 new blob.', eq('Commit 3: 0 new, total 3 blobs')], check=3)
K.calc('h', 'Same repository: how many distinct tree objects exist?', '2', 'Same content, same tree.',
       ['Commit 1 has tree T1.', 'Commit 2 changed a file, so tree T2.', eq('Commit 3 reuses T2: 2 trees')], check=2)

K.assign('blob', 'e', 'Compute a blob id',
         '<p>Write <code>blob_id(text)</code> that returns the SHA-1 object id Git gives a file with this text (UTF-8). Remember the header <code>blob &lt;size in bytes&gt;</code> and a zero byte.</p>',
         '''
import hashlib

def blob_id(text):
    # your code here
    pass
''', [("blob_id('hello\\n')", 'ce013625030ba8dba906f756967f9e9ca394464a'), ("blob_id('')", 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'),
      ("len(blob_id('anything'))", 40)],
         '''
import hashlib

def blob_id(text):
    data = text.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\\0' + data).hexdigest()
''', 'Hash the header and the bytes together, not the text alone. The size counts bytes, not characters.', '<p>e69de29b is the id of the empty file in every Git repository in the world.</p>')
K.assign('commitid', 'h', 'Build a commit object by hand',
         '<p>Write <code>commit_id(tree, parents, who, when, msg)</code>. The commit body is the line <code>tree &lt;id&gt;</code>, one <code>parent &lt;id&gt;</code> line per parent, <code>author &lt;who&gt; &lt;when&gt;</code>, <code>committer &lt;who&gt; &lt;when&gt;</code>, an empty line, then the message and a newline. Hash it with the header <code>commit &lt;size&gt;</code> and a zero byte.</p>',
         '''
import hashlib

def commit_id(tree, parents, who, when, msg):
    # your code here
    pass
''', [("commit_id('aaa96ced2d9a1c8e72c56b253a0e2fe78393feb7', [], 'Asha Rao <asha@example.com>', '1793593800 +0530', 'First commit')", '0f2f6da1b1026e7464d4051044863d17b1aaf7e6'),
      ("commit_id('d8eb32556d83f17872e22d74297ea10c82735246', ['0f2f6da1b1026e7464d4051044863d17b1aaf7e6'], 'Asha Rao <asha@example.com>', '1793593800 +0530', 'Second')", 'aa1cc961b5f90c399a85465ec3ca67ad215a0b47')],
         '''
import hashlib

def commit_id(tree, parents, who, when, msg):
    lines = ['tree ' + tree] + ['parent ' + p for p in parents]
    lines += ['author ' + who + ' ' + when, 'committer ' + who + ' ' + when, '', msg]
    body = ('\\n'.join(lines) + '\\n').encode('utf-8')
    return hashlib.sha1(b'commit ' + str(len(body)).encode() + b'\\0' + body).hexdigest()
''', 'Join the lines with newlines, end with one newline, then hash with the commit header.', '<p>These are the real ids from the chapter: your function reproduces what git commit wrote.</p>')

K.must('Four objects', 'blob (content), tree (names, modes, ids), commit (tree, parents, author, committer, message), annotated tag (object, type, name, tagger, message).')
K.must('Object id', 'SHA-1 of the type, a space, the size, a zero byte and the content. 40 hex digits (SHA-256: 64). Stored zlib compressed at .git/objects/xx/rest.')
K.must('Plumbing to inspect', 'git hash-object [-w], git cat-file -t, -s, -p, git rev-parse. Tree modes: 100644 file, 100755 executable, 120000 symlink, 040000 tree, 160000 submodule.')
K.must('Merkle chain', 'Commit ids depend on every file and every parent, so changing history changes every later id. Identical content is stored once.')
K.must('SHA-1 and SHA-256', 'SHAttered 2017, SHA-1DC since Git 2.13, --object-format=sha256 since 2.29, planned default in Git 3.0.')

T = K.topic(
    slug='objects', topic='objects', step=(5, 'Git internals', 'git-internals', 'Open the .git folder: the four object types, how ids are computed, refs, the index, packfiles and garbage collection, and the plumbing commands that porcelain is built on.', 'Advanced'),
    title='Inside .git: blobs, trees, commits and tags', short='Git objects', badge='5.1', minutes=50, added='2026-11-02',
    lead='Every Git command is built on a tiny database of four object types, each named by a hash of its content. Learn to compute an id yourself and see why history cannot be changed without everyone noticing.',
    desc='blob, tree, commit and annotated tag objects, the type and size header, SHA-1 ids, zlib storage in .git/objects, git hash-object and cat-file, tree modes, deduplication, the Merkle structure, the SHAttered collision, SHA-1DC and the SHA-256 object format.',
    summary='The four object types, how ids are computed and stored, tree modes, Merkle integrity and the move to SHA-256.',
    keywords=['blob', 'tree', 'commit object', 'hash-object', 'cat-file', 'object id', 'merkle', 'sha-256'],
    recap='<p>Git is a content addressed store of blobs, trees, commits and tags. An id is the hash of a header plus content, so one commit id vouches for all the history below it.</p>')
