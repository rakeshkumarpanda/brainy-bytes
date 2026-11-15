# Application Security 2.1: memory safety. Checked against Aleph One, Smashing the Stack for Fun and Profit
# (Phrack 49, 1996), Cowan et al., StackGuard (USENIX Security 1998), Shacham et al., On the Effectiveness of
# Address-Space Randomization (ACM CCS 2004), Shacham, The Geometry of Innocent Flesh on the Bone (ACM CCS 2007),
# Microsoft MSRC and Chromium statements on memory safety bugs (2019, 2020), Google Security Blog on Android memory
# safety (2024), the US ONCD report Back to the Building Blocks (2024), CISA and NSA memory safety guidance, the
# Linux kernel ASLR settings and the Rust reference.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-memsafe')
K = Kit()

K.code('stack_overflow', r'''
# A stack buffer overflow, modelled with a bytearray: what C's strcpy does when the input is too long.
# Layout of one stack frame (simplified, low to high addresses): buf[16] | canary[8] | saved return address[8]
import struct

def make_frame(canary):
    frame = bytearray(32)
    frame[16:24] = struct.pack("<Q", canary)
    frame[24:32] = struct.pack("<Q", 0x401136)            # where the function should return to
    return frame

def strcpy_unchecked(frame, data):
    frame[0:len(data)] = data                              # copies every byte, however many there are

def strcpy_checked(frame, data):
    if len(data) > 16:
        raise ValueError("input longer than the 16 byte buffer")
    frame[0:len(data)] = data

def function_return(frame, canary, check_canary):
    if check_canary and struct.unpack("<Q", frame[16:24])[0] != canary:
        return "*** stack smashing detected ***: program aborted"
    ret = struct.unpack("<Q", frame[24:32])[0]
    return f"returns to 0x{ret:x}" + ("  <- attacker chose this address" if ret != 0x401136 else "")

CANARY = 0x8a1f3c5e7b2d9400                                  # random per run, low byte 0 to stop string copies
good = b"alice"
evil = b"A" * 16 + b"B" * 8 + struct.pack("<Q", 0xdeadbeef)  # fill buf, smash canary, set return address

for label, data in [("normal input", good), ("long input", evil)]:
    for check in (False, True):
        f = make_frame(CANARY)
        strcpy_unchecked(f, data)
        print(f"{label:12} canary check {'on ' if check else 'off'}: {function_return(f, CANARY, check)}")
f = make_frame(CANARY)
try:
    strcpy_checked(f, evil)
except ValueError as e:
    print("bounds checked copy:        refused,", e)
''', long=True)

K.code('aslr_entropy', r'''
# How much does address space layout randomisation (ASLR) help? It depends on the bits of randomness
# and on whether a crash gives the attacker a fresh random layout or the same one again.
def expected_tries(bits, rerandomised):
    n = 2 ** bits
    return n if rerandomised else (n + 1) / 2          # with replacement versus without replacement

def p_success(bits, tries, rerandomised):
    n = 2 ** bits
    return 1 - (1 - 1 / n) ** tries if rerandomised else min(1.0, tries / n)

for name, bits in [("32 bit Linux mmap (about 8 bits)", 8), ("Shacham et al. 2004 target (16 bits)", 16),
                   ("64 bit Linux mmap (28 bits)", 28)]:
    e = expected_tries(bits, False)
    print(f"{name:38} expected guesses {e:>16,.1f}   P(win in 1000 tries) = {p_success(bits, 1000, False):.6f}")

print("\nA forking server keeps the same layout in every child, so each guess rules one address out.")
print("Re-randomising on every restart turns guessing into a fresh lottery each time:")
for bits in (8, 16):
    print(f"   {bits} bits: same layout {expected_tries(bits, False):>8,.1f} tries, fresh layout {expected_tries(bits, True):>8,} tries")
print("\nAn information leak of one pointer reveals the whole offset and makes ASLR worthless for that run.")
''', long=True)

K.code('integer_overflow', r'''
# Integer overflow: in C a 32 bit unsigned number wraps around, so a size check can be fooled.
# Python integers never overflow, so the wrap is modelled with "& 0xFFFFFFFF".
MASK = 0xFFFFFFFF

def alloc_size_buggy(count, item_size):
    return (count * item_size) & MASK             # what uint32_t size = count * item_size gives in C

def alloc_size_safe(count, item_size):
    if item_size and count > MASK // item_size:   # check before multiplying
        raise OverflowError("count * item_size does not fit in 32 bits")
    return count * item_size

for count in (1000, 0x40000001):
    size = alloc_size_buggy(count, 4)
    print(f"count {count:>11}: buffer of {size:>10} bytes, loop writes {count * 4:>11} bytes"
          + ("  <- heap overflow" if size < count * 4 else ""))
try:
    alloc_size_safe(0x40000001, 4)
except OverflowError as e:
    print("safe version:", e)

# Signed wrap: a length that looks negative passes a "too big?" check
def to_int32(x):
    x &= MASK
    return x - 2 ** 32 if x >= 2 ** 31 else x

length = to_int32(0xFFFFFFF0)                      # attacker sends 4294967280
print("as signed 32 bit:", length, "| check 'length > 1024' passes:", not length > 1024)
print("as unsigned size for memcpy:", length & MASK, "bytes")
''', long=True)

K.code('use_after_free', r'''
# Use after free on a toy heap: a freed block is reused, and an old pointer now sees someone else's data
class Heap:
    def __init__(self, blocks):
        self.mem = [None] * blocks
        self.free_list = list(range(blocks))
        self.gen = [0] * blocks                   # generation counter for the safe handle version

    def malloc(self, value):
        addr = self.free_list.pop()               # the most recently freed block is reused first (LIFO)
        self.mem[addr] = value
        return addr

    def free(self, addr):
        self.mem[addr] = None
        self.gen[addr] += 1
        self.free_list.append(addr)

heap = Heap(4)
session = heap.malloc({"user": "alice", "is_admin": False})
heap.free(session)                                # alice logs out, but the code keeps the pointer "session"
attacker = heap.malloc({"user": "mallory", "is_admin": True})
print("same block reused:", session == attacker)
print("old pointer now reads:", heap.mem[session], " <- dangling pointer sees mallory's object")

# Fix idea 1: set pointers to None after free. Fix idea 2: handles that remember the generation.
def deref(heap, handle):
    addr, gen = handle
    if heap.gen[addr] != gen:
        raise RuntimeError("use after free detected: block was freed and reused")
    return heap.mem[addr]

addr = heap.malloc({"user": "bob"})
h = (addr, heap.gen[addr])                        # a handle is the address plus its generation
heap.free(addr)
heap.malloc({"user": "eve"})
try:
    deref(heap, h)
except RuntimeError as e:
    print("generation check:", e)
print("Rust prevents this at compile time: a value cannot be used after it has been moved or dropped.")
''', long=True)

K.lesson('idea', 'Memory safety: why C and C++ bugs become exploits', f'''
{talk('A running program keeps its data in memory. Local variables and the bookkeeping for function calls live on the stack, which grows and shrinks as functions are called and return. Objects that must live longer are allocated on the heap and, in C and C++, freed by hand. These languages give the programmer raw pointers and trust them completely: reading or writing past the end of a buffer, using memory after freeing it, or freeing it twice is not an error the language catches. The behaviour is undefined, and often the program just carries on with corrupted memory. Attackers turn that corruption into control. The Morris worm of 1988 overflowed a buffer in the fingerd service. In 1996 Aleph One’s article Smashing the Stack for Fun and Profit, in Phrack, explained the technique step by step and started decades of exploits. Code Red in 2001, Slammer in 2003, and EternalBlue in 2017 were all memory corruption bugs, as was Heartbleed. In 2019 Matt Miller of Microsoft reported that about 70 percent of the security bugs Microsoft fixed each year were memory safety issues, and the Chromium project reported the same 70 percent in 2020. That number changed the debate. Governments, including the US Cybersecurity and Infrastructure Security Agency, the NSA and the White House Office of the National Cyber Director in 2024, now urge vendors to write new code in memory safe languages such as Rust, Go, Java, C sharp, Swift and Python. This chapter shows the main bug classes, the defences added to operating systems and compilers over 25 years, and why a memory safe language removes whole classes at once.')}
{src('Aleph One, Smashing the Stack for Fun and Profit, Phrack 49 (1996), Cowan et al., StackGuard: Automatic Adaptive Detection and Prevention of Buffer-Overflow Attacks (USENIX Security 1998), Shacham, Page, Pfaff, Goh, Modadugu and Boneh, On the Effectiveness of Address-Space Randomization (ACM CCS 2004), Shacham, The Geometry of Innocent Flesh on the Bone: Return-into-libc without Function Calls (ACM CCS 2007), Matt Miller, Trends, Challenges and Strategic Shifts in the Software Vulnerability Mitigation Landscape (BlueHat IL 2019), Chromium Project, Memory Safety (2020), Google Security Blog, Eliminating Memory Safety Vulnerabilities at the Source (2024), US ONCD, Back to the Building Blocks (2024), Linux kernel documentation on randomize_va_space and mmap_rnd_bits, The Rust Programming Language book.')}
{safe('Every program here models memory with Python lists and bytearrays, so nothing real is overflowed. To study real exploitation, use deliberately vulnerable binaries in a virtual machine, such as the exercises in pwn.college or picoCTF.')}
{wwh('<b>Memory safety</b> means a program can only access memory it is allowed to: within the bounds of each object, only while the object is alive, and only as the right type.',
     'Most severe vulnerabilities in operating systems, browsers and network services are memory safety bugs, and they often give the attacker full control of the process.',
     'Avoid the bugs by checking bounds and lifetimes (or by using a language that enforces them), and make the remaining bugs hard to exploit with canaries, non executable memory, ASLR, control flow integrity and hardware tagging.')}
{table(['Bug class', 'What goes wrong', 'Typical result', 'Famous case'], [
    ['Stack buffer overflow', 'Write past a local array', 'Overwrite the return address', 'Morris worm 1988, Code Red 2001'],
    ['Heap buffer overflow', 'Write past a heap object', 'Corrupt neighbouring objects', 'Slammer 2003, EternalBlue 2017'],
    ['Out of bounds read', 'Read past an object', 'Leak secrets or pointers', 'Heartbleed 2014'],
    ['Use after free', 'Use memory after freeing it', 'Attacker controlled object used', 'Many browser exploits'],
    ['Double free', 'Free the same block twice', 'Allocator corruption', 'CVE-2019-11932, WhatsApp GIF bug'],
    ['Integer overflow', 'Arithmetic wraps around', 'Too small buffer, then overflow', 'Stagefright, Android 2015'],
    ['Format string', 'User text used as printf format', 'Read or write memory', 'Many Unix tools around 2000']])}
''', kw=['memory safety', 'stack', 'heap', 'undefined behaviour', 'buffer overflow', 'use after free', 'double free', 'integer overflow', 'format string', 'Aleph One', 'Phrack', 'Morris worm', '70 percent', 'memory safe languages'])

K.lesson('overflow', 'Stack overflows, canaries, NX and return oriented programming', f'''
{talk('When a function is called, the CPU pushes the return address, the place to continue when the function ends, onto the stack. The function’s local arrays sit just below it. If the function copies input into a local array with something like strcpy or gets, which never check the size, a long input runs past the end of the array and overwrites the saved return address. When the function returns, the CPU jumps wherever the attacker wrote. In the 1990s attackers put machine code, called shellcode, in the same input and jumped straight to it. Defenders answered in layers. Stack canaries, introduced by StackGuard in 1998 and now turned on by compiler flags such as -fstack-protector, place a random value between the buffers and the return address and check it before returning: an overflow that reaches the return address must destroy the canary first. Non executable memory, the NX bit in AMD processors from 2003 and Data Execution Prevention in Windows XP Service Pack 2 in 2004, marks the stack as data only, so injected shellcode cannot run. Attackers answered with code reuse. Instead of injecting code, they chain together short pieces of the program’s own code that end in a return instruction, called gadgets. Hovav Shacham showed in 2007 that such return oriented programming can compute anything. That is why ASLR, in the next lesson, matters: gadgets are useless if you do not know where they are. Newer processors add shadow stacks, such as Intel CET since 2020, which keep a protected second copy of return addresses and stop the process if the two differ.')}
{viz('cystack')}
{run('stack_overflow')}
{fxs(fx('Overflow reaches the return address when', 'input length &gt; buffer size + canary size + saved frame pointer', 'Here 16 + 8 = 24 bytes, so bytes 24 to 31 land on the return address.', key=True),
     fx('Guessing a canary at once', 'P = 2<sup>&minus;56</sup>', 'A 64 bit canary with its low byte fixed at 0 (to stop string copies) has 56 random bits.', key=True),
     fx('Byte by byte canary leak (forking servers)', 'tries &le; 7 &times; 256 = 1792', 'If a child crash keeps the same canary, an attacker can guess one byte at a time, as in the 2014 BROP attack.'))}
{table(['Defence', 'Year', 'Stops', 'Bypassed by'], [
    ['Stack canary', '1998', 'Linear overwrite of the return address', 'Info leaks, overwriting other pointers, byte by byte guessing'],
    ['NX / DEP', '2003 to 2004', 'Running injected code on stack or heap', 'Return oriented programming'],
    ['ASLR', '2001 (PaX), 2005 (Linux), 2007 (Windows)', 'Jumping to known addresses', 'Info leaks, brute force with few bits'],
    ['Shadow stack (CET)', '2020', 'Corrupted return addresses', 'Attacks on forward edges, such as function pointers'],
    ['Safe functions', 'always', 'The bug itself', 'Nothing, if used everywhere: strncpy_s, snprintf, std::string']])}
''', kw=['stack overflow', 'return address', 'strcpy', 'gets', 'shellcode', 'stack canary', 'StackGuard', 'fstack-protector', 'NX bit', 'DEP', 'return oriented programming', 'ROP', 'gadgets', 'Shacham', 'shadow stack', 'Intel CET', 'BROP'])

K.lesson('aslr', 'ASLR: randomness against exploits', f'''
{talk('Address space layout randomisation loads the program, its libraries, the stack and the heap at random addresses each time the program starts. An exploit that needs to jump to a gadget, or to the system function in the C library, must first guess where it is, and a wrong guess usually crashes the process. The PaX project introduced ASLR for Linux in 2001, mainline Linux followed in 2005 and Windows Vista in 2007. How much it helps depends on two things. The first is entropy, the number of random bits. On 32 bit Linux the default randomisation of shared libraries is only 8 bits, 256 possibilities, which can be brute forced in seconds. In 2004 Hovav Shacham and colleagues at Stanford showed that even 16 bits on 32 bit systems fell to a brute force attack on a web server in about 216 seconds on average. On 64 bit systems Linux uses 28 bits or more by default, which makes blind guessing hopeless. The second is what happens after a crash. Servers that fork a new child for each connection give every child the same layout, so each wrong guess rules out one possibility and the attacker can simply sweep through them. A process that re-randomises after each crash makes every guess a fresh lottery. The most important caveat is that ASLR is defeated completely by an information leak. If any bug reveals one pointer into a library, the attacker learns the random offset and can compute every other address. Modern exploits therefore usually chain two bugs: one to leak an address, one to take control.')}
{viz('cyaslr')}
{run('aslr_entropy')}
{fxs(fx('Expected guesses, same layout every time', 'E = (2<sup>n</sup> + 1) / 2', 'Each failure removes one candidate: sampling without replacement. 8 bits: 128.5 tries.', key=True),
     fx('Expected guesses, fresh layout every time', 'E = 2<sup>n</sup>', 'A geometric distribution with p = 2<sup>&minus;n</sup>. 8 bits: 256 tries.', key=True),
     fx('Chance within k tries', 'same layout: k / 2<sup>n</sup>,  fresh layout: 1 &minus; (1 &minus; 2<sup>&minus;n</sup>)<sup>k</sup>', '16 bits, 1000 tries: 0.0153 with the same layout.'))}
{deep('Where the bits go on 64 bit Linux', '<p>The kernel setting /proc/sys/kernel/randomize_va_space = 2 turns on full randomisation. The mmap base, where shared libraries go, gets mmap_rnd_bits of randomness, 28 by default on x86-64, and the stack and heap have their own random offsets. A position independent executable (PIE), the default in most distributions since around 2017, lets the main program move too. Kernel ASLR (KASLR) randomises the kernel itself, though side channels such as timing attacks on the CPU’s caches have repeatedly leaked its offset.</p>')}
''', kw=['ASLR', 'address space layout randomisation', 'entropy', 'brute force', 'PaX', 'PIE', 'KASLR', 'information leak', 'fork server', 'mmap_rnd_bits', 'geometric distribution'])

K.lesson('heap', 'Heap bugs: use after free, integer overflow and friends', f'''
{talk('The heap is where long lived objects go. In C a program calls malloc to get a block and free to give it back, and the allocator keeps lists of free blocks to reuse. Three bug classes dominate here. Use after free happens when code frees an object but some pointer still refers to it. If the attacker can make the program allocate a new object of the same size, often just by sending a message or loading a web page element, the allocator hands out the same block, now filled with attacker data. The old pointer then reads the attacker’s values, which can include fake function pointers that redirect execution. Browsers, with their complex object lifetimes driven by JavaScript, have suffered from this more than any other bug class. A double free gives the same block back twice and corrupts the allocator’s own lists. Integer overflow causes heap overflows indirectly. In C a 32 bit unsigned multiplication such as count times 4 silently wraps around, so a huge count can produce a tiny allocation, and the loop that fills it then writes far past the end. In 2015 Joshua Drake showed a set of such bugs in Android’s Stagefright media library that could be triggered by a single multimedia message, affecting around 950 million devices. Signed and unsigned mix ups are similar: a length of minus 16 passes a check for being too large and then becomes four billion when passed to memcpy. The defences are checks before arithmetic, using size types correctly, allocators that delay reuse and add checks, and memory tagging in hardware such as Arm MTE, which gives each allocation a small tag that pointers must match.')}
{viz('cyuaf')}
{run('use_after_free')}
{run('integer_overflow')}
{fxs(fx('Unsigned wrap', 'result = (a &times; b) mod 2<sup>32</sup>', '0x40000001 &times; 4 = 2<sup>32</sup> + 4, which wraps to 4: a 4 byte buffer for 4 GB of data.', key=True),
     fx('Safe multiplication check', 'if b &ne; 0 and a &gt; (2<sup>32</sup> &minus; 1) / b: refuse', 'Check before multiplying. C23 adds ckd_mul, GCC and Clang have __builtin_mul_overflow.', key=True),
     fx('Two’s complement', 'signed(x) = x &minus; 2<sup>32</sup> if x &ge; 2<sup>31</sup>', '0xFFFFFFF0 is &minus;16 as signed and 4294967280 as unsigned.'))}
''', kw=['heap', 'malloc', 'free', 'use after free', 'dangling pointer', 'double free', 'integer overflow', 'wraparound', 'signedness', 'Stagefright', 'memory tagging', 'Arm MTE', 'hardened allocator'])

K.lesson('defences', 'Finding and stopping memory bugs', f'''
{talk('Defence against memory bugs works on three fronts. The first is finding bugs before attackers do. Sanitisers are compiler options that add checks to a test build: AddressSanitizer, from Google in 2011, puts poisoned zones around every allocation and stops at the first out of bounds or use after free access, at about twice the normal running cost. Fuzzers such as AFL, released by Michal Zalewski in 2013, and libFuzzer feed millions of mutated inputs to a program while watching which code paths each one reaches, and keep the inputs that find new paths. Google’s OSS-Fuzz project has used this to find tens of thousands of bugs in open source software. The second front is making bugs hard to exploit, the layers of canaries, NX, ASLR and control flow integrity covered earlier, plus hardware features such as memory tagging and pointer authentication on Arm. CHERI, a research architecture from the University of Cambridge and SRI International, goes further by replacing plain pointers with capabilities that carry their own bounds and permissions, and Arm built a prototype chip called Morello in 2022. The third front, and the only one that removes the bug classes, is memory safe languages. Rust, first stable in 2015, enforces bounds checks and tracks who owns each value and how long each reference lives, at compile time, so use after free and data races simply do not compile, while still giving C like speed without a garbage collector. Rust is now accepted in the Linux kernel and used in Android, Windows and Chromium.')}
{table(['Tool or feature', 'Kind', 'What it does'], [
    ['AddressSanitizer (ASan)', 'Testing', 'Detects out of bounds and use after free at runtime in test builds'],
    ['UndefinedBehaviorSanitizer', 'Testing', 'Detects integer overflow, bad shifts and other undefined behaviour'],
    ['AFL, libFuzzer, OSS-Fuzz', 'Testing', 'Coverage guided fuzzing with millions of generated inputs'],
    ['Stack canaries, NX, ASLR, PIE', 'Mitigation', 'Raise the cost of turning a bug into an exploit'],
    ['CFI, Intel CET, Arm PAC', 'Mitigation', 'Protect return addresses and indirect calls'],
    ['Arm MTE', 'Hardware', 'Tags memory and pointers, catches mismatches'],
    ['CHERI capabilities', 'Hardware', 'Pointers that carry bounds and permissions'],
    ['Rust, Go, Java, Swift, Python', 'Language', 'Remove the bug classes for new code']])}
{steps('A modern plan for an old C or C++ code base', [
    'Turn on every compiler hardening flag: -fstack-protector-strong, -D_FORTIFY_SOURCE=3, PIE, RELRO, CET where available.',
    'Run tests and fuzzers under AddressSanitizer and UndefinedBehaviorSanitizer in continuous integration.',
    'Replace unsafe functions (gets, strcpy, sprintf) and raw arrays with bounded alternatives.',
    'Write new components in a memory safe language and connect them through narrow interfaces.',
    'Rewrite the riskiest parts first: parsers of untrusted input such as image, font and network code.'])}
''', kw=['AddressSanitizer', 'sanitizers', 'fuzzing', 'AFL', 'libFuzzer', 'OSS-Fuzz', 'CFI', 'pointer authentication', 'CHERI', 'Morello', 'Rust', 'borrow checker', 'FORTIFY_SOURCE', 'hardening flags'])

K.lesson('versus', 'Languages and memory safety compared', f'''
{talk('People sometimes say that safe languages are slow or that careful C programmers do not make these mistakes. Decades of data from Microsoft, Google and Apple say otherwise: even the best teams ship memory bugs in large C and C++ code bases. The useful comparison is what each language guarantees, and at what cost.')}
{versus('What each language guarantees', ['', 'C', 'C++ (modern)', 'Rust', 'Go, Java, C#', 'Python'], [
    ['Bounds checks', 'No', 'Optional (at(), spans)', 'Yes, by default', 'Yes', 'Yes'],
    ['Use after free possible', 'Yes', 'Yes, fewer with smart pointers', 'No, outside unsafe blocks', 'No, garbage collected', 'No'],
    ['Integer overflow', 'Silent wrap or undefined', 'Silent wrap or undefined', 'Panics in debug, wraps explicitly in release', 'Wraps (Go, Java), checked option in C#', 'Never, integers grow'],
    ['Speed', 'Fastest', 'Fastest', 'Close to C', 'Fast, GC pauses', 'Slower'],
    ['Typical use', 'Kernels, embedded', 'Browsers, games', 'New systems code', 'Servers, apps', 'Scripts, ML, tools']],
    'Write new systems code in Rust or another safe language where you can, harden and fuzz the C and C++ you must keep, and remember that safe languages still have logic bugs, injection and unsafe escape hatches.')}
''', kw=['comparison', 'C', 'C++', 'Rust', 'Go', 'Java', 'Python', 'unsafe', 'smart pointers'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that updates often fix memory bugs and installs them. A college student can explain stack frames, overflows, canaries, NX and ASLR, and compute brute force odds. A professional hardens builds, runs sanitisers and fuzzers, and reviews C code for risky patterns. Experts write exploits in capture the flag contests and research new mitigations and the formal semantics of safe languages.')}
{ladder(
    '<p>Install updates promptly, because many of them fix memory bugs that could let a web page or file take over your device.</p>',
    '<p>Stack and heap layout, buffer overflows, canaries, NX, ASLR maths, use after free, integer overflow, and why Rust removes these classes.</p>',
    '<p>Compiler hardening flags, ASan and UBSan in CI, coverage guided fuzzing with AFL++ or libFuzzer, binary analysis with Ghidra, and migration plans to memory safe languages.</p>',
    '<p>Exploit development against modern mitigations in CTFs, heap exploitation techniques, control flow integrity design, CHERI and MTE, and formal proofs of safety such as RustBelt.</p>')}
{grow('Explain why updates fix memory bugs.',
      'Model overflows and compute mitigation odds.',
      'Harden, fuzz and migrate real code.')}
''', kw=['beginner', 'expert', 'CTF', 'exploit development', 'AFL++', 'RustBelt'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Why</b>: C and C++ trust pointers, so bounds and lifetime mistakes become exploits. About 70% of serious bugs at Microsoft and in Chromium are memory safety bugs.',
    '<b>Stack overflow</b>: a long copy overwrites the return address. Canaries (1998), NX (2003 to 2004), then ROP (2007), then shadow stacks (2020).',
    '<b>ASLR</b>: random addresses. Same layout: (2<sup>n</sup> + 1)/2 guesses, fresh layout: 2<sup>n</sup>. 8 bits is weak, 28 bits strong. One pointer leak defeats it.',
    '<b>Heap bugs</b>: use after free, double free, integer overflow (mod 2<sup>32</sup> wrap), signedness. Check before arithmetic. MTE, hardened allocators.',
    '<b>Finding bugs</b>: AddressSanitizer, fuzzers such as AFL and OSS-Fuzz. Hardening flags. CHERI and Morello.',
    '<b>Safe languages</b>: Rust, Go, Java, Swift, Python remove the classes. Android memory bugs fell from 76% (2019) to 24% (2024).'],
    'Next, Application Security 2.2: building security into development, with threat modelling, code scanning and fuzzing.')}
{files('Three tasks: a safe 32 bit multiply, the expected ASLR guesses, and a bounded copy.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is a buffer overflow?', ['A full hard disk', 'Writing more data into a buffer than it can hold, overwriting nearby memory', 'Too many network packets', 'A slow program'], 1, 'Past the end.', 'In C nothing stops it.')
K.quiz('e', 'Why are most memory safety bugs found in C and C++ code?', ['These languages are old', 'They do not check bounds or object lifetimes automatically', 'They are compiled', 'They run on servers'], 1, 'No checks.', 'Safe languages check or prevent these errors.')
K.quiz('e', 'About what share of serious security bugs did Microsoft and Chromium report as memory safety bugs?', ['7%', '70%', '30%', '99%'], 1, 'Seventy.', 'Microsoft 2019, Chromium 2020.')
K.quiz('e', 'What does a stack canary do?', ['Encrypts the stack', 'Puts a random value before the return address and checks it before returning', 'Speeds up calls', 'Logs errors'], 1, 'Tripwire.', 'An overflow must change it to reach the return address.')
K.quiz('m', 'Why did NX (non executable memory) lead to return oriented programming?', ['NX made programs slow', 'Injected code could no longer run, so attackers reused short pieces of existing code', 'NX disabled ASLR', 'ROP is older'], 1, 'Code reuse.', 'Shacham showed ROP is Turing complete in 2007.')
K.quiz('m', 'A forking server keeps the same layout for every child. With 8 bits of ASLR, the expected number of guesses is', ['8', '128.5', '256', '65536'], 1, '(2<sup>n</sup> + 1)/2.', 'Each crash rules out one offset.')
K.quiz('m', 'What defeats ASLR completely?', ['A faster CPU', 'An information leak that reveals one pointer', 'A longer password', 'A firewall'], 1, 'Leak.', 'One address gives away the random offset.')
K.quiz('m', 'In use after free, why does the attacker allocate a new object of the same size?', ['To save memory', 'So the allocator reuses the freed block and the old pointer reads attacker data', 'To crash the program', 'To free more memory'], 1, 'Reuse.', 'Allocators often reuse the most recently freed block.')
K.quiz('m', 'In 32 bit unsigned arithmetic, 0x40000001 &times; 4 equals', ['4294967300', '4', '0', '1073741825'], 1, 'Wraps.', '2<sup>32</sup> + 4 mod 2<sup>32</sup> = 4.')
K.quiz('h', 'Why does a stack canary on x86-64 Linux have its lowest byte set to zero?', ['For speed', 'String functions stop at a zero byte, so a string overflow cannot copy past it to rewrite the canary', 'It is a bug', 'To mark the stack'], 1, 'Terminator.', 'It leaves 56 random bits.')
K.quiz('h', 'What does AddressSanitizer do?', ['Encrypts memory', 'Adds poisoned zones around allocations in test builds and stops at the first bad access', 'Removes bugs automatically', 'Replaces malloc in production'], 1, 'Detects.', 'About 2x slowdown, so used in testing and fuzzing.')
K.quiz('h', 'How does Rust prevent use after free without a garbage collector?', ['Runtime checks on every pointer', 'Ownership and lifetimes checked at compile time', 'It never frees memory', 'It uses reference counting only'], 1, 'Borrow checker.', 'Code that would use a dropped value does not compile.')
K.quiz('h', 'An Intel CET shadow stack protects', ['Function pointers', 'Return addresses, by keeping a protected second copy', 'Heap objects', 'Disk files'], 1, 'Backward edges.', 'Forward edges need other CFI checks.')
K.quiz('x', 'In the style of a Stanford CS 155 question: an attacker can brute force a forking server whose canary stays the same in every child. How many tries at most to learn a 7 random byte canary byte by byte?', ['2<sup>56</sup>', '7 &times; 256 = 1792', '256', '56'], 1, 'One byte at a time.', 'A crash or no crash reveals whether each byte guess was right, as in BROP (2014).')
K.quiz('x', 'In the style of an IIT Bombay CS 745 exam: which pair of bugs does a modern browser exploit usually chain?', ['Two XSS bugs', 'An information leak to defeat ASLR, then a memory corruption to take control', 'SQL injection and CSRF', 'Two phishing emails'], 1, 'Leak, then control.', 'Then often a sandbox escape as a third step.')

K.calc('e', 'Buffer 16 bytes, canary 8 bytes, return address 8 bytes. How many input bytes fully overwrite the return address?', '32', 'Add them.', ['16 bytes fill the buffer.', '8 more cover the canary.', eq('16 + 8 + 8 = 32')], check=32)
K.calc('e', 'How many possible offsets does 8 bits of ASLR give?', '256', '2<sup>8</sup>.', ['n = 8 bits.', 'Each bit doubles the count.', eq('256')], check=256)
K.calc('e', 'What is (0x40000001 &times; 4) mod 2<sup>32</sup>?', '4', 'Wrap.', ['0x40000001 &times; 4 = 0x100000004.', 'Drop the bit above 32.', eq('4')], check=(0x40000001 * 4) % 2 ** 32)
K.calc('m', 'Expected guesses for 16 bit ASLR when the layout stays the same?', '32768.5', '(2<sup>n</sup> + 1)/2.', ['2<sup>16</sup> = 65536.', 'Add 1 and halve.', eq('32768.5')], check=32768.5)
K.calc('m', 'Expected guesses for 8 bit ASLR when every try gets a fresh layout?', '256', 'Geometric mean 1/p.', ['p = 1/256 per try.', 'Mean of a geometric distribution = 1/p.', eq('256')], check=256)
K.calc('m', 'Chance of winning within 1000 tries against 16 bit ASLR with the same layout? Round to 4 decimals.', '0.0153', 'k / 2<sup>n</sup>.', ['k = 1000.', '1000 / 65536.', eq('0.0153')], check=round(1000 / 2 ** 16, 4))
K.calc('m', 'Random bits in a 64 bit canary whose low byte is always 0?', '56', '64 &minus; 8.', ['64 bits in all.', '8 are fixed.', eq('56 bits')], check=56)
K.calc('m', 'Maximum tries to learn 7 canary bytes one at a time, 256 values each?', '1792', '7 &times; 256.', ['Each byte needs at most 256 guesses.', '7 bytes.', eq('1792')], check=1792)
K.calc('h', 'Chance of winning within 256 tries against 8 bit ASLR with fresh layouts each time? Round to 4 decimals.', '0.6328', '1 &minus; (255/256)<sup>256</sup>.', ['Miss chance per try 255/256.', '(255/256)<sup>256</sup> = 0.3672.', eq('1 &minus; 0.3672 = 0.6328')], check=round(1 - (255 / 256) ** 256, 4))
K.calc('h', 'What is 0xFFFFFFF0 as a signed 32 bit integer?', '-16', 'x &minus; 2<sup>32</sup>.', ['0xFFFFFFF0 = 4294967280.', 'It is &ge; 2<sup>31</sup>, so subtract 2<sup>32</sup>.', eq('&minus;16')], check=-16)
K.calc('h', 'Against 28 bit ASLR with the same layout, at 1000 tries per second, expected hours? Round to 2 decimals.', '37.28', '(2<sup>28</sup> + 1)/2 tries.', ['(2<sup>28</sup> + 1)/2 = 134217728.5.', 'Divide by 1000 per second: 134218 s.', eq('/ 3600 = 37.28 hours')], check=round((2 ** 28 + 1) / 2 / 1000 / 3600, 2))
K.calc('h', 'A 4 byte buffer receives 0x40000001 &times; 4 bytes. How many bytes land outside it?', '4294967296', 'Total minus 4.', ['Total = 4294967300 bytes.', 'Minus the 4 that fit.', eq('2<sup>32</sup> = 4294967296')], check=2 ** 32)
K.calc('x', 'Smallest whole n so that same layout brute force at 10<sup>4</sup> tries per second takes at least a year on average (1 year = 3.156 &times; 10<sup>7</sup> s)?', '40', 'Solve (2<sup>n</sup> + 1)/2 &ge; 3.156 &times; 10<sup>11</sup>.', ['2<sup>n</sup> &ge; 6.31 &times; 10<sup>11</sup>.', 'log<sub>2</sub>(6.31 &times; 10<sup>11</sup>) = 39.2.', eq('n = 40')], check=40)
K.calc('x', 'Android memory safety bugs fell from 76% to 24% of all its vulnerabilities. By how many percentage points?', '52', 'Subtract.', ['76 &minus; 24.', 'Percentage points, not percent.', eq('52 points, a fall of about 68% in relative terms')], check=52)

K.assign('mul32', 'e', 'A safe 32 bit multiply',
         '<p>Write <code>mul32(a, b)</code> for non negative integers. Return a &times; b if it fits in an unsigned 32 bit integer (at most 2<sup>32</sup> &minus; 1), and return None if it would overflow. Check before multiplying, as you would in C.</p>',
         '''
def mul32(a, b):
    # your code here
    pass
''', [('mul32(1000, 4)', 4000), ('mul32(0x40000001, 4)', None), ('mul32(65535, 65537)', 4294967295), ('mul32(65536, 65536)', None), ('mul32(0, 999999999999)', 0)],
         '''
MAX = 2 ** 32 - 1

def mul32(a, b):
    if b != 0 and a > MAX // b:
        return None
    return a * b
''', 'Compare a with MAX // b instead of computing a * b first.', '<p>65535 &times; 65537 = 2<sup>32</sup> &minus; 1 exactly, the largest value that fits. In C the same check prevents the Stagefright style bug.</p>')
K.assign('aslr_expected', 'm', 'Expected ASLR guesses',
         '<p>Write <code>aslr_expected(bits, same_layout)</code>. With n random bits there are 2<sup>n</sup> offsets. If the layout stays the same after each crash, return (2<sup>n</sup> + 1) / 2. If every try gets a fresh layout, return 2<sup>n</sup>. Return a float.</p>',
         '''
def aslr_expected(bits, same_layout):
    # your code here
    pass
''', [('aslr_expected(8, True)', 128.5), ('aslr_expected(8, False)', 256.0), ('aslr_expected(16, True)', 32768.5), ('aslr_expected(1, False)', 2.0)],
         '''
def aslr_expected(bits, same_layout):
    n = 2 ** bits
    return (n + 1) / 2 if same_layout else float(n)
''', 'Without replacement the mean position is (n + 1) / 2, with replacement it is n.', '<p>Re-randomising roughly doubles the attacker’s work, but adding bits multiplies it, which is why 64 bit ASLR is the real fix.</p>')
K.assign('strlcpy', 'h', 'A bounded string copy',
         '<p>Write <code>strlcpy(dst_size, src)</code> that models the BSD function. It copies at most dst_size &minus; 1 characters of src (leaving room for the terminating zero byte) and returns <code>[copied, len(src)]</code>. If dst_size is 0, copy nothing. The caller detects truncation when the second value is at least dst_size.</p>',
         '''
def strlcpy(dst_size, src):
    # your code here
    pass
''', [('strlcpy(8, "alice")', ['alice', 5]), ('strlcpy(8, "AAAAAAAAAAAA")', ['AAAAAAA', 12]), ('strlcpy(1, "x")', ['', 1]), ('strlcpy(0, "x")', ['', 1]), ('strlcpy(6, "hello")', ['hello', 5])],
         '''
def strlcpy(dst_size, src):
    if dst_size == 0:
        return ["", len(src)]
    return [src[:dst_size - 1], len(src)]
''', 'Slice to dst_size - 1 and always report the full source length.', '<p>Returning the source length lets callers write if (strlcpy(...) &gt;= size) to catch truncation, which plain strncpy does not make easy, and strncpy may also leave the result without a terminating zero.</p>')

K.must('Memory safety', 'In bounds, while alive, right type. C and C++ do not check. About 70% of serious bugs (Microsoft 2019, Chromium 2020). Morris 1988, Aleph One 1996.')
K.must('Stack overflow', 'Long copy overwrites the return address. Canary (StackGuard 1998, 56 random bits), NX/DEP (2003 to 2004), ROP (Shacham 2007), shadow stack (CET 2020).')
K.must('ASLR', 'Same layout: (2<sup>n</sup> + 1)/2 guesses. Fresh: 2<sup>n</sup>. 32 bit 8 bits, 64 bit 28 bits. Shacham 2004: 16 bits in about 216 s. Leaks defeat it.')
K.must('Heap bugs', 'Use after free (reuse of freed block), double free, integer overflow mod 2<sup>32</sup>, signedness. Check before multiply. Stagefright 2015. MTE.')
K.must('Finding bugs', 'ASan, UBSan, coverage guided fuzzing (AFL 2013, libFuzzer, OSS-Fuzz). Hardening flags: stack protector, FORTIFY_SOURCE, PIE, RELRO, CET.')
K.must('Safe languages', 'Rust ownership and borrow checker, Go, Java, Swift, Python. Android: 76% (2019) to 24% (2024). ONCD 2024 report. CHERI and Morello.')

T = K.topic(
    slug='cy-memsafe', topic='cy-memsafe', step=(2, 'Secure software and ethical hacking', 'cy-a2', 'Memory safety bugs and their defences, building security into development, the ethical hacking method and the human side of attacks.', 'Advanced'),
    title='Memory safety: overflows, ASLR, use after free and Rust', short='Memory safety', badge='2.1', minutes=80,
    lead='Why bugs in C and C++ turn into takeovers and how defenders fight back: stack frames and buffer overflows byte by byte, stack canaries, NX and return oriented programming, the probability maths of ASLR brute force, use after free, double free and integer overflow on the heap, sanitisers and fuzzing, and how Rust and other memory safe languages remove whole bug classes.',
    desc='memory safety, buffer overflow, stack overflow, return address, shellcode, stack canary, StackGuard, NX bit, DEP, return oriented programming, ROP, ASLR, PIE, KASLR, brute force, information leak, heap, use after free, dangling pointer, double free, integer overflow, signedness, Stagefright, format string, AddressSanitizer, fuzzing, AFL, libFuzzer, OSS-Fuzz, control flow integrity, Intel CET, shadow stack, Arm MTE, CHERI, Rust, borrow checker, memory safe languages, Aleph One, Morris worm',
    summary='Stack overflows and canaries, NX and ROP, ASLR brute force maths, heap bugs and integer overflow, sanitisers, fuzzing and Rust.',
    keywords=['buffer overflow', 'stack canary', 'NX', 'ROP', 'ASLR', 'use after free', 'integer overflow', 'AddressSanitizer', 'fuzzing', 'Rust'],
    recap='<p>Memory bugs are the largest source of serious vulnerabilities. Layer mitigations so bugs are hard to exploit, fuzz with sanitisers to find them, and write new code in memory safe languages so they cannot exist.</p>',
    added='2026-11-15')
