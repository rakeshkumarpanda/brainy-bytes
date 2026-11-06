# Chapter 6.1: games and minimax. Source: slide Set 3, slides 1 to 6 (decision making in competitive multi agent
# environments, the formal game S0, PLAYER, ACTIONS, RESULT, TERMINAL-TEST, UTILITY, the minimax procedure, the 27
# leaf minimax example with C1 to C9 and B1 to B3, the tic-tac-toe example with nodes 1 to 14, and food for thought
# on complexity, data structures, applications and utility functions) and the class of 8 February 2026. Evaluation
# functions, cutoffs, quiescence and the horizon effect follow Russell and Norvig, AIMA 4th ed., sections 5.1 to 5.4.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('tree', r'''
# Minimax on the 27 leaf example of the slides. A tree is a list of subtrees, a leaf is a number.
leaves = [2, 1, 5, 6, 2, 11, 8, 5, 1, 3, 2, 4, 10, 11, 12, 1, 2, 1, 2, 1, 3, 6, 1, 11, 2, 5, 1]

def build(values, size):                     # cut a flat list into groups of 3, then groups of groups
    groups = []
    for i in range(0, len(values), size):
        groups.append(values[i:i + size])
    return groups

tree = build(build(leaves, 3), 3)            # A has B1, B2, B3. Each B has three C nodes. Each C has 3 leaves.

def minimax(node, is_max):
    if type(node) == int:
        return node                          # a leaf: its utility
    values = []
    for child in node:
        values.append(minimax(child, not is_max))
    if is_max:
        return max(values)
    return min(values)

for i in range(3):
    print("B" + str(i + 1), "=", minimax(tree[i], False))
print("A =", minimax(tree, True))
''')

K.code('ttt', r'''
# Minimax on the tic-tac-toe position of the slides. O is MAX (+1 if O wins), X is MIN (-1 if X wins).
# Squares are numbered 0 to 8, row by row. " " is an empty square.
start = ["O", "X", "O",
         "X", " ", "X",
         " ", "O", " "]
lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

def winner(b):
    for a, c, d in lines:
        if b[a] != " " and b[a] == b[c] == b[d]:
            return b[a]
    return None

def minimax(b, player):
    w = winner(b)
    if w == "O":
        return 1
    if w == "X":
        return -1
    if " " not in b:
        return 0                                   # a draw
    values = []
    for i in range(9):
        if b[i] == " ":
            b[i] = player
            values.append(minimax(b, "X" if player == "O" else "O"))
            b[i] = " "                             # undo the move
    return max(values) if player == "O" else min(values)

for i in range(9):
    if start[i] == " ":
        start[i] = "O"
        print("O plays square", i, "-> value", minimax(start, "X"))
        start[i] = " "
''')

K.lesson('idea', 'Games as search problems', f'''
{src('slide Set 3, slides 1 and 2, and the class of 8 February 2026.')}
<p>In a game, other agents act too, and they want something different. Each agent tries to raise its own utility or cut its loss, and one agent\'s move changes what the others can get. Uncertainty comes from not knowing what the opponent will do, which is called strategic uncertainty. Searching in such a setting is called <b>adversarial search</b>.</p>
{table(['Part (slide 2)', 'Meaning', 'Tic-tac-toe'], [
    ['S<sub>0</sub>', 'The initial state', 'The empty board'],
    ['PLAYER(s)', 'Whose turn it is in state s', 'X and O take turns'],
    ['ACTIONS(s)', 'The legal moves in s', 'The empty squares'],
    ['RESULT(s, a)', 'The transition model: the state after move a', 'The board with the new mark'],
    ['TERMINAL-TEST(s)', 'True when the game is over', 'Three in a row, or a full board'],
    ['UTILITY(s, p)', 'The final payoff for player p in a terminal state s', '+1 win, −1 loss, 0 draw']])}
{table(['', 'Deterministic', 'Chance'], [
    ['Perfect information', 'Chess, Go, tic-tac-toe, checkers', 'Backgammon, Monopoly'],
    ['Imperfect information', 'Battleship, Kriegspiel', 'Poker, bridge, Scrabble']])}
<p>This chapter covers deterministic, two player, turn taking, <b>zero sum</b> games with perfect information: what one player wins, the other loses, so one number, the utility for MAX, describes both.</p>
''', kw=['adversarial search', 'game', 'zero sum', 'perfect information', 'utility', 'terminal test', 'strategic uncertainty'])

K.lesson('minimax', 'The minimax algorithm', f'''
{src('slide Set 3, slides 3 and 4.')}
{wwh('Minimax computes, for every node of the game tree, the best utility MAX can guarantee against an opponent who plays perfectly. MAX nodes take the largest child value and MIN nodes take the smallest.',
     'You cannot pick a move by looking only at your own options: the opponent answers. Minimax assumes the worst sensible answer, so the move it picks is safe against any opponent.',
     'Generate the game tree down to terminal states. Give each terminal its utility. Back the values up: max at MAX nodes, min at MIN nodes. The root value is what MAX can guarantee, and the move leading to it is the optimal move.')}
{fxs(fx('Minimax value', 'MINIMAX(s) = UTILITY(s) if s is terminal, max<sub>a</sub> MINIMAX(RESULT(s, a)) if MAX moves, min<sub>a</sub> MINIMAX(RESULT(s, a)) if MIN moves', 'A recursive definition, computed depth first.', key=True))}
{steps('The slide example (three levels, 27 leaves)', [
    'C nodes are MAX nodes over 3 leaves each: C1 = 5, C2 = 11, C3 = 8, C4 = 4, C5 = 12, C6 = 2, C7 = 3, C8 = 11, C9 = 5.',
    'B nodes are MIN nodes: B1 = min(5, 11, 8) = 5 (from C1), B2 = min(4, 12, 2) = 2 (from C6), B3 = min(3, 11, 5) = 3 (from C7).',
    'A is a MAX node: A = max(5, 2, 3) = 5.',
    eq('MAX plays towards B1 and is guaranteed at least 5')])}
{viz('gametree', mode='minimax', pat='mm3', b=3, leaves='2 1 5 6 2 11 8 5 1 3 2 4 10 11 12 1 2 1 2 1 3 6 1 11 2 5 1')}
{code('tree')}
{algo('MINIMAX-DECISION', [
    'function MINIMAX-DECISION(state):',
    '    return the action a in ACTIONS(state) with the largest MIN-VALUE(RESULT(state, a))',
    '',
    'function MAX-VALUE(state):',
    '    if TERMINAL-TEST(state): return UTILITY(state)',
    '    v = −∞',
    '    for each a in ACTIONS(state): v = max(v, MIN-VALUE(RESULT(state, a)))',
    '    return v',
    '',
    'function MIN-VALUE(state):',
    '    if TERMINAL-TEST(state): return UTILITY(state)',
    '    v = +∞',
    '    for each a in ACTIONS(state): v = min(v, MAX-VALUE(RESULT(state, a)))',
    '    return v'])}
''', kw=['minimax', 'MAX node', 'MIN node', 'back up values', 'optimal move', 'game tree'])

K.lesson('ttt', 'The tic-tac-toe example of the slides', f'''
{src('slide Set 3, slide 5.')}
<p>The board is O X O on top, X _ X in the middle and _ O _ at the bottom. O is MAX and moves now. Three squares are free: the centre (square 4), bottom left (6) and bottom right (8).</p>
{steps('Minimax on this position (the slide numbers the boards 1 to 14)', [
    'Board 2: O takes the centre. X can answer in either corner (boards 5 and 6), but O then takes the last square and wins with a diagonal (boards 11 and 12). Value +1, whatever X does: X\'s choice is irrelevant.',
    'Board 3: O takes bottom left. X takes the centre and completes the middle row (board 7). Value −1.',
    'Board 4: O takes bottom right. X takes the centre and wins the same way (board 9). Value −1.',
    'Level 1 is X\'s decision, a MIN level. Level 0 is O\'s decision, a MAX level.',
    eq('O chooses board 2 (the centre), the only move that wins')])}
{code('ttt')}
{note('Boards 8, 10, 13 and 14 show what happens if X does not take the centre: O wins. Minimax ignores those lines because a perfect X would not play them.', 'tip')}
''', kw=['tic-tac-toe', 'slide example', 'minimax tic-tac-toe'])

K.lesson('props', 'Properties, and what to do when the tree is too big', f'''
{src('slide Set 3, slide 6, food for thought.')}
{table(['Property', 'Minimax'], [
    ['Complete', 'Yes, if the tree is finite'],
    ['Optimal', 'Yes, against an optimal opponent. Against a weak one it is safe but may miss chances'],
    ['Time', 'O(b<sup>m</sup>): it visits the whole tree to depth m'],
    ['Space', 'O(b m) when it explores depth first and generates all moves at once, O(m) when it generates one move at a time'],
    ['Data structures', 'A recursion stack (or explicit stack) of states, the list of moves at each level, and the best value and move so far']])}
<p>For chess, b ≈ 35 and a game lasts m ≈ 100 plies (moves by one player), so the tree has about 35<sup>100</sup> ≈ 10<sup>154</sup> nodes. Real programs stop early and estimate.</p>
{fxs(
    fx('Depth limited minimax', 'replace TERMINAL-TEST by CUTOFF-TEST(s, d) and UTILITY by EVAL(s)', 'Search to a fixed depth d, then use a heuristic evaluation of the position.', key=True),
    fx('Weighted linear evaluation', 'EVAL(s) = w<sub>1</sub> f<sub>1</sub>(s) + w<sub>2</sub> f<sub>2</sub>(s) + ... + w<sub>n</sub> f<sub>n</sub>(s)', 'Chess material: pawn 1, knight 3, bishop 3, rook 5, queen 9, counted for MAX minus for MIN.'))}
{table(['Problem with cutting off', 'Fix'], [
    ['Non quiet positions: the evaluation changes wildly in the next move (a capture is about to happen)', 'Quiescence search: keep searching captures until the position is quiet'],
    ['Horizon effect: a delaying move pushes an unavoidable loss beyond the search depth, so it looks avoided', 'Singular extensions: search a clearly best move one level deeper'],
    ['Too many moves to search', 'Forward pruning: skip moves that look bad (beam search on moves). Risky but used in practice']])}
''', kw=['complexity of minimax', 'chess 10 to the 154', 'evaluation function', 'cutoff test', 'quiescence', 'horizon effect', 'forward pruning'])

K.lesson('maths', 'The maths: zero sum games and evaluation', f'''
{fxs(
    fx('Zero sum', 'UTILITY(s, MAX) + UTILITY(s, MIN) = constant', 'Chess: 1 + 0, 0 + 1 or ½ + ½. So MIN minimising MAX\'s utility is the same as maximising its own.', key=True),
    fx('Multiplayer games', 'each node holds a vector (u<sub>1</sub>, ..., u<sub>k</sub>), and the player to move picks the child with the best u<sub>own</sub>', 'With three players, alliances can appear and break, which plain minimax cannot express.'),
    fx('Size of a game tree', 'b<sup>m</sup>', 'Tic-tac-toe has at most 9! = 362,880 move sequences (fewer, because games end early), and only 5,478 legal positions.'))}
{steps('Worked example: a material evaluation', [
    'White has 8 pawns, 2 knights, 1 bishop, 2 rooks and 1 queen. Black has 7 pawns, 1 knight, 2 bishops, 2 rooks and 1 queen.',
    'White: 8 + 2 × 3 + 3 + 2 × 5 + 9 = 36.',
    'Black: 7 + 3 + 2 × 3 + 2 × 5 + 9 = 35.',
    eq('EVAL = 36 − 35 = +1 for White (a pawn up)')])}
{steps('Worked example: tree size', [
    'A game with b = 10 and depth m = 6.',
    'Leaves: 10⁶ = 1,000,000.',
    'At 1 million leaves a second, about 1 second. At depth 8, 100 seconds.',
    eq('every two extra plies cost 100 times more for b = 10')])}
''', kw=['zero sum', 'multiplayer', 'material evaluation', 'game tree size'])

K.lesson('compare', 'Minimax against other ways to choose a move', f'''
{versus('Choosing a move in a game', ['', 'Greedy (best immediate result)', 'Minimax', 'Expectimax (chapter 6.3)'], [
    ['Assumes about the opponent', 'Nothing, ignores replies', 'Plays perfectly against you', 'Plays at random with known chances'],
    ['Safe against a perfect opponent', 'No', 'Yes', 'No'],
    ['Exploits a weak opponent', 'Sometimes', 'No, it is cautious', 'Yes, if the chances are right'],
    ['Cost', 'O(b)', 'O(b<sup>m</sup>)', 'O(b<sup>m</sup>)'],
    ['Slide tic-tac-toe', 'Can pick a losing corner', 'Picks the centre, wins', 'Picks the centre too']],
    'minimax is the right tool for two player zero sum games of skill. Alpha beta pruning (chapter 6.2) gives the same answer much faster.')}
{scene('food for thought: real uses of minimax', '<p>Chess and checkers engines (Chinook solved checkers in 2007: perfect play is a draw). Security games, where a defender places guards against an attacker who adapts, use the same max min reasoning. Robust planning treats nature as an opponent: "choose the plan whose worst case is best", for example when a power grid operator plans for the worst line failure. The utility function must capture what matters: in chess material, king safety and mobility, in security the value of each target.</p>')}
''', kw=['comparison', 'Chinook', 'security games', 'robust planning'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Minimax is thinking "if I do this, what is the worst my opponent can do to me?", for every move, and choosing the move whose worst case is best.</p>',
    '<p>A game has S<sub>0</sub>, PLAYER, ACTIONS, RESULT, TERMINAL-TEST and UTILITY. Minimax backs up max at MAX nodes and min at MIN nodes. It is complete and optimal against a perfect opponent, O(b<sup>m</sup>) time and O(b m) space. Real programs cut off at a depth and use an evaluation function.</p>',
    '<p>The minimax value of a zero sum game equals the value from von Neumann\'s minimax theorem for mixed strategies when moves are simultaneous. For turn taking perfect information games, backward induction (Zermelo, 1913) shows a pure strategy optimum exists. The horizon effect and quiescence show why a static evaluation is fragile.</p>',
    '<p>Modern engines replace hand tuned evaluation with neural networks (Stockfish NNUE) or replace minimax by Monte Carlo tree search guided by networks (AlphaZero). Game theory research extends this to imperfect information (counterfactual regret minimisation in poker) and to many players.</p>')}
''', kw=['backward induction', 'Zermelo', 'NNUE', 'AlphaZero', 'CFR'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A game is a search problem with S<sub>0</sub>, PLAYER, ACTIONS, RESULT, TERMINAL-TEST and UTILITY. Two player zero sum games with perfect information are the classic case.',
    '<b>Minimax</b>: MAX nodes take the max of their children, MIN nodes the min, terminals give their utility. The root value is what MAX can guarantee.',
    'Slide example: C = 5, 11, 8, 4, 12, 2, 3, 11, 5, then B1 = 5, B2 = 2, B3 = 3, and A = 5. Slide tic-tac-toe: O takes the centre and wins.',
    'Complete for finite trees, optimal against a perfect opponent, O(b<sup>m</sup>) time and O(b m) space. Chess has about 10<sup>154</sup> nodes.',
    'Cut off at a depth with an evaluation function, and watch for quiet positions and the horizon effect.'],
    'chapter 6.2 prunes the minimax tree with alpha and beta and gets the same answer much faster.')}
{nbcard('minimax', 'Run minimax on the 27 leaf example and on the slide tic-tac-toe position, then write minimax for nested trees and for tic-tac-toe yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'At a MIN node, minimax takes', ['The largest child value', 'The smallest child value', 'The average', 'The first child'], 1,
       'The opponent.', 'MIN picks the move worst for MAX.')
K.quiz('e', 'In a zero sum game,', ['Both players can win', 'One player\'s gain is the other\'s loss', 'Utilities are zero', 'There is no opponent'], 1,
       'The total is fixed.', 'So a single number describes the outcome for both.')
K.quiz('e', 'What value does the root A have in the slide example?', ['2', '3', '5', '11'], 2,
       'max(B1, B2, B3).', 'max(5, 2, 3) = 5.')
K.quiz('e', 'Which function says whether the game is over?', ['UTILITY', 'TERMINAL-TEST', 'RESULT', 'PLAYER'], 1,
       'Game over.', 'TERMINAL-TEST(s) is true in terminal states.')
K.quiz('m', 'In the slide tic-tac-toe position, which move should O make?', ['Bottom left', 'Centre', 'Bottom right', 'Any'], 1,
       'Board 2.', 'Only the centre gives value +1.')
K.quiz('m', 'B2 = min(C4, C5, C6) with C4 = 4, C5 = 12, C6 = 2 is', ['4', '12', '2', '6'], 2,
       'Smallest.', 'min(4, 12, 2) = 2.')
K.quiz('m', 'The time complexity of minimax is', ['O(b m)', 'O(b<sup>m</sup>)', 'O(m<sup>b</sup>)', 'O(b + m)'], 1,
       'The whole tree.', 'It visits all b<sup>m</sup> leaves.')
K.quiz('m', 'The horizon effect is', ['A bug in the evaluation', 'Pushing an unavoidable bad event beyond the search depth so it seems avoided', 'Searching too deep', 'Pruning too much'], 1,
       'Out of sight.', 'Delaying moves hide the problem past the cutoff.')
K.quiz('h', 'Minimax against a weak opponent', ['Always loses', 'Is still safe but may not exploit the opponent\'s mistakes', 'Becomes greedy', 'Is not defined'], 1,
       'It assumes the worst.', 'It guarantees its value but does not gamble for more.')
K.quiz('h', 'Quiescence search', ['Stops at a fixed depth always', 'Keeps searching non quiet positions, such as pending captures, before evaluating', 'Removes the evaluation function', 'Is used only in tic-tac-toe'], 1,
       'Quiet positions.', 'Evaluating in the middle of a capture sequence gives wrong values.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: a MIN node has children whose minimax values are 3, 7 and 3. Its parent MAX node has another child worth 4. What is the parent\'s value?', ['3', '4', '7', '5'], 1,
       'MIN gives 3.', 'MIN node = 3. MAX = max(3, 4) = 4.')
K.quiz('x', 'In the style of an MIT 6.034 exam: why can three player games not be solved with a single minimax value?', ['They have no terminal states', 'Utilities are not zero sum between two sides, so each node needs a vector and players may cooperate', 'b is too small', 'Minimax needs exactly two moves'], 1,
       'One number per player.', 'Each player maximises its own component, and alliances can form.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'C1 = max(2, 1, 5).', '5', 'MAX node.',
       ['Leaves 2, 1, 5.', 'The largest.', eq('5')], check=5)
K.calc('e', 'B1 = min(C1, C2, C3) = min(5, 11, 8).', '5', 'MIN node.',
       ['C1 = 5, C2 = 11, C3 = 8.', 'The smallest.', eq('5')], check=5)
K.calc('e', 'Leaves in a tree with b = 3 and depth 3.', '27', '3³.',
       ['3 × 3 = 9.', '9 × 3.', eq('27')], check=27)
K.calc('m', 'B3 = min(max(2, 1, 3), max(6, 1, 11), max(2, 5, 1)).', '3', 'Compute the three C values.',
       ['C7 = 3, C8 = 11, C9 = 5.', 'min(3, 11, 5).', eq('3')], check=3)
K.calc('m', 'Material: White 8 pawns, 2 knights, 1 bishop, 2 rooks, 1 queen. Score with 1, 3, 3, 5, 9.', '36', 'Add.',
       ['8 + 6 + 3 = 17.', '10 + 9 = 19.', eq('17 + 19 = 36')], check=36)
K.calc('m', 'Chess: 35¹⁰⁰ ≈ 10<sup>k</sup>. Find k to the nearest whole number using log₁₀ 35 ≈ 1.544.', '154', '100 × 1.544.',
       ['log₁₀ 35¹⁰⁰ = 100 log₁₀ 35.', '100 × 1.544 = 154.4.', eq('≈ 10¹⁵⁴')], check=154)
K.calc('m', 'Minimax space O(b m) for b = 35 and m = 10: b × m.', '350', '35 × 10.',
       ['b m.', '35 × 10.', eq('350 nodes')], check=350)
K.calc('h', 'How many move sequences can tic-tac-toe have at most (ignoring early wins)? 9!.', '362880', '9 × 8 × ... × 1.',
       ['9 × 8 × 7 = 504. 504 × 6 = 3,024.', '3,024 × 5 × 4 × 3 × 2 × 1 = 362,880.', eq('362,880')], check=362880)
K.calc('h', 'b = 10. How many times more leaves does depth 8 have than depth 6?', '100', '10⁸ ⁄ 10⁶.',
       ['10⁸ ⁄ 10⁶.', '= 10².', eq('100')], check=100)
K.calc('x', 'In the style of a Stanford CS221 problem: in the slide tic-tac-toe position, how many terminal boards does a full minimax search reach? Some games end before the board is full.', '6', 'Count the finished games after each first move of O.',
       ['O centre: X has 2 replies, and O then fills the last square and wins on a diagonal. That gives 2 terminal boards.', 'O bottom left: X takes the centre and wins at once (1 board), or X takes bottom right and O takes the centre and wins (1 board). O bottom right works the same way: 2 more boards.', eq('2 + 2 + 2 = 6 terminal boards')], check=6)

# ---------------------------------------------------------------- assignments
K.assign('mm', 'e', 'Minimax on a nested list tree',
         '<p>Write <code>minimax(node, is_max)</code>. A node is a number (a leaf) or a list of child nodes. Return the minimax value, with MAX at the root when is_max is True.</p>',
         '''
def minimax(node, is_max):
    # your code here
    pass
''', [("minimax([[[2, 1, 5], [6, 2, 11], [8, 5, 1]], [[3, 2, 4], [10, 11, 12], [1, 2, 1]], [[2, 1, 3], [6, 1, 11], [2, 5, 1]]], True)", 5),
      ("minimax([[3, 12, 8], [2, 4, 6], [14, 5, 2]], True)", 3), ("minimax(7, True)", 7), ("minimax([[1, 2], [3]], False)", 2)],
         '''
def minimax(node, is_max):
    if type(node) == int:
        return node
    values = []
    for child in node:
        values.append(minimax(child, not is_max))
    if is_max:
        return max(values)
    return min(values)
''', 'A leaf returns itself. Otherwise call yourself on each child with the other player, then take max or min.', '<p>The second test is the classic AIMA figure 5.2 tree: MIN nodes 3, 2, 2, root 3.</p>')
K.assign('tttbest', 'm', 'Best tic-tac-toe move',
         '<p>Write <code>best_move(board, player)</code>. board is a list of 9 strings "X", "O" or " ". O maximises (+1 for an O win), X minimises (−1 for an X win), a draw is 0. Return the lowest numbered square with the best minimax value for player.</p>',
         '''
def best_move(board, player):
    # your code here
    pass
''', [("best_move(['O', 'X', 'O', 'X', ' ', 'X', ' ', 'O', ' '], 'O')", 4),
      ("best_move(['X', 'X', ' ', 'O', 'O', ' ', ' ', ' ', ' '], 'X')", 2),
      ("best_move(['O', ' ', 'X', ' ', 'X', ' ', ' ', ' ', 'O'], 'O')", 6)],
         '''
def best_move(board, player):
    lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

    def winner(b):
        for a, c, d in lines:
            if b[a] != " " and b[a] == b[c] == b[d]:
                return b[a]
        return None

    def value(b, turn):
        w = winner(b)
        if w == "O":
            return 1
        if w == "X":
            return -1
        if " " not in b:
            return 0
        results = []
        for i in range(9):
            if b[i] == " ":
                b[i] = turn
                results.append(value(b, "X" if turn == "O" else "O"))
                b[i] = " "
        if turn == "O":
            return max(results)
        return min(results)

    b = list(board)
    best = None
    best_value = None
    for i in range(9):
        if b[i] == " ":
            b[i] = player
            v = value(b, "X" if player == "O" else "O")
            b[i] = " "
            if best is None or (player == "O" and v > best_value) or (player == "X" and v < best_value):
                best = i
                best_value = v
    return best
''', 'Write value(board, turn) recursively, then try each empty square for the player and keep the best.', '<p>In the second test X wins at once by completing the top row at square 2. In the third test O must block the diagonal 2, 4, 6 at square 6, because any other move lets X win next turn.</p>')

K.must('Game', 'S<sub>0</sub>, PLAYER, ACTIONS, RESULT, TERMINAL-TEST, UTILITY. Zero sum: one player\'s gain is the other\'s loss.')
K.must('Minimax', 'MAX takes max, MIN takes min, terminals give utility. Root value = what MAX can guarantee.')
K.must('Slide examples', '27 leaves: B1 = 5, B2 = 2, B3 = 3, A = 5. Tic-tac-toe: O takes the centre.')
K.must('Cost', 'Complete (finite), optimal against perfect play, O(b<sup>m</sup>) time, O(b m) space. Chess ≈ 10<sup>154</sup>.')
K.must('Cutoffs', 'Depth limit with EVAL = ∑ w<sub>i</sub> f<sub>i</sub>. Quiescence search, horizon effect.')

T = K.topic(
    slug='minimax', topic='minimax', step=(6, 'Adversarial search', 'cai-games', 'Search when an opponent moves too: minimax, alpha beta pruning, and games with chance.', 'College'),
    title='Games and minimax', short='Minimax', badge='6.1', minutes=45,
    lead='When an opponent moves too, plan for the reply. Write a game as a search problem, back values up the game tree with minimax, and see why real programs cut off the search and estimate.',
    desc='The formal game, kinds of games, zero sum, the minimax algorithm on the 27 leaf slide example and the slide tic-tac-toe position, completeness, optimality and cost, depth limits, evaluation functions, quiescence and the horizon effect.',
    summary='Game formalism, minimax values, the slide examples, the cost of minimax and evaluation functions.',
    keywords=['minimax', 'adversarial search', 'game tree', 'zero sum', 'evaluation function', 'tic-tac-toe', 'horizon effect'],
    recap='<p>MAX takes the max and MIN the min. The root value is what MAX can guarantee against perfect play.</p>',
    nb={'tree': 'Minimax on the 27 leaf slide example', 'ttt': 'Minimax on the slide tic-tac-toe position'})
