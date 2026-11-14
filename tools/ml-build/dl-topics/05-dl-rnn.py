# Deep learning 2.2: recurrent neural networks. Checked against Goodfellow, Bengio and Courville, Deep Learning (MIT
# Press 2016) chapter 10, Elman, Finding structure in time (1990), Bengio, Simard and Frasconi, Learning long term
# dependencies with gradient descent is difficult (1994), Hochreiter and Schmidhuber, Long short term memory (1997),
# Gers, Schmidhuber and Cummins (2000, the forget gate), Cho and colleagues (EMNLP 2014, the GRU), Sutskever, Vinyals
# and Le, Sequence to sequence learning (NeurIPS 2014), Jozefowicz, Zaremba and Sutskever (ICML 2015), and the
# Stanford CS231n and CS224n notes.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('dl-rnn')
K = Kit()

K.code('rnn_cell', r'''
# A recurrent neural network cell, unrolled by hand over a short sequence.
import numpy as np

rng = np.random.default_rng(0)
n_in, n_hidden = 3, 4
W_xh = rng.normal(scale=0.5, size=(n_in, n_hidden))     # input to hidden
W_hh = rng.normal(scale=0.5, size=(n_hidden, n_hidden)) # hidden to hidden: the memory
b_h = np.zeros(n_hidden)

sequence = rng.normal(size=(5, n_in))                    # 5 time steps, 3 features each
h = np.zeros(n_hidden)
for t, x in enumerate(sequence, start=1):
    h = np.tanh(x @ W_xh + h @ W_hh + b_h)               # the same weights at every step
    print(f't={t}: h = {np.round(h, 3)}')

# the same cell handles a sequence of any length
long = rng.normal(size=(100, n_in))
h = np.zeros(n_hidden)
for x in long:
    h = np.tanh(x @ W_xh + h @ W_hh + b_h)
print('after 100 steps the state is still 4 numbers:', np.round(h, 3))

# how much does the state at step 100 depend on the input at step t?
# backpropagate d h_100 / d h_t through the tanh and W_hh at every step
hs = [np.zeros(n_hidden)]
for x in long:
    hs.append(np.tanh(x @ W_xh + hs[-1] @ W_hh + b_h))
J = np.eye(n_hidden)
for t in range(100, 0, -1):
    J = J @ (np.diag(1 - hs[t] ** 2) @ W_hh.T)          # chain rule: one more step back
    if 100 - t + 1 in (1, 5, 10, 20, 50):
        print(f'size of d h_100 / d h_{t - 1}: {np.linalg.norm(J):.2e}')
''', long=True)

K.code('rnn_memory', r'''
# Train a vanilla RNN with backpropagation through time (BPTT) on a memory task:
# see a number at step 1, then noise, and output the first number at the last step.
import numpy as np


def make_batch(rng, n, T):
    x = np.zeros((n, T, 2))
    x[:, :, 0] = rng.normal(scale=1.0, size=(n, T))     # channel 0: noise as large as the signal
    first = rng.uniform(-1, 1, size=(n, 1))
    x[:, 0, 0] = first[:, 0]                            # the number to remember
    x[:, 0, 1] = 1.0                                    # channel 1: a marker that says "remember this"
    return x, first


def train_rnn(T, steps=1000, H=16, lr=0.01, seed=0):
    rng = np.random.default_rng(seed)
    Wx = rng.normal(scale=0.5, size=(2, H))
    Wh = rng.normal(scale=1 / np.sqrt(H), size=(H, H))
    b = np.zeros(H)
    Wy = rng.normal(scale=0.1, size=(H, 1))
    by = np.zeros(1)
    params = [Wx, Wh, b, Wy, by]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    for step in range(1, steps + 1):
        x, target = make_batch(rng, 64, T)
        hs = [np.zeros((64, H))]
        for t in range(T):                               # forward through time
            hs.append(np.tanh(x[:, t] @ Wx + hs[-1] @ Wh + b))
        y = hs[-1] @ Wy + by
        dy = 2 * (y - target) / len(y)
        grads = [np.zeros_like(p) for p in params]
        grads[3] = hs[-1].T @ dy
        grads[4] = dy.sum(axis=0)
        dh = dy @ Wy.T
        for t in range(T, 0, -1):                        # backward through time
            dz = dh * (1 - hs[t] ** 2)
            grads[0] += x[:, t - 1].T @ dz
            grads[1] += hs[t - 1].T @ dz
            grads[2] += dz.sum(axis=0)
            dh = dz @ Wh.T
        for k, (p, g) in enumerate(zip(params, grads)):
            g = np.clip(g, -1, 1)                         # gradient clipping
            m[k] = 0.9 * m[k] + 0.1 * g
            v[k] = 0.999 * v[k] + 0.001 * g * g
            p -= lr * (m[k] / (1 - 0.9 ** step)) / (np.sqrt(v[k] / (1 - 0.999 ** step)) + 1e-8)
    x, target = make_batch(np.random.default_rng(99), 1000, T)
    h = np.zeros((1000, H))
    for t in range(T):
        h = np.tanh(x[:, t] @ Wx + h @ Wh + b)
    return np.mean((h @ Wy + by - target) ** 2)


print('always answering 0 gives an error of about 0.333')
for T in [5, 20, 40, 60]:
    print(f'remember across {T:2d} steps: test error {train_rnn(T):.4f}')
''', long=True)

K.code('lstm_memory', r'''
# The same memory task with an LSTM: gates decide what to store, keep and output.
import numpy as np


def make_batch(rng, n, T):
    x = np.zeros((n, T, 2))
    x[:, :, 0] = rng.normal(scale=1.0, size=(n, T))     # channel 0: noise as large as the signal
    first = rng.uniform(-1, 1, size=(n, 1))
    x[:, 0, 0] = first[:, 0]                            # the number to remember
    x[:, 0, 1] = 1.0                                    # channel 1: a marker that says "remember this"
    return x, first


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def lstm_forward(x, Wx, Wh, b, H):
    n, T, _ = x.shape
    h, c = np.zeros((n, H)), np.zeros((n, H))
    cache = []
    for t in range(T):
        z = x[:, t] @ Wx + h @ Wh + b
        i, f, o = sigmoid(z[:, :H]), sigmoid(z[:, H:2 * H]), sigmoid(z[:, 2 * H:3 * H])
        g = np.tanh(z[:, 3 * H:])
        c_prev, h_prev = c, h
        c = f * c_prev + i * g                           # keep some old memory, add some new
        h = o * np.tanh(c)
        cache.append((x[:, t], h_prev, c_prev, i, f, o, g, c))
    return h, cache


def train_lstm(T, forget_bias, steps=1000, H=16, lr=0.01, seed=0):
    rng = np.random.default_rng(seed)
    Wx = rng.normal(scale=0.5, size=(2, 4 * H))
    Wh = rng.normal(scale=1 / np.sqrt(H), size=(H, 4 * H))
    b = np.zeros(4 * H)
    b[H:2 * H] = forget_bias                             # a positive bias keeps the forget gate open (remember)
    Wy = rng.normal(scale=0.1, size=(H, 1))
    by = np.zeros(1)
    params = [Wx, Wh, b, Wy, by]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    for step in range(1, steps + 1):
        x, target = make_batch(rng, 64, T)
        h, cache = lstm_forward(x, Wx, Wh, b, H)
        y = h @ Wy + by
        dy = 2 * (y - target) / len(y)
        grads = [np.zeros_like(p) for p in params]
        grads[3] = h.T @ dy
        grads[4] = dy.sum(axis=0)
        dh, dc = dy @ Wy.T, np.zeros_like(h)
        for xt, h_prev, c_prev, i, f, o, g, c in reversed(cache):
            tc = np.tanh(c)
            dc = dc + dh * o * (1 - tc ** 2)
            dz = np.concatenate([dc * g * i * (1 - i), dc * c_prev * f * (1 - f),
                                 dh * tc * o * (1 - o), dc * i * (1 - g ** 2)], axis=1)
            grads[0] += xt.T @ dz
            grads[1] += h_prev.T @ dz
            grads[2] += dz.sum(axis=0)
            dh, dc = dz @ Wh.T, dc * f                    # the cell path is multiplied only by f
        for k, (p, gr) in enumerate(zip(params, grads)):
            gr = np.clip(gr, -1, 1)
            m[k] = 0.9 * m[k] + 0.1 * gr
            v[k] = 0.999 * v[k] + 0.001 * gr * gr
            p -= lr * (m[k] / (1 - 0.9 ** step)) / (np.sqrt(v[k] / (1 - 0.999 ** step)) + 1e-8)
    x, target = make_batch(np.random.default_rng(99), 1000, T)
    h, _ = lstm_forward(x, Wx, Wh, b, H)
    return np.mean((h @ Wy + by - target) ** 2)


print('always answering 0 gives an error of about 0.333')
for T, fb in [(20, 1.0), (60, 1.0), (60, 5.0)]:
    print(f'LSTM, forget bias {fb}, remember across {T} steps: test error {train_lstm(T, fb):.4f}')
''', long=True)

K.code('gru_cell', r'''
# A GRU cell by hand, and how many weights RNN, GRU and LSTM layers need.
import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


rng = np.random.default_rng(0)
n_in, H = 3, 4
W = {k: rng.normal(scale=0.5, size=(n_in, H)) for k in 'zrh'}
U = {k: rng.normal(scale=0.5, size=(H, H)) for k in 'zrh'}
b = {k: np.zeros(H) for k in 'zrh'}


def gru_step(x, h):
    z = sigmoid(x @ W['z'] + h @ U['z'] + b['z'])            # update gate: how much to change
    r = sigmoid(x @ W['r'] + h @ U['r'] + b['r'])            # reset gate: how much past to use
    h_new = np.tanh(x @ W['h'] + (r * h) @ U['h'] + b['h'])  # candidate state
    return (1 - z) * h + z * h_new, z


h = np.zeros(H)
for t, x in enumerate(rng.normal(size=(4, n_in)), start=1):
    h, z = gru_step(x, h)
    print(f't={t}: update gate {np.round(z, 2)}, h = {np.round(h, 3)}')

# if the update gate is pushed towards 0, the state is copied forward almost unchanged
b['z'][:] = -6
h0 = np.array([0.5, -0.5, 0.2, 0.9])
h = h0.copy()
for x in rng.normal(size=(50, n_in)):
    h, _ = gru_step(x, h)
print('update gate near 0 for 50 steps: start', h0, 'end', np.round(h, 2))


def n_weights(cell, n_in, H):
    gates = {'RNN': 1, 'GRU': 3, 'LSTM': 4}[cell]
    return gates * (n_in * H + H * H + H)


for cell in ['RNN', 'GRU', 'LSTM']:
    print(f'{cell:4s} layer, 100 inputs, 128 hidden units: {n_weights(cell, 100, 128):,} weights')
''', long=True)

K.lesson('idea', 'Recurrent networks: one cell reused at every time step', f'''
{src('Goodfellow, Bengio and Courville (2016) sections 10.1 and 10.2, Elman (1990), and the Stanford CS224n notes on language models and RNNs.')}
{viz('mlunroll')}
{wwh('A <b>recurrent neural network</b> (RNN) reads a sequence one item at a time and keeps a <b>hidden state</b> <b>h</b><sub>t</sub>, a vector that summarises everything seen so far. At each step it combines the new input with the previous state using the <b>same weights</b>: <b>h</b><sub>t</sub> = tanh(<b>x</b><sub>t</sub>W<sub>xh</sub> + <b>h</b><sub>t&minus;1</sub>W<sub>hh</sub> + <b>b</b>). Drawing every step side by side is called <b>unrolling</b> the network.',
     'Text, speech, sensor readings and prices arrive as sequences of varying length, and the meaning of each item depends on what came before. A dense network needs a fixed input size and cannot share what it learns across positions. An RNN handles any length with one small set of weights.',
     'Feed the inputs in order and read the output you need: the last state for classifying a whole sequence, every state for tagging each item, or feed outputs back in to generate a sequence. Train with <b>backpropagation through time</b> (BPTT): unroll, run the usual backward pass, and add up the gradients of the shared weights from every step.')}
{run('rnn_cell')}
{note('A 4 unit RNN reads 5 steps and then 100 steps, and its state is still just 4 numbers. Backpropagating from step 100, the sensitivity of the final state to earlier states falls from 1.39 one step back to 0.61 ten steps back, 0.0088 twenty steps back and 2.0e&minus;7 fifty steps back. We checked the value ten steps back against finite differences.', 'exam')}
{fxs(fx('RNN cell', '<b>h</b><sub>t</sub> = tanh(<b>x</b><sub>t</sub>W<sub>xh</sub> + <b>h</b><sub>t&minus;1</sub>W<sub>hh</sub> + <b>b</b>)', 'Same weights at every t.', key=True),
     fx('Output', '<b>y</b><sub>t</sub> = <b>h</b><sub>t</sub>W<sub>hy</sub> + <b>c</b>', 'At every step or only the last.', key=True),
     fx('BPTT', '&part;L/&part;W<sub>hh</sub> = &Sigma;<sub>t</sub> &part;L<sub>t</sub>/&part;W<sub>hh</sub>', 'Sum over the unrolled copies.', key=True),
     fx('Jacobian back one step', '&part;<b>h</b><sub>t</sub>/&part;<b>h</b><sub>t&minus;1</sub> = diag(1 &minus; <b>h</b><sub>t</sub>&sup2;) W<sub>hh</sub><sup>T</sup>', 'Multiplied once per step back.'))}
{link('nlp', 'Using RNNs for language?', 'The Natural Language Processing subject applies RNNs and LSTMs to language modelling, tagging and translation.', 'Open Natural Language Processing')}
''', kw=['recurrent neural network', 'RNN', 'hidden state', 'unrolling', 'backpropagation through time', 'BPTT', 'sequence'])

K.lesson('longterm', 'The long term dependency problem', f'''
{src('Bengio, Simard and Frasconi (1994), Hochreiter (1991), and Pascanu, Mikolov and Bengio, On the difficulty of training recurrent neural networks (ICML 2013).')}
{wwh('A <b>long term dependency</b> is when an output depends on an input many steps earlier, such as a verb agreeing with a subject far back in the sentence. In BPTT the gradient that links them is a product of one Jacobian per step, so it shrinks or grows exponentially with the distance.',
     'If the gradient <b>vanishes</b>, the network gets no learning signal from distant inputs and cannot learn to remember them. If it <b>explodes</b>, one update can wreck the weights. This is the main reason plain RNNs struggle beyond about 10 to 20 steps.',
     'Clip the gradient norm (to around 1 to 5) to stop explosions. For vanishing, change the architecture: gated cells such as the LSTM and GRU, or attention (chapter 2.3), give information a path that is not squashed at every step.')}
{run('rnn_memory')}
{note('The task: see a number at step 1 with a marker, then noise as large as the signal, and output the number at the end. Always answering 0 scores 0.333. A 16 unit plain RNN trained with BPTT and clipping reaches a test error of 0.0003 at 5 steps and 0.0007 at 20 steps, but 0.328 at 40 steps and 0.345 at 60 steps: no better than guessing 0.', 'exam')}
{fxs(fx('Gradient across k steps', '&part;<b>h</b><sub>t</sub>/&part;<b>h</b><sub>t&minus;k</sub> = &Pi;<sub>j=0</sub><sup>k&minus;1</sup> diag(1 &minus; <b>h</b><sub>t&minus;j</sub>&sup2;) W<sub>hh</sub><sup>T</sup>', 'A product of k matrices.', key=True),
     fx('Rough size', '&asymp; (&gamma; &middot; &sigma;<sub>max</sub>(W<sub>hh</sub>))<sup>k</sup>', '&gamma; &le; 1 is the tanh slope. Below 1 vanishes, above 1 can explode.', key=True),
     fx('Gradient clipping', '<b>g</b> &larr; <b>g</b> &middot; min(1, c/||<b>g</b>||)', 'Pascanu and colleagues (2013).'))}
''', kw=['long term dependency', 'vanishing gradient', 'exploding gradient', 'gradient clipping', 'memory task'])

K.lesson('lstm', 'LSTM: a memory cell with gates', f'''
{src('Hochreiter and Schmidhuber (1997), Gers, Schmidhuber and Cummins (2000), Jozefowicz, Zaremba and Sutskever (ICML 2015), and Olah, Understanding LSTM networks (2015).')}
{viz('mllstm')}
{wwh('A <b>long short term memory</b> (LSTM) cell adds a separate <b>cell state</b> <b>c</b><sub>t</sub> and three <b>gates</b>, each a sigmoid between 0 and 1. The <b>forget gate</b> f decides how much old memory to keep, the <b>input gate</b> i how much of a new candidate g to write, and the <b>output gate</b> o how much of the memory to show as <b>h</b><sub>t</sub>.',
     'The cell state is updated by multiplying with f and adding, not by squashing through a weight matrix and tanh. When f is close to 1 the memory, and its gradient, pass through many steps almost unchanged. This lets LSTMs learn dependencies over hundreds of steps, which made them the standard for speech and translation from about 2014 to 2018.',
     'Use an LSTM layer from your library, with a few hundred units. Initialise the forget gate bias to a positive value (1 is the common default, larger for long memories) so the cell remembers by default at the start of training.')}
{run('lstm_memory')}
{note('On the same memory task, an LSTM with the usual forget bias of 1 learns 20 steps (error 0.0006) but fails at 60 steps (0.345). With forget bias 5, so that f starts near 0.99, it learns 60 steps with an error of 0.0010, where the plain RNN failed already at 40. The hand written LSTM gradients were checked against finite differences.', 'exam')}
{fxs(fx('Gates', '<b>i</b>, <b>f</b>, <b>o</b> = &sigma;(<b>x</b><sub>t</sub>W + <b>h</b><sub>t&minus;1</sub>U + <b>b</b>)', 'Each has its own W, U, b.', key=True),
     fx('Candidate', '<b>g</b> = tanh(<b>x</b><sub>t</sub>W<sub>g</sub> + <b>h</b><sub>t&minus;1</sub>U<sub>g</sub> + <b>b</b><sub>g</sub>)', 'The new information.', key=True),
     fx('Cell update', '<b>c</b><sub>t</sub> = <b>f</b> &odot; <b>c</b><sub>t&minus;1</sub> + <b>i</b> &odot; <b>g</b>', 'Keep some, add some.', key=True),
     fx('Hidden state', '<b>h</b><sub>t</sub> = <b>o</b> &odot; tanh(<b>c</b><sub>t</sub>)', 'What the cell shows.', key=True),
     fx('Gradient along the cell', '&part;<b>c</b><sub>t</sub>/&part;<b>c</b><sub>t&minus;1</sub> = diag(<b>f</b>)', 'No weight matrix, no tanh in the way.', key=True))}
''', kw=['LSTM', 'long short term memory', 'cell state', 'forget gate', 'input gate', 'output gate', 'forget bias'])

K.lesson('gru', 'GRU, bidirectional and sequence to sequence models', f'''
{src('Cho and colleagues (EMNLP 2014), Chung and colleagues, Empirical evaluation of gated recurrent neural networks (2014), Schuster and Paliwal, Bidirectional recurrent neural networks (1997), and Sutskever, Vinyals and Le (NeurIPS 2014).')}
{wwh('A <b>gated recurrent unit</b> (GRU) is a simpler gated cell with two gates and no separate cell state. The <b>update gate</b> z mixes the old state with a candidate, and the <b>reset gate</b> r decides how much of the past the candidate may use. A <b>bidirectional</b> RNN runs one RNN forwards and another backwards and joins their states. A <b>sequence to sequence</b> (encoder decoder) model reads a whole input sequence into a state and then generates an output sequence from it.',
     'The GRU has about three quarters of the weights of an LSTM and often performs about as well. Bidirectional models see both left and right context, which helps tagging and speech recognition. Encoder decoder models made neural machine translation possible, and their weakness, squeezing a long sentence into one vector, led directly to attention.',
     'Try a GRU when you want a smaller, faster model and an LSTM when memory length matters most. Use bidirectional layers only when the whole sequence is available in advance, not for real time prediction. For generation, train the decoder with <b>teacher forcing</b>, feeding the true previous token, and sample at test time.')}
{run('gru_cell')}
{note('With the update gate bias set to &minus;6, a GRU copies its state almost unchanged through 50 noisy steps: (0.5, &minus;0.5, 0.2, 0.9) becomes (0.37, &minus;0.49, 0.09, 0.81). For 100 inputs and 128 hidden units, an RNN layer has 29,312 weights, a GRU 87,936 and an LSTM 117,248.', 'exam')}
{table(['Model', 'Shape', 'Typical use'], [
    ['Many to one', 'Read a sequence, output one label', 'Sentiment, activity recognition'],
    ['Many to many, aligned', 'One output per input step', 'Part of speech tagging, frame labelling'],
    ['One to many', 'One input, generate a sequence', 'Image captioning, music generation'],
    ['Encoder decoder', 'Read all, then generate', 'Translation, summarisation, speech to text']])}
{fxs(fx('GRU update', '<b>h</b><sub>t</sub> = (1 &minus; <b>z</b>) &odot; <b>h</b><sub>t&minus;1</sub> + <b>z</b> &odot; <b>h&#771;</b><sub>t</sub>', 'z near 0 copies the old state.', key=True),
     fx('GRU candidate', '<b>h&#771;</b><sub>t</sub> = tanh(<b>x</b><sub>t</sub>W + (<b>r</b> &odot; <b>h</b><sub>t&minus;1</sub>)U + <b>b</b>)', 'r near 0 ignores the past.', key=True),
     fx('Weights per layer', 'gates &times; (n<sub>in</sub>H + H&sup2; + H)', '1 for RNN, 3 for GRU, 4 for LSTM.', key=True),
     fx('Bidirectional state', '<b>h</b><sub>t</sub> = [<b>h</b>&rarr;<sub>t</sub> , <b>h</b>&larr;<sub>t</sub>]', 'Concatenate both directions.'))}
''', kw=['GRU', 'gated recurrent unit', 'update gate', 'reset gate', 'bidirectional RNN', 'sequence to sequence', 'encoder decoder', 'teacher forcing'])

K.lesson('versus', 'RNN, LSTM, GRU and transformer compared', f'''
{versus('Four sequence models', ['', 'Plain RNN', 'LSTM', 'GRU', 'Transformer'], [
    ['Memory', 'Short, about 10 to 20 steps', 'Long, hundreds of steps', 'Long, similar to LSTM', 'Whole context window directly'],
    ['Weights per layer', '1 &times; (n<sub>in</sub>H + H&sup2; + H)', '4 &times;', '3 &times;', 'Much larger, attention plus feed forward'],
    ['Training speed', 'Sequential in time', 'Sequential in time', 'Sequential in time', 'Parallel over positions'],
    ['Cost per step at inference', 'Constant', 'Constant', 'Constant', 'Grows with context length'],
    ['Common today in', 'Teaching', 'Speech, time series, small devices', 'Same as LSTM, smaller', 'Language, vision, almost everything large']],
    'use a transformer for large language and multimodal tasks. Use a GRU or LSTM for small streaming problems, sensor data or when memory and latency are tight.')}
''', kw=['RNN vs LSTM vs GRU', 'RNN vs transformer'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('RNN', '<b>h</b><sub>t</sub> = &phi;(<b>x</b><sub>t</sub>W<sub>xh</sub> + <b>h</b><sub>t&minus;1</sub>W<sub>hh</sub> + <b>b</b>)', '&phi; usually tanh.', key=True),
     fx('LSTM cell', '<b>c</b><sub>t</sub> = <b>f</b> &odot; <b>c</b><sub>t&minus;1</sub> + <b>i</b> &odot; <b>g</b>, &nbsp; <b>h</b><sub>t</sub> = <b>o</b> &odot; tanh(<b>c</b><sub>t</sub>)', 'Additive memory.', key=True),
     fx('GRU', '<b>h</b><sub>t</sub> = (1 &minus; <b>z</b>)<b>h</b><sub>t&minus;1</sub> + <b>z</b><b>h&#771;</b><sub>t</sub>', 'Interpolation.', key=True),
     fx('Memory after k steps with forget value f', 'c<sub>t+k</sub> &asymp; f<sup>k</sup> c<sub>t</sub>', 'f = 0.99 keeps 90% after 10 steps.', key=True),
     fx('Forget bias for a target f', 'b = ln(f / (1 &minus; f))', 'The inverse sigmoid (logit).'),
     fx('Sequence loss', 'L = &Sigma;<sub>t</sub> &minus;ln p(y<sub>t</sub> | y<sub>&lt;t</sub>, <b>x</b>)', 'Cross entropy at every step.'))}
{steps('Worked example: one step of a scalar LSTM', [
    'Suppose f = 0.9, i = 0.5, o = 0.5, candidate g = 0.4 and old memory c<sub>t&minus;1</sub> = 2.',
    eq('c<sub>t</sub> = 0.9 &times; 2 + 0.5 &times; 0.4 = 1.8 + 0.2 = 2.0'),
    'The output gate scales the squashed memory.',
    eq('h<sub>t</sub> = 0.5 &times; tanh(2.0) = 0.5 &times; 0.964 = 0.482'),
    'Backwards, &part;c<sub>t</sub>/&part;c<sub>t&minus;1</sub> = f = 0.9 along the cell path. Over 20 steps that gives 0.9<sup>20</sup> &asymp; 0.12, compared with a plain RNN where each factor also includes the weight and the tanh slope.'])}
{deep('Why gates help, and what replaced recurrence', '<p>The LSTM cell path behaves like a residual connection through time: c<sub>t</sub> = c<sub>t&minus;1</sub> + (changes) when f is near 1, so the Jacobian is close to the identity, the same reason ResNets train (Greff and colleagues 2017 analyse which LSTM parts matter, finding the forget gate and output activation most important). Gating does not remove vanishing entirely: memories still decay as f<sup>k</sup>, and training is sequential, which limits speed on GPUs. Attention lets every output look directly at every input, with path length 1 between any two positions, and transformers dropped recurrence altogether in 2017. Recurrence has returned in new forms: linear recurrent and state space models such as S4 (Gu and colleagues 2022), Mamba (Gu and Dao 2023) and RWKV train in parallel like transformers but run with a constant cost per step like RNNs, which matters for very long sequences.</p>')}
''', kw=['LSTM equations', 'GRU equations', 'forget bias', 'sequence loss', 'state space models', 'Mamba'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A recurrent network reads a sequence one piece at a time and keeps a running memory, like reading a sentence word by word and remembering what it was about.</p>',
    '<p>Unroll an RNN by hand, train it with backpropagation through time and clipping, build LSTM and GRU cells, and use bidirectional and encoder decoder models.</p>',
    '<p>Derive the BPTT Jacobian product, explain vanishing and exploding gradients and how gates fix them, count weights, and set forget biases for long memories.</p>',
    '<p>Study the theory of gated and orthogonal recurrences, truncated BPTT and its bias, attention based sequence models, and modern linear recurrent and state space models.</p>')}
{grow('Explain how a network can remember the past.',
      'Build and train RNN, LSTM and GRU models.',
      'Analyse memory and gradient flow in sequence models.')}
''', kw=['beginner', 'expert', 'sequence modelling'])

lc(20, 'Valid Parentheses', 'valid-parentheses', 'e', 'Push opening brackets and pop on each closing one', 'Read the string one character at a time, keeping a stack of brackets still open. A closing bracket must match the top of the stack. Like an RNN, the stack is a state that carries what matters from earlier in the sequence.', r"""
def is_valid(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack
""", [("is_valid('()[]{}')", True), ("is_valid('(]')", False), ("is_valid('([)]')", False), ("is_valid('{[]}')", True)])
lc(901, 'Online Stock Span', 'online-stock-span', 'm', 'Keep a stack of (price, span) and merge smaller prices into the new one', 'Prices arrive one at a time, and the answer must come immediately, exactly the streaming setting of an RNN. Pop every earlier price that is not higher and add its span, so each price is pushed and popped once. Our helper feeds a list of prices.', r"""
class StockSpanner:
    def __init__(self):
        self.stack = []

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span


def stock_spans(prices):
    s = StockSpanner()
    return [s.next(p) for p in prices]
""", [('stock_spans([100, 80, 60, 70, 60, 75, 85])', [1, 1, 1, 2, 1, 4, 6])])
lc(394, 'Decode String', 'decode-string', 'm', 'Save the current text and count on a stack at each opening bracket', 'Build the current piece character by character. At "[" save it with the repeat count, at "]" pop and repeat. Nested structure in a sequence is exactly what a single fixed size state finds hard, and why a stack makes it easy.', r"""
def decode_string(s):
    stack, current, num = [], '', 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == '[':
            stack.append((current, num))
            current, num = '', 0
        elif ch == ']':
            prev, k = stack.pop()
            current = prev + current * k
        else:
            current += ch
    return current
""", [("decode_string('3[a]2[bc]')", 'aaabcbc'), ("decode_string('3[a2[c]]')", 'accaccacc'), ("decode_string('2[abc]3[cd]ef')", 'abcabccdcdcdef')])
lc(1143, 'Longest Common Subsequence', 'longest-common-subsequence', 'm', 'A table over prefixes of both strings', 'dp[i][j] is the answer for the first i characters of a and the first j of b. Matching characters extend the diagonal, otherwise take the better of dropping one character. Aligning two sequences is the problem encoder decoder models and attention solve for translation.', r"""
def longest_common_subsequence(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]
""", [("longest_common_subsequence('abcde', 'ace')", 3), ("longest_common_subsequence('abc', 'abc')", 3), ("longest_common_subsequence('abc', 'def')", 0)])
lc(72, 'Edit Distance', 'edit-distance', 'h', 'Each cell is the cheapest of insert, delete or replace from a neighbour', 'dp[i][j] is the number of edits to turn the first i letters of word1 into the first j letters of word2. Speech recognition is scored with this distance at the word level (the word error rate), and CTC training for speech RNNs uses a closely related table.', r"""
def min_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]
""", [("min_distance('horse', 'ros')", 3), ("min_distance('intention', 'execution')", 5), ("min_distance('', 'a')", 1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Recurrent networks read a sequence step by step and carry a state. These problems practise state that carries forward (a stack), streaming answers, nested sequences, and dynamic programming that aligns two sequences. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'stack', 'streaming', 'sequence alignment', 'dynamic programming'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An <b>RNN</b> reads a sequence step by step with one shared cell and a <b>hidden state</b>. Train it with <b>backpropagation through time</b>, summing gradients over the unrolled steps.',
    'The gradient across k steps is a product of k Jacobians, so it <b>vanishes</b> or <b>explodes</b>. Clip gradients for explosions. Plain RNNs fail on dependencies longer than about 20 to 40 steps.',
    'The <b>LSTM</b> adds a cell state with <b>forget</b>, <b>input</b> and <b>output</b> gates: c = f &odot; c + i &odot; g, h = o &odot; tanh(c). A positive forget bias makes it remember by default.',
    'The <b>GRU</b> uses two gates and fewer weights. <b>Bidirectional</b> RNNs see both directions. <b>Encoder decoder</b> models translate, trained with teacher forcing.',
    'Transformers replaced RNNs for most large tasks because they train in parallel and connect distant positions directly.'],
    'Deep learning 2.3 builds attention and the transformer step by step.')}
{files('Three tasks: a scalar RNN forward pass, an LSTM cell update, and counting the weights of RNN, GRU and LSTM layers.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'An RNN processes a sequence by', ['Looking at all items at once with separate weights', 'Reading one item at a time and updating a hidden state with shared weights', 'Sorting the items', 'Ignoring the order'], 1, 'Step by step.', 'Same weights at every step.')
K.quiz('e', 'Unrolling an RNN means', ['Removing layers', 'Drawing the same cell once for every time step', 'Reversing the sequence', 'Making it deeper with new weights'], 1, 'One copy per step.', 'The copies share weights.')
K.quiz('e', 'The forget gate of an LSTM decides', ['Which inputs are noise', 'How much of the old cell memory to keep', 'The learning rate', 'The output size'], 1, 'Keep or forget.', 'Near 1 keeps the memory.')
K.quiz('e', 'Backpropagation through time is', ['A new optimiser', 'Ordinary backpropagation applied to the unrolled network', 'A way to reverse sequences', 'Only used for CNNs'], 1, 'Unroll, then backprop.', 'Gradients of shared weights are summed.')
K.quiz('m', 'Plain RNNs struggle with long term dependencies because', ['They have too many weights', 'The gradient is a product of many per step factors, so it vanishes or explodes', 'They cannot use tanh', 'They need labels at every step'], 1, 'Products of Jacobians.', 'Bengio and colleagues (1994).')
K.quiz('m', 'Gradient clipping mainly fixes', ['Vanishing gradients', 'Exploding gradients', 'Overfitting', 'Slow data loading'], 1, 'Caps the size.', 'Vanishing needs a different architecture.')
K.quiz('m', 'The LSTM cell state passes gradients well because', ['It has no weights at all', 'Its update is additive and multiplied only by the forget gate', 'It uses ReLU', 'It is reset every step'], 1, '&part;c<sub>t</sub>/&part;c<sub>t&minus;1</sub> = f.', 'Close to the identity when f is near 1.')
K.quiz('m', 'A GRU differs from an LSTM in that it', ['Has more gates', 'Has two gates and no separate cell state, so fewer weights', 'Cannot be trained with BPTT', 'Works only on images'], 1, 'Update and reset gates.', 'About 3/4 of the LSTM weights.')
K.quiz('m', 'A bidirectional RNN is not suitable for', ['Tagging words in a finished sentence', 'Live speech recognition that must answer before the sentence ends', 'Offline speech transcription', 'Classifying a whole document'], 1, 'It needs the future.', 'The backward pass needs the whole sequence.')
K.quiz('h', 'Teacher forcing in a sequence to sequence decoder means', ['Using a bigger teacher model', 'Feeding the true previous token as input during training instead of the model’s own guess', 'Freezing the encoder', 'Removing attention'], 1, 'Ground truth inputs.', 'At test time the model feeds its own outputs.')
K.quiz('h', 'Initialising the forget gate bias to a positive value helps because', ['It speeds up the GPU', 'The cell starts by remembering, so gradients flow through long spans early in training', 'It prevents overfitting', 'It removes the input gate'], 1, 'f starts near 1.', 'Jozefowicz and colleagues (2015).')
K.quiz('h', 'The main limitation of encoder decoder RNNs that attention addressed was', ['Too many output classes', 'The whole input had to be squeezed into one fixed size vector', 'They could not use embeddings', 'They had no loss function'], 1, 'The bottleneck.', 'Bahdanau and colleagues (2015).')
K.quiz('x', 'In the style of a Stanford CS224n exam: for an LSTM with input size 100 and hidden size 128, the number of weights including biases is', ['29,312', '87,936', '117,248', '65,536'], 2, '4 &times; (100 &times; 128 + 128&sup2; + 128).', '4 &times; 29,312.')
K.quiz('x', 'In the style of a CMU 11-785 exam: if every backward step through a plain RNN multiplies the gradient by about 0.8, after 50 steps it is about', ['0.8', '0.04', '1.4e&minus;5', '50'], 2, '0.8<sup>50</sup>.', 'Exponential decay.')

K.calc('e', 'Scalar RNN h<sub>t</sub> = tanh(0.5 h<sub>t&minus;1</sub> + x<sub>t</sub>), h<sub>0</sub> = 0, x<sub>1</sub> = 1. h<sub>1</sub>?', '0.7616', 'tanh(1).', ['0.5 &times; 0 + 1 = 1.', 'Apply tanh.', eq('tanh(1) = 0.7616')], check=0.7616, tol=0.0005)
K.calc('e', 'RNN layer with 10 inputs and 20 hidden units, with biases. Number of weights?', '620', 'n<sub>in</sub>H + H&sup2; + H.', ['10 &times; 20 = 200.', '20 &times; 20 = 400, plus 20 biases.', eq('200 + 400 + 20 = 620')], check=620)
K.calc('m', 'LSTM layer with 100 inputs and 128 hidden units. Number of weights?', '117248', '4 &times; (n<sub>in</sub>H + H&sup2; + H).', ['100 &times; 128 = 12,800 and 128&sup2; = 16,384.', 'Plus 128 gives 29,312.', eq('4 &times; 29,312 = 117,248')], check=117248)
K.calc('m', 'GRU layer with 100 inputs and 128 hidden units. Number of weights?', '87936', '3 &times; (n<sub>in</sub>H + H&sup2; + H).', ['One gate block is 29,312.', 'GRU has 3 blocks.', eq('3 &times; 29,312 = 87,936')], check=87936)
K.calc('m', 'LSTM: f = 0.9, c<sub>t&minus;1</sub> = 2, i = 0.5, g = 0.4. New cell state?', '2.0', 'f c + i g.', ['0.9 &times; 2 = 1.8.', '0.5 &times; 0.4 = 0.2.', eq('1.8 + 0.2 = 2.0')], check=2.0)
K.calc('m', 'LSTM output: o = 0.5, c = 1. h?', '0.3808', 'o tanh(c).', ['tanh(1) = 0.7616.', 'Times 0.5.', eq('0.3808')], check=0.3808, tol=0.0005)
K.calc('h', 'Each backward step multiplies the gradient by 0.8. Factor after 50 steps?', '0.0000143', '0.8<sup>50</sup>.', ['ln 0.8 = &minus;0.2231.', 'Times 50 = &minus;11.157.', eq('e<sup>&minus;11.157</sup> = 1.43e&minus;5')], check=1.427e-05, tol=2e-07)
K.calc('h', 'Forget gate fixed at 0.95. Fraction of a memory left after 20 steps?', '0.3585', 'f<sup>20</sup>.', ['ln 0.95 = &minus;0.0513.', 'Times 20 = &minus;1.026.', eq('e<sup>&minus;1.026</sup> = 0.3585')], check=0.3585, tol=0.0005)
K.calc('h', 'Forget gate bias b so that f = &sigma;(b) = 0.99 when inputs are 0?', '4.595', 'b = ln(f/(1 &minus; f)).', ['f/(1 &minus; f) = 0.99/0.01 = 99.', 'Natural log.', eq('ln 99 = 4.595')], check=4.595, tol=0.002)
K.calc('x', 'In the style of a Stanford CS224n problem: a bidirectional LSTM with 128 units in each direction. Features per time step in its output?', '256', 'Concatenate both directions.', ['Forward state: 128.', 'Backward state: 128.', eq('128 + 128 = 256')], check=256)

K.assign('rnn_forward', 'e', 'A scalar RNN forward pass',
         '<p>Write <code>rnn_forward(xs, w, u, b)</code> that runs h<sub>t</sub> = tanh(w h<sub>t&minus;1</sub> + u x<sub>t</sub> + b) from h<sub>0</sub> = 0 over the list xs and returns the list of hidden states h<sub>1</sub>, h<sub>2</sub>, &hellip;, each rounded to 4 decimals.</p>',
         """
def rnn_forward(xs, w, u, b):
    # your code here
    pass
""", [('rnn_forward([1, 0, 0], 0.5, 1.0, 0.0)', [0.7616, 0.3634, 0.1797]), ('rnn_forward([0.5, 0.5], 1.0, 2.0, 0.0)', [0.7616, 0.9427])],
         """
import math


def rnn_forward(xs, w, u, b):
    h, out = 0.0, []
    for x in xs:
        h = math.tanh(w * h + u * x + b)
        out.append(round(h, 4))
    return out
""", 'Keep one running state h, update it with the same w, u and b at every step, and record it.', '<p>The first test is the animation with w = 0.5 and one pulse: the state fades as 0.76, 0.36, 0.18.</p>')
K.assign('lstm_cell_update', 'm', 'An LSTM cell update',
         '<p>Write <code>lstm_cell_update(f, i, g, o, c_prev)</code> that returns [c, h] with c = f c_prev + i g and h = o tanh(c), each rounded to 4 decimals.</p>',
         """
def lstm_cell_update(f, i, g, o, c_prev):
    # your code here
    pass
""", [('lstm_cell_update(0.9, 0.5, 0.4, 0.5, 2.0)', [2.0, 0.482]), ('lstm_cell_update(0.0, 1.0, 0.8, 1.0, 5.0)', [0.8, 0.664])],
         """
import math


def lstm_cell_update(f, i, g, o, c_prev):
    c = f * c_prev + i * g
    h = o * math.tanh(c)
    return [round(c, 4), round(h, 4)]
""", 'Keep f times the old memory, add i times the candidate, then show o times tanh of the new memory.', '<p>In the second test the forget gate is 0, so the old memory of 5 is wiped and only the new value 0.8 is stored.</p>')
K.assign('count_rnn_weights', 'm', 'Counting recurrent weights',
         '<p>Write <code>count_rnn_weights(cell, n_in, hidden)</code> for cell in "RNN", "GRU" or "LSTM", returning the number of weights including biases, using gates &times; (n_in &times; hidden + hidden&sup2; + hidden) with 1, 3 or 4 gate blocks.</p>',
         """
def count_rnn_weights(cell, n_in, hidden):
    # your code here
    pass
""", [("count_rnn_weights('LSTM', 100, 128)", 117248), ("count_rnn_weights('GRU', 100, 128)", 87936), ("count_rnn_weights('RNN', 10, 20)", 620)],
         """
def count_rnn_weights(cell, n_in, hidden):
    blocks = {'RNN': 1, 'GRU': 3, 'LSTM': 4}[cell]
    return blocks * (n_in * hidden + hidden * hidden + hidden)
""", 'Each gate or candidate block has an input matrix, a recurrent matrix and a bias. Multiply one block by the number of blocks.', '<p>Some libraries, such as PyTorch, keep two bias vectors per block, which adds another gates &times; hidden numbers.</p>')

K.must('RNN', 'h<sub>t</sub> = tanh(x<sub>t</sub>W<sub>xh</sub> + h<sub>t&minus;1</sub>W<sub>hh</sub> + b), shared weights, any length. Train with BPTT.')
K.must('Long term problem', 'Gradient across k steps is a product of k Jacobians: vanishes or explodes. Clip for explosions.')
K.must('LSTM', 'c = f &odot; c + i &odot; g, h = o &odot; tanh(c). Cell path multiplied only by f. Positive forget bias.')
K.must('GRU', 'h = (1 &minus; z)h + z h&#771;, reset gate r. 3 blocks against 4 for LSTM.')
K.must('Weights', 'blocks &times; (n<sub>in</sub>H + H&sup2; + H): RNN 1, GRU 3, LSTM 4.')
K.must('Variants', 'Bidirectional needs the whole sequence. Encoder decoder with teacher forcing. Attention fixes the bottleneck.')

T = K.topic(
    slug='dl-rnn', topic='dl-rnn', step=(2, 'Architectures', 'dl-s2', 'The three big families of deep networks: convolutional networks for images, recurrent networks for sequences, and transformers built on attention.', 'Advanced'),
    title='Recurrent networks, LSTM and GRU', short='Recurrent networks', badge='2.2', minutes=55,
    lead='See how networks handle sequences: an RNN unrolled through time, backpropagation through time, why plain RNNs forget, LSTM and GRU gates, bidirectional and encoder decoder models.',
    desc='recurrent neural network, RNN, hidden state, unrolling, backpropagation through time, BPTT, vanishing gradient, exploding gradient, gradient clipping, long term dependency, LSTM, cell state, forget gate, input gate, output gate, GRU, update gate, reset gate, bidirectional RNN, sequence to sequence, encoder decoder, teacher forcing.',
    summary='RNNs and BPTT, the long term dependency problem, LSTM and GRU gates, and sequence model variants.',
    keywords=['RNN', 'LSTM', 'GRU', 'backpropagation through time', 'vanishing gradient', 'forget gate', 'sequence to sequence', 'bidirectional', 'hidden state', 'teacher forcing'],
    recap='<p>One shared cell reads a sequence and carries a state. Plain RNNs lose track of distant inputs because gradients shrink step by step, and gated cells such as the LSTM and GRU keep a memory path that lets information and gradients travel far.</p>',
    added='2026-11-14', leet=leet_items())
