# Chapter 2.2: expected utility and compound lotteries. Source: lecture 2 (expected payoff discrete and continuous,
# expected payoff against expected outcome, the R&D compound lottery with success 0.625 and market 0.9 or 0.5,
# reduction to 10 with 0.75 against 0.5, optimistic and pessimistic comparison, the reversal u(B) = -1 to -8 with
# EU 6.5 against 5 then 4.75 against 5, positive affine transformations, practice problems 5, 6 and 9, present value)
# and lecture 3 (sections 21 and 22, the rational choice rule under uncertainty).
from cvkit import Kit, fx, fxs, frac, sqrt, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('reduce', r'''
# Reduce the R&D compound lottery: multiply along each path, add the paths with the same payoff
tree = {"G": [(0.625, [(0.9, 10), (0.1, 0)]),      # success, then market good or bad
              (0.375, [(0.5, 10), (0.5, 0)])],     # failure, then market good or bad
        "S": [(1.0,   [(0.5, 10), (0.5, 0)])]}     # no research: only the market

for action, branches in tree.items():
    simple = {}
    for p1, leaves in branches:
        for p2, pay in leaves:
            simple[pay] = simple.get(pay, 0) + p1 * p2
    eu = sum(p * pay for pay, p in simple.items())
    print(action, {k: round(v, 4) for k, v in simple.items()}, " EU =", round(eu, 3))
''')

K.code('affine', r'''
# Same ranking C > A > D > B, two utility scales, opposite choices
def eu(u, lottery):
    return sum(p * u[x] for x, p in lottery)

G = [("A", 0.75), ("B", 0.25)]
S = [("C", 0.5), ("D", 0.5)]
u1 = {"A": 9, "B": -1, "C": 10, "D": 0}
u2 = {"A": 9, "B": -8, "C": 10, "D": 0}
v = {x: 2 * t + 3 for x, t in u1.items()}            # a positive affine copy of u1

for name, u in [("u", u1), ("u'", u2), ("2u + 3", v)]:
    g, s = eu(u, G), eu(u, S)
    print(f"{name:7} EU(G) = {g:6.2f}  EU(S) = {s:6.2f}  choose {'G' if g > s else 'S'}")
''')

K.lesson('eu', 'Expected utility', f'''
<p>Once each action is a lottery, how do we compare two lotteries? The course uses the most common answer: weight each outcome\'s utility by its probability and add. The result is the expected utility of the action, and the rational agent picks the action with the largest.</p>
{fxs(
    fx('Expected utility, discrete', '<i>EU</i>(<i>a</i>) = ∑<sub><i>i</i></sub> <i>P</i>( <i>x</i><sub><i>i</i></sub> | <i>a</i> ) <i>u</i>( <i>x</i><sub><i>i</i></sub> )', 'Probability times utility, summed over outcomes.', key=True),
    fx('Expected utility, continuous', '<i>EU</i>(<i>a</i>) = ∫ <i>u</i>(<i>x</i>) d<i>F</i><sub><i>a</i></sub>(<i>x</i>) = ∫ <i>u</i>(<i>x</i>) <i>f</i><sub><i>a</i></sub>(<i>x</i>) d<i>x</i>', 'The second form needs a density.'),
    fx('Rational choice under risk', '<i>a</i>* ∈ arg max<sub><i>a</i></sub> E[ <i>u</i>(<i>X</i>) | <i>a</i> ]', 'Maximize expected utility, not expected money.', key=True))}
<h3>Expected payoff is not expected outcome</h3>
<p>The professor stressed this. Multiply probability by the utility of the outcome, not by the outcome itself. The two agree only when u(x) = x.</p>
{steps('Practice problems 5 and 6: 100 with 0.3, 40 with 0.7', [
    'With u(x) = x: EU = 0.3 × 100 + 0.7 × 40 = 30 + 28 = 58.',
    'With u(x) = √x: u(100) = 10 and u(40) = 6.325.',
    'EU = 0.3 × 10 + 0.7 × 6.325 = 3 + 4.427 = 7.43.',
    eq('u(E[X]) = √58 = 7.616, which is not E[u(X)] = 7.43')])}
{steps('Practice problem 9: compare two risky actions', [
    'Action A: 20 with 0.4, 0 with 0.6, so EU(A) = 8.',
    'Action B: 12 with 0.8, 0 with 0.2, so EU(B) = 9.6.',
    eq('9.6 &gt; 8, choose B'),
    'B has the smaller prize but a much better chance of getting it.'])}
''', kw=['expected utility', 'expected payoff', 'expected outcome', 'rational choice under risk', 'arg max', 'practice problems'])

K.lesson('compound', 'Compound lotteries: the R&D example', f'''
<p>A firm decides whether to invest in research (action G) or not (action S). Research succeeds with probability 0.625. After success the market is good with probability 0.9. After failure it is good with probability 0.5. A good market pays 10 and a bad one 0. Without research the market is good with probability 0.5.</p>
<p>Action G is a compound lottery: a lottery whose prizes are themselves lotteries. To compare it with S, reduce it to a simple lottery over final payoffs.</p>
{fxs(fx('Reduction of compound lotteries', '<i>P</i>(final outcome) = ∑<sub>paths</sub> ∏<sub>branches on the path</sub> <i>P</i>(branch)', 'Multiply along each path, then add the paths that end at the same outcome.', key=True))}
{viz('compound')}
{steps('Reduce action G', [
    'Success and good: 0.625 × 0.9 = 0.5625.',
    'Success and bad: 0.625 × 0.1 = 0.0625.',
    'Failure and good: 0.375 × 0.5 = 0.1875. Failure and bad: 0.1875.',
    'Check: 0.5625 + 0.0625 + 0.1875 + 0.1875 = 1.',
    eq('P(10 | G) = 0.5625 + 0.1875 = 0.75, so EU(G) = 7.5 against EU(S) = 5')])}
{code('reduce')}
<h3>Other ways to compare lotteries</h3>
{table(['Rule', 'Looks at', 'R&D answer'], [
    ['Expected utility', 'Σ p u', 'G: 7.5 against 5'],
    ['Optimistic', 'Chance of the best outcome', 'G: 0.75 against 0.5'],
    ['Pessimistic', 'Chance of the worst outcome, lower is better', 'G: 0.25 against 0.5'],
    ['Others', 'Median, quantiles, worst case, variance, chance of beating a target', 'Depends on the rule']])}
<p>Here every rule agrees. They need not. The course uses expected utility because it has a clean mathematical justification, which is the von Neumann and Morgenstern theorem in the deep box below.</p>
''', kw=['compound lottery', 'reduction', 'R&D', 'optimistic', 'pessimistic', 'decision tree with chance nodes'])

K.lesson('affine', 'Why ranking is not enough under risk', f'''
<p>Chapter 1.2 showed that any increasing transformation of a utility function keeps the ranking. Under risk that is no longer true. Lecture 2 gives a sharp example.</p>
{steps('Same ranking, opposite choice', [
    'Outcomes A, B, C, D with u = 9, −1, 10, 0. The ranking is C ≻ A ≻ D ≻ B.',
    'G gives A with 0.75 and B with 0.25. S gives C with 0.5 and D with 0.5.',
    'EU(G) = 0.75 × 9 + 0.25 × (−1) = 6.5 and EU(S) = 5. Choose G.',
    'Now change only u(B) to −8. The ranking C ≻ A ≻ D ≻ B is unchanged.',
    eq('EU(G) = 6.75 − 2 = 4.75 &lt; EU(S) = 5. Now choose S.')])}
{fxs(
    fx('Positive affine transformation', '<i>v</i>(<i>x</i>) = <i>a</i> <i>u</i>(<i>x</i>) + <i>b</i>, &nbsp; <i>a</i> &gt; 0', 'The only transformations that keep every expected utility comparison.', key=True),
    fx('Why it works', 'E[ <i>a u</i>(<i>X</i>) + <i>b</i> ] = <i>a</i> E[ <i>u</i>(<i>X</i>) ] + <i>b</i>', 'Expectation is linear. Scaling by a positive a and shifting by b keeps the order of the expected values.'))}
{viz('affine')}
{code('affine')}
{note('Moving u(B) from −1 to −8 is not affine: it stretches one gap and leaves the others alone. Under risk the sizes of the gaps matter, so expected utility needs cardinal utility, unique up to a u + b with a &gt; 0.', 'exam')}
{deep('The von Neumann and Morgenstern theorem', '<p>Suppose a preference over lotteries is complete and transitive, continuous (if L ≻ M ≻ N there is a mix of L and N indifferent to M) and independent (mixing both sides with the same third lottery does not change the comparison). Then there is a utility u over outcomes such that L ⪰ M exactly when E<sub>L</sub>[u] ≥ E<sub>M</sub>[u], and u is unique up to positive affine transformations. Independence is the axiom that the Allais paradox shows people often break.</p>')}
<h3>A look ahead: money later is worth less</h3>
<p>If research pays off in t years, its payoff should be discounted. With interest rate r, a future value FV is worth PV = FV ÷ (1 + r)<sup>t</sup> today. Chapter 3.2 develops this fully.</p>
{fxs(fx('Present value', 'PV = ' + frac('FV', '(1 + <i>r</i>)<sup><i>t</i></sup>'), 'For a risky payoff: E[u(X<sub>t</sub>)] ÷ (1 + r)<sup>t</sup>.'))}
{ladder(
    '<p>To compare two gambles, multiply what each result is worth to you by how likely it is, add up, and pick the bigger total.</p>',
    '<p>EU(a) = Σ P(xᵢ | a) u(xᵢ). Reduce compound lotteries by multiplying along paths. Expected utility choices survive a u + b with a &gt; 0 but not other increasing transforms, so utility under risk is cardinal.</p>',
    '<p>The von Neumann and Morgenstern axioms (completeness, transitivity, continuity, independence) are exactly what is needed for an expected utility representation. Reduction of compound lotteries is an extra assumption that experiments on ambiguity question.</p>',
    '<p>The Allais paradox breaks independence, and Kahneman and Tversky\'s prospect theory replaces probabilities with decision weights and utility with a value function around a reference point. Rank dependent utility and Choquet expected utility are formal models that relax independence.</p>')}
''', kw=['affine transformation', 'cardinal utility', 'reversal', 'von Neumann Morgenstern', 'independence axiom', 'Allais paradox', 'present value'])


K.lesson('levels', 'From intuition to research', f'''
<p>Expected utility weights the value of each outcome by its probability. Here it is followed from a phone insurance decision to the axioms behind it and the paradoxes that test it.</p>
{scene('insuring a phone', '<p>A phone worth 100 has a 50 percent chance of breaking this year. Expected money without insurance is 50. Many people still pay more than 50 to be covered for sure, because losing everything hurts more than its money value suggests. Expected utility, not expected money, explains this.</p>')}
{steps('Work it out: sure 40 or a coin toss for 100 or 0, with u(x) = √x', ['Expected money of the toss: 0.5 × 100 = 50, more than 40.', 'Expected utility of the toss: 0.5 × √100 + 0.5 × 0 = 5.', 'Utility of the sure amount: √40 = 6.32.', eq('6.32 > 5, so this person takes the sure 40')])}
{deep('the analysis', '<p>The von Neumann and Morgenstern theorem: if preferences over lotteries are complete, transitive, continuous and satisfy independence (mixing two lotteries with a third in the same proportion keeps their order), then there is a utility u such that lottery L is preferred to M exactly when E<sub>L</sub>[u] ≥ E<sub>M</sub>[u]. The utility is unique up to a positive affine change a·u + b with a > 0, which is why cardinal differences now matter.</p>')}
{deep('the research view', '<p>The Allais paradox shows real people break the independence axiom, and prospect theory (Kahneman and Tversky 1979) models this with reference points and distorted probability weights. In AI, an agent that maximises expected reward is an expected utility maximiser, so choosing the reward function is choosing its vN-M utility.</p>')}
{note('Expected value and expected utility differ whenever u is not a straight line. Write which one a question asks for.', 'warn')}
''', kw=['expected utility', 'vN-M axioms', 'independence axiom', 'Allais paradox', 'prospect theory'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'EU(a) for a discrete lottery is', ['Σ pᵢ xᵢ', 'Σ pᵢ u(xᵢ)', 'max u(xᵢ)', 'u(Σ pᵢ xᵢ)'], 1,
       'Utility, weighted by probability.', 'Expected utility weights each outcome\'s utility by its probability.')
K.quiz('e', 'R&D: what is P(10) for action G after reduction?', ['0.5', '0.625', '0.75', '0.9'], 2,
       '0.625 × 0.9 + 0.375 × 0.5.', '0.5625 + 0.1875 = 0.75.')
K.quiz('e', 'R&D with u(10) = 10 and u(0) = 0: EU(G) and EU(S) are', ['7.5 and 5', '10 and 5', '6.25 and 5', '7.5 and 7.5'], 0,
       'Probability of 10 times 10.', '0.75 × 10 = 7.5 and 0.5 × 10 = 5.')
K.quiz('e', 'To reduce a compound lottery you', ['Add along paths, multiply across', 'Multiply along each path and add paths with the same outcome', 'Take the largest branch', 'Average the branches'], 1,
       'Paths and products.', 'Each path\'s probability is a product. Paths that end at the same payoff add.')
K.quiz('m', 'Which transformation always keeps expected utility choices?', ['u³', 'eᵘ', '3u − 4', '−u'], 2,
       'a u + b with a > 0.', '3u − 4 is positive affine. u³ and eᵘ keep ranking but can flip lottery choices.')
K.quiz('m', 'In the lecture reversal, changing u(B) from −1 to −8 makes EU(G)', ['6.5', '5', '4.75', '2'], 2,
       '0.75 × 9 + 0.25 × (−8).', '6.75 − 2 = 4.75, now below EU(S) = 5.')
K.quiz('m', 'The pessimistic rule prefers the lottery with', ['The higher chance of the best outcome', 'The lower chance of the worst outcome', 'The higher mean', 'More outcomes'], 1,
       'Fear the worst.', 'It compares the probabilities of the worst outcome and picks the lower one.')
K.quiz('m', 'With u(x) = √x, 100 with 0.3 and 40 with 0.7, is E[u(X)] equal to u(E[X])?', ['Yes', 'No, 7.43 against 7.62', 'Only if p = 0.5', 'No, 58 against 7.62'], 1,
       'Compute both.', 'E[u] = 7.43 and u(58) = 7.616.')
K.quiz('h', 'Why does expected utility need cardinal utility?', ['Probabilities are cardinal', 'Weighted sums depend on the sizes of utility gaps, not just their order', 'Utility must be money', 'It does not'], 1,
       'Look at the reversal.', 'Changing one gap without changing the order flipped the choice.')
K.quiz('h', 'Which axiom does the Allais paradox show people break?', ['Completeness', 'Transitivity', 'Independence', 'Reflexivity'], 2,
       'Mixing with a common lottery.', 'People\'s choices change when a common consequence is changed, which breaks independence.')
K.quiz('x', 'If v = a u + b with a > 0, then EU_v(L) − EU_v(M) equals', ['EU_u(L) − EU_u(M)', 'a (EU_u(L) − EU_u(M))', 'a EU_u(L) − EU_u(M) + b', 'b'], 1,
       'The b cancels.', 'Both sides gain b, which cancels, and the difference is scaled by a > 0, so its sign is kept.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Practice problem 5: 100 with 0.3, 40 with 0.7, u(x) = x. What is EU?', '58', 'Σ p x.',
       ['0.3 × 100 = 30.', '0.7 × 40 = 28.', eq('EU = 30 + 28 = 58')], check=58)
K.calc('e', 'Practice problem 9: action B gives 12 with 0.8 and 0 otherwise. What is EU(B)?', '9.6', 'p × payoff.',
       ['0.8 × 12 = 9.6.', '0.2 × 0 = 0.', eq('EU(B) = 9.6')], check=9.6)
K.calc('e', 'R&D: what is P(success and good market)?', '0.5625', 'Multiply along the path.',
       ['P(success) = 0.625.', 'P(good | success) = 0.9.', eq('0.625 × 0.9 = 0.5625')], check=0.5625)
K.calc('m', 'Practice problem 6: 100 with 0.3, 40 with 0.7, u = √x. What is EU? Two decimals.', '7.43', '√100 = 10, √40 ≈ 6.325.',
       ['0.3 × 10 = 3.', '0.7 × 6.325 = 4.427.', eq('EU = 3 + 4.427 = 7.43')], check=0.3 * 10 + 0.7 * 40 ** 0.5, tol=0.005)
K.calc('m', 'Lecture reversal: u = 9, −1, 10, 0 for A, B, C, D. G gives A with 0.75 and B with 0.25. What is EU(G)?', '6.5', 'Weighted sum.',
       ['0.75 × 9 = 6.75.', '0.25 × (−1) = −0.25.', eq('EU(G) = 6.5')], check=6.5)
K.calc('m', 'With u\'(B) = −8 instead, what is EU(G)?', '4.75', 'Only one term changes.',
       ['0.75 × 9 = 6.75.', '0.25 × (−8) = −2.', eq('EU(G) = 4.75 &lt; EU(S) = 5')], check=4.75)
K.calc('m', 'Apply v = 2u + 3 to u = 9, −1, 10, 0. What is EU_v(G) − EU_v(S)?', '3', 'The gap is multiplied by a = 2.',
       ['EU_u(G) − EU_u(S) = 6.5 − 5 = 1.5.', 'An affine map multiplies the gap by a and cancels b.', eq('2 × 1.5 = 3')], check=3)
K.calc('h', 'R&D: what P(success) makes EU(G) = EU(S) = 5, keeping 0.9 and 0.5 for the market?', '0', 'Solve p × 0.9 + (1 − p) × 0.5 = 0.5.',
       ['P(10 | G) = 0.9p + 0.5(1 − p) = 0.5 + 0.4p.', 'Equal to 0.5 only when 0.4p = 0.', eq('p = 0'), 'Any chance of success helps, because failure is no worse than not investing.'], check=0)
K.calc('h', 'R&D with P(good | failure) = 0.2 and the rest as in class. What is EU(G)?', '6.375', 'Recompute the failure branch.',
       ['Success then good: 0.625 × 0.9 = 0.5625.', 'Failure then good: 0.375 × 0.2 = 0.075.', 'P(10) = 0.6375.', eq('EU(G) = 6.375, still above 5')], check=6.375)
K.calc('h', 'Which value of u(B) makes G and S tie, with u(A) = 9, u(C) = 10, u(D) = 0?', '-7', 'Solve 0.75 × 9 + 0.25 u(B) = 5.',
       ['EU(S) = 5.', '6.75 + 0.25 u(B) = 5.', eq('u(B) = −1.75 ÷ 0.25 = −7'), 'Below −7 the choice flips to S.'], check=-7)
K.calc('x', 'A research payoff of 10 arrives in 3 years with probability 0.75 (0 otherwise). With r = 10%, what is its expected present value? Three decimals.', '5.635', 'Discount the expected payoff.',
       ['Expected payoff = 0.75 × 10 = 7.5.', 'Discount factor = 1 ÷ 1.1³ = 1 ÷ 1.331 = 0.7513.', eq('PV = 7.5 × 0.7513 = 5.635'), 'It still beats the sure 5 from not investing. If that 5 also arrived in year 3, it would be worth only 3.757 today.'], check=7.5 / 1.1 ** 3, tol=0.0005)

# ---------------------------------------------------------------- assignments
K.assign('eu', 'e', 'Expected utility',
         '<p>Write <code>expected_utility(lot, u)</code> where lot is a list of (outcome, probability) pairs and u is a function. Return Σ p u(x) rounded to 4 decimals.</p>',
         '''
def expected_utility(lot, u):
    # your code here
    pass
''', [("expected_utility([(100, 0.3), (40, 0.7)], lambda x: x)", 58.0), ("expected_utility([(100, 0.3), (40, 0.7)], lambda x: x ** 0.5)", 7.4272),
      ("expected_utility([(10, 0.75), (0, 0.25)], lambda x: x)", 7.5)],
         '''
def expected_utility(lot, u):
    return round(sum(p * u(x) for x, p in lot), 4)
''', 'Apply u to the outcome before multiplying by its probability.', '<p>The first two tests are practice problems 5 and 6 from the notes.</p>')
K.assign('reduce', 'm', 'Reduce a two stage lottery',
         '<p>Write <code>reduce(stages)</code>. stages is a list of (p, lottery) pairs, where lottery is a list of (payoff, q) pairs. Return a dictionary from payoff to its total probability p × q summed over paths, each rounded to 4 decimals.</p>',
         '''
def reduce(stages):
    # your code here
    pass
''', [("reduce([(0.625, [(10, 0.9), (0, 0.1)]), (0.375, [(10, 0.5), (0, 0.5)])])", {'10': 0.75, '0': 0.25}),
      ("reduce([(0.6, [(10, 0.8), (0, 0.2)]), (0.4, [(10, 0.3), (0, 0.7)])])", {'10': 0.6, '0': 0.4})],
         '''
def reduce(stages):
    out = {}
    for p, lot in stages:
        for pay, q in lot:
            out[str(pay)] = out.get(str(pay), 0) + p * q
    return {k: round(v, 4) for k, v in out.items()}
''', 'Use str(payoff) as the key so the result stays JSON friendly.', '<p>The tests are the R&D example and practice problem 10. Keys are strings so the answer compares cleanly.</p>')

K.must('Expected utility', 'EU(a) = Σ P(xᵢ | a) u(xᵢ), or ∫ u dF. Choose arg max EU, not arg max E[X].')
K.must('R&D compound lottery', 'P(10 | G) = 0.625 × 0.9 + 0.375 × 0.5 = 0.75, EU(G) = 7.5 > EU(S) = 5. Multiply along paths, add paths.')
K.must('Reversal', 'u = 9, −1, 10, 0: EU(G) 6.5 > 5. u(B) = −8: 4.75 < 5. Same ranking, opposite choice.')
K.must('Affine invariance', 'Only v = a u + b with a > 0 keeps every EU comparison. Utility under risk is cardinal.')
K.must('Other rules and PV', 'Optimistic (P best), pessimistic (P worst). PV = FV ÷ (1 + r)ᵗ. vNM axioms give EU.')

T = K.topic(
    slug='expected-utility', topic='expected-utility', step=(2, 'Choice under risk', 'aai-risk', 'Choose when outcomes are uncertain: lotteries, CDFs, expected utility, compound lotteries and attitudes to risk.', 'College'),
    title='Expected utility and compound lotteries', short='Expected utility', badge='2.2', minutes=45,
    lead='Score each lottery by its expected utility, reduce the R&D compound lottery step by step, and see why a mere ranking cannot compare risky choices.',
    desc='Expected utility in discrete and continuous form, expected payoff against expected outcome, the R&D compound lottery and its reduction, optimistic and pessimistic rules, the lecture 2 reversal, positive affine transformations, the von Neumann and Morgenstern axioms, and present value.',
    summary='Expected utility, reducing compound lotteries, the R&D example, the reversal under non affine changes and why utility under risk is cardinal.',
    keywords=['expected utility', 'compound lottery', 'R&D', 'affine transformation', 'cardinal utility', 'von Neumann Morgenstern', 'present value'],
    recap='<p>Weight each outcome\'s utility by its probability. Compound lotteries reduce by multiplying along paths. Only positive affine changes of utility keep every risky choice the same.</p>')
