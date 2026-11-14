# Deep learning 3.4: energy based models. Checked against Hopfield, Neural networks and physical systems with emergent
# collective computational abilities (PNAS 1982), Amit, Gutfreund and Sompolinsky, Storing infinite numbers of patterns
# in a spin-glass model of neural networks (PRL 1985), Ackley, Hinton and Sejnowski, A learning algorithm for Boltzmann
# machines (Cognitive Science 1985), Smolensky (1986) on harmoniums, Hinton, Training products of experts by minimizing
# contrastive divergence (Neural Computation 2002), Hinton, Osindero and Teh, A fast learning algorithm for deep belief
# nets (Neural Computation 2006), Tieleman, persistent contrastive divergence (ICML 2008), Salakhutdinov and Hinton, Deep
# Boltzmann machines (AISTATS 2009), Hinton, A practical guide to training RBMs (2010), Krotov and Hopfield, Dense
# associative memory (NeurIPS 2016), Ramsauer and colleagues, Hopfield networks is all you need (ICLR 2021), LeCun and
# colleagues, A tutorial on energy-based learning (2006), and the scikit-learn BernoulliRBM documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('dl-boltzmann')
K = Kit()
K.code('hopfield_memory', r'''
# A Hopfield network: store letters as patterns of +1 and -1, then recall a letter from a damaged copy.
import numpy as np

LETTERS = {
    'T': ['#####', '..#..', '..#..', '..#..', '..#..'],
    'L': ['#....', '#....', '#....', '#....', '#####'],
    'X': ['#...#', '.#.#.', '..#..', '.#.#.', '#...#'],
}
to_vec = lambda rows: np.array([1 if ch == '#' else -1 for row in rows for ch in row])
show = lambda s: '\n'.join(''.join('#' if v > 0 else '.' for v in s[r * 5:r * 5 + 5]) for r in range(5))

P = np.array([to_vec(r) for r in LETTERS.values()])                 # 3 patterns, 25 units each
N = P.shape[1]
W = P.T @ P / N                                                     # Hebb rule: units that agree get a positive weight
np.fill_diagonal(W, 0)                                              # no unit connects to itself


def energy(s):
    return -0.5 * s @ W @ s


rng = np.random.default_rng(1)
s = P[0].copy()
flip = rng.choice(N, 6, replace=False)
s[flip] *= -1                                                       # damage 6 of the 25 pixels of T
print('damaged T, energy', round(energy(s), 3))
print(show(s))
for sweep in range(3):
    for i in rng.permutation(N):                                    # asynchronous: one unit at a time
        s[i] = 1 if W[i] @ s >= 0 else -1
    print(f'after sweep {sweep + 1}: energy {energy(s):.3f}, wrong pixels {int(np.sum(s != P[0]))}')
print(show(s))

# Capacity: how many random patterns can 100 units hold? Start each one with 10 pixels flipped.
N = 100
for k in [5, 10, 14, 20, 30]:
    pats = rng.choice([-1, 1], size=(k, N))
    W2 = pats.T @ pats / N
    np.fill_diagonal(W2, 0)
    ok = 0
    for p in pats:
        s = p.copy()
        s[rng.choice(N, 10, replace=False)] *= -1
        for _ in range(5):
            for i in rng.permutation(N):
                s[i] = 1 if W2[i] @ s >= 0 else -1
        ok += np.mean(s == p) >= 0.98                               # recalled with at most 2 wrong pixels
    print(f'{k:2d} patterns in 100 units: {ok} of {k} recalled ({ok / k:.0%})')
print('Rule of thumb: about 0.14 N random patterns (14 here) before recall breaks down.')
''', long=True)

K.code('boltzmann_exact', r'''
# A tiny Boltzmann machine with 3 binary units: the exact probability of every state, and Gibbs sampling.
import itertools

import numpy as np

W = np.array([[0.0, 2.0, -1.0],
              [2.0, 0.0, 1.0],
              [-1.0, 1.0, 0.0]])                                    # symmetric weights, zero diagonal
b = np.array([-1.0, -0.5, 0.5])                                     # biases


def energy(s):
    return -0.5 * s @ W @ s - b @ s


states = np.array(list(itertools.product([0, 1], repeat=3)))       # all 2^3 = 8 states
for T in [1.0, 0.5, 4.0]:                                          # temperature
    weights = np.exp(-np.array([energy(s) for s in states]) / T)    # Boltzmann factor e^(-E/T)
    Z = weights.sum()                                               # partition function: the sum over every state
    p = weights / Z
    print(f'T = {T}: Z = {Z:.3f}, lowest energy states p = {p.max():.3f} each, highest energy state p = {p.min():.3f}')
    if T == 1.0:
        p_exact = p
        for s, e, q in zip(states, [energy(s) for s in states], p):
            print(f'   state {s}  energy {e:5.2f}  p {q:.3f}')

# Gibbs sampling: update one unit at a time from p(s_i = 1 | others) = sigmoid(sum_j w_ij s_j + b_i)
rng = np.random.default_rng(0)
s = np.zeros(3)
counts = np.zeros(8)
for step in range(60_000):
    i = step % 3
    s[i] = rng.random() < 1 / (1 + np.exp(-(W[i] @ s + b[i])))
    if step >= 3000:                                                # skip the burn in
        counts[int(s[0] * 4 + s[1] * 2 + s[2])] += 1
freq = counts / counts.sum()
print('Gibbs frequencies at T = 1:', np.round(freq, 3))
print('largest gap to the exact p:', round(float(np.abs(freq - p_exact).max()), 3))
''', long=True)

K.code('rbm_cd', r'''
# A restricted Boltzmann machine trained with contrastive divergence on 4x4 "bars and stripes" images.
# 16 pixels is small enough to compute the exact likelihood, so we can watch real learning, not a proxy.
import itertools

import numpy as np

rng = np.random.default_rng(0)
rows = np.array(list(itertools.product([0, 1], repeat=4)))
bars = np.array([np.repeat(r, 4) for r in rows])                    # each column all on or all off
stripes = np.array([np.tile(r, 4) for r in rows])                   # each row all on or all off
data = np.unique(np.vstack([bars, stripes]), axis=0).astype(float)  # 30 distinct images (empty and full appear in both)
print('training images:', len(data), '  best possible average log likelihood:', round(np.log(1 / len(data)), 3))

sig = lambda x: 1 / (1 + np.exp(-x))
ALL_V = np.array(list(itertools.product([0, 1], repeat=16)), dtype=float)   # all 65,536 images


def free_energy(v, W, a, b):
    """F(v) = -a.v - sum_j log(1 + e^(b_j + v.W_j)). Then p(v) = e^(-F(v)) / Z."""
    return -v @ a - np.logaddexp(0, v @ W + b).sum(axis=1)


def avg_log_lik(W, a, b):
    log_z = np.logaddexp.reduce(-free_energy(ALL_V, W, a, b))       # exact log Z over every image
    return float(np.mean(-free_energy(data, W, a, b) - log_z))


def train(k, epochs=5000, hidden=16, lr=0.2):
    W = rng.normal(0, 0.01, (16, hidden))
    a, b = np.zeros(16), np.zeros(hidden)
    for epoch in range(1, epochs + 1):
        v0 = data
        ph0 = sig(v0 @ W + b)                                       # positive phase: hidden given the data
        h = (rng.random(ph0.shape) < ph0).astype(float)
        for _ in range(k):                                          # k steps of Gibbs sampling
            v = (rng.random((len(data), 16)) < sig(h @ W.T + a)).astype(float)
            ph = sig(v @ W + b)
            h = (rng.random(ph.shape) < ph).astype(float)
        W += lr * (v0.T @ ph0 - v.T @ ph) / len(data)               # <v h>_data - <v h>_model
        a += lr * (v0 - v).mean(axis=0)
        b += lr * (ph0 - ph).mean(axis=0)
        if epoch in (1, 500, 2000, 5000):
            print(f'  CD-{k}  epoch {epoch:4d}: average log likelihood {avg_log_lik(W, a, b):.3f}')
    return W, a, b


W, a, b = train(k=1)
train(k=10)

# Generate: run Gibbs chains from random noise and check how many end on a real bar or stripe image
v = (rng.random((500, 16)) < 0.5).astype(float)
for _ in range(1000):
    h = (rng.random((500, W.shape[1])) < sig(v @ W + b)).astype(float)
    v = (rng.random((500, 16)) < sig(h @ W.T + a)).astype(float)
valid = {tuple(r) for r in data}
ok = np.mean([tuple(r) in valid for r in v])
print(f'CD-1 model: {ok:.0%} of 500 generated images are valid bars or stripes, '
      f'{len({tuple(r) for r in v if tuple(r) in valid})} of the 30 kinds appear')
''', long=True)

K.code('dbn_digits', r'''
# A deep belief network the classic way: pretrain RBMs one layer at a time without labels, then fine tune the
# whole stack as a deep sigmoid network with backpropagation. Only 100 labelled digits are used for fine tuning.
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import BernoulliRBM

X, y = load_digits(return_X_y=True)                                 # 8x8 handwritten digits
X = X / 16.0                                                        # pixels in 0..1, read as probabilities
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
few = np.concatenate([np.where(y_tr == d)[0][:10] for d in range(10)])   # 10 labelled images per digit

# 1. Greedy layer wise pretraining on all 1257 training images, labels never used
rbm1 = BernoulliRBM(n_components=100, learning_rate=0.05, n_iter=80, random_state=0).fit(X_tr)
rbm2 = BernoulliRBM(n_components=50, learning_rate=0.05, n_iter=80, random_state=0).fit(rbm1.transform(X_tr))

sig = lambda x: 1 / (1 + np.exp(-x))


def fine_tune(Ws, bs, epochs=300, lr=0.5):
    """Backpropagation through sigmoid layers plus a softmax output, on the 100 labelled images."""
    Ws = [w.copy() for w in Ws] + [np.random.default_rng(0).normal(0, 0.01, (Ws[-1].shape[1], 10))]
    bs = [b.copy() for b in bs] + [np.zeros(10)]
    Xl, Y = X_tr[few], np.eye(10)[y_tr[few]]
    for _ in range(epochs):
        acts = [Xl]
        for w, b in zip(Ws[:-1], bs[:-1]):
            acts.append(sig(acts[-1] @ w + b))
        z = acts[-1] @ Ws[-1] + bs[-1]
        p = np.exp(z - z.max(axis=1, keepdims=True))
        d = (p / p.sum(axis=1, keepdims=True) - Y) / len(Xl)        # gradient of cross entropy at the output
        for i in range(len(Ws) - 1, -1, -1):
            gW, gb = acts[i].T @ d, d.sum(axis=0)
            if i:
                d = (d @ Ws[i].T) * acts[i] * (1 - acts[i])         # back through a sigmoid layer
            Ws[i] -= lr * gW
            bs[i] -= lr * gb
    a = X_te
    for w, b in zip(Ws[:-1], bs[:-1]):
        a = sig(a @ w + b)
    return np.mean(np.argmax(a @ Ws[-1] + bs[-1], axis=1) == y_te)


rng = np.random.default_rng(1)
print('Deep network 64-100-50-10, fine tuned on 100 labels, test accuracy:')
print(f'  started from the pretrained RBMs:      {fine_tune([rbm1.components_.T, rbm2.components_.T], [rbm1.intercept_hidden_, rbm2.intercept_hidden_]):.3f}')
print(f'  started from tiny random weights:      {fine_tune([rng.normal(0, 0.01, (64, 100)), rng.normal(0, 0.01, (100, 50))], [np.zeros(100), np.zeros(50)]):.3f}')
print(f'  started from scaled random weights:    {fine_tune([rng.normal(0, 1 / 8, (64, 100)), rng.normal(0, 0.1, (100, 50))], [np.zeros(100), np.zeros(50)]):.3f}')
base = LogisticRegression(max_iter=5000).fit(X_tr[few], y_tr[few]).score(X_te, y_te)
print(f'Logistic regression on raw pixels, same 100 labels: {base:.3f}')
''', long=True)

K.lesson('energy', 'The energy view: low energy means likely', f'''
{src('LeCun and colleagues, A tutorial on energy-based learning (2006), and Ackley, Hinton and Sejnowski (1985).')}
{wwh('An <b>energy based model</b> gives every possible state of its units a number called the <b>energy</b>. States the model likes get low energy. The <b>Boltzmann distribution</b> turns energies into probabilities: the lower the energy, the more likely the state. The <b>temperature</b> T controls how strongly it prefers low energy.',
     'Energy is a natural way to say which combinations of features belong together, without having to say which feature causes which. The same idea links Hopfield memories, Boltzmann machines, RBMs and, through the score, the diffusion models of chapter 3.3.',
     'Write an energy function with weights between units. Learning lowers the energy of training data and raises the energy of everything else. Inference and generation look for low energy states, by settling (Hopfield) or by random sampling (Boltzmann machines).')}
{fxs(fx('Boltzmann distribution', 'p(s) = e<sup>&minus;E(s)/T</sup> / Z', 'Low energy, high probability. T is the temperature, usually 1.', key=True),
     fx('Partition function', 'Z = &Sigma;<sub>all states s</sub> e<sup>&minus;E(s)/T</sup>', 'Makes the probabilities add up to 1. Summing over 2<sup>n</sup> states is what makes these models hard.', key=True),
     fx('Energy of binary units', 'E(s) = &minus;&frac12; &Sigma;<sub>i,j</sub> w<sub>ij</sub> s<sub>i</sub> s<sub>j</sub> &minus; &Sigma;<sub>i</sub> b<sub>i</sub> s<sub>i</sub>', 'Symmetric weights w<sub>ij</sub> = w<sub>ji</sub>, no self connections.'))}
{table(['Model', 'Units', 'Learning', 'What it does'], [
    ['Hopfield network (1982)', 'All visible, &plusmn;1, fully connected', 'One shot Hebb rule', 'Stores memories and recalls them from damaged copies'],
    ['Boltzmann machine (1985)', 'Visible and hidden, 0 or 1, fully connected, random', 'Data statistics minus model statistics', 'Learns a probability distribution over data'],
    ['Restricted Boltzmann machine', 'Visible and hidden, links only between the layers', 'Contrastive divergence', 'Fast to train, learns features and generates data'],
    ['Deep belief network (2006)', 'A stack of RBMs', 'Greedy, one layer at a time, then fine tuning', 'Started the deep learning revival']])}
''', kw=['energy based model', 'energy function', 'Boltzmann distribution', 'partition function', 'temperature'])

K.lesson('hopfield', 'Hopfield networks: memories as valleys', f'''
{src('Hopfield (1982), and Amit, Gutfreund and Sompolinsky (1985).')}
{viz('mlhopfield')}
{wwh('A <b>Hopfield network</b> is a set of &plusmn;1 units, each connected to every other unit with a symmetric weight. Patterns are stored with the <b>Hebb rule</b>: units that agree in a pattern get a positive weight. To recall, start from a damaged pattern and let each unit in turn take the sign of its weighted input.',
     'It is a content addressable memory: give part of a memory and get the whole memory back, the way a few notes bring back a whole song. Hopfield showed that each update can only lower the energy, so the network always settles, and stored patterns sit at the bottoms of energy valleys.',
     'Build W from the patterns, set the diagonal to 0, then update units one at a time (asynchronously) until no unit changes. Keep the number of random patterns below about 0.14 times the number of units.')}
{run('hopfield_memory')}
{note('With 6 of 25 pixels flipped, one sweep of updates rebuilt the letter T exactly and the energy fell from &minus;2.24 to &minus;11.20. In 100 units, all 10 of 10 random patterns came back from 10 flipped pixels, 10 of 14 at the 0.14 N limit, and none of 30.', 'exam')}
{fxs(fx('Hebb rule', 'w<sub>ij</sub> = (1/N) &Sigma;<sub>&mu;</sub> p<sub>i</sub><sup>&mu;</sup> p<sub>j</sub><sup>&mu;</sup>, w<sub>ii</sub> = 0', 'One pass over the patterns, no gradient descent.', key=True),
     fx('Update rule', 's<sub>i</sub> &larr; sign( &Sigma;<sub>j</sub> w<sub>ij</sub> s<sub>j</sub> )', 'One unit at a time.', key=True),
     fx('Energy change of a flip', '&Delta;E = 2 s<sub>i</sub><sup>old</sup> h<sub>i</sub>, with h<sub>i</sub> = &Sigma;<sub>j</sub> w<sub>ij</sub> s<sub>j</sub>', 'A unit flips only when s<sub>i</sub> and h<sub>i</sub> disagree, so &Delta;E &le; 0.', key=True),
     fx('Capacity', 'about 0.138 N random patterns', 'Beyond it, recall breaks down and spurious memories take over.'))}
{note('Spurious states are valleys that are no stored pattern, such as the negative of a pattern or a mix of three patterns. The animation shows one when too many pixels are flipped.', 'warn')}
''', kw=['Hopfield network', 'associative memory', 'Hebb rule', 'energy', 'asynchronous update', 'capacity', 'spurious state'])

K.lesson('boltzmann', 'Boltzmann machines: Hopfield with randomness and hidden units', f'''
{src('Ackley, Hinton and Sejnowski, A learning algorithm for Boltzmann machines (1985).')}
{wwh('A <b>Boltzmann machine</b> has binary units (0 or 1) with symmetric weights like a Hopfield network, but each unit switches on at random with probability sigmoid of its input. Run long enough, it visits every state with its Boltzmann probability. It can also have <b>hidden units</b> that are not part of the data.',
     'The randomness lets it escape bad valleys and makes it a full probability model, so it can learn the distribution of the data and generate new samples. Hidden units let it capture patterns that no single pixel shows.',
     'Sample with <b>Gibbs sampling</b>: update one unit at a time from its conditional probability. Learn by making the model&rsquo;s statistics match the data&rsquo;s: raise w<sub>ij</sub> when units i and j are on together more often in the data than in the model&rsquo;s own samples.')}
{run('boltzmann_exact')}
{note('With 3 units there are only 8 states, so Z = 10.932 can be summed exactly. The two lowest energy states (energy &minus;1) each get p = 0.249. At T = 0.5 they get 0.339 and at T = 4 only 0.157, so a high temperature flattens the distribution. Gibbs sampling matched every exact probability within 0.005.', 'exam')}
{fxs(fx('Unit conditional', 'p(s<sub>i</sub> = 1 | rest) = &sigma;( (&Sigma;<sub>j</sub> w<sub>ij</sub> s<sub>j</sub> + b<sub>i</sub>) / T )', 'Each Gibbs step uses this. As T &rarr; 0 it becomes the Hopfield sign rule.', key=True),
     fx('Learning rule', '&Delta;w<sub>ij</sub> = &eta; ( &lang;s<sub>i</sub> s<sub>j</sub>&rang;<sub>data</sub> &minus; &lang;s<sub>i</sub> s<sub>j</sub>&rang;<sub>model</sub> )', 'The exact gradient of the log likelihood.', key=True))}
{note('The model term needs samples from the model, and in a fully connected machine every Gibbs chain is slow to mix. That is why general Boltzmann machines are rarely trained, and why the restricted version won.', 'tip')}
''', kw=['Boltzmann machine', 'stochastic unit', 'hidden units', 'Gibbs sampling', 'temperature', 'positive phase', 'negative phase'])

K.lesson('rbm', 'Restricted Boltzmann machines and contrastive divergence', f'''
{src('Smolensky (1986), Hinton, Training products of experts by minimizing contrastive divergence (2002), and Hinton, A practical guide to training RBMs (2010).')}
{viz('mlcd')}
{wwh('A <b>restricted Boltzmann machine</b> (RBM) has one visible layer and one hidden layer, with connections only between the layers. Given the visible units, the hidden units are independent of each other, and the other way round, so a whole layer is sampled in one matrix product. <b>Contrastive divergence</b> (CD-k) replaces the slow model statistics with those after only k steps of Gibbs sampling started at the data.',
     'The restriction makes Gibbs sampling fast and lets the hidden units be summed out in closed form (the free energy). CD-1 made RBMs practical to train, and they became the building block of deep belief networks and early recommender systems.',
     'For each batch: compute p(h | v<sub>0</sub>) from the data, sample h, reconstruct v<sub>1</sub>, compute p(h | v<sub>1</sub>), and move W by the difference of the two outer products. More Gibbs steps (CD-10) or persistent chains (PCD) give a better gradient at more cost.')}
{run('rbm_cd')}
{note('On 4 by 4 bars and stripes the best possible average log likelihood is ln(1/30) = &minus;3.401. CD-10 reached &minus;3.886. CD-1 peaked at &minus;4.863 and then fell back to &minus;5.696, because CD-1 does not follow the true likelihood gradient. Still, 93 percent of images generated by the CD-1 model were valid, but only 22 of the 30 kinds appeared.', 'exam')}
{fxs(fx('RBM energy', 'E(v, h) = &minus;a&middot;v &minus; b&middot;h &minus; v<sup>T</sup> W h', 'Only visible to hidden weights.', key=True),
     fx('Conditionals', 'p(h<sub>j</sub> = 1 | v) = &sigma;(b<sub>j</sub> + v&middot;W<sub>:j</sub>), p(v<sub>i</sub> = 1 | h) = &sigma;(a<sub>i</sub> + W<sub>i:</sub>&middot;h)', 'A whole layer at once.', key=True),
     fx('Free energy', 'F(v) = &minus;a&middot;v &minus; &Sigma;<sub>j</sub> ln(1 + e<sup>b<sub>j</sub> + v&middot;W<sub>:j</sub></sup>), p(v) = e<sup>&minus;F(v)</sup> / Z', 'The hidden units summed out exactly.', key=True),
     fx('CD-k update', '&Delta;W = &eta; ( v<sub>0</sub> p(h | v<sub>0</sub>)<sup>T</sup> &minus; v<sub>k</sub> p(h | v<sub>k</sub>)<sup>T</sup> )', 'Data statistics minus statistics after k Gibbs steps.'))}
{deep('Variants of the RBM', '<p><b>Persistent CD</b> (Tieleman 2008) keeps the negative chains running between updates instead of restarting them at the data, which follows the likelihood more closely. <b>Gaussian-Bernoulli RBMs</b> use real valued visible units for data such as audio. RBMs for <b>collaborative filtering</b> (Salakhutdinov, Mnih and Hinton 2007) were part of the winning blend in the Netflix Prize, with one visible unit per rated movie. Evaluating Z for big RBMs needs estimates such as annealed importance sampling.</p>')}
''', kw=['restricted Boltzmann machine', 'RBM', 'contrastive divergence', 'CD-k', 'free energy', 'persistent contrastive divergence', 'bars and stripes'])

K.lesson('dbn', 'Deep belief networks and greedy pretraining', f'''
{src('Hinton, Osindero and Teh, A fast learning algorithm for deep belief nets (2006), and Salakhutdinov and Hinton, Deep Boltzmann machines (2009).')}
{steps('Greedy layer wise training of a deep belief network', [
    'Train an RBM on the data, without labels.',
    'Use its hidden probabilities p(h | v) as the data for a second RBM, and train that one.',
    'Repeat for as many layers as you want. Each new layer models the features of the layer below.',
    'Turn the stack into a deep network, add an output layer, and fine tune all the weights with backpropagation on the labelled data.'])}
{wwh('A <b>deep belief network</b> (DBN) is a stack of RBMs trained one layer at a time. Used as a generative model, its top two layers form an RBM and the lower layers generate downwards. Used for classification, the RBM weights initialise a deep network that is then fine tuned.',
     'In 2006 deep networks with sigmoid units were very hard to train from random weights, because gradients faded on the way down. Pretraining placed the weights in a good region first. This result restarted interest in deep learning. A <b>deep Boltzmann machine</b> is different: all its layers are trained together as one undirected model.',
     'Pretrain on all the data you have, labelled or not, then fine tune on the labelled part. Today ReLU units, good initialisation, normalisation and big labelled datasets usually make pretraining by RBMs unnecessary, which the program shows too.')}
{run('dbn_digits')}
{note('With only 100 labels, the deep sigmoid network started from the pretrained RBMs scored 0.876. From tiny random weights it stalled at 0.239, the vanishing gradient problem. Sensibly scaled random weights reached 0.798. Plain logistic regression on the pixels still scored 0.906 on these easy 8 by 8 digits, so pretraining helps deep sigmoid networks but is no magic.', 'exam')}
''', kw=['deep belief network', 'DBN', 'greedy layer wise pretraining', 'fine tuning', 'deep Boltzmann machine', 'BernoulliRBM', 'vanishing gradients'])

K.lesson('today', 'Energy models today', f'''
{src('Krotov and Hopfield, Dense associative memory (2016), Ramsauer and colleagues, Hopfield networks is all you need (2021), and Song and Ermon (2019).')}
{versus('Energy based models compared', ['', 'Hopfield network', 'RBM and DBN', 'Modern Hopfield network', 'Score and diffusion models'], [
    ['States', 'Binary &plusmn;1', 'Binary or Gaussian units', 'Continuous vectors', 'Continuous data'],
    ['Learning', 'Hebb rule in one pass', 'Contrastive divergence', 'Backpropagation as a layer', 'Denoising score matching'],
    ['Capacity or quality', 'About 0.14 N patterns', 'Good on small binary data', 'Exponential in the dimension', 'State of the art images and audio'],
    ['Needs Z?', 'No, only settles', 'Yes for likelihood, avoided by CD', 'No', 'No, learns the gradient of ln p'],
    ['Used today', 'Teaching, physics', 'Teaching, small recommenders', 'Inside attention like layers', 'Stable Diffusion and similar']],
    'The score in diffusion models is &minus;&nabla;E(x) for an energy E = &minus;ln p(x), so learning the score is learning the slope of an energy landscape without ever computing Z.')}
{deep('Hopfield meets attention', '<p>Modern Hopfield networks replace the quadratic energy with one built from a log sum exp of similarities. Their update rule, new state = softmax(&beta; X<sup>T</sup> &xi;) applied to the stored patterns X, is the attention formula of chapter 2.3 with the stored patterns as keys and values. They can store exponentially many patterns. In 2024 John Hopfield and Geoffrey Hinton received the Nobel Prize in Physics for these foundational discoveries that enable machine learning with neural networks.</p>')}
''', kw=['modern Hopfield network', 'dense associative memory', 'attention', 'score', 'energy landscape', 'Nobel Prize 2024'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Boltzmann distribution', 'p(s) = e<sup>&minus;E(s)/T</sup> / Z, Z = &Sigma;<sub>s</sub> e<sup>&minus;E(s)/T</sup>', 'Ratio of two states: p(a)/p(b) = e<sup>(E(b) &minus; E(a))/T</sup>.', key=True),
     fx('Hopfield', 'W = (1/N) &Sigma; p p<sup>T</sup> with zero diagonal, s<sub>i</sub> &larr; sign(h<sub>i</sub>), &Delta;E = 2 s<sub>i</sub><sup>old</sup> h<sub>i</sub> &le; 0', 'Capacity about 0.138 N.', key=True),
     fx('Boltzmann machine gradient', '&part; ln p(v) / &part;w<sub>ij</sub> = &lang;s<sub>i</sub>s<sub>j</sub>&rang;<sub>data</sub> &minus; &lang;s<sub>i</sub>s<sub>j</sub>&rang;<sub>model</sub>', 'Positive phase minus negative phase.', key=True),
     fx('RBM', 'p(h<sub>j</sub>=1|v) = &sigma;(b<sub>j</sub> + v&middot;W<sub>:j</sub>), F(v) = &minus;a&middot;v &minus; &Sigma;<sub>j</sub> ln(1 + e<sup>b<sub>j</sub> + v&middot;W<sub>:j</sub></sup>)', 'Gradient: &minus;&part;F/&part;&theta; on data minus the same on model samples.', key=True),
     fx('Contrastive divergence', '&Delta;W = &eta; ( v<sub>0</sub> p(h|v<sub>0</sub>)<sup>T</sup> &minus; v<sub>k</sub> p(h|v<sub>k</sub>)<sup>T</sup> )', 'k = 1 is cheap but biased.'),
     fx('Link to scores', '&nabla;<sub>x</sub> ln p(x) = &minus;&nabla;<sub>x</sub> E(x) / T', 'Z does not depend on x, so it disappears from the gradient.'))}
{note('Why Z disappears from the score: ln p(x) = &minus;E(x)/T &minus; ln Z, and ln Z is the same number for every x, so its gradient with respect to x is zero.', 'exam')}
''', kw=['maths', 'formulas', 'derivation'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A network can store a picture as a valley in an energy landscape and roll back into it from a damaged copy.</p>',
    '<p>Build a Hopfield memory with the Hebb rule, compute Boltzmann probabilities and Z for a small model, and run Gibbs sampling.</p>',
    '<p>Train an RBM with CD-k and PCD, compute its free energy and exact likelihood on small data, and pretrain a deep belief network.</p>',
    '<p>Analyse capacity with spin glass theory, estimate Z with annealed importance sampling, train deep Boltzmann machines, and connect modern Hopfield networks to attention and energies to diffusion scores.</p>')}
{grow('Explain energy, temperature and memories as valleys.',
      'Train and sample Hopfield networks, Boltzmann machines and RBMs.',
      'Place energy models in the history and the present of generative AI.')}
{scene('Recommending films with an RBM', '<p>A streaming service has millions of users who rated only a few films each. An RBM gets one visible unit per film and a few hundred hidden units. Each user is one training example, with only the rated films clamped. After CD training, the hidden units capture tastes such as &ldquo;likes slow science fiction&rdquo;. To recommend, clamp a user&rsquo;s ratings, compute the hidden probabilities, and read the reconstruction probabilities of the films they have not seen. This is the approach that Salakhutdinov, Mnih and Hinton used in the Netflix Prize.</p>')}
''', kw=['beginner', 'expert', 'recommender', 'spin glass'])

lc(289, 'Game of Life', 'game-of-life', 'm', 'Update every cell from its neighbours at the same time, encoding old and new state in one number', 'A Hopfield update looks at its neighbours and sets a new state. Game of Life updates all cells at once (synchronously), so the new value must not be seen before every cell has read the old one. Store old state in bit 0 and new state in bit 1, then shift. O(mn) time, O(1) extra space.', """
def gameOfLife(board):
    m, n = len(board), len(board[0])
    for i in range(m):
        for j in range(n):
            live = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di or dj) and 0 <= i + di < m and 0 <= j + dj < n:
                        live += board[i + di][j + dj] & 1      # bit 0 is the old state
            if board[i][j] & 1 and live in (2, 3) or not board[i][j] & 1 and live == 3:
                board[i][j] |= 2                               # bit 1 is the new state
    for i in range(m):
        for j in range(n):
            board[i][j] >>= 1
    return board
""", [('gameOfLife([[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]])', [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]), ('gameOfLife([[1, 1], [1, 0]])', [[1, 1], [1, 1]]), ('gameOfLife([[1]])', [[0]])])
lc(191, 'Number of 1 Bits', 'number-of-1-bits', 'e', 'Clear the lowest set bit with n & (n - 1) until n is 0', 'A binary state vector of units can be packed into one integer. Counting its on units is counting 1 bits. n & (n minus 1) removes exactly one set bit, so the loop runs once per on unit.', """
def hammingWeight(n):
    count = 0
    while n:
        n &= n - 1          # drop the lowest 1 bit
        count += 1
    return count
""", [('hammingWeight(11)', 3), ('hammingWeight(128)', 1), ('hammingWeight(2147483645)', 30), ('hammingWeight(0)', 0)])
lc(338, 'Counting Bits', 'counting-bits', 'e', 'Reuse smaller answers: bits(i) = bits(i >> 1) + (i & 1)', 'Enumerating every state of a small Boltzmann machine walks through all integers 0 to 2^n minus 1. The number of on units in i equals that of i with its last bit removed, plus that last bit. O(n) time.', """
def countBits(n):
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)
    return ans
""", [('countBits(2)', [0, 1, 1]), ('countBits(5)', [0, 1, 1, 2, 1, 2]), ('countBits(0)', [0])])
lc(476, 'Number Complement', 'number-complement', 'e', 'Flip every bit below the highest set bit with a mask of ones', 'Flipping every unit of a binary state, like the spurious negative of a Hopfield memory. Build a mask with as many ones as n has bits and xor with it.', """
def findComplement(num):
    mask = (1 << num.bit_length()) - 1
    return num ^ mask
""", [('findComplement(5)', 2), ('findComplement(1)', 0), ('findComplement(10)', 5), ('findComplement(2147483647)', 0)])
lc(1611, 'Minimum One Bit Operations to Make Integers Zero', 'minimum-one-bit-operations-to-make-integers-zero', 'h', 'The allowed moves walk the Gray code, so the answer is the inverse Gray code of n', 'Each allowed operation changes one bit, so the states form a path in which neighbours differ in one unit, exactly like a single unit Gibbs or Hopfield update. The order of that path is the Gray code. The number of steps from n to 0 is the position of n in the Gray code, found by xoring all right shifts of n. O(log n).', """
def minimumOneBitOperations(n):
    res = 0
    while n:
        res ^= n            # inverse Gray code: xor of all right shifts
        n >>= 1
    return res
""", [('minimumOneBitOperations(3)', 2), ('minimumOneBitOperations(6)', 4), ('minimumOneBitOperations(0)', 0), ('minimumOneBitOperations(9)', 14), ('minimumOneBitOperations(333)', 393)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Energy models work on binary states that change one unit at a time. These problems use the same skills: updating a grid from its neighbours at once, counting and flipping the on units of a state packed into an integer, and walking a path of states that differ in one bit.</p>'), kw=['LeetCode', 'bit manipulation', 'Gray code', 'cellular update'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An <b>energy based model</b> gives each state an energy, and p(s) = e<sup>&minus;E/T</sup>/Z. The partition function Z sums over every state, which is what makes these models hard.',
    'A <b>Hopfield network</b> stores patterns with the Hebb rule and recalls them by lowering energy. It rebuilt T from 6 flipped pixels, and holds about 0.14 N random patterns.',
    'A <b>Boltzmann machine</b> adds randomness and hidden units. Gibbs sampling matched the exact probabilities within 0.005, and learning compares data and model statistics.',
    'An <b>RBM</b> links only visible to hidden units and trains with <b>contrastive divergence</b>. CD-10 reached &minus;3.886 against the best &minus;3.401, CD-1 drifted to &minus;5.696.',
    'A <b>deep belief network</b> stacks RBMs greedily. Pretraining lifted a deep sigmoid network from 0.239 to 0.876. Modern Hopfield networks are attention, and diffusion scores are energy slopes.'],
    'This completes the generative models step. Put models into production in the MLOps subject.')}
{files('Three tasks: Hebb weights, RBM hidden probabilities, and Boltzmann probabilities at a temperature.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In an energy based model, a state with lower energy is', ['Less likely', 'More likely', 'Impossible', 'Always the data'], 1, 'p &prop; e<sup>&minus;E</sup>.', 'Valleys are memories.')
K.quiz('e', 'A Hopfield network is mainly used as', ['A classifier', 'An associative memory that completes damaged patterns', 'A text model', 'A database'], 1, 'Content addressable memory.', 'T from a damaged T.')
K.quiz('e', 'The Hebb rule makes the weight between two units positive when', ['They disagree in the patterns', 'They agree in the patterns', 'They are far apart', 'Always'], 1, 'Fire together, wire together.', 'w = (1/N) &Sigma; p<sub>i</sub> p<sub>j</sub>.')
K.quiz('e', 'What is restricted in a restricted Boltzmann machine?', ['The number of units', 'Connections: only between the visible and hidden layers', 'The learning rate', 'The data type'], 1, 'No links inside a layer.', 'So a layer samples at once.')
K.quiz('m', 'Why does a Hopfield network always stop changing?', ['A timer', 'Each asynchronous update can only lower or keep the energy, and the energy is bounded', 'The weights shrink', 'It does not'], 1, '&Delta;E &le; 0.', 'It settles in a valley.')
K.quiz('m', 'Raising the temperature T of a Boltzmann machine', ['Makes it greedier', 'Flattens the distribution so high energy states become more likely', 'Removes hidden units', 'Changes the weights'], 1, 'Divide energies by T.', '0.249 at T = 1, 0.157 at T = 4.')
K.quiz('m', 'The partition function Z is hard to compute because', ['It needs labels', 'It sums over every possible state, 2<sup>n</sup> of them', 'It needs a GPU', 'It is negative'], 1, 'Exponential sum.', '65,536 images for 16 pixels.')
K.quiz('m', 'Contrastive divergence approximates the model statistics by', ['Exact enumeration', 'Statistics after k Gibbs steps started at the data', 'The labels', 'Random weights'], 1, 'Short chains.', 'CD-1 uses one step.')
K.quiz('m', 'Given the visible units, the hidden units of an RBM are', ['Fully dependent', 'Independent of each other', 'Always 1', 'Deterministic'], 1, 'No hidden to hidden links.', 'One matrix product.')
K.quiz('h', 'CD-1 likelihood rose to &minus;4.863 and then fell to &minus;5.696. Why can that happen?', ['A bug', 'CD-1 is a biased estimate of the likelihood gradient, so following it does not always raise the likelihood', 'Overflow', 'The data changed'], 1, 'Short chains are biased.', 'CD-10 or PCD do better.')
K.quiz('h', 'Greedy layer wise pretraining helped in 2006 mainly because', ['GPUs were fast', 'Deep sigmoid networks from random weights suffered vanishing gradients, and pretraining found a good starting point', 'Labels were plentiful', 'RBMs are convex'], 1, 'Better start.', '0.239 from tiny weights, 0.876 pretrained.')
K.quiz('h', 'A deep belief network and a deep Boltzmann machine differ in that', ['They are the same', 'A DBN is trained layer by layer and has directed lower layers, a DBM is one undirected model trained jointly', 'A DBM has no hidden units', 'A DBN cannot generate'], 1, 'Directed against undirected.', 'Salakhutdinov and Hinton 2009.')
K.quiz('x', 'In the style of a Cambridge Part III exam: in a Hopfield network unit i has s<sub>i</sub> = &minus;1 and h<sub>i</sub> = 0.8. If it flips, the energy changes by', ['+1.6', '&minus;1.6', '0.8', '&minus;0.8'], 1, '&Delta;E = 2 s<sub>i</sub><sup>old</sup> h<sub>i</sub>.', '2 &times; (&minus;1) &times; 0.8.')
K.quiz('x', 'In the style of a Stanford CS236 exam: the update of a modern Hopfield network with softmax(&beta;X<sup>T</sup>&xi;) is equivalent to', ['Convolution', 'Attention, with stored patterns as keys and values', 'Dropout', 'Batch normalisation'], 1, 'Ramsauer and colleagues 2021.', 'Exponential capacity.')

K.calc('e', 'Two units agree in 2 of 3 stored patterns and disagree in 1, with N = 4 units. Hebb weight w<sub>ij</sub>?', '0.25', '(1/N) &Sigma; p<sub>i</sub>p<sub>j</sub>.', ['Products: +1, +1, &minus;1.', 'Sum: 1.', eq('w = 1 / 4 = 0.25')], check=0.25)
K.calc('e', 'State A has energy 0 and state B energy &minus;1, at T = 1. How many times more likely is B?', '2.7183', 'e<sup>(E(A) &minus; E(B))/T</sup>.', ['E(A) &minus; E(B) = 0 &minus; (&minus;1) = 1.', 'Divide by T = 1.', eq('e<sup>1</sup> = 2.7183')], check=2.7183, tol=0.0005)
K.calc('e', 'Capacity of a Hopfield network with 1000 units, using 0.138 N?', '138', 'Multiply.', ['N = 1000.', '0.138 &times; N.', eq('0.138 &times; 1000 = 138 patterns')], check=138)
K.calc('m', 'Three states with energies 0, &minus;1 and 1 at T = 1. Probability of the lowest energy state?', '0.6652', 'e<sup>&minus;E</sup> / Z.', ['Boltzmann factors: e<sup>0</sup> = 1, e<sup>1</sup> = 2.7183, e<sup>&minus;1</sup> = 0.3679.', 'Z = 1 + 2.7183 + 0.3679 = 4.0862.', eq('2.7183 / 4.0862 = 0.6652')], check=0.6652, tol=0.0005)
K.calc('m', 'RBM hidden unit with bias &minus;1, weights 0.5 and 1 to two visible units that are both on. p(h = 1 | v)?', '0.6225', '&sigma;(b + v&middot;w).', ['Input: &minus;1 + 0.5 + 1 = 0.5.', '&sigma;(0.5) = 1 / (1 + e<sup>&minus;0.5</sup>).', eq('1 / 1.6065 = 0.6225')], check=0.6225, tol=0.0005)
K.calc('m', 'Two Hopfield units with w<sub>12</sub> = w<sub>21</sub> = 0.5, both in state +1, no biases. Energy?', '-0.5', '&minus;&frac12; &Sigma;<sub>i,j</sub> w<sub>ij</sub>s<sub>i</sub>s<sub>j</sub>.', ['Pairs (1,2) and (2,1): 0.5 &times; 1 &times; 1 each.', 'Sum: 1.0.', eq('E = &minus;&frac12; &times; 1.0 = &minus;0.5')], check=-0.5)
K.calc('m', 'RBM with a&middot;v = 1 and one hidden unit whose input b + v&middot;W is 0. Free energy F(v)?', '-1.6931', 'F = &minus;a&middot;v &minus; ln(1 + e<sup>input</sup>).', ['&minus;a&middot;v = &minus;1.', 'ln(1 + e<sup>0</sup>) = ln 2 = 0.6931.', eq('F = &minus;1 &minus; 0.6931 = &minus;1.6931')], check=-1.6931, tol=0.0005)
K.calc('h', 'An RBM has 16 visible and 16 hidden units. Summing the hidden units out with the free energy, how many terms does Z need?', '65536', 'Only visible states remain.', ['Without the free energy: 2<sup>32</sup> joint states.', 'The free energy sums the hidden units in closed form.', eq('2<sup>16</sup> = 65,536 visible states')], check=65536)
K.calc('h', 'CD-1 with &eta; = 0.1. For one pair, v<sub>0</sub>p(h|v<sub>0</sub>) = 0.9 and v<sub>1</sub>p(h|v<sub>1</sub>) = 0.6. Weight change?', '0.03', '&eta; (positive &minus; negative).', ['Positive phase: 0.9.', 'Negative phase: 0.6, difference 0.3.', eq('&Delta;w = 0.1 &times; 0.3 = 0.03')], check=0.03, tol=0.0005)
K.calc('x', 'In the style of a statistical physics of learning exam: two states differ in energy by 2. At T = 0.5, how many times more likely is the lower one?', '54.5982', 'e<sup>&Delta;E/T</sup>.', ['&Delta;E / T = 2 / 0.5 = 4.', 'Ratio = e<sup>4</sup>.', eq('e<sup>4</sup> = 54.5982 (at T = 2 it is only e<sup>1</sup> = 2.7183)')], check=54.5982, tol=0.0005)

K.assign('hebb_weights', 'e', 'Hebb weights for a Hopfield network',
         '<p>Write <code>hebb_weights(patterns)</code>. Each pattern is a list of +1 and &minus;1 of length N. Return the N by N weight matrix w<sub>ij</sub> = (1/N) &Sigma; p<sub>i</sub>p<sub>j</sub> as a list of lists, with zeros on the diagonal, each value rounded to 3 decimals.</p>',
         """
def hebb_weights(patterns):
    # your code here
    pass
""", [('hebb_weights([[1, -1]])', [[0.0, -0.5], [-0.5, 0.0]]), ('hebb_weights([[1, 1, -1], [1, -1, 1]])', [[0.0, 0.0, 0.0], [0.0, 0.0, -0.667], [0.0, -0.667, 0.0]]), ('hebb_weights([[1, 1, 1, 1], [1, 1, -1, -1], [1, -1, 1, -1]])', [[0.0, 0.25, 0.25, -0.25], [0.25, 0.0, -0.25, 0.25], [0.25, -0.25, 0.0, 0.25], [-0.25, 0.25, 0.25, 0.0]])],
         """
def hebb_weights(patterns):
    n = len(patterns[0])
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                W[i][j] = round(sum(p[i] * p[j] for p in patterns) / n + 0.0, 3)
    return W
""", 'Two loops over unit pairs, skip i equal to j, and sum the products over the patterns.', '<p>numpy does it in one line: P.T @ P / N, then fill the diagonal with 0. The weights are symmetric, which is what guarantees that the energy never rises.</p>')
K.assign('rbm_hidden_probs', 'm', 'RBM hidden probabilities',
         '<p>Write <code>rbm_hidden_probs(v, W, b)</code>. <code>v</code> is a list of visible values, <code>W</code> a list of rows (one row per visible unit, one column per hidden unit) and <code>b</code> the hidden biases. Return p(h<sub>j</sub> = 1 | v) = &sigma;(b<sub>j</sub> + &Sigma;<sub>i</sub> v<sub>i</sub>W<sub>ij</sub>) for each hidden unit, rounded to 4 decimals.</p>',
         """
def rbm_hidden_probs(v, W, b):
    # your code here
    pass
""", [('rbm_hidden_probs([1, 1], [[0.5], [1.0]], [-1.0])', [0.6225]), ('rbm_hidden_probs([0, 0], [[3.0, -2.0], [3.0, -2.0]], [0.0, 0.0])', [0.5, 0.5]), ('rbm_hidden_probs([1, 0, 1], [[2.0, -1.0], [5.0, 5.0], [2.0, -1.0]], [-2.0, 1.0])', [0.8808, 0.2689])],
         """
import math


def rbm_hidden_probs(v, W, b):
    out = []
    for j in range(len(b)):
        x = b[j] + sum(v[i] * W[i][j] for i in range(len(v)))
        out.append(round(1 / (1 + math.exp(-x)), 4))
    return out
""", 'For each hidden unit add its bias to the weighted sum of the visible values, then apply the sigmoid.', '<p>Because hidden units do not talk to each other, each probability depends only on v. In numpy this is sigmoid(v @ W + b) for a whole batch at once.</p>')
K.assign('boltzmann_probs', 'm', 'Boltzmann probabilities at a temperature',
         '<p>Write <code>boltzmann_probs(energies, T)</code> that returns p = e<sup>&minus;E/T</sup> / Z for each energy, rounded to 4 decimals. Subtract the smallest energy before taking exponentials so large energies do not overflow.</p>',
         """
def boltzmann_probs(energies, T):
    # your code here
    pass
""", [('boltzmann_probs([0, -1, 1], 1)', [0.2447, 0.6652, 0.0900]), ('boltzmann_probs([0, 0], 3)', [0.5, 0.5]), ('boltzmann_probs([0, 2], 0.5)', [0.982, 0.018]), ('boltzmann_probs([1000, 1001], 1)', [0.7311, 0.2689])],
         """
import math


def boltzmann_probs(energies, T):
    low = min(energies)
    w = [math.exp(-(e - low) / T) for e in energies]
    Z = sum(w)
    return [round(x / Z, 4) for x in w]
""", 'Shift by the minimum energy, exponentiate, then divide by the sum.', '<p>Shifting every energy by the same amount cancels in the ratio, so the probabilities do not change, but e<sup>&minus;1000</sup> would underflow to 0 without it.</p>')

K.must('Energy and Z', 'p(s) = e<sup>&minus;E/T</sup>/Z. Low energy, likely. Z sums 2<sup>n</sup> states. High T flattens, low T sharpens.')
K.must('Hopfield', 'Hebb W = (1/N)&Sigma;pp<sup>T</sup>, zero diagonal, s<sub>i</sub> &larr; sign(h<sub>i</sub>), &Delta;E = 2s<sub>i</sub>h<sub>i</sub> &le; 0. Capacity 0.138 N, spurious states.')
K.must('Boltzmann machine', 'Stochastic units p = &sigma;(h/T), hidden units, Gibbs sampling. &Delta;w = &eta;(&lang;s<sub>i</sub>s<sub>j</sub>&rang;<sub>data</sub> &minus; &lang;s<sub>i</sub>s<sub>j</sub>&rang;<sub>model</sub>).')
K.must('RBM', 'Bipartite, layers independent given the other. p(h|v) = &sigma;(b + vW). Free energy sums h out. CD-k: data minus k step statistics, CD-1 biased, PCD better.')
K.must('DBN', 'Stack RBMs greedily, then fine tune with backprop. Pretrained 0.876 against 0.239 from tiny weights. DBM is jointly trained and undirected.')
K.must('Today', 'Modern Hopfield = attention, exponential capacity. Score = &minus;&nabla;E, so diffusion learns an energy slope without Z. Nobel Prize 2024 for Hopfield and Hinton.')

T = K.topic(
    slug='dl-boltzmann', topic='dl-boltzmann', step=(3, 'Generative models', 'dl-s3', 'Networks that create new data: autoencoders and variational autoencoders, generative adversarial networks, diffusion models, and energy based models such as Boltzmann machines.', 'Advanced'),
    title='Energy based models: Hopfield networks, Boltzmann machines and RBMs', short='Boltzmann machines', badge='3.4', minutes=60,
    lead='Learn the energy view of neural networks: Hopfield networks that store and recall memories, Boltzmann machines with temperature and Gibbs sampling, restricted Boltzmann machines trained with contrastive divergence, deep belief networks built by greedy pretraining, and how modern Hopfield networks and diffusion models carry these ideas on.',
    desc='Energy based model, energy function, Boltzmann distribution, partition function, temperature, Hopfield network, Hebb rule, associative memory, capacity, spurious states, Boltzmann machine, Gibbs sampling, hidden units, restricted Boltzmann machine, RBM, free energy, contrastive divergence, CD-k, persistent contrastive divergence, deep belief network, greedy layer wise pretraining, deep Boltzmann machine, modern Hopfield network, attention, score.',
    summary='Energy and the Boltzmann distribution, Hopfield memories, Boltzmann machines and Gibbs sampling, RBMs with contrastive divergence, deep belief networks, and modern descendants.',
    keywords=['Boltzmann machine', 'restricted Boltzmann machine', 'RBM', 'Hopfield network', 'contrastive divergence', 'deep belief network', 'energy based model', 'Gibbs sampling', 'partition function', 'free energy'],
    recap='<p>Give every state an energy, let low energy mean likely, and learn by pushing the energy of the data down and the energy of the model&rsquo;s own dreams up.</p>',
    added='2026-11-14', leet=leet_items())
