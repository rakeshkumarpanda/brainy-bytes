# Advanced 4.1: social engineering and phishing. Checked against Cialdini, "Influence" (1984), Mitnick and Simon,
# "The Art of Deception" (2002), the Verizon Data Breach Investigations Report 2024 (human element in 68% of
# breaches), FBI IC3 Internet Crime Report 2023 (business email compromise losses of about 2.9 billion dollars),
# RFC 7208 (SPF), RFC 6376 (DKIM), RFC 7489 (DMARC), RFC 3492 (punycode), the Gmail and Yahoo bulk sender rules
# (February 2024), Xudong Zheng's punycode demonstration (April 2017), Tischer et al., "Users Really Do Plug in USB
# Drives They Find" (IEEE S&P 2016), public reports on the Podesta phishing (2016), Twitter (15 July 2020), Uber
# (September 2022), MGM Resorts (September 2023), the deepfake voice fraud on a UK energy firm (2019) and the Arup
# deepfake video call in Hong Kong (2024), Google's security key result reported by KrebsOnSecurity (July 2018),
# and Indian government advisories on "digital arrest" scams, the 1930 helpline and cybercrime.gov.in.
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq, scene
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, attack, safe

chapter('cy-social')
K = Kit()

K.code('url_check', r'''
# A simple phishing link checker: the clues security teams teach, written as code
from urllib.parse import urlparse

BAIT = ("login", "verify", "secure", "update", "kyc", "account", "support")

def clues(url):
    u = urlparse(url)
    host = (u.hostname or "").lower()
    labels = host.split(".")
    found = []
    if u.scheme != "https":
        found.append("not https")
    if host.replace(".", "").isdigit():
        found.append("raw IP address instead of a name")
    if "@" in u.netloc:
        found.append("@ in the address hides the real host")
    if any(l.startswith("xn--") for l in labels):
        found.append("punycode: letters from another alphabet")
    if len(labels) > 3:
        found.append(f"{len(labels)} levels of subdomain")
    if any(b in host for b in BAIT):
        found.append("bait word in the host name")
    if "-" in labels[-2] if len(labels) > 1 else False:
        found.append("hyphen in the registered name")
    return host, found

for url in ["https://www.onlinesbi.sbi/",
            "http://sbi-kyc-update.co/login",
            "https://indiapost.gov.in.track-parcel.top/pay",
            "http://192.168.10.5/paytm",
            "https://www.google.com@evil.example/",
            "https://xn--pple-43d.com/"]:
    host, found = clues(url)
    print(f"{host:36s} {len(found)} clue(s): {', '.join(found) if found else 'none'}")
''')

K.code('lookalike', r'''
# Lookalike domains: swap confusable characters, then measure edit distance to known brands
CONFUSABLE = {"0": "o", "1": "l", "3": "e", "5": "s", "а": "a", "е": "e", "о": "o", "р": "p", "с": "c"}
BRANDS = ["google", "paypal", "amazon", "apple", "sbi", "hdfcbank", "icicibank", "flipkart", "paytm"]

def normalise(name):
    name = name.replace("rn", "m").replace("vv", "w")
    return "".join(CONFUSABLE.get(ch, ch) for ch in name)

def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

def check(domain):
    name = domain.split(".")[0]
    norm = normalise(name)
    best = min(BRANDS, key=lambda b: edit_distance(norm, b))
    d = edit_distance(norm, best)
    if name == best:
        verdict = "genuine name"
    elif d <= 1:
        verdict = f"LOOKALIKE of {best}"
    elif d == 2:
        verdict = f"suspicious, close to {best}"
    else:
        verdict = "not near a known brand"
    return name, norm, best, d, verdict

for dom in ["paypa1.com", "arnazon.in", "hdfcbank.com", "flipkrt.com", "gooogle.com", "sunrise-tea.in", "аpple.com"]:
    name, norm, best, d, verdict = check(dom)
    print(f"{dom:15s} reads as {norm:10s} nearest {best:9s} distance {d}  -> {verdict}")
''', long=True)

K.code('spf_dmarc', r'''
# A small SPF and DMARC evaluator on made up DNS records (real ones live in DNS TXT records)
import ipaddress

DNS = {
    "bank.example": {"spf": "v=spf1 ip4:203.0.113.0/24 -all", "dmarc": "v=DMARC1; p=reject; rua=mailto:dmarc@bank.example"},
    "bank-example.com": {"spf": "v=spf1 ip4:192.0.2.0/24 -all", "dmarc": None},
}

def spf(domain, ip):
    rec = DNS.get(domain, {}).get("spf")
    if not rec:
        return "none"
    for part in rec.split()[1:]:
        if part.startswith("ip4:") and ipaddress.ip_address(ip) in ipaddress.ip_network(part[4:]):
            return "pass"
    return "fail"

def dmarc_policy(domain):
    rec = DNS.get(domain, {}).get("dmarc")
    if not rec:
        return None
    tags = dict(t.strip().split("=", 1) for t in rec.split(";") if "=" in t)
    return tags.get("p")

def deliver(header_from, envelope_domain, ip, dkim_domain):
    from_dom = header_from.split("@")[1]
    spf_ok = spf(envelope_domain, ip) == "pass" and envelope_domain == from_dom
    dkim_ok = dkim_domain == from_dom
    policy = dmarc_policy(from_dom)
    if spf_ok or dkim_ok:
        return "inbox (DMARC pass)"
    return {"reject": "rejected", "quarantine": "spam folder", "none": "inbox, report sent"}.get(policy, "inbox, no DMARC record")

cases = [("real bank mail", "alerts@bank.example", "bank.example", "203.0.113.25", "bank.example"),
         ("spoofed From", "alerts@bank.example", "evil.example", "198.51.100.66", None),
         ("lookalike domain", "alerts@bank-example.com", "bank-example.com", "192.0.2.10", "bank-example.com"),
         ("forwarded by a list", "alerts@bank.example", "bank.example", "233.252.0.5", "bank.example")]
for name, hf, env, ip, dk in cases:
    print(f"{name:20s} -> {deliver(hf, env, ip, dk)}")
''')

K.code('bec_verify', r'''
# Business email compromise: a payment change rule that would have stopped most cases
from datetime import date

vendors = {"Shakti Steel": {"account": "HDFC 5011 2233", "phone": "+91 22 4000 1111"}}

requests = [
    {"vendor": "Shakti Steel", "new_account": "HDFC 5011 2233", "amount": 450000, "via": "email", "urgent": False},
    {"vendor": "Shakti Steel", "new_account": "YES 9988 7766", "amount": 1850000, "via": "email", "urgent": True},
]

def check_payment(r, called_back=False):
    v = vendors[r["vendor"]]
    flags = []
    if r["new_account"] != v["account"]:
        flags.append("bank details changed")
    if r["urgent"]:
        flags.append("urgent or secret")
    if r["amount"] >= 1_000_000:
        flags.append("large amount")
    if "bank details changed" in flags and not called_back:
        return "HOLD: call the vendor on " + v["phone"] + " (from your records, never from the email)", flags
    return "pay", flags

for r in requests:
    decision, flags = check_payment(r)
    print(f"Rs {r['amount']:>9,}  flags {flags}  -> {decision}")

# the 2024 Hong Kong case: about 25 million US dollars sent after a deepfake video call
print("\nRule of thumb: a request to move money or change bank details is confirmed on a second channel")
print("you already trust, such as a known phone number, before anything is paid.")
''')

K.code('training_maths', r'''
# Phishing numbers: click rates, report rates and why technical controls still matter
staff = 2000
emails_per_person_per_year = 12          # real phishing that slips past the filter
for label, click, report in [("before training", 0.20, 0.07), ("after a year of practice", 0.05, 0.60)]:
    clicks = staff * emails_per_person_per_year * click
    print(f"{label:25s} click rate {click:4.0%}  report rate {report:4.0%}  -> about {clicks:,.0f} clicks a year")

# chance that at least one person clicks one campaign sent to n people
for n, p in [(10, 0.05), (50, 0.05), (200, 0.05)]:
    print(f"campaign to {n:3d} people, each clicks with {p:.0%}: P(at least one click) = {1 - (1 - p) ** n:.3f}")

# the first reporter matters: with 500 recipients and a 60% report rate, the first report comes fast
recipients, report_rate, minutes_to_open = 500, 0.6, 30
print(f"expected reporters in a campaign of {recipients}: {recipients * report_rate:.0f}")
print("so the defence is people who report quickly plus controls (passkeys, filters) for the few who click")
''')

# ------------------------------------------------------------------------------------------------ lessons
K.lesson('idea', 'Social engineering: hacking the person instead of the computer', f'''
{talk('Every chapter so far has been about computers. This one is about people, because attackers know that it is often easier to trick a person than to break a computer. Social engineering means persuading someone to do something that helps the attacker: click a link, share a password or an OTP, open a door, or send money. It works because it uses the same instincts that make us kind and helpful. In 1984 the psychologist Robert Cialdini described six principles of influence. Reciprocity, we want to return a favour. Commitment, once we agree to something small we keep going. Social proof, we do what others seem to do. Authority, we obey people who seem important, like a manager, a police officer or a bank. Liking, we say yes to people who are friendly or similar to us. And scarcity, we rush when something seems about to run out. Every scam message you have ever received uses at least one of these. The famous hacker Kevin Mitnick, who later became a security consultant, wrote that he got most of his access just by asking people for it on the phone. The numbers today agree. The Verizon Data Breach Investigations Report for 2024 found that a person, through an error or by being tricked, was involved in about 68 percent of breaches. In India, people receive fake KYC update messages, fake electricity disconnection notices, fake job offers and, since 2024, "digital arrest" calls, where scammers pretend to be police or customs officers on a video call and frighten people into paying. The good news is that a few simple habits stop almost all of these.')}
{src('Cialdini (1984), Mitnick and Simon (2002), Verizon DBIR 2024, FBI IC3 2023, RFC 7208, RFC 6376, RFC 7489, Gmail and Yahoo sender rules (2024), Zheng (2017), Tischer et al. (2016), public reports on Twitter (2020), Uber (2022), MGM Resorts (2023), the 2019 voice deepfake and the 2024 Arup deepfake call, and Indian government advisories.')}
{wwh('<b>Social engineering</b> is manipulating people into giving up information, access or money. <b>Phishing</b> is social engineering by message: email, SMS, chat, calls or QR codes.',
     'It goes around firewalls and encryption by targeting the person who already has the access. It is cheap, it scales, and it was involved in most breaches.',
     'Slow down, check the sender, the link and the request, confirm unusual requests on a second channel, report anything odd, and use technical controls (passkeys, email authentication, filters) that still protect you when someone slips.')}
{table(['Cialdini’s principle', 'What the scammer says', 'Your counter'], [
    ['Authority', '"This is the cyber police, you are under digital arrest"', 'Real police never arrest or collect money on a video call. Hang up and call 1930.'],
    ['Scarcity and urgency', '"Your account will be blocked in 2 hours"', 'Pressure is a red flag. Banks give time and use their own app.'],
    ['Reciprocity', '"We sent you a refund by mistake, please return it"', 'Check your real balance in the bank app, not the screenshot they send.'],
    ['Social proof', '"10,000 people already doubled their money"', 'Guaranteed returns are always a scam.'],
    ['Liking', 'A friendly new contact who slowly builds trust before an "investment"', 'Never send money to someone you only know online.'],
    ['Commitment', 'Small first task paid, then bigger "deposits" needed to withdraw', 'Stop as soon as you are asked to pay to get paid.']])}
{scene('Around you', '<p>A stranger in a delivery uniform carrying a heavy box asks you to hold the office door. Most people help. That is tailgating, and it beats a door lock without touching it. The same instinct to help makes people read out an OTP to a polite caller who says they are from the bank.</p>')}
''', kw=['social engineering', 'human element', 'Cialdini', 'principles of influence', 'authority', 'urgency', 'scarcity', 'reciprocity', 'social proof', 'Kevin Mitnick', 'Verizon DBIR', 'digital arrest scam', 'KYC scam', '1930 helpline'])

K.lesson('phishing', 'Phishing in all its forms: how to spot one', f'''
{talk('Phishing comes in many shapes. Mass phishing sends the same message to millions, hoping a few bite. Spear phishing is written for one person or team, using details from LinkedIn or the company website. Whaling targets senior leaders. Smishing arrives by SMS, vishing by voice call, and quishing hides the link inside a QR code, so you cannot hover over it. Clone phishing copies a real email you received earlier and swaps the link. Some famous cases show how simple it can be. In March 2016 John Podesta, chair of a US presidential campaign, received a fake Google security alert asking him to change his password. A staffer called it legitimate by mistake, and his emails were stolen and published. On 15 July 2020 attackers phoned Twitter employees pretending to be internal IT support, got them to log in on a fake page, and then used internal tools to post from the accounts of famous people, asking followers to send bitcoin. The animation walks through the five clues to check every time: who really sent it, whether it is pushing you to hurry, where the link really goes, what it asks for, and how it greets you. Try the CEO message. It has no link and no attachment, so spam filters often let it through, but the request itself is the giveaway. If in doubt, do not click. Open the bank’s app or type the address yourself.')}
{viz('cyphishspot')}
{table(['Kind', 'Channel', 'Typical bait', 'Real example'], [
    ['Mass phishing', 'Email', 'Account blocked, prize won, parcel waiting', 'Fake bank and courier mails sent to millions'],
    ['Spear phishing and whaling', 'Email or chat', 'A message that knows your name, role and projects', 'Podesta fake Google alert, 2016'],
    ['Smishing', 'SMS, WhatsApp', 'KYC update, electricity bill, job offer', 'Fake bank KYC links in India'],
    ['Vishing', 'Phone call', 'IT support, bank fraud team, police', 'Twitter 2020, MGM Resorts 2023'],
    ['Quishing', 'QR code', 'Pay a small fee, scan to receive money', 'Fake parking and parcel QR stickers'],
    ['Clone phishing', 'Email', 'A copy of a real email with a new link', 'Resent invoices and shared document links']])}
{note('Scanning a QR code to <b>receive</b> money is always a scam. With UPI you only scan or enter your PIN to <b>pay</b>.', 'warn')}
''', kw=['phishing', 'spear phishing', 'whaling', 'smishing', 'vishing', 'quishing', 'QR code scam', 'clone phishing', 'Podesta', 'Twitter 2020 hack', 'red flags', 'UPI PIN'])

K.lesson('lookalike', 'Reading links and lookalike domains', f'''
{talk('Most phishing links try to look like a real address. The first skill is to read a web address from the right. In indiapost dot gov dot in dot track parcel dot top, the part that matters is track parcel dot top, because that is the domain that was actually registered. Anyone who owns it can put indiapost dot gov dot in in front as a subdomain. Attackers also use typosquatting, registering common mistakes such as gooogle or flipkrt, and homoglyphs, letters that look the same. The digit one looks like a small L, the letters r and n together look like m, and some Cyrillic letters are pixel for pixel identical to Latin ones. In April 2017 the researcher Xudong Zheng registered a domain made of Cyrillic letters that looked exactly like apple dot com in several browsers. Browsers now show such names in punycode, an ASCII form that starts with xn dash dash, when the letters mix alphabets. Our animation lets you type any address. It finds the registered part, swaps lookalike letters back, and measures the edit distance, the number of single letter changes, to well known brands. Security teams use the same idea to watch for new lookalike registrations of their own brand so they can get them taken down quickly.')}
{viz('cyhomoglyph')}
{run('url_check')}
{run('lookalike')}
{fxs(fx('Edit distance (Levenshtein)', 'd(a, b) = fewest insertions, deletions or substitutions turning a into b', 'd(flipkrt, flipkart) = 1. d(gooogle, google) = 1.', key=True),
     fx('Number of one edit typos of a name of length n over 26 letters', 'about 25n + 26(n + 1) + n', 'For "paytm" (n = 5): 125 + 156 + 5 = 286 possible lookalikes.'),
     fx('Reading order', 'scheme :// subdomains . registered name . ending / path', 'Only the registered name and ending tell you who owns the site.'))}
''', kw=['URL', 'domain name', 'registered domain', 'subdomain', 'typosquatting', 'homoglyph', 'IDN homograph attack', 'punycode', 'xn--', 'Xudong Zheng', 'edit distance', 'Levenshtein', 'brand monitoring'])

K.lesson('email', 'Email authentication: SPF, DKIM and DMARC', f'''
{talk('The original email system from the 1980s let anyone write any name in the From line, the way anyone can write any return address on a postcard. Three standards were added later to fix this. SPF, the Sender Policy Framework, lets a domain publish in DNS the list of servers allowed to send its mail. DKIM, DomainKeys Identified Mail, has the sending server sign each message with a private key, and receivers check the signature with a public key published in DNS, which also proves the message was not changed on the way. DMARC ties the two to the address people actually see. It passes only if SPF or DKIM passes for the same domain as the From line, and it lets the domain owner choose what receivers should do with failures: none, which only sends reports, quarantine, which sends them to spam, or reject. In February 2024 Gmail and Yahoo began requiring all three from anyone sending large volumes of mail. The animation shows four cases. A spoofed From address fails and is refused under p equals reject. A forwarded genuine message fails SPF but keeps its DKIM signature and still passes. And a lookalike domain passes everything, because the attacker really owns it. So email authentication stops exact spoofing of your domain, and only careful people and good filters stop lookalikes.')}
{viz('cydmarc')}
{run('spf_dmarc')}
{table(['Record', 'Lives in DNS at', 'Example', 'Proves'], [
    ['SPF', 'bank.example TXT', 'v=spf1 ip4:203.0.113.0/24 -all', 'This server may send for the envelope domain'],
    ['DKIM', 'selector._domainkey.bank.example TXT', 'v=DKIM1, k=rsa, p=(public key)', 'The domain signed the message and it was not changed'],
    ['DMARC', '_dmarc.bank.example TXT', 'v=DMARC1, p=reject, rua=mailto:reports@bank.example', 'The visible From domain matches a passing check, and what to do if not']])}
{steps('Rolling out DMARC safely for a company domain', ['List every service that sends mail as your domain: mail server, newsletters, ticketing, payroll.',
       'Publish SPF for them and turn on DKIM signing for each.',
       'Publish DMARC with p=none and collect the daily reports for a few weeks.',
       'Fix every legitimate sender that fails.',
       'Move to p=quarantine, then to p=reject once failures are only fakes.'])}
''', kw=['email authentication', 'SPF', 'DKIM', 'DMARC', 'alignment', 'p=reject', 'p=quarantine', 'p=none', 'DMARC reports', 'email spoofing', 'Gmail bulk sender rules', 'DNS TXT record', 'forwarding'])

K.lesson('bec', 'Business email compromise, voice cloning and deepfakes', f'''
{talk('Business email compromise, BEC for short, is the most expensive kind of social engineering. The attacker pretends to be a boss, a supplier or a lawyer and asks for a payment or a change of bank details. Often there is no link and no malware at all, just a convincing request at a busy moment. Sometimes the attacker has really broken into the supplier’s mailbox, so the message comes from the genuine address and replies inside a real conversation. The FBI’s Internet Crime Complaint Center recorded about 2.9 billion dollars of reported BEC losses in the United States in 2023 alone. Now add artificial intelligence. In 2019 the head of a UK energy company transferred 220,000 euros after a phone call from someone who sounded exactly like his German boss, reportedly a cloned voice. In early 2024 an employee in the Hong Kong office of the engineering firm Arup joined a video call with the company’s chief financial officer and several colleagues, and made fifteen transfers totalling about 25 million US dollars. Every other person on the call was a deepfake. The defence does not depend on spotting the fake, which keeps getting harder. It depends on process. Any request to move money or change bank details is confirmed on a second channel you already trust, such as a phone number from your own records, and large payments need two people to approve. Families can agree a code word for emergencies, so a panicked call from a "relative" can be checked with one question.')}
{run('bec_verify')}
{attack([
    ('Email from a "supplier" with new bank details', 'Call the supplier on the number already on file, never one from the email, before changing anything'),
    ('Urgent, secret request from the "CEO"', 'A rule that no payment skips the normal approval, whoever asks'),
    ('Cloned voice of a manager or relative', 'Hang up and call back on a known number, or ask a pre agreed code word'),
    ('Deepfake video call with "colleagues"', 'Confirm large transfers in writing through the finance system and with a second approver'),
    ('Real supplier mailbox taken over', 'Watch for new mailbox forwarding rules, require MFA, and flag first time payee accounts')])}
{fxs(fx('Expected loss avoided by a callback rule', 'saving = P(request is fraud) &times; average loss &minus; cost of the calls', '1% of 500 change requests at Rs 20 lakh: 5 frauds, Rs 1 crore avoided for a few hours of calls.', key=True))}
''', kw=['business email compromise', 'BEC', 'CEO fraud', 'invoice fraud', 'vendor email compromise', 'FBI IC3', 'deepfake', 'voice cloning', 'Arup Hong Kong', 'callback verification', 'out of band verification', 'two person approval', 'code word'])

K.lesson('pretext', 'Pretexting, baiting, tailgating and MFA fatigue', f'''
{talk('Not all social engineering comes by email. Pretexting means inventing a believable story, a pretext, to get help. A caller says they are a new employee locked out on their first day, or an auditor who needs a file urgently. In September 2023 attackers reportedly found an MGM Resorts employee on LinkedIn, called the IT help desk pretending to be that person, and got their access reset. The resulting attack shut down hotel and casino systems for days and cost the company about 100 million dollars. Baiting leaves something tempting for the victim to pick up. In a 2016 study at the University of Illinois, researchers dropped 297 USB drives around the campus. Almost all were picked up and people opened files on at least 45 percent of them. Tailgating, or piggybacking, means following someone through a secure door. And MFA fatigue, also called push bombing, floods a person with login approval requests until they tap approve just to make it stop. In September 2022 an attacker who had an Uber contractor’s password sent repeated push requests, then messaged on WhatsApp claiming to be Uber IT and saying the approvals would stop once accepted. The contractor accepted. Defences are partly people and partly design: help desks that verify identity through a manager or a video check before any reset, a rule never to plug in found USB drives, badges that everyone must show, and MFA that cannot be approved by mistake, such as number matching or, best of all, passkeys.')}
{table(['Technique', 'Real example', 'Defence'], [
    ['Pretexting the help desk', 'MGM Resorts, 2023', 'Verify the caller through a known channel or their manager before any reset'],
    ['Baiting with USB drives', 'Illinois study, 2016: files opened on at least 45% of 297 drives', 'Never plug in found drives, block unknown USB storage on work machines'],
    ['Tailgating', 'Following staff through a badge door', 'Every person badges in, polite challenge culture, turnstiles at main doors'],
    ['MFA fatigue (push bombing)', 'Uber, 2022', 'Number matching, limits on push requests, passkeys'],
    ['Fake job offers', 'Ronin bridge engineer, 2022, malware in an "offer letter"', 'Open recruiter files only in a safe viewer, verify recruiters'],
    ['Shoulder surfing and dumpster diving', 'Reading screens and thrown away papers', 'Privacy screens, shred documents, clear desk rules']])}
{fxs(fx('Chance at least one person falls for a push bombing campaign', 'P = 1 &minus; (1 &minus; p)<sup>n</sup>', 'p = 2% per person, n = 100 targets: 1 &minus; 0.98<sup>100</sup> &asymp; 0.867.', key=True))}
''', kw=['pretexting', 'help desk social engineering', 'MGM Resorts', 'baiting', 'USB drop', 'tailgating', 'piggybacking', 'MFA fatigue', 'push bombing', 'Uber 2022', 'number matching', 'fake job offer', 'shoulder surfing', 'dumpster diving'])

K.lesson('defend', 'Defending people: training, reporting and phishing resistant login', f'''
{talk('Telling people to be careful is not enough on its own, because even careful people get tired and busy. Good organisations combine three layers. The first is technical controls that catch most attacks before a person sees them: spam and malware filters, sandboxes that open attachments safely, DMARC on your own domains, warnings for external senders and lookalike domains, and browsers that block known phishing sites. The second is phishing resistant login, which protects people even when they do click. Passkeys and FIDO2 security keys, from the authentication chapter, sign in only to the real website, so a fake page receives nothing useful. Google reported in 2018 that after it gave security keys to its more than 85,000 employees in early 2017, none of their work accounts had been taken over by phishing. The third layer is people who know what to look for and, most importantly, report quickly. Practice campaigns, where the security team sends harmless fake phishing emails, can lower click rates and raise report rates, as long as they teach rather than shame. One fast report lets the team pull the message from every inbox before others click. The program shows why the report rate matters more than the click rate: in a big campaign someone almost always clicks, so the race is to notice fast.')}
{run('training_maths')}
{fxs(fx('At least one click in a campaign', 'P = 1 &minus; (1 &minus; p)<sup>n</sup>', 'p = 0.05, n = 50: 1 &minus; 0.95<sup>50</sup> &asymp; 0.923.', key=True),
     fx('Clicks a year', 'staff &times; phishing per person &times; click rate', '2,000 &times; 12 &times; 0.05 = 1,200.', key=True))}
{versus('Three layers against social engineering', ['', 'Technical filters', 'Phishing resistant login', 'Trained people'], [
    ['Stops', 'Most bulk phishing and known bad links', 'Stolen passwords and OTPs on fake sites', 'Novel scams, BEC, phone pretexts'],
    ['Misses', 'New lookalikes, messages with no link', 'Payment fraud, voice scams', 'Tired or rushed moments'],
    ['Examples', 'Filters, sandboxes, DMARC, URL rewriting', 'Passkeys, FIDO2 keys, number matching', 'Practice campaigns, report button, callback rules']],
    'No layer is enough alone. Filters thin the flood, passkeys make stolen passwords useless, and people catch what is left and report it.')}
{safe('Practise spotting phishing with free quizzes from Google (Jigsaw phishing quiz) or your bank’s awareness pages. Only run phishing simulations inside your own organisation with written approval, and never send fake messages to people outside it.')}
''', kw=['security awareness training', 'phishing simulation', 'click rate', 'report rate', 'report phishing button', 'passkeys', 'FIDO2', 'security keys', 'Google 85,000 employees', 'email filter', 'sandbox', 'external sender warning'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows the red flags and never shares passwords or OTPs. A student can explain why the tricks work and how SPF, DKIM and DMARC fit together. A professional runs awareness programmes, deploys email authentication and builds payment verification rules. Experts study human factors, measure interventions properly and fight deepfake fraud.')}
{ladder(
    '<p>Scammers pretend to be someone you trust and rush you. Stop, check the sender and link, never share an OTP or PIN, and ask someone you trust before paying anything.</p>',
    '<p>Cialdini’s six principles, kinds of phishing, reading the registered domain, edit distance, SPF, DKIM and DMARC alignment, BEC callback rules, 1 &minus; (1 &minus; p)<sup>n</sup>.</p>',
    '<p>Deploy DMARC to p=reject, run respectful phishing simulations, design help desk identity checks and payment controls, roll out passkeys, and handle reported phishing quickly.</p>',
    '<p>Research human factors and usable security, measure training effects with proper experiments, detect deepfakes and coordinated scam operations, and shape policy against scam centres.</p>')}
{grow('Spot and report phishing and scam calls.',
      'Explain the psychology and the email standards behind defences.',
      'Run an organisation wide programme against social engineering.')}
''', kw=['beginner', 'expert', 'usable security', 'human factors'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Why it works</b>: Cialdini’s authority, urgency, reciprocity, social proof, liking, commitment. Human element in about 68% of breaches (DBIR 2024).',
    '<b>Phishing</b>: mass, spear, whaling, smishing, vishing, quishing, clone. Check sender, urgency, real link, request, greeting.',
    '<b>Links</b>: read the registered domain from the right, typosquatting, homoglyphs, punycode xn--, edit distance.',
    '<b>Email authentication</b>: SPF (allowed servers), DKIM (signature), DMARC (alignment and policy none, quarantine, reject). Stops exact spoofing, not lookalikes.',
    '<b>BEC and deepfakes</b>: about 2.9 billion dollars in 2023 (IC3), the 2019 voice clone, Arup 2024. Defence is process: callback on a known number, two approvers.',
    '<b>Other tricks</b>: pretexting (MGM 2023), baiting (USB study), tailgating, MFA fatigue (Uber 2022).',
    '<b>Defence</b>: filters, passkeys and FIDO2, trained people who report fast, India 1930 and cybercrime.gov.in.'],
    'Advanced 4.2: mobile security, because the phone in your pocket is where most of these messages arrive.')}
{files('Three tasks: find the registered domain, compute edit distance, and decide DMARC delivery.')}
''', kw=['summary', 'recap'])

# ------------------------------------------------------------------------------------------------ quiz
K.quiz('e', 'A caller says they are from your bank and asks for the OTP you just received. What should you do?', ['Read it out', 'Hang up. Banks never ask for an OTP, and call the number on your card', 'Send it by SMS instead', 'Read half of it'], 1, 'An OTP is a key.', 'Anyone with the OTP can complete a payment or login.')
K.quiz('e', 'What is smishing?', ['Phishing by SMS', 'Phishing by fax', 'A kind of malware', 'A firewall rule'], 0, 'SMS plus phishing.', 'Fake KYC update links by SMS are a common example.')
K.quiz('e', 'Which part of indiapost.gov.in.track-parcel.top shows who owns the site?', ['indiapost', 'gov.in', 'track-parcel.top', 'All of it'], 2, 'Read from the right.', 'The rest is a subdomain the owner can name anything.')
K.quiz('e', 'Someone asks you to scan a QR code to receive money on UPI. This is', ['Normal', 'A scam: you only scan or enter a PIN to pay', 'Faster than a transfer', 'Safe if the amount is small'], 1, 'Direction of money.', 'Scanning and entering a PIN sends money out.')
K.quiz('m', 'Which of Cialdini’s principles does a fake "digital arrest" call mostly use?', ['Liking', 'Authority and fear', 'Reciprocity', 'Social proof'], 1, 'Who do they pretend to be?', 'They pose as police or officials to frighten people.')
K.quiz('m', 'What does SPF check?', ['That the message was not changed', 'That the sending server is allowed to send for the domain', 'That the user is human', 'The spam score'], 1, 'Sender Policy Framework.', 'It lists permitted servers in DNS.')
K.quiz('m', 'Why can DMARC not stop a lookalike domain like bank-example.com?', ['DMARC is broken', 'The attacker owns that domain and can pass SPF and DKIM for it', 'Lookalikes are not real domains', 'It can stop them'], 1, 'Whose domain is it?', 'DMARC protects exact domains, not similar looking ones.')
K.quiz('m', 'A supplier emails new bank details for the next payment. The safest step is', ['Pay as asked', 'Reply to the email to confirm', 'Call the supplier on the number already in your records', 'Ask for a screenshot'], 2, 'A second channel you already trust.', 'Replying goes to the attacker if the mailbox is compromised.')
K.quiz('m', 'What is MFA fatigue?', ['Users forgetting passwords', 'Flooding someone with approval prompts until they accept', 'Slow logins', 'A broken token'], 1, 'Push bombing.', 'This was used against Uber in 2022.')
K.quiz('h', 'A forwarded genuine message fails SPF. Why can DMARC still pass?', ['DMARC ignores SPF', 'The DKIM signature survives forwarding and aligns with the From domain', 'Forwarders are trusted', 'It cannot pass'], 1, 'Either check is enough.', 'DMARC needs SPF or DKIM to pass and align.')
K.quiz('h', 'What does a domain starting with xn-- mean?', ['It is encrypted', 'It is punycode for a name with non ASCII letters', 'It is a government site', 'It is offline'], 1, 'Punycode.', 'Browsers show it to expose mixed alphabet lookalikes.')
K.quiz('h', 'Why do passkeys stop most phishing even when a user clicks?', ['They are long passwords', 'They sign in only to the real site’s domain, so a fake page gets nothing usable', 'They block email', 'They use SMS'], 1, 'Origin binding.', 'The browser will not use the passkey on a different domain.')
K.quiz('h', 'In the Arup case of 2024, what tricked the employee?', ['A virus', 'A video call where the other participants were deepfakes', 'A fake website', 'A USB drive'], 1, 'AI generated people.', 'About 25 million US dollars was transferred.')
K.quiz('x', 'In the style of a CMU usable security question: each of 50 people clicks a phish with probability 0.05, independently. P(at least one click)?', ['0.05', 'About 0.92', '0.5', '2.5'], 1, '1 &minus; (1 &minus; p)<sup>n</sup>.', '1 &minus; 0.95<sup>50</sup> &asymp; 0.923.')
K.quiz('x', 'In the style of an IIT Delhi network security exam: what is the edit distance between "paypa1" and "paypal"?', ['0', '1', '2', '6'], 1, 'One substitution.', 'Swap 1 for l.')

# ------------------------------------------------------------------------------------------------ problems
K.calc('e', 'Edit distance between "flipkrt" and "flipkart"?', '1', 'One insertion.', ['flipk_rt.', 'Insert a.', eq('1')], check=1)
K.calc('e', 'Clicks a year: 2,000 staff, 12 phishing emails each, 5% click rate?', '1200', 'Multiply.', ['2,000 &times; 12 = 24,000.', '&times; 0.05.', eq('1,200')], check=2000 * 12 * 0.05)
K.calc('e', 'Expected reporters among 500 recipients with a 60% report rate?', '300', 'n &times; rate.', ['500 &times; 0.6.', 'Expected value.', eq('300')], check=500 * 0.6)
K.calc('m', 'P(at least one click) with n = 50 and p = 0.05? Round to 3 decimals.', '0.923', '1 &minus; (1 &minus; p)<sup>n</sup>.', ['0.95<sup>50</sup> &asymp; 0.0769.', '1 &minus; 0.0769.', eq('&asymp; 0.923')], check=round(1 - 0.95 ** 50, 3))
K.calc('m', 'P(at least one approval) when 100 people get push bombed and each accepts with p = 0.02? Round to 3 decimals.', '0.867', '1 &minus; 0.98<sup>100</sup>.', ['0.98<sup>100</sup> &asymp; 0.1326.', 'Subtract from 1.', eq('&asymp; 0.867')], check=round(1 - 0.98 ** 100, 3))
K.calc('m', 'Click rate falls from 20% to 5%. Relative reduction in percent?', '75', '(old &minus; new) / old.', ['0.15 / 0.20.', '&times; 100.', eq('75%')], check=75)
K.calc('m', 'An IP is 203.0.113.25 and SPF allows 203.0.113.0/24. How many addresses does a /24 allow?', '256', '2<sup>32 &minus; 24</sup>.', ['32 &minus; 24 = 8 host bits.', '2<sup>8</sup>.', eq('256')], check=2 ** 8)
K.calc('h', 'One edit typos of a 5 letter name over 26 letters: 25n substitutions + 26(n + 1) insertions + n deletions. Total?', '286', 'Plug in n = 5.', ['25 &times; 5 = 125.', '26 &times; 6 = 156, plus 5.', eq('286')], check=25 * 5 + 26 * 6 + 5)
K.calc('h', 'BEC callback rule: 500 change requests a year, 1% fraudulent, average loss Rs 20 lakh. Expected loss avoided in lakh?', '100', 'n &times; p &times; loss.', ['500 &times; 0.01 = 5 frauds.', '&times; 20 lakh.', eq('100 lakh = Rs 1 crore')], check=500 * 0.01 * 20)
K.calc('h', 'In the USB study, files were opened on at least 45% of 297 drives. At least how many drives? (Round up)', '134', '0.45 &times; 297.', ['0.45 &times; 297 = 133.65.', 'Round up to a whole drive.', eq('134')], check=math.ceil(0.45 * 297))
K.calc('x', 'A team wants P(at least one click) below 50% for a campaign where p = 0.05. Largest n?', '13', 'Solve 0.95<sup>n</sup> &gt; 0.5.', ['n &lt; ln 0.5 / ln 0.95 &asymp; 13.51.', 'Largest whole n.', eq('13')], check=math.floor(math.log(0.5) / math.log(0.95)))

# ------------------------------------------------------------------------------------------------ assignments
K.assign('registered_domain', 'e', 'Find the registered domain',
         '<p>Write <code>registered(host)</code> that returns the last two labels of a host name, or the last three when the last two are one of <code>co.in</code>, <code>gov.in</code>, <code>co.uk</code>. Make it lowercase.</p>',
         '''
def registered(host):
    # your code here
    pass
''', [('registered("indiapost.gov.in.track-parcel.top")', 'track-parcel.top'), ('registered("www.ONLINESBI.sbi")', 'onlinesbi.sbi'), ('registered("mail.example.co.in")', 'example.co.in'), ('registered("example.com")', 'example.com')],
         '''
def registered(host):
    labels = host.lower().split(".")
    tail = ".".join(labels[-2:])
    if tail in ("co.in", "gov.in", "co.uk") and len(labels) > 2:
        return ".".join(labels[-3:])
    return tail
''', 'Split on dots, join the last two, and check them against the short list.', '<p>Real tools use the Public Suffix List, which has thousands of endings like co.in, because the rule "last two labels" is wrong for many countries.</p>')
K.assign('edit_distance', 'm', 'Edit distance between two names',
         '<p>Write <code>edit_distance(a, b)</code> that returns the Levenshtein distance: the fewest single letter insertions, deletions or substitutions that turn a into b.</p>',
         '''
def edit_distance(a, b):
    # your code here
    pass
''', [('edit_distance("paypa1", "paypal")', 1), ('edit_distance("flipkrt", "flipkart")', 1), ('edit_distance("google", "google")', 0), ('edit_distance("kitten", "sitting")', 3)],
         '''
def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]
''', 'Dynamic programming: keep one row of distances. Each cell is the minimum of delete, insert and substitute.', '<p>This classic algorithm, from Vladimir Levenshtein in 1965, runs in time proportional to the product of the two lengths. Brand monitoring tools run it against every newly registered domain each day.</p>')
K.assign('dmarc_fate', 'h', 'Where does the email go?',
         '<p>Write <code>fate(from_domain, spf_domain, spf_pass, dkim_domain, policy)</code>. DMARC passes if (spf_pass and spf_domain == from_domain) or dkim_domain == from_domain. On pass return <code>"inbox"</code>. On fail return <code>"rejected"</code> for policy "reject", <code>"spam"</code> for "quarantine", and <code>"inbox"</code> for "none".</p>',
         '''
def fate(from_domain, spf_domain, spf_pass, dkim_domain, policy):
    # your code here
    pass
''', [('fate("bank.example", "bank.example", True, None, "reject")', 'inbox'),
      ('fate("bank.example", "evil.example", True, None, "reject")', 'rejected'),
      ('fate("bank.example", "list.example", False, "bank.example", "reject")', 'inbox'),
      ('fate("bank.example", "evil.example", False, None, "quarantine")', 'spam'),
      ('fate("bank.example", "evil.example", False, None, "none")', 'inbox')],
         '''
def fate(from_domain, spf_domain, spf_pass, dkim_domain, policy):
    aligned = (spf_pass and spf_domain == from_domain) or dkim_domain == from_domain
    if aligned:
        return "inbox"
    return {"reject": "rejected", "quarantine": "spam"}.get(policy, "inbox")
''', 'Compute one boolean for alignment, then map the policy with a small dictionary.', '<p>The second test is the key idea: SPF passed, but for the attacker’s own domain, not the one in the From line. Alignment is what makes DMARC useful.</p>')

K.must('Social engineering', 'Manipulating people for access, data or money. Cialdini’s six principles (authority, urgency and scarcity, reciprocity, social proof, liking, commitment). Human element in about 68% of breaches (DBIR 2024).')
K.must('Kinds of phishing', 'Mass, spear, whaling, smishing (SMS), vishing (voice), quishing (QR), clone. Five clues: sender, pressure, real link, what it asks for, greeting.')
K.must('Links and domains', 'Read the registered domain from the right. Typosquatting, homoglyphs (1 for l, rn for m, Cyrillic), punycode xn-- (Zheng 2017), Levenshtein edit distance.')
K.must('SPF, DKIM, DMARC', 'SPF lists allowed servers, DKIM signs messages, DMARC requires a passing check aligned with the From domain and sets p=none, quarantine or reject. Required by Gmail and Yahoo for bulk senders since February 2024. Lookalikes still pass.')
K.must('BEC and deepfakes', 'About 2.9 billion dollars of US losses in 2023 (IC3). Voice clone 2019 (220,000 euros), Arup deepfake call 2024 (about 25 million dollars). Callback on known numbers and two person approval.')
K.must('Other techniques', 'Pretexting help desks (MGM 2023), baiting USB drives (Illinois 2016, at least 45% opened), tailgating, MFA fatigue (Uber 2022), fake job offers.')
K.must('Defence', 'Filters and sandboxes, DMARC, passkeys and FIDO2 (no phishing takeovers among Google’s 85,000 staff), training that values fast reporting. India: 1930 helpline, cybercrime.gov.in, 7726 for spam SMS.')

T = K.topic(
    slug='cy-social', topic='cy-social', step=(4, 'Beyond the web', 'cy-a4', 'Security for people, phones, connected devices, industrial systems and the APIs that link them.', 'Advanced'),
    title='Social engineering and phishing: tricks, email authentication and defences', short='Social engineering', badge='4.1', minutes=80,
    lead='Why people are the most attacked part of any system and how to protect them: the psychology of influence, every kind of phishing, reading links and lookalike domains, SPF, DKIM and DMARC, business email compromise and deepfakes, pretexting, baiting and MFA fatigue, and the layered defences that work.',
    desc='social engineering, phishing, spear phishing, whaling, smishing, vishing, quishing, Cialdini, influence, authority, urgency, pretexting, baiting, tailgating, MFA fatigue, push bombing, business email compromise, BEC, deepfake, voice cloning, Arup, lookalike domain, typosquatting, homoglyph, punycode, edit distance, SPF, DKIM, DMARC, email authentication, security awareness training, phishing simulation, passkeys, FIDO2, digital arrest, 1930, cybercrime.gov.in',
    summary='Influence principles, kinds of phishing, reading links, lookalike domains, SPF, DKIM and DMARC, BEC and deepfakes, pretexting and MFA fatigue, and layered defences.',
    keywords=['social engineering', 'phishing', 'smishing', 'vishing', 'lookalike domain', 'SPF', 'DKIM', 'DMARC', 'business email compromise', 'deepfake'],
    recap='<p>Slow down when a message pushes you, read the real domain, confirm money requests on a channel you already trust, and let passkeys and email authentication protect you on the day you slip.</p>',
    added='2026-11-22')
