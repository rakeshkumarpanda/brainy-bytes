# Chapter 1.2: utility functions. Source: lecture 1 (utility as a real number per outcome, representation
# x ⪰ y iff u(x) >= u(y), the OCR note on equality, ordinal against cardinal utility, increasing transformations,
# utility is not money, existence for finite X with complete and transitive preferences, the construction proof by
# top ranked classes, why a best outcome exists, ties at the top, n! strict rankings and the 20! remark).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('construct', r'''
# Build a utility function from a ranking by peeling off the best class again and again
weak = {("A","A"),("B","B"),("C","C"),("D","D"),
        ("A","B"),("A","C"),("A","D"),("B","D"),("C","D"),("B","C"),("C","B")}
left = ["A", "B", "C", "D"]
classes = []
while left:
    top = [x for x in left if all((x, y) in weak for y in left)]   # best among what is left
    classes.append(top)
    left = [x for x in left if x not in top]

u = {}
for level, cls in enumerate(classes):
    for x in cls:
        u[x] = len(classes) - level                 # best class gets the largest number
print("classes from best to worst:", classes)
print("utility:", u)
''')

K.code('transform', r'''
# Any strictly increasing transformation keeps the ranking, so it represents the same preference
import math
u = {"A": 10, "B": 5, "C": 5, "D": 1}
for name, f in [("2u + 7", lambda t: 2 * t + 7), ("u cubed", lambda t: t ** 3),
                ("log u", math.log), ("-u", lambda t: -t)]:
    v = {x: round(f(t), 3) for x, t in u.items()}
    same = all((u[x] >= u[y]) == (v[x] >= v[y]) for x in u for y in u)
    print(name.ljust(7), v, " same ranking:", same)
''')

K.lesson('represent', 'A number for every outcome', f'''
<p>Comparing outcomes two at a time gets tiring once there are many of them. A utility function does the work once: it gives each outcome a single real number so that bigger means better. Then choosing the best outcome is just finding the largest number.</p>
{fxs(
    fx('Utility function', '<i>u</i> : <i>X</i> → ℝ', 'A score for each outcome. It may stand for satisfaction, value, benefit or happiness. It is not money unless the model says so.'),
    fx('Representation', '<i>x</i> ⪰ <i>y</i> ⟺ <i>u</i>(<i>x</i>) ≥ <i>u</i>(<i>y</i>)', 'u represents ⪰ when the order of the numbers is exactly the order of the preference.', key=True),
    fx('The two consequences', '<i>x</i> ≻ <i>y</i> ⟺ <i>u</i>(<i>x</i>) &gt; <i>u</i>(<i>y</i>), &nbsp; <i>x</i> ∼ <i>y</i> ⟺ <i>u</i>(<i>x</i>) = <i>u</i>(<i>y</i>)', 'Strict preference matches a strictly larger number, and a tie matches equal numbers.'))}
{note('The slide transcript once read "u(x) = u(y) ⟺ x ⪰ y". That is a transcription slip. The correct condition for weak preference uses ≥. Equality belongs to indifference only.', 'warn')}
{viz('utilbuild')}
{steps('Lecture example: A ≻ B, A ≻ C, B ∼ C', [
    'We need u(A) larger than both u(B) and u(C), and u(B) = u(C).',
    'One choice: u(A) = 10, u(B) = 5, u(C) = 5.',
    'Another choice: u(A) = 100, u(B) = −10, u(C) = −10.',
    eq('Both satisfy u(A) &gt; u(B) = u(C), so both represent the same preference.')])}
''', kw=['utility function', 'payoff', 'representation', 'real numbers', 'utility is not money'])

K.lesson('ordinal', 'Ordinal and cardinal utility', f'''
<p>If two different sets of numbers represent the same preference, which one is right? For a ranking, both are. Only the order matters, not the size of the gaps. Utility that carries only order is called ordinal.</p>
{fxs(
    fx('Ordinal invariance', 'if <i>f</i> is strictly increasing, &nbsp; <i>v</i>(<i>x</i>) = <i>f</i>( <i>u</i>(<i>x</i>) ) represents the same ⪰', 'Examples: 2u + 7, u³, eᵘ, and log u when u is positive. A decreasing f such as −u reverses the ranking.', key=True),
    fx('Cardinal utility', '<i>u</i>(<i>A</i>) − <i>u</i>(<i>B</i>) compared with <i>u</i>(<i>C</i>) − <i>u</i>(<i>D</i>)', 'Cardinal utility treats the size of a difference as meaningful. It needs more assumptions than ranking alone, and it returns in chapter 2.2 with lotteries.'))}
{code('transform')}
{steps('Proof that an increasing f keeps the ranking', [
    'Assume u represents ⪰ and f is strictly increasing, which means a ≥ b ⟺ f(a) ≥ f(b).',
    'Take any x and y. By representation, x ⪰ y ⟺ u(x) ≥ u(y).',
    'Apply f to both sides. Because f is strictly increasing, u(x) ≥ u(y) ⟺ f(u(x)) ≥ f(u(y)).',
    eq('So x ⪰ y ⟺ v(x) ≥ v(y), and v = f ∘ u represents ⪰.')])}
{table(['Statement about u(A) = 10, u(B) = 5, u(C) = 1', 'Ordinal meaning', 'Cardinal meaning'], [
    ['A is preferred to B', 'Yes, meaningful', 'Yes, meaningful'],
    ['A is twice as good as B', 'Not meaningful', 'Not meaningful either. Ratios change with 2u + 7'],
    ['The step from B to A is bigger than from C to B', 'Not meaningful', 'Meaningful only when u is cardinal']])}
{scene('star ratings', '<p>A film site shows 1 to 5 stars. Saying a 5 star film is better than a 3 star film uses only order. Saying the 5 star film is worth as much as the 3 star film and the 2 star film together treats the stars as cardinal, which the ratings were never designed to support.</p>')}
''', kw=['ordinal utility', 'cardinal utility', 'increasing transformation', 'invariance', 'utility differences'])

K.lesson('existence', 'When does a utility function exist?', f'''
<p>The main theorem of lecture 1 says when a preference can be turned into numbers.</p>
{fxs(fx('Existence theorem', '<i>X</i> finite and ⪰ complete and transitive ⟹ some <i>u</i> : <i>X</i> → ℝ represents ⪰', 'Three conditions: finitely many outcomes, completeness, transitivity.', key=True))}
{steps('Proof by construction, as given in class', [
    'Find the top ranked outcomes, the x with x ⪰ y for every remaining y. Ties at the top all count.',
    'Give every one of them the same number, the largest still unused.',
    'Remove them from the set and repeat with what is left.',
    'Because X is finite, the process stops after at most |X| rounds.',
    eq('A ≻ B ∼ C ≻ D gives classes {A}, {B, C}, {D} and u = 3, 2, 2, 1')])}
{viz('utilbuild', rank='A > B ~ C > D')}
{steps('Why a top ranked outcome always exists', [
    'Suppose no outcome is top ranked. Then every outcome is beaten by some other outcome.',
    'Start at any x₁. Some x₂ ≻ x₁. Some x₃ ≻ x₂. Keep going.',
    'X is finite, so some outcome must appear twice in this chain.',
    'The repeat creates a cycle, and transitivity of ≻ would give that outcome ≻ itself.',
    eq('That is impossible, so a top ranked outcome exists.')])}
{code('construct')}
<h3>What breaks when a condition fails</h3>
{table(['Condition dropped', 'What goes wrong'], [
    ['Transitivity', 'A ≻ B ≻ C ≻ A would need u(A) &gt; u(B) &gt; u(C) &gt; u(A), so u(A) &gt; u(A). Impossible.'],
    ['Completeness', 'Real numbers are always comparable, so any u would rank pairs the agent cannot rank.'],
    ['Finiteness', 'The construction may never end. Lexicographic preference on the plane has no utility at all.']])}
<h3>How many rankings are there?</h3>
<p>With n outcomes and no ties, every ranking is an ordering of n objects, so there are n! of them. Five outcomes give 120 rankings. Twenty outcomes give 20! ≈ 2.43 × 10¹⁸. That is enormous but still finite, and finiteness is what the theorem needs. Allowing ties gives even more rankings.</p>
{viz('orderings')}
{deep('Lexicographic preference: an infinite case with no utility', '<p>Order points (a, b) of the unit square by a first and use b only to break ties, as a dictionary orders words. This relation is complete and transitive. Suppose u represented it. For each a the interval from u(a, 0) to u(a, 1) is non empty, and the intervals for different a do not overlap. Each interval contains a rational number, so we would have uncountably many different rationals. That is impossible, so no utility function exists. Debreu showed that continuity of preferences is the extra condition that rescues the theorem for infinite sets.</p>')}
{ladder(
    '<p>If you can rank your choices without going round in circles, you can give each one a score, and the best choice is the one with the highest score.</p>',
    '<p>u represents ⪰ when x ⪰ y exactly when u(x) ≥ u(y). For finite X a rational preference always has such a u, built by peeling off the best class. Any strictly increasing transform gives another valid u.</p>',
    '<p>Ordinal utility is unique only up to strictly increasing transformations. Debreu\'s theorem extends existence to continuous preferences on connected separable spaces. Lexicographic preferences show that completeness and transitivity alone are not enough on infinite sets.</p>',
    '<p>In learning from human feedback, a reward model is a learned utility over outputs fitted to pairwise comparisons, for example with the Bradley Terry model. Intransitive human judgments then show up as label noise that no single scalar reward can fit.</p>')}
''', kw=['existence theorem', 'proof by construction', 'top ranked', 'indifference class', 'n factorial', 'lexicographic', 'Debreu'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'u represents ⪰ when', ['x ⪰ y ⟺ u(x) = u(y)', 'x ⪰ y ⟺ u(x) ≥ u(y)', 'u is measured in money', 'u is always positive'], 1,
       'Bigger means at least as good.', 'Weak preference corresponds to ≥. Equality is only for indifference.')
K.quiz('e', 'u(A) = 10, u(B) = 5, u(C) = 5. What does it say about B and C?', ['B ≻ C', 'C ≻ B', 'B ∼ C', 'Nothing'], 2,
       'Equal numbers.', 'u(B) = u(C) means indifference.')
K.quiz('e', 'Which of these represents the same preference as u?', ['−u', '2u + 7', 'u − u²', '1/u for positive u'], 1,
       'Strictly increasing.', '2u + 7 keeps every comparison. −u and 1/u reverse it.')
K.quiz('e', 'A utility of 50 means', ['50 rupees', '50 dollars', 'A score whose meaning depends on the model', '50 percent'], 2,
       'Utility is not automatically money.', 'Utility is a number that represents desirability. Money is the unit only when the model says so.')
K.quiz('m', 'Which three conditions guarantee a utility function in lecture 1?', ['Finite X, completeness, transitivity', 'Continuity, convexity, monotonicity', 'Finite A, finite X, transitivity', 'Completeness, symmetry, reflexivity'], 0,
       'One about size, two about the preference.', 'Finite outcomes plus a rational preference.')
K.quiz('m', 'Why can a cycle A ≻ B ≻ C ≻ A never be represented?', ['It would need u(A) > u(A)', 'It is incomplete', 'X is too small', 'Utility must be positive'], 0,
       'Chain the inequalities.', 'u(A) > u(B) > u(C) > u(A) gives u(A) > u(A).')
K.quiz('m', 'How many strict rankings of 5 outcomes are there?', ['25', '32', '120', '3125'], 2,
       'Orderings of 5 objects.', '5! = 120.')
K.quiz('m', 'Ordinal utility means', ['Only the order of the numbers matters', 'Differences matter', 'Ratios matter', 'Utility is money'], 0,
       'Order.', 'Any strictly increasing transform gives the same ordinal utility.')
K.quiz('h', 'In the construction proof, what gets the same number?', ['All outcomes', 'Outcomes in the same indifference class', 'Outcomes next to each other in the list', 'Only the best outcome'], 1,
       'Ties.', 'Each indifference class gets one value, and values fall as the classes get worse.')
K.quiz('h', 'Which argument shows a top ranked outcome exists in finite X?', ['Induction on probability', 'If none existed, following "is beaten by" would cycle, contradicting transitivity', 'Every set has a maximum', 'Completeness alone'], 1,
       'Finite plus transitive.', 'An endless chain of improvements in a finite set must repeat, which creates a cycle.')
K.quiz('x', 'Why does lexicographic preference on the unit square have no utility function?', ['It is not transitive', 'It would need uncountably many disjoint intervals of reals, each with its own rational', 'It is incomplete', 'It is cyclic'], 1,
       'Count the rationals.', 'Each a needs a non empty interval of u values that does not overlap the others. There are only countably many rationals to fill them.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A ≻ B ∼ C ≻ D. Using the construction with values counting down to 1, what is u(B)?', '2', 'Three classes.',
       ['Classes from best to worst: {A}, {B, C}, {D}.', 'Three classes get 3, 2, 1.', eq('u(B) = 2')], check=2)
K.calc('e', 'How many strict rankings of 4 outcomes exist?', '24', '4!.',
       ['A ranking chooses the best of 4, then the best of the remaining 3, and so on.', '4 × 3 × 2 × 1.', eq('4! = 24')], check=24)
K.calc('e', 'v(x) = 2u(x) + 7 and u(A) = 10. What is v(A)?', '27', 'Substitute.',
       ['v(A) = 2 × u(A) + 7.', '2 × 10 = 20.', eq('v(A) = 20 + 7 = 27')], check=27)
K.calc('m', 'Actions a1, a2, a3 lead to x1, x2, x3 with u = 5, 10, 7. What is the largest action value v(a)?', '10', 'v(a) = u(c(a)).',
       ['v(a1) = u(x1) = 5.', 'v(a2) = u(x2) = 10, v(a3) = u(x3) = 7.', eq('max v = 10, at a2')], check=10)
K.calc('m', 'How many indifference classes does A ∼ B ≻ C ∼ D ∼ E ≻ F have?', '3', 'Count the groups.',
       ['Group 1: A, B.', 'Group 2: C, D, E.', 'Group 3: F.', eq('3 classes')], check=3)
K.calc('m', 'u(A) = 4 and u(B) = 2. Under v = u³ what is v(A) − v(B)?', '56', 'Cube each.',
       ['v(A) = 4³ = 64.', 'v(B) = 2³ = 8.', eq('v(A) − v(B) = 56'), 'The gap changed from 2 to 56, yet the ranking did not. Gaps carry no ordinal meaning.'], check=56)
K.calc('m', 'How many weak orders (rankings with ties allowed) exist on 3 outcomes?', '13', 'Split by the number of tied groups.',
       ['Three groups: 3! = 6.', 'Two groups: pick the tied pair (3 ways) and whether it sits on top or bottom (2 ways): 6.', 'One group: 1.', eq('6 + 6 + 1 = 13')], check=13)
K.calc('h', 'A ranking of 10 strict outcomes is listed one per second. How many days does it take to list all of them? Round to one decimal.', '42.0', '10! seconds.',
       ['10! = 3,628,800 rankings.', 'One day has 86,400 seconds.', eq('3,628,800 ÷ 86,400 = 42.0 days')], check=42.0, tol=0.05)
K.calc('h', 'How many digits does 20! have?', '19', 'Use 20! ≈ 2.43 × 10¹⁸.',
       ['20! = 2,432,902,008,176,640,000.', 'In scientific form that is about 2.43 × 10¹⁸.', eq('A number between 10¹⁸ and 10¹⁹ has 19 digits.')], check=19)
K.calc('h', 'u(A) = 3, u(B) = 2, u(C) = 2, u(D) = 1. Find a and b for v = a·u + b so that v(A) = 100 and v(D) = −5. Give a.', '52.5', 'Two equations, two unknowns.',
       ['3a + b = 100.', 'a + b = −5.', 'Subtract: 2a = 105.', eq('a = 52.5, b = −57.5, so v(B) = v(C) = 47.5')], check=52.5)
K.calc('x', 'How many weak orders exist on 4 outcomes?', '75', 'Count by the number of tied groups k, using surjections.',
       ['k = 4: 4! = 24.', 'k = 3: choose the tied pair (6) and order 3 groups (6): 36.', 'k = 2: split 4 into two ordered non empty groups: 2⁴ − 2 = 14.', 'k = 1: 1.', eq('24 + 36 + 14 + 1 = 75')], check=75)

# ---------------------------------------------------------------- assignments
K.assign('build', 'm', 'Build a utility function',
         '<p>Write <code>utility(X, weak)</code> that applies the construction from class. Repeatedly take the outcomes that are at least as good as every remaining outcome, give them the next value, and remove them. The worst class gets 1. Return a dictionary from outcome to value.</p>',
         '''
def utility(X, weak):
    # your code here
    pass
''', [("utility(['A','B','C'], {('A','A'),('B','B'),('C','C'),('A','B'),('A','C'),('B','C'),('C','B')})", {'A': 2, 'B': 1, 'C': 1}),
      ("utility(['A','B','C','D'], {('A','A'),('B','B'),('C','C'),('D','D'),('A','B'),('A','C'),('A','D'),('B','D'),('C','D'),('B','C'),('C','B')})", {'A': 3, 'B': 2, 'C': 2, 'D': 1})],
         '''
def utility(X, weak):
    left = list(X)
    classes = []
    while left:
        top = [x for x in left if all((x, y) in weak for y in left)]
        classes.append(top)
        left = [x for x in left if x not in top]
    return {x: len(classes) - i for i, cls in enumerate(classes) for x in cls}
''', 'Collect the classes first, then number them from the end so the worst one gets 1.',
         '<p>This is exactly the proof by construction. On a cyclic relation the top list would be empty and the loop would never end, which is the proof that cycles have no utility.</p>')
K.assign('samerank', 'e', 'Do two utilities agree?',
         '<p>Write <code>same_preference(u, v)</code> for two dictionaries over the same outcomes. Return True when u(x) ≥ u(y) exactly when v(x) ≥ v(y) for every pair.</p>',
         '''
def same_preference(u, v):
    # your code here
    pass
''', [("same_preference({'A': 10, 'B': 5, 'C': 5}, {'A': 100, 'B': -10, 'C': -10})", True),
      ("same_preference({'A': 10, 'B': 5, 'C': 1}, {'A': 10, 'B': 1, 'C': 5})", False),
      ("same_preference({'A': 1, 'B': 2}, {'A': -1, 'B': -2})", False)],
         '''
def same_preference(u, v):
    return all((u[x] >= u[y]) == (v[x] >= v[y]) for x in u for y in u)
''', 'Compare the result of ≥ for every ordered pair.', '<p>The first test is the lecture example: both functions represent A ≻ B ∼ C.</p>')

K.must('Representation', 'x ⪰ y ⟺ u(x) ≥ u(y). Strict gives >, indifference gives =. Not "=" for weak preference.')
K.must('Ordinal', 'Only order matters. Any strictly increasing f gives f(u), another valid utility. Gaps and ratios mean nothing.')
K.must('Existence', 'Finite X + complete + transitive ⟹ a utility exists. Build it by peeling off top classes: A ≻ B ∼ C ≻ D gives 3, 2, 2, 1.')
K.must('Best exists', 'In finite X an endless chain of improvements must cycle, which transitivity forbids. Ties at the top are allowed.')
K.must('Counting', 'n strict outcomes give n! rankings (5! = 120). With ties: 1, 3, 13, 75 weak orders.')

T = K.topic(
    slug='utility-functions', topic='utility-functions', step=(1, 'Rational choice', 'aai-choice', 'Turn choice into mathematics: preferences, utility functions and picking the best action when outcomes are certain.', 'School and college'),
    title='Utility functions', short='Utility', badge='1.2', minutes=40,
    lead='Turn a ranking into numbers, see why only the order of those numbers matters, and prove that every rational preference over a finite set has a utility function.',
    desc='Utility as a representation of preference, the correct ≥ condition, ordinal against cardinal utility, increasing transformations with proof, the existence theorem and its proof by construction, why a best outcome exists, what fails without each condition, and counting rankings.',
    summary='Utility representation, ordinal invariance, the existence theorem with its construction proof, and counting rankings.',
    keywords=['utility function', 'ordinal utility', 'cardinal utility', 'existence theorem', 'representation', 'increasing transformation', 'n factorial'],
    recap='<p>A utility function scores outcomes so that bigger means better. Only the order of the scores matters. A rational preference over finitely many outcomes always has one, built class by class from the top.</p>')
