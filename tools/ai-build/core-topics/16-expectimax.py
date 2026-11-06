# Chapter 6.3: games with chance. Source: slide Set 3, slides 11 and 12 (the expectimax value rules, the value,
# max-value and exp-value code, the example with chance nodes over 3 12 9, 2 4 6 and 15 6 0 giving 8, 4 and 7, the
# expectiminimax tree with probabilities 0.5, 0.4 and 0.1 giving 1.7, and the questions "What problems do you see
# here?" and "Any ideas on solution strategies?") and the class of 8 February 2026 (dice, coin bias, probabilities
# from experience, thresholds, Monte Carlo methods). The scaling example and Monte Carlo tree search follow Russell
# and Norvig, AIMA 3rd ed. section 5.5 and 4th ed. section 5.4, and Kocsis and Szepesvari, "Bandit based Monte-Carlo
# planning", ECML 2006.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('expmax', r'''
# Expectimax on the example of the slides. MAX at the top, then chance nodes, then the outcome values.
tree = [[3, 12, 9], [2, 4, 6], [15, 6, 0]]
prob = [1/3, 1/3, 1/3]                 # every outcome of a chance node has probability 1/3

def exp_value(outcomes):
    v = 0
    for i in range(len(outcomes)):
        v = v + prob[i] * outcomes[i]  # v += p * value(successor)
    return v

values = []
for outcomes in tree:
    values.append(round(exp_value(outcomes), 2))
print("chance nodes:", values)
print("MAX picks", max(values), "with move", values.index(max(values)) + 1)
''')

K.code('expmm', r'''
# Expectiminimax on the middle branch of slide 12: a chance node over three MIN nodes.
min_nodes = [[5, 4, 2], [1, 7, 2], [3, 4, 5]]
prob = [0.5, 0.4, 0.1]

v = 0
for i in range(3):
    m = min(min_nodes[i])               # MIN picks its smallest value
    print("MIN node", i + 1, "=", m, " weight", prob[i])
    v = v + prob[i] * m
print("chance node =", round(v, 2))

# Why the size of the numbers matters: AIMA's example with chances 0.9 and 0.1.
for name, leaves in [("values 2 3 1 4", [2, 3, 1, 4]), ("values 20 30 1 400", [20, 30, 1, 400])]:
    move1 = 0.9 * leaves[0] + 0.1 * leaves[1]
    move2 = 0.9 * leaves[2] + 0.1 * leaves[3]
    print(name, ": move 1 =", round(move1, 2), ", move 2 =", round(move2, 2))
''')

K.code('ucb', r'''
# Monte Carlo search at the root with UCB1. Each move has a hidden chance of winning a random game.
import math, random
random.seed(2)
chance = [0.3, 0.6, 0.45]               # hidden from the search
wins = [0, 0, 0]
visits = [0, 0, 0]
c = 1.4                                 # how much to explore
for t in range(1, 21):
    pick = -1
    best = -1.0
    for i in range(3):
        if visits[i] == 0:
            score = 1000.0              # an untried move comes first
        else:
            score = wins[i] / visits[i] + c * math.sqrt(math.log(t - 1) / visits[i])
        if score > best:
            best = score
            pick = i
    result = 1 if random.random() < chance[pick] else 0     # play one random game
    wins[pick] = wins[pick] + result
    visits[pick] = visits[pick] + 1
print("wins  ", wins)
print("visits", visits)
print("play move", visits.index(max(visits)) + 1)
''')

K.lesson('idea', 'When dice decide part of the game', f'''
{src('slide Set 3, slide 11, and the class of 8 February 2026.')}
<p>Minimax and alpha beta assume the opponent always picks the move that is worst for us. Many games are not like that. In backgammon, Ludo or snakes and ladders, a dice roll decides which moves are possible. In real life the "opponent" is often not clever at all: the weather, traffic, or a customer who acts at random with some known pattern. In class we said: the world does not always play optimally against you.</p>
{wwh('Expectimax is a game tree search where some nodes are chance nodes. A chance node does not choose. Its value is the average of its children, each weighted by its probability: the expected value.',
     'If the next event is random, planning for the worst case (minimax) is too careful, and ignoring the randomness is wrong. The expected value tells you what you will get on average if you play the same move many times.',
     'Build the tree with MAX nodes for your moves, chance nodes for random events, and (in expectiminimax) MIN nodes for the opponent. Leaves give utilities. Back the values up: max at MAX, min at MIN, and probability times value, added up, at chance nodes.')}
{fxs(
    fx('Expectimax value (slide 11)', 'V(s) = max<sub>s′ ∈ successors(s)</sub> V(s′) for agent controlled states. V(s) = ∑<sub>s′ ∈ successors(s)</sub> p(s′ | s) V(s′) for chance states. V(s) = known for terminal states', 'The same recursion as minimax, with the MIN rule replaced by an expectation.', key=True))}
{algo('Expectimax (slide 11)', [
    'def value(state):',
    '    if the state is a terminal state: return the state\'s utility',
    '    if the agent is MAX: return max-value(state)',
    '    if the agent is EXP: return exp-value(state)',
    '',
    'def max-value(state):',
    '    initialize v = −∞',
    '    for each successor of state: v = max(v, value(successor))',
    '    return v',
    '',
    'def exp-value(state):',
    '    initialize v = 0',
    '    for each successor of state:',
    '        p = probability(successor)',
    '        v += p × value(successor)',
    '    return v'])}
''', kw=['expectimax', 'chance node', 'expected value', 'dice', 'stochastic game', 'backgammon'])

K.lesson('example', 'The expectimax example of the slides', f'''
{src('slide Set 3, slide 11.')}
<p>MAX has three moves. Each leads to a chance node with three outcomes, each with probability 1/3. The outcome values are 3, 12, 9 for the first move, 2, 4, 6 for the second, and 15, 6, 0 for the third.</p>
{steps('Back up the values', [
    'First chance node: 1/3 × 3 + 1/3 × 12 + 1/3 × 9 = 24 ⁄ 3 = 8.',
    'Second chance node: 1/3 × 2 + 1/3 × 4 + 1/3 × 6 = 12 ⁄ 3 = 4.',
    'Third chance node: 1/3 × 15 + 1/3 × 6 + 1/3 × 0 = 21 ⁄ 3 = 7.',
    eq('MAX = max(8, 4, 7) = 8, so MAX takes the first move')])}
{viz('gametree', mode='exp', pat='ex', b=3, leaves='3 12 9 2 4 6 15 6 0', probs='1 1 1')}
{code('expmax')}
{note('If the same tree had MIN nodes instead of chance nodes, minimax would give min values 3, 2 and 0, and MAX would still pick the first move, but with value 3. The third move looks worst to minimax (0) and second best to expectimax (7). The two methods can choose different moves when the risk differs.', 'tip')}
''', kw=['expectimax example', 'slide 11', 'one third', '8 4 7'])

K.lesson('emm', 'Expectiminimax: chance and an opponent', f'''
{src('slide Set 3, slide 12, and the class of 8 February 2026.')}
<p>In backgammon both players roll dice. So the tree has four kinds of layers in turn: MAX, CHANCE (my roll), MIN, CHANCE (the opponent\'s roll). This is <b>expectiminimax</b>.</p>
{fxs(fx('Expectiminimax', 'EMM(s) = UTILITY(s) if terminal, max<sub>a</sub> EMM(RESULT(s, a)) if MAX, min<sub>a</sub> EMM(RESULT(s, a)) if MIN, ∑<sub>r</sub> P(r) EMM(RESULT(s, r)) if CHANCE', 'r is a chance outcome, such as a dice roll.', key=True))}
{steps('The middle branch of slide 12', [
    'The chance node has three outcomes with probabilities 0.5, 0.4 and 0.1. Each leads to a MIN node.',
    'MIN node 1 over 5, 4, 2 takes 2. MIN node 2 over 1, 7, 2 takes 1. MIN node 3 over 3, 4, 5 takes 3.',
    'Chance node: 0.5 × 2 + 0.4 × 1 + 0.1 × 3 = 1 + 0.4 + 0.3.',
    eq('= 1.7')])}
<p>The slide labels the bottom row CHANCE too. That row stands for the next chance layer of the game. Here we read its circles as the values that the search below returns.</p>
{viz('gametree', mode='exp', pat='emm', b=3, leaves='6 8 7 3 5 9 4 6 8 5 4 2 1 7 2 3 4 5 2 9 4 6 1 7 3 8 5', probs='0.5 0.4 0.1')}
{code('expmm')}
''', kw=['expectiminimax', 'slide 12', '1.7', 'MIN node', 'chance layer'])

K.lesson('issues', 'What problems do you see here?', f'''
{src('slide Set 3, slides 11 and 12 ask these questions. The answers come from the class of 8 February 2026 and AIMA section 5.5.')}
{table(['Problem', 'Why it hurts', 'Solution strategies'], [
    ['We must know the probabilities', 'In class: a coin tossed 1,000 times is never exactly 50:50, a coin may be biased, and probabilities from experience are skewed towards what we have seen', 'Estimate from data, update the estimates as you play, or test how much the decision changes when the probabilities change a little'],
    ['The tree is much bigger', 'Time O(b<sup>m</sup> n<sup>m</sup>), where n is the number of chance outcomes. Backgammon has 21 distinct rolls of two dice and about 20 moves per roll', 'Depth limit with an evaluation function, or sample a few rolls instead of all (Monte Carlo)'],
    ['The size of the values matters', 'Minimax only cares about the order of the leaves. Expectimax averages, so stretching some values can change the choice (see below)', 'The evaluation must be a positive linear function of the true expected payoff, for example the chance of winning'],
    ['Pruning is harder', 'One unseen child of a chance node can change the average by any amount', 'If the values are bounded, say between 0 and 10, a chance node gets an upper bound after a few children, and alpha beta style pruning works again'],
    ['The model of the opponent matters', 'Expectimax against a clever opponent can walk into a trap. Minimax against a random opponent is too careful', 'Pick the model that fits: MIN nodes for an adversary, chance nodes for random behaviour']])}
{steps('Why the size of the values matters (AIMA, chance 0.9 and 0.1)', [
    'Move 1 leads to values 2 (chance 0.9) and 3 (chance 0.1). Move 2 leads to values 1 (0.9) and 4 (0.1).',
    'Move 1: 0.9 × 2 + 0.1 × 3 = 2.1. Move 2: 0.9 × 1 + 0.1 × 4 = 1.3. Choose move 1.',
    'Now change the values to 20, 30, 1, 400. The order of the four values is the same.',
    'Move 1: 0.9 × 20 + 0.1 × 30 = 21. Move 2: 0.9 × 1 + 0.1 × 400 = 40.9. Now choose move 2.',
    eq('the order is kept, but the choice flips: expectimax needs values on the right scale')])}
''', kw=['problems with expectimax', 'probability estimates', 'biased coin', 'tree size', 'scale of values', 'pruning chance nodes'])

K.lesson('mcts', 'Monte Carlo tree search', f'''
{src('the class of 8 February 2026 ("certain advanced algorithms also come like Monte Carlo simulation") and Kocsis and Szepesvari, 2006.')}
{wwh('Monte Carlo tree search (MCTS) chooses a move by playing many quick random games (rollouts) and keeping a win record for each move. It grows a search tree only where the results look promising.',
     'For Go, b is about 250, and no one could write a good evaluation function by hand. Alpha beta cannot go deep enough. Random games need no evaluation function: the result of a finished game is the evaluation.',
     'Repeat four steps. Selection: from the root, pick children by UCB1 until you reach a node with untried moves. Expansion: add one new child. Simulation: play random moves from it to the end. Back up: add the result to the win and visit counts of every node on the path. Finally play the root move with the most visits.')}
{fxs(fx('UCB1 (upper confidence bound)', 'UCB1(i) = w<sub>i</sub> ⁄ n<sub>i</sub> + C √(ln N ⁄ n<sub>i</sub>)', 'w<sub>i</sub> wins in n<sub>i</sub> visits of move i, N visits of the parent, C balances the two parts. The first part is exploitation (how good the move looks), the second is exploration (how unsure we still are). C = √2 ≈ 1.4 is the usual start.', key=True))}
{viz('mcts')}
{code('ucb')}
<p>With seed 2 the search gives move 2 (the truly best move, 60% wins) 9 of the 20 visits. Change the seed: with seed 1 it ends on move 1 after 20 rounds. Twenty random games are few. Real programs play thousands per move.</p>
{note('MCTS also handles chance naturally: a dice roll in a rollout is just one more random step. That is one reason it replaced expectimax in many games with dice and cards.', 'tip')}
''', kw=['Monte Carlo tree search', 'MCTS', 'rollout', 'UCB1', 'exploration', 'exploitation', 'selection expansion simulation backpropagation'])

K.lesson('maths', 'The maths: expected value, UCB1 and cost', f'''
{fxs(
    fx('Expected value', 'E[X] = ∑<sub>x</sub> P(x) × x', 'The average result over many plays. The probabilities of the outcomes of one chance node add up to 1.', key=True),
    fx('Linearity', 'E[a X + b] = a E[X] + b for a > 0', 'This is why a positive linear change of all values keeps the expectimax choice, while other changes may not.'),
    fx('Cost of expectiminimax', 'O(b<sup>m</sup> n<sup>m</sup>)', 'b moves and n chance outcomes per level, m levels of each.'),
    fx('Where UCB1 comes from', 'P(true mean > sample mean + ε) ≤ e<sup>−2 n ε²</sup> (Hoeffding)', 'Choose ε so the chance of being wrong falls like 1 ⁄ N⁴: ε = √(2 ln N ⁄ n). That is UCB1 with C = √2.'))}
{steps('Worked example: dice in backgammon', [
    'Two dice give 36 ordered results. A double such as 3 and 3 happens 1 way in 36.',
    'A mixed roll such as 3 and 5 happens 2 ways (3 then 5, or 5 then 3), so 2 in 36 = 1 in 18.',
    'Distinct rolls: 6 doubles + 15 mixed pairs = 21.',
    eq('n = 21 chance outcomes: 6 with p = 1/36 and 15 with p = 1/18')])}
{steps('Worked example: one UCB1 value', [
    'Move i: 3 wins in 5 visits. The root has N = 10 visits. C = 1.4.',
    'Exploitation: 3 ⁄ 5 = 0.6.',
    'Exploration: 1.4 × √(ln 10 ⁄ 5) = 1.4 × √(2.303 ⁄ 5) = 1.4 × √0.4605 = 1.4 × 0.679 = 0.950.',
    eq('UCB1 = 0.6 + 0.950 ≈ 1.55')])}
{deep('Pruning chance nodes when values are bounded', '<p>Suppose every leaf lies between 0 and 10, and a chance node has three children with probability 1/3 each. After reading the first child, say 2, the largest the node can still become is (2 + 10 + 10) ⁄ 3 ≈ 7.33. If MAX above already has a move worth 8, this chance node can never win, so its other children can be skipped. This idea is called *-minimax (star minimax), due to Ballard (1983). It needs known bounds on the values.</p>')}
''', kw=['expected value', 'linearity of expectation', 'Hoeffding', 'UCB1 derivation', 'dice outcomes', 'star minimax'])

K.lesson('compare', 'Which game search to use', f'''
{versus('Game search methods', ['', 'Minimax and alpha beta', 'Expectimax', 'Expectiminimax', 'MCTS'], [
    ['Other side modelled as', 'A perfect opponent', 'Random events with known chances', 'An opponent plus random events', 'Whatever the rollout policy does'],
    ['Value at a non MAX node', 'min', 'Weighted average', 'min or weighted average', 'Win rate from rollouts'],
    ['Needs an evaluation function', 'Yes, at the depth limit', 'Yes, on the right scale', 'Yes, on the right scale', 'No'],
    ['Pruning', 'Alpha beta, exact', 'Only with bounded values', 'Only with bounded values', 'Not needed: it grows only good parts'],
    ['Typical games', 'Chess, checkers, tic-tac-toe', 'Single player games with randomness, Pac-Man ghosts that move at random', 'Backgammon', 'Go, many board and card games, planning']],
    'use minimax with alpha beta for a clever opponent and no chance, expectimax when the other side is random, expectiminimax when both happen, and MCTS when b is huge or no good evaluation function exists.')}
{scene('TD-Gammon and AlphaGo', '<p>TD-Gammon (Tesauro, 1992) played backgammon with a shallow expectiminimax search and a neural network evaluation learned by playing against itself, and reached the level of top human players. AlphaGo (2016) beat Lee Sedol at Go using MCTS guided by deep networks for move choice and position value. AlphaZero (2017) learned chess, shogi and Go from self play alone, with the same MCTS.</p>')}
''', kw=['comparison', 'TD-Gammon', 'AlphaGo', 'AlphaZero', 'Pac-Man'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>When luck is involved, think about the average result of a move, not only the worst one. If a move gives 3, 12 or 9 with equal chance, on average it gives 8.</p>',
    '<p>Expectimax adds chance nodes whose value is ∑ p × value. Expectiminimax mixes MAX, MIN and chance layers. Cost O(b<sup>m</sup> n<sup>m</sup>). Values must be on the right scale. MCTS replaces exact backup by random rollouts and UCB1 selection.</p>',
    '<p>UCB1 comes from the multi armed bandit problem: its regret grows only like log N (Auer, Cesa-Bianchi and Fischer, 2002). UCT applies UCB1 at every tree node and converges to the minimax value as the number of rollouts grows (Kocsis and Szepesvari, 2006). Expectimax is the same backup as the Bellman equation of a Markov decision process, which chapter 10 builds on.</p>',
    '<p>AlphaZero uses PUCT, which adds a prior from a policy network to the exploration term, and replaces random rollouts by a value network. MuZero learns the game model itself. For hidden information (poker), counterfactual regret minimisation and its deep variants beat top professionals (Libratus, Pluribus).</p>')}
''', kw=['bandit', 'regret', 'UCT', 'Bellman', 'PUCT', 'MuZero', 'Libratus'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A chance node does not choose. Its value is ∑ p(s′ | s) V(s′), the expected value of its children.',
    'Slide 11: chance nodes over 3 12 9, 2 4 6 and 15 6 0 with 1/3 each give 8, 4 and 7, so MAX picks 8.',
    'Expectiminimax has MAX, CHANCE and MIN layers. Slide 12: 0.5 × 2 + 0.4 × 1 + 0.1 × 3 = 1.7.',
    'Problems: the probabilities must be known, the tree grows as b<sup>m</sup> n<sup>m</sup>, the scale of values matters, and pruning needs bounded values.',
    'MCTS chooses moves from random rollouts with UCB1 = w ⁄ n + C √(ln N ⁄ n), and needs no evaluation function.'],
    'step 7 turns from search to logic: how an agent can store facts and reason with them.')}
{nbcard('expectimax', 'Run expectimax on the slide 11 tree and expectiminimax on the slide 12 branch, see how scaling flips a choice, run UCB1, then write expectimax, expectiminimax and the UCB1 move picker yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'The value of a chance node is', ['The largest child value', 'The smallest child value', 'The probability weighted average of its children', 'Always 0'], 2,
       'Slide 11.', 'V(s) = ∑ p(s′ | s) V(s′).')
K.quiz('e', 'In the slide 11 example, which move does MAX take?', ['The first (8)', 'The second (4)', 'The third (7)', 'Any of them'], 0,
       'max(8, 4, 7).', 'The first chance node is worth 8.')
K.quiz('e', 'Which game needs chance nodes?', ['Chess', 'Tic-tac-toe', 'Backgammon', 'Checkers'], 2,
       'Dice.', 'Backgammon moves depend on a dice roll.')
K.quiz('e', 'In exp-value on slide 11, v starts at', ['−∞', '0', '+∞', '1'], 1,
       'It is a sum.', 'v = 0, then v += p × value(successor).')
K.quiz('m', 'What is the value of the middle chance node on slide 12?', ['1', '1.7', '2', '3'], 1,
       '0.5 × 2 + 0.4 × 1 + 0.1 × 3.', '1 + 0.4 + 0.3 = 1.7.')
K.quiz('m', 'Why can expectimax change its choice when we stretch the leaf values but keep their order?', ['Because it uses max', 'Because it averages, and averages depend on the size of the values, not only their order', 'Because of pruning', 'It cannot'], 1,
       'AIMA 2 3 1 4 against 20 30 1 400.', 'Minimax only compares, expectimax adds.')
K.quiz('m', 'In UCB1, the term C √(ln N ⁄ n<sub>i</sub>) is large when', ['The move has many wins', 'The move has been visited only a few times', 'C = 0', 'N is small and n<sub>i</sub> is big'], 1,
       'Uncertainty.', 'Few visits mean we are unsure, so the bonus for exploring is big.')
K.quiz('m', 'At the end of MCTS, which root move is usually played?', ['The one with the highest UCB1', 'The one with the most visits', 'A random one', 'The first one'], 1,
       'The robust child.', 'The visit count is the most stable measure of how good the move looked.')
K.quiz('h', 'A probability estimate came from a biased coin. What does it do to expectimax?', ['Nothing', 'The expected values, and maybe the chosen move, are wrong', 'It makes the search faster', 'It turns expectimax into minimax'], 1,
       'From class.', 'Expectimax is only as good as its probabilities.')
K.quiz('h', 'Why is pruning hard in expectimax?', ['Chance nodes have no children', 'One unseen child of a chance node can change the average by any amount, unless values are bounded', 'There is no MAX node', 'Probabilities add to 2'], 1,
       'Unbounded leaves.', 'With bounds, *-minimax can prune.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: Pac-Man uses expectimax but the ghost actually plays as a perfect minimiser. What can happen?', ['Pac-Man always wins', 'Pac-Man may take risky paths that a minimiser punishes, so it can lose more often than with minimax', 'Nothing changes', 'The search fails to end'], 1,
       'Wrong model of the opponent.', 'Expectimax is optimistic about a random ghost, and a clever ghost exploits that.')
K.quiz('x', 'In the style of a Stanford CS221 exam: which change of leaf values always keeps the expectimax choice?', ['Squaring every value', 'Adding 10 to every value and then multiplying by 3', 'Taking the log of every value', 'Replacing values by their rank'], 1,
       'Linearity of expectation.', 'Only positive linear changes a × x + b with a > 0 are safe.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Slide 11, first chance node: 1/3 × 3 + 1/3 × 12 + 1/3 × 9.', '8', 'Add, then divide by 3.',
       ['3 + 12 + 9 = 24.', '24 ⁄ 3.', eq('8')], check=8)
K.calc('e', 'Slide 11, second chance node: 1/3 × (2 + 4 + 6).', '4', '12 ⁄ 3.',
       ['2 + 4 + 6 = 12.', '12 ⁄ 3.', eq('4')], check=4)
K.calc('e', 'Slide 11, third chance node: 1/3 × (15 + 6 + 0).', '7', '21 ⁄ 3.',
       ['15 + 6 + 0 = 21.', '21 ⁄ 3.', eq('7')], check=7)
K.calc('m', 'Slide 12: 0.5 × min(5, 4, 2) + 0.4 × min(1, 7, 2) + 0.1 × min(3, 4, 5).', '1.7', 'MIN values 2, 1, 3.',
       ['MIN values: 2, 1, 3.', '0.5 × 2 = 1, 0.4 × 1 = 0.4, 0.1 × 3 = 0.3.', eq('1 + 0.4 + 0.3 = 1.7')], check=1.7, tol=0.001)
K.calc('m', 'How many distinct rolls do two dice have, if 3 and 5 is the same roll as 5 and 3?', '21', '6 doubles plus pairs of different numbers.',
       ['Doubles: 6.', 'Different numbers: 6 × 5 ⁄ 2 = 15.', eq('6 + 15 = 21')], check=21)
K.calc('m', 'AIMA scaling example, move 1: 0.9 × 2 + 0.1 × 3.', '2.1', 'Weighted average.',
       ['0.9 × 2 = 1.8.', '0.1 × 3 = 0.3.', eq('1.8 + 0.3 = 2.1')], check=2.1, tol=0.001)
K.calc('h', 'After the values change to 20, 30, 1, 400: move 2 = 0.9 × 1 + 0.1 × 400.', '40.9', 'This now beats move 1 (21).',
       ['0.9 × 1 = 0.9.', '0.1 × 400 = 40.', eq('0.9 + 40 = 40.9 > 21, so the choice flips to move 2')], check=40.9, tol=0.001)
K.calc('h', 'UCB1 for 3 wins in 5 visits, parent visits N = 10, C = 1.4. Give 2 decimals.', '1.55', 'w ⁄ n + C √(ln N ⁄ n).',
       ['w ⁄ n = 0.6.', 'ln 10 ≈ 2.303, 2.303 ⁄ 5 = 0.4605, √0.4605 ≈ 0.679.', '1.4 × 0.679 ≈ 0.950.', eq('0.6 + 0.950 ≈ 1.55')], check=1.55, tol=0.01)
K.calc('h', 'Expectiminimax cost (b n)<sup>m</sup> with b = 20 moves, n = 21 rolls and m = 3.', '74088000', '(20 × 21)³ = 420³.',
       ['20 × 21 = 420.', '420² = 176,400.', eq('176,400 × 420 = 74,088,000 nodes')], check=74088000)
K.calc('x', 'In the style of a Berkeley CS188 exam: MAX can take a sure 6, or a chance node that gives 10 with probability 0.5, or with probability 0.5 hands over to a MIN node choosing between 4 and 8. What is the root value?', '7', 'Value the chance node first.',
       ['MIN node: min(4, 8) = 4.', 'Chance node: 0.5 × 10 + 0.5 × 4 = 7.', eq('root = max(6, 7) = 7')], check=7)
K.calc('x', 'In the style of an MIT 6.034 exam: leaves lie between 0 and 10. A chance node has three children with probability 1/3 each, and the first child is worth 2. What is the largest value this chance node can still reach? Give 2 decimals.', '7.33', 'Assume the two unseen children are 10.',
       ['Best case for the unseen children: 10 and 10.', '(2 + 10 + 10) ⁄ 3 = 22 ⁄ 3.', eq('≈ 7.33, so if MAX already has 8, prune the rest')], check=7.33, tol=0.01)

# ---------------------------------------------------------------- assignments
K.assign('expmax', 'e', 'Expectimax with equal chances',
         '<p>Write <code>expectimax(node, is_max)</code>. A node is a number (a leaf) or a list of children. MAX nodes take the largest child value. The other nodes are chance nodes where every child is equally likely, so their value is the average of the children. Levels alternate, starting with MAX when is_max is True.</p>',
         '''
def expectimax(node, is_max):
    # your code here
    pass
''', [("expectimax([[3, 12, 9], [2, 4, 6], [15, 6, 0]], True)", 8.0),
      ("expectimax([[1, 5], [4, 4]], True)", 4.0),
      ("expectimax([[[1, 3], [8, 2]], [[2, 2], [6, 0]]], False)", 4.0),
      ("expectimax(7, True)", 7)],
         '''
def expectimax(node, is_max):
    if type(node) == int:
        return node
    values = []
    for child in node:
        values.append(expectimax(child, not is_max))
    if is_max:
        return max(values)
    return sum(values) / len(values)
''', 'A leaf returns itself. Otherwise compute every child with the other kind of node, then take the max or the average.', '<p>Test 1 is the slide 11 tree. In test 3 the root is a chance node over two MAX nodes, and each MAX node is over two chance nodes. Left MAX: max(avg(1, 3), avg(8, 2)) = max(2, 5) = 5. Right MAX: max(avg(2, 2), avg(6, 0)) = max(2, 3) = 3. Root: avg(5, 3) = 4.</p>')
K.assign('emm', 'm', 'Expectiminimax with layer kinds',
         '<p>Write <code>expectiminimax(node, kinds, probs, depth)</code>. kinds is a list such as <code>["max", "chance", "min"]</code> that gives the node kind at each depth. probs is the list of probabilities used by every chance node, in child order. Return the value rounded to 2 decimals at depth 0 only.</p>',
         '''
def expectiminimax(node, kinds, probs, depth):
    # your code here
    pass
''', [("expectiminimax([[[5, 4, 2], [1, 7, 2], [3, 4, 5]]], ['max', 'chance', 'min'], [0.5, 0.4, 0.1], 0)", 1.7),
      ("expectiminimax([[3, 12, 9], [2, 4, 6], [15, 6, 0]], ['max', 'chance'], [0.2, 0.3, 0.5], 0)", 8.7),
      ("expectiminimax([[2, 3], [1, 4]], ['max', 'chance'], [0.9, 0.1], 0)", 2.1),
      ("expectiminimax([[20, 30], [1, 400]], ['max', 'chance'], [0.9, 0.1], 0)", 40.9)],
         '''
def expectiminimax(node, kinds, probs, depth):
    if type(node) == int or type(node) == float:
        return node
    values = []
    for child in node:
        values.append(expectiminimax(child, kinds, probs, depth + 1))
    kind = kinds[depth]
    if kind == "max":
        v = max(values)
    elif kind == "min":
        v = min(values)
    else:
        v = 0
        for i in range(len(values)):
            v = v + probs[i] * values[i]
    if depth == 0:
        return round(v, 2)
    return v
''', 'Look up the kind with kinds[depth]. For a chance node add probs[i] times the value of child i.', '<p>Test 1 is the slide 12 branch. Test 2 uses other chances on the slide 11 tree: 0.2 × 3 + 0.3 × 12 + 0.5 × 9 = 8.7, and the other two chance nodes give 4.6 and 4.8, so the root is max(8.7, 4.6, 4.8) = 8.7. Tests 3 and 4 are the AIMA scaling example.</p>')
K.assign('ucbpick', 'm', 'Pick a move with UCB1',
         '<p>Write <code>pick(wins, visits, c)</code>. wins and visits are lists with one entry per move. If some move has 0 visits, return the index of the first such move. Otherwise return the index of the move with the largest UCB1 = wins[i] ⁄ visits[i] + c × √(ln N ⁄ visits[i]), where N is the sum of the visits. On a tie, return the lowest index.</p>',
         '''
import math

def pick(wins, visits, c):
    # your code here
    pass
''', [("pick([0, 0, 0], [0, 0, 0], 1.4)", 0),
      ("pick([1, 0, 0], [1, 0, 0], 1.4)", 1),
      ("pick([3, 2, 1], [5, 3, 2], 0)", 1),
      ("pick([3, 2, 1], [5, 3, 2], 1.4)", 2),
      ("pick([6, 1], [10, 2], 0)", 0)],
         '''
import math

def pick(wins, visits, c):
    for i in range(len(visits)):
        if visits[i] == 0:
            return i
    total = sum(visits)
    best = 0
    best_score = -1.0
    for i in range(len(visits)):
        score = wins[i] / visits[i] + c * math.sqrt(math.log(total) / visits[i])
        if score > best_score:
            best_score = score
            best = i
    return best
''', 'First look for an untried move. Then compute the UCB1 score of each move and keep the largest, using > so the lowest index wins a tie.', '<p>Test 3 has c = 0, so only the win rate counts: 0.6, 0.67, 0.5. Test 4 adds exploration: the scores are about 1.55, 1.89 and 2.00, so the move with only 2 visits wins.</p>')

K.must('Chance node', 'V(s) = ∑ p(s′ | s) V(s′). exp-value starts at v = 0 and adds p × value.')
K.must('Slide 11', '3 12 9, 2 4 6, 15 6 0 with 1/3 each: 8, 4, 7. MAX = 8.')
K.must('Slide 12', 'MIN 2, 1, 3 with 0.5, 0.4, 0.1: 1.7. Layers MAX, CHANCE, MIN, CHANCE.')
K.must('Problems', 'Need probabilities, cost O(b<sup>m</sup> n<sup>m</sup>), value scale matters (only a x + b with a > 0 is safe), pruning needs bounds.')
K.must('MCTS', 'Select by UCB1 = w ⁄ n + C √(ln N ⁄ n), expand, simulate, back up. Play the most visited move.')

T = K.topic(
    slug='expectimax', topic='expectimax', step=(6, 'Adversarial search', 'cai-games', 'Search when an opponent moves too: minimax, alpha beta pruning, and games with chance.', 'College'),
    title='Games with chance: expectimax and Monte Carlo tree search', short='Expectimax and MCTS', badge='6.3', minutes=50,
    lead='When dice or random events decide part of the game, plan for the average result. Back up expected values with expectimax and expectiminimax, see the problems the slides ask about, and choose moves from random games with Monte Carlo tree search.',
    desc='Chance nodes and the expectimax rules of slide 11, the 8, 4, 7 example, expectiminimax and the 1.7 example of slide 12, the problems with probabilities, tree size, value scale and pruning, Monte Carlo tree search with UCB1, the maths of expectation and UCB1, and a comparison of game search methods.',
    summary='Expectimax, expectiminimax, their problems, and Monte Carlo tree search with UCB1.',
    keywords=['expectimax', 'expectiminimax', 'chance node', 'expected value', 'Monte Carlo tree search', 'MCTS', 'UCB1', 'backgammon', 'AlphaGo'],
    recap='<p>Chance nodes average their children by probability. MCTS replaces exact backup by random games and UCB1.</p>',
    nb={'expmax': 'Expectimax on the slide 11 tree', 'expmm': 'Expectiminimax on slide 12 and the scaling problem', 'ucb': 'UCB1 at the root'})
