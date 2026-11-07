# Chapter 1.1: what AI is and intelligent agents. Source: slide Set 1 (what intelligence is, humans and other species,
# the man machine symbiosis scene and its layers of behaviour, Minsky's Society of Mind, the questions slide and
# Russell and Norvig's four approaches) and the first class transcript (18 January 2026: thinking and acting humanly or
# rationally, Turing's advice to build a baby machine). Agents, PEAS, environment types and agent programs follow
# Russell and Norvig, AIMA 4th edition, chapter 2, which the slides point to.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('reflex', r'''
# A simple reflex agent for the two square vacuum world.
# It looks only at the current percept: where it is, and whether that square is dirty.
def reflex_agent(location, status):
    if status == "Dirty":
        return "Suck"
    if location == "A":
        return "Right"
    return "Left"

# Run it for 4 time steps. Both squares start dirty.
dirt = {"A": True, "B": True}
location = "A"
score = 0
for t in range(1, 5):
    status = "Dirty" if dirt[location] else "Clean"
    action = reflex_agent(location, status)
    if action == "Suck":
        dirt[location] = False
    elif action == "Right":
        location = "B"
    else:
        location = "A"
    clean_squares = (not dirt["A"]) + (not dirt["B"])
    score = score + clean_squares
    print("time", t, "percept", [location, status], "action", action, "score", score)
''')

K.code('table', r'''
# How big must a table driven agent be?
# It needs one row for every possible sequence of percepts.
percepts = 4        # vacuum world: 2 locations times 2 states (Dirty or Clean)
total_rows = 0
for t in range(1, 6):
    rows_for_t = percepts ** t
    total_rows = total_rows + rows_for_t
    print("lifetime", t, "steps needs", total_rows, "rows")
''')

K.lesson('family', 'The big picture: AI, machine learning and deep learning', f'''
{src('Goodfellow, Bengio and Courville, Deep Learning (2016), figure 1.4, for the nested circles, and Russell and Norvig, AIMA 4th edition, section 1.3, for the history. The uploaded slides do not have this diagram, so this lesson follows those textbooks.')}
<p>People often use the words AI, machine learning, deep learning and generative AI as if they mean the same thing. They do not. They fit inside each other like circles, one inside the next. The biggest circle is AI. Machine learning is a part of AI. Deep learning is a part of machine learning. Generative AI, such as ChatGPT, is a part of deep learning.</p>
{wwh('<b>Artificial intelligence (AI)</b> is any method that makes a machine act intelligently. <b>Machine learning (ML)</b> is the part of AI where the program learns its rules from data. <b>Deep learning (DL)</b> is the part of ML that uses neural networks with many layers. <b>Generative AI</b> is the part of DL that creates new text, pictures or sound.',
     'Knowing which circle a system sits in tells you how it was built, how much data it needs, and how far you can trust and explain it. It also stops a common mistake: thinking that AI means only neural networks. Most of this course is AI that does not learn from data at all.',
     'Each inner circle answers the question "where do the rules come from?" in a narrower way. In plain AI, people write the rules or the search method. In ML, the rules are learned from examples. In DL, even the features (what to look at in the data) are learned, by many layers of a network. In generative AI, the learned network produces new content.')}
{viz('aifamily')}
{table(['', 'AI with rules and search', 'Machine learning', 'Deep learning', 'Generative AI'], [
    ['Who writes the rules', 'People', 'Learned from data', 'Learned from data', 'Learned from data'],
    ['Who picks the features', 'People', 'Mostly people', 'The network learns them', 'The network learns them'],
    ['Data needed', 'Little or none', 'Hundreds to thousands of examples', 'Often millions of examples', 'Huge amounts of text or images'],
    ['Easy to explain', 'Yes, you can follow each rule', 'Often (trees, linear models)', 'Hard', 'Hard'],
    ['Example', 'A* route finder, chess search, expert system', 'Spam filter, house price model', 'Face recognition, speech to text', 'ChatGPT, image generators'],
    ['In this course', 'Steps 1 to 8', 'Parts of steps 9 and 10', 'Advanced courses', 'Advanced courses']])}
{note('Goodfellow and colleagues draw one more circle between ML and DL: <b>representation learning</b>, methods that learn their own features, such as a shallow autoencoder. Deep learning is representation learning with many layers.', 'tip')}
<h3>How AI grew</h3>
<p>AI did not grow in a straight line. It began with rules and search in the 1950s, went through two "AI winters" when promises failed and funding was cut, moved to machine learning in the 1990s, and to deep learning after 2012 when big data and fast graphics chips (GPUs) arrived. Step through the timeline to see each milestone and which circle it belongs to.</p>
{viz('aitimeline')}
{steps('Worked example: place three systems in the circles', [
    'A sudoku solver that uses backtracking and arc consistency (chapters 5.1 and 5.2). Nobody gives it data. People wrote the method. So it is AI, but not ML.',
    'A loan approval model that learns a decision tree from 10,000 past loans. It learns its rules from data, but people chose the features (income, age, debt). So it is ML, but not DL.',
    'A program that reads X-ray images with a 50 layer convolutional network. The network learns its own features from pixels. So it is DL, and therefore also ML and AI.',
    eq('AI ⊃ ML ⊃ DL ⊃ generative AI: every inner circle is a special case of the outer one')])}
''', kw=['AI vs machine learning', 'machine learning', 'deep learning', 'generative AI', 'nested circles', 'Venn diagram', 'representation learning', 'history of AI', 'AI winter', 'Dartmouth', 'perceptron', 'AlexNet', 'transformer'])

K.lesson('idea', 'What intelligence and AI mean', f'''
{src('slide Set 1 (Introduction) and the class of 18 January 2026. Agents and environments follow Russell and Norvig, chapter 2.')}
<p>Think of the people around you. A friend sees you carrying heavy bags, guesses you need help, and holds the door. Nobody told them to. They noticed, understood, and acted. That everyday skill is what we call <b>intelligence</b>: taking in what is around you, making sense of it, and choosing a sensible action.</p>
<p><b>Artificial intelligence (AI)</b> is the study and building of machines that do the same: sense their surroundings, reason about them, and act well. The slides start with a simple question: what makes humans different from other living things? We plan, we imagine, we explain, we help each other, and we learn from very few examples.</p>
{wwh('A field that builds computer programs that perceive, reason, learn and act so as to do well at a task.',
     'Many tasks are too big, too fast or too boring for people: finding a route through a city, sorting spam, diagnosing faults, playing chess, steering a robot. AI lets a machine make those choices by itself.',
     'We describe the task as an <b>agent</b> inside an <b>environment</b>. The agent gets <b>percepts</b> through sensors, and its <b>agent program</b> picks an <b>action</b> for its actuators. AI methods (search, logic, probability, learning) are different ways to write that program.')}
<h3>The four approaches to AI</h3>
<p>Russell and Norvig sort definitions of AI along two questions: should the machine copy <b>humans</b> or be <b>rational</b> (do the right thing)? And should we judge its <b>thinking</b> or its <b>acting</b>?</p>
{table(['', 'Like a human', 'Rationally (the right thing)'], [
    ['<b>Thinking</b>', 'Thinking humanly: model how people think (cognitive science, brain studies).', 'Thinking rationally: follow correct rules of reasoning (logic, the "laws of thought").'],
    ['<b>Acting</b>', 'Acting humanly: behave so that people cannot tell it is a machine (the Turing test).', 'Acting rationally: choose the action expected to do best (the <b>rational agent</b> approach, used in this course).']])}
{note('In class the four boxes were explained like this: thinking humanly is how we think, thinking rationally is making correct decisions in our head, acting humanly is doing what we think, and acting rationally is working it out so that it leads to a real, measurable result.', 'tip')}
<p>The <b>Turing test</b> (1950): a person chats by text with a hidden machine and a hidden human. If the person cannot reliably tell which is which, the machine passes. Turing also said we should not try to build an adult mind directly, but a <b>baby machine</b> that can learn, and then teach it. The lecture repeated this idea: study babies, not adults.</p>
''', kw=['intelligence', 'artificial intelligence', 'four approaches', 'thinking humanly', 'acting rationally', 'Turing test', 'baby machine'])

K.lesson('social', 'A social machine: the man machine symbiosis scene', f'''
<p>The slides show a scene with a person and a helpful robot. To behave well in that scene the robot needs much more than a fast processor. It needs:</p>
{table(['Skill', 'What it means in plain words', 'Example in the scene'], [
    ['Social etiquette', 'Knowing polite and expected behaviour', 'Waiting for the person to finish speaking'],
    ['Intuitive psychology', 'Sensing that someone is in trouble or worried, and wanting to help', 'Noticing the person is struggling and offering a hand'],
    ['Awareness of its own limits (proprioception)', 'Knowing what its own body can and cannot do', 'Not trying to lift something too heavy'],
    ['Common sense', 'Everyday facts everyone knows', 'Glass breaks if dropped'],
    ['Domain knowledge', 'Expert facts about the task', 'How a machine is repaired'],
    ['Intuitive physics', 'A feel for how objects move and fall', 'A ball rolls down a slope']])}
<p>The slides then list the layers of behaviour such a machine shows, which come from Marvin Minsky's <b>Society of Mind</b> (1986): <b>instinctive</b> (built in reactions), <b>learned</b> (habits from experience), <b>deliberative</b> (thinking through options), <b>reflective</b> (thinking about its own thinking), <b>self reflective</b> (thinking about itself as a person with goals), and <b>self conscious</b> (caring about its values, such as "scoring a good deed point").</p>
{scene('a delivery robot in an office', '<p>A delivery robot meets a person carrying a heavy box near a closed door. An <b>instinctive</b> layer stops it from bumping into them. A <b>learned</b> layer knows doors in this building open outward. A <b>deliberative</b> layer plans: put down my parcel, open the door, wait. A <b>reflective</b> layer notices "last time I blocked the corridor, so stand to the side". The lecture said today’s agentic AI is good at the learned, deliberative and reflective layers, while self-reflection and self-consciousness are still research.</p>')}
<p>The slide draws these layers stacked one on top of the other, with innate urges and drives pushing up from below and values, censors, ideals and taboos pressing down from above. Step through it as a pyramid below. The base is the oldest and simplest kind of thinking, and each layer up looks further ahead.</p>
{viz('minsky')}
<p>The questions slide asks what thoughts are, how we build a model of the world, and what makes curiosity and creativity work. These are open research questions. This course focuses on the parts we can already build well: search, reasoning, planning, probability and learning.</p>
''', kw=['social machine', 'man machine symbiosis', 'common sense', 'intuitive physics', 'Society of Mind', 'Minsky', 'reflective'])

K.lesson('agents', 'Agents, environments and PEAS', f'''
<p>An <b>agent</b> is anything that senses its environment and acts on it. A person, a thermostat, a chess program and a self driving car are all agents.</p>
{fxs(
    fx('Agent function', 'f : P* → A', 'Maps every percept sequence (everything the agent has sensed so far, P*) to an action in the set A. It is the mathematical description of behaviour.', key=True),
    fx('Agent program', 'agent = architecture + program', 'The program runs on the physical machine (the architecture) and computes the agent function one percept at a time.'),
    fx('Rational agent', 'choose a* = argmax<sub>a</sub> E[performance | percepts so far, a]', 'For every percept sequence, pick the action that is expected to give the best performance measure, given what the agent knows.', key=True))}
<p><b>Rational is not the same as all knowing.</b> A rational agent does the best it can with the information it has. If it crosses the road after looking both ways and is hit by a falling plane, it was still rational. Rational agents also <b>gather information</b> (look before crossing) and <b>learn</b> from experience.</p>
<h3>PEAS: describing a task</h3>
<p>Before building an agent, write down its <b>P</b>erformance measure, <b>E</b>nvironment, <b>A</b>ctuators and <b>S</b>ensors.</p>
{table(['Agent', 'Performance', 'Environment', 'Actuators', 'Sensors'], [
    ['Self driving taxi', 'Safe, fast, legal, comfortable, profit', 'Roads, traffic, people, weather', 'Steering, brake, accelerator, horn, display', 'Cameras, radar, GPS, speedometer'],
    ['Medical diagnosis', 'Healthy patient, low cost', 'Patient, hospital, staff', 'Questions, tests, treatments', 'Symptoms, test results, answers'],
    ['Spam filter', 'Spam caught, real mail kept', 'Email stream, users', 'Move to spam, deliver', 'Words, sender, links'],
    ['Vacuum robot', 'Clean squares over time, little energy', 'Two squares A and B with dirt', 'Left, Right, Suck, NoOp', 'Location sensor, dirt sensor']])}
{viz('vacuum')}
{code('reflex')}
''', kw=['agent', 'percept', 'action', 'agent function', 'agent program', 'rational agent', 'PEAS', 'performance measure', 'vacuum world'])

K.lesson('envtypes', 'Kinds of environment and kinds of agent', f'''
<p>The environment decides how hard the job is. Ask six questions about it.</p>
{table(['Question', 'Easy answer', 'Hard answer', 'Example of the hard case'], [
    ['Can the agent see everything that matters?', 'Fully observable', 'Partially observable', 'Poker: you cannot see the other cards'],
    ['Is the next state fixed by the action?', 'Deterministic', 'Stochastic (random)', 'A dice game, a slippery floor'],
    ['Does each decision stand alone?', 'Episodic', 'Sequential', 'Chess: a move now matters later'],
    ['Does the world change while the agent thinks?', 'Static', 'Dynamic', 'Taxi driving'],
    ['Are states and times countable steps?', 'Discrete', 'Continuous', 'Steering angle of a car'],
    ['How many agents?', 'Single agent', 'Multi agent (competitive or cooperative)', 'Chess (competitive), football team (cooperative)']])}
{table(['Task', 'Observable', 'Deterministic', 'Episodic', 'Static', 'Discrete', 'Agents'], [
    ['Crossword puzzle', 'Fully', 'Yes', 'Sequential', 'Static', 'Discrete', 'Single'],
    ['Chess with a clock', 'Fully', 'Yes', 'Sequential', 'Semi', 'Discrete', 'Multi'],
    ['Taxi driving', 'Partially', 'Stochastic', 'Sequential', 'Dynamic', 'Continuous', 'Multi'],
    ['Image classification', 'Fully', 'Yes', 'Episodic', 'Static', 'Continuous', 'Single']])}
<h3>Four kinds of agent program, from simple to clever</h3>
{steps('From simple to clever', [
    '<b>Simple reflex agent</b>: if this, then that. It looks only at the current percept. Fast, but it fails when it cannot see the whole state.',
    '<b>Model based reflex agent</b>: keeps an internal state (a model of the world it cannot see right now), updated from each percept.',
    '<b>Goal based agent</b>: knows what it wants to reach, and searches or plans a sequence of actions to get there. This is where search (chapters 1.2 to 4.2) comes in.',
    '<b>Utility based agent</b>: when many outcomes reach the goal, prefers the ones with higher utility (happiness). It handles trade offs and uncertainty.',
    '<b>Learning agent</b>: any of the above, plus a part that improves the program from feedback (a critic and a learning element). Reinforcement learning, chapter 10, is one way.'])}
{code('table')}
{note('A table driven agent stores one action for every possible percept sequence. With 4 percepts and a lifetime of T steps it needs 4 + 4² + ... + 4<sup>T</sup> rows. For a taxi camera this number is larger than the atoms in the universe. Agent programs exist to produce good behaviour from a small program instead of a huge table.', 'warn')}
''', kw=['environment types', 'fully observable', 'partially observable', 'deterministic', 'stochastic', 'episodic', 'sequential', 'static', 'dynamic', 'simple reflex agent', 'model based agent', 'goal based agent', 'utility based agent', 'learning agent'])

K.lesson('maths', 'The maths behind a rational agent', f'''
<p>Two small formulas sit under the whole course.</p>
{fxs(
    fx('Performance over a lifetime', 'U = ∑<sub>t=1</sub><sup>T</sup> r<sub>t</sub>', 'Add up the score r<sub>t</sub> earned at each time step t. In the vacuum world r<sub>t</sub> = number of clean squares (minus 1 per move if moving costs energy).'),
    fx('Expected performance of an action', 'E[U | a] = ∑<sub>s′</sub> P(s′ | a) U(s′)', 'Weight each possible result s′ by its probability. A rational agent picks the action with the largest value.', key=True),
    fx('Size of a table driven agent', 'rows = ∑<sub>t=1</sub><sup>T</sup> |P|<sup>t</sup> = |P|(|P|<sup>T</sup> − 1) ⁄ (|P| − 1)', '|P| is the number of different percepts, T the lifetime. A geometric series, so it grows exponentially in T.', key=True))}
{steps('Worked example: which action is rational?', [
    'A delivery robot can take the lift or the stairs. The lift arrives in time with probability 0.7 and then scores 10. If it is late it scores 2.',
    'The stairs always arrive, but slowly, and score 7.',
    eq('E[lift] = 0.7 × 10 + 0.3 × 2 = 7 + 0.6 = 7.6'),
    eq('E[stairs] = 1 × 7 = 7'),
    'The rational choice is the lift, 7.6 against 7, even though the lift is sometimes late. Rational means best on average with what you know, not lucky every time.'])}
{steps('Worked example: vacuum score', [
    'Both squares dirty, agent in A, simple reflex agent, 4 time steps, no move cost.',
    'Time 1: Suck in A. A is clean, B dirty. Score +1, total 1.',
    'Time 2: Right. Still 1 clean square. Total 2.',
    'Time 3: Suck in B. Both clean. +2, total 4.',
    eq('Time 4: Left. Both clean, +2. Total = 6')])}
''', kw=['performance measure', 'expected utility', 'geometric series', 'table driven agent', 'rational choice'])

K.lesson('compare', 'How the rational agent view compares', f'''
{versus('Four ways to define AI', ['Approach', 'Strength', 'Weakness', 'Used today for'], [
    ['Thinking humanly', 'Explains human minds', 'Hard to test, we do not fully know how people think', 'Cognitive science, user models'],
    ['Thinking rationally', 'Exact, provable logic', 'Not everything is certain, and logic alone can be slow', 'Theorem provers, verification'],
    ['Acting humanly', 'Clear test (Turing test)', 'Copies human mistakes too, says little about how', 'Chatbots, games'],
    ['Acting rationally', 'Measurable, general, works with uncertainty', 'Needs a good performance measure', 'Almost all modern AI systems']],
    'acting rationally is the most useful definition for engineering, because we can measure it and improve it. That is why this course builds rational agents.')}
{versus('Kinds of agent program', ['Agent', 'Memory', 'Looks ahead?', 'Good when'], [
    ['Table driven', 'Huge table', 'No', 'Never in practice, only as a thought experiment'],
    ['Simple reflex', 'None', 'No', 'Fully observable, simple rules'],
    ['Model based', 'Internal state', 'No', 'Partially observable worlds'],
    ['Goal based', 'State + goal', 'Yes, by search or planning', 'Many steps are needed to reach a goal'],
    ['Utility based', 'State + utility', 'Yes, weighs trade offs', 'Several goals, risk, uncertainty'],
    ['Learning', 'Changes itself', 'Depends on the base agent', 'The world is unknown or changing']],
    'move up the list only when the task needs it. A thermostat is a fine simple reflex agent. A taxi needs a learning, utility based agent.')}
''', kw=['comparison', 'four approaches', 'agent types', 'rational agent'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>An AI is a machine that notices what is going on and picks a good thing to do, like a helpful friend who sees you need help and opens the door.</p>',
    '<p>An agent maps percept sequences to actions. Describe the task with PEAS and the environment with its six properties. Pick the simplest agent program (reflex, model based, goal based, utility based, learning) that works.</p>',
    '<p>A rational agent maximises expected performance given its percept history and prior knowledge. Partial observability forces the agent to keep a belief state. Sequential, stochastic tasks lead to Markov decision processes (chapter 10.1).</p>',
    '<p>Bounded rationality (Simon) asks what is optimal when computing itself is costly. Open questions include how to specify the performance measure so that it matches what people really want (the value alignment problem), and how common sense and the reflective layers of the slides can be learned rather than hand written.</p>')}
{deep('why rationality is defined for each percept sequence', '<p>Rationality depends on four things: the performance measure, the agent\'s prior knowledge, the actions it can take, and the percept sequence so far. Two agents with the same actions can both be rational yet act differently, because one knows more. This is why we say "rational given what it knows", and why gathering information can itself be the rational action.</p>')}
{deep('the research view: from Turing to large language models', '<p>AI as a field began at the Dartmouth workshop in 1956. Early systems used logic and search (1956 to 1970s), then expert systems (1980s), then probability and machine learning (1990s and 2000s), then deep learning (2012 onward) and large language models (2020s). Each wave added a new way to write the agent program. The agent view of this chapter covers all of them.</p>')}
{note('A rational agent is not one that is always right. It is one that chooses the best action given what it knows. Bad luck does not make a choice irrational.', 'exam')}
''', kw=['bounded rationality', 'value alignment', 'Dartmouth 1956', 'history of AI'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'AI ⊃ machine learning ⊃ deep learning ⊃ generative AI. AI grew from rules and search (1950s), through two AI winters, to learning from data (1990s) and deep networks (2012 on).',
    'Intelligence means sensing, understanding and choosing a good action. AI builds machines that do this.',
    'Minsky’s six layers run from instinctive reactions at the base to self-conscious emotion at the top. Today’s agentic AI handles the learned, deliberative and reflective layers.',
    'Four approaches: thinking or acting, humanly or rationally. This course builds <b>rational agents</b>: act to get the best expected performance.',
    'An agent maps percept sequences to actions. Describe a task with <b>PEAS</b> and the environment by observability, determinism, episodes, change, discreteness and number of agents.',
    'Agent programs grow from simple reflex to model based, goal based, utility based and learning agents. A table driven agent is impossible in practice because it needs ∑ |P|<sup>t</sup> rows.',
    'A social machine needs etiquette, intuitive psychology, common sense and layers from instinctive to self conscious behaviour (Minsky).'],
    'chapter 1.2 turns a goal into a search problem, the first tool a goal based agent needs.')}
{nbcard('what-is-ai', 'Run the vacuum agent, count table sizes, and write your own reflex agent and table size function.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which approach to AI does this course follow?', ['Thinking humanly', 'Acting humanly', 'Thinking rationally', 'Acting rationally'], 3,
       'Do the right thing.', 'We build rational agents: they act to get the best expected performance.')
K.quiz('e', 'Which order is correct, from the biggest circle to the smallest?', ['ML, AI, DL', 'AI, ML, DL', 'DL, ML, AI', 'AI, DL, ML'], 1,
       'The nested circles.', 'Deep learning is a part of machine learning, which is a part of AI.')
K.quiz('m', 'A spam filter that learns word probabilities from marked emails with naive Bayes is', ['AI but not ML', 'ML but not DL', 'DL', 'not AI'], 1,
       'Does it learn? Does it have a deep network?', 'It learns from data, so it is ML, but it has no many layer network.')
K.quiz('m', 'In Minsky’s layers, "Action A does not solve my problem, so try action B" is', ['an instinctive reaction', 'a learned reaction', 'deliberative thinking', 'self-conscious emotion'], 2,
       'Choosing between options.', 'Deliberation picks among options A, B and C. Reflection looks back afterwards.')
K.quiz('e', 'What does the P in PEAS stand for?', ['Percept', 'Performance measure', 'Program', 'Probability'], 1,
       'How we score the agent.', 'PEAS = Performance measure, Environment, Actuators, Sensors.')
K.quiz('e', 'A simple reflex agent chooses its action using', ['Its whole percept history', 'Only the current percept', 'A plan', 'A utility function'], 1,
       'If this, then that.', 'It matches the current percept against condition action rules.')
K.quiz('e', 'The Turing test checks whether a machine', ['Thinks like a human brain', 'Can fool a judge into thinking it is human in a text chat', 'Is rational', 'Can play chess'], 1,
       'Imitation game.', 'It is an acting humanly test.')
K.quiz('m', 'Poker is', ['Fully observable', 'Partially observable', 'Episodic', 'Single agent'], 1,
       'Can you see every card?', 'The other players\' cards are hidden, so it is partially observable.')
K.quiz('m', 'Which agent keeps an internal state to handle what it cannot see right now?', ['Simple reflex', 'Model based reflex', 'Table driven', 'Random'], 1,
       'A model of the world.', 'It updates the state from each percept and its knowledge of how the world changes.')
K.quiz('m', 'An agent crosses after looking both ways and is hit by a falling plane. Was it rational?', ['No, it was hurt', 'Yes, it acted best on what it could know', 'Only if it survived', 'Rationality does not apply'], 1,
       'Rational is not all knowing.', 'Rationality is judged on the percepts and knowledge available, not on the outcome.')
K.quiz('m', 'Which layer from the slides means "thinking about its own thinking"?', ['Instinctive', 'Learned', 'Reflective', 'Deliberative'], 2,
       'Reflect.', 'Reflective behaviour examines the agent\'s own reasoning, a step above deliberative planning.')
K.quiz('h', 'A vacuum agent has 4 possible percepts and a lifetime of 3 steps. How many rows does a table driven agent need?', ['12', '64', '84', '81'], 2,
       '4 + 16 + 64.', 'One row per percept sequence of length 1, 2 and 3: 4 + 16 + 64 = 84.')
K.quiz('h', 'Taxi driving is', ['Fully observable, deterministic, static', 'Partially observable, stochastic, dynamic, continuous, multi agent', 'Episodic and discrete', 'Single agent and static'], 1,
       'The hardest of every pair.', 'Taxi driving is the textbook example of the hardest environment.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: a vacuum world is partially observable (the agent senses only dirt in its own square) and moves cost 1. Which agent can guarantee to stop moving once both squares are clean?', ['A simple reflex agent', 'A model based agent that remembers each square it has cleaned or seen clean', 'A table driven agent with a lifetime of 1', 'No agent can'], 1,
       'It must remember.', 'Without memory it cannot know the other square is clean. A model based agent records it and then chooses NoOp, avoiding the move cost.')
K.quiz('x', 'In the style of an MIT 6.034 question: which statement about rationality is FALSE?', ['It depends on the performance measure', 'It depends on the percept sequence so far', 'A rational agent never makes a bad outcome', 'Information gathering can be rational'], 2,
       'Luck.', 'Rational agents maximise expected performance. Bad outcomes can still happen.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Vacuum world: 2 locations and each square is Dirty or Clean. How many different percepts [location, status] are there?', '4', 'Multiply the choices.',
       ['Location: A or B, 2 choices.', 'Status of that square: Dirty or Clean, 2 choices.', eq('2 × 2 = 4')], check=4)
K.calc('e', 'Score the simple reflex agent for 4 steps when both squares start dirty and it starts in A (no move cost).', '6', 'Count clean squares after each step.',
       ['After step 1 (Suck A): 1 clean.', 'After step 2 (Right): 1 clean. After step 3 (Suck B): 2 clean.', eq('1 + 1 + 2 + 2 = 6')], check=6)
K.calc('e', 'Lift or stairs: lift arrives in time with 0.7 (score 10) or late (score 2). What is E[lift]?', '7.6', 'Weight each result by its probability.',
       ['0.7 × 10 = 7.', '0.3 × 2 = 0.6.', eq('E[lift] = 7.6')], check=7.6)
K.calc('m', 'A table driven agent has 4 percepts and a lifetime of 3 steps. How many rows?', '84', 'Sum 4 to the power t for t = 1 to 3.',
       ['4¹ = 4.', '4² = 16 and 4³ = 64.', eq('4 + 16 + 64 = 84')], check=84)
K.calc('m', 'Same agent with a lifetime of 10 steps. How many rows? Use |P|(|P|<sup>T</sup> − 1) ⁄ (|P| − 1).', '1398100', 'A geometric series.',
       ['|P| = 4, T = 10, so 4¹⁰ = 1,048,576.', '4 × (1,048,576 − 1) = 4,194,300.', eq('4,194,300 ⁄ 3 = 1,398,100')], check=1398100)
K.calc('m', 'With a move cost of 1, score the reflex agent for 6 steps (both dirty, starts in A).', '6', 'From step 4 it keeps moving.',
       ['Step 1 Suck: +1. Step 2 Right: +1 − 1 = 0. Step 3 Suck: +2.', 'Steps 4, 5, 6 are moves with both clean: +2 − 1 = +1 each.', eq('1 + 0 + 2 + 1 + 1 + 1 = 6')], check=6)
K.calc('m', 'Same setting, model based agent that says NoOp once it knows both are clean. Score for 6 steps?', '9', 'NoOp costs nothing.',
       ['Steps 1 to 3 as before: 1 + 0 + 2 = 3.', 'Steps 4 to 6: NoOp, +2 each = 6.', eq('3 + 6 = 9')], check=9)
K.calc('h', 'A taxi camera gives 30 frames a second. Suppose each frame could be one of only 1000 different images. Roughly how many digits does the table size for one minute have? (Count digits of 1000 to the power 1800.)', '5401', 'One minute is 1800 frames.',
       ['Frames in a minute: 30 × 60 = 1800.', 'The last term 1000¹⁸⁰⁰ = 10⁵⁴⁰⁰ dominates the sum.', eq('10⁵⁴⁰⁰ has 5401 digits'), 'Far beyond the about 10⁸⁰ atoms in the universe.'], check=5401)
K.calc('h', 'An action succeeds with probability p and scores 10, otherwise 2. Another action always scores 7. For which p are they equal? Two decimals.', '0.63', 'Solve 10p + 2(1 − p) = 7.',
       ['10p + 2 − 2p = 7.', '8p = 5.', eq('p = 0.625, about 0.63')], check=0.625, tol=0.006)
K.calc('x', 'In the style of a Stanford CS221 problem: an agent gets reward 1 per time step while a task is done and pays 0.2 per action. Doing the task takes 3 actions and then it stays done. Over 10 steps, what is the total with 3 actions then 7 NoOps (reward starts the step after the third action)?', '6.4', 'Count rewarded steps.',
       ['Actions at steps 1, 2, 3 cost 3 × 0.2 = 0.6.', 'Done from step 4 to 10: 7 steps × 1 = 7.', eq('7 − 0.6 = 6.4')], check=6.4)

# ---------------------------------------------------------------- assignments
K.assign('reflex', 'e', 'Write a simple reflex vacuum agent',
         '<p>Write <code>reflex_agent(location, status)</code>. location is "A" or "B", status is "Dirty" or "Clean". Return "Suck" if dirty, otherwise "Right" in A and "Left" in B.</p>',
         '''
def reflex_agent(location, status):
    # your code here
    pass
''', [("reflex_agent('A', 'Dirty')", 'Suck'), ("reflex_agent('A', 'Clean')", 'Right'), ("reflex_agent('B', 'Clean')", 'Left'), ("reflex_agent('B', 'Dirty')", 'Suck')],
         '''
def reflex_agent(location, status):
    if status == "Dirty":
        return "Suck"
    if location == "A":
        return "Right"
    return "Left"
''', 'Check the dirt first, then the location.', '<p>Three rules cover every percept. That is all a simple reflex agent is.</p>')
K.assign('tablesize', 'm', 'Size of a table driven agent',
         '<p>Write <code>table_size(percepts, lifetime)</code> that returns the number of rows a table driven agent needs: percepts¹ + percepts² + ... + percepts<sup>lifetime</sup>.</p>',
         '''
def table_size(percepts, lifetime):
    # your code here
    pass
''', [("table_size(4, 3)", 84), ("table_size(4, 10)", 1398100), ("table_size(2, 1)", 2)],
         '''
def table_size(percepts, lifetime):
    total = 0
    for t in range(1, lifetime + 1):
        total = total + percepts ** t
    return total
''', 'Loop t from 1 to lifetime and add percepts to the power t.', '<p>The numbers explode, which is the whole point: good agents are small programs, not giant tables.</p>')

K.must('Definition', 'AI builds agents that perceive and act. This course uses the acting rationally view: choose the action with the best expected performance.')
K.must('PEAS', 'Describe any task by Performance measure, Environment, Actuators, Sensors.')
K.must('Environment types', 'Fully or partially observable, deterministic or stochastic, episodic or sequential, static or dynamic, discrete or continuous, single or multi agent.')
K.must('Agent programs', 'Simple reflex, model based, goal based, utility based, learning. Table driven needs ∑ |P|<sup>t</sup> rows, so it is impossible.')
K.must('Rational, not perfect', 'Rationality depends on the performance measure, prior knowledge, available actions and percepts so far. Bad luck is not irrational.')
K.must('The AI family', 'AI ⊃ ML ⊃ DL ⊃ generative AI. ML learns rules from data, DL also learns the features with many layer networks. Most of Core AI is rules and search.')
K.must('Social machine', 'Needs etiquette, intuitive psychology, common sense, intuitive physics and layers from instinctive to self conscious (Minsky, Society of Mind).')

T = K.topic(
    slug='what-is-ai', topic='what-is-ai', step=(1, 'Intelligence, agents and problems', 'cai-found', 'What AI is, how an agent senses and acts, and how a goal becomes a search problem.', 'School and college'),
    title='What AI is and intelligent agents', short='What AI is', badge='1.1', minutes=45,
    lead='See how AI, machine learning, deep learning and generative AI fit inside each other and how AI grew, what intelligence and AI mean, the four approaches to AI, what a social machine needs, and how every AI system can be described as an agent that senses its environment and acts.',
    desc='AI, machine learning, deep learning and generative AI as nested circles, a timeline of AI from 1950 to 2022, intelligence and AI, the four approaches of Russell and Norvig, the Turing test, the social machine scene and Minsky’s six layers as a pyramid from the slides, agents, PEAS, environment types and the five kinds of agent program.',
    summary='The four approaches to AI, rational agents, PEAS, environment types, the social machine and the five kinds of agent program.',
    keywords=['artificial intelligence', 'machine learning', 'deep learning', 'generative AI', 'history of AI', 'rational agent', 'PEAS', 'Turing test', 'environment types', 'reflex agent', 'agent program'],
    recap='<p>AI builds rational agents: given what they have sensed, they pick the action with the best expected performance. Describe the task with PEAS and choose the simplest agent program that copes with its environment.</p>',
    nb={'reflex': 'A simple reflex agent cleaning two squares', 'table': 'How fast a table driven agent grows'})
