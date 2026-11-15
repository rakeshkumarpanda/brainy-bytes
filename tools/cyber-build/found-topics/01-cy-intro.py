# Foundations 1.1: what cybersecurity is. Checked against NIST SP 800-12 Rev. 1 (An Introduction to Information
# Security) for the CIA definitions, NIST SP 800-207 (Zero Trust Architecture), the NIST glossary (threat,
# vulnerability, risk), the UK National Audit Office report on WannaCry and the NHS (2017), the US House report on
# Equifax (2018), IBM Cost of a Data Breach 2025 (global average USD 4.44 million), Saltzer and Schroeder, "The
# Protection of Information in Computer Systems" (1975), and Gordon and Loeb, ACM TISSEC 5(4) 2002.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from mlkit import link
from cykit import talk, safe, attack

chapter('cy-intro')
K = Kit()

K.code('cia_check', r'''
# Sort some incidents by the security goal they break.
# C = confidentiality (secret seen), I = integrity (data changed), A = availability (service down)
incidents = [
    ("Customer list copied and sold online", True, False, False),
    ("Student raises own marks in the school system", False, True, False),
    ("Ransomware locks and steals hospital files", True, True, True),
    ("Fake traffic takes a ticket site down", False, False, True),
    ("Account number changed on an emailed bill", False, True, False),
]

for name, conf, integ, avail in incidents:
    broken = []
    if conf:
        broken.append("confidentiality")
    if integ:
        broken.append("integrity")
    if avail:
        broken.append("availability")
    print(name)
    print("   breaks:", ", ".join(broken))
''')

K.code('integrity_hash', r'''
import hashlib

# A hash is a short fingerprint of data. Change one letter and the fingerprint changes completely.
bill = "Pay 5000 rupees to account 1234 5678"
changed = "Pay 5000 rupees to account 1234 5679"

fingerprint_1 = hashlib.sha256(bill.encode()).hexdigest()
fingerprint_2 = hashlib.sha256(changed.encode()).hexdigest()

print("original:", fingerprint_1)
print("changed: ", fingerprint_2)

same = 0
for a, b in zip(fingerprint_1, fingerprint_2):
    if a == b:
        same = same + 1
print("matching characters:", same, "of", len(fingerprint_1))
print("is the bill unchanged?", fingerprint_1 == fingerprint_2)
''')

K.code('layered_defence', r'''
import random

# Each layer has a chance to MISS an attack. An attack gets in only if every layer misses it.
layers = [("email filter", 0.3), ("user training", 0.5), ("antivirus", 0.4), ("MFA login", 0.1)]

chance = 1.0
for name, miss in layers:
    chance = chance * miss
print("chance one attack gets through:", round(chance, 4))
print("expected breaches out of 1000:", round(1000 * chance, 1))

# Check it by simulation: send 1000 pretend attacks through the layers
random.seed(7)
got_in = 0
for attack in range(1000):
    passed = True
    for name, miss in layers:
        if random.random() > miss:     # this layer caught it
            passed = False
            break
    if passed:
        got_in = got_in + 1
print("simulated breaches out of 1000:", got_in)
''', long=True)

K.code('at_least_one', r'''
# If each person clicks a phishing link with chance p, what is the chance that AT LEAST ONE of n people clicks?
# P(nobody clicks) = (1 - p) ** n, so P(at least one) = 1 - (1 - p) ** n

p = 0.03     # 3 people in 100 click

for n in [1, 10, 50, 100, 200]:
    nobody = (1 - p) ** n
    print(n, "people -> chance at least one clicks:", round(1 - nobody, 3))
''')

K.code('expected_loss', r'''
# Expected loss of a risk = chance it happens in a year x what it costs when it happens
risks = [
    ("laptop stolen", 0.20, 80000),
    ("ransomware", 0.05, 2500000),
    ("website down for a day", 0.30, 150000),
]

total = 0
for name, chance, cost in risks:
    loss = chance * cost
    total = total + loss
    print(name, "-> expected loss per year:", round(loss))
print("total expected loss per year:", round(total))

# Gordon and Loeb: it is rarely worth spending more than about 37% (1 / e) of the expected loss on protection
import math
print("rough upper limit for the security budget:", round(total / math.e))
''')

K.lesson('idea', 'What cybersecurity is', f'''
{talk('Welcome to cybersecurity. Before we read the page, here is the story behind it. In the early days, computers sat in locked rooms and only a few trusted people could touch them. Security meant a good door lock. Then computers were joined together into networks, and later into the internet. Suddenly a person on the other side of the world could reach your computer without ever touching it. In 1988 a student named Robert Morris released a small program to measure the size of the internet. A bug made it copy itself again and again, and it slowed down thousands of computers in one day. People realised that a computer can be harmed from far away, by code alone. Today almost everything runs on computers: your bank, your hospital, the power in your home and the trains you ride. So cybersecurity is no longer a topic only for experts. It is about keeping daily life working. In this lesson we will see what cybersecurity protects, who it protects it from, and the simple words every security person uses.')}
{src('NIST SP 800-12 Rev. 1, the NIST glossary, Saltzer and Schroeder (1975) and the UK National Audit Office report on WannaCry (2017).')}
{wwh('<b>Cybersecurity</b> is the work of protecting computers, networks, programs and data from people who want to steal them, change them or stop them working. It includes tools (like passwords and firewalls), habits (like not clicking strange links) and plans (like backups and what to do after an attack).',
     'Our money, health records, photos, messages, jobs and even electricity and water now depend on computers. If an attacker steals or breaks them, real people get hurt: hospitals cancel operations, shops close, and families lose savings. Cybersecurity keeps these systems trustworthy.',
     'We first ask what we are protecting (the <b>assets</b>), from whom (the <b>threats</b>) and where we are weak (the <b>vulnerabilities</b>). Then we add <b>controls</b>, which are the things that block, spot or recover from an attack. We keep checking, because attackers keep changing.')}
{scene('the WannaCry attack on hospitals, May 2017', '<p>On 12 May 2017 a program called WannaCry spread across the world and locked the files on more than 200,000 computers in about 150 countries. It demanded payment in Bitcoin to unlock them. In England many hospitals and doctors had to cancel appointments and send ambulances to other hospitals. The program used a weakness in old Windows file sharing. Microsoft had released a fix two months before, in March 2017. The computers that were hit had simply not been updated. One missed update turned into a crisis for patients.</p>')}
<p>Cybersecurity is a mix of three things, and you need all three. <b>People</b> must know how to spot tricks. <b>Process</b> means clear rules, such as who can approve a payment and how often backups are tested. <b>Technology</b> means the tools, such as encryption, firewalls and updates. A great tool fails if people switch it off, and good people fail if the process lets one person do everything alone.</p>
{note('Cybersecurity is not only about hackers in hoodies. Most damage comes from ordinary gaps: a missed update, a reused password, a public storage folder, or a person tricked by a fake email.', 'tip')}
''', kw=['cybersecurity', 'definition', 'assets', 'threats', 'vulnerabilities', 'controls', 'people process technology', 'WannaCry'])

K.lesson('cia', 'The three goals: confidentiality, integrity and availability', f'''
{talk('Security people love short names, and the most famous one is the CIA triad. It has nothing to do with the spy agency. C stands for confidentiality, I for integrity and A for availability. These three ideas were written down in the 1970s and 1980s by people building military and banking computers, and they are still the first thing every security exam asks. Here is an easy way to remember them. Think of your diary. Confidentiality means nobody else reads it. Integrity means nobody secretly tears out a page or adds a fake line. Availability means you can open it whenever you want. If any one of these breaks, the diary is no longer safe. Every attack you will ever study breaks at least one of these three goals. So when you hear about a new attack in the news, ask yourself: which letter did it break?')}
{wwh('The <b>CIA triad</b> is the three goals of security. <b>Confidentiality</b>: only the right people can see the data. <b>Integrity</b>: the data is correct and nobody changed it without permission. <b>Availability</b>: the system and data work when the right people need them.',
     'A clear goal tells you what "safe" means. Without it, people argue about tools. With it, you can look at any system and ask three simple questions, and you can measure if a control really helps.',
     'For each asset we decide how much each goal matters. Medical records need high confidentiality and integrity. A news website needs high availability and integrity, but its articles are public. Then we pick controls: encryption for confidentiality, hashes and signatures for integrity, backups and spare servers for availability.')}
<p>Press <b>Step</b> to test an incident against the three goals. Change the incident and play it again.</p>
{viz('cycia')}
{run('cia_check')}
{table(['Goal', 'Plain question', 'Attacks that break it', 'Controls that protect it'], [
    ['Confidentiality', 'Can the wrong person read it?', 'Data leaks, sniffing traffic, stolen passwords, shoulder surfing', 'Encryption, access control, MFA, need to know'],
    ['Integrity', 'Can someone change it without being caught?', 'Tampering, fake transactions, malware editing files, man in the middle', 'Hashes, digital signatures, change logs, input checks'],
    ['Availability', 'Does it work when needed?', 'DDoS floods, ransomware, deleted data, power or hardware failure', 'Backups, spare systems, DDoS filtering, patching, capacity planning']])}
<p>A hash is like a fingerprint for data, and it is the simplest integrity tool. The program below shows that changing one digit of a bill changes the whole fingerprint, so the change is easy to catch. You will build hashes properly in the Cryptography section.</p>
{run('integrity_hash')}
{fxs(fx('Three more words that go with CIA', '<b>Authenticity</b>: it really comes from who it says. <b>Non repudiation</b>: the sender cannot later deny sending it. <b>Accountability</b>: every action can be traced to a person.', 'Some books add these to make five goals. The Parkerian hexad (Donn Parker, 1998) uses six: confidentiality, possession, integrity, authenticity, availability and utility.'),
     fx('AAA', '<b>Authentication</b> (who are you), <b>Authorisation</b> (what may you do), <b>Accounting</b> (what did you do)', 'The three steps every login system follows. Exam questions often mix them up.', key=True))}
{note('Goals can pull against each other. Locking a file with a strong password raises confidentiality but can hurt availability if the password is lost. Good security balances all three for each asset.', 'exam')}
''', kw=['CIA triad', 'confidentiality', 'integrity', 'availability', 'AAA', 'authentication', 'authorisation', 'accounting', 'non repudiation', 'Parkerian hexad'])

K.lesson('words', 'The words every security person uses', f'''
{talk('Security has its own language, and the words can feel heavy at first. The good news is that they map to things you already know from daily life. Think of your house. The things inside, like your phone and jewellery, are assets. A burglar is a threat. A window that does not lock is a vulnerability. The burglar climbing through that window is an exploit. The chance that you get robbed, and how much it would cost, is the risk. The locks, the dog and the alarm are controls. Once you see the house picture, every security report becomes easier to read. These words are also defined officially by NIST, the American standards body, and those definitions are used all over the world in exams and in contracts.')}
{table(['Word', 'Plain meaning', 'House example', 'Computer example'], [
    ['Asset', 'Something valuable we protect', 'Jewellery, your phone', 'Customer database, the website'],
    ['Threat', 'Anyone or anything that could cause harm', 'A burglar, a flood', 'A criminal gang, a careless insider'],
    ['Vulnerability', 'A weakness that a threat could use', 'A window that does not lock', 'Old software with a known bug'],
    ['Exploit', 'A way or a piece of code that uses a vulnerability', 'Climbing through the open window', 'A program that takes over the old software'],
    ['Risk', 'How likely harm is and how bad it would be', 'Chance of a break in and its cost', 'Chance of a data leak and the fine plus losses'],
    ['Control (safeguard)', 'Anything that lowers risk', 'Locks, alarm, a dog', 'Patches, firewall, MFA, backups'],
    ['Attack surface', 'All the places an attacker could try', 'Every door and window', 'Every open port, login page and API'],
    ['Zero day', 'A vulnerability the maker does not know about yet, so no fix exists', 'A secret way in that the builder forgot', 'A new bug sold on the black market'],
    ['CVE', 'A public ID number for a known vulnerability', '', 'CVE-2017-0144, the flaw WannaCry used'],
    ['Incident', 'An event that actually harms or threatens CIA', 'A real break in', 'Ransomware found on a server']])}
{fxs(fx('Risk in one line', 'risk = likelihood &times; impact', 'Likelihood is how often it is expected to happen. Impact is how much damage one event does. Chapter 1.2 turns this into money with SLE, ARO and ALE.', key=True),
     fx('No threat or no weakness, no risk', 'risk exists only when a threat can use a vulnerability against an asset', 'A locked window with no burglars around, or burglars with no way in, gives little risk.'))}
{note('A vulnerability is the weakness, an exploit is the method that uses it, and a threat is who might use it. Students often swap these three in exams.', 'warn')}
''', kw=['asset', 'threat', 'vulnerability', 'exploit', 'risk', 'control', 'safeguard', 'attack surface', 'zero day', 'CVE', 'incident'])

K.lesson('who', 'Who attacks and why: real incidents', f'''
{talk('Why would anyone attack a computer? Mostly for the same reasons people commit any crime: money, anger, beliefs, or power. In the 1980s and 1990s many attacks were done by curious teenagers who wanted to show off. Today the biggest share is organised crime, run like a business, with customer support for victims who want to pay a ransom. Governments also attack each other quietly, to spy or to prepare for conflict. And some of the most damaging attacks come from inside: an angry employee, or simply a tired one who makes a mistake. In this lesson we meet these groups and look at real incidents. Each one teaches a lesson that is still true today, so pay attention to the last column of the table, the lesson learned.')}
{table(['Who', 'What they want', 'Skill and money', 'Example'], [
    ['Script kiddies', 'Fun, fame, curiosity', 'Low. They run tools made by others', 'Defacing a school website'],
    ['Cyber criminals', 'Money', 'Medium to high. Run like a company', 'Ransomware gangs, card fraud, scam call centres'],
    ['Hacktivists', 'A political or social message', 'Low to medium', 'Floods of traffic against a government site'],
    ['Nation states (APTs)', 'Spying, sabotage, power', 'Very high, long term, well funded', 'Stuxnet damaging uranium centrifuges (found in 2010)'],
    ['Insiders', 'Revenge, money, or an honest mistake', 'They already have access', 'An employee copying files before leaving'],
    ['Competitors', 'Secrets and an edge in business', 'Medium', 'Stealing designs or price lists']])}
{table(['Year', 'Incident', 'What happened', 'Lesson learned'], [
    ['1988', 'Morris worm', 'A self copying program slowed about 6,000 computers, around one in ten on the internet then', 'One bug can spread to everything that is connected'],
    ['2013', 'Target', 'Attackers entered through a heating and cooling supplier’s login and stole about 40 million card numbers', 'Your suppliers are part of your attack surface'],
    ['2017', 'WannaCry', 'Ransomware hit more than 200,000 computers in about 150 countries, including UK hospitals', 'Install updates quickly. The fix existed two months earlier'],
    ['2017', 'Equifax', 'An unpatched web framework (Apache Struts) let attackers take data on about 147 million people', 'Know every system you run and patch it'],
    ['2020', 'SolarWinds', 'Attackers hid a back door inside a real software update used by about 18,000 customers', 'Even trusted updates can be poisoned (supply chain attack)'],
    ['2021', 'Colonial Pipeline', 'Ransomware entered through an old VPN account with no second factor. Fuel supply on the US east coast stopped for days', 'Use MFA everywhere and remove unused accounts'],
    ['2022', 'AIIMS Delhi', 'Ransomware took down the servers of India’s top public hospital for about two weeks', 'Hospitals need tested offline backups and network separation'],
    ['2024', 'CrowdStrike outage', 'A faulty security software update crashed about 8.5 million Windows computers. It was not an attack', 'Availability can fail without any attacker. Test updates in stages']])}
{scene('a fake call from the bank', '<p>Riya gets a call: "Madam, this is your bank. Your card is blocked. Please tell me the OTP we just sent so we can unblock it." The caller knows her name and the last four digits of her card, so it feels real. The OTP was really for a payment the caller started. Nothing was hacked in the computer sense. The attacker hacked a person. This is <b>social engineering</b>, and it is behind a huge share of real fraud. Banks never ask for your OTP, PIN or password on a call.</p>')}
{note('Attackers usually pick the easiest way in, not the cleverest. That is why boring basics (updates, MFA, backups, training) stop most real attacks.', 'tip')}
''', kw=['attackers', 'threat actors', 'script kiddies', 'cyber criminals', 'hacktivists', 'nation state', 'APT', 'insider threat', 'Morris worm', 'Equifax', 'SolarWinds', 'Colonial Pipeline', 'social engineering'])

K.lesson('layers', 'Defence in depth: many layers, not one wall', f'''
{talk('Old castles were not protected by one wall. They had a moat, then an outer wall, then an inner wall, then guards at the keep. An enemy had to beat every layer. Security people borrowed this idea and called it defence in depth. The reason is simple. Every single control fails sometimes. A spam filter misses some emails. A person clicks a link on a busy day. An antivirus does not know a brand new virus. But if several different layers stand in the way, an attack must slip past all of them, and that is much less likely. The maths behind this is just multiplication of chances, and the animation will show you how quickly the numbers drop. Keep one warning in mind. The maths assumes the layers fail for different reasons. If two layers share the same weakness, they can fall together.')}
{wwh('<b>Defence in depth</b> means putting several different controls one behind another, so that an attacker must beat all of them.',
     'No control is perfect. If you rely on one, its single failure is a full breach. Layers turn one big failure into several small chances that must all go wrong together.',
     'An attack gets through only if every layer misses it. If layer i misses with chance m<sub>i</sub>, and the layers fail independently, the chance of a breach is m<sub>1</sub> &times; m<sub>2</sub> &times; ... &times; m<sub>k</sub>.')}
{viz('cylayers')}
{run('layered_defence')}
{fxs(fx('Chance that an attack passes every layer', 'P(breach) = m<sub>1</sub> &times; m<sub>2</sub> &times; ... &times; m<sub>k</sub>', 'm<sub>i</sub> is the chance that layer i misses. Only true when the layers fail independently.', key=True),
     fx('Chance that at least one of many attempts succeeds', 'P(at least one) = 1 &minus; (1 &minus; p)<sup>n</sup>', 'p is the chance one attempt works, n is the number of attempts. Attackers only need to win once.', key=True))}
{run('at_least_one')}
{steps('Worked example: why one click in a big company is almost certain', [
    'A company has 100 staff. A phishing email fools each person with chance p = 0.03.',
    'Chance one person does not click: 1 &minus; 0.03 = 0.97.',
    'Chance nobody clicks, if people act independently: 0.97<sup>100</sup> &asymp; 0.048.',
    eq('P(at least one click) = 1 &minus; 0.048 &asymp; 0.952'),
    'So there is about a 95% chance someone clicks. The defender cannot rely on "nobody will click". There must be layers after the click: MFA, antivirus, network limits and monitoring.'])}
{attack([
    ['Sends a phishing email', 'Email filter blocks known bad links and attachments'],
    ['The email gets through and someone clicks', 'Training helps people report it, the browser warns about fake sites'],
    ['The person types their password into a fake page', 'MFA means the stolen password alone does not log in'],
    ['Malware runs on the laptop', 'Antivirus and EDR stop or flag it, the user has no admin rights'],
    ['Malware tries to spread', 'The network is split into zones, so it cannot reach the servers'],
    ['Data is copied out', 'Monitoring spots the large upload, and the data is encrypted at rest']])}
{note('The attacker needs to win once. The defender needs to win every time. Layers change this: now the attacker must win at every layer, every time.', 'exam')}
''', kw=['defence in depth', 'layered security', 'layers', 'probability of breach', 'at least one', 'phishing', 'castle'])

K.lesson('principles', 'Design principles that last', f'''
{talk('In 1975, two researchers at MIT, Jerome Saltzer and Michael Schroeder, wrote a paper about protecting information in computers. Computers then were huge machines shared by many users. Yet the eight design principles in their paper are still taught in every university today, because they describe how to build systems that fail safely. Think of them as habits of a careful builder. Give each person only the keys they need. Make the safe choice the default. Check every request, not just the first one. Keep things simple, because simple things are easier to check. Later, around 2010, the idea of zero trust was added: never assume someone is friendly just because they are inside your network. We will look at each idea with an everyday picture.')}
{table(['Principle', 'Plain meaning', 'Everyday picture'], [
    ['Least privilege', 'Give each user and program only the access it needs, and only for as long as needed', 'A hotel key card opens only your room, and only until you check out'],
    ['Fail safe defaults', 'If unsure, say no. Access is denied unless it is allowed', 'A new employee gets no access until a manager approves it'],
    ['Complete mediation', 'Check permission on every request, not only the first', 'A cinema checks your ticket at the door of each screen'],
    ['Economy of mechanism', 'Keep the design small and simple so it can be checked', 'A simple lock has fewer ways to break'],
    ['Open design', 'Security must not depend on hiding how it works. Only the key is secret', 'Everyone knows how a padlock works, yet it is safe without the key'],
    ['Separation of privilege', 'Need two conditions or two people for important actions', 'A bank locker needs both your key and the bank’s key'],
    ['Least common mechanism', 'Do not share the same thing between users unless needed', 'Separate towels for each guest'],
    ['Psychological acceptability', 'Security must be easy enough that people really use it', 'If the door is too hard to lock, people prop it open'],
    ['Zero trust', 'Never trust because of location. Always verify the user, the device and the request', 'Office staff still show ID at every floor, not only at the front gate']])}
{deep('Zero trust in NIST SP 800-207', '<p>NIST SP 800-207 (2020) describes zero trust as moving defences from a fixed network edge to users, devices and resources. Every request is checked by a <b>policy decision point</b> using who the user is, how healthy the device is and how sensitive the resource is, and it is enforced by a <b>policy enforcement point</b> in front of the resource. Being on the office network gives no extra trust. The old model is often called the castle and moat model: hard outside, soft inside. Zero trust exists because attackers who get inside the moat (through phishing or a stolen VPN password) used to move freely.</p>')}
{note('Open design is also called Kerckhoffs’s principle (1883): a cipher should stay safe even if the enemy knows everything about it except the key. Hiding the method is called security through obscurity, and it is not enough on its own.', 'exam')}
''', kw=['least privilege', 'fail safe defaults', 'complete mediation', 'economy of mechanism', 'open design', 'separation of privilege', 'Saltzer Schroeder', 'zero trust', 'Kerckhoffs', 'security through obscurity'])

K.lesson('versus', 'Cybersecurity compared with similar ideas', f'''
{talk('People often use words like cybersecurity, information security, privacy and safety as if they mean the same thing. They overlap, but each one has its own focus, and knowing the difference helps you read job ads, laws and exam questions. Information security is the oldest and widest. It protects information in any form, even paper in a filing cabinet. Cybersecurity focuses on information and systems that are connected, such as the internet, phones and industrial machines. Privacy is about people: what is collected about you and how it is used, even when nothing is stolen. Safety is about protecting people from accidents, while security is about protecting against someone who means harm. Let us put them side by side.')}
{versus('Security and its neighbours', ['', 'Information security', 'Cybersecurity', 'Privacy', 'Safety and reliability'], [
    ['Protects', 'Information in any form, paper or digital', 'Connected systems, networks, devices and their data', 'People’s personal data and their choices about it', 'People and machines from accidents and faults'],
    ['Main enemy', 'Anyone who misuses information', 'Attackers who come through networks and code', 'Over collection and misuse, even by the company itself', 'Chance failures, wear, human error'],
    ['Typical tools', 'Policies, locked cabinets, encryption, access control', 'Firewalls, patching, MFA, monitoring, incident response', 'Consent, data minimisation, anonymisation, laws such as GDPR', 'Redundancy, testing, safety checks'],
    ['Question it asks', 'Is the information protected?', 'Can an attacker get in through the network?', 'Should we collect and use this data at all?', 'What if this part fails by itself?']],
    'Information security is the widest circle. Cybersecurity is the part about connected systems. Privacy asks whether data should be used at all, so a perfectly secure system can still break privacy. Safety plans for accidents, security plans for enemies, and modern systems such as cars and power grids need both.')}
{table(['Approach', 'How it works', 'Strength', 'Weakness'], [
    ['One strong wall (perimeter only)', 'Protect the network edge and trust everything inside', 'Simple and cheap', 'One stolen password or bad laptop exposes everything'],
    ['Defence in depth', 'Several different layers', 'One failure is not a breach', 'More to manage, layers can share a weakness'],
    ['Zero trust', 'Verify every request, everywhere', 'Stops attackers moving around inside', 'Needs good identity data and takes time to roll out'],
    ['Security through obscurity alone', 'Hide how it works', 'Slows a casual attacker', 'Breaks completely once the secret leaks']])}
''', kw=['information security', 'cybersecurity', 'privacy', 'safety', 'perimeter security', 'comparison', 'zero trust vs perimeter'])

K.lesson('maths', 'The maths of security decisions', f'''
{talk('You might think security is all about clever tricks, but behind every good security decision there is some simple maths. Banks, insurance companies and governments decide how much to spend on security by estimating chances and costs. In 2002 two economists, Lawrence Gordon and Martin Loeb, asked a famous question: how much should a company spend to protect a piece of information? Their surprising answer was that, under fairly general conditions, it is never worth spending more than about 37 percent of the expected loss. The number 37 percent comes from one divided by e, the special number from maths that is about 2.718. In this lesson you will use three tools: multiplying chances, the chance of at least one success, and expected loss. With these you can already reason like a risk analyst.')}
<p>These four formulas come back in every section of this subject. Read them slowly and try the worked problems tab after this lesson.</p>
{fxs(fx('Expected loss', 'expected loss = probability &times; cost', 'The average loss per year if the same risk is faced many years. Used to compare risks of very different kinds.', key=True),
     fx('Independent events, all happen', 'P(A and B) = P(A) &times; P(B)', 'Used for layers that must all fail.'),
     fx('Complement', 'P(not A) = 1 &minus; P(A)', 'Often it is easier to work out the chance that nothing goes wrong, then subtract from 1.'),
     fx('Gordon and Loeb bound', 'best spend &le; (1 / e) &times; expected loss &asymp; 0.368 &times; expected loss', 'For the classes of breach probability functions studied by Gordon and Loeb (2002). A rule of thumb, not a law.', key=True))}
{run('expected_loss')}
{steps('Worked example: is this security tool worth buying?', [
    'Ransomware has a 5% chance per year of hitting a school. One attack would cost 20 lakh rupees (lost days, recovery, new machines).',
    eq('expected loss = 0.05 &times; 20,00,000 = 1,00,000 rupees per year'),
    'A backup system costs 30,000 rupees a year and would cut the cost of an attack to 2 lakh rupees.',
    eq('new expected loss = 0.05 &times; 2,00,000 = 10,000 rupees per year'),
    'Saving per year = 1,00,000 &minus; 10,000 = 90,000 rupees, for a cost of 30,000. The tool is worth it. Its cost is also well below the Gordon and Loeb limit of about 36,800 rupees.'])}
{deep('Where the 1 / e comes from', '<p>Gordon and Loeb model a firm with a potential loss L, a vulnerability v (the chance of a breach with no spending) and a breach probability S(z, v) after spending z. For the two families of S they studied, with S falling smoothly and with diminishing returns as z grows, they proved that the best spend z* satisfies z* &lt; (1/e) v L. In words: spend less than about 37% of the expected loss v L. They also showed that the best spend does not always rise with v. For very vulnerable assets it can be better to spend less and accept the loss, because each rupee buys too little protection.</p>')}
''', kw=['expected loss', 'probability', 'complement rule', 'independent events', 'Gordon Loeb', 'security investment', 'one over e'])

K.lesson('careers', 'Roles and the certification path', f'''
{talk('Cybersecurity is a big field with many kinds of jobs, and you do not need to be a genius programmer to join it. Some people defend networks in a security operations centre, watching alerts like air traffic controllers. Some test systems by attacking them with permission, which is called ethical hacking or penetration testing. Some investigate crimes after they happen, which is digital forensics. Some write policies and check that companies follow the law. Some design secure systems, and some do research on new cryptography. Certifications help employers trust that you know the basics. They usually start broad, like CompTIA Security Plus, and then become specialised, like the hands on OSCP exam for penetration testers, or CISSP for experienced managers. This subject is built to walk you along that whole path.')}
{table(['Role', 'What they do every day', 'Good first certification', 'Advanced certification'], [
    ['SOC analyst (blue team)', 'Watch alerts, check if they are real, start the response', 'CompTIA Security+', 'CompTIA CySA+, GIAC GCIH'],
    ['Penetration tester (red team)', 'Attack systems with written permission and report the gaps', 'CompTIA PenTest+, EC-Council CEH', 'OffSec OSCP'],
    ['Incident responder and forensics', 'Contain attacks, collect evidence, find the cause', 'CompTIA Security+', 'GIAC GCFA, GCIH'],
    ['Security engineer and architect', 'Design and build secure networks, clouds and apps', 'CompTIA Security+', 'ISC2 CISSP, cloud provider security certifications'],
    ['Governance, risk and compliance', 'Write policies, assess risk, prepare for audits and laws', 'ISC2 CC (Certified in Cybersecurity)', 'ISACA CISM, CISA, ISC2 CISSP'],
    ['Cryptographer and researcher', 'Design and break ciphers and protocols, publish research', 'A strong maths and computer science degree', 'A masters or PhD']])}
{table(['Section of this subject', 'Matches these exam areas'], [
    ['Foundations', 'Security+ general security concepts, CISSP security and risk management'],
    ['Cryptography', 'Security+ cryptography objectives, CISSP security architecture and engineering'],
    ['Network and Systems', 'Security+ threats and architecture, CISSP communication and network security, identity and access management'],
    ['Application Security', 'CEH and OSCP web attacks, CISSP software development security'],
    ['Security Operations', 'Security+ security operations, CySA+, CISSP security operations, governance and law'],
    ['Advanced', 'Research level topics: attacks on machine learning, federated learning, differential privacy, post quantum crypto']])}
{safe('Every attack in this subject runs on made up data inside this page or on your own computer. Testing a system you do not own without written permission is a crime in most countries, including under the Information Technology Act 2000 in India and the Computer Misuse Act 1990 in the UK. Practise on your own machines and on legal training sites built for it.')}
{note('Exam details (number of questions, time, passing score, price) change every few years. Always check the official page of CompTIA, EC-Council, ISC2 or OffSec before you book. The revision chapter at the end of this subject lists them as checked when it was written.', 'warn')}
''', kw=['careers', 'SOC analyst', 'penetration tester', 'red team', 'blue team', 'forensics', 'GRC', 'certifications', 'Security+', 'CEH', 'CISSP', 'OSCP', 'legal'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('The same idea can be explained at many depths. A school student, a college student, a masters student and a researcher can all talk about security, but they ask different questions. At school level, security is about keeping your secrets safe and your devices working. At college level, you name the goals, the threats and the controls, and you start to measure risk. At masters level, you build a threat model: you write down exactly what the attacker can and cannot do, and you check every part of a system against it. At research level, people prove that a system is secure under a precise mathematical model, or they find a new kind of attack that breaks those models. Pick the tab that matches you, then try the next one when you feel ready.')}
{ladder(
    '<p>Cybersecurity keeps your computer, phone and accounts safe. It keeps secrets secret, stops people changing your data, and keeps things working. Use strong passwords, turn on updates and never share an OTP.</p>',
    '<p>Security protects confidentiality, integrity and availability of assets against threats that use vulnerabilities. Risk is likelihood times impact. Controls are preventive, detective or corrective, and defence in depth stacks them so one failure is not a breach.</p>',
    '<p>Security engineering starts with a <b>threat model</b>: the assets, the attacker’s goals, what the attacker can do (read the network, run code, bribe an insider) and the trust boundaries. Tools such as STRIDE (spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege) and attack trees check each part of a design against that model. Risk is managed with expected loss and the economics of controls.</p>',
    '<p>Research formalises security as a game between a challenger and an adversary with bounded resources. A scheme is secure if every efficient adversary wins with only negligible advantage, proved by reduction to a hard problem (factoring, discrete log, lattice problems). The Dolev and Yao model (1983) lets the attacker control the whole network but not break cryptography. Security economics (Anderson, 2001) explains why systems stay insecure: those who could fix a problem often are not the ones who suffer from it.</p>')}
{grow('Name the CIA goals, spot threat, vulnerability and risk in a story, and list daily habits that keep you safe.',
      'Use risk = likelihood &times; impact, compute layered breach chances and at least one probabilities, and explain the Saltzer and Schroeder principles.',
      'Write a threat model with STRIDE, reason about security investment with Gordon and Loeb, and explain the Dolev and Yao attacker and reduction proofs.')}
''', kw=['beginner', 'expert', 'threat model', 'STRIDE', 'attack tree', 'Dolev Yao', 'security economics', 'reduction proof'])

K.lesson('pylink', 'Python for this subject', f'''
<p>Most chapters have small Python programs you can run in the page, step through line by line, change and download. You only need the basics: variables, loops, lists, dictionaries and functions. If Python is new to you, learn it first in the Complete Python subject, then come back. Chapter 2.3 of Foundations teaches the extra Python that security work needs: bytes, encodings, hashing, reading logs and parsing network data.</p>
{link('python', 'Complete Python', 'All of Python from print() to classes, files, regular expressions, sockets, Flask, Django and APIs, with runnable code and downloads.')}
''', kw=['Python', 'Complete Python subject', 'prerequisites'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Cybersecurity</b> protects computers, networks, programs and data from people who want to steal, change or stop them. It needs people, process and technology together.',
    'The <b>CIA triad</b>: confidentiality (only the right people read it), integrity (nobody changes it unnoticed), availability (it works when needed). Every attack breaks at least one.',
    '<b>AAA</b>: authentication (who you are), authorisation (what you may do), accounting (what you did).',
    'An asset is what we protect, a threat is who may harm it, a vulnerability is the weakness, an exploit uses the weakness, and <b>risk = likelihood &times; impact</b>.',
    'Attackers range from script kiddies to criminal gangs, hacktivists, nation states and insiders. Most real breaches use easy gaps: missed patches, no MFA, phishing.',
    '<b>Defence in depth</b>: with independent layers, P(breach) is the product of the miss chances. With many attempts, P(at least one success) = 1 &minus; (1 &minus; p)<sup>n</sup>.',
    'Saltzer and Schroeder principles (least privilege, fail safe defaults, complete mediation, open design and others) and <b>zero trust</b> guide good design.',
    'Expected loss = probability &times; cost. Gordon and Loeb: spend less than about 37% (1/e) of the expected loss.'],
    'Foundations 1.2 turns risk into numbers with SLE, ARO and ALE, sorts controls by type, and builds a full risk register.')}
{files('Three tasks: the chance an attack passes every layer, the chance at least one of many attempts succeeds, and naming which CIA goals an incident breaks.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which goal is broken when a stranger reads your private messages?', ['Integrity', 'Confidentiality', 'Availability', 'Accounting'], 1, 'Secret seen by the wrong person.', 'Reading secrets breaks confidentiality.')
K.quiz('e', 'A website is flooded with fake traffic and real users cannot open it. Which goal is broken?', ['Confidentiality', 'Integrity', 'Availability', 'Non repudiation'], 2, 'Does it work when needed?', 'A service that cannot be reached has lost availability.')
K.quiz('e', 'A window in your house that does not lock is best called', ['A threat', 'A vulnerability', 'An exploit', 'A control'], 1, 'It is the weakness.', 'A weakness that a threat could use is a vulnerability.')
K.quiz('e', 'What should you do if a caller says they are from your bank and asks for your OTP?', ['Tell them quickly', 'Refuse and call the bank on the number on your card', 'Share only half of it', 'Send it by SMS instead'], 1, 'Banks never ask for it.', 'This is social engineering. Hang up and call a number you already trust.')
K.quiz('m', 'Which of these is an integrity control?', ['A backup copy', 'A hash or digital signature', 'A DDoS filter', 'A screen privacy filter'], 1, 'It detects changes.', 'Hashes and signatures show if data was changed.')
K.quiz('m', 'In AAA, checking that you are allowed to open the payroll folder is', ['Authentication', 'Authorisation', 'Accounting', 'Availability'], 1, 'What may you do?', 'Authorisation decides what an identified user may do.')
K.quiz('m', 'Ransomware that copies files before locking them breaks', ['Only availability', 'Confidentiality, integrity and availability', 'Only integrity', 'None, if you pay'], 1, 'Copied, changed and locked.', 'Copying breaks confidentiality, encrypting changes the files and locking stops use.')
K.quiz('m', 'A hotel key card that opens only your own room is an example of', ['Open design', 'Least privilege', 'Security through obscurity', 'Complete mediation'], 1, 'Only what you need.', 'Each guest gets only the access they need.')
K.quiz('m', 'Kerckhoffs’s principle says a cipher should be safe even if the attacker knows', ['The key', 'Everything except the key', 'Nothing at all', 'Only the plaintext'], 1, 'What must stay secret?', 'Only the key should need to be secret. The method can be public.')
K.quiz('h', 'Three independent layers miss an attack with chances 0.5, 0.2 and 0.1. What is the chance an attack passes all three?', ['0.8', '0.01', '0.1', '0.5'], 1, 'Multiply.', '0.5 &times; 0.2 &times; 0.1 = 0.01.')
K.quiz('h', 'Why is the layered breach formula a best case in real life?', ['Layers are always perfect', 'Layers may fail together for the same reason, so they are not independent', 'Attackers never try twice', 'Multiplication is not allowed for chances'], 1, 'Independence.', 'A clever attacker can beat two layers at once, so real chances are higher than the product.')
K.quiz('h', 'Which STRIDE threat matches a user denying they sent a payment order?', ['Spoofing', 'Tampering', 'Repudiation', 'Elevation of privilege'], 2, 'Denying an action.', 'Repudiation is denying an action. Signatures and logs give non repudiation.')
K.quiz('x', 'In the style of an MIT 6.858 exam: zero trust mainly removes which assumption of the castle and moat model?', ['That encryption is needed', 'That a request is trustworthy because it comes from inside the network', 'That users need passwords', 'That servers need updates'], 1, 'Location based trust.', 'Zero trust verifies every request by identity, device and policy, never by network location.')
K.quiz('x', 'In the style of a Cambridge security economics question: with expected loss v L = 10 lakh, what is the Gordon and Loeb upper limit on the best spend?', ['10 lakh', 'About 3.68 lakh', 'About 1 lakh', 'There is no limit'], 1, 'Multiply by 1/e.', '10 / e &asymp; 3.68 lakh.')

K.calc('e', 'A layer misses 30% of attacks. Out of 200 attacks, how many get past it?', '60', 'Attacks &times; miss chance.', ['Miss chance 0.3.', '200 attacks.', eq('200 &times; 0.3 = 60')], check=200 * 0.3)
K.calc('e', 'Two independent layers miss with chances 0.4 and 0.5. What is the chance an attack passes both?', '0.2', 'Multiply.', ['First layer 0.4.', 'Second layer 0.5.', eq('0.4 &times; 0.5 = 0.2')], check=0.4 * 0.5)
K.calc('e', 'A risk happens with chance 0.1 per year and costs 50,000 rupees. What is the expected loss per year in rupees?', '5000', 'Probability &times; cost.', ['Chance 0.1.', 'Cost 50,000.', eq('0.1 &times; 50,000 = 5,000')], check=0.1 * 50000)
K.calc('m', 'Four layers miss with 0.3, 0.5, 0.4 and 0.1. What is P(breach)?', '0.006', 'Multiply all four.', ['0.3 &times; 0.5 = 0.15.', '0.15 &times; 0.4 = 0.06.', eq('0.06 &times; 0.1 = 0.006')], check=0.3 * 0.5 * 0.4 * 0.1, tol=1e-9)
K.calc('m', 'With the four layers above, how many of 10,000 attacks are expected to get through?', '60', 'Attacks &times; P(breach).', ['P(breach) = 0.006.', 'Attacks = 10,000.', eq('10,000 &times; 0.006 = 60')], check=10000 * 0.006)
K.calc('m', 'Each of 2 people clicks a phishing link with chance 0.1, independently. What is the chance at least one clicks?', '0.19', '1 &minus; (1 &minus; p)<sup>n</sup>.', ['Nobody clicks: 0.9 &times; 0.9 = 0.81.', 'Complement.', eq('1 &minus; 0.81 = 0.19')], check=1 - 0.9 ** 2, tol=1e-9)
K.calc('m', 'A password guess works with chance 0.001. What is the chance that at least one of 10 guesses works? Round to 4 decimal places.', '0.01', '1 &minus; 0.999<sup>10</sup>.', ['0.999<sup>10</sup> &asymp; 0.99004.', '1 &minus; 0.99004 = 0.00996.', eq('&asymp; 0.0100')], check=round(1 - 0.999 ** 10, 4))
K.calc('h', 'An MFA layer misses with chance 0.1. Adding it to a system with P(breach) = 0.05 gives what new P(breach)?', '0.005', 'Multiply by the new miss chance.', ['Old chance 0.05.', 'MFA miss 0.1.', eq('0.05 &times; 0.1 = 0.005')], check=0.05 * 0.1, tol=1e-12)
K.calc('h', 'Each of n staff clicks with chance 0.03. What is the smallest n for which P(at least one click) is above 0.5?', '23', 'Solve 0.97<sup>n</sup> &lt; 0.5.', ['n &gt; ln 0.5 / ln 0.97 = 0.6931 / 0.03046 &asymp; 22.76.', 'n must be a whole number.', eq('n = 23')], check=next(n for n in range(1, 100) if 1 - 0.97 ** n > 0.5))
K.calc('h', 'Expected loss is 2,71,828 rupees. What is the Gordon and Loeb limit 1/e &times; loss, rounded to the nearest rupee?', '100000', 'e &asymp; 2.71828.', ['Limit = loss / e.', '2,71,828 / 2.718281828.', eq('&asymp; 1,00,000')], check=round(271828 / 2.718281828459045))
K.calc('x', 'In the style of a CMU 18-730 question: a defender can either raise one layer from miss 0.2 to 0.1, or add a new independent layer with miss 0.6. The other layers give P = 0.2 &times; 0.5 = 0.1 now. Which choice gives the smaller P(breach)? Answer with the new P(breach) of the better choice.', '0.05', 'Work out both.', ['Option 1: 0.1 &times; 0.5 = 0.05.', 'Option 2: 0.2 &times; 0.5 &times; 0.6 = 0.06.', eq('better: option 1 with 0.05')], check=min(0.1 * 0.5, 0.2 * 0.5 * 0.6))

K.assign('layers', 'e', 'Chance an attack passes every layer',
         '<p>Write <code>breach_chance(miss)</code>. It gets a list of miss chances, one per layer, and returns the chance an attack passes all of them (their product). An empty list means there is no defence, so return 1.</p>',
         '''
def breach_chance(miss):
    # your code here
    pass
''', [('breach_chance([0.5, 0.2])', 0.1), ('breach_chance([])', 1), ('round(breach_chance([0.3, 0.5, 0.4, 0.1]), 6)', 0.006)],
         '''
def breach_chance(miss):
    chance = 1
    for m in miss:
        chance = chance * m
    return chance
''', 'Start with 1 and multiply by each miss chance in a loop.', '<p>This is the defence in depth formula. It assumes the layers fail independently, so in real life it is the best case.</p>')
K.assign('atleast', 'e', 'At least one success in many tries',
         '<p>Write <code>at_least_one(p, n)</code> that returns the chance that at least one of n independent tries succeeds, when each succeeds with chance p. Round the answer to 4 decimal places.</p>',
         '''
def at_least_one(p, n):
    # your code here
    pass
''', [('at_least_one(0.1, 2)', 0.19), ('at_least_one(0.03, 100)', 0.9524), ('at_least_one(0.5, 0)', 0.0)],
         '''
def at_least_one(p, n):
    nobody = (1 - p) ** n
    return round(1 - nobody, 4)
''', 'Work out the chance that every try fails, (1 &minus; p) to the power n, then take it away from 1.', '<p>Attackers only need one success. This formula shows why a big company almost always has someone who clicks a phishing link.</p>')
K.assign('cia', 'm', 'Which goals does an incident break?',
         '<p>Write <code>goals_broken(read, changed, down)</code>. The three inputs are True or False: was secret data read, was data changed, was the service down. Return a list of the broken goals in the order "C", "I", "A". For example, data read and service down gives ["C", "A"].</p>',
         '''
def goals_broken(read, changed, down):
    # your code here
    pass
''', [('goals_broken(True, False, True)', ['C', 'A']), ('goals_broken(False, False, False)', []), ('goals_broken(True, True, True)', ['C', 'I', 'A'])],
         '''
def goals_broken(read, changed, down):
    broken = []
    if read:
        broken.append("C")
    if changed:
        broken.append("I")
    if down:
        broken.append("A")
    return broken
''', 'Start with an empty list and add a letter for each True input, in the order C, I, A.', '<p>Analysts tag every incident with the goals it broke. This decides who must be told (a confidentiality breach of personal data often must be reported by law) and which controls to improve.</p>')

K.must('Cybersecurity', 'Protects systems and data from people who want to steal, change or stop them. People, process and technology together.')
K.must('CIA triad', 'Confidentiality (right people read), integrity (no unnoticed change), availability (works when needed). AAA: authentication, authorisation, accounting.')
K.must('Words', 'Asset, threat, vulnerability (weakness), exploit (method), risk = likelihood &times; impact, control, attack surface, zero day, CVE.')
K.must('Defence in depth', 'Independent layers: P(breach) = product of miss chances. Many tries: P(at least one) = 1 &minus; (1 &minus; p)<sup>n</sup>.')
K.must('Principles', 'Least privilege, fail safe defaults, complete mediation, economy of mechanism, open design (Kerckhoffs), separation of privilege, zero trust.')
K.must('Money', 'Expected loss = probability &times; cost. Gordon and Loeb: best spend under about 37% (1/e) of expected loss.')

T = K.topic(
    slug='cy-intro', topic='cy-intro', step=(1, 'Start here', 'cy-f1', 'What security protects and from whom, how risk is measured, and the maths every security decision uses.', 'Beginner'),
    title='What cybersecurity is: goals, threats and layers', short='What cybersecurity is', badge='1.1', minutes=60,
    lead='Learn what cybersecurity protects, the CIA triad and AAA, the words every security person uses, who attacks and why with real incidents, defence in depth with the maths of layers, the design principles that last, and the career and certification path.',
    desc='definition of cybersecurity, people process technology, CIA triad, confidentiality, integrity, availability, AAA, non repudiation, Parkerian hexad, asset, threat, vulnerability, exploit, risk, attack surface, zero day, CVE, threat actors, real incidents WannaCry Equifax SolarWinds Colonial Pipeline AIIMS, social engineering, defence in depth, probability of breach, at least one success, Saltzer and Schroeder principles, zero trust, Kerckhoffs, information security vs cybersecurity vs privacy vs safety, expected loss, Gordon Loeb, STRIDE, Dolev Yao, careers and certifications.',
    summary='the CIA triad, the words of security, attackers and real incidents, defence in depth with its maths, design principles, zero trust and careers.',
    keywords=['cybersecurity', 'CIA triad', 'confidentiality', 'integrity', 'availability', 'threat', 'vulnerability', 'risk', 'defence in depth', 'zero trust'],
    recap='<p>Security protects confidentiality, integrity and availability. Layers multiply the attacker’s chance of failure, and simple maths guides how much to spend.</p>',
    added='2026-11-14')
