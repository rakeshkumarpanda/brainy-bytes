# Chapter 10: IoU, non-maximum suppression, one-stage and two-stage detectors, multi-stage training,
# RetinaNet with ResNet and FPN, Faster R-CNN, bilinear interpolation and RoIAlign.
# Source: lectures 5 and 6, chapters 9 to 12.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('nms', r'''
# Non-maximum suppression, per class, on seven detections
boxes = {"P1": (40, 40, 120, 200), "P4": (108, 52, 186, 212), "P2": (46, 48, 126, 206),
         "D1": (200, 130, 300, 200), "P3": (30, 30, 112, 195), "D2": (212, 138, 306, 206)}
scores = {"P1": 0.92, "P4": 0.88, "P2": 0.85, "D1": 0.75, "P3": 0.60, "D2": 0.40}
thr = float(input("IoU threshold: "))

def iou(a, b):
    iw = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    ih = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = iw * ih
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter)

order = sorted(scores, key=scores.get, reverse=True)
kept = []
for name in order:
    same = [k for k in kept if k[0] == name[0]]          # same class letter
    if all(iou(boxes[name], boxes[k]) <= thr for k in same):
        kept.append(name)
print("kept:", kept)
''', stdin='0.5\n')

K.code('bilinear', r'''
# Bilinear interpolation at a point between four pixels
f = {(2, 4): 10, (3, 4): 20, (2, 5): 30, (3, 5): 50}
x, y = [float(v) for v in input("x y: ").split()]

i, j = int(x), int(y)
u, v = x - i, y - j                                       # fractions inside the cell
w = {(i, j): (1 - u) * (1 - v), (i + 1, j): u * (1 - v),
     (i, j + 1): (1 - u) * v, (i + 1, j + 1): u * v}
for corner in w:
    print(corner, "weight", round(w[corner], 3))
value = sum(w[c] * f[c] for c in w)
print("f(x, y) =", round(value, 3))
''', stdin='2.3 4.6\n')

K.code('fpn', r'''
# Shapes and parameters of the FPN top-down path (ResNet-50, 640 x 640 input)
C = {3: (80, 512), 4: (40, 1024), 5: (20, 2048)}        # size and channels
d = 256                                                  # FPN width
total = 0
for level in (5, 4, 3):
    size, ch = C[level]
    lateral = ch * d + d                                 # 1 x 1 conv with bias
    smooth = 3 * 3 * d * d + d                           # 3 x 3 conv with bias
    total += lateral + smooth
    print("P%d: %d x %d x %d, lateral %d, smooth %d" % (level, size, size, d, lateral, smooth))
print("parameters in the top-down path:", total)
''')

K.lesson('iou', 'Intersection over union', f'''
<p>A student first called it interaction of union. It is <b>intersection over union</b>: the area two boxes share divided by the area they cover together. It is the single most used number in detection: for matching anchors in training, for removing duplicates, and for marking predictions right or wrong in evaluation.</p>
{fx('IoU', 'IoU(<i>A</i>, <i>B</i>) = ' + frac('|<i>A</i> ∩ <i>B</i>|', '|<i>A</i> ∪ <i>B</i>|') + ' = ' + frac('|<i>A</i> ∩ <i>B</i>|', '|<i>A</i>| + |<i>B</i>| − |<i>A</i> ∩ <i>B</i>|'), 'Between 0 and 1. The overlap rectangle runs from the larger of the left edges to the smaller of the right edges, and the same for top and bottom.', key=True)}
{viz('iou')}
{steps('The lecture example', [
    'A = (50, 50, 150, 150) and B = (80, 70, 180, 170), each 100 × 100 = 10,000.',
    'Overlap x: max(50, 80) = 80 to min(150, 180) = 150, width 70. Overlap y: 70 to 150, height 80. Area 5,600.',
    'Union: 10,000 + 10,000 − 5,600 = 14,400.',
    'IoU = 5,600 ÷ 14,400 ≈ 0.389. A miss at the usual 0.5 threshold. The box (60, 55, 160, 155) gives 8,550 ÷ 11,450 ≈ 0.747, a hit.'])}
<h3>Useful facts</h3>
<ul>
<li>IoU = 0 exactly when the boxes do not overlap, and IoU = 1 exactly when they are identical.</li>
<li>It is symmetric, IoU(A, B) = IoU(B, A), and unchanged by scaling the whole image.</li>
<li>For two equal squares shifted sideways by a fraction s of their width, IoU = (1 − s) ÷ (1 + s). A 20% shift already drops it to 0.667, and a 50% shift to 0.333.</li>
</ul>
''', kw=['IoU', 'intersection over union', 'overlap', 'union', 'Jaccard index', 'threshold', 'shifted boxes'])

K.lesson('nms', 'Removing duplicates with NMS', f'''
<p>Nothing stops several neighbouring anchors from all detecting the same person, each with a slightly different box and score. The lecturer\'s recipe: every box has a confidence score, so keep the highest one and remove the lower scoring boxes that overlap it too much. This is <b>non-maximum suppression</b> (NMS).</p>
<ol>
<li>Sort the detections by score, highest first.</li>
<li>Take the best remaining box and keep it.</li>
<li>Remove every remaining box of the same class whose IoU with it is above the threshold.</li>
<li>Repeat until no boxes remain.</li>
</ol>
{steps('The slide example, threshold 0.5', [
    'Scores: A 0.95, B 0.89, D 0.81, C 0.75. IoU with A: B 0.82, C 0.71, D 0.10.',
    'Keep A. B (0.82) and C (0.71) overlap it by more than 0.5, so they are removed. D (0.10) stays.',
    'Keep D, the next best. Nothing is left.',
    'Result {A, D}: A is the person, B and C were duplicates, and D is the dog, a different object.'])}
{viz('nms')}
{code('nms')}
<h3>Weak spots</h3>
{table(['Problem', 'What happens'], [
    ['Crowds', 'Two real people who overlap by more than the threshold: the lower scoring one is deleted.'],
    ['Per class only', 'A dog box and a cat box on the same animal both survive.'],
    ['One fixed threshold', 'Too low removes real neighbours (lower recall), too high keeps duplicates (lower precision).']])}
{fx('Soft-NMS', '<i>s</i><sub><i>i</i></sub> ← <i>s</i><sub><i>i</i></sub> · <i>e</i><sup>−IoU(<i>M</i>, <i>b</i><sub><i>i</i></sub>)² ÷ σ</sup>', 'Instead of deleting, decay the score of each box by how much it overlaps the kept box <i>M</i>. Near duplicates sink, slightly overlapping neighbours survive.')}
{note('The lecturer mentioned comparing with the ground truth. At test time there is no ground truth, so NMS uses only scores and box to box IoU. Ground truth is used in training (target assignment) and in evaluation.', 'warn')}
<p>Newer designs go further. DETR (2020) predicts a fixed set of boxes with a transformer and matches them one to one with the objects during training, so it needs no NMS at all.</p>
''', kw=['NMS', 'non-maximum suppression', 'duplicates', 'score threshold', 'IoU threshold', 'soft-NMS', 'crowd', 'per class', 'DETR'])

K.lesson('stages', 'One stage or two stage', f'''
<p>The lecturer opened this part with a challenge: anyone can call YOLO from a library and run it in an hour, for example <code>YOLO("yolov8n.pt")("image.jpg")</code> with the ultralytics package. But what is happening behind it? Detectors are built from a classification backbone (VGG, Inception, ResNet) plus a detection part, in one of two patterns called <b>meta-architectures</b>.</p>
{table(['', 'One stage', 'Two stage'], [
    ['Idea', 'Image straight to boxes and classes', 'Propose likely regions first, then refine each one'],
    ['Examples', 'SSD, YOLO, RetinaNet', 'R-CNN, Fast R-CNN, Faster R-CNN, Mask R-CNN'],
    ['Structure', 'Backbone with a class head and a box head', 'Backbone, region proposals, crop each region, then classify and refine'],
    ['Strength', 'Simple operations, easy to run fast', 'Per object features, easy to add masks or keypoints']])}
<p>The old rule was one stage is fast, two stage is accurate. The slides call that outdated: modern systems blur the line. The lecturer\'s answer to which is better: it depends on your domain, so measure accuracy and speed on your own data.</p>
<h3>Class agnostic proposals</h3>
<p>The first stage of a two stage detector only answers is there an object here, and refines the box. It never says which object. That is what <b>class agnostic</b> means. The lecturer also introduced task agnostic, a model that uses no task identity, as opposed to task aware.</p>
<h3>Training several stages</h3>
<p>The lecturer\'s analogy: semesters. How you do in semester 1 affects semester 2, so the stages depend on each other.</p>
{table(['Mode', 'How', 'Assumes'], [
    ['Stage wise', 'Train stage 1 with its loss, feed its output to stage 2 and train that separately', 'The stages are independent'],
    ['Joint (end to end)', 'Add all the losses and back-propagate from the last stage to the first', 'The stages depend on each other'],
    ['Hybrid', 'Stage wise first, then joint fine tuning, or freeze stage 1 and train stage 2', 'Stability first, then end to end tuning']])}
<p>Faster R-CNN is trained jointly with four losses: proposal classification and proposal box in stage 1, object class and object box in stage 2. This works because the crop and resize step is differentiable, as the last lesson shows.</p>
''', kw=['one stage', 'two stage', 'meta-architecture', 'YOLO', 'SSD', 'Faster R-CNN', 'region proposal', 'class agnostic', 'task agnostic', 'stage wise training', 'joint training', 'end to end'])

K.lesson('fpn', 'RetinaNet and the feature pyramid', f'''
<p><b>RetinaNet</b> (Lin and colleagues, 2017) is the single stage case study. Its three ideas: a multi-resolution feature extractor (ResNet with a feature pyramid network), focal loss from the last chapter, and the small starting bias.</p>
<h3>The hierarchical assumption</h3>
<p>The lecturer asked for the basic assumption of a CNN. Students offered locality and translation invariance. Her answer: an image is processed hierarchically, fine details first, then broader features, so the resolution keeps reducing through the network. Both views are right at different levels: locality and weight sharing are the built in biases, and stacking layers with downsampling gives the hierarchy.</p>
{table(['', 'Early layers', 'Deep layers'], [
    ['Spatial resolution', 'High, for example 80 × 80', 'Low, for example 20 × 20'],
    ['Semantic meaning', 'Low: edges, colours, blobs', 'High: parts and whole objects'],
    ['Receptive field', 'Small', 'Large, sees context']])}
<p>Several students guessed that early layers carry more meaning because they hold more numbers. The lecturer corrected this: meaning develops as layers go deeper. That is the problem for small objects. They need high resolution maps, which come from early layers, which have little meaning.</p>
<h3>FPN fixes the trade off</h3>
{fxs(
    fx('One FPN merge', '<i>P</i><sub><i>l</i></sub> = Conv<sub>1×1</sub>(<i>C</i><sub><i>l</i></sub>) + Upsample<sub>×2</sub>(<i>P</i><sub><i>l</i>+1</sub>)', 'The 1 × 1 convolution matches the channel count (to 256), the upsampling matches the size, then the two maps are added. A 3 × 3 convolution then smooths each result.', key=True),
    fx('Anchors scored', 'Σ<sub>levels</sub> (cells) × <i>A</i>', 'For 640 × 640: (6,400 + 1,600 + 400 + 100 + 25) × 9 = 76,725 anchors.'))}
{viz('pyramid')}
{code('fpn')}
<p>The same class head and box head (four 3 × 3 layers of 256 channels each) run on every level. Sharing works because FPN has made every level equally rich in meaning. The lecturer\'s summary: the large map gains meaning from the small one, and the small one gains detail from the large one.</p>
''', kw=['RetinaNet', 'FPN', 'feature pyramid network', 'hierarchical', 'semantic', 'spatial resolution', 'top-down path', 'lateral connection', '1x1 convolution', 'upsampling', 'shared heads', 'anchor count'])

K.lesson('roialign', 'Faster R-CNN, interpolation and RoIAlign', f'''
<p><b>Faster R-CNN</b> is the two stage case study. Stage 1 is a <b>region proposal network</b>, itself a small single stage detector that deliberately over-predicts class agnostic boxes. Stage 2 crops each proposal from the shared feature map, resizes it to a fixed size such as 7 × 7, and classifies and refines it. Cropping features rather than pixels is cheap, because the features already exist.</p>
<h3>How do you shrink an image without a network?</h3>
<p>The lecturer asked how to turn a 256 × 256 image into 32 × 32 without any neural network or pooling. The answer is <b>interpolation</b>: compute new pixel values at new positions from their neighbours. Nearest neighbour copies the closest pixel, bilinear blends the 4 nearest, bicubic uses 16. Quantisation is a different thing: it keeps the size and reduces the bits per pixel. A student asked whether information is lost. Yes, 32 × 32 is low resolution, but the layout and relationships between objects are kept.</p>
{fx('Bilinear interpolation', '<i>f</i>(<i>x</i>, <i>y</i>) = (1 − <i>u</i>)(1 − <i>v</i>) <i>f</i><sub>00</sub> + <i>u</i>(1 − <i>v</i>) <i>f</i><sub>10</sub> + (1 − <i>u</i>)<i>v</i> <i>f</i><sub>01</sub> + <i>uv</i> <i>f</i><sub>11</sub>', '<i>u</i> and <i>v</i> are the fractional parts of <i>x</i> and <i>y</i>. Each corner\'s weight is the area of the rectangle opposite it. The weights add to 1.', key=True)}
{viz('bilinear')}
{steps('The lecture green dot at (2.3, 4.6)', [
    'Corners: f(2, 4) = 10, f(3, 4) = 20, f(2, 5) = 30, f(3, 5) = 50. Here u = 0.3 and v = 0.6.',
    'Weights: (0.7)(0.4) = 0.28, (0.3)(0.4) = 0.12, (0.7)(0.6) = 0.42, (0.3)(0.6) = 0.18. They add to 1.',
    'f = 10(0.28) + 20(0.12) + 30(0.42) + 50(0.18) = 2.8 + 2.4 + 12.6 + 9.0 = 26.8.',
    'The answer lies between 10 and 50, closest to the corner nearest the point.'])}
{code('bilinear')}
<h3>RoIAlign</h3>
<p>A proposal rarely lines up with the feature grid. <b>RoIAlign</b> (from Mask R-CNN) divides the proposal into a fixed grid of bins and samples each bin centre with bilinear interpolation. The older RoI pooling rounded the proposal to whole cells, misaligning features by up to half a cell, which hurt masks. Because bilinear interpolation is smooth, gradients flow back through the crop, and the whole detector trains end to end.</p>
{steps('RoIAlign with a 2 × 2 output', [
    'Feature map f(x, y) = 10y + x. Proposal (0.8, 1.2, 4.4, 4.8).',
    'Bin size: (4.4 − 0.8) ÷ 2 = 1.8 wide and (4.8 − 1.2) ÷ 2 = 1.8 tall.',
    'Bin centres: x = 1.7 and 3.5, y = 2.1 and 3.9.',
    'Sampling gives [[22.7, 24.5], [40.7, 42.5]], a fixed size output whatever the proposal size. Each equals 10y + x, because bilinear interpolation reproduces such a formula exactly.'])}
{ladder(
    '<p>A detector often draws several boxes around the same thing. NMS keeps the most confident box and throws away the copies that overlap it a lot. Some detectors find objects in one go, others first guess where objects might be and then look closer.</p>',
    '<p>IoU = |A ∩ B| ÷ |A ∪ B|. NMS sorts by score and removes same class boxes with IoU above a threshold. One stage detectors (SSD, YOLO, RetinaNet) predict directly, two stage ones (Faster R-CNN) propose, crop with RoIAlign and refine. FPN gives every pyramid level deep features.</p>',
    '<p>FPN merges by 1 × 1 lateral convs, nearest upsampling and addition, then 3 × 3 smoothing, and heads are shared across levels. RoIAlign uses bilinear sampling, which is piecewise linear, so gradients reach both features and box coordinates. Soft-NMS uses a Gaussian decay e<sup>−IoU² ÷ σ</sup>.</p>',
    '<p>Set prediction (DETR and its faster variants) removes NMS by bipartite matching. Real time detectors such as recent YOLO versions train with one to one assignment to become NMS free. BiFPN in EfficientDet learns weighted bidirectional fusion across levels, and transformer backbones replace ResNet in many current detectors.</p>')}
''', kw=['Faster R-CNN', 'region proposal network', 'RPN', 'crop and resize', 'interpolation', 'nearest neighbour', 'bilinear', 'bicubic', 'quantisation', 'RoIAlign', 'RoI pooling', 'Mask R-CNN', 'end to end'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'IoU stands for', ['Interaction of union', 'Intersection over union', 'Index of uncertainty', 'Image of use'], 1,
       'A ratio of two areas.', 'Shared area divided by combined area.')
K.quiz('e', 'Two boxes do not touch at all. Their IoU is', ['1', '0', '0.5', 'Undefined'], 1, 'No shared area.', 'The intersection is 0, so the ratio is 0.')
K.quiz('e', 'What does NMS keep first?', ['The largest box', 'The box with the highest score', 'The leftmost box', 'A random box'], 1,
       'Sort first.', 'NMS sorts by confidence and keeps the best box, then removes its overlapping duplicates.')
K.quiz('m', 'Why does a cat box on a dog survive NMS?', ['Its score is higher', 'NMS runs separately for each class, so boxes of different classes never suppress each other', 'Its IoU is 0', 'Cats are always kept'], 1,
       'Per class.', 'Only same class boxes are compared, unless you run a class agnostic version.')
K.quiz('m', 'Does NMS use the ground truth at test time?', ['Yes, to pick the best box', 'No, only scores and IoU between predicted boxes', 'Only for small objects', 'Only in two stage detectors'], 1,
       'There is no ground truth at test time.', 'Ground truth is used in training (assignment) and evaluation, never in NMS.')
K.quiz('m', 'In a two stage detector, the region proposal network is called class agnostic because', ['It knows every class', 'It only decides object or background and refines the box, without naming the class', 'It ignores boxes', 'It has no loss'], 1,
       'Irrespective of class.', 'Stage 2 names the class. Stage 1 only proposes where objects are.')
K.quiz('m', 'Early CNN layers have', ['Low resolution and high meaning', 'High resolution and low meaning', 'High resolution and high meaning', 'No receptive field'], 1,
       'Meaning develops with depth.', 'Early maps are large but only see edges and blobs. Deep maps are small but understand objects.')
K.quiz('h', 'In FPN, why is a 1 × 1 convolution applied before adding two maps?', ['To blur them', 'To make the channel counts equal (for example 2,048 to 256)', 'To double the size', 'To apply SoftMax'], 1,
       'Addition needs the same shape.', 'The 1 × 1 conv matches channels, the ×2 upsampling matches height and width.')
K.quiz('h', 'Why can Faster R-CNN be trained end to end with one summed loss?', ['It has only one stage', 'Crop and resize uses bilinear interpolation, which is differentiable, so gradients reach the shared features', 'It uses NMS in training', 'Its losses are equal'], 1,
       'Can gradients pass through the crop?', 'Bilinear weights are smooth functions of position, so stage 2 losses update the backbone that stage 1 also uses.')
K.quiz('h', 'Which statement about one stage and two stage detectors does the lecture support?', ['One stage is always faster and less accurate', 'The divide is fuzzy today, so measure accuracy and speed on your own task', 'Two stage detectors cannot run on GPUs', 'They are identical'], 1,
       'The slide calls the old rule outdated.', 'Modern systems blur the distinction. Evaluate, then choose.')
K.quiz('x', 'Soft-NMS with σ = 0.5 meets a box with IoU 0.857 to the kept box. Its score is multiplied by about', ['0.96', '0.23', '0.86', '0'], 1,
       'e<sup>−IoU² ÷ σ</sup>.', 'e<sup>−0.734 ÷ 0.5</sup> = e<sup>−1.469</sup> ≈ 0.23, a strong demotion without deleting it.')
K.quiz('x', 'Why did RoIAlign replace RoI pooling for masks?', ['It is faster', 'RoI pooling rounds coordinates to whole cells, misaligning features by up to half a cell, while RoIAlign keeps fractions and interpolates', 'RoIAlign uses no features', 'RoI pooling cannot handle boxes'], 1,
       'Quantisation of coordinates.', 'Half a cell on a stride 16 map is 8 pixels, harmless for a box score but visible in a pixel mask.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Boxes (50, 50, 150, 150) and (80, 70, 180, 170). What is their IoU? Give three decimals.', '0.389', 'Overlap 70 × 80.',
       ['Intersection: 70 × 80 = 5,600.', 'Union: 10,000 + 10,000 − 5,600 = 14,400.', eq('IoU = 5,600 ÷ 14,400 ≈ 0.389')], check=5600 / 14400, tol=0.0006)
K.calc('e', 'Boxes (50, 50, 150, 150) and (60, 55, 160, 155). What is their IoU? Give three decimals.', '0.747', 'Find the overlap width and height.',
       ['Overlap: x 60 to 150 = 90, y 55 to 150 = 95, area 8,550.', 'Union: 20,000 − 8,550 = 11,450.', eq('IoU = 8,550 ÷ 11,450 ≈ 0.747')], check=8550 / 11450, tol=0.0006)
K.calc('e', 'A 200 × 200 box completely contains a 100 × 100 true box. What is the IoU?', '0.25', 'The intersection is the small box.',
       ['Intersection = 10,000.', 'Union = 40,000.', eq('IoU = 10,000 ÷ 40,000 = 0.25'), 'Covering the object is not enough. The box must also be tight.'], check=0.25)
K.calc('m', 'Two equal squares are shifted sideways by 20% of their width. What is their IoU? Give three decimals.', '0.667', 'IoU = (1 − s) ÷ (1 + s).',
       ['Overlap is (1 − 0.2) of one square.', 'Union is (1 + 0.2) of one square.', eq('IoU = 0.8 ÷ 1.2 ≈ 0.667')], check=0.8 / 1.2, tol=0.0006)
K.calc('m', 'In the slide example (A 0.95, B 0.89, D 0.81, C 0.75, IoU with A of 0.82, 0.10 and 0.71 for B, D and C), how many boxes survive NMS at threshold 0.5?', '2', 'Keep A, then check the others against it.',
       ['Keep A.', 'B (0.82) and C (0.71) exceed 0.5 and are removed. D (0.10) survives.', eq('kept = {A, D}, so 2 boxes')], check=2)
K.calc('m', 'Soft-NMS (σ = 0.5) meets a box with score 0.88 and IoU 0.142 to the kept box. What is its new score? Give three decimals.', '0.845', 'New score = s × e<sup>−IoU² ÷ σ</sup>.',
       ['IoU² = 0.0202, divided by 0.5 gives 0.0403.', 'e<sup>−0.0403</sup> ≈ 0.960.', eq('0.88 × 0.960 ≈ 0.845'), 'The real second person keeps almost all its score.'], check=0.88 * 2.718281828459045 ** (-0.142 ** 2 / 0.5), tol=0.0006)
K.calc('m', 'Bilinear interpolation at (2.3, 4.6) with f(2, 4) = 10, f(3, 4) = 20, f(2, 5) = 30, f(3, 5) = 50. What is f? Give one decimal.', '26.8', 'Weights (1 − u)(1 − v), u(1 − v), (1 − u)v, uv with u = 0.3, v = 0.6.',
       ['Weights: 0.28, 0.12, 0.42, 0.18.', 'Products: 2.8, 2.4, 12.6, 9.0.', eq('f = 26.8')], check=26.8)
K.calc('h', 'In the same example, what weight does the corner (2, 5) get?', '0.42', 'It is (1 − u) × v.',
       ['u = 0.3, so 1 − u = 0.7.', 'v = 0.6.', eq('0.7 × 0.6 = 0.42'), 'The largest weight, because (2, 5) is the closest corner.'], check=0.42)
K.calc('h', 'An FPN lateral 1 × 1 convolution maps C5 with 2,048 channels to 256 channels, with biases. How many parameters?', '524544', '1 × 1 × C<sub>in</sub> × C<sub>out</sub> + C<sub>out</sub>.',
       ['Weights: 2,048 × 256 = 524,288.', 'Biases: 256.', eq('524,288 + 256 = 524,544')], check=524544)
K.calc('h', 'How many parameters does one 3 × 3 smoothing convolution from 256 to 256 channels have, with biases?', '590080', '3 × 3 × 256 × 256 + 256.',
       ['Weights: 9 × 65,536 = 589,824.', 'Biases: 256.', eq('589,824 + 256 = 590,080')], check=590080)
K.calc('x', 'RetinaNet on a 640 × 640 image uses levels with 80, 40, 20, 10 and 5 cells per side and 9 anchors per cell. How many anchors?', '76725', 'Add the squares, then multiply by 9.',
       ['6,400 + 1,600 + 400 + 100 + 25 = 8,525 cells.', 'Times 9 anchors.', eq('8,525 × 9 = 76,725'), 'With 80 classes that is about 6.1 million sigmoid scores per image.'], check=76725)
K.calc('x', 'RoIAlign divides the proposal (0.8, 1.2, 4.4, 4.8) into 2 × 2 bins. Where is the centre x of the second bin?', '3.5', 'Bin width = (x<sub>2</sub> − x<sub>1</sub>) ÷ 2.',
       ['Bin width = (4.4 − 0.8) ÷ 2 = 1.8.', 'Second bin starts at 0.8 + 1.8 = 2.6.', eq('centre = 2.6 + 0.9 = 3.5')], check=3.5)

# ---------------------------------------------------------------- assignments
K.assign('nms', 'm', 'Write NMS',
         '<p>Write <code>nms(boxes, scores, thr=0.5)</code>. Boxes are corner tuples, all one class. Return the indices of the kept boxes in the order they were kept (highest score first).</p>',
         '''
def nms(boxes, scores, thr=0.5):
    # your code here
    pass
''', [('nms([(40, 40, 120, 200), (108, 52, 186, 212), (46, 48, 126, 206), (30, 30, 112, 195)], [0.92, 0.88, 0.85, 0.60])', [0, 1]),
      ('nms([(40, 40, 120, 200), (108, 52, 186, 212)], [0.92, 0.88], 0.05)', [0]),
      ('nms([(0, 0, 10, 10), (20, 20, 30, 30)], [0.3, 0.9])', [1, 0]),
      ('nms([], [])', [])],
         '''
def nms(boxes, scores, thr=0.5):
    def iou(a, b):
        iw = max(0, min(a[2], b[2]) - max(a[0], b[0]))
        ih = max(0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = iw * ih
        return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter)
    order = sorted(range(len(boxes)), key=lambda i: scores[i], reverse=True)
    kept = []
    for i in order:
        if all(iou(boxes[i], boxes[k]) <= thr for k in kept):
            kept.append(i)
    return kept
''', 'Sort the indices by score, then keep a box only if it does not overlap any kept box too much.',
         '<p>The second test is the crowd problem: with threshold 0.05 the real second person (IoU 0.076) is deleted. This greedy version is how torchvision.ops.nms behaves.</p>')
K.assign('bilinear', 'm', 'Bilinear interpolation',
         '<p>Write <code>bilinear(img, x, y)</code> where <code>img[y][x]</code> is a grid of numbers and 0 ≤ x ≤ width − 1, 0 ≤ y ≤ height − 1. Return the bilinear value rounded to 3 decimals. On the last row or column, clamp the neighbour index so it stays inside the grid.</p>',
         '''
def bilinear(img, x, y):
    # your code here
    pass
''', [('bilinear([[10, 20], [30, 50]], 0.3, 0.6)', 26.8), ('bilinear([[10, 20], [30, 50]], 1, 1)', 50), ('bilinear([[y * 10 + x for x in range(7)] for y in range(7)], 1.7, 2.1)', 22.7), ('bilinear([[4]], 0, 0)', 4)],
         '''
def bilinear(img, x, y):
    h, w = len(img), len(img[0])
    i, j = int(x), int(y)
    u, v = x - i, y - j
    i1, j1 = min(i + 1, w - 1), min(j + 1, h - 1)
    val = (1 - u) * (1 - v) * img[j][i] + u * (1 - v) * img[j][i1] + (1 - u) * v * img[j1][i] + u * v * img[j1][i1]
    return round(val, 3)
''', 'Take the whole parts as the top left corner and the fractions as u and v.',
         '<p>The third test is the first RoIAlign sample: 10 × 2.1 + 1.7 = 22.7. Clamping matters at the edge, where x + 1 would fall outside the grid.</p>')
K.assign('levels', 'e', 'Feature pyramid sizes',
         '<p>Write <code>pyramid(n, A=9)</code> for a square input of side n. For levels 3 to 7 the map side is ceil(n ÷ 2<sup>level</sup>). Return <code>[sides, anchors]</code>, where sides is the list of five sides and anchors is the total number of cells times A.</p>',
         '''
from math import ceil

def pyramid(n, A=9):
    # your code here
    pass
''', [('pyramid(640)', [[80, 40, 20, 10, 5], 76725]), ('pyramid(640, 1)', [[80, 40, 20, 10, 5], 8525]), ('pyramid(512)', [[64, 32, 16, 8, 4], 49104])],
         '''
from math import ceil

def pyramid(n, A=9):
    sides = [ceil(n / 2 ** l) for l in range(3, 8)]
    return [sides, sum(s * s for s in sides) * A]
''', 'A list comprehension over range(3, 8) gives the five sides.',
         '<p>For 512: 4,096 + 1,024 + 256 + 64 + 16 = 5,456 cells, times 9 = 49,104 anchors.</p>')

K.must('IoU', '|A ∩ B| ÷ (|A| + |B| − |A ∩ B|). Lecture: 0.389 (miss) and 0.747 (hit) at 0.5. Equal squares shifted by s: (1 − s) ÷ (1 + s).')
K.must('NMS', 'Sort by score, keep the best, remove same class boxes with IoU above the threshold, repeat. Slide example gives {A, D}. Crowds and fixed thresholds are weak spots. Soft-NMS decays by e<sup>−IoU² ÷ σ</sup>.')
K.must('One and two stage', 'One stage: SSD, YOLO, RetinaNet. Two stage: Faster R-CNN with a class agnostic RPN. The speed and accuracy divide is fuzzy today. Stage wise, joint and hybrid training.')
K.must('RetinaNet and FPN', 'ResNet + FPN + focal loss + prior bias. Early layers: high resolution, low meaning. FPN: 1 × 1 lateral + ×2 upsample + add, shared heads. 76,725 anchors at 640 × 640.')
K.must('RoIAlign', 'Bilinear f = Σ weights × corners, weights are opposite areas and add to 1. (2.3, 4.6) gives 26.8. RoIAlign samples bins without rounding, so the detector trains end to end.')

T = K.topic(
    slug='nms-architectures', topic='nms', step=(5, 'Finding objects', 'cv-detection', 'Object detection from the ground up: anchors, losses, duplicate removal, the main architectures and how detectors are scored.', 'College and masters'),
    title='IoU, NMS and detector architectures', short='IoU, NMS and architectures', badge='5.3', minutes=55,
    lead='Measure overlap with IoU, remove duplicate boxes with non-maximum suppression, and open up the two classic designs: RetinaNet with its feature pyramid, and Faster R-CNN with region proposals and RoIAlign.',
    desc='Intersection over union, NMS and Soft-NMS step by step, one stage versus two stage meta-architectures, multi-stage training, the CNN hierarchy and FPN, shared heads, Faster R-CNN, bilinear interpolation and RoIAlign.',
    summary='IoU, NMS and Soft-NMS, one stage and two stage detectors, RetinaNet with FPN, Faster R-CNN, bilinear interpolation and RoIAlign.',
    keywords=['IoU', 'NMS', 'soft-NMS', 'one stage', 'two stage', 'YOLO', 'SSD', 'RetinaNet', 'FPN', 'feature pyramid', 'Faster R-CNN', 'RPN', 'RoIAlign', 'bilinear interpolation', 'joint training'],
    recap='<p>IoU measures how well two boxes agree. NMS uses it to keep one box per object, with Soft-NMS as a gentler option for crowds. One stage detectors predict straight from a feature pyramid that gives every level deep meaning, and two stage detectors propose regions, crop them with differentiable bilinear sampling and refine them.</p>')
