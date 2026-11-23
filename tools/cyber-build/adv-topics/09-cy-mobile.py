# Advanced 4.2: mobile security. Checked against the Android security documentation (application sandbox, runtime
# permissions from Android 6.0 in 2015, one time permissions in Android 11, approximate location in Android 12,
# network security configuration and user CAs from Android 7.0, APK signature schemes, Google Play Protect, Android
# Keystore and StrongBox, verified boot), the Apple Platform Security Guide (Secure Enclave, code signing, Data
# Protection, App Tracking Transparency in iOS 14.5, Lockdown Mode in iOS 16), the OWASP Mobile Top 10 (2024), OWASP
# MASVS and MASTG, Aviv et al. and Uellenbeck et al. on Android unlock patterns (389,112 patterns), Citizen Lab on
# Pegasus and FORCEDENTRY (2021), Zimperium on Stagefright (2015), public reports on Joker and Anatsa droppers on
# Google Play, and RBI and Google actions against predatory instant loan apps in India (2021 to 2023).
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq, scene
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, show
from cykit import talk, attack, safe

chapter('cy-mobile')
K = Kit()

K.code('permission_audit', r'''
# Read an Android style manifest and flag permissions that do not fit what the app says it does
import xml.etree.ElementTree as ET          # fine for this fixed text. For files from strangers use defusedxml

MANIFEST = """
<manifest package="com.example.torch">
  <uses-permission name="android.permission.CAMERA"/>
  <uses-permission name="android.permission.READ_CONTACTS"/>
  <uses-permission name="android.permission.READ_SMS"/>
  <uses-permission name="android.permission.ACCESS_FINE_LOCATION"/>
  <uses-permission name="android.permission.INTERNET"/>
</manifest>
"""

DANGEROUS = {"CAMERA", "READ_CONTACTS", "READ_SMS", "RECEIVE_SMS", "ACCESS_FINE_LOCATION",
             "RECORD_AUDIO", "READ_CALL_LOG", "READ_MEDIA_IMAGES"}
NEEDED = {"torch": {"CAMERA"}, "maps": {"ACCESS_FINE_LOCATION", "INTERNET"}, "chat": {"INTERNET", "CAMERA", "RECORD_AUDIO", "READ_CONTACTS"}}

def audit(xml, purpose):
    root = ET.fromstring(xml)
    perms = {p.get("name").split(".")[-1] for p in root.iter("uses-permission")}
    extra = sorted(p for p in perms if p in DANGEROUS and p not in NEEDED[purpose])
    return root.get("package"), sorted(perms), extra

pkg, perms, extra = audit(MANIFEST, "torch")
print("package:", pkg)
print("asks for:", ", ".join(perms))
print("dangerous and unexplained for a torch:", ", ".join(extra) if extra else "none")
print("risk score:", len(extra), "of", len(DANGEROUS), "dangerous permissions beyond its purpose")
''')

K.code('apk_hash', r'''
# Why a repackaged app cannot pass as an update: the signature covers a hash of every byte
import hashlib
import hmac

def digest(app_bytes):
    return hashlib.sha256(app_bytes).hexdigest()

# a stand in for a real signature: only the holder of the key can produce the tag
DEV_KEY = b"developer signing key kept in a hardware module"
ATTACKER_KEY = b"some other key"

def sign(app_bytes, key):
    return hmac.new(key, app_bytes, hashlib.sha256).hexdigest()

def install_update(app_bytes, tag, installed_key):
    expected = sign(app_bytes, installed_key)
    return "installed" if hmac.compare_digest(expected, tag) else "REFUSED: not signed by the same key"

real = b"BrainyBank v2.1: login, balance, transfer"
evil = real + b", send_sms_to_attacker()"
print("real app hash :", digest(real)[:32])
print("evil app hash :", digest(evil)[:32])

print("genuine update           ->", install_update(real, sign(real, DEV_KEY), DEV_KEY))
print("evil app, old signature  ->", install_update(evil, sign(real, DEV_KEY), DEV_KEY))
print("evil app, attacker key   ->", install_update(evil, sign(evil, ATTACKER_KEY), DEV_KEY))
print("\nReal Android signing uses RSA, ECDSA or Ed25519 public key signatures (APK scheme v2 and later),")
print("so the phone needs only the public key. HMAC is used here to keep the example short.")
''')

K.code('lock_maths', r'''
# How strong is a phone lock? PINs, patterns, passwords and the lockout that saves weak ones
import math

def bits(n):
    return math.log2(n)

def count_patterns():
    # Android 3 x 3 pattern: 4 to 9 dots, no dot twice, cannot jump over an unused dot
    skip = {}
    for a, b, mid in [(1, 3, 2), (4, 6, 5), (7, 9, 8), (1, 7, 4), (2, 8, 5), (3, 9, 6), (1, 9, 5), (3, 7, 5)]:
        skip[(a, b)] = skip[(b, a)] = mid
    def walk(cur, used, length):
        if length == 1:
            return 1
        total = 0
        for nxt in range(1, 10):
            if nxt in used:
                continue
            mid = skip.get((cur, nxt))
            if mid and mid not in used:
                continue
            total += walk(nxt, used | {nxt}, length - 1)
        return total
    return sum(walk(s, {s}, L) for L in range(4, 10) for s in range(1, 10))

patterns = count_patterns()
for name, n in [("4 digit PIN", 10 ** 4), ("6 digit PIN", 10 ** 6), ("Android pattern", patterns),
                ("8 character password, 62 symbols", 62 ** 8)]:
    print(f"{name:34s} {n:>16,}  = {bits(n):5.1f} bits")

# with 10 tries before the phone wipes, the chance of guessing a random 6 digit PIN
print(f"\nchance to guess a random 6 digit PIN in 10 tries: {10 / 10 ** 6:.5%}")
# but people pick patterns: in studies, a large share start in the top left corner and use few dots
print("real choices are far from random, so avoid birthdays, 123456 and simple L or Z patterns")
''', long=True)

K.code('pin_check', r'''
# Certificate pinning: compare the hash of the server's public key with a value built into the app
import base64
import hashlib

def spki_pin(public_key_bytes):
    return base64.b64encode(hashlib.sha256(public_key_bytes).digest()).decode()

BANK_KEY = b"bank.example public key bytes (real apps hash the DER encoded SubjectPublicKeyInfo)"
BACKUP_KEY = b"bank.example backup key, kept offline for rotation"
PINS = {spki_pin(BANK_KEY), spki_pin(BACKUP_KEY)}      # always pin a backup key too

def connect(presented_key, chain_trusted):
    if not chain_trusted:
        return "refused: certificate chain not trusted"
    if spki_pin(presented_key) not in PINS:
        return "refused: public key does not match the pin"
    return "connected"

print("pin of the real key:", spki_pin(BANK_KEY)[:24], "...")
print("home Wi-Fi, real certificate        ->", connect(BANK_KEY, chain_trusted=True))
print("café Wi-Fi, fake cert, user CA      ->", connect(b"attacker key", chain_trusted=True))
print("after the bank rotates to backup key ->", connect(BACKUP_KEY, chain_trusted=True))
''')

K.code('storage_scan', r'''
# Insecure data storage: scan an app's files for secrets that should never sit in plain text
import re

app_files = {
    "shared_prefs/settings.xml": '<string name="theme">dark</string><string name="auth_token">eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYXNoYSJ9.x1</string>',
    "files/log.txt": "2026-11-22 10:01 login ok user=asha password=Summer@2026",
    "databases/cache.db": "card=4111111111111111 exp=12/29",
    "res/config.json": '{"api_key": "AKIAEXAMPLEKEY123456", "region": "ap-south-1"}',
}

RULES = [
    ("JSON web token", r"eyJ[\w-]+\.[\w-]+\.[\w-]+"),
    ("password in a log", r"password=\S+"),
    ("card number", r"\b(?:\d[ -]?){13,16}\b"),
    ("cloud access key", r"AKIA[0-9A-Z]{16}"),
]

for path, text in app_files.items():
    hits = [name for name, rx in RULES if re.search(rx, text)]
    print(f"{path:28s} {'; '.join(hits) if hits else 'clean'}")

print("\nFix: keep tokens in the Android Keystore or iOS Keychain, never log passwords,")
print("never store card numbers, and keep cloud keys on the server, not inside the app.")
''')

NSC = '''
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <base-config cleartextTrafficPermitted="false" />
  <domain-config>
    <domain includeSubdomains="true">bank.example</domain>
    <pin-set expiration="2027-06-01">
      <pin digest="SHA-256">7HIpactkIAq2Y49orFOOQKurWxmmSFZhBCoQYcRhJ3Y=</pin>
      <pin digest="SHA-256">fwza0LRMXouZHRC8Ei+4PyuldPDcf3UKgO/04cDM1oE=</pin>
    </pin-set>
  </domain-config>
</network-security-config>
'''

# ------------------------------------------------------------------------------------------------ lessons
K.lesson('idea', 'Why phones need their own security', f'''
{talk('Your phone is probably the most personal computer you own. It goes everywhere with you, it holds your photos, chats, contacts and location history, it has a camera, a microphone and GPS, and in India it is also your bank, your UPI wallet and the place your OTPs arrive. That makes it a prize for attackers. But phones were also designed with more security from the start than desktop computers. Both Android, from Google, and iOS, from Apple, run every app in its own sandbox, a locked room where it can see only its own files. Apps must ask permission to reach anything outside, such as contacts or the camera. Every app must be signed by its developer, and both systems encrypt the storage and protect keys in special hardware. Most mobile attacks therefore do not break these walls. They trick the user into opening a door: installing a fake app from a link, granting permissions that make no sense, typing a password into a fake page, or never updating the phone. A smaller group of very advanced attacks, such as the Pegasus spyware, do break through the walls, and we will see how even those are defended. This chapter goes layer by layer, from the sandbox to the network, and ends with the OWASP list of the ten most common mistakes in mobile apps.')}
{src('Android security documentation, Apple Platform Security Guide, OWASP Mobile Top 10 (2024), OWASP MASVS and MASTG, Uellenbeck et al. (2013), Citizen Lab (2021), Zimperium (2015), public reports on Joker, Anatsa and predatory loan apps, RBI advisories.')}
{wwh('<b>Mobile security</b> protects phones and tablets, the apps on them and the data they hold, from theft, malware, spying and fraud.',
     'Phones hold money, identity, OTPs, location and private conversations, are easy to lose, and connect to untrusted Wi-Fi every day.',
     'Sandboxing and permissions, signed apps from reviewed stores, hardware backed encryption and keys, a strong lock screen, fast updates, careful users, and app developers who follow the OWASP mobile guidance.')}
{table(['Threat', 'Example', 'Main defence'], [
    ['Malicious or over curious apps', 'Torch apps reading SMS, predatory loan apps copying contacts', 'Permissions, store review, user care'],
    ['Fake apps and repackaged apps', 'Banking trojans installed from a link', 'App signing, official stores, Play Protect'],
    ['Lost or stolen phone', 'Thief opens the banking app', 'Lock screen, encryption, remote wipe'],
    ['Network interception', 'Fake café Wi-Fi', 'TLS, certificate pinning, no user installed profiles'],
    ['Advanced spyware', 'Pegasus zero click exploits', 'Fast updates, Lockdown Mode, reboots'],
    ['SIM swap', 'Attacker moves your number to their SIM', 'App based MFA or passkeys instead of SMS']])}
''', kw=['mobile security', 'Android', 'iOS', 'smartphone', 'sandbox', 'mobile threats', 'UPI', 'OTP', 'lost phone'])

K.lesson('sandbox', 'The sandbox and permissions: least privilege in your pocket', f'''
{talk('On Android every app gets its own Linux user ID, so the kernel itself keeps apps apart, and on iOS every app lives in its own container directory with strict rules. Inside the sandbox an app can do what it likes with its own files. To reach anything outside, the camera, microphone, contacts, messages, location or photos, it must hold a permission. Before Android 6.0 in 2015, apps listed all their permissions at install time, and tapping Install granted every one. Nobody read the list. Now both systems ask at the moment the app first needs something, and you can say no. Newer versions go further: Android 11 added one time permissions that expire when you close the app, Android 12 and iOS 14 let you share an approximate location instead of an exact one, and you can share a few chosen photos instead of the whole gallery. Apple’s App Tracking Transparency, from iOS 14.5 in 2021, makes apps ask before tracking you across other companies’ apps. The rule for users is simple. Ask whether the permission makes sense for what the app does. A torch needs the camera flash and nothing else. In India, fake instant loan apps asked for contacts and photos, then used them to shame and threaten borrowers’ families, which led the RBI to warn the public and Google to tighten its rules for loan apps and remove thousands of them.')}
{viz('cysandbox')}
{run('permission_audit')}
{table(['Permission change', 'When', 'What it gives users'], [
    ['Runtime permissions', 'Android 6.0 (2015), iOS from early versions', 'Ask at first use, allow or deny each one'],
    ['Background location asked separately', 'Android 10 (2019), iOS 13', 'Location only while the app is open'],
    ['One time permissions', 'Android 11 (2020)', 'Access ends when you leave the app'],
    ['Approximate location', 'iOS 14 (2020), Android 12 (2021)', 'A rough area instead of your exact spot'],
    ['App Tracking Transparency', 'iOS 14.5 (2021)', 'Apps must ask before tracking across other apps'],
    ['Photo picker', 'iOS 14, Android 13 and later', 'Share chosen photos, not the whole gallery']])}
{note('Check your phone’s privacy dashboard (Android Settings, Security and privacy, or iOS Settings, Privacy and Security) once a month and remove permissions apps no longer need.')}
''', kw=['app sandbox', 'Linux user ID', 'container', 'permissions', 'runtime permissions', 'Android 6.0', 'one time permission', 'approximate location', 'App Tracking Transparency', 'photo picker', 'privacy dashboard', 'loan apps', 'least privilege'])

K.lesson('signing', 'App signing, app stores and fake apps', f'''
{talk('Every Android and iOS app is signed by its developer. The developer keeps a private key and signs a hash covering every byte of the app. The phone remembers which key signed the installed version, and it accepts an update only if it is signed by the same key. That is what stops an attacker from replacing your real banking app with a repackaged copy that has hidden malware, which the animation shows with real SHA-256 hashes. On iPhones, apps normally come only from Apple’s App Store, where Apple reviews them and signs them, although the European Union now requires Apple to allow other stores there. On Android you can install apps from outside the Play Store, called sideloading, but only after allowing it for a particular app. Signing does not stop a brand new fake app signed with the attacker’s own key. Attackers send links saying "download the new bank app", "install this to receive your parcel" or "your electricity bill app", and some even get malware into the official store. The Joker family hid in ordinary looking apps on Google Play for years and secretly signed users up for paid subscriptions. Banking trojans such as Anatsa were delivered by harmless looking PDF reader apps that later downloaded the real malware. Google Play Protect scans apps on and off the store and can disable known malware. The user’s best defences are to install from the official store, check the developer name and reviews, and never allow installs from unknown sources because a message asked you to.')}
{viz('cysigning')}
{run('apk_hash')}
{attack([
    ('Send a link to a fake bank or delivery app', 'Install only from the official store, never enable unknown sources for a link'),
    ('Repackage a real app with hidden code', 'Signature check: updates must come from the original signing key'),
    ('Publish a harmless dropper that downloads malware later', 'Store scanning, Play Protect, and apps that ask for accessibility access without reason are a red flag'),
    ('Abuse accessibility features to read the screen and tap buttons', 'Grant accessibility only to genuine assistive apps, recent Android versions restrict it for sideloaded apps'),
    ('Steal the developer’s signing key', 'Keep signing keys in hardware security modules or Play App Signing')])}
''', kw=['app signing', 'APK signature', 'signing key', 'repackaged app', 'sideloading', 'unknown sources', 'App Store review', 'Google Play Protect', 'Joker malware', 'Anatsa', 'dropper', 'accessibility abuse', 'Play App Signing'])

K.lesson('device', 'Locks, encryption and the hardware that guards keys', f'''
{talk('What protects your data when the phone itself is stolen? First, the storage is encrypted. Modern Android uses file based encryption and iPhones use a system Apple calls Data Protection, and in both the keys are tied to your lock screen passcode and to secret values inside a special chip. On iPhones that chip is the Secure Enclave. On Android it is a trusted execution environment, and on many newer phones a separate security chip called StrongBox, which holds keys that never leave the chip. Because the keys live in hardware, a thief cannot copy the encrypted storage and guess your passcode on a fast computer. Every guess has to go through the chip, which slows guesses down and can wipe the phone after ten wrong tries if you enable that setting. That is why even a six digit PIN is reasonably strong on a phone, while the same PIN would be weak on a website without limits. The program counts the options: a 4 digit PIN has 10,000 choices, a 6 digit PIN has a million, and the Android pattern grid has 389,112 possible patterns. But people do not choose randomly. Many patterns start in the top left corner and use few dots, and the most common PINs are things like 123456. Biometrics such as fingerprint and face unlock are convenient and are matched inside the secure hardware too, but the passcode remains the master key. Finally, turn on Find My Device or Find My iPhone so you can lock or wipe a lost phone remotely.')}
{run('lock_maths')}
{fxs(fx('Choices for an n digit PIN', '10<sup>n</sup>', '6 digits: 1,000,000 = about 19.9 bits.', key=True),
     fx('Chance of guessing in k tries', 'k / N for a random choice', '10 tries on a random 6 digit PIN: 10 / 10<sup>6</sup> = 0.001%.', key=True),
     fx('Android unlock patterns', '389,112 patterns of 4 to 9 dots', 'About 18.6 bits, less than a random 6 digit PIN, and far less as people really choose them.'))}
{table(['Protection', 'Android', 'iPhone'], [
    ['Storage encryption', 'File based encryption, keys tied to the lock screen', 'Data Protection classes, keys tied to the passcode'],
    ['Key hardware', 'TEE and StrongBox, Android Keystore', 'Secure Enclave, Keychain'],
    ['Guess limits', 'Hardware enforced delays, optional wipe', 'Escalating delays, optional wipe after 10 tries'],
    ['Boot integrity', 'Verified Boot checks each stage', 'Secure boot chain from the Boot ROM'],
    ['Lost phone', 'Find My Device', 'Find My iPhone, Activation Lock']])}
''', kw=['device encryption', 'file based encryption', 'Data Protection', 'Secure Enclave', 'TEE', 'StrongBox', 'Android Keystore', 'Keychain', 'lock screen', 'PIN', 'unlock pattern', '389,112', 'biometrics', 'verified boot', 'remote wipe', 'Find My'])

K.lesson('network', 'Phones on hostile networks: TLS and certificate pinning', f'''
{talk('Phones join many networks we do not control: airport Wi-Fi, café hotspots, hotel networks. HTTPS with TLS, from the cryptography section, already protects most traffic, because the app checks that the server’s certificate is signed by a trusted certificate authority. The weak spot is the list of trusted authorities. If an attacker can get their own certificate authority added to your phone, for example by convincing you to install a "Wi-Fi profile" or a "security certificate" on a captive portal page, then their fake certificates look valid. Since Android 7 in 2016, apps ignore user installed authorities by default unless the developer opts in, which removed much of this risk. Banking and payment apps often go one step further with certificate pinning. The app contains the hash of the bank’s own public key, and it refuses to connect to any server whose key does not match, whoever signed the certificate. The animation shows all three cases. Pinning has a cost. If the bank changes its key without updating the app, the app stops working, so good apps pin a backup key as well and plan their rotations carefully. For users the advice is simple: never install profiles or certificates that a Wi-Fi page asks for, keep apps updated, and use mobile data for banking if a network seems odd.')}
{viz('cypinning')}
{show('Pinning in an Android network security configuration', NSC, {3: 'Refuse plain HTTP for the whole app.', 6: 'An expiry date stops the app breaking forever if the pins become out of date.', 7: 'The main key pin.', 8: 'A backup key pin, so the bank can rotate keys.'}, lang='xml')}
{run('pin_check')}
''', kw=['public Wi-Fi', 'man in the middle', 'TLS', 'certificate authority', 'user installed CA', 'Wi-Fi profile', 'Android 7', 'network security configuration', 'certificate pinning', 'SPKI pin', 'backup pin', 'key rotation', 'cleartext traffic'])

K.lesson('advanced', 'Spyware, zero click attacks and SIM swaps', f'''
{talk('A few attacks go straight through the walls. In 2015 researchers at Zimperium found Stagefright, a set of bugs in Android’s media library that could be triggered by a video sent in an MMS, putting an estimated 950 million phones at risk. It pushed Google to start monthly Android security updates. The most famous spyware is Pegasus, sold by the Israeli company NSO Group to governments. In 2021 the Citizen Lab at the University of Toronto found an exploit it named FORCEDENTRY, which infected iPhones through a booby trapped file sent over iMessage. The victim did not need to tap anything, which is why it is called zero click. Once inside, Pegasus could read messages, switch on the microphone and track location. Reports that year, called the Pegasus Project, listed possible targets in many countries, including India. Apple patched the bug and in 2022 added Lockdown Mode, which switches off many complex features for people at high risk, such as journalists and activists. A very different attack needs no software at all: the SIM swap. The attacker convinces or bribes a mobile shop to move your number to a new SIM, then receives your OTPs. Defences include a SIM lock PIN, carrier account PINs, and moving important accounts from SMS codes to an authenticator app or passkeys. For everyone, the most important habit is to install updates promptly and restart the phone now and then, which removes some kinds of spyware that cannot survive a reboot.')}
{table(['Attack', 'Year', 'How it got in', 'Defence'], [
    ['Stagefright', '2015', 'Malformed video in an MMS, parsed automatically', 'Monthly patches, media code moved into tighter sandboxes'],
    ['Pegasus FORCEDENTRY', '2021', 'Zero click file over iMessage', 'Fast updates, BlastDoor sandbox, Lockdown Mode'],
    ['Stalkerware', 'Ongoing', 'Installed by someone with access to the phone', 'Lock screen, check device admin and accessibility apps'],
    ['SIM swap', 'Ongoing', 'Number moved to an attacker’s SIM', 'SIM PIN, carrier PIN, app based MFA or passkeys'],
    ['Juice jacking claims', 'Ongoing warnings', 'Data over public USB charging ports', 'Use your own charger, charge only cables, phones ask before data access']])}
{note('If you think a phone has spyware, do not try to investigate it yourself first. Back it up, update it, and contact a professional or a digital security helpline. Organisations such as Amnesty Tech and Access Now help people at risk.', 'warn')}
''', kw=['Stagefright', 'Pegasus', 'NSO Group', 'FORCEDENTRY', 'zero click', 'Citizen Lab', 'Pegasus Project', 'Lockdown Mode', 'stalkerware', 'SIM swap', 'SIM PIN', 'juice jacking', 'security updates'])

K.lesson('owasp', 'Building safer apps: the OWASP Mobile Top 10', f'''
{talk('So far we have looked at the phone. Now let us look at the app, from the developer’s side. The OWASP foundation, which also publishes the web Top 10, keeps a Mobile Top 10 list of the most common risks in mobile apps, last updated in 2024, and a full checklist called MASVS with a testing guide called MASTG. The commonest real problems are surprisingly basic. Apps store tokens, passwords or card numbers in plain files, write secrets to logs, or ship secret keys for cloud services inside the app, where anyone can unpack the app and read them. The program scans a pretend app for exactly these mistakes. The fixes are well known: keep tokens in the Android Keystore or the iOS Keychain, keep secret keys on your server and give the app short lived tokens instead, use HTTPS everywhere, check every input that comes from outside the app, including links that open the app, and treat everything inside the app as visible to an attacker, because it is. Obfuscation and root or jailbreak detection can slow attackers down but must never be the main protection. Finally, the supply chain matters. Most apps include many third party libraries and advertising kits, and some of those have collected data the app developer never intended to share.')}
{run('storage_scan')}
{table(['OWASP Mobile Top 10 (2024)', 'What goes wrong', 'Fix'], [
    ['M1 Improper credential usage', 'Keys and passwords built into the app', 'Keep secrets on the server, short lived tokens'],
    ['M2 Inadequate supply chain security', 'Unsafe third party libraries and kits', 'Review and update dependencies, lock versions'],
    ['M3 Insecure authentication and authorisation', 'Checks done only in the app, not on the server', 'Enforce every check on the server'],
    ['M4 Insufficient input and output validation', 'Trusting deep links, intents and server data', 'Validate everything that crosses a boundary'],
    ['M5 Insecure communication', 'Plain HTTP, accepting any certificate', 'TLS everywhere, pinning for sensitive apps'],
    ['M6 Inadequate privacy controls', 'Collecting or leaking more personal data than needed', 'Collect less, ask clearly, follow the DPDP Act and GDPR'],
    ['M7 Insufficient binary protections', 'Easy to reverse engineer or tamper with', 'Obfuscation and integrity checks as extra layers'],
    ['M8 Security misconfiguration', 'Debug mode, exported components, backups on', 'Secure defaults, review the manifest'],
    ['M9 Insecure data storage', 'Secrets in plain files, logs or databases', 'Keystore, Keychain, encrypted storage, no secrets in logs'],
    ['M10 Insufficient cryptography', 'Old algorithms, hard coded keys, home made crypto', 'Platform crypto libraries, keys in hardware']])}
''', kw=['OWASP Mobile Top 10', 'MASVS', 'MASTG', 'insecure data storage', 'hard coded secrets', 'Keystore', 'Keychain', 'deep links', 'exported components', 'obfuscation', 'root detection', 'jailbreak', 'third party SDK', 'DPDP Act'])

K.lesson('versus', 'Android and iOS security compared', f'''
{talk('People often ask which phone is more secure. Both are very strong when kept up to date. They make different trade offs between openness and control.')}
{versus('Android and iOS security', ['', 'Android', 'iOS'], [
    ['App sources', 'Play Store plus optional sideloading', 'App Store (other stores only in some regions)'],
    ['Sandbox', 'Per app Linux user ID, SELinux', 'Per app container, strict entitlements'],
    ['Key hardware', 'TEE, StrongBox on many phones', 'Secure Enclave on every recent iPhone'],
    ['Updates', 'Monthly bulletins, speed depends on the phone maker', 'Directly from Apple to all supported iPhones'],
    ['High risk users', 'Advanced Protection settings, Pixel hardware', 'Lockdown Mode'],
    ['Biggest real world risk', 'Old unpatched phones and sideloaded fake apps', 'Phishing and, rarely, targeted spyware']],
    'The phone that gets updates and whose owner refuses unknown apps and odd permissions is the secure one. Buy a phone with a long update promise and install updates promptly.')}
''', kw=['Android versus iOS', 'SELinux', 'entitlements', 'update policy', 'Advanced Protection'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner keeps the phone updated, uses a strong lock and installs apps only from the official store. A student understands sandboxes, permissions, signing and encryption. A professional builds and tests apps against MASVS and manages company phones. Experts research mobile exploits, spyware detection and platform defences.')}
{ladder(
    '<p>Lock your phone, update it, install apps only from the official store, deny permissions that make no sense, and never install profiles or apps that a message asks you to.</p>',
    '<p>Sandbox and per app IDs, runtime permissions, signing and update rules, file based encryption and hardware keys, PIN and pattern maths, TLS and pinning, OWASP Mobile Top 10.</p>',
    '<p>Test apps with MASTG, manage company phones with mobile device management, design pinning with backup keys, keep secrets on the server, and respond to lost devices.</p>',
    '<p>Research exploit chains and sandbox escapes, forensic detection of spyware (as Citizen Lab and Amnesty Tech do), and new platform defences such as memory tagging.</p>')}
{grow('Keep your own phone safe and spot fake apps.',
      'Explain how phones isolate apps and protect data.',
      'Build, test and manage mobile apps and fleets securely.')}
''', kw=['beginner', 'expert', 'mobile device management', 'MDM', 'memory tagging'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Why</b>: phones hold money, identity, OTPs and location, and join untrusted networks daily.',
    '<b>Sandbox and permissions</b>: per app isolation, runtime permissions (Android 6.0, 2015), one time and approximate access, App Tracking Transparency. Least privilege, loan app abuse.',
    '<b>Signing</b>: updates must match the installed app’s key, repackaged apps fail, new fake apps need user caution. Joker, Anatsa, Play Protect.',
    '<b>Device</b>: file based encryption, Secure Enclave, TEE and StrongBox, guess limits. 10<sup>n</sup> PINs, 389,112 patterns.',
    '<b>Network</b>: TLS, user CAs ignored since Android 7, certificate pinning with backup pins.',
    '<b>Advanced</b>: Stagefright 2015, Pegasus FORCEDENTRY 2021, Lockdown Mode, SIM swaps. Update promptly.',
    '<b>Apps</b>: OWASP Mobile Top 10 (2024), secrets in Keystore or Keychain, nothing secret inside the app.'],
    'Advanced 4.3: IoT and industrial control security, where the computers run cameras, factories and power grids.')}
{files('Three tasks: flag extra permissions, compare a certificate pin, and count PIN guesses.')}
''', kw=['summary', 'recap'])

# ------------------------------------------------------------------------------------------------ quiz
K.quiz('e', 'A torch app asks to read your SMS messages. What should you do?', ['Allow it', 'Deny it, a torch has no reason to read messages', 'Uninstall your SMS app', 'Restart the phone'], 1, 'Least privilege.', 'Permissions should match what the app does.')
K.quiz('e', 'Where is the safest place to install apps from?', ['A link in a WhatsApp message', 'The official app store, checking the developer name', 'Any website', 'A Bluetooth file from a stranger'], 1, 'Reviewed and signed.', 'Fake apps mostly spread through links.')
K.quiz('e', 'Why should you install phone updates quickly?', ['They change the wallpaper', 'They fix security holes that attackers already know about', 'They free memory', 'They are optional'], 1, 'Patches.', 'Most attacks use bugs that already have fixes.')
K.quiz('e', 'A café Wi-Fi page asks you to install a security certificate to get online. You should', ['Install it', 'Refuse and use mobile data instead', 'Install it only once', 'Share it with friends'], 1, 'Trusted authorities.', 'A user installed CA can let the network read your traffic.')
K.quiz('m', 'What does the app sandbox do?', ['Speeds up apps', 'Keeps each app’s files and memory separate from other apps', 'Encrypts the network', 'Hides the app icon'], 1, 'A locked room.', 'On Android each app gets its own Linux user ID.')
K.quiz('m', 'Why can an attacker not ship a repackaged app as an update to your real app?', ['Stores do not allow updates', 'The update must be signed with the same key as the installed app', 'Apps cannot be changed', 'The phone checks the icon'], 1, 'Signing keys.', 'The attacker does not have the developer’s private key.')
K.quiz('m', 'Why is a 6 digit PIN reasonably strong on a phone but weak on a website without limits?', ['Phones use bigger digits', 'Hardware on the phone limits and delays guesses and can wipe after 10 tries', 'Websites store PINs in plain text', 'It is not'], 1, 'Guess limits.', 'Every guess must go through the secure chip.')
K.quiz('m', 'What does certificate pinning check?', ['The Wi-Fi password', 'That the server’s public key matches a value built into the app', 'The phone model', 'The app version'], 1, 'Public key hash.', 'Even a certificate from a trusted CA is refused if the key does not match.')
K.quiz('m', 'Which defence best protects against SIM swap attacks on your accounts?', ['A longer SMS', 'Using an authenticator app or passkeys instead of SMS codes', 'Turning off Wi-Fi', 'A new phone case'], 1, 'Do not depend on the number.', 'A SIM swap gives the attacker your SMS codes.')
K.quiz('h', 'What made the Pegasus FORCEDENTRY exploit "zero click"?', ['It needed one click', 'It infected the phone through a file sent over iMessage without any tap', 'It used Bluetooth', 'It required physical access'], 1, 'No interaction.', 'Citizen Lab found it in 2021.')
K.quiz('h', 'Since Android 7, which certificate authorities do apps trust by default?', ['All, including user installed ones', 'Only system CAs, unless the app opts in to user CAs', 'None', 'Only Google'], 1, 'Network security configuration.', 'This blocks the fake profile trick for most apps.')
K.quiz('h', 'Which OWASP Mobile risk covers a cloud access key found inside an app?', ['M5 Insecure communication', 'M1 Improper credential usage', 'M7 Binary protections', 'M4 Input validation'], 1, 'Credentials in the app.', 'Keep secrets on the server.')
K.quiz('h', 'Why should pinned apps include a backup pin?', ['To double the speed', 'So the server can change keys without breaking the app', 'Because one pin is illegal', 'To support Wi-Fi'], 1, 'Key rotation.', 'Without it, a key change locks every user out.')
K.quiz('x', 'In the style of a Stanford CS 155 question: how many bits of strength does a random 6 digit PIN have?', ['6', 'About 19.9', '24', '64'], 1, 'log<sub>2</sub> 10<sup>6</sup>.', '6 &times; 3.32 &asymp; 19.93.')
K.quiz('x', 'In the style of an IIIT Hyderabad mobile security exam: why are Android unlock patterns weaker in practice than their 389,112 count suggests?', ['The count is wrong', 'People choose a small set of common shapes and starting corners', 'Patterns are stored in plain text', 'Patterns cannot be locked'], 1, 'Human choice.', 'Real entropy is far below log<sub>2</sub> 389,112.')

# ------------------------------------------------------------------------------------------------ problems
K.calc('e', 'Choices for a 4 digit PIN?', '10000', '10<sup>4</sup>.', ['Each digit has 10 options.', '10 &times; 10 &times; 10 &times; 10.', eq('10,000')], check=10 ** 4)
K.calc('e', 'Chance to guess a random 4 digit PIN in 10 tries, as a percentage?', '0.1', '10 / 10,000.', ['10 / 10,000 = 0.001.', '&times; 100.', eq('0.1%')], check=10 / 10 ** 4 * 100)
K.calc('e', 'A torch app asks for 5 permissions and needs only 1. How many should you deny?', '4', '5 &minus; 1.', ['Keep the camera.', 'Deny the rest.', eq('4')], check=4)
K.calc('m', 'Bits of strength of a random 6 digit PIN? Round to 2 decimals.', '19.93', 'log<sub>2</sub> 10<sup>6</sup>.', ['6 &times; log<sub>2</sub> 10.', 'log<sub>2</sub> 10 &asymp; 3.3219.', eq('&asymp; 19.93')], check=round(math.log2(10 ** 6), 2))
K.calc('m', 'Bits for the 389,112 Android patterns? Round to 2 decimals.', '18.57', 'log<sub>2</sub>.', ['log<sub>2</sub> 389,112.', '2<sup>18</sup> = 262,144, 2<sup>19</sup> = 524,288.', eq('&asymp; 18.57')], check=round(math.log2(389112), 2))
K.calc('m', 'An 8 character password from 62 symbols. Bits? Round to 1 decimal.', '47.6', '8 &times; log<sub>2</sub> 62.', ['log<sub>2</sub> 62 &asymp; 5.954.', '&times; 8.', eq('&asymp; 47.6')], check=round(8 * math.log2(62), 1))
K.calc('m', 'A pin is SHA-256 of a public key. How many bits long is it?', '256', 'SHA-256 output.', ['32 bytes.', '&times; 8.', eq('256 bits')], check=256)
K.calc('h', 'Base64 length of a 32 byte pin, including padding?', '44', '4 &times; &lceil;n / 3&rceil;.', ['&lceil;32 / 3&rceil; = 11.', '4 &times; 11.', eq('44 characters')], check=4 * math.ceil(32 / 3))
K.calc('h', 'A phone delays guesses by 1 hour after the first 9. How many hours to try all 6 digit PINs at worst? (Ignore wipe)', '999991', 'Every guess after 9 costs an hour.', ['10<sup>6</sup> guesses in all.', 'The first 9 are free.', eq('999,991 hours, about 114 years')], check=10 ** 6 - 9)
K.calc('h', 'Stagefright put about 950 million phones at risk. Suppose 70% were patched within a year. How many million stay exposed?', '285', '30% of 950.', ['1 &minus; 0.7 = 0.3.', '0.3 &times; 950.', eq('285 million')], check=round(0.3 * 950))
K.calc('x', 'With a wipe after 10 tries, the chance an attacker opens a phone whose owner used one of the 20 most common 6 digit PINs (assume those 20 cover 10% of users, evenly). Round to 3 decimals.', '0.05', '10 of the 20 common PINs.', ['Each common PIN covers 0.1 / 20 = 0.005 of users.', 'Trying the top 10 covers 10 &times; 0.005.', eq('0.05, one phone in twenty')], check=round(10 * 0.1 / 20, 3))

# ------------------------------------------------------------------------------------------------ assignments
K.assign('extra_perms', 'e', 'Flag unnecessary permissions',
         '<p>Write <code>extra(asked, needed)</code> that returns a sorted list of permissions in <code>asked</code> that are not in <code>needed</code>.</p>',
         '''
def extra(asked, needed):
    # your code here
    pass
''', [('extra(["CAMERA", "READ_SMS", "READ_CONTACTS"], ["CAMERA"])', ['READ_CONTACTS', 'READ_SMS']), ('extra(["CAMERA"], ["CAMERA"])', []), ('extra([], ["INTERNET"])', [])],
         '''
def extra(asked, needed):
    return sorted(set(asked) - set(needed))
''', 'A set difference does it in one line.', '<p>App review teams and tools like the permission audit program do this at scale, then ask developers to justify every extra permission.</p>')
K.assign('pin_match', 'm', 'Check a certificate pin',
         '<p>Write <code>pin_ok(key_bytes, pins)</code> that computes the base64 encoded SHA-256 of <code>key_bytes</code> and returns True if it is in the set <code>pins</code>.</p>',
         '''
import base64
import hashlib

def pin_ok(key_bytes, pins):
    # your code here
    pass
''', [('pin_ok(b"bank", {base64.b64encode(hashlib.sha256(b"bank").digest()).decode()})', True),
      ('pin_ok(b"attacker", {base64.b64encode(hashlib.sha256(b"bank").digest()).decode()})', False),
      ('pin_ok(b"backup", {base64.b64encode(hashlib.sha256(b"bank").digest()).decode(), base64.b64encode(hashlib.sha256(b"backup").digest()).decode()})', True)],
         '''
import base64
import hashlib

def pin_ok(key_bytes, pins):
    pin = base64.b64encode(hashlib.sha256(key_bytes).digest()).decode()
    return pin in pins
''', 'hashlib.sha256(...).digest() gives bytes. base64.b64encode(...).decode() gives the string form.', '<p>The third test is the backup pin at work: the bank rotated to its backup key and the app kept working.</p>')
K.assign('guess_hours', 'h', 'How long does a brute force take?',
         '<p>A phone allows <code>free</code> guesses with no delay, then makes every further guess wait <code>delay</code> seconds. Write <code>worst_hours(digits, free, delay)</code> that returns the worst case time in hours to try every PIN of that many digits, rounded to 1 decimal.</p>',
         '''
def worst_hours(digits, free, delay):
    # your code here
    pass
''', [('worst_hours(4, 5, 30)', 83.3), ('worst_hours(6, 9, 3600)', 999991.0), ('worst_hours(4, 10000, 30)', 0.0)],
         '''
def worst_hours(digits, free, delay):
    total = 10 ** digits
    slow = max(0, total - free)
    return round(slow * delay / 3600, 1)
''', 'Count all PINs, subtract the free guesses (not below zero), multiply by the delay and convert seconds to hours.', '<p>Even a 4 digit PIN takes days with a 30 second delay. Delays plus an optional wipe are what make short PINs workable on phones.</p>')

K.must('Why mobile is special', 'Phones hold money, OTPs, identity and location, are easily lost and join untrusted networks. Both Android and iOS were built with sandboxing, permissions, signing and hardware keys.')
K.must('Sandbox and permissions', 'Per app Linux user ID or container. Runtime permissions from Android 6.0 (2015), one time (Android 11), approximate location (iOS 14, Android 12), App Tracking Transparency (iOS 14.5). Deny what makes no sense.')
K.must('Signing and stores', 'Updates must be signed by the installed app’s key. Repackaged apps fail, brand new fake apps need user caution. Sideloading, Play Protect, Joker, Anatsa droppers, accessibility abuse.')
K.must('Device protection', 'File based encryption and Data Protection, Secure Enclave, TEE, StrongBox, Keystore, Keychain. Guess limits and wipe. PIN 10<sup>n</sup>, 389,112 patterns (18.6 bits), human choice is weaker. Find My.')
K.must('Network', 'TLS, user installed CAs ignored by default since Android 7, certificate pinning of the public key hash with a backup pin. Never install Wi-Fi profiles from a portal.')
K.must('Advanced threats', 'Stagefright (2015, about 950 million phones), Pegasus FORCEDENTRY zero click (2021), Lockdown Mode (iOS 16), stalkerware, SIM swaps. Update and reboot.')
K.must('OWASP Mobile Top 10 (2024)', 'M1 credentials, M2 supply chain, M3 authentication, M4 validation, M5 communication, M6 privacy, M7 binary protection, M8 misconfiguration, M9 data storage, M10 cryptography. MASVS and MASTG.')

T = K.topic(
    slug='cy-mobile', topic='cy-mobile', step=(4, 'Beyond the web', 'cy-a4', 'Security for people, phones, connected devices, industrial systems and the APIs that link them.', 'Advanced'),
    title='Mobile security: sandboxes, permissions, signing and the OWASP Mobile Top 10', short='Mobile security', badge='4.2', minutes=80,
    lead='How phones keep apps apart and data safe, and how attackers get around that: sandboxes and permissions, app signing and fake apps, lock screens, encryption and secure hardware, café Wi-Fi and certificate pinning, spyware and SIM swaps, and the OWASP Mobile Top 10 for app developers.',
    desc='mobile security, Android, iOS, app sandbox, permissions, runtime permissions, App Tracking Transparency, app signing, sideloading, Play Protect, fake apps, Joker, Anatsa, loan apps, device encryption, Secure Enclave, StrongBox, Keystore, Keychain, PIN, unlock pattern, biometrics, certificate pinning, network security configuration, user CA, Stagefright, Pegasus, zero click, Lockdown Mode, SIM swap, OWASP Mobile Top 10, MASVS, MASTG',
    summary='Sandboxes and permissions, signing and fake apps, device encryption and lock maths, TLS and pinning, spyware and SIM swaps, and the OWASP Mobile Top 10.',
    keywords=['mobile security', 'Android', 'iOS', 'permissions', 'app signing', 'certificate pinning', 'Secure Enclave', 'Pegasus', 'SIM swap', 'OWASP Mobile Top 10'],
    recap='<p>Update the phone, lock it well, install only from the official store, give apps only the permissions their job needs, and as a developer keep every secret off the device.</p>',
    added='2026-11-22')
