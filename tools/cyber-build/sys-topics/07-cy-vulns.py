# Network and Systems 3.2: vulnerabilities, CVSS, patching and hardening. Checked against the FIRST CVSS v3.1
# specification and calculator, the FIRST EPSS model page, CISA BOD 22-01 and the KEV catalog, MITRE CVE and CWE,
# the Apache Log4j security page, the OpenSSL advisory of 7 April 2014 (CVE-2014-0160), Microsoft bulletin MS17-010,
# CIS Benchmarks, NIST SP 800-40 Rev. 4 and Google Project Zero's disclosure policy.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-vulns')
K = Kit()

K.code('cvss31', r'''
# CVSS v3.1 base score, exactly as the FIRST specification defines it
import math

W = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
    "AC": {"L": 0.77, "H": 0.44},
    "UI": {"N": 0.85, "R": 0.62},
    "CIA": {"H": 0.56, "L": 0.22, "N": 0.0},
}

def roundup(x):                          # the spec's Roundup: smallest one decimal number >= x, without float noise
    i = round(x * 100000)
    return i / 100000.0 if i % 10000 == 0 else (math.floor(i / 10000) + 1) / 10.0

def score(vector):
    m = dict(part.split(":") for part in vector.split("/")[1:])
    changed = m["S"] == "C"
    pr = {"N": 0.85, "L": 0.68 if changed else 0.62, "H": 0.5 if changed else 0.27}[m["PR"]]
    iss = 1 - (1 - W["CIA"][m["C"]]) * (1 - W["CIA"][m["I"]]) * (1 - W["CIA"][m["A"]])
    impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
    exploit = 8.22 * W["AV"][m["AV"]] * W["AC"][m["AC"]] * pr * W["UI"][m["UI"]]
    if impact <= 0:
        return 0.0, round(iss, 4), round(impact, 4), round(exploit, 4)
    base = roundup(min(1.08 * (impact + exploit), 10)) if changed else roundup(min(impact + exploit, 10))
    return base, round(iss, 4), round(impact, 4), round(exploit, 4)

def severity(s):
    return "None" if s == 0 else "Low" if s < 4 else "Medium" if s < 7 else "High" if s < 9 else "Critical"

examples = {
    "Log4Shell CVE-2021-44228": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
    "Heartbleed CVE-2014-0160": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
    "typical remote code execution": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    "local privilege escalation": "CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
    "reflected XSS (needs a click)": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
}
for name, vec in examples.items():
    base, iss, imp, exp = score(vec)
    print(f"{name:31} {base:4} {severity(base):8} (ISS {iss}, impact {imp}, exploitability {exp})")
''', long=True)

K.code('patch_priority', r'''
# Which patch first? Combine CVSS (how bad), EPSS (how likely to be exploited soon), CISA KEV (already exploited)
# and exposure (can the internet reach it). The findings are made up, the method is how real teams triage.
findings = [
    # (asset, CVE, CVSS base, EPSS probability, in KEV?, internet facing?)
    ("vpn-gateway", "CVE-A", 9.8, 0.94, True, True),
    ("hr-laptop-17", "CVE-B", 9.8, 0.02, False, False),
    ("web-shop", "CVE-C", 7.5, 0.61, True, True),
    ("build-server", "CVE-D", 8.8, 0.05, False, False),
    ("print-server", "CVE-E", 6.5, 0.001, False, False),
    ("mail-relay", "CVE-F", 5.3, 0.40, False, True),
]

def priority(cvss, epss, kev, exposed):
    risk = cvss / 10 * max(epss, 0.01)           # impact times likelihood, with a small floor
    if kev:
        risk += 1.0                              # exploited in the wild: always first
    if exposed:
        risk *= 2                                # reachable from the internet
    return round(risk, 3)

def deadline(cvss, kev):
    if kev:
        return "fix within 14 days (BOD 22-01 style)"
    if cvss >= 9:
        return "fix within 15 days"
    if cvss >= 7:
        return "fix within 30 days"
    return "fix within 90 days"

ranked = sorted(findings, key=lambda f: priority(f[2], f[3], f[4], f[5]), reverse=True)
print(f"{'rank':4} {'asset':13} {'cve':6} {'cvss':>4} {'epss':>6} {'kev':5} {'net':5} {'score':>6}  deadline")
for i, (asset, cve, cvss, epss, kev, net) in enumerate(ranked, 1):
    print(f"{i:<4} {asset:13} {cve:6} {cvss:4} {epss:6.3f} {str(kev):5} {str(net):5} {priority(cvss, epss, kev, net):6}  {deadline(cvss, kev)}")

by_cvss = sorted(findings, key=lambda f: f[2], reverse=True)
print(f"\nSorting by CVSS alone puts {by_cvss[1][0]} (EPSS {by_cvss[1][3]}) above web-shop, which attackers are already using.")
''', long=True)

K.code('version_check', r'''
# Is this version vulnerable? Compare dotted versions as numbers, not as text, against known affected ranges.
def parse(v):
    return tuple(int(part) for part in v.split("."))

# Affected ranges for Log4Shell family bugs in Apache Log4j 2, from the Apache Log4j security page.
# Simplified: the real advisories also list fixed backports on older branches (2.12.x for Java 7, 2.3.x for Java 6).
ADVISORIES = [
    ("CVE-2021-44228 (Log4Shell)", "2.0.0", "2.15.0"),   # affected from 2.0.0 up to, not including, 2.15.0
    ("CVE-2021-45046", "2.0.0", "2.16.0"),
    ("CVE-2021-45105", "2.0.0", "2.17.0"),
    ("CVE-2021-44832", "2.0.0", "2.17.1"),
]

def check(version):
    v = parse(version)
    return [cve for cve, low, fixed in ADVISORIES if parse(low) <= v < parse(fixed)]

print("text comparison says '2.9.1' > '2.15.0':", "2.9.1" > "2.15.0", "(wrong)")
print("number comparison says (2,9,1) > (2,15,0):", parse("2.9.1") > parse("2.15.0"), "(right)")
print()
inventory = {"payments-api": "2.14.1", "search": "2.9.1", "intranet": "2.16.0", "reports": "2.17.0", "new-app": "2.20.0"}
for app, ver in inventory.items():
    hits = check(ver)
    status = "VULNERABLE to " + ", ".join(hits) if hits else "no known Log4j 2 issue in this list"
    print(f"{app:13} log4j {ver:7} {status}")
''', long=True)

K.code('hardening_audit', r'''
# A tiny configuration audit in the style of CIS Benchmarks and Lynis: compare settings with a baseline
SSHD_CONFIG = """
Port 22
PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes
X11Forwarding yes
MaxAuthTries 6
Protocol 2
"""

BASELINE = [
    # (setting, safe value, why)
    ("PermitRootLogin", "no", "log in as a normal user and use sudo, so actions are traceable"),
    ("PasswordAuthentication", "no", "keys cannot be guessed or sprayed like passwords"),
    ("PubkeyAuthentication", "yes", "needed when passwords are off"),
    ("X11Forwarding", "no", "an extra channel most servers never need"),
    ("MaxAuthTries", "4", "fewer guesses per connection"),
]

def parse(text):
    conf = {}
    for line in text.strip().splitlines():
        if line.strip() and not line.startswith("#"):
            key, value = line.split(None, 1)
            conf[key] = value.strip()
    return conf

def audit(conf):
    passed, failed = [], []
    for key, safe, why in BASELINE:
        have = conf.get(key, "(not set)")
        ok = int(have) <= int(safe) if key == "MaxAuthTries" and have.isdigit() else have.lower() == safe
        (passed if ok else failed).append((key, have, safe, why))
    return passed, failed

passed, failed = audit(parse(SSHD_CONFIG))
for key, have, safe, why in failed:
    print(f"FAIL {key:23} is {have:4} should be {safe:4} because {why}")
for key, have, safe, why in passed:
    print(f"PASS {key:23} is {have}")
print(f"score {len(passed)}/{len(BASELINE)} = {len(passed) / len(BASELINE):.0%}")

# Attack surface: every listening service is a door. Close what is not needed.
listening = {22: "ssh", 80: "http", 443: "https", 3306: "mysql", 6379: "redis", 8080: "admin panel"}
needed = {22, 443}
print("close or firewall:", ", ".join(f"{p}/{listening[p]}" for p in sorted(set(listening) - needed)))
''', long=True)

K.code('heartbleed_model', r'''
# Heartbleed (CVE-2014-0160) in miniature: a reply that trusts the length the client claims.
# The "memory" here is a Python bytearray with pretend secrets next to the request buffer.
memory = bytearray(b"HELLO" + b"|user=alice|session=9f2c|privkey=MIIEv...|" + b"." * 16)
BUF = 0                                   # the client's payload was copied to the start of memory

def heartbeat_buggy(payload_len_claimed, payload_len_real):
    # OpenSSL 1.0.1 to 1.0.1f echoed back payload_len_claimed bytes without checking the real length
    return bytes(memory[BUF:BUF + payload_len_claimed])

def heartbeat_fixed(payload_len_claimed, payload_len_real):
    # The fix in 1.0.1g: silently discard a request whose claimed length is longer than what arrived
    if payload_len_claimed > payload_len_real:
        return None
    return bytes(memory[BUF:BUF + payload_len_claimed])

print("honest request, 5 bytes:    ", heartbeat_buggy(5, 5))
print("lying request, claims 50:   ", heartbeat_buggy(50, 5))
print("same lie against the fix:   ", heartbeat_fixed(50, 5))
print("honest request against fix: ", heartbeat_fixed(5, 5))
print()
print("The length field is 16 bits, so one request could leak up to", 2 ** 16 - 1, "bytes, and attackers could repeat it.")
''', long=True)

K.lesson('idea', 'What a vulnerability is, and how the world tracks them', f'''
{talk('A vulnerability is a weakness that an attacker can use to break a security property: to read what they should not, change what they should not, or stop a service. Most are ordinary bugs, a missing check or a wrong assumption, that happen to have security effects. Others are design flaws or unsafe default settings. Because the same flaw appears in thousands of companies at once, the world needs one name for each. In 1999 MITRE started the CVE list, Common Vulnerabilities and Exposures, which gives each flaw an identifier such as CVE-2021-44228. In 2006 MITRE added CWE, Common Weakness Enumeration, which names the kind of mistake, for example CWE-79 for cross site scripting or CWE-125 for an out of bounds read. The US National Vulnerability Database, run by NIST since 2005, adds scores and affected product lists. The numbers keep growing: about 40000 CVEs were published in 2024. A zero day is a flaw that attackers use before the vendor knows about it or has a fix, so defenders have had zero days to prepare. When a researcher finds a flaw, the usual practice is coordinated disclosure: tell the vendor privately, give them time to fix it, then publish. Google Project Zero gives vendors 90 days. Bug bounty programmes pay researchers for reports, an idea Netscape started in 1995, and platforms such as HackerOne now run thousands of them.')}
{src('FIRST, CVSS v3.1 Specification Document (2019) and CVSS v4.0 (2023), FIRST EPSS model documentation, CISA Binding Operational Directive 22-01 and the Known Exploited Vulnerabilities catalog (2021), MITRE CVE and CWE, NIST National Vulnerability Database, NIST SP 800-40 Rev. 4, Guide to Enterprise Patch Management Planning (2022), OpenSSL Security Advisory of 7 April 2014, Apache Log4j security vulnerabilities page, Microsoft Security Bulletin MS17-010, US GAO report on the Equifax breach (2018), CVE-2024-3094 advisories, CIS Benchmarks, Google Project Zero disclosure policy.')}
{safe('Scanning or probing systems you do not own or have written permission to test is illegal in most countries, including under the IT Act 2000 in India and the Computer Fraud and Abuse Act in the US. Every program here works on made up data inside Python.')}
{wwh('A <b>vulnerability</b> is a weakness in software, hardware, configuration or process that an attacker can use to violate confidentiality, integrity or availability.',
     'Almost every attack needs at least one. Finding, scoring and fixing them before attackers use them is the daily work of most security teams.',
     'Each flaw gets a CVE identifier, a CWE class and a CVSS score. Teams then rank them by risk, patch or mitigate them in time, and harden systems so that fewer flaws exist in the first place.')}
{table(['Vulnerability', 'Year', 'Kind of mistake', 'What happened'], [
    ['Heartbleed, CVE-2014-0160', '2014', 'Missing length check, out of bounds read (CWE-125)', 'OpenSSL leaked up to 64 KB of server memory per request'],
    ['EternalBlue, MS17-010', '2017', 'Buffer overflow in Windows SMBv1', 'Used by WannaCry and NotPetya two and three months after the patch'],
    ['Apache Struts, CVE-2017-5638', '2017', 'Input used as code (OGNL injection)', 'Equifax left it unpatched for two months: data of about 147 million people stolen'],
    ['Log4Shell, CVE-2021-44228', '2021', 'Log text treated as a lookup command (JNDI)', 'Remote code execution in countless Java apps, CVSS 10.0'],
    ['MOVEit Transfer, CVE-2023-34362', '2023', 'SQL injection', 'The Cl0p group stole data from thousands of organisations'],
    ['xz utils, CVE-2024-3094', '2024', 'A backdoor planted by a trusted maintainer', 'Found by chance by Andres Freund, who noticed SSH logins were 0.5 s slower']])}
''', kw=['vulnerability', 'CVE', 'CWE', 'NVD', 'zero day', 'coordinated disclosure', 'responsible disclosure', 'bug bounty', 'Project Zero', 'HackerOne', 'Heartbleed', 'EternalBlue', 'Log4Shell', 'Equifax', 'MOVEit', 'xz backdoor'])

K.lesson('heartbleed', 'Anatomy of a real bug: Heartbleed', f'''
{talk('Heartbleed is the classic example of how one missing line can expose half the internet. TLS has a small heartbeat feature, added in 2012, that lets one side send some bytes and ask for them back to show the connection is alive. The request carries its own length field. OpenSSL versions 1.0.1 to 1.0.1f copied as many bytes as the length field claimed, without checking that the request really contained that many. An attacker could send one byte and claim 65535, and the server would reply with 65535 bytes of whatever lay next in its memory: passwords, session cookies, and sometimes the server’s private key. The attack left no trace in normal logs and could be repeated. The bug was found independently by Neel Mehta at Google and by the Finnish company Codenomicon, and disclosed on 7 April 2014 with the fixed version 1.0.1g. Netcraft estimated that about 17 percent of secure web servers, around half a million, were affected. Many companies had to revoke and reissue their certificates, since nobody could prove their keys had not leaked. The fix was a bounds check: if the claimed length is bigger than what arrived, drop the request. Heartbleed also showed a social problem. OpenSSL, used by most of the internet, was maintained by a handful of volunteers, which led to the Core Infrastructure Initiative funding critical open source projects.')}
{viz('cyheartbleed')}
{run('heartbleed_model')}
{fxs(fx('Bytes leaked per request', 'leak = claimed &minus; real, with claimed &le; 2<sup>16</sup> &minus; 1', 'Claim 65535 with a 1 byte payload: 65534 bytes of other memory.', key=True),
     fx('The fix', 'if claimed &gt; real: drop', 'One comparison. Every length that comes from the network must be checked against the buffer it describes.', key=True))}
{deep('Why memory safe languages matter here', '<p>In C, reading past the end of a buffer is not an error, it just returns whatever bytes are there. In Python, Java, Go or Rust, the same mistake raises an error or is caught when the program is compiled, so it becomes a crash instead of a leak. Google and Microsoft have both reported that about 70 percent of their serious security bugs are memory safety bugs, which is why governments now encourage new code to be written in memory safe languages. Application Security has a full chapter on memory safety.</p>')}
''', kw=['Heartbleed', 'CVE-2014-0160', 'OpenSSL', 'TLS heartbeat', 'buffer over-read', 'bounds check', 'CWE-125', 'Neel Mehta', 'Codenomicon', 'memory safety', 'Core Infrastructure Initiative'])

K.lesson('cvss', 'Scoring severity: CVSS v3.1, formula by formula', f'''
{talk('With tens of thousands of flaws a year, teams need a common way to say how bad each one is. The Common Vulnerability Scoring System, maintained by FIRST, does this with a short vector string and fixed formulas. Version 1 came in 2005, version 3.1 in 2019, and version 4.0 in November 2023, but most databases still show 3.1 scores, so this lesson uses it. The base metrics split into two groups. Exploitability metrics say how easy the flaw is to reach and use: the attack vector (from the network, an adjacent network, a local login or physical access), attack complexity, privileges required and whether a user must do something such as click a link. Impact metrics say how much confidentiality, integrity and availability are lost: high, low or none. Scope says whether the damage can spread beyond the vulnerable component, for example from a browser into the operating system. Each value has a weight chosen by the CVSS team from expert surveys. The formulas combine them into an impact score and an exploitability score, add them, cap the total at 10 and round up to one decimal place. The result maps to a label: Low below 4, Medium below 7, High below 9 and Critical from 9. A CVSS score measures severity, not risk. It does not know whether anyone is attacking the flaw, or whether your system is even reachable, which is why the next lesson adds likelihood.')}
{viz('cycvss')}
{run('cvss31')}
{fxs(fx('Impact sub score', 'ISS = 1 &minus; (1 &minus; C)(1 &minus; I)(1 &minus; A)', 'H = 0.56, L = 0.22, N = 0. All high: 1 &minus; 0.44<sup>3</sup> = 0.9148.', key=True),
     fx('Impact', 'scope unchanged: 6.42 &times; ISS<br>scope changed: 7.52 (ISS &minus; 0.029) &minus; 3.25 (ISS &minus; 0.02)<sup>15</sup>', 'Heartbleed: 6.42 &times; 0.56 = 3.5952.', key=True),
     fx('Exploitability', '8.22 &times; AV &times; AC &times; PR &times; UI', 'Network, low complexity, no privileges, no user: 8.22 &times; 0.85 &times; 0.77 &times; 0.85 &times; 0.85 = 3.887.', key=True),
     fx('Base score', 'unchanged: Roundup(min(Impact + Exploitability, 10))<br>changed: Roundup(min(1.08 (Impact + Exploitability), 10))', '0 if Impact &le; 0. Heartbleed: Roundup(7.4822) = 7.5.', key=True),
     fx('Roundup', 'smallest number with one decimal place that is &ge; x', 'Roundup(4.02) = 4.1, Roundup(4.0) = 4.0. Version 3.1 computes it on integers to avoid floating point noise.'))}
{table(['Metric', 'Values and weights'], [
    ['Attack Vector (AV)', 'Network 0.85, Adjacent 0.62, Local 0.55, Physical 0.2'],
    ['Attack Complexity (AC)', 'Low 0.77, High 0.44'],
    ['Privileges Required (PR)', 'None 0.85, Low 0.62 (0.68 if scope changed), High 0.27 (0.5 if scope changed)'],
    ['User Interaction (UI)', 'None 0.85, Required 0.62'],
    ['Scope (S)', 'Unchanged or Changed: picks the impact formula and the 1.08 factor'],
    ['C, I, A', 'High 0.56, Low 0.22, None 0']])}
{deep('What changed in CVSS v4.0', '<p>Version 4.0 (November 2023) replaces Scope with separate impacts on the vulnerable system and on subsequent systems, adds Attack Requirements, splits user interaction into passive and active, and drops the formula in favour of a lookup table built from expert rankings of grouped vectors. It also renames the score types: CVSS-B for base only, CVSS-BT with threat metrics, CVSS-BE with environmental metrics and CVSS-BTE with all three, so readers know what a number includes. The ideas stay the same: reachability, complexity and impact.</p>')}
''', kw=['CVSS', 'CVSS v3.1', 'CVSS v4.0', 'FIRST', 'base score', 'vector string', 'attack vector', 'attack complexity', 'privileges required', 'user interaction', 'scope', 'impact sub score', 'exploitability', 'roundup', 'severity rating'])

K.lesson('prioritise', 'What to fix first: EPSS, KEV and the window of exposure', f'''
{talk('A typical company scanner reports thousands of open vulnerabilities, and more than half of all CVEs score High or Critical, so sorting by CVSS alone leaves far too much at the top. Research by Cyentia and others found that only a few percent of published CVEs are ever exploited in the wild. Three tools help find those few. EPSS, the Exploit Prediction Scoring System from FIRST, first released in 2021, is a machine learning model that estimates the probability that a CVE will be exploited in the next 30 days, using features such as public exploit code, mentions on social media and the type of flaw. It is updated every day. The CISA Known Exploited Vulnerabilities catalog, started in November 2021 with Binding Operational Directive 22-01, lists flaws with reliable evidence of active exploitation, and US federal agencies must fix them within two weeks for recent CVEs. The third input is your own context: is the system on the internet, does it hold sensitive data, are there compensating controls. CERT/CC and CISA turned these questions into a decision tree called SSVC, which ends in Track, Track star, Attend or Act. Bruce Schneier described the window of exposure in 2000: the time between the moment a flaw becomes usable and the moment it is fixed. The 2017 SMB flaw shows why the window matters. Microsoft released patch MS17-010 on 14 March, the EternalBlue exploit leaked on 14 April, and WannaCry struck on 12 May. Every machine it hit had had the patch available for 59 days.')}
{viz('cypatch')}
{run('patch_priority')}
{fxs(fx('Expected number exploited', 'E = &Sigma;<sub>i</sub> EPSS<sub>i</sub>', '10 flaws with EPSS 0.3 each: about 3 expected to be exploited within 30 days.', key=True),
     fx('At least one exploited', 'P = 1 &minus; &Pi;<sub>i</sub> (1 &minus; EPSS<sub>i</sub>)', 'Three flaws at 0.1: 1 &minus; 0.9<sup>3</sup> = 0.271. Many small chances add up.', key=True),
     fx('Window of exposure', 'W = t<sub>patched</sub> &minus; t<sub>exploit available</sub>', 'Exploit on day 31, patched on day 90: 59 days exposed.', key=True),
     fx('Simple risk score', 'risk &asymp; severity &times; likelihood &times; exposure', 'The program uses (CVSS/10) &times; EPSS, plus 1 for KEV, doubled if internet facing.'))}
{table(['Signal', 'Answers', 'Source', 'Limitation'], [
    ['CVSS base', 'How bad if exploited', 'NVD, vendors', 'Ignores whether anyone is exploiting it'],
    ['EPSS', 'How likely exploited in 30 days', 'FIRST, daily', 'A probability, not a certainty, and blind to your setup'],
    ['KEV', 'Is it being exploited now', 'CISA', 'Only confirmed cases, so it lags'],
    ['Asset context', 'Does it matter here', 'Your inventory', 'Only as good as your asset list'],
    ['SSVC', 'What action to take', 'CERT/CC, CISA', 'Needs people to answer the questions']])}
''', kw=['vulnerability prioritisation', 'EPSS', 'KEV', 'CISA', 'BOD 22-01', 'SSVC', 'risk based vulnerability management', 'window of exposure', 'EternalBlue', 'WannaCry', 'MS17-010', 'remediation SLA'])

K.lesson('patching', 'Patch management, versions and the software supply chain', f'''
{talk('Knowing what to fix is half the job. The other half is fixing it without breaking things. NIST SP 800-40 Revision 4, published in 2022, describes patching as preventive maintenance: something planned and routine, not an emergency. A good process starts with an inventory of every device and every piece of software, because you cannot patch what you do not know you have. Patches are tested on a small group first, rolled out in waves, and the result is checked by scanning again. When a patch cannot be applied quickly, teams use mitigations: turn off the vulnerable feature, block the port, or add a web application firewall rule. That is what many did for Log4Shell in December 2021, while waiting for the fixed versions. Log4Shell also showed how hard it is to know what is inside your software. Log4j was buried deep inside other libraries, so many companies spent weeks searching. A software bill of materials, or SBOM, lists every component and version in a product, in standard formats such as SPDX and CycloneDX, and US Executive Order 14028 of May 2021 pushed vendors who sell software to the US government to supply them. Version checks look simple but are easy to get wrong: as text, 2.9.1 sorts after 2.15.0, so versions must be compared as numbers. Finally, the supply chain itself can be attacked. In March 2024 Andres Freund noticed SSH logins taking half a second longer and found a backdoor in xz utils, planted over two years by a contributor who had gained the maintainer’s trust. It was caught just before it reached stable Linux releases.')}
{run('version_check')}
{steps('A patch management cycle (after NIST SP 800-40 Rev. 4)', [
    'Inventory: know every asset and every software component, with an SBOM where possible.',
    'Monitor: watch vendor advisories, the NVD, CERT-In and the CISA KEV catalog.',
    'Prioritise: combine CVSS, EPSS, KEV and asset importance, and set deadlines.',
    'Test: apply the patch to a small, representative group first.',
    'Deploy in waves, with a rollback plan.',
    'Verify: rescan, and confirm the vulnerable version is gone.',
    'Mitigate what cannot be patched yet: disable the feature, isolate the system, add a filtering rule.'])}
{table(['Version', 'CVE-2021-44228', 'CVE-2021-45046', 'CVE-2021-45105', 'CVE-2021-44832'], [
    ['2.14.1', 'vulnerable', 'vulnerable', 'vulnerable', 'vulnerable'],
    ['2.15.0', 'fixed', 'vulnerable', 'vulnerable', 'vulnerable'],
    ['2.16.0', 'fixed', 'fixed', 'vulnerable', 'vulnerable'],
    ['2.17.0', 'fixed', 'fixed', 'fixed', 'vulnerable'],
    ['2.17.1 and later', 'fixed', 'fixed', 'fixed', 'fixed']])}
{note('The four Log4j CVEs in December 2021 were found one after another as researchers looked closer at the first fix. A first patch is often not the last, so keep watching advisories after you patch.')}
''', kw=['patch management', 'NIST SP 800-40', 'asset inventory', 'mitigation', 'compensating control', 'SBOM', 'SPDX', 'CycloneDX', 'Log4j', 'version comparison', 'supply chain attack', 'xz utils', 'CVE-2024-3094', 'Andres Freund'])

K.lesson('hardening', 'Hardening: fewer doors, safer defaults', f'''
{talk('Patching fixes flaws after they are found. Hardening reduces how many flaws can matter in the first place, by shrinking the attack surface: every service, open port, account and feature that is not needed is a possible way in, so remove it. The principle is called least functionality, and it pairs with least privilege from the access control chapter. In practice teams follow published baselines. The Center for Internet Security publishes free CIS Benchmarks for operating systems, databases, cloud platforms and more, with each setting explained and checked by tools. The US Defense Information Systems Agency publishes similar guides called STIGs. Typical items are simple: disable root login over SSH, use keys instead of passwords, turn off unused services, enable the host firewall, turn on automatic updates and logging, and encrypt disks. Tools such as Lynis, OpenSCAP and the CIS-CAT assessor compare a machine with a baseline and report failures. Vulnerability scanners such as Nessus and the open source OpenVAS look for known flaws from the outside. Configuration drifts over time as people make quick changes, so modern teams define it as code, with Ansible or Terraform, and rebuild systems from a hardened image rather than fixing them by hand. Misconfiguration is now one of the most common causes of breaches, especially in the cloud, where one storage bucket set to public can expose millions of records.')}
{run('hardening_audit')}
{table(['Area', 'Hardening step', 'Why'], [
    ['Services', 'Disable everything not needed, close ports at the firewall', 'Each listening service is a door'],
    ['Remote login', 'SSH keys only, no root login, MFA for admin portals', 'Stops password guessing and spraying'],
    ['Accounts', 'Remove defaults, rename or disable built in admin, least privilege', 'Default passwords are on public lists'],
    ['Updates', 'Automatic security updates, supported versions only', 'End of life software gets no fixes'],
    ['Logging', 'Central logs with time sync', 'Needed for detection and investigation'],
    ['Data', 'Disk encryption, secure backups', 'Lost devices and ransomware'],
    ['Boot', 'Secure Boot, firmware updates, BIOS password', 'Stops boot level malware']])}
{fxs(fx('Baseline compliance', 'score = passed checks / total checks', 'The sample sshd_config passes 1 of 5: 20%.', key=True),
     fx('Attack surface (rough count)', 'surface &asymp; open ports + exposed services + accounts + features', 'Closing 4 of 6 ports removes two thirds of the network doors.'))}
''', kw=['hardening', 'attack surface', 'least functionality', 'CIS Benchmarks', 'CIS Controls', 'DISA STIG', 'Lynis', 'OpenSCAP', 'Nessus', 'OpenVAS', 'sshd_config', 'configuration drift', 'infrastructure as code', 'misconfiguration'])

K.lesson('versus', 'CVE, CWE, CVSS, EPSS and KEV compared', f'''
{talk('These acronyms are easy to confuse, and exams like to test them. CVE names one specific flaw in one product. CWE names the type of mistake behind it, and one CWE covers thousands of CVEs. CVSS scores how severe a flaw is. EPSS estimates how likely it is to be exploited soon. KEV records that it has been exploited. Related, and also often mixed up, are three kinds of testing. A vulnerability scan is automated and broad. A penetration test is a time boxed human attempt to break in and prove impact. A red team exercise copies a real adversary over weeks, to test detection and response as well as prevention.')}
{versus('The vulnerability vocabulary', ['', 'CVE', 'CWE', 'CVSS', 'EPSS', 'KEV'], [
    ['Is', 'An identifier for one flaw', 'A class of weakness', 'A severity score 0 to 10', 'A probability 0 to 1', 'A list of exploited flaws'],
    ['Example', 'CVE-2014-0160', 'CWE-125 out of bounds read', '7.5 High', '0.94', 'Listed, due in 2 weeks'],
    ['Run by', 'MITRE and CNAs', 'MITRE', 'FIRST', 'FIRST', 'CISA'],
    ['Since', '1999', '2006', '2005 (v3.1 2019)', '2021', '2021'],
    ['Answers', 'Which flaw', 'What kind of mistake', 'How bad', 'How likely soon', 'Is it happening']],
    'Use CVE to name it, CWE to learn from it, CVSS for severity, EPSS and KEV for urgency, and your own asset context to decide.')}
{versus('Three ways to test', ['', 'Vulnerability scan', 'Penetration test', 'Red team'], [
    ['Done by', 'Tools such as Nessus or OpenVAS', 'Skilled testers', 'A team acting as an adversary'],
    ['Goal', 'Find known flaws broadly', 'Exploit flaws to prove impact', 'Test detection and response'],
    ['How often', 'Weekly or continuous', 'Yearly or per release', 'Occasionally'],
    ['Output', 'Long list of findings', 'Report with proven attack paths', 'Lessons for the blue team']],
    'Scans find what is known, pentests prove what matters, red teams test whether anyone notices.')}
''', kw=['CVE versus CWE', 'CVSS versus EPSS', 'KEV', 'vulnerability scan', 'penetration test', 'red team', 'CNA'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner turns on automatic updates and removes software they do not use. A college student can compute a CVSS score by hand, explain why EPSS and KEV change the order of work, and audit a configuration against a baseline. A professional runs a vulnerability management programme for thousands of assets, with SBOMs and deadlines. Researchers study how to predict exploitation, how to find bugs automatically with fuzzing, and how to secure the open source supply chain.')}
{ladder(
    '<p>Install updates promptly, remove unused apps, and turn on automatic updates and the firewall.</p>',
    '<p>CVE, CWE and NVD, CVSS v3.1 formulas, EPSS and KEV for priority, the window of exposure, version ranges, and CIS style hardening.</p>',
    '<p>Run scanners and triage results, write patch SLAs, build SBOMs, apply SSVC, handle mitigations when patches are late, and report to management with metrics such as mean time to remediate.</p>',
    '<p>Exploit prediction models, coverage guided fuzzing (AFL, libFuzzer, OSS-Fuzz), automated patch generation, supply chain security frameworks such as SLSA and Sigstore, and formal verification of critical code.</p>')}
{grow('Explain what a vulnerability and a patch are.',
      'Score, rank and audit with real formulas and data.',
      'Run a vulnerability programme and study bug finding at scale.')}
''', kw=['beginner', 'expert', 'fuzzing', 'OSS-Fuzz', 'SLSA', 'Sigstore', 'mean time to remediate'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Names</b>: CVE for one flaw (1999), CWE for the kind of mistake (2006), NVD for scores and products. Zero days, coordinated disclosure, bug bounties.',
    '<b>Heartbleed</b>: a trusted length field leaked up to 64 KB per request. The fix was one bounds check. Memory safe languages remove the class.',
    '<b>CVSS v3.1</b>: ISS = 1 &minus; (1 &minus; C)(1 &minus; I)(1 &minus; A), impact 6.42 &times; ISS, exploitability 8.22 &times; AV &times; AC &times; PR &times; UI, Roundup. Severity, not risk.',
    '<b>Priority</b>: EPSS for likelihood, KEV for active exploitation, asset exposure, SSVC. WannaCry hit machines unpatched for 59 days.',
    '<b>Patching</b>: inventory, monitor, prioritise, test, deploy, verify, mitigate. SBOMs, numeric version checks, supply chain attacks such as xz.',
    '<b>Hardening</b>: least functionality, CIS Benchmarks and STIGs, SSH keys and no root login, closed ports, configuration as code.'],
    'This completes Network and Systems Security. Next, Application Security 1.1: how the web works and the OWASP Top 10.')}
{files('Three tasks: the CVSS impact sub score, the CVSS Roundup function, and a full CVSS v3.1 base scorer.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is a CVE identifier?', ['A type of malware', 'A unique name for one specific publicly known vulnerability', 'A severity score', 'A firewall rule'], 1, 'One flaw, one ID.', 'For example CVE-2021-44228 is Log4Shell.')
K.quiz('e', 'What is a zero day vulnerability?', ['A flaw found on 1 January', 'A flaw attackers use before the vendor knows or has a fix', 'A flaw with score 0', 'A flaw fixed the same day'], 1, 'No warning.', 'Defenders had zero days to prepare.')
K.quiz('e', 'What does hardening a system mean?', ['Buying faster hardware', 'Removing unneeded services and applying safe settings to shrink the attack surface', 'Encrypting all email', 'Adding more users'], 1, 'Fewer doors.', 'CIS Benchmarks list the settings.')
K.quiz('e', 'Coordinated disclosure means', ['Posting the bug on social media first', 'Telling the vendor privately and publishing after a fix or a deadline', 'Selling the bug', 'Never telling anyone'], 1, 'Vendor first.', 'Project Zero gives vendors 90 days.')
K.quiz('m', 'CWE-125 describes', ['One product bug', 'A class of weakness: out of bounds read', 'A CVSS metric', 'A patch'], 1, 'Kind of mistake.', 'Heartbleed is an instance of it.')
K.quiz('m', 'Which CVSS v3.1 metric changes the impact formula and adds the 1.08 factor?', ['Attack Vector', 'Scope', 'User Interaction', 'Confidentiality'], 1, 'Scope.', 'Changed scope means damage spreads beyond the vulnerable component.')
K.quiz('m', 'Heartbleed scores 7.5 rather than higher because', ['It was easy to fix', 'It harms only confidentiality: I:N and A:N', 'It needs a login', 'It is local only'], 1, 'C:H/I:N/A:N.', 'CVSS measures technical severity, not how many systems were affected.')
K.quiz('m', 'What does EPSS estimate?', ['Severity', 'The probability a CVE is exploited in the next 30 days', 'Cost of a patch', 'Number of affected users'], 1, 'Likelihood.', 'FIRST updates it daily from exploit and threat data.')
K.quiz('m', 'As text, which version string sorts higher?', ['"2.15.0"', '"2.9.1"', 'They are equal', 'It depends on the locale'], 1, 'Character by character.', '"9" &gt; "1", so text comparison is wrong. Compare tuples of integers.')
K.quiz('h', 'Why did WannaCry succeed in 2017 even though a patch existed?', ['There was no patch', 'Many organisations had not installed MS17-010, released 59 days earlier', 'It used a zero day', 'It only hit Linux'], 1, 'Window of exposure.', 'Fast patching of exploited flaws is one of the most effective controls.')
K.quiz('h', 'A flaw has CVSS 9.8 but EPSS 0.01 and sits on an isolated lab machine. Another has CVSS 7.5, is in KEV and faces the internet. Which first?', ['The 9.8 one', 'The 7.5 one in KEV', 'Neither', 'Both on the same day'], 1, 'Risk, not severity.', 'Active exploitation and exposure outrank a higher base score.')
K.quiz('h', 'What does an SBOM let a company do quickly after a new library flaw?', ['Rewrite the library', 'Find every product that contains the affected component and version', 'Score the flaw', 'Block all traffic'], 1, 'Inventory.', 'During Log4Shell, teams without one spent weeks searching.')
K.quiz('h', 'How was the xz utils backdoor (CVE-2024-3094) found?', ['By an antivirus scan', 'An engineer noticed SSH logins were about 0.5 s slower and investigated', 'The attacker confessed', 'A CVSS scan'], 1, 'Curiosity.', 'It had been planted over two years by a trusted contributor.')
K.quiz('x', 'In the style of an MIT 6.5660 question: for CVSS v3.1 with scope unchanged and C = I = A = High, what is the maximum base score?', ['10.0', '9.8', '9.0', '8.8'], 1, '5.8731 + 3.887.', 'Roundup(9.7601) = 9.8. Only a changed scope reaches 10.0.')
K.quiz('x', 'In the style of an IIT Bombay security course exam: 50 open flaws each have EPSS 0.02, independently. The chance at least one is exploited within 30 days is closest to', ['2%', '64%', '100%', '20%'], 1, '1 &minus; 0.98<sup>50</sup>.', 'About 0.636. Many low probabilities together are not low.')

K.calc('e', 'ISS for C:H, I:N, A:N in CVSS v3.1?', '0.56', 'Only C counts.', ['1 &minus; (1 &minus; 0.56)(1)(1).', '= 0.56.', eq('ISS = 0.56')], check=0.56)
K.calc('e', 'Roundup(4.02) in CVSS v3.1?', '4.1', 'Always up.', ['Smallest one decimal number &ge; 4.02.', '4.1.', eq('4.1')], check=4.1)
K.calc('e', 'A heartbeat request claims 100 bytes but carries 4. How many extra bytes does a buggy server leak?', '96', 'Claimed minus real.', ['The server copies 100 bytes starting at the payload.', 'Only 4 of them are the payload: 100 &minus; 4.', eq('96 bytes')], check=96)
K.calc('m', 'Exploitability for AV:N, AC:L, PR:N, UI:N. Round to 3 decimals.', '3.887', 'Multiply.', ['Weights: AV:N 0.85, AC:L 0.77, PR:N 0.85, UI:N 0.85.', '8.22 &times; 0.85 &times; 0.77 &times; 0.85 &times; 0.85.', eq('3.887')], check=3.887)
K.calc('m', 'ISS for C:H, I:H, A:H? Round to 4 decimals.', '0.9148', '1 &minus; 0.44<sup>3</sup>.', ['0.44<sup>3</sup> = 0.085184.', '1 &minus; 0.085184.', eq('0.9148')], check=0.9148)
K.calc('m', 'Heartbleed (scope unchanged, C:H only): Impact = 6.42 &times; ISS. Round to 4 decimals.', '3.5952', '6.42 &times; 0.56.', ['ISS = 0.56 because only C is High.', 'Scope unchanged, so Impact = 6.42 &times; ISS = 6.42 &times; 0.56.', eq('3.5952')], check=3.5952)
K.calc('m', 'Heartbleed base score: Roundup(3.5952 + 3.887)?', '7.5', 'Add then round up.', ['3.5952 + 3.887 = 7.4822.', 'Roundup gives 7.5.', eq('7.5 High')], check=7.5)
K.calc('m', '10 open flaws each have EPSS 0.3. Expected number exploited within 30 days?', '3', 'Sum of probabilities.', ['Expected value of a sum is the sum of expected values.', 'E = 10 &times; 0.3.', eq('3')], check=3)
K.calc('h', 'Three flaws each with EPSS 0.1, independent. Probability at least one is exploited? Round to 3 decimals.', '0.271', 'Complement.', ['1 &minus; 0.9<sup>3</sup>.', '1 &minus; 0.729.', eq('0.271')], check=0.271)
K.calc('h', 'Exploit public on day 31, you patch on day 90. Window of exposure in days?', '59', 'Subtract.', ['Exposure starts when the exploit is public, day 31.', 'It ends when you patch, day 90: 90 &minus; 31.', eq('59 days')], check=59)
K.calc('h', 'Same vector as a remote code execution flaw but with UI:R (user must click): AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H. Base score?', '8.8', 'Exploitability falls to 2.8353.', ['Impact 5.8731.', 'Exploitability 8.22 &times; 0.85 &times; 0.77 &times; 0.85 &times; 0.62 = 2.8353.', 'Roundup(8.7084) = 8.8.', eq('8.8 High')], check=8.8)
K.calc('h', 'A team patches 150 servers a day. How many whole days to patch 2000 servers?', '14', 'Round up.', ['2000 / 150 = 13.33.', 'Round up.', eq('14 days')], check=14)
K.calc('x', 'Local privilege escalation AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H. Exploitability rounded to 4 decimals?', '1.8346', 'PR:L = 0.62 when scope unchanged.', ['Weights: AV:L 0.55, AC:L 0.77, PR:L 0.62, UI:N 0.85.', '8.22 &times; 0.55 &times; 0.77 &times; 0.62 &times; 0.85.', eq('1.8346')], check=1.8346)
K.calc('x', '50 flaws each EPSS 0.02, independent. Probability at least one exploited? Round to 3 decimals.', '0.636', 'Complement.', ['0.98<sup>50</sup> = 0.3642.', '1 &minus; 0.3642.', eq('0.636')], check=0.636)

K.assign('cvss_iss', 'e', 'The CVSS impact sub score',
         '<p>Write <code>cvss_iss(c, i, a)</code> where each argument is one of "H", "L" or "N". Use the weights H = 0.56, L = 0.22, N = 0 and return ISS = 1 &minus; (1 &minus; C)(1 &minus; I)(1 &minus; A), rounded to 4 decimal places.</p>',
         '''
def cvss_iss(c, i, a):
    # your code here
    pass
''', [('cvss_iss("H", "H", "H")', 0.9148), ('cvss_iss("H", "N", "N")', 0.56), ('cvss_iss("L", "L", "N")', 0.3916), ('cvss_iss("N", "N", "N")', 0.0)],
         '''
def cvss_iss(c, i, a):
    w = {"H": 0.56, "L": 0.22, "N": 0.0}
    return round(1 - (1 - w[c]) * (1 - w[i]) * (1 - w[a]), 4)
''', 'Put the weights in a dictionary and apply the formula.', '<p>The product form means a second high impact adds less than the first: one H gives 0.56, two give 0.8064, three give 0.9148.</p>')
K.assign('roundup', 'm', 'The CVSS Roundup function',
         '<p>Write <code>roundup(x)</code> that returns the smallest number with one decimal place that is greater than or equal to x, as CVSS v3.1 defines it. Work on integers to avoid floating point noise: multiply by 100000 and round, and if the result is a multiple of 10000 return it divided by 100000, otherwise return (floor(i / 10000) + 1) / 10.</p>',
         '''
import math

def roundup(x):
    # your code here
    pass
''', [('roundup(4.02)', 4.1), ('roundup(4.0)', 4.0), ('roundup(7.4822)', 7.5), ('roundup(9.7601)', 9.8), ('roundup(4.000001)', 4.0)],
         '''
import math

def roundup(x):
    i = round(x * 100000)
    if i % 10000 == 0:
        return i / 100000.0
    return (math.floor(i / 10000) + 1) / 10.0
''', 'Scale to an integer first, then decide.', '<p>The last test shows why: 4.000001 rounds to 400000 at five decimals, so it stays 4.0. A plain math.ceil(x * 10) / 10 would give 4.1, and earlier CVSS calculators disagreed on such cases.</p>')
K.assign('cvss31', 'h', 'A full CVSS v3.1 base scorer',
         '<p>Write <code>cvss31(vector)</code> for a vector such as <code>"CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"</code>. Use the weights from the lesson (remember that PR depends on scope), compute ISS, Impact, Exploitability and the base score with Roundup, and return the base score as a float.</p>',
         '''
import math

def cvss31(vector):
    # your code here
    pass
''', [('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")', 9.8), ('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")', 10.0), ('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N")', 7.5), ('cvss31("CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H")', 7.8), ('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N")', 6.1), ('cvss31("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N")', 0.0)],
         '''
import math

def roundup(x):
    i = round(x * 100000)
    return i / 100000.0 if i % 10000 == 0 else (math.floor(i / 10000) + 1) / 10.0

def cvss31(vector):
    m = dict(part.split(":") for part in vector.split("/")[1:])
    changed = m["S"] == "C"
    av = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}[m["AV"]]
    ac = {"L": 0.77, "H": 0.44}[m["AC"]]
    pr = {"N": 0.85, "L": 0.68 if changed else 0.62, "H": 0.5 if changed else 0.27}[m["PR"]]
    ui = {"N": 0.85, "R": 0.62}[m["UI"]]
    w = {"H": 0.56, "L": 0.22, "N": 0.0}
    iss = 1 - (1 - w[m["C"]]) * (1 - w[m["I"]]) * (1 - w[m["A"]])
    impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
    if impact <= 0:
        return 0.0
    exploit = 8.22 * av * ac * pr * ui
    total = 1.08 * (impact + exploit) if changed else impact + exploit
    return roundup(min(total, 10))
''', 'Split on "/" and ":" into a dictionary, pick weights, then follow the four formulas in order.', '<p>Compare your answers with the FIRST online calculator. The no impact case returns 0.0 before the exploitability is even used, as the specification says.</p>')

K.must('Names', 'CVE (MITRE 1999) = one flaw, CWE (2006) = kind of mistake, NVD = scores. Zero day. Coordinated disclosure, Project Zero 90 days, bug bounties (Netscape 1995).')
K.must('Heartbleed', 'CVE-2014-0160, OpenSSL 1.0.1 to 1.0.1f, fixed 1.0.1g on 7 April 2014. Trusted length field, up to 64 KB per request. Fix: drop if claimed &gt; real. CWE-125.')
K.must('CVSS v3.1', 'ISS = 1 &minus; (1 &minus; C)(1 &minus; I)(1 &minus; A). Impact 6.42 &times; ISS (unchanged). Exploitability 8.22 &times; AV &times; AC &times; PR &times; UI, max 3.887. Roundup. Bands 4, 7, 9.')
K.must('Priority', 'EPSS = P(exploited in 30 days), FIRST 2021. KEV (CISA, BOD 22-01, 2 weeks). SSVC. Window of exposure. MS17-010 to WannaCry = 59 days.')
K.must('Patching', 'Inventory, monitor, prioritise, test, deploy in waves, verify, mitigate. NIST SP 800-40r4. SBOM (SPDX, CycloneDX). Compare versions as integers. xz 2024.')
K.must('Hardening', 'Least functionality, attack surface. CIS Benchmarks, STIGs, Lynis, OpenSCAP. SSH keys, no root login, closed ports, updates, logs, config as code.')

T = K.topic(
    slug='cy-vulns', topic='cy-vulns', step=(3, 'Malware and hardening', 'cy-s3', 'How malicious software spreads and is detected, how vulnerabilities are scored, and how systems are hardened and patched.', 'Intermediate'),
    title='Vulnerabilities: CVE, CVSS, patching and hardening', short='Vulnerabilities', badge='3.2', minutes=80,
    lead='How the world names, scores and fixes security flaws: CVE and CWE, the anatomy of Heartbleed, the CVSS v3.1 formulas worked by hand, EPSS and the CISA KEV list for deciding what to fix first, the window of exposure from MS17-010 to WannaCry, patch management with SBOMs and version checks, and hardening against CIS style baselines.',
    desc='vulnerability, CVE, CWE, NVD, zero day, coordinated disclosure, bug bounty, Project Zero, Heartbleed, CVE-2014-0160, OpenSSL, buffer over-read, memory safety, CVSS, CVSS v3.1, CVSS v4.0, base score, attack vector, scope, impact sub score, exploitability, roundup, EPSS, KEV, CISA, BOD 22-01, SSVC, window of exposure, EternalBlue, MS17-010, WannaCry, Equifax, Log4Shell, Log4j, MOVEit, xz backdoor, patch management, NIST SP 800-40, SBOM, SPDX, CycloneDX, supply chain, hardening, attack surface, CIS Benchmarks, STIG, Lynis, OpenSCAP, Nessus, OpenVAS, penetration test, red team',
    summary='CVE and CWE, Heartbleed, CVSS v3.1 maths, EPSS and KEV priority, patch management and SBOMs, system hardening.',
    keywords=['CVE', 'CVSS', 'EPSS', 'KEV', 'Heartbleed', 'patching', 'SBOM', 'hardening', 'CIS Benchmarks', 'Log4Shell'],
    recap='<p>Every system has flaws. Name them with CVE, score them with CVSS, rank them by likelihood and exposure, patch fast, and harden so fewer flaws matter.</p>',
    added='2026-11-15')
