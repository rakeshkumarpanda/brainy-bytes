# Chapter 12: what semantic segmentation predicts. Classification to detection to segmentation, why boxes are
# not enough, semantic, instance and panoptic segmentation, output tensors, SoftMax and argmax per pixel,
# ground truth masks, invariance and equivariance, receptive field, the downsampling trade-off, WHAT and WHERE,
# and the dense prediction family.
# Source: lectures 7 and 8, chapters 1 to 4.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('softmax', r'''
# SoftMax and argmax at one pixel
from math import exp
classes = ["road", "car", "person", "building", "sky"]
z = [float(v) for v in input("five logits: ").split()]

e = [exp(v) for v in z]
total = sum(e)
p = [v / total for v in e]
for c, pc in zip(classes, p):
    print(c.ljust(9), round(pc, 3))
print("sum =", round(sum(p), 3))
print("label:", classes[p.index(max(p))])
''', stdin='0 -0.51 -0.91 0.70 2.78\n')

K.code('count', r'''
# Count cars in a semantic mask with connected components (4 neighbours)
gap = int(input("columns between car A and car B (0 = touching): "))
W = 13
mask = [[0] * W for _ in range(3)]
for r in range(3):
    for c in list(range(1, 4)) + list(range(4 + gap, 7 + gap)) + [10, 11]:
        mask[r][c] = 1                      # every car pixel has the same label

seen = set()
count = 0
for r in range(3):
    for c in range(W):
        if mask[r][c] and (r, c) not in seen:
            count += 1
            stack = [(r, c)]
            seen.add((r, c))
            while stack:
                y, x = stack.pop()
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < 3 and 0 <= nx < W and mask[ny][nx] and (ny, nx) not in seen:
                        seen.add((ny, nx))
                        stack.append((ny, nx))
print("components found:", count, " real cars: 3")
''', stdin='0\n')

K.code('shrink', r'''
# Downsample one row of a mask by majority vote, upsample by copying, measure IoU
row = [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0]   # a 6 pixel blob, a 2 pixel line
F = int(input("factor (1, 2, 4, 8): "))

coarse = []
for i in range(0, 16, F):
    block = row[i:i + F]
    coarse.append(1 if 2 * sum(block) > F else 0)        # strict majority
up = [v for v in coarse for _ in range(F)]
inter = sum(a and b for a, b in zip(row, up))
union = sum(a or b for a, b in zip(row, up))
print("coarse:", coarse)
print("back:  ", up)
print("IoU =", round(inter / union, 3))
''', stdin='4\n')

K.lesson('tasks', 'From one label to a label per pixel', f'''
<p>Each vision task adds a question. Classification asks what the image shows. Detection asks what and roughly where. <b>Semantic segmentation</b> asks what is at every single pixel. The lecturer put it as semantic understanding plus spatial precision: features are extracted, every pixel gets a score per class, and the scores become the final mask.</p>
{table(['Task', 'Question', 'Output', 'Size'], [
    ['Classification', 'What is this image?', 'One label', '1 label (C scores)'],
    ['Detection', 'What, and roughly where?', 'Class, box and score per object', 'N × (4 + 1 + C)'],
    ['Semantic segmentation', 'What, and exactly where?', 'A class for every pixel (a mask)', 'H × W labels (H × W × C scores)']])}
{fx('Semantic segmentation', '<i>I</i> ∈ ℝ<sup><i>H</i> × <i>W</i> × 3</sup> → <i>Y</i> ∈ {1, …, <i>C</i>}<sup><i>H</i> × <i>W</i></sup>', 'One classification repeated at every pixel. Tasks that predict something at every pixel are called <b>dense prediction</b>.', key=True)}
<h3>Why a box is not enough</h3>
<ul>
<li>A self driving car needs the exact drivable road pixels. The road has no meaningful box at all, it is a region.</li>
<li>For a tumour, area, growth and the exact outline drive treatment. A rectangle overestimates the area.</li>
<li>Even a perfect ellipse fills only πab ÷ (2a · 2b) = π ÷ 4 ≈ 78.5% of its box. A 4 pixel lane marking running diagonally across a 100 × 100 box fills about 566 pixels, 5.7% of it.</li>
</ul>
<p>A student asked: if segmentation is better, why not use it everywhere? The lecturer gave three reasons. It is heavy to compute (a 512 × 512 image needs 262,144 predictions instead of 1). Every pixel needs a label, so annotation is slow (the Cityscapes authors report more than 1.5 hours per finely labelled image). And if classification answers the question, use classification.</p>
{table(['Field', 'Classes', 'Why shape matters'], [
    ['Autonomous driving', 'road, sidewalk, vehicles, pedestrians', 'Free space is a region, not a box'],
    ['Medical imaging', 'tumour, organ, tissue', 'Area, margin, surgical and radiation planning'],
    ['Satellite images', 'water, vegetation, road, building', 'How much land belongs to each class'],
    ['Agriculture', 'crop, weed, soil', 'Laser weeding must not burn the crop next to the weed']])}
<h3>Semantic, instance and panoptic</h3>
{table(['', 'Semantic', 'Instance', 'Panoptic'], [
    ['Answers', 'Which class is each pixel?', 'Which object is each pixel?', 'Both, for every pixel'],
    ['Three people', 'All labelled person', 'Person 1, 2 and 3', 'People separate, sky and sand labelled too'],
    ['Counting', 'Not possible from the mask', 'Yes', 'Yes, for countable things'],
    ['Typical model and metric', 'FCN, U-Net, DeepLab, mIoU', 'Mask R-CNN, mask AP', 'Panoptic FPN, Mask2Former, PQ']])}
<p>The lecturer\'s example: two cars that touch become one green blob in a semantic mask, so it looks like one big car. Counting by connected components fails exactly there.</p>
{code('count')}
{fx('Panoptic quality', 'PQ = ' + frac('Σ<sub>matched</sub> IoU', '|TP| + ½|FP| + ½|FN|') + ' = SQ × RQ', 'Segmentation quality (mean IoU of matched segments) times recognition quality (an F1 style count). Three matches with IoU 0.8, 0.7, 0.9, one FP and one FN: SQ = 0.80, RQ = 3 ÷ 4 = 0.75, PQ = 0.60.')}
''', kw=['semantic segmentation', 'dense prediction', 'mask', 'bounding box', 'instance segmentation', 'panoptic segmentation', 'things and stuff', 'connected components', 'panoptic quality', 'annotation cost'])

K.lesson('output', 'What the network outputs', f'''
<p>The input stays a 256 × 256 × 3 image. Before the final decision the output is 256 × 256 × C. The lecturer: the channels become classes. Channel k is a score map for class k, high where the network believes class k is present. The final mask is 256 × 256, one class ID per pixel.</p>
{fxs(
    fx('SoftMax at each pixel', '<i>P</i>(<i>c</i> | <i>x</i>, <i>y</i>) = ' + frac('<i>e</i><sup><i>z</i><sub><i>c</i></sub>(<i>x</i>, <i>y</i>)</sup>', 'Σ<sub><i>k</i></sub> <i>e</i><sup><i>z</i><sub><i>k</i></sub>(<i>x</i>, <i>y</i>)</sup>'), 'Positive, and the C values add to 1. Road competes with the other four classes, car with the other four, and so on.', key=True),
    fx('Label', '<i>Y</i>(<i>x</i>, <i>y</i>) = argmax<sub><i>c</i></sub> <i>P</i>(<i>c</i> | <i>x</i>, <i>y</i>)', 'Before argmax: H × W × C. After argmax: H × W.'))}
{viz('pixelsm')}
{steps('From raw scores to a label', [
    'Classes road, car, person, building, sky. Logits z = [0.00, −0.51, −0.91, 0.70, 2.78].',
    'Exponentials: 1.000, 0.600, 0.403, 2.014, 16.119. Their sum is 20.136.',
    'Divide: p = 0.050, 0.030, 0.020, 0.100, 0.801. They add to 1.',
    'The largest is sky, so this pixel becomes sky.'])}
{code('softmax')}
{deep('Why argmax of SoftMax equals argmax of the logits', '<p>Every class shares the same positive denominator, and the exponential is strictly increasing. If z<sub>a</sub> &gt; z<sub>b</sub> then e<sup>z<sub>a</sub></sup> &gt; e<sup>z<sub>b</sub></sup> and p<sub>a</sub> &gt; p<sub>b</sub>. The order is preserved, so inference can skip SoftMax. It is still needed for the loss and for confidence values.</p>')}
<p>Why SoftMax and not sigmoid? A student answered well: sigmoids do not add up to one. Two sigmoids can give 0.9 and 0.5 for the same pixel. Use SoftMax when each pixel has exactly one class. Use one sigmoid per class when a pixel may carry several labels at once, such as a vessel inside a lesion.</p>
<h3>The ground truth</h3>
<p>A mask is a matrix of class IDs. Colours are only for display. The slide used a 5 × 5 mask with 0 sky, 1 building, 2 road, 3 car and 4 person.</p>
{mat([[0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 0, 3, 3, 3], [2, 2, 2, 2, 4], [2, 2, 2, 2, 4]])}
{steps('Read a mask like the network does', [
    'Count each ID: sky 7, building 3, road 10, car 3, person 2. Total 25.',
    'Shares: road 40%, sky 28%, building 12%, car 12%, person 8%. Already imbalanced.',
    'For the loss, each pixel becomes a one hot vector. A person pixel becomes [0, 0, 0, 0, 1], so the mask becomes a 5 × 5 × 5 tensor.',
    'A pixel labelled 255 would be an ignore label and get no loss at all.'])}
{note('Dense labels are expensive. Someone must trace every boundary. When masks are scarce, people use weak labels (tags, boxes, points or scribbles), a few masks plus many unlabelled images, self supervised pre-training, or a click based tool such as SAM to speed up annotation.', 'tip')}
''', kw=['output tensor', 'H x W x C', 'SoftMax', 'argmax', 'logit', 'sigmoid', 'multi-label', 'ground truth mask', 'class ID', 'one hot', 'ignore label', 'weak supervision'])

K.lesson('where', 'Why a classifier loses the WHERE', f'''
<p>A classification network shrinks 224 × 224 × 3 down to 7 × 7 × 2048, then pools to one vector and one label. That is on purpose: it should say dog wherever the dog is. Segmentation needs the opposite, a label map that moves with the object.</p>
{table(['Classification wants', 'Segmentation needs'], [
    ['Invariance: location does not matter', 'Precision: every boundary matters'],
    ['A summary of the whole image', 'Small objects must not disappear'],
    ['One vector, one label', 'The output must keep the spatial grid']])}
{deep('Convolution is equivariant, global pooling is invariant', '<p>Let y[n] = Σ<sub>k</sub> w[k] x[n − k]. Shift the input by a: x′[n] = x[n − a]. Then y′[n] = Σ<sub>k</sub> w[k] x[n − a − k] = y[n − a]. Shifting then convolving equals convolving then shifting. That is <b>equivariance</b>.</p><p>Global average pooling averages over all positions, so the shift disappears: the output is <b>invariant</b>. Segmentation wants the equivariant part and must not throw it away with pooling and fully connected layers. Strided layers are only roughly equivariant, because a shift that is not a multiple of the stride changes the output.</p>')}
<h3>Receptive field</h3>
<p>The students defined it well: how much of the original image one neuron can see. The kernel stays 3 × 3, but its coverage in input pixels grows with depth and stride.</p>
{fx('Receptive field recurrence', '<i>r</i><sub><i>l</i></sub> = <i>r</i><sub><i>l</i>−1</sub> + (<i>k</i> − 1) · <i>d</i><sub><i>l</i></sub> · <i>j</i><sub><i>l</i>−1</sub>, &nbsp; <i>j</i><sub><i>l</i></sub> = <i>j</i><sub><i>l</i>−1</sub> · <i>s</i><sub><i>l</i></sub>', 'Start with r = 1 and j = 1. k is the kernel size, d the dilation, s the stride, j the jump between neighbouring cells in input pixels.', key=True)}
{viz('rfstack')}
{steps('Four 3 × 3 layers', [
    'Plain layers each add 2: r = 3, 5, 7, 9.',
    'Give layers 2 and 4 stride 2: r = 3, 5 (j becomes 2), 9, 13 (j becomes 4).',
    'Downsampling bought a field of 13 instead of 9, but the map is now 4 times smaller in each direction. Resolution down, receptive field up.'])}
<h3>The downsampling trade-off</h3>
{table(['Downsampling improves', 'Downsampling loses'], [
    ['Larger receptive field', 'Fine boundaries'],
    ['More abstract, semantic features', 'Thin structures such as lane markings and blood vessels'],
    ['Context, and less computation', 'Small objects']])}
<p>A structure of 16 × 8 pixels becomes 4 × 2 cells after ×4, 2 × 1 after ×8, and one cell or less after ×16. A 4 pixel lane marking at stride 16 covers a quarter of a cell and is outvoted by background.</p>
{viz('downup')}
{code('shrink')}
{deep('Why the decoder cannot invent what the encoder dropped', '<p>Let X be the image, Z the bottleneck and Ŷ the decoder output, a function of Z only. The <b>data processing inequality</b> says I(X, Ŷ) ≤ I(X, Z): the output cannot carry more information about the image than the bottleneck kept. The fix is to give the decoder other paths to the input, which is what skip connections do in the next chapter.</p>')}
{table(['', 'Early layers', 'Deep layers'], [
    ['Resolution', 'High', 'Low'],
    ['Good at', 'Edges, textures, boundaries (WHERE)', 'Objects and context (WHAT)'],
    ['Weakness', 'Weak meaning', 'Coarse location']])}
{note('The slide warned: do not memorise architecture names. FCN, U-Net, DeepLab and transformers are different answers to one question: how do we combine WHAT is present with exactly WHERE it is?', 'exam')}
''', kw=['invariance', 'equivariance', 'global pooling', 'receptive field', 'jump', 'stride', 'downsampling', 'thin structures', 'Nyquist', 'data processing inequality', 'WHAT and WHERE'])

K.lesson('dense', 'The dense prediction family', f'''
<p>Segmentation is the classification member of a family of tasks that predict something at every pixel. The others predict real numbers.</p>
{table(['Task', 'Output', 'Value', 'Typical loss'], [
    ['Classification', '1 prediction (C scores)', 'category', 'cross-entropy'],
    ['Detection', 'N × (class, box, score)', 'category and 4 numbers', 'CE or focal, plus Smooth-L1'],
    ['Semantic segmentation', 'H × W × C', 'category per pixel', 'pixel CE, Dice, focal'],
    ['Depth estimation', 'H × W × 1', 'distance', 'L1, scale invariant log loss'],
    ['Optical flow', 'H × W × 2', 'motion (u, v) per pixel', 'end point error'],
    ['Surface normals', 'H × W × 3', 'unit vector', 'angular or cosine loss'],
    ['Keypoint heat maps', 'H × W × K', 'probability per joint', 'MSE on Gaussian blobs']])}
<h3>Depth</h3>
<p>The lecturer\'s example: photograph the classroom and a depth map shows the front row close and each later row further away. Students listed uses: driving, robotic surgery, crop growth tracking, terrain from the air, pits on turbine blades and warehouse robots. Depth comes from two cameras (stereo), from LiDAR or time of flight, or from one image with a learned model.</p>
<h3>Optical flow</h3>
{steps("One pixel's flow", [
    'A bright point is at (10, 10) in frame t and at (13, 14) in frame t + 1.',
    'Flow (u, v) = (3, 4). Magnitude √(9 + 16) = 5 pixels per frame.',
    'The direction is arctan(4 ÷ 3) ≈ 53° below the horizontal, since image y grows downwards. The whole flow field is H × W × 2.'])}
{note('Same body, different head. An FCN, U-Net or DeepLab body is reused across the family. Change the last layer from C class channels to 1 channel (depth), 2 (flow) or K (heat maps) and change the loss to match.', 'tip')}
{ladder(
    '<p>Segmentation colours in every pixel of a photo with what it shows: road, car, person or sky. A box only says roughly where something is. A mask gives its exact shape, which matters for a road, a tumour or a weed.</p>',
    '<p>The network outputs H × W × C scores. SoftMax at each pixel gives probabilities, and argmax picks one class. Semantic masks cannot count touching objects, instance masks can, panoptic does both. Downsampling helps recognition but erases thin and small structures.</p>',
    '<p>Convolutions are translation equivariant and global pooling is invariant, so segmentation keeps the grid. The receptive field grows as r += (k − 1) d j. Information lost in the encoder is gone for good by the data processing inequality, so architectures must add paths around the bottleneck. PQ = SQ × RQ scores panoptic output.</p>',
    '<p>Label efficient segmentation (weak, semi and self supervised learning, and foundation model assisted labelling) is a major research theme. Strided networks are not truly shift equivariant, and anti-aliased downsampling (blur before subsampling) restores much of it. Panoptic methods now use one mask classification model for semantic, instance and panoptic output.</p>')}
''', kw=['dense prediction', 'depth estimation', 'optical flow', 'surface normals', 'keypoints', 'heat maps', 'stereo', 'LiDAR', 'monocular depth', 'same body different head'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Semantic segmentation gives', ['One label per image', 'A box per object', 'A class label for every pixel', 'A caption'], 2,
       'Dense prediction.', 'It is classification repeated at every pixel.')
K.quiz('e', 'A 128 × 128 image with 4 classes. The output before argmax is', ['128 × 128', '128 × 128 × 4', '4 × 1', '128 × 4'], 1,
       'One map per class.', 'Before argmax H × W × C. After argmax it becomes 128 × 128.')
K.quiz('e', 'Two touching cars in a semantic mask', ['Get different colours', 'Merge into one blob of the class car', 'Disappear', 'Become background'], 1,
       'Semantic segmentation does not count.', 'Every car pixel has the same label, so touching cars form one region.')
K.quiz('m', 'Why is the final 1 × 1000 ImageNet output useless for segmentation?', ['It is too big', 'It is one vector with no location, while segmentation needs a label at every pixel', 'It uses sigmoid', 'It has 1000 channels per pixel'], 1,
       'Where is the dog?', 'The head must be replaced by one that outputs C maps.')
K.quiz('m', 'Why can inference skip SoftMax and take the argmax of the logits?', ['SoftMax is random', 'The exponential is increasing and all classes share one denominator, so the order is unchanged', 'Logits are probabilities', 'Argmax needs negative numbers'], 1,
       'Order preserving.', 'The winning class is the same either way.')
K.quiz('m', 'A pixel can be both vessel and lesion. Which output suits it?', ['SoftMax over classes', 'One sigmoid per class', 'Argmax only', 'A box'], 1,
       'Several labels at once.', 'SoftMax forces exactly one class. Sigmoids are independent.')
K.quiz('m', 'Convolution layers are', ['Invariant to shifts', 'Equivariant to shifts: shift the input and the map shifts', 'Neither', 'Only rotation invariant'], 1,
       'y′[n] = y[n − a].', 'Global pooling is what makes a classifier invariant.')
K.quiz('h', 'Why is downsampling both useful and harmful for segmentation?', ['It is only harmful', 'It enlarges the receptive field and adds meaning, but loses boundaries, thin structures and small objects', 'It only saves memory', 'It changes the classes'], 1,
       'WHAT against WHERE.', 'The whole chapter is about keeping the benefit without paying the cost.')
K.quiz('h', 'If lane markings vanish in the encoder, can a better decoder restore them?', ['Yes, with more layers', 'No. The decoder only sees the bottleneck, so lost information cannot come back', 'Yes, with bilinear upsampling', 'Only for thick lanes'], 1,
       'Data processing inequality.', 'I(X, Ŷ) ≤ I(X, Z). Skips give the decoder another path to the input.')
K.quiz('h', 'Which layer holds the best boundary detail?', ['The 16 × 16 bottleneck', 'A 256 × 256 early layer', 'The classifier', 'All equal'], 1,
       'One cell per pixel.', 'A 16 × 16 cell summarises 256 pixels, so a boundary inside it is invisible.')
K.quiz('x', 'Four 3 × 3 layers all with dilation 2 and stride 1. What goes wrong?', ['Nothing', 'Gridding: only every second input pixel can influence the output', 'The map shrinks', 'The parameters double'], 1,
       'Taps at even offsets only.', 'Mixing rates (1, 2, 5) or running rates in parallel avoids the holes.')
K.quiz('x', 'Panoptic quality factorises as', ['Precision × recall', 'SQ × RQ: mean IoU of matched segments times an F1 style recognition score', 'mIoU × accuracy', 'Dice ÷ IoU'], 1,
       'PQ = Σ IoU ÷ (TP + ½FP + ½FN).', 'Split the sum by TP to get SQ, and TP ÷ (TP + ½FP + ½FN) is RQ.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many pixel predictions does a 512 × 512 image need?', '262144', 'One label per pixel.',
       ['Rows 512.', 'Columns 512.', eq('512 × 512 = 262,144')], check=262144)
K.calc('e', 'A 128 × 128 image with 4 classes. How many numbers are in the output before argmax?', '65536', 'H × W × C.',
       ['128 × 128 = 16,384 pixels.', '4 scores each.', eq('16,384 × 4 = 65,536')], check=65536)
K.calc('e', 'Logits [0, −0.51, −0.91, 0.70, 2.78] for road, car, person, building, sky. What is P(sky)? Give three decimals.', '0.801', 'e<sup>2.78</sup> ÷ Σ e<sup>z</sup>.',
       ['Exponentials: 1, 0.600, 0.403, 2.014, 16.119.', 'Sum = 20.136.', eq('P(sky) = 16.119 ÷ 20.136 ≈ 0.801')], check=0.8005, tol=0.0011)
K.calc('m', 'What fraction of its bounding box does a perfect ellipse fill? Give three decimals.', '0.785', 'πab ÷ (2a × 2b).',
       ['Ellipse area πab.', 'Box area 4ab.', eq('π ÷ 4 ≈ 0.785')], check=3.14159265 / 4, tol=0.0006)
K.calc('m', 'Panoptic: three matched segments with IoU 0.8, 0.7 and 0.9, one FP and one FN. What is PQ? Give two decimals.', '0.6', 'SQ × RQ.',
       ['SQ = 2.4 ÷ 3 = 0.80.', 'RQ = 3 ÷ (3 + 0.5 + 0.5) = 0.75.', eq('PQ = 0.80 × 0.75 = 0.60')], check=0.6)
K.calc('m', 'Four plain 3 × 3 convolutions, stride 1. What is the receptive field?', '9', 'Each adds k − 1 = 2.',
       ['Start at r = 1.', 'Four layers add 2 each.', eq('r = 1 + 4 × 2 = 9')], check=9)
K.calc('m', 'Four 3 × 3 layers, with stride 2 on layers 2 and 4. What is the receptive field?', '13', 'r += 2j, then j *= s.',
       ['Layer 1: r = 3, j = 1. Layer 2: r = 5, then j = 2.', 'Layer 3: r = 5 + 2 × 2 = 9.', 'Layer 4: r = 9 + 2 × 2 = 13, then j = 4.', eq('r = 13')], check=13)
K.calc('h', 'Layers (stride, dilation) = (1, 1), (2, 1), (1, 2), (1, 4), all 3 × 3. What is the final receptive field?', '29', 'r += 2 · d · j.',
       ['L1: r = 3, j = 1. L2: r = 5, j = 2.', 'L3: r = 5 + 2 × 2 × 2 = 13.', 'L4: r = 13 + 2 × 4 × 2 = 29.', eq('r = 29')], check=29)
K.calc('h', 'A lane marking is 6 pixels wide. What fraction of one feature cell does it cover at stride 16? Give three decimals.', '0.375', 'Width ÷ stride.',
       ['A cell spans 16 pixels.', 'The marking covers 6 of them.', eq('6 ÷ 16 = 0.375'), 'Usually outvoted by background.'], check=0.375)
K.calc('h', 'Requiring at least 2 feature cells across a 6 pixel marking, what is the largest stride?', '3', '6 ÷ s ≥ 2.',
       ['Cells across = 6 ÷ s.', 'Need 6 ÷ s ≥ 2.', eq('s ≤ 3')], check=3)
K.calc('x', 'A Cityscapes image is 1024 × 2048 with 19 classes. How many numbers are in the output tensor before argmax?', '39845888', 'H × W × C.',
       ['1024 × 2048 = 2,097,152 pixels.', 'Times 19 classes.', eq('39,845,888 numbers'), 'About 159 MB as 32-bit floats for one image.'], check=39845888)
K.calc('x', 'A 6 × 6 blob is downsampled ×4 by strict majority and only one 4 × 4 block survives. After upsampling, what is the blob IoU? Give three decimals.', '0.444', 'The surviving block is inside the blob.',
       ['Prediction: one block, 16 pixels, all inside the blob.', 'Union = the blob, 36 pixels.', eq('IoU = 16 ÷ 36 ≈ 0.444')], check=16 / 36, tol=0.0006)

# ---------------------------------------------------------------- assignments
K.assign('argmax', 'e', 'Scores to a mask',
         '<p>Write <code>to_mask(scores)</code> where <code>scores[r][c]</code> is a list of C class scores. Return the H × W mask of class indices (the first index wins a tie).</p>',
         '''
def to_mask(scores):
    # your code here
    pass
''', [('to_mask([[[0.1, 0.9], [0.8, 0.2]], [[0.3, 0.7], [0.6, 0.4]]])', [[1, 0], [1, 0]]),
      ('to_mask([[[0, -0.51, -0.91, 0.7, 2.78]]])', [[4]]),
      ('to_mask([[[1, 1, 0]]])', [[0]])],
         '''
def to_mask(scores):
    return [[px.index(max(px)) for px in row] for row in scores]
''', 'list.index(max(list)) returns the first position of the largest value.',
         '<p>No SoftMax is needed, because argmax of the logits equals argmax of the probabilities.</p>')
K.assign('components', 'm', 'Count connected regions',
         '<p>Write <code>components(mask)</code> that counts the groups of non-zero pixels connected up, down, left or right (not diagonally).</p>',
         '''
def components(mask):
    # your code here
    pass
''', [('components([[0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1]])', 2), ('components([[0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1]])', 3),
      ('components([[0, 0], [0, 0]])', 0), ('components([[1, 0], [0, 1]])', 2)],
         '''
def components(mask):
    h, w = len(mask), len(mask[0])
    seen = set()
    count = 0
    for r in range(h):
        for c in range(w):
            if mask[r][c] and (r, c) not in seen:
                count += 1
                stack = [(r, c)]
                seen.add((r, c))
                while stack:
                    y, x = stack.pop()
                    for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny][nx] and (ny, nx) not in seen:
                            seen.add((ny, nx))
                            stack.append((ny, nx))
    return count
''', 'Scan the grid. When you meet an unvisited foreground pixel, count one and flood fill from it with a stack.',
         '<p>The first test is two touching cars plus one more: 2 regions for 3 real cars. Diagonal neighbours are separate under 4 connectivity.</p>')
K.assign('rf', 'm', 'Receptive field calculator',
         '<p>Write <code>receptive_field(layers)</code> where each layer is <code>(k, s, d)</code>: kernel, stride, dilation. Return the list of receptive fields after each layer.</p>',
         '''
def receptive_field(layers):
    # your code here
    pass
''', [('receptive_field([(3, 1, 1)] * 4)', [3, 5, 7, 9]), ('receptive_field([(3, 1, 1), (3, 2, 1), (3, 1, 2), (3, 1, 4)])', [3, 5, 13, 29]),
      ('receptive_field([(3, 1, 1), (3, 1, 2), (3, 1, 4), (3, 1, 8)])', [3, 7, 15, 31]), ('receptive_field([(7, 2, 1), (3, 2, 1)])', [7, 11])],
         '''
def receptive_field(layers):
    r, j, out = 1, 1, []
    for k, s, d in layers:
        r += (k - 1) * d * j
        j *= s
        out.append(r)
    return out
''', 'Keep two numbers, the field r and the jump j. Update r first, then j.',
         '<p>The last test is the ResNet stem: a 7 × 7 stride 2 convolution followed by a 3 × 3 stride 2 max pool gives a field of 11.</p>')

K.must('The task', 'I ∈ ℝ<sup>H×W×3</sup> → Y ∈ {1..C}<sup>H×W</sup>. Before argmax H × W × C, after argmax H × W. 512 × 512 needs 262,144 predictions. Use the cheapest task that answers the question.')
K.must('Semantic, instance, panoptic', 'Semantic: class per pixel, cannot count touching objects. Instance: object identity. Panoptic: both, scored by PQ = SQ × RQ.')
K.must('SoftMax per pixel', 'p<sub>c</sub> = e<sup>z<sub>c</sub></sup> ÷ Σ e<sup>z<sub>k</sub></sup>. argmax of SoftMax = argmax of logits. SoftMax for one label per pixel, sigmoids for multi-label. Ignore label 255 gets no loss.')
K.must('Why classifiers fail', 'Convolution is equivariant, global pooling is invariant. Downsampling grows the receptive field (r += (k − 1)dj) but erases thin and small structures. What the encoder drops, the decoder cannot recover.')
K.must('WHAT and WHERE', 'Early layers: high resolution, WHERE. Deep layers: semantics, WHAT. Every architecture in the next chapter combines the two. Same body, different head for depth, flow and keypoints.')

T = K.topic(
    slug='segmentation-basics', topic='segmentation', step=(6, 'Understanding every pixel', 'cv-segmentation', 'Semantic segmentation from the output tensor to modern architectures, losses, metrics and debugging.', 'College and masters'),
    title='What segmentation predicts', short='Segmentation basics', badge='6.1', minutes=50,
    lead='Move from one label per image to one label per pixel. See what the network outputs, how SoftMax and argmax turn scores into a mask, and why a normal classifier throws away exactly the location information segmentation needs.',
    desc='Classification, detection and segmentation compared, why boxes are not enough, semantic, instance and panoptic segmentation, output tensors, SoftMax and argmax per pixel, ground truth masks, equivariance, receptive field, the downsampling trade-off and the dense prediction family.',
    summary='Pixel level classification, semantic, instance and panoptic masks, SoftMax per pixel, receptive field, the downsampling trade-off and dense prediction.',
    keywords=['semantic segmentation', 'instance segmentation', 'panoptic', 'mask', 'dense prediction', 'SoftMax', 'argmax', 'receptive field', 'equivariance', 'downsampling', 'depth estimation', 'optical flow'],
    recap='<p>Segmentation labels every pixel. The network outputs one score map per class, and argmax turns them into a mask. Classifiers pool away location on purpose, and downsampling erases thin and small structures that no decoder can recover. The architectures that follow are all ways of combining deep meaning with early detail.</p>')
