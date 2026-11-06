# Chapter 3.1: greedy best first and A* search. Source: slide Set 2, slides 53 to 70 (heuristic search and the
# meaning of h(n), food for thought IV on necessary and sufficient conditions, straight line distance on Romania,
# greedy best first and the trap of slide 58, the Iasi to Fagaras loop, A* with f = g + h and its Romania trace,
# admissibility, consistency and the questions on optimality and complexity) and the class of 31 January 2026.
# The optimality proofs, optimal efficiency and weighted A* follow Russell and Norvig, AIMA 4th ed., section 3.5.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('astar', r'''
# A* search on the Romania map, with the straight line distance to Bucharest as h.
roads = [("Arad", "Zerind", 75), ("Arad", "Sibiu", 140), ("Arad", "Timisoara", 118), ("Zerind", "Oradea", 71),
         ("Oradea", "Sibiu", 151), ("Timisoara", "Lugoj", 111), ("Lugoj", "Mehadia", 70), ("Mehadia", "Drobeta", 75),
         ("Drobeta", "Craiova", 120), ("Craiova", "Rimnicu Vilcea", 146), ("Craiova", "Pitesti", 138),
         ("Sibiu", "Fagaras", 99), ("Sibiu", "Rimnicu Vilcea", 80), ("Rimnicu Vilcea", "Pitesti", 97),
         ("Fagaras", "Bucharest", 211), ("Pitesti", "Bucharest", 101)]
h = {"Arad": 366, "Zerind": 374, "Oradea": 380, "Sibiu": 253, "Timisoara": 329, "Lugoj": 244, "Mehadia": 241,
     "Drobeta": 242, "Craiova": 160, "Rimnicu Vilcea": 193, "Fagaras": 176, "Pitesti": 100, "Bucharest": 0}

def astar(start, goal):
    frontier = [(h[start], 0, [start])]          # (f, g, path)
    best_g = {start: 0}
    while len(frontier) > 0:
        frontier.sort()
        f, g, path = frontier.pop(0)
        city = path[-1]
        print("expand", city, " g =", g, " h =", h[city], " f =", f)
        if city == goal:
            return g, path
        for a, b, cost in roads:
            if city == a or city == b:
                nxt = b if city == a else a
                new_g = g + cost
                if nxt not in best_g or new_g < best_g[nxt]:
                    best_g[nxt] = new_g
                    frontier.append((new_g + h[nxt], new_g, path + [nxt]))
    return None

print(astar("Arad", "Bucharest"))
''')

K.code('inconsistent', r'''
# An admissible but INCONSISTENT heuristic breaks graph search A* that never reopens a closed state.
# Roads: S-A 1, A-B 1, S-B 4, B-G 3. The best path is S, A, B, G with cost 5.
roads = {"S": [("A", 1), ("B", 4)], "A": [("B", 1)], "B": [("G", 3)], "G": []}
h = {"S": 0, "A": 4, "B": 0, "G": 0}     # h(A) = 4 > cost(A, B) + h(B) = 1, so h is not consistent

frontier = [(h["S"], 0, ["S"])]
closed = []
while len(frontier) > 0:
    frontier.sort()
    f, g, path = frontier.pop(0)
    node = path[-1]
    if node in closed:
        continue
    print("expand", node, "with g =", g, "f =", f)
    if node == "G":
        print("returned cost", g, "but the best cost is 5")
        break
    closed.append(node)
    for nxt, cost in roads[node]:
        if nxt not in closed:
            frontier.append((g + cost + h[nxt], g + cost, path + [nxt]))
''')

K.lesson('idea', 'Heuristics: knowing roughly where the goal is', f'''
{src('slide Set 2, slides 53 to 57, and the class of 31 January 2026.')}
<p>Uniform cost search expands the cheapest path so far, but it never asks how far that path still is from the goal. It spreads out in every direction. Often we know something about the "merit" of a node, for example the straight line distance from a city to Bucharest. A search that uses such knowledge is called <b>informed</b> or <b>heuristic</b> search.</p>
{wwh('A heuristic function h(n) is an estimate of the cost of the cheapest path from the state of node n to a goal. It must be non negative and h(n) = 0 at every goal.',
     'It lets the search look ahead. If h(n1) &lt; h(n2), n1 is probably closer to the goal, so the search can try it first and skip much useless work.',
     'Design h from knowledge of the problem, often by solving a simpler version of it (chapter 3.2). Then use h to order the frontier: alone (greedy best first) or added to g (A*).')}
<p>A heuristic is a practical rule from experience that is "good enough" as an approximation, even if it is not perfect. The straight line distance to Bucharest, h<sub>SLD</sub>, is a classic example: Arad 366, Sibiu 253, Fagaras 176, Rimnicu Vilcea 193, Pitesti 100, Bucharest 0.</p>
{note('Food for thought IV asks for necessary and sufficient conditions. For optimal A*: admissibility is sufficient for tree search, consistency is sufficient for graph search. Neither is necessary: a slightly overestimating h can still return the optimal path by luck, but then nothing is guaranteed.', 'exam')}
''', kw=['heuristic', 'informed search', 'h(n)', 'straight line distance', 'merit of a node'])

K.lesson('greedy', 'Greedy best first search', f'''
{src('slide Set 2, slides 58 and 59.')}
{wwh('Greedy best first search always expands the node with the lowest h(n), the one that looks closest to the goal.',
     'It often reaches a goal very quickly, expanding few nodes, because it heads straight for the goal.',
     'Order the frontier by h(n) only. Ignore g(n), the cost already paid.')}
<p>On Romania, greedy goes Arad → Sibiu (253 is lower than Zerind 374 and Timisoara 329) → Fagaras (176) → Bucharest. It expands only nodes on its path, so the search cost is minimal, but the route costs 450, not 418.</p>
{steps('The trap of slide 58', [
    'From S there are two ways: S → n1 → n2 → Goal (10 + 10 + 10 = 30) and S → n3 → Goal (100 + 10 = 110).',
    'h(n1) = 20 and h(n3) = 10. Greedy takes n3 because it looks closer.',
    'From n3 the goal is one step away, so greedy returns S, n3, Goal with cost 110.',
    eq('greedy pays 110 while the best path costs 30, because it ignores the 100 it paid to reach n3')])}
{viz('searchgraph', alg='greedy', gr='trap', start='S', goal='Goal')}
<p>From Iasi to Fagaras greedy first goes to Neamt (closest by straight line), which is a dead end. In tree search Neamt puts Iasi back on the frontier, and the search loops for ever between them.</p>
{table(['Property', 'Greedy best first'], [
    ['Complete', 'No in tree search (Iasi, Neamt loop). Yes in graph search on a finite space.'],
    ['Optimal', 'No (450 against 418, 110 against 30)'],
    ['Time and space', 'O(b<sup>m</sup>) in the worst case, but often far less with a good h']])}
''', kw=['greedy best first search', 'greedy', 'trap', 'Iasi', 'Neamt', 'not optimal'])

K.lesson('astar', 'A* search: f(n) = g(n) + h(n)', f'''
{src('slide Set 2, slides 60 to 66.')}
{wwh('A* expands the node with the lowest f(n) = g(n) + h(n): the cost paid so far plus the estimated cost still to go.',
     'Greedy ignores the past (g) and UCS ignores the future (h). A* adds them, so f(n) estimates the cost of the cheapest solution through n. With a good h it is both optimal and much faster than UCS.',
     'Keep the frontier as a priority queue on f. Take out the lowest f, test for the goal, and add the children with their f values. Replace a frontier entry if a cheaper g to the same state appears.')}
{fxs(fx('Evaluation function of A*', 'f(n) = g(n) + h(n)', 'g(n) is the cost of the path of node n, h(n) the estimate from n to a goal. With h = 0 A* is UCS. With g ignored it is greedy.', key=True))}
{steps('A* from Arad to Bucharest, as in the slide figures', [
    'Expand Arad (f = 0 + 366 = 366). Add Sibiu 140 + 253 = 393, Timisoara 118 + 329 = 447, Zerind 75 + 374 = 449.',
    'Expand Sibiu (393). Add Rimnicu Vilcea 220 + 193 = 413, Fagaras 239 + 176 = 415, Oradea 291 + 380 = 671, and Arad again 280 + 366 = 646.',
    'Expand Rimnicu Vilcea (413). Add Pitesti 317 + 100 = 417, Craiova 366 + 160 = 526, Sibiu 300 + 253 = 553.',
    'Expand Fagaras (415). Add Bucharest 450 + 0 = 450 and Sibiu 338 + 253 = 591. A goal is on the frontier, but not with the lowest f.',
    'Expand Pitesti (417). Add Bucharest 418 + 0 = 418, Rimnicu Vilcea 607 and Craiova 615.',
    eq('take out Bucharest with f = 418: Arad, Sibiu, Rimnicu Vilcea, Pitesti, Bucharest, the optimal route')])}
{viz('searchgraph', alg='astar', gr='romania', start='Arad', goal='Bucharest')}
{code('astar')}
<p>A* takes out 6 cities. Uniform cost search takes out 13 for the same answer (chapter 2.1).</p>
''', kw=['A star', 'A*', 'f = g + h', 'evaluation function', 'Romania A* trace'])

K.lesson('conditions', 'Admissible and consistent heuristics', f'''
{src('slide Set 2, slides 67 to 69.')}
{fxs(
    fx('Admissible', 'h(n) ≤ h*(n) for every n', 'h*(n) is the true cost of an optimal path from n to a goal (∞ if there is none). An admissible h never overestimates: it is optimistic. Also h(goal) = 0.', key=True),
    fx('Consistent (monotone)', 'h(n1) ≤ C(n1, a, n2) + h(n2) for every action a from n1 to n2', 'A triangle inequality: the estimate cannot drop by more than the cost of a step. It must hold for every action between n1 and n2.', key=True),
    fx('Consistency implies admissibility', '(∀ n1, n2, a) h(n1) ≤ C(n1, a, n2) + h(n2)  ⇒  (∀ n) h(n) ≤ h*(n)', 'Proof by induction on the number of steps to the goal (below). The other direction is false.'))}
{steps('Proof that consistent implies admissible', [
    'Take an optimal path n = n0, n1, ..., nk = goal. Induction on k.',
    'k = 0: n is a goal, h(n) = 0 = h*(n).',
    'Step: by consistency h(n0) ≤ C(n0, n1) + h(n1). By induction h(n1) ≤ h*(n1).',
    eq('h(n0) ≤ C(n0, n1) + h*(n1) = h*(n0)')])}
{steps('Why consistency makes f never decrease along a path', [
    'Let n2 be a child of n1 by action a. Then g(n2) = g(n1) + C(n1, a, n2).',
    'f(n2) = g(n1) + C(n1, a, n2) + h(n2).',
    'By consistency C(n1, a, n2) + h(n2) ≥ h(n1).',
    eq('f(n2) ≥ g(n1) + h(n1) = f(n1)')])}
<p>Because f never decreases, A* with a consistent h expands nodes in rings of growing f, called <b>contours</b>. The first time it takes out a state, it has found the cheapest path to that state, just like UCS (Lemma 3 of chapter 2.1). So graph search never needs to reopen a closed state.</p>
''', kw=['admissible', 'consistent', 'monotone', 'triangle inequality', 'h star', 'contours'])

K.lesson('optimal', 'Is A* optimal, and how fast is it', f'''
{steps('A* tree search with an admissible h is optimal', [
    'Let the optimal cost be C*. Suppose a suboptimal goal G2 with g(G2) &gt; C* is on the frontier.',
    'Some node n on an optimal path is also on the frontier (the start is, and its optimal child replaces it, and so on).',
    'Admissibility gives f(n) = g(n) + h(n) ≤ g(n) + h*(n) = C*.',
    'And f(G2) = g(G2) + 0 &gt; C*. So f(n) &lt; f(G2), and n is expanded before G2.',
    eq('every node on the optimal path is expanded before G2, so the first goal taken out costs C*')])}
<p>In graph search, an admissible but inconsistent h can fail if closed states are never reopened. In the example below the search reaches B first by the expensive road (g = 4), closes it, and later ignores the cheaper road through A (g = 2).</p>
{code('inconsistent')}
{fxs(
    fx('What A* expands', 'surely every n with f(n) &lt; C*, maybe some with f(n) = C*, never any with f(n) &gt; C*', 'With a consistent h.'),
    fx('Optimally efficient', 'no other optimal algorithm using the same h expands fewer nodes (up to ties)', 'Any algorithm that skips a node with f(n) &lt; C* risks missing a cheaper solution.', key=True),
    fx('Effective branching factor', 'N + 1 = 1 + b* + (b*)² + ... + (b*)<sup>d</sup>', 'If A* generates N nodes for a solution at depth d, b* measures how well h focuses the search. b* close to 1 is ideal.'))}
{note('The time of A* is still exponential in general, and the memory is its real weak point: it keeps every generated node. That is why chapter 3.3 builds IDA*, RBFS and SMA*.', 'warn')}
''', kw=['A* optimality', 'optimally efficient', 'reopening', 'effective branching factor', 'inconsistent heuristic'])

K.lesson('maths', 'The maths: weighted A* and the cost of a bad h', f'''
{fxs(
    fx('Weighted A*', 'f(n) = g(n) + w · h(n), w ≥ 1', 'w = 1 is A*. A larger w trusts h more, so the search is faster and greedier.'),
    fx('Bounded suboptimality', 'cost found ≤ w · C*', 'With an admissible h, weighted A* is at most w times worse than the optimum. w = 1.5 means at most 50 percent more cost.', key=True),
    fx('Error and work', 'if |h* − h| ≤ c for a constant c, the work is about b<sup>c</sup>, not b<sup>d</sup>', 'Constant absolute error still costs exponential in c. Relative error ε = (h* − h) ⁄ h* gives about b<sup>ε d</sup>.'))}
{steps('Worked example: weighted A* bound', [
    'An optimal route costs C* = 418. We run weighted A* with w = 1.2 and an admissible h.',
    'The guarantee is cost ≤ 1.2 × 418.',
    eq('cost ≤ 501.6, so the 450 route via Fagaras is allowed, and is in fact what a greedy enough search returns')])}
{steps('Worked example: effective branching factor', [
    'A* finds a solution at depth d = 2 after generating N = 6 nodes.',
    'Solve 6 + 1 = 1 + b* + (b*)², so (b*)² + b* − 6 = 0.',
    '(b* + 3)(b* − 2) = 0.',
    eq('b* = 2')])}
''', kw=['weighted A*', 'bounded suboptimal', 'heuristic error', 'effective branching factor'])

K.lesson('compare', 'Greedy against UCS against A*', f'''
{versus('Three ways to order the frontier', ['', 'UCS', 'Greedy best first', 'A*'], [
    ['Order by', 'g(n)', 'h(n)', 'g(n) + h(n)'],
    ['Looks at', 'The past only', 'The future only', 'Both'],
    ['Optimal', 'Yes', 'No', 'Yes, with admissible h (tree) or consistent h (graph)'],
    ['Complete', 'Yes (costs ≥ ε)', 'Only in graph search on finite spaces', 'Yes (costs ≥ ε, finite b)'],
    ['Romania, Arad to Bucharest', '418, 13 cities taken out', '450, 4 cities', '418, 6 cities'],
    ['Slide 58 trap', '30', '110', '30']],
    'A* is the right default when you have an admissible heuristic. Greedy is useful only when any solution will do and speed matters most.')}
{scene('route planning in a game', '<p>Units in a strategy game move across a grid with walls and forests. Game engines use A* with the Manhattan or octile distance as h, because it is admissible on grids and gives the shortest path. When thousands of units move at once, they switch to weighted A* (w around 1.5) or precomputed paths, trading a little path quality for a large saving in time.</p>')}
''', kw=['UCS against A*', 'greedy against A*', 'game pathfinding'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A* is like a hiker who adds the distance walked so far to a guess of the distance still to go, and always continues from the spot with the smallest total. If the guess is never too big, the hiker finds the shortest way.</p>',
    '<p>f = g + h. Admissible h ≤ h* makes A* tree search optimal. Consistent h(n1) ≤ C + h(n2) makes f non decreasing, so graph search is optimal without reopening. Consistent implies admissible. A* is optimally efficient but needs exponential memory.</p>',
    '<p>A* with a consistent h is UCS on reduced costs C − h(x) + h(y) ≥ 0. Weighted A* gives cost ≤ w C*. With inconsistent h, graph search must reopen closed states (or use pathmax), and the number of re expansions can be exponential in the worst case (Martelli 1977).</p>',
    '<p>Research directions include anytime A* variants (ARA*, which lowers w over time), real time search (LRTA*) for robots that must move before planning ends, multi agent path finding (CBS), and learned heuristics from neural networks that keep or relax admissibility guarantees.</p>')}
{deep('pathmax', '<p>If an admissible h is inconsistent, you can make f non decreasing by using f(n2) = max(f(n1), g(n2) + h(n2)) for a child n2 of n1. This keeps admissibility, because the true cost through n2 is at least f(n1), which is a lower bound on any solution through n1.</p>')}
''', kw=['hiker', 'pathmax', 'ARA*', 'LRTA*', 'learned heuristics'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A heuristic h(n) estimates the cost from n to a goal. It is non negative and 0 at goals.',
    '<b>Greedy best first</b> orders by h only. Fast but not optimal (450 on Romania, 110 on the slide 58 trap) and can loop in tree search.',
    '<b>A*</b> orders by f = g + h. On Romania it takes out 6 cities and finds 418.',
    '<b>Admissible</b>: h ≤ h*. Enough for optimal tree search. <b>Consistent</b>: h(n1) ≤ C(n1, a, n2) + h(n2). Enough for optimal graph search, and it implies admissible.',
    'With consistent h, f never decreases along a path, and A* is optimally efficient. Its weak point is memory.',
    'Weighted A* with f = g + w h finds a cost at most w C*.'],
    'chapter 3.2 shows how to design good heuristics, compare them, and measure them with the effective branching factor.')}
{nbcard('greedy-astar', 'Run A* on Romania, see an inconsistent heuristic fail, then write A* and a consistency checker yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A* orders the frontier by', ['g(n)', 'h(n)', 'g(n) + h(n)', 'g(n) × h(n)'], 2,
       'Past plus future.', 'f(n) = g(n) + h(n).')
K.quiz('e', 'Greedy best first search orders the frontier by', ['g(n)', 'h(n)', 'f(n)', 'depth'], 1,
       'Only the future.', 'It expands the node that looks closest to the goal.')
K.quiz('e', 'An admissible heuristic', ['Never underestimates', 'Never overestimates', 'Is always 0', 'Is always exact'], 1,
       'Optimistic.', 'h(n) ≤ h*(n) for every n.')
K.quiz('e', 'What value must h have at a goal?', ['1', '0', '∞', 'Any value'], 1,
       'Nothing left to pay.', 'h(goal) = 0 is required.')
K.quiz('m', 'On the slide 58 trap, what cost does greedy best first return?', ['30', '100', '110', '20'], 2,
       'It goes to n3.', 'S → n3 (100) → Goal (10) = 110.')
K.quiz('m', 'In the A* Romania trace, which city is expanded right after Rimnicu Vilcea (413)?', ['Pitesti (417)', 'Fagaras (415)', 'Bucharest (450)', 'Craiova (526)'], 1,
       'Lowest f.', 'Fagaras with 415 is lower than Pitesti with 417.')
K.quiz('m', 'Which statement is true?', ['Admissible implies consistent', 'Consistent implies admissible', 'They are the same', 'Neither implies the other'], 1,
       'Induction on the path.', 'Consistency gives admissibility, but an admissible h may be inconsistent.')
K.quiz('m', 'With a consistent heuristic, f along any path is', ['Decreasing', 'Non decreasing', 'Random', 'Constant'], 1,
       'f(n2) ≥ f(n1).', 'The step cost always covers the drop in h.')
K.quiz('h', 'A* with h(n) = 0 for every n behaves like', ['Greedy', 'BFS', 'Uniform cost search', 'DFS'], 2,
       'f = g.', 'Ordering by g alone is UCS.')
K.quiz('h', 'Weighted A* with w = 2 and an admissible h returns a cost at most', ['C*', '2 C*', 'C* + 2', 'C* ⁄ 2'], 1,
       'Bounded suboptimality.', 'cost ≤ w C*.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: h is admissible but not consistent. Graph search A* that never reopens closed states', ['Is always optimal', 'May return a suboptimal path', 'Never terminates', 'Becomes greedy'], 1,
       'The S, A, B, G example.', 'B is closed with g = 4 before the cheaper g = 2 path is found, and the result costs 7 instead of 5.')
K.quiz('x', 'In the style of a Stanford CS221 exam: h1 and h2 are both consistent. Which of these is guaranteed to be consistent?', ['h1 + h2', 'max(h1, h2)', '2 h1', 'h1 × h2'], 1,
       'Check the triangle inequality.', 'max keeps h(n1) ≤ C + h(n2) for both, so it holds for the max. Sums and multiples can overestimate.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A* on Romania: f(Sibiu) after expanding Arad. g = 140 and h = 253.', '393', 'f = g + h.',
       ['g = 140.', 'h = 253.', eq('f = 393')], check=393)
K.calc('e', 'f(Rimnicu Vilcea) with g = 140 + 80 and h = 193.', '413', 'Add.',
       ['g = 220.', '220 + 193.', eq('413')], check=413)
K.calc('e', 'f(Fagaras) with g = 140 + 99 and h = 176.', '415', 'Add.',
       ['g = 239.', '239 + 176.', eq('415')], check=415)
K.calc('m', 'f(Pitesti) when reached through Rimnicu Vilcea: g = 140 + 80 + 97 and h = 100.', '417', 'Add.',
       ['g = 317.', '317 + 100.', eq('417')], check=417)
K.calc('m', 'Is h(Sibiu) = 253 consistent with h(Rimnicu Vilcea) = 193 and road 80? Give the slack C + h(RV) − h(Sibiu).', '20', 'It must be ≥ 0.',
       ['C + h(RV) = 80 + 193 = 273.', '273 − 253 = 20.', eq('slack 20 ≥ 0, so this edge is consistent')], check=80 + 193 - 253)
K.calc('m', 'How much more does greedy pay than A* on the slide 58 trap?', '80', '110 − 30.',
       ['Greedy: 100 + 10 = 110.', 'A*: 10 + 10 + 10 = 30.', eq('80')], check=80)
K.calc('m', 'Weighted A* with w = 1.5 on a problem with C* = 200. Largest cost it may return?', '300', 'w × C*.',
       ['Bound: cost ≤ w C*.', '1.5 × 200.', eq('300')], check=300)
K.calc('h', 'A* generates N = 14 nodes for a solution at depth 3. Find b* from 15 = 1 + b* + b*² + b*³.', '2', 'Try whole numbers.',
       ['b* = 2: 1 + 2 + 4 + 8 = 15.', 'That matches N + 1 = 15.', eq('b* = 2')], check=2)
K.calc('h', 'In the inconsistent example (S-A 1, A-B 1, S-B 4, B-G 3), what cost does graph A* without reopening return?', '7', 'B is closed with g = 4.',
       ['B is expanded first with g = 4 (f = 4), before A (f = 5).', 'G gets g = 4 + 3 = 7.', eq('7, against the optimal 5')], check=7)
K.calc('x', 'In the style of an MIT 6.034 problem: a path visits n0, n1, n2 with h = 10, 8, 2 and step costs 3 (n0 to n1) and 5 (n1 to n2). With pathmax, f(child) = max(f(parent), g(child) + h(child)). What is f(n2)?', '11', 'Compute f one state at a time.',
       ['f(n0) = 0 + 10 = 10. g(n1) = 3, so f(n1) = max(10, 3 + 8) = 11.', 'g(n2) = 3 + 5 = 8, so g(n2) + h(n2) = 10.', eq('f(n2) = max(11, 10) = 11')], check=11)

# ---------------------------------------------------------------- assignments
K.assign('astar', 'm', 'Write A* search',
         '<p>Write <code>astar(edges, h, start, goal)</code>. edges is a list of [a, b, cost] roads that can be driven both ways, h a dict of heuristic values. Return [cost, path] for an optimal path, or None.</p>',
         '''
def astar(edges, h, start, goal):
    # your code here
    pass
''', [("astar([['S', 'A', 1], ['S', 'B', 4], ['A', 'B', 2], ['A', 'C', 5], ['B', 'C', 1], ['C', 'G', 3]], {'S': 6, 'A': 5, 'B': 3, 'C': 2, 'G': 0}, 'S', 'G')", [7, ['S', 'A', 'B', 'C', 'G']]),
      ("astar([['S', 'n1', 10], ['n1', 'n2', 10], ['n2', 'Goal', 10], ['S', 'n3', 100], ['n3', 'Goal', 10]], {'S': 30, 'n1': 20, 'n2': 10, 'n3': 10, 'Goal': 0}, 'S', 'Goal')", [30, ['S', 'n1', 'n2', 'Goal']]),
      ("astar([['A', 'B', 1]], {'A': 0, 'B': 0, 'C': 0}, 'A', 'C')", None)],
         '''
def astar(edges, h, start, goal):
    frontier = [(h[start], 0, [start])]
    best_g = {start: 0}
    while len(frontier) > 0:
        frontier.sort()
        f, g, path = frontier.pop(0)
        node = path[-1]
        if node == goal:
            return [g, path]
        for a, b, cost in edges:
            if node == a or node == b:
                nxt = b if node == a else a
                new_g = g + cost
                if nxt not in best_g or new_g < best_g[nxt]:
                    best_g[nxt] = new_g
                    frontier.append((new_g + h[nxt], new_g, path + [nxt]))
    return None
''', 'Keep (f, g, path) triples, sort them, and only add a child if its new g is lower than any g seen for it.', '<p>The second test is the slide 58 trap: A* pays 30, greedy would pay 110.</p>')
K.assign('consistent', 'e', 'Check a heuristic for consistency',
         '<p>Write <code>is_consistent(edges, h)</code>. edges is a list of [a, b, cost] two way roads. Return True if h(a) ≤ cost + h(b) and h(b) ≤ cost + h(a) for every road, else False.</p>',
         '''
def is_consistent(edges, h):
    # your code here
    pass
''', [("is_consistent([['S', 'A', 1], ['A', 'B', 1], ['S', 'B', 4], ['B', 'G', 3]], {'S': 0, 'A': 4, 'B': 0, 'G': 0})", False),
      ("is_consistent([['Sibiu', 'RV', 80], ['RV', 'Pitesti', 97], ['Pitesti', 'Bucharest', 101]], {'Sibiu': 253, 'RV': 193, 'Pitesti': 100, 'Bucharest': 0})", True),
      ("is_consistent([], {})", True)],
         '''
def is_consistent(edges, h):
    for a, b, cost in edges:
        if h[a] > cost + h[b]:
            return False
        if h[b] > cost + h[a]:
            return False
    return True
''', 'Test the triangle inequality in both directions for each road.', '<p>The first test is the inconsistent example of the lesson: h(A) = 4 &gt; 1 + h(B) = 1.</p>')

K.must('Greedy best first', 'Order by h. Not optimal (Romania 450, slide 58 trap 110). Can loop in tree search.')
K.must('A*', 'Order by f = g + h. Romania: Arad 366, Sibiu 393, RV 413, Fagaras 415, Pitesti 417, Bucharest 418.')
K.must('Admissible', 'h(n) ≤ h*(n). Makes A* tree search optimal.')
K.must('Consistent', 'h(n1) ≤ C(n1, a, n2) + h(n2). f never decreases, graph search optimal, implies admissible.')
K.must('Optimally efficient', 'A* expands every node with f &lt; C* and none with f &gt; C*. No optimal method with the same h does better.')
K.must('Weighted A*', 'f = g + w h, cost ≤ w C*.')

T = K.topic(
    slug='greedy-astar', topic='greedy-astar', step=(3, 'Informed search', 'cai-informed', 'Search with a hint of where the goal is: greedy best first, A*, heuristic design, memory bounded and AND OR search.', 'College'),
    title='Greedy best first and A* search', short='Greedy and A*', badge='3.1', minutes=55,
    lead='Use a heuristic h(n), a guess of the cost still to go, to point the search at the goal. Greedy best first trusts h alone and can be fooled. A* adds the cost already paid and finds the cheapest path when h never overestimates.',
    desc='Heuristic functions, greedy best first with the slide 58 trap and the Iasi loop, A* with f = g + h and its Romania trace, admissibility and consistency with proofs, optimality and optimal efficiency, inconsistent heuristics, weighted A* and the effective branching factor.',
    summary='Greedy best first, A*, admissible and consistent heuristics, why A* is optimal, and weighted A*.',
    keywords=['A*', 'A star', 'greedy best first', 'heuristic', 'admissible', 'consistent', 'weighted A*'],
    recap='<p>Greedy uses h and is fast but not optimal. A* uses g + h and is optimal with an admissible (tree) or consistent (graph) h.</p>',
    nb={'astar': 'A* on the Romania map', 'inconsistent': 'An inconsistent heuristic that breaks graph search A*'})
