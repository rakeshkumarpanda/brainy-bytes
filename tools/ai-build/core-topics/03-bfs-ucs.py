# Chapter 2.1: breadth first and uniform cost search. Source: slide Set 2, slides 25 to 39 (uninformed strategies,
# BFS on the water jugs with the OPEN sets of slide 27 and the numbered tree of slide 28, BFS properties and the
# 450 against 418 example, the time and space complexity of slide 31, uniform cost search with the Sibiu example
# of slide 34, its completeness and optimality, and the three lemma proof of optimality on slides 36 to 38).
# The memory table and the C*/ε bound follow Russell and Norvig, Artificial Intelligence: A Modern Approach, 3rd ed., figure 3.13 and section 3.4.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('bfs', r'''
# Breadth first search on the water jug problem (jugs of 3 and 4 gallons).
# Goal: either jug holds exactly 2 gallons. The frontier is a plain list used as a queue.
def successors(state):
    a, b = state
    pour_ab = min(a, 4 - b)
    pour_ba = min(b, 3 - a)
    return [(3, b), (a, 4), (0, b), (a, 0), (a - pour_ab, b + pour_ab), (a + pour_ba, b - pour_ba)]

def bfs(start):
    frontier = [[start]]          # a list of paths, oldest first
    seen = [start]
    while len(frontier) > 0:
        path = frontier.pop(0)    # take the OLDEST path (first in, first out)
        for child in successors(path[-1]):
            if child not in seen:
                new_path = path + [child]
                if 2 in child:    # goal test when the child is generated
                    return new_path
                seen.append(child)
                frontier.append(new_path)
    return None

answer = bfs((0, 0))
print("path:", answer)
print("actions needed:", len(answer) - 1)
''')

K.code('ucs', r'''
# Uniform cost search on the slide 34 problem: from Sibiu to Bucharest.
# The frontier holds (cost, path) pairs. We always take out the cheapest one.
roads = {
    "Sibiu": [("Rimnicu Vilcea", 80), ("Fagaras", 99)],
    "Rimnicu Vilcea": [("Pitesti", 97)],
    "Fagaras": [("Bucharest", 211)],
    "Pitesti": [("Bucharest", 101)],
    "Bucharest": [],
}

def ucs(start, goal):
    frontier = [(0, [start])]
    done = []
    while len(frontier) > 0:
        frontier.sort()                 # cheapest path first
        cost, path = frontier.pop(0)
        city = path[-1]
        print("take out", city, "with cost", cost)
        if city == goal:                # goal test when the path is taken OUT
            return cost, path
        done.append(city)
        for nxt, step in roads[city]:
            if nxt not in done:
                frontier.append((cost + step, path + [nxt]))
    return None

print(ucs("Sibiu", "Bucharest"))
''')

K.lesson('idea', 'Uninformed search and breadth first search', f'''
{src('slide Set 2, slides 25 to 31, and the classes of 24 and 25 January 2026.')}
<p><b>Uninformed</b> (or blind) search uses a fixed rule to choose the next node. The rule is the same for every problem and uses no knowledge about where the goal is. The five uninformed methods of the course are breadth first, uniform cost, depth first, depth limited and iterative deepening search.</p>
{wwh('Breadth first search (BFS) expands the shallowest node first. It looks at every path of length 1, then every path of length 2, and so on, level by level.',
     'When every action costs the same, the shallowest goal is also the cheapest. BFS is guaranteed to find it, and it never gets lost down one long branch.',
     'Keep the frontier as a first in, first out queue. Take the oldest path out, and add its children at the back. Because children always go to the back, all short paths are taken out before any longer one.')}
<h3>BFS on the water jugs, as on slide 27</h3>
<p>Start (0, 0), goal (*, 2). The frontier after each expansion (newly added paths at the end):</p>
{table(['Step', 'OPEN'], [
    ['0', '⟨(0,0)⟩'],
    ['1', '⟨(0,0),(3,0)⟩, ⟨(0,0),(0,4)⟩'],
    ['2', '⟨(0,0),(0,4)⟩, ⟨(0,0),(3,0),(0,0)⟩, ⟨(0,0),(3,0),(3,4)⟩, ⟨(0,0),(3,0),(0,3)⟩'],
    ['3', '⟨(0,0),(3,0),(0,0)⟩, ⟨(0,0),(3,0),(3,4)⟩, ⟨(0,0),(3,0),(0,3)⟩, ⟨(0,0),(0,4),(0,0)⟩, ⟨(0,0),(0,4),(3,4)⟩, ⟨(0,0),(0,4),(3,1)⟩']])}
<p>The slide shows tree search, so (0, 0) appears again as a child. Our code below uses graph search and skips states already seen.</p>
{viz('searchgraph', alg='bfs', gr='jugs', ja=3, jb=4, jw=2)}
{code('bfs')}
{algo('Breadth first search (graph version)', [
    'function BFS(problem):',
    '    node = start node',
    '    if GOAL-TEST(node.STATE): return node',
    '    frontier = FIFO queue with node',
    '    reached = { start state }',
    '    while frontier is not empty:',
    '        node = POP the oldest node',
    '        for each child of node:',
    '            if child.STATE not in reached:',
    '                if GOAL-TEST(child.STATE): return child      # early goal test',
    '                add child.STATE to reached',
    '                push child at the back of frontier',
    '    return failure'])}
''', kw=['uninformed search', 'blind search', 'breadth first search', 'BFS', 'FIFO queue', 'water jugs'])

K.lesson('bfsprops', 'Is BFS complete and optimal, and what does it cost', f'''
<p><b>Complete:</b> yes, if b is finite. The length of the path taken out of OPEN never goes down, because each expanded path is replaced by paths one step longer. So all paths of length d are examined before any of length d + 1, and a goal at depth d is found.</p>
<p><b>Optimal:</b> it finds the solution with the <b>fewest actions</b>. That is the cheapest only if every action costs the same. On Romania, BFS returns Arad, Sibiu, Fagaras, Bucharest (cost 140 + 99 + 211 = 450), but the cheapest route is Arad, Sibiu, Rimnicu Vilcea, Pitesti, Bucharest (140 + 80 + 97 + 101 = 418).</p>
{fxs(
    fx('Time of BFS', '1 + b + b² + ... + b<sup>d</sup> = O(b<sup>d</sup>)', 'With the goal test when a node is generated. If you test only when a node is taken out, the last level is generated too and the time is O(b<sup>d+1</sup>).', key=True),
    fx('Space of BFS', 'O(b<sup>d−1</sup>) explored + O(b<sup>d</sup>) frontier = O(b<sup>d</sup>)', 'Every node stays in memory. Memory, not time, is the real limit of BFS.', key=True))}
{table(['Depth d', 'Nodes (b = 10)', 'Time at 1 million nodes a second', 'Memory at 1 KB a node'], [
    ['2', '110', '0.11 ms', '107 KB'],
    ['4', '11,110', '11 ms', '10.6 MB'],
    ['6', '10⁶', '1.1 s', '1 GB'],
    ['8', '10⁸', '2 minutes', '103 GB'],
    ['10', '10¹⁰', '3 hours', '10 TB'],
    ['12', '10¹²', '13 days', '1 PB'],
    ['14', '10¹⁴', '3.5 years', '99 PB']])}
{note('Two lessons from the table. Memory runs out long before time does. And no amount of faster hardware saves you: each extra level multiplies the cost by b.', 'warn')}
{steps('Worked example: goal test at generation against at expansion', [
    'b = 2, goal at depth d = 3, and the goal is the last node of its level.',
    'Test at generation: we stop when the goal is generated, after 1 + 2 + 4 + 8 = 15 nodes at most.',
    'Test at expansion: every node of depth 3 is expanded before the goal is popped, so depth 4 is generated too: up to 15 + 16 = 31 nodes.',
    eq('early test: O(b<sup>d</sup>)   late test: O(b<sup>d+1</sup>)')])}
''', kw=['completeness', 'optimality', 'shortest path', 'time complexity', 'space complexity', 'early goal test'])

K.lesson('ucs', 'Uniform cost search', f'''
{src('slide Set 2, slides 32 to 35.')}
{wwh('Uniform cost search (UCS) always expands the path with the lowest path cost g(n). It is breadth first search ordered by cost instead of by depth.',
     'Real actions have different costs. Roads have different lengths, flights have different prices. BFS ignores costs. UCS returns the cheapest path.',
     'Keep the frontier as a priority queue ordered by g(n). Take out the cheapest path. Do the goal test only when a path is taken out, because a cheaper path to the goal may still be waiting. If a cheaper path to a state already in the frontier appears, replace the old one.')}
<h3>The Sibiu example of slide 34</h3>
{steps('Uniform cost search from Sibiu to Bucharest', [
    'Expand Sibiu. Its children Rimnicu Vilcea (80) and Fagaras (99) go into the frontier.',
    'The cheapest is Rimnicu Vilcea (80). Expand it and add Pitesti with cost 80 + 97 = 177.',
    'The cheapest is now Fagaras (99). Expand it and add Bucharest with cost 99 + 211 = 310.',
    'A goal is in the frontier, but UCS does not stop. It takes out the cheapest, Pitesti (177), and finds a second path to Bucharest with cost 177 + 101 = 278.',
    '278 is less than 310, so the old Bucharest path is discarded.',
    eq('Bucharest (278) is taken out next, so the answer is Sibiu, Rimnicu Vilcea, Pitesti, Bucharest, cost 278')])}
{code('ucs')}
{viz('searchgraph', alg='ucs', gr='romania', start='Arad', goal='Bucharest')}
<p>From Arad, UCS takes cities out in this order of cost: Arad 0, Zerind 75, Timisoara 118, Sibiu 140, Oradea 146, Rimnicu Vilcea 220, Lugoj 229, Fagaras 239, Mehadia 299, Pitesti 317, Craiova 366, Drobeta 374 and finally Bucharest 418. It spreads out in all directions like a growing circle of equal cost, because it has no idea where Bucharest is.</p>
{fxs(
    fx('Complete and optimal', 'if every action cost C(x, a, y) ≥ ε &gt; 0', 'With zero cost actions UCS can loop for ever on a zero cost cycle.'),
    fx('Time and space of UCS', 'O(b<sup>1 + ⌊C*⁄ε⌋</sup>)', 'C* is the cost of the optimal solution and ε the smallest action cost. The search may go about C*⁄ε levels deep. When all costs are equal this is b<sup>d+1</sup>.', key=True))}
''', kw=['uniform cost search', 'UCS', 'priority queue', 'path cost', 'Dijkstra', 'Sibiu', 'late goal test'])

K.lesson('proof', 'Why uniform cost search is optimal: the three lemmas', f'''
{src('slide Set 2, slides 36 to 38.')}
<p>Let c(n) be the cost of the path of node n. Assume every action costs at least ε &gt; 0.</p>
{steps('Lemma 1: costs taken out never go down', [
    'Claim: if n2 is expanded immediately after n1, then c(n1) ≤ c(n2).',
    'Case 1, n2 was already on OPEN when n1 was chosen. Then c(n1) ≤ c(n2), or else UCS would have chosen n2.',
    'Case 2, n2 was added when n1 was expanded. Then n2 extends n1 by one action, so c(n2) ≥ c(n1) + ε &gt; c(n1).',
    eq('either way c(n1) ≤ c(n2)')])}
{steps('Lemma 2: every cheaper path is expanded first', [
    'Claim: when n is expanded, every path with cost strictly less than c(n) has already been expanded.',
    'Take such a path n<sub>k</sub> = ⟨Start, s1, ..., sk⟩ with c(n<sub>k</sub>) &lt; c(n), and its prefixes n0, n1, ..., nk.',
    'Let n<sub>i</sub> be the last prefix already expanded. Then n<sub>i+1</sub> is on OPEN, and c(n<sub>i+1</sub>) ≤ c(n<sub>k</sub>) &lt; c(n), since a prefix costs no more than the whole path.',
    'Then UCS would have expanded n<sub>i+1</sub> instead of n, a contradiction. So the whole path n<sub>k</sub> was already expanded.'])}
{steps('Lemma 3: the first path to a state is the cheapest', [
    'Claim: the first time UCS expands a node n ending at state S, it has found a cheapest path to S.',
    'By Lemma 2, all cheaper paths were already expanded, and none of them ended at S.',
    'By Lemma 1, every path expanded later costs at least c(n).',
    eq('so the first goal path taken out is optimal')])}
{note('This is why UCS tests the goal when a path is taken OUT, not when it is generated. In the Sibiu example, Bucharest was generated with cost 310 before the 278 path existed. Testing at generation would have returned the wrong answer.', 'exam')}
''', kw=['proof of optimality', 'lemma', 'uniform cost', 'non decreasing cost'])

K.lesson('maths', 'The maths: geometric series and the cost bound', f'''
{fxs(
    fx('Geometric series', '∑<sub>i=0</sub><sup>d</sup> b<sup>i</sup> = (b<sup>d+1</sup> − 1) ⁄ (b − 1) ≤ b<sup>d</sup> · b ⁄ (b − 1)', 'The last level holds most of the nodes. For b = 10 it is about 90 percent of them.', key=True),
    fx('Fraction of nodes in the last level', 'b<sup>d</sup> ⁄ ((b<sup>d+1</sup> − 1) ⁄ (b − 1)) → (b − 1) ⁄ b', 'For b = 2 half the nodes are in the last level. For b = 10, 90 percent.'),
    fx('UCS depth bound', 'depth ≤ ⌊C* ⁄ ε⌋', 'A path of more than C*⁄ε actions costs more than C*, so UCS never needs to expand it before the goal.'))}
{steps('Worked example: the UCS bound', [
    'All road lengths are at least ε = 70 (the shortest Romania road is 70, Lugoj to Mehadia). The optimal cost is C* = 418.',
    '⌊418 ⁄ 70⌋ = 5. A path of 6 roads costs at least 6 × 70 = 420 &gt; 418, so UCS never expands a path with more than 5 roads.',
    'With b = 4 it generates at most about 4<sup>1 + 5</sup> = 4,096 nodes.',
    eq('the real search expands only 13 cities, so the bound is loose but safe')])}
{steps('Worked example: BFS memory', [
    'b = 10, d = 8, and each node needs 1 KB.',
    'Nodes up to depth 8: (10⁹ − 1) ⁄ 9 ≈ 1.11 × 10⁸.',
    eq('memory ≈ 1.11 × 10⁸ KB ≈ 111 GB')])}
''', kw=['geometric series', 'complexity bound', 'C star over epsilon', 'memory'])

K.lesson('compare', 'BFS against UCS against Dijkstra', f'''
{versus('Breadth first against uniform cost', ['', 'Breadth first', 'Uniform cost'], [
    ['Frontier', 'FIFO queue', 'Priority queue on g(n)'],
    ['Finds', 'Fewest actions', 'Lowest total cost'],
    ['Goal test', 'At generation (saves a level)', 'At expansion (needed for optimality)'],
    ['Complete', 'Yes, if b is finite', 'Yes, if every cost ≥ ε &gt; 0'],
    ['Time and space', 'O(b<sup>d</sup>)', 'O(b<sup>1 + ⌊C*⁄ε⌋</sup>)'],
    ['Romania answer', '450 (3 roads)', '418 (4 roads)']],
    'with equal costs the two find the same answer and BFS is a little cheaper. With different costs only UCS is optimal.')}
{versus('Uniform cost search and Dijkstra\'s algorithm', ['', 'UCS', 'Dijkstra'], [
    ['Stops', 'When the goal is taken out', 'After the cheapest path to every node is known'],
    ['Graph given', 'Implicitly, by a successor function', 'Usually explicitly, all nodes known'],
    ['Frontier starts with', 'Only the start', 'Often every node at ∞']],
    'UCS is Dijkstra\'s algorithm with an early stop and lazy generation of the graph. That matters when the graph is huge or infinite, like a puzzle.')}
{scene('a delivery app', '<p>A food delivery app finds the fastest route from the restaurant to you. Road segments take different times, so it cannot use BFS. A plain UCS from the restaurant spreads out in every direction. Real apps add a heuristic (chapter 3.1) to point the search toward you, and precompute shortcuts, so they answer in milliseconds on a country sized map.</p>')}
''', kw=['BFS against UCS', 'Dijkstra', 'comparison'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>BFS is like ripples in a pond: it checks everything one step away, then two steps away. UCS is the same but the ripples are measured in cost, like kilometres, not in steps.</p>',
    '<p>BFS uses a FIFO queue, is complete and optimal for equal costs, and costs O(b<sup>d</sup>) time and space. UCS uses a priority queue on g(n), tests the goal at expansion, and is complete and optimal when costs are at least ε, with cost O(b<sup>1 + ⌊C*⁄ε⌋</sup>).</p>',
    '<p>The proof of UCS optimality rests on one fact: the g values taken out of the queue never decrease. The same argument proves Dijkstra correct, and A* with a consistent heuristic (chapter 3.1) is UCS on modified costs C\'(x, y) = C(x, y) − h(x) + h(y).</p>',
    '<p>Bidirectional and frontier search variants cut memory by not storing the explored set. Research on very large graphs uses external memory BFS (on disk), parallel BFS on GPUs (the Graph500 benchmark), and bucket based priority queues (Dial\'s algorithm) when costs are small integers.</p>')}
{deep('why A* with a consistent h is a special case of UCS', '<p>Define new costs C\'(x, a, y) = C(x, a, y) − h(x) + h(y). Consistency h(x) ≤ C(x, a, y) + h(y) makes every C\' ≥ 0. Along a path from s to n the new costs telescope: g\'(n) = g(n) − h(s) + h(n) = f(n) − h(s). So ordering by g\' is ordering by f = g + h, and UCS on C\' expands exactly what A* expands on C. The three lemmas above then prove A* optimal for free.</p>')}
''', kw=['ripples', 'Dijkstra', 'reduced costs', 'external memory BFS'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Uninformed search uses a fixed selection rule and no knowledge about the goal.',
    '<b>BFS</b>: FIFO queue, level by level. Complete for finite b. Finds the fewest actions, which is cheapest only when all costs are equal. Time and space O(b<sup>d</sup>). Memory is the real limit.',
    'Test the goal when a node is generated in BFS (saves a whole level), but when it is taken out in UCS.',
    '<b>UCS</b>: priority queue on g(n). Complete and optimal when every cost is at least ε &gt; 0. Cost O(b<sup>1 + ⌊C*⁄ε⌋</sup>).',
    'The proof: costs taken out never decrease (Lemma 1), so every cheaper path is expanded first (Lemma 2), so the first path to a state is the cheapest (Lemma 3).',
    'On Romania, BFS gives 450 with 3 roads and UCS gives 418 with 4 roads.'],
    'chapter 2.2 trades optimality for memory with depth first, depth limited, iterative deepening and bidirectional search.')}
{nbcard('bfs-ucs', 'Run BFS on the water jugs and UCS on the Sibiu map, then write your own shortest path and cheapest cost functions.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which data structure does breadth first search use for its frontier?', ['A stack', 'A FIFO queue', 'A priority queue on g', 'A hash set only'], 1,
       'First in, first out.', 'The oldest path is taken out first, so the search goes level by level.')
K.quiz('e', 'Which uninformed method orders the frontier by path cost?', ['Breadth first', 'Depth first', 'Uniform cost', 'Iterative deepening'], 2,
       'Cost, not depth.', 'UCS always expands the lowest g(n).')
K.quiz('e', 'BFS on Romania from Arad returns the route through Fagaras with cost', ['418', '450', '366', '500'], 1,
       '140 + 99 + 211.', 'It has the fewest roads (3) but is not the cheapest.')
K.quiz('e', 'Uninformed search means the algorithm', ['Has no goal test', 'Uses no knowledge about where the goal is', 'Picks nodes at random', 'Cannot find a solution'], 1,
       'Blind.', 'It uses the same fixed rule for every problem.')
K.quiz('m', 'When must uniform cost search do the goal test?', ['When the node is generated', 'When the node is taken out of the frontier', 'Only at the start', 'Never'], 1,
       'The Sibiu example.', 'Bucharest was first generated with cost 310 and later replaced by 278. Testing at generation would return 310.')
K.quiz('m', 'BFS is optimal when', ['Costs are random', 'All actions have the same cost', 'The graph has cycles', 'b is infinite'], 1,
       'Fewest steps = cheapest?', 'Only with equal step costs is the shallowest goal also the cheapest.')
K.quiz('m', 'What is the main practical limit of BFS?', ['Time', 'Memory', 'It is incomplete', 'It needs a heuristic'], 1,
       'Look at the table.', 'At depth 10 with b = 10 it needs about 10 terabytes, long before the time becomes unbearable.')
K.quiz('m', 'UCS may fail to terminate when', ['There is a zero cost cycle', 'All costs are 1', 'The goal is shallow', 'b = 2'], 0,
       'ε &gt; 0.', 'Going round a zero cost loop never raises g, so the search can keep choosing it.')
K.quiz('h', 'In the optimality proof, Lemma 1 says that if n2 is expanded right after n1 then', ['c(n1) ≥ c(n2)', 'c(n1) ≤ c(n2)', 'c(n1) = c(n2)', 'n2 is a goal'], 1,
       'Non decreasing.', 'The costs of the paths taken out never go down.')
K.quiz('h', 'With b = 10, about what fraction of the nodes of a full tree to depth d are in the last level?', ['10 percent', '50 percent', '90 percent', '99 percent'], 2,
       '(b − 1) ⁄ b.', '9 ⁄ 10, so the last level dominates the cost.')
K.quiz('x', 'In the style of an MIT 6.034 exam: UCS and BFS are run on a graph where every edge costs 5. Which statement is true?', ['UCS finds a cheaper path than BFS', 'They return paths of the same cost', 'BFS may return a more expensive path', 'UCS is incomplete here'], 1,
       'Equal costs.', 'Cost is 5 times the number of edges, so fewest edges is also cheapest and both are optimal.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: UCS has optimal cost C* = 20 and every action costs at least 4. What is the deepest level it may expand before finding the goal?', ['4', '5', '6', '20'], 1,
       '⌊C* ⁄ ε⌋.', '⌊20 ⁄ 4⌋ = 5. A path of 6 actions costs at least 24 &gt; 20, so it is never expanded before the goal.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A tree has b = 3. How many nodes does BFS generate up to depth 3, counting the root?', '40', '1 + 3 + 9 + 27.',
       ['Depth 0: 1, depth 1: 3.', 'Depth 2: 9, depth 3: 27.', eq('1 + 3 + 9 + 27 = 40')], check=40)
K.calc('e', 'Sibiu to Bucharest through Rimnicu Vilcea and Pitesti. Roads 80, 97, 101. Total?', '278', 'Add.',
       ['80 + 97 = 177.', '177 + 101 = 278.', eq('g = 278')], check=278)
K.calc('e', 'How much cheaper is the UCS route from Arad (418) than the BFS route (450)?', '32', 'Subtract.',
       ['450 − 418.', 'The BFS route uses Fagaras (99 + 211).', eq('32')], check=32)
K.calc('m', 'With the goal test at expansion, BFS on b = 2 may generate one more level. How many nodes up to depth 4?', '31', '1 + 2 + 4 + 8 + 16.',
       ['Goal at depth 3, but depth 4 is generated before it is popped.', '1 + 2 + 4 + 8 = 15, plus 16.', eq('31')], check=31)
K.calc('m', 'BFS with b = 10 to depth 6 at 1 KB a node. About how many MB of memory? (Use 1 MB = 1000 KB and round to a whole number.)', '1111', '(10⁷ − 1) ⁄ 9 nodes.',
       ['(10⁷ − 1) ⁄ 9 = 1,111,111 nodes.', '× 1 KB = 1,111,111 KB.', eq('≈ 1,111 MB, about 1 GB')], check=1111, tol=1)
K.calc('m', 'UCS from Arad: what is g of Rimnicu Vilcea when it is taken out? Arad to Sibiu 140, Sibiu to Rimnicu Vilcea 80.', '220', 'Add.',
       ['There is only one way in: through Sibiu.', '140 + 80.', eq('220')], check=220)
K.calc('m', 'UCS from Arad takes out cities in order. How many cities are taken out up to and including Bucharest?', '13', 'Count the list in the lesson.',
       ['Arad, Zerind, Timisoara, Sibiu, Oradea, Rimnicu Vilcea, Lugoj.', 'Fagaras, Mehadia, Pitesti, Craiova, Drobeta, Bucharest.', eq('7 + 6 = 13')], check=13)
K.calc('h', 'UCS with C* = 418 and smallest road ε = 70. What is ⌊C* ⁄ ε⌋?', '5', 'Divide and round down.',
       ['418 ⁄ 70 = 5.97.', 'Round down.', eq('5')], check=418 // 70)
K.calc('h', 'For b = 2, what fraction of the nodes of a full tree to depth 9 lie at depth 9? Give a decimal to 3 places.', '0.500', 'Last level ⁄ total.',
       ['Last level 2⁹ = 512.', 'Total 2¹⁰ − 1 = 1023.', eq('512 ⁄ 1023 ≈ 0.500')], check=512 / 1023, tol=0.001)
K.calc('x', 'In the style of a Stanford CS221 problem: actions cost 1 or 3. UCS finds C* = 9. With b = 3, what is the bound b<sup>1 + ⌊C*⁄ε⌋</sup>?', '59049', 'ε = 1.',
       ['ε is the smallest cost, 1.', '1 + ⌊9 ⁄ 1⌋ = 10.', eq('3¹⁰ = 59,049')], check=3 ** 10)

# ---------------------------------------------------------------- assignments
K.assign('bfspath', 'e', 'Shortest path with breadth first search',
         '<p>Write <code>bfs_path(graph, start, goal)</code>. graph is a dict from a node to the list of its neighbours. Return the list of nodes on a path with the fewest edges, or None if there is none. Visit neighbours in the order of the list.</p>',
         '''
def bfs_path(graph, start, goal):
    # your code here
    pass
''', [("bfs_path({'A': ['B', 'C'], 'B': ['D'], 'C': ['D', 'E'], 'D': ['F'], 'E': ['F'], 'F': []}, 'A', 'F')", ['A', 'B', 'D', 'F']),
      ("bfs_path({'A': ['B'], 'B': ['A'], 'C': []}, 'A', 'C')", None),
      ("bfs_path({'A': ['B'], 'B': []}, 'A', 'A')", ['A']),
      ("bfs_path({'S': ['A', 'G'], 'A': ['G'], 'G': []}, 'S', 'G')", ['S', 'G'])],
         '''
def bfs_path(graph, start, goal):
    if start == goal:
        return [start]
    frontier = [[start]]
    seen = [start]
    while len(frontier) > 0:
        path = frontier.pop(0)
        for nxt in graph[path[-1]]:
            if nxt not in seen:
                if nxt == goal:
                    return path + [nxt]
                seen.append(nxt)
                frontier.append(path + [nxt])
    return None
''', 'Keep a list of paths. Take the oldest out with pop(0) and add each new path at the end.', '<p>The queue makes every path of length k come out before any path of length k + 1.</p>')
K.assign('ucscost', 'm', 'Cheapest cost with uniform cost search',
         '<p>Write <code>ucs_cost(edges, start, goal)</code>. edges is a list of [a, b, cost] roads that can be driven both ways. Return the lowest total cost from start to goal, or -1 if the goal cannot be reached.</p>',
         '''
def ucs_cost(edges, start, goal):
    # your code here
    pass
''', [("ucs_cost([['S', 'A', 1], ['S', 'B', 4], ['A', 'B', 2], ['A', 'C', 5], ['B', 'C', 1], ['C', 'G', 3]], 'S', 'G')", 7),
      ("ucs_cost([['Sibiu', 'RV', 80], ['Sibiu', 'Fagaras', 99], ['RV', 'Pitesti', 97], ['Fagaras', 'Bucharest', 211], ['Pitesti', 'Bucharest', 101]], 'Sibiu', 'Bucharest')", 278),
      ("ucs_cost([['A', 'B', 2]], 'A', 'C')", -1), ("ucs_cost([], 'A', 'A')", 0)],
         '''
def ucs_cost(edges, start, goal):
    frontier = [(0, start)]
    done = []
    while len(frontier) > 0:
        frontier.sort()
        cost, node = frontier.pop(0)
        if node in done:
            continue
        if node == goal:
            return cost
        done.append(node)
        for a, b, c in edges:
            if a == node and b not in done:
                frontier.append((cost + c, b))
            if b == node and a not in done:
                frontier.append((cost + c, a))
    return -1
''', 'Keep (cost, node) pairs, sort, take the first out. Skip a node you have already taken out. Test the goal when you take it out.', '<p>S, A, B, C, G costs 1 + 2 + 1 + 3 = 7, which beats S, B, C, G = 8.</p>')

K.must('BFS', 'FIFO queue. Complete (finite b). Fewest actions, optimal only for equal costs. Time and space O(b<sup>d</sup>).')
K.must('UCS', 'Priority queue on g(n). Complete and optimal if every cost ≥ ε &gt; 0. O(b<sup>1 + ⌊C*⁄ε⌋</sup>).')
K.must('Goal test timing', 'BFS: test at generation. UCS: test at expansion (Sibiu: 310 is replaced by 278).')
K.must('Romania', 'BFS 450 via Fagaras. UCS 418 via Rimnicu Vilcea and Pitesti, after taking out 13 cities.')
K.must('Optimality proof', 'Lemma 1: costs taken out never decrease. Lemma 2: cheaper paths come first. Lemma 3: first path to a state is cheapest.')
K.must('Memory', 'b = 10, d = 10 needs about 10 TB. Memory runs out before time.')

T = K.topic(
    slug='bfs-ucs', topic='bfs-ucs', step=(2, 'Uninformed search', 'cai-uninformed', 'Search with no hints: level by level, cheapest first, deepest first, and with growing limits.', 'College'),
    title='Breadth first and uniform cost search', short='BFS and UCS', badge='2.1', minutes=50,
    lead='Breadth first search explores level by level and finds the fewest actions. Uniform cost search explores in order of cost and finds the cheapest path. Learn both, their costs, and the three lemma proof that UCS is optimal.',
    desc='Uninformed strategies, BFS on the water jugs, completeness, optimality and the O(b^d) cost, the memory table, uniform cost search with the Sibiu example, the C*/ε bound, the proof of optimality and the link to Dijkstra.',
    summary='BFS with a FIFO queue, UCS with a priority queue on g(n), when each is optimal, their cost, and why UCS tests the goal late.',
    keywords=['breadth first search', 'BFS', 'uniform cost search', 'UCS', 'Dijkstra', 'priority queue', 'optimality proof'],
    recap='<p>BFS: queue, fewest steps, O(b<sup>d</sup>). UCS: priority queue on g, cheapest path, goal test at expansion.</p>',
    nb={'bfs': 'Breadth first search on the water jugs', 'ucs': 'Uniform cost search from Sibiu to Bucharest'})
