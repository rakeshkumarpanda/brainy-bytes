# Advanced 2.1: federated learning in full. Checked against McMahan, Moore, Ramage, Hampson and Aguera y Arcas,
# "Communication-Efficient Learning of Deep Networks from Decentralized Data" (AISTATS 2017, arXiv February 2016), the
# Google AI blog on federated learning (April 2017), Hard et al., "Federated Learning for Mobile Keyboard Prediction"
# (2018, a CIFG LSTM of 1.4 million parameters), Bonawitz et al., "Practical Secure Aggregation" (ACM CCS 2017) and
# "Towards Federated Learning at Scale: System Design" (MLSys 2019), Kairouz et al., "Advances and Open Problems in
# Federated Learning" (2021), Li et al., FedProx (MLSys 2020), Karimireddy et al., SCAFFOLD (ICML 2020), Yang, Liu,
# Chen and Tong, "Federated Machine Learning: Concept and Applications" (ACM TIST 2019), Pati et al., the FeTS study
# (Nature Communications 2022, 71 sites), McMahan et al., DP-FedAvg (ICLR 2018), Zhu, Liu and Han, "Deep Leakage from
# Gradients" (NeurIPS 2019), and the documentation of TensorFlow Federated, Flower, NVIDIA FLARE, PySyft and FATE.
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk

chapter('cy-fedlearn')
K = Kit()

K.code('fedavg_basic', r'''
# Federated averaging (FedAvg, McMahan et al. 2017): three hospitals train one model without sharing patient rows.
# Model: predict a blood test value y from age x with y = w * x + b (x scaled to 0 to 1).
import random

random.seed(0)
def hospital(n, age_lo, age_hi):
    rows = []
    for _ in range(n):
        x = random.uniform(age_lo, age_hi)
        rows.append((x, 2.0 * x + 1.0 + random.gauss(0, 0.1)))     # the true rule is y = 2x + 1
    return rows

clients = {"Asha (young patients)": hospital(40, 0.0, 0.4),
           "Bose (middle aged)": hospital(100, 0.3, 0.7),
           "City (older patients)": hospital(60, 0.6, 1.0)}

def local_train(w, b, rows, epochs=5, lr=0.8):
    """Plain gradient descent on the client's own rows. Only w and b leave the hospital."""
    for _ in range(epochs):
        gw = sum((w * x + b - y) * x for x, y in rows) / len(rows)
        gb = sum((w * x + b - y) for x, y in rows) / len(rows)
        w, b = w - lr * gw, b - lr * gb
    return w, b

w, b = 0.0, 0.0                                   # the global model on the server
n_total = sum(len(r) for r in clients.values())
for rnd in range(1, 101):
    new_w = new_b = 0.0
    for name, rows in clients.items():
        lw, lb = local_train(w, b, rows)          # 1. send the global model, 2. train locally
        new_w += len(rows) / n_total * lw         # 3. weighted average by data size
        new_b += len(rows) / n_total * lb
    w, b = new_w, new_b
    if rnd in (1, 5, 20, 50, 100):
        print(f"round {rnd:3}: w = {w:.3f}, b = {b:.3f}")

# what a central server would learn if it could pool all rows (the privacy cost FL avoids)
allrows = [r for rows in clients.values() for r in rows]
cw, cb = local_train(0.0, 0.0, allrows, epochs=1000, lr=0.8)
print(f"\ncentral model on pooled data: w = {cw:.3f}, b = {cb:.3f}   (true rule: w = 2, b = 1)")
''', long=True)

K.code('comm_rounds', r'''
# Communication: how many rounds until the model is good enough? FedSGD (1 local step) against FedAvg (E local steps)
import random

random.seed(0)
def hospital(n, lo, hi):
    return [(x, 2.0 * x + 1.0 + random.gauss(0, 0.1)) for x in (random.uniform(lo, hi) for _ in range(n))]

clients = [hospital(40, 0.0, 0.4), hospital(100, 0.3, 0.7), hospital(60, 0.6, 1.0)]
n_total = sum(len(c) for c in clients)
allrows = [r for c in clients for r in c]

def mse(w, b):
    return sum((w * x + b - y) ** 2 for x, y in allrows) / len(allrows)

def local_train(w, b, rows, epochs, lr=0.8):
    for _ in range(epochs):
        gw = sum((w * x + b - y) * x for x, y in rows) / len(rows)
        gb = sum((w * x + b - y) for x, y in rows) / len(rows)
        w, b = w - lr * gw, b - lr * gb
    return w, b

def rounds_needed(epochs, target=0.015, max_rounds=1000):
    w = b = 0.0
    for rnd in range(1, max_rounds + 1):
        results = [local_train(w, b, c, epochs) for c in clients]
        w = sum(len(c) / n_total * r[0] for c, r in zip(clients, results))
        b = sum(len(c) / n_total * r[1] for c, r in zip(clients, results))
        if mse(w, b) < target:
            return rnd
    return None

# a phone keyboard model has about 1.4 million parameters of 4 bytes, sent down and up every round
for e in (1, 5, 20):
    r = rounds_needed(e)
    mb = r * 2 * len(clients) * 1_400_000 * 4 / 1e6
    print(f"E = {e:2} local steps: {r:4} rounds  -> at keyboard model size that is {mb:8.1f} MB sent in total")
print("\nMore local work per round means far fewer rounds, which is the whole point of FedAvg.")
''', long=True)

K.code('client_drift', r'''
# Client drift on non-IID data, and two fixes: FedProx and SCAFFOLD.
# Each client k has its own loss f_k(w) = a_k / 2 * (w - c_k)^2 (equal data sizes).
# The best global model minimises the average loss: w* = sum(a_k * c_k) / sum(a_k).
clients = [(1.0, 0.0), (4.0, 10.0)]          # (curvature a_k, best point c_k): very different data
w_star = sum(a * c for a, c in clients) / sum(a for a, c in clients)
print(f"true global optimum w* = {w_star:.3f}")

def grad(w, a, c):
    return a * (w - c)

def fedavg_round(w, steps, lr, mu=0.0):
    new = []
    for a, c in clients:
        v = w
        for _ in range(steps):
            v -= lr * (grad(v, a, c) + mu * (v - w))   # FedProx adds mu * (v - w), FedAvg has mu = 0
        new.append(v)
    return sum(new) / len(new)

def scaffold_round(w, steps, lr):
    # control variates: each client's gradient at the global model, and their average
    ci = [grad(w, a, c) for a, c in clients]
    cg = sum(ci) / len(ci)
    new = []
    for (a, c), ck in zip(clients, ci):
        v = w
        for _ in range(steps):
            v -= lr * (grad(v, a, c) - ck + cg)          # correct the local direction towards the global one
        new.append(v)
    return sum(new) / len(new)

def run(step_fn, rounds=200):
    w = 0.0
    for _ in range(rounds):
        w = step_fn(w)
    return w

print(" E   FedAvg  FedProx mu=1  FedProx mu=4  SCAFFOLD")
for E in (1, 5, 50):
    a = run(lambda w: fedavg_round(w, E, 0.1))
    p1 = run(lambda w: fedavg_round(w, E, 0.1, 1.0))
    p4 = run(lambda w: fedavg_round(w, E, 0.1, 4.0))
    s = run(lambda w: scaffold_round(w, E, 0.1))
    print(f"{E:2}   {a:6.3f}  {p1:12.3f}  {p4:12.3f}  {s:8.3f}")
print("\nWith many local steps each client runs to its own optimum, so plain averaging drifts towards 5.0.")
print("FedProx pulls local models back towards the global one. SCAFFOLD corrects the direction and reaches 8.0.")
''', long=True)

K.code('compress_update', r'''
# Making updates small: top-k sparsification and 8 bit quantisation of a model update
import random

random.seed(2)
update = [random.gauss(0, 1) * (3 if i % 10 == 0 else 0.3) for i in range(40)]   # a few big values, many small

def top_k(u, k):
    keep = sorted(range(len(u)), key=lambda i: -abs(u[i]))[:k]
    return {i: u[i] for i in keep}                   # send (index, value) pairs only

def quantise(values, bits=8):
    lo, hi = min(values), max(values)
    levels = 2 ** bits - 1
    step = (hi - lo) / levels
    codes = [round((v - lo) / step) for v in values]  # small integers 0 to 255
    return [lo + c * step for c in codes], step

def error(u, approx):
    return sum((a - b) ** 2 for a, b in zip(u, approx)) ** 0.5 / sum(a * a for a in u) ** 0.5

full_bytes = len(update) * 4                          # 32 bit floats
sparse = top_k(update, 8)
dense_back = [sparse.get(i, 0.0) for i in range(len(update))]
q_vals, step = quantise(list(sparse.values()))
q_back = [0.0] * len(update)
for i, v in zip(sparse, q_vals):
    q_back[i] = v

print(f"full update:        {full_bytes:4} bytes, relative error 0")
print(f"top 8 of 40:        {8 * (4 + 4):4} bytes (index + value), relative error {error(update, dense_back):.3f}")
print(f"top 8 and 8 bit:    {8 * (1 + 1) + 8:4} bytes (index + code, plus lo and step), relative error {error(update, q_back):.3f}")
print("\nError feedback: each phone keeps what it did not send and adds it to its next update, so nothing is lost for good.")
''', long=True)

K.code('vertical_fl', r'''
# Vertical federated learning: a bank and a shop hold different columns about the same customers.
# Step 1 finds the shared customers, step 2 trains one logistic regression split across the two parties.
import hashlib
import math

bank = {"c01": [0.9, 0.2], "c02": [0.1, 0.8], "c03": [0.7, 0.4], "c05": [0.2, 0.9], "c06": [0.8, 0.1]}   # income, debt
labels = {"c01": 1, "c02": 0, "c03": 1, "c05": 0, "c06": 1}                                         # repaid the loan?
shop = {"c01": [0.8], "c03": [0.6], "c04": [0.5], "c05": [0.1], "c06": [0.9]}                         # spending score

# 1. find shared customers without listing them in the clear. A salted hash is only a teaching sketch:
#    real systems use a private set intersection (PSI) protocol, because short IDs can be guessed.
SALT = b"agreed-secret-salt"
def h(cid):
    return hashlib.sha256(SALT + cid.encode()).hexdigest()[:12]
shared_hashes = {h(c) for c in bank} & {h(c) for c in shop}
ids = sorted(c for c in bank if h(c) in shared_hashes)
print("shared customers:", ids)

# 2. each party keeps its own weights and computes a partial score on its own columns
wa, wb, b = [0.0, 0.0], [0.0], 0.0
for epoch in range(300):
    for cid in ids:
        za = wa[0] * bank[cid][0] + wa[1] * bank[cid][1] + b      # bank side
        zb = wb[0] * shop[cid][0]                                  # shop side, sent to the bank
        p = 1 / (1 + math.exp(-(za + zb)))
        err = p - labels[cid]                                      # only the bank knows the label
        # the bank sends err back to the shop. Real systems encrypt it (for example with Paillier).
        wa = [wa[0] - 0.5 * err * bank[cid][0], wa[1] - 0.5 * err * bank[cid][1]]
        b -= 0.5 * err
        wb = [wb[0] - 0.5 * err * shop[cid][0]]
print("bank weights (income, debt):", [round(v, 2) for v in wa], " shop weight (spending):", [round(v, 2) for v in wb])
for cid in ids:
    z = wa[0] * bank[cid][0] + wa[1] * bank[cid][1] + b + wb[0] * shop[cid][0]
    print(f"  {cid}: P(repay) = {1 / (1 + math.exp(-z)):.3f}  actual {labels[cid]}")
''', long=True)

K.code('secure_agg', r'''
# Secure aggregation (Bonawitz et al. 2017), small version: the server learns only the SUM of the phones' updates.
# Every pair of phones agrees a random mask. The lower numbered phone adds it, the higher one subtracts it.
import random

M = 2 ** 16                                  # updates are scaled to integers and added mod M
updates = {1: [12, 5, 7], 2: [3, 9, 1], 3: [8, 2, 6], 4: [4, 4, 4]}
phones = sorted(updates)

def pair_mask(i, j):
    # in the real protocol i and j derive this from a Diffie-Hellman shared key, so the server never knows it
    rng = random.Random(f"{min(i, j)}-{max(i, j)}")
    return [rng.randrange(M) for _ in range(3)]

def masked(i):
    out = list(updates[i])
    for j in phones:
        if j == i:
            continue
        m = pair_mask(i, j)
        sign = 1 if i < j else -1
        out = [(o + sign * mk) % M for o, mk in zip(out, m)]
    return out

sent = {i: masked(i) for i in phones}
for i in phones:
    print(f"phone {i} sends {sent[i]}   (its real update {updates[i]} is hidden)")
total = [sum(v[k] for v in sent.values()) % M for k in range(3)]
print("server sum:", total, "  check:", [sum(u[k] for u in updates.values()) for k in range(3)])

# phone 4 drops out after the masks were set up: its masks no longer cancel
alive = [1, 2, 3]
partial = [sum(sent[i][k] for i in alive) % M for k in range(3)]
# the survivors reveal their pair masks with phone 4 (the real protocol rebuilds them from Shamir shares)
for i in alive:
    m = pair_mask(i, 4)
    partial = [(p - mk) % M for p, mk in zip(partial, m)]     # phone i had added +mask for pair (i, 4)
print("after phone 4 drops out and its masks are removed:", partial, "  check:", [sum(updates[i][k] for i in alive) for k in range(3)])
''', long=True)

K.lesson('idea', 'Federated learning: bring the model to the data', f'''
{talk('Machine learning usually starts by collecting everyone’s data on one server. For phones, hospitals and banks that is often a bad idea or simply not allowed. Typing history, medical scans and financial records are sensitive, laws such as GDPR and India’s DPDP Act limit moving them, and one central pile of data is a tempting target for attackers. In 2016 Brendan McMahan and colleagues at Google proposed a different approach and named it federated learning. Instead of sending the data to the model, send the model to the data. A server holds a shared model. In each round it picks some devices, sends them the current model, each device trains on its own data for a few steps, and only the updated model weights come back. The server averages them into a better shared model, and the raw data never leaves the device. Google used it in 2017 to improve next word suggestions in the Gboard keyboard on Android phones. Apple has described using it with differential privacy for features such as Siri. In medicine, the FeTS study published in 2022 trained a brain tumour boundary model across 71 hospitals on six continents without moving patient scans. In 2021 Peter Kairouz and more than fifty co authors summarised the field and its open problems. This chapter covers the full picture: the FedAvg algorithm and its maths, why communication drives the design, what happens when clients have very different data, the different ways data can be split, secure aggregation so the server sees only the sum, and how real systems are built. The next chapter covers attacks on federated learning and the defences.')}
{src('McMahan et al. (AISTATS 2017), Google AI blog (2017), Hard et al. (2018), Bonawitz et al. (CCS 2017, MLSys 2019), Kairouz et al. (2021), Li et al. FedProx (2020), Karimireddy et al. SCAFFOLD (2020), Yang et al. (2019), Pati et al. FeTS (2022), McMahan et al. DP-FedAvg (2018), Zhu et al. (2019), TensorFlow Federated, Flower, NVIDIA FLARE, PySyft, FATE.')}
{wwh('<b>Federated learning (FL)</b> trains one shared model across many devices or organisations that keep their data where it is, sending only model updates to a coordinating server.',
     'Data may be private, regulated or too big to move, and a central copy is a single target for breaches. FL lets many parties benefit from each other’s data without pooling it.',
     'Repeat rounds: the server sends the global model to selected clients, each trains locally for E steps, sends back its new weights, and the server takes a weighted average. Add secure aggregation and differential privacy for stronger protection.')}
{viz('cyfedround')}
{table(['Term', 'Meaning'], [
    ['Client', 'A device or organisation holding local data: a phone, a hospital, a bank'],
    ['Server (aggregator)', 'Coordinates rounds and averages updates. It never sees raw data'],
    ['Round', 'One cycle: send the model, train locally, send updates back, average'],
    ['Local epochs E and batch size B', 'How much training each client does per round'],
    ['Client fraction C', 'The share of clients picked in each round, for example 0.1'],
    ['Update', 'The new local weights, or the difference from the global weights'],
    ['Non IID data', 'Clients’ data come from different distributions, the normal case in FL']])}
''', kw=['federated learning', 'FL', 'McMahan', 'Gboard', 'Apple Siri', 'FeTS', 'Kairouz', 'client', 'server', 'aggregator', 'round', 'local epochs', 'data minimisation', 'privacy by design'])

K.lesson('fedavg', 'The FedAvg algorithm and its maths', f'''
{talk('Federated averaging, or FedAvg, is the algorithm from the 2017 paper and still the baseline every new method is compared with. The goal is the same as ordinary training: find weights that minimise the average loss over all the data. The trick is to write that global loss as a weighted sum of each client’s own loss, weighted by how much data each client has. Then each client can work on its own part. In every round the server picks a fraction C of the clients, sends them the current weights, and each runs E passes over its data in mini batches of size B with learning rate eta. The server then averages the returned weights, weighting client k by n<sub>k</sub> over n, its share of the data. If every client takes exactly one full batch gradient step, this is called FedSGD, and it is exactly ordinary gradient descent on the pooled data, because a weighted average of the clients’ gradients is the gradient of the global loss. FedAvg simply lets clients take more local steps before averaging, which saves rounds. In our program three hospitals with patients of different ages learn the line y = 2x + 1. No hospital alone sees the whole age range, yet after enough rounds the federated model reaches almost the same answer as a model trained on pooled data.')}
{run('fedavg_basic')}
{steps('FedAvg, one step at a time', ['Server starts with weights w<sub>0</sub>.',
        'Each round t: pick a set S<sub>t</sub> of m = max(C &middot; K, 1) clients out of K.',
        'Send w<sub>t</sub> to every client in S<sub>t</sub>.',
        'Each client k sets w &larr; w<sub>t</sub> and, for E epochs over its n<sub>k</sub> examples in batches of B, does w &larr; w &minus; &eta; &nabla;&ell;(w, batch).',
        'Each client sends back its final w<sub>t+1</sub><sup>k</sup>.',
        'Server sets w<sub>t+1</sub> = &Sigma;<sub>k in S<sub>t</sub></sub> (n<sub>k</sub> / n<sub>S</sub>) w<sub>t+1</sub><sup>k</sup>, where n<sub>S</sub> is the data held by the chosen clients.'])}
{fxs(fx('Global objective', 'F(w) = &Sigma;<sub>k=1</sub><sup>K</sup> (n<sub>k</sub> / n) F<sub>k</sub>(w), F<sub>k</sub>(w) = (1 / n<sub>k</sub>) &Sigma;<sub>i in client k</sub> &ell;(w, x<sub>i</sub>, y<sub>i</sub>)', 'Clients with more data count more.', key=True),
     fx('FedAvg aggregation', 'w<sub>t+1</sub> = &Sigma;<sub>k</sub> (n<sub>k</sub> / n) w<sub>t+1</sub><sup>k</sup>', 'n = 50, 30, 20 and local weights 1.2, 0.8, 2.0: 0.6 + 0.24 + 0.4 = 1.24.', key=True),
     fx('Local updates per round', 'u<sub>k</sub> = E &middot; n<sub>k</sub> / B', 'E = 5, n<sub>k</sub> = 600, B = 20: 150 local steps.', key=True),
     fx('FedSGD is gradient descent', '&Sigma;<sub>k</sub> (n<sub>k</sub>/n)(w &minus; &eta; &nabla;F<sub>k</sub>(w)) = w &minus; &eta; &nabla;F(w)', 'Weighted gradients 2, &minus;1, 4 with weights 0.5, 0.3, 0.2 average to 1.5.', key=True))}
{deep('Why weight by data size', '<p>The pooled loss is an average over all n examples. Grouping the examples by client gives F = &Sigma; (n<sub>k</sub>/n) F<sub>k</sub>. A plain unweighted average of client models would give a phone with 10 examples as much say as one with 10000 and would optimise a different objective. Some systems cap the weight per client on purpose, to limit the influence of any one client, which also helps against poisoning and is needed for user level differential privacy.</p>')}
''', kw=['FedAvg', 'federated averaging', 'FedSGD', 'global objective', 'weighted average', 'client fraction', 'local epochs', 'batch size', 'learning rate', 'gradient descent equivalence'])

K.lesson('comm', 'Communication is the bottleneck', f'''
{talk('In a data centre, sending numbers between machines is fast. In federated learning, clients are phones on mobile networks or hospitals behind slow links, and uploads are much slower than downloads. A modern model has millions or billions of numbers, and every round sends the model down and the update back up. So the number of rounds, and the size of each message, decide the cost. FedAvg cuts rounds by doing more work locally. McMahan and colleagues reported 10 to 100 times fewer rounds than FedSGD on their tasks. Our program shows the same effect: 42 rounds with one local step, 9 rounds with twenty. The second lever is to shrink each update. Top k sparsification sends only the largest values with their positions. Quantisation rounds each value to a few bits, for example 8 bits instead of 32. Error feedback keeps what was not sent and adds it to the next update, so the errors do not pile up. Real deployments also choose clients carefully. Google’s 2019 system design paper describes phones joining only when they are idle, charging and on an unmetered Wi-Fi network, so users do not notice, and the server over selects clients because some always drop out.')}
{run('comm_rounds')}
{viz('cycompress')}
{run('compress_update')}
{fxs(fx('Data sent per round', 'bytes = 2 &times; m &times; P &times; b', 'm = 100 clients, P = 1.4 million parameters, b = 4 bytes: 1.12 &times; 10<sup>9</sup> bytes, about 1.12 GB.', key=True),
     fx('Top k with positions', 'bytes &asymp; k &times; (index bytes + value bytes)', 'Top 1% of 1 million with 4 + 4 bytes: 80000 bytes instead of 4000000, 50 times smaller.', key=True),
     fx('Uniform quantisation step', '&Delta; = (max &minus; min) / (2<sup>bits</sup> &minus; 1)', 'Range &minus;1.5 to 2.5 with 8 bits: 4 / 255 &asymp; 0.0157.'))}
''', kw=['communication cost', 'rounds', 'upload', 'compression', 'top k sparsification', 'quantisation', 'error feedback', 'client selection', 'idle charging Wi-Fi', 'over selection'])

K.lesson('noniid', 'Non IID data, client drift and fixes', f'''
{talk('In ordinary training we assume the examples are independent and identically distributed, IID for short: every batch looks like a small copy of the whole dataset. Federated data almost never looks like that. One phone types mostly in Hindi, another in English. One hospital sees mostly children, another mostly older patients. One bank serves farmers, another city workers. This is called non IID data, and it comes in several kinds: different label mixes, different feature distributions, and very different amounts of data. With non IID data, many local steps cause client drift: each client’s model runs towards the best model for its own data, and the average of those models is not the best model for everyone. Our program uses two clients whose losses are simple parabolas with different centres and steepness. The best global point is 8. With one local step per round, FedAvg finds 8. With 50 steps, each client nearly reaches its own optimum, at 0 and 10, and the average sits near 5. Two well known fixes follow. FedProx, by Tian Li and colleagues in 2020, adds a penalty that keeps each local model close to the global one. SCAFFOLD, by Sai Praneeth Karimireddy and colleagues in 2020, keeps a correction term per client that estimates how its gradient differs from the global one, and removes the drift entirely in our example. A third answer is personalisation: accept that clients differ, and fine tune the shared model locally for each one.')}
{run('client_drift')}
{fxs(fx('Best global point for quadratic clients', 'w* = &Sigma; p<sub>k</sub> a<sub>k</sub> c<sub>k</sub> / &Sigma; p<sub>k</sub> a<sub>k</sub>', 'a = (1, 4), c = (0, 10), equal p: 40 / 5 = 8.', key=True),
     fx('FedProx local objective', 'h<sub>k</sub>(w) = F<sub>k</sub>(w) + (&mu; / 2) &Vert;w &minus; w<sub>t</sub>&Vert;<sup>2</sup>', 'Its gradient adds &mu;(w &minus; w<sub>t</sub>): a = 4, w = 6, c = 10, &mu; = 1, w<sub>t</sub> = 5 gives &minus;16 + 1 = &minus;15.', key=True),
     fx('SCAFFOLD corrected step', 'w &larr; w &minus; &eta; (g<sub>k</sub>(w) &minus; c<sub>k</sub> + c)', 'c<sub>k</sub> estimates client k’s gradient, c the average. Their difference cancels the drift.'),
     fx('FedProx local optimum for a quadratic', 'w = (a c + &mu; w<sub>t</sub>) / (a + &mu;)', 'a = 4, c = 10, &mu; = 1, w<sub>t</sub> = 0: 40 / 5 = 8 instead of 10.'))}
{table(['Kind of non IID', 'Example', 'Effect'], [
    ['Label skew', 'One hospital sees mostly one disease', 'Local models favour local classes'],
    ['Feature skew', 'Different scanners or phone cameras', 'The same label looks different at each client'],
    ['Quantity skew', 'A few phones with thousands of messages, most with ten', 'Big clients dominate the weighted average'],
    ['Concept shift', 'The same word means different things in two regions', 'No single model is best for all']])}
''', kw=['non IID', 'IID', 'heterogeneity', 'client drift', 'label skew', 'feature skew', 'quantity skew', 'FedProx', 'proximal term', 'SCAFFOLD', 'control variates', 'personalisation', 'fine tuning'])

K.lesson('types', 'Cross device, cross silo, horizontal and vertical', f'''
{talk('Federated learning comes in two sizes. Cross device FL involves millions of phones or sensors, each with a little data, unreliable connections and no ability to keep state between rounds. Only a small fraction take part in each round. Cross silo FL involves a handful to a few hundred organisations, such as hospitals or banks, each with a lot of data, reliable servers and legal agreements between them. Every silo usually joins every round. Qiang Yang and colleagues in 2019 also named FL by how the data table is split. In horizontal FL the parties have the same columns for different people, as with hospitals recording the same tests. In vertical FL they have different columns for the same people, as with a bank and an online shop that share customers. Vertical FL needs two extra steps. First the parties find their shared customers with a private set intersection protocol, so neither learns the other’s non shared customers. Then they train a model split across them: each computes a partial score on its own columns, and the party with the labels sends back the errors, which real systems protect with homomorphic encryption such as Paillier, covered in the cryptography section. WeBank’s open source FATE platform was built for this in Chinese banking. Federated transfer learning covers the hard case where both people and columns barely overlap.')}
{viz('cyfedtypes')}
{run('vertical_fl')}
{versus('Cross device and cross silo FL', ['', 'Cross device', 'Cross silo'], [
    ['Clients', 'Millions of phones or sensors', '2 to a few hundred organisations'],
    ['Data per client', 'Small', 'Large'],
    ['Availability', 'Only idle, charging, on Wi-Fi, many drop out', 'Almost always available'],
    ['Each round', 'A small sample of clients', 'Usually all clients'],
    ['Trust and identity', 'Anonymous, some may be malicious', 'Known partners with contracts'],
    ['Example', 'Gboard next word prediction', 'FeTS brain tumour study across 71 sites']],
    'Cross device FL fights scale and drop outs. Cross silo FL fights legal agreements, data differences between institutions and vertical splits.')}
{note('A salted hash, as in the program, is only a sketch of matching customers. Customer IDs and phone numbers are easy to guess, so an attacker can hash every possible value. Real systems use a private set intersection protocol built on Diffie-Hellman style cryptography or oblivious transfer.', 'warn')}
''', kw=['cross device', 'cross silo', 'horizontal FL', 'vertical FL', 'federated transfer learning', 'private set intersection', 'PSI', 'entity alignment', 'split model', 'Paillier', 'FATE', 'WeBank'])

K.lesson('secagg', 'Secure aggregation: the server sees only the sum', f'''
{talk('Federated learning keeps raw data on the device, but the updates themselves can leak a lot. In 2019 Ligeng Zhu, Zhijian Liu and Song Han showed that training images and text can sometimes be rebuilt almost exactly from a single client’s gradients, an attack the next chapter studies. So a careful system makes sure the server never sees any single update, only the sum over many clients. Secure aggregation, published by Keith Bonawitz and colleagues at Google in 2017, does this with pairwise masks. Every pair of clients agrees a shared random mask using a Diffie-Hellman key exchange. The lower numbered client of each pair adds the mask to its update and the higher numbered one subtracts it. Each masked update looks like random noise, but when the server adds them all up, every mask appears once with a plus and once with a minus, so they cancel and only the true sum remains. The hard part is drop outs: phones vanish mid round, and then their masks no longer cancel. The protocol handles this by having each client split its secret keys into Shamir secret shares and give one share to every other client in advance. If a client drops out, enough survivors send their shares so the server can rebuild that client’s pairwise masks and remove them, while masks between survivors stay secret. A second layer of self masks stops the server from cheating by claiming a client dropped out when it did not. The cost grows with the number of pairs, so large systems group clients into smaller sets.')}
{viz('cysecagg')}
{run('secure_agg')}
{fxs(fx('Masked update of client i', 'y<sub>i</sub> = x<sub>i</sub> + &Sigma;<sub>j &gt; i</sub> m<sub>ij</sub> &minus; &Sigma;<sub>j &lt; i</sub> m<sub>ji</sub> (mod M)', 'Client 1: 12 + 37 + 81 = 130, mod 100 = 30.', key=True),
     fx('The masks cancel', '&Sigma;<sub>i</sub> y<sub>i</sub> = &Sigma;<sub>i</sub> x<sub>i</sub> (mod M)', '30 + 24 + 71 = 125, mod 100 = 25 = 12 + 5 + 8.', key=True),
     fx('Number of pairwise masks', 'pairs = n(n &minus; 1) / 2', '100 clients: 4950 pairs. This is why big rounds split clients into groups.', key=True))}
{note('Secure aggregation hides individual updates from the server, but the sum itself can still leak information when few clients take part, and it cannot spot a poisoned update it cannot see. That is why it is combined with a minimum number of clients per round, differential privacy, and careful defences against poisoning, as the next chapters show.', 'warn')}
''', kw=['secure aggregation', 'Bonawitz', 'pairwise masks', 'Diffie-Hellman', 'mask cancellation', 'drop outs', 'Shamir secret sharing', 'self mask', 'gradient leakage', 'Deep Leakage from Gradients'])

K.lesson('systems', 'Real systems, privacy layers and tools', f'''
{talk('A production federated system has more parts than the averaging step. On the client side there is an eligibility check, so training runs only when the phone is idle, charging and on Wi-Fi, a local training runtime, and safeguards on how much data and battery are used. On the server side there are client selection, round timeouts and over selection to handle drop outs, secure aggregation, versioned models, and evaluation on held out clients before a new model is shipped. Privacy comes in layers. Keeping data local is only the first. Secure aggregation hides individual updates. Differential privacy, added to federated averaging by Brendan McMahan and colleagues in 2018 as DP-FedAvg, clips each client’s update to a maximum size and adds calibrated noise to the sum, so the final model provably reveals little about any one user. Trusted execution environments can protect the aggregation code itself. On the threat side, the usual starting assumption is an honest but curious server, one that follows the protocol but would like to learn about users, plus some clients that may be malicious and try to poison the model. Several open source frameworks make this practical: TensorFlow Federated from Google, Flower from the University of Cambridge and Adap, NVIDIA FLARE for hospitals, PySyft from OpenMined, and FATE from WeBank for vertical FL. The next two chapters go deeper on attacks against FL and on differential privacy.')}
{table(['Layer', 'What it protects', 'What it does not'], [
    ['Data stays on device', 'Raw data from the server and from breaches of a central store', 'Information inside the updates'],
    ['Secure aggregation', 'Individual updates from the server', 'What the sum or final model reveals, poisoned updates'],
    ['Differential privacy (DP-FedAvg)', 'Any one user’s influence on the final model, with a provable bound', 'Accuracy, which drops a little as noise grows'],
    ['Trusted execution environment', 'The aggregation code and keys on the server', 'Side channel attacks and bugs inside the enclave'],
    ['Robust aggregation', 'The model from a few poisoned clients', 'Privacy, and it can hurt fairness to unusual clients']])}
{table(['Framework', 'From', 'Typical use'], [
    ['TensorFlow Federated', 'Google', 'Research and simulation of FedAvg and its variants'],
    ['Flower', 'University of Cambridge and Adap', 'Framework agnostic FL from phones to servers'],
    ['NVIDIA FLARE', 'NVIDIA', 'Cross silo FL in hospitals and medical imaging'],
    ['PySyft', 'OpenMined', 'Remote data science with privacy tools'],
    ['FATE', 'WeBank', 'Vertical FL with homomorphic encryption in finance']])}
{fxs(fx('Expected participants after drop outs', 'expected = m &times; (1 &minus; drop rate)', 'C = 0.1 of 1000 clients is m = 100, with 20% drop outs about 80 finish.', key=True))}
''', kw=['FL system design', 'eligibility', 'client selection', 'over selection', 'DP-FedAvg', 'clipping', 'trusted execution environment', 'honest but curious', 'threat model', 'TensorFlow Federated', 'Flower', 'NVIDIA FLARE', 'PySyft', 'FATE'])

K.lesson('versus', 'Federated learning compared with other privacy tools', f'''
{talk('Federated learning is one of several ways to learn from data you should not collect. It is often combined with the others rather than chosen instead of them.')}
{versus('Ways to learn without pooling raw data', ['', 'Central training', 'Federated learning', 'Secure multiparty computation', 'Homomorphic encryption', 'Differential privacy'], [
    ['Raw data moves?', 'Yes, to one server', 'No, only updates', 'Only secret shares', 'Only encrypted data', 'Usually yes, but outputs are noised'],
    ['Protects against', 'Nothing beyond normal security', 'Central data breaches, raw data exposure', 'Every party seeing others’ inputs', 'The server reading the data', 'Learning about any one person from the output'],
    ['Cost', 'Lowest', 'Communication and engineering', 'High communication', 'Very high computation', 'Some accuracy'],
    ['Used for', 'Most ML today', 'Phone keyboards, hospitals, banks', 'Secure aggregation, joint statistics', 'Encrypted scoring, vertical FL steps', 'Census data, DP-FedAvg']],
    'Use FL to keep data local, secure aggregation (a form of MPC) to hide updates, and differential privacy to bound what the final model reveals.')}
''', kw=['comparison', 'MPC', 'homomorphic encryption', 'differential privacy', 'central training'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that phones can help train a shared model without sending their data. A student can write FedAvg, compute weighted averages and communication costs, explain client drift and run secure aggregation by hand. A professional builds cross silo and cross device systems with secure aggregation and differential privacy. Experts research convergence on non IID data, personalisation, and attacks and defences.')}
{ladder(
    '<p>Your phone helps improve the keyboard’s suggestions by training on your typing locally and sending only small model changes, never your messages.</p>',
    '<p>FedAvg w = &Sigma; (n<sub>k</sub>/n) w<sup>k</sup>, FedSGD equals gradient descent, communication cost 2mPb, non IID drift, FedProx and SCAFFOLD, horizontal and vertical FL, pairwise masks and n(n &minus; 1)/2 pairs.</p>',
    '<p>Build FL systems with Flower, TFF or FLARE, handle drop outs and stragglers, add secure aggregation and DP-FedAvg, run cross silo projects with legal agreements, evaluate on held out clients.</p>',
    '<p>Research convergence theory under heterogeneity, personalised and clustered FL, communication efficient methods, FL for large language models, and provable defences against poisoning and leakage.</p>')}
{grow('Explain how a model can learn without collecting the data.',
      'Write FedAvg, measure drift and compute costs and masks by hand.',
      'Design private, robust federated systems for real organisations.')}
''', kw=['beginner', 'expert', 'personalised FL', 'clustered FL', 'convergence'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Idea</b>: send the model to the data. Rounds of select, send, train locally, return, average. McMahan et al. 2016 and 2017, Gboard, FeTS 71 sites.',
    '<b>FedAvg</b>: F = &Sigma; (n<sub>k</sub>/n) F<sub>k</sub>, w<sub>t+1</sub> = &Sigma; (n<sub>k</sub>/n) w<sup>k</sup>, u<sub>k</sub> = E n<sub>k</sub> / B. FedSGD (one full step) equals gradient descent.',
    '<b>Communication</b>: bytes = 2mPb per round. More local steps mean fewer rounds. Top k, quantisation &Delta; = range / (2<sup>bits</sup> &minus; 1), error feedback, idle, charging, Wi-Fi.',
    '<b>Non IID</b>: label, feature and quantity skew cause client drift. FedProx adds (&mu;/2)&Vert;w &minus; w<sub>t</sub>&Vert;<sup>2</sup>, SCAFFOLD corrects with control variates, personalisation fine tunes.',
    '<b>Types</b>: cross device and cross silo. Horizontal (same columns), vertical (same people, PSI then split model with encrypted errors), transfer.',
    '<b>Secure aggregation</b>: y<sub>i</sub> = x<sub>i</sub> + &Sigma; m<sub>ij</sub> &minus; &Sigma; m<sub>ji</sub>, masks cancel, Shamir shares for drop outs, n(n &minus; 1)/2 pairs. Plus DP-FedAvg and robust aggregation.'],
    'Advanced 2.2: attacks on federated learning, gradient leakage and poisoning, and robust aggregation.')}
{files('Three tasks: a FedAvg weighted average, a secure aggregation masked value, and FedProx local training.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In federated learning, what leaves a client’s device?', ['The raw data', 'Model updates (new weights)', 'The user’s password', 'Nothing at all'], 1, 'Model to the data.', 'Raw data stays local. Updates can still leak, hence secure aggregation and DP.')
K.quiz('e', 'Who proposed federated learning and FedAvg?', ['Diffie and Hellman', 'McMahan and colleagues at Google', 'Rivest, Shamir and Adleman', 'Denning'], 1, '2016 to 2017.', 'Gboard used it for next word prediction.')
K.quiz('e', 'How does FedAvg combine client models?', ['Takes the best one', 'A weighted average by data size', 'Multiplies them', 'Random choice'], 1, 'n<sub>k</sub> / n.', 'Clients with more data count more.')
K.quiz('e', 'A bank and a shop with the same customers but different columns use', ['Horizontal FL', 'Vertical FL', 'Cross device FL', 'Central training'], 1, 'Same rows, different columns.', 'They first find shared customers with a private set intersection.')
K.quiz('m', 'FedSGD (one full batch step per client) is equivalent to', ['Random search', 'Gradient descent on the pooled data', 'Adam', 'No learning'], 1, 'Weighted gradients.', '&Sigma; (n<sub>k</sub>/n) &nabla;F<sub>k</sub> = &nabla;F.')
K.quiz('m', 'Why does FedAvg let clients take many local steps?', ['To use more battery', 'To cut the number of communication rounds', 'To hide data', 'It is required by law'], 1, 'Communication is the bottleneck.', 'McMahan et al. reported 10 to 100 times fewer rounds.')
K.quiz('m', 'What is client drift?', ['Phones moving between cities', 'Local models running towards their own optimum on non IID data, so the average is off', 'Clock skew', 'Slow uploads'], 1, 'Many local steps plus different data.', 'FedProx and SCAFFOLD reduce it.')
K.quiz('m', 'What does the FedProx term (&mu;/2)&Vert;w &minus; w<sub>t</sub>&Vert;<sup>2</sup> do?', ['Speeds up uploads', 'Keeps each local model close to the global model', 'Encrypts updates', 'Removes clients'], 1, 'Proximal.', 'Larger &mu; means less drift but slower local progress.')
K.quiz('m', 'In secure aggregation, why do the pairwise masks cancel?', ['They are zero', 'Each mask is added by one client and subtracted by the other', 'The server removes them', 'They are encrypted'], 1, 'Plus and minus.', 'The sum of masked updates equals the sum of true updates mod M.')
K.quiz('h', 'How does secure aggregation recover when a client drops out?', ['It restarts from scratch', 'Survivors send Shamir shares so the server can rebuild only the dropped client’s pairwise masks', 'It ignores the problem', 'It asks the user'], 1, 'Secret sharing.', 'Masks between survivors stay secret.')
K.quiz('h', 'Two clients have losses (a/2)(w &minus; c)<sup>2</sup> with a = 1, 4 and c = 0, 10, equal data. With 50 local steps per round, FedAvg ends near', ['8', '5', '10', '0'], 1, 'Each runs to its own optimum.', 'The true optimum is 8, the average of 0 and 10 is 5: client drift.')
K.quiz('h', 'Why is a salted hash a weak way to match customers in vertical FL?', ['Hashes are slow', 'IDs and phone numbers are easy to guess, so an attacker can hash every possible value', 'Salts are illegal', 'It always fails'], 1, 'Small input space.', 'Real systems use a private set intersection protocol.')
K.quiz('h', 'Which layer bounds what the final model reveals about any one user?', ['Data staying on device', 'Secure aggregation', 'Differential privacy (DP-FedAvg)', 'Compression'], 2, 'A provable bound.', 'Clipping and noise limit each user’s influence.')
K.quiz('x', 'In the style of a CMU 10-605 question: with C = 0.1, K = 1000 clients, P = 1.4 million float32 parameters, how many bytes move per round, down and up?', ['5.6 MB', 'About 1.12 GB', '1.4 MB', '140 GB'], 1, '2 m P b.', '2 &times; 100 &times; 1400000 &times; 4 = 1.12 &times; 10<sup>9</sup>.')
K.quiz('x', 'In the style of an IIT Madras ML systems viva: SCAFFOLD removes client drift by', ['Using fewer clients', 'Correcting each local gradient with control variates c &minus; c<sub>k</sub>', 'Adding noise', 'Freezing the model'], 1, 'Variance reduction.', 'The step uses g<sub>k</sub> &minus; c<sub>k</sub> + c, an estimate of the global gradient.')

K.calc('e', 'Clients hold 50, 30 and 20 examples with local weights 1.2, 0.8 and 2.0. FedAvg weight?', '1.24', 'Weighted by n<sub>k</sub>/n.', ['Weights 0.5, 0.3, 0.2.', '0.6 + 0.24 + 0.4.', eq('1.24')], check=1.24)
K.calc('e', 'E = 5, n<sub>k</sub> = 600, B = 20. Local updates per round?', '150', 'E n / B.', ['600 / 20 = 30 batches.', 'Times 5 epochs.', eq('150')], check=150)
K.calc('e', 'How many pairwise masks do 100 clients need?', '4950', 'n(n &minus; 1)/2.', ['100 &times; 99 = 9900.', 'Divide by 2.', eq('4950')], check=4950)
K.calc('m', '100 clients, 1.4 million parameters of 4 bytes, down and up. Megabytes per round (10<sup>6</sup> bytes)?', '1120', '2 m P b.', ['2 &times; 100 = 200 transfers.', '200 &times; 1400000 &times; 4 = 1120000000 bytes.', eq('1120 MB')], check=1120)
K.calc('m', 'Quadratic clients a = (1, 4), c = (0, 10), equal data. Global optimum w*?', '8', '&Sigma; a c / &Sigma; a.', ['1 &times; 0 + 4 &times; 10 = 40.', '1 + 4 = 5.', eq('40 / 5 = 8')], check=8)
K.calc('m', 'Secure aggregation mod 100: phone 3 has 8 and subtracts masks 81 and 56. What does it send?', '71', 'Reduce mod 100.', ['8 &minus; 81 &minus; 56 = &minus;129.', '&minus;129 + 200 = 71.', eq('71')], check=71)
K.calc('m', 'Top 1% of 1000000 values sent with 4 byte index and 4 byte value. Bytes?', '80000', 'k &times; 8.', ['k = 10000.', '10000 &times; 8.', eq('80000, against 4000000 for the full update')], check=80000)
K.calc('m', 'FedProx gradient: a = 4, w = 6, c = 10, &mu; = 1, w<sub>t</sub> = 5.', '-15', 'a(w &minus; c) + &mu;(w &minus; w<sub>t</sub>).', ['4 &times; (6 &minus; 10) = &minus;16.', '1 &times; (6 &minus; 5) = 1.', eq('&minus;15')], check=-15)
K.calc('h', 'One local step from w = 0 with &eta; = 0.1 on a = 4, c = 10. New w?', '4', 'w &minus; &eta; a (w &minus; c).', ['Gradient 4 &times; (0 &minus; 10) = &minus;40.', '0 &minus; 0.1 &times; (&minus;40).', eq('4')], check=4)
K.calc('h', 'FedSGD: client gradients 2, &minus;1, 4 with weights 0.5, 0.3, 0.2, w = 1, &eta; = 0.1. New w?', '0.85', 'Average the gradients first.', ['0.5 &times; 2 &minus; 0.3 + 0.2 &times; 4 = 1.5.', '1 &minus; 0.1 &times; 1.5.', eq('0.85')], check=0.85)
K.calc('h', '8 bit quantisation of values from &minus;1.5 to 2.5. Step size? Round to 4 decimals.', '0.0157', 'range / 255.', ['Range = 4.', '4 / 255.', eq('&asymp; 0.0157')], check=round(4 / 255, 4))
K.calc('h', 'C = 0.1 of 1000 clients, 20% drop out. Expected clients that finish?', '80', 'm (1 &minus; drop).', ['m = 100.', '100 &times; 0.8.', eq('80')], check=80)
K.calc('x', 'FedProx local optimum for a = 4, c = 10, &mu; = 1, w<sub>t</sub> = 0?', '8', '(a c + &mu; w<sub>t</sub>) / (a + &mu;).', ['Set the gradient a(w &minus; c) + &mu;(w &minus; w<sub>t</sub>) to 0.', '(40 + 0) / 5.', eq('8 instead of the local 10')], check=8)
K.calc('x', 'Secure aggregation mod 100 after phone 3 drops: survivors sent 30 and 24, and phone 3 shared masks 81 and 56. Recovered sum?', '17', 'Remove the masks shared with phone 3.', ['30 + 24 = 54.', '54 &minus; 81 &minus; 56 = &minus;83.', eq('&minus;83 + 100 = 17 = 12 + 5')], check=17)

K.assign('fedavg_aggregate', 'e', 'FedAvg weighted average',
         '<p>updates is a list of client weight lists, sizes the number of examples per client. Write <code>fedavg_aggregate(updates, sizes)</code> that returns the weighted average list, each value rounded to 4 decimals.</p>',
         '''
def fedavg_aggregate(updates, sizes):
    # your code here
    pass
''', [('fedavg_aggregate([[1.2], [0.8], [2.0]], [50, 30, 20])', [1.24]),
      ('fedavg_aggregate([[1.0, 2.0], [3.0, 4.0]], [1, 1])', [2.0, 3.0]),
      ('fedavg_aggregate([[0.0, 10.0], [10.0, 0.0]], [3, 1])', [2.5, 7.5])],
         '''
def fedavg_aggregate(updates, sizes):
    total = sum(sizes)
    out = [0.0] * len(updates[0])
    for w, n in zip(updates, sizes):
        for i in range(len(w)):
            out[i] += n / total * w[i]
    return [round(v, 4) for v in out]
''', 'Divide each size by the total, then add weight times value for every position.', '<p>Production systems often send the difference from the global weights instead of the weights, which compresses better and works the same way.</p>')
K.assign('masked_value', 'm', 'Secure aggregation masked value',
         '<p>masks is a dictionary from pairs (a, b) with a &lt; b to the mask they share. Write <code>masked_value(i, x, masks, M)</code> that returns x plus every mask where i is the first of the pair, minus every mask where i is the second, all mod M.</p>',
         '''
def masked_value(i, x, masks, M):
    # your code here
    pass
''', [('masked_value(1, 12, {(1, 2): 37, (1, 3): 81, (2, 3): 56}, 100)', 30),
      ('masked_value(2, 5, {(1, 2): 37, (1, 3): 81, (2, 3): 56}, 100)', 24),
      ('masked_value(3, 8, {(1, 2): 37, (1, 3): 81, (2, 3): 56}, 100)', 71)],
         '''
def masked_value(i, x, masks, M):
    total = x
    for (a, b), m in masks.items():
        if a == i:
            total += m
        elif b == i:
            total -= m
    return total % M
''', 'Loop over the pairs. Add when i is first, subtract when i is second, then take % M.', '<p>Check it yourself: 30 + 24 + 71 = 125, and 125 mod 100 = 25 = 12 + 5 + 8. Python’s % always returns a value from 0 to M &minus; 1, even for negative totals.</p>')
K.assign('fedprox_local', 'h', 'FedProx local training',
         '<p>A client’s loss is (a/2)(w &minus; c)<sup>2</sup>. Write <code>fedprox_local(w, a, c, w_global, mu, lr, steps)</code> that takes <code>steps</code> gradient steps on the FedProx objective, whose gradient is a(w &minus; c) + mu(w &minus; w_global), and returns w rounded to 4 decimals.</p>',
         '''
def fedprox_local(w, a, c, w_global, mu, lr, steps):
    # your code here
    pass
''', [('fedprox_local(0.0, 4.0, 10.0, 0.0, 0.0, 0.1, 1)', 4.0),
      ('fedprox_local(0.0, 4.0, 10.0, 0.0, 1.0, 0.1, 50)', 8.0),
      ('fedprox_local(2.0, 2.0, 2.0, 0.0, 1.0, 0.2, 3)', 1.376)],
         '''
def fedprox_local(w, a, c, w_global, mu, lr, steps):
    for _ in range(steps):
        grad = a * (w - c) + mu * (w - w_global)
        w = w - lr * grad
    return round(w, 4)
''', 'Repeat steps times: compute the gradient with the proximal term, then move against it.', '<p>With mu = 0 this is plain FedAvg local training. As steps grow the result approaches (a c + mu w_global) / (a + mu), a compromise between the local and global models.</p>')

K.must('Idea and terms', 'Send the model to the data. Rounds: select clients (fraction C), send w<sub>t</sub>, local training (E epochs, batch B, rate &eta;), return weights, average. McMahan et al. 2016 and 2017, Gboard 2017, FeTS 71 sites (2022), Kairouz et al. 2021.')
K.must('FedAvg maths', 'F(w) = &Sigma; (n<sub>k</sub>/n) F<sub>k</sub>(w). w<sub>t+1</sub> = &Sigma; (n<sub>k</sub>/n) w<sup>k</sup><sub>t+1</sub>. u<sub>k</sub> = E n<sub>k</sub>/B. FedSGD = gradient descent because &Sigma; (n<sub>k</sub>/n)&nabla;F<sub>k</sub> = &nabla;F.')
K.must('Communication', 'Bytes per round 2mPb (100 clients, 1.4M float32 params: 1.12 GB). More local steps, fewer rounds (10 to 100 times). Top k, quantisation &Delta; = range/(2<sup>bits</sup> &minus; 1), error feedback. Clients join when idle, charging, on Wi-Fi.')
K.must('Non IID and drift', 'Label, feature, quantity skew. Drift: average of local optima is not the global optimum (quadratic: w* = &Sigma;a c/&Sigma;a). FedProx + (&mu;/2)&Vert;w &minus; w<sub>t</sub>&Vert;<sup>2</sup>. SCAFFOLD g &minus; c<sub>k</sub> + c. Personalisation.')
K.must('Types', 'Cross device (millions, few per round, drop outs) and cross silo (few organisations, all rounds). Horizontal (same columns), vertical (same people: PSI, split model, encrypted errors, FATE), federated transfer learning.')
K.must('Secure aggregation and layers', 'Bonawitz 2017: y<sub>i</sub> = x<sub>i</sub> + &Sigma;<sub>j&gt;i</sub> m<sub>ij</sub> &minus; &Sigma;<sub>j&lt;i</sub> m<sub>ji</sub> mod M, masks from DH, cancel in the sum, Shamir shares for drop outs, n(n &minus; 1)/2 pairs. Layers: local data, SecAgg, DP-FedAvg, TEE, robust aggregation.')

T = K.topic(
    slug='cy-fedlearn', topic='cy-fedlearn', step=(2, 'Federated learning and privacy', 'cy-a2', 'Training models across many devices and organisations without collecting their data, the attacks on such systems, and differential privacy.', 'Advanced'),
    title='Federated learning in full', short='Federated learning', badge='2.1', minutes=90,
    lead='Training one model across phones, hospitals and banks without moving their data: the FedAvg algorithm with its maths and the link to gradient descent, communication costs and compression, non IID data with client drift, FedProx and SCAFFOLD, cross device and cross silo, horizontal and vertical FL, secure aggregation with masks and drop out recovery, and how real systems are built.',
    desc='federated learning, FL, FedAvg, federated averaging, FedSGD, McMahan, Gboard, FeTS, global objective, weighted average, client fraction, local epochs, communication cost, compression, top k sparsification, quantisation, error feedback, non IID, client drift, FedProx, SCAFFOLD, personalisation, cross device, cross silo, horizontal federated learning, vertical federated learning, private set intersection, Paillier, FATE, secure aggregation, Bonawitz, pairwise masks, Shamir, drop outs, DP-FedAvg, TensorFlow Federated, Flower, NVIDIA FLARE, PySyft',
    summary='FedAvg and its maths, communication and compression, non IID drift with FedProx and SCAFFOLD, cross device and cross silo, horizontal and vertical FL, secure aggregation, real systems.',
    keywords=['federated learning', 'FedAvg', 'FedSGD', 'non IID', 'client drift', 'FedProx', 'SCAFFOLD', 'vertical FL', 'secure aggregation', 'communication cost', 'DP-FedAvg'],
    recap='<p>Keep data where it lives, average local models weighted by data size, cut rounds and message size, fight drift on non IID data, and hide each update with secure aggregation.</p>',
    added='2026-11-15')
