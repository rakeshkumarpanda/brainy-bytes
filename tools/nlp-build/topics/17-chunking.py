# Chapter 5.4: chunking and named entity tagging. Source: lecture 9 (POS deck slides 31 to 34: perceptron and neural
# taggers, IOB chunking with "We saw the yellow dog", the United and San Francisco NER example, chunk against
# constituent from the class question) and problem H4.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('encode', r'''
# Spans to IOB tags: B- on the first word of a chunk, I- on the rest, O outside
words = ["The", "quick", "brown", "fox", "jumped", "over", "the", "lazy", "dog"]
spans = [(0, 4, "NP"), (4, 5, "VP"), (6, 9, "NP")]       # (start, end, type), end not included
tags = ["O"] * len(words)
for s, e, typ in spans:
    tags[s] = "B-" + typ
    for i in range(s + 1, e):
        tags[i] = "I-" + typ
print(list(zip(words, tags)))
''')

K.code('decode', r'''
# IOB tags back to spans. An I- after O (or after another type) is repaired as a B-
words = ["Sidharth", "Ranjan", "teaches", "at", "IIT", "Jodhpur"]
tags = ["B-PER", "I-PER", "O", "O", "B-ORG", "I-ORG"]
spans, cur = [], None
for i, t in enumerate(tags + ["O"]):
    if cur and not (t.startswith("I-") and t[2:] == cur[2]):
        spans.append((" ".join(words[cur[0]:i]), cur[2]))
        cur = None
    if t.startswith("B-") or (t.startswith("I-") and cur is None):
        cur = (i, i, t[2:])
print(spans)
''')

K.code('regex', r'''
# A tiny regular expression chunker over POS tags, like NLTK's RegexpParser with NP: {<DT>?<JJ>*<NN.*>+}
import re
sent = [("We", "PRP"), ("saw", "VBD"), ("the", "DT"), ("yellow", "JJ"), ("dog", "NN"), ("near", "IN"),
        ("heavy", "JJ"), ("rain", "NN"), ("clouds", "NNS")]
tagstr = "".join("<" + t + ">" for _, t in sent)
pattern = r"(<DT>)?(<JJ>)*(<NN[A-Z]*>)+"
for m in re.finditer(pattern, tagstr):
    start = tagstr[:m.start()].count("<")
    n = m.group(0).count("<")
    print("NP:", " ".join(w for w, _ in sent[start:start + n]))
''')

K.code('spanf1', r'''
# Entity level scoring: a predicted span counts only if its start, end and type all match
gold = {(0, 2, "PER"), (4, 6, "ORG"), (8, 9, "LOC")}
pred = {(0, 2, "PER"), (4, 5, "ORG"), (8, 9, "LOC"), (10, 11, "LOC")}
tp = len(gold & pred)
p, r = tp / len(pred), tp / len(gold)
print("true positives:", tp, " precision:", p, " recall:", round(r, 3), " F1:", round(2 * p * r / (p + r), 3))
''')

K.lesson('chunks', 'What a chunk is', f'''
<p>"Fast" is a word and "food" is a word, but "fast food" is one unit of meaning. So are "heavy rain", "the yellow dog" and "cats and dogs". Chunking finds these groups in a sentence. It is called shallow parsing because it finds flat, non overlapping pieces instead of a full tree.</p>
{table(['', 'Chunk', 'Constituent'], [
    ['Shape', 'flat, never nested', 'nested inside a full tree'],
    ['Example', '[the yellow dog]', '[[the yellow dog] [in [the park]]]'],
    ['Defined by', 'any useful group, often base noun and verb phrases', 'grammar: noun phrase, verb phrase, adjective phrase'],
    ['Cost', 'fast and robust, a tagging problem', 'slower, needs a parser (chapter 5.5)']])}
<p>In class: "A constituent is more grammatical, a syntactic category like a noun phrase. A chunk is any meaningful group of units that we may not always annotate grammatically."</p>
<h3>A rule based chunker</h3>
<p>The quickest chunker is a regular expression over POS tags. "An optional determiner, any number of adjectives, then one or more nouns" catches most base noun phrases. NLTK writes it as <code>NP: {{&lt;DT&gt;?&lt;JJ&gt;*&lt;NN.*&gt;+}}</code>.</p>
{code('regex')}
{note('This is why POS tagging comes first. The chunker never looks at the words, only at the tags, so tagging errors flow straight into chunking errors.', 'tip')}
''', kw=['chunk', 'chunking', 'shallow parsing', 'base noun phrase', 'constituent', 'flat', 'nested', 'regular expression chunker', 'RegexpParser'])

K.lesson('iob', 'IOB: spans as tags', f'''
<p>Finding spans sounds like a new problem, but a small trick turns it into tagging, so every tagger from the last three chapters can do it. Give each word one of three kinds of label.</p>
{fxs(fx('IOB tags', '<b>B-</b><i>X</i> begins a chunk of type <i>X</i> &nbsp; <b>I-</b><i>X</i> is inside it &nbsp; <b>O</b> is outside every chunk', 'With k chunk types there are 2k + 1 labels. The input can be the words and their POS tags.', key=True))}
<p>"We saw the yellow dog ." becomes We/B-NP saw/B-VP the/B-NP yellow/I-NP dog/I-NP ./O, which is [NP We] [VP saw] [NP the yellow dog] in brackets. As the professor put it, "everything remains the same" as POS tagging: same models, new tag set.</p>
{viz('iob')}
{steps('Problem H4, both directions', [
    'Encode [NP The quick brown fox] [VP jumped] over [NP the lazy dog].',
    'The/B-NP quick/I-NP brown/I-NP fox/I-NP jumped/B-VP over/O the/B-NP lazy/I-NP dog/I-NP.',
    'over is outside every chunk, so it gets O. Each chunk starts with B and continues with I of the same type.',
    'Decode Sidharth/B-PER Ranjan/I-PER teaches/O at/O IIT/B-ORG Jodhpur/I-ORG.',
    'A span is one B-X plus the I-X tags that follow it: [Sidharth Ranjan] PER and [IIT Jodhpur] ORG.'])}
{code('encode')}
{code('decode')}
{note('Why B at all? Two chunks of the same type can sit side by side: "gave [the girl] [a book]". With only I and O, the girl a book would merge into one span. B marks where the second one starts.', 'tip')}
{deep('IOB1, IOB2 and BIOES', '<p>IOB2, used above, puts B on the first word of every chunk. The older IOB1 (Ramshaw and Marcus 1995) uses B only when a chunk directly follows another of the same type. BIOES, also called BILOU, adds E for the last word and S for a single word chunk, giving 4k + 1 labels. The extra labels give the model more precise targets and often help slightly for named entities. Ill formed sequences such as O then I-X are usually repaired by reading the I-X as B-X.</p>')}
''', kw=['IOB', 'BIO', 'B- tag', 'I- tag', 'O tag', 'span encoding', 'H4', 'IOB2', 'BIOES', 'BILOU', 'repair'])

K.lesson('ner', 'Named entity tagging', f'''
<p>Named entity recognition (NER) finds names of people, organisations, places, dates and amounts. It is chunking with entity types instead of phrase types.</p>
{steps('Reading the slide example', [
    'United/B-ORG cancelled/O the/O flight/O from/O San/B-LOC Francisco/I-LOC.',
    'A span starts at each B- and continues through the following I- tags of the same type.',
    'Spans: [United] ORG and [San Francisco] LOC. Everything tagged O is outside any entity.'])}
{table(['Type', 'Examples'], [
    ['PER (person)', 'Sidharth Ranjan, Marie Curie'],
    ['ORG (organisation)', 'United, IIT Jodhpur, the World Health Organization'],
    ['LOC or GPE (place)', 'San Francisco, the Falkland Islands, India'],
    ['DATE, MONEY, PERCENT', 'next Tuesday, 500 rupees, 12%']])}
<h3>Models</h3>
<p>The same families as POS tagging. Features matter even more: a capital letter, a title such as Dr., a word shape such as Xxxx, a gazetteer list of known cities, and the neighbouring words. The perceptron (Collins 2002) learns from its errors with these features. A conditional random field (CRF) normalises over the whole tag sequence, so it can learn that I-LOC never follows B-PER. Neural taggers, BiLSTM with a CRF layer or a fine tuned BERT, lead today.</p>
{fxs(fx('Entity level F1', 'P = ' + frac('correct spans', 'predicted spans') + ' &nbsp; R = ' + frac('correct spans', 'gold spans') + ' &nbsp; F1 = ' + frac('2PR', 'P + R'), 'A predicted span counts only if its start, end and type all match. Token accuracy is misleading because most tokens are O.', key=True))}
{code('spanf1')}
{scene('a bank reading cheque requests', '<p>A bank\'s email system receives "Please transfer 25,000 rupees to Asha Verma at Kotak Mahindra Bank by Friday". An NER tagger marks MONEY, PER, ORG and DATE spans, and a form is filled in for a human to approve. A missed boundary, such as tagging only "Kotak" as ORG, would count as wrong under entity level scoring, which is exactly the strictness the bank needs.</p>')}
{ladder(
    '<p>Mark groups of words that belong together, and names of people and places, by giving every word a small label: begin, inside or outside.</p>',
    '<p>IOB turns span finding into tagging with 2k + 1 labels. Rule chunkers use regular expressions over POS tags. NER uses the same taggers with richer features and is scored with entity level precision, recall and F1.</p>',
    '<p>Linear chain CRFs model P(Y | X) ∝ exp(Σ θ · f(y<sub>i−1</sub>, y<sub>i</sub>, X, i)) and decode with Viterbi. They avoid the label bias of left to right classifiers (MEMMs). Encoding choice (IOB2 or BIOES) changes what the transition weights can express.</p>',
    '<p>Nested NER (an organisation inside a location name) breaks flat IOB and uses span based or hypergraph models. Low resource NER uses cross lingual transfer, and large language models can extract entities from instructions with few or no examples.</p>')}
''', kw=['named entity recognition', 'NER', 'PER ORG LOC', 'gazetteer', 'perceptron', 'CRF', 'BiLSTM CRF', 'BERT', 'entity level F1', 'precision', 'recall'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In IOB, the tag O means', ['Object', 'Outside any chunk', 'Open chunk', 'Ordinal'], 1,
       'Three letters: B, I, O.', 'The word belongs to no chunk.')
K.quiz('e', 'Which is a chunk?', ['"the"', '"heavy rain"', '"."', '"is"'], 1,
       'A group of words that belong together.', 'heavy rain is one unit of meaning.')
K.quiz('e', 'Chunking is also called', ['Deep parsing', 'Shallow parsing', 'Stemming', 'Smoothing'], 1,
       'Flat pieces, no full tree.', 'It finds non overlapping groups without building a full tree.')
K.quiz('m', 'Decode San/B-LOC Francisco/I-LOC. The span is', ['[San] [Francisco]', '[San Francisco] LOC', 'No span', '[Francisco] LOC'], 1,
       'B plus following I of the same type.', 'One location span of two words.')
K.quiz('m', 'How many IOB2 labels are needed for 4 entity types?', ['4', '8', '9', '17'], 2,
       '2k + 1.', '4 B tags, 4 I tags and O.')
K.quiz('m', 'Why do we need B and not only I and O?', ['For speed', 'To separate two adjacent chunks of the same type', 'For punctuation', 'Because O is ambiguous'], 1,
       'gave [the girl] [a book].', 'Without B the two noun phrases would merge.')
K.quiz('m', 'How is a chunk different from a constituent?', ['Chunks are nested', 'Chunks are flat and never nested, constituents form a nested tree', 'They are the same', 'Constituents are single words'], 1,
       'Think of [[the dog] [in the park]].', 'Chunks do not contain other chunks.')
K.quiz('m', 'A tag sequence O I-PER is', ['Valid', 'Ill formed, usually repaired as O B-PER', 'A new entity type', 'Always an error to drop'], 1,
       'I must continue something.', 'An I with nothing to continue is read as the start of a span.')
K.quiz('h', 'Why is token accuracy a poor score for NER?', ['Too slow', 'Most tokens are O, so tagging everything O already scores high', 'It ignores O', 'It needs gold spans'], 1,
       'Class imbalance.', 'Entity level F1 counts only whole correct spans.')
K.quiz('h', 'A model predicts [IIT] ORG where gold has [IIT Jodhpur] ORG. Under entity level scoring this is', ['Correct', 'Wrong, a boundary error counts as both a false positive and a false negative', 'Half correct', 'Ignored'], 1,
       'Start, end and type must all match.', 'The predicted span is wrong and the gold span is missed.')
K.quiz('h', 'Which model normalises over the whole tag sequence and avoids label bias?', ['MEMM', 'CRF', 'Unigram tagger', 'Regex chunker'], 1,
       'Global normalisation.', 'A linear chain CRF divides by a sum over all label sequences.')
K.quiz('x', 'How many BIOES labels are needed for k types?', ['2k + 1', '3k + 1', '4k + 1', '5k'], 2,
       'B, I, E and S for each type, plus O.', '4k + 1.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'With 3 entity types (PER, ORG, LOC), how many IOB2 labels are there?', '7', '2k + 1.',
       ['B- for each type: 3.', 'I- for each type: 3.', eq('3 + 3 + O = 7')], check=7, tol=0.01)
K.calc('e', 'How many chunks are in The/B-NP quick/I-NP brown/I-NP fox/I-NP jumped/B-VP over/O the/B-NP lazy/I-NP dog/I-NP?', '3', 'Count the B tags.',
       ['Each chunk starts with exactly one B.', 'B tags: The, jumped, the.', eq('3 chunks')], check=3, tol=0.01)
K.calc('e', 'In the sentence above, how many tokens are tagged O?', '1', 'Words outside every chunk.',
       ['List the tags.', 'Only over has O.', eq('1')], check=1, tol=0.01)
K.calc('m', 'A tagger predicts 8 entity spans. 6 are exactly right. Gold has 10 spans. What is precision?', '0.75', 'Correct over predicted.',
       ['Correct spans: 6.', 'Predicted spans: 8.', eq('6 ÷ 8 = 0.75')], check=0.75, tol=0.001)
K.calc('m', 'Same tagger: what is recall?', '0.6', 'Correct over gold.',
       ['Correct spans: 6.', 'Gold spans: 10.', eq('6 ÷ 10 = 0.6')], check=0.6, tol=0.001)
K.calc('m', 'Same tagger: what is F1? Four decimals.', '0.6667', 'Harmonic mean.',
       ['P = 0.75, R = 0.6.', '2PR = 0.9 and P + R = 1.35.', eq('0.9 ÷ 1.35 = 0.6667')], check=2 / 3, tol=0.0001)
K.calc('m', 'In a 1,000 token NER test set, 880 tokens are O. What token accuracy does a tagger get by tagging everything O? Two decimals.', '0.88', 'Share of O tokens.',
       ['Right on every O token: 880.', 'Wrong on every entity token: 120.', eq('880 ÷ 1,000 = 0.88, with entity F1 = 0')], check=0.88, tol=0.001)
K.calc('h', 'Gold spans {(0,2,PER), (4,6,ORG), (8,9,LOC)}, predicted {(0,2,PER), (4,5,ORG), (8,9,LOC), (10,11,LOC)}. What is the entity F1? Three decimals.', '0.571', 'Only exact matches count.',
       ['Exact matches: (0,2,PER) and (8,9,LOC), so 2.', 'P = 2 ÷ 4 = 0.5, R = 2 ÷ 3 = 0.667.', 'F1 = 2 × 0.5 × 0.667 ÷ (0.5 + 0.667).', eq('= 0.571')], check=4 / 7, tol=0.0005)
K.calc('h', 'How many BIOES labels are needed for 4 entity types?', '17', 'B, I, E, S per type, plus O.',
       ['Four labels per type.', '4 × 4 = 16.', eq('16 + 1 = 17')], check=17, tol=0.01)
K.calc('h', 'An HMM chunker with 2k + 1 = 7 labels has how many transition parameters (a full 7 × 7 table)?', '49', 'q².',
       ['q = 7 labels.', 'Every pair (previous, next) has a parameter.', eq('7 × 7 = 49, though moves like O → I-PER should get 0')], check=49, tol=0.01)
K.calc('x', 'With k types under IOB2, how many transitions into an I- tag are valid (from B-X or I-X of the same type X)? Give it for k = 3.', '6', 'Two valid sources per I tag.',
       ['There are k I tags.', 'Each I-X may follow only B-X or I-X.', eq('2k = 6 for k = 3')], check=6, tol=0.01)

# ---------------------------------------------------------------- assignments
K.assign('enc', 'e', 'Spans to IOB',
         '<p>Write <code>to_iob(n, spans)</code>. n is the number of words and spans is a list of (start, end, type) with end not included. Return the list of IOB2 tags.</p>',
         '''
def to_iob(n, spans):
    # your code here
    pass
''', [('to_iob(9, [(0, 4, "NP"), (4, 5, "VP"), (6, 9, "NP")])', ['B-NP', 'I-NP', 'I-NP', 'I-NP', 'B-VP', 'O', 'B-NP', 'I-NP', 'I-NP']),
      ('to_iob(4, [(1, 2, "NP"), (2, 4, "NP")])', ['O', 'B-NP', 'B-NP', 'I-NP'])],
         '''
def to_iob(n, spans):
    tags = ["O"] * n
    for s, e, typ in spans:
        tags[s] = "B-" + typ
        for i in range(s + 1, e):
            tags[i] = "I-" + typ
    return tags
''', 'Fill with O, then write B on each start and I on the rest.', '<p>The second test has two adjacent noun phrases. Only the B tells them apart.</p>')
K.assign('dec', 'm', 'IOB to spans',
         '<p>Write <code>from_iob(tags)</code> that returns a list of (start, end, type) with end not included. An I-X that does not continue a span of type X starts a new span.</p>',
         '''
def from_iob(tags):
    # your code here
    pass
''', [('from_iob(["B-PER", "I-PER", "O", "O", "B-ORG", "I-ORG"])', [(0, 2, 'PER'), (4, 6, 'ORG')]),
      ('from_iob(["O", "I-LOC", "I-LOC", "B-LOC"])', [(1, 3, 'LOC'), (3, 4, 'LOC')]),
      ('from_iob(["B-PER", "I-ORG"])', [(0, 1, 'PER'), (1, 2, 'ORG')])],
         '''
def from_iob(tags):
    spans, cur = [], None
    for i, t in enumerate(tags + ["O"]):
        if cur and not (t.startswith("I-") and t[2:] == cur[1]):
            spans.append((cur[0], i, cur[1]))
            cur = None
        if t.startswith("B-") or (t.startswith("I-") and cur is None):
            cur = (i, t[2:])
    return spans
''', 'Close the open span whenever the next tag does not continue it. A sentinel O at the end closes the last one.', '<p>The second and third tests check the repair rule for ill formed input.</p>')
K.assign('f1', 'm', 'Entity level F1',
         '<p>Write <code>span_f1(gold, pred)</code> where both are lists of (start, end, type). Return (precision, recall, F1), each rounded to 3 decimals. If there are no predictions or no gold spans, the corresponding value is 0, and F1 is 0 when P + R is 0.</p>',
         '''
def span_f1(gold, pred):
    # your code here
    pass
''', [('span_f1([(0, 2, "PER"), (4, 6, "ORG"), (8, 9, "LOC")], [(0, 2, "PER"), (4, 5, "ORG"), (8, 9, "LOC"), (10, 11, "LOC")])', (0.5, 0.667, 0.571)),
      ('span_f1([(0, 1, "PER"), (3, 5, "LOC")], [(0, 1, "PER"), (3, 5, "LOC")])', (1.0, 1.0, 1.0))],
         '''
def span_f1(gold, pred):
    tp = len(set(gold) & set(pred))
    p = tp / len(pred) if pred else 0
    r = tp / len(gold) if gold else 0
    f = 2 * p * r / (p + r) if p + r else 0
    return (round(p, 3), round(r, 3), round(f, 3))
''', 'Use sets of tuples so exact matches are a set intersection.', '<p>The boundary error on ORG costs both a false positive and a false negative.</p>')

K.must('Chunk', 'A flat, non overlapping group of words such as [the yellow dog]. Chunking is shallow parsing. Constituents nest, chunks do not.')
K.must('IOB', 'B-X begins, I-X continues, O is outside. 2k + 1 labels. Turns span finding into tagging with the same models.')
K.must('Decoding IOB', 'A span is a B-X plus the following I-X tags. An I-X after O or another type is repaired as B-X.')
K.must('NER', 'PER, ORG, LOC, DATE, MONEY. Perceptron, CRF, BiLSTM CRF and BERT. Features: capitals, shape, gazetteers, neighbours.')
K.must('Scoring', 'Entity level precision, recall and F1 with exact start, end and type. Token accuracy is inflated by O.')

T = K.topic(
    slug='chunking', topic='chunking', step=(5, 'Tagging and syntax', 'nlp-syntax', 'Tag every word with its part of speech using HMMs and Viterbi, mark chunks and names with IOB, and draw constituency and dependency trees.', 'College and masters'),
    title='Chunking and named entities', short='Chunking and NER', badge='5.4', minutes=40,
    lead='Group words into flat chunks, turn spans into tags with IOB, find people, places and organisations, and score them fairly.',
    desc='Chunks against constituents, a regular expression chunker over POS tags, IOB encoding and decoding with problem H4, IOB2 and BIOES, named entity recognition with the United and San Francisco example, the perceptron and CRF, and entity level precision, recall and F1.',
    summary='Chunks, regex chunkers, IOB and BIOES encoding, NER models and entity level F1.',
    keywords=['chunking', 'IOB', 'BIOES', 'NER', 'named entity', 'CRF', 'F1', 'shallow parsing'],
    recap='<p>Chunking finds flat groups of words. IOB tags turn those groups into a tagging problem, so HMMs, CRFs and neural taggers all apply. Named entity recognition is chunking with entity types, scored by exact span precision, recall and F1.</p>')
