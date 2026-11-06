# Chapter 8.1: situation calculus and deductive planning. The uploaded slides and transcripts do not cover planning,
# so this chapter follows Russell and Norvig, AIMA 3rd ed. section 10.4.2, McCarthy and Hayes (1969), Green (1969)
# and Reiter (1991). The robot and gold world is our own small example, and every plan in it was checked by running
# the code of this chapter.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('ssa', r'''
# Successor state axioms for a robot, two rooms A and B, and a bar of gold.
# A state holds the fluents: where the robot is, where the gold is, and whether the robot holds it.
def possible(action, s):
    if action == "Grab":
        return s["gold"] == s["robot"] and not s["holding"]
    if action == "Release":
        return s["holding"]
    return action in ["Go(A)", "Go(B)"]

def result(action, s):
    # At(Robot, x, Result(a, s)) <=> a = Go(x) or (At(Robot, x, s) and a is not a Go action)
    robot = action[3] if action.startswith("Go") else s["robot"]
    # At(Gold, x, Result(a, s)) <=> (Holding(Gold, s) and a = Go(x)) or (At(Gold, x, s) and not (Holding(Gold, s) and a is a Go action))
    gold = robot if s["holding"] and action.startswith("Go") else s["gold"]
    # Holding(Gold, Result(a, s)) <=> a = Grab or (Holding(Gold, s) and a != Release)
    holding = action == "Grab" or (s["holding"] and action != "Release")
    return {"robot": robot, "gold": gold, "holding": holding}

s = {"robot": "A", "gold": "B", "holding": False}
print("S0", s)
plan = ["Go(B)", "Grab", "Go(A)", "Release"]
for i in range(len(plan)):
    if not possible(plan[i], s):
        print("not possible:", plan[i])
        break
    s = result(plan[i], s)
    print("S" + str(i + 1), s, " after", plan[i])
''')

K.code('green', r'''
# Planning as finding a situation term: search the terms Result(a, s) breadth first until the goal holds.
def possible(action, s):
    robot, gold, holding = s
    if action == "Grab":
        return gold == robot and not holding
    if action == "Release":
        return holding
    return True

def result(action, s):
    robot, gold, holding = s
    if action.startswith("Go"):
        robot = action[3]
        if holding:
            gold = robot
    if action == "Grab":
        holding = True
    if action == "Release":
        holding = False
    return (robot, gold, holding)

start = ("A", "B", False)            # robot in A, gold in B, not holding
queue = [(start, "S0")]
seen = [start]
while queue:
    s, term = queue.pop(0)
    if s[1] == "A" and not s[2]:     # goal: gold lies in room A
        print("answer: s =", term)
        break
    for a in ["Go(A)", "Go(B)", "Grab", "Release"]:
        if possible(a, s):
            t = result(a, s)
            if t not in seen:
                seen.append(t)
                queue.append((t, "Result(" + a + ", " + term + ")"))
''')

K.lesson('plan', 'What planning is', f'''
{src('Russell and Norvig, AIMA 3rd ed., chapter 10 and 4th ed., chapter 11. The uploaded slides do not cover planning, so this step follows the textbook and the papers it cites.')}
{wwh('Planning is finding a sequence of actions that takes an agent from a starting state to a state where its goals hold. Classical planning assumes the world is fully observable, deterministic, static and known.',
     'A search agent (step 2) needs a hand written successor function and a heuristic for each new problem. A planning agent reads a general description of its actions in logic, so the same planner works in every domain, and it can use the structure of the description (which facts an action changes) to search much faster.',
     'Describe states with logical facts, and actions with what they need (preconditions) and what they change (effects). Then search for a plan, either by logical deduction (this chapter), by searching through states with STRIPS actions (chapter 8.2), or by refining a partial plan (chapter 8.3).')}
{table(['Planning language', 'States', 'Actions', 'Main use'], [
    ['Situation calculus (McCarthy, 1963)', 'situations: terms such as Result(Go(B), S0)', 'axioms in first order logic', 'Deductive planning, theory of action'],
    ['STRIPS (Fikes and Nilsson, 1971)', 'sets of ground facts', 'precondition, add list, delete list', 'Fast state space planners'],
    ['PDDL (1998)', 'like STRIPS, with types and more', 'action schemas with parameters', 'The standard language of planning competitions']])}
''', kw=['planning', 'classical planning', 'plan', 'planning language', 'PDDL'])

K.lesson('sitcalc', 'Situation calculus', f'''
{src('McCarthy and Hayes, 1969, and AIMA 3rd ed., section 10.4.2.')}
{wwh('Situation calculus is a way to describe change in first order logic. A <b>situation</b> is a snapshot of the world after a sequence of actions. The function Result(a, s) names the situation after doing action a in situation s.',
     'Plain first order logic has no notion of time: a fact is just true or false. To plan, we must say what is true before and after each action, and reason about sequences of actions.',
     'Add one extra argument, the situation, to every relation that can change. At(Robot, A, S0) says the robot is in room A at the start. Write axioms that say when an action is possible and how it changes these relations.')}
{table(['Part', 'Meaning', 'Example'], [
    ['Initial situation S0', 'the start', 'At(Robot, A, S0), At(Gold, B, S0)'],
    ['Result(a, s)', 'the situation after action a in s', 'S1 = Result(Go(B), S0)'],
    ['Fluent', 'a relation or function whose value changes, with the situation as last argument', 'Holding(Gold, s)'],
    ['Atemporal (eternal) predicate', 'true or false in every situation', 'Gold(G1), Adjacent(A, B)'],
    ['Possibility axiom', 'when an action can be done', 'Poss(Grab, s) ⇔ ∃x At(Gold, x, s) ∧ At(Robot, x, s) ∧ ¬Holding(Gold, s)'],
    ['Effect axiom', 'what an action changes', 'Poss(Grab, s) ⇒ Holding(Gold, Result(Grab, s))']])}
{viz('sitcalc')}
''', kw=['situation calculus', 'situation', 'Result', 'fluent', 'possibility axiom', 'effect axiom', 'McCarthy'])

K.lesson('frame', 'The frame problem and successor state axioms', f'''
{src('McCarthy and Hayes, 1969 (the frame problem), and Reiter, 1991 (successor state axioms).')}
<p>Effect axioms say what changes. They say nothing about what stays the same. After Go(B), is the gold still in room B? Nothing in the effect axioms of Go says so, so the logic cannot conclude it. This is the <b>frame problem</b>.</p>
{table(['Version of the problem', 'What goes wrong'], [
    ['Representational frame problem', 'Writing a frame axiom such as At(Gold, x, s) ∧ ¬Holding(Gold, s) ⇒ At(Gold, x, Result(Go(y), s)) for every pair of action and fluent: A × F axioms'],
    ['Inferential frame problem', 'Carrying every unchanged fact forward one action at a time costs time for every fact at every step'],
    ['Qualification problem', 'Listing every condition for an action to succeed is endless: the robot can grab the gold unless it is glued down, too heavy, ...'],
    ['Ramification problem', 'Indirect effects: when the robot moves while holding the gold, the gold moves too']])}
{fxs(fx('Successor state axiom (one per fluent F)', 'Poss(a, s) ⇒ [F(Result(a, s)) ⇔ (a made F true) ∨ (F(s) ∧ a did not make F false)]', 'A fluent is true after an action if the action made it true, or if it was already true and the action did not make it false.', key=True))}
{steps('The successor state axioms of the robot world', [
    'Holding(Gold, Result(a, s)) ⇔ a = Grab ∨ (Holding(Gold, s) ∧ a ≠ Release).',
    'At(Robot, x, Result(a, s)) ⇔ a = Go(x) ∨ (At(Robot, x, s) ∧ ¬∃y a = Go(y)).',
    'At(Gold, x, Result(a, s)) ⇔ (Holding(Gold, s) ∧ a = Go(x)) ∨ (At(Gold, x, s) ∧ ¬(Holding(Gold, s) ∧ ∃y a = Go(y))). This also handles the ramification: the held gold moves with the robot.',
    'Unique action axioms say different action names are different: Grab ≠ Release, Go(x) ≠ Grab, and Go(x) = Go(y) only if x = y.',
    eq('F successor state axioms replace A × F frame axioms')])}
{code('ssa')}
''', kw=['frame problem', 'frame axiom', 'successor state axiom', 'Reiter', 'qualification problem', 'ramification problem', 'unique action axioms'])

K.lesson('deductive', 'Deductive planning: a plan is a proof', f'''
{src('Green, 1969, "Application of theorem proving to problem solving".')}
{wwh('In deductive planning the goal is a query to a theorem prover: is there a situation s in which the goal holds? A constructive proof must name such an s, and that name is the plan.',
     'It uses one general reasoner for everything: the same prover answers questions and makes plans. Every plan comes with a proof that it works.',
     'Ask ∃s At(Gold, A, s) ∧ ¬Holding(Gold, s). A resolution prover with answer extraction (it keeps track of what the variable s was bound to) returns s = Result(Release, Result(Go(A), Result(Grab, Result(Go(B), S0)))). Read the term from the inside out to get the plan: Go(B), Grab, Go(A), Release.')}
{code('green')}
{note('The search above is not a resolution prover. It looks through the same situation terms breadth first, which is what a fair prover ends up doing for this small problem, and it finds the same answer term.', 'tip')}
{table(['Strength of deductive planning', 'Weakness'], [
    ['Very expressive: quantifiers, functions, partial knowledge', 'General theorem provers are slow and have no planning heuristics'],
    ['A proof that the plan works', 'No guarantee of a short plan'],
    ['Clear meaning (semantics)', 'The frame problem must be handled with care, and the search space of proofs is huge']])}
<p>These weaknesses led Fikes and Nilsson to STRIPS in 1971: keep the idea of preconditions and effects, but drop full logic and search over states directly. That is chapter 8.2.</p>
''', kw=['deductive planning', 'Green', 'answer extraction', 'constructive proof', 'theorem proving'])

K.lesson('maths', 'The maths: counting axioms and situations', f'''
{fxs(
    fx('Frame axioms needed', 'A × F', 'One for each action and fluent pair that the action does not change. 20 actions and 50 fluents: up to 1,000.', key=True),
    fx('Successor state axioms needed', 'F', 'One per fluent, however many actions there are. 50 fluents: 50 axioms.', key=True),
    fx('Situations up to depth d', '1 + b + b² + ... + b<sup>d</sup>', 'b actions possible in each situation. Situations are terms, so two different action sequences are always two different situations, even when the world looks the same.'))}
{steps('Worked example: 4 actions, depth 3', [
    'Depth 0: 1 situation (S0).',
    'Depth 1: 4. Depth 2: 16. Depth 3: 64.',
    '1 + 4 + 16 + 64 = 85.',
    eq('85 situation terms, but only 6 different world states in the robot world')])}
{steps('Worked example: is Release possible in S2 = Result(Grab, Result(Go(B), S0))?', [
    'Poss(Release, s) ⇔ Holding(Gold, s).',
    'Holding(Gold, Result(Grab, S1)) ⇔ Grab = Grab ∨ ... which is true.',
    'So Holding(Gold, S2) holds.',
    eq('Release is possible in S2')])}
''', kw=['frame axioms count', 'successor state axioms count', 'situation terms', 'worked example'])

K.lesson('compare', 'Situation calculus against other ways to describe actions', f'''
{versus('Representing actions', ['', 'Situation calculus', 'STRIPS and PDDL', 'Event calculus'], [
    ['Logic', 'Full first order', 'Ground facts, no quantifiers in states', 'First order, time points'],
    ['Frame problem', 'Solved by successor state axioms', 'Solved by the STRIPS assumption: facts not in the delete list stay', 'Solved by circumscription over events'],
    ['Actions at the same time', 'Hard', 'No (sequential plans)', 'Yes, events happen at time points'],
    ['Planner speed', 'Slow (theorem proving)', 'Fast (heuristic search)', 'Slow'],
    ['Used for', 'Theory, GOLOG robot programs, reasoning about what is known', 'Practical planners, competitions', 'Narratives, commonsense reasoning']],
    'situation calculus gives the clearest meaning to actions and change. STRIPS keeps the useful part, preconditions and effects, and gives up expressiveness for speed.')}
{scene('Shakey the robot', '<p>Shakey (SRI, 1966 to 1972) was the first mobile robot that reasoned about its own actions. Its first planner, QA3, used Green\'s deductive planning. It was too slow, so the team built STRIPS, and also the A* search algorithm (Hart, Nilsson and Raphael, 1968) to plan its routes.</p>')}
''', kw=['comparison', 'event calculus', 'GOLOG', 'Shakey', 'STRIPS assumption'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Keep a diary of the world: what is true at the start, and after each action. A rule for each fact says how one action changes it, and everything else stays as it was.</p>',
    '<p>Situations S0, Result(a, s). Fluents take a situation argument. Possibility and effect axioms. The frame problem and Reiter\'s successor state axioms. Green\'s deductive planning extracts a plan from a proof of ∃s Goal(s).</p>',
    '<p>Reiter\'s basic action theories make regression possible: to check if a goal holds after a plan, rewrite it step by step into a question about S0 only. GOLOG (1997) builds a programming language on top of situation calculus, and knowledge fluents describe what the agent knows after sensing.</p>',
    '<p>Research continues on epistemic planning (planning about other agents\' knowledge), verification of GOLOG agent programs, and on mixing logic based action theories with probabilistic and learned models.</p>')}
''', kw=['regression', 'basic action theory', 'GOLOG', 'epistemic planning'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Classical planning finds action sequences in a fully observable, deterministic, static and known world.',
    'Situation calculus names situations with S0 and Result(a, s). Fluents take the situation as an extra argument. Possibility and effect axioms describe actions.',
    'The frame problem: effect axioms do not say what stays the same. Successor state axioms fix it with one axiom per fluent instead of A × F frame axioms.',
    'Deductive planning (Green, 1969) proves ∃s Goal(s). The binding of s, read from the inside out, is the plan.',
    'Theorem proving is slow for planning, which led to STRIPS.'],
    'chapter 8.2 describes actions with STRIPS and searches through states, and shows how sub goals can interact.')}
{nbcard('situation-calculus', 'Run successor state axioms on a plan and find the plan term by search, then write the axioms, a plan checker and a planner yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In situation calculus, Result(a, s) is', ['a truth value', 'the situation after doing a in s', 'an action', 'a fluent'], 1,
       'A term.', 'It names a new situation.')
K.quiz('e', 'A fluent is', ['a fixed fact', 'a relation whose truth can change from one situation to the next', 'an action', 'a plan'], 1,
       'It flows with time.', 'It takes the situation as its last argument.')
K.quiz('e', 'Which axiom says when an action can be done?', ['effect axiom', 'possibility axiom', 'frame axiom', 'unique names axiom'], 1,
       'Poss(a, s).', 'Poss(a, s) ⇔ preconditions.')
K.quiz('e', 'The frame problem is about', ['drawing pictures', 'saying what does not change after an action', 'robots falling over', 'the size of the plan'], 1,
       'The unchanged background.', 'Effect axioms only say what changes.')
K.quiz('m', 'How many successor state axioms do 30 fluents and 10 actions need?', ['10', '30', '300', '40'], 1,
       'One per fluent.', 'Each axiom covers every action.')
K.quiz('m', 'Holding(Gold, Result(a, s)) ⇔ a = Grab ∨ (Holding(Gold, s) ∧ a ≠ Release). After Go(B) while holding the gold,', ['the robot drops it', 'the robot still holds it', 'it is unknown', 'Go(B) is impossible'], 1,
       'Second part.', 'Go(B) ≠ Release, so holding continues.')
K.quiz('m', 'In deductive planning, the plan comes from', ['a heuristic', 'the binding of s in a proof of ∃s Goal(s)', 'a truth table', 'random search'], 1,
       'Answer extraction.', 'Read the Result term from the inside out.')
K.quiz('m', 'The ramification problem is about', ['too many rules', 'indirect effects, such as held gold moving with the robot', 'missing preconditions', 'slow provers'], 1,
       'Side effects.', 'Effects that follow from other effects.')
K.quiz('h', 'Why were unique action axioms needed?', ['To make actions faster', 'Without them, the logic cannot rule out Grab = Release, and the successor state axioms break', 'To count actions', 'They are not needed'], 1,
       'Different names.', 'FOL does not assume different names mean different things.')
K.quiz('h', 'The qualification problem says', ['plans are too long', 'listing every condition under which an action succeeds is endless', 'fluents have no values', 'goals are unknown'], 1,
       'Endless conditions.', 'There is always one more thing that could stop the action.')
K.quiz('x', 'In the style of a Stanford CS221 exam: two different action sequences lead to the same world. In situation calculus they are', ['the same situation', 'different situations, since Result terms differ', 'not allowed', 'merged by the frame axioms'], 1,
       'Terms, not states.', 'Situations are histories, so search over situations repeats states.')
K.quiz('x', 'In the style of an MIT 6.034 exam: why did STRIPS replace deductive planning on Shakey?', ['Logic was wrong', 'General theorem proving was too slow and had no planning heuristics', 'Shakey had no sensors', 'STRIPS is more expressive'], 1,
       'Speed.', 'STRIPS searches states directly with a restricted language.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Frame axioms for 5 actions and 8 fluents (one per pair)?', '40', 'A × F.',
       ['5 actions.', '8 fluents.', eq('5 × 8 = 40')], check=40)
K.calc('e', 'Successor state axioms for the same domain?', '8', 'One per fluent.',
       ['8 fluents.', 'One axiom each.', eq('8')], check=8)
K.calc('e', 'How many Result(...) wrappers does the plan term for Go(B), Grab, Go(A), Release have?', '4', 'One per action.',
       ['Each action adds one Result.', '4 actions.', eq('4')], check=4)
K.calc('m', 'Situation terms up to depth 3 with 4 actions possible each time.', '85', '1 + 4 + 16 + 64.',
       ['Depth 0 to 3: 1, 4, 16, 64.', 'Add them.', eq('85')], check=85)
K.calc('m', 'Different world states in the robot world (robot in A or B, gold in A or B or held). Held gold is where the robot is.', '6', 'Robot 2 × gold 3.',
       ['Robot: 2 rooms.', 'Gold: in A, in B, or held.', eq('2 × 3 = 6 states')], check=6)
K.calc('m', 'With 20 actions and 50 fluents, how many times more frame axioms than successor state axioms?', '20', '1000 ⁄ 50.',
       ['Frame axioms: 20 × 50 = 1,000.', 'Successor state axioms: 50.', eq('1,000 ⁄ 50 = 20 times more')], check=20)
K.calc('h', 'Situation terms at exactly depth 6 with b = 3.', '729', '3⁶.',
       ['3² = 9, 3³ = 27.', '27 × 27.', eq('729')], check=729)
K.calc('h', 'Breadth first search in the green example keeps a list of seen states. At most how many states can it expand in the robot world?', '6', 'Count the distinct world states.',
       ['2 robot rooms times 3 gold places.', 'Each is expanded at most once.', eq('6')], check=6)
K.calc('h', 'Start: robot in A, gold in B. Plan Go(B), Grab, Go(B), Go(A), Release. How many of its actions change no fluent at all?', '1', 'Go(B) when already in B.',
       ['Go(B) moves the robot. Grab changes Holding.', 'The second Go(B) changes nothing: the robot is already in B. Go(A) and Release change fluents.', eq('1 action changes nothing')], check=1)
K.calc('x', 'In the style of a Stanford CS221 problem: a domain has 12 fluents. Each action changes on average 2 of them. Over a 10 action plan, how many fluent values are carried over unchanged by frame reasoning?', '100', '(12 − 2) per action.',
       ['Each action leaves 12 − 2 = 10 fluents as they were.', 'Over 10 actions.', eq('10 × 10 = 100 carried over values: the inferential frame problem')], check=100)

# ---------------------------------------------------------------- assignments
ROBOT = '''
# A state is a dictionary: "robot" is "A" or "B", "gold" is "A" or "B", "holding" is True or False.
ACTIONS = ["Go(A)", "Go(B)", "Grab", "Release"]
'''
K.assign('ssa', 'e', 'Successor state axioms',
         '<p>Write <code>result(action, s)</code> that returns the new state after the action, using the successor state axioms of this chapter. The robot moves with Go(x). If it holds the gold, the gold moves too. Grab makes holding true, Release makes it false. Assume the action is possible.</p>',
         ROBOT + '''
def result(action, s):
    # your code here
    pass
''', [("result('Go(B)', {'robot': 'A', 'gold': 'B', 'holding': False})", {'robot': 'B', 'gold': 'B', 'holding': False}),
      ("result('Grab', {'robot': 'B', 'gold': 'B', 'holding': False})", {'robot': 'B', 'gold': 'B', 'holding': True}),
      ("result('Go(A)', {'robot': 'B', 'gold': 'B', 'holding': True})", {'robot': 'A', 'gold': 'A', 'holding': True}),
      ("result('Release', {'robot': 'A', 'gold': 'A', 'holding': True})", {'robot': 'A', 'gold': 'A', 'holding': False})],
         ROBOT + '''
def result(action, s):
    robot = s["robot"]
    if action.startswith("Go"):
        robot = action[3]
    gold = s["gold"]
    if s["holding"] and action.startswith("Go"):
        gold = robot
    holding = action == "Grab" or (s["holding"] and action != "Release")
    return {"robot": robot, "gold": gold, "holding": holding}
''', 'Compute each fluent on its own: robot from Go, gold from robot when holding and moving, holding from Grab and Release.', '<p>Test 3 is the ramification: the held gold moves with the robot.</p>')
K.assign('check', 'm', 'Check a plan with possibility axioms',
         '<p>Write <code>run_plan(s, plan)</code>. For each action, if it is not possible (Grab needs the robot and the gold in the same room and not holding, Release needs holding, Go is always possible), return None. Otherwise apply it. Return the final state. The starter gives a correct <code>result</code>.</p>',
         ROBOT + '''
def result(action, s):
    robot = action[3] if action.startswith("Go") else s["robot"]
    gold = robot if s["holding"] and action.startswith("Go") else s["gold"]
    holding = action == "Grab" or (s["holding"] and action != "Release")
    return {"robot": robot, "gold": gold, "holding": holding}

def run_plan(s, plan):
    # your code here
    pass
''', [("run_plan({'robot': 'A', 'gold': 'B', 'holding': False}, ['Go(B)', 'Grab', 'Go(A)', 'Release'])", {'robot': 'A', 'gold': 'A', 'holding': False}),
      ("run_plan({'robot': 'A', 'gold': 'B', 'holding': False}, ['Grab'])", None),
      ("run_plan({'robot': 'A', 'gold': 'A', 'holding': False}, ['Release'])", None),
      ("run_plan({'robot': 'A', 'gold': 'B', 'holding': False}, [])", {'robot': 'A', 'gold': 'B', 'holding': False})],
         ROBOT + '''
def result(action, s):
    robot = action[3] if action.startswith("Go") else s["robot"]
    gold = robot if s["holding"] and action.startswith("Go") else s["gold"]
    holding = action == "Grab" or (s["holding"] and action != "Release")
    return {"robot": robot, "gold": gold, "holding": holding}

def possible(action, s):
    if action == "Grab":
        return s["gold"] == s["robot"] and not s["holding"]
    if action == "Release":
        return s["holding"]
    return True

def run_plan(s, plan):
    for action in plan:
        if not possible(action, s):
            return None
        s = result(action, s)
    return s
''', 'Write possible(action, s) from the possibility axioms, then loop over the plan.', '<p>An empty plan returns the start state unchanged.</p>')
K.assign('find', 'h', 'Find the shortest plan',
         '<p>Write <code>find_plan(s, goal_gold)</code>: a shortest list of actions after which the gold lies in room goal_gold and is not held. Use breadth first search over states, trying actions in the order of ACTIONS, and skip actions that are not possible. Return [] if the goal already holds.</p>',
         ROBOT + '''
def result(action, s):
    robot = action[3] if action.startswith("Go") else s["robot"]
    gold = robot if s["holding"] and action.startswith("Go") else s["gold"]
    holding = action == "Grab" or (s["holding"] and action != "Release")
    return {"robot": robot, "gold": gold, "holding": holding}

def possible(action, s):
    if action == "Grab":
        return s["gold"] == s["robot"] and not s["holding"]
    if action == "Release":
        return s["holding"]
    return True

def find_plan(s, goal_gold):
    # your code here
    pass
''', [("find_plan({'robot': 'A', 'gold': 'B', 'holding': False}, 'A')", ['Go(B)', 'Grab', 'Go(A)', 'Release']),
      ("find_plan({'robot': 'B', 'gold': 'B', 'holding': False}, 'A')", ['Grab', 'Go(A)', 'Release']),
      ("find_plan({'robot': 'A', 'gold': 'A', 'holding': False}, 'A')", []),
      ("find_plan({'robot': 'A', 'gold': 'A', 'holding': True}, 'B')", ['Go(B)', 'Release'])],
         ROBOT + '''
def result(action, s):
    robot = action[3] if action.startswith("Go") else s["robot"]
    gold = robot if s["holding"] and action.startswith("Go") else s["gold"]
    holding = action == "Grab" or (s["holding"] and action != "Release")
    return {"robot": robot, "gold": gold, "holding": holding}

def possible(action, s):
    if action == "Grab":
        return s["gold"] == s["robot"] and not s["holding"]
    if action == "Release":
        return s["holding"]
    return True

def find_plan(s, goal_gold):
    queue = [(s, [])]
    seen = [s]
    while queue:
        state, plan = queue.pop(0)
        if state["gold"] == goal_gold and not state["holding"]:
            return plan
        for a in ACTIONS:
            if possible(a, state):
                t = result(a, state)
                if t not in seen:
                    seen.append(t)
                    queue.append((t, plan + [a]))
    return None
''', 'Keep a queue of (state, plan) pairs and a list of seen states. Test the goal when you take a state from the queue.', '<p>Breadth first search returns a shortest plan because it looks at all plans of length k before any of length k + 1.</p>')

K.must('Situations', 'S0, Result(a, s). Fluents take s as last argument. Atemporal predicates do not.')
K.must('Axioms', 'Possibility: Poss(a, s) ⇔ preconditions. Effect: Poss(a, s) ⇒ effect in Result(a, s).')
K.must('Frame problem', 'Effect axioms do not say what stays. A × F frame axioms, or F successor state axioms (Reiter).')
K.must('SSA form', 'F(Result(a, s)) ⇔ a made F true ∨ (F(s) ∧ a did not make F false). Needs unique action axioms.')
K.must('Deductive planning', 'Green 1969: prove ∃s Goal(s), extract s. Slow, so STRIPS (1971).')

T = K.topic(
    slug='situation-calculus', topic='situation-calculus', step=(8, 'Planning', 'cai-planning', 'Find a sequence of actions with logic: situation calculus, deductive planning, STRIPS, sub goals and partial order planning.', 'College'),
    title='Situation calculus and deductive planning', short='Situation calculus', badge='8.1', minutes=45,
    lead='Describe a changing world in logic and plan by proving theorems. Learn situations, fluents and action axioms, see the frame problem and how successor state axioms solve it, and extract a plan from a proof.',
    desc='What classical planning is, planning languages, situation calculus with S0, Result and fluents, possibility and effect axioms, the frame, qualification and ramification problems, successor state axioms and unique action axioms, Green\'s deductive planning with answer extraction, and why STRIPS followed.',
    summary='Situations, fluents, action axioms, the frame problem, successor state axioms and deductive planning.',
    keywords=['situation calculus', 'fluent', 'frame problem', 'successor state axiom', 'deductive planning', 'Green', 'Reiter', 'possibility axiom'],
    recap='<p>Situation calculus describes change in FOL. Successor state axioms solve the frame problem. A proof of ∃s Goal(s) gives a plan.</p>',
    nb={'ssa': 'Successor state axioms on a plan', 'green': 'Finding the plan term by search'})
