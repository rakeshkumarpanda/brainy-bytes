# Chapter 2.2: depth first, depth limited, iterative deepening and bidirectional search. Source: slide Set 2,
# slides 40 to 52 (DFS and its backtrack points on the water jugs, DFS properties and tree against graph search,
# depth limited search with limit D, iterative deepening and its stopping rule, food for thought III on path and
# cycle checking) and the class of 25 January 2026. The IDS node count and bidirectional search follow
# Russell and Norvig, Artificial Intelligence: A Modern Approach, 4th ed., sections 3.4.3 to 3.4.5.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('dfs', r'''
# Depth first search on the slide tree: A has children B and C, B has D and E, and so on down to O.
tree = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F", "G"], "D": ["H", "I"], "E": ["J", "K"],
        "F": ["L", "M"], "G": ["N", "O"]}

def dfs(node, goal, path):
    path = path + [node]
    print("visit", node)
    if node == goal:
        return path
    for child in tree.get(node, []):     # leaves have no entry, so they get []
        found = dfs(child, goal, path)
        if found is not None:
            return found
    return None                           # dead end: go back up (backtrack)

print("path:", dfs("A", "M", []))
''')

K.code('ids', r'''
# Iterative deepening: depth limited search with limit 0, then 1, then 2, ... until the goal is found.
tree = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F", "G"], "D": ["H", "I"], "E": ["J", "K"],
        "F": ["L", "M"], "G": ["N", "O"]}

def dls(node, goal, limit):
    if node == goal:
        return [node]
    if limit == 0:
        return None                       # cut off: do not go deeper
    for child in tree.get(node, []):
        found = dls(child, goal, limit - 1)
        if found is not None:
            return [node] + found
    return None

for limit in range(5):
    result = dls("A", "M", limit)
    print("limit", limit, "->", result)
    if result is not None:
        break
''')

K.lesson('dfs', 'Depth first search', f'''
{src('slide Set 2, slides 40 to 44, and the class of 25 January 2026.')}
{wwh('Depth first search (DFS) always expands the deepest node in the frontier. It goes down one branch as far as it can, and only when it hits a dead end does it go back and try the next branch.',
     'BFS keeps whole levels in memory. DFS keeps only the current path and the untried brothers of its nodes, so it needs very little memory. It also matches how people solve mazes and puzzles: try a way, and back up when stuck.',
     'Keep the frontier as a stack (last in, first out), or write it as a recursive function. Take out the newest path, and push its children on top. The nodes left on the stack are the backtrack points.')}
<p>On slide 43 DFS on the water jugs goes (0,0) → (3,0) → (0,0) → (3,0) → ... for ever in tree search, because Fill-3 then Empty-3 makes a cycle. The other children, (0,4), (3,4) and (0,3), wait on OPEN as backtrack points. This is why DFS needs a cycle check.</p>
{viz('searchgraph', alg='dfs', gr='tree', start='A', goal='M')}
{code('dfs')}
{table(['Property', 'DFS', 'Why'], [
    ['Complete', 'No on infinite or cyclic spaces (tree search). Yes on finite spaces with graph search or a path check.', 'It can follow an infinite branch for ever.'],
    ['Optimal', 'No', 'It returns the first goal it meets, which may be deep and costly.'],
    ['Time', 'O(b<sup>m</sup>)', 'm is the largest depth. It may explore the whole tree, and m can be much bigger than d.'],
    ['Space', 'O(b m)', 'Only one path plus the untried children of each node on it.']])}
{note('Backtracking search, a version of DFS that generates one child at a time and undoes changes when it goes back, needs only O(m) memory. It is the basis of CSP solvers (chapter 5.2) and Prolog.', 'tip')}
''', kw=['depth first search', 'DFS', 'stack', 'LIFO', 'backtracking', 'backtrack point', 'cycle'])

K.lesson('cycles', 'Path checking and cycle checking', f'''
{src('slide Set 2, slide 52, food for thought III.')}
<p>DFS without memory can loop. There are two cheap fixes and one expensive one.</p>
{table(['Check', 'What it does', 'Memory', 'What it misses'], [
    ['Parent check', 'Do not go straight back to the state you came from', 'None', 'Longer cycles like A → B → C → A'],
    ['Path check', 'Do not add a child whose state is already on the current path', 'O(m), the path is already stored', 'Two different paths to the same state (redundant paths)'],
    ['Full cycle check (graph search)', 'Do not add a child whose state was ever explored', 'O(number of states)', 'Nothing, but memory grows like BFS']])}
{steps('Worked example: path checking on the jugs', [
    'DFS is at path (0,0), (3,0). The children of (3,0) are (3,4), (0,0) and (0,3).',
    '(0,0) is already on the path, so the path check drops it.',
    'DFS goes on to (3,4), whose children are (0,4) and (3,0). (3,0) is on the path, dropped.',
    eq('the cycle Fill-3, Empty-3 is gone and DFS keeps moving forward')])}
{note('A path check makes DFS complete on any finite state space, while keeping memory at O(b m). It can still visit the same state many times along different paths, so the time may be much more than the number of states.', 'exam')}
''', kw=['path checking', 'cycle checking', 'redundant paths', 'graph search'])

K.lesson('dls', 'Depth limited and iterative deepening search', f'''
{src('slide Set 2, slides 45 to 51.')}
{wwh('Depth limited search (DLS) is DFS that never goes deeper than a limit D. Iterative deepening search (IDS) runs DLS with D = 0, 1, 2, ... until it finds a goal.',
     'BFS has memory problems and DFS can run down an endless path. DLS stops the endless path. IDS also removes the need to guess D, and gets the best of both: the low memory of DFS and the completeness and shortest answer of BFS.',
     'In DLS, a node at depth D is treated as if it had no children. On the slides the root is depth 0, and no path longer than D + 1 states is put on OPEN. IDS repeats DLS with a bigger limit each time. It stops when a goal is found, or when a DLS finishes without cutting off any node, which proves that no solution exists.')}
{table(['DLS result', 'Meaning'], [
    ['A solution', 'A goal was found at depth ≤ D'],
    ['Failure', 'No solution exists at all (nothing was cut off)'],
    ['Cutoff', 'No solution within the limit, but deeper nodes were cut off, so one may exist deeper']])}
{viz('searchgraph', alg='ids', gr='tree', start='A', goal='M', lim=3)}
{code('ids')}
{note('IDS is the preferred uninformed method when the search space is large and the depth of the solution is not known (slide 49).', 'tip')}
''', kw=['depth limited search', 'iterative deepening', 'IDS', 'DLS', 'cutoff', 'depth limit'])

K.lesson('idscost', 'Is iterative deepening wasteful', f'''
<p>IDS regenerates the top levels again in every iteration. That sounds wasteful, but it is not, because almost all nodes are in the last level.</p>
{fxs(
    fx('Nodes generated by IDS', 'N(IDS) = (d + 1)·1 + d·b + (d − 1)·b² + ... + 1·b<sup>d</sup> = ∑<sub>i=0</sub><sup>d</sup> (d + 1 − i) b<sup>i</sup>', 'Level i is generated in every iteration from i to d, that is d + 1 − i times.', key=True),
    fx('Overhead of IDS over BFS', 'N(IDS) ⁄ N(BFS) ≈ b ⁄ (b − 1)', 'For b = 10 that is 1.11, only 11 percent more work. For b = 2 it is 2 times.', key=True),
    fx('Cost of IDS', 'time O(b<sup>d</sup>), space O(b d)', 'Complete when b is finite, and optimal when all actions cost the same.'))}
{steps('Worked example: b = 10, d = 5', [
    'IDS: 6 × 1 + 5 × 10 + 4 × 100 + 3 × 1,000 + 2 × 10,000 + 1 × 100,000.',
    '= 6 + 50 + 400 + 3,000 + 20,000 + 100,000 = 123,456.',
    'BFS (tested at generation): 1 + 10 + 100 + 1,000 + 10,000 + 100,000 = 111,111.',
    eq('123,456 ⁄ 111,111 ≈ 1.11')])}
{deep('iterative lengthening search', '<p>The cost version of IDS uses a limit on g(n) instead of depth: run a cost limited DFS, and raise the limit to the smallest cost that was cut off. It is optimal with costs, but with many different cost values it may need one iteration per distinct cost, which can be very slow. IDA* (chapter 3.3) uses the same idea with f = g + h, where it works much better.</p>')}
''', kw=['iterative deepening cost', 'overhead', 'node count', 'iterative lengthening'])

K.lesson('bidir', 'Bidirectional search', f'''
{wwh('Bidirectional search runs two searches at once: one forward from the start and one backward from the goal. It stops when the two frontiers meet.',
     'Two searches of depth d ⁄ 2 are far smaller than one search of depth d, because the cost is exponential in depth.',
     'Alternate one step of each search. Each time a node is generated, check whether its state is already in the other search. The backward search needs predecessors, so the actions must be reversible or easy to undo, and the goal must be one explicit state.')}
{fxs(fx('Cost of bidirectional search', '2 · b<sup>d⁄2</sup> = O(b<sup>d⁄2</sup>) instead of O(b<sup>d</sup>)', 'For b = 10 and d = 6 that is 2,000 nodes against 1,000,000.', key=True))}
{steps('Worked example: b = 10, d = 8', [
    'One BFS: about 10⁸ = 100,000,000 nodes in the last level.',
    'Two BFS of depth 4: about 2 × 10⁴ = 20,000 nodes.',
    eq('5,000 times less work')])}
{note('When the frontiers first meet, the joined path is not always the shortest. With uniform costs, finish the current level before stopping, then pick the best meeting point.', 'warn')}
''', kw=['bidirectional search', 'meet in the middle', 'b to the d over 2'])

K.lesson('compare', 'All five uninformed methods side by side', f'''
{versus('Comparing uninformed search (b branching factor, d depth of shallowest goal, m largest depth, l depth limit, C* optimal cost)', ['Criterion', 'BFS', 'UCS', 'DFS', 'DLS', 'IDS', 'Bidirectional'], [
    ['Complete', 'Yes (finite b)', 'Yes (costs ≥ ε)', 'No', 'No (only if d ≤ l)', 'Yes (finite b)', 'Yes (with BFS both ways)'],
    ['Optimal', 'Equal costs only', 'Yes', 'No', 'No', 'Equal costs only', 'Equal costs only'],
    ['Time', 'O(b<sup>d</sup>)', 'O(b<sup>1 + ⌊C*⁄ε⌋</sup>)', 'O(b<sup>m</sup>)', 'O(b<sup>l</sup>)', 'O(b<sup>d</sup>)', 'O(b<sup>d⁄2</sup>)'],
    ['Space', 'O(b<sup>d</sup>)', 'O(b<sup>1 + ⌊C*⁄ε⌋</sup>)', 'O(b m)', 'O(b l)', 'O(b d)', 'O(b<sup>d⁄2</sup>)']],
    'IDS is the best default when costs are equal and the depth is unknown. UCS is the choice when costs differ. Bidirectional search wins when you can search backward from a single goal.')}
{scene('finding a friend of a friend', '<p>A social network wants to show how you are linked to a stranger. Each person has about 300 friends. A forward BFS of depth 6 would touch 300⁶ ≈ 7 × 10¹⁴ people, more than exist. Searching 3 steps from each side touches about 2 × 300³ = 54 million, and real systems go further with indexes. This meet in the middle idea is how "degrees of separation" features work.</p>')}
''', kw=['comparison table', 'uninformed search', 'six degrees'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>DFS is walking through a maze, keeping one hand on the wall: go as far as you can, then go back to the last turn you did not take. IDS does this with a rope that gets longer each time, so you never get lost too far away.</p>',
    '<p>DFS: stack, O(b m) space, not complete or optimal. DLS: DFS with a depth limit, returns solution, failure or cutoff. IDS: DLS with limits 0, 1, 2, ..., complete and optimal for equal costs, O(b<sup>d</sup>) time, O(b d) space, about b ⁄ (b − 1) times the work of BFS. Bidirectional: O(b<sup>d⁄2</sup>).</p>',
    '<p>IDS is asymptotically optimal among uninformed tree searches that use linear memory: any such method must look at the b<sup>d</sup> nodes of the last level in the worst case, and IDS adds only a constant factor. Choosing between path checking and full duplicate detection is a trade of memory against repeated work.</p>',
    '<p>Front to front bidirectional heuristic search, and the meet in the middle algorithm MM (Holte and others, 2016), guarantee that the two searches meet in the middle. Research on breadth first heuristic search and frontier search shows how to drop the explored set while still detecting duplicates, using the structure of the graph.</p>')}
{deep('why IDS is complete but DFS is not, in one line each', '<p>DFS can pick an infinite branch first and never return. IDS bounds every iteration, so each iteration finishes, and the iteration with limit d finds a goal at depth d.</p>')}
''', kw=['maze', 'asymptotic optimality', 'MM algorithm', 'frontier search'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>DFS</b> expands the deepest node (a stack or recursion). Space O(b m), time O(b<sup>m</sup>). Not optimal, and not complete on infinite or cyclic spaces.',
    'A <b>path check</b> drops children already on the current path. It makes DFS complete on finite spaces without extra memory.',
    '<b>DLS</b> stops at depth D and returns a solution, failure or cutoff.',
    '<b>IDS</b> runs DLS with D = 0, 1, 2, .... Complete, optimal for equal costs, O(b<sup>d</sup>) time and O(b d) space. It does about b ⁄ (b − 1) times the work of BFS (123,456 against 111,111 for b = 10, d = 5).',
    '<b>Bidirectional</b> search meets in the middle in O(b<sup>d⁄2</sup>), but needs reversible actions and one explicit goal.'],
    'chapter 3.1 adds knowledge about the goal with greedy best first and A* search.')}
{nbcard('dfs-ids', 'Trace DFS and iterative deepening on the slide tree, then write depth limited search and count the nodes IDS generates.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which data structure gives depth first order?', ['A FIFO queue', 'A stack (LIFO)', 'A priority queue', 'A set'], 1,
       'Last in, first out.', 'The newest path is extended first, so the search goes deep.')
K.quiz('e', 'The space needed by DFS is', ['O(b<sup>d</sup>)', 'O(b m)', 'O(b<sup>m</sup>)', 'O(1)'], 1,
       'One path plus brothers.', 'It stores the current path and the untried children along it.')
K.quiz('e', 'On the slide tree with goal M, the first node DFS visits after A is', ['C', 'B', 'M', 'D'], 1,
       'Leftmost first.', 'A B D H I E J K C F L M.')
K.quiz('e', 'Which method is preferred when the space is large and the solution depth is unknown?', ['DFS', 'DLS', 'IDS', 'Random search'], 2,
       'Slide 49.', 'IDS needs no depth guess and little memory.')
K.quiz('m', 'DLS returns "cutoff". What does that mean?', ['No solution exists', 'A solution was found', 'No solution within the limit, but one may exist deeper', 'The graph has a cycle'], 2,
       'Nodes were cut.', 'Some nodes were not expanded because of the limit.')
K.quiz('m', 'When can IDS stop and say "no solution exists"?', ['After limit 10', 'When a DLS fails without cutting off any node', 'Never', 'When memory runs out'], 1,
       'Nothing pruned.', 'Then every path was examined and none reached a goal.')
K.quiz('m', 'A path check in DFS', ['Removes all repeated states', 'Drops children whose state is already on the current path', 'Needs O(b<sup>d</sup>) memory', 'Makes DFS optimal'], 1,
       'Only the current path.', 'It removes cycles but not redundant paths through different branches.')
K.quiz('m', 'Why is DFS not optimal?', ['It uses a stack', 'It returns the first goal found, which may be deep or costly', 'It never finds a goal', 'It needs a heuristic'], 1,
       'First is not best.', 'A shallower or cheaper goal may sit in a branch it has not tried yet.')
K.quiz('h', 'For b = 10, how much more work does IDS do than BFS, roughly?', ['2 times', '11 percent more', '10 times', 'The same'], 1,
       'b ⁄ (b − 1).', '10 ⁄ 9 ≈ 1.11.')
K.quiz('h', 'Bidirectional search needs', ['A heuristic', 'Reversible actions and an explicit goal state', 'A depth limit', 'Negative costs'], 1,
       'Search backward.', 'The backward search must compute predecessors of the goal.')
K.quiz('x', 'In the style of a CMU 15-780 question: on a tree with b = 2, IDS generates about how many times the nodes BFS generates?', ['1.11', '2', '4', 'd times'], 1,
       'b ⁄ (b − 1).', '2 ⁄ 1 = 2. With a small branching factor the repeated top levels matter much more.')
K.quiz('x', 'In the style of an Oxford AI exam: the state space is finite but has cycles, and memory is very tight. Which method is complete with linear memory?', ['DFS without checks', 'BFS', 'IDS with a path check', 'Greedy best first'], 2,
       'Linear memory and complete.', 'IDS keeps O(b d) memory and, with a path check, every iteration finishes and the right limit finds the goal.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many nodes does the slide binary tree A to O have (depths 0 to 3)?', '15', '1 + 2 + 4 + 8.',
       ['Depth 0: A. Depth 1: B, C.', 'Depth 2: D, E, F, G. Depth 3: H to O.', eq('1 + 2 + 4 + 8 = 15')], check=15)
K.calc('e', 'DFS on the slide tree with goal M visits A B D H I E J K C F L M. How many nodes does it visit?', '12', 'Count.',
       ['A B D H I E J K: 8 nodes.', 'C F L M: 4 more.', eq('12')], check=12)
K.calc('e', 'DFS space: b = 3 and m = 10. About how many nodes are stored, using b × m?', '30', 'Multiply.',
       ['Each of the m levels keeps at most b nodes.', '3 × 10.', eq('30')], check=30)
K.calc('m', 'IDS nodes for b = 10, d = 5, using ∑ (d + 1 − i) b<sup>i</sup>.', '123456', 'Add six terms.',
       ['6 + 50 + 400 = 456.', '3,000 + 20,000 + 100,000 = 123,000.', eq('123,456')], check=sum((6 - i) * 10 ** i for i in range(6)))
K.calc('m', 'IDS nodes for b = 2, d = 3.', '26', '∑ (4 − i) 2<sup>i</sup>.',
       ['4 × 1 + 3 × 2 = 10.', '2 × 4 + 1 × 8 = 16.', eq('10 + 16 = 26')], check=sum((4 - i) * 2 ** i for i in range(4)))
K.calc('m', 'Bidirectional BFS with b = 10 and d = 6. About how many nodes, using 2 b<sup>d⁄2</sup>?', '2000', 'd ⁄ 2 = 3.',
       ['10³ = 1,000.', 'Two searches.', eq('2,000')], check=2000)
K.calc('m', 'How many times does IDS generate the root when it finds a goal at depth 4?', '5', 'Limits 0 to 4.',
       ['Every iteration starts at the root.', 'Iterations with limit 0, 1, 2, 3, 4.', eq('5 times')], check=5)
K.calc('h', 'Ratio N(IDS) ⁄ N(BFS) for b = 2, d = 3. BFS generates 1 + 2 + 4 + 8. Give 2 decimals.', '1.73', '26 ⁄ 15.',
       ['N(IDS) = 26 (from the earlier problem).', 'N(BFS) = 15.', eq('26 ⁄ 15 ≈ 1.73')], check=26 / 15, tol=0.01)
K.calc('h', 'Bidirectional against one BFS for b = 10, d = 8. How many times less work, using 10<sup>8</sup> against 2 × 10<sup>4</sup>?', '5000', 'Divide.',
       ['One search: 10⁸.', 'Two half searches: 2 × 10⁴.', eq('10⁸ ⁄ (2 × 10⁴) = 5,000')], check=10 ** 8 // (2 * 10 ** 4))
K.calc('x', 'In the style of a Stanford CS221 problem: a social network has 300 friends per person. How many people does a meet in the middle search of 3 steps from each side touch, using 2 × 300³? Give the answer in millions.', '54', '300³ = 27 million.',
       ['300³ = 27,000,000.', 'Two sides.', eq('54 million')], check=2 * 300 ** 3 / 10 ** 6)

# ---------------------------------------------------------------- assignments
K.assign('dls', 'e', 'Depth limited search',
         '<p>Write <code>dls(graph, node, goal, limit)</code>. graph maps a node to a list of children (a missing key means no children). Return the path from node to goal as a list if the goal is at depth ≤ limit, else None. Try children in list order.</p>',
         '''
def dls(graph, node, goal, limit):
    # your code here
    pass
''', [("dls({'A': ['B', 'C'], 'B': ['D'], 'C': ['E']}, 'A', 'E', 2)", ['A', 'C', 'E']),
      ("dls({'A': ['B', 'C'], 'B': ['D'], 'C': ['E']}, 'A', 'E', 1)", None),
      ("dls({'A': ['B']}, 'A', 'A', 0)", ['A']),
      ("dls({'A': ['B', 'C'], 'B': ['C'], 'C': []}, 'A', 'C', 3)", ['A', 'B', 'C'])],
         '''
def dls(graph, node, goal, limit):
    if node == goal:
        return [node]
    if limit == 0:
        return None
    for child in graph.get(node, []):
        found = dls(graph, child, goal, limit - 1)
        if found is not None:
            return [node] + found
    return None
''', 'Check the goal, then stop if the limit is 0, else call yourself on each child with limit − 1.', '<p>DFS with a counter. The last test shows DFS returns the first goal it meets (via B), not the shortest (A, C).</p>')
K.assign('idscount', 'm', 'Count the nodes of iterative deepening',
         '<p>Write <code>ids_nodes(b, d)</code> that returns how many nodes IDS generates on a full tree with branching factor b when the goal is at depth d: level i is generated d + 1 − i times. Also write <code>bfs_nodes(b, d)</code> for 1 + b + ... + b<sup>d</sup>.</p>',
         '''
def ids_nodes(b, d):
    # your code here
    pass

def bfs_nodes(b, d):
    # your code here
    pass
''', [("ids_nodes(10, 5)", 123456), ("bfs_nodes(10, 5)", 111111), ("ids_nodes(2, 3)", 26), ("bfs_nodes(2, 0)", 1)],
         '''
def ids_nodes(b, d):
    total = 0
    for i in range(d + 1):
        total = total + (d + 1 - i) * b ** i
    return total

def bfs_nodes(b, d):
    total = 0
    for i in range(d + 1):
        total = total + b ** i
    return total
''', 'Loop over the levels 0 to d and add the count for each level.', '<p>The ratio ids_nodes ⁄ bfs_nodes tends to b ⁄ (b − 1).</p>')

K.must('DFS', 'Stack. O(b m) space, O(b<sup>m</sup>) time. Not complete on infinite or cyclic spaces, not optimal.')
K.must('DLS', 'DFS with depth limit D. Returns solution, failure, or cutoff. Complete only if d ≤ D.')
K.must('IDS', 'DLS with D = 0, 1, 2, .... Complete, optimal for equal costs, O(b<sup>d</sup>) time, O(b d) space.')
K.must('IDS overhead', '∑ (d + 1 − i) b<sup>i</sup>, about b ⁄ (b − 1) times BFS. b = 10, d = 5: 123,456 against 111,111.')
K.must('Path check', 'Drop a child already on the current path. Removes cycles, keeps O(b m) memory.')
K.must('Bidirectional', 'Search from both ends, O(b<sup>d⁄2</sup>). Needs reversible actions and one explicit goal.')

T = K.topic(
    slug='dfs-ids', topic='dfs-ids', step=(2, 'Uninformed search', 'cai-uninformed', 'Search with no hints: level by level, cheapest first, deepest first, and with growing limits.', 'College'),
    title='Depth first, iterative deepening and bidirectional search', short='DFS, DLS and IDS', badge='2.2', minutes=50,
    lead='Depth first search saves memory by going deep first. Depth limited search stops endless dives, iterative deepening removes the need to guess the limit, and bidirectional search meets in the middle.',
    desc='DFS with a stack, backtrack points, path and cycle checks, depth limited search and its three results, iterative deepening and why its repeated work is small, bidirectional search and a comparison of all uninformed methods.',
    summary='DFS, DLS, IDS and bidirectional search, their memory and time, path checking, and the full comparison table.',
    keywords=['depth first search', 'DFS', 'depth limited search', 'iterative deepening', 'IDS', 'bidirectional search', 'path checking'],
    recap='<p>DFS saves memory, DLS bounds depth, IDS gets BFS answers with DFS memory, and bidirectional search halves the exponent.</p>',
    nb={'dfs': 'Depth first search on the slide tree', 'ids': 'Iterative deepening on the slide tree'})
