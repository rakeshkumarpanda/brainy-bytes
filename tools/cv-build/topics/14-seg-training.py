# Chapter 14: training and evaluating segmentation. Ground truth masks and ignore labels, logits, pixel-wise
# cross-entropy, class imbalance, weighted CE, focal loss, Dice loss, pixel accuracy, Dice and IoU, mIoU,
# boundary metrics, augmentation, mask resizing, the training loop, validation and leakage, failure modes,
# debugging, model selection and perception versus action.
# Source: lectures 7 and 8, chapters 10 to 13 and 15.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('pixce', r'''
# Pixel-wise cross-entropy over a small mask, skipping ignored pixels
from math import log
p_true = [0.9, 0.5, 0.05, 0.99, 0.7, 0.3]     # probability given to the true class
labels = [3, 3, 3, 0, 2, 255]                  # 255 = ignore
ignore = int(input("ignore id: "))

total, count = 0.0, 0
for p, y in zip(p_true, labels):
    if y == ignore:
        print("label", y, "skipped")
        continue
    loss = -log(p)
    total += loss
    count += 1
    print("label", y, " p =", p, " loss =", round(loss, 3))
print("mean over", count, "valid pixels =", round(total / count, 3))
print("dividing by all", len(labels), "would give", round(total / len(labels), 3))
''', stdin='255\n')

K.code('weights', r'''
# Inverse frequency class weights w = N / (C * n_c)
names = ["road", "sky", "building", "car", "pedestrian"]
counts = [int(v) for v in input("pixel counts: ").split()]

N, C = sum(counts), len(counts)
for name, n in zip(names, counts):
    w = N / (C * n)
    print(name.ljust(10), "share %5.1f%%" % (100 * n / N), " weight", round(w, 2), " weighted pixels", round(n * w))
''', stdin='50000 25000 20000 4000 1000\n')

K.code('miou', r'''
# Per class IoU, mIoU and pixel accuracy from a confusion matrix (rows = truth)
M = [[900, 20, 5],
     [30, 140, 10],
     [15, 5, 30]]
names = input("class names: ").split()

n = len(M)
total = sum(sum(r) for r in M)
ious = []
for c in range(n):
    tp = M[c][c]
    fn = sum(M[c]) - tp
    fp = sum(M[r][c] for r in range(n)) - tp
    iou = tp / (tp + fp + fn)
    ious.append(iou)
    print(names[c].ljust(7), "TP", tp, "FP", fp, "FN", fn, " IoU", round(iou, 3))
print("mIoU =", round(sum(ious) / n, 3))
print("pixel accuracy =", round(sum(M[c][c] for c in range(n)) / total, 3))
''', stdin='road car person\n')

K.lesson('loss', 'Masks, logits and the pixel loss', f'''
<p>The lecturer split machine learning design into three parts: data (what goes in and what comes out), the model (the last two chapters), and training and evaluation (this one). The slide adds: good segmentation is not only architecture, it is also data, loss, metric and understanding failures.</p>
<h3>Ignore labels</h3>
<p>Every image needs a mask of the same size. Some pixels cannot be labelled reliably: outside the annotated area, unclear boundaries, ambiguous regions. They get a reserved ID such as 255 and are skipped in the loss. In PyTorch this is <code>nn.CrossEntropyLoss(ignore_index=255)</code>, with logits of shape B × C × H × W and targets B × H × W.</p>
<h3>Logits</h3>
<p>The lecturer: the value before the activation function is the logit, also called the score. Strictly, a logit is the log-odds ln(p ÷ (1 − p)) of logistic regression. Deep learning stretched the word to mean any raw score before SoftMax or sigmoid. Logits can be any real number. Loss functions take logits and apply SoftMax inside, which is numerically safer.</p>
{fx('Pixel-wise cross-entropy', '<i>L</i> = −' + frac('1', '|Ω|') + ' Σ<sub><i>i</i> ∈ Ω</sub> ln <i>p</i><sub><i>i</i>, <i>y</i><sub><i>i</i></sub></sub>', 'Ω is the set of valid pixels and p<sub>i, y<sub>i</sub></sub> the probability given to the true class at pixel i. The one hot target picks out that one probability.', key=True)}
{table(['Prediction for a car pixel', 'P(car)', 'Loss −ln P'], [
    ['Good', '0.90', '0.105'], ['Uncertain', '0.50', '0.693'], ['Bad', '0.05', '2.996']])}
{viz('pixloss')}
{steps('Average only the valid pixels', [
    'A 5 × 5 loss map adds to 7.5, so the plain mean is 7.5 ÷ 25 = 0.30.',
    'Now five pixels with loss 0.5 carry the ignore label. The valid 20 pixels add to 7.5 − 2.5 = 5.0.',
    'Correct loss: 5.0 ÷ 20 = 0.25. Dividing by all 25 gives 0.20, silently biased.'])}
{code('pixce')}
<p>Binary or categorical? A student answered correctly: binary cross-entropy for two classes with one sigmoid, categorical for many exclusive classes with SoftMax. For independent per class masks, use a sigmoid and binary CE on each channel.</p>
''', kw=['ground truth mask', 'ignore label', 'ignore_index', 'logit', 'log-odds', 'pixel-wise cross-entropy', 'valid pixels', 'binary cross-entropy', 'categorical cross-entropy'])

K.lesson('imbalance', 'Class imbalance: weighted CE, focal and Dice', f'''
{table(['Class', 'Pixels', 'Share'], [
    ['road', '50,000', '50%'], ['sky', '25,000', '25%'], ['building', '20,000', '20%'], ['car', '4,000', '4%'], ['pedestrian', '1,000', '1%']])}
<p>The lecturer: every pixel counts equally, so the model gets very good at road and very bad at pedestrians, which is why people still ask whether self driving cars are safe for pedestrians. High pixel accuracy can hide poor performance on rare but important classes.</p>
{fxs(
    fx('Weighted cross-entropy', '<i>L</i> = ' + frac('Σ<sub><i>i</i></sub> <i>w</i><sub><i>y</i><sub><i>i</i></sub></sub> (−ln <i>p</i><sub><i>i</i>, <i>y</i><sub><i>i</i></sub></sub>)', 'Σ<sub><i>i</i></sub> <i>w</i><sub><i>y</i><sub><i>i</i></sub></sub>'), 'Rare or important classes get larger weights.', key=True),
    fx('Inverse frequency weight', '<i>w</i><sub><i>c</i></sub> = ' + frac('<i>N</i>', '<i>C</i> · <i>n</i><sub><i>c</i></sub>'), 'N pixels, C classes, n<sub>c</sub> pixels of class c. Every class then contributes N ÷ C weighted pixels.'))}
{steps('Weights for the street image', [
    'N = 100,000 and C = 5. Road: 100,000 ÷ (5 × 50,000) = 0.4. Sky 0.8, building 1.0, car 5.0, pedestrian 20.0.',
    'Each class now contributes 20,000 weighted pixels, for example 1,000 × 20 for pedestrians. Perfectly balanced.',
    'The slide\'s hand picked weights: road 0.5, sky 0.7, car 2.0, pedestrian 5.0. Three pixels with CE 0.1 (road), 0.7 (car) and 2.3 (pedestrian) give 0.05 + 1.4 + 11.5 = 12.95 over a total weight of 7.5, a mean of 1.727 against the plain 1.033.'])}
{code('weights')}
{note('Very large weights can make training unstable or raise false positives. Weights can follow importance, not only frequency.', 'warn')}
<h3>Focal loss</h3>
{fx('Focal loss', 'FL = −(1 − <i>p</i><sub><i>t</i></sub>)<sup>γ</sup> ln <i>p</i><sub><i>t</i></sub>', 'The same function as in detection (chapter 5.2). It scales by difficulty rather than by class.')}
{steps('An easy and a hard pixel, γ = 2', [
    'Easy road pixel, P = 0.99: CE = 0.01005, focal = 0.0001 × 0.01005 ≈ 1.0 × 10<sup>−6</sup>.',
    'Hard car pixel on the road boundary, P = 0.45: CE = 0.7985, focal = 0.55² × 0.7985 = 0.2415.',
    'The hard pixel weighs 79 times the easy one under CE, and about 240,000 times under focal loss. Not every pixel should teach equally.'])}
<h3>Dice loss</h3>
{fx('Soft Dice loss', '<i>L</i><sub>Dice</sub> = 1 − ' + frac('2 Σ <i>p</i><sub><i>i</i></sub> <i>g</i><sub><i>i</i></sub> + ε', 'Σ <i>p</i><sub><i>i</i></sub> + Σ <i>g</i><sub><i>i</i></sub> + ε'), 'Uses probabilities, not 0 or 1, so it is differentiable. ε avoids 0 ÷ 0 when the class is absent.', key=True)}
{steps('Soft Dice on four pixels', [
    'p = [0.9, 0.8, 0.2, 0.1], g = [1, 1, 0, 0].',
    'Σpg = 1.7, Σp = 2.0, Σg = 2.',
    'Dice = 3.4 ÷ 4 = 0.85, so the loss is 0.15.'])}
<p>A student asked why not train only on Dice, since it measures overlap directly. The lecturer: you can, if you design the loss for it. Such losses exist (V-Net, 2016). In practice Dice is usually combined with CE, because CE gives a steady gradient at every pixel while Dice is one global ratio whose gradients get noisy when the object is tiny or absent. A common recipe is L = CE + λ Dice. The lecturer\'s general form: α A + β B + γ C, with the weights chosen by what matters for your problem.</p>
{table(['Situation', 'Loss'], [
    ['Standard many class problem', 'Cross-entropy'],
    ['Rare but important classes', 'Weighted CE'],
    ['Many easy pixels, few hard ones', 'Focal loss'],
    ['Tiny foreground, overlap is the goal', 'Dice, usually with CE'],
    ['Edges matter', 'Add a boundary loss']])}
''', kw=['class imbalance', 'weighted cross-entropy', 'inverse frequency', 'focal loss', 'gamma', 'hard pixels', 'Dice loss', 'soft Dice', 'combined loss', 'V-Net'])

K.lesson('metrics', 'Metrics: accuracy, Dice, IoU and mIoU', f'''
{steps('Accuracy 90%, tumour found: none', [
    'A 10,000 pixel scan with 9,000 background and 1,000 tumour pixels. The model says background everywhere.',
    'Pixel accuracy = 9,000 ÷ 10,000 = 90%.',
    'Tumour: TP = 0, so IoU = 0 and Dice = 0.',
    'Background IoU = 0.9, so the two class mIoU = (0.9 + 0) ÷ 2 = 0.45. The metric that forces every class to count exposes the failure.'])}
{fxs(
    fx('Dice', 'Dice = ' + frac('2|<i>P</i> ∩ <i>G</i>|', '|<i>P</i>| + |<i>G</i>|') + ' = ' + frac('2TP', '2TP + FP + FN'), 'P prediction, G ground truth. The F1 score of the pixels.', key=True),
    fx('IoU (Jaccard)', 'IoU = ' + frac('|<i>P</i> ∩ <i>G</i>|', '|<i>P</i> ∪ <i>G</i>|') + ' = ' + frac('TP', 'TP + FP + FN'), 'The same IoU as for boxes, applied to pixel sets.', key=True),
    fx('Relation', 'Dice = ' + frac('2 · IoU', '1 + IoU') + ', &nbsp; IoU = ' + frac('Dice', '2 − Dice'), 'Dice ≥ IoU always, equal only at 0 and 1.'))}
{viz('overlap')}
{steps('The tumour example from the slides', [
    '|G| = 100, |P| = 120, overlap 80. So TP = 80, FP = 40, FN = 20.',
    'Dice = 160 ÷ 220 = 0.727, about 72.7% overlap quality.',
    'Union = 100 + 120 − 80 = 140, so IoU = 80 ÷ 140 = 0.571.',
    'Check: 0.727 ÷ (2 − 0.727) = 0.571. Same prediction, two numbers. Never compare them as if they were one metric.'])}
<p>The lecturer\'s rule of thumb: Dice is preferred in medical work and IoU in road scenes and benchmarks such as PASCAL VOC and Cityscapes. Both measure overlap.</p>
<h3>mean IoU</h3>
<p>Compute IoU for each class, then average. The slide: road 0.91, sky 0.88, building 0.75, car 0.62, person 0.40 gives 3.56 ÷ 5 = 0.712. The person class drags it down, exactly the information pixel accuracy hides.</p>
{viz('confmat')}
{steps('A confusion matrix by hand', [
    'Rows are truth, columns are prediction. Road row 900, 20, 5. Car row 30, 140, 10. Person row 15, 5, 30. Total 1,155.',
    'For each class TP is the diagonal, FN the rest of its row, FP the rest of its column.',
    'Road: TP 900, FN 25, FP 45, IoU 0.928. Car: TP 140, FN 40, FP 25, IoU 0.683. Person: TP 30, FN 20, FP 15, IoU 0.462.',
    'mIoU = 0.691. Pixel accuracy = 1,070 ÷ 1,155 = 0.926, much higher. Frequency weighted IoU (about 0.87) also follows the big classes.'])}
{code('miou')}
{note('Benchmarks add one confusion matrix over the whole dataset, then compute IoU per class. Averaging per image IoUs is different and noisier, since an image without a class gives 0 ÷ 0. Say which one you report.', 'warn')}
<h3>Boundaries</h3>
<p>Two masks can have the same IoU while one has blurry edges and the other has sharp edges and a small area error. For surgical planning, lanes and thin structures, edges matter. Boundary F-score and Boundary IoU compare only pixels near the true contour. Hausdorff distance is the worst gap between the two outlines, and HD95 uses the 95th percentile to ignore stray outliers.</p>
{table(['Application', 'Prefer', 'Why'], [
    ['Small brain tumour', 'Dice or IoU, plus recall', 'Tiny foreground, a miss is costly'],
    ['Road and sidewalk edges', 'Boundary metric plus IoU', 'Edges matter'],
    ['Balanced many class benchmark', 'mIoU', 'Every class counts'],
    ['Surgical planning, lane markings', 'Boundary F-score, HD95', 'A few pixels of edge error matter']])}
''', kw=['pixel accuracy', 'accuracy trap', 'Dice', 'IoU', 'Jaccard', 'Dice IoU relation', 'mIoU', 'confusion matrix', 'frequency weighted IoU', 'mean class accuracy', 'boundary F-score', 'Hausdorff distance', 'HD95'])

K.lesson('pipeline', 'The training pipeline and data leakage', f'''
<h3>Augmentation</h3>
<p>Medical datasets are small, so augmentation shows the model more variety. Spatial transforms (flip, rotate, crop, scale) must hit the image and the mask identically. The lecturer: if I flip the image I flip the mask, so X and Y stay matched. Colour changes, noise and brightness go to the image only, since class IDs are not colours. Libraries such as albumentations take <code>aug(image=img, mask=mask)</code> and handle this.</p>
<h3>Resizing masks</h3>
<p>A strip of road (1) next to a car (3), resized with bilinear interpolation, gets the values 1.5 and 2.5. Rounded, they become 2, a sidewalk that is not there. Images may use bilinear or area resizing. Masks must use nearest neighbour. Predicted logits are continuous, so they may be resized bilinearly before argmax.</p>
<h3>The loop</h3>
<ol>
<li>Load an image and its mask.</li>
<li>Apply the same spatial augmentation to both.</li>
<li>Forward pass to B × C × H × W logits.</li>
<li>Loss over valid pixels, skipping the ignore label.</li>
<li>Back-propagate and update the weights.</li>
<li>After each epoch, run the validation set, argmax, add up a confusion matrix and report mIoU or Dice.</li>
</ol>
<h3>Validation without self deception</h3>
{table(['Split', 'Role'], [
    ['Train', 'Updates the weights'],
    ['Validation', 'Tunes settings and selects models'],
    ['Test', 'Used once for the final report']])}
<p>A student asked what avoiding self deception means. The lecturer: if you apply min-max normalisation using X<sub>min</sub> and X<sub>max</sub> of all the data, the model learns the test distribution through the scaling. It looks good on the test set but is not. That is <b>data leakage</b>.</p>
{viz('leak')}
{steps('The leak in numbers', [
    'Training values 10, 20, 30 and one test value 100, a genuinely different case.',
    'Right: fit on training only, min 10, max 30. The test value maps to (100 − 10) ÷ 20 = 4.5, outside 0 to 1, so the shift is visible.',
    'Wrong: fit on all, min 10, max 100. Training becomes 0, 0.111, 0.222 and the test point 1.0. The shift is hidden and the validation score is flattered.'])}
{note('Leakage in segmentation also comes from slices of one patient or frames of one video landing in both train and test. Split by patient, scene or video, never by random image. A model with high training IoU and low validation IoU is probably overfitting.', 'exam')}
''', kw=['augmentation', 'aligned transforms', 'albumentations', 'mask resizing', 'nearest neighbour', 'training loop', 'train validation test', 'data leakage', 'min-max normalisation', 'patient level split', 'overfitting'])

K.lesson('debug', 'Failure modes and debugging', f'''
<p>The slide: a good segmentation student learns to diagnose masks visually, not only report a number.</p>
{table(['Failure', 'Symptom', 'Likely cause', 'Possible fix'], [
    ['Boundary errors', 'Right class, wrong shape, mask leaks out', 'Downsampling, weak decoder, rough labels', 'Skips, high resolution features, boundary loss'],
    ['Small or thin objects', 'Lane marking, vessel or tiny pedestrian vanish', 'Aggressive downsampling', 'High resolution branches, multi-scale features, class weights, crops around rare objects'],
    ['Class confusion', 'Road and sidewalk, tumour and oedema, crop and weed, river and shadow', 'Similar texture, weak context', 'Context modules, multi-scale features, better labels'],
    ['Domain shift', 'Works on sunny days, fails on rainy nights, new scanner, new satellite sensor', 'Test data differs from training data', 'Augmentation, diverse data, domain adaptation, self supervised pre-training'],
    ['Occlusion', 'Partly hidden objects incomplete, two objects merge', 'No evidence for the hidden part', 'Instance or panoptic methods, more context'],
    ['Over-smoothing', 'Fine detail disappears', 'Too much pooling or blur, big upsampling jumps', 'Skips, sharper decoder, boundary loss']])}
{table(['Check before blaming the architecture', 'Bug it catches'], [
    ['Are image and mask aligned after augmentation?', 'Flip or crop applied to only one'],
    ['Are class IDs intact after resizing?', 'Bilinear on masks creates phantom classes'],
    ['Are ignored pixels handled in the loss?', 'Ignore counted as a class, wrong denominator'],
    ['Is the imbalance severe?', 'A rare class learns nothing'],
    ['Is validation representative?', 'Leakage or an easy validation set'],
    ['Which classes have low IoU?', 'A good mIoU hiding one dead class'],
    ['Are errors mostly boundary, small object or domain?', 'Points to the right fix'],
    ['Did you look at the masks?', 'Checkerboards, shifts, systematic artefacts']])}
<h3>Case questions from the slides</h3>
<ol>
<li><b>Small brain tumour, a miss is serious.</b> The class answered Dice. Measure Dice or IoU and recall on the tumour class. Train with CE plus Dice, or weighted CE or focal loss.</li>
<li><b>Road scene where the road and sidewalk boundary matters.</b> Boundary problem. Inspect boundary F-score or Boundary IoU, and fix with skips, a high resolution decoder or a boundary loss.</li>
<li><b>Crop and weed look alike under new lighting.</b> Both domain shift and class confusion. Use colour and lighting augmentation, more diverse data and domain adaptation.</li>
</ol>
<h3>Choosing a model from constraints</h3>
{table(['Scenario', 'What matters', 'Direction'], [
    ['Medical', 'Boundaries, Dice, expert review', 'U-Net or nnU-Net, CE + Dice, patient level validation'],
    ['Driving', 'Real time, small objects, weather', 'Efficient multi-scale model, weather augmentation, pedestrian IoU'],
    ['Satellite', 'Huge images, scale, sensor shift', 'Multi-scale context, tiling, cross sensor augmentation'],
    ['Phone or drone', 'Latency and memory', 'Small encoder, light decoder, lower resolution, quantisation']])}
<p>The last question in class: segmentation understands the scene, but how does that become the right action for a car? The recording ends before the answer. A driving system is a pipeline: perception (segmentation, detection, depth, tracking), prediction of where others will move, planning of a safe path, and control of steering and brakes. Segmentation supplies the map of drivable space. It does not decide.</p>
{ladder(
    '<p>To train a pixel labeller you need a mask for every image, a score that punishes wrong pixels, and fair ways to measure success. Counting correct pixels can fool you when one class is tiny, so we measure overlap for each class instead.</p>',
    '<p>Pixel CE averages −ln p over valid pixels, skipping the ignore label. Imbalance is handled with class weights N ÷ (C n<sub>c</sub>), focal loss or Dice. Report per class IoU and mIoU, or Dice, never accuracy alone. Dice = 2·IoU ÷ (1 + IoU). Resize masks with nearest neighbour and fit statistics on the training split only.</p>',
    '<p>Benchmarks pool one confusion matrix over the dataset. Boundary metrics and HD95 capture edge quality that region overlap misses. Lovász-softmax optimises IoU directly. Split by patient or scene to avoid leakage, and diagnose failures by type before changing the architecture.</p>',
    '<p>Calibration of pixel probabilities, uncertainty maps and conformal prediction for masks matter in medicine and driving. Domain generalisation and test time adaptation target the shift problem. Topology aware losses (for vessels and roads) preserve connectivity that IoU ignores.</p>')}
''', kw=['failure modes', 'boundary errors', 'small objects', 'class confusion', 'domain shift', 'occlusion', 'over-smoothing', 'debugging checklist', 'case questions', 'model selection', 'perception planning control'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What happens to pixels with the ignore label (for example 255)?', ['They count as background', 'They are skipped in the loss and the metrics', 'They get double weight', 'They are deleted from the image'], 1,
       'Uncertain pixels.', 'The model is not penalised there.')
K.quiz('e', 'Which metric can be high while a tiny tumour is completely missed?', ['Tumour Dice', 'Pixel accuracy', 'Tumour IoU', 'Tumour recall'], 1,
       'Background dominates.', '90% accuracy with tumour IoU and Dice both 0.')
K.quiz('e', 'How should a label mask be resized?', ['Bilinear', 'Nearest neighbour', 'Bicubic', 'Average pooling'], 1,
       'IDs are not intensities.', 'Blending would create classes that are not there.')
K.quiz('m', 'mIoU is better than pixel accuracy because', ['It is always higher', 'Every class gets an equal vote, so rare classes are not hidden', 'It ignores small classes', 'It needs no ground truth'], 1,
       'Mean over classes.', 'A weak person class drags it down where accuracy would not move.')
K.quiz('m', 'Weighted CE and focal loss differ because', ['They are the same', 'Weighted CE scales by class, focal loss scales by how hard each pixel is', 'Focal loss needs boxes', 'Weighted CE has no weights'], 1,
       'w<sub>y</sub> against (1 − p<sub>t</sub>)<sup>γ</sup>.', 'One fixes class imbalance, the other easy against hard imbalance.')
K.quiz('m', 'Dice = 0.727 and IoU = 0.571 for the same mask. Which is true?', ['One is wrong', 'Both are right, Dice = 2·IoU ÷ (1 + IoU) is always at least IoU', 'IoU is always higher', 'They should be equal'], 1,
       'Check 2 × 0.571 ÷ 1.571.', 'Never compare a Dice with an IoU as if they were one metric.')
K.quiz('m', 'You flip the image during augmentation. What must happen to the mask?', ['Nothing', 'The same flip', 'A colour change', 'It is regenerated'], 1,
       'X and Y must stay matched.', 'Spatial transforms go to both, colour transforms only to the image.')
K.quiz('h', 'Why is Dice loss usually combined with cross-entropy?', ['Dice cannot be computed', 'CE gives a steady gradient at every pixel, while Dice is one global ratio with noisy gradients for tiny or absent objects', 'CE is a metric', 'To make training slower'], 1,
       'Gradient behaviour.', 'L = CE + λ Dice is a common recipe in medical segmentation.')
K.quiz('h', 'High training IoU and much lower validation IoU suggests', ['Underfitting', 'Overfitting', 'Data is perfect', 'A wrong metric'], 1,
       'Compare the same metric on both splits.', 'The model memorised the training set.')
K.quiz('h', 'Which split avoids leakage for CT scans?', ['Random slices', 'By patient', 'By pixel', 'By class'], 1,
       'Neighbouring slices are near copies.', 'All slices of one patient must stay in one split.')
K.quiz('x', 'A model works in sunny daytime but fails on rainy nights. Which failure mode is it?', ['Class confusion', 'Domain shift', 'Over-smoothing', 'Ignore label bug'], 1,
       'Training and test distributions differ.', 'Fix with augmentation, diverse data, domain adaptation or test time adaptation.')
K.quiz('x', 'Why can frequency weighted IoU mislead like pixel accuracy?', ['It is undefined', 'It weights each class IoU by its pixel share, so big classes dominate again', 'It ignores the diagonal', 'It uses boxes'], 1,
       'Weights by class size.', 'In the lecture matrix it is about 0.87 against an mIoU of 0.691.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A car pixel gets P(car) = 0.90. What is its cross-entropy? Give three decimals.', '0.105', '−ln P.',
       ['The one hot target picks P(car).', '−ln 0.90.', eq('≈ 0.105')], check=0.10536, tol=0.0006)
K.calc('e', '9,000 background and 1,000 tumour pixels, all predicted background. What is the pixel accuracy?', '0.9', 'Correct ÷ total.',
       ['Correct pixels 9,000.', 'Total 10,000.', eq('accuracy = 0.9'), 'Tumour IoU and Dice are both 0.'], check=0.9)
K.calc('e', '|G| = 100, |P| = 120, overlap 80. What is Dice? Give three decimals.', '0.727', '2|P ∩ G| ÷ (|P| + |G|).',
       ['2 × 80 = 160.', '120 + 100 = 220.', eq('Dice = 160 ÷ 220 ≈ 0.727')], check=160 / 220, tol=0.0006)
K.calc('m', 'Same masks. What is IoU? Give three decimals.', '0.571', 'Union = |P| + |G| − overlap.',
       ['Union = 120 + 100 − 80 = 140.', 'Intersection 80.', eq('IoU = 80 ÷ 140 ≈ 0.571')], check=80 / 140, tol=0.0006)
K.calc('m', 'Pixel losses 0.2, 0.5, 1.2, 0.1, 0.9, 0.3, 0.4, 2.0, where pixels 3 and 8 are ignored. What is the correct mean loss?', '0.4', 'Drop the ignored pixels from both sum and count.',
       ['Valid: 0.2, 0.5, 0.1, 0.9, 0.3, 0.4.', 'Sum 2.4 over 6 pixels.', eq('2.4 ÷ 6 = 0.40'), 'Dividing by 8 would wrongly give 0.30.'], check=0.4)
K.calc('m', '100,000 pixels, 5 classes, 1,000 pedestrian pixels. What is the inverse frequency weight of pedestrian?', '20', 'N ÷ (C n<sub>c</sub>).',
       ['C × n = 5 × 1,000 = 5,000.', '100,000 ÷ 5,000.', eq('w = 20')], check=20)
K.calc('m', 'Class IoUs 0.91, 0.88, 0.75, 0.62 and 0.40. What is mIoU? Give three decimals.', '0.712', 'Mean over classes.',
       ['Sum 3.56.', 'Divide by 5.', eq('mIoU = 0.712')], check=0.712, tol=0.0006)
K.calc('h', 'IoU = 0.6. What is Dice?', '0.75', 'Dice = 2 IoU ÷ (1 + IoU).',
       ['2 × 0.6 = 1.2.', '1 + 0.6 = 1.6.', eq('Dice = 1.2 ÷ 1.6 = 0.75')], check=0.75)
K.calc('h', 'Dice = 0.9. What is IoU? Give three decimals.', '0.818', 'IoU = Dice ÷ (2 − Dice).',
       ['2 − 0.9 = 1.1.', '0.9 ÷ 1.1.', eq('IoU ≈ 0.818')], check=0.9 / 1.1, tol=0.0006)
K.calc('h', 'Soft Dice with p = [0.9, 0.8, 0.2, 0.1] and g = [1, 1, 0, 0]. What is the Dice loss? Give two decimals.', '0.15', '1 − 2Σpg ÷ (Σp + Σg).',
       ['Σpg = 1.7, Σp = 2.0, Σg = 2.', 'Dice = 3.4 ÷ 4 = 0.85.', eq('loss = 1 − 0.85 = 0.15')], check=0.15)
K.calc('x', 'A hard boundary pixel has p<sub>t</sub> = 0.45. What is its focal loss with γ = 2? Give three decimals.', '0.242', '(1 − p<sub>t</sub>)<sup>γ</sup> × (−ln p<sub>t</sub>).',
       ['−ln 0.45 ≈ 0.7985.', '(0.55)² = 0.3025.', eq('0.3025 × 0.7985 ≈ 0.242')], check=0.3025 * 0.798508, tol=0.0006)
K.calc('x', 'In the lecture confusion matrix, car has TP 140, FP 25 and FN 40. What is its IoU? Give three decimals.', '0.683', 'TP ÷ (TP + FP + FN).',
       ['TP + FP + FN = 205.', '140 ÷ 205.', eq('IoU ≈ 0.683')], check=140 / 205, tol=0.0006)

# ---------------------------------------------------------------- assignments
K.assign('maskedce', 'e', 'Cross-entropy with an ignore label',
         '<p>Write <code>masked_ce(p_true, labels, ignore=255)</code>. <code>p_true[i]</code> is the probability the model gives to the true class of pixel i and <code>labels[i]</code> its class ID. Return the mean of −ln p over pixels whose label is not <code>ignore</code>, rounded to 3 decimals. Return 0.0 if no pixel is valid.</p>',
         '''
from math import log

def masked_ce(p_true, labels, ignore=255):
    # your code here
    pass
''', [('masked_ce([0.9, 0.5, 0.05], [3, 3, 3])', 1.265), ('masked_ce([0.9, 0.5, 0.05], [3, 3, 255])', 0.399),
      ('masked_ce([0.5, 0.5], [255, 255])', 0.0), ('masked_ce([0.5], [0])', 0.693)],
         '''
from math import log

def masked_ce(p_true, labels, ignore=255):
    vals = [-log(p) for p, y in zip(p_true, labels) if y != ignore]
    return round(sum(vals) / len(vals), 3) if vals else 0.0
''', 'Collect −ln p only for valid pixels, then divide by how many there are.',
         '<p>With the bad pixel ignored, the mean falls from 1.265 to 0.399. Ignoring must remove the pixel from the count too.</p>')
K.assign('diceiou', 'e', 'Dice and IoU of two masks',
         '<p>Write <code>dice_iou(pred, gt)</code> for two flat lists of 0 and 1. Return <code>[dice, iou]</code>, each rounded to 3 decimals. If both masks are empty, return <code>[1.0, 1.0]</code>.</p>',
         '''
def dice_iou(pred, gt):
    # your code here
    pass
''', [('dice_iou([1, 1, 1, 0], [1, 1, 0, 0])', [0.8, 0.667]), ('dice_iou([0, 0, 0], [0, 1, 1])', [0.0, 0.0]),
      ('dice_iou([0, 0], [0, 0])', [1.0, 1.0]), ('dice_iou([1] * 120 + [0] * 20, [1] * 80 + [0] * 40 + [1] * 20)', [0.727, 0.571])],
         '''
def dice_iou(pred, gt):
    tp = sum(1 for p, g in zip(pred, gt) if p and g)
    fp = sum(1 for p, g in zip(pred, gt) if p and not g)
    fn = sum(1 for p, g in zip(pred, gt) if g and not p)
    if tp + fp + fn == 0:
        return [1.0, 1.0]
    return [round(2 * tp / (2 * tp + fp + fn), 3), round(tp / (tp + fp + fn), 3)]
''', 'Count TP, FP and FN, then use the count forms of both formulas.',
         '<p>The last test rebuilds the lecture tumour: 120 predicted, 100 true, 80 shared.</p>')
K.assign('miou', 'm', 'mIoU from a confusion matrix',
         '<p>Write <code>scores(M)</code> where <code>M[t][p]</code> counts pixels of true class t predicted as p. Return <code>[ious, miou, accuracy]</code>, with the list of per class IoU and the two numbers all rounded to 3 decimals (average the unrounded IoUs).</p>',
         '''
def scores(M):
    # your code here
    pass
''', [('scores([[900, 20, 5], [30, 140, 10], [15, 5, 30]])', [[0.928, 0.683, 0.462], 0.691, 0.926]),
      ('scores([[50, 5, 5], [10, 30, 0], [5, 0, 15]])', [[0.667, 0.667, 0.6], 0.644, 0.792]),
      ('scores([[9000, 0], [1000, 0]])', [[0.9, 0.0], 0.45, 0.9])],
         '''
def scores(M):
    n = len(M)
    total = sum(sum(r) for r in M)
    ious = []
    for c in range(n):
        tp = M[c][c]
        fn = sum(M[c]) - tp
        fp = sum(M[r][c] for r in range(n)) - tp
        ious.append(tp / (tp + fp + fn))
    acc = sum(M[c][c] for c in range(n)) / total
    return [[round(v, 3) for v in ious], round(sum(ious) / n, 3), round(acc, 3)]
''', 'FP is the column sum minus the diagonal, FN the row sum minus the diagonal.',
         '<p>The third test is the accuracy trap: 0.9 accuracy but an mIoU of 0.45.</p>')

K.must('Pixel loss', 'L = −(1 ÷ |Ω|) Σ ln p over valid pixels. Ignore label 255 leaves both the sum and the count. P(car) 0.9, 0.5, 0.05 gives 0.105, 0.693, 2.996.')
K.must('Imbalance', 'Weights w<sub>c</sub> = N ÷ (C n<sub>c</sub>): pedestrian 20 in the street image. Focal (1 − p<sub>t</sub>)<sup>γ</sup> scales by difficulty. Soft Dice 1 − 2Σpg ÷ (Σp + Σg), usually with CE.')
K.must('Metrics', 'Accuracy hides rare classes (90% with tumour IoU 0). Dice = 2TP ÷ (2TP + FP + FN), IoU = TP ÷ (TP + FP + FN), Dice = 2IoU ÷ (1 + IoU). mIoU from a dataset confusion matrix.')
K.must('Pipeline', 'Same spatial transform for image and mask, colour only for the image. Masks resize with nearest neighbour. Fit statistics on the training split. Split by patient, scene or video.')
K.must('Debugging', 'Six failures: boundary, small or thin, class confusion, domain shift, occlusion, over-smoothing. Check alignment, IDs, ignore handling, imbalance and per class IoU before blaming the architecture.')

T = K.topic(
    slug='segmentation-training', topic='seg-training', step=(6, 'Understanding every pixel', 'cv-segmentation', 'Semantic segmentation from the output tensor to modern architectures, losses, metrics and debugging.', 'College and masters'),
    title='Training and evaluating segmentation', short='Losses, metrics and debugging', badge='6.3', minutes=60,
    lead='Train a pixel labeller and judge it honestly: pixel cross-entropy with ignore labels, weighted and focal losses for imbalance, Dice and IoU, mIoU from a confusion matrix, augmentation and mask resizing, data leakage, and a checklist for diagnosing bad masks.',
    desc='Ground truth masks and ignore labels, logits, pixel-wise cross-entropy, class imbalance, weighted CE, focal loss, soft Dice loss, pixel accuracy, Dice and IoU, mIoU, boundary metrics, augmentation, mask resizing, validation and leakage, six failure modes and a debugging checklist.',
    summary='Pixel cross-entropy, weighted CE, focal and Dice losses, Dice, IoU and mIoU, the accuracy trap, augmentation, leakage and debugging.',
    keywords=['cross-entropy', 'ignore label', 'weighted cross-entropy', 'focal loss', 'Dice loss', 'Dice', 'IoU', 'mIoU', 'confusion matrix', 'pixel accuracy', 'augmentation', 'data leakage', 'failure modes'],
    recap='<p>Pixel cross-entropy averages over valid pixels only. Imbalance needs class weights, focal loss or Dice. Measure overlap per class with IoU or Dice and average with mIoU, because pixel accuracy hides rare classes. Keep image and mask aligned, resize masks with nearest neighbour, fit statistics on training data only, and diagnose failures by type.</p>')
