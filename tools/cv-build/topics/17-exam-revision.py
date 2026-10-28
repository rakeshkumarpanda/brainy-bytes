# Chapter 17: exam revision. One place to revise the whole subject, organised by the kind of exam rather than by topic:
# school and first year questions, university semester and IIT course numericals, multiple choice and numerical answer
# papers in the NPTEL and GATE style, and derivation and essay questions in the style of MIT, Stanford and Cambridge.
# Every question here is an original practice question written in the style of that tier, not a copy of a past paper.
# Every number was checked with Python before it was written down.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('drill', r'''
# Exam drill: one convolution layer, every number an examiner can ask for
n = int(input("input size n: "))
k = int(input("kernel size k: "))
s = int(input("stride s: "))
p = int(input("padding p: "))
cin = int(input("input channels: "))
cout = int(input("output channels: "))

out = (n + 2 * p - k) // s + 1
weights = k * k * cin * cout
print("output size  = floor((", n, "+ 2 x", p, "-", k, ") /", s, ") + 1 =", out)
print("weights      =", k, "x", k, "x", cin, "x", cout, "=", weights, " plus", cout, "biases =", weights + cout)
print("mult adds    =", out, "x", out, "x", weights, "=", out * out * weights)
print("output shape =", out, "x", out, "x", cout)
''', stdin='32\n5\n2\n2\n3\n16\n')

K.lesson('map', 'How computer vision is examined', f'''
<p>This chapter is for the week before an exam. It does not teach new material. It shows the shapes questions take at each level, with worked answers, and points back to the chapter where each idea is taught. The questions are original practice questions written in the style of each tier, not copies of real past papers.</p>
{table(['Tier', 'Typical format', 'What earns the marks', 'Where to practise'], [
    ['School and first year', 'Short answers, small calculations, labelled diagrams', 'Correct definitions and units, careful arithmetic', 'Lesson 2'],
    ['University semester and IIT course exams', 'Numericals by hand, short notes, compare and contrast', 'Every step shown, formula stated first, final answer boxed', 'Lesson 3'],
    ['NPTEL and GATE style papers', 'Multiple choice, multiple select and numerical answer type, no partial credit', 'Speed, recognising the trap option, exact rounding', 'Lesson 4'],
    ['MIT, Stanford and Cambridge style', 'Derivations, proofs, design questions, critique of an experiment', 'Clear assumptions, a complete argument, trade offs named', 'Lesson 5']])}
{note('In a numerical, write the formula, substitute, then compute. Most lost marks come from skipping the first line, so the examiner cannot give method marks when the arithmetic slips.', 'exam')}
<h3>The ten ideas examined most often</h3>
<ol>
<li>Image as an array: size in bytes, colour to grey (chapter 2.1).</li>
<li>Histograms, contrast stretching and equalisation (chapter 2.2).</li>
<li>Convolution by hand, Gaussian and median filters, edge kernels (chapters 1.2 and 2.3).</li>
<li>Gradient magnitude and direction, Harris corners, HOG (chapter 1.2).</li>
<li>Optical flow constraint (chapter 3.1).</li>
<li>CNN output size, parameter count, receptive field (chapter 4.1).</li>
<li>IoU, NMS, anchors and detection losses (chapters 5.1 to 5.3).</li>
<li>Precision, recall, AP and mAP (chapter 5.4).</li>
<li>Segmentation metrics: pixel accuracy, IoU, mIoU, Dice (chapters 6.1 and 6.3).</li>
<li>Upsampling, transposed and dilated convolution, U-Net (chapter 6.2).</li>
</ol>
''', kw=['exam pattern', 'revision', 'school', 'university exam', 'IIT', 'NPTEL', 'GATE', 'MIT', 'Stanford', 'Cambridge', 'method marks'])

K.lesson('school', 'Tier 1: school and first year', f'''
<p>Questions at this level check that you can describe an image as numbers and do small calculations on it.</p>
{fxs(
    fx('Image size in bytes', 'width × height × channels × bytes per value', 'An 8 bit value takes 1 byte.', key=True),
    fx('Colour to grey', '<i>Y</i> = 0.299 <i>R</i> + 0.587 <i>G</i> + 0.114 <i>B</i>', 'Green counts most because the eye is most sensitive to it.', key=True),
    fx('Negative and brightness', 's = 255 − r, &nbsp; s = clip(r + b, 0, 255)', 'Results outside 0 to 255 are clipped.'))}
{steps('Question 1. How much memory does a Full HD colour photo take, uncompressed?', [
    'Full HD is 1920 × 1080 pixels with 3 channels of 1 byte.',
    '1920 × 1080 × 3 = 6,220,800 bytes.',
    'Divide by 1,048,576 (2<sup>20</sup>) to get about 5.93 MiB, or 6.22 MB in powers of ten. State which one you used.'])}
{steps('Question 2. Convert the pixel (R, G, B) = (200, 100, 50) to grey.', [
    'Y = 0.299 × 200 + 0.587 × 100 + 0.114 × 50.',
    '= 59.8 + 58.7 + 5.7 = 124.2.',
    'Round to the nearest whole number: 124.'])}
{steps('Question 3. How many different colours can a 24 bit image show?', [
    '8 bits per channel gives 2<sup>8</sup> = 256 levels.',
    'Three channels: 256 × 256 × 256.',
    '= 2<sup>24</sup> = 16,777,216 colours.'])}
<p>Short answer favourites: name three tasks of computer vision (classification, detection, segmentation), explain why the same object can look very different (viewpoint, light, occlusion, scale, deformation, clutter, from chapter 1.1), and explain why a photo file is smaller than width × height × 3 (compression, chapter 2.1).</p>
{note('A common slip is mixing bits and bytes. 24 bits per pixel is 3 bytes per pixel.', 'warn')}
''', kw=['image size', 'bytes', 'grey conversion', 'luminance', 'negative', 'brightness', 'bit depth', '24 bit colour', 'short answer'])

K.lesson('semester', 'Tier 2: university semester and IIT course exams', f'''
<p>Here the examiner gives a small matrix or a pair of boxes and asks you to work by hand. Show every step.</p>
{steps('Question 4. Apply the Sobel x kernel to the patch [[1, 2, 3], [4, 5, 6], [7, 8, 9]].', [
    'Sobel x = [[−1, 0, 1], [−2, 0, 2], [−1, 0, 1]]. Multiply matching entries and add.',
    'Top row: −1 + 3 = 2. Middle row: −8 + 12 = 4. Bottom row: −7 + 9 = 2.',
    'G<sub>x</sub> = 2 + 4 + 2 = 8. A positive value means brightness increases to the right.'])}
{steps('Question 5. G<sub>x</sub> = 3 and G<sub>y</sub> = 4. Find the gradient magnitude and direction.', [
    'Magnitude = √(3² + 4²) = √25 = 5.',
    'Direction θ = atan2(4, 3).',
    'θ ≈ 53.13°. The edge itself runs at right angles to this direction.'])}
{steps('Question 6. The Harris matrix is M = [[4, 0], [0, 4]] and k = 0.04. Find R and classify the point.', [
    'det M = 16, trace M = 8.',
    'R = det M − k (trace M)² = 16 − 0.04 × 64.',
    'R = 13.44, large and positive, so the point is a corner. Negative R means an edge, small |R| a flat area.'])}
{steps('Question 7. Boxes A = (0, 0, 4, 4) and B = (2, 2, 6, 6) as (x1, y1, x2, y2). Find IoU.', [
    'Overlap is from (2, 2) to (4, 4), area 4.',
    'Union = 16 + 16 − 4 = 28.',
    'IoU = 4 ÷ 28 = 1 ÷ 7 ≈ 0.143. Under the usual 0.5 rule these are different objects.'])}
{steps('Question 8. A conv layer has 3 × 3 kernels, 64 input and 128 output channels, with bias. How many parameters?', [
    'Weights per filter: 3 × 3 × 64 = 576.',
    '128 filters: 576 × 128 = 73,728.',
    'Add 128 biases: 73,856.'])}
{steps('Question 9. A detector finds 10 boxes, 8 correct, and 12 objects exist. Find P, R and F1.', [
    'TP = 8, FP = 2, FN = 12 − 8 = 4.',
    'P = 8 ÷ 10 = 0.8, R = 8 ÷ 12 ≈ 0.667.',
    'F1 = 2PR ÷ (P + R) = 1.0667 ÷ 1.4667 ≈ 0.727.'])}
<p>Short notes and compare questions at this level: median against Gaussian filter for salt and pepper noise (chapter 2.3), one stage against two stage detectors (chapter 5.3), semantic against instance against panoptic segmentation (chapter 6.1), FCN against U-Net (chapter 6.2), dense against sparse optical flow (chapter 3.1).</p>
{note('Write the box format before computing IoU. (x1, y1, x2, y2) and (x, y, w, h) give very different answers from the same four numbers.', 'warn')}
''', kw=['Sobel', 'convolution by hand', 'gradient magnitude', 'gradient direction', 'Harris', 'IoU', 'parameter count', 'precision', 'recall', 'F1', 'short notes'])

K.lesson('mcq', 'Tier 3: multiple choice and numerical answer papers', f'''
<p>NPTEL course exams and GATE style papers use multiple choice, multiple select and numerical answer questions with no partial credit. Speed matters, so learn the shortcuts and the trap options.</p>
{table(['Shortcut', 'Use it for'], [
    ['Same padding: p = (k − 1) ÷ 2 at stride 1', 'Size unchanged after a k × k conv'],
    ['Each stride 2 halves the size', '224 → 112 → 56 → 28 → 14 → 7'],
    ['Two 3 × 3 = reach 5, three 3 × 3 = reach 7', 'Receptive field without a formula'],
    ['Dilated kernel reach d (k − 1) + 1', '3 × 3 with d = 2 reaches 5'],
    ['Transposed conv out = (n − 1) s − 2p + k', 'k 4, s 2, p 1 exactly doubles the size'],
    ['Dice = 2 IoU ÷ (1 + IoU)', 'Convert between the two segmentation scores']])}
{viz('netsheet')}
{steps('Question 10. Logits (2, 1, 0), true class first. Find the cross entropy loss to three decimals.', [
    'e² = 7.389, e¹ = 2.718, e⁰ = 1. Sum 11.107.',
    'p = 7.389 ÷ 11.107 ≈ 0.665.',
    'Loss = −ln 0.665 ≈ 0.408.'])}
{steps('Question 11. A confusion matrix for two classes has rows (50, 10) and (5, 35), rows true and columns predicted. Find mIoU.', [
    'Class 0: TP 50, FN 10, FP 5. IoU = 50 ÷ 65 ≈ 0.769.',
    'Class 1: TP 35, FN 5, FP 10. IoU = 35 ÷ 50 = 0.700.',
    'mIoU = (0.769 + 0.700) ÷ 2 ≈ 0.735.'])}
{steps('Question 12. Focal loss with γ = 2 for a well classified example with p = 0.9. How much smaller is it than cross entropy?', [
    'Cross entropy = −ln 0.9 ≈ 0.105.',
    'Focal factor (1 − 0.9)² = 0.01.',
    'Focal loss ≈ 0.00105, 100 times smaller. Easy examples stop dominating the total.'])}
{note('Trap options to expect: forgetting the bias in a parameter count, using k instead of k − 1 in the receptive field, counting the background class in mIoU when the question excludes it, and rounding in the middle of a calculation.', 'exam')}
''', kw=['MCQ', 'numerical answer', 'NPTEL', 'GATE', 'shortcuts', 'same padding', 'stride', 'cross entropy', 'mIoU', 'confusion matrix', 'focal loss', 'Dice', 'traps'])

K.lesson('derive', 'Tier 4: derivations, design and critique', f'''
<p>Research university exams in the style of MIT, Stanford and Cambridge reward a complete argument more than a final number. A good answer states assumptions, derives the result, then says when it fails.</p>
<h3>Question 13. Show that a 2D Gaussian blur is separable and say why it matters.</h3>
{steps('Model answer', [
    'G(x, y) = (1 ÷ 2πσ²) e<sup>−(x² + y²) ÷ 2σ²</sup> = [(1 ÷ √(2π) σ) e<sup>−x² ÷ 2σ²</sup>] × [(1 ÷ √(2π) σ) e<sup>−y² ÷ 2σ²</sup>] = g(x) g(y).',
    'So G ∗ I = g<sub>y</sub> ∗ (g<sub>x</sub> ∗ I): blur every row, then every column.',
    'Cost per pixel falls from k² to 2k multiplications, for k = 15 from 225 to 30, 7.5 times less.',
    'Also, two Gaussian blurs make one Gaussian with σ = √(σ₁² + σ₂²), so σ = 3 then 4 equals one blur with σ = 5.'])}
<h3>Question 14. Derive the optical flow constraint and explain the aperture problem.</h3>
{steps('Model answer', [
    'Assume a point keeps its brightness as it moves: I(x + u, y + v, t + 1) = I(x, y, t).',
    'A first order Taylor expansion gives I<sub>x</sub> u + I<sub>y</sub> v + I<sub>t</sub> = 0.',
    'One equation, two unknowns: only the flow along the gradient is fixed. That is the aperture problem.',
    'Lucas and Kanade assume the flow is constant in a small window and solve the stacked equations by least squares. Example: I<sub>x</sub> = 2, I<sub>y</sub> = 1, I<sub>t</sub> = −4 with v = 0 gives u = 2.'])}
<h3>Question 15. Derive how stereo depth error grows with distance.</h3>
{steps('Model answer', [
    'Similar triangles give Z = f B ÷ d.',
    'Differentiate: dZ ÷ dd = −f B ÷ d² = −Z² ÷ (f B).',
    'So ΔZ ≈ Z² Δd ÷ (f B). Error grows with the square of depth and falls with focal length and baseline.',
    'With f = 500 px, B = 0.1 m and d = 25 px, Z = 2 m, and a 1 pixel error costs about 0.08 m.'])}
<h3>Design and critique questions</h3>
<p>A design question such as build a system that counts people in a crowded station has no single answer. Structure it as: the data and labels you need, the model family and why (detector, density map or segmentation), the metric that matches the goal, the failure cases (occlusion, scale, lighting) and how you would test them. A critique question gives an experiment, such as the blur and sharpening project in chapter 8.1, and asks what it shows. Name the controlled variable, the sample size, any train and test overlap, the operating point, and one experiment that would make the claim stronger.</p>
{note('In derivations, name each assumption when you use it: brightness constancy, small motion, rectified cameras, known σ. Examiners often ask what breaks when an assumption fails.', 'exam')}
{ladder(
    '<p>At school you are asked what a picture is made of and how to change it. You show you can count and convert carefully.</p>',
    '<p>At university you are given a small matrix or two boxes and asked to apply a formula by hand, showing each step.</p>',
    '<p>In competitive papers you must recognise the right formula quickly, avoid the trap options and round only at the end.</p>',
    '<p>At research universities you derive the formula yourself, state its assumptions, and argue when a method or an experiment fails.</p>')}
''', kw=['derivation', 'separable Gaussian', 'Gaussian cascade', 'optical flow constraint', 'aperture problem', 'Lucas Kanade', 'stereo error', 'design question', 'critique', 'assumptions', 'MIT', 'Cambridge', 'Stanford'])

K.lesson('sheet', 'Formula sheet and last minute checks', f'''
{table(['Topic', 'Formula'], [
    ['Grey value', 'Y = 0.299 R + 0.587 G + 0.114 B'],
    ['Equalisation', 's<sub>k</sub> = round((L − 1) × CDF(r<sub>k</sub>))'],
    ['Gradient', '|∇I| = √(G<sub>x</sub>² + G<sub>y</sub>²), θ = atan2(G<sub>y</sub>, G<sub>x</sub>)'],
    ['Harris', 'R = det M − k (trace M)²'],
    ['Flow constraint', 'I<sub>x</sub> u + I<sub>y</sub> v + I<sub>t</sub> = 0'],
    ['Conv output', '⌊(n + 2p − k) ÷ s⌋ + 1'],
    ['Conv weights', 'k² C<sub>in</sub> C<sub>out</sub> + C<sub>out</sub>'],
    ['Receptive field', 'r ← r + (k − 1) j, j ← j s'],
    ['Transposed conv', '(n − 1) s − 2p + k'],
    ['IoU, Dice', 'A ∩ B ÷ A ∪ B, &nbsp; 2 |A ∩ B| ÷ (|A| + |B|)'],
    ['Precision, recall, F1', 'TP ÷ (TP + FP), TP ÷ (TP + FN), 2PR ÷ (P + R)'],
    ['Cross entropy, focal', '−ln p, &nbsp; −(1 − p)<sup>γ</sup> ln p'],
    ['Stereo', 'Z = f B ÷ d, ΔZ ≈ Z² Δd ÷ (f B)'],
    ['ViT tokens', '(n ÷ p)², attention pairs N²']])}
{code('drill')}
<h3>Ten mistakes that cost marks</h3>
<ol>
<li>Rounding in the middle of a long calculation.</li>
<li>Forgetting biases in parameter counts.</li>
<li>Mixing box formats in IoU.</li>
<li>Forgetting to clip pixel values to 0 to 255.</li>
<li>Flipping the kernel for correlation, or not flipping it when the question says true convolution.</li>
<li>Treating mAP as the mean of precision instead of the mean of AP over classes.</li>
<li>Using pixel accuracy on unbalanced classes where mIoU is asked for.</li>
<li>Forgetting that NMS runs per class in most detectors.</li>
<li>Writing degrees when the formula needs radians.</li>
<li>Giving a design answer without a metric and a failure case.</li>
</ol>
''', kw=['formula sheet', 'common mistakes', 'last minute revision', 'equalisation', 'conv output', 'receptive field', 'IoU', 'Dice', 'stereo'])

# ---------------------------------------------------------------- mock quiz
K.quiz('e', 'An 8 bit grey image of 640 × 480 pixels takes how many bytes uncompressed?', ['307,200', '921,600', '2,457,600', '76,800'], 0,
       'One byte per pixel.', '640 × 480 = 307,200. RGB would be three times that.')
K.quiz('e', 'Which colour gets the largest weight in the grey conversion?', ['Red', 'Green', 'Blue', 'All equal'], 1,
       '0.587.', 'The eye is most sensitive to green.')
K.quiz('e', 'Which filter is best for salt and pepper noise?', ['Mean', 'Gaussian', 'Median', 'Sobel'], 2,
       'Outliers.', 'The median ignores extreme values instead of averaging them in.')
K.quiz('m', 'A 32 × 32 input, 5 × 5 kernel, stride 2, padding 2 gives an output of', ['14', '15', '16', '32'], 2,
       '⌊(32 + 4 − 5) ÷ 2⌋ + 1.', '⌊31 ÷ 2⌋ + 1 = 16.')
K.quiz('m', 'Harris R is large and negative. The point is', ['A corner', 'An edge', 'Flat', 'Noise'], 1,
       'One large eigenvalue.', 'Negative R means one strong direction, an edge.')
K.quiz('m', 'Two boxes with IoU 1 ÷ 7 under NMS at threshold 0.5', ['Suppress each other', 'Both survive', 'Merge', 'Are removed'], 1,
       '0.143 < 0.5.', 'Only overlaps above the threshold are suppressed.')
K.quiz('m', 'Dice for IoU = 0.6 is', ['0.6', '0.75', '0.8', '0.5'], 1,
       '2 IoU ÷ (1 + IoU).', '1.2 ÷ 1.6 = 0.75.')
K.quiz('h', 'A transposed conv with k = 4, s = 2, p = 1 on a 16 × 16 map gives', ['8', '16', '32', '34'], 2,
       '(n − 1) s − 2p + k.', '30 − 2 + 4 = 32, exactly double.')
K.quiz('h', 'Three stacked 3 × 3 convs at stride 1 have the reach of one', ['3 × 3', '5 × 5', '7 × 7', '9 × 9'], 2,
       'Each adds 2.', '1 + 2 + 2 + 2 = 7, with 27 instead of 49 weights per channel pair.')
K.quiz('h', 'The optical flow constraint alone cannot give flow because', ['Images are noisy', 'It is one equation in two unknowns', 'It needs colour', 'Brightness changes'], 1,
       'The aperture problem.', 'Only the component along the gradient is fixed.')
K.quiz('x', 'Two Gaussian blurs with σ = 3 and σ = 4 equal one blur with σ =', ['5', '7', '12', '3.5'], 0,
       'Variances add.', '√(9 + 16) = 5.')
K.quiz('x', 'Stereo depth error at 3 times the distance, everything else fixed, is', ['3 times larger', '9 times larger', 'the same', '3 times smaller'], 1,
       'Z².', 'ΔZ ≈ Z² Δd ÷ (f B).')
K.quiz('x', 'In a critique of the blur experiment, which point most limits the baseline score?', ['The GPU type', 'COCO128 images come from the training set of the pretrained model', 'The batch size', 'The YAML file name'], 1,
       'Train and test overlap.', 'The baseline is optimistic. Use held out images.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many bytes does an uncompressed 1920 × 1080 RGB image with 8 bit channels take?', '6220800', 'width × height × 3.',
       ['1920 × 1080 = 2,073,600 pixels.', 'Three bytes per pixel.', eq('6,220,800 bytes')], check=6220800)
K.calc('e', 'Grey value of (R, G, B) = (200, 100, 50), rounded to a whole number?', '124', 'Y = 0.299 R + 0.587 G + 0.114 B.',
       ['59.8 + 58.7 + 5.7.', '= 124.2.', eq('Y ≈ 124')], check=124)
K.calc('e', 'Negative of a pixel with value 70 in an 8 bit image?', '185', 's = 255 − r.',
       ['L − 1 = 255.', '255 − 70.', eq('s = 185')], check=185)
K.calc('m', 'Sobel x on [[1, 2, 3], [4, 5, 6], [7, 8, 9]]?', '8', 'Kernel [[−1, 0, 1], [−2, 0, 2], [−1, 0, 1]].',
       ['Rows give 2, 4 and 2.', 'Add them.', eq('G<sub>x</sub> = 8')], check=8)
K.calc('m', 'Gradient direction in degrees for G<sub>x</sub> = 3, G<sub>y</sub> = 4? Give two decimals.', '53.13', 'atan2(G<sub>y</sub>, G<sub>x</sub>).',
       ['tan θ = 4 ÷ 3.', 'θ = atan(1.333).', eq('θ ≈ 53.13°')], check=53.1301, tol=0.006)
K.calc('m', 'Harris R for M = [[4, 0], [0, 4]] with k = 0.04?', '13.44', 'det − k trace².',
       ['det = 16, trace = 8.', '0.04 × 64 = 2.56.', eq('R = 13.44')], check=13.44, tol=1e-9)
K.calc('m', 'Parameters in a 3 × 3 conv from 64 to 128 channels with bias?', '73856', 'k² C<sub>in</sub> C<sub>out</sub> + C<sub>out</sub>.',
       ['9 × 64 = 576 per filter.', '576 × 128 = 73,728.', eq('+ 128 = 73,856')], check=73856)
K.calc('m', 'F1 for 8 correct out of 10 boxes when 12 objects exist? Give three decimals.', '0.727', '2PR ÷ (P + R).',
       ['P = 0.8, R = 0.667.', '2 × 0.8 × 0.667 = 1.0667.', eq('1.0667 ÷ 1.4667 ≈ 0.727')], check=8 / 11, tol=0.0006)
K.calc('h', 'Cross entropy for logits (2, 1, 0) with the first class true? Three decimals.', '0.408', '−ln SoftMax.',
       ['Exponentials 7.389, 2.718, 1.', 'p = 7.389 ÷ 11.107 ≈ 0.665.', eq('−ln 0.665 ≈ 0.408')], check=0.4076, tol=0.0006)
K.calc('h', 'mIoU for the confusion matrix rows (50, 10) and (5, 35)? Three decimals.', '0.735', 'Per class TP ÷ (TP + FP + FN).',
       ['Class 0: 50 ÷ 65 ≈ 0.769.', 'Class 1: 35 ÷ 50 = 0.700.', eq('mean ≈ 0.735')], check=0.7346, tol=0.0006)
K.calc('h', 'Multiply adds of a 3 × 3 conv, 64 to 64 channels, with a 56 × 56 output?', '115605504', 'out² k² C<sub>in</sub> C<sub>out</sub>.',
       ['56² = 3,136 positions.', '9 × 64 × 64 = 36,864 per position.', eq('3,136 × 36,864 = 115,605,504')], check=115605504)
K.calc('h', 'Parameters of a ViT patch embedding for 16 × 16 RGB patches into 768 dimensions, with bias?', '590592', 'A linear layer.',
       ['Inputs per patch: 16 × 16 × 3 = 768.', '768 × 768 = 589,824 weights.', eq('+ 768 biases = 590,592')], check=590592)
K.calc('x', 'One Gaussian equivalent to blurring with σ = 3 and then σ = 4?', '5', 'Variances add.',
       ['σ² = 9 + 16.', '= 25.', eq('σ = 5')], check=5)
K.calc('x', 'I<sub>x</sub> = 2, I<sub>y</sub> = 1, I<sub>t</sub> = −4 and v = 0. Find u.', '2', 'I<sub>x</sub> u + I<sub>y</sub> v + I<sub>t</sub> = 0.',
       ['2u + 0 − 4 = 0.', '2u = 4.', eq('u = 2 pixels per frame')], check=2)
K.calc('x', 'f = 500 px, B = 0.1 m, d = 25 px. Depth error for a 1 pixel disparity error, by the rule of thumb?', '0.08', 'Z² Δd ÷ (f B).',
       ['Z = 50 ÷ 25 = 2 m.', 'Z² = 4, f B = 50.', eq('ΔZ ≈ 4 ÷ 50 = 0.08 m')], check=0.08)
K.calc('x', 'Cost ratio of a direct 15 × 15 blur to a separable one?', '7.5', 'k² against 2k.',
       ['Direct: 225.', 'Separable: 30.', eq('225 ÷ 30 = 7.5')], check=7.5)

T = K.topic(
    slug='exam-revision', topic='exam-revision', kind='revision',
    step=(9, 'Exam revision', 'cv-revision', 'Revise the whole subject by exam style, from school questions to IIT numericals, NPTEL and GATE style papers, and MIT and Cambridge style derivations.', 'All levels'),
    title='Exam revision: from school to research universities', short='Exam revision', badge='9.1', minutes=60,
    lead='Practise the question shapes of every level with worked answers: image arithmetic, numericals by hand, quick multiple choice tricks, and derivations with their assumptions.',
    desc='Exam patterns by tier, worked questions on image size, grey conversion, Sobel, Harris, IoU, parameter counts, F1, cross entropy, mIoU, focal loss, separable Gaussians, optical flow and stereo error, a formula sheet and common mistakes.',
    summary='Exam style questions from school level to research universities, with worked answers, a formula sheet and a mock quiz.',
    keywords=['exam', 'revision', 'formula sheet', 'mock quiz', 'numericals', 'derivations', 'IIT', 'NPTEL', 'GATE', 'MIT', 'Cambridge', 'Stanford'],
    recap='')
