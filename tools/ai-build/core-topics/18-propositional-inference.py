# Chapter 7.2: reasoning patterns in propositional logic. Follows Russell and Norvig, AIMA 4th ed., sections 7.5 and
# 7.6 (inference rules and proofs, the wumpus proof of no pit in [1,2] or [2,1], resolution and conjunctive normal form,
# PL-RESOLUTION, Horn and definite clauses, forward and backward chaining, DPLL and WALKSAT). The resolution, chaining
# and DPLL examples were run with the code of this chapter.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('resolve', r'''
# Resolution refutation for the wumpus question: does the KB entail "no pit in [1,2]"?
# A clause is a set of literals. "-P12" means not P12.
kb = [{"-B11", "P12", "P21"}, {"-P12", "B11"}, {"-P21", "B11"}, {"-B11"}]
goal_negated = [{"P12"}]                 # the opposite of what we want to prove

def opposite(lit):
    return lit[1:] if lit.startswith("-") else "-" + lit

def resolve(a, b):
    out = []
    for lit in sorted(a):                 # sorted, so the order is the same every run
        if opposite(lit) in b:
            out.append((a - {lit}) | (b - {opposite(lit)}))
    return out

clauses = kb + goal_negated
new_ones = goal_negated
while new_ones:
    found = []
    for a in new_ones:
        for b in clauses:
            for r in resolve(a, b):
                if r not in clauses and r not in found:
                    print("resolve", sorted(a), "with", sorted(b), "->", sorted(r) if r else "{} empty")
                    found.append(r)
    if set() in found:
        print("empty clause: the KB entails not P12")
        break
    clauses = clauses + found
    new_ones = found
''')

K.code('fc', r'''
# Forward chaining on the textbook Horn knowledge base. Each rule is (premises, conclusion).
rules = [(["P"], "Q"), (["L", "M"], "P"), (["B", "L"], "M"), (["A", "P"], "L"), (["A", "B"], "L")]
facts = ["A", "B"]
query = "Q"

count = [len(p) for p, c in rules]       # premises still unknown for each rule
known = set()
agenda = list(facts)
while agenda:
    s = agenda.pop(0)
    if s == query:
        print("proved", query)
        break
    if s in known:
        continue
    known.add(s)
    for i in range(len(rules)):
        if s in rules[i][0]:
            count[i] = count[i] - 1
            if count[i] == 0:
                print("rule", i + 1, "fires:", rules[i][1])
                agenda.append(rules[i][1])
''')

K.code('dpll', r'''
# DPLL on a small CNF formula. Literals are numbers: 1 means x1, -1 means not x1.
clauses = [[1, 2], [-1, 3], [-2, 3], [-3, 4], [-4, -1]]

def simplify(cls, lit):
    out = []
    for c in cls:
        if lit in c:
            continue                       # the clause is already true
        out.append([x for x in c if x != -lit])   # drop the false literal
    return out

def dpll(cls, model):
    if not cls:
        return model                       # every clause is true
    if [] in cls:
        return None                        # some clause is false
    for c in cls:
        if len(c) == 1:                    # unit clause: no choice
            return dpll(simplify(cls, c[0]), model + [c[0]])
    lit = cls[0][0]                        # otherwise guess, and undo if it fails
    result = dpll(simplify(cls, lit), model + [lit])
    if result is None:
        result = dpll(simplify(cls, -lit), model + [-lit])
    return result

print("model:", dpll(clauses, []))
''')

K.lesson('rules', 'Inference rules and proofs', f'''
{src('Russell and Norvig, AIMA 4th ed., section 7.5.')}
{wwh('An inference rule takes sentences of a certain shape and lets you write a new sentence. A proof is a chain of rule uses that ends with the sentence you want.',
     'Model checking looks at all 2<sup>n</sup> models. A proof can ignore every symbol that does not matter, so it can be far shorter when the KB is large.',
     'Start from the KB. Apply a sound rule to sentences you already have and add the result. Stop when the goal appears. This is a search problem: states are sets of sentences, actions are rule uses.')}
{table(['Rule', 'From', 'Conclude'], [
    ['Modus Ponens', 'α ⇒ β and α', 'β'],
    ['And-Elimination', 'α ∧ β', 'α (and β)'],
    ['Biconditional elimination', 'α ⇔ β', '(α ⇒ β) ∧ (β ⇒ α)'],
    ['Contraposition', 'α ⇒ β', '¬β ⇒ ¬α'],
    ['De Morgan', '¬(α ∨ β)', '¬α ∧ ¬β'],
    ['Unit resolution', 'α ∨ β and ¬β', 'α']])}
{steps('Proof that there is no pit in [1,2] or [2,1] (from R2 and R4 of chapter 7.1)', [
    'R2: B<sub>1,1</sub> ⇔ (P<sub>1,2</sub> ∨ P<sub>2,1</sub>). Biconditional elimination gives R6: (B<sub>1,1</sub> ⇒ (P<sub>1,2</sub> ∨ P<sub>2,1</sub>)) ∧ ((P<sub>1,2</sub> ∨ P<sub>2,1</sub>) ⇒ B<sub>1,1</sub>).',
    'And-Elimination on R6 gives R7: (P<sub>1,2</sub> ∨ P<sub>2,1</sub>) ⇒ B<sub>1,1</sub>.',
    'Contraposition gives R8: ¬B<sub>1,1</sub> ⇒ ¬(P<sub>1,2</sub> ∨ P<sub>2,1</sub>).',
    'Modus Ponens with R4 (¬B<sub>1,1</sub>) gives R9: ¬(P<sub>1,2</sub> ∨ P<sub>2,1</sub>).',
    'De Morgan gives R10: ¬P<sub>1,2</sub> ∧ ¬P<sub>2,1</sub>.',
    eq('neither [1,2] nor [2,1] has a pit, proved in 5 steps without listing 128 models')])}
{note('Logic is <b>monotonic</b>: adding sentences to a KB never removes something it already entails. If KB ⊨ α then KB ∧ β ⊨ α. So a rule can be used whenever its premises are in the KB, whatever else is there.', 'tip')}
''', kw=['inference rule', 'modus ponens', 'and elimination', 'proof', 'monotonic', 'contraposition'])

K.lesson('resolution', 'Resolution and conjunctive normal form', f'''
{src('AIMA 4th ed., section 7.5.2.')}
{fxs(
    fx('The resolution rule', 'from ℓ<sub>1</sub> ∨ ... ∨ ℓ<sub>k</sub> and m<sub>1</sub> ∨ ... ∨ m<sub>n</sub>, where ℓ<sub>i</sub> and m<sub>j</sub> are opposite literals, conclude the clause of all the other literals', 'Example: from P ∨ Q and ¬Q ∨ R, conclude P ∨ R. Copies of the same literal are kept once (factoring).', key=True),
    fx('Why it is sound', 'if ℓ<sub>i</sub> is true then m<sub>j</sub> is false, so the rest of the second clause must be true. If ℓ<sub>i</sub> is false, the rest of the first clause must be true', 'Either way, the joined rest is true.'))}
<p>Resolution works on <b>clauses</b>: ORs of literals. A sentence that is an AND of clauses is in <b>conjunctive normal form</b> (CNF). Every sentence can be turned into an equivalent CNF sentence.</p>
{steps('Converting R2: B<sub>1,1</sub> ⇔ (P<sub>1,2</sub> ∨ P<sub>2,1</sub>) to CNF', [
    'Remove ⇔: (B<sub>1,1</sub> ⇒ (P<sub>1,2</sub> ∨ P<sub>2,1</sub>)) ∧ ((P<sub>1,2</sub> ∨ P<sub>2,1</sub>) ⇒ B<sub>1,1</sub>).',
    'Remove ⇒ (α ⇒ β becomes ¬α ∨ β): (¬B<sub>1,1</sub> ∨ P<sub>1,2</sub> ∨ P<sub>2,1</sub>) ∧ (¬(P<sub>1,2</sub> ∨ P<sub>2,1</sub>) ∨ B<sub>1,1</sub>).',
    'Move ¬ inwards with De Morgan: (¬B<sub>1,1</sub> ∨ P<sub>1,2</sub> ∨ P<sub>2,1</sub>) ∧ ((¬P<sub>1,2</sub> ∧ ¬P<sub>2,1</sub>) ∨ B<sub>1,1</sub>).',
    'Distribute ∨ over ∧: (¬B<sub>1,1</sub> ∨ P<sub>1,2</sub> ∨ P<sub>2,1</sub>) ∧ (¬P<sub>1,2</sub> ∨ B<sub>1,1</sub>) ∧ (¬P<sub>2,1</sub> ∨ B<sub>1,1</sub>).',
    eq('three clauses')])}
{algo('PL-RESOLUTION', [
    'function PL-RESOLUTION(KB, α) returns true or false',
    '    clauses = the clauses of the CNF form of KB ∧ ¬α',
    '    new = { }',
    '    loop:',
    '        for each pair of clauses Ci, Cj in clauses:',
    '            resolvents = PL-RESOLVE(Ci, Cj)',
    '            if resolvents contains the empty clause: return true',
    '            new = new ∪ resolvents',
    '        if new ⊆ clauses: return false       (nothing new: no contradiction)',
    '        clauses = clauses ∪ new'])}
{viz('resolution', kb='B11 ⇔ (P12 ∨ P21)\n¬B11', q='¬P12')}
{code('resolve')}
{note('The ground resolution theorem: if a set of clauses is unsatisfiable, resolution will reach the empty clause. So resolution is a complete refutation procedure for propositional logic. It cannot list every entailed sentence directly, but it can always confirm or refute a given one.', 'exam')}
''', kw=['resolution', 'clause', 'CNF', 'conjunctive normal form', 'empty clause', 'refutation', 'factoring', 'ground resolution theorem'])

K.lesson('horn', 'Horn clauses, forward and backward chaining', f'''
{src('AIMA 4th ed., section 7.5.4.')}
{table(['Clause type', 'At most / exactly', 'Example', 'As an implication'], [
    ['Definite clause', 'exactly one positive literal', '¬L ∨ ¬M ∨ P', 'L ∧ M ⇒ P'],
    ['Fact', 'one positive literal and nothing else', 'A', 'A'],
    ['Horn clause', 'at most one positive literal', '¬A ∨ ¬B', 'A ∧ B ⇒ False (a goal clause)']])}
{wwh('Forward chaining starts with the known facts, fires every rule whose premises are all known, and adds its conclusion, until the query appears or nothing new comes. Backward chaining starts with the query and looks for rules that conclude it, then tries to prove their premises the same way.',
     'Most rule based systems use rules of the form "if these hold then that holds". For these definite clauses, chaining decides entailment in time linear in the size of the KB, far faster than general methods.',
     'Forward chaining keeps a count of unknown premises for each rule and an agenda of new facts. Backward chaining is a depth first AND OR search: OR over the rules for a goal, AND over the premises of a rule, with a check for goals already on the path.')}
{viz('chaining', mode='fc')}
{code('fc')}
{table(['', 'Forward chaining', 'Backward chaining'], [
    ['Driven by', 'Data (the facts)', 'The goal'],
    ['Good for', 'Watching a stream of new facts, such as sensors', 'Answering one question, such as "what should I do now?"'],
    ['Wasted work', 'May derive many facts unrelated to the query', 'Only touches relevant rules'],
    ['Cost', 'O(size of KB), each rule counted down at most once per premise', 'Often much less than the KB size'],
    ['Sound and complete for definite clauses', 'Yes', 'Yes, with the loop check']])}
''', kw=['Horn clause', 'definite clause', 'forward chaining', 'backward chaining', 'agenda', 'data driven', 'goal driven'])

K.lesson('sat', 'Fast satisfiability: DPLL and WalkSAT', f'''
{src('AIMA 4th ed., section 7.6.')}
{wwh('DPLL is a depth first search over truth values for a CNF formula, with three tricks that cut the search. WalkSAT is a local search that flips one symbol at a time.',
     'Proving KB ⊨ α is the same as showing KB ∧ ¬α is unsatisfiable. A good SAT solver therefore gives a good prover, and SAT solvers also find plans, schedules and circuit errors.',
     'DPLL assigns symbols one at a time and simplifies. Early termination: stop a branch as soon as a clause is false, or accept once every clause is true. Pure symbol: a symbol with the same sign in every remaining clause can be set to make them true. Unit clause: a clause with one literal left forces its value. WalkSAT picks a false clause and flips one of its symbols, either the one that makes the most clauses true or, with probability p, a random one.')}
{code('dpll')}
{table(['Method', 'Complete', 'Typical use'], [
    ['Truth table (TT-ENTAILS)', 'Yes', 'Teaching, tiny problems'],
    ['Resolution', 'Yes (refutation complete)', 'Theorem provers, the basis of first order provers'],
    ['Forward or backward chaining', 'Yes, for definite clauses only', 'Rule based systems, Prolog'],
    ['DPLL and its modern form CDCL', 'Yes', 'Industrial SAT solving with millions of clauses'],
    ['WalkSAT', 'No: it can find a model, but it cannot prove there is none', 'Large satisfiable problems']])}
{deep('Modern SAT solvers', '<p>Modern solvers use conflict driven clause learning (CDCL): when a branch fails, they work out which choices caused the conflict, add a new clause that rules out that combination, and jump back several levels at once. With watched literals for fast unit propagation, restarts and smart variable order, they solve industrial problems with millions of variables.</p>')}
''', kw=['DPLL', 'pure symbol', 'unit clause', 'early termination', 'WalkSAT', 'CDCL', 'SAT solver'])

K.lesson('maths', 'The maths: how many clauses, and how fast', f'''
{fxs(
    fx('Possible clauses over n symbols', '3<sup>n</sup>', 'Each symbol is positive, negative or absent in a clause. So resolution always stops: there are at most 3<sup>n</sup> distinct clauses to add.', key=True),
    fx('Clauses from distributing', '(a ∧ b) ∨ (c ∧ d) gives (a ∨ c) ∧ (a ∨ d) ∧ (b ∨ c) ∧ (b ∨ d)', 'An OR of k ANDs with 2 parts each gives 2<sup>k</sup> clauses: CNF can blow up. The Tseitin trick adds new symbols to keep it linear.'),
    fx('Forward chaining cost', 'O(n) for a KB of total size n', 'Each premise of each rule is counted down at most once.'),
    fx('Random 3-SAT hardness', 'm ⁄ n ≈ 4.26', 'With m clauses over n symbols, problems are hardest near this ratio. Below it almost all are satisfiable, above it almost none.'))}
{steps('Worked example: resolve (A ∨ B ∨ ¬C) with (¬B ∨ D)', [
    'The opposite pair is B and ¬B.',
    'Keep the rest of the first clause: A ∨ ¬C.',
    'Keep the rest of the second: D.',
    eq('A ∨ ¬C ∨ D')])}
{steps('Worked example: why resolving on two pairs at once is wrong', [
    'Clauses: (P ∨ Q) and (¬P ∨ ¬Q).',
    'Wrong: cancel both pairs and get the empty clause, claiming a contradiction.',
    'But P = T, Q = F makes both clauses true, so they are satisfiable.',
    eq('resolve on one pair only: P ∨ ¬P or Q ∨ ¬Q, both always true and useless')])}
''', kw=['three to the n clauses', 'Tseitin', 'CNF blow up', 'linear time chaining', 'phase transition', 'resolution worked example'])

K.lesson('compare', 'Which inference method to use', f'''
{versus('Inference in propositional logic', ['', 'Model checking', 'Inference rules by hand', 'Resolution', 'Chaining', 'DPLL and WalkSAT'], [
    ['Works on', 'Any sentences', 'Any sentences', 'CNF', 'Definite clauses only', 'CNF'],
    ['Sound and complete', 'Yes', 'Depends on the rules chosen', 'Refutation complete', 'Yes, for definite clauses', 'DPLL yes, WalkSAT not for proving'],
    ['Time', '2<sup>n</sup> always', 'Search over proofs', 'Can be exponential', 'Linear', 'Exponential worst case, fast in practice'],
    ['Easy for people to follow', 'Yes, but long', 'Yes', 'Fairly', 'Yes', 'No']],
    'use chaining whenever the knowledge fits definite clauses, a SAT solver (DPLL or CDCL) for general problems, and resolution when you need a proof that can be checked and lifted to first order logic.')}
{scene('Rule based systems', '<p>Business rule engines (such as Drools) and the expert systems of the 1980s run forward chaining over large sets of if then rules. The Rete algorithm (Forgy, 1982) speeds this up by remembering partial matches, so a new fact only touches the rules it can affect. Prolog runs backward chaining.</p>')}
''', kw=['comparison', 'Rete', 'rule engine', 'Prolog', 'expert systems'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Instead of checking every possible world, follow safe rules step by step, like "if A gives B, and A is true, then B is true", until you reach what you want.</p>',
    '<p>Sound rules: Modus Ponens, And-Elimination, equivalences, resolution. Resolution on CNF is refutation complete. Definite clauses allow linear time forward and backward chaining. DPLL adds early termination, pure symbols and unit clauses, and WalkSAT searches locally.</p>',
    '<p>Resolution proofs can need exponential length: Haken (1985) showed the pigeonhole formulas need exponentially long resolution proofs. That is a limit of the proof system, not just of a search strategy. CDCL solvers are, in a precise sense, as strong as general resolution (Pipatsrisawat and Darwiche, 2011).</p>',
    '<p>Research topics: proof systems stronger than resolution (cutting planes, extended resolution), certified SAT solving where the solver outputs a checkable proof of unsatisfiability, and learning heuristics for SAT with neural networks.</p>')}
''', kw=['Haken', 'pigeonhole', 'proof complexity', 'CDCL', 'certified SAT'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Inference rules such as Modus Ponens and And-Elimination give proofs that skip irrelevant symbols. Logic is monotonic.',
    'Resolution: from ℓ ∨ α and ¬ℓ ∨ β, get α ∨ β. Turn sentences into CNF in four steps: remove ⇔, remove ⇒, move ¬ in, distribute ∨ over ∧.',
    'Proof by resolution adds ¬α and searches for the empty clause. It is refutation complete.',
    'Definite clauses allow forward chaining (from facts) and backward chaining (from the goal) in linear time.',
    'DPLL (early termination, pure symbols, unit clauses) and WalkSAT solve SAT. Modern CDCL solvers handle millions of clauses.'],
    'chapter 7.3 moves to first order logic, which can talk about objects and relations, so one sentence covers every room.')}
{nbcard('propositional-inference', 'Run resolution, forward chaining and DPLL on small examples, then write the resolution rule, forward chaining and a DPLL solver yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Modus Ponens says: from α ⇒ β and α, conclude', ['α', 'β', '¬β', 'α ∧ ¬β'], 1,
       'The basic rule.', 'If the premise holds and the rule holds, the conclusion holds.')
K.quiz('e', 'A clause is', ['an AND of literals', 'an OR of literals', 'any sentence', 'a single symbol only'], 1,
       'CNF is an AND of these.', 'A clause is a disjunction of literals.')
K.quiz('e', 'Resolve P ∨ Q with ¬Q ∨ R. The result is', ['P ∨ R', 'Q', 'P ∧ R', '¬P ∨ ¬R'], 0,
       'Cancel Q and ¬Q.', 'Join the rest: P ∨ R.')
K.quiz('e', 'Forward chaining starts from', ['the query', 'the known facts', 'a random symbol', 'the empty clause'], 1,
       'Data driven.', 'It fires rules whose premises are known.')
K.quiz('m', 'Proof by resolution finds that KB ⊨ α when', ['it derives α', 'it derives the empty clause from KB ∧ ¬α', 'no new clause appears', 'it derives ¬α'], 1,
       'Contradiction.', 'The empty clause means KB ∧ ¬α is unsatisfiable.')
K.quiz('m', 'Which clause is a definite clause?', ['¬A ∨ ¬B', 'A ∨ B', '¬A ∨ ¬B ∨ C', 'A ∨ B ∨ ¬C'], 2,
       'Exactly one positive literal.', '¬A ∨ ¬B ∨ C is A ∧ B ⇒ C.')
K.quiz('m', 'In DPLL, a pure symbol is', ['a symbol in only one clause', 'a symbol that appears with the same sign in every remaining clause', 'a symbol already set', 'a unit clause'], 1,
       'Only positive or only negative.', 'Setting it to make its literal true can never hurt.')
K.quiz('m', 'Logic is monotonic means', ['the KB must be ordered', 'adding sentences never removes an entailed sentence', 'every rule is used once', 'proofs get shorter'], 1,
       'More knowledge, never fewer conclusions.', 'If KB ⊨ α then KB ∧ β ⊨ α.')
K.quiz('h', 'Why can WalkSAT not prove KB ⊨ α?', ['It is too slow', 'It can find a model of KB ∧ ¬α if one exists, but failing to find one does not prove none exists', 'It needs Horn clauses', 'It only works with 2 symbols'], 1,
       'Incomplete.', 'Proving entailment means proving unsatisfiability, which needs a complete method.')
K.quiz('h', 'How many distinct clauses can exist over n symbols?', ['2<sup>n</sup>', '3<sup>n</sup>', 'n²', 'n!'], 1,
       'Positive, negative or absent.', 'So resolution must stop.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: from (P ∨ Q) and (¬P ∨ ¬Q), resolving on both pairs at once gives { }. What is wrong?', ['Nothing, the clauses are unsatisfiable', 'Resolution may cancel only one pair, and the two clauses are satisfiable (P = T, Q = F)', 'Clauses cannot have two literals', 'You must use Modus Ponens'], 1,
       'Check a model.', 'One pair per step. Resolving on P gives Q ∨ ¬Q, a tautology.')
K.quiz('x', 'In the style of an MIT 6.034 exam: to prove A from {A ∨ B, ¬B}, the resolution refutation needs how many resolution steps?', ['1', '2', '3', '0'], 1,
       'Add ¬A.', '¬A with A ∨ B gives B, B with ¬B gives { }.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many clauses does the CNF of B11 ⇔ (P12 ∨ P21) have?', '3', 'One from B11 ⇒ ..., two from the other direction.',
       ['B11 ⇒ (P12 ∨ P21) gives ¬B11 ∨ P12 ∨ P21.', '(P12 ∨ P21) ⇒ B11 gives (¬P12 ∨ B11) ∧ (¬P21 ∨ B11).', eq('1 + 2 = 3 clauses')], check=3)
K.calc('e', 'How many literals has the resolvent of (A ∨ B ∨ ¬C) and (¬B ∨ D)?', '3', 'Cancel B and ¬B.',
       ['Rest of the first: A, ¬C.', 'Rest of the second: D.', eq('A ∨ ¬C ∨ D: 3 literals')], check=3)
K.calc('e', 'How many possible clauses are there over 3 symbols (each positive, negative or absent)?', '27', '3³.',
       ['3 choices per symbol.', '3 × 3 × 3.', eq('27, including the empty clause')], check=27)
K.calc('m', 'Forward chaining on the textbook KB (P ⇒ Q, L ∧ M ⇒ P, B ∧ L ⇒ M, A ∧ P ⇒ L, A ∧ B ⇒ L, facts A, B). How many rules fire before Q is taken from the agenda?', '5', 'Follow the counts.',
       ['A and B make A ∧ B ⇒ L fire (1). L makes B ∧ L ⇒ M fire (2).', 'M makes L ∧ M ⇒ P fire (3). P makes P ⇒ Q fire (4) and A ∧ P ⇒ L fire (5).', eq('5 rules fire, then Q is taken and the query is proved')], check=5)
K.calc('m', 'Distributing (a ∧ b) ∨ (c ∧ d) ∨ (e ∧ f) into CNF. How many clauses?', '8', '2 choices from each of 3 parts.',
       ['Each clause picks one literal from each AND.', '2 × 2 × 2.', eq('8 clauses')], check=8)
K.calc('m', 'Random 3-SAT with 100 symbols. At the hardest ratio m ⁄ n ≈ 4.26, about how many clauses?', '426', 'm = 4.26 × n.',
       ['n = 100.', 'm = 4.26 × 100.', eq('426 clauses')], check=426)
K.calc('h', 'A KB of definite clauses has 1,000 rules with 4 premises each. At most how many count decrements does forward chaining do?', '4000', 'Each premise is counted down at most once.',
       ['Each rule has 4 premises.', '1,000 × 4.', eq('4,000 decrements: linear in the KB size')], check=4000)
K.calc('h', 'DPLL on [x1 ∨ x2], [¬x1 ∨ x3], [¬x2 ∨ x3], [¬x3 ∨ x4], [¬x4 ∨ ¬x1]. It guesses x1 = T first. How many clauses are left after unit propagation finishes?', '0', 'Follow the units.',
       ['x1 = T: [x1 ∨ x2] is true. [¬x1 ∨ x3] becomes unit x3, and [¬x4 ∨ ¬x1] becomes unit ¬x4.', 'x3 = T: [¬x3 ∨ x4] becomes unit x4. But ¬x4 is also forced: conflict, so x1 = T fails.', 'Try x1 = F: [x1 ∨ x2] gives x2 = T, then x3 = T, then x4 = T. [¬x4 ∨ ¬x1] is true since x1 = F.', eq('0 clauses left: model x1 = F, x2 = T, x3 = T, x4 = T')], check=0)
K.calc('h', 'How many models do 20 symbols have? Give the answer in millions, to 2 decimals.', '1.05', '2²⁰.',
       ['2¹⁰ = 1,024.', '2²⁰ = 1,024² = 1,048,576.', eq('≈ 1.05 million models')], check=1.05, tol=0.01)
K.calc('x', 'In the style of a Stanford CS221 problem: KB = {A ⇒ B, B ⇒ C, A}. Prove C by resolution. Counting ¬C as given, how many resolution steps reach { }?', '3', 'Use the set of support: start from ¬C.',
       ['Clauses: ¬A ∨ B, ¬B ∨ C, A, and ¬C.', '¬C with ¬B ∨ C gives ¬B. ¬B with ¬A ∨ B gives ¬A.', '¬A with A gives { }.', eq('3 steps')], check=3)

# ---------------------------------------------------------------- assignments
K.assign('resolve', 'e', 'The resolution rule',
         '<p>A clause is a Python set of literal strings, where <code>"-P"</code> means ¬P. Write <code>resolve(a, b)</code> that returns the list of all resolvents, each as a sorted list. Resolve on one pair at a time. Leave out resolvents that contain a literal and its opposite (they are always true).</p>',
         '''
def resolve(a, b):
    # your code here
    pass
''', [("resolve({'P', 'Q'}, {'-Q', 'R'})", [['P', 'R']]),
      ("resolve({'P12'}, {'-P12', 'B11'})", [['B11']]),
      ("resolve({'B11'}, {'-B11'})", [[]]),
      ("resolve({'P', 'Q'}, {'-P', '-Q'})", []),
      ("resolve({'A'}, {'B'})", [])],
         '''
def opposite(lit):
    if lit.startswith("-"):
        return lit[1:]
    return "-" + lit

def resolve(a, b):
    out = []
    for lit in sorted(a):
        if opposite(lit) in b:
            rest = (a - {lit}) | (b - {opposite(lit)})
            useless = False
            for x in rest:
                if opposite(x) in rest:
                    useless = True
            if not useless:
                out.append(sorted(rest))
    return out
''', 'For each literal in a whose opposite is in b, join the two clauses without that pair. Skip a result that holds both X and -X.', '<p>Test 4 is the classic mistake: both possible resolvents are always true, so they are dropped and the answer is an empty list.</p>')
K.assign('fcent', 'm', 'Forward chaining',
         '<p>Write <code>fc_entails(rules, facts, q)</code>. rules is a list of <code>(premises, conclusion)</code> pairs, facts a list of symbols known to be true. Return True if forward chaining reaches q.</p>',
         '''
def fc_entails(rules, facts, q):
    # your code here
    pass
''', [("fc_entails([(['P'], 'Q'), (['L', 'M'], 'P'), (['B', 'L'], 'M'), (['A', 'P'], 'L'), (['A', 'B'], 'L')], ['A', 'B'], 'Q')", True),
      ("fc_entails([(['P'], 'Q'), (['L', 'M'], 'P'), (['B', 'L'], 'M'), (['A', 'P'], 'L')], ['A', 'B'], 'Q')", False),
      ("fc_entails([], ['A'], 'A')", True),
      ("fc_entails([(['A'], 'B'), (['B'], 'C'), (['C', 'D'], 'E')], ['A'], 'E')", False),
      ("fc_entails([(['A'], 'B'), (['B'], 'C'), (['C', 'A'], 'E')], ['A'], 'E')", True)],
         '''
def fc_entails(rules, facts, q):
    count = []
    for premises, conclusion in rules:
        count.append(len(premises))
    known = set()
    agenda = list(facts)
    while agenda:
        s = agenda.pop(0)
        if s == q:
            return True
        if s in known:
            continue
        known.add(s)
        for i in range(len(rules)):
            if s in rules[i][0]:
                count[i] = count[i] - 1
                if count[i] == 0:
                    agenda.append(rules[i][1])
    return False
''', 'Keep a count of unknown premises per rule and an agenda of symbols to process. When a count reaches 0, add that rule\'s conclusion to the agenda.', '<p>Test 2 removes the rule A ∧ B ⇒ L. Now L needs P and P needs L, so nothing fires and Q is not reached.</p>')
K.assign('dpll', 'h', 'A DPLL solver',
         '<p>Write <code>dpll_sat(clauses)</code>. Clauses are lists of non zero integers: 3 means x3 and −3 means ¬x3. Return True if some assignment makes every clause true, else False. Use early termination and unit clauses.</p>',
         '''
def dpll_sat(clauses):
    # your code here
    pass
''', [("dpll_sat([[1, 2], [-1, 3], [-2, 3], [-3, 4], [-4, -1]])", True),
      ("dpll_sat([[1], [-1]])", False),
      ("dpll_sat([[1, 2], [-1, 2], [1, -2], [-1, -2]])", False),
      ("dpll_sat([])", True),
      ("dpll_sat([[1, 2, 3], [-1], [-2], [-3, 4], [-4]])", False)],
         '''
def simplify(clauses, lit):
    out = []
    for c in clauses:
        if lit in c:
            continue
        smaller = []
        for x in c:
            if x != -lit:
                smaller.append(x)
        out.append(smaller)
    return out

def dpll_sat(clauses):
    if len(clauses) == 0:
        return True
    for c in clauses:
        if len(c) == 0:
            return False
    for c in clauses:
        if len(c) == 1:
            return dpll_sat(simplify(clauses, c[0]))
    lit = clauses[0][0]
    if dpll_sat(simplify(clauses, lit)):
        return True
    return dpll_sat(simplify(clauses, -lit))
''', 'simplify(clauses, lit) removes clauses that contain lit and removes -lit from the others. Then: no clauses means True, an empty clause means False, a unit clause forces its literal, otherwise try both values.', '<p>Test 3 lists all four clauses over x1 and x2, so every assignment breaks one. Test 5 forces x1, x2 and x3 false, which breaks the first clause.</p>')

K.must('Rules', 'Modus Ponens: α ⇒ β, α ⊢ β. And-Elimination. Equivalences as rules. Monotonic.')
K.must('Resolution', 'ℓ ∨ α, ¬ℓ ∨ β ⊢ α ∨ β. One pair at a time. Refutation complete.')
K.must('CNF steps', 'Remove ⇔, remove ⇒, move ¬ in (De Morgan, double negation), distribute ∨ over ∧.')
K.must('Chaining', 'Definite clause: exactly one positive literal. Forward from facts, backward from goal. Linear time.')
K.must('SAT', 'DPLL: early termination, pure symbol, unit clause. WalkSAT: local search, incomplete. CDCL in practice.')

T = K.topic(
    slug='propositional-inference', topic='propositional-inference', step=(7, 'Logic and knowledge', 'cai-logic', 'Agents that know facts and reason with them: propositional logic, inference rules, resolution, chaining, first order logic and unification.', 'College'),
    title='Reasoning patterns: rules, resolution and chaining', short='Propositional inference', badge='7.2', minutes=55,
    lead='Prove things without listing every model. Use inference rules, turn sentences into clauses and resolve them, chain through if then rules forwards and backwards, and see how SAT solvers like DPLL decide huge problems.',
    desc='Inference rules and proofs, monotonicity, the wumpus proof, the resolution rule, conversion to CNF, PL-RESOLUTION and refutation completeness, Horn and definite clauses, forward and backward chaining, DPLL with early termination, pure symbols and unit clauses, WalkSAT, CDCL, and the maths of clause counts and chaining cost.',
    summary='Inference rules, resolution, CNF, forward and backward chaining, DPLL and WalkSAT.',
    keywords=['inference rules', 'modus ponens', 'resolution', 'CNF', 'Horn clause', 'forward chaining', 'backward chaining', 'DPLL', 'WalkSAT'],
    recap='<p>Resolution on clauses is refutation complete. Definite clauses allow linear time chaining. DPLL decides SAT.</p>',
    nb={'resolve': 'Resolution refutation for the wumpus question', 'fc': 'Forward chaining with counts and an agenda', 'dpll': 'DPLL with unit clauses'})
