# Chapter 13: segmentation architectures. FCN and convolutionalisation, FCN-32s/16s/8s, nearest, bilinear and
# transposed convolution upsampling, encoder-decoder and the bottleneck, autoencoders and VAEs, skip connections,
# U-Net sizes and parameters, dilated convolution, ASPP and DeepLab, choosing an architecture from failures.
# Source: lectures 7 and 8, chapters 5 to 9.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('tconv', r'''
# Transposed convolution by scatter and add
x = [[1, 2], [3, 4]]
k = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
s = int(input("stride: "))

n, kk = len(x), len(k)
size = (n - 1) * s + kk
out = [[0] * size for _ in range(size)]
for i in range(n):
    for j in range(n):
        for a in range(kk):
            for b in range(kk):
                out[i * s + a][j * s + b] += x[i][j] * k[a][b]
print("output", size, "x", size)
for row in out:
    print(row)
''', stdin='2\n')

K.code('unetsize', r'''
# Trace the sizes through a U-Net with unpadded (valid) 3 x 3 convolutions
size = int(input("input tile size: "))
depth = 4

skips = []
for level in range(depth):
    size -= 4                       # two valid 3 x 3 convs remove 2 pixels each
    skips.append(size)
    print("encoder level", level + 1, "skip", size)
    size //= 2                      # 2 x 2 max pool
size -= 4
print("bottleneck", size)
for level in reversed(range(depth)):
    size *= 2                       # 2 x 2 up-convolution
    print("crop skip", skips[level], "to", size)
    size -= 4
print("output", size)
''', stdin='572\n')

K.code('dilated', r'''
# Receptive field of a stack of dilated 3 x 3 convolutions (stride 1)
rates = [int(v) for v in input("dilation rates: ").split()]

r = 1
for d in rates:
    k_eff = 2 * d + 1
    r += 2 * d
    print("rate", d, " covers", k_eff, "x", k_eff, " field so far", r)
print("plain 3 x 3 layers would give", 1 + 2 * len(rates))
''', stdin='1 2 4 8\n')

K.lesson('fcn', 'FCN: turning a classifier into a segmenter', f'''
<p>A classifier ends with global pooling or a fully connected layer and one label. A <b>fully convolutional network</b> (FCN, Long and colleagues, 2015) keeps a spatial grid to the end, so it outputs class scores at every location. The lecturer\'s caution: the first dense map is coarse. A 256 × 256 image gives only a small score map, which must then be upsampled to 256 × 256.</p>
{deep('A fully connected layer is a convolution', '<p>A fully connected layer on a 7 × 7 × 512 map flattens it to 25,088 numbers and multiplies by a 25,088 × 4,096 matrix. A 7 × 7 convolution with 512 input channels and 4,096 filters, applied at the one place where it fits, computes the same sums with the same weights: 7 · 7 · 512 · 4,096 = 102,760,448 of them.</p><p>The difference shows on a larger input. On a 14 × 14 × 512 map the convolution slides and gives (14 − 7) + 1 = 8, an 8 × 8 grid of scores, while the fully connected layer only accepts 7 × 7. So any classifier can be converted into a dense predictor.</p>')}
{table(['Variant', 'Uses', 'Map for 256 × 256', 'Final upsampling', 'Result'], [
    ['FCN-32s', 'only the 1/32 map', '8 × 8', '×32', 'strong meaning, coarse boundaries'],
    ['FCN-16s', 'adds the 1/16 map', '16 × 16', '×16', 'better spatial detail'],
    ['FCN-8s', 'adds the 1/8 map', '32 × 32', '×8', 'even better boundaries']])}
<p>The lecturer: deeper layers give meaning, early layers give refined location, and we need to combine them. FCN-16s and FCN-8s add earlier score maps to the upsampled deep one. That is the start of the skip connection idea.</p>
{note('A smaller final jump means less blur. For a 512 × 512 image FCN-8s predicts on a 64 × 64 grid, four times finer in each direction than the 16 × 16 grid of FCN-32s.', 'tip')}
''', kw=['FCN', 'fully convolutional network', 'convolutionalisation', 'fully connected as convolution', 'FCN-32s', 'FCN-16s', 'FCN-8s', 'coarse score map'])

K.lesson('upsampling', 'Three ways to make a map bigger', f'''
<p>The literature went from nearest neighbour to bilinear interpolation to learned upsampling.</p>
{table(['Method', 'How', 'Good', 'Limit'], [
    ['Nearest neighbour', 'Copy each value into an F × F block', 'Simple, fast, keeps the original values', 'Blocky boundaries, learns nothing'],
    ['Bilinear', 'Weighted average of the 4 nearest inputs', 'Smooth', 'Only blends, does not know where a boundary lies'],
    ['Transposed convolution', 'Learned kernel spread over the output', 'Learns shapes, such as a road edge against a person edge', 'Can still fail if the encoder lost the information']])}
{viz('upsample')}
{steps('Bilinear 2 × 2 → 4 × 4 with values 0, 100, 100, 200', [
    'Half pixel centres: output pixel i sits at input coordinate (i + 0.5) ÷ 2 − 0.5, so −0.25, 0.25, 0.75, 1.25, clamped to 0, 0.25, 0.75, 1.',
    'The map is f = 100x + 100y, which is linear, so bilinear reproduces it exactly.',
    'Rows: 0, 25, 75, 100 | 25, 50, 100, 125 | 75, 100, 150, 175 | 100, 125, 175, 200.',
    'With align corners the first row would be 0, 33, 67, 100. Frameworks differ, so check the setting.'])}
<h3>Transposed convolution</h3>
{fx('Output size', '<i>H</i><sub>out</sub> = (<i>H</i><sub>in</sub> − 1) · <i>s</i> − 2<i>p</i> + <i>k</i> + <i>p</i><sub>out</sub>', 's stride, p padding, k kernel, p<sub>out</sub> extra output padding. With H<sub>in</sub> = 16, k = 4, s = 2, p = 1 the size doubles to 32.', key=True)}
{viz('tconv')}
{steps('2 × 2 input, 3 × 3 kernel, stride 2', [
    'Input [[1, 2], [3, 4]], kernel [[1, 0, 1], [0, 1, 0], [1, 0, 1]]. Output size (2 − 1) × 2 + 3 = 5.',
    'Each input value scales the whole kernel and is added at (i · 2, j · 2).',
    'Placements overlap in row and column 2. The centre gets 1 + 2 + 3 + 4 = 10, because all four corner weights land there.',
    'Output rows: [1, 0, 3, 0, 2], [0, 1, 0, 2, 0], [4, 0, 10, 0, 6], [0, 3, 0, 4, 0], [3, 0, 7, 0, 4].'])}
{code('tconv')}
{deep('Why it is called transposed', '<p>An ordinary convolution is a linear map y = Cx, where each row of the matrix C holds the kernel at one output place. Back-propagation sends gradients back with Cᵀ. Using Cᵀ in the forward direction, y = Cᵀx, maps the small size back to the large one with the same connection pattern. It is not an inverse: it restores the size, not the values.</p>')}
{note('When the kernel size is not divisible by the stride, some output cells receive more overlapping contributions than others, which prints a checkerboard pattern into the mask. Fixes: kernel = 2 × stride (k = 4, s = 2), or resize with nearest or bilinear and then apply a normal convolution, or use sub-pixel convolution (PixelShuffle).', 'warn')}
<p>A student asked whether transposed convolution causes overfitting. The lecturer: overfitting is a different matter. It happens when the data is limited and the model is big, in any architecture. Detect it by comparing training and validation scores.</p>
''', kw=['upsampling', 'nearest neighbour', 'bilinear', 'align corners', 'half pixel', 'transposed convolution', 'deconvolution', 'checkerboard artefacts', 'PixelShuffle', 'resize convolution', 'overfitting'])

K.lesson('encdec', 'Encoder, decoder and skip connections', f'''
{table(['', 'Encoder', 'Decoder'], [
    ['Resolution', 'reduces', 'restores'],
    ['Receptive field', 'grows', ''],
    ['Produces', 'high level meaning', 'dense class scores'],
    ['Answers', 'What is present?', 'Where exactly?']])}
<p>The slide: compress the scene into meaning, then expand meaning back into a pixel map. The output is not a photo. It is a class map.</p>
{steps('Track the tensor shape', [
    'Input 256 × 256 × 3, encoder feature 64 × 64 × 128, bottleneck 16 × 16 × 512.',
    'A 1 × 1 classifier on the bottleneck gives 16 × 16 × C. With C = 7 that is 16 × 16 × 7.',
    'The decoder upsamples ×16 to 256 × 256, then argmax gives the mask.',
    'The 1 × 1 head alone has 512 × 7 + 7 = 3,591 parameters.'])}
<h3>The bottleneck</h3>
<p>Low resolution, many channels, a large receptive field. It recognises what is present and uses context to resolve ambiguity, but its spatial detail is coarse. How far to shrink, 32 × 32, 16 × 16 or 8 × 8, is a hyperparameter the lecturer said you find by experiment.</p>
{deep('Side topic: autoencoders and VAEs', '<p>An <b>autoencoder</b> maps x to a code z and back to x̂, trained on the reconstruction error. A <b>variational autoencoder</b> outputs a mean μ and variance σ² for each latent feature, and samples from that distribution, which lets it generate varied new images. Its training adds a KL term that keeps each distribution close to N(0, 1):</p><p>KL = ½ (μ² + σ² − 1 − ln σ²). For μ = 0.5 and σ = 0.8 this is ½(0.25 + 0.64 − 1 − ln 0.64) ≈ 0.168. It is 0 exactly when μ = 0 and σ = 1.</p><p>Sampling is made differentiable with z = μ + σ ε, where ε is drawn from N(0, 1). An autoencoder\'s target is its own input. A segmentation network\'s target is a mask. The shape is shared, the purpose is not.</p>')}
<h3>Why plain encoder-decoders fail, and the fix</h3>
<p>The lecturer: if something is missing in the encoder, the decoder cannot reconstruct it. So build a bridge from each high resolution encoder level to the decoder level of the same size. These are <b>skip connections</b>, and they carry WHERE information: edges, local texture, exact position and small structures lost after pooling.</p>
{table(['Fusion', 'How', 'Cost (128 × 128 map, 64 + 64 channels, 3 × 3 conv to 64)'], [
    ['Concatenate (U-Net)', 'Stack both feature sets, the next conv learns how to mix them', '3 · 3 · 128 · 64 + 64 = 73,792'],
    ['Add (FCN, FPN, ResNet)', 'Shapes must match, both go into one shared space', '3 · 3 · 64 · 64 + 64 = 36,928']])}
<p>The lecturer\'s view: fusion is also driven by science, so test which one your domain needs. An executive student asked for a framework that pinpoints what to change. Her answer: watch where the model fails and design for it. Neural architecture search automates part of this, but its search space still encodes human expertise.</p>
''', kw=['encoder', 'decoder', 'bottleneck', 'tensor shape', 'autoencoder', 'variational autoencoder', 'VAE', 'KL divergence', 'reparameterisation', 'skip connection', 'concatenation', 'addition', 'neural architecture search'])

K.lesson('unet', 'U-Net', f'''
<p><b>U-Net</b> (Ronneberger and colleagues, 2015) was built for cell images in microscopy, where boundaries must be precise and labelled data is scarce. It is a symmetric encoder-decoder that copies high resolution encoder maps into the decoder at every level. The lecturer stressed that a large share of medical papers build on it. Its descendants include U-Net++, Attention U-Net, 3D U-Net and nnU-Net, which configures a U-Net for a new dataset automatically. U-Net also sits inside diffusion image generators as the denoiser.</p>
{table(['Part', 'What happens'], [
    ['Contracting path', 'Two 3 × 3 convs, then 2 × 2 max pool. Resolution halves, channels double, features become more semantic.'],
    ['Bottleneck', 'The most compressed map: strongest context, coarsest detail.'],
    ['Expanding path', '2 × 2 up-convolution, concatenate the skip, two 3 × 3 convs. A final 1 × 1 conv gives class scores.'],
    ['Skips', 'U-Net does not wait until the end to recover detail. It injects detail at every decoder stage.']])}
{viz('unet')}
{steps('Why the original output is smaller than its input', [
    'The 2015 paper used unpadded 3 × 3 convs, each removing 2 pixels. Start with a 572 × 572 tile.',
    'Encoder: 572 → 568 (skip) → 284 → 280 (skip) → 140 → 136 (skip) → 68 → 64 (skip) → 32.',
    'Bottleneck: 32 → 28. Up to 56, crop the 64 skip to 56, convs to 52.',
    'Up to 104 (crop 136), convs to 100. Up to 200 (crop 280), convs to 196. Up to 392 (crop 568), convs to 388.',
    'Large images are processed as overlapping tiles. Modern code pads, so sizes go exactly 256, 128, 64, 32, 16 and back.'])}
{code('unetsize')}
{steps('Where the 31 million parameters sit', [
    'A 3 × 3 conv from C<sub>in</sub> to C<sub>out</sub> has 9 C<sub>in</sub> C<sub>out</sub> + C<sub>out</sub> parameters. The first block (1 → 64 → 64) has 640 + 36,928 = 37,568.',
    'The deepest block (512 → 1024 → 1024) has 4,719,616 + 9,438,208 = 14,157,824, almost half the network.',
    'Decoder convs take twice the channels because of concatenation. The level 4 decoder conv takes 1,024 in and gives 512: 9 · 1,024 · 512 + 512 = 4,719,104.',
    'All convs, up-convs and the final 1 × 1 (1 input channel, 2 classes) add to 31,030,658, about 31.0 M.'])}
<h3>The slide\'s activity</h3>
{table(['Question', 'Answer', 'Reason'], [
    ['Which feature is from an early layer?', 'A: sharp edges, local texture, exact position', 'Those live at high resolution'],
    ['Which is from the bottleneck?', 'B: object meaning, scene context, coarse layout', 'Deep semantics'],
    ['Which should receive a skip?', 'C, the upsampled semantic map, receives A', 'C needs its boundaries refined'],
    ['Why does the decoder need A and B?', 'A is where, B is what', 'Masks need local edges plus global context']])}
{note('Teaching sentence from the slide: deep features say this region is probably a car, skip features decide the car boundary is exactly here.', 'exam')}
''', kw=['U-Net', 'contracting path', 'expanding path', 'symmetric', 'valid convolution', '572 to 388', 'overlap tile', 'crop', 'parameters', 'nnU-Net', 'medical segmentation'])

K.lesson('deeplab', 'Dilated convolution, ASPP and DeepLab', f'''
<p>Even with skips, U-Net struggles when objects appear at very different scales. Good segmentation balances two problems.</p>
{table(['Boundary problem', 'Context problem'], [
    ['Edges may be thin or irregular', 'A grey patch could be road, wall or roof'],
    ['Nearby classes may look alike', 'Wide scene context resolves it'],
    ['The mask can leak outside the object', 'Deep features and large receptive fields help'],
    ['High resolution features help', 'But enlarging the receptive field has a cost']])}
<p>Ways to see more context: bigger kernels (parameters grow with k²), more layers, more downsampling (loses resolution, the very problem), or <b>dilation</b>, which is free in parameters and keeps resolution.</p>
{fx('Dilated 3 × 3 kernel', '<i>k</i><sub>eff</sub> = <i>k</i> + (<i>k</i> − 1)(<i>r</i> − 1) = 2<i>r</i> + 1', 'r = 1, 2, 4, 6, 12, 18 cover 3, 5, 9, 13, 25 and 37 cells. Always 9 weights. Padding r keeps the map size.', key=True)}
{viz('dilation')}
{steps('Stacking dilations 1, 2, 4, 8', [
    'Each layer adds 2r to the receptive field.',
    'r = 1 + 2(1 + 2 + 4 + 8) = 31, against 9 for four plain layers.',
    'A 256 → 256 channel layer has 589,824 weights for any rate, and the same number of multiply adds.'])}
{code('dilated')}
<p>A student asked whether the dots in the dilated picture are pixels. Yes: the taps read ordinary neighbouring pixels r apart, and the pixels in the gaps are simply not used. Another asked whether the network could choose its own dilation. The lecturer said it is a hyperparameter in classic models. Deformable convolution (Dai and colleagues, 2017) does learn per pixel sampling offsets, which is close to that idea.</p>
<h3>ASPP and DeepLab</h3>
<p><b>Atrous spatial pyramid pooling</b> runs several dilated branches in parallel on the same map: a 1 × 1 conv, three 3 × 3 convs with rates 6, 12 and 18, and an image level pooling branch. Their outputs are concatenated and mixed by a 1 × 1 conv. At output stride 16 the three dilated branches see about 13 × 16 = 208, 25 × 16 = 400 and 37 × 16 = 592 input pixels across. The slide\'s picture: several observers with different zoom levels describing the same map.</p>
<p><b>DeepLabv3+</b> adds a light decoder: the ASPP output (stride 16) is upsampled ×4, concatenated with a reduced low level map at stride 4, refined and upsampled ×4 again. Context for WHAT, decoder detail for WHERE.</p>
{table(['Design', 'Key idea', 'Remember it as'], [
    ['FCN', 'dense class score maps', 'the first classifier to segmenter conversion'],
    ['Encoder-decoder', 'compress then upsample', 'the general shape for pixel prediction'],
    ['U-Net', 'skip connections at every level', 'strong boundaries, the medical baseline'],
    ['DeepLab', 'dilated conv and ASPP', 'multi-scale context with dense features']])}
''', kw=['dilated convolution', 'atrous', 'effective kernel', 'gridding', 'ASPP', 'DeepLab', 'DeepLabv3+', 'output stride', 'multi-scale context', 'deformable convolution'])

K.lesson('choose', 'Choosing an architecture from its failures', f'''
<p>The slide: architecture design is not arbitrary, it is driven by segmentation failures. Ask four questions. Do we need small object accuracy? Do boundaries matter? Do we need global context? What are the latency and memory limits?</p>
{table(['Application', 'Sensible start', 'Why'], [
    ['Medical tumour boundary', 'U-Net or encoder-decoder', 'Boundary accuracy with little data'],
    ['Street scenes', 'DeepLab style or a transformer', 'Many scales and much context'],
    ['Drone or phone', 'Lightweight encoder-decoder', 'Latency and memory'],
    ['Satellite land cover', 'Multi-scale context model', 'Large regions and very small structures']])}
{table(['Failure', 'Architectural fix'], [
    ['Blurry object boundaries', 'Skip connections, a high resolution decoder'],
    ['Small object missed', 'High resolution features, multi-scale design'],
    ['Road confused with sidewalk', 'Broader context, DeepLab style modules'],
    ['Thin structure disappears', 'Less aggressive downsampling, more skips'],
    ['Object scale varies a lot', 'ASPP, feature pyramids']])}
<h3>Three scenarios from the slides</h3>
<ol>
<li><b>95% pixel accuracy, but pedestrians and cyclists are missed.</b> Not a good model. Road, sky and buildings dominate the pixels. Check per class IoU, mIoU, pedestrian recall, the confusion matrix and failures at night, under occlusion and at distance.</li>
<li><b>FCN-32s finds the person but misses arms and legs.</b> The 8 × 8 map knows person but not the outline, and one ×32 jump makes a blob. Fuse earlier features: FCN-16s or 8s, or U-Net skips.</li>
<li><b>A tumour covers 2% of pixels, and predicting all background scores 98%.</b> Tumour recall and Dice are 0. Measure Dice or IoU on the tumour, and weight the loss: w<sub>c</sub> = N ÷ (C · n<sub>c</sub>) gives background 100 ÷ (2 × 98) = 0.510 and tumour 100 ÷ (2 × 2) = 25, so both classes now carry half the loss.</li>
</ol>
{note('The class answered context for road against sidewalk confusion, and both slide decks agree. The recording has the lecturer saying boundary, which is most likely a transcription slip. In exams: road and sidewalk confusion is a context problem.', 'exam')}
{ladder(
    '<p>To label every pixel, a network first shrinks the image to understand what is in it, then grows it back to full size. Shortcuts carry fine detail from the early layers to the late ones so edges stay sharp.</p>',
    '<p>FCN replaces the classifier head with convolutions. Upsampling uses nearest, bilinear or learned transposed convolution. U-Net copies each encoder level into the decoder. DeepLab uses dilated convolutions, k<sub>eff</sub> = 2r + 1, and ASPP to see many scales without losing resolution.</p>',
    '<p>Transposed convolution is the adjoint Cᵀ of a convolution, with H<sub>out</sub> = (H<sub>in</sub> − 1)s − 2p + k + p<sub>out</sub>. U-Net parameters concentrate at the bottleneck. Concatenation costs twice the input channels of addition. Dilation stacks risk gridding, which mixed or parallel rates avoid.</p>',
    '<p>HRNet keeps a high resolution branch all the way through. Attention U-Net gates the skips, and nnU-Net automates configuration and is a strong medical baseline. Transformer encoders such as SegFormer and Swin, and mask classification heads (Mask2Former), now lead most benchmarks, covered in the vision and language step.</p>')}
''', kw=['architecture choice', 'failure analysis', 'boundary', 'small objects', 'context', 'class weights', 'pixel accuracy trap', 'scenario', 'FCN-32s rough masks', 'tumour 2 percent'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does FCN-32s predict for a 256 × 256 image before upsampling?', ['256 × 256', '32 × 32', '8 × 8', '1 × 1'], 2,
       '256 ÷ 32.', 'One thirty-second of the size, then a ×32 upsampling.')
K.quiz('e', 'Nearest neighbour upsampling ×2 turns one value into', ['1 value', '2 values', '4 values', '9 values'], 2,
       'A 2 × 2 block.', 'Each value is copied into an F × F block.')
K.quiz('e', 'Skip connections in U-Net mainly carry', ['Class names', 'WHERE information: edges, texture, exact position', 'The loss', 'Random noise'], 1,
       'From early, high resolution layers.', 'The decoder already has the meaning. It needs the detail.')
K.quiz('m', 'Why may a fully connected layer be replaced by a convolution?', ['It is always faster', 'A conv with the full map size as its kernel computes the same sums, and then slides on bigger inputs to give a score map', 'Convs have no weights', 'FC layers cannot be trained'], 1,
       'Same weights, same sums.', 'That is how FCN converts classifiers into dense predictors.')
K.quiz('m', 'Which resizing is right for a label mask?', ['Bilinear', 'Bicubic', 'Nearest neighbour', 'Any of them'], 2,
       'IDs are not intensities.', 'Blending class 1 and 3 gives 2, a class that is not there.')
K.quiz('m', 'What causes checkerboard artefacts in transposed convolution?', ['Too many classes', 'Kernel size not divisible by stride, so some output cells get more overlapping contributions', 'Bilinear resizing', 'Using SoftMax'], 1,
       'Count the placements per cell.', 'Use k = 2s, or resize then convolve.')
K.quiz('m', 'A dilated 3 × 3 kernel with rate 4 has how many weights?', ['9', '25', '81', '16'], 0,
       'Spacing changes, count does not.', 'It covers 9 × 9 with 9 taps.')
K.quiz('h', 'Why is the original U-Net output 388 × 388 for a 572 × 572 input?', ['Pooling rounds down', 'Every unpadded 3 × 3 conv removes 2 pixels, and skips are cropped to match', 'The final layer crops', 'It uses stride 2 convs'], 1,
       'Valid convolutions.', 'Modern code pads, so output equals input.')
K.quiz('h', 'Concatenation against addition for a skip. Which is true?', ['Addition needs more parameters', 'Concatenation keeps both feature sets and lets the next conv learn the mix, at about twice the cost', 'They are identical', 'Addition cannot be trained'], 1,
       'Count the input channels of the next conv.', '73,792 against 36,928 in the lecture example.')
K.quiz('h', 'What does ASPP add over a single dilated conv?', ['A classifier', 'Several dilation rates in parallel, so one layer sees many scales', 'Bigger stride', 'Batch norm'], 1,
       'Several observers at different zoom levels.', 'DeepLabv3 uses rates 6, 12, 18, a 1 × 1 branch and image pooling.')
K.quiz('x', 'A model confuses road and sidewalk. Which kind of problem is it, and the fix?', ['Boundary, add skips', 'Context or class confusion, add broader context such as ASPP or attention', 'Data leakage', 'Checkerboard'], 1,
       'Similar texture, different layout.', 'Sidewalks flank roads. Scene context resolves it.')
K.quiz('x', 'The KL term of a VAE is zero when', ['μ = 1, σ = 0', 'μ = 0, σ = 1', 'σ is large', 'Always'], 1,
       'KL = ½(μ² + σ² − 1 − ln σ²).', 'Only the standard normal itself has zero divergence from the standard normal.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the effective size of a 3 × 3 kernel with dilation 4?', '9', 'k<sub>eff</sub> = 2r + 1.',
       ['r = 4.', '2 × 4 + 1.', eq('k<sub>eff</sub> = 9, so it covers 9 × 9')], check=9)
K.calc('e', 'FCN-8s on a 512 × 512 image. What is the side of its score map?', '64', '512 ÷ 8.',
       ['Stride 8.', '512 ÷ 8.', eq('64, so a 64 × 64 map and ×8 upsampling')], check=64)
K.calc('e', 'A 1 × 1 head maps 512 channels to 7 classes with biases. How many parameters?', '3591', 'C<sub>in</sub> × C<sub>out</sub> + C<sub>out</sub>.',
       ['Weights 512 × 7 = 3,584.', 'Biases 7.', eq('3,591')], check=3591)
K.calc('m', 'Transposed conv with H<sub>in</sub> = 16, k = 4, s = 2, p = 1. What is H<sub>out</sub>?', '32', '(H<sub>in</sub> − 1)s − 2p + k.',
       ['(16 − 1) × 2 = 30.', '30 − 2 + 4.', eq('H<sub>out</sub> = 32')], check=32)
K.calc('m', 'In the lecture transposed conv (input [[1, 2], [3, 4]], corner kernel, stride 2), what is the centre value?', '10', 'All four corner weights land on the centre.',
       ['Input 1 adds k(2, 2) = 1.', 'Inputs 2, 3 and 4 add their corner weights, all 1.', eq('1 + 2 + 3 + 4 = 10')], check=10)
K.calc('m', 'Four 3 × 3 layers with dilations 1, 2, 4 and 8 (stride 1). What is the receptive field?', '31', 'Each adds 2r.',
       ['Sum of rates 15.', '2 × 15 = 30.', eq('r = 1 + 30 = 31')], check=31)
K.calc('m', 'Bilinear ×2 of [[10, 30], [50, 70]] with half pixel centres. What is the value at the second row, second column? ', '25', 'The map is f = 10 + 20x + 40y.',
       ['Output index 1 maps to input coordinate 0.25 in both directions.', 'f = 10 + 20 × 0.25 + 40 × 0.25.', eq('10 + 5 + 10 = 25')], check=25)
K.calc('h', 'A skip doubles the input of a 3 × 3 conv on a 128 × 128 map: 64 + 64 channels in, 64 out, with biases. How many parameters?', '73792', '9 × C<sub>in</sub> × C<sub>out</sub> + C<sub>out</sub>.',
       ['C<sub>in</sub> = 128.', '9 × 128 × 64 = 73,728.', eq('73,728 + 64 = 73,792'), 'Adding instead of concatenating gives 36,928.'], check=73792)
K.calc('h', 'A U-Net decoder level gets 128 up-convolved plus 128 skip channels, then two 3 × 3 convs to 128. How many parameters?', '442624', 'First conv 256 → 128, second 128 → 128.',
       ['9 × 256 × 128 + 128 = 295,040.', '9 × 128 × 128 + 128 = 147,584.', eq('295,040 + 147,584 = 442,624')], check=442624)
K.calc('h', 'ASPP rate 12 on a stride 16 map. About how many input pixels across does the branch see?', '400', 'k<sub>eff</sub> × stride.',
       ['k<sub>eff</sub> = 2 × 12 + 1 = 25 cells.', 'Each cell is 16 pixels.', eq('25 × 16 = 400')], check=400)
K.calc('x', 'VAE with μ = 0.5 and σ = 0.8. What is KL(q ‖ N(0, 1))? Give three decimals.', '0.168', '½(μ² + σ² − 1 − ln σ²).',
       ['μ² + σ² − 1 = 0.25 + 0.64 − 1 = −0.11.', 'ln 0.64 ≈ −0.446.', eq('½(−0.11 + 0.446) ≈ 0.168')], check=0.5 * (0.25 + 0.64 - 1 + 0.4462871), tol=0.0006)
K.calc('x', 'A 2% tumour in 100 pixels. With w<sub>c</sub> = N ÷ (C n<sub>c</sub>) and C = 2, what is the tumour weight?', '25', 'N = 100, n<sub>tumour</sub> = 2.',
       ['C × n = 2 × 2 = 4.', '100 ÷ 4.', eq('w = 25'), 'Background gets 100 ÷ 196 ≈ 0.510, so both classes carry about 50 units.'], check=25)

# ---------------------------------------------------------------- assignments
K.assign('tconv', 'm', 'Transposed convolution',
         '<p>Write <code>tconv(x, k, s)</code> for square lists <code>x</code> (n × n) and <code>k</code> (m × m) with stride <code>s</code> and no padding. Return the output grid of size (n − 1)s + m.</p>',
         '''
def tconv(x, k, s):
    # your code here
    pass
''', [('tconv([[1, 2], [3, 4]], [[1, 0, 1], [0, 1, 0], [1, 0, 1]], 2)', [[1, 0, 3, 0, 2], [0, 1, 0, 2, 0], [4, 0, 10, 0, 6], [0, 3, 0, 4, 0], [3, 0, 7, 0, 4]]),
      ('tconv([[1, 2], [3, 4]], [[1, 1], [1, 1]], 2)', [[1, 1, 2, 2], [1, 1, 2, 2], [3, 3, 4, 4], [3, 3, 4, 4]]),
      ('tconv([[5]], [[1, 2], [3, 4]], 3)', [[5, 10], [15, 20]])],
         '''
def tconv(x, k, s):
    n, m = len(x), len(k)
    size = (n - 1) * s + m
    out = [[0] * size for _ in range(size)]
    for i in range(n):
        for j in range(n):
            for a in range(m):
                for b in range(m):
                    out[i * s + a][j * s + b] += x[i][j] * k[a][b]
    return out
''', 'Four nested loops: input row, input column, kernel row, kernel column. Add into out[i * s + a][j * s + b].',
         '<p>The second test shows that a 2 × 2 kernel of ones with stride 2 is exactly nearest neighbour upsampling.</p>')
K.assign('unet', 'm', 'U-Net output size',
         '<p>Write <code>unet_out(n, depth=4)</code> for a U-Net with unpadded convs: each level does two 3 × 3 convs (−4) and a 2 × 2 pool (÷2), the bottleneck does −4, and each decoder level doubles and then does −4. Return the output size, or −1 if any map is odd before pooling or the size drops to 0 or below.</p>',
         '''
def unet_out(n, depth=4):
    # your code here
    pass
''', [('unet_out(572)', 388), ('unet_out(570)', -1), ('unet_out(572, 3)', 484), ('unet_out(20)', -1)],
         '''
def unet_out(n, depth=4):
    for _ in range(depth):
        n -= 4
        if n <= 0 or n % 2:
            return -1
        n //= 2
    n -= 4
    if n <= 0:
        return -1
    for _ in range(depth):
        n = n * 2 - 4
    return n if n > 0 else -1
''', 'Follow the sizes level by level and check before each pooling.',
         '<p>570 fails: 566 halves to 283, two convs give 279, which is odd at the next pooling. The paper chose 572 so every pooling gets an even size.</p>')
K.assign('bilinear_up', 'h', 'Bilinear upsampling',
         '<p>Write <code>upsample(m, f)</code> that enlarges a grid by an integer factor f with bilinear interpolation and half pixel centres: output index i maps to input coordinate (i + 0.5) ÷ f − 0.5, clamped to the valid range. Round each value to 1 decimal.</p>',
         '''
def upsample(m, f):
    # your code here
    pass
''', [('upsample([[0, 100], [100, 200]], 2)', [[0.0, 25.0, 75.0, 100.0], [25.0, 50.0, 100.0, 125.0], [75.0, 100.0, 150.0, 175.0], [100.0, 125.0, 175.0, 200.0]]),
      ('upsample([[10, 30], [50, 70]], 2)', [[10.0, 15.0, 25.0, 30.0], [20.0, 25.0, 35.0, 40.0], [40.0, 45.0, 55.0, 60.0], [50.0, 55.0, 65.0, 70.0]]),
      ('upsample([[7]], 2)', [[7.0, 7.0], [7.0, 7.0]])],
         '''
def upsample(m, f):
    h, w = len(m), len(m[0])
    def src(i, n):
        return min(max((i + 0.5) / f - 0.5, 0), n - 1)
    out = []
    for r in range(h * f):
        y = src(r, h)
        y0 = int(y)
        y1 = min(y0 + 1, h - 1)
        v = y - y0
        row = []
        for c in range(w * f):
            x = src(c, w)
            x0 = int(x)
            x1 = min(x0 + 1, w - 1)
            u = x - x0
            val = (1 - u) * (1 - v) * m[y0][x0] + u * (1 - v) * m[y0][x1] + (1 - u) * v * m[y1][x0] + u * v * m[y1][x1]
            row.append(round(float(val), 1))
        out.append(row)
    return out
''', 'Map each output row and column to a fractional input coordinate, then blend the four neighbours as in chapter 5.3.',
         '<p>Both test maps are linear, so bilinear reproduces them exactly. A 1 × 1 map stays constant.</p>')

K.must('FCN', 'An FC layer equals a conv with the map size as kernel, so classifiers become dense predictors. FCN-32s, 16s and 8s predict at 1/32, 1/16 and 1/8 and fuse earlier maps.')
K.must('Upsampling', 'Nearest copies, bilinear blends (0, 25, 75, 100 for the lecture map), transposed conv learns. H<sub>out</sub> = (H<sub>in</sub> − 1)s − 2p + k. Use k = 2s to avoid checkerboards. Masks: nearest only.')
K.must('Encoder-decoder and skips', 'Encoder: what. Decoder: where. Bottleneck: strongest context, coarsest detail. Skips carry WHERE. Concat costs about twice addition (73,792 against 36,928).')
K.must('U-Net', 'Contracting path, bottleneck, expanding path, skip at every level. Original 572 → 388 with valid convs, 31.0 M parameters, about half in the bottleneck.')
K.must('DeepLab', 'Dilated 3 × 3: k<sub>eff</sub> = 2r + 1, 9 weights, padding r. Rates 1, 2, 4, 8 give a field of 31. ASPP: rates 6, 12, 18 + 1 × 1 + pooling. v3+ adds a decoder at stride 4.')

T = K.topic(
    slug='segmentation-architectures', topic='seg-architectures', step=(6, 'Understanding every pixel', 'cv-segmentation', 'Semantic segmentation from the output tensor to modern architectures, losses, metrics and debugging.', 'College and masters'),
    title='Segmentation architectures', short='FCN, U-Net and DeepLab', badge='6.2', minutes=60,
    lead='Follow the line of designs that turned classifiers into pixel labellers: FCN, learned upsampling, encoder-decoders with skip connections, U-Net, and DeepLab with dilated convolution and ASPP. Each one fixes a specific failure of the one before.',
    desc='Fully convolutional networks, FCN-32s to 8s, nearest, bilinear and transposed convolution upsampling, checkerboard artefacts, the bottleneck, autoencoders and VAEs, skip connections, U-Net sizes and parameters, dilated convolution, ASPP, DeepLabv3+ and choosing a model from failures.',
    summary='FCN, upsampling and transposed convolution, encoder-decoders and skip connections, U-Net, dilated convolution, ASPP and DeepLab.',
    keywords=['FCN', 'U-Net', 'DeepLab', 'ASPP', 'dilated convolution', 'atrous', 'transposed convolution', 'upsampling', 'skip connection', 'encoder decoder', 'bottleneck', 'VAE'],
    recap='<p>FCN made classifiers dense. Upsampling restores size but not lost detail, so skip connections bring early high resolution features to the decoder, most systematically in U-Net. DeepLab keeps maps dense with dilated convolutions and sees many scales at once with ASPP. Choose the design by the failure you need to fix.</p>')
