# Chapter 1.1: why GPUs exist. Source: lecture 1 (design philosophy, CPU vs GPU, latency vs throughput, the gardener
# analogy, clock frequency and power, CPU and GPU memory hierarchy, the inference FPS study on CPU, T4 GPU and custom
# hardware, the hardware spectrum CPU GPU FPGA ASIC, TPU and NPU questions) and workbook sections 1.1 and 1.2.
# Beyond the lecture: the power wall (end of Dennard scaling) and SIMD against SIMT naming, from the CUDA guide.
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('peaks', r'''
# Peak FLOP/s = FLOPs per tick per core x ticks per second x cores
def peak(cores, ghz, flops_per_tick):
    return cores * ghz * 1e9 * flops_per_tick

chips = [("CPU, 8 cores", 8, 2.0, 16),
         ("GPU, 2048 cores", 2048, 0.8, 2),
         ("NVIDIA T4", 40 * 64, 1.59, 2),
         ("NVIDIA A100 FP32", 108 * 64, 1.41, 2)]
for name, cores, ghz, f in chips:
    p = peak(cores, ghz, f)
    print(f"{name:18s} {p / 1e9:10.1f} GFLOP/s")
print("GPU / CPU =", peak(2048, 0.8, 2) / peak(8, 2.0, 16))
''')

K.code('pile', r'''
# How long does a pile of N jobs take? The CPU does 1 at a time, the GPU does C per round.
import math
def cpu_time(n, ms):
    return n * ms
def gpu_time(n, c, ms_round):
    rounds = math.ceil(n / c)      # a part full round still costs a whole round
    return rounds * ms_round

for n in [1, 8, 9, 256, 1024]:
    c, g = cpu_time(n, 5), gpu_time(n, 256, 40)
    winner = "GPU" if g < c else ("tie" if g == c else "CPU")
    print(f"n={n:5d}  CPU {c:6d} ms  GPU {g:4d} ms  -> {winner}")
''')

K.lesson('designs', 'Two ways to build a processor', f'''
<p>A computer chip can spend its area on two kinds of things. It can spend it on <b>clever control</b> and <b>big caches</b>, so that each instruction finishes as soon as possible. Or it can spend it on <b>many small arithmetic units</b>, so that a huge number of simple instructions finish together. The first choice gives a CPU. The second gives a GPU.</p>
{table(['Part of the chip', 'CPU', 'GPU'], [
    ['Control logic (decides what runs next)', 'Large and clever: branch prediction, out of order execution', 'Small and simple, shared by a group of threads'],
    ['Cache (fast memory on the chip)', 'Large per core', 'Small per core, plus a shared L2'],
    ['ALUs (the units that add and multiply)', 'A few, powerful', 'Thousands, small and energy efficient'],
    ['Clock', 'High, about 2 to 5 GHz', 'Moderate, about 0.8 to 2 GHz'],
    ['Built for', 'Low latency: one task, fast', 'High throughput: many tasks per second']])}
{scene('the school bus and the race car', '<p>A race car takes one child to school in 5 minutes. A bus takes 20 minutes but carries 50 children. For one child the car wins. For a whole school the bus wins by a mile. A CPU is the race car. A GPU is a fleet of buses. Neither is "faster" in general. It depends on whether you move one child or a thousand.</p>')}
{scene('the gardener (from the lecture)', '<p>One 25 year old gardener picks up any single leaf faster than a 10 year old. But leaves are scattered everywhere, and 25 children can each grab a different leaf at the same moment. The children clear the garden first. Each child is slower, the team is faster. That is a GPU.</p>')}
{viz('race')}
{note('GPU does not mean "always faster". A GPU wins only when there is enough independent work to keep thousands of small units busy. For a single small task the CPU usually wins.', 'warn')}
<p>Teachers in the class asked if a GPU is SIMD and a CPU is SISD. Broadly yes. SISD means a single instruction works on a single piece of data. SIMD means one instruction works on many pieces of data at once. NVIDIA calls its version <b>SIMT</b>, single instruction multiple threads: 32 threads (a warp) run the same instruction together, but each thread has its own registers and can take its own branch. Chapter 2.3 shows this in detail.</p>
''', kw=['CPU vs GPU', 'design philosophy', 'control', 'cache', 'ALU', 'gardener analogy', 'SIMD', 'SIMT'])

K.lesson('latency', 'Latency, throughput and frames per second', f'''
{fxs(
    fx('Latency and throughput', 'Latency = time to finish ONE job<br>Throughput = jobs finished ÷ time taken', 'A CPU is built for low latency. A GPU is built for high throughput.', key=True),
    fx('Frames per second', 'FPS = 1000 ÷ (ms per frame)<br>ms per frame = 1000 ÷ FPS', 'There are 1000 milliseconds in one second.'),
    fx('Time for a batch', '<i>T</i> = ⌈<i>N</i> ÷ <i>C</i>⌉ × (time per round)', 'N jobs, C jobs done together in one round. ⌈ ⌉ means round up, because a part full round still costs a whole round.', key=True),
    fx('Pipeline', 'latency = sum of stage times<br>throughput = 1 ÷ (slowest stage)', 'Once the line is full, one result comes out every time the slowest stage finishes.'))}
{steps('Worked example from the workbook: who clears 1000 images first?', [
    'CPU: 10 ms per image, one at a time. GPU: 15 ms per round, 1000 images per round.',
    'One image: CPU 10 ms, GPU 15 ms. The CPU has lower latency.',
    'Pile of 1000: CPU needs 1000 × 10 = 10,000 ms = 10 s.',
    'GPU needs ⌈1000 ÷ 1000⌉ = 1 round = 15 ms.',
    'Throughput: CPU 1000 ÷ 10 = 100 images per second. GPU 1000 ÷ 0.015 ≈ 66,667 images per second.',
    eq('The GPU has about 667 times the throughput, even though each image takes longer')])}
{code('pile')}
{scene('a toll plaza on a highway', '<p>One toll booth with a very fast operator still makes a long queue at rush hour. Twenty booths with slower operators clear the queue far sooner. Each car still waits about as long at its own booth, so latency per car does not drop, but cars per minute go up twenty times.</p>')}
<p><b>The inference study in the lecture.</b> Ten small models were timed on an Intel Xeon CPU, an NVIDIA T4 GPU and a custom circuit on an FPGA board. Model M1 (three convolution layers) ran at 13.39 FPS on the CPU, 15.07 on the GPU and 1464.05 on custom hardware. The GPU gain was only about 1.13 times because M1 is tiny and the T4 had too little parallel work. Custom hardware has no instruction fetch or decode at all, which is why it won by about 97 times. The tailor analogy from class: ready made clothes (CPU, GPU) fit everyone, a tailored suit (custom hardware) fits one person perfectly.</p>
''', kw=['latency', 'throughput', 'FPS', 'batch time', 'ceiling', 'pipeline', 'inference FPS'])

K.lesson('clock', 'Clock speed, power and peak work', f'''
{fxs(
    fx('Cycle time', '<i>t</i><sub>cycle</sub> = 1 ÷ <i>f</i>', '1 GHz = 10⁹ ticks per second, so one tick lasts 1 ns. At 800 MHz a tick lasts 1.25 ns.'),
    fx('Dynamic power', '<i>P</i><sub>dyn</sub> ∝ α · <i>C</i> · <i>V</i>² · <i>f</i>', 'α is how often the circuit switches, C its capacitance, V the voltage (squared), f the clock. A faster clock needs a higher voltage, so power grows much faster than speed.', key=True),
    fx('Peak work per second', 'peak = (FLOPs per tick per core) × <i>f</i> × cores', 'One FMA, a × b + c, counts as 2 FLOPs.', key=True))}
{viz('peak')}
{steps('Why GPUs add cores instead of chasing clock speed (workbook P1.2.3 and P1.2.4)', [
    'Running 20 percent faster needs about 10 percent more voltage.',
    'Power factor = 1.1² × 1.2 = 1.21 × 1.2 = 1.452. Power rises 45 percent for only 20 percent more speed.',
    'Now go the other way: halve both voltage and clock. One slow core uses (½)² × ½ = ⅛ of the power.',
    'So 8 slow cores fit in the power budget of 1 fast core.',
    eq('8 cores × ½ speed = 4 times the work for the same power, if the work can be split')])}
{code('peaks')}
{deep('the power wall', '<p>Until about 2005 every new chip shrank its transistors and lowered the voltage at the same time (Dennard scaling), so clocks rose for free. Below about 1 volt the transistors leak current, the voltage could not keep falling, and power per chip hit the limit a fan can cool (about 100 to 300 W). Clock speeds stopped near 3 to 5 GHz. Since then extra transistors have been spent on more cores. GPUs push this to the extreme.</p>')}
{note('Peak FLOP/s is a ceiling, not a promise. Real kernels usually reach a fraction of it, because they wait for memory. Chapter 4.2 (the roofline) shows how to predict that fraction.', 'tip')}
''', kw=['clock', 'cycle time', 'dynamic power', 'voltage', 'peak FLOPs', 'FMA', 'power wall', 'Dennard scaling'])

K.lesson('platforms', 'CPU, GPU, TPU, NPU, FPGA and ASIC', f'''
{table(['Platform', 'Strength', 'Weakness', 'Examples from the lecture'], [
    ['CPU', 'Most flexible, cheapest, runs any program', 'Limited parallelism', 'Arm Cortex-M, Raspberry Pi'],
    ['GPU', 'Massive parallelism, good programmability', 'Power hungry', 'NVIDIA Jetson, T4, A100, Arm Mali'],
    ['FPGA', 'Custom circuits, low latency, good work per watt, can be reprogrammed', 'Small on chip memory, needs hardware design skill', 'Xilinx Zynq, Intel Arria 10'],
    ['ASIC (TPU, NPU)', 'Lowest power, highest performance for one task', 'Very costly to design, long time to market, fixed', 'Google Edge TPU, Ascend 310']])}
<p>Moving from CPU to GPU to FPGA to ASIC trades flexibility for efficiency. TPU is Google\'s name for its own neural accelerator, and other makers call theirs an NPU. A smartwatch that checks your heartbeat the same way all day is a perfect job for a tiny NPU. A GPU is kept because its work keeps changing: a heat simulation today, image processing tomorrow, a language model next week.</p>
{fx('Host and device', 'Host = CPU (starts the program, owns the operating system)<br>Device = GPU (runs the parallel parts you send it)', 'Every GPU system is driven by a CPU. CUDA is the library and language extension that lets the host hand work to the device.')}
{note('A GPU never runs alone. The CPU boots the machine, runs the serial parts and launches GPU work. This is why the time to copy data between them matters so much (chapter 1.2).', 'exam')}
''', kw=['TPU', 'NPU', 'FPGA', 'ASIC', 'hardware spectrum', 'host', 'device', 'CUDA'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>A CPU is one very fast worker. A GPU is thousands of slower workers. If the job can be split into many small pieces that do not depend on each other, the many workers finish first.</p>',
    '<p>Latency is time per job, throughput is jobs per second. Peak = FLOPs per tick × clock × cores. Power ∝ V²f, so GPUs use many cores at a moderate clock. Use ⌈N ÷ C⌉ rounds for batch time.</p>',
    '<p>GPUs hide the long latency of each operation by keeping thousands of threads in flight and switching between them every cycle at no cost. The design only pays off when the program exposes enough parallelism, which Little\'s law turns into a number in chapter 2.3.</p>',
    '<p>Modern accelerators mix the ideas: GPUs gained tensor cores (fixed function matrix units), and research chips explore near memory and in memory computing, systolic arrays (the TPU) and dataflow designs. Picking hardware is now a question of matching arithmetic intensity, precision and memory bandwidth to the workload.</p>')}
{steps('Work it out: the T4 peak (workbook P1.2.5)', [
    'Cores = 40 SMs × 64 = 2560.',
    'FLOPs per tick = 2560 × 2 = 5120 (one FMA each).',
    'Per second = 5120 × 1.59 × 10⁹ = 8.1408 × 10¹².',
    eq('Peak ≈ 8.14 TFLOP/s, and the T4 data sheet says 8.1')])}
{deep('why the GPU took over deep learning', '<p>Training a neural network is mostly matrix multiplication, millions of identical multiply adds. That is exactly the kind of work a GPU was built for in graphics. In 2012 AlexNet was trained on two consumer GPUs, and since then GPU makers have added hardware for the exact number formats AI uses (chapter 8.1).</p>')}
''', kw=['ladder', 'T4 peak', 'deep learning', 'AlexNet', 'systolic array'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Latency means', ['Jobs finished per second', 'Time to finish one job', 'The number of cores', 'The clock speed'], 1,
       'One job.', 'Latency is the delay for a single task. Throughput is how many tasks finish per unit of time.')
K.quiz('e', 'A GPU is designed mainly for', ['Low latency', 'High throughput', 'Large caches per core', 'High clock speed'], 1,
       'Many jobs at once.', 'Thousands of simple ALUs finish many jobs per second, even though each job is not faster.')
K.quiz('e', 'A frame takes 8 ms. The frame rate is', ['80 FPS', '125 FPS', '8 FPS', '12.5 FPS'], 1,
       '1000 ÷ ms.', '1000 ÷ 8 = 125 frames per second.')
K.quiz('e', 'Which part of the chip takes most of the area in a GPU?', ['Control logic', 'Large caches', 'Many small ALUs', 'Branch predictors'], 2,
       'Green boxes on the slide.', 'The GPU spends its area on arithmetic units, the CPU on control and cache.')
K.quiz('m', 'Why do GPUs not simply raise their clock to 5 GHz?', ['It is illegal', 'Power grows with V²f, so heat would explode with thousands of cores', 'Memory cannot keep up at any clock', 'Warps need slow clocks'], 1,
       'Power formula.', 'A faster clock needs more voltage, and power grows with the square of voltage times the clock.')
K.quiz('m', 'One FMA (a × b + c) counts as', ['1 FLOP', '2 FLOPs', '3 FLOPs', '0.5 FLOP'], 1,
       'A multiply and an add.', 'It does one multiplication and one addition, so 2 floating point operations.')
K.quiz('m', 'In the inference study, M1 ran only 1.13 times faster on the T4 GPU than the CPU because', ['The GPU was broken', 'M1 is tiny and gave the GPU too little parallel work', 'CPUs are always faster', 'FPS cannot be compared'], 1,
       'Three conv layers.', 'A small model cannot fill thousands of cores, so fixed overheads dominate.')
K.quiz('m', 'Moving from CPU to GPU to FPGA to ASIC you gain', ['Flexibility', 'Efficiency for one task, and lose flexibility', 'Cheaper design cost', 'Larger caches'], 1,
       'The spectrum.', 'Specialisation buys efficiency at the price of generality and design cost.')
K.quiz('h', 'A 3 stage pipeline has stages of 4, 6 and 5 ms. Its steady throughput is', ['66.7 FPS', '166.7 FPS', '200 FPS', '250 FPS'], 1,
       'Slowest stage.', 'One frame leaves every 6 ms, so 1000 ÷ 6 ≈ 166.7 FPS. Latency is still 15 ms.')
K.quiz('h', 'Halving both voltage and clock of a core and filling the same power budget gives', ['2 cores, same work', '8 cores, 4 times the work', '4 cores, 2 times the work', '16 cores, 8 times the work'], 1,
       '(½)² × ½.', 'Each slow core uses ⅛ of the power, so 8 fit, each at half speed: 4 times the work.')
K.quiz('x', 'Which statement about SIMT is correct?', ['Each thread has its own instruction stream fetched separately', 'A warp of 32 threads shares one instruction stream, but each thread has its own registers and may branch', 'SIMT is the same as SISD', 'SIMT needs one ALU per warp'], 1,
       'NVIDIA\'s variant of SIMD.', 'Threads in a warp issue the same instruction together, yet keep private state and can diverge (chapter 6.1).')
K.quiz('x', 'Peak FLOP/s doubles if you double', ['Only the memory bandwidth', 'Cores, clock or FLOPs per tick per core (any one of them)', 'The cache size', 'The number of threads launched'], 1,
       'Look at the product.', 'Peak is a product of three factors. Memory and threads change achieved speed, not the peak.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'A video must play at 60 FPS. How many milliseconds does each frame get? (two decimals)', '16.67', '1000 ÷ FPS.',
       ['One second is 1000 ms.', 'Share it among 60 frames.', eq('1000 ÷ 60 ≈ 16.67 ms')], check=1000 / 60, tol=0.005, unit='ms')
K.calc('e', 'How long is one clock tick at 800 MHz, in nanoseconds?', '1.25', '1 ÷ f.',
       ['800 MHz = 800,000,000 ticks per second.', '1 ÷ 800,000,000 s = 0.00000000125 s.', eq('= 1.25 ns')], check=1e9 / 800e6, unit='ns')
K.calc('e', 'A CPU has 8 cores at 2 GHz, each doing 16 FLOPs per tick. Peak in GFLOP/s?', '256', 'Multiply the three factors.',
       ['Per tick for the chip: 16 × 8 = 128 FLOPs.', 'Times 2 × 10⁹ ticks per second = 256 × 10⁹.', eq('256 GFLOP/s')], check=8 * 2 * 16, unit='GFLOP/s')
K.calc('m', 'GPU: 1024 images in rounds of 256, 40 ms per round. Total time in ms?', '160', 'Rounds × time.',
       ['Rounds = ⌈1024 ÷ 256⌉ = 4.', 'Time = 4 × 40.', eq('160 ms')], check=-(-1024 // 256) * 40, unit='ms')
K.calc('m', 'Same GPU against a CPU at 5 ms per image. How many times higher is the GPU throughput on 1024 images?', '32', 'Compare times.',
       ['CPU: 1024 × 5 = 5120 ms.', 'GPU: 160 ms.', eq('5120 ÷ 160 = 32')], check=1024 * 5 / 160)
K.calc('m', 'CPU 5 ms per image, GPU always 40 ms for up to 256 images. Smallest pile where the GPU is strictly faster?', '9', 'Find the tie first.',
       ['Tie: 5N = 40, N = 8.', 'At N = 8 both take 40 ms.', eq('N = 9: CPU 45 ms &gt; GPU 40 ms')], check=9)
K.calc('m', 'Power rises with V²f. Clock +20 percent needs voltage +10 percent. New power as a factor of the old? (three decimals)', '1.452', 'Square the voltage factor.',
       ['Voltage factor squared: 1.1 × 1.1 = 1.21.', 'Times clock factor 1.2.', eq('1.21 × 1.2 = 1.452')], check=1.1 ** 2 * 1.2, tol=0.0005)
K.calc('h', 'NVIDIA T4: 40 SMs × 64 cores, one FMA per tick, 1.59 GHz. Peak in TFLOP/s? (two decimals)', '8.14', 'Count cores, × 2, × clock.',
       ['Cores 40 × 64 = 2560.', 'FLOPs per tick 2560 × 2 = 5120.', eq('5120 × 1.59 × 10⁹ = 8.14 × 10¹² FLOP/s')], check=2560 * 2 * 1.59e9 / 1e12, tol=0.005, unit='TFLOP/s')
K.calc('h', 'Pipeline with stages 4, 6 and 5 ms. Latency of one frame in ms?', '15', 'Add the stages.',
       ['A single frame visits every stage.', '4 + 6 + 5.', eq('15 ms (throughput is set by the 6 ms stage)')], check=15, unit='ms')
K.calc('h', 'Model M1: custom hardware 1464.05 FPS, GPU 15.07 FPS. Speedup of hardware over GPU? (one decimal)', '97.1', 'New FPS ÷ old FPS.',
       ['Bigger FPS is better.', '1464.05 ÷ 15.07.', eq('≈ 97.1 times')], check=1464.05 / 15.07, tol=0.05)
K.calc('x', 'A memory wait lasts 80 ticks. How long is it at 1.5 GHz, in ns? (two decimals)', '53.33', 'Ticks ÷ GHz.',
       ['One tick at 1.5 GHz lasts 1 ÷ 1.5 ns.', '80 ÷ 1.5.', eq('≈ 53.33 ns, while about 80 instructions of other warps could run')], check=80 / 1.5, tol=0.005, unit='ns')
K.calc('x', 'Design B halves voltage and clock of design A. How many times more work do the B cores that fit in A\'s power budget do?', '4', 'Power per B core then count.',
       ['Power of one B core: (½)² × ½ = ⅛.', 'Cores that fit: 8.', eq('8 × ½ = 4 times the work')], check=8 * 0.5)

# ---------------------------------------------------------------- assignments
K.assign('batch', 'e', 'Time to clear a pile of jobs',
         '<p>Write <code>gpu_time(n, c, ms_round)</code>: a GPU handles up to <code>c</code> jobs per round and each round takes <code>ms_round</code> ms. Return the total ms for <code>n</code> jobs. Remember that a part full round still costs a full round.</p>',
         '''
def gpu_time(n, c, ms_round):
    # your code here
    pass
''', [("gpu_time(1000, 1000, 15)", 15), ("gpu_time(1024, 256, 40)", 160), ("gpu_time(1025, 256, 40)", 200), ("gpu_time(1, 256, 40)", 40)],
         '''
def gpu_time(n, c, ms_round):
    rounds = (n + c - 1) // c
    return rounds * ms_round
''', 'Use (n + c − 1) // c to round up with whole numbers.', '<p>1025 jobs need 5 rounds of 256, so 200 ms. The last round is almost empty but costs the same.</p>')
K.assign('peakfn', 'm', 'Peak FLOP/s of a chip',
         '<p>Write <code>peak_tflops(sms, cores_per_sm, ghz, flops_per_tick)</code> returning the peak in TFLOP/s rounded to 2 decimals.</p>',
         '''
def peak_tflops(sms, cores_per_sm, ghz, flops_per_tick):
    # your code here
    pass
''', [("peak_tflops(40, 64, 1.59, 2)", 8.14), ("peak_tflops(108, 64, 1.41, 2)", 19.49), ("peak_tflops(80, 64, 1.53, 2)", 15.67)],
         '''
def peak_tflops(sms, cores_per_sm, ghz, flops_per_tick):
    return round(sms * cores_per_sm * ghz * 1e9 * flops_per_tick / 1e12, 2)
''', 'Multiply everything, divide by 10¹².', '<p>T4 8.14, A100 FP32 19.49 (sold as 19.5), V100 FP32 15.67 TFLOP/s.</p>')

K.must('Two designs', 'CPU: big control and caches, few strong ALUs, low latency. GPU: thousands of small ALUs, small control, high throughput.')
K.must('Latency and throughput', 'Latency = time for one job. Throughput = jobs ÷ time. FPS = 1000 ÷ ms per frame. Batch time = ⌈N ÷ C⌉ × time per round.')
K.must('Power', 'P ∝ α C V² f. Higher clock needs higher voltage, so power explodes. GPUs use many cores at a moderate clock.')
K.must('Peak', 'Peak = FLOPs per tick per core × clock × cores. FMA = 2 FLOPs. T4 ≈ 8.1, A100 FP32 ≈ 19.5 TFLOP/s.')
K.must('Hardware spectrum', 'CPU → GPU → FPGA → ASIC: less flexible, more efficient. TPU and NPU are ASIC style AI accelerators. The CPU is always the host.')

T = K.topic(
    slug='why-gpus', topic='why-gpus', step=(1, 'Why GPUs', 'gpu-why', 'Why a chip with thousands of slow cores beats a few fast ones, how to measure speed, and how much a GPU can ever help.', 'School'),
    title='Why GPUs: latency, throughput and power', short='Why GPUs', badge='1.1', minutes=40,
    lead='See why a GPU spends its silicon on thousands of small arithmetic units, measure speed as latency and throughput, and work out peak FLOPs and power from first principles.',
    desc='CPU against GPU design, the bus and gardener analogies, latency, throughput, FPS and batch time, the inference FPS study, clock, voltage and dynamic power, peak FLOPs of real GPUs, the power wall, and the CPU, GPU, FPGA and ASIC spectrum with TPU and NPU.',
    summary='CPU against GPU design, latency and throughput, FPS and batch time, clock and power, peak FLOPs, and the hardware spectrum.',
    keywords=['GPU', 'CPU', 'latency', 'throughput', 'FPS', 'peak FLOPs', 'power', 'TPU', 'NPU', 'FPGA', 'ASIC'],
    recap='<p>A GPU trades the speed of one job for the number of jobs finished per second. It wins whenever a problem splits into many independent pieces.</p>')
