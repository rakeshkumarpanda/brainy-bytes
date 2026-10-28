# Chapter 2: Marr's stages of vision, what a feature is, image gradients, SIFT and HOG.
# Sources: lecture 1 (Marr, features, SIFT, HOG) and the HOG recap in lectures 3 and 4.
# Facts checked against Lowe 2004 (SIFT: DoG scale space, 4 x 4 x 8 = 128 descriptor, ratio test 0.8)
# and Dalal and Triggs 2005 (HOG: 64 x 128 window, 8 x 8 cells, 9 unsigned bins, 2 x 2 blocks, 3,780 numbers).
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('sobel', r'''
# Sobel gradients at one pixel of a small grey patch
patch = [
    [10, 10, 10, 50, 50],
    [10, 10, 10, 50, 50],
    [10, 10, 10, 50, 50],
    [10, 10, 10, 50, 50],
]
KX = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]     # change from left to right
KY = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]     # change from top to bottom

r = int(input("Row (1 to 2): "))
c = int(input("Column (1 to 3): "))
gx = gy = 0
for i in range(3):
    for j in range(3):
        v = patch[r + i - 1][c + j - 1]
        gx += KX[i][j] * v
        gy += KY[i][j] * v

from math import atan2, degrees, hypot
print("Gx =", gx, " Gy =", gy)
print("magnitude =", round(hypot(gx, gy), 2))
print("direction =", round(degrees(atan2(gy, gx)), 1), "degrees")
''', stdin='1\n2\n')

K.code('hogcell', r'''
# One HOG cell: every pixel votes its gradient angle into 9 bins of 20 degrees,
# split between the two nearest bin centres and weighted by its magnitude
mags = [10, 20, 5, 15]
angs = [25, 90, 170, 100]          # unsigned angles, 0 to 180 degrees
bins = 9
width = 180 / bins                 # 20 degrees per bin
hist = [0.0] * bins
for m, a in zip(mags, angs):
    pos = a / width - 0.5          # bin centres are at 10, 30, 50, ... degrees
    left = int(pos // 1)
    t = pos - left                 # how far we are toward the next centre
    hist[left % bins] += m * (1 - t)
    hist[(left + 1) % bins] += m * t
    print(f"angle {a:3d} -> bins {left % bins} and {(left + 1) % bins}, share {1 - t:.2f} and {t:.2f}")
print("histogram:", [round(h, 2) for h in hist])
''')

K.code('ratio', r'''
# Matching keypoints with Lowe's ratio test
from math import dist

query = [0.9, 0.1, 0.4]                 # a short descriptor from image 1
candidates = {                          # descriptors from image 2
    "A": [0.88, 0.12, 0.41],
    "B": [0.20, 0.80, 0.10],
    "C": [0.70, 0.30, 0.50],
}
ranked = sorted(candidates.items(), key=lambda kv: dist(query, kv[1]))
(best, d1), (second, d2) = [(k, dist(query, v)) for k, v in ranked[:2]]
print("nearest:", best, round(d1, 3), " second:", second, round(d2, 3))
ratio = d1 / d2
print("ratio:", round(ratio, 3))
print("accept the match" if ratio < 0.8 else "reject: the best match is not clearly better")
''')

K.lesson('marr', "Marr's stages of vision", f'''
<p>David Marr, a British neuroscientist working at MIT, described vision as a chain of representations rather than one big jump from pixels to meaning. His book <i>Vision</i> (published in 1982) still shapes how the subject is taught. The idea is simple: each stage removes some ambiguity and hands a cleaner description to the next.</p>
{table(['Stage', 'What it contains', 'Question it answers'], [
    ['1. Input image', 'Pixel intensities, colour, local contrast', 'What signal did the camera capture?'],
    ['2. Primal sketch', 'Edges, bars, blobs, ends, zero crossings, groups, boundaries', 'Where does structure begin and end?'],
    ['3. 2½-D sketch', 'Depth and surface orientation of the visible surfaces, discontinuities', 'How are the visible surfaces arranged relative to me?'],
    ['4. 3D model', 'Volumes and parts in an object centred frame', 'What is the object and what is its full shape?']])}
<h3>Why "two and a half" D</h3>
<p>The 2½-D sketch knows more than a flat picture, because it has depth and the tilt of each visible surface. It knows less than a full 3D model, because it only describes what the camera can see from where it stands. Look at a basketball: you can tell the near surface is curved and which parts are closer, but you cannot see the back. That viewpoint dependence is the half.</p>
{note('Depth is not volume. A depth map gives the distance to each visible surface. A 3D model describes the whole object, including the hidden back. The exam asks this as "why is it called 2½-D".', 'exam')}
<h3>An edge is evidence, not an answer</h3>
<p>An edge in the primal sketch can be an object boundary, a change in surface direction, a change in material, a shadow or a change in lighting. The edge only says "something changes here". Later stages decide what.</p>
{ladder(
    '<p>When you draw a cat, you first draw outlines, then shade to show which parts stick out, and only then does it look like a real cat. Marr said computers should see in the same order: outlines first, then shape, then the whole object.</p>',
    '<p>Each stage is a different data structure. The image is a 2D array of intensities. The primal sketch is a set of tokens (edge segments with position, orientation and contrast). The 2½-D sketch is a map giving depth and a surface normal for every visible point. The 3D model is a hierarchy of parts, each a simple volume such as a generalised cylinder.</p>',
    '<p>Marr also proposed three levels for explaining any information processing system: the computational level (what problem is solved and why), the algorithmic level (which representation and procedure), and the implementational level (the hardware, neurons or silicon). This is useful for analysing any vision method: first state what it computes, then how, then on what.</p>',
    '<p>Deep networks do not build explicit Marr stages, yet probing studies find intermediate layers that encode edges, then surface properties such as depth and normals, then object identity. Current work on monocular depth estimation and 3D aware generative models can be read as learning the 2½-D and 3D stages end to end.</p>')}
''', kw=['Marr', 'primal sketch', '2.5D sketch', '2½-D', '3D model', 'depth versus volume', 'three levels'])

K.lesson('features', 'What makes a good feature', f'''
<p>A <b>feature</b> is a distinctive, useful property of an image region: a corner, an edge, a texture, a colour change, a blob. Pixels alone are usually not enough. A feature is computed from pixels to carry information that helps with matching, tracking, alignment, reconstruction or recognition.</p>
<h3>Three properties of a good feature point</h3>
{table(['Property', 'Meaning', 'Bad example', 'Good example'], [
    ['Distinctive', 'Its neighbourhood looks unlike most other places', 'A patch of plain blue sky', 'The corner of a window'],
    ['Stable (repeatable)', 'It is found again in a second photo of the same scene', 'A reflection that moves when you move', 'A painted letter on a sign'],
    ['Invariant', 'Its description stays the same under scale, rotation and lighting changes', 'Raw pixel values', 'A normalised histogram of gradient directions']])}
<h3>Flat, edge and corner</h3>
<p>Imagine sliding a small window over the image. In a <b>flat</b> region the window looks the same wherever you move it, so you cannot tell where you are. On an <b>edge</b> it changes when you move across the edge but not along it, so you only know your position in one direction. At a <b>corner</b> it changes whichever way you move, so the position is pinned down. This is why corner detectors (Harris, FAST) and blob detectors (SIFT) are the classic keypoint finders.</p>
{note('Feature detection finds where the interesting points are. Feature description turns the neighbourhood of each point into a vector of numbers so points can be compared. SIFT does both. HOG is mainly a descriptor.', 'exam')}
{scene('stitching a phone panorama', '<p>When you sweep your phone for a panorama, the app finds keypoints in each frame, describes them, and matches descriptors between neighbouring frames. Three or four good matches fix how one frame lines up with the next. If you sweep across a white wall, there are no distinctive points, the matches fail, and the panorama tears. That is the "flat region" problem in real life.</p>')}
''', kw=['feature', 'distinctive', 'stable', 'repeatable', 'invariant', 'corner', 'edge', 'flat region', 'detection versus description', 'panorama'])

K.lesson('gradients', 'Image gradients', f'''
<p>A gradient measures how fast brightness changes and in which direction. It is the basic signal behind edges, HOG, SIFT, optical flow and even the first layer of a CNN.</p>
<p>For a function of one variable the derivative is the slope. An image has two directions, so it has two partial derivatives. Pixels are discrete, so we replace the derivative by a difference of neighbours.</p>
{fxs(
    fx('Central difference', '<i>G<sub>x</sub></i> ≈ <i>I</i>(<i>x</i> + 1, <i>y</i>) − <i>I</i>(<i>x</i> − 1, <i>y</i>)', 'Often divided by 2. The kernel is [−1, 0, 1].'),
    fx('Gradient magnitude', '|∇<i>I</i>| = ' + sqrt('<i>G<sub>x</sub></i>² + <i>G<sub>y</sub></i>²'), 'How strong the edge is.', key=True),
    fx('Gradient direction', 'θ = atan2(<i>G<sub>y</sub></i>, <i>G<sub>x</sub></i>)', 'Points across the edge, from dark to bright.', key=True))}
{fx('Sobel kernels', '<i>K<sub>x</sub></i> = ' + mat([['−1', '0', '1'], ['−2', '0', '2'], ['−1', '0', '1']]) + ' &nbsp; <i>K<sub>y</sub></i> = ' + mat([['−1', '−2', '−1'], ['0', '0', '0'], ['1', '2', '1']]), 'Sobel is a central difference in one direction combined with a small smoothing [1, 2, 1] in the other direction, which makes it less sensitive to noise. Prewitt uses [1, 1, 1] instead.')}
{viz('gradient')}
{steps('Worked example: Sobel on a vertical edge', [
    'Take the 3 × 3 neighbourhood ' + mat([['10', '10', '50'], ['10', '10', '50'], ['10', '10', '50']]) + '.',
    'Multiply by <i>K<sub>x</sub></i> value by value and add: (−1)(10) + 0 + (1)(50) + (−2)(10) + 0 + (2)(50) + (−1)(10) + 0 + (1)(50) = 160.',
    'Multiply by <i>K<sub>y</sub></i>: the top row and bottom row are the same, so they cancel and <i>G<sub>y</sub></i> = 0.',
    'Magnitude √(160² + 0²) = 160. Direction atan2(0, 160) = 0°, so the arrow points right, from the dark side to the bright side.'])}
{code('sobel')}
{note('With image coordinates the y axis points down. An angle of 90° therefore means "brightness increases downwards". Many textbooks draw y upwards, so check which convention a question uses.', 'warn')}
''', kw=['gradient', 'derivative', 'Sobel', 'Prewitt', 'central difference', 'gradient magnitude', 'gradient direction', 'atan2', 'edge'])

K.lesson('sift', 'SIFT: keypoints that survive zoom and rotation', f'''
<p>SIFT (Scale Invariant Feature Transform, David Lowe, 2004) finds distinctive points and describes them so the same point can be matched between two photos, even if one is zoomed, rotated or lit differently. The notes stress that it is invariant, or at least robust, to scale and rotation. It does not promise that every point matches after any change.</p>
<h3>The four steps</h3>
<ol>
<li><b>Scale space search.</b> Blur the image with Gaussians of growing width σ and subtract neighbouring blurs. This difference of Gaussians (DoG) responds strongly to blobs whose size matches σ. Keypoints are the maxima and minima across position and scale.</li>
<li><b>Keypoint refinement.</b> Throw away points with low contrast and points that lie along edges, because they are unstable.</li>
<li><b>Orientation.</b> Build a histogram of gradient directions around the point and take the strongest one. All later measurements are made relative to this angle, which is what makes SIFT rotation invariant.</li>
<li><b>Descriptor.</b> Split the neighbourhood into a 4 × 4 grid of cells, and in each cell make an 8 bin histogram of gradient directions. That gives 4 × 4 × 8 = 128 numbers, normalised to reduce the effect of lighting.</li>
</ol>
{fxs(
    fx('Gaussian blur', '<i>L</i>(<i>x</i>, <i>y</i>, σ) = <i>G</i>(<i>x</i>, <i>y</i>, σ) ∗ <i>I</i>(<i>x</i>, <i>y</i>)', '<i>G</i> is a Gaussian of width σ and ∗ is convolution.'),
    fx('Difference of Gaussians', 'DoG = <i>L</i>(<i>x</i>, <i>y</i>, <i>k</i>σ) − <i>L</i>(<i>x</i>, <i>y</i>, σ)', 'Close to (<i>k</i> − 1) σ² ∇²<i>G</i> ∗ <i>I</i>, the scale normalised Laplacian.'),
    fx('Descriptor length', '4 × 4 cells × 8 bins = 128', 'Each cell is a small histogram of gradient directions.', key=True),
    fx('Lowe ratio test', frac('<i>d</i><sub>1</sub>', '<i>d</i><sub>2</sub>') + ' &lt; 0.8', '<i>d</i><sub>1</sub> and <i>d</i><sub>2</sub> are the distances to the nearest and second nearest descriptor. Accept the match only if the best is clearly better than the runner up.'))}
{viz('scalespace')}
{code('ratio')}
{deep('why the peak tells you the size', '<p>For a bright disc of radius <i>r</i>, the scale normalised Laplacian of Gaussian at the centre of the disc is largest when σ = <i>r</i> ÷ √2. If the photo is zoomed by a factor <i>s</i>, the disc has radius <i>sr</i> and the peak moves to <i>s</i>σ. So the detector reports a size that grows with the zoom, and a descriptor measured over a region proportional to that size sees the same content in both photos. This is the precise meaning of scale invariance.</p>')}
''', kw=['SIFT', 'scale invariance', 'rotation invariance', 'difference of Gaussians', 'DoG', 'scale space', 'keypoint', '128 descriptor', 'ratio test', 'Lowe'])

K.lesson('hog', 'HOG: describing shape with edge directions', f'''
<p>HOG (Histogram of Oriented Gradients, Dalal and Triggs, 2005) describes the shape of an object through the directions of its edges. It was built for detecting pedestrians and worked far better than earlier features on that task.</p>
<h3>How HOG is built</h3>
<ol>
<li>Compute <i>G<sub>x</sub></i> and <i>G<sub>y</sub></i> for every pixel, then the magnitude and direction.</li>
<li>Cut the detection window (64 × 128 pixels for a standing person) into cells of 8 × 8 pixels.</li>
<li>In each cell, make a histogram with 9 bins covering 0° to 180°. Each pixel votes for its direction with a weight equal to its magnitude, split between the two nearest bins.</li>
<li>Group cells into overlapping blocks of 2 × 2 cells and normalise each block, so a change in lighting or contrast does not change the numbers much.</li>
<li>Join all block vectors into one long descriptor and feed it to a classifier, usually a linear support vector machine.</li>
</ol>
{fxs(
    fx('Bin width', 'width = ' + frac('180°', 'number of bins'), '9 bins give 20° per bin, with centres at 10°, 30°, 50° and so on.'),
    fx('Vote split', 'share to the upper bin = ' + frac('θ − <i>c</i><sub>lower</sub>', 'bin width'), 'The rest goes to the lower bin. Both shares are multiplied by the magnitude.'),
    fx('Descriptor length', '(<i>n<sub>x</sub></i> − 1)(<i>n<sub>y</sub></i> − 1) × 4 × <i>B</i>', 'For 64 × 128 with 8 × 8 cells: 7 × 15 = 105 blocks, each 4 × 9 = 36 numbers, so 3,780 in total.', key=True),
    fx('Block normalisation (L2)', '<i>v</i> ← ' + frac('<i>v</i>', sqrt('‖<i>v</i>‖² + ε²')), 'ε is a small number that avoids dividing by zero.'))}
{viz('hog')}
{code('hogcell')}
<h3>Why it works and where it fails</h3>
<p>HOG looks at edge directions, not colours, so a person in a red coat and a person in a blue coat give similar descriptors. The cells allow a little movement of each body part without changing the histogram much. It struggles when contrast is very low, the object bends or changes pose (sitting, lying down), the object is partly hidden, the background is very cluttered, or the object has few strong edges.</p>
{table(['', 'SIFT', 'HOG'], [
    ['Main use', 'Matching the same points across images', 'Describing the shape of a whole window for detection'],
    ['Where it is computed', 'Around sparse keypoints, at their own scale', 'Densely, on a fixed grid of cells'],
    ['Invariance', 'Scale and rotation by design, partly lighting', 'Lighting and small shifts, not rotation or pose'],
    ['Length', '128 per keypoint', '3,780 for a 64 × 128 window']])}
''', kw=['HOG', 'histogram of oriented gradients', 'Dalal Triggs', 'cells', 'blocks', 'bins', 'block normalisation', 'pedestrian detection', 'SVM', '3780'])

K.lesson('today', 'Why classical features still matter', f'''
<p>CNNs and transformers are more accurate on most benchmarks, so why learn SIFT and HOG? The notes give four reasons.</p>
{table(['Reason', 'What it means', 'Example'], [
    ['Efficiency', 'Little memory, little power, no training data needed', 'A doorbell camera, a microcontroller, a drone'],
    ['Interpretability', 'You can say why the system fired', 'A HOG glyph shows the shoulder edges that made the detector fire'],
    ['Domain knowledge', 'If you know the key pattern, you can measure it directly', 'Finding a logo, a QR code, the straight edges of a document'],
    ['Working with deep models', 'They can prepare or support a learned model', 'Keypoints for camera tracking in AR, matching in 3D reconstruction']])}
<p>Classical keypoints are still used inside modern systems. Building 3D models from internet photo collections, which the second lecture shows with the city of Rome, relies on matching keypoints across thousands of photos and then triangulating the matched points.</p>
{ladder(
    '<p>Some jobs need a big powerful machine and some need a pocket knife. Hand made features are the pocket knife: small, quick and easy to understand.</p>',
    '<p>A HOG plus SVM detector runs in real time on a CPU and needs a few thousand labelled windows. A CNN detector is more accurate but needs a GPU and tens of thousands of labelled images. Choose by accuracy needs, hardware and data.</p>',
    '<p>Learned descriptors (such as SuperPoint and the matchers built on it) now outperform SIFT in many matching benchmarks, but SIFT remains a strong baseline because it is training free and behaves predictably on new domains such as medical or aerial images.</p>',
    '<p>An open research theme is to combine the inductive biases of classical features, such as explicit scale and rotation handling, with learned representations, through equivariant networks or differentiable versions of classical pipelines.</p>')}
''', kw=['classical features', 'efficiency', 'interpretability', 'edge devices', 'domain knowledge', '3D reconstruction', 'keypoint matching'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In Marr\'s pipeline, which stage first contains depth and surface orientation?', ['Input image', 'Primal sketch', '2½-D sketch', '3D model'], 2,
       'The half D is the clue.', 'The 2½-D sketch holds depth and surface orientation of the visible surfaces from the current viewpoint.')
K.quiz('e', 'Which of these is the poorest feature point?', ['The corner of a window', 'A point in a plain blue sky', 'The end of a painted line', 'A small bright blob'], 1,
       'Can you find the same point again?', 'Every point in a plain sky looks the same, so it is not distinctive and cannot be located.')
K.quiz('e', 'What does the gradient magnitude tell you?', ['The colour of a pixel', 'How strong the change in brightness is', 'The size of the image', 'The number of objects'], 1,
       'Magnitude means size.', 'A large magnitude means brightness changes sharply, which usually means an edge.')
K.quiz('m', 'Why is Marr\'s middle representation called 2½-D?', [
    'It uses two and a half colour channels',
    'It holds depth for the visible surfaces only, more than a flat image but less than a full 3D model',
    'It is half the resolution of the image',
    'It is computed in two and a half seconds'], 1,
    'Think about the back of a basketball.', 'It depends on the viewpoint. Depth of visible surfaces is known, but hidden surfaces and full volume are not.')
K.quiz('m', 'A Sobel kernel is a central difference combined with what?', ['A median filter', 'Smoothing with weights 1, 2, 1 in the other direction', 'A colour conversion', 'A threshold'], 1,
       'Look at the middle row of Kx.', 'The [1, 2, 1] weights average three rows, which reduces the effect of noise compared with a plain difference.')
K.quiz('m', 'How many numbers are in a standard SIFT descriptor?', ['9', '36', '128', '3,780'], 2,
       '4 × 4 cells with 8 bins each.', '4 × 4 × 8 = 128.')
K.quiz('m', 'What makes SIFT rotation invariant?', [
    'It ignores gradients',
    'It measures the descriptor relative to the dominant gradient orientation at the keypoint',
    'It only works on square images',
    'It converts images to grey'], 1,
    'Step 3 of SIFT.', 'Each keypoint gets its own orientation, and the descriptor grid is rotated to match it, so a rotated photo produces the same descriptor.')
K.quiz('h', 'In the Lowe ratio test, a match with d1 = 0.5 and d2 = 0.55 is', ['Accepted, because d1 is small', 'Rejected, because d1 ÷ d2 ≈ 0.91 is above 0.8', 'Accepted, because d2 is larger', 'Undefined'], 1,
       'Compute d1 ÷ d2.', 'The best and second best are almost equally good, so the match is ambiguous and is thrown away. Repeated patterns such as windows on a building cause this.')
K.quiz('h', 'Why does HOG usually use unsigned directions (0° to 180°)?', [
    'To save one bit of memory',
    'So a dark object on a light background and a light object on a dark background give the same shape description',
    'Because angles above 180° do not exist',
    'Because SVMs cannot handle negative numbers'], 1,
    'Think of clothing colours.', 'Unsigned angles merge θ and θ + 180°, which ignores which side of the edge is brighter. Dalal and Triggs found this works better for people.')
K.quiz('h', 'A HOG person detector misses people who are sitting down. The best explanation is', [
    'The image is in colour',
    'HOG captures the edge layout of the training pose, and sitting changes that layout',
    'Sitting people have no gradients',
    'The SVM is too fast'], 1,
    'HOG is a template of edge directions.', 'HOG is tolerant to small shifts but not to big pose changes. The notes list deformable and posed objects as a HOG weakness.')
K.quiz('x', 'Which statement about edges is correct?', [
    'Every edge is an object boundary',
    'An edge marks a change in intensity, which can come from a boundary, a surface fold, a material change, a shadow or lighting',
    'Edges only appear in colour images',
    'Edges cannot be detected with derivatives'], 1,
    'Marr calls the primal sketch evidence.', 'Edges are evidence of structure. Later stages decide whether an edge is a boundary or just a shadow.')
K.quiz('x', 'A blob of radius 10 pixels gives the strongest scale normalised Laplacian response near which σ?', ['1.0', '5.0', '7.07', '14.1'], 2,
       'σ = r ÷ √2.', '10 ÷ 1.414 ≈ 7.07. Doubling the radius doubles the best σ, which is how SIFT estimates size.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'With the kernel [−1, 0, 1], what is G<sub>x</sub> at a pixel whose left neighbour is 60 and right neighbour is 180?', '120', 'Right minus left.',
       ['The kernel takes −1 × left + 0 × centre + 1 × right.', eq('G<sub>x</sub> = 180 − 60 = 120'), 'Positive means brightness increases to the right.'], check=120)
K.calc('e', 'G<sub>x</sub> = 3 and G<sub>y</sub> = 4. What is the gradient magnitude?', '5', 'Pythagoras.',
       ['|∇I| = √(G<sub>x</sub>² + G<sub>y</sub>²).', eq('√(9 + 16) = √25 = 5'), 'This is the same 3, 4, 5 triangle from school.'], check=5)
K.calc('e', 'How many degrees does each bin cover in a 9 bin unsigned HOG histogram?', '20', 'Unsigned covers 180°.',
       ['Unsigned angles run from 0° to 180°.', eq('180 ÷ 9 = 20°'), 'The bin centres are 10°, 30°, 50° and so on up to 170°.'], check=20)
K.calc('m', 'G<sub>x</sub> = 1 and G<sub>y</sub> = 1. What is the gradient direction in degrees?', '45', 'atan2(1, 1).',
       ['θ = atan2(G<sub>y</sub>, G<sub>x</sub>) = atan2(1, 1).', 'tan θ = 1 ÷ 1 = 1.', eq('θ = 45°'), 'The edge runs diagonally and the arrow points down and to the right in image coordinates.'], check=45)
K.calc('m', 'Apply the Sobel K<sub>x</sub> kernel to the neighbourhood [[10, 10, 50], [10, 10, 50], [10, 10, 50]]. What is G<sub>x</sub>?', '160', 'K<sub>x</sub> = [[−1, 0, 1], [−2, 0, 2], [−1, 0, 1]].',
       ['Row 1: −10 + 0 + 50 = 40.', 'Row 2: −20 + 0 + 100 = 80.', 'Row 3: −10 + 0 + 50 = 40.', eq('G<sub>x</sub> = 40 + 80 + 40 = 160')], check=160)
K.calc('m', 'Apply Sobel K<sub>x</sub> and K<sub>y</sub> to [[0, 0, 0], [0, 100, 100], [0, 100, 100]]. What is the gradient magnitude? Give two decimals.', '424.26', 'Both directions change here, it is a corner.',
       ['G<sub>x</sub>: (−1)(0) + (1)(0) + (−2)(0) + (2)(100) + (−1)(0) + (1)(100) = 300.', 'G<sub>y</sub>: (−1)(0) + (−2)(0) + (−1)(0) + (1)(0) + (2)(100) + (1)(100) = 300.', eq('√(300² + 300²) = 300√2 ≈ 424.26'), 'Equal G<sub>x</sub> and G<sub>y</sub> give a 45° direction, pointing into the bright corner.'], check=424.26, tol=0.01)
K.calc('m', 'How many numbers are in a SIFT descriptor?', '128', '4 × 4 cells, 8 bins each.',
       ['The patch around a keypoint is split into a 4 × 4 grid, so 16 cells.', 'Each cell has an 8 bin histogram of directions.', eq('16 × 8 = 128')], check=128)
K.calc('h', 'A pixel has gradient magnitude 10 and unsigned direction 25°. With 9 bins of 20° (centres 10°, 30°, ...), how much of its vote goes to the bin centred at 30°?', '7.5', 'Find how far 25° is from 10° as a fraction of 20°.',
       ['25° lies between the centres 10° and 30°.', 'Distance from the lower centre: 25 − 10 = 15, which is 15 ÷ 20 = 0.75 of a bin.', eq('vote to 30° = 0.75 × 10 = 7.5'), 'The other 2.5 goes to the bin centred at 10°.'], check=7.5)
K.calc('h', 'How long is the HOG descriptor for a 64 × 128 window with 8 × 8 cells, 2 × 2 cell blocks moved one cell at a time, and 9 bins?', '3780', 'Count cells, then blocks.',
       ['Cells: 64 ÷ 8 = 8 across and 128 ÷ 8 = 16 down.', 'Blocks of 2 × 2 that move one cell: (8 − 1) × (16 − 1) = 7 × 15 = 105.', 'Each block holds 4 cells × 9 bins = 36 numbers.', eq('105 × 36 = 3,780')], check=105 * 36)
K.calc('h', 'A keypoint\'s nearest descriptor is at distance 0.30 and the second nearest at 0.45. What is the ratio d1 ÷ d2? Give three decimals.', '0.667', 'Divide the nearest by the second nearest.',
       ['Ratio = 0.30 ÷ 0.45.', eq('= 0.667'), '0.667 is below 0.8, so the match is accepted.'], check=0.667, tol=0.0006)
K.calc('x', 'A gradient points at 250° (signed). What is its unsigned angle used by HOG?', '70', 'Unsigned angles are taken modulo 180°.',
       ['Unsigned means θ and θ + 180° are the same.', eq('250 − 180 = 70°'), 'So the pixel votes near the bins centred at 70° (bin 3, centre 70°).'], check=70)
K.calc('x', 'A bright blob has radius 8 pixels. At which σ does the scale normalised Laplacian of Gaussian peak? Give two decimals.', '5.66', 'σ = r ÷ √2.',
       ['For a disc, the best scale is σ = r ÷ √2.', eq('σ = 8 ÷ 1.4142 ≈ 5.66'), 'If the image is zoomed 2 times, r becomes 16 and σ becomes 11.31, so the detected size scales with the zoom.'], check=8 / 2 ** 0.5, tol=0.006)

# ---------------------------------------------------------------- assignments
K.assign('sobel', 'e', 'Sobel gradient at a pixel',
         '<p>Write <code>gradient_at(img, r, c)</code> that returns <code>[gx, gy]</code>, the Sobel gradients at row <code>r</code> and column <code>c</code>. You can assume the pixel is not on the border.</p>',
         '''
KX = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
KY = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]


def gradient_at(img, r, c):
    # your code here
    pass
''', [('gradient_at([[10,10,50],[10,10,50],[10,10,50]], 1, 1)', [160, 0]), ('gradient_at([[0,0,0],[0,100,100],[0,100,100]], 1, 1)', [300, 300]),
      ('gradient_at([[1,2,3],[4,5,6],[7,8,9]], 1, 1)', [8, 24])],
         '''
KX = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
KY = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]


def gradient_at(img, r, c):
    gx = gy = 0
    for i in range(3):
        for j in range(3):
            v = img[r + i - 1][c + j - 1]
            gx += KX[i][j] * v
            gy += KY[i][j] * v
    return [gx, gy]
''', 'Loop over i and j from 0 to 2. The pixel under kernel position (i, j) is img[r + i − 1][c + j − 1].',
         '<p>This is exactly what <code>cv2.Sobel</code> does at every pixel. For [[1, 2, 3], [4, 5, 6], [7, 8, 9]] the brightness grows by 1 per column and 3 per row, and Sobel scales each by 8, giving 8 and 24.</p>')
K.assign('magang', 'e', 'Magnitude and direction',
         '<p>Write <code>magnitude_angle(gx, gy)</code> that returns <code>[magnitude, angle]</code>. Round the magnitude to 2 decimals. Give the angle in degrees from 0 up to but not including 360, rounded to 1 decimal.</p>',
         '''
from math import atan2, degrees, hypot


def magnitude_angle(gx, gy):
    # your code here
    pass
''', [('magnitude_angle(3, 4)', [5.0, 53.1]), ('magnitude_angle(0, -5)', [5.0, 270.0]), ('magnitude_angle(-1, 0)', [1.0, 180.0]), ('magnitude_angle(160, 0)', [160.0, 0.0])],
         '''
from math import atan2, degrees, hypot


def magnitude_angle(gx, gy):
    return [round(hypot(gx, gy), 2), round(degrees(atan2(gy, gx)) % 360, 1)]
''', 'atan2 returns −180° to 180°. Taking the result modulo 360 moves negative angles into 0 to 360.',
         '<p><code>atan2</code> is better than <code>atan(gy / gx)</code> because it knows which quadrant the vector is in and never divides by zero.</p>')
K.assign('hogcell', 'm', 'Build one HOG cell',
         '<p>Write <code>hog_cell(mags, angs, bins=9)</code>. <code>mags</code> and <code>angs</code> are lists with one magnitude and one angle in degrees per pixel. Use unsigned angles (take each angle modulo 180). Bin centres are at (k + 0.5) × 180 ÷ bins. Split each vote between the two nearest centres in proportion to closeness, wrapping round from the last bin to the first. Return the histogram with each value rounded to 2 decimals.</p>',
         '''
def hog_cell(mags, angs, bins=9):
    hist = [0.0] * bins
    # your code here
    return hist
''', [('hog_cell([10], [25])', [2.5, 7.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]), ('hog_cell([10, 4], [90, 190])', [4.0, 0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0]),
      ('hog_cell([8], [175])', [2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0])],
         '''
def hog_cell(mags, angs, bins=9):
    hist = [0.0] * bins
    width = 180 / bins
    for m, a in zip(mags, angs):
        pos = (a % 180) / width - 0.5
        left = int(pos // 1)
        t = pos - left
        hist[left % bins] += m * (1 - t)
        hist[(left + 1) % bins] += m * t
    return [round(h, 2) for h in hist]
''', 'Work out pos = angle ÷ width − 0.5. Its whole part is the lower bin and its fraction is the share for the upper bin.',
         '<p>175° sits between the last centre (170°) and the first centre wrapped round (190°, which is 10°). Wrapping keeps nearly horizontal edges from being split across the two ends of the histogram unfairly.</p>')
K.assign('ratio', 'h', 'Match with the ratio test',
         '<p>Write <code>ratio_match(q, cands, ratio=0.8)</code>. <code>q</code> is a descriptor and <code>cands</code> a list of descriptors. Return the index of the nearest candidate (Euclidean distance) if its distance is less than <code>ratio</code> times the second nearest distance, otherwise return <code>-1</code>. With a single candidate, return its index.</p>',
         '''
from math import sqrt


def ratio_match(q, cands, ratio=0.8):
    # your code here
    pass
''', [('ratio_match([1, 0], [[1, 0.1], [0, 1], [5, 5]])', 0), ('ratio_match([1, 1], [[1, 1.5], [1.5, 1]])', -1), ('ratio_match([0, 0], [[3, 4]])', 0)],
         '''
from math import sqrt


def ratio_match(q, cands, ratio=0.8):
    d = sorted((sqrt(sum((a - b) ** 2 for a, b in zip(q, c))), i) for i, c in enumerate(cands))
    if len(d) == 1:
        return d[0][1]
    return d[0][1] if d[0][0] < ratio * d[1][0] else -1
''', 'Compute every distance with its index, sort, then compare the first two.',
         '<p>The second test has two candidates at exactly the same distance, so the match is ambiguous and rejected. Lowe found that a ratio of 0.8 removes about 90% of false matches while losing less than 5% of correct ones.</p>')

K.must("Marr's four stages", 'Input image, primal sketch (edges, blobs), 2½-D sketch (depth and orientation of visible surfaces), 3D model (full shape). 2½-D because it depends on the viewpoint.')
K.must('Good features', 'Distinctive, stable (repeatable) and invariant. Corners beat edges, edges beat flat regions. Detection finds points, description turns them into vectors.')
K.must('Gradients', 'Gx and Gy by differences or Sobel. Magnitude √(Gx² + Gy²), direction atan2(Gy, Gx), pointing across the edge from dark to bright.')
K.must('SIFT', 'DoG scale space for scale, dominant orientation for rotation, 4 × 4 × 8 = 128 descriptor, ratio test d1 ÷ d2 &lt; 0.8 for matching.')
K.must('HOG', 'Cells of 8 × 8, 9 unsigned bins, votes weighted by magnitude, 2 × 2 block normalisation, 3,780 numbers for 64 × 128. Good for upright people, weak on pose changes and occlusion.')
K.must('Why classical features matter', 'Efficiency, interpretability, domain knowledge and support for deep pipelines, not because CNNs overfit.')

T = K.topic(
    slug='marr-edges-features', topic='features', step=(1, 'Seeing like a machine', 'cv-foundations', 'What vision is, why it is hard for machines, and the first hand made features.', 'Start here'),
    title="Marr's theory, edges and hand made features", short='Edges and features', badge='1.2', minutes=45,
    lead="How vision moves from pixels to edges to shape, and the classic features built on image gradients: Sobel, SIFT and HOG, with the exact numbers examiners ask for.",
    desc="Marr's 2½-D sketch, image gradients and Sobel, SIFT keypoints and the ratio test, and HOG descriptors, explained with animations and worked problems.",
    summary="Marr's stages and the 2½-D sketch, what makes a good feature, image gradients and Sobel, SIFT keypoints and HOG descriptors.",
    keywords=['Marr', '2.5D sketch', 'primal sketch', 'feature', 'gradient', 'Sobel', 'SIFT', 'difference of Gaussians', 'ratio test', 'HOG', 'Dalal Triggs', 'keypoint'],
    recap='<p>Vision builds up in stages, and the first useful stage is where brightness changes. Gradients measure that change. SIFT turns gradients around a few special points into 128 numbers that survive zoom and rotation. HOG turns gradients over a whole window into a long shape description for detection.</p>')
