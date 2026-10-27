# Chapter 16: the project lab. Rebuilds the mini project notebook step by step: YOLO11n on COCO128, a 9 x 9 Gaussian
# blur, the 3 x 3 sharpening kernel, and the analysis of precision, recall, mAP50 and mAP50-95 across the three stages.
# Source: the student's notebook (Effect of Blur and Sharpening on Object Detection) and its printed results.
# Facts checked: OpenCV getGaussianKernel uses sigma = 0.3((ksize - 1) * 0.5 - 1) + 0.8 when sigma <= 0 and fixed
# binomial weights for odd sizes up to 7, filter2D computes correlation and saturates to uint8 when ddepth = -1,
# Ultralytics val uses conf 0.001 and reports mean P and R at the confidence that maximises mean F1, COCO128 is the
# first 128 images of COCO train2017, YOLO11n (fused) has 2,616,248 parameters and 6.5 GFLOPs (from the notebook log).
import html as _h
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()


def listing(src):
    return '<pre class="cc-src">' + ''.join(f'<span class="ln">{_h.escape(l)}</span>' for l in src.strip('\n').split('\n')) + '</pre>'


K.code('gausskernel', r'''
# The Gaussian weights OpenCV uses when you pass sigma = 0
from math import exp
k = int(input("odd kernel size: "))

if k == 3:
    w = [0.25, 0.5, 0.25]                          # fixed table for small sizes
    print("OpenCV uses a fixed binomial table for this size")
elif k == 5:
    w = [0.0625, 0.25, 0.375, 0.25, 0.0625]
    print("OpenCV uses a fixed binomial table for this size")
else:
    sigma = 0.3 * ((k - 1) * 0.5 - 1) + 0.8
    raw = [exp(-((i - (k - 1) / 2) ** 2) / (2 * sigma * sigma)) for i in range(k)]
    w = [v / sum(raw) for v in raw]
    print("sigma =", round(sigma, 3))
print("weights:", [round(v, 4) for v in w])
print("sum of weights:", round(sum(w), 6))
print("multiplications per pixel: direct", k * k, " separable", 2 * k)
''', stdin='9\n')

K.code('row', r'''
# One row through the project kernel. When an image does not change from top to bottom,
# the 3 x 3 kernel [[0,-1,0],[-1,5,-1],[0,-1,0]] acts on a row as [-1, 3, -1].
row = [int(v) for v in input("pixel values in a row: ").split()]
n = len(row)
out = []
for i, v in enumerate(row):
    left = row[i - 1] if i > 0 else row[1]        # reflect at the borders, as OpenCV does
    right = row[i + 1] if i < n - 1 else row[n - 2]
    raw = 3 * v - left - right
    out.append(max(0, min(255, raw)))             # uint8 output is clipped to 0..255
    print(i, "value", v, " 3 x", v, "-", left, "-", right, "=", raw, "->", out[-1])
print("sharpened row:", out)
''', stdin='60 60 60 100 140 140 140\n')

K.code('compare', r'''
# Compare three stages of an experiment: change, share won back and F1
names = ["Precision", "Recall", "mAP50", "mAP50-95"]
base = [float(v) for v in input("baseline P R mAP50 mAP50-95: ").split()]
bad = [float(v) for v in input("degraded: ").split()]
fix = [float(v) for v in input("restored: ").split()]

for n, b, d, r in zip(names, base, bad, fix):
    loss = b - d
    share = (r - d) / loss * 100 if loss != 0 else 0.0
    print(n.ljust(10), "drop", round(loss, 4), " gain back", round(r - d, 4), " share", round(share, 1), "%")
for label, s in (("baseline", base), ("degraded", bad), ("restored", fix)):
    print("F1", label.ljust(8), round(2 * s[0] * s[1] / (s[0] + s[1]), 4))
''', stdin='0.6633 0.5894 0.6706 0.5026\n0.6802 0.5358 0.6176 0.4434\n0.6583 0.5468 0.6277 0.4556\n')

K.lesson('brief', 'The project brief', f'''
<p>This chapter rebuilds your mini project from start to finish and explains every number in it. The question was simple: <b>if the pictures get blurry, how much worse does a detector become, and does sharpening fix it?</b></p>
{table(['Item', 'Choice in the notebook'], [
    ['Dataset', 'COCO128: 128 images, 929 labelled objects, 80 classes, 2 images with no objects'],
    ['Model', 'Pretrained YOLO11n (fused): 100 layers, 2,616,248 parameters, 6.5 GFLOPs'],
    ['Training', 'None. The same frozen detector is evaluated three times'],
    ['Evaluation', 'model.val at image size 640 and batch 16, reporting precision, recall, mAP50 and mAP50-95'],
    ['Stage 2', 'cv2.GaussianBlur(image, (9, 9), 0) on every image'],
    ['Stage 3', 'cv2.filter2D(blurred, −1, K) with K = [[0, −1, 0], [−1, 5, −1], [0, −1, 0]]']])}
<p>The design is a <b>controlled experiment</b>. Only one thing changes between stages, the pixels. The model, the labels, the image size and the metric code stay fixed, so any change in the scores must come from the image processing.</p>
{steps('The four stages', [
    'Baseline. Write a dataset YAML pointing at the original images and run model.val.',
    'Blur. Read every image, blur it, save it under the same file name, copy the labels unchanged, evaluate again.',
    'Sharpen. Read every blurred image, sharpen it, save, copy labels, evaluate again.',
    'Analyse. Put the twelve numbers in one table and explain the changes.'])}
<h3>The helper functions in the notebook, slightly shortened</h3>
{listing("""
def build_processed_dataset(source_root, target_root, process_image):
    target_images_dir = target_root / IMAGE_SUBDIR
    target_images_dir.mkdir(parents=True, exist_ok=True)
    for image_path in sorted((source_root / IMAGE_SUBDIR).glob("*.jpg")):
        image = cv2.imread(str(image_path))
        cv2.imwrite(str(target_images_dir / image_path.name), process_image(image))
    shutil.copytree(source_root / LABEL_SUBDIR, target_root / LABEL_SUBDIR, dirs_exist_ok=True)

def evaluate_detector(dataset_yaml, stage_name):
    r = model.val(data=str(dataset_yaml), imgsz=640, batch=16, name=stage_name, exist_ok=True)
    return {"Precision": r.box.mp, "Recall": r.box.mr, "mAP@0.5": r.box.map50, "mAP@0.5:0.95": r.box.map}
""")}
<p>One function builds a processed copy of the dataset from any image operation, so Stage 2 and Stage 3 differ only in the function passed in. The labels are copied, not recomputed, because blur and sharpening do not move objects. YOLO labels store each box as class, centre x, centre y, width and height, all as fractions of the image size, and the image size does not change.</p>
{note('The labels are copied unchanged on purpose. If you resized or cropped the images, the boxes would have to change too. Blur and sharpening keep every pixel in place.', 'tip')}
<h3>What the four numbers mean</h3>
{table(['Metric', 'Question it answers'], [
    ['Precision', 'Of the boxes the detector reported, what share were right?'],
    ['Recall', 'Of the real objects, what share were found?'],
    ['mAP50', 'Area under the precision and recall curve per class, averaged over classes, with a match needing IoU at least 0.5'],
    ['mAP50-95', 'The same, averaged over ten IoU thresholds 0.50, 0.55 and so on up to 0.95, so loose boxes score lower']])}
<p>Chapter 5.4 derives these in full. The point to keep here: mAP50-95 rewards tight boxes, so anything that blurs object edges should hurt it the most.</p>
''', kw=['project', 'COCO128', 'YOLO11n', 'model.val', 'controlled experiment', 'dataset YAML', 'labels', 'precision', 'recall', 'mAP50', 'mAP50-95'])

K.lesson('blur', 'Stage 2: the Gaussian blur', f'''
<p><code>cv2.GaussianBlur(image, (9, 9), 0)</code> replaces every pixel by a weighted average of the 9 × 9 square around it. Pixels near the centre count most, following the bell shaped Gaussian curve. Passing 0 for σ lets OpenCV choose σ from the kernel size.</p>
{fxs(
    fx('Gaussian weight', '<i>G</i>(<i>x</i>, <i>y</i>) ∝ e<sup>−(<i>x</i>² + <i>y</i>²) ÷ (2σ²)</sup>', 'Normalised so the 81 weights add to 1. A flat area keeps its brightness.', key=True),
    fx('σ chosen by OpenCV', 'σ = 0.3 ((<i>k</i> − 1) ÷ 2 − 1) + 0.8', 'k = 9 gives σ = 0.3 × 3 + 0.8 = 1.7. For odd sizes up to 7 OpenCV uses fixed binomial weights instead.', key=True))}
{steps('The 9 weights along one axis', [
    'σ = 1.7, positions −4 to 4.',
    'Unnormalised weights e<sup>−x² ÷ 5.78</sup>: 0.063, 0.211, 0.500, 0.841, 1, 0.841, 0.500, 0.211, 0.063.',
    'Divide by their sum 4.23: 0.0148, 0.0498, 0.1183, 0.1988, 0.2364, 0.1988, 0.1183, 0.0498, 0.0148.',
    'The 2D kernel is this row times this column, because the Gaussian is separable.'])}
{code('gausskernel')}
<p><b>Separable</b> means the 2D blur can be done as a horizontal pass followed by a vertical pass. That costs 9 + 9 = 18 multiplications per pixel instead of 81, and OpenCV does it this way.</p>
{viz('labpipe')}
<h3>What blur does to a detector</h3>
<p>Blur is a <b>low pass filter</b>. It keeps slow changes such as large shapes and colour regions and removes fast changes such as edges, thin lines and fine texture. A detector's early layers are edge and texture finders, so blur weakens the evidence they pass on. Small, thin and distant objects suffer most, because nearly all of their evidence is fine detail. A bus filling half the frame survives a 9 × 9 blur. A tennis racket 20 pixels wide does not.</p>
{note('Your analysis found exactly this. In 000000000531.jpg detections fell from 10 to 4 and the tennis racket and distant players disappeared. In 000000000260.jpg detections fell from 8 to 3. Blur also caused class confusion: in 000000000049.jpg a horse was labelled as a dog with score 0.30.', 'exam')}
''', kw=['GaussianBlur', 'kernel size', 'sigma', 'OpenCV sigma formula', 'binomial', 'separable filter', 'low pass filter', 'small objects', 'class confusion'])

K.lesson('sharpen', 'Stage 3: the sharpening kernel', f'''
<p>The notebook applies <code>cv2.filter2D(blurred, −1, K)</code> with</p>
{fx('The project kernel', '<i>K</i> = ' + mat([['0', '−1', '0'], ['−1', '5', '−1'], ['0', '−1', '0']]) + ' = ' + mat([['0', '0', '0'], ['0', '1', '0'], ['0', '0', '0']]) + ' − ' + mat([['0', '1', '0'], ['1', '−4', '1'], ['0', '1', '0']]), 'The identity minus the 4 neighbour Laplacian. The weights add to 5 − 4 = 1, so flat areas are unchanged.', key=True)}
<p>Written out for one pixel B(x, y) of the blurred image:</p>
{fx('Sharpened pixel', '<i>S</i>(<i>x</i>, <i>y</i>) = 5<i>B</i>(<i>x</i>, <i>y</i>) − <i>B</i>(<i>x</i> + 1, <i>y</i>) − <i>B</i>(<i>x</i> − 1, <i>y</i>) − <i>B</i>(<i>x</i>, <i>y</i> + 1) − <i>B</i>(<i>x</i>, <i>y</i> − 1)', 'Then rounded and clipped to 0 to 255, because ddepth = −1 keeps the 8 bit image type.')}
<h3>Three ways to read the same kernel</h3>
<ul>
<li><b>Image minus Laplacian.</b> The Laplacian measures how much a pixel differs from its neighbours, which is large at edges. Subtracting it pushes edges further apart in brightness.</li>
<li><b>Unsharp masking.</b> S = B + 4 (B − average of the 4 neighbours). The average is a tiny blur, B minus that blur is the detail, and the kernel adds 4 times the detail back. The general form S = B + a (B − blur) gives this kernel at a = 4.</li>
<li><b>A high frequency boost.</b> Along one axis the gain is 3 − 2 cos ω: 1 for flat areas (ω = 0), 3 at half the finest frequency, 5 at the finest.</li>
</ul>
{steps('Sharpening by hand', [
    'Flat patch, every pixel 100: 5 × 100 − 4 × 100 = 100. Unchanged.',
    'A linear ramp 60, 100, 140 along a row: 3 × 100 − 60 − 140 = 100. Unchanged, the kernel only reacts to curvature.',
    'The dark side of an edge, centre 50 with neighbours 50, 50, 50, 200: 250 − 350 = −100, clipped to 0. That is the dark halo.',
    'The bright side, centre 200 with neighbours 200, 200, 200, 50: 1,000 − 650 = 350, clipped to 255. That is the bright halo.'])}
{code('row')}
{viz('freqgain')}
<h3>Why sharpening cannot undo the blur</h3>
<p>A linear filter multiplies each frequency by its gain. The 9 × 9 blur keeps only about 3 percent of the wave at half the finest frequency and about 0.5 percent of the finest. The kernel multiplies those by 3 and 5, giving about 9 and 3 percent. The detail is not hidden somewhere waiting to be revealed. Most of it is gone, and 8 bit rounding after the blur removed even more. Meanwhile any noise or JPEG artefact at those frequencies is boosted just as strongly as real detail.</p>
{note('filter2D computes correlation, not convolution, so the kernel is not flipped. For symmetric kernels such as this one the two are identical. The border default reflects the image without repeating the edge pixel (BORDER_REFLECT_101).', 'warn')}
{deep('Could anything restore more?', '<p>If the blur kernel is known, <b>deconvolution</b> divides by the blur gain in the frequency domain. Plain division explodes where the gain is near zero, so the Wiener filter divides by gain² plus a noise to signal ratio, boosting only where the signal is still above the noise. Learned deblurring networks go further by filling in plausible detail from training data, with the same caution as super-resolution in chapter 7.1: plausible is not the same as true. The most reliable fix for a detector is usually to train it on blurred images, so it learns features that survive blur.</p>')}
''', kw=['sharpening kernel', 'filter2D', 'Laplacian', 'unsharp masking', 'high pass', 'halo', 'clipping', 'uint8', 'correlation', 'BORDER_REFLECT_101', 'deconvolution', 'Wiener filter', 'frequency response'])

K.lesson('results', 'Reading the results', f'''
{table(['Stage', 'Precision', 'Recall', 'mAP50', 'mAP50-95'], [
    ['Original', '0.6633', '0.5894', '0.6706', '0.5026'],
    ['Gaussian blur', '0.6802', '0.5358', '0.6176', '0.4434'],
    ['Sharpened', '0.6583', '0.5468', '0.6277', '0.4556']])}
{viz('stagebars')}
<h3>Blur: what fell and by how much</h3>
{table(['Metric', 'Change', 'Relative change'], [
    ['Precision', '+0.0169', '+2.5 percent'],
    ['Recall', '−0.0536', '−9.1 percent'],
    ['mAP50', '−0.0530', '−7.9 percent'],
    ['mAP50-95', '−0.0592', '−11.8 percent']])}
<p>mAP50-95 lost the most, as predicted. Blurred edges make the box borders uncertain, and the strict IoU thresholds of 0.75 to 0.95 punish slightly wrong boxes that mAP50 would still accept.</p>
<h3>The precision puzzle</h3>
<p>Precision went up under blur. That looks like the detector got better, but it reported fewer boxes, and the ones it kept were the confident, easy ones. Blur also removes fine texture, which is a common trigger for false alarms. Fewer false alarms in the denominator can lift precision even while real objects are missed.</p>
{viz('opshift')}
{fx('Share of the loss won back', frac('restored − degraded', 'baseline − degraded'), 'For mAP50-95: (0.4556 − 0.4434) ÷ (0.5026 − 0.4434) = 0.0122 ÷ 0.0592 ≈ 20.6 percent.', key=True)}
{steps('Sharpening, metric by metric', [
    'Recall: 0.0110 ÷ 0.0536 ≈ 20.5 percent of the loss won back.',
    'mAP50: 0.0101 ÷ 0.0530 ≈ 19.1 percent.',
    'mAP50-95: 0.0122 ÷ 0.0592 ≈ 20.6 percent.',
    'Precision fell from 0.6802 to 0.6583, below even the baseline 0.6633. Amplified noise and JPEG artefacts produced extra boxes, such as a duplicate person box on one woman in 000000000260.jpg.'])}
{code('compare')}
{fx('F1 at the reported point', 'F1 = ' + frac('2 <i>P</i> <i>R</i>', '<i>P</i> + <i>R</i>'), 'Original 0.6242, blur 0.5994, sharpened 0.5974. By this single number sharpening is slightly worse than blur, while by mAP it is better. Different metrics can disagree on a small effect.')}
{note('A careful conclusion uses several metrics and says which one decides. mAP summarises every threshold, so it is the main score for detectors. P and R describe one operating point.', 'exam')}
''', kw=['results table', 'relative change', 'precision rises', 'false alarms', 'share won back', 'F1', 'mAP50-95 drop', 'localisation', 'operating point'])

K.lesson('validity', 'How sure can we be, and what to try next', f'''
<p>A good analysis also says what the experiment cannot show. Five points matter here.</p>
<ol>
<li><b>The baseline saw these images in training.</b> COCO128 is the first 128 images of COCO train2017, and the pretrained YOLO11n was trained on COCO train2017. The baseline scores are therefore optimistic. A fair test would use images from val2017.</li>
<li><b>128 images is a small sample.</b> A difference of 0.01 in mAP may be within the variation you would see from a different set of 128 images. Bootstrapping, re-scoring many random resamples of the images, gives a confidence interval.</li>
<li><b>P and R come from one confidence.</b> Ultralytics reports mean precision and recall at the confidence where the mean F1 over classes is highest. That point moves between stages, so P and R compare different operating points. mAP does not have this problem.</li>
<li><b>One blur level, one sharpening setting.</b> A 9 × 9 blur is strong. The conclusion might differ for a 3 × 3 blur or for motion blur. The sharpening strength was not tuned.</li>
<li><b>Validation settings.</b> model.val uses a very low confidence threshold (0.001) so it can trace the full precision and recall curve. Example pictures from model.predict used 0.25, so they show fewer boxes than were scored.</li>
</ol>
{scene('A city traffic camera', '<p>A council runs a vehicle and pedestrian detector on roadside cameras. On foggy mornings and with dirty lenses the images blur, and the count of pedestrians drops. Someone proposes adding a sharpening step. Following this project: measure mAP on a set of foggy frames with and without the step, check that false alarms from sensor noise do not rise, compare against simply fine tuning the detector on blurred frames, and apply the step only when a blur detector (for example a low variance of the Laplacian) says the frame is soft.</p>')}
<h3>Experiments that would strengthen the conclusion</h3>
{table(['Experiment', 'What it would show'], [
    ['Blur sweep: kernel 3, 5, 9, 15', 'How fast accuracy falls with blur, and where sharpening stops helping'],
    ['Unsharp mask with tuned amount and radius', 'Whether a gentler or wider boost helps more than the fixed kernel'],
    ['Wiener deconvolution with the known Gaussian', 'The best a linear method can do'],
    ['Results by object size', 'Whether small objects carry the loss, as the examples suggest'],
    ['Fine tune with blur augmentation', 'Whether training is a better fix than preprocessing'],
    ['Evaluate on val2017', 'Scores free from training overlap']])}
<p>Your conclusion, to sharpen only images known to be blurred, matches the evidence: a cheap step with consistent small gains in recall and mAP on blurred input, at some cost in precision, and not something to apply to sharp images where it only adds noise.</p>
{ladder(
    '<p>We made photos blurry on purpose and asked a computer to find things in them. It found fewer things, especially small ones. Sharpening the blurry photos helped a little, but could not bring back details that were already smudged away.</p>',
    '<p>A 9 × 9 Gaussian blur (σ = 1.7) cut recall from 0.589 to 0.536 and mAP50-95 from 0.503 to 0.443. The kernel [[0, −1, 0], [−1, 5, −1], [0, −1, 0]] won back about a fifth of each loss and lowered precision by amplifying noise.</p>',
    '<p>Blur is a low pass filter whose gain at high frequencies is near zero, and the sharpening gain 3 − 2 cos ω cannot restore what is gone. mAP50-95 falls most because strict IoU thresholds expose uncertain box edges. P and R are reported at the max F1 confidence, so they compare shifting operating points.</p>',
    '<p>Robustness to image corruptions is studied with benchmarks such as COCO-C and ImageNet-C, which apply blur, noise and weather at several strengths. The usual findings match this project: preprocessing gives small gains, while training with corruption augmentation or learned restoration jointly optimised with the detector gives larger ones. Evaluations should report confidence intervals and avoid train and test overlap.</p>')}
''', kw=['validity', 'train test overlap', 'COCO128', 'val2017', 'sample size', 'bootstrap', 'confidence interval', 'operating point', 'blur sweep', 'augmentation', 'variance of Laplacian', 'robustness', 'ImageNet-C'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Between the stages of the project, what changes?', ['The model weights', 'Only the image pixels', 'The labels', 'The image size'], 1,
       'A controlled experiment.', 'Same model, labels and settings, so any score change comes from the image processing.')
K.quiz('e', 'Why can the labels be copied unchanged to the blurred dataset?', ['Labels do not matter', 'Blur does not move objects or change the image size', 'YOLO ignores labels', 'They are recomputed by YOLO'], 1,
       'Boxes are fractions of the image size.', 'Nothing moves, so every box stays valid.')
K.quiz('e', 'Which metric went up after blurring?', ['Recall', 'mAP50', 'Precision', 'mAP50-95'], 2,
       'Fewer boxes reported.', '0.6633 to 0.6802, because fewer weak boxes and false alarms were reported.')
K.quiz('m', 'In cv2.GaussianBlur(image, (9, 9), 0), the 0 means', ['No blur', 'σ is computed from the kernel size', 'Border type', 'Zero padding'], 1,
       'σ = 0.3 ((k − 1) ÷ 2 − 1) + 0.8.', 'For k = 9, σ = 1.7.')
K.quiz('m', 'The kernel [[0, −1, 0], [−1, 5, −1], [0, −1, 0]] equals', ['A box blur', 'The identity minus the 4 neighbour Laplacian', 'A Sobel filter', 'A Gaussian'], 1,
       '5 = 1 + 4.', 'Image minus Laplacian, also unsharp masking with a = 4.')
K.quiz('m', 'Why do the sharpening weights add to 1?', ['To speed it up', 'So flat areas keep their brightness', 'To blur', 'To clip values'], 1,
       'Apply it to a constant patch.', '5c − 4c = c.')
K.quiz('m', 'Which metric fell the most under blur?', ['Precision', 'Recall', 'mAP50', 'mAP50-95'], 3,
       'Strict IoU thresholds.', '−0.0592, because blurred edges make boxes less tight.')
K.quiz('h', 'Why could sharpening not bring the scores back to baseline?', ['The kernel was too small', 'Blur reduced high frequencies almost to zero, and boosting a tiny signal leaves it tiny while also boosting noise', 'YOLO cannot read sharpened images', 'Labels were wrong'], 1,
       'Gains multiply.', 'At half the finest frequency, 3 percent times 3 is about 9 percent.')
K.quiz('h', 'Why did precision drop after sharpening?', ['Fewer boxes', 'The kernel amplified noise and JPEG artefacts, creating extra false boxes', 'The labels changed', 'mAP fell'], 1,
       'High pass boost.', 'An example was a duplicate person box in 000000000260.jpg.')
K.quiz('h', 'Why are the baseline scores optimistic?', ['The model is small', 'COCO128 comes from COCO train2017, which the pretrained model was trained on', 'The image size is 640', 'Batch 16'], 1,
       'Train and test overlap.', 'Use val2017 images for a fair score.')
K.quiz('x', 'Ultralytics reports mean P and R at', ['A confidence of 0.25', 'The confidence that maximises mean F1 across classes', 'A confidence of 0.5', 'Every confidence averaged'], 1,
       'One operating point.', 'That point can move between stages, which is one reason P and R can disagree with mAP.')
K.quiz('x', 'Which experiment best tests whether sharpening should be used on blurred images?', ['Run the same 128 images again', 'Sweep several blur levels on held out images and report confidence intervals', 'Use a bigger model only', 'Change the labels'], 1,
       'Vary the cause, avoid overlap, measure uncertainty.', 'One blur level on training images cannot support a general rule.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What σ does OpenCV choose for a 9 × 9 Gaussian blur with σ = 0?', '1.7', 'σ = 0.3 ((k − 1) ÷ 2 − 1) + 0.8.',
       ['(9 − 1) ÷ 2 = 4.', '4 − 1 = 3, and 0.3 × 3 = 0.9.', eq('σ = 0.9 + 0.8 = 1.7')], check=1.7)
K.calc('e', 'What do the weights of the project sharpening kernel add up to?', '1', 'Centre minus the four neighbours.',
       ['Centre 5.', 'Four neighbours of −1 add to −4.', eq('5 − 4 = 1')], check=1)
K.calc('e', 'A flat patch where every pixel is 100 is sharpened with the project kernel. What is the output?', '100', '5c − 4c.',
       ['5 × 100 = 500.', 'Four neighbours of 100 give 400.', eq('500 − 400 = 100')], check=100)
K.calc('e', 'How many multiplications per pixel does a separable 9 × 9 blur need?', '18', 'One horizontal pass and one vertical pass.',
       ['Direct: 9 × 9 = 81.', 'Separable: 9 across, then 9 down.', eq('9 + 9 = 18')], check=18)
K.calc('m', 'What σ does the formula give for a 15 × 15 kernel?', '2.6', 'Same formula.',
       ['(15 − 1) ÷ 2 = 7.', '0.3 × (7 − 1) = 1.8.', eq('σ = 1.8 + 0.8 = 2.6')], check=2.6)
K.calc('m', 'A dark pixel of 50 sits beside an edge: neighbours 50, 50, 50 and 200. What is the 8 bit output of the project kernel?', '0', 'Compute, then clip to 0 to 255.',
       ['5 × 50 = 250.', 'Neighbours add to 350, so 250 − 350 = −100.', eq('clip(−100) = 0')], check=0)
K.calc('m', 'By what percentage did recall fall under blur, relative to the baseline? Give one decimal.', '9.1', 'Drop divided by baseline.',
       ['0.5894 − 0.5358 = 0.0536.', '0.0536 ÷ 0.5894 ≈ 0.0909.', eq('about 9.1 percent')], check=9.1, tol=0.05)
K.calc('m', 'What share of the mAP50-95 loss did sharpening win back? Give a percentage with one decimal.', '20.6', '(restored − degraded) ÷ (baseline − degraded).',
       ['Gain back: 0.4556 − 0.4434 = 0.0122.', 'Loss: 0.5026 − 0.4434 = 0.0592.', eq('0.0122 ÷ 0.0592 ≈ 20.6 percent')], check=20.6, tol=0.05)
K.calc('m', 'What is the baseline F1 from P = 0.6633 and R = 0.5894? Give four decimals.', '0.6242', '2PR ÷ (P + R).',
       ['2 × 0.6633 × 0.5894 = 0.7819.', 'P + R = 1.2527.', eq('F1 = 0.7819 ÷ 1.2527 ≈ 0.6242')], check=2 * 0.6633 * 0.5894 / (0.6633 + 0.5894), tol=0.00006)
K.calc('h', 'A row 60, 100, 140 passes through the project kernel (the image does not change vertically). What is the middle output?', '100', 'On such an image the kernel acts as [−1, 3, −1].',
       ['The vertical neighbours equal the centre, so 5 − 2 = 3 remains for the centre.', '3 × 100 − 60 − 140.', eq('= 100, a straight ramp is unchanged')], check=100)
K.calc('h', 'Using e<sup>−σ²ω² ÷ 2</sup>, what fraction of the wave at ω = π ÷ 2 survives a blur with σ = 1.7? Give three decimals.', '0.028', 'σ² = 2.89 and (π ÷ 2)² ≈ 2.467.',
       ['σ²ω² = 2.89 × 2.467 ≈ 7.13.', 'Half of it is 3.565.', eq('e<sup>−3.565</sup> ≈ 0.028')], check=0.0283, tol=0.0006)
K.calc('h', 'What is the gain of the project kernel along one axis at the finest frequency ω = π?', '5', 'Gain 3 − 2 cos ω.',
       ['cos π = −1.', '3 − 2 × (−1).', eq('= 5')], check=5)
K.calc('x', 'At ω = π ÷ 2, blur keeps 0.028 of a wave and the kernel multiplies by 3 − 2 cos ω. What fraction remains after both? Give three decimals.', '0.085', 'Gains multiply.',
       ['cos(π ÷ 2) = 0, so the kernel gain is 3.', '0.0283 × 3.', eq('≈ 0.085, less than a tenth of the original')], check=0.0849, tol=0.0006)
K.calc('x', 'COCO128 has 929 labelled objects on 126 images that contain objects. About how many objects per labelled image? Give two decimals.', '7.37', 'Divide.',
       ['128 images minus 2 backgrounds = 126.', '929 ÷ 126.', eq('≈ 7.37 objects per image')], check=929 / 126, tol=0.005)

# ---------------------------------------------------------------- assignments
K.assign('sigma', 'e', 'The OpenCV σ rule',
         '<p>Write <code>opencv_sigma(k)</code> for an odd kernel size k. Return the σ OpenCV computes when you pass σ = 0, using σ = 0.3 ((k − 1) ÷ 2 − 1) + 0.8, rounded to 3 decimals.</p>',
         '''
def opencv_sigma(k):
    # your code here
    pass
''', [('opencv_sigma(9)', 1.7), ('opencv_sigma(3)', 0.8), ('opencv_sigma(15)', 2.6), ('opencv_sigma(5)', 1.1)],
         '''
def opencv_sigma(k):
    return round(0.3 * ((k - 1) * 0.5 - 1) + 0.8, 3)
''', 'Half of k − 1, minus 1, times 0.3, plus 0.8. Round at the end.',
         '<p>For odd sizes up to 7 OpenCV actually uses fixed binomial weights, but this formula is what its documentation states and what it uses for larger kernels such as the project 9 × 9.</p>')
K.assign('rowsharp', 'm', 'Sharpen a row like filter2D',
         '<p>Write <code>sharpen_row(row)</code>. Treat the row as an image that does not change from top to bottom, so the project kernel acts as [−1, 3, −1]. At the ends reflect without repeating the edge pixel (the left neighbour of position 0 is position 1, the right neighbour of the last is the second last). Clip every result to 0 to 255 and return a list of ints.</p>',
         '''
def sharpen_row(row):
    # your code here
    pass
''', [('sharpen_row([10, 10, 10])', [10, 10, 10]), ('sharpen_row([50, 50, 200, 200])', [50, 0, 255, 200]),
      ('sharpen_row([100, 90, 100])', [120, 70, 120]), ('sharpen_row([60, 100, 140])', [0, 100, 220])],
         '''
def sharpen_row(row):
    n = len(row)
    out = []
    for i, v in enumerate(row):
        left = row[i - 1] if i > 0 else row[1]
        right = row[i + 1] if i < n - 1 else row[n - 2]
        out.append(max(0, min(255, 3 * v - left - right)))
    return out
''', 'Pick the left and right neighbours with the reflection rule, compute 3v − left − right, then clip.',
         '<p>The second test shows both halos: the dark side drops to 0 and the bright side hits 255. The last test shows the border effect, since reflection makes the first pixel see 100 on both sides.</p>')
K.assign('wonback', 'm', 'Share of the loss won back',
         '<p>Write <code>won_back(base, degraded, restored)</code> for one metric. Return the percentage of the loss that the restored stage recovered, (restored − degraded) ÷ (base − degraded) × 100, rounded to 1 decimal. Return 0.0 if there was no loss.</p>',
         '''
def won_back(base, degraded, restored):
    # your code here
    pass
''', [('won_back(0.5026, 0.4434, 0.4556)', 20.6), ('won_back(0.5894, 0.5358, 0.5468)', 20.5), ('won_back(0.6706, 0.6176, 0.6277)', 19.1), ('won_back(0.5, 0.5, 0.4)', 0.0)],
         '''
def won_back(base, degraded, restored):
    loss = base - degraded
    if loss == 0:
        return 0.0
    return round(100 * (restored - degraded) / loss, 1)
''', 'Compute the loss first and guard against zero.',
         '<p>About a fifth of every loss came back. For precision the formula gives a misleading number because blur raised precision, so read it only for metrics that fell.</p>')

K.must('The experiment', 'Frozen YOLO11n on COCO128 (128 images, 929 objects). Only the pixels change: baseline, 9 × 9 Gaussian blur, then the sharpening kernel. Labels are copied because nothing moves.')
K.must('Blur', 'GaussianBlur with σ = 0 uses σ = 0.3 ((k − 1) ÷ 2 − 1) + 0.8 = 1.7 for k = 9. Separable, 18 multiplications instead of 81. A low pass filter that removes edges and texture, hurting small and thin objects most.')
K.must('Sharpen', '[[0, −1, 0], [−1, 5, −1], [0, −1, 0]] = identity minus Laplacian = unsharp masking with a = 4. Weights add to 1. Gain 3 − 2 cos ω along an axis. Clipped to 0 to 255, which makes halos.')
K.must('Results', 'Blur: P 0.6633 → 0.6802, R 0.5894 → 0.5358, mAP50 0.6706 → 0.6176, mAP50-95 0.5026 → 0.4434. Sharpening won back about 20 percent of the recall and mAP losses and dropped P to 0.6583.')
K.must('Limits', 'COCO128 overlaps the training data, 128 images is a small sample, P and R come from the max F1 confidence, and one blur level was tested. Sharpen only images known to be blurred, and consider training with blur augmentation.')

T = K.topic(
    slug='project-lab', topic='project-lab', step=(8, 'Project lab', 'cv-project', 'Your own experiment rebuilt step by step: what blur and sharpening do to a YOLO detector, and how to read and question the results.', 'Hands on'),
    title='Project lab: blur, sharpening and detection', short='Project: blur and sharpen', badge='8.1', minutes=50,
    lead='Rebuild the mini project from the notebook: evaluate YOLO11n on COCO128, blur every image with a 9 × 9 Gaussian, sharpen with the Laplacian kernel, and explain every change in precision, recall and mAP.',
    desc='The YOLO11n and COCO128 blur and sharpening experiment: dataset copies with unchanged labels, OpenCV Gaussian blur and its σ rule, the sharpening kernel as identity minus Laplacian and as unsharp masking, frequency gains, the precision puzzle, share of the loss won back, F1, and the limits of the conclusion.',
    summary='The project notebook step by step: Gaussian blur, the sharpening kernel, the results table and what it can and cannot show.',
    keywords=['project', 'YOLO11n', 'COCO128', 'Gaussian blur', 'sharpening', 'Laplacian', 'unsharp masking', 'filter2D', 'precision', 'recall', 'mAP', 'F1', 'robustness', 'experiment design'],
    recap='<p>The same frozen detector was scored on original, blurred and sharpened copies of COCO128. The 9 × 9 Gaussian blur removed fine detail, cutting recall and mAP, most of all mAP50-95, while precision rose because fewer and easier boxes were reported. The Laplacian sharpening kernel boosted what detail remained and won back about a fifth of the losses, but it could not recreate lost detail and its noise boost lowered precision. The conclusion holds for this setup, with the caveats of training overlap and a small sample.</p>')
