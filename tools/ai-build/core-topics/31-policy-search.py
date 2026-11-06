# Chapter 10.4: policy search. The uploaded slides and transcripts do not cover this step, so it follows AIMA 3rd ed.
# sections 21.5 and 21.6 (4th ed. 22.5 and 22.6), Williams (1992), Sutton and others (2000) and Sutton and Barto
# (2018). Every number in this chapter was checked by running its code and the pgrad animation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP10 = (10, 'Reinforcement learning', 'cai-rl', 'Decide over time and learn from rewards: Markov decision processes, policies, Q-values, passive and active reinforcement learning, and policy search.', 'College')

K.code('softgrad', r'''
# A softmax policy over two actions and the gradient of log pi, which REINFORCE needs.
import math
theta = [0.0, 1.0]                          # one preference per action

def policy(theta):
    e = [math.exp(t) for t in theta]
    total = sum(e)
    return [x / total for x in e]

pi = policy(theta)
print("pi =", [round(p, 3) for p in pi])
for a in [0, 1]:
    grad = [(1 if k == a else 0) - pi[k] for k in range(2)]   # d log pi(a) / d theta_k
    print("action", a, "gradient of log pi:", [round(g, 3) for g in grad])
''')

K.code('reinforce', r'''
# REINFORCE on a two armed bandit. Arm 0 pays 1 with chance 0.3, arm 1 pays 1 with chance 0.7.
import math, random
rng = random.Random(2)
theta = [0.0, 0.0]
alpha, baseline = 0.4, 0.0

for t in range(1, 41):
    e0, e1 = math.exp(theta[0]), math.exp(theta[1])
    pi = [e0 / (e0 + e1), e1 / (e0 + e1)]
    a = 0 if rng.random() < pi[0] else 1
    r = 1.0 if rng.random() < [0.3, 0.7][a] else 0.0
    for k in range(2):                                  # theta += alpha (r - b) grad log pi(a)
        theta[k] = theta[k] + alpha * (r - baseline) * ((1 if k == a else 0) - pi[k])
    baseline = baseline + (r - baseline) / t            # running average reward
print("theta:", [round(x, 3) for x in theta])
print("chance of the better arm:", round(math.exp(theta[1]) / (math.exp(theta[0]) + math.exp(theta[1])), 3))
''')

K.lesson('search', 'Policy search: tune the policy directly', f'''
{src('AIMA 3rd ed., section 21.5 (4th ed., 22.5), Williams (1992), and Sutton and Barto (2018), chapter 13. The uploaded slides and transcripts do not cover this step.')}
{wwh('<b>Policy search</b> writes the policy as a formula π_θ with parameters θ and changes θ to raise the policy value ρ(θ), the expected total reward of following π_θ. It never needs to learn exact values for every state.',
     'Sometimes the best policy is simple even when the values are complicated: "steer towards the centre of the road" is easier than predicting the exact future reward of every position. Policy search also works with continuous actions, such as how hard to brake, where taking a max over actions is hard.',
     'Use a stochastic policy, such as a softmax over action preferences, so that ρ(θ) changes smoothly with θ. Estimate the gradient of ρ from trials and climb it: θ ← θ + α ∇ρ(θ).')}
{fxs(fx('Policy value', 'ρ(θ) = E[Σ γᵗ Rₜ | actions from π_θ]', 'What policy search maximises.', key=True),
     fx('Softmax policy', 'π_θ(a | s) = e^(θ · f(s, a)) ÷ Σ over b of e^(θ · f(s, b))', 'Every action keeps some chance, so the policy explores.'),
     fx('Finite difference gradient', '∂ρ ÷ ∂θᵢ ≈ (ρ(θ + h eᵢ) − ρ(θ)) ÷ h', 'Works for any policy, but needs many trials per parameter and is noisy.'))}
{code('softgrad')}
{note('With a greedy policy (always the best action under some score) ρ(θ) jumps when the best action changes, so its gradient is zero almost everywhere. That is why policy gradient methods use stochastic policies.', 'warn')}
''', kw=['policy search', 'parameterised policy', 'policy value', 'softmax policy', 'stochastic policy', 'continuous actions', 'finite differences'])

K.lesson('reinforcel', 'The policy gradient and REINFORCE', f'''
{src('Williams (1992), Simple statistical gradient following algorithms for connectionist reinforcement learning, and Sutton, McAllester, Singh and Mansour (2000), the policy gradient theorem.')}
{wwh('The policy gradient theorem gives ∇ρ as an average we can sample: E[∇ log π_θ(a | s) × (return after taking a)]. <b>REINFORCE</b> uses one trial at a time as a sample of this average.',
     'It needs no model and no derivative of the world, only the derivative of our own policy, which we wrote down. Actions followed by high returns become more likely, actions followed by low returns less likely.',
     'Run a trial. For each step t, with return Gₜ from then on, update θ ← θ + α (Gₜ − b) ∇ log π_θ(aₜ | sₜ). The baseline b, for example the average return so far, does not change the expected update but makes it much less noisy.')}
{fxs(fx('Policy gradient theorem', '∇ρ(θ) = E[∇_θ log π_θ(a | s) Q^π(s, a)]', 'Only the gradient of the policy appears.', key=True),
     fx('REINFORCE update', 'θ ← θ + α (Gₜ − b) ∇_θ log π_θ(aₜ | sₜ)', 'b is a baseline that does not depend on the action.'),
     fx('Softmax gradient', '∂ log π(a) ÷ ∂θ_k = 1[k = a] − π(k)', 'For a softmax over preferences θ.'),
     fx('Why a baseline is safe', 'E[∇ log π(a)] = Σ π(a) ∇ log π(a) = ∇ Σ π(a) = ∇ 1 = 0', 'So subtracting b changes no expected value.'))}
{viz('pgrad')}
{code('reinforce')}
{steps('Worked example: one REINFORCE step on two actions', [
    'θ = (0, 0), so π = (0.5, 0.5). The agent picks action 1 and gets r = 1. α = 0.4.',
    'Gradient of log π(1): (0 − 0.5, 1 − 0.5) = (−0.5, 0.5).',
    'No baseline: θ ← (0, 0) + 0.4 × 1 × (−0.5, 0.5) = (−0.2, 0.2).',
    eq('With baseline b = 0.5 the step is half as big: θ = (−0.1, 0.1)')])}
''', kw=['policy gradient', 'policy gradient theorem', 'REINFORCE', 'log derivative trick', 'baseline', 'variance reduction'])

K.lesson('ac', 'Actor critic and other refinements', f'''
{src('Barto, Sutton and Anderson (1983), Konda and Tsitsiklis (2000), Ng and Jordan (2000) for PEGASUS, and Schulman and others (2017) for PPO.')}
{wwh('An <b>actor critic</b> method keeps two learners: the actor is the policy π_θ, the critic learns a value function V_w. The critic’s TD error tells the actor whether an action turned out better or worse than expected.',
     'REINFORCE waits for the end of a trial and its returns are noisy. The critic gives a lower variance signal after every step, so learning is faster and works for tasks that never end.',
     'After each step: δ = r + γ V_w(s′) − V_w(s). Critic: w ← w + β δ ∇V_w(s). Actor: θ ← θ + α δ ∇ log π_θ(a | s). Correlated sampling (PEGASUS) reuses the same random numbers when comparing two policies, which removes much of the noise from finite difference estimates.')}
{fxs(fx('Actor critic', 'δ = r + γ V(s′) − V(s), θ ← θ + α δ ∇ log π_θ(a | s)', 'δ estimates the advantage of the action taken.', key=True),
     fx('Advantage', 'A(s, a) = Q(s, a) − V(s)', 'How much better a is than the policy’s average action.'),
     fx('PPO clipped objective', 'E[min(r_t(θ) Â, clip(r_t(θ), 1 − ε, 1 + ε) Â)], with r_t = π_θ ÷ π_old', 'Keeps each policy update small and safe.'))}
{steps('Worked example: a TD error as the actor’s signal', [
    'The critic says V(s) = 2.5. The agent acts, gets r = 1 and lands in s′ with V(s′) = 2. γ = 0.9.',
    'δ = 1 + 0.9 × 2 − 2.5 = 1 + 1.8 − 2.5.',
    'δ = 0.3 is positive: the action did better than expected.',
    eq('the actor raises the chance of that action, by α × 0.3 × ∇ log π')])}
''', kw=['actor critic', 'critic', 'advantage', 'TD error', 'PEGASUS', 'correlated sampling', 'PPO'])

K.lesson('apprentice', 'Learning from an expert: imitation and inverse RL', f'''
{src('AIMA 3rd ed., section 21.6, Ng and Russell (2000) for inverse reinforcement learning, and Abbeel and Ng (2004) for apprenticeship learning.')}
{wwh('Instead of a reward, the agent may watch an expert. <b>Imitation learning</b> (behaviour cloning) copies the expert’s actions with supervised learning. <b>Inverse reinforcement learning</b> works out a reward function that explains the expert’s behaviour, then plans with it.',
     'Writing a good reward by hand is hard: a reward for "drive well" is much harder to write than a few hours of a good driver’s data. A learned reward also carries over to new situations the expert never met.',
     'Behaviour cloning fits π(a | s) to the expert’s pairs. Inverse RL searches for a reward under which the expert’s policy is optimal (or nearly), often matching expected feature counts, and then solves the MDP for that reward.')}
{scene('Helicopter aerobatics', '<p>Abbeel, Coates, Quigley and Ng (2007) used apprenticeship learning and policy search to fly a model helicopter through stunts such as flips, rolls and tic tocs, learned from a few demonstrations by an expert pilot. Policy search with PEGASUS had earlier learned to hover the same helicopter (Ng and others, 2004).</p>')}
''', kw=['imitation learning', 'behaviour cloning', 'inverse reinforcement learning', 'apprenticeship learning', 'reward learning', 'helicopter'])

K.lesson('maths', 'The maths: deriving the policy gradient', f'''
{fxs(
    fx('Log derivative trick', '∇ π(a) = π(a) ∇ log π(a)', 'Turns a gradient of a sum into an expectation.', key=True),
    fx('One step (bandit) case', '∇ρ = ∇ Σ π(a) R(a) = Σ π(a) ∇ log π(a) R(a) = E[∇ log π(a) R(a)]', 'Sample a, multiply the gradient of log π(a) by its reward.'),
    fx('Exact bandit gradient for a softmax', '∂ρ ÷ ∂θ_k = π(k) (μ_k − ρ)', 'An action with above average reward gets pushed up.'),
    fx('Variance with a baseline', 'Var[(G − b) ∇ log π] is smallest near b = E[G]', 'The usual choice is an estimate of V(s).'))}
{steps('Worked example: the exact gradient for two arms with means 0.3 and 0.7, at π = (0.5, 0.5)', [
    'ρ = 0.5 × 0.3 + 0.5 × 0.7 = 0.5.',
    '∂ρ ÷ ∂θ₁ = π(1) (μ₁ − ρ) = 0.5 × (0.7 − 0.5).',
    'That is 0.5 × 0.2 = 0.1. For arm 0: 0.5 × (0.3 − 0.5) = −0.1.',
    eq('∇ρ = (−0.1, 0.1): push towards the better arm')])}
''', kw=['log derivative trick', 'score function', 'policy gradient derivation', 'baseline variance'])

K.lesson('compare', 'Value based and policy based methods compared', f'''
{versus('Ways to learn a policy', ['', 'Q-learning (value based)', 'REINFORCE', 'Actor critic', 'Finite differences or evolution', 'Imitation and inverse RL'], [
    ['Learns', 'Q(s, a), acts greedily', 'π_θ directly', 'π_θ and V_w', 'π_θ by trying perturbed θ', 'π from an expert, or a reward'],
    ['Actions', 'discrete (needs a max)', 'discrete or continuous', 'discrete or continuous', 'any', 'any'],
    ['Variance', 'low', 'high', 'medium', 'high, unless correlated sampling', 'low (supervised)'],
    ['Data efficiency', 'good (off policy, replay)', 'poor (on policy)', 'better', 'poor', 'good with an expert'],
    ['Known for', 'DQN', 'simple, unbiased', 'A3C, PPO, SAC', 'PEGASUS, evolution strategies (Salimans and others, 2017)', 'self driving data, helicopters']],
    'use value based methods for discrete actions and plenty of data, policy gradients and actor critic methods for continuous actions or stochastic policies, and imitation when an expert is available.')}
''', kw=['comparison', 'value based', 'policy based', 'A3C', 'SAC', 'evolution strategies'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Keep a dial for each choice. After you try a choice, turn its dial up if things went better than usual and down if worse.</p>',
    '<p>π_θ as a softmax, ρ(θ) as the expected return, REINFORCE θ += α (G − b) ∇ log π(a), the baseline, actor critic with the TD error.</p>',
    '<p>The policy gradient theorem, compatible function approximation, natural policy gradients and trust regions (TRPO, PPO), entropy regularisation, and why on policy data limits sample efficiency.</p>',
    '<p>Research: RL from human feedback for language models (reward models plus PPO or direct preference optimisation), offline policy optimisation, and learning policies for robots in simulation that transfer to the real world.</p>')}
''', kw=['natural gradient', 'TRPO', 'entropy regularisation', 'RLHF', 'DPO', 'sim to real'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Policy search tunes θ of a policy π_θ to raise ρ(θ), the expected return. It handles continuous actions and simple policies well.',
    'Use stochastic (softmax) policies so ρ(θ) is smooth. ∂ log π(a) ÷ ∂θ_k = 1[k = a] − π(k).',
    'REINFORCE: θ ← θ + α (G − b) ∇ log π(a | s). A baseline cuts noise without changing the expected update.',
    'Actor critic uses the critic’s TD error δ in place of G − b, for faster, lower variance learning.',
    'Imitation learning and inverse RL learn from an expert when a reward is hard to write.'],
    'step 11 brings every Core AI topic together in hard challenge problems and a revision guide.')}
{nbcard('policy-search', 'Compute softmax gradients and run REINFORCE on a two armed bandit, then write the softmax policy, its log gradient and a full REINFORCE learner yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Policy search changes', ['the reward function', 'the parameters θ of the policy', 'the transition model', 'the discount'], 1,
       'Tune the policy.', 'To raise the expected return ρ(θ).')
K.quiz('e', 'A softmax policy', ['always picks the best action', 'gives every action a chance that grows with its preference', 'ignores θ', 'is greedy'], 1,
       'e^θ ÷ Σ e^θ.', 'So it explores and is smooth in θ.')
K.quiz('e', 'REINFORCE is', ['a value iteration method', 'a policy gradient method that uses whole returns', 'a model learning method', 'a search algorithm'], 1,
       'Williams, 1992.', 'θ += α G ∇ log π.')
K.quiz('e', 'In REINFORCE, an action followed by a high return becomes', ['less likely', 'more likely', 'impossible', 'unchanged'], 1,
       'Push up good actions.', 'With a baseline, only returns above the baseline push up.')
K.quiz('m', 'Why use a baseline in REINFORCE?', ['to change the optimal policy', 'to reduce the variance of the updates without changing their expected value', 'to explore', 'to discount'], 1,
       'E[∇ log π] = 0.', 'Subtracting b keeps the mean, cuts the noise.')
K.quiz('m', 'For a softmax over θ, ∂ log π(a) ÷ ∂θ_a equals', ['π(a)', '1 − π(a)', '−π(a)', '1'], 1,
       '1[k = a] − π(k) with k = a.', 'For other actions k it is −π(k).')
K.quiz('m', 'The critic in an actor critic method', ['chooses actions', 'learns a value function and gives the actor a TD error', 'is the reward', 'is the expert'], 1,
       'Two learners.', 'δ = r + γV(s′) − V(s).')
K.quiz('m', 'Policy gradient methods suit continuous actions because', ['they need a max over actions', 'they need no max over actions, only a policy that outputs a distribution', 'they use tables', 'they are greedy'], 1,
       'No argmax.', 'For example a Gaussian policy over steering angles.')
K.quiz('h', 'Why do greedy (deterministic, argmax) policies make gradient based policy search hard?', ['they are slow', 'ρ(θ) jumps when the best action changes, so the gradient is zero almost everywhere', 'they explore too much', 'they need models'], 1,
       'Flat then jump.', 'Smooth stochastic policies fix this.')
K.quiz('h', 'Inverse reinforcement learning', ['learns P from data', 'finds a reward function that explains an expert’s behaviour', 'reverses time', 'learns a policy without data'], 1,
       'Ng and Russell, 2000.', 'Then plan with the learned reward.')
K.quiz('x', 'In the style of a Berkeley CS285 exam: the policy gradient theorem lets us estimate ∇ρ without', ['samples', 'differentiating the transition model', 'a policy', 'rewards'], 1,
       'Log derivative trick.', 'The dynamics terms in log P(trajectory) do not depend on θ, so they drop out.')
K.quiz('x', 'In the style of a Stanford CS234 exam: PPO clips the probability ratio π_θ ÷ π_old in order to', ['explore more', 'stop one update from moving the policy too far from the one that collected the data', 'remove the critic', 'make the policy greedy'], 1,
       'Trust region idea.', 'Large steps on old data can wreck the policy.')

# ---------------------------------------------------------------- calc
K.calc('e', 'Softmax with θ = (0, 1): π of action 1, to 3 decimals.', '0.731', 'e ÷ (1 + e).',
       ['e⁰ = 1, e¹ ≈ 2.718.', 'Sum ≈ 3.718.', eq('2.718 ÷ 3.718 ≈ 0.731')], check=0.731, tol=0.001)
K.calc('e', 'A policy picks arm 1 (mean 1) with 0.3 and arm 2 (mean 2) with 0.7. Its value ρ?', '1.7', 'Σ π(a) μ(a).',
       ['0.3 × 1 = 0.3.', '0.7 × 2 = 1.4.', eq('1.7')], check=1.7, tol=0.0005)
K.calc('e', 'A softmax policy with linear features: 4 actions, 10 features per action, one weight per feature and action. How many parameters?', '40', '4 × 10.',
       ['Each action has 10 weights.', '4 actions.', eq('40')], check=40)
K.calc('m', 'With θ = (0, 1), the gradient of log π(0) with respect to θ₀, to 3 decimals.', '0.731', '1 − π(0).',
       ['π(0) ≈ 0.269.', '1 − 0.269.', eq('≈ 0.731')], check=0.731, tol=0.001)
K.calc('m', 'REINFORCE: θ = (0, 0), action 1 chosen, r = 1, no baseline, α = 0.4. New θ₁?', '0.2', '0.4 × 1 × (1 − 0.5).',
       ['π(1) = 0.5.', 'Gradient for θ₁: 1 − 0.5 = 0.5.', eq('0.4 × 0.5 = 0.2')], check=0.2, tol=0.0005)
K.calc('m', 'Same step with baseline b = 0.5. New θ₁?', '0.1', '(r − b) = 0.5.',
       ['r − b = 0.5.', '0.4 × 0.5 × 0.5.', eq('0.1')], check=0.1, tol=0.0005)
K.calc('m', 'Finite difference: ρ(θ) = 1.70, ρ(θ + 0.1) = 1.72. Estimated ∂ρ ÷ ∂θ?', '0.2', '(1.72 − 1.70) ÷ 0.1.',
       ['Difference 0.02.', 'Divide by h = 0.1.', eq('0.2')], check=0.2, tol=0.0005)
K.calc('m', 'Actor critic: r = 1, γ = 0.9, V(s′) = 2, V(s) = 2.5. TD error δ?', '0.3', 'r + γV(s′) − V(s).',
       ['0.9 × 2 = 1.8.', '1 + 1.8 = 2.8.', eq('2.8 − 2.5 = 0.3')], check=0.3, tol=0.0005)
K.calc('h', 'For any softmax policy, the expected value of ∂ log π(a) ÷ ∂θ_k over a ~ π is', '0', 'Σ π(a) (1[k = a] − π(k)).',
       ['The a = k term gives π(k) (1 − π(k)).', 'The other terms give − π(k) (1 − π(k)) in total.', eq('0, which is why a baseline adds no bias')], check=0, tol=0.0005)
K.calc('x', 'Two arms with means 0.3 and 0.7, softmax at π = (0.5, 0.5). Exact ∂ρ ÷ ∂θ₁?', '0.1', 'π(1)(μ₁ − ρ).',
       ['ρ = 0.5.', 'μ₁ − ρ = 0.2.', eq('0.5 × 0.2 = 0.1')], check=0.1, tol=0.0005)

# ---------------------------------------------------------------- assignments
K.assign('softmax', 'e', 'A softmax policy',
         '<p>Write <code>softmax(theta)</code> that returns the list e^θᵢ ÷ Σ e^θ.</p>',
         '''import math

def softmax(theta):
    # your code here
    pass
''', [("[round(p, 3) for p in softmax([0.0, 1.0])]", [0.269, 0.731]), ("softmax([0.0, 0.0])", [0.5, 0.5]),
      ("[round(p, 3) for p in softmax([1.0, 2.0, 3.0])]", [0.09, 0.245, 0.665])],
         '''import math

def softmax(theta):
    e = []
    for t in theta:
        e.append(math.exp(t))
    total = sum(e)
    out = []
    for x in e:
        out.append(x / total)
    return out
''', 'Exponentiate each preference, then divide by the total.', '<p>Adding the same number to every θ gives the same policy.</p>')
K.assign('glog', 'm', 'The gradient of log π',
         '<p>Write <code>grad_log_pi(theta, a)</code> that returns the list of ∂ log π(a) ÷ ∂θ_k = (1 if k = a else 0) − π(k), for a softmax policy.</p>',
         '''import math

def grad_log_pi(theta, a):
    # your code here
    pass
''', [("[round(g, 3) for g in grad_log_pi([0.0, 1.0], 0)]", [0.731, -0.731]), ("grad_log_pi([0.0, 0.0], 1)", [-0.5, 0.5]),
      ("round(sum(grad_log_pi([0.3, -1.2, 2.0], 2)), 6)", 0.0)],
         '''import math

def grad_log_pi(theta, a):
    e = [math.exp(t) for t in theta]
    total = sum(e)
    pi = [x / total for x in e]
    out = []
    for k in range(len(theta)):
        if k == a:
            out.append(1 - pi[k])
        else:
            out.append(-pi[k])
    return out
''', 'Compute the softmax first, then 1 − π(a) for the chosen action and −π(k) for the others.', '<p>Test 3: the parts always add up to 0.</p>')
K.assign('reinf', 'h', 'REINFORCE on a two armed bandit',
         '<p>Write <code>reinforce(steps, alpha, seed)</code>: arm 0 pays 1 with chance 0.3 and arm 1 with chance 0.7 (else 0). Start at θ = (0, 0), pick arms from the softmax with <code>rng.random()</code>, update θ with the running average reward as the baseline, and return the final chance of arm 1.</p>',
         '''import math, random

def reinforce(steps, alpha, seed):
    rng = random.Random(seed)
    # your code here
    pass
''', [("reinforce(2000, 0.1, 1) > 0.9", True), ("reinforce(2000, 0.1, 7) > 0.9", True), ("0.4 < reinforce(1, 0.1, 3) < 0.6", True)],
         '''import math, random

def reinforce(steps, alpha, seed):
    rng = random.Random(seed)
    theta = [0.0, 0.0]
    baseline = 0.0
    for t in range(1, steps + 1):
        e0 = math.exp(theta[0])
        e1 = math.exp(theta[1])
        pi = [e0 / (e0 + e1), e1 / (e0 + e1)]
        if rng.random() < pi[0]:
            a = 0
        else:
            a = 1
        if rng.random() < [0.3, 0.7][a]:
            r = 1.0
        else:
            r = 0.0
        for k in range(2):
            if k == a:
                g = 1 - pi[k]
            else:
                g = -pi[k]
            theta[k] = theta[k] + alpha * (r - baseline) * g
        baseline = baseline + (r - baseline) / t
    e0 = math.exp(theta[0])
    e1 = math.exp(theta[1])
    return e1 / (e0 + e1)
''', 'Inside the loop: softmax, pick an arm, draw a reward, update both θ values, then update the baseline.', '<p>After 2000 pulls the policy picks the better arm more than 90 percent of the time.</p>')

K.must('Policy search', 'Parameterise π_θ, maximise ρ(θ) = E[Σ γᵗ Rₜ]. Use stochastic (softmax) policies so ρ is smooth.')
K.must('Policy gradient', '∇ρ = E[∇ log π_θ(a | s) Q^π(s, a)]. Softmax: ∂ log π(a) ÷ ∂θ_k = 1[k = a] − π(k).')
K.must('REINFORCE', 'θ ← θ + α (G − b) ∇ log π(a | s). Baseline unbiased since E[∇ log π] = 0.')
K.must('Actor critic', 'δ = r + γV(s′) − V(s). Actor θ += α δ ∇ log π, critic w += β δ ∇V. PPO clips the ratio.')
K.must('From experts', 'Behaviour cloning copies actions. Inverse RL learns the reward (Ng and Russell 2000).')

T = K.topic(
    slug='policy-search', topic='policy-search', step=STEP10,
    title='Policy search and policy gradients', short='Policy search', badge='10.4', minutes=45,
    lead='Skip learning values and tune the policy itself. Use softmax policies, the policy gradient theorem and REINFORCE with a baseline, then speed up with actor critic methods, and learn from experts with imitation and inverse RL.',
    desc='Policy search, parameterised and stochastic policies, the policy value, finite difference gradients and correlated sampling, the policy gradient theorem and the log derivative trick, REINFORCE with baselines, softmax gradients, actor critic methods and the advantage, PPO, imitation learning, inverse reinforcement learning and apprenticeship learning, and a comparison of value based and policy based methods.',
    summary='Policy gradients, REINFORCE, baselines, actor critic and learning from experts.',
    keywords=['policy search', 'policy gradient', 'REINFORCE', 'baseline', 'softmax policy', 'actor critic', 'advantage', 'PPO', 'inverse reinforcement learning', 'imitation learning'],
    recap='<p>θ += α (G − b) ∇ log π(a | s). Stochastic policies, baselines, critics.</p>',
    nb={'softgrad': 'The softmax policy and its log gradient', 'reinforce': 'REINFORCE on a two armed bandit'})
