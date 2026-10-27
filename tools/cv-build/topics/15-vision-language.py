# Chapter 15: connecting vision and language, and beyond 2D. Low and high level vision, CLIP and contrastive
# learning, zero-shot classification and prompts, vision transformers for dense prediction, mask classification,
# SAM and language-guided segmentation, DALL-E and generative models, restoration and super-resolution,
# 3D reconstruction and triangulation.
# Sources: lecture 2 (3D reconstruction, CLIP, DALL-E, low and high level vision, restoration, super-resolution)
# and lectures 7 and 8, chapter 14 (transformers, SegFormer, MaskFormer, SAM, open vocabulary segmentation).
# Facts checked: CLIP (Radford and colleagues, 2021) trained on 400 million image-text pairs with a batch of 32,768,
# SAM (Kirillov and colleagues, 2023) with SA-1B of 11 million images and 1.1 billion masks, ViT (2020), stereo Z = fB/d.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('cosine', r'''
# Cosine similarity between two embeddings
from math import sqrt
a = [float(v) for v in input("image embedding: ").split()]
b = [float(v) for v in input("text embedding: ").split()]

dot = sum(x * y for x, y in zip(a, b))
na = sqrt(sum(x * x for x in a))
nb = sqrt(sum(y * y for y in b))
print("dot product", round(dot, 3))
print("lengths", round(na, 3), round(nb, 3))
print("cosine similarity", round(dot / (na * nb), 3))
''', stdin='1 2 2\n2 1 2\n')

K.code('zeroshot', r'''
# Zero-shot classification: compare one image embedding with one prompt per class
from math import sqrt, exp
prompts = {"a photo of a dog": [0.9, 0.3, 0.1],
           "a photo of a cat": [0.6, 0.7, 0.2],
           "a photo of a car": [0.1, 0.2, 0.95]}
image = [float(v) for v in input("image embedding: ").split()]
scale = 100                                          # CLIP's learned logit scale is about 100

def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (sqrt(sum(x * x for x in a)) * sqrt(sum(y * y for y in b)))

sims = {t: cos(image, v) for t, v in prompts.items()}
top = max(sims.values())
weights = {t: exp(scale * (s - top)) for t, s in sims.items()}
total = sum(weights.values())
for t in prompts:
    print(t.ljust(18), "cos", round(sims[t], 3), " p", round(weights[t] / total, 3))
print("prediction:", max(sims, key=sims.get))
''', stdin='0.85 0.4 0.1\n')

K.code('stereo', r'''
# Depth from disparity with two cameras
f = 700.0                                            # focal length in pixels
B = float(input("baseline in metres: "))
d = float(input("disparity in pixels: "))

Z = f * B / d
print("depth Z = f B / d =", round(Z, 3), "m")
for err in (0.5, 1.0, 2.0):
    Z2 = f * B / (d - err)
    print("disparity off by", err, "px -> depth", round(Z2, 3), "m, error", round(Z2 - Z, 3), "m")
''', stdin='0.12\n42\n')

K.lesson('bridge', 'From pixels to meaning to words', f'''
<p>The lecturer split vision into two levels. <b>Low level vision</b> works on the signal: brightness, contrast, colour, noise, edges, blur, sharpness and resolution. <b>High level vision</b> works on meaning: classification, detection, scene recognition, activity recognition, captioning and visual question answering.</p>
{fx('The processing ladder', 'pixels → edges and textures → shapes → objects → scenes and activities', 'Pixel changes reveal edges, edges form shapes, shapes reveal objects, and objects with their relations describe the scene.', key=True)}
<p>Everything up to now used a fixed list of classes: 20 for VOC, 80 for COCO, 19 for Cityscapes. Adding a class meant collecting and labelling new data. Language removes that limit. If a model understands that a picture matches the words a photo of a zebra, any class that can be described becomes available.</p>
{table(['Model', 'Question it answers', 'Output'], [
    ['CLIP', 'Which text best matches this image?', 'Similarity scores, zero-shot labels'],
    ['DALL-E', 'What image should be created from this text?', 'A new image'],
    ['SAM', 'Which pixels belong to the object I point at?', 'Masks, without class names'],
    ['Language-guided segmentation', 'Which pixels match this phrase?', 'A mask for the phrase']])}
{note('Some models now beat the estimated human error on the ImageNet benchmark. The lecturer\'s caution: that is task specific. The same models can still fail under unusual conditions, distribution shift, adversarial changes, occlusion and new categories. Benchmark superiority is not general intelligence.', 'warn')}
''', kw=['low level vision', 'high level vision', 'processing ladder', 'fixed classes', 'vision and language', 'benchmark', 'human level'])

K.lesson('clip', 'CLIP: one space for images and text', f'''
<p><b>CLIP</b> (Radford and colleagues, OpenAI, 2021) learns from about 400 million image and caption pairs collected from the web. It has two encoders: an <b>image encoder</b> (a ResNet or a vision transformer) and a <b>text encoder</b> (a transformer). Each turns its input into an <b>embedding</b>, a vector that represents meaning. Both land in one shared space where an image of a dog lies close to the text a photo of a dog and far from a red motorcycle.</p>
{fx('Cosine similarity', 'cos(<i>x</i>, <i>y</i>) = ' + frac('<i>x</i> · <i>y</i>', '‖<i>x</i>‖ ‖<i>y</i>‖'), 'Between −1 and 1. It ignores length and compares direction only.', key=True)}
{steps('Cosine by hand', [
    'Image embedding x = (1, 2, 2) and text embedding y = (2, 1, 2).',
    'Dot product: 2 + 2 + 4 = 8. Lengths: √9 = 3 and √9 = 3.',
    'cos = 8 ÷ 9 ≈ 0.889, a close match.'])}
{code('cosine')}
<h3>Contrastive learning</h3>
<p>A batch holds N images and their N captions. Every image is compared with every caption, giving an N × N grid of similarities. The N matching pairs on the diagonal are positives, the other N² − N cells are negatives. Training pulls the diagonal up and pushes everything else down.</p>
{fx('Symmetric contrastive loss', '<i>L</i> = ½ [ CE<sub>rows</sub>(<i>S</i> ÷ τ) + CE<sub>columns</sub>(<i>S</i> ÷ τ) ]', 'Each row is a SoftMax over captions whose correct answer is the diagonal, and each column the same over images. τ is a learned temperature. CLIP used batches of 32,768 pairs, so each image had 32,767 negatives.', key=True)}
{viz('cliptrain')}
<h3>Zero-shot classification</h3>
<p>At test time, write one prompt per class: a photo of a dog, a photo of a cat, a photo of a horse. Embed the prompts once, embed the image, and pick the prompt with the highest similarity. No labelled training set for these classes is needed, which is what <b>zero-shot</b> means here.</p>
{viz('zeroshot')}
{code('zeroshot')}
{table(['Training', 'Inference'], [
    ['Image and caption pairs go in', 'One image and a list of class prompts go in'],
    ['Both encoders produce embeddings', 'Prompts are embedded once and reused'],
    ['All pairwise similarities in the batch', 'Similarity of the image with each prompt'],
    ['The contrastive loss updates both encoders', 'The highest similarity gives the class']])}
<p>Wording matters. A photo of a dog, an image of a dog and a close-up picture of a dog give slightly different embeddings, so the prompt is part of the classifier. Averaging several wordings per class, called prompt ensembling, usually helps.</p>
{note('CLIP and SAM both take prompts but answer different questions. CLIP says what an image corresponds to and outputs scores. SAM says which pixels belong to the object and outputs masks.', 'exam')}
''', kw=['CLIP', 'image encoder', 'text encoder', 'embedding', 'shared space', 'cosine similarity', 'contrastive learning', 'InfoNCE', 'temperature', 'negatives', 'zero-shot', 'prompt', 'prompt ensembling'])

K.lesson('transformers', 'Transformers for dense prediction', f'''
<p>The vision transformer (ViT, Dosovitskiy and colleagues, 2020) was introduced in chapter 4.1. A student asked how it differs from the transformer used for text. The lecturer: in NLP each word is a token, in vision the image is cut into patches and each patch is one token. The transformer block itself, self-attention plus a small MLP, is the same.</p>
<p>Why use it for segmentation? Pixel labels often depend on long range context: road against wall, river against shadow. Self-attention lets every position exchange information with every other one in a single layer. A CNN needs many layers or dilation to see that far. The price is cost.</p>
{fxs(
    fx('Tokens', '<i>N</i> = (<i>n</i> ÷ <i>p</i>)²', 'n image side, p patch side. A 224 image with 16 × 16 patches gives 14² = 196 tokens of 16 · 16 · 3 = 768 numbers each.', key=True),
    fx('Attention pairs', 'global: <i>N</i>², &nbsp; windowed: (<i>N</i> ÷ <i>w</i>²) · (<i>w</i>²)²', 'w tokens per window side.'))}
{viz('vitcost')}
{steps('How quickly attention grows', [
    '224 × 224, patch 16: 196 tokens, 196² = 38,416 pairs per head.',
    '512 × 512: 32² = 1,024 tokens and 1,048,576 pairs, 27.3 times more for 5.2 times more pixels.',
    'Patch 4 on 224 gives 56 × 56 = 3,136 tokens and 9,834,496 global pairs.',
    'Swin style 7 × 7 windows: 64 windows × 49² = 153,664 pairs, 64 times fewer.'])}
<h3>Two common confusions</h3>
<ul>
<li><b>Is a patch a vocabulary word?</b> No. A text vocabulary is a fixed table of IDs. A patch is a continuous vector of pixel values mapped to an embedding by a learned linear layer. Patch equals token is right, patch equals vocabulary word is not.</li>
<li><b>How does positional encoding work?</b> In the original ViT it is a learned table, one vector per patch position, added to the tokens and trained with everything else. Swin uses relative position bias, and SegFormer drops explicit encodings and lets a 3 × 3 convolution inside the feed forward layer supply position.</li>
</ul>
<h3>SegFormer and mask classification</h3>
<p><b>SegFormer</b> (2021) is a simple modern design: a hierarchical transformer encoder with four stages at strides 4, 8, 16 and 32, the transformer version of a CNN pyramid, plus a light all-MLP decoder that upsamples every stage to 1/4 size, concatenates and predicts.</p>
<p><b>Mask classification</b> (MaskFormer 2021, Mask2Former 2022) changes the question. Instead of H × W × C logits, N learned queries each produce one mask and one class, including no object. Training matches predictions to true segments one to one with the Hungarian algorithm, as in DETR. Because the output is a set of (mask, class) pairs, one model handles semantic, instance and panoptic segmentation.</p>
''', kw=['vision transformer', 'ViT', 'patch', 'token', 'self-attention', 'attention cost', 'windowed attention', 'Swin', 'positional encoding', 'SegFormer', 'MaskFormer', 'Mask2Former', 'mask classification', 'Hungarian matching'])

K.lesson('sam', 'Promptable and language-guided segmentation', f'''
<p>The lecturer: after DeepLab, backbones moved to transformers, then to foundation models where the prompt is an input, for example segment only the pedestrian in this image.</p>
<h3>Segment Anything (SAM)</h3>
<p>Released by Meta AI in 2023. Three parts: a large ViT image encoder that runs once per image, a prompt encoder for points, boxes or rough masks, and a light mask decoder that returns several candidate masks with quality scores when a prompt is ambiguous. It was trained on SA-1B, about 11 million images and 1.1 billion masks, built with a data engine in which the model itself helped annotate. That is about 100 masks per image.</p>
{note('SAM is class agnostic. It tells you where an object is, not what it is. Pair it with a detector or CLIP when you need names.', 'warn')}
<p>A student asked what promptable means. The lecturer compared it with ChatGPT: whatever you write is the prompt. Here the prompt tells the model which object to segment, as a click, a box or a phrase. One frozen model serves many tasks without retraining, which is what foundation model means.</p>
<h3>Open vocabulary and language-guided masks</h3>
<p>Classic segmentation has a fixed class list. Language-guided segmentation takes a query such as segment the red car and returns the matching region. Labels can come from text, models move beyond fixed datasets, and masks connect to captions, grounding, question answering and agents. The slide called this the bridge from the vision half of the course to the language half.</p>
{table(['Building block', 'What it does'], [
    ['CLIP', 'Aligns whole images with text'],
    ['LSeg, OpenSeg', 'Align per pixel embeddings with the text embedding of a class name'],
    ['CLIPSeg', 'Segments from a text or image prompt'],
    ['Grounded-SAM', 'A text driven detector (Grounding DINO) finds boxes, SAM turns them into masks']])}
{deep('Conditioning, guidance, grounding and VQA', '<p>The lecturer explained language conditioning with an example: make my face a smiling face. The text is a condition on what the model produces. Language guided stresses a query at inference time that steers the output. Mechanically both feed text embeddings into the network, by concatenation, cross-attention or feature scaling, and the terms overlap in practice.</p><p>Segment the red car is strictly <b>referring expression segmentation</b>, a grounding task whose answer is a mask. <b>Visual question answering</b> answers with text, such as what colour is the car. Both need the same image and text alignment, which is why the slide links them.</p>')}
''', kw=['SAM', 'Segment Anything', 'promptable', 'foundation model', 'SA-1B', 'class agnostic', 'open vocabulary', 'language guided segmentation', 'CLIPSeg', 'Grounded-SAM', 'referring expression', 'VQA', 'conditioning'])

K.lesson('generate', 'Generating and restoring images', f'''
<p><b>DALL-E</b> (OpenAI, 2021) creates images from text, such as an armchair shaped like an avocado. A text to image model must read the prompt, find the objects and attributes, understand how they relate, and compose a plausible scene. In a red motorcycle standing in a garage it must keep the object (motorcycle), the colour (red), the state (standing) and the place (garage).</p>
{table(['', 'CLIP', 'DALL-E'], [
    ['Direction', 'Aligns images and text', 'Text to image'],
    ['Main task', 'Matching or classification', 'Creating a new image'],
    ['Output', 'Similarity or a class', 'A generated image'],
    ['Objective', 'Align embeddings', 'Generate images conditioned on text']])}
<p>Early generators struggled with object counts, human hands, text inside images, spatial relations, consistency and long prompts. The lecturer asked students to check which of these problems remain open.</p>
{table(['Generative family', 'Idea', 'Where in this course'], [
    ['GAN', 'A generator and a discriminator compete', 'Chapter 5.2, the GAN story'],
    ['VAE', 'Encode to a distribution, sample, decode', 'Chapter 6.2, side topic'],
    ['Diffusion', 'Learn to remove noise step by step, usually with a U-Net denoiser', 'Chapter 6.2 mentions the U-Net inside'],
    ['Autoregressive', 'Predict image tokens one after another, like text', 'The first DALL-E']])}
<h3>Restoration</h3>
<p>Restoration tries to recover the true image from a degraded one: noise, blur, motion, compression, sensor limits, poor light, low resolution. It is not the same as making the picture look nice. Its history runs through space and medicine: enhancing lunar images from the Ranger 7 mission in the 1960s and tomographic reconstruction in the 1970s.</p>
<p>The lecturer\'s research example: expensive MRI scanners give clean images slowly, faster or cheaper scans give noisier ones, and a model trained on pairs maps low quality to high quality. That could cut exam time and cost, but raises a safety question: how do we know the restored image is medically correct? Use separate training, validation and test sets, clinical benchmarks, expert review against the original, and clinical measures such as whether lesions and boundaries are preserved.</p>
<h3>Super-resolution</h3>
<p>A student asked how a model can produce a high resolution image when none exists at deployment. During training it sees pairs and learns f(low resolution) ≈ high resolution. At deployment it applies f to a new image. That is inference, not recovery: the model fills in plausible details that may not match the true scene.</p>
{note('A visually attractive restored image can still contain wrong information. In medicine, legal evidence and inspection, invented detail is dangerous, so validate restoration on the task it serves, not on how it looks.', 'warn')}
''', kw=['DALL-E', 'text to image', 'generative models', 'GAN', 'VAE', 'diffusion', 'restoration', 'MRI', 'super-resolution', 'hallucination', 'validation'])

K.lesson('threed', '3D from many photographs', f'''
<p>A camera flattens the 3D world into 2D. <b>3D reconstruction</b> recovers the shapes, positions and scene geometry, and the camera viewpoints, from several images. The lecture showed Building Rome in a Day (Agarwal and colleagues, ICCV 2009), which reconstructed city landmarks from ordinary internet photos taken by different people, with different cameras, resolutions and lighting.</p>
<ol>
<li><b>Match features.</b> Find the same physical points in several photos: corners, textures, architectural details. This is where SIFT style keypoints from chapter 1.2 earn their place.</li>
<li><b>Estimate camera poses.</b> Where each camera stood and which way it faced.</li>
<li><b>Triangulate.</b> Each match gives one viewing ray per camera. The rays meet at the 3D point.</li>
</ol>
{fxs(
    fx('Stereo depth', '<i>Z</i> = ' + frac('<i>f</i> <i>B</i>', '<i>d</i>'), 'f focal length in pixels, B baseline between the cameras, d disparity: how far the point shifts between the two images.', key=True),
    fx('Depth error', 'Δ<i>Z</i> ≈ ' + frac('<i>Z</i>²', '<i>f</i> <i>B</i>') + ' Δ<i>d</i>', 'Error grows with the square of distance and falls with a wider baseline.'))}
{viz('triangulate')}
{steps('Depth from disparity', [
    'f = 700 pixels, B = 0.12 m, and the point shifts by d = 42 pixels.',
    'Z = 700 × 0.12 ÷ 42 = 2 m.',
    'A 1 pixel mistake: Z² ÷ (fB) = 4 ÷ 84 ≈ 0.048 m, about 5 cm.',
    'At 8 m the disparity is only 10.5 pixels and the same mistake costs about 0.8 m.'])}
{code('stereo')}
<p>Good reconstructions are used in digital maps, heritage preservation, architecture, robotics, augmented and virtual reality, urban planning, film and navigation. They are not perfect copies. Errors come from wrong matches, repeated textures, moving objects, poor light, occlusion and weak camera geometry.</p>
{ladder(
    '<p>Some models now understand pictures and words together. They can sort photos into categories you just type in, cut out whatever you click on, or draw a new picture from a sentence. Two cameras can also tell how far away something is, the same way your two eyes do.</p>',
    '<p>CLIP maps images and text into one space and is trained to pull matching pairs together. Zero-shot classification picks the prompt with the highest cosine similarity. SAM returns masks for points or boxes. Stereo depth is Z = fB ÷ d.</p>',
    '<p>CLIP uses a symmetric cross-entropy over an N × N similarity matrix with a learned temperature. ViT attention costs N² in the number of tokens, so dense models use hierarchy and windows. Mask classification predicts (mask, class) sets with Hungarian matching. Depth error grows as Z² ÷ (fB).</p>',
    '<p>Current work extends these ideas: open vocabulary detectors and segmenters, vision language models that answer questions and follow instructions, diffusion models that edit images under text control, and neural scene representations (NeRF, Gaussian splatting) that replace classic multi-view stereo for novel view synthesis.</p>')}
''', kw=['3D reconstruction', 'triangulation', 'camera pose', 'feature matching', 'stereo', 'disparity', 'baseline', 'depth error', 'Building Rome in a Day', 'structure from motion'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'CLIP has', ['One encoder for images only', 'An image encoder and a text encoder that share one embedding space', 'A segmentation head', 'A box regressor'], 1,
       'Two inputs, one space.', 'Matching images and captions land close together.')
K.quiz('e', 'Zero-shot classification with CLIP needs', ['A labelled dataset for each new class', 'Only a text prompt per class', 'Retraining the image encoder', 'Bounding boxes'], 1,
       'Classes are text.', 'The prompt with the highest similarity to the image wins.')
K.quiz('e', 'SAM outputs', ['Class names', 'Masks for the object the prompt points at, without class names', 'Captions', 'Depth maps'], 1,
       'Class agnostic.', 'Pair it with a detector or CLIP to name the object.')
K.quiz('m', 'In a CLIP batch of N pairs, how many negatives does each image have?', ['1', 'N − 1', 'N', 'N²'], 1,
       'Every caption except its own.', 'The other N − 1 captions in the batch.')
K.quiz('m', 'In a vision transformer a token is', ['A word from a fixed vocabulary', 'One image patch turned into an embedding', 'One pixel', 'One class'], 1,
       'Patch equals token.', 'There is no vocabulary table. A learned linear layer maps each patch to an embedding.')
K.quiz('m', 'Doubling the image side with the same patch size multiplies global attention pairs by', ['2', '4', '8', '16'], 3,
       'Tokens grow 4 times, pairs are tokens squared.', '4² = 16.')
K.quiz('m', 'CLIP and DALL-E differ because', ['They are the same model', 'CLIP matches images with text, DALL-E creates images from text', 'DALL-E classifies', 'CLIP generates images'], 1,
       'Direction of the task.', 'Matching against generation.')
K.quiz('h', 'Why can a super-resolution model not guarantee the true details?', ['It is too slow', 'It applies a mapping learned from training pairs, so it fills in plausible details rather than recovering missing ones', 'It uses JPEG', 'It needs the original'], 1,
       'Inference, not recovery.', 'Validate it on the task, especially in medicine.')
K.quiz('h', 'Mask classification models such as Mask2Former output', ['H × W × C logits only', 'A set of (mask, class) pairs from learned queries', 'Boxes', 'Captions'], 1,
       'Queries and Hungarian matching.', 'The same model can do semantic, instance and panoptic output.')
K.quiz('h', 'Segment the red car is best described as', ['Visual question answering', 'Referring expression segmentation', 'Image captioning', 'Depth estimation'], 1,
       'The answer is a mask.', 'VQA answers with text.')
K.quiz('x', 'In stereo, the same 1 pixel matching error at 4 times the distance gives a depth error about', ['the same', '4 times larger', '16 times larger', '4 times smaller'], 2,
       'ΔZ ≈ Z² Δd ÷ (fB).', 'Error grows with distance squared.')
K.quiz('x', 'What does the CLIP temperature τ do?', ['Changes the image size', 'Scales similarities before SoftMax, a small τ sharpens the probabilities', 'Adds noise', 'Sets the batch size'], 1,
       'Divide by τ.', 'CLIP learns τ, and its logit scale 1 ÷ τ ends up near 100.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Cosine similarity of (1, 0) and (0.6, 0.8)?', '0.6', 'Dot product over lengths.',
       ['Dot product 0.6.', 'Both lengths are 1.', eq('cos = 0.6')], check=0.6)
K.calc('e', 'A 224 × 224 image with 16 × 16 patches. How many tokens?', '196', '(n ÷ p)².',
       ['224 ÷ 16 = 14.', '14 × 14.', eq('196 tokens')], check=196)
K.calc('e', 'f = 700 px, B = 0.12 m, disparity 42 px. What is the depth in metres?', '2', 'Z = fB ÷ d.',
       ['fB = 84.', '84 ÷ 42.', eq('Z = 2 m')], check=2)
K.calc('m', 'Cosine similarity of (1, 2, 2) and (2, 1, 2)? Give three decimals.', '0.889', 'Dot product over lengths.',
       ['Dot = 2 + 2 + 4 = 8.', 'Lengths 3 and 3.', eq('cos = 8 ÷ 9 ≈ 0.889')], check=8 / 9, tol=0.0006)
K.calc('m', 'How many global attention pairs does a 196 token ViT have per head?', '38416', 'N².',
       ['Every token with every token.', '196 × 196.', eq('38,416')], check=38416)
K.calc('m', '3,136 tokens (56 × 56) in 7 × 7 windows. How many attention pairs?', '153664', 'Windows × 49².',
       ['56 ÷ 7 = 8, so 64 windows.', '49² = 2,401 pairs per window.', eq('64 × 2,401 = 153,664')], check=153664)
K.calc('m', 'How many tokens does a 512 × 512 image have with 16 × 16 patches?', '1024', '(n ÷ p)².',
       ['512 ÷ 16 = 32.', '32 × 32.', eq('1,024 tokens')], check=1024)
K.calc('h', 'With f = 700 px and B = 0.12 m, about how large is the depth error at 8 m for a 1 pixel disparity error? Give three decimals (rule of thumb).', '0.762', 'Z² ÷ (fB).',
       ['Z² = 64.', 'fB = 84.', eq('64 ÷ 84 ≈ 0.762 m')], check=64 / 84, tol=0.0006)
K.calc('h', 'CLIP trained with batches of 32,768 pairs. How many negatives does each image see?', '32767', 'All captions but its own.',
       ['N = 32,768.', 'One caption is the positive.', eq('N − 1 = 32,767')], check=32767)
K.calc('h', 'Two prompts have cosines 0.30 and 0.25 with an image. With logit scale 100, what probability goes to the first? Give three decimals.', '0.993', 'SoftMax of 30 and 25.',
       ['Logits 30 and 25, a gap of 5.', 'p = 1 ÷ (1 + e<sup>−5</sup>).', eq('p ≈ 0.993')], check=1 / (1 + 2.718281828 ** -5), tol=0.0006)
K.calc('x', 'SA-1B has about 1.1 billion masks on 11 million images. About how many masks per image?', '100', 'Divide.',
       ['1.1 × 10<sup>9</sup> masks.', '1.1 × 10<sup>7</sup> images.', eq('about 100 masks per image')], check=100)
K.calc('x', 'One CLIP row has similarities 0.9 (correct caption), 0.2 and 0.1, with τ = 1. What is the row loss? Give three decimals.', '0.666', '−ln of the SoftMax probability of the correct caption.',
       ['e<sup>0.9</sup> = 2.460, e<sup>0.2</sup> = 1.221, e<sup>0.1</sup> = 1.105.', 'p = 2.460 ÷ 4.786 ≈ 0.514.', eq('loss = −ln 0.514 ≈ 0.666'), 'With τ = 0.1 the same row would cost about 0.001.'], check=0.6656, tol=0.0011)

# ---------------------------------------------------------------- assignments
K.assign('cos', 'e', 'Cosine similarity',
         '<p>Write <code>cos_sim(a, b)</code> for two lists of numbers. Return the cosine similarity rounded to 3 decimals, or 0.0 if either vector has length 0.</p>',
         '''
from math import sqrt

def cos_sim(a, b):
    # your code here
    pass
''', [('cos_sim([1, 2, 2], [2, 1, 2])', 0.889), ('cos_sim([1, 0], [0, 1])', 0.0), ('cos_sim([1, 1], [-2, -2])', -1.0), ('cos_sim([0, 0], [1, 2])', 0.0)],
         '''
from math import sqrt

def cos_sim(a, b):
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return round(sum(x * y for x, y in zip(a, b)) / (na * nb), 3)
''', 'Dot product divided by the two lengths. Guard the zero vector first.',
         '<p>Opposite directions give −1, perpendicular ones 0. CLIP normalises its embeddings, so cosine equals the dot product there.</p>')
K.assign('zeroshot', 'm', 'Zero-shot classifier',
         '<p>Write <code>classify(image, prompts, scale=100)</code>. <code>prompts</code> maps a label to its text embedding. Return <code>[label, p]</code>: the label with the highest cosine similarity and its SoftMax probability over scale × cosine, rounded to 3 decimals.</p>',
         '''
from math import sqrt, exp

def classify(image, prompts, scale=100):
    # your code here
    pass
''', [("classify([1, 0], {'dog': [1, 0.1], 'cat': [0.1, 1]})", ['dog', 1.0]),
      ("classify([1, 1], {'dog': [1, 0], 'cat': [0, 1]}, 1)", ['dog', 0.5]),
      ("classify([0.3, 1], {'dog': [1, 0.2], 'cat': [0.2, 1], 'car': [-1, 0]}, 10)", ['cat', 0.995])],
         '''
from math import sqrt, exp

def classify(image, prompts, scale=100):
    def cos(a, b):
        return sum(x * y for x, y in zip(a, b)) / (sqrt(sum(x * x for x in a)) * sqrt(sum(y * y for y in b)))
    sims = {k: cos(image, v) for k, v in prompts.items()}
    top = max(sims.values())
    w = {k: exp(scale * (s - top)) for k, s in sims.items()}
    best = max(sims, key=sims.get)
    return [best, round(w[best] / sum(w.values()), 3)]
''', 'Compute every cosine, then a SoftMax of scale × cosine. Subtract the largest value before exp to avoid overflow.',
         '<p>The second test is a tie: with equal similarity the SoftMax splits 0.5 and 0.5, and max picks the first label.</p>')
K.assign('cliploss', 'h', 'The CLIP loss',
         '<p>Write <code>clip_loss(S, tau)</code> for a square similarity matrix S where S[i][j] compares image i with caption j and the diagonal holds the true pairs. Return the symmetric loss ½(mean row CE + mean column CE) of SoftMax(S ÷ τ), rounded to 3 decimals.</p>',
         '''
from math import exp, log

def clip_loss(S, tau):
    # your code here
    pass
''', [('clip_loss([[0.9, 0.2, 0.1], [0.2, 0.9, 0.1], [0.1, 0.2, 0.9]], 1)', 0.666),
      ('clip_loss([[1, 0], [0, 1]], 1)', 0.313),
      ('clip_loss([[0, 1], [1, 0]], 1)', 1.313)],
         '''
from math import exp, log

def clip_loss(S, tau):
    n = len(S)
    def ce(row, k):
        m = max(row)
        z = sum(exp((v - m) / tau) for v in row)
        return -((row[k] - m) / tau - log(z))
    rows = sum(ce(S[i], i) for i in range(n)) / n
    cols = sum(ce([S[r][j] for r in range(n)], j) for j in range(n)) / n
    return round((rows + cols) / 2, 3)
''', 'Write a helper for −ln SoftMax(row)[k]. Apply it to every row with k = i and every column with k = j.',
         '<p>The last test swaps the captions, so the true pairs score lower than the wrong ones and the loss rises from 0.313 to 1.313.</p>')

K.must('CLIP', 'Image and text encoders into one space. Cosine similarity. Symmetric contrastive loss over an N × N matrix with temperature τ. 400 million pairs, batch 32,768.')
K.must('Zero-shot', 'One prompt per class, pick the highest similarity, SoftMax of 100 × cosine for probabilities. Prompt wording matters and ensembling helps. CLIP gives scores, SAM gives masks.')
K.must('Transformers', 'Patch = token, (n ÷ p)² tokens, N² attention pairs: 196 → 38,416, 1,024 → 1,048,576. Windows cut the cost (64× in the Swin example). SegFormer, Mask2Former queries with Hungarian matching.')
K.must('SAM and language', 'SAM: ViT encoder, prompt encoder, light decoder, SA-1B (11 M images, 1.1 B masks), class agnostic. Language-guided segmentation returns a mask for a phrase. Referring segmentation answers with a mask, VQA with text.')
K.must('Generation, restoration, 3D', 'DALL-E makes images from text, CLIP matches them. Restoration and super-resolution infer plausible detail, so validate clinically. Stereo Z = fB ÷ d, error ≈ Z² Δd ÷ (fB).')

T = K.topic(
    slug='vision-language', topic='vision-language', step=(7, 'Vision meets language and 3D', 'cv-vlm', 'How modern models connect pictures with words, segment anything on request, generate and restore images, and recover depth from several views.', 'Masters and research'),
    title='Connecting vision and language', short='CLIP, SAM and beyond', badge='7.1', minutes=60,
    lead='See how CLIP learns one space for pictures and words, how text prompts become classifiers, how transformers and SAM changed segmentation, how DALL-E and restoration models generate pixels, and how two cameras recover depth.',
    desc='Low and high level vision, CLIP and contrastive learning, zero-shot classification and prompt design, vision transformers for dense prediction, SegFormer and mask classification, SAM and language-guided segmentation, DALL-E and generative families, restoration, super-resolution, 3D reconstruction and stereo triangulation.',
    summary='CLIP, contrastive learning and zero-shot prompts, transformers for segmentation, SAM, DALL-E, restoration and stereo triangulation.',
    keywords=['CLIP', 'contrastive learning', 'zero-shot', 'prompt', 'vision transformer', 'SegFormer', 'Mask2Former', 'SAM', 'open vocabulary', 'DALL-E', 'diffusion', 'restoration', 'super-resolution', 'triangulation', 'stereo'],
    recap='<p>CLIP aligns images and text by pulling matching pairs together in one space, so a list of text prompts becomes a classifier. Transformers give every patch global context at a cost that grows with the square of the tokens. SAM segments whatever a prompt points at, and language-guided models segment what a phrase describes. Generators and restorers create pixels and must be validated, and two calibrated views give depth by triangulation.</p>')
