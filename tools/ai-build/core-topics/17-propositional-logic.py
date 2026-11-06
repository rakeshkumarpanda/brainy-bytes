# Chapter 7.1: knowledge based agents and propositional logic. The uploaded slides and class transcripts end with
# adversarial search, so this chapter follows Russell and Norvig, AIMA 4th ed., sections 7.1 to 7.4 (knowledge based
# agents, the wumpus world, logic, propositional logic, the wumpus knowledge base R1 to R5 and model checking with
# TT-ENTAILS). Every number about the wumpus knowledge base was checked by running the code of this chapter.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('connectives', r'''
# The truth table of the five connectives. True and False are written T and F.
def show(v):
    return "T" if v else "F"

print("P Q | not P | P and Q | P or Q | P => Q | P <=> Q")
for p in [True, False]:
    for q in [True, False]:
        implies = (not p) or q          # false only when P is true and Q is false
        iff = (p == q)                  # true when both have the same value
        print(show(p), show(q), "|  ", show(not p), "  |   ", show(p and q), "   |  ", show(p or q), "   |  ",
              show(implies), "   |   ", show(iff))
''')

K.code('entail', r'''
# Model checking: KB = {P or Q, P => R, Q => R}. Does the KB entail R? Does it entail P?
from itertools import product

def kb_true(p, q, r):
    return (p or q) and ((not p) or r) and ((not q) or r)

models = []
for p, q, r in product([True, False], repeat=3):     # all 8 models
    if kb_true(p, q, r):
        models.append((p, q, r))
print("models of the KB (P, Q, R):", models)

entails_r = all(r for p, q, r in models)             # R true in every model of the KB?
entails_p = all(p for p, q, r in models)
print("KB entails R:", entails_r)
print("KB entails P:", entails_p)
''')

K.lesson('kba', 'Knowledge based agents', f'''
{src('Russell and Norvig, AIMA 4th ed., section 7.1. The uploaded slides stop at adversarial search, so this step follows the textbook.')}
{wwh('A knowledge based agent keeps a <b>knowledge base</b> (KB): a set of sentences in a formal language that say what the agent believes about the world. It adds new sentences with TELL and asks questions with ASK. The answer to ASK must follow from what was told.',
     'Search agents know only a fixed list of states and actions. They cannot use general facts such as "a breeze means a pit next door" in new situations. A KB lets an agent combine general rules with what it sees and work out facts it never saw directly.',
     'Each time step: TELL the KB what the agent perceives, ASK the KB which action is best, TELL the KB that this action was taken, then act. The reasoning happens inside ASK, by an inference procedure.')}
{algo('KB-AGENT', [
    'function KB-AGENT(percept) returns an action',
    '    persistent: KB, a knowledge base. t, a counter for time, at first 0',
    '    TELL(KB, MAKE-PERCEPT-SENTENCE(percept, t))',
    '    action = ASK(KB, MAKE-ACTION-QUERY(t))',
    '    TELL(KB, MAKE-ACTION-SENTENCE(action, t))',
    '    t = t + 1',
    '    return action'])}
<p>This is the <b>declarative</b> way to build an agent: tell it what it needs to know and let it reason. The <b>procedural</b> way writes the behaviour straight into code. Real systems mix both.</p>
''', kw=['knowledge base', 'KB', 'TELL', 'ASK', 'knowledge based agent', 'declarative', 'procedural'])

K.lesson('wumpus', 'The wumpus world', f'''
{src('AIMA 4th ed., section 7.2.')}
<p>A cave of 4 × 4 rooms. The agent starts in [1,1] facing right. One room holds the wumpus, a beast that eats anyone who enters its room. Some rooms hold bottomless pits. One room holds gold. The agent has one arrow.</p>
{table(['PEAS part', 'Wumpus world'], [
    ['Performance', '+1000 for climbing out with the gold, −1000 for falling into a pit or being eaten, −1 for each action, −10 for using the arrow'],
    ['Environment', '4 × 4 grid of rooms, agent starts in [1,1]. The wumpus and the gold are placed at random in other rooms, and each other room has a pit with probability 0.2'],
    ['Actuators', 'Forward, TurnLeft, TurnRight, Grab, Shoot, Climb'],
    ['Sensors', 'Stench (wumpus next door), Breeze (pit next door), Glitter (gold here), Bump (walked into a wall), Scream (the wumpus died)']])}
{steps('Reasoning in the first moves', [
    'In [1,1] the percept is [None, None, None, None, None]: no stench and no breeze. So [1,2] and [2,1] are safe.',
    'The agent moves to [2,1] and feels a Breeze. So there is a pit in [2,2] or [3,1], or both.',
    'It goes back and moves to [1,2]. It smells a Stench but feels no Breeze.',
    'No breeze in [1,2] means no pit in [2,2]. So the pit is in [3,1]. The stench in [1,2], with no stench in [2,1], puts the wumpus in [1,3].',
    eq('the agent has worked out facts it never saw directly: this is logical inference')])}
{note('Room names are [column, row]. [2,1] is one step right of the start, [1,2] is one step up.', 'tip')}
''', kw=['wumpus world', 'PEAS', 'breeze', 'stench', 'pit', 'percept'])

K.lesson('logic', 'Logic: syntax, semantics, models and entailment', f'''
{src('AIMA 4th ed., section 7.3.')}
{table(['Idea', 'Meaning', 'Example'], [
    ['Syntax', 'Which strings are well formed sentences', 'x + y = 4 is a sentence, x4y+ = is not'],
    ['Semantics', 'When a sentence is true. A sentence is true or false in each possible world', 'x + y = 4 is true in the world where x = 2, y = 2'],
    ['Model', 'A possible world, fixed exactly. In propositional logic: a true or false value for every symbol', 'P = T, Q = F, R = T'],
    ['M(α)', 'The set of all models in which α is true', 'M(P ∨ Q) has 3 of the 4 models of P, Q'],
    ['Entailment KB ⊨ α', 'α is true in every model where the KB is true', '{x = 0} ⊨ x y = 0']])}
{fxs(fx('Entailment', 'KB ⊨ α if and only if M(KB) ⊆ M(α)', 'The more a KB says, the fewer models it has. If all of them make α true, α follows.', key=True))}
{table(['Property of an inference procedure i', 'Meaning'], [
    ['KB ⊢<sub>i</sub> α', 'Procedure i derives α from the KB'],
    ['Sound (truth preserving)', 'It derives only entailed sentences: if KB ⊢<sub>i</sub> α then KB ⊨ α'],
    ['Complete', 'It can derive every entailed sentence: if KB ⊨ α then KB ⊢<sub>i</sub> α'],
    ['Grounding', 'The link between the sentences and the real world. It comes from the sensors and from learning, not from logic']])}
''', kw=['syntax', 'semantics', 'model', 'entailment', 'sound', 'complete', 'grounding'])

K.lesson('pl', 'Propositional logic', f'''
{src('AIMA 4th ed., section 7.4.')}
<p>The simplest logic. <b>Atomic sentences</b> are single symbols such as P, Q or P<sub>1,2</sub> ("there is a pit in [1,2]"). True and False are also sentences. <b>Complex sentences</b> are built with five connectives.</p>
{table(['Connective', 'Name', 'Read as', 'True when'], [
    ['¬P', 'negation', 'not P', 'P is false'],
    ['P ∧ Q', 'conjunction', 'P and Q', 'both are true'],
    ['P ∨ Q', 'disjunction', 'P or Q', 'at least one is true'],
    ['P ⇒ Q', 'implication', 'if P then Q', 'P is false, or Q is true. False only for P = T, Q = F'],
    ['P ⇔ Q', 'biconditional', 'P if and only if Q', 'both have the same value']])}
<p>Precedence, from strongest to weakest: ¬, ∧, ∨, ⇒, ⇔. So ¬A ∧ B ∨ C ⇒ D means ((¬A ∧ B) ∨ C) ⇒ D.</p>
{code('connectives')}
{note('P ⇒ Q is true whenever P is false. "If 5 is even, then Sam is smart" is true in propositional logic, whatever Sam is like. Implication does not mean that P causes Q.', 'warn')}
''', kw=['propositional logic', 'atomic sentence', 'connective', 'negation', 'conjunction', 'disjunction', 'implication', 'biconditional', 'precedence'])

K.lesson('wkb', 'A knowledge base for the wumpus world, and model checking', f'''
{src('AIMA 4th ed., sections 7.4.3 and 7.4.4. We ran the check ourselves and got the same numbers as the textbook.')}
<p>Symbols: P<sub>x,y</sub> is true if there is a pit in [x,y], B<sub>x,y</sub> if the agent feels a breeze in [x,y]. After the first two moves the KB holds:</p>
{table(['Name', 'Sentence', 'Meaning'], [
    ['R1', '¬P<sub>1,1</sub>', 'no pit in the start room'],
    ['R2', 'B<sub>1,1</sub> ⇔ (P<sub>1,2</sub> ∨ P<sub>2,1</sub>)', 'a room is breezy if and only if a neighbour has a pit'],
    ['R3', 'B<sub>2,1</sub> ⇔ (P<sub>1,1</sub> ∨ P<sub>2,2</sub> ∨ P<sub>3,1</sub>)', 'the same rule for [2,1]'],
    ['R4', '¬B<sub>1,1</sub>', 'percept: no breeze in [1,1]'],
    ['R5', 'B<sub>2,1</sub>', 'percept: breeze in [2,1]']])}
{steps('Model checking', [
    'There are 7 symbols: B<sub>1,1</sub>, B<sub>2,1</sub>, P<sub>1,1</sub>, P<sub>1,2</sub>, P<sub>2,1</sub>, P<sub>2,2</sub>, P<sub>3,1</sub>. So 2⁷ = 128 models.',
    'Only 3 of them make R1 to R5 all true: pits in [2,2] and [3,1], a pit in [2,2] only, or a pit in [3,1] only.',
    'P<sub>1,2</sub> is false in all 3, so KB ⊨ ¬P<sub>1,2</sub>: [1,2] is safe.',
    'P<sub>2,2</sub> is true in 2 and false in 1, so the KB entails neither P<sub>2,2</sub> nor ¬P<sub>2,2</sub>. The agent cannot tell yet.',
    eq('KB ⊨ ¬P<sub>1,2</sub>, KB ⊨ P<sub>2,2</sub> ∨ P<sub>3,1</sub>, but not KB ⊨ P<sub>2,2</sub>')])}
{viz('truthtable', kb='P ∨ Q\nP ⇒ R\nQ ⇒ R', q='R')}
{code('entail')}
{algo('TT-ENTAILS (truth table enumeration)', [
    'function TT-ENTAILS(KB, α): symbols = the symbols in KB and α',
    '    return TT-CHECK-ALL(KB, α, symbols, { })',
    '',
    'function TT-CHECK-ALL(KB, α, symbols, model):',
    '    if symbols is empty:',
    '        if PL-TRUE(KB, model): return PL-TRUE(α, model)',
    '        else: return true          (a model where KB is false does not matter)',
    '    P = FIRST(symbols), rest = REST(symbols)',
    '    return TT-CHECK-ALL(KB, α, rest, model ∪ {P = true}) and',
    '           TT-CHECK-ALL(KB, α, rest, model ∪ {P = false})'])}
<p>TT-ENTAILS is sound and complete, but it takes O(2<sup>n</sup>) time for n symbols, and O(n) space because it explores the models depth first.</p>
''', kw=['wumpus knowledge base', 'model checking', 'TT-ENTAILS', 'truth table', '128 models'])

K.lesson('valid', 'Validity, satisfiability and equivalence', f'''
{src('AIMA 4th ed., section 7.5.1.')}
{table(['Term', 'Meaning', 'Example'], [
    ['Valid (a tautology)', 'True in every model', 'P ∨ ¬P'],
    ['Satisfiable', 'True in at least one model', 'P ∧ Q'],
    ['Unsatisfiable', 'True in no model', 'P ∧ ¬P'],
    ['Equivalent, α ≡ β', 'True in exactly the same models. Same as α ⊨ β and β ⊨ α', 'P ⇒ Q ≡ ¬P ∨ Q']])}
{fxs(
    fx('Deduction theorem', 'KB ⊨ α if and only if (KB ⇒ α) is valid', 'Entailment can be checked as validity.', key=True),
    fx('Proof by contradiction (refutation)', 'KB ⊨ α if and only if (KB ∧ ¬α) is unsatisfiable', 'Assume α is false and show this is impossible. Resolution (chapter 7.2) works this way.', key=True))}
{table(['Equivalence', 'Name'], [
    ['α ∧ β ≡ β ∧ α, α ∨ β ≡ β ∨ α', 'commutativity'],
    ['(α ∧ β) ∧ γ ≡ α ∧ (β ∧ γ), and the same for ∨', 'associativity'],
    ['¬(¬α) ≡ α', 'double negation'],
    ['α ⇒ β ≡ ¬β ⇒ ¬α', 'contraposition'],
    ['α ⇒ β ≡ ¬α ∨ β', 'implication elimination'],
    ['α ⇔ β ≡ (α ⇒ β) ∧ (β ⇒ α)', 'biconditional elimination'],
    ['¬(α ∧ β) ≡ ¬α ∨ ¬β, ¬(α ∨ β) ≡ ¬α ∧ ¬β', 'De Morgan'],
    ['α ∧ (β ∨ γ) ≡ (α ∧ β) ∨ (α ∧ γ), α ∨ (β ∧ γ) ≡ (α ∨ β) ∧ (α ∨ γ)', 'distributivity']])}
<p>Deciding if a sentence is satisfiable (the SAT problem) was the first problem proved NP-complete (Cook, 1971). So we do not expect any method to beat 2<sup>n</sup> on every input, yet modern SAT solvers handle millions of symbols in practice.</p>
''', kw=['valid', 'tautology', 'satisfiable', 'unsatisfiable', 'equivalence', 'deduction theorem', 'refutation', 'De Morgan', 'SAT', 'NP-complete'])

K.lesson('maths', 'The maths: counting models', f'''
{fxs(
    fx('Number of models', '2<sup>n</sup> for n symbols', '3 symbols: 8 models. 7 symbols: 128. 30 symbols: over 10⁹.', key=True),
    fx('Number of different sentences up to equivalence', '2<sup>2<sup>n</sup></sup>', 'Each sentence is fixed by the set of models where it is true, and there are 2<sup>2<sup>n</sup></sup> such sets. For n = 2 there are 16 different truth tables.'),
    fx('Entailment as sets', 'KB ⊨ α ⟺ M(KB) ⊆ M(α) ⟺ M(KB) ∩ M(¬α) = ∅', 'The last form is proof by contradiction.'))}
{steps('Worked example: how many models make P ∨ Q true, with symbols P, Q, R?', [
    '2³ = 8 models in total.',
    'P ∨ Q is false only when P = F and Q = F. R can then be T or F: 2 models.',
    '8 − 2 = 6.',
    eq('|M(P ∨ Q)| = 6 out of 8')])}
{steps('Worked example: is (P ⇒ Q) ⇒ (¬Q ⇒ ¬P) valid?', [
    '¬Q ⇒ ¬P is equivalent to P ⇒ Q (contraposition).',
    'So the sentence is (P ⇒ Q) ⇒ (P ⇒ Q), which has the form α ⇒ α.',
    'α ⇒ α ≡ ¬α ∨ α, true in every model.',
    eq('valid')])}
''', kw=['number of models', 'two to the n', 'counting truth tables', 'worked example'])

K.lesson('compare', 'Logic against other ways to store knowledge', f'''
{versus('Ways to represent what an agent knows', ['', 'Atomic states (search)', 'Propositional logic', 'First order logic (7.3)', 'Probability (step 9)'], [
    ['A state is', 'one name, no inside parts', 'true or false values for fixed facts', 'objects, relations and functions', 'a distribution over possible worlds'],
    ['Can say "pits cause breezes in every room" in one sentence', 'No', 'No, one sentence per room', 'Yes', 'Yes, with a rule per variable'],
    ['Handles uncertainty', 'No', 'Only by listing cases with ∨', 'Only by listing cases', 'Yes, with numbers'],
    ['Inference', 'Search', 'Model checking, resolution, chaining', 'Unification, chaining, resolution', 'Bayes rule, Bayesian networks'],
    ['Decidable', 'Yes', 'Yes (but NP-complete)', 'Only semidecidable', 'Yes for finite models']],
    'propositional logic is the simplest language with a clear meaning and sound, complete inference. Its weakness is that it cannot talk about many objects at once, which first order logic fixes.')}
{scene('Where propositional reasoning is used', '<p>Hardware verification: chip makers check that a circuit design meets its specification by turning the question into a SAT problem. Software package managers (such as the ones for Linux) decide which versions of packages to install with SAT solvers. Planning systems such as SATPlan turn "is there a plan of length T" into one big propositional sentence.</p>')}
''', kw=['comparison', 'representation', 'SAT solvers', 'hardware verification', 'package managers'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A knowledge base is a list of facts and rules the agent believes. If something must be true in every world that fits these facts, the agent can be sure of it, even without seeing it.</p>',
    '<p>Propositional logic has symbols and five connectives. KB ⊨ α means M(KB) ⊆ M(α). Truth table model checking is sound and complete but costs 2<sup>n</sup>. Validity, satisfiability and the deduction theorem connect entailment to SAT.</p>',
    '<p>SAT is NP-complete (Cook 1971, Levin 1973). Random 3-SAT shows a sharp phase change near 4.26 clauses per symbol, where problems are hardest. Propositional logic is compact: the same set of models can need exponentially long sentences in one normal form and short ones in another.</p>',
    '<p>Research looks at proof complexity (how long the shortest proof of an unsatisfiable formula must be in a given proof system), knowledge compilation into forms such as d-DNNF that answer many queries fast, and neurosymbolic systems that combine logic with learned models.</p>')}
''', kw=['phase transition', 'proof complexity', 'knowledge compilation', 'neurosymbolic'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A knowledge based agent TELLs its KB what it perceives and ASKs it what to do. The answers come from inference.',
    'In the wumpus world, the agent works out where pits and the wumpus are from breezes and stenches.',
    'A model fixes every fact. KB ⊨ α means α is true in every model of the KB: M(KB) ⊆ M(α). Sound procedures derive only entailed sentences, complete ones derive all of them.',
    'Propositional logic: symbols, ¬ ∧ ∨ ⇒ ⇔. P ⇒ Q is false only when P is true and Q is false.',
    'Model checking with a truth table is sound and complete but costs 2<sup>n</sup>. The wumpus KB R1 to R5 has 3 models out of 128 and entails ¬P<sub>1,2</sub>.'],
    'chapter 7.2 proves things without listing every model: inference rules, resolution and chaining.')}
{nbcard('propositional-logic', 'Print the truth table of the connectives and check entailment by listing models, then write a sentence evaluator, a model counter and TT-ENTAILS for the wumpus knowledge base.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'P ⇒ Q is false when', ['P is false and Q is true', 'P is true and Q is false', 'both are false', 'both are true'], 1,
       'Only one row.', 'An implication fails only when the premise holds and the conclusion does not.')
K.quiz('e', 'What does KB ⊨ α mean?', ['α is in the KB', 'α is true in every model where the KB is true', 'α is false', 'The KB is true in every model'], 1,
       'Models.', 'M(KB) ⊆ M(α).')
K.quiz('e', 'How many models do 4 symbols have?', ['4', '8', '16', '32'], 2,
       '2<sup>n</sup>.', '2⁴ = 16.')
K.quiz('e', 'A breeze in a wumpus world room means', ['The wumpus is next door', 'A pit is in a next door room', 'Gold is here', 'A wall was hit'], 1,
       'Pits make wind.', 'Breeze: a pit in an adjacent room.')
K.quiz('m', 'An inference procedure that derives only entailed sentences is', ['complete', 'sound', 'valid', 'satisfiable'], 1,
       'Truth preserving.', 'Sound: if KB ⊢ α then KB ⊨ α.')
K.quiz('m', 'Which sentence is valid?', ['P ∧ ¬P', 'P ∨ ¬P', 'P ⇒ ¬P', 'P'], 1,
       'True in every model.', 'Either P or ¬P is always true.')
K.quiz('m', 'In the wumpus KB R1 to R5, which sentence is entailed?', ['P<sub>2,2</sub>', '¬P<sub>1,2</sub>', 'P<sub>3,1</sub>', '¬P<sub>2,2</sub>'], 1,
       'Only one is true in all 3 models.', 'No breeze in [1,1] rules out a pit in [1,2].')
K.quiz('m', 'α ⇒ β is equivalent to', ['β ⇒ α', '¬α ⇒ ¬β', '¬β ⇒ ¬α', 'α ∧ β'], 2,
       'Contraposition.', '"If raining then wet" is the same as "if not wet then not raining".')
K.quiz('h', 'KB ⊨ α holds exactly when', ['KB ∧ α is valid', 'KB ∧ ¬α is unsatisfiable', 'KB ∨ α is satisfiable', '¬KB is valid'], 1,
       'Proof by contradiction.', 'No model makes KB true and α false.')
K.quiz('h', 'From P ⇒ Q and Q, can we conclude P?', ['Yes, by modus ponens', 'No: the model P = F, Q = T makes both true and P false', 'Yes, always', 'Only if P is valid'], 1,
       'Affirming the consequent.', 'Find a model of the KB where P is false.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: a KB is unsatisfiable. Which is true?', ['It entails nothing', 'It entails every sentence', 'It entails only valid sentences', 'It has exactly one model'], 1,
       'M(KB) is empty.', 'The empty set is a subset of every M(α).')
K.quiz('x', 'In the style of an MIT 6.034 exam: how many different Boolean functions (truth tables) of 3 symbols exist?', ['8', '64', '256', '512'], 2,
       '2<sup>2<sup>n</sup></sup>.', '2⁸ = 256.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many models do 7 symbols have?', '128', '2⁷.',
       ['2⁵ = 32.', '32 × 4.', eq('128')], check=128)
K.calc('e', 'With symbols P and Q, in how many models is P ∧ Q true?', '1', 'Both must be true.',
       ['4 models in total.', 'Only P = T, Q = T.', eq('1')], check=1)
K.calc('e', 'With symbols P and Q, in how many models is P ⇒ Q true?', '3', 'False only for P = T, Q = F.',
       ['4 models.', 'One of them makes it false.', eq('4 − 1 = 3')], check=3)
K.calc('m', 'With symbols P, Q, R, in how many models is P ∨ Q true?', '6', 'Count the false case and subtract.',
       ['8 models.', 'False only when P = F and Q = F: R free, 2 models.', eq('8 − 2 = 6')], check=6)
K.calc('m', 'The KB {P ∨ Q, P ⇒ R, Q ⇒ R} over P, Q, R. How many models does it have?', '3', 'R must be true, and P or Q.',
       ['If R = F: P ⇒ R needs P = F, Q ⇒ R needs Q = F, but then P ∨ Q is false. No model.', 'If R = T: the implications hold. P ∨ Q is true in 3 of the 4 choices of P, Q.', eq('3 models, all with R = T')], check=3)
K.calc('m', 'The wumpus KB R1 to R5: how many of its 128 models make the KB true?', '3', 'B values are fixed, P11 is false, P12 and P21 are false.',
       ['R4 and R5 fix B<sub>1,1</sub> = F and B<sub>2,1</sub> = T. R1 gives P<sub>1,1</sub> = F.', 'R2 with B<sub>1,1</sub> = F forces P<sub>1,2</sub> = F and P<sub>2,1</sub> = F.', 'R3 with B<sub>2,1</sub> = T needs P<sub>2,2</sub> ∨ P<sub>3,1</sub>: 3 of the 4 choices.', eq('3 models')], check=3)
K.calc('h', 'How many different Boolean functions of 2 symbols exist?', '16', '2<sup>2<sup>n</sup></sup>.',
       ['2 symbols give 2² = 4 rows.', 'Each row can be T or F.', eq('2⁴ = 16')], check=16)
K.calc('h', 'TT-ENTAILS checks 1 million models a second. About how many seconds for 30 symbols? Give the whole number.', '1074', '2³⁰ ⁄ 10⁶.',
       ['2³⁰ = 1,073,741,824.', 'Divide by 1,000,000.', eq('≈ 1074 seconds, about 18 minutes')], check=1074, tol=1)
K.calc('h', 'Each of the 16 wumpus rooms can have a pit or not, and a breeze or not. How many models for these 32 symbols? Give the power of 2.', '32', '2<sup>n</sup> with n = 32.',
       ['16 pit symbols plus 16 breeze symbols.', 'n = 32.', eq('2³² ≈ 4.3 × 10⁹ models')], check=32)
K.calc('x', 'In the style of a Stanford CS221 problem: KB = {A ∨ B, ¬A ∨ C}. Over A, B, C, how many models does KB ∧ ¬(B ∨ C) have?', '0', 'If B and C are both false, look at the KB.',
       ['¬(B ∨ C) means B = F and C = F.', 'A ∨ B needs A = T. ¬A ∨ C then needs C = T, but C = F.', eq('0 models, so KB ⊨ B ∨ C (this is resolution on A)')], check=0)

# ---------------------------------------------------------------- assignments
K.assign('pltrue', 'e', 'Evaluate a sentence in a model',
         '<p>Sentences are written as Python values. A symbol is a string such as <code>"P"</code>. A complex sentence is a tuple: <code>("not", s)</code>, <code>("and", a, b)</code>, <code>("or", a, b)</code>, <code>("implies", a, b)</code> or <code>("iff", a, b)</code>. A model is a dictionary from symbols to True or False. Write <code>value(s, model)</code>.</p>',
         '''
def value(s, model):
    # your code here
    pass
''', [("value('P', {'P': True})", True),
      ("value(('implies', 'P', 'Q'), {'P': True, 'Q': False})", False),
      ("value(('implies', 'P', 'Q'), {'P': False, 'Q': False})", True),
      ("value(('iff', 'B11', ('or', 'P12', 'P21')), {'B11': False, 'P12': False, 'P21': False})", True),
      ("value(('not', ('and', 'P', 'Q')), {'P': True, 'Q': True})", False)],
         '''
def value(s, model):
    if type(s) == str:
        return model[s]
    op = s[0]
    if op == "not":
        return not value(s[1], model)
    a = value(s[1], model)
    b = value(s[2], model)
    if op == "and":
        return a and b
    if op == "or":
        return a or b
    if op == "implies":
        return (not a) or b
    if op == "iff":
        return a == b
''', 'A string is looked up in the model. For a tuple, look at the first item and compute the parts with value itself.', '<p>The fourth test is R2 of the wumpus KB in a model with no breeze and no pits: both sides are false, so ⇔ is true.</p>')

WUMPUS = '''
SYMBOLS = ["B11", "B21", "P11", "P12", "P21", "P22", "P31"]
KB = [("not", "P11"),
      ("iff", "B11", ("or", "P12", "P21")),
      ("iff", "B21", ("or", "P11", ("or", "P22", "P31"))),
      ("not", "B11"),
      "B21"]

def value(s, model):
    if type(s) == str:
        return model[s]
    op = s[0]
    if op == "not":
        return not value(s[1], model)
    a = value(s[1], model)
    b = value(s[2], model)
    if op == "and":
        return a and b
    if op == "or":
        return a or b
    if op == "implies":
        return (not a) or b
    return a == b

def all_models(symbols):
    # every model as a dictionary, made by doubling the list once per symbol
    models = [{}]
    for name in symbols:
        bigger = []
        for m in models:
            t = dict(m)
            t[name] = True
            f = dict(m)
            f[name] = False
            bigger.append(t)
            bigger.append(f)
        models = bigger
    return models
'''
K.assign('count', 'm', 'Count the models of the wumpus KB',
         '<p>The starter gives the wumpus knowledge base R1 to R5, <code>value</code> and <code>all_models(symbols)</code>. Write <code>count_models(kb, symbols)</code>: the number of models in which every sentence of kb is true.</p>',
         WUMPUS + '''
def count_models(kb, symbols):
    # your code here
    pass
''', [("count_models(KB, SYMBOLS)", 3),
      ("count_models([('or', 'P', 'Q')], ['P', 'Q', 'R'])", 6),
      ("count_models([('or', 'P', 'Q'), ('implies', 'P', 'R'), ('implies', 'Q', 'R')], ['P', 'Q', 'R'])", 3),
      ("count_models([('and', 'P', ('not', 'P'))], ['P'])", 0)],
         WUMPUS + '''
def count_models(kb, symbols):
    count = 0
    for m in all_models(symbols):
        ok = True
        for s in kb:
            if not value(s, m):
                ok = False
        if ok:
            count = count + 1
    return count
''', 'Loop over all_models(symbols). A model counts when value(s, m) is True for every s in kb.', '<p>The wumpus KB has 3 models out of 128, as in the textbook.</p>')
K.assign('ttent', 'm', 'TT-ENTAILS for the wumpus world',
         '<p>Write <code>tt_entails(kb, alpha, symbols)</code>: True if alpha is true in every model where all sentences of kb are true. Use <code>all_models</code> and <code>value</code> from the starter.</p>',
         WUMPUS + '''
def tt_entails(kb, alpha, symbols):
    # your code here
    pass
''', [("tt_entails(KB, ('not', 'P12'), SYMBOLS)", True),
      ("tt_entails(KB, 'P22', SYMBOLS)", False),
      ("tt_entails(KB, ('not', 'P22'), SYMBOLS)", False),
      ("tt_entails(KB, ('or', 'P22', 'P31'), SYMBOLS)", True),
      ("tt_entails([('implies', 'P', 'Q'), 'Q'], 'P', ['P', 'Q'])", False)],
         WUMPUS + '''
def tt_entails(kb, alpha, symbols):
    for m in all_models(symbols):
        kb_ok = True
        for s in kb:
            if not value(s, m):
                kb_ok = False
        if kb_ok and not value(alpha, m):
            return False
    return True
''', 'Look for a counterexample: a model where the KB is true and alpha is false. If there is none, return True.', '<p>The KB entails ¬P<sub>1,2</sub> and P<sub>2,2</sub> ∨ P<sub>3,1</sub>, but neither P<sub>2,2</sub> nor ¬P<sub>2,2</sub>. The last test is affirming the consequent.</p>')

K.must('KB agent', 'TELL percepts, ASK for an action, TELL the action. Inference happens inside ASK.')
K.must('Entailment', 'KB ⊨ α iff M(KB) ⊆ M(α). Sound: derives only entailed. Complete: derives all entailed.')
K.must('Connectives', '¬ ∧ ∨ ⇒ ⇔, in that order of precedence. P ⇒ Q false only for P = T, Q = F.')
K.must('Wumpus KB', 'R1 ¬P11, R2 B11 ⇔ (P12 ∨ P21), R3 B21 ⇔ (P11 ∨ P22 ∨ P31), R4 ¬B11, R5 B21. 3 of 128 models. Entails ¬P12.')
K.must('Validity', 'KB ⊨ α iff KB ⇒ α is valid iff KB ∧ ¬α is unsatisfiable. SAT is NP-complete.')

T = K.topic(
    slug='propositional-logic', topic='propositional-logic', step=(7, 'Logic and knowledge', 'cai-logic', 'Agents that know facts and reason with them: propositional logic, inference rules, resolution, chaining, first order logic and unification.', 'College'),
    title='Knowledge, logic and propositional logic', short='Propositional logic', badge='7.1', minutes=50,
    lead='Build an agent that knows facts and works out new ones. Meet the wumpus world, learn what models and entailment mean, write sentences in propositional logic, and check entailment with a truth table.',
    desc='Knowledge based agents with TELL and ASK, the wumpus world, syntax, semantics, models and entailment, soundness and completeness, propositional logic and its connectives, the wumpus knowledge base R1 to R5, model checking with TT-ENTAILS, validity, satisfiability and the standard equivalences.',
    summary='Knowledge based agents, entailment, propositional logic and model checking.',
    keywords=['propositional logic', 'knowledge base', 'entailment', 'model', 'wumpus world', 'truth table', 'TT-ENTAILS', 'satisfiability', 'validity'],
    recap='<p>KB ⊨ α when α holds in every model of the KB. A truth table checks this for small problems.</p>',
    nb={'connectives': 'The truth table of the connectives', 'entail': 'Entailment by listing models'})
