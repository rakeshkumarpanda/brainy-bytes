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
    hello: 'New: Manual Testing, the Complete Java Session track and TestNG, with programs in Java, Python and JavaScript',
    intro: 'Free notes that move, joke and run. Every topic comes with animations you can control, everyday examples, step by step code in Java, JavaScript and Python, and practice from easy to expert.',
    footer: 'Brainy Bytes. Free to learn, free to share.',
    searchExamples: ['binary search', 'heap sort', 'two pointers', 'Kadane', 'boundary value analysis', 'bug life cycle', 'constructor chaining', 'HashMap', 'DataProvider', 'listeners'],
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
      blurb: 'Arrays, strings, linked lists, stacks, queues, trees and graphs, animated step by step.',
      intro: 'Start with the building blocks, then climb to expert patterns. Every ready topic has animations, everyday examples, line by line code runs and practice problems with brute force and optimized solutions.',
      tags: ['Arrays', 'Strings', 'Linked lists', 'Trees', 'Graphs'],
      modules: [
        {
          id: 'getting-started', title: 'Getting started', emoji: '🚀',
          blurb: 'What DSA is and how we measure speed.',
          topics: [
            {
              id: 'introduction', title: 'Introduction to DSA', emoji: '👋',
              page: 'content/dsa/dsa-introduction.html',
              summary: 'What data structures and algorithms are, the five properties of an algorithm, linear and non linear structures, abstract data types, paradigms and a method for any problem. Code in Python, JavaScript and Java.',
              keywords: ['data structure', 'algorithm', 'abstract data type', 'adt', 'linear', 'non linear', 'paradigm', 'greedy', 'dynamic programming', 'divide and conquer'],
              added: '2026-10-19',
              sections: introSections()
            },
            {
              id: 'runtime-analysis', title: 'Run time analysis', emoji: '⏱️',
              page: 'content/dsa/runtime-analysis.html',
              summary: 'Time complexity, space complexity, auxiliary space and recursion depth: Big O, Omega and Theta, loop patterns, best, worst and amortized cases, recurrences, the master theorem and recursion trees.',
              keywords: ['big o', 'complexity', 'asymptotic', 'time complexity', 'space complexity', 'auxiliary space', 'recursion depth', 'recursion tree', 'master theorem', 'call stack'],
              added: '2026-10-19',
              sections: runtimeSections()
            }
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
              summary: '32 lessons from memory layout to segment trees, including heap sort, Tim sort, shell, counting, radix, bucket and cycle sort, 128 practice problems, quizzes, number practice and a six language narrator.',
              keywords: ['array', 'list', 'two pointers', 'sliding window', 'prefix sum', 'sorting', 'searching', 'heap sort', 'tim sort', 'shell sort', 'counting sort', 'radix sort', 'bucket sort', 'cycle sort', 'pancake sort'],
              added: '2026-10-18',
              sections: arraySections()
            },
            {
              id: 'strings', title: 'Strings', emoji: '🔤',
              page: 'content/dsa/strings.html',
              summary: 'Characters and code points, immutable strings and fast building, everyday operations and their cost, two pointers, anagram counting, sliding windows, KMP and Rabin-Karp matching, with 8 practice problems in Python, JavaScript and Java.',
              keywords: ['string', 'substring', 'palindrome', 'anagram', 'sliding window', 'kmp', 'rabin karp', 'rolling hash', 'string builder', 'unicode'],
              added: '2026-10-20',
              sections: stringsSections()
            }
          ]
        },
        {
          id: 'linear', title: 'Linear structures', emoji: '🚃',
          topics: [
            {
              id: 'linked-lists', title: 'Linked lists', emoji: '🔗',
              page: 'content/dsa/linked-lists.html',
              summary: 'Nodes and pointers, insert and delete with a dummy node, doubly linked lists, reversing, fast and slow pointers with Floyd cycle detection, merging sorted lists and when to pick a list over an array.',
              keywords: ['linked list', 'node', 'pointer', 'doubly linked list', 'reverse linked list', 'floyd cycle detection', 'fast and slow pointers', 'merge sorted lists', 'lru cache'],
              added: '2026-10-20',
              sections: linkedListSections()
            },
            {
              id: 'stacks-queues', title: 'Stacks and queues', emoji: '🥞',
              page: 'content/dsa/stacks-queues.html',
              summary: 'LIFO and FIFO, balanced brackets, postfix evaluation and the shunting yard algorithm, ring buffers, deques and priority queues, monotonic stacks, and undo and redo with two stacks.',
              keywords: ['stack', 'queue', 'deque', 'priority queue', 'balanced brackets', 'postfix', 'shunting yard', 'circular buffer', 'monotonic stack', 'next greater element'],
              added: '2026-10-20',
              sections: stackQueueSections()
            }
          ]
        },
        {
          id: 'nonlinear', title: 'Trees and graphs', emoji: '🌳',
          topics: [
            {
              id: 'trees', title: 'Trees', emoji: '🌲',
              page: 'content/dsa/trees.html',
              summary: 'Binary trees and recursion, preorder, inorder, postorder and level order traversal, binary search trees with insert, search and delete, balance and height, heaps stored in arrays, and tries for words.',
              keywords: ['tree', 'binary tree', 'traversal', 'inorder', 'binary search tree', 'bst', 'balanced tree', 'avl', 'heap', 'trie', 'lowest common ancestor'],
              added: '2026-10-20',
              sections: treeSections()
            },
            {
              id: 'graphs', title: 'Graphs', emoji: '🕸️',
              page: 'content/dsa/graphs.html',
              summary: 'Adjacency lists and matrices, breadth first and depth first search, connected components, topological order, Dijkstra shortest paths, Kruskal minimum spanning trees with union find, and grids as graphs.',
              keywords: ['graph', 'bfs', 'dfs', 'adjacency list', 'topological sort', 'dijkstra', 'shortest path', 'minimum spanning tree', 'kruskal', 'union find', 'number of islands'],
              added: '2026-10-20',
              sections: graphSections()
            }
          ]
        }
      ]
    },
    {
      id: 'manual-testing',
      title: 'Manual Testing',
      emoji: '🐞',
      color: '#f25da0',
      blurb: 'Find bugs before your users do: test design, life cycles, bug reports and test plans.',
      intro: 'Ten chapters that follow the manual testing notes in order, from what testing is to the test plan. Every diagram is redrawn as an animation, every idea has an everyday example, and each chapter ends with practice programs in Java, Python and JavaScript, quizzes from easy to expert and a narrator in six languages.',
      tags: ['STLC', 'Test cases', 'Bug life cycle', 'Regression', 'Test plan'],
      modules: mtModules()
    },
    {
      id: 'java',
      title: 'Java',
      emoji: '☕',
      color: '#ff9238',
      blurb: 'Core Java from your first identifier to the JVM, with every example compiled and run.',
      intro: 'Start with the Complete Java Session track: seven chapters that follow the session programs from the first class to reading Excel files, ending with all 66 practice programs. Then go deeper with nineteen reference chapters in seven modules. Every code block was compiled and run with JDK 21, and the real output, compile error or exception is shown under it. Each chapter has a comic strip, everyday examples, quizzes from easy to expert, number practice with full working, and a narrator who reads it aloud in six languages.',
      tags: ['OOP', 'Exceptions', 'Collections', 'Threads', 'JVM'],
      modules: [cjsModule()].concat(javaModules())
    },
    {
      id: 'testng',
      title: 'TestNG',
      emoji: '🧪',
      color: '#16a34a',
      blurb: 'Annotations, suites, data providers, listeners and framework design, run on real TestNG.',
      intro: 'Three chapters that take you from a first @Test to a Page Object framework with listeners, retries and parallel runs. Every Java example runs on real TestNG with its testng.xml, and the same idea is shown with pytest and Mocha.',
      tags: ['Annotations', 'testng.xml', 'DataProvider', 'Listeners', 'Parallel'],
      modules: [tngModule()]
    },
    {
      id: 'api-manual-testing',
      title: 'Manual API Testing',
      emoji: '🔌',
      color: '#8467f0',
      blurb: 'Test APIs by hand from your first HTTP request to security, contracts and AI APIs, with a live playground.',
      intro: 'One complete course in four levels, from what an API is to contract testing, the OWASP API Top 10 and testing AI and MCP APIs. Every part has an animation or a tool to try, and the live playground lets you send requests to a mock shop API and hunt seven hidden bugs.',
      tags: ['HTTP', 'Postman', 'Status codes', 'Auth', 'API security'],
      modules: [apiManualModule()]
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
    { id: "HeapSort", title: "Heap Sort", emoji: "⛰️", group: "Phase 3: Classical Searching and Sorting", keywords: ["heap sort", "binary heap", "max heap", "min heap", "heapify", "sift down", "priority queue", "top k", "in place", "not stable"],
      items: [
        { id: "HeapSort/practice-1", title: "Is it a max heap?", kind: 'Practice', level: "Easy" },
        { id: "HeapSort/practice-2", title: "The k largest values with a min heap", kind: 'Practice', level: "Medium" },
        { id: "HeapSort/practice-3", title: "Merge k sorted arrays", kind: 'Practice', level: "Hard" },
        { id: "HeapSort/practice-4", title: "Running median with two heaps", kind: 'Practice', level: "Expert" }
      ] },
    { id: "HybridSorts", title: "TimSort and Introsort (Hybrid Sorts)", emoji: "🧬", group: "Phase 3: Classical Searching and Sorting", keywords: ["timsort", "introsort", "hybrid sort", "runs", "minrun", "galloping", "binary insertion sort", "std::sort", "python sorted", "java arrays.sort", "depth limit"],
      items: [
        { id: "HybridSorts/practice-1", title: "Count the natural runs", kind: 'Practice', level: "Easy" },
        { id: "HybridSorts/practice-2", title: "Binary insertion sort", kind: 'Practice', level: "Medium" },
        { id: "HybridSorts/practice-3", title: "Compute TimSort's minrun", kind: 'Practice', level: "Hard" },
        { id: "HybridSorts/practice-4", title: "Introsort's safety net in action", kind: 'Practice', level: "Expert" }
      ] },
    { id: "GapSorts", title: "Shell, Comb, Cocktail, Gnome and Odd-Even Sort", emoji: "🪮", group: "Phase 3: Classical Searching and Sorting", keywords: ["shell sort", "comb sort", "cocktail shaker sort", "gnome sort", "odd even sort", "gap sequence", "knuth gaps", "ciura", "turtles", "parallel sorting"],
      items: [
        { id: "GapSorts/practice-1", title: "Knuth's gap sequence", kind: 'Practice', level: "Easy" },
        { id: "GapSorts/practice-2", title: "Is the array h-sorted?", kind: 'Practice', level: "Medium" },
        { id: "GapSorts/practice-3", title: "Comb sort versus bubble sort", kind: 'Practice', level: "Hard" },
        { id: "GapSorts/practice-4", title: "Which gap sequence is best?", kind: 'Practice', level: "Expert" }
      ] },
    { id: "NonComparisonSorts", title: "Counting, Radix and Bucket Sort", emoji: "🪣", group: "Phase 3: Classical Searching and Sorting", keywords: ["counting sort", "radix sort", "bucket sort", "LSD", "MSD", "linear time sort", "prefix sums", "stable", "pigeonhole", "maximum gap"],
      items: [
        { id: "NonComparisonSorts/practice-1", title: "Sort exam marks with counting sort", kind: 'Practice', level: "Easy" },
        { id: "NonComparisonSorts/practice-2", title: "Sort words by length, stably", kind: 'Practice', level: "Medium" },
        { id: "NonComparisonSorts/practice-3", title: "Radix sort with negative numbers", kind: 'Practice', level: "Hard" },
        { id: "NonComparisonSorts/practice-4", title: "Maximum gap in linear time", kind: 'Practice', level: "Expert" }
      ] },
    { id: "CycleSorts", title: "Cycle Sort and Pancake Sort", emoji: "🥞", group: "Phase 3: Classical Searching and Sorting", keywords: ["cycle sort", "pancake sort", "minimum writes", "prefix reversal", "permutation cycles", "minimum swaps", "cyclic sort", "first missing positive"],
      items: [
        { id: "CycleSorts/practice-1", title: "Minimum swaps to sort a permutation", kind: 'Practice', level: "Easy" },
        { id: "CycleSorts/practice-2", title: "Find all duplicates with cyclic placement", kind: 'Practice', level: "Medium" },
        { id: "CycleSorts/practice-3", title: "First missing positive", kind: 'Practice', level: "Hard" },
        { id: "CycleSorts/practice-4", title: "Pancake flips for a stack", kind: 'Practice', level: "Expert" }
      ] },
    { id: "SortCompare", title: "Choosing a Sorting Algorithm", emoji: "🏁", group: "Phase 3: Classical Searching and Sorting", keywords: ["choosing a sort", "stability", "in place", "comparison count", "nearly sorted", "few unique", "inversions", "k sorted", "cache", "which sort"],
      items: [
        { id: "SortCompare/practice-1", title: "Is the result stable?", kind: 'Practice', level: "Easy" },
        { id: "SortCompare/practice-2", title: "Sort by two keys with a stable sort", kind: 'Practice', level: "Medium" },
        { id: "SortCompare/practice-3", title: "Count inversions with merge sort", kind: 'Practice', level: "Hard" },
        { id: "SortCompare/practice-4", title: "Sort a k-sorted array with a heap", kind: 'Practice', level: "Expert" }
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

function introSections() {
  return [
    { id: "what-is", title: "What data structures and algorithms are", emoji: "🧭", group: 'Lesson', keywords: ["definition", "data structure", "algorithm", "program", "organise data", "recipe", "phone book"] },
    { id: "why", title: "Why DSA matters", emoji: "🚀", group: 'Lesson', keywords: ["scalability", "efficiency", "performance", "real world systems", "interviews", "steps per second"] },
    { id: "algorithm", title: "What makes something an algorithm", emoji: "🧾", group: 'Lesson', keywords: ["properties of algorithm", "finiteness", "definiteness", "input", "output", "effectiveness", "correctness", "pseudocode", "flowchart", "loop invariant"] },
    { id: "classify", title: "Kinds of data structures", emoji: "🗂️", group: 'Lesson', keywords: ["primitive", "non-primitive", "linear", "non-linear", "static", "dynamic", "contiguous", "linked", "array", "linked list", "stack", "queue", "tree", "graph", "hash table", "heap"] },
    { id: "adt", title: "Abstract data types", emoji: "🎭", group: 'Lesson', keywords: ["abstract data type", "ADT", "interface", "implementation", "stack ADT", "queue ADT", "list ADT", "map ADT", "priority queue", "encapsulation"] },
    { id: "operations", title: "Core operations and what they cost", emoji: "⚖️", group: 'Lesson', keywords: ["traversal", "insertion", "deletion", "searching", "sorting", "merging", "access", "time complexity table", "array vs linked list"] },
    { id: "paradigms", title: "Algorithm design paradigms", emoji: "🧠", group: 'Lesson', keywords: ["brute force", "greedy", "divide and conquer", "dynamic programming", "backtracking", "two pointers", "sliding window", "graph traversal", "randomized", "coin change"] },
    { id: "choose", title: "Choosing the right structure", emoji: "🧩", group: 'Lesson', keywords: ["choose data structure", "decision guide", "when to use stack", "queue", "hash map", "heap", "tree", "graph", "array"] },
    { id: "method", title: "A method for solving any problem", emoji: "🛠️", group: 'Lesson', keywords: ["problem solving method", "understand", "examples", "brute force first", "optimise", "edge cases", "test", "roadmap", "learning path"] },
    { id: "second-largest", title: "Second largest element", emoji: '🏋️', group: "Easy practice" },
    { id: "reverse-in-place", title: "Reverse an array in place", emoji: '🏋️', group: "Easy practice" },
    { id: "balanced-brackets", title: "Balanced brackets", emoji: '🏋️', group: "Medium practice" },
    { id: "first-unique", title: "First non-repeating character", emoji: '🏋️', group: "Medium practice" },
    { id: "two-sum", title: "Two sum", emoji: '🏋️', group: "Hard practice" },
    { id: "queue-two-stacks", title: "Queue from two stacks", emoji: '🏋️', group: "Hard practice" },
    { id: "min-coins", title: "Fewest coins for an amount", emoji: '🏋️', group: "Expert practice" },
    { id: "cycle-start", title: "Where does the linked list loop?", emoji: '🏋️', group: "Expert practice" },
    { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
    { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
  ];
}

function runtimeSections() {
  return [
    { id: "why-analyse", title: "Why count steps instead of timing", emoji: "🧮", group: 'Lesson', keywords: ["RAM model", "basic operation", "step count", "machine independent", "stopwatch", "input size n"] },
    { id: "growth", title: "Orders of growth", emoji: "📈", group: 'Lesson', keywords: ["constant", "logarithmic", "linear", "linearithmic", "n log n", "quadratic", "cubic", "exponential", "factorial", "growth rate comparison"] },
    { id: "notations", title: "Big O, Big Omega and Big Theta", emoji: "🔣", group: 'Lesson', keywords: ["big o definition", "upper bound", "big omega lower bound", "big theta tight bound", "little o", "little omega", "c and n0", "formal proof"] },
    { id: "rules", title: "Rules for finding the complexity", emoji: "📏", group: 'Lesson', keywords: ["drop constants", "drop lower order terms", "sum rule", "product rule", "sequential statements", "nested loops", "if else", "loop patterns", "logarithmic loop", "square root loop"] },
    { id: "cases", title: "Best, worst, average and amortized", emoji: "🎲", group: 'Lesson', keywords: ["best case", "worst case", "average case", "expected case", "amortized analysis", "dynamic array", "aggregate method", "linear search cases"] },
    { id: "space", title: "Space complexity", emoji: "💾", group: 'Lesson', keywords: ["space complexity", "memory", "fixed part", "variable part", "input space", "auxiliary space", "time space trade off", "hash set", "memory growth"] },
    { id: "auxiliary", title: "Auxiliary space in depth", emoji: "🧰", group: 'Lesson', keywords: ["auxiliary space", "in place algorithm", "extra memory", "merge sort buffer", "quick sort stack", "heap sort", "recursion stack counts", "sorting algorithms space table"] },
    { id: "recurrences", title: "Recurrences and the recursion tree", emoji: "🌳", group: 'Lesson', keywords: ["recurrence relation", "recursion tree method", "master theorem", "substitution", "T(n) = 2T(n/2) + n", "divide and conquer cost", "Fibonacci calls", "binary search recurrence"] },
    { id: "recursion-depth", title: "Recursion depth and the call stack", emoji: "🥞", group: 'Lesson', keywords: ["call stack", "stack frame", "recursion depth", "maximum depth", "stack overflow", "RecursionError", "StackOverflowError", "RangeError", "tail recursion", "iterative conversion", "memoization space"] },
    { id: "practical", title: "From constraints to complexity", emoji: "🎯", group: 'Lesson', keywords: ["input constraints", "time limit", "10^8 operations per second", "doubling experiment", "empirical analysis", "common mistakes", "hidden loops", "string concatenation", "slicing cost"] },
    { id: "sum-array", title: "Sum of an array, with its cost", emoji: '🏋️', group: "Easy practice" },
    { id: "power-of-two", title: "Is it a power of two?", emoji: '🏋️', group: "Easy practice" },
    { id: "pair-count", title: "Count pairs with a given sum, two ways", emoji: '🏋️', group: "Medium practice" },
    { id: "nested-analysis", title: "Analyse a nested loop", emoji: '🏋️', group: "Medium practice" },
    { id: "fast-power", title: "Fast exponentiation", emoji: '🏋️', group: "Hard practice" },
    { id: "merge-work", title: "Measure the work of merge sort", emoji: '🏋️', group: "Hard practice" },
    { id: "memo-fib", title: "Memoization: from exponential to linear", emoji: '🏋️', group: "Expert practice" },
    { id: "subsets", title: "All subsets and their recursion tree", emoji: '🏋️', group: "Expert practice" },
    { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
    { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
  ];
}

function stringsSections() {
  return [
    { id: "what-is", title: "What a string really is", emoji: "🔤", group: 'Lesson', keywords: ["character", "unicode", "ascii", "code point", "utf-8", "ord", "chr", "charAt"] },
    { id: "immutable", title: "Immutable strings and building them fast", emoji: "🧊", group: 'Lesson', keywords: ["immutable string", "string builder", "join", "concatenation cost", "StringBuilder", "quadratic concatenation"] },
    { id: "operations", title: "Everyday operations and what they cost", emoji: "🧰", group: 'Lesson', keywords: ["substring", "slice", "split", "find", "indexOf", "replace", "upper case", "trim", "string methods"] },
    { id: "two-pointers", title: "Two pointers: reverse and palindromes", emoji: "👉", group: 'Lesson', keywords: ["palindrome", "reverse string", "two pointers", "valid palindrome"] },
    { id: "counting", title: "Counting characters: anagrams and frequency", emoji: "🧮", group: 'Lesson', keywords: ["anagram", "frequency count", "character count", "hash map", "counter"] },
    { id: "window", title: "Sliding window: the longest run without repeats", emoji: "🪟", group: 'Lesson', keywords: ["sliding window", "longest substring without repeating characters", "unique characters"] },
    { id: "matching", title: "Pattern matching: naive search and KMP", emoji: "🔎", group: 'Lesson', keywords: ["pattern matching", "kmp", "prefix function", "lps array", "string search"] },
    { id: "hashing", title: "Rolling hash: Rabin and Karp", emoji: "🧬", group: 'Lesson', keywords: ["rabin karp", "rolling hash", "polynomial hash", "hash collision"] },
    { id: "reverse-words", title: "Reverse the words in a sentence", emoji: '🏋️', group: "Easy practice" },
    { id: "rotation", title: "Is one string a rotation of another", emoji: '🏋️', group: "Easy practice" },
    { id: "common-prefix", title: "Longest common prefix", emoji: '🏋️', group: "Medium practice" },
    { id: "compress", title: "Run length compression", emoji: '🏋️', group: "Medium practice" },
    { id: "longest-palindrome", title: "Longest palindromic substring", emoji: '🏋️', group: "Hard practice" },
    { id: "group-anagrams", title: "Group anagrams together", emoji: '🏋️', group: "Hard practice" },
    { id: "min-window", title: "Minimum window substring", emoji: '🏋️', group: "Expert practice" },
    { id: "edit-distance", title: "Edit distance", emoji: '🏋️', group: "Expert practice" },
    { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
    { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
  ];
}

function linkedListSections() {
  return [
    { id: "what-is", title: "Nodes holding hands", emoji: "🔗", group: 'Lesson', keywords: ["node", "next pointer", "head", "singly linked list", "traverse", "null"] },
    { id: "insert-delete", title: "Inserting and deleting by rewiring", emoji: "✂️", group: 'Lesson', keywords: ["insert at head", "insert at tail", "delete node", "dummy node", "sentinel"] },
    { id: "doubly", title: "Doubly linked and circular lists", emoji: "↔️", group: 'Lesson', keywords: ["doubly linked list", "prev pointer", "tail", "deque"] },
    { id: "reverse", title: "Reversing a list in place", emoji: "🔁", group: 'Lesson', keywords: ["reverse linked list", "three pointers", "iterative reverse", "recursive reverse"] },
    { id: "fast-slow", title: "Fast and slow pointers", emoji: "🐢", group: 'Lesson', keywords: ["floyd cycle detection", "tortoise and hare", "middle of list", "fast and slow pointers", "cycle start"] },
    { id: "merge", title: "Merging two sorted lists", emoji: "🤝", group: 'Lesson', keywords: ["merge two sorted lists", "merge sort linked list", "dummy head"] },
    { id: "when", title: "Lists versus arrays in real code", emoji: "⚖️", group: 'Lesson', keywords: ["array vs linked list", "cache locality", "when to use linked list", "LinkedList"] },
    { id: "remove-value", title: "Remove every node with a given value", emoji: '🏋️', group: "Easy practice" },
    { id: "dedup-sorted", title: "Remove duplicates from a sorted list", emoji: '🏋️', group: "Easy practice" },
    { id: "nth-from-end", title: "Remove the n-th node from the end", emoji: '🏋️', group: "Medium practice" },
    { id: "list-palindrome", title: "Is the linked list a palindrome", emoji: '🏋️', group: "Medium practice" },
    { id: "add-two", title: "Add two numbers stored as lists", emoji: '🏋️', group: "Hard practice" },
    { id: "intersection", title: "Where do two lists join", emoji: '🏋️', group: "Hard practice" },
    { id: "reverse-k", title: "Reverse nodes in groups of k", emoji: '🏋️', group: "Expert practice" },
    { id: "lru-cache", title: "Least recently used cache", emoji: '🏋️', group: "Expert practice" },
    { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
    { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
  ];
}

function stackQueueSections() {
  return [
    { id: "stack", title: "The stack: last in, first out", emoji: "🥞", group: 'Lesson', keywords: ["stack", "push", "pop", "peek", "LIFO", "call stack", "ArrayDeque"] },
    { id: "brackets", title: "Matching brackets with a stack", emoji: "🧷", group: 'Lesson', keywords: ["balanced parentheses", "valid brackets", "matching brackets"] },
    { id: "expressions", title: "Evaluating expressions", emoji: "🧮", group: 'Lesson', keywords: ["postfix", "infix", "reverse polish notation", "shunting yard", "expression evaluation", "operator precedence"] },
    { id: "queue", title: "The queue: first in, first out", emoji: "🚶", group: 'Lesson', keywords: ["queue", "enqueue", "dequeue", "FIFO", "circular buffer", "ring buffer"] },
    { id: "deque-priority", title: "Deques and priority queues", emoji: "🎟️", group: 'Lesson', keywords: ["deque", "priority queue", "heap", "heapq", "PriorityQueue"] },
    { id: "monotonic", title: "Monotonic stacks", emoji: "📈", group: 'Lesson', keywords: ["monotonic stack", "next greater element", "stock span", "daily temperatures"] },
    { id: "real-world", title: "Undo, redo and other everyday uses", emoji: "↩️", group: 'Lesson', keywords: ["undo redo", "browser history", "scheduler", "two stacks"] },
    { id: "remove-adjacent", title: "Remove adjacent duplicates", emoji: '🏋️', group: "Easy practice" },
    { id: "josephus", title: "Hot potato: who is left", emoji: '🏋️', group: "Easy practice" },
    { id: "min-stack", title: "A stack that knows its minimum", emoji: '🏋️', group: "Medium practice" },
    { id: "simplify-path", title: "Simplify a file path", emoji: '🏋️', group: "Medium practice" },
    { id: "decode-string", title: "Decode a repeated string", emoji: '🏋️', group: "Hard practice" },
    { id: "largest-rectangle", title: "Largest rectangle in a histogram", emoji: '🏋️', group: "Hard practice" },
    { id: "window-max", title: "Sliding window maximum", emoji: '🏋️', group: "Expert practice" },
    { id: "calculator", title: "A calculator with precedence and parentheses", emoji: '🏋️', group: "Expert practice" },
    { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
    { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
  ];
}

function treeSections() {
  return [
    { id: "what-is", title: "What a tree is", emoji: "🌲", group: 'Lesson', keywords: ["tree", "root", "leaf", "binary tree", "height", "depth", "subtree", "recursion"] },
    { id: "traversals", title: "Traversals: visiting every node", emoji: "🚶", group: 'Lesson', keywords: ["preorder", "inorder", "postorder", "level order", "tree traversal", "bfs on tree"] },
    { id: "bst", title: "Binary search trees", emoji: "🔍", group: 'Lesson', keywords: ["binary search tree", "bst", "bst insert", "bst search", "minimum", "maximum"] },
    { id: "bst-delete", title: "Deleting from a search tree", emoji: "✂️", group: 'Lesson', keywords: ["bst delete", "inorder successor", "inorder predecessor", "remove node"] },
    { id: "balance", title: "Balance: why shape matters", emoji: "⚖️", group: 'Lesson', keywords: ["balanced tree", "avl tree", "red black tree", "b tree", "tree height", "sorted array to bst"] },
    { id: "heap", title: "Heaps: trees inside arrays", emoji: "⛰️", group: 'Lesson', keywords: ["binary heap", "min heap", "max heap", "sift up", "sift down", "heapify", "priority queue"] },
    { id: "trie", title: "Tries: trees of letters", emoji: "🔤", group: 'Lesson', keywords: ["trie", "prefix tree", "autocomplete", "prefix search"] },
    { id: "max-depth", title: "Maximum and minimum depth", emoji: '🏋️', group: "Easy practice" },
    { id: "invert", title: "Mirror a tree", emoji: '🏋️', group: "Easy practice" },
    { id: "validate-bst", title: "Is it a valid search tree", emoji: '🏋️', group: "Medium practice" },
    { id: "path-sum", title: "Root to leaf paths with a given sum", emoji: '🏋️', group: "Medium practice" },
    { id: "lca", title: "Lowest common ancestor", emoji: '🏋️', group: "Hard practice" },
    { id: "serialize", title: "Save a tree to text and load it back", emoji: '🏋️', group: "Hard practice" },
    { id: "diameter", title: "Diameter of a tree", emoji: '🏋️', group: "Expert practice" },
    { id: "max-path-sum", title: "Maximum path sum", emoji: '🏋️', group: "Expert practice" },
    { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
    { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
  ];
}

function graphSections() {
  return [
    { id: "what-is", title: "What a graph is", emoji: "🕸️", group: 'Lesson', keywords: ["graph", "vertex", "edge", "directed", "undirected", "weighted", "adjacency list", "adjacency matrix", "degree"] },
    { id: "bfs", title: "Breadth first search", emoji: "🌊", group: 'Lesson', keywords: ["breadth first search", "bfs", "shortest path unweighted", "queue", "distance"] },
    { id: "dfs", title: "Depth first search", emoji: "🧗", group: 'Lesson', keywords: ["depth first search", "dfs", "connected components", "recursion", "backtracking"] },
    { id: "topo", title: "Topological order", emoji: "👕", group: 'Lesson', keywords: ["topological sort", "kahn algorithm", "dag", "in-degree", "dependencies", "cycle detection"] },
    { id: "dijkstra", title: "Dijkstra's shortest paths", emoji: "🗺️", group: 'Lesson', keywords: ["dijkstra", "shortest path", "weighted graph", "relaxation", "priority queue", "bellman ford"] },
    { id: "mst", title: "Minimum spanning trees and union find", emoji: "🔌", group: 'Lesson', keywords: ["minimum spanning tree", "kruskal", "union find", "disjoint set", "path compression"] },
    { id: "grids", title: "Grids are graphs too", emoji: "🏝️", group: 'Lesson', keywords: ["grid graph", "number of islands", "flood fill", "matrix bfs", "four directions"] },
    { id: "path-exists", title: "Is there a path", emoji: '🏋️', group: "Easy practice" },
    { id: "town-judge", title: "Find the town judge", emoji: '🏋️', group: "Easy practice" },
    { id: "bipartite", title: "Split into two teams", emoji: '🏋️', group: "Medium practice" },
    { id: "rotting-oranges", title: "Rotting oranges", emoji: '🏋️', group: "Medium practice" },
    { id: "word-ladder", title: "Word ladder", emoji: '🏋️', group: "Hard practice" },
    { id: "redundant-connection", title: "The edge that makes a cycle", emoji: '🏋️', group: "Hard practice" },
    { id: "cheapest-flights", title: "Cheapest flight with at most k stops", emoji: '🏋️', group: "Expert practice" },
    { id: "bridges", title: "Critical connections", emoji: '🏋️', group: "Expert practice" },
    { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
    { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
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

function mtModules() {
  return [
    {
      id: "mt-foundations", title: "Foundations", emoji: "🧪", blurb: "What testing is, how software is built, and the levels and types of testing.",
      topics: [
      {
        id: "fundamentals", title: "Software Testing Fundamentals", emoji: "🧪",
        page: "content/manual-testing/testing-fundamentals.html",
        summary: "What software is, what testing means, manual and automation testing, tools, programming and scripting languages, white, black and gray box testing, the seven testing principles and the cost of a late bug.",
        keywords: ["software testing", "manual testing", "automation testing", "test engineer", "requirement", "bug", "QTP", "UFT", "Selenium", "LoadRunner", "JMeter", "scripting language", "programming language", "white box", "black box", "gray box", "testing principles", "exhaustive testing", "defect clustering", "pesticide paradox", "cost of a bug", "record and playback"],
        added: "2026-10-20",
        sections: [
          { id: "software", title: "What software is and who builds it", emoji: "🏦", group: 'Lesson', keywords: ["software", "business need", "customer", "client", "modules", "developer", "test engineer", "bug", "ICICI example", "requirement"] },
          { id: "testing", title: "What testing means", emoji: "🔍", group: 'Lesson', keywords: ["definition of testing", "verify against requirement", "intention to find bugs", "validation", "prerequisites", "test URL", "assigned modules", "DB schema"] },
          { id: "manual", title: "Manual testing", emoji: "🙋", group: 'Lesson', keywords: ["manual testing definition", "done first", "depends on understanding", "requirement clarity", "human judgement", "exploratory", "usability"] },
          { id: "automation", title: "Automation testing", emoji: "🤖", group: 'Lesson', keywords: ["automation testing", "tool", "test script", "record and playback", "monotony", "accuracy", "time saving", "reuse", "QTP", "UFT", "Selenium", "LoadRunner", "JMeter"] },
          { id: "languages", title: "Programming and scripting languages", emoji: "⌨️", group: 'Lesson', keywords: ["programming language", "scripting language", "compiled", "interpreted", "browser", "server", "VB Script", "JavaScript", "Python", "Shell", "Perl"] },
          { id: "boxes", title: "White box, black box and gray box", emoji: "📦", group: 'Lesson', keywords: ["white box testing", "glass box", "unit testing", "black box testing", "gray box testing", "code visible", "code invisible", "developer", "test engineer"] },
          { id: "principles", title: "The seven principles of testing", emoji: "📜", group: 'Lesson', keywords: ["seven testing principles", "ISTQB", "presence of defects", "exhaustive testing impossible", "early testing", "defect clustering", "pesticide paradox", "context dependent", "absence of errors fallacy"] },
          { id: "cost", title: "Why a late bug costs more", emoji: "💸", group: 'Lesson', keywords: ["cost of a bug", "shift left", "early testing", "requirement review", "rework", "phase", "production defect"] },
          { id: "roles", title: "Who does what in a software company", emoji: "👥", group: 'Lesson', keywords: ["business analyst", "product analyst", "architect", "development manager", "developer", "test engineer", "test lead", "test manager", "build team", "customer"] },
          { id: "valid-username", title: "Check the username rule", emoji: '🏋️', group: "Easy practice" },
          { id: "pass-rate", title: "Summarise a test run", emoji: '🏋️', group: "Easy practice" },
          { id: "break-even", title: "When does automation pay off?", emoji: '🏋️', group: "Medium practice" },
          { id: "pareto-modules", title: "Which modules hold most bugs?", emoji: '🏋️', group: "Medium practice" },
          { id: "record-playback", title: "Replay a recorded script on a new build", emoji: '🏋️', group: "Hard practice" },
          { id: "one-field-at-a-time", title: "Every combination or one field at a time?", emoji: '🏋️', group: "Hard practice" },
          { id: "data-driven-test", title: "A data driven test with a bug report", emoji: '🏋️', group: "Expert practice" },
          { id: "shift-left", title: "How many review rounds?", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "sdlc", title: "SDLC and its Models", emoji: "🔄",
        page: "content/manual-testing/sdlc-models.html",
        summary: "The software development life cycle phase by phase, service and product companies, CRS and SRS, HLD and LLD, and every model: waterfall, spiral, prototype, V and V, hybrid, Agile and Scrum, with when to choose each.",
        keywords: ["SDLC", "software development life cycle", "requirement collection", "feasibility study", "design", "HLD", "LLD", "coding", "testing", "installation", "maintenance", "waterfall model", "spiral model", "prototype model", "V model", "verification and validation", "hybrid model", "agile", "scrum", "sprint", "user story", "product backlog", "sprint backlog", "scrum master", "product owner", "daily stand up", "retrospective", "CRS", "SRS", "BRS", "FRS", "service based company", "product based company", "business analyst", "product analyst"],
        added: "2026-10-20",
        sections: [
          { id: "what-sdlc", title: "What SDLC is: build it like a house", emoji: "🏠", group: 'Lesson', keywords: ["SDLC definition", "house building analogy", "phases", "life cycle", "procedure"] },
          { id: "companies", title: "Service based and product based companies", emoji: "🏢", group: 'Lesson', keywords: ["service based company", "product based company", "business analyst", "product analyst", "Wipro", "Infosys", "TCS", "Oracle", "Microsoft", "ownership"] },
          { id: "phases", title: "The seven phases, one by one", emoji: "🪜", group: 'Lesson', keywords: ["requirement collection", "feasibility study", "high level design", "low level design", "coding", "testing", "installation", "deployment", "rollout", "maintenance", "roles per phase"] },
          { id: "requirements", title: "CRS, SRS and what makes a good requirement", emoji: "📄", group: 'Lesson', keywords: ["CRS", "customer requirement specification", "BRS", "business requirement specification", "SRS", "system requirement specification", "FRS", "functional specification", "high level", "low level", "good requirement characteristics"] },
          { id: "waterfall", title: "The waterfall model", emoji: "🌊", group: 'Lesson', keywords: ["waterfall model", "sequential", "linear", "no back tracking", "requirement change not allowed", "life critical", "machine critical", "advantages", "disadvantages"] },
          { id: "spiral", title: "The spiral model", emoji: "🌀", group: 'Lesson', keywords: ["spiral model", "iterative", "cyclic", "module by module", "dependent modules", "minor change", "major change", "regression", "Excel example"] },
          { id: "prototype", title: "The prototype model", emoji: "🧩", group: 'Lesson', keywords: ["prototype model", "dummy", "customer approval", "prototype testing", "look and feel", "web developer", "UI", "customer new to application"] },
          { id: "vmodel", title: "The V and V model (V model)", emoji: "✌️", group: 'Lesson', keywords: ["V model", "verification and validation", "review", "CRS", "SRS", "HLD", "LLD", "acceptance test document", "system test document", "integration test document", "functional test document", "UAT", "system testing", "integration testing", "functional testing", "white box testing"] },
          { id: "agile", title: "Agile and Scrum", emoji: "🏃", group: 'Lesson', keywords: ["agile", "scrum", "iterative incremental", "user story", "sprint", "release", "scrum team", "scrum master", "product owner", "pigs and chickens", "product backlog", "sprint backlog", "carry forward", "sprint planning", "daily stand up", "retrospective", "kick off"] },
          { id: "choose", title: "Hybrid models and choosing a model", emoji: "🧭", group: 'Lesson', keywords: ["hybrid model", "spiral plus prototype", "prototype plus V", "choosing SDLC model", "comparison of models"] },
          { id: "phase-order", title: "Is this SDLC plan in the right order?", emoji: '🏋️', group: "Easy practice" },
          { id: "count-sprints", title: "How many sprints?", emoji: '🏋️', group: "Easy practice" },
          { id: "waterfall-rework", title: "The price of a late change in waterfall", emoji: '🏋️', group: "Medium practice" },
          { id: "velocity-forecast", title: "Forecast with velocity", emoji: '🏋️', group: "Medium practice" },
          { id: "v-model-trace", title: "Which review should have caught it?", emoji: '🏋️', group: "Hard practice" },
          { id: "spiral-changes", title: "A spiral with a major change", emoji: '🏋️', group: "Hard practice" },
          { id: "burndown", title: "Read a sprint burndown", emoji: '🏋️', group: "Expert practice" },
          { id: "sprints-with-dependencies", title: "Plan sprints that respect dependencies", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "white-box", title: "White Box Testing", emoji: "🔬",
        page: "content/manual-testing/white-box-testing.html",
        summary: "Testing the code itself: unit test programs, JUnit and friends, path testing, condition testing, loop testing, statement and branch coverage, cyclomatic complexity, memory testing and response time testing.",
        keywords: ["white box testing", "glass box testing", "unit testing", "unit test program", "UTP", "JUnit", "NUnit", "pytest", "Jest", "path testing", "independent paths", "cyclomatic complexity", "condition testing", "branch coverage", "decision coverage", "statement coverage", "loop testing", "memory testing", "memory leak", "unused variables", "Rational Purify", "response time testing", "profiler", "Rational Quantify", "static analysis"],
        added: "2026-10-20",
        sections: [
          { id: "what-wbt", title: "What white box testing is", emoji: "🔬", group: 'Lesson', keywords: ["white box testing definition", "glass box", "unit testing", "developer", "code visible", "variables", "functions"] },
          { id: "utp", title: "Unit test programs", emoji: "🧾", group: 'Lesson', keywords: ["unit test program", "UTP", "JUnit", "NUnit", "pytest", "Jest", "assert", "pass", "fail", "review", "requirement change"] },
          { id: "paths", title: "Path testing", emoji: "🛤️", group: 'Lesson', keywords: ["path testing", "independent paths", "call tree", "main function calls sub function", "Yahoo example", "cyclomatic complexity", "control flow graph"] },
          { id: "conditions", title: "Condition testing", emoji: "🔀", group: 'Lesson', keywords: ["condition testing", "true and false", "branch coverage", "decision coverage", "condition coverage", "MC/DC", "if else"] },
          { id: "loops", title: "Loop testing", emoji: "🔁", group: 'Lesson', keywords: ["loop testing", "number of iterations", "skip loop", "one pass", "n minus 1", "n", "n plus 1", "break", "infinite loop"] },
          { id: "coverage", title: "Statement and branch coverage", emoji: "📊", group: 'Lesson', keywords: ["statement coverage", "line coverage", "branch coverage", "coverage percentage", "coverage tools", "JaCoCo", "coverage.py", "Istanbul"] },
          { id: "memory", title: "Memory testing", emoji: "🧠", group: 'Lesson', keywords: ["memory testing", "unused variables", "unused functions", "memory leak", "Rational Purify", "static analysis", "Nokia game example"] },
          { id: "response", title: "Response time testing", emoji: "⏱️", group: 'Lesson', keywords: ["response time testing", "profiler", "Rational Quantify", "slow functions", "order of checks", "performance at code level"] },
          { id: "compare", title: "White box versus black box", emoji: "⚖️", group: 'Lesson', keywords: ["white box vs black box", "developer vs tester", "code vs application", "interview questions"] },
          { id: "unit-test-leap", title: "Write a unit test program", emoji: '🏋️', group: "Easy practice" },
          { id: "cover-grades", title: "Cover every branch of a grading function", emoji: '🏋️', group: "Easy practice" },
          { id: "count-paths", title: "Count paths without listing them", emoji: '🏋️', group: "Medium practice" },
          { id: "loop-counts", title: "Choose loop test counts", emoji: '🏋️', group: "Medium practice" },
          { id: "cyclomatic", title: "Cyclomatic complexity from edges", emoji: '🏋️', group: "Hard practice" },
          { id: "statement-vs-branch", title: "Full statements, half the branches", emoji: '🏋️', group: "Hard practice" },
          { id: "dead-stores", title: "Find dead stores in a tiny program", emoji: '🏋️', group: "Expert practice" },
          { id: "cheapest-check-order", title: "Order checks for the lowest expected cost", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "testing-levels", title: "Functional, Integration and System Testing", emoji: "🪜",
        page: "content/manual-testing/testing-levels.html",
        summary: "Black box testing level by level: functional testing with real values, integration testing and its types (top down, bottom up, sandwich, big bang, stubs and drivers), system testing end to end, smoke testing, ad hoc testing, UAT, alpha and beta testing, and exploratory testing.",
        keywords: ["black box testing", "functional testing", "component testing", "integration testing", "top down", "bottom up", "sandwich testing", "big bang", "incremental integration", "stub", "driver", "system testing", "end to end testing", "smoke testing", "sanity testing", "build verification test", "BVT", "dry run", "ad hoc testing", "monkey testing", "UAT", "user acceptance testing", "alpha testing", "beta testing", "exploratory testing", "domain expert", "amount transfer", "overdraft"],
        added: "2026-10-20",
        sections: [
          { id: "black-box", title: "Black box testing and the amount transfer example", emoji: "⬛", group: 'Lesson', keywords: ["black box testing", "requirement", "test URL", "objects", "components", "FAN", "TAN", "amount transfer requirement"] },
          { id: "functional", title: "Functional testing", emoji: "🧩", group: 'Lesson', keywords: ["functional testing", "component testing", "unit testing in black box", "each component independently", "positive testing", "negative testing", "over testing", "test coverage", "Gmail compose"] },
          { id: "integration", title: "Integration testing", emoji: "🔗", group: 'Lesson', keywords: ["integration testing", "data flow", "interface between modules", "amount transfer balance", "Gmail integration scenarios", "sent items", "inbox", "trash"] },
          { id: "it-types", title: "Types of integration testing, stubs and drivers", emoji: "🌲", group: 'Lesson', keywords: ["incremental integration", "top down", "bottom up", "sandwich", "hybrid", "non incremental", "big bang", "stub", "driver", "IRCTC", "HRMS"] },
          { id: "system", title: "System testing", emoji: "🌐", group: 'Lesson', keywords: ["system testing", "end to end", "whole system", "overdraft example", "production like environment", "end to end scenario"] },
          { id: "smoke", title: "Smoke testing", emoji: "💨", group: 'Lesson', keywords: ["smoke testing", "sanity testing", "build verification test", "BVT", "dry run", "skim testing", "basic and critical features", "blocker", "formal smoke", "informal smoke"] },
          { id: "adhoc", title: "Ad hoc and exploratory testing", emoji: "🐒", group: 'Lesson', keywords: ["ad hoc testing", "monkey testing", "random testing", "negative scenarios", "exploratory testing", "requirement missing", "domain expert"] },
          { id: "uat", title: "User acceptance testing, alpha and beta", emoji: "🤝", group: 'Lesson', keywords: ["UAT", "user acceptance testing", "customer", "business scenarios", "domain expert", "alpha testing", "beta testing", "service based", "product based", "trial version"] },
          { id: "levels", title: "The levels of testing at a glance", emoji: "📶", group: 'Lesson', keywords: ["levels of testing", "unit", "integration", "system", "acceptance", "functional vs non functional"] },
          { id: "classify-level", title: "Which level of testing is this?", emoji: '🏋️', group: "Easy practice" },
          { id: "subject-length", title: "Test the subject length", emoji: '🏋️', group: "Easy practice" },
          { id: "to-field", title: "Validate the To field", emoji: '🏋️', group: "Medium practice" },
          { id: "plan-stubs", title: "Plan stubs for top down integration", emoji: '🏋️', group: "Medium practice" },
          { id: "gmail-data-flow", title: "Check Gmail's data flow", emoji: '🏋️', group: "Hard practice" },
          { id: "smoke-first-days", title: "Smoke first or deep first?", emoji: '🏋️', group: "Hard practice" },
          { id: "od-rules", title: "Overdraft rules over time", emoji: '🏋️', group: "Expert practice" },
          { id: "big-bang-suspects", title: "Why big bang hides the culprit", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "environments", title: "Applications, Environments and Builds", emoji: "🖥️",
        page: "content/manual-testing/apps-environments.html",
        summary: "The parts of an application, standalone, client server and web applications, web, application and database servers, development, test, staging and production environments, SQL for testers, the build process, test cycles, respin, patch and release.",
        keywords: ["user interface", "business logic", "database", "front end", "back end", "GUI", "CLI", "standalone application", "client server application", "web application", "web server", "application server", "database server", "Apache", "Tomcat", "IIS", "Oracle", "MySQL", "production environment", "development environment", "test environment", "staging environment", "test URL", "SQL for testers", "build", "version control", "build tool", "WAR", "JAR", "test cycle", "respin", "patch", "blocker", "release", "version"],
        added: "2026-10-20",
        sections: [
          { id: "parts", title: "The three parts of an application", emoji: "🧱", group: 'Lesson', keywords: ["user interface", "UI", "business logic", "BL", "database", "DB", "front end", "back end", "GUI", "CLI"] },
          { id: "app-types", title: "Standalone, client server and web applications", emoji: "🗂️", group: 'Lesson', keywords: ["standalone application", "exe", "client server application", "web application", "URL", "advantages", "disadvantages", "data sharing"] },
          { id: "web-arch", title: "Web application architecture", emoji: "🕸️", group: 'Lesson', keywords: ["web server", "application server", "database server", "request flow", "Gmail architecture", "pages", "business logic", "tables"] },
          { id: "environments", title: "Development, test, staging and production environments", emoji: "🏗️", group: 'Lesson', keywords: ["production environment", "live server", "development server", "test server", "QA server", "staging server", "test URL", "reproduce bug", "fix", "configuration"] },
          { id: "sql", title: "SQL for testers, and skipping a 30 day wait", emoji: "🗄️", group: 'Lesson', keywords: ["SQL", "database testing", "update query", "select", "join", "waiting cases", "DB schema", "cross check UI and database"] },
          { id: "builds", title: "The build process", emoji: "📦", group: 'Lesson', keywords: ["build", "version control", "build tool", "compile", "compress", "zip", "war", "jar", "build number", "install on test server", "test cycle"] },
          { id: "respin", title: "Respin, patch and blocker", emoji: "🩹", group: 'Lesson', keywords: ["respin", "patch", "blocker bug", "hot fix", "test cycle", "temporary fix", "permanent fix", "tube puncture analogy"] },
          { id: "release", title: "Release, version and the road to production", emoji: "🚀", group: 'Lesson', keywords: ["release", "version", "release vs version", "final product", "UAT", "production", "Cheeta", "Tiger", "Lion"] },
          { id: "ui-bl-db", title: "UI, business logic or database?", emoji: '🏋️', group: "Easy practice" },
          { id: "build-ids", title: "Build numbers", emoji: '🏋️', group: "Easy practice" },
          { id: "server-hits", title: "Count server hits in a session", emoji: '🏋️', group: "Medium practice" },
          { id: "environment-urls", title: "Environment URLs", emoji: '🏋️', group: "Medium practice" },
          { id: "sql-cross-check", title: "Cross check the screen with SQL", emoji: '🏋️', group: "Hard practice" },
          { id: "build-schedule", title: "Schedule the builds", emoji: '🏋️', group: "Hard practice" },
          { id: "credit-dates", title: "Real calendar dates for the 30 day rule", emoji: '🏋️', group: "Expert practice" },
          { id: "patch-or-respin", title: "Patch or respin?", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      }
      ]
    },
    {
      id: "mt-design-defects", title: "Test design and defects", emoji: "📝", blurb: "Writing test cases with design techniques and managing bugs from report to closure.",
      topics: [
      {
        id: "test-design", title: "Test Case Design and Documents", emoji: "📝",
        page: "content/manual-testing/test-design.html",
        summary: "Test documents end to end: scenarios, the test case template, error guessing, equivalence partitioning, boundary value analysis, decision tables and state transitions, functional, integration and system test cases, review, the repository, RTM, the test execution report and STLC.",
        keywords: ["test documents", "test scenario", "test case", "test case template", "header body footer", "pre condition", "test data", "severity", "error guessing", "equivalence partitioning", "boundary value analysis", "BVA", "EP", "decision table", "state transition", "pairwise testing", "general practice method", "functional test case", "integration test case", "system test case", "test case review", "test case repository", "baseline", "RTM", "requirement traceability matrix", "TER", "test execution report", "STLC", "software testing life cycle", "requirement acceptance meeting"],
        added: "2026-10-20",
        sections: [
          { id: "why-docs", title: "Why test documents, and how they are made", emoji: "📚", group: 'Lesson', keywords: ["test documents", "without documents", "consistency", "requirement repository", "assign modules", "requirement acceptance meeting", "walk through"] },
          { id: "scenarios", title: "Test scenarios", emoji: "🗺️", group: 'Lesson', keywords: ["test scenario", "high level", "do and check", "module by module", "product based", "service based"] },
          { id: "test-case", title: "The test case template", emoji: "📋", group: 'Lesson', keywords: ["test case", "template", "header", "body", "footer", "test case name", "type", "requirement number", "module", "status", "severity", "pre condition", "test data", "release", "version", "steps", "expected result", "actual result", "author", "reviewer", "approver"] },
          { id: "techniques", title: "Error guessing, equivalence partitioning and boundary values", emoji: "🎯", group: 'Lesson', keywords: ["test case design techniques", "error guessing", "equivalence partitioning", "range", "set", "boolean", "boundary value analysis", "general practice method", "criteria", "maximum test coverage"] },
          { id: "more-techniques", title: "Decision tables, state transitions and pairwise testing", emoji: "🧮", group: 'Lesson', keywords: ["decision table testing", "state transition testing", "pairwise testing", "all pairs", "combinatorial testing", "rules", "conditions", "actions"] },
          { id: "cases", title: "Functional, integration and system test cases", emoji: "🧾", group: 'Lesson', keywords: ["functional test case", "integration test case", "system test case", "amount transfer", "overdraft", "login", "steps", "expected result"] },
          { id: "review", title: "Test case review", emoji: "🔎", group: 'Lesson', keywords: ["test case review", "author", "reviewer", "review comments", "review template", "approval", "review ethics"] },
          { id: "rtm", title: "The repository and the RTM", emoji: "🧭", group: 'Lesson', keywords: ["test case repository", "baseline", "centralised", "smoke test cases", "requirement traceability matrix", "RTM", "CRM", "missing test case", "drawback"] },
          { id: "ter", title: "The test execution report", emoji: "📊", group: 'Lesson', keywords: ["test execution report", "TER", "pass percentage", "fail percentage", "modules", "exit criteria", "stability"] },
          { id: "stlc", title: "STLC: the software testing life cycle", emoji: "🔁", group: 'Lesson', keywords: ["STLC", "software testing life cycle", "system study", "test plan", "test documents", "RTM", "test execution", "defect tracking", "TER", "retrospect", "post mortem"] },
          { id: "ep-values", title: "Equivalence partitioning values", emoji: '🏋️', group: "Easy practice" },
          { id: "case-names", title: "Build and parse test case names", emoji: '🏋️', group: "Easy practice" },
          { id: "bva-list", title: "Boundary values for a whole form", emoji: '🏋️', group: "Medium practice" },
          { id: "case-status", title: "Pass, fail or partial", emoji: '🏋️', group: "Medium practice" },
          { id: "rtm-matrix", title: "An RTM with orphans", emoji: '🏋️', group: "Hard practice" },
          { id: "review-rounds", title: "Review rounds", emoji: '🏋️', group: "Hard practice" },
          { id: "loan-bug", title: "Catch the interest band bug", emoji: '🏋️', group: "Expert practice" },
          { id: "pairwise", title: "Generate pairwise tests", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "defects", title: "Defect Management", emoji: "🐞",
        page: "content/manual-testing/defect-management.html",
        summary: "Defect, bug, error, issue and failure, the defect life cycle, who a bug is assigned to, invalid, duplicate, not reproducible, can't fix, deferred and RFE, severity and priority with examples, the bug report template, bug tracking tools and querying the bug repository.",
        keywords: ["defect", "bug", "error", "issue", "failure", "wrong implementation", "missing implementation", "extra implementation", "defect life cycle", "bug life cycle", "new", "open", "assigned", "fixed", "retest", "closed", "reopen", "invalid", "duplicate", "bug repository", "not reproducible", "can't fix", "deferred", "RFE", "request for enhancement", "severity", "priority", "blocker", "critical", "major", "minor", "P1", "bug report", "steps to reproduce", "Jira", "Bugzilla", "Mantis", "Quality Center", "query a bug", "defect clustering", "latent bug", "golden bug", "hot fix"],
        added: "2026-10-20",
        sections: [
          { id: "terms", title: "Defect, bug, error, issue and failure", emoji: "🔤", group: 'Lesson', keywords: ["defect", "bug", "error", "issue", "failure", "deviation from requirement", "wrong implementation", "missing implementation", "extra implementation"] },
          { id: "life-cycle", title: "The defect life cycle", emoji: "🔄", group: 'Lesson', keywords: ["defect life cycle", "bug life cycle", "new", "open", "assigned", "fixed", "retest", "closed", "reopen", "status"] },
          { id: "assign", title: "Who gets the bug", emoji: "📨", group: 'Lesson', keywords: ["assign bug", "developer", "development lead", "test lead", "bug review", "freshers"] },
          { id: "statuses", title: "Invalid and duplicate", emoji: "🚫", group: 'Lesson', keywords: ["invalid bug", "tester misunderstood", "developer misunderstood", "duplicate bug", "bug repository", "search before logging", "common modules"] },
          { id: "not-repro", title: "Not reproducible", emoji: "🔍", group: 'Lesson', keywords: ["not reproducible", "incomplete steps", "server mismatch", "platform mismatch", "data mismatch", "build mismatch", "inconsistent bug", "screenshot"] },
          { id: "other-statuses", title: "Can't fix, deferred and RFE", emoji: "🗂️", group: 'Lesson', keywords: ["can't fix", "deferred", "postponed", "next release", "RFE", "request for enhancement", "suggestion", "full life cycle"] },
          { id: "severity", title: "Severity and priority", emoji: "🚦", group: 'Lesson', keywords: ["severity", "priority", "blocker", "critical", "major", "minor", "urgent", "P1", "P2", "P3", "P4", "impact", "which bug first", "examples"] },
          { id: "report", title: "Writing the bug report", emoji: "📝", group: 'Lesson', keywords: ["bug report template", "bug id", "test case name", "module", "status", "reporter", "assigned to", "CC", "release", "version", "severity", "priority", "test data", "server", "OS and browser", "build", "screenshot", "brief description", "steps to reproduce", "observation", "expected result"] },
          { id: "tools", title: "Bug tracking tools and queries", emoji: "🛠️", group: 'Lesson', keywords: ["bug tracking tool", "Jira", "Bugzilla", "Mantis", "Quality Center", "ALM", "manual bug report drawbacks", "logging a bug", "query", "search", "comments"] },
          { id: "wrong-missing-extra", title: "Wrong, missing or extra", emoji: '🏋️', group: "Easy practice" },
          { id: "status-history", title: "Validate a status history", emoji: '🏋️', group: "Easy practice" },
          { id: "severity-table", title: "Bugs by module and severity", emoji: '🏋️', group: "Medium practice" },
          { id: "merge-duplicates", title: "Merge duplicate reports", emoji: '🏋️', group: "Medium practice" },
          { id: "bug-aging", title: "How long do bugs stay open", emoji: '🏋️', group: "Hard practice" },
          { id: "reopen-roles", title: "Who may change the status", emoji: '🏋️', group: "Hard practice" },
          { id: "defer-plan", title: "Fix or defer before release", emoji: '🏋️', group: "Expert practice" },
          { id: "retest-plan", title: "Which fixed bugs to retest now", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      }
      ]
    },
    {
      id: "mt-beyond", title: "Regression and non functional testing", emoji: "🚀", blurb: "Retesting, regression, automation decisions, performance, compatibility and more.",
      topics: [
      {
        id: "regression", title: "Regression, Retesting and Automation", emoji: "🔁",
        page: "content/manual-testing/regression-automation.html",
        summary: "Regression testing across releases and builds, unit, regional and full regression, impact analysis, retesting versus regression, why and when to automate, the automation life cycle, what cannot be automated, and the classic comparisons: smoke and sanity, static and dynamic, QA and QC.",
        keywords: ["regression testing", "regression test cases", "regression test suite", "unit regression", "regional regression", "full regression", "impact analysis", "impact area", "retesting", "build level regression", "release level regression", "automation testing", "automation life cycle", "test script", "QTP", "UFT", "Selenium", "LoadRunner", "JMeter", "break even", "cannot be automated", "captcha", "smoke vs sanity", "static testing", "dynamic testing", "verification", "validation", "QA vs QC", "functional vs non-functional"],
        added: "2026-10-20",
        sections: [
          { id: "what-regression", title: "What regression testing is", emoji: "🔁", group: 'Lesson', keywords: ["regression testing", "regression test cases", "releases", "new features", "deleted features", "modified features", "re-execute old test cases", "existing functionality"] },
          { id: "types", title: "Unit, regional and full regression", emoji: "🎚️", group: 'Lesson', keywords: ["unit regression", "regional regression", "full regression", "impact area", "critical application", "how much to retest"] },
          { id: "impact", title: "Impact analysis and the regression suite", emoji: "🧩", group: 'Lesson', keywords: ["impact analysis", "customer", "developer", "tester", "business knowledge", "coding knowledge", "product knowledge", "test lead consolidates", "regression test suite", "packet"] },
          { id: "retest", title: "Retesting versus regression", emoji: "↩️", group: 'Lesson', keywords: ["retesting", "regression", "build level regression", "bug fix", "impact area", "release level regression"] },
          { id: "automation", title: "Why regression moves to automation", emoji: "🤖", group: 'Lesson', keywords: ["automation testing", "test script", "tool", "time saving", "accuracy", "reuse", "break even", "functional testing tools", "performance testing tools", "QTP", "UFT", "Selenium", "LoadRunner", "JMeter"] },
          { id: "auto-lc", title: "The automation life cycle", emoji: "⚙️", group: 'Lesson', keywords: ["automation life cycle", "manual team", "automation team", "test cases", "stable application", "tool", "script execution", "failed scripts", "manual retest"] },
          { id: "cant-automate", title: "What cannot be automated", emoji: "🚧", group: 'Lesson', keywords: ["cannot automate", "unstable features", "captcha", "virtual keyboard", "OTP", "complex", "human judgement", "usability"] },
          { id: "compare", title: "The classic comparisons", emoji: "⚖️", group: 'Lesson', keywords: ["smoke vs sanity", "static vs dynamic", "verification", "validation", "QA vs QC", "quality assurance", "quality control", "functional vs non-functional", "preventive", "detective"] },
          { id: "repo-growth", title: "Repository growth", emoji: '🏋️', group: "Easy practice" },
          { id: "classify-activity", title: "Name the testing activity", emoji: '🏋️', group: "Easy practice" },
          { id: "regression-type", title: "Choose the regression type", emoji: '🏋️', group: "Medium practice" },
          { id: "pick-cases", title: "Pick the affected test cases", emoji: '🏋️', group: "Medium practice" },
          { id: "ripple", title: "Ripple effect with a depth limit", emoji: '🏋️', group: "Hard practice" },
          { id: "payback", title: "Automation payback by release", emoji: '🏋️', group: "Hard practice" },
          { id: "risk-knapsack", title: "Riskiest cases in 120 minutes", emoji: '🏋️', group: "Expert practice" },
          { id: "flaky-scripts", title: "Spot flaky scripts", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "non-functional", title: "Non-functional Testing", emoji: "⚡",
        page: "content/manual-testing/non-functional-testing.html",
        summary: "Compatibility testing across operating systems, browsers and hardware with virtual machines, forward and backward compatibility, usability checklists, and performance testing: response time, load, stability, the LoadRunner process, bottlenecks and tuning, and load, stress, scalability, volume and soak testing.",
        keywords: ["non-functional testing", "compatibility testing", "software compatibility", "hardware compatibility", "operating system", "browser", "base platform", "virtual machine", "VMware", "remote desktop", "compatibility issues", "alignment", "overlapping", "broken links", "forward compatibility", "backward compatibility", "usability testing", "usability checklist", "breadcrumb", "performance testing", "response time", "load", "stability", "LoadRunner", "JMeter", "virtual users", "bottleneck", "tuning", "load testing", "stress testing", "scalability testing", "volume testing", "soak testing", "endurance testing", "percentile", "Little's law"],
        added: "2026-10-20",
        sections: [
          { id: "what-nft", title: "What non-functional testing covers", emoji: "⚡", group: 'Lesson', keywords: ["non-functional testing", "functional testing", "how well", "compatibility", "usability", "performance", "security", "when", "functionally stable"] },
          { id: "compat", title: "Compatibility testing", emoji: "🖥️", group: 'Lesson', keywords: ["compatibility testing", "software compatibility", "hardware compatibility", "operating systems", "browsers", "RAM", "processor", "graphics card", "most used platforms", "compatibility issues", "alignment", "overlapped objects", "scattered objects", "font", "colour", "broken links"] },
          { id: "vm", title: "Virtual machines and the compatibility process", emoji: "🧰", group: 'Lesson', keywords: ["virtual machine", "VMware", "VirtualBox", "remote desktop", "base platform", "end to end", "multi boot", "forward compatibility", "backward compatibility", "internal application", "public application"] },
          { id: "usability", title: "Usability testing", emoji: "🙂", group: 'Lesson', keywords: ["usability testing", "user friendliness", "easy to access", "easy to understand", "look and feel", "navigation", "checklist", "breadcrumb", "home and logout links", "alt text", "usability report"] },
          { id: "performance", title: "Performance testing", emoji: "🚀", group: 'Lesson', keywords: ["performance testing", "response time", "load", "stability", "virtual users", "LoadRunner", "JMeter", "script", "scenario", "distribute load", "result graph", "average", "maximum", "minimum", "percentile"] },
          { id: "bottleneck", title: "Bottlenecks and tuning", emoji: "🧪", group: 'Lesson', keywords: ["bottleneck", "tuning", "analyse results", "architect", "DBA", "network admin", "code", "database", "server", "hardware", "network", "re-execute"] },
          { id: "types", title: "Load, stress, scalability, volume and soak", emoji: "📈", group: 'Lesson', keywords: ["load testing", "stress testing", "scalability testing", "stability testing", "volume testing", "soak testing", "endurance testing", "desired load", "upward", "downward", "crash"] },
          { id: "platform-combos", title: "Sensible platform combinations", emoji: '🏋️', group: "Easy practice" },
          { id: "breadcrumbs", title: "Breadcrumbs and required links", emoji: '🏋️', group: "Easy practice" },
          { id: "forward-backward", title: "Forward and backward gaps", emoji: '🏋️', group: "Medium practice" },
          { id: "split-users", title: "Split virtual users exactly", emoji: '🏋️', group: "Medium practice" },
          { id: "littles-law", title: "Little's law", emoji: '🏋️', group: "Hard practice" },
          { id: "sla-streak", title: "Longest breach in a stability test", emoji: '🏋️', group: "Hard practice" },
          { id: "capacity-knee", title: "Estimate capacity from measurements", emoji: '🏋️', group: "Expert practice" },
          { id: "soak-leak", title: "Project a memory leak", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      }
      ]
    },
    {
      id: "mt-planning", title: "Planning and closure", emoji: "🗺️", blurb: "The test plan, entry and exit criteria, risks and the end of a test cycle.",
      topics: [
      {
        id: "test-plan", title: "The Test Plan", emoji: "🗓️",
        page: "content/manual-testing/test-plan.html",
        summary: "The test plan and its thirteen sections: objective, scope, approach, schedule, methodology, roles, environment, deliverables, assumptions, risks, mitigation, tools, and entry and exit criteria, with estimation, a risk matrix, parallel testing and the whole testing journey in one view.",
        keywords: ["test plan", "objective", "scope", "in scope", "out of scope", "approach", "schedule", "test methodology", "roles and responsibilities", "test manager", "test lead", "test engineer", "test environment", "test deliverables", "assumptions", "risks", "mitigation", "contingency", "backup plan", "tools", "entry criteria", "exit criteria", "estimation", "risk matrix", "parallel testing", "hot fix", "latent bug", "golden bug"],
        added: "2026-10-20",
        sections: [
          { id: "what-plan", title: "What a test plan is", emoji: "🗓️", group: 'Lesson', keywords: ["test plan", "leads and managers", "dynamic document", "before testing starts", "future testing activities"] },
          { id: "scope", title: "Objective, scope and approach", emoji: "🎯", group: 'Lesson', keywords: ["objective", "scope", "in scope", "out of scope", "features to be tested", "features not to be tested", "approach", "flow chart", "technical writer"] },
          { id: "schedule", title: "Schedule and methodology", emoji: "📅", group: 'Lesson', keywords: ["schedule", "time duration", "milestones", "test scenarios date", "test cases date", "test execution date", "release date", "test methodology", "types of testing", "estimation"] },
          { id: "roles", title: "Roles and responsibilities", emoji: "👥", group: 'Lesson', keywords: ["roles and responsibilities", "test manager", "test lead", "test engineer", "escalation", "daily status meeting", "assigning modules", "primary contact", "secondary contact"] },
          { id: "env", title: "Test environment and deliverables", emoji: "📦", group: 'Lesson', keywords: ["test environment", "main server", "backup server", "staging", "test engineer machine", "hardware", "software", "deliverables", "test cases", "scripts", "RTM", "TER", "list of bugs", "user manual", "platforms tested"] },
          { id: "risks", title: "Assumptions, risks and mitigation", emoji: "⚠️", group: 'Lesson', keywords: ["assumptions", "risks", "mitigation", "contingency", "backup plan", "tester leaves", "server down", "primary and secondary contact", "backup server", "risk matrix", "probability", "impact"] },
          { id: "tools", title: "Tools", emoji: "🛠️", group: 'Lesson', keywords: ["tools", "functional testing tool", "performance testing tool", "test management tool", "licences", "UFT", "QTP", "Selenium", "LoadRunner", "JMeter", "Quality Center", "ALM", "Jira", "virtual users"] },
          { id: "criteria", title: "Entry and exit criteria", emoji: "🚦", group: 'Lesson', keywords: ["entry criteria", "exit criteria", "coding completed", "build installed", "test documents prepared", "resources ready", "executed percentage", "pass percentage", "blocker", "critical", "major", "minor", "release decision"] },
          { id: "more", title: "Parallel testing and the whole journey", emoji: "🧭", group: 'Lesson', keywords: ["parallel testing", "old and new version", "same inputs", "anomalies", "hot fix", "latent bug", "golden bug", "the testing journey", "STLC"] },
          { id: "scope-split", title: "In scope and out of scope", emoji: '🏋️', group: "Easy practice" },
          { id: "contacts", title: "Primary and secondary contacts", emoji: '🏋️', group: "Easy practice" },
          { id: "working-days", title: "Schedule around weekends and holidays", emoji: '🏋️', group: "Medium practice" },
          { id: "entry-check", title: "Check the entry criteria", emoji: '🏋️', group: "Medium practice" },
          { id: "progress", title: "Track execution and forecast the finish", emoji: '🏋️', group: "Hard practice" },
          { id: "tool-cost", title: "Licensed or open source", emoji: '🏋️', group: "Hard practice" },
          { id: "critical-path", title: "Critical path of the test schedule", emoji: '🏋️', group: "Expert practice" },
          { id: "balance", title: "Balance modules across testers", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      }
      ]
    }
  ];
}

function cjsModule() {
  return {
      id: "complete-java-session", title: "Complete Java Session", emoji: "🎓", blurb: "The session course in order: from how Java runs to reading test data files, ending with all 66 practice programs.",
      topics: [
      {
        id: "cjs-basics", title: "How Java Runs: Classes, Variables and Data Types", emoji: "🚀",
        page: "content/java/cjs-java-basics.html",
        summary: "How a Java program is compiled and run by the JVM, JDK, JRE and JVM, classes and objects, the eight primitive types with sizes, ranges and defaults, local and global variables, identifier rules, widening and narrowing, static and non-static members, the main method and access modifiers.",
        keywords: ["javac", "java", "bytecode", "JVM", "JRE", "JDK", "JIT", "platform independent", "class", "object", "new keyword", "reference variable", "primitive data types", "byte", "short", "int", "long", "float", "double", "char", "boolean", "default values", "non-primitive", "local variable", "instance variable", "static variable", "identifier rules", "keywords", "widening", "narrowing", "type casting", "overflow", "static", "non-static", "main method", "public static void main", "access modifiers", "public", "private", "protected", "default"],
        added: "2026-10-20",
        sections: [
          { id: "execution", title: "From source code to output", emoji: "⚙️", group: 'Lesson', keywords: ["javac", "bytecode", ".class file", "JVM", "class loader", "bytecode verifier", "interpreter", "JIT compiler", "JDK", "JRE", "platform independent", "write once run anywhere"] },
          { id: "class-object", title: "Classes and objects", emoji: "🏗️", group: 'Lesson', keywords: ["class", "blueprint", "members", "variables", "methods", "object", "state", "behaviour", "new keyword", "constructor", "reference variable", "instantiation"] },
          { id: "datatypes", title: "Data types, sizes and default values", emoji: "🔢", group: 'Lesson', keywords: ["primitive", "non-primitive", "boolean", "char", "byte", "short", "int", "long", "float", "double", "size", "range", "default value", "null", "String", "wrapper"] },
          { id: "variables", title: "Variables and identifiers", emoji: "🏷️", group: 'Lesson', keywords: ["local variable", "global variable", "instance variable", "static variable", "declaration", "initialisation", "identifier rules", "keywords", "lower case", "compilation error"] },
          { id: "casting", title: "Widening, narrowing and overflow", emoji: "🔀", group: 'Lesson', keywords: ["widening", "narrowing", "implicit", "explicit", "cast", "byte + byte", "int arithmetic", "compilation error", "loss of data", "overflow", "wrap around"] },
          { id: "static", title: "Static and non-static members", emoji: "📌", group: 'Lesson', keywords: ["static", "non-static", "instance", "class level", "object level", "static block", "cannot access non-static from static", "object reference", "shared counter"] },
          { id: "main", title: "The main method", emoji: "🚪", group: 'Lesson', keywords: ["public static void main", "String[] args", "entry point", "why static", "why public", "why void", "command line arguments"] },
          { id: "access", title: "Access modifiers", emoji: "🔐", group: 'Lesson', keywords: ["access modifiers", "public", "private", "protected", "default", "package private", "visibility", "same class", "same package", "subclass", "other package"] },
          { id: "exact-division", title: "Exact division and averages", emoji: '🏋️', group: "Easy practice" },
          { id: "swap-two", title: "Swap two numbers three ways", emoji: '🏋️', group: "Easy practice" },
          { id: "smallest-type", title: "Smallest type that fits", emoji: '🏋️', group: "Medium practice" },
          { id: "int-overflow", title: "Find the overflow", emoji: '🏋️', group: "Medium practice" },
          { id: "ascii-shift", title: "ASCII arithmetic and a Caesar shift", emoji: '🏋️', group: "Hard practice" },
          { id: "twos-complement", title: "Read two's complement", emoji: '🏋️', group: "Hard practice" },
          { id: "float-vs-double", title: "float and double precision", emoji: '🏋️', group: "Expert practice" },
          { id: "numeric-promotion", title: "Predict the result type", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "cjs-control-flow", title: "Operators, Conditions, Loops and Patterns", emoji: "🔁",
        page: "content/java/cjs-control-flow.html",
        summary: "Java operators and precedence, pre and post increment, short circuit logic, the modulo trap with negative numbers, if, else if, nested if and switch, while, do while, for and for each loops, break and continue with labels, classic loop programs such as prime checks and number reversal, and star pattern programs with nested loops.",
        keywords: ["arithmetic operators", "relational operators", "logical operators", "short circuit", "assignment operators", "compound assignment", "increment", "decrement", "pre increment", "post increment", "ternary operator", "bitwise operators", "operator precedence", "modulo", "if", "else if", "nested if", "switch", "switch expression", "while loop", "do while loop", "for loop", "for each loop", "break", "continue", "labelled break", "infinite loop", "prime number", "reverse number", "palindrome number", "pattern programs", "nested loops", "Scanner"],
        added: "2026-10-20",
        sections: [
          { id: "operators", title: "Operators and precedence", emoji: "➗", group: 'Lesson', keywords: ["arithmetic", "relational", "logical", "assignment", "compound assignment", "unary", "increment", "decrement", "ternary", "bitwise", "shift", "precedence", "modulo", "integer division"] },
          { id: "conditions", title: "if, else if, nested if and switch", emoji: "🔀", group: 'Lesson', keywords: ["if", "if else", "else if ladder", "nested if", "switch", "case", "break", "default", "fall through", "switch expression", "arrow", "ternary", "Scanner input"] },
          { id: "loops", title: "while, do while, for and for each", emoji: "🔁", group: 'Lesson', keywords: ["while loop", "do while loop", "for loop", "for each loop", "enhanced for", "initialisation", "condition", "update", "infinite loop", "iteration"] },
          { id: "break-continue", title: "break, continue and labelled loops", emoji: "⏭️", group: 'Lesson', keywords: ["break", "continue", "labelled break", "nested loop", "exit early", "skip iteration", "search"] },
          { id: "loop-programs", title: "Classic loop programs, and a prime bug", emoji: "🔢", group: 'Lesson', keywords: ["prime number", "factors", "counter", "flag", "square root", "reverse number", "palindrome", "sum of digits", "even numbers", "boundary value", "dry run"] },
          { id: "patterns", title: "Pattern programs with nested loops", emoji: "✳️", group: 'Lesson', keywords: ["pattern programs", "nested loops", "rows", "columns", "square", "right triangle", "inverted triangle", "pyramid", "number pattern", "Floyd triangle", "O(n²)"] },
          { id: "even-odd", title: "Even or odd, three ways", emoji: '🏋️', group: "Easy practice" },
          { id: "largest-smallest", title: "Largest and smallest of three", emoji: '🏋️', group: "Easy practice" },
          { id: "fizzbuzz", title: "FizzBuzz", emoji: '🏋️', group: "Medium practice" },
          { id: "leap-year", title: "Leap years", emoji: '🏋️', group: "Medium practice" },
          { id: "armstrong", title: "Armstrong numbers", emoji: '🏋️', group: "Hard practice" },
          { id: "digital-root", title: "Digital root and neon numbers", emoji: '🏋️', group: "Hard practice" },
          { id: "reverse-int", title: "Reverse an integer safely", emoji: '🏋️', group: "Expert practice" },
          { id: "more-patterns", title: "Floyd's triangle, number pyramid and diamond", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "cjs-methods", title: "Methods and Constructors", emoji: "🧰",
        page: "content/java/cjs-methods-constructors.html",
        summary: "Why methods exist, method signature and body, concrete and abstract methods, calling static and instance methods, parameters, arguments and return values, pass by value with primitives and references, method overloading, the call stack and recursion, constructors, the default constructor the compiler adds, parameterised constructors, the this keyword and constructor chaining with this().",
        keywords: ["method", "function", "method signature", "method body", "concrete method", "abstract method", "static method", "instance method", "invoke", "class name dot method", "parameter", "argument", "return type", "void", "pass by value", "reference", "method overloading", "call stack", "stack frame", "recursion", "StackOverflowError", "constructor", "default constructor", "parameterised constructor", "no return type", "this keyword", "this()", "constructor chaining", "constructor overloading", "toString", "object address", "=="],
        added: "2026-10-20",
        sections: [
          { id: "why-methods", title: "Why methods", emoji: "📦", group: 'Lesson', keywords: ["method", "block of code", "specific task", "code reuse", "redundancy", "readability", "maintainability", "signature", "body", "concrete", "abstract"] },
          { id: "calling", title: "Calling static and instance methods", emoji: "📞", group: 'Lesson', keywords: ["static method", "instance method", "direct call", "ClassName.method()", "object reference", "recommended", "not recommended", "another class"] },
          { id: "params", title: "Parameters, return values and pass by value", emoji: "↩️", group: 'Lesson', keywords: ["parameter", "argument", "return", "return type", "void", "pass by value", "primitive copy", "reference copy", "mutate object", "reassign reference"] },
          { id: "overloading", title: "Method overloading", emoji: "🎛️", group: 'Lesson', keywords: ["method overloading", "same name", "different parameters", "number of parameters", "types of parameters", "order", "compile time polymorphism", "return type not enough", "default arguments"] },
          { id: "call-stack", title: "The call stack and recursion", emoji: "🥞", group: 'Lesson', keywords: ["call stack", "stack frame", "local variables", "return address", "recursion", "base case", "factorial", "StackOverflowError", "depth"] },
          { id: "constructors", title: "Constructors", emoji: "🏗️", group: 'Lesson', keywords: ["constructor", "same name as class", "no return type", "initialise fields", "default constructor", "compiler adds", "parameterised constructor", "compilation error", "private constructor"] },
          { id: "this", title: "this and constructor chaining", emoji: "🔗", group: 'Lesson', keywords: ["this keyword", "current object", "this.field", "shadowing", "this.method()", "this()", "constructor chaining", "first statement", "order of initialisation"] },
          { id: "area-overload", title: "Overloaded area and perimeter", emoji: '🏋️', group: "Easy practice" },
          { id: "simple-interest", title: "Simple and compound interest", emoji: '🏋️', group: "Easy practice" },
          { id: "factorial", title: "Factorial three ways, and where it overflows", emoji: '🏋️', group: "Medium practice" },
          { id: "fast-power", title: "Power with a loop and by halving", emoji: '🏋️', group: "Medium practice" },
          { id: "fibonacci", title: "Fibonacci: counting the calls", emoji: '🏋️', group: "Hard practice" },
          { id: "bank-account", title: "Bank account with chained constructors", emoji: '🏋️', group: "Hard practice" },
          { id: "employee-raise", title: "Raise for employees older than 25", emoji: '🏋️', group: "Expert practice" },
          { id: "electric-bill", title: "Slab based electricity bill", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "cjs-oop", title: "OOP in Practice", emoji: "🧬",
        page: "content/java/cjs-oop.html",
        summary: "The four pillars of object oriented programming as the session teaches them: compile time polymorphism with overloading and method mapping, inheritance in its single, multilevel and hierarchical forms, why multiple inheritance of classes is blocked, runtime polymorphism with overriding, super and constructor order, upcasting, downcasting and ClassCastException, abstract classes, interfaces with default and static methods, and encapsulation with getters and setters.",
        keywords: ["object oriented programming", "OOP", "four pillars", "polymorphism", "compile time polymorphism", "runtime polymorphism", "method overloading", "method mapping", "widening", "inheritance", "extends", "single inheritance", "multilevel inheritance", "hierarchical inheritance", "multiple inheritance", "diamond problem", "hybrid inheritance", "method overriding", "@Override", "super", "super()", "constructor order", "upcasting", "downcasting", "ClassCastException", "instanceof", "abstraction", "abstract class", "abstract method", "interface", "implements", "default method", "static method in interface", "public static final", "encapsulation", "private", "getter", "setter", "data hiding"],
        added: "2026-10-20",
        sections: [
          { id: "pillars", title: "The four pillars", emoji: "🏛️", group: 'Lesson', keywords: ["OOP", "four pillars", "polymorphism", "inheritance", "abstraction", "encapsulation", "class", "object", "reuse", "hide details"] },
          { id: "mapping", title: "Overloading and method mapping", emoji: "🎯", group: 'Lesson', keywords: ["method overloading", "compile time polymorphism", "static binding", "method mapping", "widening", "byte to short", "char to int", "most specific method", "unboxing", "ambiguity"] },
          { id: "inheritance", title: "Inheritance and its types", emoji: "🌳", group: 'Lesson', keywords: ["inheritance", "extends", "parent class", "child class", "superclass", "subclass", "single level", "multilevel", "hierarchical", "multiple", "hybrid", "diamond problem", "Object class", "is-a", "instanceof"] },
          { id: "overriding", title: "Method overriding", emoji: "🔄", group: 'Lesson', keywords: ["method overriding", "runtime polymorphism", "dynamic binding", "same signature", "@Override", "cannot reduce visibility", "static methods", "final methods", "private methods", "super.method()"] },
          { id: "super", title: "super and the order of construction", emoji: "⬆️", group: 'Lesson', keywords: ["super keyword", "super()", "super.method()", "super.field", "constructor chaining", "parent constructor first", "implicit super()", "field hiding"] },
          { id: "casting", title: "Upcasting, downcasting and instanceof", emoji: "🔃", group: 'Lesson', keywords: ["upcasting", "downcasting", "implicit", "explicit", "parent reference", "child object", "ClassCastException", "instanceof", "pattern matching", "common members", "reference type", "object type"] },
          { id: "abstraction", title: "Abstraction with abstract classes", emoji: "🎭", group: 'Lesson', keywords: ["abstraction", "abstract class", "abstract method", "no object", "concrete method", "constructor in abstract class", "child must override", "partial abstraction"] },
          { id: "interfaces", title: "Interfaces", emoji: "🔌", group: 'Lesson', keywords: ["interface", "implements", "public abstract", "public static final", "default method", "static method", "JDK 8", "multiple inheritance", "diamond", "Interface.super.method()", "combination inheritance", "contract"] },
          { id: "encapsulation", title: "Encapsulation with getters and setters", emoji: "💊", group: 'Lesson', keywords: ["encapsulation", "data hiding", "private fields", "getter", "setter", "validation", "read only", "write once", "final field", "JavaBean", "Python property", "JavaScript private field"] },
          { id: "shapes", title: "Polymorphic shapes", emoji: '🏋️', group: "Easy practice" },
          { id: "animals", title: "Animal sounds with super", emoji: '🏋️', group: "Easy practice" },
          { id: "payroll", title: "Payroll with four kinds of staff", emoji: '🏋️', group: "Medium practice" },
          { id: "product", title: "An encapsulated product", emoji: '🏋️', group: "Medium practice" },
          { id: "payments", title: "Payment methods on interfaces", emoji: '🏋️', group: "Hard practice" },
          { id: "safe-cast", title: "Safe casting with instanceof", emoji: '🏋️', group: "Hard practice" },
          { id: "init-order", title: "Static blocks, instance blocks and constructors", emoji: '🏋️', group: "Expert practice" },
          { id: "toll-booth", title: "Toll booth for a vehicle family", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "cjs-apis", title: "Strings, Arrays, Collections and Exceptions", emoji: "🧺",
        page: "content/java/cjs-core-apis.html",
        summary: "The everyday Java library a tester uses: the String pool, == versus equals and immutability, the common String methods, classic string programs, arrays and their limits, wrapper classes with boxing, parsing and the Integer cache, the Collection framework with List, Set and Map, and exception handling with try, catch, finally, throw, throws and checked versus unchecked exceptions.",
        keywords: ["String", "String pool", "string constant pool", "immutable", "==", "equals", "equalsIgnoreCase", "compareTo", "intern", "length", "charAt", "substring", "indexOf", "lastIndexOf", "contains", "startsWith", "endsWith", "replace", "replaceAll", "split", "trim", "isEmpty", "isBlank", "String.format", "StringBuilder", "reverse a string", "palindrome", "camel case", "remove duplicates", "array", "ArrayIndexOutOfBoundsException", "Arrays.sort", "Arrays.toString", "wrapper class", "autoboxing", "unboxing", "Integer.parseInt", "Double.parseDouble", "Integer cache", "NumberFormatException", "Collection framework", "List", "ArrayList", "LinkedList", "ListIterator", "generics", "Set", "HashSet", "LinkedHashSet", "TreeSet", "Map", "HashMap", "LinkedHashMap", "TreeMap", "stream", "filter", "map", "exception", "try", "catch", "finally", "multiple catch", "throw", "throws", "checked exception", "unchecked exception", "RuntimeException", "custom exception", "try with resources"],
        added: "2026-10-20",
        sections: [
          { id: "string-pool", title: "Strings, the pool and equals", emoji: "🧵", group: 'Lesson', keywords: ["String", "String pool", "string constant pool", "literal", "new String", "heap", "==", "equals", "equalsIgnoreCase", "intern", "immutable", "compareTo"] },
          { id: "string-methods", title: "String methods", emoji: "🔤", group: 'Lesson', keywords: ["length", "concat", "toLowerCase", "toUpperCase", "charAt", "substring", "contains", "startsWith", "endsWith", "indexOf", "lastIndexOf", "replace", "replaceAll", "String.format", "isEmpty", "isBlank", "trim", "strip", "split", "toCharArray", "join"] },
          { id: "string-programs", title: "Classic string programs", emoji: "🔁", group: 'Lesson', keywords: ["reverse a string", "StringBuilder reverse", "palindrome", "camel case", "regex split", "first letter lower rest upper", "remove duplicate characters", "LinkedHashSet"] },
          { id: "arrays", title: "Arrays", emoji: "📏", group: 'Lesson', keywords: ["array", "fixed size", "index", "default values", "length", "for loop", "for each", "O(1) access", "Arrays.toString", "Arrays.sort", "clone", "two dimensional array", "ArrayIndexOutOfBoundsException"] },
          { id: "wrappers", title: "Wrapper classes", emoji: "🎁", group: 'Lesson', keywords: ["wrapper class", "Integer", "Double", "Boolean", "Character", "autoboxing", "unboxing", "parseInt", "parseDouble", "parseBoolean", "valueOf", "Integer cache", "-128 to 127", "NumberFormatException", "NullPointerException"] },
          { id: "collections", title: "The Collection framework", emoji: "🗂️", group: 'Lesson', keywords: ["Collection framework", "Collection", "List", "Set", "Queue", "Map", "ArrayList", "LinkedList", "HashSet", "LinkedHashSet", "TreeSet", "HashMap", "LinkedHashMap", "TreeMap", "generics", "ListIterator", "stream", "filter", "map", "duplicates", "order"] },
          { id: "exceptions", title: "Exception handling", emoji: "🧯", group: 'Lesson', keywords: ["exception", "try", "catch", "finally", "multiple catch", "order of catch blocks", "ArithmeticException", "NullPointerException", "Exception", "Throwable", "Error", "program flow", "finally with return"] },
          { id: "throw-throws", title: "Checked and unchecked, throw and throws", emoji: "🎯", group: 'Lesson', keywords: ["checked exception", "unchecked exception", "RuntimeException", "IOException", "FileNotFoundException", "throw", "throws", "custom exception", "extends Exception", "try with resources", "exception hierarchy"] },
          { id: "char-count", title: "Count vowels, consonants, digits and symbols", emoji: '🏋️', group: "Easy practice" },
          { id: "anagram", title: "Anagram check, two ways", emoji: '🏋️', group: "Easy practice" },
          { id: "word-frequency", title: "Word frequency with a map", emoji: '🏋️', group: "Medium practice" },
          { id: "first-unique", title: "First unique character and remove duplicates", emoji: '🏋️', group: "Medium practice" },
          { id: "second-largest", title: "Second largest distinct value", emoji: '🏋️', group: "Hard practice" },
          { id: "price-parser", title: "Parse prices safely with BigDecimal", emoji: '🏋️', group: "Hard practice" },
          { id: "brackets", title: "Balanced brackets with a stack", emoji: '🏋️', group: "Expert practice" },
          { id: "retry", title: "Retry runner with a custom checked exception", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "cjs-files", title: "Reading Test Data Files", emoji: "📂",
        page: "content/java/cjs-read-files.html",
        summary: "Data driven testing with external files: project paths and user.dir, text files with Files.readAllLines and BufferedReader, properties files for configuration, CSV rows for test data, JSON with Jackson and JsonPath expressions, Excel sheets with Apache POI and the Fillo style queries the session uses, and turning rows into the Object[][] shape a TestNG data provider expects.",
        keywords: ["data driven testing", "test data", "src/test/resources", "user.dir", "System.getProperty", "Path", "Paths.get", "Files.readAllLines", "BufferedReader", "FileReader", "Files.write", "try with resources", "Properties", "properties file", "getProperty", "config reader", "CSV", "split with -1", "JSON", "Jackson", "ObjectMapper", "JsonNode", "readTree", "path", "at", "JSON Pointer", "JsonPath", "$.firstName", "Excel", "xlsx", "xls", "Apache POI", "Workbook", "Sheet", "Row", "Cell", "DataFormatter", "WorkbookFactory", "Fillo", "select query", "Object[][]", "DataProvider", "IOException", "FileNotFoundException"],
        added: "2026-10-20",
        sections: [
          { id: "data-driven", title: "Why test data lives in files", emoji: "🗄️", group: 'Lesson', keywords: ["data driven testing", "separate data from code", "src/test/resources", "user.dir", "project root", "relative path", "absolute path", "Path", "Paths.get", "Maven layout"] },
          { id: "text", title: "Text files", emoji: "📄", group: 'Lesson', keywords: ["text file", "Files.readAllLines", "List of String", "BufferedReader", "readLine", "null at end", "try with resources", "Files.write", "createDirectories", "large files", "memory"] },
          { id: "properties", title: "Properties files for configuration", emoji: "⚙️", group: 'Lesson', keywords: ["properties file", "key=value", "comments", "Properties.load", "getProperty", "default value", "System.getProperty override", "-D", "ConfigReader", "environment"] },
          { id: "csv", title: "CSV rows", emoji: "🧾", group: 'Lesson', keywords: ["CSV", "comma separated values", "header row", "split", "limit -1", "empty field", "trailing empty strings", "quoted commas", "test rows", "positive and negative data"] },
          { id: "json", title: "JSON with Jackson and JsonPath", emoji: "🧩", group: 'Lesson', keywords: ["JSON", "object", "array", "key", "value", "nested", "Jackson", "ObjectMapper", "readTree", "JsonNode", "get", "path", "at", "JSON Pointer", "asText", "asInt", "isNull", "JsonPath", "DocumentContext", "parse", "read", "$", "wildcard", "filter"] },
          { id: "excel", title: "Excel with Apache POI and Fillo", emoji: "📊", group: 'Lesson', keywords: ["Excel", "xlsx", "xls", "Apache POI", "Workbook", "WorkbookFactory", "XSSFWorkbook", "HSSFWorkbook", "Sheet", "Row", "Cell", "getLastRowNum", "getLastCellNum", "DataFormatter", "Fillo", "select query", "update query", "where clause", "write back"] },
          { id: "data-provider", title: "From rows to a data driven test", emoji: "🔁", group: 'Lesson', keywords: ["Object[][]", "DataProvider", "TestNG", "parametrize", "pytest", "one test many rows", "expected result column", "positive and negative data"] },
          { id: "log-levels", title: "Count log levels in a test log", emoji: '🏋️', group: "Easy practice" },
          { id: "env-switch", title: "One config per environment", emoji: '🏋️', group: "Easy practice" },
          { id: "validate-json", title: "Validate an API response", emoji: '🏋️', group: "Medium practice" },
          { id: "csv-report", title: "CSV test report with a pass rate", emoji: '🏋️', group: "Medium practice" },
          { id: "update-json", title: "Update and save JSON", emoji: '🏋️', group: "Hard practice" },
          { id: "select-cases", title: "Pick test cases from an Excel sheet", emoji: '🏋️', group: "Hard practice" },
          { id: "compare-csv", title: "Compare expected and actual data", emoji: '🏋️', group: "Expert practice" },
          { id: "flatten-json", title: "Flatten JSON into JsonPath addresses", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "cjs-programs", title: "Practice Program Bank", emoji: "🏋️",
        page: "content/java/cjs-program-bank.html",
        summary: "All 66 programs from the session's assignment list, each linked to a solution in Java, Python and JavaScript: number programs such as swaps, primes, factors, reversing with overflow, Armstrong and neon numbers, string programs such as word reversal, run length counts, overlapping patterns and repeated characters, array programs such as missing digits and moving zeros, and arithmetic beyond long with BigInteger.",
        keywords: ["Java programs", "interview programs", "swap two numbers", "XOR swap", "ASCII", "A to Z", "is alphabet", "prime numbers 1 to n", "factors", "count digits", "multiplication table", "power", "closed paths", "reverse a number", "integer overflow", "palindrome number", "Armstrong number", "neon number", "digit root", "remove spaces", "character occurrence", "reverse words", "run length", "overlapping pattern count", "upper case letters", "capitalise words", "duplicate characters", "first repeating character", "first repeated word", "average", "sort", "missing numbers", "largest", "smallest", "move zeros", "unique values", "running total", "BigInteger", "BigDecimal"],
        added: "2026-10-20",
        sections: [
          { id: "bank", title: "The whole list in one place", emoji: "🗂️", group: 'Lesson', keywords: ["program list", "assignment list", "checklist", "interview preparation", "solved where", "progress"] },
          { id: "basics", title: "Arithmetic, swaps and characters", emoji: "🔢", group: 'Lesson', keywords: ["multiply", "decimal output", "integer division", "exact division", "cast to double", "swap with temp", "swap without temp", "XOR swap", "overflow", "ASCII", "char to int", "A to Z", "Character.isLetter"] },
          { id: "numbers", title: "Number programs", emoji: "🧮", group: 'Lesson', keywords: ["prime numbers 1 to n", "even numbers", "factors", "count digits", "do while", "multiplication table", "power", "Math.pow returns double", "closed paths in digits"] },
          { id: "reverse", title: "Reverse, palindrome, Armstrong and neon", emoji: "🔄", group: 'Lesson', keywords: ["reverse a number", "n % 10", "n / 10", "negative numbers", "trailing zero", "integer overflow", "1534236469", "palindrome number", "Armstrong number", "153", "neon number", "9", "digit root"] },
          { id: "strings", title: "String programs", emoji: "🔤", group: 'Lesson', keywords: ["remove spaces", "replace", "occurrence of a character", "reverse words", "split", "run length", "aabbbccccdddda", "overlapping pattern", "indexOf from index", "upper case letters", "Character.isUpperCase", "capitalise first letter", "capitalise each word"] },
          { id: "repeats", title: "Repeated characters and words", emoji: "🔁", group: 'Lesson', keywords: ["occurrence of every character", "LinkedHashMap", "duplicate characters", "first repeating character", "4th repeating character", "last repeating character", "first repeated word", "HashSet add returns false"] },
          { id: "arrays", title: "Array programs", emoji: "📊", group: 'Lesson', keywords: ["average", "sort", "Arrays.sort", "missing numbers 0 to 9", "boolean array", "largest", "smallest", "divisible by 4 or 6", "move zeros to end", "move zeros to front", "stable order", "unique values", "LinkedHashSet", "TreeSet"] },
          { id: "big-numbers", title: "Running totals and numbers beyond long", emoji: "🐘", group: 'Lesson', keywords: ["running total", "prefix sums", "BigInteger", "add", "subtract", "multiply", "divide", "mod", "pow", "overflow", "Long.MAX_VALUE", "BigDecimal", "money"] },
          { id: "missing-number", title: "The missing number from 1 to n", emoji: '🏋️', group: "Easy practice" },
          { id: "rotate-array", title: "Rotate an array by k", emoji: '🏋️', group: "Easy practice" },
          { id: "two-sum", title: "Pairs that add up to a target", emoji: '🏋️', group: "Medium practice" },
          { id: "word-stats", title: "Word statistics", emoji: '🏋️', group: "Medium practice" },
          { id: "compress", title: "String compression", emoji: '🏋️', group: "Hard practice" },
          { id: "merge-sorted", title: "Merge two sorted arrays", emoji: '🏋️', group: "Hard practice" },
          { id: "spiral", title: "Read a matrix in a spiral", emoji: '🏋️', group: "Expert practice" },
          { id: "big-factorial", title: "The digits of 100!", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      }
      ]
    };
}

function tngModule() {
  return {
      id: "testng-framework", title: "TestNG Framework", emoji: "🧪", blurb: "Annotations, suites, data providers, listeners and framework design.",
      topics: [
      {
        id: "tng-basics", title: "TestNG Foundations: Annotations, Assertions and Test Control", emoji: "🧪",
        page: "content/testng/testng-foundations.html",
        summary: "What TestNG adds to plain Java, setting it up with Maven, writing a first test class, the full annotation lifecycle from @BeforeSuite to @AfterSuite, hard and soft assertions, test attributes such as priority, enabled, description, timeOut, invocationCount and expectedExceptions, the default run order, and dependencies with dependsOnMethods and alwaysRun.",
        keywords: ["TestNG", "test framework", "Maven dependency", "pom.xml", "@Test", "@BeforeSuite", "@AfterSuite", "@BeforeTest", "@AfterTest", "@BeforeClass", "@AfterClass", "@BeforeMethod", "@AfterMethod", "annotations", "lifecycle", "Assert", "assertEquals", "assertTrue", "assertFalse", "assertNotNull", "SoftAssert", "assertAll", "hard assert", "soft assert", "priority", "enabled", "description", "timeOut", "invocationCount", "expectedExceptions", "expectedExceptionsMessageRegExp", "dependsOnMethods", "alwaysRun", "skipped tests", "run order", "pytest", "fixtures", "Mocha", "hooks"],
        added: "2026-10-20",
        sections: [
          { id: "why-testng", title: "Why a test framework", emoji: "🎯", group: 'Lesson', keywords: ["TestNG", "JUnit", "main method", "test runner", "report", "pass", "fail", "skip", "annotations", "Maven", "pom.xml", "dependency", "Surefire", "test-output"] },
          { id: "first-test", title: "A first test class", emoji: "✅", group: 'Lesson', keywords: ["@Test", "Assert.assertEquals", "actual expected order", "message", "assertTrue", "assertFalse", "PASSED", "FAILED", "test report", "code under test"] },
          { id: "lifecycle", title: "The annotation lifecycle", emoji: "🔄", group: 'Lesson', keywords: ["@BeforeSuite", "@BeforeTest", "@BeforeClass", "@BeforeMethod", "@Test", "@AfterMethod", "@AfterClass", "@AfterTest", "@AfterSuite", "order", "setup", "teardown", "browser per class", "page per method"] },
          { id: "assertions", title: "Hard and soft assertions", emoji: "⚖️", group: 'Lesson', keywords: ["Assert", "hard assert", "SoftAssert", "assertAll", "assertEquals", "assertNotEquals", "assertTrue", "assertNull", "assertNotNull", "assertEqualsNoOrder", "collect failures", "message"] },
          { id: "attributes", title: "Test attributes", emoji: "🏷️", group: 'Lesson', keywords: ["priority", "enabled", "description", "timeOut", "invocationCount", "threadPoolSize", "expectedExceptions", "expectedExceptionsMessageRegExp", "alphabetical order", "ThreadTimeoutException"] },
          { id: "dependencies", title: "Dependencies between tests", emoji: "🔗", group: 'Lesson', keywords: ["dependsOnMethods", "dependsOnGroups", "alwaysRun", "skipped", "cascade", "hard dependency", "soft dependency", "independent tests"] },
          { id: "text-utils", title: "Tests for a text utility", emoji: '🏋️', group: "Easy practice" },
          { id: "hook-counter", title: "Count how often each hook runs", emoji: '🏋️', group: "Easy practice" },
          { id: "cart-tests", title: "Shopping cart tests that find a bug", emoji: '🏋️', group: "Medium practice" },
          { id: "form-soft", title: "Validate a form with soft asserts", emoji: '🏋️', group: "Medium practice" },
          { id: "account-exceptions", title: "Expected exceptions on a bank account", emoji: '🏋️', group: "Hard practice" },
          { id: "run-order", title: "Predict the run order", emoji: '🏋️', group: "Hard practice" },
          { id: "password-boundaries", title: "Find a boundary bug in a password rule", emoji: '🏋️', group: "Expert practice" },
          { id: "lifecycle-table", title: "A table driven multiplication test", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "tng-suites", title: "Suites, Groups, Parameters and Data Providers", emoji: "🧾",
        page: "content/testng/testng-suites-data.html",
        summary: "Organising and feeding tests with TestNG: the structure of testng.xml with suite, test, classes, methods, include and exclude, groups for smoke and regression runs, @Parameters with suite and test level values and @Optional, data providers with Object[][], named providers, Iterator providers that read files, indices, and parallel execution with thread-count and thread safe code.",
        keywords: ["testng.xml", "suite", "test tag", "classes", "class", "methods", "include", "exclude", "packages", "groups", "smoke", "regression", "sanity", "@BeforeGroups", "dependsOnGroups", "@Parameters", "parameter", "@Optional", "suite level parameter", "test level parameter", "cross browser", "@DataProvider", "Object[][]", "dataProvider name", "Iterator<Object[]>", "indices", "data driven", "CSV data provider", "JSON data provider", "parallel", "thread-count", "parallel methods", "parallel classes", "parallel tests", "ThreadLocal", "AtomicInteger", "pytest markers", "pytest -m", "pytest -k", "parametrize", "mocha --grep"],
        added: "2026-10-20",
        sections: [
          { id: "suite-xml", title: "The testng.xml suite file", emoji: "🧾", group: 'Lesson', keywords: ["testng.xml", "suite", "test", "classes", "class", "methods", "include", "exclude", "packages", "verbose", "DOCTYPE", "run from file", "mvn test", "suiteXmlFile"] },
          { id: "groups", title: "Groups for smoke and regression runs", emoji: "🏷️", group: 'Lesson', keywords: ["groups", "include group", "exclude group", "smoke", "regression", "sanity", "@BeforeGroups", "alwaysRun", "dependsOnGroups", "pytest markers", "pytest -m", "mocha grep tags"] },
          { id: "parameters", title: "Parameters from testng.xml", emoji: "⚙️", group: 'Lesson', keywords: ["@Parameters", "parameter", "suite level", "test level", "override", "@Optional", "default value", "cross browser", "browser parameter", "baseUrl", "String only"] },
          { id: "data-provider", title: "Data providers", emoji: "📋", group: 'Lesson', keywords: ["@DataProvider", "Object[][]", "dataProvider attribute", "name", "one row per run", "arguments", "test report with arguments", "parametrize", "positive and negative data"] },
          { id: "provider-files", title: "Data providers that read files", emoji: "📂", group: 'Lesson', keywords: [] },
          { id: "parallel", title: "Parallel execution", emoji: "⚡", group: 'Lesson', keywords: ["parallel", "methods", "classes", "tests", "instances", "thread-count", "threadPoolSize", "data-provider-thread-count", "ThreadLocal", "AtomicInteger", "ConcurrentHashMap", "thread safety", "Selenium Grid"] },
          { id: "email-rule", title: "Valid and invalid email providers", emoji: '🏋️', group: "Easy practice" },
          { id: "group-run", title: "Regression without slow tests", emoji: '🏋️', group: "Easy practice" },
          { id: "cross-browser", title: "Layout on three browsers", emoji: '🏋️', group: "Medium practice" },
          { id: "rerun-rows", title: "Rerun selected rows with indices", emoji: '🏋️', group: "Medium practice" },
          { id: "json-provider", title: "Shipping rules from a JSON file", emoji: '🏋️', group: "Hard practice" },
          { id: "shared-provider", title: "A provider class shared by two tests", emoji: '🏋️', group: "Hard practice" },
          { id: "pairwise", title: "Pairwise browser combinations", emoji: '🏋️', group: "Expert practice" },
          { id: "thread-local", title: "A ThreadLocal driver in parallel", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      },
      {
        id: "tng-advanced", title: "Listeners, Retries, Factories and Framework Design", emoji: "🛠️",
        page: "content/testng/testng-advanced.html",
        summary: "The parts of TestNG that turn tests into a framework: ITestListener for screenshots and logs on failure, IRetryAnalyzer for flaky infrastructure, @Factory for running a class once per data set, SkipException for conditional skips, the Page Object Model with a BaseTest, reports and testng-failed.xml, and how it all fits into Maven and a CI pipeline.",
        keywords: ["ITestListener", "listener", "@Listeners", "onTestFailure", "screenshot on failure", "ITestResult", "ITestContext", "ISuiteListener", "IReporter", "IRetryAnalyzer", "retryAnalyzer", "flaky test", "@Factory", "factory with data provider", "SkipException", "conditional skip", "Page Object Model", "page object", "BaseTest", "WebDriver", "driver factory", "locators", "testng-failed.xml", "emailable-report.html", "test-output", "Maven Surefire", "CI pipeline", "Jenkins", "GitHub Actions", "pytest hooks", "conftest.py", "pytest-rerunfailures", "mocha retries"],
        added: "2026-10-20",
        sections: [
          { id: "listeners", title: "Listeners", emoji: "👂", group: 'Lesson', keywords: ["ITestListener", "@Listeners", "onTestStart", "onTestSuccess", "onTestFailure", "onTestSkipped", "onStart", "onFinish", "ITestResult", "ITestContext", "screenshot", "logging", "listeners in testng.xml"] },
          { id: "retry", title: "Retrying flaky tests", emoji: "🔁", group: 'Lesson', keywords: ["IRetryAnalyzer", "retryAnalyzer", "retry count", "flaky", "intermittent", "infrastructure", "timeout", "retry hides bugs", "IAnnotationTransformer", "pytest-rerunfailures", "mocha this.retries"] },
          { id: "factory", title: "@Factory: one class, many instances", emoji: "🏭", group: 'Lesson', keywords: ["@Factory", "constructor with data", "Object[]", "factory with dataProvider", "instances", "per language", "per role", "parallel instances", "parametrised class"] },
          { id: "skip", title: "Conditional skips", emoji: "⏭️", group: 'Lesson', keywords: ["SkipException", "skip at runtime", "environment check", "health check", "destructive test", "pytest.skip", "skipif", "mocha this.skip", "skipped not failed"] },
          { id: "framework", title: "A framework: Page Objects and a BaseTest", emoji: "🏗️", group: 'Lesson', keywords: ["Page Object Model", "page class", "locators", "actions", "no assertions in pages", "BaseTest", "@BeforeMethod driver", "driver factory", "ThreadLocal", "config reader", "utilities", "test layer", "project structure"] },
          { id: "reports-ci", title: "Reports, reruns and CI", emoji: "📊", group: 'Lesson', keywords: ["test-output", "emailable-report.html", "index.html", "testng-results.xml", "testng-failed.xml", "rerun failures", "Maven Surefire", "suiteXmlFiles", "mvn test", "-Dbrowser", "Jenkins", "GitHub Actions", "Extent Reports", "Allure"] },
          { id: "result-counter", title: "A listener that sets the build colour", emoji: '🏋️', group: "Easy practice" },
          { id: "search-page", title: "A search page object", emoji: '🏋️', group: "Easy practice" },
          { id: "slowest-tests", title: "Find the slowest tests", emoji: '🏋️', group: "Medium practice" },
          { id: "role-factory", title: "A factory fed by a data provider", emoji: '🏋️', group: "Medium practice" },
          { id: "rerun-file", title: "Build a rerun file for failures", emoji: '🏋️', group: "Hard practice" },
          { id: "explicit-wait", title: "An explicit wait with a fake clock", emoji: '🏋️', group: "Hard practice" },
          { id: "product-page", title: "Check a product page with soft asserts", emoji: '🏋️', group: "Expert practice" },
          { id: "retry-config", title: "A retry limit from configuration", emoji: '🏋️', group: "Expert practice" },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      }
      ]
    };
}

function apiManualModule() {
  return {
      id: 'manual-api', title: 'Manual API testing course', emoji: '📨', blurb: 'From the first HTTP request to contract, security and AI API testing.',
      topics: [
      {
        id: 'manual-api-testing', title: 'Manual API Testing: Basics to Expert', emoji: '🔌',
        page: 'content/api-testing/manual-api-testing.html',
        summary: 'HTTP, methods, status codes, headers, JSON, REST, SOAP, GraphQL and gRPC, Postman and curl, OpenAPI, JWT and OAuth 2.0 with PKCE, test design, validation, chaining, pagination, rate limits, caching, idempotency keys, Problem Details, the OWASP API Top 10, performance, async APIs, contract testing, mocking, CI, AI and MCP APIs, with a live mock API playground and seven hidden bugs.',
        keywords: ['API testing', 'manual API testing', 'REST', 'HTTP', 'status codes', 'Postman', 'curl', 'Bruno', 'OpenAPI', 'Swagger', 'JWT', 'OAuth', 'PKCE', 'idempotency', 'ETag', '304', '429', 'rate limit', 'pagination', 'BOLA', 'OWASP API Top 10', 'mass assignment', 'Problem Details', 'RFC 9457', 'GraphQL', 'gRPC', 'WebSocket', 'webhook', 'contract testing', 'Pact', 'WireMock', 'Newman', 'percentile', 'p95', 'MCP', 'LLM API'],
        added: '2026-10-20',
        sections: [
          { id: 'what-is-api', title: "What an API is and why we test it", emoji: '🔌', group: 'Level 1 · Foundations' },
          { id: 'http-basics', title: "How HTTP carries a request", emoji: '📨', group: 'Level 1 · Foundations' },
          { id: 'methods', title: "HTTP methods, safety and idempotency", emoji: '🛠️', group: 'Level 1 · Foundations' },
          { id: 'status-codes', title: "Status codes", emoji: '🚦', group: 'Level 1 · Foundations' },
          { id: 'headers', title: "Headers, cookies and content negotiation", emoji: '🏷️', group: 'Level 1 · Foundations' },
          { id: 'data-formats', title: "JSON, XML and other payloads", emoji: '🧾', group: 'Level 1 · Foundations' },
          { id: 'api-styles', title: "REST, SOAP, GraphQL, gRPC, WebSocket and webhooks", emoji: '🧭', group: 'Level 1 · Foundations' },
          { id: 'tools', title: "Tools: Postman, curl, Bruno and friends", emoji: '🧰', group: 'Level 2 · Core skills' },
          { id: 'api-docs', title: "Reading API docs and OpenAPI", emoji: '📘', group: 'Level 2 · Core skills' },
          { id: 'auth', title: "Authentication and authorization", emoji: '🔐', group: 'Level 2 · Core skills' },
          { id: 'test-design', title: "Designing API test cases", emoji: '✍️', group: 'Level 2 · Core skills' },
          { id: 'validations', title: "What to check in every response", emoji: '✅', group: 'Level 2 · Core skills' },
          { id: 'chaining', title: "Variables, chaining and end to end flows", emoji: '🔗', group: 'Level 2 · Core skills' },
          { id: 'lab', title: "API playground and bug hunt", emoji: '🧪', group: 'Hands on' },
          { id: 'pagination', title: "Pagination, filtering and sorting", emoji: '📄', group: 'Level 3 · Advanced' },
          { id: 'rate-limits', title: "Rate limits, caching and idempotency keys", emoji: '⏱️', group: 'Level 3 · Advanced' },
          { id: 'errors', title: "Error handling and Problem Details", emoji: '🧯', group: 'Level 3 · Advanced' },
          { id: 'security', title: "API security testing: the OWASP API Top 10", emoji: '🛡️', group: 'Level 3 · Advanced' },
          { id: 'performance', title: "Performance testing for APIs", emoji: '📈', group: 'Level 3 · Advanced' },
          { id: 'async', title: "Async APIs: webhooks, polling and queues", emoji: '📬', group: 'Level 3 · Advanced' },
          { id: 'scenarios', title: "Real world scenario walkthroughs", emoji: '🌍', group: 'Level 3 · Advanced' },
          { id: 'contracts', title: "Contract testing and versioning", emoji: '🤝', group: 'Level 4 · Expert and latest' },
          { id: 'mocking', title: "Mocks, service virtualization and test data", emoji: '🎭', group: 'Level 4 · Expert and latest' },
          { id: 'graphql-grpc', title: "Testing GraphQL, gRPC, WebSocket and SSE", emoji: '📡', group: 'Level 4 · Expert and latest' },
          { id: 'cicd', title: "API tests in CI, monitoring and observability", emoji: '🔭', group: 'Level 4 · Expert and latest' },
          { id: 'ai-apis', title: "Testing AI and LLM APIs and MCP servers", emoji: '🤖', group: 'Level 4 · Expert and latest' },
          { id: 'latest', title: "Latest standards and trends", emoji: '🆕', group: 'Level 4 · Expert and latest' },
          { id: 'strategy', title: "An API test strategy and great bug reports", emoji: '🗺️', group: 'Level 4 · Expert and latest' },
          { id: 'cheatsheet', title: "Cheat sheet", emoji: '📋', group: 'Hands on' },
          { id: 'interview', title: "Interview questions", emoji: '💼', group: 'Hands on' },
          { id: 'p-get-product', title: "Test cases for GET /v1/products/{id}", emoji: '🏋️', group: 'Easy practice' },
          { id: 'p-read-response', title: "Spot the problems in a response", emoji: '🏋️', group: 'Easy practice' },
          { id: 'p-boundaries', title: "Boundary tests for a coupon API", emoji: '🏋️', group: 'Medium practice' },
          { id: 'p-chain', title: "Build a chained flow in Postman", emoji: '🏋️', group: 'Medium practice' },
          { id: 'p-hunt', title: "Hunt the authorization bugs in the playground", emoji: '🏋️', group: 'Hard practice' },
          { id: 'p-pagination', title: "Plan the tests for a product list", emoji: '🏋️', group: 'Hard practice' },
          { id: 'p-contract', title: "Review a change for consumers", emoji: '🏋️', group: 'Expert practice' },
          { id: 'p-llm', title: "Test a support chatbot API", emoji: '🏋️', group: 'Expert practice' },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
        ]
      }
      ]
    };
}
