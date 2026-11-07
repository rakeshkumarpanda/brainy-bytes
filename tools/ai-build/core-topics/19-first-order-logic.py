# Chapter 7.3: first order logic, syntax and semantics. Follows Russell and Norvig, AIMA 4th ed., chapter 8
# (why first order logic, ontological commitments, models with Richard, John and the crown, terms, atomic and complex
# sentences, quantifiers and their pitfalls, equality, database semantics, the kinship domain, the wumpus world in
# first order logic, and the knowledge engineering process).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('model', r'''
# A small model: the objects and which relations hold. Then check quantified sentences by looping over objects.
objects = ["Richard", "John", "TheCrown"]
person = {"Richard", "John"}
king = {"John"}
crown = {"TheCrown"}
on_head = {("TheCrown", "John")}
brother = {("Richard", "John"), ("John", "Richard")}

# for all x: King(x) => Person(x)
print("all kings are persons:", all((x not in king) or (x in person) for x in objects))
# for all x: King(x) and Person(x)   (the common mistake)
print("everything is a king and a person:", all((x in king) and (x in person) for x in objects))
# exists x: Crown(x) and OnHead(x, John)
print("a crown is on John's head:", any((x in crown) and ((x, "John") in on_head) for x in objects))
# for all x: Person(x) => exists y: Brother(x, y)
print("every person has a brother:", all((x not in person) or any((x, y) in brother for y in objects) for x in objects))
''')

K.code('kin', r'''
# The kinship domain: define new relations from Parent with rules, then use them.
parent = [("Elizabeth", "Charles"), ("Philip", "Charles"), ("Elizabeth", "Anne"),
          ("Charles", "William"), ("Charles", "Harry")]

def children(p):
    return [c for a, c in parent if a == p]

def grandparents(x):
    # GrandParent(g, x) <=> exists p: Parent(g, p) and Parent(p, x)
    out = []
    for g, p in parent:
        if (p, x) in parent and g not in out:
            out.append(g)
    return out

def siblings(x):
    # Sibling(x, y) <=> x != y and exists p: Parent(p, x) and Parent(p, y)
    out = []
    for p, c in parent:
        if c == x:
            for s in children(p):
                if s != x and s not in out:
                    out.append(s)
    return out

print("grandparents of William:", grandparents("William"))
print("siblings of Charles:", siblings("Charles"))
print("siblings of Harry:", siblings("Harry"))
''')

K.lesson('why', 'Why we need more than propositional logic', f'''
{src('Russell and Norvig, AIMA 4th ed., section 8.1. The uploaded slides do not cover logic, so this step follows the textbook.')}
{wwh('First order logic (FOL, also called predicate logic) talks about <b>objects</b>, the <b>relations</b> between them and <b>functions</b> that map objects to objects. Quantifiers let one sentence speak about all objects, or about some object.',
     'Propositional logic has no way to say "a room is breezy if and only if a neighbouring room has a pit" once. It needs a separate sentence for every room: 16 rooms, 16 sentences, and a new set for every cave size. Natural language and mathematics talk about objects and their relations all the time.',
     'Replace fixed symbols like P<sub>1,2</sub> by atoms such as Pit([1,2]) built from a predicate and terms, and add ∀ (for all) and ∃ (there exists). One sentence, ∀s Breezy(s) ⇔ ∃r Adjacent(r, s) ∧ Pit(r), now covers every room of every cave.')}
{table(['Language (AIMA figure 8.1)', 'What exists in the world (ontological commitment)', 'What an agent believes about facts (epistemological commitment)'], [
    ['Propositional logic', 'facts', 'true, false, unknown'],
    ['First order logic', 'facts, objects, relations', 'true, false, unknown'],
    ['Temporal logic', 'facts, objects, relations, times', 'true, false, unknown'],
    ['Probability theory', 'facts', 'a degree of belief between 0 and 1'],
    ['Fuzzy logic', 'facts with a degree of truth between 0 and 1', 'a known interval value']])}
''', kw=['first order logic', 'predicate logic', 'objects', 'relations', 'functions', 'ontological commitment', 'epistemological commitment'])

K.lesson('syntax', 'Syntax: terms, atoms and sentences', f'''
{src('AIMA 4th ed., section 8.2.')}
{table(['Element', 'What it names', 'Examples'], [
    ['Constant symbol', 'one object', 'Richard, John, M1, 2'],
    ['Predicate symbol', 'a relation (true or false for its arguments)', 'Brother(·, ·), King(·), Adjacent(·, ·)'],
    ['Function symbol', 'a function: objects in, one object out', 'LeftLeg(·), Mother(·), +'],
    ['Variable', 'any object, to be fixed by a quantifier', 'x, y, s'],
    ['Term', 'a constant, a variable, or a function applied to terms', 'John, x, LeftLeg(John), Mother(Mother(x))'],
    ['Atomic sentence', 'a predicate applied to terms, or term = term', 'Brother(Richard, John), Father(x) = John'],
    ['Complex sentence', 'atoms joined by ¬ ∧ ∨ ⇒ ⇔', 'King(Richard) ∨ King(John)'],
    ['Quantified sentence', '∀x S or ∃x S', '∀x King(x) ⇒ Person(x)']])}
<p>A <b>term</b> names an object. A <b>sentence</b> is true or false. LeftLeg(John) is a term (a leg), King(John) is a sentence.</p>
{note('In this course and in the animations, names that start with a lower case letter are variables, and names that start with a capital letter are constants, predicates or functions. Prolog uses the opposite convention.', 'tip')}
''', kw=['syntax', 'constant', 'predicate', 'function symbol', 'variable', 'term', 'atomic sentence', 'quantifier'])

K.lesson('semantics', 'Semantics: models and interpretations', f'''
{src('AIMA 4th ed., section 8.2.1 and figure 8.2.')}
<p>A <b>model</b> of first order logic has a <b>domain</b>, the set of objects, and an <b>interpretation</b> that says which object each constant names, which tuples of objects each predicate holds for, and what each function returns.</p>
{steps('The textbook model (figure 8.2)', [
    'Domain: Richard the Lionheart, King John, the left legs of each, and a crown. Five objects.',
    'Relations: the brother relation holds for (Richard, John) and (John, Richard). OnHead holds for (crown, John). Person holds for Richard and John. King holds for John only. Crown holds for the crown.',
    'Function: LeftLeg maps Richard to Richard\'s left leg and John to John\'s left leg.',
    'Brother(Richard, John) is true here, King(Richard) is false.',
    eq('an atom is true when the objects named by its terms are in the relation named by its predicate')])}
<p>The animation below uses this model without the two legs, to keep the picture small.</p>
{viz('folmodel')}
{code('model')}
{note('First order logic has infinitely many models: any domain size from 1 upwards, and every interpretation of every symbol. So entailment cannot be checked by listing models, as we did with truth tables.', 'warn')}
''', kw=['model', 'domain', 'interpretation', 'Richard', 'King John', 'crown'])

K.lesson('quant', 'Quantifiers and their traps', f'''
{src('AIMA 4th ed., section 8.2.6.')}
{table(['Sentence', 'Read as', 'True when'], [
    ['∀x King(x) ⇒ Person(x)', 'all kings are persons', 'for every object, if it is a king then it is a person'],
    ['∃x Crown(x) ∧ OnHead(x, John)', 'some crown is on John\'s head', 'at least one object is a crown and on John\'s head'],
    ['∀x ∃y Loves(x, y)', 'everybody loves somebody', 'for each x there is a y (maybe different for each x)'],
    ['∃y ∀x Loves(x, y)', 'there is someone whom everybody loves', 'one y works for all x']])}
{table(['Rule of thumb', 'Why'], [
    ['∀ goes with ⇒', '∀x King(x) ∧ Person(x) says everything is a king and a person, which is far too strong'],
    ['∃ goes with ∧', '∃x Crown(x) ⇒ OnHead(x, John) is true as soon as one object is not a crown, so it says almost nothing'],
    ['Order matters for mixed quantifiers', '∀x ∃y and ∃y ∀x mean different things'],
    ['The same kind can be swapped', '∀x ∀y ≡ ∀y ∀x, ∃x ∃y ≡ ∃y ∃x']])}
{fxs(
    fx('De Morgan for quantifiers', '∀x ¬P ≡ ¬∃x P, ¬∀x P ≡ ∃x ¬P, ∀x P ≡ ¬∃x ¬P, ∃x P ≡ ¬∀x ¬P', '"Nobody likes parsnips" = "everybody dislikes parsnips".', key=True),
    fx('∀ as a big AND, ∃ as a big OR', '∀x P(x) ≡ P(o<sub>1</sub>) ∧ P(o<sub>2</sub>) ∧ ..., ∃x P(x) ≡ P(o<sub>1</sub>) ∨ P(o<sub>2</sub>) ∨ ...', 'Over a finite domain with objects o<sub>1</sub>, o<sub>2</sub>, ...'))}
<p><b>Equality</b>: t<sub>1</sub> = t<sub>2</sub> is true when both terms name the same object. "Richard has at least two brothers" is ∃x, y Brother(x, Richard) ∧ Brother(y, Richard) ∧ ¬(x = y). Without ¬(x = y), x and y could be the same brother.</p>
{deep('Database semantics', '<p>Databases and Prolog assume three extra things: <b>unique names</b> (different constants name different objects), the <b>closed world</b> assumption (an atom not known to be true is false), and <b>domain closure</b> (there are no objects other than those named). Under these rules "Richard has two brothers, John and Geoffrey" is simply Brother(John, Richard) ∧ Brother(Geoffrey, Richard). In full first order logic you must add ¬(John = Geoffrey) and say that no one else is a brother.</p>')}
''', kw=['universal quantifier', 'existential quantifier', 'nested quantifiers', 'De Morgan quantifiers', 'equality', 'database semantics', 'closed world'])

K.lesson('use', 'Using first order logic: kinship and the wumpus world', f'''
{src('AIMA 4th ed., section 8.3.')}
{table(['Kinship axiom', 'Meaning'], [
    ['∀m, c Mother(c) = m ⇔ Female(m) ∧ Parent(m, c)', 'a mother is a female parent'],
    ['∀w, h Husband(h, w) ⇔ Male(h) ∧ Spouse(h, w)', 'a husband is a male spouse'],
    ['∀p, c Parent(p, c) ⇔ Child(c, p)', 'parent and child are inverse relations'],
    ['∀g, c Grandparent(g, c) ⇔ ∃p Parent(g, p) ∧ Parent(p, c)', 'a grandparent is a parent of a parent'],
    ['∀x, y Sibling(x, y) ⇔ x ≠ y ∧ ∃p Parent(p, x) ∧ Parent(p, y)', 'siblings share a parent and are different people']])}
{code('kin')}
{table(['Wumpus world in FOL', 'Meaning'], [
    ['∀x, y, a, b Adjacent([x, y], [a, b]) ⇔ (x = a ∧ (y = b − 1 ∨ y = b + 1)) ∨ (y = b ∧ (x = a − 1 ∨ x = a + 1))', 'which rooms are neighbours, for any cave size'],
    ['∀s Breezy(s) ⇔ ∃r Adjacent(r, s) ∧ Pit(r)', 'one sentence for every room'],
    ['∀t, s At(Agent, s, t) ∧ Breeze(t) ⇒ Breezy(s)', 'what a percept at time t tells about room s']])}
{steps('The knowledge engineering process (AIMA 8.4)', [
    'Identify the questions the KB must answer.',
    'Assemble the relevant knowledge, often by talking to experts.',
    'Decide on a vocabulary of predicates, functions and constants (an ontology).',
    'Encode general knowledge about the domain as axioms.',
    'Encode the specific problem instance as facts.',
    'Pose queries to an inference procedure and get answers.',
    eq('debug the KB: a wrong answer means a missing or wrong axiom')])}
''', kw=['kinship', 'axioms', 'wumpus world FOL', 'adjacent', 'knowledge engineering', 'ontology'])

K.lesson('maths', 'The maths: counting interpretations', f'''
{fxs(
    fx('Interpretations over a fixed domain of d objects', 'd<sup>c</sup> × (2<sup>d</sup>)<sup>u</sup> × (2<sup>d²</sup>)<sup>b</sup>', 'c constants (each names one of d objects), u unary predicates (each is any subset of the d objects), b binary predicates (any subset of the d² pairs). Functions add more.', key=True),
    fx('A k-ary relation', '2<sup>d<sup>k</sup></sup> possible extensions', 'There are d<sup>k</sup> tuples, each in or out.'),
    fx('Grounding ∀', '∀x P(x) becomes d ground sentences', 'Over a finite domain, FOL can be turned into propositional logic. Functions make the set of ground terms infinite.'))}
{steps('Worked example: 2 constants, 1 binary predicate, d = 2 objects', [
    'Constants: 2² = 4 ways to map 2 constants to 2 objects.',
    'Binary predicate: d² = 4 pairs, so 2⁴ = 16 possible relations.',
    '4 × 16 = 64.',
    eq('64 interpretations for d = 2, and more for every larger d')])}
{steps('Worked example: ∀x ∃y Loves(x, y) over d = 3 people', [
    'Grounded, it is (L(a, a) ∨ L(a, b) ∨ L(a, c)) ∧ (L(b, a) ∨ ...) ∧ (L(c, a) ∨ ...).',
    'That is 3 clauses of 3 literals each.',
    'Each person needs at least one person they love.',
    eq('3 × 3 = 9 ground atoms involved')])}
''', kw=['number of interpretations', 'grounding', 'k-ary relation', 'counting models'])

K.lesson('compare', 'First order logic against its neighbours', f'''
{versus('Choosing a logic', ['', 'Propositional', 'First order', 'Higher order', 'Description logics'], [
    ['Talks about', 'fixed facts', 'objects, relations, functions', 'also relations of relations', 'classes and properties'],
    ['Can quantify over', 'nothing', 'objects', 'relations and functions too', 'objects, in limited patterns'],
    ['Entailment decidable', 'Yes', 'Semidecidable: a yes answer is found if true, but a search may never end if false', 'No complete proof method exists', 'Yes, for most variants'],
    ['Compactness', 'Low: one sentence per case', 'High', 'Highest', 'High for taxonomies'],
    ['Used in', 'SAT, hardware checking', 'Theorem provers, Prolog, databases', 'Proof assistants such as Coq and Lean', 'Web ontologies (OWL), medical terms (SNOMED)']],
    'first order logic is the usual choice: rich enough for most knowledge, with sound and complete proof methods (chapter 7.4), at the price that a proof search for a false query may not stop.')}
{scene('SQL is first order logic', '<p>A relational database query is a first order formula. SELECT name FROM person p WHERE EXISTS (SELECT * FROM parent q WHERE q.child = p.name) asks for all x with ∃y Parent(y, x). Codd built the relational model on this link in 1970, and database query languages still follow it.</p>')}
''', kw=['comparison', 'higher order logic', 'description logic', 'semidecidable', 'SQL', 'Codd'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Instead of a separate yes or no fact for every room, say things about all rooms at once: "every room next to a pit is breezy". First order logic gives you words for things (objects), how they relate, and "all" and "some".</p>',
    '<p>Terms name objects, atoms are predicates on terms, sentences combine atoms with connectives, ∀ and ∃. A model has a domain and an interpretation. Use ∀ with ⇒ and ∃ with ∧. Quantifier order matters. Equality and database semantics change what a list of facts means.</p>',
    '<p>Gödel\'s completeness theorem (1929): every entailed sentence has a proof, so entailment is semidecidable. Church and Turing (1936): entailment is not decidable. Löwenheim and Skolem: a set of sentences with an infinite model has models of every infinite size, so FOL cannot pin down the natural numbers exactly.</p>',
    '<p>Research uses decidable fragments of FOL (the two variable fragment, guarded fragments, description logics), SMT solvers that combine SAT with theories such as arithmetic, and the encoding of commonsense knowledge (Cyc, knowledge graphs) in first order style.</p>')}
''', kw=['Gödel completeness', 'Church Turing', 'Löwenheim Skolem', 'SMT', 'decidable fragments', 'knowledge graphs'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'First order logic talks about objects, relations and functions, and quantifies over objects with ∀ and ∃.',
    'Terms (constants, variables, functions of terms) name objects. Atoms apply predicates to terms. Sentences combine atoms.',
    'A model has a domain and an interpretation. There are infinitely many models, so we cannot list them.',
    'Use ∀ with ⇒ and ∃ with ∧. ∀x ∃y differs from ∃y ∀x. ¬∀x P ≡ ∃x ¬P.',
    'Knowledge engineering: questions, knowledge, vocabulary, general axioms, instance facts, queries, debugging.'],
    'chapter 7.4 shows how to reason in first order logic: unification, chaining and resolution.')}
{nbcard('first-order-logic', 'Check quantified sentences in a small model and derive kinship relations, then write quantifier checks, kinship rules and an interpretation counter yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In first order logic, LeftLeg(John) is', ['a sentence', 'a term that names an object', 'a predicate', 'a quantifier'], 1,
       'It is a leg.', 'A function applied to a term gives a term.')
K.quiz('e', 'Which quantifier means "there exists"?', ['∀', '∃', '¬', '⇒'], 1,
       'Backwards E.', '∃x P(x): some object makes P true.')
K.quiz('e', 'What does FOL add to propositional logic?', ['Numbers only', 'Objects, relations, functions and quantifiers', 'Probabilities', 'Time'], 1,
       'Ontological commitment.', 'Facts plus objects and relations.')
K.quiz('e', 'A model of FOL consists of', ['a truth table', 'a domain of objects and an interpretation of the symbols', 'only constants', 'a list of rules'], 1,
       'Section 8.2.', 'The interpretation fixes what each symbol means.')
K.quiz('m', 'The right way to say "all kings are persons" is', ['∀x King(x) ∧ Person(x)', '∀x King(x) ⇒ Person(x)', '∃x King(x) ⇒ Person(x)', '∃x King(x) ∧ Person(x)'], 1,
       '∀ with ⇒.', 'The ∧ form claims everything is a king.')
K.quiz('m', '¬∀x Likes(x, Parsnips) is equivalent to', ['∀x ¬Likes(x, Parsnips)', '∃x ¬Likes(x, Parsnips)', '¬∃x Likes(x, Parsnips)', '∃x Likes(x, Parsnips)'], 1,
       'De Morgan for quantifiers.', 'Not everybody likes them = somebody does not.')
K.quiz('m', '∀x ∃y Loves(x, y) means', ['someone is loved by everyone', 'everyone loves somebody', 'everyone loves everyone', 'nobody loves anyone'], 1,
       'For each x, some y.', 'The y may be different for each x.')
K.quiz('m', 'Under database semantics, which assumption says that unknown atoms are false?', ['unique names', 'closed world', 'domain closure', 'equality'], 1,
       'Like a database table.', 'If a fact is not stored, it is taken as false.')
K.quiz('h', 'Why does "Richard has at least two brothers" need ¬(x = y)?', ['It does not', 'Without it, x and y could name the same brother', 'Because Brother is symmetric', 'Equality is not allowed in FOL'], 1,
       'Two variables can name one object.', 'Different variables do not have to mean different objects.')
K.quiz('h', 'Why can we not check FOL entailment with a truth table?', ['FOL has no models', 'FOL has infinitely many models (any domain size)', 'Truth tables only allow 3 symbols', 'Quantifiers are not truth functional'], 1,
       'Domains can be any size.', 'There is no finite list of models to check.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: ∃x Crown(x) ⇒ OnHead(x, John). In a model with one crown, not on John\'s head, and one other object, this sentence is', ['false', 'true, because the other object is not a crown', 'undefined', 'true only if John is a king'], 1,
       'An implication with a false premise.', 'x = the other object makes Crown(x) false, so the implication holds.')
K.quiz('x', 'In the style of an MIT 6.034 exam: entailment in FOL is', ['decidable', 'semidecidable: a proof is found if the sentence is entailed, but the search may run for ever if not', 'not semidecidable', 'decidable in polynomial time'], 1,
       'Gödel and Turing.', 'Complete proof procedures exist, but no procedure can always say no.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Domain of 3 objects. How many ways can one constant be interpreted?', '3', 'It names one object.',
       ['A constant names exactly one object.', 'Any of the 3.', eq('3')], check=3)
K.calc('e', 'Domain of 3 objects. How many possible extensions does a unary predicate have?', '8', 'Any subset.',
       ['Each object is in or out.', '2 × 2 × 2.', eq('2³ = 8')], check=8)
K.calc('e', 'Domain of 3 objects. How many ordered pairs can a binary predicate hold for?', '9', 'd².',
       ['3 choices for the first, 3 for the second.', '3 × 3.', eq('9 pairs')], check=9)
K.calc('m', 'Domain of 2 objects, 2 constants, 1 binary predicate. How many interpretations?', '64', 'd<sup>c</sup> × 2<sup>d²</sup>.',
       ['Constants: 2² = 4.', 'Binary predicate: 2⁴ = 16.', eq('4 × 16 = 64')], check=64)
K.calc('m', 'Domain of 3 objects, 1 unary and 1 binary predicate, no constants. How many interpretations?', '4096', '2³ × 2⁹.',
       ['Unary: 2³ = 8.', 'Binary: 2⁹ = 512.', eq('8 × 512 = 4096')], check=4096)
K.calc('m', 'Ground ∀x ∀y Adjacent(x, y) ⇒ Adjacent(y, x) over 4 rooms. How many ground sentences?', '16', 'One per pair (x, y).',
       ['x has 4 values.', 'y has 4 values.', eq('4 × 4 = 16 ground implications')], check=16)
K.calc('h', 'The propositional wumpus KB needs one breeze rule per room. How many for a 10 × 10 cave? (First order logic needs 1.)', '100', 'One per room.',
       ['10 × 10 rooms.', 'One sentence B<sub>x,y</sub> ⇔ (...) each.', eq('100 sentences, against 1 in FOL')], check=100)
K.calc('h', 'How many possible extensions does a ternary (3 place) relation have over 2 objects?', '256', '2<sup>d<sup>3</sup></sup>.',
       ['d³ = 2³ = 8 triples.', 'Each triple in or out.', eq('2⁸ = 256')], check=256)
K.calc('h', 'Kinship data: Parent(Elizabeth, Charles), Parent(Philip, Charles), Parent(Charles, William), Parent(Charles, Harry). How many (g, c) pairs satisfy Grandparent(g, c)?', '4', 'Elizabeth and Philip, times William and Harry.',
       ['Grandparents through Charles: Elizabeth, Philip.', 'Grandchildren through Charles: William, Harry.', eq('2 × 2 = 4 pairs')], check=4)
K.calc('x', 'In the style of a Stanford CS221 problem: domain {a, b}. In how many interpretations of the binary predicate L is ∀x ∃y L(x, y) true?', '9', 'Each x needs at least one y.',
       ['For x = a: the pairs (a, a), (a, b) are any subset except the empty one: 3 choices.', 'For x = b: the same, 3 choices.', eq('3 × 3 = 9 of the 16 relations')], check=9)

# ---------------------------------------------------------------- assignments
K.assign('quant', 'e', 'Check quantified sentences in a model',
         '<p>A unary predicate is given as a Python set of the objects it holds for. Write <code>forall_implies(objects, p, q)</code> for ∀x P(x) ⇒ Q(x), and <code>exists_and(objects, p, q)</code> for ∃x P(x) ∧ Q(x).</p>',
         '''
def forall_implies(objects, p, q):
    # your code here
    pass

def exists_and(objects, p, q):
    # your code here
    pass
''', [("forall_implies(['Richard', 'John', 'TheCrown'], {'John'}, {'Richard', 'John'})", True),
      ("forall_implies(['Richard', 'John'], {'Richard', 'John'}, {'John'})", False),
      ("exists_and(['Richard', 'John', 'TheCrown'], {'TheCrown'}, {'TheCrown'})", True),
      ("exists_and(['Richard', 'John'], {'Richard'}, {'John'})", False),
      ("forall_implies([], {'A'}, set())", True)],
         '''
def forall_implies(objects, p, q):
    for x in objects:
        if x in p and x not in q:
            return False
    return True

def exists_and(objects, p, q):
    for x in objects:
        if x in p and x in q:
            return True
    return False
''', 'For ∀ look for a counterexample: an x in p but not in q. For ∃ look for one example in both sets.', '<p>The last test is an empty domain: there is no counterexample, so the ∀ sentence is true. (Standard FOL requires a non empty domain, but the code still has to give an answer.)</p>')
K.assign('kin', 'm', 'Kinship rules from Parent facts',
         '<p>parent is a list of (parent, child) pairs. Write <code>grandparents(parent, x)</code> and <code>siblings(parent, x)</code>, each returning a sorted list without repeats. Siblings share at least one parent and are not the same person.</p>',
         '''
def grandparents(parent, x):
    # your code here
    pass

def siblings(parent, x):
    # your code here
    pass
''', [("grandparents([('Elizabeth', 'Charles'), ('Philip', 'Charles'), ('Charles', 'William'), ('Charles', 'Harry')], 'William')", ['Elizabeth', 'Philip']),
      ("siblings([('Elizabeth', 'Charles'), ('Philip', 'Charles'), ('Charles', 'William'), ('Charles', 'Harry')], 'Harry')", ['William']),
      ("siblings([('Elizabeth', 'Charles'), ('Elizabeth', 'Anne'), ('Philip', 'Charles'), ('Philip', 'Anne')], 'Anne')", ['Charles']),
      ("grandparents([('A', 'B')], 'B')", [])],
         '''
def grandparents(parent, x):
    out = []
    for g, p in parent:
        if (p, x) in parent and g not in out:
            out.append(g)
    return sorted(out)

def siblings(parent, x):
    out = []
    for p, c in parent:
        if c == x:
            for p2, other in parent:
                if p2 == p and other != x and other not in out:
                    out.append(other)
    return sorted(out)
''', 'Grandparent: some p with Parent(g, p) and Parent(p, x). Sibling: some parent p of x who has another child.', '<p>Test 3 checks that Charles is listed once, even though he shares two parents with Anne.</p>')
K.assign('interp', 'm', 'Count interpretations',
         '<p>Write <code>count_interpretations(d, constants, unary, binary)</code>: the number of interpretations over a domain of d objects with that many constant symbols, unary predicates and binary predicates (no functions).</p>',
         '''
def count_interpretations(d, constants, unary, binary):
    # your code here
    pass
''', [("count_interpretations(2, 2, 0, 1)", 64), ("count_interpretations(3, 0, 1, 1)", 4096),
      ("count_interpretations(1, 3, 2, 2)", 16), ("count_interpretations(3, 1, 0, 0)", 3)],
         '''
def count_interpretations(d, constants, unary, binary):
    total = d ** constants
    total = total * (2 ** d) ** unary
    total = total * (2 ** (d * d)) ** binary
    return total
''', 'Multiply: d choices per constant, 2<sup>d</sup> per unary predicate, 2<sup>d²</sup> per binary predicate.', '<p>With d = 1 every constant names the only object, and each predicate is either true or false of it: 1 × 2² × 2² = 16.</p>')

K.must('Syntax', 'Constants, predicates, functions, variables. Terms name objects, atoms are true or false.')
K.must('Semantics', 'Model = domain + interpretation. Infinitely many models, so no truth tables.')
K.must('Quantifier traps', '∀ with ⇒, ∃ with ∧. ∀x ∃y ≠ ∃y ∀x. ¬∀x P ≡ ∃x ¬P.')
K.must('Equality', 'x = y means same object. Needed for "at least two". Database semantics: unique names, closed world, domain closure.')
K.must('Engineering', 'Questions, knowledge, vocabulary, general axioms, instance facts, queries, debug.')

T = K.topic(
    slug='first-order-logic', topic='first-order-logic', step=(7, 'Logic and knowledge', 'cai-logic', 'Agents that know facts and reason with them: propositional logic, inference rules, resolution, chaining, first order logic and unification.', 'College'),
    title='First order logic: syntax and semantics', short='First order logic', badge='7.3', minutes=50,
    lead='Say things about all objects at once. Learn the parts of first order logic, what a model and an interpretation are, how ∀ and ∃ work and where they trick people, and how to write the kinship and wumpus worlds in it.',
    desc='Why propositional logic is not enough, ontological commitments, constants, predicates, functions, terms and atoms, models with a domain and an interpretation, universal and existential quantifiers and their traps, nested quantifiers, De Morgan for quantifiers, equality, database semantics, kinship axioms, the wumpus world in FOL and the knowledge engineering process.',
    summary='Objects, relations, functions, quantifiers, models and how to write knowledge in FOL.',
    keywords=['first order logic', 'predicate logic', 'quantifier', 'forall', 'exists', 'model', 'interpretation', 'kinship', 'knowledge engineering'],
    recap='<p>FOL talks about objects with predicates, functions and quantifiers. ∀ goes with ⇒, ∃ with ∧.</p>',
    nb={'model': 'Quantified sentences in a small model', 'kin': 'Kinship relations from Parent facts'})
