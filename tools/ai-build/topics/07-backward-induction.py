# Chapter 3.1: backward induction. Source: lecture 4 (the R&D then marketing tree: success 0.625, market 0.9 or 0.5,
# marketing payoffs 13 or -7, no marketing 9 or -1, skip 10 or 0 at 0.5; backward induction steps giving 11 and 4 then
# 8.375 against 5; the cross check over the four full strategies MM 8.0, MD 8.375, DM 6.125, DD 6.5; why never to
# compare raw payoffs at a nature node; the vaccine trial signal; practice problem A, the film studio, 7.98 against 3.5).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('fold', r'''
# Backward induction on a tree. A node is ("chance", [(p, child)]), ("choice", {action: child}) or a number
def solve(node, name="root"):
    if isinstance(node, (int, float)):
        return node, {}
    kind, kids = node
    if kind == "chance":
        value, plan = 0, {}
        for p, child in kids:
            v, sub = solve(child, name)
            value += p * v
            plan.update(sub)
        return value, plan
    best = None
    for action, child in kids.items():
        v, sub = solve(child, name + "/" + action)
        if best is None or v > best[0]:
            best = (v, {**sub, name: action})
    return best

market = lambda good, bad, p: ("chance", [(p, good), (1 - p, bad)])
after = lambda p: ("choice", {"m": market(13, -7, p), "d": market(9, -1, p)})
tree = ("choice", {"g": ("chance", [(0.625, ("choice", {"m": market(13, -7, 0.9), "d": market(9, -1, 0.9)})),
                                    (0.375, after(0.5))]),
                   "s": market(10, 0, 0.5)})
value, plan = solve(tree)
print("value:", round(value, 3))
print("plan :", plan)
''')

K.code('strategies', r'''
# The cross check: list every full strategy and compute its expected payoff
from itertools import product
succ = {"M": 0.9 * 13 + 0.1 * -7, "D": 0.9 * 9 + 0.1 * -1}     # 11 and 8
fail = {"M": 0.5 * 13 + 0.5 * -7, "D": 0.5 * 9 + 0.5 * -1}     # 3 and 4
for a, b in product("MD", repeat=2):
    print(f"go, then {a} after success and {b} after failure: {0.625 * succ[a] + 0.375 * fail[b]:.3f}")
print("skip:", 0.5 * 10 + 0.5 * 0)
''')

K.lesson('idea', 'Decisions that unfold over time', f'''
<p>In chapter 2.2 the firm chose once, at the start. Lecture 4 adds a second choice later. After it learns whether research worked, the firm decides whether to spend on a marketing campaign. Because the second decision can depend on what has already happened, the firm can react to news. That is what makes this a decision over time.</p>
{table(['Path', 'Then', 'Payoffs'], [
    ['Skip research (s)', 'Nature picks the market', '10 or 0, each with 0.5'],
    ['Go for research (g), success with 0.625', 'Choose marketing m or not d, then the market is good with 0.9', 'm: 13 or −7, d: 9 or −1'],
    ['Go for research (g), failure with 0.375', 'Choose m or d, then the market is good with 0.5', 'm: 13 or −7, d: 9 or −1']])}
{fxs(
    fx('Backward induction', 'start at the last decision, replace each chance node by its expected value, keep the best action at each decision node, and move one level back', 'Repeat until you reach the root.', key=True),
    fx('At a chance node', 'V(<i>n</i>) = ∑<sub><i>k</i></sub> <i>p</i><sub><i>k</i></sub> V(child<sub><i>k</i></sub>)', 'Nature moves, so you average.'),
    fx('At a decision node', 'V(<i>n</i>) = max<sub><i>a</i></sub> V(child<sub><i>a</i></sub>)', 'You move, so you take the best.'))}
{viz('backind')}
''', kw=['decision over time', 'sequential decision', 'R&D', 'marketing', 'decision tree', 'backward induction'])

K.lesson('solve', 'Solving the R&D and marketing tree', f'''
{steps('Backward induction, exactly as in class', [
    'After success: E[m] = 0.9 × 13 + 0.1 × (−7) = 11 and E[d] = 0.9 × 9 + 0.1 × (−1) = 8. Market, and carry 11 back.',
    'After failure: E[m] = 0.5 × 13 + 0.5 × (−7) = 3 and E[d] = 0.5 × 9 + 0.5 × (−1) = 4. Do not market, and carry 4 back.',
    'Research chance node: 0.625 × 11 + 0.375 × 4 = 6.875 + 1.5 = 8.375.',
    'Skip: 0.5 × 10 + 0.5 × 0 = 5.',
    eq('8.375 &gt; 5: go for research, market only if it succeeds')])}
{code('fold')}
{note('Never compare raw leaf payoffs where nature moves. 13 is not "better than" −7 in any useful sense at a chance node, because the firm does not choose between them. Convert every chance node to its expected value first, and compare only at nodes where the firm chooses.', 'warn')}
<h3>The cross check: list every full strategy</h3>
<p>A strategy is a complete plan that says what to do at every point you might reach, even points you will not reach. Here a strategy says what to do after success and what to do after failure.</p>
{table(['After success, after failure', 'Expected payoff'], [
    ['M, M (always market)', '0.625 × 11 + 0.375 × 3 = 8.000'],
    ['M, D (market only after success)', '0.625 × 11 + 0.375 × 4 = 8.375, the best'],
    ['D, M (market only after failure)', '0.625 × 8 + 0.375 × 3 = 6.125'],
    ['D, D (never market)', '0.625 × 8 + 0.375 × 4 = 6.500']])}
{code('strategies')}
<p>Both methods give 8.375. The professor\'s point was about effort. With k binary decision nodes there are 2<sup>k</sup> full strategies, and listing them quickly becomes hopeless. Backward induction visits each node once.</p>
{scene('a vaccine maker', '<p>How does a firm know research has succeeded? A vaccine maker learns it from clinical trial results. That observable signal is what lets the marketing decision depend on the trial. Planning "if the trial works we launch a big campaign, if not we keep it small" is exactly the M, D strategy.</p>')}
''', kw=['backward induction', 'expected value', 'strategy', 'full plan', 'cross check', 'enumeration', '8.375'])

K.lesson('practice', 'Practice problem A: the film studio', f'''
<p>A studio picks a big or a small budget. With a big budget, nature sets the audience buzz: good with 0.4, weak with 0.6. After seeing the buzz the studio decides whether to push extra marketing. A small budget gives 6 or 1 with equal chance.</p>
{table(['Buzz', 'Push: success chance, payoffs', 'No push: payoffs'], [
    ['Good (0.4)', '0.8: 18 or 0', '0.8: 14 or 2'],
    ['Weak (0.6)', '0.3: 18 or −4', '0.3: 10 or 1']])}
{steps('Fold the tree back', [
    'Good buzz: push 0.8 × 18 + 0.2 × 0 = 14.4, no push 0.8 × 14 + 0.2 × 2 = 11.6. Push, value 14.4.',
    'Weak buzz: push 0.3 × 18 + 0.7 × (−4) = 2.6, no push 0.3 × 10 + 0.7 × 1 = 3.7. Hold back, value 3.7.',
    'Big budget: 0.4 × 14.4 + 0.6 × 3.7 = 5.76 + 2.22 = 7.98.',
    'Small budget: 0.5 × 6 + 0.5 × 1 = 3.5.',
    eq('Choose the big budget, push only on good buzz, value 7.98')])}
{deep('Why backward induction is correct: the principle of optimality', '<p>Bellman\'s principle says that whatever the first decision, the rest of an optimal plan must be optimal for the situation that decision creates. Suppose the best plan used a sub plan that was not best from some node. Replacing it by the better sub plan raises the value of that node without changing the probability of reaching it, so the whole plan improves, which is a contradiction. Backward induction applies this from the leaves upward. Its cost is linear in the size of the tree, while listing strategies is exponential in the number of decision nodes.</p>')}
{ladder(
    '<p>Plan from the end. Ask what you would do at the last step in each situation, then use those answers to decide the step before, and so on back to today.</p>',
    '<p>Average at chance nodes, take the max at decision nodes, and fold from the leaves to the root. A strategy is a full contingent plan. The R&D tree gives 8.375 by both folding and listing the four strategies.</p>',
    '<p>Backward induction is dynamic programming on a finite tree and rests on Bellman\'s principle of optimality. In games it gives subgame perfect equilibria. With shared sub states the tree becomes a graph and memoisation turns exponential work into polynomial work.</p>',
    '<p>Markov decision processes generalize the tree to cycles and infinite horizons, solved by value iteration V(s) = max<sub>a</sub> Σ P(s′ | s, a)[r + γ V(s′)]. Monte Carlo tree search, as in AlphaGo, estimates the same backups by sampling when the tree is too large to fold exactly.</p>')}
''', kw=['practice problem A', 'film studio', 'principle of optimality', 'Bellman', 'dynamic programming', 'MDP'])


K.lesson('levels', 'From intuition to research', f'''
<p>Backward induction solves plans that unfold over time by starting at the end. It is the idea behind dynamic programming and much of reinforcement learning.</p>
{scene('planning revision for an exam', '<p>With the exam on Friday, decide first what Thursday must cover, then what Wednesday must cover to make Thursday possible, and so on back to today. A chess player solving an endgame works the same way: from the checkmate position back to the current move.</p>')}
{steps('Work it out: invest 10 now, then launch or sell', ['After a good market (0.6): launch earns 50, selling earns 20. Choose launch, 50.', 'After a bad market (0.4): launch earns −10, selling earns 5. Choose sell, 5.', 'Value of investing: 0.6 × 50 + 0.4 × 5 − 10 = 30 + 2 − 10 = 22.', eq('22 > 0, so invest, then launch if good and sell if bad')])}
{deep('the analysis', '<p>Bellman’s principle of optimality: whatever the first decision, the remaining decisions must be optimal for the situation it creates. In equations V<sub>t</sub>(s) = max<sub>a</sub>(r(s, a) + E[V<sub>t+1</sub>(s′)]). Decision nodes take a maximum, chance nodes take an expectation, and the work grows with the number of states rather than with the number of complete plans.</p>')}
{deep('the research view', '<p>Zermelo (1913) used backward induction to show that chess is determined: either White can force a win, Black can, or both can force a draw. Nobody knows which, because the tree is too large. AlphaZero approximates the backed-up values with a neural network and tree search, which is backward induction at scale.</p>')}
{note('At chance nodes average with the probabilities. Taking the maximum there assumes luck always goes your way.', 'warn')}
''', kw=['backward induction', 'Bellman equation', 'dynamic programming', 'Zermelo', 'AlphaZero'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Backward induction starts at', ['The root', 'The last decision', 'The most likely leaf', 'The largest payoff'], 1,
       'Backward.', 'Begin where the player last acts, then move toward the first decision.')
K.quiz('e', 'At a chance node you', ['Take the maximum', 'Take the expected value', 'Take the minimum', 'Ignore it'], 1,
       'Nature moves.', 'Average the children by their probabilities.')
K.quiz('e', 'At a decision node you', ['Take the maximum', 'Average', 'Pick at random', 'Take the minimum'], 0,
       'You move.', 'Keep the action with the larger value.')
K.quiz('e', 'In the R&D tree, after success the firm should', ['Market (m)', 'Not market (d)', 'Abandon', 'Indifferent'], 0,
       '11 against 8.', 'E[m | success] = 11 > E[d | success] = 8.')
K.quiz('m', 'After failure the firm should', ['Market', 'Not market', 'Indifferent', 'Restart research'], 1,
       '3 against 4.', 'E[m | failure] = 3 < E[d | failure] = 4.')
K.quiz('m', 'The value of going for research is', ['8', '8.375', '6.5', '11'], 1,
       '0.625 × 11 + 0.375 × 4.', '6.875 + 1.5 = 8.375.')
K.quiz('m', 'A full strategy in the R&D tree specifies', ['Only the first move', 'What to do after success and after failure', 'Only the marketing choice', 'Nature\'s moves'], 1,
       'A complete contingent plan.', 'It says what to do at every decision node, even one that may not be reached.')
K.quiz('m', 'Which full strategy gives 6.125?', ['M, M', 'M, D', 'D, M', 'D, D'], 2,
       '0.625 × 8 + 0.375 × 3.', 'Never marketing after success but marketing after failure is the worst plan.')
K.quiz('h', 'Why must you not compare 13 and −7 directly in the R&D tree?', ['They are equal', 'Nature, not the firm, chooses between them, so only their expectation matters', 'They are negative', 'The tree is wrong'], 1,
       'Who moves there?', 'Only decision nodes involve choosing. Chance nodes are summarized by expectation.')
K.quiz('h', 'With k binary decision nodes, how many full strategies can there be?', ['k', '2k', '2^k', 'k!'], 2,
       'Two choices at each.', 'Each node has 2 options, giving 2^k combinations.')
K.quiz('x', 'Backward induction is correct because of', ['The law of large numbers', 'Bellman\'s principle of optimality', 'Jensen\'s inequality', 'The central limit theorem'], 1,
       'Optimal plans have optimal tails.', 'Any part of an optimal plan must be optimal from where it starts, so solving from the end is safe.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'R&D tree: what is E[m | success]?', '11', '0.9 × 13 + 0.1 × (−7).',
       ['0.9 × 13 = 11.7.', '0.1 × (−7) = −0.7.', eq('11.7 − 0.7 = 11')], check=11)
K.calc('e', 'R&D tree: what is E[d | failure]?', '4', '0.5 × 9 + 0.5 × (−1).',
       ['0.5 × 9 = 4.5.', '0.5 × (−1) = −0.5.', eq('4.5 − 0.5 = 4')], check=4)
K.calc('e', 'What is the value of skipping research?', '5', '0.5 × 10 + 0.5 × 0.',
       ['Good market pays 10 with 0.5.', 'Bad pays 0 with 0.5.', eq('E = 5')], check=5)
K.calc('m', 'What is the value of going for research with the optimal follow up?', '8.375', 'Fold back 11 and 4.',
       ['After success carry 11, after failure carry 4.', '0.625 × 11 = 6.875 and 0.375 × 4 = 1.5.', eq('V(g) = 8.375')], check=8.375)
K.calc('m', 'What is the expected payoff of the full strategy "always market" (M, M)?', '8', 'Use 11 and 3.',
       ['After success m gives 11.', 'After failure m gives 3.', eq('0.625 × 11 + 0.375 × 3 = 6.875 + 1.125 = 8')], check=8)
K.calc('m', 'Practice A: what is the value of good buzz?', '14.4', 'Compare push and no push.',
       ['Push: 0.8 × 18 + 0.2 × 0 = 14.4.', 'No push: 0.8 × 14 + 0.2 × 2 = 11.6.', eq('max = 14.4')], check=14.4)
K.calc('m', 'Practice A: what is the value of the big budget?', '7.98', 'Weak buzz is worth 3.7.',
       ['Weak buzz: push 2.6, no push 3.7, so 3.7.', '0.4 × 14.4 = 5.76 and 0.6 × 3.7 = 2.22.', eq('V = 7.98')], check=7.98, tol=0.001)
K.calc('h', 'R&D tree: below what P(success) would skipping (5) beat research? Use the optimal follow ups 11 and 4. Four decimals.', '0.1429', 'Solve 11p + 4(1 − p) = 5.',
       ['V(g) = 11p + 4(1 − p) = 4 + 7p.', 'Set 4 + 7p = 5.', eq('p = 1/7 = 0.1429')], check=1 / 7, tol=0.00005)
K.calc('h', 'After success, how low can the marketing payoff in a good market (13) fall before m and d tie? Keep −7 for a bad market.', '9.6667', 'Solve 0.9x − 0.7 = 8.',
       ['E[m | success] = 0.9x + 0.1 × (−7).', 'Tie with E[d | success] = 8 when 0.9x − 0.7 = 8.', eq('x = 8.7 ÷ 0.9 = 9.6667')], check=8.7 / 0.9, tol=0.00005)
K.calc('h', 'How much does the option to react to the research result add, compared with the best fixed plan? Compare M, D with the best of M, M and D, D.', '0.375', '8.375 against 8.',
       ['Best plan that ignores the result: max(8, 6.5) = 8, always market.', 'Best plan that reacts: 8.375.', eq('8.375 − 8 = 0.375')], check=0.375)
K.calc('x', 'A tree has 3 decision stages. At each stage the firm makes a binary choice at each of the 2 outcomes of the previous chance node, and there is 1 node at stage 1. How many full strategies are there?', '128', 'Count decision nodes: 1, 2, 4.',
       ['Stage 1: 1 node. Stage 2: 2 nodes. Stage 3: 4 nodes.', 'Total decision nodes = 7.', eq('Strategies = 2⁷ = 128'), 'Backward induction still visits each of the 7 nodes only once.'], check=128)

# ---------------------------------------------------------------- assignments
K.assign('fold', 'm', 'Fold back a tree',
         '<p>Write <code>value(node)</code>. A node is a number (a leaf), ["chance", [[p, child], ...]] or ["choice", {action: child}]. Return the backward induction value rounded to 4 decimals.</p>',
         '''
def value(node):
    # your code here
    pass
''', [("value(['choice', {'g': ['chance', [[0.625, ['choice', {'m': ['chance', [[0.9, 13], [0.1, -7]]], 'd': ['chance', [[0.9, 9], [0.1, -1]]]}]], [0.375, ['choice', {'m': ['chance', [[0.5, 13], [0.5, -7]]], 'd': ['chance', [[0.5, 9], [0.5, -1]]]}]]]], 's': ['chance', [[0.5, 10], [0.5, 0]]]}])", 8.375),
      ("value(['chance', [[0.5, 6], [0.5, 1]]])", 3.5), ("value(7)", 7)],
         '''
def value(node):
    if isinstance(node, (int, float)):
        return node
    kind, kids = node
    if kind == "chance":
        return round(sum(p * value(c) for p, c in kids), 4)
    return round(max(value(c) for c in kids.values()), 4)
''', 'Recurse: a leaf returns itself, a chance node averages, a choice node takes the max.', '<p>The first test is the lecture 4 tree. The answer 8.375 comes out in a few lines.</p>')
K.assign('plans', 'h', 'Enumerate full strategies',
         '<p>Write <code>best_strategy(succ, fail, ps)</code>. succ and fail map an action ("M" or "D") to its expected payoff after success and after failure. Return [a, b, value] for the plan (a after success, b after failure) with the highest ps × succ[a] + (1 − ps) × fail[b], value rounded to 3 decimals.</p>',
         '''
def best_strategy(succ, fail, ps):
    # your code here
    pass
''', [("best_strategy({'M': 11, 'D': 8}, {'M': 3, 'D': 4}, 0.625)", ['M', 'D', 8.375]),
      ("best_strategy({'M': 14.4, 'D': 11.6}, {'M': 2.6, 'D': 3.7}, 0.4)", ['M', 'D', 7.98])],
         '''
def best_strategy(succ, fail, ps):
    best = None
    for a in succ:
        for b in fail:
            v = round(ps * succ[a] + (1 - ps) * fail[b], 3)
            if best is None or v > best[2]:
                best = [a, b, v]
    return best
''', 'Two nested loops over the actions, keeping the best.', '<p>The second test is practice problem A with good buzz as "success".</p>')

K.must('Method', 'From the last decision back: chance node = Σ p × value, decision node = max. Never compare raw leaves at a chance node.')
K.must('R&D tree', 'Success: m 11 > d 8. Failure: m 3 < d 4. Go = 0.625 × 11 + 0.375 × 4 = 8.375 > skip 5.')
K.must('Full strategies', 'MM 8.0, MD 8.375, DM 6.125, DD 6.5. Same answer as folding, but 2ᵏ plans for k binary nodes.')
K.must('Practice A', 'Good buzz push 14.4, weak buzz hold 3.7, big budget 7.98 > small 3.5.')
K.must('Why it works', 'Bellman\'s principle of optimality: each tail of an optimal plan is optimal. Folding is linear in the tree size.')

T = K.topic(
    slug='backward-induction', topic='backward-induction', step=(3, 'Decisions over time', 'aai-time', 'Plan several moves ahead: backward induction, discounting, consumption over time and the value of information.', 'College and masters'),
    title='Backward induction', short='Backward induction', badge='3.1', minutes=40,
    lead='Solve a decision that unfolds in stages by folding the tree from the end, check it against every full strategy, and see why it scales when listing plans does not.',
    desc='Decisions over time, the R&D then marketing tree from lecture 4, backward induction step by step, why chance nodes are averaged, full strategies and the four plan cross check, practice problem A, and the principle of optimality.',
    summary='Backward induction on the R&D and marketing tree, full strategies, the film studio problem and Bellman\'s principle.',
    keywords=['backward induction', 'decision tree', 'strategy', 'dynamic programming', 'principle of optimality', 'R&D', 'expected value'],
    recap='<p>Solve from the end. Average where nature moves and take the best where you move. The R&D tree is worth 8.375 when you market only after success.</p>')
