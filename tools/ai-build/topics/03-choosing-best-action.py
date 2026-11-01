# Chapter 1.3: choosing the best action. Source: lecture 1 (rational choice assumptions, v(a) = u(c(a)), arg max and
# ties, the regression loss link, maximizing against satisficing), lecture 2 (the INOX and PVR movie decision tree with
# walking costs) and lecture 3 (problem 1.6 fruit trees with and without the variety preference, problem 1.7 city
# parks with the square root benefit, the budget cap, and the corner solution when the benefit changes).
from cvkit import Kit, fx, fxs, frac, sqrt, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('movie', r'''
# The movie problem: utility of the film minus 1 per mile walked
films = {"INOX": [("Aliens", 6), ("Blade Runner", 5), ("Casablanca", 4)],
         "PVR":  [("Doctor Strange", 3), ("Gone with the Wind", 2), ("The Matrix", 1)]}
miles = {"INOX": 1, "PVR": 3}
best = None
for theatre, shows in films.items():
    for film, u in shows:
        net = u - miles[theatre]
        print(f"{theatre:5} {film:20} {u} - {miles[theatre]} = {net}")
        if best is None or net > best[2]:
            best = (theatre, film, net)
print("best plan:", best)
''')

K.code('fruit', r'''
# Problem 1.6: expenditure change for every way of planting at most two trees
from itertools import combinations_with_replacement
trees = {"A": (100, 130), "O": (70, 90), "P": (120, 145)}   # (maintenance, food bill reduction)

def change(plan, variety):
    total, seen = 0, set()
    for t in plan:
        cost, save = trees[t]
        if variety and t in seen:
            save = save / 2              # a second tree of the same kind saves only half
        seen.add(t)
        total += cost - save
    return total

for variety in (False, True):
    plans = [()] + [p for k in (1, 2) for p in combinations_with_replacement("AOP", k)]
    res = {"".join(p) or "none": change(p, variety) for p in plans}
    best = min(res, key=res.get)
    print("variety" if variety else "plain  ", res, " best:", best, res[best])
''')

K.code('parks', r'''
# Problem 1.7: v(c) = sqrt(k c) - c / 80 with c between 0 and the cap
import math
cap = 0.05 * 20_000_000
for k in (400, 1600):
    stationary = (40 * math.sqrt(k)) ** 2          # from v'(c) = sqrt(k) / (2 sqrt(c)) - 1/80 = 0
    best = min(stationary, cap)
    value = math.sqrt(k * best) - best / 80
    print(f"k={k}: stationary point {stationary:,.0f}, feasible best {best:,.0f}, value {value:,.0f}")
''')

K.lesson('rational', 'From preferences to the best action', f'''
<p>Lecture 1 describes a rational individual with four pieces of knowledge. The agent knows the actions A, the outcomes X, which outcome each action leads to, and its own preference. With all four, choosing is a calculation.</p>
{fxs(
    fx('Value of an action', '<i>v</i>(<i>a</i>) = <i>u</i>( <i>c</i>(<i>a</i>) )', 'First find the consequence, then score it.', key=True),
    fx('Rational choice', '<i>a</i>* ∈ arg max<sub><i>a</i> ∈ <i>A</i></sub> <i>v</i>(<i>a</i>) &nbsp; ⟺ &nbsp; <i>v</i>(<i>a</i>*) ≥ <i>v</i>(<i>a</i>) for every <i>a</i>', 'arg max is a set. If two actions tie for the top, both are rational.', key=True))}
{note('The transcript sometimes wrote v(a*) &gt; v(a) for every other a. That strict version only fits when the best action is unique. With ties the right condition is ≥.', 'warn')}
<h3>Maximizing and satisficing</h3>
{table(['', 'Maximizing', 'Satisficing'], [
    ['Rule', 'Pick an action in arg max v', 'Pick any action with v(a) ≥ T, an aspiration level'],
    ['Search', 'Must compare everything', 'Can stop at the first good enough action'],
    ['Used', 'Throughout this course', 'Herbert Simon\'s model of real human choice under limited time']])}
<h3>Machine learning is rational choice</h3>
<p>A regression model that minimizes squared error L = (y − ŷ)² is maximizing the utility u = −(y − ŷ)². Changing the loss changes what counts as best. Rationality does not mean everyone wants the same thing. It means each agent consistently maximizes its own objective.</p>
{fxs(fx('Loss as negative utility', 'min (<i>y</i> − <i>ŷ</i>)² ⟺ max −(<i>y</i> − <i>ŷ</i>)²', 'Minimizing a loss and maximizing its negative pick the same answer.'))}
''', kw=['rational choice', 'arg max', 'action value', 'satisficing', 'maximizing', 'loss function', 'regression', 'Herbert Simon'])

K.lesson('trees', 'Decision trees: the movie problem', f'''
<p>A decision tree draws a choice as a picture. Square nodes are choices, branches are actions, and leaves are outcomes with their payoffs. A tree is a graph with no cycles, so every leaf has exactly one path from the root.</p>
<p>Lecture 2 asks you to choose between two cinemas. INOX is 1 mile away and shows Aliens, Blade Runner and Casablanca. PVR is 3 miles away and shows Doctor Strange, Gone with the Wind and The Matrix. You rank the six films alphabetically from best to worst and give them utilities 6 down to 1.</p>
{viz('movie')}
{steps('Solve it with walking costs of 1 per mile', [
    'Without walking, the best leaf is Aliens with utility 6, at INOX.',
    'Net payoff = film utility − miles walked.',
    'INOX: Aliens 6 − 1 = 5, Blade Runner 4, Casablanca 3.',
    'PVR: Doctor Strange 3 − 3 = 0, Gone with the Wind −1, The Matrix −2.',
    eq('Best: go to INOX and watch Aliens, net payoff 5')])}
{code('movie')}
<p>Now drag the PVR distance down to 0 in the animation, or move Aliens to PVR. The tree changes and so can the answer. That is the point of the tree: once the payoffs are written on the leaves, the choice follows mechanically.</p>
{scene('route planning', '<p>A navigation app builds the same kind of tree. Each junction is a decision node, each road a branch, and each arrival a leaf scored by minus the travel time. The cost of walking in the movie problem is the cost of a longer route here.</p>')}
''', kw=['decision tree', 'decision node', 'leaf', 'movie problem', 'INOX', 'PVR', 'walking cost'])

K.lesson('fruit', 'Problem 1.6: the fruit trees', f'''
<p>You may plant at most two fruit trees. Each tree costs money to maintain but lowers your food bill. You care only about total spending, so lower is better.</p>
{table(['Tree', 'Maintenance', 'Food bill reduction', 'Net change per tree'], [
    ['Apple', '$100', '$130', '−30'], ['Orange', '$70', '$90', '−20'], ['Pear', '$120', '$145', '−25']])}
{fxs(
    fx('Spending after a plan', '<i>u</i>(plan) = <i>X</i> + Σ maintenance − Σ reduction', 'X is what you spend with no trees. A smaller number is better.', key=True),
    fx('Variety version', 'second tree of the same kind saves only half', 'Part (d) of the problem. Mixed pairs keep the full saving.'))}
{steps('Part (a) and (b): list every action and its spending', [
    'Actions: none, A, O, P, AA, OO, PP, AO, AP, OP. That is 10, since order does not matter.',
    'Single trees: A gives X − 30, O gives X − 20, P gives X − 25.',
    'Pairs: AA = X − 60, OO = X − 40, PP = X − 50, AO = X − 50, AP = X − 55, OP = X − 45.',
    eq('Lowest spending is X − 60: plant two apple trees')])}
{steps('Part (d): a second tree of the same kind saves half', [
    'AA: maintenance 200, saving 130 + 65 = 195, so X + 5.',
    'OO: maintenance 140, saving 90 + 45 = 135, so X + 5.',
    'PP: maintenance 240, saving 145 + 72.5 = 217.5, so X + 22.5.',
    'Mixed pairs and single trees do not change: AP is still X − 55.',
    eq('Lowest spending is now X − 55: plant one apple and one pear')])}
{viz('fruit')}
{code('fruit')}
{note('A change in the payoff structure changed the rational choice. Nothing about the person\'s rationality changed, only the numbers on the leaves.', 'tip')}
''', kw=['problem 1.6', 'fruit trees', 'apple', 'orange', 'pear', 'variety', 'diminishing returns', 'expenditure'])

K.lesson('parks', 'Problem 1.7: how much to spend on parks', f'''
<p>A city has a budget of $20 million. By law, parks may receive at most 5%, which is $1 million. Spending c dollars gives a benefit that grows like a square root but has a cost that grows in a straight line.</p>
{fxs(
    fx('Benefit', '<i>v</i>(<i>c</i>) = ' + sqrt('400<i>c</i>') + ' − ' + frac('<i>c</i>', '80') + ' = 20' + sqrt('<i>c</i>') + ' − ' + frac('<i>c</i>', '80'), 'The action set is the interval A = [0, 1,000,000]. It is continuous, so we cannot list the actions, we must use calculus.', key=True),
    fx('First order condition', '<i>v</i>′(<i>c</i>) = ' + frac('10', sqrt('<i>c</i>')) + ' − ' + frac('1', '80') + ' = 0', 'Marginal benefit equals marginal cost.', key=True),
    fx('Second order condition', '<i>v</i>″(<i>c</i>) = −5 <i>c</i><sup>−3/2</sup> &lt; 0', 'v is strictly concave, so a stationary point inside the interval is the unique maximum.'))}
{steps('Part (b): solve with √(400c)', [
    'Set 10 / √c = 1/80.',
    'Then √c = 800.',
    'Square both sides: c = 640,000.',
    '640,000 lies inside [0, 1,000,000], and v is concave, so this is the maximum.',
    eq('c* = $640,000 and v(c*) = 20 × 800 − 8,000 = 8,000')])}
{steps('Part (c): the benefit changes to √(1600c)', [
    'Now v(c) = 40√c − c/80 and v′(c) = 20/√c − 1/80.',
    'Setting v′ = 0 gives √c = 1,600, so c = 2,560,000.',
    'That is more than the legal cap of 1,000,000, so it is not allowed.',
    'v is concave and its peak lies to the right of the cap, so v is increasing on the whole interval.',
    eq('c* = $1,000,000, a corner solution')])}
{viz('parks')}
{code('parks')}
{deep('The recipe for a one variable problem on an interval', '<p>To maximize v(c) on [L, U]: find every c with v′(c) = 0 inside the interval, then evaluate v at those points and at both ends L and U, and keep the largest. The second derivative tells you whether a stationary point is a peak (v″ &lt; 0) or a valley (v″ &gt; 0). For concave v the answer is the stationary point clipped to the interval: min(max(c₀, L), U).</p>')}
{ladder(
    '<p>Write down every choice, work out what each one gives you, and pick the one that gives the most. If there are too many choices to list, use a graph or calculus to find the top.</p>',
    '<p>v(a) = u(c(a)) and a* ∈ arg max v. Discrete problems are solved by listing or by a decision tree. Continuous ones are solved with v′ = 0, a check of v″, and a comparison with the boundary.</p>',
    '<p>With constraints, the Karush Kuhn Tucker conditions generalize the boundary check: at a corner the derivative need not be zero, but its sign must point out of the feasible set. Concavity turns these necessary conditions into sufficient ones.</p>',
    '<p>Bounded rationality asks what to do when computing arg max is itself costly. Satisficing, anytime algorithms and the value of computation in metareasoning (Russell and Wefald) treat thinking time as one more action with a cost.</p>')}
''', kw=['problem 1.7', 'city parks', 'square root', 'first order condition', 'concave', 'corner solution', 'budget constraint', 'marginal benefit'])


K.lesson('levels', 'From intuition to research', f'''
<p>Picking the best action means finding the largest value of a function. This lesson goes from listing options by hand to the hidden bias of choosing the maximum of noisy estimates.</p>
{scene('choosing how many hours to study', '<p>Each extra hour of study raises your score, but tiredness grows too. If the benefit of x hours is 10x − x², the first hours help a lot and later hours help less, until extra hours start to hurt. The best plan sits where one more hour adds nothing.</p>')}
{steps('Work it out: maximise u(x) = 10x − x² for 0 ≤ x ≤ 8', ['Derivative u′(x) = 10 − 2x, zero at x = 5.', 'Second derivative −2 < 0, so x = 5 is a maximum: u(5) = 25.', 'Check the ends: u(0) = 0 and u(8) = 80 − 64 = 16.', eq('Best action x = 5 with value 25')])}
{deep('the analysis', '<p>The Weierstrass theorem guarantees a best action when the value function is continuous and the action set is closed and bounded, as with 0 ≤ x ≤ 8. On an open set such as 0 < x < 1 with u(x) = x there is no best action, only better and better ones. If u is concave, any point where the derivative is zero is a global maximum, which is why economists like concave payoffs.</p>')}
{deep('the research view', '<p>The optimiser’s curse (Smith and Winkler 2006): when you pick the action with the highest estimated value and the estimates are noisy, the chosen estimate is biased upwards. In reinforcement learning the same effect makes Q-learning overestimate values, and double Q-learning (van Hasselt 2010) fixes it by choosing the action with one estimate and scoring it with another.</p>')}
{note('Setting the derivative to zero is not enough. Check the second derivative and the end points of the allowed range.', 'warn')}
''', kw=['argmax', 'Weierstrass', 'concavity', 'optimiser curse', 'double Q-learning'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In the movie problem with walking costs, which plan is best?', ['PVR, Doctor Strange', 'INOX, Aliens', 'INOX, Casablanca', 'Stay home'], 1,
       'Utility minus miles.', 'Aliens at INOX gives 6 − 1 = 5, the largest net payoff.')
K.quiz('e', 'In a decision tree, leaves stand for', ['Choices', 'Outcomes with their payoffs', 'Probabilities', 'Agents'], 1,
       'Where the paths end.', 'Each leaf is a final outcome with its payoff.')
K.quiz('e', 'arg max v(a) is', ['The largest value of v', 'The set of actions that reach the largest value', 'The smallest action', 'Always a single action'], 1,
       'arg returns the input.', 'max gives the value, arg max gives the actions that achieve it. It can contain ties.')
K.quiz('e', 'In problem 1.6 without variety preference, the best plan is', ['AP', 'AA', 'OO', 'PP'], 1,
       'Apple saves the most per tree.', 'AA gives X − 60.')
K.quiz('m', 'With the variety preference, the best plan becomes', ['AA', 'AP', 'OP', 'P alone'], 1,
       'Same kind pairs now lose money.', 'AA and OO give X + 5 and PP gives X + 22.5. AP stays at X − 55, the lowest.')
K.quiz('m', 'Problem 1.7 part (b) gives c* =', ['$400,000', '$640,000', '$800,000', '$1,000,000'], 1,
       '√c = 800.', 'Solving 10/√c = 1/80 gives c = 640,000.')
K.quiz('m', 'Why is the answer to part (c) of problem 1.7 $1,000,000?', ['It is the stationary point', 'The stationary point 2,560,000 is above the cap and v rises up to the cap', 'v is convex', 'Benefits are linear'], 1,
       'Check feasibility.', 'When the unconstrained peak lies outside the interval, the best feasible point is the nearest boundary.')
K.quiz('m', 'A satisficing agent', ['Always finds the best action', 'Stops at an action that meets an aspiration level', 'Never chooses', 'Picks at random'], 1,
       'Good enough.', 'Satisficing accepts any action with v(a) ≥ T.')
K.quiz('h', 'Minimizing squared error is the same as maximizing', ['(y − ŷ)²', '−(y − ŷ)²', '|y − ŷ|', 'ŷ'], 1,
       'Flip the sign.', 'Minimizing L and maximizing −L pick the same ŷ.')
K.quiz('h', 'How many actions are there in problem 1.6 part (a)?', ['6', '9', '10', '12'], 2,
       'None, three singles, six pairs.', '1 + 3 + 6 = 10, since AO and OA are the same plan.')
K.quiz('h', 'v″(c) = −5c^(−3/2) in problem 1.7 tells us', ['v is convex', 'v is strictly concave so the stationary point is a maximum', 'v has no maximum', 'v is linear'], 1,
       'Sign of the second derivative.', 'Negative second derivative means concave, so the first order condition gives a maximum.')
K.quiz('x', 'If v is concave on [L, U] and v′(c₀) = 0 at some real c₀, the maximizer is', ['c₀ always', 'min(max(c₀, L), U)', 'L', 'U'], 1,
       'Clip to the interval.', 'For concave v, the peak is c₀ when it is feasible, and otherwise the nearest end.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Movie problem: INOX is 1 mile away and Blade Runner has utility 5. What is its net payoff?', '4', 'Utility minus miles.',
       ['Net payoff = utility − cost per mile × miles.', '= 5 − 1 × 1.', eq('= 4')], check=4)
K.calc('e', 'Movie problem: what is the net payoff of The Matrix at PVR?', '-2', 'PVR is 3 miles away.',
       ['u(The Matrix) = 1.', 'Walking cost = 3.', eq('1 − 3 = −2')], check=-2)
K.calc('e', 'Problem 1.6: by how much does one orange tree change spending?', '-20', 'Maintenance minus reduction.',
       ['Maintenance adds 70.', 'Food bill falls by 90.', eq('70 − 90 = −20, so spending is X − 20')], check=-20)
K.calc('m', 'Problem 1.6: what is the spending change for the plan AP?', '-55', 'Add both trees.',
       ['Maintenance: 100 + 120 = 220.', 'Reduction: 130 + 145 = 275.', eq('220 − 275 = −55')], check=-55)
K.calc('m', 'Problem 1.6 with the variety preference: what is the change for PP?', '22.5', 'The second pear saves half.',
       ['Maintenance: 240.', 'Reduction: 145 + 72.5 = 217.5.', eq('240 − 217.5 = +22.5')], check=22.5)
K.calc('m', 'Problem 1.7: what is the maximum park spending in dollars?', '1000000', '5% of 20 million.',
       ['Budget = 20,000,000.', 'Cap = 0.05 × budget.', eq('= 1,000,000')], check=1000000)
K.calc('m', 'Problem 1.7 part (b): what is the benefit v(c*) at c* = 640,000?', '8000', 'v = 20√c − c/80.',
       ['√640,000 = 800, so 20 × 800 = 16,000.', '640,000 ÷ 80 = 8,000.', eq('v = 16,000 − 8,000 = 8,000')], check=8000)
K.calc('h', 'Problem 1.7 part (c): what is v at the cap, with v(c) = 40√c − c/80?', '27500', 'c = 1,000,000.',
       ['√1,000,000 = 1,000, so 40 × 1,000 = 40,000.', '1,000,000 ÷ 80 = 12,500.', eq('v = 40,000 − 12,500 = 27,500')], check=27500)
K.calc('h', 'For v(c) = √(kc) − c/80, the stationary point is c₀ = 1600k. For which k does c₀ hit the $1,000,000 cap exactly?', '625', 'Solve 1600k = 1,000,000.',
       ['v′(c) = √k / (2√c) − 1/80 = 0 gives √c = 40√k.', 'So c₀ = 1600k.', eq('1600k = 1,000,000 gives k = 625')], check=625)
K.calc('h', 'With walking cost m per mile, for which m are INOX Aliens and PVR Doctor Strange equally good? INOX is 1 mile, PVR 3 miles.', '-1.5', 'Set 6 − m = 3 − 3m.',
       ['INOX Aliens: 6 − m.', 'PVR Doctor Strange: 3 − 3m.', '6 − m = 3 − 3m gives 2m = −3.', eq('m = −1.5, a negative cost'), 'So for every real walking cost m ≥ 0, INOX wins. PVR wins only if walking were a pleasure worth more than 1.5 per mile.'], check=-1.5)
K.calc('x', 'Satisficing on the 10 fruit plans (plain version) in the order none, A, O, P, AA, OO, PP, AO, AP, OP with aspiration "save at least 40". Which position is chosen?', '5', 'Stop at the first plan with change ≤ −40.',
       ['Changes in order: 0, −30, −20, −25, −60, −40, −50, −50, −55, −45.', 'The first one at or below −40 is AA in position 5.', eq('Satisficing picks position 5, AA'), 'Here it happens to match the maximizer, but with the variety rule the first good enough plan is AO (−50), not the best AP (−55).'], check=5)

# ---------------------------------------------------------------- assignments
K.assign('argmax', 'e', 'All the best actions',
         '<p>Write <code>best_actions(v)</code> that takes a dictionary from action to value and returns the sorted list of every action that reaches the largest value.</p>',
         '''
def best_actions(v):
    # your code here
    pass
''', [("best_actions({'a1': 5, 'a2': 10, 'a3': 7})", ['a2']), ("best_actions({'x': 3, 'y': 3, 'z': 1})", ['x', 'y']), ("best_actions({'only': -4})", ['only'])],
         '''
def best_actions(v):
    m = max(v.values())
    return sorted(a for a, val in v.items() if val == m)
''', 'Find the maximum first, then keep every action equal to it.', '<p>arg max is a set. The second test shows a tie, where both actions are rational.</p>')
K.assign('trees', 'm', 'The fruit tree planner',
         '<p>Write <code>best_plan(trees, variety)</code>. trees maps a letter to (maintenance, reduction). Plans are none ("") and every multiset of one or two trees, written as sorted letters such as "AP". With variety True, a second tree of the same kind saves half. Return (plan, change) for the lowest change, with change rounded to 2 decimals.</p>',
         '''
def best_plan(trees, variety):
    # your code here
    pass
''', [("best_plan({'A': (100, 130), 'O': (70, 90), 'P': (120, 145)}, False)", ['AA', -60]),
      ("best_plan({'A': (100, 130), 'O': (70, 90), 'P': (120, 145)}, True)", ['AP', -55]),
      ("best_plan({'X': (50, 40)}, False)", ['', 0])],
         '''
from itertools import combinations_with_replacement

def best_plan(trees, variety):
    plans = [""] + ["".join(p) for k in (1, 2) for p in combinations_with_replacement(sorted(trees), k)]
    def change(plan):
        total = 0
        for i, t in enumerate(plan):
            cost, save = trees[t]
            if variety and t in plan[:i]:
                save = save / 2
            total += cost - save
        return round(total, 2)
    best = min(plans, key=change)
    return [best, change(best)]
''', 'Use itertools.combinations_with_replacement for the pairs and remember the empty plan.',
         '<p>The third test has a tree that costs more than it saves, so planting nothing is best.</p>')

K.must('Rational choice', 'v(a) = u(c(a)). a* ∈ arg max v, i.e. v(a*) ≥ v(a) for all a. Ties are all rational.')
K.must('Movie tree', 'Utilities 6 to 1, minus 1 per mile. INOX 1 mile, PVR 3. Best: INOX Aliens, net 5.')
K.must('Fruit trees 1.6', 'Plain: AA at X − 60. Second same tree saves half: AA, OO become X + 5, PP X + 22.5, best AP at X − 55.')
K.must('Parks 1.7', 'v = √(400c) − c/80 gives √c = 800, c* = 640,000 under the 1,000,000 cap. With √(1600c) the peak 2,560,000 is infeasible, so c* = 1,000,000.')
K.must('Other ideas', 'Satisficing picks the first v ≥ T. Minimizing loss = maximizing −loss. Check feasibility and boundaries.')

T = K.topic(
    slug='choosing-best-action', topic='choosing-best-action', step=(1, 'Rational choice', 'aai-choice', 'Turn choice into mathematics: preferences, utility functions and picking the best action when outcomes are certain.', 'School and college'),
    title='Choosing the best action', short='Best action', badge='1.3', minutes=50,
    lead='Put preferences to work: solve the movie decision tree, the fruit tree problem 1.6 and the city parks problem 1.7, and learn when the best choice sits at a boundary.',
    desc='The rational individual, arg max and ties, maximizing against satisficing, loss as negative utility, decision trees with the INOX and PVR movie example, problem 1.6 with and without variety, problem 1.7 with calculus, concavity and the corner solution.',
    summary='Rational choice as arg max, decision trees, the movie, fruit tree and city park problems, and constrained optimization on an interval.',
    keywords=['rational choice', 'arg max', 'decision tree', 'problem 1.6', 'problem 1.7', 'corner solution', 'satisficing', 'optimization'],
    recap='<p>Score each action by its outcome and pick the highest. With few actions, list them or draw a tree. With a continuum, set the derivative to zero and then check the result is allowed.</p>')
