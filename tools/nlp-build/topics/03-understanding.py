# Chapter 1.3: can machines understand language. Source: lecture 2 and 3 (Marr's tri-level hypothesis and the robot
# fly activity, the four camps of AI, the Turing test and its problems, qualia, the Total Turing Test, NLP against CL
# against NLU, ELIZA and SHRDLU, building blocks of NLU, metrics including BLEU, surprisal and dependency length,
# Firth and Shannon, the octopus test, Ettinger, and the NLP trinity) plus lecture 1 (symbol grounding, Chinese room).
from cvkit import Kit, fx, fxs, frac, sqrt, mat, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('metrics', r'''
# Precision, recall and F1 for a tiny named entity tagger
gold = {"Ram", "Jodhpur", "IIT"}            # entities a person marked
pred = {"Ram", "Jodhpur", "Monday"}         # entities the system found

tp = len(gold & pred)                       # found and correct
fp = len(pred - gold)                       # found but wrong
fn = len(gold - pred)                       # missed
precision = tp / (tp + fp)
recall = tp / (tp + fn)
f1 = 2 * precision * recall / (precision + recall)
print("tp, fp, fn =", tp, fp, fn)
print("precision =", round(precision, 3), " recall =", round(recall, 3), " F1 =", round(f1, 3))
''')

K.code('deplen', r'''
# Total dependency length: add the distance from every word to its head
words = ["John", "gave", "Mary", "a", "book"]
heads = [2, 0, 2, 5, 2]          # 1 based position of each head, 0 marks the root

total = 0
for i, h in enumerate(heads, start=1):
    if h:
        d = abs(i - h)
        total += d
        print(f"{words[i-1]:5} -> {words[h-1]:5} distance {d}")
print("total dependency length =", total)
''')

K.lesson('marr', 'Marr\'s three levels and the robot that flies', f'''
<p>The lecture frames the course with one question: can machines understand language? Language is linked to thought, thought to thinking, and on the working view of cognitive science, thinking is information processing. If minds and computers both process information, we can ask whether a machine can carry out the same processing. That is why vision and language share one goal: reverse engineering human perception and language.</p>
{table(['Level (Marr, 1982)', 'Question', 'What it specifies'], [
    ['1. Computational', 'What and why?', 'The goal of the computation and why it is the right goal'],
    ['2. Algorithmic or representational', 'How?', 'The representation of input and output, and the algorithm that turns one into the other'],
    ['3. Implementational', 'Where?', 'The physical substrate: neurons, gears, silicon']])}
<p>The professor\'s summary: level 1 suggests level 2 and level 2 predicts level 3 when you design. When you validate, level 3 confirms level 2 and level 2 explains level 1.</p>
{steps('Class activity: make a robot fly', [
    'Computational: the goal is flight, so produce an upward force greater than the weight (more than 9.8 newtons for every kilogram).',
    'Algorithmic: flap the wings to make thrust, keep a streamlined body, run a control loop of ground, climb, balance, descend, ground.',
    'Implementational: wings, motors, light materials and sensors.',
    'Design runs top down. "Flap" in level 2 already predicts that level 3 needs a wing. Validation runs bottom up: a wing that flaps confirms the algorithm and the goal.'])}
<p>Marr\'s own textbook example is a cash register. Its goal is addition (level 1), done by column addition with carrying (level 2), in gears or transistors (level 3). An abacus and a chip both add with very different algorithms and hardware, which is why you cannot understand a system just by staring at its hardware.</p>
{note('The professor calls jumping straight to hardware and algorithms "the rush that all computer engineers make". A purely data driven language model is tuned at levels 2 and 3 without a clear level 1 answer to what understanding is.', 'warn')}
''', kw=['Marr', 'tri-level hypothesis', 'computational level', 'algorithmic level', 'implementational level', 'robot fly', 'cash register', 'information processing', 'reverse engineering cognition'])

K.lesson('turing', 'The Turing test and what it misses', f'''
<p>Definitions of AI fall into a two by two grid, the scheme of Russell and Norvig\'s textbook.</p>
{table(['', 'Like humans', 'Rationally'], [
    ['Thinking', 'Systems that think like humans (Haugeland, Bellman)', 'Systems that think rationally (Charniak and McDermott, Winston)'],
    ['Acting', 'Systems that act like humans (Kurzweil, Rich and Knight)', 'Systems that act rationally (Schalkoff, Luger and Stubblefield)']])}
<p>Alan Turing (1950) replaced "can machines think?" with an operational question. A judge chats by text with a hidden person and a hidden machine. If the judge cannot reliably tell which is which, the machine passes. This defines intelligence by behaviour, not by inner experience.</p>
<h3>Two problems the lecture lists</h3>
<ol>
<li>It is not reproducible. The result depends on which judge asks and on the setup.</li>
<li>There is no physical interaction. It tests only text, never seeing or acting.</li>
</ol>
<p>A student added that behaviour leaves out subjective experience. Philosophers call this <b>qualia</b>, the "what it is like" of seeing red. Nagel\'s bat (1974), Jackson\'s Mary who knows all the physics of colour but has never seen red (1982), and Chalmers\'s hard problem (1995) all point at the same gap.</p>
<h3>The Total Turing Test</h3>
<p>Stevan Harnad\'s Total Turing Test asks the machine to perceive and act in the world, not just chat. To pass it a computer needs seven capabilities.</p>
{table(['Capability', 'Why'], [
    ['Natural language processing', 'Talk with the examiner'], ['Knowledge representation', 'Store what it is told'],
    ['Automated reasoning', 'Answer questions and draw conclusions'], ['Machine learning', 'Adapt and find patterns'],
    ['Vision', 'Recognise the examiner\'s actions and objects'], ['Motor control', 'Act on objects when asked'], ['Other senses', 'Hearing, touch, smell']])}
<p>This is why the course is called Foundations of Vision and Language. Even a vending machine joins vision (reading the menu), action (the purchase) and, with speech, language.</p>
''', kw=['Turing test', 'imitation game', 'operational definition', 'Russell and Norvig', 'four camps of AI', 'qualia', 'hard problem', 'Mary room', 'Total Turing Test', 'Harnad'])

K.lesson('eliza-shrdlu', 'ELIZA and SHRDLU: talking against understanding', f'''
<p>Two famous systems from MIT give opposite answers to the question "if a machine fools you, does it understand?"</p>
{viz('eliza')}
<p>Joseph Weizenbaum\'s ELIZA (1966) imitated a Rogerian therapist who reflects what the client says. It found keywords, swapped pronouns and pasted your own words into a template: "my boyfriend made me come here" became YOUR BOYFRIEND MADE YOU COME HERE. Users still confided in it, an effect now named the <b>ELIZA effect</b>. The slide says it in blue: <b>producing an appropriate looking response is not necessarily the same as understanding</b>.</p>
{viz('blocks')}
<p>Terry Winograd\'s SHRDLU (around 1970) lived in a small simulated world of blocks, pyramids and a box. It parsed English commands, kept a model of the scene, reasoned and moved a simulated arm. It asked "I DON\'T UNDERSTAND WHICH PYRAMID YOU MEAN" when a phrase fit two objects, resolved "it" to the right block, answered "how many blocks are not in the box?" from its world model, and said "I CAN\'T" when asked to stack two pyramids.</p>
{table(['', 'ELIZA (1966)', 'SHRDLU (about 1970)'], [
    ['Creator', 'Joseph Weizenbaum, MIT', 'Terry Winograd, MIT'],
    ['Pipeline', 'Language → pattern match → response', 'Language → world model → reasoning → action → response'],
    ['Grounding', 'None, text in and text out', 'In a simulated micro world'],
    ['Domain', 'General chat', 'Blocks world only'],
    ['Lesson', 'Fluent is not understanding', 'Language can be procedure tied to knowledge and action, at small scale']])}
{note('SHRDLU\'s "OK" matters because it reports that a grounded action was carried out, closing the loop between language and behaviour.', 'tip')}
''', kw=['ELIZA', 'Weizenbaum', 'Rogerian', 'pattern matching', 'ELIZA effect', 'SHRDLU', 'Winograd', 'blocks world', 'grounding', 'declarative and procedural knowledge'])

K.lesson('building', 'NLP, CL and NLU, and how systems are measured', f'''
<p>Students kept asking how the three names differ. They differ in what drives the work, not in subject.</p>
{table(['Field', 'Orientation', 'Goal'], [
    ['NLP', 'Engineering, application driven', 'Build tools: search, speech to text, translation, sentiment'],
    ['Computational linguistics', 'Science, theory driven', 'Model the human cognitive system for language'],
    ['NLU', 'The shared end goal', 'A system that really understands, built from description to representation to evaluation']])}
<h3>The building blocks</h3>
<ol>
<li><b>Corpus and annotation.</b> Text (or speech and video) with labels, such as part of speech tags for "John sat near the bank" or the root "run" for "running". Universal Dependencies gives one scheme across many languages. There are also child language, learner and eye tracking corpora.</li>
<li><b>Model.</b> Hand built grammars such as the English Resource Grammar, or statistical and neural models learned from data.</li>
<li><b>Validation</b> with performance metrics and cognitive metrics.</li>
</ol>
{fxs(
    fx('Precision, recall, F1', 'P = ' + frac('TP', 'TP + FP') + ', R = ' + frac('TP', 'TP + FN') + ', F1 = ' + frac('2PR', 'P + R'), 'Precision: how much of what you found is right. Recall: how much of the truth you found.', key=True),
    fx('BLEU', 'BLEU = BP · exp(Σ<sub><i>n</i></sub> <i>w</i><sub><i>n</i></sub> log <i>p</i><sub><i>n</i></sub>)', '<i>p</i><sub><i>n</i></sub> is clipped n-gram precision, BP = 1 if <i>c</i> &gt; <i>r</i>, else e<sup>1 − <i>r</i>/<i>c</i></sup>. Papineni et al. 2002.', key=True),
    fx('Surprisal', 'S(<i>w</i>) = −log<sub>2</sub> P(<i>w</i> | context)', 'Surprising words take longer to read (Hale 2001, Levy 2008).'),
    fx('Dependency length', 'DL = Σ<sub><i>i</i></sub> |<i>i</i> − head(<i>i</i>)|', 'Human sentences keep related words close (Gibson 2000).'))}
{code('metrics')}
{viz('bleu')}
{viz('surprisal')}
{code('deplen')}
<p>Cognitive metrics ask whether a model behaves like people, not just whether it scores well. "Apples and oranges" is expected, so it has low surprisal. "Apples and coconut" is surprising and carries more information.</p>
''', kw=['NLP vs CL vs NLU', 'computational linguistics', 'corpus', 'annotation', 'Universal Dependencies', 'precision', 'recall', 'F1', 'BLEU', 'brevity penalty', 'surprisal', 'dependency length', 'cognitive metrics'])

K.lesson('form-meaning', 'Can form alone give meaning?', f'''
<p>Is NLP just a giant knowledge engineering project, solved by enough data? The lecture gives the case for and against.</p>
<h3>The case for data</h3>
<ul>
<li><b>Firth (1957)</b>: "You shall know a word by the company it keeps." The distributional hypothesis behind word2vec, GloVe and the embeddings inside BERT.</li>
<li><b>Shannon (1948)</b>: information depends on probability, not meaning, I(<i>x</i>) = −log<sub>2</sub> P(<i>x</i>). Next word prediction and cross entropy loss come straight from this.</li>
</ul>
<h3>The case against form alone</h3>
<ul>
<li>Huge models need data and compute most languages do not have, which splits the world into high and low resource languages.</li>
<li><b>The octopus test</b> (Bender and Koller, 2020). An octopus taps a cable between two islanders and learns to imitate one perfectly. When a bear attacks and help is needed to build a weapon from sticks, it can only produce plausible text, because it never had access to sticks or bears. Form alone does not give meaning.</li>
<li><b>Ettinger (2020)</b> ran psycholinguistic tests on BERT and found it largely insensitive to negation ("a robin is a ___" and "a robin is not a ___" get similar completions) and weak at predicting roles in events.</li>
<li><b>Symbol grounding</b> (Harnad, 1990): symbols defined only by other symbols are like a dictionary in a language you cannot read. <b>The Chinese room</b> (Searle, 1980): following a rulebook to produce fluent output need not involve understanding.</li>
<li>Rare events carry the most information, yet frequency based learning handles them worst.</li>
</ul>
<h3>The NLP trinity</h3>
<p>Every NLP problem sits on three axes: the <b>language</b> (Hindi, Marathi, English, French), the <b>problem</b> in rising difficulty (morphology, POS tagging, chunking, parsing, semantics, discourse and coreference) and the <b>algorithm</b> (HMM, MEMM, CRF, RNN). A tagger built for one point does not move to another for free.</p>
{ladder(
    '<p>A parrot can repeat words without knowing what they mean. A computer that copies patterns from text may also sound clever without understanding. To understand, words must connect to real things and real goals.</p>',
    '<p>Processing maps input text to output text with learned statistics. Understanding also links symbols to referents and intentions. ELIZA processes. SHRDLU understands a little, inside its blocks world.</p>',
    '<p>The debate maps onto Marr: large models are optimised at the algorithmic level with a proxy goal (next token prediction) whose relation to the computational level goal (meaning, intent) is unclear. Diagnostic suites such as Ettinger\'s test specific competences rather than overall scores.</p>',
    '<p>Open questions include whether distributional signals implicitly encode reference, how multimodal and embodied training changes grounding, how to learn from rare but informative events, and how to evaluate understanding when benchmarks leak into training data.</p>')}
''', kw=['Firth', 'distributional hypothesis', 'Shannon information', 'octopus test', 'Bender and Koller', 'Ettinger', 'negation', 'symbol grounding', 'Chinese room', 'NLP trinity', 'coreference', 'low resource'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which of Marr\'s levels answers the question "what is the goal and why"?', ['Computational', 'Algorithmic', 'Implementational', 'None'], 0,
       'The top level.', 'The computational level states the goal and the logic of the strategy.')
K.quiz('e', 'ELIZA produced its replies by', ['Deep semantic analysis', 'Keyword pattern matching and templates', 'A world model', 'Neural networks'], 1,
       'Remember the pronoun swap.', 'It matched keywords, swapped pronouns and filled templates. No meaning was represented.')
K.quiz('e', 'The Turing test judges a machine by', ['Its hardware', 'Whether a judge can tell it from a person in text conversation', 'Its accuracy on a benchmark', 'Its speed'], 1,
       'An operational definition.', 'Intelligence is defined by indistinguishable behaviour in a text chat.')
K.quiz('m', 'What does SHRDLU do that ELIZA cannot?', ['Use capital letters', 'Ground words in a world model, reason and act', 'Talk about mothers', 'Run faster'], 1,
       'Think of the blocks.', 'SHRDLU links phrases to objects, plans and moves them, and asks when a reference is ambiguous.')
K.quiz('m', 'Which is the engineering, application driven field?', ['Computational linguistics', 'NLP', 'Phonology', 'Philosophy of mind'], 1,
       'Search, translation, speech to text.', 'NLP builds tools. CL models the human language system. NLU is the shared goal.')
K.quiz('m', 'Which is a cognitive metric rather than a performance metric?', ['F1', 'Accuracy', 'Surprisal', 'BLEU'], 2,
       'Which one links to reading times?', 'Surprisal relates to human processing difficulty, measured for example with eye tracking.')
K.quiz('m', 'BLEU\'s brevity penalty exists because', ['Long outputs are always wrong', 'Precision alone rewards very short safe outputs', 'References are short', 'It speeds up scoring'], 1,
       'What if the output is just "the"?', 'A tiny output can have perfect precision. The penalty e^(1 − r/c) lowers the score when c is shorter than r.')
K.quiz('h', 'The octopus test argues that', ['Octopuses are intelligent', 'A system trained only on linguistic form cannot learn meaning, which needs links to referents and intent', 'BLEU is flawed', 'Data is never useful'], 1,
       'Bender and Koller, 2020.', 'The octopus masters the statistics of the messages but has never touched a coconut or a bear.')
K.quiz('h', 'Ettinger found that BERT was largely insensitive to', ['Spelling', 'Negation', 'Punctuation', 'Word length'], 1,
       'A robin is (not) a ...', 'Its completions barely changed when "not" was added, a failure a system that understood would not make.')
K.quiz('h', 'Which capability is NOT on the Total Turing Test list?', ['Vision', 'Motor control', 'Knowledge representation', 'Quantum computing'], 3,
       'Seven capabilities, all about perceiving, knowing and acting.', 'NLP, knowledge representation, reasoning, learning, vision, motor control and other senses.')
K.quiz('x', 'In Marr\'s terms, the main critique of pure next word prediction models is that', ['They are slow at level 3', 'They are optimised at levels 2 and 3 without a clear level 1 account of what understanding is', 'They lack level 2', 'They use the wrong hardware'], 1,
       'Which level asks "why this goal"?', 'Next word prediction is a proxy goal. Whether it is the right computational goal for understanding is not argued.')
K.quiz('x', 'The NLP trinity says a solution at one point does not transfer for free. Which change moves along the problem axis?', [
    'From Hindi to French', 'From POS tagging to coreference resolution', 'From HMM to CRF', 'From GPU to CPU'], 1,
    'The three axes are language, problem and algorithm.', 'Morphology, POS tagging, chunking, parsing, semantics and discourse are steps along the problem axis.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A tagger finds 8 entities, 6 of them correct. What is its precision?', '0.75', 'Correct found ÷ all found.',
       ['TP = 6, everything found = 8.', eq('P = 6 ÷ 8 = 0.75'), 'Three quarters of what it reports is right.'], check=0.75)
K.calc('e', 'There are 10 true entities and the tagger finds 6 of them. What is its recall?', '0.6', 'Correct found ÷ all true.',
       ['TP = 6, true entities = 10.', eq('R = 6 ÷ 10 = 0.6'), 'It misses 4 of the 10.'], check=0.6)
K.calc('m', 'With precision 0.75 and recall 0.6, what is F1? Give three decimals.', '0.667', 'F1 = 2PR ÷ (P + R).',
       ['2 × 0.75 × 0.6 = 0.9.', 'P + R = 1.35.', eq('F1 = 0.9 ÷ 1.35 ≈ 0.667')], check=0.9 / 1.35, tol=0.0005)
K.calc('e', 'P(oranges | apples and) = 0.5. What is its surprisal in bits?', '1', 'S = −log<sub>2</sub> P.',
       ['log<sub>2</sub> 0.5 = −1.', eq('S = −(−1) = 1 bit'), 'An even chance carries exactly one bit.'], check=1)
K.calc('m', 'P(coconut | apples and) = 0.05. What is its surprisal? Give two decimals.', '4.32', 'S = −log<sub>2</sub> 0.05.',
       ['log<sub>2</sub> 0.05 = ln 0.05 ÷ ln 2 = −2.9957 ÷ 0.6931.', '≈ −4.3219.', eq('S ≈ 4.32 bits'), 'Over four times the surprisal of "oranges".'], check=4.3219, tol=0.005)
K.calc('m', 'Candidate "the the the the" against reference "the cat is on the mat". What is the clipped unigram precision?', '0.5', '"the" appears twice in the reference.',
       ['The candidate has 4 unigrams, all "the".', 'Clip the count of "the" to its reference count, 2.', eq('p<sub>1</sub> = 2 ÷ 4 = 0.5')], check=0.5)
K.calc('m', 'A candidate has 4 words and the closest reference has 6. What is the brevity penalty? Give four decimals.', '0.6065', 'BP = e<sup>1 − r/c</sup> when c ≤ r.',
       ['r ÷ c = 6 ÷ 4 = 1.5.', '1 − 1.5 = −0.5.', eq('BP = e<sup>−0.5</sup> ≈ 0.6065')], check=0.6065, tol=0.00006)
K.calc('h', 'BLEU with N = 2, BP = 1, p<sub>1</sub> = 0.8 and p<sub>2</sub> = 0.45. Give three decimals.', '0.6', 'Geometric mean of the two precisions.',
       ['Uniform weights 1/2 each.', 'exp(0.5 ln 0.8 + 0.5 ln 0.45) = √(0.8 × 0.45).', eq('√0.36 = 0.6'), 'BLEU = 1 × 0.6 = 0.600.'], check=0.6)
K.calc('h', 'For "John gave Mary a book" with heads John→gave, Mary→gave, a→book, book→gave, what is the total dependency length?', '6', 'Add |position − head position| for every word except the root.',
       ['Positions: John 1, gave 2, Mary 3, a 4, book 5.', 'Distances: John |1 − 2| = 1, Mary |3 − 2| = 1, a |4 − 5| = 1, book |5 − 2| = 3.', eq('DL = 1 + 1 + 1 + 3 = 6')], check=6)
K.calc('x', 'A model gives P = 0.25 to each of 4 possible next words. What is the average surprisal (entropy) in bits?', '2', 'Every word has the same surprisal.',
       ['Each surprisal is −log<sub>2</sub> 0.25 = 2 bits.', 'The average of four equal values is that value.', eq('H = 4 × 0.25 × 2 = 2 bits')], check=2)
K.calc('x', 'Two judges each guess "human or machine" for 100 chats. A machine passes if judges are right at most 55% of the time. Judge A is right 52 times and judge B 61 times. How many judges did the machine fool by this rule?', '1', 'Compare each score with 55.',
       ['Judge A: 52 ≤ 55, fooled.', 'Judge B: 61 &gt; 55, not fooled.', eq('fooled judges = 1'), 'The same machine passes with one judge and fails with another, which is the reproducibility problem of the Turing test.'], check=1)

# ---------------------------------------------------------------- assignments
K.assign('prf', 'e', 'Precision, recall and F1',
         '<p>Write <code>prf(gold, pred)</code> for two sets. Return <code>[precision, recall, f1]</code>, each rounded to 3 decimals. If a denominator is 0, use 0 for that value.</p>',
         '''
def prf(gold, pred):
    # your code here
    pass
''', [("prf({'Ram', 'Jodhpur', 'IIT'}, {'Ram', 'Jodhpur', 'Monday'})", [0.667, 0.667, 0.667]), ("prf({'a', 'b'}, {'a'})", [1.0, 0.5, 0.667]), ("prf({'a'}, set())", [0, 0.0, 0])],
         '''
def prf(gold, pred):
    tp = len(gold & pred)
    p = tp / len(pred) if pred else 0
    r = tp / len(gold) if gold else 0
    f = 2 * p * r / (p + r) if p + r else 0
    return [round(p, 3), round(r, 3), round(f, 3)]
''', 'tp is the size of the intersection.', '<p>An empty prediction has undefined precision. Libraries such as scikit-learn report 0 and warn, which is the same choice made here.</p>')
K.assign('bleu1', 'm', 'Clipped unigram precision',
         '<p>Write <code>p1(candidate, references)</code>. Both are strings of words separated by spaces, <code>references</code> is a list. Count each candidate word at most as many times as it appears in the reference where it appears most. Return matches ÷ candidate length, rounded to 4 decimals.</p>',
         '''
def p1(candidate, references):
    # your code here
    pass
''', [("p1('the the the the', ['the cat is on the mat'])", 0.5), ("p1('the cat is on the mat', ['there is a cat on the mat', 'the cat sat on the mat'])", 1.0),
      ("p1('a dog barked', ['the cat sat'])", 0.0)],
         '''
def p1(candidate, references):
    c = candidate.split()
    match = 0
    for w in set(c):
        best = max(r.split().count(w) for r in references)
        match += min(c.count(w), best)
    return round(match / len(c), 4)
''', 'Loop over the distinct candidate words, clip each count, and add.', '<p>This is p<sub>1</sub> of BLEU. The full score multiplies the geometric mean of p<sub>1</sub> to p<sub>4</sub> by the brevity penalty.</p>')
K.assign('deplen', 'm', 'Total dependency length',
         '<p>Write <code>dep_length(heads)</code>. <code>heads[i]</code> is the 1 based position of the head of word <code>i + 1</code>, or 0 for the root. Return the sum of |position − head| over all non root words.</p>',
         '''
def dep_length(heads):
    # your code here
    pass
''', [('dep_length([2, 0, 2, 5, 2])', 6), ('dep_length([0])', 0), ('dep_length([2, 0, 2])', 2), ('dep_length([4, 4, 4, 0])', 6)],
         '''
def dep_length(heads):
    return sum(abs(i - h) for i, h in enumerate(heads, start=1) if h)
''', 'Use enumerate with start=1 and skip the root.', '<p>Comparing this sum for real sentences and for shuffled ones shows the dependency locality effect from the lecture.</p>')

K.must('Marr', 'Computational (what and why), algorithmic (how, representation), implementational (where). Design top down, validate bottom up.')
K.must('Turing test', 'Operational, text only, not reproducible. Qualia are outside it. The Total Turing Test adds perception and action, seven capabilities.')
K.must('ELIZA and SHRDLU', 'ELIZA: keyword patterns, no understanding. SHRDLU: world model, reasoning, action and clarifying questions in a blocks world.')
K.must('Fields and pipeline', 'NLP builds tools, CL models cognition, NLU is the shared goal. Corpus and annotation, model, then validation.')
K.must('Metrics', 'P = TP ÷ (TP + FP), R = TP ÷ (TP + FN), F1 = 2PR ÷ (P + R). BLEU = BP · exp(Σ w log p). Surprisal −log₂ P. Dependency length.')
K.must('Form against meaning', 'Firth and Shannon support data. The octopus test, Ettinger, symbol grounding and the Chinese room warn that form is not meaning.')

T = K.topic(
    slug='machine-understanding', topic='understanding', step=(1, 'Language and meaning', 'nlp-language', 'What language is, why it is ambiguous, and what it would mean for a machine to understand it.', 'School and college'),
    title='Can machines understand language?', short='Machine understanding', badge='1.3', minutes=45,
    lead='Use Marr\'s three levels to frame the question, see why the Turing test is not enough, chat with an ELIZA and command a tiny SHRDLU, then learn how NLU systems are built and measured and why form alone may not give meaning.',
    desc='Marr\'s tri-level hypothesis, the Turing test and the Total Turing Test, qualia, ELIZA and SHRDLU, NLP against CL against NLU, corpora and annotation, precision, recall, F1, BLEU, surprisal, dependency length, the octopus test, Ettinger and the NLP trinity.',
    summary='Marr\'s levels, Turing and Total Turing tests, ELIZA against SHRDLU, how NLU systems are built and scored, and the debate on form and meaning.',
    keywords=['natural language understanding', 'Marr', 'Turing test', 'ELIZA', 'SHRDLU', 'BLEU', 'F1', 'surprisal', 'octopus test', 'symbol grounding', 'NLP trinity'],
    recap='<p>Fluent output is not proof of understanding. Marr asks for the goal first, the Total Turing Test asks for perception and action, SHRDLU shows grounding at small scale, and metrics from F1 to surprisal measure different things.</p>')
