# Security Operations 2.2: cloud security. Checked against the AWS, Microsoft Azure and Google Cloud shared responsibility
# pages, the AWS IAM policy evaluation logic documentation, AWS documentation on IMDSv2, AWS KMS envelope encryption,
# NIST SP 800-145 (definition of cloud computing), NIST SP 800-38D (GCM nonce limits), the CIS Benchmarks for cloud
# providers, the CSA Cloud Controls Matrix, the US Senate and court records on the Capital One breach (2019), the US Cyber
# Safety Review Board report on the Microsoft Storm-0558 intrusion (2024), Mandiant's report on the Snowflake customer
# account campaign UNC5537 (2024), and Gartner's 2019 statement on customer caused cloud failures.
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, safe, attack

chapter('cy-cloud')
K = Kit()

K.code('iam_eval', r'''
# How a cloud IAM policy decides, in the AWS order: an explicit Deny wins, then any Allow, otherwise Deny.
from fnmatch import fnmatch          # lets "*" match anything, like policy wildcards

policy = [
    {"effect": "Allow", "action": "s3:GetObject", "resource": "reports-bucket/*"},
    {"effect": "Allow", "action": "s3:PutObject", "resource": "reports-bucket/uploads/*"},
    {"effect": "Deny", "action": "s3:*", "resource": "reports-bucket/payroll/*"},
]

def decide(action, resource):
    matching = [s for s in policy if fnmatch(action, s["action"]) and fnmatch(resource, s["resource"])]
    if any(s["effect"] == "Deny" for s in matching):
        return "DENY (explicit)"
    if any(s["effect"] == "Allow" for s in matching):
        return "ALLOW"
    return "DENY (default, nothing allows it)"

requests = [
    ("s3:GetObject", "reports-bucket/q3.pdf"),
    ("s3:PutObject", "reports-bucket/uploads/a.csv"),
    ("s3:GetObject", "reports-bucket/payroll/nov.xlsx"),
    ("s3:DeleteObject", "reports-bucket/q3.pdf"),
]
for action, resource in requests:
    print(f"{action:16} {resource:34} {decide(action, resource)}")
''')

K.code('cspm_audit', r'''
# A tiny cloud security posture check (CSPM): read the settings and flag the classic mistakes
config = {
    "buckets": [
        {"name": "web-assets", "public_read": True, "encrypted": True, "purpose": "public website images"},
        {"name": "customer-exports", "public_read": True, "encrypted": False, "purpose": "CSV exports"},
        {"name": "backups", "public_read": False, "encrypted": True, "purpose": "nightly backups"},
    ],
    "firewall_rules": [
        {"name": "web", "port": 443, "source": "0.0.0.0/0"},
        {"name": "ssh-anywhere", "port": 22, "source": "0.0.0.0/0"},
        {"name": "db", "port": 5432, "source": "10.0.0.0/16"},
    ],
    "root_account_mfa": False,
    "audit_logging": True,
}

findings = []
for b in config["buckets"]:
    if b["public_read"] and "public" not in b["purpose"]:
        findings.append(("HIGH", f"bucket {b['name']} is public but holds {b['purpose']}"))
    if not b["encrypted"]:
        findings.append(("MEDIUM", f"bucket {b['name']} is not encrypted at rest"))
for r in config["firewall_rules"]:
    if r["source"] == "0.0.0.0/0" and r["port"] in (22, 3389, 5432, 3306):
        findings.append(("HIGH", f"rule {r['name']} opens admin or database port {r['port']} to the whole internet"))
if not config["root_account_mfa"]:
    findings.append(("CRITICAL", "root account has no MFA"))
if not config["audit_logging"]:
    findings.append(("HIGH", "audit logging is off"))

order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
for level, text in sorted(findings, key=lambda f: order[f[0]]):
    print(f"{level:8} {text}")
checks = len(config["buckets"]) * 2 + len(config["firewall_rules"]) + 2
print(f"\n{checks - len(findings)} of {checks} checks pass")
''')

K.code('envelope', r'''
# Envelope encryption, the way a cloud KMS does it. A toy cipher built from SHA-256 keeps it to the
# standard library. Real systems use AES-256-GCM. Never use this toy for real data.
import hashlib
import os

def keystream_xor(key, data):
    out = bytearray()
    counter = 0
    while len(out) < len(data):
        out += hashlib.sha256(key + counter.to_bytes(8, "big")).digest()
        counter += 1
    return bytes(a ^ b for a, b in zip(data, out))

MASTER_V1 = os.urandom(32)               # lives only inside the KMS hardware
file_data = b"Payroll November: 214 staff, total 1,93,40,000 rupees"

data_key = os.urandom(32)                         # 1. KMS makes a fresh data key
locked_key = keystream_xor(MASTER_V1, data_key)   #    and also returns it locked with the master key
cipher = keystream_xor(data_key, file_data)       # 2. encrypt the file with the plain data key
del data_key                                      # 3. forget the plain key, store cipher + locked_key
print("stored file  :", cipher[:24].hex(), "...")
print("stored key   :", locked_key[:12].hex(), "... (locked)")

# reading: ask KMS (which checks permission and logs the call) to unlock the data key
plain_key = keystream_xor(MASTER_V1, locked_key)
print("decrypted    :", keystream_xor(plain_key, cipher).decode())

# rotating the master key: only the 32 byte data key is re-locked, not the file
MASTER_V2 = os.urandom(32)
locked_key = keystream_xor(MASTER_V2, keystream_xor(MASTER_V1, locked_key))
print("after rotation the file bytes are unchanged, and it still opens:",
      keystream_xor(keystream_xor(MASTER_V2, locked_key), cipher) == file_data)
''', long=True)

K.code('least_privilege', r'''
# Least privilege from evidence: compare what a role is granted with what the audit log shows it used
granted = {"s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListAllMyBuckets", "ec2:RunInstances",
           "ec2:TerminateInstances", "iam:CreateUser", "iam:AttachUserPolicy", "kms:Decrypt", "sqs:SendMessage"}

# 90 days of audit log events for this role (action names only)
used_log = ["s3:GetObject"] * 4200 + ["s3:PutObject"] * 830 + ["kms:Decrypt"] * 4200 + ["sqs:SendMessage"] * 90

used = set(used_log)
unused = sorted(granted - used)
print(f"granted {len(granted)} actions, used {len(used)} in 90 days")
print("never used:", ", ".join(unused))
print(f"{len(unused) / len(granted) * 100:.0f}% of the permissions could be removed")

risky = [a for a in unused if a.startswith("iam:") or a.endswith("Terminate" + "Instances")]
print("most dangerous unused ones:", ", ".join(risky))
print("\nSuggested policy actions:", sorted(used))
''')

K.code('cidr_exposure', r'''
# How many addresses can reach our admin ports? Overlapping rules must not be counted twice.
import ipaddress

rules = [
    ("10.0.0.0/24", 22),          # office network may use SSH
    ("10.0.0.128/25", 22),        # a second rule that overlaps the first
    ("203.0.113.0/28", 3389),     # a partner may use Remote Desktop
    ("0.0.0.0/0", 443),           # the website is public, which is fine
]
ADMIN_PORTS = {22, 3389}

admin_nets = [ipaddress.ip_network(cidr) for cidr, port in rules if port in ADMIN_PORTS]
for net in admin_nets:
    print(f"{str(net):16} {net.num_addresses:6} addresses")
merged = list(ipaddress.collapse_addresses(admin_nets))
total = sum(n.num_addresses for n in merged)
print(f"\nafter merging overlaps: {[str(n) for n in merged]} = {total} addresses can reach admin ports")
print(f"if someone writes 0.0.0.0/0 for SSH: {ipaddress.ip_network('0.0.0.0/0').num_addresses} addresses")
''')

K.code('iac_scan', r'''
# Scanning infrastructure as code before it is deployed (the idea behind Checkov, tfsec and KICS)
TERRAFORM = """
resource "aws_s3_bucket_public_access_block" "exports" {
  block_public_acls   = false
  block_public_policy = false
}
resource "aws_security_group_rule" "ssh" {
  type        = "ingress"
  from_port   = 22
  cidr_blocks = ["0.0.0.0/0"]
}
resource "aws_db_instance" "main" {
  storage_encrypted = false
  publicly_accessible = true
}
resource "aws_instance" "web" {
  metadata_options { http_tokens = "optional" }
}
"""

RULES = [
    ("block_public_acls   = false", "S3 public access block is off"),
    ('cidr_blocks = ["0.0.0.0/0"]', "a rule allows the whole internet"),
    ("storage_encrypted = false", "database storage not encrypted"),
    ("publicly_accessible = true", "database reachable from the internet"),
    ('http_tokens = "optional"', "IMDSv2 not required on the instance"),
]

for number, line in enumerate(TERRAFORM.strip().splitlines(), start=1):
    for pattern, message in RULES:
        if pattern in line:
            print(f"line {number:2}: {message}")
print("\nFix these in the pull request, before anything reaches the cloud. That is shifting cloud security left.")
''')

K.lesson('idea', 'What cloud security is, and the shared responsibility model', f'''
{talk('Cloud computing means renting computers, storage and software from a provider such as Amazon Web Services, Microsoft Azure or Google Cloud, instead of buying and running your own. NIST describes three main service models. In infrastructure as a service, IaaS, you rent virtual machines and manage everything on them. In platform as a service, PaaS, the provider also runs the operating system and the platform, such as a managed database, and you bring your code and data. In software as a service, SaaS, you just use finished software such as Microsoft 365 or Gmail. Security in the cloud is shared. The provider secures the buildings, the hardware and the virtualisation layer, often called security of the cloud. You secure what you put in it, called security in the cloud: your data, your user accounts, your settings and, in IaaS, your operating systems. The line moves with the service model, as the animation shows, but your data and your accounts are always yours. Most cloud breaches come from the customer side. In 2019 Gartner predicted that through 2025, 99 percent of cloud security failures would be the customer’s fault. Real cases agree. At Capital One in 2019, a firewall setting and a server side request forgery bug exposed data on about 100 million people. In 2024, attackers logged into about 165 companies’ Snowflake data warehouse accounts with passwords stolen by malware, because those accounts had no MFA. And sometimes the provider slips: in 2023 a group Microsoft calls Storm-0558 used a stolen signing key to forge logins to government email accounts, which a US review board later called a cascade of avoidable errors.')}
{src('NIST SP 800-145 (2011), AWS, Azure and Google Cloud shared responsibility pages, AWS IAM policy evaluation logic, AWS IMDSv2 and KMS documentation, NIST SP 800-38D, CIS cloud benchmarks, CSA Cloud Controls Matrix, US court and Senate records on Capital One (2019), US Cyber Safety Review Board report on Storm-0558 (April 2024), Mandiant report on UNC5537 and Snowflake customers (June 2024), Gartner (2019).')}
{safe('The programs check made up settings and policies. To practise on a real cloud, use a free tier account of your own, turn on billing alerts, and never test against accounts you do not own.')}
{wwh('<b>Cloud security</b> is protecting the data, accounts and services you run on a provider’s platform, under a shared responsibility model.',
     'The cloud is easy to set up and easy to set up wrong. One public storage bucket or one account without MFA can expose millions of records in minutes.',
     'Know your side of the shared model, lock down identities with least privilege and MFA, encrypt with managed keys, scan settings and code continuously, and log every action.')}
{viz('cyshared')}
{table(['Model', 'You manage', 'Provider manages', 'Example'], [
    ['IaaS', 'Data, accounts, apps, OS, network settings', 'Hypervisor, hardware, buildings', 'AWS EC2, Azure Virtual Machines'],
    ['PaaS', 'Data, accounts, apps, some network settings', 'OS, runtime, hardware', 'AWS RDS, Azure App Service, Google App Engine'],
    ['SaaS', 'Data, accounts, sharing settings', 'Almost everything else', 'Microsoft 365, Google Workspace, Salesforce']])}
''', kw=['cloud security', 'shared responsibility', 'IaaS', 'PaaS', 'SaaS', 'NIST SP 800-145', 'security of the cloud', 'security in the cloud', 'Capital One', 'Snowflake', 'Storm-0558', 'Gartner'])

K.lesson('iam', 'Identity is the new perimeter: IAM and least privilege', f'''
{talk('In the cloud, almost everything is controlled through an API, so whoever holds the right identity can change anything from anywhere. That is why people say identity is the new perimeter. Identity and access management, IAM, decides who can do what to which resource. A policy is a list of statements, each saying allow or deny, which actions, and on which resources, often with wildcards like s3:* for every storage action. When a request comes in, AWS checks in a fixed order: if any statement explicitly denies it, the answer is no, whatever else is allowed. Otherwise, if any statement allows it, the answer is yes. Otherwise the default is no. Azure and Google Cloud use similar ideas with their own words. Two habits keep IAM safe. The first is least privilege: give each person and each program only the actions it needs. Over time roles collect permissions nobody uses. The program below compares what a role is granted with what the audit log shows it actually used, the same idea as AWS IAM Access Analyzer, and finds that most permissions can go. The second is to avoid long lived secret keys. People should log in through single sign on with MFA, and programs running in the cloud should use roles that give short lived keys automatically. Long lived access keys in code are one of the most common causes of cloud breaches, because they leak through public repositories, laptops and logs.')}
{viz('cyiam')}
{run('iam_eval')}
{run('least_privilege')}
{fxs(fx('Policy decision', 'decision = Deny if any Deny matches, else Allow if any Allow matches, else Deny', 'An explicit Deny cannot be overridden by any Allow.', key=True),
     fx('Unused permission share', 'unused = (granted &minus; used) / granted', '10 granted, 4 used: 6 / 10 = 60% can be removed.', key=True))}
{note('Protect the root or global admin account with a hardware security key, use it only for the few tasks that need it, and alert on every root login.', 'warn')}
''', kw=['IAM', 'identity and access management', 'policy', 'explicit deny', 'default deny', 'wildcard', 'least privilege', 'IAM Access Analyzer', 'roles', 'short lived credentials', 'access keys', 'root account', 'MFA', 'identity perimeter'])

K.lesson('config', 'Misconfiguration: buckets, firewall rules and the metadata service', f'''
{talk('The second big cause of cloud breaches is a wrong setting. Storage buckets set to public, databases reachable from the internet, firewall rules that let anyone in the world reach port 22 for SSH or 3389 for Remote Desktop, and audit logging switched off. These mistakes are easy to make, because a single tick box changes them, and easy for attackers to find, because they scan the whole internet for open services and guess bucket names all day. A cloud security posture management tool, CSPM, reads all your settings through the provider’s API and checks them against rules such as the CIS Benchmarks, as the program below does in miniature. One special setting deserves its own story. Every cloud server can ask a local address, 169.254.169.254, called the instance metadata service, for the short lived keys of its role. At Capital One in 2019, an attacker found a web app with a server side request forgery bug, made it fetch the metadata address, received the role’s keys, and used them to download data from storage buckets that the role could read. The fixes are layered: fix the bug, require IMDSv2, which needs a session token that a simple forged request cannot get, and give each role access only to its own data, as the animation shows. Address ranges are written as CIDR blocks, such as 10.0.0.0/24, and a little maths tells you how many addresses a rule really opens.')}
{run('cspm_audit')}
{viz('cyimds')}
{run('cidr_exposure')}
{fxs(fx('Addresses in a CIDR block', 'count = 2<sup>32 &minus; prefix</sup>', '/24 is 256 addresses, /20 is 4096, /0 is 4294967296, the whole IPv4 internet.', key=True),
     fx('Chance at least one setting is wrong', 'P = 1 &minus; (1 &minus; p)<sup>n</sup>', '50 buckets each wrong with p = 0.02: P &asymp; 0.636. Automated checks beat hoping.'))}
{attack([
    ['Scans the internet for open SSH, RDP and databases', 'No admin ports open to 0.0.0.0/0, use a bastion or session manager, private subnets'],
    ['Guesses names of public storage buckets', 'Block public access at the account level, CSPM alerts'],
    ['Uses an SSRF bug to read the metadata service', 'Fix SSRF, require IMDSv2, narrow role permissions'],
    ['Logs in with stolen passwords to a SaaS account', 'MFA for every user, conditional access, alerts on new locations']])}
''', kw=['misconfiguration', 'public bucket', 'security group', 'firewall rule', '0.0.0.0/0', 'CSPM', 'CIS Benchmarks', 'instance metadata service', 'IMDSv2', '169.254.169.254', 'SSRF', 'Capital One', 'CIDR'])

K.lesson('data', 'Protecting data: encryption, keys and secrets', f'''
{talk('Cloud providers encrypt data at rest by default today, but who controls the keys matters. Behind the scenes they use envelope encryption. Each file or disk gets its own data key. The data key is then locked with a master key, called a key encryption key, that lives inside the key management service, KMS, in tamper resistant hardware and never leaves it. To read the file, a program sends the locked data key to KMS, which checks the program’s permission, writes a log entry, and returns the unlocked data key. This design has three benefits, shown in the animation. A thief who copies the stored files gets only locked data and a locked key. Every unlock leaves an audit record. And rotating the master key means re locking only the small data keys, not re encrypting terabytes of data. A data key per file also keeps each key well within safe limits, because AES-GCM with random 96 bit nonces should not be used for more than about four billion messages under one key. Customers can choose provider managed keys, customer managed keys in KMS, or keys they bring from their own hardware, trading convenience for control. Passwords, API keys and database credentials, called secrets, belong in a secrets manager such as AWS Secrets Manager, Azure Key Vault or HashiCorp Vault, never in code or configuration files, and they should be rotated regularly.')}
{viz('cyenvelope')}
{run('envelope')}
{fxs(fx('Envelope encryption', 'C = E<sub>DK</sub>(file), stored with W = E<sub>KEK</sub>(DK)', 'Rotation re wraps W only. 10 TB of data with 1000000 data keys of 32 bytes: re wrapping touches 32 MB, 312500 times less.', key=True),
     fx('Random nonce collisions in GCM', 'P &asymp; n<sup>2</sup> / 2<sup>97</sup> for n messages with 96 bit nonces', 'n = 2<sup>32</sup> gives P &asymp; 2<sup>&minus;33</sup>, the limit NIST SP 800-38D sets. A key per file stays far below it.', key=True))}
{table(['Key option', 'Who holds the master key', 'Control', 'Effort'], [
    ['Provider managed', 'Provider, fully automatic', 'Low', 'None'],
    ['Customer managed in KMS', 'Provider hardware, your policies and rotation', 'Medium to high', 'Some'],
    ['Bring or hold your own key', 'Your own hardware security module', 'Highest', 'High, and losing the key loses the data']])}
''', kw=['encryption at rest', 'envelope encryption', 'data key', 'key encryption key', 'KMS', 'HSM', 'key rotation', 'customer managed keys', 'BYOK', 'secrets manager', 'Key Vault', 'Vault', 'GCM nonce limit'])

K.lesson('devsecops', 'Infrastructure as code, containers and monitoring', f'''
{talk('Modern teams create cloud resources with code, called infrastructure as code, using tools such as Terraform, AWS CloudFormation or Bicep. That is good news for security, because settings can be reviewed and scanned before they ever reach the cloud. Scanners such as Checkov, tfsec and KICS read the code and flag public buckets, open ports and missing encryption in the pull request, as the program below shows. Containers and Kubernetes add their own checks: scan images for known vulnerabilities, run containers as a non root user with a read only file system, never run privileged containers, limit what each workload can reach with network policies, and use Kubernetes role based access control. Finally, the cloud must be watched like any network. Turn on audit logs such as AWS CloudTrail, Azure activity logs and Google Cloud audit logs in every account and region, send them to a separate, locked logging account, and alert on dangerous events: root logins, logging turned off, new admin users, keys created, and policies made public. Many tools now bundle these jobs. CSPM checks settings, CWPP protects workloads such as servers and containers, CIEM manages cloud identities and permissions, and a CNAPP, cloud native application protection platform, joins them together.')}
{run('iac_scan')}
{steps('A secure cloud landing zone, step by step', [
    'Separate accounts or subscriptions for production, development, security tooling and logging.',
    'Single sign on with MFA for all people, no long lived access keys, and a locked root account.',
    'Guard rails at the top level: block public storage, deny turning off logging, allow only approved regions.',
    'Audit logs from every account sent to the logging account that nobody else can change.',
    'Infrastructure as code with scanning in every pull request, and CSPM checks on what is running.',
    'Alerts on root logins, new admin users, public resources and keys used from unusual places.'])}
''', kw=['infrastructure as code', 'Terraform', 'CloudFormation', 'Checkov', 'tfsec', 'KICS', 'containers', 'Kubernetes', 'RBAC', 'network policy', 'CloudTrail', 'landing zone', 'CSPM', 'CWPP', 'CIEM', 'CNAPP'])

K.lesson('versus', 'Cloud security tools compared', f'''
{talk('The cloud security market has many short names. They overlap, and many products now combine several. What matters is which question each one answers: are my settings right, are my workloads safe, are my identities too powerful, is my code safe before deployment, and what is happening right now.')}
{versus('Which cloud tool answers which question', ['', 'CSPM', 'CWPP', 'CIEM', 'IaC scanning', 'Cloud audit logs plus SIEM'], [
    ['Question', 'Are my settings right?', 'Are my servers and containers safe?', 'Are identities too powerful?', 'Is the code safe before deploy?', 'What is happening now?'],
    ['Looks at', 'Provider APIs', 'Agents and images', 'Policies and usage logs', 'Terraform, templates', 'Every API call'],
    ['Finds', 'Public buckets, open ports, no MFA', 'Vulnerable packages, malware, runtime attacks', 'Unused and risky permissions', 'Mistakes before they exist', 'Attacks in progress, insider misuse'],
    ['Limit', 'After the fact', 'Needs coverage of every workload', 'Needs good usage data', 'Misses changes made by hand', 'Only as good as the rules']],
    'Scan code before deploy, check settings continuously, trim identities with usage data, protect workloads, and watch the audit logs. A CNAPP can bundle these, but the habits matter more than the brand.')}
''', kw=['comparison', 'CSPM', 'CWPP', 'CIEM', 'CNAPP', 'IaC scanning', 'cloud SIEM'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that the cloud is someone else’s computer and that you still look after your own data and passwords. A student can explain shared responsibility, evaluate IAM policies, count CIDR addresses and describe envelope encryption. A professional builds secure landing zones and runs CSPM and incident response in the cloud. Experts design multi cloud security at scale and research isolation and confidential computing.')}
{ladder(
    '<p>The cloud is someone else’s computer. They lock the building, but you still choose who gets your password and which files are shared.</p>',
    '<p>IaaS, PaaS and SaaS responsibility, IAM evaluation order and least privilege, CIDR counting, public bucket and open port checks, IMDSv2, envelope encryption with KMS, IaC scanning.</p>',
    '<p>Landing zones with guard rails, single sign on and roles everywhere, CSPM and CIEM programmes, cloud incident response with audit logs, Kubernetes hardening, and certifications such as CCSP or AWS Security Specialty.</p>',
    '<p>Formal reasoning about IAM policies (AWS Zelkova uses SMT solvers), confidential computing with hardware enclaves, side channels between tenants, and multi cloud identity federation at scale.</p>')}
{grow('Explain what the provider protects and what you protect.',
      'Evaluate policies, find misconfigurations and explain key management.',
      'Design and run security for a whole cloud estate.')}
''', kw=['beginner', 'expert', 'CCSP', 'AWS Security Specialty', 'Zelkova', 'confidential computing'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Shared responsibility</b>: provider secures the cloud, you secure what is in it. IaaS, PaaS, SaaS move the line, data and accounts stay yours. Capital One 2019, Snowflake 2024, Storm-0558 2023.',
    '<b>IAM</b>: explicit Deny, then Allow, else Deny. Least privilege from usage logs, roles with short lived keys, SSO with MFA, locked root account.',
    '<b>Misconfiguration</b>: public buckets, open admin ports, logging off. CSPM and CIS Benchmarks. CIDR count = 2<sup>32 &minus; prefix</sup>. IMDSv2 plus narrow roles against SSRF.',
    '<b>Data</b>: envelope encryption, data key locked by a KMS master key, logged unlocks, cheap rotation. Secrets in a manager, never in code.',
    '<b>Build and watch</b>: IaC scanning in pull requests, container and Kubernetes hardening, audit logs to a separate account, alerts on risky changes. CSPM, CWPP, CIEM, CNAPP.'],
    'Security Operations 2.3: governance, risk and law, the rules and frameworks that shape security work.')}
{files('Three tasks: CIDR block size, an IAM policy decision, and counting addresses that can reach admin ports.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In SaaS, which of these is always the customer’s job?', ['Patching the servers', 'Data and user accounts', 'Guarding the data centre', 'Replacing hard disks'], 1, 'Always yours.', 'Even in SaaS, who can log in and what is shared is up to you.')
K.quiz('e', 'How many addresses are in a /24 block?', ['24', '256', '1024', '65536'], 1, '2<sup>8</sup>.', '32 &minus; 24 = 8 bits for hosts.')
K.quiz('e', 'Where should an API key for a database live?', ['In the source code', 'In a secrets manager', 'In a public README', 'In an email'], 1, 'Secrets manager.', 'Keys in code leak through repositories and logs.')
K.quiz('e', 'A firewall rule allows port 22 from 0.0.0.0/0. What does that mean?', ['Only the office can use SSH', 'Anyone on the internet can try to log in by SSH', 'SSH is blocked', 'Only cloud staff can connect'], 1, 'Whole internet.', '0.0.0.0/0 covers every IPv4 address.')
K.quiz('m', 'A policy allows s3:GetObject on bucket/* and denies s3:* on bucket/payroll/*. A request reads bucket/payroll/nov.xlsx. Result?', ['Allowed, Allow comes first', 'Denied, an explicit Deny always wins', 'Allowed, wildcards are ignored', 'Error'], 1, 'Deny wins.', 'Order of statements does not matter.')
K.quiz('m', 'What does IMDSv2 add that blocks simple SSRF theft of role keys?', ['A password', 'A session token that must first be fetched with a PUT request and a special header', 'Encryption of the disk', 'A firewall'], 1, 'Token first.', 'A forged simple GET cannot get the token.')
K.quiz('m', 'Why do cloud providers use envelope encryption?', ['It is required by law', 'Per file data keys, logged unlocks through KMS, and cheap master key rotation', 'It makes files smaller', 'It avoids keys'], 1, 'Key locks a key.', 'Rotation re locks only small data keys.')
K.quiz('m', 'What did the 2024 Snowflake customer breaches have in common?', ['A Snowflake software bug', 'Customer accounts with stolen passwords and no MFA', 'Quantum computers', 'Open SSH ports'], 1, 'Identity.', 'Passwords were stolen by infostealer malware on other machines.')
K.quiz('m', 'What does a CSPM tool do?', ['Writes code', 'Reads cloud settings through APIs and flags misconfigurations', 'Encrypts files', 'Replaces the firewall'], 1, 'Posture.', 'It checks against rules such as the CIS Benchmarks.')
K.quiz('h', 'A role is granted 120 actions and used 9 in 90 days. Roughly what share could be removed?', ['7.5%', '92.5%', '50%', '0%'], 1, 'Unused share.', '(120 &minus; 9) / 120 = 0.925.')
K.quiz('h', 'Two SSH rules allow 10.0.0.0/24 and 10.0.0.128/25. How many distinct addresses can reach SSH?', ['384', '256', '128', '512'], 1, 'The /25 is inside the /24.', 'Merging overlaps leaves just the /24.')
K.quiz('h', 'Why should cloud audit logs go to a separate logging account?', ['It is cheaper', 'An attacker with admin in the main account cannot then delete or change them', 'Logs are faster there', 'Providers require it'], 1, 'Out of reach.', 'Turning off logging is a common attacker step.')
K.quiz('h', 'Which cause does Gartner’s 2019 prediction name for almost all cloud security failures through 2025?', ['Provider hardware faults', 'The customer, mostly settings and identities', 'Natural disasters', 'Quantum attacks'], 1, '99%.', 'Shared responsibility in numbers.')
K.quiz('x', 'In the style of a Stanford CS 155 question: with random 96 bit nonces, about what collision chance does GCM reach after 2<sup>32</sup> messages under one key?', ['2<sup>&minus;96</sup>', '2<sup>&minus;33</sup>', '2<sup>&minus;64</sup>', '1/2'], 1, 'Birthday bound.', 'n<sup>2</sup> / 2<sup>97</sup> = 2<sup>64</sup> / 2<sup>97</sup>.')
K.quiz('x', 'In the style of a research question on IAM: how does AWS Zelkova check whether a policy can ever allow public access?', ['By testing random requests', 'By turning policies into logic formulas and asking an SMT solver', 'By asking an engineer', 'By reading CloudTrail'], 1, 'Automated reasoning.', 'It proves properties for every possible request, not just samples.')

K.calc('e', 'How many addresses in a /24 block?', '256', '2<sup>32 &minus; 24</sup>.', ['32 &minus; 24 = 8.', '2<sup>8</sup>.', eq('256')], check=256)
K.calc('e', 'How many addresses does 0.0.0.0/0 cover?', '4294967296', '2<sup>32</sup>.', ['Prefix 0 leaves all 32 bits free.', '2<sup>32</sup>.', eq('4294967296')], check=2 ** 32)
K.calc('e', 'In the IaaS model of the animation, how many of the 8 layers are fully yours?', '5', 'Count the top layers.', ['Data, accounts, application code.', 'Network settings and operating system.', eq('5 layers')], check=5)
K.calc('m', 'How many addresses in a /20 block?', '4096', '2<sup>12</sup>.', ['32 &minus; 20 = 12.', '2<sup>12</sup>.', eq('4096')], check=4096)
K.calc('m', 'A role is granted 120 actions and used 9. What percent is unused?', '92.5', '(granted &minus; used) / granted.', ['120 &minus; 9 = 111.', '111 / 120 = 0.925.', eq('92.5%')], check=92.5)
K.calc('m', '50 buckets, each wrongly set with probability 0.02. Chance at least one is wrong? Round to 4 decimals.', '0.6358', '1 &minus; 0.98<sup>50</sup>.', ['All right: 0.98<sup>50</sup> &asymp; 0.3642.', 'Complement.', eq('&asymp; 0.6358')], check=round(1 - 0.98 ** 50, 4))
K.calc('m', 'Keys must be at most 90 days old. How many rotations in 730 days?', '8', 'Whole 90 day periods.', ['730 / 90 = 8.1.', 'Rotate at days 90, 180, ... 720.', eq('8 rotations')], check=8)
K.calc('m', 'A CSPM runs 40 checks and 31 pass. Pass rate in percent?', '77.5', 'Pass over total.', ['31 / 40.', '= 0.775.', eq('77.5%')], check=77.5)
K.calc('h', '10 TB of data with 1000000 data keys of 32 bytes. How many times fewer bytes does master key rotation touch than re encrypting all data?', '312500', 'Data size over key bytes.', ['Key bytes = 1000000 &times; 32 = 32000000.', '10<sup>13</sup> / 3.2 &times; 10<sup>7</sup>.', eq('312500')], check=312500)
K.calc('h', 'SSH from 10.0.0.0/24 and 10.0.0.128/25, RDP from 203.0.113.0/28. Distinct addresses that reach admin ports?', '272', 'Merge overlaps.', ['The /25 sits inside the /24: 256.', 'The /28 adds 16.', eq('256 + 16 = 272')], check=272)
K.calc('h', 'A request matches one Allow and one Deny statement. What is the decision?', 'Denied', 'Order of checks.', ['Check explicit Deny first.', 'One matches.', eq('Denied')], check='Denied')
K.calc('x', 'GCM with random 96 bit nonces after n = 2<sup>32</sup> messages: P &asymp; n<sup>2</sup> / 2<sup>97</sup>. What is log<sub>2</sub> P?', '-33', 'Exponents.', ['n<sup>2</sup> = 2<sup>64</sup>.', '2<sup>64 &minus; 97</sup>.', eq('&minus;33')], check=-33)
K.calc('x', 'What is the last address of 10.0.16.0/20? Give the third number (octet).', '31', '4096 addresses = 16 blocks of 256.', ['A /20 spans 2<sup>12</sup> = 4096 addresses.', 'That is 16 values of the third octet: 16 to 31.', eq('10.0.31.255, so 31')], check=31)
K.calc('x', 'Each of 3 independent controls (IMDSv2, narrow role, SSRF fix) stops a key theft with probability 0.9. Chance all fail? Round to 4 decimals.', '0.001', '0.1<sup>3</sup>.', ['Each fails with 0.1.', 'All three: 0.1 &times; 0.1 &times; 0.1.', eq('0.001')], check=0.001)

K.assign('cidr_size', 'e', 'Addresses in a CIDR block',
         '<p>Write <code>cidr_size(prefix)</code> that returns how many IPv4 addresses a block with that prefix length has (0 to 32).</p>',
         '''
def cidr_size(prefix):
    # your code here
    pass
''', [('cidr_size(24)', 256), ('cidr_size(32)', 1), ('cidr_size(20)', 4096), ('cidr_size(0)', 4294967296)],
         '''
def cidr_size(prefix):
    return 2 ** (32 - prefix)
''', 'The host part has 32 &minus; prefix bits, and each bit doubles the count.', '<p>Real clouds reserve a few addresses in every subnet (AWS keeps 5), so usable addresses are slightly fewer.</p>')
K.assign('iam_decide', 'm', 'An IAM policy decision',
         '<p>policy is a list of <code>(effect, action, resource)</code> where effect is "Allow" or "Deny" and patterns may use *. Write <code>iam_decide(policy, action, resource)</code> that returns "Deny" if any matching statement is a Deny, "Allow" if any matching statement is an Allow, and "Deny" otherwise. Use <code>fnmatch</code> for the patterns.</p>',
         '''
from fnmatch import fnmatch

def iam_decide(policy, action, resource):
    # your code here
    pass
''', [('iam_decide([("Allow", "s3:GetObject", "b/*")], "s3:GetObject", "b/x")', 'Allow'),
      ('iam_decide([("Allow", "s3:GetObject", "b/*"), ("Deny", "s3:*", "b/pay/*")], "s3:GetObject", "b/pay/n")', 'Deny'),
      ('iam_decide([("Allow", "s3:GetObject", "b/*")], "s3:DeleteObject", "b/x")', 'Deny'),
      ('iam_decide([], "s3:GetObject", "b/x")', 'Deny')],
         '''
from fnmatch import fnmatch

def iam_decide(policy, action, resource):
    allowed = False
    for effect, act, res in policy:
        if fnmatch(action, act) and fnmatch(resource, res):
            if effect == "Deny":
                return "Deny"
            allowed = True
    if allowed:
        return "Allow"
    return "Deny"
''', 'Return Deny as soon as a matching Deny appears. Remember whether any Allow matched.', '<p>Real AWS evaluation also joins service control policies, permission boundaries and resource policies, but each still follows the explicit deny first rule.</p>')
K.assign('admin_exposure', 'h', 'Addresses that can reach admin ports',
         '<p>rules is a list of <code>(cidr, port)</code>. Write <code>admin_exposure(rules)</code> that returns how many distinct IPv4 addresses can reach port 22 or 3389. Overlapping blocks must be counted once (hint: <code>ipaddress.collapse_addresses</code>).</p>',
         '''
import ipaddress

def admin_exposure(rules):
    # your code here
    pass
''', [('admin_exposure([("10.0.0.0/24", 22), ("10.0.0.128/25", 22), ("203.0.113.0/28", 3389), ("0.0.0.0/0", 443)])', 272),
      ('admin_exposure([("0.0.0.0/0", 443)])', 0),
      ('admin_exposure([("10.0.0.0/25", 22), ("10.0.0.128/25", 3389)])', 256),
      ('admin_exposure([("0.0.0.0/0", 22)])', 4294967296)],
         '''
import ipaddress

def admin_exposure(rules):
    nets = []
    for cidr, port in rules:
        if port in (22, 3389):
            nets.append(ipaddress.ip_network(cidr))
    total = 0
    for net in ipaddress.collapse_addresses(nets):
        total += net.num_addresses
    return total
''', 'Keep only admin port rules, merge the networks, then add up their sizes.', '<p>CSPM tools do this across thousands of rules and also follow routes and peering, because a rule is only open if traffic can actually get there.</p>')

K.must('Shared responsibility', 'Provider: buildings, hardware, hypervisor. You: data, accounts, settings, and the OS in IaaS. IaaS, PaaS, SaaS (NIST SP 800-145). Gartner: 99% customer caused. Capital One 2019, Snowflake 2024, Storm-0558 2023.')
K.must('IAM', 'Explicit Deny, then Allow, else Deny. Least privilege from usage (Access Analyzer). Roles with short lived keys, SSO with MFA, no keys in code, hardware key on root.')
K.must('Misconfiguration', 'Public buckets, admin ports to 0.0.0.0/0, logging off. CSPM with CIS Benchmarks. CIDR size 2<sup>32 &minus; prefix</sup>. SSRF to 169.254.169.254: IMDSv2 plus narrow roles.')
K.must('Data and keys', 'Envelope: DK encrypts data, KEK in KMS locks DK. Logged unlocks, cheap rotation. GCM random nonces: about 2<sup>32</sup> messages per key. Provider, customer managed, BYOK. Secrets manager.')
K.must('Build and watch', 'IaC scanning (Checkov, tfsec, KICS). Containers non root, no privileged, network policies, RBAC. Audit logs to a separate account. CSPM, CWPP, CIEM, CNAPP. Landing zones with guard rails.')

T = K.topic(
    slug='cy-cloud', topic='cy-cloud', step=(2, 'Intelligence, cloud and governance', 'cy-o2', 'Learning about attackers before they arrive, securing the cloud, and the rules, risk methods and laws that guide security work.', 'Advanced'),
    title='Cloud security: shared responsibility, identity, settings and keys', short='Cloud security', badge='2.2', minutes=75,
    lead='How to stay safe on AWS, Azure and Google Cloud: the shared responsibility model for IaaS, PaaS and SaaS, IAM policy evaluation and least privilege, the misconfigurations behind most breaches with the Capital One metadata case, envelope encryption with KMS, infrastructure as code scanning, containers and cloud monitoring.',
    desc='cloud security, shared responsibility, IaaS, PaaS, SaaS, IAM, policy evaluation, explicit deny, least privilege, roles, MFA, access keys, misconfiguration, public bucket, security group, CIDR, CSPM, CIS Benchmarks, instance metadata service, IMDSv2, SSRF, Capital One, Snowflake, Storm-0558, encryption at rest, envelope encryption, KMS, key rotation, secrets manager, infrastructure as code, Terraform, Checkov, Kubernetes, CloudTrail, CWPP, CIEM, CNAPP, landing zone',
    summary='Shared responsibility, IAM and least privilege, misconfigurations and IMDSv2, envelope encryption with KMS, IaC scanning and cloud monitoring.',
    keywords=['cloud', 'shared responsibility', 'IAM', 'least privilege', 'CSPM', 'IMDSv2', 'KMS', 'envelope encryption', 'Terraform', 'CloudTrail'],
    recap='<p>Know your side of the line, treat identity as the perimeter, let tools check every setting, lock data with keys you control, and log every call to the cloud.</p>',
    added='2026-11-15')
