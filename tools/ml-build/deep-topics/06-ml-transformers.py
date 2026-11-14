# Deep learning 2.3: attention and transformers. Checked against Bahdanau, Cho and Bengio, Neural machine translation by
# jointly learning to align and translate (ICLR 2015), Vaswani and colleagues, Attention is all you need (NeurIPS
# 2017), Devlin and colleagues, BERT (NAACL 2019), Radford and colleagues (GPT 2, 2019), Brown and colleagues, GPT 3
# (NeurIPS 2020), Holtzman and colleagues, The curious case of neural text degeneration (ICLR 2020), Dosovitskiy and
# colleagues, ViT (ICLR 2021), Dao and colleagues, FlashAttention (NeurIPS 2022), and the Stanford CS224n notes.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-transformers')
K = Kit()

K.code('attention', r'''
# Scaled dot product attention, step by step, with numpy.
import numpy as np


def softmax(s, axis=-1):
    e = np.exp(s - s.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)          # how well each query matches each key
    if mask is not None:
        scores = np.where(mask, scores, -1e9)  # blocked positions get almost zero weight
    weights = softmax(scores)                 # each row adds up to 1
    return weights @ V, weights


# 4 tokens, each with a 2 number query, key and value (chosen by hand to be easy to follow)
Q = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]])
K = np.array([[2.0, 0.0], [0.0, 2.0], [1.0, 1.0], [-1.0, 0.0]])
V = np.array([[10.0, 0.0], [0.0, 10.0], [5.0, 5.0], [0.0, 0.0]])
out, w = attention(Q, K, V)
print('attention weights (row = query, column = key):')
print(np.round(w, 3))
print('outputs:')
print(np.round(out, 2))

# a causal mask: token t may only look at tokens 1..t (used in GPT style decoders)
causal = np.tril(np.ones((4, 4), dtype=bool))
_, w_causal = attention(Q, K, V, causal)
print('causal attention weights:')
print(np.round(w_causal, 3))

# why divide by sqrt(d_k): dot products of random vectors grow with the dimension
rng = np.random.default_rng(0)
for d in [4, 64, 512]:
    q, k = rng.normal(size=(10000, d)), rng.normal(size=(10000, d))
    dots = (q * k).sum(axis=1)
    print(f'd = {d:3d}: std of q.k = {dots.std():6.2f}, after dividing by sqrt(d) = {(dots / np.sqrt(d)).std():.2f}')
''', long=True)

K.code('transformer_block', r'''
# One transformer encoder block in numpy: multi head attention, residuals, layer norm and a feed forward network.
import numpy as np

rng = np.random.default_rng(0)
T, d_model, n_heads, d_ff = 6, 16, 4, 64
d_head = d_model // n_heads


def softmax(s):
    e = np.exp(s - s.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def layer_norm(x, eps=1e-5):
    return (x - x.mean(axis=-1, keepdims=True)) / np.sqrt(x.var(axis=-1, keepdims=True) + eps)


def positional_encoding(T, d):
    pos = np.arange(T)[:, None]
    i = np.arange(0, d, 2)[None, :]
    angle = pos / 10000 ** (i / d)
    pe = np.zeros((T, d))
    pe[:, 0::2], pe[:, 1::2] = np.sin(angle), np.cos(angle)
    return pe


W = {name: rng.normal(scale=1 / np.sqrt(d_model), size=(d_model, d_model)) for name in ['q', 'k', 'v', 'o']}
W1 = rng.normal(scale=1 / np.sqrt(d_model), size=(d_model, d_ff))
W2 = rng.normal(scale=1 / np.sqrt(d_ff), size=(d_ff, d_model))


def multi_head_attention(x):
    def split(m):                                  # (T, d_model) -> (heads, T, d_head)
        return m.reshape(T, n_heads, d_head).transpose(1, 0, 2)
    q, k, v = split(x @ W['q']), split(x @ W['k']), split(x @ W['v'])
    weights = softmax(q @ k.transpose(0, 2, 1) / np.sqrt(d_head))   # (heads, T, T)
    heads = weights @ v                                              # (heads, T, d_head)
    joined = heads.transpose(1, 0, 2).reshape(T, d_model)
    return joined @ W['o'], weights


def encoder_block(x):
    a, weights = multi_head_attention(x)
    x = layer_norm(x + a)                          # residual, then layer norm
    f = np.maximum(0, x @ W1) @ W2                 # position wise feed forward network
    return layer_norm(x + f), weights


tokens = rng.normal(size=(T, d_model))             # stand in for 6 word embeddings
x = tokens + positional_encoding(T, d_model)
out, weights = encoder_block(x)
print('input shape', x.shape, '-> output shape', out.shape)
print('attention weights of head 1, each row sums to', np.round(weights[0].sum(axis=1), 3))

# attention has no idea of order: shuffle the tokens and the outputs shuffle the same way
perm = np.array([5, 4, 3, 2, 1, 0])
out_plain, _ = encoder_block(tokens)
out_shuffled, _ = encoder_block(tokens[perm])
print('without positions, shuffling only reorders the outputs:', np.allclose(out_shuffled, out_plain[perm]))

# weights in one block of a real model (biases and layer norm ignored)
for name, d, blocks in [('BERT base', 768, 12), ('GPT 3', 12288, 96)]:
    per_block = 4 * d * d + 2 * d * 4 * d          # Q, K, V, O plus the two feed forward matrices
    print(f'{name}: {per_block / 1e6:.1f} million weights per block, {blocks} blocks, {blocks * per_block / 1e6:,.0f} million in all blocks')
''', long=True)

K.code('attention_memory', r'''
# The memory task from chapter 2.2, solved with one attention head.
# Each token has (value, marker). The last token asks: which value carried the marker?
import numpy as np


def make_batch(rng, n, T):
    x = np.zeros((n, T, 2))
    x[:, :, 0] = rng.normal(scale=1.0, size=(n, T))     # noise as large as the signal
    first = rng.uniform(-1, 1, size=(n, 1))
    x[:, 0, 0] = first[:, 0]
    x[:, 0, 1] = 1.0                                    # the marker
    return x, first


def softmax(s):
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def train_attention(T, steps=600, d=8, lr=0.02, seed=0):
    rng = np.random.default_rng(seed)
    Wq, Wk, Wv = (rng.normal(scale=0.5, size=(2, d)) for _ in range(3))
    bq = np.zeros(d)
    Wo = rng.normal(scale=0.1, size=(d, 1))
    params = [Wq, bq, Wk, Wv, Wo]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    for step in range(1, steps + 1):
        x, target = make_batch(rng, 64, T)
        q = x[:, -1] @ Wq + bq                           # the query comes from the last token
        K, V = x @ Wk, x @ Wv                            # every token offers a key and a value
        a = softmax(np.einsum('ntd,nd->nt', K, q) / np.sqrt(d))
        out = np.einsum('nt,ntd->nd', a, V)
        y = out @ Wo
        dy = 2 * (y - target) / len(y)
        dout = dy @ Wo.T
        da = np.einsum('nd,ntd->nt', dout, V)
        ds = a * (da - (a * da).sum(axis=1, keepdims=True)) / np.sqrt(d)
        dq = np.einsum('nt,ntd->nd', ds, K)
        dK = ds[:, :, None] * q[:, None, :]
        dV = a[:, :, None] * dout[:, None, :]
        grads = [x[:, -1].T @ dq, dq.sum(axis=0), np.einsum('nti,ntd->id', x, dK),
                 np.einsum('nti,ntd->id', x, dV), out.T @ dy]
        for k, (p, g) in enumerate(zip(params, grads)):
            m[k] = 0.9 * m[k] + 0.1 * g
            v[k] = 0.999 * v[k] + 0.001 * g * g
            p -= lr * (m[k] / (1 - 0.9 ** step)) / (np.sqrt(v[k] / (1 - 0.999 ** step)) + 1e-8)
    x, target = make_batch(np.random.default_rng(99), 1000, T)
    q = x[:, -1] @ Wq + bq
    a = softmax(np.einsum('ntd,nd->nt', x @ Wk, q) / np.sqrt(d))
    y = np.einsum('nt,ntd->nd', a, x @ Wv) @ Wo
    return np.mean((y - target) ** 2), a[:, 0].mean()


print('always answering 0 gives about 0.333. The plain RNN failed from 40 steps.')
for T in [20, 60, 200]:
    err, w0 = train_attention(T)
    print(f'attention, {T:3d} steps: test error {err:.1e}, weight on the marked token {w0:.3f}')
''', long=True)

K.code('decoding', r'''
# How a GPT style model turns scores into text: temperature, top k, top p, and perplexity.
import numpy as np

words = ['mat', 'sofa', 'roof', 'moon', 'piano']
logits = np.array([3.0, 2.0, 1.0, -1.0, -2.0])     # the model's scores for the next word after "The cat sat on the"


def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()


for temp in [0.5, 1.0, 2.0]:
    p = softmax(logits / temp)
    print(f'temperature {temp}: ' + ', '.join(f'{w} {q:.3f}' for w, q in zip(words, p)))

p = softmax(logits)
top_k = np.argsort(p)[::-1][:2]
print('top k = 2 keeps:', [words[i] for i in top_k], 'renormalised to', np.round(p[top_k] / p[top_k].sum(), 3))

order = np.argsort(p)[::-1]
cum = np.cumsum(p[order])
keep = order[:np.searchsorted(cum, 0.9) + 1]
print('top p = 0.9 keeps:', [words[i] for i in keep], f'(they hold {p[keep].sum():.3f} of the probability)')

rng = np.random.default_rng(0)
samples = rng.choice(len(words), size=1000, p=p)
print('1000 samples at temperature 1:', {w: int((samples == i).sum()) for i, w in enumerate(words)})

# perplexity: e to the average negative log probability of the true next words
true_probs = np.array([0.60, 0.25, 0.10, 0.40])
ce = -np.log(true_probs).mean()
print(f'cross entropy {ce:.3f} nats, perplexity {np.exp(ce):.2f}')
print('a model that guesses uniformly over 50,000 tokens has perplexity 50,000')

# attention compares every token with every token: cost grows with T squared
for T in [512, 2048, 8192]:
    print(f'context {T}: {T * T:,} attention scores per head per layer')
''', long=True)

K.lesson('idea', 'Attention: every word looks at every other word', f'''
{src('Bahdanau, Cho and Bengio (ICLR 2015), Vaswani and colleagues (NeurIPS 2017) section 3.2, and the Stanford CS224n notes on attention.')}
{viz('mlattn')}
{wwh('<b>Attention</b> lets each position build its new representation from all positions at once. Every token gets a <b>query</b> (what it is looking for), a <b>key</b> (what it offers) and a <b>value</b> (what it passes on), each a learned linear map of its embedding. A token scores every key with a dot product, turns the scores into weights with softmax, and outputs the weighted sum of the values.',
     'An RNN has to carry information step by step, so distant words are hard to connect and training cannot run in parallel over time. With attention, any two positions are one step apart, and all positions are computed at once on a GPU. This is what made very large language models possible.',
     'Stack queries, keys and values into matrices Q, K and V and compute softmax(QK<sup>T</sup>/&radic;d<sub>k</sub>)V in one go. Divide by &radic;d<sub>k</sub> so scores do not grow with the dimension. For text generation, add a <b>causal mask</b> so each position sees only earlier ones.')}
{run('attention')}
{note('With 4 hand picked tokens, the first query puts weight 0.539 on the key that points the same way and 0.065 on the one that points away. A query of all zeros gives equal weights of 0.25, so it simply averages the values. With the causal mask, the first token can only attend to itself (weight 1). For random vectors, the spread of q &middot; k grows from 2.0 at d = 4 to 22.6 at d = 512, and dividing by &radic;d brings it back to 1.', 'exam')}
{fxs(fx('Scaled dot product attention', 'Attention(Q, K, V) = softmax(QK<sup>T</sup> / &radic;d<sub>k</sub>) V', 'Vaswani and colleagues (2017).', key=True),
     fx('Projections', 'Q = XW<sub>Q</sub>, &nbsp; K = XW<sub>K</sub>, &nbsp; V = XW<sub>V</sub>', 'All learned.', key=True),
     fx('Causal mask', 'score<sub>ij</sub> = &minus;&infin; for j &gt; i', 'Decoders cannot peek ahead.', key=True),
     fx('Why &radic;d<sub>k</sub>', 'Var(q &middot; k) = d<sub>k</sub> for unit variance entries', 'Keeps softmax away from saturation.'))}
{link('nlp', 'Using transformers for language?', 'The Natural Language Processing subject covers tokenisation, embeddings, BERT, GPT and fine tuning for language tasks.', 'Open Natural Language Processing')}
''', kw=['attention', 'self attention', 'query', 'key', 'value', 'scaled dot product attention', 'softmax', 'causal mask'])

K.lesson('block', 'Multi head attention and the transformer block', f'''
{src('Vaswani and colleagues (NeurIPS 2017) sections 3.1 to 3.5, Ba, Kiros and Hinton (2016, layer normalisation), and Xiong and colleagues, On layer normalization in the transformer architecture (ICML 2020).')}
{viz('mlposenc')}
{wwh('<b>Multi head attention</b> runs several attention operations in parallel on smaller slices of the vectors, then joins and mixes the results. A <b>transformer block</b> is multi head attention followed by a position wise <b>feed forward network</b>, each wrapped in a <b>residual connection</b> and <b>layer normalisation</b>. Because attention ignores order, a <b>positional encoding</b> is added to the token embeddings.',
     'Different heads learn different relations, for example one head links pronouns to nouns and another links verbs to objects. The feed forward network then processes each position on its own. Residuals and layer norm keep deep stacks trainable, just as in ResNets. Without positions, "dog bites man" and "man bites dog" would look the same.',
     'Use d<sub>model</sub> = heads &times; d<sub>head</sub> (for example 768 = 12 &times; 64) and a feed forward size of 4 d<sub>model</sub>. Modern models put layer norm before each sub layer (pre norm) for stability, and often use learned or rotary positional encodings instead of fixed sinusoids.')}
{run('transformer_block')}
{note('A block maps 6 vectors of size 16 to 6 vectors of size 16, and each head’s attention rows sum to 1. Without positional encodings, reversing the input tokens only reverses the outputs, which shows that attention alone cannot see order. One block with d<sub>model</sub> = 768 has about 7.1 million weights, so BERT base’s 12 blocks hold 85 million. GPT 3’s 96 blocks of size 12,288 hold about 174 billion.', 'exam')}
{fxs(fx('Multi head attention', 'MultiHead(X) = Concat(head<sub>1</sub>, &hellip;, head<sub>h</sub>) W<sub>O</sub>', 'head<sub>i</sub> = Attention(XW<sub>Q</sub><sup>i</sup>, XW<sub>K</sub><sup>i</sup>, XW<sub>V</sub><sup>i</sup>).', key=True),
     fx('Transformer block (post norm)', '<b>z</b> = LN(<b>x</b> + MHA(<b>x</b>)), &nbsp; <b>y</b> = LN(<b>z</b> + FFN(<b>z</b>))', 'Pre norm uses x + MHA(LN(x)).', key=True),
     fx('Feed forward network', 'FFN(<b>x</b>) = max(0, <b>x</b>W<sub>1</sub> + <b>b</b><sub>1</sub>)W<sub>2</sub> + <b>b</b><sub>2</sub>', 'Usually 4 d<sub>model</sub> hidden units, often GELU.', key=True),
     fx('Sinusoidal encoding', 'PE(pos, 2i) = sin(pos / 10000<sup>2i/d</sup>), &nbsp; PE(pos, 2i + 1) = cos(&hellip;)', 'Wavelengths from 2&pi; to about 10000 &middot; 2&pi;.', key=True),
     fx('Weights per block', '&asymp; 4d&sup2; (attention) + 8d&sup2; (FFN) = 12d&sup2;', 'Ignoring biases and layer norm.'))}
''', kw=['multi head attention', 'transformer block', 'feed forward network', 'residual connection', 'layer normalisation', 'positional encoding', 'pre norm'])

K.lesson('why', 'Why attention beats recurrence on long distances', f'''
{src('Vaswani and colleagues (2017) section 4 and table 1, Bahdanau and colleagues (2015), and the memory task from chapter 2.2.')}
{wwh('In an RNN, information from step 1 must survive every update until step T, a path of length T. In self attention, the last position reads step 1 directly, a path of length 1. Attention also computes all positions in parallel, while an RNN must go one step at a time.',
     'Short paths mean gradients do not vanish with distance, so long range patterns are easy to learn. Parallel computation means far more data can be processed in the same time, and scale has turned out to be the main driver of quality.',
     'The price is that attention compares every pair of positions, so its cost grows with T&sup2;. Long context models use tricks such as FlashAttention (exact but memory efficient), sliding windows, sparse patterns or state space layers to manage this.')}
{run('attention_memory')}
{note('On the exact memory task where the plain RNN failed from 40 steps and the LSTM needed a forget bias of 5 to manage 60, a single attention head learns 20, 60 and even 200 steps in 600 training steps. Its test error is below 1e&minus;5, and it puts 0.987, 0.996 and 1.000 of its attention on the marked token.', 'exam')}
{table(['Layer type', 'Cost per layer', 'Sequential steps', 'Longest path between positions'], [
    ['Self attention', 'O(T&sup2; d)', 'O(1)', 'O(1)'],
    ['Recurrent', 'O(T d&sup2;)', 'O(T)', 'O(T)'],
    ['Convolution, width k', 'O(k T d&sup2;)', 'O(1)', 'O(log<sub>k</sub> T)']])}
''', kw=['path length', 'long range dependency', 'parallelism', 'quadratic cost', 'FlashAttention', 'attention vs RNN'])

K.lesson('llm', 'BERT, GPT and how text is generated', f'''
{src('Devlin and colleagues (NAACL 2019), Radford and colleagues (2018, 2019), Brown and colleagues (NeurIPS 2020), Ouyang and colleagues, InstructGPT (NeurIPS 2022), and Holtzman and colleagues (ICLR 2020).')}
{wwh('<b>BERT</b> is a stack of encoder blocks pretrained to fill in masked words, so it sees context on both sides and is used for understanding tasks. <b>GPT</b> is a stack of decoder blocks with a causal mask, pretrained to predict the next token, so it can generate text. A <b>language model</b> outputs a probability for every token in its vocabulary, and a <b>decoding</b> rule picks the next one.',
     'Pretraining on huge amounts of text teaches grammar, facts and reasoning patterns once, and then a model can be adapted to many tasks with little labelled data, through fine tuning or just a prompt. How you decode changes the output a lot: always taking the top token gives dull, repetitive text, while sampling adds variety.',
     'Fine tune BERT style models for classification and extraction. Use GPT style models for generation and chat, adapted with instruction tuning and RLHF or DPO (Reinforcement learning chapter 3.3). Control sampling with <b>temperature</b>, <b>top k</b> and <b>top p</b>, and measure language models with <b>perplexity</b>.')}
{run('decoding')}
{note('For "The cat sat on the", temperature 0.5 gives "mat" a probability of 0.867, temperature 2 lowers it to 0.456 and spreads the rest. Top k = 2 keeps mat and sofa. Top p = 0.9 keeps mat, sofa and roof, which hold 0.984 of the probability. True next words with probabilities 0.60, 0.25, 0.10 and 0.40 give a perplexity of 3.59. Going from 2,048 to 8,192 tokens multiplies the attention scores per head by 16.', 'exam')}
{table(['', 'BERT style (encoder)', 'GPT style (decoder)', 'T5 style (encoder decoder)'], [
    ['Attention', 'Both directions', 'Causal, left to right', 'Encoder both ways, decoder causal'],
    ['Pretraining task', 'Masked tokens, fill the blank', 'Next token', 'Fill in masked spans'],
    ['Good at', 'Classification, tagging, search', 'Generation, chat, code', 'Translation, summarisation'],
    ['Examples', 'BERT, RoBERTa', 'GPT family, Llama, Mistral', 'T5, BART']])}
{fxs(fx('Language model', 'p(<b>x</b>) = &Pi;<sub>t</sub> p(x<sub>t</sub> | x<sub>&lt;t</sub>)', 'Chain rule of probability.', key=True),
     fx('Temperature', 'p<sub>i</sub> = softmax(z<sub>i</sub> / T)', 'T &lt; 1 sharper, T &gt; 1 flatter.', key=True),
     fx('Perplexity', 'PPL = exp(&minus;(1/N) &Sigma; ln p(x<sub>t</sub> | x<sub>&lt;t</sub>))', 'Lower is better.', key=True),
     fx('Top p (nucleus)', 'Smallest set whose probabilities sum to at least p', 'Holtzman and colleagues (2020).'))}
''', kw=['BERT', 'GPT', 'language model', 'pretraining', 'fine tuning', 'temperature', 'top k', 'top p', 'perplexity', 'decoding'])

K.lesson('versus', 'Transformer families compared', f'''
{versus('Where transformers are used', ['', 'Encoder (BERT)', 'Decoder (GPT)', 'Vision transformer (ViT)', 'Encoder decoder (T5)'], [
    ['Input', 'Tokens', 'Tokens', 'Image patches of 16 &times; 16 pixels', 'Tokens'],
    ['Mask', 'None', 'Causal', 'None', 'Causal in the decoder'],
    ['Output', 'One vector per token', 'Next token probabilities', 'Class or features', 'A new sequence'],
    ['Typical use', 'Search, classification', 'Chat, code, reasoning', 'Image classification, multimodal', 'Translation, summarisation']],
    'choose by the job: encoder for understanding, decoder for generating, encoder decoder when input and output are different sequences, ViT for images at scale.')}
''', kw=['encoder vs decoder', 'vision transformer', 'T5', 'transformer families'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Attention', 'softmax(QK<sup>T</sup>/&radic;d<sub>k</sub> + M)V', 'M = 0 or &minus;&infin; for masking.', key=True),
     fx('Shapes', 'Q: T &times; d<sub>k</sub>, K: T &times; d<sub>k</sub>, V: T &times; d<sub>v</sub> &rArr; output T &times; d<sub>v</sub>', 'Scores T &times; T.', key=True),
     fx('Heads', 'd<sub>head</sub> = d<sub>model</sub> / h', 'Same total cost as one big head.', key=True),
     fx('Cost', 'O(T&sup2;d) time, O(T&sup2;) memory for the scores', 'Per layer.', key=True),
     fx('KV cache', '2 &times; layers &times; T &times; d<sub>model</sub> numbers', 'Stored during generation.'),
     fx('Cross entropy and perplexity', 'PPL = e<sup>H</sup>, H in nats per token', 'H = ln 4 gives PPL 4.'))}
{steps('Worked example: attention for one query by hand', [
    'Query <b>q</b> = (1, 0). Keys <b>k</b><sub>1</sub> = (1, 0) and <b>k</b><sub>2</sub> = (0, 1). Values <b>v</b><sub>1</sub> = (1, 0) and <b>v</b><sub>2</sub> = (0, 1). d<sub>k</sub> = 2.',
    eq('scores = (1, 0) / &radic;2 = (0.7071, 0)'),
    'Softmax.',
    eq('w<sub>1</sub> = e<sup>0.7071</sup> / (e<sup>0.7071</sup> + 1) = 2.028 / 3.028 = 0.6698, &nbsp; w<sub>2</sub> = 0.3302'),
    'Weighted sum of values.',
    eq('output = 0.6698 (1, 0) + 0.3302 (0, 1) = (0.6698, 0.3302)'),
    'The query matched the first key better, so the output leans towards the first value, but softmax still gives the second a share.'])}
{deep('What attention heads learn, and scaling', '<p>Studies of trained transformers find heads that track syntax, copy earlier tokens or attend to the previous token. Olsson and colleagues (2022) describe <b>induction heads</b>, pairs of heads that find an earlier occurrence of the current token and copy what followed it, which appear suddenly during training and support in context learning. Scaling laws (Kaplan and colleagues 2020, Hoffmann and colleagues 2022) show test loss falling as a power law in parameters, data and compute, with the Chinchilla result that parameters and training tokens should grow together, about 20 tokens per parameter. Efficient variants change the attention itself: FlashAttention reorders the computation to avoid storing the T &times; T matrix, multi query and grouped query attention share keys and values across heads to shrink the KV cache, and rotary position embeddings (RoPE, Su and colleagues 2021) encode relative position directly in the dot product.</p>')}
''', kw=['attention formula', 'KV cache', 'induction heads', 'scaling laws', 'RoPE', 'grouped query attention'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A transformer reads all the words at once, and each word decides which other words matter to it. Large language models are very big transformers trained to predict the next word.</p>',
    '<p>Compute attention by hand, build multi head attention and a transformer block, add positional encodings and masks, and control generation with temperature, top k and top p.</p>',
    '<p>Derive the attention shapes and costs, count weights and KV cache size, compare encoder, decoder and encoder decoder models, and explain pretraining and fine tuning.</p>',
    '<p>Study mechanistic interpretability and induction heads, scaling laws, efficient and long context attention, positional schemes such as RoPE and ALiBi, and alternatives such as state space models.</p>')}
{grow('Explain how attention lets words look at each other.',
      'Build and use transformer models.',
      'Analyse, scale and optimise transformers.')}
''', kw=['beginner', 'expert', 'large language models'])

lc(706, 'Design HashMap', 'design-hashmap', 'e', 'Buckets of key value pairs chosen by key modulo the size', 'Hash each key to a bucket and keep a small list of pairs there. A hash map is hard attention: a query matches exactly one key and returns its value. Self attention is the soft version, matching every key a little and blending the values. Our helper runs a list of operations.', r"""
class MyHashMap:
    def __init__(self, size=1009):
        self.buckets = [[] for _ in range(size)]

    def _bucket(self, key):
        return self.buckets[key % len(self.buckets)]

    def put(self, key, value):
        b = self._bucket(key)
        for pair in b:
            if pair[0] == key:
                pair[1] = value
                return
        b.append([key, value])

    def get(self, key):
        for k, v in self._bucket(key):
            if k == key:
                return v
        return -1

    def remove(self, key):
        b = self._bucket(key)
        b[:] = [p for p in b if p[0] != key]


def run_hashmap(ops):
    m, out = MyHashMap(), []
    for op in ops:
        if op[0] == 'put':
            m.put(op[1], op[2])
        elif op[0] == 'get':
            out.append(m.get(op[1]))
        else:
            m.remove(op[1])
    return out
""", [("run_hashmap([('put', 1, 1), ('put', 2, 2), ('get', 1), ('get', 3), ('put', 2, 1), ('get', 2), ('remove', 2), ('get', 2)])", [1, -1, 1, -1])])
lc(208, 'Implement Trie (Prefix Tree)', 'implement-trie-prefix-tree', 'm', 'Nested dictionaries, one level per character, with an end marker', 'Walk one character at a time, creating children as needed. Tokenisers for transformers, such as byte pair encoding, look up the longest known piece of text quickly with exactly this structure. Our helper inserts words and answers queries.', r"""
class Trie:
    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['$'] = True

    def search(self, word):
        node = self._walk(word)
        return node is not None and '$' in node

    def startsWith(self, prefix):
        return self._walk(prefix) is not None

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node:
                return None
            node = node[ch]
        return node


def run_trie(words, queries):
    t = Trie()
    for w in words:
        t.insert(w)
    return [t.search(q) if kind == 'search' else t.startsWith(q) for kind, q in queries]
""", [("run_trie(['apple'], [('search', 'apple'), ('search', 'app'), ('prefix', 'app')])", [True, False, True])])
lc(981, 'Time Based Key-Value Store', 'time-based-key-value-store', 'm', 'Keep timestamps sorted per key and binary search the latest one not after t', 'Store each key’s values in time order and use bisect to find the last one at or before the query time. Only looking at entries up to the current time is the idea behind the causal mask in a GPT style decoder.', r"""
import bisect
from collections import defaultdict


class TimeMap:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key, timestamp):
        i = bisect.bisect_right(self.times[key], timestamp)
        return self.values[key][i - 1] if i else ''


def run_timemap(ops):
    tm, out = TimeMap(), []
    for op in ops:
        if op[0] == 'set':
            tm.set(*op[1:])
        else:
            out.append(tm.get(*op[1:]))
    return out
""", [("run_timemap([('set', 'foo', 'bar', 1), ('get', 'foo', 1), ('get', 'foo', 3), ('set', 'foo', 'bar2', 4), ('get', 'foo', 4), ('get', 'foo', 5), ('get', 'foo', 0)])", ['bar', 'bar', 'bar2', 'bar2', ''])])
lc(215, 'Kth Largest Element in an Array', 'kth-largest-element-in-an-array', 'm', 'A min heap of size k keeps the k largest values seen so far', 'Push each value and pop the smallest whenever the heap grows past k. The top of the heap is the answer. Top k sampling does this every time a language model picks a token: keep the k most likely tokens and sample among them.', r"""
import heapq


def find_kth_largest(nums, k):
    heap = []
    for v in nums:
        heapq.heappush(heap, v)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]
""", [('find_kth_largest([3, 2, 1, 5, 6, 4], 2)', 5), ('find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)', 4)])
lc(23, 'Merge k Sorted Lists', 'merge-k-sorted-lists', 'h', 'A heap holds the current head of every list', 'Put the first node of each list in a min heap. Pop the smallest, attach it, and push its successor. Beam search for text generation keeps a similar heap of the best partial sequences and expands the most promising ones. Our helper builds linked lists from Python lists.', r"""
import heapq


class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


def merge_k_lists(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next


def merge_k_sorted(arrays):
    def build(vals):
        head = None
        for v in reversed(vals):
            head = ListNode(v, head)
        return head
    out, node = [], merge_k_lists([build(a) for a in arrays])
    while node:
        out.append(node.val)
        node = node.next
    return out
""", [('merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]])', [1, 1, 2, 3, 4, 4, 5, 6]), ('merge_k_sorted([])', []), ('merge_k_sorted([[]])', [])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Transformers match queries against keys, read only the past when generating, and pick the most likely tokens. These problems practise key value lookup, a tokeniser’s prefix tree, time ordered lookup, top k selection and merging candidates with a heap. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'hash map', 'trie', 'heap', 'binary search'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Attention</b>: softmax(QK<sup>T</sup>/&radic;d<sub>k</sub>)V. Each token scores every key, softmax gives weights, and the output blends the values.',
    '<b>Multi head attention</b> runs several attentions in parallel. A <b>transformer block</b> adds a feed forward network, residuals and layer norm. <b>Positional encodings</b> supply word order.',
    'Attention connects any two positions in one step and runs in parallel, so it learns long range patterns that RNNs miss, at a cost of O(T&sup2;).',
    '<b>BERT</b> (encoder, masked tokens) understands, <b>GPT</b> (decoder, causal mask, next token) generates. Decoding uses <b>temperature</b>, <b>top k</b> and <b>top p</b>, and quality is measured with <b>perplexity</b>.',
    'One block has about 12d&sup2; weights. Large models stack dozens of blocks and need a KV cache when generating.'],
    'Deep learning 3.1 turns to generative models, starting with autoencoders and variational autoencoders.')}
{files('Three tasks: a softmax, attention for one query, and a causal mask.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In attention, the query of a token represents', ['Its position', 'What the token is looking for in other tokens', 'Its final output', 'The vocabulary'], 1, 'Looking for.', 'Keys say what each token offers.')
K.quiz('e', 'The attention weights for one query', ['Can be any numbers', 'Are positive and add up to 1, because of softmax', 'Are always equal', 'Are the values'], 1, 'Softmax.', 'They form a probability distribution.')
K.quiz('e', 'A causal mask in GPT style models makes each position', ['See every position', 'See only itself and earlier positions', 'See only later positions', 'Ignore itself'], 1, 'No peeking ahead.', 'Needed to train next token prediction.')
K.quiz('e', 'Positional encodings are needed because', ['Attention is too slow', 'Attention by itself ignores the order of the tokens', 'They reduce the vocabulary', 'They replace embeddings'], 1, 'Order blind.', 'Shuffling inputs only shuffles outputs.')
K.quiz('m', 'Scores are divided by &radic;d<sub>k</sub> because', ['It saves memory', 'Dot products grow with dimension and would push softmax into saturation with tiny gradients', 'It makes the weights sum to 1', 'It removes the need for keys'], 1, 'Variance grows with d<sub>k</sub>.', 'Scaling keeps it near 1.')
K.quiz('m', 'Multi head attention helps because', ['It uses fewer weights than one head', 'Different heads can attend to different kinds of relations at the same time', 'It removes the feed forward network', 'It makes attention causal'], 1, 'Many views.', 'Total cost is similar to one wide head.')
K.quiz('m', 'Compared with an RNN, self attention', ['Needs O(T) sequential steps', 'Connects any two positions in one step and computes all positions in parallel', 'Has constant cost in T', 'Cannot handle long sequences at all'], 1, 'Path length 1.', 'The price is O(T&sup2;) cost.')
K.quiz('m', 'BERT is pretrained by', ['Predicting the next token only', 'Predicting masked tokens using context on both sides', 'Translating sentences', 'Classifying images'], 1, 'Fill the blank.', 'So it is bidirectional.')
K.quiz('m', 'Raising the sampling temperature above 1', ['Makes the output more predictable', 'Flattens the distribution so less likely tokens are chosen more often', 'Removes the causal mask', 'Changes the model weights'], 1, 'Divide logits by T.', 'More variety, more mistakes.')
K.quiz('h', 'Top p (nucleus) sampling keeps', ['Exactly p tokens', 'The smallest set of most likely tokens whose probabilities add to at least p', 'Tokens with probability above p', 'Only the top token'], 1, 'Adaptive size.', 'Holtzman and colleagues (2020).')
K.quiz('h', 'The KV cache during generation stores', ['The training data', 'The keys and values of earlier tokens so they are not recomputed at each new step', 'The gradients', 'The vocabulary'], 1, 'Reuse past K and V.', 'Its size grows with context length.')
K.quiz('h', 'A vision transformer (ViT) turns an image into tokens by', ['Using every pixel as a token', 'Cutting it into patches, for example 16 &times; 16, and embedding each patch', 'Running an RNN over rows', 'Using only edges'], 1, 'Patches as words.', 'Dosovitskiy and colleagues (2021).')
K.quiz('x', 'In the style of a Stanford CS224n exam: in a transformer with d<sub>model</sub> = 512 and 8 heads, each head has dimension', ['512', '64', '8', '4096'], 1, 'd<sub>model</sub> / h.', '512 / 8 = 64.')
K.quiz('x', 'In the style of a CMU 11-711 exam: self attention over a sequence of length T costs, per layer,', ['O(T)', 'O(T&sup2; d)', 'O(d&sup3;)', 'O(log T)'], 1, 'Every pair of positions.', 'The reason for efficient attention research.')

K.calc('e', 'Dot product of q = (1, 0) and k = (2, 0)?', '2', 'Multiply and add.', ['1 &times; 2 = 2.', '0 &times; 0 = 0.', eq('2 + 0 = 2')], check=2)
K.calc('e', 'q &middot; k = 8 with d<sub>k</sub> = 64. Scaled score?', '1', 'Divide by &radic;64.', ['&radic;64 = 8.', '8 / 8.', eq('1')], check=1)
K.calc('m', 'Two scores 0 and ln 3. Softmax weight of the second?', '0.75', 'e<sup>ln 3</sup> = 3.', ['e<sup>0</sup> = 1 and e<sup>ln 3</sup> = 3.', 'Sum 4.', eq('3 / 4 = 0.75')], check=0.75)
K.calc('m', 'Context of 512 tokens. Attention scores per head per layer?', '262144', 'T &times; T.', ['Every query against every key.', '512 &times; 512.', eq('262,144')], check=262144)
K.calc('m', 'd<sub>model</sub> = 512 with 8 heads. Dimension per head?', '64', 'd<sub>model</sub> / h.', ['Split evenly.', '512 / 8.', eq('64')], check=64)
K.calc('m', 'Approximate weights in one block with d<sub>model</sub> = 768 (12d&sup2;)?', '7077888', '12 &times; 768&sup2;.', ['768&sup2; = 589,824.', 'Times 12.', eq('7,077,888')], check=7077888)
K.calc('h', 'Wavelength of the fastest sinusoidal positional encoding pair (i = 0)?', '6.283', '2&pi; &times; 10000<sup>0</sup>.', ['10000<sup>0</sup> = 1.', 'sin(pos) repeats every 2&pi;.', eq('2&pi; = 6.283')], check=6.283, tol=0.002)
K.calc('h', 'Average cross entropy of ln 4 nats per token. Perplexity?', '4', 'e<sup>H</sup>.', ['H = ln 4 = 1.386.', 'Exponentiate.', eq('e<sup>ln 4</sup> = 4')], check=4)
K.calc('h', 'Two tokens with logits 2 and 0, temperature 0.5. Probability of the first?', '0.982', 'softmax(z / T).', ['Divide by 0.5: logits 4 and 0.', 'e<sup>4</sup> = 54.6.', eq('54.6 / 55.6 = 0.982')], check=0.982, tol=0.001)
K.calc('x', 'In the style of a systems for ML exam: KV cache for 32 layers, d<sub>model</sub> = 4096, 2,048 tokens, 2 bytes per number. Size in GiB?', '1', '2 &times; layers &times; T &times; d &times; bytes.', ['2 &times; 32 &times; 2048 &times; 4096 = 536,870,912 numbers.', 'Times 2 bytes = 1,073,741,824 bytes.', eq('1,073,741,824 / 2<sup>30</sup> = 1 GiB')], check=1)

K.assign('softmax_weights', 'e', 'A stable softmax',
         '<p>Write <code>softmax_weights(scores)</code> that returns softmax of the list, subtracting the maximum first for stability, each rounded to 4 decimals.</p>',
         """
def softmax_weights(scores):
    # your code here
    pass
""", [('softmax_weights([0.0, 0.0])', [0.5, 0.5]), ('softmax_weights([1.0, 2.0, 3.0])', [0.09, 0.2447, 0.6652]), ('softmax_weights([1000.0, 1000.0, 1000.0, 1000.0])', [0.25, 0.25, 0.25, 0.25])],
         """
import math


def softmax_weights(scores):
    m = max(scores)
    e = [math.exp(s - m) for s in scores]
    total = sum(e)
    return [round(v / total, 4) for v in e]
""", 'Subtract the largest score, exponentiate, and divide by the sum.', '<p>The last test would overflow without subtracting the maximum, because e<sup>1000</sup> is too large for a float.</p>')
K.assign('attend', 'm', 'Attention for one query',
         '<p>Write <code>attend(query, keys, values)</code> that computes scaled dot product attention for one query: scores q &middot; k / &radic;d, softmax, then the weighted sum of the value vectors, each entry rounded to 4 decimals.</p>',
         """
def attend(query, keys, values):
    # your code here
    pass
""", [('attend([1, 0], [[1, 0], [0, 1]], [[1, 0], [0, 1]])', [0.6698, 0.3302]), ('attend([0, 0], [[1, 0], [0, 1]], [[2, 4], [4, 2]])', [3.0, 3.0]), ('attend([2, 2], [[1, 1], [-1, -1], [0, 0]], [[1.0], [0.0], [0.5]])', [0.9689])],
         """
import math


def attend(query, keys, values):
    d = len(query)
    scores = [sum(q * k for q, k in zip(query, key)) / math.sqrt(d) for key in keys]
    m = max(scores)
    e = [math.exp(s - m) for s in scores]
    w = [v / sum(e) for v in e]
    return [round(sum(w[j] * values[j][i] for j in range(len(values))), 4) for i in range(len(values[0]))]
""", 'Score each key, scale by the root of the dimension, softmax the scores, and blend the values with those weights.', '<p>The second test shows that a zero query gives equal weights, so attention returns the plain average of the values.</p>')
K.assign('causal_mask', 'm', 'A causal mask',
         '<p>Write <code>causal_mask(n)</code> that returns an n &times; n list of lists with 1 where position i may attend to position j (j &le; i) and 0 elsewhere.</p>',
         """
def causal_mask(n):
    # your code here
    pass
""", [('causal_mask(3)', [[1, 0, 0], [1, 1, 0], [1, 1, 1]]), ('causal_mask(1)', [[1]])],
         """
def causal_mask(n):
    return [[1 if j <= i else 0 for j in range(n)] for i in range(n)]
""", 'Row i allows columns 0 to i and blocks the rest.', '<p>In practice the zeros are turned into &minus;&infin; added to the scores before softmax, so blocked positions get weight 0.</p>')

K.must('Attention', 'softmax(QK<sup>T</sup>/&radic;d<sub>k</sub>)V. Q, K, V are learned maps of the input. Weights sum to 1.')
K.must('Masking', 'Causal mask for decoders (GPT). Padding masks hide padding tokens.')
K.must('Block', 'MHA + FFN (4d hidden), each with residual and layer norm. About 12d&sup2; weights. d<sub>head</sub> = d/h.')
K.must('Positions', 'Sinusoidal, learned or rotary encodings. Attention alone is order blind.')
K.must('Why it won', 'Path length 1, parallel over positions. Cost O(T&sup2;d), helped by FlashAttention and KV caches.')
K.must('Models and decoding', 'BERT encoder (masked), GPT decoder (next token), T5 encoder decoder, ViT patches. Temperature, top k, top p, perplexity.')

T = K.topic(
    slug='ml-transformers', topic='ml-transformers', step=(2, 'Architectures', 'ml-d2', 'The three big families of deep networks: convolutional networks for images, recurrent networks for sequences, and transformers built on attention.', 'Advanced'),
    title='Attention and transformers', short='Transformers', badge='2.3', minutes=60,
    lead='Build the model behind modern AI: scaled dot product attention, multi head attention and the transformer block, positional encoding, why attention beats recurrence, BERT and GPT, and how text is generated.',
    desc='attention, self attention, query, key, value, scaled dot product attention, causal mask, multi head attention, transformer block, feed forward network, layer normalisation, positional encoding, BERT, GPT, T5, vision transformer, language model, temperature, top k, top p, perplexity, KV cache, FlashAttention.',
    summary='Attention, multi head attention, the transformer block, positional encoding, BERT, GPT and decoding.',
    keywords=['transformer', 'attention', 'self attention', 'multi head attention', 'positional encoding', 'BERT', 'GPT', 'causal mask', 'perplexity', 'temperature'],
    recap='<p>Every token scores every other token, softmax turns the scores into weights, and the output blends their values. Stacked with feed forward layers, residuals and positions, this transformer block powers BERT, GPT and vision transformers.</p>',
    added='2026-11-14', leet=leet_items())
