# NLP section, chapter 3.3: vanishing and exploding gradients, LSTM, GRU, BiLSTM and xLSTM. Source: FoVL lecture 3
# slides 72 to 76 and 92 to 108 (consequences of vanishing gradients and the four fixes, the effect on an RNN language
# model, gates, the LSTM memory cell and equations, how the LSTM solves the problem, "why LSTM is better at remembering",
# the BiLSTM code-switching question with 60-dimensional embeddings, hidden 32 per direction and 4 tags, the GRU gates
# and equations, issues with recurrent models and xLSTM of Beck et al. 2024).
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('vanish', r'''
# How fast a signal fades through time: RNN step factor against an LSTM forget gate
rnn_factor, forget = 0.6, 0.95
for T in [5, 10, 20, 50]:
    print("after", str(T).rjust(2), "steps  RNN", format(rnn_factor ** (T - 1), ".2e"), "  LSTM", round(forget ** (T - 1), 4))
''')

K.code('lstm', r'''
# One LSTM step with one number per vector
import math
sig = lambda x: 1 / (1 + math.exp(-x))
h_prev, c_prev, x = 0.5, 0.8, 1.0
W = {"f": (0.5, 1.0, 0.5), "i": (-1.0, 0.5, -0.5), "o": (0.5, 0.5, 0.0), "c": (-1.0, 0.2, -0.3)}   # (w_h, w_x, b)
f = sig(W["f"][0] * h_prev + W["f"][1] * x + W["f"][2])
i = sig(W["i"][0] * h_prev + W["i"][1] * x + W["i"][2])
o = sig(W["o"][0] * h_prev + W["o"][1] * x + W["o"][2])
c_tilde = math.tanh(W["c"][0] * h_prev + W["c"][1] * x + W["c"][2])
c = f * c_prev + i * c_tilde
h = o * math.tanh(c)
print("gates f, i, o =", round(f, 4), round(i, 4), round(o, 4))
print("candidate =", round(c_tilde, 4), " new cell c =", round(c, 4), " output h =", round(h, 4))
''')

K.code('gru', r'''
# One GRU step with one number per vector
import math
sig = lambda x: 1 / (1 + math.exp(-x))
h_prev, x = 0.8, 1.0
z = sig(0.5 * h_prev + 1.0 * x - 2.0)        # update gate
r = sig(1.0 * h_prev + 0.5 * x + 0.0)        # reset gate
h_tilde = math.tanh(1.0 * x + 0.8 * (r * h_prev))
h = (1 - z) * h_prev + z * h_tilde
print("z =", round(z, 4), " r =", round(r, 4), " candidate =", round(h_tilde, 4), " h =", round(h, 4))
''')

K.lesson('vanishing', 'Vanishing and exploding gradients', f'''
<p>To learn that a word at step 1 matters for a prediction at step 20, the gradient must travel back through 19 steps. Each step multiplies it by the same kind of factor. If that factor is smaller than 1 the gradient shrinks towards 0 (vanishing). If it is bigger than 1 it blows up (exploding).</p>
{fxs(fx('One step back', frac('∂h<sup>(t)</sup>', '∂h<sup>(t−1)</sup>') + ' = diag(σ′(W<sub>h</sub>h<sup>(t−1)</sup> + W<sub>x</sub>x<sup>(t)</sup> + b)) W<sub>h</sub>', 'The Jacobian of one RNN step.', key=True),
     fx('Many steps back', frac('∂J<sup>(t)</sup>', '∂h<sup>(j)</sup>') + ' = ' + frac('∂J<sup>(t)</sup>', '∂h<sup>(t)</sup>') + ' ∏<sub>j < k ≤ t</sub> ' + frac('∂h<sup>(k)</sup>', '∂h<sup>(k−1)</sup>'), 'A product of t − j Jacobians.', key=True),
     fx('Size bound', '‖∂h<sup>(t)</sup> ÷ ∂h<sup>(j)</sup>‖ ≤ (γ ‖W<sub>h</sub>‖)<sup>t−j</sup>', 'γ bounds σ′ (1 for tanh). Below 1 the bound shrinks exponentially.'))}
{viz('rnnunroll')}
{code('vanish')}
{steps('Effect on an RNN language model', [
    '"When she tried to print her tickets, she found that the printer was out of toner. She went to the stationery store to buy more toner. It was very overpriced. After installing the toner into the printer, she finally printed her ___"',
    'The answer "tickets" depends on a word about 30 steps back.',
    'If the gradient from step 30 to step 1 is close to 0, the model cannot learn this dependency.',
    eq('RNN language models learn nearby effects well and long range effects poorly')])}
{table(['Consequence (slide 72)', 'Fix'], [['early layers and early time steps learn very slowly', 'ReLU activations'], ['deep networks become hard to train', 'suitable weight initialisation, for example orthogonal W<sub>h</sub>'], ['long dependencies are lost', 'residual or more direct connections, attention'], ['memory fades in a plain RNN', 'LSTM and GRU for sequential data']])}
{fxs(fx('Gradient clipping (for exploding gradients)', 'if ‖g‖ > τ: &nbsp; g ← ' + frac('τ', '‖g‖') + ' g', 'Keeps the direction, limits the step size.'))}
{note('Vanishing gradients mean the model does not learn long range dependencies. They do not mean the loss is 0 or that training stops at once. Exploding gradients show up as NaN losses.', 'warn')}
''', kw=['vanishing gradient', 'exploding gradient', 'Jacobian', 'gradient clipping', 'long range dependency'])

K.lesson('lstm', 'Long Short-Term Memory', f'''
<p>Hochreiter and Schmidhuber (1997) gave the RNN a separate memory cell c<sup>(t)</sup>, the horizontal line on top of the diagram. Three gates, each a vector of numbers between 0 and 1, decide what to erase, what to write and what to show. A gate value of 1 means open, 0 means closed.</p>
{fxs(fx('Forget gate', 'f<sup>(t)</sup> = σ(W<sub>f</sub>h<sup>(t−1)</sup> + U<sub>f</sub>x<sup>(t)</sup> + b<sub>f</sub>)', 'What to keep from the old cell.', key=True),
     fx('Input gate', 'i<sup>(t)</sup> = σ(W<sub>i</sub>h<sup>(t−1)</sup> + U<sub>i</sub>x<sup>(t)</sup> + b<sub>i</sub>)', 'How much of the new content to write.'),
     fx('Output gate', 'o<sup>(t)</sup> = σ(W<sub>o</sub>h<sup>(t−1)</sup> + U<sub>o</sub>x<sup>(t)</sup> + b<sub>o</sub>)', 'How much of the cell to show as h.'),
     fx('New cell content', 'c̃<sup>(t)</sup> = tanh(W<sub>c</sub>h<sup>(t−1)</sup> + U<sub>c</sub>x<sup>(t)</sup> + b<sub>c</sub>)', 'The candidate to write.'),
     fx('Cell state', 'c<sup>(t)</sup> = f<sup>(t)</sup> ⊙ c<sup>(t−1)</sup> + i<sup>(t)</sup> ⊙ c̃<sup>(t)</sup>', 'Erase some, write some. ⊙ is element-wise.', key=True),
     fx('Hidden state', 'h<sup>(t)</sup> = o<sup>(t)</sup> ⊙ tanh(c<sup>(t)</sup>)', 'What the next layer and the next step see.', key=True))}
{viz('lstmcell')}
{steps('One cell update by hand (the widget start values)', [
    'c<sup>(t−1)</sup> = 0.8, candidate c̃ = −0.5, f = 0.9, i = 0.2, o = 0.7.',
    'Keep: 0.9 × 0.8 = 0.72. Write: 0.2 × (−0.5) = −0.10.',
    eq('c<sup>(t)</sup> = 0.72 − 0.10 = 0.62'),
    eq('h<sup>(t)</sup> = 0.7 × tanh(0.62) = 0.7 × 0.5511 = 0.3858')])}
{code('lstm')}
{fxs(fx('LSTM layer parameters', '4 · H · (E + H) + 4H', 'Four blocks (f, i, o, c̃), each with an H × E input matrix, an H × H recurrent matrix and a bias.', key=True))}
{scene('remembering the subject of a long sentence', '<p>In "The keys to the old wooden cabinet in the hall <b>are</b> on the table", the verb must agree with "keys", eight words back. An LSTM can write "subject is plural" into one cell dimension, keep its forget gate near 1 while the cabinet phrase goes by, and read it out at the verb. A plain RNN tends to let the nearer word "hall" win.</p>')}
''', kw=['LSTM', 'memory cell', 'forget gate', 'input gate', 'output gate', 'cell state'])

K.lesson('why-lstm', 'How the LSTM keeps gradients alive', f'''
<p>The key is the additive update of the cell. From c<sup>(t)</sup> = f ⊙ c<sup>(t−1)</sup> + i ⊙ c̃, the direct path from the old cell to the new one is multiplied only by the forget gate, with no squashing function and no shared weight matrix in between.</p>
{fxs(fx('Direct cell path', frac('∂c<sup>(t)</sup>', '∂c<sup>(t−1)</sup>') + ' ≈ diag(f<sup>(t)</sup>)', 'Ignoring the paths through the gates. With f = 1 the cell is a straight wire.', key=True),
     fx('Over many steps', '∏<sub>k</sub> f<sup>(k)</sup>', 'The network learns f. Near 1 it keeps information for many steps, near 0 it forgets on purpose.'))}
{viz('gates')}
{table(['', 'RNN', 'LSTM'], [['memory', 'h<sup>(t)</sup>, rewritten every step', 'separate cell c<sup>(t)</sup>, changed only through gates'], ['gradient through one step', 'W<sub>h</sub> times tanh′', 'f, learned per step'], ['to keep a fact', 'weights must be tuned just right, which is very hard', 'set the forget gate to 1 and the input gate to 0']])}
<p>The slide summary: if the forget gate tells the model to remember everything, the memory inside the LSTM hardly changes and the information can stay for many time steps. A normal RNN has no special memory control, so important information often fades as time passes.</p>
{note('An LSTM does not guarantee there is no vanishing or exploding gradient. It makes it much easier for the model to learn long range dependencies. In practice it handles about 100 steps well where a plain RNN manages about 7.', 'exam')}
{deep('residual connections are the same idea', '<p>ResNets add x to the output of a block: y = x + F(x), so ∂y/∂x = I + ∂F/∂x always contains an identity path. The LSTM cell with f = 1 is that identity path through time. Highway networks (Srivastava et al. 2015) made the link explicit with a learned gate between the identity and the transformation.</p>')}
''', kw=['additive update', 'forget gate path', 'long memory', 'residual connections'])

K.lesson('gru', 'Gated Recurrent Units', f'''
<p>Cho and others (2014) proposed a simpler gated unit with no separate cell. The hidden state holds both short and long term memory. An update gate decides how much new information replaces the old memory, and a reset gate decides how much of the past is used to build the new candidate.</p>
{fxs(fx('Update gate', 'z<sub>t</sub> = σ(W<sub>z</sub>x<sub>t</sub> + U<sub>z</sub>h<sub>t−1</sub> + b<sub>z</sub>)', 'How much new information to store.', key=True),
     fx('Reset gate', 'r<sub>t</sub> = σ(W<sub>r</sub>x<sub>t</sub> + U<sub>r</sub>h<sub>t−1</sub> + b<sub>r</sub>)', 'How much of the past to forget when building the candidate.'),
     fx('Candidate', 'h̃<sub>t</sub> = tanh(W<sub>h</sub>x<sub>t</sub> + U<sub>h</sub>(r<sub>t</sub> ⊙ h<sub>t−1</sub>) + b<sub>h</sub>)', 'New information from the input and the filtered past.'),
     fx('New state', 'h<sub>t</sub> = (1 − z<sub>t</sub>) ⊙ h<sub>t−1</sub> + z<sub>t</sub> ⊙ h̃<sub>t</sub>', 'A blend of old and new. z = 0 keeps the old state exactly.', key=True))}
{steps('One GRU update by hand', [
    'h<sub>t−1</sub> = 0.8, candidate h̃ = −0.5, update gate z = 0.3.',
    'Old part: (1 − 0.3) × 0.8 = 0.56.',
    'New part: 0.3 × (−0.5) = −0.15.',
    eq('h<sub>t</sub> = 0.56 − 0.15 = 0.41')])}
{code('gru')}
{table(['', 'LSTM', 'GRU'], [['gates', 'forget, input, output', 'update, reset'], ['memory', 'cell c and state h', 'state h only'], ['parameter blocks', '4', '3'], ['parameters (E = 100, H = 64, no biases)', '4 × 64 × 164 = 41,984', '3 × 64 × 164 = 31,488'], ['when to use', 'default, long dependencies, plenty of data', 'faster, fewer parameters, small data']])}
{note('In a GRU, (1 − z) plays the role of the LSTM forget gate and z the role of the input gate. Tying them means writing new information always erases the same amount of old information.', 'tip')}
''', kw=['GRU', 'update gate', 'reset gate', 'candidate state', 'LSTM vs GRU'])

K.lesson('bilstm', 'BiLSTM, the parameter question and xLSTM', f'''
<p>A BiLSTM runs one LSTM forwards and another backwards and joins their states, exactly like the BiRNN of chapter 3.2. The lecture asks for its parameter count in a language identification task for code-switched text, where each word must be tagged with its language, as in "main kal market jaaunga to buy vegetables".</p>
{steps('The BiLSTM question', [
    'Embedding 60, hidden 32 per direction, 4 language tags, no biases.',
    'One LSTM direction: 4 × 32 × (60 + 32) = 4 × 32 × 92 = 11,776.',
    'Two directions: 2 × 11,776 = 23,552.',
    'Output layer on the joined 64 numbers: 64 × 4 = 256.',
    eq('Total = 23,552 + 256 = 23,808')])}
{viz('paramcount', model='bilstm', E=60, H=32, K=4)}
<p>Recurrent models have two deeper issues. Information between distant words must pass through every step in between (linear interaction distance). And step t cannot start before step t − 1 finishes, so the computation cannot be parallelised over the sequence, which inhibits training on very large datasets. These issues led to attention and transformers.</p>
{table(['xLSTM (Beck et al. 2024)', 'What changes'], [['exponential gating', 'gates can grow beyond 1 with a normaliser, so the model can revise a stored decision more strongly'], ['sLSTM', 'scalar memory with memory mixing between heads'], ['mLSTM', 'a matrix memory updated with a covariance rule, fully parallelisable'], ['result', 'LSTM style models that scale close to transformers on language modelling']])}
{ladder(
    '<p>A plain RNN forgets things quickly. An LSTM has a notebook and three switches: erase, write and show. Keeping the erase switch off lets it remember for a long time.</p>',
    '<p>LSTM: c = f ⊙ c<sub>old</sub> + i ⊙ c̃, h = o ⊙ tanh(c). GRU: h = (1 − z) ⊙ h<sub>old</sub> + z ⊙ h̃. Parameters 4H(E + H) and 3H(E + H), doubled for a bidirectional model.</p>',
    '<p>The additive cell path gives ∂c<sup>(t)</sup>/∂c<sup>(t−1)</sup> ≈ diag(f), a learned and input dependent factor instead of a fixed W<sub>h</sub> times tanh′. This is the same identity path idea as residual connections.</p>',
    '<p>xLSTM revisits the LSTM with exponential gates and a matrix memory. State space models such as Mamba also keep a recurrent state but train in parallel, which reopens the question of whether attention is needed at every layer.</p>')}
''', kw=['BiLSTM', '23,808', 'code-switching', 'parallelism', 'xLSTM'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A gradient that shrinks towards 0 as it goes back in time is', ['exploding', 'vanishing', 'clipped', 'normalised'], 1, 'Factors below 1.', 'Vanishing gradient.')
K.quiz('e', 'The LSTM gate that decides what to erase from the cell is the', ['input gate', 'output gate', 'forget gate', 'reset gate'], 2, 'f.', 'f multiplies the old cell.')
K.quiz('e', 'A GRU has how many gates?', ['1', '2', '3', '4'], 1, 'Update and reset.', 'Two gates and no separate cell.')
K.quiz('e', 'Gradient clipping fixes', ['vanishing gradients', 'exploding gradients', 'overfitting', 'slow inference'], 1, 'Too large.', 'It rescales g when ‖g‖ is above a threshold.')
K.quiz('m', 'In an LSTM, h<sup>(t)</sup> equals', ['f ⊙ c', 'o ⊙ tanh(c)', 'i ⊙ c̃', 'tanh(c)'], 1, 'Output gate.', 'The output gate filters the squashed cell.')
K.quiz('m', 'f = 1 and i = 0 in an LSTM means', ['the cell is erased', 'the cell is copied unchanged', 'the output is 0', 'training stops'], 1, 'Keep all, write nothing.', 'c<sup>(t)</sup> = c<sup>(t−1)</sup>.')
K.quiz('m', 'In a GRU with z = 0', ['the new state is the candidate', 'the new state equals the old state', 'the state is reset to 0', 'the output is random'], 1, 'h = (1 − z)h<sub>old</sub> + z h̃.', 'Nothing new is written.')
K.quiz('m', 'Which is not listed on the slide as a fix for vanishing gradients?', ['ReLU', 'weight initialisation', 'residual connections', 'a larger vocabulary'], 3, 'Slide 72.', 'Vocabulary size has nothing to do with it.')
K.quiz('m', 'Parameters of one LSTM direction with E = 60, H = 32, no biases?', ['5,888', '8,832', '11,776', '23,552'], 2, '4 × 32 × 92.', '11,776.')
K.quiz('h', 'Why can an LSTM keep gradients alive over many steps?', ['it has more parameters', 'the cell update is additive, so ∂c<sup>(t)</sup>/∂c<sup>(t−1)</sup> ≈ f, which can stay near 1', 'it uses ReLU', 'it reads backwards'], 1, 'The cell path.', 'No repeated multiplication by W<sub>h</sub> and tanh′ on that path.')
K.quiz('h', 'BiLSTM: E = 60, H = 32 per direction, 4 tags, no biases. Total?', ['11,776', '23,552', '23,808', '24,064'], 2, 'Two directions plus 64 × 4.', '23,552 + 256 = 23,808.')
K.quiz('h', 'A main reason recurrent models were replaced for very large data is', ['they cannot use embeddings', 'their steps cannot be parallelised over the sequence', 'they need labelled data', 'they have no loss function'], 1, 'Slide 106.', 'Step t waits for step t − 1.')
K.quiz('x', 'xLSTM introduces', ['convolutions', 'exponential gating and a matrix memory', 'beam search', 'BIO tags'], 1, 'Beck et al. 2024.', 'sLSTM and mLSTM blocks.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'c<sup>(t−1)</sup> = 0.8, c̃ = −0.5, f = 0.9, i = 0.2. New cell value.', '0.62', 'f c + i c̃.',
       ['0.9 × 0.8 = 0.72.', '0.2 × (−0.5) = −0.10.', eq('0.62')], check=0.62, tol=1e-9)
K.calc('e', 'Same cell with o = 0.7. Hidden state h, four decimals.', '0.3858', 'o tanh(c).',
       ['tanh(0.62) = 0.5511.', 'Times 0.7.', eq('0.3858')], check=0.3857896199767029, tol=5e-4)
K.calc('e', 'GRU: h<sub>t−1</sub> = 0.8, h̃ = −0.5, z = 0.3. New state.', '0.41', '(1 − z)h + z h̃.',
       ['0.7 × 0.8 = 0.56.', '0.3 × (−0.5) = −0.15.', eq('0.41')], check=0.41, tol=1e-9)
K.calc('m', 'A plain RNN multiplies the gradient by 0.6 each step. Size after 19 steps, in scientific notation (give the number).', '0.0000609', '0.6<sup>19</sup>.',
       ['ln 0.6 = −0.5108, times 19 = −9.706.', 'e<sup>−9.706</sup>.', eq('6.09 × 10<sup>−5</sup>')], check=0.6 ** 19, tol=2e-6)
K.calc('m', 'An LSTM forget gate stays at 0.95. Fraction kept after 19 steps, four decimals.', '0.3774', '0.95<sup>19</sup>.',
       ['ln 0.95 = −0.0513, times 19 = −0.9746.', 'e<sup>−0.9746</sup>.', eq('0.3774, about 6000 times more than the RNN')], check=0.95 ** 19, tol=5e-4)
K.calc('m', 'Gradient g = (3, 4) and clipping threshold τ = 1. First component of the clipped gradient.', '0.6', 'τ g ÷ ‖g‖.',
       ['‖g‖ = 5 > 1.', 'Scale by 1 ÷ 5.', eq('(0.6, 0.8), first component 0.6')], check=0.6, tol=1e-9)
K.calc('m', 'One LSTM layer, E = 100, H = 64, no biases. Parameters.', '41984', '4H(E + H).',
       ['E + H = 164.', '4 × 64 = 256.', eq('256 × 164 = 41,984')], check=41984, tol=1e-9)
K.calc('m', 'One GRU layer, E = 100, H = 64, no biases. Parameters.', '31488', '3H(E + H).',
       ['E + H = 164.', '3 × 64 = 192.', eq('192 × 164 = 31,488')], check=31488, tol=1e-9)
K.calc('h', 'BiLSTM: E = 60, H = 32 per direction, 4 tags, no biases. Total parameters.', '23808', 'Two directions plus output.',
       ['One direction: 4 × 32 × 92 = 11,776.', 'Two: 23,552. Output: 64 × 4 = 256.', eq('23,808')], check=23808, tol=1e-9)
K.calc('h', 'Same BiLSTM with biases: each direction adds 4H for the gates, the output adds 4. Total.', '24068', 'Add 2 × 128 + 4.',
       ['Gate biases: 2 × 4 × 32 = 256.', 'Output bias: 4.', eq('23,808 + 260 = 24,068')], check=24068, tol=1e-9)
K.calc('h', 'tanh RNN with ‖W<sub>h</sub>‖ = 0.8 and γ = 1. Upper bound on ‖∂h<sup>(20)</sup>/∂h<sup>(10)</sup>‖, four decimals.', '0.1074', '(γ‖W<sub>h</sub>‖)<sup>10</sup>.',
       ['10 steps back.', '0.8<sup>10</sup>.', eq('0.1074')], check=0.8 ** 10, tol=5e-4)
K.calc('x', 'How many steps until a constant factor 0.9 shrinks the gradient below 0.01? Whole number.', '44', 'Solve 0.9<sup>n</sup> < 0.01.',
       ['n > ln 0.01 ÷ ln 0.9.', '= −4.605 ÷ −0.1054 = 43.7.', eq('n = 44 steps')], check=44, tol=1e-9)

# ---------------------------------------------------------------- assignments
K.assign('lstmstep', 'e', 'One LSTM cell update from gate values',
         '<p>Write <code>lstm_update(c_prev, c_tilde, f, i, o)</code> that returns (c, h) with c = f·c_prev + i·c_tilde and h = o·tanh(c), both rounded to 4 decimals.</p>',
         '''
import math

def lstm_update(c_prev, c_tilde, f, i, o):
    pass
''', [('lstm_update(0.8, -0.5, 0.9, 0.2, 0.7)', (0.62, 0.3858)), ('lstm_update(0.5, 0.9, 1, 0, 1)', (0.5, 0.4621)), ('lstm_update(0.5, 0.9, 0, 1, 0)', (0.9, 0.0))],
         '''
import math

def lstm_update(c_prev, c_tilde, f, i, o):
    c = f * c_prev + i * c_tilde
    return (round(c, 4), round(o * math.tanh(c), 4))
''', 'Cell first, then the output.', '<p>The second test keeps the old cell, the third replaces it but hides it.</p>')
K.assign('grustep', 'm', 'A full GRU step',
         '<p>Write <code>gru_step(h, x, Wz, Uz, bz, Wr, Ur, br, Wh, Uh, bh)</code> for one number per vector. Use the four GRU equations of the lesson and return the new h rounded to 4 decimals.</p>',
         '''
import math

def gru_step(h, x, Wz, Uz, bz, Wr, Ur, br, Wh, Uh, bh):
    pass
''', [('gru_step(0.8, 1.0, 1.0, 0.5, -2.0, 0.5, 1.0, 0.0, 1.0, 0.8, 0.0)', 0.8374), ('gru_step(0.3, 0.0, 0, 0, -50, 0, 0, 0, 1, 1, 0)', 0.3), ('gru_step(0.0, 1.0, 0, 0, 50, 0, 0, 0, 1, 0, 0)', 0.7616)],
         '''
import math

def gru_step(h, x, Wz, Uz, bz, Wr, Ur, br, Wh, Uh, bh):
    sig = lambda v: 1 / (1 + math.exp(-v))
    z = sig(Wz * x + Uz * h + bz)
    r = sig(Wr * x + Ur * h + br)
    ht = math.tanh(Wh * x + Uh * (r * h) + bh)
    return round((1 - z) * h + z * ht, 4)
''', 'Gates from x and the old h, candidate from x and r ⊙ h.', '<p>The second test closes the update gate, so h stays 0.3. The third opens it fully, so h becomes tanh(1).</p>')
K.assign('rnnparams', 'h', 'Count recurrent layer parameters',
         '<p>Write <code>rec_params(kind, E, H, K, bi)</code> without biases. kind is "rnn", "gru" or "lstm" (1, 3 or 4 blocks of H(E + H)). bi doubles the recurrent part. K output labels read H numbers, or 2H when bi is True. K = 0 means no output layer.</p>',
         '''
def rec_params(kind, E, H, K, bi):
    pass
''', [('rec_params("lstm", 60, 32, 4, True)', 23808), ('rec_params("rnn", 300, 50, 11, False)', 18050), ('rec_params("gru", 100, 64, 0, False)', 31488)],
         '''
def rec_params(kind, E, H, K, bi):
    blocks = {"rnn": 1, "gru": 3, "lstm": 4}[kind]
    d = 2 if bi else 1
    return d * blocks * H * (E + H) + d * H * K
''', 'Blocks times H(E + H), times the number of directions, plus the output.', '<p>All three tests are lecture answers or lesson examples.</p>')

K.must('Vanishing and exploding', 'BPTT multiplies one Jacobian diag(σ′)W<sub>h</sub> per step: below 1 it vanishes, above 1 it explodes. Fixes: ReLU, initialisation, residual links, LSTM/GRU, clipping for exploding.')
K.must('LSTM equations', 'f, i, o = σ(Wh + Ux + b), c̃ = tanh(...), c = f ⊙ c<sub>old</sub> + i ⊙ c̃, h = o ⊙ tanh(c). Parameters 4H(E + H) + 4H.')
K.must('Why LSTM works', 'Additive cell path: ∂c<sup>(t)</sup>/∂c<sup>(t−1)</sup> ≈ f. With f near 1 information and gradients survive many steps.')
K.must('GRU', 'z and r gates, h̃ = tanh(Wx + U(r ⊙ h) + b), h = (1 − z) ⊙ h + z ⊙ h̃. Parameters 3H(E + H). Faster, fewer parameters.')
K.must('BiLSTM answer', 'E = 60, H = 32 each way, 4 tags: 2 × 4 × 32 × 92 + 64 × 4 = 23,808. RNNs cannot parallelise over time, so attention and transformers followed.')

T = K.topic(
    slug='lstm-gru', topic='nn-lstm-gru', step=(3, 'Language models and RNNs', 'nn-rnn', 'Predict the next word: n-gram models and their limits, fixed window and recurrent neural language models, sequence labelling with BIO tags, and why LSTM and GRU fix vanishing gradients.', 'College and masters'),
    title='Vanishing gradients, LSTM and GRU', short='LSTM and GRU', badge='3.3', minutes=50, added='2026-11-01',
    lead='Why a plain RNN forgets, how the gated LSTM cell and the simpler GRU keep information and gradients alive, the 23,808 parameter BiLSTM question and where xLSTM fits.',
    desc='Vanishing and exploding gradients through time, the Jacobian product and its bound, gradient clipping, the LSTM gates and cell equations, why the additive cell path keeps gradients alive, the GRU update and reset gates, LSTM against GRU parameter counts, the BiLSTM code-switching question and xLSTM.',
    summary='Vanishing gradients, LSTM and GRU equations, why gating works, parameter counts and xLSTM.',
    keywords=['vanishing gradient', 'exploding gradient', 'LSTM', 'GRU', 'forget gate', 'BiLSTM', 'gradient clipping', 'xLSTM'],
    recap='<p>A plain RNN multiplies its gradient by a similar factor at every step, so long range signals vanish or explode. The LSTM adds a memory cell with an additive, gated update, and the GRU blends old and new states with an update gate, so both can remember across many steps.</p>')
