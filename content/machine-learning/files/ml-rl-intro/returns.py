# 1.1 Agents, rewards and returns
# Example "returns" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

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
