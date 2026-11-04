# Chapter 5.5: Scan and histogram. Not in lectures 1 to 12: added because every GPU course and library relies on
# them (stream compaction, radix sort, sparse matrices, image statistics). Builds on the reduction tree (chapter 5.1)
# and atomics (chapter 7.2). Algorithms: Hillis and Steele (1986), Blelloch (1990), privatised histograms with shared
# memory atomics as in the CUDA samples and "Programming Massively Parallel Processors".
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

HS = r'''
// Inclusive Hillis and Steele scan of one block (n = blockDim.x <= 1024), double buffered
__global__ void scanBlock(const int *in, int *out, int n) {
    extern __shared__ int buf[];               // 2 * n ints: two halves we swap between
    int t = threadIdx.x, src = 0, dst = n;
    buf[t] = (t < n) ? in[t] : 0;
    __syncthreads();
    for (int off = 1; off < n; off <<= 1) {
        int v = buf[src + t];
        if (t >= off) v += buf[src + t - off];  // add the value off places to the left
        buf[dst + t] = v;
        __syncthreads();
        int tmp = src; src = dst; dst = tmp;    // swap halves, never read and write one array
    }
    if (t < n) out[t] = buf[src + t];
}
'''

HIST = r'''
#define BINS 256

// Histogram of bytes: private copy per block in shared memory, then merge
__global__ void histogram(const unsigned char *data, int n, unsigned int *hist) {
    __shared__ unsigned int local[BINS];
    for (int b = threadIdx.x; b < BINS; b += blockDim.x) local[b] = 0;
    __syncthreads();
    for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < n; i += blockDim.x * gridDim.x)
        atomicAdd(&local[data[i]], 1u);         // fast shared memory atomic
    __syncthreads();
    for (int b = threadIdx.x; b < BINS; b += blockDim.x)
        if (local[b]) atomicAdd(&hist[b], local[b]);   // one global atomic per bin per block
}
'''

K.code('scan', r'''
# Inclusive and exclusive scan, serial and Hillis-Steele
a = [3, 1, 7, 0, 4, 1, 6, 3]
inc, s = [], 0
for v in a:
    s += v
    inc.append(s)
exc = [0] + inc[:-1]
print("inclusive", inc)
print("exclusive", exc)
x, off, adds = a[:], 1, 0
while off < len(x):
    x = [x[i] + (x[i - off] if i >= off else 0) for i in range(len(x))]
    adds += len(x) - off
    off *= 2
print("Hillis-Steele", x, "adds", adds)
''')

K.code('compact', r'''
# Stream compaction: keep the even numbers, in order, using an exclusive scan of flags
data = [5, 8, 2, 7, 6, 1, 4, 9]
flags = [1 if v % 2 == 0 else 0 for v in data]
pos, s = [], 0
for f in flags:
    pos.append(s)        # exclusive scan: where each kept value goes
    s += f
out = [None] * s
for i, v in enumerate(data):
    if flags[i]:
        out[pos[i]] = v  # every thread can write at the same time, no clashes
print("flags", flags, "positions", pos)
print("compacted", out)
''')

K.lesson('scan', 'Prefix sums: inclusive and exclusive', f'''
<p>A <b>scan</b> (prefix sum) turns a list into running totals. It looks serial, because each total needs the one before it, but it can be done in log₂ n parallel steps.</p>
{fxs(
    fx('Inclusive scan', 'y<sub>i</sub> = x<sub>0</sub> + x<sub>1</sub> + … + x<sub>i</sub>', '[3, 1, 7, 0] → [3, 4, 11, 11].', key=True),
    fx('Exclusive scan', 'y<sub>i</sub> = x<sub>0</sub> + … + x<sub>i−1</sub>, y<sub>0</sub> = 0', '[3, 1, 7, 0] → [0, 3, 4, 11]. The inclusive scan shifted right by one.', key=True))}
{viz('scan')}
{code('scan')}
{table(['Algorithm', 'Steps', 'Additions', 'Note'], [
    ['Serial loop', 'n − 1', 'n − 1', 'one thread'],
    ['Hillis and Steele', 'log₂ n', 'n log₂ n − (n − 1)', 'simple, extra work'],
    ['Blelloch', '2 log₂ n', 'about 2(n − 1)', 'work efficient, exclusive']])}
''', kw=['scan', 'prefix sum', 'inclusive', 'exclusive', 'Hillis Steele', 'Blelloch', 'work efficient'])

K.lesson('code', 'A block scan in CUDA', f'''
{cu('scan_block.cu', HS, {3: 'Two halves of shared memory. A step reads one half and writes the other.', 7: 'off = 1, 2, 4, …: log₂ n steps.', 9: 'Threads with t < off have nothing to the left at this distance and keep their value.', 11: 'Every thread must write before anyone reads the next step.', 12: 'Swapping halves avoids the race where a thread reads a value its neighbour already overwrote in this step.'})}
{note('Updating one array in place with buf[t] += buf[t − off] is a race: thread t may read buf[t − off] after thread t − off has already added to it. Double buffering or a barrier between the read and the write fixes it.', 'warn')}
{deep('scans larger than one block', '<p>Scan each block, write each block\'s total to an array, scan that array, then add each block\'s scanned total to all its elements. CUB\'s DeviceScan does it in a single pass with decoupled look back.</p>')}
''', kw=['block scan', 'double buffering', 'race', 'multi block scan', 'CUB DeviceScan'])

K.lesson('uses', 'What scans are for: compaction', f'''
<p>Filtering a list on the GPU is hard because each thread does not know where to write its kept value. An exclusive scan of 0/1 flags gives every kept value its output position, so all threads can write at the same time without clashing.</p>
{code('compact')}
{table(['Use', 'How the scan helps'], [
    ['Stream compaction', 'positions of kept items'], ['Radix sort', 'positions of keys with bit 0 and bit 1'],
    ['Sparse matrices (CSR)', 'row start offsets from row lengths'], ['Allocating variable output', 'each thread\'s write offset']])}
''', kw=['stream compaction', 'filter', 'radix sort', 'CSR', 'offsets'])

K.lesson('hist', 'Histograms and atomic contention', f'''
<p>A histogram counts how many values fall in each bin. Many threads may hit the same bin at once, so the increment must be an atomic operation. When many threads hit one address, the atomics are done one after another (<b>contention</b>).</p>
{fxs(
    fx('Global atomics without privatisation', 'one atomic per element', 'n = 10⁶ bytes → 10⁶ global atomics, all on 256 addresses.'),
    fx('Privatised (shared memory) histogram', 'global atomics = blocks × bins at most', 'Each block counts in fast shared memory, then merges once.', key=True))}
{cu('histogram.cu', HIST, {5: 'A private histogram for this block in shared memory.', 6: 'Clear it with a block stride loop: 256 bins and any number of threads.', 8: 'Grid stride loop over the data (chapter 2.2).', 9: 'Shared memory atomics are much cheaper than global ones, and only threads of this block compete.', 12: 'Merge: at most 256 global atomics per block instead of one per element.'})}
{scene('a class vote', '<p>Asking 1000 pupils to walk to one ballot box makes a long queue. Letting each class count its own votes, then sending one sheet per class to the head teacher, removes the queue.</p>')}
''', kw=['histogram', 'atomicAdd', 'contention', 'privatisation', 'shared memory atomics'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Running totals and tallies. With many helpers the totals can be built in a few rounds, and each class can count its own votes first.</p>',
    '<p>Inclusive and exclusive scan, Hillis and Steele (log n steps, n log n work), Blelloch (2 log n steps, 2n work). Histogram: private shared memory copy, then one global atomic per bin per block.</p>',
    '<p>Bank conflicts in Blelloch are removed with padding. Warp scans use __shfl_up_sync. Histograms with very skewed data (one hot bin) suffer most contention, aggregating in registers first helps.</p>',
    '<p>Single pass scans with decoupled look back (Merrill and Garland 2016) run at memory bandwidth. Onesweep radix sort builds on them and is used in CUB.</p>')}
''', kw=['ladder', '__shfl_up_sync', 'decoupled look back', 'Onesweep'])

K.quiz('e', 'Inclusive scan of [1, 2, 3, 4]', ['[1, 3, 6, 10]', '[0, 1, 3, 6]', '[10, 9, 7, 4]', '[1, 2, 3, 4]'], 0, 'Running totals.', '1, 3, 6, 10.')
K.quiz('e', 'Exclusive scan of [1, 2, 3, 4]', ['[1, 3, 6, 10]', '[0, 1, 3, 6]', '[0, 1, 2, 3]', '[1, 3, 6, 0]'], 1, 'Shift right, start at 0.', '0, 1, 3, 6.')
K.quiz('e', 'Why must histogram increments be atomic?', ['For speed', 'Many threads may add to the same bin at once', 'Bins are in constant memory', 'They are not'], 1, 'Read, add, write.', 'Otherwise updates are lost (chapter 7.1).')
K.quiz('m', 'Hillis and Steele steps for 16 values', ['4', '8', '15', '16'], 0, 'log₂ 16.', '4.')
K.quiz('m', 'Additions of Hillis and Steele for 8 values', ['7', '14', '17', '24'], 2, '7 + 6 + 4.', '17.')
K.quiz('m', 'Stream compaction uses', ['A reduction', 'An exclusive scan of keep flags', 'A sort', 'Atomics only'], 1, 'Positions.', 'The scan gives each kept value its slot.')
K.quiz('m', 'A privatised histogram keeps', ['One copy in constant memory', 'One copy per block in shared memory, merged at the end', 'One copy per thread in global memory', 'No copy'], 1, 'Private per block.', 'Merge once.')
K.quiz('h', 'Why is buf[t] += buf[t − off] in place a bug?', ['It is slow', 'Thread t may read a value that thread t − off already updated this step', 'Out of bounds', 'Bank conflict'], 1, 'Read after write in one step.', 'Use two buffers or separate read and write with a barrier.')
K.quiz('h', 'Blelloch scan is called work efficient because', ['It uses fewer threads', 'It does about 2n additions, the same order as the serial loop', 'It has no barriers', 'It is inclusive'], 1, 'O(n) work.', 'Hillis and Steele does O(n log n).')
K.quiz('h', '1,000,000 bytes, 256 bins, 1000 blocks. Most global atomics with privatisation', ['1,000,000', '256,000', '256', '1000'], 1, 'Blocks × bins.', '1000 × 256.')
K.quiz('x', 'Contention is worst when', ['Values are spread evenly', 'Most values fall in one bin', 'There are many bins', 'Blocks are small'], 1, 'One hot address.', 'All atomics queue on one bin.')
K.quiz('x', 'CSR row offsets come from', ['A reduction of row lengths', 'An exclusive scan of row lengths', 'A transpose', 'A histogram of columns'], 1, 'Start of each row.', 'Row r starts after all earlier rows.')

K.calc('e', 'Inclusive scan of [3, 1, 7, 0, 4]: last value?', '15', 'Total.',
       ['3 + 1 + 7 + 0 + 4.', '= 15.', eq('15')], check=15)
K.calc('e', 'Exclusive scan of [3, 1, 7, 0, 4]: value at index 3?', '11', '3 + 1 + 7.',
       ['Sum of the values before index 3.', '3 + 1 + 7.', eq('11')], check=11)
K.calc('e', 'Hillis and Steele steps for 1024 values?', '10', 'log₂.',
       ['2¹⁰ = 1024.', 'One step per doubling.', eq('10')], check=10)
K.calc('m', 'Hillis and Steele additions for 16 values?', '49', '15 + 14 + 12 + 8.',
       ['off 1: 15, off 2: 14, off 4: 12, off 8: 8.', 'Add.', eq('49 (serial needs 15)')], check=15 + 14 + 12 + 8)
K.calc('m', 'Blelloch additions for 16 values (up sweep + down sweep)?', '30', '2(n − 1).',
       ['Up sweep 15.', 'Down sweep 15.', eq('30')], check=30)
K.calc('m', 'Keep flags [1, 0, 1, 1, 0, 1]. Output position of the last kept value?', '3', 'Exclusive scan.',
       ['Exclusive scan: [0, 1, 1, 2, 3, 3].', 'Index 5 holds 3.', eq('Position 3')], check=3)
K.calc('m', 'Shared memory for a 256 bin unsigned int histogram, bytes?', '1024', '256 × 4.',
       ['256 bins.', '4 bytes each.', eq('1024 bytes')], check=1024)
K.calc('h', '10⁶ elements, 256 bins, 240 blocks. Global atomics with privatisation (at most)?', '61440', 'Blocks × bins.',
       ['240 × 256.', '= 61,440.', eq('61,440 instead of 1,000,000')], check=240 * 256)
K.calc('h', 'Hillis and Steele work ratio to serial for n = 1024 (one decimal)?', '9.0', 'n log n − (n − 1) over n − 1.',
       ['1024 × 10 − 1023 = 9217.', '÷ 1023.', eq('≈ 9.0 times more additions')], check=(1024 * 10 - 1023) / 1023, tol=0.05)
K.calc('x', 'Row lengths [2, 0, 3, 1]. CSR row offsets: last row starts at?', '5', 'Exclusive scan.',
       ['Exclusive scan [0, 2, 2, 5].', 'Row 3 starts at 5.', eq('5 (total 6 entries)')], check=5)
K.calc('x', 'Each block scans 1024 values. Values 2²⁰: block totals to scan in the second pass?', '1024', '2²⁰ ÷ 2¹⁰.',
       ['1,048,576 ÷ 1024.', '= 1024 block totals.', eq('One block can scan them')], check=1024)

K.assign('excl', 'e', 'Exclusive scan',
         '<p>Write <code>exclusive_scan(a)</code>.</p>',
         '''
def exclusive_scan(a):
    # your code here
    pass
''', [("exclusive_scan([3, 1, 7, 0, 4, 1, 6, 3])", [0, 3, 4, 11, 11, 15, 16, 22]), ("exclusive_scan([5])", [0]), ("exclusive_scan([])", [])],
         '''
def exclusive_scan(a):
    out, s = [], 0
    for v in a:
        out.append(s)
        s += v
    return out
''', 'Write the running total before adding.', '<p>The first test matches the Blelloch animation.</p>')
K.assign('compactf', 'm', 'Stream compaction with a scan',
         '<p>Write <code>compact(data, keep)</code> where <code>keep(v)</code> is a rule given as a string: <code>"even"</code>, <code>"odd"</code> or <code>"positive"</code>. Use an exclusive scan of flags to place values. Return the compacted list.</p>',
         '''
def compact(data, keep):
    # your code here
    pass
''', [("compact([5, 8, 2, 7, 6, 1, 4, 9], 'even')", [8, 2, 6, 4]), ("compact([-1, 3, 0, 2], 'positive')", [3, 2]), ("compact([2, 4], 'odd')", [])],
         '''
def compact(data, keep):
    rule = {'even': lambda v: v % 2 == 0, 'odd': lambda v: v % 2 == 1, 'positive': lambda v: v > 0}[keep]
    flags = [1 if rule(v) else 0 for v in data]
    pos, s = [], 0
    for f in flags:
        pos.append(s)
        s += f
    out = [None] * s
    for i, v in enumerate(data):
        if flags[i]:
            out[pos[i]] = v
    return out
''', 'Flags, exclusive scan, scatter.', '<p>Each value is written exactly once, so in CUDA all threads can scatter at the same time.</p>')

K.must('Scan', 'Inclusive y_i = x_0 + … + x_i. Exclusive starts at 0 and stops before x_i.')
K.must('Algorithms', 'Hillis and Steele: log₂ n steps, n log₂ n − (n − 1) adds. Blelloch: 2 log₂ n steps, 2(n − 1) adds.')
K.must('Race', 'Never scan in place in one step. Double buffer or barrier between read and write.')
K.must('Compaction', 'Exclusive scan of keep flags gives each kept value its output slot.')
K.must('Histogram', 'Atomics per bin. Privatise in shared memory, merge with at most blocks × bins global atomics.')

T = K.topic(
    slug='scan-histogram', topic='scan-histogram', step=(5, 'Parallel patterns', 'gpu-patterns', 'Learn the patterns behind most GPU code: reductions, tiled matrix multiply, stencils, convolution and scans.', 'College'),
    title='Scan, compaction and histograms', short='Scan and histogram', badge='5.5', minutes=45,
    lead='Build running totals in log₂ n parallel steps, use them to filter lists without clashes, and count values into bins with atomics that do not queue up.',
    desc='Inclusive and exclusive scans, Hillis and Steele and Blelloch, a double buffered block scan, multi block scans, stream compaction, CSR offsets, histograms, atomic contention and privatisation. A concept added beyond the lectures.',
    summary='Scans, work efficiency, compaction, histograms with privatised atomics.',
    keywords=['scan', 'prefix sum', 'Blelloch', 'stream compaction', 'histogram', 'atomics'],
    recap='<p>A scan gives running totals in log n steps and turns filtering into a clash free scatter. Histograms need atomics, best done in shared memory first.</p>')
