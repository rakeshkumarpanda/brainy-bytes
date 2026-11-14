# 1.1 Classical ciphers: Caesar, substitution, Vigenère and the one time pad
# Example "caesar_brute" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The Caesar cipher, and breaking it by trying every key
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def caesar(text, k):
    out = ""
    for ch in text:
        if ch in ABC:
            out = out + ABC[(ABC.index(ch) + k) % 26]
        else:
            out = out + ch            # spaces and punctuation stay as they are
    return out

secret = caesar("MEET AT THE OLD BRIDGE", 3)
print("ciphertext:", secret)
print("decrypted :", caesar(secret, -3))

print("Brute force, all 26 keys:")
for k in range(26):
    print(k, caesar(secret, -k))
