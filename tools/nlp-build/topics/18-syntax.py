# Chapter 5.5: syntax. Source: lecture 9 (POS deck slides 36 to 44: constituents, phrase structure and bracket notation,
# Fed raises interest rates, the movement test, dependency structure with "The boy put the tortoise on the rug",
# argument and modifier labels, the comparison table, the elephant in my pajamas, the tools) and problems H5 to H10.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('brackets', r'''
# Read a bracketed tree and count phrase nodes, part of speech nodes and leaves (problem H5)
s = "(S (NP (Det the) (N dog)) (VP (V chased) (NP (Det a) (N cat))))"
toks = s.replace("(", " ( ").replace(")", " ) ").split()
phrases, pos, leaves, stack = [], [], [], []
i = 0
while i < len(toks):
    if toks[i] == "(":
        label = toks[i + 1]
        if toks[i + 2] not in "()":
            pos.append(label)
            leaves.append(toks[i + 2])
            i += 4
            continue
        phrases.append(label)
        i += 2
    else:
        i += 1
print("phrase nodes:", phrases, " part of speech nodes:", pos)
print("non terminals:", len(phrases) + len(pos), " leaves:", leaves)
''')

K.code('cfg', r'''
# A tiny context free grammar and every sentence it generates
G = {"S": [["NP", "VP"]], "NP": [["Det", "N"]], "VP": [["V", "NP"], ["V"]],
     "Det": [["the"]], "N": [["dog"], ["cat"]], "V": [["chased"], ["slept"]]}

def expand(sym):
    if sym not in G:
        return [[sym]]
    out = []
    for rhs in G[sym]:
        parts = [[]]
        for x in rhs:
            parts = [p + q for p in parts for q in expand(x)]
        out += parts
    return out

sents = [" ".join(s) for s in expand("S")]
print(len(sents), "sentences:")
print(sents)
''')

K.code('deps', r'''
# Check that a dependency analysis is a tree: one head per word, a single root, no cycles, and whether it is projective
words = ["The", "boy", "put", "the", "tortoise", "on", "the", "rug"]
head = [2, 3, 0, 5, 3, 3, 8, 6]           # head of word i + 1, 0 = ROOT
roots = [i + 1 for i, h in enumerate(head) if h == 0]
ok = True
for i in range(1, len(words) + 1):        # follow heads upwards, it must reach ROOT
    seen, j = set(), i
    while j != 0 and j not in seen:
        seen.add(j)
        j = head[j - 1]
    ok = ok and j == 0
arcs = [(min(h, d), max(h, d)) for d, h in enumerate(head, 1) if h]
cross = [(a, b) for a in arcs for b in arcs if a[0] < b[0] < a[1] < b[1]]
print("root:", [words[r - 1] for r in roots], " acyclic:", ok, " arcs:", len(head), " projective:", not cross)
print("children of put:", [words[d - 1] for d, h in enumerate(head, 1) if h == 3])
''')

K.code('pcfg', r'''
# Problem H9: the two elephant parses differ in one rule each
R = {"S->NP VP": 1.0, "NP->Pro": 0.3, "NP->Det N": 0.5, "NP->NP PP": 0.2,
     "VP->V NP": 0.7, "VP->VP PP": 0.3, "PP->P NP": 1.0}
vp_attach = ["S->NP VP", "NP->Pro", "VP->VP PP", "VP->V NP", "NP->Det N", "PP->P NP", "NP->Det N"]
np_attach = ["S->NP VP", "NP->Pro", "VP->V NP", "NP->NP PP", "NP->Det N", "PP->P NP", "NP->Det N"]

def prob(rules):
    p = 1.0
    for r in rules:
        p *= R[r]
    return p

a, b = prob(vp_attach), prob(np_attach)
print("VP attachment:", round(a, 5), " NP attachment:", round(b, 5), " ratio:", round(a / b, 2))
''')

K.code('catalan', r'''
# Parses of "V NP" followed by k prepositional phrases grow as the Catalan numbers C(k + 1)
from math import comb
for k in range(1, 7):
    n = k + 1
    print(k, "PPs:", comb(2 * n, n) // (n + 1), "parses")
''')

K.lesson('constituency', 'Constituents and phrase structure', f'''
<p>A constituent, or phrase, is a group of words that acts as one unit. All of these are noun phrases, and each can sit before a verb: "Harry the Horse", "the Broadway coppers", "they", "a high class spot such as Mindy\'s", "three parties from Brooklyn". Phrase structure nests these units into a hierarchy: N + N gives the NP "interest rates", V + NP gives the VP "raises interest rates", and NP + VP gives a sentence S.</p>
{fxs(fx('Bracket notation', '(S (NP (N Fed)) (VP (V raises) (NP (N interest) (N rates))))', 'Each opening bracket starts a node and names its label. Treebanks store trees this way, on one line, called a linearised tree.', key=True))}
{viz('parsetree')}
<p>Every phrase type contains a word of its own kind, its head: a VP contains a verb (VB*), an NP a noun (NN*), an ADJP an adjective (JJ*), a PP a preposition (IN).</p>
<h3>How do we know something is a constituent?</h3>
{table(['Test', 'What you do', '"about drugs" in "John talked to the children about drugs"'], [
    ['Movement', 'Move the group as a block', 'John talked [about drugs] [to the children]: fine'],
    ['Fragment answer', 'Use it alone as an answer', 'What did John talk about? About drugs.'],
    ['Substitution', 'Replace it with a pro form (it, there, did so)', 'John talked to the children about it.'],
    ['Coordination', 'Join it with a similar group', 'about drugs and about school'],
    ['Clefting', '"It was X that …"', 'It was about drugs that John talked to the children.']])}
<p>"drugs to the children" fails every test: it cannot move as a block, cannot answer a question and has no pro form. It straddles two prepositional phrases, so it is not a constituent (problem H6). A star marks an ungrammatical sentence, such as *John talked drugs to the children about.</p>
{steps('Problem H5: read a tree', [
    'Tree: (S (NP (Det the) (N dog)) (VP (V chased) (NP (Det a) (N cat)))).',
    'Root S has two children, NP and VP. VP has V and a second NP.',
    'Constituents: [the dog] NP, [a cat] NP, [chased a cat] VP, [the dog chased a cat] S.',
    'Phrase nodes S, NP, VP, NP: 4. Part of speech nodes Det, N, V, Det, N: 5.',
    eq('9 non terminals and 5 leaves')])}
{code('brackets')}
''', kw=['constituent', 'phrase', 'phrase structure', 'bracket notation', 'treebank', 'head', 'movement test', 'substitution', 'fragment', 'coordination', 'cleft', 'H5', 'H6'])

K.lesson('cfg', 'Context free grammars', f'''
{fxs(fx('CFG four tuple', '(<i>N</i>, Σ, <i>R</i>, <i>S</i>)', '<i>N</i> non terminals (S, NP, VP …), Σ terminals (the words), <i>R</i> rules of the form A → β, and the start symbol <i>S</i>. A sentence is grammatical if S can be rewritten into it, and the rewriting history is its parse tree.', key=True))}
{table(['Rule', 'Reads as'], [
    ['S → NP VP', 'a sentence is a noun phrase followed by a verb phrase'],
    ['NP → Det N', 'a noun phrase can be a determiner and a noun'],
    ['VP → V NP | V', 'a verb phrase is a verb with or without an object'],
    ['Det → the, N → dog | cat, V → chased | slept', 'the lexicon: which words fill each slot']])}
<p>This small grammar generates 2 × (2 × 2 + 2) = 12 sentences, from "the dog chased the cat" to "the cat slept". Some read well. Others, such as "the cat chased the cat", are grammatical but odd. Add the determiner a and the count jumps to 40. Grammar decides structure, not sense.</p>
{code('cfg')}
<p>The Penn Treebank has about a million words of Wall Street Journal text with hand built trees. Reading the rules off those trees and counting them gives a probabilistic grammar, used in the last lesson.</p>
{deep('Why not a finite state machine?', '<p>Sentences can nest without limit: "the rat the cat the dog chased ate died". Matching each subject with its verb needs a stack, which an FSA does not have. Formally, centre embedding produces patterns like a<sup>n</sup>b<sup>n</sup>, which no FSA can recognise but a CFG can. In practice deep nesting is rare, which is why finite state tools still cover most local patterns. Parsing a CFG takes O(n³) with the CKY chart algorithm, the parsing cousin of Viterbi.</p>')}
''', kw=['context free grammar', 'CFG', 'rules', 'non terminal', 'terminal', 'start symbol', 'lexicon', 'Penn Treebank', 'centre embedding', 'CKY'])

K.lesson('dependency', 'Dependency structure', f'''
<p>Instead of phrase nodes, dependency grammar links words directly. "You can get a lot done with binary relations among the words." Each link goes from a head (governor) to a dependent (modifier) and may carry a label.</p>
{viz('deptree')}
<p>In "The boy put the tortoise on the rug", put is the root and has three immediate children: boy, tortoise and on. The, the and rug are grandchildren, not children. Whether on or rug hangs from put is a design choice: older schemes and the slide let the preposition head the phrase, while Universal Dependencies makes content words heads, so put → rug (obl) and rug → on (case).</p>
{table(['Kind', 'Labels', 'Meaning'], [
    ['Argument', 'nsubj, obj, iobj', 'the participants the verb needs: who paints, what is painted, to whom'],
    ['Modifier', 'det, amod, nmod, advmod', 'optional extras: determiners, adjectives, noun and adverb modifiers']])}
{steps('Problem H7: The student reads books', [
    'The root is the main verb: reads ← ROOT.',
    'student → head reads, nsubj. books → head reads, obj. The → head student, det.',
    'Each word has exactly one head. 4 words give 4 arcs including ROOT.',
    'No cycles, and no arcs cross when drawn above the sentence, so the tree is projective.'])}
{code('deps')}
{note('A student asked whether this is a DAG, as in compilers. It is stricter: a tree. Every word has exactly one head, there are no cycles, and a sentence of n words has exactly n arcs counting the ROOT arc.', 'exam')}
{table(['', 'Dependency structure', 'Phrase structure'], [
    ['Shows', 'head to dependent relations, with function labels', 'nested phrases with category labels (NP, VP)'],
    ['Nodes', 'only the words', 'words plus phrase nodes'],
    ['Good for', 'free word order, relation extraction, who did what to whom', 'phrase boundaries, coordination, grammar engineering'],
    ['Treebank', 'Universal Dependencies, 100+ languages', 'Penn Treebank']])}
''', kw=['dependency', 'head', 'dependent', 'root', 'nsubj', 'obj', 'det', 'Universal Dependencies', 'projective', 'tree', 'DAG', 'H7'])

K.lesson('attachment', 'Attachment ambiguity and PCFGs', f'''
<p>Groucho Marx: "One morning I shot an elephant in my pajamas. How he got into my pajamas I\'ll never know." Two ambiguities sit here. Lexical: shot with a gun or with a camera. Attachment: the phrase "in my pajamas" attaches inside the verb phrase (I was wearing them) or inside the noun phrase (the elephant was).</p>
{fxs(fx('Probabilistic CFG', 'P(tree) = ∏<sub>rules A → β used</sub> P(β | A), &nbsp; with Σ<sub>β</sub> P(β | A) = 1 for each A', 'Rule probabilities come from treebank counts: P(VP → V NP) = C(VP → V NP) ÷ C(VP). Choose the tree with the higher product.', key=True))}
{viz('pcfg')}
{steps('Problem H9: who wore the pajamas?', [
    'Both parses use S → NP VP, NP → Pro, VP → V NP, PP → P NP and NP → Det N twice.',
    'VP attachment adds VP → VP PP (0.3). NP attachment adds NP → NP PP (0.2).',
    'Shared factor: 1.0 × 0.3 × 0.7 × 1.0 × 0.5 × 0.5 = 0.0525.',
    eq('VP attachment = 0.0525 × 0.3 = 0.01575, &nbsp; NP attachment = 0.0525 × 0.2 = 0.0105'),
    'Ratio 1.5, so the PCFG says "I was in my pajamas". It never looked at the words elephant or pajamas.'])}
{code('pcfg')}
<h3>How fast ambiguity grows</h3>
<p>"I saw the man on the hill with a telescope." Each prepositional phrase can attach to the verb or to any noun before it, as long as no arcs cross. If "on the hill" attaches to man, "with a telescope" can go to saw, man or hill: 3 parses. If it attaches to saw, "with" can go to saw or hill but not to man, since that arc would cross: 2 parses. That is 5 in all (problem H10).</p>
{fxs(fx('Catalan growth', '<i>C<sub>n</sub></i> = ' + frac('(2<i>n</i>)!', '(<i>n</i> + 1)! <i>n</i>!') + ' &nbsp; parses with <i>k</i> PPs = <i>C</i><sub><i>k</i>+1</sub>: 2, 5, 14, 42, 132 …', 'Exponential growth, just like tag sequences. Chart parsers (CKY) share sub trees in O(n³) time.'))}
{code('catalan')}
{table(['Tool', 'What it gives you'], [
    ['NLTK', 'corpora (Brown, Penn Treebank sample), n-gram and perceptron taggers, chunkers, CFG and PCFG parsers'],
    ['spaCy', 'fast pipelines: tokens, POS, lemmas, dependency parse, named entities'],
    ['Stanza', 'neural pipeline for 60+ languages with UPOS, XPOS, UD dependency parsing and NER']])}
{note('In spaCy, every token knows its text, t.pos_, t.dep_ and t.head.text. Running it on the elephant sentence shows which attachment the trained parser picked.', 'tip')}
{scene('a legal contract search', '<p>A law firm searches contracts for "payment to the supplier within 30 days". A dependency parser finds that "within 30 days" attaches to payment, not to supplier, so the system extracts a deadline on the payment. Read with the wrong attachment, the clause would describe a supplier located within 30 days, which is nonsense. Getting attachment right is what turns text into the correct database row.</p>')}
{ladder(
    '<p>Sentences have structure. Words group into phrases, or each word hangs from another word. The same words can sometimes be grouped two ways, and that changes the meaning.</p>',
    '<p>Constituents pass movement, substitution and fragment tests. CFGs generate trees. Dependency trees have one head per word and n arcs. A PCFG multiplies rule probabilities to pick between parses.</p>',
    '<p>CKY parses a CFG in Chomsky normal form in O(n³ |G|). The inside algorithm sums over trees like the forward algorithm. Lexicalised PCFGs (Collins 1999) and Hindle and Rooth\'s attachment statistics fix the blindness of plain PCFGs to words. Transition based and graph based dependency parsers work in linear or cubic time.</p>',
    '<p>Neural parsers with biaffine attention reach about 95% unlabelled attachment on English. Research covers non projective parsing, cross lingual parsing with Universal Dependencies, and probing whether large language models encode syntax trees in their hidden states.</p>')}
''', kw=['attachment ambiguity', 'elephant in my pajamas', 'PCFG', 'rule probability', 'H9', 'Catalan', 'H10', 'CKY', 'NLTK', 'spaCy', 'Stanza'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A constituent is', ['Any two words', 'A group of words that acts as one unit', 'A single letter', 'A sentence boundary'], 1,
       'Think of "the yellow dog".', 'It can move, be replaced by a pro form and answer a question as a unit.')
K.quiz('e', 'In (S (NP (N Fed)) (VP …)), the label of the root is', ['NP', 'S', 'VP', 'N'], 1,
       'The first label after the first bracket.', 'S, the sentence.')
K.quiz('e', 'In a dependency tree, the root of "The student reads books" is', ['The', 'student', 'reads', 'books'], 2,
       'The main verb.', 'reads is attached to ROOT.')
K.quiz('m', 'How many immediate children does put have in "The boy put the tortoise on the rug"?', ['2', '3', '5', '7'], 1,
       'Not grandchildren.', 'boy, tortoise and on.')
K.quiz('m', 'Which test shows that "about drugs" is a constituent?', ['It contains a noun', 'It can move as a block and answer a question alone', 'It is short', 'It ends the sentence'], 1,
       'Movement and fragment tests.', 'John talked [about drugs] [to the children], and "About drugs." as an answer.')
K.quiz('m', 'A dependency tree for 9 words has how many arcs, counting the ROOT arc?', ['8', '9', '10', '18'], 1,
       'One head per word.', 'Each word has exactly one incoming arc.')
K.quiz('m', 'nsubj and obj are', ['Modifier dependencies', 'Argument dependencies', 'POS tags', 'Chunk tags'], 1,
       'Participants the verb needs.', 'Subject and object are arguments of the verb.')
K.quiz('m', 'In Universal Dependencies, "on the rug" attaches as', ['put → on, on → rug', 'put → rug (obl), rug → on (case)', 'rug → put', 'on → put'], 1,
       'Content words are heads.', 'The noun heads the phrase and the preposition is a case marker.')
K.quiz('h', 'In the elephant sentence, the two parses differ in', ['Every rule', 'VP → VP PP against NP → NP PP', 'The lexicon', 'The start symbol'], 1,
       'Shared rules cancel.', 'Only those two rules differ, so the decision compares them.')
K.quiz('h', 'A plain PCFG chooses attachment using', ['The meaning of pajamas', 'Rule frequencies only, not the words', 'A dictionary', 'Word embeddings'], 1,
       'Look at what the product contains.', 'It never looks at elephant or pajamas, which lexicalised parsers fix.')
K.quiz('h', 'Why can a finite state automaton not handle all of English?', ['Too many words', 'Centre embedding needs a stack, like a<sup>n</sup>b<sup>n</sup>', 'It cannot read spaces', 'It has no start state'], 1,
       'Nesting without limit.', 'Matching each subject with its verb needs memory that grows with depth.')
K.quiz('x', 'With 3 prepositional phrases after "V NP", how many projective parses are there?', ['5', '8', '14', '42'], 2,
       'C(k + 1).', 'C₄ = 14.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many arcs, including ROOT, does a dependency tree for a 12 word sentence have?', '12', 'One head per word.',
       ['Every word has exactly one head.', 'The root word\'s head is ROOT.', eq('12 arcs')], check=12, tol=0.01)
K.calc('e', 'Problem H5: (S (NP (Det the) (N dog)) (VP (V chased) (NP (Det a) (N cat)))). How many non terminal nodes?', '9', 'Phrase nodes plus part of speech nodes.',
       ['Phrase nodes: S, NP, VP, NP = 4.', 'Part of speech nodes: Det, N, V, Det, N = 5.', eq('4 + 5 = 9')], check=9, tol=0.01)
K.calc('e', 'With VP → V NP at 0.7 and VP → VP PP at 0.3, are the VP rules a valid distribution? Give their sum.', '1', 'Rules for one non terminal sum to 1.',
       ['VP rules: V NP and VP PP.', '0.7 + 0.3.', eq('= 1.0, valid')], check=1, tol=0.001)
K.calc('m', 'Problem H9: shared rules 1.0 × 0.3 × 0.7 × 1.0 × 0.5 × 0.5. What is the shared factor? Four decimals.', '0.0525', 'Multiply the six.',
       ['1.0 × 0.3 = 0.3.', '× 0.7 = 0.21, × 1.0 = 0.21.', eq('× 0.5 × 0.5 = 0.0525')], check=0.0525, tol=0.00005)
K.calc('m', 'Problem H9: P(VP attachment) = shared 0.0525 × P(VP → VP PP) 0.3. Five decimals.', '0.01575', 'One more rule.',
       ['Shared factor: 0.0525.', 'Extra rule: 0.3.', eq('0.0525 × 0.3 = 0.01575')], check=0.01575, tol=0.000005)
K.calc('m', 'Problem H9: ratio of VP attachment (0.01575) to NP attachment (0.0105)?', '1.5', 'Shared factors cancel.',
       ['Only 0.3 against 0.2 differ.', '0.01575 ÷ 0.0105.', eq('= 1.5, VP attachment wins')], check=1.5, tol=0.001)
K.calc('m', 'A CFG has S → NP VP, NP → Det N with Det → the | a and N → dog | cat, and VP → V NP | V with V → chased | slept. How many sentences does it generate?', '40', 'Count NPs and VPs.',
       ['NP: 2 determiners × 2 nouns = 4.', 'VP: V NP gives 2 × 4 = 8, V alone gives 2, so 10.', eq('S: 4 × 10 = 40')], check=40, tol=0.01)
K.calc('h', 'Problem H10: how many projective parses does "I saw the man on the hill with a telescope" have?', '5', 'Case on where "on the hill" attaches.',
       ['on → man: with → saw, man or hill. 3 parses.', 'on → saw: with → saw or hill, man would cross. 2 parses.', eq('3 + 2 = 5 = C₃')], check=5, tol=0.01)
K.calc('h', 'Catalan C₅ = 10! ÷ (6! × 5!) gives the parses for 4 PPs. Compute it.', '42', '10! = 3,628,800.',
       ['6! = 720 and 5! = 120, product 86,400.', '3,628,800 ÷ 86,400.', eq('= 42')], check=42, tol=0.01)
K.calc('h', 'In the pcfg animation, P(VP → V NP) = 1 − P(VP → VP PP). With P(VP → VP PP) = 0.3, what P(NP → NP PP) makes the two parses tie?', '0.3', 'Set the two differing products equal.',
       ['VP attach ∝ 0.3 × 0.7.', 'NP attach ∝ 0.7 × P(NP → NP PP).', eq('0.21 = 0.7 x gives x = 0.3')], check=0.3, tol=0.001)
K.calc('x', 'CKY parsing costs about n³ × |G|. For a 30 word sentence and |G| = 1,000 rules, how many basic steps?', '27000000', 'Cube then multiply.',
       ['n³ = 27,000.', '× 1,000 rules.', eq('27,000,000')], check=27000000, tol=0.5)

# ---------------------------------------------------------------- assignments
K.assign('count', 'm', 'Read a bracketed tree',
         '<p>Write <code>tree_stats(s)</code> for a bracketed tree string. Return (phrase nodes, part of speech nodes, leaves) as counts. A part of speech node is a bracket whose only child is a word.</p>',
         '''
def tree_stats(s):
    # your code here
    pass
''', [('tree_stats("(S (NP (Det the) (N dog)) (VP (V chased) (NP (Det a) (N cat))))")', (4, 5, 5)),
      ('tree_stats("(S (NP (N Fed)) (VP (V raises) (NP (N interest) (N rates))))")', (4, 4, 4))],
         '''
def tree_stats(s):
    t = s.replace("(", " ( ").replace(")", " ) ").split()
    phrases = pos = 0
    for i in range(len(t) - 3):
        if t[i] == "(":
            if t[i + 2] not in "()" and t[i + 3] == ")":
                pos += 1
            else:
                phrases += 1
    return (phrases, pos, pos)
''', 'Split the brackets into tokens. After "(", look two tokens ahead: a word there means a part of speech node.', '<p>Every leaf hangs from exactly one part of speech node, so leaves equal part of speech nodes in a treebank style tree.</p>')
K.assign('dtree', 'h', 'Is it a valid projective dependency tree?',
         '<p>Write <code>check(head)</code>. head[i] is the head of word i + 1, with 0 for ROOT. Return (is_tree, is_projective). is_tree means exactly one root and every word reaches ROOT without a cycle. is_projective means no two arcs cross (arcs a and b cross when a.left &lt; b.left &lt; a.right &lt; b.right). If it is not a tree, return False for both.</p>',
         '''
def check(head):
    # your code here
    pass
''', [('check([2, 3, 0, 5, 3, 3, 8, 6])', (True, True)), ('check([2, 0, 2, 2])', (True, True)),
      ('check([2, 1, 0])', (False, False)), ('check([0, 4, 1, 1])', (True, False))],
         '''
def check(head):
    n = len(head)
    if sum(1 for h in head if h == 0) != 1:
        return (False, False)
    for i in range(1, n + 1):
        seen, j = set(), i
        while j != 0:
            if j in seen:
                return (False, False)
            seen.add(j)
            j = head[j - 1]
    arcs = [(min(h, d), max(h, d)) for d, h in enumerate(head, 1) if h]
    for a in arcs:
        for b in arcs:
            if a[0] < b[0] < a[1] < b[1]:
                return (True, False)
    return (True, True)
''', 'Follow heads upwards from each word, remembering where you have been.', '<p>In the last test the arc 1 → 3 and the arc 4 → 2 cross, so the tree is valid but not projective.</p>')
K.assign('pcfgp', 'm', 'Score a parse with a PCFG',
         '<p>Write <code>tree_prob(rules, used)</code>. rules maps a rule string such as "VP->V NP" to its probability and used lists the rules a parse uses, with repeats. Return the product rounded to 6 decimals.</p>',
         '''
def tree_prob(rules, used):
    # your code here
    pass
''', [('tree_prob({"S->NP VP": 1.0, "NP->Pro": 0.3, "NP->Det N": 0.5, "VP->V NP": 0.7, "VP->VP PP": 0.3, "PP->P NP": 1.0}, ["S->NP VP", "NP->Pro", "VP->VP PP", "VP->V NP", "NP->Det N", "PP->P NP", "NP->Det N"])', 0.01575),
      ('tree_prob({"S->NP VP": 1.0, "NP->Pro": 0.3, "NP->Det N": 0.5, "NP->NP PP": 0.2, "VP->V NP": 0.7, "PP->P NP": 1.0}, ["S->NP VP", "NP->Pro", "VP->V NP", "NP->NP PP", "NP->Det N", "PP->P NP", "NP->Det N"])', 0.0105)],
         '''
def tree_prob(rules, used):
    p = 1.0
    for r in used:
        p *= rules[r]
    return round(p, 6)
''', 'A parse is just a bag of rules. Multiply them.', '<p>These are the two elephant parses from problem H9.</p>')

K.must('Constituents', 'Groups that act as one unit. Tests: movement, substitution by a pro form, fragment answer, coordination, clefting.')
K.must('CFG', 'Four tuple (N, Σ, R, S). Rules A → β. Bracket notation stores trees. Penn Treebank supplies trees and rule counts.')
K.must('Dependencies', 'Head → dependent arcs with labels (nsubj, obj, det). A tree: one head per word, n arcs with ROOT, no cycles. UD makes content words heads.')
K.must('PCFG', 'P(tree) = product of rule probabilities, rules for each non terminal sum to 1. Elephant: VP attach 0.01575 against 0.0105, ratio 1.5.')
K.must('Ambiguity growth', 'k PPs give Catalan C(k + 1) parses: 2, 5, 14, 42. CKY parses in O(n³).')

T = K.topic(
    slug='syntax', topic='syntax', step=(5, 'Tagging and syntax', 'nlp-syntax', 'Tag every word with its part of speech using HMMs and Viterbi, mark chunks and names with IOB, and draw constituency and dependency trees.', 'College and masters'),
    title='Constituency and dependency syntax', short='Syntax', badge='5.5', minutes=50,
    lead='Find the phrases a sentence is built from, draw them as constituency and dependency trees, and let a probabilistic grammar decide who wore the pajamas.',
    desc='Constituents and the tests that find them, bracket notation and Fed raises interest rates, context free grammars, dependency trees with The boy put the tortoise on the rug, argument and modifier labels, Universal Dependencies, the elephant in my pajamas decided by a PCFG, Catalan growth of attachment ambiguity, and NLTK, spaCy and Stanza.',
    summary='Constituency tests, CFGs, dependency trees, PCFGs, attachment ambiguity and Catalan growth.',
    keywords=['constituency', 'dependency', 'CFG', 'PCFG', 'parse tree', 'attachment ambiguity', 'Universal Dependencies', 'Catalan'],
    recap='<p>Phrase structure nests words into constituents that pass movement and substitution tests. Dependency structure links each word to its head in a tree. When a sentence has several trees, a PCFG multiplies rule probabilities to choose, and the number of candidate trees grows as the Catalan numbers.</p>')
