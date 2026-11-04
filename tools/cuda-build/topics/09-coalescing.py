# Chapter 3.2: Coalescing global memory. Source: lecture 7 and 8 (memory coalescing, sectors per warp read, row
# against column walks), lecture 11 (stride benchmark on a T4, 206 GB/s at stride 1, the sector model), workbook 7.2
# and 11.1, Quiz 1 question 5 (the transposed store into B) and Rakesh's worked solution.
# Beyond the lecture: array of structures against structure of arrays, float4 vector loads, and the shared memory
# transpose as the standard fix.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq
from cudakit import cu

K = Kit()

STRIDE = r'''
#include <cstdio>

__global__ void copyStride(float *out, const float *in, int n, int s) {
    int i = (blockIdx.x * blockDim.x + threadIdx.x) * s;   // thread t touches element t * s
    if (i < n) out[i] = in[i];
}

int main() {
    const int n = 1 << 24;
    float *in, *out;
    cudaMalloc(&in, n * sizeof(float));
    cudaMalloc(&out, n * sizeof(float));
    cudaEvent_t a, b;
    cudaEventCreate(&a); cudaEventCreate(&b);
    for (int s = 1; s <= 32; s *= 2) {
        int threads = n / s;
        cudaEventRecord(a);
        copyStride<<<(threads + 255) / 256, 256>>>(out, in, n, s);
        cudaEventRecord(b); cudaEventSynchronize(b);
        float ms; cudaEventElapsedTime(&ms, a, b);
        double useful = 2.0 * threads * sizeof(float);       // one read and one write per thread
        printf("stride %2d: %7.1f GB/s useful\n", s, useful / ms / 1e6);
    }
    cudaFree(in); cudaFree(out);
    return 0;
}
'''

AOS = r'''
struct ParticleAoS { float x, y, z, mass; };        // array of structures: 16 bytes per particle

struct ParticlesSoA { float *x, *y, *z, *mass; };   // structure of arrays: one array per field

__global__ void moveAoS(ParticleAoS *p, float dx, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) p[i].x += dx;                        // lanes read floats 16 bytes apart: stride 4
}

__global__ void moveSoA(ParticlesSoA p, float dx, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) p.x[i] += dx;                        // lanes read neighbouring floats: stride 1
}
'''

TRANSPOSE = r'''
#define TILE 32

// Naive: reads are coalesced, writes jump by n floats (like Quiz 1 question 5)
__global__ void transposeNaive(float *out, const float *in, int n) {
    int x = blockIdx.x * TILE + threadIdx.x;
    int y = blockIdx.y * TILE + threadIdx.y;
    if (x < n && y < n) out[x * n + y] = in[y * n + x];
}

// Through shared memory: both the read and the write walk along rows
__global__ void transposeShared(float *out, const float *in, int n) {
    __shared__ float tile[TILE][TILE + 1];          // +1 avoids bank conflicts (chapter 3.3)
    int x = blockIdx.x * TILE + threadIdx.x;
    int y = blockIdx.y * TILE + threadIdx.y;
    if (x < n && y < n) tile[threadIdx.y][threadIdx.x] = in[y * n + x];
    __syncthreads();
    x = blockIdx.y * TILE + threadIdx.x;            // swap the block coordinates
    y = blockIdx.x * TILE + threadIdx.y;
    if (x < n && y < n) out[y * n + x] = tile[threadIdx.x][threadIdx.y];
}
'''

K.code('sectors', r'''
# Sectors touched by one warp: thread t reads elem bytes at offset + t*stride*elem
def warp_read(stride, elem=4, offset=0):
    first = {(offset + t * stride * elem) // 32 for t in range(32)}
    last = {(offset + t * stride * elem + elem - 1) // 32 for t in range(32)}
    n = len(first | last)
    return n, round(100 * 32 * elem / (32 * n), 1)
for s in [1, 2, 8, 32]:
    print("stride", s, "->", warp_read(s))
print("16 byte offset ->", warp_read(1, 4, 16))
''')

K.lesson('sectors', 'Memory hands out 32 byte boxes', f'''
<p>DRAM does not deliver single floats. It delivers <b>sectors</b> of 32 bytes (8 floats). When the 32 threads of a warp issue a load, the hardware collects all their addresses and fetches the smallest set of sectors that covers them. This is called <b>coalescing</b>.</p>
{fxs(
    fx('Bytes the warp wants', 'useful = 32 × element size', 'Floats: 128 bytes. Doubles: 256 bytes.', key=True),
    fx('Efficiency', 'efficiency = useful bytes ÷ (sectors × 32)', 'Stride 1 floats: 128 ÷ (4 × 32) = 100 percent.', key=True),
    fx('Sectors for stride s (floats, aligned)', 'sectors = min(32, 4 × s)', 'Each thread lands in its own sector once s ≥ 8.'))}
{viz('coalesce')}
{code('sectors')}
{scene('buying sweets', '<p>Buying one sweet from each of 32 different shops costs 32 trips. Buying 32 sweets from one shop costs one trip. Neighbouring threads should read neighbouring addresses so the warp visits as few shops as possible.</p>')}
''', kw=['coalescing', 'sector', '32 bytes', 'efficiency', 'stride', 'misaligned'])

K.lesson('rowcol', 'Rows, columns and Quiz 1 question 5', f'''
<p>In C, a 2-D array is stored row by row (row major). Element [y][x] sits at position y × width + x. Consecutive threads should vary <b>x</b>, the fast moving index.</p>
{table(['Thread t reads', 'Neighbouring lanes are', 'Sectors per warp read (floats)'], [
    ['A[row][t] (along a row)', '4 bytes apart', '4 (100 percent)'],
    ['A[t][col] (down a column of width 1024)', '4096 bytes apart', '32 (12.5 percent)']])}
{steps('Quiz 1 question 5: the store B[x × height + y]', [
    'blockDim.x = 32, so a warp holds 32 consecutive x values and one y.',
    'Lane x writes B[x × 2048 + y]. Neighbouring lanes are 2048 floats = 8192 bytes apart.',
    'Every lane falls in a different 128 byte segment.',
    eq('32 segments for the store (the load from A uses only 1)')])}
{cu('transpose.cu', TRANSPOSE, {4: 'This is the Quiz 1 question 5 pattern: the read is along a row, the write goes down a column.', 7: 'out[x × n + y]: lanes with consecutive x write n floats apart, so every lane needs its own segment.', 12: 'The tile is 33 floats wide. Chapter 3.3 explains why the extra column matters.', 15: 'Step 1: read a 32 × 32 tile along rows (coalesced) into shared memory.', 16: 'Every thread must finish writing the tile before anyone reads it back.', 17: 'Swap the block coordinates, because the output tile sits in the mirrored position.', 19: 'Step 2: write along rows again, reading the tile by column from fast shared memory.'})}
''', kw=['row major', 'column walk', 'Quiz 1 question 5', 'segments', 'transpose', 'shared memory transpose'])

K.lesson('stride', 'The stride benchmark (lecture 11)', f'''
<p>The lecture measured a copy kernel on a T4 while making threads read further and further apart. At stride 1 it reached 206 GB/s, about 64 percent of the T4\'s 320 GB/s data sheet value.</p>
{fxs(fx('Sector model', 'useful bandwidth ≈ (stride 1 bandwidth) ÷ min(s, 8)', 'Once threads are 8 floats apart each lane needs its own sector, and the model stops falling. Real GPUs fall further at big strides because of DRAM page and TLB effects.', key=True))}
{table(['Stride', 'Model (GB/s)', 'Sectors per warp read'], [['1', '206', '4'], ['2', '103', '8'], ['4', '51.5', '16'], ['8', '25.75', '32'], ['16', '25.75', '32'], ['32', '25.75', '32']])}
{cu('stride_copy.cu', STRIDE, {5: 'Thread t copies element t × s, so neighbouring lanes are s floats apart.', 18: 'For bigger strides we launch fewer threads, so each run copies n ÷ s elements.', 22: 'Useful bytes are one read and one write of 4 bytes per thread. Wasted sector bytes are not counted.'}, out='(on a T4 the lecture measured 206 GB/s at stride 1, falling as the stride grows)')}
''', kw=['stride benchmark', 'T4', '206 GB/s', 'sector model', 'useful bandwidth'])

K.lesson('layout', 'Data layout: AoS against SoA, and wider loads', f'''
{cu('particles.cu', AOS, {1: 'Array of structures: x, y, z and mass of one particle sit together, 16 bytes per particle.', 3: 'Structure of arrays: all x values together, then all y values and so on.', 7: 'Reading only p[i].x makes lanes 16 bytes apart, so 3 of every 4 bytes fetched are wasted.', 12: 'Now lane i reads x[i]: a perfect stride 1 read.'})}
{fxs(fx('Vector loads', 'float4: 32 lanes × 16 bytes = 512 bytes = 16 sectors, 100 percent', 'One instruction moves four floats per thread, so fewer instructions for the same bytes. The address must be 16 byte aligned.'))}
{note('AoS is natural for the CPU and often slow on the GPU. When kernels touch only some fields, store each field in its own array.', 'tip')}
{deep('L1 caching and 128 byte lines', '<p>L1 and L2 track data in 128 byte lines made of four 32 byte sectors. Older GPUs (Fermi, Kepler) moved whole 128 byte lines on an L1 miss, so a scattered warp could move 32 × 128 = 4096 bytes. Modern GPUs fetch only the sectors that are needed, which is why the course counts sectors.</p>')}
''', kw=['AoS', 'SoA', 'float4', 'vector loads', 'alignment', 'cache line', '128 bytes'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Neighbouring threads should read neighbouring addresses. Then one delivery covers the whole warp.</p>',
    '<p>Sectors are 32 bytes. Efficiency = 32 × element size ÷ (sectors × 32). Stride s floats needs min(32, 4s) sectors. Row major: let threadIdx.x move along the row.</p>',
    '<p>Misaligned starts cost one extra sector. AoS to SoA turns stride 4 into stride 1. Transposes and column walks are fixed by staging a tile in shared memory. Nsight Compute reports "sectors per request" to check this.</p>',
    '<p>Hopper\'s TMA loads whole multi dimensional tiles with a single descriptor and handles strides and edges in hardware, which is how FlashAttention 3 keeps memory busy.</p>')}
''', kw=['ladder', 'sectors per request', 'TMA'])

K.quiz('e', 'A sector is', ['4 bytes', '32 bytes', '128 bytes', '1 KB'], 1, 'Delivery box.', 'DRAM moves data in 32 byte sectors.')
K.quiz('e', 'A warp reads 32 neighbouring floats. Sectors?', ['1', '4', '8', '32'], 1, '128 ÷ 32.', '4 sectors, 100 percent.')
K.quiz('e', 'Row major means', ['Columns are stored together', 'Each row is stored in one piece, row after row', 'Random order', 'Only for square matrices'], 1,
       'C arrays.', 'Element [y][x] is at y × width + x.')
K.quiz('m', 'Stride 2 floats. Efficiency?', ['100 percent', '50 percent', '25 percent', '12.5 percent'], 1, '8 sectors.', '128 ÷ 256.')
K.quiz('m', 'Stride 32 floats. Efficiency?', ['50 percent', '25 percent', '12.5 percent', '3 percent'], 2, '32 sectors.', '128 ÷ 1024.')
K.quiz('m', 'Quiz 1 question 5: segments touched by the store into B', ['1', '4', '16', '32'], 3,
       'Lanes 2048 floats apart.', 'Each lane needs its own 128 byte segment.')
K.quiz('m', 'Which layout makes reading only the x field coalesced?', ['Array of structures', 'Structure of arrays', 'Linked list', 'Both'], 1,
       'One array per field.', 'SoA puts all x values next to each other.')
K.quiz('h', 'Stride 1 floats starting 16 bytes into a sector. Sectors and efficiency?', ['4, 100 percent', '5, 80 percent', '8, 50 percent', '4, 80 percent'], 1,
       'One extra sector.', 'Bytes 16 to 143 touch sectors 0 to 4.')
K.quiz('h', 'The sector model predicts stride 16 on a T4 as', ['12.9 GB/s', '25.75 GB/s', '103 GB/s', '206 GB/s'], 1,
       'min(16, 8) = 8.', '206 ÷ 8.')
K.quiz('h', 'A shared memory transpose fixes the naive transpose because', ['Shared memory is bigger', 'Both global read and global write become row walks', 'It uses fewer threads', 'It avoids __syncthreads'], 1,
       'Change the walk.', 'The column walk happens in fast shared memory instead.')
K.quiz('x', 'Each thread loads one float4 (16 bytes), lanes adjacent. Sectors and efficiency?', ['4, 100 percent', '16, 100 percent', '32, 50 percent', '16, 50 percent'], 1,
       '512 bytes.', '512 ÷ 32 = 16 sectors, all used.')
K.quiz('x', 'Thread t walks down column t of a 1024 × 1024 float matrix. Per warp read, sectors?', ['1', '4', '32', '1024'], 1,
       'At one step lanes read row r, columns t.', 'At each step the 32 lanes read 32 neighbouring columns of one row: 4 sectors. Walking down a column per thread is coalesced across the warp.')

K.calc('e', 'Doubles, stride 1. Sectors per warp read?', '8', '32 × 8 bytes.',
       ['Useful 256 bytes.', '256 ÷ 32.', eq('8 sectors, 100 percent')], check=8)
K.calc('e', '206 GB/s is what percent of 320 GB/s? (one decimal)', '64.4', 'Divide.',
       ['206 ÷ 320 = 0.6438.', '× 100.', eq('64.4 percent')], check=100 * 206 / 320, tol=0.05)
K.calc('e', 'Sector model: stride 4 on the T4 (GB/s)?', '51.5', '206 ÷ 4.',
       ['min(4, 8) = 4.', '206 ÷ 4.', eq('51.5 GB/s')], check=206 / 4)
K.calc('m', 'Stride 4 floats. Efficiency in percent?', '25', '16 sectors.',
       ['Lanes 16 bytes apart: 2 per sector.', '32 ÷ 2 = 16 sectors = 512 bytes.', eq('128 ÷ 512 = 25 percent')], check=25)
K.calc('m', 'Read 256 MB (10⁶ bytes) at 25.75 GB/s. Time in ms? (two decimals)', '9.94', 'bytes ÷ bandwidth.',
       ['256 × 10⁶ ÷ 25.75 × 10⁹.', '= 0.009942 s.', eq('9.94 ms (1.24 ms at 206 GB/s)')], check=1000 * 256e6 / 25.75e9, tol=0.005)
K.calc('m', 'AoS with 16 byte particles, kernel reads only x. Efficiency in percent?', '25', 'Like stride 4.',
       ['Lanes 16 bytes apart.', '4 useful bytes of every 16 fetched.', eq('25 percent')], check=25)
K.calc('m', 'float4 loads by 32 adjacent lanes: sectors?', '16', '512 ÷ 32.',
       ['32 × 16 = 512 bytes.', '÷ 32.', eq('16 sectors, 100 percent')], check=16)
K.calc('h', '1024 × 1024 floats. Thread t walks row t (each thread its own row). Sectors per warp read?', '32', 'At one step lanes are 4096 bytes apart.',
       ['Lane t reads A[t][k]: address t × 4096 + 4k.', 'Every lane is in a different sector.', eq('32 sectors (4 if threads walked columns)')], check=32)
K.calc('h', 'That row walk reads the whole 4 MB matrix. Total bytes moved in MB, with 32 byte sectors per 4 useful bytes?', '32', '8 times the useful bytes.',
       ['Each 4 useful bytes cost a 32 byte sector (if nothing stays cached).', '4 MB × 8.', eq('32 MB moved (4 MB for the column walk)')], check=4 * 8)
K.calc('x', 'Quiz 1 question 5: bytes moved by one warp\'s store into B with 32 byte sectors?', '1024', '32 lanes, one sector each.',
       ['Each lane is 8192 bytes from the next.', '32 sectors × 32 bytes.', eq('1024 bytes moved for 128 useful, 12.5 percent')], check=32 * 32)
K.calc('x', 'Doubles with stride 2. Sectors and efficiency in percent?', '50', '16 bytes between lanes.',
       ['Lanes 16 bytes apart: 2 per sector, 16 sectors.', 'Useful 256 bytes of 512.', eq('50 percent')], check=50)

K.assign('sect', 'm', 'Sector counter',
         '<p>Write <code>sectors(stride, elem, offset)</code>: the number of distinct 32 byte sectors touched when thread t (0 to 31) reads <code>elem</code> bytes at byte address <code>offset + t * stride * elem</code>.</p>',
         '''
def sectors(stride, elem, offset):
    # your code here
    pass
''', [("sectors(1, 4, 0)", 4), ("sectors(32, 4, 0)", 32), ("sectors(1, 4, 16)", 5), ("sectors(2, 8, 0)", 16), ("sectors(1, 16, 0)", 16)],
         '''
def sectors(stride, elem, offset):
    seen = set()
    for t in range(32):
        a = offset + t * stride * elem
        seen.add(a // 32)
        seen.add((a + elem - 1) // 32)
    return len(seen)
''', 'An element can span two sectors, so add the first and last byte.', '<p>Elements up to 16 bytes that are aligned never cross a sector boundary, so the first and last byte are enough.</p>')
K.assign('segq5', 'h', 'Segments for a 2-D store',
         '<p>Write <code>segments(width, height, y)</code> for the Quiz 1 question 5 store: lanes x = 0 to 31 write <code>B[x * height + y]</code> (floats). Return the number of distinct 128 byte segments.</p>',
         '''
def segments(width, height, y):
    # your code here
    pass
''', [("segments(2048, 2048, 0)", 32), ("segments(2048, 1, 0)", 1), ("segments(2048, 8, 3)", 8), ("segments(2048, 16, 0)", 16)],
         '''
def segments(width, height, y):
    return len({(x * height + y) * 4 // 128 for x in range(32)})
''', 'Address in bytes is index × 4.', '<p>With height 1 the store is along a row again and needs one segment.</p>')

K.must('Sectors', 'Warp loads are coalesced into 32 byte sectors. Efficiency = 32 × element ÷ (sectors × 32).')
K.must('Strides', 'Floats: stride 1 → 4 sectors, 2 → 8, 4 → 16, ≥ 8 → 32. Misaligned start adds a sector.')
K.must('Row major', 'Let threadIdx.x move along the row. Q5 store B[x·h + y] touches 32 segments.')
K.must('Sector model', 'Useful bandwidth ≈ stride 1 bandwidth ÷ min(s, 8). T4 206 GB/s at stride 1.')
K.must('Fixes', 'SoA instead of AoS, float4 loads, and shared memory tiles for transposes.')

T = K.topic(
    slug='coalescing', topic='coalescing', step=(3, 'GPU memory', 'gpu-memory', 'Learn where data lives, how a warp reads global memory in sectors, and how shared memory banks work.', 'College'),
    title='Coalescing: reading global memory well', short='Coalescing', badge='3.2', minutes=45,
    lead='See how a warp\'s 32 loads are merged into 32 byte sectors, why strides and column walks waste bandwidth, and how to lay out data so every byte fetched is used.',
    desc='Sectors and coalescing, efficiency for strides and misalignment, row major walks, Quiz 1 question 5, the stride benchmark and sector model, AoS against SoA, float4 loads and the shared memory transpose.',
    summary='Sectors per warp read, stride and alignment, Quiz 1 Q5, sector model, AoS and SoA, transposes.',
    keywords=['coalescing', 'sectors', 'stride', 'row major', 'SoA', 'transpose'],
    recap='<p>A warp reads in 32 byte sectors. Neighbouring lanes must read neighbouring addresses, otherwise most of each sector is wasted.</p>')
