# Chapter 5.1: constraint satisfaction problems and arc consistency. Source: slide Set 4, slides 1 to 7 (CSP
# preliminaries, the N queens formulation with Boolean variables X_ij, map colouring and the car assembly job
# scheduling example, domain consistency, the constraint network, arc consistency and its three outcomes, AC-3,
# forward checking against arc consistency) and the class of 8 February 2026. Constraint types, path and k
# consistency and the AC-3 complexity follow Russell and Norvig, AIMA 4th ed., sections 6.1 and 6.2.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('check', r'''
# Map colouring of Australia as a CSP. A full assignment is a solution if no two neighbours share a colour.
neighbours = [("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "Q"), ("SA", "Q"),
              ("SA", "NSW"), ("SA", "V"), ("Q", "NSW"), ("NSW", "V")]

def broken(colour):
    bad = []
    for a, b in neighbours:
        if colour[a] == colour[b]:
            bad.append(a + "-" + b)
    return bad

good = {"WA": "red", "NT": "green", "SA": "blue", "Q": "red", "NSW": "green", "V": "red", "T": "green"}
poor = {"WA": "red", "NT": "green", "SA": "blue", "Q": "green", "NSW": "red", "V": "red", "T": "red"}
print("good assignment breaks:", broken(good))
print("poor assignment breaks:", broken(poor))
print("number of full assignments:", 3 ** 7)
''')

K.code('ac3', r'''
# AC-3 on the slide network: A < B and B < C, every domain {1, 2, 3}.
domains = {"A": [1, 2, 3], "B": [1, 2, 3], "C": [1, 2, 3]}

def ok(x, vx, y, vy):                    # is the pair allowed by the constraint between x and y?
    if (x, y) == ("A", "B"): return vx < vy
    if (x, y) == ("B", "A"): return vx > vy
    if (x, y) == ("B", "C"): return vx < vy
    if (x, y) == ("C", "B"): return vx > vy

def revise(x, y):
    removed = False
    for vx in domains[x][:]:              # loop over a copy, because we delete from the list
        support = False
        for vy in domains[y]:
            if ok(x, vx, y, vy):
                support = True
        if not support:
            domains[x].remove(vx)
            print("remove", vx, "from", x, "(no partner in", y + ")")
            removed = True
    return removed

queue = [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B")]
while len(queue) > 0:
    x, y = queue.pop(0)
    if revise(x, y):
        for arc in [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B")]:
            if arc[1] == x and arc[0] != y and arc not in queue:
                queue.append(arc)         # the neighbours of x must be checked again
print(domains)
''')

K.lesson('idea', 'What a constraint satisfaction problem is', f'''
{src('slide Set 4, slides 1 to 4, and the class of 8 February 2026.')}
<p>In ordinary search a state is a black box: the algorithm can only ask "is this the goal?" and "what are the successors?". In a <b>constraint satisfaction problem</b> (CSP) the state has an inner structure, a set of variables with values, and the goal is described by rules, so the algorithm can look inside and reason.</p>
{wwh('A CSP has a set of variables X = {X<sub>1</sub>, ..., X<sub>n</sub>}, a domain D<sub>i</sub> of allowed values for each variable, and a set of constraints C that say which combinations of values are allowed. A solution is a complete assignment that breaks no constraint.',
     'Only the final assignment matters, not the path. Writing the problem as variables and constraints lets general methods prune huge parts of the space at once: one rule like "WA and NT differ" removes every assignment that breaks it.',
     'Assign values one variable at a time, and after each choice use the constraints to remove values that can no longer work (constraint propagation). When a variable has no value left, go back (backtracking, chapter 5.2).')}
<h3>Example 1: colouring the map of Australia</h3>
{table(['Part', 'Value'], [
    ['Variables', 'WA, NT, SA, Q, NSW, V, T'],
    ['Domains', 'D<sub>i</sub> = {red, green, blue}'],
    ['Constraints', 'Neighbouring regions differ: WA ≠ NT, WA ≠ SA, NT ≠ SA, NT ≠ Q, SA ≠ Q, SA ≠ NSW, SA ≠ V, Q ≠ NSW, NSW ≠ V'],
    ['A solution', 'WA = red, NT = green, SA = blue, Q = red, NSW = green, V = red, T = green']])}
{code('check')}
<p>The <b>constraint graph</b> has a node for each variable and an edge for each binary constraint. Tasmania (T) has no edges, so it is an independent sub problem: any colour works.</p>
''', kw=['constraint satisfaction problem', 'CSP', 'variables', 'domains', 'constraints', 'map colouring', 'constraint graph'])

K.lesson('examples', 'More CSPs: N queens and job scheduling', f'''
{src('slide Set 4, slides 3 and 4.')}
<h3>N queens with Boolean variables (slide 3)</h3>
{table(['Part', 'Formulation'], [
    ['Variables', 'X<sub>ij</sub> for 0 ≤ i, j &lt; N, one for each square (row i, column j)'],
    ['Domains', '{0, 1}: 1 means a queen stands on the square'],
    ['Same row', '∀ i, j, k: (X<sub>ij</sub>, X<sub>ik</sub>) ∈ {(0, 0), (0, 1), (1, 0)}, at most one queen'],
    ['Same column', '∀ i, j, k: (X<sub>ij</sub>, X<sub>kj</sub>) ∈ {(0, 0), (0, 1), (1, 0)}'],
    ['Diagonals', '(X<sub>ij</sub>, X<sub>i+k, j+k</sub>) and (X<sub>ij</sub>, X<sub>i+k, j−k</sub>) ∈ {(0, 0), (0, 1), (1, 0)}'],
    ['Count', '∑<sub>i, j</sub> X<sub>ij</sub> = N, exactly N queens']])}
<p>A smaller formulation uses one variable Q<sub>j</sub> per column with domain {{0, ..., N − 1}} (the row of its queen). Then "one queen per column" is built in, and only rows and diagonals need constraints: Q<sub>j</sub> ≠ Q<sub>k</sub> and |Q<sub>j</sub> − Q<sub>k</sub>| ≠ |j − k|.</p>
<h3>Job scheduling: assembling a car (slide 4)</h3>
{table(['Part', 'Formulation'], [
    ['Variables', 'Axle<sub>F</sub>, Axle<sub>B</sub>, Wheel<sub>RF</sub>, Wheel<sub>LF</sub>, Wheel<sub>RB</sub>, Wheel<sub>LB</sub>, Nuts for each wheel, Cap for each wheel, Inspect: 15 tasks, each value is a start time'],
    ['Precedence', 'T<sub>1</sub> + d<sub>1</sub> ≤ T<sub>2</sub>: task 1 must finish before task 2 starts. Axle<sub>F</sub> + 10 ≤ Wheel<sub>RF</sub>, Wheel<sub>RF</sub> + 1 ≤ Nuts<sub>RF</sub>, Nuts<sub>RF</sub> + 2 ≤ Cap<sub>RF</sub>, ...'],
    ['Disjunctive', 'The two axles share one tool: Axle<sub>F</sub> + 10 ≤ Axle<sub>B</sub> or Axle<sub>B</sub> + 10 ≤ Axle<sub>F</sub>'],
    ['Inspection last', 'X + d<sub>X</sub> ≤ Inspect for every other task X, and Inspect takes 3 minutes'],
    ['Deadline 30 minutes', 'D<sub>i</sub> = {1, 2, 3, ..., 27}, so even Inspect ends by minute 30']])}
{table(['Kind of constraint', 'Example'], [
    ['Unary (one variable)', 'SA ≠ green, B ≠ 3'],
    ['Binary (two variables)', 'WA ≠ NT, A &lt; B'],
    ['Global (any number)', 'Alldiff(all cells in a Sudoku row)'],
    ['Preference (soft)', 'Prof. R prefers morning lectures. Breaking it costs, but is allowed (constrained optimisation)']])}
''', kw=['N queens CSP', 'boolean variables', 'job scheduling', 'precedence constraint', 'disjunctive constraint', 'unary', 'binary', 'global constraint', 'Alldiff'])

K.lesson('consistency', 'Node and arc consistency', f'''
{src('slide Set 4, slide 6.')}
{wwh('Constraint propagation removes values from domains that cannot be part of any solution, before or during search. Node consistency handles unary constraints and arc consistency handles binary ones.',
     'Every value removed now is a whole branch the search never has to try. Sometimes propagation alone solves the problem or proves it impossible, with no search at all.',
     'A variable is node consistent if every value in its domain satisfies its unary constraints, so dom(B) = {1, 2, 3, 4} is not node consistent under B ≠ 3. An arc ⟨X, r(X, Y)⟩ is arc consistent if for each value x in dom(X) there is some y in dom(Y) with r(x, y) true. If not, delete the values of X that have no partner.')}
{fxs(
    fx('Arc consistency', '∀ x ∈ dom(X) ∃ y ∈ dom(Y): r(x, y)', 'Every value of X has a supporting value of Y. A network is arc consistent when all its arcs are.', key=True),
    fx('The three outcomes (slide 6)', 'a domain is empty ⇒ no solution. Every domain has one value ⇒ the unique solution. Some domains have several values ⇒ search is still needed', 'Arc consistency alone does not always decide the problem.'))}
<p>The constraint network of the slides has one node per variable, one node per constraint, and an edge between a variable and each constraint it appears in. Each binary constraint gives two arcs, one in each direction.</p>
''', kw=['constraint propagation', 'node consistency', 'domain consistency', 'arc consistency', 'constraint network', 'support'])

K.lesson('ac3', 'The AC-3 algorithm', f'''
{src('slide Set 4, slide 7.')}
{algo('AC-3', [
    'function AC-3(csp):',
    '    queue = all arcs (X, Y) of the csp',
    '    while queue is not empty:',
    '        (X, Y) = remove the first arc',
    '        if REVISE(X, Y):',
    '            if dom(X) is empty: return false          # no solution',
    '            for each neighbour Z of X except Y: add (Z, X) to queue',
    '    return true',
    '',
    'function REVISE(X, Y):',
    '    revised = false',
    '    for each x in dom(X):',
    '        if no y in dom(Y) satisfies the constraint with x:',
    '            delete x from dom(X); revised = true',
    '    return revised'])}
{steps('AC-3 on the slide network A &lt; B &lt; C with domains {1, 2, 3}', [
    'Arc (A, B): A = 3 has no larger B. Remove 3 from A. dom(A) = {1, 2}.',
    'Arc (B, A): B = 1 has no smaller A. Remove 1 from B. dom(B) = {2, 3}.',
    'Arc (B, C): B = 3 has no larger C. Remove 3. dom(B) = {2}. Add (A, B) to the queue again.',
    'Arc (C, B): C must be larger than 2, so C = 3. dom(C) = {3}.',
    'Arc (A, B) again: A must be less than 2, so A = 1.',
    eq('A = 1, B = 2, C = 3: every domain has one value, the unique solution, found with no search')])}
{viz('ac3', pre='abc')}
{code('ac3')}
{fxs(fx('Cost of AC-3', 'O(c d³)', 'c binary constraints, domains of size at most d. Each arc can be added to the queue at most d times (once per value deleted from its head), and REVISE costs d² checks.', key=True))}
''', kw=['AC-3', 'REVISE', 'queue of arcs', 'unique solution', 'A less than B less than C'])

K.lesson('fcvsac', 'Forward checking against arc consistency', f'''
{src('slide Set 4, slide 7.')}
{versus('Two kinds of inference', ['', 'Forward checking', 'Arc consistency (AC-3)'], [
    ['What it checks', 'Only arcs from the variable just assigned to its unassigned neighbours', 'Every arc in the network, again and again until nothing changes'],
    ['Strength', 'Weaker', 'Stronger: it also catches conflicts between two unassigned variables'],
    ['Cost per step', 'Cheap: O(d) per neighbour', 'Heavier: up to O(c d³)'],
    ['Australia, after WA = red and Q = green', 'NT = {blue}, SA = {blue}, and no failure is seen yet', 'Checks NT against SA, finds both must be blue, empties a domain: failure detected at once']],
    'forward checking is cheap and often enough. Running AC-3 after each choice (MAC, chapter 5.2) prunes more and is the usual choice for hard problems.')}
{viz('ac3', pre='aus')}
<h3>Stronger consistency</h3>
{table(['Level', 'Meaning'], [
    ['Node (1 consistency)', 'Each value meets its unary constraints'],
    ['Arc (2 consistency)', 'Each value of a variable has a partner in every neighbour'],
    ['Path (3 consistency)', 'Each consistent pair (x, y) can be extended to any third variable z'],
    ['k consistency', 'Any consistent assignment to k − 1 variables extends to any k-th variable'],
    ['Strong n consistency', 'k consistent for every k ≤ n: then a solution can be found with no backtracking, but reaching it costs exponential time in general']])}
{note('Arc consistency cannot see that 2 colours are not enough for a triangle WA, NT, SA: each arc on its own is fine ({red, blue} against {red, blue}). Path consistency catches it.', 'warn')}
''', kw=['forward checking', 'arc consistency', 'MAC', 'path consistency', 'k consistency'])

K.lesson('maths', 'The maths: counting assignments and solutions', f'''
{fxs(
    fx('Number of complete assignments', 'd<sup>n</sup>', 'n variables, domain size d. Australia: 3<sup>7</sup> = 2,187.', key=True),
    fx('Naive search tree', 'n! · d<sup>n</sup> leaves', 'If any unassigned variable can be chosen at each level: n d choices at the top, (n − 1) d next, and so on. Fixing the variable order (assignments commute) brings it back to d<sup>n</sup>.', key=True),
    fx('Solutions of the Australia map', '3 × 2 × 3 = 18', 'Pick SA (3 ways). WA, NT, Q, NSW, V form a chain around SA and must alternate the other two colours (2 ways). T is free (3 ways).'))}
{steps('Worked example: why fixing the order matters', [
    'Australia has n = 7 and d = 3.',
    'Naive tree: 7! × 3⁷ = 5,040 × 2,187 = 11,022,480 leaves.',
    'With a fixed order: 3⁷ = 2,187 leaves.',
    eq('assignments commute (WA = red then NT = green is the same as the reverse), so a CSP search needs only d<sup>n</sup>')])}
{steps('Worked example: Boolean N queens', [
    '4 queens with X<sub>ij</sub>: 16 Boolean variables.',
    'Complete assignments: 2¹⁶ = 65,536.',
    'With one variable per column (domain size 4): 4⁴ = 256.',
    eq('a good formulation shrinks the space 256 times')])}
''', kw=['d to the n', 'n factorial', 'commutativity', '18 solutions'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A CSP is like a seating plan: everyone needs a seat (a value), and some people cannot sit next to each other (constraints). You fill seats one by one and cross out seats that would break a rule.</p>',
    '<p>A CSP is (X, D, C). Constraints can be unary, binary, global or soft. Node consistency fixes unary constraints, arc consistency makes every value have a partner. AC-3 runs in O(c d³) and ends with an empty domain (no solution), single values (unique solution) or a need to search.</p>',
    '<p>Any finite CSP can be turned into a binary CSP using auxiliary variables (dual graph). Global constraints have special propagators, for example Alldiff with matching gives stronger pruning than pairwise ≠. Strong k consistency removes the need to backtrack but costs exponential time in k.</p>',
    '<p>Modern solvers mix constraint propagation with SAT style clause learning (lazy clause generation), and constraint programming is used for industrial scheduling, rostering and chip verification. Research studies tractable classes by the structure of the constraint graph (tree width) and by the type of constraints (CSP dichotomy theorem, proved in 2017).</p>')}
{scene('university exam timetabling', '<p>Each exam is a variable, its domain is the set of time slots, and two exams that share a student must not be in the same slot (a binary ≠ constraint, like map colouring). Room capacity gives global constraints, and "no student has two exams in one day" gives more. Universities solve this every term with constraint solvers that combine propagation and search.</p>')}
''', kw=['seating plan', 'dual graph', 'Alldiff propagator', 'lazy clause generation', 'tree width', 'timetabling'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>CSP</b> is variables X, domains D and constraints C. A solution assigns every variable with no constraint broken. Only the final assignment matters.',
    'Examples: Australia map colouring (3<sup>7</sup> = 2,187 assignments, 18 solutions), N queens (Boolean X<sub>ij</sub> or one variable per column), and car assembly scheduling with precedence and disjunctive constraints.',
    'Constraints are unary, binary, global (Alldiff) or soft (preferences).',
    '<b>Arc consistency</b>: every value of X has a partner in Y. <b>AC-3</b> repeats REVISE until no arc changes, in O(c d³).',
    'Outcomes: an empty domain means no solution, single values give the unique solution, otherwise search is needed. A &lt; B &lt; C with {1, 2, 3} gives A = 1, B = 2, C = 3.',
    'Forward checking only looks at the arcs from the variable just assigned. Arc consistency looks at all arcs and finds failures earlier.'],
    'chapter 5.2 searches for solutions with backtracking and the MRV, degree and LCV heuristics.')}
{nbcard('csp-basics', 'Check map colourings, run AC-3 on the slide network, then write REVISE and AC-3 yourself and count the solutions of a small map.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A CSP is defined by', ['States and actions', 'Variables, domains and constraints', 'A heuristic and a cost', 'A population'], 1,
       'Three parts.', 'X, D and C.')
K.quiz('e', 'In Australia map colouring, how many colours does each domain have?', ['2', '3', '4', '7'], 1,
       'Red, green, blue.', 'D<sub>i</sub> = {red, green, blue}.')
K.quiz('e', 'Which region has no constraints with the others?', ['SA', 'NSW', 'T', 'WA'], 2,
       'An island.', 'Tasmania has no neighbours on the mainland, so any colour works.')
K.quiz('e', 'B ≠ 3 is a', ['Unary constraint', 'Binary constraint', 'Global constraint', 'Preference'], 0,
       'One variable.', 'It involves only B.')
K.quiz('m', 'An arc (X, Y) is arc consistent if', ['X and Y have equal domains', 'Every value of X has some value of Y that satisfies the constraint', 'Y has one value', 'X is assigned'], 1,
       'Support.', '∀ x ∃ y: r(x, y).')
K.quiz('m', 'After AC-3, every domain has exactly one value. This means', ['No solution', 'The unique solution is found', 'Search is still needed', 'AC-3 failed'], 1,
       'Slide 6.', 'Single values mean the unique solution.')
K.quiz('m', 'AC-3 on A &lt; B &lt; C with domains {1, 2, 3} gives', ['A = 1, B = 2, C = 3', 'A = 3, B = 2, C = 1', 'No solution', 'A = 1, B = 3, C = 2'], 0,
       'Only one way.', 'Each value is forced.')
K.quiz('m', 'In car assembly scheduling, "the two axles cannot be fitted at the same time" is a', ['Unary constraint', 'Precedence constraint', 'Disjunctive constraint', 'Soft constraint'], 2,
       'Either one first.', 'Axle<sub>F</sub> + 10 ≤ Axle<sub>B</sub> or Axle<sub>B</sub> + 10 ≤ Axle<sub>F</sub>.')
K.quiz('h', 'What is the cost of AC-3 with c constraints and domain size d?', ['O(c d)', 'O(c d²)', 'O(c d³)', 'O(d<sup>c</sup>)'], 2,
       'd re-adds times d² checks.', 'Each arc can return to the queue d times, and REVISE costs d².')
K.quiz('h', 'Why can AC-3 not prove that a triangle cannot be coloured with 2 colours?', ['It has a bug', 'Each single arc is consistent, the problem is only visible with three variables at once', 'Triangles have no arcs', 'It needs unary constraints'], 1,
       'Pairs look fine.', '{red, blue} against {red, blue} is consistent for each pair. Path consistency is needed.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: WA = red and Q = green are assigned. Which does forward checking miss that arc consistency catches?', ['NT has no colour', 'NT and SA are both forced to blue, but they are neighbours', 'V must be red', 'T must be green'], 1,
       'Two unassigned neighbours.', 'Forward checking only looks at arcs from WA and Q. AC-3 checks NT against SA and empties a domain.')
K.quiz('x', 'In the style of an Oxford exam: a naive CSP search lets any unassigned variable be chosen at each level. How many leaves does its tree have for n variables with domain size d?', ['d<sup>n</sup>', 'n! d<sup>n</sup>', 'n d', 'd!'], 1,
       'Choices per level.', 'n d at level 1, (n − 1) d at level 2, ..., giving n! d<sup>n</sup>. Commutativity cuts it to d<sup>n</sup>.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Complete assignments for Australia: 7 regions, 3 colours.', '2187', '3⁷.',
       ['3³ = 27.', '3⁶ = 729.', eq('3⁷ = 2,187')], check=3 ** 7)
K.calc('e', 'How many binary constraints does the Australia map have?', '9', 'Count neighbouring pairs.',
       ['WA-NT, WA-SA, NT-SA, NT-Q.', 'SA-Q, SA-NSW, SA-V, Q-NSW, NSW-V.', eq('4 + 5 = 9')], check=9)
K.calc('e', 'Arcs for AC-3 on the Australia map (each constraint gives 2).', '18', '2 × 9.',
       ['9 constraints.', 'Two directions each.', eq('18 arcs')], check=18)
K.calc('m', 'Number of solutions of the Australia map with 3 colours.', '18', 'SA, then the chain, then T.',
       ['SA: 3 choices.', 'The chain WA, NT, Q, NSW, V alternates the 2 other colours: 2 ways.', eq('3 × 2 × 3 (T) = 18')], check=18)
K.calc('m', 'Boolean formulation of 4 queens: how many complete assignments?', '65536', '16 variables, 2 values.',
       ['4 × 4 = 16 variables.', '2¹⁶.', eq('65,536')], check=2 ** 16)
K.calc('m', 'One variable per column for 4 queens: complete assignments?', '256', '4⁴.',
       ['4 variables.', '4 values each.', eq('256')], check=256)
K.calc('m', 'AC-3 bound c d³ for Australia: c = 9, d = 3.', '243', '9 × 27.',
       ['d³ = 27.', '9 × 27.', eq('243 checks at most')], check=243)
K.calc('h', 'Leaves of the naive tree for Australia: 7! × 3⁷.', '11022480', '5040 × 2187.',
       ['7! = 5,040.', '5,040 × 2,187.', eq('11,022,480')], check=5040 * 2187)
K.calc('h', 'Car assembly with domains {1, ..., 27} and 15 variables. How many complete assignments, as a power of 27? Give the exponent.', '15', '27<sup>15</sup>.',
       ['Each of the 15 tasks takes one of 27 start times.', 'd<sup>n</sup> = 27<sup>15</sup>.', eq('exponent 15, about 2.9 × 10²¹ assignments')], check=15)
K.calc('x', 'In the style of a CMU 15-381 problem: with A &lt; B, B &lt; C, C &lt; D and every domain {1, ..., 5}, how many values are left in dom(B) after AC-3?', '2', 'B needs one smaller and two larger values.',
       ['A ≥ 1 means B ≥ 2.', 'C ≤ 4 and D ≤ 5 mean B ≤ 3.', eq('dom(B) = {2, 3}, 2 values')], check=2)

# ---------------------------------------------------------------- assignments
K.assign('revise', 'm', 'REVISE and AC-3',
         '<p>Write <code>ac3(domains, less)</code>. domains is a dict of lists. less is a list of [X, Y] pairs meaning X &lt; Y. Run AC-3 and return the new domains as a dict of sorted lists, or None if a domain becomes empty.</p>',
         '''
def ac3(domains, less):
    # your code here
    pass
''', [("ac3({'A': [1, 2, 3], 'B': [1, 2, 3], 'C': [1, 2, 3]}, [['A', 'B'], ['B', 'C']])", {'A': [1], 'B': [2], 'C': [3]}),
      ("ac3({'A': [1, 2, 3, 4, 5], 'B': [1, 2, 3, 4, 5], 'C': [1, 2, 3, 4, 5], 'D': [1, 2, 3, 4, 5]}, [['A', 'B'], ['B', 'C'], ['C', 'D']])", {'A': [1, 2], 'B': [2, 3], 'C': [3, 4], 'D': [4, 5]}),
      ("ac3({'A': [1, 2], 'B': [1, 2], 'C': [1, 2]}, [['A', 'B'], ['B', 'C']])", None),
      ("ac3({'X': [3], 'Y': [1, 5]}, [['X', 'Y']])", {'X': [3], 'Y': [5]})],
         '''
def ac3(domains, less):
    dom = {}
    for v in domains:
        dom[v] = list(domains[v])
    arcs = []
    for x, y in less:
        arcs.append([x, y, "lt"])
        arcs.append([y, x, "gt"])
    queue = list(arcs)
    while len(queue) > 0:
        x, y, kind = queue.pop(0)
        removed = False
        for vx in dom[x][:]:
            support = False
            for vy in dom[y]:
                if (kind == "lt" and vx < vy) or (kind == "gt" and vx > vy):
                    support = True
            if not support:
                dom[x].remove(vx)
                removed = True
        if removed:
            if len(dom[x]) == 0:
                return None
            for arc in arcs:
                if arc[1] == x and arc[0] != y and arc not in queue:
                    queue.append(arc)
    for v in dom:
        dom[v].sort()
    return dom
''', 'Make two arcs per constraint, one "less than" and one "greater than". After a removal from X, put back every arc (Z, X).', '<p>The third test has 3 variables in a chain but only 2 values, so a domain empties.</p>')
K.assign('count', 'e', 'Count the colourings of a map',
         '<p>Write <code>count_colourings(regions, borders, k)</code> that returns how many ways the regions can be coloured with k colours so that no two bordering regions share a colour. Try every complete assignment.</p>',
         '''
def count_colourings(regions, borders, k):
    # your code here
    pass
''', [("count_colourings(['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T'], [['WA', 'NT'], ['WA', 'SA'], ['NT', 'SA'], ['NT', 'Q'], ['SA', 'Q'], ['SA', 'NSW'], ['SA', 'V'], ['Q', 'NSW'], ['NSW', 'V']], 3)", 18),
      ("count_colourings(['A', 'B', 'C'], [['A', 'B'], ['B', 'C'], ['A', 'C']], 2)", 0),
      ("count_colourings(['A', 'B'], [['A', 'B']], 3)", 6)],
         '''
def count_colourings(regions, borders, k):
    n = len(regions)
    count = 0
    for code in range(k ** n):
        colour = {}
        rest = code
        for r in regions:
            colour[r] = rest % k
            rest = rest // k
        good = True
        for a, b in borders:
            if colour[a] == colour[b]:
                good = False
        if good:
            count = count + 1
    return count
''', 'Turn each number from 0 to k<sup>n</sup> − 1 into a colouring by writing it in base k.', '<p>This brute force tries all 2,187 colourings of Australia. Chapter 5.2 does the same job far faster with backtracking.</p>')

K.must('CSP', 'Variables X, domains D, constraints C. Solution: complete and consistent assignment.')
K.must('Examples', 'Australia: 3<sup>7</sup> = 2,187 assignments, 18 solutions. N queens with X<sub>ij</sub> ∈ {0, 1}. Car assembly with precedence T1 + d1 ≤ T2 and disjunctive constraints.')
K.must('Arc consistency', '∀ x ∈ dom(X) ∃ y ∈ dom(Y): r(x, y). AC-3 costs O(c d³).')
K.must('Three outcomes', 'Empty domain: no solution. All singletons: unique solution. Otherwise search.')
K.must('Forward checking against AC-3', 'FC checks arcs from the newly assigned variable only. AC-3 checks every arc and finds failures earlier.')

T = K.topic(
    slug='csp-basics', topic='csp-basics', step=(5, 'Constraint satisfaction', 'cai-csp', 'Problems made of variables, domains and constraints: arc consistency, backtracking with smart ordering, and local search.', 'College'),
    title='Constraint satisfaction problems and arc consistency', short='CSPs and AC-3', badge='5.1', minutes=50,
    lead='Some problems are best written as variables that need values under rules. Learn to formulate map colouring, N queens and job scheduling as CSPs, and to shrink domains with node and arc consistency and the AC-3 algorithm.',
    desc='Variables, domains and constraints, the Australia map, N queens with Boolean variables, car assembly scheduling, types of constraints, node and arc consistency, AC-3 with the slide example, its O(cd³) cost, forward checking against arc consistency and higher consistency.',
    summary='CSP formulation, constraint types, node and arc consistency, AC-3 and its three outcomes.',
    keywords=['constraint satisfaction', 'CSP', 'AC-3', 'arc consistency', 'map colouring', 'job scheduling', 'N queens'],
    recap='<p>Write the problem as variables, domains and constraints, then let arc consistency remove values that cannot work.</p>',
    nb={'check': 'Checking a map colouring', 'ac3': 'AC-3 on the slide network A < B < C'})
