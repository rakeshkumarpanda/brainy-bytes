# Chapter 11: evaluating detectors. Datasets and the long tail, TP, FP and FN matching, precision and recall,
# the score threshold, the PR curve, AP, mAP and the COCO protocol, choosing a model, the Pareto frontier,
# speed levers, batch norm with small batches and transfer learning.
# Source: lectures 5 and 6, chapters 13 to 15.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('match', r'''
# Mark each detection TP or FP by greedy IoU matching, highest score first
# (detection, score, best overlapping ground truth, IoU with it)
dets = [("d1", 0.95, "GT1", 0.80), ("d2", 0.90, "GT2", 0.30),
        ("d3", 0.85, "GT3", 0.75), ("d4", 0.60, "GT1", 0.60)]
ground_truth = ["GT1", "GT2", "GT3"]
alpha = float(input("IoU threshold alpha: "))

matched = set()
tp = fp = 0
for name, score, gt, iou in sorted(dets, key=lambda d: -d[1]):
    if iou >= alpha and gt not in matched:
        matched.add(gt)
        tp += 1
        print(name, "TP, matched", gt)
    else:
        fp += 1
        reason = "duplicate of " + gt if gt in matched else "IoU too low"
        print(name, "FP,", reason)
fn = len(ground_truth) - len(matched)
print("TP", tp, "FP", fp, "FN", fn)
print("precision", round(tp / (tp + fp), 3), "recall", round(tp / (tp + fn), 3))
''', stdin='0.5\n')

K.code('ap', r'''
# Average precision from a ranked list of TP (1) and FP (0) marks
marks = [int(c) for c in input("marks, best first (e.g. 1101010100): ")]
n_gt = int(input("number of ground truth objects: "))

tp = fp = 0
points = []
for rank, m in enumerate(marks, start=1):
    tp += m
    fp += 1 - m
    points.append((tp / n_gt, tp / (tp + fp)))     # (recall, precision)
    print(rank, "TP" if m else "FP", "P = %.3f  R = %.3f" % (points[-1][1], points[-1][0]))

def envelope(r):                                     # best precision at recall >= r
    return max([p for rr, p in points if rr >= r - 1e-9], default=0.0)

ap, prev = 0.0, 0.0
for r, p in points:
    if r > prev + 1e-9:
        ap += (r - prev) * envelope(r)
        prev = r
eleven = sum(envelope(i / 10) for i in range(11)) / 11
print("AP (all points) =", round(ap, 3))
print("AP (11 points)  =", round(eleven, 3))
''', stdin='1101010100\n6\n')

K.code('repeat', r'''
# Repeat factor sampling for a long tailed dataset (LVIS)
from math import sqrt
freq = {"person": 0.50, "car": 0.10, "giraffe": 0.002, "tiara": 0.0001}   # fraction of images
t = float(input("threshold t: "))

r = {}
for c, f in freq.items():
    r[c] = max(1.0, sqrt(t / f))
    print(c.ljust(8), "f =", f, " r =", round(r[c], 2))

image = ["person", "tiara"]                          # classes in one image
print("this image is repeated", round(max(r[c] for c in image), 2), "times per epoch")
''', stdin='0.001\n')

K.lesson('datasets', 'Datasets and the long tail', f'''
<p>To score a detector you first need labelled images, then a metric that copes with boxes, duplicates and misses. This chapter builds both. The lecture started with the four datasets almost every paper uses.</p>
{table(['Dataset', 'Classes', 'Images (slide)', 'Notes'], [
    ['PASCAL VOC', '20', 'about 5K', 'The classic small benchmark. The 2007 train and validation split has 5,011 images.'],
    ['MS COCO', '80', 'about 120K', 'The standard. The lecturer: any good paper will use this.'],
    ['Open Images', '600', '1.7M', 'Very large, many boxes per image.'],
    ['LVIS', 'about 1,000 on the slide', '50K', 'Large vocabulary with an extreme long tail. The released version 1.0 has 1,203 categories.']])}
<p>The lecturer asked what happens to accuracy if the dataset shrinks. Expect a learning curve: mAP falls as data shrinks, and it falls fastest for rare classes. Starting from a pre-trained backbone, covered at the end of this chapter, softens the fall.</p>
<h3>The long tail</h3>
<p>Plot the number of boxes per class with classes sorted by frequency and you get a few classes with huge counts and many with very few. A student called it class imbalance. The lecturer gave the more exact name: a <b>long tailed</b> dataset, where the imbalance is across semantic categories.</p>
{table(['Imbalance', 'Where', 'Typical cure'], [
    ['Foreground against background', 'Inside every image, most anchors see background', 'Focal loss, hard example mining (chapter 5.2)'],
    ['Long tail', 'Across the dataset, some classes are rare', 'Repeat factor sampling, class balanced loss weights, decoupled training']])}
{fx('Repeat factor sampling (LVIS)', '<i>r</i>(<i>c</i>) = max(1, ' + sqrt('<i>t</i> ÷ <i>f</i>(<i>c</i>)') + '), &nbsp; <i>r</i>(image) = max over its classes <i>r</i>(<i>c</i>)', '<i>f</i>(<i>c</i>) is the fraction of training images that contain class <i>c</i> and <i>t</i> is a threshold, 0.001 in the LVIS paper. Images with rare classes are shown <i>r</i> times per epoch.', key=True)}
{steps('A rare class', [
    't = 0.001 and the class appears in f = 0.0001 of the images.',
    't ÷ f = 10, and the square root is about 3.16.',
    'Images that contain this class are repeated about 3 times per epoch. A class in 5% of images gives √0.02 &lt; 1, so the max keeps it at 1.'])}
{code('repeat')}
{note('Always look at the class histogram of a dataset before comparing mAP numbers. A model can look good on average while failing every rare class.', 'tip')}
''', kw=['dataset', 'PASCAL VOC', 'COCO', 'Open Images', 'LVIS', 'long tail', 'class imbalance', 'repeat factor sampling', 'learning curve', 'rare classes'])

K.lesson('matching', 'Matching detections: TP, FP and FN', f'''
<p>The lecturer showed why classification is easy to score: four images, three correct labels, accuracy 75%. Detection has two extra problems.</p>
<ol>
<li><b>Location errors.</b> The predicted dog box is near the true box but not on it. How close is close enough?</li>
<li><b>Over and under prediction.</b> Three boxes on one dog and none on a second dog. One accuracy number cannot capture too many and too few.</li>
</ol>
<h3>Close enough means IoU above α</h3>
<p>A detection counts as correct when its IoU with a true box exceeds a threshold α that we choose, exactly as we choose a probability threshold in classification. The lecturer showed overlaps of 0.5, 0.7 and 0.95 and asked which to accept. Her answer: it depends on you.</p>
{table(['Threshold', 'Meaning', 'Suits'], [
    ['α = 0.5', 'Roughly the right place. The PASCAL VOC rule.', 'Counting people in a crowd'],
    ['α = 0.75', 'A tight box', 'A robot grasping an object, measuring size'],
    ['0.5 to 0.95 averaged', 'Rewards tight boxes at every level. The COCO rule.', 'Comparing detectors fairly']])}
<p>For two equal squares shifted sideways by a fraction s of their width, IoU = (1 − s) ÷ (1 + s): 0.818 at 10%, 0.667 at 20%, 0.538 at 30% and 0.333 at 50%. A shift of a third of the width already fails at α = 0.5.</p>
<h3>The matching rules</h3>
{table(['Outcome', 'Rule'], [
    ['True positive (TP)', 'Right class, IoU above α with a true box that has not been matched yet'],
    ['False positive (FP)', 'IoU below α (poor box), lies on background, or a duplicate of an object already matched'],
    ['False negative (FN)', 'A true object that no detection matched. Also called a miss.'],
    ['True negative', 'Not used. The number of empty windows is effectively infinite.']])}
{steps('Three dogs, four detections, α = 0.5', [
    'Sort by score: d1 0.95, d2 0.90, d3 0.85, d4 0.60.',
    'd1 overlaps GT1 with IoU 0.80 and GT1 is free, so TP. GT1 is now matched.',
    'd2 best overlaps GT2, but IoU 0.30 is below 0.5, so FP. GT2 stays free.',
    'd3 overlaps GT3 with IoU 0.75, so TP.',
    'd4 overlaps GT1 with IoU 0.60, but GT1 is taken, so FP (a duplicate).',
    'GT2 was never matched, so FN = 1. Totals: TP 2, FP 2, FN 1.'])}
{code('match')}
{note('Remember the names this way. The first word says whether the model was right, the second says what it predicted. A false positive is a box the model drew that was wrong. The lecturer added that books draw the confusion matrix in different layouts, so learn the idea and not one picture.', 'exam')}
''', kw=['TP', 'FP', 'FN', 'true positive', 'false positive', 'false negative', 'matching', 'IoU threshold', 'alpha', 'duplicate', 'confusion matrix', 'location error'])

K.lesson('pr', 'Precision, recall and the score threshold', f'''
{fxs(
    fx('Precision', 'P = ' + frac('TP', 'TP + FP'), 'Of the boxes the model drew, how many were right. False alarms lower it.', key=True),
    fx('Recall', 'R = ' + frac('TP', 'TP + FN'), 'Of the real objects, how many were found. Misses lower it.', key=True),
    fx('F1 score', 'F<sub>1</sub> = ' + frac('2PR', 'P + R'), 'The harmonic mean. It is low if either one is low.'))}
<p>For the three dogs: P = 2 ÷ 4 = 0.50, R = 2 ÷ 3 = 0.667 and F1 = 2(0.5)(0.667) ÷ 1.167 = 0.571.</p>
<h3>Which one matters more</h3>
<p>Students said medical cases need precision and fraud detection needs recall. The lecturer agreed for fraud: calling an honest case suspicious is acceptable, missing a fraud is not. The medical case needs care. In screening, such as finding a tumour on a scan, a miss is the worst error, so recall comes first and a second test clears the false alarms. Precision comes first when the next action is costly or cannot be undone, such as surgery or blocking an account. Ask which mistake costs more.</p>
<h3>The score threshold</h3>
<p>The last step of a detector keeps only boxes whose score is at least a threshold. The lecturer: move it one way and precision falls while recall rises, move it the other way and the reverse happens.</p>
{viz('prsweep')}
{table(['Threshold', 'Kept', 'TP', 'FP', 'Precision', 'Recall'], [
    ['≥ 0', '6', '3', '3', '0.50', '1.00'],
    ['≥ 0.05', '5', '3', '2', '0.60', '1.00'],
    ['≥ 0.2', '4', '3', '1', '0.75', '1.00'],
    ['≥ 0.4', '3', '2', '1', '0.67', '0.67'],
    ['≥ 0.6', '2', '2', '0', '1.00', '0.67'],
    ['≥ 0.95', '1', '1', '0', '1.00', '0.33']])}
<p>Precision is not perfectly monotonic: 0.75 at 0.2, then 0.67 at 0.4. That zig-zag is the reason the next lesson smooths the curve. Instead of arguing about one threshold, look at all of them at once.</p>
''', kw=['precision', 'recall', 'F1', 'harmonic mean', 'score threshold', 'trade-off', 'screening', 'fraud detection', 'false alarm', 'miss'])

K.lesson('ap', 'The PR curve and average precision', f'''
<p>Sweep the score threshold, record (recall, precision) at each step and plot recall across and precision up. That is the <b>precision recall curve</b>. An ideal detector hugs the top right corner. <b>Average precision</b> (AP) is the area under the curve: a single number between 0 and 1, always stated for an IoU threshold, such as AP@0.5.</p>
{fxs(
    fx('Interpolated precision', '<i>p</i><sub>interp</sub>(<i>r</i>) = max<sub><i>r</i>′ ≥ <i>r</i></sub> <i>p</i>(<i>r</i>′)', 'The best precision at this recall or any higher recall. It turns the zig-zag into a staircase that only goes down.', key=True),
    fx('AP, all points', 'AP = Σ<sub><i>k</i></sub> (<i>r</i><sub><i>k</i></sub> − <i>r</i><sub><i>k</i>−1</sub>) · <i>p</i><sub>interp</sub>(<i>r</i><sub><i>k</i></sub>)', 'Add a rectangle each time recall increases.', key=True),
    fx('AP, 11 points', 'AP<sub>11</sub> = ' + frac('1', '11') + ' Σ<sub><i>r</i> ∈ {0, 0.1, …, 1}</sub> <i>p</i><sub>interp</sub>(<i>r</i>)', 'PASCAL VOC 2007. COCO uses 101 points, 0 to 1 in steps of 0.01.'))}
{viz('apcurve')}
{steps('AP for one class, 6 true objects, 10 detections', [
    'Rank by score and mark TP or FP: T T F T F T F T F F. Five of the six objects are found, so recall stops at 5 ÷ 6 = 0.833.',
    'Running precision and recall: 1.000 and 0.167, 1.000 and 0.333, 0.667 and 0.333, 0.750 and 0.500, 0.600 and 0.500, 0.667 and 0.667, 0.571 and 0.667, 0.625 and 0.833, 0.556 and 0.833, 0.500 and 0.833.',
    'Envelope: 1.000 up to recall 0.333, 0.750 up to 0.5, 0.667 up to 0.667, 0.625 up to 0.833, then 0.',
    'Area: 0.333 × 1.000 + 0.167 × 0.750 + 0.167 × 0.667 + 0.167 × 0.625 = 0.3333 + 0.1250 + 0.1111 + 0.1042 = 0.674.',
    '11 points: (4 × 1.0 + 2 × 0.75 + 0.667 + 2 × 0.625 + 0 + 0) ÷ 11 = 0.674 as well.'])}
{code('ap')}
{deep('Why use the envelope', '<p>A false positive at rank 3 lowers precision for a moment. A user who wants more recall would pick whichever threshold gives the best precision at that recall or higher, so the dip is never a real operating point. Taking the envelope removes the dip and makes AP less sensitive to the exact order of detections with nearly equal scores.</p>')}
''', kw=['PR curve', 'precision recall curve', 'average precision', 'AP', 'interpolated precision', 'envelope', '11 point', '101 point', 'area under curve', 'ranking'])

K.lesson('map', 'mAP and the COCO protocol', f'''
<p>AP is for one class. The headline number averages it.</p>
<ol>
<li>Compute AP separately for every class: airplane, apple, backpack, banana and so on.</li>
<li><b>mAP</b> is the mean of those APs at one IoU threshold, for example mAP@0.5 or mAP@0.75.</li>
<li><b>COCO</b> also averages over ten IoU thresholds, 0.50, 0.55 up to 0.95. That is the number papers call AP or mAP@[0.5:0.95]. It rewards accurate boxes, not just finding the object.</li>
</ol>
{fxs(
    fx('mAP', 'mAP = ' + frac('1', '<i>C</i>') + ' Σ<sub><i>c</i></sub> AP<sub><i>c</i></sub>', 'The mean over the C classes.', key=True),
    fx('COCO AP', 'AP<sub>COCO</sub> = ' + frac('1', '10') + ' Σ<sub><i>t</i> ∈ {0.50, 0.55, …, 0.95}</sub> mAP<sub><i>t</i></sub>', 'Mean over classes and over IoU thresholds.', key=True))}
{steps('mAP by hand', [
    'Class APs at IoU 0.5: dog 0.72, cat 0.65, car 0.80.',
    'mAP@0.5 = (0.72 + 0.65 + 0.80) ÷ 3 = 2.17 ÷ 3 = 0.723.',
    'One class across the ten thresholds: 0.80, 0.78, 0.75, 0.71, 0.66, 0.60, 0.52, 0.42, 0.27, 0.08 (illustrative values).',
    'Their mean is 5.59 ÷ 10 = 0.559, well below the 0.80 at IoU 0.5, because tight boxes are demanded.'])}
{viz('cocoap')}
<p>COCO also reports AP<sub>S</sub>, AP<sub>M</sub> and AP<sub>L</sub> for small objects (area below 32² pixels), medium ones and large ones (above 96² pixels), and average recall. AP<sub>S</sub> is almost always the lowest, which is why feature pyramids matter.</p>
{table(['Detector on COCO (slide 92)', 'mAP'], [
    ['SSD with MobileNet, low resolution', '21'],
    ['SSD with Inception V2, low resolution', '24'],
    ['R-FCN with ResNet-101, 300 proposals', '30'],
    ['Faster R-CNN with ResNet-101, 100 proposals', '32'],
    ['Faster R-CNN with Inception-ResNet-V2, 300 proposals', '37']])}
{note('Check which metric a paper reports. COCO AP numbers of 30 to 50 look small next to PASCAL VOC AP@0.5 numbers of 70 to 90, but they measure a much stricter thing.', 'warn')}
''', kw=['mAP', 'mean average precision', 'COCO', 'AP@0.5', 'AP@0.75', 'AP 0.5:0.95', 'IoU thresholds', 'APS', 'APM', 'APL', 'small objects', 'average recall'])

K.lesson('practice', 'Choosing, speeding up and training a detector', f'''
<h3>How to pick a model</h3>
<p>Three choices: the meta-architecture (SSD, Faster R-CNN, R-FCN and others), the feature extractor (VGG, ResNet, Inception, MobileNet) and the image size (300 × 300 up to 800 × 1296). Then the deployment limits: the sensor, the device (laptop, data centre, phone, Raspberry Pi, TPU), the latency and the memory. The lecturer was firm that no model is guaranteed best for a domain. Try several architectures and several resolutions, measure, and choose.</p>
<h3>The Pareto frontier</h3>
<p>Slides from Huang and colleagues (CVPR 2017) plot mAP against GPU time for many detectors. Past a certain accuracy each extra point costs much more time. The best detectors lie on the <b>Pareto optimal</b> curve. A student offered the Pareto principle, the 80/20 rule. Same Vilfredo Pareto, different idea. A model is Pareto optimal when no other model is at least as good on both accuracy and speed and strictly better on one.</p>
{viz('pareto')}
{steps('Seven detectors (mAP, latency in ms)', [
    'A (21, 30), B (24, 45), C (30, 90), D (32, 80), E (34, 150), F (37, 200), G (28, 120).',
    'C: D is more accurate and faster, so C is dominated. G: D beats it too.',
    'A, B, D, E and F: none is beaten on both counts, so they form the frontier.',
    'Choose along it by budget: A or B for real time on a phone, F for offline accuracy.'])}
<h3>Simple speed levers</h3>
<ul>
<li><b>Lower resolution</b>, for example 300 instead of 600: much faster, but small objects shrink and are missed.</li>
<li><b>Fewer proposals</b> in a two stage detector, for example 100 instead of 300: much faster with a small loss of recall. Big backbones gain more from many proposals than small ones.</li>
</ul>
<h3>High resolution and batch norm</h3>
{table(['Data', 'Resolution', 'Pixels', 'Compared with 224 × 224'], [
    ['MNIST', '28 × 28', '784', '0.02×'],
    ['ImageNet', '224 × 224', '50,176', '1×'],
    ['COCO', '640 × 640', '409,600', '8.2×'],
    ['COCO', '800 × 1333', '1,066,400', '21.3×']])}
<p>Bigger images need more memory each, so the batch shrinks, from 32 to 2 for example. Batch normalisation estimates a mean and variance from the batch, and the standard error of a batch mean grows like 1 ÷ √N. Going from 32 to 2 images makes the estimate √16 = 4 times noisier. The cures: freeze batch norm and reuse the pre-trained statistics, use GroupNorm which normalises within each image, or use synchronised batch norm across many GPUs.</p>
{fx('Noise of a batch statistic', 'SE(<i>μ̂</i><sub>B</sub>) = ' + frac('σ', sqrt('<i>N</i>')), 'σ is the spread of the activation and N the batch size.')}
<h3>Transfer learning</h3>
<p>Start from a network pre-trained to classify a larger dataset, then fine tune it for detection. The slide (Sun and colleagues, 2017): COCO AP rises from 34.3 with ImageNet pre-training to 36.7 with JFT-300M, a set of 300 million images, and to 37.4 with both. Larger pre-training data helps, and it also softens the small data drop from the first lesson.</p>
{ladder(
    '<p>To check a detector we count how many of its boxes were right and how many real objects it found. One number, average precision, sums up both. Picking a detector means balancing how accurate it is against how fast it runs.</p>',
    '<p>A detection is a TP when its IoU with an unmatched true box is above α. Precision is TP ÷ (TP + FP), recall is TP ÷ (TP + FN). Sweeping the score threshold gives the PR curve, AP is its area, and mAP averages AP over classes. Models on the Pareto frontier are the only sensible choices.</p>',
    '<p>AP uses the interpolated envelope, all points or 11 or 101 sampled recalls. COCO averages over IoU 0.50 to 0.95 and reports AP by object size. Long tailed data needs repeat factor sampling r = max(1, √(t ÷ f)). Small batches make batch norm noisy as 1 ÷ √N, so detectors freeze BN or use GroupNorm or Sync-BN.</p>',
    '<p>LVIS introduced federated annotation and rare, common and frequent splits. Newer metrics address AP blind spots, for example LRP error and the boundary aware measures for masks. Speed comparisons are only fair on the same hardware, batch size and precision, and many papers now report latency with export to TensorRT or similar runtimes.</p>')}
''', kw=['model selection', 'Pareto frontier', 'Pareto optimal', 'speed accuracy trade-off', 'latency', 'resolution', 'proposals', 'batch normalisation', 'GroupNorm', 'Sync-BN', 'transfer learning', 'JFT-300M', 'pre-training'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which dataset has 80 classes and is the usual benchmark for detection papers?', ['PASCAL VOC', 'MS COCO', 'MNIST', 'Open Images'], 1,
       'The lecturer said any good paper uses it.', 'COCO has 80 classes and about 120K images.')
K.quiz('e', 'Precision is', ['TP ÷ (TP + FN)', 'TP ÷ (TP + FP)', 'TN ÷ (TN + FP)', 'FP ÷ TP'], 1,
       'Of the boxes drawn.', 'How many of the predicted boxes were correct.')
K.quiz('e', 'A real object that no detection matched is a', ['True positive', 'False positive', 'False negative', 'True negative'], 2,
       'The model said nothing and was wrong.', 'A miss is a false negative.')
K.quiz('m', 'Two detections overlap the same true dog above α. The lower scoring one is', ['A TP', 'An FP, as a duplicate', 'Ignored', 'An FN'], 1,
       'Each true box can be matched once.', 'Only the first match counts. Later ones are false positives.')
K.quiz('m', 'Why are true negatives not used in detection metrics?', ['They are always zero', 'The number of empty windows is effectively unlimited', 'They are the same as FN', 'COCO forbids them'], 1,
       'Count every empty position and scale.', 'Background windows have no natural count, so only TP, FP and FN are used.')
K.quiz('m', 'Raising the score threshold usually', ['Raises recall and lowers precision', 'Raises precision and lowers recall', 'Raises both', 'Changes neither'], 1,
       'Fewer boxes are kept.', 'Fewer boxes means fewer false alarms but more misses.')
K.quiz('m', 'For cancer screening on scans, which should come first?', ['Precision', 'Recall', 'Neither', 'Speed'], 1,
       'Which mistake is worse?', 'A missed tumour is the worst error. A second test can clear false alarms.')
K.quiz('h', 'Why does AP use the interpolated envelope rather than the raw precision?', ['To make AP bigger on purpose', 'Dips are never a sensible operating point, since a higher recall threshold offers better precision', 'Raw precision cannot be computed', 'COCO requires integers'], 1,
       'Would anyone choose the dip?', 'The envelope takes the best precision at that recall or more, which removes the zig-zag.')
K.quiz('h', 'COCO AP is lower than AP@0.5 for the same detector because', ['COCO has more classes', 'It averages over IoU thresholds up to 0.95, which demand tight boxes', 'It ignores small objects', 'It uses 11 points'], 1,
       'Ten thresholds.', 'Strict thresholds score loose boxes as false positives.')
K.quiz('h', 'Model C (mAP 30, 90 ms) and model D (mAP 32, 80 ms). Which is true?', ['C dominates D', 'D dominates C', 'Neither dominates', 'They are equal'], 1,
       'At least as good on both, better on one.', 'D is more accurate and faster, so C is never the right pick.')
K.quiz('x', 'Repeat factor sampling with t = 0.001. A class appears in 5% of images. Its repeat factor is', ['0.14', '1', '3.16', '20'], 1,
       'r = max(1, √(t ÷ f)).', '√(0.001 ÷ 0.05) = √0.02 ≈ 0.14, and the max lifts it to 1. Common classes are not down-sampled.')
K.quiz('x', 'Training on 800 × 1333 images forces a batch of 2 instead of 32. Which fix keeps normalisation stable without more GPUs?', ['Raise the learning rate', 'Use GroupNorm or freeze the pre-trained batch norm statistics', 'Remove the backbone', 'Use 11 point AP'], 1,
       'Batch statistics get noisy as 1 ÷ √N.', 'GroupNorm normalises within each image, and frozen BN uses fixed statistics, so neither depends on the batch.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A detector gives TP = 2 and FP = 2. What is its precision?', '0.5', 'TP ÷ (TP + FP).',
       ['TP + FP = 4.', 'Precision = 2 ÷ 4.', eq('P = 0.5')], check=0.5)
K.calc('e', 'TP = 2 and FN = 1. What is the recall? Give three decimals.', '0.667', 'TP ÷ (TP + FN).',
       ['TP + FN = 3 real objects.', 'Recall = 2 ÷ 3.', eq('R ≈ 0.667')], check=2 / 3, tol=0.0006)
K.calc('e', 'With P = 0.5 and R = 2/3, what is F1? Give three decimals.', '0.571', 'F1 = 2PR ÷ (P + R).',
       ['2PR = 2 × 0.5 × 0.667 = 0.667.', 'P + R = 1.167.', eq('F1 = 0.667 ÷ 1.167 ≈ 0.571')], check=0.5714, tol=0.0006)
K.calc('m', 'Slide 84 detections: Dog 0.99 (TP), Cat 0.90 (TP), Human 0.50 (FP), Cup 0.30 (TP), Laundry 0.10 (FP), Tortilla 0.02 (FP). At threshold 0.2, what is the precision?', '0.75', 'Keep the scores of at least 0.2.',
       ['Kept: Dog, Cat, Human and Cup.', 'TP = 3, FP = 1.', eq('P = 3 ÷ 4 = 0.75'), 'Recall is 3 ÷ 3 = 1.'], check=0.75)
K.calc('m', 'Repeat factor sampling with t = 0.001 and a class in f = 0.0001 of the images. What is r? Give two decimals.', '3.16', 'r = max(1, √(t ÷ f)).',
       ['t ÷ f = 0.001 ÷ 0.0001 = 10.', '√10 ≈ 3.162, which is above 1.', eq('r ≈ 3.16')], check=10 ** 0.5, tol=0.006)
K.calc('m', 'Two equal squares are shifted sideways by 30% of their width. What is their IoU? Give three decimals.', '0.538', 'IoU = (1 − s) ÷ (1 + s).',
       ['Overlap: 1 − 0.3 = 0.7 of a square.', 'Union: 1 + 0.3 = 1.3 squares.', eq('IoU = 0.7 ÷ 1.3 ≈ 0.538'), 'A miss at α = 0.5 is close.'], check=0.7 / 1.3, tol=0.0006)
K.calc('m', 'Class APs at IoU 0.5 are dog 0.72, cat 0.65 and car 0.80. What is mAP@0.5? Give three decimals.', '0.723', 'Mean over classes.',
       ['Sum = 2.17.', 'Divide by 3 classes.', eq('mAP@0.5 = 0.723')], check=2.17 / 3, tol=0.0006)
K.calc('h', 'Ranked marks T T F T F T F T F F with 6 true objects. What is the all point AP? Give three decimals.', '0.674', 'Envelope 1, 1, 0.75, 0.667, 0.625 at recalls 1/6 to 5/6.',
       ['Recall grows by 1/6 at ranks 1, 2, 4, 6 and 8.', 'Envelope at those recalls: 1.000, 1.000, 0.750, 0.667, 0.625.', 'Sum = 4.042.', eq('AP = 4.042 ÷ 6 ≈ 0.674')], check=(1 + 1 + 0.75 + 2 / 3 + 0.625) / 6, tol=0.0006)
K.calc('h', 'In the same list, what is the raw precision after rank 7? Give three decimals.', '0.571', 'Count TP and FP in the first seven.',
       ['First seven: T T F T F T F.', 'TP = 4, FP = 3.', eq('P = 4 ÷ 7 ≈ 0.571')], check=4 / 7, tol=0.0006)
K.calc('h', 'AP at the ten COCO thresholds is 0.80, 0.78, 0.75, 0.71, 0.66, 0.60, 0.52, 0.42, 0.27 and 0.08. What is the COCO AP? Give three decimals.', '0.559', 'Mean of the ten.',
       ['Sum = 5.59.', 'Divide by 10.', eq('AP<sub>COCO</sub> = 0.559'), 'Compare 0.80 at IoU 0.5.'], check=0.559, tol=0.0006)
K.calc('x', 'The batch drops from 32 images to 2. By what factor does the standard error of the batch mean grow?', '4', 'SE ∝ 1 ÷ √N.',
       ['Ratio = √32 ÷ √2.', '= √16.', eq('= 4')], check=4)
K.calc('x', 'How many times more pixels does an 800 × 1333 COCO image have than a 224 × 224 ImageNet crop? Give one decimal.', '21.3', 'Divide the pixel counts.',
       ['800 × 1333 = 1,066,400.', '224 × 224 = 50,176.', eq('1,066,400 ÷ 50,176 ≈ 21.3')], check=1066400 / 50176, tol=0.06)

# ---------------------------------------------------------------- assignments
K.assign('prf', 'e', 'Precision, recall and F1',
         '<p>Write <code>prf(tp, fp, fn)</code> that returns <code>[precision, recall, f1]</code>, each rounded to 3 decimals. If there are no detections, precision is 0.0. If there are no real objects, recall is 0.0. If both are 0, F1 is 0.0.</p>',
         '''
def prf(tp, fp, fn):
    # your code here
    pass
''', [('prf(2, 2, 1)', [0.5, 0.667, 0.571]), ('prf(2, 0, 1)', [1.0, 0.667, 0.8]), ('prf(3, 3, 0)', [0.5, 1.0, 0.667]), ('prf(0, 0, 3)', [0.0, 0.0, 0.0])],
         '''
def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return [round(p, 3), round(r, 3), round(f1, 3)]
''', 'Guard each division with a check that the denominator is not zero.',
         '<p>The second test is threshold 0.6 on slide 84 (Cat and Dog kept). The third is threshold 0, where every box is kept.</p>')
K.assign('ap', 'm', 'Average precision',
         '<p>Write <code>average_precision(marks, n_gt)</code>. <code>marks</code> is a list of 1 (TP) and 0 (FP) in score order, best first. Use the all point method with the interpolated envelope and return AP rounded to 3 decimals.</p>',
         '''
def average_precision(marks, n_gt):
    # your code here
    pass
''', [('average_precision([1, 1, 0, 1, 0, 1, 0, 1, 0, 0], 6)', 0.674), ('average_precision([1, 1, 1, 1, 1, 0, 0, 0, 0, 0], 6)', 0.833),
      ('average_precision([0, 0, 0, 0, 0, 1, 1, 1, 1, 1], 6)', 0.417), ('average_precision([0, 0], 3)', 0.0)],
         '''
def average_precision(marks, n_gt):
    tp = fp = 0
    pts = []
    for m in marks:
        tp += m
        fp += 1 - m
        pts.append((tp / n_gt, tp / (tp + fp)))
    ap, prev = 0.0, 0.0
    for r, p in pts:
        if r > prev + 1e-9:
            ap += (r - prev) * max(q for rr, q in pts if rr >= r - 1e-9)
            prev = r
    return round(ap, 3)
''', 'Build the list of (recall, precision) first. Then add a rectangle each time recall grows, with height equal to the best precision at that recall or later.',
         '<p>The same five TPs give AP 0.833 when ranked first and 0.417 when ranked last. AP rewards putting correct boxes at the top of the list.</p>')
K.assign('pareto', 'm', 'The Pareto frontier',
         '<p>Write <code>pareto(models)</code> where each model is <code>(name, mAP, latency)</code>. Return the names of the models that no other model dominates, sorted by latency and then by name. Model Y dominates X when Y has mAP ≥ X and latency ≤ X, with at least one strictly better.</p>',
         '''
def pareto(models):
    # your code here
    pass
''', [("pareto([('A', 21, 30), ('B', 24, 45), ('C', 30, 90), ('D', 32, 80), ('E', 34, 150), ('F', 37, 200), ('G', 28, 120)])", ['A', 'B', 'D', 'E', 'F']),
      ("pareto([('A', 21, 30), ('B', 24, 45), ('C', 30, 90), ('D', 32, 80), ('E', 34, 150), ('F', 37, 200), ('G', 28, 120), ('H', 38, 120)])", ['A', 'B', 'D', 'H']),
      ("pareto([('X', 30, 50), ('Y', 30, 50)])", ['X', 'Y'])],
         '''
def pareto(models):
    def beats(y, x):
        return y[1] >= x[1] and y[2] <= x[2] and (y[1] > x[1] or y[2] < x[2])
    front = [x for x in models if not any(beats(y, x) for y in models)]
    return [x[0] for x in sorted(front, key=lambda m: (m[2], m[0]))]
''', 'For each model, check whether any other model beats it on both counts.',
         '<p>The third test shows that two identical models do not dominate each other, because neither is strictly better.</p>')

K.must('Matching', 'Sort by score. TP if IoU above α with an unmatched true box, otherwise FP (poor box, background or duplicate). Unmatched true boxes are FN. No true negatives. Three dogs example: TP 2, FP 2, FN 1.')
K.must('Precision and recall', 'P = TP ÷ (TP + FP), R = TP ÷ (TP + FN), F1 = 2PR ÷ (P + R). Example 0.5, 0.667, 0.571. A higher score threshold usually raises P and lowers R.')
K.must('AP', 'Envelope p<sub>interp</sub>(r) = max precision at recall ≥ r. All point AP adds rectangles where recall grows. Lecture list gives 0.674, and the 11 point version also 0.674. COCO uses 101 points.')
K.must('mAP and COCO', 'mAP = mean AP over classes. COCO AP also averages IoU 0.50 to 0.95, so 0.80 at IoU 0.5 became 0.559. AP<sub>S</sub> below 32², AP<sub>L</sub> above 96².')
K.must('Practice', 'Dominated models are never the right pick. Lower resolution and fewer proposals speed things up. Batch 32 to 2 makes BN 4 times noisier, so use frozen BN, GroupNorm or Sync-BN. Pre-training helps: 34.3 to 36.7 to 37.4. Long tail: r = max(1, √(t ÷ f)).')

T = K.topic(
    slug='detection-evaluation', topic='evaluation', step=(5, 'Finding objects', 'cv-detection', 'Object detection from the ground up: anchors, losses, duplicate removal, the main architectures and how detectors are scored.', 'College and masters'),
    title='Evaluating and choosing detectors', short='Evaluation and mAP', badge='5.4', minutes=55,
    lead='Score a detector properly: match boxes to objects, count true and false positives, trace the precision recall curve, compute AP and COCO mAP by hand, then choose and train a model with the speed and accuracy trade-off in mind.',
    desc='Datasets and the long tail, repeat factor sampling, TP, FP and FN matching, precision, recall and F1, the score threshold, the PR curve, average precision, mAP, the COCO protocol, the Pareto frontier, speed levers, batch norm with small batches and transfer learning.',
    summary='Datasets and the long tail, TP and FP matching, precision and recall, AP, mAP and COCO AP, the Pareto frontier, batch norm with small batches and transfer learning.',
    keywords=['evaluation', 'precision', 'recall', 'F1', 'average precision', 'mAP', 'COCO', 'PR curve', 'long tail', 'repeat factor sampling', 'Pareto frontier', 'batch norm', 'GroupNorm', 'transfer learning'],
    recap='<p>A detection is right when its IoU with an unmatched true box clears α. Counting TP, FP and FN gives precision and recall, sweeping the threshold gives the PR curve, and its interpolated area is AP. mAP averages over classes, and COCO also averages over strict IoU thresholds. To choose a model, stay on the Pareto frontier of accuracy and speed.</p>')
