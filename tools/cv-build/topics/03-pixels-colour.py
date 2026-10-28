# Chapter 3: images as discrete signals, colour models, compression, the JPEG pipeline and video frame types.
# Sources: lecture 2 (image representation, colour models, JPEG, lossy and lossless, I, P and B frames, surveillance)
# and the colour and JPEG recap at the start of lectures 3 and 4.
# Facts checked: BT.601 grey weights (used by OpenCV cvtColor), JFIF YCbCr equations, the JPEG Annex K luminance table
# and the IJG quality scaling rule.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('colours', r'''
# Convert one RGB colour into the other models from the lecture
r = int(input("Red 0-255: "))
g = int(input("Green 0-255: "))
b = int(input("Blue 0-255: "))

grey = 0.299 * r + 0.587 * g + 0.114 * b          # how bright it looks to the eye
print("grey:", round(grey))

R, G, B = r / 255, g / 255, b / 255                # scale to 0..1
k = 1 - max(R, G, B)                              # black ink
if k < 1:
    c, m, y = [(1 - v - k) / (1 - k) for v in (R, G, B)]
else:
    c = m = y = 0.0
print("CMYK:", round(c, 3), round(m, 3), round(y, 3), round(k, 3))

mx, mn = max(R, G, B), min(R, G, B)
light = (mx + mn) / 2
sat = 0 if mx == mn else (mx - mn) / (1 - abs(2 * light - 1))
print("lightness:", round(light, 3), " saturation:", round(sat, 3))

cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
print("YCbCr:", round(grey, 1), round(cb, 1), round(cr, 1))
print("as BGR the same numbers mean:", (b, g, r))
''', stdin='255\n128\n0\n')

K.code('dct1d', r'''
# JPEG works on 8 x 8 blocks. The same idea in one dimension: 8 pixels -> 8 frequencies.
from math import cos, pi, sqrt

pixels = [52, 55, 61, 66, 70, 61, 64, 73]
q = int(input("Quantisation step (1 = no loss): "))
shifted = [p - 128 for p in pixels]                    # JPEG first centres values on 0
basis = [[cos((2 * x + 1) * u * pi / 16) for x in range(8)] for u in range(8)]
scale = [1 / (2 * sqrt(2))] + [0.5] * 7                # C(u) / 2

F = []
for u in range(8):                                      # forward DCT
    F.append(scale[u] * sum(map(lambda a, b: a * b, shifted, basis[u])))
print("frequencies:", [round(v, 1) for v in F])

Fq = [round(v / q) for v in F]                          # the lossy step
print("quantised:  ", Fq, " zeros:", Fq.count(0))

back = []
for x in range(8):                                      # inverse DCT
    s = sum(scale[u] * Fq[u] * q * basis[u][x] for u in range(8))
    back.append(round(s + 128))
print("decoded:    ", back)
print("errors:     ", [a - b for a, b in zip(pixels, back)])
''', stdin='10\n')

K.code('gop', r'''
# Average frame size and B frame delay for a group of pictures
pattern = input("Pattern of I, P and B frames: ").strip().upper()
size = {"I": 80, "P": 25, "B": 10}                      # kilobytes, typical proportions
fps = 30

total = sum(size[t] for t in pattern)
print("frames:", len(pattern), " total:", total, "KB  average:", round(total / len(pattern), 2), "KB")
print("all I frames would be", len(pattern) * size["I"], "KB")

run = longest = 0
for t in pattern:
    run = run + 1 if t == "B" else 0
    longest = max(longest, run)
print("longest B run:", longest, "-> about", round(longest * 1000 / fps, 1), "ms of extra delay")
''', stdin='IBBPBBPBBPBB\n')

K.lesson('signal', 'An image is a discrete signal', f'''
<p>A digital image is a grid of samples of the light that reached the camera. Each sample is a pixel, and each pixel stores numbers. For an 8 bit grey image, 0 is black, 255 is white and everything in between is a shade of grey.</p>
{fxs(
    fx('Image as a function', '<i>I</i> : {0, …, <i>H</i> − 1} × {0, …, <i>W</i> − 1} → {0, …, 255}<sup><i>C</i></sup>', 'Each position (row, column) maps to <i>C</i> numbers.'),
    fx('Stored values', '<i>H</i> × <i>W</i> × <i>C</i>', 'For the lecture example 16 × 16 × 3 = 768.', key=True))}
<h3>Low level and high level vision</h3>
<p>The lecture separates two layers of work. <b>Low level vision</b> deals with the signal: brightness, contrast, colour, noise, edges, blur, sharpness, resolution. <b>High level vision</b> deals with meaning: classification, detection, scenes, activities, captions, answering questions. Information flows upwards: pixel changes give edges, edges give shapes, shapes give objects, and objects with their relationships give scenes. That is why low level choices such as compression and colour handling can change high level accuracy.</p>
<h3>Before an image reaches a model</h3>
<p>The lecture lists five things to check every time: channel order, pixel range, data type, normalisation and layout. A model trained on RGB values scaled to 0 to 1, laid out as channels first, will give nonsense if it receives BGR values from 0 to 255 laid out channels last.</p>
{fxs(
    fx('Scale to 0 to 1', "<i>x</i>′ = " + frac('<i>x</i>', '255'), 'Turns 8 bit integers into floats.'),
    fx('Standardise per channel', "<i>x</i>″ = " + frac("<i>x</i>′ − μ<sub><i>c</i></sub>", 'σ<sub><i>c</i></sub>'), 'μ and σ are the mean and standard deviation of channel <i>c</i> over the training data.'))}
{note('Compression and normalisation are different things. Compression makes files smaller for storage and transfer. Normalisation changes the scale of numbers so a model can learn. The notes list this as a common confusion.', 'warn')}
''', kw=['digital image', 'pixel', 'discrete signal', '0 to 255', 'H W C', 'low level vision', 'high level vision', 'normalisation', 'channel order'])

K.lesson('colour', 'Colour models: RGB, CMYK, HSL and YCbCr', f'''
<p>A computer does not know the word "orange". A colour model says which numbers describe a colour and how they combine.</p>
{table(['Model', 'Channels', 'How it works', 'Where it is used'], [
    ['RGB', 'Red, green, blue', 'Additive: start from black and add light. All three at full give white.', 'Screens, cameras, most image files'],
    ['CMYK', 'Cyan, magenta, yellow, key (black)', 'Subtractive: start from white paper and add ink that absorbs light.', 'Printing'],
    ['HSL', 'Hue, saturation, lightness', 'Separates which colour, how pure, and how light.', 'Photo editing, colour based filtering'],
    ['YCbCr', 'Luma Y, blue difference Cb, red difference Cr', 'Separates brightness from colour.', 'JPEG and video codecs'],
    ['BGR', 'Blue, green, red', 'Same as RGB with the order reversed.', 'OpenCV in memory']])}
{viz('colour')}
{fxs(
    fx('Grey from RGB (BT.601)', '<i>Y</i> = 0.299 <i>R</i> + 0.587 <i>G</i> + 0.114 <i>B</i>', 'Green gets the biggest weight because the eye is most sensitive to it. OpenCV uses these weights.', key=True),
    fx('RGB to CMYK', '<i>K</i> = 1 − max(<i>R</i>′, <i>G</i>′, <i>B</i>′), &nbsp; <i>C</i> = ' + frac('1 − <i>R</i>′ − <i>K</i>', '1 − <i>K</i>'), '<i>R</i>′ = <i>R</i> ÷ 255. <i>M</i> and <i>Y</i> use <i>G</i>′ and <i>B</i>′ the same way.'),
    fx('HSL lightness and saturation', '<i>L</i> = ' + frac('max + min', '2') + ', &nbsp; <i>S</i> = ' + frac('max − min', '1 − |2<i>L</i> − 1|'), 'max and min of <i>R</i>′, <i>G</i>′, <i>B</i>′. Hue is the angle on the colour wheel.'),
    fx('Colour difference channels (JPEG)', '<i>Cb</i> = 128 − 0.1687 <i>R</i> − 0.3313 <i>G</i> + 0.5 <i>B</i><br><i>Cr</i> = 128 + 0.5 <i>R</i> − 0.4187 <i>G</i> − 0.0813 <i>B</i>', 'A pure grey has <i>Cb</i> = <i>Cr</i> = 128.'))}
{code('colours')}
{scene('picking ripe tomatoes on a conveyor belt', '<p>A sorting machine must separate red tomatoes from green ones under factory lights that change through the day. In RGB, a darker red tomato has smaller numbers in every channel, so a fixed threshold on R fails when the lights dim. In HSL the hue of a red tomato stays near 0° whether the light is bright or dim. Thresholding on hue and ignoring lightness makes the sorter far more robust. Choosing the right colour model is often the cheapest fix in a real project.</p>')}
''', kw=['RGB', 'additive', 'CMYK', 'subtractive', 'HSL', 'hue', 'saturation', 'lightness', 'YCbCr', 'luma', 'chroma', 'BGR', 'grey conversion'])

K.lesson('compression', 'Why and how images are compressed', f'''
<p>Raw images and video are huge, as the first chapter showed. Compression reduces storage, bandwidth, server cost and transfer time, and makes streaming and mobile apps possible. It works by removing <b>redundancy</b>: neighbouring pixels are similar, colour channels are correlated, smooth regions repeat the same values, and the eye does not notice some details.</p>
{fxs(
    fx('Compression ratio', 'ratio = ' + frac('original size', 'compressed size'), 'A ratio of 15 means the file is 15 times smaller.', key=True),
    fx('Bits per pixel', 'bpp = ' + frac('8 × file bytes', '<i>H</i> × <i>W</i>'), 'Raw colour is 24 bpp. A good JPEG photo is often 1 to 2 bpp.'))}
{table(['', 'Lossless (PNG)', 'Lossy (JPEG)'], [
    ['Recovery', 'Exact, every pixel comes back', 'Approximate, some information is gone for ever'],
    ['File size', 'Larger', 'Much smaller'],
    ['Best for', 'Text, diagrams, screenshots, transparency, medical data', 'Photographs'],
    ['Repeated saving', 'No change', 'Quality can drop each time'],
    ['Typical damage', 'None', 'Blocks, blur, ringing near edges, lost fine texture']])}
<ul>
<li><b>Spatial redundancy</b> is inside one picture: a smooth sky, a repeated texture.</li>
<li><b>Temporal redundancy</b> is between frames of a video: a still background, a slowly moving person.</li>
</ul>
{note('For medical, legal and industrial images, use lossless or very light compression. The fine edges that JPEG throws away can be the tumour boundary, the digit on a number plate or the crack in a weld.', 'warn')}
''', kw=['compression', 'redundancy', 'lossy', 'lossless', 'PNG', 'JPEG', 'compression ratio', 'bits per pixel', 'spatial redundancy', 'temporal redundancy'])

K.lesson('jpeg', 'The JPEG pipeline and the DCT', f'''
<p>The lectures describe JPEG in five steps. Decompression runs them backwards.</p>
<ol>
<li><b>Colour transform.</b> RGB becomes YCbCr, separating brightness (Y) from colour (Cb, Cr).</li>
<li><b>Downsampling.</b> Cb and Cr are stored at lower resolution, because the eye is far more sensitive to brightness than to colour. In the common 4:2:0 scheme each colour channel keeps one value per 2 × 2 pixels.</li>
<li><b>Discrete cosine transform (DCT).</b> Each 8 × 8 block is written as a mix of 64 cosine patterns, from flat (low frequency) to fine checkerboards (high frequency).</li>
<li><b>Quantisation.</b> Each coefficient is divided by a number from a table and rounded. Low frequencies get small divisors and keep their detail. High frequencies get large divisors and often become zero. This is the only step that loses information.</li>
<li><b>Encoding.</b> The coefficients are read in a zig zag order so the zeros bunch together, then run length and Huffman coding store them compactly.</li>
</ol>
{fxs(
    fx('2D DCT of an 8 × 8 block', '<i>F</i>(<i>u</i>, <i>v</i>) = ¼ <i>C</i>(<i>u</i>) <i>C</i>(<i>v</i>) Σ<sub><i>x</i>=0</sub><sup>7</sup> Σ<sub><i>y</i>=0</sub><sup>7</sup> <i>f</i>(<i>x</i>, <i>y</i>) cos ' + frac('(2<i>x</i> + 1)<i>u</i>π', '16') + ' cos ' + frac('(2<i>y</i> + 1)<i>v</i>π', '16'), '<i>C</i>(0) = 1 ÷ √2 and <i>C</i>(<i>k</i>) = 1 otherwise. <i>f</i> is the pixel value minus 128.', key=True),
    fx('Quantisation', '<i>F<sub>q</sub></i>(<i>u</i>, <i>v</i>) = round' + '(' + frac('<i>F</i>(<i>u</i>, <i>v</i>)', '<i>Q</i>(<i>u</i>, <i>v</i>)') + ')', 'Decoding multiplies back by <i>Q</i>. The rounding error is the loss.', key=True),
    fx('The DC coefficient', '<i>F</i>(0, 0) = ' + frac('1', '8') + ' Σ Σ <i>f</i>(<i>x</i>, <i>y</i>) = 8 × mean', 'The top left coefficient is just 8 times the block average after subtracting 128.'),
    fx('Chroma subsampling 4:2:0', 'data kept = ' + frac('1 + ¼ + ¼', '3') + ' = ½', 'Y keeps every pixel, Cb and Cr keep a quarter each.'))}
{viz('dct')}
{steps('Worked example: a flat block of value 140', [
    'Subtract 128: every value becomes 12.',
    'A flat block has no variation, so every coefficient except the DC one is 0.',
    'DC = 8 × mean = 8 × 12 = 96.',
    'The standard table has Q(0, 0) = 16, so the stored value is round(96 ÷ 16) = 6. One small number replaces 64 pixels.'])}
{code('dct1d')}
{deep('why cosines and not some other pattern', '<p>For natural images, neighbouring pixels are strongly correlated. For such signals the DCT comes close to the Karhunen Loeve transform, the transform that packs the most energy into the fewest coefficients. Cosines also avoid the jumps at the block edges that a plain Fourier transform would create, because the DCT implicitly mirrors the block. The price of working on separate 8 × 8 blocks is the blocking artefact at high compression, which is one reason newer formats use larger and overlapping transforms.</p>')}
''', kw=['JPEG', 'YCbCr', 'chroma subsampling', '4:2:0', 'DCT', 'discrete cosine transform', 'quantisation', 'quantization table', 'DC coefficient', 'zig zag', 'Huffman', 'ringing', 'blocking'])

K.lesson('video', 'Video compression: I, P and B frames', f'''
<p>A video is a sequence of frames, and neighbouring frames are usually almost the same. Codecs (H.264, H.265, AV1 and earlier H.261 to H.263) store some full frames and predict the rest.</p>
{table(['Frame', 'How it is coded', 'Strength', 'Weakness'], [
    ['I (intra)', 'On its own, like a JPEG', 'Can be decoded alone, good for seeking and recovering from errors', 'Largest'],
    ['P (predicted)', 'From an earlier frame, using motion vectors and the leftover difference', 'Much smaller than I', 'Errors carry forward until the next I frame'],
    ['B (bi predicted)', 'From an earlier and a later frame', 'Smallest', 'Needs a future frame, which adds delay and memory']])}
{viz('gop')}
{fx('Extra delay from B frames', 'delay ≈ ' + frac('longest run of B frames', 'fps') + ' seconds', 'Each B frame in a row makes the decoder wait one more frame time for its future reference.')}
<h3>Why not use only B frames</h3>
<p>Because a B frame needs the future, the encoder must look ahead and the decoder must buffer frames before it can show anything. That is fine for a film on a streaming service, where the whole file exists. It is not fine for a video call, a live broadcast, controlling a drone or a car's perception system, where every millisecond of delay matters. Live systems use I and P frames with few or no B frames.</p>
{code('gop')}
{scene('a city with a thousand surveillance cameras', '<p>Sending every frame from every camera to the cloud needs huge bandwidth and storage and raises privacy risks. The lecture suggests processing near the camera (edge processing): detect people, vehicles or unusual motion locally, send only the important frames or just the metadata, and compress empty scenes heavily. The risk is that aggressive compression can destroy evidence, such as the face of a fast moving person. So the compression level should depend on motion speed, event importance, the evidence quality the law needs, resolution, storage budget and real time limits.</p>')}
{ladder(
    '<p>A flip book where most pages are almost the same can be saved by drawing the first page fully and then only writing down what moved on each new page.</p>',
    '<p>P frames store motion vectors for blocks plus a residual image. The residual is compressed like a JPEG. B frames average a forward and a backward prediction, which handles objects that appear from behind something.</p>',
    '<p>The encoder balances rate and distortion. It picks motion vectors, block sizes and quantisation to minimise D + λR, where D is the distortion, R is the bit rate and λ sets the trade off. The GOP structure trades compression against random access, error resilience and latency.</p>',
    '<p>Learned video codecs replace hand designed motion estimation and transforms with neural networks trained end to end on the rate distortion objective. Research also studies compression for machines: codecs tuned so that a detector, not a human, gets the best accuracy per bit.</p>')}
''', kw=['video compression', 'codec', 'H.264', 'H.265', 'AV1', 'I-frame', 'P-frame', 'B-frame', 'GOP', 'motion vectors', 'latency', 'surveillance', 'edge processing'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'How many values does a 16 × 16 RGB image store?', ['256', '512', '768', '48'], 2, 'H × W × C.', '16 × 16 × 3 = 768, the example from the lecture.')
K.quiz('e', 'Which colour model is subtractive and used for printing?', ['RGB', 'CMYK', 'HSL', 'YCbCr'], 1, 'Ink absorbs light.', 'CMYK adds ink to white paper, and each ink subtracts some light. RGB adds light on a black screen.')
K.quiz('e', 'Which format is lossless?', ['JPEG', 'PNG', 'H.264 at normal settings', 'MP3'], 1, 'Every pixel comes back.', 'PNG stores the image exactly. JPEG and typical video codecs throw information away.')
K.quiz('m', 'An image loaded with OpenCV is shown with Matplotlib and the sky looks orange. Why?', [
    'The image is corrupted', 'OpenCV stores BGR and Matplotlib expects RGB, so red and blue are swapped', 'Matplotlib cannot show blue', 'The file is a PNG'], 1,
    'Look at the channel order.', 'Convert with cv2.cvtColor(img, cv2.COLOR_BGR2RGB) before showing or feeding the image to an RGB model.')
K.quiz('m', 'Why does JPEG shrink Cb and Cr but not Y?', [
    'Because Y is always zero', 'The eye is much more sensitive to brightness detail than to colour detail', 'Because colour cannot be compressed', 'To make the image grey'], 1,
    'Think about human vision.', 'Losing colour resolution is hard to see, losing brightness resolution is easy to see, so JPEG spends its bits on Y.')
K.quiz('m', 'Which JPEG step actually loses information?', ['Colour transform', 'DCT', 'Quantisation', 'Huffman coding'], 2,
    'Which step involves rounding?', 'The DCT and the colour transform can be inverted. Huffman coding is lossless. Rounding F ÷ Q throws away precision for ever. Downsampling also loses colour detail.')
K.quiz('m', 'A video call app should mostly use which frames?', ['Only B frames', 'I and P frames', 'Only I frames', 'B frames with long runs'], 1,
    'Live means no future frames.', 'P frames give good compression without waiting for the future. Occasional I frames allow recovery from lost packets.')
K.quiz('h', 'A JPEG of a page of small text looks fuzzy around the letters. What is the best fix?', [
    'Use a lower JPEG quality', 'Save it as PNG, because text has sharp edges whose high frequencies JPEG removes', 'Convert to CMYK', 'Add more B frames'], 1,
    'Sharp edges need high frequencies.', 'The ringing comes from quantising the high frequency coefficients that sharp edges need. Lossless PNG keeps them, and text pages compress well losslessly.')
K.quiz('h', 'Why is the DC coefficient of a block equal to 8 times its mean (after subtracting 128)?', [
    'Because the DC basis is a constant and the normalisation is ¼ × (1 ÷ √2)² = 1/8 of the sum',
    'Because JPEG multiplies everything by 8',
    'Because there are 8 bits per pixel',
    'It is a coincidence'], 0,
    'Set u = v = 0 in the formula.', 'With u = v = 0 both cosines are 1, so F(0, 0) = ¼ × (1 ÷ √2)(1 ÷ √2) × Σ f = Σ f ÷ 8. With 64 pixels that is 64 × mean ÷ 8 = 8 × mean.')
K.quiz('h', 'An AI system restores a blurry MRI scan. The restored image looks sharp and clean. What must happen before doctors use it?', [
    'Nothing, it looks better', 'Validation on a separate test set, against clinical benchmarks and by expert radiologists, checking that lesions and boundaries are preserved', 'Save it as JPEG', 'Convert it to colour'], 1,
    'Looking good is not the same as being right.', 'The lecture warns that restoration can invent plausible details. In medicine a hallucinated or erased lesion is dangerous, so restoration must be validated clinically, not just visually.')
K.quiz('x', 'In a GOP of IBBBP at 25 frames per second, roughly how much extra delay do the B frames cause?', ['0 ms', '40 ms', '120 ms', '1 second'], 2,
    'Three B frames in a row, each one frame time.', 'Each frame time is 1000 ÷ 25 = 40 ms, and three B frames in a row wait for the P frame, so about 3 × 40 = 120 ms.')
K.quiz('x', 'Which statement about the frequency domain is correct?', [
    'High frequencies are always noise and can always be removed',
    'Compression usually keeps low frequencies and reduces high ones, but fine edges in text, medical and legal images live in high frequencies and may matter a lot',
    'Low frequencies hold the edges',
    'The frequency domain has fewer numbers than the image'], 1,
    'The notes warn about this.', 'Low frequencies hold smooth structure. High frequencies hold edges and texture as well as noise. How much to remove depends on the application.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many values are stored for a 16 × 16 RGB image?', '768', 'H × W × C.',
       ['H = 16, W = 16, C = 3.', eq('16 × 16 × 3 = 768'), 'This is the example from the lecture.'], check=768)
K.calc('e', 'Convert pure red (255, 0, 0) to grey with Y = 0.299R + 0.587G + 0.114B, rounded to a whole number.', '76', 'Only the R term is non zero.',
       ['Y = 0.299 × 255 + 0.587 × 0 + 0.114 × 0.', eq('Y = 76.245'), 'Rounded: 76. Pure red looks quite dark in grey.'], check=76)
K.calc('m', 'Convert (100, 150, 200) to grey with the BT.601 weights. Give two decimals.', '140.75', 'Multiply each channel by its weight.',
       ['0.299 × 100 = 29.9.', '0.587 × 150 = 88.05.', '0.114 × 200 = 22.8.', eq('Y = 29.9 + 88.05 + 22.8 = 140.75')], check=140.75, tol=0.001)
K.calc('m', 'Convert (255, 128, 0) to CMYK. What is M? Give three decimals.', '0.498', 'First find K = 1 − max of the scaled values.',
       ['Scale: R′ = 1, G′ = 128 ÷ 255 ≈ 0.502, B′ = 0.', 'K = 1 − max(1, 0.502, 0) = 0.', eq('M = (1 − 0.502 − 0) ÷ (1 − 0) ≈ 0.498'), 'C = 0 and Y = 1, so this orange is made of yellow ink with about half strength magenta.'], check=1 - 128 / 255, tol=0.0006)
K.calc('m', 'What is the HSL lightness of (200, 100, 50)? Give two decimals.', '0.49', 'L = (max + min) ÷ 2 on the 0 to 1 scale.',
       ['Scale: 200 ÷ 255 ≈ 0.784 and 50 ÷ 255 ≈ 0.196.', eq('L = (0.784 + 0.196) ÷ 2 ≈ 0.490'), 'The colour is a mid lightness brown orange.'], check=0.49, tol=0.001)
K.calc('m', 'With 4:2:0 chroma subsampling, what fraction of the YCbCr data is kept? Give a decimal.', '0.5', 'Y is full size, each chroma channel is a quarter.',
       ['Full YCbCr has 3 planes of size 1.', 'After 4:2:0: 1 + 0.25 + 0.25 = 1.5 planes.', eq('1.5 ÷ 3 = 0.5'), 'Half the data is gone before the DCT even starts.'], check=0.5)
K.calc('h', 'An 8 × 8 block has every pixel equal to 140. What is the quantised DC coefficient if Q(0, 0) = 16?', '6', 'Subtract 128, then DC = 8 × mean.',
       ['After the level shift every value is 140 − 128 = 12.', 'DC = 8 × mean = 8 × 12 = 96.', eq('round(96 ÷ 16) = 6')], check=6)
K.calc('h', 'A 1920 × 1080 RGB photo (8 bits per value) is saved as a 400,000 byte JPEG. What is the compression ratio? Give three decimals.', '15.552', 'Raw size ÷ JPEG size.',
       ['Raw size: 1920 × 1080 × 3 = 6,220,800 bytes.', eq('6,220,800 ÷ 400,000 = 15.552'), 'The file is about 15.6 times smaller.'], check=15.552, tol=0.0005)
K.calc('h', 'For the same 400,000 byte JPEG of a 1920 × 1080 photo, how many bits per pixel does it use? Give two decimals.', '1.54', 'bpp = 8 × bytes ÷ pixels.',
       ['Bits: 400,000 × 8 = 3,200,000.', 'Pixels: 1920 × 1080 = 2,073,600.', eq('3,200,000 ÷ 2,073,600 ≈ 1.54 bpp'), 'Raw RGB is 24 bpp, so 24 ÷ 1.54 ≈ 15.6, matching the ratio.'], check=400000 * 8 / (1920 * 1080), tol=0.006)
K.calc('m', 'A GOP is IBBPBBPBB with I = 60 KB, P = 20 KB and B = 8 KB. What is the average frame size in KB? Give two decimals.', '16.44', 'Count each type first.',
       ['Counts: 1 I, 2 P and 6 B frames, 9 in total.', 'Total: 60 + 2 × 20 + 6 × 8 = 60 + 40 + 48 = 148 KB.', eq('148 ÷ 9 ≈ 16.44 KB'), 'All I frames would average 60 KB, about 3.6 times more.'], check=148 / 9, tol=0.006)
K.calc('x', 'A live stream at 30 frames per second uses runs of two B frames. About how many milliseconds of extra delay does that add? Give two decimals.', '66.67', 'Each B in a row adds one frame time.',
       ['One frame time is 1000 ÷ 30 ≈ 33.33 ms.', eq('2 × 33.33 ≈ 66.67 ms'), 'For a video call this is noticeable on top of network delay, which is why calls avoid B frames.'], check=2000 / 30, tol=0.006)
K.calc('x', 'The IJG library scales the JPEG table by 200 − 2q percent for quality q ≥ 50, with Q′ = floor((Q × scale + 50) ÷ 100). What is the DC divisor Q′(0, 0) at quality 75 if Q(0, 0) = 16?', '8', 'Work out the scale first.',
       ['scale = 200 − 2 × 75 = 50.', 'Q′ = floor((16 × 50 + 50) ÷ 100) = floor(850 ÷ 100).', eq('floor(8.5) = 8'), 'Higher quality means smaller divisors, so more detail survives rounding.'], check=8)

# ---------------------------------------------------------------- assignments
K.assign('grey', 'e', 'RGB to grey',
         '<p>Write <code>rgb_to_gray(r, g, b)</code> that returns the BT.601 grey value rounded to the nearest whole number.</p>',
         '''
def rgb_to_gray(r, g, b):
    # your code here
    pass
''', [('rgb_to_gray(255, 0, 0)', 76), ('rgb_to_gray(100, 150, 200)', 141), ('rgb_to_gray(255, 255, 255)', 255), ('rgb_to_gray(0, 255, 0)', 150)],
         '''
def rgb_to_gray(r, g, b):
    return round(0.299 * r + 0.587 * g + 0.114 * b)
''', 'Y = 0.299 R + 0.587 G + 0.114 B.', '<p>The weights add up to 1, so white stays 255 and black stays 0. Pure green is twice as bright as pure red in grey, matching how we see it.</p>')
K.assign('cmyk', 'm', 'RGB to CMYK',
         '<p>Write <code>rgb_to_cmyk(r, g, b)</code> that returns <code>[c, m, y, k]</code>, each rounded to 3 decimals. For pure black return <code>[0.0, 0.0, 0.0, 1.0]</code>.</p>',
         '''
def rgb_to_cmyk(r, g, b):
    # your code here
    pass
''', [('rgb_to_cmyk(255, 128, 0)', [0.0, 0.498, 1.0, 0.0]), ('rgb_to_cmyk(0, 0, 0)', [0.0, 0.0, 0.0, 1.0]), ('rgb_to_cmyk(51, 102, 153)', [0.667, 0.333, 0.0, 0.4]), ('rgb_to_cmyk(255, 255, 255)', [0.0, 0.0, 0.0, 0.0])],
         '''
def rgb_to_cmyk(r, g, b):
    R, G, B = r / 255, g / 255, b / 255
    k = 1 - max(R, G, B)
    if k == 1:
        return [0.0, 0.0, 0.0, 1.0]
    return [round((1 - v - k) / (1 - k), 3) for v in (R, G, B)] + [round(k, 3)]
''', 'Scale to 0 to 1, compute K, then C, M and Y with (1 − v − K) ÷ (1 − K). Handle K = 1 first to avoid dividing by zero.',
         '<p>Black ink (K) replaces equal amounts of C, M and Y. This saves coloured ink and gives a deeper black on paper.</p>')
K.assign('quant', 'm', 'Quantise a block of coefficients',
         '<p>Write <code>quantise(F, Q)</code> that divides each coefficient in the 2D list <code>F</code> by the matching entry of <code>Q</code> and rounds with Python\'s <code>round</code>. Then write <code>zeros(block)</code> that counts the zero entries.</p>',
         '''
def quantise(F, Q):
    # your code here
    pass


def zeros(block):
    # your code here
    pass
''', [('quantise([[96, -30], [12, 3]], [[16, 11], [12, 12]])', [[6, -3], [1, 0]]), ('zeros(quantise([[96, -30], [12, 3]], [[16, 11], [12, 12]]))', 1),
      ('zeros(quantise([[48, 6, 2], [4, 1, 0], [1, 0, 0]], [[16, 11, 10], [12, 12, 14], [14, 13, 16]]))', 7)],
         '''
def quantise(F, Q):
    return [[round(f / q) for f, q in zip(fr, qr)] for fr, qr in zip(F, Q)]


def zeros(block):
    return sum(row.count(0) for row in block)
''', 'Zip the rows of F and Q together, then zip the values inside each pair of rows.',
         '<p>In the third test only 2 of 9 values survive. Real JPEG blocks of smooth areas often keep fewer than 10 of 64 coefficients, and the long runs of zeros are what make the file small.</p>')
K.assign('subsample', 'h', 'Bytes after chroma subsampling',
         '<p>Write <code>ycbcr_bytes(h, w, scheme)</code> for an 8 bit image of height <code>h</code> and width <code>w</code>. <code>scheme</code> is <code>"4:4:4"</code> (no subsampling), <code>"4:2:2"</code> (each chroma channel keeps half the samples) or <code>"4:2:0"</code> (each chroma channel keeps a quarter). Return the total bytes as a whole number.</p>',
         '''
def ycbcr_bytes(h, w, scheme):
    # your code here
    pass
''', [('ycbcr_bytes(1080, 1920, "4:4:4")', 6220800), ('ycbcr_bytes(1080, 1920, "4:2:0")', 3110400), ('ycbcr_bytes(1080, 1920, "4:2:2")', 4147200), ('ycbcr_bytes(2, 2, "4:2:0")', 6)],
         '''
def ycbcr_bytes(h, w, scheme):
    share = {"4:4:4": 1, "4:2:2": 0.5, "4:2:0": 0.25}[scheme]
    return int(h * w * (1 + 2 * share))
''', 'Y always has h × w bytes. Add two chroma channels, each h × w times its share.',
         '<p>A 2 × 2 block in 4:2:0 stores 4 Y values, 1 Cb and 1 Cr, so 6 bytes instead of 12. This is why almost every camera and streaming service uses 4:2:0.</p>')

K.must('Image as numbers', 'H × W × C values from 0 to 255. Check channel order, range, type, normalisation and layout before a model sees an image.')
K.must('Colour models', 'RGB adds light, CMYK adds ink, HSL separates hue from lightness, YCbCr separates brightness from colour. OpenCV uses BGR. Grey = 0.299R + 0.587G + 0.114B.')
K.must('Lossy and lossless', 'PNG keeps every pixel, JPEG throws away detail the eye misses. Use lossless for text, medical and legal images.')
K.must('JPEG in five steps', 'YCbCr, chroma downsampling, 8 × 8 DCT, quantisation (the lossy step), zig zag plus Huffman coding. DC = 8 × mean.')
K.must('I, P and B frames', 'I stands alone, P predicts from the past, B from past and future. B is smallest but adds delay, so live systems avoid it.')
K.must('Compression and evidence', 'Edge processing and content aware compression save bandwidth, but heavy compression can erase important detail.')

T = K.topic(
    slug='pixels-colour-compression', topic='pixels-colour', step=(2, 'Images as numbers', 'cv-image-basics', 'How pictures are stored, coloured, compressed, measured and cleaned before any recognition happens.', 'School and college'),
    title='Pixels, colour models and compression', short='Pixels, colour and compression', badge='2.1', minutes=45,
    lead='How an image is stored as numbers, how RGB, CMYK, HSL and YCbCr describe colour, how JPEG uses the DCT to shrink photos, and why video uses I, P and B frames.',
    desc='Images as discrete signals, colour models and conversions, lossy and lossless compression, the JPEG pipeline with the DCT and quantisation, and I, P and B frames in video.',
    summary='Images as discrete signals, RGB, CMYK, HSL, YCbCr and BGR, lossy and lossless compression, JPEG and the DCT, and I, P and B video frames.',
    keywords=['pixel', 'RGB', 'CMYK', 'HSL', 'YCbCr', 'BGR', 'compression', 'JPEG', 'DCT', 'quantisation', 'PNG', 'lossy', 'lossless', 'I-frame', 'P-frame', 'B-frame', 'video codec'],
    recap='<p>Every later chapter assumes you know what the numbers in an image mean. Colour models change how those numbers are grouped, and compression decides which of them survive. Remember that JPEG loses information only at quantisation, and that B frames trade delay for size.</p>')
