# Chapter 7.2: Barriers, atomics and GPU locks. Source: lecture 10 (slides 13 to 18: __syncthreads, atomicCAS lock,
# barrier against lock), lecture 11 (slides 5 to 10: priority locks, block priority, cooperative groups, who shares a
# variable decides the synchronisation), lecture 12 (slides 9 and 10: unsafe_inc and the shared atomic fix), workbook
# P10.1.6 and P10.2.5. Corrections from the notes: the slide's critical_kernel can hang before Volta and needs fences,
# and the priority counter skips levels. Beyond the lecture: ticket lock from atomics (class Q40), memory fence scopes.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

LOCK = r'''
__device__ int lock = 0;                       // 0 = free, 1 = taken
__device__ volatile int total = 0;

__device__ void acquire(int *l) {
    while (atomicCAS(l, 0, 1) != 0) ;          // try to change 0 into 1
}

__device__ void release(int *l) {
    __threadfence();                           // writes in the critical section go first
    atomicExch(l, 0);                          // free the lock
}

__global__ void add_block_sums(const int *part) {
    if (threadIdx.x == 0) {                    // only one thread per block takes the lock
        acquire(&lock);
        total = total + part[blockIdx.x];      // the critical section
        release(&lock);
    }
    __syncthreads();                           // the rest of the block waits here
}
'''

TICKET = r'''
__device__ unsigned int next_ticket = 0;
__device__ unsigned int now_serving = 0;

__device__ void ticket_acquire() {
    unsigned int my = atomicAdd(&next_ticket, 1);     // take a ticket
    while (atomicAdd(&now_serving, 0) != my) ;        // an atomic read, until my number is called
    __threadfence();
}

__device__ void ticket_release() {
    __threadfence();
    atomicAdd(&now_serving, 1);                       // call the next ticket
}
'''

PRIVAT = r'''
__global__ void count_ones(const int *x, int n, int *count) {
    __shared__ int local;
    if (threadIdx.x == 0) local = 0;
    __syncthreads();
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n && x[i] == 1) atomicAdd(&local, 1);    // fast atomic inside the block
    __syncthreads();
    if (threadIdx.x == 0) atomicAdd(count, local);   // one global atomic per block
}
'''

GRID = r'''
#include <cooperative_groups.h>
namespace cg = cooperative_groups;

__global__ void two_phase(float *a, float *b, int n) {
    cg::grid_group grid = cg::this_grid();       // every thread of the launch
    int i = grid.thread_rank();
    if (i < n) a[i] = a[i] * 2.0f;               // phase 1
    grid.sync();                                 // every block has finished phase 1
    if (i < n) b[i] = a[(i + 1) % n];            // phase 2 reads results of other blocks
}

void launch(float *a, float *b, int n, int blocks, int threads) {
    void *args[] = {&a, &b, &n};
    cudaLaunchCooperativeKernel((void *)two_phase, blocks, threads, args);
}
'''

K.code('atomics', r'''
# Workbook P10.1.6: 10 blocks of 256 threads, each adds 1 to one counter
blocks, tpb = 10, 256
per_thread = blocks * tpb          # one global atomicAdd per thread
privatised = blocks                # shared atomics inside, then one global per block
print("global atomics, per thread :", per_thread)
print("global atomics, privatised :", privatised)
print("shared atomics, privatised :", blocks * tpb)
print("fewer global atomics by    :", per_thread // privatised, "times")
''')

K.code('prio', r'''
# Lecture 11 priority counter: every thread adds 1 on the way out
pri = [0, 1, 2, 2, 2, 3, 4]
done = [False] * len(pri)
now = 0
while True:
    group = [t for t, p in enumerate(pri) if not done[t] and p == now]
    if not group:
        break
    for t in group:
        done[t] = True
    print("level", now, "threads", group, "run together")
    now += len(group)              # each thread calls atomicAdd(&now, 1)
print("counter ends at", now)
print("waiting for ever:", [t for t in range(len(pri)) if not done[t]])
''')

K.lesson('barrier', 'Barrier or lock', f'''
<p>There are two very different ways to make threads wait for each other.</p>
<p>A <b>barrier</b> such as <code>__syncthreads()</code> is a meeting point. Nobody in the block goes past it until everyone in the block has arrived. It is like a traffic light that stays red until the whole group is at the line.</p>
<p>A <b>lock</b> lets only one thread at a time into a critical section. The others wait outside, like a queue for a single restroom. Threads that do not need the section are not held up.</p>
{viz('syncbar')}
{table(['', '__syncthreads()', 'Lock from atomicCAS'], [
    ['Purpose', 'everyone reaches a point', 'one at a time'],
    ['Who waits', 'all threads of the block', 'only threads that want the lock'],
    ['Scope', 'one block', 'the whole device (global memory), or shared memory'],
    ['Typical use', 'tiled matmul, reductions, stencils', 'global counters, shared queues, rare updates']])}
<p>The lecture ends with a simple rule: <b>who shares a variable decides which tool you need.</b></p>
{table(['Who shares the data', 'Where it lives', 'How to synchronise'], [
    ['one thread', 'registers, local memory', 'nothing'],
    ['threads of one block', 'shared memory', '__syncthreads(), or shared atomics'],
    ['threads of different blocks', 'global memory', 'atomics, locks, or end the kernel and start another']])}
{note('Every thread of the block must reach every __syncthreads(). A barrier inside an if that only some threads enter is undefined behaviour: the kernel may hang, or seem to work and give wrong results. The reduction chapter shows the lecture 12 example.', 'warn')}
''', kw=['barrier', '__syncthreads', 'lock', 'critical section', 'scope', 'who shares'])

K.lesson('atomics', 'Atomic instructions and the atomicCAS lock', f'''
<p>An <b>atomic</b> operation reads, changes and writes a memory word as one step. No other thread can see or change the word in the middle. The hardware does this, so it is correct even with thousands of threads.</p>
{table(['Function', 'What it does as one step', 'Returns'], [
    ['atomicAdd(p, v)', '*p = *p + v', 'the old value'],
    ['atomicSub, atomicMin, atomicMax', 'subtract, keep the smaller, keep the larger', 'the old value'],
    ['atomicExch(p, v)', '*p = v', 'the old value'],
    ['atomicAnd, atomicOr, atomicXor', 'bit operations', 'the old value'],
    ['atomicCAS(p, cmp, v)', 'if *p == cmp then *p = v', 'the old value']])}
{fxs(
    fx('Compare and swap', 'old = *p,  if old = cmp then *p = v,  return old', 'If old = cmp, you won. Any other value means somebody else changed it first.', key=True))}
<p>All threads try to change the lock from 0 to 1. Exactly one gets back 0 and goes in. Everyone else gets back 1 and tries again.</p>
{cu('lock.cu', LOCK, {2: 'volatile so the compiler reads total from memory each time and does not reuse a stale copy.', 5: 'Spin until this thread is the one that changed 0 into 1.', 9: 'Make the writes of the critical section visible before anyone else can get the lock.', 10: 'atomicExch writes 0 as one step and frees the lock.', 14: 'Only thread 0 of each block competes. 32 lanes of one warp spinning on the same lock could hang older GPUs.', 16: 'Inside the lock one thread reads and writes total safely.', 19: 'The other threads of the block wait here for thread 0.'})}
{note('The slide\'s critical_kernel lets every thread call acquire_lock. Before Volta (2017) the 32 lanes of a warp move in lock step. One lane wins the lock, but the warp keeps running the spin loop for the losers and never lets the winner reach release_lock, so the kernel hangs. Newer GPUs avoid the hang, but the lock then makes every thread of the grid wait in a single line, which is very slow. Take the lock with one thread per block, and add a fence before the release.', 'exam')}
<p>A plain CAS spin lock has no queue, so a thread can lose again and again. A <b>ticket lock</b> fixes this with two counters. It is the Bakery idea built from atomics.</p>
{cu('ticket.cu', TICKET, {5: 'atomicAdd returns the old value, so every thread gets a different ticket.', 6: 'Adding 0 is a way to read the counter atomically.', 7: 'The fence keeps reads in the critical section from running before the lock is held.', 12: 'Moving the counter on lets the next ticket in, in arrival order.'})}
{deep('Memory fences and their scope', '<p>A fence makes this thread\'s earlier writes visible before its later ones. __threadfence_block() covers the threads of the same block, __threadfence() the whole GPU, and __threadfence_system() the GPU and the CPU (for mapped host memory). A fence does not make anyone wait. It only fixes the order in which other threads can see the writes.</p>')}
''', kw=['atomic', 'atomicAdd', 'atomicCAS', 'atomicExch', 'spin lock', 'intra-warp deadlock', 'Volta', '__threadfence', 'ticket lock'])

K.lesson('privat', 'Fewer atomics: privatisation', f'''
<p>Atomics are always correct, but atomics on the <b>same address</b> are done one after another. Thousands of threads adding to one global counter form a long queue.</p>
<p>Lecture 12 shows the problem. In <code>unsafe_inc</code> every thread reads a shared variable, adds 1 and writes it back, so 10 threads in one warp give 1. The fix uses <code>atomicAdd</code> on the shared variable. With many blocks the best plan is <b>privatisation</b>: each block counts in its own shared memory first, then one thread adds the block total to global memory.</p>
{viz('privat')}
{code('atomics')}
{cu('count_ones.cu', PRIVAT, {2: 'One private counter per block, in fast shared memory.', 3: 'Start the block counter at 0, not at the global value. Otherwise blocks would count each other\'s work.', 4: 'Everyone must see the 0 before adding.', 6: 'Shared memory atomic: no lost updates and much cheaper than a global one.', 7: 'Wait until all threads of the block have added.', 8: 'One global atomic per block instead of one per thread.'})}
{steps('Workbook P10.2.5: 2²⁰ values, blocks of 1024, one atomic per block', [
    'Blocks = 1,048,576 ÷ 1024 = 1024.',
    'Each block reduces its values in shared memory and does one global atomicAdd.',
    'One atomic per element would be 1,048,576.',
    eq('1024 global atomics instead of 1,048,576')])}
{note('compute-sanitizer --tool racecheck finds races on shared memory, such as the unsafe_inc example. Run it whenever a result changes from run to run.', 'tip')}
''', kw=['privatisation', 'contention', 'shared atomic', 'global atomic', 'unsafe_inc', 'racecheck', 'histogram'])

K.lesson('priority', 'Priority locks and grid wide barriers', f'''
<p>Lecture 11 builds a priority lock from one "now serving" counter, like the token display at a clinic. A thread waits until the counter equals its priority, works, and then adds 1.</p>
{viz('prio')}
{code('prio')}
{table(['Problem', 'Why', 'Fix'], [
    ['Not mutual exclusion', 'All threads with the same priority pass together.', 'Add a real lock inside each level.'],
    ['Levels get skipped', 'Three threads at level 2 each add 1, so the counter goes from 2 to 5.', 'Move the counter on once per level, when the last thread of that level is done.'],
    ['Deadlock by residency', 'If the priority 0 blocks are not running yet because spinning blocks fill the GPU, nobody moves the counter.', 'Do not spin on other blocks. Use a grid barrier or separate kernels.'],
    ['Starvation', 'A steady stream of high priority work keeps low priority work waiting.', 'Ageing: raise the priority of work that has waited long.']])}
{note('In the block priority code of slide 7, the counter must be read as volatile or atomically, or the compiler may move the read out of the loop and spin for ever. CUDA does not promise which blocks are running or in what order they start. That this code usually works is luck.', 'exam')}
<p><b>Cooperative groups</b> name a group of threads (a warp tile, a block, a cluster or the whole grid) and synchronise exactly that group. <code>grid.sync()</code> is a barrier for every thread of the launch, which <code>__syncthreads()</code> cannot do.</p>
{cu('grid_sync.cu', GRID, {5: 'A handle to every thread of the launch.', 6: 'The thread\'s number across the whole grid.', 8: 'A barrier for the whole grid. Every block must be running at the same time for this to work.', 9: 'Now it is safe to read values that other blocks wrote in phase 1.', 14: 'A cooperative launch checks that all blocks fit on the GPU at once and fails otherwise.'})}
{fxs(
    fx('Largest cooperative grid', 'blocks ≤ (blocks per SM) × (number of SMs)', 'The occupancy chapter gives blocks per SM. T4: 40 SMs, 4 blocks of 256 per SM, so at most 160 blocks.', key=True))}
''', kw=['priority lock', 'now serving', 'level skipping', 'residency deadlock', 'cooperative groups', 'grid.sync', 'cudaLaunchCooperativeKernel', 'ageing'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A class trip waits at the bus until every child is back. That is a barrier. The single key to the store room, passed from hand to hand, is a lock.</p>',
    '<p>__syncthreads() for one block, atomics for different blocks. atomicCAS returns the old value. Take locks with one thread per block, fence before release, and prefer atomicAdd or privatisation to locks.</p>',
    '<p>Measure contention: global atomics on one address are serialised. Replace with warp shuffles plus one atomic per warp or block. grid.sync() needs a cooperative launch with all blocks resident.</p>',
    '<p>The PTX memory model gives acquire, release and scope to every atomic (cuda::atomic_ref in libcu++). Lock free queues, work stealing and split arrive and wait barriers (cuda::barrier, mbarrier on Hopper) build on these ideas.</p>')}
''', kw=['ladder', 'contention', 'warp shuffle', 'memory model', 'cuda::atomic_ref', 'cuda::barrier'])

K.quiz('e', '__syncthreads() waits for', ['All threads of the grid', 'All threads of the block', 'One warp', 'The CPU'], 1, 'Block scope.', 'It cannot reach other blocks.')
K.quiz('e', 'atomicCAS returns', ['The new value', 'The old value', 'true or false', 'Nothing'], 1, 'Compare with what you expected.', 'Getting back cmp means you won.')
K.quiz('e', 'Threads of different blocks share data through global memory. Use', ['__syncthreads()', 'Atomics, or a new kernel launch', 'Registers', 'Nothing'], 1, 'Across blocks.', 'A barrier only covers one block.')
K.quiz('m', 'With a lock, who waits?', ['Every thread of the block', 'Only threads that want the lock', 'No one', 'The CPU'], 1, 'Exclusive, not collective.', 'Others keep working.')
K.quiz('m', 'What does __threadfence() do?', ['Waits for all threads', 'Orders this thread\'s writes as seen by others', 'Frees a lock', 'Starts a kernel'], 1, 'Visibility order.', 'It does not make anyone wait.')
K.quiz('m', '10 blocks × 256 threads with privatisation. Global atomics', ['2560', '256', '10', '1'], 2, 'One per block.', '10.')
K.quiz('m', 'A CAS spin lock is fair', ['Always', 'No: a thread can lose again and again', 'Only on Volta', 'Only with 2 threads'], 1, 'No queue.', 'Use a ticket lock for order.')
K.quiz('h', 'Why can every thread taking a CAS lock hang a pre-Volta GPU?', ['Too many registers', 'The warp keeps spinning for the losers and the winner never reaches release', 'Atomics are not supported', 'Shared memory overflows'], 1, 'Lock step lanes.', 'Intra warp deadlock.')
K.quiz('h', 'Priorities 0, 1, 2, 2, 2, 3, 4, every thread adds 1 when done. Who waits for ever?', ['Nobody', 'The threads with priority 3 and 4', 'Priority 2', 'Priority 0'], 1, 'Counter jumps 2 to 5.', 'Levels 3 and 4 are skipped.')
K.quiz('h', 'grid.sync() is only safe when', ['Blocks are 32 threads', 'All blocks are resident at once (cooperative launch)', 'The grid has one block', 'Always'], 1, 'Everyone must be able to arrive.', 'Otherwise waiting blocks block the ones not yet started.')
K.quiz('x', 'Block priority code reads the counter without volatile. Risk', ['None', 'The compiler moves the read out of the loop and it spins for ever', 'A race on shared memory', 'A slower launch only'], 1, 'Hoisting.', 'Read volatile or atomically.')
K.quiz('x', 'In privatisation, the shared counter should start at', ['The global value', '0', 'blockIdx.x', 'Any value'], 1, 'Each block adds only its own count.', 'Starting from the global value counts it twice.')

K.calc('e', '10 blocks × 256 threads, one global atomic per thread. Global atomics?', '2560', 'Multiply.',
       ['10 × 256.', '= 2560.', eq('2560 global atomics')], check=2560)
K.calc('e', 'Same, privatised. Global atomics?', '10', 'One per block.',
       ['Shared atomics do the counting.', 'Thread 0 of each block adds once.', eq('10 global atomics')], check=10)
K.calc('e', 'Same, privatised. Shared atomics?', '2560', 'One per thread.',
       ['Each thread adds 1 in shared memory.', '10 × 256.', eq('2560 shared atomics')], check=2560)
K.calc('m', 'How many times fewer global atomics with privatisation?', '256', '2560 ÷ 10.',
       ['Per thread: 2560.', 'Per block: 10.', eq('256 times fewer')], check=256)
K.calc('m', '2²⁰ values, blocks of 1024, one atomic per block. Atomics?', '1024', 'Blocks.',
       ['1,048,576 ÷ 1024.', '= 1024 blocks.', eq('1024 atomics against 1,048,576')], check=1024)
K.calc('m', 'Priorities 0, 1, 2, 2, 2, 3, 4. Counter value after level 2 finishes?', '5', '2 + 3.',
       ['Level 2 starts with counter 2.', 'Three threads each add 1.', eq('5')], check=5)
K.calc('m', 'In that case, how many threads wait for ever?', '2', 'Levels 3 and 4.',
       ['The counter skipped 3 and 4.', 'One thread at each.', eq('2 threads')], check=2)
K.calc('h', 'T4: 40 SMs, 4 blocks of 256 per SM. Largest cooperative grid in blocks?', '160', 'Multiply.',
       ['All blocks must be resident.', '40 × 4.', eq('160 blocks')], check=160)
K.calc('h', 'Ticket lock: you got ticket 4 and now_serving starts at 0. Critical sections before yours?', '4', 'Tickets 0 to 3.',
       ['Tickets 0, 1, 2 and 3 go first.', 'Each enters once.', eq('4 critical sections')], check=4)
K.calc('x', '2²⁰ values in blocks of 256, privatised. Global atomics?', '4096', 'Blocks.',
       ['1,048,576 ÷ 256.', '= 4096.', eq('4096 global atomics')], check=4096)
K.calc('x', 'grid.sync() once per priority level, levels 0 to 7. Calls per thread?', '8', 'One per level.',
       ['Every thread must call it the same number of times.', 'Levels 0 to 7 is 8 levels.', eq('8 calls')], check=8)

K.assign('globalatomics', 'e', 'Count the global atomics',
         '<p>Write <code>global_atomics(blocks, tpb, privatised)</code>. Every thread adds 1 to one counter. Without privatisation every thread does one global atomic. With privatisation each block does one. Return the number of global atomics.</p>',
         '''
def global_atomics(blocks, tpb, privatised):
    # your code here
    pass
''', [("global_atomics(10, 256, False)", 2560), ("global_atomics(10, 256, True)", 10), ("global_atomics(4096, 256, True)", 4096), ("global_atomics(1, 32, False)", 32)],
         '''
def global_atomics(blocks, tpb, privatised):
    if privatised:
        return blocks
    return blocks * tpb
''', 'One per block or one per thread.', '<p>This is workbook P10.1.6.</p>')
K.assign('prioritystuck', 'm', 'Who waits for ever?',
         '<p>Write <code>stuck(pri)</code>. <code>pri[t]</code> is the priority of thread t. The counter starts at 0. All waiting threads whose priority equals the counter run, and each adds 1 to the counter. Repeat until no waiting thread matches. Return the sorted list of threads that never run.</p>',
         '''
def stuck(pri):
    # your code here
    pass
''', [("stuck([0, 1, 2, 2, 2, 3, 4])", [5, 6]), ("stuck([0, 1, 2, 3])", []), ("stuck([1, 1, 2])", [0, 1, 2]), ("stuck([0, 0, 2])", [])],
         '''
def stuck(pri):
    done = [False] * len(pri)
    now = 0
    while True:
        group = [t for t, p in enumerate(pri) if not done[t] and p == now]
        if not group:
            break
        for t in group:
            done[t] = True
        now += len(group)
    return [t for t in range(len(pri)) if not done[t]]
''', 'Keep a done flag per thread and loop until nobody matches.', '<p>In the last test two threads at level 0 push the counter to 2, which happens to match. The result depends on luck, which is the problem.</p>')

K.must('Barrier against lock', '__syncthreads(): all threads of one block meet. Lock: one thread at a time, only those who want it wait.')
K.must('Who shares', 'Registers: nothing. Shared memory: __syncthreads(). Global across blocks: atomics, locks or a new kernel.')
K.must('atomicCAS lock', 'Spin on atomicCAS(&l, 0, 1) until it returns 0, do the work, call __threadfence(), then atomicExch(&l, 0). One thread per block takes it.')
K.must('Privatisation', 'Count in shared memory, then one global atomicAdd per block. 10 × 256: 2560 global atomics become 10.')
K.must('Priority counter', 'Same level runs together, levels get skipped, and non resident blocks can deadlock. grid.sync() needs a cooperative launch.')

T = K.topic(
    slug='barriers-atomics', topic='barriers-atomics', step=(7, 'Synchronisation', 'gpu-sync', 'Learn why shared updates go wrong, how classic locks fix it, and how GPUs use barriers and atomic instructions.', 'College'),
    title='Barriers, atomics and GPU locks', short='Barriers and atomics', badge='7.2', minutes=45,
    lead='Choose between a barrier and a lock, build a lock from atomicCAS without hanging the GPU, cut atomic traffic with privatisation, and see why a simple priority counter fails.',
    desc='__syncthreads against an atomicCAS lock, who shares a variable decides the tool, atomic functions, the intra warp deadlock and missing fences in the slide\'s lock, ticket locks, memory fence scopes, privatisation with workbook P10.1.6, the priority counter and its three problems, and cooperative groups with grid.sync.',
    summary='Barriers, atomics, CAS and ticket locks, privatisation, priority locks, grid sync.',
    keywords=['__syncthreads', 'atomicCAS', 'atomicAdd', 'privatisation', 'cooperative groups', 'grid.sync'],
    recap='<p>A barrier makes a block meet, a lock lets one thread in at a time. Atomics are correct but serialise on one address, so count in shared memory first. Grid wide waiting needs a cooperative launch.</p>')
