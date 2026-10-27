# Chapter 9: target assignment, the per-anchor objective, MAE, MSE and Huber for boxes, normalisation,
# class imbalance, entropy and cross entropy, focal loss, bias initialisation and the architecture versus loss view.
# Source: lectures 5 and 6, chapters 5 to 8.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('huber', r'''
# Squared error versus Huber (Smooth L1) on four box errors
errors = [0.2, 0.3, 0.4, float(input("Error of the bad box: "))]

def huber(e, d=1.0):
    return 0.5 * e * e if abs(e) <= d else d * (abs(e) - 0.5 * d)

sq = [e * e for e in errors]
hu = [huber(e) for e in errors]
print("squared:", [round(v, 3) for v in sq])
print("huber:  ", [round(v, 3) for v in hu])
print("bad box / rest, squared:", round(sq[3] / sum(sq[:3]), 1))
print("bad box / rest, huber:  ", round(hu[3] / sum(hu[:3]), 1))
''', stdin='10\n')

K.code('focal', r'''
# Who owns the loss: easy background or hard objects?
from math import log

gamma = float(input("Focusing parameter gamma (0 = cross entropy): "))
n_easy, p_easy = 100000, 0.99
n_hard, p_hard = 10, 0.10

def focal(pt, g):
    return -((1 - pt) ** g) * log(pt)

easy = n_easy * focal(p_easy, gamma)
hard = n_hard * focal(p_hard, gamma)
print("easy total:", round(easy, 4))
print("hard total:", round(hard, 4))
print("share of easy background:", round(100 * easy / (easy + hard), 2), "%")
''', stdin='2\n')

K.code('entropy', r'''
# Entropy of a coin, and binary cross entropy for one prediction
from math import log2, log

p = float(input("Probability of heads: "))
H = 0.0
for q in (p, 1 - p):
    if q > 0:
        H -= q * log2(q)                 # average surprise in bits
print("entropy:", round(H, 3), "bits")

y, pred = 1, 0.8                         # true label and model probability
bce = -(y * log(pred) + (1 - y) * log(1 - pred))
print("binary cross entropy:", round(bce, 3))
''', stdin='0.9\n')

K.lesson('targets', 'Giving every anchor a target', f'''
<p>Detection is supervised learning. Annotators drew the true boxes and classes, but there are only a few of them, while the network makes a prediction for ten thousand or more anchors. <b>Target assignment</b> decides which true box, if any, each anchor must learn.</p>
<ul>
<li>Match each anchor to the true box it overlaps most, measured by IoU.</li>
<li>If that IoU is high enough the anchor is <b>positive</b>: it gets the object\'s class and a box target.</li>
<li>If it is low the anchor is <b>background</b> (class 0) and gets no box target.</li>
<li>Anchors in between are <b>ignored</b>, so borderline cases do not confuse training.</li>
</ul>
{viz('assign')}
{table(['Detector', 'Positive', 'Background'], [['RetinaNet', 'IoU ≥ 0.5', 'IoU < 0.4'], ['Faster R-CNN region proposals', 'IoU > 0.7 (or the best anchor for an object)', 'IoU < 0.3']])}
<p>A student asked whether Manhattan distance could replace Euclidean distance for matching. The lecturer said any distance can be used if it suits the problem. In practice most detectors use IoU because it is <b>scale invariant</b>: a 5 pixel centre error is huge for a 20 pixel box and tiny for a 500 pixel box, and IoU sees that difference while a plain distance does not.</p>
<h3>The training objective</h3>
{fx('Per-anchor loss', '<i>L</i> = ' + frac('1', '<i>N</i>') + ' Σ<sub>anchors</sub> [ α <i>L</i><sub>cls</sub> + β δ(positive) <i>L</i><sub>loc</sub> ]', 'δ is 1 for a positive anchor and 0 otherwise, so background anchors only pay the class loss. <i>N</i> is often the number of positive anchors.', key=True)}
<p>Two losses, one for what and one for where, added together. The rest of this chapter is about choosing each one well: a box loss that is not thrown by outliers, and a class loss that is not swamped by background.</p>
''', kw=['target assignment', 'positive anchor', 'negative anchor', 'background', 'ignored anchor', 'IoU threshold', 'Euclidean', 'Manhattan', 'scale invariant', 'training objective', 'multi-task loss'])

K.lesson('boxloss', 'Box loss: MSE, MAE and Huber', f'''
{fxs(
    fx('Mean squared error', 'MSE = ' + frac('1', '<i>n</i>') + ' Σ (<i>ŷ</i><sub><i>i</i></sub> − <i>y</i><sub><i>i</i></sub>)²', 'Squares the error, so large errors are punished far more: 0.1² = 0.01 but 10² = 100.'),
    fx('Mean absolute error', 'MAE = ' + frac('1', '<i>n</i>') + ' Σ |<i>ŷ</i><sub><i>i</i></sub> − <i>y</i><sub><i>i</i></sub>|', 'Grows linearly, so outliers matter less. Its best constant guess is the median, MSE\'s is the mean.'),
    fx('Huber (Smooth L1)', 'Huber(<i>e</i>) = ½<i>e</i>² if |<i>e</i>| ≤ 1, &nbsp; |<i>e</i>| − ½ otherwise', '<i>e</i> is prediction minus target, not Euler\'s number. The general form uses a threshold δ.', key=True),
    fx('Huber slope', '∂Huber ÷ ∂<i>e</i> = clip(<i>e</i>, −1, 1)', 'Proportional for small errors, capped for large ones.'))}
<h3>Why not plain MSE for boxes?</h3>
<p>The class gave the right instinct: large outliers should not dominate training. The lecturer explained why that matters early on. At the start every box is a rough guess, so MSE hands out huge penalties and the model does not learn smoothly. Her comparison: giving a full exam in the second class, before any introduction. Feedback should be smooth, hence the name smooth L1.</p>
<p>The deeper reason is the gradient. With MSE the push on each box is proportional to its error, so one box with error 10 pushes harder than all the good boxes together, and training becomes unstable. Huber caps the push at 1.</p>
{viz('huber')}
{steps('One bad box among four (the slide example)', [
    'Errors 0.2, 0.3, 0.4 and 10.',
    'Squared: 0.04, 0.09, 0.16 and 100. The good boxes total 0.29, so the bad one contributes 100 ÷ 0.29 ≈ 345 times more.',
    'Huber: 0.02, 0.045, 0.08 and 10 − 0.5 = 9.5.',
    'Gradients: with ½e² they are 0.2, 0.3, 0.4 and 10, so the outlier is 11 times the rest. With Huber they are 0.2, 0.3, 0.4 and 1, only 1.1 times.'])}
{code('huber')}
{deep('Huber is smooth and convex', '<p>At |e| = 1 the two pieces meet: ½ × 1² = 0.5 and 1 − ½ = 0.5. Their slopes also meet: e = 1 and sign(e) = 1. So the loss has no kink, unlike MAE at 0. Its slope clip(e, −1, 1) never decreases, which makes the loss convex with a single minimum at e = 0. A student asked if 0 was a saddle point. It is not: a saddle needs directions going both up and down, and a convex function has none. MSE is the maximum likelihood loss for Gaussian noise, MAE for Laplacian (heavier tailed) noise, and Huber sits between them.</p>')}
<h3>Why normalise</h3>
<p>The lecture example: age runs from 20 to 30 while income runs into crores. Without scaling, income dominates every distance. Min-max scaling maps each feature to [0, 1]: x′ = (x − min) ÷ (max − min). For boxes the same idea appears as anchor relative encoding from the previous chapter: dividing by the anchor size makes a target mean the same thing for tiny and huge objects.</p>
''', kw=['MSE', 'MAE', 'Huber loss', 'Smooth L1', 'outlier', 'gradient', 'clip', 'convex', 'normalisation', 'min-max scaling', 'mean', 'median'])

K.lesson('imbalance', 'Class imbalance and cross entropy', f'''
<p>Picture a beach photo: one third sky, sand at the bottom, two people. Almost every anchor lands on sky, sky, sand, background. Each of these easy negatives has a tiny loss, but there are tens of thousands of them, and together they overwhelm the few anchors that sit on real objects.</p>
{steps('How easy negatives swamp the loss', [
    '100,000 easy background anchors, each classified correctly with p<sub>t</sub> = 0.99. 10 hard object anchors with p<sub>t</sub> = 0.10.',
    'Cross entropy per easy anchor: −ln 0.99 = 0.01005. Total 100,000 × 0.01005 ≈ 1,005.',
    'Per hard anchor: −ln 0.10 = 2.303. Total 10 × 2.303 ≈ 23.',
    'The easy background owns 1,005 ÷ 1,028 ≈ 97.8% of the loss. Training mostly learns to keep saying background.'])}
<h3>Four standard remedies</h3>
{table(['Remedy', 'What it does', 'Example'], [
    ['Subsample negatives', 'Use only some background anchors', 'SSD keeps 3 negatives per positive, the Faster R-CNN RPN samples 256 anchors per image'],
    ['Down-weight negatives', 'Keep all, but give background a smaller weight', 'α-balanced cross entropy'],
    ['Online hard example mining', 'Compute every loss, keep only the hardest negatives', 'OHEM (Shrivastava and colleagues, 2016)'],
    ['Focal loss', 'Reshape the loss so easy examples contribute almost nothing', 'RetinaNet (Lin and colleagues, 2017)']])}
<p>A student asked whether focal loss and hard mining are the same. The lecturer\'s answer: the idea is the same, the process differs. Mining is a selection that keeps or drops each example. Focal loss is a loss function that gives every example a continuous weight. She also compared it with token pruning in large language models, where unimportant tokens are removed to save computation. Pruning deletes, focal loss re-weights.</p>
<h3>Entropy and cross entropy</h3>
{fxs(
    fx('Entropy', '<i>H</i>(<i>p</i>) = −Σ<sub><i>k</i></sub> <i>p</i><sub><i>k</i></sub> log <i>p</i><sub><i>k</i></sub>', 'Average surprise. Highest when all outcomes are equally likely, zero when the outcome is certain. The lecturer\'s picture: a messy table has high entropy, a tidy one low.'),
    fx('Binary cross entropy', 'BCE = −[ <i>y</i> ln <i>p</i> + (1 − <i>y</i>) ln(1 − <i>p</i>) ]', 'If <i>y</i> = 1 only the first term is active, if <i>y</i> = 0 only the second.', key=True),
    fx('p<sub>t</sub> notation', '<i>p</i><sub>t</sub> = <i>p</i> if <i>y</i> = 1, &nbsp; 1 − <i>p</i> if <i>y</i> = 0, &nbsp; so &nbsp; BCE = −ln <i>p</i><sub>t</sub>', 'p<sub>t</sub> is the probability given to the correct answer.'))}
{code('entropy')}
{deep('cross entropy is maximum likelihood', '<p>Model a label as Bernoulli(p): P(y | p) = p<sup>y</sup>(1 − p)<sup>1−y</sup>. Its negative log is exactly BCE, so minimising BCE is maximum likelihood estimation. For distributions, H(p, q) = −Σ p log q = H(p) + KL(p ‖ q). The data fixes H(p), so minimising cross entropy minimises the KL divergence, which is zero only when the model matches the data.</p>')}
''', kw=['class imbalance', 'easy negatives', 'subsampling', 'hard example mining', 'OHEM', 'token pruning', 'entropy', 'cross entropy', 'binary cross entropy', 'BCE', 'p_t', 'KL divergence'])

K.lesson('focal', 'Focal loss and the RetinaNet bias trick', f'''
{fx('Focal loss', 'FL(<i>p</i><sub>t</sub>) = −α<sub>t</sub> (1 − <i>p</i><sub>t</sub>)<sup>γ</sup> ln <i>p</i><sub>t</sub>', 'The factor (1 − p<sub>t</sub>)<sup>γ</sup> goes to 0 for easy, confident examples and stays near 1 for hard ones. γ = 0 gives cross entropy. RetinaNet used γ = 2 and α = 0.25 for the foreground class.', key=True)}
{viz('focal')}
{table(['p<sub>t</sub>', 'CE', 'weight γ = 2', 'FL (γ = 2)'], [
    ['0.1 (hard)', '2.3026', '0.81', '1.8651'],
    ['0.5', '0.6931', '0.25', '0.1733'],
    ['0.9 (easy)', '0.1054', '0.01', '0.0011'],
    ['0.99 (very easy)', '0.0101', '0.0001', '0.000001']])}
<p>With γ = 2 a well classified example at p<sub>t</sub> = 0.9 loses 100 times its cross entropy, while a hard one at 0.1 keeps 81% of it.</p>
{steps('Focal loss rescues the beach photo', [
    'Same setting: 100,000 easy anchors at 0.99, 10 hard ones at 0.10, γ = 2.',
    'Easy: (1 − 0.99)² × 0.01005 = 0.0001 × 0.01005 ≈ 1.005 × 10<sup>−6</sup> each, 0.1005 in total.',
    'Hard: (0.9)² × 2.303 = 0.81 × 2.303 ≈ 1.865 each, 18.65 in total.',
    'The background now owns 0.1005 ÷ 18.75 ≈ 0.54% of the loss, down from 97.8%. The objects drive training.'])}
{code('focal')}
<h3>Starting with the right bias</h3>
<p>A fresh sigmoid classifier outputs p = 0.5 for every anchor. With 100,000 background anchors the first loss is enormous and training can blow up. RetinaNet sets the bias of the last class layer so that every anchor starts out predicting a small prior probability π of being an object.</p>
{fx('Prior bias', 'σ(<i>b</i>) = π &nbsp; ⟹ &nbsp; <i>b</i> = ln ' + frac('π', '1 − π'), 'With π = 0.01: b = −ln 99 ≈ −4.595. Every anchor begins by saying probably background.', key=True)}
{scene('a traffic camera', '<p>A fixed camera at a junction sees mostly road, sky and buildings, with a few cars and cyclists. A detector trained with plain cross entropy learns that saying background is almost always right and starts missing cyclists, the rare and important class. Focal loss and a sensible bias start let the rare objects shape the model.</p>')}
''', kw=['focal loss', 'gamma', 'alpha', 'modulating factor', 'RetinaNet', 'easy examples', 'hard examples', 'prior probability', 'bias initialisation', 'sigmoid'])

K.lesson('axes', 'Architecture or loss: the GAN story', f'''
<p>The lecturer used generative adversarial networks to show how a field moves forward along the design axes from the CNN chapter: architecture, loss and optimisation. A GAN (Goodfellow and colleagues, 2014) trains a generator against a discriminator.</p>
{table(['Step', 'What changed', 'Axis'], [
    ['GAN (2014)', 'The discriminator is a binary classifier: real or fake, sigmoid and cross entropy', 'Original'],
    ['DCGAN (2015)', 'Convolutional layers, batch normalisation, no fully connected layers, which made GANs train stably', 'Architecture'],
    ['WGAN (2017)', 'The loss becomes the Wasserstein (earth mover) distance. The critic outputs a real number, not a probability', 'Loss']])}
{fx('Earth mover distance in 1D', '<i>W</i><sub>1</sub> = Σ<sub><i>i</i></sub> |<i>F</i><sub><i>P</i></sub>(<i>i</i>) − <i>F</i><sub><i>Q</i></sub>(<i>i</i>)|', 'For unit spacing, using the cumulative sums <i>F</i>. It is the least total work to move one pile of earth into the shape of the other.')}
{steps('Earth mover distance by hand', [
    'P = [0.5, 0.5, 0] and Q = [0, 0.5, 0.5] over positions 0, 1, 2.',
    'Cumulative sums: F<sub>P</sub> = [0.5, 1.0, 1.0], F<sub>Q</sub> = [0, 0.5, 1.0].',
    'W<sub>1</sub> = 0.5 + 0.5 + 0 = 1.0.',
    'Check by moving earth: 0.5 from position 0 to 1 costs 0.5, and 0.5 from 1 to 2 costs 0.5. Total 1.0.'])}
<p>Detection followed the same pattern: architecture upgrades such as feature pyramids, and loss upgrades such as Huber and focal loss. The lecturer\'s advice for a thesis: think architecture first, then loss, and choose optimisation only if you enjoy the mathematics.</p>
{ladder(
    '<p>To learn, a detector needs to know how wrong it was. For the box it measures the distance from the right answer, but stops a single crazy guess from shouting over everything else. For the label it learns to ignore the endless easy background and focus on the few real objects.</p>',
    '<p>Anchors are labelled by IoU thresholds. The loss is α L<sub>cls</sub> + β δ L<sub>loc</sub> per anchor. Huber gives quadratic loss near zero and linear beyond, capping gradients at 1. Focal loss −(1 − p<sub>t</sub>)<sup>γ</sup> ln p<sub>t</sub> with γ = 2 cuts the background share in the worked example from 97.8% to 0.54%.</p>',
    '<p>Cross entropy is the Bernoulli negative log likelihood and equals H(p) + KL(p‖q). Huber is the M-estimator between Gaussian and Laplacian noise. The prior bias b = ln(π ÷ (1 − π)) sets the starting loss scale. WGAN replaces Jensen-Shannon divergence by W<sub>1</sub>, which stays informative when distributions do not overlap, and needs a 1-Lipschitz critic.</p>',
    '<p>Box losses moved from coordinates to overlap itself: IoU, GIoU, DIoU and CIoU losses optimise the evaluation measure directly. Assignment became learned or dynamic (ATSS, OTA, the Hungarian matching of DETR), and quality focal and varifocal losses join the class score with localisation quality.</p>')}
''', kw=['architecture', 'loss function', 'optimisation', 'GAN', 'DCGAN', 'WGAN', 'Wasserstein', 'earth mover distance', 'discriminator', 'generator', 'thesis'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'An anchor whose best IoU with any true box is 0.1 is labelled', ['Positive', 'Background', 'Ignored', 'Deleted from the image'], 1,
       'Below the lower threshold.', 'It becomes class 0, background, and gets a class loss but no box loss.')
K.quiz('e', 'Which loss punishes a large error the most?', ['MAE', 'MSE', 'Huber', 'They are equal'], 1,
       'Squaring.', 'MSE squares the error: an error of 10 costs 100, against 10 for MAE and 9.5 for Huber.')
K.quiz('e', 'Focal loss with γ = 0 is the same as', ['MSE', 'Cross entropy', 'Huber', 'Zero'], 1,
       '(1 − p<sub>t</sub>)<sup>0</sup> = 1.', 'The modulating factor becomes 1, leaving −ln p<sub>t</sub>.')
K.quiz('m', 'Why do most detectors match anchors by IoU rather than centre distance?', ['IoU is faster', 'IoU is scale invariant, so the same pixel error counts more for small boxes', 'Distances cannot be computed', 'IoU ignores size'], 1,
       'A 5 pixel error on a 20 pixel box.', 'Overlap automatically compares the error with the object size. A plain distance treats every object the same.')
K.quiz('m', 'Huber loss is preferred for boxes because', ['It is always smaller', 'It is quadratic near zero for precise convergence and linear for large errors, so outliers cannot dominate', 'It needs no gradient', 'It is a classification loss'], 1,
       'Two behaviours in one.', 'Its gradient is clip(e, −1, 1): smooth near the answer, bounded far away.')
K.quiz('m', 'Online hard example mining and focal loss differ because', ['They target different problems', 'Mining selects the hardest examples and drops the rest, focal loss keeps every example with a continuous weight', 'Focal loss only works for boxes', 'Mining is a loss function'], 1,
       'Selection versus weighting.', 'Both stop easy negatives from dominating. One deletes, the other re-weights.')
K.quiz('m', 'What is the entropy of a fair coin in bits?', ['0', '1', '0.5', '2'], 1, '−(½ log₂ ½ + ½ log₂ ½).', 'Each term is ½ × 1, total 1 bit, the maximum for two outcomes.')
K.quiz('h', 'In focal loss, what happens to an easy example with p<sub>t</sub> = 0.9 when γ = 2?', ['Its loss doubles', 'Its loss is multiplied by (0.1)² = 0.01, a 100 times reduction', 'It is deleted', 'Nothing'], 1,
       '(1 − p<sub>t</sub>)<sup>γ</sup>.', '(1 − 0.9)² = 0.01. Hard examples near p<sub>t</sub> = 0.1 keep 81%.')
K.quiz('h', 'Why does RetinaNet set the class bias so the starting probability is 0.01?', ['To speed up inference', 'So the huge number of background anchors start with a small loss instead of each paying −ln 0.5', 'To improve NMS', 'To make boxes larger'], 1,
       'What does p = 0.5 cost for 100,000 background anchors?', 'Each would pay −ln 0.5 ≈ 0.69, about 69,000 in total. Starting near the prior avoids the early blow-up.')
K.quiz('h', 'Minimising cross entropy H(p, q) between data p and model q is equivalent to', ['Maximising entropy', 'Minimising KL(p ‖ q), since H(p, q) = H(p) + KL(p ‖ q)', 'Minimising MSE', 'Nothing useful'], 1,
       'H(p) is fixed by the data.', 'Only the KL term depends on the model, and it is zero exactly when q = p.')
K.quiz('x', 'The lecture said WGAN changed the GAN from classification to regression. What does that mean?', [
    'It predicts boxes', 'The critic outputs an unbounded real score whose difference between real and fake estimates the Wasserstein distance, instead of a probability', 'It removed the generator', 'It uses MSE'], 1,
    'No sigmoid at the end.', 'The discriminator became a critic with a real valued output and a 1-Lipschitz constraint, a loss change rather than an architecture change.')
K.quiz('x', 'With thresholds 0.5 and 0.4, an anchor has IoU 0.45 with a person. It is', ['Positive', 'Background', 'Ignored, contributing no loss', 'Matched to the background box'], 2,
       'Between the two thresholds.', 'Anchors in the grey zone are left out of training so ambiguous cases do not send mixed signals.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the Huber loss (δ = 1) for an error of 0.4?', '0.08', '|e| ≤ 1, so use ½e².',
       ['0.4² = 0.16.', 'Half of it.', eq('Huber = 0.08')], check=0.08)
K.calc('e', 'What is the Huber loss (δ = 1) for an error of 10?', '9.5', '|e| > 1, so use |e| − ½.',
       ['|10| = 10.', '10 − 0.5.', eq('Huber = 9.5'), 'Compare ½e² = 50 and e² = 100.'], check=9.5)
K.calc('e', 'Min-max scale an age of 25 when ages run from 20 to 30.', '0.5', 'x′ = (x − min) ÷ (max − min).',
       ['25 − 20 = 5.', '30 − 20 = 10.', eq('5 ÷ 10 = 0.5')], check=0.5)
K.calc('m', 'Anchor A1 = (30, 20, 110, 180) and person box G1 = (40, 30, 120, 190), both 80 × 160. What is their IoU? Give three decimals.', '0.695', 'Find the overlap rectangle first.',
       ['Overlap x: 40 to 110, width 70. Overlap y: 30 to 180, height 150. Area 10,500.', 'Each box: 80 × 160 = 12,800. Union = 25,600 − 10,500 = 15,100.', eq('IoU = 10,500 ÷ 15,100 ≈ 0.695'), 'Above 0.5, so A1 is a positive for the person.'], check=10500 / 15100, tol=0.0006)
K.calc('m', 'Box errors are 0.2, 0.3, 0.4 and 10. How many times larger is the squared loss of the bad box than the other three combined? Round to a whole number.', '345', 'Square each, then divide.',
       ['0.04 + 0.09 + 0.16 = 0.29.', '10² = 100.', eq('100 ÷ 0.29 ≈ 345')], check=100 / 0.29, tol=0.5)
K.calc('m', 'What is the binary cross entropy when y = 1 and the model predicts p = 0.8? Give three decimals.', '0.223', 'BCE = −ln p when y = 1.',
       ['Only the y ln p term is active.', 'ln 0.8 ≈ −0.2231.', eq('BCE ≈ 0.223')], check=0.223, tol=0.0006)
K.calc('m', 'What is the entropy in bits of a coin with P(heads) = 0.9? Give three decimals.', '0.469', 'H = −(0.9 log₂ 0.9 + 0.1 log₂ 0.1).',
       ['0.9 × log₂ 0.9 ≈ 0.9 × (−0.152) = −0.137.', '0.1 × log₂ 0.1 ≈ 0.1 × (−3.322) = −0.332.', eq('H ≈ 0.137 + 0.332 = 0.469 bits'), 'A tidier room than the fair coin at 1 bit.'], check=0.469, tol=0.0006)
K.calc('h', '100,000 easy anchors each have p<sub>t</sub> = 0.99. What is their total cross entropy? Give one decimal.', '1005.0', 'Each costs −ln 0.99.',
       ['−ln 0.99 ≈ 0.0100503.', 'Multiply by 100,000.', eq('≈ 1,005.0')], check=100000 * 0.01005033585350145, tol=0.06)
K.calc('h', 'What share of the cross entropy do those easy anchors own, if 10 hard anchors each have p<sub>t</sub> = 0.10? Give a percentage to one decimal.', '97.8', 'Hard total = 10 × (−ln 0.10).',
       ['Hard total ≈ 10 × 2.3026 = 23.03.', 'Easy total ≈ 1,005.0.', eq('1,005.0 ÷ (1,005.0 + 23.03) ≈ 97.8%')], check=97.76, tol=0.06)
K.calc('h', 'With focal loss, γ = 2, what is the loss of one hard anchor with p<sub>t</sub> = 0.10? Give three decimals.', '1.865', 'FL = (1 − p<sub>t</sub>)<sup>γ</sup> × (−ln p<sub>t</sub>).',
       ['(1 − 0.10)² = 0.81.', '−ln 0.10 ≈ 2.3026.', eq('0.81 × 2.3026 ≈ 1.865')], check=0.81 * 2.302585, tol=0.0006)
K.calc('x', 'RetinaNet wants every anchor to start at foreground probability π = 0.01. What bias b does it use? Give three decimals.', '-4.595', 'b = ln(π ÷ (1 − π)).',
       ['π ÷ (1 − π) = 0.01 ÷ 0.99 ≈ 0.010101.', 'ln 0.010101 = −ln 99.', eq('b ≈ −4.595'), 'Check: σ(−4.595) = 1 ÷ (1 + 99) = 0.01.'], check=-4.59512, tol=0.0006)
K.calc('x', 'What is the earth mover distance between P = [0.5, 0.5, 0] and Q = [0, 0.5, 0.5] on positions 0, 1, 2?', '1', 'Add the absolute differences of the cumulative sums.',
       ['F<sub>P</sub> = [0.5, 1.0, 1.0] and F<sub>Q</sub> = [0, 0.5, 1.0].', 'Differences: 0.5, 0.5, 0.', eq('W<sub>1</sub> = 1.0')], check=1)

# ---------------------------------------------------------------- assignments
K.assign('iou', 'e', 'Intersection over union',
         '<p>Write <code>iou(a, b)</code> for boxes in corner form (x1, y1, x2, y2). Return the IoU rounded to 3 decimals, and 0.0 when the boxes do not overlap.</p>',
         '''
def iou(a, b):
    # your code here
    pass
''', [('iou((30, 20, 110, 180), (40, 30, 120, 190))', 0.695), ('iou((0, 0, 10, 10), (20, 20, 30, 30))', 0.0), ('iou((0, 0, 10, 10), (0, 0, 10, 10))', 1.0), ('iou((50, 50, 150, 150), (80, 70, 180, 170))', 0.389)],
         '''
def iou(a, b):
    iw = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    ih = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = iw * ih
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return round(inter / union, 3) if union > 0 else 0.0
''', 'The overlap width is min of the right edges minus max of the left edges, but never below 0.',
         '<p>The max(0, ...) is the whole trick: without it two far apart boxes would get a negative width times a negative height, a positive "overlap".</p>')
K.assign('huber', 'e', 'Huber loss',
         '<p>Write <code>huber(e, d=1.0)</code> that returns ½e² when |e| ≤ d and d(|e| − ½d) otherwise, rounded to 4 decimals.</p>',
         '''
def huber(e, d=1.0):
    # your code here
    pass
''', [('huber(0.4)', 0.08), ('huber(10)', 9.5), ('huber(-3)', 2.5), ('huber(3, 2.0)', 4.0), ('huber(1)', 0.5)],
         '''
def huber(e, d=1.0):
    a = abs(e)
    return round(0.5 * e * e if a <= d else d * (a - 0.5 * d), 4)
''', 'Use abs(e) so negative errors are handled the same way.',
         '<p>At e = d both formulas give ½d², so the two pieces join without a jump.</p>')
K.assign('focal', 'm', 'Focal loss for one prediction',
         '<p>Write <code>focal(p, y, gamma=2.0)</code> where p is the predicted probability of the object class and y is 1 for an object or 0 for background. Use p<sub>t</sub> = p if y = 1, else 1 − p, and return −(1 − p<sub>t</sub>)<sup>γ</sup> ln p<sub>t</sub> rounded to 5 decimals.</p>',
         '''
from math import log

def focal(p, y, gamma=2.0):
    # your code here
    pass
''', [('focal(0.1, 1)', 1.86509), ('focal(0.01, 0)', 0.0), ('focal(0.1, 1, 0)', 2.30259), ('focal(0.5, 0)', 0.17329)],
         '''
from math import log

def focal(p, y, gamma=2.0):
    pt = p if y == 1 else 1 - p
    return round(-((1 - pt) ** gamma) * log(pt), 5)
''', 'Turn p into p<sub>t</sub> first, then everything is one formula.',
         '<p>The second test is an easy background anchor: p<sub>t</sub> = 0.99 gives about 10<sup>−6</sup>, which rounds to 0. With γ = 0 you get plain cross entropy, as the third test shows.</p>')
K.assign('assign', 'h', 'Assign anchors to objects',
         '<p>Write <code>assign(anchors, gts, hi=0.5, lo=0.4)</code>. For each anchor find the true box with the highest IoU. Return a list with that box\'s index when IoU ≥ hi, −1 (background) when IoU < lo, and −2 (ignored) otherwise. Boxes are in corner form.</p>',
         '''
def assign(anchors, gts, hi=0.5, lo=0.4):
    # your code here
    pass
''', [('assign([(30, 20, 110, 180), (55, 65, 135, 225), (160, 115, 270, 195), (280, 20, 330, 90), (70, 70, 150, 230)], [(40, 30, 120, 190), (150, 110, 260, 190)])', [0, -2, 1, -1, -1]),
      ('assign([(30, 20, 110, 180), (160, 115, 270, 195)], [(40, 30, 120, 190), (150, 110, 260, 190)], 0.7, 0.3)', [-2, 1]),
      ('assign([(0, 0, 10, 10)], [])', [-1])],
         '''
def assign(anchors, gts, hi=0.5, lo=0.4):
    def iou(a, b):
        iw = max(0, min(a[2], b[2]) - max(a[0], b[0]))
        ih = max(0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = iw * ih
        union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
        return inter / union if union > 0 else 0.0
    out = []
    for a in anchors:
        best, idx = 0.0, -1
        for j, g in enumerate(gts):
            v = iou(a, g)
            if v > best:
                best, idx = v, j
        if best >= hi:
            out.append(idx)
        elif best < lo:
            out.append(-1)
        else:
            out.append(-2)
    return out
''', 'Reuse your IoU function inside a loop over anchors and true boxes.',
         '<p>These are the five anchors from the animation. With no objects in the image, everything is background, as the last test checks.</p>')

K.must('Target assignment', 'Match anchors to true boxes by IoU. RetinaNet: ≥ 0.5 positive, < 0.4 background, between ignored. RPN: 0.7 and 0.3. Background gets only a class loss.')
K.must('Box loss', 'MSE squares errors (outliers dominate), MAE is robust but kinked, Huber = ½e² for |e| ≤ 1 else |e| − ½, gradient clip(e, −1, 1). Bad box example: 345× under e², 1.1× in gradient with Huber.')
K.must('Imbalance', 'Easy background swamps the loss: 97.8% in the worked example. Remedies: subsample, down-weight, hard example mining, focal loss.')
K.must('Cross entropy and focal loss', 'BCE = −ln p<sub>t</sub>. FL = −α(1 − p<sub>t</sub>)<sup>γ</sup> ln p<sub>t</sub>, γ = 2, α = 0.25. Background share falls to 0.54%. Bias b = ln(π ÷ (1 − π)) = −4.595 for π = 0.01.')
K.must('Design axes', 'Architecture, loss, optimisation. GAN → DCGAN (architecture) → WGAN (loss, earth mover distance).')

T = K.topic(
    slug='detection-losses', topic='losses', step=(5, 'Finding objects', 'cv-detection', 'Object detection from the ground up: anchors, losses, duplicate removal, the main architectures and how detectors are scored.', 'College and masters'),
    title='Training a detector: targets and losses', short='Targets and losses', badge='5.2', minutes=55,
    lead='Decide which anchor learns which object, then see why boxes use Huber loss instead of squared error, and how focal loss stops thousands of easy background anchors from drowning the few real objects.',
    desc='Target assignment by IoU, the per-anchor objective, MSE, MAE and Huber loss with gradients, normalisation, class imbalance and its remedies, entropy and cross entropy, focal loss, prior bias initialisation and the GAN design story.',
    summary='Anchor targets by IoU, Huber loss for boxes, class imbalance, cross entropy and focal loss, bias initialisation and architecture versus loss.',
    keywords=['target assignment', 'IoU threshold', 'Huber loss', 'Smooth L1', 'MSE', 'MAE', 'class imbalance', 'hard example mining', 'cross entropy', 'entropy', 'focal loss', 'RetinaNet', 'prior bias', 'WGAN'],
    recap='<p>Each anchor gets a target by IoU, and only positives learn a box. Huber loss keeps box training stable by capping the gradient of large errors. Thousands of easy background anchors would dominate cross entropy, and focal loss scales their loss down by (1 − p<sub>t</sub>)<sup>γ</sup>. A small starting bias keeps the first steps calm.</p>')
