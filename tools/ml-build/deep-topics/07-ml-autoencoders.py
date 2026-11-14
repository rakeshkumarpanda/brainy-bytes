# Deep learning 3.1: autoencoders and variational autoencoders. Checked against Goodfellow, Bengio and Courville, Deep
# Learning (MIT Press 2016) chapters 14 and 20.10.3, Hinton and Salakhutdinov, Reducing the dimensionality of data with
# neural networks (Science 2006), Vincent and colleagues, denoising autoencoders (ICML 2008), Kingma and Welling,
# Auto-encoding variational Bayes (ICLR 2014), Rezende, Mohamed and Wierstra (ICML 2014), Higgins and colleagues,
# beta-VAE (ICLR 2017), van den Oord and colleagues, VQ-VAE (NeurIPS 2017), and Baldi and Hornik (1989) on linear
# autoencoders and PCA.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-autoencoders')
K = Kit()

K.code('autoencoder', r'''
# An autoencoder squeezes 64 pixel digits through a small code and rebuilds them.
# Compare it with PCA, which is the best possible linear compression.
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X = load_digits().data / 16.0                        # 1797 images, 64 pixels in [0, 1]
rng = np.random.default_rng(0)
idx = rng.permutation(len(X))
X_tr, X_te = X[idx[:1400]], X[idx[1400:]]
mean = X_tr.mean(axis=0)


def train_autoencoder(k, hidden=64, epochs=200, lr=0.003, seed=0):
    r = np.random.default_rng(seed)
    sizes = [64, hidden, k, hidden, 64]
    W = [r.normal(scale=np.sqrt(1 / a), size=(a, b)) for a, b in zip(sizes, sizes[1:])]
    b = [np.zeros(s) for s in sizes[1:]]
    m = [np.zeros_like(p) for p in W + b]
    v = [np.zeros_like(p) for p in W + b]
    acts = [np.tanh, lambda z: z, np.tanh, lambda z: z]     # the code layer and output are linear
    t = 0

    def forward(x):
        hs = [x - mean]
        for Wi, bi, f in zip(W, b, acts):
            hs.append(f(hs[-1] @ Wi + bi))
        return hs

    for epoch in range(epochs):
        order = r.permutation(len(X_tr))
        for start in range(0, len(X_tr), 64):
            xb = X_tr[order[start:start + 64]]
            hs = forward(xb)
            g = 2 * (hs[-1] - (xb - mean)) / len(xb)
            gW, gb = [None] * 4, [None] * 4
            for i in (3, 2, 1, 0):
                gW[i], gb[i] = hs[i].T @ g, g.sum(axis=0)
                if i > 0:
                    g = g @ W[i].T
                    if acts[i - 1] is np.tanh:
                        g = g * (1 - hs[i] ** 2)
            t += 1
            for j, (p, gr) in enumerate(zip(W + b, gW + gb)):
                m[j] = 0.9 * m[j] + 0.1 * gr
                v[j] = 0.999 * v[j] + 0.001 * gr * gr
                p -= lr * (m[j] / (1 - 0.9 ** t)) / (np.sqrt(v[j] / (1 - 0.999 ** t)) + 1e-8)
    rec = forward(X_te)[-1] + mean
    return np.mean((rec - X_te) ** 2)


for k in [2, 8]:
    pca = PCA(n_components=k).fit(X_tr)
    pca_err = np.mean((pca.inverse_transform(pca.transform(X_te)) - X_te) ** 2)
    ae_err = train_autoencoder(k)
    print(f'code size {k}: PCA error {pca_err:.4f}, autoencoder error {ae_err:.4f}  (64 pixels -> {k} numbers)')
print(f'just predicting the average image: error {np.mean((mean - X_te) ** 2):.4f}')
''', long=True)

K.code('ae_uses', r'''
# Two everyday uses of autoencoders, with scikit-learn's MLPRegressor as the network.
import numpy as np
from sklearn.datasets import load_digits
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import roc_auc_score

digits = load_digits()
X, y = digits.data / 16.0, digits.target
rng = np.random.default_rng(0)
idx = rng.permutation(len(X))
tr, te = idx[:1400], idx[1400:]

# 1. Denoising: learn to map a noisy image back to the clean one
noisy = np.clip(X + rng.normal(scale=0.3, size=X.shape), 0, 1)
dae = MLPRegressor(hidden_layer_sizes=(64, 16, 64), max_iter=400, random_state=0)
dae.fit(noisy[tr], X[tr])
cleaned = np.clip(dae.predict(noisy[te]), 0, 1)
print(f'error of the noisy test images:   {np.mean((noisy[te] - X[te]) ** 2):.4f}')
print(f'error after the denoising network: {np.mean((cleaned - X[te]) ** 2):.4f}')

# 2. Anomaly detection: train only on digits 0 to 4, then digits 5 to 9 rebuild badly
normal_tr = tr[y[tr] <= 4]
ae = MLPRegressor(hidden_layer_sizes=(32, 8, 32), max_iter=400, random_state=0)
ae.fit(X[normal_tr], X[normal_tr])
err = np.mean((ae.predict(X[te]) - X[te]) ** 2, axis=1)
is_new = (y[te] >= 5).astype(int)
print(f'average reconstruction error, digits 0 to 4: {err[is_new == 0].mean():.4f}')
print(f'average reconstruction error, digits 5 to 9: {err[is_new == 1].mean():.4f}')
print(f'ROC AUC of using the error to spot digits 5 to 9: {roc_auc_score(is_new, err):.3f}')
''')

K.code('vae', r'''
# A variational autoencoder (VAE) on 8 x 8 digits with a 2 number latent space, written in numpy.
import numpy as np
from sklearn.datasets import load_digits

digits = load_digits()
X = digits.data / 16.0
rng = np.random.default_rng(0)
H, Z = 64, 2
W1 = rng.normal(scale=0.1, size=(64, H)); b1 = np.zeros(H)
Wm = rng.normal(scale=0.1, size=(H, Z)); bm = np.zeros(Z)        # encoder mean
Wv = rng.normal(scale=0.1, size=(H, Z)); bv = np.zeros(Z)        # encoder log variance
W3 = rng.normal(scale=0.1, size=(Z, H)); b3 = np.zeros(H)
W4 = rng.normal(scale=0.1, size=(H, 64)); b4 = np.zeros(64)
params = [W1, b1, Wm, bm, Wv, bv, W3, b3, W4, b4]
m = [np.zeros_like(p) for p in params]
v = [np.zeros_like(p) for p in params]


def decode(z):
    h2 = np.tanh(z @ W3 + b3)
    return h2, 1 / (1 + np.exp(-(h2 @ W4 + b4)))


t = 0
for epoch in range(1, 201):
    order = rng.permutation(len(X))
    total_rec = total_kl = 0.0
    for start in range(0, len(X), 64):
        x = X[order[start:start + 64]]
        n = len(x)
        h = np.tanh(x @ W1 + b1)
        mu, logvar = h @ Wm + bm, h @ Wv + bv
        eps = rng.normal(size=mu.shape)
        z = mu + np.exp(0.5 * logvar) * eps                   # the reparameterisation trick
        h2, xhat = decode(z)
        rec = -np.sum(x * np.log(xhat + 1e-7) + (1 - x) * np.log(1 - xhat + 1e-7)) / n
        kl = -0.5 * np.sum(1 + logvar - mu ** 2 - np.exp(logvar)) / n
        total_rec += rec * n
        total_kl += kl * n
        d4 = (xhat - x) / n                                    # gradient of the reconstruction term
        dh2 = d4 @ W4.T * (1 - h2 ** 2)
        dz = dh2 @ W3.T
        dmu = dz + mu / n                                      # plus the KL gradient
        dlogvar = dz * eps * 0.5 * np.exp(0.5 * logvar) + 0.5 * (np.exp(logvar) - 1) / n
        dh = (dmu @ Wm.T + dlogvar @ Wv.T) * (1 - h ** 2)
        grads = [x.T @ dh, dh.sum(0), h.T @ dmu, dmu.sum(0), h.T @ dlogvar, dlogvar.sum(0),
                 z.T @ dh2, dh2.sum(0), h2.T @ d4, d4.sum(0)]
        t += 1
        for k, (p, g) in enumerate(zip(params, grads)):
            m[k] = 0.9 * m[k] + 0.1 * g
            v[k] = 0.999 * v[k] + 0.001 * g * g
            p -= 0.005 * (m[k] / (1 - 0.9 ** t)) / (np.sqrt(v[k] / (1 - 0.999 ** t)) + 1e-8)
    if epoch in (1, 10, 50, 100, 200):
        print(f'epoch {epoch:2d}: reconstruction {total_rec / len(X):6.2f}, KL {total_kl / len(X):5.2f}, '
              f'loss (negative ELBO) {(total_rec + total_kl) / len(X):6.2f}')

# where do the digits sit in the 2 number latent space?
mu_all = np.tanh(X @ W1 + b1) @ Wm + bm
for d in [0, 1, 6]:
    c = mu_all[digits.target == d].mean(axis=0)
    print(f'digit {d}: average code ({c[0]:5.2f}, {c[1]:5.2f})')

# walk through the latent space from the average code of a 1 to the average code of a 0
c1, c0 = mu_all[digits.target == 1].mean(axis=0), mu_all[digits.target == 0].mean(axis=0)
codes = np.array([c1, 0.5 * (c1 + c0), c0])
imgs = decode(codes)[1].reshape(3, 8, 8)
print('decoded from the code of a 1, the halfway point, and the code of a 0:')
for r in range(8):
    print('   '.join(''.join('#' if p > 0.5 else '+' if p > 0.25 else '.' for p in imgs[k, r]) for k in range(3)))
''', long=True)

K.code('vq_codes', r'''
# Discrete codes, the idea behind VQ-VAE: replace each continuous code by the nearest entry of a codebook.
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

X = load_digits().data / 16.0
pca = PCA(n_components=8, random_state=0).fit(X)
codes = pca.transform(X)                              # continuous 8 number codes (a linear encoder)
cont_err = np.mean((pca.inverse_transform(codes) - X) ** 2)
print(f'continuous 8 number code: error {cont_err:.4f}')

for size in [4, 16, 256]:
    km = KMeans(n_clusters=size, n_init=4, random_state=0).fit(codes)
    quantised = km.cluster_centers_[km.labels_]       # snap each code to its nearest codebook vector
    err = np.mean((pca.inverse_transform(quantised) - X) ** 2)
    print(f'codebook of {size:3d} vectors: {int(np.log2(size))} bits per image, error {err:.4f}')

# an image becomes a token id, so a transformer can model images as sequences of tokens
print('first 10 images as token ids (codebook of 16):', KMeans(n_clusters=16, n_init=4, random_state=0).fit(codes).labels_[:10])
''')

K.lesson('idea', 'Autoencoders: compress, then rebuild', f'''
{src('Goodfellow, Bengio and Courville (2016) chapter 14, Hinton and Salakhutdinov (Science 2006), and Baldi and Hornik (1989).')}
{viz('mlbottleneck')}
{wwh('An <b>autoencoder</b> is a network trained to output its own input. An <b>encoder</b> maps the input to a short <b>code</b> (also called the latent vector or bottleneck), and a <b>decoder</b> maps the code back to the input space. The loss is the <b>reconstruction error</b>, for example the mean squared difference between input and output.',
     'The bottleneck forces the network to keep only what matters most, so the code is a compact summary learned without any labels. It is useful for compression, visualisation, denoising, anomaly detection and as a starting point for generative models.',
     'Pick a code size much smaller than the input. Use the same kind of layers as for supervised learning (dense for tables, convolutions for images). A <b>linear</b> autoencoder with squared error learns the same subspace as PCA, so add nonlinear layers to capture curved structure.')}
{run('autoencoder')}
{note('Compressing 8 &times; 8 digits (64 pixels) to 2 numbers, PCA reaches a test error of 0.0534 and a nonlinear autoencoder 0.0357. With 8 numbers, PCA gives 0.0245 and the autoencoder 0.0147. Just predicting the average image gives 0.0743.', 'exam')}
{fxs(fx('Autoencoder', '<b>z</b> = f<sub>enc</sub>(<b>x</b>), &nbsp; <b>x&#770;</b> = f<sub>dec</sub>(<b>z</b>)', 'dim(<b>z</b>) much smaller than dim(<b>x</b>).', key=True),
     fx('Reconstruction loss', 'L = ||<b>x</b> &minus; <b>x&#770;</b>||&sup2;, or binary cross entropy for values in [0, 1]', 'No labels needed.', key=True),
     fx('Linear autoencoder', 'Optimal solution spans the top k principal components', 'Baldi and Hornik (1989).', key=True))}
{link('machine-learning', 'Want the linear version first?', 'Chapter Unsupervised 2.1 of this subject explains PCA, the best linear compression, with its own animations.', 'Open Machine Learning')}
''', kw=['autoencoder', 'encoder', 'decoder', 'latent code', 'bottleneck', 'reconstruction error', 'PCA'])

K.lesson('uses', 'Denoising and anomaly detection', f'''
{src('Vincent and colleagues, Extracting and composing robust features with denoising autoencoders (ICML 2008), and Sakurada and Yairi, Anomaly detection using autoencoders with nonlinear dimensionality reduction (2014).')}
{wwh('A <b>denoising autoencoder</b> receives a corrupted input, with added noise or missing parts, and is trained to output the clean original. An autoencoder used for <b>anomaly detection</b> is trained only on normal data, and an input that it rebuilds badly is flagged as unusual.',
     'Denoising forces the network to learn the structure of the data rather than copy pixels, and it cleans real images, audio and sensor readings. Anomaly detection with reconstruction error needs no examples of the rare faults or frauds, which are often unknown in advance.',
     'For denoising, add realistic corruption during training. For anomaly detection, choose a threshold on the reconstruction error from a validation set of normal data, for example the 99th percentile, and check it against any labelled anomalies you have.')}
{run('ae_uses')}
{note('Adding noise with standard deviation 0.3 gives the test digits an error of 0.0524, and the denoising network brings it down to 0.0324. An autoencoder trained only on digits 0 to 4 rebuilds them with error 0.0322 but digits 5 to 9 with 0.0605, and using the error as an anomaly score separates the two groups with a ROC AUC of 0.901.', 'exam')}
{table(['Variant', 'What changes', 'Used for'], [
    ['Undercomplete', 'Small bottleneck', 'Compression, features'],
    ['Denoising', 'Corrupt the input, rebuild the clean one', 'Cleaning data, robust features'],
    ['Sparse', 'Penalise active code units', 'Interpretable features'],
    ['Contractive', 'Penalise sensitivity of the code to the input', 'Robust features'],
    ['Variational (VAE)', 'Code is a distribution, KL penalty', 'Generating new data']])}
{scene('Spotting faulty machines', 'A factory records vibration from healthy motors for a month and trains an autoencoder on it. In production, each new reading is rebuilt and its error is compared with a threshold set at the 99th percentile of healthy errors. A worn bearing produces vibration patterns the autoencoder never saw, so the error jumps and maintenance is called before the motor fails. No examples of failures were needed to build it.')}
''', kw=['denoising autoencoder', 'anomaly detection', 'reconstruction error', 'threshold', 'sparse autoencoder'])

K.lesson('vae', 'Variational autoencoders', f'''
{src('Kingma and Welling (ICLR 2014), Rezende, Mohamed and Wierstra (ICML 2014), Doersch, Tutorial on variational autoencoders (2016), and Higgins and colleagues (ICLR 2017).')}
{viz('mlvae')}
{wwh('A <b>variational autoencoder</b> (VAE) makes the encoder output a mean <b>&mu;</b> and a spread <b>&sigma;</b> for the code, and samples z = &mu; + &sigma;&epsilon; with &epsilon; from N(0, 1), the <b>reparameterisation trick</b>. The loss adds a <b>KL divergence</b> term that keeps each code distribution close to the <b>prior</b> N(0, I). Together the two terms are the negative <b>evidence lower bound</b> (ELBO).',
     'A plain autoencoder’s codes can sit anywhere, with gaps between them, so decoding a random code gives nonsense. The KL term packs the codes into a smooth region around 0, so you can sample z from N(0, I), decode it, and get a new, realistic example, and moving through the code space changes the output gradually.',
     'Use a Gaussian encoder that outputs &mu; and log &sigma;&sup2; (more stable than &sigma;), binary cross entropy or squared error for the reconstruction, and the closed form KL. Weight the KL by &beta; to trade sharp reconstructions (small &beta;) for a tidier, more disentangled code (large &beta;).')}
{run('vae')}
{note('A VAE with a 2 number code trained on the digits for 200 epochs lowers its loss (negative ELBO) from 36.3 to 24.4 nats per image: reconstruction 21.75 plus KL 2.62. Different digits get different average codes, for example (&minus;1.33, &minus;0.39) for 1 and (1.33, 0.92) for 0. Decoding the point halfway between them gives a shape in between, a smooth path through the code space.', 'exam')}
{fxs(fx('Reparameterisation', 'z = &mu; + &sigma; &odot; &epsilon;, &nbsp; &epsilon; ~ N(0, I)', 'Randomness moved outside the network.', key=True),
     fx('ELBO', 'ln p(<b>x</b>) &ge; E<sub>q(z|x)</sub>[ln p(<b>x</b>|z)] &minus; KL(q(z|<b>x</b>) || p(z))', 'Maximise the lower bound.', key=True),
     fx('Gaussian KL', 'KL = &frac12; &Sigma;<sub>j</sub> (&mu;<sub>j</sub>&sup2; + &sigma;<sub>j</sub>&sup2; &minus; 1 &minus; ln &sigma;<sub>j</sub>&sup2;)', 'Against N(0, I).', key=True),
     fx('&beta; VAE', 'L = reconstruction + &beta; &middot; KL', 'Higgins and colleagues (2017).'))}
''', kw=['variational autoencoder', 'VAE', 'reparameterisation trick', 'KL divergence', 'ELBO', 'prior', 'latent space', 'beta VAE'])

K.lesson('discrete', 'Discrete codes and latent spaces in modern models', f'''
{src('van den Oord, Vinyals and Kavukcuoglu, Neural discrete representation learning (VQ-VAE, NeurIPS 2017), Ramesh and colleagues, DALL-E (ICML 2021), and Rombach and colleagues, latent diffusion (CVPR 2022).')}
{wwh('A <b>vector quantised</b> autoencoder (VQ-VAE) snaps each continuous code to the nearest vector in a learned <b>codebook</b>, so every image or patch becomes a token id. Modern image generators also run in the <b>latent space</b> of an autoencoder rather than on raw pixels.',
     'Discrete tokens let a transformer model images, audio and video exactly as it models text. Working in a compact latent space cuts the cost of generation many times, which is why Stable Diffusion first encodes images to a latent 8 times smaller in each direction.',
     'Learn the codebook with the autoencoder, using a straight through gradient for the snapping step and a commitment loss that keeps codes near their codebook vectors. More codebook entries keep more detail, at the cost of more bits per token.')}
{run('vq_codes')}
{note('Snapping 8 number codes of the digits to a codebook of 4 vectors (2 bits per image) gives an error of 0.0549, 16 vectors (4 bits) give 0.0375 and 256 vectors (8 bits) give 0.0273, approaching the continuous code’s 0.0239. Each image becomes a single token id. Here the codebook is learned with k means on PCA codes, a simple stand in for a trained VQ-VAE.', 'exam')}
{fxs(fx('Quantisation', 'z<sub>q</sub> = e<sub>k</sub>, &nbsp; k = argmin<sub>j</sub> ||z<sub>e</sub> &minus; e<sub>j</sub>||', 'Nearest codebook vector.', key=True),
     fx('Bits per token', 'log<sub>2</sub>(codebook size)', '256 entries = 8 bits.', key=True),
     fx('VQ-VAE loss', '||<b>x</b> &minus; <b>x&#770;</b>||&sup2; + ||sg[z<sub>e</sub>] &minus; e||&sup2; + &beta;||z<sub>e</sub> &minus; sg[e]||&sup2;', 'sg = stop gradient.'))}
''', kw=['VQ-VAE', 'codebook', 'vector quantisation', 'discrete latent', 'latent space', 'tokens'])

K.lesson('versus', 'Autoencoder, VAE and PCA compared', f'''
{versus('Ways to learn a compact code', ['', 'PCA', 'Autoencoder', 'Variational autoencoder', 'VQ-VAE'], [
    ['Mapping', 'Linear', 'Nonlinear', 'Nonlinear, probabilistic', 'Nonlinear, discrete'],
    ['Code', 'Fixed point', 'Fixed point', 'A distribution N(&mu;, &sigma;&sup2;)', 'A codebook index'],
    ['Can generate new data', 'Poorly', 'Poorly, gaps in code space', 'Yes, sample from the prior', 'Yes, with a prior over tokens'],
    ['Training', 'Closed form (SVD)', 'Gradient descent', 'Gradient descent with reparameterisation', 'Gradient descent with straight through'],
    ['Typical use', 'Quick compression, visualising', 'Denoising, anomaly detection', 'Generation, smooth latent spaces', 'Image and audio tokens, latent generators']],
    'use PCA first as a baseline, an autoencoder for nonlinear compression or anomalies, and a VAE or VQ-VAE when you need to generate.')}
''', kw=['PCA vs autoencoder', 'autoencoder vs VAE', 'VQ-VAE'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Reconstruction (Gaussian)', '&minus;ln p(<b>x</b>|z) &prop; ||<b>x</b> &minus; <b>x&#770;</b>||&sup2;', 'Squared error.', key=True),
     fx('Reconstruction (Bernoulli)', '&minus;&Sigma; [x ln x&#770; + (1 &minus; x) ln(1 &minus; x&#770;)]', 'Binary cross entropy.', key=True),
     fx('KL of one dimension', '&frac12;(&mu;&sup2; + &sigma;&sup2; &minus; 1 &minus; ln &sigma;&sup2;)', 'Zero only at &mu; = 0, &sigma; = 1.', key=True),
     fx('Log variance', '&sigma; = exp(&frac12; log &sigma;&sup2;)', 'Network outputs log &sigma;&sup2; for stability.', key=True),
     fx('ELBO gap', 'ln p(<b>x</b>) &minus; ELBO = KL(q(z|<b>x</b>) || p(z|<b>x</b>))', 'Tight when q matches the true posterior.'))}
{steps('Worked example: deriving the ELBO', [
    'Start from the log likelihood and bring in the encoder distribution q(z|<b>x</b>).',
    eq('ln p(<b>x</b>) = ln &int; p(<b>x</b>|z) p(z) dz = ln E<sub>q</sub>[p(<b>x</b>|z) p(z) / q(z|<b>x</b>)]'),
    'Jensen’s inequality moves the log inside the expectation, since ln is concave.',
    eq('ln p(<b>x</b>) &ge; E<sub>q</sub>[ln p(<b>x</b>|z)] + E<sub>q</sub>[ln p(z) &minus; ln q(z|<b>x</b>)]'),
    'The second term is minus a KL divergence.',
    eq('ln p(<b>x</b>) &ge; E<sub>q</sub>[ln p(<b>x</b>|z)] &minus; KL(q(z|<b>x</b>) || p(z)) = ELBO'),
    'Example of the KL for one dimension with &mu; = 0 and &sigma; = 0.5: &frac12;(0 + 0.25 &minus; 1 &minus; ln 0.25) = &frac12;(0.25 &minus; 1 + 1.386) = 0.318.'])}
{deep('Posterior collapse, disentanglement and better bounds', '<p>A strong decoder, such as an autoregressive one, can model the data without using z, and the KL term then pushes every q(z|x) onto the prior: <b>posterior collapse</b>. Remedies include KL annealing (start with &beta; = 0 and raise it), free bits (no KL penalty below a set amount per dimension) and weaker decoders. A larger &beta; encourages each code dimension to capture one factor of variation (&beta; VAE, Higgins and colleagues 2017), though Locatello and colleagues (ICML 2019) proved that unsupervised disentanglement is impossible without inductive biases. Importance weighted autoencoders (Burda and colleagues 2016) tighten the bound with several samples, and hierarchical VAEs such as NVAE (Vahdat and Kautz 2020) reach image quality close to GANs. Diffusion models (chapter 3.3) can be viewed as a very deep hierarchical VAE with a fixed encoder.</p>')}
''', kw=['ELBO derivation', 'Jensen inequality', 'KL formula', 'posterior collapse', 'disentanglement', 'hierarchical VAE'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>An autoencoder learns to shrink data into a few numbers and rebuild it. If it can rebuild well, those few numbers must capture what matters.</p>',
    '<p>Build autoencoders and compare them with PCA, use denoising and reconstruction error for anomalies, and train a VAE with the reparameterisation trick.</p>',
    '<p>Derive the ELBO and the Gaussian KL, choose reconstruction losses, tune &beta;, and explain discrete codebooks and latent spaces in modern generators.</p>',
    '<p>Study posterior collapse, tighter bounds, hierarchical and flow based priors, disentanglement theory and the link between VAEs and diffusion models.</p>')}
{grow('Explain what an autoencoder learns.',
      'Build autoencoders and VAEs for real tasks.',
      'Analyse latent variable models and their bounds.')}
''', kw=['beginner', 'expert', 'latent variable models'])

lc(461, 'Hamming Distance', 'hamming-distance', 'e', 'XOR the numbers and count the 1 bits', 'Bits that differ become 1 after XOR, so count them. Binary codes compared by Hamming distance are used for fast similarity search with learned hash codes, a close cousin of autoencoder codes.', r"""
def hamming_distance(x, y):
    return bin(x ^ y).count('1')
""", [('hamming_distance(1, 4)', 2), ('hamming_distance(3, 1)', 1)])
lc(535, 'Encode and Decode TinyURL', 'encode-and-decode-tinyurl', 'm', 'Map each long URL to a short code and back with two dictionaries', 'The encoder turns a long URL into a short code and the decoder turns the code back. This is lossless, unlike an autoencoder, but the same encoder and decoder pair. Our helper checks that every URL survives a round trip.', r"""
class Codec:
    def __init__(self):
        self.long_to_code, self.code_to_long = {}, {}

    def encode(self, long_url):
        if long_url not in self.long_to_code:
            code = str(len(self.long_to_code))
            self.long_to_code[long_url] = code
            self.code_to_long[code] = long_url
        return 'http://tinyurl.com/' + self.long_to_code[long_url]

    def decode(self, short_url):
        return self.code_to_long[short_url.rsplit('/', 1)[1]]


def round_trip(urls):
    c = Codec()
    return [c.decode(c.encode(u)) == u for u in urls]
""", [("round_trip(['https://leetcode.com/problems/design-tinyurl', 'https://example.org/a'])", [True, True])])
lc(443, 'String Compression', 'string-compression', 'm', 'Two pointers: read a run, write the character and its count', 'Walk through runs of the same character and overwrite the array in place with the character followed by the run length. Run length encoding is a simple lossless compressor, the opposite end from an autoencoder’s learned, lossy one. Our helper returns the new length and the compressed text.', r"""
def compress(chars):
    write = read = 0
    while read < len(chars):
        ch, start = chars[read], read
        while read < len(chars) and chars[read] == ch:
            read += 1
        chars[write] = ch
        write += 1
        if read - start > 1:
            for d in str(read - start):
                chars[write] = d
                write += 1
    return write


def compress_result(s):
    chars = list(s)
    n = compress(chars)
    return [n, ''.join(chars[:n])]
""", [("compress_result('aabbccc')", [6, 'a2b2c3']), ("compress_result('a')", [1, 'a']), ("compress_result('abbbbbbbbbbbb')", [4, 'ab12'])])
lc(89, 'Gray Code', 'gray-code', 'm', 'i XOR (i shifted right by 1) gives the i-th Gray code', 'Neighbouring Gray codes differ in exactly one bit, so a small step in the sequence is a small change in the code. A good VAE latent space has the same property: nearby codes decode to similar outputs.', r"""
def gray_code(n):
    return [i ^ (i >> 1) for i in range(2 ** n)]
""", [('gray_code(2)', [0, 1, 3, 2]), ('gray_code(1)', [0, 1]), ('gray_code(3)', [0, 1, 3, 2, 6, 7, 5, 4])])
lc(297, 'Serialize and Deserialize Binary Tree', 'serialize-and-deserialize-binary-tree', 'h', 'Preorder with a marker for empty children, then rebuild recursively', 'Write the value of each node before its children and "#" for a missing child. Reading the list back in the same order rebuilds the exact tree. An encoder and decoder that must agree on a format is the core of any autoencoder. Our helper builds a tree from level order, serialises it and checks the round trip.', r"""
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def serialize(root):
    out = []

    def walk(node):
        if node is None:
            out.append('#')
            return
        out.append(str(node.val))
        walk(node.left)
        walk(node.right)
    walk(root)
    return ','.join(out)


def deserialize(data):
    vals = iter(data.split(','))

    def build():
        v = next(vals)
        if v == '#':
            return None
        node = TreeNode(int(v))
        node.left = build()
        node.right = build()
        return node
    return build()


def tree_round_trip(level_order):
    nodes = [None if v is None else TreeNode(v) for v in level_order]
    kids = iter(nodes[1:])
    for node in nodes:
        if node:
            node.left, node.right = next(kids, None), next(kids, None)
    root = nodes[0] if nodes else None
    text = serialize(root)
    return [text, serialize(deserialize(text)) == text]
""", [('tree_round_trip([1, 2, 3, None, None, 4, 5])', ['1,2,#,#,3,4,#,#,5,#,#', True]), ('tree_round_trip([])', ['#', True])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Autoencoders are encoder and decoder pairs that agree on a compact code. These problems practise comparing binary codes, round trip encoders, simple lossless compression, codes where neighbours differ by one bit, and serialising a structure so it can be rebuilt. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'encoding', 'compression', 'bit manipulation', 'serialisation'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An <b>autoencoder</b> learns an encoder and decoder that rebuild the input through a small <b>code</b>, trained on reconstruction error without labels.',
    'A <b>linear</b> autoencoder matches PCA. Nonlinear layers capture curved structure and rebuild better with the same code size.',
    '<b>Denoising</b> autoencoders clean corrupted inputs. Training on normal data and flagging high <b>reconstruction error</b> detects <b>anomalies</b>.',
    'A <b>VAE</b> outputs &mu; and &sigma;, samples z = &mu; + &sigma;&epsilon;, and adds <b>KL</b> = &frac12;&Sigma;(&mu;&sup2; + &sigma;&sup2; &minus; 1 &minus; ln &sigma;&sup2;). The loss is the negative <b>ELBO</b>, and sampling z from N(0, I) generates new data.',
    '<b>VQ-VAE</b> codes are codebook indices, turning images into tokens, and latent spaces make modern generators efficient.'],
    'Deep learning 3.2 covers generative adversarial networks, where two networks compete.')}
{files('Three tasks: the reparameterisation step, the Gaussian KL, and the reconstruction error.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'An autoencoder is trained to', ['Predict labels', 'Output its own input after passing it through a small code', 'Generate random noise', 'Sort the data'], 1, 'Rebuild the input.', 'No labels needed.')
K.quiz('e', 'The bottleneck of an autoencoder is', ['The output layer', 'The small code layer in the middle', 'The loss function', 'The optimiser'], 1, 'The narrow part.', 'It forces compression.')
K.quiz('e', 'A denoising autoencoder is given', ['Clean inputs and noisy targets', 'Noisy inputs and the clean originals as targets', 'Labels', 'Only noise'], 1, 'Noisy in, clean out.', 'It must learn the structure.')
K.quiz('e', 'For anomaly detection, an autoencoder is trained on', ['Only anomalies', 'Mostly normal data, then high reconstruction error flags anomalies', 'Random data', 'Labels of anomalies'], 1, 'Normal data.', 'It rebuilds unseen patterns badly.')
K.quiz('m', 'A linear autoencoder trained with squared error learns', ['A random projection', 'The same subspace as PCA', 'A clustering', 'A decision tree'], 1, 'Baldi and Hornik (1989).', 'Nonlinearity is what adds power.')
K.quiz('m', 'The reparameterisation trick writes the sample as', ['z = &mu; &times; &sigma;', 'z = &mu; + &sigma;&epsilon; with &epsilon; from N(0, 1)', 'z = &epsilon;', 'z = &mu; only'], 1, 'Move the randomness out.', 'So gradients reach &mu; and &sigma;.')
K.quiz('m', 'The KL term in a VAE', ['Measures reconstruction quality', 'Keeps each code distribution close to the prior N(0, I)', 'Is always negative', 'Counts parameters'], 1, 'Regulariser.', 'Makes sampling from the prior work.')
K.quiz('m', 'Why can a VAE generate new data but a plain autoencoder struggles?', ['The VAE has more layers', 'The VAE’s codes fill a smooth region around 0, so random codes from N(0, I) decode well', 'The plain autoencoder has no decoder', 'The VAE uses labels'], 1, 'No gaps in code space.', 'The KL term does this.')
K.quiz('m', 'The encoder of a VAE usually outputs log &sigma;&sup2; instead of &sigma; because', ['It is faster', 'It can be any real number and keeps &sigma; positive and stable', 'It makes KL zero', 'It removes the decoder'], 1, '&sigma; = exp(&frac12; log &sigma;&sup2;).', 'No constraint needed.')
K.quiz('h', 'Increasing &beta; in a &beta; VAE tends to', ['Sharpen reconstructions', 'Give a tidier, more disentangled code at the cost of blurrier reconstructions', 'Remove the KL term', 'Make training supervised'], 1, 'Trade off.', 'Higgins and colleagues (2017).')
K.quiz('h', 'Posterior collapse means', ['The encoder outputs huge codes', 'The decoder ignores z and every q(z|x) matches the prior', 'Training diverges', 'The KL becomes negative'], 1, 'Unused latent.', 'KL annealing and free bits help.')
K.quiz('h', 'A VQ-VAE turns each code into', ['A probability', 'The index of the nearest codebook vector, a discrete token', 'A label', 'A random number'], 1, 'Quantisation.', 'Lets transformers model images as tokens.')
K.quiz('x', 'In the style of a Stanford CS236 exam: the ELBO is a lower bound on', ['The KL divergence', 'The log likelihood ln p(x)', 'The reconstruction error', 'The number of parameters'], 1, 'Evidence = ln p(x).', 'The gap is KL(q(z|x) || p(z|x)).')
K.quiz('x', 'In the style of an Oxford deep learning exam: the KL between N(&mu;, &sigma;&sup2;) and N(0, 1) is zero exactly when', ['&mu; = 1, &sigma; = 0', '&mu; = 0 and &sigma; = 1', '&sigma; = 0', 'Never'], 1, 'Identical distributions.', '&frac12;(&mu;&sup2; + &sigma;&sup2; &minus; 1 &minus; ln &sigma;&sup2;) = 0.')

K.calc('e', 'An autoencoder compresses 64 pixels into 8 numbers. Compression factor?', '8', 'Input size over code size.', ['Input 64 numbers.', 'Code 8 numbers.', eq('64 / 8 = 8')], check=8)
K.calc('e', 'Reparameterisation with &mu; = 1, &sigma; = 0.5 and &epsilon; = 2. z?', '2', '&mu; + &sigma;&epsilon;.', ['&sigma;&epsilon; = 0.5 &times; 2 = 1.', 'Add &mu;.', eq('1 + 1 = 2')], check=2)
K.calc('m', 'KL between N(1, 1) and N(0, 1)?', '0.5', '&frac12;(&mu;&sup2; + &sigma;&sup2; &minus; 1 &minus; ln &sigma;&sup2;).', ['&mu;&sup2; = 1, &sigma;&sup2; = 1, ln 1 = 0.', '1 + 1 &minus; 1 &minus; 0 = 1.', eq('&frac12; &times; 1 = 0.5')], check=0.5)
K.calc('m', 'KL between N(0, 0.5&sup2;) and N(0, 1)?', '0.3181', 'Same formula with &sigma; = 0.5.', ['&sigma;&sup2; = 0.25, ln 0.25 = &minus;1.3863.', '0 + 0.25 &minus; 1 + 1.3863 = 0.6363.', eq('&frac12; &times; 0.6363 = 0.3181')], check=0.3181, tol=0.0005)
K.calc('m', 'The encoder outputs log &sigma;&sup2; = &minus;2. &sigma;?', '0.3679', 'exp(&frac12; log &sigma;&sup2;).', ['&frac12; &times; (&minus;2) = &minus;1.', 'Exponentiate.', eq('e<sup>&minus;1</sup> = 0.3679')], check=0.3679, tol=0.0005)
K.calc('m', 'Binary cross entropy for one pixel with x = 1 and x&#770; = 0.8?', '0.2231', '&minus;ln x&#770; when x = 1.', ['The (1 &minus; x) term is 0.', '&minus;ln 0.8.', eq('0.2231')], check=0.2231, tol=0.0005)
K.calc('h', 'Data with PCA eigenvalues 5, 3, 1 and 1. A linear autoencoder with a 2 number code. Fraction of variance it cannot rebuild?', '0.2', 'Unused eigenvalues over the total.', ['It keeps the top two: 5 + 3 = 8.', 'Total 10, missing 2.', eq('2 / 10 = 0.2')], check=0.2)
K.calc('h', 'Dense autoencoder 64 &rarr; 16 &rarr; 64 with biases. Number of weights?', '2128', 'Two layers.', ['Encoder 64 &times; 16 + 16 = 1,040.', 'Decoder 16 &times; 64 + 64 = 1,088.', eq('1,040 + 1,088 = 2,128')], check=2128)
K.calc('h', '&beta; VAE with reconstruction 20, KL 3 and &beta; = 4. Loss?', '32', 'reconstruction + &beta; KL.', ['&beta; KL = 4 &times; 3 = 12.', 'Add the reconstruction.', eq('20 + 12 = 32')], check=32)
K.calc('x', 'In the style of a Stanford CS236 problem: a 2 dimensional code with &mu; = (1, 0) and &sigma; = (1, 0.5). Total KL to N(0, I)?', '0.8181', 'Sum the KL of each dimension.', ['Dimension 1: &frac12;(1 + 1 &minus; 1 &minus; 0) = 0.5.', 'Dimension 2: 0.3181 from the earlier problem.', eq('0.5 + 0.3181 = 0.8181')], check=0.8181, tol=0.0005)

K.assign('reparameterize', 'e', 'The reparameterisation step',
         '<p>Write <code>reparameterize(mu, logvar, eps)</code> that returns z = mu + exp(0.5 &times; logvar) &times; eps, rounded to 4 decimals.</p>',
         """
def reparameterize(mu, logvar, eps):
    # your code here
    pass
""", [('reparameterize(1.0, 0.0, 2.0)', 3.0), ('reparameterize(0.0, -2.0, 1.0)', 0.3679), ('reparameterize(-1.0, 0.0, -1.0)', -2.0)],
         """
import math


def reparameterize(mu, logvar, eps):
    return round(mu + math.exp(0.5 * logvar) * eps, 4)
""", 'Turn the log variance into a standard deviation with exp(0.5 &times; logvar), multiply by eps and add mu.', '<p>In a real VAE, eps is drawn fresh from N(0, 1) for every example at every step. Passing it in makes the function easy to test.</p>')
K.assign('kl_gaussian', 'm', 'The Gaussian KL term',
         '<p>Write <code>kl_gaussian(mus, sigmas)</code> that returns the KL divergence from N(mu, sigma&sup2;) to N(0, 1), summed over all dimensions, rounded to 4 decimals.</p>',
         """
def kl_gaussian(mus, sigmas):
    # your code here
    pass
""", [('kl_gaussian([0.0], [1.0])', 0.0), ('kl_gaussian([1.0], [1.0])', 0.5), ('kl_gaussian([1.0, 0.0], [1.0, 0.5])', 0.8181)],
         """
import math


def kl_gaussian(mus, sigmas):
    total = 0.0
    for m, s in zip(mus, sigmas):
        total += 0.5 * (m * m + s * s - 1 - math.log(s * s))
    return round(total, 4)
""", 'Apply &frac12;(&mu;&sup2; + &sigma;&sup2; &minus; 1 &minus; ln &sigma;&sup2;) to each dimension and add them up.', '<p>The dimensions are independent under both distributions, which is why their KL values simply add.</p>')
K.assign('reconstruction_mse', 'm', 'Reconstruction error',
         '<p>Write <code>reconstruction_mse(x, x_hat)</code> that returns the mean squared difference between the input list and its reconstruction, rounded to 4 decimals.</p>',
         """
def reconstruction_mse(x, x_hat):
    # your code here
    pass
""", [('reconstruction_mse([1.0, 0.0, 1.0], [0.8, 0.2, 1.0])', 0.0267), ('reconstruction_mse([0.5], [0.5])', 0.0)],
         """
def reconstruction_mse(x, x_hat):
    return round(sum((a - b) ** 2 for a, b in zip(x, x_hat)) / len(x) + 0.0, 4)
""", 'Square each difference, average them, and round.', '<p>For anomaly detection, this number is the score: compare it with a threshold set from normal data.</p>')

K.must('Autoencoder', 'Encoder to a small code, decoder back. Train on reconstruction error, no labels.')
K.must('Versus PCA', 'Linear autoencoder = PCA subspace. Nonlinear layers rebuild curved data better.')
K.must('Uses', 'Denoising (noisy in, clean out). Anomalies: train on normal data, flag high reconstruction error.')
K.must('VAE', 'Encoder gives &mu;, log &sigma;&sup2;. z = &mu; + &sigma;&epsilon;. Loss = reconstruction + KL = negative ELBO.')
K.must('KL', '&frac12;&Sigma;(&mu;&sup2; + &sigma;&sup2; &minus; 1 &minus; ln &sigma;&sup2;), zero only for N(0, 1). &beta; weights it.')
K.must('Discrete and latent', 'VQ-VAE: nearest codebook index, log<sub>2</sub>(size) bits. Latent spaces make diffusion cheap.')

T = K.topic(
    slug='ml-autoencoders', topic='ml-autoencoders', step=(3, 'Generative models', 'ml-d3', 'Networks that create new data: autoencoders and variational autoencoders, generative adversarial networks, and diffusion models.', 'Advanced'),
    title='Autoencoders and variational autoencoders', short='Autoencoders and VAEs', badge='3.1', minutes=55,
    lead='Learn compact codes without labels: autoencoders against PCA, denoising and anomaly detection, variational autoencoders with the reparameterisation trick and the ELBO, and discrete codes behind modern generators.',
    desc='autoencoder, encoder, decoder, latent code, bottleneck, reconstruction error, PCA, denoising autoencoder, anomaly detection, variational autoencoder, VAE, reparameterisation trick, KL divergence, ELBO, prior, beta VAE, posterior collapse, VQ-VAE, codebook, latent space.',
    summary='Autoencoders, denoising and anomaly detection, VAEs with the ELBO, and discrete latent codes.',
    keywords=['autoencoder', 'VAE', 'variational autoencoder', 'reparameterisation', 'KL divergence', 'ELBO', 'anomaly detection', 'denoising', 'latent space', 'VQ-VAE'],
    recap='<p>Squeeze data through a small code and rebuild it, and the code learns what matters. Make the code a distribution kept close to N(0, I), and the decoder becomes a generator of new data.</p>',
    added='2026-11-14', leet=leet_items())
