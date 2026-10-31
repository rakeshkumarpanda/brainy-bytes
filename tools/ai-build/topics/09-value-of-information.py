# Chapter 3.3: the value of information. Source: lecture 4 (the MBA decision with cost 10, market good 0.25,
# medium 0.5, poor 0.25, gross payoffs 32, 16, 12 with the MBA and 12, 8, 4 without; deciding first gives 9 against 8;
# the oracle gives 10.5; VOI 1.5; the student's mistake; VOI is never negative; the exploratory drilling and lease
# pricing case; practice problem C, the outdoor or indoor venue with VOI 10).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('voi', r'''
# Value of perfect information: best expected payoff with the oracle minus best without it
states = [("good", 0.25), ("medium", 0.5), ("poor", 0.25)]
pay = {"MBA":    {"good": 32 - 10, "medium": 16 - 10, "poor": 12 - 10},
       "no MBA": {"good": 12,      "medium": 8,       "poor": 4}}

without = {a: sum(p * pay[a][s] for s, p in states) for a in pay}
best_without = max(without.values())
with_info = sum(p * max(pay[a][s] for a in pay) for s, p in states)

print("decide first   :", without, " best =", best_without)
print("oracle first   :", with_info)
print("value of information =", with_info - best_without)
''')

K.code('imperfect', r'''
# An imperfect forecast for the venue problem: it is right with probability q
prior = {"sunny": 0.5, "rainy": 0.5}
pay = {"outdoor": {"sunny": 50, "rainy": -20}, "indoor": {"sunny": 30, "rainy": 25}}
best_without = max(sum(prior[s] * pay[a][s] for s in prior) for a in pay)

for q in (0.5, 0.7, 0.9, 1.0):
    total = 0
    for signal in prior:                              # the forecast says "sunny" or "rainy"
        joint = {s: prior[s] * (q if s == signal else 1 - q) for s in prior}
        p_signal = sum(joint.values())
        post = {s: joint[s] / p_signal for s in prior}  # Bayes rule
        total += p_signal * max(sum(post[s] * pay[a][s] for s in prior) for a in pay)
    print(f"forecast accuracy {q}: value of the forecast = {total - best_without:.2f}")
''')

K.lesson('mba', 'What is it worth to know first?', f'''
<p>You must decide whether to do an MBA, which costs 10, before you know how the job market will look when you graduate. Nature makes the market good with 0.25, medium with 0.5 and poor with 0.25.</p>
{table(['Market (probability)', 'With MBA, gross', 'With MBA, net of 10', 'Without MBA'], [
    ['Good (0.25)', '32', '22', '12'], ['Medium (0.5)', '16', '6', '8'], ['Poor (0.25)', '12', '2', '4']])}
{steps('Case A: decide before the market is known', [
    'E[MBA] = 0.25 × 22 + 0.5 × 6 + 0.25 × 2 = 5.5 + 3 + 0.5 = 9.',
    'E[no MBA] = 0.25 × 12 + 0.5 × 8 + 0.25 × 4 = 3 + 4 + 1 = 8.',
    eq('Get the MBA, expected payoff 9')])}
{steps('Case B: an oracle tells you the market first', [
    'Good: max(22, 12) = 22, get the MBA.',
    'Medium: max(6, 8) = 8, skip it. Poor: max(2, 4) = 4, skip it.',
    eq('E[with information] = 0.25 × 22 + 0.5 × 8 + 0.25 × 4 = 10.5')])}
{fxs(
    fx('Value of perfect information', 'VOI = E[ max<sub><i>a</i></sub> <i>u</i>(<i>a</i>, <i>s</i>) ] − max<sub><i>a</i></sub> E[ <i>u</i>(<i>a</i>, <i>s</i>) ]', 'Best with the oracle (choose per state, then average) minus best without (average per action, then choose).', key=True),
    fx('MBA example', 'VOI = 10.5 − 9 = 1.5', 'Pay an oracle anything below 1.5. Above 1.5 you are better off deciding now.', key=True))}
{viz('voi')}
{code('voi')}
{note('A student in class computed 0.25 × 22 + 0.5 × 8 + 0.25 × 4 as the no information value. That mixes actions across states, which you can only do once you know the state. Without information you must use one action in every state.', 'warn')}
''', kw=['value of information', 'MBA', 'oracle', 'perfect information', 'decide first', 'job market'])

K.lesson('never', 'Information is never worth less than zero', f'''
<p>With the oracle you could always ignore what it says and take the action you would have taken anyway. So the best plan with information is at least as good as the best plan without it.</p>
{steps('Proof that VOI ≥ 0', [
    'Let a* be the best action without information, so the no information value is E[u(a*, s)].',
    'For every state s, max<sub>a</sub> u(a, s) ≥ u(a*, s), since a* is one of the options.',
    'Take the expectation of both sides over s.',
    eq('E[max<sub>a</sub> u(a, s)] ≥ E[u(a*, s)], so VOI ≥ 0'),
    'Equality holds exactly when one action is best in every state. The oracle then never changes your choice.'])}
{steps('Practice problem C: book an outdoor or indoor venue before knowing the weather', [
    'Sunny 0.5, rainy 0.5. Outdoor pays 50 or −20. Indoor pays 30 or 25.',
    'No forecast: E[outdoor] = 15 and E[indoor] = 27.5, so book indoor, value 27.5.',
    'Perfect forecast: sunny pick outdoor 50, rainy pick indoor 25, so 0.5 × 50 + 0.5 × 25 = 37.5.',
    eq('VOI = 37.5 − 27.5 = 10')])}
{viz('voi', names='Outdoor, Indoor', tab='Sunny 0.5 50 30\nRainy 0.5 -20 25', fee=5)}
{scene('exploratory drilling', '<p>An oil company can buy a lease at price X. From geology it already has probabilities for how oily the site is, which give an expected value Y without any survey. A survey costs money but reveals more. If X is far below Y the deal is good enough already and the survey adds little. If the survey is cheap compared with what it might change, survey first. The probabilities are known before drilling, exactly like the market probabilities in the MBA example. This is also one reason firms negotiate options on two or three sites instead of surveying one in depth.</p>')}
''', kw=['VOI non negative', 'proof', 'practice problem C', 'venue', 'weather forecast', 'drilling', 'lease'])

K.lesson('imperfect', 'Imperfect information and Bayes', f'''
<p>Real forecasts are not oracles. Suppose a forecast is right with probability q. When it says "sunny", update your belief with Bayes\' rule, choose the best action for the updated belief, and average over what the forecast might say.</p>
{fxs(
    fx('Bayes update', '<i>P</i>(<i>s</i> | signal) = ' + frac('<i>P</i>(signal | <i>s</i>) <i>P</i>(<i>s</i>)', '<i>P</i>(signal)'), 'The forecast shifts the probabilities, not the payoffs.', key=True),
    fx('Value of imperfect information', 'VOI = ∑<sub>signals</sub> <i>P</i>(signal) max<sub><i>a</i></sub> E[<i>u</i>(<i>a</i>, <i>s</i>) | signal] − max<sub><i>a</i></sub> E[<i>u</i>(<i>a</i>, <i>s</i>)]', 'Between 0 and the value of perfect information.'))}
{code('imperfect')}
{steps('Venue problem with a forecast that is right 90% of the time', [
    'Forecast says sunny with probability 0.5. Then P(sunny | says sunny) = 0.45/0.5 = 0.9.',
    'Outdoor: 0.9 × 50 + 0.1 × (−20) = 43. Indoor: 0.9 × 30 + 0.1 × 25 = 29.5. Choose outdoor, 43.',
    'Forecast says rainy: P(sunny) = 0.1. Outdoor 5 − 18 = −13, indoor 3 + 22.5 = 25.5. Choose indoor, 25.5.',
    'Expected value with the forecast: 0.5 × 43 + 0.5 × 25.5 = 34.25.',
    eq('VOI = 34.25 − 27.5 = 6.75, less than 10 for a perfect forecast')])}
{deep('A forecast that is right half the time is worth nothing', '<p>With q = 0.5 the posterior after either signal equals the prior, 0.5 and 0.5. The best action after each signal is the same as without the forecast, so the value is exactly 0. Information has value only if it can change what you do. Below q = 0.5 the forecast is still useful: reverse what it says.</p>')}
{ladder(
    '<p>Finding out before you decide can only help, because you can always ignore what you learn. It is worth paying for only when it might change your choice.</p>',
    '<p>VOI = E[best per state] − best E[per action]. MBA: 10.5 − 9 = 1.5. Venue: 37.5 − 27.5 = 10. VOI ≥ 0, and it is 0 when one action wins in every state.</p>',
    '<p>For imperfect signals, compute posteriors by Bayes and the value of sample information. Blackwell\'s theorem (1953) orders information structures: one experiment is more informative than another exactly when every decision maker values it at least as much.</p>',
    '<p>In active learning and Bayesian optimization, the next query is chosen to maximize expected information or knowledge gradient, a direct use of value of information. Exploration bonuses in reinforcement learning, such as information directed sampling, trade the value of information against the immediate regret.</p>')}
''', kw=['imperfect information', 'Bayes rule', 'posterior', 'forecast accuracy', 'Blackwell', 'value of sample information', 'active learning'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In the MBA example without information, which action is best?', ['Get the MBA, 9', 'Skip the MBA, 8', 'Indifferent', 'Ask the oracle'], 0,
       'Compare 9 and 8.', 'E[MBA] = 9 > E[no MBA] = 8.')
K.quiz('e', 'With the oracle, the expected payoff is', ['9', '10', '10.5', '22'], 2,
       'Pick per state, then average.', '0.25 × 22 + 0.5 × 8 + 0.25 × 4 = 10.5.')
K.quiz('e', 'The value of perfect information in the MBA example is', ['0.5', '1', '1.5', '2.5'], 2,
       '10.5 − 9.', 'You should pay up to 1.5 for the oracle.')
K.quiz('e', 'The value of information can be', ['Negative', 'Zero or positive', 'Only positive', 'Any number'], 1,
       'You can ignore what you learn.', 'Ignoring the information reproduces the no information value, so VOI ≥ 0.')
K.quiz('m', 'When is VOI exactly 0?', ['When the oracle is expensive', 'When one action is best in every state', 'When all states are equally likely', 'Never'], 1,
       'Would you ever change your mind?', 'If the same action wins in every state, knowing the state changes nothing.')
K.quiz('m', 'Practice problem C: the best choice without a forecast is', ['Outdoor, 15', 'Indoor, 27.5', 'Outdoor, 37.5', 'Indoor, 25'], 1,
       'Average each action.', 'Indoor 0.5 × 30 + 0.5 × 25 = 27.5 beats outdoor 15.')
K.quiz('m', 'Practice problem C: the value of a perfect forecast is', ['5', '10', '12.5', '37.5'], 1,
       '37.5 − 27.5.', 'With the forecast you get 37.5.')
K.quiz('m', 'An oracle for the MBA decision asks 2. Should you pay?', ['Yes', 'No, 2 > 1.5', 'Only if risk loving', 'It does not matter'], 1,
       'Compare with VOI.', 'Paying 2 leaves 10.5 − 2 = 8.5 < 9.')
K.quiz('h', 'Why is 0.25 × 22 + 0.5 × 8 + 0.25 × 4 not the no information value?', ['Arithmetic error', 'It uses different actions in different states, which needs the state to be known', 'The probabilities are wrong', 'The MBA cost is ignored'], 1,
       'One action for all states.', 'Without information, one action must be used whatever the state.')
K.quiz('h', 'A weather forecast that is right exactly half the time is worth', ['Half the perfect value', 'Nothing', 'The full perfect value', 'A negative amount'], 1,
       'Does it change beliefs?', 'With q = 0.5 the posterior equals the prior, so no decision changes.')
K.quiz('x', 'Blackwell\'s theorem compares', ['Utility functions', 'Information structures by how every decision maker values them', 'Discount factors', 'Strategies in games'], 1,
       'More informative experiments.', 'One experiment is more informative than another if every decision problem values it at least as much.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'MBA example: what is E[MBA] net of its cost?', '9', 'Net payoffs 22, 6, 2.',
       ['0.25 × 22 = 5.5.', '0.5 × 6 = 3 and 0.25 × 2 = 0.5.', eq('E = 9')], check=9)
K.calc('e', 'MBA example: what is E[no MBA]?', '8', 'Payoffs 12, 8, 4.',
       ['0.25 × 12 = 3.', '0.5 × 8 = 4 and 0.25 × 4 = 1.', eq('E = 8')], check=8)
K.calc('e', 'MBA example: what is the value of perfect information?', '1.5', 'With minus without.',
       ['With the oracle: 10.5.', 'Without: 9.', eq('VOI = 1.5')], check=1.5)
K.calc('m', 'Practice problem C: what is E[outdoor] without a forecast?', '15', '0.5 × 50 + 0.5 × (−20).',
       ['0.5 × 50 = 25.', '0.5 × (−20) = −10.', eq('E = 15')], check=15)
K.calc('m', 'Practice problem C: what is the expected payoff with a perfect forecast?', '37.5', 'Best per state.',
       ['Sunny: max(50, 30) = 50.', 'Rainy: max(−20, 25) = 25.', eq('0.5 × 50 + 0.5 × 25 = 37.5')], check=37.5)
K.calc('m', 'MBA example: if the MBA cost were 12 instead of 10, what would E[MBA] be?', '7', 'Subtract 2 more in every state.',
       ['Net payoffs become 20, 4, 0.', '0.25 × 20 + 0.5 × 4 + 0 = 5 + 2.', eq('E[MBA] = 7 &lt; 8, now skip it')], check=7)
K.calc('m', 'With MBA cost 12, what is the value of perfect information?', '2', 'Recompute both sides.',
       ['Without: max(E[MBA], E[no MBA]) = max(7, 8) = 8.', 'With the oracle: good max(20, 12) = 20, medium max(4, 8) = 8, poor max(0, 4) = 4.', 'Expected value with the oracle: 0.25 × 20 + 0.5 × 8 + 0.25 × 4 = 5 + 4 + 1 = 10.', eq('VOI = 10 − 8 = 2'), 'A dearer MBA makes the decision closer, so knowing the market is worth more.'], check=2)
K.calc('h', 'Venue problem with a forecast right 90% of the time: what is the value of the forecast?', '6.75', 'Bayes, choose per signal, average.',
       ['Says sunny (prob 0.5): P(sunny) = 0.9, outdoor 43 beats indoor 29.5.', 'Says rainy (prob 0.5): P(sunny) = 0.1, indoor 25.5 beats outdoor −13.', 'With the forecast: 0.5 × 43 + 0.5 × 25.5 = 34.25.', eq('Value = 34.25 − 27.5 = 6.75')], check=6.75)
K.calc('h', 'Venue problem: below what P(sunny) is indoor better than outdoor without a forecast? Four decimals.', '0.6923', 'Solve 50p − 20(1 − p) = 30p + 25(1 − p).',
       ['Outdoor: 70p − 20. Indoor: 5p + 25.', '70p − 20 = 5p + 25 gives 65p = 45.', eq('p = 45/65 = 0.6923')], check=45 / 65, tol=0.00005)
K.calc('h', 'Venue problem with P(sunny) = 0.8: what is the value of perfect information?', '9', 'Recompute with the new prior.',
       ['Without: outdoor 0.8 × 50 − 0.2 × 20 = 36, indoor 24 + 5 = 29, choose outdoor 36.', 'With: 0.8 × 50 + 0.2 × 25 = 45.', eq('VOI = 45 − 36 = 9')], check=9)
K.calc('x', 'Venue problem: what is the smallest forecast accuracy q at which the forecast has positive value? Four decimals.', '0.6923', 'After a "sunny" signal, outdoor must become best.',
       ['Before the signal indoor is best, so value appears once a signal flips the choice.', 'After "sunny": P(sunny | sunny) = 0.5q ÷ 0.5 = q.', 'Outdoor beats indoor when q &gt; 45/65.', eq('q &gt; 0.6923')], check=45 / 65, tol=0.00005)

# ---------------------------------------------------------------- assignments
K.assign('voi', 'e', 'Value of perfect information',
         '<p>Write <code>voi(probs, pay)</code>. probs is a list of state probabilities and pay maps an action to its list of payoffs, one per state. Return the value of perfect information rounded to 4 decimals.</p>',
         '''
def voi(probs, pay):
    # your code here
    pass
''', [("voi([0.25, 0.5, 0.25], {'MBA': [22, 6, 2], 'No': [12, 8, 4]})", 1.5), ("voi([0.5, 0.5], {'Out': [50, -20], 'In': [30, 25]})", 10.0),
      ("voi([0.5, 0.5], {'A': [10, 8], 'B': [5, 3]})", 0.0)],
         '''
def voi(probs, pay):
    without = max(sum(p * x for p, x in zip(probs, xs)) for xs in pay.values())
    with_info = sum(p * max(xs[i] for xs in pay.values()) for i, p in enumerate(probs))
    return round(with_info - without, 4)
''', 'Without: average each action, then take the max. With: take the max in each state, then average.', '<p>The third test has one action best in every state, so the information is worth 0.</p>')
K.assign('forecast', 'h', 'Value of an imperfect forecast',
         '<p>Write <code>forecast_value(prior, pay, q)</code> for two states. prior is [P(s0), P(s1)], pay maps action to [payoff in s0, payoff in s1], and the forecast names the true state with probability q. Return the value of the forecast rounded to 4 decimals.</p>',
         '''
def forecast_value(prior, pay, q):
    # your code here
    pass
''', [("forecast_value([0.5, 0.5], {'Out': [50, -20], 'In': [30, 25]}, 0.9)", 6.75), ("forecast_value([0.5, 0.5], {'Out': [50, -20], 'In': [30, 25]}, 0.5)", 0.0),
      ("forecast_value([0.5, 0.5], {'Out': [50, -20], 'In': [30, 25]}, 1.0)", 10.0)],
         '''
def forecast_value(prior, pay, q):
    without = max(sum(p * x for p, x in zip(prior, xs)) for xs in pay.values())
    total = 0
    for sig in (0, 1):
        joint = [prior[s] * (q if s == sig else 1 - q) for s in (0, 1)]
        ps = sum(joint)
        if ps == 0:
            continue
        total += max(sum(j * x for j, x in zip(joint, xs)) for xs in pay.values())
    return round(total - without, 4)
''', 'For each signal, the joint probabilities P(s and signal) already include P(signal), so the max of Σ joint × payoff is P(signal) times the posterior best.',
         '<p>q = 1 reproduces the perfect forecast value 10, and q = 0.5 is worthless.</p>')

K.must('VOI formula', 'VOI = E[max_a u(a, s)] − max_a E[u(a, s)]. Choose per state then average, minus average per action then choose.')
K.must('MBA', 'Cost 10, states 0.25/0.5/0.25. No info: 9 (MBA) vs 8. Oracle: 22, 8, 4 gives 10.5. VOI = 1.5.')
K.must('Never negative', 'You can ignore the oracle, so VOI ≥ 0. It is 0 when one action is best in every state.')
K.must('Venue practice C', 'Outdoor 50/−20, indoor 30/25 at 0.5 each. 27.5 without, 37.5 with, VOI = 10. 90% forecast: 6.75.')
K.must('Imperfect signals', 'Update by Bayes, pick the best per signal, average. Worth 0 if it cannot change the decision (q = 0.5).')

T = K.topic(
    slug='value-of-information', topic='value-of-information', step=(3, 'Decisions over time', 'aai-time', 'Plan several moves ahead: backward induction, discounting, consumption over time and the value of information.', 'College and masters'),
    title='The value of information', short='Value of information', badge='3.3', minutes=40,
    lead='Work out how much it is worth to learn the state of the world before you decide, prove it can never be negative, and price imperfect forecasts with Bayes\' rule.',
    desc='The MBA decision from lecture 4, deciding before and after an oracle, the value of perfect information and the common mistake, the proof that it is never negative, practice problem C, the drilling and lease case, imperfect forecasts with Bayes\' rule, and Blackwell\'s theorem.',
    summary='The value of perfect and imperfect information, the MBA and venue examples, and why information is never worth less than zero.',
    keywords=['value of information', 'perfect information', 'oracle', 'Bayes rule', 'MBA', 'forecast', 'decision analysis'],
    recap='<p>Information is worth the gain from choosing per state instead of once for all states. The MBA oracle is worth 1.5 and a perfect weather forecast 10.</p>')
