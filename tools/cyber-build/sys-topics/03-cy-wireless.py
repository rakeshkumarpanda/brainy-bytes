# Network and Systems 1.3: wireless security. Checked against IEEE 802.11-1997 (WEP), Borisov, Goldberg and Wagner
# (2001), Fluhrer, Mantin and Shamir (2001), Tews, Weinmann and Pyshkin (2007), IEEE 802.11i (2004, PBKDF2 test
# vector H.4), Viehbock (WPS, 2011), Vanhoef and Piessens (KRACK, 2017), Steube (PMKID, 2018), Vanhoef and Ronen
# (Dragonblood, 2019), Wi-Fi Alliance WPA3 specification, RFC 8110 (OWE) and Antonioli et al. (KNOB, 2019).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-wireless')
K = Kit()

K.code('wep_flaws', r'''
# Why WEP failed: a 24 bit IV repeats quickly, a repeated keystream leaks plaintext, and CRC-32 is not a MAC
import math
import random
import zlib

def rc4(key, n):                         # RC4 keystream, the cipher WEP used
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = []
    for _ in range(n):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) % 256])
    return bytes(out)

root_key = b"\x13\x37\xc0\xde\x42"      # the shared 40 bit WEP key, the same for every packet

# 1. Birthday paradox: how soon does a random 24 bit IV repeat?
N = 2 ** 24
print("packets for a 50% chance of a repeated IV:", round(math.sqrt(2 * math.log(2) * N)))
rng = random.Random(7)
seen, count = set(), 0
while True:
    iv = rng.randrange(N)
    count += 1
    if iv in seen:
        break
    seen.add(iv)
print("this run saw its first repeat after", count, "packets")

# 2. Same IV means same keystream, and XOR of two ciphertexts is XOR of the two plaintexts
iv = b"\x00\x00\x2a"
ks = rc4(iv + root_key, 32)
p1, p2 = b"GET /bank/login HTTP/1.1  ", b"user=asha&pin=4821&go=yes "
c1 = bytes(a ^ b for a, b in zip(p1, ks))
c2 = bytes(a ^ b for a, b in zip(p2, ks))
leak = bytes(a ^ b for a, b in zip(c1, c2))
print("attacker who guesses p1 recovers p2:", bytes(a ^ b for a, b in zip(leak, p1)))

# 3. CRC-32 is linear: flip bits in the message and fix the checksum without the key
msg = b"pay 0100 to bob"
crc = zlib.crc32(msg)
delta = bytes(a ^ b for a, b in zip(msg, b"pay 9900 to eve"))
fixed_crc = crc ^ zlib.crc32(delta) ^ zlib.crc32(bytes(len(msg)))
print("forged message passes the CRC check:", fixed_crc == zlib.crc32(b"pay 9900 to eve"))
''', long=True)

K.code('wpa2_psk', r'''
# WPA2-Personal: how the pass phrase becomes keys, and why a captured handshake allows offline guessing
import hashlib
import hmac

def pmk(passphrase, ssid):              # 802.11i: PBKDF2-HMAC-SHA1, 4096 rounds, 256 bits
    return hashlib.pbkdf2_hmac("sha1", passphrase.encode(), ssid.encode(), 4096, 32)

print("802.11i test vector, 'password' on SSID 'IEEE':")
print("  ", pmk("password", "IEEE").hex())

def prf(key, label, data, nbytes):      # the 802.11i pseudo random function built on HMAC-SHA1
    out = b""
    i = 0
    while len(out) < nbytes:
        out += hmac.new(key, label + b"\x00" + data + bytes([i]), hashlib.sha1).digest()
        i += 1
    return out[:nbytes]

def ptk(pmk_, ap_mac, sta_mac, anonce, snonce):
    data = min(ap_mac, sta_mac) + max(ap_mac, sta_mac) + min(anonce, snonce) + max(anonce, snonce)
    return prf(pmk_, b"Pairwise key expansion", data, 48)    # KCK 16 + KEK 16 + TK 16 bytes

# A pretend capture of the 4 way handshake (everything here is sent in the clear)
ap, sta = bytes.fromhex("020000000001"), bytes.fromhex("020000000002")
anonce, snonce = hashlib.sha256(b"a").digest(), hashlib.sha256(b"s").digest()
eapol = b"EAPOL message 2 contents"
real = ptk(pmk("sunflower77", "CafeNet"), ap, sta, anonce, snonce)
mic = hmac.new(real[:16], eapol, hashlib.sha1).digest()[:16]   # message 2 carries this MIC

# Offline dictionary attack: no more contact with the network is needed
wordlist = ["password", "12345678", "cafenet123", "sunflower77", "letmein1"]
for guess in wordlist:
    k = ptk(pmk(guess, "CafeNet"), ap, sta, anonce, snonce)
    if hmac.new(k[:16], eapol, hashlib.sha1).digest()[:16] == mic:
        print("pass phrase found offline:", guess)
        break
print("defence: a long random pass phrase, or WPA3-SAE, which removes offline guessing")
''', long=True)

K.code('wps_pin', r'''
# Why WPS PINs fall in hours: the router checks the two halves of the PIN separately (Viehbock, 2011)
def checksum(pin7):                      # the last digit of a WPS PIN is a checksum of the first 7
    accum = 0
    while pin7:
        accum += 3 * (pin7 % 10)
        pin7 //= 10
        accum += pin7 % 10
        pin7 //= 10
    return (10 - accum % 10) % 10

print("PIN 1234567 + checksum ->", f"1234567{checksum(1234567)}")
print("naive guesses for 8 digits:", 10 ** 8)
print("but the 8th digit is a checksum:", 10 ** 7)
print("and the halves are confirmed separately:", 10 ** 4, "+", 10 ** 3, "=", 10 ** 4 + 10 ** 3)
seconds_per_try = 1.5
print(f"at {seconds_per_try} s per try, worst case: {(10 ** 4 + 10 ** 3) * seconds_per_try / 3600:.1f} hours")
print("defence: turn WPS PIN mode off, or use routers that lock out after failures")
''', long=True)

K.code('rogue_ap', r'''
# Spot rogue access points and evil twins in a list of beacons (a pretend Wi-Fi survey)
authorised = {                           # what IT installed: BSSID -> (SSID, security)
    "a0:00:00:00:00:01": ("CorpWiFi", "WPA3-Enterprise"),
    "a0:00:00:00:00:02": ("CorpWiFi", "WPA3-Enterprise"),
    "a0:00:00:00:00:10": ("CorpGuest", "WPA3-SAE"),
}
survey = [                               # (BSSID, SSID, security, signal in dBm)
    ("a0:00:00:00:00:01", "CorpWiFi", "WPA3-Enterprise", -60),
    ("de:ad:be:ef:00:01", "CorpWiFi", "WPA2-PSK", -38),        # same name, stronger, weaker security
    ("a0:00:00:00:00:10", "CorpGuest", "WPA3-SAE", -55),
    ("12:34:56:78:9a:bc", "Printer-Setup", "Open", -70),        # someone plugged in a device AP
    ("a0:00:00:00:00:02", "CorpWiFi", "WPA2-PSK", -58),         # a real AP that was misconfigured
]
our_ssids = {ssid for ssid, sec in authorised.values()}
for bssid, ssid, sec, dbm in survey:
    if bssid in authorised:
        want = authorised[bssid][1]
        verdict = "ok" if sec == want else f"MISCONFIGURED: {sec}, should be {want}"
    elif ssid in our_ssids:
        verdict = "EVIL TWIN: our network name from an unknown radio"
    else:
        verdict = "rogue or neighbour: check where it is"
    print(f"{bssid}  {ssid:14} {sec:16} {dbm:4} dBm -> {verdict}")
''', long=True)

K.lesson('idea', 'Why wireless needs its own security', f'''
{talk('A wired network has a physical boundary: to listen, you must plug in. Radio has no such boundary. Wi-Fi signals pass through walls and into car parks, and anyone with a laptop can record them or transmit their own. So wireless security must do three jobs that cables gave for free: keep outsiders off the network, keep traffic secret from listeners, and let devices know they are talking to the real access point. The history of Wi-Fi security is a lesson in how hard this is. The first scheme, WEP, shipped with the original 802.11 standard in 1997 and was badly broken by 2001. In 2007 the retailer TJX revealed that attackers who first got in through a store’s weak WEP network had stolen about 45 million card numbers. WPA arrived in 2003 as a stopgap, WPA2 in 2004 with AES, and WPA3 in 2018 to fix the offline password guessing that WPA2-Personal allows. Along the way researchers found protocol level attacks such as KRACK in 2017, and Bluetooth has had its own share, such as KNOB in 2019. This chapter walks through each generation, shows the maths that broke WEP, and explains what to configure today.')}
{src('IEEE 802.11-1997, Borisov, Goldberg and Wagner, Intercepting Mobile Communications (MobiCom 2001), Fluhrer, Mantin and Shamir (SAC 2001), Tews, Weinmann and Pyshkin (2007), IEEE 802.11i-2004, Viehböck, Brute forcing Wi-Fi Protected Setup (2011), Vanhoef and Piessens, KRACK (CCS 2017), Vanhoef and Ronen, Dragonblood (IEEE S&amp;P 2020), RFC 8110, Antonioli, Tippenhauer and Rasmussen, KNOB (USENIX Security 2019), Vanhoef, FragAttacks (2021).')}
{safe('Only capture or attack wireless networks you own, in a lab or with written permission. Recording other people’s Wi-Fi traffic or cracking their passwords is illegal in most countries. The programs here use made up handshakes and packets.')}
{wwh('<b>Wireless security</b> protects radio networks: access control (who may join), confidentiality and integrity of frames, and authentication of the network itself.',
     'Radio reaches anyone nearby, so listening and fake access points need no physical access. Weak Wi-Fi has been the first step of large breaches.',
     'Modern Wi-Fi uses WPA3: SAE for home networks, 802.1X with EAP-TLS for enterprises, AES-CCMP or GCMP encryption, and protected management frames.')}
{table(['Generation', 'Year', 'Encryption and integrity', 'Status'], [
    ['WEP', '1997', 'RC4 with 24 bit IV, CRC-32', 'Broken in minutes, never use'],
    ['WPA (TKIP)', '2003', 'RC4 with per packet keys, Michael MIC', 'Deprecated'],
    ['WPA2 (802.11i)', '2004', 'AES-CCMP', 'Still common, PSK allows offline guessing'],
    ['WPA3', '2018', 'AES-CCMP or GCMP, SAE, protected management frames', 'Current, required for Wi-Fi 6 certification'],
    ['Wi-Fi Enhanced Open (OWE)', '2018', 'Unauthenticated Diffie-Hellman for open networks', 'Encrypts café Wi-Fi without a password']])}
''', kw=['wireless security', 'Wi-Fi', 'WEP', 'WPA', 'WPA2', 'WPA3', 'TJX breach', 'OWE', 'Enhanced Open', '802.11'])

K.lesson('wep', 'How WEP broke', f'''
{talk('WEP encrypted each frame with RC4, using a key made of a 24 bit initialisation vector, sent in the clear, followed by the shared secret key. It added a CRC-32 checksum as an integrity check. Almost every design choice failed. First, 24 bits gives only about 16.8 million IVs, and by the birthday paradox a randomly chosen IV is likely to repeat after about 4800 packets, which a busy access point sends in seconds. When an IV repeats, the RC4 keystream repeats, and XORing two ciphertexts cancels the keystream, leaving the XOR of two plaintexts. Network traffic has a lot of predictable content, so this leaks real data. Second, CRC-32 is linear: flipping bits in the message changes the checksum in a predictable way, so an attacker can change a packet and fix the checksum without knowing the key. Nikita Borisov, Ian Goldberg and David Wagner showed these problems in 2001. Third, and worst, Fluhrer, Mantin and Shamir showed in 2001 that RC4 leaks information about its key when the first key bytes are known, as WEP’s IV is, so collecting enough packets reveals the secret key itself. In 2007 the PTW attack needed only about 40000 packets for a 50% chance, under a minute of captured traffic.')}
{viz('cywep')}
{run('wep_flaws')}
{fxs(fx('Birthday bound', 'P(repeat) &asymp; 1 &minus; e<sup>&minus;n&sup2;/(2N)</sup>, 50% at n &asymp; &radic;(2N ln 2) &asymp; 1.177&radic;N', 'N = 2<sup>24</sup>: n &asymp; 1.177 &times; 4096 = 4823 packets.', key=True),
     fx('Keystream reuse', 'c<sub>1</sub> &oplus; c<sub>2</sub> = (p<sub>1</sub> &oplus; k) &oplus; (p<sub>2</sub> &oplus; k) = p<sub>1</sub> &oplus; p<sub>2</sub>', 'Knowing or guessing p<sub>1</sub> gives p<sub>2</sub>. The program recovers a PIN this way.', key=True),
     fx('CRC linearity', 'CRC(a &oplus; b) = CRC(a) &oplus; CRC(b) &oplus; CRC(0)', 'So a bit flip &Delta; in the message is fixed by XORing CRC(&Delta;) &oplus; CRC(0) into the checksum. A checksum is not a MAC.', key=True))}
{note('Lessons from WEP that apply everywhere: never reuse a nonce with a stream cipher, use a keyed MAC (or an AEAD cipher) for integrity, never put known bytes in front of a key for RC4, and have designs reviewed in public before they ship.', 'exam')}
''', kw=['WEP', 'RC4', 'initialisation vector', 'IV reuse', 'birthday paradox', 'keystream reuse', 'CRC-32', 'linearity', 'FMS attack', 'PTW attack', 'Borisov Goldberg Wagner'])

K.lesson('wpa2', 'WPA2: the four way handshake and offline guessing', f'''
{talk('WPA2, standardised as 802.11i in 2004, replaced RC4 with AES in CCM mode, called CCMP, with a 48 bit packet number that counts up and a proper message integrity code. Its key management has two modes. In Personal mode, also called PSK, every device knows the same pass phrase. Both sides turn it into a 256 bit pairwise master key with PBKDF2, using the network name as salt and 4096 rounds of HMAC-SHA1. Then the four way handshake runs. The access point sends a random ANonce, the device replies with its own SNonce, and both mix the master key, both MAC addresses and both nonces into a pairwise transient key. Part of that key signs each handshake message with a MIC. The weakness is that everything in the handshake except the pass phrase is sent in the clear. An attacker who records messages 1 and 2 can test pass phrases at home: for each guess compute the master key, the transient key and the MIC, and compare. Since 2018, Jens Steube’s PMKID attack even works from the first message alone. So WPA2-Personal is only as strong as its pass phrase. In 2017 Mathy Vanhoef found KRACK, which tricks a device into reinstalling a key already in use, resetting its packet counter so nonces repeat. Patches fixed it in clients and access points.')}
{viz('cyhandshake')}
{run('wpa2_psk')}
{wwh('<b>WPA2-Personal</b>: PMK = PBKDF2-HMAC-SHA1(pass phrase, SSID, 4096, 256 bits). The four way handshake derives a fresh PTK per session from the PMK, both MACs and two nonces, then installs keys for CCMP.',
     'It gives strong AES encryption and per session keys, and it is still everywhere, so knowing its limits matters.',
     'PTK = PRF(PMK, "Pairwise key expansion", min(MACs) &#8214; max(MACs) &#8214; min(nonces) &#8214; max(nonces)). The first 16 bytes (KCK) make the MIC on handshake messages.')}
{fxs(fx('Pass phrase to PMK', 'PMK = PBKDF2(HMAC-SHA1, pass phrase, SSID, 4096, 32 bytes)', '802.11i test vector: "password" on SSID "IEEE" gives f42c6fc5...a12e, which the program reproduces.', key=True),
     fx('Cost of a guess', 'about 2 &times; 4096 = 8192 HMAC-SHA1 per PMK (two output blocks)', 'At 10<sup>9</sup> HMAC per second: about 122000 guesses per second. 8 lowercase letters (26<sup>8</sup>) fall in about 20 days, a 20 character random pass phrase never.', key=True),
     fx('Strength of a random pass phrase', 'bits = L &times; log<sub>2</sub>(alphabet)', '20 characters from 62 letters and digits: 20 &times; 5.95 &asymp; 119 bits.'))}
{table(['Attack', 'Year', 'Needs', 'Fix'], [
    ['Offline dictionary on the handshake', '2004 onwards', 'A recorded handshake, a weak pass phrase', 'Long random pass phrase, WPA3-SAE'],
    ['PMKID', '2018', 'Message 1 from the access point only', 'Same as above, disable PMKID caching for PSK'],
    ['WPS PIN brute force', '2011', 'WPS PIN mode on', 'Turn WPS PIN off'],
    ['KRACK (key reinstallation)', '2017', 'Man in the middle position on the channel', 'Patched clients and access points'],
    ['FragAttacks', '2021', 'Nearby attacker, design and implementation flaws in fragmentation', 'Firmware updates']])}
''', kw=['WPA2', '802.11i', 'CCMP', 'PSK', 'PBKDF2', 'PMK', 'PTK', 'four way handshake', 'ANonce', 'SNonce', 'MIC', 'offline dictionary attack', 'PMKID', 'KRACK', 'FragAttacks'])

K.lesson('wps', 'WPS, WPA3 and enterprise Wi-Fi', f'''
{talk('Wi-Fi Protected Setup was meant to make joining easy with an 8 digit PIN. In 2011 Stefan Viehböck showed the design was fatally flawed: the last digit is only a checksum, and the access point tells you separately whether the first four digits and the next three are right. So instead of a hundred million guesses an attacker needs at most eleven thousand, a few hours. Turning WPS PIN mode off is the fix. WPA3, announced in 2018, replaces the pre shared key handshake in Personal mode with SAE, Simultaneous Authentication of Equals, a password authenticated key exchange based on Dan Harkins’ Dragonfly. Each run uses fresh random secrets, so a recording is useless for offline guessing, every guess requires a live attempt, and the resulting key has forward secrecy. WPA3 also requires protected management frames, which stop forged disconnect messages. Vanhoef and Ronen found side channel flaws in early SAE implementations, called Dragonblood, which led to constant time fixes. For organisations, WPA2 and WPA3 Enterprise use 802.1X: each user or device logs in to a RADIUS server through EAP, ideally EAP-TLS with certificates. The critical setting is that devices must check the server certificate. Without that check, an evil twin access point can run a fake RADIUS server and collect password hashes.')}
{viz('cyeviltwin')}
{run('wps_pin')}
{run('rogue_ap')}
{fxs(fx('WPS PIN search', '10<sup>4</sup> + 10<sup>3</sup> = 11000 guesses instead of 10<sup>8</sup>', 'The 8th digit is a checksum (10<sup>7</sup>), and the halves are confirmed separately. At 1.5 s per try: about 4.6 hours.', key=True),
     fx('SAE (simplified)', 'PE = hash to curve(password, MACs), each side sends commit s = r + m and E = &minus;m&middot;PE, then K = r&middot;(s<sub>peer</sub>&middot;PE + E<sub>peer</sub>)', 'Fresh r and m every run: the transcript reveals nothing that can test a password guess offline.'))}
{table(['Setting', 'Home or small office', 'Enterprise'], [
    ['Mode', 'WPA3-Personal (SAE), or WPA2/WPA3 transition', 'WPA3-Enterprise with 802.1X'],
    ['Authentication', 'Long random pass phrase', 'EAP-TLS certificates, or PEAP with server certificate checks enforced'],
    ['Extras', 'WPS off, firmware updated, admin password changed', 'Protected management frames, rogue AP detection, separate guest network'],
    ['Guest or public', 'Separate guest network', 'OWE (Enhanced Open) or a captive portal plus VPN']])}
{note('Bluetooth has its own history: BlueBorne (2017) allowed takeover of unpatched devices over the air, and KNOB (2019) let an attacker force the encryption key of Bluetooth Classic down to one byte of entropy, only 256 possibilities. Keep devices updated and turn Bluetooth off when not needed.', 'warn')}
''', kw=['WPS', 'WPS PIN', 'Viehbock', 'Reaver', 'WPA3', 'SAE', 'Dragonfly', 'forward secrecy', 'Dragonblood', 'protected management frames', '802.11w', '802.1X', 'EAP-TLS', 'PEAP', 'RADIUS', 'evil twin', 'rogue access point', 'Bluetooth', 'BlueBorne', 'KNOB'])

K.lesson('versus', 'Wi-Fi security options compared', f'''
{talk('When an exam or a manager asks which Wi-Fi security to use, the answer depends on who connects. A home needs WPA3-Personal with a strong pass phrase. A company needs Enterprise mode, so each person has their own credentials, leavers can be removed one by one, and a stolen laptop does not reveal a shared key. Public places need encryption without a password, which is what OWE gives. WEP and TKIP should not appear on any network today, and WPA2-Personal is acceptable only with a long random pass phrase.')}
{versus('Wireless security choices', ['', 'WEP', 'WPA2-Personal', 'WPA3-Personal', 'WPA2/3-Enterprise', 'OWE'], [
    ['Encryption', 'RC4, broken', 'AES-CCMP', 'AES-CCMP or GCMP', 'AES-CCMP or GCMP', 'AES-CCMP'],
    ['Authentication', 'Shared key', 'Shared pass phrase', 'Shared password with SAE', 'Per user via 802.1X', 'None'],
    ['Offline guessing', 'Key recovered outright', 'Yes, from one handshake', 'No', 'Depends on EAP method', 'Not applicable'],
    ['Forward secrecy', 'No', 'No', 'Yes', 'With EAP-TLS and fresh keys', 'Yes'],
    ['Use for', 'Nothing', 'Legacy devices, long pass phrase', 'Homes, small offices', 'Organisations', 'Cafés, airports']],
    'Use WPA3: SAE at home, 802.1X with EAP-TLS and enforced server certificate checks at work, and OWE for open networks.')}
''', kw=['comparison', 'WEP', 'WPA2', 'WPA3', 'Enterprise', 'OWE'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner learns to choose WPA3 or WPA2 with a long pass phrase, to turn off WPS, and to be careful on public Wi-Fi. A college student can explain why WEP broke using the birthday paradox, keystream reuse and CRC linearity, describe the four way handshake and why it allows offline guessing, and compute the cost of guessing pass phrases. A masters student studies 802.1X and EAP methods, protected management frames, the security proofs of the four way handshake and why KRACK slipped past them, and SAE as a password authenticated key exchange. Researchers fuzz Wi-Fi and Bluetooth stacks, find design flaws like FragAttacks, analyse side channels in SAE implementations, and model protocols formally with tools such as Tamarin.')}
{ladder(
    '<p>Use WPA3 or WPA2 with a long pass phrase, turn off WPS, update your router, and treat public Wi-Fi as untrusted.</p>',
    '<p>WEP’s IV birthday problem, keystream reuse and CRC linearity, the PBKDF2 and four way handshake maths, offline guessing costs, WPS halves and evil twins.</p>',
    '<p>802.1X and EAP-TLS, PMF, KRACK and the gap between proofs and state machines, SAE and PAKEs, GCMP, rogue AP detection with wireless IDS.</p>',
    '<p>Formal analysis of Wi-Fi protocols, Dragonblood style side channels, stack fuzzing, FragAttacks style design flaws, and Bluetooth key negotiation attacks such as KNOB and BIAS.</p>')}
{grow('Choose the right Wi-Fi settings and explain why.',
      'Compute guessing costs and explain each historic attack.',
      'Analyse handshakes and implementations for subtle flaws.')}
''', kw=['beginner', 'expert', 'Tamarin', 'fuzzing', 'BIAS'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Radio has no walls</b>: wireless security must control access, protect frames and authenticate the network.',
    '<b>WEP</b>: 24 bit IV repeats after about 4823 packets (birthday), keystream reuse leaks p<sub>1</sub> &oplus; p<sub>2</sub>, CRC-32 is linear, FMS and PTW recover the key.',
    '<b>WPA2</b>: AES-CCMP. PMK = PBKDF2(pass phrase, SSID, 4096). Four way handshake gives PTK. A recording allows offline guessing (PMKID too).',
    '<b>Attacks</b>: WPS halves (11000 guesses), KRACK nonce reuse (2017), FragAttacks (2021), evil twins.',
    '<b>WPA3</b>: SAE (Dragonfly) stops offline guessing and gives forward secrecy. PMF required. Dragonblood fixed by constant time code.',
    '<b>Enterprise</b>: 802.1X with EAP-TLS, and always validate the server certificate. OWE for open networks.',
    '<b>Bluetooth</b>: BlueBorne, KNOB (1 byte keys), BIAS. Update and disable when unused.'],
    'Next, Network and Systems 2.1: authentication, from passwords and MFA to passkeys, Kerberos and OAuth.')}
{files('Three tasks: the WPS checksum digit, the IV birthday probability, and finding a WPA2 pass phrase from a PMK with a word list.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which Wi-Fi security should a new home router use?', ['WEP', 'WPA (TKIP)', 'WPA3-Personal, or WPA2 with a long random pass phrase', 'Open with a hidden name'], 2, 'Newest.', 'WEP and TKIP are broken, and hiding the network name does not protect anything.')
K.quiz('e', 'Why is radio harder to protect than a cable?', ['It is slower', 'Anyone nearby can listen and transmit without plugging in', 'It uses more power', 'It has no addresses'], 1, 'No walls.', 'Signals reach car parks and neighbours.')
K.quiz('e', 'What should you do with WPS PIN mode on a router?', ['Leave it on', 'Turn it off', 'Change the PIN daily', 'Share the PIN'], 1, '11000 guesses.', 'The PIN design lets attackers find it in hours.')
K.quiz('e', 'An evil twin is', ['A backup router', 'A fake access point using a real network’s name', 'Two routers on one channel', 'A Bluetooth headset'], 1, 'Same name.', 'Devices join the strongest known name unless the network proves who it is.')
K.quiz('m', 'Why does a repeated WEP IV leak data?', ['The IV is the key', 'Same IV and key give the same RC4 keystream, so XOR of two ciphertexts is XOR of two plaintexts', 'CRC fails', 'Packets get lost'], 1, 'Keystream reuse.', 'Predictable plaintext then reveals the other message.')
K.quiz('m', 'What can an attacker do with a captured WPA2-PSK four way handshake?', ['Nothing', 'Test pass phrase guesses offline until the MIC matches', 'Read traffic immediately', 'Change the SSID'], 1, 'Offline.', 'Everything except the pass phrase is in the clear, so guesses can be checked at home.')
K.quiz('m', 'What is the salt in WPA2’s PBKDF2?', ['A random number', 'The network name (SSID)', 'The MAC address', 'The time'], 1, 'Common names.', 'That is why precomputed tables exist for common SSIDs like "linksys". A unique SSID helps a little, a strong pass phrase helps a lot.')
K.quiz('m', 'What does SAE in WPA3 prevent?', ['Jamming', 'Offline dictionary attacks on a recorded handshake', 'Evil twins on open networks', 'All side channels'], 1, 'PAKE.', 'Fresh secrets mean each guess needs a live attempt.')
K.quiz('m', 'In 802.1X Wi-Fi, what must clients check to stop evil twins?', ['Signal strength', 'The RADIUS server’s certificate and name', 'The channel number', 'The MAC address of the AP'], 1, 'Server identity.', 'Without it, a fake RADIUS server collects login hashes.')
K.quiz('h', 'Why could an attacker fix WEP’s CRC-32 after changing a packet?', ['CRC is secret', 'CRC is linear, so the change to the checksum is computable from the change to the message', 'CRC is encrypted twice', 'RC4 hides it'], 1, 'Linear.', 'CRC(a &oplus; b) = CRC(a) &oplus; CRC(b) &oplus; CRC(0). Integrity needs a keyed MAC.')
K.quiz('h', 'What did KRACK (2017) force a victim to do?', ['Reveal its password', 'Reinstall a key already in use, resetting the packet number so nonces repeat', 'Use WEP', 'Disconnect forever'], 1, 'Reinstallation.', 'Replaying message 3 caused the reset. Nonce reuse breaks CCMP and GCMP guarantees.')
K.quiz('h', 'The WPS PIN has 8 digits. Why are only 11000 guesses needed?', ['PINs are short', 'The last digit is a checksum, and the first 4 and next 3 digits are confirmed separately', 'Routers print the PIN', 'Only even digits are used'], 1, 'Halves.', '10<sup>4</sup> + 10<sup>3</sup> = 11000.')
K.quiz('h', 'What does Wi-Fi Enhanced Open (OWE) give an open café network?', ['Passwords', 'Encryption between each device and the access point using unauthenticated Diffie-Hellman', 'Authentication of the café', 'Free VPN'], 1, 'RFC 8110.', 'Passive listeners are stopped, but an active evil twin is still possible without authentication.')
K.quiz('x', 'In the style of a Berkeley CS 161 question: the four way handshake was proven secure, yet KRACK broke it. Why?', ['The proof was wrong', 'The proof did not model when keys are installed or that message 3 may be retransmitted', 'AES was broken', 'KRACK used quantum computers'], 1, 'Model gap.', 'Proofs cover the model. The state machine in real code had behaviour the model left out.')
K.quiz('x', 'In the style of an IIT Delhi wireless security exam: about how many packets give a 50% chance of a repeated random 24 bit IV?', ['2<sup>24</sup>', 'About 4823', 'About 1000', '2<sup>12</sup> exactly'], 1, '&radic;(2N ln 2).', '1.1774 &times; 2<sup>12</sup> &asymp; 4823.')

K.calc('e', 'How many different 24 bit IVs exist?', '16777216', '2<sup>24</sup>.', ['24 bits.', '2<sup>24</sup> = 16777216.', eq('16777216')], check=2 ** 24)
K.calc('e', 'How many guesses does the WPS halves attack need at most?', '11000', '10<sup>4</sup> + 10<sup>3</sup>.', ['First half: 4 digits.', 'Second half: 3 digits plus the checksum.', eq('11000')], check=10 ** 4 + 10 ** 3)
K.calc('e', '"64 bit WEP" was a 40 bit key plus the IV. How many bits was the IV?', '24', '64 &minus; 40.', ['Only 40 bits were secret.', '64 &minus; 40 = 24.', eq('24 bits')], check=64 - 40)
K.calc('m', 'About how many packets give a 50% chance of a repeated 24 bit IV? Use &radic;(2N ln 2).', '4823', 'N = 2<sup>24</sup>.', ['2N ln 2 = 2 &times; 16777216 &times; 0.693 = 23258000.', '&radic; &asymp; 4823.', eq('about 4823')], check=round((2 * 2 ** 24 * __import__('math').log(2)) ** 0.5))
K.calc('m', 'At 1000 packets per second, how many hours to use every 24 bit IV once? Round to a whole number.', '5', '2<sup>24</sup> / 1000 / 3600.', ['16777 seconds.', '/ 3600 = 4.66.', eq('about 5 hours')], check=round(2 ** 24 / 1000 / 3600))
K.calc('m', 'A PMK costs 8192 HMAC-SHA1 operations. A GPU does 10<sup>9</sup> per second. About how many thousand guesses per second? Round to a whole number.', '122', '10<sup>9</sup> / 8192.', ['10<sup>9</sup> / 8192 = 122070.', 'In thousands.', eq('about 122 thousand')], check=round(1e9 / 8192 / 1000))
K.calc('m', 'At that rate, how many days to try all 8 lowercase letter pass phrases (26<sup>8</sup>)? Round to a whole number.', '20', '26<sup>8</sup> / 122070 / 86400.', ['26<sup>8</sup> = 208827064576.', '/ 122070 = 1710700 s = 19.8 days.', eq('about 20 days')], check=round(26 ** 8 / (1e9 / 8192) / 86400))
K.calc('m', 'WPS halves attack at 1.5 seconds per try: worst case in seconds?', '16500', '11000 &times; 1.5.', ['11000 guesses.', '&times; 1.5 = 16500 s, about 4.6 hours.', eq('16500 s')], check=round(11000 * 1.5))
K.calc('h', 'KNOB forced Bluetooth key entropy down to 1 byte. How many keys must an attacker try?', '256', '2<sup>8</sup>.', ['1 byte = 8 bits.', '2<sup>8</sup> = 256.', eq('256 keys')], check=2 ** 8)
K.calc('h', 'Chance of an IV repeat after 10000 packets with 24 bit IVs, in percent? Round to a whole number.', '95', '1 &minus; e<sup>&minus;n&sup2;/2N</sup>.', ['n&sup2;/2N = 10<sup>8</sup> / 33554432 = 2.98.', '1 &minus; e<sup>&minus;2.98</sup> = 0.949.', eq('about 95%')], check=round(100 * (1 - __import__('math').exp(-1e8 / 2 ** 25))))
K.calc('h', 'A random pass phrase of 20 characters from 62 letters and digits has about how many bits? Round to a whole number.', '119', '20 &times; log<sub>2</sub> 62.', ['log<sub>2</sub> 62 = 5.954.', '&times; 20 = 119.1.', eq('about 119 bits')], check=round(20 * __import__('math').log2(62)))
K.calc('h', 'The CCMP pairwise transient key is KCK + KEK + TK, 16 bytes each. How many bits is it?', '384', '48 bytes.', ['16 &times; 3 = 48 bytes.', '&times; 8 = 384 bits.', eq('384 bits')], check=48 * 8)
K.calc('x', 'The expected number of packets until the first repeated IV is &radic;(&pi;N/2). For N = 2<sup>24</sup>, what is it? Round to a whole number.', '5134', '&radic;(&pi; &times; 2<sup>23</sup>).', ['&pi; &times; 8388608 = 26353589.', '&radic; &asymp; 5134.', eq('about 5134')], check=round((__import__('math').pi * 2 ** 24 / 2) ** 0.5))
K.calc('x', 'CCMP’s 48 bit packet number at 10<sup>6</sup> packets per second: how many years until it wraps? Round to a whole number.', '9', '2<sup>48</sup> / 10<sup>6</sup> / seconds per year.', ['2<sup>48</sup> = 2.81 &times; 10<sup>14</sup>.', '/ 10<sup>6</sup> / 31557600 = 8.9.', eq('about 9 years')], check=round(2 ** 48 / 1e6 / (365.25 * 86400)))

K.assign('wps_checksum', 'e', 'The WPS checksum digit',
         '<p>Write <code>wps_checksum(pin7)</code> for a 7 digit number. Walk from the rightmost digit: add 3 times that digit, then add the next digit once, and repeat. Return (10 &minus; total mod 10) mod 10.</p>',
         '''
def wps_checksum(pin7):
    # your code here
    pass
''', [('wps_checksum(1234567)', 0), ('wps_checksum(1111111)', 5), ('wps_checksum(5551234)', 3)],
         '''
def wps_checksum(pin7):
    accum = 0
    while pin7:
        accum += 3 * (pin7 % 10)
        pin7 //= 10
        accum += pin7 % 10
        pin7 //= 10
    return (10 - accum % 10) % 10
''', 'Use % 10 to take the last digit and //= 10 to drop it, alternating the weights 3 and 1.', '<p>Because this digit is computed, only 10<sup>7</sup> PINs are valid, and the split confirmation cuts the search to 11000.</p>')
K.assign('iv_repeat', 'm', 'Birthday probability for IVs',
         '<p>Write <code>iv_repeat(n, bits)</code> that returns the approximate chance that n random IVs of the given size contain a repeat: 1 &minus; e<sup>&minus;n&sup2;/(2N)</sup> with N = 2<sup>bits</sup>, rounded to 2 decimal places.</p>',
         '''
import math

def iv_repeat(n, bits):
    # your code here
    pass
''', [('iv_repeat(4823, 24)', 0.5), ('iv_repeat(1000, 24)', 0.03), ('iv_repeat(65536, 32)', 0.39)],
         '''
import math

def iv_repeat(n, bits):
    N = 2 ** bits
    return round(1 - math.exp(-n * n / (2 * N)), 2)
''', 'Compute N, then 1 - math.exp(-n * n / (2 * N)), and round.', '<p>For 32 bits, 65536 = &radic;N gives n&sup2;/2N = 1/2, so 1 &minus; e<sup>&minus;0.5</sup> &asymp; 0.39.</p>')
K.assign('find_passphrase', 'h', 'Recover a WPA2 pass phrase from a word list',
         '<p>Write <code>find_passphrase(words, ssid, target_hex)</code>. For each word compute PMK = PBKDF2-HMAC-SHA1(word, ssid, 4096 rounds, 32 bytes) with <code>hashlib.pbkdf2_hmac</code>, and return the first word whose PMK in hex equals <code>target_hex</code>. Return None if no word matches.</p>',
         '''
import hashlib

def find_passphrase(words, ssid, target_hex):
    # your code here
    pass
''', [('find_passphrase(["letmein", "password", "qwerty"], "IEEE", "f42c6fc52df0ebef9ebb4b90b38a5f902e83fe1b135a70e23aed762e9710a12e")', 'password'), ('find_passphrase(["ThisIsAPassword"], "ThisIsASSID", "0dc0d6eb90555ed6419756b9a15ec3e3209b63df707dd508d14581f8982721af")', 'ThisIsAPassword'), ('find_passphrase(["abc"], "IEEE", "00" * 32)', None)],
         '''
import hashlib

def find_passphrase(words, ssid, target_hex):
    for word in words:
        pmk = hashlib.pbkdf2_hmac("sha1", word.encode(), ssid.encode(), 4096, 32)
        if pmk.hex() == target_hex:
            return word
    return None
''', 'hashlib.pbkdf2_hmac("sha1", word.encode(), ssid.encode(), 4096, 32).hex() gives the PMK in hex.', '<p>Both targets are the test vectors from IEEE 802.11i. Real attacks check the handshake MIC instead of the PMK, but the expensive step, PBKDF2 per guess, is the same.</p>')

K.must('Wireless basics', 'Radio has no walls. Jobs: access control, frame protection, network authentication. WEP 1997, WPA 2003, WPA2 2004, WPA3 2018.')
K.must('WEP', '24 bit IV: 50% repeat at &radic;(2N ln 2) &asymp; 4823. c<sub>1</sub> &oplus; c<sub>2</sub> = p<sub>1</sub> &oplus; p<sub>2</sub>. CRC-32 linear. FMS 2001, PTW 2007. TJX breach.')
K.must('WPA2', 'CCMP (AES), 48 bit PN. PMK = PBKDF2-SHA1(pass, SSID, 4096). 4 way handshake: ANonce, SNonce, PTK, MIC. Offline guessing, PMKID 2018.')
K.must('Attacks', 'WPS halves 10<sup>4</sup> + 10<sup>3</sup> = 11000. KRACK 2017 key reinstallation. FragAttacks 2021. Evil twin, deauth (stopped by PMF).')
K.must('WPA3', 'SAE (Dragonfly PAKE): no offline guessing, forward secrecy. PMF required. Dragonblood 2019. OWE for open networks (RFC 8110).')
K.must('Enterprise and BT', '802.1X, RADIUS, EAP-TLS, check the server certificate. Bluetooth: BlueBorne 2017, KNOB 2019 (1 byte keys, 256), BIAS 2020.')

T = K.topic(
    slug='cy-wireless', topic='cy-wireless', step=(1, 'Defending the network', 'cy-s1', 'Network attacks and how to stop them, firewalls, intrusion detection and VPNs, and the security of wireless networks.', 'Intermediate'),
    title='Wireless security: from WEP to WPA3', short='Wireless', badge='1.3', minutes=75,
    lead='Why radio needs its own security and how each generation fared: WEP’s birthday paradox, keystream reuse and linear CRC, WPA2’s PBKDF2 and four way handshake with offline guessing costs worked out, WPS halves, KRACK, WPA3’s SAE, enterprise 802.1X and evil twins, OWE and Bluetooth flaws.',
    desc='wireless security, Wi-Fi security, WEP, RC4, IV reuse, birthday paradox, CRC-32 linearity, FMS attack, PTW attack, WPA, TKIP, WPA2, 802.11i, CCMP, PSK, PBKDF2, PMK, PTK, four way handshake, offline dictionary attack, PMKID, KRACK, FragAttacks, WPS PIN, WPA3, SAE, Dragonfly, Dragonblood, forward secrecy, protected management frames, 802.11w, 802.1X, EAP-TLS, PEAP, RADIUS, evil twin, rogue access point, OWE, Enhanced Open, Bluetooth, BlueBorne, KNOB',
    summary='WEP’s failures, WPA2 handshake and offline guessing, WPS, KRACK, WPA3 SAE, enterprise Wi-Fi, evil twins and Bluetooth.',
    keywords=['WEP', 'WPA2', 'WPA3', 'four way handshake', 'PBKDF2', 'KRACK', 'SAE', 'WPS', 'evil twin', '802.1X'],
    recap='<p>Wi-Fi security moved from a broken design to one that resists offline guessing. Use WPA3, long pass phrases, 802.1X with certificate checks, and keep firmware updated.</p>',
    added='2026-11-15')
