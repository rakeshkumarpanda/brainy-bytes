# Chapter 6.2: alpha beta pruning. Source: slide Set 3, slides 7 to 10 (alpha and beta values, parent to child and
# child to parent rules, prune when alpha >= beta, the worked example with leaves 2 3 5 9 0 1 7 5, and food for
# thought on complexity, data structures, applications and utility functions) and the class of 8 February 2026
# (node arrangement matters, thresholds). Move ordering and the best case bound follow Knuth and Moore, "An analysis
# of alpha-beta pruning", Artificial Intelligence 6, 1975, and Russell and Norvig, AIMA 4th ed., section 5.3.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('slide', r'''
# Alpha beta pruning on the example of the slides. A is MAX, B and C are MIN, D, E, F, G are MAX.
tree = [[[2, 3], [5, 9]],          # B has D = [2, 3] and E = [5, 9]
        [[0, 1], [7, 5]]]          # C has F = [0, 1] and G = [7, 5]
big = 1000                          # stands for infinity

def alphabeta(node, is_max, alpha, beta):
    if type(node) == int:
        print("read leaf", node)
        return node
    if is_max:
        value = -big
        for child in node:
            value = max(value, alphabeta(child, False, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                print("  prune at a MAX node: alpha", alpha, ">= beta", beta)
                break
        return value
    value = big
    for child in node:
        value = min(value, alphabeta(child, True, alpha, beta))
        beta = min(beta, value)
        if alpha >= beta:
            print("  prune at a MIN node: alpha", alpha, ">= beta", beta)
            break
    return value

print("A =", alphabeta(tree, True, -big, big))
''')

K.code('order', r'''
# The same values in two different orders. Alpha beta gives the same answer, but reads a different number of leaves.
big = 1000
count = [0]                         # a list, so the function can change it

def alphabeta(node, is_max, alpha, beta):
    if type(node) == int:
        count[0] = count[0] + 1
        return node
    value = -big if is_max else big
    for child in node:
        v = alphabeta(child, not is_max, alpha, beta)
        if is_max:
            value = max(value, v)
            alpha = max(alpha, value)
        else:
            value = min(value, v)
            beta = min(beta, value)
        if alpha >= beta:
            break
    return value

good = [[[2, 3], [5, 9]], [[0, 1], [7, 5]]]       # the slide order
bad = [[[5, 7], [0, 1]], [[5, 9], [2, 3]]]        # each node sees its worst child first
for name, tree in [("slide order", good), ("worst order", bad)]:
    count[0] = 0
    v = alphabeta(tree, True, -big, big)
    print(name, ": value", v, ", leaves read", count[0], "of 8")
''')

K.lesson('idea', 'Why we can skip parts of the tree', f'''
{src('slide Set 3, slide 7, and the class of 8 February 2026.')}
{wwh('Alpha beta pruning is minimax with two extra numbers, α and β, that let it skip branches which cannot change the final decision. It always returns the same root value as minimax.',
     'Minimax looks at every leaf, and the tree grows as b<sup>m</sup>. Often one look at a branch already shows that a player will never let the game go there. Reading the rest of that branch is wasted work.',
     'Search depth first, as minimax does. Carry α (the best value MAX can already guarantee on the path, a lower bound) and β (the best value MIN can already guarantee, an upper bound) down to the children. Send node values back up and update α at MAX nodes and β at MIN nodes. As soon as α ≥ β at a node, stop looking at its remaining children.')}
{table(['Value (slide 7)', 'Meaning', 'Starts at', 'Changed at'], [
    ['α', 'The highest value MAX can guarantee so far on the path to this node. A lower bound', '−∞', 'MAX nodes: α = max(α, value)'],
    ['β', 'The lowest value MIN can guarantee so far on the path to this node. An upper bound', '+∞', 'MIN nodes: β = min(β, value)']])}
{table(['Direction (slide 7)', 'What moves'], [
    ['Parent to child', 'The current α and β values'],
    ['Child to parent', 'The node value, which then updates α (at a MAX parent) or β (at a MIN parent)']])}
<p>The rule to prune: if at any point α ≥ β, the current branch cannot affect the final decision, because the opponent will avoid this path for a better one. So the branch is pruned and the search moves to the next branch.</p>
{note('The slide text says "the initial value of alpha is +∞" in the line about beta. That is a typing slip: it is β that starts at +∞, and α starts at −∞.', 'warn')}
''', kw=['alpha beta pruning', 'alpha', 'beta', 'lower bound', 'upper bound', 'prune', 'alpha greater or equal beta'])

K.lesson('example', 'The worked example of the slides', f'''
{src('slide Set 3, slides 8 and 9.')}
<p>A is MAX. Its children B and C are MIN. Their children D, E (under B) and F, G (under C) are MAX. The leaves are 2, 3 (under D), 5, 9 (under E), 0, 1 (under F) and 7, 5 (under G). In the animation the same nodes are called B1, B2 and C1 to C4.</p>
{steps('Step by step', [
    'Start at A with α = −∞ and β = +∞. Pass them down to B and then to D.',
    'D is MAX. It reads 2 (α = 2), then 3 (α = 3). D = 3. Send 3 up to B.',
    'B is MIN: β = min(+∞, 3) = 3. Pass α = −∞ and β = 3 down to E.',
    'E is MAX. It reads 5, so α = 5. Now α = 5 ≥ β = 3. MIN at B already has 3 and will never let play reach E, whatever the 9 is. <b>Prune the 9.</b> E = 5 (at least 5).',
    'B = min(3, 5) = 3. Send 3 up to A: α = max(−∞, 3) = 3.',
    'Pass α = 3 and β = +∞ down to C, then to F. F reads 0, then 1. F = 1.',
    'C is MIN: β = min(+∞, 1) = 1. Now α = 3 ≥ β = 1. MAX at A already has 3 and C can give at most 1. <b>Prune the whole of G</b> (7 and 5).',
    eq('A = max(3, 1) = 3, the same as minimax, after reading only 5 of the 8 leaves')])}
{viz('gametree', mode='ab', pat='mm3', b=2, leaves='2 3 5 9 0 1 7 5')}
{code('slide')}
{note('A pruned node gets a bound, not an exact value: E is "at least 5" and C is "at most 1". These bounds are enough to choose the move, which is all we need at the root.', 'exam')}
''', kw=['alpha beta example', 'slide example', 'prune leaf 9', 'prune subtree G'])

K.lesson('algo', 'The algorithm', f'''
{algo('ALPHA-BETA-SEARCH', [
    'function ALPHA-BETA-SEARCH(state):',
    '    v = MAX-VALUE(state, −∞, +∞)',
    '    return the action in ACTIONS(state) whose child has value v',
    '',
    'function MAX-VALUE(state, α, β):',
    '    if TERMINAL-TEST(state): return UTILITY(state)',
    '    v = −∞',
    '    for each a in ACTIONS(state):',
    '        v = max(v, MIN-VALUE(RESULT(state, a), α, β))',
    '        if v ≥ β: return v          (prune: MIN above will not allow this)',
    '        α = max(α, v)',
    '    return v',
    '',
    'function MIN-VALUE(state, α, β):',
    '    if TERMINAL-TEST(state): return UTILITY(state)',
    '    v = +∞',
    '    for each a in ACTIONS(state):',
    '        v = min(v, MAX-VALUE(RESULT(state, a), α, β))',
    '        if v ≤ α: return v          (prune: MAX above will not allow this)',
    '        β = min(β, v)',
    '    return v'])}
<p>The test "v ≥ β" at a MAX node is the same as "α ≥ β" after updating α, so the slide rule and this code agree. Our Python code uses the slide form.</p>
{table(['Property', 'Alpha beta'], [
    ['Same answer as minimax', 'Yes, always, at the root. Pruning never changes the decision'],
    ['Complete and optimal', 'Same as minimax: complete for finite trees, optimal against a perfect opponent'],
    ['Time, best order', 'O(b<sup>m/2</sup>)'],
    ['Time, random order', 'About O(b<sup>3m/4</sup>) for moderate b'],
    ['Time, worst order', 'O(b<sup>m</sup>), no pruning at all'],
    ['Space', 'O(b m), like depth first minimax. Only the current path and its α, β values are stored'],
    ['Data structures', 'The recursion stack. Each frame holds a state, its list of moves, v, α and β. Real programs add a transposition table (a hash map of positions already searched)']])}
''', kw=['alpha beta algorithm', 'max value', 'min value', 'complexity', 'data structures'])

K.lesson('ordering', 'Move ordering decides how much is pruned', f'''
{src('the class of 8 February 2026 ("arrangement of nodes also matter") and Knuth and Moore, 1975.')}
<p>Alpha beta prunes most when each node looks at its best child first. Then α and β get tight early and many later children fail the test at once. If the worst child always comes first, nothing is pruned.</p>
{table(['Tree', 'Leaves', 'Read by alpha beta', 'Pruned'], [
    ['Slide example, slide order (b = 2, depth 3)', '8', '5', '3'],
    ['Same values, worst order', '8', '8', '0'],
    ['27 leaf slide tree, slide order (b = 3, depth 3)', '27', '11', '16'],
    ['Same 27 values, worst order', '27', '27', '0']])}
<p>Both slide trees are already in the best possible order: no order can read fewer leaves. We checked this by running alpha beta on every tree, and it matches the formula below.</p>
{fxs(fx('Fewest leaves alpha beta can read (Knuth and Moore)', 'b<sup>⌈d/2⌉</sup> + b<sup>⌊d/2⌋</sup> − 1', 'For a uniform tree with branching b and depth d, with perfect ordering. b = 2, d = 3: 4 + 2 − 1 = 5. b = 3, d = 3: 9 + 3 − 1 = 11.', key=True))}
{viz('gametree', mode='ab', pat='mm3', b=3, leaves='10 11 12 2 3 4 1 1 2 1 6 11 1 2 5 1 2 3 2 6 11 1 5 8 1 2 5')}
{code('order')}
{table(['How real programs get a good order', 'Idea'], [
    ['Iterative deepening', 'Search depth 1, 2, 3 and so on. The best move found at depth d − 1 is tried first at depth d'],
    ['Killer moves', 'A move that caused a prune at the same depth elsewhere is tried early, since it is likely good again'],
    ['Captures first', 'In chess, try captures and threats before quiet moves'],
    ['Transposition table', 'Store each searched position with its value and best move, so a position reached by a different move order is not searched twice']])}
''', kw=['move ordering', 'best case', 'worst case', 'Knuth Moore', 'killer moves', 'iterative deepening', 'transposition table'])

K.lesson('maths', 'The maths: how much faster, and how much deeper', f'''
{fxs(
    fx('Best order cost', 'O(b<sup>m/2</sup>) = O((√b)<sup>m</sup>)', 'The effective branching factor drops from b to √b. Chess: √35 ≈ 5.9.', key=True),
    fx('Depth for the same work', 'b<sup>d</sup> = (√b)<sup>2d</sup>', 'In the time minimax searches depth d, alpha beta with good ordering searches depth 2d.'),
    fx('Random order cost', 'about O(b<sup>3m/4</sup>)', 'Still a big saving: the depth grows by about a third.'),
    fx('Negamax form', 'max(a, b) = −min(−a, −b)', 'So one function can serve both players: value = max over children of −value(child), with the window (−β, −α).'))}
{steps('Worked example: chess', [
    'Say a computer can look at 10⁹ positions per move. With b = 35, minimax reaches depth d where 35<sup>d</sup> = 10⁹.',
    'd = 9 ⁄ log₁₀ 35 = 9 ⁄ 1.544 ≈ 5.8, so about 5 to 6 plies.',
    'Alpha beta with near perfect ordering: (√35)<sup>d</sup> = 10⁹ gives d ≈ 11.7.',
    eq('about twice as deep: roughly 11 plies instead of 5 or 6')])}
{steps('Worked example: the best case formula for b = 10, d = 4', [
    'b<sup>⌈d/2⌉</sup> = 10² = 100.',
    'b<sup>⌊d/2⌋</sup> = 10² = 100.',
    '100 + 100 − 1 = 199 leaves.',
    eq('199 instead of 10⁴ = 10,000 leaves, about 50 times fewer')])}
{deep('Why the best case is b<sup>⌈d/2⌉</sup> + b<sup>⌊d/2⌋</sup> − 1', '<p>To prove that the root value is v, MAX must show "I can get at least v" and "I cannot get more than v". For the first, MAX needs only one good move at each of its levels, but all of MIN\'s replies. For the second, MIN needs one good reply at each of its levels, but all of MAX\'s moves. So one proof tree branches only at MIN levels (about b<sup>⌊d/2⌋</sup> leaves), the other only at MAX levels (about b<sup>⌈d/2⌉</sup> leaves). They share one leaf, the principal variation, which gives the −1. With perfect ordering alpha beta reads exactly these leaves and no more.</p>')}
''', kw=['effective branching factor', 'square root of b', 'double the depth', 'negamax', 'minimal tree'])

K.lesson('food', 'Food for thought from the slides', f'''
{src('slide Set 3, slide 10.')}
{table(['Question (slide 10)', 'Answer'], [
    ['Time and space complexity', 'Time O(b<sup>m/2</sup>) with best ordering, about O(b<sup>3m/4</sup>) with random ordering, O(b<sup>m</sup>) in the worst case. Space O(b m)'],
    ['Data structures', 'A recursion stack with α and β per frame, a move list per level, and in practice a hash table of positions (transposition table) and a small table of killer moves per depth'],
    ['Real life uses', 'Chess, checkers, Othello and Connect Four engines. Adversarial planning such as security patrols, where the attacker answers the defender. Puzzle game AI in mobile apps'],
    ['Utility functions', 'Chess: material, king safety, mobility, pawn structure, weighted and added. Connect Four: number of open lines of 2 and 3. Security: value of each target minus the cost of guarding it']])}
{scene('IBM Deep Blue, 1997', '<p>Deep Blue beat the world chess champion Garry Kasparov in 1997. It used alpha beta search on special chess chips that could examine about 200 million positions a second, with a hand written evaluation of about 8,000 features. Today Stockfish still uses alpha beta (in the form called principal variation search), now with a neural network evaluation called NNUE. Alpha beta is the reason chess programs became strong long before deep learning.</p>')}
{note('In class we noted that when the order of nodes is poor, or when you add your own thresholds to prune more, you may cut away a good move. Plain alpha beta never does that: its pruning is exact. Only extra rules such as forward pruning or chance thresholds can lose the best move.', 'tip')}
''', kw=['food for thought', 'Deep Blue', 'Stockfish', 'principal variation search', 'utility function'])

K.lesson('compare', 'Alpha beta against other game search methods', f'''
{versus('Searching a game tree', ['', 'Minimax', 'Alpha beta', 'Depth limited alpha beta', 'Monte Carlo tree search (6.3)'], [
    ['Same answer as full minimax', 'Yes', 'Yes', 'Only as good as EVAL', 'Approaches it with many rollouts'],
    ['Leaves read', 'All b<sup>m</sup>', 'b<sup>m/2</sup> to b<sup>m</sup>, depends on order', 'b<sup>d/2</sup> to b<sup>d</sup> for depth d', 'Chosen by statistics, not by depth'],
    ['Needs an evaluation function', 'No (full tree)', 'No (full tree)', 'Yes', 'No, uses random playouts'],
    ['Good for', 'Tiny games', 'Small to medium games', 'Chess, checkers', 'Go, games with b in the hundreds'],
    ['Handles chance', 'No', 'No', 'No', 'Yes, naturally']],
    'alpha beta is free speed: same answer as minimax, often twice the depth. Use it for any two player zero sum game with a good evaluation function, and switch to Monte Carlo tree search when b is huge or no good evaluation exists.')}
{table(['Improvement', 'What it adds'], [
    ['Aspiration windows', 'Start with a narrow window [v − δ, v + δ] around the last value instead of [−∞, +∞]. More prunes, research if the result falls outside'],
    ['Principal variation search (NegaScout)', 'Search the first move with the full window, the rest with a zero width window to prove they are worse. Research only when the proof fails'],
    ['Null move pruning', 'Let the opponent move twice. If MAX is still above β, the real position is surely good enough, so prune'],
    ['Transposition tables', 'Reuse values of positions already seen through another move order']])}
''', kw=['comparison', 'aspiration window', 'principal variation search', 'NegaScout', 'null move'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>If one reply already shows that a move is worse than a move you have, you do not need to check the other replies to that move. Alpha beta is minimax with this common sense built in.</p>',
    '<p>α is the best MAX can force so far, β the best MIN can force so far. They pass down, values pass up, and a branch is pruned when α ≥ β. The root value equals minimax. Time is O(b<sup>m/2</sup>) with best ordering, about O(b<sup>3m/4</sup>) with random ordering, and O(b<sup>m</sup>) in the worst case.</p>',
    '<p>Knuth and Moore (1975) proved the minimal tree has b<sup>⌈d/2⌉</sup> + b<sup>⌊d/2⌋</sup> − 1 leaves and that alpha beta reads exactly it with perfect ordering. Pearl (1982) showed alpha beta is asymptotically optimal among game tree search algorithms with random leaf values. Iterative deepening, killer moves and transposition tables get close to the best order in practice.</p>',
    '<p>Research went on with best first methods such as SSS* and MTD(f), which can read fewer leaves than alpha beta by using null windows and memory. Modern engines combine alpha beta with learned evaluation (NNUE) and learned move ordering, and AlphaZero showed a different path with Monte Carlo tree search and deep networks.</p>')}
''', kw=['Knuth and Moore', 'Pearl', 'SSS star', 'MTD(f)', 'NNUE'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'α is the best value MAX can guarantee so far (starts at −∞), β the best value MIN can guarantee so far (starts at +∞).',
    'α and β pass from parent to child. Node values pass from child to parent and update α at MAX nodes and β at MIN nodes.',
    'When α ≥ β, the rest of the branch cannot change the decision, so it is pruned. The root value is always the same as minimax.',
    'Slide example: leaves 2 3 5 9 0 1 7 5. The 9 under E and the whole subtree G are pruned, and A = 3 after reading 5 of 8 leaves.',
    'Good move ordering is key: best case O(b<sup>m/2</sup>), so the same time searches about twice as deep. Worst case O(b<sup>m</sup>).'],
    'chapter 6.3 adds dice and other chance events with expectimax, and Monte Carlo tree search for very large games.')}
{nbcard('alpha-beta', 'Run alpha beta on the slide example, compare the slide order with the worst order, then write alpha beta and a leaf counter yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is the starting value of α?', ['0', '−∞', '+∞', '1'], 1,
       'A lower bound for MAX.', 'α starts at −∞ because MAX has not found anything yet.')
K.quiz('e', 'When does alpha beta prune?', ['When α < β', 'When α ≥ β', 'When α = 0', 'Never'], 1,
       'Slide 7.', 'If α ≥ β, the branch cannot change the decision.')
K.quiz('e', 'Compared with minimax, alpha beta gives at the root', ['A smaller value', 'The same value', 'A bigger value', 'A random value'], 1,
       'Pruning is exact.', 'It skips only branches that cannot change the decision.')
K.quiz('e', 'Which value is updated at a MIN node?', ['α', 'β', 'Both', 'Neither'], 1,
       'MIN lowers the upper bound.', 'β = min(β, value) at MIN nodes.')
K.quiz('m', 'In the slide example, why is the 9 under E never read?', ['It is too big', 'B (MIN) already has 3, and E is already at least 5, so B will never choose E', 'E is a MIN node', 'Leaves are always skipped'], 1,
       'α = 5 ≥ β = 3.', 'Whatever the 9 is, E is at least 5 and B prefers 3.')
K.quiz('m', 'In the slide example, why is the whole subtree G pruned?', ['G has the smallest values', 'A already has 3, and C can give at most 1', 'G is a leaf', 'C is a MAX node'], 1,
       'α = 3 ≥ β = 1 at C.', 'MAX will choose B over C, whatever G holds.')
K.quiz('m', 'With perfect move ordering the time of alpha beta is', ['O(b<sup>m</sup>)', 'O(b<sup>m/2</sup>)', 'O(b m)', 'O(log b<sup>m</sup>)'], 1,
       'Square root.', 'The effective branching factor falls to √b.')
K.quiz('m', 'The space used by alpha beta is', ['O(b<sup>m</sup>)', 'O(b m)', 'O(b<sup>m/2</sup>)', 'O(1)'], 1,
       'Depth first.', 'Only the current path with its α and β values.')
K.quiz('h', 'Which technique helps alpha beta get a good move order?', ['Searching the worst move first', 'Iterative deepening, trying last iteration\'s best move first', 'Random shuffling of moves', 'Removing the evaluation function'], 1,
       'Learn from the shallow search.', 'The best move at depth d − 1 is often the best at depth d.')
K.quiz('h', 'If a node is pruned, what do we know about its value?', ['Its exact value', 'Only a bound, such as "at least 5"', 'Nothing at all', 'That it is 0'], 1,
       'E in the slide example.', 'E is at least 5 and C at most 1. Bounds are enough for the decision.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: a MAX root has two MIN children. The first MIN child has leaves 4, 6. The second MIN child has leaves 3, then 8. Which leaf is pruned?', ['4', '6', '3', '8'], 3,
       'After the first child, α = 4.', 'The second MIN node reads 3, so β = 3 ≤ α = 4: the 8 is pruned.')
K.quiz('x', 'In the style of an MIT 6.034 exam: can alpha beta ever prune at the leftmost path of the tree?', ['Yes, often', 'No, on the leftmost path α = −∞ and β = +∞ come straight from the root, so α ≥ β cannot happen until a sibling has been searched', 'Only at MIN nodes', 'Only with chance nodes'], 1,
       'Look at the first descent.', 'Pruning needs a value already backed up from an earlier sibling branch.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Slide example: D = max(2, 3).', '3', 'D is a MAX node.',
       ['Leaves 2 and 3.', 'The largest.', eq('D = 3')], check=3)
K.calc('e', 'After B returns 3 to A, what is α at A?', '3', 'α = max(−∞, 3).',
       ['A is MAX.', 'α = max(−∞, 3).', eq('α = 3')], check=3)
K.calc('e', 'Fewest leaves alpha beta can read with b = 2 and depth 3: b<sup>⌈d/2⌉</sup> + b<sup>⌊d/2⌋</sup> − 1.', '5', '⌈3/2⌉ = 2, ⌊3/2⌋ = 1.',
       ['2² = 4.', '2¹ = 2.', eq('4 + 2 − 1 = 5, exactly the 5 leaves of the slide example')], check=5)
K.calc('m', 'The same formula for b = 3 and depth 3 (the 27 leaf tree).', '11', '3² + 3¹ − 1.',
       ['3² = 9.', '3¹ = 3.', eq('9 + 3 − 1 = 11')], check=11)
K.calc('m', 'The same formula for b = 10 and depth 4. How many leaves?', '199', '10² + 10² − 1.',
       ['⌈4/2⌉ = ⌊4/2⌋ = 2.', '100 + 100.', eq('200 − 1 = 199 leaves, against 10,000 for minimax')], check=199)
K.calc('m', 'The effective branching factor of chess with perfect ordering: √35. Give 2 decimals.', '5.92', 'Between 5.9 and 6.',
       ['5.9² = 34.81.', '5.92² = 35.05.', eq('√35 ≈ 5.92')], check=5.92, tol=0.01)
K.calc('m', 'Minimax reaches depth 6 in the time limit. About how deep does alpha beta with perfect ordering reach in the same time?', '12', 'b<sup>d</sup> = (√b)<sup>2d</sup>.',
       ['Minimax cost b⁶.', 'Alpha beta cost b<sup>d/2</sup>. Set b<sup>d/2</sup> = b⁶.', eq('d/2 = 6, so d = 12')], check=12)
K.calc('h', 'b = 16 and depth 8. How many times fewer leaves does random order alpha beta read than minimax, using b<sup>3d/4</sup>?', '256', '16⁸ ⁄ 16⁶.',
       ['3 × 8 ⁄ 4 = 6, so alpha beta reads about 16⁶.', '16⁸ ⁄ 16⁶ = 16².', eq('256 times fewer')], check=256)
K.calc('h', 'Chess: 10⁹ positions per move. How deep does minimax reach? 35<sup>d</sup> = 10⁹, log₁₀ 35 ≈ 1.544. Give 1 decimal.', '5.8', 'd = 9 ⁄ 1.544.',
       ['Take log₁₀ of both sides: d × 1.544 = 9.', 'd = 9 ⁄ 1.544.', eq('d ≈ 5.8 plies')], check=5.8, tol=0.05)
K.calc('x', 'In the style of a Berkeley CS188 exam: MAX root, three MIN children with leaves (3, 12, 8), (2, 4, 6), (14, 5, 2), searched left to right. How many leaves does alpha beta read?', '7', 'After the first MIN node, α = 3.',
       ['First MIN node: read 3, 12, 8. Value 3, so α = 3 at the root.', 'Second MIN node: read 2. β = 2 ≤ α = 3, so prune 4 and 6.', 'Third MIN node: read 14 (β = 14), 5 (β = 5), 2 (β = 2). None of these is ≤ 3 until the last leaf, so all three are read.', eq('3 + 1 + 3 = 7 leaves read, root = 3')], check=7)
K.calc('x', 'In the style of a Stanford CS221 problem: the 27 leaf slide tree in the worst order, 10 11 12 2 3 4 1 1 2 1 6 11 1 2 5 1 2 3 2 6 11 1 5 8 1 2 5. How many leaves are pruned?', '0', 'Each node sees its worst child first, so α and β never cross.',
       ['At each MAX node the children come in rising order of value, and at each MIN node in falling order.', 'So every new child improves the bound a little but never enough to cross the other bound.', eq('0 leaves pruned: all 27 are read, root still 5')], check=0)

# ---------------------------------------------------------------- assignments
K.assign('ab', 'e', 'Alpha beta on a nested list tree',
         '<p>Write <code>alphabeta(node, is_max, alpha, beta)</code>. A node is a number (a leaf) or a list of children. Return the same value as minimax, but stop looking at the remaining children of a node as soon as alpha ≥ beta. Use −1000 and 1000 for −∞ and +∞.</p>',
         '''
def alphabeta(node, is_max, alpha, beta):
    # your code here
    pass
''', [("alphabeta([[[2, 3], [5, 9]], [[0, 1], [7, 5]]], True, -1000, 1000)", 3),
      ("alphabeta([[3, 12, 8], [2, 4, 6], [14, 5, 2]], True, -1000, 1000)", 3),
      ("alphabeta([[[2, 1, 5], [6, 2, 11], [8, 5, 1]], [[3, 2, 4], [10, 11, 12], [1, 2, 1]], [[2, 1, 3], [6, 1, 11], [2, 5, 1]]], True, -1000, 1000)", 5),
      ("alphabeta(7, True, -1000, 1000)", 7)],
         '''
def alphabeta(node, is_max, alpha, beta):
    if type(node) == int:
        return node
    if is_max:
        value = -1000
        for child in node:
            value = max(value, alphabeta(child, False, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    value = 1000
    for child in node:
        value = min(value, alphabeta(child, True, alpha, beta))
        beta = min(beta, value)
        if alpha >= beta:
            break
    return value
''', 'Copy minimax, add alpha and beta as inputs, update alpha at MAX nodes and beta at MIN nodes, and break when alpha >= beta.', '<p>The three trees are the slide alpha beta example, the AIMA figure 5.2 tree and the 27 leaf slide minimax tree.</p>')
K.assign('abcount', 'm', 'Count the leaves alpha beta reads',
         '<p>Write <code>count_leaves(tree)</code>. Run alpha beta from a MAX root with −1000 and 1000 and return <code>[value, leaves]</code>, where leaves is how many leaf numbers were actually read.</p>',
         '''
def count_leaves(tree):
    # your code here
    pass
''', [("count_leaves([[[2, 3], [5, 9]], [[0, 1], [7, 5]]])", [3, 5]),
      ("count_leaves([[[5, 7], [0, 1]], [[5, 9], [2, 3]]])", [3, 8]),
      ("count_leaves([[3, 12, 8], [2, 4, 6], [14, 5, 2]])", [3, 7]),
      ("count_leaves([[[2, 1, 5], [6, 2, 11], [8, 5, 1]], [[3, 2, 4], [10, 11, 12], [1, 2, 1]], [[2, 1, 3], [6, 1, 11], [2, 5, 1]]])", [5, 11])],
         '''
def count_leaves(tree):
    count = [0]

    def alphabeta(node, is_max, alpha, beta):
        if type(node) == int:
            count[0] = count[0] + 1
            return node
        value = -1000 if is_max else 1000
        for child in node:
            v = alphabeta(child, not is_max, alpha, beta)
            if is_max:
                value = max(value, v)
                alpha = max(alpha, value)
            else:
                value = min(value, v)
                beta = min(beta, value)
            if alpha >= beta:
                break
        return value

    value = alphabeta(tree, True, -1000, 1000)
    return [value, count[0]]
''', 'Keep the counter in a list so the inner function can change it. Add 1 each time you return a leaf.', '<p>The second test is the slide tree in the worst order: nothing is pruned. The last test is the 27 leaf tree, which is already in the best order: 11 = 3² + 3 − 1.</p>')

K.must('α and β', 'α = best MAX can guarantee so far (starts −∞). β = best MIN can guarantee so far (starts +∞).')
K.must('Rule', 'α, β go parent to child. Values go child to parent. Prune when α ≥ β. Root value = minimax.')
K.must('Slide example', 'Leaves 2 3 5 9 0 1 7 5. Prune the 9 under E and all of G. A = 3 after 5 of 8 leaves.')
K.must('Cost', 'Best O(b<sup>m/2</sup>), random about O(b<sup>3m/4</sup>), worst O(b<sup>m</sup>). Space O(b m). Same time, twice the depth.')
K.must('Ordering', 'Best first: b<sup>⌈d/2⌉</sup> + b<sup>⌊d/2⌋</sup> − 1 leaves. Iterative deepening, killer moves, transposition tables.')

T = K.topic(
    slug='alpha-beta', topic='alpha-beta', step=(6, 'Adversarial search', 'cai-games', 'Search when an opponent moves too: minimax, alpha beta pruning, and games with chance.', 'College'),
    title='Alpha beta pruning', short='Alpha beta', badge='6.2', minutes=45,
    lead='Get the minimax answer while reading far fewer leaves. Learn what α and β mean, follow the slide example prune by prune, and see why move ordering lets the same time search twice as deep.',
    desc='Alpha and beta as bounds, the parent to child and child to parent rules, the slide example with leaves 2 3 5 9 0 1 7 5, the algorithm, complexity in the best, random and worst order, the Knuth and Moore minimal tree, move ordering, food for thought, and improvements such as aspiration windows and principal variation search.',
    summary='Alpha and beta, the prune rule, the slide example, move ordering and the cost of alpha beta.',
    keywords=['alpha beta pruning', 'alpha', 'beta', 'prune', 'move ordering', 'Knuth Moore', 'Deep Blue', 'effective branching factor'],
    recap='<p>α and β pass down, values pass up, and a branch is pruned when α ≥ β. Same answer as minimax, about twice the depth with good ordering.</p>',
    nb={'slide': 'Alpha beta on the slide example', 'order': 'Slide order against worst order'})
