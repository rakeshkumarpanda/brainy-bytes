# Chapter 2.3: counting words and tags. Source: the NLTK notebook FreqDist cells, the Brown corpus counting cell,
# exercise 1b (top tags in brown.txt and in Brown), exercises 2 and 3 (Penn Treebank words and tags under both
# tagsets), and lecture 9 Q28 on how many POS tags there are. Every count below is copied from the notebook output.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from nlpkit import listing

K = Kit()

K.code('count', r'''
# FreqDist without NLTK: a dictionary from each sample to its count
tokens = ["a", "b", "a", "a", "c", "b", "a"]

counts = {}
for t in tokens:
    counts[t] = counts.get(t, 0) + 1

N = sum(counts.values())                 # outcomes: every token
B = len(counts)                          # samples: distinct types
best = max(counts, key=counts.get)
print(counts)
print("N =", N, " B =", B, " max =", best, " freq(a) =", round(counts["a"] / N, 4))
''')

K.code('tagged', r'''
# A tagged corpus line in Brown format: every token is word/tag
line = "The/at Fulton/np-tl County/nn-tl Grand/jj-tl Jury/nn-tl said/vbd Friday/nr an/at investigation/nn of/in Atlanta's/np$ recent/jj primary/nn election/nn produced/vbd"

tags = {}
for token in line.split():
    word, tag = token.rsplit("/", 1)     # rsplit, because a word itself may contain a slash
    tags[tag] = tags.get(tag, 0) + 1

for tag, c in sorted(tags.items(), key=lambda kv: -kv[1]):
    print(tag, c)
''')

K.code('universal', r'''
# Mapping fine PTB tags to the 12 universal tags merges their counts
TO_UNIVERSAL = {"NN": "NOUN", "NNS": "NOUN", "NNP": "NOUN", "PRP": "PRON", "PRP$": "PRON",
                "VB": "VERB", "VBD": "VERB", "MD": "VERB", "DT": "DET", "IN": "ADP", "TO": "PRT", ".": "."}
tagged = [("A", "DT"), ("villager", "NN"), ("went", "VBD"), ("to", "TO"), ("city", "NN"), ("to", "TO"),
          ("sell", "VB"), ("his", "PRP$"), ("property", "NN"), ("along", "IN"), ("with", "IN"),
          ("his", "PRP$"), ("wife", "NN"), (".", ".")]

fine, coarse = {}, {}
for word, tag in tagged:
    fine[tag] = fine.get(tag, 0) + 1
    u = TO_UNIVERSAL[tag]
    coarse[u] = coarse.get(u, 0) + 1
print("PTB tags:", len(fine), fine)
print("universal tags:", len(coarse), coarse)
''')

K.code('bigrams', r'''
# Counting pairs of neighbours is the first step towards a language model (chapter 4)
words = "<s> I am Sam </s> <s> Sam I am </s> <s> I do not like green eggs and ham </s>".split()

uni, bi = {}, {}
for w in words:
    uni[w] = uni.get(w, 0) + 1
for a, b in zip(words, words[1:]):
    if a != "</s>":                      # do not join the end of one sentence to the next
        bi[(a, b)] = bi.get((a, b), 0) + 1

print("c(I) =", uni["I"], " c(I am) =", bi[("I", "am")])
print("P(am | I) = c(I am) / c(I) =", round(bi[("I", "am")] / uni["I"], 3))
print("P(Sam | <s>) =", round(bi[("<s>", "Sam")] / uni["<s>"], 3))
''')

K.lesson('freqdist', 'Counting with FreqDist', f'''
<p>Almost every method in this course starts by counting. How often does a word occur, how often does a tag occur, how often does one word follow another. NLTK gives you one class for all of it, <code>FreqDist</code>, which is a dictionary from each item to its count with a few helpful extras.</p>
{listing("""from nltk.probability import FreqDist
tokens = ['a', 'b', 'a', 'a', 'c', 'b', 'a']
fdist = FreqDist(tokens)
print(fdist)
print(fdist['a'], fdist['d'], fdist.max())
print(fdist.freq('a'), fdist.N(), fdist.B())""", """<FreqDist with 3 samples and 7 outcomes>
4 0 a
0.5714285714285714 7 3""", title='Python with NLTK, from the notebook (outputs combined)')}
{table(['Call', 'Meaning', 'Value here'], [
    ['fdist[x]', 'Count of x. An unseen item gives 0, not an error', "fdist['a'] = 4, fdist['d'] = 0"],
    ['N()', 'Number of outcomes, which is every token counted', '7'],
    ['B()', 'Number of samples (bins), which is the distinct types', '3'],
    ['freq(x)', 'Relative frequency, count of x divided by N', '4 ÷ 7 = 0.5714'],
    ['max()', 'The most common sample', 'a'],
    ['most_common(k)', 'The k most common samples with counts', "[('a', 4), ('b', 2)] for k = 2"]])}
<p>The words sample and outcome come from probability. Each token is one outcome of an experiment, and each type is a possible sample value. So N() is tokens and B() is types, the two numbers from chapter 2.1.</p>
{fxs(
    fx('Relative frequency', 'freq(<i>x</i>) = ' + frac('c(<i>x</i>)', '<i>N</i>'), 'This is also the maximum likelihood estimate of P(x). Chapter 4 builds language models from exactly this ratio.', key=True),
    fx('Check', '∑<sub><i>x</i></sub> freq(<i>x</i>) = 1', 'The relative frequencies of all samples always add to one, so they form a probability distribution.'))}
{viz('freqdist')}
{code('count')}
<p>The notebook then counted the sentence "This is an example sentence to tell you how this example works". word_tokenize gave 12 tokens with 11 types, because This and this are different strings. After lower casing there were 10 types, since this and example each occur twice.</p>
{note('An item seen once is called a hapax legomenon (Greek for "said once"). In real corpora about half of all types are hapaxes. They are the reason smoothing exists, which is the subject of chapter 4.', 'tip')}
''', kw=['FreqDist', 'frequency distribution', 'counting', 'N()', 'B()', 'freq', 'most_common', 'relative frequency', 'hapax'])

K.lesson('corpora', 'Corpora: Brown and the Penn Treebank', f'''
<p>A corpus is a large, carefully chosen collection of text. A tagged corpus also stores a part of speech tag for every token, added by trained annotators. These tags are the gold standard that taggers learn from and are scored against.</p>
{table(['', 'Brown corpus', 'Penn Treebank (NLTK sample)'], [
    ['Source', '500 samples of American English printed in 1961, from 15 genres such as news, fiction and science', 'Wall Street Journal news articles'],
    ['Built by', 'Francis and Kučera at Brown University', 'Marcus, Santorini and Marcinkiewicz at the University of Pennsylvania (1993)'],
    ['Tokens in NLTK', '1,161,192', '100,676'],
    ['Types', '56,057', '12,408'],
    ['Most common word', 'the (62,713 times, 5.40%)', ', (4,885 times). the is second with 4,045 (4.02%)'],
    ['Distinct tags', '472 (compound tags counted separately)', '46 PTB tags, or 12 universal tags']])}
<h3>What tagged text looks like</h3>
{listing("""from nltk.corpus import brown
print(brown.tagged_sents()[0][:8])
print(brown.tagged_sents(tagset='universal')[0][:8])""", """[('The', 'AT'), ('Fulton', 'NP-TL'), ('County', 'NN-TL'), ('Grand', 'JJ-TL'), ('Jury', 'NN-TL'), ('said', 'VBD'), ('Friday', 'NR'), ('an', 'AT')]
[('The', 'DET'), ('Fulton', 'NOUN'), ('County', 'NOUN'), ('Grand', 'ADJ'), ('Jury', 'NOUN'), ('said', 'VERB'), ('Friday', 'NOUN'), ('an', 'DET')]""", title='Python with NLTK, from the notebook (first eight tokens shown)')}
<p>On disk the class file brown.txt stores the same thing as text, one word/tag token after another: <code>The/at Fulton/np-tl County/nn-tl</code>. The suffix -tl marks a word in a title, so nn-tl is a common noun that is part of a name such as "Grand Jury".</p>
{code('tagged')}
{viz('tagcount')}
<h3>Why Brown and PTB look different</h3>
<ul>
<li><b>Size.</b> Brown in NLTK is more than eleven times larger, so it has more types (56,057 against 12,408).</li>
<li><b>Genre.</b> PTB is financial news, full of numbers and company names. Brown mixes fifteen genres.</li>
<li><b>Empty elements.</b> PTB inserts placeholder tokens such as *-1 and 0 that mark moved or missing words in its syntax trees. They are tagged -NONE-. There are 6,592 of them, so only 94,084 tokens are real words, and two of the top ten "words" are placeholders.</li>
<li><b>Commas.</b> In PTB the comma (4,885) beats the (4,045). Business writing uses many lists and clauses.</li>
</ul>
{note('Exam questions often ask you to "verbally describe how the results differ". Mention size, genre, tagset and the -NONE- tokens, and back each point with one number.', 'exam')}
''', kw=['corpus', 'Brown corpus', 'Penn Treebank', 'PTB', 'tagged corpus', 'gold standard', '-NONE-', 'empty element', 'word/tag'])

K.lesson('tagsets', 'How many tags? Tagsets', f'''
<p>A student in lecture 9 answered "eight, sir" when asked how many parts of speech there are. The professor's answer: it depends on the tagset. Finer distinctions mean more tags.</p>
{table(['Tagset', 'Size', 'Example distinctions'], [
    ['Traditional grammar', '8', 'noun, pronoun, verb, adjective, adverb, preposition, conjunction, interjection'],
    ['Universal (Petrov et al., 2012)', '12', 'NOUN VERB ADJ ADV PRON DET ADP NUM CONJ PRT . X'],
    ['Universal Dependencies UPOS', '17', 'adds PROPN, AUX, SCONJ, SYM, INTJ, PUNCT'],
    ['Penn Treebank', '45', 'NN NNS NNP NNPS, VB VBD VBG VBN VBP VBZ, JJ JJR JJS, RB RBR RBS'],
    ['Brown', 'about 87 base tags', 'plus compound forms such as NN-TL and NP$, which is why NLTK counts 472']])}
<h3>Coarse and fine</h3>
<p>A fine tagset can be mapped to a coarse one, never the other way. The notebook checked this on PTB adverbs:</p>
{fxs(
    fx('Merging tags adds their counts', 'c(ADV) = c(RB) + c(RBR) + c(RBS) + c(WRB)', 'Every universal tag count is the sum of the PTB tags mapped to it.', key=True),
    fx('Notebook numbers', '3,171 = 2,822 + 136 + 35 + 178', 'RB does not exist in the universal tagset, so fdist["RB"] gave 0 there.'))}
{listing("""fdist_univ_tag = FreqDist(tag for (word, tag) in treebank.tagged_words(tagset='universal'))
print(sorted(fdist_univ_tag.keys()))
print(fdist_univ_tag.most_common(4))""", """['.', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM', 'PRON', 'PRT', 'VERB', 'X']
[('NOUN', 28867), ('VERB', 13564), ('.', 11715), ('ADP', 9857)]""")}
{code('universal')}
<h3>Which tagset should you use</h3>
{table(['Fine tagset (PTB, Brown)', 'Coarse tagset (universal)'], [
    ['More information: singular or plural, past or present', 'Less information'],
    ['Harder to tag, because there are more classes to confuse', 'Easier and more accurate'],
    ['Useful for parsing and grammar checking', 'Useful across languages, since the same 12 tags fit most languages']])}
{scene('a grammar checker for job applications', '<p>A tool flags "She have worked here for two years". It needs to know that She is third person singular and that have is a base form verb (VBP) where VBZ (has) is required. The universal tag VERB hides that difference, so this tool must use a fine tagset like PTB.</p>')}
{deep('Tags and ambiguity in numbers', '<p>Jurafsky and Martin report that in Brown only about 11 percent of word types can take more than one tag, but they are the common words, so about 40 percent of tokens are ambiguous. Always choosing the most frequent tag for each word is right about 92 percent of the time. Context based taggers in chapter 5 push this past 97 percent.</p>')}
''', kw=['tagset', 'universal tagset', 'Penn Treebank tagset', 'Brown tagset', 'UPOS', 'coarse', 'fine', 'tag mapping', 'ADV', 'RB'])

K.lesson('sequences', 'Counting pairs: towards language models', f'''
<p>So far we counted single items. Counting pairs of neighbouring words, called bigrams, is the small step that turns counting into prediction. If "I am" occurs 2 times and "I" occurs 3 times, then after "I" the next word was "am" two times out of three.</p>
{code('bigrams')}
{fxs(
    fx('Bigram probability by counting', 'P(<i>w</i><sub><i>i</i></sub> | <i>w</i><sub><i>i</i>−1</sub>) = ' + frac('c(<i>w</i><sub><i>i</i>−1</sub> <i>w</i><sub><i>i</i></sub>)', 'c(<i>w</i><sub><i>i</i>−1</sub>)'), 'The maximum likelihood estimate. Chapter 4 explains why it fails for pairs never seen.', key=True),
    fx('Most frequent tag baseline', 'tag(<i>w</i>) = argmax<sub><i>t</i></sub> c(<i>w</i>, <i>t</i>)', 'Counting word and tag pairs gives the simplest tagger. Chapter 5 adds context.'))}
{steps('Using counts to answer a question from the notebook', [
    'Question: what share of PTB tokens are nouns of any kind?',
    'Under the universal tagset, NOUN = 28,867.',
    eq('28,867 ÷ 100,676 ≈ 0.2867 = 28.67%'),
    'Under the PTB tagset you would add NN, NNS, NNP and NNPS, which gives the same total because they all map to NOUN.'])}
{ladder(
    '<p>Counting tells you which words and tags are common. Dividing a count by the total gives a share, which is a probability.</p>',
    '<p>FreqDist stores counts, N() is tokens and B() is types. Relative frequency is the maximum likelihood estimate. Tagged corpora like Brown and PTB give counts of words, tags and word tag pairs, and tagsets range from 12 to about 87 base tags.</p>',
    '<p>Counts from a sample estimate a population distribution. The estimate is unbiased for frequent items but unreliable for rare ones, and gives zero to anything unseen. Good Turing and Kneser Ney smoothing (chapter 4) correct this. Corpus design (balance across genres, as in Brown) decides which population the counts represent.</p>',
    '<p>Modern corpora reach trillions of tokens, and counting itself becomes a systems problem: count min sketches, suffix arrays and infini-gram style indices return n-gram counts over web scale text. Research also studies dataset documentation, contamination of test sets inside training data, and how tagset design affects cross lingual transfer.</p>')}
''', kw=['bigram', 'counting pairs', 'maximum likelihood', 'most frequent tag', 'language model', 'conditional probability'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'For tokens a b a a c b a, what does FreqDist print?', ['<FreqDist with 7 samples and 3 outcomes>', '<FreqDist with 3 samples and 7 outcomes>', '<FreqDist with 4 samples and 7 outcomes>', '<FreqDist with 3 samples and 4 outcomes>'], 1,
       'Samples are types, outcomes are tokens.', 'Three distinct items (a, b, c) and seven tokens.')
K.quiz('e', "What does fdist['d'] return when d was never seen?", ['An error', 'None', '0', '-1'], 2,
       'FreqDist is a Counter.', 'Unseen samples have count 0.')
K.quiz('e', 'Which is the most frequent word in the NLTK Brown corpus?', ['of', 'the', ',', 'and'], 1,
       'It is over 5% of all tokens.', 'the, with 62,713 occurrences.')
K.quiz('e', 'What is the most frequent "word" in the NLTK Penn Treebank sample?', ['the', ',', '.', 'of'], 1,
       'Punctuation counts as a token.', 'The comma, 4,885 times, ahead of the with 4,045.')
K.quiz('m', 'What does the tag nn-tl in brown.txt mean?', ['A plural noun', 'A common noun inside a title or name', 'A noun used as a verb', 'A noun at the end of a line'], 1,
       'Look at "Grand Jury".', 'The -tl suffix marks words that are part of a title.')
K.quiz('m', "Why does fdist['RB'] give 0 under the universal tagset?", ['PTB has no adverbs', 'Universal tags merge RB, RBR, RBS and WRB into ADV', 'RB is a typo', 'Adverbs were removed'], 1,
       'Different tag names.', 'The universal tagset has only ADV, with count 3,171.')
K.quiz('m', 'What are tokens like *-1 and 0 in the Penn Treebank?', ['Numbers', 'Empty elements tagged -NONE-, marking moved or missing words', 'Typos', 'Punctuation'], 1,
       'Their tag is -NONE-.', 'They are placeholders in the syntax trees and not real words.')
K.quiz('m', 'How many tags does the universal tagset have?', ['8', '12', '45', '87'], 1,
       'Petrov et al. 2012.', 'NOUN VERB ADJ ADV PRON DET ADP NUM CONJ PRT . X.')
K.quiz('h', 'Why does NLTK count 472 distinct Brown tags when Brown has about 87 base tags?', ['Annotation errors', 'Compound forms such as NN-TL and NP$ count as separate tags', 'It includes PTB tags', 'Lower and upper case'], 1,
       'Look at the tags on "Fulton County Grand Jury".', 'Suffixes like -TL, -HL and $ combine with base tags into many distinct strings.')
K.quiz('h', 'A grammar checker must spot "She have". Which tagset is needed?', ['Universal', 'A fine tagset like PTB that separates VBP and VBZ', 'No tagset', 'Traditional 8'], 1,
       'The error is about person and number.', 'Universal VERB hides the difference between have (VBP) and has (VBZ).')
K.quiz('h', 'FreqDist.freq(x) is the maximum likelihood estimate of', ['The number of types', 'P(x)', 'The tag of x', 'The rank of x'], 1,
       'Count divided by total.', 'c(x) / N is the MLE of the probability of x.')
K.quiz('x', 'Brown has 56,057 types in 1,161,192 tokens. PTB has 12,408 in 100,676. Why is the PTB type token ratio higher?', ['PTB is more varied', 'Smaller corpora have higher TTR because new types are still appearing quickly', 'PTB is lower cased', 'Brown removed rare words'], 1,
       'TTR falls as N grows.', 'TTR is not comparable across corpora of different sizes. Heaps\' law says V grows slower than N.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'For tokens a b a a c b a, what is freq(a)? Give four decimals.', '0.5714', 'Count of a over all tokens.',
       ['c(a) = 4.', 'N = 7.', eq('4 ÷ 7 ≈ 0.5714')], check=4 / 7, tol=0.00005)
K.calc('e', 'What percentage of Brown tokens is "the"? Give two decimals.', '5.40', 'c(the) ÷ N × 100.',
       ['c(the) = 62,713.', 'N = 1,161,192.', eq('62,713 ÷ 1,161,192 × 100 ≈ 5.40%')], check=100 * 62713 / 1161192, tol=0.005)
K.calc('e', 'How many real word tokens does the PTB sample have after removing -NONE- tokens?', '94084', 'Subtract the placeholders.',
       ['Total tokens = 100,676.', 'Tokens tagged -NONE- = 6,592.', eq('100,676 − 6,592 = 94,084')], check=94084)
K.calc('m', 'Check the notebook: RB 2,822, RBR 136, RBS 35, WRB 178. What is the universal ADV count?', '3171', 'Add the four.',
       ['2,822 + 136 = 2,958.', '2,958 + 35 = 2,993.', eq('2,993 + 178 = 3,171'), 'This matches fdist_univ_tag[\'ADV\'].'], check=3171)
K.calc('m', 'What share of PTB tokens carry the universal tag NOUN? Give a percentage to two decimals.', '28.67', 'NOUN count over all tokens.',
       ['NOUN = 28,867.', 'N = 100,676.', eq('28,867 ÷ 100,676 × 100 ≈ 28.67%')], check=100 * 28867 / 100676, tol=0.005)
K.calc('m', 'What is the type token ratio of the NLTK Brown corpus? Give four decimals.', '0.0483', 'Types ÷ tokens.',
       ['V = 56,057.', 'N = 1,161,192.', eq('56,057 ÷ 1,161,192 ≈ 0.0483')], check=56057 / 1161192, tol=0.00005)
K.calc('m', 'What is the type token ratio of the PTB sample? Give four decimals.', '0.1232', 'Types ÷ tokens.',
       ['V = 12,408.', 'N = 100,676.', eq('12,408 ÷ 100,676 ≈ 0.1232'), 'More than twice the Brown value, because PTB is about eleven times smaller.'], check=12408 / 100676, tol=0.00005)
K.calc('h', 'In brown.txt (2,242 tokens) the top 10 tags have counts 327, 217, 203, 119, 105, 88, 87, 87, 82 and 75. What percentage of tokens do they cover? One decimal.', '62.0', 'Add the counts, then divide.',
       ['Sum = 327 + 217 + 203 + 119 + 105 + 88 + 87 + 87 + 82 + 75 = 1,390.', eq('1,390 ÷ 2,242 ≈ 0.620'), 'So 10 of the 84 tags cover 62 percent of tokens.'], check=100 * 1390 / 2242, tol=0.05)
K.calc('h', 'NN is 327 of 2,242 tokens in brown.txt and 152,470 of 1,161,192 in the full Brown corpus. What is the difference in percentage points? Two decimals.', '1.45', 'Compute both shares.',
       ['brown.txt: 327 ÷ 2,242 ≈ 14.59%.', 'Brown: 152,470 ÷ 1,161,192 ≈ 13.13%.', eq('14.59 − 13.13 ≈ 1.45 points'), 'A small sample already shows the same pattern as the full corpus.'], check=100 * (327 / 2242 - 152470 / 1161192), tol=0.01)
K.calc('h', 'In "<s> I am Sam </s> <s> Sam I am </s> <s> I do not like green eggs and ham </s>", what is P(am | I)? Three decimals.', '0.667', 'c(I am) ÷ c(I).',
       ['c(I) = 3.', 'c(I am) = 2.', eq('P(am | I) = 2 ÷ 3 ≈ 0.667')], check=2 / 3, tol=0.0005)
K.calc('x', 'A tagger always picks the most frequent tag and is right 92% of the time. On 100,676 tokens, how many errors is that, to the nearest whole number?', '8054', 'Errors = (1 − accuracy) × N.',
       ['Error rate = 0.08.', eq('0.08 × 100,676 = 8,054.08'), 'About 8,054 wrong tags. A 97% tagger makes about 3,020.'], check=8054, tol=0.5)

# ---------------------------------------------------------------- assignments
K.assign('fdist', 'e', 'Your own FreqDist',
         '<p>Write <code>summary(tokens, x)</code> that returns <code>[N, B, most, freq]</code>: the number of tokens, the number of distinct tokens, the most common token (the first one seen wins a tie) and the relative frequency of <code>x</code> rounded to 4 decimals.</p>',
         '''
def summary(tokens, x):
    # your code here
    pass
''', [("summary(['a', 'b', 'a', 'a', 'c', 'b', 'a'], 'a')", [7, 3, 'a', 0.5714]), ("summary(['x', 'y'], 'z')", [2, 2, 'x', 0.0]),
      ("summary('this is an example sentence to tell you how this example works'.split(), 'example')", [12, 10, 'this', 0.1667])],
         '''
def summary(tokens, x):
    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    most = None
    for t in counts:
        if most is None or counts[t] > counts[most]:
            most = t
    return [len(tokens), len(counts), most, round(counts.get(x, 0) / len(tokens), 4)]
''', 'A dictionary keeps insertion order, so a strict greater than comparison keeps the first item on ties.',
         '<p>The first test is the notebook list. The last one is the notebook sentence after lower casing: 12 outcomes and 10 samples.</p>')
K.assign('tags', 'm', 'Top tags from a tagged file',
         '<p>Write <code>top_tags(text, k)</code>. text is Brown style word/tag tokens separated by spaces. Split each token at its last slash, count the tags, and return the k most common as a list of <code>[tag, count]</code> pairs, highest first, ties in order of first appearance.</p>',
         '''
def top_tags(text, k):
    # your code here
    pass
''', [("top_tags('The/at jury/nn said/vbd the/at jury/nn left/vbd ./.', 2)", [['at', 2], ['nn', 2]]),
      ("top_tags('1/2/cd cups/nns', 1)", [['cd', 1]]),
      ("top_tags('a/at b/nn c/nn', 3)", [['nn', 2], ['at', 1]])],
         '''
def top_tags(text, k):
    counts = {}
    for tok in text.split():
        tag = tok.rsplit("/", 1)[1]
        counts[tag] = counts.get(tag, 0) + 1
    order = sorted(counts.items(), key=lambda kv: -kv[1])
    return [[t, c] for t, c in order[:k]]
''', 'sorted is stable, so items with equal counts keep their first appearance order.',
         '<p>The second test is why the notebook used rsplit: the word 1/2 itself contains a slash.</p>')
K.assign('merge', 'm', 'Map fine tags to universal tags',
         '<p>Write <code>to_universal(counts, mapping)</code>. counts maps PTB tags to counts. mapping maps PTB tags to universal tags. Return a dictionary of universal tag counts. A PTB tag missing from mapping goes to X.</p>',
         '''
def to_universal(counts, mapping):
    # your code here
    pass
''', [("to_universal({'RB': 2822, 'RBR': 136, 'RBS': 35, 'WRB': 178}, {'RB': 'ADV', 'RBR': 'ADV', 'RBS': 'ADV', 'WRB': 'ADV'})", {'ADV': 3171}),
      ("to_universal({'NN': 5, 'VB': 2, 'FW': 1}, {'NN': 'NOUN', 'VB': 'VERB'})", {'NOUN': 5, 'VERB': 2, 'X': 1}),
      ("to_universal({}, {})", {})],
         '''
def to_universal(counts, mapping):
    out = {}
    for tag, c in counts.items():
        u = mapping.get(tag, "X")
        out[u] = out.get(u, 0) + c
    return out
''', 'Look up each fine tag and add its count to the coarse bucket.', '<p>The first test reproduces the notebook check 2,822 + 136 + 35 + 178 = 3,171.</p>')

K.must('FreqDist', 'N() = tokens (outcomes), B() = types (samples), freq(x) = c(x)/N, unseen count = 0. a b a a c b a gives 3 samples, 7 outcomes, freq(a) = 0.5714.')
K.must('Brown numbers', '1,161,192 tokens, 56,057 types, the = 62,713 (5.40%). 472 distinct tags, top tag NN 152,470.')
K.must('PTB numbers', '100,676 tokens, 12,408 types, comma is most common (4,885), the 4,045 (4.02%). 6,592 -NONE- tokens.')
K.must('Tagsets', '8 traditional, 12 universal, 17 UPOS, 45 PTB, about 87 Brown. Fine maps to coarse: ADV 3,171 = RB + RBR + RBS + WRB.')
K.must('Bigram counts', 'P(w | prev) = c(prev w) / c(prev). From I am Sam: P(am | I) = 2/3.')

T = K.topic(
    slug='counting-corpora', topic='counting', step=(2, 'Text as data', 'nlp-text', 'Turn raw text into sentences, tokens, stems, lemmas and counts, exactly as the NLTK notebook does.', 'School and college'),
    title='Counting words and tags', short='Counting corpora', badge='2.3', minutes=35,
    lead='Count tokens, types and tags with FreqDist, read the Brown corpus and the Penn Treebank as the notebook did, and see how the choice of tagset changes every number.',
    desc='FreqDist and its methods, relative frequency as maximum likelihood, the Brown and Penn Treebank corpora with the real notebook counts, tagged text formats, tagsets from 8 to 87 tags, mapping PTB to universal tags, and counting bigrams.',
    summary='FreqDist, the Brown corpus and the Penn Treebank with real counts, tagsets and tag mapping, and the first bigram probabilities.',
    keywords=['FreqDist', 'Brown corpus', 'Penn Treebank', 'tagset', 'universal tagset', 'POS tags', 'counting', 'bigram', 'NLTK'],
    recap='<p>Counting turns text into numbers. FreqDist gives tokens, types and relative frequencies. The Brown corpus and the Penn Treebank differ in size, genre and tagset, and fine tags can always be merged into coarse ones by adding their counts.</p>')
