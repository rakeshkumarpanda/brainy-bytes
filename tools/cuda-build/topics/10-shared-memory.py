# Chapter 3.3: Shared memory and banks. Source: lecture 5 and 6 (shared memory, __shared__, __syncthreads, a
# programmer managed cache), lecture 11 (shared memory banks, conflicts, padding, output layout of the powers
# example), workbook 11.2 and 11.3.
# Beyond the lecture: dynamic shared memory with extern __shared__, the broadcast rule, 64-bit access on recent
# GPUs and the carve out between shared memory and L1.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

REVERSE = r'''
#include <cstdio>

// Reverse each block of 256 elements using a shared memory buffer
__global__ void reverseBlock(int *d, int n) {
    __shared__ int s[256];                   // one copy per block, on the SM
    int t = threadIdx.x;
    int i = blockIdx.x * blockDim.x + t;
    if (i < n) s[t] = d[i];                  // every thread loads one element
    __syncthreads();                         // wait until the whole tile is loaded
    int src = blockDim.x - 1 - t;
    if (i < n) d[i] = s[src];                // read an element another thread loaded
}

int main() {
    const int n = 1024;
    int h[n], *d;
    for (int k = 0; k < n; ++k) h[k] = k;
    cudaMalloc(&d, n * sizeof(int));
    cudaMemcpy(d, h, n * sizeof(int), cudaMemcpyHostToDevice);
    reverseBlock<<<n / 256, 256>>>(d, n);
    cudaMemcpy(h, d, n * sizeof(int), cudaMemcpyDeviceToHost);
    printf("%d %d %d\n", h[0], h[255], h[256]);
    cudaFree(d);
    return 0;
}
'''

DYN = r'''
// Dynamic shared memory: the size is chosen at launch time
__global__ void scaleTile(float *d, float a) {
    extern __shared__ float buf[];           // size comes from the third launch parameter
    int t = threadIdx.x, i = blockIdx.x * blockDim.x + t;
    buf[t] = d[i];
    __syncthreads();
    d[i] = a * buf[t];
}

void launch(float *d, int n, int threads) {
    size_t bytes = threads * sizeof(float);
    scaleTile<<<n / threads, threads, bytes>>>(d, 2.0f);
}
'''

POWERS = r'''
// 32 threads, each computes 32 powers of its own number into shared memory
__global__ void powers(float *out, const float *x) {
    __shared__ float A[32 * 32];
    __shared__ float B[32 * 32];
    int i = threadIdx.x;
    float v = 1.0f;
    for (int p = 0; p < 32; ++p) {
        v *= x[i];
        A[32 * i + p] = v;      // layout A: lanes 32 words apart, every lane in bank 0
        B[32 * p + i] = v;      // layout B: lanes 1 word apart, one lane per bank
    }
    __syncthreads();
    for (int k = i; k < 32 * 32; k += 32) out[k] = A[k] + B[k];
}
'''

K.code('banks', r'''
# Bank conflicts for stride s: lanes share a bank every 32 / gcd(s, 32) lanes
from math import gcd
for s in [1, 2, 6, 8, 32, 33]:
    banks_used = len({(s * t) % 32 for t in range(32)})
    print("stride", s, ":", 32 // banks_used, "way, gcd rule", gcd(s, 32))
print("broadcast: 1 way, every lane reads the same word")
''')

K.lesson('shared', 'Shared memory: a cache you control', f'''
<p>Each SM has a small, very fast memory that the threads of a block share. You declare it with <code>__shared__</code>, fill it from global memory, call <code>__syncthreads()</code> so everyone sees the full tile, and then read it many times. Unlike a normal cache, nothing is loaded or kept unless you write the code for it.</p>
{cu('reverse.cu', REVERSE, {5: '256 ints = 1 KB of shared memory per block.', 8: 'Each thread copies one element from slow global memory into the tile.', 9: 'The barrier: no thread continues until every thread of the block has reached this line.', 10: 'Thread t reads the element thread 255 − t wrote. Without the barrier it could read a value not loaded yet.'}, out='255 0 511')}
{cu('dynamic_shared.cu', DYN, {3: 'extern __shared__ with empty brackets means the size is decided at launch.', 12: 'The third value inside <<< >>> is the number of dynamic shared memory bytes per block.'})}
{note('__syncthreads() must be reached by every thread of the block. Putting it inside an if that only some threads enter can hang the block or give wrong results.', 'warn')}
''', kw=['__shared__', '__syncthreads', 'barrier', 'extern __shared__', 'dynamic shared memory', 'programmer managed cache'])

K.lesson('banks', 'Banks and conflicts', f'''
<p>Shared memory is split into 32 <b>banks</b>, each 4 bytes wide. Each bank can serve one 4 byte word per tick. If the 32 lanes of a warp hit 32 different banks, the access takes one pass. If several lanes need <b>different</b> words in the same bank, they take turns.</p>
{fxs(
    fx('Bank of an address', 'bank = ⌊byte address ÷ 4⌋ mod 32', 'Word w lives in bank w mod 32. Byte 260 is word 65, bank 1.', key=True),
    fx('Conflict for stride s', 'ways = gcd(s, 32)', 'Odd strides are always conflict free.', key=True),
    fx('Broadcast', 'same word for many lanes → no conflict', 'One read is sent to every lane that asked for it.'))}
{viz('banks')}
{code('banks')}
{scene('32 ticket windows', '<p>A station has 32 ticket windows. If 32 travellers each go to a different window, everyone is served at once. If 8 travellers queue at window 0 for different tickets, the last one waits 8 turns. If 8 travellers all want the same newspaper, the clerk holds it up once and everyone reads it.</p>')}
''', kw=['banks', 'bank conflict', 'gcd', 'broadcast', '4 byte words', 'n-way conflict'])

K.lesson('padding', 'Padding and layout fixes', f'''
{steps('Workbook 11.2 worked example: thread t reads tile[t][0] of a 32 × 32 float tile', [
    'Element [t][0] is word 32t, so bank (32t) mod 32 = 0 for every lane.',
    '32 different words in bank 0: 32 passes.',
    'Declare the tile as [32][33]: element [t][0] is word 33t, bank t mod 32.',
    eq('32 different banks, 1 pass. The cost is 32 × 33 × 4 − 32 × 32 × 4 = 128 bytes')])}
{steps('Workbook 11.3: 32 threads each store 32 powers', [
    'Layout A writes A[32i + p]: at each p the lanes are 32 words apart, a 32-way conflict.',
    '32 steps × 32 passes = 1024 passes.',
    'Layout B writes B[32p + i]: lanes 1 word apart, 1 pass per step.',
    eq('32 passes, 32 times faster')])}
{cu('powers.cu', POWERS, {9: 'Layout A: thread i owns a row of 32 values, so at one moment all lanes write column p: same bank.', 10: 'Layout B: the 32 lanes write one row together: 32 different banks.', 12: 'Both tiles must be complete before they are copied out.', 13: 'Copy out with consecutive lanes on consecutive words, which is also coalesced in global memory.'})}
{deep('8 byte values', '<p>A double covers two banks. Under the plain 32-bit model, lane t reading double t touches words 2t and 2t + 1, so 16 lanes fill the 32 banks and the warp needs 2 passes. Recent GPUs serve 64-bit accesses in two half warp phases, which gives the same 2 passes without any extra waiting.</p>')}
''', kw=['padding', '[32][33]', 'layout', 'powers example', 'doubles', 'transpose tile'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Shared memory is a fast shelf for a team. It has 32 doors. Spread the team over the doors, or let everyone read the same thing.</p>',
    '<p>bank = word mod 32, conflict = gcd(stride, 32). Pad 2-D tiles to an odd width. __syncthreads() between writing and reading a tile.</p>',
    '<p>Shared memory and L1 share one SRAM per SM. You can ask for a bigger shared carve out with cudaFuncSetAttribute and cudaFuncAttributePreferredSharedMemoryCarveout. More shared memory per block lowers occupancy (chapter 2.4).</p>',
    '<p>Swizzled layouts (XOR of row and column bits) avoid conflicts without wasting padding. CUTLASS and the Hopper TMA use them for matrix tiles.</p>')}
''', kw=['ladder', 'carve out', 'swizzle', 'CUTLASS'])

K.quiz('e', 'Shared memory is declared with', ['__global__', '__shared__', '__device__', 'cudaMalloc'], 1, 'Keyword.', '__shared__.')
K.quiz('e', 'How many banks does shared memory have?', ['16', '32', '64', '128'], 1, 'One per lane.', '32 banks of 4 bytes.')
K.quiz('e', 'Why call __syncthreads() after loading a tile?', ['To free memory', 'So no thread reads before all threads have written', 'To speed up loads', 'To launch a kernel'], 1,
       'Barrier.', 'Threads of a block run at different speeds.')
K.quiz('m', 'Bank of byte address 260', ['0', '1', '4', '65'], 1, '260 ÷ 4 = 65.', '65 mod 32 = 1.')
K.quiz('m', 'Stride 8 words. Conflict?', ['None', '2-way', '4-way', '8-way'], 3, 'gcd(8, 32).', '8 lanes per bank.')
K.quiz('m', 'All 32 lanes read A[5]', ['32-way conflict', 'No conflict (broadcast)', '2-way', 'Error'], 1, 'Same word.', 'Broadcast.')
K.quiz('m', 'Stride 6 words. Conflict?', ['None', '2-way', '3-way', '6-way'], 1, 'gcd(6, 32).', '2-way.')
K.quiz('h', 'Tile width 48 floats, threads read a column. Conflict and fix?', ['None', '16-way, pad to 49', '48-way, pad to 64', '2-way, no fix'], 1,
       'gcd(48, 32) = 16.', 'An odd width such as 49 removes it.')
K.quiz('h', 'extern __shared__ float buf[] gets its size from', ['The compiler', 'The third launch parameter in bytes', 'blockDim', 'cudaMalloc'], 1,
       'Dynamic.', '<<<grid, block, bytes>>>.')
K.quiz('h', 'Thread t reads double t under the 32-bit bank model', ['No conflict', '2-way', '4-way', '32-way'], 1,
       'Two words per lane.', '64 words over 32 banks.')
K.quiz('x', 'Layout A in the powers example takes how many passes for 32 steps?', ['32', '64', '256', '1024'], 3, '32-way each step.', '32 × 32.')
K.quiz('x', 'Stride 24 words for 32 steps. Total passes?', ['32', '128', '256', '768'], 2, 'gcd(24, 32) = 8.', '8 × 32 = 256.')

K.calc('e', 'Bank of word 70?', '6', '70 mod 32.',
       ['70 = 2 × 32 + 6.', 'Remainder 6.', eq('Bank 6')], check=70 % 32)
K.calc('e', 'Shared memory for a 32 × 32 float tile in bytes?', '4096', '1024 × 4.',
       ['32 × 32 = 1024 floats.', '× 4 bytes.', eq('4096 bytes')], check=4096)
K.calc('e', 'Stride 2 conflict (ways)?', '2', 'gcd.',
       ['gcd(2, 32) = 2.', 'Lanes 0 and 16 share bank 0.', eq('2-way')], check=2)
K.calc('m', 'Bytes for a padded 32 × 33 float tile?', '4224', '32 × 33 × 4.',
       ['1056 floats.', '× 4.', eq('4224 bytes, 128 more')], check=32 * 33 * 4)
K.calc('m', 'Row width 48, column read. Ways?', '16', 'gcd(48, 32).',
       ['Element [t][0] = word 48t.', 'gcd(48, 32) = 16.', eq('16-way')], check=16)
K.calc('m', '16 threads write out[16i]. Ways?', '8', 'Banks 0 and 16 only.',
       ['Words 0, 16, 32, 48, ...', 'Banks alternate 0, 16, 0, 16.', eq('8 lanes per bank: 8-way')], check=8)
K.calc('m', 'Stride 33 words. Ways?', '1', 'gcd(33, 32).',
       ['33 is odd.', 'gcd = 1.', eq('Conflict free')], check=1)
K.calc('h', 'Powers example layout A: total passes?', '1024', '32 steps × 32 ways.',
       ['Each step: lanes 32 words apart, 32-way.', '32 steps.', eq('1024 passes')], check=1024)
K.calc('h', 'Stride 24 for 32 steps: total passes?', '256', 'gcd(24, 32) × 32.',
       ['gcd(24, 32) = 8.', '8 × 32.', eq('256 passes')], check=256)
K.calc('x', 'A block uses a 64 × 65 float tile and an A100 SM offers 164 KB of shared memory (plus 1 KB reserved per block). Blocks by shared memory?', '9', 'Bytes per block first.',
       ['64 × 65 × 4 = 16,640 bytes.', '+ 1024 reserved = 17,664.', eq('167,936 ÷ 17,664 = 9.5, so 9 blocks')], check=167936 // (64 * 65 * 4 + 1024))
K.calc('x', 'Reverse 1024 ints with 256 thread blocks as in reverse.cu. Value at h[256] afterwards?', '511', 'Block 1 reverses 256 to 511.',
       ['Block 1 holds elements 256 to 511.', 'Position 256 is thread 0, which reads s[255] = 511.', eq('511')], check=511)

K.assign('bankw', 'e', 'Conflict degree',
         '<p>Write <code>ways(words)</code>: given the word index each lane reads, return the largest number of <b>different</b> words that fall in one bank (32 banks).</p>',
         '''
def ways(words):
    # your code here
    pass
''', [("ways(list(range(32)))", 1), ("ways([2 * t for t in range(32)])", 2), ("ways([5] * 32)", 1), ("ways([32 * t for t in range(32)])", 32)],
         '''
def ways(words):
    banks = {}
    for w in words:
        banks.setdefault(w % 32, set()).add(w)
    return max(len(v) for v in banks.values())
''', 'Use a set per bank so a broadcast counts once.', '<p>The set makes the broadcast case count as one word.</p>')
K.assign('pad', 'm', 'Smallest conflict free padding',
         '<p>Write <code>pad(width)</code>: the smallest padded width ≥ <code>width</code> such that reading a column (thread t reads word t × padded width, t = 0 to 31) has no bank conflict.</p>',
         '''
def pad(width):
    # your code here
    pass
''', [("pad(32)", 33), ("pad(48)", 49), ("pad(33)", 33), ("pad(64)", 65)],
         '''
from math import gcd
def pad(width):
    w = width
    while gcd(w, 32) != 1:
        w += 1
    return w
''', 'Conflict free means gcd(width, 32) = 1.', '<p>Any odd width works, so at most one extra column is needed.</p>')

K.must('Shared memory', '__shared__, one copy per block, fill then __syncthreads() then read. extern __shared__ size is the third launch value.')
K.must('Banks', '32 banks × 4 bytes. bank = ⌊byte ÷ 4⌋ mod 32. Different words in one bank take turns.')
K.must('Conflicts', 'Stride s gives gcd(s, 32) ways. Same word is a broadcast, no conflict.')
K.must('Padding', 'Tile [32][33] makes column reads conflict free for 128 extra bytes.')
K.must('Layout', 'Let lanes write consecutive words: powers example 1024 passes against 32.')

T = K.topic(
    slug='shared-memory', topic='shared-memory', step=(3, 'GPU memory', 'gpu-memory', 'Learn where data lives, how a warp reads global memory in sectors, and how shared memory banks work.', 'College'),
    title='Shared memory and bank conflicts', short='Shared memory', badge='3.3', minutes=45,
    lead='Use shared memory as a fast scratch pad for a block, and learn how its 32 banks work, when lanes must wait for each other, and how padding fixes it.',
    desc='__shared__ and __syncthreads, dynamic shared memory, 32 banks, bank of an address, gcd rule for strides, broadcast, padding tiles to 33, output layout of the powers example and 64-bit accesses.',
    summary='Shared memory use, barriers, 32 banks, gcd conflict rule, broadcast, padding and layout.',
    keywords=['shared memory', 'banks', 'bank conflict', 'padding', '__syncthreads'],
    recap='<p>Shared memory is fast only when the lanes of a warp hit different banks or the same word. Odd strides and padded tiles keep it conflict free.</p>')
