# Chapter 6.2: exam revision for Advanced AI. One place to revise the whole subject, organised by the kind of exam:
# school and first year questions, university semester and IIT course numericals, multiple choice and numerical answer
# papers in the NPTEL and GATE style, and derivation questions in the style of MIT and Cambridge.
# Every question is an original practice question written in the style of that tier, not a copy of a past paper.
# Every number was checked with Python before it was written down.
from cvkit import Kit, fx, fxs, frac, sqrt, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('drill', r'''
# Exam drill: a lottery and a utility function give EU, certainty equivalent and risk premium
import math
prizes = [float(x) for x in input("prizes: ").split()]
probs = [float(x) for x in input("probabilities: ").split()]
ev = sum(p * x for p, x in zip(probs, prizes))
eu = sum(p * math.sqrt(x) for p, x in zip(probs, prizes))     # u(w) = sqrt(w)
ce = eu ** 2                                                    # u inverse
print("expected value      =", round(ev, 4))
print("expected utility    =", round(eu, 4), " with u = sqrt(w)")
print("certainty equivalent =", round(ce, 4))
print("risk premium        =", round(ev - ce, 4), " positive means risk averse")
''', stdin='100 0\n0.5 0.5\n')

K.code('cournot', r'''
# Exam drill: linear Cournot duopoly p = a - b(q1 + q2), cost c per unit
a, b, c = 100, 1, 10
q = (a - c) / (3 * b)                 # each firm, from q_i = (a - c - b q_j) / 2b
p = a - b * 2 * q
print("each firm q* =", q, " price =", p, " profit each =", (p - c) * q)
Q = (a - c) / (2 * b)                 # joint monopoly
pm = a - b * Q
print("monopoly Q =", Q, " price =", pm, " total profit =", (pm - c) * Q)
''')

K.lesson('map', 'How Advanced AI is examined', f'''
<p>This chapter is for the week before an exam. It does not teach new material. It shows the shapes questions take at each level, with worked answers, and points back to the chapter where each idea is taught. The questions are original practice questions written in the style of each tier, not copies of real past papers.</p>
{table(['Tier', 'Typical format', 'What earns the marks', 'Where to practise'], [
    ['School and first year', 'Short answers, expected values, simple tables', 'A clear definition with an example, careful arithmetic', 'Lesson 2'],
    ['University semester and IIT course exams', 'Numericals by hand on trees, lotteries and games', 'Formula first, every step shown, the answer stated with its meaning', 'Lesson 3'],
    ['NPTEL and GATE style papers', 'Multiple choice, multiple select and numerical answer type', 'Speed, spotting the trap option, exact rounding', 'Lesson 4'],
    ['MIT and Cambridge style', 'Proofs, derivations and critique of a model', 'Assumptions named, a complete argument, when it breaks', 'Lesson 5']])}
<h3>The twelve ideas examined most often</h3>
<ol>
<li>Completeness and transitivity, and why a cycle allows a money pump (chapter 1.1).</li>
<li>Ordinal utility and its existence on a finite set (chapter 1.2).</li>
<li>Choosing the best action, with constraints (chapter 1.3).</li>
<li>Lotteries, CDFs and first order stochastic dominance (chapter 2.1).</li>
<li>Expected utility, compound lotteries and affine invariance (chapter 2.2).</li>
<li>Risk attitudes, certainty equivalent and risk premium (chapter 2.3).</li>
<li>Backward induction on a decision tree (chapter 3.1).</li>
<li>Discounting and the consumption problem (chapter 3.2).</li>
<li>The value of information (chapter 3.3).</li>
<li>Normal form games, best responses and Pareto optimality (chapters 4.1 to 4.3).</li>
<li>Strict and weak dominance, and the dominant strategy equilibrium (chapter 5.1).</li>
<li>IESDS and its order independence, Cournot by elimination (chapters 5.2 and 5.3).</li>
</ol>
''', kw=['exam pattern', 'revision', 'school', 'university exam', 'IIT', 'NPTEL', 'GATE', 'MIT', 'Cambridge', 'derivations'])

K.lesson('school', 'Tier 1: school and first year', f'''
<p>Questions at this level check that you can read a preference, compute an average over chances and spot a choice that is always better.</p>
{fxs(
    fx('Expected value', 'E[X] = Σ <i>p</i><sub>i</sub> <i>x</i><sub>i</sub>', 'Weight each prize by its chance and add.', key=True),
    fx('Present value', 'PV = Σ δ<sup>t</sup> <i>x</i><sub>t</sub>', 'A payment t periods away is worth δ<sup>t</sup> of its face value today.', key=True),
    fx('Strict orderings', 'n!', 'The number of ways to rank n outcomes with no ties.'))}
{steps('Question 1. Riya prefers tea to coffee and coffee to juice, but juice to tea. Is she rational in the sense of this course?', [
    'Rational preferences must be complete and transitive.',
    'Transitivity needs tea preferred to juice, but she says juice is preferred to tea.',
    'So she is not rational. A trader could sell her each swap for a small fee and take her money round the cycle, the money pump of chapter 1.1.'])}
{steps('Question 2. A raffle ticket wins 100 rupees with probability 0.3 and nothing otherwise. What is its expected value?', [
    'E = 0.3 × 100 + 0.7 × 0.',
    '= 30 rupees.',
    'A risk neutral buyer would pay up to 30 for it. A risk averse buyer would pay less.'])}
{steps('Question 3. In how many ways can you rank 4 films with no ties?', [
    'The first place has 4 choices, then 3, then 2, then 1.',
    '4 × 3 × 2 × 1.',
    '= 24 strict orderings.'])}
{steps('Question 4. Two players each pick Quiet or Confess. Confessing is better for you whatever the other does. Why do both confess?', [
    'Confess strictly dominates Quiet for each player.',
    'A rational player never plays a strictly dominated strategy.',
    'So (Confess, Confess) is played, even though (Quiet, Quiet) is better for both. That gap is the lesson of the Prisoner\'s Dilemma.'])}
{viz('bimatrix', pre='pd')}
{note('Try the presets stag and pennies in the game above. Stag has two equilibria and pennies has none in pure strategies.', 'tip')}
''', kw=['expected value', 'present value', 'orderings', 'money pump', 'transitivity', 'Prisoner\'s Dilemma', 'short answer'])

K.lesson('semester', 'Tier 2: university semester and IIT course exams', f'''
<p>Here the examiner gives a tree, a lottery or a game and asks you to work it by hand. State the formula, then show each step.</p>
{steps('Question 5. With u(w) = √w, find the certainty equivalent and risk premium of a lottery paying 100 or 0 with equal chance.', [
    'EU = 0.5 × √100 + 0.5 × √0 = 5.',
    'CE solves √CE = 5, so CE = 25.',
    'EV = 50, so the risk premium is 50 − 25 = 25.',
    'The person would swap the lottery for a sure 25. Concave utility means risk aversion.'])}
{code('drill')}
{viz('risk')}
{steps('Question 6. Two firms face p = 100 − (q₁ + q₂) with unit cost 10. Find the Cournot equilibrium.', [
    'Firm 1 maximises (100 − q₁ − q₂ − 10) q₁. The first order condition is 90 − 2q₁ − q₂ = 0.',
    'Best response q₁ = (90 − q₂) ÷ 2, and the same for firm 2.',
    'By symmetry q = (90 − q) ÷ 2, so q* = 30 each.',
    'Price 100 − 60 = 40, profit (40 − 10) × 30 = 900 each.'])}
{code('cournot')}
{viz('cournot')}
{steps('Question 7. Action A pays 10 if the market is good and 0 if bad. Action B pays 4 for sure. The market is good with probability 0.6. What is the value of perfect information?', [
    'Without information: E(A) = 6, E(B) = 4, so pick A for 6.',
    'With information: if good pick A for 10, if bad pick B for 4.',
    'Expected value with information = 0.6 × 10 + 0.4 × 4 = 7.6.',
    'VOI = 7.6 − 6 = 1.6. Never pay more than 1.6 for the forecast.'])}
{viz('voi', names='A, B', tab='Good 0.6 10 4\nBad 0.4 0 4', fee=1)}
{steps('Question 8. Split K = 100 over two periods to maximise ln x₁ + δ ln x₂ with δ = 0.9.', [
    'The first order conditions give 1 ÷ x₁ = δ ÷ x₂, so x₂ = δ x₁.',
    'Budget x₁ + δ x₁ = 100, so x₁ = 100 ÷ 1.9.',
    eq('x₁ = 52.63, x₂ = 47.37'),
    'A more patient person (δ closer to 1) spreads consumption more evenly.'])}
{viz('consume')}
''', kw=['certainty equivalent', 'risk premium', 'Cournot', 'best response', 'value of information', 'consumption', 'ln utility', 'hand computation'])

K.lesson('mcq', 'Tier 3: multiple choice and numerical answer papers', f'''
<p>In these papers there is no partial credit and often a penalty for a wrong option. Learn the quick checks below and use them to rule options out before you compute.</p>
{table(['Quick check', 'Use it to'], [
    ['A strictly dominant strategy equilibrium, if it exists, is unique', 'Reject any option listing two'],
    ['Affine change a u + b with a &gt; 0 keeps every expected utility ranking', 'Reject options where a rescaled utility flips a choice'],
    ['Concave u means CE &lt; EV and a positive risk premium', 'Spot a risk averse answer at a glance'],
    ['VOI is never negative', 'Reject a negative VOI at once'],
    ['IESDS order does not change the result, iterated weak dominance can', 'Answer order questions in one line'],
    ['Linear Cournot q* = (a − c) ÷ 3b, Bertrand price = c', 'Compute in seconds']])}
{steps('Question 9 (numerical answer). A payment of 100 arrives in 2 years with δ = 0.9. Its present value is', [
    'PV = δ² × 100.',
    '= 0.81 × 100.',
    '= 81.'])}
{steps('Question 10 (multiple select). Which are true for u(w) = w²? (a) risk loving (b) CE &gt; EV (c) risk premium &lt; 0 (d) concave', [
    'u is convex, so the person is risk loving. (a) is true.',
    'For a convex u, Jensen gives u(EV) ≤ EU, so CE ≥ EV. (b) is true for a lottery with real risk.',
    'Risk premium = EV − CE &lt; 0. (c) is true.',
    '(d) is false. Answer: a, b, c.'])}
{steps('Question 11 (numerical answer). A player has 3 decision nodes with 2 actions at each. How many pure strategies?', [
    'A strategy names one action at every node, even nodes it never reaches.',
    '2 × 2 × 2.',
    '= 8. The R&amp;D tree of chapter 3.1 had 2 nodes and 4 strategies, MM, MD, DM and DD.'])}
{steps('Question 12 (numerical answer). A lottery pays 2<sup>k</sup> with probability 2<sup>−k</sup> for k = 1 to 10. Its expected value is', [
    'Each term is 2<sup>−k</sup> × 2<sup>k</sup> = 1.',
    'Ten terms.',
    '= 10. Without the cap the sum grows without bound, the St Petersburg paradox.'])}
{note('Round only at the very end. A numerical answer type key often has a narrow range such as 52.6 to 52.7.', 'exam')}
''', kw=['MCQ', 'numerical answer type', 'GATE', 'NPTEL', 'quick checks', 'present value', 'pure strategies', 'St Petersburg'])

K.lesson('derive', 'Tier 4: proofs, derivations and critique', f'''
<p>Exams in the style of MIT and Cambridge reward a complete argument more than a final number. State the assumptions, prove the claim, then say when it fails.</p>
<h3>Question 13. Show that every complete and transitive preference on a finite set has a utility function.</h3>
{steps('Model answer', [
    'For each outcome x, let u(x) be the number of outcomes y with x ⪰ y.',
    'If x ⪰ z then, by transitivity, every y below z is also below x, so u(x) ≥ u(z).',
    'If x ≻ z then z ⪰ x fails, so x is counted for x but not for z, and u(x) &gt; u(z).',
    'Completeness makes sure every pair is compared, so u represents ⪰.',
    'It fails on some infinite sets, for example lexicographic preferences on the plane have no real valued utility.'])}
<h3>Question 14. Show that a concave utility gives a positive risk premium.</h3>
{steps('Model answer', [
    'Jensen: for concave u, E[u(X)] ≤ u(E[X]).',
    'The certainty equivalent satisfies u(CE) = E[u(X)] ≤ u(E[X]).',
    'u is increasing, so CE ≤ E[X], and the risk premium E[X] − CE ≥ 0.',
    'Equality holds only for a lottery with no real risk or a linear u.'])}
<h3>Question 15. Show that expected utility rankings survive a positive affine change.</h3>
{steps('Model answer', [
    'Let v = a u + b with a &gt; 0.',
    'E[v] = a E[u] + b because expectation is linear.',
    'So E[u(L₁)] ≥ E[u(L₂)] if and only if E[v(L₁)] ≥ E[v(L₂)].',
    'A non affine change such as u² can flip the ranking, which is why vNM utility is cardinal (chapter 2.2).'])}
<h3>Question 16. Show that a strictly dominant strategy equilibrium is unique.</h3>
{steps('Model answer', [
    'Suppose s and t are both strictly dominant for player i and s ≠ t.',
    'Since s strictly dominates every other strategy, u<sub>i</sub>(s, x) &gt; u<sub>i</sub>(t, x) for every x.',
    'Since t is strictly dominant, u<sub>i</sub>(t, x) &gt; u<sub>i</sub>(s, x). Both cannot hold.',
    'So each player has at most one, and the equilibrium is unique. Weak dominance does not give this.'])}
<h3>Critique questions</h3>
<p>A critique question gives a model and asks what is wrong with it. For example, "a firm uses expected value to price insurance". The answer names the missing piece: the buyer is risk averse, so the willingness to pay exceeds the expected loss by the risk premium. Another favourite: "the players will reach (Quiet, Quiet) because it is Pareto better". The answer: Pareto optimality says nothing about what rational players choose. Each player still gains by deviating.</p>
{note('In proofs, name each assumption when you use it: completeness, transitivity, the vNM axioms, common knowledge of rationality. Examiners often ask what breaks when one fails.', 'exam')}
{ladder(
    '<p>At school you read preferences, compute expected values and spot a choice that is always better.</p>',
    '<p>At university you solve trees, lotteries and games by hand, step by step, and explain what the number means.</p>',
    '<p>In competitive papers you must recognise the right formula fast, use quick checks to drop options and round only at the end.</p>',
    '<p>At research universities you prove existence of utility, Jensen based risk results, affine invariance and the uniqueness and order independence results for dominance.</p>')}
''', kw=['proof', 'utility existence', 'Jensen', 'risk premium proof', 'affine invariance', 'dominant strategy uniqueness', 'critique', 'MIT', 'Cambridge'])

K.lesson('sheet', 'Formula sheet and last minute checks', f'''
{table(['Topic', 'Formula'], [
    ['Rational preference', 'complete and transitive'],
    ['Utility representation', 'x ⪰ y if and only if u(x) ≥ u(y)'],
    ['CDF', 'F(x) = P(X ≤ x), non decreasing, from 0 to 1'],
    ['First order stochastic dominance', 'F<sub>A</sub>(x) ≤ F<sub>B</sub>(x) for all x'],
    ['Expected utility', 'E[u] = Σ p<sub>i</sub> u(x<sub>i</sub>)'],
    ['Certainty equivalent, risk premium', 'u(CE) = E[u], &nbsp; RP = E[X] − CE'],
    ['Present value', 'PV = Σ δ<sup>t</sup> x<sub>t</sub>, &nbsp; perpetuity δ ÷ (1 − δ) per unit from next period'],
    ['ln consumption, two periods', 'x₁ = K ÷ (1 + δ), x₂ = δ K ÷ (1 + δ)'],
    ['Value of information', 'VOI = E[max with information] − max E[without]'],
    ['Linear Cournot duopoly', 'q* = (a − c) ÷ 3b, &nbsp; monopoly Q = (a − c) ÷ 2b'],
    ['Bertrand with equal cost', 'p* = c'],
    ['Pareto optimal', 'no other profile makes someone better and nobody worse']])}
<h3>Ten mistakes that cost marks</h3>
<ol>
<li>Calling a preference rational without checking transitivity.</li>
<li>Treating ordinal utility as cardinal, for example adding utilities of different people.</li>
<li>Computing expected value when the question asks for expected utility.</li>
<li>Reporting expected utility as the certainty equivalent without applying u inverse.</li>
<li>Forgetting chance nodes when folding back a tree.</li>
<li>Listing a strategy that skips nodes off the path.</li>
<li>Discounting the first payment when it is received today.</li>
<li>Reporting a negative value of information.</li>
<li>Confusing a Pareto optimal profile with an equilibrium.</li>
<li>Deleting weakly dominated strategies when the question asks for strict IESDS.</li>
</ol>
''', kw=['formula sheet', 'common mistakes', 'last minute revision', 'expected utility', 'Cournot', 'VOI', 'present value'])

# ---------------------------------------------------------------- mock quiz
K.quiz('e', 'Which pair of properties makes a preference rational in this course?', ['Reflexive and symmetric', 'Complete and transitive', 'Continuous and convex', 'Monotone and concave'], 1,
       'Two properties from chapter 1.1.', 'Rational means complete and transitive.')
K.quiz('e', 'A ticket wins 50 with probability 0.2 and 0 otherwise. Its expected value is', ['5', '10', '20', '50'], 1,
       'p × prize.', '0.2 × 50 = 10.')
K.quiz('e', 'How many strict orderings of 3 outcomes are there?', ['3', '6', '9', '13'], 1,
       'n!.', '3! = 6. With ties allowed there are 13 weak orders.')
K.quiz('m', 'A person with u(w) = √w is', ['Risk loving', 'Risk neutral', 'Risk averse', 'Undefined'], 2,
       'Concave or convex.', '√w is concave, so the person is risk averse.')
K.quiz('m', 'Which change of utility always keeps expected utility rankings?', ['u²', 'ln u', '3u + 7', '−u'], 2,
       'Positive affine.', 'Only a u + b with a &gt; 0 is safe.')
K.quiz('m', 'In the linear Cournot duopoly with a = 100, b = 1 and c = 10, each firm produces', ['45', '30', '22.5', '90'], 1,
       '(a − c) ÷ 3b.', '90 ÷ 3 = 30.')
K.quiz('m', 'The value of perfect information can be', ['Negative', 'Zero or positive', 'Only positive', 'Any real number'], 1,
       'Information can be ignored.', 'You can always ignore it, so VOI ≥ 0. It is 0 when no signal changes your choice.')
K.quiz('h', 'In the Prisoner\'s Dilemma, (Quiet, Quiet) is', ['The equilibrium and Pareto optimal', 'Pareto optimal but not an equilibrium', 'Neither', 'An equilibrium but not Pareto optimal'], 1,
       'Check deviations.', 'Both are better off than at (Confess, Confess), but each gains by deviating.')
K.quiz('h', 'IESDS with strict dominance gives', ['A result that depends on the order', 'The same result in any order', 'Always a single profile', 'Always the Pareto optimum'], 1,
       'Theorem from chapter 5.2.', 'Strict IESDS is order independent. Weak IESDS is not.')
K.quiz('h', 'With δ = 0.9 and ln utility over two periods, the share of K eaten in period 1 is', ['0.5', '0.474', '0.526', '0.9'], 2,
       '1 ÷ (1 + δ).', '1 ÷ 1.9 = 0.526.')
K.quiz('x', 'The standard proof that concave utility gives risk aversion uses', ['Bayes rule', 'Jensen\'s inequality', 'Backward induction', 'The intermediate value theorem only'], 1,
       'Concave and expectation.', 'Jensen gives E[u(X)] ≤ u(E[X]).')
K.quiz('x', 'Lexicographic preferences on the plane are', ['Not transitive', 'Complete and transitive but have no real utility function', 'Represented by u = x + y', 'Incomplete'], 1,
       'Chapter 1.2.', 'They are rational but no real valued u represents them.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Expected value of a ticket paying 100 with probability 0.3 and 0 otherwise?', '30', 'p × prize.',
       ['0.3 × 100 = 30.', '0.7 × 0 = 0.', eq('E = 30')], check=30)
K.calc('e', 'Number of strict orderings of 4 outcomes?', '24', '4!.',
       ['4 × 3 = 12.', '12 × 2 = 24.', eq('24 × 1 = 24')], check=24)
K.calc('e', 'Present value of 100 paid in 2 years with δ = 0.9?', '81', 'δ² × 100.',
       ['δ² = 0.81.', '0.81 × 100.', eq('PV = 81')], check=0.81 * 100, tol=0.001)
K.calc('m', 'Certainty equivalent of 100 or 0 with equal chance, u(w) = √w?', '25', 'Square the expected utility.',
       ['EU = 0.5 × 10 + 0.5 × 0 = 5.', 'u(CE) = 5.', eq('CE = 5² = 25')], check=25)
K.calc('m', 'Risk premium of that lottery?', '25', 'EV − CE.',
       ['EV = 50.', 'CE = 25.', eq('RP = 25')], check=25)
K.calc('m', 'Cournot with p = 100 − Q and c = 10: quantity of each firm?', '30', '(a − c) ÷ 3b.',
       ['a − c = 90.', '3b = 3.', eq('q* = 30')], check=30)
K.calc('m', 'Price in that Cournot equilibrium?', '40', 'p = 100 − 2q*.',
       ['Q = 60.', 'p = 100 − 60.', eq('p = 40')], check=40)
K.calc('m', 'Value of perfect information in question 7 (A pays 10 or 0, B pays 4, P(good) = 0.6)?', '1.6', 'With minus without.',
       ['Without: max(6, 4) = 6.', 'With: 0.6 × 10 + 0.4 × 4 = 7.6.', eq('VOI = 1.6')], check=0.6 * 10 + 0.4 * 4 - 6, tol=0.0001)
K.calc('h', 'Optimal x₁ for ln x₁ + 0.9 ln x₂ with x₁ + x₂ = 100? Two decimals.', '52.63', 'K ÷ (1 + δ).',
       ['x₂ = δ x₁.', 'x₁ (1 + 0.9) = 100.', eq('x₁ = 52.63')], check=100 / 1.9, tol=0.005)
K.calc('h', 'Arrow Pratt coefficient −u″ ÷ u′ for u(w) = ln w at w = 50?', '0.02', 'u′ = 1/w, u″ = −1/w².',
       ['u′(50) = 0.02.', 'u″(50) = −0.0004.', eq('−u″ ÷ u′ = 0.02')], check=1 / 50, tol=0.00001)
K.calc('x', 'Present value of 10 every period forever, starting today, with δ = 0.95?', '200', '10 ÷ (1 − δ).',
       ['Sum 10 (1 + δ + δ² + …).', 'Geometric sum 1 ÷ (1 − 0.95) = 20.', eq('PV = 200')], check=10 / (1 - 0.95), tol=0.001)
K.calc('x', 'Expected value of a lottery paying 2<sup>k</sup> with probability 2<sup>−k</sup> for k = 1 to 10?', '10', 'Each term is 1.',
       ['2<sup>−k</sup> × 2<sup>k</sup> = 1.', 'There are 10 terms.', eq('E = 10')], check=sum(2 ** -k * 2 ** k for k in range(1, 11)), tol=0.0001)
K.calc('x', 'Pure strategies of a player with 3 decision nodes and 2 actions at each?', '8', 'Multiply the choices.',
       ['A strategy names an action at every node.', '2 × 2 × 2.', eq('8')], check=8)

T = K.topic(
    slug='exam-revision', topic='exam-revision', kind='revision',
    step=(6, 'Quiz and exam revision', 'aai-review', 'Check yourself with Quiz 1 fully solved, then revise the whole subject by exam style from school level to IIT, MIT and Cambridge.', 'All levels'),
    title='Exam revision: from school to research universities', short='Exam revision', badge='6.2', minutes=60,
    lead='Practise the question shapes of every level with worked answers: expected values and money pumps, trees, lotteries and Cournot by hand, quick multiple choice checks, and proofs with their assumptions.',
    desc='Exam patterns by tier, worked questions on rational preference, expected value, certainty equivalent, Cournot, value of information, consumption, present value and strategies, proofs of utility existence, risk aversion, affine invariance and dominant strategy uniqueness, a formula sheet and common mistakes.',
    summary='Exam style questions from school level to research universities, with worked answers, a formula sheet and a mock quiz.',
    keywords=['exam', 'revision', 'formula sheet', 'mock quiz', 'numericals', 'proofs', 'IIT', 'NPTEL', 'GATE', 'MIT', 'Cambridge'],
    recap='')
