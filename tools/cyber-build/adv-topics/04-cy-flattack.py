# Advanced 2.2: attacks on federated learning and the defences. Checked against Phong et al. (IEEE TIFS 2018, first
# shown 2017), Zhu, Liu and Han, "Deep Leakage from Gradients" (NeurIPS 2019), Zhao et al., iDLG (2020), Geiping et al.,
# "Inverting Gradients" (NeurIPS 2020), Melis et al. (IEEE S&P 2019), Hitaj, Ateniese and Perez-Cruz (ACM CCS 2017),
# Nasr, Shokri and Houmansadr (IEEE S&P 2019), Bagdasaryan et al., "How To Backdoor Federated Learning" (AISTATS 2020),
# Bhagoji et al. (ICML 2019), Sun et al., "Can You Really Backdoor Federated Learning?" (2019), Wang et al., edge case
# backdoors (NeurIPS 2020), Lamport, Shostak and Pease (1982), Blanchard et al., Krum (NeurIPS 2017), Yin et al.,
# median and trimmed mean (ICML 2018), Baruch et al., "A Little Is Enough" (NeurIPS 2019), Fang et al. (USENIX Security
# 2020), Cao et al., FLTrust (NDSS 2021), Douceur, "The Sybil Attack" (IPTPS 2002), Fung, Yoon and Beschastnikh,
# FoolsGold (2018, RAID 2020), Lin et al. on free riders (2019) and Kairouz et al. (2021).
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, safe

chapter('cy-flattack')
K = Kit()

K.code('grad_leak', r'''
# Gradient leakage: why the server must not see one client's update. For a dense layer z = W x + b and one example,
# dL/dW = delta * x (an outer product) and dL/db = delta, so dividing a row of dL/dW by dL/db gives x back exactly.
import math
import random

random.seed(5)
x = [0.9, 0.1, 0.7, 0.3]                  # a private input: say four pixel brightnesses, or four health values
W = [[random.uniform(-1, 1) for _ in range(4)] for _ in range(2)]
b = [0.0, 0.0]
y = [1, 0]                                 # one hot label

def gradients(x, y):
    z = [sum(W[r][c] * x[c] for c in range(4)) + b[r] for r in range(2)]
    e = [math.exp(v) for v in z]
    p = [v / sum(e) for v in e]            # softmax
    delta = [p[r] - y[r] for r in range(2)] # dL/dz for cross entropy
    gW = [[delta[r] * x[c] for c in range(4)] for r in range(2)]
    return gW, delta

gW, gb = gradients(x, y)
recovered = [round(gW[0][c] / gb[0], 4) for c in range(4)]
print("private input:      ", x)
print("rebuilt from update:", recovered)

# a batch of 4 examples: the update is the average, so division gives a mix of the inputs
batch = [[0.9, 0.1, 0.7, 0.3], [0.2, 0.8, 0.4, 0.6], [0.5, 0.5, 0.9, 0.1], [0.1, 0.3, 0.2, 0.9]]
labels = [[1, 0], [0, 1], [1, 0], [0, 1]]
avgW = [[0.0] * 4 for _ in range(2)]
avgb = [0.0, 0.0]
for xi, yi in zip(batch, labels):
    g, d = gradients(xi, yi)
    for r in range(2):
        avgb[r] += d[r] / 4
        for c in range(4):
            avgW[r][c] += g[r][c] / 4
print("batch of 4, rebuilt: ", [round(avgW[0][c] / avgb[0], 4) for c in range(4)], " (a mix, not one person's input)")
print("\nDefences: secure aggregation (server sees only sums), bigger batches, and DP noise. Optimisation attacks")
print("such as Deep Leakage from Gradients (2019) can still separate small batches, so do not rely on batching alone.")
''', long=True)

K.code('model_replace', r'''
# Model replacement (Bagdasaryan et al. 2020): one client scales its update so the average becomes its own model.
# The server uses G_new = G + (eta / n) * sum(L_i - G), where L_i are the clients' models.
import math

G = [1.0, 2.0]                     # current global model (two weights to keep it readable)
n, eta = 10, 1.0                   # 10 clients this round, server learning rate 1
honest = [[1.0 + 0.05 * i, 2.0 - 0.03 * i] for i in range(9)]   # small, sensible changes
X = [5.0, -3.0]                    # the attacker's backdoored model

gamma = n / eta                    # boost factor
attacker = [G[k] + gamma * (X[k] - G[k]) for k in range(2)]
print("attacker sends", [round(v, 2) for v in attacker], "after boosting by", gamma)

def aggregate(models, clip=None):
    upd = [0.0, 0.0]
    for L in models:
        d = [L[k] - G[k] for k in range(2)]
        size = math.hypot(*d)
        if clip and size > clip:
            d = [v * clip / size for v in d]          # norm clipping: no change may be longer than clip
        upd = [upd[k] + d[k] for k in range(2)]
    return [G[k] + eta / n * upd[k] for k in range(2)]

print("FedAvg result:          ", [round(v, 3) for v in aggregate(honest + [attacker])], "  close to X =", X)
print("with norm clip 1.0:     ", [round(v, 3) for v in aggregate(honest + [attacker], clip=1.0)])
print("if the attacker sent no change:", [round(v, 3) for v in aggregate(honest)])
''')

K.code('robust_agg', r'''
# Byzantine robust aggregation: the mean, coordinate wise median, trimmed mean and Krum against 3 bad clients of 10
import statistics as st

honest = [[1.0, 0.5], [1.1, 0.4], [0.9, 0.6], [1.05, 0.55], [0.95, 0.45], [1.2, 0.5], [0.85, 0.5]]
bad = [[-8.0, 9.0], [-8.5, 9.5], [-7.5, 8.5]]          # attackers push the model the wrong way together
updates = honest + bad
f = len(bad)

def mean(us):
    return [sum(u[k] for u in us) / len(us) for k in range(2)]

def median(us):
    return [st.median(u[k] for u in us) for k in range(2)]

def trimmed_mean(us, beta):
    out = []
    for k in range(2):
        vals = sorted(u[k] for u in us)[beta:len(us) - beta]   # drop the beta smallest and largest
        out.append(sum(vals) / len(vals))
    return out

def krum(us, f):
    # score each update by its summed squared distance to its n - f - 2 nearest neighbours, pick the lowest
    scores = []
    for i, u in enumerate(us):
        d = sorted(sum((u[k] - v[k]) ** 2 for k in range(2)) for j, v in enumerate(us) if j != i)
        scores.append(sum(d[:len(us) - f - 2]))
    return us[scores.index(min(scores))]

print("true honest mean:  ", [round(v, 3) for v in mean(honest)])
print("plain mean:        ", [round(v, 3) for v in mean(updates)], "  dragged away by 3 attackers")
print("coordinate median: ", [round(v, 3) for v in median(updates)])
print("trimmed mean b=3:  ", [round(v, 3) for v in trimmed_mean(updates, 3)])
print("Krum (f=3):        ", krum(updates, f))
''', long=True)

K.code('robust_train', r'''
# A full federated run with 3 malicious clients out of 10: plain FedAvg against a coordinate wise median
import math
import random
import statistics as st

random.seed(7)
def make(n):
    data = []
    for _ in range(n):
        y = random.randint(0, 1)
        c = 0.7 if y else 0.3
        data.append(([random.gauss(c, 0.12), random.gauss(c, 0.12)], y))
    return data

clients = [make(40) for _ in range(10)]
test = make(300)
MALICIOUS = {7, 8, 9}

def local_update(w, data, bad, steps=20, lr=0.5):
    w = list(w)
    for _ in range(steps):
        g = [0.0, 0.0, 0.0]
        for x, y in data:
            if bad:
                y = 1 - y                                   # flip every label
            p = 1 / (1 + math.exp(-(w[0] * x[0] + w[1] * x[1] + w[2])))
            g = [g[0] + (p - y) * x[0], g[1] + (p - y) * x[1], g[2] + (p - y)]
        w = [w[k] - lr * g[k] / len(data) for k in range(3)]
    if bad:
        w = [v * 3 for v in w]                              # and boost the bad model
    return w

def accuracy(w):
    return sum(((w[0] * x[0] + w[1] * x[1] + w[2]) > 0) == y for x, y in test) / len(test)

for rule in ("mean", "median"):
    w = [0.0, 0.0, 0.0]
    for rnd in range(15):
        locals_ = [local_update(w, d, i in MALICIOUS) for i, d in enumerate(clients)]
        if rule == "mean":
            w = [sum(l[k] for l in locals_) / len(locals_) for k in range(3)]
        else:
            w = [st.median(l[k] for l in locals_) for k in range(3)]
    print(f"{rule:6} aggregation: test accuracy {accuracy(w):.3f}")
''', long=True)

K.code('sybil_cosine', r'''
# Spotting Sybils (fake clients run by one attacker): their updates point the same way round after round.
# FoolsGold (Fung et al.) lowers the weight of clients whose update history is too similar to another client's.
import math
import random

random.seed(11)
def honest_update():
    return [random.gauss(0, 1) for _ in range(6)]       # honest users have different data, so different directions

goal = [0.0, 0.0, 0.0, 0.0, 2.0, -2.0]                  # the attacker's poisoned direction
history = {f"user{i}": [0.0] * 6 for i in range(1, 6)}
history.update({f"sybil{i}": [0.0] * 6 for i in range(1, 4)})

for rnd in range(5):                                    # add up each client's updates over 5 rounds
    for name in history:
        if name.startswith("sybil"):
            u = [g + random.gauss(0, 0.1) for g in goal]
        else:
            u = honest_update()
        history[name] = [h + v for h, v in zip(history[name], u)]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

names = list(history)
for a in names:
    top = max(cosine(history[a], history[b]) for b in names if b != a)
    weight = max(0.0, min(1.0, 1 - top))                # very similar to someone else: weight near 0
    print(f"{a:7} highest similarity to another client {top:5.2f}  -> weight {weight:.2f}")
''', long=True)

K.lesson('idea', 'Who can attack a federated system?', f'''
{talk('Federated learning keeps raw data on the devices, which removes one big risk. But it opens new ones, because the server and every client now take part in training. A threat model asks who might be malicious and what they want. The server might be honest but curious, following the protocol while trying to learn about users from their updates, or fully malicious, sending clients a specially crafted model to make their updates leak more. Clients might be malicious too. In cross device FL anyone can install the app, so an attacker can control some phones, or create thousands of fake ones, which is called a Sybil attack after a 2002 paper by John Douceur. Malicious clients can try to poison the model, either to ruin it, called an untargeted or availability attack, or to plant a backdoor that only they can trigger. Some clients just want the final model without contributing, the free rider problem. And outsiders can attack the finished model with the methods from Advanced 1.2. Two goals pull against each other here. For privacy we want the server to see as little as possible about each update. For robustness we want the server to inspect updates and reject bad ones. This chapter studies the attacks on both sides on toy models, and the layered defences used in practice.')}
{src('Phong et al. (2018), Zhu et al. (2019), Zhao et al. (2020), Geiping et al. (2020), Melis et al. (2019), Hitaj et al. (2017), Nasr et al. (2019), Bagdasaryan et al. (2020), Bhagoji et al. (2019), Sun et al. (2019), Wang et al. (2020), Lamport et al. (1982), Blanchard et al. (2017), Yin et al. (2018), Baruch et al. (2019), Fang et al. (2020), Cao et al. (2021), Douceur (2002), Fung et al. (2018), Lin et al. (2019), Kairouz et al. (2021).')}
{wwh('<b>Attacks on federated learning</b> either pull private information out of the updates (privacy attacks) or corrupt the shared model through malicious updates (poisoning and backdoors).',
     'FL is used for keyboards, medical imaging and finance. A curious server could learn users’ data, and a few bad clients could plant a backdoor in a model used by millions.',
     'Hide individual updates with secure aggregation and DP noise, limit each client’s influence with clipping and robust aggregation, authenticate clients and detect Sybils, and validate every new model before release.')}
{table(['Who', 'What they want', 'Example attack', 'Main defence'], [
    ['Honest but curious server', 'Learn users’ private data', 'Rebuild inputs from one client’s gradients', 'Secure aggregation, DP noise'],
    ['Malicious server', 'Learn more by cheating', 'Send a crafted model that makes updates leak, fake drop outs', 'Verifiable protocols, client side checks, minimum round size'],
    ['Malicious clients', 'Ruin the model or plant a backdoor', 'Label flipping, boosted model replacement', 'Clipping, robust aggregation, validation'],
    ['Sybil attacker', 'Gain many votes cheaply', 'Thousands of fake phones pushing one direction', 'Device attestation, rate limits, similarity checks'],
    ['Free rider', 'Get the model without contributing', 'Send random or stale updates', 'Contribution checks, incentives'],
    ['Outsider', 'Attack the final model', 'Evasion, membership inference (Advanced 1.2)', 'Robust training, DP']])}
{safe('These attacks are shown on toy models inside the page. Federated systems in production belong to their operators: test them only with permission, through their bug bounty or research programmes.')}
''', kw=['threat model', 'honest but curious', 'malicious server', 'malicious clients', 'Sybil attack', 'Douceur', 'free rider', 'privacy versus robustness', 'availability attack', 'backdoor'])

K.lesson('leak', 'Privacy attacks: what one update reveals', f'''
{talk('An early surprise in federated learning was how much a single update can reveal. In 2017 Le Trieu Phong and colleagues pointed out that for a single example passing through a dense layer with a bias, the input can be read straight from the gradient. The gradient of a weight row is the error signal times the input, and the gradient of the bias is the error signal itself, so dividing one by the other gives the input back exactly. Our animation and program show it. In 2019 Ligeng Zhu, Zhijian Liu and Song Han went further with Deep Leakage from Gradients. They start with a random fake image and label, compute the gradient it would produce, and adjust the fake until its gradient matches the real one. The fake turns into the real training image, pixel for pixel, for small batches. In 2020 Jonas Geiping and colleagues rebuilt recognisable ImageNet photos from realistic updates. Other attacks learn properties rather than full inputs. Luca Melis and colleagues showed in 2019 that updates can reveal, for example, whether people in a client’s photos wear glasses, or when a certain person appears in a client’s data. And if the server is malicious it can send clients a specially chosen model that makes their updates leak even more. The defences follow from the maths. Never let the server see a single client’s update, which is what secure aggregation guarantees. Add differential privacy noise, which bounds what anyone can learn about one example or one user. Larger batches and more local steps make simple inversion harder, but they are not a defence on their own.')}
{viz('cygradleak')}
{run('grad_leak')}
{fxs(fx('Gradient of a dense layer for one example', '&part;L/&part;W<sub>r</sub> = &delta;<sub>r</sub> x, &part;L/&part;b<sub>r</sub> = &delta;<sub>r</sub>', 'z = W x + b and &delta;<sub>r</sub> = &part;L/&part;z<sub>r</sub>.', key=True),
     fx('Reading the input back', 'x = (&part;L/&part;W<sub>r</sub>) / (&part;L/&part;b<sub>r</sub>)', '&delta; = &minus;0.62 and gradient entry &minus;0.558: &minus;0.558 / &minus;0.62 = 0.9.', key=True),
     fx('Deep Leakage from Gradients', 'x&#770;, y&#770; = argmin &Vert;&nabla;W(x&#770;, y&#770;) &minus; &nabla;W<sub>real</sub>&Vert;<sup>2</sup>', 'Optimise a fake input until its gradient matches the shared one.'))}
{deep('Why batches only blur', '<p>For a batch of B examples the shared gradient is the average of the per example gradients, so the division gives &Sigma; &delta;<sub>i</sub> x<sub>i</sub> / &Sigma; &delta;<sub>i</sub>, a weighted mix of inputs whose weights can be negative. Optimisation attacks treat all B inputs as unknowns and solve for them together, which works for small B. Zhao et al. (2020) also showed the label of a single example can be read from the sign of the last layer’s gradient.</p>')}
''', kw=['gradient leakage', 'gradient inversion', 'Phong', 'Deep Leakage from Gradients', 'DLG', 'iDLG', 'Geiping', 'property inference', 'Melis', 'malicious server', 'batch size', 'secure aggregation', 'differential privacy'])

K.lesson('poison', 'Poisoning and backdoors in federated learning', f'''
{talk('Poisoning is easier in federated learning than in central training, because the server cannot see the clients’ data and cannot check their labels. Data poisoning means a malicious client trains honestly on bad data, for example with flipped labels. Model poisoning is stronger: the client sends whatever update it likes. In 2020 Eugene Bagdasaryan and colleagues showed model replacement. The server adds the average of the clients’ changes to the global model. If an attacker wants the global model to become its own backdoored model X, it can send its change multiplied by n over eta, where n is the number of clients in the round and eta the server learning rate. When everyone else’s changes are small, they nearly cancel, and the new global model lands almost exactly on X, after a single round. The backdoor might make a keyboard suggest a chosen brand after certain words, or a classifier label cars with racing stripes as birds. Arjun Bhagoji and colleagues showed similar boosting attacks in 2019, and Hongyi Wang and colleagues in 2020 showed backdoors on rare edge case inputs are both effective and hard to spot. The first line of defence is norm clipping: no client’s change may be longer than a bound M. Ziteng Sun and colleagues at Google showed in 2019 that clipping plus a little Gaussian noise, the same steps used for differential privacy, stops most simple backdoors when attackers are a small fraction.')}
{viz('cyreplace')}
{run('model_replace')}
{fxs(fx('Server update with a learning rate', 'G<sub>t+1</sub> = G<sub>t</sub> + (&eta; / n) &Sigma;<sub>i</sub> (L<sub>i</sub> &minus; G<sub>t</sub>)', 'With &eta; = 1 this is exactly the FedAvg average of the clients’ models.', key=True),
     fx('Model replacement boost', 'L<sub>m</sub> = G<sub>t</sub> + &gamma; (X &minus; G<sub>t</sub>), &gamma; = n / &eta;', 'n = 10, &eta; = 1: &gamma; = 10. If other changes cancel, G<sub>t+1</sub> &asymp; X.', key=True),
     fx('Norm clipping', '&Delta; &larr; &Delta; &middot; min(1, M / &Vert;&Delta;&Vert;)', 'A change of length 5 with M = 1 is scaled by 0.2 to length 1.', key=True))}
{table(['Attack', 'What the client sends', 'Goal', 'Defence'], [
    ['Data poisoning (label flipping)', 'An honest update trained on bad labels', 'Lower accuracy or target a class', 'Robust aggregation, validation'],
    ['Model poisoning (boosting)', 'A crafted, scaled update', 'Replace the global model', 'Norm clipping, robust aggregation'],
    ['Backdoor', 'An update that adds a trigger rule', 'Hidden behaviour on a trigger', 'Clipping with noise, anomaly checks, validation'],
    ['Edge case backdoor', 'A backdoor on rare inputs', 'Stay hidden from accuracy checks', 'Hard: test on diverse data, limit influence']])}
''', kw=['poisoning', 'data poisoning', 'model poisoning', 'model replacement', 'Bagdasaryan', 'boosting', 'Bhagoji', 'backdoor', 'edge case backdoor', 'norm clipping', 'weak differential privacy', 'Sun et al.'])

K.lesson('robust', 'Robust aggregation: surviving Byzantine clients', f'''
{talk('Byzantine is the name computer science gives to a participant that may behave in any arbitrary way, after the Byzantine generals problem described by Leslie Lamport, Robert Shostak and Marshall Pease in 1982. Robust aggregation replaces the plain average with a rule that a minority of Byzantine clients cannot drag far away. The coordinate wise median takes the middle value of each weight separately. It stays among the honest values as long as attackers are fewer than half, which is called a breakdown point of 50 percent. The trimmed mean, studied by Dong Yin and colleagues in 2018 together with the median, drops the beta largest and beta smallest values of each coordinate and averages the rest, which is safe while there are no more than beta attackers. Krum, from Peva Blanchard and colleagues in 2017, picks the single client update whose nearest neighbours are closest, and needs n greater than 2f plus 2. FLTrust, from Xiaoyu Cao and colleagues in 2021, lets the server keep a small clean dataset and trust clients in proportion to how well their update agrees with the update from that data. These rules are not magic. They throw away information from unusual but honest clients, which hurts non IID users, and clever attackers can craft updates that sit just inside the accepted range. Moran Baruch and colleagues showed in 2019 with A Little Is Enough that small coordinated shifts inside the normal spread can still steer the model, and Minghong Fang and colleagues in 2020 built attacks tuned to each robust rule.')}
{viz('cyrobust')}
{run('robust_agg')}
{run('robust_train')}
{fxs(fx('Coordinate wise median', 'G<sub>k</sub> = median(u<sub>1,k</sub>, ..., u<sub>n,k</sub>) for each weight k', 'Breakdown point 50%: safe while f &lt; n/2.', key=True),
     fx('Trimmed mean', 'G<sub>k</sub> = mean of the values left after dropping the &beta; smallest and &beta; largest', 'Needs &beta; &ge; f. n = 10, &beta; = 3: average the middle 4.', key=True),
     fx('Krum score', 's(i) = &Sigma;<sub>j in the n &minus; f &minus; 2 nearest to i</sub> &Vert;u<sub>i</sub> &minus; u<sub>j</sub>&Vert;<sup>2</sup>, pick the lowest', 'Safe when n &gt; 2f + 2: n = 10 tolerates f = 3.', key=True))}
''', kw=['Byzantine', 'Byzantine generals', 'Lamport', 'robust aggregation', 'coordinate wise median', 'trimmed mean', 'breakdown point', 'Krum', 'FLTrust', 'A Little Is Enough', 'adaptive attack', 'Fang et al.'])

K.lesson('sybil', 'Sybils, free riders and client checks', f'''
{talk('Robust aggregation assumes attackers are a minority. In cross device FL that assumption can fail if creating a client is free: an attacker could run thousands of fake phones and become the majority. John Douceur named this the Sybil attack in 2002, after a book about a woman with many personalities, and showed that without some central check it cannot be fully prevented. So the first defences are about identity. Real deployments ask devices to prove they are genuine, unmodified phones using hardware backed attestation, limit how many updates any account or device can send, and sample clients randomly so an attacker cannot choose to be in every round. A second defence looks at behaviour. Sybils controlled by one attacker push the same goal, so their updates point in the same direction round after round, while honest users with different data point in different directions. FoolsGold, from Clement Fung, Chris Yoon and Ivan Beschastnikh in 2018, measures the cosine similarity between clients’ update histories and lowers the weight of clients that are too similar to someone else, as our animation and program show in simplified form. A careful attacker can add noise to look diverse, so this is one layer, not a complete answer. Free riders are a quieter problem: clients who send random or stale updates to receive the final model without spending their data or battery. Checking each update’s contribution on a validation set and rewarding honest work are the usual answers.')}
{viz('cysybil')}
{run('sybil_cosine')}
{fxs(fx('Cosine similarity', 'cos(a, b) = (a &middot; b) / (&Vert;a&Vert; &Vert;b&Vert;)', 'a = (1, 2), b = (2, 4): 10 / (&radic;5 &times; &radic;20) = 1, the same direction.', key=True),
     fx('FoolsGold style weight (simplified)', 'w<sub>i</sub> = 1 &minus; max<sub>j &ne; i</sub> cos(h<sub>i</sub>, h<sub>j</sub>), clipped to 0 to 1', 'Highest similarity 0.98 gives a weight of 0.02.'))}
''', kw=['Sybil', 'Douceur', 'attestation', 'rate limits', 'random sampling', 'FoolsGold', 'cosine similarity', 'update history', 'free rider', 'contribution'])

K.lesson('stack', 'Privacy and robustness together: a defence stack', f'''
{talk('Here is the tension in one sentence: secure aggregation hides each update from the server, but robust aggregation needs to look at each update. If the server only sees the sum, it cannot compute a median. There are three ways forward, and real systems mix them. First, rules that work on hidden updates: each client clips its own update before masking, so even the server cannot be fooled by a huge update, and validity proofs let clients prove in zero knowledge that their masked update is within the bound. Second, central differential privacy: clip, aggregate securely, then add noise, which limits both what the model reveals about any user and how much any user can change the model. Third, layered system defences that do not need to see updates at all: authentication and attestation, random client sampling, minimum round sizes, and testing every new model on a trusted validation set before release, with automatic rollback if accuracy or backdoor checks fail. Research continues on secure robust aggregation that gets the best of both. The stack in the table below is a practical starting point for a production system.')}
{table(['Layer', 'Defends against', 'How'], [
    ['Client identity', 'Sybils, cheap mass attacks', 'Device attestation, account limits, random sampling'],
    ['Client side clipping', 'Boosted model replacement', 'Each update scaled to length at most M before sending'],
    ['Secure aggregation', 'A curious server reading single updates', 'Pairwise masks, Shamir shares for drop outs, minimum round size'],
    ['Differential privacy noise', 'Leakage about any user, small backdoors', 'Gaussian noise on the clipped sum, tracked privacy budget'],
    ['Robust aggregation (where updates are visible)', 'A minority of Byzantine clients', 'Median, trimmed mean, Krum, FLTrust'],
    ['Model validation and rollback', 'Anything that slipped through', 'Trusted test set, backdoor probes, compare with the last model']])}
{versus('Defences compared', ['', 'Norm clipping', 'Median or trimmed mean', 'Krum', 'Similarity checks (FoolsGold)', 'DP noise'], [
    ['Stops', 'Boosted updates', 'Minority of extreme updates', 'Minority of outliers', 'Sybils pushing one goal', 'Small backdoors, leakage'],
    ['Needs to see updates?', 'No (clients can clip)', 'Yes', 'Yes', 'Yes, over many rounds', 'No'],
    ['Cost to honest users', 'Slower progress if M is small', 'Ignores unusual honest clients', 'Uses one update, wastes others', 'Similar honest users lose weight', 'Some accuracy'],
    ['Breaks when', 'Many attackers at the bound', 'Attackers reach half', 'n &le; 2f + 2', 'Sybils add noise', 'Too little noise']],
    'No single rule is enough. Combine identity checks, clipping, secure aggregation, DP noise and validation, and test against adaptive attacks.')}
''', kw=['privacy versus robustness', 'defence in depth', 'client side clipping', 'validity proofs', 'zero knowledge', 'central DP', 'minimum round size', 'model validation', 'rollback', 'secure robust aggregation'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that bad phones could teach a shared model bad habits and that updates can reveal data. A student can rebuild an input from a gradient, compute a model replacement boost, and run median, trimmed mean and Krum. A professional designs defence stacks for production FL. Experts research attacks and provable defences.')}
{ladder(
    '<p>If some phones lie during training, the shared model can learn the lie. And the small changes a phone sends can sometimes reveal what was on it, so they must be hidden and limited.</p>',
    '<p>x = &part;L/&part;W<sub>r</sub> / &part;L/&part;b<sub>r</sub>, model replacement &gamma; = n/&eta;, norm clipping, median breakdown 50%, trimmed mean &beta; &ge; f, Krum n &gt; 2f + 2, cosine similarity for Sybils.</p>',
    '<p>Build defence stacks: attestation, client side clipping, secure aggregation with DP, robust aggregation where possible, validation and rollback. Red team FL systems with adaptive attacks.</p>',
    '<p>Research gradient inversion at scale, provable robustness under non IID data, secure robust aggregation with zero knowledge proofs, and incentive design against free riders.</p>')}
{grow('Explain how federated training can be spied on or poisoned.',
      'Run the attacks and defences on toy models and compute their limits.',
      'Design and test layered defences for real federated systems.')}
''', kw=['beginner', 'expert', 'red team', 'research'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Threat model</b>: curious or malicious server, malicious clients, Sybils, free riders, outsiders. Privacy and robustness pull in opposite directions.',
    '<b>Leakage</b>: one example through a dense layer: x = &part;L/&part;W<sub>r</sub> / &part;L/&part;b<sub>r</sub>. DLG (2019), Inverting Gradients (2020), property inference (2019). Defences: SecAgg, DP.',
    '<b>Poisoning</b>: label flipping, boosted model replacement L = G + (n/&eta;)(X &minus; G), backdoors and edge cases. Norm clipping min(1, M/&Vert;&Delta;&Vert;) plus noise.',
    '<b>Robust aggregation</b>: median (50% breakdown), trimmed mean (&beta; &ge; f), Krum (n &gt; 2f + 2), FLTrust. Adaptive attacks (A Little Is Enough) still work.',
    '<b>Sybils and free riders</b>: attestation, rate limits, random sampling, cosine similarity weights (FoolsGold), contribution checks.',
    '<b>Stack</b>: identity, client clipping, secure aggregation, DP noise, robust aggregation where visible, validation and rollback.'],
    'Advanced 2.3: differential privacy, the maths that bounds what any output reveals about one person.')}
{files('Three tasks: rebuild an input from a gradient, a coordinate wise median, and Krum selection.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is a Sybil attack?', ['A brute force on passwords', 'One attacker controlling many fake identities', 'A phishing email', 'A DDoS'], 1, 'Many personalities.', 'In FL, fake clients can outvote honest ones.')
K.quiz('e', 'What does norm clipping do to a client’s update?', ['Encrypts it', 'Scales it down if it is longer than a bound', 'Deletes it always', 'Doubles it'], 1, 'Limit the length.', 'It caps any single client’s influence.')
K.quiz('e', 'Which aggregate is dragged furthest by one extreme value?', ['Median', 'Trimmed mean', 'Plain mean', 'Krum'], 2, 'Every value pulls on it.', 'One huge value can move the mean anywhere.')
K.quiz('e', 'A free rider in FL', ['Pays for the server', 'Takes the final model without contributing useful updates', 'Is a faster client', 'Encrypts data'], 1, 'No work, full reward.', 'Contribution checks and incentives help.')
K.quiz('m', 'For one example through a dense layer with bias, how can the server read the input from the update?', ['It cannot', 'Divide a row of the weight gradient by the matching bias gradient', 'Multiply all gradients', 'Look at the loss only'], 1, '&delta; x / &delta;.', 'Phong et al. pointed this out in 2017.')
K.quiz('m', 'In model replacement, what boost does the attacker use?', ['1', 'n / &eta;', '&eta; / n', '0'], 1, 'Undo the averaging.', 'The average divides by n and multiplies by &eta;.')
K.quiz('m', 'What is the breakdown point of the coordinate wise median?', ['10%', '25%', '50%', '100%'], 2, 'The middle value.', 'It stays among honest values while attackers are fewer than half.')
K.quiz('m', 'Krum needs which condition between n clients and f attackers?', ['n &gt; f', 'n &gt; 2f + 2', 'n = f', 'n &lt; f'], 1, 'Blanchard et al. 2017.', 'n = 10 tolerates f = 3.')
K.quiz('m', 'Why do Sybil updates stand out to FoolsGold?', ['They are larger', 'They point in the same direction round after round', 'They arrive late', 'They are encrypted'], 1, 'One goal.', 'Honest users with different data point in different directions.')
K.quiz('h', 'Why can secure aggregation and median aggregation not be combined directly?', ['They use different languages', 'Secure aggregation reveals only the sum, but the median needs each update', 'The median is too slow', 'They can, always'], 1, 'What does the server see?', 'Workarounds: client side clipping, validity proofs, DP, validation.')
K.quiz('h', 'What did A Little Is Enough (Baruch et al. 2019) show?', ['FL is always safe', 'Small coordinated shifts inside the normal spread can bypass robust aggregation', 'Clipping is useless', 'Krum is perfect'], 1, 'Stay inside the range.', 'Attackers tuned to the defence avoid looking like outliers.')
K.quiz('h', 'Why are larger batches not a full defence against gradient inversion?', ['They slow training', 'Optimisation attacks can still solve for several inputs at once, especially for small batches', 'They leak labels only', 'They are illegal'], 1, 'DLG.', 'Batching blurs simple division but not optimisation attacks.')
K.quiz('h', 'With 6 attackers among 10 clients, which aggregator still works?', ['Median', 'Trimmed mean', 'Krum', 'None of them'], 3, 'Honest majority assumption.', 'Robust aggregation needs attackers to be a minority. Identity checks must stop such numbers.')
K.quiz('x', 'In the style of an MIT 6.5660 question: a client’s update has length 5 and the clip bound is M = 1. By what factor is it scaled?', ['5', '1', '0.2', '0'], 2, 'M / &Vert;&Delta;&Vert;.', 'min(1, 1/5) = 0.2.')
K.quiz('x', 'In the style of an IISc federated learning viva: why does norm clipping plus Gaussian noise help both privacy and robustness?', ['It encrypts updates', 'Clipping bounds each user’s influence and noise hides what remains, the core of DP', 'It removes attackers', 'It speeds up training'], 1, 'Bounded sensitivity.', 'Sun et al. (2019) found it stops most simple backdoors.')

K.calc('e', 'Gradient row entry &minus;0.558 and bias gradient &minus;0.62. Rebuilt input value?', '0.9', 'Divide.', ['&minus;0.558 / &minus;0.62.', 'Signs cancel.', eq('0.9')], check=round(0.558 / 0.62, 4))
K.calc('e', 'Model replacement with n = 10 clients and &eta; = 1. Boost factor &gamma;?', '10', 'n / &eta;.', ['10 / 1.', 'The attacker scales its change 10 times.', eq('10')], check=10)
K.calc('e', 'An update of length 5, clip bound M = 1. Scale factor?', '0.2', 'min(1, M / length).', ['1 / 5 = 0.2.', 'Smaller than 1, so apply it.', eq('0.2')], check=0.2)
K.calc('m', 'G = 1, attacker target X = 5, n = 10, &eta; = 1. What does the attacker send?', '41', 'G + &gamma;(X &minus; G).', ['&gamma; = 10.', '1 + 10 &times; 4.', eq('41')], check=41)
K.calc('m', 'Values 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 8, 8, 8. Median?', '1.025', 'Middle two of 10.', ['Sorted, the 5th and 6th are 1.0 and 1.05.', 'Average them.', eq('1.025')], check=1.025)
K.calc('m', 'Same 10 values. Plain mean? Round to 3 decimals.', '3.065', 'Sum over 10.', ['Honest sum 0.8 + 0.85 + 0.9 + 0.95 + 1.0 + 1.05 + 1.1 = 6.65.', 'Plus 24 = 30.65.', eq('30.65 / 10 = 3.065')], check=3.065)
K.calc('m', 'Trimmed mean of the same 10 values with &beta; = 3. Round to 3 decimals.', '1.025', 'Drop 3 from each end.', ['Left: 0.95, 1.0, 1.05, 1.1.', 'Sum 4.1.', eq('4.1 / 4 = 1.025')], check=1.025)
K.calc('m', 'Krum with n = 10 and f = 3. How many nearest neighbours enter each score?', '5', 'n &minus; f &minus; 2.', ['10 &minus; 3 &minus; 2.', 'Squared distances to the 5 nearest.', eq('5')], check=5)
K.calc('h', 'Largest f that Krum tolerates with n = 10?', '3', 'n &gt; 2f + 2.', ['2f + 2 &lt; 10 gives f &lt; 4.', 'Largest whole f.', eq('3')], check=3)
K.calc('h', 'cos(a, b) for a = (1, 2) and b = (2, 4)?', '1', 'Dot over lengths.', ['a &middot; b = 2 + 8 = 10.', '&Vert;a&Vert; &Vert;b&Vert; = &radic;5 &times; &radic;20 = 10.', eq('1')], check=1)
K.calc('h', 'cos(a, b) for a = (1, 0) and b = (1, 1)? Round to 4 decimals.', '0.7071', 'Dot over lengths.', ['a &middot; b = 1.', '&Vert;a&Vert; &Vert;b&Vert; = 1 &times; &radic;2.', eq('1 / &radic;2 &asymp; 0.7071')], check=round(1 / math.sqrt(2), 4))
K.calc('h', 'G = (1, 2), clip M = 1, an update L = (41, &minus;48). Length of its change from G? Round to 2 decimals.', '64.03', '&Vert;L &minus; G&Vert;.', ['L &minus; G = (40, &minus;50).', '&radic;(1600 + 2500) = &radic;4100.', eq('&asymp; 64.03')], check=round(math.hypot(40, -50), 2))
K.calc('x', 'With clip M = 1, by what factor is that change of length &radic;4100 scaled? Round to 4 decimals.', '0.0156', 'M / length.', ['Length &asymp; 64.03.', '1 / 64.03.', eq('&asymp; 0.0156')], check=round(1 / math.hypot(40, -50), 4))
K.calc('x', 'A FoolsGold style weight for a client whose highest similarity to another client is 0.97?', '0.03', '1 &minus; max similarity.', ['1 &minus; 0.97.', 'Clip to 0 to 1.', eq('0.03')], check=0.03)

K.assign('recover_input', 'e', 'Rebuild an input from a gradient',
         '<p>Write <code>recover_input(grad_row, grad_bias)</code> that returns the input rebuilt from one row of a dense layer’s weight gradient and the matching bias gradient: each entry divided by grad_bias, rounded to 4 decimals.</p>',
         '''
def recover_input(grad_row, grad_bias):
    # your code here
    pass
''', [('recover_input([-0.558, -0.062, -0.434, -0.186], -0.62)', [0.9, 0.1, 0.7, 0.3]),
      ('recover_input([0.2, 0.4], 0.5)', [0.4, 0.8]),
      ('recover_input([1.5, -3.0, 0.0], 3.0)', [0.5, -1.0, 0.0])],
         '''
def recover_input(grad_row, grad_bias):
    out = []
    for g in grad_row:
        out.append(round(g / grad_bias, 4))
    return out
''', 'Divide every entry of the row by the bias gradient.', '<p>This only works for a single example and a layer with a bias. It is a reminder that model updates are personal data and need the same care as the data itself.</p>')
K.assign('coord_median', 'm', 'Coordinate wise median',
         '<p>updates is a list of equal length lists. Write <code>coord_median(updates)</code> that returns the median of each position, rounded to 4 decimals. Use <code>statistics.median</code>.</p>',
         '''
import statistics

def coord_median(updates):
    # your code here
    pass
''', [('coord_median([[1.0, 0.5], [1.1, 0.4], [0.9, 0.6], [1.05, 0.55], [0.95, 0.45], [1.2, 0.5], [0.85, 0.5], [-8.0, 9.0], [-8.5, 9.5], [-7.5, 8.5]])', [0.925, 0.525]),
      ('coord_median([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [100.0, -100.0, 0.0]])', [4.0, 2.0, 3.0]),
      ('coord_median([[1.0], [2.0], [3.0], [4.0]])', [2.5])],
         '''
import statistics

def coord_median(updates):
    out = []
    for k in range(len(updates[0])):
        column = [u[k] for u in updates]
        out.append(round(statistics.median(column), 4))
    return out
''', 'For each position k, collect that position from every update and take its median.', '<p>The median of each coordinate need not be any client’s actual update. Krum, in the next task, always returns a real update instead.</p>')
K.assign('krum_select', 'h', 'Krum selection',
         '<p>Write <code>krum_select(updates, f)</code> that returns the index of the update chosen by Krum: for each update, add the squared distances to its n &minus; f &minus; 2 nearest other updates, and return the index with the smallest total (the first one if there is a tie).</p>',
         '''
def krum_select(updates, f):
    # your code here
    pass
''', [('krum_select([[1.0, 0.5], [1.1, 0.4], [0.9, 0.6], [1.05, 0.55], [0.95, 0.45], [1.2, 0.5], [0.85, 0.5], [-8.0, 9.0], [-8.5, 9.5], [-7.5, 8.5]], 3)', 0),
      ('krum_select([[0.0], [0.1], [0.2], [5.0], [0.15]], 1)', 4),
      ('krum_select([[1, 1], [1.2, 0.9], [0.9, 1.1], [10, 10], [1.1, 1.0], [0.95, 1.05], [9, 11]], 2)', 0)],
         '''
def krum_select(updates, f):
    n = len(updates)
    scores = []
    for i, u in enumerate(updates):
        dists = []
        for j, v in enumerate(updates):
            if j != i:
                dists.append(sum((a - b) ** 2 for a, b in zip(u, v)))
        dists.sort()
        scores.append(sum(dists[:n - f - 2]))
    return scores.index(min(scores))
''', 'Build the list of squared distances for each update, sort it, add the first n &minus; f &minus; 2, then pick the smallest score.', '<p>Multi-Krum averages the m best scoring updates instead of taking one, which keeps more honest information while staying robust.</p>')

K.must('Threat model', 'Honest but curious or malicious server, malicious clients (Byzantine), Sybils (Douceur 2002), free riders, outsiders. Privacy wants updates hidden, robustness wants them inspected.')
K.must('Leakage', 'Dense layer, one example: &part;L/&part;W<sub>r</sub> = &delta;<sub>r</sub>x, &part;L/&part;b<sub>r</sub> = &delta;<sub>r</sub>, so x = ratio (Phong 2017). DLG optimisation (Zhu 2019), Inverting Gradients (Geiping 2020), property inference (Melis 2019). Defences: SecAgg, DP, not batching alone.')
K.must('Poisoning', 'Data poisoning (label flips) and model poisoning. Model replacement L = G + (n/&eta;)(X &minus; G) (Bagdasaryan 2020). Edge case backdoors (2020). Norm clipping &Delta; min(1, M/&Vert;&Delta;&Vert;) plus noise (Sun 2019).')
K.must('Robust aggregation', 'Byzantine (Lamport 1982). Median: 50% breakdown. Trimmed mean: &beta; &ge; f (Yin 2018). Krum: lowest sum over n &minus; f &minus; 2 nearest, n &gt; 2f + 2 (Blanchard 2017). FLTrust root data (2021). Adaptive attacks: A Little Is Enough (2019), Fang (2020).')
K.must('Sybils and free riders', 'Attestation, rate limits, random sampling, minimum round size. FoolsGold: cosine similarity of update histories, weight 1 &minus; max similarity. Contribution checks for free riders.')
K.must('Defence stack', 'Identity, client side clipping, secure aggregation, DP noise, robust aggregation where updates are visible, validation with backdoor probes and rollback. Honest majority is assumed by every robust rule.')

T = K.topic(
    slug='cy-flattack', topic='cy-flattack', step=(2, 'Federated learning and privacy', 'cy-a2', 'Training models across many devices and organisations without collecting their data, the attacks on such systems, and differential privacy.', 'Advanced'),
    title='Attacks and defences in federated learning', short='Attacks on FL', badge='2.2', minutes=80,
    lead='What can go wrong when many parties train together: the threat model, rebuilding private inputs from gradients, poisoning and boosted model replacement, norm clipping, Byzantine robust aggregation with the median, trimmed mean and Krum, Sybil detection by update similarity, free riders, and a layered defence stack that balances privacy and robustness.',
    desc='federated learning attacks, threat model, honest but curious server, gradient leakage, gradient inversion, Deep Leakage from Gradients, property inference, poisoning, model poisoning, model replacement, backdoor, edge case backdoor, norm clipping, Byzantine, robust aggregation, coordinate wise median, trimmed mean, Krum, FLTrust, breakdown point, A Little Is Enough, Sybil attack, FoolsGold, cosine similarity, free rider, attestation, defence in depth',
    summary='FL threat model, gradient leakage, poisoning and model replacement, clipping, median, trimmed mean and Krum, Sybil detection, free riders, and a layered defence stack.',
    keywords=['federated learning', 'gradient leakage', 'model replacement', 'backdoor', 'norm clipping', 'robust aggregation', 'median', 'Krum', 'Sybil', 'FoolsGold'],
    recap='<p>Hide each update, cap each client’s influence, use robust rules while attackers are a minority, check identities, and validate every model before it ships.</p>',
    added='2026-11-15')
