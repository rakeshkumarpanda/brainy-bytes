# Foundations 1.2: risk in numbers. Checked against NIST SP 800-30 Rev. 1 (Guide for Conducting Risk Assessments,
# 2012), NIST SP 800-37 Rev. 2 (Risk Management Framework, 2018, seven steps), ISO/IEC 27005:2022, the CompTIA
# Security+ SY0-701 objectives (control categories and types, SLE, ARO, ALE, RTO, RPO, MTTR, MTBF), the Open Group
# FAIR standard (O-RA), Bruce Schneier, "Attack Trees", Dr. Dobb's Journal (December 1999), and Microsoft's STRIDE
# (Kohnfelder and Garg, 1999).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk

chapter('cy-risk')
K = Kit()

K.code('ale', r'''
# Quantitative risk: how much money a risk is expected to cost each year
asset_value = 2000000        # AV: value of the customer database in rupees
exposure_factor = 0.4        # EF: share of the value lost in one incident (40%)
aro = 0.5                    # ARO: incidents expected per year (once every 2 years)

sle = asset_value * exposure_factor      # single loss expectancy: cost of ONE incident
ale = sle * aro                          # annualised loss expectancy: cost per YEAR
print("SLE (one incident):", sle)
print("ALE (per year):    ", ale)

# A control cuts the ARO to 0.1 and costs 60,000 rupees a year. Is it worth it?
ale_after = sle * 0.1
control_cost = 60000
value = ale - ale_after - control_cost
print("ALE after the control:", ale_after)
print("value of the control per year:", value)
if value > 0:
    print("worth buying")
else:
    print("costs more than it saves")
''')

K.code('register', r'''
# A small risk register: each risk gets likelihood and impact from 1 to 5
risks = [
    ["phishing", 4, 3],
    ["laptop theft", 3, 2],
    ["ransomware", 2, 5],
    ["website down", 3, 3],
    ["flood in server room", 1, 4],
]

def zone(score):
    if score >= 16:
        return "critical"
    if score >= 10:
        return "high"
    if score >= 5:
        return "medium"
    return "low"

for r in risks:
    r.append(r[1] * r[2])          # score = likelihood x impact

risks.sort(key=lambda r: r[3], reverse=True)
appetite = 8
for name, likelihood, impact, score in risks:
    action = "treat" if score > appetite else "accept and watch"
    print(name, "| score", score, "|", zone(score), "|", action)
''')

K.code('attack_tree', r'''
# An attack tree: a leaf is a cost. A node is ("AND", children) or ("OR", children).
tree = ("OR", [
    ("AND", [1, 5]),        # take over an admin: phishing email AND beat MFA
    3,                      # SQL injection
    20,                     # bribe an insider
    ("AND", [4, 50]),       # steal a backup AND crack its encryption
])

def cheapest(node):
    if not isinstance(node, tuple):    # a leaf: its cost
        return node
    kind, children = node
    costs = []
    for child in children:
        costs.append(cheapest(child))
    if kind == "AND":
        return sum(costs)              # every step must be paid for
    return min(costs)                  # OR: the attacker picks the cheapest route

print("cheapest attack costs:", cheapest(tree), "thousand")

# The same tree with chances of success instead of costs
chance_tree = ("OR", [("AND", [0.3, 0.2]), 0.1, 0.5, ("AND", [0.2, 0.01])])

def success(node):
    if not isinstance(node, tuple):
        return node
    kind, children = node
    if kind == "AND":
        p = 1
        for child in children:
            p = p * success(child)
        return p
    fail = 1
    for child in children:
        fail = fail * (1 - success(child))
    return 1 - fail

print("chance the goal is reached:", round(success(chance_tree), 4))
''')

K.code('monte_carlo', r'''
import random

# FAIR style: simulate many years. Each month a breach happens with a small chance,
# and each breach costs a random amount between a low and a high estimate.
random.seed(1)
chance_per_month = 0.04
low, high = 200000, 1500000

years = []
for y in range(5000):
    loss = 0
    for month in range(12):
        if random.random() < chance_per_month:
            loss = loss + random.uniform(low, high)
    years.append(loss)

years.sort()
average = sum(years) / len(years)
print("average loss per year:", round(average))
print("years with no breach:", sum(1 for v in years if v == 0), "of", len(years))
print("1 year in 10 is worse than:", round(years[int(0.9 * len(years))]))
print("1 year in 100 is worse than:", round(years[int(0.99 * len(years))]))
''', long=True)

K.code('nines', r'''
# Availability and downtime: how many minutes per year can a service be down?
minutes_per_year = 365 * 24 * 60

for availability in [0.99, 0.999, 0.9999, 0.99999]:
    down = (1 - availability) * minutes_per_year
    print(str(availability * 100) + "% up ->", round(down, 1), "minutes down per year")

# Availability from failures: MTBF = mean time between failures, MTTR = mean time to repair
mtbf = 1000   # hours
mttr = 2      # hours
print("availability =", round(mtbf / (mtbf + mttr), 5))
''')

K.lesson('idea', 'What risk is and why we measure it', f'''
{talk('Every day you manage risk without thinking about it. You lock your bicycle, you carry an umbrella when the sky is grey, and you do not keep all your money in one pocket. You are weighing two questions: how likely is something bad, and how bad would it be? Companies must answer the same two questions, but they have thousands of assets and limited money. They cannot protect everything perfectly, so they must choose. Risk management is the method for choosing well. It grew out of insurance, where people have priced risk for hundreds of years, and it was brought into computing by standards bodies such as NIST in the United States and ISO internationally. In this chapter you will learn to put a number on risk, both with simple scores and with money, and to decide what to do about each risk.')}
{src('NIST SP 800-30 Rev. 1, NIST SP 800-37 Rev. 2, ISO/IEC 27005:2022, the CompTIA Security+ SY0-701 objectives and the Open Group FAIR standard.')}
{wwh('<b>Risk</b> is the chance that a threat uses a vulnerability to harm an asset, combined with how much harm it would do. In one line: <b>risk = likelihood &times; impact</b>.',
     'Money, people and time are limited. Without measuring risk, teams fix whatever is loudest, not what is most dangerous. Measuring risk lets you compare very different problems (a flood, a phishing attack, a lost laptop) on one scale and spend where it matters most.',
     'List the assets, the threats and the weaknesses. Score each risk for likelihood and impact, with words (low to critical) or with money (expected loss per year). Sort the list, compare with the risk the business is willing to accept, and pick a response for each risk above that line.')}
{scene('the school server room', '<p>A school keeps its marks server in a small room. The head teacher worries about three things: a hacker, a flood and a stolen laptop. Floods are rare here (once in 20 years) but would destroy the server. Laptops are stolen about once a year but hold only a few files. Phishing emails arrive every week, and one success could leak every student’s data. Ranking these by likelihood and impact shows that phishing training and backups matter far more than a waterproof door, even though the flood sounds scarier.</p>')}
{fxs(fx('Risk', 'risk = likelihood &times; impact', 'Likelihood: how often. Impact: how bad one event is. Both can be scores (1 to 5) or numbers (events per year, rupees).', key=True),
     fx('Inherent and residual risk', 'residual risk = inherent risk &minus; what the controls remove', 'Inherent risk is the risk before any control. Residual risk is what is left after controls. Some residual risk always stays.'))}
{note('Risk is never zero. The goal is to bring it down to a level the business accepts, called the <b>risk appetite</b>, at a sensible cost.', 'tip')}
''', kw=['risk', 'likelihood', 'impact', 'risk management', 'inherent risk', 'residual risk', 'risk appetite'])

K.lesson('matrix', 'Qualitative risk: the risk matrix', f'''
{talk('The quickest way to talk about risk is with simple words and a coloured chart. You ask a group of people who know the system: how likely is this, from very rare to almost certain? And how bad would it be, from small to disastrous? You turn each answer into a number from one to five and multiply. This is called qualitative risk assessment, because it uses judgement rather than exact money. It is fast and everyone understands the colours. Its weakness is that the numbers are opinions, and a score of twelve is not truly twice as bad as a score of six. Still, almost every company starts here, and the risk matrix you are about to build is the picture you will see in board meetings all over the world.')}
<p>Press <b>Step</b> to place each risk on the matrix. Change the likelihoods, impacts and the appetite, then play it again.</p>
{viz('cyrisk')}
{run('register')}
{table(['Score', 'Likelihood words', 'Impact words'], [
    ['1', 'Rare: may happen once in many years', 'Negligible: a small delay, no data lost'],
    ['2', 'Unlikely: could happen in a few years', 'Minor: a little data or a few hours lost'],
    ['3', 'Possible: about once a year', 'Moderate: a day of downtime, some customers affected'],
    ['4', 'Likely: several times a year', 'Major: large data leak, big fines, news stories'],
    ['5', 'Almost certain: monthly or more', 'Severe: the business may not survive, or lives are at risk']])}
{note('Matrix scores are labels, not real measurements. Do not add or average them across risks, and do not say a 12 is exactly twice a 6. Use them to sort and to start a conversation.', 'warn')}
''', kw=['qualitative risk', 'risk matrix', 'heat map', 'risk register', 'likelihood score', 'impact score', 'appetite'])

K.lesson('ale', 'Quantitative risk: SLE, ARO and ALE', f'''
{talk('Managers and finance teams like money more than colours. Quantitative risk assessment turns each risk into rupees or dollars per year. The idea comes straight from insurance. If something worth ten lakh rupees loses forty percent of its value each time it is hit, one hit costs four lakh. If that happens once every two years, then on average it costs two lakh per year. This yearly number is called the annualised loss expectancy, or ALE. Once every risk has an ALE, you can compare it directly with the price of a control. If a firewall costs one lakh a year and cuts the expected loss by three lakh a year, it pays for itself. These short names, SLE, ARO and ALE, are asked in almost every security certification exam, so learn them well.')}
{wwh('<b>Quantitative risk assessment</b> gives each risk a money value per year, so it can be compared with the cost of controls.',
     'A board must decide between buying a backup system, more training or cyber insurance. Money makes these choices comparable and easy to explain.',
     'Find the asset value (AV) and the share lost in one incident, the exposure factor (EF). Their product is the single loss expectancy (SLE). Multiply by the number of incidents expected per year, the annualised rate of occurrence (ARO), to get the annualised loss expectancy (ALE).')}
{fxs(fx('Single loss expectancy', 'SLE = AV &times; EF', 'AV is the asset value in money. EF is the fraction of that value lost in one incident, from 0 to 1.', key=True),
     fx('Annualised loss expectancy', 'ALE = SLE &times; ARO', 'ARO is how many incidents are expected per year. Once in 4 years is 0.25.', key=True),
     fx('Value of a control (safeguard)', 'value = ALE<sub>before</sub> &minus; ALE<sub>after</sub> &minus; annual cost of the control', 'Positive means the control saves more than it costs.', key=True))}
{run('ale')}
{steps('Worked example: should a shop buy a backup service?', [
    'The online shop’s order database is worth AV = 10,00,000 rupees. Ransomware would destroy 60% of its value, so EF = 0.6.',
    eq('SLE = 10,00,000 &times; 0.6 = 6,00,000 rupees'),
    'Ransomware is expected once every 5 years, so ARO = 0.2.',
    eq('ALE = 6,00,000 &times; 0.2 = 1,20,000 rupees per year'),
    'A backup service costs 30,000 a year and cuts EF to 0.05 (only a few hours of orders are lost). New SLE = 50,000, new ALE = 10,000.',
    eq('value = 1,20,000 &minus; 10,000 &minus; 30,000 = 80,000 rupees per year'),
    'The value is positive, so the backup service is worth buying.'])}
{note('ARO is a rate per year, not a probability. An event expected twice a year has ARO = 2. For rare events the ARO and the yearly probability are close, but they are not the same thing.', 'exam')}
''', kw=['quantitative risk', 'SLE', 'ALE', 'ARO', 'AV', 'EF', 'asset value', 'exposure factor', 'single loss expectancy', 'annualised loss expectancy', 'cost benefit', 'safeguard value'])

K.lesson('respond', 'What to do with a risk: four responses and control types', f'''
{talk('Once you know a risk is too high, you have only four choices, and they apply to life in general. Suppose you are worried about losing your phone. You could stop carrying a phone, which avoids the risk. You could buy a strong case and turn on tracking, which reduces it. You could buy phone insurance, which transfers the money loss to someone else. Or you could decide the phone is cheap and simply accept the risk. Companies do exactly the same with cyber risk. Then, to reduce a risk, they use controls, and security people sort controls in two ways: by what kind of thing they are, and by what job they do. Exams ask about both, so we will build a table you can memorise.')}
{table(['Response', 'Plain meaning', 'Example'], [
    ['Avoid', 'Stop doing the risky thing', 'Do not store card numbers at all, let a payment company handle them'],
    ['Reduce (mitigate)', 'Add controls to lower likelihood or impact', 'Patching, MFA, backups, training'],
    ['Transfer (share)', 'Move the money loss to someone else', 'Cyber insurance, a contract that makes a supplier pay for its mistakes'],
    ['Accept', 'Live with it, with a written sign off by someone senior', 'An old internal printer with a known bug, behind a firewall, worth little']])}
{table(['Control category (what it is)', 'Examples'], [
    ['Technical (logical)', 'Firewalls, encryption, MFA, antivirus, access control lists'],
    ['Managerial (administrative)', 'Policies, risk assessments, security awareness programmes, hiring checks'],
    ['Operational', 'Guards checking IDs, backup procedures, patch routines, done by people'],
    ['Physical', 'Locks, fences, CCTV, badge readers, fire suppression']])}
{table(['Control type (what job it does)', 'Job', 'Examples'], [
    ['Preventive', 'Stops the attack from happening', 'Firewall rule, MFA, door lock'],
    ['Deterrent', 'Makes the attacker not want to try', 'Warning banner, visible cameras, legal notices'],
    ['Detective', 'Spots an attack that is happening or happened', 'Intrusion detection, log review, CCTV recording'],
    ['Corrective', 'Fixes the damage and restores normal', 'Restoring from backup, patching after an incident'],
    ['Compensating', 'A replacement when the normal control is not possible', 'Extra monitoring on an old machine that cannot be patched'],
    ['Directive', 'Tells people what to do', 'Policy saying "lock your screen", signs, procedures']])}
{note('One control can belong to a category and a type at once. A CCTV camera is a physical control that is both deterrent (people see it) and detective (it records).', 'exam')}
{note('Accepting a risk is a real decision only when an owner with authority signs it, with a date to review. Ignoring a risk is not accepting it.', 'warn')}
''', kw=['risk response', 'avoid', 'mitigate', 'transfer', 'accept', 'cyber insurance', 'control categories', 'technical', 'managerial', 'operational', 'physical', 'preventive', 'detective', 'corrective', 'deterrent', 'compensating', 'directive'])

K.lesson('threat', 'Threat modelling: STRIDE and attack trees', f'''
{talk('Before a building is built, an architect thinks about fire exits, earthquakes and burglars. Threat modelling is the same habit for software and systems: you think like an attacker before the attacker does. In 1999 two Microsoft engineers, Loren Kohnfelder and Praerit Garg, gave the world a simple checklist called STRIDE, six kinds of threats, one for each letter. The same year, the cryptographer Bruce Schneier described attack trees. You write the attacker’s goal at the top, and below it all the ways to reach it. Some ways need several steps together, and some are alternatives. Then you put a cost or a chance on each leaf and work upwards, like adding up a family tree. The cheapest route tells you where to put your money first.')}
{table(['STRIDE threat', 'It breaks', 'Example', 'Control'], [
    ['Spoofing', 'Authenticity', 'Logging in with someone else’s stolen password', 'MFA, strong authentication'],
    ['Tampering', 'Integrity', 'Changing a price in a web request', 'Signatures, server side checks, hashes'],
    ['Repudiation', 'Non repudiation', 'A user says "I never sent that order"', 'Signed records, secure logs'],
    ['Information disclosure', 'Confidentiality', 'An error page shows the database password', 'Encryption, least privilege, safe error messages'],
    ['Denial of service', 'Availability', 'Flooding the login page', 'Rate limits, DDoS filtering, capacity'],
    ['Elevation of privilege', 'Authorisation', 'A normal user gets admin rights through a bug', 'Least privilege, patching, input checks']])}
<p>Press <b>Step</b> to evaluate the attack tree from the leaves up. Switch between cost and chance, and try fixing a leaf.</p>
{viz('cyattacktree')}
{run('attack_tree')}
{fxs(fx('Attack tree with costs', 'AND node: cost = sum of children &nbsp;&nbsp; OR node: cost = smallest child', 'The attacker pays for every step of an AND route, and picks the cheapest OR route.', key=True),
     fx('Attack tree with chances', 'AND node: p = p<sub>1</sub> &times; p<sub>2</sub> &times; ... &nbsp;&nbsp; OR node: p = 1 &minus; (1 &minus; p<sub>1</sub>)(1 &minus; p<sub>2</sub>)...', 'Assumes the steps are independent and that the attacker tries every OR route.'))}
{note('Fix the cheapest route first. Making an expensive route even more expensive does nothing while a cheap route is still open.', 'tip')}
''', kw=['threat modelling', 'STRIDE', 'spoofing', 'tampering', 'repudiation', 'information disclosure', 'denial of service', 'elevation of privilege', 'attack tree', 'Schneier', 'AND OR node'])

K.lesson('simulate', 'Better numbers: FAIR and Monte Carlo simulation', f'''
{talk('A single ALE number hides something important. A risk that costs one lakh every year and a risk that costs nothing for ninety nine years and then ten crore once can have the same average, but they are very different for a business. Real losses are uncertain, so modern risk analysts use ranges instead of single numbers. The FAIR method, which stands for Factor Analysis of Information Risk, was created by Jack Jones in the early 2000s and is now an Open Group standard. It breaks risk into how often loss events happen and how big each loss is, gives each a range, and then uses a computer to play out thousands of possible years. This is called Monte Carlo simulation, named after the famous casino, because it is driven by random numbers. The result is not one number but a picture: the average year, a bad year, and a very bad year.')}
{wwh('<b>Monte Carlo risk simulation</b> plays out thousands of random years using ranges for how often incidents happen and how much each costs, then reports the average and the bad tail.',
     'Averages hide rare but huge losses. A company needs to know how bad a 1 in 10 or 1 in 100 year could be, to choose insurance and reserves.',
     'For each simulated year, draw whether incidents happen (for example a small chance each month) and draw a cost for each one from its range. Repeat many times, sort the yearly losses and read off the average and the high percentiles.')}
{run('monte_carlo')}
{fxs(fx('FAIR top level', 'risk = loss event frequency &times; loss magnitude', 'Loss event frequency = threat event frequency &times; vulnerability (the chance a threat event becomes a loss).', key=True),
     fx('Percentile of yearly loss', '90th percentile = the loss that only 1 year in 10 is worse than', 'Also called loss exceedance. Insurers and boards often ask for the 1 in 10 and the 1 in 100 year loss.'))}
{deep('Why the average alone is dangerous', '<p>In the simulation above most years have no breach at all, yet the average is far from zero because of the rare bad years. Cyber losses have <b>heavy tails</b>: a few events cause most of the total loss. Research on breach sizes finds distributions such as the log normal or power law, where the mean can be much larger than the typical (median) event. This is why FAIR reports a loss exceedance curve, the chance that yearly loss exceeds each amount, instead of one ALE.</p>')}
''', kw=['FAIR', 'Monte Carlo', 'simulation', 'loss event frequency', 'loss magnitude', 'percentile', 'loss exceedance', 'heavy tail'])

K.lesson('continuity', 'Availability numbers: RTO, RPO, MTBF and the nines', f'''
{talk('Some risks are not about stolen data but about time. If a hospital system stops, how long can doctors manage without it? If a bank loses its database, how many minutes of transactions can it afford to lose? These questions lead to a set of time numbers that every business continuity plan uses. The recovery time objective is how fast you must be back. The recovery point objective is how much data, measured in time, you can lose. Engineers also measure how often things break and how long repairs take. From these comes the famous language of nines: three nines means up ninety nine point nine percent of the time, which still allows almost nine hours of downtime a year.')}
{table(['Term', 'Plain meaning', 'Example'], [
    ['RTO (recovery time objective)', 'The longest the service may be down before it must be back', 'Online banking RTO 2 hours'],
    ['RPO (recovery point objective)', 'The most data, counted in time, that may be lost', 'RPO 15 minutes means back up at least every 15 minutes'],
    ['MTD (maximum tolerable downtime)', 'After this long, the business suffers severe damage. RTO must be shorter', 'A shop may survive 3 days without its website'],
    ['MTBF (mean time between failures)', 'Average time a system runs before it fails', '1000 hours'],
    ['MTTR (mean time to repair)', 'Average time to fix it after a failure', '2 hours']])}
{fxs(fx('Availability from MTBF and MTTR', 'A = MTBF / (MTBF + MTTR)', 'The share of time the system is working.', key=True),
     fx('Downtime allowed', 'downtime per year = (1 &minus; A) &times; 525,600 minutes', '99.9% gives about 525.6 minutes (8.76 hours). 99.99% gives about 52.6 minutes. 99.999% gives about 5.3 minutes.', key=True),
     fx('Two parts in a chain (both needed)', 'A = A<sub>1</sub> &times; A<sub>2</sub>', 'A chain is weaker than each part.'),
     fx('Two copies in parallel (either works)', 'A = 1 &minus; (1 &minus; A<sub>1</sub>)(1 &minus; A<sub>2</sub>)', 'A spare copy raises availability, the same maths as an OR node.'))}
{run('nines')}
{note('RPO is about data loss and decides how often you back up. RTO is about downtime and decides how fast you restore. Exams love to swap them.', 'exam')}
''', kw=['RTO', 'RPO', 'MTD', 'MTBF', 'MTTR', 'availability', 'nines', 'downtime', 'business continuity', 'redundancy'])

K.lesson('frameworks', 'Risk frameworks used in the real world', f'''
{talk('Big organisations do not invent their own way of managing risk. They follow published frameworks so that auditors, customers and regulators can trust the process. The two most used families are from NIST, the American standards institute, and ISO, the international standards organisation. NIST’s Risk Management Framework describes seven steps that run in a cycle, from preparing the organisation to monitoring controls forever. ISO 27005 gives guidance on information security risk that fits inside the ISO 27001 management system, which thousands of companies around the world are certified against. You do not need to memorise every page, but you should know the steps and why they repeat.')}
{table(['NIST RMF step (SP 800-37 Rev. 2)', 'What happens'], [
    ['1. Prepare', 'Set roles, risk strategy and appetite for the organisation and the system'],
    ['2. Categorise', 'Decide how bad a loss of C, I or A would be for this system (low, moderate, high)'],
    ['3. Select', 'Choose controls from the NIST SP 800-53 catalogue that fit the category'],
    ['4. Implement', 'Put the controls in place and write down how'],
    ['5. Assess', 'Test that the controls work as intended'],
    ['6. Authorise', 'A senior official accepts the remaining risk and allows the system to run'],
    ['7. Monitor', 'Keep watching controls, changes and new threats, and repeat']])}
{versus('Ways to assess risk', ['', 'Qualitative (matrix)', 'Quantitative (ALE)', 'FAIR with Monte Carlo'], [
    ['Inputs', 'Scores 1 to 5 from experts', 'Single money values: AV, EF, ARO', 'Ranges for frequency and loss'],
    ['Output', 'Colour zones and a ranked list', 'Money per year for each risk', 'Average loss plus bad year percentiles'],
    ['Speed', 'Fast, a workshop', 'Medium, needs some data', 'Slower, needs data and a tool'],
    ['Strength', 'Easy for everyone to read', 'Direct cost benefit of controls', 'Shows uncertainty and rare big losses'],
    ['Weakness', 'Scores are opinions, cannot be added', 'Single numbers look more exact than they are', 'Needs skill, ranges can still be guesses']],
    'Start with a matrix to find the big risks fast, use ALE to justify spending on them, and use FAIR style simulation for the few risks where rare huge losses matter, such as ransomware or a major data leak.')}
''', kw=['NIST RMF', 'SP 800-37', 'SP 800-53', 'SP 800-30', 'ISO 27005', 'ISO 27001', 'framework', 'qualitative vs quantitative', 'FAIR'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Risk sounds like a manager’s topic, but at the top level it becomes serious mathematics. A beginner learns that risk is likelihood times impact. A college student uses SLE, ARO and ALE and picks controls by cost. A masters student models uncertainty with probability distributions, simulation and decision theory, and asks how risks are linked to each other. Researchers study cyber insurance markets, how risks spread across companies that share the same software, and why companies under invest in security when the harm falls on others. As you move up, notice that the questions stay the same, how likely and how bad, but the tools become sharper.')}
{ladder(
    '<p>Risk is how likely something bad is and how bad it would be. We fix the biggest risks first, and we can never make risk zero.</p>',
    '<p>Use a risk matrix to rank risks, and SLE = AV &times; EF, ALE = SLE &times; ARO to price them. Choose avoid, reduce, transfer or accept for each risk above the appetite, and pick controls by category and type.</p>',
    '<p>Model frequency and severity as distributions (for example Poisson events with log normal losses), simulate yearly loss, and report expected loss and value at risk. Threat models (STRIDE, attack trees) feed the likelihoods. Controls are chosen to maximise risk reduction per rupee, subject to a budget.</p>',
    '<p>Research covers correlated cyber risk (one cloud outage or one software flaw hitting thousands of firms at once, which makes cyber insurance hard to price), game theoretic models of attacker and defender investment, the Gordon and Loeb model and its extensions, and externalities: when a firm’s weak security mainly harms others, the market under invests, which is why laws such as breach notification rules exist.</p>')}
{grow('Explain risk, read a risk matrix and name the four responses.',
      'Compute SLE, ALE and control value, availability and downtime, and evaluate an attack tree.',
      'Run a Monte Carlo loss model, read percentiles, and explain correlated risk and security externalities.')}
''', kw=['beginner', 'expert', 'value at risk', 'correlated risk', 'cyber insurance', 'externalities', 'game theory'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Risk = likelihood &times; impact.</b> Inherent risk is before controls, residual risk is after. Risk appetite is how much the business accepts.',
    'A <b>risk matrix</b> scores likelihood and impact from 1 to 5. Scores rank risks but are opinions, so do not add them.',
    '<b>SLE = AV &times; EF</b>, <b>ALE = SLE &times; ARO</b>, and a control is worth buying when ALE<sub>before</sub> &minus; ALE<sub>after</sub> &minus; cost &gt; 0.',
    'Four responses: <b>avoid, reduce, transfer, accept</b>. Control categories: technical, managerial, operational, physical. Types: preventive, deterrent, detective, corrective, compensating, directive.',
    '<b>STRIDE</b>: spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege.',
    '<b>Attack trees</b>: AND adds costs (multiplies chances), OR takes the cheapest (1 minus the product of failure chances). Fix the cheapest route first.',
    '<b>FAIR and Monte Carlo</b> use ranges and simulation to show the average loss and the bad 1 in 10 or 1 in 100 year.',
    'RTO is time to restore, RPO is data you may lose. A = MTBF / (MTBF + MTTR). 99.9% allows about 8.76 hours of downtime a year.'],
    'Foundations 1.3 teaches the maths every later chapter uses: binary and hex, XOR, modular arithmetic, probability, entropy and the size of key spaces.')}
{files('Three tasks: annualised loss expectancy, the yearly value of a control, and the cheapest attack in a nested attack tree.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Risk is best described as', ['Likelihood plus impact', 'Likelihood times impact', 'Impact only', 'The number of attackers'], 1, 'Two questions, multiplied.', 'Risk combines how likely and how bad: likelihood times impact.')
K.quiz('e', 'Buying cyber insurance is which risk response?', ['Avoid', 'Reduce', 'Transfer', 'Accept'], 2, 'The money loss moves to someone else.', 'Insurance transfers the financial loss.')
K.quiz('e', 'A CCTV camera that records a break in is mainly a', ['Preventive control', 'Detective control', 'Corrective control', 'Directive control'], 1, 'It spots and records.', 'Recording shows what happened, so it detects.')
K.quiz('e', 'Restoring files from a backup after ransomware is a', ['Deterrent control', 'Corrective control', 'Preventive control', 'Physical control'], 1, 'It fixes the damage.', 'Corrective controls restore normal operation.')
K.quiz('m', 'SLE stands for', ['Secure login entry', 'Single loss expectancy', 'System loss estimate', 'Standard loss exposure'], 1, 'The cost of one incident.', 'SLE = AV &times; EF, the cost of one incident.')
K.quiz('m', 'An event expected once every 4 years has an ARO of', ['4', '0.25', '0.4', '1'], 1, 'Events per year.', 'One event per 4 years is 0.25 per year.')
K.quiz('m', 'Which STRIDE threat is a normal user getting admin rights through a bug?', ['Spoofing', 'Tampering', 'Elevation of privilege', 'Repudiation'], 2, 'Gaining more rights.', 'Getting more rights than allowed is elevation of privilege.')
K.quiz('m', 'In an attack tree with costs, an OR node takes', ['The sum of its children', 'The cheapest child', 'The most expensive child', 'The average'], 1, 'Any one route is enough.', 'The attacker picks the cheapest route.')
K.quiz('m', 'A company must back up at least every 15 minutes. Which number sets this?', ['RTO', 'RPO', 'MTBF', 'MTTR'], 1, 'How much data may be lost.', 'The recovery point objective limits data loss in time.')
K.quiz('h', 'Why should risk matrix scores not be added across risks?', ['They are too big', 'They are ordinal labels from judgement, not real measurements', 'Addition is slower than multiplication', 'Because the matrix has 25 cells'], 1, 'Is 12 really twice 6?', 'The scores only order risks. Their gaps have no fixed meaning.')
K.quiz('h', 'Two servers each 99% available run in parallel, and either one can serve. Availability is', ['98%', '99%', '99.99%', '100%'], 2, '1 &minus; (1 &minus; A)<sup>2</sup>.', '1 &minus; 0.01 &times; 0.01 = 0.9999.')
K.quiz('h', 'Two risks have the same ALE. Risk X loses a small amount every year, risk Y loses nothing for decades then a huge amount. What does FAIR style simulation show that ALE hides?', ['Nothing, they are equal', 'The tail: Y has a much worse 1 in 100 year loss', 'X is always worse', 'Y has a higher average'], 1, 'Look beyond the mean.', 'Percentiles of the simulated yearly loss reveal the heavy tail of Y.')
K.quiz('x', 'In the style of a Stanford MS&amp;E risk question: a control lowers ARO from 0.5 to 0.1 for an SLE of 8 lakh and costs 2 lakh a year. What is its yearly value?', ['1.2 lakh', '3.2 lakh', '4 lakh', '&minus;0.8 lakh'], 0, 'ALE before minus after minus cost.', '4 &minus; 0.8 &minus; 2 = 1.2 lakh.')
K.quiz('x', 'In the style of a CMU 18-631 question: an attack tree OR node has children with success chances 0.5 and 0.5, tried independently. A defender can halve one child or remove the other. Which gives the lower root chance?', ['Halving one child', 'Removing one child', 'Both give the same', 'Neither changes it'], 1, 'Compute 1 &minus; product of failures.', 'Halve: 1 &minus; 0.75 &times; 0.5 = 0.625. Remove: 0.5. Removing is better.')

K.calc('e', 'An asset is worth 5,00,000 rupees and one incident destroys 20% of it. What is the SLE in rupees?', '100000', 'SLE = AV &times; EF.', ['AV = 5,00,000.', 'EF = 0.2.', eq('SLE = 5,00,000 &times; 0.2 = 1,00,000')], check=500000 * 0.2)
K.calc('e', 'SLE is 1,00,000 rupees and the event happens twice a year. What is the ALE?', '200000', 'ALE = SLE &times; ARO.', ['SLE = 1,00,000.', 'ARO = 2.', eq('ALE = 2,00,000')], check=100000 * 2)
K.calc('e', 'A risk has likelihood 4 and impact 4. What is its matrix score?', '16', 'Multiply.', ['Likelihood 4.', 'Impact 4.', eq('4 &times; 4 = 16')], check=16)
K.calc('m', 'AV = 20,00,000, EF = 0.4, ARO = 0.5. What is the ALE?', '400000', 'First SLE, then ALE.', ['SLE = 20,00,000 &times; 0.4 = 8,00,000.', 'ALE = 8,00,000 &times; 0.5.', eq('= 4,00,000')], check=2000000 * 0.4 * 0.5)
K.calc('m', 'ALE falls from 4,00,000 to 80,000 with a control that costs 60,000 a year. What is the control’s yearly value?', '260000', 'Before minus after minus cost.', ['Saving = 4,00,000 &minus; 80,000 = 3,20,000.', 'Minus cost 60,000.', eq('value = 2,60,000')], check=400000 - 80000 - 60000)
K.calc('m', 'MTBF is 999 hours and MTTR is 1 hour. What is the availability?', '0.999', 'MTBF / (MTBF + MTTR).', ['999 + 1 = 1000.', '999 / 1000.', eq('A = 0.999')], check=999 / 1000)
K.calc('m', 'How many minutes per year may a 99.99% available service be down? Round to 1 decimal place.', '52.6', '(1 &minus; A) &times; 525,600.', ['1 &minus; 0.9999 = 0.0001.', '0.0001 &times; 525,600 = 52.56.', eq('&asymp; 52.6 minutes')], check=round((1 - 0.9999) * 525600, 1))
K.calc('h', 'An attack tree OR node has an AND child with costs 2 and 7, and a leaf of cost 8. What is the cheapest attack?', '8', 'AND adds, OR takes the minimum.', ['AND child: 2 + 7 = 9.', 'OR of 9 and 8.', eq('min = 8')], check=min(2 + 7, 8))
K.calc('h', 'An OR node has independent children with success chances 0.2 and 0.5. What is the chance the goal is reached?', '0.6', '1 &minus; (1 &minus; 0.2)(1 &minus; 0.5).', ['Both fail: 0.8 &times; 0.5 = 0.4.', 'Complement.', eq('1 &minus; 0.4 = 0.6')], check=1 - 0.8 * 0.5, tol=1e-9)
K.calc('h', 'A web server (99.9%) and a database (99.5%) are both needed. What is the overall availability? Round to 4 decimal places.', '0.994', 'Chain: multiply.', ['0.999 &times; 0.995.', '= 0.994005.', eq('&asymp; 0.9940')], check=round(0.999 * 0.995, 4))
K.calc('x', 'In the style of an MIT 15.S quiz: incidents arrive as a Poisson process with rate 0.5 per year. What is the chance of at least one incident in a year? Round to 4 decimal places.', '0.3935', 'P(none) = e<sup>&minus;&lambda;</sup>.', ['P(0 events) = e<sup>&minus;0.5</sup> &asymp; 0.6065.', '1 &minus; 0.6065.', eq('&asymp; 0.3935')], check=round(1 - 2.718281828459045 ** -0.5, 4))

K.assign('ale', 'e', 'Annualised loss expectancy',
         '<p>Write <code>ale(asset_value, exposure_factor, aro)</code> that returns the annualised loss expectancy: first the single loss expectancy (asset value times exposure factor), then times the yearly rate.</p>',
         '''
def ale(asset_value, exposure_factor, aro):
    # your code here
    pass
''', [('ale(2000000, 0.4, 0.5)', 400000.0), ('ale(100, 1, 3)', 300), ('ale(500000, 0.2, 0)', 0.0)],
         '''
def ale(asset_value, exposure_factor, aro):
    sle = asset_value * exposure_factor
    return sle * aro
''', 'Two multiplications: AV &times; EF gives the SLE, then SLE &times; ARO.', '<p>ALE puts every risk on a money scale per year, so a manager can compare risks of very different kinds.</p>')
K.assign('value', 'e', 'Is the control worth it?',
         '<p>Write <code>control_value(ale_before, ale_after, cost)</code> that returns a pair: the yearly value of the control (before minus after minus cost) and the word "buy" when the value is above 0, otherwise "skip".</p>',
         '''
def control_value(ale_before, ale_after, cost):
    # your code here
    pass
''', [('control_value(400000, 80000, 60000)', [260000, 'buy']), ('control_value(10000, 9000, 5000)', [-4000, 'skip']), ('control_value(100, 50, 50)', [0, 'skip'])],
         '''
def control_value(ale_before, ale_after, cost):
    value = ale_before - ale_after - cost
    if value > 0:
        return [value, "buy"]
    return [value, "skip"]
''', 'Work out the value first, then decide the word with one if.', '<p>A control that costs more than the loss it removes is not worth it, however impressive it sounds. This simple test stops wasteful spending.</p>')
K.assign('tree', 'm', 'The cheapest attack in an attack tree',
         '<p>Write <code>cheapest(node)</code>. A node is either a number (the cost of one action) or a list whose first item is "AND" or "OR" followed by its children. An AND node costs the sum of its children, an OR node costs its cheapest child. For example <code>["OR", ["AND", 1, 5], 3]</code> costs 3.</p>',
         '''
def cheapest(node):
    # your code here
    pass
''', [('cheapest(["OR", ["AND", 1, 5], 3])', 3), ('cheapest(7)', 7), ('cheapest(["OR", ["AND", 1, 5], 3, 20, ["AND", 4, 50]])', 3), ('cheapest(["AND", ["OR", 9, 4], ["OR", 2, ["AND", 1, 1]]])', 6)],
         '''
def cheapest(node):
    if not isinstance(node, list):
        return node
    kind = node[0]
    costs = []
    for child in node[1:]:
        costs.append(cheapest(child))
    if kind == "AND":
        return sum(costs)
    return min(costs)
''', 'A number is its own cost. For a list, work out each child with the same function (recursion), then add for AND or take the smallest for OR.', '<p>This bottom up rule is exactly how attack tree tools rank routes. The same recursion with other rules gives the chance of success or the time an attack needs.</p>')

K.must('Risk', 'Risk = likelihood &times; impact. Inherent before controls, residual after. Appetite = what the business accepts.')
K.must('Money', 'SLE = AV &times; EF. ALE = SLE &times; ARO. Control value = ALE<sub>before</sub> &minus; ALE<sub>after</sub> &minus; cost.')
K.must('Responses and controls', 'Avoid, reduce, transfer, accept. Categories: technical, managerial, operational, physical. Types: preventive, deterrent, detective, corrective, compensating, directive.')
K.must('Threat models', 'STRIDE: spoofing, tampering, repudiation, information disclosure, DoS, elevation of privilege. Attack trees: AND adds, OR takes the cheapest.')
K.must('Uncertainty', 'FAIR: risk = loss event frequency &times; loss magnitude. Monte Carlo gives the average and the 1 in 10 or 1 in 100 year loss.')
K.must('Time', 'RTO = time to restore, RPO = data you may lose. A = MTBF / (MTBF + MTTR). 99.9% = 8.76 h down per year.')

T = K.topic(
    slug='cy-risk', topic='cy-risk', step=(1, 'Start here', 'cy-f1', 'What security protects and from whom, how risk is measured, and the maths every security decision uses.', 'Beginner'),
    title='Risk in numbers: matrices, ALE, attack trees and continuity', short='Risk in numbers', badge='1.2', minutes=60,
    lead='Learn to measure risk: the risk matrix, SLE, ARO and ALE with control cost benefit, the four risk responses and every control type, threat modelling with STRIDE and attack trees, FAIR with Monte Carlo simulation, RTO, RPO and the nines, and the NIST and ISO frameworks.',
    desc='risk equals likelihood times impact, inherent and residual risk, risk appetite, risk matrix, risk register, qualitative and quantitative risk, asset value, exposure factor, SLE, ARO, ALE, safeguard value, avoid reduce transfer accept, control categories and types, STRIDE, attack trees, FAIR, Monte Carlo, loss exceedance, RTO, RPO, MTD, MTBF, MTTR, availability, nines, NIST RMF, SP 800-37, SP 800-30, ISO 27005, correlated cyber risk.',
    summary='risk matrices, SLE, ARO and ALE, risk responses and control types, STRIDE and attack trees, FAIR simulation, RTO, RPO and the nines.',
    keywords=['risk', 'risk matrix', 'ALE', 'SLE', 'ARO', 'controls', 'STRIDE', 'attack tree', 'FAIR', 'RTO RPO'],
    recap='<p>Score risks to rank them, price them with ALE to choose controls, model attackers with trees, and plan recovery with RTO and RPO.</p>',
    added='2026-11-14')
