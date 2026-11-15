# Security Operations 1.2: incident response. Checked against NIST SP 800-61 Rev. 2 (2012) and Rev. 3 (2025), the
# NIST Cybersecurity Framework 2.0 (2024), the SANS incident handler's handbook (PICERL), GDPR article 33, the EU NIS2
# directive article 23, the US SEC rule on cybersecurity disclosure (Form 8-K item 1.05, 2023), the CERT-In Directions of
# 28 April 2022, the US CISA StopRansomware guide, and public reports on WannaCry (2017), NotPetya and Maersk (2017),
# Colonial Pipeline (2021) and the AIIMS Delhi ransomware attack (2022).
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, safe, attack

chapter('cy-incident')
K = Kit()

K.code('ir_triage', r'''
# Triage: give every incident a priority from its impact and its urgency (each 1 low, 2 medium, 3 high)
def priority(impact, urgency):
    score = impact * urgency
    if score >= 9:
        return "P1 critical: call the response team now, day or night"
    if score >= 6:
        return "P2 high: start within 1 hour"
    if score >= 3:
        return "P3 medium: start today"
    return "P4 low: handle in normal work"

incidents = [
    ("Ransomware renaming files on the main file server", 3, 3),
    ("One laptop with adware pop ups", 1, 2),
    ("Admin account logged in from an unknown country", 3, 2),
    ("Phishing email reported, nobody clicked", 1, 3),
    ("Public website defaced", 2, 3),
]
for name, impact, urgency in sorted(incidents, key=lambda x: -x[1] * x[2]):
    print(f"impact {impact} x urgency {urgency} = {impact * urgency}  {priority(impact, urgency)}")
    print("        " + name)
''')

K.code('contain_spread', r'''
# Ransomware on a grid of 4 x 6 machines. Each minute it reaches the machines next to an infected one.
# How many machines are hit if the SOC isolates them at minute m, with and without a firewall between the halves?
from collections import deque

ROWS, COLS = 4, 6

def minutes_to_reach(firewall):
    """Breadth first search from the first laptop at row 0, column 0."""
    dist = {(0, 0): 0}
    queue = deque([(0, 0)])
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            r2, c2 = r + dr, c + dc
            if not (0 <= r2 < ROWS and 0 <= c2 < COLS):
                continue
            if firewall and {c, c2} == {2, 3}:        # the firewall sits between column 2 and column 3
                continue
            if (r2, c2) not in dist:
                dist[(r2, c2)] = dist[(r, c)] + 1
                queue.append((r2, c2))
    return dist

flat = minutes_to_reach(False)
split = minutes_to_reach(True)
print("isolate at minute   flat network   with firewall")
for m in range(1, 10):
    hit_flat = sum(1 for d in flat.values() if d <= m)
    hit_split = sum(1 for d in split.values() if d <= m)
    print(f"{m:17}   {hit_flat:12}   {hit_split:13}")
print("\nFast isolation limits the damage. Segments put a ceiling on it even when the team is slow.")
''', long=True)

K.code('backup_rpo', r'''
# Backups against ransomware: data lost (recovery point) and time to restore (recovery time)
INCIDENT_HOUR = 15.5        # 15:30
DATA_TB = 4                 # size of the file server
RESTORE_MB_PER_S = 400      # restore speed

def last_backup(every):
    """Backups run at 0, every, 2 * every, ... Return the last one before the incident."""
    t = 0
    while t + every <= INCIDENT_HOUR:
        t += every
    return t

restore_hours = DATA_TB * 1_000_000 / RESTORE_MB_PER_S / 3600
print(f"Restoring {DATA_TB} TB at {RESTORE_MB_PER_S} MB/s takes {restore_hours:.2f} hours (the recovery time)\n")
for every in [24, 12, 4, 1]:
    t = last_backup(every)
    print(f"backup every {every:2} h: last good copy at {t:5.1f} h, work lost = {INCIDENT_HOUR - t:4.1f} h")

def check_32110(copies):
    """copies: list of (kind of storage, off site?, offline or immutable?, last restore test passed?)"""
    kinds = {c[0] for c in copies}
    rules = {
        "3 copies": len(copies) >= 3,
        "2 kinds of storage": len(kinds) >= 2,
        "1 off site": any(c[1] for c in copies),
        "1 offline or immutable": any(c[2] for c in copies),
        "0 restore errors": all(c[3] for c in copies),
    }
    return rules

plan = [("disk", False, False, True), ("disk", False, False, True), ("cloud", True, False, True)]
print()
for rule, ok in check_32110(plan).items():
    print(f"{rule:24} {'yes' if ok else 'NO, fix this'}")
''')

K.code('ir_metrics', r'''
# Incident metrics from timelines: time to detect, time to contain, time to recover (in hours)
from datetime import datetime

def hours(a, b):
    fmt = "%Y-%m-%d %H:%M"
    return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).total_seconds() / 3600

# start of attack, detected, contained, recovered
incidents = {
    "phishing account": ("2026-03-02 08:10", "2026-03-02 09:40", "2026-03-02 10:05", "2026-03-02 13:00"),
    "ransomware FS-02": ("2026-05-18 01:00", "2026-05-18 03:30", "2026-05-18 04:15", "2026-05-19 18:00"),
    "web shell": ("2026-07-01 12:00", "2026-07-09 12:00", "2026-07-09 15:00", "2026-07-10 09:00"),
}
detect, contain, recover = [], [], []
for name, (start, found, held, back) in incidents.items():
    d, c, r = hours(start, found), hours(found, held), hours(held, back)
    detect.append(d); contain.append(c); recover.append(r)
    print(f"{name:17} detect {d:6.1f} h   contain {c:4.2f} h   recover {r:5.1f} h")

n = len(incidents)
print(f"\nMTTD {sum(detect) / n:.1f} h, mean time to contain {sum(contain) / n:.2f} h, mean time to recover {sum(recover) / n:.1f} h")
print("The web shell went unseen for 8 days. That number, not the others, is where to invest first.")
''')

K.code('notify_deadlines', r'''
# Who must be told, and by when? Deadlines counted from when the team became aware of the incident.
from datetime import datetime, timedelta

aware = datetime(2026, 11, 12, 22, 30)      # a Thursday, 22:30

def add_business_days(start, days):
    day = start
    while days > 0:
        day += timedelta(days=1)
        if day.weekday() < 5:                 # Monday is 0, Friday is 4
            days -= 1
    return day

deadlines = [
    ("CERT-In, India (report within 6 hours)", aware + timedelta(hours=6)),
    ("EU NIS2 early warning (24 hours)", aware + timedelta(hours=24)),
    ("GDPR supervisory authority (72 hours)", aware + timedelta(hours=72)),
    ("US SEC Form 8-K (4 business days after deciding it is material)", add_business_days(aware, 4)),
]
print("aware:", aware.strftime("%a %d %b %H:%M"))
for who, when in deadlines:
    print(f"{when.strftime('%a %d %b %H:%M')}  {who}")
print("\nKeep a lawyer and the data protection officer in the loop. Rules depend on the country and the sector.")
''')

K.code('playbook', r'''
# A response playbook written as data, run step by step, the way a SOAR tool runs it.
# The case: a user reported a phishing email after typing their password into the fake page.
case = {"user": "meena", "entered_password": True, "mfa_enrolled": False, "forward_rule": True, "others_got_email": 14}

PLAYBOOK = [
    ("Reset password and end all sessions", lambda c: c["entered_password"]),
    ("Enrol user in phishing resistant MFA", lambda c: not c["mfa_enrolled"]),
    ("Delete the mail forwarding rule the attacker made", lambda c: c["forward_rule"]),
    ("Remove the same email from other mailboxes", lambda c: c["others_got_email"] > 0),
    ("Block the phishing domain at the proxy and DNS", lambda c: True),
    ("Ask a human to review sign ins of the last 7 days", lambda c: True),
]

done = 0
for step, (action, needed) in enumerate(PLAYBOOK, start=1):
    if needed(case):
        done += 1
        print(f"step {step}: DO   {action}")
    else:
        print(f"step {step}: skip {action} (not needed for this case)")
print(f"\n{done} actions for {case['user']}. {case['others_got_email']} other people got the email, so check whether any of them clicked too.")
''')

K.lesson('idea', 'What incident response is, and why a plan beats panic', f'''
{talk('An incident is any event that harms, or could harm, the safety of your systems or data. A stolen password, a laptop left in a taxi, ransomware on a server, or a website that suddenly shows strange text are all incidents. Incident response is the planned way a team deals with them. The key word is planned. When something bad happens at three in the morning, people under stress make poor choices, such as switching off every machine and destroying the evidence, or paying a ransom before checking the backups. A written plan, practised beforehand, lets people act calmly. Real cases show the cost of being unready. In May 2017 the WannaCry ransomware spread across about 150 countries in a few days and hit hospitals in the UK National Health Service, which had to cancel thousands of appointments. It was slowed when a researcher, Marcus Hutchins, registered a web address hidden in its code that acted as a kill switch. A month later NotPetya hit the shipping company Maersk, which had to reinstall about 45000 computers. Its recovery was saved by one domain controller in Ghana that happened to be offline because of a power cut. In May 2021 Colonial Pipeline shut down the main fuel pipeline on the US east coast after ransomware hit its business systems, and paid a ransom of about 4.4 million dollars, part of which the FBI later recovered. In November 2022 ransomware hit AIIMS in New Delhi, and its servers were down for about two weeks, so staff went back to paper. Each of these teams learned that the plan, the backups and the people matter more than any single tool.')}
{src('NIST SP 800-61 Rev. 2, Computer Security Incident Handling Guide (2012) and Rev. 3 (2025), NIST Cybersecurity Framework 2.0 (2024), SANS Incident Handler’s Handbook, UK National Audit Office report on WannaCry and the NHS (2017), Maersk public statements (2017 to 2019), US Department of Justice statement on the Colonial Pipeline ransom recovery (June 2021), news reports on the AIIMS Delhi attack (November and December 2022), CISA and FBI StopRansomware guide.')}
{safe('The programs here only model incidents on made up data. Practise response with tabletop exercises, where a team talks through a written scenario around a table, and with free ranges such as the CISA tabletop exercise packages.')}
{wwh('<b>Incident response</b> is the planned, step by step way a team finds, stops, cleans up and learns from a security incident.',
     'Without a plan, people panic: evidence is lost, attackers keep access, the wrong people are told too late, and the same mistake happens again.',
     'Prepare before anything happens, detect and analyse, contain the damage, remove the cause, recover safely, and feed the lessons back into preparation.')}
{table(['Word', 'Plain meaning', 'Example'], [
    ['Event', 'Anything that happens on a system', 'A user logs in'],
    ['Alert', 'An event a tool thinks is suspicious', 'Ten failed logins in a minute'],
    ['Incident', 'An event that really harms, or threatens, security', 'An attacker logged in with a guessed password'],
    ['Breach', 'An incident where data was seen or taken by someone not allowed', 'Customer records copied out'],
    ['Playbook', 'Step by step instructions for one kind of incident', 'What to do for a phishing report']])}
''', kw=['incident', 'incident response', 'event', 'alert', 'breach', 'playbook', 'WannaCry', 'NotPetya', 'Maersk', 'Colonial Pipeline', 'AIIMS ransomware', 'kill switch'])

K.lesson('lifecycle', 'The life cycle: NIST SP 800-61 and SANS PICERL', f'''
{talk('Two models describe the same work. NIST, the US standards body, published SP 800-61 in 2004 and its second revision in 2012. It has four phases: preparation, then detection and analysis, then containment, eradication and recovery, and finally post incident activity. SANS, a training organisation, splits the same work into six steps with the short name PICERL: preparation, identification, containment, eradication, recovery and lessons learned. In April 2025 NIST published revision 3, which ties incident response to the six functions of its Cybersecurity Framework 2.0: govern, identify, protect, detect, respond and recover. The words differ but the order is the same. Preparation means the plan, the contact list, the tools, the logs and the backups are ready before you need them. Detection and analysis means deciding whether an alert is a real incident and how big it is. Containment means stopping the damage from spreading, for example by isolating a machine or disabling an account. Eradication means removing the cause, such as malware, a back door or the hole the attacker used. Recovery means bringing systems back safely and watching them closely. Lessons learned means a meeting, within about two weeks, where the team asks what happened, what worked, and what to change. In real life the phases overlap and loop. A team that finds a second back door during eradication goes back to analysis. Try the animation with three different incidents.')}
{viz('cyirlife')}
{table(['NIST SP 800-61 Rev. 2', 'SANS PICERL', 'Key questions'], [
    ['Preparation', 'Preparation', 'Do we have a plan, contacts, tools, logs, backups and practice?'],
    ['Detection and analysis', 'Identification', 'Is it real? What is affected? How bad is it?'],
    ['Containment, eradication and recovery', 'Containment', 'How do we stop the spread now, without destroying evidence?'],
    ['', 'Eradication', 'What is the root cause, and have we removed every foothold?'],
    ['', 'Recovery', 'How do we restore safely and know it is clean?'],
    ['Post incident activity', 'Lessons learned', 'What will we change so it does not happen again?']])}
{note('Containment comes before eradication. First stop the attacker from doing more harm, then take the time to find everything they touched.')}
''', kw=['NIST SP 800-61', 'Rev. 3', 'SANS', 'PICERL', 'preparation', 'detection and analysis', 'containment', 'eradication', 'recovery', 'lessons learned', 'CSF 2.0'])

K.lesson('prepare', 'Preparation and triage: being ready, and sorting what matters', f'''
{talk('Most of incident response happens before the incident. A good preparation list includes a written plan approved by management, a team with named roles and backups for each person, a contact list that works even if email is down, playbooks for the common cases such as phishing, ransomware, lost devices and data leaks, logs that are already being collected, backups that have been restored in a test, and tools ready to use, such as EDR that can isolate a machine with one click. Teams also agree in advance who may take big decisions, like taking the website offline, and who talks to the press, the police and the regulators. Then, when alerts arrive, the team must triage, which means sorting by priority, the same word hospitals use for the emergency room. A simple method rates impact, how much harm, and urgency, how fast it is getting worse, each from low to high, and multiplies them. Ransomware spreading on the main server is high and high, so it is priority 1 and wakes people up at night. Adware on one laptop is low and medium, so it waits for normal hours. NIST also suggests asking three questions: what is the functional impact on the business, what is the information impact, meaning was data seen, changed or taken, and how hard will recovery be.')}
{run('ir_triage')}
{fxs(fx('Priority score', 'score = impact &times; urgency, each 1 to 3', '9 is P1, 6 is P2, 3 or 4 is P3, 1 or 2 is P4.', key=True),
     fx('Chance that at least one person clicks', 'P = 1 &minus; (1 &minus; p)<sup>n</sup>', 'If each of 200 staff clicks with p = 0.03, P &asymp; 0.998. Plan for the click, do not hope it never comes.', key=True))}
{steps('A tabletop exercise in one hour', [
    'Pick a realistic scenario, for example: the finance shared drive is encrypted on a Friday evening.',
    'Gather the people who would really respond: IT, security, a manager, legal, communications.',
    'Read the scenario in parts, adding a new fact every ten minutes.',
    'At each part, ask: who does what now, using which tool, and who must be told?',
    'Write down every gap: a missing phone number, an untested backup, an unclear decision.',
    'Fix the gaps and run a new scenario in a few months.'])}
''', kw=['preparation', 'incident response plan', 'roles', 'contact list', 'triage', 'impact', 'urgency', 'priority', 'functional impact', 'information impact', 'tabletop exercise'])

K.lesson('contain', 'Containment, eradication and recovery', f'''
{talk('Containment means stopping the harm from growing. Speed matters most here, because modern ransomware and worms move from machine to machine in minutes. The animation shows a simple network where the infection reaches the neighbouring machines every minute. If the team isolates infected machines at minute three, ten out of twenty four are hit. At minute nine, all of them are. A firewall that splits the network into segments puts a ceiling on the damage, even if the team is slow. This is why playbooks often let a tier 1 analyst isolate a machine at once without asking a manager. Containment has short term steps, like isolating a host, disabling an account, or blocking an IP address, and long term steps, like moving services to clean machines while the investigation goes on. One important rule: do not just switch everything off. Memory holds valuable evidence, such as running malware and encryption keys, and it disappears when power is cut. EDR network isolation cuts the machine off from the network but keeps it running. Eradication means removing the cause: delete the malware, close the hole the attacker used, remove accounts and back doors they created, and reset passwords, especially for admin and service accounts. Recovery means bringing systems back, often rebuilding from known good images instead of trusting cleaned machines, restoring data from clean backups, and watching closely for the attacker to return, which happens often when a foothold was missed.')}
{viz('cycontain')}
{run('contain_spread')}
{attack([
    ['Ransomware spreads from one laptop to file servers', 'Isolate infected hosts fast with EDR, network segments, block SMB between workstations'],
    ['Attacker keeps a back door account', 'List every account created or changed during the incident, remove the unknown ones, reset admin passwords'],
    ['Attacker returns through the same hole', 'Find the root cause and patch it before recovery, then watch the restored systems closely'],
    ['Attacker deletes logs to hide', 'Logs already shipped to a SIEM, so the copy survives']])}
{fxs(fx('Unchecked spread', 'I(t) = I<sub>0</sub> &middot; 2<sup>t / T</sup>', 'Doubling every T = 10 minutes from 1 machine gives 64 machines after 60 minutes.', key=True),
     fx('Deadline to stay under a limit', 't = T &middot; log<sub>2</sub>(L / I<sub>0</sub>)', 'To stay under 100 machines with T = 10: t &asymp; 66.4 minutes.'))}
''', kw=['containment', 'isolation', 'EDR network containment', 'segmentation', 'eradication', 'root cause', 'recovery', 'rebuild from image', 'volatile evidence', 'exponential spread'])

K.lesson('backups', 'Backups, RPO and RTO: recovering from ransomware', f'''
{talk('Backups are the main reason a company can recover from ransomware without paying. Two numbers describe a recovery plan. The recovery point objective, RPO, is how much data you can afford to lose, measured in time. If you back up every four hours, you may lose up to four hours of work. The recovery time objective, RTO, is how long you can afford to be down. Restoring four terabytes at four hundred megabytes a second takes almost three hours, before counting the time to check and restart everything. Modern attackers know backups are the defence, so they hunt for them first. If the backup share sits on the same network and can be reached with the same admin account, it gets encrypted too, as the animation shows. That is why the old 3 2 1 rule, three copies, on two kinds of storage, one off site, has grown into 3 2 1 1 0: add one copy that is offline or immutable, meaning it cannot be changed or deleted for a set time, and make sure restore tests show zero errors. A backup that has never been restored in a test is only a hope. Agencies such as CISA, the FBI and CERT-In advise against paying ransoms, because payment funds more attacks, does not guarantee the data comes back, and can break sanctions laws if the gang is on a sanctions list.')}
{viz('cyrpo')}
{run('backup_rpo')}
{fxs(fx('Data lost', 'loss = incident time &minus; time of last good backup &le; backup interval', 'Backups every 4 hours, incident at 15:30: last good copy at 12:00, so 3.5 hours lost.', key=True),
     fx('Restore time', 'RTO &ge; data size / restore speed', '4 TB / 400 MB per second = 10000 seconds &asymp; 2.78 hours.', key=True),
     fx('Yearly downtime from availability', 'downtime = (1 &minus; A) &times; 8760 hours', 'A = 99.9% allows 8.76 hours a year.'))}
{note('Keep backup systems in their own security zone with separate admin accounts and MFA. If one stolen admin password can delete both the servers and the backups, you have one copy, not three.', 'warn')}
''', kw=['backup', 'RPO', 'RTO', 'recovery point objective', 'recovery time objective', '3-2-1 rule', '3-2-1-1-0', 'immutable backup', 'offline backup', 'restore test', 'ransom payment', 'sanctions'])

K.lesson('comms', 'Telling the right people: roles, evidence and legal deadlines', f'''
{talk('An incident is not only a technical problem. People inside and outside the company need to know the right things at the right time. Inside, there is usually an incident commander who leads and decides, technical leads who do the hands on work, a scribe who writes down every action with its time, and someone who handles communication. Outside, the laws set deadlines. In India, the CERT-In directions of April 2022 say many kinds of incidents must be reported to CERT-In within 6 hours of noticing them. In the European Union, GDPR article 33 says a personal data breach must be reported to the data protection authority within 72 hours of becoming aware of it, and the NIS2 directive asks important companies for an early warning within 24 hours and a fuller report within 72 hours. In the United States, listed companies must file a Form 8-K with the SEC within four business days after deciding an incident is material. India’s Digital Personal Data Protection Act of 2023 also requires telling the Data Protection Board and the affected people about a personal data breach. Because of these rules, the scribe’s timeline matters: it shows when the company became aware. Evidence also needs care. Each item, such as a disk image, should have a chain of custody record that says who collected it, when, and who held it since, so it can be trusted later. The next chapter, on forensics, goes deeper into that.')}
{run('notify_deadlines')}
{run('ir_metrics')}
{table(['Rule', 'Who to tell', 'Deadline'], [
    ['CERT-In Directions (India, 2022)', 'CERT-In', '6 hours from noticing'],
    ['GDPR article 33 (EU)', 'Data protection authority', '72 hours from awareness'],
    ['NIS2 article 23 (EU)', 'National CSIRT or authority', 'Early warning 24 hours, notification 72 hours, final report 1 month'],
    ['SEC Form 8-K item 1.05 (US)', 'Investors, through the SEC', '4 business days after deciding it is material'],
    ['DPDP Act 2023 (India)', 'Data Protection Board and affected people', 'As set out in the DPDP rules']])}
{fxs(fx('Mean time to detect, contain and recover', 'mean = &Sigma; durations / number of incidents', 'Detection times of 1.5, 2.5 and 192 hours give an MTTD of 65.3 hours. One slow case dominates the mean, so also look at the median.', key=True),
     fx('Little’s law for the team’s queue', 'L = &lambda; W', '6 new incidents a day, each open 2.5 days on average, means about 15 open at any time.'))}
''', kw=['incident commander', 'scribe', 'communication', 'CERT-In 6 hours', 'GDPR article 33', '72 hours', 'NIS2', 'SEC 8-K', 'DPDP Act', 'chain of custody', 'timeline', 'Little law'])

K.lesson('lessons', 'Lessons learned and automation', f'''
{talk('The last phase is the one teams skip most often, and it is the one that makes the next incident smaller. Within about two weeks, everyone involved meets for a blameless review. Blameless means the goal is to fix the system, not to punish a person, because people hide mistakes when they fear blame, and hidden mistakes come back. The review walks through the timeline and asks what happened, why it happened, what helped, what slowed us down, and what we will change. A simple tool is the five whys: keep asking why until you reach a cause you can fix. The ransomware got in through the VPN. Why? It was not patched. Why? The patch needed a reboot and nobody owned that device. Why? It was missing from the asset list. Now the fix is clear: every device needs an owner in the asset list. Each lesson becomes a task with an owner and a date. Repetitive steps from playbooks can then be automated with SOAR, as in the program below, so the next time a phishing report arrives, the password reset, the session revoke and the email clean up happen within minutes, and a human only checks the result.')}
{run('playbook')}
{steps('The five whys for one incident', [
    'Ransomware encrypted the file server. Why did it get in? Through the company VPN.',
    'Why could it use the VPN? The VPN had a known flaw with a patch available for three weeks.',
    'Why was it not patched? The patch needed a reboot and nobody owned the device.',
    'Why did nobody own it? It was missing from the asset list.',
    'Fix: every device must have an owner in the asset list, and critical patches have a deadline that is tracked.'])}
''', kw=['lessons learned', 'blameless postmortem', 'five whys', 'root cause analysis', 'action items', 'SOAR', 'automation', 'playbook'])

K.lesson('versus', 'Response approaches compared', f'''
{talk('Companies choose how much of incident response to do themselves. Some build their own team. Others hire a managed detection and response company that watches alerts all day and night. Many sign an incident response retainer with a specialist firm that will send experts within hours when something big happens. Cyber insurance often requires one of these, and it may pay for the specialist firm and the lawyers. Each choice trades cost, speed and knowledge of your own systems.')}
{versus('Who handles incidents', ['', 'In house team', 'Managed detection and response', 'Retainer with a specialist firm', 'Ad hoc, no plan'], [
    ['Knows your systems', 'Best', 'Medium', 'Low at first', 'Varies'],
    ['Available 24 hours', 'Costly to staff', 'Yes', 'Within agreed hours', 'No'],
    ['Deep forensic skill', 'Depends on hiring', 'Medium', 'High', 'Low'],
    ['Cost', 'High and fixed', 'Monthly fee', 'Yearly fee plus hours', 'Cheapest until the incident, then the most expensive']],
    'A common mix is a small in house team that owns the plan and the playbooks, managed detection for round the clock watching, and a retainer for the rare big incident.')}
''', kw=['comparison', 'MDR', 'managed detection and response', 'retainer', 'cyber insurance', 'in house SOC'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that a team needs a plan for bad days and that reporting quickly helps. A student can name the phases, triage incidents, and work out RPO, RTO and how spread grows. A professional writes playbooks, leads response calls, and meets legal deadlines. Experts handle large crises across many countries and design how whole organisations recover.')}
{ladder(
    '<p>When something goes wrong with computers at school or work, tell an adult or the IT team quickly, and do not try to hide it. Fast reporting keeps the problem small.</p>',
    '<p>The NIST and SANS phases, triage by impact and urgency, containment versus eradication, exponential spread, RPO and RTO, 3 2 1 1 0 backups, legal deadlines, MTTD and Little’s law.</p>',
    '<p>Write and test playbooks, lead an incident call as commander, keep a defensible timeline, work with lawyers and insurers, and automate response steps with SOAR.</p>',
    '<p>Crisis management across countries and sectors, response to state sponsored intrusions, recovery engineering for very large estates, and research on automated containment that stays safe.</p>')}
{grow('Explain the phases of incident response and why reporting fast matters.',
      'Triage incidents, plan containment and work out recovery numbers.',
      'Lead a real incident from first alert to lessons learned.')}
''', kw=['beginner', 'expert', 'incident commander', 'crisis management'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Incident response</b>: the planned way to find, stop, clean and learn. Event, alert, incident, breach. WannaCry and NotPetya 2017, Colonial 2021, AIIMS 2022.',
    '<b>Life cycle</b>: NIST SP 800-61 (prepare, detect and analyse, contain eradicate recover, post incident), Rev. 3 in 2025 maps to CSF 2.0. SANS PICERL.',
    '<b>Preparation and triage</b>: plan, roles, contacts, playbooks, tested backups. Priority = impact &times; urgency. Tabletop exercises.',
    '<b>Containment</b>: speed limits spread, segments cap it. Isolate, do not switch off, to keep memory evidence. Eradicate the root cause, rebuild, watch.',
    '<b>Backups</b>: RPO is data lost, RTO is time down. 3 2 1 1 0 with an offline or immutable copy. Test restores. Agencies advise against paying.',
    '<b>Communication</b>: commander, scribe, timeline, chain of custody. CERT-In 6 hours, GDPR 72 hours, NIS2 24 and 72 hours, SEC 4 business days, DPDP Act.',
    '<b>Lessons</b>: blameless review, five whys, owners and dates, SOAR playbooks.'],
    'Security Operations 1.3: digital forensics, collecting and reading evidence so it holds up.')}
{files('Three tasks: priority from impact and urgency, data lost for a backup schedule, and machines hit by a spreading infection.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which phase comes first in NIST SP 800-61?', ['Containment', 'Preparation', 'Recovery', 'Lessons learned'], 1, 'Before anything happens.', 'Plans, contacts, tools and tested backups are made ready first.')
K.quiz('e', 'What does RPO measure?', ['How long we are down', 'How much data, in time, we can afford to lose', 'The ransom amount', 'Number of servers'], 1, 'Recovery point.', 'Backups every 4 hours mean an RPO of up to 4 hours.')
K.quiz('e', 'Ransomware is found on a server. Why isolate it instead of pulling the power?', ['Pulling power is illegal', 'Memory holds evidence such as running malware and keys, which is lost when power goes', 'Isolation is slower', 'It saves electricity'], 1, 'Volatile evidence.', 'EDR isolation cuts the network but keeps the machine running.')
K.quiz('e', 'What does the 1 offline or immutable copy in 3 2 1 1 0 protect against?', ['Disk failure only', 'Attackers who delete or encrypt every backup they can reach', 'Slow networks', 'Bad passwords'], 1, 'Attackers hunt backups.', 'An offline or locked copy cannot be changed by the attacker.')
K.quiz('m', 'Why does containment come before eradication?', ['It is cheaper', 'First stop further harm, then take time to find every foothold', 'Eradication is optional', 'Regulators require it'], 1, 'Stop the bleeding.', 'Searching while the attacker still acts lets damage grow.')
K.quiz('m', 'Under the CERT-In directions of 2022, how soon must many incidents be reported?', ['72 hours', '6 hours', '30 days', '1 week'], 1, 'Six.', 'GDPR is 72 hours, CERT-In is 6 hours from noticing.')
K.quiz('m', 'What is a blameless review for?', ['Finding someone to fire', 'Fixing the system that allowed the incident, so people report mistakes openly', 'Avoiding meetings', 'Writing press releases'], 1, 'System, not person.', 'Fear of blame hides mistakes, and hidden mistakes return.')
K.quiz('m', 'A ransomware gang offers the key for payment. What do CISA, the FBI and CERT-In advise?', ['Always pay quickly', 'Do not pay: it funds crime, may not work and can break sanctions laws', 'Pay half', 'Pay only in cash'], 1, 'Do not pay.', 'Restore from clean backups wherever possible.')
K.quiz('m', 'What made Maersk’s recovery from NotPetya possible?', ['A new firewall', 'One domain controller in Ghana that was offline during the attack because of a power cut', 'Paying the ransom', 'Cloud backups only'], 1, 'Luck.', 'It held a clean copy of the account directory. Plan for offline copies on purpose.')
K.quiz('h', 'Detection times of 1.5, 2.5 and 192 hours. Why report the median as well as the mean?', ['The mean is always wrong', 'One very slow case pulls the mean far up, the median shows the typical case', 'Medians are required by law', 'They are the same'], 1, 'Outliers.', 'Mean 65.3 hours, median 2.5 hours. Both tell part of the story.')
K.quiz('h', 'Ransomware doubles the number of infected machines every 10 minutes. How long until 1 becomes 64?', ['64 minutes', '60 minutes', '6 minutes', '640 minutes'], 1, 'Six doublings.', '2<sup>6</sup> = 64, so 6 &times; 10 minutes.')
K.quiz('h', 'A US listed company decides on a Thursday that an incident is material. When is the Form 8-K due at the latest?', ['Friday', 'The next Wednesday', 'Thursday the week after', 'Monday'], 1, 'Four business days.', 'Friday, Monday, Tuesday, Wednesday.')
K.quiz('h', 'Why rebuild servers from known good images instead of only deleting the malware?', ['It is faster', 'A hidden foothold may remain, and a clean image removes everything the attacker changed', 'Images are free', 'Malware cannot be deleted'], 1, 'Trust.', 'Attackers often leave several back doors.')
K.quiz('x', 'In the style of a Stanford security exam: 6 new incidents arrive per day and each stays open 2.5 days on average. How many are open at a typical time?', ['2.4', '15', '8.5', '3.5'], 1, 'Little’s law.', 'L = &lambda; W = 6 &times; 2.5 = 15.')
K.quiz('x', 'In the style of an IIT Bombay question: with doubling time T, the latest containment time to stay under L infected machines from I<sub>0</sub> is', ['T &middot; L / I<sub>0</sub>', 'T &middot; log<sub>2</sub>(L / I<sub>0</sub>)', 'T<sup>2</sup>', 'L &minus; I<sub>0</sub>'], 1, 'Solve 2<sup>t/T</sup> = L / I<sub>0</sub>.', 'Take log base 2 of both sides and multiply by T.')

K.calc('e', 'Backups every 4 hours starting at 00:00. Ransomware hits at 15:30. Hours of work lost?', '3.5', 'Last backup before 15:30.', ['Backups at 00, 04, 08, 12, 16.', 'The last one before 15:30 is 12:00.', eq('15.5 &minus; 12 = 3.5 hours')], check=3.5)
K.calc('e', 'Impact 3 and urgency 2. What is the priority score?', '6', 'Multiply.', ['score = impact &times; urgency.', '3 &times; 2.', eq('6, which is P2')], check=6)
K.calc('e', 'Three incidents were contained in 2, 4 and 6 hours. Mean time to contain?', '4', 'Average.', ['Sum = 12 hours.', 'Three incidents.', eq('12 / 3 = 4 hours')], check=4)
K.calc('m', 'Infected machines double every 10 minutes from 1. How many after 60 minutes?', '64', 'Count the doublings.', ['60 / 10 = 6 doublings.', '2<sup>6</sup>.', eq('64 machines')], check=64)
K.calc('m', 'On the 4 by 6 grid, spreading one step a minute from a corner, how many machines are hit by minute 3?', '10', 'Count r + c &le; 3.', ['Row 0: 4 machines, row 1: 3.', 'Row 2: 2, row 3: 1.', eq('4 + 3 + 2 + 1 = 10')], check=10)
K.calc('m', 'Restore 4 TB at 400 MB per second. How many hours? Round to 2 decimals.', '2.78', 'Size over speed.', ['4 TB = 4000000 MB.', '4000000 / 400 = 10000 seconds.', eq('10000 / 3600 &asymp; 2.78 hours')], check=round(4e6 / 400 / 3600, 2))
K.calc('m', 'Availability target 99.9%. Allowed downtime per year in hours?', '8.76', '(1 &minus; A) &times; 8760.', ['1 &minus; 0.999 = 0.001.', 'A year has 8760 hours.', eq('0.001 &times; 8760 = 8.76 hours')], check=8.76)
K.calc('m', 'Downtime of 18 hours costs 500000 rupees an hour. Total cost in rupees?', '9000000', 'Multiply.', ['18 &times; 500000.', 'That is 90 lakh rupees.', eq('9000000')], check=9000000)
K.calc('m', 'An incident is noticed at 23:30. CERT-In needs a report within 6 hours. By what time (hours after midnight, as a decimal)?', '5.5', 'Add 6 hours.', ['23:30 plus 6 hours.', 'That passes midnight.', eq('05:30, that is 5.5')], check=5.5)
K.calc('h', 'Each of 200 staff clicks a phishing email with probability 0.03. Chance at least one clicks? Round to 4 decimals.', '0.9977', '1 &minus; (1 &minus; p)<sup>n</sup>.', ['Nobody clicks: 0.97<sup>200</sup>.', '0.97<sup>200</sup> &asymp; 0.002261.', eq('1 &minus; 0.002261 &asymp; 0.9977')], check=round(1 - 0.97 ** 200, 4))
K.calc('h', 'Ransomware ARO 0.5 a year. SLE falls from 20000000 to 4000000 rupees with immutable backups costing 3000000 a year. Net yearly benefit in rupees?', '5000000', 'ALE saved minus cost.', ['ALE before = 0.5 &times; 20000000 = 10000000.', 'ALE after = 0.5 &times; 4000000 = 2000000, saving 8000000.', eq('8000000 &minus; 3000000 = 5000000')], check=5000000)
K.calc('h', 'Decided material on a Thursday. Form 8-K due within 4 business days. Which day?', 'Wednesday', 'Skip the weekend.', ['Day 1 Friday.', 'Days 2, 3 and 4 are Monday, Tuesday and Wednesday.', eq('Wednesday')], check='Wednesday')
K.calc('x', 'Spread doubles every 10 minutes from 1 machine. Latest containment time, in minutes, to stay under 100 machines? Round to 2 decimals.', '66.44', 'T log<sub>2</sub>(L / I<sub>0</sub>).', ['Solve 2<sup>t/10</sup> = 100.', 't = 10 &times; log<sub>2</sub> 100.', eq('10 &times; 6.6439 &asymp; 66.44 minutes')], check=round(10 * math.log2(100), 2))
K.calc('x', '6 incidents arrive per day and each is open 2.5 days. Average number open (Little’s law)?', '15', 'L = &lambda; W.', ['&lambda; = 6 per day.', 'W = 2.5 days.', eq('L = 6 &times; 2.5 = 15')], check=15)

K.assign('priority_level', 'e', 'Priority from impact and urgency',
         '<p>Write <code>priority_level(impact, urgency)</code> where each is 1, 2 or 3. Multiply them. Return "P1" for 9, "P2" for 6, "P3" for 3 or 4, and "P4" for 1 or 2.</p>',
         '''
def priority_level(impact, urgency):
    # your code here
    pass
''', [('priority_level(3, 3)', 'P1'), ('priority_level(3, 2)', 'P2'), ('priority_level(2, 2)', 'P3'), ('priority_level(1, 3)', 'P3'), ('priority_level(1, 2)', 'P4')],
         '''
def priority_level(impact, urgency):
    score = impact * urgency
    if score >= 9:
        return "P1"
    if score >= 6:
        return "P2"
    if score >= 3:
        return "P3"
    return "P4"
''', 'Compute the score, then check from the highest level down.', '<p>Real teams add more inputs, such as whether personal data is involved, but the idea of a small fixed table stays the same, so everyone sorts alerts the same way.</p>')
K.assign('work_lost', 'm', 'Data lost for a backup schedule',
         '<p>Backups run at hour 0, every, 2 &times; every and so on. Write <code>work_lost(every, incident)</code> that returns the hours between the last backup at or before the incident hour and the incident, rounded to 2 decimals.</p>',
         '''
def work_lost(every, incident):
    # your code here
    pass
''', [('work_lost(4, 15.5)', 3.5), ('work_lost(24, 15.5)', 15.5), ('work_lost(1, 15.5)', 0.5), ('work_lost(12, 12)', 0.0), ('work_lost(5, 23)', 3.0)],
         '''
def work_lost(every, incident):
    last = 0
    while last + every <= incident:
        last += every
    return round(float(incident - last), 2)
''', 'Step forward through backup times while the next one is still at or before the incident.', '<p>The same answer comes from <code>incident % every</code>, the remainder after dividing. The loop shows the idea more plainly.</p>')
K.assign('machines_hit', 'h', 'Machines hit before containment',
         '<p>A grid has <code>rows</code> by <code>cols</code> machines. Infection starts at row 0, column 0 and each minute reaches the 4 neighbours of infected machines. If <code>wall</code> is a number w, machines in columns w and w + 1 cannot infect each other. Write <code>machines_hit(rows, cols, minutes, wall=None)</code> that returns how many machines are infected after the given minutes.</p>',
         '''
from collections import deque

def machines_hit(rows, cols, minutes, wall=None):
    # your code here
    pass
''', [('machines_hit(4, 6, 3)', 10), ('machines_hit(4, 6, 9)', 24), ('machines_hit(4, 6, 9, wall=2)', 12), ('machines_hit(1, 1, 5)', 1), ('machines_hit(3, 3, 0)', 1)],
         '''
from collections import deque

def machines_hit(rows, cols, minutes, wall=None):
    dist = {(0, 0): 0}
    queue = deque([(0, 0)])
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            r2, c2 = r + dr, c + dc
            if not (0 <= r2 < rows and 0 <= c2 < cols):
                continue
            if wall is not None and {c, c2} == {wall, wall + 1}:
                continue
            if (r2, c2) not in dist:
                dist[(r2, c2)] = dist[(r, c)] + 1
                queue.append((r2, c2))
    count = 0
    for d in dist.values():
        if d <= minutes:
            count += 1
    return count
''', 'Breadth first search gives each machine the minute it is reached. Count those reached by the given minute.', '<p>Real networks are graphs, not grids, but the same search shows which machines an attacker can reach and how a segment wall changes that.</p>')

K.must('Incident response', 'Planned way to find, stop, clean and learn. Event, alert, incident, breach. WannaCry and NotPetya 2017 (Maersk about 45000 PCs), Colonial 2021, AIIMS Delhi 2022.')
K.must('Life cycle', 'NIST SP 800-61 Rev. 2: prepare, detect and analyse, contain eradicate recover, post incident. Rev. 3 (2025) maps to CSF 2.0. SANS PICERL. Contain before eradicate.')
K.must('Triage', 'Priority = impact &times; urgency (9 P1, 6 P2, 3 to 4 P3, 1 to 2 P4). Functional and information impact. P(at least one click) = 1 &minus; (1 &minus; p)<sup>n</sup>. Tabletop exercises.')
K.must('Containment', 'Speed and segments. I(t) = I<sub>0</sub> 2<sup>t/T</sup>, deadline t = T log<sub>2</sub>(L/I<sub>0</sub>). Isolate, keep power for memory evidence. Rebuild from clean images.')
K.must('Backups', 'RPO = data lost in time, RTO = time down &ge; size / speed. 3 2 1 1 0: offline or immutable copy, zero restore errors. Separate backup admin. Do not pay ransoms.')
K.must('Deadlines', 'CERT-In 6 hours. GDPR art. 33 72 hours. NIS2 24 h warning, 72 h notice, 1 month report. SEC 8-K 4 business days. DPDP Act: Board and people. Scribe timeline, chain of custody.')
K.must('Lessons', 'Blameless review within about 2 weeks, five whys, owners and dates. MTTD, MTTC, MTTR, look at median too. Little’s law L = &lambda;W. SOAR automates playbook steps.')

T = K.topic(
    slug='cy-incident', topic='cy-incident', step=(1, 'Detect, respond and investigate', 'cy-o1', 'How defenders watch logs and raise alerts, handle an incident step by step, and collect digital evidence that holds up.', 'Intermediate'),
    title='Incident response: from the first alert to lessons learned', short='Incident response', badge='1.2', minutes=75,
    lead='What a calm team does when something goes wrong: the NIST and SANS life cycles, triage by impact and urgency, why fast containment and network segments limit damage, backups against ransomware with RPO and RTO, the legal deadlines for reporting in India, the EU and the US, and blameless lessons learned with automated playbooks.',
    desc='incident response, NIST SP 800-61, SANS PICERL, preparation, triage, priority, impact, urgency, tabletop exercise, containment, isolation, EDR, segmentation, eradication, recovery, ransomware, WannaCry, NotPetya, Maersk, Colonial Pipeline, AIIMS, backups, RPO, RTO, 3-2-1-1-0, immutable backup, CERT-In 6 hours, GDPR 72 hours, NIS2, SEC 8-K, DPDP Act, chain of custody, MTTD, MTTR, Little law, blameless postmortem, five whys, SOAR playbook',
    summary='Response life cycle, triage, containment speed, backups with RPO and RTO, reporting deadlines and lessons learned.',
    keywords=['incident response', 'NIST 800-61', 'PICERL', 'triage', 'containment', 'ransomware', 'backups', 'RPO', 'RTO', 'CERT-In', 'GDPR'],
    recap='<p>Prepare before you need it, sort alerts by real harm, contain fast without losing evidence, restore from copies the attacker cannot touch, tell the right people on time, and learn without blame.</p>',
    added='2026-11-15')
