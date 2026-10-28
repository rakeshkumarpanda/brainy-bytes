# Chapter 6: optical flow, HOF and MBH, the traditional action recognition pipeline and modern video tasks.
# Source: lectures 3 and 4, parts V to VIII.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('flow', r'''
# One flow vector: magnitude, direction, speed and its HOF bin
from math import atan2, degrees, sqrt

u = float(input("u, horizontal motion in pixels per frame (right is +): "))
v = float(input("v, vertical motion in pixels per frame (up is +): "))
fps = 30

magnitude = sqrt(u ** 2 + v ** 2)
angle = degrees(atan2(v, u)) % 360            # 0 = right, 90 = up
speed = magnitude * fps                        # pixels per second

names = ["right", "up-right", "up", "up-left", "left", "down-left", "down", "down-right"]
b = round(angle / 45) % 8                      # nearest of 8 directions
print("magnitude:", round(magnitude, 2), "pixels per frame")
print("direction:", round(angle, 2), "degrees")
print("speed:", round(speed, 1), "pixels per second at", fps, "fps")
print("HOF bin:", b, names[b])
''', stdin='3\n4\n')

K.code('hof', r'''
# A HOF histogram: 8 direction bins, each vote weighted by the flow magnitude
from math import atan2, sqrt, pi

flows = [(2, 0), (3, 0), (2.5, 0.5), (0, 4), (-1, 0), (0, 0)]
hist = [0.0] * 8
for u, v in flows:
    m = sqrt(u * u + v * v)
    if m == 0:
        continue                               # still pixels cast no vote
    b = round(atan2(v, u) / (pi / 4)) % 8
    hist[b] += m

print("bins:", ["->", "/^", "^", "^\\", "<-", "v/", "v", "\\v"])
print("HOF: ", [round(h, 2) for h in hist])
print("dominant bin:", hist.index(max(hist)))
''')

K.code('words', r'''
# Bag of visual words: map each descriptor to its nearest word, then count
words = [(0.2, 0.3), (0.3, 0.75), (0.75, 0.25), (0.8, 0.7)]    # k-means centres
clip = [(0.22, 0.28), (0.18, 0.35), (0.31, 0.7), (0.7, 0.3), (0.25, 0.33)]

def nearest(d):
    best, best_d = 0, float("inf")
    for j, w in enumerate(words):
        dist = (d[0] - w[0]) ** 2 + (d[1] - w[1]) ** 2
        if dist < best_d:
            best, best_d = j, dist
    return best

hist = [0] * len(words)
for d in clip:
    hist[nearest(d)] += 1
print("word counts:", hist)
print("normalised: ", [round(h / len(clip), 2) for h in hist])
''')

K.lesson('flow', 'Video and optical flow', f'''
<p>The lecture opens this part with one sentence: a video adds one more piece of information that a still image does not have, <b>time</b>. A video is a stack of frames, so it is 2D plus time, an image plus motion.</p>
<p><b>Optical flow</b> is the pattern of apparent motion of objects, surfaces and edges in a scene, caused by the relative motion between the camera and the scene. Compare frame T with frame T + 1, and give every point a <b>flow vector</b> (<i>u</i>, <i>v</i>): how far it moved across and how far it moved up or down.</p>
{fxs(
    fx('Flow magnitude', '|(<i>u</i>, <i>v</i>)| = ' + sqrt('<i>u</i>² + <i>v</i>²'), 'How far the point moved between two frames, in pixels per frame.', key=True),
    fx('Flow direction', 'θ = atan2(<i>v</i>, <i>u</i>)', 'The angle of the motion. 0° is right, 90° is up (with up taken as positive).'),
    fx('Speed', 'speed = magnitude × fps', 'Pixels per frame times frames per second gives pixels per second.', key=True))}
{viz('flow')}
<h3>Sparse or dense</h3>
{table(['Type', 'What it computes', 'When to use it'], [
    ['Sparse', 'Motion for a selected set of informative points, usually corners', 'Limited computing power, or a uniform still background where only a few objects need tracking'],
    ['Dense', 'Motion for almost every pixel', 'Crowded scenes such as pedestrians in a busy street, where motion matters everywhere. It needs much more computation.']])}
{steps('The lecture problem', [
    'A pixel moves by (u, v) = (3, 4) pixels between two frames.',
    'Magnitude: √(3² + 4²) = √(9 + 16) = √25 = 5 pixels per frame.',
    'At 30 fps each frame lasts 1/30 of a second, so speed = 5 × 30 = 150 pixels per second.',
    'Direction: atan2(4, 3) ≈ 53.13°, between right and up. With 8 bins of 45°, the nearest is up-right.'])}
{code('flow')}
{note('In flow pictures, colour shows direction and the strength of the colour shows speed. Learn to read the colour wheel, because exam figures often use it.', 'exam')}
''', kw=['video', 'time', 'optical flow', 'flow vector', 'magnitude', 'direction', 'atan2', 'speed', 'fps', 'sparse flow', 'dense flow', 'colour wheel'])

K.lesson('constancy', 'How flow is measured: brightness constancy', f'''
<p>A computer cannot see motion directly. It sees two grids of numbers. The classic trick is to assume that a point keeps its brightness as it moves. That assumption turns into one equation per pixel.</p>
{fxs(
    fx('Brightness constancy', '<i>I</i>(<i>x</i> + <i>u</i>, <i>y</i> + <i>v</i>, <i>t</i> + 1) = <i>I</i>(<i>x</i>, <i>y</i>, <i>t</i>)', 'The same point has the same brightness in the next frame, just somewhere else.'),
    fx('Optical flow constraint', '<i>I</i><sub><i>x</i></sub> <i>u</i> + <i>I</i><sub><i>y</i></sub> <i>v</i> + <i>I</i><sub><i>t</i></sub> = 0', 'From a first order Taylor expansion of the line above. <i>I</i><sub><i>x</i></sub>, <i>I</i><sub><i>y</i></sub> are the image gradients from chapter 1.2 and <i>I</i><sub><i>t</i></sub> is the change over time.', key=True))}
<p>One equation, two unknowns. On a straight edge you can only measure the motion across the edge, never the motion along it. This is the <b>aperture problem</b>, and you can watch it below.</p>
{viz('aperture')}
<h3>Two classic fixes (both from 1981)</h3>
{table(['Method', 'Extra assumption', 'Result'], [
    ['Lucas and Kanade', 'All pixels in a small window share one (u, v). Solve the window equations together by least squares.', 'Fast and local. Works at corners, fails on plain edges and flat areas. Used for sparse tracking.'],
    ['Horn and Schunck', 'The flow field is smooth over the whole image. Minimise the constraint error plus a smoothness penalty.', 'A dense field everywhere, but it blurs across object boundaries.']])}
{deep('the Lucas and Kanade equations', '<p>Stack the constraint for the <i>n</i> pixels of a window: <i>A</i> [<i>u</i>, <i>v</i>]<sup>T</sup> = −<i>b</i>, where row <i>i</i> of <i>A</i> is (<i>I</i><sub><i>x</i></sub>, <i>I</i><sub><i>y</i></sub>) at pixel <i>i</i> and <i>b</i> holds the <i>I</i><sub><i>t</i></sub> values. The least squares answer solves (<i>A</i><sup>T</sup><i>A</i>) [<i>u</i>, <i>v</i>]<sup>T</sup> = −<i>A</i><sup>T</sup><i>b</i>. The 2 × 2 matrix <i>A</i><sup>T</sup><i>A</i> is the same structure tensor used by the Harris corner detector. It can be inverted only when both of its eigenvalues are large, which happens at corners. That is the mathematical reason sparse trackers follow corners. Large motions break the Taylor approximation, so real systems run the method on an image pyramid, coarse to fine.</p>')}
{scene('your phone camera', '<p>Video stabilisation, slow motion and the night mode that merges several frames all need to know how pixels moved between frames. Modern phones estimate flow with small neural networks descended from FlowNet (2015) and RAFT (2020), but the target they estimate is the same (<i>u</i>, <i>v</i>) field defined here.</p>')}
''', kw=['brightness constancy', 'optical flow constraint', 'aperture problem', 'Lucas Kanade', 'Horn Schunck', 'least squares', 'structure tensor', 'image pyramid', 'FlowNet', 'RAFT'])

K.lesson('hof', 'HOF and MBH: describing motion', f'''
<p>Before deep learning, action recognition used hand made <b>motion descriptors</b>: compact lists of numbers that summarise how a video moves. The pipeline is video frames → optical flow → HOF or MBH → action clue.</p>
<h3>HOF: which way is the motion happening</h3>
<p>The <b>histogram of oriented optical flow</b> counts motion directions. The lecture gives four steps.</p>
<ol>
<li>Take two consecutive frames, T and T + 1.</li>
<li>Compute optical flow, a motion vector for each pixel or region.</li>
<li>Group the vectors by direction into bins: right, left, up, down and the diagonals.</li>
<li>Build the histogram. The tallest bin is the dominant direction. In fuller versions each vote is weighted by the flow magnitude.</li>
</ol>
{fx('HOF bin weight', '<i>H</i>[<i>b</i>] = Σ<sub>pixels with direction in bin <i>b</i></sub> ' + sqrt('<i>u</i>² + <i>v</i>²'), 'With 8 bins of 45°, the bin of a vector is round(θ ÷ 45°) mod 8.', key=True)}
<h3>MBH: where motion changes</h3>
<p>The <b>motion boundary histogram</b> does not look at the motion itself. It looks at where the motion changes. It takes the spatial gradient of the flow components <i>u</i> and <i>v</i>, exactly as HOG takes the gradient of the intensity, and builds orientation histograms of those gradients.</p>
{fx('MBH input', '∇<i>u</i> = (∂<i>u</i>/∂<i>x</i>, ∂<i>u</i>/∂<i>y</i>), &nbsp; ∇<i>v</i> = (∂<i>v</i>/∂<i>x</i>, ∂<i>v</i>/∂<i>y</i>)', 'If the camera adds the same vector to every pixel, every gradient stays the same. That is why MBH ignores camera motion.', key=True)}
{viz('hofmbh')}
{code('hof')}
{table(['', 'HOG', 'HOF', 'MBH'], [
    ['Question', 'What does it look like?', 'Which way is it moving?', 'Where does motion differ from its surroundings?'],
    ['Signal', 'Gradient of intensity', 'Flow direction', 'Gradient of the flow'],
    ['Good for', 'Shape of a person or object', 'Clear directional motion with a still camera', 'Camera motion, separating object from background'],
    ['Weakness', 'Ignores motion', 'Can be swamped by camera motion', 'Less direct for a pure direction summary']])}
{note('HOF is how things move. MBH is where motion differs. HOG is what it looks like. All three are the same operation, a local histogram of orientations, applied to three different signals.', 'tip')}
''', kw=['HOF', 'histogram of oriented optical flow', 'MBH', 'motion boundary histogram', 'HOG', 'motion descriptor', 'dominant direction', 'camera motion', 'flow gradient'])

K.lesson('scenarios', 'Which descriptor? The lecture scenarios', f'''
<p>The lecturer asked a series of which descriptor questions across both sessions. They are exactly the kind of reasoning exams test, so here they are with answers. Use the animation in the previous lesson to check each one.</p>
{table(['Scenario', 'Answer', 'Why'], [
    ['Two people walk in opposite directions. Are their HOF features the same?', 'Different', 'HOF is direction sensitive. Their tallest bins are on opposite sides. Over the whole frame you would see two peaks.'],
    ['A person walks while the camera pans right. Which descriptor isolates the person?', 'MBH', 'The pan adds uniform motion to the background, which swamps HOF. MBH suppresses uniform motion and keeps the person boundaries.'],
    ['A fixed camera films a ball moving up in front of a still wall.', 'HOF', 'No competing motion. HOF shows the upward bin directly and MBH adds little.'],
    ['A person cycles to the right.', 'Both tell different things', 'HOF says the dominant direction is right. MBH highlights the pedalling legs, whose motion differs from the steady torso.'],
    ['A drone flies beside a running cheetah, keeping it centred. You want the leg motion.', 'MBH', 'The grass streaks past everywhere. MBH ignores that uniform motion and highlights the legs moving relative to the body.']])}
<h3>The self study question: four camera and person combinations</h3>
{table(['Camera', 'Person', 'What the flow shows', 'Better descriptor'], [
    ['Fixed', 'Moving', 'Flow only on the person', 'HOF is enough'],
    ['Moving', 'Still', 'Uniform flow on the background, the person moves with it in the image', 'MBH (and it reports almost nothing, correctly)'],
    ['Moving the same way', 'Moving', 'The person can look almost still while the background streams past', 'MBH'],
    ['Moving the opposite way', 'Moving', 'Person and background flows point opposite ways and add up in size', 'MBH, or HOF after removing the camera motion']])}
{note('The rule from the lecture: whenever camera motion is present and could contaminate HOF, prefer MBH. When nothing competes with the motion you care about, HOF alone is sufficient.', 'exam')}
<h3>Two questions the lecture answered briefly</h3>
<p><b>Can HOF or MBH describe colour or appearance?</b> No. They are built only from flow direction and size. MBH gives at most a rough outline of a moving blob, enough to say human shaped, not enough to tell a fox from a dog.</p>
<p><b>Is MBH still used?</b> Yes, where deep models cannot run: small edge devices with no GPU and little memory. Elsewhere, learned motion features have replaced it.</p>
''', kw=['scenario', 'camera panning', 'opposite directions', 'cheetah', 'cyclist', 'ball moving up', 'which descriptor', 'camera motion combinations'])

K.lesson('pipeline', 'The traditional action recognition pipeline', f'''
<p>Here is how the descriptors were combined into a full action classifier before deep learning. Every step was designed and tuned by hand.</p>
<ol>
<li><b>Find space time interest points</b>, places where motion or appearance changes, such as moving joints and limbs.</li>
<li><b>Cut space time patches</b> around each point: small windows in space and time, at several scales.</li>
<li><b>Describe each patch</b> with HOG for appearance, HOF for motion or MBH for motion boundaries.</li>
<li><b>Cluster into a dictionary of visual words.</b> k-means groups similar descriptors from many training videos. Each cluster centre is one word.</li>
<li><b>Build a histogram of visual words</b> for each video: how often each word occurs. Every video becomes a vector of the same length.</li>
<li><b>Classify with an SVM</b> (support vector machine), which predicts the action label.</li>
</ol>
{fx('k-means objective', '<i>J</i> = Σ<sub><i>i</i></sub> ‖<b>x</b><sub><i>i</i></sub> − <b>μ</b><sub><i>c</i>(<i>i</i>)</sub>‖²', 'Alternate two steps: assign each descriptor to its nearest centre, then move each centre to the mean of its descriptors. <i>J</i> never increases.', key=True)}
{viz('bovw')}
{code('words')}
<p>This is the <b>bag of words</b> model from language processing, applied to video. A document is a count of words from a fixed dictionary, ignoring order. A video is a count of visual words, ignoring where and when each occurred.</p>
<h3>What deep learning replaced</h3>
{table(['Hand made step', 'Learned replacement'], [
    ['Interest points, patches, HOG and HOF', '3D CNNs that convolve over height, width and time together (for example C3D, I3D)'],
    ['Separate appearance and motion descriptors', 'Two stream networks: one stream sees RGB frames (like HOG), one sees stacked optical flow (like HOF), Simonyan and Zisserman 2014'],
    ['Visual word dictionary and SVM', 'Video transformers that attend across space and time, trained end to end']])}
{deep('why the two stream split mirrors HOG and HOF', '<p>The two stream network makes the same split the hand made pipeline made: appearance from single frames and motion from flow. Its flow stream takes a stack of about 10 flow fields (20 channels for <i>u</i> and <i>v</i>) as input, so its first layer learns filters over flow, which is what HOF and MBH were designed by hand to summarise. Later work (I3D, 2017) showed that adding the flow stream still helped even strong 3D CNNs, which is evidence that explicit motion carries information that RGB networks do not easily learn alone.</p>')}
''', kw=['action recognition', 'space time interest points', 'STIP', 'visual words', 'bag of visual words', 'k-means', 'SVM', 'support vector machine', '3D CNN', 'two stream network', 'video transformer'])

K.lesson('tasks', 'Modern video tasks', f'''
<p>The lecture ended this part with a quick tour of current video problems. The point is breadth: know what each task is and why it is hard.</p>
{table(['Task', 'What it means', 'Notes from the lecture'], [
    ['Frame interpolation', 'Predict an unknown frame between two known frames', 'Used for slow motion (for example Super SloMo). Smooth interpolation in a generative model latent space shows the model learned a continuous space rather than memorising examples.'],
    ['Stabilisation', 'Remove unwanted camera shake', 'A phone feature and a preprocessing step, since shake corrupts flow, HOF and MBH. Gaps created by the correction can be filled like inpainting.'],
    ['Video denoising', 'Remove noise using several frames', 'Image denoising from chapter 2.3, extended over time.'],
    ['Person re-identification', 'Find every appearance of one person across a video or cameras', 'Despite changes in pose, clothing colour or light. Used to follow one ID through a campus from entry gate to exit gate.'],
    ['Object propagation', 'Share detections over time', 'If an object was found confidently in frame T, use that to find it cheaply in frame T + 1 instead of starting again.'],
    ['Context and relations', 'Understand interactions, not single actions', 'Graph neural networks link people and objects. Example: a character interaction map and event flow built from a film.'],
    ['Video question answering and RAG', 'Answer questions about a long video', 'Summarise video into text first, then retrieve the relevant part and answer from text plus video. Example: insurance claims after a car accident.']])}
{note('Interpolation was defined in class only after several attempts. It is not generating new images and not editing pixels. It is predicting the missing frame between two frames.', 'warn')}
{scene('a university campus', '<p>Cameras at the main gate see a visitor enter. Re-identification gives that person an ID and matches them as they appear on other cameras, even when lighting and viewing angle change. Object propagation keeps tracking cheap between frames. At the exit gate the system confirms the same ID left. Each piece uses ideas from this chapter: motion between frames, descriptors that survive change, and sharing information over time.</p>')}
{ladder(
    '<p>A video is a flip book. Optical flow is a set of arrows that show where each bit of the picture moved from one page to the next. HOF counts which way the arrows point. MBH looks for places where the arrows suddenly change, like at the edge of a moving car.</p>',
    '<p>Flow (<i>u</i>, <i>v</i>) has magnitude √(<i>u</i>² + <i>v</i>²) and speed magnitude × fps. Brightness constancy gives <i>I</i><sub>x</sub><i>u</i> + <i>I</i><sub>y</sub><i>v</i> + <i>I</i><sub>t</sub> = 0, one equation for two unknowns. HOF bins flow directions, MBH bins gradients of the flow, and a bag of visual words with an SVM classifies the action.</p>',
    '<p>Lucas and Kanade solve the constraint by least squares in a window, with the structure tensor deciding whether the answer is stable. Horn and Schunck add a global smoothness term and solve a variational problem. Dense trajectories (2011) tracked points through dense flow for 15 frames and described each track with HOG, HOF and MBH, which made MBH the strongest hand made motion feature of its time.</p>',
    '<p>Learned flow estimators such as RAFT build a 4D correlation volume between all pixel pairs and refine the flow with a recurrent update. Self supervised methods train flow by warping one frame onto the next and penalising the photometric error, which is brightness constancy turned into a loss. Video foundation models now learn motion implicitly from masked frame prediction, and long video understanding is moving toward retrieval over text and visual memories.</p>')}
''', kw=['frame interpolation', 'Super SloMo', 'latent space', 'stabilisation', 'video denoising', 'person re-identification', 're-ID', 'object propagation', 'graph neural network', 'context', 'video RAG', 'retrieval augmented generation'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What extra information does a video have that a single image does not?', ['Colour', 'Time', 'Edges', 'Resolution'], 1,
       'The lecture said it in one word.', 'A video is 2D plus time. Motion between frames is the new signal.')
K.quiz('e', 'A pixel has flow (u, v) = (6, 8). What is its magnitude?', ['14', '10', '48', '2'], 1,
       '√(u² + v²).', '√(36 + 64) = √100 = 10 pixels per frame.')
K.quiz('e', 'When is sparse optical flow the better choice?', [
    'In a crowded scene where everything moves', 'When computing power is limited or the background is still and only a few objects need tracking', 'Always', 'Never'], 1,
    'Sparse tracks only a few points.', 'The lecture rule: limited resources or a uniform background means sparse. Crowds need dense flow.')
K.quiz('m', 'Two people walk in opposite directions. Their HOF features are', ['The same', 'Different, because HOF is direction sensitive', 'Both empty', 'Identical to HOG'], 1,
       'Which bins are tallest?', 'One person fills the right bin and the other the left bin, so the histograms differ.')
K.quiz('m', 'A person walks while the camera pans. Which descriptor best isolates the person\'s own motion?', ['HOG', 'HOF', 'MBH', 'A colour histogram'], 2,
       'Uniform background motion has zero gradient.', 'MBH takes the gradient of the flow, so the uniform pan cancels and the person boundaries remain.')
K.quiz('m', 'A fixed camera films a ball rising in front of a still wall. Which descriptor captures the upward direction most clearly?', ['MBH', 'HOF', 'HOG', 'Neither'], 1,
       'Is there any competing motion?', 'With no camera or background motion, HOF directly shows the upward bin.')
K.quiz('m', 'What is the aperture problem?', [
    'The lens is too small', 'Through a small window you can only measure the motion across an edge, not along it', 'Too few frames per second', 'Colour is lost in video'], 1,
    'One equation, two unknowns.', 'The constraint Ixu + Iyv + It = 0 fixes only the component of motion along the gradient, which is across the edge.')
K.quiz('h', 'In the traditional pipeline, what produces the dictionary of visual words?', ['An SVM', 'k-means clustering of descriptors from many training videos', 'Optical flow', 'Histogram equalisation'], 1,
       'Group similar descriptors.', 'Each k-means cluster centre is one visual word. New descriptors are assigned to the nearest centre.')
K.quiz('h', 'Why does adding the same camera motion to every pixel leave MBH unchanged?', [
    'MBH ignores the flow', 'MBH uses spatial gradients of the flow, and the gradient of a constant is zero', 'MBH uses colour', 'Camera motion is always zero'], 1,
    'Differentiate u + c.', '∂(u + c)/∂x = ∂u/∂x. A constant added everywhere disappears in every derivative.')
K.quiz('h', 'Which modern network directly mirrors the HOG and HOF split?', ['U-Net', 'Two stream network: an RGB stream and an optical flow stream', 'GAN', 'Autoencoder'], 1,
       'Appearance and motion.', 'The RGB stream sees appearance like HOG, the flow stream sees motion like HOF.')
K.quiz('x', 'Lucas and Kanade can solve for flow reliably at a corner but not on a straight edge. Why?', [
    'Corners are brighter', 'At a corner the gradients point in two directions, so the 2 × 2 matrix AᵀA has two large eigenvalues and can be inverted', 'Edges have no gradient', 'Corners move faster'], 1,
    'Think about the structure tensor.', 'On a straight edge all gradients are parallel, so AᵀA has one eigenvalue near zero and the system is singular. That is the aperture problem in matrix form.')
K.quiz('x', 'Which statement about video frame interpolation is correct?', [
    'It edits pixel intensities of one frame', 'It predicts an intermediate frame between two known frames, and smooth latent interpolation suggests a model learned a continuous latent space', 'It is the same as compression', 'It removes camera shake'], 1,
    'The answer the class reached last.', 'Interpolation fills in the frame between two frames. In generative models, smooth paths between two samples are evidence against memorisation.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A pixel moves by (u, v) = (3, 4) between frames. What is the flow magnitude in pixels per frame?', '5', 'Magnitude = √(u² + v²).',
       ['u² = 9 and v² = 16.', '9 + 16 = 25.', eq('√25 = 5 pixels per frame')], check=5)
K.calc('e', 'The same pixel is in a 30 fps video. What is its speed in pixels per second?', '150', 'Speed = magnitude × fps.',
       ['Magnitude = 5 pixels per frame.', 'Each second has 30 frames.', eq('5 × 30 = 150 pixels per second')], check=150)
K.calc('e', 'At 5 pixels per frame and 30 fps, how far does the pixel travel in 0.5 seconds?', '75', 'Find the number of frames in 0.5 s first.',
       ['0.5 s × 30 fps = 15 frames.', 'Each frame moves 5 pixels.', eq('15 × 5 = 75 pixels')], check=75)
K.calc('m', 'What is the direction θ = atan2(v, u) of the flow (3, 4) in degrees? Give two decimals.', '53.13', 'tan θ = v ÷ u = 4 ÷ 3.',
       ['v ÷ u = 4 ÷ 3 ≈ 1.3333.', 'Both u and v are positive, so θ is between 0° and 90°.', eq('θ = arctan(1.3333) ≈ 53.13°')], check=53.13, tol=0.006)
K.calc('m', 'With 8 HOF bins of 45° (bin 0 = right, bin 1 = up-right, bin 2 = up, and so on), which bin does θ = 53.13° fall in?', '1', 'bin = round(θ ÷ 45) mod 8.',
       ['53.13 ÷ 45 ≈ 1.18.', 'Rounded to the nearest whole number: 1.', eq('bin = 1 mod 8 = 1, up-right')], check=1)
K.calc('m', 'A HOF uses magnitude weighting. The flow vectors are (2, 0), (3, 0), (0, 4) and (−1, 0). What is the weight of the right bin?', '5', 'Only vectors pointing right vote for it, each with its magnitude.',
       ['(2, 0) points right with magnitude 2.', '(3, 0) points right with magnitude 3. (0, 4) is up and (−1, 0) is left.', eq('H[right] = 2 + 3 = 5'), 'The up bin gets 4 and the left bin 1, so right is the dominant direction.'], check=5)
K.calc('m', 'A person walks right at 4 pixels per frame while the camera pans right at 3 pixels per frame. What is the person\'s horizontal flow in the image?', '1', 'Panning right shifts the whole picture left by the pan amount.',
       ['Image flow = own motion − pan.', 'Person: 4 − 3.', eq('u = 1 pixel per frame'), 'The background gets u = −3. HOF now sees mostly leftward motion, which is why MBH is preferred here.'], check=1)
K.calc('h', 'The horizontal flow along one row is u = [2, 2, 2, 6, 6, 6]. Using the forward difference u[i + 1] − u[i], what is the largest motion boundary response?', '4', 'Only one neighbour pair differs.',
       ['Differences: 0, 0, 4, 0, 0.', 'The flat parts give 0, however fast they move.', eq('max = 6 − 2 = 4'), 'MBH fires only at the boundary between the two motions.'], check=4)
K.calc('h', 'At one pixel I<sub>x</sub> = 2, I<sub>y</sub> = 1 and I<sub>t</sub> = −8. If the vertical motion is known to be v = 0, what is u?', '4', 'Use I<sub>x</sub>u + I<sub>y</sub>v + I<sub>t</sub> = 0.',
       ['Substitute: 2u + 1 × 0 − 8 = 0.', '2u = 8.', eq('u = 4 pixels per frame'), 'Without knowing v, the single equation would allow infinitely many answers, which is the aperture problem.'], check=4)
K.calc('h', 'A 1920 × 1080 frame is tracked with dense flow, or with sparse flow on 500 corners. How many times more vectors does dense flow compute? Give one decimal.', '4147.2', 'One vector per pixel for dense flow.',
       ['Dense: 1920 × 1080 = 2,073,600 vectors.', 'Sparse: 500 vectors.', eq('2,073,600 ÷ 500 = 4,147.2')], check=4147.2)
K.calc('x', 'An edge at 45° moves straight right at 4 pixels per frame. Seen through a small aperture, how fast does it appear to move? Give two decimals.', '2.83', 'Only the component along the edge normal is visible.',
       ['The normal of a 45° edge is at 135°.', 'The angle between the motion (0°) and the normal is 135°, and |cos 135°| ≈ 0.7071.', eq('4 × 0.7071 ≈ 2.83 pixels per frame'), 'It also seems to move at right angles to the edge, not to the right.'], check=4 * 0.5 ** 0.5, tol=0.006)
K.calc('x', 'A clip of 30 frames gets one new frame inserted between every pair of neighbours. How many frames does it have afterwards?', '59', 'Count the gaps between 30 frames.',
       ['30 frames have 29 gaps between neighbours.', 'One new frame per gap adds 29 frames.', eq('30 + 29 = 59 frames'), 'Played at the original frame rate, the clip lasts about twice as long, which is slow motion.'], check=59)

# ---------------------------------------------------------------- assignments
K.assign('flowstats', 'e', 'Flow magnitude, direction and speed',
         '<p>Write <code>flow_stats(u, v, fps)</code> that returns <code>[magnitude, angle, speed]</code>: the magnitude rounded to 2 decimals, the direction atan2(v, u) in degrees between 0 and 360 rounded to 1 decimal, and magnitude × fps rounded to 1 decimal.</p>',
         '''
from math import atan2, degrees, sqrt

def flow_stats(u, v, fps):
    # your code here
    pass
''', [('flow_stats(3, 4, 30)', [5.0, 53.1, 150.0]), ('flow_stats(-2, 0, 24)', [2.0, 180.0, 48.0]), ('flow_stats(0, -5, 60)', [5.0, 270.0, 300.0])],
         '''
from math import atan2, degrees, sqrt

def flow_stats(u, v, fps):
    m = sqrt(u * u + v * v)
    a = degrees(atan2(v, u)) % 360
    return [round(m, 2), round(a, 1), round(m * fps, 1)]
''', 'atan2 returns angles from −180° to 180°. The % 360 moves negative angles into range.',
         '<p>The third test points straight down, which atan2 reports as −90°. Taking it modulo 360 gives 270°.</p>')
K.assign('hof', 'm', 'Build a HOF histogram',
         '<p>Write <code>hof(flows, bins=8)</code>. For each (u, v) with non zero magnitude, find its bin as round(θ ÷ (360 ÷ bins)) mod bins, where θ = atan2(v, u) in degrees, and add its magnitude. Return the histogram with values rounded to 2 decimals.</p>',
         '''
from math import atan2, degrees, sqrt

def hof(flows, bins=8):
    # your code here
    pass
''', [('hof([(2, 0), (3, 0), (0, 4), (-1, 0)])', [5.0, 0.0, 4.0, 0.0, 1.0, 0.0, 0.0, 0.0]),
      ('hof([(1, 1), (0, 0)])', [0.0, 1.41, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
      ('hof([(0, -2), (3, 0)], 4)', [3.0, 0.0, 0.0, 2.0])],
         '''
from math import atan2, degrees, sqrt

def hof(flows, bins=8):
    h = [0.0] * bins
    width = 360 / bins
    for u, v in flows:
        m = sqrt(u * u + v * v)
        if m == 0:
            continue
        b = round(degrees(atan2(v, u)) / width) % bins
        h[b] += m
    return [round(x, 2) for x in h]
''', 'Skip zero vectors, because they have no direction.',
         '<p>The first test is the worked problem: right gets 5, up gets 4, left gets 1. Real HOF splits the frame into cells and joins the cell histograms, as HOG does.</p>')
K.assign('boundary', 'e', 'Find motion boundaries',
         '<p>Write <code>motion_boundaries(u)</code> that takes one row of horizontal flow values and returns the list of |u[i + 1] − u[i]| for every neighbouring pair.</p>',
         '''
def motion_boundaries(u):
    # your code here
    pass
''', [('motion_boundaries([2, 2, 2, 6, 6, 6])', [0, 0, 4, 0, 0]), ('motion_boundaries([-3, -3, 1, 1, -3])', [0, 4, 0, 4]), ('motion_boundaries([5, 5, 5])', [0, 0])],
         '''
def motion_boundaries(u):
    return [abs(u[i + 1] - u[i]) for i in range(len(u) - 1)]
''', 'zip(u, u[1:]) or a range over len(u) − 1 gives each neighbouring pair.',
         '<p>The last test is a uniform camera pan: everything moves at 5, so there is no boundary at all. That is MBH ignoring camera motion in one line.</p>')
K.assign('bovw', 'm', 'Bag of visual words',
         '<p>Write <code>bag_of_words(descriptors, words)</code>. Assign each descriptor (a tuple of numbers) to the word with the smallest squared Euclidean distance, ties going to the lower index, and return the list of counts per word.</p>',
         '''
def bag_of_words(descriptors, words):
    # your code here
    pass
''', [('bag_of_words([(0, 0), (1, 1), (9, 9)], [(0, 0), (10, 10)])', [2, 1]),
      ('bag_of_words([(0.22, 0.28), (0.18, 0.35), (0.31, 0.7), (0.7, 0.3), (0.25, 0.33)], [(0.2, 0.3), (0.3, 0.75), (0.75, 0.25), (0.8, 0.7)])', [3, 1, 1, 0]),
      ('bag_of_words([], [(1, 2)])', [0]),
      ('bag_of_words([(5, 5)], [(4, 4), (6, 6)])', [1, 0])],
         '''
def bag_of_words(descriptors, words):
    counts = [0] * len(words)
    for d in descriptors:
        dists = [sum((a - b) ** 2 for a, b in zip(d, w)) for w in words]
        counts[dists.index(min(dists))] += 1
    return counts
''', 'For each descriptor compute the distance to every word and take the index of the smallest.',
         '<p>list.index returns the first minimum, which handles the tie in the last test. The counts vector is what an SVM would classify.</p>')

K.must('Optical flow', 'Flow (u, v) per pixel between frames T and T + 1. Magnitude √(u² + v²), direction atan2(v, u), speed = magnitude × fps. Lecture: (3, 4) gives 5 px per frame, 150 px per second at 30 fps.')
K.must('Sparse and dense', 'Sparse tracks a few corners and is cheap. Dense gives every pixel a vector and suits crowded scenes but costs much more.')
K.must('Brightness constancy', 'Ixu + Iyv + It = 0: one equation, two unknowns, so the aperture problem. Lucas and Kanade (window, least squares, corners) and Horn and Schunck (global smoothness).')
K.must('HOF and MBH', 'HOF bins flow directions (how things move). MBH bins gradients of the flow (where motion differs) and ignores uniform camera motion. HOG is appearance.')
K.must('Action pipeline', 'Interest points → patches → HOG, HOF, MBH → k-means visual words → histogram → SVM. Replaced by 3D CNNs, two stream networks and video transformers.')
K.must('Video tasks', 'Interpolation predicts a missing middle frame. Also stabilisation, denoising, re-identification, propagation over time, context graphs and video RAG.')

T = K.topic(
    slug='motion-video', topic='motion', step=(3, 'Motion and video', 'cv-motion', 'Adding time: how pixels move between frames, how motion is described, and how actions were recognised before and after deep learning.', 'College'),
    title='Optical flow, HOF, MBH and video tasks', short='Motion and video', badge='3.1', minutes=50,
    lead='Add time to images. Measure how each pixel moves with optical flow, see why a single edge cannot reveal its full motion, describe motion with HOF and MBH, and follow the classic action recognition pipeline to today\'s video tasks.',
    desc='Optical flow vectors, magnitude and speed, sparse and dense flow, brightness constancy and the aperture problem, HOF, MBH and the lecture scenarios, bag of visual words with k-means and SVM, and modern video tasks.',
    summary='Optical flow and the aperture problem, HOF versus MBH with every lecture scenario, the bag of visual words pipeline and modern video tasks.',
    keywords=['optical flow', 'flow magnitude', 'sparse flow', 'dense flow', 'aperture problem', 'Lucas Kanade', 'HOF', 'MBH', 'action recognition', 'visual words', 'k-means', 'SVM', 'two stream', 'frame interpolation', 're-identification', 'video RAG'],
    recap='<p>Video adds time. Optical flow gives each pixel a motion vector, measured from brightness constancy, which on its own only sees motion across an edge. HOF summarises flow directions, MBH summarises where the flow changes and so ignores camera motion. Visual words and an SVM turned these into action labels before deep networks learned the whole chain.</p>')
