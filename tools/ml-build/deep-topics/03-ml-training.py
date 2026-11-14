# Deep learning 1.3: training deep networks. Checked against Goodfellow, Bengio and Courville, Deep Learning (MIT Press
# 2016) chapters 7 and 8, Polyak (1964, momentum), Hinton's Coursera lecture 6 (RMSprop), Kingma and Ba, Adam (ICLR
# 2015), Loshchilov and Hutter, SGDR (ICLR 2017) and AdamW (ICLR 2019), Ioffe and Szegedy, Batch normalization (ICML
# 2015), Ba, Kiros and Hinton, Layer normalization (2016), Srivastava and colleagues, Dropout (JMLR 2014), Goyal and
# colleagues, Accurate, large minibatch SGD (2017), and Karpathy's "A recipe for training neural networks" (2019).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-training')
K = Kit()

K.code('optimizers', r'''
# Four optimisers on a long, narrow valley: f(x, y) = 0.5 * (x**2 + K * y**2) with K = 100.
# The minimum is at (0, 0). The valley is 100 times more curved across y than along x.
import numpy as np

K = 100


def grad(p):
    return np.array([p[0], K * p[1]])


def loss(p):
    return 0.5 * (p[0] ** 2 + K * p[1] ** 2)


def run(name, lr, steps=60):
    p = np.array([-4.0, 1.5])
    v = np.zeros(2)          # momentum, or the first moment in Adam
    s = np.zeros(2)          # running average of squared gradients
    for t in range(1, steps + 1):
        g = grad(p)
        if name == 'SGD':
            p = p - lr * g
        elif name == 'Momentum':
            v = 0.9 * v + g
            p = p - lr * v
        elif name == 'RMSprop':
            s = 0.9 * s + 0.1 * g * g
            p = p - lr * g / (np.sqrt(s) + 1e-8)
        elif name == 'Adam':
            v = 0.9 * v + 0.1 * g
            s = 0.999 * s + 0.001 * g * g
            v_hat = v / (1 - 0.9 ** t)
            s_hat = s / (1 - 0.999 ** t)
            p = p - lr * v_hat / (np.sqrt(s_hat) + 1e-8)
    return loss(p)


settings = [('SGD', 0.019), ('Momentum', 0.01), ('RMSprop', 0.1), ('Adam', 0.1)]
print('loss after 60 steps, starting from', loss(np.array([-4.0, 1.5])))
for name, lr in settings:
    print(f'  {name:8s} lr {lr:<5} {run(name, lr):.6f}')

print('plain SGD: it is stable only while lr < 2 / K = 0.02')
for lr in [0.01, 0.019, 0.021, 0.03]:
    print(f'  lr {lr:<6} loss {run("SGD", lr):.4g}')
''', long=True)

K.code('schedules', r'''
# Mini-batch SGD on a noisy linear regression: batch size and learning rate schedules.
import math
import numpy as np

rng = np.random.default_rng(0)
n, d = 1000, 5
X = rng.normal(size=(n, d))
true_w = np.array([2.0, -1.0, 0.5, 3.0, -2.0])
y = X @ true_w + rng.normal(scale=1.0, size=n)
best = np.linalg.lstsq(X, y, rcond=None)[0]
best_loss = np.mean((X @ best - y) ** 2) / 2


def train(batch, epochs, schedule, lr0=0.1, seed=1):
    r = np.random.default_rng(seed)
    w = np.zeros(d)
    steps_per_epoch = n // batch
    total = epochs * steps_per_epoch
    t = 0
    for epoch in range(epochs):
        order = r.permutation(n)
        for k in range(steps_per_epoch):
            idx = order[k * batch:(k + 1) * batch]
            g = X[idx].T @ (X[idx] @ w - y[idx]) / batch
            lr = schedule(lr0, t, total)
            w -= lr * g
            t += 1
    return np.mean((X @ w - y) ** 2) / 2 - best_loss, t


def constant(lr0, t, total):
    return lr0


def step_decay(lr0, t, total):
    return lr0 * 0.1 ** (3 * t // total)          # divide by 10 at 1/3 and 2/3


def cosine(lr0, t, total):
    return 0.5 * lr0 * (1 + math.cos(math.pi * t / total))


def warmup_cosine(lr0, t, total, warm=50):
    if t < warm:
        return lr0 * (t + 1) / warm
    return cosine(lr0, t - warm, total - warm)


print(f'best possible loss {best_loss:.4f}')
print('extra loss above the best, batch 8, 6 epochs')
for name, sch in [('constant', constant), ('step decay', step_decay), ('cosine', cosine), ('warmup + cosine', warmup_cosine)]:
    gap, t = train(8, 6, sch)
    print(f'  {name:16s} {gap:.5f}')

print('batch size, constant lr 0.1, 6 epochs')
for batch in [1, 8, 64, 1000]:
    gap, t = train(batch, 6, constant)
    print(f'  batch {batch:4d}: {t:5d} updates, extra loss {gap:.5f}')
''', long=True)

K.code('batchnorm', r'''
# Batch normalisation and dropout, written by hand with numpy.
import numpy as np

rng = np.random.default_rng(0)


def batchnorm(h, gamma, beta, eps=1e-5):
    mean = h.mean(axis=0)
    var = h.var(axis=0)
    return gamma * (h - mean) / np.sqrt(var + eps) + beta


# 1. A deep tanh network with weights that are a little too small
X = rng.normal(size=(256, 100))
for use_bn in [False, True]:
    h = X
    stds = []
    for layer in range(10):
        W = rng.normal(scale=0.5 / np.sqrt(100), size=(100, 100))
        z = h @ W
        if use_bn:
            z = batchnorm(z, np.ones(100), np.zeros(100))
        h = np.tanh(z)
        stds.append(h.std())
    label = 'with batch norm   ' if use_bn else 'without batch norm'
    print(label, 'activation std at layers 1, 5, 10:', [round(float(stds[i]), 4) for i in (0, 4, 9)])

# 2. Batch norm output: each feature has mean 0 and std 1 before gamma and beta
z = rng.normal(loc=5.0, scale=3.0, size=(64, 3))
out = batchnorm(z, np.array([1.0, 2.0, 1.0]), np.array([0.0, 0.0, 10.0]))
print('feature means after batch norm:', np.round(out.mean(axis=0), 3) + 0.0)
print('feature stds after batch norm: ', np.round(out.std(axis=0), 3))

# 3. Inverted dropout keeps the expected activation the same
a = np.ones(100000)
p_keep = 0.8
mask = rng.random(a.shape) < p_keep
dropped = a * mask / p_keep
print(f'kept fraction {mask.mean():.3f}, mean before {a.mean():.3f}, mean after {dropped.mean():.3f}')
print('at test time dropout is switched off and nothing is rescaled')
''', long=True)

K.code('regularize', r'''
# Overfitting and four cures: weight decay, dropout and early stopping on a tiny regression.
import numpy as np

rng = np.random.default_rng(3)
x_train = np.sort(rng.uniform(-3, 3, 16)).reshape(-1, 1)
y_train = np.sin(x_train) + rng.normal(scale=0.3, size=x_train.shape)
x_val = np.linspace(-3, 3, 200).reshape(-1, 1)
y_val = np.sin(x_val) + rng.normal(scale=0.3, size=x_val.shape)


def train(decay=0.0, keep=1.0, patience=None, epochs=3000, lr=0.01, seed=0):
    r = np.random.default_rng(seed)
    sizes = [1, 64, 64, 1]
    W = [r.normal(scale=np.sqrt(1 / a), size=(a, b)) for a, b in zip(sizes, sizes[1:])]
    b = [np.zeros(s) for s in sizes[1:]]
    m = [np.zeros_like(p) for p in W + b]
    v = [np.zeros_like(p) for p in W + b]

    def forward(x, train_mode):
        hs, raw, masks = [x], [], []
        for i in range(2):
            h = np.tanh(hs[-1] @ W[i] + b[i])
            mask = (r.random(h.shape) < keep) / keep if train_mode else 1.0
            raw.append(h)
            masks.append(mask)
            hs.append(h * mask)
        return hs, raw, masks, hs[-1] @ W[2] + b[2]

    best, best_epoch, best_params = np.inf, 0, None
    for t in range(1, epochs + 1):
        hs, raw, masks, out = forward(x_train, True)
        g = 2 * (out - y_train) / len(x_train)
        grads_W, grads_b = [None] * 3, [None] * 3
        for i in (2, 1, 0):
            grads_W[i] = hs[i].T @ g + decay * W[i]
            grads_b[i] = g.sum(axis=0)
            if i > 0:
                g = (g @ W[i].T) * masks[i - 1] * (1 - raw[i - 1] ** 2)
        for j, (p, gr) in enumerate(zip(W + b, grads_W + grads_b)):
            m[j] = 0.9 * m[j] + 0.1 * gr
            v[j] = 0.999 * v[j] + 0.001 * gr * gr
            p -= lr * (m[j] / (1 - 0.9 ** t)) / (np.sqrt(v[j] / (1 - 0.999 ** t)) + 1e-8)
        if patience:
            val = np.mean((forward(x_val, False)[3] - y_val) ** 2)
            if val < best:
                best, best_epoch, best_params = val, t, ([w.copy() for w in W], [c.copy() for c in b])
            elif t - best_epoch >= patience:
                W[:], b[:] = best_params
                break
    train_mse = np.mean((forward(x_train, False)[3] - y_train) ** 2)
    val_mse = np.mean((forward(x_val, False)[3] - y_val) ** 2)
    return train_mse, val_mse, t


print('                  train MSE   validation MSE')
for name, kw in [('no regularisation', {}), ('weight decay', {'decay': 0.01}), ('dropout keep 0.8', {'keep': 0.8}), ('early stopping', {'patience': 200})]:
    tr, va, t = train(**kw)
    extra = f'   (stopped at epoch {t})' if 'patience' in kw else ''
    print(f'  {name:17s} {tr:.4f}      {va:.4f}{extra}')
''', long=True)

K.lesson('idea', 'Optimisers: SGD, momentum, RMSprop and Adam', f'''
{src('Goodfellow, Bengio and Courville (2016) sections 8.3 and 8.5, Polyak (1964), Hinton’s Coursera lecture 6e, and Kingma and Ba, Adam (ICLR 2015).')}
{viz('mloptim')}
{wwh('An <b>optimiser</b> is the rule that turns gradients into weight updates. Plain <b>stochastic gradient descent</b> (SGD) steps against the gradient of a mini batch. <b>Momentum</b> keeps a running velocity so steps build up along consistent directions. <b>RMSprop</b> divides each weight’s step by a running size of its own gradients. <b>Adam</b> combines momentum with RMSprop scaling and corrects both averages for their start at zero.',
     'Real loss surfaces have long, narrow valleys: some directions are far more curved than others. Plain SGD must keep its learning rate below the limit set by the steepest direction, so it crawls along the shallow ones. Momentum and adaptive scaling make progress in every direction at once, which often means training in fewer steps and with less tuning.',
     'Start with Adam (learning rate about 0.001) or AdamW for most networks, because it is forgiving. For large vision models, SGD with momentum 0.9 and a good schedule often generalises a little better. Whatever you pick, the learning rate is still the most important setting to tune.')}
{run('optimizers')}
{note('On the valley f = &frac12;(x&sup2; + 100y&sup2;), plain SGD is stable only below learning rate 2/100 = 0.02. At its best safe rate 0.019 it reaches a loss of 0.80 after 60 steps, and at 0.021 it explodes to about 10 million. Momentum reaches 0.105 with a rate of only 0.01, Adam reaches 0.103 and RMSprop reaches 0.00005. RMSprop wins so clearly here because this valley lines up with the axes, so scaling each coordinate separately fixes the problem completely. A tilted valley would be harder for it.', 'exam')}
{fxs(fx('SGD', '&theta; &larr; &theta; &minus; &eta; g', 'g is the mini batch gradient.', key=True),
     fx('Momentum', 'v &larr; &beta;v + g, &nbsp; &theta; &larr; &theta; &minus; &eta;v', '&beta; about 0.9.', key=True),
     fx('RMSprop', 's &larr; &rho;s + (1 &minus; &rho;)g&sup2;, &nbsp; &theta; &larr; &theta; &minus; &eta;g / (&radic;s + &epsilon;)', 'Per weight step size.', key=True),
     fx('Adam', 'm &larr; &beta;<sub>1</sub>m + (1 &minus; &beta;<sub>1</sub>)g, &nbsp; v &larr; &beta;<sub>2</sub>v + (1 &minus; &beta;<sub>2</sub>)g&sup2;', '&beta;<sub>1</sub> = 0.9, &beta;<sub>2</sub> = 0.999.', key=True),
     fx('Adam update', 'm&#770; = m/(1 &minus; &beta;<sub>1</sub><sup>t</sup>), &nbsp; v&#770; = v/(1 &minus; &beta;<sub>2</sub><sup>t</sup>), &nbsp; &theta; &larr; &theta; &minus; &eta;m&#770;/(&radic;v&#770; + &epsilon;)', 'Bias correction for the zero start.', key=True))}
{link('ml-maths', 'Need a refresher on gradient descent and curvature?', 'The Maths for Machine Learning subject explains gradients, the Hessian and why curvature limits the learning rate.', 'Open Maths for Machine Learning')}
''', kw=['optimiser', 'SGD', 'momentum', 'RMSprop', 'Adam', 'AdamW', 'learning rate', 'ill conditioning'])

K.lesson('schedules', 'Mini batches and learning rate schedules', f'''
{src('Goodfellow, Bengio and Courville (2016) section 8.1.3, Loshchilov and Hutter, SGDR (ICLR 2017), Goyal and colleagues, Accurate, large minibatch SGD (2017), and Smith, Cyclical learning rates (WACV 2017).')}
{wwh('A <b>mini batch</b> is the small group of examples used for one gradient step. One pass over all the data is an <b>epoch</b>. A <b>learning rate schedule</b> changes the learning rate during training: <b>step decay</b> divides it by 10 at set points, <b>cosine decay</b> lowers it smoothly to 0, and <b>warm up</b> raises it gently over the first few hundred steps.',
     'A mini batch gradient is a noisy estimate of the full gradient. A large learning rate makes fast early progress but the noise keeps the weights bouncing around the minimum. Lowering the rate later lets them settle. Warm up protects the first steps, when the weights are random and Adam’s averages are still unreliable.',
     'Choose the largest batch that fits in memory and gives good results, often 32 to 512. When you multiply the batch size by k, multiply the learning rate by about k too (the <b>linear scaling rule</b>), with warm up. Use cosine decay with a short warm up as a strong default.')}
{run('schedules')}
{note('Mini batch SGD with batch 8 on a noisy linear regression ends 0.0167 above the best possible loss with a constant learning rate. Step decay, cosine decay and warm up with cosine all end about 0.0002 above it, roughly 80 times closer, with the same number of steps. For batch size, batch 1 makes 6,000 noisy updates and ends 0.177 above the best, batch 64 makes 90 updates and ends 0.0007 above, and the full batch makes only 6 updates in 6 epochs and is still 2.56 above.', 'exam')}
{table(['Batch size', 'Gradient noise', 'Updates per epoch', 'Typical effect'], [
    ['1 (pure SGD)', 'Very high', 'n', 'Slow on hardware, noisy, needs a small rate'],
    ['32 to 512', 'Moderate', 'n / batch', 'Good default, noise helps generalisation'],
    ['Thousands', 'Low', 'Few', 'Fast per epoch on GPUs, needs larger rate and warm up'],
    ['Full batch', 'None', '1', 'Plain gradient descent, many epochs needed']])}
{fxs(fx('Step decay', '&eta;<sub>t</sub> = &eta;<sub>0</sub> &middot; &gamma;<sup>&lfloor;t/s&rfloor;</sup>', 'For example &gamma; = 0.1 every s epochs.', key=True),
     fx('Cosine decay', '&eta;<sub>t</sub> = &frac12;&eta;<sub>0</sub>(1 + cos(&pi;t/T))', 'Smooth from &eta;<sub>0</sub> to 0.', key=True),
     fx('Linear warm up', '&eta;<sub>t</sub> = &eta;<sub>0</sub> &middot; (t + 1)/w for t &lt; w', 'Then the main schedule.', key=True),
     fx('Linear scaling rule', 'batch &times; k &rArr; &eta; &times; k', 'Goyal and colleagues (2017).'))}
''', kw=['mini batch', 'epoch', 'batch size', 'learning rate schedule', 'step decay', 'cosine decay', 'warm up', 'linear scaling rule'])

K.lesson('normalise', 'Batch normalisation and layer normalisation', f'''
{src('Ioffe and Szegedy, Batch normalization (ICML 2015), Ba, Kiros and Hinton, Layer normalization (2016), and Santurkar and colleagues, How does batch normalization help optimization? (NeurIPS 2018).')}
{wwh('<b>Batch normalisation</b> (BN) takes each feature of a layer over the current mini batch, subtracts its mean and divides by its standard deviation, then applies a learned scale &gamma; and shift &beta;. At test time it uses running averages collected during training. <b>Layer normalisation</b> (LN) does the same across the features of one example instead of across the batch.',
     'Normalisation keeps the signal in each layer at a steady size whatever the weights do, so deep networks train faster, tolerate larger learning rates and depend less on careful initialisation. BN is standard in convolutional networks. LN is standard in transformers and recurrent networks, because it works with any batch size and with sequences.',
     'Place the normalisation layer just before or just after the activation, following the architecture you copy. Remember to switch the model to evaluation mode (model.eval() in PyTorch) at test time, otherwise BN uses the statistics of the test batch.')}
{run('batchnorm')}
{note('In a 10 layer tanh network with weights a little too small, the activation spread falls from 0.415 at layer 1 to 0.0007 at layer 10. With batch normalisation before each tanh, it stays at about 0.63 in every layer. After BN with &gamma; = 1 and &beta; = 0 each feature has mean 0 and standard deviation 1, and &gamma; = 2 or &beta; = 10 rescale or shift it exactly as asked.', 'exam')}
{table(['', 'Batch norm', 'Layer norm'], [
    ['Statistics over', 'The batch, per feature', 'The features, per example'],
    ['Depends on batch size', 'Yes, poor with tiny batches', 'No'],
    ['Train and test differ', 'Yes, running averages at test', 'No'],
    ['Typical home', 'CNNs', 'Transformers, RNNs']])}
{fxs(fx('Batch norm', 'x&#770; = (x &minus; &mu;<sub>B</sub>) / &radic;(&sigma;<sub>B</sub>&sup2; + &epsilon;), &nbsp; y = &gamma;x&#770; + &beta;', 'Per feature over the batch.', key=True),
     fx('Running mean', '&mu; &larr; 0.9&mu; + 0.1&mu;<sub>B</sub>', 'Used at test time.', key=True),
     fx('Layer norm', 'Same formula with &mu; and &sigma; over one example’s features', 'No batch dependence.', key=True))}
''', kw=['batch normalisation', 'layer normalisation', 'gamma beta', 'running mean', 'internal covariate shift', 'eval mode'])

K.lesson('regular', 'Regularisation: weight decay, dropout and early stopping', f'''
{src('Goodfellow, Bengio and Courville (2016) chapter 7, Srivastava and colleagues, Dropout (JMLR 2014), Loshchilov and Hutter, Decoupled weight decay regularization (ICLR 2019), and Prechelt, Early stopping, but when? (1998).')}
{viz('mlfitreg')}
{wwh('<b>Regularisation</b> is anything that stops a model fitting the noise in its training data. <b>Weight decay</b> (L2) pulls every weight a little towards zero each step. <b>Dropout</b> switches off each hidden unit at random during training, with probability 1 &minus; keep, so no unit can rely on another. <b>Early stopping</b> watches the validation error and keeps the weights from the epoch where it was lowest.',
     'Neural networks have far more weights than training examples, so they can memorise the training set. Then training error keeps falling while validation error rises: <b>overfitting</b>. Regularisation trades a little training error for a model that does better on new data.',
     'Use weight decay almost always (AdamW with about 0.01 to 0.1). Add dropout of 0.1 to 0.5 in large fully connected layers or transformers. Always keep a validation set and save the best checkpoint, which gives early stopping for free. More data and data augmentation are the strongest regularisers of all.')}
{run('regularize')}
{note('A network with two layers of 64 tanh units, trained on 16 noisy points of sin(x), reaches a training error of 0.0026 but a validation error of 0.596. Weight decay 0.01 gives a validation error of 0.111, dropout with keep 0.8 gives 0.132, and early stopping halts at epoch 447 with 0.118. The noise alone gives about 0.09, so these are close to the best possible.', 'exam')}
{fxs(fx('L2 penalty', 'L&prime; = L + (&lambda;/2)||<b>w</b>||&sup2;', 'Adds &lambda;<b>w</b> to the gradient.', key=True),
     fx('Weight decay step', '<b>w</b> &larr; <b>w</b>(1 &minus; &eta;&lambda;) &minus; &eta;g', 'Same as L2 for plain SGD, not for Adam.', key=True),
     fx('Inverted dropout', 'h&#771; = h &middot; m / p, m ~ Bernoulli(p)', 'Keeps the expected value. No change at test time.', key=True),
     fx('Early stopping', 'keep &theta; at argmin<sub>epoch</sub> validation loss', 'Patience: how long to wait for improvement.'))}
''', kw=['regularisation', 'overfitting', 'weight decay', 'L2', 'AdamW', 'dropout', 'early stopping', 'validation set'])

K.lesson('recipe', 'A practical recipe for training a network', f'''
{src('Karpathy, A recipe for training neural networks (2019), Smith, A disciplined approach to neural network hyper parameters (2018), and Google’s Deep learning tuning playbook (2023).')}
{wwh('Training a network well is mostly a careful process, not one clever trick. The recipe is: look at the data, get a simple baseline working end to end, make the model overfit a small sample, then regularise and tune.',
     'Neural network bugs rarely crash. A wrong label shuffle, a missing model.eval() or a learning rate ten times too large just gives a model that is quietly worse. Checking each stage separately finds these silent failures early.',
     'Follow the steps in the table in order and change one thing at a time. Plot training and validation loss for every run, and keep a log of each setting you tried.')}
{table(['Step', 'What to do', 'What it catches'], [
    ['1. Check the loss at start', 'With C classes the first loss should be about ln C', 'Wrong labels, bad initialisation'],
    ['2. Overfit one batch', 'Training loss on 2 to 10 examples should reach almost 0', 'Bugs in the model or the loss'],
    ['3. Find the learning rate', 'Raise it over a short run and pick a value below where loss explodes', 'Rates that are too small or too large'],
    ['4. Train the full model', 'Adam or SGD with momentum, cosine schedule, warm up', 'Underfitting'],
    ['5. Regularise', 'Weight decay, dropout, augmentation, early stopping', 'Overfitting'],
    ['6. Tune', 'Random search over rate, decay and batch size', 'Leftover performance']])}
{scene('Debugging a network that will not learn', 'A student’s image classifier for 10 classes stays at 10% accuracy. The first loss is 2.30, which matches ln 10, so the start is fine. Trying to overfit 8 images fails too, which points to a bug rather than a hard problem. The student finds that the images were normalised but the labels were shuffled separately. After fixing it, the 8 images reach a loss near 0 within 100 steps, and the full model trains normally.')}
''', kw=['training recipe', 'overfit one batch', 'learning rate finder', 'baseline', 'debugging neural networks', 'tuning'])

K.lesson('versus', 'Optimisers compared', f'''
{versus('Choosing an optimiser', ['', 'SGD', 'SGD with momentum', 'RMSprop', 'Adam or AdamW'], [
    ['Extra memory per weight', 'None', '1 value', '1 value', '2 values'],
    ['Sensitive to the learning rate', 'Very', 'Quite', 'Less', 'Least'],
    ['Handles narrow valleys', 'Poorly', 'Better', 'Well when aligned with axes', 'Well'],
    ['Typical learning rate', '0.01 to 0.1', '0.01 to 0.1', '0.001', '0.001 (3e&minus;4 is common)'],
    ['Common use', 'Teaching, simple convex models', 'Large CNNs on images', 'RNNs, reinforcement learning', 'Transformers, most new models']],
    'start with AdamW. Try SGD with momentum and a schedule if you train a large vision model and have time to tune.')}
''', kw=['SGD vs Adam', 'optimiser comparison', 'AdamW'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Stability limit for gradient descent', '&eta; &lt; 2 / &lambda;<sub>max</sub>', '&lambda;<sub>max</sub> is the largest curvature (Hessian eigenvalue).', key=True),
     fx('Condition number', '&kappa; = &lambda;<sub>max</sub> / &lambda;<sub>min</sub>', 'Large &kappa; means a narrow valley and slow SGD.', key=True),
     fx('Momentum terminal speed', 'v &rarr; g / (1 &minus; &beta;)', '&beta; = 0.9 gives steps 10 times larger on a steady slope.', key=True),
     fx('Adam bias correction', 'E[m<sub>t</sub>] &asymp; (1 &minus; &beta;<sub>1</sub><sup>t</sup>) E[g]', 'Divide by 1 &minus; &beta;<sup>t</sup> to undo it.', key=True),
     fx('Gradient noise', 'Var(g<sub>B</sub>) &asymp; Var(g<sub>1</sub>) / B', 'Bigger batches give cleaner gradients.'),
     fx('AdamW', '&theta; &larr; &theta; &minus; &eta;(m&#770;/(&radic;v&#770; + &epsilon;) + &lambda;&theta;)', 'Decay outside the adaptive scaling.'))}
{steps('Worked example: why plain SGD has a speed limit on f = &frac12;(x&sup2; + 100y&sup2;)', [
    'The gradient is (x, 100y), so one SGD step multiplies x by (1 &minus; &eta;) and y by (1 &minus; 100&eta;).',
    eq('y<sub>t</sub> = (1 &minus; 100&eta;)<sup>t</sup> y<sub>0</sub>'),
    'This shrinks only if |1 &minus; 100&eta;| &lt; 1, that is &eta; &lt; 2/100 = 0.02.',
    eq('&eta; = 0.019: &nbsp; x<sub>t</sub> = 0.981<sup>t</sup> x<sub>0</sub>, &nbsp; 0.981<sup>60</sup> &asymp; 0.316'),
    'So after 60 steps x is still about a third of its start, and the loss &frac12;(4 &times; 0.316)&sup2; &asymp; 0.80 matches the program. The steep direction limits the rate and the shallow direction pays for it.'])}
{deep('Sharp and flat minima, and why the noise of small batches can help', '<p>Many different weight settings give near zero training loss in a large network. Some sit in narrow, sharp valleys and some in wide, flat ones. Keskar and colleagues (ICLR 2017) found that very large batches tend to end in sharper minima that generalise worse, and that the noise of small batch SGD helps find flatter ones. The ratio of learning rate to batch size acts like a temperature for this noise, which is one reason behind the linear scaling rule. Methods such as sharpness aware minimisation (Foret and colleagues, ICLR 2021) seek flat minima on purpose by minimising the worst loss in a small ball around the weights. Second order methods that use curvature directly, such as K FAC and Shampoo, can cut the number of steps further but cost more per step.</p>')}
''', kw=['learning rate limit', 'condition number', 'momentum maths', 'bias correction', 'sharp minima', 'flat minima'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Training a network means repeating small corrections. The optimiser decides how big each correction is, and regularisation stops the network from memorising the examples instead of learning the pattern.</p>',
    '<p>Implement SGD, momentum and Adam, use mini batches with a learning rate schedule, add batch normalisation, and compare weight decay, dropout and early stopping on validation data.</p>',
    '<p>Derive the stability limit and bias correction, explain BN against LN, apply the linear scaling rule with warm up, and run a disciplined training and tuning recipe.</p>',
    '<p>Study the theory of adaptive methods and their convergence, sharpness and generalisation, normalisation free networks, second order optimisers and large scale training dynamics.</p>')}
{grow('Explain what an optimiser and regularisation do.',
      'Train and tune a deep network reliably.',
      'Analyse optimisation and generalisation in deep learning.')}
''', kw=['beginner', 'expert', 'training dynamics'])

lc(2574, 'Left and Right Sum Differences', 'left-and-right-sum-differences', 'e', 'Keep a running sum from the left and get the right sum from the total', 'Walk once from left to right. The right sum is the total minus the left sum minus the current value. Keeping one running total instead of recomputing everything is how momentum and Adam store their averages.', r"""
def left_right_difference(nums):
    total, left, out = sum(nums), 0, []
    for v in nums:
        right = total - left - v
        out.append(abs(left - right))
        left += v
    return out
""", [('left_right_difference([10, 4, 8, 3])', [15, 1, 11, 22]), ('left_right_difference([1])', [0])])
lc(1870, 'Minimum Speed to Arrive on Time', 'minimum-speed-to-arrive-on-time', 'm', 'Binary search for the smallest speed that is fast enough', 'Being on time only gets easier as the speed rises, so binary search on the answer. Every train but the last waits for the next whole hour. Searching for the largest safe value of a setting is how a learning rate range test works.', r"""
import math


def min_speed_on_time(dist, hour):
    def time_at(speed):
        t = sum(math.ceil(d / speed) for d in dist[:-1])
        return t + dist[-1] / speed

    lo, hi = 1, 10 ** 7
    if time_at(hi) > hour:
        return -1
    while lo < hi:
        mid = (lo + hi) // 2
        if time_at(mid) <= hour:
            hi = mid
        else:
            lo = mid + 1
    return lo
""", [('min_speed_on_time([1, 3, 2], 6)', 1), ('min_speed_on_time([1, 3, 2], 2.7)', 3), ('min_speed_on_time([1, 3, 2], 1.9)', -1)])
lc(2064, 'Minimized Maximum of Products Distributed to Any Store', 'minimized-maximum-of-products-distributed-to-any-store', 'm', 'Binary search the largest load and count the stores it needs', 'For a candidate maximum x, product q needs ceil(q / x) stores. Find the smallest x whose total fits in n stores. Splitting work into equal pieces is the same arithmetic as choosing a batch size.', r"""
import math


def minimized_maximum(n, quantities):
    lo, hi = 1, max(quantities)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(math.ceil(q / mid) for q in quantities) <= n:
            hi = mid
        else:
            lo = mid + 1
    return lo
""", [('minimized_maximum(6, [11, 6])', 3), ('minimized_maximum(7, [15, 10, 10])', 5), ('minimized_maximum(1, [100000])', 100000)])
lc(1552, 'Magnetic Force Between Two Balls', 'magnetic-force-between-two-balls', 'm', 'Binary search the gap and place balls greedily', 'Sort the positions. For a candidate gap, place a ball whenever the distance from the last one is big enough, and check whether m balls fit. Keep the largest gap that works.', r"""
def max_distance(position, m):
    position = sorted(position)

    def fits(gap):
        count, last = 1, position[0]
        for p in position[1:]:
            if p - last >= gap:
                count, last = count + 1, p
        return count >= m

    lo, hi = 1, position[-1] - position[0]
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if fits(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
""", [('max_distance([1, 2, 3, 4, 7], 3)', 3), ('max_distance([5, 4, 3, 2, 1, 1000000000], 2)', 999999999)])
lc(410, 'Split Array Largest Sum', 'split-array-largest-sum', 'h', 'Binary search the largest piece sum and split greedily', 'For a limit, cut a new piece whenever adding the next number would pass it, and count the pieces. The smallest limit that needs at most k pieces is the answer. This is how data and pipeline parallel training balance work across devices.', r"""
def split_array(nums, k):
    def pieces(limit):
        count, current = 1, 0
        for v in nums:
            if current + v > limit:
                count, current = count + 1, 0
            current += v
        return count

    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if pieces(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
""", [('split_array([7, 2, 5, 10, 8], 2)', 18), ('split_array([1, 2, 3, 4, 5], 2)', 9), ('split_array([1, 4, 4], 3)', 4)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Training uses running averages and searches for good settings such as the learning rate and batch size. These problems practise a running sum and binary search on the answer, from a speed limit to splitting work into balanced pieces. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'binary search on the answer', 'prefix sum', 'greedy'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'SGD is limited by the steepest direction: &eta; &lt; 2/&lambda;<sub>max</sub>. <b>Momentum</b> builds speed on steady slopes, <b>RMSprop</b> scales each weight’s step, and <b>Adam</b> does both with bias correction.',
    'Mini batches give noisy gradients. A <b>schedule</b> (cosine or step decay with <b>warm up</b>) starts fast and settles at the end. Scale the learning rate with the batch size.',
    '<b>Batch norm</b> normalises each feature over the batch and uses running averages at test time. <b>Layer norm</b> normalises each example and suits transformers.',
    '<b>Weight decay</b>, <b>dropout</b> and <b>early stopping</b> fight overfitting. Use AdamW for decoupled decay and inverted dropout so test time needs no change.',
    'Follow a recipe: check the first loss, overfit one batch, find the learning rate, then regularise and tune one thing at a time.'],
    'Deep learning 2.1 starts the architectures with convolutional neural networks for images.')}
{files('Three tasks: a momentum update, an Adam step, and a batch normalisation forward pass.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'An optimiser in deep learning', ['Chooses the network architecture', 'Turns gradients into weight updates', 'Cleans the data', 'Computes the gradients'], 1, 'The update rule.', 'Backpropagation computes the gradients, the optimiser uses them.')
K.quiz('e', 'Momentum helps because', ['It removes the need for gradients', 'It builds up speed along directions where the gradient keeps pointing the same way', 'It makes every step smaller', 'It shuffles the data'], 1, 'A running velocity.', 'Zigzags cancel, steady directions add up.')
K.quiz('e', 'Dropout during training', ['Deletes training examples', 'Switches off random hidden units each step', 'Lowers the learning rate', 'Removes layers permanently'], 1, 'Random units off.', 'At test time all units are used.')
K.quiz('e', 'Early stopping keeps the weights from', ['The last epoch', 'The epoch with the lowest validation error', 'The first epoch', 'The epoch with the lowest training error'], 1, 'Watch validation.', 'Training error usually keeps falling.')
K.quiz('m', 'Adam divides each step by &radic;v&#770; so that', ['All weights get the same update', 'Weights with large gradients take relatively smaller steps and weights with small gradients relatively larger ones', 'The learning rate grows', 'Momentum is removed'], 1, 'Per weight scaling.', 'Like RMSprop.')
K.quiz('m', 'Adam’s bias correction is needed because', ['Gradients are biased', 'm and v start at zero, so their early averages are too small', 'The learning rate is too large', 'Batch norm is used'], 1, 'Zero start.', 'Divide by 1 &minus; &beta;<sup>t</sup>.')
K.quiz('m', 'At test time batch normalisation uses', ['The statistics of the test batch', 'Running averages of mean and variance collected during training', 'Mean 0 and variance 1 with no learned scale', 'Nothing, it is removed'], 1, 'Running averages.', 'Forgetting model.eval() is a classic bug.')
K.quiz('m', 'Layer normalisation is preferred in transformers mainly because', ['It is older', 'It normalises each example on its own, so it does not depend on the batch', 'It has no learned parameters', 'It works only for images'], 1, 'No batch dependence.', 'Works with any batch size and sequence length.')
K.quiz('m', 'With inverted dropout and keep probability 0.8, kept activations are', ['Multiplied by 0.8', 'Divided by 0.8 during training', 'Set to 1', 'Unchanged'], 1, 'Scale by 1/p.', 'So test time needs no rescaling.')
K.quiz('h', 'Weight decay and L2 regularisation are the same for', ['Adam', 'Plain SGD, but not for adaptive methods like Adam, which is why AdamW decouples them', 'No optimiser', 'Every optimiser'], 1, 'Loshchilov and Hutter (2019).', 'Adam rescales the L2 gradient.')
K.quiz('h', 'When the batch size is multiplied by 4, the linear scaling rule suggests', ['Dividing the learning rate by 4', 'Multiplying the learning rate by about 4, with warm up', 'Keeping the learning rate the same', 'Using no schedule'], 1, 'Scale with batch.', 'Goyal and colleagues (2017).')
K.quiz('h', 'A very first training loss far above ln C for C classes suggests', ['Perfect training', 'A bug or a bad initialisation, since a random model should be near uniform', 'Too much data', 'Weight decay is too small'], 1, 'Expected start ln C.', 'Step 1 of the recipe.')
K.quiz('x', 'In the style of a Stanford CS231n exam: gradient descent on f = &frac12;(x&sup2; + 100y&sup2;) diverges when', ['&eta; &gt; 2', '&eta; &gt; 0.02', '&eta; &gt; 0.2', 'Never'], 1, '&eta; &lt; 2/&lambda;<sub>max</sub>.', '&lambda;<sub>max</sub> = 100.')
K.quiz('x', 'In the style of an MIT 6.S191 or CMU 11-785 exam: very large batch training often generalises worse because', ['It uses fewer examples', 'Less gradient noise tends to lead to sharper minima', 'It cannot use momentum', 'Batch norm fails'], 1, 'Sharp against flat minima.', 'Keskar and colleagues (2017).')

K.calc('e', 'Momentum with &beta; = 0.9: previous velocity 2, new gradient 1. New velocity?', '2.8', 'v = &beta;v + g.', ['0.9 &times; 2 = 1.8.', 'Add the gradient.', eq('1.8 + 1 = 2.8')], check=2.8)
K.calc('e', 'Inverted dropout with keep probability 0.8. A kept activation of 2.0 becomes?', '2.5', 'Divide by p.', ['Kept, so the mask is 1.', 'Scale by 1/0.8.', eq('2.0 / 0.8 = 2.5')], check=2.5)
K.calc('m', 'Plain gradient descent on f = &frac12;(x&sup2; + 100y&sup2;). Largest stable learning rate?', '0.02', '2/&lambda;<sub>max</sub>.', ['Curvatures 1 and 100.', '&lambda;<sub>max</sub> = 100.', eq('2 / 100 = 0.02')], check=0.02)
K.calc('m', 'Adam first step: g = 3, &beta;<sub>1</sub> = 0.9, m starts at 0. Bias corrected m&#770;?', '3', 'm/(1 &minus; &beta;<sub>1</sub>).', ['m = 0.1 &times; 3 = 0.3.', 'Divide by 1 &minus; 0.9 = 0.1.', eq('0.3 / 0.1 = 3')], check=3)
K.calc('m', 'Cosine decay with &eta;<sub>0</sub> = 0.1. Learning rate exactly halfway through training?', '0.05', '&frac12;&eta;<sub>0</sub>(1 + cos(&pi;/2)).', ['cos(&pi;/2) = 0.', '&frac12; &times; 0.1 &times; 1.', eq('0.05')], check=0.05)
K.calc('m', 'Batch norm on the batch (2, 4, 6) with &gamma; = 1, &beta; = 0 and &epsilon; ignored. Output for 6?', '1.2247', '(6 &minus; &mu;)/&sigma;.', ['&mu; = 4, variance (4 + 0 + 4)/3 = 2.667.', '&sigma; = 1.633.', eq('2 / 1.633 = 1.2247')], check=1.2247, tol=0.001)
K.calc('h', 'Step decay: &eta;<sub>0</sub> = 0.1, divided by 10 every 30 epochs. Learning rate at epoch 65?', '0.001', '&eta;<sub>0</sub> &middot; 0.1<sup>&lfloor;65/30&rfloor;</sup>.', ['&lfloor;65/30&rfloor; = 2.', '0.1<sup>2</sup> = 0.01.', eq('0.1 &times; 0.01 = 0.001')], check=0.001)
K.calc('h', 'Linear scaling rule: learning rate 0.1 works with batch 256. Learning rate for batch 1024?', '0.4', 'Scale by the batch ratio.', ['1024 / 256 = 4.', 'Multiply the rate by 4.', eq('0.1 &times; 4 = 0.4')], check=0.4)
K.calc('h', 'SGD with weight decay: w = 2, &eta; = 0.1, &lambda; = 0.01, loss gradient 0. New w?', '1.998', 'w(1 &minus; &eta;&lambda;).', ['&eta;&lambda; = 0.001.', '1 &minus; 0.001 = 0.999.', eq('2 &times; 0.999 = 1.998')], check=1.998)
K.calc('x', 'In the style of a Stanford CS231n problem: momentum &beta; = 0.9, learning rate 0.01, constant gradient 1. Step size once the velocity has settled?', '0.1', '&eta;g/(1 &minus; &beta;).', ['Terminal velocity g/(1 &minus; &beta;) = 10.', 'Times the learning rate.', eq('0.01 &times; 10 = 0.1')], check=0.1)

K.assign('momentum_update', 'e', 'A momentum update',
         '<p>Write <code>momentum_update(w, v, g, lr, beta)</code> that applies one momentum step, v = beta v + g and then w = w &minus; lr v, and returns [new w, new v], each rounded to 4 decimals.</p>',
         """
def momentum_update(w, v, g, lr, beta):
    # your code here
    pass
""", [('momentum_update(1.0, 0.0, 2.0, 0.1, 0.9)', [0.8, 2.0]), ('momentum_update(0.8, 2.0, 1.0, 0.1, 0.9)', [0.52, 2.8])],
         """
def momentum_update(w, v, g, lr, beta):
    v = beta * v + g
    w = w - lr * v
    return [round(w, 4), round(v, 4)]
""", 'Update the velocity first, then move the weight by the learning rate times the velocity.', '<p>With a steady gradient the velocity settles at g/(1 &minus; beta), 10 times g for beta = 0.9.</p>')
K.assign('adam_step', 'm', 'One Adam step',
         '<p>Write <code>adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8)</code> that updates m and v, applies bias correction for step t, updates w, and returns [w, m, v], each rounded to 6 decimals.</p>',
         """
def adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
    # your code here
    pass
""", [('adam_step(1.0, 0.0, 0.0, 0.5, 1, lr=0.1)', [0.9, 0.05, 0.00025]), ('adam_step(0.0, 0.0, 0.0, -4.0, 1, lr=0.01)', [0.01, -0.4, 0.016])],
         """
def adam_step(w, m, v, g, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * g * g
    m_hat = m / (1 - b1 ** t)
    v_hat = v / (1 - b2 ** t)
    w = w - lr * m_hat / (v_hat ** 0.5 + eps)
    return [round(w, 6), round(m, 6), round(v, 6)]
""", 'Update both averages, divide each by 1 minus beta to the power t, then step by lr times m hat over the root of v hat.', '<p>On the first step m hat is g and v hat is g squared, so the step is lr times the sign of g, whatever the size of g.</p>')
K.assign('batchnorm_forward', 'm', 'A batch normalisation forward pass',
         '<p>Write <code>batchnorm_forward(values, gamma, beta, eps=1e-5)</code> for one feature over a batch: subtract the mean, divide by &radic;(variance + eps) using the population variance, then multiply by gamma and add beta. Return the list rounded to 4 decimals.</p>',
         """
def batchnorm_forward(values, gamma, beta, eps=1e-5):
    # your code here
    pass
""", [('batchnorm_forward([1.0, 2.0, 3.0], 1.0, 0.0)', [-1.2247, 0.0, 1.2247]), ('batchnorm_forward([2.0, 2.0, 2.0], 2.0, 1.0)', [1.0, 1.0, 1.0]), ('batchnorm_forward([0.0, 10.0], 1.0, 5.0)', [4.0, 6.0])],
         """
def batchnorm_forward(values, gamma, beta, eps=1e-5):
    n = len(values)
    mean = sum(values) / n
    var = sum((x - mean) ** 2 for x in values) / n
    return [round(gamma * (x - mean) / (var + eps) ** 0.5 + beta + 0.0, 4) for x in values]
""", 'Find the mean and the population variance, normalise each value, then scale and shift.', '<p>eps stops a division by zero when every value in the batch is the same, as in the second test.</p>')

K.must('Optimisers', 'SGD &eta; &lt; 2/&lambda;<sub>max</sub>. Momentum v = &beta;v + g. RMSprop divides by &radic;s. Adam = both plus bias correction.')
K.must('Defaults', 'AdamW with &eta; about 1e&minus;3 or 3e&minus;4 and decay 0.01 to 0.1. SGD momentum 0.9 for large CNNs.')
K.must('Schedules', 'Warm up, then cosine or step decay. Batch &times; k means learning rate &times; k.')
K.must('Normalisation', 'BN over the batch per feature, running averages at test. LN per example, for transformers.')
K.must('Regularisation', 'Weight decay, inverted dropout (divide by p), early stopping on validation, more data and augmentation.')
K.must('Recipe', 'Check loss ln C at start, overfit one batch, find the rate, then regularise and tune one thing at a time.')

T = K.topic(
    slug='ml-training', topic='ml-training', step=(1, 'Neural network basics', 'ml-d1', 'Build neural networks from single neurons: perceptrons and multilayer networks, backpropagation, and the tricks that make deep networks train well.', 'Intermediate'),
    title='Training deep networks: optimisers, normalisation and regularisation', short='Training deep networks', badge='1.3', minutes=55,
    lead='Train networks that learn fast and generalise: SGD, momentum, RMSprop and Adam, mini batches and learning rate schedules, batch and layer normalisation, weight decay, dropout, early stopping, and a practical recipe.',
    desc='optimiser, SGD, momentum, RMSprop, Adam, AdamW, learning rate, mini batch, batch size, learning rate schedule, cosine decay, warm up, linear scaling rule, batch normalisation, layer normalisation, regularisation, weight decay, dropout, early stopping, overfitting, training recipe.',
    summary='Optimisers, schedules, normalisation, regularisation and a practical recipe for training deep networks.',
    keywords=['optimiser', 'Adam', 'momentum', 'learning rate schedule', 'batch normalisation', 'layer normalisation', 'dropout', 'weight decay', 'early stopping', 'overfitting'],
    recap='<p>Pick a good optimiser and schedule so the network learns quickly, normalise so deep layers stay healthy, and regularise so it learns the pattern rather than the noise. Check each stage with a careful recipe.</p>',
    added='2026-11-14', leet=leet_items())
