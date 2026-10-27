# Chapter 8: what a detector predicts, sliding windows and their cost, anchor boxes, box encoding and decoding,
# anchor density, convolutional heads and confidence. Source: lectures 3 and 4 (part IX) and lectures 5 and 6 (chapters 1 to 4).
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('windows', r'''
# How many sliding windows does one image need?
W, H = 640, 480                  # image size
w, h = 64, 128                   # window size (a person shape)
s = int(input("Stride in pixels: "))

nx = (W - w) // s + 1            # positions across
ny = (H - h) // s + 1            # positions down
n = nx * ny
print("positions:", nx, "x", ny, "=", n, "windows")

gflops = 4                       # one ResNet-50 pass at 224 x 224
tflops = n * gflops / 1000
print("compute:", round(tflops, 2), "TFLOPs")
print("time at 10 TFLOP/s:", round(tflops / 10, 2), "seconds")
''', stdin='8\n')

K.code('decode', r'''
# Decode network corrections t into a box, using the lecture anchor
from math import exp

xa, ya, wa, ha = 100, 120, 60, 120              # anchor centre and size
t = [float(v) for v in input("tx ty tw th: ").split()]

x = xa + t[0] * wa                              # shift in anchor widths
y = ya + t[1] * ha                              # shift in anchor heights
w = wa * exp(t[2])                              # scale in log space
h = ha * exp(t[3])
print("centre:", round(x, 2), round(y, 2), " size:", round(w, 2), "x", round(h, 2))
print("corners:", [round(v, 2) for v in (x - w / 2, y - h / 2, x + w / 2, y + h / 2)])
''', stdin='0.10 -0.05 0.20 -0.10\n')

K.code('encode', r'''
# Encode a ground-truth box as the training target for an anchor
from math import log

xa, ya, wa, ha = 100, 120, 60, 120              # anchor
x, y, w, h = 108, 112, 75, 110                  # ground truth

tx = (x - xa) / wa
ty = (y - ya) / ha
tw = log(w / wa)
th = log(h / ha)
print("target t* =", [round(v, 4) for v in (tx, ty, tw, th)])
''')

K.lesson('detector', 'What a detector predicts', f'''
<p>Classification says what is in the picture. <b>Object detection</b> says what is there and where, for every object, however many there are. The lecture calls it a multi-task problem: identify each object and locate it.</p>
{table(['Task', 'Answers', 'Output'], [
    ['Classification', 'What is in the image?', 'One class label'],
    ['Localisation', 'What and where, one object', 'One label and one box'],
    ['Detection', 'What and where, many objects', 'A list of (class, box, score) of any length'],
    ['Segmentation', 'Where, pixel by pixel', 'A class for every pixel']])}
<p>For each object a detector returns three things: a <b>class label</b> (person, car, dog, with background as an extra class), a <b>bounding box</b> of four numbers, and a <b>confidence score</b> such as 0.94.</p>
{fxs(
    fx('Two box formats', '(<i>x</i><sub>1</sub>, <i>y</i><sub>1</sub>, <i>x</i><sub>2</sub>, <i>y</i><sub>2</sub>) &nbsp; ⟷ &nbsp; (<i>x</i><sub>c</sub>, <i>y</i><sub>c</sub>, <i>w</i>, <i>h</i>)', '<i>x</i><sub>c</sub> = (<i>x</i><sub>1</sub> + <i>x</i><sub>2</sub>) ÷ 2, <i>w</i> = <i>x</i><sub>2</sub> − <i>x</i><sub>1</sub>, and the same for <i>y</i>. Image <i>y</i> grows downwards.', key=True),
    fx('Detection output', '{{ class, box, confidence }} × <i>N</i> objects', '<i>N</i> is not known in advance. It can be 0 or 50.'))}
<h3>Why detection is harder than ImageNet classification</h3>
<ul>
<li>The number of outputs varies from image to image.</li>
<li>Objects can be tiny, with far fewer pixels than an ImageNet photo, so the model must use context: a kite is in the sky, a surfer is on the sea.</li>
<li>Images must be larger, often 600 × 1000 or more, so small objects keep enough pixels.</li>
</ul>
{table(['Application', 'Which mistake hurts more'], [
    ['Self driving and driver assistance', 'A missed pedestrian (false negative), so favour recall'],
    ['Surveillance', 'A missed threat, but too many false alarms cause alarm fatigue'],
    ['Crop disease spotting', 'Missed disease loses the crop, false alarms waste spray'],
    ['Medical screening', 'A missed lesion, so favour recall and let a doctor confirm']])}
''', kw=['object detection', 'localisation', 'bounding box', 'class label', 'confidence score', 'box format', 'corners', 'centre size', 'multi-task', 'applications'])

K.lesson('sliding', 'Sliding windows and their four problems', f'''
<p>The simplest detector: take a window, place it in a corner, crop the patch, run a classifier that answers background or which class, then slide the window one step and repeat over the whole image. The lecturer compared it to working out a product by repeated addition, 2 + 2 + 2 + …, instead of multiplying. It always works, but the cost is huge.</p>
{fx('Number of window positions', '<i>N</i> = (⌊' + frac('<i>W</i> − <i>w</i>', '<i>s</i>') + '⌋ + 1) × (⌊' + frac('<i>H</i> − <i>h</i>', '<i>s</i>') + '⌋ + 1)', 'Image <i>W</i> × <i>H</i>, window <i>w</i> × <i>h</i>, stride <i>s</i>. For every window shape and scale.', key=True)}
{viz('slidewin')}
{table(['Problem', 'What goes wrong'], [
    ['Location', 'A small step is accurate but slow. A large step is fast but can cut an object in half and miss it.'],
    ['Scale', 'Objects can be tiny or huge. A small window loses context, a fixed window cannot fit both a far person and a near bus.'],
    ['Shape', 'People are tall, cars are wide. One square window fits neither.'],
    ['Computation', 'Thousands of windows, each a full classifier pass, recomputing almost the same pixels as its neighbours.']])}
{steps('The lecture count for a 640 × 480 image', [
    'Window 64 × 128 (a person shape), stride 8.',
    'Across: ⌊(640 − 64) ÷ 8⌋ + 1 = 72 + 1 = 73. Down: ⌊(480 − 128) ÷ 8⌋ + 1 = 44 + 1 = 45.',
    'Total: 73 × 45 = 3,285 windows for this one shape. Stride 4 gives 12,905 and stride 1 gives 203,681.',
    'At about 4 GFLOPs per ResNet-50 pass, 3,285 windows need about 13 TFLOPs, over a second on a fast GPU. Add 9 shapes and it reaches about 94 TFLOPs, around 9 seconds. Real time needs about 30 milliseconds.'])}
{code('windows')}
{note('Overlap between windows is a consequence, not a separate problem. A fine stride makes neighbouring windows overlap heavily, and that is why the same pixels are processed again and again.', 'exam')}
''', kw=['sliding window', 'stride', 'window count', 'location', 'scale', 'shape', 'computation', 'GFLOPs', 'brute force'])

K.lesson('anchors', 'Anchor boxes and box regression', f'''
<p>The fix is to test far fewer rough boxes and learn how to adjust them. An <b>anchor</b> is a predefined rough box at a fixed place. The lecturer put it simply: do not try to be perfect, just put one box. The network then predicts four corrections that move and resize the anchor onto the object.</p>
<p>Choosing a class is <b>classification</b>, a choice from a finite list. The corrections are <b>regression</b>, because a box can take infinitely many positions and sizes, so they are real numbers. Detection uses both.</p>
<h3>The simple version from the lecture</h3>
{steps('Anchor centre (100, 150), size 40 × 80, corrections Δx = +5, Δy = −10, Δw = +8, Δh = +4', [
    'New centre x = 100 + 5 = 105, new centre y = 150 − 10 = 140.',
    'New width = 40 + 8 = 48, new height = 80 + 4 = 84.',
    'Final box: centre (105, 140), size 48 × 84. No exhaustive search was needed.'])}
<h3>The version real detectors use</h3>
<p>Real detectors predict corrections relative to the anchor size, and use logarithms for the sizes.</p>
{fxs(
    fx('Encode (make the training target)', '<i>t</i><sub>x</sub> = ' + frac('<i>x</i> − <i>x</i><sub>a</sub>', '<i>w</i><sub>a</sub>') + ', &nbsp; <i>t</i><sub>y</sub> = ' + frac('<i>y</i> − <i>y</i><sub>a</sub>', '<i>h</i><sub>a</sub>') + ', &nbsp; <i>t</i><sub>w</sub> = ln ' + frac('<i>w</i>', '<i>w</i><sub>a</sub>') + ', &nbsp; <i>t</i><sub>h</sub> = ln ' + frac('<i>h</i>', '<i>h</i><sub>a</sub>'), 'Anchor (<i>x</i><sub>a</sub>, <i>y</i><sub>a</sub>, <i>w</i><sub>a</sub>, <i>h</i><sub>a</sub>), true box (<i>x</i>, <i>y</i>, <i>w</i>, <i>h</i>), all in centre size form.', key=True),
    fx('Decode (turn a prediction into a box)', '<i>x</i> = <i>x</i><sub>a</sub> + <i>t</i><sub>x</sub><i>w</i><sub>a</sub>, &nbsp; <i>y</i> = <i>y</i><sub>a</sub> + <i>t</i><sub>y</sub><i>h</i><sub>a</sub>, &nbsp; <i>w</i> = <i>w</i><sub>a</sub><i>e</i><sup><i>t</i><sub>w</sub></sup>, &nbsp; <i>h</i> = <i>h</i><sub>a</sub><i>e</i><sup><i>t</i><sub>h</sub></sup>', 'The exact reverse of encoding.', key=True))}
{viz('anchor')}
{code('decode')}
{code('encode')}
<h3>Why divide by the anchor size, and why logarithms</h3>
<ul>
<li><b>Same meaning at every scale.</b> A 10 pixel error is half of a 20 pixel object but only 2% of a 500 pixel one. Dividing by the anchor size makes the targets comparable.</li>
<li><b>Positive sizes for free.</b> <i>w</i> = <i>w</i><sub>a</sub><i>e</i><sup><i>t</i><sub>w</sub></sup> is positive for any <i>t</i><sub>w</sub>, so the network can output any number.</li>
<li><b>Symmetry.</b> Doubling is ln 2 = +0.693 and halving is ln ½ = −0.693, equal effort in opposite directions.</li>
<li><b>Scale invariance.</b> A 75 pixel box on a 60 pixel anchor and a 750 pixel box on a 600 pixel anchor both give ln 1.25 = 0.223.</li>
</ul>
''', kw=['anchor', 'anchor box', 'bounding box regression', 'box encoding', 'box decoding', 'offsets', 'tx ty tw th', 'log space', 'regression versus classification'])

K.lesson('density', 'Anchor grids, shapes and convolutional heads', f'''
<p>Where do the anchors come from? Run the backbone CNN once over the whole image. Each position of its feature map sees a patch of the image through its receptive field and is treated as one sliding window anchor. The same small classifier and box regressor are applied at every position, and applying the same weights everywhere is exactly what a convolution does. One forward pass therefore scores every anchor at once. This answers the hint on the sliding window slide: fast, and not so inaccurate after all.</p>
{fxs(
    fx('Heads as convolutions', 'class scores = SoftMax(Conv(<i>V</i>, <i>W</i><sub>cls</sub>)), &nbsp; offsets = Conv(<i>V</i>, <i>W</i><sub>loc</sub>)', '<i>V</i> is the feature map. Two heads, one backbone.'),
    fx('Head sizes', 'class channels = <i>k</i>(<i>C</i> + 1), &nbsp; box channels = 4<i>k</i>', '<i>k</i> anchors per position, <i>C</i> classes plus background.', key=True))}
<h3>Several shapes and sizes</h3>
<p>With one anchor shape the network cannot cope with fine and coarse objects in the same picture. So each position gets several anchors, typically 3 scales × 3 aspect ratios = 9: tall ones for pedestrians, wide ones for cars and buses, small and large for far and near objects. Each anchor type has its own classifier and regressor.</p>
<p><b>SSD</b> (2016) also predicts from several layers: fine 38 × 38 maps for small objects and coarse 3 × 3 and 1 × 1 maps for large ones. With 4 or 6 anchors per cell it scores 38² × 4 + 19² × 6 + 10² × 6 + 5² × 6 + 3² × 4 + 1² × 4 = 8,732 boxes per class.</p>
<h3>How close must the anchors be?</h3>
{viz('anchorgrid')}
{fx('Anchor stride rule', 's ≤ 0.367 <i>w</i>', 'Worst case: the object sits midway between four grid points. Requiring IoU ≥ 0.5 there gives (<i>w</i> − <i>s</i>/2)² ≥ ⅔ <i>w</i>², which simplifies to this.')}
{note('This is why anchor sizes grow with the stride of each feature level. RetinaNet uses anchors of 32 on its stride 8 level: 8 ÷ 32 = 0.25, safely under 0.367.', 'tip')}
''', kw=['anchor grid', 'feature map', 'convolutional heads', 'weight sharing', 'multiple anchors', 'aspect ratio', 'scale', 'SSD', '8732', 'anchor density', 'stride'])

K.lesson('trust', 'How far can we trust the score?', f'''
<p>The lecturer stressed that every model is uncertain, and that a field, <b>uncertainty quantification</b>, studies how much to trust predictions. The class listed where this matters: finance, cyclone forecasts, traffic, tumour diagnosis, drug discovery, fraud and surveillance. In each, a wrong answer has a cost.</p>
<p>In detection, uncertainty applies to three things: the class, the box position, and whether the object exists at all.</p>
{table(['Kind', 'Source', 'Does more data help?'], [
    ['Aleatoric', 'Noise in the data itself: blur, occlusion, a tiny object', 'No'],
    ['Epistemic', 'The model does not know: too little or unrepresentative data, wrong assumptions', 'Yes']])}
<p>SoftMax scores are guaranteed to lie between 0 and 1 and to add up to 1. That is a mathematical fact, but it does not make them correct probabilities. Modern networks are often overconfident.</p>
{steps('Expected calibration error, worked', [
    '100 predictions. 60 have average confidence 0.90 but only 70% are right. 40 have confidence 0.60 and 60% are right.',
    'First group: gap |0.70 − 0.90| = 0.20, weight 60 ÷ 100 = 0.6, contribution 0.12.',
    'Second group: gap |0.60 − 0.60| = 0, contribution 0.',
    'ECE = 0.12. The model is overconfident by 12 percentage points on average.'])}
{deep('a real guarantee: conformal prediction', '<p>Split conformal prediction turns any classifier into one that outputs a set of classes containing the truth with probability at least 1 − α, assuming only that calibration and test images are exchangeable. Hold out <i>n</i> calibration images and score each by s = 1 − p̂(true class). Let q̂ be the <i>k</i>-th smallest score with <i>k</i> = ⌈(<i>n</i> + 1)(1 − α)⌉. For a new image, output every class with 1 − p̂(class) ≤ q̂. The rank of the new score among all <i>n</i> + 1 scores is uniform, so the chance that it is at most <i>k</i> is <i>k</i> ÷ (<i>n</i> + 1) ≥ 1 − α. With <i>n</i> = 9 and α = 0.2, <i>k</i> = ⌈10 × 0.8⌉ = 8.</p>')}
{ladder(
    '<p>A detector draws boxes around things and names them. Checking every possible box would take far too long, so it starts from a set of ready made boxes on a grid and learns to nudge each one into place.</p>',
    '<p>Sliding windows cost (⌊(W − w) ÷ s⌋ + 1)(⌊(H − h) ÷ s⌋ + 1) classifier passes per shape. Anchors plus regression of t = ((x − x<sub>a</sub>) ÷ w<sub>a</sub>, (y − y<sub>a</sub>) ÷ h<sub>a</sub>, ln(w ÷ w<sub>a</sub>), ln(h ÷ h<sub>a</sub>)) replace the search, and convolutional heads score all anchors in one pass.</p>',
    '<p>Anchor design is a coverage problem: the grid stride must satisfy s ≤ 0.367w for worst case IoU 0.5, so multi-scale feature maps carry anchors proportional to their stride. Calibration (ECE, temperature scaling) and the split between aleatoric and epistemic uncertainty decide whether scores can drive decisions.</p>',
    '<p>Anchor free detectors (FCOS, CenterNet) predict boxes directly from points, and DETR treats detection as set prediction with a transformer and Hungarian matching, removing hand designed anchors and duplicate removal. Conformal methods are being extended to give coverage guarantees for boxes, not only classes.</p>')}
''', kw=['uncertainty quantification', 'aleatoric', 'epistemic', 'calibration', 'ECE', 'overconfident', 'conformal prediction', 'coverage guarantee', 'trust'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What three things does a detector output for each object?', ['Colour, size, age', 'Class label, bounding box, confidence score', 'Only a class label', 'A mask for each pixel'], 1,
       'What, where and how sure.', 'Class, four box numbers and a score. Detection repeats this for a variable number of objects.')
K.quiz('e', 'Detection is described in the lecture as', ['Unsupervised', 'Multi-task: classification plus localisation', 'Only regression', 'Image compression'], 1,
       'What is it and where is it.', 'One backbone feeds a classification head and a box regression head, trained with a combined loss.')
K.quiz('e', 'Which is a problem of sliding windows named in the lecture?', ['Too few windows', 'Shape: people are tall and cars are wide, so one window fits neither', 'Windows are always too large', 'They need no classifier'], 1,
       'Four problems: location, scale, shape, computation.', 'A fixed window shape cannot match objects with very different aspect ratios.')
K.quiz('m', 'Why are box corrections a regression problem?', [
    'Because there are 80 classes', 'Because box positions and sizes are continuous real numbers, not a finite list', 'Because anchors are random', 'Because regression is faster'], 1,
    'Could you make a class for every possible box?', 'The set of boxes is effectively infinite, so the network outputs real valued offsets instead of choosing from a menu.')
K.quiz('m', 'Why is t<sub>w</sub> = ln(w ÷ w<sub>a</sub>) used instead of w − w<sub>a</sub>?', [
    'Logarithms are faster to compute', 'The decoded width w<sub>a</sub>e<sup>t<sub>w</sub></sup> is always positive, and doubling and halving become equal and opposite', 'To make the width negative', 'It is only a convention with no effect'], 1,
    'Think about e to any power.', 'Exponentials are always positive, and ln 2 = −ln ½, so growing and shrinking are treated symmetrically and the target is the same at every scale.')
K.quiz('m', 'The same 10 pixel centre error matters most for', ['A 500 pixel object', 'A 20 pixel object', 'Both equally', 'Neither'], 1,
       'Divide by the size.', '10 ÷ 20 = 0.5 of the object against 10 ÷ 500 = 0.02. Encoding relative to the anchor size captures this.')
K.quiz('m', 'How does a convolutional detector avoid running a classifier on every window separately?', [
    'It skips half the windows', 'The backbone runs once, and the class and box heads are convolutions applied at every feature map position', 'It uses bigger windows', 'It uses only one anchor'], 1,
    'Weight sharing.', 'Every feature map position acts as an anchor. Applying the same small heads everywhere is a convolution, so all anchors are scored in one pass.')
K.quiz('h', 'A feature map is 38 × 38 with 4 anchors per cell and 20 classes plus background. How many class channels does the head need?', ['24', '84', '80', '16'], 1,
       'k(C + 1).', '4 × 21 = 84 class channels, and 4 × 4 = 16 box channels.')
K.quiz('h', 'Why do detectors use several anchor shapes at each position?', ['To slow training', 'So that at least one starting box roughly matches each object, tall or wide, small or large', 'Because SoftMax needs them', 'To remove duplicates'], 1,
       'One shape cannot fit everything.', 'Tall anchors suit people, wide ones cars. More shapes raise the chance of a good starting overlap.')
K.quiz('h', 'Which uncertainty cannot be reduced by collecting more data?', ['Epistemic', 'Aleatoric', 'Both', 'Neither'], 1,
       'Noise in the data itself.', 'A blurry or occluded object stays ambiguous however much data you collect. Epistemic uncertainty, the model\'s ignorance, does shrink with more data.')
K.quiz('x', 'Anchors equal in size to a 40 pixel object sit on a grid. What is the largest stride that keeps worst case IoU at least 0.5?', ['About 8', 'About 14.7', 'About 20', 'About 40'], 1,
       's ≤ 0.367w.', '0.367 × 40 ≈ 14.7 pixels.')
K.quiz('x', 'A model\'s SoftMax scores are always between 0 and 1 and add up to 1. Does that make them trustworthy probabilities?', [
    'Yes, by definition', 'No, they can still be miscalibrated, for example saying 0.9 while being right 70% of the time', 'Only for two classes', 'Only after NMS'], 1,
    'Valid numbers are not the same as correct ones.', 'The normalisation is guaranteed, the calibration is not. Temperature scaling, ensembles or conformal prediction address the gap.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A box has corners (40, 30, 120, 190). What is its width?', '80', 'w = x<sub>2</sub> − x<sub>1</sub>.',
       ['x<sub>1</sub> = 40 and x<sub>2</sub> = 120.', '120 − 40.', eq('w = 80'), 'Its height is 190 − 30 = 160 and its centre is (80, 110).'], check=80)
K.calc('e', 'Anchor centre (100, 150), size 40 × 80. The lecture corrections are Δx = +5, Δy = −10, Δw = +8, Δh = +4. What is the new height?', '84', 'Add Δh to the height.',
       ['The height starts at 80.', 'Δh = +4.', eq('80 + 4 = 84'), 'The full box: centre (105, 140), size 48 × 84.'], check=84)
K.calc('e', 'How many horizontal window positions fit a 64 pixel wide window in a 640 pixel image at stride 8?', '73', '⌊(W − w) ÷ s⌋ + 1.',
       ['640 − 64 = 576.', '576 ÷ 8 = 72.', eq('72 + 1 = 73')], check=73)
K.calc('m', 'With 73 positions across and 45 down, how many windows are there for one shape?', '3285', 'Multiply.',
       ['Across: 73.', 'Down: 45.', eq('73 × 45 = 3,285')], check=3285)
K.calc('m', 'Repeat the count at stride 4 for the 64 × 128 window in a 640 × 480 image.', '12905', 'Recompute both directions.',
       ['Across: ⌊576 ÷ 4⌋ + 1 = 145.', 'Down: ⌊(480 − 128) ÷ 4⌋ + 1 = ⌊352 ÷ 4⌋ + 1 = 89.', eq('145 × 89 = 12,905'), 'Halving the stride roughly quadruples the windows.'], check=12905)
K.calc('m', 'Decode t<sub>x</sub> = 0.10 for the anchor centred at x<sub>a</sub> = 100 with width 60. What is the new centre x?', '106', 'x = x<sub>a</sub> + t<sub>x</sub> w<sub>a</sub>.',
       ['t<sub>x</sub> w<sub>a</sub> = 0.10 × 60 = 6.', 'x = 100 + 6.', eq('x = 106')], check=106)
K.calc('m', 'Decode t<sub>w</sub> = 0.20 for an anchor of width 60. What is the new width? Give two decimals.', '73.28', 'w = w<sub>a</sub> e<sup>t<sub>w</sub></sup>.',
       ['e<sup>0.20</sup> ≈ 1.2214.', '60 × 1.2214.', eq('w ≈ 73.28')], check=60 * 2.718281828459045 ** 0.2, tol=0.006)
K.calc('h', 'Encode the true width 75 against an anchor width 60: what is t<sub>w</sub>? Give four decimals.', '0.2231', 't<sub>w</sub> = ln(w ÷ w<sub>a</sub>).',
       ['75 ÷ 60 = 1.25.', 'ln 1.25.', eq('t<sub>w</sub> ≈ 0.2231'), 'A 750 pixel box on a 600 pixel anchor gives the same target.'], check=0.2231, tol=0.00006)
K.calc('h', 'Encode the true centre y = 112 against the anchor y<sub>a</sub> = 120, h<sub>a</sub> = 120: what is t<sub>y</sub>? Give four decimals.', '-0.0667', 't<sub>y</sub> = (y − y<sub>a</sub>) ÷ h<sub>a</sub>.',
       ['112 − 120 = −8.', '−8 ÷ 120.', eq('t<sub>y</sub> ≈ −0.0667'), 'Negative means the object is slightly above the anchor centre, since image y grows downwards.'], check=-0.0667, tol=0.00006)
K.calc('h', 'SSD uses maps of 38, 19, 10, 5, 3 and 1 cells per side with 4, 6, 6, 6, 4 and 4 anchors per cell. How many boxes per class?', '8732', 'Add size² × anchors for each map.',
       ['38² × 4 = 5,776 and 19² × 6 = 2,166.', '10² × 6 = 600, 5² × 6 = 150, 3² × 4 = 36, 1² × 4 = 4.', eq('5,776 + 2,166 + 600 + 150 + 36 + 4 = 8,732')], check=8732)
K.calc('x', 'Anchors of size 32 sit on a stride 8 grid. In the worst case the object is offset by 4 pixels in both directions. What is the IoU? Give three decimals.', '0.620', 'I = (w − s/2)², union = 2w² − I.',
       ['I = (32 − 4)² = 28² = 784.', 'Union = 2 × 1,024 − 784 = 1,264.', eq('IoU = 784 ÷ 1,264 ≈ 0.620'), 'Above 0.5, so every object has a good starting anchor.'], check=784 / 1264, tol=0.0006)
K.calc('x', 'A model makes 60 predictions at average confidence 0.90 with 70% correct, and 40 at 0.60 with 60% correct. What is the expected calibration error?', '0.12', 'Weighted average of |accuracy − confidence|.',
       ['Group 1: 0.6 × |0.70 − 0.90| = 0.6 × 0.20 = 0.12.', 'Group 2: 0.4 × |0.60 − 0.60| = 0.', eq('ECE = 0.12 + 0 = 0.12')], check=0.12)

# ---------------------------------------------------------------- assignments
K.assign('count', 'e', 'Count sliding windows',
         '<p>Write <code>count_windows(W, H, w, h, s)</code> that returns how many positions a w × h window takes in a W × H image with stride s. Return 0 if the window does not fit.</p>',
         '''
def count_windows(W, H, w, h, s):
    # your code here
    pass
''', [('count_windows(640, 480, 64, 128, 8)', 3285), ('count_windows(640, 480, 64, 128, 4)', 12905), ('count_windows(100, 100, 100, 100, 5)', 1), ('count_windows(50, 50, 64, 64, 1)', 0)],
         '''
def count_windows(W, H, w, h, s):
    if w > W or h > H:
        return 0
    return ((W - w) // s + 1) * ((H - h) // s + 1)
''', 'Use // for the floor, and check the window fits first.',
         '<p>A window as large as the image fits exactly once. One larger than the image cannot be placed at all.</p>')
K.assign('fmt', 'e', 'Convert box formats',
         '<p>Write <code>to_centre(box)</code> that turns corners (x1, y1, x2, y2) into [xc, yc, w, h], and <code>to_corners(box)</code> that does the reverse.</p>',
         '''
def to_centre(box):
    # your code here
    pass

def to_corners(box):
    # your code here
    pass
''', [('to_centre((40, 30, 120, 190))', [80.0, 110.0, 80, 160]), ('to_corners((80, 110, 80, 160))', [40.0, 30.0, 120.0, 190.0]), ('to_corners(to_centre((1, 2, 5, 10)))', [1.0, 2.0, 5.0, 10.0])],
         '''
def to_centre(box):
    x1, y1, x2, y2 = box
    return [(x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1]

def to_corners(box):
    xc, yc, w, h = box
    return [xc - w / 2, yc - h / 2, xc + w / 2, yc + h / 2]
''', 'The centre is the average of the two corners. The corners are the centre plus or minus half the size.',
         '<p>The last test converts and converts back. Libraries such as torchvision.ops.box_convert do this, and mixing the two formats up is one of the most common detection bugs.</p>')
K.assign('decode', 'm', 'Decode a prediction',
         '<p>Write <code>decode(anchor, t)</code>. The anchor is (xa, ya, wa, ha) in centre size form and t is (tx, ty, tw, th). Return the corners [x1, y1, x2, y2], each rounded to 2 decimals.</p>',
         '''
from math import exp

def decode(anchor, t):
    # your code here
    pass
''', [('decode((100, 120, 60, 120), (0.10, -0.05, 0.20, -0.10))', [69.36, 59.71, 142.64, 168.29]), ('decode((50, 50, 20, 20), (0, 0, 0, 0))', [40.0, 40.0, 60.0, 60.0]), ('decode((0, 0, 10, 10), (1, -1, 0.6931471805599453, 0))', [0.0, -15.0, 20.0, -5.0])],
         '''
from math import exp

def decode(anchor, t):
    xa, ya, wa, ha = anchor
    x = xa + t[0] * wa
    y = ya + t[1] * ha
    w = wa * exp(t[2])
    h = ha * exp(t[3])
    return [round(x - w / 2, 2), round(y - h / 2, 2), round(x + w / 2, 2), round(y + h / 2, 2)]
''', 'Find the centre and size first, then convert to corners.',
         '<p>The second test shows that t = 0 returns the anchor itself. In the third, t<sub>w</sub> = ln 2 doubles the width.</p>')
K.assign('encode', 'm', 'Encode a training target',
         '<p>Write <code>encode(anchor, gt)</code> where both are (x, y, w, h) in centre size form. Return [tx, ty, tw, th] rounded to 4 decimals.</p>',
         '''
from math import log

def encode(anchor, gt):
    # your code here
    pass
''', [('encode((100, 120, 60, 120), (108, 112, 75, 110))', [0.1333, -0.0667, 0.2231, -0.087]), ('encode((50, 50, 20, 20), (50, 50, 20, 20))', [0.0, 0.0, 0.0, 0.0]), ('encode((70, 100, 80, 160), (80, 110, 80, 160))', [0.125, 0.0625, 0.0, 0.0])],
         '''
from math import log

def encode(anchor, gt):
    xa, ya, wa, ha = anchor
    x, y, w, h = gt
    return [round((x - xa) / wa, 4), round((y - ya) / ha, 4), round(log(w / wa), 4), round(log(h / ha), 4)]
''', 'Four formulas, one per output.',
         '<p>Encoding then decoding returns the original box exactly. The third test is anchor A1 matched to the person box in the next chapter.</p>')

K.must('Detector output', 'For each object: class, box, confidence. Corners (x1, y1, x2, y2) or centre size (xc, yc, w, h). The number of objects varies.')
K.must('Sliding windows', '(⌊(W − w) ÷ s⌋ + 1)(⌊(H − h) ÷ s⌋ + 1) windows per shape: 3,285 for 64 × 128 at stride 8 in 640 × 480. Four problems: location, scale, shape, computation.')
K.must('Anchors and regression', 'Rough box plus four learned corrections. t = ((x − xa) ÷ wa, (y − ya) ÷ ha, ln(w ÷ wa), ln(h ÷ ha)), decode with x = xa + tx wa and w = wa e^tw.')
K.must('Heads and anchor design', 'One backbone pass, conv heads score all anchors. k(C + 1) class and 4k box channels. 9 anchors = 3 scales × 3 ratios. SSD 8,732 boxes. Stride s ≤ 0.367w.')
K.must('Trusting scores', 'Aleatoric (data noise) versus epistemic (model ignorance). SoftMax is valid but often overconfident. ECE measures it. Conformal prediction gives a coverage guarantee.')

T = K.topic(
    slug='detection-anchors', topic='anchors', step=(5, 'Finding objects', 'cv-detection', 'Object detection from the ground up: anchors, losses, duplicate removal, the main architectures and how detectors are scored.', 'College and masters'),
    title='From sliding windows to anchor boxes', short='Sliding windows and anchors', badge='5.1', minutes=50,
    lead='Find out what a detector must output, why scanning windows is hopeless, and how anchors with four learned corrections, scored by convolutional heads in a single pass, made detection fast.',
    desc='Detector outputs and box formats, sliding window counts and their four problems, anchor boxes, box encoding and decoding in log space, anchor density, convolutional heads, SSD and confidence calibration.',
    summary='Detector outputs, sliding window cost, anchors with box encoding and decoding, anchor grids and heads, and trusting confidence scores.',
    keywords=['object detection', 'bounding box', 'sliding window', 'anchor', 'box regression', 'encoding', 'decoding', 'log space', 'SSD', 'anchor density', 'convolutional head', 'calibration', 'uncertainty'],
    recap='<p>A detector outputs a variable list of class, box and score. Scanning windows costs thousands of classifier passes, so detectors place anchors on a feature map grid and learn four corrections per anchor, encoded relative to the anchor size and in log space. Convolutional heads score every anchor in one pass, and the score itself needs calibration before it can be trusted.</p>')
