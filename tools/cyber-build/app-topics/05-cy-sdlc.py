# Application Security 2.2: secure development. Checked against Microsoft SDL and the STRIDE per element table,
# Kohnfelder and Garg, The Threats to Our Products (1999), Schneier, Attack Trees (Dr. Dobb's Journal, 1999), Shostack,
# Threat Modeling: Designing for Security (2014) and the Threat Modeling Manifesto, NIST SP 800-218 SSDF (2022), OWASP
# SAMM and ASVS, SLSA, the Bandit rule list, AFL and libFuzzer documentation, OSS-Fuzz, and public reports on the
# SolarWinds (2020) and Uber (2016) incidents.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-sdlc')
K = Kit()

K.code('stride', r'''
# STRIDE per element: list the threats that apply to each part of a data flow diagram
STRIDE = {
    "S": "Spoofing (pretending to be someone else)       -> authentication",
    "T": "Tampering (changing data or code)              -> integrity",
    "R": "Repudiation (denying an action)                -> logging, non repudiation",
    "I": "Information disclosure (leaking data)          -> confidentiality",
    "D": "Denial of service (making it unavailable)      -> availability",
    "E": "Elevation of privilege (gaining more rights)   -> authorisation",
}
APPLIES = {                      # Microsoft's STRIDE per element table
    "external entity": "SR",
    "process": "STRIDE",
    "data store": "TRID",        # R applies when the store holds logs
    "data flow": "TID",
}
diagram = [
    ("Customer (browser)", "external entity"),
    ("Web app", "process"),
    ("Orders database", "data store"),
    ("Browser -> web app (HTTPS)", "data flow"),
    ("Web app -> payment provider", "data flow"),
]
total = 0
for name, kind in diagram:
    letters = APPLIES[kind]
    total += len(letters)
    print(f"{name} [{kind}]: {letters}")
    for letter in letters:
        print("    " + STRIDE[letter])
print(f"\n{total} threats to think through for {len(diagram)} elements")
''', long=True)

K.code('attack_tree', r'''
# An attack tree (Schneier, 1999): the goal at the root, ways to reach it below.
# OR node: the attacker picks the cheapest child. AND node: the attacker needs every child.
tree = ("OR", "Read customer database", [
    ("AND", "Use a stolen admin password", [
        ("LEAF", "Phish an admin", 2000, 0.3),
        ("LEAF", "Bypass MFA (push fatigue)", 1000, 0.2),
    ]),
    ("LEAF", "SQL injection in the search page", 500, 0.1),
    ("AND", "Steal a backup", [
        ("LEAF", "Find the backup bucket name", 100, 0.5),
        ("LEAF", "Bucket left public", 0, 0.05),
    ]),
])

def evaluate(node, depth=0, show=True, fixed=()):
    kind, name = node[0], node[1]
    if kind == "LEAF":
        cost, p = (float("inf"), 0.0) if name in fixed else (node[2], node[3])
    else:
        results = [evaluate(child, depth + 1, show, fixed) for child in node[2]]
        if kind == "OR":
            cost = min(c for c, _ in results)               # cheapest way
            q = 1.0
            for _, pc in results:
                q *= 1 - pc
            p = 1 - q                                       # at least one way works (independent)
        else:
            cost = sum(c for c, _ in results)               # must pay for every step
            p = 1.0
            for _, pc in results:
                p *= pc                                     # every step must work
    if show:                                                # children print before their parent
        print(f"{'    ' * depth}{kind:4} {name:36} cost {cost:5}  P(success) {p:.4f}")
    return cost, p

cost, p = evaluate(tree)
print("\nWhat if we fix leaves? (a fixed leaf costs infinity and never succeeds)")
for fix in [("SQL injection in the search page",), ("Bucket left public",),
            ("SQL injection in the search page", "Bucket left public")]:
    c, pr = evaluate(tree, show=False, fixed=fix)
    print(f"   fix {' + '.join(fix):55} cheapest attack {c:5}  P(success) {pr:.4f}")
''', long=True)

K.code('sast_scan', r'''
# A tiny static analyser (in the spirit of Bandit or Semgrep): walk the syntax tree of Python code
# and flag dangerous calls. The code being scanned is only parsed, never run.
import ast

SOURCE = """
import pickle, subprocess, sqlite3
DB_PASSWORD = "hunter2"

def search(db, term):
    return db.execute(f"SELECT * FROM items WHERE name = '{term}'")

def ping(host):
    subprocess.run("ping -c 1 " + host, shell=True)

def load(blob):
    return pickle.loads(blob)

def calc(expr):
    return eval(expr)

def safe_search(db, term):
    return db.execute("SELECT * FROM items WHERE name = ?", (term,))
"""

class Scanner(ast.NodeVisitor):
    def __init__(self):
        self.findings = []

    def add(self, node, rule, msg):
        self.findings.append((node.lineno, rule, msg))

    def visit_Call(self, node):
        name = ast.unparse(node.func)
        if name in ("eval", "exec"):
            self.add(node, "B307", f"{name}() runs any code it is given")
        if name in ("pickle.loads", "pickle.load"):
            self.add(node, "B301", "unpickling untrusted data can run code")
        if any(k.arg == "shell" and getattr(k.value, "value", False) is True for k in node.keywords):
            self.add(node, "B602", "subprocess with shell=True, injection risk")
        if name.endswith(".execute") and node.args and isinstance(node.args[0], (ast.JoinedStr, ast.BinOp)):
            self.add(node, "B608", "SQL built with an f-string or +, use ? placeholders")
        self.generic_visit(node)

    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(t, ast.Name) and "PASSWORD" in t.id.upper() and isinstance(node.value, ast.Constant):
                self.add(node, "B105", f"hard coded password in {t.id}")
        self.generic_visit(node)

s = Scanner()
s.visit(ast.parse(SOURCE))
for line, rule, msg in sorted(s.findings):
    print(f"line {line:2}  {rule}  {msg}")
print(f"{len(s.findings)} findings. safe_search on line 18 is not flagged, because it uses placeholders.")
''', long=True)

K.code('secret_scan', r'''
# Secret scanning: find keys and passwords committed to code, using known patterns plus entropy
import math, re
from collections import Counter

FILES = {
    "config.py": 'DEBUG = True\nAWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"\nREGION = "ap-south-1"\n',
    "deploy.sh": 'export API_TOKEN="q8Zr3VbN1xTt6YwP0kLm9sDf2GhJ4cXe"\necho "deploying build 4417"\n',
    "README.md": "Set your token in the environment. Example: TOKEN=changeme\n",
    "id_rsa": "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAA...\n",
}
PATTERNS = {
    "AWS access key id": r"\bAKIA[0-9A-Z]{16}\b",
    "private key file": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}

def entropy(s):
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in Counter(s).values())

for name, text in FILES.items():
    for label, pat in PATTERNS.items():
        for m in re.finditer(pat, text):
            print(f"{name:10} pattern  {label}: {m.group(0)[:24]}")
    for m in re.finditer(r'"([A-Za-z0-9+/=_-]{20,})"', text):     # long quoted strings
        h = entropy(m.group(1))
        if h > 4.0:
            print(f"{name:10} entropy  {h:.2f} bits per character in {m.group(1)[:12]}... looks like a random secret")
print("AKIAIOSFODNN7EXAMPLE is the documented example key from AWS, never a real one.")
print("Found a real secret? Revoke and rotate it first: deleting the commit does not remove it from clones.")
''', long=True)

K.code('fuzz', r'''
# Coverage guided fuzzing in miniature (the idea behind AFL and libFuzzer): mutate inputs, keep the ones
# that reach new code, and find a bug that random inputs almost never hit.
import random

def parse(data):
    """A toy parser for messages like b'MSG' + length + body. It has a hidden bug."""
    path = []
    if len(data) < 4:
        return path, None
    path.append("len>=4")
    if data[0:1] == b"M":
        path.append("M")
        if data[1:2] == b"S":
            path.append("MS")
            if data[2:3] == b"G":
                path.append("MSG")
                n = data[3]
                body = data[4:]
                if n > len(body):                       # the bug: trusts the length byte, like Heartbleed
                    return path, "CRASH: read past the end of the buffer"
    return path, None

def mutate(rng, data):
    d = bytearray(data)
    op = rng.randrange(3)
    if op == 0 and d:
        d[rng.randrange(len(d))] = rng.randrange(256)    # change a byte
    elif op == 1:
        d.insert(rng.randrange(len(d) + 1), rng.randrange(256))   # insert a byte
    elif d:
        del d[rng.randrange(len(d))]                     # delete a byte
    return bytes(d)

def fuzz(guided, budget=200000, seed=1):
    rng = random.Random(seed)
    corpus, seen = [b"AAAAAAAA"], set()
    for i in range(1, budget + 1):
        parent = rng.choice(corpus) if guided else b"AAAAAAAA"
        child = mutate(rng, parent)
        for _ in range(rng.randrange(4)):
            child = mutate(rng, child)
        path, crash = parse(child)
        if crash:
            return i, child, len(corpus)
        key = tuple(path)
        if guided and key not in seen:                   # new coverage: keep this input
            seen.add(key)
            corpus.append(child)
    return None, None, len(corpus)

for guided in (False, True):
    tries, crasher, size = fuzz(guided)
    name = "coverage guided" if guided else "blind random   "
    print(f"{name}: " + (f"crash after {tries:6} inputs, input {crasher!r}, corpus {size}" if tries else f"no crash in 200000 inputs"))
''', long=True)

K.lesson('idea', 'Building security in: the secure development life cycle', f'''
{talk('For a long time security was something tested at the end, if at all. On 15 January 2002, after worms such as Code Red and Nimda had hit Windows servers, Bill Gates sent every Microsoft employee a memo titled Trustworthy Computing, saying that security must come before new features. Microsoft stopped much of its Windows development for security training and code review, and in 2004 made the Security Development Lifecycle, SDL, mandatory for its products. The idea spread: build security into every phase, from requirements and design through coding, testing, release and response, instead of bolting it on afterwards. This is often called shifting left, because security work moves earlier on the project timeline, where flaws are cheaper to fix. Today the main frameworks are the NIST Secure Software Development Framework, SP 800-218 from 2022, which US government suppliers must attest to, OWASP SAMM for measuring a programme’s maturity, OWASP ASVS as a checklist of verifiable requirements, and SLSA for the integrity of the build and supply chain. DevSecOps means doing all of this inside fast automated pipelines, so that every commit is scanned and tested without slowing developers down. This chapter covers the core practices: threat modelling at design time, attack trees to decide where to spend, static analysis and secret scanning on code, fuzzing during testing, and protecting the build pipeline itself, which attackers targeted in the SolarWinds compromise of 2020.')}
{src('Bill Gates, Trustworthy Computing memo (15 January 2002), Microsoft Security Development Lifecycle and STRIDE per element guidance, Kohnfelder and Garg, The Threats to Our Products (Microsoft, 1999), Bruce Schneier, Attack Trees (Dr. Dobb’s Journal, December 1999), Adam Shostack, Threat Modeling: Designing for Security (2014), Threat Modeling Manifesto (2020), NIST SP 800-218 Secure Software Development Framework (2022), OWASP SAMM and ASVS, SLSA specification, Sigstore, Bandit documentation, Michal Zalewski, American Fuzzy Lop (2013), LLVM libFuzzer, Google OSS-Fuzz, CISA and Mandiant reports on SolarWinds (2020 and 2021), US FTC complaint on the Uber 2016 breach.')}
{safe('The scanners here read code and text you give them, and the fuzzer attacks a toy parser in the same program. Only scan and fuzz software you own or are allowed to test.')}
{wwh('A <b>secure development life cycle</b> builds security activities into every stage of making software: requirements, design, coding, testing, release and maintenance.',
     'Design flaws are expensive or impossible to patch later, and many bugs can be caught automatically before release. Customers and regulators now expect proof of secure development.',
     'Model threats when designing, review and scan code as it is written, fuzz and test before release, protect the build and its dependencies, and feed every incident back into the process.')}
{table(['Phase', 'Security activity', 'Tools and outputs'], [
    ['Requirements', 'Security and privacy requirements, abuse cases', 'ASVS level chosen, misuse stories'],
    ['Design', 'Threat modelling, attack trees, secure design review', 'Data flow diagrams, STRIDE lists, mitigations'],
    ['Code', 'Secure coding standards, peer review, static analysis, secret scanning', 'Semgrep, CodeQL, Bandit, gitleaks'],
    ['Build', 'Dependency scanning, signed and reproducible builds', 'SBOM, SCA tools, Sigstore, SLSA levels'],
    ['Test', 'Fuzzing, dynamic scanning, penetration tests', 'AFL++, libFuzzer, OWASP ZAP, reports'],
    ['Release and run', 'Hardening, monitoring, incident response, bug bounty', 'Runbooks, alerts, disclosure policy']])}
''', kw=['secure development life cycle', 'SDL', 'SSDLC', 'Trustworthy Computing', 'shift left', 'DevSecOps', 'NIST SSDF', 'SP 800-218', 'OWASP SAMM', 'OWASP ASVS', 'SLSA', 'abuse cases'])

K.lesson('threats', 'Threat modelling with STRIDE', f'''
{talk('Threat modelling means thinking like an attacker about a design before it is built. Adam Shostack, who led threat modelling at Microsoft, sums it up in four questions: what are we working on, what can go wrong, what are we going to do about it, and did we do a good job. The usual first step is a data flow diagram that shows external entities such as users and other systems, the processes that handle data, the data stores, the flows between them, and the trust boundaries where data crosses from a less trusted zone to a more trusted one, such as from the internet into your network. Most attacks happen at those boundaries. The second step is to ask what can go wrong, and STRIDE, created by Loren Kohnfelder and Praerit Garg at Microsoft in 1999, gives a checklist of six threat types, each the opposite of a security property. Spoofing breaks authentication, Tampering breaks integrity, Repudiation breaks non repudiation, Information disclosure breaks confidentiality, Denial of service breaks availability, and Elevation of privilege breaks authorisation. Microsoft’s STRIDE per element table says which letters apply to which kind of element: processes can suffer all six, data flows can be tampered with, read or blocked, and so on. Each threat found becomes a work item with an owner: mitigate it, transfer it, avoid it by changing the design, or accept it with a recorded reason. Other methods exist, such as PASTA, which is risk centred, LINDDUN for privacy threats, and simple attack trees, but STRIDE remains the most taught. An older scoring scheme, DREAD, was dropped by Microsoft because scores varied too much between people.')}
{viz('cystride')}
{run('stride')}
{table(['Threat', 'Property broken', 'Example', 'Typical mitigation'], [
    ['Spoofing', 'Authentication', 'Logging in with a stolen password', 'MFA, strong session handling'],
    ['Tampering', 'Integrity', 'Changing a price in a request', 'Server side validation, signatures, TLS'],
    ['Repudiation', 'Non repudiation', 'Denying a transfer was made', 'Tamper evident audit logs, signed receipts'],
    ['Information disclosure', 'Confidentiality', 'Reading another user’s files', 'Access control, encryption'],
    ['Denial of service', 'Availability', 'Flooding the login API', 'Rate limits, quotas, autoscaling'],
    ['Elevation of privilege', 'Authorisation', 'A normal user reaching admin functions', 'Least privilege, checks on every request']])}
{note('Threat models are living documents. Update the diagram when the design changes, and review it when an incident shows a threat you missed.')}
''', kw=['threat modelling', 'STRIDE', 'data flow diagram', 'trust boundary', 'STRIDE per element', 'Shostack four questions', 'Kohnfelder', 'Garg', 'PASTA', 'LINDDUN', 'DREAD', 'mitigate transfer avoid accept'])

K.lesson('trees', 'Attack trees: quantifying where to defend', f'''
{talk('Bruce Schneier popularised attack trees in Dr. Dobb’s Journal in December 1999. The attacker’s goal sits at the root, such as read the customer database. Below it are the ways to achieve it, and below those the steps each way needs. A node is either an OR node, where any one child is enough, or an AND node, where all children are needed. Once leaves carry numbers, such as the attacker’s cost, the skill needed or the chance of success, the tree can be evaluated from the bottom up. For cost, an OR node takes the cheapest child and an AND node adds its children. For probability, assuming independence, an AND node multiplies its children’s chances, and an OR node gives one minus the product of the chances of failing. The root then shows the attacker’s cheapest route, and trying a defence means setting a leaf to impossible and evaluating again. This makes the main lesson of security economics visible: a rational attacker takes the weakest path, so strengthening anything other than the weakest path changes little. Fixing an injection bug while a backup bucket sits open to the internet leaves the cheapest attack exactly where it was. Attack trees connect naturally to the MITRE ATT&amp;CK framework, whose techniques make good leaves, and to the risk calculations in the foundations section.')}
{viz('cytree')}
{run('attack_tree')}
{fxs(fx('OR node', 'cost = min(children), P = 1 &minus; &Pi;(1 &minus; p<sub>i</sub>)', 'Any one child works. Probabilities combine as at least one success, if independent.', key=True),
     fx('AND node', 'cost = &Sigma; children, P = &Pi; p<sub>i</sub>', 'Every child is needed. Phish (0.3) and beat MFA (0.2): 0.06.', key=True),
     fx('Value of a defence', '&Delta; = root cost after &minus; root cost before', 'Locking the bucket: 500 &minus; 100 = 400. Fixing only the injection: 100 &minus; 100 = 0.'))}
''', kw=['attack tree', 'Schneier', 'OR node', 'AND node', 'cheapest attack path', 'security economics', 'weakest link', 'MITRE ATT&CK'])

K.lesson('sast', 'Static analysis and secret scanning', f'''
{talk('Static application security testing, SAST, reads source code without running it and looks for dangerous patterns. Simple tools work like the program below: they parse the code into a syntax tree and flag calls such as eval, pickle.loads or subprocess with shell set to true. Bandit does this for Python, and Semgrep lets teams write such rules in a few lines for many languages. Deeper tools such as GitHub CodeQL track data flow, following untrusted input from where it enters, called a source, to dangerous functions, called sinks, so they can tell a SQL query built from user input from one built from constants. No static analyser can be perfect. Rice’s theorem, from 1953, says that no program can decide any interesting property of all programs, so every tool either misses some bugs or raises some false alarms, and good tools let teams tune that balance. Secret scanning is a special, very valuable case. Developers often commit passwords, API keys and private keys by accident. In 2016 attackers found AWS credentials in a private GitHub repository used by Uber engineers, used them to download data on 57 million riders and drivers from cloud storage, and Uber then paid the attackers to stay quiet, which led to criminal charges against its security chief. Scanners such as gitleaks and GitHub’s secret scanning match known key formats, such as AWS keys beginning with AKIA, and also flag strings with high entropy that look random. When a real secret leaks, deleting the commit is not enough, because copies exist in clones and caches. The secret must be revoked and replaced.')}
{run('sast_scan')}
{run('secret_scan')}
{fxs(fx('Character entropy', 'H = &minus;&Sigma; p<sub>c</sub> log<sub>2</sub> p<sub>c</sub> bits per character', 'English words score around 2.5 to 3.5, random base64 keys around 5 to 6. Scanners flag long strings above a threshold such as 4.', key=True),
     fx('Alert quality', 'precision = true findings / all findings', 'A tool with 10 real issues in 40 alerts has precision 0.25, and developers start ignoring it. Tune rules to keep precision high.', key=True))}
{deep('Sources, sinks and taint', '<p>Taint analysis marks values from untrusted sources, such as request parameters, files and environment variables, as tainted. Taint flows through assignments and function calls. Passing a value through a sanitiser, such as an escaping function or a strict parser, removes the taint. A finding is reported when tainted data reaches a sink, such as a SQL execute call, a shell command, eval or an HTML template marked safe. This is how CodeQL and commercial tools find injection paths that cross many files.</p>')}
''', kw=['SAST', 'static analysis', 'syntax tree', 'Bandit', 'Semgrep', 'CodeQL', 'taint analysis', 'sources and sinks', 'Rice theorem', 'false positives', 'secret scanning', 'gitleaks', 'entropy', 'Uber breach 2016', 'key rotation'])

K.lesson('fuzzing', 'Fuzzing: millions of strange inputs', f'''
{talk('Fuzzing means feeding a program huge numbers of malformed or random inputs and watching for crashes, hangs or sanitiser reports. Barton Miller at the University of Wisconsin coined the term in 1988, after a stormy night when line noise on his dial up connection crashed Unix tools, and his class found that random input crashed about a quarter to a third of standard Unix utilities. Pure random fuzzing is weak against programs that check their input step by step, because random bytes almost never pass several checks in a row. The breakthrough was coverage guidance. Michal Zalewski’s American Fuzzy Lop, AFL, released in 2013, instruments the program so that each run reports which branches it took, keeps any input that reaches new branches, and mutates those inputs further. The fuzzer climbs through the program check by check, as in the animation, where a crash that random inputs would need tens of millions of tries to hit appears after about twenty thousand. AFL found hundreds of bugs in widely used software, and libFuzzer and AFL++ continue the line. Google’s OSS-Fuzz, launched in 2016, runs these fuzzers continuously for over a thousand open source projects and has found tens of thousands of bugs, many of them security issues. Fuzzing works best together with sanitisers, which turn silent memory corruption into crashes, and with grammar based or structure aware fuzzers for formats such as PDF, fonts, protocols and JavaScript.')}
{viz('cyfuzz')}
{run('fuzz')}
{fxs(fx('Chance of passing k byte checks at random', 'p = 256<sup>&minus;k</sup>', 'Three exact bytes: 1 in 16777216. Coverage guidance turns this into three steps of about 1 in 256 each.', key=True),
     fx('Expected tries, blind', 'E = 1 / p', 'For k = 3: about 16.8 million inputs, before even counting the length check.'))}
{note('Fuzzing finds bugs, it does not prove their absence. Keep the crashing inputs as regression tests, so the bug never comes back.')}
''', kw=['fuzzing', 'Barton Miller', 'coverage guided fuzzing', 'AFL', 'AFL++', 'libFuzzer', 'OSS-Fuzz', 'corpus', 'mutation', 'instrumentation', 'grammar based fuzzing', 'regression tests'])

K.lesson('supply', 'The build pipeline and software supply chain', f'''
{talk('Modern software is mostly other people’s code: a typical application pulls in hundreds of open source packages, and it is built and shipped by automated pipelines. Attackers have learned that compromising the pipeline or a popular dependency reaches thousands of victims at once. In the SolarWinds attack, discovered in December 2020, intruders, attributed by the US government to Russia’s foreign intelligence service, planted code in the build system of the Orion network management product, so the company itself signed and shipped a backdoored update to about 18000 customers, including US government agencies. In the same years attackers published malicious packages with names close to popular ones, called typosquatting, took over abandoned packages, and in the xz utils case spent two years earning a maintainer’s trust. Defences focus on knowing and controlling what goes into a build. A software bill of materials lists every component. Dependencies are pinned to exact versions and verified with hashes. Software composition analysis tools match components against vulnerability databases. Builds run in isolated, short lived environments from version controlled definitions, and their outputs are signed, for example with Sigstore, so users can check where an artefact came from. The SLSA framework, started by Google in 2021, defines levels of build integrity, up to builds whose provenance can be verified end to end. Pipelines themselves need protection: secrets kept in a vault, branch protection and required reviews, and least privilege tokens for every automated step.')}
{steps('A DevSecOps pipeline for every commit', [
    'Pre commit: secret scanning and formatting hooks on the developer’s machine.',
    'Pull request: peer review, SAST (Semgrep, CodeQL), dependency scan, licence check.',
    'Build: pinned dependencies with hashes, isolated runner, SBOM generated, artefact signed.',
    'Test: unit and integration tests, fuzzing for parsers, dynamic scan of a test deployment.',
    'Deploy: verify signatures and provenance, infrastructure as code checks, least privilege credentials.',
    'Run: monitoring, alerts, and a path for vulnerability reports back into the backlog.'])}
{table(['Supply chain attack', 'Example', 'Defence'], [
    ['Build system compromise', 'SolarWinds Orion (2020)', 'Isolated, reproducible builds, SLSA provenance'],
    ['Malicious maintainer', 'xz utils (2024)', 'Review of releases, funding and support for maintainers'],
    ['Typosquatting package', 'Fake packages on PyPI and npm', 'Pin and verify dependencies, allow lists, registry scanning'],
    ['Compromised CI secret', 'Codecov bash uploader (2021)', 'Short lived tokens, secrets in vaults, script integrity checks'],
    ['Vulnerable dependency', 'Log4Shell (2021)', 'SBOM, SCA alerts, fast patching']])}
''', kw=['software supply chain', 'SolarWinds', 'build system', 'typosquatting', 'dependency confusion', 'SBOM', 'SCA', 'pinning', 'hash verification', 'Sigstore', 'SLSA', 'provenance', 'DevSecOps pipeline', 'Codecov'])

K.lesson('versus', 'Security testing methods compared', f'''
{talk('Testing methods are complementary, because each sees the software from a different angle. Static analysis sees all the code but not how it behaves at runtime. Dynamic scanning sees the running app from outside but not the code. Fuzzing goes deep into parsers. Software composition analysis covers the code you did not write. Penetration testers find the logic flaws that tools miss. A mature programme uses all of them at the stage where each is cheapest.')}
{versus('Ways to find security bugs', ['', 'SAST', 'DAST', 'Fuzzing', 'SCA', 'Manual review and pentest'], [
    ['Looks at', 'Source code', 'Running app from outside', 'Running code with generated inputs', 'Dependencies and versions', 'Design, code and behaviour'],
    ['Finds well', 'Injection patterns, secrets, unsafe calls', 'Misconfiguration, missing headers, XSS', 'Memory bugs, parser crashes', 'Known CVEs in libraries', 'Logic and access control flaws'],
    ['Weakness', 'False positives, no runtime context', 'Shallow coverage', 'Needs harnesses, slow for complex states', 'Only known issues', 'Expensive, not continuous'],
    ['When', 'Every commit', 'Every deployment to test', 'Continuously', 'Every build', 'Before major releases']],
    'Automate SAST, SCA and secret scanning on every change, fuzz the parsers continuously, scan test deployments, and spend human time on design review and logic testing.')}
''', kw=['comparison', 'SAST', 'DAST', 'IAST', 'SCA', 'fuzzing', 'penetration test', 'code review'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner understands that security is part of building software, not an afterthought. A college student can draw a data flow diagram, apply STRIDE, evaluate an attack tree, and write simple scanners and fuzzers. A professional runs threat modelling sessions, maintains a DevSecOps pipeline and tunes tools so developers trust them. Researchers work on precise static analysis, smarter fuzzers that use symbolic execution or machine learning, and verifiable build provenance.')}
{ladder(
    '<p>Know that good software teams plan for attacks, review each other’s code, and keep their tools and libraries up to date.</p>',
    '<p>The SDL phases, data flow diagrams and STRIDE, attack tree maths, SAST with syntax trees, secret scanning with entropy, coverage guided fuzzing, SBOMs and signed builds.</p>',
    '<p>Run threat modelling workshops, write Semgrep and CodeQL rules, build fuzzing harnesses, set up SLSA provenance and Sigstore signing, and measure the programme with OWASP SAMM.</p>',
    '<p>Sound and precise static analysis, symbolic and concolic execution (KLEE, angr), hybrid and ML guided fuzzing, reproducible builds, and formal verification of critical components.</p>')}
{grow('Explain why security belongs in every step of building software.',
      'Model threats and build simple scanners and fuzzers.',
      'Run a secure development programme with tuned automation.')}
''', kw=['beginner', 'expert', 'symbolic execution', 'KLEE', 'angr', 'reproducible builds'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>SDL</b>: Trustworthy Computing memo 2002, Microsoft SDL 2004. Security in every phase. NIST SSDF (SP 800-218), OWASP SAMM and ASVS, SLSA. DevSecOps automates it.',
    '<b>Threat modelling</b>: data flow diagrams, trust boundaries, STRIDE (Kohnfelder and Garg 1999) per element. Mitigate, transfer, avoid or accept. Shostack’s four questions.',
    '<b>Attack trees</b>: OR = min cost and 1 &minus; &Pi;(1 &minus; p), AND = sum of costs and &Pi; p. Defend the weakest path first.',
    '<b>Static analysis</b>: syntax tree rules (Bandit, Semgrep), taint from sources to sinks (CodeQL). Rice’s theorem: never perfect. Secret scanning with patterns and entropy, rotate leaked keys.',
    '<b>Fuzzing</b>: Miller 1988, AFL 2013, coverage guidance climbs check by check. OSS-Fuzz. Pair with sanitisers.',
    '<b>Supply chain</b>: SolarWinds 2020, xz 2024. SBOM, pinned and hashed dependencies, isolated builds, signed artefacts, SLSA provenance.'],
    'Next, Application Security 2.3: ethical hacking, from scoping and reconnaissance to reporting.')}
{files('Three tasks: STRIDE letters per element, attack tree evaluation, and string entropy for secret scanning.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does shifting security left mean?', ['Moving servers', 'Doing security work earlier in development, at design and coding time', 'Using left handed keyboards', 'Testing only in production'], 1, 'Earlier.', 'Flaws found early are cheaper to fix.')
K.quiz('e', 'What does the S in STRIDE stand for?', ['Scanning', 'Spoofing', 'SQL', 'Sandbox'], 1, 'Spoofing.', 'Pretending to be someone else, the opposite of authentication.')
K.quiz('e', 'A developer committed an AWS key to a public repository. What must be done first?', ['Delete the commit', 'Revoke and rotate the key', 'Make the repository private', 'Nothing'], 1, 'Rotate.', 'Copies of the commit already exist elsewhere.')
K.quiz('e', 'What does a fuzzer do?', ['Encrypts files', 'Feeds huge numbers of malformed inputs to a program to find crashes', 'Speeds up builds', 'Formats code'], 1, 'Strange inputs.', 'Barton Miller coined the term in 1988.')
K.quiz('m', 'In a data flow diagram, where do most attacks happen?', ['Inside one process', 'At trust boundaries, where data crosses from less to more trusted zones', 'In comments', 'In the legend'], 1, 'Boundaries.', 'For example from the internet into your network.')
K.quiz('m', 'Which STRIDE threats apply to a data flow in Microsoft’s per element table?', ['S, R', 'T, I, D', 'All six', 'E only'], 1, 'TID.', 'Flows can be changed, read or blocked.')
K.quiz('m', 'In an attack tree, the cost of an OR node is', ['The sum of its children', 'The cheapest child', 'The most expensive child', 'Always zero'], 1, 'Any one works.', 'AND nodes add costs instead.')
K.quiz('m', 'Why can no static analyser be both complete and free of false alarms?', ['Computers are slow', 'Rice’s theorem: non trivial properties of all programs are undecidable', 'Languages change', 'Licences forbid it'], 1, 'Undecidable.', 'Tools trade misses against false alarms.')
K.quiz('m', 'What made AFL so much better than random fuzzing?', ['Faster CPUs', 'It keeps inputs that reach new code branches and mutates them further', 'It reads the source code', 'It uses the GPU'], 1, 'Coverage guidance.', 'It climbs through checks one at a time.')
K.quiz('h', 'In SolarWinds (2020), why did customers trust the malicious update?', ['It was unsigned', 'Attackers changed the vendor’s build system, so the vendor signed and shipped it', 'Customers turned off checks', 'It came by email'], 1, 'Build compromise.', 'Signatures prove origin, not that the build was clean.')
K.quiz('h', 'Fixing a bug on a path that is not the cheapest one in an attack tree mainly', ['Stops all attacks', 'Leaves the cheapest attack cost unchanged', 'Doubles the cost', 'Removes the root'], 1, 'Weakest link.', 'A rational attacker takes the cheapest path.')
K.quiz('h', 'A secret scanner flags a 32 character string with entropy 5.0 bits per character. Why?', ['It is long', 'Random keys use many different characters evenly, giving high entropy, unlike words', 'It contains digits', 'It is in quotes'], 1, 'Looks random.', 'English text is around 2.5 to 3.5.')
K.quiz('h', 'Taint analysis reports a finding when', ['Code is long', 'Data from an untrusted source reaches a dangerous sink without passing a sanitiser', 'A variable is unused', 'Tests fail'], 1, 'Source to sink.', 'This is how CodeQL finds injection paths.')
K.quiz('x', 'In the style of an MIT 6.858 question: a parser checks 4 exact magic bytes before a bug. Roughly how many inputs does blind random fuzzing need to pass them?', ['1024', '256<sup>4</sup> &asymp; 4.3 &times; 10<sup>9</sup>', '256', '4'], 1, '256<sup>&minus;4</sup>.', 'Coverage guidance needs about 4 &times; 256.')
K.quiz('x', 'In the style of an IISc secure software exam: which practice gives verifiable evidence of how an artefact was built?', ['Code comments', 'SLSA provenance signed by the build system', 'A README', 'Manual testing'], 1, 'Provenance.', 'Users can check source, builder and steps before deploying.')

K.calc('e', 'STRIDE per element: how many threats for 1 process and 2 data flows?', '12', '6 + 3 + 3.', ['A process gets all 6 letters.', 'Each data flow gets T, I, D.', eq('6 + 3 + 3 = 12')], check=12)
K.calc('e', 'AND node with child probabilities 0.3 and 0.2. Success probability?', '0.06', 'Multiply.', ['Both steps must work.', '0.3 &times; 0.2.', eq('0.06')], check=0.06)
K.calc('e', 'OR node with child costs 3000, 500 and 100. Its cost?', '100', 'Cheapest.', ['The attacker needs only one child.', 'min(3000, 500, 100).', eq('100')], check=100)
K.calc('m', 'OR node with independent child probabilities 0.06, 0.1 and 0.025. Success probability? Round to 4 decimals.', '0.1752', 'One minus all fail.', ['Fail chances: 0.94, 0.9, 0.975.', 'Product = 0.8248.', eq('1 &minus; 0.8248 = 0.1752')], check=round(1 - 0.94 * 0.9 * 0.975, 4))
K.calc('m', 'Character entropy of "abcdefgh" (8 different characters, once each)?', '3', 'log<sub>2</sub> 8.', ['Each p = 1/8.', 'H = log<sub>2</sub> 8.', eq('3 bits per character')], check=3)
K.calc('m', 'How many random inputs, on average, until the first three bytes are exactly M, S, G?', '16777216', '256<sup>3</sup>.', ['Each byte matches with p = 1/256.', 'Three independent bytes.', eq('256<sup>3</sup> = 16777216')], check=256 ** 3)
K.calc('m', 'A scanner raised 40 alerts, 10 of them real. Precision?', '0.25', 'Real / all.', ['10 true findings.', '40 alerts in all.', eq('10 / 40 = 0.25')], check=0.25)
K.calc('m', 'A diagram has 2 external entities, 3 processes, 2 data stores and 6 data flows. STRIDE per element count?', '48', '2 + 6 + 4 + 3 letters.', ['Entities 2 &times; 2 = 4, processes 3 &times; 6 = 18.', 'Stores 2 &times; 4 = 8, flows 6 &times; 3 = 18.', eq('4 + 18 + 8 + 18 = 48')], check=48)
K.calc('h', 'Entropy of a 32 character string in which all 32 characters are different?', '5', 'log<sub>2</sub> 32.', ['Each character has p = 1/32.', 'H = log<sub>2</sub> 32.', eq('5 bits per character')], check=5)
K.calc('h', 'Blind: 256<sup>3</sup> tries. Guided: about 3 &times; 256 = 768. How many times faster is guided? Round to 2 decimals.', '21845.33', 'Divide.', ['16777216 / 768.', 'Ignores the cost of choosing parents.', eq('21845.33')], check=round(256 ** 3 / 768, 2))
K.calc('h', 'In the attack tree, after locking the backup bucket only, what is the cheapest attack cost?', '500', 'min(3000, 500, &infin;).', ['The backup path becomes impossible.', 'Remaining: 3000 (admin) and 500 (SQL injection).', eq('500')], check=500)
K.calc('h', '400 alerts at precision 0.25. Triage takes 3 minutes per false alarm. Hours wasted?', '15', 'False alarms times time.', ['False alarms = 400 &times; 0.75 = 300.', '300 &times; 3 = 900 minutes.', eq('900 / 60 = 15 hours')], check=15)
K.calc('x', 'Expected random inputs to pass a check of 4 exact bytes?', '4294967296', '256<sup>4</sup>.', ['p = 256<sup>&minus;4</sup>.', 'E = 1/p.', eq('4294967296')], check=256 ** 4)
K.calc('x', 'Three independent attack paths each succeed with probability 0.1. Chance at least one works? Round to 3 decimals.', '0.271', '1 &minus; 0.9<sup>3</sup>.', ['All fail: 0.9<sup>3</sup> = 0.729.', 'Complement.', eq('0.271')], check=round(1 - 0.9 ** 3, 3))

K.assign('stride_letters', 'e', 'STRIDE per element',
         '<p>Write <code>stride_letters(kind)</code> that returns the STRIDE letters for a data flow diagram element: "external entity" gives "SR", "process" gives "STRIDE", "data store" gives "TRID" and "data flow" gives "TID". Return "" for anything else.</p>',
         '''
def stride_letters(kind):
    # your code here
    pass
''', [('stride_letters("process")', 'STRIDE'), ('stride_letters("data flow")', 'TID'), ('stride_letters("external entity")', 'SR'), ('stride_letters("data store")', 'TRID'), ('stride_letters("cloud")', '')],
         '''
def stride_letters(kind):
    table = {"external entity": "SR", "process": "STRIDE", "data store": "TRID", "data flow": "TID"}
    return table.get(kind, "")
''', 'A dictionary with .get and a default does it in one line.', '<p>Counting len(stride_letters(k)) over all elements gives the number of threats to review, as in the calculations above.</p>')
K.assign('tree_cost', 'm', 'Cheapest attack in an attack tree',
         '<p>A tree is a list: <code>["LEAF", cost]</code>, <code>["OR", [children]]</code> or <code>["AND", [children]]</code>. Write <code>tree_cost(node)</code> that returns the attacker’s cheapest cost: a leaf’s cost, the minimum over an OR node’s children, or the sum over an AND node’s children.</p>',
         '''
def tree_cost(node):
    # your code here
    pass
''', [('tree_cost(["LEAF", 7])', 7), ('tree_cost(["OR", [["LEAF", 3000], ["LEAF", 500], ["LEAF", 100]]])', 100), ('tree_cost(["AND", [["LEAF", 2000], ["LEAF", 1000]]])', 3000), ('tree_cost(["OR", [["AND", [["LEAF", 2000], ["LEAF", 1000]]], ["LEAF", 500], ["AND", [["LEAF", 100], ["LEAF", 0]]]]])', 100)],
         '''
def tree_cost(node):
    kind = node[0]
    if kind == "LEAF":
        return node[1]
    costs = [tree_cost(child) for child in node[1]]
    return min(costs) if kind == "OR" else sum(costs)
''', 'Recursion: evaluate the children first, then combine with min or sum.', '<p>The last test is the chapter’s tree: the backup path at cost 100 is the cheapest, so that is where to defend first.</p>')
K.assign('str_entropy', 'h', 'Entropy for secret scanning',
         '<p>Write <code>str_entropy(s)</code> that returns the Shannon entropy of the characters of s in bits per character, H = &minus;&Sigma; p log<sub>2</sub> p, rounded to 2 decimal places. Return 0.0 for an empty string.</p>',
         '''
import math
from collections import Counter

def str_entropy(s):
    # your code here
    pass
''', [('str_entropy("aaaa")', 0.0), ('str_entropy("abcdefgh")', 3.0), ('str_entropy("q8Zr3VbN1xTt6YwP0kLm9sDf2GhJ4cXe")', 5.0), ('str_entropy("")', 0.0), ('str_entropy("aab")', 0.92)],
         '''
import math
from collections import Counter

def str_entropy(s):
    if not s:
        return 0.0
    n = len(s)
    h = -sum(c / n * math.log2(c / n) for c in Counter(s).values())
    return round(abs(h), 2)
''', 'Counter counts characters, then sum p * log2(p) and negate.', '<p>Scanners combine this with length, character classes and known prefixes, because short or structured strings can score high by chance.</p>')

K.must('SDL', 'Trustworthy Computing memo 15 Jan 2002, Microsoft SDL 2004. Shift left. NIST SSDF SP 800-218 (2022), OWASP SAMM, ASVS, SLSA. DevSecOps.')
K.must('Threat modelling', 'DFD with trust boundaries. STRIDE (1999): S auth, T integrity, R non repudiation, I confidentiality, D availability, E authorisation. Per element: entity SR, process all, store TRID, flow TID.')
K.must('Attack trees', 'Schneier 1999. OR: min cost, 1 &minus; &Pi;(1 &minus; p). AND: sum cost, &Pi; p. Fix the weakest path. Fixed leaf = &infin;.')
K.must('Static analysis', 'AST rules (Bandit, Semgrep), taint source to sink (CodeQL). Rice’s theorem. Precision matters. Secret scanning: patterns + entropy, rotate keys (Uber 2016).')
K.must('Fuzzing', 'Miller 1988. AFL 2013 coverage guidance. libFuzzer, AFL++, OSS-Fuzz 2016. 256<sup>&minus;k</sup> blind versus about k &times; 256 guided. Use with ASan.')
K.must('Supply chain', 'SolarWinds 2020 (build compromise, about 18000 customers), xz 2024, typosquatting, Codecov 2021. SBOM, pin and hash, isolated builds, Sigstore, SLSA.')

T = K.topic(
    slug='cy-sdlc', topic='cy-sdlc', step=(2, 'Secure software and ethical hacking', 'cy-a2', 'Memory safety bugs and their defences, building security into development, the ethical hacking method and the human side of attacks.', 'Advanced'),
    title='Secure development: threat models, scanners, fuzzing and the supply chain', short='Secure development', badge='2.2', minutes=80,
    lead='How teams build security into software instead of testing it in at the end: the secure development life cycle, threat modelling with data flow diagrams and STRIDE, attack trees with the maths of cheapest paths, static analysis with syntax trees and taint, secret scanning with entropy, coverage guided fuzzing, and protecting builds and dependencies after SolarWinds.',
    desc='secure development life cycle, SDL, Trustworthy Computing, shift left, DevSecOps, NIST SSDF, OWASP SAMM, ASVS, threat modelling, STRIDE, data flow diagram, trust boundary, attack tree, Schneier, SAST, static analysis, Bandit, Semgrep, CodeQL, taint analysis, Rice theorem, secret scanning, entropy, Uber, fuzzing, AFL, libFuzzer, OSS-Fuzz, coverage guided, software supply chain, SolarWinds, typosquatting, SBOM, Sigstore, SLSA, provenance, DAST, SCA',
    summary='SDL and DevSecOps, STRIDE threat modelling, attack trees, static analysis and secret scanning, fuzzing, supply chain security.',
    keywords=['SDL', 'threat modelling', 'STRIDE', 'attack tree', 'SAST', 'secret scanning', 'fuzzing', 'AFL', 'supply chain', 'SLSA'],
    recap='<p>Think about attacks at design time, defend the weakest path, let tools check every commit, fuzz the code that reads untrusted input, and protect the pipeline that builds it all.</p>',
    added='2026-11-15')
