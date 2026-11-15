# Security Operations 2.1: threat intelligence. Checked against the MITRE ATT&CK Enterprise matrix (14 tactics) and its
# history, Hutchins, Cloppert and Amin, Intelligence-Driven Computer Network Defense Informed by Analysis of Adversary
# Campaigns and Intrusion Kill Chains (Lockheed Martin, 2011), Caltagirone, Pendergast and Betz, The Diamond Model of
# Intrusion Analysis (2013), David Bianco, The Pyramid of Pain (2013), OASIS STIX 2.1 and TAXII 2.1, FIRST Traffic Light
# Protocol 2.0 (2022), the NATO Admiralty code (source reliability and information credibility), US ICD 203 analytic
# standards, MISP project documentation, the Conficker Working Group lessons learned report (2010), and public reports on
# the SolarWinds discovery by FireEye (December 2020).
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, safe

chapter('cy-threatintel')
K = Kit()

K.code('ioc_match', r'''
# Match our own logs against a feed of indicators of compromise (IOCs), and ignore indicators that have expired
from datetime import date

today = date(2026, 11, 15)
feed = [
    # value, type, date added, days it stays useful
    ("203.0.113.80", "ip", date(2026, 11, 10), 14),
    ("update-checker.example", "domain", date(2026, 10, 1), 90),
    ("198.51.100.66", "ip", date(2026, 9, 1), 14),          # old: probably reused by someone else now
    ("e3b0c44298fc1c149afbf4c8996fb924", "md5", date(2026, 11, 1), 365),
]
logs = [
    "10:01 fw ALLOW 10.0.0.22 -> 203.0.113.80:443",
    "10:02 dns QUERY update-checker.example from 10.0.0.31",
    "10:05 fw ALLOW 10.0.0.40 -> 198.51.100.66:80",
    "10:09 edr FILE written md5=e3b0c44298fc1c149afbf4c8996fb924 host PC-9",
    "10:12 dns QUERY flipkart.com from 10.0.0.22",
]

active = []
for value, kind, added, life in feed:
    age = (today - added).days
    if age <= life:
        active.append(value)
    else:
        print(f"expired, skipped: {value} ({kind}, {age} days old, useful for {life})")

print()
for line in logs:
    hits = [v for v in active if v in line]
    if hits:
        print("MATCH", hits[0], "|", line)
print("\nOld IP indicators cause false alarms, because cloud addresses are reused by new, innocent owners.")
''')

K.code('attack_coverage', r'''
# Map detection rules to MITRE ATT&CK tactics and find the gaps
TACTICS = ["Reconnaissance", "Resource Development", "Initial Access", "Execution", "Persistence",
           "Privilege Escalation", "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
           "Collection", "Command and Control", "Exfiltration", "Impact"]

rules = {
    "Phishing attachment opened": ("T1566", "Initial Access"),
    "PowerShell encoded command": ("T1059.001", "Execution"),
    "New Run key": ("T1547.001", "Persistence"),
    "Event log cleared": ("T1070.001", "Defense Evasion"),
    "Brute force": ("T1110", "Credential Access"),
    "LSASS memory read": ("T1003.001", "Credential Access"),
    "Admin share login": ("T1021.002", "Lateral Movement"),
    "Beaconing to rare domain": ("T1071", "Command and Control"),
    "Mass file rename": ("T1486", "Impact"),
}

count = {t: 0 for t in TACTICS}
for name, (technique, tactic) in rules.items():
    count[tactic] += 1

for tactic in TACTICS:
    bar = "#" * count[tactic]
    print(f"{tactic:21} {count[tactic]}  {bar}")
covered = sum(1 for t in TACTICS if count[t] > 0)
print(f"\ncovered {covered} of {len(TACTICS)} tactics = {covered / len(TACTICS) * 100:.1f}%")
print("gaps:", ", ".join(t for t in TACTICS if count[t] == 0))
''')

K.code('stix_share', r'''
# Sharing an indicator in a STIX 2.1 style object, marked with a Traffic Light Protocol level
import json

TLP = {
    "TLP:RED": "only the people in the meeting or the named recipients",
    "TLP:AMBER+STRICT": "only inside the recipient's own organisation",
    "TLP:AMBER": "the recipient's organisation and its clients who need it",
    "TLP:GREEN": "the wider community, but not public websites",
    "TLP:CLEAR": "anyone, it can be published",
}

indicator = {
    "type": "indicator",
    "spec_version": "2.1",
    "id": "indicator--6d3f6a6c-0e3c-4d3b-9f1e-7a2b5c9d1e01",
    "name": "Payroll themed phishing C2 domain",
    "pattern": "[domain-name:value = 'update-checker.example']",
    "pattern_type": "stix",
    "valid_from": "2026-11-15T00:00:00Z",
    "valid_until": "2027-02-13T00:00:00Z",
    "labels": ["malicious-activity"],
    "kill_chain_phases": [{"kill_chain_name": "mitre-attack", "phase_name": "command-and-control"}],
    "x_tlp": "TLP:AMBER",
}

text = json.dumps(indicator, indent=2)
print("\n".join(text.splitlines()[:9]) + "\n  ...")
received = json.loads(text)
print(f"\nreceived: {received['name']}")
print(f"look for: {received['pattern']}")
print(f"share with: {TLP[received['x_tlp']]}")
''')

K.code('dga_detect', r'''
# Spot domains made up by malware (domain generation algorithms) from how random their letters look
import math
from collections import Counter

def entropy(s):
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in Counter(s).values())

def vowel_share(s):
    return sum(1 for ch in s if ch in "aeiou") / len(s)

def score(name):
    total = entropy(name)
    if vowel_share(name) < 0.2:
        total += 1          # real words need vowels
    if any(ch.isdigit() for ch in name):
        total += 1          # digits inside a word are unusual
    return total

THRESHOLD = 3.5
domains = ["google", "wikipedia", "xkqzvbtrwplm", "flipkart", "q7j2nd9vx0ra",
           "icicibank", "bwuzhfaiyeqo", "irctc", "zzqjxkwv", "timesofindia"]
for d in domains:
    s = score(d)
    print(f"{d + '.com':18} entropy {entropy(d):4.2f}  vowels {vowel_share(d):4.2f}  score {s:4.2f}  {'FLAG' if s > THRESHOLD else ''}")
''', long=True)

K.code('confidence', r'''
# How sure are we? Update the chance that an IP is malicious as independent sources report it (Bayes with odds).
def to_odds(p):
    return p / (1 - p)

def to_prob(odds):
    return odds / (1 + odds)

prior = 0.20                   # before any report: 1 in 5 IPs on this list turn out to be bad
reports = [
    ("Feed A (reliable, B2 on the Admiralty scale)", 4.0),   # likelihood ratio: how much more likely if really bad
    ("Our own sandbox saw it as C2", 9.0),
    ("Feed C (unknown source, F6)", 1.0),                    # no information: ratio 1 changes nothing
]

odds = to_odds(prior)
print(f"start: P = {prior:.2f}, odds = {odds:.2f}")
for source, ratio in reports:
    odds = odds * ratio
    print(f"after {source}: odds x {ratio} = {odds:.2f}, P = {to_prob(odds):.3f}")
print("\nIndependent sources multiply. Two feeds that copy each other are really one source, so do not count them twice.")
''')

K.code('ioc_decay', r'''
# Indicators go stale. Model usefulness as halving every h days, and retire an indicator below 10%.
import math

HALF_LIFE = {"file hash": 180, "domain": 30, "ip": 7}     # rough values, tune them on your own data
RETIRE_BELOW = 0.10

for kind, h in HALF_LIFE.items():
    retire_day = h * math.log2(1 / RETIRE_BELOW)
    values = [2 ** (-t / h) for t in (0, 7, 30, 90)]
    print(f"{kind:9} half life {h:3} days | day 0, 7, 30, 90: " + ", ".join(f"{v:.2f}" for v in values) + f" | retire after {retire_day:.1f} days")
print("\nIP addresses change hands fastest, so their indicators age fastest. Behaviour (TTPs) ages slowest of all.")
''')

K.lesson('idea', 'What threat intelligence is, and the intelligence cycle', f'''
{talk('Threat intelligence means knowledge about attackers that helps you defend. Raw data, such as a list of a million IP addresses, is not intelligence. It becomes intelligence when someone checks it, adds context, and makes it useful for a decision: block this domain today, patch this product first, or train staff on this new kind of scam. The idea comes from military and government intelligence, which works in a loop called the intelligence cycle. First, direction: decide what questions matter, such as which groups target banks in India. Second, collection: gather data from sources such as your own logs, vendor reports, government advisories from CERT-In, sharing groups and the open internet. Third, processing: clean it, remove duplicates and put it in a standard format. Fourth, analysis: connect the pieces and judge what they mean, with a level of confidence. Fifth, dissemination: give the right answer to the right people in the right form. Sixth, feedback: ask whether it helped and adjust the questions. A good example of intelligence in action is the SolarWinds case. In December 2020 the security company FireEye found that its own tools had been stolen, traced the intrusion to a poisoned SolarWinds software update, and published detailed indicators and detection rules within days. Thousands of other defenders used that intelligence to check their own networks.')}
{src('Hutchins, Cloppert and Amin, Lockheed Martin (2011), Caltagirone, Pendergast and Betz, The Diamond Model of Intrusion Analysis (2013), David Bianco, The Pyramid of Pain (2013), MITRE ATT&amp;CK Enterprise matrix, OASIS STIX 2.1 and TAXII 2.1 standards, FIRST Traffic Light Protocol 2.0 (2022), US ICD 203, MISP project, Conficker Working Group Lessons Learned (2010), FireEye and Mandiant SolarWinds disclosures (December 2020).')}
{safe('The programs use made up indicators from documentation address ranges such as 203.0.113.0/24 and example domains. Use real indicator feeds only on networks you are responsible for.')}
{wwh('<b>Threat intelligence</b> is checked, explained knowledge about attackers, their tools and their methods, given to the people who need it to make a defence decision.',
     'Defenders cannot watch everything. Intelligence tells them which threats are likely, which clues to look for, and which weaknesses to fix first.',
     'Run the intelligence cycle: set questions, collect, process, analyse with confidence levels, share in standard formats, and get feedback.')}
{table(['Level', 'Audience', 'Question it answers', 'Example'], [
    ['Strategic', 'Board and leaders', 'Who might attack us and why, what is the business risk?', 'Ransomware groups are targeting hospitals this year'],
    ['Operational', 'Security managers', 'What campaign is coming and how does it work?', 'A phishing wave with fake tax refund emails starts next week'],
    ['Tactical', 'SOC and hunters', 'Which techniques do they use?', 'They use PowerShell and scheduled tasks to persist'],
    ['Technical', 'Tools and SIEM', 'Which exact clues can we block?', 'Domain update-checker.example, file hash e3b0...']])}
''', kw=['threat intelligence', 'intelligence cycle', 'direction', 'collection', 'processing', 'analysis', 'dissemination', 'feedback', 'strategic', 'operational', 'tactical', 'technical', 'SolarWinds', 'FireEye'])

K.lesson('pyramid', 'Indicators and the Pyramid of Pain', f'''
{talk('An indicator of compromise, IOC for short, is a clue that an attack happened or is happening: a file hash, an IP address, a domain name, a strange file path or registry key. Indicator feeds share these clues, and the program below matches a feed against logs. But not all clues are equal. In 2013 David Bianco drew the Pyramid of Pain. At the bottom are file hashes. They are exact and easy to block, but an attacker can change one byte of the malware and get a new hash in seconds, so blocking a hash causes almost no pain. Above that are IP addresses, which cost a few minutes to change, and domain names, which cost a little money. Higher up are artefacts the attack leaves on the network and on machines, then the attacker’s tools, and at the top their tactics, techniques and procedures, TTPs, which means the way they work. Changing how they work is slow and expensive for an attacker. So the higher up the pyramid a defender can detect, the more pain they cause. Indicators also go stale. Cloud IP addresses are handed to new, innocent owners within days, so an old IP indicator causes false alarms. Good teams give each indicator an expiry date, as the program below does.')}
{viz('cypyramid')}
{run('ioc_match')}
{run('ioc_decay')}
{fxs(fx('Indicator usefulness', 'U(t) = 2<sup>&minus;t / h</sup>', 'With a half life of h = 7 days, an IP indicator is worth 0.25 after 14 days.', key=True),
     fx('When to retire', 't = h &middot; log<sub>2</sub>(1 / U<sub>min</sub>)', 'For h = 7 and U<sub>min</sub> = 0.1: t &asymp; 23.3 days.', key=True))}
''', kw=['IOC', 'indicator of compromise', 'Pyramid of Pain', 'David Bianco', 'hash', 'IP address', 'domain', 'artefacts', 'tools', 'TTPs', 'indicator expiry', 'half life'])

K.lesson('models', 'Models of an attack: Kill Chain, Diamond and ATT&amp;CK', f'''
{talk('To describe attacks in the same words, defenders use models. In 2011 three Lockheed Martin analysts, Eric Hutchins, Michael Cloppert and Rohan Amin, described the Cyber Kill Chain, borrowing a military term. An intrusion has seven links: reconnaissance, weaponisation, delivery, exploitation, installation, command and control, and actions on objectives. The attacker needs every link, but the defender only needs to break one, and breaking an early link causes less harm, as the animation shows. In 2013 Sergio Caltagirone, Andrew Pendergast and Christopher Betz published the Diamond Model, which says every intrusion event has four corners: an adversary, a capability such as malware, infrastructure such as servers, and a victim. Knowing one corner helps find the others. For example, a server used against one victim may reveal other victims. The most used model today is MITRE ATT&amp;CK, started inside MITRE in 2013 and made public in 2015. It is a large, free knowledge base built from real incidents. Its Enterprise matrix has 14 tactics, which are the attacker’s goals, from reconnaissance to impact, and hundreds of techniques and sub techniques under them, each with an ID such as T1110 for brute force. Teams tag every detection rule with its technique, which shows coverage and gaps, as in the second animation and program.')}
{viz('cykillchain')}
{viz('cyattackmap')}
{run('attack_coverage')}
{fxs(fx('Breaking several links', 'P(attack succeeds) = &Pi; (1 &minus; b<sub>i</sub>)', 'Three independent controls that each stop 70%: 0.3<sup>3</sup> = 0.027. Layers multiply.', key=True),
     fx('Coverage', 'coverage = tactics with at least one rule / 14', '9 of 14 tactics &asymp; 64.3%. Count techniques too, not only tactics.'))}
{table(['Model', 'Year', 'Main idea', 'Good for'], [
    ['Cyber Kill Chain', '2011', 'Seven links, break any one', 'Explaining layered defence, planning controls'],
    ['Diamond Model', '2013', 'Adversary, capability, infrastructure, victim', 'Linking events, finding more of a campaign'],
    ['MITRE ATT&amp;CK', '2013 internal, 2015 public', '14 tactics, hundreds of techniques from real cases', 'Detection coverage, hunting, red and blue teams sharing words']])}
''', kw=['Cyber Kill Chain', 'Lockheed Martin', 'Diamond Model', 'adversary', 'capability', 'infrastructure', 'victim', 'MITRE ATT&CK', 'tactics', 'techniques', 'T1110', 'coverage'])

K.lesson('share', 'Sharing intelligence: STIX, TAXII, TLP and MISP', f'''
{talk('Intelligence is worth more when it is shared, because an attack seen at one bank today may reach another bank tomorrow. Sharing needs a common language and clear rules. STIX, Structured Threat Information Expression, now at version 2.1 and run by the standards body OASIS, is a JSON format for objects such as indicators, malware, threat actors, attack patterns and the relationships between them. TAXII is the matching protocol for sending STIX over the internet. The open source platform MISP, widely used by CERTs and companies, stores and shares intelligence and speaks STIX. Rules about who may see what come from the Traffic Light Protocol. Its version 2.0, published by FIRST in August 2022, has five labels. TLP:RED means only the named people. TLP:AMBER+STRICT means only inside your own organisation. TLP:AMBER means your organisation and clients who need it. TLP:GREEN means your community, but not public. TLP:CLEAR means anyone. Sharing groups exist for many sectors, called ISACs, Information Sharing and Analysis Centres, such as the financial sector FS-ISAC. In India, CERT-In publishes advisories and vulnerability notes, and sector CSIRTs cover areas such as finance and power. A last word on quality: a feed with many false indicators can do harm, for example by blocking a popular content delivery network, so test feeds before you let them block anything automatically.')}
{run('stix_share')}
{table(['TLP 2.0 label', 'Who may receive it'], [
    ['TLP:RED', 'Only the people present or named, no further sharing'],
    ['TLP:AMBER+STRICT', 'Only the recipient’s own organisation'],
    ['TLP:AMBER', 'The recipient’s organisation and its clients, on a need to know basis'],
    ['TLP:GREEN', 'The wider community, but not public channels'],
    ['TLP:CLEAR', 'Anyone, it may be published']])}
''', kw=['STIX 2.1', 'TAXII', 'OASIS', 'MISP', 'Traffic Light Protocol', 'TLP 2.0', 'TLP:RED', 'TLP:AMBER+STRICT', 'TLP:CLEAR', 'ISAC', 'FS-ISAC', 'CERT-In advisories', 'feed quality'])

K.lesson('analysis', 'Analysis with confidence: sources, Bayes and hunting', f'''
{talk('An intelligence report must say how sure it is. Two simple tools help. The NATO Admiralty code rates the source from A, completely reliable, to F, reliability cannot be judged, and the information itself from 1, confirmed by other sources, to 6, truth cannot be judged. So B2 means a usually reliable source with probably true information. Analysts also use careful words for likelihood, such as likely or almost certain, following standards such as the US ICD 203. Under the words sits Bayes’ rule. Start with a prior chance that an IP is malicious. Each independent report multiplies the odds by a likelihood ratio, which says how much more likely that report is if the IP is really bad. A strong source might have a ratio of 4, your own sandbox seeing it call home a ratio of 9, and a source you know nothing about a ratio of 1, which changes nothing. The program below shows the chance climbing from 20 percent to over 90 percent. One trap is counting the same evidence twice: two feeds that copy each other are one source. Intelligence also drives threat hunting. A hunter starts with a hypothesis from intelligence, such as this group uses scheduled tasks for persistence, searches the logs for it, and either finds an intruder or writes a new rule so the SIEM watches for it from now on. Some clues can be found by pattern alone, like domains that malware makes up by itself, called a domain generation algorithm or DGA. The Conficker worm in 2008 and 2009 made up to 50000 names a day, and defenders had to work out its algorithm to block them in advance.')}
{run('confidence')}
{viz('cydga')}
{run('dga_detect')}
{fxs(fx('Bayes with odds', 'posterior odds = prior odds &times; LR<sub>1</sub> &times; LR<sub>2</sub> &times; ...', 'Prior 0.2 gives odds 0.25. After ratios 4 and 9: odds 9, so P = 0.9.', key=True),
     fx('Odds and probability', 'odds = p / (1 &minus; p), p = odds / (1 + odds)', 'odds 1 means p = 0.5.', key=True),
     fx('Letter entropy', 'H = &minus;&Sigma; p<sub>c</sub> log<sub>2</sub> p<sub>c</sub>', 'google: 1.918 bits per letter. 12 different letters: log<sub>2</sub> 12 &asymp; 3.585, the maximum for that length.'))}
{table(['Admiralty source reliability', 'Information credibility'], [
    ['A completely reliable', '1 confirmed by other sources'],
    ['B usually reliable', '2 probably true'],
    ['C fairly reliable', '3 possibly true'],
    ['D not usually reliable', '4 doubtful'],
    ['E unreliable', '5 improbable'],
    ['F reliability cannot be judged', '6 truth cannot be judged']])}
''', kw=['confidence', 'Admiralty code', 'source reliability', 'information credibility', 'ICD 203', 'estimative language', 'Bayes', 'likelihood ratio', 'odds', 'threat hunting', 'hypothesis', 'DGA', 'Conficker', 'entropy'])

K.lesson('versus', 'Kinds of intelligence sources compared', f'''
{talk('Intelligence comes from many places, each with strengths and weaknesses. Your own telemetry is the most relevant but sees only what reached you. Commercial feeds are broad but costly and vary in quality. Open source intelligence is free but noisy. Government and sharing groups are trusted but can be slower. A mature team blends them and measures which ones actually led to detections.')}
{versus('Where intelligence comes from', ['', 'Own telemetry', 'Commercial feeds', 'Open source (OSINT)', 'Government and CERTs', 'Sharing groups (ISACs)'], [
    ['Relevance to you', 'Highest', 'Medium', 'Low to medium', 'Medium', 'High for your sector'],
    ['Cost', 'Staff time', 'High', 'Free', 'Free', 'Membership fee'],
    ['Speed', 'Real time', 'Fast', 'Varies', 'Can be slower', 'Fast within members'],
    ['Main risk', 'Sees only what reached you', 'False positives, duplicates', 'Noise, unverified claims', 'Broad, generic advice', 'Depends on members sharing']],
    'Start from your own logs, add CERT-In and sector sharing, and pay for commercial feeds only when you can show they produce detections you would otherwise miss.')}
''', kw=['comparison', 'OSINT', 'commercial feeds', 'telemetry', 'CERT-In', 'ISAC'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that defenders share warnings about attackers. A student can match indicators, map rules to ATT&amp;CK and update confidence with Bayes. A working analyst writes reports with confidence levels, runs hunts and manages feeds. Experts track whole groups across years, link campaigns, and advise leaders on strategic risk.')}
{ladder(
    '<p>Defenders tell each other about tricks and bad websites they have seen, so others can block them early, like neighbours warning each other about a thief in the area.</p>',
    '<p>The intelligence cycle and four levels, IOCs and their decay, Pyramid of Pain, Kill Chain, Diamond Model, ATT&amp;CK coverage, STIX and TLP 2.0, Admiralty code, Bayes with odds, DGA scoring.</p>',
    '<p>Run a threat intelligence programme: collection plans, MISP, feed scoring, hunts from hypotheses, finished reports with estimative language, and sharing with ISACs and CERT-In.</p>',
    '<p>Attribution and its limits, campaign clustering, graph analytics over infrastructure, measuring the value of intelligence, and machine learning for domain and URL classification that resists evasion.</p>')}
{grow('Explain why sharing warnings about attackers helps everyone.',
      'Match indicators, map coverage and judge confidence with numbers.',
      'Run an intelligence and hunting programme for an organisation.')}
''', kw=['beginner', 'expert', 'attribution', 'campaign tracking'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Intelligence</b>: checked knowledge that supports a decision. Cycle: direction, collection, processing, analysis, dissemination, feedback. Levels: strategic, operational, tactical, technical.',
    '<b>Indicators</b>: hashes, IPs, domains, artefacts, tools, TTPs. Pyramid of Pain (Bianco 2013): higher hurts the attacker more. Decay U = 2<sup>&minus;t/h</sup>, give expiry dates.',
    '<b>Models</b>: Kill Chain (2011, 7 links), Diamond (2013, 4 corners), ATT&amp;CK (14 tactics, technique IDs). Layers multiply: &Pi;(1 &minus; b<sub>i</sub>).',
    '<b>Sharing</b>: STIX 2.1 objects over TAXII, MISP, TLP 2.0 (RED, AMBER+STRICT, AMBER, GREEN, CLEAR), ISACs, CERT-In.',
    '<b>Analysis</b>: Admiralty A to F and 1 to 6, estimative words, Bayes with odds and likelihood ratios, no double counting. Hunting from hypotheses. DGA scoring (Conficker).'],
    'Security Operations 2.2: cloud security, the shared responsibility model and the mistakes behind most cloud breaches.')}
{files('Three tasks: count log lines that match indicators, tactic coverage, and Bayes updating with likelihood ratios.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which indicator is easiest for an attacker to change?', ['Their TTPs', 'A file hash', 'Their tools', 'Their way of working'], 1, 'Bottom of the pyramid.', 'Changing one byte of a file gives a new hash.')
K.quiz('e', 'How many tactics does the MITRE ATT&amp;CK Enterprise matrix have?', ['7', '10', '14', '20'], 2, 'From reconnaissance to impact.', 'Hundreds of techniques sit under those 14 tactics.')
K.quiz('e', 'What does TLP:CLEAR mean?', ['Do not share', 'Anyone may see it, it can be published', 'Only your team', 'Only the police'], 1, 'Open.', 'It replaced TLP:WHITE in TLP 2.0.')
K.quiz('e', 'Raw data becomes intelligence when', ['It is large', 'It is checked, explained and useful for a decision', 'It is encrypted', 'It is old'], 1, 'Decision.', 'A list of a million IPs is data, not intelligence.')
K.quiz('m', 'In the Cyber Kill Chain, why is breaking an early link better?', ['It is required by law', 'Less of the attack has happened, so there is less harm and clean up', 'Later links cannot be broken', 'It is cheaper to buy'], 1, 'Earlier, less harm.', 'Stopping delivery means nothing was installed.')
K.quiz('m', 'What are the four corners of the Diamond Model?', ['CIA plus audit', 'Adversary, capability, infrastructure, victim', 'Detect, protect, respond, recover', 'Hash, IP, domain, tool'], 1, 'Four corners.', 'Knowing one corner helps find the others.')
K.quiz('m', 'Why give IP address indicators a short expiry?', ['IPs are long', 'Cloud addresses are reused by innocent owners within days', 'IPs are encrypted', 'Feeds cost money'], 1, 'Reuse.', 'Old IP indicators cause false alarms.')
K.quiz('m', 'On the Admiralty scale, what does B2 mean?', ['Unreliable, false', 'Usually reliable source, probably true information', 'Confirmed by the government', 'Second hand rumour'], 1, 'Letter for source, number for information.', 'A to F for the source, 1 to 6 for the information.')
K.quiz('m', 'What format is STIX 2.1 written in?', ['XML only', 'JSON', 'CSV', 'PDF'], 1, 'Modern web format.', 'STIX 1.x used XML. TAXII carries STIX over HTTPS.')
K.quiz('h', 'Two feeds both report an IP, but feed B copies feed A. How should Bayes treat them?', ['Multiply both ratios', 'As one source, because they are not independent', 'Ignore both', 'Add the ratios'], 1, 'Independence.', 'Double counting makes you far too confident.')
K.quiz('h', 'Three independent controls each stop 70% of attacks. What share gets past all three?', ['30%', '2.7%', '0.9%', '70%'], 1, 'Multiply the passes.', '0.3 &times; 0.3 &times; 0.3 = 0.027.')
K.quiz('h', 'Why does detecting TTPs cause the attacker more pain than blocking IPs?', ['TTPs are secret', 'Changing how they work takes much more time and money than renting a new server', 'IPs cannot be blocked', 'TTPs are hashed'], 1, 'Cost to change.', 'Top of the Pyramid of Pain.')
K.quiz('h', 'Conficker made up to 50000 domains a day. How did defenders block it?', ['Blocked each domain after it was used', 'Reverse engineered the algorithm and blocked or registered future domains in advance', 'Turned off DNS', 'Paid the authors'], 1, 'Predict.', 'The Conficker Working Group coordinated with registries worldwide.')
K.quiz('x', 'In the style of a CMU 18-731 question: prior 1%, a source reports malicious with P(report | bad) = 0.9 and P(report | benign) = 0.1. Posterior?', ['90%', 'About 8.3%', '50%', '1%'], 1, 'LR = 9.', 'odds 1/99 &times; 9 = 0.0909, p = 0.0833. A good source on a rare event still leaves doubt.')
K.quiz('x', 'In the style of an Oxford security question: the highest letter entropy a 12 character string can have is', ['12 bits per letter', 'log<sub>2</sub> 12 &asymp; 3.585 bits per letter', '8 bits per letter', '1 bit per letter'], 1, 'All letters different.', 'Maximum entropy is log<sub>2</sub> n when all n symbols differ.')

K.calc('e', 'Rules cover 9 of 14 ATT&amp;CK tactics. Coverage as a percent? Round to 2 decimals.', '64.29', 'Divide and times 100.', ['9 / 14 = 0.642857.', 'Times 100.', eq('64.29%')], check=round(9 / 14 * 100, 2))
K.calc('e', 'Prior chance 0.2. What are the odds?', '0.25', 'p / (1 &minus; p).', ['1 &minus; 0.2 = 0.8.', '0.2 / 0.8.', eq('0.25')], check=0.25)
K.calc('e', 'Letter entropy of "abcd"?', '2', 'log<sub>2</sub> 4.', ['Four different letters, each p = 1/4.', 'H = log<sub>2</sub> 4.', eq('2 bits per letter')], check=2)
K.calc('m', 'Prior 0.2, then one report with likelihood ratio 4. Posterior probability?', '0.5', 'Odds times ratio.', ['Prior odds 0.25.', '0.25 &times; 4 = 1.', eq('p = 1 / 2 = 0.5')], check=0.5)
K.calc('m', 'Then a second independent report with ratio 4. Posterior probability?', '0.8', 'Odds 4.', ['Odds 1 &times; 4 = 4.', 'p = 4 / 5.', eq('0.8')], check=0.8)
K.calc('m', 'An IP indicator has a half life of 7 days. Usefulness after 14 days?', '0.25', 'Two halvings.', ['14 / 7 = 2 half lives.', '2<sup>&minus;2</sup>.', eq('0.25')], check=0.25)
K.calc('m', 'Half life 7 days. After how many days is usefulness below 0.1? Round to 2 decimals.', '23.25', 'h log<sub>2</sub> 10.', ['Solve 2<sup>&minus;t/7</sup> = 0.1.', 't = 7 &times; log<sub>2</sub> 10 = 7 &times; 3.3219.', eq('&asymp; 23.25 days')], check=round(7 * math.log2(10), 2))
K.calc('m', 'A DGA makes 50000 domains a day. How many in a year of 365 days?', '18250000', 'Multiply.', ['50000 &times; 365.', 'Each one would need blocking.', eq('18250000')], check=50000 * 365)
K.calc('m', 'Three independent controls stop 70% each. Chance an attack passes all? Round to 3 decimals.', '0.027', '0.3<sup>3</sup>.', ['Each lets through 0.3.', 'All three: 0.3 &times; 0.3 &times; 0.3.', eq('0.027')], check=0.027)
K.calc('h', 'Letter entropy of "google"? Round to 3 decimals.', '1.918', 'g and o twice, l and e once.', ['p = 1/3, 1/3, 1/6, 1/6.', 'H = 2 &times; (1/3)(1.585) + 2 &times; (1/6)(2.585).', eq('&asymp; 1.057 + 0.862 = 1.918')], check=round(1.9182958340544896, 3))
K.calc('h', 'A feed of 10000 IPs, 2% belong to shared hosting used by many good sites. How many blocks could hit good sites?', '200', 'Share of the feed.', ['2% = 0.02.', '0.02 &times; 10000.', eq('200 risky blocks')], check=200)
K.calc('h', 'Prior odds 0.25 and ratios 4, 9 and 1. Final probability? Round to 2 decimals.', '0.9', 'Multiply the odds.', ['0.25 &times; 4 &times; 9 &times; 1 = 9.', 'p = 9 / 10.', eq('0.9')], check=0.9)
K.calc('x', 'Prior 0.01, P(report | bad) = 0.9, P(report | benign) = 0.1. Posterior? Round to 4 decimals.', '0.0833', 'Bayes.', ['Top: 0.9 &times; 0.01 = 0.009.', 'Bottom: 0.009 + 0.1 &times; 0.99 = 0.108.', eq('0.009 / 0.108 &asymp; 0.0833')], check=round(0.009 / 0.108, 4))
K.calc('x', 'Maximum letter entropy for a 12 letter string? Round to 3 decimals.', '3.585', 'log<sub>2</sub> 12.', ['All 12 letters different.', 'Each p = 1/12.', eq('log<sub>2</sub> 12 &asymp; 3.585')], check=round(math.log2(12), 3))

K.assign('count_matches', 'e', 'Count log lines that match indicators',
         '<p>Write <code>count_matches(lines, iocs)</code> that returns how many lines contain at least one of the indicator strings.</p>',
         '''
def count_matches(lines, iocs):
    # your code here
    pass
''', [('count_matches(["a 1.2.3.4", "b evil.example", "c ok"], ["1.2.3.4", "evil.example"])', 2), ('count_matches(["x 1.2.3.4 evil.example"], ["1.2.3.4", "evil.example"])', 1), ('count_matches([], ["1.2.3.4"])', 0), ('count_matches(["clean"], [])', 0)],
         '''
def count_matches(lines, iocs):
    count = 0
    for line in lines:
        for ioc in iocs:
            if ioc in line:
                count += 1
                break
    return count
''', 'For each line, stop at the first indicator found, so a line counts once.', '<p>Real SIEMs match on parsed fields, not raw text, so that an IP inside a longer number does not match by mistake.</p>')
K.assign('tactic_coverage', 'm', 'ATT&amp;CK tactic coverage',
         '<p>rules is a list of tactic names, one per rule (a tactic may repeat). Write <code>tactic_coverage(rules, total=14)</code> that returns the percent of tactics with at least one rule, rounded to 1 decimal.</p>',
         '''
def tactic_coverage(rules, total=14):
    # your code here
    pass
''', [('tactic_coverage(["Execution", "Impact"])', 14.3), ('tactic_coverage(["Execution", "Execution"])', 7.1), ('tactic_coverage([])', 0.0), ('tactic_coverage(["A", "B", "C", "D"], total=4)', 100.0)],
         '''
def tactic_coverage(rules, total=14):
    covered = len(set(rules))
    return round(covered / total * 100, 1)
''', 'A set removes repeats. Divide by the total and turn it into a percent.', '<p>Counting techniques gives a much harder and more honest picture, since a tactic can have dozens of techniques.</p>')
K.assign('posterior', 'h', 'Bayes with likelihood ratios',
         '<p>Write <code>posterior(prior, ratios)</code> that turns the prior probability into odds, multiplies by every likelihood ratio, turns the odds back into a probability and returns it rounded to 4 decimals.</p>',
         '''
def posterior(prior, ratios):
    # your code here
    pass
''', [('posterior(0.2, [4])', 0.5), ('posterior(0.2, [4, 4])', 0.8), ('posterior(0.2, [4, 9, 1])', 0.9), ('posterior(0.01, [9])', 0.0833), ('posterior(0.5, [])', 0.5)],
         '''
def posterior(prior, ratios):
    odds = prior / (1 - prior)
    for ratio in ratios:
        odds = odds * ratio
    return round(odds / (1 + odds), 4)
''', 'odds = p / (1 &minus; p), multiply, then p = odds / (1 + odds).', '<p>Working in odds turns Bayes’ rule into plain multiplication, which is why analysts and spam filters like it.</p>')

K.must('Intelligence', 'Checked knowledge for a decision. Cycle: direction, collection, processing, analysis, dissemination, feedback. Strategic, operational, tactical, technical. FireEye found SolarWinds (Dec 2020).')
K.must('Indicators', 'IOCs: hash, IP, domain, artefacts, tools, TTPs. Pyramid of Pain (Bianco 2013): higher costs the attacker more. U(t) = 2<sup>&minus;t/h</sup>, retire at t = h log<sub>2</sub>(1/U<sub>min</sub>).')
K.must('Models', 'Kill Chain (Lockheed Martin 2011): recon, weaponise, deliver, exploit, install, C2, actions. Diamond (2013): adversary, capability, infrastructure, victim. ATT&amp;CK: 14 tactics, IDs like T1110.')
K.must('Sharing', 'STIX 2.1 (JSON) over TAXII, MISP. TLP 2.0 (FIRST 2022): RED, AMBER+STRICT, AMBER, GREEN, CLEAR. ISACs, CERT-In. Test feeds before auto blocking.')
K.must('Confidence', 'Admiralty A to F source, 1 to 6 information. ICD 203 words. Posterior odds = prior odds &times; &Pi; LR. Independent sources only. Layers: P(pass) = &Pi;(1 &minus; b<sub>i</sub>).')
K.must('Hunting and DGA', 'Hypothesis from intel, search, then a new rule. DGA: entropy, few vowels, digits, domain age. Conficker up to 50000 domains a day, blocked by predicting the algorithm.')

T = K.topic(
    slug='cy-threatintel', topic='cy-threatintel', step=(2, 'Intelligence, cloud and governance', 'cy-o2', 'Learning about attackers before they arrive, securing the cloud, and the rules, risk methods and laws that guide security work.', 'Advanced'),
    title='Threat intelligence: knowing the attacker', short='Threat intelligence', badge='2.1', minutes=70,
    lead='How defenders learn about attackers and use that knowledge: the intelligence cycle and its four levels, indicators and the Pyramid of Pain, the Cyber Kill Chain, the Diamond Model and MITRE ATT&amp;CK, sharing with STIX, TAXII and TLP 2.0, judging confidence with the Admiralty code and Bayes, and hunting, including spotting machine made domains.',
    desc='threat intelligence, intelligence cycle, strategic, operational, tactical, technical, IOC, indicator of compromise, Pyramid of Pain, Bianco, TTPs, Cyber Kill Chain, Lockheed Martin, Diamond Model, MITRE ATT&CK, tactics, techniques, coverage, STIX 2.1, TAXII, MISP, TLP 2.0, ISAC, CERT-In, Admiralty code, ICD 203, Bayes, likelihood ratio, odds, threat hunting, DGA, Conficker, entropy, indicator decay',
    summary='The intelligence cycle, IOCs and the Pyramid of Pain, Kill Chain, Diamond and ATT&amp;CK, STIX and TLP, confidence with Bayes, hunting and DGAs.',
    keywords=['threat intelligence', 'IOC', 'Pyramid of Pain', 'Kill Chain', 'Diamond Model', 'MITRE ATT&CK', 'STIX', 'TLP', 'Admiralty', 'Bayes', 'DGA'],
    recap='<p>Turn data into decisions, detect behaviour rather than throwaway clues, describe attacks in shared words, share under clear rules, and always say how sure you are.</p>',
    added='2026-11-15')
