# 1.3 Wireless security: from WEP to WPA3
# Example "wpa2_psk" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
