# Security Operations 1.1: logging, monitoring and the SIEM. Checked against RFC 3164 and RFC 5424 (syslog), the
# Microsoft Windows security auditing event reference (4624, 4625, 4672, 4688, 4720, 1102), the Sigma project
# specification (Roth and Patzke, 2017), MITRE ATT&CK techniques T1110, T1078 and T1070, NIST SP 800-92 Guide to
# Computer Security Log Management (2006), Axelsson, The Base-Rate Fallacy and its Implications for the Difficulty of
# Intrusion Detection (ACM CCS 1999), Schneier and Kelsey, Secure Audit Logs to Support Computer Forensics (1998),
# PCI DSS v4.0 requirement 10, CERT-In Directions of 28 April 2022, and public reports on the Target (2013) and
# Equifax (2017) breaches.
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, safe, attack

chapter('cy-siem')
K = Kit()

K.code('parse_logs', r'''
# Turn log lines from three different systems into one common shape (a dictionary with the same keys)
import json
import re

RAW_LINES = [
    "Nov 15 09:12:04 web1 sshd[811]: Failed password for root from 203.0.113.9 port 52144 ssh2",
    "EventID=4625 Time=2026-11-15T09:12:09Z Account=asha Source=203.0.113.9 Host=PC-22",
    '{"ts": "2026-11-15T09:12:30Z", "event": "login", "user": "asha", "ip": "203.0.113.9", "ok": true}',
    "Nov 15 09:14:40 web1 sshd[815]: Accepted password for deploy from 10.0.0.5 port 50001 ssh2",
]

SSH_PATTERN = re.compile(r"(\w+ +\d+ [\d:]+) (\S+) sshd\[\d+\]: (Failed|Accepted) password for (\S+) from (\S+)")


def parse(line):
    """Return one event as a dictionary, or None if we do not know this format."""
    match = SSH_PATTERN.search(line)
    if match:
        time, host, word, user, ip = match.groups()
        result = "failure" if word == "Failed" else "success"
        return {"time": time, "host": host, "user": user, "ip": ip, "action": "logon", "outcome": result, "source": "sshd"}
    if line.startswith("EventID="):
        fields = dict(part.split("=", 1) for part in line.split())
        result = "failure" if fields["EventID"] == "4625" else "success"   # 4625 failed logon, 4624 success
        return {"time": fields["Time"], "host": fields["Host"], "user": fields["Account"], "ip": fields["Source"],
                "action": "logon", "outcome": result, "source": "windows"}
    if line.startswith("{"):
        data = json.loads(line)
        result = "success" if data["ok"] else "failure"
        return {"time": data["ts"], "host": "shop-app", "user": data["user"], "ip": data["ip"],
                "action": "logon", "outcome": result, "source": "webapp"}
    return None


events = []
for line in RAW_LINES:
    event = parse(line)
    events.append(event)
    print(f"{event['source']:8} {event['user']:7} {event['ip']:12} {event['outcome']}")

# Now one simple search works across every source
bad_ip = "203.0.113.9"
hits = [e for e in events if e["ip"] == bad_ip]
print(f"\nEvents from {bad_ip}: {len(hits)}")
for e in hits:
    print("   ", e["source"], e["user"], e["outcome"])
''')

K.code('brute_rule', r'''
# A detection rule: alert when one source IP has N or more failed logins inside W minutes.
# A second rule: a success from the same IP soon after that alert means the guessing may have worked.
from collections import defaultdict, deque

N = 5      # how many failures
W = 5      # inside how many minutes

# (minute, source ip, user, outcome) in time order
events = [
    (1, "198.51.100.4", "ravi", "failure"),
    (4, "198.51.100.4", "ravi", "success"),           # one typo, then fine: normal
    (10, "203.0.113.9", "admin", "failure"),
    (11, "203.0.113.9", "admin", "failure"),
    (11, "203.0.113.9", "root", "failure"),
    (12, "203.0.113.9", "admin", "failure"),
    (12, "203.0.113.9", "test", "failure"),
    (13, "203.0.113.9", "admin", "failure"),
    (15, "203.0.113.9", "admin", "success"),          # guessed it
]

recent = defaultdict(deque)     # ip -> minutes of recent failures
alerted = {}                    # ip -> minute of the alert

for minute, ip, user, outcome in events:
    window = recent[ip]
    while window and window[0] <= minute - W:      # forget failures older than W minutes
        window.popleft()
    if outcome == "failure":
        window.append(minute)
        if len(window) >= N and ip not in alerted:
            alerted[ip] = minute
            print(f"minute {minute:2}: ALERT brute force from {ip}, {len(window)} failures in {W} minutes")
    elif ip in alerted:
        print(f"minute {minute:2}: CRITICAL {ip} logged in as {user} after a brute force alert. Lock the account now.")

print("\nIPs alerted:", list(alerted))
print("The single typo from 198.51.100.4 raised nothing, which is what we want.")
''')

K.code('sigma_rule', r'''
# A rule written as data, in the spirit of Sigma: the same rule can be turned into a search for any SIEM.
# This one looks for the Windows security log being cleared (event 1102), a common step to hide an attack.
RULE = {
    "title": "Security event log cleared",
    "attack_technique": "T1070.001 Indicator Removal: Clear Windows Event Logs",
    "level": "high",
    "selection": {"source": "windows", "EventID": "1102"},
    "filter_admin_tool": {"user": "backup-svc"},          # a known, approved job that rotates logs
    "condition": "selection and not filter_admin_tool",
}

events = [
    {"source": "windows", "EventID": "4624", "user": "asha", "host": "PC-22"},
    {"source": "windows", "EventID": "1102", "user": "backup-svc", "host": "DC-1"},
    {"source": "windows", "EventID": "1102", "user": "asha", "host": "PC-22"},
    {"source": "linux", "EventID": "1102", "user": "root", "host": "web1"},
]


def matches(event, block):
    """True if every field in the block has the same value in the event."""
    for field, value in block.items():
        if event.get(field) != value:
            return False
    return True


def rule_fires(event, rule):
    selected = matches(event, rule["selection"])
    filtered = matches(event, rule["filter_admin_tool"])
    return selected and not filtered        # the condition written in the rule


for event in events:
    if rule_fires(event, RULE):
        print(f"[{RULE['level']}] {RULE['title']} on {event['host']} by {event['user']}")
        print(f"        maps to MITRE ATT&CK {RULE['attack_technique']}")
print("The approved backup job and the Linux event did not fire, so the rule stays quiet when it should.")
''')

K.code('impossible_travel', r'''
# Impossible travel: two logins by the same user, too far apart to fly between in the time given
import math

def distance_km(lat1, lon1, lat2, lon2):
    """Great circle distance with the haversine formula. Earth radius 6371 km."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    d_lat = p2 - p1
    d_lon = math.radians(lon2 - lon1)
    h = math.sin(d_lat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d_lon / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))

CITY = {"Mumbai": (19.0760, 72.8777), "Delhi": (28.6139, 77.2090), "London": (51.5074, -0.1278)}
MAX_SPEED = 900          # km per hour, roughly a passenger jet

# (user, hour of the day, city where the IP address is located)
logins = [
    ("meena", 9.0, "Mumbai"),
    ("meena", 12.5, "Delhi"),     # a morning flight: possible
    ("meena", 13.0, "London"),    # half an hour later: impossible
]

for (u1, t1, c1), (u2, t2, c2) in zip(logins, logins[1:]):
    km = distance_km(*CITY[c1], *CITY[c2])
    hours = t2 - t1
    speed = km / hours
    verdict = "IMPOSSIBLE, alert" if speed > MAX_SPEED else "possible"
    print(f"{u1}: {c1} -> {c2}  {km:7.1f} km in {hours:.1f} h = {speed:8.1f} km/h  {verdict}")

print("\nBefore alerting, check for a VPN or a company proxy. They make a user appear in another city.")
''')

K.code('base_rate', r'''
# The base rate fallacy: what share of alerts are real attacks? (Bayes' rule)
TOTAL = 1_000_000

def precision(attacks, detection_rate, false_alarm_rate):
    true_alerts = attacks * detection_rate
    false_alerts = (TOTAL - attacks) * false_alarm_rate
    return true_alerts, false_alerts, true_alerts / (true_alerts + false_alerts)

print("attacks  detect  false alarm   true   false   precision")
for attacks, det, fa in [(100, 0.99, 0.01), (100, 0.99, 0.001), (100, 0.99, 0.0001), (10000, 0.99, 0.01), (100, 0.50, 0.0001)]:
    tp, fp, p = precision(attacks, det, fa)
    print(f"{attacks:7}  {det:6.2f}  {fa:11.4f}  {tp:5.0f}  {fp:6.0f}   {p:9.4f}")

print("\nLesson: when attacks are rare, cutting false alarms helps far more than catching a few more attacks.")
''')

K.code('hash_chain', r'''
# A tamper evident log: each record stores HMAC(key, previous tag + text). Change or delete one line and
# the check fails at that point. The key lives on a separate server, so the intruder cannot rebuild the tags.
import hashlib
import hmac

KEY = b"kept-on-the-log-server"     # in real life: a secret from a vault, never in code

def tag(prev, text):
    return hmac.new(KEY, (prev + "|" + text).encode(), hashlib.sha256).hexdigest()[:12]

def write_log(lines):
    records, prev = [], "start"
    for text in lines:
        prev = tag(prev, text)
        records.append([text, prev])
    return records

def first_broken(records):
    prev = "start"
    for i, (text, stored) in enumerate(records):
        if tag(prev, text) != stored:
            return i + 1                    # line number, counting from 1
        prev = stored
    return None

log = write_log(["09:00 asha logged in", "09:05 asha opened payroll.xlsx",
                 "09:07 asha exported 900 rows", "09:09 asha deleted export.csv", "09:10 asha logged out"])
print("untouched log, first broken line:", first_broken(log))

edited = [r[:] for r in log]
edited[2][0] = "09:07 asha exported 9 rows"
print("after editing line 3, first broken line:", first_broken(edited))

deleted = log[:3] + log[4:]
print("after deleting line 4, first broken line:", first_broken(deleted))
''')

K.lesson('idea', 'Why we log, and what a SIEM does', f'''
{talk('Think of logs as the diary of every computer. Each time someone logs in, opens a file, starts a program or sends data out, the system can write one line about it. On a single laptop that is a few thousand lines a day. In a company with thousands of machines it is billions. Nobody can read that by hand. A SIEM, which stands for Security Information and Event Management, is the tool that collects all these lines in one place, puts them into the same shape, keeps them safe, and runs rules on them all day and all night to spot trouble. The name was coined by two Gartner analysts, Mark Nicolett and Amrit Williams, in 2005, when they joined two older ideas: keeping logs for reports, and watching events live. Today the best known SIEMs are Splunk, Microsoft Sentinel, IBM QRadar, Elastic Security and Google Security Operations, and Wazuh is a popular free one. Logs matter because most attacks leave traces long before damage is done. In the Target breach of 2013, security tools raised alerts when the attackers installed their malware, but the alerts were not acted on, and data on about 40 million payment cards was stolen. At Equifax in 2017, a device that inspected outgoing traffic had an expired certificate, so for about 76 days nobody saw the data leaving. Both stories teach the same lesson. Collecting logs is not enough. Someone, or some rule, has to look at them, and the tools have to be kept working. In India, the CERT-In rules of April 2022 ask companies to keep their logs for 180 days and to report serious incidents within 6 hours, so logging is also the law.')}
{src('NIST SP 800-92 Guide to Computer Security Log Management (2006), Gartner (Nicolett and Williams, 2005), RFC 3164 and RFC 5424 (syslog), Microsoft Windows security auditing reference, US Senate Commerce Committee report on the Target breach (2014), US GAO report on the Equifax breach (GAO-18-559, 2018), PCI DSS v4.0 requirement 10, CERT-In Directions under section 70B of the IT Act (28 April 2022).')}
{safe('Every program in this chapter reads made up log lines written inside the program. To practise on real logs, use your own laptop, for example the Linux journal with journalctl or the Windows Event Viewer, or free practice data sets such as the Splunk Boss of the SOC data.')}
{wwh('A <b>log</b> is a line a system writes when something happens. A <b>SIEM</b> collects logs from every system, puts them into one shape, keeps them safe and runs detection rules on them.',
     'Attacks leave traces. Without logs you cannot spot an attack while it happens, find out what happened afterwards, or prove it to a court or a regulator.',
     'Agents and collectors send logs to the SIEM. It parses each line into fields, adds context such as who owns an IP, stores everything with the right time, and checks rules. Matches become alerts for analysts.')}
{steps('The journey of one log line', [
    'A user types a wrong password on a server. The SSH service writes a line to the system log.',
    'A small agent on the server, such as a forwarder, reads the new line and sends it over an encrypted link to the SIEM.',
    'The SIEM parses the line into fields: time, host, user, source IP, action and outcome.',
    'It adds context: the IP belongs to a foreign hosting company, and the user is an administrator.',
    'Detection rules check the event together with recent events. Five failures in five minutes from one IP fire an alert.',
    'An analyst sees the alert, looks at the related events and decides what to do. The raw line is stored for months in case it is needed later.'])}
''', kw=['log', 'SIEM', 'security information and event management', 'Gartner', 'Splunk', 'Microsoft Sentinel', 'QRadar', 'Elastic', 'Wazuh', 'Target breach', 'Equifax', 'CERT-In', 'log retention', 'NIST SP 800-92'])

K.lesson('sources', 'What to log: the sources and the events that matter', f'''
{talk('You cannot log everything forever, because storage costs money and noise hides the signal. So teams pick the sources and events that tell the most. The first group is identity: logins that work and logins that fail, password resets, new accounts, and accounts that get admin rights. The second group is endpoints, meaning laptops and servers: which programs start, which services are installed, and when the audit log itself is cleared, because attackers love to wipe their tracks. The third group is the network: firewall allow and deny records, DNS lookups, web proxy logs and VPN connections. The fourth is the cloud: who changed what in the cloud console. The fifth is the applications themselves. On Windows each kind of event has a number. 4624 means a successful logon, 4625 a failed logon, 4672 means special admin rights were given at logon, 4688 means a new process started, 4720 means a user account was created, and 1102 means the security log was cleared. Many analysts know these numbers by heart. On Linux and network devices the common format is syslog, which Eric Allman wrote for the Sendmail program in the 1980s and which was later written down as RFC 3164 and then RFC 5424 in 2009. Two practical rules matter as much as the list. First, every machine must have the right time, set by NTP, or you cannot put events from different machines in order. Second, logs must leave the machine quickly, because an attacker with admin rights on a machine can delete its local logs.')}
{table(['Source', 'Key events', 'What they help catch'], [
    ['Identity (Active Directory, Entra ID, Okta)', 'Logon success 4624, failure 4625, admin logon 4672, new account 4720, MFA prompts', 'Password guessing, stolen accounts, new back door accounts'],
    ['Endpoints (Windows, Linux, macOS)', 'Process start 4688 or Sysmon 1, service install, log cleared 1102, PowerShell script logs', 'Malware running, persistence, hiding tracks'],
    ['Network', 'Firewall allow and deny, DNS queries, proxy URLs, VPN logins', 'Command and control traffic, data leaving, scans'],
    ['Cloud', 'AWS CloudTrail, Azure activity log, Google Cloud audit logs', 'Risky changes, public buckets, stolen API keys'],
    ['Applications', 'Logins, payments, admin actions, errors', 'Fraud, abuse of features, injection attempts']])}
{fxs(fx('Log volume', 'events per day = events per second &times; 86400', '2000 events per second is 172800000 events a day.', key=True),
     fx('Storage', 'bytes = events &times; average size &times; days kept', '172.8 million events of 500 bytes for 180 days is about 15.6 TB before compression.'))}
{note('Never log secrets. Passwords, full card numbers, session tokens and private keys must not appear in logs, because logs are read by many people and kept for a long time.', 'warn')}
''', kw=['log sources', 'Windows event ID', '4624', '4625', '4672', '4688', '4720', '1102', 'Sysmon', 'syslog', 'RFC 5424', 'Eric Allman', 'NTP', 'CloudTrail', 'DNS logs', 'log volume'])

K.lesson('parse', 'Parsing and normalising: one shape for every log', f'''
{talk('Every product writes its logs in its own way. The SSH service on Linux writes a sentence. Windows writes an event with numbered fields. A modern web app writes JSON. A firewall writes its own short codes. If you want to ask a simple question like show me everything from this IP address, the SIEM first has to turn all of these into the same set of fields. This step is called parsing, and the shared set of fields is called a schema. Common schemas are the Elastic Common Schema, Splunk’s Common Information Model, and OCSF, the Open Cybersecurity Schema Framework, started in 2022 by AWS, Splunk and others. Parsing often uses regular expressions, which are small patterns that match text, as in the program below. After parsing comes enrichment, which means adding facts the log line did not carry: which country an IP is in, whether it is on a list of known bad addresses, which department a user works in, and how important a server is. Good parsing is boring but vital. If a parser breaks after a software update, the rules that depend on it go silent, and nobody notices until an attack is missed. That is why teams watch for sources that suddenly stop sending logs.')}
{viz('cylogparse')}
{run('parse_logs')}
{deep('Regular expressions in one minute', '<p>A regular expression is a pattern. <code>\\d+</code> means one or more digits, <code>\\S+</code> means one or more characters that are not spaces, and brackets <code>( )</code> capture the part we want to keep. The pattern in the program, <code>Failed password for (\\S+) from (\\S+)</code>, captures the user and the IP from an SSH log line. Write patterns that are strict enough not to grab the wrong text, and test them on real samples.</p>')}
{note('Keep the raw line as well as the parsed fields. If the parser was wrong, you can parse the raw line again later, and courts often want the original record.')}
''', kw=['parsing', 'normalisation', 'schema', 'Elastic Common Schema', 'CIM', 'OCSF', 'regular expression', 'enrichment', 'geo IP', 'threat intelligence lookup'])

K.lesson('rules', 'Detection rules: thresholds, correlation and Sigma', f'''
{talk('A detection rule is a small question the SIEM asks again and again. The simplest kind is a match: tell me whenever the security log is cleared. The next kind is a threshold over a time window: tell me when one IP fails to log in five times within five minutes. That catches password guessing, which MITRE ATT&amp;CK calls technique T1110, Brute Force. A sliding window means the SIEM always looks back the same number of minutes from now, so old failures drop out as time moves on. The third kind is correlation, which links different events into a story. Many failures followed by one success from the same IP is far more worrying than either alone, because it suggests the attacker guessed the password and is now inside, which ATT&amp;CK calls T1078, Valid Accounts. Choosing the numbers is a balance. If the threshold is too low, ordinary people who mistype raise alerts all day. If it is too high or the window too short, a patient attacker who tries one password every few minutes slips through. This is called low and slow. In 2017 Florian Roth and Thomas Patzke started Sigma, a way to write rules as plain data files that can be converted into the search language of any SIEM. Sigma rules are shared freely, so a rule written by one defender can protect thousands of companies. Each good rule also names the ATT&amp;CK technique it detects, so a team can see which techniques it covers and which it does not.')}
{viz('cybrute')}
{run('brute_rule')}
{run('sigma_rule')}
{fxs(fx('Sliding window count', 'count(t) = number of failures with t &minus; W &lt; time &le; t', 'At minute 13 with W = 5, failures at minutes 10, 11, 11, 12, 12 and 13 are inside: count 6.', key=True),
     fx('Chance that a normal user trips the rule', 'P(X &ge; N) = 1 &minus; &Sigma;<sub>k=0</sub><sup>N&minus;1</sup> e<sup>&minus;&lambda;</sup> &lambda;<sup>k</sup> / k!', 'If normal users average &lambda; = 2 failures in a window, P(X &ge; 5) is about 0.053. This Poisson model helps pick N.', key=True))}
{attack([
    ['Guess many passwords on one account fast', 'Threshold rule per account and per IP, account lockout or slow down, MFA'],
    ['Try one common password on many accounts (password spraying)', 'Count distinct accounts failed per IP, not only failures per account'],
    ['Guess slowly, one try every few minutes', 'Longer windows such as 60 minutes or a day, and baselines per user'],
    ['Clear the event log to hide', 'Rule on event 1102, and forward logs off the machine at once']])}
''', kw=['detection rule', 'threshold', 'sliding window', 'correlation', 'brute force', 'T1110', 'T1078', 'password spraying', 'low and slow', 'Sigma', 'Florian Roth', 'MITRE ATT&CK', 'Poisson'])

K.lesson('travel', 'Impossible travel and behaviour baselines', f'''
{talk('Some rules do not look for a bad event at all. They look for something that is unusual for this person. The best known is impossible travel. If Meena logs in from Mumbai at nine in the morning and from London half an hour later, she cannot have flown that far. Either someone else has her password, or something is hiding her real location. To check, the SIEM looks up where each IP address is, works out the distance on the curved surface of the Earth with the haversine formula, and divides by the time between the two logins. If the speed is faster than a passenger jet, about 900 kilometres an hour, it raises an alert. There are honest reasons for false alarms. Company VPNs, mobile networks and cloud proxies can make a user seem to be in another city, so good rules know the company’s own VPN addresses and ignore them. The wider idea is called user and entity behaviour analytics, UEBA. The system learns what is normal for each user and each machine, such as the hours they work, the servers they use, and how much data they usually download, and it flags big changes. A clerk who suddenly downloads ten thousand customer records at two in the morning is worth a look, even if each action alone is allowed.')}
{run('impossible_travel')}
{fxs(fx('Haversine distance', 'd = 2R &middot; arcsin &radic;( sin<sup>2</sup>(&Delta;&phi;/2) + cos &phi;<sub>1</sub> cos &phi;<sub>2</sub> sin<sup>2</sup>(&Delta;&lambda;/2) )', '&phi; is latitude and &lambda; is longitude, in radians. R = 6371 km. Mumbai to London is about 7192 km.', key=True),
     fx('Travel speed', 'v = d / &Delta;t', '7192 km in 0.5 hours is about 14383 km per hour, far above 900.', key=True))}
{note('Location from an IP address is a guess, not a fact. Treat impossible travel as a reason to check, then confirm with the user through a trusted channel such as a known phone number.')}
''', kw=['impossible travel', 'haversine', 'geo location', 'UEBA', 'behaviour analytics', 'baseline', 'VPN false positive', 'anomaly'])

K.lesson('baserate', 'The base rate problem: why most alerts are false', f'''
{talk('Here is a surprise that every security analyst must understand. Imagine a detector that catches 99 out of every 100 attacks, and wrongly flags only 1 out of every 100 normal events. It sounds excellent. Now feed it one million events, of which only 100 are attacks. It catches 99 attacks. But it also flags 1 percent of the 999900 normal events, which is 9999 false alarms. So an analyst sees about 10098 alerts and only 99 of them are real, less than 1 in 100. This is called the base rate fallacy, and Stefan Axelsson explained it for intrusion detection at the ACM CCS conference in 1999. The cause is simple: real attacks are rare, so even a tiny false alarm rate on a huge number of normal events makes a mountain of noise. The maths is Bayes’ rule, which you met in the foundations section. The lesson for defenders is practical. Making the detector catch a few more attacks hardly helps. Cutting false alarms helps a lot. Teams do that by adding context, by requiring two different signals before alerting, by allowing known good activity, and by ranking alerts by risk. When analysts are flooded with false alarms they get tired and start to ignore alerts, which is called alert fatigue, and that is how real attacks such as the one at Target slip through.')}
{viz('cybaserate')}
{run('base_rate')}
{fxs(fx('Bayes’ rule for alerts', 'P(attack | alert) = P(alert | attack) P(attack) / P(alert)', 'P(alert) = TPR &middot; P(attack) + FPR &middot; (1 &minus; P(attack)).', key=True),
     fx('Precision', 'precision = TP / (TP + FP)', '99 / (99 + 9999) &asymp; 0.0098.', key=True),
     fx('Two independent signals must agree', 'TPR = TPR<sub>1</sub> TPR<sub>2</sub>, FPR = FPR<sub>1</sub> FPR<sub>2</sub>', '0.9 &times; 0.9 = 0.81 detection, but 0.01 &times; 0.01 = 0.0001 false alarms. Precision jumps.'))}
''', kw=['base rate fallacy', 'Axelsson', 'Bayes rule', 'precision', 'false positive rate', 'true positive rate', 'alert fatigue', 'risk based alerting'])

K.lesson('integrity', 'Keeping logs trustworthy: time, retention and tamper evidence', f'''
{talk('A log is only useful if you can trust it. That needs three things. The first is correct time. If one server’s clock is five minutes slow, its events land in the wrong place in the story, so every machine syncs its clock with NTP, and logs should record time in UTC with the time zone shown. The second is retention, which means keeping logs long enough. Many breaches are found months after they start, so a log kept for only a week is often useless. PCI DSS, the card industry standard, asks for at least one year of audit logs with the last three months ready to search, and CERT-In in India asks for 180 days. The third is integrity, meaning that nobody can quietly change or delete old lines. Attackers with admin rights often clear logs, so logs should be copied off the machine at once to a store that only accepts new lines, often called write once storage. On top of that, the log can be made tamper evident with a hash chain. Bruce Schneier and John Kelsey described secure audit logs in 1998. Each record carries a hash, or better a keyed hash called an HMAC, of the previous record’s tag plus its own text. If anyone edits or deletes a record, the chain stops matching at that point, and the checker can show exactly where. The same idea is used in systemd journal sealing on Linux and, in a bigger form, in blockchains and in Certificate Transparency logs.')}
{viz('cyhashchain')}
{run('hash_chain')}
{fxs(fx('Hash chain', 't<sub>i</sub> = HMAC<sub>K</sub>(t<sub>i&minus;1</sub> || m<sub>i</sub>), t<sub>0</sub> = start value', 'Changing m<sub>j</sub> changes t<sub>j</sub>, so the check fails at record j.', key=True),
     fx('Cost to check', 'n records need n HMAC computations', 'A million records take well under a second on a laptop.'))}
{note('A hash chain shows that a log was changed, not what it said before. Pair it with copies kept on a separate system that the attacker cannot reach.')}
''', kw=['log integrity', 'NTP', 'UTC', 'retention', 'PCI DSS requirement 10', 'write once storage', 'WORM', 'hash chain', 'HMAC', 'Schneier and Kelsey', 'secure audit log', 'journal sealing', 'Certificate Transparency'])

K.lesson('soc', 'The security operations centre: people, triage and automation', f'''
{talk('The SIEM is a tool. The people who use it work in a security operations centre, or SOC. Many SOCs have tiers. Tier 1 analysts look at new alerts, check the facts and close the false ones or pass the real ones up. Tier 2 analysts dig deeper into real incidents and decide how to contain them. Tier 3 analysts and threat hunters look for attackers that no rule has found yet, and they write new rules. A SOC lead watches the numbers. Two of the most important are mean time to detect, MTTD, which is how long attackers are inside before anyone notices, and mean time to respond, MTTR, which is how long it then takes to stop them. Lower is better for both. Triage means sorting alerts by how urgent they are, using the importance of the machine, the rights of the user, and how sure the rule is. Repetitive work is handed to SOAR tools, which stands for security orchestration, automation and response. A SOAR playbook can, for example, look up an IP in threat intelligence, check whether the user is travelling, and lock the account, all within seconds, and then ask a human to confirm. Detection engineering is the name for treating rules like software: write them, test them on real and simulated data, keep them in version control, measure their false alarms, and retire the ones that never help.')}
{steps('Triage of one alert, the way a tier 1 analyst does it', [
    'Read the alert: which rule fired, on which host and user, and when.',
    'Check the context: is the host important, does the user have admin rights, is the IP known good or known bad.',
    'Look at nearby events from the same user, host and IP in the minutes before and after.',
    'Decide: false alarm (close it with a reason), or real or unsure (raise to tier 2 with notes).',
    'If it was a false alarm, suggest a rule change so it does not happen again.'])}
{fxs(fx('Mean time to detect', 'MTTD = (&Sigma; detection time &minus; start time) / number of incidents', 'Incidents found after 2, 5, 11 and 30 days give MTTD = 12 days.', key=True),
     fx('Analysts needed', 'analysts = alerts per day &times; minutes per alert / minutes per shift', '3000 alerts of 10 minutes over 480 minute shifts need 62.5 analysts. Cutting false alarms is cheaper.'))}
''', kw=['SOC', 'security operations centre', 'tier 1', 'tier 2', 'threat hunting', 'MTTD', 'MTTR', 'triage', 'SOAR', 'playbook', 'detection engineering'])

K.lesson('versus', 'SIEM compared with other monitoring tools', f'''
{talk('People often mix up the names of monitoring tools, so here they are side by side. Log management simply collects and stores logs for search and reports. A SIEM adds normalising, correlation rules and alerts across every source. EDR, endpoint detection and response, is an agent on each laptop and server that watches processes in great detail and can stop or isolate a machine. NDR watches network traffic. XDR joins endpoint, network, email and cloud data from one vendor into one view. SOAR automates the response steps. They work together: EDR and NDR see deeply in their own area, the SIEM sees across everything, and SOAR acts fast.')}
{versus('Which monitoring tool does what', ['', 'Log management', 'SIEM', 'EDR', 'XDR', 'SOAR'], [
    ['Main job', 'Collect, store and search logs', 'Correlate all sources and alert', 'Watch and control each endpoint', 'Unify several sensors from one vendor', 'Automate response steps'],
    ['Sees', 'Whatever is sent to it', 'Every log source', 'Processes, files and memory on one host', 'Endpoint, email, network, cloud', 'Alerts from other tools'],
    ['Can act', 'No', 'Alerts only, actions through SOAR', 'Yes: kill process, isolate host', 'Yes, within its products', 'Yes: lock accounts, block IPs, open tickets'],
    ['Weak spot', 'No detection logic', 'Only as good as its rules and data', 'Blind where no agent runs', 'Ties you to one vendor', 'A bad playbook acts fast and wrong']],
    'Use EDR on every machine for depth, a SIEM for the whole picture and for evidence, and SOAR to take the boring steps off analysts.')}
''', kw=['comparison', 'log management', 'SIEM', 'EDR', 'NDR', 'XDR', 'SOAR'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('At the start, you only need to know that computers keep a diary and that someone should read it. A college student can parse logs, write threshold and correlation rules, and explain the base rate problem with numbers. A working analyst triages alerts, writes Sigma rules mapped to ATT&amp;CK and tunes them. Experts design whole detection programmes and research better ways to find rare attacks in huge data.')}
{ladder(
    '<p>Every computer keeps a diary called a log. If a stranger tries many wrong passwords, the diary shows it, and a guard program can raise an alarm.</p>',
    '<p>Log sources and Windows event IDs, syslog, parsing with regular expressions, sliding window and correlation rules, impossible travel with haversine, Bayes and the base rate problem, hash chained logs.</p>',
    '<p>Run a SIEM, write and test Sigma rules mapped to MITRE ATT&amp;CK, measure precision and coverage, build SOAR playbooks, and size storage and retention for laws such as PCI DSS and CERT-In.</p>',
    '<p>Streaming detection at scale, graph based correlation of attack stories, learning baselines that stay robust when attackers poison them, provable log integrity with forward secure keys, and cost aware alert ranking.</p>')}
{grow('Explain what a log and a SIEM are, and why alerts need people.',
      'Parse logs, write detection rules and work out their precision.',
      'Design and tune a detection programme for a whole company.')}
''', kw=['beginner', 'expert', 'detection programme', 'forward secure logging'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Logs and SIEM</b>: logs are each system’s diary. A SIEM collects, normalises, stores and checks them with rules (term from Gartner, 2005). Target 2013 and Equifax 2017 show logs must be watched and tools kept working.',
    '<b>Sources</b>: identity, endpoint, network, cloud and apps. Windows 4624, 4625, 4672, 4688, 4720, 1102. Syslog RFC 5424. NTP time, never log secrets.',
    '<b>Parsing</b>: regular expressions turn text into fields in one schema (ECS, CIM, OCSF). Enrich with geo, threat intel and asset value. Keep the raw line.',
    '<b>Rules</b>: match, threshold in a sliding window, correlation (failures then success). Sigma rules as data, mapped to ATT&amp;CK T1110, T1078, T1070.',
    '<b>Baselines</b>: impossible travel with haversine and v = d / t, UEBA. Check VPNs before alerting.',
    '<b>Base rate</b>: precision = TP / (TP + FP). Rare attacks make most alerts false (Axelsson 1999). Cut false alarms, combine signals.',
    '<b>Trust</b>: UTC and NTP, retention (PCI 1 year, CERT-In 180 days), ship logs off the host, HMAC hash chains (Schneier and Kelsey 1998).'],
    'Security Operations 1.2: incident response, from the first alert to the lessons learned.')}
{files('Three tasks: parse an SSH log line, a sliding window brute force rule, and finding the first broken link in a hash chained log.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is a SIEM mainly used for?', ['Writing code', 'Collecting logs from many systems and alerting on suspicious patterns', 'Encrypting disks', 'Blocking spam only'], 1, 'Collect and alert.', 'It puts all logs in one shape and runs detection rules on them.')
K.quiz('e', 'Which Windows event ID means a failed logon?', ['4624', '4688', '4625', '1102'], 2, 'Failed.', '4624 is a successful logon, 4688 a new process, 1102 the log being cleared.')
K.quiz('e', 'Why must every server’s clock be synced with NTP?', ['To save power', 'So events from different machines can be put in the right order', 'To speed up logins', 'NTP encrypts logs'], 1, 'Order.', 'Wrong clocks scramble the story of an attack.')
K.quiz('e', 'Which of these should never be written to a log?', ['A user name', 'A failed login time', 'A user’s password', 'The source IP'], 2, 'Secrets.', 'Logs are read by many people and kept for a long time.')
K.quiz('m', 'Many failed logins from one IP, then a success from the same IP. Why is this worse than the failures alone?', ['It is not worse', 'The attacker may have guessed the password and is now inside', 'It means the firewall is off', 'It shows a disk fault'], 1, 'Correlation.', 'ATT&amp;CK calls using a guessed or stolen login T1078, Valid Accounts.')
K.quiz('m', 'An attacker tries one common password on 500 different accounts. Which rule catches it best?', ['Failures per account in 5 minutes', 'Distinct accounts failed per source IP', 'Successful logins per day', 'Disk usage'], 1, 'Spraying.', 'Each account sees only one failure, so per account counts miss it.')
K.quiz('m', 'What is Sigma?', ['A SIEM product', 'A shared format for writing detection rules as data that converts to any SIEM', 'An encryption mode', 'A Windows event'], 1, 'Rules as data.', 'Started by Florian Roth and Thomas Patzke in 2017.')
K.quiz('m', 'Why should logs be sent off the machine quickly?', ['To free disk space only', 'An attacker with admin rights can delete local logs', 'Local logs are always wrong', 'It is faster to read them'], 1, 'Hide tracks.', 'Clearing logs is ATT&amp;CK technique T1070.')
K.quiz('m', 'Logins from Mumbai and then London 30 minutes apart. What is a likely honest explanation to rule out first?', ['A slow clock', 'A VPN or proxy that makes the user appear elsewhere', 'A full disk', 'An old browser'], 1, 'VPN.', 'IP location is a guess, so check known VPN ranges.')
K.quiz('h', 'A detector has 99% detection and 1% false alarms. Attacks are 1 in 10000 events. About what share of alerts are real?', ['99%', '50%', 'About 1%', '0%'], 2, 'Base rate.', 'Precision is about 0.0098, as Axelsson showed in 1999.')
K.quiz('h', 'To improve precision when attacks are rare, which change helps most?', ['Raise detection from 99% to 99.5%', 'Cut the false alarm rate from 1% to 0.01%', 'Add more storage', 'Use a bigger screen'], 1, 'False alarms.', 'The number of false alarms scales with the huge number of normal events.')
K.quiz('h', 'In a hash chained log, an intruder deletes record 4 of 10. Where does the checker first fail?', ['Record 1', 'At the record that now sits where record 4 was', 'Record 10 only', 'It never fails'], 1, 'Next link.', 'The old record 5 now follows record 3, and its tag does not match.')
K.quiz('h', 'Why is an HMAC with a key kept elsewhere better than a plain hash for a tamper evident log?', ['It is shorter', 'Without the key, an intruder cannot recompute valid tags after changing records', 'It is faster', 'It compresses the log'], 1, 'Key.', 'With a plain hash, an intruder can rebuild the whole chain.')
K.quiz('x', 'In the style of a CMU security operations exam: normal users average 2 failed logins per window (Poisson). With N = 5, about what share of user windows trip the rule?', ['0.5%', 'About 5.3%', '50%', '20%'], 1, '1 &minus; P(X &le; 4).', 'e<sup>&minus;2</sup>(1 + 2 + 2 + 4/3 + 2/3) &asymp; 0.947, so about 0.053.')
K.quiz('x', 'In the style of an MIT 6.858 question: two independent detectors must both alert. Each has TPR 0.9 and FPR 0.01. What are the combined rates?', ['TPR 0.9, FPR 0.01', 'TPR 0.81, FPR 0.0001', 'TPR 0.99, FPR 0.02', 'TPR 0.81, FPR 0.02'], 1, 'Multiply.', 'Both must fire, so both rates multiply. Detection drops a little, false alarms drop a hundred times.')

K.calc('e', 'Failures from one IP at minutes 10, 11, 11, 12, 12 and 13. At minute 13 with a 5 minute window, how many are counted?', '6', 'Count those after minute 8.', ['The window covers 8 &lt; t &le; 13.', 'All six failures are inside.', eq('count = 6')], check=6)
K.calc('e', '2000 events per second. How many events per day?', '172800000', 'Seconds in a day.', ['A day has 24 &times; 3600 = 86400 seconds.', '2000 &times; 86400.', eq('172800000 events')], check=2000 * 86400)
K.calc('e', '99 true alerts and 9999 false alarms. What is the precision? Round to 4 decimals.', '0.0098', 'TP / (TP + FP).', ['TP + FP = 10098.', '99 / 10098.', eq('0.0098')], check=round(99 / 10098, 4))
K.calc('m', '172.8 million events a day at 500 bytes each. How many GB a day? (1 GB = 10<sup>9</sup> bytes)', '86.4', 'Multiply then divide.', ['172800000 &times; 500 = 86400000000 bytes.', 'Divide by 10<sup>9</sup>.', eq('86.4 GB per day')], check=86.4)
K.calc('m', 'Keep 86.4 GB a day for 180 days, as CERT-In asks. How many GB?', '15552', 'Multiply.', ['86.4 &times; 180.', 'Before any compression.', eq('15552 GB, about 15.6 TB')], check=round(86.4 * 180, 6))
K.calc('m', 'Base rate 1 in 10000, detection 0.99, false alarm rate 0.01. P(attack | alert)? Round to 4 decimals.', '0.0098', 'Bayes.', ['Top: 0.99 &times; 0.0001 = 0.000099.', 'Bottom: 0.000099 + 0.01 &times; 0.9999 = 0.010098.', eq('0.000099 / 0.010098 &asymp; 0.0098')], check=round(0.99e-4 / (0.99e-4 + 0.01 * 0.9999), 4))
K.calc('m', 'A user logs in 5000 km away 2.5 hours after the last login. Speed in km per hour?', '2000', 'Distance over time.', ['v = d / &Delta;t.', '5000 / 2.5.', eq('2000 km/h, faster than a jet, so alert')], check=2000)
K.calc('m', 'Two places on the equator are 10 degrees of longitude apart. Distance in km with R = 6371? Round to 2 decimals.', '1111.95', 'Arc length.', ['On the equator d = R &times; &Delta;&lambda; in radians.', '10 degrees = &pi;/18 = 0.174533 radians.', eq('6371 &times; 0.174533 &asymp; 1111.95 km')], check=round(6371 * math.pi / 18, 2))
K.calc('m', 'Incidents were found 2, 5, 11 and 30 days after they started. What is the MTTD in days?', '12', 'Average.', ['Sum = 48.', 'There are 4 incidents.', eq('48 / 4 = 12 days')], check=12)
K.calc('h', '3000 alerts a day, 10 minutes each, 480 minute shifts. How many analysts?', '62.5', 'Total minutes over shift.', ['3000 &times; 10 = 30000 minutes.', 'Divide by 480.', eq('62.5 analysts')], check=62.5)
K.calc('h', '100 attacks in 1000000 events and perfect detection. What false alarm rate gives precision 0.5? Round to 6 decimals.', '0.0001', 'FP must equal TP.', ['TP = 100, so FP must be 100.', 'FPR = 100 / 999900.', eq('&asymp; 0.0001, that is 0.01%')], check=round(100 / 999900, 6))
K.calc('h', '100000000 normal events a day and a false alarm rate of 0.001%. How many false alarms a day?', '1000', 'Rate as a fraction.', ['0.001% = 0.00001.', '10<sup>8</sup> &times; 10<sup>&minus;5</sup>.', eq('1000 false alarms')], check=1000)
K.calc('x', 'Two detectors must both fire: TPR 0.81, FPR 0.0001. 100 attacks in 1000000 events. Precision? Round to 4 decimals.', '0.4475', 'TP / (TP + FP).', ['TP = 100 &times; 0.81 = 81.', 'FP = 999900 &times; 0.0001 = 99.99.', eq('81 / 180.99 &asymp; 0.4475')], check=round(81 / (81 + 99.99), 4))
K.calc('x', 'Normal failures per window follow Poisson with &lambda; = 2. P(X &ge; 5)? Round to 4 decimals.', '0.0527', '1 minus P(0 to 4).', ['P(X &le; 4) = e<sup>&minus;2</sup>(1 + 2 + 2 + 4/3 + 2/3) = 7e<sup>&minus;2</sup>.', '7 &times; 0.135335 = 0.947347.', eq('1 &minus; 0.947347 &asymp; 0.0527')], check=round(1 - 7 * math.exp(-2), 4))

K.assign('parse_ssh', 'e', 'Parse an SSH log line',
         '<p>Write <code>parse_ssh(line)</code>. If the line contains <code>Failed password for USER from IP</code> or <code>Accepted password for USER from IP</code>, return a tuple <code>(user, ip, outcome)</code> where outcome is "failure" or "success". Otherwise return None.</p>',
         '''
import re

def parse_ssh(line):
    # your code here
    pass
''', [('parse_ssh("Nov 15 09:12:04 web1 sshd[811]: Failed password for root from 203.0.113.9 port 52144 ssh2")', ('root', '203.0.113.9', 'failure')),
      ('parse_ssh("Nov 15 09:14:40 web1 sshd[815]: Accepted password for deploy from 10.0.0.5 port 50001 ssh2")', ('deploy', '10.0.0.5', 'success')),
      ('parse_ssh("Nov 15 09:20:00 web1 cron[90]: job started")', None)],
         '''
import re

def parse_ssh(line):
    match = re.search(r"(Failed|Accepted) password for (\\S+) from (\\S+)", line)
    if match is None:
        return None
    word, user, ip = match.groups()
    outcome = "failure" if word == "Failed" else "success"
    return (user, ip, outcome)
''', 'One regular expression with three groups: the word, the user and the IP.', '<p>Real SSH logs also have lines such as "Invalid user" and "Disconnected", so real parsers carry several patterns.</p>')
K.assign('window_alerts', 'm', 'A sliding window brute force rule',
         '<p>events is a list of <code>(minute, ip)</code> failures in time order. Write <code>window_alerts(events, n, w)</code> that returns the list of IPs, in the order they first alert, that have at least n failures with minutes in the range <code>minute &minus; w &lt; t &le; minute</code> at the moment of a failure. Each IP alerts at most once.</p>',
         '''
def window_alerts(events, n, w):
    # your code here
    pass
''', [('window_alerts([(10, "C"), (11, "C"), (11, "C"), (12, "C"), (12, "C")], 5, 5)', ['C']),
      ('window_alerts([(1, "B"), (7, "B"), (13, "B"), (19, "B"), (25, "B")], 5, 5)', []),
      ('window_alerts([(1, "B"), (7, "B"), (13, "B"), (19, "B"), (25, "B")], 5, 60)', ['B']),
      ('window_alerts([(1, "A"), (2, "B"), (2, "A"), (3, "B"), (3, "A")], 3, 5)', ['A'])],
         '''
def window_alerts(events, n, w):
    alerted = []
    for minute, ip in events:
        if ip in alerted:
            continue
        count = 0
        for t, other_ip in events:
            if other_ip == ip and minute - w < t <= minute:
                count += 1
        if count >= n:
            alerted.append(ip)
    return alerted
''', 'For each failure, count earlier and same time failures from the same IP that fall in the window.', '<p>This simple version looks back over the whole list each time. A real SIEM keeps a queue per IP, as in the brute_rule program, so each event costs almost nothing.</p>')
K.assign('first_broken', 'h', 'Find the tampered line in a hash chained log',
         '<p>Each record is <code>[text, tag]</code>, where tag is the first 12 hex digits of SHA-256 of <code>previous_tag + "|" + text</code> and the first previous tag is <code>"start"</code>. Write <code>first_broken(records)</code> that returns the line number (from 1) of the first record whose tag does not match, or None if all match. Use the stored tag as the previous tag for the next record.</p>',
         '''
import hashlib

def make_tag(prev, text):
    return hashlib.sha256((prev + "|" + text).encode()).hexdigest()[:12]

def first_broken(records):
    # your code here
    pass
''', [('first_broken([["a", make_tag("start", "a")], ["b", make_tag(make_tag("start", "a"), "b")]])', None),
      ('first_broken([["a", make_tag("start", "a")], ["B", make_tag(make_tag("start", "a"), "b")]])', 2),
      ('first_broken([["x", "000000000000"]])', 1),
      ('first_broken([])', None)],
         '''
import hashlib

def make_tag(prev, text):
    return hashlib.sha256((prev + "|" + text).encode()).hexdigest()[:12]

def first_broken(records):
    prev = "start"
    number = 1
    for text, stored in records:
        if make_tag(prev, text) != stored:
            return number
        prev = stored
        number += 1
    return None
''', 'Walk the records, recompute each tag from the previous stored tag and the text, and stop at the first mismatch.', '<p>Real systems use an HMAC with a secret key, so an intruder cannot simply recompute all the tags after a change.</p>')

K.must('SIEM', 'Collects, normalises, stores and checks logs from every source (Gartner 2005). Target 2013 alerts ignored, Equifax 2017 expired certificate: logs must be watched and tools maintained.')
K.must('Log sources', 'Identity, endpoint, network, cloud, apps. Windows 4624 ok, 4625 fail, 4672 admin, 4688 process, 4720 new user, 1102 log cleared. Syslog RFC 5424. NTP and UTC. Never log secrets.')
K.must('Rules', 'Match, threshold in a sliding window, correlation (fails then success). Spraying: distinct accounts per IP. Sigma (2017) rules as data mapped to ATT&amp;CK T1110, T1078, T1070.')
K.must('Impossible travel', 'Haversine d = 2R arcsin &radic;(sin<sup>2</sup>(&Delta;&phi;/2) + cos &phi;<sub>1</sub> cos &phi;<sub>2</sub> sin<sup>2</sup>(&Delta;&lambda;/2)), R = 6371 km, v = d / t over 900 km/h. Rule out VPNs. UEBA baselines.')
K.must('Base rate', 'P(attack | alert) = TPR p / (TPR p + FPR (1 &minus; p)). Precision = TP / (TP + FP). Rare attacks make most alerts false (Axelsson 1999). Cut FPR, combine signals. Alert fatigue.')
K.must('Log trust', 'UTC with NTP, retention (PCI DSS 1 year with 3 months online, CERT-In 180 days and 6 hour reporting), forward off host, WORM storage, HMAC hash chain t<sub>i</sub> = HMAC(t<sub>i&minus;1</sub> || m<sub>i</sub>).')
K.must('SOC', 'Tier 1 triage, tier 2 investigation, tier 3 hunting and rules. MTTD and MTTR. SOAR playbooks automate lookups and containment. Detection engineering: rules as tested code.')

T = K.topic(
    slug='cy-siem', topic='cy-siem', step=(1, 'Detect, respond and investigate', 'cy-o1', 'How defenders watch logs and raise alerts, handle an incident step by step, and collect digital evidence that holds up.', 'Intermediate'),
    title='Logging, monitoring and the SIEM', short='Logging and SIEM', badge='1.1', minutes=80,
    lead='How defenders see attacks: which logs to collect, how a SIEM parses them into one shape, how detection rules with time windows and correlation work, impossible travel with the haversine formula, why most alerts are false when attacks are rare, and how to keep logs trustworthy with time sync, retention and hash chains.',
    desc='logging, SIEM, security information and event management, log sources, Windows event ID 4624 4625 4688 1102, syslog, RFC 5424, parsing, normalisation, schema, OCSF, enrichment, detection rule, threshold, sliding window, correlation, brute force, password spraying, Sigma, MITRE ATT&CK, impossible travel, haversine, UEBA, base rate fallacy, Bayes, precision, alert fatigue, log integrity, hash chain, HMAC, retention, PCI DSS, CERT-In, SOC, MTTD, MTTR, SOAR, EDR, XDR',
    summary='Log sources, parsing, detection rules, impossible travel, the base rate problem, tamper evident logs and the SOC.',
    keywords=['SIEM', 'logs', 'Windows events', 'syslog', 'detection rules', 'Sigma', 'impossible travel', 'base rate', 'hash chain', 'SOC'],
    recap='<p>Collect the right logs with the right time, put them in one shape, write rules that tell a story, measure how many alerts are real, and protect the logs themselves.</p>',
    added='2026-11-15')
