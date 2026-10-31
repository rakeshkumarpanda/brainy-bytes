# Chapter 1.1: decision problems and preference relations. Source: lecture 1 (the decision problem A, X, c and the
# preference relation, weak and strict preference, indifference, the A > B ~ C example, incomplete and cyclic
# preferences, completeness and transitivity, the homework on whether properties pass from weak preference to strict
# preference and indifference, equality against indifference, incompleteness against indifference).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('relation', r'''
# A preference relation is a set of ordered pairs (x, y) meaning "x is at least as good as y"
X = ["A", "B", "C"]
weak = {("A", "A"), ("B", "B"), ("C", "C"), ("A", "B"), ("A", "C"), ("B", "C"), ("C", "B")}

strict = {(x, y) for (x, y) in weak if (y, x) not in weak}
indiff = {(x, y) for (x, y) in weak if (y, x) in weak}

complete = all((x, y) in weak or (y, x) in weak for x in X for y in X)
transitive = all((x, z) in weak for (x, y) in weak for (y2, z) in weak if y == y2)

print("strict  :", sorted(strict))
print("indiff  :", sorted(indiff))
print("complete:", complete, " transitive:", transitive)
''')

K.code('cycle', r'''
# A money pump: an agent with the cycle A > B > C > A pays 1 coin for every swap it likes
better = {("A", "B"), ("B", "C"), ("C", "A")}     # (x, y) means x is strictly better than y
holding, coins = "A", 10
offer = {"A": "C", "B": "A", "C": "B"}            # always offer the item the agent prefers to what it holds
for trade in range(6):
    new = offer[holding]
    if (new, holding) in better:
        holding, coins = new, coins - 1
        print("swap to", new, " coins left:", coins)
print("after 6 swaps the agent holds", holding, "again and has lost", 10 - coins, "coins")
''')

K.lesson('problem', 'What a decision problem is', f'''
<p>Every day you choose. Which bus to take, which film to watch, which job offer to accept. The first lecture of the course turns this everyday act into mathematics so that a computer can do it too. A decision problem has three parts.</p>
{fxs(
    fx('A decision problem', '( <i>A</i>, <i>X</i>, <i>c</i>, ⪰ )', 'A is the set of actions you can take. X is the set of outcomes that can happen. c is the map that says which outcome each action leads to. ⪰ is your preference over outcomes.', key=True),
    fx('The consequence map', '<i>c</i> : <i>A</i> → <i>X</i>', 'With certainty, each action leads to exactly one outcome. Later chapters let an action lead to a lottery over outcomes.'),
    fx('Action value', '<i>v</i>(<i>a</i>) = <i>u</i>( <i>c</i>(<i>a</i>) )', 'We like outcomes, not actions. An action is worth whatever its outcome is worth.'))}
{table(['Part', 'Everyday example', 'AI example'], [
    ['Actions A', 'Go to INOX or go to PVR', 'Move left, right, up or down'],
    ['Outcomes X', 'The film you end up watching', 'The square the robot reaches'],
    ['Consequence c', 'INOX shows Aliens', 'Moving right from (1, 1) reaches (2, 1)'],
    ['Preference ⪰', 'Aliens is better than Casablanca', 'The charging dock is better than the stairs']])}
<p>The professor stressed one distinction. An action is something you choose. An outcome is something you receive. Utility is given to outcomes, and the value of an action is borrowed from the outcome it leads to.</p>
{scene('a delivery robot', '<p>A warehouse robot can take the lift, take the ramp or wait. The lift reaches the shelf in 40 seconds, the ramp in 70 seconds, and waiting reaches nothing. Write A = {{lift, ramp, wait}}, X = {{shelf in 40 s, shelf in 70 s, no delivery}}, and c(lift) = shelf in 40 s. Once the robot can rank the three outcomes, picking an action is a lookup.</p>')}
''', kw=['decision problem', 'actions', 'outcomes', 'consequence function', 'action value', 'rational agent'])

K.lesson('relations', 'Weak preference, strict preference and indifference', f'''
<p>A preference relation compares two outcomes at a time. The basic building block is weak preference: x ⪰ y means "x is at least as good as y". Everything else is built from it.</p>
{fxs(
    fx('Weak preference', '<i>x</i> ⪰ <i>y</i>', 'x is at least as good as y. It allows a tie.', key=True),
    fx('Strict preference', '<i>x</i> ≻ <i>y</i> ⟺ <i>x</i> ⪰ <i>y</i> and not <i>y</i> ⪰ <i>x</i>', 'x is better and the reverse does not hold.', key=True),
    fx('Indifference', '<i>x</i> ∼ <i>y</i> ⟺ <i>x</i> ⪰ <i>y</i> and <i>y</i> ⪰ <i>x</i>', 'Both directions hold, so the two are equally good.', key=True))}
<p>Mathematically a relation is just a set of ordered pairs. For X = {{A, B, C}} with A ≻ B, A ≻ C and B ∼ C the lecture writes the sets out in full.</p>
{table(['Relation', 'Pairs it contains'], [
    ['⪰ weak', '(A, A), (B, B), (C, C), (A, B), (A, C), (B, C), (C, B)'],
    ['≻ strict', '(A, B), (A, C)'],
    ['∼ indifference', '(A, A), (B, B), (C, C), (B, C), (C, B)']])}
{viz('prefmatrix')}
{code('relation')}
{steps('Worked example from the lecture: A ≻ B ∼ C ≻ D', [
    'Start with the reflexive pairs, since every outcome is at least as good as itself: (A, A), (B, B), (C, C), (D, D).',
    'A beats everything below it: (A, B), (A, C), (A, D).',
    'B and C both beat D: (B, D), (C, D).',
    'B and C tie, so both directions go in: (B, C), (C, B).',
    eq('|⪰| = 4 + 3 + 2 + 2 = 11 pairs'),
    'Strict pairs are those whose reverse is missing: (A, B), (A, C), (A, D), (B, D), (C, D), so 5. Indifference pairs are the 4 reflexive ones plus (B, C) and (C, B), so 6.'])}
{note('Equality and indifference are different ideas. Equality means two things are the same object. Indifference means two different outcomes are judged equally good. Tea and coffee are not equal, but you may be indifferent between them.', 'warn')}
''', kw=['weak preference', 'strict preference', 'indifference', 'relation', 'ordered pairs', 'reflexive'])

K.lesson('rational', 'Completeness and transitivity', f'''
<p>Not every set of pairs is a sensible preference. The course calls a preference rational when it has two properties.</p>
{fxs(
    fx('Completeness', 'for all <i>x</i>, <i>y</i> ∈ <i>X</i>: &nbsp; <i>x</i> ⪰ <i>y</i> or <i>y</i> ⪰ <i>x</i>', 'You can always compare. You may say better, worse or equally good, but you may not leave a pair unanswered.', key=True),
    fx('Transitivity', '<i>x</i> ⪰ <i>y</i> and <i>y</i> ⪰ <i>z</i> ⟹ <i>x</i> ⪰ <i>z</i>', 'Rankings chain together without contradiction.', key=True),
    fx('Rational preference', 'rational = complete + transitive', 'A rational agent has such a preference and picks an action whose outcome it likes most.'))}
<h3>When completeness fails</h3>
<p>Picture two cars. One is cheaper, less powerful and more reliable. The other is dearer, more powerful and less reliable. If you have no way to trade price against power against reliability, you cannot rank them. That is incompleteness, and it is not the same as indifference. Indifference says "they are equally good". Incompleteness says "I cannot say".</p>
<h3>When transitivity fails</h3>
<p>Suppose A ≻ B, B ≻ C and C ≻ A. Nothing can be called best, since each outcome loses to another. Worse, someone can exploit you. They sell you B for A plus a coin, then C for B plus a coin, then A for C plus a coin. You end up holding A again with three coins fewer. This is called a money pump.</p>
{code('cycle')}
{steps('Homework 1: if ⪰ is transitive, is ≻ transitive?', [
    'Assume x ≻ y and y ≻ z. Then x ⪰ y and y ⪰ z, so transitivity of ⪰ gives x ⪰ z.',
    'We still need "not z ⪰ x". Suppose instead that z ⪰ x.',
    'From z ⪰ x and x ⪰ y transitivity gives z ⪰ y.',
    'But y ≻ z says z ⪰ y is false. That is a contradiction.',
    eq('So x ≻ z, and strict preference is transitive.')])}
{steps('Homework 2: if ⪰ is transitive, is ∼ transitive?', [
    'Assume x ∼ y and y ∼ z. That gives four facts: x ⪰ y, y ⪰ x, y ⪰ z, z ⪰ y.',
    'Chain x ⪰ y and y ⪰ z to get x ⪰ z.',
    'Chain z ⪰ y and y ⪰ x to get z ⪰ x.',
    eq('Both directions hold, so x ∼ z.')])}
{table(['Does it carry over from ⪰?', 'To ≻', 'To ∼'], [
    ['Transitivity', 'Yes, proof above', 'Yes, proof above'],
    ['Completeness', 'No. If x ∼ y then neither x ≻ y nor y ≻ x', 'No. If x ≻ y then x ∼ y is false and so is y ∼ x'],
    ['Reflexivity', 'No. x ≻ x never holds', 'Yes. x ⪰ x in both directions']])}
{deep('Why completeness implies reflexivity', '<p>Completeness says that for every pair x, y at least one of x ⪰ y or y ⪰ x holds. Nothing stops us from choosing y = x. Then the statement reads "x ⪰ x or x ⪰ x", so x ⪰ x. A complete relation is therefore always reflexive. This is why every rational weak preference contains the diagonal pairs (A, A), (B, B) and so on.</p>')}
{ladder(
    '<p>To choose well you must be able to compare any two options, and your comparisons must not go round in a circle.</p>',
    '<p>A preference is a set of ordered pairs. Strict preference and indifference are built from weak preference. A rational preference is complete and transitive. Transitivity of ⪰ passes to ≻ and to ∼, but completeness does not.</p>',
    '<p>A complete and transitive relation is a total preorder. Its indifference classes are equivalence classes, and ≻ orders those classes strictly. Dropping completeness gives a partial preorder, which is the starting point of multi criteria decision making and Pareto analysis.</p>',
    '<p>Experiments by Tversky (1969) found intransitive choices in people when options differ slightly on several attributes. Research on regret theory, context dependent preferences and incomplete preference models (Aumann 1962, Bewley 1986) asks how much of rational choice survives once these axioms are weakened.</p>')}
''', kw=['completeness', 'transitivity', 'rational preference', 'money pump', 'cycle', 'incomplete preference', 'homework', 'total preorder'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In a decision problem (A, X, c, ⪰), what does c do?', ['Ranks the outcomes', 'Maps each action to its outcome', 'Lists the actions', 'Measures cost in money'], 1,
       'c stands for consequence.', 'c : A → X tells you which outcome each action produces.')
K.quiz('e', 'What does x ⪰ y mean?', ['x is strictly better than y', 'x is at least as good as y', 'x equals y', 'x cannot be compared with y'], 1,
       'The bar under the symbol allows a tie.', 'Weak preference allows x to be better than or equally good as y.')
K.quiz('e', 'Which two properties make a preference rational in this course?', ['Completeness and transitivity', 'Symmetry and transitivity', 'Continuity and convexity', 'Reflexivity and symmetry'], 0,
       'One is about comparing, one about chaining.', 'Rational preference = complete + transitive.')
K.quiz('e', 'Utility is assigned to', ['Actions', 'Outcomes', 'Agents', 'Probabilities'], 1,
       'You enjoy what you receive.', 'Utility is given to outcomes, and an action is valued through its outcome: v(a) = u(c(a)).')
K.quiz('m', 'You cannot rank two cars that differ in price, power and reliability. Which property fails?', ['Transitivity', 'Completeness', 'Reflexivity', 'None, this is indifference'], 1,
       'Can you compare them at all?', 'No comparison in either direction is incompleteness. Indifference would mean you judge them equal.')
K.quiz('m', 'A ≻ B, B ≻ C and C ≻ A. What is wrong?', ['It is incomplete', 'It is not transitive', 'Nothing', 'It is not reflexive'], 1,
       'Chain the first two.', 'Transitivity would force A ≻ C, but the agent says C ≻ A. The cycle has no best element.')
K.quiz('m', 'If ⪰ is complete, must ≻ be complete?', ['Yes', 'No, a tie x ∼ y gives neither x ≻ y nor y ≻ x', 'Only for finite X', 'Only when ⪰ is transitive'], 1,
       'Think about a tie.', 'Ties are compared by ⪰ but by neither direction of ≻.')
K.quiz('m', 'If ⪰ is transitive, is ∼ transitive?', ['Yes', 'No', 'Only for three outcomes', 'Only if ⪰ is complete'], 0,
       'Chain both directions.', 'x ∼ y and y ∼ z give x ⪰ z and z ⪰ x, so x ∼ z.')
K.quiz('h', 'For X = {A, B, C, D} with A ≻ B ∼ C ≻ D, how many pairs are in ⪰?', ['8', '10', '11', '16'], 2,
       'Reflexive pairs, pairs from A, pairs to D, and the tie.', '4 reflexive + 3 from A + 2 to D + 2 for the tie = 11.')
K.quiz('h', 'Why does every complete relation contain (x, x) for all x?', ['By definition of a set', 'Completeness with y = x gives x ⪰ x', 'Because of transitivity', 'It does not have to'], 1,
       'Apply completeness to one outcome.', 'Choosing y = x in "x ⪰ y or y ⪰ x" gives x ⪰ x.')
K.quiz('h', 'An agent with a preference cycle can be exploited by', ['A money pump', 'A lottery', 'A discount factor', 'A mixed strategy'], 0,
       'Trading in circles.', 'Each swap looks like an improvement, yet the agent ends where it started having paid every time.')
K.quiz('x', 'A complete and transitive relation is called', ['A total preorder', 'An equivalence relation', 'A strict partial order', 'A lattice'], 0,
       'It can have ties.', 'It is total (complete) and a preorder (reflexive and transitive). The ties form equivalence classes.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'X = {A, B, C} with A ≻ B, A ≻ C and B ∼ C. How many pairs are in the weak relation ⪰?', '7', 'Reflexive pairs, plus A over each, plus the tie both ways.',
       ['Reflexive pairs: (A, A), (B, B), (C, C), so 3.', 'A over B and A over C, so 2.', 'B ∼ C gives (B, C) and (C, B), so 2.', eq('|⪰| = 3 + 2 + 2 = 7')], check=7)
K.calc('e', 'For the same example, how many pairs are in the strict relation ≻?', '2', 'Keep only the pairs whose reverse is missing.',
       ['Reflexive pairs have their reverse (themselves), so drop them.', '(B, C) and (C, B) reverse each other, so drop them.', eq('≻ = {(A, B), (A, C)}, so 2 pairs')], check=2)
K.calc('e', 'X has 4 outcomes. How many unordered pairs must a complete preference compare, not counting an outcome with itself?', '6', 'Choose 2 from 4.',
       ['Each pair of different outcomes needs an answer.', 'The number of such pairs is C(4, 2).', eq('C(4, 2) = 4 × 3 ÷ 2 = 6')], check=6)
K.calc('m', 'For A ≻ B ∼ C ≻ D, how many pairs are in ∼?', '6', 'Reflexive pairs plus the tie.',
       ['Reflexive pairs: 4.', 'B ∼ C gives (B, C) and (C, B).', eq('|∼| = 4 + 2 = 6')], check=6)
K.calc('m', 'A complete relation on n outcomes contains at least how many ordered pairs? Find it for n = 5.', '15', 'Reflexive pairs plus at least one direction of every other pair.',
       ['Each outcome is compared with itself: n pairs.', 'Each unordered pair of different outcomes needs at least one direction: n(n − 1)/2 pairs.', 'For n = 5: 5 + 10.', eq('minimum |⪰| = 15')], check=15)
K.calc('m', 'A strict ranking of 5 outcomes with no ties contains how many pairs in ⪰?', '15', 'No ties means each unordered pair appears once.',
       ['Reflexive pairs: 5.', 'Every unordered pair appears in exactly one direction: C(5, 2) = 10.', eq('|⪰| = 5 + 10 = 15')], check=15)
K.calc('m', 'If all 5 outcomes are tied, how many pairs are in ⪰?', '25', 'Every ordered pair is in.',
       ['Every outcome is at least as good as every other.', 'So every ordered pair (x, y) belongs to ⪰.', eq('|⪰| = 5 × 5 = 25')], check=25)
K.calc('h', 'An agent with the cycle A ≻ B ≻ C ≻ A pays 2 coins per swap. How many coins are lost after 3 full trips round the cycle?', '18', 'One trip is 3 swaps.',
       ['One trip round the cycle: 3 swaps.', 'Three trips: 9 swaps.', eq('loss = 9 × 2 = 18 coins'), 'The agent holds the same item it started with.'], check=18)
K.calc('h', 'How many of the 2⁴ = 16 possible relations on X = {A, B} are complete?', '3', 'Reflexive pairs must be in, and at least one of (A, B), (B, A).',
       ['(A, A) and (B, B) must be in, which fixes 2 of the 4 pairs.', 'Of (A, B) and (B, A), at least one must be in: 3 choices out of 4.', eq('3 complete relations: A ≻ B, B ≻ A, A ∼ B')], check=3)
K.calc('h', 'A preference on n = 4 outcomes is a strict ranking. How many strict pairs does ≻ contain?', '6', 'Every unordered pair of different outcomes is strict.',
       ['No ties, so every pair of different outcomes is strictly ranked.', 'Each unordered pair gives exactly one strict ordered pair.', eq('|≻| = C(4, 2) = 6')], check=6)
K.calc('x', 'How many complete and transitive relations (weak orders) exist on 3 outcomes?', '13', 'Count rankings with ties by how many tied groups there are.',
       ['3 groups, all strict: 3! = 6.', '2 groups: choose which pair ties (3 ways) and whether the pair is on top or bottom (2 ways), so 6.', '1 group, all tied: 1.', eq('6 + 6 + 1 = 13 weak orders'), 'These are the ordered Bell (Fubini) numbers 1, 3, 13, 75, 541.'], check=13)

# ---------------------------------------------------------------- assignments
K.assign('props', 'e', 'Check a preference relation',
         '<p>Write <code>is_rational(X, weak)</code>. X is a list of outcomes and weak is a set of pairs (x, y) meaning x ⪰ y. Return True only if the relation is complete and transitive.</p>',
         '''
def is_rational(X, weak):
    # your code here
    pass
''', [("is_rational(['A', 'B', 'C'], {('A','A'),('B','B'),('C','C'),('A','B'),('A','C'),('B','C'),('C','B')})", True),
      ("is_rational(['A', 'B'], {('A','A'),('B','B')})", False),
      ("is_rational(['A', 'B', 'C'], {('A','A'),('B','B'),('C','C'),('A','B'),('B','C'),('C','A')})", False)],
         '''
def is_rational(X, weak):
    complete = all((x, y) in weak or (y, x) in weak for x in X for y in X)
    transitive = all((x, z) in weak for (x, y) in weak for (y2, z) in weak if y == y2)
    return complete and transitive
''', 'Completeness checks every pair of X. Transitivity checks every chain (x, y), (y, z).',
         '<p>The second relation leaves A and B unranked, so it is incomplete. The third is the cycle from the lecture.</p>')
K.assign('split', 'm', 'Split weak preference into strict and indifferent',
         '<p>Write <code>split(weak)</code> that returns a pair (number of strict pairs, number of indifference pairs) for the weak relation given as a set of pairs.</p>',
         '''
def split(weak):
    # your code here
    pass
''', [("split({('A','A'),('B','B'),('C','C'),('A','B'),('A','C'),('B','C'),('C','B')})", [2, 5]),
      ("split({('A','A'),('B','B'),('C','C'),('D','D'),('A','B'),('A','C'),('A','D'),('B','D'),('C','D'),('B','C'),('C','B')})", [5, 6])],
         '''
def split(weak):
    strict = [p for p in weak if (p[1], p[0]) not in weak]
    indiff = [p for p in weak if (p[1], p[0]) in weak]
    return [len(strict), len(indiff)]
''', 'A pair is strict when its reverse is not in the set, and indifferent when it is.',
         '<p>These are the two examples from lecture 1: A ≻ B ∼ C and A ≻ B ∼ C ≻ D.</p>')

K.must('Decision problem', '(A, X, c, ⪰): actions, outcomes, consequence map c : A → X, preference. Utility goes on outcomes, v(a) = u(c(a)).')
K.must('Three relations', 'Weak x ⪰ y. Strict x ≻ y means x ⪰ y and not y ⪰ x. Indifference x ∼ y means both directions.')
K.must('Rationality', 'Complete (every pair compared) plus transitive (rankings chain). Cycles have no best element and allow a money pump.')
K.must('What carries over', 'Transitivity of ⪰ passes to ≻ and ∼. Completeness does not pass to either.')
K.must('Indifference is not incompleteness', 'Indifferent: equally good. Incomplete: cannot compare. Equality: the same object.')

T = K.topic(
    slug='decision-problems', topic='decision-problems', step=(1, 'Rational choice', 'aai-choice', 'Turn choice into mathematics: preferences, utility functions and picking the best action when outcomes are certain.', 'School and college'),
    title='Decision problems and preferences', short='Preferences', badge='1.1', minutes=40,
    lead='Write any choice as actions, outcomes and a preference, learn the three preference relations, and see why rational preferences must be complete and transitive.',
    desc='The decision problem (A, X, c, ⪰), weak and strict preference, indifference written as sets of pairs, incomplete and cyclic preferences, completeness and transitivity, the money pump, and the lecture 1 homework proofs.',
    summary='Decision problems, the three preference relations, completeness, transitivity, cycles and what carries over from weak to strict preference.',
    keywords=['decision problem', 'preference relation', 'weak preference', 'strict preference', 'indifference', 'completeness', 'transitivity', 'rationality'],
    recap='<p>A decision problem lists actions, outcomes, the map between them and a preference. A rational preference can compare any two outcomes and never goes round in a circle.</p>')
