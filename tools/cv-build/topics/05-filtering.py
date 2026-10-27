# Chapter 5: noise models, convolution, smoothing (mean, Gaussian, median), sharpening and the frequency view.
# Source: lectures 3 and 4, part IV, plus the blur and sharpen stages of the project notebook.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('mean_median', r'''
# Mean versus median on the lecture patch (Problems 6 and 7)
patch = [[10, 20, 10],
         [100, 20, 10],
         [10, 10, 20]]

outlier = int(input("Value of the noisy pixel (the lecture uses 100): "))
patch[1][0] = outlier

values = [v for row in patch for v in row]   # the 9 neighbours
mean = sum(values) / 9
print("mean filter output:", round(mean, 2))

ordered = sorted(values)
print("sorted:", ordered)
print("median filter output:", ordered[4])   # the 5th of 9 values
''', stdin='100\n')

K.code('conv2d', r'''
# 2D filtering with no padding: slide a 3 x 3 kernel over a 5 x 5 image
img = [[10, 10, 10, 90, 90],
       [10, 10, 10, 90, 90],
       [10, 10, 10, 90, 90],
       [10, 10, 10, 90, 90],
       [10, 10, 10, 90, 90]]
k = [[0, -1, 0],
     [-1, 5, -1],
     [0, -1, 0]]                       # the sharpening kernel from the notebook

out_size = len(img) - 3 + 1           # (W - k + 2P) / S + 1 with P = 0, S = 1
out = []
for y in range(out_size):
    row = []
    for x in range(out_size):
        s = sum(k[i][j] * img[y + i][x + j] for i in range(3) for j in range(3))
        row.append(s)
    out.append(row)

for row in out:
    print(row)
''')

K.code('psnr', r'''
# PSNR between a clean image and a noisy copy
from math import log10

clean = [[50, 50, 50], [50, 200, 50], [50, 50, 50]]
noisy = [[60, 40, 50], [50, 220, 50], [50, 50, 40]]

n = 9
mse = sum((clean[y][x] - noisy[y][x]) ** 2 for y in range(3) for x in range(3)) / n
print("MSE:", round(mse, 2))

psnr = 10 * log10(255 ** 2 / mse)
print("PSNR:", round(psnr, 2), "dB")
''')

K.lesson('noise', 'Four kinds of noise', f'''
<p>No camera records a perfect copy of the scene. The lecture calls noise the unwanted guests in an image: random changes caused by the sensor, the electronics, poor light, the weather or errors during transmission. Each kind of noise has its own pattern, and each pattern calls for a different filter. Using the wrong filter either leaves the noise or destroys real detail.</p>
{fxs(
    fx('Additive noise', '<i>g</i>(<i>x</i>, <i>y</i>) = <i>f</i>(<i>x</i>, <i>y</i>) + <i>n</i>(<i>x</i>, <i>y</i>)', '<i>f</i> is the true image, <i>g</i> the one you record. The noise does not depend on the brightness.', key=True),
    fx('Multiplicative (speckle) noise', '<i>g</i>(<i>x</i>, <i>y</i>) = <i>f</i>(<i>x</i>, <i>y</i>) · (1 + <i>n</i>(<i>x</i>, <i>y</i>))', 'The noise is scaled by the signal, so bright regions get noisier than dark ones.', key=True))}
{table(['Noise', 'What it looks like', 'Typical source', 'Best filter'], [
    ['Gaussian (white)', 'Many small random changes over the whole image, a grainy look', 'Sensor and electronic noise', 'Gaussian or averaging filter'],
    ['Impulse (salt and pepper)', 'A few pixels jump to pure black (0) or pure white (255)', 'Transmission or sensor errors', 'Median filter'],
    ['Speckle', 'Granular texture whose strength grows with local brightness', 'Ultrasound and SAR (synthetic aperture radar)', 'Adaptive or median type filters'],
    ['Poisson (shot)', 'Grain that is worst in low light', 'Too few photons reach the sensor', 'Denoising with variance stabilisation']])}
{viz('noiselab')}
<p>The lecture made one more point that is easy to miss. High frequency is not a type of noise. It only means the intensity changes quickly from pixel to pixel. Gaussian and impulse noise both contain strong high frequencies, but so do real edges and fine texture. A filter that simply removes all high frequencies therefore blurs away detail along with the noise.</p>
{note('Salt and pepper pushes a few pixels straight to an extreme by a sudden jump. Speckle changes values gradually by multiplying them. The mechanisms differ, which is why they need different filters.', 'exam')}
''', kw=['noise', 'Gaussian noise', 'white noise', 'salt and pepper', 'impulse noise', 'speckle', 'Poisson noise', 'shot noise', 'additive noise', 'multiplicative noise', 'SAR', 'ultrasound'])

K.lesson('convolution', 'Convolution: sliding a kernel', f'''
<p><b>Spatial filtering</b> means applying a small grid of weights, called a <b>kernel</b> or mask, to the neighbourhood of every pixel. Lay the kernel over the image, multiply each weight by the pixel beneath it, add up the products, and write the total into the output. Then slide one step and repeat. The same idea, with the weights learned instead of chosen, is the building block of every convolutional neural network later in the course.</p>
{fxs(
    fx('Filtering (correlation)', '<i>g</i>(<i>x</i>, <i>y</i>) = Σ<sub><i>i</i>=−<i>a</i></sub><sup><i>a</i></sup> Σ<sub><i>j</i>=−<i>b</i></sub><sup><i>b</i></sup> <i>h</i>(<i>i</i>, <i>j</i>) · <i>f</i>(<i>x</i> + <i>i</i>, <i>y</i> + <i>j</i>)', 'A (2<i>a</i> + 1) × (2<i>b</i> + 1) kernel <i>h</i>. This is what cv2.filter2D and CNN layers compute.', key=True),
    fx('True convolution', '(<i>h</i> ∗ <i>f</i>)(<i>x</i>, <i>y</i>) = Σ<sub><i>i</i></sub> Σ<sub><i>j</i></sub> <i>h</i>(<i>i</i>, <i>j</i>) · <i>f</i>(<i>x</i> − <i>i</i>, <i>y</i> − <i>j</i>)', 'The same, with the kernel flipped in both directions. For symmetric kernels such as box and Gaussian the two are identical.'),
    fx('Output size', '<i>O</i> = ⌊' + frac('<i>W</i> − <i>k</i> + 2<i>P</i>', '<i>S</i>') + '⌋ + 1', '<i>W</i> input width, <i>k</i> kernel size, <i>P</i> padding on each side, <i>S</i> stride.', key=True))}
{viz('conv')}
<h3>What happens at the border</h3>
<p>At the edge of the image part of the kernel hangs over empty space. There are three common choices. <b>Zero padding</b> pretends the outside is black and keeps the size. <b>Replicate</b> copies the edge pixel outward, which avoids a dark frame. <b>Valid</b> (no padding) only computes where the kernel fits, so the output shrinks by <i>k</i> − 1. Turn the padding dial in the animation and watch the corner values change.</p>
{code('conv2d')}
{deep('why convolution is linear and shift invariant', '<p>If you filter <i>af</i><sub>1</sub> + <i>bf</i><sub>2</sub> you get <i>a</i>(<i>h</i> ∗ <i>f</i><sub>1</sub>) + <i>b</i>(<i>h</i> ∗ <i>f</i><sub>2</sub>), because each output is a weighted sum. Shifting the input shifts the output by the same amount, because the same weights are used everywhere. Every operation that is both linear and shift invariant is a convolution with some kernel, namely its response to a single bright pixel (the impulse response). Try the spike input in the animation: the output is the kernel itself, flipped. This is also why a CNN layer can detect a pattern wherever it appears in the image.</p>')}
''', kw=['convolution', 'correlation', 'kernel', 'mask', 'spatial filtering', 'padding', 'zero padding', 'stride', 'output size', 'filter2D', 'impulse response', 'linear shift invariant'])

K.lesson('smoothing', 'Smoothing: mean, Gaussian and median', f'''
<p>Smoothing filters are <b>low pass</b> filters. They keep slow changes and remove quick ones, which makes the image look softer and quieter.</p>
{fxs(
    fx('Mean (box) filter', '<i>h</i> = ' + frac('1', '9') + mat([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), 'Each output is the plain average of the 3 × 3 neighbourhood. The weights add up to 1, so flat areas keep their brightness.', key=True),
    fx('Gaussian kernel', '<i>G</i>(<i>x</i>, <i>y</i>) = ' + frac('1', '2πσ²') + ' exp(−' + frac('<i>x</i>² + <i>y</i>²', '2σ²') + ')', 'Near pixels count more than far ones. A common 3 × 3 version is (1/16)[[1, 2, 1], [2, 4, 2], [1, 2, 1]].', key=True),
    fx('OpenCV default σ', 'σ = 0.3 × ((<i>k</i> − 1) × 0.5 − 1) + 0.8', 'Used when you pass σ = 0, as the notebook does with cv2.GaussianBlur(image, (9, 9), 0). For <i>k</i> = 9 this gives σ = 1.7.'),
    fx('Median filter', '<i>g</i>(<i>x</i>, <i>y</i>) = median{{ <i>f</i>(<i>s</i>, <i>t</i>) : (<i>s</i>, <i>t</i>) in the window }}', 'Not a weighted sum at all. Sort the neighbours and take the middle one.'))}
{steps('The lecture problem: mean versus median', [
    'Patch: [[10, 20, 10], [100, 20, 10], [10, 10, 20]]. The 100 is almost certainly a noisy pixel.',
    'Mean: 10 + 20 + 10 + 100 + 20 + 10 + 10 + 10 + 20 = 210, and 210 ÷ 9 ≈ 23.33. Without the outlier the average would be near 14.4, so one bad pixel pulled it up a lot.',
    'Median: sort the nine values to 10, 10, 10, 10, 10, 20, 20, 20, 100 and take the 5th. The answer is 10.',
    'The median is far closer to the true local value, because the outlier sorts to the end of the list and never reaches the middle.'])}
{code('mean_median')}
<h3>Why the median keeps edges sharp</h3>
<p>Averaging is linear, so every neighbour, including a badly wrong one, pulls the result toward itself. For an outlier to change the median, more than half the window would have to be outliers too. And the median is always a value that really occurred in the window, while the mean can invent a blended value that was never there. At an edge the mean produces a ramp of new in between values, but the median picks a value from one side or the other, so the edge stays crisp.</p>
{deep('separable filters save work', '<p>A kernel is separable when it equals a column vector times a row vector. The box and Gaussian kernels are separable, for example (1/16)[[1, 2, 1], [2, 4, 2], [1, 2, 1]] is (1/4)[1, 2, 1] down the columns times (1/4)[1, 2, 1] across the rows. Filtering with a <i>k</i> × <i>k</i> kernel costs <i>k</i>² multiplications per pixel, but filtering rows and then columns costs only 2<i>k</i>. For <i>k</i> = 9 that is 81 against 18. The median is not separable, and fast versions use running histograms instead.</p>')}
''', kw=['smoothing', 'low pass', 'mean filter', 'box filter', 'averaging filter', 'Gaussian blur', 'GaussianBlur', 'sigma', 'median filter', 'order statistic', 'edge preserving', 'separable'])

K.lesson('sharpening', 'Sharpening and the Laplacian', f'''
<p>Sharpening is the opposite job. It makes edges and fine detail stand out by boosting quick changes. Two kernels appear in this course, and they are closely related.</p>
{fxs(
    fx('Lecture high pass kernel', '<i>h</i> = ' + frac('1', '9') + mat([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]), 'The weights add up to 0. In a flat region every neighbour cancels the centre and the output is 0. At an edge the output is large.', key=True),
    fx('Notebook sharpening kernel', '<i>h</i> = ' + mat([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]), 'The weights add up to 1, so flat regions keep their brightness while edges get extra contrast. The project used this kernel in Stage 3.', key=True),
    fx('Unsharp masking', 'sharpened = <i>f</i> + <i>k</i> (<i>f</i> − <i>G</i><sub>σ</sub> ∗ <i>f</i>)', '<i>f</i> − <i>G</i> ∗ <i>f</i> is the detail that a blur removes. Add <i>k</i> times it back.'))}
<p>Both kernels come from the same recipe. The lecture kernel is the identity minus the box average: the centre weight is 1 − 1/9 = 8/9 and the others are −1/9. So it equals <b>original minus low pass</b>, which is the high pass part. The notebook kernel equals the identity minus the 4 neighbour Laplacian [[0, 1, 0], [1, −4, 1], [0, 1, 0]], which is <b>original plus high pass</b>. The Laplacian is a discrete second derivative, and it is exactly what the lecture means by highlights edges and fine details.</p>
{viz('edge1d')}
{steps('Sharpening one pixel with the notebook kernel', [
    'A pixel of value 100 has four neighbours (up, down, left, right) of value 80.',
    'Multiply: 5 × 100 = 500, and each neighbour gives −1 × 80 = −80.',
    'Add: 500 − 4 × 80 = 500 − 320 = 180.',
    'The pixel was 20 brighter than its neighbours and is now 100 brighter. In a flat region of 80s the output would be 5 × 80 − 320 = 80, unchanged.'])}
{note('Sharpening cannot bring back detail that blur destroyed. It boosts whatever high frequencies are left, and that includes noise. In the project, sharpening the blurred COCO128 images raised mAP50 from 0.6176 to 0.6277 but it stayed below the original 0.6706. You will meet those numbers again in the project lab.', 'warn')}
{scene('a phone camera', '<p>Almost every phone applies some sharpening before it saves a photo, because the tiny lens and sensor blur fine detail. Push it too far and you see bright halos around dark edges and crunchy noise in the sky. Those halos are the overshoots in the curve animation above. Photo editors expose the same three dials as unsharp masking: amount (<i>k</i>), radius (σ) and a threshold that skips small, noisy differences.</p>')}
''', kw=['sharpening', 'high pass', 'Laplacian', 'second derivative', 'unsharp masking', 'sharpen kernel', 'halo', 'overshoot', 'edge enhancement'])

K.lesson('frequency', 'The frequency view and learning from noise', f'''
<p>Filtering can be done in two places. In the <b>spatial domain</b> you slide a kernel over the pixels, as above. In the <b>frequency domain</b> you first turn the image into its frequencies, the same idea as the DCT behind JPEG in chapter 2.1, then multiply each frequency by a gain and turn it back.</p>
{fx('Convolution theorem', '<i>g</i> = <i>h</i> ∗ <i>f</i> &nbsp; ⟺ &nbsp; <i>G</i>(ω<sub>1</sub>, ω<sub>2</sub>) = <i>H</i>(ω<sub>1</sub>, ω<sub>2</sub>) <i>F</i>(ω<sub>1</sub>, ω<sub>2</sub>)', 'Convolving in space is the same as multiplying in frequency. Capital letters are Fourier transforms.', key=True)}
{table(['Filter', 'Keeps', 'Removes', 'Looks like'], [
    ['Low pass (mean, Gaussian)', 'Slow changes, large shapes', 'Fine texture, noise, sharp edges', 'Blur'],
    ['High pass (Laplacian, lecture 1/9 kernel)', 'Edges and fine detail', 'Flat areas and smooth shading', 'A dark image with bright outlines'],
    ['Sharpen = original + high pass', 'Everything, with extra edges', 'Nothing', 'Crisper edges, more visible noise']])}
<p>For large kernels the frequency route is faster, because a fast Fourier transform costs about <i>N</i> log <i>N</i> operations, while direct convolution costs <i>N</i> × <i>k</i>². For the small kernels used here, direct filtering wins.</p>
<h3>Noise is also added on purpose</h3>
<p>The lecturer described a review of a medical imaging paper. The reviewers said the test images were too clean to represent real clinics. The fix was to add different kinds and combinations of noise to the test set and show the model still worked. Noise is therefore not only something to remove. It is a tool for testing robustness.</p>
<p>A whole family of models learns by removing noise. A <b>denoising autoencoder</b> (Vincent and colleagues, 2008) is trained to rebuild a clean image from a deliberately corrupted copy. <b>Diffusion models</b>, behind most current image generators, add Gaussian noise to real images over many small steps and train a network to undo one step at a time. To generate a picture they start from pure noise and run the learned denoising process repeatedly.</p>
{code('psnr')}
{ladder(
    '<p>Noise is random speckle that the camera adds. Blurring hides it by mixing each dot with its neighbours. Sharpening does the opposite and makes edges pop. The median filter is like asking nine neighbours and going with the middle answer, so one person shouting a wild number cannot change the result.</p>',
    '<p>A linear filter is a convolution with a kernel. Low pass kernels have weights that add to 1, high pass kernels add to 0. The output size is ⌊(W − k + 2P) ÷ S⌋ + 1. The median is a non linear order statistic that removes impulse noise and keeps edges. PSNR = 10 log<sub>10</sub>(255² ÷ MSE) measures quality against a clean reference.</p>',
    '<p>By the convolution theorem, filtering multiplies the spectrum by <i>H</i>. The Gaussian is the only kernel that is both separable and rotationally symmetric, and its Fourier transform is again a Gaussian, so it removes high frequencies smoothly without ringing. The box filter has a sinc shaped spectrum with side lobes, which lets some high frequencies through. Wiener filtering chooses <i>H</i> = |<i>F</i>|² ÷ (|<i>F</i>|² + |<i>N</i>|²) to minimise mean squared error when the signal and noise spectra are known.</p>',
    '<p>Modern denoisers are learned. Noise2Noise showed a network can be trained on pairs of independent noisy images with no clean target, because the expected error points to the same answer. Score based diffusion models learn the gradient of the log density of noisy images at every noise level. PSNR rewards blurry averages, so research also reports SSIM and learned perceptual metrics such as LPIPS.</p>')}
''', kw=['frequency domain', 'spatial domain', 'convolution theorem', 'Fourier transform', 'FFT', 'low pass', 'high pass', 'robustness', 'denoising autoencoder', 'diffusion model', 'PSNR', 'MSE'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A few pixels in a photo are pure white or pure black and the rest look fine. What is this noise?', ['Gaussian', 'Salt and pepper (impulse)', 'Speckle', 'Poisson'], 1,
       'Extreme values, only a few pixels.', 'Impulse noise forces a few pixels to 0 or 255. The best filter is the median.')
K.quiz('e', 'Which filter is best for salt and pepper noise?', ['Mean', 'Median', 'Sharpening', 'Negative'], 1,
       'Which one ignores outliers?', 'The median sorts the window and takes the middle value, so a single 0 or 255 never reaches the output.')
K.quiz('e', 'What do the weights of the 3 × 3 mean filter add up to?', ['0', '1', '9', '1/9'], 1,
       'Nine weights of 1/9.', '9 × 1/9 = 1, so a flat region keeps its brightness.')
K.quiz('m', 'Speckle noise is modelled as', ['g = f + n', 'g = f · (1 + n)', 'g = 255 − f', 'g = n'], 1,
       'It grows with the signal.', 'Speckle is multiplicative. Brighter regions get proportionally larger errors, which is why it looks granular and signal dependent.')
K.quiz('m', 'The lecture high pass kernel (1/9)[[−1, −1, −1], [−1, 8, −1], [−1, −1, −1]] is applied to a flat region of value 120. The output is', ['120', '0', '960', '−120'], 1,
       'The weights add to 0.', '(8 × 120 − 8 × 120) ÷ 9 = 0. High pass kernels give zero in flat regions and respond only at changes.')
K.quiz('m', 'Why does the median preserve edges better than the mean?', [
    'It is faster', 'It always returns a value that occurred in the window and ignores outliers, so it does not invent in between values', 'It uses a larger window', 'It is linear'], 1,
    'Think about what values the output can take.', 'The mean blends both sides of an edge into a ramp. The median picks a value from the majority side, so the step stays sharp.')
K.quiz('m', 'A 32 × 32 image is filtered with a 3 × 3 kernel, no padding, stride 1. The output size is', ['32 × 32', '30 × 30', '31 × 31', '16 × 16'], 1,
       '(W − k + 2P) ÷ S + 1.', '(32 − 3 + 0) ÷ 1 + 1 = 30.')
K.quiz('h', 'Which statement about the notebook kernel [[0, −1, 0], [−1, 5, −1], [0, −1, 0]] is true?', [
    'It blurs the image', 'It is the identity minus the 4 neighbour Laplacian, so it adds a high pass part to the original', 'Its weights add to 0', 'It is a median filter'], 1,
    'Subtract [[0, 1, 0], [1, −4, 1], [0, 1, 0]] from the identity.', 'Identity minus the Laplacian gives centre 1 − (−4) = 5 and −1 for each neighbour. The weights add to 1.')
K.quiz('h', 'By the convolution theorem, blurring an image with kernel h is the same as', [
    'Adding H to F', 'Multiplying the spectrum F by H', 'Taking the median of F', 'Dividing F by H'], 1,
    'Convolution in one domain becomes something simpler in the other.', 'g = h ∗ f corresponds to G = H · F. A low pass H is close to 1 at low frequencies and small at high ones.')
K.quiz('h', 'A detector was tested on blurred images and then on the same images after sharpening. What does the course project show?', [
    'Sharpening restores the original accuracy exactly', 'Sharpening recovers a little of the lost mAP but stays below the original, because blur destroys detail and sharpening also boosts noise', 'Sharpening always lowers accuracy', 'Blur has no effect on detection'], 1,
    'Compare 0.6706, 0.6176 and 0.6277.', 'mAP50 was 0.6706 on the original images, 0.6176 after blur and 0.6277 after sharpening. Some edge contrast returns, the lost fine detail does not.')
K.quiz('x', 'Why are diffusion models connected to this chapter?', [
    'They use the median filter', 'They are trained to remove Gaussian noise step by step, and generate images by denoising pure noise', 'They store images as JPEG', 'They only work on video'], 1,
    'Add noise, then learn to remove it.', 'This is the denoising principle the lecture described, the same idea as a denoising autoencoder applied over many noise levels.')
K.quiz('x', 'Filtering with a separable 9 × 9 Gaussian as two 1D passes needs how many multiplications per pixel instead of 81?', ['9', '18', '40', '72'], 1,
    'One pass of 9 along rows, one pass of 9 along columns.', '9 + 9 = 18 multiplications instead of 9 × 9 = 81, a saving of 4.5 times.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Apply the 3 × 3 mean filter to the centre of [[10, 20, 10], [100, 20, 10], [10, 10, 20]]. Give two decimals.', '23.33', 'Add all nine values and divide by 9.',
       ['Sum: 10 + 20 + 10 + 100 + 20 + 10 + 10 + 10 + 20 = 210.', 'Divide by 9.', eq('210 ÷ 9 ≈ 23.33'), 'The single outlier 100 pulls the result well above the typical value of 10 to 20.'], check=210 / 9, tol=0.006)
K.calc('e', 'Apply the 3 × 3 median filter to the same patch. What is the output?', '10', 'Sort the nine values and take the 5th.',
       ['Values: 10, 20, 10, 100, 20, 10, 10, 10, 20.', 'Sorted: 10, 10, 10, 10, 10, 20, 20, 20, 100.', eq('5th value = 10'), 'The outlier sits at the end of the list and has no effect.'], check=10)
K.calc('e', 'What is the sum of the weights in the lecture high pass kernel (1/9)[[−1, −1, −1], [−1, 8, −1], [−1, −1, −1]]?', '0', 'Eight weights of −1 and one of 8, all divided by 9.',
       ['Neighbours: 8 × (−1) = −8.', 'Centre: 8.', eq('(−8 + 8) ÷ 9 = 0'), 'A zero sum means flat regions give zero output, the signature of an edge or high pass kernel.'], check=0)
K.calc('m', 'Speckle noise g = f(1 + n) acts on a pixel with f = 200 and n = 0.1. By how much does the pixel change?', '20', 'Work out g, then g − f.',
       ['g = 200 × (1 + 0.1) = 200 × 1.1.', 'g = 220.', eq('g − f = 220 − 200 = 20'), 'The same n on a pixel of value 50 would change it by only 5. Speckle grows with brightness.'], check=20)
K.calc('m', 'A 32 × 32 image is filtered with a 3 × 3 kernel, no padding, stride 1. How wide is the output?', '30', 'O = ⌊(W − k + 2P) ÷ S⌋ + 1.',
       ['W = 32, k = 3, P = 0, S = 1.', '(32 − 3 + 0) ÷ 1 = 29.', eq('O = 29 + 1 = 30'), 'Each valid filter pass trims k − 1 = 2 pixels.'], check=30)
K.calc('m', 'A 224 × 224 input passes through a 7 × 7 filter with padding 3 and stride 2, as in the first layer of ResNet. How wide is the output?', '112', 'O = ⌊(W − k + 2P) ÷ S⌋ + 1.',
       ['W − k + 2P = 224 − 7 + 6 = 223.', '⌊223 ÷ 2⌋ = 111.', eq('O = 111 + 1 = 112'), 'Stride 2 roughly halves the size.'], check=112)
K.calc('m', 'The notebook calls cv2.GaussianBlur(image, (9, 9), 0). What σ does OpenCV use?', '1.7', 'σ = 0.3 × ((k − 1) × 0.5 − 1) + 0.8.',
       ['(k − 1) × 0.5 = 8 × 0.5 = 4.', '4 − 1 = 3, and 0.3 × 3 = 0.9.', eq('σ = 0.9 + 0.8 = 1.7')], check=1.7)
K.calc('m', 'Apply the notebook sharpening kernel [[0, −1, 0], [−1, 5, −1], [0, −1, 0]] to a pixel of value 100 whose four neighbours are each 80.', '180', 'Centre times 5, minus each of the four neighbours.',
       ['Centre: 5 × 100 = 500.', 'Neighbours: 4 × (−1 × 80) = −320.', eq('500 − 320 = 180'), 'The difference from the neighbours grew from 20 to 100. A flat region stays unchanged.'], check=180)
K.calc('h', 'The MSE between a clean and a filtered 8 bit image is 100. What is the PSNR in dB? Give two decimals.', '28.13', 'PSNR = 10 log<sub>10</sub>(255² ÷ MSE).',
       ['255² = 65,025.', '65,025 ÷ 100 = 650.25.', 'log<sub>10</sub> 650.25 ≈ 2.8131.', eq('PSNR ≈ 10 × 2.8131 ≈ 28.13 dB')], check=28.13, tol=0.006)
K.calc('h', 'How many multiplications does a 3 × 3 filter need on a 640 × 480 grey image with same size output?', '2764800', 'One multiplication per kernel weight per pixel.',
       ['Pixels: 640 × 480 = 307,200.', 'Weights per pixel: 3 × 3 = 9.', eq('307,200 × 9 = 2,764,800'), 'About 2.8 million per frame, or 83 million per second at 30 fps, which is why filters run on GPUs or in hardware.'], check=2764800)
K.calc('h', 'A 5 × 5 Gaussian is applied as two 1D passes instead of one 2D pass. By what factor does the work per pixel drop?', '2.5', 'Compare k² with 2k.',
       ['2D pass: 5 × 5 = 25 multiplications.', 'Two 1D passes: 5 + 5 = 10.', eq('25 ÷ 10 = 2.5'), 'The saving grows with k: for 9 × 9 it is 81 ÷ 18 = 4.5.'], check=2.5)
K.calc('x', 'A row of pixels is [20, 50, 30]. Filter the middle pixel with h = [−1, 0, 1] as correlation, then as true convolution (kernel flipped). What does convolution give?', '-10', 'Correlation lines up h with the pixels as written. Convolution uses h reversed.',
       ['Correlation: −1 × 20 + 0 × 50 + 1 × 30 = 10.', 'Flipped kernel: [1, 0, −1].', eq('Convolution: 1 × 20 + 0 × 50 − 1 × 30 = −10'), 'Same size, opposite sign. For symmetric kernels such as the mean and Gaussian the two operations agree.'], check=-10)

# ---------------------------------------------------------------- assignments
K.assign('convolve2d', 'm', 'Filter an image with zero padding',
         '<p>Write <code>filter2d(img, k)</code> for a 3 × 3 kernel <code>k</code>. Pad with zeros so the output has the same size as <code>img</code>. Compute g(y, x) = Σ<sub>i</sub> Σ<sub>j</sub> k[i][j] · f(y + i − 1, x + j − 1) and round each result to 2 decimals.</p>',
         '''
def filter2d(img, k):
    # your code here
    pass
''', [('filter2d([[0, 0, 0], [0, 9, 0], [0, 0, 0]], [[1/9] * 3] * 3)', [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]),
      ('filter2d([[1, 2], [3, 4]], [[0, 0, 0], [0, 1, 0], [0, 0, 0]])', [[1, 2], [3, 4]]),
      ('filter2d([[80, 80, 80], [80, 100, 80], [80, 80, 80]], [[0, -1, 0], [-1, 5, -1], [0, -1, 0]])[1][1]', 180),
      ('filter2d([[5, 5], [5, 5]], [[1, 1, 1], [1, 1, 1], [1, 1, 1]])', [[20, 20], [20, 20]])],
         '''
def filter2d(img, k):
    h, w = len(img), len(img[0])
    def px(y, x):
        return img[y][x] if 0 <= y < h and 0 <= x < w else 0
    out = []
    for y in range(h):
        row = []
        for x in range(w):
            s = 0
            for i in range(3):
                for j in range(3):
                    s += k[i][j] * px(y + i - 1, x + j - 1)
            row.append(round(s, 2))
        out.append(row)
    return out
''', 'Write a small helper that returns 0 for positions outside the image.',
         '<p>The last test shows the dark frame that zero padding creates: corner pixels see only 4 of 9 neighbours, so 5 × 4 = 20 instead of 45. Replicate padding avoids this.</p>')
K.assign('median3', 'e', 'Median filter on one window',
         '<p>Write <code>median3(patch)</code> that returns the median of a 3 × 3 patch (a list of three lists of three numbers).</p>',
         '''
def median3(patch):
    # your code here
    pass
''', [('median3([[10, 20, 10], [100, 20, 10], [10, 10, 20]])', 10), ('median3([[0, 255, 0], [255, 7, 255], [0, 255, 0]])', 7), ('median3([[1, 2, 3], [4, 5, 6], [7, 8, 9]])', 5)],
         '''
def median3(patch):
    values = sorted(v for row in patch for v in row)
    return values[4]
''', 'Flatten, sort and take index 4, the 5th of 9.',
         '<p>The second test is half salt and half pepper: four 0s, four 255s and a 7 in the middle, so the median is 7. A median filter needs more than half the window to be bad before it fails.</p>')
K.assign('outsize', 'e', 'Output size of a filter',
         '<p>Write <code>output_size(w, k, p=0, s=1)</code> that returns ⌊(w − k + 2p) ÷ s⌋ + 1.</p>',
         '''
def output_size(w, k, p=0, s=1):
    # your code here
    pass
''', [('output_size(32, 3)', 30), ('output_size(224, 7, 3, 2)', 112), ('output_size(7, 3, 0, 2)', 3), ('output_size(28, 5, 2)', 28)],
         '''
def output_size(w, k, p=0, s=1):
    return (w - k + 2 * p) // s + 1
''', 'Integer division with // does the floor for you.',
         '<p>The last test is same padding: with p = (k − 1) ÷ 2 and stride 1 the size never changes. CNNs use this so layers can be stacked without the image shrinking.</p>')
K.assign('psnr', 'm', 'Measure PSNR',
         '<p>Write <code>psnr(a, b)</code> for two 8 bit images of the same size. Return 10 log<sub>10</sub>(255² ÷ MSE) rounded to 2 decimals, or the string <code>"inf"</code> when the images are identical.</p>',
         '''
from math import log10

def psnr(a, b):
    # your code here
    pass
''', [('psnr([[0, 0], [0, 0]], [[10, 10], [10, 10]])', 28.13), ('psnr([[5, 6]], [[5, 6]])', 'inf'), ('psnr([[50, 50, 50], [50, 200, 50], [50, 50, 50]], [[60, 40, 50], [50, 220, 50], [50, 50, 40]])', 29.22)],
         '''
from math import log10

def psnr(a, b):
    diffs = [(x - y) ** 2 for ra, rb in zip(a, b) for x, y in zip(ra, rb)]
    mse = sum(diffs) / len(diffs)
    if mse == 0:
        return "inf"
    return round(10 * log10(255 ** 2 / mse), 2)
''', 'Collect the squared differences of matching pixels, then average them.',
         '<p>MSE 100 gives 28.13 dB, the worked problem above. The identical case would divide by zero, so it is checked first.</p>')

K.must('Noise models', 'Additive g = f + n (Gaussian, salt and pepper), multiplicative g = f(1 + n) (speckle). Gaussian → averaging or Gaussian filter, impulse → median, speckle → adaptive or median type, shot → denoising.')
K.must('Convolution', 'Slide a kernel, multiply and add. Output size ⌊(W − k + 2P) ÷ S⌋ + 1. True convolution flips the kernel, correlation does not.')
K.must('Smoothing', 'Mean (1/9)·ones, Gaussian with σ (OpenCV σ = 1.7 for 9 × 9), median for outliers. Lecture patch: mean 23.33, median 10.')
K.must('Sharpening', 'Lecture high pass (1/9)[[−1, −1, −1], [−1, 8, −1], [−1, −1, −1]] sums to 0. Notebook kernel [[0, −1, 0], [−1, 5, −1], [0, −1, 0]] sums to 1 and equals identity minus Laplacian.')
K.must('Frequency view', 'g = h ∗ f ⟺ G = H · F. Low pass blurs, high pass keeps edges. Noise is added on purpose for robustness tests and is the core of denoising autoencoders and diffusion models.')

T = K.topic(
    slug='noise-filtering', topic='filtering', step=(2, 'Images as numbers', 'cv-image-basics', 'How pictures are stored, coloured, compressed, measured and cleaned before any recognition happens.', 'School and college'),
    title='Noise, convolution and filtering', short='Noise and filtering', badge='2.3', minutes=45,
    lead='Name the four kinds of noise, slide a kernel by hand, compare mean, Gaussian and median filters, and see why sharpening helps edges but also boosts noise, using the same kernels as the lectures and the project notebook.',
    desc='Gaussian, impulse, speckle and Poisson noise, convolution and padding, output size, mean, Gaussian and median filters, the Laplacian and unsharp masking, PSNR and the frequency view.',
    summary='Noise models, convolution and output size, mean, Gaussian and median smoothing, sharpening kernels, PSNR and the convolution theorem.',
    keywords=['noise', 'salt and pepper', 'speckle', 'convolution', 'kernel', 'padding', 'stride', 'mean filter', 'Gaussian blur', 'median filter', 'sharpening', 'Laplacian', 'unsharp masking', 'PSNR', 'frequency domain'],
    recap='<p>Every image carries noise, and its pattern decides the filter. A linear filter is a kernel slid over the image. Low pass kernels sum to 1 and blur, high pass kernels sum to 0 and find edges, and sharpening adds the high pass part back. The median is the outlier proof choice for impulse noise.</p>')
