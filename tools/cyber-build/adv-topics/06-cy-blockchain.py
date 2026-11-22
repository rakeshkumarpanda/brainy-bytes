# Advanced 3.1: blockchain security. Checked against Haber and Stornetta, "How to Time-Stamp a Digital Document"
# (J. Cryptology 1991), Merkle (1979, CRYPTO 1987), Nakamoto, "Bitcoin: A Peer-to-Peer Electronic Cash System"
# (31 October 2008, sections 4, 7, 8 and 11), the Bitcoin genesis block (3 January 2009), CVE-2010-5139 (the value
# overflow of block 74638, 15 August 2010), BIP 32 and BIP 39, Eyal and Sirer, "Majority is not Enough" (FC 2014),
# Heilman et al., "Eclipse Attacks on Bitcoin's Peer-to-Peer Network" (USENIX Security 2015), Meiklejohn et al.,
# "A Fistful of Bitcoins" (IMC 2013), the Bitcoin Gold (May 2018) and Ethereum Classic (January 2019, August 2020)
# 51% attack reports, the Ethereum Merge (15 September 2022), the Mt. Gox collapse (February 2014), the WazirX theft
# (July 2024), the Bybit theft (21 February 2025, FBI attribution to North Korea) and the US Department of Justice
# recovery of 63.7 bitcoin of the Colonial Pipeline ransom (June 2021).
import hashlib
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq, scene
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, attack, safe

chapter('cy-blockchain')
K = Kit()

K.code('hash_chain', r'''
# A tiny blockchain: every block stores the SHA-256 fingerprint of the block before it
import hashlib

def block_hash(number, prev, data):
    text = f"{number}|{prev}|{data}"
    return hashlib.sha256(text.encode()).hexdigest()

def make_chain(payments):
    chain = [{"n": 0, "prev": "0" * 64, "data": "genesis"}]
    chain[0]["hash"] = block_hash(0, chain[0]["prev"], "genesis")
    for i, p in enumerate(payments, start=1):
        prev = chain[-1]["hash"]
        chain.append({"n": i, "prev": prev, "data": p, "hash": block_hash(i, prev, p)})
    return chain

def check(chain):
    for i, b in enumerate(chain):
        if b["hash"] != block_hash(b["n"], b["prev"], b["data"]):
            return f"block {i}: its stored hash does not match its contents"
        if i and b["prev"] != chain[i - 1]["hash"]:
            return f"block {i}: the link to block {i - 1} is broken"
    return "valid"

chain = make_chain(["Asha pays Ravi 5", "Ravi pays Meena 2", "Meena pays Arjun 1"])
for b in chain:
    print(b["n"], b["hash"][:16], "<-", b["prev"][:16], "|", b["data"])
print("check:", check(chain))

chain[1]["data"] = "Asha pays Ravi 50"          # a cheater edits an old block
print("after editing block 1:", check(chain))
chain[1]["hash"] = block_hash(1, chain[1]["prev"], chain[1]["data"])   # and fixes its own hash
print("after fixing block 1's hash:", check(chain))
''')

K.code('mine', r'''
# Proof of work: find a nonce so that the hash starts with enough zeros
import hashlib

def mine(data, zeros):
    target = "0" * zeros
    nonce = 0
    while True:
        h = hashlib.sha256(f"{data}|{nonce}".encode()).hexdigest()
        if h.startswith(target):
            return nonce, h
        nonce += 1

for zeros in (1, 2, 3):
    nonce, h = mine("Block 7: Asha pays Ravi 5", zeros)
    print(f"{zeros} zero(s): nonce {nonce:5d} after {nonce + 1:5d} tries (average {16 ** zeros:5d})  {h[:20]}")

# checking is one hash, whatever the difficulty
nonce, h = mine("Block 7: Asha pays Ravi 5", 3)
check = hashlib.sha256(f"Block 7: Asha pays Ravi 5|{nonce}".encode()).hexdigest()
print("anyone can check the work with one hash:", check == h)
''', long=True)

K.code('difficulty', r'''
# How Bitcoin keeps one block about every 10 minutes: the difficulty retarget every 2016 blocks
TARGET_SECONDS = 2016 * 600              # two weeks

def retarget(old_difficulty, actual_seconds):
    # Bitcoin limits one adjustment to a factor of 4 in either direction
    actual = min(max(actual_seconds, TARGET_SECONDS / 4), TARGET_SECONDS * 4)
    return old_difficulty * TARGET_SECONDS / actual

d = 100.0
for days, why in [(14, "on time"), (10, "new machines joined, blocks came fast"),
                  (20, "miners left after a price fall"), (2, "a huge jump, capped at 4 times")]:
    new = retarget(d, days * 86400)
    print(f"2016 blocks took {days:2d} days ({why}): difficulty {d:7.2f} -> {new:7.2f}")
    d = new

# expected hashes for a given number of leading zero bits
for bits in (20, 40, 78):
    print(f"{bits} zero bits: about 2^{bits} = {2 ** bits:.3e} hashes per block")
''')

K.code('merkle_proof', r'''
# A Merkle tree and a proof that one payment is inside the block (Bitcoin pairs an odd last hash with itself)
import hashlib

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def levels(payments):
    L = [[h(p) for p in payments]]
    while len(L[-1]) > 1:
        cur, nxt = L[-1], []
        for i in range(0, len(cur), 2):
            right = cur[i + 1] if i + 1 < len(cur) else cur[i]
            nxt.append(h(cur[i] + right))
        L.append(nxt)
    return L

def proof(L, index):
    path = []
    for level in L[:-1]:
        sib = index ^ 1
        if sib >= len(level):
            sib = index
        path.append((level[sib], "right" if sib >= index else "left"))
        index //= 2
    return path

def verify(payment, path, root):
    cur = h(payment)
    for sib, side in path:
        cur = h(cur + sib) if side == "right" else h(sib + cur)
    return cur == root

pays = ["Asha pays Ravi 5", "Ravi pays Meena 2", "Meena pays Arjun 1", "Arjun pays Zoya 3", "Zoya pays Asha 4"]
L = levels(pays)
root = L[-1][0]
print("Merkle root:", root[:24], "...")
p = proof(L, 2)
print("proof for payment 3 uses", len(p), "hashes:", [s[:8] for s, _ in p])
print("verify real payment :", verify("Meena pays Arjun 1", p, root))
print("verify fake payment :", verify("Meena pays Arjun 100", p, root))
for n in (4, 4000, 1_000_000):
    print(f"{n:>9} payments need about {max(1, (n - 1).bit_length())} hashes in a proof")
''')

K.code('nakamoto', r'''
# The double spend race (Nakamoto 2008, section 11): chance an attacker with share q ever overtakes after z blocks
import math
import random

def attacker_success(q, z):
    p = 1 - q
    if q >= p:
        return 1.0
    lam = z * q / p
    total = 1.0
    for k in range(z + 1):
        poisson = math.exp(-lam) * lam ** k / math.factorial(k)
        total -= poisson * (1 - (q / p) ** (z - k))
    return total

print("q     z=1      z=3      z=6")
for q in (0.1, 0.2, 0.3, 0.45):
    print(f"{q:<5} " + "  ".join(f"{attacker_success(q, z):.5f}" for z in (1, 3, 6)))

def confirmations_needed(q, risk=0.001):
    z = 0
    while attacker_success(q, z) >= risk:
        z += 1
    return z

for q in (0.1, 0.15, 0.25, 0.3):
    print(f"attacker {q:.0%}: wait for {confirmations_needed(q)} blocks to push the risk below 0.1%")

# check one value by simulating many races
random.seed(5)
def race(q, z, give_up=40):
    honest = attacker = 0
    while honest < z:
        if random.random() < q: attacker += 1
        else: honest += 1
    while honest - attacker < give_up:
        if attacker >= honest: return True      # caught up: Nakamoto counts a tie as success
        if random.random() < q: attacker += 1
        else: honest += 1
    return False
wins = sum(race(0.3, 3) for _ in range(4000))
print(f"simulated q=0.3, z=3: {wins / 4000:.3f}   formula: {attacker_success(0.3, 3):.3f}")
''', long=True)

K.code('seed_phrase', r'''
# Why a 12 word recovery phrase is safe, and why a phrase you invent yourself is not (BIP 39 maths)
import hashlib
import math
import secrets

WORDS = 2048                               # BIP 39 has 2048 words, so each word carries 11 bits
for n_words, ent_bits in ((12, 128), (24, 256)):
    checksum = ent_bits // 32
    print(f"{n_words} words = {n_words * 11} bits = {ent_bits} random bits + {checksum} checksum bits")

entropy = secrets.token_bytes(16)          # 128 random bits from the operating system
check = hashlib.sha256(entropy).digest()[0] >> 4           # the first 4 bits of SHA-256
bits = bin(int.from_bytes(entropy, "big"))[2:].zfill(128) + bin(check)[2:].zfill(4)
indices = [int(bits[i:i + 11], 2) for i in range(0, 132, 11)]
print("word numbers (0 to 2047):", len(indices), "words, all below 2048:", all(i < 2048 for i in indices))

guesses_per_second = 1e12
years = 2 ** 128 / guesses_per_second / (3600 * 24 * 365)
print(f"guessing 2^128 at a trillion a second: {years:.2e} years")

# a human chosen 'brain wallet': 4 common words from a 5,000 word vocabulary
human = 5000 ** 4
print(f"4 common words: {math.log2(human):.1f} bits, found in {human / guesses_per_second:.3f} seconds")
''')

K.code('clustering', r'''
# Following the money: the common input heuristic (Meiklejohn et al. 2013) on a made up ledger
# Coins spent together as inputs of one transaction almost always belong to one owner.
txs = [
    {"id": "t1", "inputs": ["A1", "A2"], "outputs": ["S1"]},        # ransom paid to S1
    {"id": "t2", "inputs": ["S1", "S2"], "outputs": ["S3", "X9"]},
    {"id": "t3", "inputs": ["S3"], "outputs": ["EX1"]},             # EX1 is a known exchange deposit address
    {"id": "t4", "inputs": ["B1", "B2", "B3"], "outputs": ["C1"]},
]

parent = {}
def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a
def union(a, b):
    parent[find(a)] = find(b)

for t in txs:
    first = t["inputs"][0]
    for other in t["inputs"][1:]:
        union(first, other)

clusters = {}
for addr in list(parent):
    clusters.setdefault(find(addr), []).append(addr)
for c in clusters.values():
    print("one owner probably controls:", sorted(c))

flows = {o: t["id"] for t in txs for o in t["outputs"]}
print("the ransom wallet S1 shares an owner with S2, and money moved on to exchange address EX1 in", flows["EX1"])
print("exchanges must know their customers, so investigators can ask who owns EX1")
''')

# ------------------------------------------------------------------------------------------------ lessons
K.lesson('idea', 'What a blockchain is, and what it protects', f'''
{talk('Imagine a notebook that the whole village keeps together. Every time someone pays someone, the payment is written on a new page, and every family keeps an identical copy. Nobody can rip out an old page, because everyone else still has it, and every page carries a seal that depends on the page before. That shared notebook is a blockchain. The idea has two parents. In 1991 Stuart Haber and Scott Stornetta showed how to time stamp documents by linking each one to the fingerprint of the one before, and their company later printed those fingerprints every week in the classified adverts of the New York Times so that nobody could quietly change history. Then on 31 October 2008 someone using the name Satoshi Nakamoto published a nine page paper called Bitcoin, a peer to peer electronic cash system. It added the missing piece: a way for strangers on the internet who do not trust each other to agree on one notebook, without a bank in the middle. The first block was mined on 3 January 2009, and it carries a newspaper headline about a bank bailout, a quiet comment on why the system was built. For security people a blockchain is interesting because it protects integrity and availability very strongly, but it gives almost no confidentiality, and the people and programs around it are often the weak point. Most money lost in this world was not lost by breaking the chain. It was lost through stolen keys, buggy programs and tricked people.')}
{src('Haber and Stornetta (1991), Nakamoto (2008), the Bitcoin genesis block (2009), Merkle (1979), Eyal and Sirer (2014), Heilman et al. (2015), Meiklejohn et al. (2013), BIP 32 and BIP 39, public reports on Mt. Gox (2014), Bitcoin Gold (2018), Ethereum Classic (2019, 2020), WazirX (2024) and Bybit (2025).')}
{wwh('A <b>blockchain</b> is a list of records (blocks) shared by many computers, where each block includes the hash of the one before it, and a <b>consensus</b> rule decides which new block everyone accepts next.',
     'It lets people who do not trust each other keep one shared history that nobody can secretly rewrite, without a central bank, court or company keeping the book.',
     'Hash links make old blocks tamper evident, Merkle trees summarise every payment in one hash, digital signatures prove who may spend, and proof of work or proof of stake makes rewriting history very expensive.')}
{table(['Security goal', 'What a public blockchain gives', 'What it does not give'], [
    ['Integrity', 'Very strong: old blocks are linked by hashes and buried under work or stake', 'It cannot tell whether the data was true when it was written'],
    ['Availability', 'Thousands of copies across the world, no single server to switch off', 'Fees rise and payments slow down when the network is busy'],
    ['Confidentiality', 'Almost none: every payment is public forever', 'Names are hidden behind addresses, but addresses can be linked'],
    ['Authentication', 'Only the holder of a private key can sign a spend', 'Lose or leak the key and nobody can help you']])}
{scene('Around you', '<p>When a friend sends you money on UPI, your bank and theirs keep the record and the NPCI system settles it. In Bitcoin there is no bank. Thousands of computers each keep the record, and they agree on it using maths. That is why a lost Bitcoin password cannot be reset by calling customer care.</p>')}
''', kw=['blockchain', 'distributed ledger', 'Haber Stornetta', 'time stamping', 'Satoshi Nakamoto', 'Bitcoin white paper', 'genesis block', 'consensus', 'integrity', 'availability', 'confidentiality'])

K.lesson('chain', 'Blocks and hash links: why old pages cannot be changed', f'''
{talk('Let us build a chain ourselves. A block is a small box of data. In Bitcoin it holds a header of 80 bytes and the list of payments. The header includes the hash of the previous block header. A hash function such as SHA-256, which you met in the hashing chapter, turns any input into a 256 bit fingerprint, and changing even one letter of the input changes about half of the output bits. So if a cheater edits a payment in block 1, the fingerprint of block 1 changes, and block 2, which stored the old fingerprint, no longer matches. Every computer checking the chain spots this in microseconds. Of course the cheater could recompute the fingerprint of block 2 and every later block too. On its own a hash chain only makes tampering visible, it does not make it hard. That is why the next lesson adds work to every block. In the animation the hashes are real SHA-256 values computed in your browser, so try typing your own payments and see every later fingerprint change. In August 2010 a bug let someone create 184 billion bitcoins in block 74638 through an integer overflow, a mistake in the software rather than in the chain. Developers released a fix within hours and the network moved to a corrected chain that left the bad block behind, which shows that the chain is only as safe as the code that checks it.')}
{viz('cychain')}
{run('hash_chain')}
{fxs(fx('A block hash', 'h<sub>i</sub> = H(i &#8214; h<sub>i&minus;1</sub> &#8214; data<sub>i</sub>)', 'Bitcoin hashes an 80 byte header twice: SHA-256(SHA-256(header)).', key=True),
     fx('The avalanche effect', 'Change 1 input bit and each output bit flips with probability about &frac12;', 'Expected bits changed: 256 &times; &frac12; = 128.'),
     fx('Chance of a random hash matching a stored one', '2<sup>&minus;256</sup>', 'About 8.6 &times; 10<sup>&minus;78</sup>. Forging a link by luck is hopeless.'))}
{steps('How a node checks a chain', ['Start at the genesis block, which every node knows by heart.',
       'For each block, recompute its hash from its contents and compare with the stored hash.',
       'Check that its "previous" field equals the hash of the block before.',
       'Check every payment inside: valid signatures, no coin spent twice, amounts add up.',
       'Check the proof of work (or proof of stake signatures) meets the rule.'])}
''', kw=['block', 'block header', 'hash link', 'previous hash', 'SHA-256', 'avalanche effect', 'tamper evident', 'value overflow incident', 'CVE-2010-5139', 'block 74638'])

K.lesson('pow', 'Proof of work: making the past expensive to rewrite', f'''
{talk('Proof of work turns a cheap hash chain into one that is very expensive to rewrite. The rule is simple. A block is valid only if its hash is below a target, which in practice means it starts with a certain number of zeros. The miner cannot choose the hash, so they change a number called the nonce and hash again, over and over, like rolling dice until all of them show six. Each extra hex zero makes the search about sixteen times longer. Checking the answer takes one hash. In the animation, two hex zeros need about 256 tries on average. Bitcoin today needs roughly 78 zero bits, which is about 2 to the 78 hashes, so the whole world’s mining machines together find one block about every ten minutes. Every 2016 blocks, roughly two weeks, Bitcoin adjusts the target so that blocks keep coming every ten minutes whether miners join or leave. The miner who finds a block earns new coins, the block reward, which halves every 210,000 blocks, from 50 bitcoin in 2009 to 3.125 since April 2024, so there will never be more than 21 million. Rewriting a block buried under six others means redoing all that work faster than everyone else, and that cost is what protects the past. The price is energy. Bitcoin mining uses about as much electricity as a medium sized country, which is why Ethereum moved away from proof of work in 2022.')}
{viz('cypow')}
{run('mine')}
{run('difficulty')}
{fxs(fx('Expected tries for k leading hex zeros', 'E[tries] = 16<sup>k</sup> = 2<sup>4k</sup>', 'k = 3: 4,096 tries.', key=True),
     fx('Probability one hash wins', 'p = target / 2<sup>256</sup>', 'For k hex zeros p = 16<sup>&minus;k</sup>. The number of tries is geometric with mean 1/p.', key=True),
     fx('Difficulty retarget', 'new = old &times; (2016 &times; 600 s) / actual time, limited to a factor of 4', '2016 blocks in 10 days: 100 &times; 14 / 10 = 140.', key=True),
     fx('Block reward after n halvings', 'reward = 50 / 2<sup>n</sup>', 'n = 4 (April 2024): 50 / 16 = 3.125 bitcoin.'),
     fx('Total supply', '210,000 &times; 50 &times; (1 + &frac12; + &frac14; + &hellip;) = 21,000,000', 'A geometric series with sum 2.'))}
''', kw=['proof of work', 'mining', 'nonce', 'target', 'difficulty', 'leading zeros', 'retarget', '2016 blocks', 'block reward', 'halving', '21 million', 'energy use', 'ASIC'])

K.lesson('merkle', 'Merkle trees: one fingerprint for every payment in a block', f'''
{talk('A block can hold thousands of payments, and a phone wallet cannot download them all. The trick comes from Ralph Merkle, who patented hash trees in 1979. Hash every payment, then hash the results in pairs, then pair again, until one hash is left at the top. That top hash, the Merkle root, sits in the 80 byte block header. Change any payment and the root changes. To prove that your payment is in a block, a full node sends you only the sibling hash at each level, the orange boxes in the animation, and you recompute the path to the root yourself. For a block with four thousand payments that is just twelve hashes. Satoshi called this simplified payment verification, section 8 of the Bitcoin paper, and it is how light wallets work. Certificate Transparency logs, Git and many file systems use the same tree. One real lesson from history: Bitcoin pairs an odd last hash with itself, and in 2012 developers found that this let two different lists of payments give the same root, a weakness tracked as CVE-2012-2459 that nodes now guard against by rejecting duplicated payments.')}
{viz('cymerkle')}
{run('merkle_proof')}
{fxs(fx('Proof length', 'about &lceil;log<sub>2</sub> n&rceil; sibling hashes', 'n = 4,000: &lceil;11.97&rceil; = 12 hashes, about 384 bytes.', key=True),
     fx('Parent node', 'parent = H(left &#8214; right)', 'With an odd count, the last node is paired with itself.'),
     fx('Saving from a proof', 'n payments versus log<sub>2</sub> n hashes', 'One million payments: 20 hashes instead of a million.'))}
{note('A Merkle proof shows that a payment is <b>in</b> a block. It does not show the block is on the longest chain, so light wallets also check the chain of block headers and their proof of work.')}
''', kw=['Merkle tree', 'Merkle root', 'Ralph Merkle', 'Merkle proof', 'SPV', 'simplified payment verification', 'light wallet', 'CVE-2012-2459', 'log n proof'])

K.lesson('race', 'Consensus, forks, double spending and the 51% attack', f'''
{talk('Sometimes two miners find a block at almost the same moment, and for a short while the network has two competing tips, a fork. The rule is to follow the chain with the most total work. Within a block or two one side pulls ahead and the other block becomes an orphan, so a payment is never treated as final the instant it appears. Now picture a cheater. They pay a shop, and at the same time they secretly mine their own chain in which that payment never happened. If their secret chain ever catches up and pulls ahead, they publish it, every node switches, and the coins return to the cheater, who has the goods as well. That is a double spend. The chance depends on q, the attacker’s share of all mining power, and z, the number of blocks the shop waits for. Nakamoto worked out the formula in section 11 of his paper. With ten percent of the power and six confirmations, the chance is about 0.02 percent. With more than half the power, the attacker wins in the end whatever the shop does, which is why it is called a 51 percent attack. This is not only theory. Bitcoin Gold lost about 18 million dollars to double spends in May 2018. Ethereum Classic was attacked in January 2019, then three times in August 2020, once with a reorganisation of more than 3,600 blocks. Small chains are at risk because renting enough computing power for an hour can cost only a few thousand dollars.')}
{viz('cy51')}
{run('nakamoto')}
{fxs(fx('Attacker catch up from z behind (gambler’s ruin)', 'q<sub>z</sub> = 1 if q &ge; p, else (q / p)<sup>z</sup>, with p = 1 &minus; q', 'q = 0.3, z = 3: (0.3/0.7)<sup>3</sup> &asymp; 0.0787.', key=True),
     fx('Nakamoto’s formula', 'P = 1 &minus; &Sigma;<sub>k=0</sub><sup>z</sup> (&lambda;<sup>k</sup> e<sup>&minus;&lambda;</sup> / k!) (1 &minus; (q/p)<sup>z&minus;k</sup>), &lambda; = z q / p', 'q = 0.1, z = 6: P &asymp; 0.00024.', key=True),
     fx('Expected attacker progress', '&lambda; = z q / p', 'While honest miners add z blocks, the attacker adds about this many.'))}
{table(['Attack on consensus', 'How it works', 'Defence'], [
    ['51% attack and double spend', 'A miner with most of the power rewrites recent blocks', 'Wait for more confirmations, use chains with huge total work, watch for deep reorganisations'],
    ['Selfish mining (Eyal and Sirer 2014)', 'Hold found blocks back and release them to waste honest work', 'Profitable from about one third of the power in their model, so no pool should be that big'],
    ['Eclipse attack (Heilman et al. 2015)', 'Surround one node with attacker peers so it sees a fake view', 'Many diverse outgoing connections, random peer choice, anchor peers'],
    ['Sybil attack', 'Create thousands of fake nodes', 'Voting power comes from work or stake, not from node count'],
    ['Zero confirmation double spend', 'Send two conflicting payments to different nodes at once', 'Never treat an unconfirmed payment as final for valuable goods']])}
''', kw=['fork', 'longest chain', 'most work', 'orphan block', 'confirmations', 'double spend', '51% attack', 'Nakamoto formula', 'gambler’s ruin', 'selfish mining', 'eclipse attack', 'Sybil attack', 'Bitcoin Gold', 'Ethereum Classic', 'reorganisation'])

K.lesson('pos', 'Proof of stake: security from locked money instead of electricity', f'''
{talk('Proof of stake replaces electricity with money put at risk. People who want to help run the chain, called validators, lock up coins as a deposit. On Ethereum each validator locks 32 ether. Time is cut into twelve second slots, and in each slot one validator is picked at random to propose a block while committees of others vote, called attestations, that it is correct. Thirty two slots make an epoch of 6.4 minutes, and once two thirds of all staked ether has voted for a checkpoint across two epochs, it is finalised, which means reversing it would destroy at least one third of all the stake. If a validator cheats, for example by signing two different blocks for the same slot, anyone can submit the two signatures as proof and the validator is slashed, losing part of the deposit and being thrown out. Ethereum switched from proof of work to proof of stake on 15 September 2022 in an upgrade called the Merge, and its energy use fell by more than 99.9 percent. Proof of stake brings its own risks. Validators must keep their signing keys online, so key security matters even more. A few large staking services control a big share of the stake, which raises questions of centralisation. And long range attacks, where old keys are bought to build a fake history from long ago, are handled by checkpoints that new nodes must trust.')}
{fxs(fx('Epoch length on Ethereum', '32 slots &times; 12 s = 384 s = 6.4 minutes', 'Finality usually takes 2 epochs, about 12.8 minutes.', key=True),
     fx('Finality rule', 'a checkpoint is final when validators holding &ge; &frac23; of the stake vote for it', 'Reverting it needs &ge; &frac13; of all stake to be slashable.', key=True),
     fx('Cost of breaking finality', '&ge; &frac13; &times; total stake', 'With 30 million ether staked: at least 10 million ether at risk.'))}
{versus('Ways to agree on the next block', ['', 'Proof of work', 'Proof of stake', 'Permissioned (PBFT style)'], [
    ['Who votes', 'Whoever has computing power', 'Whoever has locked coins', 'A fixed list of known organisations'],
    ['What an attack costs', 'Hardware and electricity, more than half the hash power', 'One third to two thirds of all stake, which gets slashed', 'Corrupting one third of the members'],
    ['Finality', 'Probabilistic, grows with confirmations', 'Explicit after two epochs', 'Immediate after a vote'],
    ['Energy', 'Very high', 'Low', 'Low'],
    ['Examples', 'Bitcoin, Litecoin, Ethereum Classic', 'Ethereum since 2022, Cardano, Solana', 'Hyperledger Fabric, bank settlement networks']],
    'Public money networks need open voting, so they use work or stake. A group of banks that already know each other can use a permissioned chain, which is fast but trusts its members.')}
''', kw=['proof of stake', 'validator', '32 ether', 'slot', 'epoch', 'attestation', 'finality', 'slashing', 'the Merge', 'long range attack', 'weak subjectivity', 'PBFT', 'permissioned blockchain', 'Hyperledger'])

K.lesson('keys', 'Wallets and keys: where most money is actually lost', f'''
{talk('Here is the most important truth of this chapter. A wallet does not hold coins. The coins are entries on the chain. A wallet holds the private key that can sign a payment moving them. Bitcoin and Ethereum both use the elliptic curve secp256k1 from the elliptic curve chapter. The private key is a 256 bit random number, the public key is that number times a fixed point on the curve, and the address is a hash of the public key. Whoever knows the private key owns the coins, and there is no reset button. To make keys easier to back up, BIP 39 turns 128 random bits plus a 4 bit checksum into 12 words from a list of 2048, and BIP 32 grows a whole tree of keys from that one seed. Guessing 128 random bits is impossible, but a phrase that a person makes up, a so called brain wallet, can be found in seconds, and early brain wallets were emptied by bots within minutes. History is full of key disasters. In February 2014 Mt. Gox, then the biggest exchange, collapsed after losing about 850,000 bitcoin over years of poor key handling. In July 2024 the Indian exchange WazirX lost about 230 million dollars when attackers tricked the signers of a multi signature wallet into approving a malicious change. On 21 February 2025 the exchange Bybit lost about 1.5 billion dollars in ether, the largest theft in this field so far, after attackers broke into a developer machine of its wallet provider and changed what the signers saw on screen. The FBI attributed it to North Korea. None of these broke the maths. They broke computers and people around the keys.')}
{viz('cyecdh')}
{run('seed_phrase')}
{fxs(fx('Seed phrase size (BIP 39)', 'words = (ENT + ENT/32) / 11', '128 bits: (128 + 4) / 11 = 12 words. 256 bits: (256 + 8) / 11 = 24 words.', key=True),
     fx('Strength of a human phrase', 'bits = k &times; log<sub>2</sub>(vocabulary)', '4 words from 5,000: 4 &times; 12.29 &asymp; 49.2 bits, weak.', key=True),
     fx('m of n multisig', 'any m of the n keys must sign', '2 of 3: one lost or stolen key alone can neither spend nor block spending.'))}
{table(['Wallet type', 'Where the key lives', 'Main risk', 'Good for'], [
    ['Hot wallet', 'A phone app or exchange server, online', 'Malware, phishing, server breach', 'Small daily amounts'],
    ['Hardware wallet', 'A small device that signs inside a secure chip', 'Lost device without a backup, fake devices', 'Personal savings'],
    ['Cold storage', 'Offline, sometimes on paper or metal', 'Fire, theft, mistakes when moving funds', 'Large long term holdings'],
    ['Multisig', 'Several keys held by different people or devices', 'Signers tricked into approving a bad payment (WazirX, Bybit)', 'Companies and exchanges'],
    ['Custodial account', 'The exchange holds the key for you', 'Exchange failure or theft (Mt. Gox)', 'Beginners, with care']])}
{attack([
    ('Phishing sites and fake wallet apps that ask for the 12 words', 'Never type the seed phrase into any website or app. Real support never asks for it.'),
    ('Clipboard malware that swaps a copied address for the attacker’s', 'Check the first and last characters of the address on the hardware wallet screen.'),
    ('Blind signing: approving a payment whose details you cannot read', 'Use devices that show the real destination and amount, and verify on a second device.'),
    ('SIM swap to steal the phone number that resets an exchange account', 'Use an authenticator app or passkey, not SMS, for exchange logins.')])}
''', kw=['wallet', 'private key', 'public key', 'address', 'secp256k1', 'BIP 39', 'seed phrase', 'mnemonic', 'BIP 32', 'brain wallet', 'hot wallet', 'hardware wallet', 'cold storage', 'multisig', 'Mt. Gox', 'WazirX', 'Bybit', 'blind signing', 'clipboard hijacker'])

K.lesson('privacy', 'Privacy and crime: pseudonyms, tracing and ransomware', f'''
{talk('People often think Bitcoin is anonymous. It is not. It is pseudonymous: your name is not written on the chain, but every payment between addresses is public forever. Researchers led by Sarah Meiklejohn showed in 2013 that simple rules link many addresses to one owner. The best known is the common input rule: when several coins are spent together in one transaction, the same person almost always controls all of them. Add a few addresses whose owners are known, such as exchange deposit addresses, and whole flows of money become visible. Companies now sell this blockchain analysis to police and banks. In May 2021 the Colonial Pipeline company in the United States paid a ransom of 75 bitcoin. A month later the Department of Justice announced it had seized 63.7 of those bitcoin by following them to a wallet whose key it obtained. Criminals respond with mixers, which pool coins from many users, and privacy coins such as Monero, which hide amounts and senders with cryptography. Governments respond with sanctions and with rules that exchanges must know their customers, called KYC. Two other crimes are worth knowing. Cryptojacking is malware or a hidden script in a website that uses your computer to mine coins for someone else, which the Coinhive script did on thousands of hacked sites until 2019. And investment scams and rug pulls, where a project’s creators run off with investors’ money, take more money from ordinary people every year than technical hacks.')}
{run('clustering')}
{table(['Idea', 'What it means', 'Example'], [
    ['Pseudonymity', 'Addresses instead of names, but every payment is public', 'Bitcoin, Ethereum'],
    ['Common input heuristic', 'Inputs spent together share one owner', 'Meiklejohn et al. 2013'],
    ['Know your customer (KYC)', 'Exchanges record who owns each account', 'Indian exchanges register with the Financial Intelligence Unit'],
    ['Mixers and privacy coins', 'Break the link between sender and receiver', 'CoinJoin, Monero'],
    ['Cryptojacking', 'Stealing computing power to mine', 'Coinhive scripts on hacked sites, 2017 to 2019']])}
{safe('Explore a public block explorer for a famous old transaction, such as the 10,000 bitcoin pizza payment of 22 May 2010. Reading the public chain is legal and harmless. Never send coins to an address you found in a message, and never try to trace or contact real people from what you see.')}
''', kw=['pseudonymity', 'anonymity', 'blockchain analysis', 'common input heuristic', 'address clustering', 'Meiklejohn', 'Colonial Pipeline', 'ransomware tracing', 'mixer', 'CoinJoin', 'Monero', 'KYC', 'cryptojacking', 'Coinhive', 'rug pull'])

K.lesson('versus', 'Blockchain compared with an ordinary database', f'''
{talk('A blockchain is a tool with a high price, so it is worth asking when it is the right one. If one trusted organisation runs the system, an ordinary database with backups and signed audit logs is faster, cheaper and private. A blockchain makes sense when many parties who do not trust each other must share one record and nobody should be able to change it alone.')}
{versus('Where should the record live', ['', 'Ordinary database', 'Signed audit log', 'Public blockchain'], [
    ['Who controls it', 'One organisation', 'One organisation, with tamper evidence', 'Nobody alone'],
    ['Speed', 'Thousands of writes a second', 'Fast', 'Bitcoin about 7 payments a second, minutes to settle'],
    ['Privacy', 'Private by default', 'Private', 'Public forever'],
    ['Fixing mistakes', 'An administrator can correct them', 'Corrections are new entries', 'Practically impossible, by design'],
    ['Best when', 'One trusted owner', 'You must prove logs were not changed', 'Many parties with no shared trust']],
    'The hash chained logs of the SIEM chapter give tamper evidence without any of the cost. Reach for a blockchain only when no single party may hold the pen.')}
''', kw=['blockchain versus database', 'audit log', 'when to use blockchain', 'throughput', 'immutability'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that a blockchain is a shared notebook with linked pages and that whoever holds the private key owns the coins. A student can compute a hash chain, a Merkle proof and the double spend probability. A professional secures keys and wallets, judges confirmation counts and traces funds. Experts design consensus protocols and analyse attacks on them.')}
{ladder(
    '<p>A blockchain is a shared notebook. Each page includes a seal made from the page before, so nobody can change old pages without everyone noticing. Your secret key is your money, so never share your recovery words.</p>',
    '<p>Hash links h<sub>i</sub> = H(i &#8214; h<sub>i&minus;1</sub> &#8214; data), proof of work with 16<sup>k</sup> expected tries, retarget every 2016 blocks, Merkle proofs of log<sub>2</sub> n hashes, Nakamoto’s double spend formula, BIP 39 sizes.</p>',
    '<p>Run key ceremonies, hardware security modules and multisig policies, verify transactions on independent screens, monitor reorganisations, and use chain analysis in incident response.</p>',
    '<p>Research consensus security (selfish mining, eclipse, long range attacks), formal proofs of protocols, privacy with zero knowledge proofs, and the economics of attacks on small chains.</p>')}
{grow('Explain how hash links and keys protect a blockchain.',
      'Compute mining work, Merkle proofs and double spend risk.',
      'Secure wallets and judge when a blockchain is the right tool.')}
''', kw=['beginner', 'expert', 'key ceremony', 'HSM', 'consensus research'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>What</b>: a shared list of blocks, each holding the hash of the one before (Haber and Stornetta 1991, Nakamoto 2008). Strong integrity and availability, almost no confidentiality.',
    '<b>Proof of work</b>: find a nonce so the hash is below a target, 16<sup>k</sup> tries for k hex zeros, retarget every 2016 blocks, reward 50 / 2<sup>n</sup>, at most 21 million.',
    '<b>Merkle trees</b>: one root for all payments, proofs of about log<sub>2</sub> n hashes, used by light wallets.',
    '<b>Consensus attacks</b>: double spend race, (q/p)<sup>z</sup> and Nakamoto’s formula, 51% attacks on Bitcoin Gold and Ethereum Classic, selfish mining, eclipse, Sybil.',
    '<b>Proof of stake</b>: 32 ether validators, slots, epochs, finality at two thirds, slashing. Ethereum Merge 15 September 2022.',
    '<b>Keys</b>: whoever holds the key owns the coins. BIP 39 12 words = 128 + 4 bits. Mt. Gox, WazirX and Bybit were key and people failures, not broken maths.',
    '<b>Privacy</b>: pseudonymous, not anonymous. Common input clustering, Colonial Pipeline recovery, mixers and KYC.'],
    'Advanced 3.2: Ethereum and smart contract security, where the code on the chain is the next thing attackers target.')}
{files('Three tasks: check a chain, check a proof of work, and build a Merkle root.')}
''', kw=['summary', 'recap'])

# ------------------------------------------------------------------------------------------------ quiz
K.quiz('e', 'What does each block in a blockchain store to link it to the past?', ['The name of the miner', 'The hash of the previous block', 'A copy of every earlier block', 'The current price'], 1, 'The chain part.', 'Changing an old block changes its hash, so the next block’s link breaks.')
K.quiz('e', 'Who owns the coins at an address?', ['The bank', 'Whoever knows the private key', 'The miner who found the block', 'The exchange'], 1, 'Signatures.', 'Only the private key can sign a valid spend, and it cannot be reset.')
K.quiz('e', 'Which security goal does a public blockchain give least of?', ['Integrity', 'Availability', 'Confidentiality', 'Tamper evidence'], 2, 'Who can read it?', 'Every payment is public forever.')
K.quiz('e', 'A support agent on a chat app asks for your 12 recovery words to fix your wallet. What should you do?', ['Send them', 'Send half of them', 'Refuse, because anyone with the words can take everything', 'Send them in a photo'], 2, 'The words are the key.', 'Real support never needs the seed phrase. This is the most common crypto scam.')
K.quiz('m', 'Each extra hex zero in the target makes mining about', ['2 times harder', '16 times harder', '256 times harder', 'No harder'], 1, 'One hex digit has 16 values.', 'Expected tries 16<sup>k</sup>.')
K.quiz('m', 'Why can a light wallet check a payment without downloading the whole block?', ['It trusts the sender', 'A Merkle proof of about log<sub>2</sub> n hashes leads to the root in the header', 'It uses a password', 'Blocks are tiny'], 1, 'Sibling hashes.', '4,000 payments need about 12 hashes.')
K.quiz('m', 'What is a double spend?', ['Paying twice by mistake', 'Spending the same coins in two conflicting payments so that one is later undone', 'Paying double fees', 'Two miners finding a block'], 1, 'The race.', 'The attacker’s secret chain removes the payment to the shop.')
K.quiz('m', 'Why do shops wait for several confirmations?', ['To collect fees', 'Each extra block makes rewriting the payment much less likely', 'The law requires it', 'To save energy'], 1, 'Nakamoto’s formula.', 'With q = 0.1, six blocks push the risk to about 0.02%.')
K.quiz('m', 'In Ethereum proof of stake, what happens to a validator that signs two different blocks for the same slot?', ['Nothing', 'It is slashed and loses part of its deposit', 'It earns a bonus', 'Its block is accepted twice'], 1, 'Cheating costs stake.', 'The two signatures are proof of misbehaviour.')
K.quiz('h', 'What did the common input heuristic (Meiklejohn et al. 2013) assume?', ['All addresses belong to exchanges', 'Coins spent together as inputs of one transaction share an owner', 'Every output is change', 'Miners are honest'], 1, 'Spending together.', 'This rule clusters addresses and makes many flows traceable.')
K.quiz('h', 'Why are small proof of work chains more exposed to 51% attacks?', ['Their code is older', 'Renting more than half of their small total hash power can be cheap', 'They have no blocks', 'They use SHA-1'], 1, 'Cost of majority.', 'Ethereum Classic and Bitcoin Gold were both attacked this way.')
K.quiz('h', 'The Bybit theft of February 2025 happened mainly because', ['SHA-256 was broken', 'Attackers changed what multisig signers saw and they approved a malicious transaction', 'The chain had a 51% attack', 'A miner stole the block reward'], 1, 'People and software around the key.', 'A compromised developer machine at the wallet provider served altered content.')
K.quiz('h', 'A 12 word BIP 39 phrase holds how many random bits?', ['132', '128', '144', '256'], 1, '12 &times; 11 = 132 total.', '128 bits of entropy plus a 4 bit checksum.')
K.quiz('x', 'In the style of a Stanford CS 251 question: an attacker with q = 0.3 is z = 3 blocks behind. What is the chance they ever catch up (gambler’s ruin)?', ['0.3', 'About 0.079', 'About 0.43', '1'], 1, '(q/p)<sup>z</sup>.', '(3/7)<sup>3</sup> &asymp; 0.0787.')
K.quiz('x', 'In the style of an IIT Kanpur blockchain course: why does proof of stake need weak subjectivity checkpoints?', ['To save energy', 'Old validators could sell keys that let anyone build a fake history from long ago', 'Blocks are too big', 'To pay rewards'], 1, 'Long range attacks.', 'Keys that are no longer staked cost nothing to misuse, so new nodes start from a recent trusted checkpoint.')

# ------------------------------------------------------------------------------------------------ problems
K.calc('e', 'Expected tries to find a hash starting with 3 hex zeros?', '4096', '16<sup>k</sup>.', ['Each hex digit is 0 with probability 1/16.', '16 &times; 16 &times; 16.', eq('4096')], check=16 ** 3)
K.calc('e', 'Block reward after 4 halvings, starting from 50?', '3.125', '50 / 2<sup>n</sup>.', ['2<sup>4</sup> = 16.', '50 / 16.', eq('3.125')], check=50 / 2 ** 4)
K.calc('e', 'A BIP 39 phrase with 256 bits of entropy has how many words?', '24', '(ENT + ENT/32) / 11.', ['Checksum 256 / 32 = 8 bits.', '264 / 11.', eq('24')], check=(256 + 8) // 11)
K.calc('m', 'Hashes in a Merkle proof for 4,000 payments?', '12', '&lceil;log<sub>2</sub> n&rceil;.', ['2<sup>11</sup> = 2048 &lt; 4000.', '2<sup>12</sup> = 4096 &ge; 4000.', eq('12')], check=math.ceil(math.log2(4000)))
K.calc('m', 'Difficulty 100. The last 2016 blocks took 10 days instead of 14. New difficulty?', '140', 'old &times; 14 / actual.', ['14 / 10 = 1.4.', '100 &times; 1.4.', eq('140')], check=100 * 14 / 10)
K.calc('m', 'Difficulty 100 and the blocks took 2 days. New difficulty after the factor of 4 limit?', '400', 'Cap the change at 4 times.', ['Unlimited it would be 100 &times; 7 = 700.', 'The rule caps it at 4 times.', eq('400')], check=100 * 4)
K.calc('m', 'Gambler’s ruin: q = 0.3, z = 3. Chance the attacker ever catches up? Round to 4 decimals.', '0.0787', '(q/p)<sup>z</sup>.', ['p = 0.7, q/p = 0.4286.', 'Cubed.', eq('&asymp; 0.0787')], check=round((0.3 / 0.7) ** 3, 4))
K.calc('m', 'Ethereum: 32 slots of 12 seconds. Epoch length in minutes?', '6.4', '32 &times; 12 / 60.', ['384 seconds.', 'Divide by 60.', eq('6.4')], check=32 * 12 / 60)
K.calc('h', 'Nakamoto’s formula with q = 0.1 and z = 6. Probability? Round to 5 decimals.', '0.00024', '&lambda; = z q / p.', ['&lambda; = 6 &times; 0.1 / 0.9 = 0.6667.', 'Sum the Poisson terms times (1 &minus; (q/p)<sup>z&minus;k</sup>) and subtract from 1.', eq('&asymp; 0.00024')], check=round(1 - sum(math.exp(-6 * 0.1 / 0.9) * (6 * 0.1 / 0.9) ** k / math.factorial(k) * (1 - (0.1 / 0.9) ** (6 - k)) for k in range(7)), 5))
K.calc('h', 'A human made phrase of 4 words from 5,000. Bits of strength? Round to 1 decimal.', '49.2', '4 &times; log<sub>2</sub> 5000.', ['log<sub>2</sub> 5000 &asymp; 12.288.', 'Times 4.', eq('&asymp; 49.2')], check=round(4 * math.log2(5000), 1))
K.calc('h', 'Total Bitcoin supply: 210,000 blocks per era, starting reward 50, halving forever. Total in millions?', '21', '210,000 &times; 50 &times; 2.', ['First era: 10.5 million.', 'Geometric series 1 + &frac12; + &frac14; + &hellip; = 2.', eq('21 million')], check=210000 * 50 * 2 / 1e6)
K.calc('x', 'Proof of stake: 30 million ether staked. Minimum ether slashable to break finality, in millions?', '10', '&frac13; of the stake.', ['Two conflicting finalised checkpoints need two thirds each.', 'Their overlap is at least one third.', eq('10 million')], check=30 / 3)

# ------------------------------------------------------------------------------------------------ assignments
K.assign('chain_valid', 'e', 'Check a hash chain',
         '<p>Each block is a dict with keys <code>n</code>, <code>prev</code>, <code>data</code> and <code>hash</code>, where hash is the SHA-256 hex of <code>f"{n}|{prev}|{data}"</code>. Write <code>chain_valid(chain)</code> that returns the index of the first bad block (stored hash wrong, or prev not equal to the hash before), or <code>-1</code> if the chain is valid.</p>',
         '''
import hashlib

def bh(n, prev, data):
    return hashlib.sha256(f"{n}|{prev}|{data}".encode()).hexdigest()

def make(datas):
    chain, prev = [], "0" * 64
    for i, d in enumerate(datas):
        h = bh(i, prev, d)
        chain.append({"n": i, "prev": prev, "data": d, "hash": h})
        prev = h
    return chain

def chain_valid(chain):
    # your code here
    pass
''', [('chain_valid(make(["genesis", "a pays b 5", "b pays c 2"]))', -1),
      ('chain_valid([dict(b, data="a pays b 50") if b["n"] == 1 else b for b in make(["genesis", "a pays b 5", "b pays c 2"])])', 1),
      ('chain_valid([dict(b, prev="0" * 64) if b["n"] == 2 else b for b in make(["genesis", "x", "y"])])', 2),
      ('chain_valid([])', -1)],
         '''
import hashlib

def bh(n, prev, data):
    return hashlib.sha256(f"{n}|{prev}|{data}".encode()).hexdigest()

def make(datas):
    chain, prev = [], "0" * 64
    for i, d in enumerate(datas):
        h = bh(i, prev, d)
        chain.append({"n": i, "prev": prev, "data": d, "hash": h})
        prev = h
    return chain

def chain_valid(chain):
    for i, b in enumerate(chain):
        if b["hash"] != bh(b["n"], b["prev"], b["data"]):
            return i
        if i > 0 and b["prev"] != chain[i - 1]["hash"]:
            return i
    return -1
''', 'Loop with enumerate. Recompute each hash with bh, then compare prev with the previous block’s hash.', '<p>Real nodes do exactly this, plus checking signatures and proof of work, for every block they receive. Never trust a block because a peer says it is fine.</p>')
K.assign('meets_target', 'm', 'Check a proof of work',
         '<p>Write <code>meets_target(data, nonce, zeros)</code> that returns True when the SHA-256 hex of <code>f"{data}|{nonce}"</code> starts with <code>zeros</code> zero characters. Then write <code>first_nonce(data, zeros)</code> that returns the smallest nonce from 0 upward that meets the target.</p>',
         '''
import hashlib

def meets_target(data, nonce, zeros):
    # your code here
    pass

def first_nonce(data, zeros):
    # your code here
    pass
''', [('meets_target("x", first_nonce("x", 2), 2)', True),
      ('all(not meets_target("x", n, 2) for n in range(first_nonce("x", 2)))', True),
      ('meets_target("anything", 0, 0)', True),
      ('first_nonce("Block 7", 1) < 200', True)],
         '''
import hashlib

def meets_target(data, nonce, zeros):
    h = hashlib.sha256(f"{data}|{nonce}".encode()).hexdigest()
    return h.startswith("0" * zeros)

def first_nonce(data, zeros):
    nonce = 0
    while not meets_target(data, nonce, zeros):
        nonce += 1
    return nonce
''', 'startswith("0" * zeros) does the check. first_nonce keeps adding 1 until meets_target is True.', '<p>Notice the asymmetry: first_nonce may take thousands of hashes, while meets_target takes one. That gap between finding and checking is the whole idea of proof of work.</p>')
K.assign('merkle_root', 'h', 'Build a Merkle root',
         '<p>Write <code>merkle_root(items)</code> for a non empty list of strings. Hash each item with SHA-256 (hex). Then, while more than one hash is left, join neighbours as <code>h(left + right)</code>, pairing an odd last hash with itself. Return the final hex string.</p>',
         '''
import hashlib

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def merkle_root(items):
    # your code here
    pass
''', [('merkle_root(["a"]) == h("a")', True),
      ('merkle_root(["a", "b"]) == h(h("a") + h("b"))', True),
      ('merkle_root(["a", "b", "c"]) == h(h(h("a") + h("b")) + h(h("c") + h("c")))', True),
      ('merkle_root(["a", "b", "c", "d"]) != merkle_root(["a", "b", "d", "c"])', True)],
         '''
import hashlib

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def merkle_root(items):
    level = [h(x) for x in items]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]
''', 'Make the first level with a list comprehension. In the loop, copy the last hash when the length is odd, then hash pairs.', '<p>The last test shows that order matters: swapping two payments changes the root. Duplicating the odd hash is what made CVE-2012-2459 possible, so real nodes also reject blocks that repeat a payment.</p>')

K.must('What a blockchain is', 'Blocks linked by hashes, shared by many nodes, plus a consensus rule. Haber and Stornetta 1991, Nakamoto 31 October 2008, genesis block 3 January 2009. Strong integrity and availability, weak confidentiality.')
K.must('Proof of work', 'Hash below a target, 16<sup>k</sup> expected tries for k hex zeros, one hash to check. Retarget every 2016 blocks to 10 minutes, capped at 4 times. Reward 50 / 2<sup>n</sup>, 3.125 since April 2024, 21 million cap.')
K.must('Merkle trees', 'Parent = H(left &#8214; right), odd node paired with itself, root in the header, proofs of &lceil;log<sub>2</sub> n&rceil; hashes (SPV). CVE-2012-2459 duplicate weakness.')
K.must('Consensus attacks', 'Double spend race, catch up (q/p)<sup>z</sup>, Nakamoto formula (q = 0.1, z = 6: 0.024%). 51% attacks: Bitcoin Gold 2018, Ethereum Classic 2019 and 2020. Selfish mining (one third), eclipse, Sybil.')
K.must('Proof of stake', 'Ethereum since the Merge (15 September 2022): 32 ether validators, 12 s slots, 32 slot epochs, finality at two thirds after two epochs, slashing for double signing, weak subjectivity checkpoints.')
K.must('Keys and wallets', 'Key = ownership. secp256k1, address = hash of public key. BIP 39: 128 + 4 bits = 12 words of 2048. Hot, hardware, cold, multisig. Mt. Gox 2014, WazirX 2024, Bybit 2025 (about 1.5 billion dollars). Never share the seed phrase, check what you sign.')
K.must('Privacy and tracing', 'Pseudonymous, not anonymous. Common input clustering (Meiklejohn 2013), KYC at exchanges, Colonial Pipeline 63.7 of 75 bitcoin seized (2021), mixers, Monero, cryptojacking.')

T = K.topic(
    slug='cy-blockchain', topic='cy-blockchain', step=(3, 'Blockchain and emerging systems', 'cy-a3', 'How blockchains, cryptocurrencies and smart contracts are secured, and how they are attacked.', 'Advanced'),
    title='Blockchain security: hash chains, mining, consensus and wallets', short='Blockchain security', badge='3.1', minutes=90,
    lead='How a blockchain keeps one honest history among strangers: hash linked blocks, proof of work and its maths, Merkle proofs, the double spend race and 51% attacks, proof of stake and slashing, and the keys and wallets where most real losses happen, with tracing and privacy at the end.',
    desc='blockchain, Bitcoin, distributed ledger, hash chain, block header, SHA-256, proof of work, mining, nonce, difficulty, retarget, halving, block reward, Merkle tree, Merkle proof, SPV, consensus, fork, longest chain, double spend, 51% attack, Nakamoto formula, selfish mining, eclipse attack, Sybil attack, proof of stake, validator, slashing, finality, Ethereum Merge, wallet, private key, seed phrase, BIP 39, multisig, hardware wallet, Mt. Gox, WazirX, Bybit, blockchain analysis, common input heuristic, Colonial Pipeline, cryptojacking',
    summary='Hash linked blocks, proof of work maths, Merkle proofs, forks and double spends, 51% attacks, proof of stake and slashing, wallets and key theft, and tracing on a public chain.',
    keywords=['blockchain', 'Bitcoin', 'proof of work', 'Merkle tree', 'double spend', '51% attack', 'proof of stake', 'wallet', 'seed phrase', 'blockchain analysis'],
    recap='<p>Hashes make history tamper evident, work or stake makes it expensive to rewrite, and keys decide who can spend. Most losses come from stolen keys and tricked people, not broken maths.</p>',
    added='2026-11-22')
