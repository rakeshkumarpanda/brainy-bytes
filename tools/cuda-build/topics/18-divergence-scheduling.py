# Chapter 6.1: Warp divergence and warp scheduling. Source: lecture 7 (warp divergence, SIMT masks, the warp
# scheduling deck: round robin, greedy then oldest, two level), lecture 6 (latency hiding by counting warps),
# Quiz 1 question 9 with Rakesh's worked solution, workbook 6.2, 7.3 and 7.4.
# Beyond the lecture: predication for short branches, branch free code, and __syncwarp under independent thread
# scheduling.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu, nb

K = Kit()

Q9 = r'''
#include <cstdio>

__global__ void addArrays(const float *a, const float *b, float *c, int N) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < N) {
        if (tid % 4 == 1)
            c[tid] = a[tid] - b[tid];   // Branch A: lanes 1, 5, 9, ..., 29
        else
            c[tid] = a[tid] + b[tid];   // Branch B: the other 24 lanes
    }
}

int main() {
    const int N = 32;
    float h[N], ha[N], hb[N], *a, *b, *c;
    for (int i = 0; i < N; ++i) { ha[i] = i + 1; hb[i] = 2 * (i + 1); }
    cudaMalloc(&a, sizeof(ha)); cudaMalloc(&b, sizeof(hb)); cudaMalloc(&c, sizeof(h));
    cudaMemcpy(a, ha, sizeof(ha), cudaMemcpyHostToDevice);
    cudaMemcpy(b, hb, sizeof(hb), cudaMemcpyHostToDevice);
    addArrays<<<1, 32>>>(a, b, c, N);
    cudaMemcpy(h, c, sizeof(h), cudaMemcpyDeviceToHost);
    printf("c[1] = %.0f, c[2] = %.0f\n", h[1], h[2]);
    cudaFree(a); cudaFree(b); cudaFree(c);
    return 0;
}
'''

BRANCHFREE = r'''
// Same result without a branch: every lane runs the same instructions
__global__ void addOrSub(const float *a, const float *b, float *c, int N) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N) return;
    float sign = (tid % 4 == 1) ? -1.0f : 1.0f;   // compiles to a select, not a jump
    c[tid] = a[tid] + sign * b[tid];
}

// Divergence only between warps, never inside one
__global__ void perWarp(float *x, int N) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= N) return;
    if ((tid / 32) % 2 == 0) x[tid] *= 2.0f;       // whole warps choose the same path
    else                    x[tid] += 1.0f;
}
'''

K.code('div', r'''
# Time and efficiency of one warp: each path any lane takes costs its full length
def warp_cost(path_of_lane, length):
    used = set(path_of_lane)
    time = sum(length[p] for p in used)
    useful = sum(length[p] for p in path_of_lane)
    return time, round(100 * useful / (32 * time), 1)
L = {"A": 10, "B": 10}
print("tid % 2  :", warp_cost(["A" if t % 2 == 0 else "B" for t in range(32)], L))
print("tid % 4==1:", warp_cost(["A" if t % 4 == 1 else "B" for t in range(32)], L))
print("8 vs 24  :", warp_cost(["A"] * 8 + ["B"] * 24, {"A": 10, "B": 30}))
print("Q9 sum of ids in A:", sum(t for t in range(32) if t % 4 == 1))
''')

K.code('latency', r'''
# How many warps hide a wait of W ticks if each warp has c ticks of work between waits?
import math
def warps_needed(wait, work):
    return math.ceil((wait + work) / work)
print("work 1, wait 3:", warps_needed(3, 1))
print("L=400, 20 instructions per load:", warps_needed(400, 20))
print("L=400, 10 instructions per load:", warps_needed(400, 10))
''')

K.lesson('div', 'Warp divergence', f'''
<p>All lanes of a warp share one instruction stream. At an <code>if</code> where lanes disagree, the warp runs the <b>then</b> path with the other lanes switched off (masked), then the <b>else</b> path with the first group masked. Both paths cost time for the whole warp.</p>
{fxs(
    fx('Warp time', 'time = sum of the lengths of every path at least one lane takes', 'Paths no lane takes are skipped.', key=True),
    fx('Efficiency', 'efficiency = (sum over lanes of their path length) ÷ (32 × warp time)', '8 lanes on a 10 tick path and 24 on a 30 tick path: 800 ÷ 1280 = 62.5 percent.', key=True),
    fx('Worst case', '32 different paths: 32 × L, efficiency 1/32 = 3.1 percent', 'A 32 times slowdown.'))}
{viz('diverge')}
{code('div')}
{note('Divergence only happens inside a warp. If whole warps take the same side, as with if ((tid / 32) % 2 == 0), there is no divergence cost at all.', 'tip')}
''', kw=['warp divergence', 'SIMT mask', 'branch', 'efficiency', 'paths', 'serialisation'])

K.lesson('q9', 'Quiz 1 question 9', f'''
{steps('Rakesh\'s worked solution', [
    'One warp of 32 threads, tid = 0 to 31.',
    'Branch A is taken when tid % 4 == 1: tid = 1, 5, 9, 13, 17, 21, 25, 29 (8 lanes).',
    'This is an arithmetic series: 8 terms, first 1, last 29.',
    'Sum = 8 × (1 + 29) ÷ 2 = 8 × 15.',
    eq('120')])}
{cu('quiz1_q9.cu', Q9, {6: 'Inside one warp, 8 lanes say yes and 24 say no, so the warp diverges.', 7: 'Branch A runs first with 24 lanes masked off.', 9: 'Then branch B runs with the 8 lanes of A masked off.', 16: 'a = 1 to 32 and b = 2 to 64, as in the quiz.'}, out='c[1] = -2, c[2] = 9')}
{cu('branch_free.cu', BRANCHFREE, {5: 'A select picks −1 or +1 without jumping. Every lane runs the same two instructions.', 13: 'tid / 32 is the warp number, so all 32 lanes of a warp agree and nothing is masked.'})}
{deep('predication', '<p>For very short branches the compiler often uses predicated instructions: every lane computes both results and keeps the one its predicate selects. No jump happens, so the cost is just the extra instructions.</p>')}
''', kw=['Quiz 1 question 9', 'arithmetic series', 'branch free', 'select', 'predication'])

K.lesson('sched', 'Warp schedulers', f'''
<p>Each SM sub partition has a warp scheduler that issues one instruction per tick from a warp that is ready. Which ready warp it picks changes how well waiting is hidden.</p>
{table(['Policy', 'Rule', 'Strength', 'Weakness'], [
    ['Round robin (RR)', 'take turns in order', 'fair', 'all warps reach their loads together and wait together'],
    ['Greedy then oldest (GTO)', 'keep issuing the same warp until it stalls, then the oldest ready one', 'spreads loads out, good cache locality', 'less fair, a warp can starve'],
    ['Two level', 'RR inside a small active group, switch group when all stall', 'between the two', 'needs tuning of the group size']])}
{viz('sched')}
{fxs(
    fx('Rules (workbook 7.4)', 'one instruction per tick, a load at tick t lets the warp go again at t + L', 'finish = tick of the last load + L.'),
    fx('Best possible finish', 'finish ≥ (total instructions − 1) + L', '4 warps × 12 instructions, L = 12: 47 + 12 = 59. GTO reaches it.', key=True))}
''', kw=['warp scheduler', 'round robin', 'greedy then oldest', 'GTO', 'two level', 'idle ticks'])

K.lesson('hide', 'How many warps hide the wait?', f'''
<p>If each warp does c ticks of work and then waits W ticks, other warps must fill the gap. While one warp waits, the others each need c ticks of their own work.</p>
{fxs(fx('Warps to hide a wait', 'warps = ⌈(W + c) ÷ c⌉', 'Work 1 tick, wait 3: 4 warps. One warp leaves 75 percent idle, two leave 50 percent.', key=True))}
{code('latency')}
{note('More independent instructions per warp (unrolling, ILP) cut the warps needed: c from 10 to 20 at W = 400 saves 20 warps.', 'tip')}
{nb('08-warps-races-atomics.ipynb', 'Notebook: warps, divergence, races and atomics', 'Measure a divergent branch and sum a warp with shuffles.')}
''', kw=['latency hiding', 'warps needed', 'ILP', 'unrolling'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A group of 32 must walk together. If some want to go left and some right, the group visits both places one after the other.</p>',
    '<p>Warp time = sum of used path lengths. Efficiency = lane ticks ÷ 32 × time. Q9: ids 1, 5, …, 29 sum to 120. GTO beats RR when loads dominate.</p>',
    '<p>Independent thread scheduling (Volta and later) keeps a program counter per thread, so diverged lanes can interleave, but they still issue separately. Reconverge with __syncwarp() before warp level operations.</p>',
    '<p>Research schedulers (cache conscious wavefront scheduling, CAWS) choose warps to protect L1 locality. Dynamic warp formation regroups lanes from different warps that take the same path.</p>')}
''', kw=['ladder', 'independent thread scheduling', '__syncwarp', 'CCWS', 'dynamic warp formation'])

K.quiz('e', 'Warp divergence happens when', ['Two warps take different paths', 'Lanes of one warp take different paths', 'A block is too big', 'Memory is slow'], 1, 'Inside a warp.', 'Only within a warp.')
K.quiz('e', 'tid % 2 == 0, both paths 10 ticks. Warp time', ['10', '20', '5', '320'], 1, 'Both paths run.', '20 ticks.')
K.quiz('e', 'Quiz 1 Q9: sum of thread ids taking branch A', ['112', '120', '128', '496'], 1, '1 + 5 + … + 29.', '120.')
K.quiz('m', 'if ((threadIdx.x / 32) % 2 == 0) in a 256 thread block. Split warps', ['0', '4', '8', '256'], 0, 'Whole warps agree.', 'None.')
K.quiz('m', 'A 4-way switch on tid % 4, each case 10 ticks', ['10 ticks, 100 percent', '40 ticks, 25 percent', '20 ticks, 50 percent', '40 ticks, 100 percent'], 1, 'Four paths.', '40 ticks, a quarter useful.')
K.quiz('m', 'if (tid < 40) in a 64 thread block splits', ['Warp 0', 'Warp 1', 'Both', 'Neither'], 1, 'Lanes 32 to 63.', 'Warp 1 has 8 yes and 24 no.')
K.quiz('m', 'Round robin loses time on memory heavy code because', ['It is slow to switch', 'All warps reach their loads together and wait together', 'It starves warps', 'It uses more registers'], 1, 'Lockstep.', 'No one is left to run.')
K.quiz('h', 'A path of 8 lanes × 10 ticks and 24 lanes × 30 ticks. Efficiency', ['50 percent', '62.5 percent', '75 percent', '25 percent'], 1, '800 ÷ 1280.', '62.5 percent.')
K.quiz('h', 'Workbook 7.4: GTO finishes at', ['75', '63', '59', '48'], 2, 'Best possible.', '(48 − 1) + 12 = 59.')
K.quiz('h', 'Work 1 tick, wait 3. Warps to keep the SM busy', ['2', '3', '4', '8'], 2, '(3 + 1) ÷ 1.', '4.')
K.quiz('x', 'GTO with 3 warps (C C C L, L = 12) leaves', ['0 idle ticks', '6 idle ticks', '16 idle ticks', '2 idle ticks'], 1, 'Needs 4 warps.', '6 idle ticks.')
K.quiz('x', 'Under independent thread scheduling, divergent lanes', ['Run at the same time on separate units', 'Still issue separately, but may interleave and need __syncwarp to reconverge', 'Are merged automatically', 'Cannot diverge'], 1, 'Separate program counters.', 'Issue is still per path.')

K.calc('e', 'Quiz 1 Q9: sum of ids with tid % 4 == 1 for tid 0 to 31?', '120', 'Arithmetic series.',
       ['Terms 1, 5, …, 29: 8 of them.', '8 × (1 + 29) ÷ 2.', eq('120')], check=sum(t for t in range(32) if t % 4 == 1))
K.calc('e', 'A 4-way switch, 10 ticks per case. Efficiency in percent?', '25', '1 ÷ 4.',
       ['Time 40.', 'Each lane useful 10.', eq('320 ÷ 1280 = 25 percent')], check=25)
K.calc('e', 'Quiz 1 Q9: value of c[1] (a = 1 to 32, b = 2 to 64)?', '-2', 'Branch A subtracts.',
       ['a[1] = 2, b[1] = 4.', '2 − 4.', eq('−2')], check=-2)
K.calc('m', 'Path A 8 lanes × 10, path B 24 lanes × 30. Efficiency in percent? (one decimal)', '62.5', 'Useful ÷ 32 × time.',
       ['Time 40.', 'Useful 80 + 720 = 800.', eq('800 ÷ 1280 = 62.5 percent')], check=62.5)
K.calc('m', 'if (tid < 48): then 20 ticks, else 5 ticks. Warp 1 time?', '25', 'Both paths in warp 1.',
       ['Warp 1 holds tid 32 to 63: 16 yes, 16 no.', '20 + 5.', eq('25 ticks at 50 percent')], check=25)
K.calc('m', 'RR in workbook 7.4: finish tick?', '75', 'Last load at 63.',
       ['Loads come in 3 rounds, each round ends with 8 idle ticks except the last.', 'Last load at tick 63.', eq('63 + 12 = 75')], check=75)
K.calc('m', '2 warps, C C C L × 3, L = 6. GTO finish?', '31', 'Timeline 00001111.00001111.00001111.',
       ['Last load at tick 25.', '25 + 6.', eq('31 ticks, 2 idle')], check=31)
K.calc('h', 'L = 400, 20 instructions per load. Warps to hide it?', '21', '⌈(400 + 20) ÷ 20⌉.',
       ['420 ÷ 20.', '= 21.', eq('21 warps (41 with only 10 instructions)')], check=-(-420 // 20))
K.calc('h', 'A scheduler holds 8 warps with c = 10. Longest wait it can hide (ticks)?', '70', '(warps − 1) × c.',
       ['The other 7 warps provide 7 × 10 ticks of work.', 'While one waits.', eq('70 ticks')], check=70)
K.calc('x', 'A scheduler holds 16 warps. For L = 400, independent instructions c needed? (nearest whole, round up)', '27', '(16 − 1) c ≥ 400.',
       ['c ≥ 400 ÷ 15 = 26.67.', 'Round up.', eq('27 instructions')], check=-(-400 // 15))
K.calc('x', '3 warps, L = 12, C C C L × 3. RR finish?', '65', 'Simulate or reason by rounds.',
       ['Rounds of 12 issue ticks, loads at 9 to 11, ready from 21.', 'Last load at tick 53.', eq('53 + 12 = 65')], check=65)

K.assign('warptime', 'e', 'Divergent warp cost',
         '<p>Write <code>warp_time(paths, length)</code>. <code>paths</code> gives the path name of each lane, <code>length</code> maps a path to its ticks. Return <code>[time, efficiency percent rounded to 1 decimal]</code>.</p>',
         '''
def warp_time(paths, length):
    # your code here
    pass
''', [("warp_time(['A'] * 16 + ['B'] * 16, {'A': 10, 'B': 10})", [20, 50.0]), ("warp_time(['A'] * 8 + ['B'] * 24, {'A': 10, 'B': 30})", [40, 62.5]), ("warp_time(['A'] * 32, {'A': 7})", [7, 100.0])],
         '''
def warp_time(paths, length):
    time = sum(length[p] for p in set(paths))
    useful = sum(length[p] for p in paths)
    return [time, round(100 * useful / (len(paths) * time), 1)]
''', 'Sum each used path once for the time.', '<p>A warp that agrees everywhere is 100 percent efficient.</p>')
K.assign('schedsim', 'h', 'Scheduler simulator',
         '<p>Write <code>simulate(nw, L, policy)</code> for warps running C C C L three times (C 1 tick, a load lets the warp issue again at t + L). Policy is <code>"rr"</code> or <code>"gto"</code> (stay on the last warp while it is ready, else the lowest numbered ready warp). Return <code>[finish, idle]</code> with finish = last load tick + L.</p>',
         '''
def simulate(nw, L, policy):
    # your code here
    pass
''', [("simulate(4, 12, 'rr')", [75, 16]), ("simulate(4, 12, 'gto')", [59, 0]), ("simulate(2, 6, 'rr')", [37, 8]), ("simulate(2, 6, 'gto')", [31, 2])],
         '''
def simulate(nw, L, policy):
    prog = 'CCCL' * 3
    pc = [0] * nw
    ready = [0] * nw
    t, last, idle, last_load = 0, -1, 0, 0
    while any(p < len(prog) for p in pc):
        cand = [w for w in range(nw) if pc[w] < len(prog) and ready[w] <= t]
        pick = None
        if cand:
            if policy == 'rr':
                for k in range(1, nw + 1):
                    w = (last + k) % nw
                    if w in cand:
                        pick = w
                        break
            else:
                pick = last if last in cand else min(cand)
        if pick is None:
            idle += 1
        else:
            ins = prog[pc[pick]]
            pc[pick] += 1
            ready[pick] = t + L if ins == 'L' else t + 1
            if ins == 'L':
                last_load = t
            last = pick
        t += 1
    return [last_load + L, idle]
''', 'Loop over ticks, collect ready warps, pick by policy.', '<p>These four results are the workbook 7.4 answers.</p>')

K.must('Divergence', 'Inside a warp only. Time = sum of used path lengths. Efficiency = lane ticks ÷ (32 × time).')
K.must('Q9', 'tid % 4 == 1 → lanes 1, 5, …, 29, sum 120.')
K.must('Avoid it', 'Branch on warp number, use selects, keep data dependent branches short.')
K.must('Schedulers', 'RR waits together, GTO spreads loads (best = (instructions − 1) + L), two level in between.')
K.must('Hiding', 'Warps = ⌈(W + c) ÷ c⌉. More ILP per warp means fewer warps needed.')

T = K.topic(
    slug='divergence-scheduling', topic='divergence-scheduling', step=(6, 'Execution and overlap', 'gpu-exec', 'See how branches and warp schedulers decide the speed of a warp, and overlap copies with kernels using streams.', 'College'),
    title='Warp divergence and warp scheduling', short='Divergence', badge='6.1', minutes=45,
    lead='See what happens when lanes of a warp disagree at a branch, solve Quiz 1 question 9, and compare round robin with greedy then oldest scheduling tick by tick.',
    desc='SIMT masks, warp time and efficiency for divergent branches, Quiz 1 question 9, branch free code, RR, GTO and two level schedulers with the workbook timelines, best possible finish and warps needed to hide waits.',
    summary='Divergence cost, Quiz 1 Q9, branch free tricks, warp schedulers, hiding waits.',
    keywords=['warp divergence', 'SIMT', 'Quiz 1', 'round robin', 'GTO', 'latency hiding'],
    recap='<p>A divergent warp pays for every path any lane takes. Schedulers that let one warp run ahead spread loads out and hide waits better.</p>')
