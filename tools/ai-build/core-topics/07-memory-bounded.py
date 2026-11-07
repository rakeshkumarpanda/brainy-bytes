# Chapter 3.3: memory bounded heuristic search. Source: slide Set 2, slides 71 to 74 (IDA* with an f cost cutoff,
# RBFS with the f-limit of the best alternative and backed up values, the question BFS against IDS against IDA*,
# the RBFS figure on Romania) and the classes of 31 January and 1 February 2026, where the minor exam was said to be
# a coding task such as RBFS. SMA* and the memory comparison follow Russell and Norvig, AIMA 4th ed., section 3.5.5.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

MAP = r'''roads = {
    "Arad": [("Zerind", 75), ("Sibiu", 140), ("Timisoara", 118)],
    "Zerind": [("Arad", 75), ("Oradea", 71)],
    "Oradea": [("Zerind", 71), ("Sibiu", 151)],
    "Timisoara": [("Arad", 118), ("Lugoj", 111)],
    "Lugoj": [("Timisoara", 111)],
    "Sibiu": [("Arad", 140), ("Oradea", 151), ("Fagaras", 99), ("Rimnicu Vilcea", 80)],
    "Fagaras": [("Sibiu", 99), ("Bucharest", 211)],
    "Rimnicu Vilcea": [("Sibiu", 80), ("Pitesti", 97), ("Craiova", 146)],
    "Craiova": [("Rimnicu Vilcea", 146), ("Pitesti", 138)],
    "Pitesti": [("Rimnicu Vilcea", 97), ("Craiova", 138), ("Bucharest", 101)],
    "Bucharest": [("Fagaras", 211), ("Pitesti", 101)],
}
h = {"Arad": 366, "Zerind": 374, "Oradea": 380, "Timisoara": 329, "Lugoj": 244, "Sibiu": 253, "Fagaras": 176,
     "Rimnicu Vilcea": 193, "Craiova": 160, "Pitesti": 100, "Bucharest": 0}
INF = 10 ** 9
'''

K.code('ida', '# IDA* on the western part of the Romania map (enough for Arad to Bucharest).\n' + MAP + r'''
def contour(city, g, limit, path):
    # depth first search that stops when f = g + h is above the limit.
    # It returns the path if it finds Bucharest, and otherwise the smallest f that was over the limit.
    f = g + h[city]
    if f > limit:
        return None, f
    if city == "Bucharest":
        return path, f
    smallest = INF
    for nxt, cost in roads[city]:
        if nxt not in path:
            found, over = contour(nxt, g + cost, limit, path + [nxt])
            if found is not None:
                return found, over
            smallest = min(smallest, over)
    return None, smallest

# We start from Sibiu to keep the run short. Try "Arad" too: the limits are then 366, 393, 413, 415, 417, 418.
limit = h["Sibiu"]
while True:
    print("iteration with f limit", limit)
    found, next_limit = contour("Sibiu", 0, limit, ["Sibiu"])
    if found is not None:
        print("found", found, "with cost", next_limit)
        break
    limit = next_limit
''')

K.code('rbfs', '# Recursive best first search (RBFS) on the same map.\n' + MAP + r'''
def rbfs(city, g, f_city, f_limit, path):
    print("at", city, " f =", f_city, " limit =", f_limit)
    if city == "Bucharest":
        return path, f_city
    kids = []
    for nxt, cost in roads[city]:
        if nxt not in path:
            f_new = max(g + cost + h[nxt], f_city)     # a child is never better than its parent
            kids.append([f_new, nxt, g + cost])
    if len(kids) == 0:
        return None, INF
    while True:
        kids.sort()
        best = kids[0]
        if best[0] > f_limit:
            return None, best[0]                      # give up here and report the best f we saw
        alt = INF
        if len(kids) > 1:
            alt = kids[1][0]                          # f of the best alternative
        result, best[0] = rbfs(best[1], best[2], best[0], min(f_limit, alt), path + [best[1]])
        if result is not None:
            return result, best[0]

path, cost = rbfs("Arad", 0, h["Arad"], INF, ["Arad"])
print(path, cost)
''')

K.lesson('idea', 'Why A* runs out of memory', f'''
{src('slide Set 2, slides 71 to 74, and the classes of 31 January and 1 February 2026.')}
<p>A* keeps every node it generates, in the frontier or the explored set. Its time is often fine, but its memory grows exponentially, and on hard problems it runs out of memory long before it runs out of time. Memory bounded methods keep the optimality of A* while using far less memory, at the price of repeating some work.</p>
{table(['Method', 'Idea', 'Memory'], [
    ['IDA*', 'Iterative deepening, but the cutoff is on f = g + h instead of depth', 'O(b d), linear'],
    ['RBFS', 'Best first search written as a recursion that remembers only the f of the best alternative', 'O(b d), linear'],
    ['SMA*', 'A* that uses all the memory it has, and drops the worst leaf when memory is full', 'Whatever you give it']])}
{note('The minor exam of this course was announced as a coding task, such as writing RBFS. The code in lesson 3 is short enough to learn by heart, and the notebook lets you practise it.', 'exam')}
''', kw=['memory bounded search', 'A* memory', 'IDA*', 'RBFS', 'SMA*'])

K.lesson('ida', 'IDA*: iterative deepening A*', f'''
{wwh('IDA* runs a depth first search that stops whenever f = g + h is above a limit. If no goal is found, it raises the limit and starts again.',
     'Iterative deepening saves memory, but on its own it ignores costs and h. Using f as the cutoff keeps the low memory and makes the search follow the A* contours, so it is optimal with an admissible h.',
     'Start with limit = f(start) = h(start). In each iteration, remember the smallest f that went over the limit. That value is the next limit. Stop when a goal is taken out within the limit.')}
{steps('IDA* from Arad to Bucharest', [
    'Limit 366 = h(Arad). Every child of Arad is over: Sibiu 393, Timisoara 447, Zerind 449. Next limit: 393.',
    'Limit 393. Sibiu is expanded. Its children are over: Rimnicu Vilcea 413, Fagaras 415, Oradea 671. Next limit: 413.',
    'Limit 413. Rimnicu Vilcea is expanded. Pitesti 417 and Craiova 526 are over. Fagaras 415 is over too. Next limit: 415.',
    'Limit 415. Fagaras is expanded, Bucharest via Fagaras is 450, over. Pitesti 417 is still over. Next limit: 417.',
    'Limit 417. Pitesti is expanded, Bucharest via Pitesti is 418, over. Next limit: 418.',
    eq('limit 418: Bucharest is reached with f = 418, the optimal cost, after 6 iterations')])}
{viz('idastar', start='Arad')}
{code('ida')}
{fxs(fx('Iterations of IDA*', 'one per distinct f value up to C*', 'With integer costs and a good h that is few. With many different real valued costs, each iteration may add only one new node, and IDA* can take about N² time for N nodes A* would expand.', key=True))}
''', kw=['IDA*', 'iterative deepening A*', 'f limit', 'contour', 'cutoff'])

K.lesson('rbfs', 'RBFS: recursive best first search', f'''
{wwh('RBFS is a recursive search that acts like best first search but stores only the current path and, for each node on it, the f value of its best alternative (the f-limit).',
     'It keeps the best first order of A*, so it wastes less work than IDA*, while still using linear memory.',
     'At a node, sort its children by f. Go into the best child with f-limit = min(the limit from above, f of the second best child). If the best child\'s f goes over the limit, unwind (backtrack) and replace the f of that node with the best f found below it (the backed up value). Then the alternative may become the best, and the search switches there.')}
{steps('RBFS on Romania, as in the slide figure', [
    'At Arad. Children: Sibiu 393, Timisoara 447, Zerind 449. Go to Sibiu with limit 447 (the best alternative, Timisoara).',
    'At Sibiu. Children: Rimnicu Vilcea 413, Fagaras 415, Oradea 671, Arad 646. Go to Rimnicu Vilcea with limit min(447, 415) = 415.',
    'At Rimnicu Vilcea. Best child Pitesti has f = 417 &gt; 415. Unwind, and Rimnicu Vilcea gets the backed up value 417.',
    'At Sibiu again. Now Fagaras 415 is best. Go there with limit min(447, 417) = 417.',
    'At Fagaras. Best child Bucharest has f = 450 &gt; 417. Unwind, and Fagaras gets 450.',
    'At Sibiu. Rimnicu Vilcea (417) is best again. Go there with limit min(447, 450) = 447, then Pitesti (417), then Bucharest (418).',
    eq('the path Arad, Sibiu, Rimnicu Vilcea, Pitesti, Bucharest with cost 418')])}
{viz('rbfs', start='Arad')}
{code('rbfs')}
{algo('RBFS (AIMA style)', [
    'function RBFS(node, f_limit):',
    '    if GOAL-TEST(node): return node, f(node)',
    '    children = expand(node)',
    '    if no children: return failure, ∞',
    '    for each child s: s.f = max(g(s) + h(s), node.f)',
    '    loop:',
    '        best = child with the lowest f',
    '        if best.f > f_limit: return failure, best.f',
    '        alt = second lowest f among the children',
    '        result, best.f = RBFS(best, min(f_limit, alt))',
    '        if result is not failure: return result, best.f'])}
''', kw=['RBFS', 'recursive best first search', 'f-limit', 'backed up value', 'unwind', 'backtracking'])

K.lesson('sma', 'SMA*: use all the memory you have', f'''
{wwh('SMA* (simplified memory bounded A*) behaves like A* until memory is full. Then, to add a new node, it drops the worst leaf, the one with the highest f (and the oldest among ties).',
     'IDA* and RBFS use too little memory: they forget almost everything and must regenerate it. SMA* remembers as much as memory allows, so it repeats much less work.',
     'When a leaf is dropped, its f value is backed up into its parent. The parent then knows how good the best path through the forgotten subtree was, and regenerates it only if every other path looks worse.')}
{table(['Property', 'SMA*'], [
    ['Complete', 'Yes, if the depth of the shallowest goal is less than the memory size (the path must fit)'],
    ['Optimal', 'Yes, if an optimal solution fits in memory. Otherwise it returns the best solution that fits.'],
    ['Weak point', 'When memory is very tight, it can thrash: switch back and forth between paths and regenerate them many times']])}
{note('All three methods are a trade between time and memory. In practice, SMA* style methods are the most robust when memory is limited but not tiny.', 'tip')}
''', kw=['SMA*', 'simplified memory bounded A*', 'drop worst leaf', 'thrashing'])

K.lesson('maths', 'The maths: memory and repeated work', f'''
{fxs(
    fx('Memory', 'A*: O(b<sup>d</sup>)  IDA*, RBFS: O(b d)  SMA*: M, the memory you give it', 'b branching factor, d solution depth.', key=True),
    fx('IDA* number of iterations', 'k = number of distinct f values in (h(start), C*]', 'Romania: 366, 393, 413, 415, 417, 418 gives 6 iterations.'),
    fx('Worst case of IDA*', '1 + 2 + ... + N = N(N + 1) ⁄ 2 = O(N²)', 'If each iteration adds just one new node to the N nodes A* expands.'))}
{steps('Worked example: memory of A* against IDA*', [
    'b = 3, d = 20, 100 bytes a node.',
    'A* may store about 3²⁰ ≈ 3.5 × 10⁹ nodes, 350 GB.',
    'IDA* stores about b × d = 60 nodes, 6 KB.',
    eq('the price: re expanding the top of the tree once per iteration')])}
{steps('Worked example: IDA* worst case', [
    'A* would expand N = 1,000 nodes, all with different f values.',
    'IDA* then needs 1,000 iterations, the k-th one expanding k nodes.',
    eq('1,000 × 1,001 ⁄ 2 = 500,500 node expansions, about 500 times more than A*')])}
''', kw=['memory complexity', 'IDA* iterations', 'quadratic worst case'])

K.lesson('compare', 'BFS against IDS against IDA* against RBFS', f'''
{src('the question on slide 73.')}
{versus('Memory bounded search compared', ['', 'BFS', 'IDS', 'A*', 'IDA*', 'RBFS', 'SMA*'], [
    ['Uses h', 'No', 'No', 'Yes', 'Yes', 'Yes', 'Yes'],
    ['Optimal', 'Equal costs', 'Equal costs', 'Yes', 'Yes (admissible h)', 'Yes (admissible h)', 'If the solution fits'],
    ['Memory', 'O(b<sup>d</sup>)', 'O(b d)', 'O(b<sup>d</sup>)', 'O(b d)', 'O(b d)', 'M'],
    ['Repeated work', 'None', 'Top levels per iteration', 'None', 'One iteration per f value', 'Each time it switches back', 'Only for dropped nodes'],
    ['Romania, Arad to Bucharest', '450', '450', '418', '418, 6 iterations', '418, 2 switches', '418']],
    'IDA* is simplest and works well with few distinct f values (unit costs, puzzles). RBFS wastes less when f values vary. SMA* is best when you have a fixed amount of memory to fill.')}
{scene('solving the 15 puzzle', '<p>The 15 puzzle has about 10¹³ states. A* with Manhattan distance runs out of memory on hard instances, but IDA* with Manhattan distance (Korf, 1985) solves random instances optimally using a few kilobytes, because all costs are 1 and f takes few distinct values. Adding pattern databases makes it fast enough to solve the 24 puzzle too.</p>')}
''', kw=['comparison', 'IDA* against RBFS', '15 puzzle', 'Korf'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>If your notebook is small, you cannot write down every road you have looked at. So you remember only the road you are on and the best other choice, and you come back to it when your road gets too long.</p>',
    '<p>IDA*: DFS with an f cutoff that grows to the smallest f over the last limit. RBFS: recursion with an f-limit equal to the best alternative, and backed up values when it unwinds. SMA*: A* that drops the worst leaf. All optimal with an admissible h. IDA* and RBFS use O(b d) memory.</p>',
    '<p>IDA* repeats work when f values are many and different, up to O(N²). RBFS also repeats work when it switches between paths. Both cannot detect repeated states without extra memory, so on graphs with many cycles they may explore exponentially many paths to the same state. Transposition tables fix this with a fixed memory budget.</p>',
    '<p>Modern variants include IDA* with transposition tables and pattern databases, frontier search that drops the closed list, breadth first heuristic search, and external memory A* that keeps the frontier on disk, which solved problems with more than 10¹² states.</p>')}
''', kw=['transposition table', 'external memory A*', 'frontier search'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A* runs out of memory before time, because it stores every node.',
    '<b>IDA*</b>: DFS with an f cutoff. The next cutoff is the smallest f over the old one. Romania: 366, 393, 413, 415, 417, 418. Linear memory, optimal with admissible h.',
    '<b>RBFS</b>: go into the best child with f-limit = min(limit, best alternative). When the best f goes over the limit, unwind and back up that f. Linear memory, optimal.',
    '<b>SMA*</b>: A* until memory is full, then drop the worst leaf and back up its f to the parent. Optimal if the solution fits.',
    'The trade: less memory means more repeated work. IDA* can take O(N²) when every f is different.'],
    'chapter 3.4 searches when actions are non deterministic, with AND OR trees and AO*.')}
{nbcard('memory-bounded', 'Run IDA* and RBFS on Romania, then write IDA* and RBFS yourself on a small graph, the kind of task set in the minor exam.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'IDA* uses a cutoff on', ['Depth', 'g(n)', 'f(n) = g(n) + h(n)', 'h(n)'], 2,
       'The A* value.', 'It cuts off when f exceeds the limit.')
K.quiz('e', 'The first f limit of IDA* is', ['0', 'h(start)', '∞', 'C*'], 1,
       'f(start) = 0 + h(start).', 'From Arad it is 366.')
K.quiz('e', 'How much memory do IDA* and RBFS need?', ['O(b<sup>d</sup>)', 'O(b d)', 'O(1)', 'O(d²)'], 1,
       'Like DFS.', 'Only the current path and the children along it.')
K.quiz('e', 'SMA* drops which node when memory is full?', ['The newest', 'The leaf with the highest f', 'The root', 'A random one'], 1,
       'The worst.', 'And backs its f up to the parent.')
K.quiz('m', 'IDA* from Arad: what is the limit of the third iteration?', ['393', '413', '415', '418'], 1,
       '366, 393, ...', 'The limits are 366, 393, 413, 415, 417, 418.')
K.quiz('m', 'In RBFS at Sibiu, the f-limit passed to Rimnicu Vilcea is', ['447', '415', '413', '417'], 1,
       'min(limit, best alternative).', 'min(447, f(Fagaras) = 415) = 415.')
K.quiz('m', 'When RBFS unwinds from Rimnicu Vilcea, its stored f becomes', ['413', '415', '417', '418'], 2,
       'The best f below it.', 'Pitesti had f = 417, so the backed up value is 417.')
K.quiz('m', 'Why can IDA* be slow when step costs are many different real numbers?', ['It needs more memory', 'Each iteration may add only one new node', 'It becomes greedy', 'h becomes inadmissible'], 1,
       'Distinct f values.', 'One iteration per distinct f value, so up to O(N²) work.')
K.quiz('h', 'SMA* is complete if', ['Always', 'The depth of the shallowest goal fits in memory', 'h is consistent', 'b = 2'], 1,
       'The path must fit.', 'Otherwise it cannot even store the solution path.')
K.quiz('h', 'RBFS sets a child\'s f to max(g + h, parent f). Why?', ['To save memory', 'So a backed up value is not lost when the child is regenerated', 'To make h consistent', 'It has no effect'], 1,
       'Inherited bound.', 'When a forgotten subtree is regenerated, its children should not look better than the value backed up for it.')
K.quiz('x', 'In the style of an IIT Delhi exam: on a graph with many cycles and no transposition table, IDA* may', ['Use exponential memory', 'Explore the same state through exponentially many paths', 'Become incomplete', 'Return a suboptimal path'], 1,
       'No closed list.', 'It only checks the current path, so different paths to the same state are explored again and again.')
K.quiz('x', 'In the style of a CMU 15-780 exam: which property must the heuristic have for IDA* to be optimal?', ['Consistent', 'Admissible', 'Zero', 'Dominant'], 1,
       'IDA* is a tree search.', 'Tree search A* only needs admissibility, and so does IDA*.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'IDA* from Arad: how many iterations until Bucharest is found? Limits 366, 393, 413, 415, 417, 418.', '6', 'Count the limits.',
       ['366, 393, 413: 3.', '415, 417, 418: 3 more.', eq('6 iterations')], check=6)
K.calc('e', 'f(Timisoara) from Arad: g = 118, h = 329.', '447', 'Add.',
       ['g + h.', '118 + 329.', eq('447')], check=447)
K.calc('e', 'IDA* memory with b = 3 and d = 20 using b × d nodes.', '60', 'Multiply.',
       ['b × d.', '3 × 20.', eq('60 nodes')], check=60)
K.calc('m', 'RBFS: f(Bucharest via Fagaras) = 140 + 99 + 211 + 0.', '450', 'Add the roads.',
       ['140 + 99 = 239.', '239 + 211 = 450.', eq('450, over the limit 417, so Fagaras backs up 450')], check=450)
K.calc('m', 'RBFS at Sibiu after Fagaras backs up 450: what limit is passed to Rimnicu Vilcea now? Limit from Arad 447.', '447', 'min(447, 450).',
       ['The alternative is now Fagaras with 450.', 'min(447, 450).', eq('447')], check=447)
K.calc('m', 'IDA* worst case: A* would expand N = 100 nodes, each with a distinct f. Expansions of IDA* using N(N + 1) ⁄ 2?', '5050', 'Triangle number.',
       ['100 × 101 = 10,100.', 'Divide by 2.', eq('5,050')], check=5050)
K.calc('m', 'A* memory with b = 3, d = 12 (about 3¹² nodes). How many nodes?', '531441', 'Power.',
       ['3⁶ = 729.', '729² = 531,441.', eq('531,441')], check=3 ** 12)
K.calc('h', 'A tree with unit costs, h = 0, goal at depth 4. IDA* limits are 0, 1, 2, 3, 4. How many iterations?', '5', 'With h = 0 IDA* is IDS.',
       ['f = g = depth.', 'Limits 0 to 4.', eq('5 iterations, the same as IDS')], check=5)
K.calc('h', 'RBFS at a node with children f = 20, 25, 30 and a limit 22 from above. What f-limit is passed to the best child?', '22', 'min(limit, second best).',
       ['Best child f = 20.', 'Second best 25. min(22, 25).', eq('22')], check=22)
K.calc('x', 'In the style of a Stanford exam: SMA* has room for 3 nodes. Leaves in memory have f = 12, 15 and 19, and a new node must be added. Which f is backed up to the parent of the dropped leaf?', '19', 'Drop the highest f.',
       ['Memory is full.', 'The worst leaf has f = 19.', eq('19 is backed up to its parent')], check=19)

# ---------------------------------------------------------------- assignments
G = "{'S': [['A', 1], ['B', 4]], 'A': [['B', 2], ['C', 5]], 'B': [['C', 1]], 'C': [['G', 3]], 'G': []}"
H = "{'S': 6, 'A': 5, 'B': 3, 'C': 2, 'G': 0}"
K.assign('ida', 'm', 'Write IDA*',
         '<p>Write <code>ida_star(graph, h, start, goal)</code>. graph maps a node to a list of [child, cost]. Return [cost, limits], where limits is the list of f limits used, the last being the one where the goal is found. Return None if the goal cannot be reached.</p>',
         '''
def ida_star(graph, h, start, goal):
    # your code here
    pass
''', [(f"ida_star({G}, {H}, 'S', 'G')", [7, [6, 7]]),
      ("ida_star({'S': [['n1', 10], ['n3', 100]], 'n1': [['n2', 10]], 'n2': [['Goal', 10]], 'n3': [['Goal', 10]], 'Goal': []}, {'S': 30, 'n1': 20, 'n2': 10, 'n3': 10, 'Goal': 0}, 'S', 'Goal')", [30, [30]]),
      ("ida_star({'A': [['B', 1]], 'B': []}, {'A': 0, 'B': 0, 'C': 0}, 'A', 'C')", None)],
         '''
def ida_star(graph, h, start, goal):
    big = 10 ** 9

    def search(node, g, limit, path):
        f = g + h[node]
        if f > limit:
            return None, f
        if node == goal:
            return g, f
        smallest = big
        for child, cost in graph[node]:
            if child not in path:
                found, over = search(child, g + cost, limit, path + [child])
                if found is not None:
                    return found, over
                smallest = min(smallest, over)
        return None, smallest

    limit = h[start]
    limits = []
    while limit < big:
        limits.append(limit)
        found, nxt = search(start, 0, limit, [start])
        if found is not None:
            return [found, limits]
        limit = nxt
    return None
''', 'Write a helper that returns (cost, f) when it finds the goal and (None, smallest f over the limit) otherwise. Loop until the limit becomes "infinity".', '<p>On the small graph, the first limit is h(S) = 6. The smallest f over 6 is 7, and the goal is found at 7.</p>')
K.assign('rbfs', 'h', 'Write RBFS',
         '<p>Write <code>rbfs_cost(graph, h, start, goal)</code> that returns the cost of the path RBFS finds (or None). graph maps a node to a list of [child, cost]. Use f(child) = max(g + h(child), f(parent)), the f-limit min(limit, second best f), and back up the f of a child when it fails.</p>',
         '''
def rbfs_cost(graph, h, start, goal):
    # your code here
    pass
''', [(f"rbfs_cost({G}, {H}, 'S', 'G')", 7),
      ("rbfs_cost({'S': [['n1', 10], ['n3', 100]], 'n1': [['n2', 10]], 'n2': [['Goal', 10]], 'n3': [['Goal', 10]], 'Goal': []}, {'S': 30, 'n1': 20, 'n2': 10, 'n3': 10, 'Goal': 0}, 'S', 'Goal')", 30),
      ("rbfs_cost({'A': [['B', 1]], 'B': []}, {'A': 0, 'B': 0, 'C': 0}, 'A', 'C')", None)],
         '''
def rbfs_cost(graph, h, start, goal):
    big = 10 ** 9

    def rbfs(node, g, f_node, limit, path):
        if node == goal:
            return g, f_node
        kids = []
        for child, cost in graph[node]:
            if child not in path:
                kids.append([max(g + cost + h[child], f_node), child, g + cost])
        if len(kids) == 0:
            return None, big
        while True:
            kids.sort()
            best = kids[0]
            if best[0] > limit or best[0] >= big:     # over the limit, or every child is a dead end
                return None, best[0]
            alt = big
            if len(kids) > 1:
                alt = kids[1][0]
            result, best[0] = rbfs(best[1], best[2], best[0], min(limit, alt), path + [best[1]])
            if result is not None:
                return result, best[0]

    cost, f = rbfs(start, 0, h[start], big, [start])
    return cost
''', 'Keep the children as [f, name, g] lists so you can change f in place when a child backs up a value.', '<p>This is the same RBFS as the lesson, returning the cost instead of the path. When no path exists, the best f becomes "infinity" (big) and RBFS stops.</p>')

K.must('Why', 'A* stores every node and runs out of memory first. Memory bounded methods trade memory for repeated work.')
K.must('IDA*', 'DFS with an f cutoff, next cutoff = smallest f over the old one. Romania: 366, 393, 413, 415, 417, 418.')
K.must('RBFS', 'f-limit = min(limit, best alternative). Unwind when best f &gt; limit and back up that f. Linear memory.')
K.must('SMA*', 'A* until memory is full, then drop the highest f leaf and back up its f. Optimal if the solution fits.')
K.must('Costs', 'IDA* and RBFS: O(b d) memory. IDA* worst case O(N²) time with many distinct f values.')

T = K.topic(
    slug='memory-bounded', topic='memory-bounded', step=(3, 'Informed search', 'cai-informed', 'Search with a hint of where the goal is: greedy best first, A*, heuristic design, memory bounded and AND OR search.', 'College'),
    title='Memory bounded heuristic search: IDA*, RBFS and SMA*', short='IDA*, RBFS, SMA*', badge='3.3', minutes=55,
    lead='A* finds the cheapest path but keeps every node in memory. IDA*, RBFS and SMA* keep it optimal with linear or fixed memory, by repeating some work. Step through each one on the Romania map.',
    desc='Why A* runs out of memory, IDA* and its f limits, RBFS with the f-limit and backed up values on the slide example, SMA*, the cost of repeated work, and a comparison of BFS, IDS, A*, IDA*, RBFS and SMA*.',
    summary='IDA* with f cutoffs, RBFS with f-limits and backed up values, SMA*, and the memory against time trade.',
    keywords=['IDA*', 'RBFS', 'SMA*', 'memory bounded search', 'iterative deepening A*', 'recursive best first search'],
    recap='<p>IDA* deepens on f, RBFS remembers the best alternative, SMA* fills its memory and forgets the worst leaf.</p>',
    nb={'ida': 'IDA* on the Romania map', 'rbfs': 'RBFS on the Romania map'})
