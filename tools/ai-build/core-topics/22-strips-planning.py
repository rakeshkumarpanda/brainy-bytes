# Chapter 8.2: STRIPS planning, forward and backward state space search, planning heuristics and sub goals.
# The uploaded slides and transcripts do not cover planning, so this chapter follows Russell and Norvig, AIMA 3rd ed.
# chapter 10 and sections 11.1 to 11.2, Fikes and Nilsson (1971), Sussman (1973), Bonet and Geffner (2001) and
# Hoffmann and Nebel (2001). Every plan and count in it was checked by running the code of this chapter.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('bw', r'''
# Forward (progression) search in the blocks world. A state maps each block to what it sits on.
def moves(state):
    below = set(state.values())                 # blocks with something on top are not clear
    free = [b for b in sorted(state) if b not in below]
    out = []
    for b in free:
        if state[b] != "Table":
            out.append(("MoveToTable(" + b + ", " + state[b] + ")", b, "Table"))
        for y in free:
            if y != b:
                out.append(("Move(" + b + ", " + state[b] + ", " + y + ")", b, y))
    return out

start = {"A": "Table", "B": "Table", "C": "A"}      # the Sussman anomaly
queue = [(start, [])]
seen = [start]
while queue:
    state, plan = queue.pop(0)
    if state["A"] == "B" and state["B"] == "C":   # goal: On(A, B) and On(B, C)
        print("plan:", plan)
        print("states seen:", len(seen))
        break
    for name, b, to in moves(state):
        new = dict(state)
        new[b] = to
        if new not in seen:
            seen.append(new)
            queue.append((new, plan + [name]))
''')

K.code('regress', r'''
# Backward (regression) search, one step: which goal must hold before an action, so the goal holds after it?
def move(b, x, y):
    return {"name": "Move(" + b + ", " + x + ", " + y + ")",
            "pre": {"On(" + b + ", " + x + ")", "Clear(" + b + ")", "Clear(" + y + ")"},
            "add": {"On(" + b + ", " + y + ")"} | ({"Clear(" + x + ")"} if x != "Table" else set()),
            "del": {"On(" + b + ", " + x + ")", "Clear(" + y + ")"}}

def regress(goal, a):
    if not (a["add"] & goal):
        return None                     # not relevant: it achieves no part of the goal
    if a["del"] & goal:
        return None                     # not consistent: it would undo part of the goal
    return (goal - a["add"]) | a["pre"]

goal = {"On(A, B)", "On(B, C)"}
for a in [move("A", "Table", "B"), move("B", "Table", "C"), move("C", "A", "B")]:
    g = regress(goal, a)
    print(a["name"], "->", sorted(g) if g else "not usable")
''')


K.lesson('strips', 'STRIPS: actions with preconditions, add lists and delete lists', f'''
{src('Fikes and Nilsson, 1971, and Russell and Norvig, AIMA 3rd ed., section 10.1 (4th ed., section 11.1).')}
{wwh('STRIPS describes a state as a set of ground facts, such as On(C, A) and Clear(B). An action schema lists its preconditions (facts that must hold), its add list (facts it makes true) and its delete list (facts it makes false).',
     'Situation calculus needs a theorem prover and frame axioms. STRIPS is a small language where the frame problem disappears and states can be searched directly, which made fast planners possible.',
     'An action can run in state s when every precondition is in s. The new state is (s − delete list) ∪ add list. Any fact not mentioned stays as it was: this is the <b>STRIPS assumption</b>. Facts not listed in a state are false (closed world).')}
{fxs(fx('Applying an action', 'RESULT(s, a) = (s − DEL(a)) ∪ ADD(a), if PRE(a) ⊆ s', 'Delete first, then add.', key=True))}
{table(['Domain', 'Action schema (PDDL style)'], [
    ['Blocks world', 'Move(b, x, y): PRE On(b, x) ∧ Clear(b) ∧ Clear(y). ADD On(b, y) ∧ Clear(x). DEL On(b, x) ∧ Clear(y)'],
    ['Blocks world', 'MoveToTable(b, x): PRE On(b, x) ∧ Clear(b). ADD On(b, Table) ∧ Clear(x). DEL On(b, x)'],
    ['Air cargo', 'Fly(p, from, to): PRE At(p, from) ∧ Plane(p) ∧ Airport(from) ∧ Airport(to). ADD At(p, to). DEL At(p, from)'],
    ['Air cargo', 'Load(c, p, a): PRE At(c, a) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a). ADD In(c, p). DEL At(c, a)'],
    ['Spare tyre', 'PutOn(t, Axle): PRE Tire(t) ∧ At(t, Ground) ∧ ¬At(Flat, Axle). ADD At(t, Axle). DEL At(t, Ground)']])}
<p>Schemas have variables. A <b>ground action</b> replaces every variable with a constant: Move(C, A, Table) is not allowed (y must be a block), but MoveToTable(C, A) is.</p>
{note('PDDL (Planning Domain Definition Language, 1998) is the modern form of STRIPS. It adds types, negative preconditions, equality and more, and is used in the International Planning Competition.', 'tip')}
''', kw=['STRIPS', 'PDDL', 'precondition', 'add list', 'delete list', 'STRIPS assumption', 'action schema', 'ground action'])

K.lesson('search', 'Searching forwards and backwards', f'''
{src('AIMA 3rd ed., section 10.2.')}
{table(['', 'Forward (progression) search', 'Backward (regression) search'], [
    ['Starts from', 'the initial state', 'the goal'],
    ['A step', 'apply an action whose preconditions hold', 'regress the goal through a relevant action'],
    ['Branching', 'every applicable action, often many irrelevant ones', 'only actions that achieve part of the goal'],
    ['Search nodes', 'complete states', 'sets of goal facts (partial descriptions)'],
    ['Heuristics', 'easy to compute from a full state', 'harder, since nodes are sets of states']])}
{fxs(fx('Regression', 'g′ = (g − ADD(a)) ∪ PRE(a)', 'a is <b>relevant</b> if it adds some fact of g, and <b>consistent</b> if it deletes none.', key=True))}
{viz('strips', mode='bfs')}
{code('bw')}
{code('regress')}
{note('Regressing On(A, B) ∧ On(B, C) through Move(B, Table, C) gives a goal with both On(A, B) and Clear(B), which no state can satisfy. Backward planners need extra rules (state constraints) to throw such goals away early.', 'warn')}
''', kw=['forward search', 'progression', 'backward search', 'regression', 'relevant action', 'consistent action'])

K.lesson('heur', 'Heuristics for planning', f'''
{src('AIMA 3rd ed., section 10.2.3, and Hoffmann and Nebel, 2001 (the FF planner).')}
{wwh('Planning heuristics are made automatically from the action schemas by relaxing the problem: removing some of its rules so that it becomes easy to solve. The cost of the relaxed plan estimates the real cost.',
     'Without a heuristic, forward search tries every applicable action. With a good one, planners like FF and Fast Downward solve problems with thousands of actions.',
     'Ignore preconditions: every action can always run, so count how many actions are needed to make each goal fact true. Ignore delete lists: actions never undo anything, so facts only grow, and a relaxed plan can be found fast. The length of that relaxed plan is the heuristic.')}
{table(['Relaxation', 'Heuristic', 'Admissible'], [
    ['Ignore preconditions', 'number of unsatisfied goal facts (when each action adds one goal fact), or a set cover', 'Yes in its exact form, the set cover version is hard to compute exactly'],
    ['Ignore delete lists', 'h<sup>+</sup>, the cost of the best relaxed plan', 'Yes, but finding h<sup>+</sup> is NP-hard'],
    ['Ignore delete lists, greedy relaxed plan', 'h<sup>FF</sup> (FF planner)', 'No, but very informative'],
    ['Sub goal independence', 'sum (or max) of the costs of the goals solved one at a time', 'Max is admissible, sum is not']])}
{steps('Heuristics for the Sussman anomaly (true cost 3)', [
    'Unsatisfied goals: On(A, B) and On(B, C). Ignore preconditions: h = 2.',
    'Ignore delete lists: MoveToTable(C, A) gives Clear(A). Move(A, Table, B) gives On(A, B). Clear(B) is never deleted, so Move(B, Table, C) still runs and gives On(B, C).',
    'Relaxed plan length: 3.',
    eq('h = 2 with ignore preconditions, h<sup>+</sup> = 3 with ignore delete lists, true cost 3')])}
''', kw=['planning heuristic', 'relaxation', 'ignore preconditions', 'ignore delete lists', 'h plus', 'FF', 'sub goal independence'])

K.lesson('subgoal', 'Sub goals and the Sussman anomaly', f'''
{src('Sussman, 1975, and AIMA 3rd ed., section 10.4.4.')}
{wwh('A conjunctive goal such as On(A, B) ∧ On(B, C) has sub goals. A <b>linear</b> (non interleaved) planner solves the sub goals one at a time, in some order, and puts the plans one after the other. The original STRIPS planner worked this way with a goal stack.',
     'Splitting a goal into parts makes each part easy. If the parts do not interact (they are independent), this is fast and gives a good plan.',
     'Pick a sub goal, plan for it from the current state, run the plan, then move to the next sub goal. If a later plan undoes an earlier sub goal (clobbers it), go back and achieve it again.')}
{steps('The Sussman anomaly: start C on A, A and B on the table. Goal On(A, B) ∧ On(B, C)', [
    'Order 1, On(A, B) first: move C to the table, put A on B. Now B is under A. To get On(B, C), A must come off B, which undoes On(A, B).',
    'Order 2, On(B, C) first: put B on C. Now A is under C, which is under B. To get On(A, B), C must come off A, so B must come off C first, which undoes On(B, C).',
    'Either order undoes the first sub goal. A linear planner without going back gives a longer plan than needed (5 or 7 actions here).',
    'The best plan interleaves the two sub goals: MoveToTable(C, A) (for On(A, B)), Move(B, Table, C) (for On(B, C)), Move(A, Table, B) (for On(A, B)).',
    eq('sub goals interact, so plans for them must be interleaved: 3 actions')])}
{viz('strips', mode='sub')}
<p>Interleaving can be done by searching over partial plans instead of states, where steps for different sub goals can be ordered freely. That is the partial order planner of chapter 8.3.</p>
''', kw=['sub goal', 'linear planning', 'goal stack', 'Sussman anomaly', 'interleaving', 'clobbering', 'independent sub goals'])

K.lesson('maths', 'The maths: how big planning problems are', f'''
{fxs(
    fx('Ground actions in the blocks world with n blocks', 'n(n − 1) MoveToTable + n(n − 1) Move from the table + n(n − 1)(n − 2) Move between blocks', 'n = 3: 6 + 6 + 6 = 18. n = 4: 12 + 12 + 24 = 48.', key=True),
    fx('States of the blocks world', '1, 3, 13, 73, 501, ... for n = 1, 2, 3, 4, 5', 'The ways to arrange n named blocks into stacks. It grows faster than n!.'),
    fx('Complexity', 'PlanSAT (is there any plan?) is PSPACE-complete for STRIPS', 'Bylander, 1994. Bounded PlanSAT (is there a plan of length ≤ k?) is also PSPACE-complete in general, and NP-complete for many restricted forms.'))}
{steps('Worked example: regress On(A, B) through Move(A, Table, B)', [
    'ADD = {On(A, B)}, so the action is relevant. DEL = {On(A, Table), Clear(B)} does not touch the goal, so it is consistent.',
    'g − ADD = { }.',
    'Add PRE = {On(A, Table), Clear(A), Clear(B)}.',
    eq('g′ = On(A, Table) ∧ Clear(A) ∧ Clear(B)')])}
''', kw=['number of ground actions', 'blocks world states', 'PSPACE', 'Bylander', 'regression worked example'])

K.lesson('compare', 'Ways to plan with STRIPS actions', f'''
{versus('Planning algorithms', ['', 'Forward search + heuristic', 'Backward search', 'Linear sub goal planning', 'Partial order planning (8.3)', 'GraphPlan and SATPlan'], [
    ['Searches over', 'states', 'goal sets', 'sub goals, one at a time', 'partial plans', 'a planning graph, or a SAT formula'],
    ['Handles interacting sub goals', 'Yes', 'Yes', 'No (gives long plans or fails)', 'Yes', 'Yes'],
    ['Plan form', 'sequence', 'sequence', 'sequence', 'partial order: flexible', 'sequence of parallel steps'],
    ['Strength', 'Fastest today (FF, Fast Downward)', 'Few relevant actions', 'Simple', 'Least commitment, easy to explain', 'Good for plans with parallel actions'],
    ['Weakness', 'Many irrelevant actions without a heuristic', 'Goal sets can be impossible', 'Incomplete for interacting goals', 'Slower than heuristic state search', 'Large graphs or formulas']],
    'heuristic forward search is the usual choice today. Partial order planning still matters when a flexible plan is needed, for example when people or several robots carry out the steps.')}
{scene('Planning in practice', '<p>NASA\'s Remote Agent planned and controlled the Deep Space 1 spacecraft in 1999. The Mars rovers use planning tools to build each day\'s list of actions. Logistics companies, video games (the F.E.A.R. game used STRIPS style goal planning for its enemies) and cloud systems that set up servers all use STRIPS style planners.</p>')}
''', kw=['comparison', 'FF', 'Fast Downward', 'GraphPlan', 'SATPlan', 'Remote Agent', 'goal oriented action planning'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Each action is a card: "you need these things", "you get these things", "you lose these things". A planner chains cards from where you are to what you want.</p>',
    '<p>STRIPS states are sets of facts. RESULT(s, a) = (s − DEL) ∪ ADD. Forward search uses full states, backward search regresses goals through relevant actions. Heuristics come from relaxations. Linear sub goal planning fails on the Sussman anomaly.</p>',
    '<p>Planning with STRIPS is PSPACE-complete. The planning graph (Blum and Furst, 1995) gives admissible heuristics with mutual exclusion links. Landmarks (facts every plan must make true) and abstraction heuristics such as pattern databases power modern optimal planners.</p>',
    '<p>Current research: learning heuristics and generalised policies with neural networks, planning with large language models checked by a classical planner, and temporal and numeric planning (PDDL 2.1) for real time and resources.</p>')}
''', kw=['planning graph', 'landmarks', 'pattern databases', 'generalised planning', 'LLM planning'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'STRIPS: states are sets of ground facts, actions have preconditions, an add list and a delete list. Facts not mentioned stay the same.',
    'Forward search applies actions to states. Backward search regresses goals: g′ = (g − ADD) ∪ PRE through relevant, consistent actions.',
    'Heuristics come from relaxed problems: ignore preconditions, ignore delete lists (h<sup>+</sup>, h<sup>FF</sup>), sub goal independence.',
    'Solving sub goals one at a time fails when they interact. The Sussman anomaly needs the steps for On(A, B) and On(B, C) to be interleaved.',
    'STRIPS planning is PSPACE-complete, yet heuristic planners solve large real problems.'],
    'chapter 8.3 plans with partial orders: add steps only as needed, link them, and order them only when they clash.')}
{nbcard('strips-planning', 'Run forward search on the Sussman anomaly and regress a goal through actions, then write action application, regression and a blocks world planner yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In STRIPS, applying action a in state s gives', ['s ∪ ADD(a)', '(s − DEL(a)) ∪ ADD(a)', 's − ADD(a)', 'PRE(a)'], 1,
       'Delete, then add.', 'Facts not in the lists stay.')
K.quiz('e', 'The STRIPS assumption says', ['every action is possible', 'facts not mentioned in the effects stay unchanged', 'the goal is one fact', 'there are no variables'], 1,
       'The frame problem.', 'Only listed facts change.')
K.quiz('e', 'Move(b, x, y) in the blocks world needs', ['On(b, x), Clear(b), Clear(y)', 'On(b, y)', 'Clear(x)', 'Holding(b)'], 0,
       'b must be free and y must be free.', 'b sits on x, nothing is on b, nothing is on y.')
K.quiz('e', 'Forward planning search is also called', ['regression', 'progression', 'resolution', 'unification'], 1,
       'It moves forward in time.', 'From the initial state to the goal.')
K.quiz('m', 'An action is relevant for goal g in backward search if', ['its preconditions hold', 'it adds at least one fact of g', 'it deletes a fact of g', 'it has no effects'], 1,
       'It helps.', 'And it must also not delete any fact of g.')
K.quiz('m', 'The ignore delete lists heuristic assumes', ['actions have no preconditions', 'actions never make a fact false', 'there is one goal', 'plans have length 1'], 1,
       'Facts only grow.', 'The relaxed problem is much easier.')
K.quiz('m', 'In the Sussman anomaly, the shortest plan has how many actions?', ['2', '3', '4', '5'], 1,
       'Interleave.', 'MoveToTable(C, A), Move(B, Table, C), Move(A, Table, B).')
K.quiz('m', 'Why does solving sub goals one at a time fail on the Sussman anomaly?', ['There are too many blocks', 'The plan for one sub goal undoes the other, in either order', 'The goal is impossible', 'STRIPS cannot express it'], 1,
       'Clobbering.', 'The sub goals interact.')
K.quiz('h', 'The number of unsatisfied goal facts is admissible when', ['always', 'each action adds at most one goal fact and none is deleted', 'never', 'actions have no preconditions'], 1,
       'One action, one goal.', 'Then at least that many actions are needed.')
K.quiz('h', 'Planning with STRIPS (is there any plan?) is', ['polynomial', 'NP-complete', 'PSPACE-complete', 'undecidable'], 2,
       'Bylander 1994.', 'Plans can be exponentially long.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: regressing On(A, B) ∧ On(B, C) through Move(B, Table, C) gives a goal containing On(A, B) and Clear(B). What should a backward planner do?', ['Keep it, it is fine', 'Prune it: no state has A on B and B clear', 'Add On(B, A)', 'Regress again through the same action'], 1,
       'State constraints.', 'Something on B means B is not clear.')
K.quiz('x', 'In the style of an MIT 6.034 exam: which heuristic is admissible for STRIPS planning in general?', ['h<sup>FF</sup>', 'h<sup>+</sup> (optimal relaxed plan cost, ignoring delete lists)', 'the sum of sub goal costs', 'the number of facts in the state'], 1,
       'Relaxed problems give lower bounds when solved optimally.', 'h<sup>FF</sup> is greedy and may overestimate, and the sum double counts shared steps.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Ground MoveToTable actions for 3 blocks: n(n − 1).', '6', '3 × 2.',
       ['b has 3 choices.', 'x is another block: 2 choices.', eq('6')], check=6)
K.calc('e', 'How many unsatisfied goal facts in the Sussman start (goal On(A, B) ∧ On(B, C))?', '2', 'Neither holds yet.',
       ['On(A, B) is false.', 'On(B, C) is false.', eq('2')], check=2)
K.calc('e', 'How many facts does the regressed goal (g − ADD) ∪ PRE have for g = On(A, B), a = Move(A, Table, B)?', '3', 'g − ADD is empty.',
       ['g − {On(A, B)} = { }.', 'PRE = On(A, Table), Clear(A), Clear(B).', eq('3 facts')], check=3)
K.calc('m', 'All ground actions for 3 blocks (MoveToTable, Move from table, Move between blocks).', '18', '6 + 6 + 6.',
       ['MoveToTable: 3 × 2 = 6. From the table: 3 × 2 = 6.', 'Between blocks: 3 × 2 × 1 = 6.', eq('18')], check=18)
K.calc('m', 'The same for 4 blocks.', '48', '12 + 12 + 24.',
       ['4 × 3 = 12 and 12.', '4 × 3 × 2 = 24.', eq('48')], check=48)
K.calc('m', 'Forward breadth first search on the Sussman anomaly. How many blocks world states exist for 3 blocks?', '13', 'All arrangements of 3 named blocks into stacks.',
       ['All on the table: 1. One stack of 2 and one alone: 6.', 'One stack of 3: 3! = 6.', eq('1 + 6 + 6 = 13')], check=13)
K.calc('h', 'How many states does the blocks world with 4 blocks have?', '73', 'Count by stack shapes.',
       ['All alone: 1. One pair, two alone: 6 × 2 = 12. Two pairs: 3 × 4 = 12.', 'A tower of 3 and one alone: 4 × 6 = 24. A tower of 4: 24.', eq('1 + 12 + 12 + 24 + 24 = 73')], check=73)
K.calc('h', 'Linear planning on the Sussman anomaly with On(A, B) first gave 5 actions. How many more than the shortest plan?', '2', '5 − 3.',
       ['Linear plan: 5 actions.', 'Shortest plan: 3.', eq('2 wasted actions')], check=2)
K.calc('h', 'The ignore delete lists heuristic h<sup>+</sup> for the Sussman start.', '3', 'Find the shortest relaxed plan.',
       ['MoveToTable(C, A) gives Clear(A). Move(A, Table, B) gives On(A, B), and Clear(B) is not deleted.', 'Move(B, Table, C) gives On(B, C). Two actions cannot add both goals and Clear(A).', eq('h<sup>+</sup> = 3')], check=3)
K.calc('x', 'In the style of a Stanford CS221 problem: air cargo with 2 planes, 2 cargo items and 3 airports. How many ground Fly(p, from, to) actions with from ≠ to?', '12', 'p, then an ordered pair of airports.',
       ['2 planes.', 'Ordered pairs of different airports: 3 × 2 = 6.', eq('2 × 6 = 12')], check=12)

# ---------------------------------------------------------------- assignments
K.assign('apply', 'e', 'Apply a STRIPS action',
         '<p>A state is a Python set of fact strings. An action is a dictionary with sets "pre", "add" and "del". Write <code>apply(state, action)</code>: return None if some precondition is missing, else the new state (delete first, then add).</p>',
         '''
def apply(state, action):
    # your code here
    pass
''', [("sorted(apply({'On(C, A)', 'On(A, Table)', 'On(B, Table)', 'Clear(C)', 'Clear(B)'}, {'pre': {'On(C, A)', 'Clear(C)'}, 'add': {'On(C, Table)', 'Clear(A)'}, 'del': {'On(C, A)'}}))",
       ['Clear(A)', 'Clear(B)', 'Clear(C)', 'On(A, Table)', 'On(B, Table)', 'On(C, Table)']),
      ("apply({'On(A, Table)'}, {'pre': {'Clear(A)'}, 'add': set(), 'del': set()})", None),
      ("sorted(apply({'P', 'Q'}, {'pre': {'P'}, 'add': {'R'}, 'del': {'P'}}))", ['Q', 'R'])],
         '''
def apply(state, action):
    for p in action["pre"]:
        if p not in state:
            return None
    new = set(state)
    for d in action["del"]:
        new.discard(d)
    for a in action["add"]:
        new.add(a)
    return new
''', 'Check every precondition. Then copy the state, remove the delete list and add the add list.', '<p>Test 1 is MoveToTable(C, A) in the Sussman start.</p>')
K.assign('regress', 'm', 'Regress a goal through an action',
         '<p>Write <code>regress(goal, action)</code> with sets as in the last task. Return None if the action is not relevant (adds nothing in the goal) or not consistent (deletes something in the goal). Otherwise return (goal − add) ∪ pre.</p>',
         '''
def regress(goal, action):
    # your code here
    pass
''', [("sorted(regress({'On(A, B)', 'On(B, C)'}, {'pre': {'On(A, Table)', 'Clear(A)', 'Clear(B)'}, 'add': {'On(A, B)'}, 'del': {'On(A, Table)', 'Clear(B)'}}))",
       ['Clear(A)', 'Clear(B)', 'On(A, Table)', 'On(B, C)']),
      ("regress({'On(A, B)'}, {'pre': {'X'}, 'add': {'Y'}, 'del': set()})", None),
      ("regress({'P', 'Q'}, {'pre': {'R'}, 'add': {'P'}, 'del': {'Q'}})", None),
      ("sorted(regress({'P'}, {'pre': {'R', 'S'}, 'add': {'P'}, 'del': set()}))", ['R', 'S'])],
         '''
def regress(goal, action):
    if len(goal & action["add"]) == 0:
        return None
    if len(goal & action["del"]) > 0:
        return None
    return (goal - action["add"]) | action["pre"]
''', 'Use set intersection (&) to test relevance and consistency, then set difference and union.', '<p>Test 3: the action adds P but deletes Q, which the goal also needs, so it cannot be the last step.</p>')
K.assign('bwplan', 'h', 'A blocks world planner',
         '<p>A state is a dictionary from block to what it sits on ("Table" or another block). Write <code>plan_blocks(start, goal)</code> that returns a shortest list of moves as (block, to) pairs, using breadth first search. A move picks a clear block and puts it on the table (if it is not there already) or on another clear block. goal is a dictionary of required On facts.</p>',
         '''
def plan_blocks(start, goal):
    # your code here
    pass
''', [("len(plan_blocks({'A': 'Table', 'B': 'Table', 'C': 'A'}, {'A': 'B', 'B': 'C'}))", 3),
      ("plan_blocks({'A': 'Table', 'B': 'Table'}, {'A': 'B'})", [('A', 'B')]),
      ("plan_blocks({'A': 'B', 'B': 'Table'}, {'A': 'B'})", []),
      ("len(plan_blocks({'A': 'B', 'B': 'C', 'C': 'Table'}, {'C': 'B', 'B': 'A'}))", 3)],
         '''
def plan_blocks(start, goal):
    queue = [(start, [])]
    seen = [start]
    while queue:
        state, plan = queue.pop(0)
        done = True
        for b in goal:
            if state[b] != goal[b]:
                done = False
        if done:
            return plan
        below = set(state.values())
        free = []
        for b in sorted(state):
            if b not in below:
                free.append(b)
        for b in free:
            targets = []
            if state[b] != "Table":
                targets.append("Table")
            for y in free:
                if y != b:
                    targets.append(y)
            for to in targets:
                new = dict(state)
                new[b] = to
                if new not in seen:
                    seen.append(new)
                    queue.append((new, plan + [(b, to)]))
    return None
''', 'A block is clear if no block sits on it. Keep a queue of (state, plan) and a list of seen states.', '<p>Test 4 turns a tower upside down. At the start A is on top and C is at the bottom. The goal puts C on B and B on A, so A must end at the bottom. The shortest plan has three moves: A to the table, B onto A, then C onto B.</p>')

K.must('STRIPS', 'State = set of facts. Action = PRE, ADD, DEL. RESULT = (s − DEL) ∪ ADD. Unmentioned facts stay.')
K.must('Regression', 'g′ = (g − ADD) ∪ PRE, for actions that add part of g and delete none of it.')
K.must('Heuristics', 'Ignore preconditions, ignore delete lists (h<sup>+</sup> admissible, h<sup>FF</sup> greedy), sub goal independence.')
K.must('Sussman anomaly', 'C on A, goal A on B and B on C. Either sub goal order undoes the other. Shortest plan 3: C to table, B on C, A on B.')
K.must('Complexity', 'STRIPS planning is PSPACE-complete. Blocks world states: 13 for 3 blocks, 73 for 4.')

T = K.topic(
    slug='strips-planning', topic='strips-planning', step=(8, 'Planning', 'cai-planning', 'Find a sequence of actions with logic: situation calculus, deductive planning, STRIPS, sub goals and partial order planning.', 'College'),
    title='STRIPS planning and sub goals', short='STRIPS and sub goals', badge='8.2', minutes=50,
    lead='Describe actions by what they need, add and delete, and search for plans forwards and backwards. Build planning heuristics by relaxing the problem, and see with the Sussman anomaly why solving sub goals one at a time can fail.',
    desc='STRIPS states and action schemas, the STRIPS assumption, PDDL, the blocks world, air cargo and spare tyre domains, forward progression and backward regression search, relevant and consistent actions, heuristics from relaxations, linear sub goal planning, the Sussman anomaly and interleaving, and the complexity of planning.',
    summary='STRIPS actions, forward and backward search, planning heuristics, sub goals and the Sussman anomaly.',
    keywords=['STRIPS', 'PDDL', 'blocks world', 'progression', 'regression', 'planning heuristic', 'sub goal', 'Sussman anomaly', 'linear planning'],
    recap='<p>STRIPS: (s − DEL) ∪ ADD. Search forwards or backwards with relaxed heuristics. Interacting sub goals must be interleaved.</p>',
    nb={'bw': 'Forward search on the Sussman anomaly', 'regress': 'Regressing a goal through actions'})
