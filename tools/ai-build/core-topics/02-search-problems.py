# Chapter 1.2: problems as search. Source: slide Set 2, slides 1 to 24 (why search, the holiday from Edinburgh to
# London, the formalism: state space, actions, initial state and goal, heuristics, the Romania and water jug examples,
# the inputs and outputs of a search algorithm, successor functions annotated with actions, the node fields STATE,
# PARENT, ACTION and PATH-COST, the OPEN set, cycles, the selection rule, the four properties, food for thought I)
# and the class of 24 January 2026 (the class itself as a search problem: states, transitions, heuristics, constraints).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('jugs', r'''
# The water jug problem from the slides: a 3 gallon jug and a 4 gallon jug.
# A state is a pair (gal3, gal4). The successor function lists every state one action away.
def successors(state):
    gal3, gal4 = state
    result = []
    result.append(("Fill-3", (3, gal4)))
    result.append(("Fill-4", (gal3, 4)))
    result.append(("Empty-3", (0, gal4)))
    result.append(("Empty-4", (gal3, 0)))
    pour = min(gal3, 4 - gal4)
    result.append(("Pour-3-into-4", (gal3 - pour, gal4 + pour)))
    pour = min(gal4, 3 - gal3)
    result.append(("Pour-4-into-3", (gal3 + pour, gal4 - pour)))
    return result

for action, new_state in successors((0, 0)):
    print(action, "->", new_state)
''')

K.code('node', r'''
# A search node remembers its state, its parent node, the action that made it, and the path cost g.
class Node:
    def __init__(self, state, parent=None, action=None, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = cost

    def path(self):
        # follow the parent links back to the start, then reverse
        states = []
        node = self
        while node is not None:
            states.append(node.state)
            node = node.parent
        states.reverse()
        return states

start = Node("Arad")
n1 = Node("Sibiu", start, "go Sibiu", 140)
n2 = Node("Fagaras", n1, "go Fagaras", 140 + 99)
n3 = Node("Bucharest", n2, "go Bucharest", 140 + 99 + 211)
print("path:", n3.path())
print("cost:", n3.path_cost)
''')

K.lesson('idea', 'Why search, and what a search problem is', f'''
{src('slide Set 2 (Searching Techniques), slides 1 to 24, and the class of 24 January 2026.')}
<p>You are on holiday in Edinburgh and your flight leaves from London tomorrow. You think: "If I take the 6 am train, where will I be at 2 pm? Will I still reach the airport on time?" This is <b>hypothetical reasoning</b>: you imagine what state you will be in after some actions, and look for a sequence of actions that brings you to a state you want. <b>Search</b> is the computer\'s way of doing exactly this.</p>
{wwh('A general method that tries out sequences of actions, on paper, to find one that turns the start state into a goal state.',
     'Many problems have no special formula, but they can be written as states and actions. Search then solves them all with one method. It is the hidden engine inside route finders, puzzle solvers, game players and planners.',
     'Write the problem as a state space with actions, a start and a goal test. Keep a list of paths still to explore (the frontier, also called OPEN). Repeatedly take a path out, check if it ends at a goal, and if not, extend it by every action.')}
<h3>Why search works well, and where it stops</h3>
{table(['Why search', 'Limits of search'], [
    ['Game playing programs based on search beat world champions.', 'Search does not tell you how to <b>formulate</b> the problem. Choosing the states and actions is up to you.'],
    ['Many problems have no special algorithm. Casting them as search is often the easiest way.', 'Search only solves a problem once it is correctly formulated.'],
    ['Local search gives good approximations for huge optimisation problems.', 'Without good knowledge (heuristics) it can be very slow.'],
    ['Problem specific heuristics let search use extra knowledge, and planning can be cast as search.', '']])}
{scene('a teacher in class', '<p>In class the professor described her own lecture as a search problem. The start state is "I have just said something and five of you look confused". The goal state is "everybody understands". Each transition is a new example or a new explanation. The heuristic is her sense of which example will help most, and a constraint is the time left in the class. Because students keep asking questions, the next state is never fully known in advance, so she keeps choosing again. That is a search through states, done live.</p>')}
''', kw=['search', 'hypothetical reasoning', 'state', 'goal', 'why search', 'limits of search'])

K.lesson('formal', 'The formalism: states, actions, start, goal', f'''
<p>To turn a problem into a search problem, write down four things.</p>
{table(['Part', 'Meaning', 'Romania trip', 'Water jugs'], [
    ['State space', 'All configurations the problem can be in, kept as computer data', 'The city you are in', 'Pairs (gal3, gal4), gallons in each jug'],
    ['Actions (transitions)', 'Moves from one state to another', 'Drive to a neighbouring city', 'Fill, empty, or pour one jug into the other'],
    ['Initial state and goal', 'Where you start and the condition you want', 'In Arad, goal: be in Bucharest', 'Start (0, 0), goal e.g. (0, 2) or (*, 3)'],
    ['Heuristics', 'Hints that guide the search', 'Straight line distance to Bucharest', 'How far each jug is from the target amount']])}
<p><b>Abstraction</b> means leaving out details that do not matter. For Romania we ignore the radio, the weather and where exactly on the road the car is. We keep only the city. A good abstraction keeps what you need to find a valid plan and nothing more.</p>
{viz('searchgraph', alg='bfs', gr='jugs', ja=3, jb=4, jw=2)}
{code('jugs')}
<p>Observations from the slides about the jugs: from whole numbers you only ever reach whole numbers. Some states, for example (1, 2), can never be reached from (0, 0). Some actions do not change the state at all, for example emptying an empty jug. Of the 4 × 5 = 20 possible pairs, only 14 can be reached from (0, 0).</p>
{note('The goal can be a <b>condition</b>, not one state. "(*, 3)" means any state where the 4 gallon jug holds 3, whatever the 3 gallon jug holds. The goal test is a function that returns true or false.', 'tip')}
''', kw=['state space', 'actions', 'initial state', 'goal test', 'abstraction', 'water jugs', 'Romania'])

K.lesson('inout', 'Inputs, outputs and nodes of a search algorithm', f'''
<p>Every search algorithm in this course gets the same inputs and returns the same kind of answer.</p>
{fxs(
    fx('Successor function', 'S(x) = {⟨y, a⟩ : action a takes x to y}', 'All states one action away from x, each tagged with the action used. Two different actions may reach the same state.', key=True),
    fx('Action cost', 'C(x, a, y) ≥ ε &gt; 0', 'The cost of going from x to y with action a. C = ∞ if a does not lead from x to y. Every cost is at least a small positive ε.'),
    fx('Path cost', 'g(n) = ∑<sub>i</sub> C(s<sub>i</sub>, a<sub>i</sub>, s<sub>i+1</sub>)', 'Add the costs along the path from the start to node n.', key=True))}
<p>The output is a sequence of states (or actions) from the start to a state that passes the goal test. Some algorithms promise the cheapest path, some the shortest, some promise nothing.</p>
<h3>A node is a path</h3>
<p>A <b>node</b> is a bookkeeping record for one path. It has four fields: <b>n.STATE</b> (the state it ends in), <b>n.PARENT</b> (the node it came from), <b>n.ACTION</b> (the action that made it) and <b>n.PATH-COST</b>, written g(n). Following PARENT links back to the start rebuilds the whole path.</p>
{code('node')}
{algo('The search template (slide 18)', [
    'function TREE-SEARCH(problem):',
    '    frontier = { node(initial state) }',
    '    loop:',
    '        if frontier is empty: return failure',
    '        n = take a node out of the frontier      # the selection rule',
    '        if GOAL-TEST(n.STATE): return the path of n',
    '        add every child of n to the frontier',
    '',
    'function GRAPH-SEARCH(problem):',
    '    same, but keep an explored set:',
    '    add n.STATE to explored after taking n out,',
    '    and add a child only if its state is not in the frontier or explored'])}
{note('Cycles can cause non termination. Arad → Sibiu → Arad → Sibiu ... is a valid path in tree search, so a search may never stop. Graph search fixes this by remembering explored states.', 'warn')}
''', kw=['successor function', 'action cost', 'path cost', 'node', 'parent', 'frontier', 'OPEN', 'tree search', 'graph search', 'explored set'])

K.lesson('props', 'The selection rule and the four properties', f'''
<p>Every search algorithm in chapters 2 to 4 follows the template above. They differ in one thing only: <b>which node they take out of the frontier next</b> (the selection rule). This choice decides whether a solution is found, how much it costs, and the time and memory needed.</p>
{table(['Property', 'Question it answers'], [
    ['Completeness', 'If a solution exists, will the algorithm always find one?'],
    ['Optimality', 'Will it find the cheapest solution (when actions have costs)?'],
    ['Time complexity', 'How many nodes does it generate before it finds a solution?'],
    ['Space complexity', 'What is the largest number of nodes it must keep in memory?']])}
{fxs(
    fx('Branching factor and depth', 'b = most children of any node, d = depth of the shallowest goal, m = largest depth', 'These three numbers measure every algorithm.'),
    fx('Nodes in a full tree', '1 + b + b² + ... + b<sup>d</sup> = (b<sup>d+1</sup> − 1) ⁄ (b − 1) = O(b<sup>d</sup>)', 'The number of nodes up to depth d. It grows exponentially with d.', key=True))}
{steps('Worked example: how big is a search tree?', [
    'Take b = 10 and d = 5.',
    eq('1 + 10 + 100 + 1,000 + 10,000 + 100,000 = 111,111 nodes'),
    'At 1 million nodes a second this takes about 0.1 seconds.',
    'With d = 10 it is about 1.1 × 10¹⁰ nodes, which takes about 3 hours. One more level multiplies the work by b.'])}
{viz('searchgraph', alg='bfs', gr='romania', start='Arad', goal='Bucharest')}
<h3>Food for thought from the slides</h3>
<p>Try to write each of these as a search problem with states, actions, start and goal: making a cup of tea, buying a book online, picking an example to explain a doubt in class, and a doctor\'s differential diagnosis. For tea, a state could be (water boiled?, tea in cup?, milk added?, sugar added?), and actions boil, add tea, add milk, add sugar, stir.</p>
''', kw=['selection rule', 'completeness', 'optimality', 'time complexity', 'space complexity', 'branching factor', 'depth'])

K.lesson('maths', 'The maths behind search problems', f'''
{fxs(
    fx('Size of a state space', '|S| = product of the number of values of each part of the state', 'Jugs: 4 values for gal3 (0 to 3) × 5 for gal4 (0 to 4) = 20 states, of which 14 are reachable from (0, 0).'),
    fx('8 puzzle reachable states', '9! ⁄ 2 = 181,440', 'Nine tiles (with the blank) in 9! orders, but only half can be reached from a given start, because a move never changes the parity of the arrangement.', key=True),
    fx('Paths are much bigger than states', 'tree nodes up to depth d ≈ b<sup>d</sup> while states may be few', 'In a grid with 4 moves, a tree search to depth d makes 4<sup>d</sup> paths but only about 2d² distinct cells are within d steps. This is why graph search remembers explored states.', key=True))}
{steps('Worked example: why repeated states matter in a grid', [
    'Robot on an open grid, 4 moves: up, down, left, right. b = 4.',
    'Tree search to depth 10: 1 + 4 + ... + 4¹⁰ = (4¹¹ − 1) ⁄ 3 = 1,398,101 nodes.',
    'Cells within 10 steps (a diamond): 2 × 10² + 2 × 10 + 1 = 221.',
    eq('Graph search touches at most 221 states, about 6,000 times fewer')])}
''', kw=['state space size', '8 puzzle', 'repeated states', 'geometric series', 'diamond'])

K.lesson('compare', 'How problem formulation choices compare', f'''
{versus('Tree search against graph search', ['', 'Tree search', 'Graph search'], [
    ['Remembers explored states?', 'No', 'Yes (explored set)'],
    ['Can loop for ever on cycles?', 'Yes', 'No, on a finite state space'],
    ['Memory', 'Only the frontier', 'Frontier plus every explored state'],
    ['Best when', 'The space is a true tree, or memory is very tight', 'Many paths lead to the same state (maps, puzzles)']],
    'use graph search when states repeat, which is almost always. Use tree search with a path check when memory is the problem (as in depth first search, chapter 2.2).')}
{versus('Good and bad formulations of 8 queens', ['Formulation', 'States', 'Comment'], [
    ['Add one queen at a time anywhere', '64 × 63 × ... × 57 ≈ 1.8 × 10¹⁴ sequences', 'Very wasteful'],
    ['Add one queen per column, in a row not attacked', '2,057 states', 'Same problem, tiny space'],
    ['Complete state: 8 queens, one per column, move a queen in its column', '8⁸ ≈ 16.8 million states', 'Used by local search (chapter 4.1, 5.3)']],
    'the same puzzle can be easy or hard depending on how you choose states and actions. Formulation is the most important step, and search cannot do it for you.')}
''', kw=['tree search', 'graph search', 'formulation', '8 queens'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Search is trying out moves in your head before you make them, like planning a train trip by checking which trains connect.</p>',
    '<p>A search problem has a state space, actions with costs, a start and a goal test. Nodes are paths with STATE, PARENT, ACTION and PATH-COST. Algorithms differ only in the selection rule, and are judged on completeness, optimality, time and space in terms of b, d and m.</p>',
    '<p>Graph search removes repeated states but needs memory for the explored set. The size of the reachable state space, not the tree, then bounds the work. Choosing the abstraction (what to keep in a state) can shrink a problem by many orders of magnitude.</p>',
    '<p>Automatically finding good abstractions and problem formulations is still open. Modern planners learn state representations and action models from data, and large language models are used to propose formulations that a classical search then solves exactly.</p>')}
{deep('why the 8 puzzle has exactly 9! ⁄ 2 reachable states', '<p>Read the tiles in row order, ignoring the blank, and count inversions (pairs in the wrong order). A sideways move does not change this order. An up or down move jumps a tile over two others, which changes the number of inversions by 0 or ±2. So the parity of the inversion count never changes. Half of the 9! arrangements have each parity, and every arrangement with the right parity can be reached, so exactly 9! ⁄ 2 = 181,440 states are reachable.</p>')}
{note('Exam questions often ask you to formulate a problem. Always list all four parts: states, actions (with costs), initial state, goal test. Say how big the state space is.', 'exam')}
''', kw=['abstraction', 'formulation', 'inversions', 'parity'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Search is hypothetical reasoning: imagine sequences of actions and look for one that reaches the goal.',
    'A search problem has a <b>state space</b>, <b>actions</b> with costs C(x, a, y) ≥ ε &gt; 0, an <b>initial state</b> and a <b>goal test</b>. Heuristics are optional hints.',
    'A node is a path: STATE, PARENT, ACTION, PATH-COST g(n). The frontier (OPEN) holds paths waiting to be extended.',
    'Tree search can loop on cycles. Graph search keeps an explored set and never expands a state twice.',
    'Algorithms differ only in the <b>selection rule</b>. Judge them by completeness, optimality, time and space, using b, d and m. A full tree to depth d has (b<sup>d+1</sup> − 1) ⁄ (b − 1) nodes.'],
    'chapter 2.1 gives the first two selection rules: breadth first and uniform cost search.')}
{nbcard('search-problems', 'Generate water jug successors, rebuild paths from nodes, and code your own successor function and path cost.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which of these is NOT one of the parts of a search problem?', ['Initial state', 'Goal test', 'Actions', 'A neural network'], 3,
       'Four parts.', 'State space, actions, initial state and goal (plus optional heuristics).')
K.quiz('e', 'In the Romania problem, a state is', ['A road', 'The city you are in', 'The whole map', 'The fuel left'], 1,
       'Abstraction.', 'We keep only the current city and leave out every other detail.')
K.quiz('e', 'The frontier (OPEN set) holds', ['Explored states', 'Paths that are waiting to be extended', 'Goal states only', 'Action costs'], 1,
       'Waiting list.', 'It is the set of leaf nodes available for expansion.')
K.quiz('e', 'What makes one search algorithm different from another in the template?', ['The goal test', 'Which node is taken out of the frontier next', 'The programming language', 'The start state'], 1,
       'The selection rule.', 'The order of selection from OPEN decides everything else.')
K.quiz('m', 'Which state cannot be reached from (0, 0) in the 3 and 4 gallon jug problem?', ['(3, 1)', '(0, 2)', '(1, 2)', '(2, 4)'], 2,
       'The slides name one.', 'Only 14 of the 20 pairs are reachable, and (1, 2) is not one of them.')
K.quiz('m', 'Why can tree search fail to terminate on Romania?', ['Costs are negative', 'Cycles like Arad, Sibiu, Arad, ... are valid paths', 'The map is too big', 'There is no goal'], 1,
       'Going back and forth.', 'Without an explored set the same states repeat for ever.')
K.quiz('m', 'A node stores STATE, PARENT, ACTION and', ['DEPTH-LIMIT', 'PATH-COST', 'HEURISTIC', 'GOAL'], 1,
       'g(n).', 'PATH-COST, written g(n), is the cost from the start to this node.')
K.quiz('m', 'Completeness means', ['It finds the cheapest solution', 'It finds a solution whenever one exists', 'It uses little memory', 'It is fast'], 1,
       'Always finds one.', 'Optimality is the cheapest. Completeness is finding one at all.')
K.quiz('h', 'How many nodes does a full tree with b = 3 and d = 4 have?', ['81', '121', '243', '40'], 1,
       '(3⁵ − 1) ⁄ 2.', '1 + 3 + 9 + 27 + 81 = 121.')
K.quiz('h', 'How many states of the 8 puzzle are reachable from a given start?', ['9!', '9! ⁄ 2', '8!', '2⁹'], 1,
       'Parity.', 'Moves keep the parity of inversions, so exactly half of 9! = 181,440.')
K.quiz('x', 'In the style of an IIT entrance to AI course: in graph search, when is a child NOT added to the frontier?', ['When its cost is high', 'When its state is already in the frontier or the explored set', 'When it is a goal', 'Never'], 1,
       'The two sets.', 'Graph search skips states already seen. Uniform cost and A* may still replace a frontier entry with a cheaper path.')
K.quiz('x', 'In the style of a CMU 15-381 question: which change to a formulation can turn an exponential tree search into a polynomial graph search on a grid?', ['Adding more actions', 'Detecting repeated states', 'Using a deeper goal', 'Removing the goal test'], 1,
       'Paths against cells.', 'A grid has about 2d² cells within d steps but 4<sup>d</sup> paths, so remembering states removes the blow up.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Romania: what is the cost of Arad → Sibiu → Fagaras → Bucharest? Roads 140, 99, 211.', '450', 'Add the three roads.',
       ['140 + 99 = 239.', '239 + 211 = 450.', eq('g = 450')], check=140 + 99 + 211)
K.calc('e', 'Romania: what is the cost of Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest? Roads 140, 80, 97, 101.', '418', 'Add the four roads.',
       ['140 + 80 = 220.', '220 + 97 = 317.', eq('317 + 101 = 418')], check=140 + 80 + 97 + 101)
K.calc('e', 'Jugs of 3 and 4 gallons. How many pairs (gal3, gal4) exist in total?', '20', 'gal3 has 4 values, gal4 has 5.',
       ['gal3 can be 0, 1, 2 or 3: 4 values.', 'gal4 can be 0 to 4: 5 values.', eq('4 × 5 = 20')], check=20)
K.calc('m', 'Jugs: how many states are reachable from (0, 0)?', '14', 'Explore by breadth first.',
       ['Depth 0: (0,0). Depth 1: (3,0), (0,4). Depth 2: (3,4), (0,3), (3,1).', 'Depth 3: (3,3), (0,1). Depth 4: (2,4), (1,0). Depth 5: (2,0), (1,4). Depth 6: (0,2), (3,2).', eq('1 + 2 + 3 + 2 + 2 + 2 + 2 = 14')], check=14)
K.calc('m', 'Jugs: what is the fewest number of actions to get 2 gallons in the 4 gallon jug, starting from (0, 0)?', '6', 'The depth of (0, 2) or (3, 2).',
       ['(0,0) → (3,0) → (0,3) → (3,3) → (2,4) → (2,0) → (0,2).', 'That is 6 actions.', eq('depth of (0, 2) = 6')], check=6)
K.calc('m', 'Nodes in a full tree with b = 10 and d = 5?', '111111', 'Use (b<sup>d+1</sup> − 1) ⁄ (b − 1).',
       ['10⁶ − 1 = 999,999.', 'Divide by 9.', eq('111,111')], check=(10 ** 6 - 1) // 9)
K.calc('m', 'Tree search on an open grid with 4 moves to depth 10. How many nodes?', '1398101', '(4¹¹ − 1) ⁄ 3.',
       ['4¹¹ = 4,194,304.', 'Minus 1 is 4,194,303.', eq('÷ 3 = 1,398,101')], check=(4 ** 11 - 1) // 3)
K.calc('h', 'Cells within 10 moves of a start cell on an open grid (the diamond 2d² + 2d + 1)?', '221', 'd = 10.',
       ['2 × 100 = 200.', '2 × 10 = 20, plus 1.', eq('200 + 20 + 1 = 221')], check=2 * 100 + 20 + 1)
K.calc('h', 'How many states of the 8 puzzle are reachable from a given start?', '181440', '9! ⁄ 2.',
       ['9! = 362,880.', 'Half keep the right parity.', eq('362,880 ⁄ 2 = 181,440')], check=181440)
K.calc('x', 'In the style of a Stanford CS221 exam: at 1 million nodes a second, how many seconds does a full tree search with b = 10, d = 8 take? Use (b<sup>d+1</sup> − 1) ⁄ (b − 1). Round to 1 decimal.', '111.1', 'Count the nodes first.',
       ['(10⁹ − 1) ⁄ 9 = 111,111,111 nodes.', 'Divide by 1,000,000 a second.', eq('≈ 111.1 seconds')], check=111.111111, tol=0.06)

# ---------------------------------------------------------------- assignments
K.assign('succ', 'e', 'Successors of a water jug state',
         '<p>Write <code>jug_successors(gal3, gal4)</code> that returns the sorted list of distinct states (as [gal3, gal4] lists) one action away, for a 3 gallon and a 4 gallon jug. Leave out the state itself if an action does not change it.</p>',
         '''
def jug_successors(gal3, gal4):
    # your code here
    pass
''', [("jug_successors(0, 0)", [[0, 4], [3, 0]]), ("jug_successors(3, 0)", [[0, 0], [0, 3], [3, 4]]), ("jug_successors(2, 4)", [[0, 4], [2, 0], [3, 3], [3, 4]])],
         '''
def jug_successors(gal3, gal4):
    states = []
    states.append([3, gal4])
    states.append([gal3, 4])
    states.append([0, gal4])
    states.append([gal3, 0])
    pour = min(gal3, 4 - gal4)
    states.append([gal3 - pour, gal4 + pour])
    pour = min(gal4, 3 - gal3)
    states.append([gal3 + pour, gal4 - pour])
    result = []
    for s in states:
        if s != [gal3, gal4] and s not in result:
            result.append(s)
    result.sort()
    return result
''', 'List all six actions, then remove repeats and the unchanged state.', '<p>This is the successor function S(x) of the slides for the jug problem.</p>')
K.assign('pathcost', 'm', 'Cost of a path on the Romania map',
         '<p>Write <code>path_cost(path, roads)</code>. roads is a dict like {"Arad-Sibiu": 140, ...} with each road written once in any direction. Return the total cost, or -1 if some step has no road.</p>',
         '''
def path_cost(path, roads):
    # your code here
    pass
''', [("path_cost(['Arad', 'Sibiu', 'Fagaras', 'Bucharest'], {'Arad-Sibiu': 140, 'Sibiu-Fagaras': 99, 'Bucharest-Fagaras': 211})", 450),
      ("path_cost(['Arad', 'Bucharest'], {'Arad-Sibiu': 140})", -1), ("path_cost(['Arad'], {})", 0)],
         '''
def path_cost(path, roads):
    total = 0
    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]
        if a + "-" + b in roads:
            total = total + roads[a + "-" + b]
        elif b + "-" + a in roads:
            total = total + roads[b + "-" + a]
        else:
            return -1
    return total
''', 'Look up each pair in both directions.', '<p>This is g(n), the path cost of the slides.</p>')

K.must('Search problem', 'State space, actions with costs C(x, a, y) ≥ ε &gt; 0, initial state, goal test (a condition). Heuristics are optional.')
K.must('Node', 'STATE, PARENT, ACTION, PATH-COST g(n). Follow PARENT links to rebuild the path.')
K.must('Tree against graph search', 'Tree search can loop on cycles. Graph search keeps an explored set and skips seen states.')
K.must('Four properties', 'Completeness, optimality, time and space, measured with b, d and m. Full tree: (b<sup>d+1</sup> − 1) ⁄ (b − 1) nodes.')
K.must('Water jugs', '14 of 20 states reachable from (0, 0). (1, 2) unreachable. Getting 2 gallons in the 4 gallon jug takes 6 actions.')
K.must('Formulation', 'Search cannot choose the states for you. A good abstraction can shrink the space enormously (8 queens: 1.8 × 10¹⁴ to 2,057).')

T = K.topic(
    slug='search-problems', topic='search-problems', step=(1, 'Intelligence, agents and problems', 'cai-found', 'What AI is, how an agent senses and acts, and how a goal becomes a search problem.', 'School and college'),
    title='Problems as search', short='Problems as search', badge='1.2', minutes=45,
    lead='Turn a goal into a search problem: states, actions, a start and a goal test. Learn what a node, the frontier and the explored set are, and the four properties used to judge every search algorithm.',
    desc='Why search, the holiday example, the formalism with the Romania map and the water jugs, successor functions, nodes, the tree and graph search template, cycles, the selection rule and completeness, optimality, time and space.',
    summary='States, actions, start and goal, nodes and the frontier, tree against graph search, and the four properties of search.',
    keywords=['search problem', 'state space', 'successor function', 'node', 'frontier', 'graph search', 'water jugs', 'Romania'],
    recap='<p>Write a problem as states, actions, a start and a goal test. Every search algorithm keeps a frontier of paths and differs only in which path it extends next.</p>',
    nb={'jugs': 'The successor function of the water jug problem', 'node': 'Search nodes and rebuilding a path'})
