# Foundations 2.3: Python for security. Checked against the Python 3.14 documentation (str.encode, bytes.hex,
# base64, hashlib including file_digest from 3.11, hmac.compare_digest, re, struct, secrets and PEP 506, random and
# its Mersenne Twister warning, subprocess and the shell=True warning, shlex.quote, posixpath, pickle's security
# warning, tarfile extraction filters from PEP 706), RFC 3629 (UTF-8), RFC 4648 (base64), RFC 1071 (internet
# checksum), RFC 1035 (DNS header), FIPS 180-4 (SHA-256) and Webster and Tavares (1985) on the avalanche criterion.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack
from mlkit import link

chapter('cy-python')
K = Kit()

K.code('text_bytes', r'''
# Text and bytes: what a security tool really reads
import base64

word = "café"
data = word.encode("utf-8")            # text (str) to bytes
print("text      :", word, "has", len(word), "characters")
print("bytes     :", data, "has", len(data), "bytes")
print("hex       :", data.hex())
print("numbers   :", list(data))      # every byte is a number from 0 to 255

bits = ""
for b in data:
    bits = bits + format(b, "08b") + " "
print("bits      :", bits)

encoded = base64.b64encode(data)
print("base64    :", encoded.decode("ascii"))
print("back again:", base64.b64decode(encoded).decode("utf-8"))

# bytes.fromhex reads a hex dump back into bytes
packet = bytes.fromhex("48 54 54 50")
print("from hex  :", packet, "is the text", packet.decode("ascii"))
''')

K.code('hash_demo', r'''
# Hashes: a fixed size fingerprint of any data
import hashlib
import hmac
import io

a = hashlib.sha256(b"pay 100 to Riya").hexdigest()
b = hashlib.sha256(b"pay 900 to Riya").hexdigest()
print("A:", a)
print("B:", b)

def bits_different(hex1, hex2):
    x = int(hex1, 16) ^ int(hex2, 16)    # XOR keeps a 1 where the bits differ
    return bin(x).count("1")

print("bits that differ:", bits_different(a, b), "of 256")

# Hash a big file piece by piece, so even a 50 GB file needs little memory
fake_file = io.BytesIO(b"A" * 100000)     # stands in for open("big.iso", "rb")
h = hashlib.sha256()
pieces = 0
while True:
    chunk = fake_file.read(8192)
    if not chunk:
        break
    h.update(chunk)
    pieces = pieces + 1
print("file read in", pieces, "pieces, hash starts", h.hexdigest()[:16])

# Compare secrets with compare_digest, not ==
published = h.hexdigest()
print("download is genuine:", hmac.compare_digest(published, h.hexdigest()))
print("MD5 is", len(hashlib.md5(b"x").hexdigest()) * 4, "bits and broken: never use it for security")
''', long=True)

K.code('log_regex', r'''
# Find failed SSH logins in a log and count them per address
import re

log = """Nov 14 09:00:01 web1 sshd[811]: Failed password for root from 203.0.113.7 port 51022 ssh2
Nov 14 09:00:03 web1 sshd[811]: Failed password for root from 203.0.113.7 port 51023 ssh2
Nov 14 09:00:04 web1 sshd[812]: Accepted password for riya from 198.51.100.4 port 50110 ssh2
Nov 14 09:00:06 web1 sshd[813]: Failed password for invalid user admin from 203.0.113.7 port 51030 ssh2
Nov 14 09:00:09 web1 sshd[814]: Failed password for amit from 198.51.100.23 port 40001 ssh2
Nov 14 09:00:11 web1 sshd[815]: Failed password for root from 203.0.113.7 port 51041 ssh2
Nov 14 09:00:15 web1 CRON[900]: pam_unix(cron:session): session opened for user root
Nov 14 09:00:20 web1 sshd[816]: Failed password for amit from 198.51.100.23 port 40007 ssh2"""

pattern = re.compile(r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>[\d.]+)")

counts = {}
for line in log.splitlines():
    m = pattern.search(line)
    if m:
        ip = m.group("ip")
        counts[ip] = counts.get(ip, 0) + 1
        print("failed:", m.group("user"), "from", ip)

LIMIT = 3
for ip in counts:
    if counts[ip] >= LIMIT:
        print("BLOCK", ip, "after", counts[ip], "failures")
''', long=True)

K.code('packet_parse', r'''
# Reading binary data with struct: a DNS header and the internet checksum
import struct

# A DNS query header is six 16 bit numbers in network byte order ("!" means big endian)
header = struct.pack("!HHHHHH", 0x1A2B, 0x0100, 1, 0, 0, 0)
print("header bytes:", header.hex(), "=", len(header), "bytes")

ident, flags, questions, answers, authority, extra = struct.unpack("!HHHHHH", header)
print("id", hex(ident), " flags", hex(flags), " questions", questions)
print("recursion desired bit:", (flags >> 8) & 1)

# The internet checksum (RFC 1071), used in IPv4, TCP and UDP headers
def checksum(data):
    total = 0
    for i in range(0, len(data), 2):
        total = total + (data[i] << 8) + data[i + 1]
    while total > 0xFFFF:                       # fold the carries back in
        total = (total & 0xFFFF) + (total >> 16)
    return 0xFFFF - total                        # ones complement

ip = bytes.fromhex("450000730000400040110000c0a80001c0a800c7")   # checksum field is 0000 for now
value = checksum(ip)
print("IPv4 header checksum:", hex(value))

fixed = ip[:10] + struct.pack("!H", value) + ip[12:]
print("check the fixed header:", checksum(fixed), "(0 means it is correct)")
''', long=True)

K.code('random_vs_secrets', r'''
# random is for games and simulations. secrets is for passwords, tokens and keys.
import random
import secrets

random.seed(2026)
first = []
for i in range(6):
    first.append(random.randint(0, 9))

random.seed(2026)
second = []
for i in range(6):
    second.append(random.randint(0, 9))

print("random with the same seed:", first, second, "same:", first == second)

token = secrets.token_hex(16)            # 16 random bytes from the operating system
print("secrets token:", token)
print("length:", len(token), "hex digits =", len(token) * 4, "bits")
print("URL safe token:", secrets.token_urlsafe(16))
''', long=True)

K.code('safe_input', r'''
# Two classic mistakes with user input: path traversal and command injection
import posixpath
import shlex

BASE = "/srv/files"

def safe_join(base, name):
    full = posixpath.normpath(posixpath.join(base, name))   # turns a/../b into b
    if full == base or full.startswith(base + "/"):
        return full
    return None                                                # outside the folder: refuse

for name in ["report.pdf", "2026/nov.csv", "../../etc/passwd", "/etc/shadow", "a/../../files2/x"]:
    print(repr(name), "->", safe_join(BASE, name))

user_input = "report.pdf && rm -rf ~"
unsafe = "ls -l " + user_input           # a shell would run TWO commands
safer = ["ls", "-l", user_input]         # subprocess.run(safer) passes ONE argument, no shell
print("unsafe string:", unsafe)
print("safe list    :", safer)
print("quoted       :", "ls -l " + shlex.quote(user_input))
''', long=True)

K.code('port_check', r'''
# Is a TCP port open? Checked only on this computer (127.0.0.1), never on someone else's.
import socket

def is_open(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex((host, port))      # 0 means the handshake worked
    s.close()
    return result == 0

server = socket.socket()
server.bind(("127.0.0.1", 0))                 # port 0: let the OS pick a free port
server.listen()
open_port = server.getsockname()[1]

spare = socket.socket()
spare.bind(("127.0.0.1", 0))
closed_port = spare.getsockname()[1]
spare.close()                                 # nothing listens here any more

print("port with a listener open:", is_open("127.0.0.1", open_port))
print("port with no listener open:", is_open("127.0.0.1", closed_port))
server.close()
''', long=True)

K.lesson('idea', 'Why security people learn Python', f'''
{talk('Python was created by Guido van Rossum and first released in 1991. It was meant to be easy to read, and that is exactly why the security world adopted it. Security work is full of small, one off jobs: read a log, decode a strange string, check a thousand files, parse a packet. Writing those in C takes hours. In Python they take minutes. Over the years, many famous security tools were written in Python: Scapy for building and reading network packets, Volatility for studying memory dumps after an attack, sqlmap for testing databases, Impacket for Windows network protocols, and fail2ban, which blocks addresses that keep failing to log in. Defenders use Python to automate alerts and investigations, and researchers use it to analyse malware. You do not need to be a professional programmer. You need variables, loops, lists, dictionaries, functions, and the handful of security modules this chapter shows.')}
{src('Python 3.14 documentation for bytes, base64, hashlib, hmac, re, struct, secrets, subprocess and pickle, RFC 3629, RFC 4648, RFC 1071, RFC 1035 and FIPS 180-4.')}
{wwh('<b>Python for security</b> means using a few standard modules to handle bytes, hashes, text patterns, binary formats, randomness and network sockets, and writing code that cannot be tricked by bad input.',
     'Security jobs are full of repeated small tasks. A 15 line script that reads 10,000 log lines beats reading them by eye, and it does the same thing every time.',
     'Learn the core language first. Then learn the security modules: <code>bytes</code> and <code>base64</code>, <code>hashlib</code> and <code>hmac</code>, <code>re</code>, <code>struct</code>, <code>secrets</code>, <code>socket</code>, and the safe ways to use <code>subprocess</code> and files.')}
{link('python', 'Complete Python', 'New to Python, or need a refresher? The Complete Python subject teaches the whole language from print() to classes, files, regular expressions, sockets and web apps, with runnable code and downloads.')}
{table(['Security task', 'Python module', 'Lesson'], [
    ['Decode a strange string from a log or email', 'bytes, base64, binascii', 'Text and bytes'],
    ['Check a download or store a fingerprint', 'hashlib, hmac', 'Hashes'],
    ['Find failed logins or attack patterns in logs', 're', 'Regular expressions'],
    ['Read packet headers or file formats', 'struct', 'Binary data'],
    ['Make passwords, tokens and keys', 'secrets', 'Safe code'],
    ['Handle file names and commands from users', 'pathlib, posixpath, subprocess, shlex', 'Safe code'],
    ['Check your own services', 'socket', 'Sockets']])}
{term(['$ python3 -m venv sec-env            # a private folder for this project\'s packages', '$ source sec-env/bin/activate        # on Windows: sec-env\\Scripts\\activate', '(sec-env) $ python --version', 'Python 3.14.0', '(sec-env) $ python -m pip install pip-audit', '(sec-env) $ pip-audit                # lists installed packages with known vulnerabilities'], 'A clean Python setup for security scripts')}
{note('Every program in this chapter uses only the standard library, so it runs on any Python 3.11 or newer with nothing to install. Each one has a download link under it.', 'tip')}
''', kw=['Python for security', 'why Python', 'Scapy', 'Volatility', 'sqlmap', 'Impacket', 'fail2ban', 'venv', 'pip-audit', 'standard library'])

K.lesson('bytes', 'Text and bytes: UTF-8, hex and base64', f'''
{talk('Inside a computer there are no letters, only numbers. A byte is eight bits, a number from 0 to 255. Long ago, the ASCII table from 1963 gave each English letter a number below 128: capital A is 65, small a is 97. That was fine for English but useless for Hindi, Chinese or Arabic. Unicode fixed that by giving every character in every language its own number, called a code point. Then in 1992, Ken Thompson and Rob Pike designed UTF-8, a clever way to store those code points as bytes: plain English letters still take one byte, exactly like ASCII, and other characters take two, three or four bytes. Today almost every web page uses UTF-8. Security people meet bytes everywhere: in network packets, in hashes, in keys, in malware. Two ways of writing bytes as text are everywhere. Hex writes each byte as two digits from 0 to f. Base64 packs every three bytes into four printable letters, so binary data can travel inside emails, web addresses and JSON. Attackers often hide commands in base64, so reading it quickly is a daily skill.')}
{wwh('A Python <code>str</code> holds text (code points). A <code>bytes</code> object holds raw numbers from 0 to 255. <code>encode()</code> turns text into bytes and <code>decode()</code> turns bytes back into text. <b>Hex</b> and <b>base64</b> are two ways to write bytes using only printable characters.',
     'Hashes, keys, packets and files are bytes. If you mix up text and bytes you get wrong hashes, broken parsers and security checks that can be bypassed with strange characters.',
     'UTF-8 uses 1 byte for code points below 128, 2 bytes up to 2,047, 3 bytes up to 65,535 and 4 bytes above that. Hex uses 2 digits per byte. Base64 cuts each group of 3 bytes (24 bits) into four 6 bit numbers and maps each to one of 64 letters, adding = padding at the end when needed.')}
{viz('cybytes')}
{run('text_bytes')}
{table(['Code points', 'UTF-8 bytes', 'Example'], [
    ['0 to 127', '1', 'A (65), 7 (55)'],
    ['128 to 2,047', '2', 'é (233) becomes c3 a9'],
    ['2,048 to 65,535', '3', '₹ (8,377) becomes e2 82 b9'],
    ['65,536 to 1,114,111', '4', 'emoji such as the thumbs up sign (128,077)']])}
{fxs(fx('Hex length', 'hex digits = 2 &times; bytes', 'One byte is 8 bits, one hex digit is 4 bits. A 32 byte SHA-256 hash is 64 hex digits.', key=True),
     fx('Base64 length', 'L = 4 &times; ceil(n / 3)', 'n bytes become L characters. 5 bytes: 4 &times; 2 = 8. Base64 makes data about 33% bigger.', key=True),
     fx('Bits per base64 character', 'log<sub>2</sub>(64) = 6', 'Each character carries 6 bits, so 4 characters carry 24 bits = 3 bytes.'))}
{note('Base64 is an encoding, not encryption. Anyone can decode it. Seeing a password "protected" by base64 in a config file is a finding to report.', 'warn')}
{scene('the base64 command in a phishing email', '<p>A help desk analyst opens a suspicious email attachment in a safe sandbox and finds a script that runs PowerShell with <code>-EncodedCommand</code> followed by a long base64 string. Instead of running it, the analyst decodes it with Python: <code>base64.b64decode(s).decode("utf-16-le")</code>, because PowerShell encodes commands as UTF-16 little endian. The decoded text shows a command that downloads a file from a strange address. The analyst blocks that address for the whole company in minutes. Knowing which encoding to try was the whole job.</p>')}
''', kw=['bytes', 'str', 'encode', 'decode', 'UTF-8', 'Unicode', 'code point', 'ASCII', 'hex', 'base64', 'padding', 'EncodedCommand'])

K.lesson('hashing', 'Hashes in Python: hashlib and hmac', f'''
{talk('A hash function takes data of any size and returns a short fingerprint of fixed size. The same input always gives the same fingerprint, but you cannot run the function backwards to get the input, and it is practically impossible to find two inputs with the same fingerprint. Ron Rivest designed MD5 in 1991, and it was used everywhere until 2004, when Wang Xiaoyun and her team showed how to make two different files with the same MD5 hash. SHA-1 fell the same way in 2017, when Google and the CWI institute in Amsterdam published two different PDF files with the same SHA-1 hash. Today the standard choice is SHA-256, from the SHA-2 family that the NSA designed and NIST published in 2001. In daily security work you use hashes to check that downloads were not changed, to identify known malware by its fingerprint, and as one piece of how passwords are stored. The Cryptography section explains how SHA-256 works inside. Here you learn to use it correctly from Python.')}
{wwh('<code>hashlib</code> computes hashes such as SHA-256. <code>hmac</code> adds a secret key to a hash, and <code>hmac.compare_digest</code> compares two secret values safely.',
     'A hash proves data was not changed: if one bit changes, the hash changes completely. Malware databases, file integrity monitors and software downloads all rely on this.',
     'Call <code>hashlib.sha256(data).hexdigest()</code> for small data. For big files, read pieces and call <code>update()</code> on each, or use <code>hashlib.file_digest(f, "sha256")</code> (Python 3.11 and newer). Compare secret values with <code>hmac.compare_digest</code>, which takes the same time whether the first byte or the last byte differs.')}
{viz('cyavalanche')}
{run('hash_demo')}
{fxs(fx('Expected bits that flip', 'E = n &times; 1/2 = 256 &times; 1/2 = 128', 'Each output bit of a good hash flips with probability 1/2 when the input changes.', key=True),
     fx('Spread', '&sigma; = &radic;(n &times; p &times; (1 &minus; p)) = &radic;(256 &times; 1/4) = 8', 'So nearly every change flips between 104 and 152 bits (three spreads either side).'),
     fx('Finding a collision', 'about 2<sup>n/2</sup> tries', 'The birthday bound. For SHA-256 that is 2<sup>128</sup> tries, far beyond any computer. For MD5 better attacks need only seconds.'))}
{table(['Hash', 'Output', 'Status for security'], [
    ['MD5', '128 bits (32 hex digits)', 'Broken (collisions since 2004). Only for non security checks'],
    ['SHA-1', '160 bits (40 hex digits)', 'Broken (public collision in 2017). Being removed everywhere'],
    ['SHA-256, SHA-512', '256 or 512 bits', 'Safe. The standard choice'],
    ['SHA3-256', '256 bits', 'Safe. A different design, a good backup'],
    ['bcrypt, scrypt, Argon2', 'Password hashes', 'Deliberately slow. Use these for passwords, never plain SHA-256']])}
{note('Never compare a secret token or MAC with ==. Python stops comparing at the first different character, so the time taken leaks how many leading characters were right. An attacker can measure that and guess one character at a time.', 'exam')}
''', kw=['hashlib', 'sha256', 'hexdigest', 'update', 'file_digest', 'hmac', 'compare_digest', 'timing attack', 'MD5', 'SHA-1', 'avalanche effect', 'birthday bound'])

K.lesson('regex', 'Regular expressions for logs', f'''
{talk('A regular expression is a small pattern language for finding text. The mathematician Stephen Kleene described regular languages in the 1950s, and Ken Thompson put them into the Unix tools ed and grep around 1973. The name grep even comes from the ed command g slash re slash p: globally search for a regular expression and print. Security teams live in logs, and logs are text, so regular expressions are one of the most used skills in security. A pattern such as Failed password for something from some address pulls out the user name and the address from thousands of lines in a second. The parts in round brackets are called groups and capture the pieces you want. But patterns can go wrong in two ways. They can miss lines you wanted, and an attacker who knows your pattern can write lines that slip past it. And some patterns are so slow on carefully made input that they freeze a server. That second problem is called ReDoS, and it took down Stack Overflow in 2016 and much of Cloudflare for about half an hour in 2019.')}
{wwh('A <b>regular expression</b> describes a set of strings. <code>re.search(pattern, text)</code> finds the first match. Round brackets make <b>groups</b> that capture text, and <code>(?P&lt;name&gt;...)</code> gives a group a name.',
     'Logs from servers, firewalls and apps are the main evidence of attacks. Patterns turn thousands of free text lines into counts and alerts.',
     'Build the pattern from a real line, test it on lines that should match and lines that should not, then count matches per key in a dictionary.')}
{viz('cyregex')}
{run('log_regex')}
{table(['Pattern piece', 'Matches', 'Example'], [
    ['<code>\\d</code>', 'One digit', '<code>\\d+</code> matches 51022'],
    ['<code>\\S</code>', 'One character that is not a space', '<code>\\S+</code> matches root or 203.0.113.7'],
    ['<code>[\\d.]+</code>', 'Digits and dots', 'An IPv4 address'],
    ['<code>(?:...)?</code>', 'An optional part that is not captured', '<code>(?:invalid user )?</code>'],
    ['<code>(?P&lt;ip&gt;...)</code>', 'A named group (Python syntax)', '<code>m.group("ip")</code>'],
    ['<code>^</code> and <code>$</code>', 'Start and end of the text', 'Anchor a full match for input checks']])}
{fx('ReDoS cost model', 'steps &asymp; 2<sup>n</sup>', 'A pattern such as (a+)+$ on n letters a followed by one b can try about 2<sup>n</sup> ways to split the a letters before it fails. 30 letters already means about a billion steps.', key=True)}
{attack([
    ['Writes "Failed password for invalid user ..." lines that a careless pattern misses', 'Test patterns on every known variant of the line, and alert when lines match nothing at all'],
    ['Puts a fake log line inside a user name, for example a name containing a new line', 'Log libraries should escape new lines, and patterns should be anchored with ^ and $'],
    ['Sends text designed to make a nested pattern backtrack for minutes (ReDoS)', 'Avoid nested repeats such as (a+)+, limit input length, and use a time limit or a linear time engine such as RE2']])}
{note('Use raw strings for patterns: <code>r"\\d+"</code>. Without the r, Python reads the backslash first and some patterns change meaning.', 'tip')}
''', kw=['regular expression', 're', 'search', 'groups', 'named groups', 'raw string', 'log parsing', 'fail2ban', 'ReDoS', 'backtracking', 'RE2', 'grep'])

K.lesson('struct', 'Binary data with struct: headers and checksums', f'''
{talk('Network packets and many file formats are not text. They are fixed layouts of numbers: two bytes for this field, four bytes for that one. The struct module, part of Python since its early days, reads and writes such layouts. You describe the layout with a short format string, such as exclamation mark H H I, which means network byte order, then two 16 bit numbers, then one 32 bit number. Network byte order means big endian: the most significant byte comes first. Intel and AMD processors store numbers the other way round, little endian, which is why every network program has to convert. Tools like Scapy and Wireshark do this for every packet they show you. Writing a small parser yourself teaches you what those tools see. It also teaches you why parsers are a favourite target of attackers: a length field that says 60,000 when only 20 bytes arrived has caused countless security bugs in C programs. Python checks the bounds for you, which is one reason it is a safe choice for quick parsers.')}
{wwh('<code>struct.pack(format, values)</code> turns numbers into bytes, and <code>struct.unpack(format, data)</code> turns bytes back into numbers. "!" means network byte order (big endian). B is 1 byte, H is 2 bytes, I is 4 bytes and Q is 8 bytes.',
     'Every network protocol and many file formats are fixed layouts of numbers. To read a packet capture, check a header or study a malware file, you need to read bytes as numbers.',
     'Write down the layout from the standard (for DNS that is RFC 1035: six 16 bit numbers), build the format string, unpack, and check each value. Check lengths before you trust them.')}
{run('packet_parse')}
{show('The DNS header layout (RFC 1035)', '''offset 0   ID        16 bits  matches a reply to its question
offset 2   FLAGS     16 bits  QR, opcode, AA, TC, RD, RA, rcode
offset 4   QDCOUNT   16 bits  number of questions
offset 6   ANCOUNT   16 bits  number of answers
offset 8   NSCOUNT   16 bits  number of authority records
offset 10  ARCOUNT   16 bits  number of additional records''', {1: 'A random ID makes it harder for an attacker to fake a reply (DNS cache poisoning).', 2: 'RD (recursion desired) is the bit with value 0x0100. Our query sets it.', 3: 'Unpack all six at once with the format "!HHHHHH", 12 bytes.'}, lang='text')}
{fxs(fx('Header size', 'size = sum of field sizes', '"!HHHHHH" = 6 &times; 2 = 12 bytes. struct.calcsize gives it for you.', key=True),
     fx('Internet checksum', 'checksum = NOT( sum of 16 bit words, carries folded back in )', 'Adding the header with its checksum in place gives 0xFFFF, so the check function returns 0.', key=True))}
{note('A checksum catches accidents, not attackers. Anyone who changes a packet can compute a new checksum. Protection against deliberate changes needs a MAC or a signature, covered in Cryptography.', 'exam')}
''', kw=['struct', 'pack', 'unpack', 'network byte order', 'big endian', 'little endian', 'DNS header', 'RFC 1035', 'checksum', 'RFC 1071', 'parser bugs'])

K.lesson('safecode', 'Writing safe Python: randomness, paths, commands and untrusted data', f'''
{talk('A security script that is itself insecure is worse than no script. Python makes some dangerous things very easy, so here are the habits that matter most. First, randomness. The random module uses an algorithm called the Mersenne Twister, from 1998. It is excellent for games and simulations, but after seeing 624 of its outputs anyone can predict every future value. That is why Python added the secrets module in version 3.6, through PEP 506, for passwords, tokens and keys. Second, file paths. If a user can type a file name such as dot dot slash dot dot slash etc slash passwd, a careless program may read a file far outside the folder it meant to use. This is called path traversal. Python’s own tarfile module had such a bug, CVE 2007 4559, that went unfixed for fifteen years, and researchers in 2022 estimated that hundreds of thousands of projects used tarfile unsafely. Third, commands. Building a shell command by joining strings lets a user add their own command. Fourth, never load pickle, unsafe YAML or eval on data from outside, because each one can run code.')}
{wwh('<b>Safe Python</b> means using <code>secrets</code> for anything secret, checking that file paths stay inside the folder you expect, calling <code>subprocess</code> with a list and no shell, and never running <code>pickle.load</code>, <code>yaml.load</code> or <code>eval</code> on untrusted data.',
     'Attackers do not attack your idea. They attack your input handling. These four mistakes cause a large share of real vulnerabilities in Python code.',
     'For paths: join, normalise, then check the result still starts with the base folder plus a slash. For commands: pass a list such as <code>["ls", "-l", name]</code> so the name is one argument. For data: use <code>json</code> or <code>yaml.safe_load</code>.')}
{run('random_vs_secrets')}
{run('safe_input')}
{attack([
    ['Predicts a password reset token made with random.randint', 'Make tokens with secrets.token_urlsafe(32)'],
    ['Downloads ../../etc/passwd through a file download page', 'Normalise the path and check it stays inside the base folder'],
    ['Adds "&& rm -rf ~" to a file name passed to a shell', 'subprocess.run with a list and shell=False (the default)'],
    ['Sends a pickle file that runs a command when loaded', 'Use JSON for data from outside. pickle only for data you made yourself'],
    ['Uploads a tar file with ../ names that overwrite files', 'tarfile extraction filters (filter="data", the default from Python 3.14)'],
    ['Publishes a package named like a popular one on PyPI (typosquatting)', 'Pin versions with hashes (pip install --require-hashes) and run pip-audit']])}
{note('The check <code>full.startswith(base)</code> without the trailing slash is a classic bug: /srv/files2/secret starts with /srv/files. The program above shows it.', 'exam')}
{safe('Every example here works on made up names and strings. Nothing deletes or reads real system files.')}
''', kw=['secrets', 'random', 'Mersenne Twister', 'token', 'path traversal', 'normpath', 'command injection', 'subprocess', 'shell=False', 'shlex.quote', 'pickle', 'yaml safe_load', 'eval', 'tarfile', 'typosquatting', 'require-hashes'])

K.lesson('sockets', 'Sockets: checking your own services', f'''
{talk('A socket is the programming door to the network. The socket interface came from the University of California, Berkeley, in the early 1980s, in the BSD version of Unix, and almost every operating system still uses the same design. A program that wants to talk over TCP creates a socket, connects it to an address and a port, and then sends and receives bytes. If nothing is listening on that port, the other computer answers the connection with a reset and the connect fails. That simple fact is the basis of port scanning, which you met in the networks chapter. Defenders scan their own servers to find services that should not be running, such as an old database left open to the world. Attackers scan to find targets. The law is clear on this in most countries: scanning computers you do not own or do not have written permission to test can be a crime. So the program in this lesson only checks ports on your own computer, at address 127.0.0.1, which always means this machine.')}
{wwh('A <b>socket</b> is an endpoint for sending and receiving data. <code>connect_ex((host, port))</code> tries a TCP handshake and returns 0 when something is listening.',
     'Knowing which ports are open on your own machines is basic hygiene. Every open port is a door that needs a reason to exist.',
     'Create a socket, set a short timeout, call <code>connect_ex</code>, close it. A result of 0 means open. Anything else means closed or filtered.')}
{local('port_check', 'It opens real network sockets. It only talks to 127.0.0.1, your own computer.')}
{term(['$ ss -tlnp              # Linux: list listening TCP ports and their programs', 'State   Local Address:Port   Process', 'LISTEN  127.0.0.1:5432       postgres', 'LISTEN  0.0.0.0:22           sshd', '$ netstat -ano | findstr LISTENING     # Windows'], 'See what listens on your own computer')}
{note('A service bound to 127.0.0.1 can only be reached from the same computer. One bound to 0.0.0.0 can be reached from any network the computer is on. Many database leaks came from a single 0.0.0.0.', 'warn')}
{safe('Scan only computers you own or have written permission to test. Practise on your own machine or a lab you build yourself.')}
''', kw=['socket', 'connect_ex', 'TCP', 'port check', 'localhost', '127.0.0.1', '0.0.0.0', 'ss', 'netstat', 'BSD sockets', 'permission'])

K.lesson('versus', 'Python compared with other security languages', f'''
{talk('Python is not the only language in security. System administrators on Linux reach for Bash, the shell, because it joins existing tools together in one line. Windows administrators use PowerShell, which Microsoft released in 2006, and which can reach almost every part of Windows. Sadly, attackers love PowerShell for the same reason, so defenders must know it well too. Go, from Google in 2009, has become popular for security tools that must be fast and easy to ship, because a Go program compiles into one file that runs without installing anything. C and Rust are used when you need full control of memory, for example in operating systems, exploits and very fast scanners. Rust adds memory safety, which removes the class of bugs behind most serious vulnerabilities in C. A good security person can read all of these and writes most daily scripts in Python.')}
{versus('Languages for security work', ['', 'Python', 'Bash', 'PowerShell', 'Go', 'C and Rust'], [
    ['Best for', 'Parsing, analysis, glue, quick tools, data and ML', 'Chaining Linux tools in one line', 'Windows and Active Directory administration', 'Fast network tools shipped as one file', 'Operating systems, exploits, very fast code'],
    ['Learning effort', 'Low', 'Low for basics, high for safe scripts', 'Medium', 'Medium', 'High'],
    ['Speed', 'Slow, fine for most jobs', 'Slow', 'Medium', 'Fast', 'Fastest'],
    ['Memory safety', 'Yes', 'Yes', 'Yes', 'Yes', 'C no, Rust yes'],
    ['Security weak spot', 'pickle, eval, shell=True', 'Unquoted variables split into many arguments', 'Abused by attackers, so heavily logged', 'Large binaries are hard to inspect', 'C: buffer overflows']],
    'Use Python as the default for scripts and analysis, Bash for one liners on Linux, PowerShell on Windows, and Go or Rust when the tool must be fast and shipped to many machines.')}
''', kw=['Python vs Bash', 'PowerShell', 'Go', 'Rust', 'C', 'memory safety', 'comparison', 'security languages'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Python in security grows with you. A beginner writes ten line scripts that decode base64 and hash a file. A college student writes parsers for logs and packets, uses the secrets module, avoids shell injection, and automates checks with small tools. A masters student builds real tools: a packet sniffer with Scapy, a memory analysis plugin for Volatility, a detection pipeline that feeds a SIEM, or a fuzzer that throws strange inputs at a parser to find crashes. At the research level, Python drives serious program analysis. The angr framework from the University of California, Santa Barbara does symbolic execution of binaries, exploring every path through a program to find inputs that reach a bug. Google’s Atheris brings coverage guided fuzzing to Python code. And Python itself is studied as an attack surface: its package ecosystem, PyPI, is a constant target of supply chain attacks with fake and hijacked packages.')}
{ladder(
    '<p>Python can turn text into bytes and back, make a fingerprint of a file, find words in a log and make strong random passwords. Base64 is not a secret code.</p>',
    '<p>Use encode, decode, hex and base64 fluently, hash files in chunks, compare secrets with compare_digest, write and test regular expressions with named groups, parse headers with struct, use secrets for tokens, and call subprocess with a list.</p>',
    '<p>Build tools: Scapy for packets, Volatility plugins for memory, log pipelines into a SIEM, fuzzers for parsers. Understand ReDoS and linear time regex engines, timing attacks on comparisons, pickle and YAML deserialisation risks, and software supply chain controls such as pinned hashes, signed packages and pip-audit.</p>',
    '<p>Program analysis in Python: symbolic execution with angr, coverage guided fuzzing with Atheris and libFuzzer, taint analysis of Python web apps, and research on PyPI supply chain attacks (typosquatting, dependency confusion, malicious install scripts) and their detection with static and dynamic analysis.</p>')}
{grow('Turn text into bytes, decode base64, hash a file and make secure tokens.',
      'Parse logs with regular expressions, read packet headers with struct, and avoid path traversal and command injection.',
      'Build packet, memory and fuzzing tools, and analyse code and packages for supply chain risks.')}
''', kw=['beginner', 'expert', 'Scapy', 'Volatility plugin', 'fuzzing', 'Atheris', 'angr', 'symbolic execution', 'supply chain', 'PyPI', 'dependency confusion'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <code>str</code> holds text, <code>bytes</code> holds numbers 0 to 255. <code>encode()</code> and <code>decode()</code> convert, using UTF-8 (1 to 4 bytes per character).',
    'Hex uses 2 digits per byte. Base64 uses 4 characters per 3 bytes: L = 4 &times; ceil(n / 3). Base64 is an encoding, not encryption.',
    '<code>hashlib.sha256(data).hexdigest()</code> gives 64 hex digits. Hash big files in chunks with <code>update()</code>. MD5 and SHA-1 are broken.',
    'One input change flips about 128 of 256 bits (spread 8). Compare secrets with <code>hmac.compare_digest</code>, never with ==.',
    'Regular expressions with groups turn logs into counts. Test patterns on every line variant, use raw strings, and avoid nested repeats that cause ReDoS.',
    '<code>struct</code> reads binary layouts. "!" means network byte order. B = 1, H = 2, I = 4, Q = 8 bytes. A checksum catches accidents, not attackers.',
    'Use <code>secrets</code> for tokens, never <code>random</code>. Check paths stay inside the base folder plus a slash. Call subprocess with a list. Never unpickle untrusted data.',
    'Check ports only on your own machines. <code>connect_ex</code> returns 0 when a port is open.'],
    'Cryptography starts next with classical ciphers and the maths of breaking them, then moves to AES, hashing, number theory and RSA.')}
{files('Three tasks: text to hex, counting failed logins with a regular expression, and a safe path check.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does "hello".encode() return?', ['A str', 'A bytes object', 'A list of letters', 'A hash'], 1, 'encode goes from text to ...', 'encode() turns text into bytes, here b"hello".')
K.quiz('e', 'How many hex digits does one byte need?', ['1', '2', '4', '8'], 1, 'A byte is 8 bits, a hex digit 4 bits.', '8 / 4 = 2 hex digits.')
K.quiz('e', 'Which module should make a password reset token?', ['random', 'secrets', 'math', 'time'], 1, 'Made for secrets.', 'secrets uses the operating system’s secure random source.')
K.quiz('e', 'Is base64 a form of encryption?', ['Yes, it hides data', 'No, anyone can decode it', 'Only with a key', 'Only for passwords'], 1, 'No key is involved.', 'Base64 is a public encoding with no key.')
K.quiz('m', 'How many bytes is "é" in UTF-8?', ['1', '2', '3', '4'], 1, 'Its code point is 233.', 'Code points 128 to 2,047 take 2 bytes: c3 a9.')
K.quiz('m', 'What does the "!" mean in struct.unpack("!HH", data)?', ['Ignore errors', 'Network byte order (big endian)', 'Little endian', 'Signed numbers'], 1, 'Networks have one order.', '"!" selects network byte order, which is big endian.')
K.quiz('m', 'Which call is safe when the file name comes from a user?', ['os.system("cat " + name)', 'subprocess.run("cat " + name, shell=True)', 'subprocess.run(["cat", name])', 'eval("cat " + name)'], 2, 'No shell.', 'A list with no shell passes the name as one argument.')
K.quiz('m', 'In a regular expression, what does (?:invalid user )? do?', ['Captures the words', 'Makes the words optional without capturing them', 'Requires them twice', 'Ends the pattern'], 1, '?: and ? together.', '(?:...) groups without capturing, and ? makes it optional.')
K.quiz('m', 'Why read a big file in chunks before hashing it?', ['It is more secure', 'It keeps memory use small', 'SHA-256 needs chunks', 'It changes the hash'], 1, 'Think of a 50 GB file.', 'update() on chunks gives the same hash with little memory.')
K.quiz('h', 'safe_join checks full.startswith(base) with base = "/srv/files". Which path wrongly passes?', ['/srv/files/a.txt', '/srv/files2/secret', '/srv/files', '/srv/files/x/y'], 1, 'Missing slash.', '"/srv/files2" starts with "/srv/files", so check base + "/".')
K.quiz('h', 'Why is pickle.load on a file from the internet dangerous?', ['It is slow', 'A pickle can make Python call any function, so it can run commands', 'It loses data', 'It only works on Linux'], 1, 'Read the pickle docs warning.', 'Pickles can call functions such as os.system while loading.')
K.quiz('h', 'A pattern for "Failed password for USER from" captures one word after "for". Which failed logins does it miss?', ['Accepted password lines', 'Failed password for invalid user ... lines', 'Lines with IPv6', 'Lines at midnight'], 1, 'What follows "for"?', 'After "for" come the words "invalid user", so one word followed by "from" no longer fits.')
K.quiz('x', 'In the style of a Stanford CS 155 question: why does comparing a secret token with == leak information?', ['== is random', 'It stops at the first different character, so the time reveals how many leading characters are right', 'It changes the token', 'It logs the token'], 1, 'Time depends on the data.', 'Early exit makes time depend on the matching prefix, which allows a character by character attack.')
K.quiz('x', 'In the style of an MIT 6.858 exam: after seeing 624 consecutive 32 bit outputs of Python random, an attacker can', ['Learn nothing', 'Rebuild the Mersenne Twister state and predict every future output', 'Read the seed file', 'Only predict the next one'], 1, 'The state is 624 words.', 'MT19937 output is a reversible function of its 624 word state, so it can be rebuilt exactly.')

K.calc('e', 'How many bytes is "café" in UTF-8?', '5', 'c, a and f take 1 byte each.', ['c, a, f: 3 bytes.', 'é: 2 bytes.', eq('3 + 2 = 5')], check=len('café'.encode('utf-8')))
K.calc('e', 'What is the hex byte 0x41 in decimal?', '65', '4 sixteens and 1.', ['4 &times; 16 = 64.', 'Plus 1.', eq('64 + 1 = 65 (the letter A)')], check=0x41)
K.calc('e', 'How many hex digits does a SHA-256 hash have?', '64', '256 bits, 4 bits per digit.', ['256 bits.', 'Each hex digit holds 4 bits.', eq('256 / 4 = 64')], check=256 // 4)
K.calc('m', 'How many base64 characters encode 10 bytes?', '16', 'L = 4 &times; ceil(n / 3).', ['ceil(10 / 3) = 4 groups.', 'Each group gives 4 characters.', eq('4 &times; 4 = 16')], check=4 * -(-10 // 3))
K.calc('m', 'How many characters does secrets.token_hex(16) return?', '32', '2 hex digits per byte.', ['16 bytes.', '2 digits each.', eq('16 &times; 2 = 32')], check=2 * 16)
K.calc('m', 'What is struct.calcsize("!HHI")?', '8', 'H = 2, I = 4.', ['Two H: 2 + 2 = 4.', 'One I: 4.', eq('4 + 4 = 8 bytes')], check=__import__('struct').calcsize('!HHI'))
K.calc('m', 'What is 0x5A XOR 0x3C in decimal?', '102', 'XOR bit by bit.', ['0x5A = 0101 1010, 0x3C = 0011 1100.', 'XOR = 0110 0110 = 0x66.', eq('6 &times; 16 + 6 = 102')], check=0x5A ^ 0x3C)
K.calc('m', 'How many output bits do you expect to flip in SHA-256 when one input bit changes?', '128', 'Each bit flips with probability 1/2.', ['n = 256 bits.', 'p = 1/2.', eq('E = 256 &times; 1/2 = 128')], check=256 // 2)
K.calc('h', 'What is the standard deviation of the number of flipped bits in SHA-256?', '8', '&sigma; = &radic;(n p (1 &minus; p)).', ['n p (1 &minus; p) = 256 &times; 1/2 &times; 1/2 = 64.', 'Square root.', eq('&sigma; = &radic;64 = 8')], check=int((256 * 0.25) ** 0.5))
K.calc('h', 'A 128 bit token is guessed at 10<sup>9</sup> tries per second. On average half the space is searched. About how many years is that? Answer the power of ten (k in 10<sup>k</sup>).', '21', 'Half of 2<sup>128</sup> is 2<sup>127</sup>.', ['2<sup>127</sup> &asymp; 1.7 &times; 10<sup>38</sup> tries.', 'Divide by 10<sup>9</sup> per second and 3.16 &times; 10<sup>7</sup> seconds per year.', eq('&asymp; 5.4 &times; 10<sup>21</sup> years, so k = 21')], check=__import__('math').floor(__import__('math').log10(2 ** 127 / 1e9 / (365.25 * 86400))))
K.calc('x', 'In the style of a Stanford CS 155 problem: a regex engine tries about 2<sup>n</sup> paths on a ReDoS input with n = 30, at 10<sup>8</sup> steps per second. How many seconds, rounded?', '11', '2<sup>30</sup> is about a billion.', ['2<sup>30</sup> = 1,073,741,824 steps.', 'Divide by 10<sup>8</sup> per second.', eq('1,073,741,824 / 100,000,000 &asymp; 10.7, about 11 seconds')], check=round(2 ** 30 / 1e8))

K.assign('tohex', 'e', 'Text to hex',
         '<p>Write <code>to_hex(text)</code> that returns the UTF-8 bytes of the text as a lower case hex string with no spaces. For example "Hi" gives "4869".</p>',
         '''
def to_hex(text):
    # your code here
    pass
''', [('to_hex("Hi")', '4869'), ('to_hex("é")', 'c3a9'), ('to_hex("")', ''), ('to_hex("A1")', '4131')],
         '''
def to_hex(text):
    data = text.encode("utf-8")
    return data.hex()
''', 'Encode the text to bytes first, then call .hex() on the bytes.', '<p>Hashes, keys and packet dumps are shown as hex. Remember that text must become bytes before any hash or hex step.</p>')
K.assign('failed', 'm', 'Count failed logins per address',
         '<p>Write <code>failed_ips(lines, limit)</code>. lines is a list of sshd log lines. Count lines that contain "Failed password for", with or without "invalid user", and capture the address after "from". Return a sorted list of addresses with at least limit failures.</p>',
         '''
import re

def failed_ips(lines, limit):
    # your code here
    pass
''', [('failed_ips(["Failed password for root from 1.2.3.4 port 1", "Failed password for invalid user x from 1.2.3.4 port 2", "Accepted password for a from 5.6.7.8 port 3"], 2)', ['1.2.3.4']),
      ('failed_ips([], 1)', []),
      ('failed_ips(["Failed password for a from 9.9.9.9 port 1", "Failed password for b from 8.8.8.8 port 1"], 1)', ['8.8.8.8', '9.9.9.9'])],
         '''
import re

def failed_ips(lines, limit):
    pattern = re.compile(r"Failed password for (?:invalid user )?\\S+ from ([\\d.]+)")
    counts = {}
    for line in lines:
        m = pattern.search(line)
        if m:
            ip = m.group(1)
            counts[ip] = counts.get(ip, 0) + 1
    found = []
    for ip in counts:
        if counts[ip] >= limit:
            found.append(ip)
    return sorted(found)
''', 'Use the optional part (?:invalid user )? and one group for the address. Count in a dictionary.', '<p>The first test only passes if the "invalid user" line is counted, which is the trap from the lesson.</p>')
K.assign('safepath', 'm', 'A safe path check',
         '<p>Write <code>is_safe(base, name)</code>. Join base and name with posixpath.join, normalise with posixpath.normpath, and return True only when the result equals base or starts with base + "/".</p>',
         '''
import posixpath

def is_safe(base, name):
    # your code here
    pass
''', [('is_safe("/srv/files", "a.txt")', True), ('is_safe("/srv/files", "../../etc/passwd")', False), ('is_safe("/srv/files", "/etc/shadow")', False), ('is_safe("/srv/files", "x/../../files2/y")', False), ('is_safe("/srv/files", "x/../y.txt")', True)],
         '''
import posixpath

def is_safe(base, name):
    full = posixpath.normpath(posixpath.join(base, name))
    return full == base or full.startswith(base + "/")
''', 'Normalise first, then compare with base + "/" so that /srv/files2 does not pass.', '<p>Joining with an absolute name such as /etc/shadow throws away the base completely, which is why the check must come after the join.</p>')

K.must('Text and bytes', 'str is text, bytes is 0 to 255. encode() and decode() with UTF-8 (1 to 4 bytes per character). Hex = 2 digits per byte.')
K.must('Base64', 'L = 4 &times; ceil(n / 3), = padding. An encoding, not encryption. PowerShell -EncodedCommand is base64 of UTF-16 LE.')
K.must('Hashes', 'hashlib.sha256(data).hexdigest(), 64 hex digits. Chunks with update(). MD5 and SHA-1 broken. compare_digest for secrets.')
K.must('Regex', 'Raw strings, groups, (?P&lt;name&gt;...), (?:...)? optional. Test every line variant. Avoid (a+)+ (ReDoS).')
K.must('struct', '"!" network byte order. B 1, H 2, I 4, Q 8 bytes. Checksums catch accidents only.')
K.must('Safe code', 'secrets not random. Path check with base + "/". subprocess with a list, no shell. No pickle, yaml.load or eval on untrusted data.')

T = K.topic(
    slug='cy-python', topic='cy-python', step=(2, 'How computers and networks work', 'cy-f2', 'How operating systems keep users apart, how data moves across networks, and the Python every security person needs.', 'Beginner'),
    title='Python for security: bytes, hashes, logs, packets and safe code', short='Python for security', badge='2.3', minutes=60,
    lead='The Python a security person uses every day: text and bytes with UTF-8, hex and base64, hashing with hashlib and hmac, regular expressions for logs, binary headers with struct and the internet checksum, secrets versus random, path traversal and command injection, and checking your own ports with sockets.',
    desc='Python for security, bytes, str, encode, decode, UTF-8, hex, base64, hashlib, sha256, hmac compare_digest, avalanche effect, regular expressions, log parsing, named groups, ReDoS, struct, network byte order, DNS header, internet checksum, secrets, random Mersenne Twister, path traversal, command injection, subprocess, shlex, pickle, tarfile, sockets, connect_ex, port check, pip-audit',
    summary='bytes, UTF-8, hex and base64, hashlib and hmac, regular expressions for logs, struct and checksums, and safe Python habits.',
    keywords=['Python', 'bytes', 'base64', 'hashlib', 'regex', 'struct', 'secrets', 'path traversal', 'subprocess', 'socket'],
    recap='<p>Turn text into bytes before hashing, read logs with tested patterns, parse binary layouts with struct, and never trust input.</p>',
    added='2026-11-14')
