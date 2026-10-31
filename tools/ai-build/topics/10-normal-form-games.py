# Chapter 4.1: static games, complete information and the normal form. Source: lecture 5 (multi agent interaction
# along two axes, static against dynamic as observation not clock time, complete information and its four parts,
# common knowledge and the course boycott example, the normal form game N, S_i, v_i, profiles, finite and infinite
# games, the bimatrix convention, the Prisoner's Dilemma story and payoffs, best responses and a first look at
# dominance, practice problem D) and lecture 6 (the s_-i notation and unilateral deviation).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('game', r'''
# A finite two player game as a dictionary from profile to (payoff 1, payoff 2)
S1, S2 = ["M", "C"], ["M", "C"]
v = {("M", "M"): (-2, -2), ("M", "C"): (-5, -1),
     ("C", "M"): (-1, -5), ("C", "C"): (-4, -4)}

def best_responses_1(s2):
    top = max(v[(s1, s2)][0] for s1 in S1)
    return [s1 for s1 in S1 if v[(s1, s2)][0] == top]

def best_responses_2(s1):
    top = max(v[(s1, s2)][1] for s2 in S2)
    return [s2 for s2 in S2 if v[(s1, s2)][1] == top]

for s2 in S2:
    print("if player 2 plays", s2, "player 1's best reply:", best_responses_1(s2))
for s1 in S1:
    print("if player 1 plays", s1, "player 2's best reply:", best_responses_2(s1))
''')

K.code('deviate', r'''
# Unilateral deviation: from a profile, can any single player gain by changing only her own choice?
S = ["M", "C"]
v = {("M", "M"): (-2, -2), ("M", "C"): (-5, -1), ("C", "M"): (-1, -5), ("C", "C"): (-4, -4)}

for prof in v:
    gains = []
    for i in (0, 1):
        for alt in S:
            new = list(prof)
            new[i] = alt
            if v[tuple(new)][i] > v[prof][i]:
                gains.append(f"player {i + 1} to {alt}")
    print(prof, v[prof], "->", gains if gains else "no one gains alone, self enforcing")
''')

K.lesson('static', 'Many agents: static games of complete information', f'''
<p>Up to now one agent faced nature. From lecture 5 on, several rational agents face each other, and each one\'s payoff depends on what everyone does. The course places such interactions on two axes.</p>
{table(['Axis', 'One end', 'Other end'], [
    ['What do players know about each other?', 'Complete information', 'Incomplete information'],
    ['When do players act?', 'Static: choose without seeing others\' choices', 'Dynamic: some players see earlier moves']])}
<p>This step studies the corner that is static with complete information. "Static" does not mean everyone acts at the same clock time. It means no player sees what any other player actually chose before choosing. Thinking about what the other might do is allowed. Seeing what they did is not.</p>
{steps('Practice problem D: static or dynamic?', [
    'Sealed tenders opened together after both are submitted: static. Neither bidder sees the other bid.',
    'Chess: dynamic. Every move is seen before the next one.',
    'Two candidates reveal platforms at the same moment, drafted without seeing each other: static.',
    eq('Poker betting, where each player sees earlier bets: dynamic')])}
<h3>Complete information and common knowledge</h3>
<p>Complete information means four things are common knowledge: every player\'s possible actions, the possible outcomes, how each combination of actions leads to an outcome, and every player\'s preferences. Common knowledge is stronger than everyone knowing. Everyone knows it, everyone knows that everyone knows it, and so on without end.</p>
{fxs(fx('Common knowledge', '<i>E</i> is common knowledge ⟺ (everyone knows)<sup><i>n</i></sup> <i>E</i> for every <i>n</i> = 1, 2, 3, …', 'Knowing a fact privately is mutual knowledge. Common knowledge needs the whole infinite chain.', key=True))}
{scene('the class boycott', '<p>The professor used the course itself. Grades are relative. Suppose the whole class secretly agrees that nobody writes anything in the exam. For that to hold, each student must be sure every other student is committed, and sure that everyone else is sure, and so on. The moment anyone suspects one classmate might study, writing a little becomes very attractive under relative grading. Without common knowledge of commitment, the boycott unravels.</p>')}
''', kw=['static game', 'dynamic game', 'complete information', 'common knowledge', 'mutual knowledge', 'practice problem D'])

K.lesson('normal', 'The normal form of a game', f'''
<p>A static game of complete information is written as a normal form game, also called the strategic form. It has three ingredients.</p>
{fxs(
    fx('Normal form game', '⟨ <i>N</i>, {{<i>S</i><sub><i>i</i></sub>}}, {{<i>v</i><sub><i>i</i></sub>}} ⟩', 'N = {1, …, n} players. Sᵢ = pure strategies of player i. vᵢ = payoff of player i.', key=True),
    fx('Strategy profile', '<i>s</i> = (<i>s</i>₁, …, <i>s</i><sub><i>n</i></sub>) ∈ <i>S</i>₁ × … × <i>S</i><sub><i>n</i></sub>', 'One choice per player. In a static game a strategy is simply an action.'),
    fx('Payoff function', '<i>v</i><sub><i>i</i></sub> : <i>S</i>₁ × … × <i>S</i><sub><i>n</i></sub> → ℝ', 'Your payoff depends on the whole profile, not only on your own choice.', key=True),
    fx('Everyone else', '<i>s</i><sub>−<i>i</i></sub> = (<i>s</i>₁, …, <i>s</i><sub><i>i</i>−1</sub>, <i>s</i><sub><i>i</i>+1</sub>, …, <i>s</i><sub><i>n</i></sub>)', 'Read "s minus i". We write s = (sᵢ, s₋ᵢ).'))}
<p>A game is finite when there are finitely many players and each has finitely many strategies. If even one player has infinitely many, such as any quantity in [0, ∞), the game is infinite.</p>
<h3>The bimatrix convention</h3>
<p>For two players with finite strategies, draw a table. Rows are player 1\'s strategies and columns player 2\'s. Each cell holds two numbers: the row player\'s payoff first, then the column player\'s.</p>
<h3>The Prisoner\'s Dilemma</h3>
<p>Two suspects are held in separate rooms. Each can stay mum (M) or confess (C). Both mum: 2 years each. Both confess: 4 years each. One confesses: the confessor gets 1 year and the other 5. A year in prison is worth −1.</p>
{table(['Player 1 (rows), Player 2 (columns)', 'M', 'C'], [['M', '(−2, −2)', '(−5, −1)'], ['C', '(−1, −5)', '(−4, −4)']])}
{viz('bimatrix')}
''', kw=['normal form', 'strategic form', 'strategy profile', 'payoff function', 'bimatrix', "Prisoner's Dilemma", 's minus i'])

K.lesson('br', 'Best responses and unilateral deviation', f'''
<p>A best response is your best choice when you take the others\' choices as fixed.</p>
{fxs(
    fx('Best response', '<i>s</i><sub><i>i</i></sub> ∈ BR<sub><i>i</i></sub>(<i>s</i><sub>−<i>i</i></sub>) ⟺ <i>v</i><sub><i>i</i></sub>(<i>s</i><sub><i>i</i></sub>, <i>s</i><sub>−<i>i</i></sub>) ≥ <i>v</i><sub><i>i</i></sub>(<i>s</i>′<sub><i>i</i></sub>, <i>s</i><sub>−<i>i</i></sub>) for all <i>s</i>′<sub><i>i</i></sub>', 'Hold everyone else fixed and maximize your own payoff.', key=True),
    fx('Unilateral deviation', 'from <i>s</i> to (<i>s</i>′<sub><i>i</i></sub>, <i>s</i><sub>−<i>i</i></sub>)', 'Only player i changes. A profile where no unilateral deviation helps anyone is self enforcing.'))}
{steps('Best responses in the Prisoner\'s Dilemma', [
    'If player 2 plays M, player 1 compares −2 (M) with −1 (C). C is better.',
    'If player 2 plays C, player 1 compares −5 (M) with −4 (C). C is better again.',
    'So C is player 1\'s best reply whatever player 2 does. The game is symmetric, so the same holds for player 2.',
    eq('Both confess and get (−4, −4), although (−2, −2) was better for both')])}
{code('game')}
{code('deviate')}
{note('A best response is computed against fixed choices of the others. It is not a guess about what they will do. Whether the others actually play those choices is what a solution concept, in chapter 4.3, decides.', 'tip')}
{deep('Static games and extensive form', '<p>A static game is a normal form game. A dynamic game is drawn as a tree, the extensive form, with information sets that group nodes a player cannot tell apart. A static game is the special case where each player\'s whole move sits in one information set, because she has seen nothing. Every extensive form game also has a normal form, whose strategies are full contingent plans, as in the R&D tree of chapter 3.1.</p>')}
{ladder(
    '<p>In a game, what you get depends on what others choose too. A table lists every combination of choices and what each player gets from it.</p>',
    '<p>A normal form game has players N, strategy sets Sᵢ and payoffs vᵢ on profiles. Static means unobserved choices, not same time. Complete information makes actions, outcomes, the map and preferences common knowledge. Best responses hold s₋ᵢ fixed.</p>',
    '<p>Common knowledge is the fixed point of the everyone knows operator. Aumann\'s agreement theorem and the muddy children puzzle show how public announcements create it. Normal forms of extensive games can be reduced by merging equivalent strategies.</p>',
    '<p>Multi agent reinforcement learning builds empirical normal form games from trained policies (PSRO, Lanctot et al. 2017) and computes best responses with RL. Epistemic game theory studies which solution concepts follow from which assumptions about knowledge and rationality.</p>')}
''', kw=['best response', 'unilateral deviation', 'self enforcing', 'extensive form', 'information set', 'dominance preview'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A game is static when', ['All players act at the same clock time', 'No player sees another\'s actual choice before choosing', 'Payoffs do not change', 'There are two players'], 1,
       'Observation, not time.', 'Static is about what is observed, not about when actions happen.')
K.quiz('e', 'In a bimatrix cell (a, b), a is', ['The column player\'s payoff', 'The row player\'s payoff', 'The total', 'A probability'], 1,
       'Row first.', 'The first number belongs to the row player.')
K.quiz('e', 'The three parts of a normal form game are', ['Players, strategies, payoffs', 'Actions, outcomes, probabilities', 'States, rewards, policies', 'Players, trees, chance'], 0,
       '⟨N, S, v⟩.', 'A set of players, a strategy set for each, and a payoff function for each.')
K.quiz('e', 'Chess is', ['Static', 'Dynamic', 'Zero player', 'Infinite'], 1,
       'You see every move.', 'Each player observes earlier moves before choosing.')
K.quiz('m', 'Common knowledge of E means', ['Everyone knows E', 'Everyone knows E, knows that everyone knows E, and so on forever', 'E is written down', 'At least one player knows E'], 1,
       'An infinite chain.', 'Everyone knowing E is only mutual knowledge.')
K.quiz('m', 'In the Prisoner\'s Dilemma, player 1\'s best response to M is', ['M', 'C', 'Both', 'Neither'], 1,
       '−1 against −2.', 'Confessing gives −1, staying mum −2.')
K.quiz('m', 'A Cournot game where quantities can be any number in [0, ∞) is', ['Finite', 'Infinite', 'Zero sum', 'Dynamic'], 1,
       'Count the strategies.', 'An infinite strategy set makes the game infinite, even with two players.')
K.quiz('m', 's₋ᵢ denotes', ['Player i\'s strategy', 'The profile with player i\'s entry removed', 'The negative of sᵢ', 'A mixed strategy'], 1,
       'Minus i.', 'It lists every other player\'s choice.')
K.quiz('h', 'Why is (M, M) in the Prisoner\'s Dilemma not self enforcing?', ['It is not Pareto optimal', 'Each player gains by confessing alone', 'It needs mixed strategies', 'It is the worst outcome'], 1,
       'Unilateral deviation.', 'From (M, M) each player can move to C and get −1 instead of −2.')
K.quiz('h', 'Which of these is NOT part of complete information in lecture 5?', ['All actions', 'All outcomes', 'Everyone\'s preferences', 'What each player will actually choose'], 3,
       'Knowing the game, not the play.', 'Complete information is about the structure of the game. Choices are what the analysis predicts.')
K.quiz('x', 'How many pure strategy profiles does a game with 3 players having 2, 3 and 4 strategies have?', ['9', '12', '24', '81'], 2,
       'Multiply.', '2 × 3 × 4 = 24.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Prisoner\'s Dilemma: what is v₁(C, M)?', '-1', 'Player 1 confesses, player 2 stays mum.',
       ['The confessor gets 1 year.', 'Each year counts −1.', eq('v₁(C, M) = −1')], check=-1)
K.calc('e', 'How many profiles does the Prisoner\'s Dilemma have?', '4', 'Two strategies each.',
       ['Player 1: 2 strategies.', 'Player 2: 2 strategies.', eq('2 × 2 = 4')], check=4)
K.calc('e', 'Three players each choose 0 or 1. How many profiles?', '8', 'Multiply.',
       ['Each player has 2 choices.', 'By the counting principle, multiply.', eq('2³ = 8')], check=8)
K.calc('m', 'Prisoner\'s Dilemma: by how much does player 1 gain by deviating from (M, M) to (C, M)?', '1', 'Compare −2 and −1.',
       ['At (M, M) player 1 gets −2.', 'At (C, M) player 1 gets −1.', eq('gain = −1 − (−2) = 1')], check=1)
K.calc('m', 'Prisoner\'s Dilemma: what is the total payoff at (C, C) and at (M, M)? Give the difference (M, M) minus (C, C).', '4', 'Add both players.',
       ['(C, C): −4 + −4 = −8.', '(M, M): −2 + −2 = −4.', eq('−4 − (−8) = 4')], check=4)
K.calc('m', 'A game has 4 players with 3 strategies each. How many profiles?', '81', 'Power.',
       ['Each player has 3 strategies.', 'Profiles = 3 × 3 × 3 × 3.', eq('3⁴ = 81')], check=81)
K.calc('m', 'In a 3 × 3 bimatrix, how many cells must player 1 compare to find all her best responses?', '9', 'One column at a time.',
       ['For each of 3 columns, compare 3 entries.', '3 columns × 3 rows.', eq('9 entries')], check=9)
K.calc('h', 'In a 2 player game with m and k strategies, how many unilateral deviations must be checked to test one profile?', '5', 'Take m = 3, k = 4.',
       ['Player 1 can switch to any of m − 1 other rows.', 'Player 2 can switch to any of k − 1 other columns.', eq('(3 − 1) + (4 − 1) = 5')], check=5)
K.calc('h', 'Prisoner\'s Dilemma: how many of the 4 profiles have at least one profitable unilateral deviation?', '3', 'Check each cell.',
       ['(M, M): both gain by confessing.', '(M, C): player 1 gains by confessing. (C, M): player 2 gains.', '(C, C): moving to M gives −5 &lt; −4, nobody gains.', eq('3 profiles')], check=3)
K.calc('h', 'With 5 players each choosing 0 or 1, how many profiles have exactly 2 contributors?', '10', 'Choose 2 of 5.',
       ['A profile with exactly 2 ones picks which 2 players contribute.', 'C(5, 2) = 5 × 4 ÷ 2.', eq('= 10')], check=10)
K.calc('x', 'A normal form game has n players with 2 strategies each. How many numbers must the full payoff table store?', '384', 'Take n = 6.',
       ['Profiles: 2⁶ = 64.', 'Each profile stores one payoff per player: 6.', eq('64 × 6 = 384')], check=384)

# ---------------------------------------------------------------- assignments
K.assign('br', 'e', 'Best responses in a bimatrix',
         '<p>Write <code>best_rows(table, col)</code>. table is a list of rows, each a list of [a, b] cells. Return the sorted list of row indices that are best responses of the row player to column col.</p>',
         '''
def best_rows(table, col):
    # your code here
    pass
''', [("best_rows([[[-2, -2], [-5, -1]], [[-1, -5], [-4, -4]]], 0)", [1]), ("best_rows([[[1, 1], [0, 0]], [[1, 1], [2, 1]]], 0)", [0, 1]),
      ("best_rows([[[4, 3], [5, 1]], [[2, 1], [8, 4]], [[3, 0], [9, 6]]], 1)", [2])],
         '''
def best_rows(table, col):
    vals = [row[col][0] for row in table]
    top = max(vals)
    return [i for i, x in enumerate(vals) if x == top]
''', 'Collect the row player\'s payoffs in that column, then keep every row equal to the maximum.', '<p>The second test has a tie. A best response is a set, as arg max was in chapter 1.3.</p>')
K.assign('stable', 'm', 'Find the self enforcing cells',
         '<p>Write <code>stable_cells(table)</code> for a bimatrix (list of rows of [a, b]). Return the sorted list of [row, col] where no player gains by a unilateral deviation.</p>',
         '''
def stable_cells(table):
    # your code here
    pass
''', [("stable_cells([[[-2, -2], [-5, -1]], [[-1, -5], [-4, -4]]])", [[1, 1]]), ("stable_cells([[[4, 4], [0, 3]], [[3, 0], [3, 3]]])", [[0, 0], [1, 1]]),
      ("stable_cells([[[1, -1], [-1, 1]], [[-1, 1], [1, -1]]])", [])],
         '''
def stable_cells(table):
    out = []
    R, C = len(table), len(table[0])
    for r in range(R):
        for c in range(C):
            a, b = table[r][c]
            if all(table[r2][c][0] <= a for r2 in range(R)) and all(table[r][c2][1] <= b for c2 in range(C)):
                out.append([r, c])
    return out
''', 'A cell is stable when its first number is the largest in its column and its second number is the largest in its row.',
         '<p>These are the pure Nash equilibria that later chapters will name. Stag Hunt has two, Matching Pennies has none.</p>')

K.must('Two axes', 'Complete vs incomplete information. Static (no one sees others\' choices) vs dynamic. Static is about observation, not clock time.')
K.must('Common knowledge', 'Everyone knows, everyone knows everyone knows, forever. Complete info: actions, outcomes, map, preferences are common knowledge.')
K.must('Normal form', '⟨N, Sᵢ, vᵢ⟩ with vᵢ on full profiles. Finite if all Sᵢ finite. Bimatrix cell = (row payoff, column payoff).')
K.must('Prisoner\'s Dilemma', '(M,M) = (−2,−2), (M,C) = (−5,−1), (C,M) = (−1,−5), (C,C) = (−4,−4). C is the best reply to both.')
K.must('Best response', 'BRᵢ(s₋ᵢ) maximizes vᵢ(·, s₋ᵢ). A profile with no profitable unilateral deviation is self enforcing.')

T = K.topic(
    slug='normal-form-games', topic='normal-form-games', step=(4, 'Games between rational agents', 'aai-games', 'Model interactions between several rational agents: normal form games, Cournot, Bertrand, public goods, solution concepts and Pareto optimality.', 'College and masters'),
    title='Static games and the normal form', short='Normal form', badge='4.1', minutes=40,
    lead='Move from one decision maker to several: what static and complete information really mean, how to write a game as players, strategies and payoffs, and how to read best responses off a table.',
    desc='The two axes of multi agent interaction, static against dynamic, complete information and common knowledge with the class boycott example, the normal form ⟨N, S, v⟩, profiles and s₋ᵢ, finite and infinite games, the bimatrix convention, the Prisoner\'s Dilemma, best responses and unilateral deviation, and practice problem D.',
    summary='Static games of complete information, common knowledge, the normal form, the Prisoner\'s Dilemma and best responses.',
    keywords=['game theory', 'normal form', 'static game', 'common knowledge', "Prisoner's Dilemma", 'best response', 'bimatrix'],
    recap='<p>A static game lists players, their strategies and a payoff for every profile. Static means choices are unseen, and complete information means the whole game is common knowledge. In the Prisoner\'s Dilemma confessing is the best reply to anything.</p>')
