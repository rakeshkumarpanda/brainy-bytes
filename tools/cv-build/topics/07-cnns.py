# Chapter 7: image classification, datasets, convolutional networks, SoftMax and cross entropy, confidence,
# and the architectures from AlexNet to Vision Transformers. Source: lecture 1 (section 13), lecture 2 (sections 3 and 4),
# lectures 3 and 4 (part IX) and lectures 5 and 6 (sections 4 and 5).
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('softmax', r'''
# SoftMax, cross entropy and the gradient p - y
from math import exp, log

logits = [float(v) for v in input("Logits for dog, cat, wolf: ").split()]
true = 0                                       # the image really is a dog

top = max(logits)
e = [exp(z - top) for z in logits]             # subtract the max for safety
total = sum(e)
p = [v / total for v in e]
print("probabilities:", [round(v, 3) for v in p])
print("sum:", round(sum(p), 3))

loss = -log(p[true])
grad = [round(p[i] - (1 if i == true else 0), 3) for i in range(len(p))]
print("cross entropy loss:", round(loss, 3))
print("gradient p - y:", grad)
''', stdin='2 1 0.1\n')

K.code('layer', r'''
# Size and cost of one convolution layer
h = w = int(input("Input height and width: "))
c_in = int(input("Input channels: "))
k = int(input("Kernel size k: "))
c_out = int(input("Number of filters (output channels): "))
p, s = 0, 1                                    # padding and stride

out = (h - k + 2 * p) // s + 1
params = k * k * c_in * c_out + c_out          # weights plus one bias per filter
macs = out * out * k * k * c_in * c_out        # multiply-add operations
print("output:", out, "x", out, "x", c_out)
print("parameters:", params)
print("multiply-adds:", macs)
''', stdin='80\n128\n1\n256\n')

K.code('pool', r'''
# ReLU, then 2 x 2 max pooling with stride 2
fmap = [[ 1, -3,  2,  0],
        [ 4,  8, -1,  5],
        [ 0, -2,  9,  6],
        [-3,  1,  4,  7]]

relu = [[max(0, v) for v in row] for row in fmap]
print("after ReLU:")
for row in relu:
    print(row)

pooled = []
for y in range(0, 4, 2):
    row = []
    for x in range(0, 4, 2):
        row.append(max(relu[y][x], relu[y][x + 1], relu[y + 1][x], relu[y + 1][x + 1]))
    pooled.append(row)
print("after max pooling:", pooled)
''')

K.lesson('classify', 'Image classification and its datasets', f'''
<p><b>Image classification</b> answers one question about the whole picture: what is the main thing in it. The model does not return just a word. It returns a probability for every class, and the highest one becomes the prediction.</p>
{table(['Class', 'Predicted probability'], [['Dog', '0.82'], ['Cat', '0.10'], ['Wolf', '0.05'], ['Other', '0.03']])}
<h3>The datasets that drove progress</h3>
<p>Caltech 101, PASCAL VOC and ImageNet gave researchers many images, fixed categories, agreed train and test splits and common metrics, so models could be compared fairly. The lecture singles out <b>ImageNet</b>: about 22,000 categories and about 15 million images in total. Its yearly challenge (ILSVRC) used a controlled subset of 1,000 classes with about 1.28 million training images, or about 1.43 million counting the validation and test images.</p>
<h3>Why ImageNet was hard</h3>
{table(['Difficulty', 'Meaning', 'Example'], [
    ['Many classes', '1,000 categories, many of them close', 'Over a hundred dog breeds'],
    ['Inter-class similarity', 'Different classes can look alike', 'Wolf and husky, truck and bus'],
    ['Intra-class variation', 'One class can look very different', 'A chair from the side, from above, folded, in the dark']])}
<h3>Data size and model capacity</h3>
{table(['', 'Underfitting', 'Overfitting'], [
    ['Cause', 'Model too simple for the data', 'Model memorises the training examples and their noise'],
    ['Training score', 'Poor', 'High'],
    ['Test score', 'Poor', 'Poor'],
    ['Typical fix', 'Bigger model, more training', 'More data, augmentation, regularisation, early stopping']])}
<p>The central lesson from the lecture: more data often needs a more powerful architecture to learn from it. A small model on ImageNet underfits however long you train it.</p>
{note('Classification gives one label for the whole image. Detection adds a box for each of a variable number of objects. Segmentation labels every pixel. Know all three outputs.', 'exam')}
''', kw=['image classification', 'class probabilities', 'ImageNet', 'ILSVRC', 'PASCAL VOC', 'Caltech 101', 'inter-class variation', 'intra-class variation', 'underfitting', 'overfitting', 'capacity'])

K.lesson('cnn', 'Convolutional neural networks', f'''
<p>In chapter 2.3 you chose the kernel numbers yourself: a box for blur, Sobel for edges. A <b>convolutional neural network</b> (CNN) uses exactly the same sliding operation, but it <b>learns</b> the kernel numbers from labelled examples. Each layer has many filters, and each filter produces one feature map.</p>
{fxs(
    fx('One convolution layer', '<i>y</i> = ReLU(<i>W</i> ∗ <i>x</i> + <i>b</i>), &nbsp; ReLU(<i>t</i>) = max(0, <i>t</i>)', 'The filters <i>W</i> and biases <i>b</i> are learned. ReLU keeps positive responses and sets the rest to 0.', key=True),
    fx('Parameters of a layer', 'params = <i>k</i> × <i>k</i> × <i>C</i><sub>in</sub> × <i>C</i><sub>out</sub> + <i>C</i><sub>out</sub>', 'Each of the <i>C</i><sub>out</sub> filters spans all <i>C</i><sub>in</sub> input channels and has one bias.', key=True),
    fx('Output size', '<i>O</i> = ⌊' + frac('<i>W</i> − <i>k</i> + 2<i>P</i>', '<i>S</i>') + '⌋ + 1', 'The same formula as chapter 2.3. The number of output channels is the number of filters you choose.'))}
{viz('convlayer')}
<h3>Pooling</h3>
<p>Pooling shrinks a feature map. <b>Max pooling</b> keeps the largest value in each 2 × 2 block, <b>average pooling</b> keeps the mean. Pooling makes the network a little tolerant to small shifts, reduces computation, and lets later layers see a larger part of the image.</p>
{code('pool')}
<h3>A hierarchy of features</h3>
<p>The lecture describes how CNNs learn in layers. Early layers respond to simple edges and intensity patterns, much like Sobel and HOG. Middle layers combine these into textures, corners and parts. Deep layers respond to whole objects and meaningful concepts. This is the same climb from pixels to meaning that Marr described in chapter 1.2, but learned from data rather than designed.</p>
{viz('receptive')}
{code('layer')}
''', kw=['CNN', 'convolutional neural network', 'convolution layer', 'filter', 'feature map', 'ReLU', 'activation', 'pooling', 'max pooling', 'average pooling', 'parameters', 'receptive field', 'feature hierarchy'])

K.lesson('softmax', 'SoftMax, sigmoid and cross entropy', f'''
<p>The last layer of a classifier outputs one raw number per class, called a <b>logit</b>. These numbers can be any size and sign, so they are turned into probabilities.</p>
{fxs(
    fx('SoftMax', '<i>p</i><sub><i>i</i></sub> = ' + frac('<i>e</i><sup><i>z</i><sub><i>i</i></sub></sup>', 'Σ<sub><i>j</i></sub> <i>e</i><sup><i>z</i><sub><i>j</i></sub></sup>'), 'All probabilities are positive and add up to 1, so the classes compete.', key=True),
    fx('Sigmoid', 'σ(<i>z</i>) = ' + frac('1', '1 + <i>e</i><sup>−<i>z</i></sup>'), 'Squashes one score into (0, 1). Independent sigmoids do not add up to 1.', key=True),
    fx('Cross entropy loss', '<i>L</i> = −Σ<sub><i>j</i></sub> <i>y</i><sub><i>j</i></sub> ln <i>p</i><sub><i>j</i></sub> = −ln <i>p</i><sub>true</sub>', '<i>y</i> is one hot: 1 for the true class, 0 elsewhere. A confident correct answer gives a loss near 0.', key=True),
    fx('Gradient', '∂<i>L</i> ÷ ∂<i>z</i><sub><i>k</i></sub> = <i>p</i><sub><i>k</i></sub> − <i>y</i><sub><i>k</i></sub>', 'Push the true logit up and the others down, each in proportion to its error.'))}
{steps('The lecture example by hand', [
    'Logits z = [2.0, 1.0, 0.1].',
    'Exponentiate: e<sup>2.0</sup> = 7.389, e<sup>1.0</sup> = 2.718, e<sup>0.1</sup> = 1.105.',
    'Sum: 7.389 + 2.718 + 1.105 = 11.213.',
    'Divide: p = [0.659, 0.242, 0.099], which adds up to 1.',
    'If class 1 is correct, the loss is −ln 0.659 ≈ 0.417 and the gradient is [−0.341, 0.242, 0.099].'])}
{viz('softmax')}
{code('softmax')}
<h3>SoftMax or sigmoid</h3>
<p>The lecturer's rule: sigmoid for two classes, SoftMax for many, although SoftMax also works for two. The precise picture: use SoftMax when exactly one class is correct, and one sigmoid per class when several labels can be true at once (a photo tagged both beach and sunset). With two classes they are the same thing, because e<sup>z<sub>1</sub></sup> ÷ (e<sup>z<sub>1</sub></sup> + e<sup>z<sub>2</sub></sup>) = σ(z<sub>1</sub> − z<sub>2</sub>).</p>
{note('Computers overflow when they raise e to a large number. Since SoftMax(z) = SoftMax(z − max z), real code subtracts the largest logit first. The answer does not change.', 'tip')}
''', kw=['SoftMax', 'softmax', 'sigmoid', 'logit', 'cross entropy', 'one hot', 'gradient', 'p minus y', 'multi-label', 'temperature', 'numerical stability'])

K.lesson('confidence', 'Confidence, inductive bias and calibration', f'''
<p>When a model says dog with probability 0.80, that number is called its <b>confidence</b>. The class answer in the lecture was correct: most often it is the SoftMax output, though entropy based measures are also used.</p>
<h3>Inductive bias</h3>
<p>The lecture asked what inductive bias is. The answer: the assumptions a model makes so that it can generalise. The example was the sequence 2, 4, 6. Most people say the next number is 8, assuming add 2 each time. But add the last two numbers would give 10, and that also fits. Every model must assume something to fill the gap between the examples it saw and new ones, and its confidence is shaped by those assumptions.</p>
{scene('ducks on a lake', '<p>A model is trained only on photos of ducks swimming on blue lakes. It learns that blue background means duck, and then says not a duck for a duck standing on brown sand. The data was consistent with two rules, duck shape or blue background, and the model picked the wrong one, just as 8 was only one valid answer for 2, 4, 6. This is called background bias or a spurious correlation, and it is why diverse training data matters.</p>')}
<h3>Calibration</h3>
{fx('Calibration', 'Among all predictions made with confidence <i>c</i>, the fraction that is correct should be about <i>c</i>', 'A model that says 0.80 but is right only half the time is overconfident.', key=True)}
<p>The lecturer stressed safety: if a model is used to save a life and acts on a prediction it is only 10% sure of, the cost of a mistake is severe. A trustworthy model must be accurate and also well calibrated. Modern deep networks tend to be overconfident. A simple fix, temperature scaling, divides the logits by one number <i>T</i> chosen on validation data (try the temperature dial in the SoftMax animation).</p>
{deep('measuring calibration', '<p>Sort predictions into bins by confidence, for example 0.0 to 0.1, 0.1 to 0.2 and so on. In each bin compare the average confidence with the accuracy. The expected calibration error is the weighted average gap: ECE = Σ<sub><i>b</i></sub> (<i>n</i><sub><i>b</i></sub> ÷ <i>N</i>) |acc(<i>b</i>) − conf(<i>b</i>)|. A reliability diagram plots accuracy against confidence, and a perfect model lies on the diagonal. Guo and colleagues (2017) showed that modern networks such as ResNets are often overconfident, and that temperature scaling fixes much of it without changing which class is predicted.</p>')}
''', kw=['confidence', 'inductive bias', '2 4 6', 'spurious correlation', 'background bias', 'calibration', 'overconfident', 'temperature scaling', 'ECE', 'reliability diagram', 'uncertainty'])

K.lesson('architectures', 'From AlexNet to Vision Transformers', f'''
<p>The lecture traces the architectures that pushed ImageNet error down year after year.</p>
{table(['Model', 'Year', 'Key idea'], [
    ['AlexNet', '2012', 'Deep CNN trained on GPUs with ReLU, dropout regularisation and data augmentation. A large jump over hand made features.'],
    ['VGG', '2014', 'Only small 3 × 3 filters, stacked deep. Repeated small filters reach as far as large ones with fewer weights and more non linearity.'],
    ['GoogLeNet (Inception)', '2014', 'Filters of several sizes side by side, because objects contain patterns of different sizes. 1 × 1 convolutions keep it cheap.'],
    ['ResNet', '2015', 'Shortcut connections, so each block learns a correction F(x) = H(x) − x. Made networks of 100 and more layers trainable.'],
    ['Vision Transformer (ViT)', '2020', 'Cut the image into patches and treat them as a sequence of tokens. Attention links distant parts directly.']])}
{fx('Residual learning', '<i>H</i>(<i>x</i>) = <i>F</i>(<i>x</i>) + <i>x</i>', 'The shortcut passes <i>x</i> straight through. The layers only learn the difference <i>F</i>(<i>x</i>).', key=True)}
<p>Why does this help? Making a plain network deeper does not automatically make it better. Very deep plain networks suffer from vanishing gradients and become hard to optimise, and even their training accuracy can get worse, which the ResNet authors called the <b>degradation problem</b>. A shortcut lets information and gradients flow straight through, so a block that has nothing useful to add can simply learn F(x) = 0.</p>
{viz('residual')}
<h3>The 1 × 1 convolution</h3>
<p>The lecture set this as homework: an 80 × 80 × 128 feature map goes through a 1 × 1 convolution. What comes out? One student guessed 160 × 160 with twice the channels, which is not right. A 1 × 1 convolution with stride 1 keeps the height and width and mixes the channels at each pixel. The number of output channels equals the number of filters you choose. With 256 filters the output is 80 × 80 × 256, with 1 × 1 × 128 × 256 + 256 = 33,024 parameters. It was introduced in Network in Network (2013) and made popular by GoogLeNet as a cheap way to change the channel count.</p>
{fx('ViT tokens', 'number of tokens = (' + frac('<i>H</i>', '<i>P</i>') + ') × (' + frac('<i>W</i>', '<i>P</i>') + ')', 'For a 224 × 224 image and 16 × 16 patches: 14 × 14 = 196 tokens.')}
{note('Some models now report lower error than the estimated human error on ImageNet. That does not mean human level vision. Models still fail under unusual conditions, distribution shift, adversarial changes, occlusion, new categories and ambiguous scenes. Benchmark wins are specific to the benchmark.', 'warn')}
''', kw=['AlexNet', 'VGG', 'GoogLeNet', 'Inception', 'ResNet', 'residual', 'skip connection', 'degradation problem', 'vanishing gradient', '1x1 convolution', 'Network in Network', 'Vision Transformer', 'ViT', 'patches', 'tokens', 'attention'])

K.lesson('design', 'Designing a model: architecture, loss, optimisation', f'''
<p>The lecturer asked what three dimensions every deep learning design has. A student guessed width and height. The answer: <b>architecture</b>, <b>loss function</b> and <b>optimisation</b>. The lecturer added that only about 1% of people work on optimisation, which needs a strong mathematical background, while most work goes into architectures and losses.</p>
{table(['Axis', 'Question it answers', 'Examples'], [
    ['Architecture', 'Which functions can the model represent?', 'Convolutions, residual blocks, attention, feature pyramids'],
    ['Loss', 'What do we ask it to do?', 'Cross entropy, Huber, focal loss (chapter 5.2)'],
    ['Optimisation', 'How do we search for good weights?', 'SGD, momentum, Adam, learning rate schedules']])}
{fx('Gradient descent', '<i>w</i> ← <i>w</i> − η ' + frac('∂<i>L</i>', '∂<i>w</i>'), 'η is the learning rate. Too large and training jumps around, too small and it crawls.', key=True)}
<p><b>Regularisation</b> keeps a model from overfitting. A weight decay term lives inside the loss, as the lecture said. Dropout, data augmentation and early stopping also regularise, but they do it without any loss term.</p>
{ladder(
    '<p>A CNN looks at a picture through many tiny windows. Each window checks for a simple pattern such as an edge. Later layers combine the patterns into eyes, wheels and leaves, and the last layer turns all of it into a score for each possible answer.</p>',
    '<p>A conv layer computes ReLU(W ∗ x + b) with k × k × C<sub>in</sub> × C<sub>out</sub> + C<sub>out</sub> parameters. Pooling and stride shrink the maps and grow the receptive field. SoftMax turns logits into probabilities, cross entropy −ln p<sub>true</sub> is the loss, and its gradient p − y drives gradient descent.</p>',
    '<p>Convolution builds in two inductive biases: locality and translation equivariance, with weights shared across positions. Residual connections make the network an ensemble of paths of many depths and keep the Jacobian close to the identity. ViTs drop most of the convolutional bias, so they need more data or strong augmentation, which is why hybrid designs and pre training matter.</p>',
    '<p>Current research studies scaling laws relating data, parameters and compute, self supervised pre training (contrastive and masked image modelling), robustness to distribution shift, and calibration and uncertainty, including conformal prediction that gives sets of classes with a guaranteed error rate.</p>')}
''', kw=['architecture', 'loss function', 'optimisation', 'gradient descent', 'learning rate', 'SGD', 'Adam', 'regularisation', 'weight decay', 'dropout', 'data augmentation', 'early stopping'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What does an image classifier return?', ['A box around each object', 'A probability for each class, and the highest is the prediction', 'A label for every pixel', 'A cleaned image'], 1,
       'One question about the whole image.', 'Classification outputs a distribution over classes, for example dog 0.82, cat 0.10.')
K.quiz('e', 'A wolf and a husky look very similar. This is an example of', ['Intra-class variation', 'Inter-class similarity', 'Overfitting', 'Noise'], 1,
       'Inter means between classes.', 'Different classes that look alike make inter-class differences small. Intra-class variation is one class looking very different.')
K.quiz('e', 'What does ReLU do to the value −3?', ['Keeps −3', 'Turns it into 0', 'Turns it into 3', 'Turns it into 1'], 1, 'ReLU(t) = max(0, t).', 'max(0, −3) = 0. Negative responses are switched off.')
K.quiz('m', 'A model scores 99% on training data and 62% on test data. This is', ['Underfitting', 'Overfitting', 'Good generalisation', 'Calibration'], 1,
       'Big gap between train and test.', 'The model memorised the training set. More data, augmentation or regularisation would help.')
K.quiz('m', 'An 80 × 80 × 128 map goes through a 1 × 1 convolution with 256 filters, stride 1. The output is', ['160 × 160 × 256', '80 × 80 × 256', '80 × 80 × 128', '1 × 1 × 256'], 1,
       'A 1 × 1 filter does not change height or width.', 'The spatial size stays 80 × 80. The channels equal the number of filters, 256.')
K.quiz('m', 'A photo can be tagged beach, sunset and people at the same time. Which output layer fits?', ['SoftMax over all tags', 'One sigmoid per tag', 'ReLU', 'Max pooling'], 1,
       'Can several labels be true?', 'SoftMax forces the probabilities to compete and add to 1. Independent sigmoids let each tag be yes or no on its own.')
K.quiz('m', 'In ResNet, a block outputs H(x) = F(x) + x. What do the layers inside the block learn?', ['The whole mapping H(x)', 'Only the correction F(x) = H(x) − x', 'Nothing', 'The input x'], 1,
       'The shortcut already passes x.', 'Learning a correction is easier, and F(x) = 0 is enough when the block has nothing to add.')
K.quiz('h', 'Why do stacked 3 × 3 filters (VGG) beat one large filter with the same reach?', [
    'They see further', 'Fewer weights and more non linear ReLUs for the same receptive field', 'They need no training', 'They remove pooling'], 1,
    'Three 3 × 3 layers reach 7 pixels.', 'Three 3 × 3 layers use 27 weights per channel pair against 49 for a 7 × 7, and add two extra ReLUs.')
K.quiz('h', 'The lecture asked for the next number after 2, 4, 6. What idea was it illustrating?', ['Overfitting', 'Inductive bias: the assumptions a model makes to generalise', 'Pooling', 'Data augmentation'], 1,
       '8 is only one rule that fits.', 'Both add 2 (giving 8) and add the last two (giving 10) fit the data. Choosing one is an assumption.')
K.quiz('h', 'A model says 80% on 100 predictions but only 50 are correct. The model is', ['Well calibrated', 'Overconfident', 'Underconfident', 'Overfitting by definition'], 1,
       'Compare stated confidence with accuracy.', 'It claims 0.80 but achieves 0.50, so it is overconfident. Temperature scaling is one fix.')
K.quiz('x', 'Adding the same constant to every logit changes the SoftMax output by', ['Doubling it', 'Nothing', 'Making it uniform', 'Shifting it by the constant'], 1,
       'Factor e to the constant out of the top and bottom.', 'e<sup>z + c</sup> ÷ Σ e<sup>z + c</sup> = e<sup>z</sup> ÷ Σ e<sup>z</sup>. That is why subtracting the maximum is safe.')
K.quiz('x', 'Which three axes did the lecturer give for any deep learning design?', ['Width, height, depth', 'Architecture, loss function, optimisation', 'Data, GPU, time', 'Precision, recall, accuracy'], 1,
       'One student guessed width and height.', 'Architecture decides what can be represented, the loss what is asked, optimisation how weights are found. Regularisation sits partly in the loss.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Apply ReLU then 2 × 2 max pooling (stride 2) to [[1, −3, 2, 0], [4, 8, −1, 5], [0, −2, 9, 6], [−3, 1, 4, 7]]. What is the top right output value?', '5', 'The top right block is rows 1 to 2, columns 3 to 4.',
       ['Top right block: 2, 0, −1, 5.', 'ReLU: 2, 0, 0, 5.', eq('max(2, 0, 0, 5) = 5'), 'The full output is [[8, 5], [1, 9]].'], check=5)
K.calc('e', 'What is σ(2), the sigmoid of 2? Give three decimals.', '0.881', 'σ(z) = 1 ÷ (1 + e<sup>−z</sup>).',
       ['e<sup>−2</sup> ≈ 0.1353.', '1 + 0.1353 = 1.1353.', eq('σ(2) = 1 ÷ 1.1353 ≈ 0.881')], check=0.881, tol=0.0006)
K.calc('m', 'SoftMax of the logits [2.0, 1.0, 0.1]: what is the probability of the first class? Give three decimals.', '0.659', 'Exponentiate each, divide by the sum.',
       ['e<sup>2</sup> = 7.389, e<sup>1</sup> = 2.718, e<sup>0.1</sup> = 1.105.', 'Sum = 11.213.', eq('p<sub>1</sub> = 7.389 ÷ 11.213 ≈ 0.659')], check=0.659, tol=0.0006)
K.calc('m', 'With p<sub>true</sub> = 0.659, what is the cross entropy loss? Give three decimals.', '0.417', 'L = −ln p<sub>true</sub>.',
       ['ln 0.659 ≈ −0.417.', 'Change the sign.', eq('L ≈ 0.417'), 'If the model were 0.99 sure the loss would be 0.010. At 0.01 it would be 4.6.'], check=0.417, tol=0.0006)
K.calc('m', 'For the same example with class 1 true, what is the gradient ∂L/∂z<sub>1</sub>? Give three decimals.', '-0.341', '∂L/∂z<sub>k</sub> = p<sub>k</sub> − y<sub>k</sub>.',
       ['p<sub>1</sub> = 0.659 and y<sub>1</sub> = 1.', '0.659 − 1.', eq('∂L/∂z<sub>1</sub> = −0.341'), 'Negative, so gradient descent increases z<sub>1</sub>.'], check=-0.341, tol=0.0006)
K.calc('m', 'A first layer has 64 filters of size 3 × 3 on an RGB image. How many parameters does it have, with biases?', '1792', 'k × k × C<sub>in</sub> × C<sub>out</sub> + C<sub>out</sub>.',
       ['Weights: 3 × 3 × 3 × 64 = 1,728.', 'Biases: 64.', eq('1,728 + 64 = 1,792')], check=1792)
K.calc('m', 'How many parameters does a 1 × 1 convolution from 128 to 256 channels have, with biases?', '33024', 'k × k × C<sub>in</sub> × C<sub>out</sub> + C<sub>out</sub> with k = 1.',
       ['Weights: 1 × 1 × 128 × 256 = 32,768.', 'Biases: 256.', eq('32,768 + 256 = 33,024')], check=33024)
K.calc('h', 'On an 80 × 80 map, how many multiply-adds does that 1 × 1 convolution need?', '209715200', 'Each output value needs C<sub>in</sub> multiply-adds.',
       ['Output values: 80 × 80 × 256 = 1,638,400.', 'Each needs 1 × 1 × 128 = 128 multiply-adds.', eq('1,638,400 × 128 = 209,715,200'), 'About 0.21 billion, small for a GPU.'], check=209715200)
K.calc('h', 'How many weights (no biases) do two stacked 3 × 3 layers with 64 input and 64 output channels need?', '73728', 'Each layer has 3 × 3 × 64 × 64 weights.',
       ['One layer: 9 × 64 × 64 = 36,864.', 'Two layers: 2 × 36,864.', eq('= 73,728'), 'One 5 × 5 layer with the same reach needs 25 × 64 × 64 = 102,400, about 39% more.'], check=73728)
K.calc('h', 'Three 3 × 3 convolution layers with stride 1 are stacked. How wide is the receptive field of one top neuron?', '7', 'r grows by k − 1 per layer when the stride is 1.',
       ['Start with r = 1.', 'Each layer adds 3 − 1 = 2.', eq('r = 1 + 2 + 2 + 2 = 7')], check=7)
K.calc('x', 'A plain network passes the gradient back through 10 layers that each multiply it by 0.8. What fraction reaches the first layer? Give two decimals.', '0.11', 'Multiply ten slopes.',
       ['Fraction = 0.8<sup>10</sup>.', '0.8<sup>2</sup> = 0.64, 0.8<sup>5</sup> ≈ 0.328.', eq('0.8<sup>10</sup> ≈ 0.328² ≈ 0.107 ≈ 0.11'), 'After 30 such layers it is about 0.0012. ResNet shortcuts keep this close to 1.'], check=0.8 ** 10, tol=0.006)
K.calc('x', 'A Vision Transformer takes a 224 × 224 image in 16 × 16 patches. How many patch tokens are there?', '196', 'Patches per side, squared.',
       ['224 ÷ 16 = 14 patches across.', '14 patches down.', eq('14 × 14 = 196 tokens'), 'Attention compares every pair of tokens, so its cost grows with 196² = 38,416 pairs per head and layer.'], check=196)

# ---------------------------------------------------------------- assignments
K.assign('softmax', 'e', 'SoftMax',
         '<p>Write <code>softmax(z)</code> that returns the SoftMax of a list of logits, each rounded to 3 decimals. Subtract the largest logit first so large inputs do not overflow.</p>',
         '''
from math import exp

def softmax(z):
    # your code here
    pass
''', [('softmax([2.0, 1.0, 0.1])', [0.659, 0.242, 0.099]), ('softmax([0, 0])', [0.5, 0.5]), ('softmax([1000, 1000, 1000, 1000])', [0.25, 0.25, 0.25, 0.25])],
         '''
from math import exp

def softmax(z):
    m = max(z)
    e = [exp(v - m) for v in z]
    s = sum(e)
    return [round(v / s, 3) for v in e]
''', 'Compute the exponentials of z − max(z), then divide each by their sum.',
         '<p>Without the subtraction the third test would overflow, because e<sup>1000</sup> is far beyond the range of a float.</p>')
K.assign('params', 'e', 'Count the parameters of a layer',
         '<p>Write <code>conv_params(k, c_in, c_out, bias=True)</code> that returns the number of learnable parameters of a k × k convolution layer.</p>',
         '''
def conv_params(k, c_in, c_out, bias=True):
    # your code here
    pass
''', [('conv_params(3, 3, 64)', 1792), ('conv_params(1, 128, 256)', 33024), ('conv_params(3, 64, 64, False)', 36864), ('conv_params(7, 3, 64)', 9472)],
         '''
def conv_params(k, c_in, c_out, bias=True):
    return k * k * c_in * c_out + (c_out if bias else 0)
''', 'One bias per filter.', '<p>The last test has the shape of the first ResNet layer, 64 filters of 7 × 7 on RGB: 7 × 7 × 3 × 64 + 64 = 9,472 with biases. ResNet itself leaves the bias out, because batch normalisation follows.</p>')
K.assign('maxpool', 'm', 'Max pooling',
         '<p>Write <code>max_pool(m)</code> for 2 × 2 max pooling with stride 2. If the height or width is odd, ignore the last row or column.</p>',
         '''
def max_pool(m):
    # your code here
    pass
''', [('max_pool([[1, 3, 2, 0], [4, 8, 0, 5], [0, 0, 9, 6], [0, 1, 4, 7]])', [[8, 5], [1, 9]]), ('max_pool([[1, 2], [3, 4]])', [[4]]), ('max_pool([[1, 2, 9], [3, 4, 9], [9, 9, 9]])', [[4]])],
         '''
def max_pool(m):
    h, w = len(m) // 2 * 2, len(m[0]) // 2 * 2
    return [[max(m[y][x], m[y][x + 1], m[y + 1][x], m[y + 1][x + 1]) for x in range(0, w, 2)] for y in range(0, h, 2)]
''', 'Step through y and x in twos, and take the max of four values each time.',
         '<p>The third test shows the floor in the output size formula: ⌊(3 − 2) ÷ 2⌋ + 1 = 1, so the last row and column are dropped.</p>')
K.assign('rf', 'h', 'Receptive field of a stack of layers',
         '<p>Write <code>receptive_field(layers)</code> where <code>layers</code> is a list of (k, s) pairs, kernel size and stride, from first to last. Use r = 1, j = 1, then for each layer r = r + (k − 1) × j and j = j × s. Return r.</p>',
         '''
def receptive_field(layers):
    # your code here
    pass
''', [('receptive_field([(3, 1), (3, 1), (3, 1)])', 7), ('receptive_field([(7, 1)])', 7), ('receptive_field([(3, 1), (2, 2), (3, 1), (2, 2), (3, 1)])', 18), ('receptive_field([])', 1)],
         '''
def receptive_field(layers):
    r, j = 1, 1
    for k, s in layers:
        r += (k - 1) * j
        j *= s
    return r
''', 'Update r before j, because the growth uses the jump from the layer below.',
         '<p>The third test is conv, pool, conv, pool, conv: 1 + 2 + 1 + 4 + 2 + 8 = 18. Each pooling layer doubles how fast later layers grow.</p>')

K.must('Classification', 'One label for the whole image, from a probability per class. ImageNet challenge: 1,000 classes, about 1.28 million training images. Hard because of inter-class similarity and intra-class variation.')
K.must('CNN layer', 'y = ReLU(W ∗ x + b), params k × k × C<sub>in</sub> × C<sub>out</sub> + C<sub>out</sub>, output ⌊(W − k + 2P) ÷ S⌋ + 1. Pooling shrinks maps. Features go from edges to parts to objects.')
K.must('SoftMax and loss', 'p<sub>i</sub> = e<sup>z<sub>i</sub></sup> ÷ Σ e<sup>z<sub>j</sub></sup>, loss −ln p<sub>true</sub>, gradient p − y. [2, 1, 0.1] gives [0.659, 0.242, 0.099]. Sigmoids for multi-label.')
K.must('Confidence', 'Confidence is usually the SoftMax output. Inductive bias (2, 4, 6) shapes it. A calibrated model is right c of the time when it says c.')
K.must('Architectures', 'AlexNet (GPU, ReLU, augmentation), VGG (stacked 3 × 3), Inception (several sizes, 1 × 1), ResNet H(x) = F(x) + x, ViT (patches as tokens).')
K.must('Design axes', 'Architecture, loss, optimisation. 1 × 1 conv on 80 × 80 × 128 with 256 filters gives 80 × 80 × 256 and 33,024 parameters.')

T = K.topic(
    slug='classification-cnns', topic='cnns', step=(4, 'Recognising what is in an image', 'cv-recognition', 'From hand made features to learned ones: how convolutional networks classify images and how confident they really are.', 'College'),
    title='Image classification and convolutional networks', short='Classification and CNNs', badge='4.1', minutes=55,
    lead='See how a network learns its own filters, turns scores into probabilities with SoftMax, measures its mistakes with cross entropy, and how AlexNet, VGG, Inception, ResNet and Vision Transformers pushed ImageNet error down.',
    desc='Image classification and ImageNet, convolution layers, ReLU and pooling, receptive fields, SoftMax and sigmoid, cross entropy and its gradient, confidence, inductive bias and calibration, and the classic architectures.',
    summary='Classification datasets, CNN layers and receptive fields, SoftMax and cross entropy, confidence and calibration, and AlexNet to ViT.',
    keywords=['image classification', 'ImageNet', 'CNN', 'convolution layer', 'ReLU', 'pooling', 'receptive field', 'SoftMax', 'sigmoid', 'cross entropy', 'calibration', 'inductive bias', 'AlexNet', 'VGG', 'ResNet', 'Vision Transformer', '1x1 convolution'],
    recap='<p>A CNN learns the filters that earlier chapters designed by hand, stacks them with ReLU and pooling, and ends with SoftMax probabilities trained by cross entropy. Its confidence reflects its assumptions and should be calibrated. Deeper networks became trainable with residual shortcuts, and transformers replaced local filters with attention over patches.</p>')
