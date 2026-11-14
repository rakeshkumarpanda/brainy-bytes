# Deep learning 3.2: generative adversarial networks. Checked against Goodfellow and colleagues, Generative adversarial
# nets (NeurIPS 2014), Goodfellow, NIPS 2016 tutorial on GANs, Radford, Metz and Chintala, DCGAN (ICLR 2016), Salimans
# and colleagues, Improved techniques for training GANs (NeurIPS 2016), Arjovsky, Chintala and Bottou, Wasserstein GAN
# (ICML 2017), Gulrajani and colleagues, WGAN-GP (NeurIPS 2017), Heusel and colleagues, FID and TTUR (NeurIPS 2017),
# Karras and colleagues, ProGAN (ICLR 2018) and StyleGAN (CVPR 2019), Mirza and Osindero, conditional GANs (2014),
# Isola and colleagues, pix2pix (CVPR 2017), and Zhu and colleagues, CycleGAN (ICCV 2017).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('dl-gans')
K = Kit()
K.code('gan_1d', r'''
# A tiny GAN in NumPy. Real data: numbers from N(4, 0.5 squared).
# Generator: x = a * z + b with z from N(0, 1), so it can only shift and stretch the noise.
# Discriminator: logistic regression on the features 1, x/4, (x/4)^2 and, optionally, the spread of the whole batch.
import numpy as np


def sigmoid(t):
    return 1 / (1 + np.exp(-t))


def features(x, use_batch_std):
    batch_std = np.full_like(x, x.std()) if use_batch_std else np.zeros_like(x)
    return np.stack([np.ones_like(x), x / 4, (x / 4) ** 2, batch_std])


def train(generator_loss, use_batch_std=False, steps=3000, d_steps=5, d_lr=1.0, g_lr=0.05, batch=256, seed=0):
    rng = np.random.default_rng(seed)
    a, b = 1.0, 0.0                     # the generator starts as N(0, 1), far from the data
    w = np.zeros(4)                     # discriminator weights
    for step in range(steps + 1):
        # 1. Discriminator: a few steps of logistic regression with real = 1 and fake = 0
        for _ in range(d_steps):
            real = rng.normal(4, 0.5, batch)
            fake = a * rng.normal(0, 1, batch) + b
            fr, ff = features(real, use_batch_std), features(fake, use_batch_std)
            w -= d_lr * (fr @ (sigmoid(w @ fr) - 1) + ff @ sigmoid(w @ ff)) / batch
        # 2. Generator: one step that makes the discriminator score the fakes higher
        z = rng.normal(0, 1, batch)
        fake = a * z + b
        d_fake = sigmoid(w @ features(fake, use_batch_std))
        if generator_loss == 'non-saturating':     # minimise -log D(G(z))
            dloss_dlogit = -(1 - d_fake)
        else:                                      # minimise log(1 - D(G(z))), the original minimax loss
            dloss_dlogit = -d_fake
        dlogit_dx = (w[1] + 2 * w[2] * fake / 4) / 4
        grad_a = np.mean(dloss_dlogit * dlogit_dx * z) + np.mean(dloss_dlogit) * w[3] * np.sign(a) * z.std()
        grad_b = np.mean(dloss_dlogit * dlogit_dx)
        a, b = a - g_lr * grad_a, b - g_lr * grad_b
        if step in (0, 100, 300, 1000, 3000):
            print(f'  step {step:4d}: fake mean {b:5.2f}, fake std {abs(a):4.2f}')


print('Real data: mean 4.00, std 0.50')
for loss, mb in (('saturating', False), ('non-saturating', False), ('non-saturating', True)):
    print(f'Generator loss {loss}' + (', discriminator also sees the batch spread' if mb else ''))
    train(loss, mb)
''', long=True)

K.code('gan_theory', r'''
# The optimal discriminator and what the GAN game really minimises.
# Real data p = N(0, 1). Generator q = N(m, 1) for a few shifts m. We work on a fine grid of x values.
import numpy as np

x = np.linspace(-20, 30, 200001)
dx = x[1] - x[0]


def normal_pdf(x, mean, std=1.0):
    return np.exp(-0.5 * ((x - mean) / std) ** 2) / (std * np.sqrt(2 * np.pi))


def kl(p, q):
    mask = p > 1e-300
    return np.sum(p[mask] * np.log(p[mask] / q[mask])) * dx


p = normal_pdf(x, 0)
print('shift m | D* at x = 0 | value V(D*, G) | -log 4 + 2 JS | JS divergence')
for m in (0, 1, 3, 10):
    q = normal_pdf(x, m)
    d_star = p / (p + q + 1e-300)                    # the best possible discriminator for this generator
    value = (np.sum(p * np.log(d_star + 1e-300)) + np.sum(q * np.log(1 - d_star + 1e-300))) * dx
    mix = (p + q) / 2
    js = 0.5 * kl(p, mix) + 0.5 * kl(q, mix)
    print(f'{m:7d} | {d_star[np.argmin(abs(x))]:11.3f} | {value:14.4f} | {-np.log(4) + 2 * js:13.4f} | {js:.4f}')
print(f'log 2 = {np.log(2):.4f}, -log 4 = {-np.log(4):.4f}')
''', long=True)

K.code('gan_distances', r'''
# Why Wasserstein GANs help: JS divergence stops changing once two distributions stop overlapping,
# but the Wasserstein (earth mover's) distance keeps growing with the gap, so it still gives a useful gradient.
import numpy as np
from scipy.stats import wasserstein_distance

rng = np.random.default_rng(0)
real = rng.uniform(0, 1, 20000)                     # real data: uniform on [0, 1]


def js_divergence(a, b, bins):
    p, _ = np.histogram(a, bins=bins)
    q, _ = np.histogram(b, bins=bins)
    p, q = p / p.sum(), q / q.sum()
    m = (p + q) / 2
    kl = lambda u, v: np.sum(u[u > 0] * np.log(u[u > 0] / v[u > 0]))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


bins = np.linspace(-1, 12, 1301)
print('shift | JS divergence | Wasserstein distance')
for shift in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0):
    fake = rng.uniform(0, 1, 20000) + shift          # the generator's samples, moved to the right
    print(f'{shift:5.1f} | {js_divergence(real, fake, bins):13.3f} | {wasserstein_distance(real, fake):20.3f}')
print(f'JS can never exceed log 2 = {np.log(2):.3f}')
''', long=True)

K.code('fid', r'''
# Frechet distance (the idea behind FID) between sets of digit images.
# Real FID uses features from an Inception network. Here PCA features of 8 x 8 digits play that role.
import numpy as np
from scipy.linalg import sqrtm
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

X, y = load_digits(return_X_y=True)
X = X / 16.0
rng = np.random.default_rng(0)
idx = rng.permutation(len(X))
train, test, y_train = X[idx[:900]], X[idx[900:]], y[idx[:900]]
pca = PCA(n_components=20).fit(train)


def frechet(a, b):
    fa, fb = pca.transform(a), pca.transform(b)
    mu_a, mu_b = fa.mean(axis=0), fb.mean(axis=0)
    cov_a, cov_b = np.cov(fa, rowvar=False), np.cov(fb, rowvar=False)
    root = sqrtm(cov_a @ cov_b).real
    return np.sum((mu_a - mu_b) ** 2) + np.trace(cov_a + cov_b - 2 * root)


candidates = {
    'other real digits': train,
    'real digits plus noise (std 0.2)': np.clip(train + rng.normal(0, 0.2, train.shape), 0, 1),
    'real digits plus noise (std 0.4)': np.clip(train + rng.normal(0, 0.4, train.shape), 0, 1),
    'only real 1s (mode collapse)': train[y_train == 1],
    'the average image, repeated': np.tile(train.mean(axis=0), (900, 1)) + rng.normal(0, 0.01, (900, 64)),
}
for name, images in candidates.items():
    print(f'{name:34s} distance to the test digits: {frechet(images, test):6.2f}')
''', long=True)


K.lesson('idea', 'The GAN game: a generator against a discriminator', f'''
{src('Goodfellow and colleagues, Generative adversarial nets (NeurIPS 2014), and Goodfellow, NIPS 2016 tutorial on generative adversarial networks.')}
{viz('mlgan1d')}
{wwh('A <b>generative adversarial network</b> (GAN) trains two networks against each other. The <b>generator</b> G turns random noise z into a fake example G(z). The <b>discriminator</b> D looks at an example and outputs the probability that it is real. D is trained to tell real from fake, and G is trained to fool D.',
     'A GAN learns to generate data without ever writing down a probability formula for it. All it needs is samples of real data and a network that can judge them. This gave the first sharp, realistic generated faces and images, and the same idea of a learned critic is still used in image restoration, super resolution and the decoders of modern image generators.',
     'Alternate two steps. First, update D with ordinary binary cross entropy: real examples have label 1 and generated examples have label 0. Then, update G so that D gives its fakes higher scores, passing the gradient through D into G while D stays fixed. Repeat for many thousands of steps.')}
{run('gan_1d')}
{note('In this tiny GAN the real numbers come from a bell curve with mean 4.00 and spread 0.50. With the original minimax loss the generator is still at mean 1.15 after 100 steps and its spread later collapses to 0.00. The non saturating loss reaches mean 3.83 by step 100 and settles at mean 4.03, but with a spread of only 0.17. When the discriminator can also see the spread of each batch, the generator ends at mean 4.00 and spread 0.50.', 'exam')}
{fxs(fx('Minimax game', 'min<sub>G</sub> max<sub>D</sub> V(D, G) = E<sub>x~p<sub>data</sub></sub>[ln D(x)] + E<sub>z~p<sub>z</sub></sub>[ln(1 &minus; D(G(z)))]', 'Goodfellow and colleagues (2014).', key=True),
     fx('Discriminator loss', 'L<sub>D</sub> = &minus;ln D(x) &minus; ln(1 &minus; D(G(z)))', 'Binary cross entropy, real = 1, fake = 0.', key=True),
     fx('Generator loss (non saturating)', 'L<sub>G</sub> = &minus;ln D(G(z))', 'Used in practice.', key=True))}
{scene('A forger and an inspector', 'A new banknote inspector and a forger start on the same day. At first the forger draws crude notes and the inspector rejects them by their colour. The forger fixes the colour, so the inspector starts checking the watermark. Each time one gets better, the other has to improve. In a GAN the forger is the generator and the inspector is the discriminator, and both are networks updated by gradient descent.')}
''', kw=['GAN', 'generative adversarial network', 'generator', 'discriminator', 'minimax', 'noise vector', 'adversarial training'])

K.lesson('trouble', 'The best discriminator, the right loss, and mode collapse', f'''
{src('Goodfellow and colleagues (2014) section 4, Goodfellow (2016) section 3.2.3, Salimans and colleagues, Improved techniques for training GANs (NeurIPS 2016), and Karras and colleagues, ProGAN (ICLR 2018).')}
{viz('mlganloss')}
{wwh('For a fixed generator, the best discriminator is <b>D*(x) = p<sub>data</sub>(x) / (p<sub>data</sub>(x) + p<sub>g</sub>(x))</b>. With that D, the GAN value equals &minus;ln 4 + 2 &middot; JS(p<sub>data</sub>, p<sub>g</sub>), so the generator is really lowering the <b>Jensen Shannon divergence</b> between the real and the generated distribution. The <b>non saturating</b> generator loss &minus;ln D(G(z)) replaces ln(1 &minus; D(G(z))) because it gives strong gradients early in training. <b>Mode collapse</b> is when the generator produces only a few kinds of output.',
     'This explains the two classic failures. Early on, D rejects every fake, D(G(z)) is near 0, and ln(1 &minus; D) is almost flat there, so the original loss gives the generator nearly no signal. Later, the generator can score well by producing one convincing output again and again, because each fake is judged on its own and nothing rewards variety.',
     'Use the non saturating loss. Give D information about the whole batch, for example the minibatch standard deviation layer of ProGAN and StyleGAN, or minibatch discrimination (Salimans and colleagues 2016). Watch generated samples during training, not only the losses, because a GAN loss does not steadily fall the way a classifier loss does.')}
{run('gan_theory')}
{note('With the real data N(0, 1) and the generator N(m, 1), the best discriminator scores x = 0 as 0.500 when m = 0, 0.622 when m = 1 and 0.989 when m = 3. The GAN value V(D*, G) matches &minus;ln 4 + 2 JS exactly: &minus;1.3863 at m = 0, &minus;1.1635 at m = 1, &minus;0.3327 at m = 3 and 0.0000 at m = 10, where JS reaches its ceiling ln 2 = 0.6931.', 'exam')}
{table(['Problem', 'What you see', 'Common fixes'], [
    ['Saturating generator loss', 'Generator barely changes early on', 'Non saturating loss &minus;ln D(G(z))'],
    ['Mode collapse', 'Many samples look the same', 'Minibatch features, Wasserstein loss, unrolled GANs'],
    ['Oscillation', 'Samples keep changing, losses swing', 'Lower learning rates, two time scale updates (TTUR), averaging generator weights'],
    ['Discriminator too strong', 'D near 100 percent, G stuck', 'Gradient penalty, spectral normalisation, label smoothing, data augmentation (DiffAugment, ADA)']])}
{fxs(fx('Optimal discriminator', 'D*(x) = p<sub>data</sub>(x) / (p<sub>data</sub>(x) + p<sub>g</sub>(x))', 'For a fixed generator.', key=True),
     fx('Value at the optimum', 'V(D*, G) = &minus;ln 4 + 2 JS(p<sub>data</sub> || p<sub>g</sub>)', 'Smallest, &minus;ln 4, when p<sub>g</sub> = p<sub>data</sub>.', key=True),
     fx('Gradient on the logit t', 'saturating: &minus;D, &nbsp; non saturating: &minus;(1 &minus; D)', 'D = &sigma;(t).', key=True))}
''', kw=['optimal discriminator', 'Jensen Shannon divergence', 'non saturating loss', 'mode collapse', 'vanishing gradient', 'minibatch standard deviation', 'training instability'])

K.lesson('wgan', 'Wasserstein GANs and other stable losses', f'''
{src('Arjovsky, Chintala and Bottou, Wasserstein GAN (ICML 2017), Gulrajani and colleagues, Improved training of Wasserstein GANs (NeurIPS 2017), Miyato and colleagues, Spectral normalization (ICLR 2018), and Mao and colleagues, Least squares GANs (ICCV 2017).')}
{wwh('The <b>Wasserstein GAN</b> (WGAN) replaces the discriminator with a <b>critic</b> f that outputs any real number, not a probability. The critic maximises E[f(real)] &minus; E[f(fake)], and the generator maximises E[f(fake)]. If f is kept smooth (<b>1 Lipschitz</b>), this difference estimates the <b>Wasserstein distance</b>, also called the earth mover&rsquo;s distance: the least total work needed to move one pile of probability onto the other.',
     'Real images lie on thin surfaces in pixel space, so the real and generated distributions often do not overlap at all. Then the JS divergence is stuck at ln 2 and gives no direction to improve, while the Wasserstein distance still shrinks as the fakes move closer. The WGAN critic value also tracks sample quality, which makes training easier to monitor.',
     'Keep the critic smooth with a <b>gradient penalty</b> (WGAN-GP), which adds &lambda;(||&nabla;f(x&#770;)|| &minus; 1)&sup2; at points x&#770; between real and fake samples, or with <b>spectral normalisation</b> of every weight matrix. The original weight clipping works but is crude. Train the critic several times per generator step, often 5.')}
{run('gan_distances')}
{note('Shifting a uniform distribution on [0, 1] to the right, the JS divergence is 0.345 at a shift of 0.5 and then stuck at 0.693 for every shift of 1 or more, once the two stop overlapping. The Wasserstein distance keeps growing with the shift: 0.497, 0.994, 1.996, 4.997 and 9.996.', 'exam')}
{fxs(fx('Wasserstein distance', 'W(p, q) = inf<sub>&gamma;</sub> E<sub>(x, y)~&gamma;</sub>||x &minus; y||', 'Cheapest way to move p onto q.', key=True),
     fx('Kantorovich Rubinstein duality', 'W(p, q) = sup<sub>||f||<sub>L</sub> &le; 1</sub> E<sub>p</sub>[f(x)] &minus; E<sub>q</sub>[f(x)]', 'What the critic estimates.', key=True),
     fx('Gradient penalty', '&lambda; E[(||&nabla;<sub>x&#770;</sub> f(x&#770;)|| &minus; 1)&sup2;], &nbsp; &lambda; = 10', 'Gulrajani and colleagues (2017).', key=True),
     fx('Least squares GAN', 'L<sub>D</sub> = (D(x) &minus; 1)&sup2; + D(G(z))&sup2;', 'Mao and colleagues (2017).'))}
''', kw=['Wasserstein GAN', 'WGAN', 'critic', 'earth mover distance', 'Lipschitz', 'gradient penalty', 'WGAN-GP', 'spectral normalisation'])

K.lesson('family', 'DCGAN, conditional GANs, StyleGAN, and measuring quality', f'''
{src('Radford, Metz and Chintala, DCGAN (ICLR 2016), Mirza and Osindero, Conditional GANs (2014), Isola and colleagues, pix2pix (CVPR 2017), Zhu and colleagues, CycleGAN (ICCV 2017), Karras and colleagues, StyleGAN (CVPR 2019), and Heusel and colleagues, GANs trained by a two time scale update rule converge to a local Nash equilibrium (NeurIPS 2017).')}
{wwh('<b>DCGAN</b> uses transposed convolutions in the generator and strided convolutions in the discriminator, with batch normalisation. A <b>conditional GAN</b> feeds a label or an input image to both networks, so you can ask for a specific class or translate one image into another (<b>pix2pix</b> with paired examples, <b>CycleGAN</b> with unpaired ones). <b>StyleGAN</b> maps z to a style vector that controls each resolution of the image. The <b>Fr&eacute;chet Inception Distance</b> (FID) measures quality and variety together.',
     'Plain GANs give random samples. Conditioning gives control, which is what applications need: turn a sketch into a photo, a day scene into night, a map into a satellite view. A number like FID is needed because people cannot inspect millions of samples, and the GAN loss itself does not say how good the images are.',
     'To compute FID, pass real and generated images through a pretrained Inception network, fit a Gaussian (mean and covariance) to each set of features, and compute the Fr&eacute;chet distance between the two Gaussians. Lower is better. Use at least 10,000 samples, because FID is biased for small sets, and report it with precision and recall when variety matters.')}
{run('fid')}
{note('Using PCA features of the digits in place of Inception features, other real digits score 0.03 against the test digits. Adding noise with spread 0.2 gives 0.10 and spread 0.4 gives 0.33. A set of only real 1s scores 3.23, even though every image in it is a real digit: FID punishes mode collapse because the feature covariance is wrong. The average image repeated scores 4.04.', 'exam')}
{table(['Model', 'Idea', 'Known for'], [
    ['DCGAN (2016)', 'All convolutional generator and discriminator', 'First stable image GAN recipe'],
    ['Conditional GAN (2014)', 'Label given to G and D', 'Class controlled samples'],
    ['pix2pix (2017)', 'Conditional GAN plus an L1 loss on paired images', 'Sketch to photo, maps to aerial views'],
    ['CycleGAN (2017)', 'Two generators and a cycle consistency loss', 'Horses to zebras without paired data'],
    ['StyleGAN (2019 to 2021)', 'Style vector controls each resolution', 'Photorealistic faces, editing by style'],
    ['GAN discriminators today', 'Adversarial loss inside other models', 'Super resolution, decoders of latent diffusion']])}
{fxs(fx('Fr&eacute;chet distance of Gaussians', 'FID = ||&mu;<sub>r</sub> &minus; &mu;<sub>g</sub>||&sup2; + Tr(&Sigma;<sub>r</sub> + &Sigma;<sub>g</sub> &minus; 2(&Sigma;<sub>r</sub>&Sigma;<sub>g</sub>)<sup>1/2</sup>)', 'Lower is better.', key=True),
     fx('Cycle consistency', 'L<sub>cyc</sub> = ||F(G(x)) &minus; x||<sub>1</sub> + ||G(F(y)) &minus; y||<sub>1</sub>', 'CycleGAN.', key=True),
     fx('Transposed convolution size', 'out = (in &minus; 1) &times; stride &minus; 2 &times; pad + kernel', 'Upsampling in DCGAN.', key=True))}
{link('computer-vision', 'Want more on image generation and translation?', 'The Computer Vision subject covers convolutional networks, encoders and decoders and modern vision models in depth.', 'Open Computer Vision')}
''', kw=['DCGAN', 'conditional GAN', 'pix2pix', 'CycleGAN', 'StyleGAN', 'FID', 'Frechet Inception Distance', 'transposed convolution'])

K.lesson('versus', 'GANs compared with other generative models', f'''
{versus('Ways to generate new data', ['', 'GAN', 'VAE', 'Diffusion model', 'Autoregressive model'], [
    ['How it learns', 'Generator fools a discriminator', 'Maximise the ELBO', 'Learn to remove noise step by step', 'Predict the next piece'],
    ['Sample quality', 'Very sharp', 'Often blurry', 'Very sharp', 'Sharp'],
    ['Variety (mode coverage)', 'Can collapse', 'Good', 'Good', 'Good'],
    ['Sampling speed', 'One pass, fast', 'One pass, fast', 'Many steps, slow', 'One step per token, slow'],
    ['Likelihood available', 'No', 'A lower bound', 'A lower bound', 'Exact'],
    ['Training', 'Unstable, needs care', 'Stable', 'Stable', 'Stable']],
    'GANs when you need fast, sharp samples in a narrow domain, VAEs for smooth latent spaces, diffusion for the best quality and variety, and autoregressive models for text and exact likelihoods.')}
''', kw=['GAN vs VAE', 'GAN vs diffusion', 'autoregressive', 'mode coverage'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('GAN value', 'V(D, G) = E<sub>data</sub>[ln D(x)] + E<sub>z</sub>[ln(1 &minus; D(G(z)))]', 'D maximises, G minimises.', key=True),
     fx('Optimal D', 'D*(x) = p<sub>data</sub> / (p<sub>data</sub> + p<sub>g</sub>)', 'Pointwise maximum.', key=True),
     fx('JS divergence', 'JS(p || q) = &frac12; KL(p || m) + &frac12; KL(q || m), &nbsp; m = &frac12;(p + q)', 'Between 0 and ln 2.', key=True),
     fx('WGAN critic', 'max<sub>f 1 Lipschitz</sub> E<sub>data</sub>[f(x)] &minus; E<sub>z</sub>[f(G(z))]', 'Estimates W(p<sub>data</sub>, p<sub>g</sub>).', key=True),
     fx('FID', '||&mu;<sub>r</sub> &minus; &mu;<sub>g</sub>||&sup2; + Tr(&Sigma;<sub>r</sub> + &Sigma;<sub>g</sub> &minus; 2(&Sigma;<sub>r</sub>&Sigma;<sub>g</sub>)<sup>1/2</sup>)', 'In one dimension: (&mu;<sub>r</sub> &minus; &mu;<sub>g</sub>)&sup2; + (&sigma;<sub>r</sub> &minus; &sigma;<sub>g</sub>)&sup2;.'))}
{steps('Worked example: why the best discriminator is p<sub>data</sub> / (p<sub>data</sub> + p<sub>g</sub>)', [
    'Write the value as one integral over x, using p<sub>g</sub> for the distribution of G(z).',
    eq('V = &int; [ p<sub>data</sub>(x) ln D(x) + p<sub>g</sub>(x) ln(1 &minus; D(x)) ] dx'),
    'At each x, D(x) is a free number y in (0, 1). Maximise a ln y + b ln(1 &minus; y) with a = p<sub>data</sub>(x) and b = p<sub>g</sub>(x).',
    eq('d/dy: a / y &minus; b / (1 &minus; y) = 0 &nbsp; so &nbsp; y = a / (a + b)'),
    'Put D* back into V. Each log term becomes a KL divergence to the mixture m = &frac12;(p<sub>data</sub> + p<sub>g</sub>), plus a constant.',
    eq('V(D*, G) = &minus;ln 4 + KL(p<sub>data</sub> || m) + KL(p<sub>g</sub> || m) = &minus;ln 4 + 2 JS(p<sub>data</sub> || p<sub>g</sub>)'),
    'JS is 0 only when the two distributions are equal, so the best generator copies the data exactly and then D* = &frac12; everywhere.'])}
{deep('Game theory, convergence and what GANs really learn', '<p>A GAN is a two player game, and gradient descent on both players looks for a <b>Nash equilibrium</b>, not a minimum. Simple games such as min<sub>x</sub> max<sub>y</sub> xy make plain simultaneous gradient steps circle around the equilibrium or spiral away, which is the oscillation seen in practice. Mescheder, Geiger and Nowozin (ICML 2018) showed that unregularised GANs need not converge and that a gradient penalty on real data (R1) makes training locally convergent. Heusel and colleagues (2017) proved convergence for two time scale updates (TTUR). Arora and colleagues (ICML 2017) showed that a discriminator with limited capacity cannot detect a generator that memorised a small set of samples, so a GAN can win the game without learning the full distribution, which the birthday paradox test measures. f-GANs (Nowozin and colleagues 2016) show that changing the loss lets a GAN minimise any f divergence, with the original GAN as the JS case.</p>')}
''', kw=['optimal discriminator derivation', 'JS divergence', 'Nash equilibrium', 'TTUR', 'R1 penalty', 'f-GAN'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>One network makes fakes and another tries to spot them. As each gets better, the fakes become hard to tell from the real thing.</p>',
    '<p>Write the GAN losses, train a small GAN, recognise saturation and mode collapse, and use conditional GANs for controlled generation.</p>',
    '<p>Derive the optimal discriminator and the JS result, explain why the Wasserstein loss and gradient penalties help, and evaluate models with FID.</p>',
    '<p>Study the game dynamics and convergence, divergence families such as f-GANs, memorisation and generalisation, and GAN losses inside modern diffusion and super resolution systems.</p>')}
{grow('Explain the generator and discriminator game.',
      'Train and debug GANs with stable losses.',
      'Analyse GAN objectives and their convergence.')}
''', kw=['beginner', 'expert', 'game dynamics'])

lc(292, 'Nim Game', 'nim-game', 'e', 'You lose exactly when the number of stones is a multiple of 4', 'Whatever you take (1 to 3), your opponent can make the total of the round 4. So multiples of 4 are losing positions for the player to move. Two players who each play their best against the other is the same setting as the GAN game.', r"""
def can_win_nim(n):
    return n % 4 != 0
""", [('can_win_nim(4)', False), ('can_win_nim(1)', True), ('can_win_nim(7)', True)])
lc(486, 'Predict the Winner', 'predict-the-winner', 'm', 'Minimax on intervals: best lead = max(take left minus their best lead, take right minus their best lead)', 'Let lead(i, j) be the most the player to move can get ahead by on nums[i..j]. Taking an end gives that number minus the opponent&rsquo;s best lead on what remains. This is a minimax game: each player assumes the other plays as well as possible, as the generator and the discriminator do.', r"""
def predict_the_winner(nums):
    n = len(nums)
    diff = nums[:]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            diff[i] = max(nums[i] - diff[i + 1], nums[j] - diff[i])
    return diff[0] >= 0
""", [('predict_the_winner([1, 5, 2])', False), ('predict_the_winner([1, 5, 233, 7])', True)])
lc(877, 'Stone Game', 'stone-game', 'm', 'Same interval minimax as Predict the Winner (and the first player always wins with an even count)', 'Compute the best lead of the player to move on piles[i..j] from shorter intervals. With an even number of piles and an odd total, the first player can always take all the even positions or all the odd ones, so the answer is always true, but the dynamic programming shows why.', r"""
def stone_game(piles):
    n = len(piles)
    lead = piles[:]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            lead[i] = max(piles[i] - lead[i + 1], piles[j] - lead[i])
    return lead[0] > 0
""", [('stone_game([5, 3, 4, 5])', True), ('stone_game([3, 7, 2, 3])', True)])
lc(375, 'Guess Number Higher or Lower II', 'guess-number-higher-or-lower-ii', 'm', 'cost(lo, hi) = min over guesses g of g + max(cost(lo, g minus 1), cost(g + 1, hi))', 'You pick the guess (min) and the number is chosen to hurt you most (max). Memoise the cost of every range. The min over your choices of the max over the opponent&rsquo;s choices is exactly the min over G of the max over D in the GAN value.', r"""
from functools import lru_cache


def get_money_amount(n):
    @lru_cache(maxsize=None)
    def cost(lo, hi):
        if lo >= hi:
            return 0
        return min(g + max(cost(lo, g - 1), cost(g + 1, hi)) for g in range(lo, hi + 1))
    return cost(1, n)
""", [('get_money_amount(10)', 16), ('get_money_amount(1)', 0), ('get_money_amount(2)', 1)])
lc(1406, 'Stone Game III', 'stone-game-iii', 'h', 'best[i] = max over taking 1, 2 or 3 stones of (stones taken minus best[next])', 'Work backwards from the end. The player to move takes 1 to 3 values and then the opponent faces the rest, so the lead is what you took minus the opponent&rsquo;s best lead. The sign of best[0] names the winner.', r"""
def stone_game_iii(values):
    n = len(values)
    best = [0] * (n + 3)
    for i in range(n - 1, -1, -1):
        take, best[i] = 0, float('-inf')
        for k in range(3):
            if i + k < n:
                take += values[i + k]
                best[i] = max(best[i], take - best[i + k + 1])
    if best[0] > 0:
        return 'Alice'
    return 'Bob' if best[0] < 0 else 'Tie'
""", [('stone_game_iii([1, 2, 3, 7])', 'Bob'), ('stone_game_iii([1, 2, 3, -9])', 'Alice'), ('stone_game_iii([1, 2, 3, 6])', 'Tie')])

K.lesson('leetcode', 'LeetCode practice', leet('<p>A GAN is a two player game where each side plays its best against the other. These problems practise exactly that kind of reasoning: winning and losing positions, minimax over intervals, and the min over your choices of the max over the opponent&rsquo;s. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'game theory', 'minimax', 'dynamic programming'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>GAN</b> trains a <b>generator</b> to turn noise into fakes and a <b>discriminator</b> to tell real from fake, alternating their updates in a <b>minimax</b> game.',
    'The best discriminator is p<sub>data</sub> / (p<sub>data</sub> + p<sub>g</sub>), and then the generator lowers the <b>JS divergence</b>. The ideal end point is p<sub>g</sub> = p<sub>data</sub> with D = &frac12;.',
    'Use the <b>non saturating</b> loss &minus;ln D(G(z)), because ln(1 &minus; D) gives almost no gradient while the fakes are bad. Fight <b>mode collapse</b> with batch level features and stable losses.',
    'The <b>Wasserstein GAN</b> critic estimates the earth mover&rsquo;s distance, which keeps giving gradients when the distributions do not overlap. Keep the critic smooth with a <b>gradient penalty</b> or spectral normalisation.',
    '<b>Conditional</b> GANs (pix2pix, CycleGAN) give control, <b>StyleGAN</b> gives photorealistic faces, and <b>FID</b> compares feature means and covariances to score quality and variety.'],
    'Deep learning 3.3 covers diffusion models, which now lead image generation.')}
{files('Three tasks: the discriminator loss, both generator losses, and the Fr&eacute;chet distance in one dimension.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In a GAN, the generator', ['Classifies images', 'Turns random noise into fake examples', 'Computes the loss', 'Labels the data'], 1, 'Noise in, fake out.', 'It never sees real data directly.')
K.quiz('e', 'The discriminator outputs', ['A new image', 'The probability that its input is real', 'The noise vector', 'A class label for ten classes'], 1, 'Real or fake.', 'A binary classifier.')
K.quiz('e', 'During the generator update, the discriminator', ['Is deleted', 'Is kept fixed while gradients pass through it', 'Is trained harder', 'Is replaced by labels'], 1, 'Frozen, but differentiable.', 'Gradients flow from D into G.')
K.quiz('e', 'Mode collapse means the generator', ['Crashes', 'Produces only a few kinds of output', 'Becomes a discriminator', 'Outputs noise'], 1, 'Little variety.', 'Each fake is judged on its own.')
K.quiz('m', 'For a fixed generator, the best discriminator is', ['Always 0.5', 'p<sub>data</sub>(x) / (p<sub>data</sub>(x) + p<sub>g</sub>(x))', 'p<sub>g</sub>(x)', '1 for every x'], 1, 'Maximise pointwise.', 'Goodfellow and colleagues (2014).')
K.quiz('m', 'With the best discriminator, the generator minimises', ['The mean squared error', 'The Jensen Shannon divergence between data and generated distributions', 'The number of parameters', 'The KL to a Gaussian'], 1, 'V = &minus;ln 4 + 2 JS.', 'Zero only when they match.')
K.quiz('m', 'Why use &minus;ln D(G(z)) for the generator instead of ln(1 &minus; D(G(z)))?', ['It is cheaper', 'It gives strong gradients when D confidently rejects the fakes', 'It removes the discriminator', 'It makes D linear'], 1, 'Push 1 &minus; D instead of D.', 'The original loss saturates early.')
K.quiz('m', 'A conditional GAN', ['Has no discriminator', 'Gives a label or input image to both networks so you control what is generated', 'Only works on text', 'Uses no noise'], 1, 'Condition on y.', 'pix2pix and CycleGAN build on it.')
K.quiz('m', 'FID compares', ['Pixel values directly', 'Means and covariances of deep features of real and generated images', 'File sizes', 'Discriminator losses'], 1, 'Fr&eacute;chet distance of Gaussians.', 'Lower is better.')
K.quiz('h', 'A WGAN critic differs from a GAN discriminator because it', ['Outputs a probability', 'Outputs any real number and must stay 1 Lipschitz', 'Has no weights', 'Sees only fakes'], 1, 'Critic, not classifier.', 'It estimates the Wasserstein distance.')
K.quiz('h', 'When real and generated distributions do not overlap, the JS divergence', ['Is zero', 'Is stuck at ln 2 and gives no useful gradient', 'Becomes negative', 'Equals the Wasserstein distance'], 1, 'Saturates.', 'The Wasserstein distance still shrinks as they approach.')
K.quiz('h', 'CycleGAN can translate horses to zebras without paired images because of', ['Labels', 'A cycle consistency loss: translating there and back should give the original', 'A bigger discriminator', 'Weight clipping'], 1, 'F(G(x)) &asymp; x.', 'Zhu and colleagues (2017).')
K.quiz('x', 'In the style of a Stanford CS236 exam: at the global optimum of the original GAN game, the value V(D*, G*) is', ['0', '&minus;ln 4', 'ln 2', '1'], 1, 'JS = 0 there.', 'D* = &frac12; everywhere.')
K.quiz('x', 'In the style of a CMU deep learning exam: plain simultaneous gradient steps on min<sub>x</sub> max<sub>y</sub> xy', ['Converge quickly', 'Circle around or spiral away from the equilibrium', 'Stop at x = 1', 'Need no learning rate'], 1, 'Rotational dynamics.', 'Why GAN training can oscillate.')

K.calc('e', 'The discriminator gives a real image D = 0.8. Its binary cross entropy loss for this example?', '0.2231', '&minus;ln D for a real example.', ['Real label 1, so the loss is &minus;ln D(x).', 'ln 0.8 = &minus;0.2231.', eq('&minus;ln 0.8 = 0.2231')], check=0.2231, tol=0.0005)
K.calc('e', 'D(real) = 0.9 and D(fake) = 0.2. Discriminator loss &minus;ln D(real) &minus; ln(1 &minus; D(fake))?', '0.3285', 'Add both terms.', ['&minus;ln 0.9 = 0.1054.', '&minus;ln(1 &minus; 0.2) = &minus;ln 0.8 = 0.2231.', eq('0.1054 + 0.2231 = 0.3285')], check=0.3285, tol=0.0005)
K.calc('m', 'At some x, p<sub>data</sub>(x) = 0.3 and p<sub>g</sub>(x) = 0.1. Best discriminator D*(x)?', '0.75', 'p<sub>data</sub> / (p<sub>data</sub> + p<sub>g</sub>).', ['Numerator 0.3.', 'Denominator 0.3 + 0.1 = 0.4.', eq('0.3 / 0.4 = 0.75')], check=0.75)
K.calc('m', 'GAN value V(D*, G) at the global optimum, to 4 decimals?', '−1.3863', '&minus;ln 4 + 2 JS with JS = 0.', ['p<sub>g</sub> = p<sub>data</sub>, so JS = 0 and D* = &frac12;.', 'V = ln &frac12; + ln &frac12; = &minus;ln 4.', eq('&minus;ln 4 = &minus;1.3863')], check=-1.3863, tol=0.0005)
K.calc('m', 'D(G(z)) = 0.05. How many times larger is the non saturating push (1 &minus; D) than the saturating push (D)?', '19', 'Divide the two.', ['Non saturating: 1 &minus; 0.05 = 0.95.', 'Saturating: 0.05.', eq('0.95 / 0.05 = 19')], check=19)
K.calc('m', 'Non saturating generator loss &minus;ln D(G(z)) when D(G(z)) = 0.1?', '2.3026', '&minus;ln 0.1.', ['ln 0.1 = &minus;2.3026.', 'Change the sign.', eq('&minus;ln 0.1 = 2.3026')], check=2.3026, tol=0.0005)
K.calc('h', 'With the best discriminator, V(D*, G) = &minus;1.0. JS divergence between data and generator?', '0.1931', 'V = &minus;ln 4 + 2 JS.', ['2 JS = V + ln 4 = &minus;1.0 + 1.3863 = 0.3863.', 'Divide by 2.', eq('JS = 0.3863 / 2 = 0.1931')], check=0.1931, tol=0.0005)
K.calc('h', 'Wasserstein distance between the equal weight point sets {0, 1} and {2, 4}?', '2.5', 'In one dimension, match sorted points.', ['Match 0 with 2 (distance 2) and 1 with 4 (distance 3).', 'Each point carries weight &frac12;.', eq('(2 + 3) / 2 = 2.5')], check=2.5)
K.calc('h', 'One dimensional FID between N(1, 1) and N(3, 4) (variances 1 and 4)?', '5', '(&mu;<sub>1</sub> &minus; &mu;<sub>2</sub>)&sup2; + &sigma;<sub>1</sub>&sup2; + &sigma;<sub>2</sub>&sup2; &minus; 2&sigma;<sub>1</sub>&sigma;<sub>2</sub>.', ['Mean term (1 &minus; 3)&sup2; = 4.', 'Covariance term 1 + 4 &minus; 2&radic;(1 &times; 4) = 5 &minus; 4 = 1.', eq('4 + 1 = 5')], check=5)
K.calc('x', 'In the style of a DCGAN design question: a transposed convolution with kernel 4, stride 2 and padding 1 takes a 4 &times; 4 map. Output size?', '8', '(in &minus; 1) &times; stride &minus; 2 &times; pad + kernel.', ['(4 &minus; 1) &times; 2 = 6.', '6 &minus; 2 &times; 1 = 4.', eq('4 + 4 = 8')], check=8)

K.assign('discriminator_loss', 'e', 'The discriminator loss',
         '<p>Write <code>discriminator_loss(d_real, d_fake)</code> that takes the discriminator&rsquo;s scores on a list of real examples and a list of fake examples, and returns the average of &minus;ln D(real) over the real list plus the average of &minus;ln(1 &minus; D(fake)) over the fake list, rounded to 4 decimals.</p>',
         """
def discriminator_loss(d_real, d_fake):
    # your code here
    pass
""", [('discriminator_loss([0.9], [0.2])', 0.3285), ('discriminator_loss([0.5, 0.5], [0.5, 0.5])', 1.3863), ('discriminator_loss([0.99], [0.01])', 0.0201)],
         """
import math


def discriminator_loss(d_real, d_fake):
    real_part = sum(-math.log(d) for d in d_real) / len(d_real)
    fake_part = sum(-math.log(1 - d) for d in d_fake) / len(d_fake)
    return round(real_part + fake_part, 4)
""", 'Average &minus;ln d over the real scores and &minus;ln(1 &minus; d) over the fake scores, then add the two averages.', '<p>At the ideal end point every score is &frac12; and this loss is 2 ln 2 = 1.3863, which is the second test.</p>')
K.assign('generator_loss', 'm', 'Saturating and non saturating generator losses',
         '<p>Write <code>generator_loss(d_fake, kind)</code>. For kind <code>\'ns\'</code> return the average of &minus;ln d, and for kind <code>\'sat\'</code> return the average of ln(1 &minus; d), over the list of scores, rounded to 4 decimals.</p>',
         """
def generator_loss(d_fake, kind):
    # your code here
    pass
""", [("generator_loss([0.1], 'ns')", 2.3026), ("generator_loss([0.1], 'sat')", -0.1054), ("generator_loss([0.5, 0.5], 'ns')", 0.6931)],
         """
import math


def generator_loss(d_fake, kind):
    if kind == 'ns':
        terms = [-math.log(d) for d in d_fake]
    else:
        terms = [math.log(1 - d) for d in d_fake]
    return round(sum(terms) / len(terms), 4)
""", 'Pick the formula from kind, apply it to each score and average.', '<p>Both losses are minimised by making d large, but at d = 0.1 the non saturating loss is far steeper on the logit scale, which is why it trains faster.</p>')
K.assign('frechet_1d', 'm', 'The Fr&eacute;chet distance in one dimension',
         '<p>Write <code>frechet_1d(mu1, var1, mu2, var2)</code> that returns (mu1 &minus; mu2)&sup2; + var1 + var2 &minus; 2&radic;(var1 &times; var2), rounded to 4 decimals. This is FID with one feature.</p>',
         """
def frechet_1d(mu1, var1, mu2, var2):
    # your code here
    pass
""", [('frechet_1d(1, 1, 3, 4)', 5.0), ('frechet_1d(0, 1, 0, 1)', 0.0), ('frechet_1d(2, 0.25, 2, 1)', 0.25)],
         """
import math


def frechet_1d(mu1, var1, mu2, var2):
    return round((mu1 - mu2) ** 2 + var1 + var2 - 2 * math.sqrt(var1 * var2) + 0.0, 4)
""", 'Square the gap between the means, add both variances and subtract twice the square root of their product.', '<p>The second term equals (&sigma;<sub>1</sub> &minus; &sigma;<sub>2</sub>)&sup2;, so a generator with the right mean but too little spread, as in mode collapse, still gets a positive score.</p>')

K.must('GAN game', 'Generator: noise to fake. Discriminator: real or fake. Alternate updates, min over G of max over D.')
K.must('Losses', 'L<sub>D</sub> = &minus;ln D(x) &minus; ln(1 &minus; D(G(z))). Generator: &minus;ln D(G(z)) (non saturating).')
K.must('Theory', 'D* = p<sub>data</sub> / (p<sub>data</sub> + p<sub>g</sub>). V(D*, G) = &minus;ln 4 + 2 JS. Optimum p<sub>g</sub> = p<sub>data</sub>, D = &frac12;.')
K.must('Failures', 'Saturation, mode collapse, oscillation, D too strong. Fixes: minibatch features, TTUR, penalties, augmentation.')
K.must('WGAN', 'Critic outputs real numbers, estimates earth mover distance. Keep 1 Lipschitz: gradient penalty or spectral norm.')
K.must('Variants and FID', 'DCGAN, conditional, pix2pix, CycleGAN (cycle loss), StyleGAN. FID: feature means and covariances, lower is better.')

T = K.topic(
    slug='dl-gans', topic='dl-gans', step=(3, 'Generative models', 'dl-s3', 'Networks that create new data: autoencoders and variational autoencoders, generative adversarial networks, and diffusion models.', 'Advanced'),
    title='Generative adversarial networks', short='GANs', badge='3.2', minutes=55,
    lead='Train a generator against a discriminator: the minimax game, the best discriminator and the JS divergence, the non saturating loss, mode collapse, Wasserstein GANs, conditional GANs and StyleGAN, and FID.',
    desc='GAN, generative adversarial network, generator, discriminator, minimax, optimal discriminator, Jensen Shannon divergence, non saturating loss, mode collapse, Wasserstein GAN, critic, gradient penalty, spectral normalisation, DCGAN, conditional GAN, pix2pix, CycleGAN, StyleGAN, FID.',
    summary='The GAN game, its theory and failures, Wasserstein GANs, conditional GANs and StyleGAN, and FID.',
    keywords=['GAN', 'generator', 'discriminator', 'minimax', 'mode collapse', 'Wasserstein GAN', 'gradient penalty', 'conditional GAN', 'StyleGAN', 'FID'],
    recap='<p>Let one network make fakes and another judge them, and both improve until the fakes match the data. Choose the loss with care, give the judge a view of variety, and measure the result with FID.</p>',
    added='2026-11-14', leet=leet_items())
