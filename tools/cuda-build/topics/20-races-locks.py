# Chapter 7.1: Race conditions and locks. Source: lecture 10 (slides 2 to 12: counter++ as three steps, the three
# requirements, Dekker's three attempts, Peterson), lecture 11 (slides 2 to 4: Bakery and Filter), workbook 10.1.
# Corrections from the notes: slide 8 calls attempt 2 a deadlock (it breaks mutual exclusion), the class said the three
# attempts fail the same way (they fail three different ways), and the class said Peterson does not solve the problem
# (it does, under in order memory). Beyond the lecture: the real Dekker algorithm and why volatile needs a fence.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, nb

K = Kit()

COUNTER = r'''
#include <cstdio>

__global__ void unsafe_inc(int *c) {
    *c = *c + 1;                       // load, add, store: three separate steps
}

__global__ void safe_inc(int *c) {
    atomicAdd(c, 1);                   // one indivisible read, add and write
}

int main() {
    int *d, h;
    cudaMalloc(&d, sizeof(int));
    cudaMemset(d, 0, sizeof(int));
    unsafe_inc<<<1, 10>>>(d);
    cudaMemcpy(&h, d, sizeof(int), cudaMemcpyDeviceToHost);
    printf("unsafe: %d\n", h);
    cudaMemset(d, 0, sizeof(int));
    safe_inc<<<1, 10>>>(d);
    cudaMemcpy(&h, d, sizeof(int), cudaMemcpyDeviceToHost);
    printf("atomic: %d\n", h);
    cudaFree(d);
    return 0;
}
'''

DEKKER = r'''
volatile bool flag[2] = {false, false};
volatile int turn = 0;

void dekker_enter(int me) {            // me is 0 or 1
    int other = 1 - me;
    flag[me] = true;                   // I want in
    while (flag[other]) {              // the other wants in too
        if (turn != me) {              // and it is not my turn
            flag[me] = false;          // step back
            while (turn != me) ;       // wait for my turn
            flag[me] = true;           // try again
        }
    }
}

void dekker_leave(int me) {
    turn = 1 - me;                     // give the turn away
    flag[me] = false;
}
'''

PETERSON = r'''
__device__ volatile int flag[2] = {0, 0};
__device__ volatile int turn = 0;

__device__ void peterson_enter(int me) {
    int other = 1 - me;
    flag[me] = 1;                          // 1. I want in
    turn = other;                          // 2. but you go first
    __threadfence();                       // both writes visible before the reads below
    while (flag[other] && turn == other) ; // 3. wait only if the other wants in and it is its turn
}

__device__ void peterson_leave(int me) {
    __threadfence();                       // writes made inside the critical section go first
    flag[me] = 0;                          // 4. done
}
'''

NLOCKS = r'''
#define N 4
volatile bool choosing[N];
volatile int number[N];

void bakery_enter(int i) {
    choosing[i] = true;
    int m = 0;
    for (int j = 0; j < N; j++) if (number[j] > m) m = number[j];
    number[i] = m + 1;                 // a ticket one larger than any in use
    choosing[i] = false;
    for (int j = 0; j < N; j++) {
        while (choosing[j]) ;          // j is still picking its ticket
        while (number[j] != 0 &&
               (number[j] < number[i] || (number[j] == number[i] && j < i))) ;
    }
}

void bakery_leave(int i) { number[i] = 0; }

volatile int level[N];
volatile int victim[N];

static bool someone_at(int i, int k) {
    for (int j = 0; j < N; j++)
        if (j != i && level[j] >= k) return true;
    return false;
}

void filter_enter(int i) {
    for (int k = 1; k < N; k++) {      // N - 1 gates
        level[i] = k;                  // I am at gate k
        victim[k] = i;                 // I arrived last at this gate
        while (someone_at(i, k) && victim[k] == i) ;
    }
}

void filter_leave(int i) { level[i] = 0; }
'''

K.code('orders', r'''
# How many ways can the steps of several threads interleave?
from math import factorial
def orders(steps):
    total = factorial(sum(steps))
    for s in steps:
        total //= factorial(s)
    return total
print("2 threads x 3 steps:", orders([3, 3]))
print("3 threads x 3 steps:", orders([3, 3, 3]))
print("3 steps and 4 steps:", orders([3, 4]))
correct = factorial(3)      # only the 3! fully serial orders give 3
print("chance of 3 with 3 threads:", round(100 * correct / orders([3, 3, 3]), 2), "%")
''')

K.code('lockstep', r'''
# Workbook 10.1: 10 threads of one warp run counter = counter + 1 in lock step
n = 10
counter = 0
regs = [counter for _ in range(n)]   # step 1: every thread loads 0
regs = [r + 1 for r in regs]         # step 2: every thread adds 1
for r in regs:                       # step 3: every thread stores 1
    counter = r
print("result:", counter, " lost updates:", n - counter)
''')

K.lesson('race', 'Why counter = counter + 1 goes wrong', f'''
<p>To you it is one line. To the hardware it is three steps: <b>load</b> the value into a register, <b>add</b> 1 to the register, <b>store</b> the register back. When two threads do this at the same time, their steps can mix.</p>
{table(['Time', 'Thread 1', 'Thread 2', 'counter in memory'], [
    ['1', 'load, r1 = 0', '', '0'],
    ['2', '', 'load, r2 = 0', '0'],
    ['3', 'r1 = 1', '', '0'],
    ['4', '', 'r2 = 1', '0'],
    ['5', 'store 1', '', '1'],
    ['6', '', 'store 1', '1, but it should be 2']])}
<p>A <b>race condition</b> is when the result depends on the timing of threads that share data and at least one of them writes. Step through it yourself. Change the number of threads and the order, and see how many updates are lost.</p>
{viz('counter')}
{fxs(
    fx('Orders of n threads with s steps each', '(n × s)! ÷ (s!)<sup>n</sup>', 'Pick which thread takes each time slot. Steps inside one thread keep their order.', key=True),
    fx('Two threads, three steps', '6! ÷ (3! × 3!) = 20', 'Only the 2 fully serial orders give 2. That is 10 percent.'),
    fx('Three threads, three steps', '9! ÷ (3!)<sup>3</sup> = 1680', 'Only 3! = 6 serial orders give 3. That is about 0.4 percent.', key=True))}
{code('orders')}
<p>Inside a GPU warp the threads run in lock step: all load, then all add, then all store. Every thread loads the same old value, so the result is just 1.</p>
{code('lockstep')}
{cu('counter.cu', COUNTER, {3: 'Every thread reads the same counter, adds 1 and writes back. Updates are lost.', 4: 'This single line becomes a load, an add and a store.', 8: 'atomicAdd does the read, the add and the write as one step that nobody can split.', 15: 'One warp of 10 threads. In lock step they all read 0.', 19: 'Same launch with the atomic version.'}, out='unsafe: 1\natomic: 10')}
{note('The unsafe result is not guaranteed to be 1. It depends on how the hardware schedules the threads. A race means the answer is unpredictable, which is worse than always wrong.', 'warn')}
''', kw=['race condition', 'counter++', 'load add store', 'interleaving', '1680 orders', 'lost update', 'atomicAdd'])

K.lesson('rules', 'The critical section and Dekker\'s three attempts', f'''
<p>A <b>critical section</b> is the piece of code that touches the shared data. Only one thread may run it at a time. Any correct solution must meet three rules.</p>
{table(['Rule', 'Meaning', 'If it breaks'], [
    ['Mutual exclusion', 'At most one thread is inside at any moment.', 'Two threads change the data together.'],
    ['Progress', 'If the section is free and someone wants in, someone gets in. A thread that does not want in cannot block others.', 'Deadlock, or waiting for a thread that has gone home.'],
    ['Bounded waiting', 'After I ask, others can go first only a limited number of times.', 'Starvation: I wait for ever.']])}
<p>Think of one bathroom at a roadside restaurant. Never two people inside. If it is empty and someone waits, they go in. Nobody waits for ever while others keep jumping the queue.</p>
<p>Lecture 10 tries three simple ideas for two threads. Each uses busy waiting: a while loop that spins until it may go on. Pick an attempt below and choose a schedule of 0s and 1s (which thread takes the next step).</p>
{viz('locks')}
{table(['Attempt', 'Idea', 'Mutual exclusion', 'Progress', 'What goes wrong'], [
    ['1. Take turns', 'a shared turn variable', 'yes', 'no', 'Strict alternation. If thread 2 stops wanting in, thread 1 enters once and then waits for ever.'],
    ['2. Check, then set', 'look at the other flag, then raise mine', 'no', 'yes', 'Both check before either sets. Both enter.'],
    ['3. Set, then check', 'raise my flag, then look', 'yes', 'no', 'Both raise flags, then each waits for the other. Deadlock.']])}
{note('Slide 8 says attempt 2 can deadlock. It cannot: a thread sets its flag only after passing its loop, so nobody waits after the flags are set. The real flaw is that both can pass the check, which breaks mutual exclusion. The class also concluded that the three attempts suffer from the same drawback. They fail in three different ways: attempt 2 checks too early, attempt 3 claims too early, attempt 1 is safe but too rigid.', 'exam')}
<p>The fix combines the flags of attempt 3 (safety) with the turn variable of attempt 1 (a tie breaker). Dekker found the first correct version in the 1960s.</p>
{cu('dekker.cu', DEKKER, {6: 'Raise my flag first, as in attempt 3.', 7: 'Someone else also wants in, so there is a tie to break.', 8: 'The turn variable breaks the tie, as in attempt 1.', 9: 'Lower my flag so the other thread can go in. This removes the deadlock of attempt 3.', 10: 'Spin until the turn comes back to me.', 17: 'On the way out, hand the turn to the other thread.'})}
''', kw=['critical section', 'mutual exclusion', 'progress', 'bounded waiting', 'deadlock', 'starvation', 'Dekker', 'busy waiting'])

K.lesson('peterson', 'Peterson\'s algorithm and why it is correct', f'''
<p>Peterson (1981) found a shorter correct lock for two threads. Each thread says "I want in" and then "but you go first". Whoever said "you go first" last is the one who waits.</p>
{cu('peterson.cu', PETERSON, {6: 'Step 1: raise my flag.', 7: 'Step 2: give the turn to the other thread. Both threads write turn, and the last writer waits.', 8: 'A fence stops the hardware from letting the read below go ahead of the two writes above.', 9: 'Step 3: wait only while the other wants in and it is the other thread\'s turn.', 13: 'Everything written in the critical section must be visible before I lower my flag.', 14: 'Step 4: lower my flag on the way out.'})}
{steps('Proof of mutual exclusion', [
    'Suppose both threads are inside. Each wrote its flag, then turn.',
    'Say P0 wrote turn last, so turn = 1 from then on.',
    'P1 set flag[1] before it wrote turn, which was before P0 wrote turn. So when P0 tested, flag[1] was true and turn was 1.',
    'Then P0 would still be waiting. Contradiction. The other case is the same with 0 and 1 swapped.',
    eq('At most one thread inside')])}
<p><b>Progress.</b> If P1 does not want in, flag[1] is false and P0 walks straight in. If both want in, turn is 0 or 1, so exactly one of the two loop conditions is false. Somebody always gets in.</p>
<p><b>Bounded waiting.</b> If P1 leaves and tries again at once, it first writes turn = 0, which makes itself wait and lets P0 go. So P0 waits for at most one turn of P1.</p>
{note('In class the conclusion was that the deadlock danger is still looming. That is not correct. With reads and writes that happen in program order, Peterson meets all three rules. Swapping steps 1 and 2 (turn first, then flag) does break mutual exclusion, so the order matters.', 'exam')}
{deep('Why volatile is not enough on real hardware', '<p>volatile only stops the compiler from keeping the variable in a register. Modern CPUs and GPUs may still reorder memory operations. A store can sit in a store buffer while a later load runs ahead. Then each thread reads the other flag as false before its own flag is visible, and both enter. You need a fence between the writes and the read: __threadfence() in CUDA, or std::atomic with sequential consistency in C++. In practice programmers use hardware atomic instructions, which is the next chapter.</p>')}
''', kw=['Peterson', 'turn', 'flag', 'proof', 'volatile', '__threadfence', 'memory reordering', 'store buffer'])

K.lesson('nlocks', 'Locks for N threads: Bakery and Filter', f'''
<p>Peterson works for two threads. Lecture 11 shows two ways to handle N threads.</p>
<p><b>Lamport\'s Bakery lock.</b> Like the ticket machine at a bakery counter: take a ticket one larger than any ticket in use and wait until every smaller ticket has been served. Two threads can pick the same number at the same moment, so equal tickets are broken by thread id.</p>
<p><b>Filter lock.</b> N − 1 gates in a row. At each gate the thread that arrived last (the victim) waits while anyone else is at that gate or further. Each gate holds back at least one thread, so after N − 1 gates only one remains.</p>
{cu('locks_n.cu', NLOCKS, {6: 'choosing[i] says that thread i is in the middle of picking a ticket.', 9: 'Take a ticket one larger than every ticket in use.', 12: 'Do not compare with j while j is still picking. Its ticket might end up smaller than mine.', 13: 'Wait while j holds a smaller ticket, or the same ticket with a smaller id.', 18: 'Leaving: throw the ticket away.', 31: 'I am now trying to pass gate k.', 32: 'I arrived last at gate k, so I am the one who waits if needed.', 33: 'Wait while someone else is at gate k or beyond and I am still the victim.'})}
{steps('Filter: at most N − k threads get past gate k', [
    'Gate 0: at most N threads, which is true.',
    'Assume at most N − k + 1 threads reach gate k − 1. Suppose all of them pass gate k.',
    'Let A be the last of them to write victim[k]. Every other one has level ≥ k, so A must wait. Contradiction.',
    'So at most N − k pass gate k. At the last gate k = N − 1 that is 1 thread.',
    eq('Mutual exclusion for N threads')])}
{table(['Lock', 'Threads', 'Fairness', 'Cost per entry'], [
    ['Peterson', '2', 'waits at most one turn', 'constant'],
    ['Bakery', 'N', 'first come, first served', 'O(N), tickets grow without limit'],
    ['Filter', 'N', 'starvation free, but no fixed bound', 'O(N²) checks in the worst case']])}
{note('Slide 3 says the Filter lock has bounded waiting. It is starvation free (every waiting thread gets in in the end), but a thread can be overtaken any number of times at a gate, so there is no fixed bound r. The Bakery lock is the one with first come, first served order.', 'exam')}
{nb('08-warps-races-atomics.ipynb', 'Notebook: a race you can see', 'A plain counter loses updates on a GPU, an atomic counter does not.')}
''', kw=['Bakery', 'Lamport', 'ticket', 'Filter lock', 'victim', 'starvation free', 'r-bounded', 'N threads'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Two people write the score on one whiteboard. Each reads 5, adds 1 and writes 6. One point is lost. They need a rule so that only one person holds the marker at a time.</p>',
    '<p>counter++ is load, add, store. A critical section needs mutual exclusion, progress and bounded waiting. Dekker attempt 1 fails progress, 2 fails mutual exclusion, 3 deadlocks. Peterson and Bakery meet all three.</p>',
    '<p>Prove locks by looking at who wrote a shared variable last. Check small cases by trying every interleaving, as the notes did (62 states for Peterson). On real hardware add fences or use atomics.</p>',
    '<p>Model checkers such as TLA+ and SPIN explore every state of a lock. Weak memory models (C++, PTX) need careful proofs. Real systems use hardware compare and swap, ticket locks and queue locks such as MCS.</p>')}
''', kw=['ladder', 'model checking', 'memory model', 'MCS lock', 'ticket lock'])

K.quiz('e', 'counter = counter + 1 is how many hardware steps?', ['1', '2', '3', '4'], 2, 'Load, add, store.', 'Three steps that other threads can come between.')
K.quiz('e', 'A race condition needs', ['Only reads', 'Shared data with at least one writer and timing that matters', 'One thread', 'A GPU'], 1, 'At least one write.', 'Readers alone never race.')
K.quiz('e', 'Mutual exclusion means', ['Everyone enters together', 'At most one thread in the critical section', 'Threads take turns strictly', 'No thread waits'], 1, 'One at a time.', 'Never two inside.')
K.quiz('e', 'Two threads, three steps each. Number of orders', ['6', '9', '20', '36'], 2, '6! ÷ (3! × 3!).', '20.')
K.quiz('m', 'Dekker attempt 1 (shared turn) breaks which rule?', ['Mutual exclusion', 'Progress', 'Nothing', 'Atomicity'], 1, 'Strict alternation.', 'If one thread leaves, the other waits for ever.')
K.quiz('m', 'Dekker attempt 2 (check, then set) really breaks', ['Progress by deadlock', 'Mutual exclusion', 'Bounded waiting only', 'Nothing'], 1, 'Both check before either sets.', 'Slide 8 calls it deadlock, but both threads enter.')
K.quiz('m', 'Dekker attempt 3 (set, then check) fails by', ['Both entering', 'Deadlock', 'Lost updates', 'Starvation of one thread only'], 1, 'Both flags up.', 'Each waits for the other for ever.')
K.quiz('m', 'In Peterson, which thread waits when both want in?', ['Thread 0 always', 'The one that wrote turn last', 'The one that wrote turn first', 'Neither'], 1, 'turn = other.', 'The last writer gave the turn away last.')
K.quiz('h', 'Swap Peterson steps 1 and 2 (write turn, then flag). Result', ['Still correct', 'Mutual exclusion can break', 'Always deadlocks', 'Becomes faster only'], 1, 'Try P1 entirely between P0\'s two writes.', 'Both can enter.')
K.quiz('h', 'What does volatile guarantee?', ['Hardware will not reorder', 'The compiler reads and writes memory each time', 'Atomic updates', 'Mutual exclusion'], 1, 'Compiler only.', 'Hardware reordering needs a fence.')
K.quiz('x', 'The Filter lock is', ['Not mutually exclusive', 'Starvation free but has no fixed waiting bound', 'First come, first served', 'Deadlock prone'], 1, 'Can be overtaken many times.', 'Slide 3 overstates it.')
K.quiz('x', 'Bakery: threads 2 and 4 both hold ticket 7, nobody holds a smaller one. Who enters first?', ['Thread 4', 'Thread 2', 'Both', 'Neither, deadlock'], 1, 'Tie broken by id.', 'Smaller id first.')

K.calc('e', 'Orders for two threads with 3 steps each?', '20', '6! ÷ (3!)².',
       ['720 ÷ 36.', '= 20.', eq('20 orders')], check=20)
K.calc('e', 'Orders for three threads with 3 steps each?', '1680', '9! ÷ (3!)³.',
       ['362,880 ÷ 216.', '= 1680.', eq('1680 orders')], check=1680)
K.calc('e', 'Orders for one thread with 3 steps and one with 4?', '35', '7! ÷ (3! × 4!).',
       ['5040 ÷ 144.', '= 35.', eq('35 orders')], check=35)
K.calc('m', 'All 20 orders equally likely. Chance of the right answer in percent?', '10', '2 good orders.',
       ['Only the two serial orders give 2.', '2 ÷ 20.', eq('10 percent')], check=10)
K.calc('m', '10 threads of one warp in lock step. Updates lost?', '9', 'All load 0.',
       ['Every thread stores 1.', 'Result 1 instead of 10.', eq('9 lost')], check=9)
K.calc('m', 'Three threads. Chance of the correct 3, in percent? (two decimals)', '0.36', '3! ÷ 1680.',
       ['Only the 6 serial orders give 3.', '6 ÷ 1680 = 0.00357.', eq('≈ 0.36 percent')], check=round(600 / 1680, 2), tol=0.005)
K.calc('m', 'Orders for four threads with 3 steps each?', '369600', '12! ÷ (3!)⁴.',
       ['479,001,600 ÷ 1296.', '= 369,600.', eq('369,600 orders')], check=369600)
K.calc('h', 'Four threads. How many of those orders give the correct 4?', '24', 'Serial orders only.',
       ['Each thread must finish before the next loads.', 'Number of ways to order 4 threads: 4!.', eq('24 orders')], check=24)
K.calc('h', 'Filter lock with N = 6. How many gates?', '5', 'N − 1.',
       ['One thread is held back at each gate.', '6 − 1.', eq('5 gates')], check=5)
K.calc('x', 'Filter lock, N = 6. At most how many threads can be past gate 4?', '2', 'N − k.',
       ['The induction gives at most N − k past gate k.', '6 − 4.', eq('2 threads')], check=2)
K.calc('x', 'Two threads with 5 steps each. Number of orders?', '252', 'C(10, 5).',
       ['10! ÷ (5! × 5!).', '3,628,800 ÷ 14,400.', eq('252 orders')], check=252)

K.assign('orders', 'e', 'Count the interleavings',
         '<p>Write <code>orders(steps)</code>. <code>steps</code> is a list with the number of steps of each thread. Return how many different orders the steps can run in, if each thread keeps its own steps in order.</p>',
         '''
def orders(steps):
    # your code here
    pass
''', [("orders([3, 3])", 20), ("orders([3, 3, 3])", 1680), ("orders([3, 4])", 35), ("orders([1, 1, 1, 1])", 24)],
         '''
from math import factorial

def orders(steps):
    total = factorial(sum(steps))
    for s in steps:
        total //= factorial(s)
    return total
''', 'Total steps factorial, divided by the factorial of each thread\'s steps.', '<p>This is the multinomial coefficient.</p>')
K.assign('replay', 'm', 'Replay a schedule of counter++',
         '<p>Write <code>run_counter(n, order)</code>. There are n threads, each doing load, add, store on one counter that starts at 0. <code>order</code> lists which thread takes its next step. Return the final counter.</p>',
         '''
def run_counter(n, order):
    # your code here
    pass
''', [("run_counter(2, [0, 1, 0, 1, 0, 1])", 1), ("run_counter(2, [0, 0, 0, 1, 1, 1])", 2), ("run_counter(10, list(range(10)) * 3)", 1), ("run_counter(3, [0, 0, 1, 0, 1, 1, 2, 2, 2])", 2)],
         '''
def run_counter(n, order):
    counter = 0
    reg = [0] * n
    step = [0] * n
    for t in order:
        if step[t] == 0:
            reg[t] = counter
        elif step[t] == 1:
            reg[t] += 1
        else:
            counter = reg[t]
        step[t] += 1
    return counter
''', 'Keep one register and one step number per thread.', '<p>The lock step case loses 9 of 10 updates.</p>')

K.must('Three steps', 'counter++ is load, add, store. Other threads can come between them.')
K.must('Counting orders', '(n × s)! ÷ (s!)ⁿ. Two threads: 20, three threads: 1680. Only the serial orders are correct.')
K.must('Three rules', 'Mutual exclusion, progress, bounded waiting. Breaking them gives two inside, deadlock, starvation.')
K.must('Dekker attempts', '1 fails progress (strict turns), 2 fails mutual exclusion (not deadlock), 3 deadlocks.')
K.must('Peterson', 'flag[me] = 1, turn = other, wait while flag[other] and turn == other. Correct, with fences on real hardware.')
K.must('N threads', 'Bakery: tickets plus id, first come first served. Filter: N − 1 gates, starvation free but not bounded.')

T = K.topic(
    slug='races-locks', topic='races-locks', step=(7, 'Synchronisation', 'gpu-sync', 'Learn why shared updates go wrong, how classic locks fix it, and how GPUs use barriers and atomic instructions.', 'College'),
    title='Race conditions and locks', short='Races and locks', badge='7.1', minutes=45,
    lead='See why one line of code can lose updates, learn the three rules any lock must follow, and step through Dekker, Peterson, Bakery and Filter locks.',
    desc='counter++ as load, add and store, counting interleavings, the critical section rules, Dekker\'s three attempts with the slide 8 correction, the real Dekker algorithm, Peterson with a proof, volatile against fences, and the Bakery and Filter locks for N threads.',
    summary='Races, the three lock rules, Dekker, Peterson, Bakery and Filter.',
    keywords=['race condition', 'critical section', 'Dekker', 'Peterson', 'Bakery', 'Filter lock'],
    recap='<p>A race loses updates because one line is three steps. A correct lock needs mutual exclusion, progress and bounded waiting. Peterson and Bakery meet all three in theory, and real hardware also needs fences.</p>')
