# Chapter 1.1: what language is. Source: lecture 1 (definition, six levels, symbolic and interactive functions, the
# semiotic triangle, four realities, the speaker and hearer chain, Zipf and Grice) and the start of lecture 2
# (recursion, matrix and embedded clauses, the Piraha debate).
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('morph', r'''
# Split a word into prefix, root and suffixes with a small list of English affixes
PREFIXES = ["un", "dis", "re", "in"]
SUFFIXES = ["ness", "ful", "ing", "ed", "s"]

def split(word):
    parts = []
    for p in PREFIXES:
        if word.startswith(p) and len(word) > len(p) + 2:
            parts.append(p + "-")
            word = word[len(p):]
            break
    tail = []
    changed = True
    while changed:
        changed = False
        for s in SUFFIXES:
            if word.endswith(s) and len(word) > len(s) + 2:
                tail.insert(0, "-" + s)
                word = word[:-len(s)]
                changed = True
                break
    if word.endswith("i"):              # happi -> happy, the spelling rule y -> i
        word = word[:-1] + "y"
    return parts + [word] + tail

for w in ["unhappiness", "distaste", "cats", "replaying"]:
    print(w, "->", split(w))
''')

K.code('truth', r'''
# The lecture conditional: "If it rains tomorrow, then I will not go to class"
# P = it rains, Q = I skip class. P -> Q is false only when P is true and Q is false.
def implies(p, q):
    return (not p) or q

print("P      Q      P -> Q")
for p in [True, False]:
    for q in [True, False]:
        print(f"{p!s:6} {q!s:6} {implies(p, q)}")
''')

K.code('nest', r'''
# Recursion in grammar: a clause can hold another clause, which can hold another
def nest(clauses):
    if len(clauses) == 1:                # the innermost clause stops the recursion
        return clauses[0]
    return clauses[0] + " that " + nest(clauses[1:])

parts = ["John said", "Mary thought", "Tom knew", "Ravi had left"]
for depth in range(1, len(parts) + 1):
    print(depth, ":", nest(parts[:depth]))
''')

K.lesson('definition', 'What language is', f'''
<p>Ask a class "what is language?" and you get many true but partial answers: a medium of communication, a reflection of thought, words in a grammatical order, a script of symbols. The lecture puts the pieces together into one working definition that the whole course uses.</p>
{fx('Working definition from the lecture', 'Language is a <b>systematic, symbolic and structured</b> system that (1) starts as thought in the mind, (2) organises chaotic ideas into structure, and (3) lets those ideas be sent out, carried and rebuilt in another mind.', 'Every later topic in this course, from tokens to parse trees, is a way of recovering some part of this structure from text.', key=True)}
<h3>From an idea to an utterance</h3>
<p>The professor traced every sentence back to the mind with a simple chain: an idea forms, you conceptualise it, you articulate it, and you say it as a form (a sound, written letters or a sign). Keep this chain in mind. The lecture uses it three times, for one word, for a full conversation and for the origin of speech.</p>
<h3>A window to the mind</h3>
<p>Language does two jobs at once. It <b>reflects</b> the patterns of our thought, so studying how people build sentences gives indirect evidence of how they think. That is why linguistics is treated as a cognitive science. It also <b>organises</b> thought. Close your eyes for a minute and your raw thoughts overlap and drift. Language imposes order on them, and structure is what turns a pile of words into a claim that can be true or false.</p>
{note('Structure creates meaning. "Dog bites man" and "man bites dog" use the same three words. A bag of words model that ignores order cannot tell them apart, which is why later chapters bother with tags, n-grams and parse trees.', 'tip')}
<h3>Two questions you can ask about language</h3>
{table(['Question', 'What it needs', 'Where it leads'], [
    ['How do I manipulate this string of words?', 'String operations, patterns, counts and probabilities', 'Statistical NLP: n-gram models, classifiers and today the next word prediction of large language models'],
    ['What kind of system could produce this behaviour?', 'A theory of the representations and rules inside a mind or machine', 'Symbolic NLP, formal grammars and the cognitive science side of linguistics']])}
<p>The modern twist is that large language models are trained only on the first question, predicting the next token, yet they show behaviour that looks like the second. Whether that means they understand is one of the open questions of this course.</p>
''', kw=['what is language', 'definition of language', 'systematic symbolic structured', 'idea conceptualise articulate', 'window to the mind', 'structure creates meaning', 'two questions'])

K.lesson('six-levels', 'The six levels of linguistic structure', f'''
<p>This is the backbone of the course. Each level combines the units of the level below it. Sounds combine into words, words into sentences, sentences carry a literal meaning, and context decides what the speaker meant.</p>
{table(['Level', 'Unit studied', 'Question it answers', 'Example'], [
    ['Phonetics', 'Raw speech sounds', 'How are sounds produced, carried and heard?', '[k] is made by stopping air at the back of the mouth with no voice'],
    ['Phonology', 'Phonemes, the sound system', 'Which sound differences change meaning in this language?', '/p/ against /b/ turns "pat" into "bat"'],
    ['Morphology', 'Words and word parts', 'How are words built from meaningful parts?', 'dis + taste = distaste'],
    ['Syntax', 'Phrases and sentences', 'How do words combine into sentences?', '"The cat jumped" is subject then verb'],
    ['Semantics', 'Literal meaning', 'What does the sentence mean on its own?', '"The cat jumped" names a jumping event done by a cat'],
    ['Pragmatics', 'Meaning in context', 'What does the speaker intend here and now?', '"I sat near a bank": river or money?']])}
{viz('levels')}
<h3>Phonetics against phonology</h3>
<p>The lecture used the two words almost as one, but exams like to separate them. <b>Phonetics</b> is the physics and biology of speech sounds and is the same for every language. <b>Phonology</b> is the mental sound system of one language: which differences matter. English treats the breathy p in "pin" and the plain p in "spin" as one phoneme. Hindi treats प and फ as two different phonemes, so the same physical difference changes meaning in one language and not in the other.</p>
<h3>Morphology in more detail</h3>
<ul>
<li>A <b>morpheme</b> is the smallest unit that carries meaning or a grammatical job. It is not a syllable: "cats" has two morphemes (cat + s) but one syllable.</li>
<li>A <b>free</b> morpheme stands alone (taste, cat, run). A <b>bound</b> morpheme must attach to something (dis-, -s, -ing, -ness).</li>
<li>Affixes by position: <b>prefix</b> before the root (dis-taste), <b>suffix</b> after (taste-ful), <b>infix</b> inside (common in Tagalog, rare in English), <b>circumfix</b> on both sides at once (German ge-lob-t, praised).</li>
</ul>
{code('morph')}
<p>Stemming and lemmatisation, which you meet in chapter 2.2, are computer approximations of exactly this analysis. The small program above shows both the idea and its weakness: the length rules stop it from cutting "ring" to "r", but a fixed list of affixes still cuts "bless" to "bles", and spelling changes like happy to happi need extra rules.</p>
{ladder(
    '<p>Language is built in layers, like letters into words and words into sentences. Sounds make words, words make sentences, and sentences mean something. On top of that, the situation tells you what the person really wanted to say.</p>',
    '<p>The six levels are phonetics, phonology, morphology, syntax, semantics and pragmatics. A useful test: if a change in sound alters meaning, that is phonology. If the problem is word order, it is syntax. If the sentence is well formed but the meaning is odd, it is semantics. If you need the situation, it is pragmatics.</p>',
    '<p>NLP systems map onto these levels. Speech recognition works at the phonetic and phonological levels, tokenisers and stemmers at the morphological level, taggers and parsers at the syntactic level, semantic role labellers and entailment models at the semantic level, and dialogue systems at the pragmatic level. Errors propagate upward, which is why pipeline systems were replaced by joint models.</p>',
    '<p>The levels are not sealed. Prosody (a phonological property) changes pragmatic meaning, morphology and syntax trade off across languages (rich case marking allows free word order, as in Hindi), and neural models learn representations whose layers loosely track these levels, which probing studies try to measure. Whether such models need explicit linguistic structure is an open research question.</p>')}
''', kw=['six levels', 'phonetics', 'phonology', 'morphology', 'syntax', 'semantics', 'pragmatics', 'phoneme', 'morpheme', 'free morpheme', 'bound morpheme', 'prefix', 'suffix', 'infix', 'circumfix'])

K.lesson('symbolic', 'The symbolic function: words stand for concepts', f'''
<p>The lecture splits what language does into two functions. The <b>symbolic function</b> lets words stand for objects, events and ideas, even when those things are not present. The <b>interactive function</b> lets two minds coordinate, which is the next lesson.</p>
<p>Symbols come in many sizes: a bound morpheme like dis-, a whole word like cat, or a full proposition such as "If it rains tomorrow, then I will not go to class", which can itself be agreed with or denied.</p>
{fx('The key claim', 'Language does not directly represent the external world. It represents our <b>conceptualised experience</b> of the world.', 'Say "leopard" in a classroom. No leopard appears, yet everyone understands, because the word calls up a concept that speaker and listener already share.', key=True)}
<h3>World, percept, concept, meaning, form</h3>
<p>For one word the lecture traces this pipeline. A real cat exists. Your senses register its shape and colour (percept). Your brain matches that to a stored concept of a small four legged pet (concept). The concept links both ways to a meaning your community agreed on (linguistic meaning). Finally that meaning is packed into a form, the sound [kæt] or the letters c, a, t. The brackets mark the International Phonetic Alphabet, where each symbol stands for exactly one sound.</p>
{viz('triangle')}
<p>The diagram has a name: the <b>semiotic triangle</b> of Ogden and Richards (1923). Its bottom edge is dashed on purpose. A word is linked to the world only through a concept in a mind. The $ sign means money only because a community agreed on that pairing, a <b>convention</b>, not because its shape looks like money.</p>
<h3>Four kinds of reality that grammar can encode</h3>
{table(['Reality', 'Example from the lecture', 'How grammar marks it'], [
    ['Present', 'The cat is sleeping.', 'Present tense with progressive aspect (is + verb + ing)'],
    ['Past', 'The cat was sleeping.', 'Past tense with progressive aspect (was + verb + ing)'],
    ['Imagined', 'Imagine a cat flying over the moon.', 'Irrealis mood, signalled by "imagine"'],
    ['Abstract', 'Justice is important.', 'A property turned into a noun with no physical referent']])}
<p>Linguists call this machinery <b>TAM</b>: tense (when), aspect (ongoing or completed) and mood (fact or hypothesis). A word like unicorn has meaning without a real referent because its concept is built from parts that do have referents. Frege called this having a sense without a reference.</p>
<h3>A sentence as a logical symbol</h3>
<p>Write P = "it rains tomorrow" and Q = "I will not go to class". The sentence has the form P → Q. The promise is broken only when it rains and you go to class anyway.</p>
{code('truth')}
{note('Listeners usually also infer "if it does not rain, I will go", which the logic does not say. This gap between logical form and everyday meaning is one reason formal logic alone could not solve language understanding.', 'warn')}
''', kw=['symbolic function', 'form meaning pair', 'semiotic triangle', 'Ogden and Richards', 'percept concept meaning form', 'IPA', 'convention', 'TAM', 'tense aspect mood', 'sense and reference', 'material conditional'])

K.lesson('interactive', 'The interactive function: from one mind to another', f'''
<p>"Let's meet tomorrow!" packs a time limit, a proposal and a request for agreement into three words. The lecture calls this <b>quick and effective expression</b>, and it is the interactive function at work. For any message you need two roles: a speaker who encodes an idea and a hearer who decodes it.</p>
{fx('The communication chain', 'Thought → linguistic representation → signal → linguistic representation → reconstructed thought', 'The first and last boxes are different. Communication never copies a thought. It only gives the hearer enough to rebuild an approximation.', key=True)}
<p>The professor called this a <b>two body problem</b>. A speaker has to model not only their own idea but also what the listener already knows. The same picture appears in engineering as the Shannon Weaver model (source, transmitter, channel with noise, receiver, destination). Shannon wrote that meaning was irrelevant to his engineering problem. A course on language understanding has to put meaning back in.</p>
<h3>The effort against clarity trade off</h3>
<p>Speakers save effort with short phrases, listeners need enough detail to understand. Two classic ideas formalise this balance.</p>
{fxs(
    fx('Zipf: least effort', '<i>f</i>(<i>r</i>) ≈ ' + frac('<i>C</i>', '<i>r</i><sup>α</sup>') + ', α ≈ 1', 'A few short words such as "the" are used constantly. Thousands of rare words are kept for precision. Chapter 3.1 measures this on real text.'),
    fx('Grice: the cooperative principle', 'Quantity, Quality, Relation, Manner', 'Say enough but not too much, be truthful, be relevant, be clear. Breaking a maxim on purpose creates an implied meaning.'))}
{scene('a customer support chat', '<p>A user types "my order hasn\'t arrived". A good reply follows the maxims: it gives the tracking status (quantity), does not invent a delivery date (quality), talks about this order and not a sale (relation) and avoids jargon (manner). A reply that repeats "I understand your frustration" three times breaks quantity and relation, and users feel they were not understood even though every sentence is polite.</p>')}
{note('In an essay, link Zipf to the speaker side (minimise effort) and Grice to the shared contract between both sides.', 'exam')}
''', kw=['interactive function', 'speaker and hearer', 'encoder decoder', 'two body problem', 'Shannon Weaver model', 'speech chain', 'Zipf least effort', 'Grice maxims', 'cooperative principle', 'quantity quality relation manner'])

K.lesson('recursion', 'Recursion and the Pirahã debate', f'''
<p>Lecture 2 opened by finishing a debate from lecture 1. Linguists define <b>recursion</b> precisely: a clause can contain another clause of the same kind, which can contain another, with no fixed limit.</p>
{steps('Building a recursive sentence, as in class', [
    'Matrix clause only: [John said that Mary had left.]',
    'Embed a clause: [John said that [Mary had left before Tom arrived]].',
    'Embed again: [John said that [Mary had left before [Tom, who was late, arrived]]].',
    'Each bracket is a clause with its own subject and verb, sitting inside a bigger clause. That self similar nesting is recursion.'])}
{code('nest')}
<h3>Why it caused a fight</h3>
<p>In 2002, Hauser, Chomsky and Fitch proposed that recursion may be the single core property that makes human language unique. The linguist Daniel Everett, who lived with the Pirahã people of the Brazilian Amazon, claimed in 2005 that their language has no embedded clauses, no exact number words and no fixed colour terms. He explained this by an immediacy of experience principle: speakers talk about what they or someone they know witnessed directly. If one human language truly lacks recursion, recursion cannot be a universal that every language must have. Nevins, Pesetsky and Rodrigues (2009) re examined Everett\'s own data and argued it does not show that. The question is still open.</p>
<h3>Why an NLP course cares</h3>
<ul>
<li>Most NLP systems are built on high resource languages such as English. Assumptions that look universal may only be English habits.</li>
<li>A language with few speakers has little digital text, so word counts are tiny and a statistical model has almost nothing to learn from. This is the <b>low resource</b> problem.</li>
<li>Computers store words as numbers: build a vocabulary, give each word an index, then count. A classmate described exactly this, which is the subject of chapter 2.</li>
</ul>
{deep('recursion in formal grammar', '<p>A context free rule such as S → NP VP with VP → V S lets a sentence appear inside a verb phrase, so the grammar generates sentences of unbounded depth. Finite state machines (chapter 5.2) cannot handle unbounded centre embedding like "the rat the cat the dog chased bit died", which is one classic argument that natural language is not a regular language. People struggle with more than two levels of centre embedding, so the formal capacity and real use are different things.</p>')}
''', kw=['recursion', 'matrix clause', 'embedded clause', 'Piraha', 'Pirahã', 'Daniel Everett', 'Hauser Chomsky Fitch', 'immediacy of experience', 'low resource language', 'centre embedding'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which level of language studies how words are built from smaller meaningful parts?', ['Phonetics', 'Morphology', 'Syntax', 'Pragmatics'], 1,
       'Think of dis + taste.', 'Morphology studies morphemes, the smallest meaningful units, and how they combine into words.')
K.quiz('e', 'How many morphemes are in the word "cats"?', ['1', '2', '3', '4'], 1, 'One part names the animal, one part adds a meaning.',
       'cat + s. The plural -s is a bound morpheme. The word still has only one syllable, which is why morphemes are not syllables.')
K.quiz('e', 'Saying "It is cold in here" to ask someone to close a window is an example of', ['Phonology', 'Morphology', 'Semantics only', 'Pragmatics'], 3,
       'The intended meaning needs the situation.', 'The literal meaning is a temperature report. The request comes from context, which is pragmatics.')
K.quiz('e', 'In the semiotic triangle, which pair is NOT directly connected?', ['Symbol and concept', 'Concept and referent', 'Symbol and referent', 'All three are directly connected'], 2,
       'Look for the dashed edge.', 'A word reaches the world only through a concept in a mind. The symbol to referent edge is drawn dashed or left out.')
K.quiz('m', '"Colourless green ideas sleep furiously" shows that', ['A sentence can be grammatical but meaningless', 'English has no syntax', 'Phonology decides meaning', 'Every grammatical sentence is true'], 0,
       'Is the word order wrong?', 'The syntax is fine, the semantics is odd. Chomsky used it to show that grammaticality and meaning are separate levels.')
K.quiz('m', 'Which affix type wraps around a root on both sides at once?', ['Prefix', 'Suffix', 'Infix', 'Circumfix'], 3,
       'German ge-lob-t.', 'A circumfix has two parts placed before and after the root at the same time.')
K.quiz('m', 'English treats the breathy p of "pin" and the plain p of "spin" as one sound, but Hindi treats प and फ as two. This difference is studied in', ['Phonetics', 'Phonology', 'Morphology', 'Syntax'], 1,
       'The physical sounds are the same in both languages. What differs?', 'Which differences change meaning is a property of each language sound system, which is phonology.')
K.quiz('m', 'Which statement matches the lecture view of communication?', ['The listener receives an exact copy of the thought', 'The listener rebuilds an approximation of the thought from a signal', 'Meaning travels inside the sound wave', 'Only the speaker matters'], 1,
       'Look at the last box of the chain.', 'Thought → representation → signal → representation → reconstructed thought. The reconstruction is never a perfect copy.')
K.quiz('h', 'The conditional P → Q is false in exactly which case?', ['P false, Q false', 'P false, Q true', 'P true, Q false', 'P true, Q true'], 2,
       'When is a promise broken?', 'Only when the condition happens and the promised result does not. The other three rows keep the promise.')
K.quiz('h', 'Why did Everett\'s claims about Pirahã matter so much?', ['Pirahã has the largest vocabulary', 'If a human language lacks recursion, recursion cannot be a universal core of language', 'Pirahã has no sounds', 'It proved Chomsky right'], 1,
       'Hauser, Chomsky and Fitch, 2002.', 'They proposed recursion as the possibly unique core of the language faculty. A counterexample would weaken that claim. Critics dispute that Everett\'s data show it.')
K.quiz('h', 'Grice\'s maxim of Quantity says', ['Always speak briefly', 'Give as much information as needed, and no more', 'Never use numbers', 'Say only true things'], 1,
       'Quality is the one about truth.', 'Quantity balances too little against too much, the effort against clarity trade off from the lecture.')
K.quiz('x', '"Unicorn" is meaningful though no unicorn exists. The best explanation is', [
    'The word refers to horses', 'Meaning is tied to a concept built compositionally from parts that do have referents, a sense without a reference', 'The word is meaningless', 'It refers to a picture'], 1,
    'Frege separated sense and reference.', 'The concept horse plus single horn plus white is meaningful, so the word has a sense even though its reference in our world is empty.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many morphemes are in "unhappiness"?', '3', 'Look for a prefix, a root and a suffix.',
       ['Prefix un- means not.', 'Root happy (spelled happi before the suffix).', 'Suffix -ness turns an adjective into a noun.', eq('un + happy + ness = 3 morphemes')], check=3)
K.calc('e', 'Of the four rows of the truth table for P → Q, how many are false?', '1', 'Only one combination breaks the promise.',
       ['The rows are TT, TF, FT and FF.', 'P → Q fails only when P is true and Q is false.', eq('false rows = 1')], check=1)
K.calc('e', 'How many different orders can subject (S), verb (V) and object (O) be placed in?', '6', 'Count the arrangements of three different things.',
       ['The first slot has 3 choices, the second 2 and the last 1.', eq('3 × 2 × 1 = 3! = 6'), 'They are SOV (Hindi), SVO (English), VSO (Irish), VOS, OVS and OSV.'], check=6)
K.calc('m', 'A truth table for three propositions P, Q and R has how many rows?', '8', 'Each proposition is true or false.',
       ['Each of the 3 propositions has 2 values.', eq('2 × 2 × 2 = 2<sup>3</sup> = 8 rows'), 'In general n propositions need 2<sup>n</sup> rows.'], check=8)
K.calc('m', 'A sentence has two ambiguous words, each with 2 senses, and one attachment that can go 2 ways. If all choices are independent, how many readings are possible?', '8', 'Multiply the choices.',
       ['Word 1: 2 senses. Word 2: 2 senses.', 'Attachment: 2 trees.', eq('2 × 2 × 2 = 8 readings'), 'This multiplication is why ambiguity grows so fast in long sentences.'], check=8)
K.calc('m', 'How many clauses are in "John said that Mary had left before Tom, who was late, arrived"?', '4', 'Count the verbs that each have their own subject.',
       ['John said (the matrix clause).', 'Mary had left.', 'Tom arrived.', 'who (Tom) was late.', eq('4 clauses, one matrix and three embedded')], check=4)
K.calc('m', 'With Zipf\'s law f(r) = C ÷ r and the most common word seen 60,000 times, how often is the word of rank 3 expected?', '20000', 'C is the frequency of rank 1.',
       ['C = f(1) = 60,000.', 'f(3) = 60,000 ÷ 3.', eq('f(3) = 20,000')], check=20000)
K.calc('h', 'A vocabulary has 1,000 words. How many different 3 word strings can be formed if any word can go in any slot?', '1000000000', 'Each slot is filled independently.',
       ['Slot 1: 1,000 choices, slot 2: 1,000, slot 3: 1,000.', eq('1,000<sup>3</sup> = 10<sup>9</sup>'), 'Only a tiny share of these are grammatical, which is exactly what syntax and later language models must capture.'], check=10 ** 9)
K.calc('h', 'Using Shannon\'s capacity C = B log<sub>2</sub>(1 + S/N), what is C for B = 3,000 Hz and S/N = 1,023? Give bits per second.', '30000', 'log<sub>2</sub>(1,024) is a whole number.',
       ['1 + S/N = 1 + 1,023 = 1,024 = 2<sup>10</sup>.', 'log<sub>2</sub> 1,024 = 10.', eq('C = 3,000 × 10 = 30,000 bits per second'), 'This is the pure engineering limit. It says nothing about meaning, which is the lecture point.'], check=30000)
K.calc('x', 'The nesting program builds a sentence from a list of clauses joined by "that". With 4 clauses, how many times does the word "that" appear?', '3', 'Each step of the recursion adds one "that".',
       ['nest of 1 clause returns it unchanged, with no "that".', 'Each extra clause adds exactly one "that" in front of the inner part.', eq('number of "that" = clauses − 1 = 4 − 1 = 3')], check=3)
K.calc('x', 'A language has 30 phonemes. If words were any string of exactly 3 phonemes, how many distinct words would be possible?', '27000', 'Each of the 3 positions can hold any of the 30 phonemes.',
       ['Position 1: 30 choices.', 'Positions 2 and 3: 30 each.', eq('30<sup>3</sup> = 27,000'), 'Real languages use far fewer because phonology forbids many sound sequences (phonotactics).'], check=27000)

# ---------------------------------------------------------------- assignments
K.assign('affix', 'e', 'Strip a prefix',
         '<p>Write <code>strip_prefix(word, prefixes)</code>. If the word starts with one of the prefixes and at least 3 letters remain after it, return <code>[prefix, rest]</code>. Otherwise return <code>[word]</code>. Try the prefixes in the given order.</p>',
         '''
def strip_prefix(word, prefixes):
    # your code here
    pass
''', [("strip_prefix('distaste', ['un', 'dis'])", ['dis', 'taste']), ("strip_prefix('unhappy', ['un', 'dis'])", ['un', 'happy']),
      ("strip_prefix('under', ['un'])", ['un', 'der']), ("strip_prefix('uno', ['un'])", ['uno']), ("strip_prefix('cat', ['un', 'dis'])", ['cat'])],
         '''
def strip_prefix(word, prefixes):
    for p in prefixes:
        if word.startswith(p) and len(word) - len(p) >= 3:
            return [p, word[len(p):]]
    return [word]
''', 'Use str.startswith and slicing.', '<p>The third test shows the weakness of pure string rules: "under" is not un + der. Real morphological analysers check the remainder against a dictionary.</p>')
K.assign('implies', 'e', 'The truth table of a conditional',
         '<p>Write <code>table()</code> that returns the four rows of the truth table of P → Q as lists <code>[P, Q, result]</code>, in the order TT, TF, FT, FF.</p>',
         '''
def table():
    # your code here
    pass
''', [('table()', [[True, True, True], [True, False, False], [False, True, True], [False, False, True]]), ('sum(r[2] for r in table())', 3)],
         '''
def table():
    rows = []
    for p in [True, False]:
        for q in [True, False]:
            rows.append([p, q, (not p) or q])
    return rows
''', 'P → Q equals (not P) or Q.', '<p>Exactly one row is false. That is the row where it rains and you still go to class.</p>')
K.assign('nest', 'm', 'Recursive sentences',
         '<p>Write a recursive function <code>nest(clauses)</code> that joins a list of clauses with " that " so each clause contains the next, as in the lecture. Then write <code>depth(sentence)</code> that returns how many clauses a sentence built this way has.</p>',
         '''
def nest(clauses):
    # your code here
    pass

def depth(sentence):
    # your code here
    pass
''', [("nest(['John said', 'Mary left'])", 'John said that Mary left'), ("nest(['Tom left'])", 'Tom left'),
      ("nest(['A said', 'B thought', 'C left'])", 'A said that B thought that C left'), ("depth('A said that B thought that C left')", 3)],
         '''
def nest(clauses):
    if len(clauses) == 1:
        return clauses[0]
    return clauses[0] + " that " + nest(clauses[1:])

def depth(sentence):
    return sentence.count(" that ") + 1
''', 'The base case is a single clause.', '<p>The function calls itself on a shorter list. This mirrors a grammar rule that lets a clause appear inside a clause.</p>')

K.must('Working definition', 'Language is a systematic, symbolic and structured system that starts as thought, organises it, and lets it be rebuilt in another mind.')
K.must('Six levels', 'Phonetics, phonology, morphology, syntax, semantics, pragmatics. Each combines the units of the level below.')
K.must('Two functions', 'Symbolic: words stand for concepts, not directly for things (semiotic triangle). Interactive: a speaker encodes and a hearer reconstructs, never an exact copy.')
K.must('Form and meaning', 'A symbol is a conventional form meaning pair. Unicorn has a sense without a reference. TAM marks present, past and imagined reality.')
K.must('Effort and clarity', 'Zipf: least effort, f(r) ≈ C ÷ r. Grice: quantity, quality, relation, manner.')
K.must('Recursion', 'A clause inside a clause without limit. Everett claimed Pirahã lacks it, a challenge to Hauser, Chomsky and Fitch. Still debated.')

T = K.topic(
    slug='what-is-language', topic='what-is-language', step=(1, 'Language and meaning', 'nlp-language', 'What language is, why it is ambiguous, and what it would mean for a machine to understand it.', 'School and college'),
    title='What language is', short='What language is', badge='1.1', minutes=35,
    lead='Start where the course starts: a working definition of language, the six levels from sounds to context, how words stand for concepts, how a message travels between two minds, and why recursion caused one of the big debates in linguistics.',
    desc='Definition of language, the six levels of linguistic structure, morphemes, the symbolic and interactive functions, the semiotic triangle, tense aspect and mood, Zipf and Grice, recursion and the Piraha debate.',
    summary='The working definition, six levels from phonetics to pragmatics, symbols and the semiotic triangle, the speaker and hearer chain, Zipf and Grice, and recursion.',
    keywords=['language', 'linguistics', 'six levels', 'phonetics', 'phonology', 'morphology', 'syntax', 'semantics', 'pragmatics', 'semiotic triangle', 'Grice', 'recursion', 'Piraha'],
    recap='<p>Language turns thought into a structured, symbolic form that another mind can rebuild. It is studied in six levels, words reach the world only through concepts, and every message is a reconstruction, not a copy.</p>')
