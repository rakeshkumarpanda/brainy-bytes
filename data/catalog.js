/* =====================================================================
   CATALOG: the one file that controls what the website shows.
   Edit this file, save it, upload it, and refresh the site. That is all.

   Levels:  subject  →  module  →  topic  →  sections (optional)  →  items (optional)

   SUBJECT fields
     id        short unique name used in links, letters, numbers and dashes only. Example: 'dsa'
     title     name on the dashboard card
     emoji     one emoji for the card
     color     card colour, any CSS colour. Example: '#2b7de9'
     blurb     one or two sentences for the card
     intro     (optional) longer text for the subject overview page
     tags      (optional) small labels on the card, also used by search
     page      (optional) path to ONE html page for the whole subject.
               Use this when a subject is a single page, with no modules.
     modules   list of modules

   MODULE fields
     id, title, emoji, blurb (optional), topics

   TOPIC fields
     id        unique inside its subject
     title     name in the contents list
     emoji     icon in the contents list
     page      path to the topic's html page. Example: 'content/dsa/arrays.html'
               Leave it out (or set soon: true) and the topic shows as "Coming soon".
     summary   one line shown under the title
     keywords  extra words people may search for
     added     (optional) date like '2026-10-18'. The newest topics appear on the home page.
     sections  (optional) places inside the page that search can jump to.
               Each section: { id, title, group, keywords, items }
               id is the part after # in the page address. Example: id 'Kadane' opens page#Kadane
               items are smaller things inside a section, each with its own id, title, kind and level.

   Adding a new topic page in 3 steps:
     1. Put the html file in content/<subject>/  (copy content/_template/topic-template.html to start)
     2. Add a topic block below with its page path
     3. Upload both files. The dashboard, contents list and search update by themselves.
   ===================================================================== */

window.CATALOG = {
  site: {
    name: 'Brainy Bytes',
    tagline: 'Deep concepts, served with a smile',
    headline: ['Learn it deep.', 'Laugh along the way.'],
    hello: 'New: the full Java course, plus quizzes and a narrator in 6 languages',
    intro: 'Free notes that move, joke and run. Every topic comes with animations you can control, everyday examples, step by step code in Java, JavaScript and Python, and practice from easy to expert.',
    footer: 'Brainy Bytes. Free to learn, free to share.',
    searchExamples: ['binary search', 'sieve', 'two pointers', 'GCD', 'Kadane', 'HashMap', 'transient', 'synchronized', 'serialization', 'try with resources'],
    jokes: [
      ['Why did the array go to therapy', 'It had too many unresolved indexes.'],
      ['Why do programmers mix up Halloween and Christmas', 'Because Oct 31 equals Dec 25.'],
      ['How does a binary search find its keys', 'It looks in half the places you would.'],
      ['Why was the loop so tired', 'It kept going round in circles all night.'],
      ['Why did the tester bring a ladder', 'To reach the high priority bugs.'],
      ['What did the stack say to the queue', 'You are so first in, first out.'],
      ['Why was the prime number lonely', 'Nobody could divide its attention.'],
      ['Why did the developer go broke', 'He used up all his cache.'],
      ['What is a programmer’s favourite hangout place', 'The Foo Bar.'],
      ['Why did the sorting algorithm win the race', 'It merged into the fast lane.'],
      ['Why did the Java developer wear glasses', 'Because he could not C#.'],
      ['What do you call a bug that keeps coming back', 'A regression with commitment issues.'],
      ['Why did zero refuse to fight eight', 'Eight was just zero with a belt on.'],
      ['Why did the matrix feel confident', 'It had its rows and columns in order.'],
      ['Why did the Java object refuse to travel', 'It was not Serializable.'],
      ['Why was the thread so calm', 'It had learned to wait and be notified.']
    ],
    doodles: ['{ }', 'O(n)', '[ ]', '∑', '🐞', '0101', '</>', 'π', '✓', 'if', '∞', '√', '++', '→', 'gcd', 'i++']
  },

  subjects: [
    {
      id: 'dsa',
      title: 'Data Structures & Algorithms',
      emoji: '🧩',
      color: '#2b7de9',
      blurb: 'Arrays, maths, searching, sorting and clever patterns, animated step by step.',
      intro: 'Start with the building blocks, then climb to expert patterns. Every ready topic has animations, everyday examples, line by line code runs and practice problems with brute force and optimized solutions.',
      tags: ['Arrays', 'Math', 'Searching', 'Sorting', 'Patterns'],
      modules: [
        {
          id: 'getting-started', title: 'Getting started', emoji: '🚀',
          blurb: 'What DSA is and how we measure speed.',
          topics: [
            { id: 'introduction', title: 'Introduction', emoji: '👋', summary: 'What data structures and algorithms are, and why they matter.', soon: true },
            { id: 'runtime-analysis', title: 'Run time analysis', emoji: '⏱️', summary: 'Big O, best and worst cases, and how to count steps.', keywords: ['big o', 'complexity', 'asymptotic'], soon: true }
          ]
        },
        {
          id: 'core', title: 'Core building blocks', emoji: '🧱',
          blurb: 'The maths and the arrays that almost every algorithm stands on.',
          topics: [
            {
              id: 'math', title: 'Mathematics in DSA', emoji: '🧮',
              page: 'content/dsa/math-in-dsa.html',
              summary: '22 maths problems from primes and GCD to Miller-Rabin, naive versus optimized, with quizzes, number practice and a six language narrator.',
              keywords: ['number theory', 'prime', 'gcd', 'lcm', 'sieve of eratosthenes', 'modular arithmetic', 'combinatorics'],
              added: '2026-10-18',
              sections: mathSections()
            },
            {
              id: 'arrays', title: 'Arrays', emoji: '📦',
              page: 'content/dsa/array-adventure.html',
              summary: '26 lessons from memory layout to segment trees, 104 practice problems, quizzes, number practice and a six language narrator.',
              keywords: ['array', 'list', 'two pointers', 'sliding window', 'prefix sum', 'sorting', 'searching'],
              added: '2026-10-18',
              sections: arraySections()
            },
            { id: 'strings', title: 'Strings', emoji: '🔤', summary: 'Characters, patterns and clever matching.', keywords: ['string', 'substring', 'palindrome', 'kmp'], soon: true }
          ]
        },
        {
          id: 'linear', title: 'Linear structures', emoji: '🚃',
          topics: [
            { id: 'linked-lists', title: 'Linked lists', emoji: '🔗', summary: 'Nodes holding hands in a line.', soon: true },
            { id: 'stacks-queues', title: 'Stacks and queues', emoji: '🥞', summary: 'Last in first out, first in first out.', soon: true }
          ]
        },
        {
          id: 'nonlinear', title: 'Trees and graphs', emoji: '🌳',
          topics: [
            { id: 'trees', title: 'Trees', emoji: '🌲', summary: 'Family trees for data.', soon: true },
            { id: 'graphs', title: 'Graphs', emoji: '🕸️', summary: 'Maps, friends and networks.', soon: true }
          ]
        }
      ]
    },
    {
      id: 'manual-testing',
      title: 'Manual Testing',
      emoji: '🐞',
      color: '#f25da0',
      blurb: 'Find bugs before your users do: test design, life cycles and bug reports.',
      tags: ['STLC', 'Test cases', 'Bug life cycle'],
      modules: [
        {
          id: 'fundamentals', title: 'Fundamentals', emoji: '🧪',
          topics: [
            { id: 'sdlc-stlc', title: 'SDLC and STLC', emoji: '🔄', summary: 'Where testing fits in building software.', soon: true },
            { id: 'test-design', title: 'Test case design', emoji: '📝', summary: 'Boundary values, equivalence classes and decision tables.', keywords: ['boundary value analysis', 'equivalence partitioning'], soon: true },
            { id: 'bug-life-cycle', title: 'Bug life cycle', emoji: '🐛', summary: 'From new to closed, and every stop between.', soon: true }
          ]
        }
      ]
    },
    {
      id: 'java',
      title: 'Java',
      emoji: '☕',
      color: '#ff9238',
      blurb: 'Core Java from your first identifier to the JVM, with every example compiled and run.',
      intro: 'Nineteen chapters in seven modules. Every code block was compiled and run with JDK 21, and the real output, compile error or exception is shown under it. Each chapter has a comic strip, everyday examples, quizzes from easy to expert, number practice with full working, and a narrator who reads it aloud in six languages.',
      tags: ['OOP', 'Exceptions', 'Collections', 'Threads', 'JVM'],
      modules: javaModules()
    }
  ]
};

/* ===== Section lists for the DSA pages and the Java chapters. Generated, but safe to edit by hand. ===== */

function mathSections() {
  return [
    { id: "primality", title: "Primality Testing", emoji: '🧮', group: "Easy problems", keywords: ["Number theory", "Trial division", "Square root bound", "prime number", "is prime", "trial division", "square root bound", "6k plus minus 1", "composite"] },
    { id: "gcd", title: "GCD and LCM (Euclidean Algorithm)", emoji: '🧮', group: "Easy problems", keywords: ["Number theory", "Euclid", "Divisibility", "greatest common divisor", "least common multiple", "euclid", "hcf", "lcm", "reduce fraction"] },
    { id: "digits", title: "Counting Digits and Palindrome Number", emoji: '🧮', group: "Easy problems", keywords: ["Digit manipulation", "Modulo 10", "Two halves", "count digits", "palindrome number", "reverse number", "mod 10", "divide by 10", "digit sum"] },
    { id: "divisors", title: "All Divisors of N", emoji: '🧮', group: "Easy problems", keywords: ["Number theory", "Square root bound", "Divisor pairs", "divisors", "factors", "divisor pairs", "square root", "perfect number", "number of divisors"] },
    { id: "bits", title: "Power of Two and Counting Set Bits", emoji: '🧮', group: "Easy problems", keywords: ["Bit manipulation", "Kernighan", "Two's complement", "bit manipulation", "power of two", "popcount", "set bits", "Kernighan", "n & (n - 1)", "binary"] },
    { id: "base", title: "Base Conversion (Any Base 2 to 36)", emoji: '🧮', group: "Easy problems", keywords: ["Positional notation", "Repeated division", "Horner's rule", "base conversion", "binary", "hexadecimal", "octal", "radix", "Horner method", "positional notation"] },
    { id: "fib", title: "Nth Fibonacci Number", emoji: '🧮', group: "Easy problems", keywords: ["Recursion", "Overlapping subproblems", "Iteration", "fibonacci", "recursion", "memoization", "dynamic programming", "iterative", "overlapping subproblems"] },
    { id: "sieve", title: "Sieve of Eratosthenes", emoji: '🧮', group: "Medium problems", keywords: ["Primes", "Sieve", "Precomputation", "sieve of eratosthenes", "primes up to n", "prime table", "crossing out multiples", "n log log n"] },
    { id: "modpow", title: "Modular Exponentiation (Fast Power)", emoji: '🧮', group: "Medium problems", keywords: ["Binary exponentiation", "Modular arithmetic", "Divide and conquer", "modular exponentiation", "fast power", "binary exponentiation", "square and multiply", "mod 1e9+7", "RSA"] },
    { id: "factorial", title: "Factorial and Trailing Zeros", emoji: '🧮', group: "Medium problems", keywords: ["Factorial", "Legendre's formula", "Prime powers", "factorial", "trailing zeros", "legendre formula", "powers of 5", "big integer", "n!"] },
    { id: "factorize", title: "Prime Factorization", emoji: '🧮', group: "Medium problems", keywords: ["Trial division", "Fundamental theorem", "Smallest prime factor", "prime factorization", "trial division", "prime factors", "exponent", "unique factorization"] },
    { id: "totient", title: "Euler's Totient Function", emoji: '🧮', group: "Medium problems", keywords: ["Coprime counting", "Product formula", "Multiplicative function", "euler totient", "phi function", "coprime count", "gcd equals 1", "euler product formula", "RSA"] },
    { id: "ncr", title: "Binomial Coefficient nCr mod p", emoji: '🧮', group: "Medium problems", keywords: ["Combinatorics", "Pascal's triangle", "Fermat inverse", "binomial coefficient", "nCr", "combinations", "pascal triangle", "modular inverse", "fermat little theorem", "factorial mod p"] },
    { id: "isqrt", title: "Integer Square Root", emoji: '🧮', group: "Medium problems", keywords: ["Binary search on answer", "Newton's method", "Overflow safety", "integer square root", "floor sqrt", "binary search on answer", "newton method", "perfect square"] },
    { id: "incexc", title: "Inclusion-Exclusion: Count Multiples", emoji: '🧮', group: "Medium problems", keywords: ["Combinatorics", "Inclusion-exclusion", "Bitmask subsets", "LCM", "inclusion exclusion", "count multiples", "union of sets", "lcm", "subsets", "principle of inclusion exclusion"] },
    { id: "modinv", title: "Modular Inverse (Extended Euclid)", emoji: '🧮', group: "Hard problems", keywords: ["Extended Euclidean algorithm", "Bezout identity", "Modular arithmetic", "modular inverse", "extended euclidean algorithm", "bezout identity", "ax ≡ 1 mod m", "coprime", "division mod m"] },
    { id: "matfib", title: "Matrix Exponentiation (Nth Fibonacci in O(log N))", emoji: '🧮', group: "Hard problems", keywords: ["Linear recurrences", "Matrix power", "Binary exponentiation", "matrix exponentiation", "fibonacci log n", "linear recurrence", "fast power matrix", "2x2 matrix"] },
    { id: "lucas", title: "Lucas' Theorem (nCr mod small prime)", emoji: '🧮', group: "Hard problems", keywords: ["Combinatorics", "Base-p digits", "Pascal's triangle mod p", "lucas theorem", "nCr mod small prime", "base p digits", "binomial mod p", "combinatorics"] },
    { id: "catalan", title: "Catalan Numbers", emoji: '🧮', group: "Hard problems", keywords: ["Combinatorics", "Recurrence", "Dynamic programming", "Dyck paths", "catalan numbers", "balanced parentheses", "binary trees count", "dyck paths", "recursion", "dynamic programming"] },
    { id: "crt", title: "Chinese Remainder Theorem", emoji: '🧮', group: "Hard problems", keywords: ["Congruences", "Extended Euclid", "Number theory", "chinese remainder theorem", "system of congruences", "remainders", "extended euclid", "merging congruences", "lcm"] },
    { id: "segsieve", title: "Segmented Sieve (Primes in a Range)", emoji: '🧮', group: "Hard problems", keywords: ["Primes", "Sieve", "Memory efficiency", "segmented sieve", "primes in a range", "L to R", "sieve window", "memory efficient sieve"] },
    { id: "millerrabin", title: "Miller-Rabin Primality Test", emoji: '🧮', group: "Hard problems", keywords: ["Primality", "Fermat's little theorem", "Fast power", "Randomized algorithms", "miller rabin", "probabilistic primality", "deterministic bases", "strong pseudoprime", "fermat test", "big primes"] }
  ];
}

function arraySections() {
  return [
    { id: "MemoryAllocation", title: "Memory Allocation: Stack vs Heap", emoji: "🧠", group: "Phase 1: Foundations and Memory Architecture", keywords: ["stack", "heap", "garbage collection", "malloc", "free", "reference", "stack overflow", "memory leak"],
      items: [
        { id: "MemoryAllocation/practice-1", title: "Return a fresh array and keep the original safe", kind: 'Practice', level: "Easy" },
        { id: "MemoryAllocation/practice-2", title: "How many bytes does an array really use", kind: 'Practice', level: "Medium" },
        { id: "MemoryAllocation/practice-3", title: "Count islands without blowing the call stack", kind: 'Practice', level: "Hard" },
        { id: "MemoryAllocation/practice-4", title: "Build a first-fit heap allocator", kind: 'Practice', level: "Expert" }
      ] },
    { id: "ContiguousLayout", title: "Contiguous Memory Layout", emoji: "📏", group: "Phase 1: Foundations and Memory Architecture", keywords: ["address calculation", "base address", "row major", "column major", "padding", "alignment", "O(1) access"],
      items: [
        { id: "ContiguousLayout/practice-1", title: "Address calculator", kind: 'Practice', level: "Easy" },
        { id: "ContiguousLayout/practice-2", title: "From an address back to an index", kind: 'Practice', level: "Medium" },
        { id: "ContiguousLayout/practice-3", title: "Addresses with custom index ranges (exam classic)", kind: 'Practice', level: "Hard" },
        { id: "ContiguousLayout/practice-4", title: "Struct padding and array-of-structs addresses", kind: 'Practice', level: "Expert" }
      ] },
    { id: "CacheLocality", title: "Cache Locality", emoji: "⚡", group: "Phase 1: Foundations and Memory Architecture", keywords: ["cache line", "spatial locality", "temporal locality", "cache miss", "row major traversal", "prefetching", "tiling"],
      items: [
        { id: "CacheLocality/practice-1", title: "How many cache lines does a scan touch", kind: 'Practice', level: "Easy" },
        { id: "CacheLocality/practice-2", title: "Simulate an LRU cache: sequential versus strided", kind: 'Practice', level: "Medium" },
        { id: "CacheLocality/practice-3", title: "Row order versus column order on a matrix", kind: 'Practice', level: "Hard" },
        { id: "CacheLocality/practice-4", title: "Blocked (tiled) matrix transpose", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Indexing", title: "Array Indexing Mechanics", emoji: "🔢", group: "Phase 1: Foundations and Memory Architecture", keywords: ["zero based", "one based", "negative index", "off by one", "modulo", "circular index", "bounds check"],
      items: [
        { id: "Indexing/practice-1", title: "The k-th item and the k-th from the end", kind: 'Practice', level: "Easy" },
        { id: "Indexing/practice-2", title: "Circular indexing with negative offsets", kind: 'Practice', level: "Medium" },
        { id: "Indexing/practice-3", title: "Fixed point: find i where a[i] equals i", kind: 'Practice', level: "Hard" },
        { id: "Indexing/practice-4", title: "First missing positive using indexes as storage", kind: 'Practice', level: "Expert" }
      ] },
    { id: "StaticArray", title: "Static Arrays", emoji: "🧱", group: "Phase 2: Fundamental Types and Core Operations", keywords: ["fixed size", "capacity", "int[]", "ring buffer", "circular queue", "overflow", "k stacks"],
      items: [
        { id: "StaticArray/practice-1", title: "Smallest, largest and total in one pass", kind: 'Practice', level: "Easy" },
        { id: "StaticArray/practice-2", title: "Merge two sorted arrays inside a fixed buffer", kind: 'Practice', level: "Medium" },
        { id: "StaticArray/practice-3", title: "Circular queue (ring buffer) in a fixed array", kind: 'Practice', level: "Hard" },
        { id: "StaticArray/practice-4", title: "k stacks sharing one fixed array", kind: 'Practice', level: "Expert" }
      ] },
    { id: "DynamicArray", title: "Dynamic Arrays and Amortized Cost", emoji: "🎈", group: "Phase 2: Fundamental Types and Core Operations", keywords: ["ArrayList", "vector", "resize", "doubling", "amortized analysis", "capacity", "append"],
      items: [
        { id: "DynamicArray/practice-1", title: "Count the resizes and the copies", kind: 'Practice', level: "Easy" },
        { id: "DynamicArray/practice-2", title: "Grow and shrink without thrashing", kind: 'Practice', level: "Medium" },
        { id: "DynamicArray/practice-3", title: "A growable deque on a circular buffer", kind: 'Practice', level: "Hard" },
        { id: "DynamicArray/practice-4", title: "Gap buffer for a text editor", kind: 'Practice', level: "Expert" }
      ] },
    { id: "BasicOps", title: "Insertion, Deletion and Shifting", emoji: "↔️", group: "Phase 2: Fundamental Types and Core Operations", keywords: ["insert", "delete", "shift", "swap delete", "in place", "remove element", "rotate"],
      items: [
        { id: "BasicOps/practice-1", title: "Remove every copy of a value in place", kind: 'Practice', level: "Easy" },
        { id: "BasicOps/practice-2", title: "Move all zeros to the end", kind: 'Practice', level: "Medium" },
        { id: "BasicOps/practice-3", title: "Rotate an array by k steps in place", kind: 'Practice', level: "Hard" },
        { id: "BasicOps/practice-4", title: "Set with O(1) insert, delete and random pick", kind: 'Practice', level: "Expert" }
      ] },
    { id: "MultiDim", title: "Multi-Dimensional Arrays", emoji: "🔲", group: "Phase 2: Fundamental Types and Core Operations", keywords: ["2D array", "matrix", "row major", "column major", "grid", "flatten", "reshape"],
      items: [
        { id: "MultiDim/practice-1", title: "Transpose a rectangular matrix", kind: 'Practice', level: "Easy" },
        { id: "MultiDim/practice-2", title: "Reshape a matrix using the flattened index", kind: 'Practice', level: "Medium" },
        { id: "MultiDim/practice-3", title: "Binary search a sorted matrix as if it were 1D", kind: 'Practice', level: "Hard" },
        { id: "MultiDim/practice-4", title: "Game of Life in place", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Jagged", title: "Jagged Arrays", emoji: "🪜", group: "Phase 2: Fundamental Types and Core Operations", keywords: ["array of arrays", "ragged array", "pascal triangle", "CSR", "compressed sparse row", "adjacency list"],
      items: [
        { id: "Jagged/practice-1", title: "Pascal's triangle", kind: 'Practice', level: "Easy" },
        { id: "Jagged/practice-2", title: "Iterator over a jagged array with empty rows", kind: 'Practice', level: "Medium" },
        { id: "Jagged/practice-3", title: "Diagonal traversal of a jagged array", kind: 'Practice', level: "Hard" },
        { id: "Jagged/practice-4", title: "Pack a jagged array into CSR form", kind: 'Practice', level: "Expert" }
      ] },
    { id: "LinearSearch", title: "Linear Search", emoji: "🔦", group: "Phase 3: Classical Searching and Sorting", keywords: ["sequential search", "scan", "sentinel", "find", "indexOf", "unsorted", "O(n)"],
      items: [
        { id: "LinearSearch/practice-1", title: "First and last position of a value", kind: 'Practice', level: "Easy" },
        { id: "LinearSearch/practice-2", title: "Second largest distinct value in one pass", kind: 'Practice', level: "Medium" },
        { id: "LinearSearch/practice-3", title: "Staircase search in a row and column sorted matrix", kind: 'Practice', level: "Hard" },
        { id: "LinearSearch/practice-4", title: "Self-organizing list with move-to-front", kind: 'Practice', level: "Expert" }
      ] },
    { id: "BinarySearch", title: "Binary Search", emoji: "🎯", group: "Phase 3: Classical Searching and Sorting", keywords: ["divide and conquer", "lower bound", "upper bound", "bisect", "sorted array", "O(log n)", "search space"],
      items: [
        { id: "BinarySearch/practice-1", title: "Search insert position", kind: 'Practice', level: "Easy" },
        { id: "BinarySearch/practice-2", title: "First and last position in a sorted array", kind: 'Practice', level: "Medium" },
        { id: "BinarySearch/practice-3", title: "Search in a rotated sorted array", kind: 'Practice', level: "Hard" },
        { id: "BinarySearch/practice-4", title: "Median of two sorted arrays", kind: 'Practice', level: "Expert" }
      ] },
    { id: "SimpleSorts", title: "Bubble, Insertion and Selection Sort", emoji: "🫧", group: "Phase 3: Classical Searching and Sorting", keywords: ["bubble sort", "insertion sort", "selection sort", "stable sort", "in place", "O(n^2)", "adaptive"],
      items: [
        { id: "SimpleSorts/practice-1", title: "Bubble sort and count the swaps", kind: 'Practice', level: "Easy" },
        { id: "SimpleSorts/practice-2", title: "Stable sort of people by height", kind: 'Practice', level: "Medium" },
        { id: "SimpleSorts/practice-3", title: "Minimum swaps to sort", kind: 'Practice', level: "Hard" },
        { id: "SimpleSorts/practice-4", title: "Pancake sorting", kind: 'Practice', level: "Expert" }
      ] },
    { id: "AdvancedSorts", title: "Merge Sort and Quick Sort", emoji: "🚀", group: "Phase 3: Classical Searching and Sorting", keywords: ["merge sort", "quick sort", "divide and conquer", "pivot", "partition", "O(n log n)", "stable", "quickselect"],
      items: [
        { id: "AdvancedSorts/practice-1", title: "Merge two sorted arrays", kind: 'Practice', level: "Easy" },
        { id: "AdvancedSorts/practice-2", title: "k-th largest element with Quickselect", kind: 'Practice', level: "Medium" },
        { id: "AdvancedSorts/practice-3", title: "Count inversions with merge sort", kind: 'Practice', level: "Hard" },
        { id: "AdvancedSorts/practice-4", title: "Count of smaller numbers after each element", kind: 'Practice', level: "Expert" }
      ] },
    { id: "TwoPointers", title: "Two Pointers Technique", emoji: "👉", group: "Phase 4: Foundational Techniques and Patterns", keywords: ["opposite ends", "fast and slow", "pair sum", "palindrome", "remove duplicates", "container with most water", "3sum"],
      items: [
        { id: "TwoPointers/practice-1", title: "Valid palindrome", kind: 'Practice', level: "Easy" },
        { id: "TwoPointers/practice-2", title: "3Sum: all unique triplets that add to zero", kind: 'Practice', level: "Medium" },
        { id: "TwoPointers/practice-3", title: "Trapping rain water", kind: 'Practice', level: "Hard" },
        { id: "TwoPointers/practice-4", title: "Find the duplicate with fast and slow pointers", kind: 'Practice', level: "Expert" }
      ] },
    { id: "SlidingWindow", title: "Sliding Window", emoji: "🪟", group: "Phase 4: Foundational Techniques and Patterns", keywords: ["fixed window", "variable window", "subarray", "substring", "running sum", "longest substring", "minimum window"],
      items: [
        { id: "SlidingWindow/practice-1", title: "Maximum average of k neighbours", kind: 'Practice', level: "Easy" },
        { id: "SlidingWindow/practice-2", title: "Longest substring without repeating characters", kind: 'Practice', level: "Medium" },
        { id: "SlidingWindow/practice-3", title: "Minimum window containing all characters", kind: 'Practice', level: "Hard" },
        { id: "SlidingWindow/practice-4", title: "Subarrays with exactly K distinct values", kind: 'Practice', level: "Expert" }
      ] },
    { id: "PrefixSum", title: "Prefix Sums and Difference Arrays", emoji: "➕", group: "Phase 4: Foundational Techniques and Patterns", keywords: ["cumulative sum", "range sum query", "difference array", "subarray sum equals k", "running total"],
      items: [
        { id: "PrefixSum/practice-1", title: "Range sum queries on a fixed array", kind: 'Practice', level: "Easy" },
        { id: "PrefixSum/practice-2", title: "Count subarrays that sum to k", kind: 'Practice', level: "Medium" },
        { id: "PrefixSum/practice-3", title: "Car pooling with a difference array", kind: 'Practice', level: "Hard" },
        { id: "PrefixSum/practice-4", title: "Shortest subarray with sum at least K (negatives allowed)", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Frequency", title: "Frequency Arrays", emoji: "🧮", group: "Phase 4: Foundational Techniques and Patterns", keywords: ["counting", "histogram", "hash map", "anagram", "count array", "counting sort", "radix sort"],
      items: [
        { id: "Frequency/practice-1", title: "Valid anagram", kind: 'Practice', level: "Easy" },
        { id: "Frequency/practice-2", title: "First character that appears only once", kind: 'Practice', level: "Medium" },
        { id: "Frequency/practice-3", title: "Find all anagrams of a pattern in a text", kind: 'Practice', level: "Hard" },
        { id: "Frequency/practice-4", title: "Radix sort built from counting arrays", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Kadane", title: "Kadane's Algorithm", emoji: "📈", group: "Phase 5: Advanced Algorithmic Patterns", keywords: ["maximum subarray", "dynamic programming", "running sum", "max product subarray", "circular subarray"],
      items: [
        { id: "Kadane/practice-1", title: "Maximum subarray sum", kind: 'Practice', level: "Easy" },
        { id: "Kadane/practice-2", title: "Maximum product subarray", kind: 'Practice', level: "Medium" },
        { id: "Kadane/practice-3", title: "Maximum circular subarray sum", kind: 'Practice', level: "Hard" },
        { id: "Kadane/practice-4", title: "Maximum sum rectangle in a matrix", kind: 'Practice', level: "Expert" }
      ] },
    { id: "DutchFlag", title: "Dutch National Flag", emoji: "🇳🇱", group: "Phase 5: Advanced Algorithmic Patterns", keywords: ["three way partition", "sort colors", "0 1 2", "low mid high", "in place partition", "Dijkstra"],
      items: [
        { id: "DutchFlag/practice-1", title: "Separate 0s and 1s", kind: 'Practice', level: "Easy" },
        { id: "DutchFlag/practice-2", title: "Sort colours", kind: 'Practice', level: "Medium" },
        { id: "DutchFlag/practice-3", title: "Three-way partition around a range", kind: 'Practice', level: "Hard" },
        { id: "DutchFlag/practice-4", title: "Wiggle sort II", kind: 'Practice', level: "Expert" }
      ] },
    { id: "BoyerMoore", title: "Boyer-Moore Majority Vote", emoji: "🗳️", group: "Phase 5: Advanced Algorithmic Patterns", keywords: ["majority element", "voting algorithm", "candidate", "n/2", "n/3", "Misra Gries", "streaming"],
      items: [
        { id: "BoyerMoore/practice-1", title: "Majority element", kind: 'Practice', level: "Easy" },
        { id: "BoyerMoore/practice-2", title: "Every value appearing more than n/3 times", kind: 'Practice', level: "Medium" },
        { id: "BoyerMoore/practice-3", title: "Minimum index of a valid split", kind: 'Practice', level: "Hard" },
        { id: "BoyerMoore/practice-4", title: "Values above n/k with k − 1 counters (Misra-Gries)", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Matrix", title: "Matrix Manipulations", emoji: "🔄", group: "Phase 5: Advanced Algorithmic Patterns", keywords: ["rotate matrix", "transpose", "spiral order", "diagonal", "in place", "layers", "rings"],
      items: [
        { id: "Matrix/practice-1", title: "Sum of both diagonals", kind: 'Practice', level: "Easy" },
        { id: "Matrix/practice-2", title: "Fill a matrix in spiral order", kind: 'Practice', level: "Medium" },
        { id: "Matrix/practice-3", title: "Rotate 90° in place, ring by ring", kind: 'Practice', level: "Hard" },
        { id: "Matrix/practice-4", title: "Rotate every ring of a grid by k steps", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Monotonic", title: "Monotonic Stack and Queue", emoji: "🏔️", group: "Phase 6: Expert Optimization and Data Structures", keywords: ["monotonic stack", "monotonic queue", "next greater element", "sliding window maximum", "daily temperatures", "histogram"],
      items: [
        { id: "Monotonic/practice-1", title: "Daily temperatures", kind: 'Practice', level: "Easy" },
        { id: "Monotonic/practice-2", title: "Next greater element in a circular array", kind: 'Practice', level: "Medium" },
        { id: "Monotonic/practice-3", title: "Largest rectangle in a histogram", kind: 'Practice', level: "Hard" },
        { id: "Monotonic/practice-4", title: "Largest rectangle of 1s in a binary matrix", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Prefix2D", title: "Two-Dimensional Prefix Sum", emoji: "🗺️", group: "Phase 6: Expert Optimization and Data Structures", keywords: ["2D prefix sum", "summed area table", "integral image", "rectangle sum", "inclusion exclusion", "matrix block sum"],
      items: [
        { id: "Prefix2D/practice-1", title: "Rectangle sum queries", kind: 'Practice', level: "Easy" },
        { id: "Prefix2D/practice-2", title: "Matrix block sum", kind: 'Practice', level: "Medium" },
        { id: "Prefix2D/practice-3", title: "Largest square with sum at most a threshold", kind: 'Practice', level: "Hard" },
        { id: "Prefix2D/practice-4", title: "Number of sub-matrices that sum to a target", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Intervals", title: "Interval Overlapping Patterns", emoji: "📅", group: "Phase 6: Expert Optimization and Data Structures", keywords: ["merge intervals", "meeting rooms", "overlap", "sweep line", "insert interval", "greedy", "scheduling"],
      items: [
        { id: "Intervals/practice-1", title: "Can one person attend every meeting", kind: 'Practice', level: "Easy" },
        { id: "Intervals/practice-2", title: "Insert an interval into a sorted list", kind: 'Practice', level: "Medium" },
        { id: "Intervals/practice-3", title: "Minimum number of meeting rooms", kind: 'Practice', level: "Hard" },
        { id: "Intervals/practice-4", title: "Cover [0, T] with the fewest clips", kind: 'Practice', level: "Expert" }
      ] },
    { id: "SqrtDecomp", title: "Square Root Decomposition and Mo’s Algorithm", emoji: "🧱", group: "Phase 6: Expert Optimization and Data Structures", keywords: ["square root decomposition", "blocks", "range query", "point update", "Mo algorithm", "offline queries", "lazy"],
      items: [
        { id: "SqrtDecomp/practice-1", title: "Range minimum with √n blocks", kind: 'Practice', level: "Easy" },
        { id: "SqrtDecomp/practice-2", title: "Range sums with point updates", kind: 'Practice', level: "Medium" },
        { id: "SqrtDecomp/practice-3", title: "Range add and range sum with lazy blocks", kind: 'Practice', level: "Hard" },
        { id: "SqrtDecomp/practice-4", title: "Mo's algorithm: equal pairs in a range", kind: 'Practice', level: "Expert" }
      ] },
    { id: "Trees", title: "Fenwick Trees and Segment Trees", emoji: "🌳", group: "Phase 6: Expert Optimization and Data Structures", keywords: ["fenwick tree", "binary indexed tree", "segment tree", "lazy propagation", "range sum", "range minimum", "O(log n)"],
      items: [
        { id: "Trees/practice-1", title: "Fenwick tree: sums with updates", kind: 'Practice', level: "Easy" },
        { id: "Trees/practice-2", title: "Segment tree for range minimum", kind: 'Practice', level: "Medium" },
        { id: "Trees/practice-3", title: "Count inversions with a Fenwick tree", kind: 'Practice', level: "Hard" },
        { id: "Trees/practice-4", title: "Segment tree with lazy propagation", kind: 'Practice', level: "Expert" }
      ] }
  ];
}

function javaModules() {
  return [
    {
      id: "basics", title: "Java Basics", emoji: "🌱",
      topics: [
      {
        id: "language-fundamentals", title: "Language Fundamentals", emoji: "🧱",
        page: "content/java/language-fundamentals.html",
        summary: "Identifiers, reserved words, the 8 primitive types, literals, arrays, variables, var-args, main() and command line arguments.",
        keywords: ["identifier", "keyword", "reserved words", "data types", "primitive", "byte range", "literal", "octal", "hexadecimal", "binary literal", "array", "jagged array", "anonymous array", "instance variable", "static variable", "local variable", "var-args", "main method", "command line arguments", "coding standards", "java bean"],
        added: '2026-10-19',
        sections: [
          { id: "identifiers", title: "Identifiers", emoji: "🏷️", group: "Chapter 1", keywords: ["naming rules", "valid identifier", "case sensitive"] },
          { id: "reserved-words", title: "Reserved words", emoji: "🚫", group: "Chapter 1", keywords: ["keywords", "53 reserved words", "goto", "const", "true false null"] },
          { id: "data-types", title: "The 8 primitive data types", emoji: "🔢", group: "Chapter 1", keywords: ["byte short int long float double char boolean", "range", "size", "default value", "two's complement"] },
          { id: "literals", title: "Literals", emoji: "✍️", group: "Chapter 1", keywords: ["integral literal", "octal", "hexadecimal", "binary", "underscore", "long suffix", "float suffix", "char literal", "unicode", "escape sequence"] },
          { id: "conversions", title: "Widening and narrowing", emoji: "↔️", group: "Chapter 1", keywords: ["type promotion", "widening", "narrowing", "implicit conversion", "compile time constant"] },
          { id: "arrays", title: "Arrays", emoji: "📦", group: "Chapter 1", keywords: ["array declaration", "array creation", "default values", "multi dimensional", "jagged array", "length", "anonymous array", "ArrayIndexOutOfBoundsException", "NegativeArraySizeException"] },
          { id: "variables", title: "Types of variables", emoji: "🗃️", group: "Chapter 1", keywords: ["instance variable", "static variable", "local variable", "default value", "primitive variable", "reference variable", "scope"] },
          { id: "var-args", title: "Var-arg methods", emoji: "🎒", group: "Chapter 1", keywords: ["variable arguments", "varargs", "int...", "ellipsis", "var-arg priority"] },
          { id: "main-method", title: "The main() method", emoji: "🚪", group: "Chapter 1", keywords: ["public static void main", "String[] args", "NoSuchMethodError", "main overloading", "main inheritance"] },
          { id: "command-line", title: "Command line arguments", emoji: "⌨️", group: "Chapter 1", keywords: ["args", "args.length", "String args", "parseInt", "ArrayIndexOutOfBoundsException"] },
          { id: "coding-standards", title: "Java coding standards", emoji: "📏", group: "Chapter 1", keywords: ["naming conventions", "camelCase", "PascalCase", "constants", "java bean", "getter", "setter", "listener"] }
        ]
      },
      {
        id: "operators", title: "Operators and Assignments", emoji: "➗",
        page: "content/java/operators.html",
        summary: "Increment and decrement, arithmetic rules, string joining, comparisons, instanceof, bitwise and short-circuit operators, casting, assignments, the ternary operator and evaluation order.",
        keywords: ["operator", "increment", "decrement", "pre increment", "post increment", "arithmetic", "ArithmeticException", "NaN", "Infinity", "string concatenation", "relational", "equality", "instanceof", "bitwise", "xor", "complement", "shift", "short circuit", "type casting", "compound assignment", "ternary", "conditional operator", "operator precedence", "evaluation order"],
        added: '2026-10-19',
        sections: [
          { id: "increment-decrement", title: "Increment and decrement", emoji: "➕", group: "Chapter 2", keywords: ["++", "--", "pre increment", "post increment", "x++ vs ++x"] },
          { id: "arithmetic", title: "Arithmetic operators", emoji: "🧮", group: "Chapter 2", keywords: ["+ - * / %", "result type", "ArithmeticException", "Infinity", "NaN", "modulo", "remainder"] },
          { id: "string-concat", title: "String concatenation", emoji: "🔗", group: "Chapter 2", keywords: ["+ operator overloaded", "string concatenation", "left to right"] },
          { id: "relational", title: "Relational operators", emoji: "📐", group: "Chapter 2", keywords: [] },
          { id: "equality", title: "Equality operators", emoji: "⚖️", group: "Chapter 2", keywords: ["==", "!=", "reference comparison", "incomparable types"] },
          { id: "instanceof", title: "The instanceof operator", emoji: "🔎", group: "Chapter 2", keywords: ["instanceof", "type check", "pattern matching for instanceof"] },
          { id: "bitwise", title: "Bitwise and boolean operators", emoji: "💡", group: "Chapter 2", keywords: [] },
          { id: "short-circuit", title: "Short-circuit operators", emoji: "⚡", group: "Chapter 2", keywords: ["&&", "||", "short circuit", "lazy evaluation", "& vs &&"] },
          { id: "type-casting", title: "Type casting", emoji: "🎭", group: "Chapter 2", keywords: ["implicit casting", "explicit casting", "widening", "narrowing", "loss of precision"] },
          { id: "assignment", title: "Assignment operators", emoji: "📝", group: "Chapter 2", keywords: ["=", "chained assignment", "compound assignment", "+=", "implicit cast in compound assignment"] },
          { id: "conditional", title: "The conditional operator", emoji: "❓", group: "Chapter 2", keywords: ["ternary operator", "?:", "nested ternary"] },
          { id: "precedence", title: "new, [ ] and the evaluation order", emoji: "🧭", group: "Chapter 2", keywords: ["new operator", "array operator", "operator precedence", "evaluation order", "left to right"] }
        ]
      },
      {
        id: "flow-control", title: "Flow Control", emoji: "🔀",
        page: "content/java/flow-control.html",
        summary: "if else, switch (classic and modern), while, do while, for, for-each, break, continue and labels, with every compile-time trap.",
        keywords: ["if else", "switch", "fall through", "switch expression", "arrow case", "yield", "pattern matching switch", "while", "do while", "for loop", "for each", "enhanced for", "break", "continue", "label", "labeled break", "unreachable statement", "infinite loop"],
        added: '2026-10-19',
        sections: [
          { id: "overview", title: "Three families of flow control", emoji: "🗺️", group: "Chapter 3", keywords: ["selection statements", "iterative statements", "transfer statements"] },
          { id: "if-else", title: "if else", emoji: "🛣️", group: "Chapter 3", keywords: ["if statement", "else", "boolean condition", "curly braces", "dangling else"] },
          { id: "switch", title: "switch", emoji: "🎛️", group: "Chapter 3", keywords: ["switch statement", "case label", "default", "fall through", "compile time constant", "String switch", "enum switch"] },
          { id: "while", title: "while loop", emoji: "🔁", group: "Chapter 3", keywords: ["while loop", "unknown iterations", "unreachable statement", "infinite loop"] },
          { id: "do-while", title: "do while loop", emoji: "🔂", group: "Chapter 3", keywords: ["do while", "at least once", "semicolon after while"] },
          { id: "for", title: "for loop", emoji: "🔢", group: "Chapter 3", keywords: ["for loop", "initialization", "condition", "increment", "optional parts", "multiple variables"] },
          { id: "for-each", title: "for-each loop", emoji: "🍡", group: "Chapter 3", keywords: ["enhanced for loop", "for each", "arrays", "Iterable", "collections"] },
          { id: "break", title: "break", emoji: "🛑", group: "Chapter 3", keywords: ["break statement", "exit loop", "break inside switch", "labeled block"] },
          { id: "continue", title: "continue", emoji: "⏭️", group: "Chapter 3", keywords: ["continue statement", "skip iteration"] },
          { id: "labels", title: "Labeled break and continue", emoji: "🏷️", group: "Chapter 3", keywords: ["labeled break", "labeled continue", "nested loops", "outer loop"] }
        ]
      }
      ]
    },
    {
      id: "oop", title: "Object Oriented Java", emoji: "🧩",
      topics: [
      {
        id: "declarations-access-modifiers", title: "Declarations and Access Modifiers", emoji: "🔐",
        page: "content/java/declarations-access-modifiers.html",
        summary: "Source file structure, import and static import, packages, class and member modifiers, final, abstract, static and friends, interfaces, marker and adapter classes.",
        keywords: ["source file structure", "public class", "import", "wildcard import", "static import", "package", "javac -d", "access modifiers", "public", "private", "protected", "default access", "final", "abstract", "static", "native", "synchronized", "transient", "volatile", "strictfp", "interface", "default method", "marker interface", "adapter class", "abstract class vs interface"],
        added: '2026-10-19',
        sections: [
          { id: "source-file", title: "Java source file structure", emoji: "📄", group: "Chapter 4", keywords: ["public class", "file name", "multiple classes in one file", ".class files"] },
          { id: "import", title: "The import statement", emoji: "📥", group: "Chapter 4", keywords: ["import", "fully qualified name", "explicit import", "implicit import", "wildcard", "java.lang", "ambiguity"] },
          { id: "static-import", title: "Static import", emoji: "⚡", group: "Chapter 4", keywords: ["import static", "Math.sqrt", "out.println", "static import ambiguity", "precedence"] },
          { id: "packages", title: "Packages", emoji: "📦", group: "Chapter 4", keywords: ["package statement", "reverse domain name", "javac -d", "folder structure", "fully qualified name"] },
          { id: "class-modifiers", title: "Class level modifiers", emoji: "🏛️", group: "Chapter 4", keywords: ["public class", "default class", "final class", "abstract class", "strictfp class", "top level class modifiers"] },
          { id: "final", title: "final", emoji: "🔒", group: "Chapter 4", keywords: ["final class", "final method", "final variable", "blank final", "final instance variable", "final static variable"] },
          { id: "abstract", title: "abstract", emoji: "🧩", group: "Chapter 4", keywords: ["abstract method", "abstract class", "illegal combination", "partial implementation"] },
          { id: "member-modifiers", title: "public, protected, default and private", emoji: "👀", group: "Chapter 4", keywords: ["access modifiers", "visibility table", "protected access", "package private", "private members"] },
          { id: "other-modifiers", title: "static, native, synchronized, transient, volatile, strictfp", emoji: "🧰", group: "Chapter 4", keywords: ["static method", "static variable", "instance access from static", "native method", "synchronized method", "transient field", "volatile field", "strictfp"] },
          { id: "interfaces", title: "Interfaces", emoji: "🔌", group: "Chapter 4", keywords: ["interface", "implements", "extends", "interface methods public abstract", "interface variables public static final", "default method", "static method", "private method"] },
          { id: "interface-conflicts", title: "Naming conflicts in interfaces", emoji: "⚔️", group: "Chapter 4", keywords: ["method naming conflict", "variable naming conflict", "same signature", "different return type", "ambiguous variable"] },
          { id: "marker-adapter", title: "Marker interfaces and adapter classes", emoji: "🏷️", group: "Chapter 4", keywords: ["marker interface", "tag interface", "Serializable", "Cloneable", "RandomAccess", "adapter class", "functional interface"] },
          { id: "abstract-vs-interface", title: "Abstract class or interface", emoji: "🤔", group: "Chapter 4", keywords: ["abstract class vs interface", "difference", "when to use"] }
        ]
      },
      {
        id: "oops-concepts", title: "OOP Concepts", emoji: "🧬",
        page: "content/java/oops-concepts.html",
        summary: "Data hiding, abstraction, encapsulation, IS-A and HAS-A, overloading, overriding, polymorphism, static and instance control flow, constructors, singletons, coupling, cohesion and type casting.",
        keywords: ["oops", "object oriented", "data hiding", "abstraction", "encapsulation", "tightly encapsulated", "inheritance", "is-a", "has-a", "composition", "aggregation", "method signature", "overloading", "overriding", "covariant return", "method hiding", "polymorphism", "static control flow", "instance control flow", "static block", "instance block", "constructor", "default constructor", "super", "this", "singleton", "coupling", "cohesion", "type casting", "ClassCastException"],
        added: '2026-10-19',
        sections: [
          { id: "data-hiding", title: "Data hiding", emoji: "🙈", group: "Chapter 5", keywords: ["private fields", "validation", "getter setter"] },
          { id: "abstraction", title: "Abstraction", emoji: "🎭", group: "Chapter 5", keywords: ["hide implementation", "interface", "abstract class", "ATM"] },
          { id: "encapsulation", title: "Encapsulation", emoji: "💊", group: "Chapter 5", keywords: ["encapsulation", "tightly encapsulated class", "getter", "setter"] },
          { id: "is-a", title: "IS-A relationship (inheritance)", emoji: "👨‍👧", group: "Chapter 5", keywords: ["inheritance", "extends", "parent reference child object", "multiple inheritance", "cyclic inheritance", "Object class"] },
          { id: "has-a", title: "HAS-A relationship", emoji: "🚗", group: "Chapter 5", keywords: ["composition", "aggregation", "has-a", "association"] },
          { id: "method-signature", title: "Method signature", emoji: "✒️", group: "Chapter 5", keywords: ["method name", "argument types", "return type not part of signature"] },
          { id: "overloading", title: "Overloading", emoji: "🎚️", group: "Chapter 5", keywords: ["method overloading", "compile time polymorphism", "automatic promotion", "most specific method", "ambiguity", "null argument"] },
          { id: "overriding", title: "Overriding", emoji: "🔁", group: "Chapter 5", keywords: ["method overriding", "runtime polymorphism", "dynamic method dispatch", "covariant return type", "method hiding", "weaker access", "checked exception rule"] },
          { id: "overload-vs-override", title: "Overloading versus overriding", emoji: "🆚", group: "Chapter 5", keywords: ["difference between overloading and overriding"] },
          { id: "polymorphism", title: "Polymorphism", emoji: "🦎", group: "Chapter 5", keywords: ["polymorphism", "compile time", "runtime", "parent reference", "many forms"] },
          { id: "static-control-flow", title: "Static control flow", emoji: "🧊", group: "Chapter 5", keywords: ["static block", "static variable", "class loading", "RIWO", "read indirectly write only", "illegal forward reference"] },
          { id: "instance-control-flow", title: "Instance control flow", emoji: "🏗️", group: "Chapter 5", keywords: ["instance block", "instance variable initialization", "constructor order", "object creation"] },
          { id: "constructors", title: "Constructors", emoji: "🔨", group: "Chapter 5", keywords: ["constructor rules", "default constructor", "super()", "this()", "constructor overloading", "recursive constructor invocation"] },
          { id: "singleton", title: "Singleton classes", emoji: "☝️", group: "Chapter 5", keywords: ["singleton pattern", "private constructor", "Runtime.getRuntime", "factory method", "eager", "lazy"] },
          { id: "coupling-cohesion", title: "Coupling and cohesion", emoji: "🧷", group: "Chapter 5", keywords: ["loose coupling", "tight coupling", "high cohesion", "low cohesion"] },
          { id: "type-casting", title: "Object type casting", emoji: "🎭", group: "Chapter 5", keywords: ["downcasting", "upcasting", "ClassCastException", "compile time check", "runtime check"] }
        ]
      },
      {
        id: "inner-classes", title: "Inner Classes", emoji: "🪆",
        page: "content/java/inner-classes.html",
        summary: "Normal inner classes, method local inner classes, anonymous inner classes and static nested classes, with Outer.this, effectively final locals and the .class files they create.",
        keywords: ["inner class", "nested class", "regular inner class", "Outer.Inner", "new Outer().new Inner()", "Outer.this", "method local inner class", "effectively final", "anonymous inner class", "static nested class", "Outer$Inner.class", "Map.Entry", "lambda"],
        added: '2026-10-19',
        sections: [
          { id: "why-inner", title: "Why inner classes exist", emoji: "🫀", group: "Chapter 6", keywords: ["inner class purpose", "has-a without existence", "four kinds"] },
          { id: "normal-inner", title: "Normal inner classes", emoji: "📥", group: "Chapter 6", keywords: ["regular inner class", "Outer.Inner", "new Outer().new Inner()", "Outer.this", "Outer$Inner.class"] },
          { id: "method-local", title: "Method local inner classes", emoji: "🧪", group: "Chapter 6", keywords: ["method local inner class", "effectively final", "local variable access", "final abstract only"] },
          { id: "anonymous", title: "Anonymous inner classes", emoji: "🎭", group: "Chapter 6", keywords: ["anonymous inner class", "extends a class", "implements an interface", "argument", "Thread", "Runnable", "lambda", "Main$1.class"] },
          { id: "general-vs-anonymous", title: "Normal class versus anonymous class", emoji: "🆚", group: "Chapter 6", keywords: ["anonymous class limitations", "constructors", "extends and implements"] },
          { id: "static-nested", title: "Static nested classes", emoji: "🧊", group: "Chapter 6", keywords: ["static nested class", "no outer object needed", "Outer.Nested", "static members only"] },
          { id: "comparison", title: "Normal inner versus static nested", emoji: "📊", group: "Chapter 6", keywords: ["difference normal inner class static nested class"] },
          { id: "combinations", title: "Classes and interfaces inside each other", emoji: "🧱", group: "Chapter 6", keywords: ["interface inside class", "class inside interface", "nested interface", "Map.Entry"] }
        ]
      }
      ]
    },
    {
      id: "apis", title: "Core Java APIs", emoji: "🧰",
      topics: [
      {
        id: "java-lang", title: "java.lang: Object, String and Wrappers", emoji: "🧵",
        page: "content/java/java-lang.html",
        summary: "The Object class and its methods, String immutability and the string constant pool, StringBuffer and StringBuilder, wrapper classes, autoboxing and immutable classes.",
        keywords: ["java.lang", "Object class", "toString", "hashCode", "equals", "== vs equals", "clone", "shallow copy", "deep copy", "getClass", "String", "immutable", "string constant pool", "SCP", "intern", "StringBuffer", "StringBuilder", "capacity", "wrapper class", "valueOf", "parseInt", "xxxValue", "Integer cache", "autoboxing", "unboxing", "immutable class"],
        added: '2026-10-19',
        sections: [
          { id: "object-class", title: "The Object class", emoji: "🌳", group: "Chapter 7", keywords: ["java.lang.Object", "root class", "methods of Object"] },
          { id: "tostring", title: "toString()", emoji: "📝", group: "Chapter 7", keywords: ["toString", "ClassName@hashCode", "override toString", "println calls toString"] },
          { id: "hashcode", title: "hashCode()", emoji: "#️⃣", group: "Chapter 7", keywords: ["hashCode", "hash based collections", "HashMap bucket", "override hashCode"] },
          { id: "equals", title: "equals() and ==", emoji: "⚖️", group: "Chapter 7", keywords: ["equals", "==", "content comparison", "reference comparison", "equals hashCode contract", "Objects.equals"] },
          { id: "clone", title: "clone(): shallow and deep copies", emoji: "🐑", group: "Chapter 7", keywords: ["clone", "Cloneable", "shallow cloning", "deep cloning"] },
          { id: "getclass", title: "getClass()", emoji: "🔍", group: "Chapter 7", keywords: ["getClass", "runtime class", "reflection", "Class object"] },
          { id: "string-immutable", title: "String is immutable", emoji: "🧊", group: "Chapter 7", keywords: ["immutable", "String concat", "mutable StringBuffer", "String vs StringBuffer"] },
          { id: "string-pool", title: "The string constant pool", emoji: "🏊", group: "Chapter 7", keywords: ["string constant pool", "SCP", "literal", "new String", "intern", "number of objects created", "compile time constant"] },
          { id: "string-methods", title: "Important String methods", emoji: "🛠️", group: "Chapter 7", keywords: ["charAt", "length", "substring", "indexOf", "lastIndexOf", "replace", "toUpperCase", "trim", "strip", "split", "join", "equalsIgnoreCase", "isEmpty", "isBlank", "repeat"] },
          { id: "stringbuffer", title: "StringBuffer", emoji: "🧱", group: "Chapter 7", keywords: ["StringBuffer", "mutable", "capacity", "append", "insert", "delete", "reverse", "setLength", "synchronized"] },
          { id: "stringbuilder", title: "StringBuilder and choosing between the three", emoji: "⚡", group: "Chapter 7", keywords: ["StringBuilder", "non synchronized", "method chaining", "String vs StringBuffer vs StringBuilder"] },
          { id: "wrapper-classes", title: "Wrapper classes", emoji: "🎁", group: "Chapter 7", keywords: ["wrapper class", "Byte", "Short", "Integer", "Long", "Float", "Double", "Character", "Boolean", "valueOf", "xxxValue", "parseXxx", "toString radix", "toBinaryString", "Integer cache"] },
          { id: "autoboxing", title: "Autoboxing and unboxing", emoji: "📦", group: "Chapter 7", keywords: ["autoboxing", "auto unboxing", "NullPointerException unboxing", "overloading with boxing", "widening vs boxing vs var-args"] },
          { id: "final-vs-immutable", title: "final versus immutable", emoji: "🔏", group: "Chapter 7", keywords: ["final reference", "immutable object", "how to make immutable class"] }
        ]
      },
      {
        id: "exception-handling", title: "Exception Handling", emoji: "🚨",
        page: "content/java/exception-handling.html",
        summary: "What exceptions are, the runtime stack, the Throwable hierarchy, checked versus unchecked, try catch finally, throw and throws, custom exceptions, the top ten exceptions and modern try-with-resources.",
        keywords: ["exception", "error", "Throwable", "runtime stack", "default exception handler", "stack trace", "checked exception", "unchecked exception", "fully checked", "partially checked", "try catch", "multiple catch", "finally", "return and finally", "System.exit", "final finally finalize", "throw", "throws", "custom exception", "ArithmeticException", "NullPointerException", "ArrayIndexOutOfBoundsException", "ClassCastException", "NumberFormatException", "IllegalArgumentException", "IllegalStateException", "StackOverflowError", "ExceptionInInitializerError", "NoClassDefFoundError", "try with resources", "multi catch", "AutoCloseable"],
        added: '2026-10-19',
        sections: [
          { id: "introduction", title: "What is an exception", emoji: "🌧️", group: "Chapter 8", keywords: ["exception definition", "graceful termination", "exception handling meaning"] },
          { id: "runtime-stack", title: "The runtime stack and default handling", emoji: "📚", group: "Chapter 8", keywords: ["runtime stack", "stack frame", "default exception handler", "exception propagation", "stack trace"] },
          { id: "hierarchy", title: "The exception hierarchy", emoji: "🌳", group: "Chapter 8", keywords: ["Throwable", "Exception", "Error", "RuntimeException", "IOException", "hierarchy"] },
          { id: "checked-unchecked", title: "Checked and unchecked exceptions", emoji: "✅", group: "Chapter 8", keywords: ["checked exception", "unchecked exception", "compiler check", "fully checked", "partially checked"] },
          { id: "try-catch", title: "try and catch", emoji: "🧤", group: "Chapter 8", keywords: ["try block", "catch block", "control flow", "multiple catch", "catch order", "unreachable catch"] },
          { id: "printing", title: "Printing exception information", emoji: "🖨️", group: "Chapter 8", keywords: ["printStackTrace", "toString", "getMessage"] },
          { id: "finally", title: "finally", emoji: "🧹", group: "Chapter 8", keywords: ["finally block", "cleanup", "return vs finally", "System.exit", "finally always executes"] },
          { id: "final-finally-finalize", title: "final, finally and finalize", emoji: "🔤", group: "Chapter 8", keywords: ["final vs finally vs finalize"] },
          { id: "nested", title: "Nested try catch finally", emoji: "🪆", group: "Chapter 8", keywords: ["nested try catch finally", "inner catch", "outer catch", "control flow"] },
          { id: "throw", title: "throw", emoji: "🎯", group: "Chapter 8", keywords: ["throw keyword", "throw new", "throw null", "unreachable after throw"] },
          { id: "throws", title: "throws", emoji: "📤", group: "Chapter 8", keywords: ["throws clause", "delegate responsibility", "checked exception declaration", "never thrown in body"] },
          { id: "custom-exceptions", title: "Custom exceptions", emoji: "🧑‍🎨", group: "Chapter 8", keywords: ["customized exception", "user defined exception", "extends RuntimeException", "extends Exception"] },
          { id: "top-exceptions", title: "The top ten exceptions", emoji: "🔟", group: "Chapter 8", keywords: ["JVM exceptions", "programmatic exceptions", "ArrayIndexOutOfBoundsException", "NullPointerException", "ClassCastException", "StackOverflowError", "NoClassDefFoundError", "ExceptionInInitializerError", "IllegalArgumentException", "NumberFormatException", "IllegalStateException", "AssertionError"] },
          { id: "modern", title: "Modern exception handling", emoji: "🆕", group: "Chapter 8", keywords: ["try with resources", "AutoCloseable", "multi catch", "helpful NullPointerException", "suppressed exceptions"] }
        ]
      },
      {
        id: "enum", title: "Enum", emoji: "🎨",
        page: "content/java/enum.html",
        summary: "Declaring enums, enums in switch, java.lang.Enum, values, ordinal and valueOf, constructors and fields, constant-specific bodies, EnumSet and EnumMap.",
        keywords: ["enum", "enumeration", "named constants", "java.lang.Enum", "values", "ordinal", "valueOf", "name", "enum constructor", "enum fields", "enum methods", "constant specific body", "enum in switch", "EnumSet", "EnumMap", "Enumeration"],
        added: '2026-10-19',
        sections: [
          { id: "intro", title: "Why enums", emoji: "🍽️", group: "Chapter 9", keywords: ["named constants", "type safety", "enum vs int constants"] },
          { id: "declaration", title: "Declaring and using an enum", emoji: "📝", group: "Chapter 9", keywords: ["enum declaration", "public static final constants", "enum toString"] },
          { id: "switch", title: "Enums in switch", emoji: "🎛️", group: "Chapter 9", keywords: ["enum switch", "case labels", "unqualified constant names"] },
          { id: "java-lang-enum", title: "java.lang.Enum", emoji: "🧬", group: "Chapter 9", keywords: ["java.lang.Enum", "enum extends Enum", "enum cannot extend", "enum implements interface", "final"] },
          { id: "values-ordinal", title: "values(), ordinal() and valueOf()", emoji: "🔢", group: "Chapter 9", keywords: ["values method", "ordinal", "valueOf", "name", "compareTo", "IllegalArgumentException"] },
          { id: "constructors-fields", title: "Constructors, fields and methods", emoji: "🏗️", group: "Chapter 9", keywords: ["enum constructor", "enum fields", "enum methods", "private constructor", "constructors run at class loading"] },
          { id: "constant-bodies", title: "Constant-specific bodies", emoji: "🎭", group: "Chapter 9", keywords: ["constant specific class body", "abstract method in enum", "override per constant"] },
          { id: "main-in-enum", title: "An enum with main", emoji: "🚀", group: "Chapter 9", keywords: ["main method in enum", "run enum"] },
          { id: "enum-vs-enumeration", title: "enum, Enum and Enumeration", emoji: "🔤", group: "Chapter 9", keywords: ["enum keyword", "java.lang.Enum class", "java.util.Enumeration interface", "difference"] },
          { id: "enumset-enummap", title: "EnumSet and EnumMap", emoji: "🗃️", group: "Chapter 9", keywords: ["EnumSet", "EnumMap", "bit vector", "fast enum collections"] }
        ]
      },
      {
        id: "regex", title: "Regular Expressions", emoji: "🔍",
        page: "content/java/regex.html",
        summary: "Pattern and Matcher, character classes, predefined classes, quantifiers, split and StringTokenizer, validation of mobile numbers, identifiers and emails, and find and replace with groups.",
        keywords: ["regular expression", "regex", "Pattern", "Matcher", "find", "start", "end", "group", "character class", "predefined character class", "\\d", "\\w", "\\s", "quantifier", "greedy", "split", "StringTokenizer", "matches", "replaceAll", "mobile number validation", "email validation", "capturing group"],
        added: '2026-10-19',
        sections: [
          { id: "intro", title: "What is a regular expression", emoji: "🧩", group: "Chapter 10", keywords: ["regex definition", "pattern", "applications"] },
          { id: "pattern-matcher", title: "Pattern and Matcher", emoji: "🔧", group: "Chapter 10", keywords: ["Pattern.compile", "matcher", "find", "start", "end", "group"] },
          { id: "character-classes", title: "Character classes", emoji: "🔤", group: "Chapter 10", keywords: ["[abc]", "[^abc]", "[a-z]", "[A-Z]", "[0-9]", "ranges", "negation"] },
          { id: "predefined", title: "Predefined character classes", emoji: "🧰", group: "Chapter 10", keywords: ["\\\\s", "\\\\S", "\\\\d", "\\\\D", "\\\\w", "\\\\W", "dot", "word character", "whitespace"] },
          { id: "quantifiers", title: "Quantifiers", emoji: "🔢", group: "Chapter 10", keywords: ["quantifier", "+", "*", "?", "{n}", "{n", "m}", "greedy", "zero length match"] },
          { id: "split", title: "Splitting text", emoji: "✂️", group: "Chapter 10", keywords: ["split", "Pattern.split", "String.split", "StringTokenizer", "delimiter"] },
          { id: "validation", title: "Validating input", emoji: "✅", group: "Chapter 10", keywords: ["String.matches", "mobile number regex", "identifier regex", "email regex", "password rule"] },
          { id: "find-replace", title: "Find, extract and replace", emoji: "🔁", group: "Chapter 10", keywords: ["replaceAll", "capturing group", "group(1)", "backreference", "extract numbers", "read file"] }
        ]
      },
      {
        id: "i18n", title: "Internationalization (I18N)", emoji: "🌍",
        page: "content/java/i18n.html",
        summary: "Locale, NumberFormat for numbers, currency and percentages, lakh and crore grouping, DateFormat styles, modern java.time formatting and ResourceBundle for translated messages.",
        keywords: ["internationalization", "I18N", "localization", "L10N", "Locale", "Locale.of", "NumberFormat", "currency format", "percent format", "Indian number format", "DateFormat", "SHORT MEDIUM LONG FULL", "DateTimeFormatter", "FormatStyle", "ResourceBundle", "ListResourceBundle"],
        added: '2026-10-19',
        sections: [
          { id: "intro", title: "What is I18N", emoji: "🗺️", group: "Chapter 11", keywords: ["internationalization", "localization", "I18N", "L10N"] },
          { id: "locale", title: "Locale", emoji: "📍", group: "Chapter 11", keywords: ["Locale", "language", "country", "Locale.of", "Locale.US", "getDefault", "getDisplayLanguage"] },
          { id: "numberformat", title: "NumberFormat", emoji: "💰", group: "Chapter 11", keywords: ["NumberFormat", "getInstance", "getCurrencyInstance", "getPercentInstance", "format", "parse", "Indian grouping", "lakh crore", "rupee"] },
          { id: "digits", title: "Controlling digits", emoji: "🔢", group: "Chapter 11", keywords: ["setMaximumFractionDigits", "setMinimumFractionDigits", "setMinimumIntegerDigits", "setMaximumIntegerDigits", "rounding"] },
          { id: "dateformat", title: "DateFormat", emoji: "📅", group: "Chapter 11", keywords: ["DateFormat", "getDateInstance", "getDateTimeInstance", "SHORT", "MEDIUM", "LONG", "FULL", "Date"] },
          { id: "java-time", title: "Modern dates with java.time", emoji: "⏰", group: "Chapter 11", keywords: ["LocalDate", "DateTimeFormatter", "FormatStyle", "ofLocalizedDate", "java.time"] },
          { id: "resource-bundle", title: "ResourceBundle: translated messages", emoji: "💬", group: "Chapter 11", keywords: ["ResourceBundle", "ListResourceBundle", "properties file", "getBundle", "fallback"] }
        ]
      }
      ]
    },
    {
      id: "collections", title: "Collections and Generics", emoji: "🧺",
      topics: [
      {
        id: "collections", title: "Collections Framework", emoji: "🧺",
        page: "content/java/collections.html",
        summary: "Arrays versus collections, the key interfaces, List, ArrayList, LinkedList, Vector and Stack, cursors, Set and its classes, Comparable and Comparator, Map and its classes, Navigable collections, Queue and PriorityQueue, the Collections and Arrays utility classes.",
        keywords: ["collections", "collection framework", "Collection vs Collections", "List", "ArrayList", "LinkedList", "Vector", "Stack", "RandomAccess", "Iterator", "ListIterator", "Enumeration", "fail fast", "ConcurrentModificationException", "Set", "HashSet", "LinkedHashSet", "TreeSet", "SortedSet", "NavigableSet", "Comparable", "Comparator", "compareTo", "Map", "HashMap", "LinkedHashMap", "TreeMap", "Hashtable", "IdentityHashMap", "WeakHashMap", "Properties", "Map.Entry", "Queue", "PriorityQueue", "Deque", "Collections.sort", "binarySearch", "Arrays.asList", "List.of", "unmodifiable"],
        added: '2026-10-19',
        sections: [
          { id: "why-collections", title: "Arrays versus collections", emoji: "🧺", group: "Chapter 12", keywords: ["limitations of arrays", "growable", "heterogeneous", "ready made methods"] },
          { id: "framework", title: "The nine key interfaces", emoji: "🗺️", group: "Chapter 12", keywords: ["Collection interface", "List", "Set", "SortedSet", "NavigableSet", "Queue", "Map", "SortedMap", "NavigableMap", "Collection vs Collections"] },
          { id: "list", title: "The List interface", emoji: "📋", group: "Chapter 12", keywords: ["List", "index", "duplicates allowed", "insertion order", "get", "set", "indexOf", "remove index"] },
          { id: "arraylist", title: "ArrayList", emoji: "📦", group: "Chapter 12", keywords: ["ArrayList", "resizable array", "growable", "capacity", "RandomAccess", "retrieval", "synchronizedList"] },
          { id: "linkedlist", title: "LinkedList", emoji: "🔗", group: "Chapter 12", keywords: ["LinkedList", "doubly linked list", "addFirst", "addLast", "getFirst", "removeFirst", "Deque"] },
          { id: "vector-stack", title: "Vector and Stack", emoji: "🥞", group: "Chapter 12", keywords: ["Vector", "legacy class", "synchronized", "Stack", "push", "pop", "peek", "search", "LIFO"] },
          { id: "cursors", title: "Cursors: Enumeration, Iterator, ListIterator", emoji: "👉", group: "Chapter 12", keywords: ["Enumeration", "Iterator", "ListIterator", "hasNext", "next", "remove", "previous", "set", "add", "fail fast", "ConcurrentModificationException"] },
          { id: "set", title: "Set, HashSet, LinkedHashSet and TreeSet", emoji: "🎲", group: "Chapter 12", keywords: ["Set", "no duplicates", "HashSet", "LinkedHashSet", "TreeSet", "add returns false", "null in TreeSet", "SortedSet methods"] },
          { id: "comparable-comparator", title: "Comparable and Comparator", emoji: "⚖️", group: "Chapter 12", keywords: ["Comparable", "compareTo", "natural sorting order", "Comparator", "compare", "custom sorting", "Comparator.comparing", "thenComparing", "reversed"] },
          { id: "map", title: "Map and its classes", emoji: "🗝️", group: "Chapter 12", keywords: ["Map", "key value", "Entry", "put returns old value", "get", "keySet", "values", "entrySet", "HashMap", "LinkedHashMap", "TreeMap", "Hashtable", "IdentityHashMap", "WeakHashMap", "Properties"] },
          { id: "navigable", title: "NavigableSet and NavigableMap", emoji: "🧭", group: "Chapter 12", keywords: ["NavigableSet", "NavigableMap", "floor", "lower", "ceiling", "higher", "pollFirst", "pollLast", "descendingSet", "floorKey", "ceilingKey"] },
          { id: "queue", title: "Queue and PriorityQueue", emoji: "🚶", group: "Chapter 12", keywords: ["Queue", "offer", "poll", "peek", "element", "remove", "PriorityQueue", "heap", "Deque", "ArrayDeque"] },
          { id: "utilities", title: "The Collections and Arrays classes", emoji: "🛠️", group: "Chapter 12", keywords: ["Collections.sort", "Collections.binarySearch", "insertion point", "reverse", "reverseOrder", "max", "frequency", "unmodifiableList", "synchronizedList", "Arrays.sort", "Arrays.binarySearch", "Arrays.asList"] },
          { id: "modern", title: "Modern collection tools", emoji: "🆕", group: "Chapter 12", keywords: ["List.of", "Set.of", "Map.of", "immutable collections", "ConcurrentHashMap", "streams", "sequenced collections"] }
        ]
      },
      {
        id: "generics", title: "Generics", emoji: "🧪",
        page: "content/java/generics.html",
        summary: "Why generics exist, generic classes, the diamond operator, bounded types, generic methods, wildcards with extends and super, type erasure and raw types.",
        keywords: ["generics", "type safety", "type casting", "generic class", "type parameter", "diamond operator", "bounded type", "extends", "multiple bounds", "generic method", "wildcard", "? extends", "? super", "PECS", "type erasure", "raw type", "heap pollution", "ArrayStoreException"],
        added: '2026-10-19',
        sections: [
          { id: "why", title: "Why generics", emoji: "🛡️", group: "Chapter 13", keywords: ["type safety", "type casting problem", "raw collection", "ClassCastException"] },
          { id: "generic-classes", title: "Generic classes", emoji: "🏷️", group: "Chapter 13", keywords: [] },
          { id: "bounded-types", title: "Bounded types", emoji: "📏", group: "Chapter 13", keywords: ["bounded type", "T extends Number", "T extends Runnable", "multiple bounds", "class first then interface"] },
          { id: "generic-methods", title: "Generic methods", emoji: "⚙️", group: "Chapter 13", keywords: ["generic method", "type parameter before return type", "static generic method", "bounded generic method", "type inference"] },
          { id: "wildcards", title: "Wildcards: ?, ? extends and ? super", emoji: "🃏", group: "Chapter 13", keywords: ["wildcard", "unbounded wildcard", "upper bounded wildcard", "lower bounded wildcard", "PECS", "producer extends consumer super"] },
          { id: "polymorphism", title: "Generics and polymorphism", emoji: "🦎", group: "Chapter 13", keywords: [] },
          { id: "type-erasure", title: "Type erasure", emoji: "🧽", group: "Chapter 13", keywords: ["type erasure", "compile time only", "same class at runtime", "name clash", "cannot instantiate T", "instanceof generic"] },
          { id: "raw-types", title: "Raw types and legacy code", emoji: "⚠️", group: "Chapter 13", keywords: ["raw type", "legacy code", "unchecked warning", "heap pollution", "mixing generic and non generic"] }
        ]
      }
      ]
    },
    {
      id: "threads", title: "Multithreading", emoji: "🏃",
      topics: [
      {
        id: "multithreading", title: "Multithreading", emoji: "🏃",
        page: "content/java/multithreading.html",
        summary: "Multitasking, defining threads with Thread and Runnable, start versus run, names and priorities, the life cycle, yield, join and sleep, interruption, synchronization, wait and notify, deadlock, daemon threads and modern executors and virtual threads.",
        keywords: ["multithreading", "multitasking", "thread", "Thread class", "Runnable", "start vs run", "thread scheduler", "IllegalThreadStateException", "thread name", "currentThread", "thread priority", "life cycle", "getState", "yield", "join", "sleep", "interrupt", "InterruptedException", "synchronized", "race condition", "object lock", "class level lock", "synchronized block", "wait", "notify", "notifyAll", "IllegalMonitorStateException", "deadlock", "daemon thread", "ExecutorService", "Callable", "Future", "AtomicInteger", "virtual threads"],
        added: '2026-10-19',
        sections: [
          { id: "multitasking", title: "Multitasking", emoji: "🤹", group: "Chapter 14", keywords: ["multitasking", "process based", "thread based", "response time"] },
          { id: "defining-thread", title: "Defining a thread by extending Thread", emoji: "🧵", group: "Chapter 14", keywords: ["extends Thread", "run method", "start method", "thread scheduler", "t.run vs t.start", "IllegalThreadStateException"] },
          { id: "runnable", title: "Defining a thread with Runnable", emoji: "🏃", group: "Chapter 14", keywords: ["implements Runnable", "Thread(Runnable)", "best approach", "lambda thread"] },
          { id: "names-priorities", title: "Names and priorities", emoji: "🏷️", group: "Chapter 14", keywords: ["getName", "setName", "currentThread", "main thread", "priority 1 to 10", "MIN_PRIORITY", "NORM_PRIORITY", "MAX_PRIORITY", "inherited priority"] },
          { id: "lifecycle", title: "The thread life cycle", emoji: "🔄", group: "Chapter 14", keywords: ["NEW", "RUNNABLE", "BLOCKED", "WAITING", "TIMED_WAITING", "TERMINATED", "getState"] },
          { id: "prevent-execution", title: "yield, join and sleep", emoji: "⏸️", group: "Chapter 14", keywords: ["yield", "join", "sleep", "InterruptedException", "waiting for a thread", "pause"] },
          { id: "interrupt", title: "Interrupting a thread", emoji: "🔔", group: "Chapter 14", keywords: ["interrupt", "InterruptedException", "sleeping thread", "waiting thread", "interrupted flag"] },
          { id: "synchronization", title: "Synchronization", emoji: "🔒", group: "Chapter 14", keywords: ["synchronized method", "synchronized block", "race condition", "object lock", "class level lock", "static synchronized", "data inconsistency"] },
          { id: "inter-thread", title: "Inter-thread communication: wait and notify", emoji: "📨", group: "Chapter 14", keywords: ["wait", "notify", "notifyAll", "IllegalMonitorStateException", "producer consumer", "lock release"] },
          { id: "deadlock", title: "Deadlock", emoji: "💀", group: "Chapter 14", keywords: ["deadlock", "two locks", "waiting forever", "lock ordering"] },
          { id: "daemon", title: "Daemon threads", emoji: "👻", group: "Chapter 14", keywords: ["daemon thread", "setDaemon", "isDaemon", "background thread", "garbage collector"] },
          { id: "modern", title: "Modern concurrency", emoji: "🆕", group: "Chapter 14", keywords: ["ExecutorService", "thread pool", "Callable", "Future", "AtomicInteger", "CompletableFuture", "virtual threads", "Java 21"] }
        ]
      }
      ]
    },
    {
      id: "io", title: "Files and Serialization", emoji: "📁",
      topics: [
      {
        id: "file-io", title: "File I/O", emoji: "📄",
        page: "content/java/file-io.html",
        summary: "The File class, FileWriter and FileReader, BufferedWriter and BufferedReader, PrintWriter, merging and filtering files, byte streams versus character streams, and modern java.nio Files and Path.",
        keywords: ["java.io", "File", "createNewFile", "mkdir", "exists", "list", "FileWriter", "append", "FileReader", "read returns -1", "BufferedWriter", "newLine", "BufferedReader", "readLine returns null", "PrintWriter", "println", "flush", "close", "merge files", "byte stream", "character stream", "FileInputStream", "FileOutputStream", "java.nio.file", "Files", "Path", "try with resources"],
        added: '2026-10-19',
        sections: [
          { id: "file-class", title: "The File class", emoji: "🗂️", group: "Chapter 15", keywords: ["java.io.File", "file path", "directory", "exists", "createNewFile", "mkdir", "isFile", "isDirectory", "list", "length", "delete"] },
          { id: "filewriter", title: "FileWriter", emoji: "✍️", group: "Chapter 15", keywords: ["FileWriter", "write", "append mode", "flush", "close", "line separator"] },
          { id: "filereader", title: "FileReader", emoji: "📖", group: "Chapter 15", keywords: ["FileReader", "read", "-1 end of file", "char array read"] },
          { id: "buffered", title: "BufferedWriter and BufferedReader", emoji: "🚚", group: "Chapter 15", keywords: ["BufferedWriter", "newLine", "BufferedReader", "readLine", "null at end", "wrapping a FileWriter"] },
          { id: "printwriter", title: "PrintWriter", emoji: "🖨️", group: "Chapter 15", keywords: ["PrintWriter", "print", "println", "printf", "write vs print", "most enhanced writer"] },
          { id: "merge-files", title: "Classic file programs", emoji: "🧩", group: "Chapter 15", keywords: ["merge two files", "alternate lines", "remove duplicates", "filter lines", "program examples"] },
          { id: "byte-vs-char", title: "Byte streams and character streams", emoji: "🔢", group: "Chapter 15", keywords: ["InputStream", "OutputStream", "FileInputStream", "FileOutputStream", "Reader", "Writer", "binary data", "text data"] },
          { id: "modern", title: "Modern file handling with java.nio", emoji: "🆕", group: "Chapter 15", keywords: ["java.nio.file", "Path", "Files", "readAllLines", "writeString", "lines", "Files.write", "StandardOpenOption", "charset UTF-8"] }
        ]
      },
      {
        id: "serialization", title: "Serialization", emoji: "📦",
        page: "content/java/serialization.html",
        summary: "Saving whole objects to a file and reading them back: Serializable, ObjectOutputStream and ObjectInputStream, transient, object graphs, customised serialization, inheritance rules, Externalizable, serialVersionUID and modern advice.",
        keywords: ["serialization", "deserialization", "Serializable", "marker interface", "ObjectOutputStream", "ObjectInputStream", "writeObject", "readObject", "NotSerializableException", "transient", "transient static", "transient final", "object graph", "customized serialization", "defaultWriteObject", "defaultReadObject", "serialization inheritance", "no-arg constructor", "Externalizable", "writeExternal", "readExternal", "InvalidClassException", "serialVersionUID", "records", "ObjectInputFilter"],
        added: '2026-10-19',
        sections: [
          { id: "intro", title: "What serialization means", emoji: "📦", group: "Chapter 16", keywords: ["serialization", "deserialization", "marker interface", "Serializable", "persistence"] },
          { id: "write-read", title: "Writing and reading an object", emoji: "💾", group: "Chapter 16", keywords: ["ObjectOutputStream", "ObjectInputStream", "FileOutputStream", "writeObject", "readObject", "ClassNotFoundException", "cast", "NotSerializableException"] },
          { id: "transient", title: "The transient keyword", emoji: "🙈", group: "Chapter 16", keywords: ["transient", "default value", "password", "transient static", "transient final", "security"] },
          { id: "object-graph", title: "Object graphs", emoji: "🕸️", group: "Chapter 16", keywords: ["object graph", "has-a", "reachable objects", "NotSerializableException", "nested objects"] },
          { id: "custom", title: "Customised serialization", emoji: "🛠️", group: "Chapter 16", keywords: ["customized serialization", "private writeObject", "private readObject", "defaultWriteObject", "defaultReadObject", "encrypt transient field", "callback methods"] },
          { id: "inheritance", title: "Serialization and inheritance", emoji: "👪", group: "Chapter 16", keywords: ["parent Serializable", "child Serializable", "non-serializable parent", "no-arg constructor", "InvalidClassException", "instance initializer during deserialization"] },
          { id: "externalizable", title: "Externalizable", emoji: "🎛️", group: "Chapter 16", keywords: ["Externalizable", "writeExternal", "readExternal", "public no-arg constructor", "full control", "Serializable vs Externalizable"] },
          { id: "version-uid", title: "serialVersionUID", emoji: "🔖", group: "Chapter 16", keywords: ["serialVersionUID", "InvalidClassException", "local class incompatible", "default UID", "compatibility", "private static final long"] },
          { id: "modern", title: "Modern advice", emoji: "🆕", group: "Chapter 16", keywords: ["records serialization", "canonical constructor", "ObjectInputFilter", "deserialization security", "JSON", "alternatives"] }
        ]
      }
      ]
    },
    {
      id: "jvm", title: "JVM and Tooling", emoji: "⚙️",
      topics: [
      {
        id: "garbage-collection", title: "Garbage Collection", emoji: "♻️",
        page: "content/java/garbage-collection.html",
        summary: "How the JVM frees memory: reachability, the four ways an object becomes eligible, island of isolation, requesting a collection with System.gc and Runtime, reading heap figures, finalize and its replacement Cleaner, OutOfMemoryError and modern collectors.",
        keywords: ["garbage collection", "garbage collector", "heap", "reachable", "eligible for GC", "nullifying reference", "reassigning reference", "objects created inside method", "island of isolation", "System.gc", "Runtime.getRuntime", "Runtime.gc", "totalMemory", "freeMemory", "maxMemory", "availableProcessors", "finalize", "Cleaner", "WeakReference", "OutOfMemoryError", "Xmx", "G1", "ZGC", "memory leak"],
        added: '2026-10-19',
        sections: [
          { id: "intro", title: "Why a garbage collector", emoji: "♻️", group: "Chapter 17", keywords: ["garbage collector", "heap", "memory leak", "automatic memory management", "daemon thread", "reachable", "unreachable"] },
          { id: "eligible", title: "Four ways to make an object eligible", emoji: "🎯", group: "Chapter 17", keywords: ["nullify reference", "reassign reference", "objects created inside a method", "method return", "island of isolation", "WeakReference"] },
          { id: "request-gc", title: "Requesting a collection", emoji: "🙋", group: "Chapter 17", keywords: ["System.gc", "Runtime.getRuntime().gc", "singleton Runtime", "request not command", "DisableExplicitGC"] },
          { id: "runtime-memory", title: "Looking at memory with Runtime", emoji: "📊", group: "Chapter 17", keywords: ["totalMemory", "freeMemory", "maxMemory", "availableProcessors", "used memory", "Xmx", "Xms", "OutOfMemoryError", "Java heap space"] },
          { id: "finalization", title: "finalize and Cleaner", emoji: "🧹", group: "Chapter 17", keywords: ["finalize", "deprecated for removal", "Cleaner", "PhantomReference", "try-with-resources", "AutoCloseable", "cleanup"] },
          { id: "modern", title: "Modern collectors and good habits", emoji: "🆕", group: "Chapter 17", keywords: ["G1", "ZGC", "Serial GC", "Parallel GC", "generational", "young generation", "old generation", "pause time", "memory leak in Java", "static collections", "listeners"] }
        ]
      },
      {
        id: "assertions", title: "Assertions", emoji: "✅",
        page: "content/java/assertions.html",
        summary: "Checking your own assumptions while developing: assert as a keyword, the simple and augmented forms, enabling and disabling with -ea and -da at class and package level, system assertions, AssertionError, and where assertions belong and where they do not.",
        keywords: ["assertions", "assert keyword", "assert as identifier", "Java 1.4", "simple assert", "augmented assert", "AssertionError", "-ea", "-da", "-esa", "-dsa", "enableassertions", "disableassertions", "package level assertions", "assertions in public methods", "assertions in private methods", "default case", "side effects in assert", "catching AssertionError"],
        added: '2026-10-19',
        sections: [
          { id: "intro", title: "Why assertions", emoji: "🔍", group: "Chapter 18", keywords: ["debugging", "System.out.println debugging", "assert", "development", "testing", "production", "Java 1.4"] },
          { id: "keyword", title: "assert as a keyword", emoji: "🔑", group: "Chapter 18", keywords: ["assert keyword", "identifier", "Java 1.4", "-source", "reserved word", "compile error"] },
          { id: "forms", title: "The two forms", emoji: "✌️", group: "Chapter 18", keywords: ["simple assert", "augmented assert", "assert condition", "assert condition : message", "AssertionError", "toString", "detail message"] },
          { id: "flags", title: "Enabling and disabling", emoji: "🎚️", group: "Chapter 18", keywords: ["-ea", "-enableassertions", "-da", "-disableassertions", "-esa", "-dsa", "system assertions", "class level", "package level", "three dots", "order of flags"] },
          { id: "usage", title: "Where to use them and where not", emoji: "📍", group: "Chapter 18", keywords: ["appropriate use", "inappropriate use", "public method arguments", "private method arguments", "default case", "switch", "command line arguments", "side effects", "IllegalArgumentException"] },
          { id: "assertion-error", title: "AssertionError", emoji: "💥", group: "Chapter 18", keywords: ["AssertionError", "Error", "unchecked", "catch AssertionError", "Throwable hierarchy", "legal but bad practice", "JUnit assertions"] }
        ]
      },
      {
        id: "development", title: "Development Tools", emoji: "🛠️",
        page: "content/java/development.html",
        summary: "The tools around your code: javac and its -d option, the java launcher and command line arguments, the classpath, building and running JAR files, executable JARs with a manifest, system properties with -D, JDK versus JRE versus JVM, PATH versus CLASSPATH, and modern shortcuts like single-file programs and jshell.",
        keywords: ["javac", "java command", "-d option", "package folders", "command line arguments", "String[] args", "classpath", "-cp", "CLASSPATH environment variable", "ClassNotFoundException", "NoClassDefFoundError", "jar", "jar -cvf", "jar -tf", "jar -xvf", "manifest", "Main-Class", "java -jar", "executable jar", "system properties", "-D", "System.getProperty", "Integer.getInteger", "JDK", "JRE", "JVM", "PATH", "single-file source", "jshell", "jdeps", "javap"],
        added: '2026-10-19',
        sections: [
          { id: "javac", title: "Compiling with javac", emoji: "🧱", group: "Chapter 19", keywords: ["javac", "compile", ".class file", "-d option", "package directory", "multiple files", "wildcard", "compile error"] },
          { id: "java-launcher", title: "Running with java", emoji: "🚀", group: "Chapter 19", keywords: ["java command", "fully qualified name", "main method", "command line arguments", "args", "Main method not found", "Could not find or load main class"] },
          { id: "classpath", title: "The classpath", emoji: "🧭", group: "Chapter 19", keywords: ["classpath", "-cp", "-classpath", "CLASSPATH environment variable", "current directory", "dot", "separator colon semicolon", "ClassNotFoundException", "NoClassDefFoundError", "package does not exist"] },
          { id: "jar", title: "JAR files", emoji: "🫙", group: "Chapter 19", keywords: ["jar", "Java ARchive", "jar -cvf", "jar -tf", "jar -xvf", "jar -cvfm", "manifest", "MANIFEST.MF", "Main-Class", "java -jar", "executable jar", "-C option"] },
          { id: "properties", title: "System properties", emoji: "🏷️", group: "Chapter 19", keywords: ["system properties", "-D option", "System.getProperty", "default value", "Integer.getInteger", "Boolean.getBoolean", "user.home", "java.version", "os.name", "line.separator"] },
          { id: "jdk-jre-jvm", title: "JDK, JRE and JVM", emoji: "🪆", group: "Chapter 19", keywords: ["JDK", "JRE", "JVM", "Java Development Kit", "Java Runtime Environment", "Java Virtual Machine", "bytecode", "platform independent", "PATH", "CLASSPATH difference", "JAVA_HOME"] },
          { id: "modern", title: "Modern shortcuts", emoji: "🆕", group: "Chapter 19", keywords: ["single-file source code program", "java Hello.java", "jshell", "javap", "jdeps", "Maven", "Gradle", "build tools", "multi-file source launch"] }
        ]
      }
      ]
    }
  ];
}
