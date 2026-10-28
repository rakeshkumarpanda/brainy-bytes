# Chapter 4: histograms, brightness, contrast, dynamic range and point operations (negative, linear stretch, log,
# gamma, grey level slicing) and histogram equalisation. Source: lectures 3 and 4, parts II and III.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('histogram', r'''
# Histogram, brightness and contrast of a tiny 4 x 4 grey image
img = [
    [ 80,  80,  80,  80],
    [100, 100, 100, 100],
    [120, 120, 120, 120],
    [140, 140, 140, 140],
]
pixels = [v for row in img for v in row]      # flatten the rows
n = len(pixels)

hist = {}
for v in pixels:                               # h(i): how many pixels have value i
    hist[v] = hist.get(v, 0) + 1
print("histogram:", hist)

brightness = sum(pixels) / n                   # B(I): the mean
var = sum((v - brightness) ** 2 for v in pixels) / n
print("brightness:", brightness)
print("contrast (standard deviation):", round(var ** 0.5, 2))
print("levels used:", len(hist), "of 256")
''')

K.code('equalise', r'''
# Histogram equalisation, exactly as in the lecture
img = [[80, 80, 80, 80], [100, 100, 100, 100], [120, 120, 120, 120], [140, 140, 140, 140]]
pixels = [v for row in img for v in row]
n = len(pixels)

levels = sorted(set(pixels))
cdf, running = {}, 0
for r in levels:
    running += pixels.count(r) / n             # add this level's probability
    cdf[r] = running
cmin = cdf[levels[0]]

mapping = {r: round((cdf[r] - cmin) / (1 - cmin) * 255) for r in levels}
print("CDF:", cdf)
print("mapping:", mapping)
out = [[mapping[v] for v in row] for row in img]
for row in out:
    print(row)
''')

K.code('pointops', r'''
# Point operations on one row of pixels
from math import log

row = [0, 10, 40, 90, 160, 220, 255]
print("negative:", [255 - v for v in row])

c = 255 / log(256)                              # so that 255 maps to 255
print("log:     ", [round(c * log(1 + v)) for v in row])

gamma = float(input("Gamma (below 1 brightens): "))
print("gamma:   ", [round(255 * (v / 255) ** gamma) for v in row])

a, b = 80, 200                                  # grey level slicing range
print("slice:   ", [255 if a <= v <= b else 0 for v in row])
''', stdin='0.5\n')

K.lesson('histogram', 'The image histogram', f'''
<p>A histogram counts. For an 8 bit grey image it has 256 bars, one for each value from 0 to 255, and the height of bar <i>i</i> is the number of pixels with value <i>i</i>. Divide by the number of pixels and you get a probability distribution over intensities.</p>
{fxs(
    fx('Histogram', '<i>h</i>(<i>i</i>) = number of pixels with value <i>i</i>', '<i>i</i> = 0, 1, …, 255. The bars add up to <i>N</i> = <i>w</i> × <i>h</i>.'),
    fx('Normalised histogram', '<i>p</i>(<i>i</i>) = ' + frac('<i>h</i>(<i>i</i>)', '<i>N</i>'), 'The values add up to 1.'),
    fx('Cumulative distribution', 'CDF(<i>r</i>) = Σ<sub><i>i</i> ≤ <i>r</i></sub> <i>p</i>(<i>i</i>)', 'A running total that climbs from 0 to 1.', key=True))}
<h3>How many, never where</h3>
<p>A histogram throws away every position. Very different pictures can have exactly the same histogram, as the animation shows. This is the main limitation the lecture stresses.</p>
{viz('samehist')}
<h3>Reading exposure from the histogram</h3>
{table(['Photo', 'Histogram shape', 'What you see'], [
    ['Underexposed', 'A tall, narrow peak near the dark end', 'Dark, shadow detail lost'],
    ['Well exposed', 'A wide spread across the range', 'Clear detail in darks and lights'],
    ['Overexposed', 'Everything bunched near the bright end, little variation', 'Washed out, flat, low contrast'],
    ['Low contrast (fog)', 'A narrow hump in the middle', 'Grey and dull']])}
{code('histogram')}
''', kw=['histogram', 'normalised histogram', 'CDF', 'cumulative distribution', 'how many not where', 'underexposed', 'overexposed', 'exposure'])

K.lesson('brightness', 'Brightness, contrast and dynamic range', f'''
<p>The lecture gives a sentence worth memorising: <b>brightness decides where the intensity distribution sits, contrast decides how widely it is spread, and dynamic range is how many distinct levels are used.</b></p>
{fxs(
    fx('Brightness', '<i>B</i>(<i>I</i>) = ' + frac('1', '<i>wh</i>') + ' Σ<sub><i>v</i>=1</sub><sup><i>h</i></sup> Σ<sub><i>u</i>=1</sub><sup><i>w</i></sup> <i>I</i>(<i>u</i>, <i>v</i>)', 'The average intensity of all pixels.', key=True),
    fx('RMS contrast', 'σ = ' + sqrt(frac('1', '<i>wh</i>') + ' Σ Σ (<i>I</i>(<i>u</i>, <i>v</i>) − <i>B</i>)²'), 'The standard deviation of the intensities, the spread of the histogram.'),
    fx('Michelson contrast', '<i>C</i> = ' + frac('<i>I</i><sub>max</sub> − <i>I</i><sub>min</sub>', '<i>I</i><sub>max</sub> + <i>I</i><sub>min</sub>'), 'A change in luminance relative to the average luminance, from 0 to 1.'),
    fx('Linear contrast and brightness', '<i>g</i> = α<i>f</i> + β, then clip to [0, 255]', 'α above 1 stretches the histogram, β shifts it.'))}
<p>Contrast is about the <b>spread</b> of the histogram, not the height of its peak. A narrow central hump means low contrast. A wide spread means good contrast. Piling values at both ends (0 and 255) gives very high contrast but loses detail, and the lecture warns it can start to look like noise.</p>
<p><b>Dynamic range</b> counts the distinct levels an image uses. More levels give smoother gradations, which is why TVs advertise HDR (high dynamic range). An image with few levels looks posterised.</p>
{ladder(
    '<p>Brightness is how much light the whole picture gives off. Contrast is how different the light and dark parts are. A foggy day has low contrast: everything is a similar grey.</p>',
    '<p>Brightness is the mean of the pixel values and contrast is often measured by their standard deviation. Adding a constant changes the mean but not the standard deviation. Multiplying by α changes both the mean and the standard deviation by a factor α (before clipping).</p>',
    '<p>Perceived contrast is not linear in intensity. Weber&#39;s law says the smallest visible change is roughly proportional to the background level, which is why gamma and log curves, which expand dark values, often look more natural than linear stretching. Sensor noise also grows with signal, so stretching dark regions amplifies noise.</p>',
    '<p>HDR imaging merges several exposures into a radiance map with far more range than a display can show, then uses tone mapping (global curves or local operators) to compress it. Learned tone mapping and exposure correction networks are an active research area, along with evaluating them without a ground truth image.</p>')}
''', kw=['brightness', 'mean intensity', 'contrast', 'RMS contrast', 'Michelson contrast', 'standard deviation', 'dynamic range', 'HDR', 'linear transform'])

K.lesson('pointops', 'Point operations: negative, log, gamma and slicing', f'''
<p>A <b>point operation</b> changes each pixel using only its own value. It is a function <i>s</i> = <i>T</i>(<i>r</i>) from input level <i>r</i> to output level <i>s</i>, so it can be drawn as a curve. Point operations are the simplest form of image processing, and they are very fast because each pixel is handled once.</p>
{fxs(
    fx('Negative', '<i>g</i>(<i>x</i>, <i>y</i>) = <i>L</i> − <i>f</i>(<i>x</i>, <i>y</i>)', '<i>L</i> is the maximum value, 255 for 8 bits. In OpenCV: img_neg = 255 − img.', key=True),
    fx('Log transform', '<i>s</i> = <i>c</i> · log(1 + |<i>r</i>|)', 'Compresses large values more than small ones. Choose <i>c</i> = 255 ÷ log(256) so 255 maps to 255.', key=True),
    fx('Gamma (power law)', '<i>s</i> = 255 (' + frac('<i>r</i>', '255') + ')<sup>γ</sup>', 'γ below 1 brightens dark areas, γ above 1 darkens.'),
    fx('Grey level slicing', '<i>s</i> = high if <i>A</i> ≤ <i>r</i> ≤ <i>B</i>, otherwise low (or unchanged)', 'Highlights one band of intensities.'))}
{viz('pointops')}
<h3>When to use which</h3>
{table(['Operation', 'Use it when', 'Example'], [
    ['Negative', 'Detail sits in dark areas and is easier to read inverted', 'Reading X ray films, mammograms'],
    ['Linear stretch', 'The histogram is narrow but its shape is fine', 'A foggy photo'],
    ['Log', 'A few very bright pixels hide everything else', 'Astronomy, the magnitude of a Fourier spectrum, satellite and medical images'],
    ['Gamma', 'You need a smooth, adjustable brighten or darken', 'Display correction, under or overexposed photos'],
    ['Slicing', 'Only one intensity band matters', 'Tissue in a scan, water in a satellite image, a material in inspection']])}
{code('pointops')}
{scene('a radiologist looking for a small lesion', '<p>A large dark region in a scan can dominate an AI model, which then learns mostly about that region and misses small important structures. The lecture describes grey level slicing as a fix: keep only the intensity band of the tissue of interest and set everything else to a flat constant. A flat region has no pattern, so the model cannot be biased by it, and the lesion stands out, just as it does for a radiologist when a region is pre highlighted.</p>')}
''', kw=['point operation', 'negative', 'log transform', 'gamma correction', 'power law', 'grey level slicing', 'gray level slicing', 'transfer function'])

K.lesson('equalise', 'Histogram equalisation', f'''
<p>Histogram equalisation is a point operation whose curve is chosen automatically from the image itself. It spreads crowded values over the full 0 to 255 range, so neighbouring intensities that were hard to tell apart become clearly different. The lecture adds an honest caveat: it does not make the histogram perfectly flat, it makes better use of the available range.</p>
{fx('Equalisation mapping', '<i>s</i> = round[ ' + frac('CDF(<i>r</i>) − CDF<sub>min</sub>', '1 − CDF<sub>min</sub>') + ' × 255 ]', 'CDF<sub>min</sub> is the smallest non zero CDF value, the CDF of the darkest level present. In general replace 255 by <i>L</i> − 1.', key=True)}
{viz('histeq')}
{steps('Worked example from the lecture', [
    'The image is four rows of 80, 100, 120 and 140. It uses only the range 80 to 140, so it looks grey.',
    'Histogram: each level has 4 of the 16 pixels, so each probability is 4 ÷ 16 = 0.25.',
    'CDF: 80 → 0.25, 100 → 0.50, 120 → 0.75, 140 → 1.00. So CDF<sub>min</sub> = 0.25.',
    'Map 100: (0.50 − 0.25) ÷ (1 − 0.25) × 255 = 0.333 × 255 = 85. In the same way 80 → 0, 120 → 170, 140 → 255.',
    'The output uses the full range: black, dark grey, light grey and white.'])}
{code('equalise')}
{deep('why the CDF flattens the histogram', '<p>Treat the intensity as a random variable <i>R</i> with cumulative distribution <i>F</i>. Define <i>S</i> = <i>F</i>(<i>R</i>). For any <i>t</i> between 0 and 1, P(<i>S</i> ≤ <i>t</i>) = P(<i>R</i> ≤ <i>F</i><sup>−1</sup>(<i>t</i>)) = <i>F</i>(<i>F</i><sup>−1</sup>(<i>t</i>)) = <i>t</i>. A variable whose probability of being below <i>t</i> equals <i>t</i> is uniform on [0, 1]. This is the probability integral transform. Images are discrete, so all pixels of one value must move together and the result is only roughly flat. That is the caveat in the notes.</p>')}
{note('Global equalisation can over boost noise in flat regions and wash out areas that were already fine. CLAHE (contrast limited adaptive histogram equalisation) equalises small tiles separately and limits how steep the curve can get. It is the version most used in medical imaging and as a preprocessing step.', 'tip')}
''', kw=['histogram equalisation', 'histogram equalization', 'CDF mapping', 'CDFmin', 'probability integral transform', 'CLAHE', 'contrast enhancement'])

K.lesson('models', 'Why this matters for AI models', f'''
<p>It is tempting to think a deep network will cope with any input. The lecture asked what happens if a very dark, low contrast image goes straight into a model. The class answers were all correct: objects cannot be identified, features are not extracted, and the dominant dark region biases what the model learns.</p>
<ul>
<li>Edges and gradients are the raw material of HOG, SIFT and the first layer of a CNN. In a squashed histogram, neighbouring surfaces get almost the same value, so their edges are weak or vanish.</li>
<li>A model trained on well exposed photos sees a dark photo as a different distribution. Normalising contrast is a cheap way to reduce that shift.</li>
<li>In medicine, astronomy and remote sensing, the important detail is often in a small part of a huge dynamic range. Log transforms and slicing make it visible to people and to models.</li>
</ul>
{table(['Problem in the histogram', 'Tool', 'Effect'], [
    ['Narrow hump, good shape', 'Linear stretch', 'Spreads values, keeps their order and spacing'],
    ['Narrow and unevenly crowded', 'Histogram equalisation or CLAHE', 'Spreads crowded values the most'],
    ['A few huge values', 'Log or gamma below 1', 'Compresses highlights, lifts shadows'],
    ['Only one band matters', 'Grey level slicing', 'Removes everything else']])}
{note('These methods change the input distribution. Apply exactly the same preprocessing at training time and at deployment, or the model sees two different worlds.', 'warn')}
''', kw=['preprocessing', 'dark image', 'low contrast', 'model bias', 'dominant region', 'distribution shift', 'feature extraction'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does an image histogram count?', ['The number of edges', 'How many pixels have each intensity value', 'The number of colours in the scene', 'The position of the brightest pixel'], 1,
       'Bars over 0 to 255.', 'Bar i is the number of pixels with value i. It says nothing about where those pixels are.')
K.quiz('e', 'The brightness B(I) of a grey image is', ['Its largest value', 'The average of all pixel values', 'The number of distinct values', 'The difference between the largest and smallest values'], 1,
       'Sum, then divide by the count.', 'B(I) = (1 ÷ wh) Σ Σ I(u, v), the mean intensity.')
K.quiz('e', 'What is the negative of a pixel with value 30 in an 8 bit image?', ['30', '225', '255', '−30'], 1, 'g = 255 − f.', '255 − 30 = 225.')
K.quiz('m', 'Two images have identical histograms. Which statement must be true?', [
    'They look the same', 'They have the same mean brightness and the same number of pixels at each value', 'They have the same edges', 'They show the same object'], 1,
    'Histograms forget position.', 'Same histogram means same counts, so the same mean and standard deviation, but the pixels can be arranged in any way.')
K.quiz('m', 'Contrast is linked mainly to which property of the histogram?', ['The height of the tallest bar', 'Its spread', 'Its leftmost bar', 'The number of pixels'], 1,
       'The lecture says not the peak.', 'A wide spread means good contrast. Brightness is where the distribution sits, contrast is how wide it is.')
K.quiz('m', 'Which transform best reveals faint stars next to a very bright one?', ['Negative', 'Log transform', 'Grey level slicing at 250 to 255', 'Multiplying by 0.5'], 1,
       'Compress the large values.', 'log(1 + r) squeezes the huge values of the bright star much more than the small values of faint ones, so both fit on the display.')
K.quiz('m', 'Gamma correction with γ = 0.5 on a dark photo will', ['Darken it', 'Brighten the dark tones more than the bright ones', 'Invert it', 'Leave it unchanged'], 1,
       '(r ÷ 255) to the power 0.5 is larger than r ÷ 255 for values between 0 and 1.', 'Square roots of numbers below 1 are larger than the numbers themselves, and the effect is strongest for small values.')
K.quiz('h', 'After histogram equalisation the histogram of a real image is usually', ['Perfectly flat', 'Roughly spread across the range but not perfectly flat, because equal pixel values must move together', 'Identical to the input', 'A single bar'], 1,
       'Pixels are discrete.', 'The probability integral transform gives a uniform result only for continuous values. With 256 levels, all pixels with one value land on one output value.')
K.quiz('h', 'In equalisation, why subtract CDFmin before scaling?', [
    'To make the result negative', 'So the darkest level present maps to 0 and the full range 0 to 255 is used', 'To remove noise', 'Because the CDF starts at 1'], 1,
    'What does the darkest level map to without it?', 'Without subtracting, the darkest level would map to CDFmin × 255, for example 64 in the lecture example, wasting the range below it.')
K.quiz('h', 'g = 2f − 100 is applied to an image whose values run from 40 to 180. What happens?', [
    'Nothing is lost', 'Values below 50 become negative and values above 177.5 exceed 255, so both ends are clipped and that detail is lost', 'The image becomes a negative', 'The histogram narrows'], 1,
    'Check the two ends.', '2 × 40 − 100 = −20 and 2 × 180 − 100 = 260, so both ends clip. Clipped pixels all become 0 or 255 and their differences are gone.')
K.quiz('x', 'A photo has a large black background and a small object of interest. A classifier trained on such photos focuses on the background. Which preprocessing from the lecture best addresses this?', [
    'Increase brightness', 'Grey level slicing so the background becomes a flat constant with no pattern', 'Save as JPEG', 'Convert to CMYK'], 1,
    'A flat region gives the model nothing to learn.', 'The lecture contrasts a real but dominant region (which can still bias the model) with a sliced, uniform region, which carries no pattern and so cannot bias it.')
K.quiz('x', 'Which statement about point operations is correct?', [
    'They use the neighbours of each pixel', 'They can be described by a single curve s = T(r), and histogram equalisation is one whose curve is the scaled CDF', 'They always increase contrast', 'They change the size of the image'], 1,
    'Point means one pixel at a time.', 'A point operation depends only on the pixel value, so it is a lookup table. Filters, which use neighbours, come in the next chapter.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the brightness (mean) of the 2 × 2 image [[100, 140], [120, 120]]?', '120', 'Add the four values and divide by 4.',
       ['Sum: 100 + 140 + 120 + 120 = 480.', 'Number of pixels: 4.', eq('B = 480 ÷ 4 = 120')], check=120)
K.calc('e', 'What is the negative of a pixel with value 200 in an 8 bit image?', '55', 'g = 255 − f.',
       ['L = 255 for 8 bits.', eq('g = 255 − 200 = 55'), 'Bright becomes dark and dark becomes bright.'], check=55)
K.calc('e', 'How many bars does the histogram of a 64 × 64 grey image add up to?', '4096', 'The bars count every pixel once.',
       ['Each pixel falls in exactly one bar.', eq('64 × 64 = 4,096'), 'So the heights of all bars add up to 4,096.'], check=4096)
K.calc('m', 'In the lecture example (four rows of 80, 100, 120, 140), what is CDF(120)?', '0.75', 'Add the probabilities of 80, 100 and 120.',
       ['Each level has probability 4 ÷ 16 = 0.25.', 'CDF(120) = p(80) + p(100) + p(120).', eq('0.25 + 0.25 + 0.25 = 0.75')], check=0.75)
K.calc('m', 'In the same example, what does level 100 map to after equalisation?', '85', 's = round[(CDF − CDFmin) ÷ (1 − CDFmin) × 255].',
       ['CDF(100) = 0.50 and CDFmin = 0.25.', '(0.50 − 0.25) ÷ (1 − 0.25) = 0.25 ÷ 0.75 = 0.3333.', eq('0.3333 × 255 = 85')], check=85)
K.calc('m', 'An image has I<sub>max</sub> = 200 and I<sub>min</sub> = 50. What is its Michelson contrast?', '0.6', '(max − min) ÷ (max + min).',
       ['Top: 200 − 50 = 150.', 'Bottom: 200 + 50 = 250.', eq('C = 150 ÷ 250 = 0.6')], check=0.6)
K.calc('m', 'What is the RMS contrast (population standard deviation) of the pixels 10, 20, 30, 40? Give two decimals.', '11.18', 'Find the mean, then the average squared distance from it.',
       ['Mean: (10 + 20 + 30 + 40) ÷ 4 = 25.', 'Squared distances: 225, 25, 25, 225, which add to 500.', 'Variance: 500 ÷ 4 = 125.', eq('σ = √125 ≈ 11.18')], check=125 ** 0.5, tol=0.006)
K.calc('h', 'A log transform uses s = c · ln(1 + r) with c = 255 ÷ ln(256). What is s for r = 10? Give two decimals.', '110.27', 'Work out c first.',
       ['c = 255 ÷ ln 256 = 255 ÷ 5.5452 ≈ 45.986.', 'ln(1 + 10) = ln 11 ≈ 2.3979.', eq('s ≈ 45.986 × 2.3979 ≈ 110.27'), 'A dark value of 10 is lifted to 110, while 255 stays at 255.'], check=110.27, tol=0.01)
K.calc('h', 'A 4 × 4 image has three 50s, three 100s, four 150s and six 200s. After equalisation, what does 150 map to?', '137', 'Build the CDF first: counts 3, 3, 4, 6 out of 16.',
       ['CDF: 50 → 3/16 = 0.1875, 100 → 6/16 = 0.375, 150 → 10/16 = 0.625, 200 → 1.', 'CDFmin = 0.1875.', '(0.625 − 0.1875) ÷ (1 − 0.1875) = 0.4375 ÷ 0.8125 ≈ 0.5385.', eq('0.5385 × 255 ≈ 137.3 → 137')], check=137)
K.calc('h', 'Apply gamma correction s = 255 (r ÷ 255)<sup>γ</sup> with γ = 0.5 to r = 64. Give two decimals.', '127.75', 'Divide by 255, take the square root, multiply by 255.',
       ['r ÷ 255 = 64 ÷ 255 ≈ 0.25098.', '√0.25098 ≈ 0.50098.', eq('s ≈ 0.50098 × 255 ≈ 127.75'), 'A quarter brightness pixel is lifted to about half brightness.'], check=255 * (64 / 255) ** 0.5, tol=0.006)
K.calc('x', 'A linear stretch maps the range [80, 140] onto [0, 255] with s = (r − 80) × 255 ÷ 60. What is s for r = 110?', '127.5', 'Substitute r = 110.',
       ['r − 80 = 30.', '30 × 255 = 7,650.', eq('7,650 ÷ 60 = 127.5'), 'The middle of the old range lands in the middle of the new one. Equalisation of the lecture example gave 85 and 170 instead, because it follows the CDF, not a straight line.'], check=127.5)
K.calc('x', 'An image uses 37 distinct grey levels. How many bits per pixel are needed at least to store those levels without loss?', '6', 'Find the smallest b with 2<sup>b</sup> ≥ 37.',
       ['2<sup>5</sup> = 32 is too few.', '2<sup>6</sup> = 64 is enough.', eq('b = ⌈log<sub>2</sub> 37⌉ = 6'), 'The dynamic range of 37 levels fits in 6 bits, even though the file may store 8.'], check=6)

# ---------------------------------------------------------------- assignments
K.assign('hist', 'e', 'Compute a histogram',
         '<p>Write <code>histogram(img, levels=256)</code> that returns a list of length <code>levels</code> where entry <code>i</code> counts the pixels with value <code>i</code>.</p>',
         '''
def histogram(img, levels=256):
    # your code here
    pass
''', [('histogram([[0, 1], [1, 3]], 4)', [1, 2, 0, 1]), ('histogram([[2, 2, 2]], 3)', [0, 0, 3]), ('sum(histogram([[5] * 8] * 8))', 64)],
         '''
def histogram(img, levels=256):
    h = [0] * levels
    for row in img:
        for v in row:
            h[v] += 1
    return h
''', 'Start with a list of zeros and add one for each pixel.', '<p>NumPy does this in one line with <code>np.bincount(img.ravel(), minlength=256)</code>, and OpenCV with <code>cv2.calcHist</code>.</p>')
K.assign('stats', 'e', 'Brightness and contrast',
         '<p>Write <code>stats(img)</code> that returns <code>[brightness, contrast]</code>: the mean and the population standard deviation of all pixels, each rounded to 2 decimals.</p>',
         '''
def stats(img):
    # your code here
    pass
''', [('stats([[100, 140], [120, 120]])', [120.0, 14.14]), ('stats([[10, 20, 30, 40]])', [25.0, 11.18]), ('stats([[7, 7], [7, 7]])', [7.0, 0.0])],
         '''
def stats(img):
    px = [v for row in img for v in row]
    mean = sum(px) / len(px)
    var = sum((v - mean) ** 2 for v in px) / len(px)
    return [round(mean, 2), round(var ** 0.5, 2)]
''', 'Flatten the rows into one list first.', '<p>A flat image has zero contrast. Adding 50 to every pixel would change the first number but not the second.</p>')
K.assign('equalise', 'm', 'Histogram equalisation',
         '<p>Write <code>equalise(img)</code> that returns the equalised image using s = round[(CDF(r) − CDFmin) ÷ (1 − CDFmin) × 255]. If the image has only one value, return all zeros.</p>',
         '''
def equalise(img):
    # your code here
    pass
''', [('equalise([[80, 80, 80, 80], [100, 100, 100, 100], [120, 120, 120, 120], [140, 140, 140, 140]])', [[0, 0, 0, 0], [85, 85, 85, 85], [170, 170, 170, 170], [255, 255, 255, 255]]),
      ('equalise([[10, 20], [10, 20]])', [[0, 255], [0, 255]]),
      ('equalise([[50, 50, 50, 100], [100, 100, 150, 150], [150, 150, 200, 200], [200, 200, 200, 200]])', [[0, 0, 0, 59], [59, 59, 137, 137], [137, 137, 255, 255], [255, 255, 255, 255]]),
      ('equalise([[9, 9]])', [[0, 0]])],
         '''
def equalise(img):
    px = [v for row in img for v in row]
    n = len(px)
    levels = sorted(set(px))
    if len(levels) == 1:
        return [[0 for _ in row] for row in img]
    cdf, total = {}, 0
    for r in levels:
        total += px.count(r) / n
        cdf[r] = total
    cmin = cdf[levels[0]]
    m = {r: round((cdf[r] - cmin) / (1 - cmin) * 255) for r in levels}
    return [[m[v] for v in row] for row in img]
''', 'Build a dictionary from level to CDF, then a dictionary from level to new value, then rebuild the image.',
         '<p>The third test is the worked problem from this chapter: 100 → 59, 150 → 137. The single value case would divide by zero, so it is handled first.</p>')
K.assign('slice', 'm', 'Grey level slicing',
         '<p>Write <code>slice_levels(img, a, b, keep=False)</code>. Pixels with <code>a ≤ v ≤ b</code> become 255. Other pixels become 0, or stay unchanged when <code>keep</code> is true.</p>',
         '''
def slice_levels(img, a, b, keep=False):
    # your code here
    pass
''', [('slice_levels([[10, 100, 200]], 50, 150)', [[0, 255, 0]]), ('slice_levels([[10, 100, 200]], 50, 150, True)', [[10, 255, 200]]), ('slice_levels([[50, 150]], 50, 150)', [[255, 255]])],
         '''
def slice_levels(img, a, b, keep=False):
    return [[255 if a <= v <= b else (v if keep else 0) for v in row] for row in img]
''', 'A conditional expression inside a nested list comprehension does it in one line.',
         '<p>Both forms appear in textbooks. Setting the rest to 0 isolates the band. Keeping the rest shows the band in context.</p>')

K.must('Histogram', 'h(i) counts pixels with value i, p(i) = h(i) ÷ N, CDF is the running total. It tells how many, never where.')
K.must('Brightness, contrast, dynamic range', 'Brightness = mean (where the histogram sits), contrast = spread such as σ or Michelson, dynamic range = number of levels used.')
K.must('Point operations', 'Negative 255 − f, linear αf + β with clipping, log c·log(1 + r) to compress highlights, gamma 255(r ÷ 255)^γ, slicing for one band.')
K.must('Equalisation', 's = round[(CDF − CDFmin) ÷ (1 − CDFmin) × 255]. Lecture example 80, 100, 120, 140 gives 0, 85, 170, 255. Not perfectly flat for discrete images.')
K.must('Why it matters', 'Dark, low contrast inputs weaken edges and bias models toward dominant regions. Use the same preprocessing in training and deployment.')

T = K.topic(
    slug='histograms-contrast', topic='histograms', step=(2, 'Images as numbers', 'cv-image-basics', 'How pictures are stored, coloured, compressed, measured and cleaned before any recognition happens.', 'School and college'),
    title='Histograms, brightness and contrast', short='Histograms and contrast', badge='2.2', minutes=40,
    lead='Measure an image with a histogram, then change it pixel by pixel: negatives, contrast stretching, log and gamma curves, grey level slicing and histogram equalisation, with the lecture example worked step by step.',
    desc='Image histograms, brightness and contrast formulas, dynamic range, negative, log, gamma and slicing transforms, and histogram equalisation with a full worked example.',
    summary='Histograms and the CDF, brightness, contrast and dynamic range, negatives, log, gamma and slicing, and histogram equalisation step by step.',
    keywords=['histogram', 'brightness', 'contrast', 'dynamic range', 'negative', 'log transform', 'gamma', 'grey level slicing', 'histogram equalisation', 'CDF', 'CLAHE', 'exposure'],
    recap='<p>A histogram summarises the values but forgets their positions. Brightness is where it sits, contrast how wide it is, and dynamic range how many levels it uses. Point operations reshape it with a single curve, and equalisation picks that curve from the CDF.</p>')
