# Chapter 4.2: genetic algorithms. Source: slide Set 2, slides 84 to 87 (genes and chromosomes, crossover and
# mutation with flip, switch and scramble, roulette wheel and tournament selection, the worked example that
# maximises f(x) = x^2 over 5 bit strings with its tables, and the comparison table of hill climbing, simulated
# annealing and genetic algorithms) and the class of 1 February 2026. The 8 queens example and the schema theorem
# follow Russell and Norvig, AIMA 4th ed., section 4.1.4, and Holland (1975).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()

K.code('gen1', r'''
# One generation of the slide example: maximise f(x) = x * x where x is a 5 bit number.
population = ["01101", "11000", "01000", "10011"]

fitness = []
for s in population:
    x = int(s, 2)                       # read the bits as a whole number
    fitness.append(x * x)
total = sum(fitness)
average = total / len(fitness)
print("fitness:", fitness, " total:", total, " average:", average)

for i in range(4):
    p = fitness[i] / total              # chance of being picked by the roulette wheel
    expected = fitness[i] / average     # expected number of copies in the mating pool
    print(population[i], " p =", round(p, 2), " expected copies =", round(expected, 2))

def crossover(a, b, cut):
    return a[:cut] + b[cut:], b[:cut] + a[cut:]

# the slide mating pool: string 2 twice, string 3 dropped. Pairs and cut points from the slide.
print(crossover("01101", "11000", 4))   # -> 01100 and 11001
print(crossover("11000", "10011", 2))   # -> 11011 and 10000
''')

K.code('roulette', r'''
# Roulette wheel selection: each string gets a slice of the wheel as big as its fitness.
import random
random.seed(1)

population = ["01101", "11000", "01000", "10011"]
fitness = [169, 576, 64, 361]

def spin():
    point = random.random() * sum(fitness)   # where the ball stops
    running = 0
    for i in range(len(fitness)):
        running = running + fitness[i]
        if point < running:
            return population[i]
    return population[-1]

counts = {}
for k in range(20):
    s = spin()
    counts[s] = counts.get(s, 0) + 1
print(counts)       # 11000 (fitness 576) should come up most often
''')

K.lesson('idea', 'Search by evolution', f'''
{src('slide Set 2, slides 84 to 87, and the class of 1 February 2026.')}
{wwh('A genetic algorithm (GA) keeps a population of candidate solutions, each written as a string (a chromosome) of genes. Better solutions are more likely to be chosen as parents, and children are made by mixing parents (crossover) and making small random changes (mutation).',
     'It searches many regions at once, so it is less likely to get stuck than one hill climber. Crossover can join good parts found by different parents into one better solution.',
     'Each generation: measure the fitness of every individual, select parents in proportion to fitness, cross them over at a random point, mutate a few genes, and replace the old population with the children. Repeat for many generations or until a good enough solution appears.')}
{table(['Word', 'Meaning', 'In the x² example'], [
    ['Gene', 'One encoded decision value', 'One bit'],
    ['Chromosome (individual)', 'A full candidate solution, a string of genes', '01101'],
    ['Population', 'The set of individuals in one generation', '4 strings'],
    ['Fitness function', 'How good an individual is (higher is better)', 'f(x) = x², with x the number the bits encode'],
    ['Selection', 'Choosing parents, fitter ones more often', 'Roulette wheel'],
    ['Crossover', 'Swap the tails of two parents after a cut point', '0110|1 and 1100|0 give 01100 and 11001'],
    ['Mutation', 'A small random change', 'Flip one bit']])}
{algo('Genetic algorithm', [
    'function GENETIC-ALGORITHM(population, FITNESS):',
    '    repeat:',
    '        new_population = empty',
    '        for i = 1 to size(population):',
    '            x = RANDOM-SELECTION(population, FITNESS)',
    '            y = RANDOM-SELECTION(population, FITNESS)',
    '            child = REPRODUCE(x, y)          # crossover at a random cut point',
    '            with a small probability: child = MUTATE(child)',
    '            add child to new_population',
    '        population = new_population',
    '    until some individual is fit enough, or enough time has passed',
    '    return the best individual'])}
''', kw=['genetic algorithm', 'population', 'chromosome', 'gene', 'fitness', 'selection', 'crossover', 'mutation'])

K.lesson('example', 'The slide example: maximise x² with 5 bits', f'''
{src('slide Set 2, slide 85.')}
<p>Find the 5 bit number x (0 to 31) that maximises f(x) = x². We know the answer is 11111 = 31, which lets us watch the GA head toward it. Start with four random strings.</p>
{table(['String', 'x', 'f(x) = x²', 'P(pick) = f ⁄ ∑f', 'Expected copies = f ⁄ average', 'Actual copies'], [
    ['01101', '13', '169', '0.14', '0.58', '1'],
    ['11000', '24', '576', '0.49', '1.97', '2'],
    ['01000', '8', '64', '0.05 (the slide rounds to 0.06)', '0.22', '0'],
    ['10011', '19', '361', '0.31', '1.23', '1'],
    ['Total', '', '1170', '1.00', '4.00', '4'],
    ['Average', '', '292.5 (the slide rounds to 293)', '', '', ''],
    ['Maximum', '', '576', '', '', '']])}
{steps('Making the next generation', [
    'Selection: the mating pool is 01101, 11000, 11000, 10011. The best string gets two copies, the worst none.',
    'Pair 1: 0110|1 and 1100|0, cut after bit 4. Children 01100 (x = 12, f = 144) and 11001 (x = 25, f = 625).',
    'Pair 2: 11|000 and 10|011, cut after bit 2. Children 11011 (x = 27, f = 729) and 10000 (x = 16, f = 256).',
    'New total 144 + 625 + 729 + 256 = 1754, average 438.5, maximum 729.',
    eq('in one generation the average rose from 292.5 to 438.5 and the best from 576 to 729')])}
{note('The slide table lists x = 10 for the string 10000. In binary 10000 is 16, and 16² = 256 matches the f column, so x should read 16.', 'warn')}
{viz('genetic', mode='slide', pop='01101 11000 01000 10011', gens=1, mu=0)}
{code('gen1')}
''', kw=['x squared example', 'roulette wheel', 'expected copies', 'crossover point', 'fitness table'])

K.lesson('operators', 'Selection, crossover and mutation in detail', f'''
{table(['Selection method', 'How it works', 'Strength', 'Weakness'], [
    ['Roulette wheel (fitness proportionate)', 'P(i) = f<sub>i</sub> ⁄ ∑f. Spin a wheel with slices sized by fitness', 'Simple, matches the theory', 'One very fit individual can take over too early. Needs positive fitness'],
    ['Tournament', 'Pick k individuals at random, the fittest of them wins', 'Easy to tune with k, works with any fitness scale', 'Large k is very greedy'],
    ['Rank', 'Sort by fitness, pick by rank, not by raw value', 'Not fooled by huge fitness gaps', 'Ignores how much better the best is'],
    ['Elitism', 'Copy the best few unchanged into the next generation', 'Never loses the best found so far', 'Can reduce diversity']])}
{code('roulette')}
{table(['Operator (slide 84)', 'Example', 'Note'], [
    ['One point crossover', 'AB|CD and MN|OP give ABOP and MNCD', 'The cut point is chosen at random'],
    ['Two point and uniform crossover', 'Swap a middle segment, or each gene with chance 0.5', 'Mix more freely'],
    ['Flip mutation', '01101 → 01001', 'For bit strings'],
    ['Switch (swap) mutation', 'ABCD → ADCB', 'Keeps a permutation valid, for example a tour'],
    ['Scramble mutation', 'ABCD → ACBD (shuffle a segment)', 'Bigger jump']])}
{note('For problems like the travelling salesperson, plain one point crossover makes invalid tours (a city twice). Use order crossover or swap mutation, which always give valid permutations.', 'warn')}
''', kw=['roulette wheel', 'tournament selection', 'rank selection', 'elitism', 'one point crossover', 'flip mutation', 'swap mutation', 'scramble'])

K.lesson('queens', 'A GA for 8 queens', f'''
<p>AIMA writes an 8 queens state as 8 digits, the row of the queen in each column, for example 24748552. The fitness is the number of <b>non attacking</b> pairs, at most 28 for a solution.</p>
{steps('Selection in the AIMA example', [
    'Four boards have fitness 24, 23, 20 and 11. The total is 78.',
    'Selection chances: 24 ⁄ 78 = 31 percent, 23 ⁄ 78 = 29 percent, 20 ⁄ 78 = 26 percent, 11 ⁄ 78 = 14 percent.',
    'Crossover joins the left columns of one parent with the right columns of the other.',
    eq('if each parent has its queens placed well on one side, the child can be good on both sides')])}
{fxs(
    fx('Fitness for 8 queens', 'fitness = 28 − (number of attacking pairs)', '28 is the number of pairs among 8 queens, 8 × 7 ⁄ 2.'),
    fx('Search space for the digit string', '8<sup>8</sup> ≈ 16.8 million', 'The same as for hill climbing on 8 queens.'))}
{note('Crossover helps when nearby genes form meaningful blocks, like the left half of the board. If the encoding scatters related decisions, crossover mostly breaks good solutions, and a GA is no better than random restarts.', 'tip')}
''', kw=['8 queens GA', 'non attacking pairs', 'encoding', 'building blocks'])

K.lesson('maths', 'The maths: selection pressure and schemata', f'''
{fxs(
    fx('Roulette wheel probability', 'P(i) = f<sub>i</sub> ⁄ ∑<sub>j</sub> f<sub>j</sub>', 'Expected copies of i in a population of n: n P(i) = f<sub>i</sub> ⁄ f̄.', key=True),
    fx('Schema theorem (Holland)', 'E[m(H, t + 1)] ≥ m(H, t) · (f(H) ⁄ f̄) · [1 − p<sub>c</sub> δ(H) ⁄ (l − 1) − o(H) p<sub>m</sub>]', 'm(H, t) individuals match schema H (like 1***1). f(H) is their average fitness, δ(H) the defining length, o(H) the order (fixed positions), l the string length, p<sub>c</sub> and p<sub>m</sub> the crossover and mutation rates.'),
    fx('Chance a string escapes mutation', '(1 − p<sub>m</sub>)<sup>l</sup>', 'With p<sub>m</sub> = 0.01 and l = 5: 0.99⁵ ≈ 0.951.'))}
{steps('Worked example: the schema 1**** in the slide example', [
    'Strings matching 1****: 11000 (576) and 10011 (361). m = 2, average f(H) = (576 + 361) ⁄ 2 = 468.5.',
    'Population average f̄ = 292.5.',
    'δ(H) = 0 (one fixed position) and o(H) = 1, so crossover cannot break it. With no mutation the factor in brackets is 1.',
    eq('E[m] ≥ 2 × 468.5 ⁄ 292.5 ≈ 3.2 copies next generation (all 4 children start with 1 except 01100)')])}
{note('Short, low order schemata with above average fitness grow exponentially. These are the "building blocks" that crossover combines.', 'tip')}
''', kw=['schema theorem', 'building blocks', 'selection pressure', 'mutation rate'])

K.lesson('compare', 'Comparing hill climbing, annealing and genetic algorithms', f'''
{src('slide Set 2, slide 86.')}
{versus('The slide 86 comparison', ['Feature', 'Hill climbing', 'Simulated annealing', 'Genetic algorithm'], [
    ['Inspiration', 'Climbing a hill', 'Annealing in metallurgy', 'Natural selection and evolution'],
    ['Search space', 'Local', 'Broad (with controlled randomness)', 'Very broad (population based)'],
    ['Moves to worse solutions', 'No', 'Yes (probabilistic)', 'Yes (via mutation and crossover)'],
    ['Avoids local optima', 'No', 'Yes', 'Yes'],
    ['Memory usage', 'Low', 'Medium', 'High'],
    ['Parameter tuning needed', 'Minimal', 'High (temperature, cooling)', 'High (population, mutation rate)'],
    ['Speed', 'Fast', 'Moderate', 'Slower (population evolution)'],
    ['Complexity', 'Simple', 'Moderate', 'High'],
    ['Best use case', 'Small or simple problems', 'Problems with many local optima', 'Complex optimisation problems']],
    'a GA is worth its cost when good solutions are built from parts that can be found separately and combined. Otherwise annealing or restarts are simpler.')}
{scene('designing an antenna', '<p>NASA used an evolutionary algorithm to design the antenna of the ST5 spacecraft (2006). Each individual was a sequence of bending and branching instructions. The fitness came from a simulation of the radio pattern. The evolved shape looked like a bent paper clip that no engineer would draw, yet it met the mission needs, which is the classic strength of evolutionary search: it does not need intuition about what a good design looks like.</p>')}
''', kw=['comparison', 'slide 86', 'NASA antenna', 'evolutionary design'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A genetic algorithm copies nature: the fitter animals have more children, children mix their parents, and small random changes sometimes help. Over many generations the population gets better.</p>',
    '<p>Encode solutions as strings, choose parents by fitness (roulette, tournament, rank, elitism), cross over at a random point, mutate with a small probability. In the slide example the average fitness rose from 292.5 to 438.5 in one generation.</p>',
    '<p>The schema theorem explains why short, fit building blocks spread. Diversity matters: too much selection pressure leads to premature convergence on one local optimum. Encodings must keep children valid (order crossover for permutations).</p>',
    '<p>Research descendants include evolution strategies with self adapted mutation (CMA-ES), genetic programming that evolves programs as trees, neuroevolution of network weights and shapes (NEAT), and multi objective GAs (NSGA-II) that return a Pareto front of trade offs instead of one answer.</p>')}
''', kw=['schema', 'premature convergence', 'CMA-ES', 'genetic programming', 'NEAT', 'NSGA-II'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A <b>genetic algorithm</b> evolves a population of chromosomes (strings of genes) using a fitness function.',
    'Each generation: <b>selection</b> by fitness, <b>crossover</b> at a cut point, <b>mutation</b> with a small probability.',
    'Roulette wheel: P(i) = f<sub>i</sub> ⁄ ∑f, expected copies f<sub>i</sub> ⁄ f̄. Slide example: 169, 576, 64, 361, total 1170, chances 0.14, 0.49, 0.06, 0.31.',
    'After one generation the children are 01100, 11001, 11011, 10000 with best fitness 729 (x = 27).',
    'Crossover helps when good solutions are built from blocks. GAs search broadly but use more memory and need more tuning than hill climbing or annealing.'],
    'chapter 5.1 turns to problems with explicit constraints: constraint satisfaction.')}
{nbcard('genetic-algorithms', 'Compute the slide fitness table, spin a roulette wheel, then write crossover, mutation and one full generation yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'In a genetic algorithm, a chromosome is', ['One bit', 'A full candidate solution', 'The fitness function', 'The population size'], 1,
       'A string of genes.', 'Each individual is one chromosome.')
K.quiz('e', 'Which operator swaps the tails of two parents after a cut point?', ['Mutation', 'Selection', 'Crossover', 'Elitism'], 2,
       'Two parents.', 'Crossover mixes the parents.')
K.quiz('e', 'In the slide example, what is the fitness of 11000?', ['24', '576', '361', '169'], 1,
       'x = 24.', '24² = 576.')
K.quiz('e', 'Roulette wheel selection picks an individual with probability', ['Equal for all', 'Proportional to its fitness', 'Proportional to its length', 'Only the best'], 1,
       'Slice size.', 'P(i) = f<sub>i</sub> ⁄ ∑f.')
K.quiz('m', 'Crossing 0110|1 with 1100|0 after bit 4 gives', ['01100 and 11001', '01101 and 11000', '01000 and 11101', '11100 and 01001'], 0,
       'Swap the last bit.', '0110 + 0 = 01100 and 1100 + 1 = 11001.')
K.quiz('m', 'Which selection method never loses the best individual?', ['Roulette wheel', 'Tournament', 'Elitism', 'Random'], 2,
       'Copy it unchanged.', 'Elitism keeps the best few as they are.')
K.quiz('m', 'Which mutation keeps a tour of cities valid?', ['Bit flip', 'Swap two cities', 'One point crossover', 'Adding a city'], 1,
       'Permutations.', 'Swapping two positions keeps every city exactly once.')
K.quiz('m', 'In the AIMA 8 queens GA, the fitness of a solution is', ['0', '8', '28', '56'], 2,
       'Non attacking pairs.', '8 × 7 ⁄ 2 = 28 pairs, none attacking.')
K.quiz('h', 'Premature convergence means', ['The GA finds the global optimum early', 'The population loses diversity and settles on a local optimum', 'Mutation is too high', 'Crossover is skipped'], 1,
       'Everyone looks the same.', 'Strong selection can make all individuals copies of one good but not best solution.')
K.quiz('h', 'According to the schema theorem, which schemata grow fastest?', ['Long and high order with low fitness', 'Short, low order, above average fitness', 'Any schema with a 0', 'Only the full string'], 1,
       'Building blocks.', 'They are rarely broken by crossover or mutation and are selected more.')
K.quiz('x', 'In the style of a Stanford CS221 question: all individuals have fitness between 1000 and 1001. Why does roulette wheel selection work badly, and what fixes it?', ['It works well, no fix', 'All chances are almost equal, so selection pressure vanishes. Use rank or tournament selection', 'Fitness must be negative', 'Use more crossover'], 1,
       'Look at f ⁄ ∑f.', 'Each gets about 1 ⁄ n of the wheel, so the GA becomes a random search. Rank and tournament depend only on order.')
K.quiz('x', 'In the style of an IISc exam: when is a GA likely to beat random restart hill climbing?', ['When the encoding places related decisions next to each other so crossover combines good blocks', 'When the fitness has one smooth peak', 'When the population is 1', 'Never'], 0,
       'What crossover needs.', 'Without meaningful blocks, crossover is just a large random mutation.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Total fitness of 01101, 11000, 01000, 10011 under f(x) = x².', '1170', '169 + 576 + 64 + 361.',
       ['169 + 576 = 745.', '64 + 361 = 425.', eq('745 + 425 = 1170')], check=1170)
K.calc('e', 'Average fitness of that population.', '292.5', '1170 ⁄ 4.',
       ['Total 1170.', '4 strings.', eq('292.5')], check=292.5)
K.calc('e', 'Fitness of the child 11011.', '729', 'x = 27.',
       ['11011 = 16 + 8 + 2 + 1 = 27.', '27².', eq('729')], check=729)
K.calc('m', 'Selection chance of 11000 (2 decimals).', '0.49', '576 ⁄ 1170.',
       ['576 ⁄ 1170.', '= 0.4923.', eq('≈ 0.49')], check=576 / 1170, tol=0.005)
K.calc('m', 'Expected copies of 10011 (2 decimals).', '1.23', '361 ⁄ 292.5.',
       ['f ⁄ average.', '361 ⁄ 292.5 = 1.234.', eq('≈ 1.23')], check=361 / 292.5, tol=0.005)
K.calc('m', 'Average fitness of the new population 144, 625, 729, 256.', '438.5', 'Sum ⁄ 4.',
       ['144 + 625 = 769. 729 + 256 = 985.', '769 + 985 = 1754.', eq('1754 ⁄ 4 = 438.5')], check=438.5)
K.calc('m', 'AIMA 8 queens: selection chance of the board with fitness 24, out of 24 + 23 + 20 + 11 (percent, whole number).', '31', '24 ⁄ 78.',
       ['Total 78.', '24 ⁄ 78 = 0.3077.', eq('≈ 31 percent')], check=24 / 78 * 100, tol=0.5)
K.calc('h', 'Chance a 5 bit string has no mutation when each bit flips with p = 0.01 (3 decimals).', '0.951', '0.99⁵.',
       ['Each bit survives with 0.99.', '0.99⁵.', eq('≈ 0.951')], check=0.99 ** 5, tol=0.001)
K.calc('h', 'Schema 1**** in the slide population: expected copies next generation using m × f(H) ⁄ f̄ (1 decimal).', '3.2', 'm = 2, f(H) = 468.5.',
       ['f(H) = (576 + 361) ⁄ 2 = 468.5.', '2 × 468.5 ⁄ 292.5.', eq('≈ 3.2')], check=2 * 468.5 / 292.5, tol=0.05)
K.calc('x', 'In the style of a CMU 10-707 problem: tournament selection with k = 2 (pick 2 at random with replacement, keep the fitter). What is the chance the best of n = 4 individuals wins one tournament? Give a decimal.', '0.4375', '1 − (3 ⁄ 4)².',
       ['The best wins if it is picked at least once.', 'P(not picked in 2 draws) = (3 ⁄ 4)² = 0.5625.', eq('1 − 0.5625 = 0.4375')], check=1 - 0.75 ** 2)

# ---------------------------------------------------------------- assignments
K.assign('xover', 'e', 'Crossover and mutation',
         '<p>Write <code>crossover(a, b, cut)</code> that returns [child1, child2]: child1 is a[:cut] + b[cut:] and child2 is b[:cut] + a[cut:]. Also write <code>flip(s, i)</code> that returns s with bit i flipped (0 to 1 or 1 to 0).</p>',
         '''
def crossover(a, b, cut):
    # your code here
    pass

def flip(s, i):
    # your code here
    pass
''', [("crossover('01101', '11000', 4)", ['01100', '11001']), ("crossover('11000', '10011', 2)", ['11011', '10000']),
      ("flip('01101', 0)", '11101'), ("flip('01101', 4)", '01100')],
         '''
def crossover(a, b, cut):
    child1 = a[:cut] + b[cut:]
    child2 = b[:cut] + a[cut:]
    return [child1, child2]

def flip(s, i):
    if s[i] == "0":
        new_bit = "1"
    else:
        new_bit = "0"
    return s[:i] + new_bit + s[i + 1:]
''', 'Use string slices. A string cannot be changed in place, so build a new one.', '<p>These are the two crossovers of the slide example.</p>')
K.assign('table', 'm', 'The fitness table of one generation',
         '<p>Write <code>ga_table(population)</code> for f(x) = x² where each member is a bit string. Return [fitness list, total, chances rounded to 2 decimals, expected copies rounded to 2 decimals].</p>',
         '''
def ga_table(population):
    # your code here
    pass
''', [("ga_table(['01101', '11000', '01000', '10011'])", [[169, 576, 64, 361], 1170, [0.14, 0.49, 0.05, 0.31], [0.58, 1.97, 0.22, 1.23]]),
      ("ga_table(['00001', '00010'])", [[1, 4], 5, [0.2, 0.8], [0.4, 1.6]])],
         '''
def ga_table(population):
    fitness = []
    for s in population:
        x = int(s, 2)
        fitness.append(x * x)
    total = sum(fitness)
    average = total / len(fitness)
    chances = []
    copies = []
    for f in fitness:
        chances.append(round(f / total, 2))
        copies.append(round(f / average, 2))
    return [fitness, total, chances, copies]
''', 'int(s, 2) reads a bit string as a number.', '<p>64 ⁄ 1170 = 0.0547, which rounds to 0.05. The slide shows 0.06, rounding up by hand.</p>')

K.must('GA words', 'Gene, chromosome, population, fitness, selection, crossover, mutation.')
K.must('Roulette wheel', 'P(i) = f<sub>i</sub> ⁄ ∑f. Expected copies f<sub>i</sub> ⁄ f̄.')
K.must('Slide example', 'Fitness 169, 576, 64, 361, total 1170, average 292.5. Children 01100, 11001, 11011 (729), 10000.')
K.must('Other selections', 'Tournament, rank, elitism. Rank and tournament ignore the scale of fitness.')
K.must('When GAs help', 'When good solutions are built from blocks crossover can combine. Watch diversity to avoid premature convergence.')

T = K.topic(
    slug='genetic-algorithms', topic='genetic-algorithms', step=(4, 'Local and evolutionary search', 'cai-local', 'Improve one state or a population step by step when the space is too big to explore: hill climbing, annealing and genetic algorithms.', 'College'),
    title='Genetic algorithms', short='Genetic algorithms', badge='4.2', minutes=45,
    lead='Search with a whole population that evolves: fitter solutions get more children, children mix their parents, and small mutations keep variety. Follow the slide example that maximises x² one generation at a time.',
    desc='Genes, chromosomes and fitness, the GA loop, the x² worked example with its tables, roulette wheel, tournament, rank and elitism, crossover and mutation types, 8 queens, the schema theorem and the slide comparison of hill climbing, annealing and GAs.',
    summary='Population, fitness, selection, crossover and mutation, the slide x² example, and when a GA beats other local search.',
    keywords=['genetic algorithm', 'crossover', 'mutation', 'roulette wheel', 'tournament selection', 'schema theorem', 'evolutionary search'],
    recap='<p>Select by fitness, cross over, mutate, repeat. The slide example lifts the best fitness from 576 to 729 in one generation.</p>',
    nb={'gen1': 'One generation of the slide x² example', 'roulette': 'Roulette wheel selection'})
