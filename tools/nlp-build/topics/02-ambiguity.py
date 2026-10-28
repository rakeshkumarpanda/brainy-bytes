# Chapter 1.2: ambiguity. Source: lecture 1 (bank, homonymy and polysemy, homophones, the cat over the wall,
# John saw Mary with a telescope) and lecture 2 (the 1985 "understands you like your mother" advert, ASR ambiguity,
# "copy the local patient files", lexical against structural ambiguity, how NLP resolves it).
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('catalan', r'''
# How many parse trees does "verb + object + k prepositional phrases" have?
# Church and Patil (1982): the count follows the Catalan numbers C(k + 1).
from math import comb

def catalan(n):
    return comb(2 * n, n) // (n + 1)

for k in range(1, 7):
    print(k, "phrases ->", catalan(k + 1), "trees")
''')

K.code('lesk', r'''
# Simplified Lesk: pick the sense whose gloss shares most words with the sentence
STOP = {"the", "a", "an", "and", "of", "to", "in", "on", "i", "my", "near", "was"}
SENSES = {
    "money bank": "money deposit loan account cash savings branch",
    "river bank": "river water stream fishing grass shore edge",
}

def lesk(sentence):
    words = {w for w in sentence.lower().split() if w not in STOP}
    best, best_score = None, -1
    for sense, gloss in SENSES.items():
        score = len(words & set(gloss.split()))
        print(f"  {sense:11} shares {score}")
        if score > best_score:
            best, best_score = sense, score
    return best

for s in ["I sat on the bank fishing in the river", "I opened a savings account at the bank"]:
    print(s)
    print("  ->", lesk(s))
''')

K.lesson('lexical', 'Lexical ambiguity: one word, several meanings', f'''
<p>A student in lecture 1 said "I sat near a bank" and the class split. People who think of the State Bank of India heard money. People who like nature heard a river. Taken alone, the word cannot decide. What decides in real life is the earlier conversation, the knowledge speaker and listener share, and the physical setting.</p>
{table(['Term', 'What it means', 'Example'], [
    ['Homonymy', 'Same spelling and sound, unrelated meanings with different histories', 'bank (river, from Old Norse banki) and bank (money, from Italian banca, a bench)'],
    ['Polysemy', 'One word, several related senses from one origin', 'mouth of a person and mouth of a river, head of a company'],
    ['Homophone', 'Same sound, different spelling and meaning', 'pear and peer, write and right'],
    ['Homograph', 'Same spelling, different sound and meaning', 'lead the metal and lead the verb']])}
<p>Choosing the right sense by computer is called <b>word sense disambiguation</b> (WSD). The oldest practical method, Lesk (1986), compares the words around the target with the dictionary definition (the gloss) of each sense and picks the sense with the largest overlap. It is Firth\'s idea that you know a word by the company it keeps, turned into a counting rule.</p>
{fx('Simplified Lesk', 'sense* = argmax<sub><i>s</i></sub> |context(<i>w</i>) ∩ gloss(<i>s</i>)|', 'Count the shared words between the sentence and each gloss, after removing very common words. Ties and zero overlaps fall back to the most frequent sense.', key=True)}
{viz('sensepick')}
{code('lesk')}
<h3>The cat jumped over the wall</h3>
<p>The class drew four different paths for one sentence: landing on top of the wall, a straight hop beside it, dropping onto it from above, and a full arc to the other side. Most chose the full arc, but not everyone. The word <b>over</b> carries the ambiguity. It can mean above and across (a plane over a hill), covering (a blanket over a bed) or finished (the meeting is over). George Lakoff (1987) showed these senses form a family around one spatial picture, a textbook case of polysemy. Language under specifies, and the listener fills the gap with expectations about how cats jump.</p>
''', kw=['lexical ambiguity', 'homonymy', 'polysemy', 'homophone', 'homograph', 'word sense disambiguation', 'WSD', 'Lesk algorithm', 'gloss overlap', 'bank', 'over', 'Lakoff'])

K.lesson('structural', 'Structural ambiguity: one string, several trees', f'''
<p>"John saw Mary with a telescope" has no ambiguous word. Yet it has two meanings, because the same words can be grouped into two different trees.</p>
{table(['Reading', 'Where the phrase attaches', 'Meaning'], [
    ['Instrument', 'To the verb phrase (high attachment)', 'John used a telescope to see Mary'],
    ['Possession', 'To the noun phrase Mary (low attachment)', 'John saw Mary, who had a telescope']])}
{viz('ppattach')}
<p>This is <b>prepositional phrase attachment ambiguity</b>. Grammar allows both trees, so only world knowledge or context can choose. "Ate pizza with a fork" prefers the verb (a fork is a tool), "ate pizza with olives" prefers the noun (olives are a topping), yet the two strings have exactly the same shape.</p>
<h3>Ambiguity grows very fast</h3>
<p>Add more phrases and the number of trees explodes. Church and Patil (1982) showed that a verb, its object and <i>k</i> prepositional phrases can be bracketed in a number of ways given by the Catalan numbers.</p>
{fx('Catalan numbers', '<i>C</i><sub><i>n</i></sub> = ' + frac('1', '<i>n</i> + 1') + ' × (2<i>n</i> choose <i>n</i>) = ' + frac('(2<i>n</i>)!', '(<i>n</i> + 1)! <i>n</i>!'), 'With <i>k</i> phrases the count is <i>C</i><sub><i>k</i>+1</sub>: 2, 5, 14, 42, 132 for <i>k</i> = 1 to 5.', key=True)}
{steps('Why "I saw the man on the hill with a telescope" has 5 readings', [
    'There are k = 2 phrases: "on the hill" and "with a telescope".',
    'The count is C<sub>3</sub> = (1 ÷ 4) × (6 choose 3) = 20 ÷ 4 = 5.',
    'Two of the five: I was on the hill using a telescope, or the man was on a hill that had a telescope on it.',
    'A third phrase ("in the morning") would give C<sub>4</sub> = 14 trees from a short, ordinary sentence.'])}
{code('catalan')}
<h3>The 1985 advert</h3>
<p>Lecture 2 showed a real McDonnell Douglas slogan: "At last, a computer that understands you like your mother." The class found three readings.</p>
<ol>
<li>The computer understands you as well as your mother understands you (the intended one).</li>
<li>The computer understands that you like your mother.</li>
<li>The computer understands you as well as it understands your mother.</li>
</ol>
<p>Spoken aloud it adds a speech recognition problem, since "you like your mother" sounds almost like "your lie cured mother". And "mother" even has an old second sense, a slimy starter used to make vinegar. One slogan shows acoustic, lexical and structural ambiguity at once. "Copy the local patient files to disk" adds an adjective attachment puzzle: are the patients local or the files?</p>
{note('If an exam asks you to classify an example, ask one question: does any single word have two meanings? If yes, lexical. If every word is clear but the grouping can change, structural.', 'exam')}
''', kw=['structural ambiguity', 'PP attachment', 'prepositional phrase attachment', 'telescope', 'high attachment', 'low attachment', 'Catalan numbers', 'Church and Patil', 'understands you like your mother', 'local patient files', 'ASR ambiguity'])

K.lesson('resolving', 'How machines resolve ambiguity', f'''
<p>The professor promised later lectures on the technology. Here is the map of how the field has attacked the problem, from rules to neural models.</p>
{table(['Era', 'Approach', 'How it decides'], [
    ['1960s to 1980s', 'Rules and heuristics', 'Hand written grammar plus defaults such as right association (attach low, to the nearest phrase)'],
    ['1990s to 2000s', 'Statistics from treebanks', 'Count how often a verb or noun takes this preposition in a hand parsed corpus, choose the more likely tree'],
    ['2010s onward', 'Contextual neural models', 'Each word vector depends on the whole sentence, so telescope near astronomy and telescope near ship get different representations']])}
{fx('Lexical association for attachment', 'P(verb attachment) ≈ ' + frac('<i>c</i>(verb, prep)', '<i>c</i>(verb, prep) + <i>c</i>(noun, prep)'), 'In the spirit of Hindle and Rooth (1993): compare how strongly the preposition goes with the verb and with the noun in a large corpus.')}
{ladder(
    '<p>Many sentences can mean two things. People pick the meaning that makes most sense in the situation. A computer has to learn the same habit from lots of examples.</p>',
    '<p>Lexical ambiguity is solved by word sense disambiguation, for example Lesk overlap. Structural ambiguity is solved by a parser that scores competing trees, for example with counts of which words go with which preposition.</p>',
    '<p>Probabilistic parsers (chapter 5.3) assign every tree a probability and return the most likely one. Attachment decisions are a classic benchmark. Lexicalised models that condition on the head words beat plain grammars because "eat with fork" and "eat with olives" differ only in the head noun of the phrase.</p>',
    '<p>Large models still fail on carefully built ambiguity tests. The class tried ChatGPT and Gemini live and found errors on these classic sentences. Research asks whether models represent several readings at once, how they use discourse to decide, and how to evaluate when even people disagree, as the class did on the cat and the wall.</p>')}
{scene('a voice assistant in a hospital', '<p>A nurse says "copy the local patient files to disk". If the assistant reads "local patient" it might search for patients from the local area. The safe design is to detect that two readings are possible and ask, exactly what SHRDLU did with "grasp the pyramid" (chapter 1.3). In medicine, a wrong guess costs more than one clarifying question.</p>')}
''', kw=['resolving ambiguity', 'right association', 'late closure', 'treebank', 'Penn Treebank', 'lexical association', 'Hindle and Rooth', 'contextual embeddings', 'clarifying question'])

# ---------------------------------------------------------------- quiz
K.quiz('e', '"I sat near a bank" is an example of which kind of ambiguity?', ['Structural', 'Lexical', 'Phonetic only', 'None'], 1,
       'Is one word responsible?', 'The single word bank has two meanings, so it is lexical ambiguity.')
K.quiz('e', '"John saw Mary with a telescope" is ambiguous because', ['telescope has two meanings', 'the phrase "with a telescope" can attach to the verb or to Mary', 'saw is a noun', 'English has no grammar'], 1,
       'Every word is clear.', 'Both trees are grammatical. The meaning changes with the attachment, which is structural ambiguity.')
K.quiz('e', 'Words that sound the same but differ in spelling and meaning, like pear and peer, are', ['Homographs', 'Homophones', 'Synonyms', 'Antonyms'], 1,
       'phone means sound.', 'Homophones share pronunciation only.')
K.quiz('m', 'mouth of a person and mouth of a river is an example of', ['Homonymy', 'Polysemy', 'A homophone', 'Structural ambiguity'], 1,
       'Are the senses related?', 'Both senses come from one origin and share the idea of an opening, which is polysemy.')
K.quiz('m', 'Simplified Lesk chooses a sense by', ['Picking the first sense always', 'Counting words shared between the context and each sense gloss', 'Parsing the sentence', 'Translating the word'], 1,
       'Gloss means dictionary definition.', 'The sense whose definition overlaps most with the surrounding words wins.')
K.quiz('m', 'How many parse trees does a verb, its object and 2 prepositional phrases have?', ['2', '4', '5', '6'], 2,
       'Catalan number C3.', 'C3 = 5. Church and Patil showed the count follows the Catalan numbers.')
K.quiz('m', 'Which reading of "a computer that understands you like your mother" was the advertiser\'s intended one?', [
    'The computer knows that you like your mother', 'The computer understands you as well as your mother does', 'The computer understands you as well as it understands your mother', 'The computer is your mother'], 1,
    'Think of the flattering one.', 'The other two readings are grammatical too, which is the point of the example.')
K.quiz('h', 'Right association (late closure) predicts that in "I saw the man with the telescope" the phrase attaches to', ['The verb saw', 'The nearest noun phrase, the man', 'The subject I', 'Nothing'], 1,
       'Attach to the most recent phrase.', 'The heuristic prefers low attachment to the nearest phrase. It is a default, often wrong when the verb strongly takes the preposition.')
K.quiz('h', 'A counts based attachment model sees c(ate, with) = 30 and c(pizza, with) = 10. Which attachment does it pick?', ['Noun', 'Verb', 'Both equally', 'It cannot decide'], 1,
       'Compute 30 ÷ 40.', 'P(verb) = 0.75, so it attaches to the verb. It gives the same answer for "with olives", which shows why head words of the phrase also matter.')
K.quiz('h', 'Why can "100% accuracy" be undefined for some ambiguous sentences?', ['Computers are slow', 'People themselves disagree on the reading when there is no context, so there is no single true answer', 'Accuracy is always undefined', 'Because of tokenisation'], 1,
       'Remember the class vote on the cat and the wall.', 'Without context there may be no gold label to score against, not just a hard one.')
K.quiz('x', 'Which pair shows that the right attachment depends on the head noun inside the prepositional phrase?', [
    'saw the man / saw the woman', 'ate pizza with a fork / ate pizza with olives', 'the bank / a bank', 'run / running'], 1,
    'Same verb, object and preposition.', 'Only the noun after "with" changes, yet the attachment flips, so a model must look at that noun.')
K.quiz('x', 'Spoken "you like your mother" against "your lie cured mother" is an ambiguity at which stage?', ['Morphology', 'Speech recognition (acoustic)', 'Pragmatics', 'Discourse'], 1,
       'Which system turns sound into words?', 'The audio is nearly identical, so the speech recogniser must choose the word sequence, usually with a language model.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the Catalan number C<sub>2</sub>?', '2', 'C<sub>n</sub> = (2n)! ÷ ((n + 1)! n!).',
       ['n = 2: (2n)! = 4! = 24.', '(n + 1)! n! = 3! × 2! = 6 × 2 = 12.', eq('C<sub>2</sub> = 24 ÷ 12 = 2'), 'So one prepositional phrase gives 2 trees, the telescope case.'], check=2)
K.calc('e', 'A sentence has one ambiguous word with 3 senses and one with 2 senses. How many sense combinations are there?', '6', 'Multiply.',
       ['Word 1 can take 3 senses.', 'Word 2 can take 2 senses.', eq('3 × 2 = 6 combinations')], check=6)
K.calc('m', 'How many parse trees does "verb + object + 3 prepositional phrases" have?', '14', 'Use C<sub>k+1</sub> with k = 3.',
       ['k + 1 = 4.', 'C<sub>4</sub> = 8! ÷ (5! × 4!) = 40,320 ÷ (120 × 24) = 40,320 ÷ 2,880.', eq('C<sub>4</sub> = 14')], check=14)
K.calc('m', 'Lesk: the context words are {river, water, fishing, sat} and the river gloss is {river, water, stream, fishing, grass}. What is the overlap?', '3', 'Count the shared words.',
       ['river is in both.', 'water is in both.', 'fishing is in both. sat is not in the gloss.', eq('overlap = 3')], check=3)
K.calc('m', 'Counts: c(saw, with) = 60 and c(Mary, with) = 25. What is P(verb attachment)? Give three decimals.', '0.706', 'Divide the verb count by the total.',
       ['Total = 60 + 25 = 85.', eq('P = 60 ÷ 85 ≈ 0.706'), 'Above 0.5, so the model attaches to the verb.'], check=60 / 85, tol=0.0005)
K.calc('m', 'In a class poll on the cat and wall picture, 18 of 30 students chose the full arc. What fraction chose another path?', '0.4', 'Take the rest.',
       ['Other paths: 30 − 18 = 12.', eq('12 ÷ 30 = 0.4'), 'Forty percent disagree with the majority on a short, everyday sentence.'], check=0.4)
K.calc('h', 'What is C<sub>5</sub>, the number of trees for a verb, an object and 4 prepositional phrases?', '42', 'C<sub>5</sub> = (1 ÷ 6) × (10 choose 5).',
       ['10 choose 5 = 252.', '252 ÷ 6 = 42.', eq('C<sub>5</sub> = 42')], check=42)
K.calc('h', 'Catalan numbers grow roughly like 4<sup>n</sup>. Using exact values, what is C<sub>6</sub> ÷ C<sub>5</sub>? Give two decimals.', '3.14', 'C<sub>6</sub> = 132 and C<sub>5</sub> = 42.',
       ['C<sub>6</sub> = (1 ÷ 7) × (12 choose 6) = 924 ÷ 7 = 132.', 'Ratio 132 ÷ 42.', eq('≈ 3.14'), 'The ratio C<sub>n+1</sub> ÷ C<sub>n</sub> = 2(2n + 1) ÷ (n + 2) climbs towards 4 as n grows.'], check=132 / 42, tol=0.005)
K.calc('h', 'A sentence has 2 prepositional phrases (5 trees) and 2 ambiguous words with 2 senses each. If all are independent, how many full readings?', '20', 'Multiply trees by sense choices.',
       ['Trees: C<sub>3</sub> = 5.', 'Sense choices: 2 × 2 = 4.', eq('5 × 4 = 20 readings')], check=20)
K.calc('x', 'A parser chooses verb attachment when P(verb) ≥ 0.5. If c(noun, prep) = 45, what is the smallest whole verb count that gives verb attachment?', '45', 'Solve v ÷ (v + 45) ≥ 0.5.',
       ['v ÷ (v + 45) ≥ 0.5 means v ≥ 0.5v + 22.5.', '0.5v ≥ 22.5, so v ≥ 45.', eq('smallest v = 45'), 'At v = 45 the two are tied and the rule picks the verb.'], check=45)
K.calc('x', 'Using the formula C<sub>n+1</sub> = C<sub>n</sub> × 2(2n + 1) ÷ (n + 2), find C<sub>7</sub> from C<sub>6</sub> = 132.', '429', 'Use n = 6.',
       ['2(2 × 6 + 1) = 2 × 13 = 26.', 'n + 2 = 8.', eq('C<sub>7</sub> = 132 × 26 ÷ 8 = 3,432 ÷ 8 = 429')], check=429)

# ---------------------------------------------------------------- assignments
K.assign('catalan', 'e', 'Count the parse trees',
         '<p>Write <code>trees(k)</code> that returns how many parse trees a verb, its object and <code>k</code> prepositional phrases have, using the Catalan number C<sub>k+1</sub>.</p>',
         '''
def trees(k):
    # your code here
    pass
''', [('trees(1)', 2), ('trees(2)', 5), ('trees(3)', 14), ('trees(6)', 429)],
         '''
from math import comb

def trees(k):
    n = k + 1
    return comb(2 * n, n) // (n + 1)
''', 'C(n) = comb(2n, n) // (n + 1).', '<p>Six phrases already give 429 trees. A parser cannot list them all for long sentences, which is why chart parsing (chapter 5.3) shares work between trees.</p>')
K.assign('lesk', 'm', 'Simplified Lesk',
         '<p>Write <code>lesk(sentence, senses, stop)</code>. <code>senses</code> maps a sense name to a gloss string. Lower case the sentence, split on spaces, drop words in <code>stop</code>, and return the sense with the largest overlap. On a tie return the sense that comes first in the dictionary.</p>',
         '''
def lesk(sentence, senses, stop):
    # your code here
    pass
''', [("lesk('I fished from the river bank', {'money': 'cash loan account', 'river': 'river water fish'}, {'i', 'the', 'from'})", 'river'),
      ("lesk('my loan from the bank', {'money': 'cash loan account', 'river': 'river water fish'}, {'my', 'the', 'from'})", 'money'),
      ("lesk('a bank', {'money': 'cash', 'river': 'water'}, {'a'})", 'money')],
         '''
def lesk(sentence, senses, stop):
    words = {w for w in sentence.lower().split() if w not in stop}
    best, best_score = None, -1
    for sense, gloss in senses.items():
        score = len(words & set(gloss.split()))
        if score > best_score:
            best, best_score = sense, score
    return best
''', 'Use a set intersection and keep the best score seen so far. Use a strict greater than so the first sense wins ties.',
         '<p>The third test has no overlap at all, so the first sense is returned. Real systems fall back to the most frequent sense, which is a strong baseline.</p>')
K.assign('attach', 'm', 'Decide an attachment from counts',
         '<p>Write <code>attach(cv, cn)</code> that returns <code>\'verb\'</code> when cv ÷ (cv + cn) is at least 0.5 and <code>\'noun\'</code> otherwise. If both counts are 0 return <code>\'noun\'</code> (the right association default).</p>',
         '''
def attach(cv, cn):
    # your code here
    pass
''', [('attach(60, 25)', 'verb'), ('attach(5, 80)', 'noun'), ('attach(10, 10)', 'verb'), ('attach(0, 0)', 'noun')],
         '''
def attach(cv, cn):
    if cv + cn == 0:
        return 'noun'
    return 'verb' if cv / (cv + cn) >= 0.5 else 'noun'
''', 'Handle the zero total first to avoid dividing by zero.', '<p>Falling back to low attachment when there is no evidence is exactly the old right association heuristic.</p>')

K.must('Two kinds', 'Lexical: one word, several meanings (bank, over). Structural: one string, several trees (telescope).')
K.must('Word types', 'Homonymy (unrelated meanings), polysemy (related senses), homophones (same sound), homographs (same spelling).')
K.must('Lesk', 'Pick the sense whose gloss shares most words with the context. A counting version of Firth.')
K.must('Catalan growth', 'A verb, object and k prepositional phrases have C(k + 1) trees: 2, 5, 14, 42, 132.')
K.must('Resolution', 'Rules (right association), treebank statistics (lexical association), contextual neural models. Ask when the cost of a wrong guess is high.')
K.must('Lecture examples', 'I sat near a bank. The cat jumped over the wall. John saw Mary with a telescope. Understands you like your mother. Copy the local patient files.')

T = K.topic(
    slug='ambiguity', topic='ambiguity', step=(1, 'Language and meaning', 'nlp-language', 'What language is, why it is ambiguous, and what it would mean for a machine to understand it.', 'School and college'),
    title='Ambiguity: why language is hard for machines', short='Ambiguity', badge='1.2', minutes=35,
    lead='One word with two meanings, one sentence with two trees. See how the lecture examples break apart, count how fast the readings grow, and try the methods machines use to choose.',
    desc='Lexical and structural ambiguity, homonymy, polysemy, homophones, word sense disambiguation with Lesk, prepositional phrase attachment, Catalan numbers, the 1985 advert, and rule based, statistical and neural resolution.',
    summary='Lexical against structural ambiguity, the Lesk method, PP attachment, Catalan growth of parse trees and how machines resolve ambiguity.',
    keywords=['ambiguity', 'lexical ambiguity', 'structural ambiguity', 'word sense disambiguation', 'Lesk', 'PP attachment', 'Catalan numbers', 'homonymy', 'polysemy', 'telescope'],
    recap='<p>Ambiguity comes from single words (lexical) or from grouping (structural), and the readings multiply quickly. Machines choose with overlaps, counts or context vectors, and a careful system asks when it cannot be sure.</p>')
