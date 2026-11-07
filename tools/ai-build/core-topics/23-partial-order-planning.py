# Chapter 8.3: partial order planning. The uploaded slides and transcripts do not cover planning, so this chapter
# follows Russell and Norvig, AIMA 2nd ed. section 11.3 and 3rd ed. section 10.4.4, Weld (1994), McAllester and
# Rosenblitt (1991) and Penberthy and Weld (1992). Every plan and count in it was checked by running the code of
# this chapter and the pop animation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('lin', r'''
# A partial order plan keeps only the orderings it needs. Count the total orders (linearizations) it allows.
steps = ["RightSock", "RightShoe", "LeftSock", "LeftShoe"]
before = [("RightSock", "RightShoe"), ("LeftSock", "LeftShoe")]   # (a, b) means a must come before b

def linearize(done, left):
    if not left:
        return [done]
    out = []
    for s in left:
        ready = True
        for a, b in before:
            if b == s and a in left:      # a must come first but has not been placed
                ready = False
        if ready:
            rest = [x for x in left if x != s]
            out = out + linearize(done + [s], rest)
    return out

orders = linearize([], steps)
print("total orders allowed:", len(orders))
for o in orders:
    print("  ", ", ".join(o))
''')

K.code('pop', r'''
# A small partial order planner: steps, orderings and causal links, with threats fixed by promotion or demotion.
acts = {"Remove(Spare, Trunk)": (["At(Spare, Trunk)"], ["At(Spare, Ground)"], ["At(Spare, Trunk)"]),
        "Remove(Flat, Axle)": (["At(Flat, Axle)"], ["At(Flat, Ground)", "Free(Axle)"], ["At(Flat, Axle)"]),
        "PutOn(Spare, Axle)": (["At(Spare, Ground)", "Free(Axle)"], ["At(Spare, Axle)"], ["At(Spare, Ground)", "Free(Axle)"])}
acts["Start"] = ([], ["At(Flat, Axle)", "At(Spare, Trunk)"], [])     # (pre, add, del)
acts["Finish"] = (["At(Spare, Axle)"], [], [])

def after(order, a, b):              # is a forced to come after b (b before a)?
    seen, todo = [], [b]
    while todo:
        x = todo.pop()
        for p, q in order:
            if p == x and q not in seen:
                seen.append(q)
                todo.append(q)
    return a in seen

def pop(plan, order, links, agenda):
    if not agenda:
        return plan, order
    p, need = agenda[0]
    for s in plan + [a for a in acts if a not in plan]:
        if p not in acts[s][1] or after(order, s, need) or s == need:
            continue
        new_plan = plan + [s] if s not in plan else plan
        new_order = order + [(s, need)]
        new_agenda = agenda[1:] + ([(q, s) for q in acts[s][0]] if s not in plan else [])
        new_links = links + [(s, p, need)]
        ok = True
        for a, f, b in new_links:            # fix every threat: a step that deletes f could run between a and b
            for t in new_plan:
                if f in acts[t][2] and t != a and t != b and not after(new_order, a, t) and not after(new_order, t, b):
                    if not after(new_order, t, a) and t != "Start":
                        new_order = new_order + [(t, a)]      # demotion: t before a
                    elif not after(new_order, b, t) and b != "Finish":
                        new_order = new_order + [(b, t)]      # promotion: t after b
                    else:
                        ok = False
        if ok:
            print("link", s, "--", p, "->", need)
            result = pop(new_plan, new_order, new_links, new_agenda)
            if result:
                return result
    return None

plan, order = pop(["Start", "Finish"], [("Start", "Finish")], [], [("At(Spare, Axle)", "Finish")])
print("steps:", [s for s in plan if s not in ("Start", "Finish")])
''')

K.lesson('partial', 'Partial plans: steps, orderings and causal links', f'''
{src('Russell and Norvig, AIMA 3rd ed., section 10.4.4, and AIMA 2nd ed., section 11.3, which gives the full algorithm used here. Sacerdoti (1975) and Tate (1977) built the first planners of this kind.')}
{wwh('A <b>partial order plan</b> is a set of steps with only the orderings that are really needed. It has four parts: the steps, ordering constraints (A ≺ B means A comes before B), causal links (A gives fact p to B, written A →p→ B), and open preconditions (facts some step needs that no link supplies yet).',
     'State space planners fix the full order of every action, even when the order does not matter. Fixing an order too early can force the planner to undo work later. Leaving steps unordered until a clash appears is called <b>least commitment</b>, and it handles sub goals that interact, such as the Sussman anomaly.',
     'Start with two dummy steps. Start has the initial state as its effects. Finish has the goal as its preconditions. Then repeat: pick an open precondition, add or reuse a step that achieves it, record a causal link and an ordering, and protect every link from steps that could undo it.')}
{table(['Part', 'Meaning', 'Socks and shoes example'], [
    ['Steps', 'actions in the plan, plus Start and Finish', 'RightSock, RightShoe, LeftSock, LeftShoe'],
    ['Ordering A ≺ B', 'A must run before B', 'RightSock ≺ RightShoe'],
    ['Causal link A →p→ B', 'A makes p true for B, and nothing may undo p between them', 'RightSock →RightSockOn→ RightShoe'],
    ['Open precondition', 'a precondition with no causal link yet', 'at the start: RightShoeOn and LeftShoeOn of Finish']])}
{viz('pop', dom='socks')}
<p>The finished plan says only that each sock goes on before its shoe. Any total order that keeps those two rules is a valid plan. Such a total order is called a <b>linearization</b> of the partial plan.</p>
{code('lin')}
{note('A partial plan is <b>consistent</b> when its orderings have no cycle (A ≺ B and B ≺ A cannot both hold) and no causal link is threatened. A consistent plan with no open preconditions is a <b>solution</b>: every linearization of it reaches the goal.', 'tip')}
''', kw=['partial order plan', 'least commitment', 'causal link', 'ordering constraint', 'open precondition', 'linearization', 'Start and Finish'])

K.lesson('threats', 'Threats, promotion and demotion', f'''
{src('AIMA 2nd ed., section 11.3, and McAllester and Rosenblitt, 1991 (SNLP).')}
{wwh('A step C <b>threatens</b> the causal link A →p→ B when C deletes p and the orderings allow C to run after A and before B. If C ran there, B would no longer have p.',
     'Causal links are the promises a partial plan makes. A threat can break a promise, so the plan would fail in some of its linearizations.',
     'Fix a threat by adding one ordering. <b>Demotion</b> puts C before A (C ≺ A). <b>Promotion</b> puts C after B (B ≺ C). Keep the fix only if the orderings still have no cycle. If neither works, the planner goes back and tries another choice.')}
{fxs(fx('Threat', 'C deletes p, and neither C ≺ A nor B ≺ C follows from the orderings', 'C could sit between A and B.', key=True),
     fx('Demotion', 'add C ≺ A', 'C runs before p is made.'),
     fx('Promotion', 'add B ≺ C', 'C runs after p is used.'))}
{viz('pop', dom='tire')}
{code('pop')}
{steps('Worked example from the Sussman anomaly animation', [
    'Link: Start →Clear(C)→ MoveToTable(C, A). MoveToTable(C, A) needs C to be clear.',
    'New step Move(B, Table, C) deletes Clear(C), and nothing yet orders it.',
    'Demotion would put Move(B, Table, C) before Start, which is not allowed: Start is always first.',
    'Promotion puts it after MoveToTable(C, A). The orderings stay free of cycles.',
    eq('MoveToTable(C, A) ≺ Move(B, Table, C)')])}
{note('Some textbooks add a third fix for lifted plans with variables: <b>separation</b>, a constraint such as x ≠ C that stops the threatening step from deleting this exact fact.', 'tip')}
''', kw=['threat', 'clobbering', 'promotion', 'demotion', 'separation', 'protected link'])

K.lesson('algorithm', 'The POP algorithm', f'''
{src('AIMA 2nd ed., section 11.3, Penberthy and Weld, 1992 (UCPOP), and Weld, 1994, An Introduction to Least Commitment Planning.')}
{algo('POP (partial order planner)', [
    'plan = steps {Start, Finish}, orderings {Start ≺ Finish}, links { }',
    'agenda = every precondition of Finish',
    'loop:',
    '    if the agenda is empty: return plan',
    '    pick an open precondition p of step B from the agenda',
    '    choose a step A that adds p (an old step, or a new one from the schemas)',
    '        if A is new: add A, add Start ≺ A ≺ Finish, put the preconditions of A on the agenda',
    '        add the causal link A →p→ B and the ordering A ≺ B',
    '    for every threat C to any link A →q→ B:',
    '        choose demotion (C ≺ A) or promotion (B ≺ C) if it keeps the orderings free of cycles',
    '        if neither works: fail and go back to the last choice'])}
<p>There are two kinds of choices. Picking which open precondition to work on next does not need going back: every one must be solved in the end. Choosing the achieving step and the threat fix does need going back, so POP is a search over partial plans.</p>
{viz('pop', dom='sussman')}
{steps('Why POP solves the Sussman anomaly', [
    'It adds Move(A, Table, B) for On(A, B) and MoveToTable(C, A) to clear A, with no order against the B steps yet.',
    'It adds Move(B, Table, C) for On(B, C). This step deletes Clear(C), which MoveToTable(C, A) needs, so it is promoted after MoveToTable(C, A).',
    'Move(A, Table, B) deletes Clear(B), which Move(B, Table, C) needs, so it is promoted after Move(B, Table, C).',
    eq('plan: MoveToTable(C, A), Move(B, Table, C), Move(A, Table, B), 3 actions')])}
{note('POP is <b>sound</b> (every plan it returns works) and <b>complete</b> (it finds a plan if one exists) when the step and threat choices are searched fully, for example breadth first or with iterative deepening on the number of steps. The animation uses iterative deepening, so it reports the step limit it needed.', 'tip')}
''', kw=['POP algorithm', 'agenda', 'soundness', 'completeness', 'choice points', 'UCPOP', 'Sussman anomaly'])

K.lesson('maths', 'The maths: counting orders and checking threats', f'''
{fxs(
    fx('Linearizations of independent chains', '(n₁ + n₂ + ... + n_k)! ÷ (n₁! n₂! ... n_k!)', 'k chains of steps, chain i has n_i steps in a fixed order, and the chains do not constrain each other. This is the multinomial coefficient.', key=True),
    fx('Two chains of length 2', '4! ÷ (2! × 2!) = 24 ÷ 4 = 6', 'The socks and shoes plan allows 6 total orders.'),
    fx('Steps with no orderings at all', 'n!', 'Every order is allowed.'),
    fx('Causal links in a finished plan', 'number of links = total number of preconditions of all steps (including Finish)', 'Each precondition gets exactly one link.'),
    fx('Cost of one threat check', 'links × steps pairs, each needing a reachability test in the ordering graph', 'Reachability is a graph search, about O(steps + orderings) each time.'))}
{steps('Worked example: count the causal links in the finished Sussman plan', [
    'Finish needs On(A, B) and On(B, C): 2 preconditions.',
    'Move(A, Table, B) needs On(A, Table), Clear(A), Clear(B): 3.',
    'MoveToTable(C, A) needs On(C, A), Clear(C): 2.',
    'Move(B, Table, C) needs On(B, Table), Clear(B), Clear(C): 3.',
    eq('2 + 3 + 2 + 3 = 10 causal links')])}
{steps('Worked example: socks, shoes and gloves', [
    'Sock then shoe on the right is a chain of 2 steps. Sock then shoe on the left is another chain of 2. The two gloves need no order, so each glove is a chain of 1 step.',
    'Chains have lengths 2, 2, 1, 1. Total steps: 6.',
    '6! = 720. Divide by 2! × 2! × 1! × 1! = 4.',
    eq('720 ÷ 4 = 180 total orders')])}
''', kw=['linearizations', 'multinomial coefficient', 'number of causal links', 'threat check cost', 'reachability'])

K.lesson('compare', 'POP compared with other planners', f'''
{versus('Partial order planning and its neighbours', ['', 'Partial order planning', 'Forward state search with heuristics', 'Linear sub goal planning', 'GraphPlan', 'Hierarchical task networks (HTN)'], [
    ['Searches over', 'partial plans', 'world states', 'one sub goal at a time', 'a layered planning graph', 'ways to break big tasks into smaller ones'],
    ['Plan form', 'partial order, flexible', 'total order', 'total order', 'layers of parallel actions', 'partial or total order'],
    ['Interacting sub goals', 'handled by threat fixes', 'handled by search', 'often fails or gives long plans', 'handled by mutex links', 'handled by the method author'],
    ['Speed today', 'slower on large problems', 'fastest general method (FF, Fast Downward)', 'fast but incomplete', 'good on small parallel problems', 'very fast with good methods'],
    ['Best use', 'flexible plans to explain or to run in parallel', 'large benchmark problems', 'teaching, independent goals', 'parallel plans, heuristics', 'real systems with expert knowledge']],
    'POP lost the speed race in the late 1990s, but RePOP (Nguyen and Kambhampati, 2001) showed that state space heuristics make it competitive again. Its plans are easy to explain and to run with several agents.')}
{scene('Where partial order plans are used', '<p>NASA spacecraft and rover planners such as the Remote Agent on Deep Space 1 (1999) used plans with flexible timing, a direct descendant of partial order planning. Plans that people carry out, such as maintenance procedures and project schedules, keep only the orderings that matter so that work can run in parallel. Multi robot systems use partial orders so that each robot can move as soon as its own steps are ready.</p>')}
''', kw=['comparison', 'RePOP', 'GraphPlan', 'HTN', 'hierarchical planning', 'Remote Agent', 'parallel plans'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Getting dressed: you must put a sock on before its shoe, but you can do the left or right foot first. A partial order plan writes down only the "before" rules that matter.</p>',
    '<p>A partial plan has steps, orderings, causal links and open preconditions. POP closes open preconditions with causal links and fixes threats by demotion or promotion. A plan is a solution when it has no open preconditions, no threats and no ordering cycles.</p>',
    '<p>Chapman (1987) gave the Modal Truth Criterion for his planner TWEAK, an exact test of when a fact must hold at a point of a partial plan, and showed that such tests become intractable for richer action languages. SNLP (McAllester and Rosenblitt, 1991) made the search systematic, so no partial plan is visited twice. UCPOP (Penberthy and Weld, 1992) added variables, conditional effects and universal quantifiers.</p>',
    '<p>Research: temporal planners with simple temporal networks keep flexible start times. Plan repair and plan explanation reuse causal links. Large language models are now tested on producing partial order plans, with a classical planner or validator such as VAL used to check them.</p>')}
''', kw=['TWEAK', 'Modal Truth Criterion', 'SNLP', 'UCPOP', 'temporal planning', 'simple temporal network', 'plan repair'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A partial order plan has steps, ordering constraints, causal links and open preconditions. Start gives the initial state and Finish needs the goal.',
    'POP picks an open precondition, adds or reuses a step that achieves it, and records a causal link and an ordering.',
    'A step threatens a causal link A →p→ B if it deletes p and could run between A and B. Fix it by demotion (before A) or promotion (after B).',
    'Least commitment: steps stay unordered until a threat forces an order. This solves the Sussman anomaly with 3 actions.',
    'A finished plan stands for all its linearizations. Independent chains of lengths n₁, ..., n_k give (Σ n_i)! ÷ Π n_i! orders.'],
    'step 9 moves from plans to beliefs: probability, Bayesian networks and reasoning under uncertainty.')}
{nbcard('partial-order-planning', 'Count the linearizations of a partial plan and run a small partial order planner on the spare tyre problem, then write a cycle check, a threat fixer and an order counter yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A causal link A →p→ B means', ['A and B both add p', 'A makes p true, B needs p, and p must stay true between them', 'B comes before A', 'p is in the initial state'], 1,
       'A promise.', 'A supplies p to B, and no step may delete p in between.')
K.quiz('e', 'The Start step of a partial plan has as its effects', ['the goal', 'the initial state', 'nothing', 'every action'], 1,
       'Where the world begins.', 'Finish has the goal as its preconditions.')
K.quiz('e', 'Least commitment means', ['use as few actions as possible', 'add an ordering only when it is needed', 'never go back', 'pick the cheapest action'], 1,
       'Do not decide too early.', 'Steps stay unordered until a clash forces an order.')
K.quiz('e', 'In the socks and shoes plan, which order is required?', ['RightSock before LeftSock', 'each sock before its own shoe', 'both socks before both shoes', 'no order at all'], 1,
       'Look at the causal links.', 'Left and right stay unordered.')
K.quiz('m', 'A step C threatens the link A →p→ B when', ['C adds p', 'C deletes p and could run between A and B', 'C comes after B', 'C needs p'], 1,
       'It could break the link.', 'If C must run before A or after B, there is no threat.')
K.quiz('m', 'Demotion fixes a threat C to the link A →p→ B by adding', ['C ≺ A', 'B ≺ C', 'A ≺ B', 'a new link'], 0,
       'Move C down, to before A.', 'Promotion adds B ≺ C.')
K.quiz('m', 'A partial plan is a solution when', ['it has a Finish step', 'it has no open preconditions, no threats and no ordering cycles', 'it has one linearization', 'it uses all actions'], 1,
       'All three conditions.', 'Then every linearization reaches the goal.')
K.quiz('m', 'Which choice in POP never needs going back?', ['which step achieves p', 'which open precondition to work on next', 'promotion or demotion', 'none'], 1,
       'Every open precondition must be closed anyway.', 'The other two are real choice points.')
K.quiz('h', 'Why can demotion never place a step before Start?', ['Start has no effects', 'Start must come before every other step', 'Start is a goal', 'it can'], 1,
       'Start is first.', 'So a threat to a link that starts at Start can only be fixed by promotion.')
K.quiz('h', 'How many linearizations does a plan with two independent chains of 3 steps each have?', ['6', '9', '20', '36'], 2,
       '6! ÷ (3! × 3!).', '720 ÷ 36 = 20.')
K.quiz('x', 'In the style of a Stanford CS221 exam: in the spare tyre problem, why does POP never add LeaveOvernight?', ['It has no preconditions', 'It deletes facts that causal links need, and it adds nothing an open precondition needs', 'It is too expensive', 'It is not a STRIPS action'], 1,
       'POP adds a step only to close an open precondition.', 'LeaveOvernight achieves nothing, so it is never chosen as an achiever.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: SNLP differs from earlier partial order planners because', ['it ignores threats', 'it is systematic: it never visits the same partial plan twice, since every link also protects against steps that add p again', 'it uses state space search', 'it has no Finish step'], 1,
       'McAllester and Rosenblitt, 1991.', 'SNLP treats a step that adds or deletes p between A and B as a threat, which makes the search tree free of repeats.')

# ---------------------------------------------------------------- calc
K.calc('e', 'Linearizations of the socks and shoes plan: two chains of 2 steps.', '6', '4! ÷ (2! × 2!).',
       ['4! = 24.', '2! × 2! = 4.', eq('24 ÷ 4 = 6')], check=6)
K.calc('e', 'Three steps with no orderings between them. How many total orders?', '6', '3!.',
       ['3 choices for the first step.', '2 for the second, 1 for the last.', eq('3 × 2 × 1 = 6')], check=6)
K.calc('e', 'Causal links in the finished socks and shoes plan (Start has no effects).', '4', 'One link for each precondition.',
       ['Finish needs 2 facts: 2 links.', 'Each shoe needs its sock: 2 links.', eq('2 + 2 = 4')], check=4)
K.calc('m', 'Two chains: one with 3 steps, one with 2. How many linearizations?', '10', '5! ÷ (3! × 2!).',
       ['5! = 120.', '3! × 2! = 12.', eq('120 ÷ 12 = 10')], check=10)
K.calc('m', 'Causal links in the finished spare tyre plan.', '5', 'Count all preconditions, Finish included.',
       ['Finish: At(Spare, Axle). 1.', 'PutOn(Spare, Axle): At(Spare, Ground), Free(Axle). 2.', 'Each Remove: 1 precondition, so 2.', eq('1 + 2 + 2 = 5')], check=5)
K.calc('m', 'Linearizations of the finished spare tyre plan (both Remove steps before PutOn, the two Remove steps unordered).', '2', 'Only the first two steps can swap.',
       ['PutOn(Spare, Axle) must be last.', 'Remove(Spare, Trunk) and Remove(Flat, Axle) can go in either order.', eq('2! = 2')], check=2)
K.calc('m', 'Causal links in the finished Sussman plan.', '10', 'Finish 2, Move(A, Table, B) 3, MoveToTable(C, A) 2, Move(B, Table, C) 3.',
       ['Finish: 2.', 'Move(A, Table, B): 3. MoveToTable(C, A): 2.', 'Move(B, Table, C): 3.', eq('10')], check=10)
K.calc('h', 'Three pairs of steps (sock then shoe on each of two feet, and a shirt then a jacket). How many linearizations?', '90', '6! ÷ (2! × 2! × 2!).',
       ['6! = 720.', '2! × 2! × 2! = 8.', eq('720 ÷ 8 = 90')], check=90)
K.calc('h', 'Socks and shoes, plus two gloves that need no order. How many linearizations?', '180', 'Chains of lengths 2, 2, 1, 1.',
       ['6! = 720.', 'Divide by 2! × 2! × 1! × 1! = 4.', eq('180')], check=180)
K.calc('x', 'A plan has 4 causal links and 6 steps (Start and Finish included). How many (step, link) pairs must a full threat check test?', '24', 'Every step against every link.',
       ['Each of the 4 links.', 'Is tested against each of the 6 steps.', eq('4 × 6 = 24 pairs')], check=24)

# ---------------------------------------------------------------- assignments
K.assign('consistent', 'e', 'Check that orderings have no cycle',
         '<p>before is a list of pairs (a, b) meaning a ≺ b. Write <code>consistent(before)</code> that returns True if no step must come before itself, and False if the orderings have a cycle.</p>',
         '''
def consistent(before):
    # your code here
    pass
''', [("consistent([('A', 'B'), ('B', 'C')])", True),
      ("consistent([('A', 'B'), ('B', 'A')])", False),
      ("consistent([('A', 'B'), ('B', 'C'), ('C', 'A')])", False),
      ("consistent([])", True)],
         '''
def consistent(before):
    steps = []
    for a, b in before:
        if a not in steps:
            steps.append(a)
        if b not in steps:
            steps.append(b)
    for s in steps:
        seen = []
        todo = [s]
        while todo:
            x = todo.pop()
            for a, b in before:
                if a == x and b not in seen:
                    seen.append(b)
                    todo.append(b)
        if s in seen:
            return False
    return True
''', 'For every step, follow the pairs forward and see whether you come back to the same step.', '<p>Test 3 has the cycle A ≺ B ≺ C ≺ A.</p>')
K.assign('fix', 'm', 'Fix a threat by demotion or promotion',
         '<p>Step t threatens the causal link from a to b. Write <code>fix(t, a, b, before)</code>. Try demotion first: if adding (t, a) keeps the orderings free of cycles, return "demotion". Otherwise try promotion with (b, t) and return "promotion". If both make a cycle, return None. You may copy your consistent function into the cell.</p>',
         '''
def consistent(before):
    # paste your answer from the last task
    pass

def fix(t, a, b, before):
    # your code here
    pass
''', [("fix('T', 'A', 'B', [('A', 'B')])", 'demotion'),
      ("fix('T', 'A', 'B', [('A', 'B'), ('A', 'T')])", 'promotion'),
      ("fix('T', 'A', 'B', [('A', 'T'), ('T', 'B')])", None),
      ("fix('T', 'Start', 'B', [('Start', 'A'), ('A', 'B'), ('Start', 'T')])", 'promotion')],
         '''
def consistent(before):
    steps = []
    for a, b in before:
        if a not in steps:
            steps.append(a)
        if b not in steps:
            steps.append(b)
    for s in steps:
        seen = []
        todo = [s]
        while todo:
            x = todo.pop()
            for a, b in before:
                if a == x and b not in seen:
                    seen.append(b)
                    todo.append(b)
        if s in seen:
            return False
    return True

def fix(t, a, b, before):
    if consistent(before + [(t, a)]):
        return "demotion"
    if consistent(before + [(b, t)]):
        return "promotion"
    return None
''', 'Add the new pair to a copy of the list and test it with consistent.', '<p>Test 3: t is already forced between a and b, so the threat cannot be fixed and the planner must go back. Test 4: demotion would put T before Start, which makes a cycle with Start ≺ T.</p>')
K.assign('orders', 'h', 'Count the linearizations of a partial plan',
         '<p>Write <code>count_orders(steps, before)</code> that returns how many total orders of the steps respect every pair (a, b) in before.</p>',
         '''
def count_orders(steps, before):
    # your code here
    pass
''', [("count_orders(['RS', 'RH', 'LS', 'LH'], [('RS', 'RH'), ('LS', 'LH')])", 6),
      ("count_orders(['A', 'B', 'C', 'D', 'E'], [('A', 'B'), ('B', 'C'), ('D', 'E')])", 10),
      ("count_orders(['A', 'B', 'C'], [])", 6),
      ("count_orders(['A', 'B', 'C'], [('A', 'B'), ('B', 'C')])", 1)],
         '''
def count_orders(steps, before):
    if len(steps) == 0:
        return 1
    total = 0
    for s in steps:
        ready = True
        for a, b in before:
            if b == s and a in steps:
                ready = False
        if ready:
            rest = []
            for x in steps:
                if x != s:
                    rest.append(x)
            total = total + count_orders(rest, before)
    return total
''', 'Pick any step whose required earlier steps are all placed, then count the orders of the rest. Add up over all such choices.', '<p>Test 2 has chains of 3 and 2 steps: 5! ÷ (3! × 2!) = 10.</p>')

K.must('Partial plan', 'Steps, orderings A ≺ B, causal links A →p→ B, open preconditions. Start gives the initial state, Finish needs the goal.')
K.must('Threat', 'C deletes p and could run between A and B of the link A →p→ B.')
K.must('Fixes', 'Demotion: C ≺ A. Promotion: B ≺ C. Keep the orderings free of cycles, else go back.')
K.must('Solution', 'No open preconditions, no threats, no cycles. Every linearization then reaches the goal.')
K.must('Counting', 'Independent chains n₁, ..., n_k give (Σ n_i)! ÷ Π n_i! linearizations. Socks and shoes: 6.')
K.must('Sussman by POP', 'MoveToTable(C, A) ≺ Move(B, Table, C) ≺ Move(A, Table, B), found by two promotions.')

T = K.topic(
    slug='partial-order-planning', topic='partial-order-planning', step=(8, 'Planning', 'cai-planning', 'Find a sequence of actions with logic: situation calculus, deductive planning, STRIPS, sub goals and partial order planning.', 'College'),
    title='Partial order planning', short='Partial order planning', badge='8.3', minutes=50,
    lead='Build plans that order steps only when they must. Learn causal links, threats, promotion and demotion, and watch the partial order planner solve socks and shoes, the spare tyre and the Sussman anomaly.',
    desc='Partial order plans with steps, ordering constraints, causal links and open preconditions, least commitment, linearizations, threats, promotion, demotion and separation, the POP algorithm with its choice points, soundness and completeness, the Sussman anomaly, counting linearizations with the multinomial coefficient, and the history from NOAH and TWEAK to SNLP, UCPOP and RePOP.',
    summary='Partial order plans, causal links, threats, promotion and demotion, and the POP algorithm.',
    keywords=['partial order planning', 'POP', 'causal link', 'threat', 'promotion', 'demotion', 'least commitment', 'linearization', 'SNLP', 'UCPOP'],
    recap='<p>Order steps only when a threat forces it. Fix threats by demotion or promotion. A solution has no open preconditions and no threats.</p>',
    nb={'lin': 'Counting the linearizations of socks and shoes', 'pop': 'A small partial order planner on the spare tyre'})
