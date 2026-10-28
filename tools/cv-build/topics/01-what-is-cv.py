# Chapter 1: what computer vision is, the recognition tasks, why vision is hard, the cost of images and video,
# and where computer vision sits inside AI. Source: lecture 1 of the course notes.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

# ---------------------------------------------------------------- Python examples
K.code('grid', r'''
# A tiny grey picture: 4 rows and 6 columns, values from 0 (black) to 255 (white)
img = [
    [ 20,  20, 200, 200,  20,  20],
    [ 20, 200, 255, 255, 200,  20],
    [ 20, 200, 255, 255, 200,  20],
    [ 20,  20, 200, 200,  20,  20],
]
h = len(img)          # number of rows
w = len(img[0])       # number of columns
print("shape:", h, "x", w, "=", h * w, "pixels")
print("top left pixel:", img[0][0])
print("centre pixel:", img[1][2])

# crop rows 1 to 2 and columns 1 to 4 (the end index is not included)
crop = [row[1:5] for row in img[1:3]]
print("crop:", crop)

# mirror the picture left to right
mirror = [row[::-1] for row in img]
print("first row mirrored:", mirror[0])

# brighten by an amount the user types, keeping every value inside 0 to 255
add = int(input("Brighten by how much? "))
bright = [[min(255, max(0, v + add)) for v in row] for row in img]
print("first row brightened:", bright[0])
''', stdin='40\n')

K.code('video_cost', r'''
# How much raw data does a camera produce before any compression?
h = int(input("Height in pixels: "))
w = int(input("Width in pixels: "))
fps = int(input("Frames per second: "))
channels = 3                      # red, green and blue
bits = 8                          # one byte per number

per_frame = h * w * channels * bits // 8          # bytes in one frame
per_second = per_frame * fps
print("one frame:", per_frame, "bytes =", per_frame / 1e6, "MB")
print("one second:", per_second / 1e6, "MB")
print("one hour:", round(per_second * 3600 / 1e9, 1), "GB")
''', stdin='1080\n1920\n30\n')

# ---------------------------------------------------------------- lessons
K.lesson('what', 'What computer vision is', f'''
<p>Computer vision is the part of computer science that teaches machines to understand pictures and videos. A camera gives the computer only a grid of numbers. Computer vision is everything that happens between those numbers and an answer such as "a child is crossing the road in front of the car".</p>
<p>The course notes use a careful definition: <b>computer vision uses algorithms and representations to compute properties of the physical world from visual data.</b> Notice the words "physical world". The goal is not the picture itself. The goal is the real scene that the picture came from.</p>
<h3>Three jobs computer vision does</h3>
{table(['Job', 'The question it answers', 'Everyday example'], [
    ['Measurement', 'How big, how far, what shape, how fast?', 'A phone measuring a room, a car estimating the distance to the car in front'],
    ['Perception and interpretation', 'What is in the scene and what is happening?', 'Face unlock, a doctor\'s tool marking a tumour, a robot finding a cup'],
    ['Search, organisation and interaction', 'Which pictures match, and what do they mean?', 'Searching your gallery for "beach", reverse image search, answering a question about a photo']])}
<h3>You see meaning, the computer sees numbers</h3>
<p>When you look at a chair your brain does a lot of work without telling you. The eyes record light and dark. The brain finds edges, joins edges into a shape, guesses depth and the direction of each surface, decides it is a chair and even knows you can sit on it. A computer has to build every one of those steps itself. The animation below shows what it starts with.</p>
{viz('pixels')}
{ladder(
    '<p>A photo on a computer is like a giant sheet of graph paper. Every little square holds a number that says how bright it is. Computer vision is teaching the computer to look at all those numbers and say "that is a cat".</p>',
    '<p>A grey image is a matrix <i>I</i> with <i>H</i> rows and <i>W</i> columns. Each entry <i>I</i>(<i>r</i>, <i>c</i>) is a whole number from 0 to 255. A colour image stacks three such matrices, one each for red, green and blue, giving an array of shape <i>H</i> × <i>W</i> × 3. Vision algorithms are functions that map this array to useful outputs such as a label, a box or a depth map.</p>',
    '<p>A camera performs a projection from the 3D world to a 2D image plane, so depth is lost and many different scenes can produce the same image. Vision is therefore an inverse problem: from the image <i>I</i> we want the scene <i>S</i> with <i>I</i> = <i>f</i>(<i>S</i>), where <i>f</i> includes geometry, lighting, the lens and the sensor. The inverse is not unique, so every method adds assumptions, either hand written (smooth surfaces, rigid objects) or learned from data.</p>',
    '<p>Modern research frames vision as learning representations: functions that map pixels to vectors in which the things we care about (identity, pose, depth, relations) are easy to read out and the nuisances (lighting, viewpoint, background) are suppressed. Open questions include robustness under distribution shift, learning from few labels, linking vision with language, and understanding 3D structure and physics from video.</p>')}
{note('A picture is only a measurement of the world. The same object can produce very different numbers, and different objects can produce similar numbers. Every hard part of vision comes from this.')}
''', kw=['computer vision definition', 'measurement', 'perception', 'search', 'pixels', 'human vision'])

K.lesson('tasks', 'What recognition involves', f'''
<p>"Recognise the picture" sounds like one task. In practice it is a family of tasks, and each one gives a different kind of answer. Knowing which task you are solving is the first step of any vision project.</p>
{table(['Task', 'Question', 'Output'], [
    ['Image classification', 'What is this picture mainly of?', 'One label, for example "dog"'],
    ['Object detection', 'What objects are present, and where?', 'Boxes with a label and a confidence each'],
    ['Categorisation', 'Which general class is this object?', 'Person, vehicle, chair'],
    ['Instance recognition', 'Which exact object is this?', '"This is the Eiffel Tower", "this is your car"'],
    ['Scene recognition', 'What kind of place is this?', 'Kitchen, highway, market, forest'],
    ['Attribute recognition', 'What is it like?', 'Red, metal, wet, broken, open'],
    ['Activity recognition', 'What is happening over time?', 'Walking, falling, crossing the road'],
    ['Relationship recognition', 'How do the objects relate?', '"A person is holding a bag", "a car is approaching a cyclist"'],
    ['Segmentation', 'Which pixels belong to which thing?', 'A label for every pixel']])}
<p>Detection is really two jobs at once: <b>classification</b> (what it is) and <b>localisation</b> (where it is). Category recognition says "this is a building". Instance recognition says "this is the Eiffel Tower". Relationship recognition is a big step beyond detection, because two correctly found boxes say nothing about whether the person is holding the bag or just standing near it.</p>
<h3>Context changes the answer</h3>
<p>The same small rectangle can be a book in a classroom, a traffic sign by a road and a tray in a kitchen. Recognition uses the surroundings, not just the pixels inside the object. This is why scene recognition often helps object recognition.</p>
{scene('a self driving car at a junction', '<p>A car approaching a junction needs almost every task in the table. Detection finds the pedestrian, the cyclist and the traffic light. Attribute recognition reads the light as red. Activity recognition notices the pedestrian has started walking. Relationship recognition notices the cyclist is moving into the car\'s lane. Measurement estimates that the pedestrian is 14 metres away. A mistake in any one of them can lead to a wrong decision, which is why the notes stress that recognition errors become action errors for autonomous agents.</p>')}
{note('Examiners like the pair detection versus recognition. Detection finds and localises objects. Recognition decides what they are and what they mean. Categorisation gives a class, instance recognition names one particular object.', 'exam')}
''', kw=['object detection', 'classification', 'instance recognition', 'scene recognition', 'attribute', 'activity recognition', 'relationship', 'context'])

K.lesson('hard', 'Why vision is hard', f'''
<p>People find vision easy, so it is surprising how hard it is for machines. The reason is that the numbers in an image change a lot when the world changes only a little. The notes list the main troublemakers.</p>
{table(['Challenge', 'What happens', 'Example'], [
    ['Illumination', 'The same object gives different numbers under different light', 'Night, glare, shadows, a face lit from one side'],
    ['Viewpoint and pose', 'The shape on the image changes with the camera angle', 'A car from the front and from the side'],
    ['Scale', 'Objects far away are only a few pixels', 'A pedestrian 100 metres away'],
    ['Occlusion', 'Part of the object is hidden', 'A child standing behind an adult'],
    ['Clutter', 'A busy background hides boundaries', 'A crowded market, a supermarket shelf'],
    ['Intra class variation', 'Members of one class look different', 'Office chair, stool, wheelchair'],
    ['Inter class similarity', 'Different classes look alike', 'Wolf and husky, bus and truck'],
    ['Limited field of view', 'Important things are outside the frame', 'A car coming from behind the camera'],
    ['Weather', 'Contrast and visibility change', 'Rain, fog, dust, snow'],
    ['Irregular environments', 'The world is messier than the dataset', 'Potholes, missing lane markings']])}
<p>The animation shows why the simplest idea, "store a picture of the object and compare pixels", breaks so quickly. Some changes can be undone with maths. Others cannot.</p>
{viz('nuisance')}
{fx('Normalised cross correlation (NCC)', f'NCC = {frac("Σ (<i>T</i> − <i>T̄</i>)(<i>I</i> − <i>Ī</i>)", "√( Σ (<i>T</i> − <i>T̄</i>)² · Σ (<i>I</i> − <i>Ī</i>)² )")}', '<i>T</i> is the template, <i>I</i> is the image patch, and a bar means the average. The score runs from −1 to 1. If <i>I</i> = <i>a</i>·<i>T</i> + <i>b</i> with <i>a</i> &gt; 0, the score is exactly 1, so brightness and contrast changes do not matter.')}
<h3>Robustness, generalisation and imbalance</h3>
<p>Three words from the notes that are easy to mix up:</p>
<ul>
<li><b>Robustness</b> is staying correct under the variations you expect, such as different lighting or a slightly different pose.</li>
<li><b>Generalisation</b> is staying correct on new data that differs from the training data, for example a model trained on clean city roads used on rural roads with potholes. The training data and the deployment data come from different distributions. This is called distribution shift.</li>
<li><b>Data imbalance</b> is when some conditions or classes are rare in the training data, for example many summer images and very few snowy ones. It is a common cause of poor generalisation for the rare cases.</li>
</ul>
{ladder(
    '<p>If you only ever practised football on a sunny day, you might play badly in the rain. Computers are the same. They do well on what they practised and can fail on things they rarely saw.</p>',
    '<p>A classifier learns from training examples. If test images look like training images it does well. Changes in lighting, angle or background move the test images away from what it learned, and accuracy falls. More varied training data and augmentation (random changes during training) are the usual fixes.</p>',
    '<p>Formally the model is trained to minimise expected loss under the training distribution <i>P</i><sub>train</sub>(<i>x</i>, <i>y</i>), but it is judged under <i>P</i><sub>test</sub>. Covariate shift changes <i>P</i>(<i>x</i>) and keeps <i>P</i>(<i>y</i> | <i>x</i>). Label shift changes <i>P</i>(<i>y</i>). Imbalance means some regions of <i>x</i> have few samples, so the empirical risk there has high variance. Reweighting, targeted data collection and domain adaptation each address a different part of this.</p>',
    '<p>Research on robustness studies invariance and equivariance built into architectures, test time adaptation, benchmarks with natural shifts (weather, geography, sensors), and the link between robustness and shortcut learning, where a model uses a background cue that happens to correlate with the label.</p>')}
{note('A high score on the test set does not prove the model will work after deployment. If the deployment conditions are missing from the data, the test set cannot measure them.', 'warn')}
''', kw=['illumination', 'viewpoint', 'occlusion', 'clutter', 'intra class variation', 'inter class similarity', 'robustness', 'generalisation', 'distribution shift', 'data imbalance', 'normalised cross correlation'])

K.lesson('cost', 'Images, video and their cost', f'''
<p>Every pixel is a number the computer has to store and process. Pictures get big very fast, and video multiplies the size by the number of frames.</p>
{fxs(
    fx('Numbers in an image', '<i>N</i> = <i>H</i> × <i>W</i> × <i>C</i>', '<i>H</i> rows, <i>W</i> columns, <i>C</i> channels (1 for grey, 3 for colour).', key=True),
    fx('Bytes in an image', 'bytes = ' + frac('<i>H</i> × <i>W</i> × <i>C</i> × <i>b</i>', '8'), '<i>b</i> is the bits per number. With 8 bits each number is one byte.'),
    fx('Levels per number', 'levels = 2<sup><i>b</i></sup>', '8 bits give 256 levels, from 0 to 255.'),
    fx('Raw video data rate', 'rate = <i>H</i> × <i>W</i> × <i>C</i> × ' + frac('<i>b</i>', '8') + ' × fps', 'Bytes per second before compression. fps is frames per second.', key=True))}
{steps('Worked example: why the lecture compared 32 × 32 with 2048 × 2048', [
    'A 32 × 32 image has 32 × 32 = 1,024 pixels.',
    'A 2048 × 2048 image has 2048 × 2048 = 4,194,304 pixels.',
    'The ratio is 4,194,304 ÷ 1,024 = 4,096. The large image has 4,096 times as many pixels.',
    'Any step that touches every pixel once, such as a 3 × 3 filter, now does 4,096 times the work. This is why resolution is a cost, not just a quality setting.'])}
{steps('Worked example: one second of Full HD video', [
    'Full HD is 1920 × 1080 with 3 channels and 8 bits per number.',
    'One frame is 1920 × 1080 × 3 = 6,220,800 bytes, about 6.2 MB.',
    'At 30 frames per second that is 6,220,800 × 30 = 186,624,000 bytes, about 187 MB every second.',
    'This is why video is almost always compressed, and why a vision system must decide which frames to process.'])}
{code('video_cost')}
<h3>Three costs every vision system pays</h3>
{table(['Cost', 'Question to ask', 'Why it matters'], [
    ['Time', 'Can each frame be processed before the next one arrives?', 'A car at 72 km/h moves 2 metres in 100 ms'],
    ['Memory', 'Can the frames and the model fit on the device?', 'Phones, drones and cameras have little memory'],
    ['Energy', 'How much battery or power does it use?', 'Edge devices run on small batteries']])}
<p>The notes stress the trade off between accuracy, speed, memory and energy. A very accurate model can be too slow for real time use, and a very fast model can miss things. Video adds a fourth difficulty: the system must keep track of the same object across frames, decide whether movement is real or caused by the camera moving, and keep its answers consistent over time.</p>
<h3>Limited supervision</h3>
<p>Supervised learning needs labelled examples, and labels are expensive. In some areas the data is rare by nature: rare diseases, rare natural disasters, unusual factory faults. Medical data is also private and needs experts to label it. The usual tools are transfer learning, self supervised learning, few shot learning, semi supervised learning, careful augmentation and domain adaptation. None of them removes the need for good, representative data.</p>
''', kw=['pixel count', 'image size', 'bytes', 'bit depth', 'video data rate', 'frames per second', 'time memory energy', 'limited supervision', 'medical data'])

K.lesson('ai', 'Where computer vision sits in AI', f'''
<p>Computer vision uses ideas from all of artificial intelligence. The notes give a simple nesting: artificial intelligence contains machine learning, machine learning contains deep learning, and deep learning includes convolutional networks (CNNs), recurrent networks (RNNs), transformers and other designs.</p>
{table(['Era', 'How features were made', 'Example'], [
    ['Classical vision', 'People design the features by hand, then a simple classifier decides', 'SIFT or HOG features with a support vector machine'],
    ['Deep learning', 'The network learns the features from labelled data', 'CNNs such as AlexNet and ResNet'],
    ['Foundation models', 'Very large models learn from huge, loosely labelled data, often with text', 'CLIP, SAM, vision transformers']])}
<h3>What a CNN learns, layer by layer</h3>
<p>CNNs tend to learn a hierarchy. Early layers respond to edges and simple light and dark patterns. Middle layers respond to textures, corners and parts. Deeper layers respond to whole objects and concepts. This mirrors the staged view of vision in the next chapter, where edges come first and meaning comes last.</p>
<h3>The brain and AI</h3>
<p>The notes put it this way: the brain inspires AI, and AI helps us understand the brain. Studies of the visual cortex found neurons that respond to edges at particular orientations, which inspired layered feature detectors. Today, neural networks are used as models to compare with brain recordings. The notes also warn against taking the analogy literally. An artificial neuron is not a biological neuron, and supervised learning is not how children learn.</p>
{ladder(
    '<p>Old computer vision was like giving a robot a checklist: "a face has two eyes and a mouth". New computer vision is like showing a robot thousands of faces and letting it work out the checklist itself.</p>',
    '<p>In a classical pipeline you compute a feature vector by hand (for example a histogram of edge directions) and train a classifier on it. In deep learning, the feature extractor is a stack of learned layers trained end to end with the classifier, using gradient descent on a loss function.</p>',
    '<p>Learned features win when labelled data and compute are plentiful, because the network can discover features no person would design. Classical features still win when data is scarce, compute is tight, or you need to explain each decision. Many real systems mix both, for example classical keypoints for camera tracking and a CNN for recognition.</p>',
    '<p>Representation learning asks what makes a good feature space. Self supervised methods learn from unlabelled images by predicting missing parts or matching two views of the same image. Multimodal models align images with text so that a single space supports classification, retrieval and question answering without task specific labels.</p>')}
{note('Do not say that classical features such as HOG are needed "because CNNs overfit". The notes correct this. Overfitting depends on data size, model size, regularisation and augmentation. Classical features are useful because they are efficient, simple and easy to interpret.', 'warn')}
''', kw=['AI hierarchy', 'machine learning', 'deep learning', 'CNN', 'transformer', 'feature hierarchy', 'brain and AI', 'classical vision', 'foundation models'])

K.lesson('python', 'Images in Python', f'''
<p>You do not need a special library to understand images. A grey image is a list of rows, and each row is a list of numbers. The example below builds a tiny picture, reads pixels, crops, mirrors and brightens it. Press Run line by line to watch every variable change, or Edit and run to try your own values. It asks how much to brighten by, so you can type your own number.</p>
{code('grid')}
<h3>The same ideas with NumPy and OpenCV</h3>
<p>Real projects use NumPy arrays, which do the same thing much faster. These lines are for reading, they are not run on this page.</p>
<pre class="cc-src"><span class="ln">import cv2                       # OpenCV</span><span class="ln">img = cv2.imread("street.jpg")   # shape (H, W, 3), values 0 to 255</span><span class="ln">print(img.shape, img.dtype)      # for example (1080, 1920, 3) uint8</span><span class="ln">crop = img[100:300, 200:500]     # rows 100 to 299, columns 200 to 499</span><span class="ln">mirror = img[:, ::-1]            # flip left to right</span><span class="ln">gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)</span></pre>
{note('OpenCV loads colour images in BGR order, not RGB. Most other libraries (Matplotlib, PIL, PyTorch models) expect RGB. Forgetting to convert is one of the most common bugs in vision code.', 'warn')}
<p>Two indexing rules to keep straight: an image is indexed <b>row first, then column</b>, so <code>img[r][c]</code> means row <i>r</i> (the <i>y</i> position) and column <i>c</i> (the <i>x</i> position). And slices do not include their end, so <code>img[1:3]</code> gives rows 1 and 2.</p>
''', kw=['python image', 'nested list', 'numpy', 'opencv', 'imread', 'BGR', 'crop', 'flip', 'shape'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which definition matches the course notes?', [
    'Computer vision makes pictures look nicer',
    'Computer vision uses algorithms and representations to compute properties of the physical world from visual data',
    'Computer vision is the study of cameras and lenses',
    'Computer vision is another name for image compression'], 1,
    'The notes stress "the physical world".',
    'The aim is to learn about the real scene, such as sizes, distances, objects and events, from images and video. Making pictures look nicer is image processing, which is only one tool.')
K.quiz('e', 'A system says "this photo shows the Taj Mahal". Which task is this?', [
    'Categorisation', 'Instance recognition', 'Scene recognition', 'Attribute recognition'], 1,
    'Is it naming a general class or one particular object?',
    'Naming one specific building is instance recognition. Saying "a building" would be categorisation.')
K.quiz('e', 'Object detection answers which two questions?', [
    'What and where', 'What and when', 'How many pixels and how many colours', 'Which camera and which lens'], 0,
    'Detection combines classification with localisation.',
    'Detection outputs a class label (what) and a box (where) for each object.')
K.quiz('e', 'How many numbers does a 100 × 200 colour image hold?', ['20,000', '40,000', '60,000', '300'], 2,
    'Multiply rows, columns and channels.',
    '100 × 200 × 3 = 60,000. Each pixel has red, green and blue values.')
K.quiz('m', 'A model trained only on sunny city roads fails on a rainy village road. Which idea best names the problem?', [
    'Overfitting to the test set', 'Distribution shift and poor generalisation', 'Too many colour channels', 'Instance recognition'], 1,
    'The deployment data comes from a different distribution than the training data.',
    'The model meets conditions it never saw. That is distribution shift, and the failure is a failure to generalise. Rain and missing lane markings are not in its training distribution.')
K.quiz('m', 'Why does normalised cross correlation ignore a change in brightness?', [
    'It only looks at the brightest pixel',
    'It subtracts the mean and divides by the spread, so adding a constant or scaling all pixels does not change the score',
    'It converts the image to colour first',
    'It ignores half of the pixels'], 1,
    'Look at the bars in the formula.',
    'Subtracting the mean removes any constant added to every pixel. Dividing by the spread removes any positive scale factor. Rotation, scale changes and occlusion are not removed this way.')
K.quiz('m', 'A child is partly hidden behind an adult. Which challenge is this?', ['Clutter', 'Occlusion', 'Inter class similarity', 'Illumination'], 1,
    'Something is in front of the object.',
    'Occlusion means part of the object is hidden by something closer to the camera. The system must use the visible parts, context and shape to infer the rest.')
K.quiz('m', 'Office chairs, wheelchairs and stools all belong to "chair" but look very different. What is this called?', [
    'Inter class similarity', 'Intra class variation', 'Data imbalance', 'Limited field of view'], 1,
    'Intra means within one class.',
    'Variation within one class is intra class variation. Inter class similarity is the opposite problem: different classes that look alike, such as wolves and huskies.')
K.quiz('h', 'Your dataset has 9,000 summer images and 100 snowy images. Overall accuracy is 95%. What is the most likely hidden problem?', [
    'The model is perfect',
    'Accuracy on snowy images may be much lower, because they are only about 1% of the data and barely affect the average',
    'The images have too many pixels',
    'The model must be using colour'], 1,
    'Ask how much the rare group can move the overall number.',
    'With imbalance, the overall score is dominated by the common case. Always report accuracy per condition. Collecting more snowy images or weighting them more in training are the usual fixes.')
K.quiz('h', 'Why is video so much more expensive than a single image?', [
    'Videos use a different colour system',
    'Each second holds many frames, and understanding them needs links across time such as tracking and motion',
    'Videos cannot be stored as numbers',
    'Only because video files have sound'], 1,
    'Think about both data size and the extra tasks.',
    'Raw data grows with the frame rate, for example 30 frames each second. The system must also keep objects consistent across frames, separate camera motion from object motion and recognise activities, which a single image never needs.')
K.quiz('x', 'Which statement about classical features and deep learning matches the notes?', [
    'HOG is needed because CNNs always overfit',
    'Classical features are useful for efficiency, simplicity, interpretability and when domain knowledge is clear, and can complement deep models',
    'Classical features are always more accurate than CNNs',
    'Deep learning cannot use edges'], 1,
    'The notes include a correction about overfitting.',
    'Overfitting depends on data, model size and training. The real reasons to use classical features are low cost, low data needs, interpretability and known structure, and they can sit inside a larger deep pipeline.')
K.quiz('x', 'A camera sees I = 2T + 5 everywhere, where T is the stored template. What is the normalised cross correlation?', ['0', '0.5', '1', '2'], 2,
    'A positive scale and an added constant are both removed.',
    'Subtracting the means removes the 5. The factor 2 appears on the top and on the bottom of the formula and cancels. The score is exactly 1.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many pixels are in a 32 × 32 image?', '1024', 'Multiply the two sides.',
       ['Pixels = rows × columns.', eq('32 × 32 = 1,024'), 'So a 32 × 32 thumbnail has 1,024 pixels.'], check=32 * 32)
K.calc('e', 'How many pixels are in a 2048 × 2048 image?', '4194304', 'Multiply 2048 by 2048.',
       ['Pixels = rows × columns.', eq('2048 × 2048 = 4,194,304'), 'That is about 4.2 million pixels, as in the lecture.'], check=2048 * 2048)
K.calc('e', 'How many grey levels can an 8 bit pixel take?', '256', 'Levels = 2 to the power of the bits.',
       ['Each extra bit doubles the number of values.', eq('2<sup>8</sup> = 256'), 'The values run from 0 to 255.'], check=2 ** 8)
K.calc('e', 'How many numbers are stored for a 640 × 480 colour image?', '921600', 'N = H × W × C with C = 3.',
       ['Pixels: 640 × 480 = 307,200.', 'Each pixel has 3 numbers (red, green, blue).', eq('307,200 × 3 = 921,600')], check=640 * 480 * 3)
K.calc('m', 'How many times more pixels does a 2048 × 2048 image have than a 32 × 32 image?', '4096', 'Divide the two pixel counts, or square the ratio of the sides.',
       ['Ratio of sides: 2048 ÷ 32 = 64.', 'Pixels grow with the square of the side.', eq('64² = 4,096')], check=(2048 * 2048) // (32 * 32))
K.calc('m', 'A 1920 × 1080 colour frame uses 8 bits per number. How many megabytes is it? (1 MB = 1,000,000 bytes)', '6.2208', 'bytes = H × W × C × 8 ÷ 8.',
       ['Numbers: 1920 × 1080 × 3 = 6,220,800.', 'Each number is one byte, so 6,220,800 bytes.', eq('6,220,800 ÷ 1,000,000 = 6.2208 MB')], check=1920 * 1080 * 3 / 1e6, unit='MB')
K.calc('m', 'Raw Full HD video (1920 × 1080, colour, 8 bit) runs at 30 frames per second. How many megabytes per second is that?', '186.624', 'Multiply one frame by 30.',
       ['One frame is 6,220,800 bytes.', 'Per second: 6,220,800 × 30 = 186,624,000 bytes.', eq('186,624,000 ÷ 1,000,000 = 186.624 MB/s')], check=1920 * 1080 * 3 * 30 / 1e6, unit='MB/s')
K.calc('m', 'How many gigabytes is one minute of raw 1280 × 720 colour video at 25 frames per second? (1 GB = 10<sup>9</sup> bytes)', '4.1472', 'Bytes per frame × frames per second × 60 seconds.',
       ['One frame: 1280 × 720 × 3 = 2,764,800 bytes.', 'One second: 2,764,800 × 25 = 69,120,000 bytes.', 'One minute: 69,120,000 × 60 = 4,147,200,000 bytes.', eq('4,147,200,000 ÷ 10<sup>9</sup> = 4.1472 GB')], check=1280 * 720 * 3 * 25 * 60 / 1e9, unit='GB')
K.calc('h', 'A model is 95% accurate on 9,000 summer images, 60% on 900 rainy images and 30% on 100 snowy images. What is its overall accuracy as a decimal?', '0.912', 'Weight each accuracy by how many images it covers.',
       ['Correct summer: 9,000 × 0.95 = 8,550.', 'Correct rainy: 900 × 0.60 = 540. Correct snowy: 100 × 0.30 = 30.', 'Total correct: 8,550 + 540 + 30 = 9,120 out of 10,000.', eq('9,120 ÷ 10,000 = 0.912'), 'The overall 91.2% hides the 30% on snow. This is the danger of imbalance.'], check=(9000 * .95 + 900 * .6 + 100 * .3) / 10000)
K.calc('h', 'A car drives at 72 km/h and its vision system takes 100 ms per frame. How many metres does the car travel while one frame is processed?', '2', 'Turn km/h into metres per second first.',
       ['72 km/h = 72,000 m ÷ 3,600 s = 20 m/s.', '100 ms = 0.1 s.', eq('20 × 0.1 = 2 m'), 'Every frame of delay costs 2 metres of braking distance.'], check=72000 / 3600 * 0.1, unit='m')
K.calc('x', 'A 4K camera (3840 × 2160, colour, 8 bit) runs at 60 frames per second. Its raw data rate is how many times a 1 Gbit/s link? Give two decimals.', '11.94', 'Work in bits per second.',
       ['Numbers per frame: 3840 × 2160 × 3 = 24,883,200.', 'Bits per frame: 24,883,200 × 8 = 199,065,600.', 'Bits per second: 199,065,600 × 60 = 11,943,936,000.', eq('11,943,936,000 ÷ 10<sup>9</sup> ≈ 11.94'), 'The raw stream needs almost 12 such links, so the camera must compress or process on the device.'], check=11.943936, tol=0.006)
K.calc('x', 'A template is T = [10, 20, 30, 40] and the camera sees I = [25, 45, 65, 85]. What is the mean absolute difference between them? (The NCC is 1 because I = 2T + 5.)', '30', 'Subtract position by position, take absolute values, then average.',
       ['Differences: 25 − 10 = 15, 45 − 20 = 25, 65 − 30 = 35, 85 − 40 = 45.', 'Sum: 15 + 25 + 35 + 45 = 120.', eq('120 ÷ 4 = 30'), 'A raw difference of 30 looks like a bad match, yet NCC says it is a perfect match after removing lighting and contrast.'], check=30)

# ---------------------------------------------------------------- assignments
K.assign('pixels', 'e', 'Count the numbers in an image',
         '<p>Write <code>pixel_numbers(h, w, c)</code> that returns how many numbers an image of height <code>h</code>, width <code>w</code> and <code>c</code> channels holds. Then write <code>image_bytes(h, w, c, bits)</code> that returns the size in bytes when each number uses <code>bits</code> bits. Return a whole number when the size is whole.</p>',
         '''
def pixel_numbers(h, w, c):
    # your code here
    pass


def image_bytes(h, w, c, bits):
    # your code here
    pass
''', [('pixel_numbers(32, 32, 1)', 1024), ('pixel_numbers(480, 640, 3)', 921600), ('image_bytes(1080, 1920, 3, 8)', 6220800), ('image_bytes(100, 100, 1, 1)', 1250)],
         '''
def pixel_numbers(h, w, c):
    return h * w * c


def image_bytes(h, w, c, bits):
    total_bits = pixel_numbers(h, w, c) * bits
    return total_bits // 8 if total_bits % 8 == 0 else total_bits / 8
''', 'Multiply height, width and channels. For bytes multiply by the bits and divide by 8.',
         '<p>N = H × W × C, and bytes = N × bits ÷ 8. The 1 bit case shows why bit depth matters: 10,000 pixels need only 1,250 bytes.</p>')
K.assign('crop', 'm', 'Crop a region of interest',
         '<p>Write <code>crop(img, top, left, height, width)</code>. <code>img</code> is a list of rows. Return a new list of rows that starts at row <code>top</code> and column <code>left</code> and is <code>height</code> rows tall and <code>width</code> columns wide. If the box runs past the edge, keep only the part inside the image.</p>',
         '''
def crop(img, top, left, height, width):
    # your code here
    pass
''', [('crop([[1,2,3],[4,5,6],[7,8,9]], 0, 0, 2, 2)', [[1, 2], [4, 5]]), ('crop([[1,2,3],[4,5,6],[7,8,9]], 1, 1, 2, 2)', [[5, 6], [8, 9]]),
      ('crop([[1,2,3],[4,5,6],[7,8,9]], 2, 1, 5, 5)', [[8, 9]]), ('crop([[1,2,3,4]], 0, 1, 1, 2)', [[2, 3]])],
         '''
def crop(img, top, left, height, width):
    return [row[left:left + width] for row in img[top:top + height]]
''', 'Slice the rows first with img[top:top + height], then slice each row.',
         '<p>Python slices stop at the end of a list without an error, so a box that runs past the edge is clipped for free. The same slice in NumPy is <code>img[top:top + height, left:left + width]</code>.</p>')
K.assign('video', 'm', 'Plan the storage for a camera',
         '<p>Write <code>video_gb(h, w, fps, seconds)</code> that returns the size of raw colour video (3 channels, 8 bits per number) in gigabytes, where 1 GB is 10<sup>9</sup> bytes. Round to 3 decimal places.</p>',
         '''
def video_gb(h, w, fps, seconds):
    # your code here
    pass
''', [('video_gb(720, 1280, 25, 60)', 4.147), ('video_gb(1080, 1920, 30, 1)', 0.187), ('video_gb(2160, 3840, 60, 10)', 14.93)],
         '''
def video_gb(h, w, fps, seconds):
    total = h * w * 3 * fps * seconds
    return round(total / 1e9, 3)
''', 'Bytes per frame are h × w × 3. Multiply by the frames per second and the seconds.',
         '<p>Ten seconds of raw 4K at 60 frames per second is about 15 GB. Video codecs bring this down by a factor of 100 or more, which you will meet in the chapter on pixels and compression.</p>')
K.assign('ncc', 'h', 'Write a template matcher',
         '<p>Write <code>ncc(a, b)</code> for two lists of the same length. Return the normalised cross correlation rounded to 4 decimal places. If either list is constant, return <code>0.0</code>, because the spread is zero.</p>',
         '''
from math import sqrt


def ncc(a, b):
    # your code here
    pass
''', [('ncc([1, 2, 3], [2, 4, 6])', 1.0), ('ncc([1, 2, 3], [3, 2, 1])', -1.0), ('ncc([10, 20, 30, 40], [12, 18, 33, 41])', 0.987), ('ncc([5, 5, 5], [1, 2, 3])', 0.0)],
         '''
from math import sqrt


def ncc(a, b):
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    top = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    bottom = sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    if bottom == 0:
        return 0.0
    return round(top / bottom, 4)
''', 'Find both means, then the top sum and the two spreads. Check for a zero spread before dividing.',
         '<p>NCC is the Pearson correlation of the pixel values. It is the classic way to compare a template with an image patch, and OpenCV offers it as <code>cv2.matchTemplate</code> with <code>TM_CCOEFF_NORMED</code>.</p>')

# ---------------------------------------------------------------- summary
K.must('The definition', 'Computer vision computes properties of the physical world from images and video. Its three jobs are measurement, perception and search.')
K.must('The task family', 'Classification, detection (what and where), categorisation, instance recognition, scene, attribute, activity and relationship recognition, and segmentation.')
K.must('Why it is hard', 'Illumination, viewpoint, scale, occlusion, clutter, intra class variation, inter class similarity, field of view, weather and messy environments.')
K.must('Robustness and generalisation', 'Robustness handles expected variation. Generalisation handles new or shifted data. Imbalance hides poor performance on rare cases.')
K.must('Size and cost', 'N = H × W × C, bytes = N × b ÷ 8, levels = 2 to the power b, raw video rate = frame bytes × fps. Systems trade accuracy against time, memory and energy.')
K.must('Classical and learned features', 'Classical features are designed by hand and are cheap and interpretable. Deep networks learn features in a hierarchy from edges to objects.')

T = K.topic(
    slug='what-is-computer-vision', topic='what-is-cv', step=(1, 'Seeing like a machine', 'cv-foundations', 'What vision is, why it is hard for machines, and the first hand made features.', 'Start here'),
    title='What computer vision is and why it is hard', short='What computer vision is', badge='1.1', minutes=35,
    lead='Computers receive only a grid of numbers. This chapter explains what computer vision tries to recover from those numbers, the tasks it solves, and why lighting, viewpoint and hidden objects make it so hard.',
    desc='Computer vision explained from school level: the definition, recognition tasks, why vision is hard, robustness, generalisation, image and video cost, and where vision sits in AI.',
    summary='The definition, the recognition tasks, why vision is hard, robustness and generalisation, the cost of images and video, and where computer vision sits in AI.',
    keywords=['computer vision', 'what is computer vision', 'recognition', 'detection', 'occlusion', 'illumination', 'robustness', 'generalisation', 'data imbalance', 'pixels', 'video cost'],
    recap='<p>Computer vision turns grids of numbers into facts about the world. The hard part is that the numbers change with light, angle, distance and clutter while the object stays the same. Keep the size formulas in mind, because every later method has to pay for each pixel it touches.</p>')
