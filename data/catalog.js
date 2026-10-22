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
    hello: 'New: Maths for Machine Learning, twelve animated chapters from school basics to expert with interview questions, plus JavaScript, Manual Testing, Java and TestNG',
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
      intro: 'Start with the building blocks, then climb to expert patterns. Every ready topic has animations, everyday examples, line by line code runs and practice problems with brute force and optimized solutions. The last chapter is a bank of coding interview questions with hints and full answers.',
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
      ].concat(iqModule('dsa'))
    },
    {
      id: 'manual-testing',
      title: 'Manual Testing',
      emoji: '🐞',
      color: '#f25da0',
      blurb: 'Find bugs before your users do: test design, life cycles, bug reports and test plans.',
      intro: 'Ten chapters that follow the manual testing notes in order, from what testing is to the test plan. Every diagram is redrawn as an animation, every idea has an everyday example, and each chapter ends with practice programs in Java, Python and JavaScript, quizzes from easy to expert and a narrator in six languages. The last chapter collects the interview questions asked most, with hints and full answers.',
      tags: ['STLC', 'Test cases', 'Bug life cycle', 'Regression', 'Test plan'],
      modules: mtModules().concat(iqModule('manual-testing'))
    },
    {
      id: 'java',
      title: 'Java',
      emoji: '☕',
      color: '#ff9238',
      blurb: 'Core Java from your first identifier to the JVM, with every example compiled and run.',
      intro: 'Start with the Complete Java Session track: seven chapters that follow the session programs from the first class to reading Excel files, ending with all 66 practice programs. Then go deeper with nineteen reference chapters in seven modules. Every code block was compiled and run with JDK 21, and the real output, compile error or exception is shown under it. Each chapter has a comic strip, everyday examples, quizzes from easy to expert, number practice with full working, and a narrator who reads it aloud in six languages. Finish with the Interview Questions chapter, where you answer first, then use a hint, then see the full explanation.',
      tags: ['OOP', 'Exceptions', 'Collections', 'Threads', 'JVM'],
      modules: [cjsModule()].concat(javaModules(), iqModule('java'))
    },
    {
      id: 'testng',
      title: 'TestNG',
      emoji: '🧪',
      color: '#16a34a',
      blurb: 'Annotations, suites, data providers, listeners and framework design, run on real TestNG.',
      intro: 'Three chapters that take you from a first @Test to a Page Object framework with listeners, retries and parallel runs. Every Java example runs on real TestNG with its testng.xml, and the same idea is shown with pytest and Mocha. The last chapter is a set of TestNG interview questions with hints and full answers.',
      tags: ['Annotations', 'testng.xml', 'DataProvider', 'Listeners', 'Parallel'],
      modules: [tngModule(), iqModule('testng')]
    },
    {
      id: 'javascript',
      title: 'JavaScript',
      emoji: '🟨',
      color: '#ca8a04',
      blurb: 'JavaScript from your first variable to the latest features, with unit, API and UI test automation for QA.',
      intro: 'Twenty seven chapters in eight modules take you from values and functions to async code, the DOM and Node.js, then deeper into how the engine works, debugging, regular expressions, functional style and metaprogramming. A full TypeScript module covers types, generics, advanced types, real projects and test automation written in TypeScript. Parts marked QA are the ones testers need for Selenium, Playwright and Cypress. The testing module runs unit tests in node:test, Jest, Vitest and Mocha, then API tests and full browser tests. Every example was run with Node.js 26 and every TypeScript example was checked with tsc, and the real output is shown under it. Each chapter has quizzes, number practice, coding exercises and a narrator in six languages. The last chapter is a bank of JavaScript and TypeScript interview questions with hints and full answers.',
      tags: ['ES2026', 'Async', 'TypeScript', 'Jest and Vitest', 'Playwright', 'Interview'],
      modules: jsModules().concat(iqModule('javascript'))
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
    },
    {
      id: 'api-automation',
      title: 'API Automation Testing',
      emoji: '🤖',
      color: '#8467f0',
      blurb: 'Pick a language, then a tool: Rest Assured, Playwright or HttpClient in Java, requests or Playwright in Python, Postman, Playwright or fetch in JavaScript.',
      intro: 'One page that asks for your programming language first, then for a tool: Rest Assured, Playwright or HttpClient in Java, requests or Playwright in Python, and Postman, Playwright or fetch in JavaScript. Every track runs from a first GET to schema checks, mocking, framework design, parallel runs and CI, with a real world scenario, a quiz, an animated request walkthrough and a hands on sandbox. Every code sample was run against a copy of the Restful Booker practice API.',
      tags: ['Rest Assured', 'Playwright', 'pytest', 'Postman', 'Newman', 'fetch', 'HttpClient', 'JSON Schema'],
      page: 'content/api-automation/api-automation.html'
    },
    {
      id: 'master-claude',
      title: 'Master the Claude',
      emoji: '✨',
      color: '#d97757',
      blurb: 'Get the most out of Claude: prompting, projects, Claude Code and the Claude API.',
      intro: 'Fifteen chapters in five modules take you from your first chat to your own agents and to the Claude 101 certificate. Learn to prompt well and manage context, then set up Claude Code step by step and see exactly what goes in CLAUDE.md, rules, skills, settings, hooks, subagents, output styles, plugins and .mcp.json, with ready to copy files for real jobs, including skills and rules for a QA engineer\'s day and a developer\'s day, and a screenshot for every setup step. Build MCP servers in Python, automate daily work with claude -p and GitHub Actions, call the Claude API, and build agents with tools and safety limits. Every file name, field and command was checked against the official documentation, and every script, hook, MCP server and SDK example on these pages was run for real. Parts marked Easy make a beginner path a child can follow. Chapter 15 walks through Anthropic Academy\'s Claude 101 course lesson by lesson and prepares you for the Claude Certified Associate exam. The last chapter is a bank of interview questions with hints and full answers.',
      tags: ['Prompting', 'Claude Code', 'Claude API', 'Agents', 'MCP', 'Claude 101'],
      modules: claudeModules().concat(iqModule('master-claude'))
    },

    /* ===== Coming soon subjects. Each one shows a Coming soon card until its first topic gets a page. ===== */
    {
      id: 'security-testing',
      title: 'Security Testing, Hands On',
      emoji: '🛡️',
      color: '#dc2626',
      blurb: 'Find security holes by hand and with automation, from the OWASP Top 10 to scanners in CI.',
      intro: 'A complete hands on course on security testing. You will learn to test web apps and APIs by hand, then automate the same checks with ZAP, Burp Suite and scripts that run in your pipeline.',
      tags: ['OWASP Top 10', 'Manual', 'Automation', 'ZAP', 'Burp Suite'],
      modules: [soonModule([
        ['Security testing basics', '🔰', 'What security testing is, threats, vulnerabilities and risk.'],
        ['OWASP Top 10 by hand', '🕵️', 'Test each common web weakness manually with real examples.'],
        ['Authentication and session testing', '🔑', 'Logins, tokens, cookies and session handling.'],
        ['API security testing', '🔌', 'The OWASP API Top 10 tested step by step.'],
        ['Automated scanning with ZAP and Burp Suite', '🤖', 'Run scanners, read their reports and remove false alarms.'],
        ['Security checks in CI', '🚦', 'Add scans and dependency checks to every build.']
      ])]
    },
    {
      id: 'selenium',
      title: 'Selenium',
      emoji: '🕸️',
      color: '#43b02a',
      blurb: 'Automate real browsers with Selenium WebDriver, from the first locator to a full framework.',
      intro: 'Learn Selenium WebDriver from setup to a Page Object framework with waits, data driven tests, parallel runs on Selenium Grid and reports.',
      tags: ['WebDriver', 'Locators', 'Waits', 'Page Object', 'Grid'],
      modules: [soonModule([
        ['Selenium setup and first test', '🚀', 'Install the driver and open your first page.'],
        ['Locators and XPath', '🎯', 'Find any element with CSS selectors and XPath.'],
        ['Waits and synchronisation', '⏳', 'Implicit, explicit and fluent waits without flaky tests.'],
        ['Page Object Model', '🧱', 'Keep tests clean with page classes.'],
        ['Selenium Grid and parallel runs', '🖧', 'Run tests on many browsers at once.']
      ])]
    },
    {
      id: 'playwright',
      title: 'Playwright',
      emoji: '🎭',
      color: '#2ead33',
      blurb: 'Fast and reliable browser tests with auto waiting, tracing and parallel runs.',
      intro: 'Learn Playwright for UI testing from the first test to fixtures, network mocking, visual checks, traces and CI.',
      tags: ['Locators', 'Auto wait', 'Fixtures', 'Tracing', 'CI'],
      modules: [soonModule([
        ['Playwright setup and first test', '🚀', 'Install Playwright and run your first browser test.'],
        ['Locators and assertions', '🎯', 'Role based locators and web first assertions.'],
        ['Fixtures and test hooks', '🧩', 'Share setup cleanly between tests.'],
        ['Network mocking', '🛰️', 'Intercept and fake API calls in the browser.'],
        ['Traces, reports and CI', '📊', 'Debug failures with the trace viewer and run in pipelines.']
      ])]
    },
    {
      id: 'python',
      title: 'Python',
      emoji: '🐍',
      color: '#3776ab',
      blurb: 'Python from your first variable to classes, files, testing and automation scripts.',
      intro: 'A full Python course for beginners and testers. It covers the core language, data structures, object oriented code, files, error handling, pytest and scripts that automate everyday work.',
      tags: ['Basics', 'Collections', 'OOP', 'pytest', 'Scripting'],
      modules: [soonModule([
        ['Python basics', '👋', 'Variables, types, input and output.'],
        ['Control flow and functions', '🔁', 'Conditions, loops and reusable functions.'],
        ['Lists, tuples, sets and dictionaries', '📦', 'The built in collections and when to use each.'],
        ['Object oriented Python', '🧱', 'Classes, inheritance and dunder methods.'],
        ['Files and error handling', '📁', 'Read and write files and handle exceptions.'],
        ['Testing with pytest', '🧪', 'Fixtures, parametrize and plugins.']
      ])]
    },
    {
      id: 'ml-maths',
      title: 'Maths for Machine Learning',
      emoji: '📐',
      color: '#0ea5e9',
      blurb: 'The linear algebra, calculus, probability and statistics that machine learning is built on.',
      intro: 'Twelve chapters that start from school arithmetic and climb to the maths inside real models. Every idea is shown as a step by step animation you can control, worked through with examples, and run as code in Python, JavaScript, TypeScript and Java.',
      tags: ['Linear algebra', 'Calculus', 'Probability', 'Statistics', 'Loss and metrics'],
      modules: mlMathModules().concat(iqModule('ml-maths'))
    },
    {
      id: 'machine-learning',
      title: 'Machine Learning',
      emoji: '🤖',
      color: '#7c3aed',
      blurb: 'Teach computers to learn from data, from linear regression to model evaluation.',
      intro: 'Learn supervised and unsupervised learning with animated explanations, real datasets and code you can run in Python with scikit-learn.',
      tags: ['Regression', 'Classification', 'Clustering', 'scikit-learn'],
      modules: [soonModule([
        ['What machine learning is', '👋', 'Data, features, labels and the learning loop.'],
        ['Linear and logistic regression', '📈', 'The first models every learner should know.'],
        ['Decision trees and ensembles', '🌳', 'Random forests and gradient boosting.'],
        ['Clustering', '🫧', 'K means and hierarchical clustering.'],
        ['Model evaluation', '🎯', 'Train and test splits, cross validation and metrics.']
      ])]
    },
    {
      id: 'neural-networks',
      title: 'Neural Networks',
      emoji: '🧠',
      color: '#db2777',
      blurb: 'Neurons, layers, activation functions and backpropagation, built from scratch.',
      intro: 'Build a neural network by hand first, then with a library. Each step of the forward pass and backpropagation is animated so you can see the numbers change.',
      tags: ['Perceptron', 'Activation', 'Backpropagation', 'Loss'],
      modules: [soonModule([
        ['The perceptron', '⚪', 'One neuron, weights and bias.'],
        ['Activation functions', '〰️', 'Sigmoid, tanh, ReLU and softmax.'],
        ['Forward pass and loss', '➡️', 'How a network makes a guess and scores it.'],
        ['Backpropagation', '⬅️', 'How gradients flow back and weights update.'],
        ['Training tips', '🛠️', 'Learning rate, batches, overfitting and regularisation.']
      ])]
    },
    {
      id: 'deep-learning',
      title: 'Deep Learning',
      emoji: '🧬',
      color: '#9333ea',
      blurb: 'Deep networks with PyTorch: CNNs, RNNs, transformers and transfer learning.',
      intro: 'Go from a simple network to the models used in industry today. You will train models in PyTorch and see what each layer learns.',
      tags: ['PyTorch', 'CNN', 'RNN', 'Transformers'],
      modules: [soonModule([
        ['Deep learning with PyTorch', '🔥', 'Tensors, autograd and a first training loop.'],
        ['Convolutional networks', '🖼️', 'Filters, pooling and image models.'],
        ['Recurrent networks', '🔁', 'Sequences, LSTM and GRU.'],
        ['Transformers and attention', '👀', 'Self attention and the transformer block.'],
        ['Transfer learning', '🎁', 'Reuse pretrained models for new tasks.']
      ])]
    },
    {
      id: 'computer-vision',
      title: 'Computer Vision',
      emoji: '👁️',
      color: '#0891b2',
      blurb: 'Teach machines to see: images, filters, detection and segmentation.',
      intro: 'Start with how images are stored as numbers, then work up to object detection and segmentation with OpenCV and deep learning.',
      tags: ['OpenCV', 'Image processing', 'Detection', 'Segmentation'],
      modules: [soonModule([
        ['Images as numbers', '🔢', 'Pixels, channels and colour spaces.'],
        ['Image processing with OpenCV', '🎛️', 'Filters, edges and transforms.'],
        ['Image classification', '🏷️', 'Classify pictures with CNNs.'],
        ['Object detection', '📦', 'Bounding boxes and YOLO style detectors.'],
        ['Segmentation', '🧩', 'Label every pixel in an image.']
      ])]
    },
    {
      id: 'nlp',
      title: 'Natural Language Processing',
      emoji: '💬',
      color: '#ea580c',
      blurb: 'Work with text: tokens, embeddings, language models and real NLP tasks.',
      intro: 'Learn how computers read and write text, from tokenisation and word embeddings to transformers and large language models.',
      tags: ['Tokenisation', 'Embeddings', 'Transformers', 'LLMs'],
      modules: [soonModule([
        ['Text preprocessing', '🧹', 'Tokens, stemming and stop words.'],
        ['Word embeddings', '🗺️', 'Word2Vec, GloVe and meaning as vectors.'],
        ['Text classification', '🏷️', 'Sentiment analysis and spam detection.'],
        ['Transformers for text', '🔤', 'BERT, GPT and how attention reads text.'],
        ['Large language models', '🦾', 'Prompting, fine tuning and retrieval.']
      ])]
    },
    {
      id: 'cuda',
      title: 'GPU Programming with CUDA',
      emoji: '⚡',
      color: '#76b900',
      blurb: 'Write code that runs on thousands of GPU cores with CUDA C++.',
      intro: 'Learn how a GPU runs work in parallel, then write CUDA kernels, manage memory and speed up real programs.',
      tags: ['CUDA C++', 'Kernels', 'Threads', 'Memory', 'Performance'],
      modules: [soonModule([
        ['How a GPU works', '🖥️', 'Cores, warps and why GPUs are fast.'],
        ['Your first CUDA kernel', '🚀', 'Threads, blocks and grids.'],
        ['GPU memory', '💾', 'Global, shared and constant memory.'],
        ['Parallel patterns', '🧵', 'Reduction, scan and matrix multiplication.'],
        ['Profiling and tuning', '⏱️', 'Find and fix slow kernels.']
      ])]
    },
    {
      id: 'cyber-security',
      title: 'Cyber Security',
      emoji: '🔐',
      color: '#475569',
      blurb: 'Networks, cryptography, attacks and defences, explained with safe hands on labs.',
      intro: 'Learn how systems are attacked and how they are defended. Each topic has an animation and a safe lab you can try in the browser.',
      tags: ['Networking', 'Cryptography', 'Attacks', 'Defence'],
      modules: [soonModule([
        ['Security fundamentals', '🔰', 'Confidentiality, integrity and availability.'],
        ['Networking for security', '🌐', 'TCP/IP, ports, firewalls and VPNs.'],
        ['Cryptography', '🔏', 'Hashing, encryption and digital signatures.'],
        ['Common attacks', '⚠️', 'Phishing, malware, injection and more.'],
        ['Defence and incident response', '🚨', 'Monitoring, logging and responding to attacks.']
      ])]
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

/* Interview Questions: the last chapter of a subject. The page and its questions are built by
   tools/interview-build/build.py from the question sets in tools/interview-build/sets/. */
function iqModule(sid) {
  const info = {
    'dsa': ['content/dsa/interview-questions.html', 'Coding round questions on complexity, arrays, two pointers, binary search, linked lists, stacks, trees, graphs and dynamic programming, each with the pattern, the steps, the complexity and Python code.', ['two sum', 'kadane', 'sliding window', 'reverse linked list', 'cycle detection', 'LRU cache', 'valid parentheses', 'BFS', 'DFS', 'topological sort', 'dijkstra', 'coin change', 'big o']],
    'java': ['content/java/interview-questions.html', 'Real Java interview questions on the JVM, OOP, strings, exceptions, collections, Java 8 streams, threads and framework design, with output questions run on the JDK.', ['JDK JRE JVM', 'string pool', 'equals and hashCode', 'HashMap internals', 'checked exception', 'final finally finalize', 'streams', 'functional interface', 'ThreadLocal', 'singleton', 'immutable class']],
    'testng': ['content/testng/interview-questions.html', 'TestNG questions from automation interviews: annotation order, testng.xml, groups, dependencies, data providers, soft asserts, listeners, retries, parallel runs and Maven.', ['annotation order', 'testng.xml', 'groups', 'dependsOnMethods', 'DataProvider', 'SoftAssert', 'ITestListener', 'IRetryAnalyzer', 'parallel', 'surefire']],
    'javascript': ['content/javascript/interview-questions.html', 'JavaScript and TypeScript questions from developer and automation interviews: types, closures, this, prototypes, the event loop, promises, TypeScript generics and narrowing, unit and API tests, Playwright and framework design, with output questions run on Node.js.', ['var let const', 'hoisting', 'closure', 'this', 'event loop', 'microtask', 'Promise.all', 'debounce', 'deep clone', 'interface vs type', 'any vs unknown', 'generics', 'utility types', 'mocks and spies', 'auto waiting', 'flaky tests', 'fixtures']],
    'manual-testing': ['content/manual-testing/interview-questions.html', 'Manual and QA interview questions on testing principles, SDLC and STLC, levels and types, test design techniques, the bug life cycle, test planning and real project scenarios.', ['verification vs validation', 'smoke vs sanity', 'retesting vs regression', 'severity vs priority', 'bug life cycle', 'boundary value analysis', 'test plan', 'RTM', 'how to test a login page', 'test a pen']],
    'ml-maths': ['content/ml-maths/interview-questions.html', 'Maths questions from machine learning interviews and certification theory sections: dot products, matrix shapes, eigenvalues and PCA, derivatives, backpropagation, gradient descent and Adam, Bayes, distributions, confidence intervals, A/B tests, entropy, losses and metrics, each solved step by step.', ['dot product', 'cosine similarity', 'matrix multiplication', 'eigenvalues', 'PCA', 'chain rule', 'sigmoid derivative', 'gradient descent', 'Adam', 'Bayes theorem', 'central limit theorem', 'p-value', 'A/B test', 'cross entropy', 'precision recall', 'ROC AUC']],
    'master-claude': ['content/claude/interview-questions.html', 'Claude interview questions on prompting, context engineering, CLAUDE.md and rules, skills, permissions and hooks, subagents, MCP, claude -p and GitHub Actions, the Claude API, agents, cost and safety, with real scenario questions.', ['prompt engineering', 'context rot', 'CLAUDE.md', 'rules.md', 'SKILL.md', 'hooks exit code 2', 'subagents', 'MCP', '.mcp.json', 'claude -p', 'tool use loop', 'prompt caching', 'agent safety']]
  }[sid];
  return {
    id: 'interview', title: 'Interview Questions', emoji: '🎤',
    blurb: 'Try each question yourself, open a hint if you are stuck, then compare with the full answer.',
    topics: [{
      id: 'interview-questions', title: 'Interview Questions', emoji: '🎤', page: info[0],
      summary: info[1],
      keywords: ['interview', 'interview questions', 'viva', 'FAQ', 'job preparation'].concat(info[2]),
      added: '2026-10-20'
    }]
  };
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
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' },
          { id: 'interview', title: 'Interview Questions', emoji: '💼', group: 'Interview Questions', keywords: ['interview questions', 'API testing interview', 'REST interview', 'Postman interview', 'SOAP versus REST'] }
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
        summary: 'Web services, SOAP and REST, HTTP, methods, status codes, headers, JSON, REST, SOAP, GraphQL and gRPC, Postman and curl, OpenAPI, JWT and OAuth 2.0 with PKCE, test design, validation, chaining, pagination, rate limits, caching, idempotency keys, Problem Details, the OWASP API Top 10, performance, async APIs, contract testing, mocking, CI, AI and MCP APIs, with a live mock API playground, seven hidden bugs and 68 interview questions.',
        keywords: ['API testing', 'manual API testing', 'REST', 'HTTP', 'status codes', 'Postman', 'curl', 'Bruno', 'OpenAPI', 'Swagger', 'JWT', 'OAuth', 'PKCE', 'idempotency', 'ETag', '304', '429', 'rate limit', 'pagination', 'BOLA', 'OWASP API Top 10', 'mass assignment', 'Problem Details', 'RFC 9457', 'GraphQL', 'gRPC', 'WebSocket', 'webhook', 'contract testing', 'Pact', 'WireMock', 'Newman', 'percentile', 'p95', 'MCP', 'LLM API', 'web service', 'SOAP', 'WSDL', 'Richardson Maturity Model', 'HATEOAS', 'interview questions'],
        added: '2026-10-20',
        sections: [
          { id: 'what-is-api', title: "What an API is and why we test it", emoji: '🔌', group: 'Level 1 · Foundations' },
          { id: 'web-services', title: "What a web service is", emoji: '🌐', group: 'Level 1 · Foundations', keywords: ['web service', 'API versus web service', 'SOAP', 'REST', 'WSDL', 'XSD', 'SoapUI', 'SOAP fault', 'SOAPAction'] },
          { id: 'rest', title: "REST in depth", emoji: '🏛️', group: 'Level 1 · Foundations', keywords: ['REST', 'RESTful', 'Roy Fielding', 'REST constraints', 'stateless', 'resource', 'representation', 'URI', 'URL', 'URN', 'Richardson Maturity Model', 'HATEOAS'] },
          { id: 'api-types', title: "Kinds of APIs and where they sit in a system", emoji: '🗂️', group: 'Level 1 · Foundations', keywords: ['public API', 'partner API', 'internal API', 'composite API', 'microservices', 'monolith', 'API gateway', 'load balancer', 'endpoint', 'payload'] },
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
          { id: 'p-get-product', title: "Test cases for GET /v1/products/{id}", emoji: '🏋️', group: 'Easy practice' },
          { id: 'p-read-response', title: "Spot the problems in a response", emoji: '🏋️', group: 'Easy practice' },
          { id: 'p-boundaries', title: "Boundary tests for a coupon API", emoji: '🏋️', group: 'Medium practice' },
          { id: 'p-chain', title: "Build a chained flow in Postman", emoji: '🏋️', group: 'Medium practice' },
          { id: 'p-hunt', title: "Hunt the authorization bugs in the playground", emoji: '🏋️', group: 'Hard practice' },
          { id: 'p-pagination', title: "Plan the tests for a product list", emoji: '🏋️', group: 'Hard practice' },
          { id: 'p-contract', title: "Review a change for consumers", emoji: '🏋️', group: 'Expert practice' },
          { id: 'p-llm', title: "Test a support chatbot API", emoji: '🏋️', group: 'Expert practice' },
          { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
          { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' },
          { id: 'interview', title: 'Interview Questions', emoji: '💼', group: 'Interview Questions', keywords: ['interview questions', 'API testing interview', 'REST interview', 'Postman interview', 'SOAP versus REST'] }
        ]
      }
      ]
    };
}

/* ===== js-build: JavaScript chapters. Generated by tools/js-build/build.py, edit the topic files instead. ===== */
function jsModules() {
  return [
    { id: "js-foundations", title: "Foundations", emoji: "🌱", blurb: "From your first program to functions and closures. Developers and testers both start here.", topics: [
      { id: "js-getting-started", title: "Getting Started with JavaScript", emoji: "🚀", page: "content/javascript/js-getting-started.html",
        summary: "What JavaScript is and where it runs, ECMAScript and TC39, engines and runtimes, installing Node.js and VS Code, your first program, the console toolbox, script loading with defer and async, strict mode and how to read errors and stack traces.",
        keywords: ["JavaScript", "introduction", "ECMAScript", "Node.js", "console", "DevTools", "strict mode", "error messages", "stack trace", "script tag", "first program"],
        added: "2026-10-20",
        sections: [
        { id: "what-is-js", title: "What JavaScript is and where it runs", emoji: "🌍", group: "QA essential", keywords: ["ECMAScript", "TC39", "V8", "SpiderMonkey", "JavaScriptCore", "Node.js", "Deno", "Bun", "runtime", "engine", "ES6", "ES2015"] },
        { id: "setup", title: "Setting up Node.js and an editor", emoji: "🧰", group: "QA essential", keywords: ["install Node.js", "LTS", "nvm", "VS Code", "REPL", "node -v", "npm -v", ".nvmrc", "engines"] },
        { id: "first-program", title: "Your first program", emoji: "👋", group: "Lesson", keywords: ["console.log", "hello world", "statement", "comment", "semicolon", "ASI", "automatic semicolon insertion", "template literal"] },
        { id: "console", title: "The console toolbox", emoji: "🖨️", group: "QA essential", keywords: ["console.table", "console.group", "console.count", "console.assert", "console.time", "console.warn", "console.error", "debugging", "format specifiers"] },
        { id: "browser", title: "JavaScript in a web page", emoji: "🌐", group: "QA essential", keywords: ["script tag", "defer", "async", "type module", "DOM", "querySelector", "DevTools", "console", "executeScript", "page.evaluate", "cy.window"] },
        { id: "how-it-runs", title: "How the engine runs your code", emoji: "⚙️", group: "Lesson", keywords: ["engine", "parse", "JIT", "bytecode", "single thread", "strict mode", "use strict", "sloppy mode", "SyntaxError"] },
        { id: "errors", title: "Reading error messages", emoji: "🚨", group: "QA essential", keywords: ["TypeError", "ReferenceError", "SyntaxError", "RangeError", "stack trace", "error message", "Cannot read properties of undefined", "try catch"] },
        { id: "scenario", title: "Real world scenario: summarise a test run", emoji: "🎬", group: "QA essential", keywords: ["test report", "summary", "node --test", "node:test", "assert", "deepEqual", "npm test"] },
        { id: "greet", title: "Say hello", emoji: "🏋️", group: "Easy practice" },
        { id: "seconds", title: "Milliseconds to seconds", emoji: "🏋️", group: "Medium practice" },
        { id: "summary", title: "Count the results", emoji: "🏋️", group: "Hard practice" },
        { id: "stack-line", title: "Find the line in a stack trace", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-values-types", title: "Variables, Types and Operators", emoji: "🔢", page: "content/javascript/js-values-types.html",
        summary: "let, const and var, the seven primitive types and objects, copy by value against shared objects, floating point numbers, NaN and BigInt, conversion and coercion, truthy and falsy values, ==, === and Object.is with Jest matchers, and every operator including optional chaining and nullish coalescing.",
        keywords: ["variables", "let", "const", "var", "data types", "typeof", "number", "BigInt", "NaN", "coercion", "truthy", "falsy", "equality", "===", "operators", "optional chaining", "nullish coalescing"],
        added: "2026-10-20",
        sections: [
        { id: "variables", title: "Variables with let and const", emoji: "📦", group: "QA essential", keywords: ["let", "const", "var", "variable", "reassign", "Object.freeze", "camelCase", "block scope"] },
        { id: "types", title: "The types of value", emoji: "🧬", group: "QA essential", keywords: ["primitive", "string", "number", "bigint", "boolean", "undefined", "null", "symbol", "object", "typeof", "reference", "copy by value", "shared object"] },
        { id: "numbers", title: "Numbers, NaN and BigInt", emoji: "🔢", group: "QA essential", keywords: ["floating point", "0.1 + 0.2", "NaN", "Infinity", "Number.EPSILON", "MAX_SAFE_INTEGER", "BigInt", "toFixed", "Intl.NumberFormat", "money", "toBeCloseTo"] },
        { id: "coercion", title: "Type conversion and coercion", emoji: "🔄", group: "QA essential", keywords: ["coercion", "type conversion", "Number()", "String()", "Boolean()", "parseInt", "parseFloat", "truthy", "falsy", "string concatenation", "environment variable"] },
        { id: "equality", title: "Equality: ==, === and Object.is", emoji: "⚖️", group: "QA essential", keywords: ["==", "===", "strict equality", "loose equality", "Object.is", "NaN", "toBe", "toEqual", "toStrictEqual", "deep equal", "reference equality"] },
        { id: "operators", title: "Operators", emoji: "➕", group: "QA essential", keywords: ["operators", "modulo", "exponent", "ternary", "logical AND", "logical OR", "nullish coalescing", "??", "optional chaining", "?.", "||=", "??=", "&&="] },
        { id: "scenario", title: "Real world scenario: clean up data from an API", emoji: "🎬", group: "QA essential", keywords: ["normalise data", "API response", "parse price", "test data", "console.table", "map", "filter"] },
        { id: "price", title: "Read a price", emoji: "🏋️", group: "Easy practice" },
        { id: "city", title: "Read a value that may be missing", emoji: "🏋️", group: "Medium practice" },
        { id: "close", title: "Compare decimals", emoji: "🏋️", group: "Hard practice" },
        { id: "same", title: "Write your own Object.is", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-control-flow", title: "Control Flow, Loops and Errors", emoji: "🔀", page: "content/javascript/js-control-flow.html",
        summary: "Decisions with if, else and switch, guard clauses, every loop with break, continue and labels, why forEach does not wait for await, throwing and catching errors with finally, custom errors and error causes, polling loops with timeouts, retries with backoff and data driven test tables.",
        keywords: ["if else", "switch", "loops", "for of", "for in", "while", "break", "continue", "try catch", "finally", "throw", "custom error", "error cause", "polling", "retry", "forEach await", "data driven"],
        added: "2026-10-20",
        sections: [
        { id: "if-else", title: "Making decisions with if and else", emoji: "🔀", group: "QA essential", keywords: ["if", "else", "else if", "condition", "guard clause", "early return", "branch coverage", "boundary value"] },
        { id: "switch", title: "switch and lookup tables", emoji: "🎛️", group: "Lesson", keywords: ["switch", "case", "default", "break", "fall through", "lookup table", "object map"] },
        { id: "loops", title: "Loops", emoji: "🔁", group: "Lesson", keywords: ["for loop", "while", "do while", "for...of", "for...in", "break", "continue", "label", "Object.entries", "infinite loop"] },
        { id: "async-loops", title: "Loops with async steps", emoji: "⏱️", group: "QA essential", keywords: ["forEach await", "async loop", "for of await", "Promise.all", "sequential", "parallel", "flaky test"] },
        { id: "errors", title: "Throwing and catching errors", emoji: "🧯", group: "QA essential", keywords: ["throw", "try", "catch", "finally", "Error", "TypeError", "RangeError", "custom error", "instanceof", "error cause", "rethrow", "cleanup"] },
        { id: "polling", title: "Polling and retry loops", emoji: "⏳", group: "QA essential", keywords: ["polling", "wait for", "waitUntil", "timeout", "interval", "retry", "exponential backoff", "expect.poll", "auto waiting", "flaky"] },
        { id: "scenario", title: "Real world scenario: data driven password checks", emoji: "🎬", group: "QA essential", keywords: ["data driven testing", "test table", "test.each", "boundary values", "password validation", "test cases"] },
        { id: "grade", title: "Grade a score", emoji: "🏋️", group: "Easy practice" },
        { id: "first-fail", title: "Stop at the first failure", emoji: "🏋️", group: "Medium practice" },
        { id: "retry-sync", title: "Retry a flaky function", emoji: "🏋️", group: "Hard practice" },
        { id: "wait-until", title: "Write waitUntil", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-functions", title: "Functions, Scope and Closures", emoji: "🧩", page: "content/javascript/js-functions.html",
        summary: "Function declarations and expressions, arrow functions, default and rest parameters, options objects, lexical scope, hoisting and the temporal dead zone, closures and private state, the loop closure bug, this with call, apply and bind and why Mocha needs function, higher order functions, memoize, debounce, recursion and a closure based test data factory.",
        keywords: ["function", "arrow function", "parameters", "scope", "hoisting", "closure", "this", "bind", "call", "apply", "higher order function", "callback", "memoize", "debounce", "recursion", "test data factory"],
        added: "2026-10-20",
        sections: [
        { id: "functions", title: "Declaring functions", emoji: "🧩", group: "Lesson", keywords: ["function", "parameter", "argument", "return", "default parameter", "rest parameter", "spread", "options object", "destructuring parameters"] },
        { id: "arrows", title: "Function expressions and arrow functions", emoji: "🏹", group: "QA essential", keywords: ["function expression", "arrow function", "implicit return", "anonymous function", "callback"] },
        { id: "scope", title: "Scope, hoisting and the temporal dead zone", emoji: "🔭", group: "Lesson", keywords: ["scope", "lexical scope", "block scope", "function scope", "global scope", "shadowing", "hoisting", "temporal dead zone", "TDZ", "scope chain"] },
        { id: "closures", title: "Closures", emoji: "🎒", group: "QA essential", keywords: ["closure", "private state", "factory function", "counter", "loop closure", "var in loop", "encapsulation"] },
        { id: "this", title: "this, call, apply and bind", emoji: "👉", group: "QA essential", keywords: ["this", "call", "apply", "bind", "method", "arrow function this", "lost this", "Mocha this.timeout", "Cypress alias this"] },
        { id: "higher-order", title: "Higher order functions", emoji: "🧠", group: "QA essential", keywords: ["higher order function", "callback", "function returning function", "currying", "memoize", "debounce", "throttle", "validation rules"] },
        { id: "recursion", title: "Recursion and the call stack", emoji: "🪆", group: "Lesson", keywords: ["recursion", "base case", "call stack", "stack overflow", "Maximum call stack size exceeded", "factorial", "tree walk", "nested data"] },
        { id: "scenario", title: "Real world scenario: a test data factory", emoji: "🎬", group: "QA essential", keywords: ["test data factory", "builder pattern", "unique email", "overrides", "fixtures", "faker"] },
        { id: "discount", title: "A discount with a default", emoji: "🏋️", group: "Easy practice" },
        { id: "counter", title: "A counter with a closure", emoji: "🏋️", group: "Medium practice" },
        { id: "once", title: "Run only once", emoji: "🏋️", group: "Hard practice" },
        { id: "debounce", title: "Write debounce", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "js-data", title: "Working with data", emoji: "📦", blurb: "Objects, arrays, text, numbers, dates, JSON and collections: the data every app and every test handles.", topics: [
      { id: "js-objects-arrays", title: "Objects and Arrays", emoji: "📦", page: "content/javascript/js-objects-arrays.html",
        summary: "Object literals, keys, entries and freeze, destructuring with defaults and renames, spread and the shallow copy trap, structuredClone, array basics, sorting with compare functions and the ES2023 copying methods, map, filter, reduce, find, some, every and flatMap, Object.groupBy and Sets, and checking a sorted product listing with Vitest matchers.",
        keywords: ["object", "array", "destructuring", "spread", "structuredClone", "deep copy", "map", "filter", "reduce", "find", "some", "every", "sort", "toSorted", "groupBy", "Set", "toEqual", "arrayContaining"],
        added: "2026-10-20",
        sections: [
        { id: "objects", title: "Objects", emoji: "🗃️", group: "QA essential", keywords: ["object", "property", "key", "dot notation", "bracket notation", "computed key", "shorthand", "Object.keys", "Object.values", "Object.entries", "Object.fromEntries", "Object.hasOwn", "Object.freeze", "delete"] },
        { id: "destructuring", title: "Destructuring", emoji: "✂️", group: "QA essential", keywords: ["destructuring", "object destructuring", "array destructuring", "default values", "rename", "rest in destructuring", "swap", "fixtures", "test.each"] },
        { id: "spread", title: "Spread, copies and immutability", emoji: "🧬", group: "QA essential", keywords: ["spread", "shallow copy", "deep copy", "structuredClone", "immutability", "defaults and overrides", "object merge"] },
        { id: "arrays", title: "Arrays", emoji: "📚", group: "Lesson", keywords: ["array", "index", "length", "at", "push", "pop", "shift", "unshift", "splice", "slice", "includes", "indexOf", "join", "Array.from", "flat", "sort", "compare function", "toSorted", "toReversed", "with"] },
        { id: "array-methods", title: "Array methods: map, filter, reduce and friends", emoji: "⚙️", group: "QA essential", keywords: ["map", "filter", "reduce", "find", "findIndex", "findLast", "some", "every", "flatMap", "method chaining", "allTextContents", "array of elements"] },
        { id: "grouping", title: "Grouping, counting and unique values", emoji: "🧺", group: "QA essential", keywords: ["Object.groupBy", "Map.groupBy", "group by", "count", "reduce to object", "unique values", "Set", "remove duplicates"] },
        { id: "scenario", title: "Real world scenario: verify a sorted product listing", emoji: "🎬", group: "QA essential", keywords: ["sorted listing", "sort check", "duplicates", "toEqual", "toContainEqual", "arrayContaining", "objectContaining", "test.each", "Vitest"] },
        { id: "pluck", title: "Pluck one field", emoji: "🏋️", group: "Easy practice" },
        { id: "sorted", title: "Is it sorted", emoji: "🏋️", group: "Medium practice" },
        { id: "count-by", title: "Count by a key", emoji: "🏋️", group: "Hard practice" },
        { id: "deep-equal", title: "Deep equality", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-strings-dates-json", title: "Strings, Regex, Numbers, Dates and JSON", emoji: "🔤", page: "content/javascript/js-strings-dates-json.html",
        summary: "String methods and Unicode, normalising page text for comparisons, regular expressions with groups, lookahead and flags, regex in Playwright, Cypress and Jest, Math and rounding traps, Intl.NumberFormat for currencies, Date and time zone traps, Temporal, JSON with replacers and revivers, JSON fixture files and validating an order API response.",
        keywords: ["string", "regex", "regular expression", "Math", "Intl.NumberFormat", "currency", "Date", "time zone", "Temporal", "JSON", "JSON.parse", "JSON.stringify", "fixtures", "toMatch", "toMatchObject"],
        added: "2026-10-20",
        sections: [
        { id: "strings", title: "Working with strings", emoji: "🔤", group: "QA essential", keywords: ["string", "trim", "includes", "startsWith", "slice", "split", "replace", "replaceAll", "padStart", "toUpperCase", "unicode", "normalize", "localeCompare", "whitespace", "non breaking space"] },
        { id: "regex", title: "Regular expressions", emoji: "🧷", group: "QA essential", keywords: ["regular expression", "regex", "RegExp", "test", "match", "matchAll", "replace", "capture group", "named group", "lookahead", "flags", "toMatch", "toHaveText regex", "stringMatching", "RegExp.escape"] },
        { id: "math", title: "Math and number formatting", emoji: "🧮", group: "QA essential", keywords: ["Math", "Math.round", "Math.floor", "Math.ceil", "Math.random", "random integer", "toFixed", "Intl.NumberFormat", "currency format", "percent", "compact notation"] },
        { id: "dates", title: "Dates, time zones and Temporal", emoji: "📅", group: "QA essential", keywords: ["Date", "Date.UTC", "toISOString", "getTime", "timestamp", "time zone", "UTC", "Intl.DateTimeFormat", "Temporal", "PlainDate", "ZonedDateTime", "Duration", "fake timers", "page.clock", "cy.clock"] },
        { id: "json", title: "JSON", emoji: "📄", group: "QA essential", keywords: ["JSON", "JSON.stringify", "JSON.parse", "replacer", "reviver", "pretty print", "fixtures", "cy.fixture", "import JSON", "import attributes"] },
        { id: "scenario", title: "Real world scenario: validate an order API response", emoji: "🎬", group: "QA essential", keywords: ["API response validation", "toMatchObject", "expect.stringMatching", "expect.any", "JSON body", "ISO date check", "currency check"] },
        { id: "slugify", title: "Make a URL slug", emoji: "🏋️", group: "Easy practice" },
        { id: "mask", title: "Mask an email", emoji: "🏋️", group: "Medium practice" },
        { id: "order-ids", title: "Extract order numbers", emoji: "🏋️", group: "Hard practice" },
        { id: "business-days", title: "Add business days", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-collections-iterators", title: "Map, Set, Iterators and Generators", emoji: "🗂️", page: "content/javascript/js-collections-iterators.html",
        summary: "Map and when it beats an object, getOrInsert, Set with union, intersection and difference, WeakMap and WeakRef, the iteration protocol, lazy iterator helpers, generators that pause and resume, async generators and for await for paginated APIs, symbols and well known symbols, and comparing an expected menu with the real one.",
        keywords: ["Map", "Set", "union", "intersection", "difference", "WeakMap", "WeakRef", "iterator", "iterable", "iterator helpers", "generator", "yield", "async generator", "for await", "pagination", "Symbol"],
        added: "2026-10-20",
        sections: [
        { id: "map", title: "Map", emoji: "🗺️", group: "QA essential", keywords: ["Map", "set", "get", "has", "delete", "size", "insertion order", "object keys", "counter", "getOrInsert", "cache"] },
        { id: "set", title: "Set and set operations", emoji: "🧺", group: "QA essential", keywords: ["Set", "unique", "add", "has", "union", "intersection", "difference", "symmetricDifference", "isSubsetOf", "compare lists", "missing items"] },
        { id: "weak", title: "WeakMap, WeakSet and WeakRef", emoji: "🪶", group: "Lesson", keywords: ["WeakMap", "WeakSet", "WeakRef", "FinalizationRegistry", "garbage collection", "memory leak"] },
        { id: "iterators", title: "Iterators and iterator helpers", emoji: "🔁", group: "Lesson", keywords: ["iterable", "iterator", "Symbol.iterator", "next", "done", "iteration protocol", "iterator helpers", "take", "drop", "toArray", "Iterator.from", "lazy evaluation"] },
        { id: "generators", title: "Generators and async generators", emoji: "⏯️", group: "QA essential", keywords: ["generator", "function*", "yield", "yield*", "next", "lazy", "async generator", "for await", "pagination", "Array.fromAsync"] },
        { id: "symbols", title: "Symbols", emoji: "🔣", group: "Lesson", keywords: ["Symbol", "Symbol.for", "unique key", "well known symbols", "Symbol.iterator", "Symbol.toPrimitive", "Symbol.asyncIterator"] },
        { id: "scenario", title: "Real world scenario: compare a menu and walk every page", emoji: "🎬", group: "QA essential", keywords: ["compare menu", "expected vs actual", "set difference", "duplicates", "pagination", "async generator", "for await"] },
        { id: "unique", title: "Unique, in order", emoji: "🏋️", group: "Easy practice" },
        { id: "diff", title: "Expected against actual", emoji: "🏋️", group: "Medium practice" },
        { id: "range", title: "A range generator", emoji: "🏋️", group: "Hard practice" },
        { id: "lru", title: "A small LRU cache", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "js-structure", title: "Structure and tooling", emoji: "🏗️", blurb: "Classes, modules, packages, TypeScript and the tools that keep a growing codebase and test suite in order.", topics: [
      { id: "js-oop", title: "Prototypes, Classes and the Page Object Model", emoji: "🏛️", page: "content/javascript/js-oop.html",
        summary: "The prototype chain, constructor functions and new, classes with fields, getters and static methods, lost this and other class traps, private fields and static blocks, inheritance with extends and super, custom error classes with cause, mixins and dependency injection, the Page Object Model in plain DOM, Playwright and Selenium, a test data builder and an API client class.",
        keywords: ["prototype", "class", "constructor", "getter", "static", "private field", "extends", "super", "custom error", "mixin", "composition", "dependency injection", "Page Object Model", "POM", "builder pattern"],
        added: "2026-10-20",
        sections: [
        { id: "prototypes", title: "Objects and prototypes", emoji: "🧬", group: "Lesson", keywords: ["prototype", "prototype chain", "__proto__", "Object.create", "Object.getPrototypeOf", "hasOwn", "constructor function", "new", "Object.prototype"] },
        { id: "classes", title: "Classes", emoji: "🏛️", group: "QA essential", keywords: ["class", "constructor", "method", "field", "getter", "setter", "get", "static", "this", "chaining", "strict mode", "hoisting"] },
        { id: "private", title: "Private fields and encapsulation", emoji: "🔒", group: "Lesson", keywords: ["private", "#", "private field", "private method", "encapsulation", "static block", "ergonomic brand check", "in", "ES2022"] },
        { id: "inheritance", title: "Inheritance with extends and super", emoji: "🌳", group: "QA essential", keywords: ["extends", "super", "inheritance", "override", "instanceof", "subclass", "custom error", "Error cause", "HttpError", "BasePage"] },
        { id: "composition", title: "Composition over inheritance", emoji: "🧩", group: "Lesson", keywords: ["composition", "mixin", "dependency injection", "has a", "is a", "component", "logger", "retry"] },
        { id: "pom", title: "The Page Object Model", emoji: "📄", group: "QA essential", keywords: ["Page Object Model", "POM", "page object", "locator", "loginAs", "BasePage", "component", "Playwright", "Selenium", "maintainable tests"] },
        { id: "scenario", title: "Real world scenario: test data and an API client", emoji: "🎬", group: "QA essential", keywords: ["builder pattern", "test data builder", "API client", "base class", "dependency injection", "fake transport", "fluent interface"] },
        { id: "rect", title: "A rectangle class", emoji: "🏋️", group: "Easy practice" },
        { id: "stack", title: "A stack with private storage", emoji: "🏋️", group: "Medium practice" },
        { id: "errors", title: "A custom error class", emoji: "🏋️", group: "Hard practice" },
        { id: "page-object", title: "A page object for a search box", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-modules-tooling", title: "Modules, npm, TypeScript and Tooling", emoji: "📦", page: "content/javascript/js-modules-tooling.html",
        summary: "Named and default exports, dynamic import, JSON modules, CommonJS and how it mixes with ES modules, package.json scripts and dependencies, semantic version ranges, npm ci and the lock file, TypeScript types and the type checker, ESLint and Prettier on real code, environment variables with --env-file, and a test project with separate unit and API scripts.",
        keywords: ["import", "export", "ES modules", "CommonJS", "require", "npm", "package.json", "semver", "package-lock.json", "npm ci", "TypeScript", "tsc", "ESLint", "Prettier", "process.env", ".env", "project structure"],
        added: "2026-10-20",
        sections: [
        { id: "esm", title: "ES modules: import and export", emoji: "📦", group: "QA essential", keywords: ["module", "ES modules", "ESM", "import", "export", "default export", "named export", "dynamic import", "top level await", "import attributes", "JSON modules", "import.meta"] },
        { id: "cjs", title: "CommonJS and how the two mix", emoji: "🧱", group: "QA essential", keywords: ["CommonJS", "require", "module.exports", ".cjs", ".mjs", "type module", "Cannot use import statement outside a module", "__dirname", "require esm"] },
        { id: "npm", title: "npm and package.json", emoji: "📥", group: "QA essential", keywords: ["npm", "package.json", "package-lock.json", "node_modules", "dependencies", "devDependencies", "scripts", "npm ci", "npx", "semver", "caret", "tilde", "npm audit"] },
        { id: "typescript", title: "TypeScript", emoji: "🔷", group: "QA essential", keywords: ["TypeScript", "types", "interface", "type alias", "union", "generics", "tsc", "tsconfig", "type stripping", "strict", "erasableSyntaxOnly", "optional property"] },
        { id: "lint", title: "ESLint and Prettier", emoji: "🧹", group: "QA essential", keywords: ["ESLint", "lint", "eslint.config.js", "flat config", "rules", "Prettier", "format", "no-unused-vars", "eqeqeq", "no-floating-promises", "eslint-plugin-playwright"] },
        { id: "env", title: "Environment variables and config", emoji: "🔐", group: "QA essential", keywords: ["environment variables", "process.env", ".env", "--env-file", "dotenv", "secrets", "config", "baseURL", "staging"] },
        { id: "scenario", title: "Real world scenario: lay out a test project", emoji: "🎬", group: "QA essential", keywords: ["project structure", "folder layout", "npm scripts", "test:unit", "test:api", "test:e2e", "node --test", "CI jobs"] },
        { id: "env-parse", title: "Parse an env file", emoji: "🏋️", group: "Easy practice" },
        { id: "config", title: "Typed config from strings", emoji: "🏋️", group: "Medium practice" },
        { id: "caret", title: "Does ^ allow it?", emoji: "🏋️", group: "Hard practice" },
        { id: "resolve", title: "Resolve an import path", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "js-platform", title: "Async and the platform", emoji: "⏳", blurb: "Promises and the event loop, the browser DOM, and HTTP from both sides: everything a UI or API test waits for.", topics: [
      { id: "js-async", title: "Asynchronous JavaScript: Promises, async and await", emoji: "⏳", page: "content/javascript/js-async.html",
        summary: "The single thread and the event loop with microtasks and tasks, error first callbacks, promises and chaining, Promise.withResolvers, async and await, sequential against parallel awaits, the missing await that makes a test pass by mistake, all, allSettled, race and any, AbortController and AbortSignal.timeout, polling and retry with exponential backoff, waiting in Playwright, and a link checker with a concurrency limit.",
        keywords: ["event loop", "microtask", "callback", "Promise", "then", "catch", "async", "await", "Promise.all", "Promise.allSettled", "Promise.race", "Promise.any", "AbortController", "timeout", "retry", "backoff", "polling", "flaky tests"],
        added: "2026-10-20",
        sections: [
        { id: "event-loop", title: "One thread and the event loop", emoji: "🔄", group: "Lesson", keywords: ["event loop", "single thread", "call stack", "microtask", "macrotask", "task queue", "setTimeout", "queueMicrotask", "blocking", "non-blocking"] },
        { id: "callbacks", title: "Callbacks", emoji: "📞", group: "Lesson", keywords: ["callback", "error-first callback", "callback hell", "promisify", "fs/promises"] },
        { id: "promises", title: "Promises", emoji: "🤝", group: "QA essential", keywords: ["Promise", "pending", "fulfilled", "rejected", "then", "catch", "finally", "chaining", "unhandled rejection", "Promise.withResolvers", "resolve", "reject"] },
        { id: "async-await", title: "async and await", emoji: "⏸️", group: "QA essential", keywords: ["async", "await", "try catch", "Promise.all", "sequential", "parallel", "forgot await", "floating promise", "false positive", "flaky test", "top level await"] },
        { id: "combinators", title: "Running many promises: all, allSettled, race, any", emoji: "🧮", group: "QA essential", keywords: ["Promise.all", "Promise.allSettled", "Promise.race", "Promise.any", "AggregateError", "AbortController", "AbortSignal", "AbortSignal.timeout", "AbortSignal.any", "cancel", "timeout"] },
        { id: "waiting", title: "Retries, polling and waiting the right way", emoji: "⏱️", group: "QA essential", keywords: ["wait", "polling", "waitFor", "sleep", "fixed sleep", "retry", "exponential backoff", "auto-waiting", "expect.poll", "waitForResponse", "flaky"] },
        { id: "scenario", title: "Real world scenario: a link checker", emoji: "🎬", group: "QA essential", keywords: ["link checker", "concurrency limit", "mapLimit", "timeout", "smoke test", "AbortSignal.timeout", "report"] },
        { id: "sleep", title: "A sleep helper", emoji: "🏋️", group: "Easy practice" },
        { id: "timeout", title: "Give up after a timeout", emoji: "🏋️", group: "Medium practice" },
        { id: "retry", title: "Retry a flaky call", emoji: "🏋️", group: "Hard practice" },
        { id: "limit", title: "Run with a concurrency limit", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-dom-browser", title: "The DOM and the Browser", emoji: "🌐", page: "content/javascript/js-dom-browser.html",
        summary: "The DOM tree and how to move around it, CSS selectors including :has and attribute selectors, XPath by text and ancestor, which locators stay stable, textContent against innerHTML and XSS, events with capture and bubble, delegation and trusted events, form values and validation, shadow DOM and iframes in each test tool, waiting with MutationObserver, localStorage, sessionStorage and cookies, and checking every row of an order table.",
        keywords: ["DOM", "querySelector", "CSS selector", "XPath", "locator", "getByRole", "data-test", "textContent", "innerHTML", "XSS", "event", "bubbling", "delegation", "form validation", "shadow DOM", "iframe", "MutationObserver", "localStorage", "cookie"],
        added: "2026-10-20",
        sections: [
        { id: "dom", title: "The DOM tree", emoji: "🌳", group: "QA essential", keywords: ["DOM", "document", "element", "node", "tree", "getElementById", "querySelector", "querySelectorAll", "closest", "NodeList", "parentElement"] },
        { id: "selectors", title: "Selectors and locators", emoji: "🎯", group: "QA essential", keywords: ["CSS selector", "locator", "XPath", "attribute selector", ":has", ":not", "nth-of-type", "data-test", "data-testid", "getByRole", "getByText", "stable locators", "ancestor"] },
        { id: "change", title: "Changing the page", emoji: "✏️", group: "Lesson", keywords: ["textContent", "innerText", "innerHTML", "classList", "setAttribute", "dataset", "createElement", "append", "remove", "XSS", "cross site scripting"] },
        { id: "events", title: "Events", emoji: "🖱️", group: "QA essential", keywords: ["event", "addEventListener", "click", "capture", "bubble", "event delegation", "target", "currentTarget", "preventDefault", "stopPropagation", "CustomEvent", "dispatchEvent", "isTrusted", "force click"] },
        { id: "forms", title: "Forms and validation", emoji: "📝", group: "QA essential", keywords: ["form", "input", "value", "checked", "select", "validation", "checkValidity", "validity", "required", "FormData", "submit", "requestSubmit", "boundary values"] },
        { id: "advanced", title: "Shadow DOM, iframes and observers", emoji: "🧱", group: "QA essential", keywords: ["shadow DOM", "shadowRoot", "web components", "custom elements", "iframe", "contentDocument", "frameLocator", "switchTo frame", "MutationObserver", "wait for element"] },
        { id: "storage", title: "Storage and cookies", emoji: "🍪", group: "QA essential", keywords: ["localStorage", "sessionStorage", "cookie", "document.cookie", "HttpOnly", "SameSite", "storageState", "session", "login state"] },
        { id: "scenario", title: "Real world scenario: check an order table", emoji: "🎬", group: "QA essential", keywords: ["table", "rows", "cells", "scrape", "data validation", "totals", "price parsing", "UI data check"] },
        { id: "selector", title: "Build a CSS selector", emoji: "🏋️", group: "Easy practice" },
        { id: "cookies", title: "Parse document.cookie", emoji: "🏋️", group: "Medium practice" },
        { id: "path", title: "The path of an event", emoji: "🏋️", group: "Hard practice" },
        { id: "sorted", title: "Is the price list sorted?", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-http-node", title: "HTTP, fetch and Node.js Servers", emoji: "📡", page: "content/javascript/js-http-node.html",
        summary: "A raw HTTP exchange, methods and status codes, fetch with GET and POST and why it does not reject on 404, building URLs with the URL class, token login and access checks, an Express REST API with proper status codes, reading CSV test data and writing reports, running other programs, and a mock API with reset, fault injection and delays.",
        keywords: ["HTTP", "status code", "fetch", "URL", "URLSearchParams", "Bearer token", "401", "403", "Express", "REST", "middleware", "fs", "path", "child_process", "mock server", "fault injection"],
        added: "2026-10-20",
        sections: [
        { id: "http", title: "How HTTP works", emoji: "📨", group: "QA essential", keywords: ["HTTP", "request", "response", "method", "GET", "POST", "PUT", "PATCH", "DELETE", "status code", "headers", "body", "idempotent", "200", "201", "404", "500"] },
        { id: "fetch", title: "fetch and URLs", emoji: "📡", group: "QA essential", keywords: ["fetch", "Response", "res.ok", "res.status", "res.json", "headers", "POST body", "Content-Type", "URL", "URLSearchParams", "encodeURIComponent", "query string"] },
        { id: "auth", title: "Authentication: 401 against 403", emoji: "🔑", group: "QA essential", keywords: ["authentication", "authorization", "token", "Bearer", "Authorization header", "401", "403", "JWT", "session", "roles", "access control"] },
        { id: "server", title: "Writing a server with Express", emoji: "🖥️", group: "QA essential", keywords: ["Express", "server", "route", "middleware", "req.params", "req.query", "req.body", "res.status", "res.json", "REST", "CRUD", "201", "204", "400"] },
        { id: "node", title: "Node.js core modules", emoji: "🧰", group: "QA essential", keywords: ["fs", "fs/promises", "readFile", "writeFile", "mkdir", "path", "path.join", "os", "process.argv", "child_process", "execFile", "CSV", "test data"] },
        { id: "scenario", title: "Real world scenario: a mock API for UI tests", emoji: "🎬", group: "QA essential", keywords: ["mock API", "mock server", "test double", "fault injection", "reset state", "health check", "page.route", "cy.intercept", "Express"] },
        { id: "status", title: "Group a status code", emoji: "🏋️", group: "Easy practice" },
        { id: "build-url", title: "Build a request URL", emoji: "🏋️", group: "Medium practice" },
        { id: "link", title: "Read a Link header", emoji: "🏋️", group: "Hard practice" },
        { id: "route", title: "Match a route with parameters", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "js-depth", title: "JavaScript in depth", emoji: "🔬", blurb: "How the engine really works, errors and debugging, regular expressions, functional style, metaprogramming and Node.js in depth.", topics: [
      { id: "js-engine", title: "How JavaScript really works", emoji: "🔬", page: "content/javascript/js-engine.html",
        summary: "The call stack and stack traces, the creation phase with hoisting, the temporal dead zone and lexical scope, the five rules of this and how methods lose it, the Node.js event loop phases with nextTick and microtasks, V8 compilers, hidden classes and inline caches, generational garbage collection, and a page object that crashes inside a retry helper.",
        keywords: ["execution context", "call stack", "hoisting", "TDZ", "scope chain", "this", "bind", "event loop phases", "process.nextTick", "setImmediate", "V8", "hidden class", "inline cache", "garbage collection", "JavaScript internals", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "stack", title: "Execution contexts and the call stack", emoji: "📚", group: "QA essential", keywords: ["execution context", "call stack", "stack frame", "stack trace", "stack overflow", "RangeError", "Maximum call stack size exceeded", "recursion"] },
        { id: "contexts", title: "Creation phase, hoisting and the scope chain", emoji: "🏗️", group: "Lesson", keywords: ["creation phase", "hoisting", "temporal dead zone", "TDZ", "lexical scope", "scope chain", "lexical environment", "var in loops", "closure", "let per iteration"] },
        { id: "this", title: "this in depth: five rules and a precedence", emoji: "👉", group: "QA essential", keywords: ["this", "default binding", "implicit binding", "explicit binding", "call", "apply", "bind", "new", "arrow function this", "class field arrow", "lost this", "strict mode"] },
        { id: "loop", title: "The Node.js event loop, phase by phase", emoji: "🔄", group: "QA essential", keywords: ["event loop phases", "timers phase", "poll phase", "check phase", "setImmediate", "process.nextTick", "microtask", "queueMicrotask", "libuv", "await microtask"] },
        { id: "v8", title: "Inside V8: JIT, hidden classes and inline caches", emoji: "⚙️", group: "Lesson", keywords: ["V8", "Ignition", "TurboFan", "Maglev", "Sparkplug", "JIT", "bytecode", "hidden class", "shape", "map", "inline cache", "monomorphic", "megamorphic", "deoptimisation", "delete"] },
        { id: "gc", title: "Garbage collection", emoji: "🧹", group: "QA essential", keywords: ["garbage collection", "generational GC", "young generation", "old generation", "scavenge", "mark and sweep", "roots", "reachability", "heap snapshot", "v8.getHeapStatistics", "memory"] },
        { id: "scenario", title: "Real world scenario: a crash only in the retry helper", emoji: "🎬", group: "QA essential", keywords: ["debugging", "this undefined", "retry helper", "page object", "bind", "arrow wrapper", "unbound-method"] },
        { id: "order", title: "Predict the log order", emoji: "🏋️", group: "Easy practice" },
        { id: "bindme", title: "Write your own bind", emoji: "🏋️", group: "Medium practice" },
        { id: "fixthis", title: "Fix the lost this", emoji: "🏋️", group: "Hard practice" },
        { id: "miniloop", title: "A tiny event loop", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-errors-debugging", title: "Errors, debugging and logging", emoji: "🧯", page: "content/javascript/js-errors-debugging.html",
        summary: "Built in error types and custom error classes with codes and causes, errors in callbacks and promises, unhandled rejections and global handlers, errors as values, inspecting values and starting the debuggers, JSON logs with a request id through AsyncLocalStorage, source maps for TypeScript stack traces, and sorting test failures by error type.",
        keywords: ["errors", "custom error", "error cause", "AggregateError", "unhandled rejection", "uncaughtException", "debugging", "debugger", "trace viewer", "util.inspect", "structured logging", "AsyncLocalStorage", "source maps", "triage", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "types", title: "The error types and building your own", emoji: "🧯", group: "QA essential", keywords: ["Error", "TypeError", "ReferenceError", "RangeError", "SyntaxError", "URIError", "AggregateError", "custom error", "extends Error", "error code", "cause", "instanceof", "new.target"] },
        { id: "async", title: "Errors in async code", emoji: "⏳", group: "QA essential", keywords: ["async error", "try catch", "await", "rejected promise", "unhandledRejection", "uncaughtException", "finally", "exit code", "floating promise", "process.on"] },
        { id: "values", title: "Throw or return: errors as values", emoji: "📬", group: "Lesson", keywords: ["result object", "errors as values", "throw vs return", "validation", "expected failure", "empty catch"] },
        { id: "debugging", title: "Debugging tools", emoji: "🔎", group: "QA essential", keywords: ["debugging", "console.table", "console.dir", "util.inspect", "console.count", "console.assert", "--inspect", "--inspect-brk", "breakpoint", "conditional breakpoint", "logpoint", "debugger statement", "PWDEBUG", "trace viewer", "VS Code debugger"] },
        { id: "logging", title: "Structured logging", emoji: "🪵", group: "QA essential", keywords: ["structured logging", "JSON logs", "log levels", "pino", "request id", "correlation id", "AsyncLocalStorage", "context", "observability"] },
        { id: "sourcemaps", title: "Source maps", emoji: "🗺️", group: "Lesson", keywords: ["source map", "sourceMap", "--enable-source-maps", "minified code", "stack trace", "TypeScript", "Sentry"] },
        { id: "scenario", title: "Real world scenario: triage a red pipeline", emoji: "🎬", group: "QA essential", keywords: ["triage", "test failure analysis", "AssertionError", "TimeoutError", "ECONNREFUSED", "environment issue", "product bug", "test bug", "nightly run"] },
        { id: "httperror", title: "A custom error class", emoji: "🏋️", group: "Easy practice" },
        { id: "safejson", title: "Parse JSON without throwing", emoji: "🏋️", group: "Medium practice" },
        { id: "retryif", title: "Retry only the right errors", emoji: "🏋️", group: "Hard practice" },
        { id: "triage", title: "Triage a failure", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-regex", title: "Regular expressions in depth", emoji: "🧷", page: "content/javascript/js-regex.html",
        summary: "How the backtracking engine matches, greedy against lazy, lookarounds for password rules and backreferences, the m, s, g and y flags and the lastIndex trap, unicode letters and emoji, replacing with groups and functions to mask secrets, a sticky tokeniser, catastrophic backtracking, validation patterns with table driven tests, and parsing access logs.",
        keywords: ["regex", "regular expressions", "backtracking", "lazy quantifier", "lookahead", "lookbehind", "backreference", "lastIndex", "unicode regex", "replace function", "masking", "tokenizer", "ReDoS", "validation", "log parsing", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "engine", title: "How the regex engine matches", emoji: "⚙️", group: "Lesson", keywords: ["regex engine", "backtracking", "greedy", "lazy", "non greedy", ".*?", "negated character class", "match position"] },
        { id: "lookaround", title: "Lookarounds and backreferences", emoji: "👀", group: "QA essential", keywords: ["lookahead", "lookbehind", "negative lookahead", "negative lookbehind", "backreference", "password regex", "\\1", "\\k"] },
        { id: "flags", title: "Flags in depth and the lastIndex trap", emoji: "🚩", group: "QA essential", keywords: ["g flag", "m flag", "multiline", "s flag", "dotAll", "y flag", "sticky", "i flag", "lastIndex", "stateful regex"] },
        { id: "unicode", title: "Unicode and every language", emoji: "🌍", group: "QA essential", keywords: ["unicode", "u flag", "v flag", "\\p{L}", "Unicode property escapes", "Script", "emoji", "normalize", "NFD", "accents", "i18n testing"] },
        { id: "replace", title: "Replacing, masking and splitting", emoji: "✂️", group: "QA essential", keywords: ["replace", "replaceAll", "replace function", "$1", "$<name>", "masking", "PII", "split", "tokenizer", "sticky", "lexer"] },
        { id: "redos", title: "ReDoS and safe patterns", emoji: "💣", group: "QA essential", keywords: ["ReDoS", "catastrophic backtracking", "nested quantifier", "denial of service", "exponential", "eslint-plugin-regexp", "input length limit"] },
        { id: "validate", title: "Validation patterns and testing them", emoji: "✅", group: "QA essential", keywords: ["validation", "email regex", "date regex", "UUID regex", "PIN code", "semver regex", "assert.match", "table driven tests", "boundary cases"] },
        { id: "scenario", title: "Real world scenario: mine the access logs", emoji: "🎬", group: "QA essential", keywords: ["log parsing", "access log", "named groups", "load test", "5xx errors", "slow requests", "performance analysis"] },
        { id: "prices", title: "Extract rupee prices", emoji: "🏋️", group: "Easy practice" },
        { id: "policy", title: "A password policy", emoji: "🏋️", group: "Medium practice" },
        { id: "mask", title: "Mask card numbers", emoji: "🏋️", group: "Hard practice" },
        { id: "kv", title: "Parse key=value pairs", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-functional", title: "Functional programming in JavaScript", emoji: "🧩", page: "content/javascript/js-functional.html",
        summary: "Pure functions and injecting the clock, freeze, deep freeze and immutable updates, curry, partial application, pipe and compose, eager arrays against lazy iterator helpers, recursion over JSON, trampolines and deep equality, and a composable validator that reports the JSON path of each wrong field.",
        keywords: ["functional programming", "pure function", "side effects", "immutability", "Object.freeze", "currying", "partial application", "compose", "pipe", "lazy evaluation", "recursion", "trampoline", "validator", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "pure", title: "Pure functions and side effects", emoji: "💧", group: "QA essential", keywords: ["pure function", "side effect", "referential transparency", "dependency injection", "deterministic", "testability", "functional programming"] },
        { id: "immutable", title: "Immutability", emoji: "🧊", group: "QA essential", keywords: ["immutability", "Object.freeze", "deep freeze", "shallow", "structuredClone", "spread", "immutable update", "const", "shared state"] },
        { id: "compose", title: "Currying, partial application and composition", emoji: "🧩", group: "Lesson", keywords: ["currying", "curry", "partial application", "compose", "pipe", "point free", "function arity", "fn.length", "higher order function"] },
        { id: "lazy", title: "Eager and lazy collections", emoji: "🦥", group: "Lesson", keywords: ["lazy evaluation", "eager", "iterator helpers", "take", "reduce", "flatMap", "index by id", "data pipeline"] },
        { id: "recursion", title: "Recursion on real data", emoji: "🌳", group: "QA essential", keywords: ["recursion", "tree walk", "nested JSON", "trampoline", "stack overflow", "deep equality", "deepStrictEqual", "toEqual"] },
        { id: "scenario", title: "Real world scenario: a validator built from tiny functions", emoji: "🎬", group: "QA essential", keywords: ["validator", "schema validation", "combinator", "Zod", "Joi", "API response check", "JSON path", "composition"] },
        { id: "pipe", title: "Write pipe", emoji: "🏋️", group: "Easy practice" },
        { id: "deepfreeze", title: "Deep freeze", emoji: "🏋️", group: "Medium practice" },
        { id: "addqty", title: "An immutable cart update", emoji: "🏋️", group: "Hard practice" },
        { id: "findkey", title: "Find every value of a key", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-metaprogramming", title: "Objects in depth and metaprogramming", emoji: "🪞", page: "content/javascript/js-metaprogramming.html",
        summary: "Descriptor flags, getters, setters and the three levels of locking, well known symbols and hiding secrets from logs, Proxy and Reflect for strict config, negative indexes and usage tracking, a proxy that logs and retries page object steps, tagged templates for HTML and SQL, decorators, and a fluent API client.",
        keywords: ["property descriptor", "defineProperty", "getter", "setter", "Object.seal", "Symbol.toPrimitive", "util.inspect.custom", "Proxy", "Reflect", "trap", "tagged template", "String.raw", "decorators", "spy", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "descriptors", title: "Property descriptors, getters and setters", emoji: "🧾", group: "Lesson", keywords: ["property descriptor", "defineProperty", "writable", "enumerable", "configurable", "getter", "setter", "accessor", "Object.freeze", "Object.seal", "preventExtensions"] },
        { id: "symbols", title: "Well known symbols", emoji: "🔣", group: "QA essential", keywords: ["Symbol.toPrimitive", "Symbol.hasInstance", "Symbol.toStringTag", "Symbol.iterator", "util.inspect.custom", "toJSON", "well known symbols", "secrets in logs"] },
        { id: "proxy", title: "Proxy and Reflect", emoji: "🪞", group: "QA essential", keywords: ["Proxy", "Reflect", "trap", "get trap", "set trap", "has", "deleteProperty", "apply", "construct", "validation proxy", "negative index", "auto mock", "step logging"] },
        { id: "tagged", title: "Tagged template literals", emoji: "🏷️", group: "QA essential", keywords: ["tagged template", "template literal", "String.raw", "escape HTML", "SQL injection", "parameterised query", "dedent", "gql"] },
        { id: "decorators", title: "Decorators", emoji: "🎀", group: "Lesson", keywords: ["decorators", "stage 3", "@decorator", "method decorator", "TypeScript decorators", "Babel"] },
        { id: "scenario", title: "Real world scenario: a fluent API client", emoji: "🎬", group: "QA essential", keywords: ["API client", "fluent API", "Proxy", "REST", "URL builder", "fake fetch"] },
        { id: "readonly", title: "A read only view", emoji: "🏋️", group: "Easy practice" },
        { id: "defaults", title: "Defaults for missing keys", emoji: "🏋️", group: "Medium practice" },
        { id: "htmltag", title: "An escaping HTML tag", emoji: "🏋️", group: "Hard practice" },
        { id: "recorder", title: "Record every method call", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-node-deep", title: "Node.js in depth", emoji: "🟩", page: "content/javascript/js-node-deep.html",
        summary: "EventEmitter with once, error events and async iteration, generating and filtering a big file with streams, backpressure and drain, buffers, encodings, SHA-256 and HMAC webhook signatures, the built in SQLite database with prepared statements, spawn with streaming output and SIGTERM clean up, and a log check CLI tested with spawnSync.",
        keywords: ["Node.js", "EventEmitter", "streams", "pipeline", "backpressure", "Buffer", "crypto", "HMAC", "webhook", "node:sqlite", "SQLite", "spawn", "SIGTERM", "exit code", "parseArgs", "CLI", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "events", title: "Events and EventEmitter", emoji: "📣", group: "QA essential", keywords: ["EventEmitter", "on", "once", "emit", "error event", "events.once", "events.on", "async iterator", "AbortSignal", "listener", "reporter"] },
        { id: "streams", title: "Streams and backpressure", emoji: "🌊", group: "QA essential", keywords: ["streams", "Readable", "Writable", "Transform", "pipeline", "stream/promises", "backpressure", "highWaterMark", "drain", "readline", "Readable.from", "objectMode", "big files"] },
        { id: "buffers", title: "Buffers, encodings and crypto", emoji: "🔢", group: "QA essential", keywords: ["Buffer", "Uint8Array", "encoding", "UTF-8", "base64", "hex", "crypto", "createHash", "sha256", "HMAC", "timingSafeEqual", "randomUUID", "webhook signature"] },
        { id: "sqlite", title: "The built in SQLite database", emoji: "🗄️", group: "QA essential", keywords: ["node:sqlite", "SQLite", "DatabaseSync", "SQL", "prepared statement", "placeholder", "JOIN", "GROUP BY", "test data", "database testing", "constraint"] },
        { id: "process", title: "Processes, signals and graceful shutdown", emoji: "⚙️", group: "QA essential", keywords: ["child_process", "spawn", "exec", "stdout", "signals", "SIGTERM", "SIGINT", "graceful shutdown", "exit code", "process.exitCode", "kill"] },
        { id: "cli", title: "Building and testing a command line tool", emoji: "💻", group: "QA essential", keywords: ["CLI", "command line tool", "parseArgs", "util.parseArgs", "bin", "shebang", "styleText", "NO_COLOR", "spawnSync", "exit code", "readline", "CI gate"] },
        { id: "bus", title: "A tiny event bus", emoji: "🏋️", group: "Easy practice" },
        { id: "splitter", title: "Split chunks into lines", emoji: "🏋️", group: "Medium practice" },
        { id: "checksum", title: "Verify a checksum", emoji: "🏋️", group: "Hard practice" },
        { id: "flags", title: "Parse command line flags", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "js-testing", title: "Testing with JavaScript", emoji: "🧪", blurb: "Unit tests, API tests and browser automation with node:test, Jest, Vitest, Mocha, supertest, Playwright, Selenium and Cypress.", topics: [
      { id: "js-unit-testing", title: "Unit Testing: node:test, Jest, Vitest and Mocha", emoji: "🧪", page: "content/javascript/js-unit-testing.html",
        summary: "The test pyramid and Arrange Act Assert, node:test with mocks and a fake clock, Jest matchers, test.each, module mocks, spies and fake timers, Vitest and Mocha with Chai and Sinon, seven ways to run a node:test suite and five with Jest, a CI matrix with shards, UI component tests with jsdom, Testing Library and user-event, API route tests with supertest, outgoing HTTP faked with nock, and a bug turned into a regression test.",
        keywords: ["unit testing", "node:test", "Jest", "Vitest", "Mocha", "Chai", "Sinon", "mock", "spy", "stub", "fake timers", "test.each", "filter", "tags", "shard", "coverage", "JUnit", "CI", "jsdom", "Testing Library", "supertest", "nock", "TDD", "regression test"],
        added: "2026-10-20",
        sections: [
        { id: "basics", title: "What a unit test is", emoji: "🧱", group: "QA essential", keywords: ["unit test", "test pyramid", "Arrange Act Assert", "AAA", "node:test", "describe", "it", "assert", "assert.equal", "assert.throws", "deepEqual"] },
        { id: "doubles", title: "Mocks, spies, stubs and fake timers", emoji: "🎭", group: "QA essential", keywords: ["mock", "spy", "stub", "fake", "test double", "mock.fn", "mock.timers", "fake timers", "dependency injection", "beforeEach", "callCount"] },
        { id: "jest", title: "Jest", emoji: "🃏", group: "QA essential", keywords: ["Jest", "expect", "toBe", "toEqual", "toMatchObject", "toThrow", "test.each", "jest.fn", "jest.mock", "jest.spyOn", "mockResolvedValue", "useFakeTimers", "advanceTimersByTime"] },
        { id: "vitest-mocha", title: "Vitest and Mocha", emoji: "⚡", group: "QA essential", keywords: ["Vitest", "vi.fn", "vi.useFakeTimers", "Mocha", "Chai", "Sinon", "expect", "spy", "stub", "mocharc", "debounce", "concurrent"] },
        { id: "running", title: "Running tests in different ways", emoji: "🏃", group: "QA essential", keywords: ["run tests", "filter", "grep", "test-name-pattern", "-t", "tags", "only", "skip", "todo", "watch", "shard", "bail", "reporter", "junit", "coverage", "coverage threshold", "CI", "GitHub Actions", "matrix"] },
        { id: "web", title: "Unit testing web (UI) code", emoji: "🖼️", group: "QA essential", keywords: ["jsdom", "Testing Library", "user-event", "screen", "getByRole", "getByLabelText", "findByText", "waitFor", "component test", "testEnvironment", "jest-environment-jsdom", "environment jsdom"] },
        { id: "api", title: "Unit testing API code", emoji: "🔌", group: "QA essential", keywords: ["API unit test", "supertest", "nock", "Express", "route test", "status code", "mock HTTP", "outgoing request", "dependency injection", "503", "404"] },
        { id: "scenario", title: "Real world scenario: turn a bug report into a test", emoji: "🎬", group: "QA essential", keywords: ["regression test", "bug report", "TDD", "test driven development", "red green refactor", "rounding", "money", "paise"] },
        { id: "deep", title: "Deep equality", emoji: "🏋️", group: "Easy practice" },
        { id: "spy", title: "A spy function", emoji: "🏋️", group: "Medium practice" },
        { id: "runner", title: "A tiny test runner", emoji: "🏋️", group: "Hard practice" },
        { id: "shard", title: "Split tests into shards", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-api-testing", title: "Automated API Testing with JavaScript", emoji: "🔌", page: "content/javascript/js-api-testing.html",
        summary: "What an API test checks, a CRUD flow against a running server, JSON Schema validation with Ajv that catches breaking changes, data driven negative and boundary tests, login with tokens and checking side effects and conflicts, Playwright request with webServer, Cypress, Newman and k6 in brief, percentiles for response times, and an order flow written as named subtests.",
        keywords: ["API testing", "REST", "CRUD", "fetch", "supertest", "Playwright request", "Ajv", "JSON Schema", "contract test", "negative testing", "boundary", "auth", "401", "409", "p95", "response time", "cleanup", "Newman", "k6"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "What an API test checks", emoji: "🗺️", group: "QA essential", keywords: ["API testing", "what to test", "status code", "headers", "body", "schema", "side effects", "negative testing", "security", "response time", "test pyramid"] },
        { id: "live", title: "Testing a running server: a CRUD flow", emoji: "🔁", group: "QA essential", keywords: ["CRUD", "running server", "fetch", "port 0", "before", "after", "POST", "GET", "PATCH", "DELETE", "Location header", "node:test"] },
        { id: "schema", title: "Checking the shape with JSON Schema", emoji: "📐", group: "QA essential", keywords: ["JSON Schema", "Ajv", "schema validation", "contract test", "additionalProperties", "required", "OpenAPI", "breaking change", "response shape"] },
        { id: "negative", title: "Negative, boundary and data driven tests", emoji: "🚫", group: "QA essential", keywords: ["negative testing", "boundary values", "data driven", "it.each", "test.each", "validation", "400", "malformed JSON", "supertest", "equivalence classes"] },
        { id: "auth", title: "Authentication, state and conflicts", emoji: "🔐", group: "QA essential", keywords: ["authentication", "Bearer token", "beforeAll", "supertest auth", "401", "409 Conflict", "stock", "state change", "side effect", "Jest ESM"] },
        { id: "playwright", title: "API testing with Playwright", emoji: "🎭", group: "QA essential", keywords: ["Playwright", "request fixture", "APIRequestContext", "webServer", "baseURL", "toBeOK", "cy.request", "Newman", "Postman", "k6"] },
        { id: "performance", title: "Response times", emoji: "⏱️", group: "QA essential", keywords: ["response time", "latency", "percentile", "p95", "p99", "median", "throughput", "error rate", "load test", "performance"] },
        { id: "scenario", title: "Real world scenario: buying the last two mugs", emoji: "🎬", group: "QA essential", keywords: ["end to end API flow", "subtests", "t.test", "stock", "sold out", "409", "test data cleanup", "API client"] },
        { id: "check", title: "Check a response", emoji: "🏋️", group: "Easy practice" },
        { id: "schema-mini", title: "A tiny schema validator", emoji: "🏋️", group: "Medium practice" },
        { id: "pct", title: "Percentiles", emoji: "🏋️", group: "Hard practice" },
        { id: "diff", title: "What changed in the response?", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-ui-automation", title: "UI Automation: Playwright, Selenium, Cypress and WebdriverIO", emoji: "🎭", page: "content/javascript/js-ui-automation.html",
        summary: "How each tool reaches the browser, a Playwright suite with role based locators and web first assertions, a strict mode failure, page.route for errors and fake data, waitForRequest, a page object with a fixture, retries that report flaky tests, the Playwright command line, Selenium WebDriver with Mocha, explicit waits, XPath and screenshots, the same tests in Cypress and WebdriverIO, and a sharded GitHub Actions workflow.",
        keywords: ["UI automation", "end to end", "Playwright", "Selenium", "WebDriver", "Cypress", "WebdriverIO", "locator", "getByRole", "auto-waiting", "explicit wait", "strict mode", "page.route", "cy.intercept", "page object", "fixture", "retries", "flaky", "trace", "shard", "CI"],
        added: "2026-10-20",
        sections: [
        { id: "tools", title: "The tools and how they drive a browser", emoji: "🧭", group: "QA essential", keywords: ["UI automation", "end to end", "Playwright", "Selenium", "WebDriver", "Cypress", "WebdriverIO", "CDP", "BiDi", "Appium", "browser driver", "tool comparison"] },
        { id: "playwright", title: "Playwright: locators and web first assertions", emoji: "🎭", group: "QA essential", keywords: ["Playwright", "page", "locator", "getByRole", "getByLabel", "getByText", "getByTestId", "filter", "hasText", "expect", "toHaveText", "toHaveCount", "toBeVisible", "auto-waiting", "strict mode", "web first assertions"] },
        { id: "network", title: "Controlling the network", emoji: "🛰️", group: "QA essential", keywords: ["page.route", "route.fulfill", "network mocking", "waitForRequest", "waitForResponse", "postDataJSON", "error state", "cy.intercept", "stub API"] },
        { id: "framework", title: "Page objects, fixtures and retries", emoji: "🏗️", group: "QA essential", keywords: ["page object", "fixture", "test.extend", "use", "retries", "flaky", "trace", "testInfo.retry", "grep", "headed", "debug", "UI mode", "codegen", "shard", "repeat-each"] },
        { id: "selenium", title: "Selenium WebDriver", emoji: "🚗", group: "QA essential", keywords: ["Selenium", "WebDriver", "selenium-webdriver", "chromedriver", "By", "xpath", "css", "driver.wait", "until", "explicit wait", "implicit wait", "sendKeys", "Grid", "Mocha", "screenshot"] },
        { id: "cypress", title: "Cypress and WebdriverIO", emoji: "🌲", group: "QA essential", keywords: ["Cypress", "cy.get", "cy.contains", "cy.intercept", "cy.wait", "alias", "custom command", "should", "command queue", "WebdriverIO", "wdio", "$", "$$", "Appium"] },
        { id: "scenario", title: "Real world scenario: a UI suite in CI", emoji: "🎬", group: "QA essential", keywords: ["CI", "GitHub Actions", "shard", "matrix", "HTML report", "trace", "artifact", "playwright install", "pipeline", "flaky tests", "test strategy"] },
        { id: "pick", title: "Pick the best locator", emoji: "🏋️", group: "Easy practice" },
        { id: "wait", title: "A waitFor helper", emoji: "🏋️", group: "Medium practice" },
        { id: "filter", title: "filter({ hasText }) for cards", emoji: "🏋️", group: "Hard practice" },
        { id: "flaky", title: "Find the flaky tests", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "ts", title: "TypeScript", emoji: "🔷", blurb: "TypeScript from the first type to generics, advanced types, typed projects and test automation written in TypeScript.", topics: [
      { id: "ts-basics", title: "TypeScript fundamentals", emoji: "🔷", page: "content/javascript/ts-basics.html",
        summary: "What TypeScript is and how Node.js runs it, a modern tsconfig, everyday types, inference, readonly and unknown, typed functions, callbacks and overloads, interface against type, unions and narrowing, enum against as const, what strict mode catches, and reading untyped JSON safely with a type predicate.",
        keywords: ["TypeScript", "tsc", "tsconfig", "types", "inference", "unknown", "any", "interface", "type alias", "union", "narrowing", "enum", "as const", "strict", "type predicate", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "why", title: "What TypeScript is and how it runs", emoji: "🔷", group: "QA essential", keywords: ["TypeScript", "tsc", "type annotation", "type erasure", "type stripping", "tsconfig.json", "strict", "noEmit", "erasableSyntaxOnly", "@types/node", "tsx"] },
        { id: "everyday", title: "Everyday types", emoji: "🧱", group: "QA essential", keywords: ["type inference", "string", "number", "boolean", "array type", "tuple", "object type", "optional property", "readonly", "literal type", "unknown", "any", "never", "const inference"] },
        { id: "functions", title: "Functions", emoji: "🧩", group: "Lesson", keywords: ["function types", "parameter types", "return type", "optional parameter", "default parameter", "rest parameter", "overloads", "void", "never", "callback type", "type assertion", "as"] },
        { id: "shapes", title: "interface and type", emoji: "📐", group: "QA essential", keywords: ["interface", "type alias", "extends", "intersection", "&", "Record", "index signature", "declaration merging", "object shape"] },
        { id: "narrowing", title: "Unions and narrowing", emoji: "🔍", group: "QA essential", keywords: ["union type", "narrowing", "typeof", "instanceof", "in operator", "equality narrowing", "discriminated union", "control flow analysis", "type guard"] },
        { id: "enums", title: "Enums and their modern alternative", emoji: "🏷️", group: "Lesson", keywords: ["enum", "const enum", "as const", "keyof typeof", "erasableSyntaxOnly", "literal union", "string enum"] },
        { id: "strict", title: "Strict options", emoji: "🛡️", group: "QA essential", keywords: ["strict", "strictNullChecks", "noImplicitAny", "noUncheckedIndexedAccess", "exactOptionalPropertyTypes", "tsconfig options", "undefined", "null"] },
        { id: "scenario", title: "Real world scenario: typed results from untyped JSON", emoji: "🎬", group: "QA essential", keywords: ["unknown", "JSON.parse", "type predicate", "is", "runtime validation", "type guard", "filter", "test results"] },
        { id: "isorder", title: "A type guard", emoji: "🏋️", group: "Easy practice" },
        { id: "describe", title: "Handle a union", emoji: "🏋️", group: "Medium practice" },
        { id: "browsers", title: "An as const lookup", emoji: "🏋️", group: "Hard practice" },
        { id: "safeget", title: "Safe reads with defaults", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "ts-advanced", title: "Advanced TypeScript types", emoji: "🧬", page: "content/javascript/ts-advanced.html",
        summary: "Generic functions and types, typeof, keyof and indexed access, the utility types and what they cannot prove, mapped and conditional types with infer, template literal types for routes and test ids, satisfies for config objects, exhaustive switches with never, assertion functions and branded ids, and typed API routes with inferred path parameters.",
        keywords: ["generics", "keyof", "indexed access", "utility types", "Partial", "Omit", "Record", "mapped types", "conditional types", "infer", "template literal types", "satisfies", "never", "exhaustive", "assertion functions", "branded types", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "generics", title: "Generics", emoji: "🧬", group: "QA essential", keywords: ["generics", "type parameter", "<T>", "generic constraint", "extends", "default type parameter", "generic type", "inference"] },
        { id: "keyof", title: "typeof, keyof and indexed access", emoji: "🔑", group: "Lesson", keywords: ["typeof type", "keyof", "indexed access type", "T[K]", "lookup type", "K extends keyof T", "Partial"] },
        { id: "utility", title: "Utility types", emoji: "🧰", group: "QA essential", keywords: ["utility types", "Partial", "Required", "Pick", "Omit", "Record", "Readonly", "ReturnType", "Parameters", "Awaited", "NonNullable", "Exclude", "Extract", "excess property check"] },
        { id: "mapped", title: "Mapped and conditional types", emoji: "🗺️", group: "Lesson", keywords: ["mapped types", "key remapping", "as", "Capitalize", "-readonly", "conditional types", "infer", "distributive conditional types", "never"] },
        { id: "template", title: "Template literal types", emoji: "🧵", group: "QA essential", keywords: ["template literal types", "string patterns", "Capitalize", "Uppercase", "route types", "event names", "data-testid"] },
        { id: "satisfies", title: "satisfies", emoji: "✔️", group: "QA essential", keywords: ["satisfies", "type annotation", "widening", "config object", "as const satisfies", "precise types"] },
        { id: "exhaustive", title: "Exhaustive checks with never", emoji: "🧱", group: "QA essential", keywords: ["discriminated union", "exhaustive check", "never", "assertNever", "switch", "keyword driven", "state machine"] },
        { id: "assertions", title: "Assertion functions and branded types", emoji: "🛂", group: "QA essential", keywords: ["assertion function", "asserts", "asserts value is", "branded type", "nominal typing", "opaque type", "type safety", "environment variables"] },
        { id: "scenario", title: "Real world scenario: typed API routes", emoji: "🎬", group: "QA essential", keywords: ["typed API client", "route types", "path parameters", "infer", "OpenAPI", "openapi-typescript", "response types"] },
        { id: "pick", title: "A typed pick at run time", emoji: "🏋️", group: "Easy practice" },
        { id: "groupkey", title: "Group by a key name", emoji: "🏋️", group: "Medium practice" },
        { id: "steps", title: "An exhaustive step runner", emoji: "🏋️", group: "Hard practice" },
        { id: "orderid", title: "Parse a branded id", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "ts-projects", title: "TypeScript classes and real projects", emoji: "🏛️", page: "content/javascript/ts-projects.html",
        summary: "Classes with access modifiers, abstract members and interfaces, TypeScript private compared with #private, standard decorators that log steps and retry, declaration files and module augmentation, type checking JavaScript with JSDoc, a safe migration plan and the tools to run TypeScript, and a typed page object hierarchy.",
        keywords: ["TypeScript classes", "abstract class", "access modifiers", "private", "#private", "decorators", ".d.ts", "declaration files", "module augmentation", "JSDoc", "checkJs", "migration", "tsc --noEmit", "page object", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "classes", title: "Classes in TypeScript", emoji: "🏛️", group: "QA essential", keywords: ["class", "public", "private", "protected", "readonly", "abstract class", "abstract method", "implements", "override", "parameter properties", "#private", "access modifiers"] },
        { id: "decorators", title: "Decorators", emoji: "🎀", group: "QA essential", keywords: ["decorators", "method decorator", "ClassMethodDecoratorContext", "stage 3 decorators", "experimentalDecorators", "test.step", "retry decorator"] },
        { id: "dts", title: "Declaration files and augmentation", emoji: "📜", group: "QA essential", keywords: ["declaration file", ".d.ts", "declare module", "declare global", "module augmentation", "@types", "DefinitelyTyped", "custom matchers", "Cypress.Chainable"] },
        { id: "jsdoc", title: "Checking JavaScript with JSDoc", emoji: "📝", group: "QA essential", keywords: ["JSDoc", "checkJs", "@ts-check", "allowJs", "@param", "@returns", "@typedef", "type checking JavaScript"] },
        { id: "migrate", title: "Moving a project to TypeScript, and the tools around it", emoji: "🚚", group: "QA essential", keywords: ["migration", "JavaScript to TypeScript", "allowJs", "tsc --noEmit", "tsx", "esbuild", "vite", "path aliases", "package imports", "CI type check"] },
        { id: "scenario", title: "Real world scenario: a typed page object hierarchy", emoji: "🎬", group: "QA essential", keywords: ["page object model", "abstract class", "typed page object", "fluent page objects", "protected", "test data types"] },
        { id: "account", title: "A class with a private field", emoji: "🏋️", group: "Easy practice" },
        { id: "abstract", title: "Enforce an abstract method at run time", emoji: "🏋️", group: "Medium practice" },
        { id: "wrap", title: "A decorator by hand", emoji: "🏋️", group: "Hard practice" },
        { id: "steplog", title: "A typed step log", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "ts-testing", title: "Test automation in TypeScript", emoji: "🧪", page: "content/javascript/ts-testing.html",
        summary: "How TypeScript catches mistakes in test code, running unit tests in TypeScript with node:test, Vitest and Jest, testing types with expectTypeOf, typed Playwright page objects and fixtures, an API client that checks every response with zod, a CI pipeline that type checks first, and typed test data builders.",
        keywords: ["TypeScript testing", "Playwright TypeScript", "Vitest", "node:test", "ts-jest", "expectTypeOf", "typed fixtures", "page object", "zod", "z.infer", "API client", "tsc --noEmit", "typescript-eslint", "test data builder", "interview"],
        added: "2026-10-20",
        sections: [
        { id: "why", title: "Why write tests in TypeScript", emoji: "🛡️", group: "QA essential", keywords: ["TypeScript tests", "typed tests", "compile time errors", "test typos", "Playwright types", "fixture types", "editor auto complete"] },
        { id: "unit", title: "Unit tests in TypeScript", emoji: "🧪", group: "QA essential", keywords: ["node --test", "type stripping", "Vitest TypeScript", "it.each", "ts-jest", "@swc/jest", "babel-jest", "jest.config.ts", "tsc --noEmit"] },
        { id: "typetests", title: "Type tests", emoji: "🔬", group: "QA essential", keywords: ["expectTypeOf", "expect-type", "type tests", "test-d.ts", "vitest --typecheck", "toEqualTypeOf", "tsd"] },
        { id: "pw", title: "Playwright in TypeScript", emoji: "🎭", group: "QA essential", keywords: ["Playwright TypeScript", "typed page object", "test.extend", "typed fixtures", "option fixture", "Locator type", "Page type", "playwright.config.ts"] },
        { id: "api", title: "A typed API client with run time checks", emoji: "🔌", group: "QA essential", keywords: ["zod", "z.infer", "schema validation", "runtime validation", "API client", "contract testing", "ZodError", "unknown JSON"] },
        { id: "ci", title: "TypeScript in CI", emoji: "🚦", group: "QA essential", keywords: ["CI", "GitHub Actions", "tsc --noEmit", "typescript-eslint", "no-floating-promises", "await-thenable", "projectService", "quality gate"] },
        { id: "scenario", title: "Real world scenario: typed test data builders", emoji: "🎬", group: "QA essential", keywords: ["test data builder", "factory", "Partial", "generics", "test data", "unique ids", "fixtures", "object mother"] },
        { id: "builder", title: "A test data builder", emoji: "🏋️", group: "Easy practice" },
        { id: "parse", title: "Check a response by hand", emoji: "🏋️", group: "Medium practice" },
        { id: "fixtures", title: "A fixture runner", emoji: "🏋️", group: "Hard practice" },
        { id: "poll", title: "A polling assertion", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "js-expert", title: "Expert and latest", emoji: "🧠", blurb: "The newest language features, performance, patterns, security and the habits of expert JavaScript developers and testers.", topics: [
      { id: "js-modern", title: "Modern JavaScript: ES2020 to 2026", emoji: "🆕", page: "content/javascript/js-modern.html",
        summary: "The yearly release process and a table of editions, ES2020 to ES2023 features for safer access and copies, ES2024 and ES2025 grouping, iterator helpers, Set methods and safer regular expressions, the newest features such as using and await using, Error.isError and base64, Temporal for dates, ages, time zones and durations, and modernising an old helper with a check that its results did not change.",
        keywords: ["ES2020", "ES2021", "ES2022", "ES2023", "ES2024", "ES2025", "ES2026", "optional chaining", "nullish coalescing", "toSorted", "groupBy", "iterator helpers", "RegExp.escape", "Promise.try", "using", "Symbol.dispose", "Temporal", "latest JavaScript"],
        added: "2026-10-20",
        sections: [
        { id: "yearly", title: "How JavaScript grows every year", emoji: "📅", group: "Lesson", keywords: ["ECMAScript", "ES2015", "ES6", "ES2020", "ES2021", "ES2022", "ES2023", "ES2024", "ES2025", "ES2026", "TC39", "stage 4", "browser support"] },
        { id: "es2020", title: "ES2020 to ES2023: safer access and copies", emoji: "❓", group: "QA essential", keywords: ["optional chaining", "?.", "nullish coalescing", "??", "BigInt", "logical assignment", "??=", "replaceAll", "at", "Object.hasOwn", "error cause", "findLast", "toSorted", "toReversed", "toSpliced", "with", "change by copy"] },
        { id: "es2024", title: "ES2024 and ES2025: grouping, iterators, safer regexes", emoji: "🧰", group: "QA essential", keywords: ["Object.groupBy", "Map.groupBy", "Promise.withResolvers", "v flag", "isWellFormed", "iterator helpers", "Set methods", "RegExp.escape", "Promise.try", "duplicate named groups", "regex modifiers", "Float16Array", "import attributes"] },
        { id: "es2026", title: "Arriving now: using, Error.isError and more", emoji: "🆕", group: "QA essential", keywords: ["using", "await using", "Symbol.dispose", "Symbol.asyncDispose", "explicit resource management", "Error.isError", "Array.fromAsync", "toBase64", "fromBase64", "getOrInsertComputed", "Iterator.concat", "JSON.parse source"] },
        { id: "temporal", title: "Temporal: dates done right", emoji: "🕰️", group: "QA essential", keywords: ["Temporal", "PlainDate", "PlainDateTime", "ZonedDateTime", "Instant", "Duration", "time zone", "daylight saving", "leap year", "age check", "immutable dates"] },
        { id: "scenario", title: "Real world scenario: modernise safely", emoji: "🎬", group: "QA essential", keywords: ["refactoring", "modernise", "legacy code", "characterisation test", "optional chaining", "groupBy", "toSorted"] },
        { id: "safe", title: "Safe access with defaults", emoji: "🏋️", group: "Easy practice" },
        { id: "copy", title: "Sort without side effects", emoji: "🏋️", group: "Medium practice" },
        { id: "group", title: "Write groupBy yourself", emoji: "🏋️", group: "Hard practice" },
        { id: "dispose", title: "Clean up like using", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "js-expert", title: "Expert JavaScript: performance, security and test quality", emoji: "🏆", page: "content/javascript/js-expert.html",
        summary: "Counting steps and benchmarking with a warm up and median, listener leaks and weak references, memoize, pipe, strategy, observer, builder and factory patterns, worker threads and Web Workers, XSS and prototype pollution with a security checklist, property based testing, mutation testing and order dependent flaky tests, and balancing CI shards by duration.",
        keywords: ["performance", "Big O", "benchmark", "memory leak", "WeakMap", "design patterns", "test data builder", "worker threads", "Web Workers", "XSS", "prototype pollution", "security testing", "property based testing", "mutation testing", "flaky tests", "CI sharding", "expert JavaScript"],
        added: "2026-10-20",
        sections: [
        { id: "performance", title: "Performance: count first, then measure", emoji: "⚡", group: "QA essential", keywords: ["performance", "Big O", "O(n)", "O(n²)", "performance.now", "benchmark", "median", "warm up", "JIT", "Core Web Vitals", "LCP", "INP", "CLS", "Lighthouse"] },
        { id: "memory", title: "Memory: leaks and weak references", emoji: "🧠", group: "QA essential", keywords: ["memory leak", "garbage collection", "event listener leak", "AbortController", "AbortSignal", "WeakMap", "WeakRef", "WeakSet", "FinalizationRegistry", "heap snapshot", "CDP"] },
        { id: "patterns", title: "Patterns experts reach for", emoji: "🧩", group: "QA essential", keywords: ["design patterns", "memoize", "pipe", "compose", "strategy pattern", "observer pattern", "pub sub", "builder pattern", "test data builder", "factory", "page object"] },
        { id: "workers", title: "Workers: real parallel work", emoji: "🧵", group: "QA essential", keywords: ["worker_threads", "Web Worker", "Worker", "postMessage", "workerData", "parallel", "CPU bound", "main thread", "test workers"] },
        { id: "security", title: "Security every JavaScript developer should test", emoji: "🔐", group: "QA essential", keywords: ["security", "XSS", "cross site scripting", "innerHTML", "textContent", "Content Security Policy", "CSP", "prototype pollution", "__proto__", "eval", "npm audit", "secrets", "OWASP"] },
        { id: "quality", title: "Test quality: properties, mutants and flaky tests", emoji: "🎯", group: "QA essential", keywords: ["property based testing", "fast-check", "seed", "shrinking", "mutation testing", "Stryker", "mutation score", "flaky test", "test isolation", "beforeEach", "test order"] },
        { id: "scenario", title: "Real world scenario: a faster CI pipeline", emoji: "🎬", group: "QA essential", keywords: ["CI", "sharding", "test splitting", "parallel", "JUnit timings", "longest processing time", "pipeline speed"] },
        { id: "memo", title: "Memoize a pure function", emoji: "🏋️", group: "Easy practice" },
        { id: "debounce", title: "Debounce a search box", emoji: "🏋️", group: "Medium practice" },
        { id: "escape", title: "Escape HTML", emoji: "🏋️", group: "Hard practice" },
        { id: "shards", title: "Balance test shards", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] }
  ];
}
/* ===== end of js-build ===== */

/* ===== Coming soon helper ===== */

/* Builds a "Planned chapters" module from [title, emoji, summary] rows.
   The topics have no page, so they show as Coming soon until one is added. */
function soonModule(rows) {
  return {
    id: 'planned', title: 'Planned chapters', emoji: '🗓️',
    blurb: 'These chapters are being written. Each one opens as soon as its page is ready.',
    topics: rows.map(([title, emoji, summary]) => ({
      id: title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''),
      title, emoji, summary, soon: true
    }))
  };
}

/* ===== claude-build: Master the Claude chapters. Generated by tools/claude-build/build.py, edit the topic files instead. ===== */
function claudeModules() {
  return [
    { id: "claude-foundations", title: "Foundations", emoji: "🌱", blurb: "What Claude is, how to talk to it, and how to give it the right information at the right time.", topics: [
      { id: "claude-meet", title: "Meet Claude: Models, Tokens, Projects and Skills", emoji: "👋", page: "content/claude/claude-meet.html",
        summary: "The Claude products (claude.ai, Claude Code, the API), the four models with their API names and prices, tokens and the 1M token context window, why every turn re-sends the chat, a first practical prompt, claude.ai Projects with instructions and knowledge, Skills uploaded as a ZIP, and a map of every file this subject teaches.",
        keywords: ["Claude", "models", "Opus", "Sonnet", "Haiku", "Fable", "tokens", "context window", "pricing", "Projects", "project instructions", "Skills", "claude.ai"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "What Claude is, in plain words", emoji: "👋", group: "Beginner path", keywords: ["what is Claude", "Anthropic", "claude.ai", "Claude Code", "Claude API", "desktop app"] },
        { id: "models", title: "The Claude models and when to pick each", emoji: "🧠", group: "Beginner path", keywords: ["models", "Opus", "Sonnet", "Haiku", "Fable", "pricing", "model id"] },
        { id: "tokens", title: "Tokens and the context window", emoji: "🔢", group: "Beginner path", keywords: ["tokens", "context window", "1M tokens", "input tokens", "output tokens", "cost"] },
        { id: "turns", title: "How a conversation really works", emoji: "🔁", group: "Beginner path", keywords: ["conversation", "messages", "system prompt", "new chat", "stateless"] },
        { id: "first", title: "Your first useful prompt", emoji: "✍️", group: "Beginner path", keywords: ["first prompt", "daily automation", "table", "orders"] },
        { id: "projects", title: "claude.ai Projects: instructions plus knowledge", emoji: "🗂️", group: "Beginner path", keywords: ["claude.ai Projects", "project instructions", "project knowledge", "custom instructions"] },
        { id: "skills-intro", title: "Skills: teach Claude a task once", emoji: "🧰", group: "Beginner path", keywords: ["skills", "SKILL.md", "upload skill", "zip", "capabilities"] },
        { id: "map", title: "The map of this subject", emoji: "🗺️", group: "Beginner path", keywords: ["overview", "which file", "map"] },
        { id: "habits", title: "Safe habits from day one", emoji: "🛡️", group: "Beginner path", keywords: ["safety", "privacy", "API keys", "review"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-prompting", title: "Prompt Engineering That Works", emoji: "✍️", page: "content/claude/claude-prompting.html",
        summary: "Clear and direct prompts, giving reasons, few shot examples in example tags, XML tags with long documents first, roles in the system prompt, controlling output format and why prefill no longer works, step by step thinking, reusable prompt templates for daily work, prompt chains for self correction, and a seven step prompt recipe.",
        keywords: ["prompt engineering", "prompting", "few shot", "examples", "XML tags", "system prompt", "role", "output format", "prefill", "chain of thought", "template", "prompt chaining"],
        added: "2026-10-20",
        sections: [
        { id: "clear", title: "Be clear and direct", emoji: "🎯", group: "Beginner path", keywords: ["clear prompt", "specific", "golden rule", "new employee"] },
        { id: "why", title: "Say why, not only what", emoji: "💡", group: "Beginner path", keywords: ["context", "motivation", "reason", "positive instructions"] },
        { id: "examples", title: "Show examples", emoji: "🧪", group: "Beginner path", keywords: ["few shot", "multishot", "examples", "example tags", "classification"] },
        { id: "xml", title: "Use XML tags to separate the pieces", emoji: "🏷️", group: "Lesson", keywords: ["XML tags", "documents", "long context", "quotes", "grounding"] },
        { id: "role", title: "Give Claude a role", emoji: "🎭", group: "Lesson", keywords: ["role", "system prompt", "persona", "tutor"] },
        { id: "format", title: "Control the format of the answer", emoji: "📐", group: "Beginner path", keywords: ["format", "output format", "list", "JSON", "prefill", "preamble"] },
        { id: "think", title: "Let Claude think before answering", emoji: "🤔", group: "Lesson", keywords: ["step by step", "thinking", "chain of thought", "adaptive thinking"] },
        { id: "template", title: "Prompt templates for daily work", emoji: "🧩", group: "Beginner path", keywords: ["template", "variables", "daily automation", "inbox triage"] },
        { id: "chain", title: "Chain prompts: draft, review, refine", emoji: "⛓️", group: "Lesson", keywords: ["prompt chaining", "self correction", "review", "pipeline"] },
        { id: "recipe", title: "A recipe card for any prompt", emoji: "📋", group: "Beginner path", keywords: ["prompt checklist", "recipe", "structure"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-context", title: "Context Engineering: The Right Information at the Right Time", emoji: "🧠", page: "content/claude/claude-context.html",
        summary: "Context engineering versus prompt engineering, context rot and the attention budget, instructions at the right altitude, tools and examples as context, just in time retrieval, compaction, progress files and subagents for long tasks, what Claude Code loads when and what survives /compact, and a checklist for where each piece of context belongs.",
        keywords: ["context engineering", "context window", "context rot", "attention budget", "just in time", "retrieval", "compaction", "/compact", "/context", "/clear", "progress notes", "subagents"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "Context engineering in one sentence", emoji: "🧠", group: "Beginner path", keywords: ["context engineering", "context", "tokens", "what Claude sees"] },
        { id: "rot", title: "Why more is not always better", emoji: "🫧", group: "Beginner path", keywords: ["context rot", "attention budget", "window size", "/context"] },
        { id: "altitude", title: "Write instructions at the right altitude", emoji: "🎚️", group: "Lesson", keywords: ["system prompt", "altitude", "principles", "instructions"] },
        { id: "tools", title: "Tools and examples are context too", emoji: "🔧", group: "Lesson", keywords: ["tools", "tool descriptions", "MCP tools", "examples"] },
        { id: "jit", title: "Just in time retrieval", emoji: "🎯", group: "Beginner path", keywords: ["just in time", "retrieval", "search", "progressive disclosure", "RAG"] },
        { id: "long", title: "Long tasks: compaction, notes and subagents", emoji: "⏳", group: "Lesson", keywords: ["compaction", "structured notes", "progress file", "subagents", "long running tasks"] },
        { id: "cc", title: "Context tools in Claude Code", emoji: "💻", group: "Beginner path", keywords: ["/context", "/clear", "/compact", "/btw", "compaction", "context cost"] },
        { id: "checklist", title: "A context checklist for any task", emoji: "✅", group: "Beginner path", keywords: ["checklist", "where to put context"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "claude-code-files", title: "Claude Code and its files", emoji: "🛠️", blurb: "Claude Code step by step, and exactly what goes in CLAUDE.md, rules, skills, settings, hooks, agents and MCP files.", topics: [
      { id: "claude-code-start", title: "Claude Code: First Steps", emoji: "💻", page: "content/claude/claude-code-start.html",
        summary: "What Claude Code is, installing it on macOS, Linux and Windows, first requests, the gather, act and verify loop with a real test run, the six permission modes, plan mode and the explore, plan, code, commit workflow, Esc, /rewind and resuming sessions, the most used slash commands, and a full map of the .claude folder and home folder, including why there is no single rules.md file.",
        keywords: ["Claude Code", "install", "permission modes", "plan mode", "Shift+Tab", "agent loop", "/rewind", "checkpoints", "--continue", "--resume", "slash commands", ".claude folder", "settings.local.json"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "What Claude Code is", emoji: "💻", group: "Beginner path", keywords: ["Claude Code", "agent", "terminal", "VS Code", "JetBrains", "desktop app"] },
        { id: "install", title: "Install and start, step by step", emoji: "📥", group: "Beginner path", keywords: ["install", "curl install.sh", "winget", "brew", "claude --version", "login"] },
        { id: "loop", title: "How it works: the agent loop", emoji: "🔄", group: "Beginner path", keywords: ["agent loop", "tools", "Read", "Edit", "Bash", "Grep", "verify", "tests"] },
        { id: "perms", title: "Permission modes: how much Claude may do alone", emoji: "🚦", group: "Beginner path", keywords: ["permission modes", "Shift+Tab", "acceptEdits", "plan mode", "auto mode", "bypassPermissions", "defaultMode"] },
        { id: "plan", title: "Explore, plan, code, commit", emoji: "🗺️", group: "Lesson", keywords: ["plan mode", "explore plan code commit", "Ctrl+G", "workflow"] },
        { id: "control", title: "Stop, undo and come back later", emoji: "⏪", group: "Beginner path", keywords: ["Esc", "/rewind", "checkpoints", "--continue", "--resume", "claude -p"] },
        { id: "commands", title: "The commands you will use most", emoji: "⌨️", group: "Beginner path", keywords: ["slash commands", "/init", "/memory", "/skills", "/hooks", "/mcp", "/plugin", "/doctor", "@ mention"] },
        { id: "folder", title: "The .claude folder: where everything lives", emoji: "📁", group: "Beginner path", keywords: [".claude folder", "project settings", "home folder", "file map", "rules.md", "agents.md"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-md", title: "CLAUDE.md and Memory: What Goes Where", emoji: "📘", page: "content/claude/claude-md.html",
        summary: "What CLAUDE.md is for and why it is guidance not enforcement, managed, user, project and local locations with the real load order, Anthropic's include and exclude table, three ready to copy CLAUDE.md files, personal files, @ imports run through a model of the loader, AGENTS.md rules, auto memory with MEMORY.md and memory types, and a workflow with /init, /context and /doctor prompt-audit.",
        keywords: ["CLAUDE.md", "CLAUDE.local.md", "~/.claude/CLAUDE.md", "memory", "auto memory", "MEMORY.md", "@ import", "AGENTS.md", "/init", "/memory", "load order", "what to include"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "What CLAUDE.md is for", emoji: "📘", group: "Beginner path", keywords: ["CLAUDE.md", "project instructions", "memory", "persistent context"] },
        { id: "where", title: "Where CLAUDE.md files live", emoji: "📍", group: "Beginner path", keywords: ["locations", "load order", "managed policy", "user CLAUDE.md", "CLAUDE.local.md", "subdirectory"] },
        { id: "put", title: "What to put in, and what to leave out", emoji: "📥", group: "Beginner path", keywords: ["what to include", "what to exclude", "200 lines", "IMPORTANT", "best practices"] },
        { id: "examples", title: "Three real CLAUDE.md files", emoji: "🧾", group: "Beginner path", keywords: ["CLAUDE.md example", "web app", "data team", "writer", "template"] },
        { id: "personal", title: "Your personal files: ~/.claude/CLAUDE.md and CLAUDE.local.md", emoji: "🙋", group: "Beginner path", keywords: ["user CLAUDE.md", "CLAUDE.local.md", "personal preferences", "gitignore"] },
        { id: "imports", title: "Split a long file with @ imports", emoji: "🔗", group: "Lesson", keywords: ["@ imports", "import", "four hops", "HTML comments", "backticks"] },
        { id: "agentsmd", title: "AGENTS.md and other tools", emoji: "🤝", group: "Lesson", keywords: ["AGENTS.md", "other tools", "project instructions setting"] },
        { id: "auto", title: "Auto memory: notes Claude writes for itself", emoji: "🧠", group: "Beginner path", keywords: ["auto memory", "MEMORY.md", "autoMemoryEnabled", "memory types"] },
        { id: "workflow", title: "Create, check and improve it", emoji: "🔁", group: "Beginner path", keywords: ["/init", "/memory", "/context", "/doctor prompt-audit", "maintain"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-rules", title: "Rules: The .claude/rules Folder and Path Rules", emoji: "📏", page: "content/claude/claude-rules.html",
        summary: "The name check (no rules.md, the real .claude/rules/ folder), creating rule files step by step, path rules with the paths field and glob patterns, a table of which rules load for which file, ready to copy rules for APIs, tests, blog posts and contracts, a screenshot guide, QA rules for test design, API tests, UI tests and bug reports, developer rules for Python, migrations and pull requests, personal rules in ~/.claude/rules/, sharing rules with symlinks, choosing between rules, CLAUDE.md, skills and hooks, and debugging rules.",
        keywords: ["rules", "rules.md", ".claude/rules", "paths", "path rules", "glob", "frontmatter", "user rules", "symlink", "CLAUDE.md vs rules", "QA rules", "developer rules", "test rules"],
        added: "2026-10-20",
        sections: [
        { id: "name", title: "First, the name: there is no rules.md", emoji: "🔎", group: "Beginner path", keywords: ["rules.md", "name check", ".claude/rules", "cursorrules"] },
        { id: "setup", title: "Create your first rules, step by step", emoji: "🧱", group: "Beginner path", keywords: ["create rules", "one topic per file", "subfolders", "setup"] },
        { id: "paths", title: "Path rules: load only for matching files", emoji: "🎯", group: "Lesson", keywords: ["paths", "frontmatter", "glob", "path-specific rules", "brace expansion"] },
        { id: "examples", title: "Ready to copy rule files", emoji: "🧾", group: "Beginner path", keywords: ["rule examples", "testing rules", "content rules", "legal rules"] },
        { id: "setup-shots", title: "Set up QA and developer rules, with screenshots", emoji: "📸", group: "Beginner path", keywords: ["setup rules", "screenshots", "step by step", "/context"] },
        { id: "qa-rules", title: "Rule files for a QA engineer", emoji: "🧪", group: "Beginner path", keywords: ["QA rules", "test rules", "API test rules", "UI test rules", "Playwright", "bug report rules", "tester"] },
        { id: "dev-rules", title: "Rule files for a developer", emoji: "👩‍💻", group: "Lesson", keywords: ["developer rules", "python rules", "migration rules", "pull request rules", "Alembic"] },
        { id: "user", title: "Personal rules in ~/.claude/rules/", emoji: "🙋", group: "Beginner path", keywords: ["user rules", "personal rules", "home folder"] },
        { id: "share", title: "Share one set of rules across many projects", emoji: "🔗", group: "Lesson", keywords: ["symlink", "shared rules", "company standards"] },
        { id: "choose", title: "Rules, CLAUDE.md, skills or hooks?", emoji: "⚖️", group: "Beginner path", keywords: ["rules vs CLAUDE.md", "rules vs skills", "compaction", "when to use"] },
        { id: "debug", title: "When a rule does not seem to work", emoji: "🩺", group: "Lesson", keywords: ["debug rules", "/context", "claude --debug", "troubleshooting"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-skills", title: "Skills: Build SKILL.md Step by Step", emoji: "🧰", page: "content/claude/claude-skills.html",
        summary: "What a skill is and its three loading levels, a first skill in three steps, personal, project and plugin locations and command names, every front matter field with good and weak descriptions, arguments and dynamic context with what Claude receives, supporting files and a Python script checking a real invoice, invocation control, daily work skills, QA skills for test cases, bug reports and picking regression tests with a real Python script, developer skills to fix issues, review a branch and write release notes, a screenshot guide for Claude Code and for claude.ai uploads, the claude.ai upload rules, and tips for reliable skills.",
        keywords: ["skills", "SKILL.md", "Skills.md", "frontmatter", "description", "$ARGUMENTS", "dynamic context", "allowed-tools", "disable-model-invocation", "user-invocable", "context fork", "claude.ai upload", "Agent Skills", "progressive disclosure", "QA skills", "developer skills", "test cases", "bug report", "regression", "screenshots"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "What a skill is", emoji: "🧰", group: "Beginner path", keywords: ["skill", "SKILL.md", "progressive disclosure", "levels"] },
        { id: "first", title: "Build your first skill in three steps", emoji: "🚀", group: "Beginner path", keywords: ["first skill", "create skill", "step by step", "summarize-changes"] },
        { id: "setup-shots", title: "Set up a skill in Claude Code, with screenshots", emoji: "📸", group: "Beginner path", keywords: ["setup skill", "screenshots", "step by step", "install skill", "/skills"] },
        { id: "where", title: "Where skills live and how they get their name", emoji: "📍", group: "Beginner path", keywords: ["skill locations", "personal skills", "project skills", "command name", "skills.md", ".claude/commands"] },
        { id: "front", title: "The front matter: what goes at the top", emoji: "🏷️", group: "Lesson", keywords: ["frontmatter", "description", "disable-model-invocation", "user-invocable", "allowed-tools", "context fork", "when_to_use"] },
        { id: "args", title: "Arguments and live data", emoji: "🔣", group: "Lesson", keywords: ["$ARGUMENTS", "$0", "arguments", "dynamic context", "!command", "CLAUDE_SKILL_DIR"] },
        { id: "files", title: "Supporting files and scripts", emoji: "📎", group: "Lesson", keywords: ["supporting files", "scripts", "reference files", "500 lines", "invoice"] },
        { id: "who", title: "Who can start a skill", emoji: "🎛️", group: "Lesson", keywords: ["disable-model-invocation", "user-invocable", "context fork", "agent", "side effects"] },
        { id: "daily", title: "Skills for daily work", emoji: "📅", group: "Beginner path", keywords: ["daily automation", "meeting notes", "commit message", "skill examples"] },
        { id: "qa-skills", title: "Skills for a QA engineer's day", emoji: "🧪", group: "Beginner path", keywords: ["QA skills", "test cases", "bug report", "regression", "tester", "boundary values", "daily QA"] },
        { id: "dev-skills", title: "Skills for a developer's day", emoji: "👩‍💻", group: "Lesson", keywords: ["developer skills", "fix issue", "PR review", "release notes", "daily developer", "code review"] },
        { id: "upload", title: "Skills in claude.ai and the API", emoji: "☁️", group: "Lesson", keywords: ["claude.ai upload", "Skills API", "Agent Skills spec", "zip", "name rules"] },
        { id: "tips", title: "Make skills that work every time", emoji: "💡", group: "Beginner path", keywords: ["skill tips", "testing skills", "/skills", "skill-creator", "troubleshooting"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-settings-hooks", title: "settings.json, Permissions and Hooks", emoji: "🪝", page: "content/claude/claude-settings-hooks.html",
        summary: "Settings files and precedence, permission rules with a run of deny, ask and allow matching, ready to copy team, personal and local settings, hook events and how hooks talk through stdin and exit codes, four hooks run for real (block dangerous commands, protect files with a JSON answer, add a release freeze notice, log every edit), the official format and notification hooks, and debugging with /hooks, /permissions and /status.",
        keywords: ["settings.json", "settings.local.json", "permissions", "allow", "deny", "ask", "hooks", "PreToolUse", "PostToolUse", "UserPromptSubmit", "Notification", "exit code 2", "/hooks", "defaultMode"],
        added: "2026-10-20",
        sections: [
        { id: "files", title: "The settings files and which one wins", emoji: "⚙️", group: "Beginner path", keywords: ["settings.json", "settings precedence", "managed settings", "settings.local.json", "$schema"] },
        { id: "perms", title: "Permission rules: allow, ask and deny", emoji: "🚦", group: "Beginner path", keywords: ["permissions", "allow", "ask", "deny", "rule syntax", "Bash()", "Read()", "WebFetch domain"] },
        { id: "copy", title: "Ready to copy settings files", emoji: "📄", group: "Beginner path", keywords: ["settings example", "env", "model", "defaultMode", "workspace trust"] },
        { id: "hooks", title: "Hooks: code that runs on events", emoji: "🪝", group: "Beginner path", keywords: ["hooks", "events", "PreToolUse", "PostToolUse", "UserPromptSubmit", "Notification", "exit code 2", "stdin JSON"] },
        { id: "block", title: "Hook 1: block dangerous commands", emoji: "⛔", group: "Beginner path", keywords: ["PreToolUse", "block command", "exit 2", "rm -rf", "force push"] },
        { id: "protect", title: "Hook 2: protect secret files, with a JSON answer", emoji: "🔒", group: "Lesson", keywords: ["protect files", "permissionDecision", "deny", "JSON output", ".env"] },
        { id: "context", title: "Hook 3: add live facts to prompts", emoji: "📣", group: "Lesson", keywords: ["UserPromptSubmit", "additionalContext", "release freeze", "inject context"] },
        { id: "after", title: "Hook 4: after every edit, log, format or notify", emoji: "🧹", group: "Lesson", keywords: ["PostToolUse", "audit log", "ruff format", "Notification hook", "osascript"] },
        { id: "check", title: "Check and debug", emoji: "🩺", group: "Lesson", keywords: ["/hooks", "/permissions", "/status", "debug hooks", "claude --debug"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-subagents", title: "Subagents and Output Styles", emoji: "🤖", page: "content/claude/claude-subagents.html",
        summary: "What subagents are and how much context they save, built-in agents, creating an agent file step by step and the agents.md name check, every frontmatter field with a broken agent file and its four mistakes, ready to copy test-runner and doc-researcher agents, three ways to call an agent and --agent sessions, agent memory, and built-in and custom output styles.",
        keywords: ["subagents", ".claude/agents", "agents.md", "agent file", "Explore", "Plan", "tools", "model", "maxTurns", "memory", "@-mention", "--agent", "output styles", "keep-coding-instructions"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "What a subagent is", emoji: "🤖", group: "Beginner path", keywords: ["subagent", "delegation", "own context window", "summary"] },
        { id: "builtin", title: "Built-in subagents you already have", emoji: "🧩", group: "Beginner path", keywords: ["Explore", "Plan", "general-purpose", "built-in agents"] },
        { id: "create", title: "Create your first subagent, step by step", emoji: "🛠️", group: "Beginner path", keywords: ["create subagent", "agent file", "system prompt", "agents.md"] },
        { id: "fields", title: "Every field in an agent file", emoji: "🏷️", group: "Lesson", keywords: ["frontmatter", "tools", "model", "permissionMode", "maxTurns", "skills", "mcpServers", "memory", "isolation worktree"] },
        { id: "gallery", title: "Ready to copy agents", emoji: "🗂️", group: "Beginner path", keywords: ["test runner agent", "research agent", "agent examples"] },
        { id: "use", title: "Calling a subagent", emoji: "📣", group: "Beginner path", keywords: ["invoke subagent", "@-mention", "--agent", "parallel subagents"] },
        { id: "memory", title: "Agents that remember", emoji: "🧠", group: "Lesson", keywords: ["agent memory", "persistent memory", "memory field"] },
        { id: "styles", title: "Output styles: change how Claude talks for a whole session", emoji: "🎨", group: "Beginner path", keywords: ["output styles", "Concise", "Explanatory", "Learning", "Proactive", "keep-coding-instructions", "/output-style"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-mcp", title: "MCP: Connect and Build Servers", emoji: "🔌", page: "content/claude/claude-mcp.html",
        summary: "What MCP servers offer, connecting a first server, managing servers, local, project and user scopes with a full .mcp.json, a Python expenses server built and tested with a real client, the JSON-RPC handshake on the wire, tool names and permission rules, output limits and tool search, claude_desktop_config.json, a screenshot guide with real claude mcp output, and custom connectors in claude.ai.",
        keywords: ["MCP", "Model Context Protocol", "claude mcp add", ".mcp.json", "scopes", "MCPServer", "@mcp.tool", "Python MCP", "JSON-RPC", "mcp__", "Claude Desktop", "claude_desktop_config.json", "connectors", "custom connector", "screenshots"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "What MCP is", emoji: "🔌", group: "Beginner path", keywords: ["MCP", "Model Context Protocol", "server", "client", "tools", "resources", "prompts"] },
        { id: "connect", title: "Connect a server, step by step", emoji: "🧷", group: "Beginner path", keywords: ["claude mcp add", "--transport http", "stdio", "claude mcp list", "/mcp"] },
        { id: "setup-shots", title: "Set up MCP in Claude Code, with screenshots", emoji: "📸", group: "Beginner path", keywords: ["setup MCP", "screenshots", "claude mcp list", "claude mcp get", "pending approval", "step by step"] },
        { id: "scopes", title: "Scopes and the .mcp.json file", emoji: "📍", group: "Lesson", keywords: ["scope", "local", "project", "user", ".mcp.json", "environment variables", "${VAR}"] },
        { id: "build", title: "Build your own server in Python", emoji: "🐍", group: "Beginner path", keywords: ["build MCP server", "Python MCP server", "MCPServer", "@mcp.tool", "@mcp.resource", "pip install mcp"] },
        { id: "wire", title: "What travels between Claude and a server", emoji: "📨", group: "Lesson", keywords: ["JSON-RPC", "initialize", "tools/list", "tools/call", "protocol"] },
        { id: "use", title: "Using MCP inside Claude Code", emoji: "🎛️", group: "Beginner path", keywords: ["mcp__server__tool", "permissions", "resources @", "MCP prompts", "MAX_MCP_OUTPUT_TOKENS", "tool search"] },
        { id: "desktop", title: "The same servers in Claude Desktop", emoji: "🖥️", group: "Lesson", keywords: ["Claude Desktop", "claude_desktop_config.json", "add-from-claude-desktop", "claude mcp serve"] },
        { id: "connectors", title: "MCP in claude.ai: connectors, with screenshots", emoji: "🧩", group: "Beginner path", keywords: ["connectors", "custom connector", "claude.ai MCP", "remote MCP", "tool access", "Connectors Directory"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-automation", title: "Daily Automation: Plugins, Scripts and GitHub", emoji: "⚙️", page: "content/claude/claude-automation.html",
        summary: "A full plugin layout with its skill and hooks files and three common mistakes, plugin commands and marketplaces, claude -p flags, --bare, structured JSON output used by a real script, GitHub Actions set up for @claude and a weekday report, a table of cron lines, /loop, and five daily recipes.",
        keywords: ["automation", "plugin", "plugin.json", "claude -p", "headless", "--json-schema", "structured_output", "GitHub Actions", "claude-code-action", "cron", "schedule", "/loop", "recipes"],
        added: "2026-10-20",
        sections: [
        { id: "plugins", title: "Plugins: share your whole setup in one folder", emoji: "📦", group: "Beginner path", keywords: ["plugin", "plugin.json", "manifest", "marketplace", "--plugin-dir", "claude plugin validate"] },
        { id: "headless", title: "claude -p: use Claude in scripts", emoji: "🧾", group: "Beginner path", keywords: ["claude -p", "headless", "--allowedTools", "--bare", "--continue", "scripts"] },
        { id: "json", title: "Get data back, not just text", emoji: "🧮", group: "Lesson", keywords: ["--output-format json", "--json-schema", "structured_output", "total_cost_usd", "jq"] },
        { id: "gha", title: "Claude in GitHub Actions", emoji: "🐙", group: "Beginner path", keywords: ["GitHub Actions", "claude-code-action", "@claude", "/install-github-app", "secrets"] },
        { id: "schedule", title: "Run it on a schedule", emoji: "⏰", group: "Lesson", keywords: ["schedule", "cron", "UTC", "claude_args", "--max-turns", "/loop"] },
        { id: "recipes", title: "Daily automation recipes", emoji: "🍳", group: "Beginner path", keywords: ["automation recipes", "commit message", "meeting notes", "CSV cleaning", "CI failure"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "claude-build-api", title: "Building with the API", emoji: "🔌", blurb: "Call Claude from your own code: the Messages API, tools, agent loops and the Agent SDK.", topics: [
      { id: "claude-api", title: "The Claude API Step by Step", emoji: "🧩", page: "content/claude/claude-api.html",
        summary: "API keys and SDK install, a first call with every response field explained, a tutor with a system prompt and history, models and prices with a worked cost table, streaming, json_schema outputs, effort and cache_control, and error codes with retries.",
        keywords: ["Claude API", "Messages API", "anthropic", "messages.create", "system prompt", "streaming", "structured outputs", "pricing", "prompt caching", "effort", "errors"],
        added: "2026-10-20",
        sections: [
        { id: "setup", title: "Get a key and install the SDK", emoji: "🔑", group: "Beginner path", keywords: ["API key", "ANTHROPIC_API_KEY", "pip install anthropic", "Claude Console"] },
        { id: "first", title: "Your first call, line by line", emoji: "👋", group: "Beginner path", keywords: ["messages.create", "model", "max_tokens", "messages", "stop_reason", "usage"] },
        { id: "system", title: "System prompts and conversations", emoji: "🧑‍🏫", group: "Beginner path", keywords: ["system prompt", "conversation history", "stateless", "multi-turn"] },
        { id: "models", title: "Choose a model and know the cost", emoji: "⚖️", group: "Beginner path", keywords: ["models", "pricing", "Haiku", "Sonnet", "Opus", "Fable", "tokens", "cost"] },
        { id: "stream", title: "Streaming: show words as they arrive", emoji: "🌊", group: "Lesson", keywords: ["streaming", "messages.stream", "text_stream", "get_final_message"] },
        { id: "json", title: "Get JSON your code can trust", emoji: "🧾", group: "Lesson", keywords: ["structured outputs", "json_schema", "output_config", "JSON"] },
        { id: "cache", title: "Effort and prompt caching", emoji: "💾", group: "Lesson", keywords: ["effort", "prompt caching", "cache_control", "ephemeral", "cache_read_input_tokens"] },
        { id: "errors", title: "When things go wrong", emoji: "🧯", group: "Lesson", keywords: ["errors", "429", "retries", "max_tokens", "refusal"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "claude-agents", title: "Build Your Own Agents", emoji: "🤖", page: "content/claude/claude-agents.html",
        summary: "The agent loop explained, writing tool definitions, a two round stock agent built by hand and run step by step, the tool runner version with a spending gate that refuses a big order, the Claude Agent SDK with built-in tools, and a table for choosing the right approach.",
        keywords: ["agents", "agent loop", "tools", "tool_use", "tool_result", "tool runner", "@beta_tool", "Claude Agent SDK", "claude-agent-sdk", "safety gate", "Managed Agents"],
        added: "2026-10-20",
        sections: [
        { id: "what", title: "What an agent really is", emoji: "🔁", group: "Beginner path", keywords: ["agent", "agent loop", "tool_use", "tool_result", "stop_reason"] },
        { id: "tools", title: "Define tools Claude can use", emoji: "🧰", group: "Beginner path", keywords: ["tool definition", "input_schema", "tool description", "JSON schema"] },
        { id: "manual", title: "Build the loop by hand, step by step", emoji: "✍️", group: "Beginner path", keywords: ["manual agent loop", "tool_use_id", "messages", "max steps"] },
        { id: "runner", title: "Less code with the tool runner", emoji: "🏃", group: "Lesson", keywords: ["tool runner", "@beta_tool", "tool_runner", "safety gate", "human approval"] },
        { id: "sdk", title: "The Claude Agent SDK: Claude Code as a library", emoji: "🧠", group: "Beginner path", keywords: ["Claude Agent SDK", "claude-agent-sdk", "query", "ClaudeAgentOptions", "allowed_tools"] },
        { id: "choose", title: "Which way to build your agent", emoji: "🧭", group: "Beginner path", keywords: ["choose agent approach", "Managed Agents", "workflow vs agent", "start simple"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "claude-capstone", title: "Capstone", emoji: "🏁", blurb: "Put it all together: the full file map and a complete setup built step by step.", topics: [
      { id: "claude-file-map", title: "Capstone: Which File Holds What", emoji: "🗺️", page: "content/claude/claude-file-map.html",
        summary: "The complete Claude file map with what goes in and stays out of each file, the real names behind common wrong ones, a decision table for eleven example instructions, a full project setup with two problems to fix, a homework helper with CLAUDE.md, a quiz skill and a claude.ai Project version, and a six week practice path.",
        keywords: ["file map", "CLAUDE.md", "rules", "SKILL.md", "agents", "settings.json", ".mcp.json", "what goes where", "homework helper", "capstone"],
        added: "2026-10-20",
        sections: [
        { id: "map", title: "Every file, and what goes in it", emoji: "🗺️", group: "Beginner path", keywords: ["file map", "which file", "what goes where"] },
        { id: "names", title: "The real names behind the names people use", emoji: "🔎", group: "Beginner path", keywords: ["rules.md", "skills.md", "agents.md", "prompt file", "name check"] },
        { id: "decide", title: "Decide where an instruction belongs", emoji: "🧭", group: "Beginner path", keywords: ["decision guide", "hook or CLAUDE.md", "skill or rule"] },
        { id: "setup", title: "A complete project, reviewed", emoji: "🏗️", group: "Lesson", keywords: ["project setup", "full example", "review"] },
        { id: "kid", title: "Build a homework helper, step by step", emoji: "🧒", group: "Beginner path", keywords: ["homework helper", "kids", "claude.ai Projects", "beginner build"] },
        { id: "next", title: "Your next level, one week at a time", emoji: "🚀", group: "Beginner path", keywords: ["learning path", "next steps", "practice plan"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "claude-cert", title: "Certification prep", emoji: "🎓", blurb: "Claude 101 from Anthropic Academy lesson by lesson, and how to prepare for the Claude Certified Associate exam.", topics: [
      { id: "claude-101", title: "Claude 101 and Certification Prep", emoji: "🎓", page: "content/claude/claude-101.html",
        summary: "The official Claude 101 outline and how to earn its certificate, what Claude is and how to get better results, Chat, Cowork and Code, projects with RAG, artifacts and skills, memory and incognito, connectors, enterprise search and Research, use cases by role, other ways to use Claude, the Claude Certified Associate exam facts and its seven domains, worked exam scenarios, a seven day study plan and a cheat sheet.",
        keywords: ["Claude 101", "Anthropic Academy", "certificate", "certification", "Claude Certified Associate", "CCAO-F", "exam", "Skilljar", "projects", "artifacts", "connectors", "Research", "Cowork", "study plan"],
        added: "2026-10-22",
        sections: [
        { id: "about", title: "What Claude 101 is and how you earn the certificate", emoji: "🎓", group: "Beginner path", keywords: ["Claude 101", "Anthropic Academy", "Skilljar", "certificate of completion", "course outline", "free course"] },
        { id: "meet", title: "Module 1: Meet Claude and get better results", emoji: "👋", group: "Beginner path", keywords: ["what is Claude", "large language model", "knowledge cutoff", "first conversation", "better results", "specific prompts", "feedback"] },
        { id: "desktop", title: "Module 1: Chat, Cowork and Code on your desktop", emoji: "🖥️", group: "Beginner path", keywords: ["Claude Desktop", "Chat", "Cowork", "Code", "permission modes", "usage limits"] },
        { id: "organise", title: "Module 2: Projects, artifacts and skills", emoji: "🗂️", group: "Beginner path", keywords: ["projects", "project knowledge", "RAG", "artifacts", "skills", "share project", "Can view", "Can edit"] },
        { id: "memory", title: "Memory, past chats and incognito", emoji: "🧠", group: "Beginner path", keywords: ["memory", "chat search", "incognito", "project memory", "privacy"] },
        { id: "reach", title: "Module 3: Connectors, enterprise search and Research", emoji: "🔌", group: "Beginner path", keywords: ["connectors", "enterprise search", "Ask your org", "Research", "web search", "permissions", "MCP"] },
        { id: "roles", title: "Module 4: Claude in action, role by role", emoji: "🧑‍💼", group: "Beginner path", keywords: ["use cases by role", "marketing", "sales", "HR", "finance", "engineering", "operations"] },
        { id: "other", title: "Module 4: Other ways to work with Claude", emoji: "🧭", group: "Beginner path", keywords: ["claude.ai", "Claude Desktop", "mobile", "Claude Code", "API", "billing", "which feature"] },
        { id: "exam", title: "The Claude Certified Associate exam (CCAO-F)", emoji: "📝", group: "Lesson", keywords: ["Claude Certified Associate", "CCAO-F", "exam", "Pearson VUE", "domains", "pass mark", "720"] },
        { id: "domains", title: "What each exam domain tests, with one tip each", emoji: "🎯", group: "Lesson", keywords: ["exam domains", "output evaluation", "hallucination", "governance", "model selection", "Haiku", "Sonnet", "Opus"] },
        { id: "scenarios", title: "Exam style scenarios, worked through", emoji: "🧩", group: "Beginner path", keywords: ["exam scenarios", "fact checking", "model choice", "personal data", "responsible use"] },
        { id: "plan", title: "A seven day study plan", emoji: "📅", group: "Beginner path", keywords: ["study plan", "seven days", "exam preparation", "practice"] },
        { id: "cheat", title: "Cheat sheet: numbers and menu paths", emoji: "📌", group: "Beginner path", keywords: ["cheat sheet", "numbers to remember", "menu paths", "revision"] },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Number crunch', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] }
  ];
}
/* ===== end of claude-build ===== */

/* ===== mlmath-build: Maths for Machine Learning chapters. Generated by tools/mlmath-build/build.py, edit the topic files instead. ===== */
function mlMathModules() {
  return [
    { id: "foundations", title: "School foundations", emoji: "🌱", blurb: "The school maths every model is written in: numbers, algebra, functions, exponents and logarithms.", topics: [
      { id: "numbers-algebra", title: "Numbers, Algebra and Equations", emoji: "🌱", page: "content/ml-maths/numbers-algebra.html",
        summary: "Number families and floating point, BODMAS, fractions and percentages, linear and simultaneous equations, exponent rules and scientific notation, sigma and pi notation, absolute value and the mean absolute error.",
        keywords: ["numbers", "algebra", "BODMAS", "percentage", "linear equation", "simultaneous equations", "exponents", "scientific notation", "sigma notation", "summation", "absolute value", "MAE", "floating point"],
        added: "2026-10-22",
        sections: [
        { id: "why", title: "Why machine learning needs maths", emoji: "🗺️", group: "Lesson", keywords: ["why maths", "roadmap", "model", "parameters", "weights"] },
        { id: "numbers", title: "Kinds of numbers and how computers store them", emoji: "🔢", group: "Lesson", keywords: ["natural numbers", "integers", "rational", "irrational", "real numbers", "floating point", "0.1 + 0.2"] },
        { id: "order", title: "Order of operations, fractions and percentages", emoji: "➗", group: "Lesson", keywords: ["BODMAS", "PEMDAS", "order of operations", "fractions", "percentage", "percentage change", "accuracy"] },
        { id: "algebra", title: "Variables, expressions and equations", emoji: "⚖️", group: "Lesson", keywords: ["variable", "expression", "equation", "solve for x", "linear equation", "simultaneous equations", "elimination", "cramer rule"] },
        { id: "powers", title: "Powers, roots and scientific notation", emoji: "⚡", group: "Lesson", keywords: ["exponent", "power", "root", "square root", "scientific notation", "exponent rules", "1e-3", "learning rate"] },
        { id: "sigma", title: "Sigma and Pi notation: the maths shorthand", emoji: "Σ", group: "Lesson", keywords: ["sigma notation", "summation", "sum", "mean", "average", "pi notation", "product", "gauss"] },
        { id: "abs", title: "Absolute value, inequalities and distance", emoji: "📏", group: "Lesson", keywords: ["absolute value", "modulus", "distance", "inequality", "interval", "mean absolute error", "MAE"] },
        { id: "solve-linear", title: "Solve any a·x + b = c", emoji: "🏋️", group: "Easy practice" },
        { id: "compound", title: "Growth by a percentage every year", emoji: "🏋️", group: "Medium practice" },
        { id: "spread", title: "Average squared distance from the mean", emoji: "🏋️", group: "Hard practice" },
        { id: "babylon", title: "Square roots by repeated averaging", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "functions-logs", title: "Functions, Graphs, Exponents and Logarithms", emoji: "📈", page: "content/ml-maths/functions-logs.html",
        summary: "Domain and range, slope and intercept, the quadratic formula and the vertex, exponential growth and e, log rules and why ML adds log probabilities, sigmoid, tanh and ReLU, composition, shifts and inverse functions such as logit.",
        keywords: ["function", "graph", "slope", "intercept", "quadratic", "parabola", "exponential", "euler number", "logarithm", "ln", "sigmoid", "tanh", "ReLU", "logit", "inverse function", "composition"],
        added: "2026-10-22",
        sections: [
        { id: "functions", title: "What a function is", emoji: "⚙️", group: "Lesson", keywords: ["function", "f(x)", "domain", "range", "graph", "vertical line test"] },
        { id: "lines", title: "Straight lines: slope and intercept", emoji: "📈", group: "Lesson", keywords: ["straight line", "slope", "intercept", "y = mx + b", "gradient of a line", "weights", "bias", "linear regression"] },
        { id: "quadratic", title: "Quadratics and polynomials", emoji: "🪣", group: "Lesson", keywords: ["quadratic", "parabola", "vertex", "roots", "quadratic formula", "discriminant", "polynomial", "overfitting"] },
        { id: "exponential", title: "Exponential growth and the number e", emoji: "🚀", group: "Lesson", keywords: ["exponential", "exponential growth", "decay", "euler number", "e", "compound interest", "half life"] },
        { id: "logs", title: "Logarithms: the undo button for powers", emoji: "🪵", group: "Lesson", keywords: ["logarithm", "log", "ln", "natural log", "log rules", "change of base", "log loss", "underflow", "decibel"] },
        { id: "activation", title: "The S curve and other functions machine learning uses", emoji: "〰️", group: "Lesson", keywords: ["sigmoid", "tanh", "ReLU", "activation function", "softmax", "S curve", "logistic function"] },
        { id: "compose", title: "Composing, shifting and inverting functions", emoji: "🔗", group: "Lesson", keywords: ["composition", "inverse function", "logit", "odds", "shift", "stretch", "f(g(x))"] },
        { id: "line-two-points", title: "The line through two points", emoji: "🏋️", group: "Easy practice" },
        { id: "half-life", title: "When does the medicine drop below 50 mg", emoji: "🏋️", group: "Medium practice" },
        { id: "log-likelihood", title: "Products of probabilities as sums of logs", emoji: "🏋️", group: "Hard practice" },
        { id: "invert-sigmoid", title: "Invert the sigmoid by bisection", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "linear-algebra", title: "Linear algebra", emoji: "🧮", blurb: "Vectors, matrices, eigenvalues, SVD and PCA: the maths that lets a model handle thousands of numbers at once.", topics: [
      { id: "vectors", title: "Vectors", emoji: "➡️", page: "content/ml-maths/vectors.html",
        summary: "Feature vectors and embeddings, adding and scaling, L1, L2 and L infinity norms, unit vectors and distances, the dot product and the angle between vectors, cosine similarity for recommendations and search, projections, span, independence and basis.",
        keywords: ["vector", "feature vector", "embedding", "norm", "L1 norm", "L2 norm", "unit vector", "euclidean distance", "dot product", "cosine similarity", "projection", "span", "linear independence", "basis", "k nearest neighbours"],
        added: "2026-10-22",
        sections: [
        { id: "what", title: "What a vector is", emoji: "➡️", group: "Lesson", keywords: ["vector", "component", "feature vector", "dimension", "embedding", "R^n"] },
        { id: "ops", title: "Adding, subtracting and scaling vectors", emoji: "➕", group: "Lesson", keywords: ["vector addition", "scalar multiplication", "linear combination", "tip to tail", "resultant"] },
        { id: "norm", title: "Length (norm) and distance", emoji: "📏", group: "Lesson", keywords: ["norm", "length", "magnitude", "euclidean distance", "manhattan distance", "L1", "L2", "unit vector", "normalise", "feature scaling"] },
        { id: "dot", title: "The dot product", emoji: "✖️", group: "Lesson", keywords: ["dot product", "inner product", "angle between vectors", "orthogonal", "perpendicular", "cos theta", "attention"] },
        { id: "cosine", title: "Cosine similarity: how alike are two things", emoji: "🎬", group: "Lesson", keywords: ["cosine similarity", "similarity", "recommendation", "semantic search", "embedding", "RAG"] },
        { id: "proj", title: "Projection: the shadow of a vector", emoji: "🔦", group: "Lesson", keywords: ["projection", "vector projection", "scalar projection", "shadow", "orthogonal decomposition"] },
        { id: "span", title: "Span, independence and basis", emoji: "🧱", group: "Lesson", keywords: ["span", "linear independence", "linearly dependent", "basis", "dimension", "orthonormal basis", "multicollinearity"] },
        { id: "nearest-shop", title: "Which shop is nearest", emoji: "🏋️", group: "Easy practice" },
        { id: "rank-docs", title: "Rank documents for a search", emoji: "🏋️", group: "Medium practice" },
        { id: "gram-schmidt", title: "Make two vectors perpendicular", emoji: "🏋️", group: "Hard practice" },
        { id: "knn", title: "A k nearest neighbours classifier", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "matrices", title: "Matrices and Matrix Multiplication", emoji: "🔢", page: "content/ml-maths/matrices.html",
        summary: "Shapes and data matrices, addition, transpose and the element wise product, matrix multiplication with the shape rule, transformations and the Wx + b layer, identity, determinant and inverse, Gaussian elimination, rank, special matrices and the normal equations for regression.",
        keywords: ["matrix", "matrix multiplication", "transpose", "shape", "linear transformation", "rotation matrix", "determinant", "inverse", "identity matrix", "gaussian elimination", "Ax = b", "rank", "normal equations", "dense layer", "markov chain"],
        added: "2026-10-22",
        sections: [
        { id: "what", title: "What a matrix is", emoji: "🔢", group: "Lesson", keywords: ["matrix", "shape", "rows", "columns", "entry", "tensor", "dataset matrix"] },
        { id: "basic", title: "Adding, scaling and transposing", emoji: "🧩", group: "Lesson", keywords: ["matrix addition", "scalar multiplication", "transpose", "hadamard product", "element wise product"] },
        { id: "matmul", title: "Matrix multiplication, step by step", emoji: "🎯", group: "Lesson", keywords: ["matrix multiplication", "matmul", "row times column", "shape rule", "not commutative", "associative"] },
        { id: "transform", title: "A matrix is a transformation", emoji: "🔄", group: "Lesson", keywords: ["linear transformation", "rotation matrix", "scaling", "shear", "reflection", "dense layer", "Wx + b"] },
        { id: "inverse", title: "Identity, determinant and inverse", emoji: "↩️", group: "Lesson", keywords: ["identity matrix", "inverse matrix", "determinant", "singular matrix", "invertible", "2x2 inverse"] },
        { id: "systems", title: "Solving many equations at once", emoji: "🧮", group: "Lesson", keywords: ["system of linear equations", "Ax = b", "gaussian elimination", "back substitution", "augmented matrix", "normal equations"] },
        { id: "rank", title: "Rank and special matrices", emoji: "🏷️", group: "Lesson", keywords: ["rank", "diagonal matrix", "symmetric matrix", "orthogonal matrix", "triangular matrix", "sparse matrix", "low rank", "LoRA", "markov chain"] },
        { id: "shapes", title: "AB and BA have different shapes", emoji: "🏋️", group: "Easy practice" },
        { id: "rotate", title: "Rotate a square with a matrix", emoji: "🏋️", group: "Medium practice" },
        { id: "markov", title: "Population moves with a matrix power", emoji: "🏋️", group: "Hard practice" },
        { id: "normal-eq", title: "Fit a line with the normal equations", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "eigen-svd-pca", title: "Eigenvalues, SVD and PCA", emoji: "🧭", page: "content/ml-maths/eigen-svd-pca.html",
        summary: "Eigenvectors as directions a matrix keeps, the characteristic equation, the trace and determinant checks, diagonalisation and matrix powers, Markov steady states, power iteration and PageRank, SVD as rotate stretch rotate, low rank approximation, PCA step by step, explained variance and the condition number.",
        keywords: ["eigenvalue", "eigenvector", "characteristic equation", "trace", "diagonalisation", "power iteration", "pagerank", "svd", "singular value decomposition", "singular values", "low rank approximation", "pca", "principal component analysis", "covariance matrix", "explained variance", "condition number"],
        added: "2026-10-22",
        sections: [
        { id: "what", title: "Eigenvectors: the directions a matrix keeps", emoji: "🧭", group: "Lesson", keywords: ["eigenvector", "eigenvalue", "Av = λv", "lambda", "special direction"] },
        { id: "find", title: "Finding eigenvalues by hand", emoji: "🔎", group: "Lesson", keywords: ["characteristic equation", "det(A − λI) = 0", "trace", "find eigenvalues", "2x2 eigenvalues"] },
        { id: "props", title: "Rules that save time", emoji: "🧩", group: "Lesson", keywords: ["trace", "determinant", "diagonalisation", "eigendecomposition", "PDP⁻¹", "matrix power", "steady state", "symmetric matrix"] },
        { id: "power", title: "Power iteration and PageRank", emoji: "🔁", group: "Lesson", keywords: ["power iteration", "rayleigh quotient", "dominant eigenvalue", "pagerank", "convergence"] },
        { id: "svd", title: "Singular value decomposition (SVD)", emoji: "🧱", group: "Lesson", keywords: ["svd", "singular value decomposition", "singular values", "UΣVᵀ", "low rank approximation", "eckart young", "image compression", "pseudo inverse"] },
        { id: "pca", title: "Principal component analysis (PCA)", emoji: "🎯", group: "Lesson", keywords: ["pca", "principal component analysis", "covariance matrix", "explained variance", "dimensionality reduction", "standardise", "scree plot"] },
        { id: "ml", title: "Where machine learning uses all this", emoji: "🤖", group: "Lesson", keywords: ["condition number", "hessian eigenvalues", "spectral clustering", "low rank", "LoRA", "recommender", "matrix factorisation"] },
        { id: "check", title: "Is it an eigenvector?", emoji: "🏋️", group: "Easy practice" },
        { id: "steady", title: "The long run of a Markov chain", emoji: "🏋️", group: "Medium practice" },
        { id: "power3", title: "The top principal direction by power iteration", emoji: "🏋️", group: "Hard practice" },
        { id: "lowrank", title: "Compress a picture with one singular value", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "calculus", title: "Calculus", emoji: "📉", blurb: "Derivatives, gradients, the chain rule and optimisation: the maths that lets a model learn from its mistakes.", topics: [
      { id: "derivatives", title: "Derivatives and Integrals", emoji: "📈", page: "content/ml-maths/derivatives.html",
        summary: "Average and instant rate of change, limits and the difference quotient, numerical derivatives and gradient checking, the differentiation rules and table, the chain rule and the sigmoid derivative, critical points and the second derivative, convexity, Riemann sums, the fundamental theorem and how derivatives drive learning.",
        keywords: ["derivative", "slope", "tangent", "limit", "power rule", "product rule", "quotient rule", "chain rule", "sigmoid derivative", "second derivative", "maximum", "minimum", "convex", "integral", "riemann sum", "newton method"],
        added: "2026-10-22",
        sections: [
        { id: "rate", title: "Rate of change and slope", emoji: "🚗", group: "Lesson", keywords: ["derivative", "rate of change", "slope", "secant", "tangent", "average speed", "instant speed"] },
        { id: "limit", title: "Limits and the derivative from first principles", emoji: "🔬", group: "Lesson", keywords: ["limit", "first principles", "difference quotient", "central difference", "gradient checking", "numerical derivative"] },
        { id: "rules", title: "The rules of differentiation", emoji: "📏", group: "Lesson", keywords: ["power rule", "product rule", "quotient rule", "sum rule", "derivative of e^x", "derivative of ln x", "derivative table"] },
        { id: "chain", title: "The chain rule", emoji: "⛓️", group: "Lesson", keywords: ["chain rule", "composite function", "sigmoid derivative", "backpropagation", "vanishing gradient", "outside inside"] },
        { id: "shape", title: "Peaks, valleys and the second derivative", emoji: "⛰️", group: "Lesson", keywords: ["critical point", "maximum", "minimum", "second derivative", "concave", "convex", "inflection point", "optimisation"] },
        { id: "integral", title: "Integrals: adding up tiny pieces", emoji: "📐", group: "Lesson", keywords: ["integral", "area under curve", "riemann sum", "antiderivative", "fundamental theorem of calculus", "definite integral", "AUC"] },
        { id: "ml", title: "Why derivatives make machines learn", emoji: "🤖", group: "Lesson", keywords: ["loss", "gradient descent preview", "learning rate", "activation derivatives", "relu derivative", "automatic differentiation", "newton method"] },
        { id: "tangent", title: "The tangent line to a cubic", emoji: "🏋️", group: "Easy practice" },
        { id: "box", title: "The biggest open box", emoji: "🏋️", group: "Medium practice" },
        { id: "newton", title: "Square root of 2 with Newton's method", emoji: "🏋️", group: "Hard practice" },
        { id: "simpson", title: "Area under the bell curve", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "gradients", title: "Gradients and Backpropagation", emoji: "🧗", page: "content/ml-maths/gradients.html",
        summary: "Partial derivatives as slices, the gradient as the steepest uphill direction, contour lines, directional derivatives and tangent planes, Jacobian and Hessian matrices with the bowl, cap and saddle test, computational graphs, backpropagation through a neuron and a two layer net, and the vectorised MSE gradient.",
        keywords: ["partial derivative", "gradient", "nabla", "contour", "directional derivative", "tangent plane", "jacobian", "hessian", "saddle point", "computational graph", "chain rule", "backpropagation", "gradient check", "mse gradient", "autograd"],
        added: "2026-10-22",
        sections: [
        { id: "partial", title: "Partial derivatives: one knob at a time", emoji: "🎚️", group: "Lesson", keywords: ["partial derivative", "multivariable function", "hold constant", "∂f/∂x", "slice"] },
        { id: "gradient", title: "The gradient: the steepest way uphill", emoji: "🧗", group: "Lesson", keywords: ["gradient", "nabla", "∇f", "steepest ascent", "steepest descent", "contour lines", "level curves"] },
        { id: "approx", title: "Directional derivatives and linear approximation", emoji: "📐", group: "Lesson", keywords: ["directional derivative", "tangent plane", "linear approximation", "first order taylor", "dot product with gradient"] },
        { id: "jacobian", title: "Jacobian and Hessian matrices", emoji: "🧮", group: "Lesson", keywords: ["jacobian", "hessian", "second partial derivatives", "saddle point", "curvature", "second derivative test"] },
        { id: "chain", title: "The chain rule on a computational graph", emoji: "🔗", group: "Lesson", keywords: ["computational graph", "multivariable chain rule", "forward pass", "backward pass", "local gradient", "add node", "multiply node"] },
        { id: "backprop", title: "Backpropagation through a neuron", emoji: "🧠", group: "Lesson", keywords: ["backpropagation", "neuron gradient", "sigmoid neuron", "gradient check", "chain rule example", "weights and bias gradients"] },
        { id: "ml", title: "Gradients for whole datasets", emoji: "🤖", group: "Lesson", keywords: ["vectorised gradient", "mse gradient", "Xᵀ(Xw − y)", "mini batch", "stochastic gradient", "autograd"] },
        { id: "plane", title: "Guess a value with the tangent plane", emoji: "🏋️", group: "Easy practice" },
        { id: "hessian", title: "Bowl or saddle?", emoji: "🏋️", group: "Medium practice" },
        { id: "linreg-grad", title: "The gradient of mean squared error", emoji: "🏋️", group: "Hard practice" },
        { id: "twolayer", title: "Backprop through a two layer network", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "optimisation", title: "Gradient Descent and Optimisation", emoji: "⛷️", page: "content/ml-maths/optimisation.html",
        summary: "The gradient descent update, learning rates that crawl, converge, zig zag or diverge, SGD, mini batches and epochs, momentum, RMSProp and Adam with bias correction, convex and non convex landscapes, the condition number and feature scaling, Lagrange multipliers, warm up, cosine decay, clipping and early stopping.",
        keywords: ["gradient descent", "learning rate", "sgd", "mini batch", "epoch", "momentum", "rmsprop", "adam", "adamw", "convex", "saddle point", "condition number", "lagrange multiplier", "learning rate schedule", "gradient clipping", "early stopping"],
        added: "2026-10-22",
        sections: [
        { id: "idea", title: "Gradient descent: walk downhill", emoji: "⛷️", group: "Lesson", keywords: ["gradient descent", "update rule", "learning rate", "eta", "minimise loss", "downhill"] },
        { id: "lr", title: "The learning rate: not too small, not too big", emoji: "🎛️", group: "Lesson", keywords: ["learning rate", "step size", "divergence", "oscillation", "convergence", "stability", "too large learning rate"] },
        { id: "sgd", title: "Stochastic and mini batch gradient descent", emoji: "🎲", group: "Lesson", keywords: ["stochastic gradient descent", "sgd", "mini batch", "batch size", "epoch", "shuffle", "noise"] },
        { id: "adam", title: "Momentum, RMSProp and Adam", emoji: "🚀", group: "Lesson", keywords: ["momentum", "rmsprop", "adam", "adamw", "adaptive learning rate", "narrow valley", "zig zag", "bias correction"] },
        { id: "landscape", title: "Convexity, local minima and saddles", emoji: "🗺️", group: "Lesson", keywords: ["convex", "non convex", "local minimum", "global minimum", "saddle point", "plateau", "condition number", "feature scaling", "initialisation"] },
        { id: "lagrange", title: "Optimising with constraints: Lagrange multipliers", emoji: "🔒", group: "Lesson", keywords: ["lagrange multiplier", "constrained optimisation", "constraint", "parallel gradients", "svm", "regularisation as constraint"] },
        { id: "practice", title: "Training tricks: schedules, clipping and stopping", emoji: "🛠️", group: "Lesson", keywords: ["learning rate schedule", "warm up", "cosine decay", "gradient clipping", "early stopping", "weight decay", "NaN loss"] },
        { id: "mean", title: "Gradient descent finds the mean", emoji: "🏋️", group: "Easy practice" },
        { id: "lr-sweep", title: "Four learning rates on one bowl", emoji: "🏋️", group: "Medium practice" },
        { id: "lagrange", title: "The biggest field against a wall", emoji: "🏋️", group: "Hard practice" },
        { id: "adam", title: "Adam by hand", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "probability", title: "Probability and statistics", emoji: "🎲", blurb: "Chance, distributions and statistics: the maths that lets a model handle uncertainty and judge its own results.", topics: [
      { id: "probability", title: "Probability and Bayes' Theorem", emoji: "🎲", page: "content/ml-maths/probability.html",
        summary: "Outcomes, events and the complement rule, the law of large numbers, AND and OR rules, independent versus mutually exclusive events, factorials, permutations and combinations, conditional probability from a table, Bayes' theorem and base rates, naive Bayes with Laplace smoothing, and Monte Carlo estimates.",
        keywords: ["probability", "sample space", "event", "addition rule", "multiplication rule", "independent events", "mutually exclusive", "permutation", "combination", "conditional probability", "bayes theorem", "prior", "posterior", "naive bayes", "monte carlo", "birthday problem"],
        added: "2026-10-22",
        sections: [
        { id: "basics", title: "Chance, outcomes and events", emoji: "🎲", group: "Lesson", keywords: ["probability", "sample space", "event", "outcome", "complement", "law of large numbers", "dice"] },
        { id: "rules", title: "AND, OR and independence", emoji: "➕", group: "Lesson", keywords: ["addition rule", "multiplication rule", "union", "intersection", "independent events", "mutually exclusive", "venn diagram"] },
        { id: "counting", title: "Counting: permutations and combinations", emoji: "🔢", group: "Lesson", keywords: ["factorial", "permutation", "combination", "n choose k", "counting", "lottery odds"] },
        { id: "conditional", title: "Conditional probability", emoji: "🔍", group: "Lesson", keywords: ["conditional probability", "given", "contingency table", "P(A|B)", "independence test", "prosecutor fallacy"] },
        { id: "bayes", title: "Bayes' theorem: updating beliefs", emoji: "🔄", group: "Lesson", keywords: ["bayes theorem", "prior", "posterior", "likelihood", "evidence", "base rate", "false positive", "medical test"] },
        { id: "naive", title: "Naive Bayes: a classifier from counting", emoji: "📧", group: "Lesson", keywords: ["naive bayes", "spam filter", "laplace smoothing", "text classification", "conditional independence", "log probabilities"] },
        { id: "ml", title: "Probability inside machine learning", emoji: "🤖", group: "Lesson", keywords: ["monte carlo", "simulation", "predicted probability", "calibration", "likelihood", "sampling", "birthday problem"] },
        { id: "cards", title: "Aces and hearts", emoji: "🏋️", group: "Easy practice" },
        { id: "birthday", title: "The birthday surprise", emoji: "🏋️", group: "Medium practice" },
        { id: "bayes-two", title: "Testing positive again", emoji: "🏋️", group: "Hard practice" },
        { id: "naive", title: "A naive Bayes spam score", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "distributions", title: "Random Variables and Distributions", emoji: "🔔", page: "content/ml-maths/distributions.html",
        summary: "Discrete and continuous random variables, PMF, PDF and CDF, expected value, variance and standard deviation, the Bernoulli, binomial and Poisson distributions, the normal curve and the 68, 95, 99.7 rule, z-scores, the central limit theorem and standard error, covariance and correlation.",
        keywords: ["random variable", "probability distribution", "pmf", "pdf", "cdf", "expected value", "variance", "standard deviation", "bernoulli", "binomial", "poisson", "normal distribution", "gaussian", "z-score", "central limit theorem", "standard error", "covariance", "correlation"],
        added: "2026-10-22",
        sections: [
        { id: "rv", title: "Random variables, PMF, PDF and CDF", emoji: "🎯", group: "Lesson", keywords: ["random variable", "discrete", "continuous", "pmf", "pdf", "cdf", "probability mass function", "probability density function", "cumulative distribution"] },
        { id: "expect", title: "Expected value and variance", emoji: "⚖️", group: "Lesson", keywords: ["expected value", "mean", "variance", "standard deviation", "E[X]", "linearity of expectation", "dice game"] },
        { id: "binomial", title: "Bernoulli and binomial: counting successes", emoji: "🪙", group: "Lesson", keywords: ["bernoulli", "binomial distribution", "success probability", "n choose k", "coin flips", "number of successes"] },
        { id: "poisson", title: "Poisson, uniform and exponential", emoji: "📞", group: "Lesson", keywords: ["poisson distribution", "lambda", "rate", "uniform distribution", "exponential distribution", "waiting time", "count data"] },
        { id: "normal", title: "The normal distribution and z-scores", emoji: "🔔", group: "Lesson", keywords: ["normal distribution", "gaussian", "bell curve", "z-score", "standard normal", "68 95 99.7 rule", "standardisation"] },
        { id: "clt", title: "The central limit theorem", emoji: "📊", group: "Lesson", keywords: ["central limit theorem", "clt", "sample mean", "standard error", "square root n", "sampling distribution"] },
        { id: "cov", title: "Covariance, correlation and distributions in ML", emoji: "🔗", group: "Lesson", keywords: ["covariance", "correlation", "pearson r", "correlation is not causation", "covariance matrix", "distributions in machine learning"] },
        { id: "raffle", title: "Is a raffle ticket worth it?", emoji: "🏋️", group: "Easy practice" },
        { id: "freethrow", title: "Free throws", emoji: "🏋️", group: "Medium practice" },
        { id: "poisson", title: "Calls at the help desk", emoji: "🏋️", group: "Hard practice" },
        { id: "exam", title: "Exam cutoffs on the bell curve", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] },
      { id: "statistics", title: "Statistics and Inference", emoji: "📈", page: "content/ml-maths/statistics.html",
        summary: "Descriptive statistics and outliers, populations, samples and bias, standard error, confidence intervals, null and alternative hypotheses, p-values, Type I and Type II errors, two proportion z-tests for A/B tests, sample size and power, maximum likelihood estimation, least squares regression, R² and the bias and variance trade-off.",
        keywords: ["statistics", "mean", "median", "standard deviation", "outlier", "sample", "bias", "standard error", "confidence interval", "hypothesis test", "p-value", "a/b test", "maximum likelihood", "linear regression", "R squared", "overfitting", "bias variance"],
        added: "2026-10-22",
        sections: [
        { id: "describe", title: "Describing data: centre, spread and outliers", emoji: "📋", group: "Lesson", keywords: ["descriptive statistics", "mean", "median", "mode", "variance", "standard deviation", "quartile", "IQR", "outlier", "bessel correction"] },
        { id: "sampling", title: "Samples, bias and standard error", emoji: "🎣", group: "Lesson", keywords: ["population", "sample", "statistic", "parameter", "standard error", "sampling bias", "selection bias", "survivorship bias"] },
        { id: "ci", title: "Confidence intervals", emoji: "📏", group: "Lesson", keywords: ["confidence interval", "margin of error", "z star", "95 percent", "interval estimate", "coverage"] },
        { id: "tests", title: "Hypothesis tests and p-values", emoji: "⚖️", group: "Lesson", keywords: ["hypothesis test", "null hypothesis", "alternative hypothesis", "p-value", "significance level", "type I error", "type II error", "power", "z test"] },
        { id: "ab", title: "A/B testing", emoji: "🆎", group: "Lesson", keywords: ["a/b test", "conversion rate", "two proportion z test", "pooled proportion", "peeking", "sample size", "online experiment"] },
        { id: "mle", title: "Maximum likelihood estimation", emoji: "🎯", group: "Lesson", keywords: ["maximum likelihood", "MLE", "likelihood", "log-likelihood", "estimator", "cross entropy", "least squares"] },
        { id: "regress", title: "Regression, R² and the bias and variance trade-off", emoji: "📈", group: "Lesson", keywords: ["linear regression", "least squares", "residual", "R squared", "coefficient of determination", "bias variance tradeoff", "overfitting", "underfitting"] },
        { id: "outlier", title: "Spot the outlier", emoji: "🏋️", group: "Easy practice" },
        { id: "poll", title: "Reading a poll", emoji: "🏋️", group: "Medium practice" },
        { id: "ztest", title: "Is the coffee machine off?", emoji: "🏋️", group: "Hard practice" },
        { id: "samplesize", title: "How big should an A/B test be?", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] },
    { id: "models", title: "Maths inside ML models", emoji: "🤖", blurb: "Entropy, loss functions, regularisation and evaluation metrics: where all the earlier maths meets real models.", topics: [
      { id: "loss-metrics", title: "Entropy, Loss Functions and Metrics", emoji: "🎯", page: "content/ml-maths/loss-metrics.html",
        summary: "Surprise and entropy in bits, cross entropy and KL divergence, softmax with temperature and the log-sum-exp trick, regression losses and outliers, binary cross entropy and its p − y gradient, ridge and lasso regularisation, and classification metrics from the confusion matrix to ROC and AUC.",
        keywords: ["entropy", "information theory", "cross entropy", "kl divergence", "softmax", "temperature", "log sum exp", "loss function", "mse", "mae", "huber", "log loss", "regularisation", "ridge", "lasso", "precision", "recall", "f1", "roc", "auc"],
        added: "2026-10-22",
        sections: [
        { id: "entropy", title: "Information and entropy", emoji: "🔥", group: "Lesson", keywords: ["information theory", "entropy", "bits", "surprise", "self information", "information gain", "shannon"] },
        { id: "xent", title: "Cross entropy and KL divergence", emoji: "🎯", group: "Lesson", keywords: ["cross entropy", "kl divergence", "kullback leibler", "relative entropy", "one hot", "information loss"] },
        { id: "softmax", title: "Softmax, temperature and log-sum-exp", emoji: "🌡️", group: "Lesson", keywords: ["softmax", "logits", "temperature", "log sum exp", "numerical stability", "overflow", "multiclass classification"] },
        { id: "losses", title: "Loss functions for regression", emoji: "📉", group: "Lesson", keywords: ["loss function", "mean squared error", "MSE", "mean absolute error", "MAE", "huber loss", "outliers", "regression loss"] },
        { id: "logloss", title: "Log loss for classification", emoji: "🪵", group: "Lesson", keywords: ["log loss", "binary cross entropy", "logistic regression", "sigmoid", "gradient p minus y", "classification loss"] },
        { id: "reg", title: "Regularisation: L2 and L1", emoji: "🧲", group: "Lesson", keywords: ["regularisation", "L2", "ridge", "weight decay", "L1", "lasso", "lambda", "sparsity", "overfitting"] },
        { id: "metrics", title: "Classification metrics, ROC and AUC", emoji: "📊", group: "Lesson", keywords: ["confusion matrix", "accuracy", "precision", "recall", "F1 score", "ROC curve", "AUC", "threshold", "true positive rate", "false positive rate", "imbalanced data"] },
        { id: "bits", title: "Counting bits", emoji: "🏋️", group: "Easy practice" },
        { id: "stable", title: "A softmax that does not overflow", emoji: "🏋️", group: "Medium practice" },
        { id: "ridge", title: "Ridge shrinks the weight", emoji: "🏋️", group: "Hard practice" },
        { id: "auc", title: "AUC by counting pairs", emoji: "🏋️", group: "Expert practice" },
        { id: 'quiz', title: 'Quiz', emoji: '🎯', group: 'Check yourself' },
        { id: 'numbers', title: 'Worked problems', emoji: '🧮', group: 'Check yourself' }
      ] }
    ] }
  ];
}
/* ===== end of mlmath-build ===== */
