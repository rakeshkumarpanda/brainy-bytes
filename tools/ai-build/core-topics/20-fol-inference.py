# Chapter 7.4: inference in first order logic. Follows Russell and Norvig, AIMA 4th ed., chapter 9 (universal and
# existential instantiation, propositionalisation, unification and Generalised Modus Ponens, forward chaining on the
# crime example, backward chaining and Prolog, conversion to CNF with Skolemisation, and resolution). The unification
# table and the forward chaining rounds were checked by running the code of this chapter.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('unify', r'''
# Unification. A variable is a string that starts with a lower case letter, a constant starts with a capital.
# A compound term or atom is a tuple: ("Knows", "John", "x") means Knows(John, x).
def is_var(t):
    return type(t) == str and t[0].islower()

def unify(x, y, theta):
    if theta is None:
        return None
    if x == y:
        return theta
    if is_var(x):
        return unify_var(x, y, theta)
    if is_var(y):
        return unify_var(y, x, theta)
    if type(x) == tuple and type(y) == tuple and len(x) == len(y):
        for a, b in zip(x, y):
            theta = unify(a, b, theta)
        return theta
    return None

def unify_var(v, t, theta):
    if v in theta:
        return unify(theta[v], t, theta)
    if is_var(t) and t in theta:
        return unify(v, theta[t], theta)
    if occurs(v, t, theta):
        return None
    new = dict(theta)
    new[v] = t
    return new

def occurs(v, t, theta):
    if t == v:
        return True
    if is_var(t) and t in theta:
        return occurs(v, theta[t], theta)
    if type(t) == tuple:
        return any(occurs(v, a, theta) for a in t)
    return False

def subst(theta, t):
    if is_var(t) and t in theta:
        return subst(theta, theta[t])
    if type(t) == tuple:
        return tuple(subst(theta, a) for a in t)
    return t

q = ("Knows", "John", "x")
for other in [("Knows", "John", "Jane"), ("Knows", "y", "Bill"), ("Knows", "y", ("Mother", "y")), ("Knows", "x", "Elizabeth")]:
    theta = unify(q, other, {})
    if theta is None:
        print(other, "-> fail")
    else:
        print(other, "->", {v: subst(theta, v) for v in theta})
''')

K.code('fcfol', r'''
# Forward chaining on the crime example. Facts are stored by predicate name, so a premise is only
# compared with facts of the same predicate. Facts have no variables, so matching is simple.
facts = {"American": [("West",)], "Missile": [("M1",)], "Owns": [("Nono", "M1")], "Enemy": [("Nono", "America")]}
rules = [([("Missile", "x")], ("Weapon", "x")),
         ([("Missile", "x"), ("Owns", "Nono", "x")], ("Sells", "West", "x", "Nono")),
         ([("Enemy", "x", "America")], ("Hostile", "x")),
         ([("American", "x"), ("Weapon", "y"), ("Sells", "x", "y", "z"), ("Hostile", "z")], ("Criminal", "x"))]

def match(args, values, theta):
    theta = dict(theta)
    for a, v in zip(args, values):
        if a[0].islower():                    # a variable: bind it, or check its binding
            if theta.get(a, v) != v:
                return None
            theta[a] = v
        elif a != v:                          # a constant must be equal
            return None
    return theta

def all_matches(premises, theta):
    if not premises:
        return [theta]
    out = []
    first = premises[0]
    for values in facts.get(first[0], []):
        t = match(first[1:], values, theta)
        if t is not None:
            out = out + all_matches(premises[1:], t)
    return out

for rnd in [1, 2]:
    new = []
    for premises, head in rules:
        for theta in all_matches(premises, {}):
            args = tuple([theta.get(a, a) for a in head[1:]])
            if args not in facts.get(head[0], []) and (head[0], args) not in new:
                new.append((head[0], args))
    print("round", rnd, "adds", ", ".join([p + "(" + ", ".join(a) + ")" for p, a in new]))
    for p, a in new:
        facts.setdefault(p, []).append(a)
''')

K.lesson('prop', 'From first order inference to propositional inference', f'''
{src('Russell and Norvig, AIMA 4th ed., section 9.1. The uploaded slides do not cover logic, so this step follows the textbook.')}
{table(['Rule', 'What it does', 'Example'], [
    ['Universal Instantiation (UI)', 'From ∀v α, infer α with v replaced by any ground term g', 'From ∀x King(x) ∧ Greedy(x) ⇒ Evil(x), infer King(John) ∧ Greedy(John) ⇒ Evil(John)'],
    ['Existential Instantiation (EI)', 'From ∃v α, infer α with v replaced by a brand new constant k (a Skolem constant)', 'From ∃x Crown(x) ∧ OnHead(x, John), infer Crown(C1) ∧ OnHead(C1, John)']])}
<p>UI can be used many times, with every ground term. EI is used once, and then the ∃ sentence is dropped. Using both on every quantified sentence, a first order KB becomes a propositional KB: this is <b>propositionalisation</b>.</p>
{steps('Why that is not enough', [
    'With k constants, a rule with v variables becomes k<sup>v</sup> ground rules. Most of them are useless.',
    'With a function symbol such as Father(·), there are infinitely many ground terms: John, Father(John), Father(Father(John)), and so on.',
    'Herbrand\'s theorem saves completeness: if α is entailed, it is entailed by a finite part of the ground KB. So try terms of depth 0, then depth 1, then depth 2, until a proof is found.',
    'But if α is not entailed, this can go on for ever.',
    eq('first order entailment is semidecidable: a yes is always found, a no may never come')])}
''', kw=['universal instantiation', 'existential instantiation', 'Skolem constant', 'propositionalisation', 'Herbrand', 'semidecidable'])

K.lesson('unify', 'Unification and lifting', f'''
{src('AIMA 4th ed., section 9.2.')}
{wwh('Unification finds a substitution θ that makes two atoms look the same. Generalised Modus Ponens uses it to apply a rule to facts directly, without making every ground copy of the rule first. This is called <b>lifting</b> an inference rule to first order logic.',
     'Propositionalisation makes k<sup>v</sup> copies of each rule. Unification makes only the substitutions that the facts at hand need, so most useless work disappears.',
     'Compare the two atoms from the outside in. Same predicate and argument count: unify the arguments pair by pair. A variable meets a term: bind it, unless the variable occurs inside the term (the occurs check). Two different constants, or two different functions: fail. Keep the bindings in θ and apply them as you go.')}
{fxs(
    fx('Generalised Modus Ponens (GMP)', 'from p<sub>1</sub>′, ..., p<sub>n</sub>′ and (p<sub>1</sub> ∧ ... ∧ p<sub>n</sub> ⇒ q), infer SUBST(θ, q), where SUBST(θ, p<sub>i</sub>′) = SUBST(θ, p<sub>i</sub>) for every i', 'King(John), Greedy(y) and King(x) ∧ Greedy(x) ⇒ Evil(x) with θ = {x/John, y/John} give Evil(John).', key=True),
    fx('UNIFY', 'UNIFY(p, q) = θ where SUBST(θ, p) = SUBST(θ, q)', 'θ is written as a set of bindings variable/term.'))}
{table(['p', 'q', 'θ = UNIFY(p, q)'], [
    ['Knows(John, x)', 'Knows(John, Jane)', '{x/Jane}'],
    ['Knows(John, x)', 'Knows(y, Bill)', '{x/Bill, y/John}'],
    ['Knows(John, x)', 'Knows(y, Mother(y))', '{y/John, x/Mother(John)}'],
    ['Knows(John, x)', 'Knows(x, Elizabeth)', 'fail: x cannot be John and Elizabeth'],
    ['Knows(John, x)', 'Knows(x17, Elizabeth)', '{x17/John, x/Elizabeth}, after standardising apart']])}
<p><b>Standardising apart</b>: rename the variables of one sentence so that the two sentences share none. The x in "John knows x" and the x in "x knows Elizabeth" are different variables that happen to share a name.</p>
<p><b>Most general unifier (MGU)</b>: Knows(John, x) and Knows(y, z) unify with {{y/John, x/z}} or with {{y/John, x/John, z/John}}. The first is more general, since it commits to less. Up to renaming of variables, every unifiable pair has a single MGU.</p>
{viz('unify')}
{code('unify')}
{note('The occurs check (does the variable appear inside the term?) makes unification cost quadratic in the size of the terms. Prolog leaves it out for speed, so Prolog can unify x with F(x) and build an endless term.', 'warn')}
''', kw=['unification', 'substitution', 'generalised modus ponens', 'lifting', 'standardising apart', 'most general unifier', 'occurs check'])

K.lesson('fc', 'Forward chaining: the crime example', f'''
{src('AIMA 4th ed., section 9.3.')}
<p>"The law says that it is a crime for an American to sell weapons to hostile nations. The country Nono, an enemy of America, has some missiles, and all of its missiles were sold to it by Colonel West, who is American. Prove that West is a criminal."</p>
{table(['Sentence in definite clauses', 'Meaning'], [
    ['American(x) ∧ Weapon(y) ∧ Sells(x, y, z) ∧ Hostile(z) ⇒ Criminal(x)', 'the law'],
    ['Owns(Nono, M1), Missile(M1)', 'Nono has a missile, M1 (EI on "Nono has some missiles")'],
    ['Missile(x) ∧ Owns(Nono, x) ⇒ Sells(West, x, Nono)', 'all of Nono\'s missiles were sold by West'],
    ['Missile(x) ⇒ Weapon(x)', 'missiles are weapons'],
    ['Enemy(x, America) ⇒ Hostile(x)', 'an enemy of America counts as hostile'],
    ['American(West), Enemy(Nono, America)', 'facts']])}
{steps('Forward chaining', [
    'Round 1: Missile(x) ⇒ Weapon(x) with {x/M1} gives Weapon(M1).',
    'Round 1: Missile(x) ∧ Owns(Nono, x) ⇒ Sells(West, x, Nono) with {x/M1} gives Sells(West, M1, Nono).',
    'Round 1: Enemy(x, America) ⇒ Hostile(x) with {x/Nono} gives Hostile(Nono).',
    'Round 2: the law with {x/West, y/M1, z/Nono} gives Criminal(West).',
    eq('proved in 2 rounds, and a fixed point: nothing more can be added')])}
{viz('folchain', mode='fc')}
{code('fcfol')}
{table(['Fact about first order forward chaining', 'Detail'], [
    ['Sound and complete for first order definite clauses', 'Every entailed atom is eventually derived'],
    ['Datalog', 'Definite clauses with no function symbols. Forward chaining then stops after polynomially many steps'],
    ['Pattern matching is hard', 'Finding all θ that match a rule\'s premises to the facts is like solving a CSP, and is NP-hard in general. Order the premises, most constrained first'],
    ['Incremental forward chaining', 'In round t, only try rules with a premise that matches a fact new in round t − 1'],
    ['Rete', 'Store partial matches in a network so new facts update them cheaply (used in rule engines)']])}
''', kw=['forward chaining', 'crime example', 'Colonel West', 'Datalog', 'pattern matching', 'Rete', 'fixed point'])

K.lesson('bc', 'Backward chaining and Prolog', f'''
{src('AIMA 4th ed., section 9.4.')}
<p>Backward chaining starts with the goal Criminal(West). It finds a rule whose head unifies with the goal, then makes each premise a new goal, carrying the bindings found so far from left to right. It is a depth first AND OR search over proofs.</p>
{viz('folchain', mode='bc')}
{table(['Prolog feature', 'What it means'], [
    ['Syntax', 'criminal(X) :- american(X), weapon(Y), sells(X, Y, Z), hostile(Z). Upper case letters are variables'],
    ['Search', 'Depth first, rules in the order written, premises left to right'],
    ['Negation as failure', 'not P (written with a special operator in Prolog) succeeds if P cannot be proved. This is the closed world assumption, not real negation'],
    ['No occurs check', 'Faster unification, but unsound in rare cases'],
    ['Incomplete', 'A left recursive rule such as path(X, Z) :- path(X, Y), link(Y, Z) can loop for ever. Writing link first fixes it'],
    ['Tabling', 'Remembering solved subgoals (memoisation) avoids repeated work and many loops']])}
{note('Backward chaining is the reason Prolog programs can be read as logic and run as programs. But the order of rules and premises changes what happens, which pure logic does not care about.', 'tip')}
''', kw=['backward chaining', 'Prolog', 'depth first', 'negation as failure', 'left recursion', 'tabling'])

K.lesson('res', 'Resolution in first order logic', f'''
{src('AIMA 4th ed., section 9.5.')}
{steps('Conversion to CNF: "everyone who loves all animals is loved by someone"', [
    'Start: ∀x [∀y Animal(y) ⇒ Loves(x, y)] ⇒ [∃y Loves(y, x)].',
    'Remove ⇒: ∀x ¬[∀y ¬Animal(y) ∨ Loves(x, y)] ∨ [∃y Loves(y, x)].',
    'Move ¬ inwards (¬∀ becomes ∃¬): ∀x [∃y Animal(y) ∧ ¬Loves(x, y)] ∨ [∃y Loves(y, x)].',
    'Standardise variables: ∀x [∃y Animal(y) ∧ ¬Loves(x, y)] ∨ [∃z Loves(z, x)].',
    'Skolemise: each ∃ variable becomes a Skolem function of the ∀ variables around it: y becomes F(x), z becomes G(x). ∀x [Animal(F(x)) ∧ ¬Loves(x, F(x))] ∨ Loves(G(x), x).',
    'Drop ∀ and distribute ∨ over ∧:',
    eq('[Animal(F(x)) ∨ Loves(G(x), x)] ∧ [¬Loves(x, F(x)) ∨ Loves(G(x), x)]')])}
{fxs(fx('Binary resolution', 'from ℓ<sub>1</sub> ∨ ... ∨ ℓ<sub>k</sub> and m<sub>1</sub> ∨ ... ∨ m<sub>n</sub> with UNIFY(ℓ<sub>i</sub>, ¬m<sub>j</sub>) = θ, infer SUBST(θ, all other literals)', 'Example: [Animal(F(x)) ∨ Loves(G(x), x)] and [¬Loves(u, v) ∨ ¬Kills(u, v)] with θ = {u/G(x), v/x} give Animal(F(x)) ∨ ¬Kills(G(x), x).', key=True))}
{steps('Resolution proof that West is a criminal (add ¬Criminal(West))', [
    '¬Criminal(West) with the law gives ¬American(West) ∨ ¬Weapon(y) ∨ ¬Sells(West, y, z) ∨ ¬Hostile(z).',
    'With American(West): ¬Weapon(y) ∨ ¬Sells(West, y, z) ∨ ¬Hostile(z). With ¬Missile(x) ∨ Weapon(x): ¬Missile(y) ∨ ¬Sells(West, y, z) ∨ ¬Hostile(z).',
    'With Missile(M1): ¬Sells(West, M1, z) ∨ ¬Hostile(z). With the Sells rule: ¬Missile(M1) ∨ ¬Owns(Nono, M1) ∨ ¬Hostile(Nono).',
    'With Missile(M1), then Owns(Nono, M1): ¬Hostile(Nono). With the Hostile rule: ¬Enemy(Nono, America). With Enemy(Nono, America): the empty clause.',
    eq('9 resolution steps, and they follow exactly the steps of backward chaining')])}
{table(['Fact about first order resolution', 'Detail'], [
    ['Refutation complete (Robinson, 1965)', 'If KB ⊨ α, resolution with factoring derives { } from KB ∧ ¬α'],
    ['Factoring', 'Merge two literals of one clause that unify, for example P(x) ∨ P(A) becomes P(A)'],
    ['Equality', 'Needs extra rules: demodulation (rewrite with x = y) and paramodulation'],
    ['Strategies', 'Unit preference (resolve with short clauses), set of support (always use a clause from ¬α or derived from it), input resolution, subsumption (delete clauses implied by shorter ones)'],
    ['Used in', 'Theorem provers such as Vampire and E, and software verification']])}
''', kw=['resolution', 'CNF for FOL', 'Skolemisation', 'Skolem function', 'factoring', 'set of support', 'refutation complete', 'Robinson'])

K.lesson('maths', 'The maths: instances, ground terms and proof size', f'''
{fxs(
    fx('Ground instances of one rule', 'k<sup>v</sup>', 'k constants, v variables. The crime law has v = 3 and the KB has k = 4 constants (West, M1, Nono, America): 64 copies, of which forward chaining needs 1.', key=True),
    fx('Ground terms with one unary function F and one constant A, up to depth d', 'd + 1', 'A, F(A), F(F(A)), and so on.'),
    fx('Ground terms with c constants and one binary function, depth at most 1', 'c + c²', 'Each argument is a constant. Depth 2 grows much faster.'))}
{steps('Worked example: unify P(x, F(y)) with P(G(z), F(A))', [
    'Same predicate P with 2 arguments: unify pair by pair.',
    'x with G(z): x is a variable, so bind x/G(z).',
    'F(y) with F(A): same function, so unify y with A: bind y/A.',
    eq('θ = {x/G(z), y/A}, and both become P(G(z), F(A))')])}
{steps('Worked example: why P(x, x) does not unify with P(A, B)', [
    'First pair: x with A, bind x/A.',
    'Second pair: x with B. x is already bound to A, so compare A with B.',
    'A and B are different constants.',
    eq('fail')])}
''', kw=['ground instances', 'k to the v', 'Herbrand terms', 'unification worked example'])

K.lesson('compare', 'Which first order inference method to use', f'''
{versus('Inference in first order logic', ['', 'Propositionalisation', 'Forward chaining', 'Backward chaining (Prolog)', 'Resolution'], [
    ['Works on', 'Any FOL KB', 'Definite clauses', 'Definite clauses', 'Any FOL KB in CNF'],
    ['Complete', 'Yes, with growing term depth', 'Yes', 'No with plain depth first search (loops), yes with tabling', 'Yes, refutation complete'],
    ['Main cost', 'k<sup>v</sup> copies of every rule', 'Matching premises to facts', 'Repeated subgoals', 'Many useless resolvents'],
    ['Best for', 'Small finite domains', 'Databases, rule engines, Datalog', 'Answering queries, logic programming', 'Mathematics, software verification']],
    'use forward chaining when facts stream in and many conclusions are wanted, backward chaining for one query at a time, and resolution when the knowledge is not in definite clause form.')}
{scene('Proving theorems with computers', '<p>In 1996 the resolution style prover EQP proved the Robbins conjecture, an open question in algebra for over 60 years. Amazon uses automated reasoning to check access policies in its cloud, and chip companies prove properties of floating point units with first order and higher order provers.</p>')}
''', kw=['comparison', 'Robbins conjecture', 'EQP', 'automated reasoning'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A rule with variables is a pattern. Unification is the matching step: it finds which values for the variables make the rule fit the facts you have.</p>',
    '<p>UI and EI reduce FOL to propositional logic but blow up. Unification and GMP lift inference instead. Forward chaining, backward chaining (Prolog) and resolution (with CNF and Skolemisation) are the three main methods. First order entailment is semidecidable.</p>',
    '<p>Unification can be done in linear time (Paterson and Wegman, 1978). Herbrand\'s theorem underlies propositionalisation. Resolution with a fair strategy is refutation complete. Datalog with stratified negation is the basis of deductive databases.</p>',
    '<p>Research continues on superposition calculi for equality, SMT solving that mixes theories, higher order unification (undecidable in general), and machine learned premise selection for large libraries of mathematics such as the Lean mathlib.</p>')}
''', kw=['linear unification', 'superposition', 'SMT', 'higher order unification', 'premise selection'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Universal and existential instantiation turn FOL into propositional logic, but rules get k<sup>v</sup> copies and functions make it infinite. FOL entailment is semidecidable.',
    'Unification finds the most general θ that makes two atoms equal, with the occurs check. Standardise variables apart first.',
    'Generalised Modus Ponens applies a rule through unification. Forward chaining proves Criminal(West) in 2 rounds.',
    'Backward chaining (Prolog) works from the goal, depth first and left to right. It is fast but can loop.',
    'Resolution needs CNF with Skolem functions, and is refutation complete. The crime proof takes 9 resolution steps.'],
    'step 8 uses logic to plan: situation calculus, STRIPS and partial order planning.')}
{nbcard('fol-inference', 'Run unification on the textbook pairs and forward chaining on the crime example, then write subst, unify and a forward chainer yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'UNIFY(Knows(John, x), Knows(John, Jane)) is', ['{John/Jane}', '{x/Jane}', 'fail', '{x/John}'], 1,
       'Bind the variable.', 'x is the only variable.')
K.quiz('e', 'Existential instantiation replaces the variable with', ['any constant already used', 'a brand new constant', 'a variable', 'True'], 1,
       'Skolem constant.', 'A new name that appears nowhere else.')
K.quiz('e', 'In the crime example, how many rounds does forward chaining need?', ['1', '2', '3', '4'], 1,
       'Weapon, Sells, Hostile first.', 'Round 1 adds three facts, round 2 adds Criminal(West).')
K.quiz('e', 'Prolog uses', ['forward chaining', 'backward chaining, depth first', 'resolution with set of support', 'model checking'], 1,
       'Goal driven.', 'Depth first, left to right.')
K.quiz('m', 'UNIFY(Knows(John, x), Knows(x, Elizabeth)) fails because', ['different predicates', 'x would need to be both John and Elizabeth', 'Elizabeth is a variable', 'of the occurs check'], 1,
       'One x, two values.', 'Standardising apart fixes it.')
K.quiz('m', 'The occurs check stops', ['unifying two constants', 'binding a variable to a term that contains it, such as x with F(x)', 'unifying two variables', 'all bindings'], 1,
       'Endless terms.', 'x = F(x) has no finite solution.')
K.quiz('m', 'In Skolemisation, ∀x ∃y Loves(x, y) becomes', ['∀x Loves(x, A)', '∀x Loves(x, F(x))', 'Loves(A, B)', '∃y Loves(y, y)'], 1,
       'y depends on x.', 'The Skolem term must be a function of the ∀ variable.')
K.quiz('m', 'Datalog is', ['FOL with equality', 'first order definite clauses without function symbols', 'Prolog with negation', 'propositional logic'], 1,
       'No functions.', 'So forward chaining always stops.')
K.quiz('h', 'Why can Prolog loop on path(X, Z) :- path(X, Y), link(Y, Z)?', ['It has no occurs check', 'Depth first search calls path again with no progress before using link', 'It uses breadth first search', 'path is not a definite clause'], 1,
       'Left recursion.', 'Putting link(X, Y) first makes each call consume a link.')
K.quiz('h', 'First order entailment is semidecidable. This means', ['nothing can be proved', 'if KB ⊨ α a complete method finds a proof, but if not it may run for ever', 'it is decidable for Horn clauses only', 'proofs are always short'], 1,
       'Gödel and Turing.', 'Yes answers come, no answers may not.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: UNIFY(P(x, G(x)), P(F(y), y)) is', ['{x/F(y), y/G(x)}', 'fail, because of the occurs check', '{x/y}', '{y/F(x)}'], 1,
       'Follow the bindings.', 'x/F(y), then y must unify with G(F(y)), which contains y.')
K.quiz('x', 'In the style of an MIT 6.034 exam: which resolution strategy keeps every step connected to the negated query?', ['unit preference', 'set of support', 'subsumption', 'factoring'], 1,
       'Goal directed.', 'Each resolution uses a clause from ¬α or one derived from it.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A rule with 2 variables, a KB with 3 constants. How many ground instances by UI?', '9', 'k<sup>v</sup>.',
       ['3 choices for the first variable.', '3 for the second.', eq('3² = 9')], check=9)
K.calc('e', 'The crime law has 3 variables and the KB has 4 constants. How many ground instances?', '64', '4³.',
       ['West, M1, Nono, America: k = 4.', 'x, y, z: v = 3.', eq('4³ = 64 instances, only 1 of them is useful')], check=64)
K.calc('e', 'How many bindings are in UNIFY(Knows(John, x), Knows(y, Bill))?', '2', 'One per variable.',
       ['y/John.', 'x/Bill.', eq('2 bindings')], check=2)
K.calc('m', 'Ground terms up to depth 3 with one constant A and one unary function F.', '4', 'A, F(A), F(F(A)), F(F(F(A))).',
       ['Depth 0: A. Depth 1: F(A).', 'Depth 2: F(F(A)). Depth 3: F(F(F(A))).', eq('4 terms')], check=4)
K.calc('m', 'Ground terms with 2 constants A, B and one binary function G, with depth at most 1.', '6', 'c + c².',
       ['Depth 0: A, B.', 'Depth 1: G(A, A), G(A, B), G(B, A), G(B, B).', eq('2 + 4 = 6')], check=6)
K.calc('m', 'How many facts are known after forward chaining ends on the crime example (start with 4)?', '8', '4 at the start, 3 in round 1, 1 in round 2.',
       ['Start: American(West), Missile(M1), Owns(Nono, M1), Enemy(Nono, America).', 'Round 1: Weapon(M1), Sells(West, M1, Nono), Hostile(Nono). Round 2: Criminal(West).', eq('4 + 3 + 1 = 8')], check=8)
K.calc('h', 'The resolution proof of Criminal(West) uses how many resolution steps?', '9', 'One step per premise solved, plus the subgoals.',
       ['Steps 1 to 4: the law, American, Weapon rule, Missile.', 'Steps 5 to 7: Sells rule, Missile, Owns. Steps 8 and 9: Hostile rule, Enemy.', eq('9 steps')], check=9)
K.calc('h', 'Unification with the occurs check scans the term each time a variable is bound. Two terms of size 50 with 10 bindings: at most how many term nodes are scanned for occurs checks?', '500', 'Up to the term size per binding.',
       ['Each check scans at most 50 nodes.', '10 bindings.', eq('10 × 50 = 500, which grows like n² for bigger terms')], check=500)
K.calc('h', 'Propositionalising a KB with 10 constants and a rule with 4 variables. How many ground rules?', '10000', '10⁴.',
       ['k = 10, v = 4.', '10 × 10 × 10 × 10.', eq('10,000 ground copies of one rule')], check=10000)
K.calc('x', 'In the style of a Stanford CS221 problem: how many Skolem functions or constants does CNF conversion of ∀x ∃y ∀z ∃w R(x, y, z, w) introduce, and how many arguments does the one for w take?', '2', 'One per ∃ variable. w is inside ∀x and ∀z.',
       ['y becomes F(x): it depends on x only.', 'w becomes G(x, z): it depends on x and z.', eq('2 Skolem functions, and G takes 2 arguments')], check=2)

# ---------------------------------------------------------------- assignments
TERMS = '''
# A variable is a string that starts with a lower case letter. A constant starts with a capital.
# A compound term or atom is a tuple: ("Knows", "John", "x") means Knows(John, x).
def is_var(t):
    return type(t) == str and t[0].islower()
'''
K.assign('subst', 'e', 'Apply a substitution',
         '<p>Write <code>subst(theta, t)</code>: replace every variable in t that is bound in theta, following chains of bindings (if x is bound to y and y to John, x becomes John).</p>',
         TERMS + '''
def subst(theta, t):
    # your code here
    pass
''', [("subst({'x': 'Jane'}, ('Knows', 'John', 'x'))", ('Knows', 'John', 'Jane')),
      ("subst({'y': 'John', 'x': ('Mother', 'y')}, ('Knows', 'y', 'x'))", ('Knows', 'John', ('Mother', 'John'))),
      ("subst({}, 'x')", 'x'),
      ("subst({'x': 'y', 'y': 'A'}, ('P', 'x'))", ('P', 'A'))],
         TERMS + '''
def subst(theta, t):
    if is_var(t) and t in theta:
        return subst(theta, theta[t])
    if type(t) == tuple:
        parts = []
        for a in t:
            parts.append(subst(theta, a))
        return tuple(parts)
    return t
''', 'A bound variable is replaced by subst of its value. A tuple is rebuilt from subst of each part. Anything else stays.', '<p>The second test needs the chain x to Mother(y) to Mother(John).</p>')
K.assign('unify', 'm', 'Unification with the occurs check',
         '<p>Write <code>unify(x, y, theta)</code> as in the textbook. Return the new dictionary of bindings, or None on failure. Use the occurs check. The starter gives is_var.</p>',
         TERMS + '''
def unify(x, y, theta):
    # your code here
    pass
''', [("unify(('Knows', 'John', 'x'), ('Knows', 'John', 'Jane'), {})", {'x': 'Jane'}),
      ("unify(('Knows', 'John', 'x'), ('Knows', 'y', 'Bill'), {})", {'y': 'John', 'x': 'Bill'}),
      ("unify(('Knows', 'John', 'x'), ('Knows', 'x', 'Elizabeth'), {})", None),
      ("unify(('P', 'x'), ('P', ('F', 'x')), {})", None),
      ("unify(('P', 'x', 'x'), ('P', 'A', 'A'), {})", {'x': 'A'})],
         TERMS + '''
def unify(x, y, theta):
    if theta is None:
        return None
    if x == y:
        return theta
    if is_var(x):
        return unify_var(x, y, theta)
    if is_var(y):
        return unify_var(y, x, theta)
    if type(x) == tuple and type(y) == tuple and len(x) == len(y):
        for i in range(len(x)):
            theta = unify(x[i], y[i], theta)
        return theta
    return None

def unify_var(v, t, theta):
    if v in theta:
        return unify(theta[v], t, theta)
    if is_var(t) and t in theta:
        return unify(v, theta[t], theta)
    if occurs(v, t, theta):
        return None
    new = dict(theta)
    new[v] = t
    return new

def occurs(v, t, theta):
    if t == v:
        return True
    if is_var(t) and t in theta:
        return occurs(v, theta[t], theta)
    if type(t) == tuple:
        for a in t:
            if occurs(v, a, theta):
                return True
    return False
''', 'Cases: same term, x is a variable, y is a variable, two tuples of the same length (unify element by element), otherwise fail. In unify_var, follow existing bindings, then do the occurs check, then bind.', '<p>The fourth test needs the occurs check. The last test binds x to A and then checks that the second A agrees.</p>')
K.assign('fcask', 'h', 'Forward chaining with variables',
         '<p>Write <code>fc_ask(facts, rules, query)</code>. facts is a list of ground atoms as tuples. rules is a list of <code>(premises, head)</code> pairs whose atoms may contain variables. Facts and query have no variables. Repeat rounds of forward chaining until the query is known (return True) or a round adds nothing (return False).</p>',
         TERMS + '''
def fc_ask(facts, rules, query):
    # your code here
    pass
''', [("fc_ask([('American', 'West'), ('Missile', 'M1'), ('Owns', 'Nono', 'M1'), ('Enemy', 'Nono', 'America')], "
       "[([('Missile', 'x')], ('Weapon', 'x')), ([('Missile', 'x'), ('Owns', 'Nono', 'x')], ('Sells', 'West', 'x', 'Nono')), "
       "([('Enemy', 'x', 'America')], ('Hostile', 'x')), "
       "([('American', 'x'), ('Weapon', 'y'), ('Sells', 'x', 'y', 'z'), ('Hostile', 'z')], ('Criminal', 'x'))], ('Criminal', 'West'))", True),
      ("fc_ask([('American', 'West'), ('Missile', 'M1')], [([('Missile', 'x')], ('Weapon', 'x'))], ('Criminal', 'West'))", False),
      ("fc_ask([('Parent', 'A', 'B'), ('Parent', 'B', 'C')], [([('Parent', 'x', 'y'), ('Parent', 'y', 'z')], ('Grandparent', 'x', 'z'))], ('Grandparent', 'A', 'C'))", True),
      ("fc_ask([('Parent', 'A', 'B'), ('Parent', 'B', 'C')], [([('Parent', 'x', 'y'), ('Parent', 'y', 'z')], ('Grandparent', 'x', 'z'))], ('Grandparent', 'B', 'C'))", False)],
         TERMS + '''
def match(pattern, fact, theta):
    if len(pattern) != len(fact) or pattern[0] != fact[0]:
        return None
    theta = dict(theta)
    for i in range(1, len(pattern)):
        p = pattern[i]
        f = fact[i]
        if is_var(p):
            if p in theta and theta[p] != f:
                return None
            theta[p] = f
        elif p != f:
            return None
    return theta

def all_matches(premises, facts, theta):
    if len(premises) == 0:
        return [theta]
    out = []
    for f in facts:
        t = match(premises[0], f, theta)
        if t is not None:
            out = out + all_matches(premises[1:], facts, t)
    return out

def fc_ask(facts, rules, query):
    facts = list(facts)
    if query in facts:
        return True
    while True:
        new = []
        for premises, head in rules:
            for theta in all_matches(premises, facts, {}):
                parts = [head[0]]
                for a in head[1:]:
                    parts.append(theta.get(a, a))
                fact = tuple(parts)
                if fact not in facts and fact not in new:
                    new.append(fact)
        if len(new) == 0:
            return False
        facts = facts + new
        if query in facts:
            return True
''', 'Write match(pattern, fact, theta) for one premise against one ground fact. all_matches tries the premises left to right, carrying theta. Each round, add every new head, then check the query.', '<p>Test 1 is the crime example: two rounds. Test 4 asks for a grandparent link that does not exist.</p>')

K.must('UI and EI', 'UI: any ground term, many times. EI: new Skolem constant, once. Propositionalisation: k<sup>v</sup> copies. Semidecidable.')
K.must('Unify', '{x/Jane}, {y/John, x/Bill}, {y/John, x/Mother(John)}, fail for Knows(x, Elizabeth). Occurs check. Standardise apart. MGU.')
K.must('GMP and FC', 'Generalised Modus Ponens with θ. Crime: round 1 Weapon, Sells, Hostile, round 2 Criminal(West). Datalog stops.')
K.must('BC', 'Goal driven, depth first, left to right (Prolog). Left recursion loops. Negation as failure.')
K.must('FOL resolution', 'CNF: remove ⇒, ¬ in, standardise, Skolemise (∃y inside ∀x gives F(x)), drop ∀, distribute. Refutation complete.')

T = K.topic(
    slug='fol-inference', topic='fol-inference', step=(7, 'Logic and knowledge', 'cai-logic', 'Agents that know facts and reason with them: propositional logic, inference rules, resolution, chaining, first order logic and unification.', 'College'),
    title='Inference in first order logic: unification, chaining and resolution', short='FOL inference', badge='7.4', minutes=60,
    lead='Reason with rules that have variables. Reduce first order logic to propositional logic and see why that blows up, then lift inference with unification, prove that Colonel West is a criminal by forward chaining, backward chaining and resolution, and meet Prolog.',
    desc='Universal and existential instantiation, propositionalisation and Herbrand, semidecidability, unification with the occurs check, standardising apart and the most general unifier, Generalised Modus Ponens, forward chaining on the crime example, Datalog and Rete, backward chaining and Prolog, CNF with Skolemisation, first order resolution and its strategies.',
    summary='Instantiation, unification, GMP, forward and backward chaining, and resolution in FOL.',
    keywords=['unification', 'generalised modus ponens', 'forward chaining', 'backward chaining', 'Prolog', 'resolution', 'Skolemisation', 'crime example', 'Datalog'],
    recap='<p>Unification lifts inference rules to FOL. Forward and backward chaining handle definite clauses, resolution handles everything.</p>',
    nb={'unify': 'Unification on the textbook pairs', 'fcfol': 'Forward chaining on the crime example'})
