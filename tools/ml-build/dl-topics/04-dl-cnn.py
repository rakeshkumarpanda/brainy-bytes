# Deep learning 2.1: convolutional neural networks. Checked against Goodfellow, Bengio and Courville, Deep Learning
# (MIT Press 2016) chapter 9, the Stanford CS231n notes on convolutional networks, LeCun and colleagues, Gradient based
# learning applied to document recognition (1998), Krizhevsky, Sutskever and Hinton, AlexNet (NeurIPS 2012), Simonyan
# and Zisserman, VGG (ICLR 2015), He and colleagues, Deep residual learning (CVPR 2016), Tan and Le, EfficientNet (ICML
# 2019), Dosovitskiy and colleagues, An image is worth 16x16 words (ICLR 2021), and Yu and Koltun, dilated
# convolutions (ICLR 2016).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('dl-cnn')
K = Kit()

K.code('conv2d', r'''
# A 2D convolution written by hand, used to find edges in a tiny image.
import numpy as np


def conv2d(image, kernel, stride=1, padding=0):
    if padding:
        image = np.pad(image, padding)
    k = kernel.shape[0]
    out_size = (image.shape[0] - k) // stride + 1
    out = np.zeros((out_size, out_size))
    for i in range(out_size):
        for j in range(out_size):
            patch = image[i * stride:i * stride + k, j * stride:j * stride + k]
            out[i, j] = np.sum(patch * kernel)      # multiply and add
    return out


# a 6 x 6 image: dark on the left, bright on the right
image = np.array([[0, 0, 0, 9, 9, 9]] * 6, dtype=float)
vertical_edge = np.array([[-1, 0, 1],
                          [-1, 0, 1],
                          [-1, 0, 1]], dtype=float)
horizontal_edge = vertical_edge.T

print('vertical edge filter output:')
print(conv2d(image, vertical_edge))
print('horizontal edge filter output (no horizontal edges):')
print(conv2d(image, horizontal_edge))

# output size = (n + 2p - k) // s + 1
for n, k, p, s in [(6, 3, 0, 1), (6, 3, 1, 1), (7, 3, 0, 2), (32, 5, 2, 1), (224, 7, 3, 2)]:
    size = (n + 2 * p - k) // s + 1
    print(f'n={n}, k={k}, padding={p}, stride={s}: output {size} x {size}')

out = conv2d(image, vertical_edge, stride=2, padding=1)
print('stride 2 with padding 1 gives shape', out.shape)
''', long=True)

K.code('pooling', r'''
# Max pooling, weight sharing and how far each unit can see.
import numpy as np


def max_pool(x, size=2):
    h, w = x.shape[0] // size, x.shape[1] // size
    return x[:h * size, :w * size].reshape(h, size, w, size).max(axis=(1, 3))


fmap = np.array([[1, 3, 2, 1],
                 [4, 6, 5, 0],
                 [7, 2, 9, 8],
                 [1, 0, 3, 4]], dtype=float)
print('2 x 2 max pooling:')
print(max_pool(fmap))

# shifting the input by one pixel inside a pooling window often leaves the pooled output unchanged
x = np.zeros((4, 4))
x[0, 0] = 5
shifted = np.zeros((4, 4))
shifted[1, 1] = 5
print('pooled before shift:', max_pool(x).ravel(), ' after shift:', max_pool(shifted).ravel())

# weights: a dense layer against a convolution on a 32 x 32 x 3 image
dense = (32 * 32 * 3) * (32 * 32 * 16) + 32 * 32 * 16
conv = 3 * 3 * 3 * 16 + 16
print(f'dense layer to 32x32x16: {dense:,} weights')
print(f'3x3 conv with 16 filters: {conv:,} weights ({dense // conv:,} times fewer)')

# receptive field: r grows by (k - 1) * jump, jump multiplies by the stride
layers = [('conv 3x3', 3, 1), ('conv 3x3', 3, 1), ('pool 2x2', 2, 2), ('conv 3x3', 3, 1), ('pool 2x2', 2, 2), ('conv 3x3', 3, 1)]
r, jump = 1, 1
for name, k, s in layers:
    r += (k - 1) * jump
    jump *= s
    print(f'after {name}: each unit sees {r} x {r} input pixels')
''', long=True)

K.code('cnn_digits', r'''
# A small convolutional network in numpy, trained on 8 x 8 handwritten digits.
# conv 3x3 (8 filters, padding 1) -> ReLU -> 2x2 max pool -> dense 10 -> softmax
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

digits = load_digits()
X = digits.images / 16.0                       # shape (1797, 8, 8), values 0 to 1
y = digits.target
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)

rng = np.random.default_rng(0)
F = 8
Wc = rng.normal(scale=np.sqrt(2 / 9), size=(9, F))     # each column is one 3x3 filter
bc = np.zeros(F)
Wd = rng.normal(scale=np.sqrt(2 / (4 * 4 * F)), size=(4 * 4 * F, 10))
bd = np.zeros(10)


def patches(imgs):
    # every 3x3 patch of the padded images as a row: (n, 8, 8, 9)
    p = np.pad(imgs, ((0, 0), (1, 1), (1, 1)))
    return np.stack([p[:, i:i + 8, j:j + 8] for i in range(3) for j in range(3)], axis=-1)


def forward(imgs):
    P = patches(imgs)
    z = P @ Wc + bc                                   # (n, 8, 8, F): the convolution
    a = np.maximum(z, 0)
    blocks = a.reshape(-1, 4, 2, 4, 2, F)
    pooled = blocks.max(axis=(2, 4))                  # (n, 4, 4, F)
    scores = pooled.reshape(len(imgs), -1) @ Wd + bd
    return P, z, a, blocks, pooled, scores


def accuracy(imgs, labels):
    return np.mean(forward(imgs)[-1].argmax(axis=1) == labels)


v = [np.zeros_like(p) for p in (Wc, bc, Wd, bd)]
lr = 0.05
for epoch in range(1, 9):
    order = rng.permutation(len(X_tr))
    for start in range(0, len(order), 32):
        idx = order[start:start + 32]
        imgs, labels = X_tr[idx], y_tr[idx]
        P, z, a, blocks, pooled, scores = forward(imgs)
        e = np.exp(scores - scores.max(axis=1, keepdims=True))
        prob = e / e.sum(axis=1, keepdims=True)
        prob[np.arange(len(idx)), labels] -= 1           # softmax cross entropy gradient
        g = prob / len(idx)
        gWd = pooled.reshape(len(idx), -1).T @ g
        gbd = g.sum(axis=0)
        gpool = (g @ Wd.T).reshape(pooled.shape)
        mask = blocks == pooled[:, :, None, :, None, :]  # where each max came from
        ga = (mask * gpool[:, :, None, :, None, :]).reshape(a.shape)
        gz = ga * (z > 0)
        gWc = P.reshape(-1, 9).T @ gz.reshape(-1, F)
        gbc = gz.reshape(-1, F).sum(axis=0)
        for k, (p, gr) in enumerate(zip((Wc, bc, Wd, bd), (gWc, gbc, gWd, gbd))):
            v[k] = 0.9 * v[k] + gr          # SGD with momentum
            p -= lr * v[k]
    if epoch in (1, 2, 4, 8):
        print(f'epoch {epoch}: train accuracy {accuracy(X_tr, y_tr):.3f}, test accuracy {accuracy(X_te, y_te):.3f}')

n_weights = Wc.size + bc.size + Wd.size + bd.size
print('weights in the network:', n_weights)
''', long=True)

K.code('residual', r'''
# Why residual connections (ResNet) let very deep networks train.
# Compare the gradient that reaches layer 1 in a plain network and in a residual network.
import numpy as np

rng = np.random.default_rng(0)
width, depth = 64, 50
x = rng.normal(size=(128, width))
weights = [rng.normal(scale=0.1 * np.sqrt(2 / width), size=(width, width)) for _ in range(depth)]


def grad_at_first_layer(residual):
    hs, zs = [x], []
    for W in weights:
        z = hs[-1] @ W
        f = np.maximum(z, 0)
        zs.append(z)
        hs.append(hs[-1] + f if residual else f)
    g = np.ones_like(hs[-1]) / len(x)              # gradient of sum(output) / batch
    for W, z in zip(reversed(weights), reversed(zs)):
        branch = (g * (z > 0)) @ W.T
        g = g + branch if residual else branch      # the skip path adds the gradient straight through
    return np.abs(g).mean() * len(x)              # gradient at layer 1 relative to the output gradient


for residual in [False, True]:
    ratio = grad_at_first_layer(residual)
    name = 'residual' if residual else 'plain   '
    print(f'{name} {depth} layers: gradient at layer 1 is {ratio:.2e} times the gradient at the output')

# with the branch weights at zero, a residual block is exactly the identity
h = rng.normal(size=5)
print('zero branch keeps the input:', np.allclose(h + np.maximum(h @ np.zeros((5, 5)), 0), h))
''', long=True)

K.lesson('idea', 'Convolution: a small filter slid over the image', f'''
{src('Goodfellow, Bengio and Courville (2016) sections 9.1 to 9.3, and the Stanford CS231n notes on convolutional networks.')}
{viz('mlconv')}
{wwh('A <b>convolutional layer</b> slides a small grid of weights, the <b>filter</b> or <b>kernel</b>, across the image. At each position it multiplies the filter by the patch under it and adds the results, giving one number of the output <b>feature map</b>. A layer has many filters, each learning to detect one pattern such as an edge, a corner or a texture.',
     'An image has thousands of pixels, so a dense layer would need millions of weights and would have to learn the same pattern separately at every position. A convolution reuses the same few weights everywhere (<b>weight sharing</b>) and looks only at nearby pixels (<b>local connections</b>). It needs far fewer weights and finds a pattern wherever it appears.',
     'Choose the filter size k (3 is the usual choice), the number of filters, the <b>stride</b> s (how far the filter moves) and the <b>padding</b> p (a border of zeros). The output size is &lfloor;(n + 2p &minus; k)/s&rfloor; + 1. With k = 3, p = 1 and s = 1 the size stays the same.')}
{run('conv2d')}
{note('On an image that is dark on the left and bright on the right, the vertical edge filter gives 27 exactly where the brightness jumps and 0 elsewhere, and the horizontal edge filter gives 0 everywhere. A 224 &times; 224 image with a 7 &times; 7 filter, padding 3 and stride 2 gives a 112 &times; 112 output, the first layer of ResNet.', 'exam')}
{fxs(fx('Convolution (as used in deep learning)', 'Y[i, j] = &Sigma;<sub>a, b</sub> X[i&middot;s + a, j&middot;s + b] &middot; K[a, b] + b', 'Strictly a cross correlation: the filter is not flipped.', key=True),
     fx('Output size', 'o = &lfloor;(n + 2p &minus; k) / s&rfloor; + 1', 'Same for height and width.', key=True),
     fx('Weights in a conv layer', 'k &times; k &times; C<sub>in</sub> &times; C<sub>out</sub> + C<sub>out</sub>', 'Independent of the image size.', key=True),
     fx('Same padding', 'p = (k &minus; 1) / 2 for stride 1', 'Keeps the size.'))}
{link('computer-vision', 'Want classical image processing first?', 'The Computer Vision subject covers pixels, filters, edges and features before deep learning.', 'Open Computer Vision')}
''', kw=['convolution', 'filter', 'kernel', 'feature map', 'stride', 'padding', 'weight sharing', 'local connectivity'])

K.lesson('pool', 'Channels, pooling and the receptive field', f'''
{src('Goodfellow, Bengio and Courville (2016) section 9.3, Luo and colleagues, Understanding the effective receptive field (NeurIPS 2016), and Yu and Koltun (ICLR 2016).')}
{viz('mlreceptive')}
{wwh('A colour image has 3 <b>channels</b> (red, green, blue), and each layer outputs one channel per filter, so a filter really spans k &times; k &times; C<sub>in</sub> numbers. <b>Max pooling</b> keeps the largest value in each small window, usually 2 &times; 2, halving the height and width. The <b>receptive field</b> of a unit is the patch of the input image that can affect it.',
     'Pooling (or a convolution with stride 2) shrinks the maps so later layers are cheaper and each unit sees a larger area. It also makes the output change less when the object moves by a pixel or two. A large receptive field lets the top layers recognise whole objects from the small edges found by the bottom layers.',
     'Stack 3 &times; 3 convolutions and downsample by 2 every few layers while doubling the number of channels: this is the shape of VGG and ResNet. Check that the receptive field of the last layer covers the objects you need to see.')}
{run('pooling')}
{note('2 &times; 2 max pooling turns the 4 &times; 4 map into [[6, 5], [7, 9]]. A 3 &times; 3 convolution with 16 filters on a 32 &times; 32 &times; 3 image has 448 weights, while a dense layer producing the same 32 &times; 32 &times; 16 output would need about 50.3 million, 112,384 times more. Through conv, conv, pool, conv, pool, conv the receptive field grows 3, 5, 6, 10, 12, 20.', 'exam')}
{fxs(fx('Receptive field', 'r<sub>l</sub> = r<sub>l&minus;1</sub> + (k<sub>l</sub> &minus; 1) &middot; d<sub>l</sub> &middot; j<sub>l&minus;1</sub>', 'd is the dilation, j the jump.', key=True),
     fx('Jump', 'j<sub>l</sub> = j<sub>l&minus;1</sub> &middot; s<sub>l</sub>', 'Strides multiply.', key=True),
     fx('Max pooling', 'Y[i, j] = max over the window of X', 'No weights to learn.', key=True),
     fx('Global average pooling', 'y<sub>c</sub> = mean over all positions of channel c', 'Replaces big dense layers at the end.'))}
''', kw=['channels', 'max pooling', 'average pooling', 'receptive field', 'dilation', 'downsampling', 'translation invariance'])

K.lesson('train', 'Training a CNN on handwritten digits', f'''
{src('LeCun and colleagues (1998), the scikit-learn digits dataset (UCI optical recognition of handwritten digits), and the CS231n notes on backpropagation through convolution and pooling.')}
{wwh('A complete CNN chains convolution, ReLU and pooling blocks, then flattens the maps and ends with a dense layer and softmax. It is trained with backpropagation like any network. The gradient of a convolution is itself a convolution, and the gradient of max pooling goes only to the position that held the maximum.',
     'Writing one small CNN by hand shows that nothing is magic: the same chain rule from chapter 1.2 handles shared weights by adding up the gradient from every position where the filter was used.',
     'Here the network is conv 3 &times; 3 with 8 filters and padding 1, ReLU, 2 &times; 2 max pooling, then a dense layer to 10 classes. The convolution is done by gathering every 3 &times; 3 patch into a row and multiplying by the filter matrix, the trick (called im2col) that real libraries use too.')}
{run('cnn_digits')}
{note('On the 8 &times; 8 scikit learn digits, trained with SGD with momentum for 8 epochs, test accuracy rises from 0.88 after the first epoch to about 0.97. The network has only 1,370 weights: 80 in the 8 filters and 1,290 in the final dense layer.', 'exam')}
{table(['Layer', 'Output shape', 'Weights'], [
    ['Input', '8 &times; 8 &times; 1', '0'],
    ['Conv 3 &times; 3, 8 filters, padding 1', '8 &times; 8 &times; 8', '9 &times; 8 + 8 = 80'],
    ['ReLU', '8 &times; 8 &times; 8', '0'],
    ['Max pool 2 &times; 2', '4 &times; 4 &times; 8', '0'],
    ['Dense to 10 classes', '10', '128 &times; 10 + 10 = 1,290']])}
{fxs(fx('Filter gradient', '&part;L/&part;K[a, b] = &Sigma;<sub>i, j</sub> &part;L/&part;Y[i, j] &middot; X[i + a, j + b]', 'Summed over every position.', key=True),
     fx('Max pool gradient', 'Goes to the arg max of each window, 0 elsewhere', 'Like a switch.', key=True))}
''', kw=['CNN training', 'im2col', 'convolution gradient', 'max pool gradient', 'digits', 'LeNet'])

K.lesson('arch', 'Famous architectures and residual connections', f'''
{src('LeCun and colleagues (1998), Krizhevsky and colleagues (2012), Simonyan and Zisserman (2015), Szegedy and colleagues, GoogLeNet (CVPR 2015), He and colleagues (CVPR 2016), Tan and Le (ICML 2019), and Dosovitskiy and colleagues (ICLR 2021).')}
{wwh('A <b>residual block</b> adds its input to its output: <b>h</b><sub>out</sub> = <b>h</b> + F(<b>h</b>). The block only has to learn the change F, and if F is zero the block passes its input unchanged. ResNet stacks dozens or hundreds of these blocks.',
     'Before ResNet, adding layers beyond about 20 made accuracy worse, even on the training set, because the gradient faded on its way down. The skip path gives the gradient a direct route to every layer, so networks with 152 layers trained well and won ImageNet 2015.',
     'Use a pretrained ResNet or EfficientNet as a default image model. For very large datasets, vision transformers (chapter 2.3) now match or beat CNNs. For small datasets and phones, CNNs remain strong and efficient.')}
{run('residual')}
{note('With 50 layers and small weights, the gradient that reaches layer 1 of a plain network is 2.7e&minus;50 times the gradient at the output: it has vanished. With the same weights and residual connections it is about 10.5 times the output gradient, because the skip path carries it straight through. Real ResNets also use batch normalisation to keep the sizes steady.', 'exam')}
{table(['Network', 'Year', 'Key idea', 'Depth', 'ImageNet top 5 error'], [
    ['LeNet 5', '1998', 'Conv and pool for digits', '7', 'Not on ImageNet'],
    ['AlexNet', '2012', 'ReLU, dropout, GPUs', '8', '15.3%'],
    ['VGG 16', '2014', 'Only 3 &times; 3 convolutions', '16', '7.3%'],
    ['GoogLeNet', '2014', 'Inception: parallel filter sizes', '22', '6.7%'],
    ['ResNet 152', '2015', 'Residual connections', '152', '3.6%'],
    ['EfficientNet', '2019', 'Balanced scaling of depth, width, resolution', 'Varies', 'About 2.9%'],
    ['Vision transformer', '2020', 'Attention on image patches', '12 to 32', 'Similar or better at scale']])}
{fxs(fx('Residual block', '<b>h</b><sub>l+1</sub> = <b>h</b><sub>l</sub> + F(<b>h</b><sub>l</sub>, W<sub>l</sub>)', 'He and colleagues (2016).', key=True),
     fx('Gradient through a residual block', '&part;L/&part;<b>h</b><sub>l</sub> = &part;L/&part;<b>h</b><sub>l+1</sub>(I + &part;F/&part;<b>h</b><sub>l</sub>)', 'The I keeps the gradient alive.', key=True),
     fx('1 &times; 1 convolution', 'Mixes channels at each pixel: C<sub>in</sub> &times; C<sub>out</sub> weights', 'Used to shrink channels cheaply.'))}
''', kw=['ResNet', 'residual connection', 'skip connection', 'AlexNet', 'VGG', 'GoogLeNet', 'Inception', 'EfficientNet', 'vision transformer', 'ImageNet'])

K.lesson('transfer', 'Transfer learning and data augmentation', f'''
{src('Yosinski and colleagues, How transferable are features in deep neural networks? (NeurIPS 2014), Shorten and Khoshgoftaar, A survey on image data augmentation (2019), and the PyTorch torchvision documentation.')}
{wwh('<b>Transfer learning</b> starts from a network already trained on a large dataset such as ImageNet and adapts it to your task. <b>Feature extraction</b> freezes the pretrained layers and trains only a new final layer. <b>Fine tuning</b> also updates some or all pretrained layers with a small learning rate. <b>Data augmentation</b> creates new training images by flipping, cropping, rotating or recolouring the ones you have.',
     'Early layers learn general features such as edges and textures that are useful for almost any image task. Reusing them means you can reach good accuracy with hundreds of images instead of millions, in minutes instead of days. Augmentation teaches the network that a cat flipped left to right is still a cat, which reduces overfitting.',
     'With little data, freeze the backbone and train the head. With more data, unfreeze the top blocks and fine tune with a learning rate about 10 times smaller. Only use augmentations that keep the label true: flipping a 6 upside down makes a 9.')}
{table(['Your data', 'Similar to ImageNet', 'Different from ImageNet'], [
    ['Small', 'Freeze the backbone, train a new head', 'Freeze early layers, train later ones and the head'],
    ['Large', 'Fine tune the whole network', 'Fine tune everything, or train from scratch']])}
{scene('Classifying plant diseases with 800 photos', 'A farm cooperative has 800 labelled leaf photos in 4 classes. Training a CNN from scratch overfits and reaches about 60% validation accuracy. A ResNet 50 pretrained on ImageNet, with its layers frozen and a new 4 class head, reaches about 90% in a few minutes. Adding random flips, crops and colour changes, then fine tuning the last block with a learning rate of 1e&minus;4, raises it further. The numbers here are illustrative, a typical pattern rather than a measured result.')}
''', kw=['transfer learning', 'fine tuning', 'feature extraction', 'pretrained model', 'data augmentation', 'ImageNet'])

K.lesson('versus', 'CNN, dense network and vision transformer compared', f'''
{versus('Three ways to learn from images', ['', 'Dense network (MLP)', 'Convolutional network', 'Vision transformer'], [
    ['Connections', 'Every pixel to every unit', 'Local window, shared weights', 'Every patch attends to every patch'],
    ['Built in assumptions', 'None', 'Locality and translation equivariance', 'Very few'],
    ['Weights for a 224 &times; 224 image', 'Huge', 'Small, independent of image size', 'Moderate'],
    ['Data needed', 'A lot, and still poor', 'Works well with modest data', 'Needs large data or pretraining'],
    ['Best for', 'Small tabular inputs', 'Most vision tasks, phones and edge devices', 'Large scale vision, multimodal models']],
    'use a pretrained CNN for most image tasks with limited data, and a pretrained vision transformer when you have lots of data or need one model for images and text.')}
''', kw=['CNN vs MLP', 'CNN vs vision transformer', 'inductive bias'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Output size', 'o = &lfloor;(n + 2p &minus; k)/s&rfloor; + 1', 'Per spatial dimension.', key=True),
     fx('Conv weights', '(k&sup2;C<sub>in</sub> + 1) C<sub>out</sub>', 'Bias per filter.', key=True),
     fx('Conv multiply adds', 'o&sup2; &middot; k&sup2; &middot; C<sub>in</sub> &middot; C<sub>out</sub>', 'Where most compute goes.', key=True),
     fx('Receptive field', 'r &larr; r + (k &minus; 1) d j, &nbsp; j &larr; j s', 'Start r = j = 1.', key=True),
     fx('Equivariance', 'conv(shift(X)) = shift(conv(X))', 'Translation equivariance of convolution.'),
     fx('Depthwise separable conv', 'k&sup2;C<sub>in</sub> + C<sub>in</sub>C<sub>out</sub> weights instead of k&sup2;C<sub>in</sub>C<sub>out</sub>', 'MobileNet.'))}
{steps('Worked example: shapes and weights through a small CNN on a 32 &times; 32 &times; 3 image', [
    'Conv 3 &times; 3, 16 filters, padding 1, stride 1: the size stays 32.',
    eq('(32 + 2 &minus; 3)/1 + 1 = 32 &rArr; 32 &times; 32 &times; 16, &nbsp; weights (9 &times; 3 + 1) &times; 16 = 448'),
    'Max pool 2 &times; 2 halves the size and has no weights.',
    eq('16 &times; 16 &times; 16'),
    'Conv 3 &times; 3, 32 filters, padding 1, then pool again.',
    eq('weights (9 &times; 16 + 1) &times; 32 = 4,640, &nbsp; output 8 &times; 8 &times; 32 = 2,048 numbers'),
    'A dense layer from 2,048 numbers to 10 classes has 20,490 weights, so the final dense layer holds most of the weights. Global average pooling would cut it to 32 &times; 10 + 10 = 330.'])}
{deep('Equivariance, inductive bias and what CNNs see', '<p>A convolution is <b>equivariant</b> to translation: shift the input and the feature map shifts the same way. Pooling then adds a little <b>invariance</b>. These built in assumptions, called an <b>inductive bias</b>, are why CNNs learn from far less data than a dense network. In practice, strided layers and padding break exact equivariance, so small shifts can change predictions (Azulay and Weiss 2019, Zhang 2019, who proposed blurring before downsampling). Visualisation studies (Zeiler and Fergus 2014, Olah and colleagues 2017) show early filters detecting edges and colours, middle layers textures and parts, and late layers whole objects. Group equivariant CNNs (Cohen and Welling 2016) extend weight sharing to rotations and reflections. Vision transformers drop most of this bias and recover it from data, which is why they need more of it.</p>')}
''', kw=['output size formula', 'parameter count', 'FLOPs', 'equivariance', 'inductive bias', 'depthwise separable'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A convolutional network looks at an image through many small windows. Early layers spot edges, later layers combine them into shapes and objects.</p>',
    '<p>Compute convolutions and output sizes by hand, build a CNN with conv, ReLU and pooling layers, train it on digits, and use a pretrained ResNet with augmentation for a new task.</p>',
    '<p>Count weights and multiply adds, design receptive fields with strides and dilation, explain residual connections and batch norm, and choose between fine tuning and feature extraction.</p>',
    '<p>Study equivariance and group CNNs, efficient architectures and neural architecture search, the effective receptive field, and the trade offs between convolutions and attention.</p>')}
{grow('Explain how a CNN looks at images.',
      'Build, train and fine tune CNNs.',
      'Design and analyse vision architectures.')}
''', kw=['beginner', 'expert', 'architecture design'])

lc(661, 'Image Smoother', 'image-smoother', 'e', 'Average each cell with its neighbours that exist', 'For every cell, add up the values in the 3 &times; 3 window that fall inside the image and divide by how many there were. This is exactly a blur filter, the first filter in the animation, with the edges handled by counting instead of padding.', r"""
def image_smoother(img):
    m, n = len(img), len(img[0])
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            total = count = 0
            for a in range(max(0, i - 1), min(m, i + 2)):
                for b in range(max(0, j - 1), min(n, j + 2)):
                    total += img[a][b]
                    count += 1
            out[i][j] = total // count
    return out
""", [('image_smoother([[1, 1, 1], [1, 0, 1], [1, 1, 1]])', [[0, 0, 0], [0, 0, 0], [0, 0, 0]]), ('image_smoother([[100, 200, 100], [200, 50, 200], [100, 200, 100]])', [[137, 141, 137], [141, 138, 141], [137, 141, 137]])])
lc(835, 'Image Overlap', 'image-overlap', 'm', 'Count, for every shift, how many 1s line up', 'Pair every 1 in the first image with every 1 in the second and record the shift between them. The shift seen most often gives the largest overlap. Sliding one image over another and counting matches is a cross correlation, the same operation a convolution layer computes.', r"""
def largest_overlap(img1, img2):
    n = len(img1)
    ones1 = [(i, j) for i in range(n) for j in range(n) if img1[i][j]]
    ones2 = [(i, j) for i in range(n) for j in range(n) if img2[i][j]]
    counts = {}
    for a, b in ones1:
        for c, d in ones2:
            shift = (c - a, d - b)
            counts[shift] = counts.get(shift, 0) + 1
    return max(counts.values(), default=0)
""", [('largest_overlap([[1, 1, 0], [0, 1, 0], [0, 1, 0]], [[0, 0, 0], [0, 1, 1], [0, 0, 1]])', 3), ('largest_overlap([[1]], [[1]])', 1), ('largest_overlap([[0]], [[0]])', 0)])
lc(304, 'Range Sum Query 2D, Immutable', 'range-sum-query-2d-immutable', 'm', 'Precompute a 2D prefix sum (an integral image)', 'Store s[i][j], the sum of everything above and to the left. Any rectangle sum is then four lookups. Integral images make box filters cost the same for any window size, and they powered the classic Viola and Jones face detector. Our helper answers a list of queries.', r"""
class NumMatrix:
    def __init__(self, matrix):
        m, n = len(matrix), len(matrix[0])
        self.s = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                self.s[i + 1][j + 1] = matrix[i][j] + self.s[i][j + 1] + self.s[i + 1][j] - self.s[i][j]

    def sumRegion(self, r1, c1, r2, c2):
        s = self.s
        return s[r2 + 1][c2 + 1] - s[r1][c2 + 1] - s[r2 + 1][c1] + s[r1][c1]


def region_sums(matrix, queries):
    nm = NumMatrix(matrix)
    return [nm.sumRegion(*q) for q in queries]
""", [('region_sums([[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]], [(2, 1, 4, 3), (1, 1, 2, 2), (1, 2, 2, 4)])', [8, 11, 12])])
lc(221, 'Maximal Square', 'maximal-square', 'm', 'The square ending at a cell is 1 plus the smallest of its three neighbours', 'dp[i][j] is the side of the largest all 1 square whose bottom right corner is (i, j). It equals 1 plus the minimum of the cells above, to the left and diagonally up left. Each cell depends on a small window of earlier cells, the same local pattern a convolution uses.', r"""
def maximal_square(matrix):
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    best = 0
    for i in range(m):
        for j in range(n):
            if matrix[i][j] == '1':
                dp[i + 1][j + 1] = 1 + min(dp[i][j], dp[i][j + 1], dp[i + 1][j])
                best = max(best, dp[i + 1][j + 1])
    return best * best
""", [("maximal_square([['1', '0', '1', '0', '0'], ['1', '0', '1', '1', '1'], ['1', '1', '1', '1', '1'], ['1', '0', '0', '1', '0']])", 4), ("maximal_square([['0', '1'], ['1', '0']])", 1), ("maximal_square([['0']])", 0)])
lc(85, 'Maximal Rectangle', 'maximal-rectangle', 'h', 'Turn each row into a histogram and find its largest rectangle with a stack', 'Keep, for each column, how many 1s stand above the current row. Each row is then a histogram, and a monotonic stack finds its largest rectangle in one pass. Building up a 2D answer row by row from 1D summaries is how many image algorithms stay fast.', r"""
def maximal_rectangle(matrix):
    heights = [0] * len(matrix[0])
    best = 0
    for row in matrix:
        heights = [h + 1 if v == '1' else 0 for h, v in zip(heights, row)]
        bars = heights + [0]
        stack = []
        for i, h in enumerate(bars):
            while stack and bars[stack[-1]] >= h:
                top = stack.pop()
                left = stack[-1] + 1 if stack else 0
                best = max(best, bars[top] * (i - left))
            stack.append(i)
    return best
""", [("maximal_rectangle([['1', '0', '1', '0', '0'], ['1', '0', '1', '1', '1'], ['1', '1', '1', '1', '1'], ['1', '0', '0', '1', '0']])", 6), ("maximal_rectangle([['0']])", 0), ("maximal_rectangle([['1']])", 1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Convolutional networks work on grids with small sliding windows. These problems practise a blur filter, cross correlation by shifting, an integral image, and dynamic programming over local windows. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'matrix', 'sliding window', 'prefix sum 2D', 'monotonic stack'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>convolution</b> slides a small filter over the image, multiplying and adding. <b>Weight sharing</b> and <b>local connections</b> need far fewer weights than a dense layer.',
    'Output size &lfloor;(n + 2p &minus; k)/s&rfloor; + 1. Weights (k&sup2;C<sub>in</sub> + 1)C<sub>out</sub>, whatever the image size.',
    '<b>Pooling</b> and strides shrink the maps and grow the <b>receptive field</b>: r &larr; r + (k &minus; 1)dj, j &larr; js.',
    '<b>Residual connections</b> h + F(h) let gradients reach early layers, so very deep networks train. LeNet, AlexNet, VGG, ResNet and EfficientNet mark the history.',
    'With little data, use <b>transfer learning</b> from a pretrained network plus <b>data augmentation</b>.'],
    'Deep learning 2.2 moves from grids to sequences with recurrent networks, LSTMs and GRUs.')}
{files('Three tasks: the output size formula, a valid convolution, and 2 &times; 2 max pooling.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A convolutional filter', ['Looks at the whole image at once', 'Slides over the image, multiplying and adding over a small window', 'Sorts the pixels', 'Deletes edges'], 1, 'A small window.', 'The same weights at every position.')
K.quiz('e', 'Weight sharing in a CNN means', ['Two networks share weights', 'The same filter weights are used at every position of the image', 'Weights are shared between classes', 'All weights are equal'], 1, 'One filter everywhere.', 'This saves weights and finds patterns anywhere.')
K.quiz('e', 'Max pooling with a 2 &times; 2 window', ['Doubles the size', 'Keeps the largest value of each window and halves height and width', 'Averages all pixels', 'Adds weights'], 1, 'Largest value.', 'No weights to learn.')
K.quiz('e', 'Padding of 1 with a 3 &times; 3 filter and stride 1', ['Shrinks the image by 2', 'Keeps the output the same size as the input', 'Doubles the size', 'Removes the borders'], 1, '(n + 2 &minus; 3) + 1 = n.', 'Same padding.')
K.quiz('m', 'The number of weights in a conv layer depends on', ['The image size', 'The filter size and the numbers of input and output channels', 'The batch size', 'The number of classes only'], 1, 'k&sup2;C<sub>in</sub>C<sub>out</sub> + C<sub>out</sub>.', 'Not on the image size.')
K.quiz('m', 'Stacking three 3 &times; 3 conv layers instead of one 7 &times; 7 layer', ['Sees less of the image', 'Sees the same 7 &times; 7 area with fewer weights and more nonlinearity', 'Needs more weights', 'Is impossible'], 1, '27 against 49 per channel pair.', 'The VGG idea.')
K.quiz('m', 'A residual block computes', ['F(h) only', 'h + F(h)', 'h &times; F(h)', 'max(h, F(h))'], 1, 'Skip connection.', 'It learns the change.')
K.quiz('m', 'The gradient of max pooling flows', ['Equally to all four inputs', 'Only to the input that held the maximum', 'To none of them', 'To the smallest input'], 1, 'Like a switch.', 'The others did not affect the output.')
K.quiz('m', 'With only 500 labelled images, a good first approach is', ['Train a large CNN from scratch', 'Use a pretrained network, freeze it, and train a new final layer, with augmentation', 'Use a dense network on raw pixels', 'Collect no validation set'], 1, 'Transfer learning.', 'Fine tune later if needed.')
K.quiz('h', 'A convolution is translation equivariant, which means', ['Its output does not change at all when the input shifts', 'Shifting the input shifts the output the same way', 'It works only on centred objects', 'It rotates the image'], 1, 'Equivariant, not invariant.', 'Pooling adds some invariance.')
K.quiz('h', 'A 1 &times; 1 convolution is useful because it', ['Detects edges', 'Mixes channels at each position cheaply, for example to reduce the channel count', 'Increases the receptive field a lot', 'Removes the need for ReLU'], 1, 'Channel mixing.', 'Used in Inception and ResNet bottlenecks.')
K.quiz('h', 'Dilated convolutions grow the receptive field', ['By removing pixels', 'By spacing out the filter taps without pooling or losing resolution', 'By using larger images', 'They do not'], 1, 'Gaps between taps.', 'Popular in segmentation.')
K.quiz('x', 'In the style of a Stanford CS231n exam: input 32 &times; 32 &times; 3, conv with 10 filters of 5 &times; 5, stride 1, padding 2. The number of weights including biases is', ['760', '250', '7,680', '10,240'], 0, '(5 &times; 5 &times; 3 + 1) &times; 10.', '76 per filter.')
K.quiz('x', 'In the style of an Oxford or MIT vision exam: plain networks deeper than about 20 layers trained worse even on training data because', ['They overfit', 'Optimisation became harder as gradients faded, which residual connections fix', 'GPUs ran out of memory', 'ReLU was not used'], 1, 'The degradation problem.', 'He and colleagues (2016).')

K.calc('e', 'Image 6 &times; 6, filter 3 &times; 3, padding 0, stride 1. Output size?', '4', '(n + 2p &minus; k)/s + 1.', ['n + 2p &minus; k = 6 &minus; 3 = 3.', 'Divide by s = 1.', eq('3 + 1 = 4')], check=4)
K.calc('e', 'Conv layer: 3 &times; 3 filters, 3 input channels, 16 filters, with biases. Number of weights?', '448', '(k&sup2;C<sub>in</sub> + 1)C<sub>out</sub>.', ['9 &times; 3 = 27.', 'Plus 1 bias = 28.', eq('28 &times; 16 = 448')], check=448)
K.calc('m', 'Image 32 &times; 32, filter 5 &times; 5, padding 2, stride 1. Output size?', '32', 'Same padding.', ['32 + 4 &minus; 5 = 31.', 'Divide by 1.', eq('31 + 1 = 32')], check=32)
K.calc('m', 'Image 224 &times; 224, filter 7 &times; 7, padding 3, stride 2. Output size?', '112', '&lfloor;(224 + 6 &minus; 7)/2&rfloor; + 1.', ['224 + 6 &minus; 7 = 223.', '&lfloor;223/2&rfloor; = 111.', eq('111 + 1 = 112')], check=112)
K.calc('m', '2 &times; 2 max pooling of the top left window [[1, 3], [4, 6]]. Output?', '6', 'Largest value.', ['Values 1, 3, 4, 6.', 'Take the maximum.', eq('6')], check=6)
K.calc('m', 'Receptive field of three stacked 3 &times; 3 conv layers with stride 1?', '7', 'Each adds k &minus; 1 = 2.', ['Start 1.', '1 + 2 + 2 + 2.', eq('7')], check=7)
K.calc('h', 'Conv 3 &times; 3 from 64 to 128 channels, with biases. Number of weights?', '73856', '(9 &times; 64 + 1) &times; 128.', ['9 &times; 64 = 576.', '577 &times; 128.', eq('73,856')], check=73856)
K.calc('h', 'Padding needed to keep the size with a 5 &times; 5 filter and stride 1?', '2', '(k &minus; 1)/2.', ['k &minus; 1 = 4.', 'Half of it.', eq('2')], check=2)
K.calc('h', 'Input 32 &times; 32 &times; 3, 10 filters of 5 &times; 5, stride 1, padding 2. Numbers in the output volume?', '10240', 'o &times; o &times; C<sub>out</sub>.', ['o = (32 + 4 &minus; 5) + 1 = 32.', '32 &times; 32 = 1,024.', eq('1,024 &times; 10 = 10,240')], check=10240)
K.calc('x', 'In the style of a Stanford CS231n problem: receptive field after conv 3 &times; 3, pool 2 &times; 2 (stride 2), conv 3 &times; 3, pool 2 &times; 2, conv 3 &times; 3?', '18', 'r &larr; r + (k &minus; 1)j, j &larr; js.', ['Conv: 3. Pool: 3 + 1 = 4, j = 2.', 'Conv: 4 + 2 &times; 2 = 8. Pool: 8 + 1 &times; 2 = 10, j = 4.', eq('Conv: 10 + 2 &times; 4 = 18')], check=18)

K.assign('conv_output_size', 'e', 'The output size formula',
         '<p>Write <code>conv_output_size(n, k, p, s)</code> that returns the output size of a convolution on an n &times; n input with a k &times; k filter, padding p and stride s.</p>',
         """
def conv_output_size(n, k, p, s):
    # your code here
    pass
""", [('conv_output_size(6, 3, 0, 1)', 4), ('conv_output_size(224, 7, 3, 2)', 112), ('conv_output_size(7, 3, 0, 2)', 3)],
         """
def conv_output_size(n, k, p, s):
    return (n + 2 * p - k) // s + 1
""", 'Add the padding on both sides, subtract the filter size, divide by the stride with floor division, and add 1.', '<p>If (n + 2p &minus; k) is not divisible by s, the last pixels are simply skipped, which is why the formula uses floor division.</p>')
K.assign('conv2d_valid', 'm', 'A valid convolution',
         '<p>Write <code>conv2d_valid(image, kernel)</code> for lists of lists: slide the square kernel over the image with stride 1 and no padding, and return the output grid of sums of products (no flipping, as in deep learning).</p>',
         """
def conv2d_valid(image, kernel):
    # your code here
    pass
""", [('conv2d_valid([[0, 0, 9, 9]] * 4, [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])', [[27, 27], [27, 27]]), ('conv2d_valid([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 0], [0, -1]])', [[-4, -4], [-4, -4]])],
         """
def conv2d_valid(image, kernel):
    n, k = len(image), len(kernel)
    out = []
    for i in range(n - k + 1):
        row = []
        for j in range(len(image[0]) - k + 1):
            row.append(sum(image[i + a][j + b] * kernel[a][b] for a in range(k) for b in range(k)))
        out.append(row)
    return out
""", 'For each top left position, multiply the k &times; k patch by the kernel element by element and add up.', '<p>Libraries do the same work much faster by turning patches into rows of a matrix (im2col) or with fast Fourier transforms for large filters.</p>')
K.assign('max_pool_2x2', 'm', '2 &times; 2 max pooling',
         '<p>Write <code>max_pool_2x2(fmap)</code> that takes a square list of lists with an even size and returns the 2 &times; 2 max pooled grid with stride 2.</p>',
         """
def max_pool_2x2(fmap):
    # your code here
    pass
""", [('max_pool_2x2([[1, 3, 2, 1], [4, 6, 5, 0], [7, 2, 9, 8], [1, 0, 3, 4]])', [[6, 5], [7, 9]]), ('max_pool_2x2([[1, 2], [3, 4]])', [[4]])],
         """
def max_pool_2x2(fmap):
    n = len(fmap)
    return [[max(fmap[i][j], fmap[i][j + 1], fmap[i + 1][j], fmap[i + 1][j + 1])
             for j in range(0, n, 2)] for i in range(0, n, 2)]
""", 'Step through the grid two at a time in both directions and keep the largest of the four values.', '<p>Average pooling would take the mean of the four values instead. Global average pooling takes the mean over the whole map.</p>')

K.must('Convolution', 'Slide a k &times; k filter, multiply and add. Weight sharing, local connections. Output &lfloor;(n + 2p &minus; k)/s&rfloor; + 1.')
K.must('Weights', '(k&sup2;C<sub>in</sub> + 1)C<sub>out</sub> per conv layer, independent of image size. 1 &times; 1 conv mixes channels.')
K.must('Pooling', 'Max or average over windows, halves the size, no weights. Gradient goes to the arg max.')
K.must('Receptive field', 'r &larr; r + (k &minus; 1)dj, j &larr; js. Three 3 &times; 3 = one 7 &times; 7 with fewer weights.')
K.must('Architectures', 'LeNet, AlexNet (ReLU, GPUs), VGG (3 &times; 3), GoogLeNet (Inception), ResNet (h + F(h)), EfficientNet, ViT.')
K.must('Practice', 'Pretrained backbone, new head, augmentation that keeps labels true, then fine tune with a smaller learning rate.')

T = K.topic(
    slug='dl-cnn', topic='dl-cnn', step=(2, 'Architectures', 'dl-s2', 'The three big families of deep networks: convolutional networks for images, recurrent networks for sequences, and transformers built on attention.', 'Advanced'),
    title='Convolutional neural networks', short='Convolutional networks', badge='2.1', minutes=60,
    lead='See how networks learn from images: convolution, stride and padding, pooling and the receptive field, a CNN trained by hand on digits, residual networks, famous architectures, and transfer learning.',
    desc='convolutional neural network, CNN, convolution, filter, kernel, feature map, stride, padding, channels, max pooling, receptive field, dilation, weight sharing, im2col, LeNet, AlexNet, VGG, GoogLeNet, ResNet, residual connection, EfficientNet, vision transformer, transfer learning, fine tuning, data augmentation.',
    summary='Convolution, pooling, receptive fields, a hand built CNN, ResNet and transfer learning.',
    keywords=['CNN', 'convolution', 'pooling', 'receptive field', 'ResNet', 'residual connection', 'transfer learning', 'data augmentation', 'stride', 'padding'],
    recap='<p>Small shared filters slide over the image to find local patterns, pooling and stacking grow what each unit sees, and residual connections let very deep networks train. Pretrained CNNs and augmentation make it work with little data.</p>',
    added='2026-11-14', leet=leet_items())
