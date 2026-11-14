# Reinforcement 1.1: agents, rewards and returns. Checked against Sutton and Barto, Reinforcement Learning: An
# Introduction (2nd edition, 2018) chapters 1 and 3, the Gymnasium documentation (Env.reset and Env.step with
# terminated and truncated, Farama Foundation), Silver, UCL Course on RL lecture 1, and Mnih and colleagues,
# Human-level control through deep reinforcement learning (Nature 2015).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-rl-intro')
K = Kit()

K.code('corridor', r'''
import random

class Corridor:
    """Cells 0 to 5. Start in cell 2. Cell 5 holds treasure (+10), cell 0 a pit (-10). Each move costs 1."""
    def reset(self):
        self.pos = 2
        return self.pos

    def step(self, action):                              # action: -1 = left, +1 = right
        self.pos += action
        if self.pos == 5:
            return self.pos, 10, True                    # new state, reward, episode over
        if self.pos == 0:
            return self.pos, -10, True
        return self.pos, -1, False

random.seed(23)
env = Corridor()
state, done, total, t = env.reset(), False, 0, 0
while not done:
    action = random.choice([-1, 1])                      # a random policy
    new_state, reward, done = env.step(action)
    t += 1
    print("t", t, " state", state, " action", "right" if action == 1 else "left ", " reward", str(reward).rjust(3), " next", new_state)
    state, total = new_state, total + reward
print("episode over after", t, "steps, total reward", total)
''')

K.code('returns', r'''
rewards = [-1, -1, -1, 10]                               # rewards of one episode, in order

def discounted_return(rewards, gamma):
    G = 0.0
    for r in reversed(rewards):                          # work backwards: G_t = r_t+1 + gamma * G_t+1
        G = r + gamma * G
    return G

for gamma in [1.0, 0.9, 0.5, 0.0]:
    print("gamma", gamma, " return from the start", round(discounted_return(rewards, gamma), 3))

gamma, G, returns = 0.9, 0.0, []
for r in reversed(rewards):
    G = r + gamma * G
    returns.append(round(G, 3))
print("return from each time step (gamma 0.9):", returns[::-1])
''')

K.code('compare_policies', r'''
import random

class Corridor:
    def reset(self):
        self.pos = 2
        return self.pos

    def step(self, action):
        self.pos += action
        if self.pos == 5:
            return self.pos, 10, True
        if self.pos == 0:
            return self.pos, -10, True
        return self.pos, -1, False

def run(policy, episodes=2000, max_steps=100):
    env, totals = Corridor(), []
    for _ in range(episodes):
        s, done, total, steps = env.reset(), False, 0, 0
        while not done and steps < max_steps:
            s, r, done = env.step(policy(s))
            total, steps = total + r, steps + 1
        totals.append(total)
    return sum(totals) / len(totals)

random.seed(0)
policies = {
    "random": lambda s: random.choice([-1, 1]),
    "always right": lambda s: 1,
    "always left": lambda s: -1,
    "right 80% of the time": lambda s: 1 if random.random() < 0.8 else -1,
}
for name, pi in policies.items():
    print(name.ljust(22), " average total reward", round(run(pi), 2))
''', long=True)

K.code('gym_loop', r'''
import numpy as np

class LineWorld:
    """A tiny environment with the same interface as Gymnasium: reset() and step() returning 5 values."""
    def __init__(self, size=7, max_steps=20):
        self.size, self.max_steps = size, max_steps
        self.rng = np.random.default_rng()

    def reset(self, seed=None):
        self.rng = np.random.default_rng(seed)
        self.pos, self.t = self.size // 2, 0
        return self.pos, {}                              # observation, info

    def step(self, action):                              # 0 = left, 1 = right
        self.pos = int(np.clip(self.pos + (1 if action == 1 else -1), 0, self.size - 1))
        self.t += 1
        terminated = self.pos == self.size - 1           # reached the goal: a real end
        truncated = self.t >= self.max_steps             # ran out of time: an artificial cut
        reward = 1.0 if terminated else -0.1
        return self.pos, reward, terminated, truncated, {}

env = LineWorld()
obs, info = env.reset(seed=42)
total, done = 0.0, False
while not done:
    action = int(env.rng.random() < 0.6)                 # lean right 60% of the time
    obs, reward, terminated, truncated, info = env.step(action)
    total += reward
    done = terminated or truncated
print("finished at step", env.t, " position", obs, " terminated", terminated, " truncated", truncated, " total", round(total, 2))
''')

K.lesson('idea', 'Learning from rewards: the agent and its environment', f'''
{src('Sutton and Barto, Reinforcement Learning: An Introduction (2nd edition, 2018) chapters 1 and 3, and Silver, UCL Course on RL lecture 1.')}
{viz('mlagent')}
{wwh('<b>Reinforcement learning</b> (RL) is learning what to do by trial and error. An <b>agent</b> acts in an <b>environment</b>. At each time step it observes a <b>state</b>, chooses an <b>action</b>, and receives a <b>reward</b> (a number) and the next state. Its rule for choosing actions is its <b>policy</b>. The goal is a policy that collects as much reward as possible over time.',
     'Many problems have no labelled right answer for each step, only a score that comes later: winning a game, keeping a robot upright, cutting the energy a data centre uses. RL learns from that score alone. It beat world champions at Go (AlphaGo, 2016), learned Atari games from pixels (DQN, 2015), and is used to fine tune large language models from human preferences.',
     'Write the problem as states, actions and rewards. Let the agent act, record what happens, and change the policy so that actions which led to more total reward become more likely. The rest of this section shows how: bandits, Markov decision processes, dynamic programming, Q learning and deep RL.')}
{run('corridor')}
{note('The random agent stepped right, left, left, right, right, right, right. Six moves cost &minus;1 each and the treasure gave +10, so the total was 4. Going right three times in a row would have scored 8. The agent did not know that. Learning means finding it out from experience.', 'exam')}
{table(['Term', 'Meaning', 'In the corridor'], [
    ['State s', 'What the agent observes now', 'Its cell number'],
    ['Action a', 'A choice the agent can make', 'Left or right'],
    ['Reward r', 'A number the environment gives after each action', '&minus;1 per move, +10 treasure, &minus;10 pit'],
    ['Policy &pi;', 'The rule that maps states to actions', '"Go right with chance 0.5"'],
    ['Episode', 'One run from a start to an end', 'Start in cell 2, stop at the pit or the treasure']])}
{link('ai', 'Seen RL in the Artificial Intelligence subject?', 'The AI subject covers Markov decision processes, passive and active RL and policy search from the Russell and Norvig point of view. This section goes further into code, maths and modern deep RL.', 'Open Artificial Intelligence')}
''', kw=['reinforcement learning', 'agent', 'environment', 'state', 'action', 'reward', 'policy', 'episode'])

K.lesson('returns', 'The return and the discount factor', f'''
{src('Sutton and Barto (2018) section 3.3, Returns and Episodes.')}
{viz('mlreturn')}
{wwh('The agent does not maximise the next reward but the <b>return</b> G<sub>t</sub>: the sum of all rewards from step t on. A <b>discount factor</b> &gamma; between 0 and 1 multiplies a reward k steps ahead by &gamma;<sup>k</sup>, so G<sub>t</sub> = r<sub>t+1</sub> + &gamma; r<sub>t+2</sub> + &gamma;<sup>2</sup> r<sub>t+3</sub> + ...',
     'Some good actions pay off only much later, and some quick wins lead to disaster. Adding up future rewards captures that. Discounting keeps the sum finite in tasks that never end, and expresses that sooner rewards are surer and worth more.',
     'Compute returns backwards from the end of an episode with G<sub>t</sub> = r<sub>t+1</sub> + &gamma; G<sub>t+1</sub>. Pick &gamma; for the task: 0.9 to 0.999 is common. Small &gamma; makes a short sighted agent, and &gamma; = 1 is safe only when every episode ends.')}
{run('returns')}
{note('The rewards &minus;1, &minus;1, &minus;1, +10 add up to 7. With &gamma; = 0.9 the return is 4.58, because the treasure three steps away counts as 0.9<sup>3</sup> &times; 10 = 7.29. With &gamma; = 0 only the first reward counts, &minus;1, and the treasure is invisible. Working backwards gives the return from every step at once: 10, 8, 6.2 and 4.58.', 'exam')}
{fxs(fx('Return', 'G<sub>t</sub> = &Sigma;<sub>k=0</sub><sup>&infin;</sup> &gamma;<sup>k</sup> r<sub>t+k+1</sub>', 'The quantity RL maximises in expectation.', key=True),
     fx('Recursive form', 'G<sub>t</sub> = r<sub>t+1</sub> + &gamma; G<sub>t+1</sub>', 'The seed of the Bellman equation.', key=True),
     fx('Constant reward', 'r + &gamma;r + &gamma;<sup>2</sup>r + ... = r / (1 &minus; &gamma;)', 'Bounded whenever &gamma; &lt; 1.'),
     fx('Effective horizon', 'about 1 / (1 &minus; &gamma;) steps', '&gamma; = 0.99 looks about 100 steps ahead.'))}
''', kw=['return', 'discount factor', 'gamma', 'discounted return', 'horizon', 'delayed reward'])

K.lesson('policies', 'Policies, value and the explore or exploit choice', f'''
{src('Sutton and Barto (2018) sections 1.3 and 3.5.')}
{wwh('A <b>policy</b> &pi;(a | s) gives the chance of each action in each state. It can be <b>deterministic</b> (always right) or <b>stochastic</b> (right 80% of the time). The <b>value</b> of a policy is the return it earns on average. RL compares policies by value and searches for the best one, the <b>optimal policy</b> &pi;*.',
     'The agent must try actions to learn what they do (<b>exploration</b>) but also use what it already knows to earn reward (<b>exploitation</b>). Too much of either wastes reward. This trade off is the core difficulty of RL and has no counterpart in supervised learning.',
     'Estimate the value of a policy by running many episodes and averaging the totals, as below. Later chapters estimate value much more cleverly, state by state, and improve the policy step by step.')}
{run('compare_policies')}
{note('Over 2,000 episodes: always right earns 8, its exact best path. Right 80% of the time earns 5.29, random earns &minus;7.03 and always left &minus;11. A theory check: a fair random walk from cell 2 between 0 and 5 reaches the treasure first with chance 2/5 and takes 2 &times; 3 = 6 steps on average, so its expected total is &minus;5 + 0.4 &times; 10 + 0.6 &times; (&minus;10) = &minus;7, just as the simulation found.', 'exam')}
{table(['', 'Exploit', 'Explore'], [
    ['Does', 'Pick the best action found so far', 'Try an action that may be worse'],
    ['Gains', 'Reward now', 'Information for later'],
    ['Risk', 'Stuck with a second best choice', 'Lost reward while testing'],
    ['Simple rule', 'Greedy', '&epsilon; greedy: random action with chance &epsilon;']])}
''', kw=['policy', 'deterministic policy', 'stochastic policy', 'value', 'optimal policy', 'exploration', 'exploitation', 'epsilon greedy'])

K.lesson('gym', 'Environments in code: the Gymnasium interface', f'''
{src('Gymnasium documentation (Farama Foundation), Env.reset and Env.step, and Towers and colleagues, Gymnasium: A Standard Interface for Reinforcement Learning Environments (2024).')}
{wwh('<b>Gymnasium</b>, the maintained successor of OpenAI Gym, is the standard Python interface for RL environments. <code>reset(seed)</code> starts an episode and returns the first observation and an info dictionary. <code>step(action)</code> returns five values: observation, reward, <b>terminated</b>, <b>truncated</b> and info.',
     'With one interface, the same agent code can learn CartPole, Atari games or a robot simulator, and libraries such as Stable Baselines3 plug straight in. Knowing the difference between terminated and truncated avoids a classic bug in value estimates.',
     'Loop: reset, then step until terminated or truncated. <b>Terminated</b> means the task really ended (goal or failure), so no future reward follows. <b>Truncated</b> means a time limit cut it short, so the state still has future value, and a learning update must not treat it as an end. Install with pip install gymnasium, then gymnasium.make("CartPole-v1").')}
{run('gym_loop')}
{note('The agent leaned right but did not reach cell 6 within 20 steps, so the episode was <b>truncated</b>, not terminated. Its last state, cell 2, still had a future. A learner that treated this as a true end would wrongly believe cell 2 is worth nothing after this step.', 'exam')}
{table(['Kind of task', 'Ends?', 'Examples', 'Discount'], [
    ['Episodic', 'Yes, in a terminal state', 'A game of chess, one maze run', '&gamma; = 1 is allowed'],
    ['Continuing', 'No', 'Stock trading, heating control', '&gamma; &lt; 1 needed']])}
{deep('Where RL is used, and where it struggles', '<p>Successes: games (Atari, Go, StarCraft II, Dota 2), robot control in simulation, chip floor planning, data centre cooling, recommendation with long term goals, and reinforcement learning from human feedback (RLHF) for language models. Struggles: it can need millions of trials, rewards are easy to specify wrongly (the agent finds loopholes, called reward hacking), results vary a lot between random seeds, and trial and error is unsafe on real machines and people. Many real systems therefore learn in simulation or from logged data first. The last chapter of this section returns to these issues.</p>')}
''', kw=['Gymnasium', 'OpenAI Gym', 'reset', 'step', 'terminated', 'truncated', 'episodic task', 'continuing task', 'reward hacking'])

K.lesson('versus', 'Reinforcement learning compared', f'''
{versus('Three kinds of learning', ['', 'Supervised', 'Unsupervised', 'Reinforcement'], [
    ['Feedback', 'The right answer for every example', 'None', 'A reward, often delayed'],
    ['Data', 'A fixed labelled dataset', 'A fixed unlabelled dataset', 'Created by the agent’s own actions'],
    ['Goal', 'Predict labels', 'Find structure', 'Maximise total reward'],
    ['Main difficulty', 'Generalising', 'Deciding what structure matters', 'Exploration and credit for delayed rewards'],
    ['Example', 'Spam filter', 'Customer segments', 'Game playing agent']],
    'use RL when decisions affect future data and the only feedback is a score. If you have the right action for each state, supervised learning is simpler.')}
''', kw=['reinforcement vs supervised learning', 'reinforcement vs unsupervised learning'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Interaction', 's<sub>0</sub>, a<sub>0</sub>, r<sub>1</sub>, s<sub>1</sub>, a<sub>1</sub>, r<sub>2</sub>, s<sub>2</sub>, ...', 'A trajectory.'),
     fx('Policy', '&pi;(a | s) = P(A<sub>t</sub> = a | S<sub>t</sub> = s)', 'Stochastic in general.', key=True),
     fx('Return', 'G<sub>t</sub> = &Sigma;<sub>k&ge;0</sub> &gamma;<sup>k</sup> r<sub>t+k+1</sub> = r<sub>t+1</sub> + &gamma; G<sub>t+1</sub>', '0 &le; &gamma; &le; 1.', key=True),
     fx('Goal', 'find &pi; that maximises E<sub>&pi;</sub>[G<sub>0</sub>]', 'The expected return from the start.', key=True),
     fx('Geometric sum', '&Sigma;<sub>k&ge;0</sub> &gamma;<sup>k</sup> = 1 / (1 &minus; &gamma;)', 'For &gamma; &lt; 1. Bounds every return by r<sub>max</sub> / (1 &minus; &gamma;).'),
     fx('Gambler’s ruin', 'P(reach N before 0 from k) = k / N, E[steps] = k(N &minus; k)', 'For a fair random walk.'))}
{steps('Worked example: return of the best corridor path', [
    'Start in cell 2 and always go right: rewards &minus;1, &minus;1, +10.',
    'Plain sum: &minus;1 &minus; 1 + 10 = 8.',
    eq('With &gamma; = 0.9: &minus;1 + 0.9 &times; (&minus;1) + 0.81 &times; 10 = &minus;1 &minus; 0.9 + 8.1 = 6.2'),
    'Backwards: G<sub>3</sub> = 10, G<sub>2</sub> = &minus;1 + 0.9 &times; 10 = 8, G<sub>1</sub> = &minus;1 + 0.9 &times; 8 = 6.2.'])}
{deep('Why discounting is more than a trick', '<p>For continuing tasks the plain sum of rewards can be infinite, so policies cannot be compared. Discounting with &gamma; &lt; 1 bounds the return by r<sub>max</sub> / (1 &minus; &gamma;). It can also be read as a chance 1 &minus; &gamma; that the world ends at every step, or as interest rates in economics. An alternative for continuing tasks is the average reward per step, which Sutton and Barto treat in chapter 10. In practice &gamma; is also a tuning knob: a smaller &gamma; makes value estimates lower in variance but more short sighted.</p>')}
''', kw=['trajectory', 'policy formula', 'return formula', 'geometric series', 'gamblers ruin'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>An agent tries actions, gets rewards, and learns which actions lead to more reward over time.</p>',
    '<p>Name states, actions, rewards, policies and episodes, compute discounted returns, and write the reset and step loop of a Gymnasium environment.</p>',
    '<p>Evaluate policies by simulation, reason about exploration against exploitation, handle terminated against truncated correctly, and choose &gamma; for a task.</p>',
    '<p>Study reward design and reward hacking, average reward formulations, partial observability (POMDPs), and the sample efficiency limits of model free RL.</p>')}
{grow('Explain how an agent learns from rewards.',
      'Simulate an environment and measure the return of a policy.',
      'Analyse returns, discounting and the design of RL problems.')}
''', kw=['beginner', 'expert', 'POMDP', 'reward design'])

lc(657, 'Robot Return to Origin', 'robot-return-to-origin', 'e', 'Count moves in each direction', 'The robot is back at the start when right moves equal left moves and up moves equal down moves. Tracking where actions take the agent is the job of an environment’s step function.', r"""
def judge_circle(moves):
    x = moves.count("R") - moves.count("L")
    y = moves.count("U") - moves.count("D")
    return x == 0 and y == 0
""", [('judge_circle("UD")', True), ('judge_circle("LL")', False)])
lc(70, 'Climbing Stairs', 'climbing-stairs', 'e', 'Ways to reach step n = ways to reach n &minus; 1 + ways to reach n &minus; 2', 'Build the answer from smaller ones and keep only the last two numbers. The same idea of reusing the answer from the next step gives returns backwards: G<sub>t</sub> = r + &gamma; G<sub>t+1</sub>.', r"""
def climb_stairs(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a
""", [('climb_stairs(2)', 2), ('climb_stairs(3)', 3), ('climb_stairs(10)', 89)])
lc(874, 'Walking Robot Simulation', 'walking-robot-simulation', 'm', 'Simulate one square at a time and check a set of obstacles', 'Keep a direction index into lists of x and y steps, turn by changing the index, and move one square at a time unless the next square is blocked. Track the largest squared distance. Writing a faithful step by step simulator is the first job in any RL project.', r"""
def robot_sim(commands, obstacles):
    blocked = set(map(tuple, obstacles))
    dx, dy = [0, 1, 0, -1], [1, 0, -1, 0]
    x = y = d = best = 0
    for c in commands:
        if c == -2:
            d = (d + 3) % 4
        elif c == -1:
            d = (d + 1) % 4
        else:
            for _ in range(c):
                if (x + dx[d], y + dy[d]) in blocked:
                    break
                x, y = x + dx[d], y + dy[d]
                best = max(best, x * x + y * y)
    return best
""", [('robot_sim([4, -1, 3], [])', 25), ('robot_sim([4, -1, 4, -2, 4], [[2, 4]])', 65), ('robot_sim([6, -1, -1, 6], [])', 36)])
lc(2400, 'Number of Ways to Reach a Position After Exactly k Steps', 'number-of-ways-to-reach-a-position-after-exactly-k-steps', 'm', 'Count how many of the k steps must go right', 'If the distance is d, you need (k + d) / 2 steps right and the rest left, and the parity must match. The answer is a binomial coefficient. Walks on a line are the corridor of this chapter.', r"""
def number_of_ways(start_pos, end_pos, k):
    MOD = 10 ** 9 + 7
    d = abs(end_pos - start_pos)
    if d > k or (k - d) % 2:
        return 0
    right = (k + d) // 2
    ways = 1
    for i in range(right):
        ways = ways * (k - i) // (i + 1)
    return ways % MOD
""", [('number_of_ways(1, 2, 3)', 3), ('number_of_ways(2, 5, 10)', 0)])
lc(576, 'Out of Boundary Paths', 'out-of-boundary-paths', 'm', 'Spread path counts one move at a time', 'Keep the number of ways to stand on each cell after each move. Every move that leaves the grid adds its count to the answer. Pushing counts (or probabilities) forward step by step is how the distribution of states under a policy is computed.', r"""
def find_paths(m, n, max_move, start_row, start_column):
    MOD = 10 ** 9 + 7
    count = {(start_row, start_column): 1}
    out = 0
    for _ in range(max_move):
        nxt = {}
        for (r, c), w in count.items():
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n:
                    nxt[(nr, nc)] = (nxt.get((nr, nc), 0) + w) % MOD
                else:
                    out = (out + w) % MOD
        count = nxt
    return out
""", [('find_paths(2, 2, 2, 0, 0)', 6), ('find_paths(1, 3, 3, 0, 1)', 12)])
lc(1269, 'Number of Ways to Stay in the Same Place After Some Steps', 'number-of-ways-to-stay-in-the-same-place-after-some-steps', 'h', 'Dynamic programming over position, capped at steps / 2 + 1 cells', 'Each step you may go left, go right or stay. Keep the number of ways to be at each position. You can never usefully go further than steps / 2 cells, which keeps the array small even when the corridor is huge.', r"""
def num_ways_stay(steps, arr_len):
    MOD = 10 ** 9 + 7
    width = min(arr_len, steps // 2 + 1)
    ways = [1] + [0] * (width - 1)
    for _ in range(steps):
        nxt = [0] * width
        for i in range(width):
            total = ways[i]
            if i > 0:
                total += ways[i - 1]
            if i + 1 < width:
                total += ways[i + 1]
            nxt[i] = total % MOD
        ways = nxt
    return ways[0]
""", [('num_ways_stay(3, 2)', 4), ('num_ways_stay(2, 4)', 2), ('num_ways_stay(4, 2)', 8), ('num_ways_stay(27, 7)', 127784505)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>An RL environment is a simulator, and returns are built backwards from the future. These problems practise tracking moves, building answers from later steps, simulating a robot with obstacles, counting walks on a line, and spreading counts over a grid move by move. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'simulation', 'dynamic programming', 'random walk', 'counting paths'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An <b>agent</b> observes a <b>state</b>, takes an <b>action</b>, and receives a <b>reward</b> and the next state from the <b>environment</b>.',
    'A <b>policy</b> &pi;(a | s) chooses actions. The goal is the policy with the largest expected return.',
    'The <b>return</b> G<sub>t</sub> = r<sub>t+1</sub> + &gamma; G<sub>t+1</sub> adds discounted future rewards. Small &gamma; is short sighted.',
    'The agent must balance <b>exploration</b> (learning) and <b>exploitation</b> (earning).',
    'Gymnasium’s step returns observation, reward, terminated, truncated and info. Truncated is not a real end.',
    'RL fits problems where actions shape future data and feedback is a delayed score.'],
    'Reinforcement 1.2 covers multi armed bandits: &epsilon; greedy, UCB and Thompson sampling.')}
{files('Three tasks: a discounted return, the return from every step, and a corridor simulator.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'In RL the agent learns from', ['Labelled examples', 'Rewards it receives after acting', 'Clusters', 'A teacher who gives every right action'], 1, 'Trial and error.', 'A numeric reward signal.')
K.quiz('e', 'A policy is', ['The reward function', 'A rule that chooses an action in each state', 'The environment', 'The discount factor'], 1, '&pi;(a | s).', 'It can be random or fixed.')
K.quiz('e', 'An episode is', ['One action', 'One run from a start state to an end', 'A reward', 'A neural network'], 1, 'Start to finish.', 'For example one game.')
K.quiz('e', 'With &gamma; = 0 the agent cares about', ['All future rewards equally', 'Only the next reward', 'Nothing', 'The last reward'], 1, '&gamma;<sup>k</sup> = 0 for k &ge; 1.', 'Completely short sighted.')
K.quiz('m', 'Rewards &minus;1, &minus;1, +10 with &gamma; = 1. Return from the start?', ['10', '8', '&minus;2', '12'], 1, 'Plain sum.', '&minus;1 &minus; 1 + 10.')
K.quiz('m', 'Why use &gamma; &lt; 1 in a continuing task?', ['To speed up the computer', 'To keep the return finite and prefer sooner rewards', 'It is required by Gymnasium', 'To make rewards negative'], 1, 'Geometric series.', 'Bounded by r<sub>max</sub> / (1 &minus; &gamma;).')
K.quiz('m', 'Exploration means', ['Using the best known action', 'Trying actions that may be worse to learn about them', 'Ending the episode', 'Discounting'], 1, 'Gathering information.', 'Exploitation uses what is known.')
K.quiz('m', 'In Gymnasium, truncated = True means', ['The goal was reached', 'A time limit cut the episode, so the state still has future value', 'The agent crashed', 'The reward was negative'], 1, 'Not a real end.', 'Do not treat it as terminal in updates.')
K.quiz('m', 'Gymnasium’s step(action) returns', ['Only the reward', 'Observation, reward, terminated, truncated, info', 'The policy', 'A dataset'], 1, 'Five values.', 'Since Gym 0.26 and Gymnasium.')
K.quiz('h', 'The effective horizon of &gamma; = 0.99 is about', ['10 steps', '100 steps', '1,000 steps', '1 step'], 1, '1 / (1 &minus; &gamma;).', '1 / 0.01.')
K.quiz('h', 'The main difference between RL data and supervised data is that RL data', ['Is always images', 'Depends on the agent’s own actions, so it changes as the policy changes', 'Has more labels', 'Is smaller'], 1, 'The agent creates its data.', 'Hence exploration matters.')
K.quiz('h', 'Reward hacking means', ['Stealing rewards', 'The agent finds a loophole that scores well without doing the intended task', 'Rewards are too small', 'Discounting too much'], 1, 'Specification gaming.', 'Reward design matters.')
K.quiz('x', 'In the style of a Stanford CS234 exam: a fair random walk on cells 0 to 5 starts in cell 2. Chance it reaches 5 before 0?', ['0.2', '0.4', '0.5', '0.6'], 1, 'Gambler’s ruin k / N.', '2 / 5.')
K.quiz('x', 'In the style of a Stanford CS234 exam: every reward is in [0, 1] and &gamma; = 0.9. The largest possible return is', ['1', '9', '10', 'Infinite'], 2, 'r<sub>max</sub> / (1 &minus; &gamma;).', '1 / 0.1 = 10.')

K.calc('e', 'Rewards &minus;1, &minus;1, &minus;1, +10 with &gamma; = 1. Return from the start?', '7', 'Add them.', ['&minus;1 &minus; 1 &minus; 1 = &minus;3.', 'Plus 10.', eq('&minus;3 + 10 = 7')], check=7)
K.calc('e', 'Rewards 1 then 2 with &gamma; = 0.5. Return from the start?', '2', 'r<sub>1</sub> + &gamma; r<sub>2</sub>.', ['First reward 1.', 'Second reward 2 &times; 0.5 = 1.', eq('1 + 1 = 2')], check=2)
K.calc('m', 'Rewards 0, 0, 10 with &gamma; = 0.9. Return from the start?', '8.1', '&gamma;<sup>2</sup> &times; 10.', ['The first two rewards are 0.', '0.9<sup>2</sup> = 0.81.', eq('0.81 &times; 10 = 8.1')], check=8.1)
K.calc('m', 'Reward 1 at every step forever, &gamma; = 0.9. Return?', '10', 'r / (1 &minus; &gamma;).', ['Geometric series.', '1 &minus; 0.9 = 0.1.', eq('1 / 0.1 = 10')], check=10)
K.calc('m', 'Effective horizon of &gamma; = 0.99, in steps?', '100', '1 / (1 &minus; &gamma;).', ['1 &minus; 0.99 = 0.01.', 'Invert it.', eq('1 / 0.01 = 100')], check=100)
K.calc('m', 'Next reward 2, &gamma; = 0.9, and the return from the next step is 10. G<sub>t</sub>?', '11', 'r + &gamma; G<sub>t+1</sub>.', ['&gamma; G<sub>t+1</sub> = 9.', 'Add the reward 2.', eq('2 + 9 = 11')], check=11)
K.calc('h', 'Which &gamma; makes a reward 10 steps ahead count exactly half?', '0.933', '&gamma;<sup>10</sup> = 0.5.', ['Take the 10th root.', '&gamma; = 0.5<sup>0.1</sup>.', eq('&gamma; &asymp; 0.933')], check=0.933, tol=0.001)
K.calc('h', 'Corridor: always right from cell 2 gives rewards &minus;1, &minus;1, +10. Return with &gamma; = 0.9?', '6.2', 'Discount each reward.', ['&minus;1.', '0.9 &times; (&minus;1) = &minus;0.9.', eq('0.81 &times; 10 = 8.1, total 6.2')], check=6.2)
K.calc('h', 'Fair random walk on cells 0 to 5 from cell 2. Expected number of steps until it hits an end?', '6', 'k(N &minus; k).', ['k = 2, N = 5.', 'N &minus; k = 3.', eq('2 &times; 3 = 6')], check=6)
K.calc('x', 'In the style of a Stanford CS234 problem: the random policy in the corridor (cells 0 to 5, start 2, &minus;1 per move, &plusmn;10 at the ends) has what expected total reward?', '-7', 'Expected steps and end chances.', ['6 steps on average: 5 cost &minus;1 and the last gives the end reward.', 'P(treasure) = 0.4, P(pit) = 0.6.', eq('&minus;5 + 0.4 &times; 10 + 0.6 &times; (&minus;10) = &minus;7')], check=-7)

K.assign('discounted_return', 'e', 'Discounted return',
         '<p>Write <code>discounted_return(rewards, gamma)</code> that returns r<sub>1</sub> + &gamma; r<sub>2</sub> + &gamma;<sup>2</sup> r<sub>3</sub> + ... for the list rewards, rounded to 4 decimals.</p>',
         """
def discounted_return(rewards, gamma):
    # your code here
    pass
""", [('discounted_return([-1, -1, -1, 10], 0.9)', 4.58), ('discounted_return([-1, -1, -1, 10], 1.0)', 7.0), ('discounted_return([5], 0.5)', 5.0), ('discounted_return([1, 2, 4], 0.5)', 3.0)],
         """
def discounted_return(rewards, gamma):
    G = 0.0
    for r in reversed(rewards):
        G = r + gamma * G
    return round(G, 4)
""", 'Work backwards: G = r + gamma times G.', '<p>Going backwards needs one multiplication per reward and no powers of gamma.</p>')
K.assign('returns_per_step', 'm', 'Return from every step',
         '<p>Write <code>returns_per_step(rewards, gamma)</code> that returns the list [G<sub>1</sub>, G<sub>2</sub>, ...], the return from each step to the end, each rounded to 3 decimals.</p>',
         """
def returns_per_step(rewards, gamma):
    # your code here
    pass
""", [('returns_per_step([-1, -1, -1, 10], 0.9)', [4.58, 6.2, 8.0, 10.0]), ('returns_per_step([1, 1, 1], 0.5)', [1.75, 1.5, 1.0])],
         """
def returns_per_step(rewards, gamma):
    G = 0.0
    out = []
    for r in reversed(rewards):
        G = r + gamma * G
        out.append(round(G, 3))
    return out[::-1]
""", 'Collect G while walking backwards, then reverse the list.', '<p>Monte Carlo learning (a later chapter) uses exactly these per step returns as targets for every state visited.</p>')
K.assign('corridor_run', 'm', 'Corridor simulator',
         '<p>Write <code>corridor_run(n, start, actions)</code>. Cells are 0 to n &minus; 1. Each action is &minus;1 (left) or 1 (right). A move into cell n &minus; 1 gives +10 and ends the episode, a move into cell 0 gives &minus;10 and ends it, and any other move gives &minus;1. Ignore actions after the end. Return [total reward, steps taken, final cell].</p>',
         """
def corridor_run(n, start, actions):
    # your code here
    pass
""", [('corridor_run(6, 2, [1, -1, -1, 1, 1, 1, 1])', [4, 7, 5]), ('corridor_run(6, 2, [-1, -1, 1, 1])', [-11, 2, 0]), ('corridor_run(6, 2, [1, 1])', [-2, 2, 4])],
         """
def corridor_run(n, start, actions):
    pos, total, steps = start, 0, 0
    for a in actions:
        pos += a
        steps += 1
        if pos == n - 1:
            total += 10
            break
        if pos == 0:
            total -= 10
            break
        total -= 1
    return [total, steps, pos]
""", 'Move, then check for the two ends before charging the normal move cost.', '<p>The first test replays the random episode from the lesson: total 4 after 7 steps, ending on the treasure.</p>')

K.must('Loop', 'State, action, reward, next state. The agent picks actions with a policy &pi;(a | s).')
K.must('Return', 'G<sub>t</sub> = r<sub>t+1</sub> + &gamma; G<sub>t+1</sub>. &gamma; in [0, 1]. Constant reward r gives r / (1 &minus; &gamma;).')
K.must('Goal', 'Maximise the expected return. The best policy is &pi;*.')
K.must('Trade off', 'Explore to learn, exploit to earn. &epsilon; greedy is the simplest balance.')
K.must('Gymnasium', 'reset(seed) gives obs and info. step(a) gives obs, reward, terminated, truncated, info. Truncated is not terminal.')
K.must('When to use', 'Actions change future data and feedback is a delayed score. Watch for reward hacking and sample cost.')

T = K.topic(
    slug='ml-rl-intro', topic='ml-rl-intro', step=(1, 'RL basics', 'ml-r1', 'Learn how an agent learns from rewards: returns and discounting, bandits that balance trying and using, and the Markov decision process behind every RL problem.', 'Intermediate'),
    title='Agents, rewards and returns', short='Agents and rewards', badge='1.1', minutes=40,
    lead='Start reinforcement learning: an agent acting in an environment, states, actions, rewards and policies, the discounted return, exploration against exploitation, and the Gymnasium reset and step loop.',
    desc='reinforcement learning, agent, environment, state, action, reward, policy, episode, return, discount factor, gamma, exploration, exploitation, Gymnasium, terminated, truncated, episodic task, continuing task.',
    summary='The agent and environment loop, discounted returns, policies and the explore or exploit choice, and the Gymnasium interface.',
    keywords=['reinforcement learning', 'agent', 'reward', 'return', 'discount factor', 'policy', 'exploration', 'Gymnasium', 'terminated', 'truncated'],
    recap='<p>RL learns a policy from rewards. The agent maximises the discounted return, balances exploring and exploiting, and talks to its environment through reset and step.</p>',
    added='2026-11-13', leet=leet_items())
