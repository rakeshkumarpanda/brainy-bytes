# Chapter 3.4: search with non deterministic actions, AND OR trees and AO*. Source: slide Set 2, slides 88 to 93
# (AND nodes and OR nodes, the and-or tree only specifies the search space, the AO* worked example and food for
# thought VII on its complexity and data structures) and the classes of 1 and 7 February 2026 (the television
# example: steal it, or earn money AND buy it, and the AO* example worked on the board). The erratic and slippery
# vacuum worlds, conditional and cyclic plans follow Russell and Norvig, AIMA 4th ed., section 4.3.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('andor', r'''
# AND OR search in the erratic vacuum world. A state is (where, A_dirty, B_dirty).
# Erratic Suck: on a dirty square it cleans it, and sometimes the other square too.
#               On a clean square it sometimes drops dirt.
def results(state, action):
    where, a, b = state
    if action == "Right":
        return [("B", a, b)]
    if action == "Left":
        return [("A", a, b)]
    if where == "A":
        if a == 1:
            return sorted(set([("A", 0, b), ("A", 0, 0)]))
        return [("A", 0, b), ("A", 1, b)]
    if b == 1:
        return sorted(set([("B", a, 0), ("B", 0, 0)]))
    return [("B", a, 0), ("B", a, 1)]

def is_goal(state):
    return state[1] == 0 and state[2] == 0

def or_search(state, path):
    if is_goal(state):
        return []
    if state in path:
        return None                       # a loop: give up on this branch
    for action in ["Suck", "Right", "Left"]:
        plan = and_search(results(state, action), [state] + path)
        if plan is not None:
            return [action, plan]
    return None

def and_search(states, path):
    plans = {}
    for s in states:                      # EVERY outcome needs a plan
        plan = or_search(s, path)
        if plan is None:
            return None
        plans[s] = plan
    return plans

print(or_search(("A", 1, 1), []))
''')

K.code('aostar', r'''
# AO* style bottom up costs on the AND OR graph of the slides. Every edge costs 1.
# A node has a list of connectors. A connector is a list of children that must ALL be solved.
graph = {"A": [["B"], ["C", "D"]], "B": [["E"], ["F"]], "C": [["G"], ["H", "I"]], "D": [["J"]]}
h = {"E": 7, "F": 9, "G": 3, "H": 0, "I": 0, "J": 0}   # the leaves: their exact cost

def cost(node):
    if node not in graph:
        return h[node]
    best = None
    for connector in graph[node]:
        total = 0
        for child in connector:
            total = total + 1 + cost(child)          # edge cost 1 plus the child's cost
        print(node, "via", "+".join(connector), "costs", total)
        if best is None or total < best:
            best = total
    return best

print("cost of A:", cost("A"))
''')

K.lesson('idea', 'When actions do not always do the same thing', f'''
{src('slide Set 2, slide 88, and the classes of 1 and 7 February 2026.')}
<p>So far every action had exactly one result. In many real problems an action can end in several states, and the agent only learns which one after acting. A floor cleaning robot\'s suction may also clean the next square, or may drop dirt. A delivery may arrive or get lost. Such actions are <b>non deterministic</b>.</p>
{wwh('An AND OR search tree has two kinds of nodes. At an OR node the agent chooses one action (at least one child must work). At an AND node nature chooses the outcome, so every child must be solved.',
     'With non deterministic actions a single sequence of actions is not enough. The agent needs a <b>contingency plan</b> (a conditional plan) that says what to do for each outcome: "Suck, and if the other square is still dirty then go Right and Suck".',
     'Search the AND OR tree depth first. At an OR node, try actions until one gives a plan. At an AND node, find a plan for every outcome, and fail if any one fails. Stop a branch when it reaches a state already on its path.')}
{scene('getting a television, from the class', '<p>You need a television. One way is to steal it. The other way is to earn money AND buy it. "Get a TV" is an OR node with two choices. "Earn money and buy" is an AND node: you must do both parts. An AND OR tree like this describes a problem broken into sub problems, also called <b>problem reduction</b>. The tree only describes the search space. You can search it depth first, breadth first or best first.</p>')}
{table(['', 'OR node', 'AND node'], [
    ['Who chooses', 'The agent', 'Nature (the environment)'],
    ['Solved when', 'At least one child is solved', 'Every child is solved'],
    ['Cost', 'The cheapest child (plus the edge)', 'The sum over all children (plus the edges)'],
    ['Drawn as', 'Separate branches', 'Branches joined by an arc']])}
''', kw=['non deterministic actions', 'contingency plan', 'conditional plan', 'AND OR tree', 'AND node', 'OR node', 'problem reduction'])

K.lesson('vacuum', 'The erratic vacuum world and AND OR search', f'''
<p>The vacuum world has 8 states: the robot is in square A or B, and each square is dirty or clean. States 7 and 8 (both clean) are goals. In the <b>erratic</b> version, Suck on a dirty square cleans it and sometimes also cleans the other square, and Suck on a clean square sometimes drops dirt on it.</p>
{viz('andor', world='erratic', s=1)}
{code('andor')}
{algo('AND-OR-SEARCH (AIMA figure 4.11)', [
    'function OR-SEARCH(state, path):',
    '    if GOAL-TEST(state): return the empty plan',
    '    if state is on path: return failure',
    '    for each action:',
    '        plan = AND-SEARCH(RESULTS(state, action), [state] + path)',
    '        if plan is not failure: return [action] + plan',
    '    return failure',
    '',
    'function AND-SEARCH(states, path):',
    '    for each s_i in states:',
    '        plan_i = OR-SEARCH(s_i, path)',
    '        if plan_i is failure: return failure',
    '    return [if s_1 then plan_1 else if s_2 then plan_2 ... else plan_n]'])}
<p>From state 1 the plan is <b>[Suck, if State = 5 then [Right, Suck] else []]</b>. If Suck cleaned both squares we are in state 7 and done. If it cleaned only A we are in state 5, so go Right and Suck.</p>
{note('Failing on a state already on the path does not miss solutions: if a plan exists from a repeated state, it also exists from its first occurrence. That keeps AND OR search complete on finite state spaces.', 'tip')}
''', kw=['erratic vacuum world', 'AND OR search', 'conditional plan', 'Suck', 'state 5', 'state 7'])

K.lesson('cyclic', 'Slippery worlds and cyclic plans', f'''
<p>In the <b>slippery</b> vacuum world, Right and Left sometimes fail and leave the robot where it is. Then every plan from state 5 can come back to state 5, which is on its path, so AND OR search finds no plan. But there is an obvious working plan: keep trying Right until it works.</p>
{viz('andor', world='slippery', s=1)}
{fxs(
    fx('A cyclic plan', '[Suck, L1: Right, if State = 5 then L1 else Suck]', 'L1 is a label. "if State = 5 then L1" means go back to the label and try Right again. In code it is a while loop: while State = 5: Right.', key=True),
    fx('When a cyclic plan is a solution', 'every leaf is a goal, and a goal can be reached from every point of the plan', 'Each try must succeed with some chance. If the floor is so slippery that Right never works, no plan helps.'))}
{note('A cyclic plan only works under a <b>fairness</b> assumption: an action that can succeed will succeed if you try it often enough. If the failure has a hidden cause (the wheel is broken), trying again is useless and the agent must learn the cause instead.', 'warn')}
''', kw=['slippery vacuum world', 'cyclic plan', 'while loop', 'label', 'fairness'])

K.lesson('aostar', 'AO*: best first search on AND OR graphs', f'''
{src('slide Set 2, slides 89 to 92, worked in the class of 7 February 2026.')}
{wwh('AO* is the AND OR version of A*. It keeps a best partial solution graph, expands one of its unexpanded nodes, and revises the costs back up to the root.',
     'AND OR search finds some plan. When the parts of a plan have costs, we want the cheapest solution graph, and AO* uses heuristic estimates to find it without expanding everything.',
     'Cost of an OR choice: the cheapest connector. Cost of an AND connector: the sum of its edges and children. After each expansion, propagate the new cost to the ancestors, mark the best connector at each node, and mark a node solved when every child on its best connector is solved. Stop when the root is solved.')}
{steps('The slide example (every edge costs 1)', [
    'Expand A. Through B: 1 + h(B) = 1 + 5 = 6. Through C AND D: 1 + 2 + 1 + 4 = 8. The best is B (6).',
    'Expand B. B → E costs 1 + 7 = 8 and B → F costs 1 + 9 = 10. So h(B) becomes 8.',
    'Revise A. Through B: 1 + 8 = 9. Through C AND D: still 8. Now C AND D is better, so A switches.',
    'Expand C. C → G costs 1 + 3 = 4 and C → H AND I costs 1 + 0 + 1 + 0 = 2. h(C) = 2 and C is solved (H and I are goals).',
    'Expand D. D → J costs 1 + 0 = 1. h(D) = 1 and D is solved.',
    eq('revise A: through C AND D = 1 + 2 + 1 + 1 = 5. A is solved with cost 5: A → C + D, C → H + I, D → J')])}
{viz('aostar', hs='B 5, C 2, D 4, E 7, F 9, G 3, H 0, I 0, J 0', ec=1)}
{note('Look closely at the slide numbers: h(D) = 4 but D really costs only 1 (D → J). So this h overestimates and is not admissible. Here AO* still ends at the best answer 5, but try the second tip (h(H) = 6): AO* stops at 9 while the true best is 7. Like A*, AO* is only guaranteed optimal when h never overestimates.', 'warn')}
{code('aostar')}
{algo('AO* (outline)', [
    'G = graph with only the start node, marked unsolved',
    'loop until start is solved or its cost is ∞:',
    '    follow the marked best connectors from the start and pick an unexpanded tip n',
    '    expand n: add its successors, estimate each new node with h',
    '    S = { n }',
    '    while S is not empty:',
    '        take a node m from S that has no descendant in S',
    '        cost(m) = min over connectors of ∑ (edge cost + cost(child))',
    '        mark that connector. m is solved if all its children on it are solved',
    '        if cost(m) changed or m became solved: add the parents of m to S'])}
''', kw=['AO*', 'AO star', 'best partial solution graph', 'connector', 'revise costs', 'solved'])

K.lesson('maths', 'The maths: cost of a solution graph and complexity', f'''
{fxs(
    fx('Cost at an OR node', 'cost(n) = min<sub>connectors k</sub> cost(n, k)', 'The agent picks the cheapest way.'),
    fx('Cost of an AND connector', 'cost(n, k) = ∑<sub>children c of k</sub> (C(n, c) + cost(c))', 'All parts must be done, so their costs add.', key=True),
    fx('Admissibility for AO*', 'h(n) ≤ the true cost of the best solution graph below n', 'With such an h, AO* returns an optimal solution graph (on graphs without cycles).'))}
{steps('Worked example: food for thought VII, the complexity of AO*', [
    'Like A*, AO* may need to expand every node in the worst case, so time and memory are exponential in the depth: O(b<sup>d</sup>).',
    'Each revision walks up to the root through the ancestors, which costs O(d) per expansion on a tree, more on a graph with shared nodes.',
    'Data structures: a dictionary from node to its list of connectors, its cost, its marked connector and a solved flag, plus a parent list for each node to propagate costs upward.',
    eq('time and space O(b<sup>d</sup>), with an O(d) revision after each expansion on a tree')])}
{steps('Worked example: the size of a conditional plan', [
    'Each AND node with k outcomes multiplies the number of branches by k.',
    'A plan of 3 actions, each with 2 possible outcomes, may need 2³ = 8 branches.',
    eq('conditional plans can be exponentially larger than plain action sequences')])}
''', kw=['cost of solution graph', 'AO* complexity', 'data structures'])

K.lesson('compare', 'AND OR search against ordinary search', f'''
{versus('Plain search, AND OR search and AO*', ['', 'A* or BFS', 'AND OR search (DFS)', 'AO*'], [
    ['Actions', 'Deterministic', 'Non deterministic, or problems split into parts', 'Same as AND OR, with costs'],
    ['Solution', 'A path (a list of actions)', 'A tree: a conditional plan', 'The cheapest solution graph'],
    ['Uses h', 'A*: yes', 'No', 'Yes'],
    ['Handles loops', 'Explored set', 'Fails on a repeated state, cyclic plans need labels', 'Classic AO* assumes no cycles (LAO* handles them)'],
    ['Example', 'Romania route', 'Erratic vacuum plan', 'Slide graph, cost 5']],
    'use plain search when actions are certain, AND OR search when you need any plan that works for every outcome, and AO* when the parts have costs and you want the cheapest plan.')}
{versus('Contingency planning against probabilistic planning', ['', 'AND OR (contingency)', 'Markov decision process (chapter 10.1)'], [
    ['Outcomes', 'A set of possible states', 'States with probabilities'],
    ['Goal', 'Reach a goal in every outcome', 'Maximise expected reward'],
    ['Result', 'Conditional plan', 'Policy for every state']],
    'when you know the chances of each outcome, an MDP can trade a small risk for a big gain, which an AND OR plan cannot.')}
''', kw=['comparison', 'LAO*', 'MDP', 'contingency planning'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Sometimes you cannot be sure what happens after you act. So you plan for every case: "if it rains, take the bus, otherwise walk". An AND OR tree writes down all those cases.</p>',
    '<p>OR nodes are the agent\'s choices, AND nodes are nature\'s outcomes. AND OR search returns a conditional plan, failing a branch that repeats a state on its path. Slippery worlds need cyclic plans. AO* finds the cheapest solution graph by expanding the best partial graph and revising costs upward.</p>',
    '<p>AO* is optimal with an admissible h on acyclic graphs. Plans can grow exponentially with the number of uncertain steps. For partially observable worlds the same search runs over belief states (sets of possible states), and sensing actions split a belief state into AND branches.</p>',
    '<p>LAO* extends AO* to cyclic graphs and is a bridge to MDP solvers. Fully observable non deterministic (FOND) planners such as PRP find strong cyclic plans for large planning benchmarks, and AND OR search is used in game solving and in proof search for theorem provers.</p>')}
{deep('belief states', '<p>If the agent cannot see the state, it tracks the set of states it might be in, its belief state. With 8 vacuum states there are 2⁸ = 256 belief states. A sensorless agent can still solve the vacuum world: [Right, Suck, Left, Suck] cleans both squares from any start, moving the belief state from all 8 states to {7}.</p>')}
''', kw=['belief state', 'FOND planning', 'LAO*', 'sensorless'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'With <b>non deterministic</b> actions, the agent needs a contingency (conditional) plan, not a single sequence.',
    'In an AND OR tree, OR nodes are the agent\'s choices (one child must work) and AND nodes are nature\'s outcomes (every child must work).',
    '<b>AND OR search</b> is a depth first search that fails a branch when a state repeats on its path. Erratic vacuum from state 1: [Suck, if State = 5 then [Right, Suck] else []].',
    'In a slippery world no plan without loops exists. A <b>cyclic plan</b> such as [Suck, L1: Right, if State = 5 then L1 else Suck] works if each try can succeed.',
    '<b>AO*</b>: expand the best partial solution graph, add costs at AND connectors, take the min at OR nodes, and revise upward. The slide example ends at 5 via C AND D.'],
    'chapter 4.1 drops paths entirely: local search keeps only the current state and improves it step by step.')}
{nbcard('and-or-search', 'Run AND OR search on the erratic vacuum world and the AO* costs of the slide graph, then write cost propagation and a plan checker yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'At an AND node of an AND OR tree,', ['One child must be solved', 'Every child must be solved', 'No child matters', 'The agent chooses'], 1,
       'All parts.', 'Nature picks the outcome, so each outcome needs a plan.')
K.quiz('e', 'At an OR node,', ['The agent chooses one action', 'Every child must be solved', 'Nature chooses', 'The cost is a sum'], 0,
       'A choice.', 'At least one child must work.')
K.quiz('e', 'In the class example, "earn money and buy a television" is', ['An OR node', 'An AND node', 'A goal', 'A heuristic'], 1,
       'Both parts.', 'You must earn the money AND buy the TV.')
K.quiz('e', 'A plan for non deterministic actions is called', ['A path', 'A contingency or conditional plan', 'A heuristic', 'A policy gradient'], 1,
       'It has if then branches.', 'It says what to do for each possible outcome.')
K.quiz('m', 'In the erratic vacuum world, Suck in state 1 can lead to', ['Only 5', '5 or 7', '1 or 5', '7 or 8'], 1,
       'Cleans A, maybe B too.', 'State 5 (A clean, B dirty) or state 7 (both clean).')
K.quiz('m', 'Why does AND OR search fail a branch when a state is already on its path?', ['To save time only', 'A plan from the repeat would also work from the first occurrence, so nothing is lost', 'Loops are always solutions', 'It is a bug'], 1,
       'Completeness is kept.', 'Any non cyclic plan can avoid repeating a state.')
K.quiz('m', 'In the slide AO* example, after B is expanded, the cost of A through B becomes', ['6', '8', '9', '5'], 2,
       '1 + h(B), h(B) is now 8.', '1 + 8 = 9, more than C AND D at 8, so A switches.')
K.quiz('m', 'The cost of an AND connector is', ['The min over its children', 'The sum of edge costs and children costs', 'The max of its children', 'Always 1'], 1,
       'All parts are paid for.', 'Every child must be done, so the costs add.')
K.quiz('h', 'A cyclic plan is a valid solution only if', ['It has no labels', 'Every action that can succeed eventually does (fairness)', 'The world is deterministic', 'h is admissible'], 1,
       'Keep trying.', 'If a failure is permanent, looping never ends.')
K.quiz('h', 'Classic AO* can be wrong on graphs with', ['Cycles', 'AND nodes', 'Edge costs of 1', 'Zero heuristics'], 0,
       'Revisions loop.', 'Cost revision assumes no cycles. LAO* handles cyclic graphs.')
K.quiz('x', 'In the style of an IIT Kharagpur exam: in the slide graph, set h(H) = 6 and run AO*. It returns 9 via B. The true cheapest solution costs 7. Why?', ['AO* is never optimal', 'h(D) = 4 overestimates the true cost of D, which is 1, so h is not admissible', 'The graph has a cycle', 'Edge costs are 1'], 1,
       'Compare h(D) with the real cost below D.', 'D → J costs only 1. With h(D) = 4, C AND D looks like 10, so AO* never expands D and stops at B with 9. With an admissible h it would find A → C + D = 7.')
K.quiz('x', 'In the style of a Berkeley CS188 question: a sensorless vacuum agent does not know its start state. Which plan cleans both squares from every start?', ['[Suck]', '[Right, Suck]', '[Right, Suck, Left, Suck]', 'No plan exists'], 2,
       'Visit both squares and suck in each.', 'After Right the robot is surely in B. Suck cleans B. Left puts it in A, Suck cleans A.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'AO* slide example: cost of A through B at the start, with edge cost 1 and h(B) = 5.', '6', 'Edge plus h.',
       ['Edge A to B: 1.', 'h(B) = 5.', eq('1 + 5 = 6')], check=6)
K.calc('e', 'Cost of A through C AND D at the start: edges 1 each, h(C) = 2, h(D) = 4.', '8', 'Add both parts.',
       ['C part: 1 + 2 = 3.', 'D part: 1 + 4 = 5.', eq('3 + 5 = 8')], check=8)
K.calc('e', 'Cost of C → H AND I with h(H) = h(I) = 0 and edges 1.', '2', 'Two edges.',
       ['1 + 0.', '1 + 0.', eq('2')], check=2)
K.calc('m', 'Final cost of A through C AND D, with cost(C) = 2 and cost(D) = 1.', '5', 'Edges plus children.',
       ['1 + 2 = 3.', '1 + 1 = 2.', eq('3 + 2 = 5')], check=5)
K.calc('m', 'How many states does the two square vacuum world have?', '8', '2 locations × 2 × 2.',
       ['Robot in A or B: 2.', 'Each square dirty or clean: 2 × 2.', eq('2 × 2 × 2 = 8')], check=8)
K.calc('m', 'How many belief states (sets of states) exist for the 8 vacuum states, counting the empty set?', '256', '2⁸.',
       ['Each state is in the set or not.', '2 choices for each of 8 states.', eq('2⁸ = 256')], check=256)
K.calc('m', 'A plan has 4 steps and each step has 2 possible outcomes. How many leaves can the conditional plan have?', '16', '2⁴.',
       ['Each AND node doubles the branches.', 'Four of them.', eq('2⁴ = 16')], check=16)
K.calc('h', 'In the slide graph set h(H) = 6. What is the cost of C → H AND I now?', '8', '1 + 6 + 1 + 0.',
       ['H part: 1 + 6 = 7.', 'I part: 1 + 0 = 1.', eq('8, so C prefers G with 4')], check=8)
K.calc('h', 'With h(H) = 6, what is the cost of A through C AND D, using cost(C) = 4 and h(D) = 4?', '10', 'Add.',
       ['1 + 4 = 5.', '1 + 4 = 5.', eq('10, so A → B with 9 wins')], check=10)
K.calc('x', 'In the style of a CMU exam: an action succeeds with probability 0.25 and otherwise leaves the state unchanged. How many tries does a cyclic plan need on average? (Mean of a geometric distribution, 1 ⁄ p.)', '4', '1 ⁄ 0.25.',
       ['Each try is independent and succeeds with p = 0.25.', 'The expected number of tries is 1 ⁄ p.', eq('1 ⁄ 0.25 = 4 tries')], check=4)

# ---------------------------------------------------------------- assignments
GR = "{'A': [['B'], ['C', 'D']], 'B': [['E'], ['F']], 'C': [['G'], ['H', 'I']], 'D': [['J']]}"
K.assign('aocost', 'm', 'Cost of the best solution graph',
         '<p>Write <code>best_cost(graph, leaf, node)</code>. graph maps a node to a list of connectors (lists of children). leaf maps each leaf to its exact cost. Every edge costs 1. Return the cost of the cheapest solution graph below node: the min over connectors of the sum of (1 + cost of each child).</p>',
         '''
def best_cost(graph, leaf, node):
    # your code here
    pass
''', [(f"best_cost({GR}, {{'E': 7, 'F': 9, 'G': 3, 'H': 0, 'I': 0, 'J': 0}}, 'A')", 5),
      (f"best_cost({GR}, {{'E': 7, 'F': 9, 'G': 3, 'H': 6, 'I': 0, 'J': 0}}, 'A')", 7),
      (f"best_cost({GR}, {{'E': 7, 'F': 9, 'G': 3, 'H': 0, 'I': 0, 'J': 0}}, 'B')", 8),
      ("best_cost({}, {'X': 4}, 'X')", 4)],
         '''
def best_cost(graph, leaf, node):
    if node not in graph:
        return leaf[node]
    best = None
    for connector in graph[node]:
        total = 0
        for child in connector:
            total = total + 1 + best_cost(graph, leaf, child)
        if best is None or total < best:
            best = total
    return best
''', 'A leaf returns its own cost. Otherwise add up each connector and keep the smallest total.', '<p>This is the true optimum. AO* reaches it while expanding only part of the graph, but only if h never overestimates. With h(H) = 6 the true best is 7 (A → C + D, C → G, D → J), while AO* with the slide estimate h(D) = 4 stops at 9.</p>')
K.assign('plancheck', 'h', 'Does a conditional plan always reach the goal?',
         '<p>The erratic vacuum world is given by <code>results(state, action)</code> below. A plan is [] (done) or [action, {state: plan, ...}] with a sub plan for every outcome. Write <code>works(state, plan)</code> that returns True if following the plan from state always ends in a state with both squares clean, else False.</p>',
         '''
def results(state, action):
    where, a, b = state
    if action == "Right":
        return [("B", a, b)]
    if action == "Left":
        return [("A", a, b)]
    if where == "A":
        if a == 1:
            return sorted(set([("A", 0, b), ("A", 0, 0)]))
        return [("A", 0, b), ("A", 1, b)]
    if b == 1:
        return sorted(set([("B", a, 0), ("B", 0, 0)]))
    return [("B", a, 0), ("B", a, 1)]

def works(state, plan):
    # your code here
    pass
''', [("works(('A', 1, 1), ['Suck', {('A', 0, 0): [], ('A', 0, 1): ['Right', {('B', 0, 1): ['Suck', {('B', 0, 0): []}]}]}])", True),
      ("works(('A', 1, 1), ['Suck', {('A', 0, 0): []}])", False),
      ("works(('A', 0, 0), [])", True),
      ("works(('A', 1, 0), [])", False)],
         '''
def results(state, action):
    where, a, b = state
    if action == "Right":
        return [("B", a, b)]
    if action == "Left":
        return [("A", a, b)]
    if where == "A":
        if a == 1:
            return sorted(set([("A", 0, b), ("A", 0, 0)]))
        return [("A", 0, b), ("A", 1, b)]
    if b == 1:
        return sorted(set([("B", a, 0), ("B", 0, 0)]))
    return [("B", a, 0), ("B", a, 1)]

def works(state, plan):
    if len(plan) == 0:
        return state[1] == 0 and state[2] == 0
    action = plan[0]
    branches = plan[1]
    for s in results(state, action):
        if s not in branches:
            return False
        if not works(s, branches[s]):
            return False
    return True
''', 'For an action, every outcome must appear in the dict and its sub plan must work.', '<p>The second test fails because the plan has no branch for state (A, 0, 1).</p>')

K.must('AND and OR nodes', 'OR: the agent chooses, one child must work. AND: nature chooses, every child must work.')
K.must('Contingency plan', 'Erratic vacuum from state 1: [Suck, if State = 5 then [Right, Suck] else []].')
K.must('AND OR search', 'DFS that fails a branch on a state already on its path. Complete on finite spaces.')
K.must('Cyclic plan', 'Slippery world: [Suck, L1: Right, if State = 5 then L1 else Suck]. Needs fairness.')
K.must('AO*', 'Expand the best partial graph, AND = sum, OR = min, revise upward. Slide example: 6, then 9 against 8, ends at 5. Optimal only with admissible h.')

T = K.topic(
    slug='and-or-search', topic='and-or-search', step=(3, 'Informed search', 'cai-informed', 'Search with a hint of where the goal is: greedy best first, A*, heuristic design, memory bounded and AND OR search.', 'College'),
    title='AND OR search and AO*', short='AND OR and AO*', badge='3.4', minutes=50,
    lead='When an action can end in several states, a list of actions is not enough. AND OR trees describe the agent\'s choices and nature\'s outcomes, AND OR search builds a plan with if then branches, and AO* finds the cheapest one.',
    desc='Non deterministic actions, AND and OR nodes, the television example, the erratic vacuum world, AND OR search and conditional plans, slippery worlds and cyclic plans, AO* on the slide graph, its complexity, and a comparison with plain search and MDPs.',
    summary='AND OR trees, conditional and cyclic plans, AND OR search on the erratic vacuum world, and AO* on the slide example.',
    keywords=['AND OR search', 'AO*', 'conditional plan', 'contingency plan', 'erratic vacuum world', 'cyclic plan', 'non deterministic'],
    recap='<p>OR nodes choose, AND nodes cover every outcome. AND OR search returns a conditional plan, AO* the cheapest one.</p>',
    nb={'andor': 'AND OR search in the erratic vacuum world', 'aostar': 'Cost of the best solution graph on the slide example'})
