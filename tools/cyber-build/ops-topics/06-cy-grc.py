# Security Operations 2.3: governance, risk, compliance and law. Checked against ISO/IEC 27001:2022 and 27002:2022 (93
# Annex A controls in four themes), the NIST Cybersecurity Framework 2.0 (February 2024), CIS Critical Security Controls
# v8 (18 controls, 153 safeguards, IG1 56), AICPA SOC 2 trust services criteria, PCI DSS v4.0, the Information
# Technology Act 2000 with the 2008 amendment (sections 43, 43A, 66, 66C, 66D, 66F, 72A), the Digital Personal Data
# Protection Act 2023 and its schedule of penalties, the CERT-In Directions of 28 April 2022, the RBI Cyber Security
# Framework for banks (2016), GDPR articles 5, 25, 33, 34, 35 and 83, the Irish DPC decision against Meta (May 2023), the
# Council of Europe Budapest Convention (2001), the US Computer Fraud and Abuse Act (1986), and AICPA audit sampling
# guidance.
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk

chapter('cy-grc')
K = Kit()

K.code('control_crosswalk', r'''
# One control, many frameworks: a crosswalk shows which NIST CSF 2.0 function each of our controls supports
controls = [
    # our control, ISO 27001:2022 Annex A, CIS Controls v8, CSF 2.0 function
    ("Security policy approved by the board", "5.1", "-", "GV"),
    ("Supplier security reviews", "5.19", "15", "GV"),
    ("Asset inventory", "5.9", "1", "ID"),
    ("MFA for all users", "8.5", "6", "PR"),
    ("Security awareness training", "6.3", "14", "PR"),
    ("Patch management", "8.8", "7", "PR"),
    ("Central logging and alerts", "8.15, 8.16", "8", "DE"),
    ("Incident response plan", "5.24", "17", "RS"),
]
FUNCTIONS = {"GV": "Govern", "ID": "Identify", "PR": "Protect", "DE": "Detect", "RS": "Respond", "RC": "Recover"}

count = {code: 0 for code in FUNCTIONS}
for name, iso, cis, fn in controls:
    count[fn] += 1
    print(f"{name:38} ISO A.{iso:10} CIS {cis:3} -> {FUNCTIONS[fn]}")

print()
for code, name in FUNCTIONS.items():
    print(f"{name:9} {'#' * count[code]:5} {count[code]}")
print("\nRecover has nothing: add tested backups and a recovery plan (ISO A.8.13, CIS 11).")
''')

K.code('audit_sample', r'''
# Audit sampling: how big a sample gives a good chance of catching a control failure?
import math
import random

def chance_to_catch(error_rate, n):
    """Probability that a sample of n contains at least one exception (independent draws)."""
    return 1 - (1 - error_rate) ** n

def sample_size(error_rate, confidence):
    """Smallest n so that the chance to catch at least one exception reaches the confidence."""
    return math.ceil(math.log(1 - confidence) / math.log(1 - error_rate))

for n in (5, 25, 45, 60):
    print(f"n = {n:2}: chance to catch a 5% failure rate = {chance_to_catch(0.05, n):.4f}")
print("\nsample needed for 95% confidence at a 5% failure rate:", sample_size(0.05, 0.95))
print("sample needed for 99% confidence at a 2% failure rate:", sample_size(0.02, 0.99))

# try it: 200 changes, 10 of them not approved, draw 25 at random 1000 times
random.seed(7)
population = [True] * 10 + [False] * 190          # True means "not approved"
hits = sum(any(random.sample(population, 25)) for _ in range(1000))
print(f"\nsimulation: a sample of 25 caught a problem in {hits} of 1000 audits")
''', long=True)

K.code('dpia_check', r'''
# Does this project need a data protection impact assessment (DPIA)? A simple screening like GDPR article 35.
projects = {
    "Staff canteen menu app": {"personal": False, "sensitive": False, "large_scale": False, "monitoring": False, "new_tech": False},
    "Face recognition at office gates": {"personal": True, "sensitive": True, "large_scale": False, "monitoring": True, "new_tech": True},
    "Loyalty card for 5 million shoppers": {"personal": True, "sensitive": False, "large_scale": True, "monitoring": True, "new_tech": False},
}

def needs_dpia(p):
    if not p["personal"]:
        return False, "no personal data"
    flags = [k for k in ("sensitive", "large_scale", "monitoring", "new_tech") if p[k]]
    # common rule of thumb from EU guidance: two or more high risk signs means do a DPIA
    return len(flags) >= 2, ", ".join(flags) if flags else "low risk processing"

for name, p in projects.items():
    need, why = needs_dpia(p)
    print(f"{name:36} {'DPIA needed' if need else 'no DPIA':12} ({why})")
print("\nPrivacy by design (GDPR article 25): build the safeguards in at the start, not after launch.")
''')

K.code('fine_calc', r'''
# The size of the stick: maximum fines under GDPR and India's DPDP Act
def gdpr_max(turnover_eur, serious=True):
    """Article 83: the higher of a fixed amount or a share of worldwide yearly turnover."""
    if serious:
        return max(20_000_000, 0.04 * turnover_eur)
    return max(10_000_000, 0.02 * turnover_eur)

for turnover in (50_000_000, 500_000_000, 2_000_000_000, 100_000_000_000):
    print(f"turnover EUR {turnover:>15,}: max serious fine EUR {gdpr_max(turnover):>15,.0f}")

# DPDP Act 2023 schedule, highest amounts in rupees (crore = 10 million)
CRORE = 10_000_000
dpdp = {
    "no reasonable security safeguards to prevent a breach": 250 * CRORE,
    "not telling the Board or people about a breach": 200 * CRORE,
    "breaking extra duties about children's data": 200 * CRORE,
}
print()
for breach, amount in dpdp.items():
    print(f"up to Rs {amount:>13,}  for {breach}")
print("\nThe biggest GDPR fine so far: EUR 1.2 billion against Meta (Irish DPC, May 2023), for data transfers to the US.")
''')

K.code('vendor_tier', r'''
# Third party risk: score suppliers from a questionnaire and decide how closely to watch each one
WEIGHTS = {"data_access": 0.4, "security_controls": 0.3, "past_incidents": 0.3}

vendors = {
    "Payroll SaaS": {"data_access": 90, "security_controls": 60, "past_incidents": 70},
    "Office plant supplier": {"data_access": 5, "security_controls": 40, "past_incidents": 10},
    "Cloud backup provider": {"data_access": 80, "security_controls": 85, "past_incidents": 20},
}
# each score is 0 (no risk) to 100 (high risk)

def risk_score(answers):
    total = 0
    for item, weight in WEIGHTS.items():
        total += weight * answers[item]
    return total

def tier(score):
    if score >= 60:
        return "Tier 1: yearly assessment, contract security clauses, SOC 2 Type II report"
    if score >= 30:
        return "Tier 2: questionnaire every two years"
    return "Tier 3: basic checks only"

for name, answers in sorted(vendors.items(), key=lambda v: -risk_score(v[1])):
    s = risk_score(answers)
    print(f"{name:22} risk {s:5.1f}  {tier(s)}")
''')

K.code('security_metrics', r'''
# Metrics for the board: key performance indicators (KPIs) and key risk indicators (KRIs) against thresholds
metrics = [
    # name, value, target, higher is better?
    ("MFA coverage (% of accounts)", 1840 / 2000 * 100, 99, True),
    ("Critical patches applied within 15 days (%)", 270 / 300 * 100, 95, True),
    ("Phishing test click rate (%)", 6.0, 5, False),
    ("Mean time to contain incidents (hours)", 1.4, 4, False),
    ("Backups restored successfully in tests (%)", 100.0, 100, True),
]
for name, value, target, higher in metrics:
    ok = value >= target if higher else value <= target
    print(f"{name:44} {value:6.1f}  target {'>=' if higher else '<='} {target:<4}  {'OK' if ok else 'ACTION NEEDED'}")

before, after = 18.0, 6.0
print(f"\nPhishing click rate fell from {before}% to {after}%: a {(before - after) / before * 100:.1f}% drop after training.")
''')

K.lesson('idea', 'Governance, risk and compliance: steering security', f'''
{talk('So far this course has looked at how to protect, detect and respond. Governance, risk and compliance, often called GRC, is about steering all of that. Governance means deciding who is in charge, what the rules are, how much risk the organisation is willing to take, which is called its risk appetite, and how leaders check that security is working. In most companies the board of directors is responsible in the end, and a chief information security officer, the CISO, runs the programme day to day. Risk management means finding, measuring and treating risks, which the foundations chapter on risk covered with matrices, ALE and FAIR simulations. Compliance means meeting the laws, regulations, contracts and standards that apply, and proving it to auditors, customers and regulators. GRC can sound like paperwork, but it decides where the money goes, and failures here cause real harm. After the Equifax breach of 2017, US lawmakers asked why a known patch had not been applied for months, and the answers pointed to unclear ownership. In 2023 the US Securities and Exchange Commission even charged SolarWinds and its CISO over how security risks had been described to investors, although a court later dismissed most of those claims. Good governance makes security everyone’s business, with clear owners, written rules, measured results, and regular reports to leaders in words they understand.')}
{src('ISO/IEC 27001:2022 and 27002:2022, NIST Cybersecurity Framework 2.0 (2024), CIS Controls v8, AICPA SOC 2, PCI DSS v4.0, Information Technology Act 2000 and the 2008 amendment, Digital Personal Data Protection Act 2023, CERT-In Directions (2022), RBI Cyber Security Framework (2016), GDPR (EU 2016/679), Irish DPC decision against Meta (May 2023), Budapest Convention (2001), US CFAA (1986), US House Oversight report on Equifax (2018), SEC v. SolarWinds (2023 complaint, 2024 ruling).')}
{wwh('<b>GRC</b> is how an organisation steers security: governance sets owners, rules and risk appetite, risk management decides what to fix first, and compliance proves the rules and laws are met.',
     'Without it, security spending is random, nobody owns the gaps, laws are broken without anyone noticing, and leaders cannot judge whether the organisation is safe.',
     'Leaders approve policies and risk appetite, a CISO runs a programme based on a framework, risks are registered and treated, controls are audited, and results are reported with clear metrics.')}
{viz('cypolicy')}
{table(['Role', 'Main job'], [
    ['Board of directors', 'Owns the risk in the end, sets risk appetite, asks hard questions'],
    ['CISO', 'Runs the security programme, reports to leaders and the board'],
    ['Data protection officer (DPO)', 'Watches over personal data handling, contact for regulators'],
    ['Risk and asset owners', 'Business leaders who decide on treating risks to their systems and data'],
    ['Internal audit', 'Checks independently that controls work as described']])}
''', kw=['governance', 'GRC', 'risk appetite', 'board', 'CISO', 'DPO', 'policy', 'standard', 'procedure', 'guideline', 'compliance', 'Equifax', 'SolarWinds SEC'])

K.lesson('frameworks', 'Frameworks: ISO 27001, NIST CSF 2.0, CIS Controls, SOC 2 and PCI DSS', f'''
{talk('A framework is a ready made structure so you do not have to invent security from nothing. ISO/IEC 27001 is the international standard for an information security management system, an ISMS. It asks you to set the scope, assess risks, choose controls, run them, measure them and improve, in a loop called plan, do, check, act. Its 2022 version lists 93 example controls in Annex A, grouped in four themes: 37 organisational, 8 people, 14 physical and 34 technological. Companies can be certified against ISO 27001 by an accredited auditor, which customers often ask for. The NIST Cybersecurity Framework, first published in 2014, describes security outcomes in functions. Version 2.0, from February 2024, has six: Govern, Identify, Protect, Detect, Respond and Recover, with Govern new and at the centre. Organisations write a current profile and a target profile and plan the gap. The CIS Critical Security Controls, version 8, list 18 controls with 153 practical safeguards, and Implementation Group 1, with 56 safeguards, is a good starting point for small organisations. SOC 2 is an auditor’s report, from the American Institute of CPAs, on a service company’s controls against five trust services criteria: security, availability, processing integrity, confidentiality and privacy. A Type I report checks the design at one point in time, and a Type II report checks that controls worked over a period, usually 6 to 12 months. PCI DSS, now version 4.0, is the rule book for anyone who stores, processes or sends payment card data. Many controls appear in all of these, so teams keep a crosswalk, as the program below shows.')}
{viz('cycsf')}
{run('control_crosswalk')}
{versus('Which framework for which need', ['', 'ISO/IEC 27001:2022', 'NIST CSF 2.0', 'CIS Controls v8', 'SOC 2', 'PCI DSS v4.0'], [
    ['What it is', 'Certifiable management system', 'Outcome framework and common language', 'Prioritised technical safeguards', 'Auditor’s report on a service company', 'Mandatory rules for card data'],
    ['Size', '93 Annex A controls, 4 themes', '6 functions, 22 categories', '18 controls, 153 safeguards', '5 trust services criteria', '12 requirements'],
    ['Proof', 'Certificate from an accredited body', 'Self assessment, profiles', 'Self assessment', 'Type I or Type II report', 'Assessment by a QSA or self assessment'],
    ['Best for', 'Showing customers worldwide a managed programme', 'Planning and talking to leaders', 'Knowing what to do first', 'SaaS vendors selling to companies', 'Merchants and payment firms']],
    'Use NIST CSF to plan and report, CIS Controls to decide what to do first, ISO 27001 or SOC 2 when customers need proof, and PCI DSS whenever card data is involved.')}
''', kw=['framework', 'ISO 27001', 'ISMS', 'PDCA', 'Annex A', '93 controls', 'NIST CSF 2.0', 'Govern', 'profiles', 'tiers', 'CIS Controls v8', 'implementation groups', 'SOC 2', 'Type I', 'Type II', 'trust services criteria', 'PCI DSS', 'crosswalk'])

K.lesson('audit', 'Audits, evidence and sampling', f'''
{talk('An audit checks whether controls are designed well and whether they actually work. Internal auditors work for the company but report independently. External auditors, such as ISO certification bodies, SOC 2 firms and PCI qualified security assessors, come from outside. Auditors ask for evidence: screenshots of settings, exported logs, signed approvals, training records and interview notes. Because an auditor cannot check every one of thousands of changes, user accounts or tickets, they test a random sample. The maths decides how big the sample must be. If a fraction p of items are bad and the auditor tests n items picked at random, the chance of finding at least one bad item is one minus the chance that all n are good, which is one minus (1 minus p) to the power n. With a 5 percent failure rate and a sample of 25, that is only about 72 percent, so more than a quarter of audits would wrongly come out clean. To reach 95 percent confidence, the auditor needs about 59 items, as the animation and program show. Findings are rated by severity, and each gets an owner, a fix and a due date. A finding that repeats from the last audit is treated more seriously, because it shows the fix did not work.')}
{viz('cyaudit')}
{run('audit_sample')}
{fxs(fx('Chance to catch at least one exception', 'P = 1 &minus; (1 &minus; p)<sup>n</sup>', 'p = 0.05, n = 45: P &asymp; 0.9006.', key=True),
     fx('Sample size for a confidence C', 'n = &lceil; ln(1 &minus; C) / ln(1 &minus; p) &rceil;', 'C = 0.95, p = 0.05: ln 0.05 / ln 0.95 = 58.4, so n = 59.', key=True))}
{deep('Why the formula is only approximate', '<p>Picking without putting items back changes the odds a little after each pick, which the hypergeometric distribution handles exactly. When the sample is small compared with the population, the simple formula is close enough, and it errs on the safe side. Auditing standards publish tables built on the exact maths.</p>')}
''', kw=['audit', 'internal audit', 'external audit', 'evidence', 'sampling', 'confidence', 'sample size', 'exception', 'finding', 'hypergeometric', 'QSA'])

K.lesson('law', 'Cyber law in India and around the world', f'''
{talk('Laws set the minimum that organisations must do and punish people who break into systems. In India, the Information Technology Act of 2000, strengthened in 2008, is the main cyber law. Section 43 makes a person who accesses, damages or downloads from a computer without permission liable to pay compensation, and section 66 makes doing it dishonestly or fraudulently a crime, with up to three years in prison or a fine up to five lakh rupees. Section 66C covers identity theft, such as using someone’s password or digital signature, and 66D covers cheating by pretending to be someone else using a computer, which includes many online scams. Section 66F covers cyber terrorism and can carry life imprisonment. Section 43A required companies handling sensitive personal data to keep reasonable security, and section 72A punishes disclosing personal information in breach of a contract. The Digital Personal Data Protection Act of 2023 now sets rules for personal data of people in India: get valid consent, use data only for the stated purpose, keep it safe, tell the Data Protection Board and the affected people about breaches, and respect rights such as correction and erasure. Its penalties go up to 250 crore rupees for failing to keep reasonable security safeguards. CERT-In’s 2022 directions require reporting many incidents within 6 hours and keeping logs for 180 days. Regulators add sector rules, such as RBI for banks and SEBI for market firms. Around the world, the EU’s GDPR, in force since May 2018, allows fines up to 20 million euros or 4 percent of worldwide turnover, and the largest so far is 1.2 billion euros against Meta in 2023. The US Computer Fraud and Abuse Act of 1986 covers unauthorised access, and the Budapest Convention of 2001 helps countries cooperate on cyber crime.')}
{viz('cylaw')}
{run('fine_calc')}
{table(['Law', 'Where', 'Key points'], [
    ['IT Act 2000, amended 2008', 'India', 'Sec 43 compensation, 66 hacking (3 years or 5 lakh), 66C identity theft, 66D cheating by personation, 66F cyber terrorism, 72A disclosure'],
    ['DPDP Act 2023', 'India', 'Consent and purpose, breach notice to the Board and people, penalties up to 250 crore rupees'],
    ['CERT-In Directions 2022', 'India', 'Report within 6 hours, keep logs 180 days, synchronise clocks'],
    ['GDPR (2016, applies from 2018)', 'EU and anyone handling EU residents’ data', 'Principles in article 5, privacy by design (25), 72 hour notice (33), DPIA (35), fines up to 4% (83)'],
    ['CFAA 1986', 'USA', 'Unauthorised access to protected computers'],
    ['Budapest Convention 2001', 'International treaty', 'Common definitions of cyber crimes and cooperation between countries']])}
{fxs(fx('GDPR maximum fine (serious breaches)', 'fine<sub>max</sub> = max(20000000, 0.04 &times; worldwide turnover) euros', 'Turnover 2 billion euros: max(20 million, 80 million) = 80 million.', key=True),
     fx('Return on security investment', 'ROSI = (ALE before &minus; ALE after &minus; cost) / cost', 'ALE 50 lakh to 10 lakh for a cost of 15 lakh: (40 &minus; 15) / 15 &asymp; 1.67.'))}
{note('This lesson explains the law in general terms for learning. For a real case, get advice from a qualified lawyer, because details, rules and court decisions change.', 'warn')}
''', kw=['cyber law', 'IT Act 2000', 'section 43', 'section 66', '66C', '66D', '66F', '43A', '72A', 'DPDP Act 2023', 'Data Protection Board', 'CERT-In', 'RBI', 'SEBI', 'GDPR', 'article 83', 'Meta fine', 'CFAA', 'Budapest Convention'])

K.lesson('privacy', 'Privacy, third parties and people', f'''
{talk('Privacy is not the same as security. Security keeps data safe from people who should not have it. Privacy is about whether the organisation should collect and use the data at all, and whether it is fair to the person it belongs to. GDPR article 5 lists the principles: lawful, fair and transparent use, purpose limitation, data minimisation, accuracy, storage limitation, integrity and confidentiality, and accountability. India’s DPDP Act follows similar ideas. Privacy by design, a term from Ann Cavoukian, a privacy commissioner in Canada, means building these protections in from the start. For risky new projects, such as face recognition or tracking large numbers of people, a data protection impact assessment, DPIA, is done before launch, as the program below screens for. Next, third parties. Most organisations depend on hundreds of suppliers, and many breaches start there. The 2013 Target breach began with stolen credentials from a heating and air conditioning contractor. Third party risk management means tiering suppliers by how much data and access they have, asking for evidence such as SOC 2 reports or ISO certificates, writing security duties into contracts, and reviewing the riskiest ones every year. Last, people. Security awareness training, phishing simulations and a culture where staff report mistakes quickly are controls too, and they can be measured, as the metrics program shows.')}
{run('dpia_check')}
{run('vendor_tier')}
{run('security_metrics')}
{fxs(fx('Weighted vendor risk', 'R = &Sigma; w<sub>i</sub> s<sub>i</sub>, with &Sigma; w<sub>i</sub> = 1', 'Weights 0.4, 0.3, 0.3 and scores 80, 50, 70: 32 + 15 + 21 = 68, so tier 1.', key=True),
     fx('Relative change', 'change = (before &minus; after) / before', 'Click rate 18% to 6%: 12 / 18 &asymp; 66.7% lower.'))}
{table(['GDPR article 5 principle', 'In plain words'], [
    ['Lawfulness, fairness, transparency', 'Have a legal reason, be fair, tell people what you do'],
    ['Purpose limitation', 'Use data only for the reason you collected it'],
    ['Data minimisation', 'Collect only what you need'],
    ['Accuracy', 'Keep it correct and up to date'],
    ['Storage limitation', 'Delete it when you no longer need it'],
    ['Integrity and confidentiality', 'Keep it secure'],
    ['Accountability', 'Be able to prove you follow all of the above']])}
''', kw=['privacy', 'privacy by design', 'Ann Cavoukian', 'GDPR article 5', 'data minimisation', 'purpose limitation', 'DPIA', 'third party risk', 'vendor tiering', 'SOC 2 report', 'Target HVAC', 'security awareness', 'phishing simulation', 'KPI', 'KRI', 'metrics'])

K.lesson('versus', 'Compliance and security compared', f'''
{talk('Being compliant and being secure are related but not the same. Compliance proves you meet a written set of rules at the time of the audit. Security is the real ability to resist and recover from attacks every day. Target was certified as PCI compliant shortly before its 2013 breach. A good programme uses compliance as a floor and a source of discipline, and keeps going beyond it.')}
{versus('Compliant versus secure', ['', 'Compliance focus', 'Security focus'], [
    ['Question', 'Do we meet the rules and can we prove it?', 'Can we stop, detect and recover from real attacks?'],
    ['Timing', 'Point in time or audit period', 'Every day'],
    ['Measured by', 'Audit findings, certificates', 'Incidents, time to detect and contain, attack simulations'],
    ['Risk', 'Box ticking that misses new threats', 'Spending without proof for customers and regulators'],
    ['Best use', 'Floor of good practice, discipline, trust with customers', 'Reducing real risk beyond the floor']],
    'Aim to be secure, and let compliance be the evidence. Map controls once to many frameworks, so the same work satisfies every audit.')}
''', kw=['compliance versus security', 'box ticking', 'Target PCI', 'continuous compliance'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that organisations have security rules, that laws protect personal data, and that breaking into computers is a crime. A student can compare frameworks, compute sample sizes and fines, and explain the main Indian and EU laws. A professional runs an ISMS, audits, vendor programmes and board reporting. Experts shape policy and law, lead large compliance programmes and research how to measure security well.')}
{ladder(
    '<p>Schools and companies write rules about using computers safely, and the law punishes people who break into computers or misuse other people’s data.</p>',
    '<p>Policy, standard, procedure, guideline. ISO 27001 Annex A themes, NIST CSF 2.0 functions, CIS IGs, SOC 2 types, PCI DSS. Audit sampling maths, GDPR and DPDP fines, IT Act sections.</p>',
    '<p>Run an ISMS to certification, lead SOC 2 and PCI audits, manage third party risk, write DPIAs, report KPIs and KRIs to the board, and earn CISSP, CISM or CISA.</p>',
    '<p>Cyber risk quantification for boards and insurers, measuring control effectiveness with data, regulation design and its economics, and international law on state cyber operations (the Tallinn Manual).</p>')}
{grow('Explain why organisations write security rules and why laws protect data.',
      'Compare frameworks, size audit samples and work out fines.',
      'Run governance, compliance and reporting for a whole organisation.')}
''', kw=['beginner', 'expert', 'CISSP', 'CISM', 'CISA', 'Tallinn Manual'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>GRC</b>: governance (owners, rules, risk appetite), risk management, compliance with proof. Board, CISO, DPO. Policy, standard, procedure, guideline.',
    '<b>Frameworks</b>: ISO 27001:2022 (93 controls, 4 themes, PDCA, certifiable), NIST CSF 2.0 (Govern, Identify, Protect, Detect, Respond, Recover), CIS v8 (18 controls, IG1 56), SOC 2 Type I and II, PCI DSS v4.0.',
    '<b>Audit</b>: evidence and sampling. P(catch) = 1 &minus; (1 &minus; p)<sup>n</sup>, n = &lceil;ln(1 &minus; C) / ln(1 &minus; p)&rceil;. Owners and due dates for findings.',
    '<b>Law</b>: IT Act 43, 43A, 66, 66C, 66D, 66F, 72A. DPDP Act 2023 (up to 250 crore). CERT-In 6 hours, 180 days logs. GDPR up to 4% (Meta 1.2 billion euros). CFAA, Budapest Convention.',
    '<b>Privacy and people</b>: article 5 principles, privacy by design, DPIA. Vendor tiering with weighted scores and SOC 2 reports. Awareness and metrics, KPIs and KRIs.'],
    'Advanced 1.1: machine learning for security, teaching computers to spot attacks.')}
{files('Three tasks: GDPR maximum fine, audit sample size, and a weighted vendor risk score.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which document says why and what, and is approved by leaders?', ['Procedure', 'Policy', 'Guideline', 'Ticket'], 1, 'Top layer.', 'Standards and procedures sit below it.')
K.quiz('e', 'How many functions does NIST CSF 2.0 have?', ['4', '5', '6', '8'], 2, 'Govern was added.', 'Govern, Identify, Protect, Detect, Respond, Recover.')
K.quiz('e', 'Which Indian law is the main cyber crime law?', ['Companies Act', 'Information Technology Act 2000', 'Motor Vehicles Act', 'Income Tax Act'], 1, 'IT Act.', 'Amended in 2008 to add sections such as 66C and 66F.')
K.quiz('e', 'What is a guideline?', ['A mandatory rule', 'Helpful advice that is not compulsory', 'A law', 'An audit finding'], 1, 'Optional.', 'Policies, standards and procedures are mandatory.')
K.quiz('m', 'How many controls are in ISO/IEC 27001:2022 Annex A?', ['114', '93', '18', '153'], 1, '2022 version.', 'The 2013 version had 114. CIS v8 has 18 controls and 153 safeguards.')
K.quiz('m', 'What is the difference between a SOC 2 Type I and Type II report?', ['Type II is cheaper', 'Type I checks design at one point, Type II checks controls worked over a period', 'Type I is for banks', 'No difference'], 1, 'Point versus period.', 'Customers usually ask for Type II.')
K.quiz('m', 'Which IT Act section covers identity theft such as using someone’s password?', ['43', '66C', '66F', '72A'], 1, 'C for credentials.', '66D covers cheating by personation, 66F cyber terrorism.')
K.quiz('m', 'Under GDPR, how soon must a personal data breach usually be reported to the authority?', ['24 hours', '72 hours', '30 days', 'Never'], 1, 'Article 33.', 'People are told too when the risk to them is high (article 34).')
K.quiz('m', 'Why can being compliant still leave you insecure?', ['Audits are illegal', 'Compliance checks rules at a point in time and can miss new threats', 'Compliance means no controls', 'Frameworks forbid security'], 1, 'Floor, not ceiling.', 'Target was PCI compliant shortly before its 2013 breach.')
K.quiz('h', 'An auditor tests 25 random items from a population where 5% are bad. About how likely is the sample to find none?', ['5%', 'About 28%', '72%', '0%'], 1, '0.95<sup>25</sup>.', '0.95<sup>25</sup> &asymp; 0.277, so more than a quarter of audits miss it.')
K.quiz('h', 'A company has worldwide turnover of 100 million euros. What is the maximum GDPR fine for a serious breach?', ['4 million euros', '20 million euros', '100 million euros', '1 million euros'], 1, 'The higher of the two.', '4% is 4 million, so the 20 million floor applies.')
K.quiz('h', 'Which of these was new in NIST CSF 2.0?', ['Detect', 'Govern', 'Recover', 'Identify'], 1, 'At the centre.', 'It moved governance outcomes out of Identify into their own function.')
K.quiz('h', 'The 2013 Target breach began with', ['A cloud bucket', 'Stolen credentials of a heating and air conditioning contractor', 'A quantum attack', 'A lost laptop'], 1, 'Third party.', 'Supplier access is a classic way in, hence third party risk management.')
K.quiz('x', 'In the style of a CMU information security policy exam: what sample size gives 99% confidence of catching a 2% failure rate?', ['50', '228', '99', '1000'], 1, 'ln 0.01 / ln 0.98.', '= 227.9, round up to 228.')
K.quiz('x', 'In the style of a London School of Economics law and technology question: which treaty, opened for signature in 2001, sets common definitions of cyber crimes?', ['Wassenaar Arrangement', 'Budapest Convention', 'Geneva Convention', 'Paris Agreement'], 1, 'Council of Europe.', 'India has not joined it, but many countries use its definitions.')

K.calc('e', 'How many Annex A controls are in ISO/IEC 27001:2022?', '93', 'Add the four themes.', ['Organisational 37, people 8.', 'Physical 14, technological 34.', eq('37 + 8 + 14 + 34 = 93')], check=93)
K.calc('e', 'Turnover 2 billion euros. Maximum GDPR fine for a serious breach, in euros?', '80000000', 'Higher of 20 million or 4%.', ['4% of 2000000000 = 80000000.', 'Compare with 20000000.', eq('80000000')], check=80000000)
K.calc('e', '1840 of 2000 accounts have MFA. Coverage in percent?', '92', 'Part over whole.', ['1840 / 2000 = 0.92.', 'Times 100.', eq('92%')], check=92)
K.calc('m', 'Turnover 100 million euros. Maximum GDPR fine for a serious breach?', '20000000', 'The floor applies.', ['4% = 4000000.', 'max(20000000, 4000000).', eq('20000000')], check=20000000)
K.calc('m', 'Failure rate 5%, sample of 45. Chance to catch at least one? Round to 4 decimals.', '0.9006', '1 &minus; 0.95<sup>45</sup>.', ['0.95<sup>45</sup> &asymp; 0.0994.', 'Complement.', eq('&asymp; 0.9006')], check=round(1 - 0.95 ** 45, 4))
K.calc('m', 'Sample size for 95% confidence at a 5% failure rate?', '59', 'Round up.', ['ln 0.05 = &minus;2.9957, ln 0.95 = &minus;0.0513.', 'Ratio = 58.4.', eq('n = 59')], check=59)
K.calc('m', 'Click rate fell from 18% to 6%. Relative drop in percent? Round to 2 decimals.', '66.67', '(before &minus; after) / before.', ['18 &minus; 6 = 12.', '12 / 18 = 0.6667.', eq('66.67%')], check=round(12 / 18 * 100, 2))
K.calc('m', '270 of 300 critical patches were applied within 15 days. Percent?', '90', 'Divide.', ['270 / 300 = 0.9.', 'Times 100.', eq('90%')], check=90)
K.calc('h', 'CIS Controls v8: 56 of 153 safeguards are in IG1. Percent? Round to 1 decimal.', '36.6', 'Divide.', ['56 / 153 = 0.366.', 'Times 100.', eq('36.6%')], check=round(56 / 153 * 100, 1))
K.calc('h', 'The DPDP Act maximum of 250 crore rupees. Write it in rupees (1 crore = 10000000).', '2500000000', 'Multiply.', ['250 &times; 10000000.', 'That is 2.5 billion.', eq('2500000000')], check=2500000000)
K.calc('h', 'Vendor weights 0.4, 0.3, 0.3 and risk scores 80, 50, 70. Weighted score?', '68', 'Multiply and add.', ['0.4 &times; 80 = 32.', '0.3 &times; 50 = 15, 0.3 &times; 70 = 21.', eq('32 + 15 + 21 = 68')], check=68)
K.calc('x', 'Sample size for 99% confidence at a 2% failure rate?', '228', 'Round up.', ['ln 0.01 = &minus;4.6052, ln 0.98 = &minus;0.0202.', 'Ratio = 227.9.', eq('n = 228')], check=228)
K.calc('x', 'ALE falls from 50 lakh to 10 lakh rupees for a control costing 15 lakh. ROSI? Round to 4 decimals.', '1.6667', '(saving &minus; cost) / cost.', ['Saving = 40 lakh.', '(40 &minus; 15) / 15.', eq('&asymp; 1.6667, a 167% return')], check=round(25 / 15, 4))
K.calc('x', 'Population 200 with 10 bad items. Chance a sample of 25, with replacement, finds none? Round to 4 decimals.', '0.2774', '0.95<sup>25</sup>.', ['Each pick is good with 190 / 200 = 0.95.', '25 independent picks.', eq('0.95<sup>25</sup> &asymp; 0.2774')], check=round(0.95 ** 25, 4))

K.assign('gdpr_fine', 'e', 'GDPR maximum fine',
         '<p>Write <code>gdpr_fine(turnover)</code> that returns the maximum fine for a serious breach: the higher of 20000000 or 4% of turnover, as a float rounded to 2 decimals.</p>',
         '''
def gdpr_fine(turnover):
    # your code here
    pass
''', [('gdpr_fine(2000000000)', 80000000.0), ('gdpr_fine(100000000)', 20000000.0), ('gdpr_fine(0)', 20000000.0), ('gdpr_fine(600000000)', 24000000.0)],
         '''
def gdpr_fine(turnover):
    return round(float(max(20000000, 0.04 * turnover)), 2)
''', 'max of the fixed amount and the percentage.', '<p>Actual fines are set by regulators case by case, looking at the harm, intent, cooperation and past record. This is only the ceiling.</p>')
K.assign('audit_size', 'm', 'Audit sample size',
         '<p>Write <code>audit_size(error_rate, confidence)</code> that returns the smallest whole n with 1 &minus; (1 &minus; error_rate)<sup>n</sup> &ge; confidence, using <code>math.ceil(math.log(1 - confidence) / math.log(1 - error_rate))</code> or a loop.</p>',
         '''
import math

def audit_size(error_rate, confidence):
    # your code here
    pass
''', [('audit_size(0.05, 0.95)', 59), ('audit_size(0.02, 0.99)', 228), ('audit_size(0.1, 0.9)', 22), ('audit_size(0.5, 0.75)', 2)],
         '''
import math

def audit_size(error_rate, confidence):
    n = 0
    chance = 0.0
    while chance < confidence:
        n += 1
        chance = 1 - (1 - error_rate) ** n
    return n
''', 'Increase n one at a time until the chance to catch reaches the confidence.', '<p>The loop and the logarithm give the same answer. The loop is easier to read, the formula is faster for tiny error rates.</p>')
K.assign('vendor_score', 'h', 'Weighted vendor risk score',
         '<p>weights and scores are dictionaries with the same keys. Write <code>vendor_score(weights, scores)</code> that returns the weighted sum rounded to 1 decimal, and raises <code>ValueError</code> if the weights do not add up to 1 (allow a difference of 1e-9).</p>',
         '''
def vendor_score(weights, scores):
    # your code here
    pass
''', [('vendor_score({"a": 0.4, "b": 0.3, "c": 0.3}, {"a": 80, "b": 50, "c": 70})', 68.0),
      ('vendor_score({"a": 0.5, "b": 0.5}, {"a": 10, "b": 20})', 15.0),
      ('vendor_score({"a": 1.0}, {"a": 33})', 33.0)],
         '''
def vendor_score(weights, scores):
    if abs(sum(weights.values()) - 1) > 1e-9:
        raise ValueError("weights must add up to 1")
    total = 0
    for key, weight in weights.items():
        total += weight * scores[key]
    return round(total, 1)
''', 'Check the weights first, then add weight times score for each key.', '<p>Weighted scores are simple and easy to explain to a board, but the weights are opinions, so write down why you chose them.</p>')

K.must('GRC', 'Governance (owners, rules, risk appetite), risk management, compliance with proof. Board accountable, CISO runs it, DPO for personal data. Policy, standard, procedure (mandatory), guideline (optional).')
K.must('Frameworks', 'ISO 27001:2022: ISMS, PDCA, 93 Annex A controls (37 org, 8 people, 14 physical, 34 tech), certifiable. NIST CSF 2.0 (Feb 2024): GV, ID, PR, DE, RS, RC, profiles, tiers 1 to 4. CIS v8: 18 controls, 153 safeguards, IG1 56. SOC 2 Type I and II. PCI DSS v4.0.')
K.must('Audit', 'Evidence and sampling. P(catch) = 1 &minus; (1 &minus; p)<sup>n</sup>. n = &lceil;ln(1 &minus; C) / ln(1 &minus; p)&rceil;: 59 for 95% at 5%, 228 for 99% at 2%.')
K.must('India', 'IT Act 2000 (2008): 43 compensation, 43A reasonable security, 66 (3 years or 5 lakh), 66C identity theft, 66D personation, 66F terrorism, 72A disclosure. DPDP 2023 up to 250 crore. CERT-In 6 hours, 180 days.')
K.must('World', 'GDPR (2018): art. 5 principles, 25 privacy by design, 33 72 hours, 35 DPIA, 83 fines up to max(20 million euros, 4% turnover), Meta 1.2 billion (2023). CFAA 1986, Budapest Convention 2001.')
K.must('Privacy and suppliers', 'Privacy by design (Cavoukian), DPIA for high risk. Vendor tiers from R = &Sigma; w<sub>i</sub>s<sub>i</sub>, SOC 2 reports, contract clauses (Target 2013 HVAC). KPIs and KRIs. Compliance is the floor.')

T = K.topic(
    slug='cy-grc', topic='cy-grc', step=(2, 'Intelligence, cloud and governance', 'cy-o2', 'Learning about attackers before they arrive, securing the cloud, and the rules, risk methods and laws that guide security work.', 'Advanced'),
    title='Governance, risk, compliance and cyber law', short='Governance and law', badge='2.3', minutes=75,
    lead='How security is steered and proven: roles and the policy hierarchy, ISO 27001, NIST CSF 2.0, CIS Controls, SOC 2 and PCI DSS, audits with the maths of sampling, Indian cyber law (IT Act, DPDP Act, CERT-In) next to GDPR and other laws, privacy by design, third party risk and security metrics.',
    desc='governance, GRC, risk appetite, CISO, DPO, policy, standard, procedure, guideline, ISO 27001, ISMS, Annex A, NIST CSF 2.0, Govern, CIS Controls v8, SOC 2, Type II, PCI DSS, crosswalk, audit, sampling, sample size, IT Act 2000, section 66, 66C, 66D, 66F, 43A, 72A, DPDP Act 2023, CERT-In, RBI, GDPR, article 33, article 83, fines, Meta, CFAA, Budapest Convention, privacy by design, DPIA, third party risk, vendor tiering, KPI, KRI, ROSI',
    summary='Roles and policies, ISO 27001, NIST CSF 2.0, CIS, SOC 2, PCI DSS, audit sampling, Indian and world cyber law, privacy and third parties.',
    keywords=['governance', 'ISO 27001', 'NIST CSF', 'CIS Controls', 'SOC 2', 'PCI DSS', 'audit sampling', 'IT Act', 'DPDP Act', 'GDPR', 'DPIA'],
    recap='<p>Name owners, write rules in layers, pick a framework, prove controls with honest samples, know the laws that apply, and report results leaders can act on.</p>',
    added='2026-11-15')
