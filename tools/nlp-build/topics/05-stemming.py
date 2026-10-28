# Chapter 2.2: stemming and lemmatisation. Source: lecture 1 side topic on morphemes, lecture 9 warm-up Q27
# (stem against lemma, named as exam material), the NLTK notebook stemming, lemmatisation and exercise cells.
# Every stem below was produced by NLTK 3.10 PorterStemmer, SnowballStemmer("english") and LancasterStemmer.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from nlpkit import listing

K = Kit()

K.code('conflate', r'''
# Why normalise? Five surface forms, one idea. A crude suffix stripper merges them into one type
SUFFIXES = ["ions", "ion", "ing", "ed", "s"]

def strip(word):
    for suf in SUFFIXES:                     # longest suffixes are listed first
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[:-len(suf)]
    return word

words = ["connect", "connected", "connecting", "connection", "connections"]
stems = [strip(w) for w in words]
print(stems)
print("types before:", len(set(words)), " types after:", len(set(stems)))
''')

K.code('measure', r'''
# Porter's measure m: write the word as [C](VC)^m[V] and count the VC pairs
def is_cons(word, i):
    ch = word[i]
    if ch in "aeiou":
        return False
    if ch == "y":                            # y after a consonant acts as a vowel (happy, ivy)
        return i == 0 or not is_cons(word, i - 1)
    return True

def measure(word):
    pattern = "".join("C" if is_cons(word, i) else "V" for i in range(len(word)))
    return pattern, pattern.count("VC")       # VC can only appear where a vowel run meets a consonant run

for w in ["tree", "trouble", "oats", "ivy", "troubles", "private"]:
    p, m = measure(w)
    print(w, p, "m =", m)
''')

K.code('step1', r'''
# Porter step 1a: plural endings. Rules are tried in order and the first match wins
RULES = [("sses", "ss"), ("ies", "i"), ("ss", "ss"), ("s", "")]

def step1a(word):
    for old, new in RULES:
        if word.endswith(old):
            return word[:len(word) - len(old)] + new
    return word

for w in ["caresses", "ponies", "caress", "cats", "bus"]:
    print(w, "->", step1a(w))
''')

K.code('lemma', r'''
# A tiny lemmatiser in the style of WordNet morphy: exceptions first, then suffix rules checked against a dictionary
EXCEPTIONS = {"n": {"children": "child", "geese": "goose", "mice": "mouse"},
              "v": {"saw": "see", "went": "go", "was": "be"}}
RULES = {"n": [("ies", "y"), ("es", ""), ("s", "")], "v": [("ing", "e"), ("ing", ""), ("ed", "e"), ("ed", ""), ("s", "")]}
LEXICON = {"child", "goose", "mouse", "leaf", "study", "box", "cat", "see", "go", "be", "love", "walk", "saw", "loving"}

def lemmatize(word, pos="n"):
    if word in EXCEPTIONS[pos]:
        return EXCEPTIONS[pos][word]
    for old, new in RULES[pos]:
        if word.endswith(old) and word[:-len(old)] + new in LEXICON:
            return word[:-len(old)] + new
    return word                               # unknown words come back unchanged

for w, pos in [("children", "n"), ("studies", "n"), ("boxes", "n"), ("loving", "n"), ("loving", "v"), ("saw", "n"), ("saw", "v"), ("walked", "v")]:
    print(w, pos, "->", lemmatize(w, pos))
''')

K.lesson('morphology', 'Words have parts', f'''
<p>Look at play, plays, played, playing, player and replay. A person sees one idea dressed six ways. A computer that compares strings sees six unrelated words, so evidence about one form never helps the others. Stemming and lemmatisation exist to undo this, and both rest on morphology, the study of how words are built from parts.</p>
<h3>Morphemes, a quick reminder</h3>
<p>Chapter 1.1 met the morpheme, the smallest piece that carries meaning or a grammar job. A free morpheme stands alone (help, build). A bound morpheme must attach to something (un-, -ful, -ing). The lecture worked problem split four words.</p>
{table(['Word', 'Morphemes', 'Count'], [
    ['rebuilding', 're- (bound prefix, again) + build (free root) + -ing (bound suffix, progressive)', '3'],
    ['unhelpful', 'un- (bound prefix, not) + help (free root) + -ful (bound suffix, full of)', '3'],
    ['teachers', 'teach (free root) + -er (bound suffix, one who) + -s (bound suffix, plural)', '3'],
    ['impossibility', 'im- (bound prefix, not) + possible (free root) + -ity (bound suffix, makes a noun)', '3']])}
<h3>Two kinds of suffix</h3>
{table(['', 'Inflection', 'Derivation'], [
    ['What it does', 'Adds grammar: number, tense, person, comparison', 'Makes a new word, often a new part of speech'],
    ['Examples', 'cat → cats, walk → walked, big → bigger', 'teach → teacher, happy → happiness, nation → national'],
    ['Part of speech', 'Stays the same', 'Often changes (verb → noun)'],
    ['Lemma', 'Same lemma as the base word', 'A different lemma with its own dictionary entry']])}
<p>This table decides what the two tools should do. A lemmatiser removes inflection only: walked becomes walk, but teacher stays teacher because it is a separate dictionary word. A stemmer cuts both kinds without asking, so national and nation can both become nation.</p>
{code('conflate')}
{fxs(
    fx('Vocabulary after normalisation', '<i>V</i><sub>after</sub> ≤ <i>V</i><sub>before</sub>, &nbsp; reduction = 1 − ' + frac('<i>V</i><sub>after</sub>', '<i>V</i><sub>before</sub>'), 'Merging forms can only lower the number of types. Above, 5 types become 1, a reduction of 80 percent.'),
    fx('Why counts improve', 'c(connect*) = c(connect) + c(connected) + c(connecting) + …', 'Evidence that was split over five rare types is pooled into one common type. Chapter 4 shows why fewer, larger counts give better probabilities.'))}
{scene('searching a news archive', '<p>A reader searches an Indian news archive for "flooding in Assam". Articles say "floods", "flooded" and "flood". With exact matching most relevant stories are missed. With stemming, flooding, floods and flooded all become flood, and the search finds them. The cost is that "flood of complaints" about a phone launch may also match.</p>')}
{note('Hindi, Turkish, Finnish and Tamil pack many more endings into one word than English does. One Turkish verb can have hundreds of forms, so normalisation matters even more for them.', 'tip')}
''', kw=['morphology', 'morpheme', 'free morpheme', 'bound morpheme', 'inflection', 'derivation', 'affix', 'normalisation', 'conflation'])

K.lesson('stemming', 'Stemming: chop with rules', f'''
<p>A stemmer removes endings using a fixed list of rules and no dictionary. The piece that is left is the <b>stem</b>. It is fast and needs no data, but the stem does not have to be a real word. The professor's own examples: gaming gives game, which happens to be a word, while leaves gives leav, which is not.</p>
{listing("""from nltk.stem import PorterStemmer
ps = PorterStemmer()
stem_words = ["game", "gaming", "gamed", "games", "leaves", "cared", "children",
              "sportingly", "fairly", "saw", "loving", "boy's"]
for word in stem_words:
    print(ps.stem(word))""", "game\ngame\ngame\ngame\nleav\ncare\nchildren\nsportingli\nfairli\nsaw\nlove\nboy'")}
<p>Read the output carefully, because each line teaches something.</p>
<ul>
<li>game, gaming, gamed and games all become game. Four forms now share one count.</li>
<li>leaves becomes leav. The rule removed -es and did not know that the singular is leaf.</li>
<li>children is left alone. No suffix rule turns an irregular plural into child.</li>
<li>sportingly becomes sportingli and fairly becomes fairli. Porter rewrites a final y as i so that happy and happiness meet at happi.</li>
<li>saw is unchanged. A stemmer cannot know that saw can be the past of see.</li>
</ul>
{viz('porter')}
<h3>The measure m</h3>
<p>Porter only removes a long ending when enough of the word is left. He measured "enough" by writing the word as runs of consonants (C) and vowels (V). The letters a, e, i, o and u are vowels, and y is a vowel when it follows a consonant.</p>
{fxs(
    fx('Porter\'s word shape', '[C] (VC)<sup><i>m</i></sup> [V]', 'Square brackets mean optional. m counts how many times a vowel run is followed by a consonant run.', key=True),
    fx('Examples from Porter (1980)', 'm = 0: tree, by<br>m = 1: trouble, oats, ivy<br>m = 2: troubles, private', 'tr-ee is C V, so m = 0. tr-ou-bl-e is C V C V, so m = 1.'))}
{code('measure')}
<p>A rule such as "(m &gt; 1) EMENT → nothing" turns replacement into replac (m of replac is 2) but leaves cement alone, because the stem c has m = 0. The condition stops the stemmer from cutting short words to nothing.</p>
{note('In an exam, write the C and V pattern under the letters first, then count VC pairs. Most mistakes come from forgetting that y after a consonant is a vowel.', 'exam')}
''', kw=['stemming', 'stem', 'Porter stemmer', 'measure', 'consonant', 'vowel', 'suffix stripping', 'leav'])

K.lesson('porter-steps', 'Inside the Porter algorithm', f'''
<p>Martin Porter published the algorithm in 1980 for search engines. It has five steps, applied in order. Each step holds a list of rules of the form (condition) SUFFIX → REPLACEMENT, and within a step only the longest matching suffix is used.</p>
{table(['Step', 'Job', 'Example rules', 'Examples'], [
    ['1a', 'Plurals', 'SSES → SS, IES → I, SS → SS, S → nothing', 'caresses → caress, ponies → poni, cats → cat'],
    ['1b', 'Past tense and -ing', '(m &gt; 0) EED → EE, (*v*) ED → nothing, (*v*) ING → nothing, then tidy up', 'plastered → plaster, motoring → motor, hopping → hop, sing → sing'],
    ['1c', 'Final y', '(*v*) Y → I', 'happy → happi, sky → sky'],
    ['2', 'Double suffixes', '(m &gt; 0) ATIONAL → ATE, IZATION → IZE, FULNESS → FUL', 'relational → relate, vietnamization → vietnamize'],
    ['3', 'More endings', '(m &gt; 0) ICATE → IC, FUL → nothing, NESS → nothing', 'triplicate → triplic, hopeful → hope, goodness → good'],
    ['4', 'Long suffixes', '(m &gt; 1) AL, ANCE, ENCE, ER, IC, ABLE, IBLE, ANT, EMENT, MENT, ENT, ION, ISM, ATE, IVE … → nothing', 'revival → reviv, adjustable → adjust, adoption → adopt'],
    ['5', 'Tidy the end', '(m &gt; 1) E → nothing, (m &gt; 1 and double L) → single L', 'probate → probat, rate → rate, controll → control']])}
<p>The symbol *v* means "the stem contains a vowel". It is why sing keeps its -ing: removing it would leave s, which has no vowel.</p>
{steps('Trace: hopefulness with NLTK PorterStemmer', [
    'Step 1a and 1b: no plural, past or -ing ending. hopefulness stays.',
    'Step 2: FULNESS → FUL needs m &gt; 0 on the stem hope. m(hope) = 1, so hopefulness → hopeful.',
    'Step 3: FUL → nothing needs m &gt; 0 on hope. It applies, so hopeful → hope.',
    'Step 4: no long suffix matches hope.',
    'Step 5: E → nothing needs m &gt; 1 on the stem hop, but m(hop) = 1. The other branch (m = 1 and the stem hop does not end in consonant vowel consonant) fails too, because hop does end in c v c. So the e stays.',
    eq('hopefulness → hope')])}
{code('step1')}
{deep('NLTK mode against the original paper', '<p>NLTK\'s PorterStemmer runs in NLTK_EXTENSIONS mode by default. It adds a few fixes that the 1980 paper does not have. One is that a four letter word ending in ies keeps ie, so ties becomes tie in NLTK but ti in the paper. Another is a small exception list that maps forms such as dying and lying to die and lie. When an exam asks you to apply "the Porter rules", use the paper rules and say so.</p>')}
<h3>Snowball and Lancaster</h3>
<p>Porter later wrote Snowball (also called Porter2), a cleaned up version with better handling of endings like -ly. Lancaster (Paice and Husk, 1990) is far more aggressive. All three ran in NLTK on the same words:</p>
{table(['Word', 'Porter', 'Snowball', 'Lancaster'], [
    ['sportingly', 'sportingli', 'sport', 'sport'], ['fairly', 'fairli', 'fair', 'fair'], ['gaming', 'game', 'game', 'gam'],
    ['generously', 'gener', 'generous', 'gen'], ['organization', 'organ', 'organ', 'org'], ['studies', 'studi', 'studi', 'study'], ['maximum', 'maximum', 'maximum', 'maxim']])}
''', kw=['Porter algorithm', 'step 1a', 'step 1b', 'Snowball', 'Porter2', 'Lancaster', 'Paice Husk', 'NLTK_EXTENSIONS', 'suffix rules'])

K.lesson('lemmatisation', 'Lemmatisation: look it up', f'''
<p>A <b>lemma</b> is the dictionary form of a word, the form you would look up. children has the lemma child, leaves (the noun) has the lemma leaf, and better (the adjective) has the lemma good. A lemmatiser always returns a real word, because it uses a dictionary rather than chopping blindly.</p>
<h3>The part of speech matters</h3>
<p>The same spelling can have different lemmas. saw as a verb is the past of see, but saw as a noun is a tool. leaves can be the plural of leaf or a form of the verb leave. So a lemmatiser needs to know the part of speech, and NLTK's WordNetLemmatizer assumes a noun when you do not tell it.</p>
{listing("""lemma = nltk.wordnet.WordNetLemmatizer()
print(lemma.lemmatize('loving', 'v'))     # told it is a verb
for word in stem_words:
    print(lemma.lemmatize(word))          # no POS given, so noun is assumed""",
         "love\n\ngame\ngaming\ngamed\ngame\nleaf\ncared\nchild\nsportingly\nfairly\nsaw\nloving\nboy's")}
<p>As a noun, only games, leaves and children changed. gaming, cared and loving were left alone because they are verb forms, and the lemmatiser was looking for nouns. Asked with pos='v', loving correctly became love.</p>
<h3>How WordNet's lemmatiser works</h3>
<ol>
<li>Look the word up in an exception list for that part of speech (children → child, geese → goose).</li>
<li>Otherwise try the detachment rules for that part of speech, such as -ies → -y, -es → nothing and -s → nothing for nouns.</li>
<li>Keep a result only if it is a real entry in WordNet.</li>
<li>If nothing works, return the word unchanged.</li>
</ol>
{code('lemma')}
{note('Run a POS tagger first and pass each tag to the lemmatiser. Without the tag, most verbs and adjectives come back unchanged, exactly as in the notebook output above.', 'warn')}
{scene('a voice assistant booking cabs', '<p>A rider says "I booked a cab yesterday, cancel the bookings." The intent system has one entry for the action book and one for the object booking. A lemmatiser with POS tags maps booked (verb) to book and bookings (noun) to booking, which keeps the action and the object apart. A stemmer would turn both into book and blur the two.</p>')}
''', kw=['lemmatisation', 'lemmatization', 'lemma', 'WordNet', 'WordNetLemmatizer', 'morphy', 'part of speech', 'dictionary form'])

K.lesson('compare', 'Stem or lemma: choosing well', f'''
<p>The professor said this question will appear in the exam: "What is a lemma and what is a stem? Answer with examples." Here is a complete answer.</p>
{table(['', 'Stem', 'Lemma'], [
    ['Definition', 'What is left after rule based suffix stripping', 'The dictionary (citation) form of the word'],
    ['Real word', 'Not always: leaves → leav, studies → studi', 'Always: leaves → leaf, studies → study'],
    ['Needs', 'Only a rule list', 'A dictionary and the part of speech'],
    ['Irregular forms', 'Missed: children, saw, better unchanged', 'Handled: child, see (verb), good (adjective)'],
    ['Speed', 'Very fast', 'Slower (tagging plus lookup)'],
    ['Typical use', 'Search engines, quick text classification', 'Question answering, chatbots, linguistics']])}
{viz('stemcompare')}
<h3>Two kinds of mistake</h3>
<ul>
<li><b>Over stemming</b> merges words that mean different things. university, universe and universal all become univers in Porter.</li>
<li><b>Under stemming</b> fails to merge forms of the same word. alumnus becomes alumnu but alumni stays alumni, so the two never meet. children and child never meet either.</li>
</ul>
<p>The notebook exercise tested both stemmers on thirteen words. They agreed on twelve and differed only on alumnus (Porter alumnu, Snowball alumnus). Neither joined alumni with alumnus.</p>
{listing("""stem_words = ["alumnus", "running", "alumnu", "alumni", "alumna", "alumnae", "cats",
              "catty", "cat", "chocolates", "chocolatey", "choco", "children"]
print([snowball.stem(w) for w in stem_words])""",
         "['alumnus', 'run', 'alumnu', 'alumni', 'alumna', 'alumna', 'cat', 'catti', 'cat', 'chocol', 'chocolatey', 'choco', 'children']")}
<h3>Measuring the effect in search</h3>
<p>A search engine is judged by precision (the share of returned documents that are relevant) and recall (the share of relevant documents that are returned). Stemming usually raises recall, because more forms match, and can lower precision, because over stemming lets wrong documents in.</p>
{fxs(
    fx('Precision and recall', '<i>P</i> = ' + frac('relevant returned', 'all returned') + ' &nbsp; &nbsp; <i>R</i> = ' + frac('relevant returned', 'all relevant'), 'Both lie between 0 and 1.', key=True),
    fx('F1 score', '<i>F</i><sub>1</sub> = ' + frac('2 <i>P R</i>', '<i>P</i> + <i>R</i>'), 'The harmonic mean. It is high only when both P and R are high.'))}
{ladder(
    '<p>Stemming cuts the end off a word with simple rules, so playing and played both become play. Sometimes the result is not a real word, like leav. Lemmatising looks the word up and gives the dictionary word, like leaf.</p>',
    '<p>A stemmer applies ordered suffix rules with conditions on the measure m. A lemmatiser uses an exception list, detachment rules and a lexicon, and needs the POS tag. Stemming conflates inflection and derivation. Lemmatisation removes inflection only.</p>',
    '<p>Normalisation trades recall for precision in retrieval and reduces sparsity for count based models. Over stemming and under stemming are measured with conflation based indices (Paice, 1994). For morphologically rich languages, finite state transducers (two level morphology, Koskenniemi 1983) analyse words into lemma plus features, such as walked → walk +V +PAST.</p>',
    '<p>Neural models mostly replace explicit normalisation with subword tokens (chapter 2.1), which learn shared pieces like walk and ##ed from data. Lemmatisation remains useful for low resource languages, for interpretable features and for evaluation. Research studies neural morphological analysers and shared tasks such as SIGMORPHON reinflection.</p>')}
''', kw=['stem vs lemma', 'over stemming', 'under stemming', 'precision', 'recall', 'F1', 'information retrieval', 'alumnus'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Porter stems "leaves" to', ['leaf', 'leave', 'leav', 'leaves'], 2,
       'A stem need not be a real word.', 'The rule removed -es. Porter has no dictionary, so it cannot know the singular is leaf.')
K.quiz('e', 'What is the lemma of "children"?', ['childr', 'child', 'children', 'kid'], 1,
       'The dictionary form.', 'child. Stemmers leave children unchanged because no suffix rule handles this irregular plural.')
K.quiz('e', 'Which tool always returns a real word?', ['Porter stemmer', 'Lancaster stemmer', 'Lemmatiser', 'Snowball stemmer'], 2,
       'Which one uses a dictionary?', 'A lemmatiser only returns forms found in its lexicon, or the word itself.')
K.quiz('e', 'In the notebook, what did WordNetLemmatizer return for "loving" with no POS given?', ['love', 'loving', 'lov', 'loved'], 1,
       'The default POS is noun.', 'loving is not a noun form it can reduce, so it came back unchanged. With pos=\'v\' it gave love.')
K.quiz('m', 'Which pair shows inflection rather than derivation?', ['teach → teacher', 'happy → happiness', 'walk → walked', 'nation → national'], 2,
       'Which one keeps the part of speech?', 'walked is still a verb with a tense added. The others create new words.')
K.quiz('m', 'Porter and Snowball disagreed on which word in the notebook exercise list?', ['running', 'alumnus', 'chocolates', 'children'], 1,
       'Only one row differed.', 'Porter gave alumnu, Snowball kept alumnus.')
K.quiz('m', 'Why does Porter leave "sing" unchanged while "motoring" becomes "motor"?', [
    'sing is in a dictionary', 'Removing ing from sing leaves s, which has no vowel', 'sing is too common', 'Porter ignores verbs'], 1,
    'Look at the condition (*v*).', 'The rule (*v*) ING → nothing needs a vowel in what remains. s has none.')
K.quiz('m', 'university, universe and universal all become univers. This is', ['Under stemming', 'Over stemming', 'Lemmatisation', 'Tokenisation'], 1,
       'Different meanings were merged.', 'Words with different meanings collapsed into one stem.')
K.quiz('h', 'What is m for "troubles"?', ['0', '1', '2', '3'], 2,
       'Write C and V under each letter.', 'tr ou bl e s is C V C V C, which has two VC pairs, so m = 2.')
K.quiz('h', 'Which effect does stemming usually have on a search engine?', ['Higher precision, lower recall', 'Higher recall, possibly lower precision', 'Both always fall', 'No effect'], 1,
       'More forms match.', 'More relevant documents are found, but over stemming can also let unrelated ones in.')
K.quiz('h', 'A lemmatiser turns "better" into "good" only when', ['It is a noun', 'It is told the word is an adjective', 'It is at the start of a sentence', 'Always'], 1,
       'Lemmas depend on POS.', 'better is listed as an irregular comparative under adjectives.')
K.quiz('x', 'Which stemmer is the most aggressive of Porter, Snowball and Lancaster?', ['Porter', 'Snowball', 'Lancaster', 'They are equal'], 2,
       'Look at gaming and organization.', 'Lancaster gives gam and org, cutting further than the others.')
K.quiz('x', 'Why did BERT style models move away from stemming?', ['Stemming is illegal', 'Subword tokens learn shared pieces from data and keep the full word available', 'They only handle English', 'Lemmas are too long'], 1,
       'Think of chapter 2.1.', 'Subword vocabularies capture shared stems and endings without throwing information away.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the measure m of "trouble"?', '1', 'Mark consonants and vowels.',
       ['t r → C', 'ou → V', 'b l → C', 'e → V', eq('C V C V = C (VC)<sup>1</sup> V, so m = 1')], check=1)
K.calc('e', 'Of the 12 notebook words, how many did PorterStemmer leave exactly unchanged?', '3', 'Compare each output with its input.',
       ['Unchanged: game, children, saw.', 'Every other word lost or changed its ending.', eq('3 words')], check=3)
K.calc('e', 'How many morphemes are in "unhelpful"?', '3', 'Prefix, root, suffix.',
       ['un- is a bound prefix meaning not.', 'help is the free root.', '-ful is a bound suffix meaning full of.', eq('un + help + ful = 3')], check=3)
K.calc('m', 'On the 12 tutorial words, how many stems differ between Porter and Snowball?', '3', 'Compare the two notebook outputs line by line.',
       ['sportingly: sportingli against sport.', 'fairly: fairli against fair.', "boy's: boy' against boy.", eq('3 differences')], check=3)
K.calc('m', 'With no POS given, how many of the 12 tutorial words did WordNetLemmatizer change?', '3', 'The default POS is noun.',
       ['games → game.', 'leaves → leaf.', 'children → child.', eq('3 words changed. All verb forms stayed as they were.')], check=3)
K.calc('m', 'connect, connected, connecting, connection and connections all stem to connect. By what percentage does the vocabulary shrink?', '80', 'Types before and after.',
       ['Before: 5 types.', 'After: 1 type.', eq('1 − 1/5 = 0.8 = 80%')], check=80)
K.calc('m', 'What is m for "generalization"? (Porter maps it to gener.)', '6', 'Count VC pairs in the full word.',
       ['g e n e r a l i z a t i o n', 'C V C V C V C V C V C V V C', 'VC pairs: en, er, al, iz, at, ion.', eq('m = 6')], check=6)
K.calc('h', 'There are 40 relevant documents. Without stemming the engine returns 25 documents, 20 of them relevant. With stemming it returns 50, 34 relevant. What is recall with stemming?', '0.85', 'Relevant returned over all relevant.',
       ['Without stemming: R = 20 / 40 = 0.5.', 'With stemming: relevant returned = 34.', eq('R = 34 / 40 = 0.85')], check=0.85, tol=0.001)
K.calc('h', 'In the same search, what is precision with stemming?', '0.68', 'Relevant returned over all returned.',
       ['Without stemming: P = 20 / 25 = 0.8.', 'With stemming: 34 relevant out of 50 returned.', eq('P = 34 / 50 = 0.68'), 'Recall rose, precision fell, as expected.'], check=0.68, tol=0.001)
K.calc('h', 'Compute F1 before and after stemming in that search. Give F1 after stemming to three decimals.', '0.756', 'F1 = 2PR / (P + R).',
       ['Before: 2 × 0.8 × 0.5 / 1.3 = 0.615.', 'After: 2 × 0.68 × 0.85 / 1.53.', eq('F<sub>1</sub> = 1.156 / 1.53 ≈ 0.756'), 'Stemming helped overall in this case.'], check=2 * 0.68 * 0.85 / 1.53, tol=0.0005)
K.calc('x', 'A tagger is 97% accurate on 10,000 tokens. When a tag is wrong, the lemma changes 30% of the time. How many wrong lemmas are expected?', '90', 'Errors times the share that matters.',
       ['Wrong tags: 10,000 × 0.03 = 300.', 'Lemma affected: 300 × 0.3.', eq('= 90 wrong lemmas'), 'Lemmatiser quality is capped by tagger quality.'], check=90)

# ---------------------------------------------------------------- assignments
K.assign('measure', 'm', "Porter's measure",
         '<p>Write <code>measure(word)</code> that returns Porter\'s m. Letters a e i o u are vowels. y is a vowel when it follows a consonant and a consonant otherwise (including at the start). m is the number of times a vowel is directly followed by a consonant.</p>',
         '''
def measure(word):
    # your code here
    pass
''', [("measure('tree')", 0), ("measure('trouble')", 1), ("measure('ivy')", 1), ("measure('troubles')", 2), ("measure('private')", 2), ("measure('yes')", 1)],
         '''
def measure(word):
    def cons(i):
        ch = word[i]
        if ch in "aeiou":
            return False
        if ch == "y":
            return i == 0 or not cons(i - 1)
        return True
    m = 0
    for i in range(1, len(word)):
        if not cons(i - 1) and cons(i):
            m += 1
    return m
''', 'Build a helper that says whether position i is a consonant, then count positions where a vowel is followed by a consonant.',
         '<p>ivy is V C V because the y follows the consonant v. yes starts with a consonant y, so it is C V C with m = 1.</p>')
K.assign('step1a', 'e', 'Porter step 1a',
         '<p>Write <code>step1a(word)</code> that applies the first matching rule in this order: sses → ss, ies → i, ss → ss, s → nothing. Words with none of these endings come back unchanged.</p>',
         '''
def step1a(word):
    # your code here
    pass
''', [("step1a('caresses')", 'caress'), ("step1a('ponies')", 'poni'), ("step1a('caress')", 'caress'), ("step1a('cats')", 'cat'), ("step1a('tree')", 'tree')],
         '''
def step1a(word):
    for old, new in [("sses", "ss"), ("ies", "i"), ("ss", "ss"), ("s", "")]:
        if word.endswith(old):
            return word[:len(word) - len(old)] + new
    return word
''', 'Order matters. If s were tried first, caress would lose its final s.', '<p>The ss → ss rule looks useless but it protects words like caress and glass from the last rule.</p>')
K.assign('lemmatize', 'h', 'A tiny noun lemmatiser',
         '<p>Write <code>lemmatize(word, lexicon)</code> for nouns. Check the exceptions children → child, geese → goose and mice → mouse first. Then try the rules ies → y, es → nothing, s → nothing in that order, and return the first result that is in <code>lexicon</code> (a set). Otherwise return the word unchanged.</p>',
         '''
def lemmatize(word, lexicon):
    # your code here
    pass
''', [("lemmatize('children', set())", 'child'), ("lemmatize('studies', {'study'})", 'study'), ("lemmatize('boxes', {'box'})", 'box'),
      ("lemmatize('cats', {'cat'})", 'cat'), ("lemmatize('loving', {'love'})", 'loving'), ("lemmatize('glasses', {'glass'})", 'glass')],
         '''
def lemmatize(word, lexicon):
    exc = {"children": "child", "geese": "goose", "mice": "mouse"}
    if word in exc:
        return exc[word]
    for old, new in [("ies", "y"), ("es", ""), ("s", "")]:
        if word.endswith(old) and word[:-len(old)] + new in lexicon:
            return word[:-len(old)] + new
    return word
''', 'Only accept a rule result that is a real dictionary word. That is the difference from a stemmer.',
         '<p>This is the shape of WordNet\'s morphy function. loving is returned unchanged because it is a verb form, the same thing the notebook showed.</p>')

K.must('Stem against lemma', 'Stem: rule based chop, may not be a word (leaves → leav). Lemma: dictionary form, uses POS (leaves → leaf, children → child).')
K.must('Porter measure', 'Word = [C](VC)^m[V]. tree 0, trouble 1, troubles 2. y after a consonant is a vowel.')
K.must('Notebook results', 'Porter: sportingli, fairli, boy\'. Snowball: sport, fair, boy. Exercise list differs only on alumnus.')
K.must('Lemmatiser needs POS', 'WordNetLemmatizer defaults to noun. loving stays loving, but with pos=\'v\' it becomes love.')
K.must('Errors and effect', 'Over stemming: university, universe → univers. Under stemming: alumnus and alumni stay apart. Stemming raises recall, may lower precision.')

T = K.topic(
    slug='stemming-lemmatisation', topic='stemming', step=(2, 'Text as data', 'nlp-text', 'Turn raw text into sentences, tokens, stems, lemmas and counts, exactly as the NLTK notebook does.', 'School and college'),
    title='Stems and lemmas', short='Stemming and lemmas', badge='2.2', minutes=35,
    lead='See why play, played and playing should count as one word, how the Porter stemmer chops endings with rules, how a lemmatiser looks words up, and how to answer the stem against lemma exam question.',
    desc='Morphology, inflection and derivation, the Porter algorithm step by step with the measure m, Snowball and Lancaster, WordNet lemmatisation with POS, the notebook outputs, over and under stemming, and the effect on precision and recall.',
    summary='Inflection and derivation, Porter stemming and the measure m, Snowball and Lancaster, WordNet lemmatisation, stem against lemma, and the precision and recall trade off.',
    keywords=['stemming', 'lemmatisation', 'lemmatization', 'Porter', 'Snowball', 'Lancaster', 'WordNet', 'lemma', 'stem', 'morphology', 'measure'],
    recap='<p>A stemmer cuts endings with ordered rules and may leave a non word. A lemmatiser uses a dictionary and the part of speech and always returns a real word. Both shrink the vocabulary so that counts are pooled.</p>')
