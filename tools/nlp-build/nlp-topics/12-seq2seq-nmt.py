# NLP section, chapter 4.1: machine translation with sequence-to-sequence models. Source: FoVL lecture 3 slides 77 to
# 85, 109 to 111 (machine translation, NMT with an encoder RNN and a decoder RNN on "il a m' entarte" and "he hit me with a
# pie", test time argmax feeding, seq2seq for summarisation, dialogue, parsing and code, the conditional language model,
# training on a parallel corpus, the multi-layer encoder and decoder of Sutskever et al. 2014 and Luong et al. 2015, the
# bottleneck problem, the six low-resource NMT approaches and the Spanish to French parameter question).
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('condlm', r'''
# A conditional language model scores a translation word by word
import math
x = "il a m' entarte"
y = ["he", "hit", "me", "with", "a", "pie", "<END>"]
p = [0.62, 0.48, 0.81, 0.55, 0.70, 0.44, 0.90]      # P(y_t | y_<t, x) from the decoder
logp = sum(math.log(v) for v in p)
print("P(y | x) =", round(math.exp(logp), 5))
print("log P(y | x) =", round(logp, 4))
print("training loss J = -(1/T) sum log P =", round(-logp / len(p), 4))
''')

K.code('greedy', r'''
# Test time: feed the argmax word back in (greedy decoding) with a toy next word table
table = {
    "<START>": {"he": 0.6, "it": 0.3, "she": 0.1},
    "he": {"hit": 0.5, "struck": 0.4, "is": 0.1},
    "hit": {"me": 0.8, "him": 0.2},
    "me": {"with": 0.7, "<END>": 0.3},
    "with": {"a": 0.9, "the": 0.1},
    "a": {"pie": 0.6, "cake": 0.4},
    "pie": {"<END>": 1.0},
}
word, out, prob = "<START>", [], 1.0
while word != "<END>" and len(out) < 10:
    nxt = max(table[word], key=table[word].get)
    prob *= table[word][nxt]
    out.append(nxt)
    word = nxt
print(" ".join(out), " probability", round(prob, 4))
''')

K.code('count', r'''
# The Spanish to French question with one stated set of assumptions (no biases)
Vs, Vt, E, He, Hd = 35000, 45000, 256, 128, 256
parts = {
    "source embeddings Vs x E": Vs * E,
    "target embeddings Vt x E": Vt * E,
    "encoder RNN: E x He + He x He": E * He + He * He,
    "bridge from encoder to decoder state: He x Hd": He * Hd,
    "decoder RNN: E x Hd + Hd x Hd": E * Hd + Hd * Hd,
    "attention projection: Hd x He": Hd * He,
    "output on [s_t, context]: (Hd + He) x Vt": (Hd + He) * Vt,
}
for k, v in parts.items():
    print(k.ljust(48), format(v, ","))
print("total".ljust(48), format(sum(parts.values()), ","))
''')

K.lesson('mt', 'Neural machine translation', f'''
<p>Machine translation turns a sentence x in a source language into a sentence y in a target language, for example x: "I like deep learning" and y: "我喜欢深度学习". Neural machine translation (NMT) does it with a single neural network trained end to end. The architecture is called sequence-to-sequence (seq2seq) and uses two RNNs.</p>
{table(['Part', 'What it does'], [['Encoder RNN', 'reads the source sentence "il a m’ entarté" and produces an encoding of it'], ['Encoding', 'the last encoder state, used as the initial hidden state of the decoder'], ['Decoder RNN', 'a language model that writes the target "he hit me with a pie", conditioned on the encoding'], ['At test time', 'each decoder output (the argmax word) is fed back in as the next input until &lt;END&gt;']])}
{viz('seq2seq')}
{code('greedy')}
{fxs(fx('Encoder', 'h<sub>i</sub><sup>enc</sup> = RNN<sub>enc</sub>(h<sub>i−1</sub><sup>enc</sup>, x<sub>i</sub>), &nbsp; i = 1 ... n', 'Reads the source word by word.'),
     fx('Decoder', 's<sub>t</sub> = RNN<sub>dec</sub>(s<sub>t−1</sub>, y<sub>t−1</sub>), &nbsp; s<sub>0</sub> = h<sub>n</sub><sup>enc</sup>', 'Starts from the encoding and reads its own previous output.', key=True),
     fx('Output', 'P(y<sub>t</sub> | y<sub>&lt;t</sub>, x) = softmax(W<sub>o</sub> s<sub>t</sub>)', 'A distribution over the target vocabulary.'))}
{scene('translating a hotel review', '<p>A travel site shows a French review to an English reader. The encoder reads "le petit déjeuner était excellent", the decoder starts from its final state and writes "the", then "breakfast", then "was", then "excellent", then &lt;END&gt;. Every word choice depends both on the French sentence and on the English words already written.</p>')}
''', kw=['machine translation', 'NMT', 'seq2seq', 'encoder', 'decoder'])

K.lesson('conditional', 'A conditional language model', f'''
<p>The seq2seq model is a conditional language model. It is a language model because the decoder predicts the next word of the target y. It is conditional because every prediction also depends on the source x. This extra conditioning is the key difference from the RNN language model of chapter 3.1.</p>
{fxs(fx('NMT probability', 'P(y | x) = ∏<sub>t=1</sub><sup>T</sup> P(y<sub>t</sub> | y<sub>1</sub>, ..., y<sub>t−1</sub>, x)', 'Each factor conditions on the target words so far and on the entire source sentence.', key=True),
     fx('Training loss', 'J = ' + frac('1', 'T') + ' ∑<sub>t=1</sub><sup>T</sup> −log P(y<sub>t</sub><sup>gold</sup> | y<sub>&lt;t</sub><sup>gold</sup>, x)', 'Teacher forcing: the decoder reads the gold previous word.', key=True))}
{code('condlm')}
{steps('Score a three word translation', [
    'The decoder gives the gold words probabilities 0.5, 0.4 and 0.9.',
    eq('P(y | x) = 0.5 × 0.4 × 0.9 = 0.18'),
    'Losses: −ln 0.5 = 0.6931, −ln 0.4 = 0.9163, −ln 0.9 = 0.1054.',
    eq('J = (0.6931 + 0.9163 + 0.1054) ÷ 3 = 0.5716')])}
<p>How to train an NMT system: get a big parallel corpus, sentence pairs in both languages, and backpropagate the loss through decoder and encoder together. Real systems stack several RNN layers: the hidden states of layer i are the inputs of layer i + 1 (Sutskever et al. 2014 used 4 layers, Luong et al. 2015 stacked LSTMs as well).</p>
{note('In the exam, name both parts: "language model" because it predicts the next target word, "conditional" because it conditions on the whole source x.', 'exam')}
''', kw=['conditional language model', 'P(y | x)', 'parallel corpus', 'teacher forcing', 'stacked RNNs'])

K.lesson('uses', 'Seq2seq is versatile', f'''
<p>The general idea is an encoder-decoder model. One neural network takes the input and builds a neural representation. Another network produces the output from that representation. When both input and output are sequences, it is a seq2seq model.</p>
{table(['Task', 'Input sequence', 'Output sequence'], [['Summarisation', 'long text', 'short text'], ['Dialogue', 'previous utterances', 'next utterance'], ['Parsing', 'input text', 'the parse written as a sequence'], ['Code generation', 'natural language', 'Python code'], ['Speech recognition', 'audio frames', 'words'], ['Transliteration', 'Hindi in Devanagari letters', 'the same words in Latin letters']])}
{steps('Parsing as a sequence', [
    'Input: "John has a dog".',
    'A tree can be written with brackets: (S (NP John) (VP has (NP a dog))).',
    'Treat every bracket and label as a token.',
    eq('The decoder writes the tree token by token, so a seq2seq model can parse')])}
{note('Encoder and decoder do not need to be RNNs. The encoder can be a CNN over an image (image captioning) and both can be transformers.', 'tip')}
''', kw=['encoder-decoder', 'summarisation', 'dialogue', 'parsing', 'code generation'])

K.lesson('bottleneck', 'The bottleneck problem', f'''
<p>Without attention the decoder sees the source only through one vector, the last encoder state. A long sentence must be squeezed into that one vector and then reconstructed into another long sentence, so information is lost. This is the bottleneck problem, and it is why translation quality of plain seq2seq drops for long sentences.</p>
{viz('seq2seq', attn=False, src='the protests escalated over the weekend after the police arrived in the old city centre', tgt='die Proteste waren am Wochenende eskaliert')}
{steps('How tight is the bottleneck?', [
    'A 50 word sentence with 256-dimensional embeddings holds 50 × 256 = 12,800 input numbers.',
    'The encoder must summarise them in a hidden state of 256 numbers.',
    eq('256 ÷ 12,800 = 2 percent of the input size for the whole sentence'),
    'The same 256 numbers must also hold the first word for as long as the decoder needs it.'])}
<p>Early fixes reversed the source sentence (Sutskever et al. 2014), which brings the first source words close to the first target words. The real fix is attention (chapter 4.2): let every decoder step look at all encoder states directly.</p>
{deep('quality against sentence length', '<p>Cho et al. (2014) and Bahdanau et al. (2015) plotted BLEU against sentence length. The plain encoder-decoder was competitive up to about 20 words and then fell steadily, while the attention model stayed nearly flat up to 50 to 60 words. That plot is the clearest evidence for the bottleneck.</p>')}
''', kw=['bottleneck', 'information loss', 'long sentences', 'reversing the source'])

K.lesson('params', 'Low-resource NMT and the parameter question', f'''
<p>NMT needs a big parallel corpus, which most of the world’s 7,000 languages do not have. The lecture lists six ways to cope.</p>
{table(['Approach', 'Idea'], [['Transfer learning', 'train on a high-resource pair first, then fine-tune on the low-resource data'], ['Multilingual NMT', 'one model for many languages, low-resource languages share representations'], ['Back translation', 'translate monolingual target text back into the source to make synthetic parallel data'], ['Data augmentation', 'paraphrasing, noise injection, word replacement'], ['Pivot translation', 'A to English to B when direct A to B data is scarce'], ['Unsupervised NMT', 'only monolingual data, no parallel corpus at all']])}
<p>The lecture problem: a seq2seq RNN with attention from Spanish to French. Source vocabulary 35,000, target vocabulary 45,000, both with 256-dimensional embeddings. Encoder hidden size 128, decoder hidden size 256. Ignore biases. The answer depends on design choices the question does not fix, so write your assumptions. One standard set gives:</p>
{table(['Component', 'Shape', 'Count'], [['Source embeddings', '35,000 × 256', '8,960,000'], ['Target embeddings', '45,000 × 256', '11,520,000'], ['Encoder RNN', '256 × 128 + 128 × 128', '49,152'], ['Bridge, encoder to decoder state', '128 × 256', '32,768'], ['Decoder RNN', '256 × 256 + 256 × 256', '131,072'], ['Attention projection (sizes differ)', '256 × 128', '32,768'], ['Output on [s<sub>t</sub>, c<sub>t</sub>]', '384 × 45,000', '17,280,000'], ['Total', '', '38,005,760']])}
{viz('paramcount', model='seq2seq', V=35000, V2=45000, E=256, H=128, H2=256)}
{code('count')}
{note('Most of the parameters sit in the embeddings and the output layer, about 37.8 million of 38 million. The RNNs themselves are tiny. Variants change the total: concatenating the context to the decoder input adds 128 × 256 = 32,768, and a decoder with the same size as the encoder needs no bridge or projection.', 'exam')}
{ladder(
    '<p>A translation model reads the whole sentence in one language, then writes it word by word in the other, each time looking at what it already wrote.</p>',
    '<p>Seq2seq models P(y | x) as a product of next word probabilities. It is trained on parallel sentences with teacher forcing and the average cross-entropy, and decodes by feeding outputs back in.</p>',
    '<p>The single context vector is a bottleneck. Parameter counts are dominated by |V| × d matrices, which is why subword vocabularies (BPE) and tying input and output embeddings matter in practice.</p>',
    '<p>Back translation (Sennrich et al. 2016) and multilingual models with a target language token (Johnson et al. 2017, zero-shot translation) are standard. Massively multilingual models such as NLLB-200 cover 200 languages with one network.</p>')}
''', kw=['low-resource NMT', 'back translation', 'pivot', 'parameter count', '38,005,760'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In seq2seq NMT the part that reads the source sentence is the', ['decoder', 'encoder', 'softmax', 'beam'], 1, 'Encoder RNN.', 'It produces the encoding.')
K.quiz('e', 'NMT is trained on', ['monolingual text only', 'a parallel corpus', 'images', 'a dictionary only'], 1, 'Slide 101.', 'Sentence pairs in both languages.')
K.quiz('e', 'Which is a seq2seq task?', ['spam detection', 'summarisation', 'POS counting', 'word frequency'], 1, 'Long text to short text.', 'Input and output are both sequences.')
K.quiz('e', 'At test time the decoder input at step t is', ['the gold word', 'its own previous output', 'a random word', 'the source word t'], 1, 'Slide 78 note.', 'The argmax output is fed back.')
K.quiz('m', 'Seq2seq is a conditional language model because', ['it uses conditions in code', 'its next word predictions also depend on the source x', 'it is trained conditionally', 'it uses if statements'], 1, 'Slide 101.', 'P(y<sub>t</sub> | y<sub>&lt;t</sub>, x).')
K.quiz('m', 'The bottleneck problem is that', ['the vocabulary is too big', 'the whole source must pass through one vector', 'training is too slow', 'the decoder has no softmax'], 1, 'Slide 85.', 'One vector for a whole sentence loses information.')
K.quiz('m', 'Back translation creates', ['a bigger vocabulary', 'synthetic parallel data from monolingual target text', 'a pivot language', 'more layers'], 1, 'Slide 109.', 'Translate target text into the source.')
K.quiz('m', 'Pivot translation from Hindi to Tamil via English is used when', ['Hindi and Tamil are the same', 'direct Hindi to Tamil data is scarce', 'English is unknown', 'the model is too large'], 1, 'A to English to B.', 'Two well resourced steps instead of one poor one.')
K.quiz('m', 'Gold word probabilities 0.5, 0.4, 0.9. P(y | x)?', ['0.18', '0.36', '0.45', '1.8'], 0, 'Multiply.', '0.5 × 0.4 × 0.9.')
K.quiz('h', 'In the Spanish to French question, the largest single matrix is', ['the encoder RNN', 'the target embeddings', 'the output layer (384 × 45,000)', 'the attention projection'], 2, '17.28 million.', 'Output layers over big vocabularies dominate.')
K.quiz('h', 'Why might the decoder need a projection for dot-product attention in that question?', ['to add bias', 'encoder states have 128 numbers and decoder states 256, so a dot product needs equal sizes', 'to reduce the vocabulary', 'it never does'], 1, 'Sizes differ.', 'A 256 × 128 matrix makes s<sup>T</sup>W h defined.')
K.quiz('h', 'Unsupervised NMT uses', ['only parallel data', 'only monolingual data', 'only a dictionary', 'labelled entities'], 1, 'Slide 109.', 'No parallel corpus.')
K.quiz('x', 'Reversing the source sentence (Sutskever 2014) helps because', ['it is shorter', 'the first source words end up close to the first target words', 'it removes stop words', 'it doubles the data'], 1, 'Short paths at the start.', 'Early target words get short gradient paths to their sources.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Gold word probabilities 0.5, 0.4, 0.9. Compute P(y | x).', '0.18', 'Product.',
       ['0.5 × 0.4 = 0.2.', '0.2 × 0.9.', eq('0.18')], check=0.18, tol=1e-9)
K.calc('e', 'Same probabilities. Average cross-entropy loss, four decimals.', '0.5716', 'Mean of −ln p.',
       ['0.6931 + 0.9163 + 0.1054 = 1.7148.', 'Divide by 3.', eq('0.5716')], check=1.7147984280919266 / 3, tol=5e-4)
K.calc('e', 'Source embeddings: vocabulary 35,000, dimension 256. Number of parameters.', '8960000', 'V × E.',
       ['35,000 × 256.', '= 35 × 256 thousand.', eq('8,960,000')], check=8960000, tol=1e-9)
K.calc('m', 'Output layer on [s<sub>t</sub>, c<sub>t</sub>] with s of size 256, c of size 128, target vocabulary 45,000. Parameters.', '17280000', '(256 + 128) × 45,000.',
       ['Input size 384.', 'Times 45,000.', eq('17,280,000')], check=17280000, tol=1e-9)
K.calc('m', 'Encoder RNN with E = 256, H = 128, no biases. Parameters.', '49152', 'E·H + H·H.',
       ['256 × 128 = 32,768.', '128 × 128 = 16,384.', eq('49,152')], check=49152, tol=1e-9)
K.calc('m', 'Decoder RNN with E = 256, H = 256, no biases. Parameters.', '131072', 'E·H + H·H.',
       ['256 × 256 = 65,536.', 'Twice.', eq('131,072')], check=131072, tol=1e-9)
K.calc('h', 'Full Spanish to French model with the lesson assumptions. Total parameters.', '38005760', 'Add the seven parts.',
       ['Embeddings 8,960,000 + 11,520,000 = 20,480,000.', 'RNNs, bridge and attention: 49,152 + 32,768 + 131,072 + 32,768 = 245,760. Output 17,280,000.', eq('38,005,760')], check=38005760, tol=1e-9)
K.calc('h', 'Same model. What fraction of the parameters is in the embeddings and the output layer? Three decimals.', '0.994', '(20,480,000 + 17,280,000) ÷ 38,005,760.',
       ['Numerator 37,760,000.', 'Divide by 38,005,760.', eq('0.994')], check=37760000 / 38005760, tol=5e-4)
K.calc('m', 'A 50 word source with 256-dimensional embeddings goes into a 256-number encoder state. What percent of the input size is the state?', '2', '256 ÷ (50 × 256).',
       ['Input numbers 12,800.', '256 ÷ 12,800 = 0.02.', eq('2 percent')], check=2, tol=1e-9)
K.calc('m', '100,000 real sentence pairs plus 900,000 back translated pairs. Fraction of synthetic data.', '0.9', 'synthetic ÷ total.',
       ['Total 1,000,000.', '900,000 synthetic.', eq('0.9')], check=0.9, tol=1e-9)
K.calc('h', 'Pivot translation: A to English is right 80 percent of the time and English to B 85 percent, independently. Chance both steps are right.', '0.68', 'Multiply.',
       ['0.8 × 0.85.', 'Errors compound across the two steps.', eq('0.68')], check=0.68, tol=1e-9)
K.calc('x', 'Greedy decoding on the toy table gives "he hit me with a pie &lt;END&gt;" with step probabilities 0.6, 0.5, 0.8, 0.7, 0.9, 0.6, 1.0. Probability of the output, four decimals.', '0.0907', 'Product.',
       ['0.6 × 0.5 = 0.3, × 0.8 = 0.24.', '× 0.7 = 0.168, × 0.9 = 0.1512.', eq('× 0.6 × 1.0 = 0.0907')], check=0.6 * 0.5 * 0.8 * 0.7 * 0.9 * 0.6, tol=5e-5)

# ---------------------------------------------------------------- assignments
K.assign('logp', 'e', 'Score a translation',
         '<p>Write <code>score(probs)</code> that returns (P, J): the product of the gold word probabilities and the average −ln p, both rounded to 4 decimals.</p>',
         '''
import math

def score(probs):
    pass
''', [('score([0.5, 0.4, 0.9])', (0.18, 0.5716)), ('score([1.0])', (1.0, 0.0)), ('score([0.5, 0.5])', (0.25, 0.6931))],
         '''
import math

def score(probs):
    P = 1.0
    for p in probs:
        P *= p
    J = sum(-math.log(p) for p in probs) / len(probs)
    return (round(P, 4), round(J, 4))
''', 'Multiply for P, average the negative logs for J.', '<p>J is −ln P divided by the length.</p>')
K.assign('greedy', 'm', 'Greedy decoding from a table',
         '<p>Write <code>greedy(table, start, end, max_len)</code>. table maps a word to a dict of next words and probabilities. Starting from start, repeatedly pick the most likely next word until end or max_len words. Return the list of words produced (including end if reached).</p>',
         '''
def greedy(table, start, end, max_len):
    pass
''', [('greedy({"S": {"a": 0.6, "b": 0.4}, "a": {"E": 1.0}, "b": {"E": 1.0}}, "S", "E", 5)', ['a', 'E']),
      ('greedy({"S": {"x": 1.0}, "x": {"x": 0.9, "E": 0.1}}, "S", "E", 3)', ['x', 'x', 'x']),
      ('greedy({"S": {"E": 1.0}}, "S", "E", 5)', ['E'])],
         '''
def greedy(table, start, end, max_len):
    out, w = [], start
    while len(out) < max_len:
        w = max(table[w], key=table[w].get)
        out.append(w)
        if w == end:
            break
    return out
''', 'Feed each chosen word back in.', '<p>The second test never reaches E, so max_len stops it, a real risk of greedy decoding.</p>')
K.assign('s2sparams', 'h', 'Seq2seq parameter count',
         '<p>Write <code>s2s_params(Vs, Vt, E, He, Hd)</code> with the lesson assumptions: both embedding tables, encoder and decoder RNNs, a bridge He × Hd and an attention projection Hd × He only when He differs from Hd, and an output layer on [s, c] of size Hd + He. No biases.</p>',
         '''
def s2s_params(Vs, Vt, E, He, Hd):
    pass
''', [('s2s_params(35000, 45000, 256, 128, 256)', 38005760), ('s2s_params(10, 10, 4, 3, 3)', 10 * 4 * 2 + 4 * 3 + 9 + 4 * 3 + 9 + 6 * 10), ('s2s_params(100, 200, 8, 4, 4)', 100 * 8 + 200 * 8 + 8 * 4 + 16 + 8 * 4 + 16 + 8 * 200)],
         '''
def s2s_params(Vs, Vt, E, He, Hd):
    total = Vs * E + Vt * E
    total += E * He + He * He
    total += E * Hd + Hd * Hd
    if He != Hd:
        total += He * Hd + Hd * He
    total += (Hd + He) * Vt
    return total
''', 'List every matrix with its shape, then add.', '<p>With equal sizes the bridge and projection are not needed.</p>')

K.must('Seq2seq', 'Encoder RNN reads x, its last state starts the decoder RNN, which writes y one word at a time and feeds its outputs back in at test time.')
K.must('Conditional LM', 'P(y | x) = ∏ P(y<sub>t</sub> | y<sub>&lt;t</sub>, x). Language model: predicts the next target word. Conditional: on the whole source. Trained on a parallel corpus.')
K.must('Uses', 'Translation, summarisation, dialogue, parsing, code generation: any task whose input and output are sequences.')
K.must('Bottleneck', 'The whole source passes through one vector, so long sentences lose information. Attention fixes it.')
K.must('Low-resource and parameters', 'Transfer, multilingual, back translation, augmentation, pivot, unsupervised. Spanish to French count with stated assumptions: 38,005,760, nearly all in embeddings and output.')

T = K.topic(
    slug='seq2seq-nmt', topic='nn-seq2seq', step=(4, 'Translation, attention and decoding', 'nn-seq2seq', 'Translate and generate text: the encoder-decoder model as a conditional language model, the bottleneck, attention with its worked problem, and greedy, beam and sampling decoders.', 'Masters'),
    title='Sequence-to-sequence models and machine translation', short='Seq2seq and NMT', badge='4.1', minutes=45, added='2026-11-01',
    lead='Translate with two RNNs: an encoder that reads the source and a decoder that writes the target, as a conditional language model, with the bottleneck, low-resource tricks and the parameter question.',
    desc='Neural machine translation with an encoder RNN and a decoder RNN, test time feeding of argmax outputs, the conditional language model P(y | x), training on a parallel corpus, seq2seq for summarisation, dialogue, parsing and code, the bottleneck problem, six low-resource NMT approaches and the Spanish to French parameter count with its assumptions.',
    summary='Encoder and decoder, conditional LM, training, uses, the bottleneck, low-resource NMT and parameter counting.',
    keywords=['seq2seq', 'NMT', 'encoder-decoder', 'conditional language model', 'bottleneck', 'back translation', 'parameter count'],
    recap='<p>Seq2seq NMT encodes the source with one RNN and decodes the target with another, modelling P(y | x) word by word. It is trained on parallel text, struggles with the single vector bottleneck, and can be helped in low-resource settings by transfer, multilingual training and back translation.</p>')
