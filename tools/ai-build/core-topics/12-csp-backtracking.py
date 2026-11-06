# Chapter 5.2: backtracking search for CSPs. Source: slide Set 4, slides 5 to 7 (backtracking, minimum remaining
# values, the degree heuristic with SA first, least constraining value with WA = red and NT = green, forward
# checking and constraint propagation, MAC) and the class of 8 February 2026. Commutativity, backjumping,
# conflict directed backjumping and no good learning follow Russell and Norvig, AIMA 4th ed., section 6.3.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('plain', r'''
# Plain backtracking on the map of Australia, fixed order and fixed colour order.
order = ["WA", "NT", "NSW", "Q", "SA", "V", "T"]
neighbours = {"WA": ["NT", "SA"], "NT": ["WA", "SA", "Q"], "SA": ["WA", "NT", "Q", "NSW", "V"],
              "Q": ["NT", "SA", "NSW"], "NSW": ["Q", "SA", "V"], "V": ["SA", "NSW"], "T": []}
colours = ["red", "green", "blue"]
tries = 0

def backtrack(assignment):
    global tries
    if len(assignment) == len(order):
        return assignment
    var = order[len(assignment)]               # next variable in the fixed order
    for c in colours:
        tries = tries + 1
        clash = False
        for n in neighbours[var]:
            if assignment.get(n) == c:
                clash = True
        if not clash:
            assignment[var] = c
            result = backtrack(assignment)
            if result is not None:
                return result
            del assignment[var]                # undo and try the next colour
            print("backtrack: undo", var, "=", c)
    return None

print(backtrack({}))
print("colours tried:", tries)
''')

K.code('mrvfc', r'''
# Backtracking with MRV (fewest values left) and forward checking on the same map.
neighbours = {"WA": ["NT", "SA"], "NT": ["WA", "SA", "Q"], "SA": ["WA", "NT", "Q", "NSW", "V"],
              "Q": ["NT", "SA", "NSW"], "NSW": ["Q", "SA", "V"], "V": ["SA", "NSW"], "T": []}

def solve(assignment, domains):
    if len(assignment) == len(neighbours):
        return assignment
    # MRV: the unassigned variable with the fewest values left (ties: most neighbours)
    best = None
    for v in neighbours:
        if v not in assignment:
            if best is None or len(domains[v]) < len(domains[best]) or \
               (len(domains[v]) == len(domains[best]) and len(neighbours[v]) > len(neighbours[best])):
                best = v
    for c in domains[best]:
        new_domains = {}
        for v in domains:
            new_domains[v] = list(domains[v])
        new_domains[best] = [c]
        dead = False
        for n in neighbours[best]:              # forward checking
            if n not in assignment and c in new_domains[n]:
                new_domains[n].remove(c)
                if len(new_domains[n]) == 0:
                    dead = True
        print("choose", best, "=", c, " dead end" if dead else "")
        if not dead:
            assignment[best] = c
            result = solve(assignment, new_domains)
            if result is not None:
                return result
            del assignment[best]
    return None

start = {}
for v in neighbours:
    start[v] = ["red", "green", "blue"]
print(solve({}, start))
''')

K.lesson('idea', 'Backtracking search', f'''
{src('slide Set 4, slide 5, and the class of 8 February 2026.')}
{wwh('Backtracking search is depth first search that assigns one variable at a time and goes back as soon as a constraint is broken.',
     'Arc consistency alone often leaves several values per variable. Plain search over complete assignments tries all d<sup>n</sup> of them. Backtracking checks constraints after each single choice, so a bad partial assignment is abandoned at once, together with every completion of it.',
     'Pick an unassigned variable, try each value in its domain, and keep a value only if it fits with the values already chosen. Recurse. If no value works, undo the last choice and try that variable\'s next value.')}
{algo('BACKTRACKING-SEARCH (AIMA figure 6.5)', [
    'function BACKTRACK(assignment, csp):',
    '    if assignment is complete: return assignment',
    '    var = SELECT-UNASSIGNED-VARIABLE(csp, assignment)        # MRV, degree',
    '    for each value in ORDER-DOMAIN-VALUES(var, assignment):  # LCV',
    '        if value is consistent with assignment:',
    '            add {var = value} to assignment',
    '            inferences = INFERENCE(csp, var, value)          # forward checking or MAC',
    '            if inferences is not failure:',
    '                add inferences to csp',
    '                result = BACKTRACK(assignment, csp)',
    '                if result is not failure: return result',
    '                remove inferences from csp',
    '            remove {var = value} from assignment',
    '    return failure'])}
<p>Backtracking only needs to consider one variable per level, because assignments <b>commute</b>: WA = red then NT = green is the same as NT = green then WA = red. That shrinks the tree from n! d<sup>n</sup> to d<sup>n</sup> leaves.</p>
{viz('mapcolor', vo='fixed', val='fixed', inf='none', k=3)}
{code('plain')}
<p>In the fixed order WA, NT, NSW, Q, SA, V, T, the choices WA = red, NT = green, NSW = red force Q = blue, and then SA has no colour left. Backtracking undoes Q and then NSW, tries NSW = green, and succeeds.</p>
''', kw=['backtracking search', 'depth first', 'commutativity', 'undo', 'Australia'])

K.lesson('ordering', 'Which variable next, which value first', f'''
{src('slide Set 4, slide 5.')}
{table(['Heuristic', 'Rule', 'Why it helps', 'Slide example'], [
    ['Minimum remaining values (MRV), also "most constrained variable" or "fail first"', 'Choose the variable with the fewest legal values left', 'If some variable has no values left, MRV picks it and the failure is found at once, before wasting time on others', 'After WA and NT are coloured, SA has only one colour left, so colour SA next'],
    ['Degree heuristic', 'Choose the variable involved in the most constraints on other unassigned variables', 'Lowers the branching factor of future choices. Used to break ties of MRV, and at the very start when all domains are equal', 'Choose SA first: it has degree 5'],
    ['Least constraining value (LCV)', 'Try first the value that rules out the fewest choices for neighbouring variables', 'Leaves the most room for the rest, so a solution is found sooner', 'After WA = red and NT = green, Q = blue would remove SA\'s last value, so LCV prefers Q = red']])}
{note('Variable ordering is fail first: pick the hardest variable so a dead end shows up early. Value ordering is succeed first: pick the value most likely to work. When you want all solutions, or none exists, value ordering does not matter, because every value gets tried anyway.', 'exam')}
{viz('mapcolor', vo='deg', val='lcv', inf='fc', k=3)}
<p>With MRV, degree tie breaking, LCV and forward checking, SA is chosen first and the map is coloured with no backtracking at all.</p>
''', kw=['MRV', 'minimum remaining values', 'most constrained variable', 'fail first', 'degree heuristic', 'least constraining value', 'LCV'])

K.lesson('inference', 'Forward checking and maintaining arc consistency', f'''
{wwh('Inference during search removes values from the domains of unassigned variables right after each choice.',
     'Without inference, backtracking only notices a problem when it reaches the stuck variable, possibly many levels later. Inference notices it immediately, when a domain becomes empty.',
     '<b>Forward checking</b>: after X = x, remove x (or any value in conflict with it) from the domain of each unassigned neighbour of X. <b>MAC</b> (maintaining arc consistency): after X = x, run AC-3 starting with the arcs (Y, X) for the unassigned neighbours Y, so the removals spread through the whole network.')}
{steps('Forward checking on Australia (fixed order)', [
    'WA = red. Remove red from NT and SA.',
    'NT = green. Remove green from SA and Q. SA = {blue}.',
    'NSW = red. Remove red from Q and V. Q = {blue}.',
    'Q = blue. Remove blue from SA. SA = { } is empty, so this branch fails at once, without trying SA.',
    eq('forward checking spots the dead end one level earlier than plain backtracking')])}
{viz('mapcolor', vo='fixed', val='fixed', inf='fc', k=3)}
{code('mrvfc')}
{note('Forward checking misses conflicts between two unassigned variables. After WA = red and Q = green, NT and SA both have only blue left and are neighbours. Forward checking does not see it. MAC does, because it also checks the arc NT, SA.', 'warn')}
''', kw=['forward checking', 'MAC', 'maintaining arc consistency', 'inference', 'empty domain'])

K.lesson('smarter', 'Smarter backtracking: backjumping and learning', f'''
<p>Plain backtracking goes back to the most recent variable (<b>chronological backtracking</b>), even if that variable had nothing to do with the failure.</p>
{steps('Example: why chronological backtracking wastes time', [
    'Fixed order Q, NSW, V, T, SA, WA, NT. Assign Q = red, NSW = green, V = blue, T = red.',
    'SA neighbours Q, NSW and V, which use all three colours, so SA has no value.',
    'Chronological backtracking goes back to T and tries T = green, then T = blue. Neither helps: T is not connected to SA.',
    eq('backjumping goes straight back to V, the most recent variable in SA\'s conflict set {Q, NSW, V}')])}
{table(['Method', 'Idea'], [
    ['Backjumping', 'Jump back to the most recent variable in the conflict set of the failed variable (the assigned variables that removed its values)'],
    ['Conflict directed backjumping', 'When jumping back from X to Y, add X\'s conflict set (minus Y) to Y\'s, so the next jump from Y can also skip unrelated variables'],
    ['Constraint learning (no goods)', 'Record the smallest set of assignments that caused the failure, for example {Q = red, NSW = green, V = blue}, and never try that combination again'],
    ['Symmetry breaking', 'In map colouring, any solution with colours permuted is also a solution. Fix WA = red at the start to cut the work by 3! = 6']])}
{note('Forward checking already finds every conflict that simple backjumping would jump over, so backjumping adds little to forward checking. Conflict directed backjumping and learning do add power, and they are the core of modern SAT solvers.', 'tip')}
''', kw=['chronological backtracking', 'backjumping', 'conflict set', 'conflict directed backjumping', 'no good', 'constraint learning', 'symmetry breaking'])

K.lesson('maths', 'The maths: branching and pruning', f'''
{fxs(
    fx('Worst case of backtracking', 'O(d<sup>n</sup>)', 'Every partial assignment may be extended until the last variable. General CSPs are NP complete (3 colouring is), so no method avoids this in the worst case.', key=True),
    fx('Forward checking cost per assignment', 'O(e d) at most, e = number of neighbours', 'Each neighbour loses at most the conflicting values.'),
    fx('Symmetry', 'k colours ⇒ k! equivalent solutions', 'Fixing the first colour divides the search by k, fixing an ordering of all colours by k!.'))}
{steps('Worked example: nodes visited in the fixed order', [
    'Plain backtracking on Australia in the fixed order tries 17 colours in total (the code prints this count).',
    'With MRV, degree, LCV and forward checking, 7 choices are made and none is undone.',
    'The full space has 3⁷ = 2,187 complete assignments.',
    eq('good ordering and inference turn search into almost straight line decisions')])}
{steps('Worked example: LCV counts', [
    'After WA = red and NT = green, Q can be red or blue.',
    'Q = red removes red from NSW (and SA has no red). Remaining values for SA and NSW: SA {blue}, NSW {green, blue}: total 3.',
    'Q = blue removes blue from SA and NSW. Remaining: SA { }, NSW {red, green}: total 2, and SA is empty.',
    eq('LCV prefers Q = red, which leaves more choices')])}
''', kw=['NP complete', 'worst case', 'symmetry', 'LCV count'])

K.lesson('compare', 'Comparing CSP search strategies', f'''
{versus('Backtracking with different helpers on Australia, 3 colours', ['Method', 'Order', 'Inference', 'Backtracks'], [
    ['Plain backtracking', 'Fixed WA, NT, NSW, Q, SA, V, T', 'None', '2'],
    ['With forward checking', 'Fixed', 'Forward checking', '2, but each dead end is found one level earlier'],
    ['MRV with degree and LCV', 'SA first', 'Forward checking', '0'],
    ['2 colours with MAC', 'SA first', 'MAC', 'Proves no solution after trying both colours for SA']],
    'the variable order matters most. MRV with degree tie breaking plus forward checking is a strong default, and MAC pays off on hard or impossible problems.')}
{versus('Backtracking for CSPs against plain search', ['', 'Search over states (chapter 2)', 'CSP backtracking'], [
    ['State', 'Black box', 'Partial assignment with visible structure'],
    ['Pruning', 'Only by the goal test or h', 'Constraints prune at every step, inference removes values ahead'],
    ['Heuristics', 'Problem specific h', 'General ones that work for any CSP: MRV, degree, LCV']],
    'the structure of a CSP gives general purpose heuristics for free. That is the big win of formulating a problem as a CSP.')}
{scene('Sudoku', '<p>A Sudoku is a CSP with 81 variables, domains {1, ..., 9}, and 27 Alldiff constraints (rows, columns, boxes). Newspaper puzzles are usually solved by arc consistency alone. Harder ones need search, and MRV picks the cell with the fewest candidates first, which is exactly what a human expert does when they look for a cell with only one or two possible digits.</p>')}
''', kw=['comparison', 'Sudoku', 'general heuristics'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>To colour a map, start with the hardest region (the one touching the most others), pick the colour that blocks the fewest neighbours, and cross out colours as you go. If you get stuck, rub out the last choice and try again.</p>',
    '<p>Backtracking assigns one variable per level. MRV and degree choose the variable, LCV the value. Forward checking and MAC remove values ahead and catch dead ends early. Backjumping and learning avoid repeating the same mistake.</p>',
    '<p>CSPs are NP complete in general, so the worst case stays exponential, but heuristics change the average case enormously. Conflict directed backjumping and no good learning give the same kind of power as clause learning in SAT solvers. Random restarts with heavy tailed run times make solvers far more robust.</p>',
    '<p>State of the art constraint solvers (for example Google OR-Tools CP-SAT) combine propagation, clause learning, restarts and linear relaxations. Research studies phase transitions in random CSPs (hard instances sit at a critical ratio of constraints to variables) and learned branching heuristics.</p>')}
''', kw=['NP complete', 'SAT solver', 'CP-SAT', 'phase transition', 'heavy tailed'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Backtracking</b> is DFS that assigns one variable at a time and undoes a choice as soon as a constraint breaks. Commutativity means one variable per level, d<sup>n</sup> leaves.',
    '<b>MRV</b> (fail first): fewest legal values. <b>Degree</b>: most constraints on unassigned variables (SA first). <b>LCV</b>: the value that rules out the fewest neighbour values (Q = red, not blue).',
    '<b>Forward checking</b> removes conflicting values from neighbours after each choice. <b>MAC</b> runs AC-3 and also catches conflicts between unassigned variables.',
    'Australia in the fixed order needs 2 backtracks. MRV with degree, LCV and forward checking needs 0.',
    '<b>Backjumping</b>, conflict directed backjumping and <b>no good learning</b> avoid going back to variables that did not cause the failure.'],
    'chapter 5.3 solves CSPs with local search (min-conflicts) and by using the shape of the constraint graph.')}
{nbcard('csp-backtracking', 'Run plain backtracking and MRV with forward checking on Australia, then write backtracking and the MRV choice yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Backtracking search for CSPs is a kind of', ['Breadth first search', 'Depth first search', 'Greedy search', 'Local search'], 1,
       'Goes deep, undoes.', 'It assigns deeper and deeper and backs up when stuck.')
K.quiz('e', 'MRV chooses the variable with', ['The most values left', 'The fewest legal values left', 'The longest name', 'The most neighbours only'], 1,
       'Fail first.', 'If a variable has no values left, MRV finds it immediately.')
K.quiz('e', 'Which region does the degree heuristic choose first in Australia?', ['WA', 'T', 'SA', 'V'], 2,
       'Degree 5.', 'SA borders five other regions.')
K.quiz('e', 'LCV orders', ['Variables', 'Values', 'Constraints', 'Colours by name'], 1,
       'Least constraining value.', 'It tries first the value that rules out the fewest options for neighbours.')
K.quiz('m', 'After WA = red and NT = green, LCV prefers Q =', ['blue', 'red', 'green', 'any'], 1,
       'Slide 5.', 'Q = blue would remove SA\'s last value.')
K.quiz('m', 'Forward checking, after assigning X, removes values from', ['All variables', 'Unassigned neighbours of X', 'X only', 'Assigned variables'], 1,
       'One step ahead.', 'It only looks at arcs from X to its unassigned neighbours.')
K.quiz('m', 'Why does backtracking pick only one variable per level?', ['To save memory', 'Assignments commute, so the order of the same assignments does not matter', 'Because of MRV', 'It is a rule of DFS'], 1,
       'WA then NT = NT then WA.', 'This cuts the tree from n! d<sup>n</sup> to d<sup>n</sup>.')
K.quiz('m', 'MAC differs from forward checking because it', ['Uses no constraints', 'Runs AC-3 after each choice, spreading removals', 'Picks values randomly', 'Only works on trees'], 1,
       'Maintaining arc consistency.', 'It also catches conflicts between unassigned variables.')
K.quiz('h', 'Backjumping goes back to', ['The start', 'The most recent variable in the conflict set of the failed variable', 'A random variable', 'The variable with the most values'], 1,
       'Who caused the failure?', 'It skips variables that did not remove any value of the failed variable.')
K.quiz('h', 'When looking for ALL solutions, value ordering', ['Matters a lot', 'Does not matter, every value is tried', 'Must be LCV', 'Must be random'], 1,
       'Everything gets tried.', 'Value ordering only helps to find the first solution sooner.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: order Q, NSW, V, T, SA with Q = red, NSW = green, V = blue, T = red. SA fails. Where does conflict directed backjumping go?', ['T', 'V', 'Q', 'The start'], 1,
       'SA\'s conflict set.', 'The conflict set of SA is {Q, NSW, V}. The most recent of them is V. T is skipped.')
K.quiz('x', 'In the style of an IIT Bombay exam: which statement is true for 3 colouring of general graphs?', ['It is solvable in polynomial time with MRV', 'It is NP complete, so backtracking can need exponential time in the worst case', 'AC-3 always solves it', 'It never needs backtracking'], 1,
       'A classic hard problem.', 'Heuristics help on average but cannot remove the exponential worst case unless P = NP.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'How many neighbours does SA have?', '5', 'WA, NT, Q, NSW, V.',
       ['WA, NT.', 'Q, NSW, V.', eq('5')], check=5)
K.calc('e', 'After WA = red and NT = green, how many colours are left for SA?', '1', 'SA touches both.',
       ['Red is gone (WA).', 'Green is gone (NT).', eq('only blue, 1 colour')], check=1)
K.calc('e', 'Complete assignments for 7 regions with 3 colours, which a fixed order backtracking tree has at most as leaves.', '2187', '3⁷.',
       ['d<sup>n</sup>.', '3⁷.', eq('2,187')], check=2187)
K.calc('m', 'Plain backtracking in the fixed order WA, NT, NSW, Q, SA, V, T: how many backtracks?', '2', 'Undo Q, then NSW.',
       ['Q = blue leaves SA with no colour: undo Q.', 'Q has no other colour: undo NSW = red.', eq('2 backtracks')], check=2)
K.calc('m', 'LCV: after WA = red and NT = green, how many values remain in SA and NSW together if Q = red?', '3', 'SA {blue}, NSW {green, blue}.',
       ['SA: blue only, 1.', 'NSW: red removed, green and blue left, 2.', eq('1 + 2 = 3')], check=3)
K.calc('m', 'Same, if Q = blue.', '2', 'SA { }, NSW {red, green}.',
       ['SA loses blue: 0.', 'NSW loses blue: 2.', eq('0 + 2 = 2')], check=2)
K.calc('m', 'Symmetry: with 3 colours, how many colour permutations map one solution to another?', '6', '3!.',
       ['Swap the colour names in any order.', '3 × 2 × 1.', eq('6')], check=6)
K.calc('h', 'Australia has 18 solutions. If we fix SA = red to break symmetry, how many remain?', '6', '18 ⁄ 3.',
       ['Each colour of SA is equally common.', '18 ⁄ 3.', eq('6')], check=6)
K.calc('h', 'Naive tree leaves n! d<sup>n</sup> for n = 4, d = 2, against d<sup>n</sup>. What is the ratio?', '24', 'n!.',
       ['n! d<sup>n</sup> = 24 × 16 = 384.', 'd<sup>n</sup> = 16.', eq('384 ⁄ 16 = 24 = 4!')], check=24)
K.calc('x', 'In the style of a CMU 15-381 problem: a Sudoku row has 9 cells. If 6 cells are filled with 1 to 6, how many values does each empty cell of that row have left after the row\'s Alldiff is enforced?', '3', '9 − 6.',
       ['Digits 1 to 6 are used in the row.', 'Each empty cell can only take 7, 8 or 9.', eq('3 values')], check=3)

# ---------------------------------------------------------------- assignments
NB = "{'WA': ['NT', 'SA'], 'NT': ['WA', 'SA', 'Q'], 'SA': ['WA', 'NT', 'Q', 'NSW', 'V'], 'Q': ['NT', 'SA', 'NSW'], 'NSW': ['Q', 'SA', 'V'], 'V': ['SA', 'NSW'], 'T': []}"
K.assign('bt', 'm', 'Backtracking map colouring',
         '<p>Write <code>colour_map(order, neighbours, colours)</code> that colours the variables in the given order, trying colours in the given order, and backtracks when stuck. Return the assignment as a dict, or None if there is none.</p>',
         '''
def colour_map(order, neighbours, colours):
    # your code here
    pass
''', [(f"colour_map(['WA', 'NT', 'NSW', 'Q', 'SA', 'V', 'T'], {NB}, ['red', 'green', 'blue'])", {'WA': 'red', 'NT': 'green', 'NSW': 'green', 'Q': 'red', 'SA': 'blue', 'V': 'red', 'T': 'red'}),
      (f"colour_map(['WA', 'NT', 'NSW', 'Q', 'SA', 'V', 'T'], {NB}, ['red', 'green'])", None),
      ("colour_map(['A', 'B'], {'A': ['B'], 'B': ['A']}, ['x', 'y'])", {'A': 'x', 'B': 'y'})],
         '''
def colour_map(order, neighbours, colours):
    assignment = {}

    def backtrack(i):
        if i == len(order):
            return True
        var = order[i]
        for c in colours:
            clash = False
            for n in neighbours[var]:
                if assignment.get(n) == c:
                    clash = True
            if not clash:
                assignment[var] = c
                if backtrack(i + 1):
                    return True
                del assignment[var]
        return False

    if backtrack(0):
        return assignment
    return None
''', 'Use a helper backtrack(i) that colours order[i] and calls backtrack(i + 1). Delete the colour when you undo.', '<p>The answer matches the animation: two backtracks, then NSW = green.</p>')
K.assign('mrv', 'e', 'Pick the next variable with MRV and degree',
         '<p>Write <code>pick(domains, assigned, neighbours)</code>. Among unassigned variables, return the one with the fewest values in domains. Break ties by the most unassigned neighbours, then by the order the variables appear in domains.</p>',
         '''
def pick(domains, assigned, neighbours):
    # your code here
    pass
''', [(f"pick({{'WA': ['r', 'g', 'b'], 'NT': ['r', 'g', 'b'], 'SA': ['r', 'g', 'b'], 'Q': ['r', 'g', 'b'], 'NSW': ['r', 'g', 'b'], 'V': ['r', 'g', 'b'], 'T': ['r', 'g', 'b']}}, [], {NB})", 'SA'),
      (f"pick({{'WA': ['r'], 'NT': ['g'], 'SA': ['b'], 'Q': ['r', 'b'], 'NSW': ['r', 'g', 'b'], 'V': ['r', 'g', 'b'], 'T': ['r', 'g', 'b']}}, ['WA', 'NT'], {NB})", 'SA'),
      (f"pick({{'WA': ['r'], 'NT': ['g'], 'SA': ['b'], 'Q': ['r'], 'NSW': ['g', 'b'], 'V': ['r', 'g'], 'T': ['r', 'g', 'b']}}, ['WA', 'NT', 'SA', 'Q'], {NB})", 'NSW')],
         '''
def pick(domains, assigned, neighbours):
    best = None
    best_size = None
    best_degree = None
    for v in domains:
        if v in assigned:
            continue
        size = len(domains[v])
        degree = 0
        for n in neighbours[v]:
            if n not in assigned:
                degree = degree + 1
        if best is None or size < best_size or (size == best_size and degree > best_degree):
            best = v
            best_size = size
            best_degree = degree
    return best
''', 'Keep the best so far, and replace it only if the new one has fewer values, or the same number and a higher degree.', '<p>At the start all domains are equal, so degree decides: SA. In the last test NSW and V both have 2 values, and NSW has the higher degree (V is its only unassigned neighbour, and T has 3 values).</p>')

K.must('Backtracking', 'DFS, one variable per level (assignments commute), undo on a broken constraint. d<sup>n</sup> leaves.')
K.must('MRV and degree', 'MRV: fewest legal values (fail first). Degree: most constraints on unassigned variables, breaks ties. SA first.')
K.must('LCV', 'Value ruling out fewest neighbour values first. WA = red, NT = green: Q = red, not blue.')
K.must('FC and MAC', 'FC prunes neighbours of the assigned variable. MAC runs AC-3 and catches more.')
K.must('Backjumping and learning', 'Jump to the latest variable in the conflict set. Record no goods so the same failure never repeats.')

T = K.topic(
    slug='csp-backtracking', topic='csp-backtracking', step=(5, 'Constraint satisfaction', 'cai-csp', 'Problems made of variables, domains and constraints: arc consistency, backtracking with smart ordering, and local search.', 'College'),
    title='Backtracking search for CSPs', short='CSP backtracking', badge='5.2', minutes=50,
    lead='Solve CSPs by assigning one variable at a time and going back as soon as a rule breaks. Choose the next variable with MRV and degree, the value with LCV, and prune ahead with forward checking and MAC.',
    desc='Backtracking search, commutativity, the MRV, degree and LCV heuristics with the slide examples, forward checking and MAC on Australia, backjumping, conflict directed backjumping and no good learning, symmetry breaking and a comparison of strategies.',
    summary='Backtracking, MRV, degree, LCV, forward checking, MAC, backjumping and learning.',
    keywords=['backtracking search', 'MRV', 'degree heuristic', 'LCV', 'forward checking', 'MAC', 'backjumping'],
    recap='<p>Assign one variable at a time, fail first with MRV, succeed first with LCV, and prune ahead with forward checking or MAC.</p>',
    nb={'plain': 'Plain backtracking on the map of Australia', 'mrvfc': 'Backtracking with MRV and forward checking'})
