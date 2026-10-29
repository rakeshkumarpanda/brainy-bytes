# Chapter 2.1: tokenisation. Source: lecture 9 warm-up (the preprocessing pipeline of activity 3), the NLTK notebook
# (sent_tokenize and word_tokenize on the Dr. jack paragraph, reading files), the classmate's aside in lecture 2 on
# vocabulary and word indices, plus subword tokenisation as the bridge to modern models.
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq
from nlpkit import listing

K = Kit()

PARA = "All work and no play make Dr. jack a dull boy. It's a beautiful day out there in Jodhpur. Don't you think, it will rain today?"

K.code('split', r'''
# A small sentence splitter: a full stop ends a sentence unless the word is a known abbreviation
ABBREV = {"dr.", "mr.", "mrs.", "prof.", "etc."}
text = "All work and no play make Dr. jack a dull boy. It's a beautiful day out there in Jodhpur. Don't you think, it will rain today?"

sentences, current = [], []
for word in text.split():
    current.append(word)
    if word[-1] in ".!?" and word.lower() not in ABBREV:
        sentences.append(" ".join(current))
        current = []
if current:
    sentences.append(" ".join(current))

for i, s in enumerate(sentences, 1):
    print(i, s)
''')

K.code('tokenize', r'''
# Treebank style tokens without NLTK: split punctuation and contractions
import re

def tokenize(sentence):
    s = re.sub(r"([,;:?!])", r" \1 ", sentence)          # punctuation becomes its own token
    s = re.sub(r"(\w)\.\s*$", r"\1 .", s)                 # only the final full stop is split off
    s = re.sub(r"(\w)(n't)\b", r"\1 \2", s)               # Don't -> Do n't
    s = re.sub(r"(\w)('s|'re|'ll|'m|'ve|'d)\b", r"\1 \2", s)  # It's -> It 's
    return s.split()

for sent in ["All work and no play make Dr. jack a dull boy.", "It's a beautiful day out there in Jodhpur.", "Don't you think, it will rain today?"]:
    print(tokenize(sent))
''')

K.code('vocab', r'''
# Words become numbers: build a vocabulary and replace every token by its index
tokens = "the cat sat on the mat and the dog sat on the log".split()

vocab = {}
for t in tokens:
    if t not in vocab:
        vocab[t] = len(vocab)          # the next free index

ids = [vocab[t] for t in tokens]
print("vocabulary:", vocab)
print("ids:", ids)
print("tokens:", len(tokens), " types:", len(vocab), " type token ratio:", round(len(vocab) / len(tokens), 3))
''')

K.code('bpe', r'''
# Byte pair encoding. Merge the most frequent pair of adjacent symbols, again and again
from collections import Counter

words = {("l", "o", "w", "_"): 5, ("l", "o", "w", "e", "r", "_"): 2,
         ("n", "e", "w", "e", "s", "t", "_"): 6, ("w", "i", "d", "e", "s", "t", "_"): 3}

def merge(word, pair):
    out, i = [], 0
    while i < len(word):
        if i + 1 < len(word) and (word[i], word[i + 1]) == pair:
            out.append(word[i] + word[i + 1])
            i += 2
        else:
            out.append(word[i])
            i += 1
    return tuple(out)

for step in range(1, 4):
    pairs = Counter()
    for w, c in words.items():
        for a, b in zip(w, w[1:]):
            pairs[(a, b)] += c
    best = max(pairs, key=pairs.get)
    words = {merge(w, best): c for w, c in words.items()}
    print(step, "merge", best, "seen", pairs[best], "times")
print([" ".join(w) for w in words])
''')

K.lesson('pipeline', 'The preprocessing pipeline', f'''
<p>Before a computer can count, tag or model text, the raw string has to be cut into pieces it can work with. Lecture 9 opened with a notebook that walks through the classic pipeline with NLTK. The professor named two items from it as exam material: the difference between a stem and a lemma, and the idea of tagsets.</p>
{table(['Step', 'What it does', 'Example'], [
    ['Sentence segmentation', 'Split a paragraph into sentences', '"I came. I saw." → ["I came.", "I saw."]'],
    ['Tokenisation', 'Split each sentence into tokens (words and punctuation)', '"John went to Patna." → John, went, to, Patna, .'],
    ['Stemming', 'Chop endings with rules. The stem need not be a word', 'gaming → game, leaves → leav'],
    ['Lemmatisation', 'Map to the dictionary form using the part of speech', 'children → child, leaves → leaf'],
    ['POS tagging', 'Give each token a grammatical category', 'John/NNP went/VBD to/TO Patna/NNP'],
    ['Frequency distribution', 'Count tokens or tags', 'FreqDist(brown.words()).most_common(10)']])}
<h3>Tokens and types</h3>
<p>Two words you will use all through the course. A <b>token</b> is one occurrence of a word in running text. A <b>type</b> is a distinct word. "the cat sat on the mat" has 6 tokens but 5 types, because "the" appears twice. The vocabulary of a corpus is its set of types.</p>
{fxs(
    fx('Tokens and types', '<i>N</i> = number of tokens, &nbsp; <i>V</i> = |vocabulary| = number of types', 'FreqDist calls these N() (outcomes) and B() (samples).', key=True),
    fx('Type token ratio', 'TTR = ' + frac('<i>V</i>', '<i>N</i>'), 'Higher means more varied vocabulary. It falls as a text gets longer, so only compare texts of similar length.'))}
<h3>Words become numbers</h3>
<p>A classmate in lecture 2 put it plainly: computers understand only numbers, so give each vocabulary word an index ("water" → 1) and count. That is exactly how every NLP system starts, from n-gram models to transformers.</p>
{code('vocab')}
''', kw=['preprocessing pipeline', 'NLTK', 'token', 'type', 'vocabulary', 'type token ratio', 'word index', 'tokens and types'])

K.lesson('sentences', 'Sentence segmentation', f'''
<p>Splitting at every full stop sounds easy until you meet "Dr.", "p.m.", "3.50" or "U.S.". The notebook used NLTK\'s <b>Punkt</b> sentence tokenizer. Punkt is unsupervised: it was trained on a large amount of plain English text and learned which words are usually abbreviations, which pairs of words go together, and which words usually start a sentence. The pretrained English model ships with NLTK, so no hand written list is needed.</p>
{listing("""import nltk
nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize

data = "All work and no play make Dr. jack a dull boy. It's a beautiful day out there in Jodhpur. Don't you think, it will rain today?"
sentences = sent_tokenize(data)
print(sentences)""", """['All work and no play make Dr. jack a dull boy.', "It's a beautiful day out there in Jodhpur.", "Don't you think, it will rain today?"]""")}
<p>Three sentences, with "Dr." correctly kept inside the first one even though the next word "jack" is lower case. The animation lets you switch the rules on and off.</p>
{viz('sentsplit')}
{code('split')}
{note('Full stops are ambiguous in English: end of sentence, abbreviation, decimal point, or part of an email address. Segmentation is a classification problem for every full stop.', 'tip')}
''', kw=['sentence segmentation', 'sentence tokenization', 'sent_tokenize', 'Punkt', 'abbreviation', 'full stop ambiguity'])

K.lesson('words', 'Word tokenisation', f'''
<p>Word tokenisation splits a sentence into tokens. NLTK\'s word_tokenize first splits sentences with Punkt and then applies the Penn Treebank conventions to each sentence.</p>
{listing("""from nltk.tokenize import word_tokenize
words = word_tokenize(data)
print(words)""", """['All', 'work', 'and', 'no', 'play', 'make', 'Dr.', 'jack', 'a', 'dull', 'boy', '.', 'It', "'s", 'a', 'beautiful', 'day', 'out', 'there', 'in', 'Jodhpur', '.', 'Do', "n't", 'you', 'think', ',', 'it', 'will', 'rain', 'today', '?']""")}
{table(['Convention', 'Example', 'Why'], [
    ['Punctuation is its own token', 'boy. → boy, .', 'So "boy" and "boy." are one type'],
    ['Contractions split off', "Don't → Do, n't &nbsp; It's → It, 's", "n't is the word not, 's can be is or a possessive"],
    ['Abbreviations stay whole', 'Dr. stays Dr.', 'The full stop is part of the word'],
    ['Only the sentence final stop is split', 'Jodhpur. → Jodhpur, .', 'Inner stops belong to abbreviations or numbers']])}
{viz('tokenizer')}
{code('tokenize')}
<h3>Why tokenisation is harder than it looks</h3>
<ul>
<li><b>Hyphens and compounds:</b> state-of-the-art, New Delhi, ice cream. One token or several?</li>
<li><b>Numbers, dates and links:</b> 3.50, 28/10/2026, www.iitj.ac.in should not be cut at the dots.</li>
<li><b>Languages without spaces:</b> Chinese and Japanese need a segmenter just to find word boundaries.</li>
<li><b>Rich morphology and code mixing:</b> Hindi and Marathi attach many endings, and Indian social media mixes Hindi and English in one sentence.</li>
</ul>
{scene('a search engine for a railway helpdesk', '<p>Users type "can\'t book tatkal", "cannot book Tatkal" and "cant book tatkal". If the tokenizer keeps "can\'t" whole and lower casing is off, these become three different queries. Splitting the contraction (ca, n\'t), lower casing and mapping n\'t and not to one form makes all three match the same help article.</p>')}
''', kw=['word tokenization', 'word_tokenize', 'Penn Treebank tokenizer', 'contractions', "n't", 'punctuation tokens', 'hyphens', 'code mixing'])

K.lesson('subwords', 'Beyond words: subword tokens', f'''
<p>A word level vocabulary has a hard edge. Any word not seen in training is <b>out of vocabulary</b> (OOV), and chapter 4 shows how badly that hurts a language model. Modern systems avoid the edge by splitting rare words into smaller pieces.</p>
{steps('Byte pair encoding (Sennrich et al., 2016) on a tiny corpus', [
    'Start with characters plus an end of word mark: low ×5, lower ×2, newest ×6, widest ×3.',
    'Count adjacent pairs, weighted by word count. e s appears 6 + 3 = 9 times, the most frequent pair.',
    'Merge it into one symbol es, then count again. es t (9) and est _ (9) come next.',
    'Then l o (5 + 2 = 7). After a few thousand merges, common words are single tokens and rare words split into known pieces.'])}
{code('bpe')}
{ladder(
    '<p>A computer reads text by cutting it into pieces called tokens, usually words and punctuation marks. It then gives every different piece a number.</p>',
    '<p>Sentence segmentation and word tokenisation are rule or model based. Types are distinct tokens, and the vocabulary is the set of types. Unknown words in new text are a problem for word level models.</p>',
    '<p>Subword tokenisers such as BPE, WordPiece (BERT) and unigram language model tokenisation (SentencePiece) learn a vocabulary of pieces from data, so any word can be written with known pieces and OOV disappears. The vocabulary size, often 30,000 to 100,000, trades sequence length against embedding table size.</p>',
    '<p>Tokenisation affects fairness and cost: languages written in non Latin scripts are often split into many more tokens per sentence, so they cost more and fit less text in a context window. Research looks at tokenizer free byte models, better multilingual vocabularies and how token boundaries affect arithmetic and spelling in large models.</p>')}
''', kw=['subword', 'byte pair encoding', 'BPE', 'WordPiece', 'SentencePiece', 'out of vocabulary', 'OOV', 'vocabulary size'])

K.lesson('files', 'Reading text files in Python', f'''
<p>The notebook also practised reading a corpus from a file, because real corpora live on disk. Three habits are worth keeping.</p>
{listing("""with open('document.txt') as f:      # with closes the file for you
    lines = f.readlines()             # a list, one item per line
print(lines[-1])                      # the last line

last = ""
with open('document.txt') as f:
    for line in f:                    # read one line at a time
        last = line                   # only the newest line is kept
print(last)""", """Good Luck!
Good Luck!""", title='Python, from the notebook file exercise')}
<ul>
<li>Use <code>with open(...)</code>. The file is closed even if an error happens inside the block.</li>
<li><code>read()</code> gives one long string, <code>readlines()</code> a list of lines. For a huge corpus loop over the file object so only one line is in memory.</li>
<li>Modes: "r" read, "w" overwrite, "a" append to the end.</li>
</ul>
{note('Every SRILM file in chapter 6 has one sentence per line with tokens separated by spaces. That format is the result of exactly the segmentation and tokenisation in this chapter.', 'exam')}
''', kw=['reading files', 'open', 'with statement', 'readlines', 'context manager', 'one sentence per line'])

# ---------------------------------------------------------------- quiz
K.quiz('e', '"the cat sat on the mat" has how many tokens and types?', ['6 tokens, 6 types', '6 tokens, 5 types', '5 tokens, 6 types', '5 tokens, 5 types'], 1,
       '"the" appears twice.', 'Six occurrences, but only five distinct words.')
K.quiz('e', 'How many sentences did sent_tokenize find in the notebook paragraph?', ['2', '3', '4', '5'], 1,
       'Dr. is an abbreviation.', 'Three. Punkt did not split after "Dr." because it learned that Dr. is an abbreviation.')
K.quiz('e', 'word_tokenize turns "Don\'t" into', ["Don't", "Don, 't", "Do, n't", 'Do, not'], 2,
       'Penn Treebank convention.', "The negation n't is split off as its own token.")
K.quiz('m', 'Why does the tokenizer separate "boy." into "boy" and "."?', ['To save memory', 'So that "boy" at the end of a sentence counts as the same type as "boy" elsewhere', 'Because full stops are words', 'To find abbreviations'], 1,
       'Think about counting types.', 'Otherwise the vocabulary would contain both boy and boy., splitting the counts of one word.')
K.quiz('m', 'Punkt is described as unsupervised because', ['It needs no text', 'It learns abbreviations and sentence starters from plain unlabelled text', 'It was written by hand', 'It uses a neural network'], 1,
       'No one labelled sentence boundaries.', 'It was trained on plain text and discovered statistically which words behave like abbreviations.')
K.quiz('m', 'Splitting on spaces gives 26 pieces for the notebook paragraph, word_tokenize gives 32. Where do the 6 extra tokens come from?', [
    'Duplicated words', "Punctuation split off (. . , ? ) and the contractions 's and n't", 'Lower casing', 'Stemming'], 1,
    'Count the punctuation marks and contractions.', "Four punctuation marks (. . , ?) plus 's and n't make 6 extra tokens.")
K.quiz('m', 'Which language needs a segmenter just to find where words begin and end?', ['English', 'Hindi', 'Chinese', 'Spanish'], 2,
       'Which writing system uses no spaces?', 'Chinese is written without spaces between words.')
K.quiz('h', 'What problem does subword tokenisation such as BPE mainly solve?', ['Slow reading', 'Out of vocabulary words', 'Sentence segmentation', 'Stemming errors'], 1,
       'What happens to an unseen word?', 'Any word can be built from learned pieces, so nothing is out of vocabulary.')
K.quiz('h', 'In BPE, which pair is merged first?', ['A random pair', 'The most frequent adjacent pair of symbols, weighted by word counts', 'The longest word', 'The rarest pair'], 1,
       'Frequency drives every merge.', 'Each step counts adjacent pairs across the corpus and merges the most frequent one.')
K.quiz('h', 'The type token ratio of a long novel compared with a short story by the same author is usually', ['Higher', 'Lower', 'The same', 'Exactly 1'], 1,
       'New words keep appearing but more slowly.', 'Common words repeat more as text grows, so V grows slower than N and the ratio falls (Heaps\' law).')
K.quiz('x', 'Why can tokenisation make language models more expensive for Hindi than for English?', [
    'Hindi has no grammar', 'Tokenizers trained mostly on English split Hindi text into many more tokens per sentence', 'Hindi words are shorter', 'Hindi cannot be stored as numbers'], 1,
    'Cost is counted per token.', 'More tokens per sentence means more compute, more cost and less text in the context window.')
K.quiz('x', 'Which reading of a file keeps memory use smallest for a 10 GB corpus?', ['f.read()', 'f.readlines()', 'for line in f: ...', 'list(f)'], 2,
       'Which one holds the whole file?', 'Iterating over the file object reads one line at a time. The others load everything.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many tokens does word_tokenize give for the notebook paragraph?', '32', 'Count the list in the notebook output.',
       ['Sentence 1: 11 words + "." = 12.', 'Sentence 2: It, \'s, a, beautiful, day, out, there, in, Jodhpur, . = 10.', 'Sentence 3: Do, n\'t, you, think, ",", it, will, rain, today, ? = 10.', eq('12 + 10 + 10 = 32')], check=32)
K.calc('e', 'How many types are among those 32 tokens (case sensitive)?', '30', 'Find tokens that repeat.',
       ['"a" appears twice.', '"." appears twice.', 'Every other token appears once.', eq('32 − 2 = 30 types')], check=30)
K.calc('e', 'What is the type token ratio of "the cat sat on the mat"? Give three decimals.', '0.833', 'V ÷ N.',
       ['N = 6 tokens.', 'V = 5 types.', eq('TTR = 5 ÷ 6 ≈ 0.833')], check=5 / 6, tol=0.0005)
K.calc('m', 'How many pieces does text.split() give for the notebook paragraph?', '26', 'Count words separated by spaces.',
       ['Sentence 1 has 11 space separated pieces.', 'Sentence 2 has 8 (It\'s counts as one).', 'Sentence 3 has 7 (Don\'t and think, count as one each).', eq('11 + 8 + 7 = 26')], check=len(PARA.split()))
K.calc('m', 'In "the cat sat on the mat and the dog sat on the log", how many tokens and types are there? Give tokens.', '13', 'Count every word.',
       ['the(4) cat sat(2) on(2) mat and dog log.', 'Tokens: 13.', eq('N = 13'), 'Types: the, cat, sat, on, mat, and, dog, log = 8.'], check=13)
K.calc('m', 'For that sentence (13 tokens, 8 types) what is the type token ratio? Give three decimals.', '0.615', 'V ÷ N.',
       ['V = 8.', 'N = 13.', eq('8 ÷ 13 ≈ 0.615')], check=8 / 13, tol=0.0005)
K.calc('m', 'In the BPE example (low ×5, lower ×2, newest ×6, widest ×3), how many times does the pair e s occur?', '9', 'Only words with "es" count.',
       ['newest contains e s once and appears 6 times.', 'widest contains e s once and appears 3 times.', eq('6 + 3 = 9')], check=9)
K.calc('h', 'In the same corpus, how often does the pair l o occur?', '7', 'Which words start with l o?',
       ['low: 5 times.', 'lower: 2 times.', eq('5 + 2 = 7'), 'So l o is merged after the three es, est and est_ merges, which each have 9.'], check=7)
K.calc('h', 'A vocabulary has 50,000 entries and each entry has a 768 number embedding. How many numbers does the embedding table hold?', '38400000', 'Rows times columns.',
       ['Rows = 50,000 types.', 'Columns = 768.', eq('50,000 × 768 = 38,400,000'), 'This is why vocabulary size is a real cost in model design.'], check=50000 * 768)
K.calc('h', 'A tokenizer uses 1.3 tokens per English word and 4.2 per Hindi word. For the same 1,000 word text, how many more tokens does Hindi need?', '2900', 'Compute both totals and subtract.',
       ['English: 1,000 × 1.3 = 1,300 tokens.', 'Hindi: 1,000 × 4.2 = 4,200 tokens.', eq('4,200 − 1,300 = 2,900 more tokens')], check=2900)
K.calc('x', 'Heaps\' law says V ≈ k N<sup>β</sup>. With k = 30 and β = 0.5, how many types are expected in 1,000,000 tokens?', '30000', 'Take the square root of N.',
       ['N<sup>0.5</sup> = √1,000,000 = 1,000.', eq('V ≈ 30 × 1,000 = 30,000'), 'Doubling the text does not double the vocabulary. It grows by about √2 ≈ 1.41.'], check=30000)

# ---------------------------------------------------------------- assignments
K.assign('tok', 'e', 'Tokens, types and the ratio',
         '<p>Write <code>stats(text)</code> that splits on spaces, lower cases every token and returns <code>[tokens, types, ratio]</code> where ratio is types ÷ tokens rounded to 3 decimals.</p>',
         '''
def stats(text):
    # your code here
    pass
''', [("stats('the cat sat on the mat')", [6, 5, 0.833]), ("stats('This is an example sentence to tell you how this example works')", [12, 10, 0.833]), ("stats('a a a a')", [4, 1, 0.25])],
         '''
def stats(text):
    toks = [t.lower() for t in text.split()]
    v = len(set(toks))
    return [len(toks), v, round(v / len(toks), 3)]
''', 'A set keeps one copy of each type.', '<p>The second test is the notebook FreqDist sentence: 12 outcomes and 10 samples after lower casing.</p>')
K.assign('treebank', 'm', 'A Treebank style tokenizer',
         '<p>Write <code>tokenize(sentence)</code> that splits on spaces after these rules: put spaces around , ? ! and : so they become tokens, split a final full stop off the last word, split <code>n\'t</code> off its word (Don\'t → Do n\'t) and split <code>\'s</code> off its word.</p>',
         '''
def tokenize(sentence):
    # your code here
    pass
''', [("tokenize(\"Don't you think, it will rain today?\")", ['Do', "n't", 'you', 'think', ',', 'it', 'will', 'rain', 'today', '?']),
      ("tokenize(\"It's a beautiful day out there in Jodhpur.\")", ['It', "'s", 'a', 'beautiful', 'day', 'out', 'there', 'in', 'Jodhpur', '.']),
      ("tokenize('All work and no play make Dr. jack a dull boy.')", ['All', 'work', 'and', 'no', 'play', 'make', 'Dr.', 'jack', 'a', 'dull', 'boy', '.'])],
         '''
import re

def tokenize(sentence):
    s = re.sub(r"([,?!:])", r" \\1 ", sentence)
    s = re.sub(r"\\.\\s*$", " .", s)
    s = re.sub(r"(\\w)(n't)", r"\\1 \\2", s)
    s = re.sub(r"(\\w)('s)", r"\\1 \\2", s)
    return s.split()
''', 'Use re.sub for each rule, then split. Only the stop at the very end of the string is split, which keeps "Dr." whole.',
         '<p>Your output now matches the three sentences of the notebook word_tokenize output exactly.</p>')
K.assign('vocab', 'm', 'Map words to numbers',
         '<p>Write <code>encode(tokens)</code> that returns <code>[vocab, ids]</code>. <code>vocab</code> maps each new token to the next free index starting at 0, in order of first appearance. <code>ids</code> is the list of indices for the tokens.</p>',
         '''
def encode(tokens):
    # your code here
    pass
''', [("encode(['the', 'cat', 'the'])", [{'the': 0, 'cat': 1}, [0, 1, 0]]), ("encode([])", [{}, []]), ("encode(['a', 'b', 'c', 'b'])[1]", [0, 1, 2, 1])],
         '''
def encode(tokens):
    vocab = {}
    for t in tokens:
        if t not in vocab:
            vocab[t] = len(vocab)
    return [vocab, [vocab[t] for t in tokens]]
''', 'len(vocab) is always the next free index.', '<p>Every model in this course, from an n-gram counter to BERT, starts from exactly this mapping.</p>')

K.must('Pipeline', 'Sentence segmentation, tokenisation, stemming or lemmatisation, POS tagging, counting.')
K.must('Tokens and types', 'Token = an occurrence, type = a distinct word. N() and B() in FreqDist. TTR = V ÷ N falls as text grows.')
K.must('Punkt', 'Unsupervised sentence splitter that learned abbreviations. Kept "Dr. jack" together: 3 sentences in the notebook.')
K.must('Treebank tokens', "Punctuation split off, Don't → Do n't, It's → It 's. 32 tokens for the notebook paragraph against 26 from split().")
K.must('Subwords', 'BPE merges the most frequent adjacent pair again and again, so no word is out of vocabulary.')

T = K.topic(
    slug='tokenisation', topic='tokenisation', step=(2, 'Text as data', 'nlp-text', 'Turn raw text into sentences, tokens, stems, lemmas and counts, exactly as the NLTK notebook does.', 'School and college'),
    title='Sentences, tokens and vocabularies', short='Tokenisation', badge='2.1', minutes=35,
    lead='Cut raw text into sentences and tokens the way NLTK does, see why "Dr." and "Don\'t" need special rules, turn words into numbers, and meet the subword tokens that modern models use.',
    desc='The NLP preprocessing pipeline, tokens and types, sentence segmentation with Punkt, Treebank word tokenisation with the notebook output, vocabularies and word indices, BPE subword tokens and reading files.',
    summary='The preprocessing pipeline, tokens and types, Punkt sentence splitting, Treebank word tokens, vocabularies and BPE subwords.',
    keywords=['tokenisation', 'tokenization', 'sentence segmentation', 'Punkt', 'word_tokenize', 'tokens', 'types', 'vocabulary', 'BPE', 'subword', 'NLTK'],
    recap='<p>Text becomes data in steps: sentences, then tokens, then a vocabulary of types with an index each. The conventions (split punctuation, split contractions, keep abbreviations) decide what gets counted as the same word.</p>')
