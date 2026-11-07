# Chapter 10.1: Markov decision processes. The uploaded slides and transcripts do not cover this step, so it follows
# AIMA 3rd ed. chapter 17 (4th ed. chapter 16), Bellman (1957) and Howard (1960). The racing car MDP is from Berkeley
# CS188. Every number in this chapter was checked by running its code and the gridmdp animation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP10 = (10, 'Reinforcement learning', 'cai-rl', 'Decide over time and learn from rewards: Markov decision processes, policies, Q-values, passive and active reinforcement learning, and policy search.', 'College')

K.code('vi', r'''
# Value iteration on the racing car MDP (Berkeley CS188). The car can be cool or warm. Overheated ends the race.
# T[state][action] is a list of (probability, next state, reward).
T = {"cool": {"slow": [(1.0, "cool", 1)],
              "fast": [(0.5, "cool", 2), (0.5, "warm", 2)]},
     "warm": {"slow": [(0.5, "cool", 1), (0.5, "warm", 1)],
              "fast": [(1.0, "over", -10)]}}
gamma = 0.9
V = {"cool": 0.0, "warm": 0.0, "over": 0.0}

for k in range(1, 4):
    new = {"over": 0.0}
    for s in T:
        best = None
        for a in T[s]:
            q = sum(p * (r + gamma * V[s2]) for p, s2, r in T[s][a])
            if best is None or q > best:
                best = q
        new[s] = best
    V = new
    print("after sweep", k, ":", {s: round(V[s], 3) for s in ["cool", "warm"]})
''')

K.code('pi', r'''
# Policy iteration on the same racing car MDP. Policy evaluation solves two linear equations exactly.
T = {"cool": {"slow": [(1.0, "cool", 1)],
              "fast": [(0.5, "cool", 2), (0.5, "warm", 2)]},
     "warm": {"slow": [(0.5, "cool", 1), (0.5, "warm", 1)],
              "fast": [(1.0, "over", -10)]}}
g = 0.9

def evaluate(pi):
    # V(s) = sum p (r + g V(s')). Write it as a V(cool) + b V(warm) = c for each state, then solve.
    rows = []
    for s in ["cool", "warm"]:
        a_c, a_w, c = 0.0, 0.0, 0.0
        for p, s2, r in T[s][pi[s]]:
            c = c + p * r
            if s2 == "cool":
                a_c = a_c + g * p
            if s2 == "warm":
                a_w = a_w + g * p
        rows.append((a_c, a_w, c))
    (p1, q1, c1), (p2, q2, c2) = rows
    # (1 - p1) Vc - q1 Vw = c1 and -p2 Vc + (1 - q2) Vw = c2
    det = (1 - p1) * (1 - q2) - q1 * p2
    vc = (c1 * (1 - q2) + q1 * c2) / det
    vw = ((1 - p1) * c2 + p2 * c1) / det
    return {"cool": vc, "warm": vw, "over": 0.0}

pi = {"cool": "slow", "warm": "slow"}
while True:
    V = evaluate(pi)
    print("policy", pi, "-> V =", {s: round(V[s], 2) for s in ["cool", "warm"]})
    new = {}
    for s in T:
        new[s] = max(T[s], key=lambda a: sum(p * (r + g * V[s2]) for p, s2, r in T[s][a]))
    if new == pi:
        break
    pi = new
print("optimal policy:", pi)
''')

K.lesson('mdp', 'Markov decision processes', f'''
{src('Bellman (1957), Howard (1960), and AIMA 3rd ed., sections 17.1 to 17.3 (4th ed., 16.1 and 16.2). The 4 × 3 world is AIMA figure 17.1. The racing car example is from Berkeley CS188. The uploaded slides and transcripts do not cover this step.')}
{wwh('A <b>Markov decision process</b> (MDP) is a problem where an agent acts again and again in a world with chance. It has states, actions, a transition model P(s′ | s, a), a reward for each state (or each move), and usually a discount γ. The <b>Markov</b> property says the next state depends only on the current state and action, not on the past.',
     'Search assumed every action has one sure result. Real robots slip, markets move, opponents surprise. A plan as a fixed list of actions breaks the first time something unexpected happens.',
     'Instead of a plan, find a <b>policy</b> π(s): the action to take in every state. The best policy π* gets the highest expected total discounted reward from every state. It is found with the Bellman equation.')}
{table(['Part', '4 × 3 world', 'Racing car'], [
    ['States', '11 squares', 'cool, warm, overheated (end)'],
    ['Actions', 'Up, Down, Left, Right', 'slow, fast'],
    ['Transitions', 'intended move 0.8, each side 0.1', 'cool + fast: cool or warm (0.5 each), warm + fast: overheated'],
    ['Rewards', 'R = −0.04 per step, +1 and −1 at the end squares', 'slow +1, fast +2, overheating −10'],
    ['Discount', 'γ = 1', 'γ = 0.9']])}
{fxs(fx('Utility of a reward sequence', 'U = R₀ + γ R₁ + γ² R₂ + ... = Σ γᵗ Rₜ', 'γ between 0 and 1. With γ < 1 the sum is at most R_max ÷ (1 − γ).', key=True),
     fx('Utility of a state under π', 'U^π(s) = E[Σ γᵗ R(Sₜ) | S₀ = s, actions from π]', 'Expected discounted reward when starting in s.'),
     fx('Optimal policy', 'π*(s) = argmax over a of Σ P(s′ | s, a) U(s′)', 'One step look ahead with the true utilities.'))}
{note('Why discount: a reward now is worth more than the same reward later, an agent may stop at any time, and with γ < 1 infinite sums stay finite. γ close to 1 means a patient agent.', 'tip')}
''', kw=['MDP', 'Markov decision process', 'policy', 'transition model', 'reward', 'discount', 'utility', 'Markov property'])

K.lesson('bellmanl', 'The Bellman equation and value iteration', f'''
{src('Bellman (1957), and AIMA 3rd ed., section 17.2.')}
{wwh('The <b>Bellman equation</b> says the utility of a state is its reward plus the discounted expected utility of the next state, if the agent then acts optimally. <b>Value iteration</b> solves it by repeating the equation as an update until the values stop changing.',
     'There is one equation per state, but the max makes them non linear, so they cannot be solved like ordinary linear equations. Repeating the update always works and is simple.',
     'Start with U(s) = 0. In each sweep, set every U(s) to R(s) + γ max over a of Σ P(s′ | s, a) U(s′), using the old values. Stop when the largest change is small. Then read the policy from the values.')}
{fxs(fx('Bellman equation', 'U(s) = R(s) + γ max over a of Σ over s′ of P(s′ | s, a) U(s′)', 'One equation per state.', key=True),
     fx('Bellman update', 'U_(i+1)(s) ← R(s) + γ max over a of Σ P(s′ | s, a) U_i(s′)', 'Value iteration repeats this.'),
     fx('Contraction', '‖U_(i+1) − U‖ ≤ γ ‖U_i − U‖', 'Each sweep shrinks the error by at least γ (in the max norm), so value iteration always converges for γ < 1.'),
     fx('Stopping rule', 'if ‖U_(i+1) − U_i‖ < ε (1 − γ) ÷ γ then ‖U_(i+1) − U‖ < ε', 'A safe test for "close enough".'))}
{viz('gridmdp', alg='vi')}
{code('vi')}
{steps('Worked example: the first sweep for square (3,3) of the 4 × 3 world', [
    'All utilities start at 0, except the end squares: +1 and −1.',
    'Action Right: 0.8 × U(4,3) + 0.1 × U(3,3) + 0.1 × U(3,2) = 0.8 × 1 + 0 + 0 = 0.8.',
    'No other action does better.',
    eq('U₁(3,3) = −0.04 + 1 × 0.8 = 0.76')])}
''', kw=['Bellman equation', 'Bellman update', 'value iteration', 'contraction', 'convergence', 'stopping rule'])

K.lesson('pil', 'Policy iteration and Q-values', f'''
{src('Howard (1960), Puterman and Shin (1978) for modified policy iteration, and AIMA 3rd ed., section 17.3.')}
{wwh('<b>Policy iteration</b> works with policies, not values. It alternates two steps: policy evaluation (find U^π for the current policy) and policy improvement (change the action in each state to the best one under those values). A <b>Q-value</b> Q(s, a) is the expected utility of taking action a in state s and acting optimally afterwards.',
     'Often the policy becomes optimal long before the values stop changing. Policy iteration stops as soon as the policy stops changing, usually after very few rounds. Q-values let an agent pick the best action without a transition model, which is the key to Q-learning in chapter 10.3.',
     'Evaluation: with the action in each state fixed, the Bellman equations lose the max and become linear, so solve them exactly (or with a few sweeps, as in modified policy iteration). Improvement: π(s) ← argmax over a of Σ P(s′ | s, a) U(s′). Stop when nothing changes.')}
{fxs(fx('Policy evaluation', 'U^π(s) = R(s) + γ Σ P(s′ | s, π(s)) U^π(s′)', 'n linear equations, O(n³) to solve exactly.', key=True),
     fx('Q-value', 'Q(s, a) = Σ P(s′ | s, a) [R(s, a, s′) + γ max over a′ of Q(s′, a′)]', 'U(s) = max over a of Q(s, a).'),
     fx('Termination', 'there are |A|^|S| policies and each round is at least as good as the last', 'So policy iteration ends after a finite number of rounds.'))}
{viz('gridmdp', alg='pi')}
{code('pi')}
{steps('Worked example: evaluate the policy (cool: fast, warm: slow) of the racing car with γ = 0.9', [
    'V(cool) = 0.5 (2 + 0.9 V(cool)) + 0.5 (2 + 0.9 V(warm)) = 2 + 0.45 V(cool) + 0.45 V(warm).',
    'V(warm) = 0.5 (1 + 0.9 V(cool)) + 0.5 (1 + 0.9 V(warm)) = 1 + 0.45 V(cool) + 0.45 V(warm).',
    'Subtract: V(cool) − V(warm) = 1. Put V(cool) = V(warm) + 1 into the second line: V(warm) = 1.45 + 0.9 V(warm).',
    eq('V(warm) = 14.5, V(cool) = 15.5')])}
{deep('Partially observable MDPs', '<p>When the agent cannot see the state, it keeps a <b>belief state</b> b(s), a probability for each state, and updates it with Bayes’s rule after each action and percept. A POMDP is an MDP over belief states, which are continuous, so it is much harder: finding optimal POMDP policies is PSPACE-hard even for finite horizons (Papadimitriou and Tsitsiklis, 1987). Point based value iteration and online search such as POMCP make large POMDPs practical.</p>')}
''', kw=['policy iteration', 'policy evaluation', 'policy improvement', 'modified policy iteration', 'Q-value', 'POMDP', 'belief state'])

K.lesson('maths', 'The maths: bounds and counts', f'''
{fxs(
    fx('Bound on utilities', '|U(s)| ≤ R_max ÷ (1 − γ)', 'Geometric series: R_max (1 + γ + γ² + ...).', key=True),
    fx('Sweeps needed', 'N = ⌈log(2 R_max ÷ (ε (1 − γ))) ÷ log(1 ÷ γ)⌉', 'Enough sweeps for error below ε, starting from 0. It grows fast as γ nears 1.'),
    fx('Policy loss', 'if ‖U_i − U‖ < ε then ‖U^(π_i) − U‖ < 2 ε γ ÷ (1 − γ)', 'The greedy policy is good even before the values have fully converged.'),
    fx('Number of policies', '|A|^|S|', '4 × 3 world: 4⁹ = 262,144 policies for the 9 squares where a choice matters.'))}
{steps('Worked example: two sweeps of value iteration on the racing car (γ = 0.9)', [
    'Sweep 1 (from 0): cool: slow gives 1, fast gives 2, so 2. warm: slow gives 1, fast gives −10, so 1.',
    'Sweep 2, cool, fast: 0.5 (2 + 0.9 × 2) + 0.5 (2 + 0.9 × 1) = 1.9 + 1.45 = 3.35. Slow: 1 + 0.9 × 2 = 2.8. So 3.35.',
    'Sweep 2, warm, slow: 0.5 (1 + 1.8) + 0.5 (1 + 0.9) = 1.4 + 0.95 = 2.35. Fast: −10. So 2.35.',
    eq('V₂(cool) = 3.35, V₂(warm) = 2.35')])}
''', kw=['utility bound', 'number of sweeps', 'policy loss bound', 'number of policies'])

K.lesson('compare', 'MDP solvers compared', f'''
{versus('Solving a known MDP', ['', 'Value iteration', 'Policy iteration', 'Modified policy iteration', 'Linear programming', 'Expectimax search (6.3)'], [
    ['Works on', 'utilities', 'policies', 'policies, with a few sweeps for evaluation', 'utilities as LP variables', 'a tree from the current state'],
    ['Cost per round', 'O(|S|² |A|)', 'O(|S|³) for exact evaluation plus O(|S|² |A|)', 'O(k |S|²) plus O(|S|² |A|)', 'polynomial overall', 'exponential in the depth'],
    ['Rounds', 'many when γ is near 1', 'few', 'few', 'one LP', 'one search per move'],
    ['Best for', 'simple and general', 'small state spaces', 'the usual choice in practice', 'theory: MDPs are solvable in polynomial time', 'huge state spaces, online decisions']],
    'value iteration is the easiest to write, and policy iteration usually needs fewer rounds. All of them need the full model, which reinforcement learning (next chapters) does without.')}
{scene('MDPs in the real world', '<p>MDPs plan maintenance (when to repair a machine as it wears), stock control (how much to order each week), medical treatment plans (when to change a drug), and robot navigation with wheel slip. Airline seat pricing and the energy grid also use dynamic programming over MDP models.</p>')}
''', kw=['comparison', 'linear programming', 'expectimax', 'applications'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A policy is a rule book: in this situation, do this. The value of a situation is how much reward you expect from it on average if you follow the best rule book.</p>',
    '<p>MDP = states, actions, P(s′ | s, a), R, γ. Bellman equation, value iteration (contraction by γ), policy iteration (evaluate, improve), Q-values.</p>',
    '<p>Bounds: utilities at most R_max ÷ (1 − γ), stopping rule ε (1 − γ) ÷ γ, policy loss 2εγ ÷ (1 − γ). MDPs are P-complete (Papadimitriou and Tsitsiklis, 1987), POMDPs are much harder.</p>',
    '<p>Research: approximate dynamic programming with function approximation, factored MDPs that exploit structure, safe and constrained MDPs, and large scale planning with learned models (as in MuZero, Schrittwieser and others, 2020).</p>')}
''', kw=['P-complete', 'factored MDP', 'approximate dynamic programming', 'MuZero'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An MDP has states, actions, P(s′ | s, a), rewards and a discount γ. A solution is a policy π(s).',
    'Bellman equation: U(s) = R(s) + γ max over a of Σ P(s′ | s, a) U(s′).',
    'Value iteration repeats the Bellman update. It converges because each sweep shrinks the error by γ. In the 4 × 3 world U(1,1) = 0.705.',
    'Policy iteration alternates exact evaluation (linear equations) and greedy improvement, and stops after a few rounds.',
    'Q(s, a) = Σ P(s′ | s, a) [R + γ max Q(s′, a′)] gives the best action without a model, the bridge to reinforcement learning.'],
    'chapter 10.2 learns utilities when the agent does not know P or R: passive reinforcement learning.')}
{nbcard('mdp', 'Run value iteration and policy iteration on the racing car MDP, then write discounted returns, a Bellman update and value iteration with policy extraction yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A policy π in an MDP is', ['a fixed list of actions', 'a rule giving an action for every state', 'the reward function', 'the transition model'], 1,
       'State to action.', 'It works whatever state the agent ends up in.')
K.quiz('e', 'The Markov property says the next state depends on', ['the whole history', 'only the current state and action', 'only the reward', 'nothing'], 1,
       'No memory needed.', 'P(s′ | s, a).')
K.quiz('e', 'With γ = 0.5, the rewards 1, 1, 1 are worth', ['3', '1.75', '1.5', '2'], 1,
       '1 + 0.5 + 0.25.', 'Each later reward counts half as much.')
K.quiz('e', 'Value iteration starts with', ['the optimal policy', 'U(s) = 0 for all states (or any values)', 'a random transition model', 'Q = 1'], 1,
       'Any start works.', 'The contraction pulls every start to the same answer.')
K.quiz('m', 'Why does value iteration converge when γ < 1?', ['the states are finite', 'the Bellman update is a contraction by γ in the max norm', 'rewards are positive', 'it uses search'], 1,
       'Error shrinks each sweep.', '‖U_(i+1) − U‖ ≤ γ ‖U_i − U‖.')
K.quiz('m', 'Policy evaluation is easier than solving the Bellman equation because', ['it has fewer states', 'with the action fixed there is no max, so the equations are linear', 'it ignores rewards', 'it is random'], 1,
       'No max.', 'Solve n linear equations.')
K.quiz('m', 'In the 4 × 3 world with R = −0.04, the policy in square (3,1) goes', ['Up, towards −1', 'Left, the long way round', 'Right', 'Down'], 1,
       'Risk of slipping into −1.', 'Going Up from (3,1) to (3,2) passes next to the −1 square, so the long way is safer.')
K.quiz('m', 'U(s) and Q(s, a) are linked by', ['U = Q × γ', 'U(s) = max over a of Q(s, a)', 'Q = U + R', 'they are unrelated'], 1,
       'Best action.', 'The utility of a state is the value of its best action.')
K.quiz('h', 'With R_max = 1 and γ = 0.9, utilities can be at most', ['1', '9', '10', '0.9'], 2,
       'R_max ÷ (1 − γ).', '1 ÷ 0.1 = 10.')
K.quiz('h', 'Policy iteration always stops because', ['it uses a stopping rule on values', 'there are finitely many policies and each round never gets worse', 'γ < 1', 'the model is known'], 1,
       '|A|^|S| policies.', 'A policy cannot repeat once improved.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: in the 4 × 3 world, as R becomes very negative (R < −1.63), the optimal policy', ['avoids both exits', 'heads for the nearest exit, even the −1 square', 'stays still', 'goes round the long way'], 1,
       'Life hurts more than −1.', 'Ending fast costs less than staying.')
K.quiz('x', 'In the style of a Stanford CS234 exam: which statement about modified policy iteration is true?', ['it never converges', 'it runs only k sweeps of evaluation per round, which sits between value iteration (k = 1) and policy iteration (k → ∞)', 'it needs no model', 'it is slower than both'], 1,
       'Interpolates.', 'With k = 1 it is close to value iteration.')

# ---------------------------------------------------------------- calc
K.calc('e', 'Discounted return of rewards 1, 1, 1, ... for ever, with γ = 0.9.', '10', 'Geometric series.',
       ['1 + 0.9 + 0.81 + ...', '= 1 ÷ (1 − 0.9).', eq('10')], check=10)
K.calc('e', 'A trial in the 4 × 3 world: 7 steps at −0.04, then +1. Its total reward with γ = 1.', '0.72', '−0.28 + 1.',
       ['7 × (−0.04) = −0.28.', 'Add the +1.', eq('0.72')], check=0.72, tol=0.0005)
K.calc('e', 'Upper bound on utilities with R_max = 2 and γ = 0.8.', '10', 'R_max ÷ (1 − γ).',
       ['1 − 0.8 = 0.2.', '2 ÷ 0.2.', eq('10')], check=10)
K.calc('m', 'First sweep of value iteration for (3,3) in the 4 × 3 world.', '0.76', 'Action Right reaches +1 with 0.8.',
       ['Σ P U = 0.8 × 1 + 0.1 × 0 + 0.1 × 0 = 0.8.', 'Add R = −0.04.', eq('0.76')], check=0.76, tol=0.0005)
K.calc('m', 'Racing car, γ = 0.9: V₂(cool) after two sweeps from 0.', '3.35', 'V₁ = (cool 2, warm 1).',
       ['fast: 0.5 (2 + 1.8) + 0.5 (2 + 0.9) = 1.9 + 1.45.', 'slow: 1 + 1.8 = 2.8.', eq('max = 3.35')], check=3.35, tol=0.0005)
K.calc('m', 'Racing car, γ = 0.9: V₂(warm).', '2.35', 'slow is best.',
       ['slow: 0.5 (1 + 1.8) + 0.5 (1 + 0.9) = 1.4 + 0.95.', 'fast: −10.', eq('2.35')], check=2.35, tol=0.0005)
K.calc('m', 'How many deterministic policies does the 4 × 3 world have (9 squares where a choice matters, 4 actions)?', '262144', '4⁹.',
       ['4 choices in each of 9 squares.', '4⁹ = 262,144.', eq('262144')], check=262144)
K.calc('h', 'Racing car, γ = 0.9, policy (cool: fast, warm: slow): V(cool).', '15.5', 'Solve the two linear equations.',
       ['V(cool) − V(warm) = 1.', 'V(warm) = 1.45 + 0.9 V(warm), so V(warm) = 14.5.', eq('V(cool) = 15.5')], check=15.5, tol=0.0005)
K.calc('h', 'Stopping rule: with ε = 0.01 and γ = 0.9, stop when the largest change is below ε(1 − γ) ÷ γ. Give 5 decimals.', '0.00111', '0.01 × 0.1 ÷ 0.9.',
       ['0.01 × 0.1 = 0.001.', 'Divide by 0.9.', eq('≈ 0.00111')], check=0.00111, tol=0.00001)
K.calc('x', 'Policy loss bound: values within ε = 0.01 of optimal, γ = 0.9. Bound on ‖U^π − U‖ = 2εγ ÷ (1 − γ).', '0.18', '2 × 0.01 × 0.9 ÷ 0.1.',
       ['2 × 0.01 × 0.9 = 0.018.', 'Divide by 0.1.', eq('0.18')], check=0.18, tol=0.0005)

# ---------------------------------------------------------------- assignments
CAR = '''T = {"cool": {"slow": [(1.0, "cool", 1)],
              "fast": [(0.5, "cool", 2), (0.5, "warm", 2)]},
     "warm": {"slow": [(0.5, "cool", 1), (0.5, "warm", 1)],
              "fast": [(1.0, "over", -10)]}}   # T[s][a] = list of (probability, next state, reward)
'''
K.assign('ret', 'e', 'Discounted return',
         '<p>Write <code>discounted_return(rewards, gamma)</code> = Σ gammaᵗ × rewards[t].</p>',
         '''
def discounted_return(rewards, gamma):
    # your code here
    pass
''', [("discounted_return([1, 1, 1], 0.5)", 1.75), ("round(discounted_return([-0.04] * 7 + [1], 1), 2)", 0.72),
      ("round(discounted_return([0, 0, 10], 0.9), 2)", 8.1), ("discounted_return([], 0.9)", 0.0)],
         '''
def discounted_return(rewards, gamma):
    total = 0.0
    factor = 1.0
    for r in rewards:
        total = total + factor * r
        factor = factor * gamma
    return total
''', 'Keep a factor that starts at 1 and is multiplied by gamma after each reward.', '<p>Test 3: 10 × 0.9² = 8.1.</p>')
K.assign('bellman', 'm', 'One Bellman update',
         '<p>Write <code>bellman(V, gamma)</code> for the racing car T: return a new dictionary with V(s) = max over a of Σ p (r + gamma V(s′)) for "cool" and "warm", and 0.0 for "over".</p>',
         CAR + '''
def bellman(V, gamma):
    # your code here
    pass
''', [("bellman({'cool': 0.0, 'warm': 0.0, 'over': 0.0}, 0.9)", {'cool': 2.0, 'warm': 1.0, 'over': 0.0}),
      ("{s: round(v, 2) for s, v in bellman({'cool': 2.0, 'warm': 1.0, 'over': 0.0}, 0.9).items()}", {'cool': 3.35, 'warm': 2.35, 'over': 0.0}),
      ("{s: round(v, 2) for s, v in bellman({'cool': 15.5, 'warm': 14.5, 'over': 0.0}, 0.9).items()}", {'cool': 15.5, 'warm': 14.5, 'over': 0.0})],
         CAR + '''
def bellman(V, gamma):
    new = {"over": 0.0}
    for s in T:
        best = None
        for a in T[s]:
            q = 0.0
            for p, s2, r in T[s][a]:
                q = q + p * (r + gamma * V[s2])
            if best is None or q > best:
                best = q
        new[s] = best
    return new
''', 'For each state, compute a Q value per action and keep the largest.', '<p>Test 3: the optimal values do not change under the update, since they solve the Bellman equation.</p>')
K.assign('vi', 'h', 'Value iteration with the policy',
         '<p>Write <code>solve(gamma)</code> for the racing car: repeat Bellman updates from all zeros until the largest change is below 1e-9, then return (V, policy), where policy maps "cool" and "warm" to the best action.</p>',
         CAR + '''
def solve(gamma):
    # your code here
    pass
''', [("solve(0.9)[1]", {'cool': 'fast', 'warm': 'slow'}), ("round(solve(0.9)[0]['cool'], 2)", 15.5),
      ("solve(0.1)[1]", {'cool': 'fast', 'warm': 'slow'}), ("round(solve(0.5)[0]['warm'], 3)", 2.5)],
         CAR + '''
def q_value(V, s, a, gamma):
    total = 0.0
    for p, s2, r in T[s][a]:
        total = total + p * (r + gamma * V[s2])
    return total

def solve(gamma):
    V = {"cool": 0.0, "warm": 0.0, "over": 0.0}
    while True:
        new = {"over": 0.0}
        change = 0.0
        for s in T:
            best = max(q_value(V, s, a, gamma) for a in T[s])
            new[s] = best
            change = max(change, abs(best - V[s]))
        V = new
        if change < 1e-9:
            break
    policy = {}
    for s in T:
        best_a = None
        for a in T[s]:
            if best_a is None or q_value(V, s, a, gamma) > q_value(V, s, best_a, gamma):
                best_a = a
        policy[s] = best_a
    return V, policy
''', 'Loop until the change is tiny, then pick the action with the largest Q value in each state.', '<p>Test 4, γ = 0.5: V(cool) − V(warm) = 1 still holds, and V(warm) = 1.25 + 0.5 V(warm) gives V(warm) = 2.5.</p>')

K.must('MDP', 'States, actions, P(s′ | s, a), R, γ. Solution: policy π(s). Utility = E[Σ γᵗ Rₜ] ≤ R_max ÷ (1 − γ).')
K.must('Bellman', 'U(s) = R(s) + γ max_a Σ P(s′ | s, a) U(s′). Q(s, a) = Σ P [R + γ max Q(s′, a′)]. U = max_a Q.')
K.must('Value iteration', 'Repeat the update. Contraction by γ. Stop when δ < ε(1 − γ) ÷ γ. 4 × 3: U(1,1) = 0.705.')
K.must('Policy iteration', 'Evaluate (linear equations, O(n³)), improve greedily, stop when unchanged. Few rounds.')
K.must('Racing car', 'γ = 0.9: V₁ = (2, 1), V₂ = (3.35, 2.35). Optimal: cool fast, warm slow, V = (15.5, 14.5).')

T = K.topic(
    slug='mdp', topic='mdp', step=STEP10,
    title='Markov decision processes', short='MDPs', badge='10.1', minutes=55,
    lead='Plan when actions have chance outcomes. Describe the problem as states, actions, transitions and rewards, then find the best policy with the Bellman equation, value iteration, policy iteration and Q-values.',
    desc='Markov decision processes, the Markov property, policies, utilities of reward sequences and discounting, the Bellman equation, value iteration and its contraction proof, the stopping rule and policy loss bound, policy iteration with exact evaluation, modified policy iteration, Q-values, the 4 × 3 world, the racing car MDP and partially observable MDPs.',
    summary='MDPs, the Bellman equation, value iteration, policy iteration and Q-values.',
    keywords=['MDP', 'policy', 'discount', 'Bellman equation', 'value iteration', 'policy iteration', 'Q-value', 'contraction', 'POMDP'],
    recap='<p>U(s) = R(s) + γ max Σ P U(s′). Value iteration repeats it, policy iteration evaluates and improves.</p>',
    nb={'vi': 'Value iteration on the racing car', 'pi': 'Policy iteration on the racing car'})
