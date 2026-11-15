# Network and Systems 2.2: access control models. Checked against Lampson, Protection (1971), Anderson (1972),
# Saltzer and Schroeder (1975), Harrison, Ruzzo and Ullman (1976), Bell and LaPadula (1973 to 1976), Biba (1977),
# Clark and Wilson (1987), Brewer and Nash (1989), Ferraiolo and Kuhn (1992), ANSI INCITS 359-2004 (RBAC),
# NIST SP 800-162 (ABAC, 2014), Hardy, The Confused Deputy (1988) and Pang et al., Zanzibar (2019).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-access')
K = Kit()

K.code('access_matrix', r'''
# Lampson's access matrix (1971), and the two ways systems store it: ACLs and capability lists
matrix = {                               # matrix[subject][object] = set of rights
    "asha":  {"payroll.xlsx": {"read", "write"}, "wiki": {"read", "write"}},
    "ravi":  {"payroll.xlsx": {"read"},          "wiki": {"read"}},
    "build": {"repo": {"read"},                  "wiki": {"read"}},
}

# ACL: store each COLUMN with its object (what Linux, Windows and S3 buckets do)
acl = {}
for subject, row in matrix.items():
    for obj, rights in row.items():
        acl.setdefault(obj, {})[subject] = rights
# Capability list: store each ROW with its subject (like file descriptors or signed tokens)
caps = {subject: dict(row) for subject, row in matrix.items()}

print("ACL of payroll.xlsx:", {s: sorted(r) for s, r in acl["payroll.xlsx"].items()})
print("capabilities of ravi:", {o: sorted(r) for o, r in caps["ravi"].items()})

def check(subject, obj, right):
    return right in matrix.get(subject, {}).get(obj, set())

for s, o, r in [("ravi", "payroll.xlsx", "read"), ("ravi", "payroll.xlsx", "write"), ("build", "payroll.xlsx", "read")]:
    print(f"{s} {r} {o}: {'allowed' if check(s, o, r) else 'denied'}")

# Questions each layout answers quickly
print("who can touch payroll? (easy with ACLs):", sorted(acl["payroll.xlsx"]))
print("what can ravi touch?  (easy with capabilities):", sorted(caps["ravi"]))
''', long=True)

K.code('blp_biba', r'''
# Bell-LaPadula (secrecy) and Biba (integrity) on a lattice of levels and categories
LEVELS = {"UNCLASSIFIED": 0, "CONFIDENTIAL": 1, "SECRET": 2, "TOP SECRET": 3}

def dominates(a, b):
    # label a dominates b when its level is at least b's and it holds every category of b
    return LEVELS[a[0]] >= LEVELS[b[0]] and set(b[1]) <= set(a[1])

def blp(subject, obj, op):
    if op == "read":
        return dominates(subject, obj)   # simple security property: no read up
    return dominates(obj, subject)       # star property: no write down

officer = ("SECRET", {"NUCLEAR"})
files = {
    "lunch menu": ("UNCLASSIFIED", set()),
    "reactor plan": ("SECRET", {"NUCLEAR"}),
    "missile codes": ("TOP SECRET", {"NUCLEAR"}),
    "spy list": ("SECRET", {"CRYPTO"}),
}
for name, label in files.items():
    r = "yes" if blp(officer, label, "read") else "no"
    w = "yes" if blp(officer, label, "write") else "no"
    print(f"{name:14} {label[0]:13} {sorted(label[1])!s:12} read {r:3} write {w}")

# Biba flips the arrows to protect integrity: no read down, no write up
INTEGRITY = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
def biba(subject, obj, op):
    if op == "read":
        return INTEGRITY[obj] >= INTEGRITY[subject]     # never read less trusted data
    return INTEGRITY[subject] >= INTEGRITY[obj]          # never write to more trusted data
print("browser (LOW) writes system file (HIGH):", biba("LOW", "HIGH", "write"))
print("installer (HIGH) reads downloaded file (LOW):", biba("HIGH", "LOW", "read"))
''', long=True)

K.code('chinese_wall', r'''
# The Chinese Wall model (Brewer and Nash, 1989): what you may see depends on what you have already seen
conflict_classes = {
    "banks": {"Bank A", "Bank B", "Bank C"},
    "oil": {"Oil X", "Oil Y"},
}
history = {"consultant": set()}          # companies whose data this person has already opened

def company_class(company):
    return next(name for name, members in conflict_classes.items() if company in members)

def may_read(person, company):
    cls = conflict_classes[company_class(company)]
    seen_rivals = (history[person] & cls) - {company}
    return not seen_rivals               # allowed unless a competitor in the same class was already seen

for company in ["Bank A", "Oil X", "Bank A", "Bank B", "Oil Y"]:
    ok = may_read("consultant", company)
    if ok:
        history["consultant"].add(company)
    print(f"open {company:7}: {'allowed' if ok else 'BLOCKED (conflict of interest)'}  seen so far: {sorted(history['consultant'])}")
''', long=True)

K.code('rbac', r'''
# Role based access control (RBAC) with a role hierarchy and separation of duties
role_perms = {
    "employee":   {"read:wiki", "submit:expense"},
    "manager":    {"approve:expense"},
    "accountant": {"pay:expense", "read:ledger"},
    "auditor":    {"read:ledger", "read:logs"},
}
juniors = {"manager": ["employee"], "accountant": ["employee"], "auditor": ["employee"]}   # seniors inherit
user_roles = {"asha": {"manager"}, "ravi": {"accountant"}, "meera": {"auditor"}, "dev": {"employee"}}
conflicts = [("manager", "accountant")]  # the same person must not approve AND pay (separation of duties)

def all_roles(role):
    found = {role}
    for j in juniors.get(role, []):
        found |= all_roles(j)
    return found

def perms(user):
    out = set()
    for r in user_roles.get(user, set()):
        for rr in all_roles(r):
            out |= role_perms[rr]
    return out

for user in user_roles:
    print(f"{user:6} roles {sorted(user_roles[user])} -> {sorted(perms(user))}")

def assign(user, role):
    new = user_roles[user] | {role}
    for a, b in conflicts:
        if a in new and b in new:
            return f"refused: {a} and {b} conflict (separation of duties)"
    user_roles[user] = new
    return "assigned"

print("give asha the accountant role:", assign("asha", "accountant"))
print("give dev the manager role:   ", assign("dev", "manager"))
print("asha may pay expenses:", "pay:expense" in perms("asha"))
''', long=True)

K.code('abac', r'''
# Attribute based access control (ABAC): decide from attributes of user, resource, action and context
POLICY = [                               # checked in order, deny rules win (deny overrides)
    ("deny",  lambda u, r, a, c: not c["device_managed"], "unmanaged device"),
    ("deny",  lambda u, r, a, c: r["classification"] == "restricted" and u["clearance"] < 2, "clearance too low"),
    ("allow", lambda u, r, a, c: u["dept"] == r["dept"] and a in ("read", "edit"), "same department"),
    ("allow", lambda u, r, a, c: u["role"] == "auditor" and a == "read", "auditors may read"),
]

def decide(u, r, a, c):
    allow_reason = None
    for effect, test, why in POLICY:
        if test(u, r, a, c):
            if effect == "deny":
                return "DENY", why
            allow_reason = allow_reason or why
    return ("ALLOW", allow_reason) if allow_reason else ("DENY", "no rule allows it (default deny)")

doc = {"dept": "finance", "classification": "restricted"}
people = {
    "asha (finance, clearance 2)": {"dept": "finance", "clearance": 2, "role": "staff"},
    "ravi (finance, clearance 1)": {"dept": "finance", "clearance": 1, "role": "staff"},
    "meera (audit, clearance 2)":  {"dept": "audit", "clearance": 2, "role": "auditor"},
    "dev (sales, clearance 2)":    {"dept": "sales", "clearance": 2, "role": "staff"},
}
for name, user in people.items():
    print(f"{name:28} edit: {decide(user, doc, 'edit', {'device_managed': True})}")
print("asha on a personal laptop:", decide(people["asha (finance, clearance 2)"], doc, "read", {"device_managed": False}))
''', long=True)

K.lesson('idea', 'Subjects, objects and the reference monitor', f'''
{talk('Once a system knows who you are, it must decide what you may do. This is access control, also called authorisation. The vocabulary comes from the early 1970s. Subjects are the active parties, users and the processes acting for them. Objects are the things they act on: files, records, devices, API endpoints. Rights or permissions are the operations allowed, such as read, write or execute. Butler Lampson described in 1971 the access matrix, a table with a row for each subject, a column for each object, and the rights in each cell. In 1972 James Anderson’s report for the US Air Force introduced the reference monitor: a component that checks every access, cannot be tampered with, and is small enough to verify. Every operating system kernel, database and web framework contains some version of it. In 1975 Jerome Saltzer and Michael Schroeder wrote down design principles that are still taught, among them least privilege, fail safe defaults and complete mediation. Access control is still where many breaches happen: broken access control is number one in the 2021 OWASP Top 10, and the 2019 Capital One breach combined a server side request forgery with an overly powerful cloud role. This chapter covers the classic models and how they appear in real systems today.')}
{src('Lampson, Protection (1971), Anderson, Computer Security Technology Planning Study (1972), Saltzer and Schroeder, The Protection of Information in Computer Systems (1975), Harrison, Ruzzo and Ullman (1976), Bell and LaPadula (MITRE 1973 to 1976), Biba (1977), Clark and Wilson (IEEE S&amp;P 1987), Brewer and Nash (1989), Ferraiolo and Kuhn (1992), ANSI INCITS 359-2004, NIST SP 800-162 (2014), Hardy (1988), Pang et al., Zanzibar (USENIX ATC 2019), OWASP Top 10 (2021).')}
{wwh('<b>Access control</b> decides whether a subject may perform an operation on an object, according to a policy, and enforces that decision on every access.',
     'Authentication only says who you are. Without correct authorisation, any logged in user, or any process an attacker hijacks, could do anything.',
     'A reference monitor intercepts each request and checks it against stored policy: an access matrix kept as ACLs or capabilities, security labels, roles or attributes.')}
{fxs(fx('Access matrix', 'A[s, o] = set of rights subject s has on object o', '10000 users and 10<sup>6</sup> objects give 10<sup>10</sup> cells, almost all empty, so systems store only the non empty ones.', key=True),
     fx('Reference monitor requirements', 'always invoked + tamper proof + verifiable', 'Complete mediation: check every access, not only the first one, or a cached decision can be abused.'))}
{table(['Saltzer and Schroeder principle', 'Meaning', 'Example today'], [
    ['Least privilege', 'Give only the rights needed for the task', 'Cloud roles scoped to one bucket'],
    ['Fail safe defaults', 'Deny unless explicitly allowed', 'Default deny firewall and IAM policies'],
    ['Complete mediation', 'Check every access', 'Authorisation on every API call, not only the menu'],
    ['Separation of privilege', 'Require two conditions or people', 'Two person approval for payments'],
    ['Economy of mechanism', 'Keep the checker small and simple', 'A small kernel or policy engine'],
    ['Open design', 'Security must not depend on secret design', 'Public algorithms and policy languages']])}
''', kw=['access control', 'authorisation', 'subject', 'object', 'rights', 'access matrix', 'Lampson', 'reference monitor', 'Anderson report', 'Saltzer and Schroeder', 'least privilege', 'complete mediation', 'fail safe defaults', 'broken access control', 'Capital One'])

K.lesson('matrix', 'ACLs and capabilities', f'''
{talk('No system stores the whole access matrix, because it is huge and mostly empty. There are two natural ways to store only its useful parts. An access control list stores one column with each object: for this file, asha may read and write, ravi may read. Unix permission bits are a compressed ACL with three entries, owner, group and others, and Windows, macOS, cloud storage buckets and databases all use richer ACLs. A capability list stores one row with each subject: this process holds a right to read this file and write that socket. An open file descriptor in Unix is a capability: once you have it, the kernel does not check the file’s permissions again. ACLs make it easy to answer who can access an object and to revoke one person, but hard to list everything a subject can reach. Capabilities make delegation and checking easy, because holding the capability is the proof, but revocation is hard, since copies may be anywhere. Capabilities also avoid the confused deputy problem, described by Norm Hardy in 1988, where a privileged program is tricked into using its own authority on behalf of a caller who should not have it. Server side request forgery and many cloud breaches are confused deputy attacks.')}
{viz('cymatrix')}
{run('access_matrix')}
{table(['', 'Access control list', 'Capability list'], [
    ['Stored with', 'The object (column)', 'The subject (row)'],
    ['Quick question', 'Who can access this object?', 'What can this subject access?'],
    ['Revocation', 'Easy: edit one list', 'Hard: copies may exist'],
    ['Delegation', 'Needs an admin or owner to edit the list', 'Easy: pass the capability'],
    ['Examples', 'Unix bits, Windows ACLs, S3 bucket policies', 'File descriptors, Capsicum, seL4, signed bearer tokens']])}
{note('A confused deputy is a program with authority that acts on a request without checking the requester’s authority. A web server that fetches any URL a user gives it, including the cloud metadata service, is a confused deputy. Fix it by checking on behalf of whom an action is done, or by passing capabilities instead of names.', 'warn')}
''', kw=['ACL', 'access control list', 'capability', 'capability list', 'file descriptor', 'Unix permissions', 'revocation', 'delegation', 'confused deputy', 'Hardy', 'SSRF', 'Capsicum', 'seL4'])

K.lesson('mac', 'DAC and MAC: Bell-LaPadula and Biba', f'''
{talk('In discretionary access control, DAC, the owner of an object decides who may use it. Most desktop systems work this way. Its weakness is that any program you run acts with your rights, so a Trojan horse can copy your secret file anywhere you can write. Mandatory access control, MAC, takes the decision away from users: the system enforces a policy based on security labels that users cannot change. The classic secrecy model is Bell-LaPadula, developed at MITRE from 1973 for the US military. Each subject has a clearance and each object a classification, such as Confidential, Secret or Top Secret, plus categories called compartments, such as Nuclear or Crypto. Labels form a lattice. A subject may read an object only if its label dominates the object’s label: no read up. It may write only if the object’s label dominates its own: no write down. Together these stop information from flowing to a lower level, even through a Trojan horse. In 1977 Kenneth Biba turned the model around for integrity: no read down, so trusted processes are not polluted by untrusted data, and no write up, so untrusted processes cannot corrupt trusted data. Today SELinux, released by the NSA in 2000 and part of Android since 2014, and AppArmor provide MAC in Linux, and Windows Mandatory Integrity Control follows Biba’s idea.')}
{viz('cyblp')}
{run('blp_biba')}
{wwh('<b>Bell-LaPadula</b> (secrecy): read if L(s) &ge; L(o), write if L(o) &ge; L(s). <b>Biba</b> (integrity): read if I(o) &ge; I(s), write if I(s) &ge; I(o).',
     'They give guarantees that hold even when users make mistakes or run malicious code, which DAC cannot.',
     'Give every subject and object a label (level plus a set of categories). The reference monitor compares labels with the dominance relation on every read and write.')}
{fxs(fx('Dominance', '(l<sub>1</sub>, C<sub>1</sub>) &ge; (l<sub>2</sub>, C<sub>2</sub>) iff l<sub>1</sub> &ge; l<sub>2</sub> and C<sub>2</sub> &sube; C<sub>1</sub>', 'SECRET {NUCLEAR} dominates UNCLASSIFIED {}, but not SECRET {CRYPTO}: the categories do not nest.', key=True),
     fx('Number of labels', '|levels| &times; 2<sup>|categories|</sup>', '4 levels and 3 categories: 4 &times; 8 = 32 labels.', key=True),
     fx('Lattice operations', 'join = (max level, union of categories), meet = (min level, intersection)', 'Data combined from two labels must carry their join.'))}
{deep('Why the star property is needed', '<p>With only no read up, a Secret user could run a program that reads a Secret file and writes its contents into an Unclassified file, which Unclassified users can read. The leak needs no read up at all, just a write down. The star property forbids that write. It does make life awkward: a Secret user cannot even send an email to an Unclassified colleague. Real systems add trusted subjects that may downgrade after review. Even then, covert channels, such as a high process varying CPU load or file locks that a low process can observe, can leak bits, which is why high assurance systems also measure and limit covert channel bandwidth.</p>')}
''', kw=['DAC', 'discretionary access control', 'MAC', 'mandatory access control', 'Bell-LaPadula', 'no read up', 'no write down', 'star property', 'Biba', 'integrity', 'lattice', 'dominance', 'clearance', 'categories', 'SELinux', 'AppArmor', 'Mandatory Integrity Control', 'covert channel', 'Trojan horse'])

K.lesson('commercial', 'Commercial models: Clark-Wilson and the Chinese Wall', f'''
{talk('Businesses care less about classified levels and more about honest records and conflicts of interest. In 1987 David Clark and David Wilson described a model based on how accountants keep books. Data that matters, such as account balances, may only be changed by well formed transactions, programs certified to keep the data consistent, and duties are separated so no single person can both create and approve a change. Every change is logged so it can be audited. In 1989 David Brewer and Michael Nash formalised the Chinese Wall policy used by consultancies and banks. Companies are grouped into conflict of interest classes, such as all banks or all oil firms. A consultant may at first read any company’s data, but once they have read one bank’s files, they may no longer read another bank’s, although an oil company is still fine. What you may access depends on what you have already accessed, which makes this model dynamic, unlike Bell-LaPadula.')}
{run('chinese_wall')}
{table(['Model', 'Year', 'Protects', 'Key rule'], [
    ['Clark-Wilson', '1987', 'Integrity of business data', 'Only certified transactions change data, duties are separated, everything is logged'],
    ['Chinese Wall (Brewer-Nash)', '1989', 'Conflicts of interest', 'After reading one company in a class, rivals in that class are blocked'],
    ['Bell-LaPadula', '1973', 'Secrecy', 'No read up, no write down'],
    ['Biba', '1977', 'Integrity', 'No read down, no write up']])}
{fxs(fx('Chinese Wall choices', 'possible sets of companies one person can end up with = product of class sizes', 'Classes of 4, 3 and 5 companies: 4 &times; 3 &times; 5 = 60 possible final sets, each with at most one company per class.', key=True))}
''', kw=['Clark-Wilson', 'well formed transaction', 'separation of duties', 'audit', 'Chinese Wall', 'Brewer-Nash', 'conflict of interest', 'dynamic policy'])

K.lesson('rbac', 'Role based access control', f'''
{talk('In a company of thousands, giving permissions to each person directly becomes unmanageable: people join, move and leave every week. Role based access control, proposed by David Ferraiolo and Richard Kuhn at NIST in 1992 and standardised in 2004, adds a layer in between. Permissions are assigned to roles, such as accountant or nurse, and users are assigned to roles. When someone changes job, an administrator changes their roles, not hundreds of permissions. Roles can form a hierarchy, where a senior role inherits the permissions of junior ones. Constraints add safety: static separation of duties forbids one person from holding two conflicting roles, such as the person who approves payments and the person who makes them, and dynamic separation forbids activating both in the same session. RBAC is everywhere: databases, Kubernetes, cloud platforms and business applications. Its typical problem is role explosion, where organisations create thousands of narrow roles, and permission creep, where people collect roles as they move and never lose them, which regular access reviews must catch.')}
{viz('cyrbac')}
{run('rbac')}
{wwh('<b>RBAC</b>: users &rarr; roles &rarr; permissions, with role hierarchies and separation of duty constraints (ANSI INCITS 359-2004).',
     'It matches how organisations think about jobs, cuts administration, and makes reviews and audits practical.',
     'Store user assignment (UA) and permission assignment (PA) relations. A user has permission p if some role they hold, or a role that role inherits, has p. Refuse assignments that break conflict rules.')}
{fxs(fx('Administration saving', 'direct: |users| &times; perms per user, RBAC: |UA| + |PA|', '1000 users with 80 permissions each: 80000 direct entries. With 20 roles: 2000 user role links + 800 role permission links = 2800.', key=True),
     fx('Possible conflicting pairs', 'C(r, 2) = r(r &minus; 1)/2', '6 roles give 15 pairs to consider for separation of duties.'))}
''', kw=['RBAC', 'role based access control', 'Ferraiolo and Kuhn', 'role hierarchy', 'separation of duties', 'static SoD', 'dynamic SoD', 'role explosion', 'permission creep', 'access review', 'Kubernetes RBAC'])

K.lesson('abac', 'Attribute based and relationship based access control', f'''
{talk('Roles are sometimes too coarse. A hospital may want to say that a doctor may read a patient’s record only while assigned to that patient’s ward, during a shift, from a managed device. Attribute based access control, ABAC, described in NIST SP 800-162 in 2014, writes policies over attributes of the subject (department, clearance, role), the resource (owner, classification), the action, and the environment (time, location, device health). A policy engine evaluates each request against the rules. Cloud identity policies, such as those in AWS IAM with their conditions, and policy engines such as Open Policy Agent work this way, and XACML is an older standard language for it. When rules conflict, a combining rule decides, commonly deny overrides: any matching deny wins. A related idea, relationship based access control, decides from a graph of relationships: you may edit this document because you are a member of a group that owns its folder. Google described its global system for this, Zanzibar, in 2019, and it inspired open source systems such as SpiceDB and OpenFGA. The trade off is power against understandability: the more expressive the policy, the harder it is to know who can actually do what.')}
{run('abac')}
{wwh('<b>ABAC</b>: allow or deny from rules over subject, resource, action and environment attributes. <b>ReBAC</b>: decide from relationships in a graph.',
     'It expresses context such as time, location, device health and ownership that roles alone cannot, which zero trust needs.',
     'A policy decision point evaluates rules, combines results (often deny overrides with default deny), and a policy enforcement point applies the result.')}
{fxs(fx('Attribute combinations', 'cases = product of the number of values of each attribute', '5 departments &times; 3 clearances &times; 2 device states = 30 cases a policy must handle correctly.', key=True))}
{note('More expressive policies are harder to audit. Test policies like code: write cases that must be allowed and must be denied, and run them on every change.', 'tip')}
''', kw=['ABAC', 'attribute based access control', 'NIST SP 800-162', 'policy engine', 'Open Policy Agent', 'XACML', 'AWS IAM', 'deny overrides', 'ReBAC', 'relationship based access control', 'Zanzibar', 'SpiceDB', 'OpenFGA'])

K.lesson('versus', 'Access control models compared', f'''
{talk('Most real systems mix models. A Linux server uses DAC permission bits, SELinux MAC labels and sudo roles. A cloud account uses RBAC for broad roles and ABAC conditions for context. The useful exam habit is to match the model to the goal: secrecy with labels calls for Bell-LaPadula, integrity for Biba or Clark-Wilson, conflicts of interest for the Chinese Wall, organisational jobs for RBAC, and context dependent rules for ABAC.')}
{versus('Access control models side by side', ['', 'DAC', 'MAC (BLP, Biba)', 'RBAC', 'ABAC', 'Capabilities'], [
    ['Who decides', 'Object owner', 'System policy and labels', 'Admins via roles', 'Policy over attributes', 'Whoever holds and passes the token'],
    ['Strength', 'Flexible, simple', 'Strong guarantees against Trojans', 'Scales with organisations', 'Context aware, fine grained', 'Easy delegation, no confused deputy'],
    ['Weakness', 'Trojans, mistakes spread', 'Rigid, awkward to use', 'Role explosion, creep', 'Hard to audit', 'Hard to revoke'],
    ['Example', 'Unix permissions, file sharing', 'SELinux, military systems', 'Kubernetes, databases', 'AWS IAM conditions, OPA', 'File descriptors, seL4, signed URLs'],
    ['Exam phrase', 'Owner discretion', 'No read up, no write down', 'Users to roles to permissions', 'Rules over attributes', 'Unforgeable token']],
    'Combine them: least privilege roles, attribute conditions for context, MAC for the most sensitive systems, and regular reviews.')}
''', kw=['comparison', 'DAC', 'MAC', 'RBAC', 'ABAC', 'capabilities'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner understands that logging in is not the same as being allowed, and that everyone should have only the access they need. A college student can explain the access matrix, ACLs and capabilities, Bell-LaPadula and Biba rules, RBAC with separation of duties, and write a policy check in code. A masters student studies lattice based information flow, the Harrison, Ruzzo and Ullman result that deciding whether a right can ever leak is undecidable in general, Clark-Wilson certification, SELinux type enforcement, cloud IAM policy analysis and the confused deputy. Researchers verify kernels such as seL4, analyse policies with SMT solvers, as cloud providers now do to find public buckets, design language based information flow control, and build relationship based systems at global scale.')}
{ladder(
    '<p>Logging in is not permission. Give people only the access they need, and remove it when they change jobs.</p>',
    '<p>Access matrix, ACLs versus capabilities, DAC and MAC, Bell-LaPadula and Biba rules with dominance, Chinese Wall, RBAC with SoD, ABAC with deny overrides.</p>',
    '<p>Lattices and information flow, HRU undecidability, Clark-Wilson, SELinux type enforcement, IAM policy evaluation, confused deputies and SSRF, access reviews.</p>',
    '<p>Verified kernels (seL4), SMT based policy analysis, information flow type systems, Zanzibar style ReBAC at scale, and covert channel analysis.</p>')}
{grow('Explain least privilege and spot over broad access.',
      'Apply each model to a scenario and code a checker.',
      'Analyse and verify policies and information flow.')}
''', kw=['beginner', 'expert', 'HRU', 'undecidable', 'type enforcement', 'SMT', 'information flow control', 'seL4'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Basics</b>: subjects, objects, rights. Lampson’s matrix (1971), Anderson’s reference monitor (1972), Saltzer and Schroeder’s principles (1975).',
    '<b>ACLs and capabilities</b>: columns with objects (easy revoke) or rows with subjects (easy delegate). Confused deputy and SSRF.',
    '<b>DAC and MAC</b>: owner decides, or labels decide. Bell-LaPadula: no read up, no write down. Biba: no read down, no write up.',
    '<b>Dominance</b>: level &ge; and categories &sube;. Labels = levels &times; 2<sup>categories</sup>. SELinux, AppArmor, Windows integrity levels.',
    '<b>Commercial</b>: Clark-Wilson (certified transactions, SoD, audit), Chinese Wall (rivals blocked after first access).',
    '<b>RBAC</b>: users to roles to permissions, hierarchy, static and dynamic SoD. Watch role explosion and creep.',
    '<b>ABAC and ReBAC</b>: rules over attributes (NIST SP 800-162, deny overrides) and relationship graphs (Zanzibar).'],
    'Next, Network and Systems 3.1: malware, how it spreads, how detection works and the maths of epidemics.')}
{files('Three tasks: an ACL check, Bell-LaPadula with categories, and RBAC with role inheritance.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is the principle of least privilege?', ['Give everyone admin', 'Give each user or program only the rights it needs for its task', 'Use the fewest passwords', 'Deny everything'], 1, 'Minimum.', 'It limits the damage from mistakes and stolen accounts.')
K.quiz('e', 'In discretionary access control (DAC), who decides who may use a file?', ['The government', 'The file’s owner', 'The CPU', 'Nobody'], 1, 'Discretion.', 'Owners grant and revoke access themselves.')
K.quiz('e', 'Bell-LaPadula mainly protects', ['Availability', 'Secrecy (confidentiality)', 'Integrity', 'Speed'], 1, 'Military secrets.', 'Biba is the integrity counterpart.')
K.quiz('e', 'In RBAC, permissions are given to', ['Each user directly', 'Roles, and users get roles', 'Files', 'Networks'], 1, 'Middle layer.', 'Change a role once and everyone in it changes.')
K.quiz('m', 'Under Bell-LaPadula, a Secret user may', ['Read Top Secret', 'Write to an Unclassified file', 'Read Confidential and write Top Secret', 'Read and write anything'], 2, 'Up only.', 'No read up, no write down. Reading lower and writing higher are both allowed.')
K.quiz('m', 'Why is the star property (no write down) needed?', ['To save disk space', 'Without it a Trojan horse could copy secret data into a lower level file', 'To stop reading', 'For speed'], 1, 'Trojan.', 'No read up alone does not stop leaks through writes.')
K.quiz('m', 'An ACL is stored with', ['The subject', 'The object', 'The network', 'The CPU'], 1, 'Column.', 'Capability lists are stored with the subject.')
K.quiz('m', 'Separation of duties stops', ['Slow logins', 'One person both approving and paying an expense', 'Encryption', 'Backups'], 1, 'Fraud.', 'Two conflicting roles must be held by different people.')
K.quiz('m', 'In the Chinese Wall model, after reading Bank A’s files a consultant may still read', ['Bank B', 'An oil company’s files', 'Every bank', 'Nothing'], 1, 'Other class.', 'Only rivals in the same conflict of interest class are blocked.')
K.quiz('h', 'Does SECRET {NUCLEAR} dominate SECRET {CRYPTO}?', ['Yes', 'No, their category sets do not nest', 'Only on weekends', 'Yes, same level'], 1, 'Both conditions.', 'Dominance needs level &ge; and category subset. Neither label dominates the other.')
K.quiz('h', 'Biba’s rules are', ['No read up, no write down', 'No read down, no write up', 'Read anything', 'Write anything'], 1, 'Flipped.', 'Trusted processes must not read untrusted data or be written by untrusted processes.')
K.quiz('h', 'A web server fetches any URL a user supplies, including the cloud metadata service. This is an example of', ['Least privilege', 'A confused deputy', 'Biba', 'RBAC'], 1, 'Borrowed authority.', 'The server uses its own authority on the attacker’s behalf, the pattern behind SSRF breaches such as Capital One 2019.')
K.quiz('h', 'Which is hardest to do with pure capabilities?', ['Delegation', 'Revocation', 'Checking access', 'Passing rights to a child process'], 1, 'Copies.', 'Once handed out, a capability may be copied anywhere.')
K.quiz('x', 'In the style of a Stanford CS 155 question: Harrison, Ruzzo and Ullman (1976) proved that in the general access matrix model', ['Every system is safe', 'Deciding whether a right can ever leak to a subject is undecidable', 'ACLs are faster', 'MAC is impossible'], 1, 'Safety problem.', 'It reduces to the halting problem, so restricted models are used when safety must be decidable.')
K.quiz('x', 'In the style of an IIT Madras OS security exam: with levels {L, H} and categories {a, b}, how many ordered pairs of labels (x, y) have x dominating y?', ['16', '27', '64', '8'], 1, '3 &times; 9.', 'Level pairs with l<sub>x</sub> &ge; l<sub>y</sub>: 3. Category pairs with C<sub>y</sub> &sube; C<sub>x</sub>: 3<sup>2</sup> = 9. Total 27.')

K.calc('e', 'An access matrix for 50 users and 200 files has how many cells?', '10000', 'Rows &times; columns.', ['50 &times; 200.', 'Most are empty in practice.', eq('10000 cells')], check=50 * 200)
K.calc('e', 'Levels U = 0, C = 1, S = 2, TS = 3. Under Bell-LaPadula, how many of these levels may a Secret subject read?', '3', 'At or below.', ['U, C and S.', 'Not TS.', eq('3 levels')], check=3)
K.calc('e', 'Same levels. How many levels may a Secret subject write to under the star property?', '2', 'At or above.', ['S and TS.', 'Not U or C.', eq('2 levels')], check=2)
K.calc('m', '4 levels and 3 categories. How many different security labels exist?', '32', 'levels &times; 2<sup>categories</sup>.', ['Category subsets: 2<sup>3</sup> = 8.', '4 &times; 8.', eq('32 labels')], check=4 * 2 ** 3)
K.calc('m', 'Biba with integrity Low = 0, Medium = 1, High = 2. How many levels may a Medium subject read?', '2', 'At or above.', ['Medium and High.', 'Not Low.', eq('2 levels')], check=2)
K.calc('m', '1000 users, each in 2 roles. 20 roles, each with 40 permissions. How many RBAC assignment entries (UA + PA)?', '2800', '2000 + 800.', ['UA: 1000 &times; 2 = 2000.', 'PA: 20 &times; 40 = 800.', eq('2800 entries')], check=1000 * 2 + 20 * 40)
K.calc('m', 'Without roles, the same 1000 users each need 80 permissions. How many direct entries?', '80000', '1000 &times; 80.', ['One entry per user and permission.', '1000 &times; 80.', eq('80000 entries')], check=1000 * 80)
K.calc('m', 'How many pairs of roles must be considered for separation of duties among 6 roles?', '15', 'C(6, 2).', ['6 &times; 5 / 2.', '= 15.', eq('15 pairs')], check=6 * 5 // 2)
K.calc('h', 'Chinese Wall classes with 4 banks, 3 oil firms and 5 airlines. How many different final sets of companies can one consultant end up with, one per class?', '60', 'Product.', ['One choice in each class.', '4 &times; 3 &times; 5.', eq('60 sets')], check=4 * 3 * 5)
K.calc('h', 'ABAC attributes: 5 departments, 3 clearances, 2 device states. How many combinations?', '30', 'Product.', ['5 &times; 3 = 15.', '&times; 2 = 30.', eq('30 combinations')], check=5 * 3 * 2)
K.calc('h', 'Unix permission bits give an ACL with how many entries (owner, group, others)?', '3', 'Three classes.', ['Owner, group, others.', 'Each with r, w, x.', eq('3 entries')], check=3)
K.calc('h', '10000 users and 10<sup>6</sup> objects. If each object has on average 3 ACL entries, how many ACL entries are stored?', '3000000', '10<sup>6</sup> &times; 3.', ['Store only non empty cells.', '3 &times; 10<sup>6</sup>, against 10<sup>10</sup> matrix cells.', eq('3000000')], check=3 * 10 ** 6)
K.calc('x', 'Levels {L, H} and categories {a, b}. How many ordered pairs (x, y) of labels have x dominating y?', '27', 'Level pairs &times; category pairs.', ['Level pairs with l<sub>x</sub> &ge; l<sub>y</sub>: (L,L), (H,L), (H,H) = 3.', 'Category pairs with C<sub>y</sub> &sube; C<sub>x</sub>: each element in neither, only x, or both: 3<sup>2</sup> = 9.', eq('3 &times; 9 = 27')], check=3 * 3 ** 2)
K.calc('x', 'With n categories, how many ordered pairs (A, B) of category sets satisfy B &sube; A? Give the value for n = 4.', '81', '3<sup>n</sup>.', ['Each category is in neither, in A only, or in both.', '3<sup>4</sup> = 81.', eq('81')], check=3 ** 4)

K.assign('acl_allows', 'e', 'Check an ACL',
         '<p>Write <code>acl_allows(acl, user, obj, op)</code>. <code>acl</code> maps each object to a dict that maps users to a list of operations. Return True if the user may do op on obj, and False otherwise, including when the object or user is missing.</p>',
         '''
def acl_allows(acl, user, obj, op):
    # your code here
    pass
''', [('acl_allows({"payroll": {"asha": ["read", "write"], "ravi": ["read"]}}, "ravi", "payroll", "read")', True), ('acl_allows({"payroll": {"asha": ["read", "write"], "ravi": ["read"]}}, "ravi", "payroll", "write")', False), ('acl_allows({"payroll": {"asha": ["read"]}}, "dev", "wiki", "read")', False)],
         '''
def acl_allows(acl, user, obj, op):
    return op in acl.get(obj, {}).get(user, [])
''', 'Chain .get with empty defaults so missing objects and users fall through to False.', '<p>Default deny comes for free: anything not listed is refused.</p>')
K.assign('blp_ok', 'm', 'Bell-LaPadula with categories',
         '<p>A label is [level, categories] with level a number and categories a list. Write <code>blp_ok(subject, obj, op)</code>. Label a dominates b if a’s level &ge; b’s level and every category of b is in a. Reading is allowed if the subject dominates the object, writing if the object dominates the subject.</p>',
         '''
def blp_ok(subject, obj, op):
    # your code here
    pass
''', [('blp_ok([2, ["NUC"]], [0, []], "read")', True), ('blp_ok([2, ["NUC"]], [0, []], "write")', False), ('blp_ok([2, ["NUC"]], [3, ["NUC"]], "write")', True), ('blp_ok([2, ["NUC"]], [2, ["CRY"]], "read")', False)],
         '''
def dominates(a, b):
    return a[0] >= b[0] and set(b[1]) <= set(a[1])

def blp_ok(subject, obj, op):
    if op == "read":
        return dominates(subject, obj)
    return dominates(obj, subject)
''', 'Write a helper dominates(a, b) using set(b[1]) <= set(a[1]) for the subset test.', '<p>The last test shows incomparable labels: neither dominates the other, so neither read nor write is allowed.</p>')
K.assign('rbac_has', 'h', 'RBAC with role inheritance',
         '<p>Write <code>rbac_has(user_roles, juniors, role_perms, user, perm)</code>. <code>user_roles</code> maps users to lists of roles, <code>juniors</code> maps a role to the roles it inherits (which may inherit further), and <code>role_perms</code> maps roles to lists of permissions. Return True if any role of the user, or any role reachable through inheritance, holds perm.</p>',
         '''
def rbac_has(user_roles, juniors, role_perms, user, perm):
    # your code here
    pass
''', [('rbac_has({"ravi": ["accountant"]}, {"accountant": ["employee"]}, {"employee": ["read wiki"], "accountant": ["pay"]}, "ravi", "read wiki")', True),
      ('rbac_has({"ravi": ["accountant"]}, {"accountant": ["employee"]}, {"employee": ["read wiki"], "accountant": ["pay"]}, "ravi", "approve")', False),
      ('rbac_has({"cfo": ["director"]}, {"director": ["manager"], "manager": ["employee"]}, {"employee": ["read wiki"], "manager": ["approve"], "director": []}, "cfo", "read wiki")', True)],
         '''
def rbac_has(user_roles, juniors, role_perms, user, perm):
    seen = set()
    stack = list(user_roles.get(user, []))
    while stack:
        role = stack.pop()
        if role in seen:
            continue
        seen.add(role)
        if perm in role_perms.get(role, []):
            return True
        stack.extend(juniors.get(role, []))
    return False
''', 'Walk the role graph with a stack or recursion, keep a seen set to avoid loops, and check each role’s permissions.', '<p>The third test needs two levels of inheritance: director to manager to employee.</p>')

K.must('Foundations', 'Subject, object, right. Lampson matrix 1971. Reference monitor: always invoked, tamper proof, verifiable. Least privilege, fail safe defaults, complete mediation.')
K.must('ACL and capability', 'ACL = column with object (easy revoke). Capability = row with subject (easy delegate, hard revoke). Confused deputy (Hardy 1988), SSRF.')
K.must('BLP and Biba', 'BLP: read if L(s) &ge; L(o), write if L(o) &ge; L(s). Biba flips. Dominance: level &ge; and categories &sube;. Labels = levels &times; 2<sup>k</sup>.')
K.must('Commercial', 'Clark-Wilson 1987: certified transactions, SoD, audit. Chinese Wall 1989: rivals in a class blocked after first access.')
K.must('RBAC', 'Users to roles to permissions (Ferraiolo and Kuhn 1992, ANSI 2004). Hierarchy, static and dynamic SoD. Role explosion, creep, reviews.')
K.must('ABAC and more', 'NIST SP 800-162: attributes of subject, resource, action, environment. Deny overrides. ReBAC (Zanzibar 2019). HRU 1976: safety undecidable.')

T = K.topic(
    slug='cy-access', topic='cy-access', step=(2, 'Identity and access', 'cy-s2', 'How systems prove who you are, from passwords and MFA to passkeys and Kerberos, and how they decide what you may do.', 'Intermediate'),
    title='Access control models: from the access matrix to RBAC and ABAC', short='Access control', badge='2.2', minutes=75,
    lead='How systems decide what an authenticated user may do: Lampson’s access matrix, the reference monitor and Saltzer and Schroeder’s principles, ACLs against capabilities and the confused deputy, Bell-LaPadula and Biba with lattice maths, Clark-Wilson and the Chinese Wall, RBAC with separation of duties, and ABAC and relationship based policies.',
    desc='access control, authorisation, access matrix, Lampson, reference monitor, Saltzer and Schroeder, least privilege, complete mediation, ACL, capability, confused deputy, DAC, MAC, Bell-LaPadula, no read up, no write down, star property, Biba, integrity, lattice, dominance, SELinux, AppArmor, Clark-Wilson, Chinese Wall, Brewer-Nash, RBAC, role hierarchy, separation of duties, ABAC, NIST SP 800-162, XACML, Open Policy Agent, ReBAC, Zanzibar, HRU, broken access control',
    summary='the access matrix, ACLs and capabilities, Bell-LaPadula and Biba, Clark-Wilson, Chinese Wall, RBAC and ABAC.',
    keywords=['access control', 'access matrix', 'ACL', 'capability', 'Bell-LaPadula', 'Biba', 'Chinese Wall', 'RBAC', 'ABAC', 'least privilege'],
    recap='<p>Authorisation turns identity into permissions. Choose the model that fits the goal, keep privileges minimal, and check every access.</p>',
    added='2026-11-15')
