# 1.2 Symmetric encryption: AES, GF(2⁸) and modes of operation
# Example "aes_core" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# AES-128 from scratch, checked against the example in FIPS 197 (Appendix C.1). For learning only.
def xtime(a):                       # multiply by 2 in GF(2^8)
    a = a << 1
    if a & 0x100:
        a = a ^ 0x11B
    return a

def gmul(a, b):                     # multiply two bytes in GF(2^8)
    result = 0
    while b:
        if b & 1:
            result = result ^ a
        a = xtime(a)
        b = b >> 1
    return result

# 3 generates every non zero byte: 3^0, 3^1, ..., 3^254. Log tables then give inverses quickly.
EXP = [1] * 255
for i in range(1, 255):
    EXP[i] = gmul(EXP[i - 1], 3)
LOG = [0] * 256
for i in range(255):
    LOG[EXP[i]] = i

def inverse(a):
    if a == 0:
        return 0
    return EXP[(255 - LOG[a]) % 255]

SBOX = []                           # inverse, then a fixed bit mixing (affine) step, then XOR 0x63
for x in range(256):
    b = inverse(x)
    s = 0x63
    for i in range(8):
        bit = (b >> i) ^ (b >> ((i + 4) % 8)) ^ (b >> ((i + 5) % 8)) ^ (b >> ((i + 6) % 8)) ^ (b >> ((i + 7) % 8))
        s = s ^ ((bit & 1) << i)
    SBOX.append(s)

def sub_bytes(state):
    return [SBOX[v] for v in state]

def shift_rows(state):              # state is 16 bytes, column by column
    out = [0] * 16
    for i in range(16):
        row, col = i % 4, i // 4
        out[i] = state[row + 4 * ((col + row) % 4)]
    return out

def mix_columns(state):
    out = []
    for c in range(4):
        a0, a1, a2, a3 = state[4 * c:4 * c + 4]
        out.append(gmul(a0, 2) ^ gmul(a1, 3) ^ a2 ^ a3)
        out.append(a0 ^ gmul(a1, 2) ^ gmul(a2, 3) ^ a3)
        out.append(a0 ^ a1 ^ gmul(a2, 2) ^ gmul(a3, 3))
        out.append(gmul(a0, 3) ^ a1 ^ a2 ^ gmul(a3, 2))
    return out

def add_round_key(state, key):
    return [state[i] ^ key[i] for i in range(16)]

def expand_key(key):                # 11 round keys of 16 bytes from one 16 byte key
    keys = [list(key)]
    rcon = 1
    for r in range(1, 11):
        prev = keys[-1]
        t = [SBOX[prev[13]] ^ rcon, SBOX[prev[14]], SBOX[prev[15]], SBOX[prev[12]]]
        new = []
        for i in range(16):
            if i < 4:
                new.append(prev[i] ^ t[i])
            else:
                new.append(prev[i] ^ new[i - 4])
        keys.append(new)
        rcon = xtime(rcon)
    return keys

def encrypt_block(block, key):
    keys = expand_key(key)
    state = add_round_key(list(block), keys[0])
    for r in range(1, 11):
        state = sub_bytes(state)
        state = shift_rows(state)
        if r < 10:                  # the last round has no MixColumns
            state = mix_columns(state)
        state = add_round_key(state, keys[r])
    return bytes(state)

key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
plain = bytes.fromhex("00112233445566778899aabbccddeeff")
cipher = encrypt_block(plain, key)
print("S-box of {53}:", hex(SBOX[0x53]), "(FIPS 197 says 0xed)")
print("ciphertext   :", cipher.hex())
print("FIPS 197 says: 69c4e0d86a7b0430d8cdb78070b4c55a")
print("match:", cipher.hex() == "69c4e0d86a7b0430d8cdb78070b4c55a")
