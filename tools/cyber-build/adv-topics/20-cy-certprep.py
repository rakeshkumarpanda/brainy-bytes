# Advanced 5.1: certification revision. Exam facts checked against the official outlines and exam pages: CompTIA
# Security+ SY0-701 (2023) and CySA+ CS0-003 (2023), the ISC2 CISSP outline effective April 2024 (CAT of 100 to 150
# items in 3 hours), ISC2 Certified in Cybersecurity, and the EC-Council CEH exam page. Process facts from NIST SP
# 800-61 Revisions 2 (2012) and 3 (2025), NIST SP 800-207 (zero trust), RFC 3227 (order of volatility), GDPR
# Article 33, FIPS 197, FIPS 180-4, FIPS 203 and 204 (2024) and NIST SP 800-57 Part 1 (key sizes). Outlines change
# every few years, so the page tells readers to check the current outline before booking.
import math

from cvkit import Kit, fx, fxs, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, grow
from cykit import talk

chapter('cy-certprep')
K = Kit()

K.code('port_drill', r'''
# A port and protocol drill: the facts every security exam expects you to know
import random

PORTS = {
    20: "FTP data", 21: "FTP control", 22: "SSH, SFTP, SCP", 23: "Telnet (plain text, avoid)",
    25: "SMTP", 53: "DNS", 67: "DHCP server", 80: "HTTP", 88: "Kerberos", 110: "POP3",
    123: "NTP", 143: "IMAP", 161: "SNMP", 389: "LDAP", 443: "HTTPS", 445: "SMB",
    514: "Syslog", 636: "LDAPS", 993: "IMAPS", 995: "POP3S", 1812: "RADIUS authentication",
    3389: "RDP",
}
SECURE = {"Telnet (plain text, avoid)": "SSH 22", "HTTP": "HTTPS 443", "LDAP": "LDAPS 636",
          "IMAP": "IMAPS 993", "POP3": "POP3S 995", "FTP control": "SFTP 22 or FTPS 990"}

random.seed(7)
quiz = random.sample(sorted(PORTS), 8)
for port in quiz:
    print(f"port {port:5d}  ->  {PORTS[port]}")

print("\nplain text protocol and its secure replacement:")
for old, new in SECURE.items():
    print(f"  {old:28s} -> {new}")

well_known = sum(1 for p in PORTS if p < 1024)
print(f"\n{well_known} of {len(PORTS)} ports here are well known (below 1024), so only administrators can open them on Linux by default")
''')

K.code('revision_maths', r'''
# Every formula of the subject in one small program, so you can check your exam answers
import math

# 1. Risk (Foundations 1.2 and Operations 2.3)
asset_value, exposure, aro = 200000, 0.25, 0.4
sle = asset_value * exposure
ale = sle * aro
print(f"risk: SLE = {asset_value} x {exposure} = {sle:.0f}, ALE = SLE x ARO = {ale:.0f} per year")
control_cost, ale_after = 12000, 4000
print(f"      control value = ALE before - ALE after - cost = {ale - ale_after - control_cost:.0f}")

# 2. Passwords and brute force (Foundations 1.3, Systems 2.1)
length, alphabet = 12, 62
bits = length * math.log2(alphabet)
guesses_per_second = 1e10
years = 2 ** bits / 2 / guesses_per_second / (3600 * 24 * 365)
print(f"password: {length} characters from {alphabet}: {bits:.1f} bits, average crack time {years:.2e} years at 1e10 per second")

# 3. Hash collisions: the birthday bound (Crypto 1.3)
n = 128
print(f"birthday: a {n} bit hash needs about 2^{n // 2} = {2 ** (n // 2):.2e} tries for a 50% collision chance")

# 4. Toy RSA (Crypto 2.2), numbers far too small for real use
p, q, e = 61, 53, 17
N, phi = p * q, (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = 65
c = pow(m, e, N)
print(f"RSA: N = {N}, phi = {phi}, d = {d}, encrypt {m} -> {c}, decrypt -> {pow(c, d, N)}")

# 5. Diffie Hellman (Crypto 2.3)
P, g, a, b = 23, 5, 6, 15
A, B = pow(g, a, P), pow(g, b, P)
print(f"DH: A = {A}, B = {B}, shared secret {pow(B, a, P)} = {pow(A, b, P)}")

# 6. Alerts and the base rate (Operations 1.1, Advanced 1.1)
prior, tpr, fpr = 0.001, 0.99, 0.01
ppv = tpr * prior / (tpr * prior + fpr * (1 - prior))
print(f"base rate: detector with 99% TPR and 1% FPR, 1 in 1000 events bad: P(bad | alert) = {ppv:.3f}")

# 7. Availability (Foundations 1.2, Operations 1.2)
mtbf, mttr = 2000, 4
avail = mtbf / (mtbf + mttr)
print(f"availability: {mtbf} / ({mtbf} + {mttr}) = {avail:.5f}, downtime {(1 - avail) * 8760:.1f} hours a year")
for nines in (0.999, 0.9999, 0.99999):
    print(f"      {nines * 100:g}% up means {(1 - nines) * 525600:.1f} minutes down a year")

# 8. Differential privacy (Advanced 2.3)
eps = 0.5
print(f"DP: Laplace scale for a count at eps {eps} is b = 1 / eps = {1 / eps:.1f}, attack advantage at most e^eps - 1 = {math.exp(eps) - 1:.3f}")
''')

K.code('leitner', r'''
# Spaced repetition with Leitner boxes: review a card less often each time you get it right
import random

random.seed(4)
cards = ["port 22", "port 443", "AES block size", "SHA-256 length", "ALE formula", "RTO vs RPO",
         "order of volatility", "NIST IR phases", "Kerberos port", "RSA d", "Laplace scale", "Krum"]
skill = {c: random.uniform(0.3, 0.7) for c in cards}   # chance of recalling each card at the start
box = {c: 1 for c in cards}                              # every card starts in box 1
EVERY = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}                  # box k is reviewed every EVERY[k] days

reviews = 0
for day in range(1, 31):
    for c in cards:
        if day % EVERY[box[c]] != 0:
            continue
        reviews += 1
        if random.random() < skill[c]:
            box[c] = min(5, box[c] + 1)                  # right: move up, see it less often
            skill[c] = min(0.98, skill[c] + 0.05)        # each correct recall makes the memory stronger
        else:
            box[c] = 1                                   # wrong: back to box 1, see it daily
    if day in (1, 7, 14, 30):
        counts = [sum(1 for c in cards if box[c] == k) for k in range(1, 6)]
        print(f"day {day:2d}: cards in boxes 1 to 5 = {counts}")

print(f"\n{reviews} reviews in 30 days instead of {len(cards) * 30} for daily review of every card")
print("weak cards:", [c for c in cards if box[c] <= 2])
''', long=True)

K.lesson('map', 'How security certifications work', f'''
{talk('Security certifications grew up with the industry. ISC2 was founded in 1989 and gave the first CISSP exams in 1994. In 2004 the CISSP became the first information security credential accredited under the international standard ISO 17024, which sets rules for how a certification body must work. CompTIA launched Security+ in 2002 as a vendor neutral entry exam. Both are on the list of approved certifications for the cyber workforce of the United States Department of Defense, first under directive 8570 and now under 8140, so many employers worldwide use them as a hiring filter. A certification does not make you an expert. It proves you know a broad, agreed body of knowledge, in the words the industry uses. That is why this subject keeps using the same terms as the exam outlines. This chapter maps every chapter of the subject to the main exams, collects the facts and formulas you must recall quickly, shows how scenario questions are marked, and ends with a mock exam. One warning. Exam outlines are revised every few years. Always open the official page of your exam and check the current outline code before you book.')}
{src('CompTIA Security+ SY0-701 and CySA+ CS0-003 exam objectives (2023), ISC2 CISSP exam outline (April 2024), ISC2 Certified in Cybersecurity, EC-Council CEH exam information, US DoD Manual 8140.03.')}
{wwh('A <b>security certification</b> is an exam, run by an independent body, that checks you know an agreed outline of security knowledge, often with an experience requirement and yearly continuing education.',
     'Employers and governments use certifications as a shared measure of skill. Preparing for one also gives your study a clear outline, so you do not leave gaps.',
     'Read the official outline, map each domain to what you have learned, revise with active recall and spaced repetition, practise timed questions, then book the exam.')}
{table(['Exam', 'Level', 'Format', 'Time', 'Pass mark', 'Good for'], [
    ['ISC2 Certified in Cybersecurity (CC)', 'Entry', '100 multiple choice', '2 hours', '700 of 1000', 'A first credential with no experience'],
    ['CompTIA Security+ (SY0-701)', 'Entry to junior', 'Up to 90, multiple choice and performance based', '90 minutes', '750 on a 100 to 900 scale', 'Any first security job, DoD 8140 roles'],
    ['CompTIA CySA+ (CS0-003)', 'Analyst', 'Up to 85, multiple choice and performance based', '165 minutes', '750 on a 100 to 900 scale', 'SOC analyst, threat hunter'],
    ['EC-Council CEH', 'Junior to mid', '125 multiple choice', '4 hours', 'Set per question form', 'Attack theory for defenders and testers'],
    ['ISC2 CISSP', 'Senior, manager, architect', 'Adaptive, 100 to 150 items', '3 hours', '700 of 1000', 'Five years of paid work in two or more of the eight domains']])}
{note('The codes SY0-701 and CS0-003 are the 2023 outlines. CompTIA replaces an outline about every three years, so check whether a newer code is live before you book. CISSP adaptive testing gives harder questions as you answer correctly and stops once it is sure you have passed or failed.', 'warn')}
{steps('How to answer a certification question', [
    'Read the last sentence first. It tells you what is asked: the FIRST step, the BEST control, the MOST likely cause.',
    'Read the scenario and underline the facts that matter: the asset, the threat, what has already been done.',
    'Remove the two answers that are wrong or illegal. Two remain.',
    'Of the two, choose the one that fixes the cause, follows the process and is in your role. For CISSP think like a manager: protect people first, follow policy, reduce risk to the business.',
    'Skip performance based or long questions on the first pass and return to them, so the easy marks are not lost to the clock.'])}
''', kw=['certification', 'Security+', 'CySA+', 'CISSP', 'CEH', 'ISC2 CC', 'exam format', 'pass mark', 'exam technique', 'DoD 8140'])

K.lesson('domains', 'Exam domains mapped to this subject', f'''
{talk('Every exam outline divides its questions into domains, and each domain has a weight, the share of the questions it gets. If security operations is twenty eight percent of the exam, about one question in four is about logs, incidents, forensics and access. That tells you where to spend your time. The animation shows the domains of three exams one at a time, with the chapters of this subject that teach each one. Notice that the same chapters appear in every exam. The vocabulary is shared. Once you know risk, cryptography, networks, identity, operations and secure development, you can move between exams by learning each one’s style rather than new material.')}
{viz('cyexammap')}
{table(['Security+ domain', 'Weight', 'Chapters in this subject'], [
    ['1. General security concepts', '12%', 'What cybersecurity is, Classical ciphers to Elliptic curves, Authentication'],
    ['2. Threats, vulnerabilities and mitigations', '22%', 'Network attacks, Malware, Vulnerabilities, Injection, XSS and CSRF, Memory safety'],
    ['3. Security architecture', '18%', 'Networks, Firewalls and IDS, Wireless, PKI and TLS, Cloud security'],
    ['4. Security operations', '28%', 'Logging and SIEM, Incident response, Digital forensics, Access control, Operating systems'],
    ['5. Security program management and oversight', '20%', 'Risk in numbers, Governance and law, Threat intelligence']])}
{table(['CISSP domain', 'Weight', 'Chapters in this subject'], [
    ['1. Security and risk management', '16%', 'What cybersecurity is, Risk in numbers, Governance and law'],
    ['2. Asset security', '10%', 'Governance and law, Differential privacy, Cloud security'],
    ['3. Security architecture and engineering', '13%', 'The cryptography section, Post quantum, Memory safety'],
    ['4. Communication and network security', '13%', 'Networks, Network attacks, Firewalls and IDS, Wireless, PKI and TLS'],
    ['5. Identity and access management', '13%', 'Authentication, Access control'],
    ['6. Security assessment and testing', '12%', 'Vulnerabilities, Secure development, Logging and SIEM'],
    ['7. Security operations', '13%', 'Incident response, Digital forensics, Threat intelligence'],
    ['8. Software development security', '10%', 'Web security, Injection, XSS and CSRF, Secure development, Attacks on ML']])}
{note('The Advanced section (machine learning security, federated learning, differential privacy) goes beyond these exams. It is asked in research interviews, university exams and newer credentials on AI security, and it appears in CISSP domain 2 and Security+ domain 2 as privacy and data protection.')}
''', kw=['exam domains', 'domain weights', 'Security+ domains', 'CISSP domains', 'CySA+ domains', 'syllabus map'])

K.lesson('recall', 'Facts to recall quickly: ports, crypto and controls', f'''
{talk('Some exam questions test pure recall. Which port does Kerberos use. How long is a SHA 256 output. Which control type is a security camera. You cannot reason your way to these in the exam, so you must know them cold. The good news is that the list is short. The tables here hold the facts that appear again and again, and the program prints a port drill you can run as often as you like. Learn each table with active recall: cover the right column, say the answer, then check.')}
{run('port_drill')}
{table(['Algorithm or fact', 'Value', 'Chapter'], [
    ['AES block size and keys', '128 bit block, 128, 192 or 256 bit keys, 10, 12 or 14 rounds', 'AES and modes'],
    ['SHA-256, SHA-1, MD5 output', '256, 160 and 128 bits. SHA-1 and MD5 are broken for collisions', 'Hashes and MACs'],
    ['RSA key size', '2048 bits at least today, 3072 for about 128 bit security', 'RSA'],
    ['Elliptic curve P-256', 'About 128 bit security, same as RSA 3072, much smaller keys', 'Elliptic curves'],
    ['Quantum effect', 'Shor breaks RSA, DH and ECC. Grover halves symmetric strength, so use AES-256', 'Post quantum'],
    ['Post quantum standards (2024)', 'ML-KEM (FIPS 203) for key exchange, ML-DSA (FIPS 204) for signatures', 'Post quantum'],
    ['TLS 1.3', 'Only ephemeral (EC)DHE key exchange, so every session has forward secrecy', 'PKI and TLS'],
    ['Password storage', 'Salted slow hash: Argon2id, scrypt, bcrypt or PBKDF2', 'Hashes and MACs']])}
{table(['Control type', 'Purpose', 'Example'], [
    ['Preventive', 'Stops an incident before it happens', 'Firewall rule, MFA, door lock'],
    ['Detective', 'Notices an incident while or after it happens', 'IDS, SIEM alert, log review, camera recording'],
    ['Corrective', 'Limits damage and restores', 'Restoring a backup, patching after an attack'],
    ['Deterrent', 'Discourages an attacker', 'Warning banner, visible guard'],
    ['Compensating', 'Replaces a control that cannot be used', 'Extra monitoring on an old system that cannot be patched'],
    ['Directive', 'Tells people what to do', 'Policy, acceptable use rules']])}
{table(['Access control model', 'Who decides', 'Typical place'], [
    ['DAC (discretionary)', 'The owner of each file', 'Windows and Linux file permissions'],
    ['MAC (mandatory)', 'The system, from labels and clearances', 'Military systems, SELinux'],
    ['RBAC (role based)', 'The role a person holds', 'Most companies'],
    ['ABAC (attribute based)', 'Rules on attributes of user, resource and context', 'Cloud IAM policies, zero trust']])}
{note('Controls also have categories: technical, managerial, operational and physical. A question may ask for both, for example a camera is a physical detective control, and a security policy is a managerial directive control.')}
''', kw=['ports', 'protocols', 'port drill', 'AES', 'SHA-256', 'RSA key size', 'control types', 'preventive', 'detective', 'compensating', 'DAC', 'MAC', 'RBAC', 'ABAC'])

K.lesson('maths', 'Every formula in one place', f'''
{talk('Most security exams have a few numerical questions, and university and interview exams have many more. They nearly always come from the same small set of formulas: risk in money, password strength in bits, the birthday bound for hashes, modular arithmetic for RSA and Diffie Hellman, Bayes for alerts, availability for service levels, and the noise scale of differential privacy. This lesson puts them all on one page. The program computes every one of them on example numbers, so you can change a number and check your own answer.')}
{fxs(fx('Risk in money', 'SLE = AV &times; EF, ALE = SLE &times; ARO', 'Asset value, exposure factor, annual rate of occurrence. A control is worth buying if ALE before &minus; ALE after &minus; yearly cost &gt; 0.', key=True),
     fx('Password strength', 'H = L log<sub>2</sub> N bits, average guesses 2<sup>H</sup> / 2', 'Length L from an alphabet of N symbols, only if every character is random.', key=True),
     fx('Birthday bound', 'collision after about 2<sup>n/2</sup> tries', 'An n bit hash gives n/2 bits of collision resistance.'),
     fx('RSA', 'N = pq, &phi; = (p &minus; 1)(q &minus; 1), ed &equiv; 1 (mod &phi;), c = m<sup>e</sup> mod N, m = c<sup>d</sup> mod N', 'Security rests on factoring N.', key=True),
     fx('Diffie-Hellman', 'A = g<sup>a</sup> mod p, B = g<sup>b</sup> mod p, K = B<sup>a</sup> = A<sup>b</sup> mod p', 'Security rests on the discrete logarithm.'),
     fx('Alert precision (Bayes)', 'P(bad | alert) = TPR &middot; p / (TPR &middot; p + FPR &middot; (1 &minus; p))', 'When the base rate p is tiny, most alerts are false.', key=True),
     fx('Availability', 'A = MTBF / (MTBF + MTTR), downtime = (1 &minus; A) &times; 525600 minutes a year', '99.9% is 8.76 hours a year, 99.99% is 52.6 minutes.'),
     fx('Differential privacy', 'Laplace b = &Delta;f / &epsilon;, attack advantage &le; e<sup>&epsilon;</sup> &minus; 1', 'Smaller &epsilon; means more noise and more privacy.'))}
{run('revision_maths')}
{viz('cybaserate')}
{deep('Why these formulas keep returning', '<p>Each formula answers one of the questions a security team asks every week. Is this control worth its cost (ALE). Will this password or key survive a guessing attack (entropy and the birthday bound). Can an attacker read or forge this message (RSA and Diffie-Hellman). Should an analyst trust this alert (Bayes). Can we promise this uptime to a customer (availability). Can we publish this statistic without exposing a person (differential privacy). If you can say which question a formula answers, you will know when to use it in an exam.</p>')}
''', kw=['formulas', 'ALE', 'SLE', 'ARO', 'entropy', 'birthday bound', 'RSA maths', 'Diffie-Hellman maths', 'Bayes', 'base rate', 'availability', 'nines', 'MTBF', 'MTTR'])

K.lesson('scenarios', 'Scenario questions: what to do first', f'''
{talk('The hardest exam questions describe a situation and ask what you should do first, next or best. Several answers are good actions, but only one is right at that moment. Two orders solve most of them. The first is the incident response life cycle from NIST: preparation, detection and analysis, containment, eradication, recovery, and lessons learned. The second is the order of volatility from RFC 3227: collect the evidence that disappears fastest first. Add the rule that human safety comes before everything, and the rule that you follow the documented process and your own role, and you can answer almost any scenario.')}
{viz('cyirflow')}
{table(['Scenario', 'Best first answer', 'Why the tempting answers are wrong'], [
    ['Ransomware found on one laptop', 'Isolate it from the network', 'Wiping destroys evidence, paying is not a first step, restoring before containment lets it spread'],
    ['A user typed their password into a phishing page', 'Reset the password and end all sessions', 'Deleting the email does not stop the attacker who already has the password'],
    ['A fire alarm sounds during an incident', 'Get people out safely', 'Human safety comes before data, in every exam'],
    ['A server must be examined for an intrusion', 'Capture memory before shutting down', 'Pulling the plug loses running processes and keys in RAM'],
    ['A critical patch breaks an old system', 'Apply a compensating control and record the risk', 'Ignoring the patch or removing the system without a business decision'],
    ['Management asks you to accept a high risk', 'Document it and get a formal sign off by the risk owner', 'Accepting it yourself is outside your role']])}
{steps('Order of volatility (RFC 3227)', [
    'CPU registers and cache',
    'Routing table, ARP cache, process table, kernel statistics and memory',
    'Temporary file systems',
    'Disk',
    'Remote logging and monitoring data',
    'Physical configuration and network topology',
    'Archive media such as backup tapes'])}
{table(['Business continuity term', 'Meaning', 'Example'], [
    ['RTO (recovery time objective)', 'Longest the service may be down', 'Online shop back within 4 hours'],
    ['RPO (recovery point objective)', 'Most data, in time, you may lose', 'Backups every 15 minutes, so RPO 15 minutes'],
    ['MTD (maximum tolerable downtime)', 'Downtime after which the business is seriously harmed', 'RTO must be shorter than MTD'],
    ['Hot, warm and cold site', 'Ready in minutes, days, or weeks', 'Hot costs most, cold costs least']])}
''', kw=['scenario questions', 'first step', 'NIST incident response', 'containment', 'order of volatility', 'RFC 3227', 'RTO', 'RPO', 'MTD', 'hot site', 'human safety'])

K.lesson('traps', 'Pairs that exams love to confuse', f'''
{talk('Many wrong answers are the right answer to a slightly different question. An exam will offer encryption when the question is about integrity, an intrusion detection system when it asks for prevention, or recovery time when it asks about lost data. The fastest way to beat these traps is to learn the pairs side by side, which is what this lesson does.')}
{versus('Protecting data', ['', 'Encoding', 'Hashing', 'Encryption', 'MAC or signature'], [
    ['Goal', 'Change the format', 'Integrity check, password storage', 'Confidentiality', 'Integrity and authenticity'],
    ['Key?', 'No', 'No (a salt is not a key)', 'Yes', 'Yes'],
    ['Reversible?', 'Yes, by anyone', 'No', 'Yes, with the key', 'No, it is verified'],
    ['Example', 'Base64', 'SHA-256, Argon2id', 'AES-GCM, RSA-OAEP', 'HMAC-SHA256, Ed25519']],
    'Ask which property the question wants. Secrecy points to encryption, unchanged data to hashing or a MAC, proof of who sent it to a signature.')}
{versus('Commonly confused pairs', ['', 'First', 'Second'], [
    ['IDS or IPS', 'IDS detects and alerts, sits out of line', 'IPS sits in line and blocks'],
    ['Vulnerability scan or penetration test', 'Automated, finds known weaknesses', 'People exploit them with permission to show real impact'],
    ['Authentication or authorisation', 'Who you are', 'What you may do'],
    ['RTO or RPO', 'How long you are down', 'How much data you lose'],
    ['Risk transfer or risk avoidance', 'Insurance or a contract moves the cost', 'Stop doing the risky activity'],
    ['Bell-LaPadula or Biba', 'Confidentiality: no read up, no write down', 'Integrity: no read down, no write up'],
    ['SIEM or SOAR', 'Collects and correlates logs, raises alerts', 'Runs playbooks that respond automatically'],
    ['Symmetric or asymmetric', 'One shared key, fast (AES)', 'Key pair, slow, for key exchange and signatures (RSA, ECC)'],
    ['Anonymisation or differential privacy', 'Removes names, often reversible by linking', 'Adds noise with a mathematical guarantee'],
    ['Federated learning or plain distributed training', 'Data stays on many owners’ devices, non IID', 'One owner splits its data across servers']],
    'When two answers look right, find the word in the question that only one of them satisfies.')}
''', kw=['confused pairs', 'encoding', 'hashing', 'encryption', 'IDS vs IPS', 'scan vs pentest', 'authentication vs authorisation', 'Bell-LaPadula', 'Biba', 'SIEM vs SOAR', 'risk transfer'])

K.lesson('advanced', 'Revising the advanced section for interviews and research exams', f'''
{talk('Interviews for security research roles and exams at top universities rarely ask for a port number. They ask you to explain why something works, prove a small property, or find the flaw in a design. The advanced section of this subject, on machine learning security, federated learning and differential privacy, is where those questions come from. The table lists the results you should be able to state and derive. The questions after it are in the style of graduate courses at places such as MIT, Stanford, CMU and the IITs, with short model answers. Try each one on paper before opening the answer.')}
{table(['Result', 'Statement', 'Chapter'], [
    ['FGSM (2015)', 'x&prime; = x + &epsilon; sign(&nabla;<sub>x</sub>L), one step in the direction that raises the loss', 'Attacks on ML'],
    ['Randomised smoothing radius', 'R = &sigma; &Phi;<sup>&minus;1</sup>(p<sub>A</sub>) for the smoothed classifier', 'Attacks on ML'],
    ['FedAvg (2017)', 'w = &Sigma; (n<sub>k</sub>/n) w<sub>k</sub>, many local steps between rounds', 'Federated learning'],
    ['Secure aggregation', 'Pairwise masks cancel in the sum, the server sees only the total', 'Federated learning'],
    ['Krum (2017)', 'Choose the update with the smallest sum of distances to its n &minus; f &minus; 2 nearest neighbours', 'Attacks on FL'],
    ['DP-SGD (2016)', 'Clip each gradient to C, add N(0, &sigma;<sup>2</sup>C<sup>2</sup>), track (&epsilon;, &delta;) with an accountant', 'Differential privacy']])}
{deep('Question 1. Prove that running an &epsilon;<sub>1</sub>-DP and an &epsilon;<sub>2</sub>-DP mechanism on the same data is (&epsilon;<sub>1</sub> + &epsilon;<sub>2</sub>)-DP.',
      '<p>For independent mechanisms the output pair has probability P[M<sub>1</sub>(D) = a] P[M<sub>2</sub>(D) = b]. Each factor is at most e<sup>&epsilon;<sub>i</sub></sup> times the same factor for D&prime;. Multiply the two bounds: the product is at most e<sup>&epsilon;<sub>1</sub> + &epsilon;<sub>2</sub></sup> times the product for D&prime;. Summing over any set S of output pairs keeps the bound.</p>')}
{deep('Question 2. Why is textbook RSA (c = m<sup>e</sup> mod N with no padding) insecure even with a 4096 bit key?',
      '<p>It is deterministic, so the same message always gives the same ciphertext and an attacker can test guesses. It is malleable: c &times; 2<sup>e</sup> decrypts to 2m, so an attacker can change a message in a predictable way. Small messages with e = 3 can be recovered by an ordinary cube root. Padding such as OAEP adds randomness and structure to fix all three.</p>')}
{deep('Question 3. A detector has 99% recall and a 0.1% false positive rate. Attacks are 1 in 100000 events. What share of alerts are real, and what does this mean for design?',
      '<p>P(bad | alert) = 0.99 &times; 0.00001 / (0.99 &times; 0.00001 + 0.001 &times; 0.99999) &asymp; 0.0098, so about 1 alert in 100 is real. Design must add context to cut false positives (correlation, allow lists, a second stage model) and must measure precision, not accuracy.</p>')}
{deep('Question 4. Show that FedAvg with one local gradient step per round and equal sized clients equals ordinary gradient descent on the pooled data.',
      '<p>Each client computes w<sub>k</sub> = w &minus; &eta; &nabla;F<sub>k</sub>(w). The average is w &minus; &eta; (1/K) &Sigma; &nabla;F<sub>k</sub>(w). With equal sizes, (1/K) &Sigma; F<sub>k</sub> is the loss on the pooled data, so this is one gradient step on it. The difference appears only with several local steps, where client drift on non IID data pulls the models apart.</p>')}
{deep('Question 5. Why does reusing a nonce in AES-GCM break both confidentiality and authenticity?',
      '<p>GCM encrypts with a counter mode keystream that depends only on the key and nonce. Two messages under the same nonce share the keystream, so c<sub>1</sub> &oplus; c<sub>2</sub> = m<sub>1</sub> &oplus; m<sub>2</sub>. Their authentication tags are polynomials in the same secret H, and subtracting them gives an equation an attacker can solve for H, which then lets them forge tags for any message.</p>')}
''', kw=['interview questions', 'research questions', 'IIT', 'MIT', 'proof', 'composition proof', 'textbook RSA', 'base rate', 'FedAvg proof', 'GCM nonce reuse', 'FGSM', 'Krum', 'DP-SGD'])

K.lesson('plan', 'A study plan that works', f'''
{talk('People who pass security exams on the first attempt rarely study more hours. They study in a better way. Two methods have strong evidence from memory research. Active recall means testing yourself instead of rereading. Spaced repetition means returning to a fact just before you would forget it, with the gap growing each time you get it right. Sebastian Leitner turned this into a simple box system in 1972. The program simulates it with twelve exam facts. Cards you know move to boxes you review rarely, and cards you miss come back every day, so your time goes where it is needed.')}
{run('leitner')}
{table(['Week', 'Focus', 'Practice'], [
    ['1', 'Foundations and risk, read the exam outline', 'Write the domain list from memory'],
    ['2', 'Cryptography and PKI', 'Toy RSA and Diffie-Hellman by hand, the crypto table'],
    ['3', 'Networks, attacks, firewalls, wireless', 'Port drill daily, draw a network with its controls'],
    ['4', 'Identity, access control, malware, vulnerabilities', 'CVSS scoring, access model questions'],
    ['5', 'Application security and secure development', 'Spot the bug in short code samples'],
    ['6', 'Operations: SIEM, incident response, forensics', 'Scenario questions, order of volatility'],
    ['7', 'Governance, cloud, law and the weakest domain', 'Two timed mock exams, review every wrong answer'],
    ['8', 'Rest of the weak cards, light review', 'One last mock, then sleep well before the exam']])}
{grow('Learn the vocabulary and pass an entry exam such as ISC2 CC or Security+.',
      'Pass an analyst exam such as CySA+ and explain every answer, not only choose it.',
      'Earn the CISSP after five years of work, and answer research questions from the advanced section.')}
''', kw=['study plan', 'active recall', 'spaced repetition', 'Leitner boxes', 'mock exam', 'revision timetable'])

K.lesson('recap', 'Revision summary', f'''
{recap([
    '<b>Exams</b>: ISC2 CC and Security+ to start, CySA+ for analysts, CISSP after five years. Check the current outline code before booking.',
    '<b>Domains</b>: weight your time by domain weight. Security operations is the largest Security+ domain (28%).',
    '<b>Recall</b>: ports, crypto sizes, control types (preventive, detective, corrective, deterrent, compensating, directive) and access models.',
    '<b>Maths</b>: ALE = AV &times; EF &times; ARO, H = L log<sub>2</sub> N, birthday 2<sup>n/2</sup>, RSA and DH, Bayes for alerts, availability, Laplace b = &Delta;f/&epsilon;.',
    '<b>Scenarios</b>: safety first, then the NIST order (prepare, detect, contain, eradicate, recover, learn) and the order of volatility.',
    '<b>Method</b>: active recall, spaced repetition, timed mocks and a review of every wrong answer.'],
    'The interview questions page for the whole subject, and the full and compact cheatsheets for last day revision.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which port does Kerberos use by default?', ['22', '88', '389', '443'], 1, 'Eighty something.', 'Port 389 is LDAP, and 636 is LDAPS.')
K.quiz('e', 'A security camera that records a break in is which type of control?', ['Preventive', 'Detective', 'Corrective', 'Directive'], 1, 'It notices.', 'A visible camera can also deter, but recording is detective.')
K.quiz('e', 'Annual loss expectancy is', ['AV &times; EF', 'SLE &times; ARO', 'ARO / SLE', 'AV + EF'], 1, 'Yearly.', 'SLE = AV &times; EF is one event.')
K.quiz('e', 'Which algorithm is symmetric?', ['RSA', 'AES', 'ECDSA', 'Diffie-Hellman'], 1, 'One key.', 'The others use key pairs.')
K.quiz('e', 'Why is a salt added before hashing a password?', ['To encrypt it', 'So identical passwords get different hashes and precomputed tables fail', 'To make it shorter', 'To allow decryption'], 1, 'Rainbow tables.', 'The salt is stored in the clear next to the hash.')
K.quiz('e', 'Buying cyber insurance is which risk response?', ['Avoid', 'Transfer', 'Mitigate', 'Accept'], 1, 'Someone else pays.', 'The risk itself remains, the cost moves.')
K.quiz('e', 'The principle of giving each user only the rights they need is', ['Separation of duties', 'Least privilege', 'Defence in depth', 'Need to share'], 1, 'Least.', 'Separation of duties splits one task between people.')
K.quiz('e', 'Which replaces Telnet for secure remote login?', ['FTP', 'SSH', 'SNMP', 'RDP over HTTP'], 1, 'Port 22.', 'Telnet sends passwords in plain text.')
K.quiz('m', 'Ransomware is found on one laptop. What should be done FIRST?', ['Pay the ransom', 'Isolate the laptop from the network', 'Wipe the laptop', 'Restore from backup'], 1, 'Containment.', 'Restoring or wiping before containment risks spread and loses evidence.')
K.quiz('m', 'According to RFC 3227, which evidence should be collected first?', ['Disk image', 'Backup tapes', 'CPU registers, cache and memory', 'Network diagrams'], 2, 'Most volatile.', 'It disappears when power is lost.')
K.quiz('m', 'RPO measures', ['How long a service may be down', 'How much data, in time, may be lost', 'Mean time between failures', 'The cost of downtime'], 1, 'Point.', 'RTO is the time to recover.')
K.quiz('m', 'Bell-LaPadula protects confidentiality with which rules?', ['No read down, no write up', 'No read up, no write down', 'Read anything, write nothing', 'Owner decides'], 1, 'Secrets stay up.', 'Biba is the integrity model with the opposite rules.')
K.quiz('m', 'The best defence against SQL injection is', ['Input length limits', 'Parameterised queries', 'Hiding error messages', 'A web firewall only'], 1, 'Data stays data.', 'The others help but do not remove the cause.')
K.quiz('m', 'A user entered their password on a phishing page. Best first step?', ['Delete the email from all mailboxes', 'Reset the password and revoke active sessions', 'Send an awareness email', 'Block the sender'], 1, 'The password is out.', 'The other steps follow, but the attacker already holds the credential.')
K.quiz('m', 'In IaaS cloud, who patches the guest operating system?', ['The cloud provider', 'The customer', 'Nobody', 'The hardware vendor'], 1, 'Shared responsibility.', 'The provider patches the hypervisor and hardware.')
K.quiz('m', 'Under GDPR Article 33, a personal data breach must normally be reported to the authority within', ['24 hours', '72 hours', '7 days', '30 days'], 1, 'Three days.', 'Counted from when the controller becomes aware of it.')
K.quiz('m', 'A CVSS base score of 9.5 is rated', ['Medium', 'High', 'Critical', 'Low'], 2, '9.0 and above.', 'High is 7.0 to 8.9.')
K.quiz('m', 'Which device blocks malicious traffic in line?', ['IDS', 'IPS', 'SIEM', 'Honeypot'], 1, 'Prevention.', 'An IDS only alerts.')
K.quiz('m', 'TLS 1.3 gives forward secrecy because', ['It uses longer RSA keys', 'Key exchange is always ephemeral (EC)DHE', 'It disables certificates', 'It uses MD5'], 1, 'Fresh keys per session.', 'Static RSA key exchange was removed.')
K.quiz('h', 'A fire breaks out while you are containing an incident in the data centre. What is your first priority?', ['Finish containment', 'Save the evidence', 'Get people out safely', 'Call the CEO'], 2, 'Always first.', 'Human safety comes before data in every certification.')
K.quiz('h', 'An old system cannot be patched but must keep running. Best answer?', ['Ignore it', 'Apply a compensating control such as isolation and extra monitoring, and record the risk', 'Turn it off without asking', 'Patch it anyway'], 1, 'Replace the missing control.', 'Removing it is a business decision, not yours alone.')
K.quiz('h', 'Which pair is correct for post quantum standards from 2024?', ['ML-KEM for signatures, ML-DSA for key exchange', 'ML-KEM for key exchange, ML-DSA for signatures', 'Both for hashing', 'AES-128 and SHA-1'], 1, 'KEM means key encapsulation.', 'FIPS 203 is ML-KEM, FIPS 204 is ML-DSA.')
K.quiz('h', 'Why does Grover’s algorithm make AES-256 the safe choice?', ['It breaks AES-128 completely', 'It roughly halves the effective key length of symmetric ciphers', 'It factors keys', 'It only affects hashes'], 1, 'Square root speed up.', 'AES-256 keeps about 128 bit strength against it.')
K.quiz('h', 'A detector has a 1% false positive rate and attacks are 1 in 10000 events. Most alerts are', ['Real attacks', 'False alarms', 'Half and half', 'Impossible to say'], 1, 'Base rate.', 'False alarms outnumber real ones about 100 to 1.')
K.quiz('h', 'Zero trust architecture (NIST SP 800-207) means', ['No firewalls', 'Every request is authenticated and authorised, wherever it comes from', 'Trust inside the network', 'Users get no access'], 1, 'Never trust the location.', 'Access decisions use identity, device and context.')
K.quiz('h', 'FedAvg combines client models by', ['Taking the best client', 'A weighted average by number of local examples', 'Majority vote', 'Keeping the median only'], 1, 'n<sub>k</sub>/n.', 'The median is a robust variant used against poisoning.')
K.quiz('x', 'Krum with n clients tolerates f attackers only when', ['n &gt; f', 'n &gt; 2f + 2', 'n = f', 'f = 0'], 1, 'Neighbours.', 'Each score uses n &minus; f &minus; 2 neighbours, which must outnumber the attackers.')
K.quiz('x', 'Two mechanisms with &epsilon; = 0.3 and &epsilon; = 0.5 run on the same people. Total privacy cost?', ['0.5', '0.8', '0.15', '0.4'], 1, 'Sequential composition.', 'On disjoint groups it would be the maximum, 0.5.')
K.quiz('x', 'Why is textbook RSA malleable?', ['Because keys are short', 'Multiplying c by 2<sup>e</sup> gives a ciphertext of 2m', 'Because it uses AES', 'It is not malleable'], 1, 'Multiplicative.', 'OAEP padding prevents this.')
K.quiz('x', 'What breaks if an AES-GCM nonce is reused?', ['Only speed', 'Confidentiality and authenticity', 'Only the key length', 'Nothing'], 1, 'Same keystream, same H.', 'The XOR of plaintexts leaks and tags can be forged.')

K.calc('e', 'An asset worth 80000 has exposure factor 0.5 and an annual rate of occurrence of 0.25. ALE?', '10000', 'SLE first.',
       ['SLE = 80000 &times; 0.5 = 40000.', 'ALE = SLE &times; ARO.', eq('40000 &times; 0.25 = 10000')], check=80000 * 0.5 * 0.25)
K.calc('e', 'Laplace noise for a count (sensitivity 1) at &epsilon; = 0.25. Scale b?', '4', 'b = &Delta;f / &epsilon;.',
       ['&Delta;f = 1 for a count.', '&epsilon; = 0.25.', eq('b = 1 / 0.25 = 4')], check=1 / 0.25)
K.calc('e', 'How many usable host addresses in a /26 IPv4 subnet?', '62', '32 minus 26 host bits.',
       ['Host bits = 32 &minus; 26 = 6.', '2<sup>6</sup> = 64 addresses.', eq('64 &minus; 2 (network and broadcast) = 62')], check=2 ** 6 - 2)
K.calc('m', 'Password of 10 random lowercase letters. Entropy in bits? Round to 1 decimal.', '47.0', 'L log<sub>2</sub> N.',
       ['N = 26, L = 10.', 'log<sub>2</sub> 26 &asymp; 4.7004.', eq('10 &times; 4.7004 &asymp; 47.0 bits')], check=round(10 * math.log2(26), 1))
K.calc('m', 'Birthday bound for a 64 bit hash. About how many tries for a likely collision?', '4294967296', '2<sup>n/2</sup>.',
       ['n = 64.', 'n / 2 = 32.', eq('2<sup>32</sup> = 4294967296')], check=2 ** 32)
K.calc('m', 'Toy RSA with p = 5, q = 11, e = 3. Private exponent d?', '27', 'Inverse of e mod &phi;.',
       ['N = 55, &phi; = 4 &times; 10 = 40.', 'Find d with 3d &equiv; 1 (mod 40).', eq('3 &times; 27 = 81 = 2 &times; 40 + 1, so d = 27')], check=pow(3, -1, 40))
K.calc('m', 'Diffie-Hellman with p = 23, g = 5 and secret a = 6. Public value A?', '8', 'g<sup>a</sup> mod p.',
       ['5<sup>2</sup> = 25 &equiv; 2 (mod 23).', '5<sup>6</sup> = (5<sup>2</sup>)<sup>3</sup> &equiv; 2<sup>3</sup> = 8.', eq('A = 8')], check=pow(5, 6, 23))
K.calc('m', 'Service with 99.95% availability. Downtime in minutes a year? Round to 1 decimal.', '262.8', '(1 &minus; A) &times; 525600.',
       ['1 &minus; 0.9995 = 0.0005.', 'A year has 525600 minutes.', eq('0.0005 &times; 525600 = 262.8')], check=round((1 - 0.9995) * 525600, 1))
K.calc('h', 'Base rate 1%, TPR 0.9, FPR 0.05. P(bad | alert)? Round to 3 decimals.', '0.154', 'Bayes.',
       ['True alerts: 0.9 &times; 0.01 = 0.009.', 'False alerts: 0.05 &times; 0.99 = 0.0495.', eq('0.009 / (0.009 + 0.0495) &asymp; 0.154')], check=round(0.9 * 0.01 / (0.9 * 0.01 + 0.05 * 0.99), 3))
K.calc('h', 'ALE before a control 50000, after 10000, control costs 15000 a year. Yearly value of the control?', '25000', 'Saving minus cost.',
       ['Saving = 50000 &minus; 10000 = 40000.', 'Subtract the yearly cost 15000.', eq('40000 &minus; 15000 = 25000')], check=50000 - 10000 - 15000)
K.calc('h', 'FedAvg: client A has 100 examples and parameter 2.0, client B has 300 examples and parameter 4.0. New global parameter?', '3.5', 'Weight by examples.',
       ['Total n = 400.', 'Weights 0.25 and 0.75.', eq('0.25 &times; 2.0 + 0.75 &times; 4.0 = 3.5')], check=(100 * 2.0 + 300 * 4.0) / 400)
K.calc('h', '8 characters from 95 printable symbols at 10<sup>9</sup> guesses a second. Average days to crack? Round to 1 decimal.', '38.4', 'Half the space.',
       ['95<sup>8</sup> &asymp; 6.634 &times; 10<sup>15</sup>.', 'Half of that at 10<sup>9</sup> a second is about 3.317 &times; 10<sup>6</sup> seconds.', eq('3.317 &times; 10<sup>6</sup> / 86400 &asymp; 38.4 days')], check=round(95 ** 8 / 2 / 1e9 / 86400, 1))
K.calc('x', 'CISSP adaptive exam: 180 minutes for at most 150 items. Average minutes per item if all 150 appear?', '1.2', 'Time over items.',
       ['Time = 180 minutes.', 'Items = 150.', eq('180 / 150 = 1.2 minutes')], check=180 / 150)

T = K.topic(
    slug='cy-certprep', topic='cy-certprep', kind='revision',
    step=(5, 'Certification revision', 'cy-a5', 'Revising the whole subject for security certifications, interviews and university exams.', 'All levels'),
    title='Certification revision: exams, recall, formulas and scenarios', short='Certification revision', badge='5.1', minutes=70,
    lead='Bring the whole subject together for exams: how Security+, CySA+, CISSP, ISC2 CC and CEH work, which chapters cover each domain, the facts and formulas to recall, how to answer first and best scenario questions, research style questions on the advanced section, a study plan and a mock exam.',
    desc='certification, exam revision, Security+, SY0-701, CySA+, CS0-003, CISSP, ISC2 CC, CEH, exam domains, domain weights, ports, control types, access control models, formulas, ALE, entropy, birthday bound, RSA, Diffie-Hellman, Bayes, availability, Laplace, scenario questions, NIST incident response, order of volatility, RTO, RPO, Bell-LaPadula, Biba, interview questions, spaced repetition, Leitner, mock exam',
    summary='Exam formats and domains mapped to the chapters, recall tables, every formula, scenario answering, research style questions and a mock exam.',
    keywords=['certification', 'exam revision', 'Security+', 'CISSP', 'CySA+', 'mock exam', 'formulas', 'scenarios', 'study plan'],
    recap='', added='2026-11-15')
