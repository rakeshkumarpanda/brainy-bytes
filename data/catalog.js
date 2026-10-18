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
    hello: 'New: watch code run line by line',
    intro: 'Free notes that move, joke and run. Every topic comes with animations you can control, everyday examples, step by step code in Java, JavaScript and Python, and practice from easy to expert.',
    footer: 'Brainy Bytes. Free to learn, free to share.',
    searchExamples: ['binary search', 'sieve', 'two pointers', 'GCD', 'Kadane', 'sliding window', 'prime', 'heap'],
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
      ['Why did the matrix feel confident', 'It had its rows and columns in order.']
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
              summary: '22 maths problems from primes and GCD to Miller-Rabin, naive versus optimized.',
              keywords: ['number theory', 'prime', 'gcd', 'lcm', 'sieve of eratosthenes', 'modular arithmetic', 'combinatorics'],
              added: '2026-10-18',
              sections: mathSections()
            },
            {
              id: 'arrays', title: 'Arrays', emoji: '📦',
              page: 'content/dsa/array-adventure.html',
              summary: '26 lessons from memory layout to segment trees, with 104 practice problems.',
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
      blurb: 'From your first class to collections and streams.',
      tags: ['OOP', 'Collections', 'Streams'],
      modules: [
        {
          id: 'basics', title: 'Basics', emoji: '🌱',
          topics: [
            { id: 'first-program', title: 'Your first program', emoji: '👶', summary: 'main, classes and printing.', soon: true },
            { id: 'oop', title: 'Object oriented programming', emoji: '🏗️', summary: 'Classes, objects, inheritance and polymorphism.', keywords: ['oop', 'inheritance', 'polymorphism', 'encapsulation'], soon: true },
            { id: 'collections', title: 'Collections', emoji: '🧺', summary: 'List, Set, Map and friends.', soon: true }
          ]
        }
      ]
    }
  ]
};

/* ===== Section lists for the two DSA pages. Generated, but safe to edit by hand. ===== */

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
