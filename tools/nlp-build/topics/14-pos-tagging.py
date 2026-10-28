# Chapter 5.1: part of speech tagging. Source: lecture 9 (activity 3 and the tagsets, the POS deck slides 3 to 9:
# the task, book and can, British Left Waffles on Falkland Islands, types of tagger, look up taggers, generative
# against discriminative models with the Bayes argument, the perceptron and MaxEnt taggers) and problem G10.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('baseline', r'''
# The most frequent tag baseline: remember each word's commonest tag
from collections import Counter, defaultdict
train = [[("I", "PRP"), ("read", "VBP"), ("a", "DT"), ("book", "NN")],
         [("Please", "UH"), ("book", "VB"), ("a", "DT"), ("ticket", "NN")],
         [("We", "PRP"), ("book", "VBP"), ("rooms", "NNS")],
         [("A", "DT"), ("book", "NN"), ("fell", "VBD")]]

seen = defaultdict(Counter)
for sent in train:
    for w, t in sent:
        seen[w][t] += 1
best = {w: c.most_common(1)[0][0] for w, c in seen.items()}
print("book was tagged", dict(seen["book"]), "so the baseline always says", best["book"])
test = ["Please", "book", "a", "room"]
print([(w, best.get(w, "NN")) for w in test])
''')

K.code('backoff', r'''
# A bigram tagger that backs off to a unigram tagger, then to a default tag
from collections import Counter, defaultdict
train = [[("They", "PRP"), ("can", "MD"), ("fish", "VB")],
         [("A", "DT"), ("can", "NN"), ("of", "IN"), ("soda", "NN")],
         [("She", "PRP"), ("can", "MD"), ("dance", "VB")]]
uni, bi = defaultdict(Counter), defaultdict(Counter)
for sent in train:
    prev = "<s>"
    for w, t in sent:
        uni[w][t] += 1
        bi[(prev, w)][t] += 1
        prev = t

def tag(words):
    prev, out = "<s>", []
    for w in words:
        if (prev, w) in bi:
            t, by = bi[(prev, w)].most_common(1)[0][0], "bigram"
        elif w in uni:
            t, by = uni[w].most_common(1)[0][0], "unigram"
        else:
            t, by = "NN", "default"
        out.append((w, t, by))
        prev = t
    return out

print(tag(["A", "can", "of", "fish"]))
''')

K.code('accuracy', r'''
# Tagging accuracy is the share of tokens whose tag matches the gold standard
gold = ["DT", "NN", "VBZ", "NNS", "."]
pred = ["DT", "NN", "NNS", "NNS", "."]
right = sum(g == p for g, p in zip(gold, pred))
print("correct:", right, "of", len(gold), " accuracy:", right / len(gold))
print("errors:", [(i, g, p) for i, (g, p) in enumerate(zip(gold, pred)) if g != p])
''')

K.lesson('task', 'What part of speech tagging is', f'''
<p>Part of speech (POS) tagging gives every word in a sentence its grammatical category: The/DT student/NN reads/VBZ books/NNS. It is usually the first step after tokenisation, and later steps such as chunking, parsing, information extraction and translation lean on it.</p>
<p>How does a person decide? The class found two cues. The first is the word itself: "book" on its own is a noun. The second is the context: in "Please book a ticket", booking is happening, so book is a verb. The professor joked that the class was being unfair to the word by changing its tag, but that is exactly what language does.</p>
{table(['Sentence', 'Word', 'Tag', 'Why'], [
    ['I read a book', 'book', 'noun', 'a thing you read'],
    ['Please book a ticket', 'book', 'verb', 'an action'],
    ['She can dance', 'can', 'modal verb', 'ability'],
    ['A can of soda', 'can', 'noun', 'a container'],
    ['They can fish', 'can', 'verb (or modal)', 'they put fish in cans, or they are able to fish']])}
<h3>A headline with two tag sequences</h3>
{table(['Input', 'British', 'left', 'waffles', 'on', 'Falkland', 'Islands'], [
    ['Reading 1: the political Left is indecisive', 'N', 'N', 'V', 'P', 'N', 'N'],
    ['Reading 2: British people left some waffles', 'N', 'V', 'N', 'P', 'N', 'N']])}
<p>Both sequences are grammatical. Headlines drop the small words ("The British left is waffling") that would normally settle it. The professor: "Such a simple task. POS tagging is indeed very difficult. I pity the poor machines."</p>
{fxs(fx('The problem statement', 'given words <i>W</i> = <i>w</i>₁ … <i>w<sub>n</sub></i>, &nbsp; find tags <i>T̂</i> = argmax<sub><i>T</i></sub> P(<i>T</i> | <i>W</i>)', 'Supervised: train on sentences whose correct tags were added by linguists (a gold standard), then tag new sentences whose tags are hidden. It is classification into one of q tags, done for a whole sequence so the choices interact.', key=True))}
{note('Not every ambiguity is a tagging problem. In "The fisherman sat near the bank", bank is a noun in both readings, river bank and money bank. That is word sense ambiguity, a different task.', 'tip')}
''', kw=['POS tagging', 'part of speech', 'book noun verb', 'can modal', 'British Left Waffles', 'headline', 'sequence tagging', 'gold standard'])

K.lesson('tagsets', 'How many tags are there?', f'''
<p>Asked in class, students said eight or nine. The professor's answer: it depends on the tagset. Finer distinctions give more tags.</p>
{table(['Tagset', 'Tags', 'Examples'], [
    ['Traditional grammar', 'about 8', 'noun, pronoun, verb, adjective, adverb, preposition, conjunction, interjection'],
    ['Universal (Petrov and colleagues, 2012)', '12', 'NOUN, VERB, ADJ, ADV, PRON, DET, ADP, NUM, CONJ, PRT, ".", X'],
    ['Universal Dependencies UPOS', '17', 'adds PROPN, AUX, SCONJ, SYM, INTJ and others'],
    ['Penn Treebank', '45 (46 in NLTK\'s list)', 'NN, NNS, NNP, NNPS, VB, VBD, VBG, VBN, VBP, VBZ, JJ, JJR, JJS, …'],
    ['Brown corpus', 'about 87', 'even finer, with separate tags for forms of be and have']])}
<p>A bigger tagset is harder to predict, since there are more classes, but more useful to later steps such as parsing. NLTK maps Brown and Penn tags to the universal set with <code>tagset="universal"</code>, which is how activity 3 compared them.</p>
{steps('Why tagging is hard but not hopeless', [
    'In the Brown corpus only about 11% of word types are ambiguous (DeRose 1988).',
    'But those types are the frequent ones, such as that, back, down, put and set, so about 40% of word tokens are ambiguous.',
    'Tagging each word with its most frequent tag is already right about 92% of the time.',
    'Models that use context reach 97% and above on the Penn Treebank. The last few percent are the hard cases.'])}
{code('baseline')}
{code('accuracy')}
''', kw=['tagset', 'universal tagset', 'Penn Treebank', 'Brown tagset', 'UPOS', 'ambiguous types', 'most frequent tag baseline', 'accuracy'])

K.lesson('taggers', 'Kinds of tagger', f'''
{table(['Family', 'Examples', 'Idea'], [
    ['Rule based and look up', 'Regular expression tagger, default tagger, unigram and bigram taggers in NLTK', 'Hand rules such as "-ing → VBG", or a table of the commonest tag, backing off when unseen'],
    ['Statistical, generative', 'HMM tagger', 'Model P(W, T) = P(T) P(W | T): tags generate words. Decode with Viterbi.'],
    ['Statistical, discriminative', 'Maximum entropy, perceptron, CRF', 'Model P(T | W) directly from rich features: prefix, suffix, capital letters, neighbouring words and tags'],
    ['Neural', 'BiLSTM CRF, BERT, spaCy, Stanza', 'Learn dense embeddings and read context in both directions']])}
<h3>The look up tagger</h3>
<p>A student asked what "look up" means. It is the same idea as the n-gram tables of step 4: count, then store the answer in a dictionary. A unigram tagger stores each word's most frequent tag. A bigram tagger keys on the previous tag and the word. Chained with backoff, the most specific tagger that has seen the case decides.</p>
{viz('lookup')}
{code('backoff')}
<h3>Discriminative taggers</h3>
<p>The perceptron tagger (Collins 2002) learns from its errors. It reads features of the word, its prefix and suffix, the words before and after, and the previous tags, so it can use clues that a bigram of tags cannot see. NLTK's default <code>pos_tag</code> is an averaged perceptron. A maximum entropy tagger is a log linear classifier, P(t | context) = exp(Σ θ<sub>k</sub> f<sub>k</sub>(t, context)) ÷ Z, with binary features such as "word ends in -ing and tag is VBG". Ratnaparkhi (1996) reached about 96.6% on the Penn Treebank with one.</p>
{note('Whatever tagger you use, do error analysis. Find where it fails, group the errors, then improve. The professor asked students to do activity 3 with their own hands, not with a chatbot: "You will only learn when you do it yourself."', 'tip')}
''', kw=['rule based tagger', 'look up tagger', 'unigram tagger', 'bigram tagger', 'backoff', 'HMM tagger', 'perceptron', 'maximum entropy', 'CRF', 'neural tagger'])

K.lesson('genvsdisc', 'Generative or discriminative', f'''
{fxs(
    fx('Generative', '<i>T̂</i> = argmax<sub><i>T</i></sub> P(<i>W</i>, <i>T</i>) = argmax<sub><i>T</i></sub> P(<i>T</i>) · P(<i>W</i> | <i>T</i>)', 'Learns how tag sequences go and which words each tag produces: a noun tends to produce student, dog, book. "A joint win for both parties."', key=True),
    fx('Discriminative', '<i>T̂</i> = argmax<sub><i>T</i></sub> P(<i>T</i> | <i>W</i>)', 'Learns directly which tags fit these words in this context: reads in "The student reads books" is likely a verb.', key=True))}
{steps('Why both give the same answer', [
    'Bayes: P(T | W) = P(W, T) ÷ P(W).',
    'While we search over tag sequences, the sentence W is fixed, so P(W) is one positive number for every candidate T.',
    'Dividing every score by the same positive number cannot change which is largest.',
    eq('argmax<sub>T</sub> P(T | W) = argmax<sub>T</sub> P(W, T)'),
    'For "they can fish" (chapter 5.3) the best sequence N M V has P(W, T) = 0.05292 and P(T | W) = 0.7233. The ranking of all six non zero sequences is the same under both.'])}
{deep('Is this the same as supervised against unsupervised?', '<p>A student asked exactly this. No: it is a different axis. Both kinds of model can be trained from tagged data, as here. The difference is what is modelled: the joint P(W, T), which can also generate sentences, or only the conditional P(T | W). One practical bonus of the generative HMM is that it can also be trained from untagged text with the Baum-Welch (EM) algorithm, because it models P(W).</p>')}
{ladder(
    '<p>Give every word a label such as noun or verb. The same word can need different labels in different sentences.</p>',
    '<p>Tagsets range from 12 to about 87 tags. Look up taggers with backoff are a strong baseline (about 92%). Generative HMMs model P(W, T), discriminative taggers model P(T | W), and both pick the same best sequence.</p>',
    '<p>The decision is a structured prediction over q<sup>n</sup> sequences. Generative models need few features but strong independence assumptions. Discriminative models such as CRFs normalise over the whole sequence, avoiding the label bias of left to right classifiers.</p>',
    '<p>Neural taggers reach about 97.5 to 98% on the Penn Treebank, close to the agreement between human annotators. Research looks at low resource languages, cross lingual transfer with Universal Dependencies, and what tagging information large language models learn without being taught.</p>')}
''', kw=['generative model', 'discriminative model', 'joint probability', 'conditional probability', 'Bayes', 'argmax', 'Baum-Welch', 'supervised'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In "Please book a ticket", book is a', ['Noun', 'Verb', 'Adjective', 'Preposition'], 1,
       'Is something being done?', 'Booking is happening, so it is a verb.')
K.quiz('e', 'How many tags does the universal tagset have?', ['8', '12', '45', '87'], 1,
       'Petrov and colleagues, 2012.', 'NOUN, VERB, ADJ, ADV, PRON, DET, ADP, NUM, CONJ, PRT, "." and X.')
K.quiz('e', 'Which tagset is the largest?', ['Universal', 'Penn Treebank', 'Brown', 'Traditional'], 2,
       'Finer distinctions, more tags.', 'Brown uses about 87 tags against 45 for the Penn Treebank.')
K.quiz('e', 'A look up unigram tagger stores', ['Every sentence', 'Each word\'s most frequent tag', 'Tag bigrams only', 'Word embeddings'], 1,
       'A dictionary from word to tag.', 'It tags a word with the tag it had most often in training.')
K.quiz('m', 'Why does "She can dance" against "a can of soda" matter for tagging?', ['Spelling', 'The same word needs different tags in different contexts', 'Punctuation', 'Capital letters'], 1,
       'Identity is not enough.', 'Context decides: modal in one, noun in the other.')
K.quiz('m', 'About what share of Brown tokens are ambiguous, although only about 11% of types are?', ['1%', '11%', '40%', '90%'], 2,
       'The ambiguous types are the frequent ones.', 'Frequent words such as that and back are ambiguous, so about 40% of running tokens are.')
K.quiz('m', 'A bigram look up tagger keys its table on', ['The word only', 'The previous tag and the word', 'The next word', 'The sentence length'], 1,
       'Bigram over tags.', 'NLTK\'s BigramTagger uses (previous tag, word).')
K.quiz('m', 'Which model is discriminative?', ['HMM', 'Perceptron tagger', 'Unigram language model', 'Markov chain'], 1,
       'Which models P(T | W) directly?', 'The perceptron scores tags from features of the words.')
K.quiz('h', 'Why can a generative tagger ignore P(W) when choosing tags?', ['P(W) = 1', 'P(W) is the same for every candidate tag sequence', 'P(W) is 0', 'It cannot'], 1,
       'The sentence is fixed.', 'Dividing all candidates by the same positive constant keeps the winner.')
K.quiz('h', '"The fisherman sat near the bank". Will POS tagging resolve the ambiguity?', ['Yes', 'No, bank is a noun in both readings, it is word sense ambiguity', 'Only with a trigram', 'Only in Brown'], 1,
       'Check the tag in both readings.', 'Both readings use a noun, so the tag cannot tell them apart.')
K.quiz('h', 'Generative against discriminative is the same distinction as supervised against unsupervised.', ['True', 'False'], 1,
       'Both kinds can be trained from tagged data.', 'They differ in what is modelled, P(W, T) or P(T | W), not in how they are trained.')
K.quiz('x', 'Which practical advantage does the generative HMM have over a discriminative tagger?', ['Higher accuracy always', 'It can be trained on untagged text with Baum-Welch, since it models P(W)', 'No parameters', 'It needs no tagset'], 1,
       'It models the words too.', 'EM can fit an HMM from raw text because the model assigns probability to the words.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A tagger gets 47 of 50 tokens right. What is its accuracy in percent?', '94', 'Correct ÷ total.',
       ['Correct tokens: 47.', 'Total tokens: 50.', eq('47 ÷ 50 = 0.94 = 94%')], check=94, tol=0.01)
K.calc('e', 'In training, book was tagged NN 5 times, VB 2 times and VBP 1 time. What share of its uses does the unigram tagger get right on this data? Three decimals.', '0.625', 'It always says the most frequent tag.',
       ['Most frequent tag: NN, 5 times.', 'Total uses: 5 + 2 + 1 = 8.', eq('5 ÷ 8 = 0.625')], check=0.625, tol=0.0005)
K.calc('e', 'With 12 tags and 3 words, how many tag sequences are possible?', '1728', 'q to the power T.',
       ['Each word can take any of 12 tags.', 'The choices multiply.', eq('12³ = 1,728')], check=1728, tol=0.5)
K.calc('m', 'In 1,000 tokens, 40% are ambiguous. The baseline gets every unambiguous token right and 80% of the ambiguous ones. What is its accuracy in percent?', '92', 'Add the two groups.',
       ['Unambiguous: 600 tokens, all right.', 'Ambiguous: 400 tokens, 80% right = 320.', eq('(600 + 320) ÷ 1,000 = 92%')], check=92, tol=0.01)
K.calc('m', 'A tagger moves from 92% to 97% accuracy. By what percentage does the error rate fall? Two decimals.', '62.5', 'Errors go from 8% to 3%.',
       ['Old error rate: 8%.', 'New error rate: 3%.', eq('(8 − 3) ÷ 8 = 0.625, a 62.5% cut in errors')], check=62.5, tol=0.01)
K.calc('m', 'P(W, T) for the best tagging of "they can fish" is 0.05292 and P(W) = 0.073164. What is P(T | W)? Four decimals.', '0.7233', 'Bayes.',
       ['P(T | W) = P(W, T) ÷ P(W).', '0.05292 ÷ 0.073164.', eq('= 0.7233')], check=0.05292 / 0.073164, tol=0.0001)
K.calc('m', 'A sentence of 20 tokens is tagged with 2 errors. What is the sentence level tagging accuracy in percent, and is the whole sentence right? Give the percentage.', '90', 'Token accuracy.',
       ['Correct tokens: 18.', '18 ÷ 20 = 0.9.', eq('90%, but the sentence as a whole is not fully correct')], check=90, tol=0.01)
K.calc('h', 'Per token accuracy is 97%. If errors were independent, what is the chance that a 25 token sentence is tagged with no error at all? Three decimals.', '0.467', '0.97 to the power 25.',
       ['Each token is right with probability 0.97.', 'All 25 right: 0.97²⁵.', 'ln 0.97 = −0.030459, times 25 = −0.76148.', eq('e<sup>−0.76148</sup> = 0.467')], check=0.97 ** 25, tol=0.0005)
K.calc('h', 'Second best tagging: P(W, T) = 0.00756 against the best 0.05292. How many times more likely is the best? Two decimals.', '7', 'Ratio of joint probabilities.',
       ['The P(W) factor cancels in the ratio.', '0.05292 ÷ 0.00756.', eq('= 7.00')], check=7, tol=0.01)
K.calc('h', 'Universal tags for 1,390 tokens: NOUN 400, VERB 300, the rest spread out. A tagger that always says NOUN gets what accuracy? Three decimals.', '0.288', 'Share of NOUN tokens.',
       ['Always NOUN is right only on NOUN tokens.', 'NOUN tokens: 400 of 1,390.', eq('400 ÷ 1,390 = 0.288')], check=400 / 1390, tol=0.0005)
K.calc('x', 'With a 45 tag set, how many free parameters does a bigram tag transition table have (rows must sum to 1)?', '1980', 'Each of q rows has q − 1 free values.',
       ['q = 45 rows (previous tag).', 'Each row has 45 entries that sum to 1, so 44 are free.', eq('45 × 44 = 1,980')], check=1980, tol=0.5)

# ---------------------------------------------------------------- assignments
K.assign('mft', 'e', 'The most frequent tag table',
         '<p>Write <code>most_frequent_tags(sents)</code>. sents is a list of sentences, each a list of (word, tag) pairs. Return a dict from each word to the tag it had most often. Break ties by the alphabetically first tag.</p>',
         '''
def most_frequent_tags(sents):
    # your code here
    pass
''', [('most_frequent_tags([[("book", "NN"), ("a", "DT")], [("book", "VB")], [("book", "NN")]])', {'book': 'NN', 'a': 'DT'}),
      ('most_frequent_tags([[("can", "MD")], [("can", "NN")]])', {'can': 'MD'})],
         '''
from collections import Counter, defaultdict

def most_frequent_tags(sents):
    c = defaultdict(Counter)
    for s in sents:
        for w, t in s:
            c[w][t] += 1
    return {w: sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for w, cnt in c.items()}
''', 'Count per word, then sort by count descending and tag ascending.', '<p>The tie break matters in tests. A real tagger would break ties by the overall tag frequency.</p>')
K.assign('backoff', 'm', 'A backoff tagger',
         '<p>Write <code>backoff_tag(sents, words, default)</code>. Build a bigram table keyed on (previous tag, word), with "&lt;s&gt;" as the previous tag at the start, and a unigram table keyed on the word. Tag each word with the bigram answer if seen, else the unigram answer, else default. Use the most frequent tag in each table, ties broken alphabetically. Return the list of tags.</p>',
         '''
def backoff_tag(sents, words, default):
    # your code here
    pass
''', [('backoff_tag([[("I", "PRP"), ("book", "VBP")], [("a", "DT"), ("book", "NN")], [("book", "NN")]], ["I", "book", "it"], "NN")', ['PRP', 'VBP', 'NN']),
      ('backoff_tag([[("a", "DT"), ("book", "NN")]], ["the", "book"], "DT")', ['DT', 'NN'])],
         '''
from collections import Counter, defaultdict

def backoff_tag(sents, words, default):
    uni, bi = defaultdict(Counter), defaultdict(Counter)
    for s in sents:
        prev = "<s>"
        for w, t in s:
            uni[w][t] += 1
            bi[(prev, w)][t] += 1
            prev = t
    pick = lambda c: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    out, prev = [], "<s>"
    for w in words:
        if (prev, w) in bi:
            t = pick(bi[(prev, w)])
        elif w in uni:
            t = pick(uni[w])
        else:
            t = default
        out.append(t)
        prev = t
    return out
''', 'Remember to update the previous tag with the tag you just chose.', '<p>In the first test the unigram alone would say NN for book, but after PRP the bigram table knows VBP.</p>')
K.assign('acc', 'e', 'Accuracy and the confused pairs',
         '<p>Write <code>evaluate(gold, pred)</code> that returns (accuracy rounded to 3 decimals, sorted list of (gold, pred) pairs that were wrong).</p>',
         '''
def evaluate(gold, pred):
    # your code here
    pass
''', [('evaluate(["DT", "NN", "VBZ", "NNS"], ["DT", "NN", "NNS", "NNS"])', (0.75, [('VBZ', 'NNS')])), ('evaluate(["N", "V"], ["N", "V"])', (1.0, []))],
         '''
def evaluate(gold, pred):
    wrong = sorted((g, p) for g, p in zip(gold, pred) if g != p)
    return (round(1 - len(wrong) / len(gold), 3), wrong)
''', 'Zip the two lists and collect the mismatches.', '<p>Listing the confused pairs is the first step of error analysis: VBZ and NNS are both words ending in s.</p>')

K.must('The task', 'Give each word its part of speech. Two cues: the word itself and its context. book: noun or verb. can: modal, noun or verb.')
K.must('Tagsets', 'Traditional about 8, universal 12, UPOS 17, Penn Treebank 45, Brown about 87. More tags, harder but more informative.')
K.must('Ambiguity numbers', 'About 11% of Brown types but 40% of tokens are ambiguous. Most frequent tag baseline about 92%, good taggers 97% and above.')
K.must('Kinds of tagger', 'Look up with backoff, generative HMM (P(W, T)), discriminative MaxEnt, perceptron, CRF (P(T | W)), neural BiLSTM and BERT.')
K.must('Generative and discriminative', 'argmax P(T | W) = argmax P(W, T) because P(W) is fixed. Not the same axis as supervised and unsupervised.')

T = K.topic(
    slug='pos-tagging', topic='postag', step=(5, 'Tagging and syntax', 'nlp-syntax', 'Tag every word with its part of speech using HMMs and Viterbi, mark chunks and names with IOB, and draw constituency and dependency trees.', 'College and masters'),
    title='Part of speech tagging', short='POS tagging', badge='5.1', minutes=40,
    lead='Label every word with its grammatical category, see why the same word needs different labels, and compare look up, generative and discriminative taggers.',
    desc='The tagging task with book, can and the British Left Waffles headline, tagsets from 8 to 87 tags, how much of English is ambiguous, look up taggers chained with backoff, the perceptron and maximum entropy taggers, and why generative and discriminative models choose the same tags.',
    summary='The tagging task, tagsets, ambiguity, look up and backoff taggers, and generative against discriminative models.',
    keywords=['POS tagging', 'tagset', 'Penn Treebank', 'universal tags', 'backoff tagger', 'perceptron', 'generative', 'discriminative'],
    recap='<p>A tagger labels each word with a part of speech using the word and its context. Look up taggers with backoff give a strong baseline. HMMs model how tags and words are generated together, discriminative taggers predict tags from features, and Bayes shows they pick the same best sequence.</p>')
