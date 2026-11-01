# NLP section, chapter 3.2: RNNs for sequence labelling, named entity recognition with BIO tags, sentence
# classification and bidirectional RNNs. Source: FoVL lecture 3 slides 47 to 69 (RNN uses, POS tagging, the four
# common entity types PER, LOC, ORG and GPE, why NER is useful and hard, the Jane Villanueva sentence in BIO, 2n + 1
# tags, the two parameter questions with 300-dimensional embeddings, hidden size 50, 50 POS tags or 5 entity types,
# sentence classification and the bidirectional RNN for sentiment) and Jurafsky and Martin, SLP3 chapter 8.
from cvkit import Kit, fx, fxs, frac, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('bio', r'''
# Turn entity spans into one BIO tag per token
tokens = "Jane Villanueva of United , a unit of United Airlines Holding , said".split()
spans = [(0, 2, "PER"), (3, 4, "ORG"), (8, 11, "ORG")]     # (start, end exclusive, type)
tags = ["O"] * len(tokens)
for s, e, t in spans:
    tags[s] = "B-" + t
    for i in range(s + 1, e):
        tags[i] = "I-" + t
for w, t in zip(tokens, tags):
    print(w.ljust(11), t)
n = 4
print("tags needed for", n, "types:", 2 * n + 1)
''')

K.code('spanf1', r'''
# Span level precision, recall and F1 for NER
gold = {(0, 2, "PER"), (3, 4, "ORG"), (8, 11, "ORG"), (17, 18, "LOC")}
pred = {(0, 2, "PER"), (3, 4, "ORG"), (8, 10, "ORG"), (17, 18, "LOC"), (12, 13, "PER")}
tp = len(gold & pred)
P, R = tp / len(pred), tp / len(gold)
print("correct spans:", tp, " P =", P, " R =", R, " F1 =", round(2 * P * R / (P + R), 4))
''')

K.code('birnn', r'''
# A bidirectional RNN with one number per state: read left to right and right to left, then join
import math
xs = [1.0, 0.0, -1.0, 2.0]
def run(seq, w=0.5, u=1.0):
    h, out = 0.0, []
    for x in seq:
        h = math.tanh(w * h + u * x)
        out.append(round(h, 3))
    return out
fwd = run(xs)
bwd = run(xs[::-1])[::-1]          # run on the reversed input, then flip back
for t in range(len(xs)):
    print("t =", t + 1, " forward", fwd[t], " backward", bwd[t], " joined", [fwd[t], bwd[t]])
''')

K.lesson('labelling', 'Sequence labelling with an RNN', f'''
<p>RNNs have three main uses: generating text, labelling every word of a sequence, and classifying a whole sentence. In sequence labelling the RNN outputs one label per word. Part of speech tagging is the classic example: "Janet will back the bill" becomes NOUN AUX VERB DET NOUN.</p>
{fxs(fx('Tag distribution at step t', 'ŷ<sup>(t)</sup> = softmax(V h<sup>(t)</sup>) ∈ ℝ<sup>K</sup>', 'K is the number of tags. h<sup>(t)</sup> is the RNN state after reading word t.', key=True),
     fx('Training loss', 'J = −' + frac('1', 'T') + ' ∑<sub>t</sub> log ŷ<sup>(t)</sup><sub>y<sub>t</sub></sub>', 'Cross-entropy with the gold tag at every position.'),
     fx('Prediction', 'tag<sub>t</sub> = argmax<sub>k</sub> ŷ<sub>k</sub><sup>(t)</sup>', 'One independent choice per word.'))}
{table(['Use of an RNN', 'Output', 'Example'], [['Generation', 'next word at every step', 'language model'], ['Sequence labelling', 'one label per word', 'POS tagging, NER'], ['Classification', 'one label per sentence', 'sentiment, spam']])}
{steps('Tagging "Janet will back the bill"', [
    'Each word goes in as an embedding. The RNN state h<sup>(t)</sup> carries what came before.',
    '"back" can be a noun, a verb or an adverb. After "Janet will" the state favours a verb.',
    'The softmax over 17 universal POS tags gives VERB the highest probability.',
    eq('Output: NOUN AUX VERB DET NOUN, one tag per word, no segmentation needed')])}
{note('A left to right RNN tagger only sees the past when it tags word t. "back" in "the back of the bill" needs the words after it, which is what bidirectional RNNs add.', 'tip')}
''', kw=['sequence labelling', 'POS tagging', 'RNN tagger', 'softmax per token'])

K.lesson('ner', 'Named entity recognition', f'''
<p>A named entity is anything that can be referred to with a proper name. NER finds the spans of text that are proper names and tags their type. The term also covers things that are not entities, such as dates, times and prices.</p>
{table(['Tag', 'Type', 'Example'], [['PER', 'person', 'Marie Curie'], ['LOC', 'location', 'New York City'], ['ORG', 'organisation', 'Stanford University'], ['GPE', 'geo-political entity', 'Boulder, Colorado']])}
<p>NER is useful for sentiment analysis (how do customers feel about a company or a person), question answering (answer questions about an entity) and information extraction (pull facts about entities out of text).</p>
{table(['Why NER is hard', 'Example'], [['Segmentation: POS gives one tag per word, NER must find where each entity starts and ends', '"United Airlines Holding" is one entity of three words'], ['Type ambiguity: the same string can be different types', 'Washington: a person, a city (GPE), a state, or the government (ORG)']])}
{scene('screening news for a trading desk', '<p>A bank reads thousands of news stories an hour. NER finds every company (ORG) and country (GPE) mentioned, so a story about "Apple" is routed to the analyst for Apple Inc. and not to the fruit market desk. Getting the span right matters: "Bank of America" must not be split into "Bank" and "America".</p>')}
''', kw=['NER', 'named entities', 'PER LOC ORG GPE', 'segmentation', 'type ambiguity'])

K.lesson('bio', 'BIO tagging: spans become one tag per word', f'''
<p>How can a span problem become a sequence problem with one label per word, like POS tagging? BIO tagging marks the first word of a span with B, the other words inside it with I, and every word outside any span with O. The type is attached to B and I.</p>
<p>The slide sentence: [PER Jane Villanueva] of [ORG United] , a unit of [ORG United Airlines Holding] , said the fare applies to the [LOC Chicago] route.</p>
{table(['Word', 'Jane', 'Villanueva', 'of', 'United', ',', 'United', 'Airlines', 'Holding', 'Chicago'], [['BIO', 'B-PER', 'I-PER', 'O', 'B-ORG', 'O', 'B-ORG', 'I-ORG', 'I-ORG', 'B-LOC']])}
{fxs(fx('Number of BIO tags', '2n + 1', 'n B tags, n I tags and 1 O tag, where n is the number of entity types.', key=True),
     fx('Other schemes', 'IO: n + 1, &nbsp; BIOES: 4n + 1', 'BIOES adds E for the last word and S for a single word span.'))}
{viz('bio')}
{code('bio')}
<p>NER is scored per entity span, not per word. A predicted span counts only if both its boundaries and its type match the gold span exactly.</p>
{fxs(fx('Span precision and recall', 'P = ' + frac('correct spans', 'predicted spans') + ', &nbsp; R = ' + frac('correct spans', 'gold spans'), 'F1 = 2PR ÷ (P + R).', key=True))}
{code('spanf1')}
{steps('Span F1 by hand', [
    'Gold has 4 spans. The model predicts 5 spans.',
    '"United Airlines" is predicted instead of "United Airlines Holding": a boundary error, so it is wrong. 3 predicted spans match exactly.',
    'P = 3 ÷ 5 = 0.6, R = 3 ÷ 4 = 0.75.',
    eq('F1 = 2 × 0.6 × 0.75 ÷ 1.35 = 0.667')])}
{note('Why B is needed: with IO tags "[ORG Google] [ORG Microsoft]" becomes I-ORG I-ORG and looks like one entity. B marks the start of the second one.', 'warn')}
''', kw=['BIO', '2n + 1', 'BIOES', 'span F1', 'entity boundaries'])

K.lesson('params', 'The two parameter questions', f'''
<p>The lecture asks for parameter counts of an RNN tagger. The input is a 300-dimensional embedding, the hidden vector has 50 numbers, and biases are excluded. Three matrices matter: embedding to hidden, hidden to hidden, hidden to output.</p>
{fxs(fx('RNN tagger parameters (no biases)', 'E·H + H·H + H·K', 'E embedding size, H hidden size, K number of output labels. The embedding table itself is not counted here.', key=True),
     fx('BiRNN tagger', '2(E·H + H·H) + 2H·K', 'Two directions, and the output layer reads the joined 2H vector.'))}
{steps('POS tagging with 50 tags', [
    'Embedding to hidden: 300 × 50 = 15,000.',
    'Hidden to hidden: 50 × 50 = 2,500.',
    'Hidden to output: 50 × 50 = 2,500.',
    eq('Total = 20,000')])}
{steps('NER with 5 entity types and BIO', [
    'BIO creates a B tag and an I tag for each type plus O: 2 × 5 + 1 = 11 labels.',
    'Embedding to hidden 15,000 and hidden to hidden 2,500 are unchanged.',
    'Hidden to output: 50 × 11 = 550.',
    eq('Total = 15,000 + 2,500 + 550 = 18,050')])}
{viz('paramcount', model='tagger', E=300, H=50, K=11)}
{note('State what you count. If the question says "excluding bias terms" and does not mention the embedding table, count only the RNN and output weights, as the lecture answer does.', 'exam')}
''', kw=['parameter count', '20,000', '18,050', 'POS tagger', 'NER tagger'])

K.lesson('birnn', 'Sentence classification and bidirectional RNNs', f'''
<p>To classify a whole sentence, run the RNN over it and turn the hidden states into one sentence vector. The simplest choice is the final state h<sup>(T)</sup>. Often better is the element-wise mean or max of all the hidden states. A softmax on that vector gives the class.</p>
<p>Sentiment shows why one direction is not enough. In "the movie was terribly exciting", the word "terribly" looks negative from the left, but "exciting" on its right makes it positive. A bidirectional RNN runs one RNN left to right and another right to left and joins their states.</p>
{fxs(fx('Forward RNN', 'h→<sup>(t)</sup> = RNN<sub>FW</sub>(h→<sup>(t−1)</sup>, x<sup>(t)</sup>)', 'Reads from the start.'),
     fx('Backward RNN', 'h←<sup>(t)</sup> = RNN<sub>BW</sub>(h←<sup>(t+1)</sup>, x<sup>(t)</sup>)', 'Reads from the end, with its own weights.'),
     fx('Joined state', 'h<sup>(t)</sup> = [h→<sup>(t)</sup>, h←<sup>(t)</sup>] ∈ ℝ<sup>2H</sup>', 'Each word now sees the whole sentence.', key=True),
     fx('Sentence vector', 's = ' + frac('1', 'T') + ' ∑<sub>t</sub> h<sup>(t)</sup> &nbsp; or &nbsp; s = h<sup>(T)</sup>', 'Then ŷ = softmax(W s).'))}
{code('birnn')}
{table(['', 'Unidirectional', 'Bidirectional'], [['Sees at word t', 'words 1 to t', 'the whole sentence'], ['Good for', 'language modelling and generation', 'tagging, NER, classification, encoders'], ['Not usable for', '', 'language modelling, because the future is not known yet']])}
{steps('BiRNN tagger parameters', [
    'E = 300, H = 50 in each direction, 11 BIO labels, no biases.',
    'Each direction: 300 × 50 + 50 × 50 = 17,500, so two directions: 35,000.',
    'Output layer reads 2H = 100 numbers: 100 × 11 = 1,100.',
    eq('Total = 36,100')])}
{ladder(
    '<p>An RNN can give a label to every word, for example "this word is the name of a person". Reading the sentence from both ends helps, because the meaning of a word often depends on what comes after it.</p>',
    '<p>NER becomes per word classification with BIO tags (2n + 1 labels). A BiRNN joins forward and backward states for each word, and a sentence vector from the final or pooled states feeds a classifier.</p>',
    '<p>Choosing each tag independently can produce invalid sequences such as O I-PER. A CRF layer on top scores whole tag sequences with transition weights and decodes the best one with the Viterbi algorithm, as in the BiLSTM-CRF of Lample et al. (2016).</p>',
    '<p>Modern NER fine-tunes a pre-trained transformer such as BERT, with subword tokens aligned to word level BIO tags. Nested entities ("[ORG Bank of [GPE America]]") do not fit flat BIO and need span based or hypergraph models.</p>')}
''', kw=['sentence classification', 'bidirectional RNN', 'BiRNN', 'pooling', 'sentiment'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'With n entity types, BIO tagging needs', ['n', 'n + 1', '2n', '2n + 1'], 3, 'B and I per type, plus O.', '2n + 1.')
K.quiz('e', 'In BIO, the first word of an entity gets', ['O', 'B', 'I', 'E'], 1, 'Begin.', 'B marks the start of a span.')
K.quiz('e', 'GPE stands for', ['general purpose entity', 'geo-political entity', 'global person entity', 'grouped phrase entity'], 1, 'Boulder, Colorado.', 'Countries, states and cities with governments.')
K.quiz('e', 'POS tagging gives', ['one label per sentence', 'one label per word', 'a translation', 'a parse tree'], 1, 'Sequence labelling.', 'Every word gets a part of speech.')
K.quiz('m', 'What makes NER harder than POS tagging?', ['more words', 'segmentation: finding where entities start and end', 'no training data', 'it needs a GPU'], 1, 'Slide 58.', 'And type ambiguity.')
K.quiz('m', '5 entity types with BIO. Output labels?', ['5', '10', '11', '16'], 2, '2 × 5 + 1.', '11.')
K.quiz('m', 'E = 300, H = 50, 50 POS tags, no biases. RNN tagger parameters?', ['17,500', '18,050', '20,000', '22,500'], 2, '15,000 + 2,500 + 2,500.', '20,000.')
K.quiz('m', 'A bidirectional RNN cannot be used directly for', ['NER', 'sentiment', 'language modelling', 'POS tagging'], 2, 'The future is unknown.', 'A language model may only look at the words so far.')
K.quiz('m', 'The joined BiRNN state at word t has size', ['H', '2H', 'H²', 'T × H'], 1, '[h→, h←].', 'Two vectors of size H.')
K.quiz('h', 'Gold 4 spans, predicted 5 spans, 3 exactly right. F1?', ['0.600', '0.667', '0.750', '0.857'], 1, 'P = 0.6, R = 0.75.', '2PR ÷ (P + R) = 0.667.')
K.quiz('h', 'Same NER question with 5 types and BIO. Parameters?', ['18,050', '20,000', '17,500', '15,550'], 0, 'Only the output layer changes.', '15,000 + 2,500 + 550.')
K.quiz('h', 'Why is B needed in BIO?', ['to mark verbs', 'to separate two adjacent entities of the same type', 'to speed up training', 'to mark the sentence start'], 1, '[ORG Google] [ORG Microsoft].', 'IO would merge them.')
K.quiz('x', 'A CRF layer on top of a BiLSTM tagger', ['replaces the embeddings', 'scores whole tag sequences with transitions, ruling out O I-PER', 'adds attention', 'doubles the hidden size'], 1, 'Lample et al. 2016.', 'Decoded with Viterbi.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Number of BIO tags for 4 entity types (PER, LOC, ORG, GPE).', '9', '2n + 1.',
       ['B tags: 4.', 'I tags: 4, plus O.', eq('9')], check=9, tol=1e-9)
K.calc('e', 'Number of BIOES tags for 4 entity types.', '17', '4n + 1.',
       ['B, I, E and S per type: 16.', 'Plus O.', eq('17')], check=17, tol=1e-9)
K.calc('e', 'E = 300, H = 50, 50 POS tags, no biases. RNN tagger parameters.', '20000', 'E·H + H·H + H·K.',
       ['300 × 50 = 15,000.', '50 × 50 = 2,500 twice.', eq('20,000')], check=20000, tol=1e-9)
K.calc('m', 'Same tagger for NER with 5 types in BIO. Parameters.', '18050', '11 labels.',
       ['K = 2 × 5 + 1 = 11.', '15,000 + 2,500 + 50 × 11.', eq('18,050')], check=18050, tol=1e-9)
K.calc('m', 'Gold 4 spans, predicted 5, correct 3. Precision.', '0.6', 'correct ÷ predicted.',
       ['correct 3.', 'predicted 5.', eq('0.6')], check=0.6, tol=1e-9)
K.calc('m', 'Same counts. F1 to three decimals.', '0.667', '2PR ÷ (P + R).',
       ['P = 0.6, R = 0.75.', '2 × 0.45 = 0.9, P + R = 1.35.', eq('0.9 ÷ 1.35 = 0.667')], check=2 / 3, tol=5e-4)
K.calc('m', 'BiRNN tagger: E = 300, H = 50 per direction, 11 labels, no biases. Parameters.', '36100', 'Two directions and a 2H output.',
       ['One direction: 15,000 + 2,500 = 17,500.', 'Two: 35,000. Output: 100 × 11 = 1,100.', eq('36,100')], check=36100, tol=1e-9)
K.calc('m', 'Sentence classifier: E = 100, H = 64, 3 classes, no biases. RNN plus output parameters.', '10688', 'E·H + H·H + H·C.',
       ['100 × 64 = 6,400.', '64 × 64 = 4,096, 64 × 3 = 192.', eq('10,688')], check=10688, tol=1e-9)
K.calc('h', 'Hidden states 1, 0, −1, 2 (one number each). Mean pooled sentence value.', '0.5', 'Average.',
       ['Sum 1 + 0 − 1 + 2 = 2.', '4 states.', eq('2 ÷ 4 = 0.5')], check=0.5, tol=1e-9)
K.calc('h', 'Same states. Max pooled value.', '2', 'Largest.',
       ['Compare 1, 0, −1, 2.', 'Largest is the last.', eq('2, the same as the final state here')], check=2, tol=1e-9)
K.calc('h', 'A tagger predicts 0.7 for the gold tag at word 1 and 0.4 at word 2. Average cross-entropy, four decimals.', '0.6365', 'Mean of −ln p.',
       ['−ln 0.7 = 0.3567.', '−ln 0.4 = 0.9163.', eq('(0.3567 + 0.9163) ÷ 2 = 0.6365')], check=(0.35667494393873245 + 0.916290731874155) / 2, tol=5e-4)
K.calc('x', 'With 20 entity types, how many more labels does BIOES need than BIO?', '40', '(4n + 1) − (2n + 1).',
       ['BIOES: 81.', 'BIO: 41.', eq('2n = 40 more labels')], check=40, tol=1e-9)

# ---------------------------------------------------------------- assignments
K.assign('tobio', 'e', 'Spans to BIO tags',
         '<p>Write <code>to_bio(n_tokens, spans)</code>. spans is a list of (start, end, type) with end exclusive. Return the list of tags: B-type, I-type or O.</p>',
         '''
def to_bio(n_tokens, spans):
    pass
''', [('to_bio(5, [(0, 2, "PER")])', ['B-PER', 'I-PER', 'O', 'O', 'O']), ('to_bio(3, [(0, 1, "ORG"), (1, 2, "ORG")])', ['B-ORG', 'B-ORG', 'O']), ('to_bio(2, [])', ['O', 'O'])],
         '''
def to_bio(n_tokens, spans):
    tags = ["O"] * n_tokens
    for s, e, t in spans:
        tags[s] = "B-" + t
        for i in range(s + 1, e):
            tags[i] = "I-" + t
    return tags
''', 'Fill with O, then write B at each start and I after it.', '<p>The second test shows two adjacent entities of the same type, each starting with B.</p>')
K.assign('spanf1', 'm', 'Span level F1',
         '<p>Write <code>span_f1(gold, pred)</code> for two lists of (start, end, type) spans. Return F1 rounded to 4 decimals, and 0.0 if nothing matches.</p>',
         '''
def span_f1(gold, pred):
    pass
''', [('span_f1([(0, 2, "PER"), (3, 4, "ORG"), (8, 11, "ORG"), (17, 18, "LOC")], [(0, 2, "PER"), (3, 4, "ORG"), (8, 10, "ORG"), (17, 18, "LOC"), (12, 13, "PER")])', 0.6667),
      ('span_f1([(0, 1, "PER")], [(0, 1, "ORG")])', 0.0), ('span_f1([(0, 1, "PER")], [(0, 1, "PER")])', 1.0)],
         '''
def span_f1(gold, pred):
    tp = len(set(gold) & set(pred))
    if tp == 0:
        return 0.0
    P, R = tp / len(pred), tp / len(gold)
    return round(2 * P * R / (P + R), 4)
''', 'Exact match on start, end and type.', '<p>A wrong type is as wrong as a wrong boundary.</p>')
K.assign('tagparams', 'h', 'Count tagger parameters',
         '<p>Write <code>tagger_params(E, H, K, bi)</code> for an RNN tagger without biases. If bi is True, use two directions and an output layer on the joined 2H vector.</p>',
         '''
def tagger_params(E, H, K, bi):
    pass
''', [('tagger_params(300, 50, 50, False)', 20000), ('tagger_params(300, 50, 11, False)', 18050), ('tagger_params(300, 50, 11, True)', 36100)],
         '''
def tagger_params(E, H, K, bi):
    d = 2 if bi else 1
    return d * (E * H + H * H) + d * H * K
''', 'Count the RNN matrices once per direction.', '<p>The first two tests are the lecture answers.</p>')

K.must('Sequence labelling', 'One softmax over K tags per word, trained with cross-entropy. POS tagging is the classic case. RNN uses: generate, label, classify.')
K.must('NER', 'Find spans that are proper names and their type: PER, LOC, ORG, GPE (also dates, prices). Hard because of segmentation and type ambiguity.')
K.must('BIO', 'B starts a span, I continues it, O is outside. 2n + 1 tags (IO n + 1, BIOES 4n + 1). Score NER with exact span F1.')
K.must('Parameter answers', 'E·H + H·H + H·K: 300, 50, 50 tags gives 20,000. NER with 5 types: 11 labels, 18,050. BiRNN doubles the RNN part and reads 2H.')
K.must('BiRNN', 'h<sup>(t)</sup> = [h→<sup>(t)</sup>, h←<sup>(t)</sup>]: each word sees the whole sentence. Not for language modelling. Sentence vector: final, mean or max state.')

T = K.topic(
    slug='sequence-labelling-ner', topic='nn-sequence-labelling', step=(3, 'Language models and RNNs', 'nn-rnn', 'Predict the next word: n-gram models and their limits, fixed window and recurrent neural language models, sequence labelling with BIO tags, and why LSTM and GRU fix vanishing gradients.', 'College and masters'),
    title='Sequence labelling, NER and bidirectional RNNs', short='NER and BiRNN', badge='3.2', minutes=45, added='2026-11-01',
    lead='Give every word a label: POS tagging, named entities with BIO tags, the 20,000 and 18,050 parameter questions, span F1, sentence classification and bidirectional RNNs.',
    desc='RNN uses for generation, labelling and classification, the RNN tagger and its loss, named entity types and why NER is hard, BIO tagging with 2n + 1 tags and the Jane Villanueva sentence, span level precision, recall and F1, the two lecture parameter counts, sentence vectors and bidirectional RNNs.',
    summary='RNN taggers, NER, BIO tags, span F1, the parameter questions and bidirectional RNNs.',
    keywords=['sequence labelling', 'POS tagging', 'NER', 'BIO', 'span F1', 'bidirectional RNN', 'sentence classification'],
    recap='<p>An RNN tagger outputs one label per word. BIO tags turn entity spans into such labels with 2n + 1 tags, and NER is scored on exact spans. Bidirectional RNNs let every word see the whole sentence, which helps tagging and classification but not language modelling.</p>')
