# Deep learning 3.3: diffusion models. Checked against Sohl-Dickstein and colleagues, Deep unsupervised learning using
# nonequilibrium thermodynamics (ICML 2015), Ho, Jain and Abbeel, Denoising diffusion probabilistic models (NeurIPS 2020),
# Song and Ermon, score matching with Langevin dynamics (NeurIPS 2019), Song and colleagues, Score based generative
# modeling through SDEs (ICLR 2021), Song, Meng and Ermon, DDIM (ICLR 2021), Nichol and Dhariwal, Improved DDPM (ICML 2021),
# Dhariwal and Nichol, Diffusion models beat GANs on image synthesis (NeurIPS 2021), Ho and Salimans, Classifier free
# diffusion guidance (2022), Rombach and colleagues, latent diffusion (CVPR 2022), Karras and colleagues, EDM (NeurIPS
# 2022), Peebles and Xie, DiT (ICCV 2023), and Lipman and colleagues, Flow matching (ICLR 2023).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('dl-diffusion')
K = Kit()
K.code('forward_noise', r'''
# The forward process of a diffusion model: add a little Gaussian noise at every step until only noise is left.
# Data: numbers from two bumps, around -2 and +2. Schedule: DDPM linear betas, T = 1000 steps.
import numpy as np

rng = np.random.default_rng(0)
x0 = np.where(rng.random(5000) < 0.5, -2.0, 2.0) + rng.normal(0, 0.3, 5000)

T = 1000
betas = np.linspace(1e-4, 0.02, T)          # noise added at step t
alphas = 1 - betas
alpha_bar = np.cumprod(alphas)              # how much of x0 is left after t steps

# Step by step: x_t = sqrt(1 - beta_t) x_(t-1) + sqrt(beta_t) noise
x = x0.copy()
print(f'start  data: mean {x0.mean():.2f}  std {x0.std():.2f}  share in the valley {np.mean(np.abs(x0) < 0.5):.2f}')
print('   t   alpha_bar   step by step: mean  std   one jump: mean  std   share in the valley |x| < 0.5')
for t in range(1, T + 1):
    x = np.sqrt(alphas[t - 1]) * x + np.sqrt(betas[t - 1]) * rng.normal(size=x.shape)
    if t in (1, 50, 100, 250, 500, 1000):
        # One jump: x_t = sqrt(alpha_bar_t) x0 + sqrt(1 - alpha_bar_t) noise gives the same distribution
        a = alpha_bar[t - 1]
        jump = np.sqrt(a) * x0 + np.sqrt(1 - a) * rng.normal(size=x0.shape)
        valley = np.mean(np.abs(x) < 0.5)                # empty at the start, 38 percent for N(0, 1)
        print(f'{t:4d}   {a:9.5f}   {x.mean():17.2f} {x.std():5.2f}   {jump.mean():13.2f} {jump.std():5.2f}   {valley:10.2f}')
print('After 1000 steps the data is plain N(0, 1) noise: the bumps are gone.')
''', long=True)

K.code('ddpm_1d', r'''
# Train a tiny noise predictor and generate new data with DDPM sampling. NumPy only.
# Data: two bumps at -2 and +2 (spread 0.3). The "network" is a linear model on smooth features of (x, t),
# trained with the DDPM loss: predict the noise that was added.
import numpy as np

rng = np.random.default_rng(0)
T = 1000
betas = np.linspace(1e-4, 0.02, T)
alphas = 1 - betas
alpha_bar = np.cumprod(alphas)


def sample_data(n):
    return np.where(rng.random(n) < 0.5, -2.0, 2.0) + rng.normal(0, 0.3, n)


CENTRES = np.linspace(-5, 5, 51)


def features(x, t):
    s = t / T                                                         # time scaled to 0..1
    bumps = np.exp(-((x[:, None] - CENTRES) ** 2) / (2 * 0.2 ** 2))   # 51 smooth bumps over x
    bumps = np.concatenate([bumps, x[:, None]], axis=1)               # plus x itself, for values far out
    time = np.stack([np.ones_like(s), s, s ** 2, np.sqrt(s)], axis=1)
    return (bumps[:, :, None] * time[:, None, :]).reshape(len(x), -1)


# Training: pick x0, a random step t and noise eps, build x_t, and fit eps_hat(x_t, t) to eps
n = 20000
x0 = sample_data(n)
t = rng.integers(1, T + 1, n)
eps = rng.normal(size=n)
xt = np.sqrt(alpha_bar[t - 1]) * x0 + np.sqrt(1 - alpha_bar[t - 1]) * eps
F = features(xt, t)
w = np.linalg.solve(F.T @ F + 1e-3 * np.eye(F.shape[1]), F.T @ eps)   # least squares = one perfect training run
loss = np.mean((F @ w - eps) ** 2)
print(f'DDPM training loss (mean squared error of the noise): {loss:.3f}   (guessing 0 would give 1.000)')

# Sampling: start from pure noise and remove the predicted noise step by step
x = rng.normal(size=2000)
for step in range(T, 0, -1):
    eps_hat = features(x, np.full(len(x), step)) @ w
    a, ab, b = alphas[step - 1], alpha_bar[step - 1], betas[step - 1]
    x = (x - b / np.sqrt(1 - ab) * eps_hat) / np.sqrt(a)
    if step > 1:
        x += np.sqrt(b) * rng.normal(size=len(x))                    # DDPM adds fresh noise on every step but the last

real = sample_data(2000)
for name, v in [('real data ', real), ('generated ', x)]:
    left, right = v[v < 0], v[v > 0]
    print(f'{name} share right {np.mean(v > 0):.2f}   left bump mean {left.mean():5.2f} std {left.std():.2f}   right bump mean {right.mean():5.2f} std {right.std():.2f}')
counts, edges = np.histogram(x, bins=16, range=(-4, 4))
for c, e in zip(counts, edges):
    print(f'{e:5.1f} {"#" * int(c / 12)}')
''', long=True)

K.code('samplers', r'''
# DDPM against DDIM, and classifier free guidance. To focus on the samplers, the noise predictor here is the exact
# best one for our two bump data (a trained network learns to approximate it).
import numpy as np

T = 1000
betas = np.linspace(1e-4, 0.02, T)
alpha_bar = np.cumprod(1 - betas)
MEANS, SPREAD = np.array([-2.0, 2.0]), 0.3


def eps_exact(x, t, weights=(0.5, 0.5)):
    """The best noise prediction at step t (1..T) for data made of bumps with these weights."""
    a = alpha_bar[t - 1]
    var = a * SPREAD ** 2 + 1 - a                                  # each bump after t steps of noise
    logp = np.log(np.array(weights) + 1e-300) - (x[:, None] - np.sqrt(a) * MEANS) ** 2 / (2 * var)
    r = np.exp(logp - logp.max(axis=1, keepdims=True))
    r /= r.sum(axis=1, keepdims=True)                              # which bump each x probably came from
    score = (r * -(x[:, None] - np.sqrt(a) * MEANS) / var).sum(axis=1)
    return -np.sqrt(1 - a) * score


def ddpm(n, eps_fn, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    for t in range(T, 0, -1):
        b, ab = betas[t - 1], alpha_bar[t - 1]
        x = (x - b / np.sqrt(1 - ab) * eps_fn(x, t)) / np.sqrt(1 - b)
        if t > 1:
            x += np.sqrt(b) * rng.normal(size=n)
    return x


def ddim(n, eps_fn, steps, seed=0):
    rng = np.random.default_rng(seed)
    ts = np.linspace(T, 1, steps).round().astype(int)              # visit only a few of the 1000 steps
    x = rng.normal(size=n)
    for i, t in enumerate(ts):
        e = eps_fn(x, t)
        x0_hat = (x - np.sqrt(1 - alpha_bar[t - 1]) * e) / np.sqrt(alpha_bar[t - 1])
        if i + 1 < len(ts):
            s = ts[i + 1]
            x = np.sqrt(alpha_bar[s - 1]) * x0_hat + np.sqrt(1 - alpha_bar[s - 1]) * e   # no fresh noise
        else:
            x = x0_hat
    return x


def describe(name, x, calls):
    right = x[x > 0]
    print(f'{name:22s} {calls:5d} network calls   share right {np.mean(x > 0):.2f}   right bump mean {right.mean():.2f} std {right.std():.2f}')


print('Real data: share right 0.50, each bump has mean +-2.00 and std 0.30')
describe('DDPM, 1000 steps', ddpm(3000, eps_exact), 1000)
for k in (50, 10, 3):
    describe(f'DDIM, {k} steps', ddim(3000, eps_exact, k), k)

print()
print('Classifier free guidance towards the right bump: eps = (1 + w) eps_cond - w eps_uncond')
for w in (0, 1, 3, 7):
    guided = lambda x, t, w=w: (1 + w) * eps_exact(x, t, (0.0, 1.0)) - w * eps_exact(x, t)
    describe(f'guidance w = {w}', ddim(3000, guided, 50), 2 * 50)
''', long=True)

K.code('schedules', r'''
# Noise schedules: how fast the signal fades. Linear (Ho and colleagues, 2020) against cosine (Nichol and Dhariwal, 2021).
import numpy as np

T = 1000
t = np.arange(1, T + 1)
linear = np.cumprod(1 - np.linspace(1e-4, 0.02, T))
s = 0.008
f = np.cos((t / T + s) / (1 + s) * np.pi / 2) ** 2
cosine = f / np.cos(s / (1 + s) * np.pi / 2) ** 2              # alpha_bar_t of the cosine schedule

print('   t    linear alpha_bar   cosine alpha_bar')
for k in (100, 250, 500, 750, 900, 1000):
    print(f'{k:4d}   {linear[k - 1]:16.4f}   {cosine[k - 1]:16.4f}')

for name, ab in [('linear', linear), ('cosine', cosine)]:
    snr = ab / (1 - ab)                                        # signal to noise ratio
    half = t[np.argmax(snr < 1)]                               # first step where noise outweighs signal
    useless = np.mean(ab < 0.001)                              # steps where almost nothing of x0 is left
    print(f'{name}: signal and noise are equal at step {half}, and {useless:.0%} of the steps have alpha_bar below 0.001')
''', long=True)

AB = '&#257;'

K.lesson('idea', 'The idea: destroy data with noise, then learn to undo it', f'''
{src('Sohl-Dickstein and colleagues (2015), and Ho, Jain and Abbeel, Denoising diffusion probabilistic models (2020).')}
{viz('mlforward')}
{wwh('A <b>diffusion model</b> has two processes. The <b>forward process</b> is fixed and needs no learning: over T steps (1000 in DDPM) it adds a little Gaussian noise to the data each time, until only pure noise is left. The <b>reverse process</b> is learned: a network learns to remove a little noise at a time, so that starting from pure noise and running it backwards produces brand new data.',
     'Turning noise into an image in one step is very hard, which is why GANs are unstable. Removing a small amount of noise is an easy, well defined task, and many easy steps add up to one hard one. Diffusion models train with a simple regression loss, do not collapse onto a few modes, and now power most image, video and audio generators.',
     'Pick a noise schedule &beta;<sub>1</sub> to &beta;<sub>T</sub>. Thanks to a closed form you can jump straight to any step t: x<sub>t</sub> = &radic;{AB}<sub>t</sub> x<sub>0</sub> + &radic;(1 &minus; {AB}<sub>t</sub>) &epsilon;. Train a network to look at x<sub>t</sub> and t and predict &epsilon;. To generate, start from noise and remove the predicted noise step by step.')}
{run('forward_noise')}
{note('Adding noise one step at a time and jumping straight to step t give the same mean and spread (1.63 against 1.61 at step 250, 1.01 against 0.99 at step 1000). The valley between the two bumps fills up from 0 to 38 percent of the points, which is exactly the share of N(0, 1) within 0.5 of zero.', 'exam')}
{fxs(fx('One forward step', 'q(x<sub>t</sub> | x<sub>t&minus;1</sub>) = N(&radic;(1 &minus; &beta;<sub>t</sub>) x<sub>t&minus;1</sub>, &beta;<sub>t</sub> I)', 'Shrink a little, add noise with variance &beta;<sub>t</sub>.', key=True),
     fx('Jump to any step', f'x<sub>t</sub> = &radic;{AB}<sub>t</sub> x<sub>0</sub> + &radic;(1 &minus; {AB}<sub>t</sub>) &epsilon;, &nbsp; &epsilon; ~ N(0, I)', f'{AB}<sub>t</sub> = (1 &minus; &beta;<sub>1</sub>)(1 &minus; &beta;<sub>2</sub>) ... (1 &minus; &beta;<sub>t</sub>).', key=True),
     fx('Signal to noise ratio', f'SNR(t) = {AB}<sub>t</sub> / (1 &minus; {AB}<sub>t</sub>)', 'Falls from very large to almost 0.'))}
{scene('Restoring an old photo, many times over', '<p>Imagine a photo that someone sprinkles with a little dust every second for a whole day, until it is pure grey speckle. A restorer who has watched thousands of photos get dusty learns one small skill: given a dusty photo and how long it has been sprinkled, guess the dust that was added last and brush it off. Applied a thousand times to pure speckle, that one small skill paints a brand new photo that never existed.</p>')}
''', kw=['diffusion model', 'forward process', 'reverse process', 'noise schedule', 'alpha bar', 'Gaussian noise', 'DDPM'])

K.lesson('train', 'Training: predict the noise', f'''
{src('Ho, Jain and Abbeel (2020), Algorithm 1 and section 3.4 (the simplified loss).')}
{wwh('The network &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t) gets a noisy example and the step number and predicts the noise &epsilon; that was mixed in. The loss is the mean squared error between the true and the predicted noise.',
     'The full training objective is a variational bound, like the VAE&rsquo;s ELBO. Ho and colleagues showed that it simplifies, with one change of weights, into plain noise prediction, which trains more stably and gives better samples. Predicting noise also means the target always has the same scale, whatever the step.',
     'Repeat: take a real example x<sub>0</sub>, pick a random step t from 1 to T, draw noise &epsilon;, build x<sub>t</sub> with the closed form, and take a gradient step on ||&epsilon; &minus; &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t)||&sup2;. No sampling chain is run during training, so it is as cheap as training a regression network.')}
{run('ddpm_1d')}
{note('The model is only a linear layer on smooth features of x and t, fitted in one least squares solve, but it is trained with exactly the DDPM loss. Its loss is 0.253, far below the 1.000 of always guessing zero. Sampled with 1000 DDPM steps it makes new numbers whose bumps have mean &minus;1.99 and 2.01 and spread 0.29, against &minus;2.00, 2.01 and 0.30 in the real data.', 'tip')}
{steps('Training, one step at a time (Algorithm 1)', [
    'Take a batch of real examples x<sub>0</sub>.',
    'For each, draw a step t uniformly from 1 to T, and noise &epsilon; ~ N(0, I).',
    eq(f'x<sub>t</sub> = &radic;{AB}<sub>t</sub> x<sub>0</sub> + &radic;(1 &minus; {AB}<sub>t</sub>) &epsilon;'),
    'Ask the network for its guess of the noise, &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t).',
    eq('L = || &epsilon; &minus; &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t) ||&sup2;, then one gradient step'),
    'Repeat for hundreds of thousands of steps.'])}
{fxs(fx('Simple DDPM loss', 'L<sub>simple</sub> = E<sub>t, x<sub>0</sub>, &epsilon;</sub> || &epsilon; &minus; &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t) ||&sup2;', 'A regression loss on the noise.', key=True),
     fx('Noise, data and score are the same thing', f'score &nabla; ln p<sub>t</sub>(x<sub>t</sub>) &asymp; &minus;&epsilon;<sub>&theta;</sub> / &radic;(1 &minus; {AB}<sub>t</sub>)', 'Predicting noise is learning the direction towards more likely data.', key=True))}
{deep('Where the simple loss comes from', f'<p>Like a VAE, the model maximises a lower bound on ln p(x<sub>0</sub>). Because every step is Gaussian, the bound becomes a sum of KL divergences between Gaussians, one per step, between the true reverse step q(x<sub>t&minus;1</sub> | x<sub>t</sub>, x<sub>0</sub>), which has a closed form, and the model&rsquo;s step. Writing the model&rsquo;s mean in terms of predicted noise turns each KL term into a weighted squared error on &epsilon;. Dropping the weights gives L<sub>simple</sub>, which puts more effort on the noisier, harder steps. Later work (EDM, v prediction, min SNR weighting) chooses the weights on purpose instead of dropping them.</p>')}
''', kw=['noise prediction', 'training loss', 'L simple', 'ELBO', 'score', 'epsilon prediction'])

K.lesson('sample', 'Sampling: DDPM and the faster DDIM', f'''
{src('Ho, Jain and Abbeel (2020), Algorithm 2, and Song, Meng and Ermon, Denoising diffusion implicit models (2021).')}
{viz('mlreverse')}
{wwh('<b>DDPM sampling</b> starts from noise x<sub>T</sub> and, for t = T down to 1, removes the predicted noise and adds a smaller amount of fresh noise. <b>DDIM</b> uses the same trained network but takes big deterministic jumps: predict the clean example, then move to a much earlier step without fresh noise.',
     'DDPM needs one network call per step, 1000 for one image, which is slow. DDIM gives nearly the same quality in 25 to 50 calls, and because it is deterministic the same starting noise always gives the same image, which makes editing and interpolation possible.',
     'Choose the sampler and the number of steps when you generate, not when you train. Fewer steps are faster but, below a point, the samples blur towards the average of the data.')}
{run('samplers')}
{note('DDIM with 50 steps matches DDPM with 1000 (bump spread 0.28 against 0.29), and 10 steps is still close (mean 1.92). With 3 steps the right bump has mean 0.82 and spread 0.50: the samples sit between the bumps, the blur of a model sampled too fast.', 'exam')}
{fxs(fx('DDPM step', f'x<sub>t&minus;1</sub> = (x<sub>t</sub> &minus; &beta;<sub>t</sub> / &radic;(1 &minus; {AB}<sub>t</sub>) &middot; &epsilon;<sub>&theta;</sub>) / &radic;(1 &minus; &beta;<sub>t</sub>) + &radic;&beta;<sub>t</sub> z', 'z ~ N(0, I), and no z on the last step.', key=True),
     fx('Predicted clean data', f'x&#770;<sub>0</sub> = (x<sub>t</sub> &minus; &radic;(1 &minus; {AB}<sub>t</sub>) &epsilon;<sub>&theta;</sub>) / &radic;{AB}<sub>t</sub>', 'The closed form, solved for x<sub>0</sub>.', key=True),
     fx('DDIM jump from t to s', f'x<sub>s</sub> = &radic;{AB}<sub>s</sub> x&#770;<sub>0</sub> + &radic;(1 &minus; {AB}<sub>s</sub>) &epsilon;<sub>&theta;</sub>', 'Deterministic: no fresh noise.', key=True))}
''', kw=['DDPM sampling', 'DDIM', 'deterministic sampler', 'number of steps', 'x0 prediction'])

K.lesson('guide', 'Conditioning, guidance and text to image', f'''
{src('Dhariwal and Nichol (2021), Ho and Salimans, Classifier free diffusion guidance (2022), and Rombach and colleagues, High resolution image synthesis with latent diffusion models (2022).')}
{wwh('A <b>conditional</b> diffusion model also gets a condition c, such as a class or a text prompt, and predicts &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t, c). <b>Classifier free guidance</b> trains one network both with and without the condition (the condition is dropped about 10 percent of the time) and at sampling time pushes away from the unconditional prediction.',
     'Plain conditioning follows the prompt only loosely. Guidance makes samples match the condition much more closely, at the cost of variety. It is the guidance scale slider in every text to image tool.',
     'Compute both predictions at each step and mix them: (1 + w) &epsilon;<sub>cond</sub> &minus; w &epsilon;<sub>uncond</sub>. Small w keeps variety, large w gives sharp, typical, less varied samples. Each step now costs two network calls.')}
{table(['Guidance w', 'Share in the right bump', 'Mean', 'Spread'], [['0', '1.00', '1.99', '0.27'], ['1', '1.00', '2.17', '0.19'], ['3', '1.00', '2.38', '0.15'], ['7', '1.00', '2.63', '0.13']])}
{note('These are the guidance lines of the samplers program. All samples land in the asked for bump even with w = 0. Raising w pushes them further from the other bump and squeezes the spread from 0.27 to 0.13: more typical, less varied. Very large w in image models gives oversaturated, cartoonish pictures.', 'warn')}
{fxs(fx('Classifier free guidance', '&epsilon;&#771; = (1 + w) &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t, c) &minus; w &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t, &empty;)', 'w = 0 is plain conditioning. Many tools show the scale as 1 + w.', key=True),
     fx('Latent diffusion size', '512 &times; 512 &times; 3 pixels &rarr; 64 &times; 64 &times; 4 latent', 'An autoencoder shrinks the image 48 times before diffusion runs.', key=True))}
{deep('How a text to image system fits together', '<p>A latent diffusion system such as Stable Diffusion has three parts. A <b>VAE</b> (Deep learning 3.1) compresses each image into a small latent and decodes latents back to pixels. A <b>text encoder</b> (CLIP or T5) turns the prompt into vectors. A <b>denoiser</b>, first a U-Net with cross attention to the text (Deep learning 2.1 and 2.3) and now often a transformer on latent patches (DiT), runs the diffusion process in latent space. Generation is: encode the prompt, start from latent noise, run 20 to 50 guided DDIM like steps, decode the latent into an image. Video and audio models use the same recipe on other latents.</p>')}
{link('computer-vision', 'Want the vision models these systems build on?', 'The Computer Vision subject covers modern vision models such as CLIP, vision transformers and segment anything.', 'Open Computer Vision')}
''', kw=['conditional diffusion', 'classifier free guidance', 'guidance scale', 'text to image', 'latent diffusion', 'Stable Diffusion', 'U-Net', 'DiT', 'cross attention'])

K.lesson('schedule', 'Noise schedules and the denoiser network', f'''
{src('Nichol and Dhariwal, Improved denoising diffusion probabilistic models (2021), and Karras and colleagues, Elucidating the design space of diffusion based generative models (2022).')}
{wwh('The <b>noise schedule</b> decides how fast {AB}<sub>t</sub> falls from 1 to 0. The linear schedule of DDPM raises &beta;<sub>t</sub> evenly from 0.0001 to 0.02. The <b>cosine schedule</b> makes {AB}<sub>t</sub> follow a cosine curve.',
     'With the linear schedule the data is almost destroyed halfway through, so many late steps only shuffle noise and teach the network little. The cosine schedule spreads the destruction more evenly, which helps small images most.',
     'Compare the schedules by when the signal to noise ratio reaches 1 and by how many steps are almost pure noise. The denoiser is usually a U-Net (Deep learning 2.1) that also receives t through a sinusoidal embedding, like the positional encoding of transformers (Deep learning 2.3).')}
{run('schedules')}
{note('With the linear schedule signal and noise are equal at step 260 and 18 percent of the steps have {AB} below 0.001. With the cosine schedule the crossing moves to step 497 and only 2 percent of the steps are spent on almost pure noise.', 'tip')}
''', kw=['noise schedule', 'linear schedule', 'cosine schedule', 'SNR', 'U-Net', 'time embedding', 'EDM'])

K.lesson('versus', 'Diffusion compared with other generative models', f'''
{versus('Generative models', ['', 'VAE', 'GAN', 'Diffusion', 'Autoregressive (GPT style)'], [
    ['How it generates', 'Decode one latent', 'One generator pass', 'Many denoising steps', 'One token at a time'],
    ['Training', 'Stable, ELBO', 'Unstable game', 'Stable regression on noise', 'Stable, next token loss'],
    ['Sample quality', 'Often blurry', 'Sharp', 'Sharp and varied', 'Sharp'],
    ['Variety (mode coverage)', 'Good', 'Can collapse', 'Good', 'Good'],
    ['Speed of sampling', 'Fast', 'Fast', 'Slow, sped up by DDIM and distillation', 'Slow for long outputs'],
    ['Used today for', 'Latent spaces, compression', 'Fast or real time images, super resolution', 'Images, video, audio, molecules', 'Text, code']],
    'Diffusion is the default for images, video and audio when quality and variety matter most. GANs remain where one fast pass is essential, and VAEs supply the latent space that diffusion runs in.')}
{deep('Score models, SDEs and flow matching', '<p>Song and Ermon trained networks to estimate the <b>score</b> &nabla; ln p(x) of the data at many noise levels and sampled with Langevin dynamics. Song and colleagues (2021) showed that DDPM and score models are two discretisations of one <b>stochastic differential equation</b>, and that every such SDE has a deterministic <b>probability flow ODE</b> with the same distributions at every time, which is what DDIM follows. <b>Flow matching</b> and rectified flow (2023) learn the velocity of a straight path from noise to data directly. They are now used in many leading image models because the straighter paths need fewer sampling steps. <b>Distillation</b> methods such as consistency models compress sampling to one to four steps.</p>')}
''', kw=['VAE vs GAN vs diffusion', 'score based models', 'SDE', 'probability flow ODE', 'flow matching', 'consistency models'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Forward step', 'q(x<sub>t</sub> | x<sub>t&minus;1</sub>) = N(&radic;&alpha;<sub>t</sub> x<sub>t&minus;1</sub>, &beta;<sub>t</sub> I), &nbsp; &alpha;<sub>t</sub> = 1 &minus; &beta;<sub>t</sub>', 'Fixed, no parameters.', key=True),
     fx('Closed form', f'q(x<sub>t</sub> | x<sub>0</sub>) = N(&radic;{AB}<sub>t</sub> x<sub>0</sub>, (1 &minus; {AB}<sub>t</sub>) I), &nbsp; {AB}<sub>t</sub> = &prod;<sub>s&le;t</sub> &alpha;<sub>s</sub>', 'Jump straight to any step.', key=True),
     fx('True reverse step given x<sub>0</sub>', f'q(x<sub>t&minus;1</sub> | x<sub>t</sub>, x<sub>0</sub>) = N(&mu;&#771;<sub>t</sub>, &beta;&#771;<sub>t</sub> I), &nbsp; &beta;&#771;<sub>t</sub> = (1 &minus; {AB}<sub>t&minus;1</sub>) / (1 &minus; {AB}<sub>t</sub>) &middot; &beta;<sub>t</sub>', 'The target each model step tries to match.', key=True),
     fx('Model mean from predicted noise', f'&mu;<sub>&theta;</sub> = (x<sub>t</sub> &minus; &beta;<sub>t</sub> / &radic;(1 &minus; {AB}<sub>t</sub>) &middot; &epsilon;<sub>&theta;</sub>) / &radic;&alpha;<sub>t</sub>', 'Used in the DDPM step.', key=True),
     fx('Tweedie formula', f'E[x<sub>0</sub> | x<sub>t</sub>] = (x<sub>t</sub> + (1 &minus; {AB}<sub>t</sub>) &nabla; ln p<sub>t</sub>(x<sub>t</sub>)) / &radic;{AB}<sub>t</sub>', 'Denoising and the score are linked exactly.'))}
{steps('Worked example: why the closed form holds', [
    'Write two forward steps with independent noises &epsilon;<sub>1</sub> and &epsilon;<sub>2</sub>.',
    eq('x<sub>1</sub> = &radic;&alpha;<sub>1</sub> x<sub>0</sub> + &radic;(1 &minus; &alpha;<sub>1</sub>) &epsilon;<sub>1</sub>, &nbsp; x<sub>2</sub> = &radic;&alpha;<sub>2</sub> x<sub>1</sub> + &radic;(1 &minus; &alpha;<sub>2</sub>) &epsilon;<sub>2</sub>'),
    'Substitute x<sub>1</sub> into x<sub>2</sub>.',
    eq('x<sub>2</sub> = &radic;(&alpha;<sub>1</sub>&alpha;<sub>2</sub>) x<sub>0</sub> + &radic;&alpha;<sub>2</sub> &radic;(1 &minus; &alpha;<sub>1</sub>) &epsilon;<sub>1</sub> + &radic;(1 &minus; &alpha;<sub>2</sub>) &epsilon;<sub>2</sub>'),
    'A sum of independent Gaussians is Gaussian, and the variances add.',
    eq('&alpha;<sub>2</sub>(1 &minus; &alpha;<sub>1</sub>) + (1 &minus; &alpha;<sub>2</sub>) = 1 &minus; &alpha;<sub>1</sub>&alpha;<sub>2</sub>'),
    f'So x<sub>2</sub> = &radic;{AB}<sub>2</sub> x<sub>0</sub> + &radic;(1 &minus; {AB}<sub>2</sub>) &epsilon; with {AB}<sub>2</sub> = &alpha;<sub>1</sub>&alpha;<sub>2</sub>. Induction gives every t.'])}
''', kw=['closed form derivation', 'reverse posterior', 'Tweedie formula', 'variance'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Teach a computer to clean a little noise off a picture. Start with pure noise, clean it a thousand times, and a new picture appears.</p>',
    '<p>Know the forward closed form, train a network to predict the noise, sample with DDPM or DDIM, and steer samples with classifier free guidance.</p>',
    '<p>Derive the loss from the ELBO, compare schedules and parameterisations (noise, x<sub>0</sub>, v), build latent diffusion with a VAE, a text encoder and a U-Net or DiT.</p>',
    '<p>Work with the SDE and probability flow ODE view, flow matching, distillation to a few steps, guidance theory, and diffusion for video, 3D, molecules and policies in robotics.</p>')}
{grow('Explain how noise becomes an image.',
      'Train and sample a small diffusion model.',
      'Design fast, controllable generators.')}
''', kw=['beginner', 'expert', 'v prediction', 'distillation'])

lc(1720, 'Decode XORed Array', 'decode-xored-array', 'e', 'Undo each step: if a ^ b = e then b = a ^ e', 'Start from first and undo the encoding one element at a time, like a reverse process that walks back step by step.', """
def decode(encoded, first):
    arr = [first]
    for e in encoded:
        arr.append(arr[-1] ^ e)            # a ^ b = e  means  b = a ^ e
    return arr
""", [('decode([1, 2, 3], 1)', [1, 0, 2, 1]), ('decode([6, 2, 7, 3], 4)', [4, 2, 0, 7, 4])])
lc(2007, 'Find Original Array From Doubled Array', 'find-original-array-from-doubled-array', 'm', 'Sort and count: the smallest remaining value must be an original, so remove its double', 'Work from the smallest value up. Each x needs one 2x to pair with. Zeros pair with zeros. Time O(n log n).', """
from collections import Counter


def findOriginalArray(changed):
    if len(changed) % 2:
        return []
    count = Counter(changed)
    original = []
    for x in sorted(count):                # smallest first: the smallest value must be an original
        if count[x] == 0:
            continue
        if x == 0:
            if count[0] % 2:
                return []
            original += [0] * (count[0] // 2)
            continue
        if count[2 * x] < count[x]:
            return []
        original += [x] * count[x]
        count[2 * x] -= count[x]
    return original
""", [('findOriginalArray([1, 3, 4, 2, 6, 8])', [1, 3, 4]), ('findOriginalArray([6, 3, 0, 1])', []), ('findOriginalArray([1])', []), ('findOriginalArray([0, 0, 0, 0])', [0, 0])])
lc(1734, 'Decode XORed Permutation', 'decode-xored-permutation', 'm', 'Recover the first element from the xor of 1..n and the xor of every other encoded value', 'The xor of the whole permutation is the xor of 1 to n. The encoded values at odd positions xor to perm[1] ^ ... ^ perm[n minus 1]. Their xor is perm[0], and the rest follows by undoing each step.', """
def decodePerm(encoded):
    n = len(encoded) + 1
    total = 0
    for v in range(1, n + 1):
        total ^= v                          # xor of the whole permutation
    rest = 0
    for i in range(1, n - 1, 2):
        rest ^= encoded[i]                  # perm[1] ^ perm[2] ^ ... ^ perm[n - 1]
    perm = [total ^ rest]
    for e in encoded:
        perm.append(perm[-1] ^ e)
    return perm
""", [('decodePerm([3, 1])', [1, 2, 3]), ('decodePerm([6, 5, 4, 6])', [2, 4, 1, 5, 3])])
lc(950, 'Reveal Cards In Increasing Order', 'reveal-cards-in-increasing-order', 'm', 'Simulate the reveal process on positions with a queue, then place the sorted cards', 'Run the reveal on the positions 0 to n minus 1 instead of on cards. The order in which positions come out is where the smallest, next smallest and so on must go.', """
from collections import deque


def deckRevealedIncreasing(deck):
    order = deque(range(len(deck)))         # positions in the order they will be revealed
    result = [0] * len(deck)
    for card in sorted(deck):
        result[order.popleft()] = card
        if order:
            order.append(order.popleft())   # the next card goes to the bottom
    return result
""", [('deckRevealedIncreasing([17, 13, 11, 2, 3, 5, 7])', [2, 13, 3, 11, 5, 17, 7]), ('deckRevealedIncreasing([1, 1000])', [1, 1000])])
lc(780, 'Reaching Points', 'reaching-points', 'h', 'Run the moves backwards from the target: the larger coordinate came last, and modulo skips many steps at once', 'Forwards there are two choices at every step, backwards only one, just as the reverse process of a diffusion model walks back one determined path. Use modulo to jump many subtractions, like DDIM skips steps. Time O(log max).', """
def reachingPoints(sx, sy, tx, ty):
    while tx >= sx and ty >= sy:            # run the moves backwards: the larger number came last
        if tx == ty:
            break
        if tx > ty:
            if ty > sy:
                tx %= ty
            else:
                return (tx - sx) % ty == 0
        else:
            if tx > sx:
                ty %= tx
            else:
                return (ty - sy) % tx == 0
    return tx == sx and ty == sy
""", [('reachingPoints(1, 1, 3, 5)', True), ('reachingPoints(1, 1, 2, 2)', False), ('reachingPoints(1, 1, 1, 1)', True), ('reachingPoints(3, 7, 3, 4)', False), ('reachingPoints(9, 5, 12, 8)', False)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>A diffusion model learns to run a process backwards. These problems are about the same skill: undoing an encoding step by step, recovering an original from a transformed copy, and working backwards from the end where going forwards has too many choices.</p>'), kw=['LeetCode', 'reverse process', 'xor decoding', 'work backwards'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    f'The <b>forward process</b> adds Gaussian noise over T steps. Any step in one jump: x<sub>t</sub> = &radic;{AB}<sub>t</sub> x<sub>0</sub> + &radic;(1 &minus; {AB}<sub>t</sub>) &epsilon;.',
    'Training is regression: predict the added noise with the loss ||&epsilon; &minus; &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t)||&sup2;. Predicting noise is the same as learning the score.',
    '<b>DDPM</b> samples with 1000 small noisy steps. <b>DDIM</b> jumps deterministically and matched it with 50 steps, but 3 steps blurred the samples.',
    '<b>Classifier free guidance</b> (1 + w) &epsilon;<sub>cond</sub> &minus; w &epsilon;<sub>uncond</sub> follows the condition more closely and narrows the variety (spread 0.27 to 0.13).',
    '<b>Latent diffusion</b> runs in a VAE latent 48 times smaller than the pixels, with a text encoder and a U-Net or DiT. The cosine schedule wastes fewer steps on pure noise.'],
    'Coming next: energy based models, from Hopfield networks and Boltzmann machines to RBMs and deep belief networks.')}
{files('Three tasks: the alpha bar schedule, a noisy sample in one jump, and classifier free guidance.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'The forward process of a diffusion model', ['Is learned', 'Adds a little Gaussian noise at every step until only noise is left', 'Removes noise', 'Compresses the image'], 1, 'Fixed, no learning.', 'Only the reverse process is learned.')
K.quiz('e', 'What does the DDPM network predict?', ['The class', 'The noise that was added to x<sub>t</sub>', 'The next pixel', 'A real or fake score'], 1, 'Noise prediction.', 'The loss is a squared error on the noise.')
K.quiz('e', 'Generation starts from', ['A real image', 'Pure Gaussian noise', 'A blank image', 'A text file'], 1, 'Step T.', 'Then the noise is removed step by step.')
K.quiz('e', f'As t grows, {AB}<sub>t</sub>', ['Grows', 'Falls from about 1 to about 0', 'Stays at 1', 'Becomes negative'], 1, 'Less of the data is left.', 'It is a product of numbers below 1.')
K.quiz('m', 'Why can training pick a random step t without running the chain?', ['It cannot', 'The closed form gives x<sub>t</sub> from x<sub>0</sub> in one jump', 'The network ignores t', 'Training uses DDIM'], 1, 'Sum of Gaussians.', 'Training is as cheap as regression.')
K.quiz('m', 'DDIM is faster than DDPM because it', ['Uses a smaller network', 'Takes big deterministic jumps, visiting far fewer steps', 'Skips training', 'Uses GPUs'], 1, 'Fewer network calls.', '50 calls matched 1000 here.')
K.quiz('m', 'Raising the classifier free guidance scale w', ['Increases variety', 'Makes samples follow the condition more closely but less varied', 'Speeds up sampling', 'Has no effect'], 1, 'Quality against variety.', 'Spread fell from 0.27 to 0.13.')
K.quiz('m', 'Latent diffusion runs the diffusion process', ['On raw pixels', 'In the small latent space of an autoencoder', 'On text', 'On the labels'], 1, 'Cheaper.', '64 by 64 by 4 instead of 512 by 512 by 3.')
K.quiz('m', 'Compared with GANs, diffusion models usually', ['Collapse onto few modes', 'Train stably and cover the data well, but sample slowly', 'Need no data', 'Sample in one pass'], 1, 'Stable and varied.', 'The price is many steps.')
K.quiz('h', 'Classifier free guidance is trained by', ['Training a separate classifier', 'Dropping the condition for part of the training examples', 'Using two datasets', 'Freezing the network'], 1, 'One network, two modes.', 'About 10 percent of the time.')
K.quiz('h', 'With too few DDIM steps, samples tend to', ['Become sharper', 'Blur towards the average of the data', 'Copy training images', 'Turn into noise'], 1, 'x&#770;<sub>0</sub> at high noise is an average.', '3 steps put the bump at 0.82 instead of 2.')
K.quiz('h', 'The cosine schedule improves on the linear one mainly by', ['Using fewer parameters', 'Destroying the signal more evenly, so fewer steps are wasted on near pure noise', 'Removing the need for noise', 'Making sampling deterministic'], 1, 'SNR = 1 at step 497, not 260.', 'Only 2 percent of steps are near pure noise.')
K.quiz('x', 'In the style of a Stanford CS236 exam: the noise prediction and the score are related by', ['score = &epsilon;', f'score = &minus;&epsilon; / &radic;(1 &minus; {AB}<sub>t</sub>)', 'score = &epsilon;&sup2;', 'They are unrelated'], 1, 'Gradient of a Gaussian log density.', 'Denoising is score matching.')
K.quiz('x', 'In the style of an MIT 6.S978 question: DDIM sampling with no fresh noise follows', ['A random walk', 'The probability flow ODE of the diffusion SDE', 'Gradient ascent on the loss', 'A GAN generator'], 1, 'Song and colleagues (2021).', 'Same marginals, deterministic paths.')

K.calc('e', 'Two steps with &beta; = 0.1 and &beta; = 0.2. Find &#257;<sub>2</sub>.', '0.72', 'Multiply the (1 &minus; &beta;) values.', ['1 &minus; 0.1 = 0.9.', '1 &minus; 0.2 = 0.8.', eq('&#257;<sub>2</sub> = 0.9 &times; 0.8 = 0.72')], check=0.72)
K.calc('e', 'x<sub>0</sub> = 2, &#257;<sub>t</sub> = 0.64 and the drawn noise is &epsilon; = 0.5. Find x<sub>t</sub>.', '1.9', '&radic;&#257; x<sub>0</sub> + &radic;(1 &minus; &#257;) &epsilon;.', ['&radic;0.64 = 0.8 and &radic;0.36 = 0.6.', '0.8 &times; 2 = 1.6 and 0.6 &times; 0.5 = 0.3.', eq('x<sub>t</sub> = 1.6 + 0.3 = 1.9')], check=1.9)
K.calc('e', 'DDPM uses 1000 network calls and DDIM uses 50. How many times faster is DDIM?', '20', 'Ratio of calls.', ['DDPM: 1000 calls.', 'DDIM: 50 calls.', eq('1000 / 50 = 20')], check=20)
K.calc('m', 'Find the signal to noise ratio when &#257;<sub>t</sub> = 0.8.', '4', '&#257; / (1 &minus; &#257;).', ['Signal share: 0.8.', 'Noise share: 1 &minus; 0.8 = 0.2.', eq('SNR = 0.8 / 0.2 = 4')], check=4)
K.calc('m', 'x<sub>t</sub> = 1.9, &#257;<sub>t</sub> = 0.64 and the network predicts &epsilon;&#770; = 0.5. Predicted clean x&#770;<sub>0</sub>?', '2', '(x<sub>t</sub> &minus; &radic;(1 &minus; &#257;) &epsilon;&#770;) / &radic;&#257;.', ['&radic;(1 &minus; 0.64) &times; 0.5 = 0.6 &times; 0.5 = 0.3.', '1.9 &minus; 0.3 = 1.6.', eq('x&#770;<sub>0</sub> = 1.6 / 0.8 = 2')], check=2)
K.calc('m', 'A 512 &times; 512 RGB image becomes a 64 &times; 64 &times; 4 latent. How many times fewer numbers?', '48', 'Count both.', ['Image: 512 &times; 512 &times; 3 = 786,432.', 'Latent: 64 &times; 64 &times; 4 = 16,384.', eq('786,432 / 16,384 = 48')], check=48)
K.calc('m', '&epsilon;<sub>cond</sub> = 0.4, &epsilon;<sub>uncond</sub> = 0.1 and w = 3. Guided noise prediction?', '1.3', '(1 + w) &epsilon;<sub>cond</sub> &minus; w &epsilon;<sub>uncond</sub>.', ['(1 + 3) &times; 0.4 = 1.6.', '3 &times; 0.1 = 0.3.', eq('1.6 &minus; 0.3 = 1.3')], check=1.3)
K.calc('h', 'Data with variance 4 is noised to &#257;<sub>t</sub> = 0.5241. Spread (standard deviation) of x<sub>t</sub>?', '1.604', 'Var = &#257; Var(x<sub>0</sub>) + (1 &minus; &#257;).', ['0.5241 &times; 4 = 2.0964.', '2.0964 + 0.4759 = 2.5723.', eq('&radic;2.5723 = 1.604')], check=1.604, tol=0.001)
K.calc('h', 'One DDPM step without the noise term: x<sub>t</sub> = 1, &beta;<sub>t</sub> = 0.02, &#257;<sub>t</sub> = 0.5, &epsilon;&#770; = 0.5. Find the mean of x<sub>t&minus;1</sub>.', '0.9959', '(x<sub>t</sub> &minus; &beta;<sub>t</sub> / &radic;(1 &minus; &#257;<sub>t</sub>) &epsilon;&#770;) / &radic;(1 &minus; &beta;<sub>t</sub>).', ['0.02 / &radic;0.5 = 0.02828, times 0.5 = 0.01414.', '1 &minus; 0.01414 = 0.98586, and &radic;0.98 = 0.98995.', eq('0.98586 / 0.98995 = 0.9959')], check=0.9959, tol=0.0005)
K.calc('x', 'In the style of a score matching exam: &#257;<sub>t</sub> = 0.75 and the network predicts &epsilon;&#770; = 0.6. Estimated score &nabla; ln p<sub>t</sub>(x<sub>t</sub>)?', '−1.2', '&minus;&epsilon;&#770; / &radic;(1 &minus; &#257;<sub>t</sub>).', ['1 &minus; 0.75 = 0.25.', '&radic;0.25 = 0.5.', eq('&minus;0.6 / 0.5 = &minus;1.2')], check=-1.2)

K.assign('alpha_bars', 'e', 'The alpha bar schedule',
         '<p>Write <code>alpha_bars(betas)</code> that returns the list of &#257;<sub>t</sub> = (1 &minus; &beta;<sub>1</sub>) ... (1 &minus; &beta;<sub>t</sub>), each rounded to 4 decimals.</p>',
         """
def alpha_bars(betas):
    # your code here
    pass
""", [('alpha_bars([0.1, 0.2])', [0.9, 0.72]), ('alpha_bars([0.5, 0.5, 0.5])', [0.5, 0.25, 0.125]), ('alpha_bars([])', [])],
         """
def alpha_bars(betas):
    out, prod = [], 1.0
    for b in betas:
        prod *= 1 - b
        out.append(round(prod, 4))
    return out
""", 'Keep a running product of 1 &minus; &beta; and record it after each step.', '<p>np.cumprod(1 &minus; betas) does the same in one line. It only goes down, because every factor is below 1.</p>')
K.assign('noisy_sample', 'e', 'A noisy sample in one jump',
         '<p>Write <code>noisy_sample(x0, alpha_bar, eps)</code> that returns &radic;&#257; &middot; x0 + &radic;(1 &minus; &#257;) &middot; eps rounded to 4 decimals.</p>',
         """
def noisy_sample(x0, alpha_bar, eps):
    # your code here
    pass
""", [('noisy_sample(2, 0.64, 0.5)', 1.9), ('noisy_sample(1, 1.0, 3)', 1.0), ('noisy_sample(0, 0.0, -1.5)', -1.5)],
         """
import math


def noisy_sample(x0, alpha_bar, eps):
    return round(math.sqrt(alpha_bar) * x0 + math.sqrt(1 - alpha_bar) * eps, 4)
""", 'Two square roots, then a weighted sum.', '<p>At &#257; = 1 nothing is noised, at &#257; = 0 only the noise is left.</p>')
K.assign('guided_eps', 'm', 'Classifier free guidance',
         '<p>Write <code>guided_eps(eps_cond, eps_uncond, w)</code> for two lists of the same length. Return (1 + w) &middot; cond &minus; w &middot; uncond for each position, rounded to 4 decimals.</p>',
         """
def guided_eps(eps_cond, eps_uncond, w):
    # your code here
    pass
""", [('guided_eps([0.4], [0.1], 3)', [1.3]), ('guided_eps([1, 2], [1, 0], 1)', [1, 4]), ('guided_eps([0.3, -0.2], [0.9, 0.5], 0)', [0.3, -0.2])],
         """
def guided_eps(eps_cond, eps_uncond, w):
    return [round((1 + w) * c - w * u, 4) for c, u in zip(eps_cond, eps_uncond)]
""", 'Combine the two predictions position by position.', '<p>With w = 0 you get the plain conditional prediction. Each guided step needs both predictions, so it costs two network calls.</p>')

K.must('Forward', f'Fixed noising over T steps. Closed form x<sub>t</sub> = &radic;{AB}<sub>t</sub> x<sub>0</sub> + &radic;(1 &minus; {AB}<sub>t</sub>) &epsilon;, {AB}<sub>t</sub> = &prod;(1 &minus; &beta;).')
K.must('Training', 'Random t, build x<sub>t</sub>, regress the noise: ||&epsilon; &minus; &epsilon;<sub>&theta;</sub>(x<sub>t</sub>, t)||&sup2;. Stable, no chain during training.')
K.must('Sampling', 'DDPM: 1000 noisy steps. DDIM: deterministic jumps, 50 steps matched it, 3 steps blur.')
K.must('Guidance', '(1 + w) &epsilon;<sub>cond</sub> &minus; w &epsilon;<sub>uncond</sub>. Higher w: closer to the prompt, less variety. Condition dropped about 10 percent in training.')
K.must('Latent diffusion', 'VAE latent (48 times fewer numbers), text encoder, U-Net or DiT denoiser, 20 to 50 guided steps, decode.')
K.must('Theory', f'score = &minus;&epsilon; / &radic;(1 &minus; {AB}<sub>t</sub>). DDPM and score models share one SDE, DDIM follows its ODE. Cosine schedule wastes fewer steps.')

T = K.topic(
    slug='dl-diffusion', topic='dl-diffusion', step=(3, 'Generative models', 'dl-s3', 'Networks that create new data: autoencoders and variational autoencoders, generative adversarial networks, diffusion models, and energy based models such as Boltzmann machines.', 'Advanced'),
    title='Diffusion models', short='Diffusion models', badge='3.3', minutes=60,
    lead='Generate data by learning to remove noise: the forward process and its closed form, training by noise prediction, DDPM and DDIM sampling, classifier free guidance, latent diffusion for text to image, and noise schedules.',
    desc='Diffusion model, forward process, reverse process, noise schedule, alpha bar, DDPM, noise prediction, score, DDIM, classifier free guidance, guidance scale, latent diffusion, Stable Diffusion, U-Net, DiT, cosine schedule, SDE, probability flow ODE, flow matching.',
    summary='Forward noising, noise prediction training, DDPM and DDIM sampling, guidance, latent diffusion and schedules.',
    keywords=['diffusion model', 'DDPM', 'DDIM', 'noise prediction', 'classifier free guidance', 'latent diffusion', 'Stable Diffusion', 'score', 'noise schedule', 'flow matching'],
    recap='<p>Ruin data with noise in many small steps, train a network to guess the noise, and then run the process backwards from pure noise, guided by a prompt, to create something new.</p>',
    added='2026-11-14', leet=leet_items())
