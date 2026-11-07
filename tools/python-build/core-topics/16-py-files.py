# Core Python 5.3: files. Follows PCAP-31-03 section 4 (files: I/O streams, open() modes, text and binary files,
# read(), readline(), readlines(), write(), writelines(), bytearray and readinto(), close(), the errno variable and
# its values, stdin, stdout and stderr), checked against the Python 3.14 tutorial section 7.2 "Reading and Writing
# Files", the io, os, pathlib, errno, csv and json documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('py-files')
K = Kit()

K.code('write', r'''
import os, tempfile
os.chdir(tempfile.mkdtemp())          # work in an empty folder made for this demo

f = open("shopping.txt", "w", encoding="utf-8")
f.write("milk\n")                      # write() does not add a new line by itself
f.write("eggs\n")
f.writelines(["rice\n", "tea\n"])      # nor does writelines()
print("bread", file=f)                 # print() adds the new line
f.close()

print(open("shopping.txt", encoding="utf-8").read())
print(os.path.getsize("shopping.txt"), "bytes")
''')

K.code('read', r'''
import os, tempfile
os.chdir(tempfile.mkdtemp())
with open("marks.txt", "w", encoding="utf-8") as f:
    f.write("Asha 88\nRavi 72\nMeera 95\n")

with open("marks.txt", encoding="utf-8") as f:   # "r" (read text) is the default mode
    print(repr(f.read()))                         # everything as one string

with open("marks.txt", encoding="utf-8") as f:
    print(repr(f.readline()))                     # one line, with its new line
    print(f.readlines())                          # the remaining lines as a list

total = 0
with open("marks.txt", encoding="utf-8") as f:
    for line in f:                                # best: one line at a time
        name, mark = line.split()
        total += int(mark)
print("total", total)
''')

K.code('modes', r'''
import os, tempfile
os.chdir(tempfile.mkdtemp())

with open("log.txt", "w") as f:      # w: create or empty
    f.write("start\n")
with open("log.txt", "a") as f:      # a: add to the end
    f.write("more\n")
print(open("log.txt").read().splitlines())

with open("log.txt", "w") as f:      # w again: the old text is gone
    f.write("fresh\n")
print(open("log.txt").read().splitlines())

try:
    open("log.txt", "x")             # x: create, but only if it does not exist
except FileExistsError as err:
    print("FileExistsError:", err.strerror)

with open("log.txt", "r+") as f:     # r+: read and write, no emptying
    f.write("FR")                    # overwrites the first two characters
print(open("log.txt").read().splitlines())
''')

K.code('with', r'''
import os, tempfile
os.chdir(tempfile.mkdtemp())

with open("a.txt", "w") as f:
    f.write("hello")
    print("inside, closed?", f.closed)
print("after, closed?", f.closed)       # with closed it, even if an error had happened

with open("a.txt") as src, open("b.txt", "w") as dst:   # two files in one with
    dst.write(src.read().upper())
print(open("b.txt").read())
''')

K.code('binary', r'''
import os, tempfile
os.chdir(tempfile.mkdtemp())

data = bytes([137, 80, 78, 71, 13, 10, 26, 10])   # the first 8 bytes of every PNG image
with open("fake.png", "wb") as f:                 # b: binary, no encoding, no new line changes
    f.write(data)

with open("fake.png", "rb") as f:
    head = f.read(4)
print(head, list(head), head[1:4].decode("ascii"))

buffer = bytearray(8)                             # a changeable block of bytes
with open("fake.png", "rb") as f:
    count = f.readinto(buffer)                    # fill it straight from the file
print(count, buffer[:4])

with open("fake.png", "rb") as f:
    f.seek(4)                                     # jump to byte 4
    print(f.tell(), f.read(2))
''')

K.code('encoding', r'''
import os, tempfile
os.chdir(tempfile.mkdtemp())

with open("greet.txt", "w", encoding="utf-8") as f:
    f.write("नमस्ते ₹100 café\n")
print(os.path.getsize("greet.txt"), "bytes for", len("नमस्ते ₹100 café\n"), "characters")

print(open("greet.txt", encoding="utf-8").read().strip())
try:
    open("greet.txt", encoding="ascii").read()
except UnicodeDecodeError as err:
    print("UnicodeDecodeError:", err.reason)
print(open("greet.txt", encoding="ascii", errors="replace").read().strip()[:12])
''')

K.code('errors', r'''
import errno, os

try:
    open("no_such_file.txt")
except FileNotFoundError as err:
    print(type(err).__name__, err.errno, err.strerror, err.filename)
    print(err.errno == errno.ENOENT, isinstance(err, OSError))

try:
    open("no_such_file.txt")
except OSError as err:                     # the parent of every file error
    if err.errno == errno.ENOENT:
        print("not found:", os.strerror(err.errno))
    elif err.errno == errno.EACCES:
        print("no permission")
''')

K.code('paths', r'''
from pathlib import Path
import tempfile

base = Path(tempfile.mkdtemp())
folder = base / "reports" / "2026"           # / joins path parts on every system
folder.mkdir(parents=True, exist_ok=True)
(folder / "jan.csv").write_text("a,b\n1,2\n", encoding="utf-8")
(folder / "feb.csv").write_text("a,b\n3,4\n", encoding="utf-8")
(folder / "notes.txt").write_text("hi", encoding="utf-8")

p = folder / "jan.csv"
print(p.name, p.stem, p.suffix, p.parent.name)
print(p.exists(), p.is_file(), folder.is_dir())
print(sorted(f.name for f in folder.glob("*.csv")))
print(p.read_text(encoding="utf-8").splitlines())
p.rename(folder / "january.csv")
print(sorted(f.name for f in folder.iterdir()))
''')

K.code('osmod', r'''
import os, shutil, tempfile
os.chdir(tempfile.mkdtemp())

os.makedirs("photos/2026/trip", exist_ok=True)
for name in ["a.jpg", "b.jpg", "c.txt"]:
    open(os.path.join("photos", "2026", "trip", name), "w").close()

print(sorted(os.listdir("photos/2026/trip")))
for folder, subfolders, names in os.walk("photos"):
    print(folder.replace(os.sep, "/"), subfolders, sorted(names))

os.remove("photos/2026/trip/c.txt")
os.rename("photos/2026/trip/a.jpg", "photos/2026/trip/beach.jpg")
print(sorted(os.listdir("photos/2026/trip")))
shutil.rmtree("photos")                 # delete a whole folder tree: be careful!
print(os.path.exists("photos"))
''')

K.code('streams', r'''
import sys

sys.stdout.write("stdout: normal output\n")      # print() writes here
print("errors belong on stderr", file=sys.stderr)  # shown in red in many terminals
print(sys.stdin.readable(), sys.stdout.writable())
print(type(sys.stdout).__name__)
''')

K.code('csvjson', r'''
import csv, json, os, tempfile
os.chdir(tempfile.mkdtemp())

rows = [{"name": "Asha", "city": "Pune", "mark": 88}, {"name": "Ravi, Jr", "city": "Delhi", "mark": 72}]
with open("students.csv", "w", newline="", encoding="utf-8") as f:   # newline="" for csv
    writer = csv.DictWriter(f, fieldnames=["name", "city", "mark"])
    writer.writeheader()
    writer.writerows(rows)
print(open("students.csv", encoding="utf-8").read())

with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"], int(row["mark"]) + 5)

with open("students.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)
with open("students.json", encoding="utf-8") as f:
    back = json.load(f)
print(back == rows, back[1]["name"])
''')

K.lesson('idea', 'Files: data that lasts', f'''
{src('Python 3.14 tutorial section 7.2, the io, os, pathlib, errno, csv and json documentation, and PCAP-31-03 section 4.')}
{wwh('A <b>file</b> is named data stored on a disk. Python reaches it through a <b>file object</b> (a stream) that open() gives you. Text files hold characters, binary files hold raw bytes.',
     'Variables vanish when a program ends. Files keep data between runs: settings, saved games, reports, logs, photos. They are also how programs exchange data, as CSV, JSON or plain text.',
     'open(name, mode) connects to the file and returns a file object with a <b>cursor</b>. read and write work at the cursor and move it on. close() (or the end of a with block) saves everything and frees the file. In text mode Python decodes bytes to str with an encoding such as UTF-8.')}
{scene('a notebook and a bookmark', '<p>Opening a notebook to read puts a bookmark at page 1. Each page you read moves the bookmark forward. Opening it to write a fresh story ("w") tears out every old page first. Opening it to add notes ("a") turns to the last page. Closing the notebook puts it back on the shelf. The bookmark is the file cursor.</p>')}
{run('write')}
{note('All the programs in this chapter first move into a new empty temporary folder with tempfile.mkdtemp(), so they never touch your own files. Drop that line when you work in your project folder.', 'tip')}
''', kw=['file', 'open', 'file object', 'stream', 'write', 'text file', 'binary file'])

K.lesson('read', 'Reading a text file', f'''
{run('read')}
{table(['Method', 'Returns', 'At the end of the file'], [
    ['read()', 'The rest of the file as one str', '""'],
    ['read(n)', 'Up to n characters', '""'],
    ['readline()', 'One line, including its new line character', '""'],
    ['readlines()', 'A list of all remaining lines', '[]'],
    ['for line in f', 'One line per turn, without loading the whole file', 'The loop ends']])}
{note('Lines keep their new line character. Use line.strip() or line.rstrip("&#92;n") before you compare or split them. For big files loop with for line in f, which reads one line at a time instead of loading gigabytes into memory.', 'exam')}
''', kw=['read', 'readline', 'readlines', 'iterate file', 'new line', 'strip'])

K.lesson('modes', 'Open modes', f'''
{viz('pyfile')}
{run('modes')}
{table(['Mode', 'Read', 'Write', 'File must exist', 'Empties the file', 'Cursor starts'], [
    ['r (default)', 'Yes', 'No', 'Yes (else FileNotFoundError)', 'No', 'Start'],
    ['w', 'No', 'Yes', 'No, it is created', '<b>Yes</b>', 'Start'],
    ['a', 'No', 'Yes, always at the end', 'No, it is created', 'No', 'End'],
    ['x', 'No', 'Yes', 'Must NOT exist (else FileExistsError)', 'New file', 'Start'],
    ['r+', 'Yes', 'Yes', 'Yes', 'No', 'Start'],
    ['w+', 'Yes', 'Yes', 'No', '<b>Yes</b>', 'Start'],
    ['a+', 'Yes', 'Yes, at the end', 'No', 'No', 'End']])}
{note('Add t (text, the default) or b (binary) to any mode: "rb", "wb", "ab", "r+b". The most common accident is opening a file with "w" when you meant "a": the old contents are gone at once.', 'warn')}
''', kw=['open modes', 'r', 'w', 'a', 'x', 'r+', 'w+', 'text mode', 'binary mode', 'truncate'])

K.lesson('with', 'Always use with', f'''
{run('with')}
{versus('Closing files', ['', 'f = open(...) then f.close()', 'with open(...) as f:'], [
    ['If an exception happens in between', 'close() is skipped, the file may stay open and data may not be saved', 'The file is closed anyway'],
    ['If you forget close()', 'Data may sit in a buffer and never reach the disk', 'Not possible'],
    ['Lines of code', 'More, plus try and finally to be safe', 'Fewer']],
    'open files with with every time. It is try and finally in one line.')}
''', kw=['with statement', 'close', 'context manager', 'buffer', 'flush'])

K.lesson('binary', 'Binary files, bytes and bytearray', f'''
{run('binary')}
{versus('Text mode or binary mode', ['', 'text ("r", "w")', 'binary ("rb", "wb")'], [
    ['read() returns', 'str', 'bytes'],
    ['write() takes', 'str', 'bytes or bytearray'],
    ['Encoding', 'Decodes and encodes (say encoding="utf-8")', 'None, raw bytes'],
    ['New line characters', 'Changed to and from the system style', 'Never changed'],
    ['Use for', 'Text, CSV, JSON, code', 'Images, audio, zip, PDF, anything not text']],
    'use text mode for human readable text, and binary mode for everything else, or when you must copy a file byte for byte.')}
''', kw=['binary file', 'bytes', 'bytearray', 'readinto', 'rb', 'wb', 'seek', 'tell', 'magic number'])

K.lesson('encoding', 'Encodings: always say utf-8', f'''
{run('encoding')}
{note('Without encoding=..., open() uses a default that depends on the computer. It is UTF-8 on Linux and macOS but can be an old code page on Windows, so a file written on one computer may not read on another. Since Python 3.15 the default becomes UTF-8 everywhere (PEP 686), but writing encoding="utf-8" is still the safe habit.', 'warn')}
''', kw=['encoding', 'utf-8', 'UnicodeDecodeError', 'errors replace', 'PEP 686', 'locale'])

K.lesson('errors', 'File errors and errno', f'''
{run('errors')}
{table(['Exception (all are OSError)', 'errno name', 'When'], [
    ['FileNotFoundError', 'ENOENT', 'The file or folder does not exist'],
    ['FileExistsError', 'EEXIST', 'Mode "x" or mkdir on something that exists'],
    ['PermissionError', 'EACCES or EPERM', 'Not allowed to read or write it'],
    ['IsADirectoryError', 'EISDIR', 'open() on a folder'],
    ['NotADirectoryError', 'ENOTDIR', 'A path part is a file, not a folder'],
    ['OSError with ENOSPC', 'ENOSPC', 'The disk is full']])}
''', kw=['FileNotFoundError', 'PermissionError', 'OSError', 'errno', 'ENOENT', 'strerror'])

K.lesson('paths', 'Paths with pathlib', f'''
{run('paths')}
{versus('Two ways to work with paths', ['', 'os.path (strings)', 'pathlib.Path (objects)'], [
    ['Join', 'os.path.join("a", "b.txt")', 'Path("a") / "b.txt"'],
    ['Parts', 'os.path.basename, splitext', 'p.name, p.stem, p.suffix, p.parent'],
    ['Read and write', 'open(...) then read()', 'p.read_text(), p.write_text()'],
    ['Find files', 'glob.glob("*.csv")', 'p.glob("*.csv"), p.rglob("*.csv")'],
    ['Style', 'Older, everywhere in old code', 'Modern, clearer']],
    'use pathlib in new code. Both work on Windows, macOS and Linux, which use different separators.')}
''', kw=['pathlib', 'Path', 'os.path', 'glob', 'mkdir', 'suffix', 'stem', 'cross platform paths'])

K.lesson('osmod', 'Folders with os and shutil', f'''
{run('osmod')}
{note('os.remove, os.rename and shutil.rmtree do not use a recycle bin: deleted files are gone. Print the paths and check them before you delete anything in a loop.', 'warn')}
''', kw=['os module', 'listdir', 'walk', 'makedirs', 'remove', 'rename', 'shutil', 'rmtree'])

K.lesson('streams', 'stdin, stdout and stderr', f'''
{run('streams')}
{table(['Stream', 'Python name', 'Used by'], [
    ['Standard input', 'sys.stdin', 'input() reads from it'],
    ['Standard output', 'sys.stdout', 'print() writes to it'],
    ['Standard error', 'sys.stderr', 'Tracebacks and warnings, print(..., file=sys.stderr)']])}
{note('The page shows only stdout, so the stderr line above is not in the output. In a terminal both appear, but they are separate streams: python3 app.py &gt; out.txt saves only stdout and still shows errors on the screen.', 'tip')}
''', kw=['stdin', 'stdout', 'stderr', 'sys', 'redirect', 'streams'])

K.lesson('csvjson', 'CSV and JSON files', f'''
{run('csvjson')}
{note('Never split CSV lines with line.split(","). A value like "Ravi, Jr" contains a comma and is stored in quotes. The csv module handles quotes, commas and new lines inside values correctly. Advanced 6.2 covers csv, json, xml and sqlite3 in depth.', 'warn')}
''', kw=['csv', 'DictReader', 'DictWriter', 'json.dump', 'json.load', 'newline'])

K.lesson('maths', 'Sizes, bytes and cursors', f'''
{fxs(fx('File size in bytes of an ASCII text', 'sum of len(line) for all lines, new lines included', '"milk&#92;n" is 5 bytes. On Windows a text file stores each new line as 2 bytes (&#92;r&#92;n).', key=True),
     fx('UTF-8 size', '1 byte for code points 0 to 127, 2 up to 2,047, 3 up to 65,535, 4 above', '"नमस्ते ₹100 café&#92;n" has 16 characters but 31 bytes.', key=True),
     fx('Units', '1 KB = 1,000 bytes, 1 KiB = 1,024 bytes', 'Disks are sold in KB, MB, GB (powers of 10). Operating systems often show KiB, MiB, GiB (powers of 2).'),
     fx('Cursor after a read in text mode (ASCII)', 'new position = old position + characters read', 'In binary mode tell() is always a byte offset. In text mode it is an opaque number, so only seek() to values that tell() gave you.'),
     fx('Lines in memory', 'readlines(): O(file size). for line in f: O(longest line)', 'A 10 GB log can be processed with a for loop on a laptop with 8 GB of memory.'))}
{steps('Worked example: size of the shopping file', [
    'Lines: "milk&#92;n", "eggs&#92;n", "rice&#92;n", "tea&#92;n", "bread&#92;n".',
    'Lengths: 5, 5, 5, 4, 6.',
    eq('5 + 5 + 5 + 4 + 6 = 25 bytes, which is what os.path.getsize printed')])}
''', kw=['file size', 'bytes', 'UTF-8 size', 'KB vs KiB', 'memory', 'cursor'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>open a file with "w" to write and "r" to read, and use with so it closes itself.</p>',
    '<p>Know every mode, read with read, readline, readlines and a for loop, write with write and writelines, say encoding="utf-8", and catch FileNotFoundError.</p>',
    '<p>Use binary mode for non text data, bytearray and readinto for buffers, pathlib for paths, os and shutil for folders, errno to tell OSErrors apart, and csv and json for structured data.</p>',
    '<p>open() builds a layered stack: a raw FileIO (system calls), a BufferedReader or BufferedWriter (fewer system calls), and a TextIOWrapper (decoding and new line translation). flush() pushes the buffer to the operating system, and os.fsync() asks it to write to the disk. Writing to a temporary file and then os.replace() makes saving atomic, so a crash never leaves a half written file.</p>')}
{grow('Write and read a text file with with and a for loop.',
      'Choose the right mode, handle file errors, use encodings, binary files, pathlib and csv.',
      'Explain the io layers and buffering, write files atomically, and process files bigger than memory.')}
''', kw=['beginner', 'expert', 'io layers', 'buffering', 'fsync', 'atomic write', 'os.replace'])

lc(1816, 'Truncate Sentence', 'truncate-sentence', 'e', 'split and join', 'Split on spaces, keep the first k words, join them again.', r'''
def truncate_sentence(s, k):
    return " ".join(s.split()[:k])
''', [('truncate_sentence("Hello how are you Contestant", 4)', 'Hello how are you'), ('truncate_sentence("chopper is not a tanuki", 5)', 'chopper is not a tanuki')])
lc(819, 'Most Common Word', 'most-common-word', 'e', 'Clean text, count words', 'Turn every non letter into a space, lower case everything, count the words that are not banned and take the most common.', r'''
def most_common_word(paragraph, banned):
    clean = ""
    for ch in paragraph:
        if ch.isalpha():
            clean = clean + ch.lower()
        else:
            clean = clean + " "
    banned_set = set(banned)
    counts = {}
    for word in clean.split():
        if word not in banned_set:
            counts[word] = counts.get(word, 0) + 1
    return max(counts, key=counts.get)
''', [('most_common_word("Bob hit a ball, the hit BALL flew far after it was hit.", ["hit"])', 'ball'), ('most_common_word("a.", [])', 'a')])
lc(884, 'Uncommon Words from Two Sentences', 'uncommon-words-from-two-sentences', 'e', 'Count words of both texts', 'A word is uncommon if it appears exactly once in the two sentences together.', r'''
def uncommon_from_sentences(s1, s2):
    counts = {}
    for word in (s1 + " " + s2).split():
        counts[word] = counts.get(word, 0) + 1
    return [w for w in counts if counts[w] == 1]
''', [('sorted(uncommon_from_sentences("this apple is sweet", "this apple is sour"))', ['sour', 'sweet']), ('uncommon_from_sentences("apple apple", "banana")', ['banana'])])
lc(1592, 'Rearrange Spaces Between Words', 'rearrange-spaces-between-words', 'e', 'Count spaces, divide', 'Count the spaces and words. Put spaces // (words &minus; 1) between words and the rest at the end.', r'''
def reorder_spaces(text):
    spaces = text.count(" ")
    words = text.split()
    if len(words) == 1:
        return words[0] + " " * spaces
    gap = spaces // (len(words) - 1)
    extra = spaces % (len(words) - 1)
    return (" " * gap).join(words) + " " * extra
''', [('reorder_spaces("  this   is  a sentence ")', 'this   is   a   sentence'), ('reorder_spaces(" practice   makes   perfect")', 'practice   makes   perfect '), ('reorder_spaces("  hello")', 'hello  ')])
lc(2042, 'Check if Numbers Are Ascending in a Sentence', 'check-if-numbers-are-ascending-in-a-sentence', 'e', 'Parse tokens', 'Split into tokens. Every token made of digits must be bigger than the previous number.', r'''
def are_numbers_ascending(s):
    last = -1
    for token in s.split():
        if token.isdigit():
            if int(token) <= last:
                return False
            last = int(token)
    return True
''', [('are_numbers_ascending("1 box has 3 blue 4 red 6 green and 12 yellow marbles")', True), ('are_numbers_ascending("hello world 5 x 5")', False)])
lc(609, 'Find Duplicate File in System', 'find-duplicate-file-in-system', 'm', 'Group paths by content', 'Each entry is "folder name(content) ...". Group full paths by content in a dict and keep groups with more than one path.', r'''
def find_duplicate(paths):
    groups = {}
    for entry in paths:
        parts = entry.split()
        folder = parts[0]
        for item in parts[1:]:
            name, rest = item.split("(")
            content = rest[:-1]
            if content not in groups:
                groups[content] = []
            groups[content].append(folder + "/" + name)
    return [g for g in groups.values() if len(g) > 1]
''', [('sorted(sorted(g) for g in find_duplicate(["root/a 1.txt(abcd) 2.txt(efgh)", "root/c 3.txt(abcd)", "root/c/d 4.txt(efgh)", "root 4.txt(efgh)"]))', [['root/4.txt', 'root/a/2.txt', 'root/c/d/4.txt'], ['root/a/1.txt', 'root/c/3.txt']])])
lc(388, 'Longest Absolute File Path', 'longest-absolute-file-path', 'm', 'Depth by tabs, a stack of lengths', 'Split into lines. The number of tabs is the depth. Keep the path length at each depth. A name with a dot is a file.', r'''
def length_longest_path(text):
    best = 0
    length_at = {0: 0}
    for line in text.split("\n"):
        name = line.lstrip("\t")
        depth = len(line) - len(name)
        if "." in name:
            best = max(best, length_at[depth] + len(name))
        else:
            length_at[depth + 1] = length_at[depth] + len(name) + 1
    return best
''', [('length_longest_path("dir\\n\\tsubdir1\\n\\tsubdir2\\n\\t\\tfile.ext")', 20), ('length_longest_path("a")', 0), ('length_longest_path("file1.txt\\nfile2.txt\\nlongfile.txt")', 12)])
lc(1233, 'Remove Sub-Folders from the Filesystem', 'remove-sub-folders-from-the-filesystem', 'm', 'Sort, then compare with the last kept folder', 'After sorting, a sub folder comes right after its parent. Keep a folder unless it starts with the last kept folder plus "/".', r'''
def remove_subfolders(folder):
    result = []
    for f in sorted(folder):
        if not result or not f.startswith(result[-1] + "/"):
            result.append(f)
    return result
''', [('remove_subfolders(["/a", "/a/b", "/c/d", "/c/d/e", "/c/f"])', ['/a', '/c/d', '/c/f']), ('remove_subfolders(["/a/b/c", "/a/b/ca", "/a/b/d"])', ['/a/b/c', '/a/b/ca', '/a/b/d'])])
lc(1047, 'Remove All Adjacent Duplicates In String', 'remove-all-adjacent-duplicates-in-string', 'e', 'Stack', 'Push each character. If it equals the top of the stack, pop instead.', r'''
def remove_duplicates_text(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)
''', [('remove_duplicates_text("abbaca")', 'ca'), ('remove_duplicates_text("azxxzy")', 'ay')])
lc(68, 'Text Justification', 'text-justification', 'h', 'Greedy lines, spread spaces', 'Fill each line with as many words as fit. Spread the spaces, giving the left gaps one extra when they do not divide evenly. The last line is left aligned.', r'''
def full_justify(words, max_width):
    lines = []
    i = 0
    while i < len(words):
        j = i
        width = 0
        while j < len(words) and width + len(words[j]) + (j - i) <= max_width:
            width = width + len(words[j])
            j = j + 1
        gaps = j - i - 1
        if j == len(words) or gaps == 0:
            line = " ".join(words[i:j])
            line = line + " " * (max_width - len(line))
        else:
            spaces = max_width - width
            line = ""
            for k in range(i, j - 1):
                extra = 1 if (k - i) < spaces % gaps else 0
                line = line + words[k] + " " * (spaces // gaps + extra)
            line = line + words[j - 1]
        lines.append(line)
        i = j
    return lines
''', [('full_justify(["This", "is", "an", "example", "of", "text", "justification."], 16)', ['This    is    an', 'example  of text', 'justification.  ']), ('full_justify(["What", "must", "be", "acknowledgment", "shall", "be"], 16)', ['What   must   be', 'acknowledgment  ', 'shall be        '])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Files are mostly text, folders and paths. These problems practise exactly that: cleaning and counting words, parsing tokens, grouping files by content and working with folder paths.</p>'), kw=['LeetCode', 'text processing', 'file paths', 'duplicate files', 'text justification', 'most common word'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'open(name, mode, encoding="utf-8") returns a file object with a cursor. Always use <b>with</b> so it closes.',
    'Modes: r read (must exist), w write (empties), a append, x create new only, + adds the other direction, b for binary.',
    'read(), read(n), readline(), readlines(), and for line in f, which is best for big files. Lines keep their new line.',
    'write() and writelines() do not add new lines. print(..., file=f) does.',
    'Binary mode reads and writes bytes. bytearray and readinto fill a buffer. seek and tell move and report the cursor.',
    'File errors are OSErrors: FileNotFoundError, FileExistsError, PermissionError. err.errno matches errno.ENOENT and friends.',
    'pathlib.Path joins with /, and has name, suffix, glob, read_text and write_text. os and shutil handle folders.',
    'sys.stdin, sys.stdout, sys.stderr are the standard streams. Use csv and json for structured files.'],
    'Step 6 starts object oriented programming: classes, objects, attributes and methods.')}
{files('Three tasks: count words in a file, append a log line with a time stamp, and copy a file in fixed size chunks.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which mode opens a file for reading only?', ['"w"', '"r"', '"a"', '"x"'], 1, 'Read.', '"r" is read, and it is the default.')
K.quiz('e', 'What does mode "w" do to an existing file?', ['Adds to the end', 'Empties it first', 'Raises an error', 'Nothing'], 1, 'Write fresh.', '"w" truncates the file to zero length.')
K.quiz('e', 'Why use with open(...) as f?', ['It is faster', 'It closes the file for you', 'It reads the whole file', 'It makes a backup'], 1, 'Cleanup.', 'with closes the file even if an error happens.')
K.quiz('m', 'What does f.readline() return at the end of the file?', ['None', '""', '"&#92;n"', 'EOFError'], 1, 'Empty text.', 'At the end it returns the empty string.')
K.quiz('m', 'f.write("hi") then f.write("there"). What is in the file?', ['hi there', 'hithere', 'hi then there on two lines', 'there'], 1, 'No automatic new line.', 'write adds exactly what you give it.')
K.quiz('m', 'Which mode raises FileExistsError if the file is already there?', ['"w"', '"a"', '"x"', '"r+"'], 2, 'Exclusive.', '"x" only creates new files.')
K.quiz('m', 'In "rb" mode, what type does read() return?', ['str', 'bytes', 'bytearray', 'list'], 1, 'Binary.', 'Binary mode reads bytes.')
K.quiz('m', 'Which exception is the parent of FileNotFoundError?', ['ValueError', 'OSError', 'LookupError', 'EOFError'], 1, 'Operating system.', 'All file errors are OSErrors (IOError is another name for OSError).')
K.quiz('h', 'A file holds "ab&#92;ncd". After f.read(1) and f.readline(), where is the cursor?', ['1', '2', '3', '5'], 2, 'readline takes the rest of the line with its new line.', 'read(1) gives "a" (cursor 1), readline gives "b&#92;n" (cursor 3).')
K.quiz('h', 'Which is best for a 20 GB log file?', ['f.read()', 'f.readlines()', 'for line in f', 'list(f)'], 2, 'Memory.', 'Only the for loop keeps one line in memory at a time.')
K.quiz('h', 'err.errno == errno.ENOENT means', ['No permission', 'No such file or directory', 'Disk full', 'File exists'], 1, 'Error NO ENTry.', 'ENOENT is the code for a missing file or folder.')
K.quiz('x', 'In the style of a CMU 15-213 exam: a program writes to a file without closing it and then the computer loses power. What can be lost?', ['Nothing, write() saves at once', 'Data still in the buffer', 'Only the file name', 'The whole disk'], 1, 'Buffers.', 'write() fills a buffer in memory. Without close, flush or fsync, the last data may never reach the disk.')
K.quiz('x', 'In the style of an MIT 6.033 question: why write a new version to a temp file and then os.replace(tmp, real)?', ['It is faster', 'Readers see either the whole old file or the whole new file, never half', 'It compresses the file', 'It avoids encodings'], 1, 'Atomic rename.', 'os.replace is atomic on the same file system, so a crash cannot leave a half written file.')

K.calc('e', 'Bytes in a file with the lines "milk&#92;n", "eggs&#92;n", "rice&#92;n", "tea&#92;n", "bread&#92;n".', '25', 'Count the new lines too.', ['5 + 5 + 5 + 4 + 6.', 'Each new line is 1 byte on Linux.', eq('25')], check=25)
K.calc('e', 'len("Asha 88&#92;nRavi 72&#92;n".splitlines())?', '2', 'Two lines.', ['splitlines splits at new lines.', 'Two lines.', eq('2')], check=2)
K.calc('e', 'Total of the marks 88, 72 and 95 read from marks.txt.', '255', 'Add them.', ['88 + 72 = 160.', '160 + 95.', eq('255')], check=255)
K.calc('m', 'UTF-8 bytes of "café&#92;n".', '6', 'é is 2 bytes.', ['c, a, f: 3 bytes.', 'é: 2, new line: 1.', eq('6')], check=len('café\n'.encode()))
K.calc('m', 'How many KiB is 1 MiB?', '1024', '2<sup>10</sup>.', ['1 MiB = 2<sup>20</sup> bytes.', '1 KiB = 2<sup>10</sup> bytes.', eq('1024')], check=1024)
K.calc('m', 'A file holds "hello world". After f.seek(6) and f.read(3), what is f.tell() (binary mode)?', '9', '6 + 3.', ['seek(6) puts the cursor at 6.', 'read(3) moves it 3 on.', eq('9')], check=9)
K.calc('m', 'Bytes in 1 GB minus bytes in 1 GiB, in millions (whole number, rounded down).', '73', '2<sup>30</sup> &minus; 10<sup>9</sup>.', ['2<sup>30</sup> = 1,073,741,824.', 'Minus 1,000,000,000 = 73,741,824.', eq('73 million (1 GiB is the bigger one)')], check=(2 ** 30 - 10 ** 9) // 10 ** 6)
K.calc('h', 'A Windows text file has 1,000 lines of 20 characters plus a new line each. How many bytes on disk?', '22000', '&#92;r&#92;n is 2 bytes.', ['Each line: 20 + 2 = 22 bytes.', '1,000 lines.', eq('22,000 bytes')], check=22000)
K.calc('h', 'Chunks needed to copy a 10,000,000 byte file with 65,536 byte chunks.', '153', 'Round up.', ['10,000,000 / 65,536 = 152.6.', 'Round up for the last partial chunk.', eq('153')], check=-(-10_000_000 // 65_536))
K.calc('x', 'In the style of a Stanford CS110 problem: a disk reads 200 MB per second and each read call has 0.1 ms of overhead. How many milliseconds does reading 1,000 MB take with 64 KiB chunks? (Round to a whole number. 1 MB = 10<sup>6</sup> bytes.)', '6526', 'Transfer time plus calls times overhead.', ['Transfer: 1,000 / 200 = 5 s = 5,000 ms.', 'Calls: 10<sup>9</sup> / 65,536 &asymp; 15,259, so overhead &asymp; 1,526 ms.', eq('5,000 + 1,526 = 6,526 ms. Bigger chunks mean fewer calls, which is why buffering matters')], check=round(5000 + (-(-10 ** 9 // 65536)) * 0.1))

K.assign('wc', 'e', 'Count words in a file',
         '<p>Write <code>count_words(path)</code> that opens a UTF-8 text file and returns the number of words (separated by any spaces or new lines). If the file does not exist, return 0. make_file() is a helper for the tests.</p>',
         '''
def count_words(path):
    # your code here
    pass


def make_file(text):
    import tempfile
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name
''', [('count_words(make_file("one two\\nthree"))', 3), ('count_words(make_file(""))', 0), ('count_words("/no/such/file.txt")', 0), ('count_words(make_file("  a  b  \\n\\n c "))', 3)],
         '''
def count_words(path):
    try:
        with open(path, encoding="utf-8") as f:
            total = 0
            for line in f:
                total = total + len(line.split())
            return total
    except FileNotFoundError:
        return 0


def make_file(text):
    import tempfile
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name
''', 'Open with with inside try. Add len(line.split()) for each line. Return 0 in except FileNotFoundError.', '<p>Reading line by line means this works for files of any size. This is what the Unix command wc -w does.</p>')
K.assign('log', 'm', 'Append a log line',
         '<p>Write <code>add_log(path, message, stamp)</code> that adds one line "stamp | message" to the end of the file (creating it if needed) and returns the number of lines the file now has.</p>',
         '''
def add_log(path, message, stamp):
    # your code here
    pass


def new_path():
    import os, tempfile
    return os.path.join(tempfile.mkdtemp(), "app.log")
''', [('(lambda p: (add_log(p, "start", "09:00"), add_log(p, "stop", "17:00")))(new_path())', (1, 2)), ('(lambda p: (add_log(p, "x", "1"), open(p).read()))(new_path())[1]', '1 | x\n')],
         '''
def add_log(path, message, stamp):
    with open(path, "a", encoding="utf-8") as f:
        f.write(stamp + " | " + message + "\\n")
    with open(path, encoding="utf-8") as f:
        count = 0
        for line in f:
            count = count + 1
    return count


def new_path():
    import os, tempfile
    return os.path.join(tempfile.mkdtemp(), "app.log")
''', 'Open with "a" to add the line (with a new line character). Then open again with "r" and count the lines.', '<p>Mode "a" creates the file if it is missing and never overwrites old lines, which is exactly what a log needs.</p>')
K.assign('copy', 'm', 'Copy a file in chunks',
         '<p>Write <code>copy_file(src, dst, chunk=4)</code> that copies any file byte for byte, reading at most chunk bytes at a time in binary mode. Return the number of read calls that returned data.</p>',
         '''
def copy_file(src, dst, chunk=4):
    # your code here
    pass


def make_bin(data):
    import tempfile
    f = tempfile.NamedTemporaryFile("wb", delete=False)
    f.write(data)
    f.close()
    return f.name
''', [('(lambda s: (copy_file(s, s + ".copy"), open(s + ".copy", "rb").read() == bytes(range(10))))(make_bin(bytes(range(10))))', (3, True)), ('copy_file(make_bin(b""), make_bin(b"x"))', 0)],
         '''
def copy_file(src, dst, chunk=4):
    calls = 0
    with open(src, "rb") as a, open(dst, "wb") as b:
        while True:
            block = a.read(chunk)
            if block == b"":
                break
            b.write(block)
            calls = calls + 1
    return calls


def make_bin(data):
    import tempfile
    f = tempfile.NamedTemporaryFile("wb", delete=False)
    f.write(data)
    f.close()
    return f.name
''', 'Open src with "rb" and dst with "wb". Loop: read(chunk), stop at b"", write the block.', '<p>10 bytes in chunks of 4 take 3 reads (4, 4, 2). shutil.copyfile does the same with large chunks.</p>')

K.must('open and with', 'with open(path, mode, encoding="utf-8") as f: closes automatically. Modes r, w (empties), a, x (new only), +, b.')
K.must('Reading', 'read(), read(n), readline() ("" at end), readlines(), for line in f (best for big files). Lines keep their new line.')
K.must('Writing', 'write(s) and writelines(list) add no new lines. print(x, file=f) does. write returns characters written.')
K.must('Binary and cursor', '"rb"/"wb" use bytes. bytearray + readinto. seek(n) moves, tell() reports.')
K.must('Errors and paths', 'OSError family: FileNotFoundError (ENOENT), FileExistsError, PermissionError. pathlib.Path / "x", glob, read_text.')

T = K.topic(
    slug='py-files', topic='py-files', step=(5, 'Errors, modules and files', 'py-c5', 'Handle errors with exceptions, organise code in modules and packages, and read and write files.', 'Intermediate'),
    title='Files: reading, writing, modes, paths and streams', short='Files', badge='5.3', minutes=60,
    lead='Make data last after the program ends. Learn open and with, every open mode, reading line by line, writing, binary files with bytes and bytearray, encodings, file errors and errno, paths with pathlib, folders with os and shutil, the standard streams, and CSV and JSON files.',
    desc='file objects and streams, open() and its modes r, w, a, x, r+, w+, a+, text and binary, read, read(n), readline, readlines, iterating over a file, write, writelines, print to a file, with and close, bytes, bytearray, readinto, seek and tell, encodings and UnicodeDecodeError, OSError, FileNotFoundError, errno and strerror, pathlib, os.listdir, os.walk, shutil, stdin, stdout and stderr, csv and json files, file sizes and buffering.',
    summary='open modes, with, read and write methods, binary files, encodings, errno, pathlib, os and shutil, streams, csv and json.',
    keywords=['files', 'open', 'with', 'read', 'write', 'readline', 'binary', 'bytearray', 'encoding', 'errno', 'pathlib', 'os', 'stdout', 'csv', 'PCAP'],
    recap='<p>Open files with with, choose the mode carefully, read big files line by line, say the encoding, and catch OSError for anything the disk can do wrong.</p>',
    added='2026-11-07', leet=leet_items())
