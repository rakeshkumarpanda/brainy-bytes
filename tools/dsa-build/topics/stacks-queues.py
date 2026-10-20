# Stacks and queues: LIFO and FIFO, bracket matching, expressions, circular buffers,
# deques and priority queues, monotonic stacks, and undo and redo.

CODES = {}


def C(key, py, js, java):
    CODES[key] = {'py': py, 'js': js, 'java': java}


# ---------------------------------------------------------------- lesson programs
C('stack_basic', py=r'''
stack = []
for x in [10, 20, 30]:
    stack.append(x)                 # push onto the top
    print("push", x, "size", len(stack))
print("peek", stack[-1])            # look at the top without removing it
while stack:
    print("pop", stack.pop())       # last in, first out
print("empty" if not stack else "not empty")
''', js=r'''
const stack = [];
for (const x of [10, 20, 30]) {
  stack.push(x);                    // push onto the top
  console.log("push", x, "size", stack.length);
}
console.log("peek", stack[stack.length - 1]);  // look at the top without removing it
while (stack.length > 0) {
  console.log("pop", stack.pop());  // last in, first out
}
console.log(stack.length === 0 ? "empty" : "not empty");
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;

public class StackBasic {
    public static void main(String[] args) {
        Deque<Integer> stack = new ArrayDeque<>();
        for (int x : new int[]{10, 20, 30}) {
            stack.push(x);                  // push onto the top
            System.out.println("push " + x + " size " + stack.size());
        }
        System.out.println("peek " + stack.peek());   // look at the top without removing it
        while (!stack.isEmpty()) {
            System.out.println("pop " + stack.pop()); // last in, first out
        }
        System.out.println(stack.isEmpty() ? "empty" : "not empty");
    }
}
''')

C('brackets', py=r'''
PAIRS = {")": "(", "]": "[", "}": "{"}


def balanced(s):
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)                 # an opener waits for its partner
        elif ch in PAIRS:
            if not stack or stack[-1] != PAIRS[ch]:
                return False                 # wrong partner, or nothing to close
            stack.pop()
    return not stack                         # anything still open is an error too


for s in ["{[()()]}", "([)]", "(("]:
    print(s, "balanced" if balanced(s) else "not balanced")
''', js=r'''
const PAIRS = { ")": "(", "]": "[", "}": "{" };

function balanced(s) {
  const stack = [];
  for (const ch of s) {
    if ("([{".includes(ch)) {
      stack.push(ch);                        // an opener waits for its partner
    } else if (ch in PAIRS) {
      if (stack.length === 0 || stack[stack.length - 1] !== PAIRS[ch]) return false;  // wrong partner, or nothing to close
      stack.pop();
    }
  }
  return stack.length === 0;                 // anything still open is an error too
}

for (const s of ["{[()()]}", "([)]", "(("]) {
  console.log(s, balanced(s) ? "balanced" : "not balanced");
}
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;

public class Brackets {
    static final Map<Character, Character> PAIRS = Map.of(')', '(', ']', '[', '}', '{');

    static boolean balanced(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        for (char ch : s.toCharArray()) {
            if ("([{".indexOf(ch) >= 0) {
                stack.push(ch);                      // an opener waits for its partner
            } else if (PAIRS.containsKey(ch)) {
                if (stack.isEmpty() || !stack.peek().equals(PAIRS.get(ch))) return false;  // wrong partner, or nothing to close
                stack.pop();
            }
        }
        return stack.isEmpty();                      // anything still open is an error too
    }

    public static void main(String[] args) {
        for (String s : new String[]{"{[()()]}", "([)]", "(("}) {
            System.out.println(s + " " + (balanced(s) ? "balanced" : "not balanced"));
        }
    }
}
''')

C('eval_postfix', py=r'''
def eval_postfix(tokens):
    stack = []
    for t in tokens:
        if t in ("+", "-", "*"):
            b = stack.pop()          # the right operand is on top
            a = stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            else:
                stack.append(a * b)
        else:
            stack.append(int(t))
    return stack.pop()


# (3 + 4) * 2 - 5 written in postfix
print(eval_postfix("3 4 + 2 * 5 -".split()))
''', js=r'''
function evalPostfix(tokens) {
  const stack = [];
  for (const t of tokens) {
    if (t === "+" || t === "-" || t === "*") {
      const b = stack.pop();       // the right operand is on top
      const a = stack.pop();
      if (t === "+") stack.push(a + b);
      else if (t === "-") stack.push(a - b);
      else stack.push(a * b);
    } else {
      stack.push(Number(t));
    }
  }
  return stack.pop();
}

// (3 + 4) * 2 - 5 written in postfix
console.log(evalPostfix("3 4 + 2 * 5 -".split(" ")));
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;

public class Postfix {
    static int evalPostfix(String[] tokens) {
        Deque<Integer> stack = new ArrayDeque<>();
        for (String t : tokens) {
            if (t.equals("+") || t.equals("-") || t.equals("*")) {
                int b = stack.pop();       // the right operand is on top
                int a = stack.pop();
                if (t.equals("+")) stack.push(a + b);
                else if (t.equals("-")) stack.push(a - b);
                else stack.push(a * b);
            } else {
                stack.push(Integer.parseInt(t));
            }
        }
        return stack.pop();
    }

    public static void main(String[] args) {
        // (3 + 4) * 2 - 5 written in postfix
        System.out.println(evalPostfix("3 4 + 2 * 5 -".split(" ")));
    }
}
''')

C('to_postfix', py=r'''
PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def to_postfix(tokens):
    out, ops = [], []
    for t in tokens:
        if t.isdigit():
            out.append(t)                     # numbers go straight to the output
        elif t == "(":
            ops.append(t)
        elif t == ")":
            while ops[-1] != "(":
                out.append(ops.pop())
            ops.pop()                         # drop the "("
        else:
            while ops and ops[-1] != "(" and PREC[ops[-1]] >= PREC[t]:
                out.append(ops.pop())         # stronger or equal operators go first
            ops.append(t)
    while ops:
        out.append(ops.pop())
    return out


print(" ".join(to_postfix("( 3 + 4 ) * 2 - 5".split())))
print(" ".join(to_postfix("1 + 2 * 3".split())))
''', js=r'''
const PREC = { "+": 1, "-": 1, "*": 2, "/": 2 };

function toPostfix(tokens) {
  const out = [], ops = [];
  for (const t of tokens) {
    if (/^\d+$/.test(t)) {
      out.push(t);                            // numbers go straight to the output
    } else if (t === "(") {
      ops.push(t);
    } else if (t === ")") {
      while (ops[ops.length - 1] !== "(") out.push(ops.pop());
      ops.pop();                              // drop the "("
    } else {
      while (ops.length && ops[ops.length - 1] !== "(" && PREC[ops[ops.length - 1]] >= PREC[t]) {
        out.push(ops.pop());                  // stronger or equal operators go first
      }
      ops.push(t);
    }
  }
  while (ops.length) out.push(ops.pop());
  return out;
}

console.log(toPostfix("( 3 + 4 ) * 2 - 5".split(" ")).join(" "));
console.log(toPostfix("1 + 2 * 3".split(" ")).join(" "));
''', java=r'''
import java.util.*;

public class ToPostfix {
    static final Map<String, Integer> PREC = Map.of("+", 1, "-", 1, "*", 2, "/", 2);

    static List<String> toPostfix(String[] tokens) {
        List<String> out = new ArrayList<>();
        Deque<String> ops = new ArrayDeque<>();
        for (String t : tokens) {
            if (Character.isDigit(t.charAt(0))) {
                out.add(t);                            // numbers go straight to the output
            } else if (t.equals("(")) {
                ops.push(t);
            } else if (t.equals(")")) {
                while (!ops.peek().equals("(")) out.add(ops.pop());
                ops.pop();                             // drop the "("
            } else {
                while (!ops.isEmpty() && !ops.peek().equals("(") && PREC.get(ops.peek()) >= PREC.get(t)) {
                    out.add(ops.pop());                // stronger or equal operators go first
                }
                ops.push(t);
            }
        }
        while (!ops.isEmpty()) out.add(ops.pop());
        return out;
    }

    public static void main(String[] args) {
        System.out.println(String.join(" ", toPostfix("( 3 + 4 ) * 2 - 5".split(" "))));
        System.out.println(String.join(" ", toPostfix("1 + 2 * 3".split(" "))));
    }
}
''')

C('circular_queue', py=r'''
class CircularQueue:
    def __init__(self, capacity):
        self.buf = [None] * capacity
        self.head = 0                  # index of the front item
        self.size = 0

    def enqueue(self, x):
        if self.size == len(self.buf):
            return False               # full
        tail = (self.head + self.size) % len(self.buf)
        self.buf[tail] = x
        self.size += 1
        return True

    def dequeue(self):
        if self.size == 0:
            return None
        x = self.buf[self.head]
        self.buf[self.head] = None
        self.head = (self.head + 1) % len(self.buf)   # wrap around to 0 after the last slot
        self.size -= 1
        return x


q = CircularQueue(3)
for x in [1, 2, 3]:
    q.enqueue(x)
print("added" if q.enqueue(4) else "full")
print(q.dequeue(), q.dequeue())
q.enqueue(4)
q.enqueue(5)                           # these reuse the slots at the start of the buffer
print(q.dequeue(), q.dequeue(), q.dequeue())
''', js=r'''
class CircularQueue {
  constructor(capacity) {
    this.buf = new Array(capacity).fill(null);
    this.head = 0;                     // index of the front item
    this.size = 0;
  }

  enqueue(x) {
    if (this.size === this.buf.length) return false;  // full
    const tail = (this.head + this.size) % this.buf.length;
    this.buf[tail] = x;
    this.size++;
    return true;
  }

  dequeue() {
    if (this.size === 0) return null;
    const x = this.buf[this.head];
    this.buf[this.head] = null;
    this.head = (this.head + 1) % this.buf.length;    // wrap around to 0 after the last slot
    this.size--;
    return x;
  }
}

const q = new CircularQueue(3);
for (const x of [1, 2, 3]) q.enqueue(x);
console.log(q.enqueue(4) ? "added" : "full");
console.log(q.dequeue(), q.dequeue());
q.enqueue(4);
q.enqueue(5);                          // these reuse the slots at the start of the buffer
console.log(q.dequeue(), q.dequeue(), q.dequeue());
''', java=r'''
public class CircularQueue {
    int[] buf;
    int head = 0;                      // index of the front item
    int size = 0;

    CircularQueue(int capacity) { buf = new int[capacity]; }

    boolean enqueue(int x) {
        if (size == buf.length) return false;   // full
        int tail = (head + size) % buf.length;
        buf[tail] = x;
        size++;
        return true;
    }

    int dequeue() {
        int x = buf[head];
        buf[head] = 0;
        head = (head + 1) % buf.length;         // wrap around to 0 after the last slot
        size--;
        return x;
    }

    public static void main(String[] args) {
        CircularQueue q = new CircularQueue(3);
        for (int x : new int[]{1, 2, 3}) q.enqueue(x);
        System.out.println(q.enqueue(4) ? "added" : "full");
        System.out.println(q.dequeue() + " " + q.dequeue());
        q.enqueue(4);
        q.enqueue(5);                           // these reuse the slots at the start of the buffer
        System.out.println(q.dequeue() + " " + q.dequeue() + " " + q.dequeue());
    }
}
''')

C('deque_heap', py=r'''
from collections import deque
import heapq

d = deque()
d.append("b")
d.appendleft("a")            # O(1) at both ends
d.append("c")
print(d.popleft(), d.pop(), len(d))

# a priority queue always hands out the smallest item first
pq = []
for x in [5, 1, 8, 3]:
    heapq.heappush(pq, x)    # O(log n)
order = []
while pq:
    order.append(heapq.heappop(pq))
print(order)
''', js=r'''
// JavaScript has no built in deque or heap. A small binary heap takes a few lines.
class MinHeap {
  constructor() { this.a = []; }
  push(x) {
    const a = this.a;
    a.push(x);
    let i = a.length - 1;
    while (i > 0 && a[(i - 1) >> 1] > a[i]) {   // bubble up past bigger parents
      const p = (i - 1) >> 1;
      [a[p], a[i]] = [a[i], a[p]];
      i = p;
    }
  }
  pop() {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) {
      a[0] = last;
      let i = 0;
      for (;;) {                                  // sink down to the smaller child
        const l = 2 * i + 1, r = l + 1;
        let m = i;
        if (l < a.length && a[l] < a[m]) m = l;
        if (r < a.length && a[r] < a[m]) m = r;
        if (m === i) break;
        [a[m], a[i]] = [a[i], a[m]];
        i = m;
      }
    }
    return top;
  }
  get size() { return this.a.length; }
}

const d = ["b"];
d.unshift("a");              // fine for tiny arrays, but unshift is O(n)
d.push("c");
console.log(d.shift(), d.pop(), d.length);

// a priority queue always hands out the smallest item first
const pq = new MinHeap();
for (const x of [5, 1, 8, 3]) pq.push(x);   // O(log n)
const order = [];
while (pq.size) order.push(pq.pop());
console.log("[" + order.join(", ") + "]");
''', java=r'''
import java.util.*;

public class DequeHeap {
    public static void main(String[] args) {
        Deque<String> d = new ArrayDeque<>();
        d.addLast("b");
        d.addFirst("a");             // O(1) at both ends
        d.addLast("c");
        String first = d.pollFirst();
        String last = d.pollLast();
        System.out.println(first + " " + last + " " + d.size());

        // a priority queue always hands out the smallest item first
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int x : new int[]{5, 1, 8, 3}) pq.add(x);   // O(log n)
        List<Integer> order = new ArrayList<>();
        while (!pq.isEmpty()) order.add(pq.poll());
        System.out.println(order);
    }
}
''')

C('next_greater', py=r'''
def next_greater(a):
    result = [-1] * len(a)
    stack = []                       # indexes still waiting for a bigger value
    for i in range(len(a)):
        while stack and a[stack[-1]] < a[i]:
            result[stack.pop()] = a[i]   # a[i] is the first bigger value to their right
        stack.append(i)
    return result


print(next_greater([4, 5, 2, 25, 7, 8]))
''', js=r'''
function nextGreater(a) {
  const result = new Array(a.length).fill(-1);
  const stack = [];                  // indexes still waiting for a bigger value
  for (let i = 0; i < a.length; i++) {
    while (stack.length && a[stack[stack.length - 1]] < a[i]) {
      result[stack.pop()] = a[i];    // a[i] is the first bigger value to their right
    }
    stack.push(i);
  }
  return result;
}

console.log("[" + nextGreater([4, 5, 2, 25, 7, 8]).join(", ") + "]");
''', java=r'''
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;

public class NextGreater {
    static int[] nextGreater(int[] a) {
        int[] result = new int[a.length];
        Arrays.fill(result, -1);
        Deque<Integer> stack = new ArrayDeque<>();   // indexes still waiting for a bigger value
        for (int i = 0; i < a.length; i++) {
            while (!stack.isEmpty() && a[stack.peek()] < a[i]) {
                result[stack.pop()] = a[i];          // a[i] is the first bigger value to their right
            }
            stack.push(i);
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(nextGreater(new int[]{4, 5, 2, 25, 7, 8})));
    }
}
''')

C('undo_redo', py=r'''
text = ""
undo, redo = [], []


def type_text(s):
    global text
    undo.append(text)        # remember the state before the change
    redo.clear()             # a new change makes the old redo history meaningless
    text += s


def do_undo():
    global text
    if undo:
        redo.append(text)
        text = undo.pop()


def do_redo():
    global text
    if redo:
        undo.append(text)
        text = redo.pop()


type_text("Hello")
type_text(" world")
print("[" + text + "]")
do_undo()
print("[" + text + "]")
do_redo()
print("[" + text + "]")
do_undo()
do_undo()
print("[" + text + "]")
''', js=r'''
let text = "";
const undo = [], redo = [];

function typeText(s) {
  undo.push(text);           // remember the state before the change
  redo.length = 0;           // a new change makes the old redo history meaningless
  text += s;
}

function doUndo() {
  if (undo.length) {
    redo.push(text);
    text = undo.pop();
  }
}

function doRedo() {
  if (redo.length) {
    undo.push(text);
    text = redo.pop();
  }
}

typeText("Hello");
typeText(" world");
console.log("[" + text + "]");
doUndo();
console.log("[" + text + "]");
doRedo();
console.log("[" + text + "]");
doUndo();
doUndo();
console.log("[" + text + "]");
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;

public class UndoRedo {
    static String text = "";
    static Deque<String> undo = new ArrayDeque<>();
    static Deque<String> redo = new ArrayDeque<>();

    static void typeText(String s) {
        undo.push(text);         // remember the state before the change
        redo.clear();            // a new change makes the old redo history meaningless
        text += s;
    }

    static void doUndo() {
        if (!undo.isEmpty()) {
            redo.push(text);
            text = undo.pop();
        }
    }

    static void doRedo() {
        if (!redo.isEmpty()) {
            undo.push(text);
            text = redo.pop();
        }
    }

    public static void main(String[] args) {
        typeText("Hello");
        typeText(" world");
        System.out.println("[" + text + "]");
        doUndo();
        System.out.println("[" + text + "]");
        doRedo();
        System.out.println("[" + text + "]");
        doUndo();
        doUndo();
        System.out.println("[" + text + "]");
    }
}
''')

# ---------------------------------------------------------------- practice solutions
C('p_remove_adjacent', py=r'''
def remove_adjacent(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()              # a matching pair cancels out
        else:
            stack.append(ch)
    return "".join(stack)


print(remove_adjacent("abbaca"))
print(remove_adjacent("azxxzy"))
''', js=r'''
function removeAdjacent(s) {
  const stack = [];
  for (const ch of s) {
    if (stack.length && stack[stack.length - 1] === ch) stack.pop();  // a matching pair cancels out
    else stack.push(ch);
  }
  return stack.join("");
}

console.log(removeAdjacent("abbaca"));
console.log(removeAdjacent("azxxzy"));
''', java=r'''
public class RemoveAdjacent {
    static String removeAdjacent(String s) {
        StringBuilder stack = new StringBuilder();   // a StringBuilder works as a stack of characters
        for (char ch : s.toCharArray()) {
            int n = stack.length();
            if (n > 0 && stack.charAt(n - 1) == ch) stack.deleteCharAt(n - 1);  // a matching pair cancels out
            else stack.append(ch);
        }
        return stack.toString();
    }

    public static void main(String[] args) {
        System.out.println(removeAdjacent("abbaca"));
        System.out.println(removeAdjacent("azxxzy"));
    }
}
''')

C('p_josephus', py=r'''
from collections import deque


def josephus(n, k):
    q = deque(range(1, n + 1))
    order = []
    while len(q) > 1:
        for _ in range(k - 1):
            q.append(q.popleft())    # pass the potato: front person goes to the back
        order.append(q.popleft())    # the k-th person leaves
    return order, q[0]


order, last = josephus(7, 3)
print("out:", " ".join([str(x) for x in order]))
print("survivor:", last)
''', js=r'''
function josephus(n, k) {
  const q = [];
  for (let i = 1; i <= n; i++) q.push(i);
  let head = 0;                      // index of the front, so removing from the front is O(1)
  const order = [];
  while (q.length - head > 1) {
    for (let s = 0; s < k - 1; s++) q.push(q[head++]);  // pass the potato: front person goes to the back
    order.push(q[head++]);           // the k-th person leaves
  }
  return [order, q[head]];
}

const [order, last] = josephus(7, 3);
console.log("out:", order.join(" "));
console.log("survivor:", last);
''', java=r'''
import java.util.*;

public class Josephus {
    public static void main(String[] args) {
        int n = 7, k = 3;
        Deque<Integer> q = new ArrayDeque<>();
        for (int i = 1; i <= n; i++) q.addLast(i);
        List<String> order = new ArrayList<>();
        while (q.size() > 1) {
            for (int s = 0; s < k - 1; s++) q.addLast(q.pollFirst());  // pass the potato: front person goes to the back
            order.add(String.valueOf(q.pollFirst()));                 // the k-th person leaves
        }
        System.out.println("out: " + String.join(" ", order));
        System.out.println("survivor: " + q.peekFirst());
    }
}
''')

C('p_min_stack', py=r'''
class MinStack:
    def __init__(self):
        self.items = []
        self.mins = []               # mins[-1] is the smallest value in the stack right now

    def push(self, x):
        self.items.append(x)
        self.mins.append(x if not self.mins else min(x, self.mins[-1]))

    def pop(self):
        self.mins.pop()
        return self.items.pop()

    def get_min(self):
        return self.mins[-1]


s = MinStack()
for x in [5, 3, 7, 2]:
    s.push(x)
print(s.get_min())
s.pop()
print(s.get_min())
s.pop()
s.pop()
print(s.get_min())
''', js=r'''
class MinStack {
  constructor() {
    this.items = [];
    this.mins = [];                  // the last entry is the smallest value in the stack right now
  }
  push(x) {
    this.items.push(x);
    this.mins.push(this.mins.length ? Math.min(x, this.mins[this.mins.length - 1]) : x);
  }
  pop() {
    this.mins.pop();
    return this.items.pop();
  }
  getMin() {
    return this.mins[this.mins.length - 1];
  }
}

const s = new MinStack();
for (const x of [5, 3, 7, 2]) s.push(x);
console.log(s.getMin());
s.pop();
console.log(s.getMin());
s.pop();
s.pop();
console.log(s.getMin());
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;

public class MinStack {
    Deque<Integer> items = new ArrayDeque<>();
    Deque<Integer> mins = new ArrayDeque<>();    // the top is the smallest value in the stack right now

    void push(int x) {
        items.push(x);
        mins.push(mins.isEmpty() ? x : Math.min(x, mins.peek()));
    }

    int pop() {
        mins.pop();
        return items.pop();
    }

    int getMin() {
        return mins.peek();
    }

    public static void main(String[] args) {
        MinStack s = new MinStack();
        for (int x : new int[]{5, 3, 7, 2}) s.push(x);
        System.out.println(s.getMin());
        s.pop();
        System.out.println(s.getMin());
        s.pop();
        s.pop();
        System.out.println(s.getMin());
    }
}
''')

C('p_simplify_path', py=r'''
def simplify(path):
    stack = []
    for part in path.split("/"):
        if part == "..":
            if stack:
                stack.pop()          # go up one folder
        elif part and part != ".":
            stack.append(part)       # skip empty pieces and "."
    return "/" + "/".join(stack)


print(simplify("/home//user/./docs/../music/"))
print(simplify("/../"))
''', js=r'''
function simplify(path) {
  const stack = [];
  for (const part of path.split("/")) {
    if (part === "..") {
      if (stack.length) stack.pop();          // go up one folder
    } else if (part && part !== ".") {
      stack.push(part);                       // skip empty pieces and "."
    }
  }
  return "/" + stack.join("/");
}

console.log(simplify("/home//user/./docs/../music/"));
console.log(simplify("/../"));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class SimplifyPath {
    static String simplify(String path) {
        List<String> stack = new ArrayList<>();
        for (String part : path.split("/")) {
            if (part.equals("..")) {
                if (!stack.isEmpty()) stack.remove(stack.size() - 1);  // go up one folder
            } else if (!part.isEmpty() && !part.equals(".")) {
                stack.add(part);                                       // skip empty pieces and "."
            }
        }
        return "/" + String.join("/", stack);
    }

    public static void main(String[] args) {
        System.out.println(simplify("/home//user/./docs/../music/"));
        System.out.println(simplify("/../"));
    }
}
''')

C('p_decode_string', py=r'''
def decode(s):
    counts, parts = [], []
    cur, k = "", 0
    for ch in s:
        if ch.isdigit():
            k = k * 10 + int(ch)
        elif ch == "[":
            counts.append(k)         # save the repeat count and the text built so far
            parts.append(cur)
            cur, k = "", 0
        elif ch == "]":
            cur = parts.pop() + cur * counts.pop()
        else:
            cur += ch
    return cur


print(decode("3[a2[c]]"))
print(decode("2[ab]3[x]"))
''', js=r'''
function decode(s) {
  const counts = [], parts = [];
  let cur = "", k = 0;
  for (const ch of s) {
    if (ch >= "0" && ch <= "9") {
      k = k * 10 + Number(ch);
    } else if (ch === "[") {
      counts.push(k);                // save the repeat count and the text built so far
      parts.push(cur);
      cur = "";
      k = 0;
    } else if (ch === "]") {
      cur = parts.pop() + cur.repeat(counts.pop());
    } else {
      cur += ch;
    }
  }
  return cur;
}

console.log(decode("3[a2[c]]"));
console.log(decode("2[ab]3[x]"));
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;

public class DecodeString {
    static String decode(String s) {
        Deque<Integer> counts = new ArrayDeque<>();
        Deque<String> parts = new ArrayDeque<>();
        String cur = "";
        int k = 0;
        for (char ch : s.toCharArray()) {
            if (Character.isDigit(ch)) {
                k = k * 10 + (ch - '0');
            } else if (ch == '[') {
                counts.push(k);              // save the repeat count and the text built so far
                parts.push(cur);
                cur = "";
                k = 0;
            } else if (ch == ']') {
                cur = parts.pop() + cur.repeat(counts.pop());
            } else {
                cur += ch;
            }
        }
        return cur;
    }

    public static void main(String[] args) {
        System.out.println(decode("3[a2[c]]"));
        System.out.println(decode("2[ab]3[x]"));
    }
}
''')

C('p_largest_rect', py=r'''
def largest_rectangle(h):
    stack = []                       # indexes of bars with increasing heights
    best = 0
    for i in range(len(h) + 1):
        cur = h[i] if i < len(h) else 0      # a final bar of height 0 empties the stack
        while stack and h[stack[-1]] > cur:
            height = h[stack.pop()]
            left = stack[-1] + 1 if stack else 0
            best = max(best, height * (i - left))   # the popped bar spans from left to i - 1
        stack.append(i)
    return best


print(largest_rectangle([2, 1, 5, 6, 2, 3]))
''', js=r'''
function largestRectangle(h) {
  const stack = [];                  // indexes of bars with increasing heights
  let best = 0;
  for (let i = 0; i <= h.length; i++) {
    const cur = i < h.length ? h[i] : 0;     // a final bar of height 0 empties the stack
    while (stack.length && h[stack[stack.length - 1]] > cur) {
      const height = h[stack.pop()];
      const left = stack.length ? stack[stack.length - 1] + 1 : 0;
      best = Math.max(best, height * (i - left));  // the popped bar spans from left to i - 1
    }
    stack.push(i);
  }
  return best;
}

console.log(largestRectangle([2, 1, 5, 6, 2, 3]));
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;

public class Histogram {
    static int largestRectangle(int[] h) {
        Deque<Integer> stack = new ArrayDeque<>();   // indexes of bars with increasing heights
        int best = 0;
        for (int i = 0; i <= h.length; i++) {
            int cur = i < h.length ? h[i] : 0;       // a final bar of height 0 empties the stack
            while (!stack.isEmpty() && h[stack.peek()] > cur) {
                int height = h[stack.pop()];
                int left = stack.isEmpty() ? 0 : stack.peek() + 1;
                best = Math.max(best, height * (i - left));  // the popped bar spans from left to i - 1
            }
            stack.push(i);
        }
        return best;
    }

    public static void main(String[] args) {
        System.out.println(largestRectangle(new int[]{2, 1, 5, 6, 2, 3}));
    }
}
''')

C('p_window_max', py=r'''
from collections import deque


def window_max(a, k):
    dq = deque()                     # indexes whose values decrease from front to back
    out = []
    for i in range(len(a)):
        while dq and a[dq[-1]] <= a[i]:
            dq.pop()                 # a smaller value can never be a maximum again
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()             # the front slid out of the window
        if i >= k - 1:
            out.append(a[dq[0]])
    return out


print(window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
''', js=r'''
function windowMax(a, k) {
  const dq = [];                     // indexes whose values decrease from front to back
  let head = 0;                      // dq[head] is the front
  const out = [];
  for (let i = 0; i < a.length; i++) {
    while (dq.length > head && a[dq[dq.length - 1]] <= a[i]) dq.pop();  // a smaller value can never be a maximum again
    dq.push(i);
    if (dq[head] <= i - k) head++;   // the front slid out of the window
    if (i >= k - 1) out.push(a[dq[head]]);
  }
  return out;
}

console.log("[" + windowMax([1, 3, -1, -3, 5, 3, 6, 7], 3).join(", ") + "]");
''', java=r'''
import java.util.*;

public class WindowMax {
    static List<Integer> windowMax(int[] a, int k) {
        Deque<Integer> dq = new ArrayDeque<>();      // indexes whose values decrease from front to back
        List<Integer> out = new ArrayList<>();
        for (int i = 0; i < a.length; i++) {
            while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();  // a smaller value can never be a maximum again
            dq.addLast(i);
            if (dq.peekFirst() <= i - k) dq.pollFirst();                     // the front slid out of the window
            if (i >= k - 1) out.add(a[dq.peekFirst()]);
        }
        return out;
    }

    public static void main(String[] args) {
        System.out.println(windowMax(new int[]{1, 3, -1, -3, 5, 3, 6, 7}, 3));
    }
}
''')

C('p_calculator', py=r'''
PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def apply(nums, op):
    b = nums.pop()
    a = nums.pop()
    if op == "+":
        nums.append(a + b)
    elif op == "-":
        nums.append(a - b)
    elif op == "*":
        nums.append(a * b)
    else:
        nums.append(int(a / b))      # cut toward zero, like Java and JavaScript


def calculate(s):
    nums, ops = [], []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isdigit():
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            nums.append(int(s[i:j]))
            i = j
            continue
        if ch == "(":
            ops.append(ch)
        elif ch == ")":
            while ops[-1] != "(":
                apply(nums, ops.pop())
            ops.pop()
        elif ch in PREC:
            while ops and ops[-1] != "(" and PREC[ops[-1]] >= PREC[ch]:
                apply(nums, ops.pop())
            ops.append(ch)
        i += 1
    while ops:
        apply(nums, ops.pop())
    return nums[-1]


print(calculate("3 + 2 * (4 - 1)"))
print(calculate("(8 + 4) / 3 - 1"))
''', js=r'''
const PREC = { "+": 1, "-": 1, "*": 2, "/": 2 };
const isDigit = c => c >= "0" && c <= "9";

function apply(nums, op) {
  const b = nums.pop();
  const a = nums.pop();
  if (op === "+") nums.push(a + b);
  else if (op === "-") nums.push(a - b);
  else if (op === "*") nums.push(a * b);
  else nums.push(Math.trunc(a / b));   // cut toward zero
}

function calculate(s) {
  const nums = [], ops = [];
  let i = 0;
  while (i < s.length) {
    const ch = s[i];
    if (isDigit(ch)) {
      let j = i;
      while (j < s.length && isDigit(s[j])) j++;
      nums.push(Number(s.slice(i, j)));
      i = j;
      continue;
    }
    if (ch === "(") {
      ops.push(ch);
    } else if (ch === ")") {
      while (ops[ops.length - 1] !== "(") apply(nums, ops.pop());
      ops.pop();
    } else if (ch in PREC) {
      while (ops.length && ops[ops.length - 1] !== "(" && PREC[ops[ops.length - 1]] >= PREC[ch]) apply(nums, ops.pop());
      ops.push(ch);
    }
    i++;
  }
  while (ops.length) apply(nums, ops.pop());
  return nums[nums.length - 1];
}

console.log(calculate("3 + 2 * (4 - 1)"));
console.log(calculate("(8 + 4) / 3 - 1"));
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;

public class Calculator {
    static final Map<Character, Integer> PREC = Map.of('+', 1, '-', 1, '*', 2, '/', 2);

    static void apply(Deque<Integer> nums, char op) {
        int b = nums.pop();
        int a = nums.pop();
        if (op == '+') nums.push(a + b);
        else if (op == '-') nums.push(a - b);
        else if (op == '*') nums.push(a * b);
        else nums.push(a / b);              // Java integer division cuts toward zero
    }

    static int calculate(String s) {
        Deque<Integer> nums = new ArrayDeque<>();
        Deque<Character> ops = new ArrayDeque<>();
        int i = 0;
        while (i < s.length()) {
            char ch = s.charAt(i);
            if (Character.isDigit(ch)) {
                int j = i;
                while (j < s.length() && Character.isDigit(s.charAt(j))) j++;
                nums.push(Integer.parseInt(s.substring(i, j)));
                i = j;
                continue;
            }
            if (ch == '(') {
                ops.push(ch);
            } else if (ch == ')') {
                while (ops.peek() != '(') apply(nums, ops.pop());
                ops.pop();
            } else if (PREC.containsKey(ch)) {
                while (!ops.isEmpty() && ops.peek() != '(' && PREC.get(ops.peek()) >= PREC.get(ch)) apply(nums, ops.pop());
                ops.push(ch);
            }
            i++;
        }
        while (!ops.isEmpty()) apply(nums, ops.pop());
        return nums.peek();
    }

    public static void main(String[] args) {
        System.out.println(calculate("3 + 2 * (4 - 1)"));
        System.out.println(calculate("(8 + 4) / 3 - 1"));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    dict(id='stack', emoji='🥞', title='The stack: last in, first out', html='''
<p>A <b>stack</b> is a pile. You add to the top (<b>push</b>), look at the top (<b>peek</b>) and remove from the top (<b>pop</b>). The last item in is the first item out, which is called <b>LIFO</b>.</p>
<div class="tw"><table class="jt"><tr><th>Operation</th><th>Python list</th><th>JavaScript array</th><th>Java <code>ArrayDeque</code></th><th>Cost</th></tr>
<tr><td>push</td><td><code>s.append(x)</code></td><td><code>s.push(x)</code></td><td><code>s.push(x)</code></td><td class="yes">O(1) amortized</td></tr>
<tr><td>pop</td><td><code>s.pop()</code></td><td><code>s.pop()</code></td><td><code>s.pop()</code></td><td class="yes">O(1)</td></tr>
<tr><td>peek</td><td><code>s[-1]</code></td><td><code>s[s.length - 1]</code></td><td><code>s.peek()</code></td><td class="yes">O(1)</td></tr>
<tr><td>is empty</td><td><code>not s</code></td><td><code>s.length === 0</code></td><td><code>s.isEmpty()</code></td><td class="yes">O(1)</td></tr>
</table></div>
<div class="viz" data-viz="sqplay"></div>
<div class="c3" data-k="stack_basic" data-label="Push, peek and pop"></div>
<div class="grid2">
<div class="box"><h4>📞 The call stack</h4><p>Every function call pushes a frame with its local variables. Returning pops it. Infinite recursion keeps pushing until the stack overflows.</p></div>
<div class="box"><h4>⚠️ Underflow</h4><p>Popping an empty stack is an error: an exception in Python and Java, <code>undefined</code> in JavaScript. Always check that it is not empty first.</p></div>
</div>
<div class="warn">In Java, avoid the old <code>Stack</code> class. It is synchronized and slower. <code>ArrayDeque</code> is the recommended stack and queue.</div>
'''),
    dict(id='brackets', emoji='🧷', title='Matching brackets with a stack', html='''
<p>Code editors, compilers and HTML checkers all need to know whether brackets are properly nested. A stack does it in one pass: push every opener, and when a closer arrives, the top of the stack must be its partner.</p>
<div class="viz" data-viz="brackets"></div>
<div class="c3" data-k="brackets" data-label="Balanced brackets"></div>
<p>Three things can go wrong, and the code checks all three: a closer with an empty stack, a closer whose partner is not on top, and openers left on the stack at the end. Each character is pushed and popped at most once, so it is <b>O(n)</b>.</p>
<div class="rule">Whenever the most recent unfinished thing must be finished first, think stack: brackets, nested tags, undo, function calls, backtracking.</div>
'''),
    dict(id='expressions', emoji='🧮', title='Evaluating expressions', html='''
<p>People write <b>infix</b> expressions like <code>(3 + 4) * 2 − 5</code>, with operators between the numbers and parentheses for order. Computers prefer <b>postfix</b> (also called reverse Polish notation), where each operator comes after its two operands: <code>3 4 + 2 * 5 −</code>. Postfix needs no parentheses and no precedence rules.</p>
<h3>Evaluating postfix</h3>
<p>Read the tokens left to right. Push numbers. For an operator, pop the right operand, then the left one, compute, and push the result.</p>
<div class="tw"><table class="jt"><tr><th>Token</th><th>Action</th><th>Stack after</th></tr>
<tr><td>3, 4</td><td>push</td><td>3 4</td></tr>
<tr><td>+</td><td>pop 4 and 3, push 7</td><td>7</td></tr>
<tr><td>2</td><td>push</td><td>7 2</td></tr>
<tr><td>*</td><td>pop 2 and 7, push 14</td><td>14</td></tr>
<tr><td>5</td><td>push</td><td>14 5</td></tr>
<tr><td>−</td><td>pop 5 and 14, push 9</td><td>9</td></tr>
</table></div>
<div class="c3" data-k="eval_postfix" data-label="Evaluate a postfix expression"></div>
<h3>Turning infix into postfix</h3>
<p>Edsger Dijkstra's <b>shunting yard</b> algorithm uses a stack of operators. Numbers go straight to the output. Before pushing an operator, pop every operator on the stack with greater or equal precedence. A <code>(</code> waits on the stack until its <code>)</code> arrives.</p>
<div class="c3" data-k="to_postfix" data-label="Shunting yard: infix to postfix"></div>
<div class="exam">Pop order matters for − and /. The first pop gives the <b>right</b> operand. For <code>8 2 −</code> you pop 2, then 8, and compute 8 − 2 = 6, not 2 − 8.</div>
'''),
    dict(id='queue', emoji='🚶', title='The queue: first in, first out', html='''
<p>A <b>queue</b> is a line at a ticket counter. Items join at the back (<b>enqueue</b>) and leave from the front (<b>dequeue</b>). The first item in is the first item out: <b>FIFO</b>.</p>
<div class="warn">Removing the first element of a Python list (<code>pop(0)</code>) or a JavaScript array (<code>shift()</code>) moves every other element, which is <b>O(n)</b>. Use <code>collections.deque</code> in Python, <code>ArrayDeque</code> in Java, and a head index or a ring buffer in JavaScript.</div>
<h3>The circular buffer</h3>
<p>A fixed size array can hold a queue with no shifting at all. Keep the index of the front (<code>head</code>) and the number of items (<code>size</code>). The back is at <code>(head + size) mod capacity</code>. When an index runs off the end of the array, the remainder wraps it back to 0.</p>
<span class="eq">tail = (head + size) mod capacity      head = (head + 1) mod capacity</span>
<div class="viz" data-viz="ring"></div>
<div class="c3" data-k="circular_queue" data-label="A queue in a circular buffer"></div>
<div class="tip">Keyboard input, audio streaming and network cards all use ring buffers: a fixed block of memory that is reused forever, with O(1) enqueue and dequeue.</div>
'''),
    dict(id='deque-priority', emoji='🎟️', title='Deques and priority queues', html='''
<div class="grid2">
<div class="box"><h4>↔️ Deque</h4><p>A <b>double ended queue</b> allows push and pop at both ends in O(1). It can act as a stack, a queue, or both at once. Sliding window problems love it.</p></div>
<div class="box"><h4>🏥 Priority queue</h4><p>Items leave in order of <b>priority</b>, not arrival. An emergency room treats the most urgent patient first. It is built on a <b>binary heap</b>: insert and remove the smallest in O(log n).</p></div>
</div>
<div class="tw"><table class="jt"><tr><th></th><th>Python</th><th>JavaScript</th><th>Java</th></tr>
<tr><td>Deque</td><td><code>collections.deque</code></td><td>none built in</td><td><code>ArrayDeque</code></td></tr>
<tr><td>Priority queue</td><td><code>heapq</code> on a list</td><td>none built in, write a small heap</td><td><code>PriorityQueue</code></td></tr>
</table></div>
<div class="c3" data-k="deque_heap" data-label="A deque and a priority queue"></div>
<p>A heap is a complete binary tree stored in an array: the children of index i sit at 2i + 1 and 2i + 2, and every parent is smaller than its children. The Trees topic explains it in detail.</p>
'''),
    dict(id='monotonic', emoji='📈', title='Monotonic stacks', html='''
<p>A <b>monotonic stack</b> keeps its items in increasing or decreasing order. It answers "what is the next bigger (or smaller) item to my right?" for every position in a single pass.</p>
<p>For the <b>next greater element</b>, keep indexes of values still waiting for an answer. When a bigger value arrives, it is the answer for every smaller waiting value, so pop them and fill in their result. Then push the new index.</p>
<div class="viz" data-viz="mono"></div>
<div class="c3" data-k="next_greater" data-label="Next greater element with a monotonic stack"></div>
<p>Each index is pushed once and popped at most once, so the nested loops still add up to <b>O(n)</b>, not O(n²).</p>
<span class="eq">pushes + pops ≤ n + n = 2n</span>
<div class="tip">The same pattern solves "days until a warmer day", stock spans, the largest rectangle in a histogram and trapping rain water.</div>
'''),
    dict(id='real-world', emoji='↩️', title='Undo, redo and other everyday uses', html='''
<p>Undo and redo are two stacks. Every change pushes the old state onto the undo stack. Undo moves the current state to the redo stack and pops the previous one. A brand new change clears the redo stack, because the future it remembered no longer exists.</p>
<div class="c3" data-k="undo_redo" data-label="Undo and redo with two stacks"></div>
<div class="tw"><table class="jt"><tr><th>Where</th><th>Structure</th><th>Why</th></tr>
<tr><td>Browser back button</td><td>stack</td><td>the most recent page comes back first</td></tr>
<tr><td>Printer jobs, chat messages</td><td>queue</td><td>fair order of arrival</td></tr>
<tr><td>Breadth first search</td><td>queue</td><td>visit nearest places first</td></tr>
<tr><td>Depth first search, backtracking</td><td>stack (or recursion)</td><td>finish the newest path first</td></tr>
<tr><td>Operating system scheduler</td><td>priority queue</td><td>important tasks run first</td></tr>
<tr><td>Recent items, sliding windows</td><td>deque</td><td>add on one end, drop from the other</td></tr>
</table></div>
'''),
]

INFO = {
    'title': 'Plates and queues',
    'panels': [
        {'s': [['e', '🥞'], ['c', [4, 8, 15], {'hl': {2: 'hl'}, 'p': {2: 'top'}}]], 'h': 'Stack', 't': 'Push and pop at the top.', 'more': 'Last in, first out, like a pile of plates. Undo and the call stack work this way.'},
        {'s': [['e', '🚶🚶🚶'], ['c', [3, 9, 1], {'hl': {0: 'ok'}, 'p': {0: 'front'}}]], 'h': 'Queue', 't': 'Join at the back, leave from the front.', 'more': 'First in, first out, like a ticket line. Printers and breadth first search work this way.'},
        {'s': [['e', '🔄'], ['t', 'tail = (head + size) mod n', {'b': 1, 'size': 11}]], 'h': 'Ring buffer', 't': 'A queue that wraps around.', 'more': 'A fixed array, two numbers and the remainder operator give O(1) at both ends.'},
        {'s': [['e', '🏥'], ['t', 'smallest out first', {'b': 1}]], 'h': 'Priority queue', 't': 'The most urgent item leaves first.', 'more': 'A binary heap inserts and removes the minimum in O(log n).'},
    ],
    'remember': 'Stack: last in, first out. Queue: first in, first out. Both do their main operations in O(1), as long as you never remove from the front of a plain array.',
}

REAL = [
    ['↩️', 'Ctrl+Z in every app', 'Each edit is pushed onto an undo stack. Undo pops the newest change first, which is exactly the one you want to take back.'],
    ['🖨️', 'The office printer', 'Print jobs wait in a queue and come out in the order they were sent, so nobody can jump the line.'],
    ['🏥', 'Hospital triage', 'Patients are seen by urgency, not by arrival time. That is a priority queue: the most urgent case always comes out first.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome',
     'en': 'Welcome to stacks and queues. A stack takes and gives from the top, last in first out. A queue lets items join at the back and leave from the front, first in first out. You will see how these two simple rules check brackets, evaluate expressions, power undo, and much more.',
     'hi': 'Stacks और queues में आपका स्वागत है। Stack ऊपर से लेता और देता है, last in first out। Queue में items पीछे जुड़ते हैं और आगे से निकलते हैं, first in first out। आप देखेंगे कि ये दो सरल नियम brackets जाँचते हैं, expressions हल करते हैं, undo चलाते हैं, और बहुत कुछ करते हैं।',
     'kn': 'Stacks ಮತ್ತು queues ಗೆ ಸ್ವಾಗತ. Stack ಮೇಲಿನಿಂದ ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ ಮತ್ತು ಕೊಡುತ್ತದೆ, last in first out. Queue ನಲ್ಲಿ items ಹಿಂದೆ ಸೇರುತ್ತವೆ ಮತ್ತು ಮುಂದೆಯಿಂದ ಹೊರಡುತ್ತವೆ, first in first out. ಈ ಎರಡು ಸರಳ ನಿಯಮಗಳು brackets ಪರೀಕ್ಷಿಸುವುದು, expressions ಲೆಕ್ಕಿಸುವುದು, undo ನಡೆಸುವುದು ಹೇಗೆ ಎಂದು ನೋಡುತ್ತೀರಿ.',
     'or': 'Stacks ଓ queues କୁ ସ୍ୱାଗତ। Stack ଉପରୁ ନିଏ ଓ ଦିଏ, last in first out। Queue ରେ items ପଛରେ ଯୋଡ଼ି ହୁଅନ୍ତି ଓ ଆଗରୁ ବାହାରନ୍ତି, first in first out। ଆପଣ ଦେଖିବେ ଏହି ଦୁଇ ସରଳ ନିୟମ କିପରି brackets ଯାଞ୍ଚ କରେ, expressions ହିସାବ କରେ, undo ଚଲାଏ, ଏବଂ ଆହୁରି ଅନେକ।',
     'ar': 'مرحبًا بك في المكدسات والطوابير. المكدس يأخذ ويعطي من الأعلى، الداخل أخيرًا يخرج أولًا. والطابور يدخل فيه العنصر من الخلف ويخرج من الأمام، الداخل أولًا يخرج أولًا. سترى كيف تفحص هاتان القاعدتان البسيطتان الأقواس وتحسبان التعابير وتشغلان التراجع وغير ذلك كثيرًا.',
     'de': 'Willkommen bei Stapeln und Warteschlangen. Ein Stapel nimmt und gibt oben, zuletzt hinein, zuerst heraus. In einer Warteschlange stellt man sich hinten an und geht vorne hinaus, zuerst hinein, zuerst heraus. Du siehst, wie diese zwei einfachen Regeln Klammern prüfen, Ausdrücke berechnen, Rückgängig machen ermöglichen und vieles mehr.'},
    {'id': 'stack', 'h': 'The stack',
     'en': 'A stack has three main operations: push adds to the top, peek looks at the top, and pop removes the top. All of them take one step. Popping an empty stack is an error called underflow, so check first.',
     'hi': 'Stack के तीन मुख्य काम हैं: push ऊपर जोड़ता है, peek ऊपर देखता है, और pop ऊपर से हटाता है। सब एक कदम में होते हैं। ख़ाली stack से pop करना underflow नाम की गलती है, इसलिए पहले जाँचें।',
     'kn': 'Stack ನ ಮೂರು ಮುಖ್ಯ ಕೆಲಸಗಳು: push ಮೇಲೆ ಸೇರಿಸುತ್ತದೆ, peek ಮೇಲೆ ನೋಡುತ್ತದೆ, pop ಮೇಲಿನಿಂದ ತೆಗೆಯುತ್ತದೆ. ಎಲ್ಲವೂ ಒಂದೇ ಹೆಜ್ಜೆ. ಖಾಲಿ stack ನಿಂದ pop ಮಾಡುವುದು underflow ಎಂಬ ದೋಷ, ಆದ್ದರಿಂದ ಮೊದಲು ಪರೀಕ್ಷಿಸಿ.',
     'or': 'Stack ର ତିନୋଟି ମୁଖ୍ୟ କାମ: push ଉପରେ ଯୋଡ଼େ, peek ଉପରେ ଦେଖେ, pop ଉପରୁ ହଟାଏ। ସବୁ ଗୋଟିଏ ପାଦରେ ହୁଏ। ଖାଲି stack ରୁ pop କରିବା underflow ନାମକ ତ୍ରୁଟି, ତେଣୁ ପ୍ରଥମେ ଯାଞ୍ଚ କରନ୍ତୁ।',
     'ar': 'للمكدس ثلاث عمليات رئيسية: الدفع يضيف إلى الأعلى، والنظرة ترى الأعلى، والسحب يزيل الأعلى. كلها تستغرق خطوة واحدة. السحب من مكدس فارغ خطأ يسمى النقصان، فتحقق أولًا.',
     'de': 'Ein Stapel hat drei Hauptoperationen: push legt oben drauf, peek schaut oben nach und pop nimmt oben weg. Alle dauern einen Schritt. Von einem leeren Stapel zu nehmen ist ein Fehler namens Unterlauf, also vorher prüfen.'},
    {'id': 'brackets', 'h': 'Matching brackets',
     'en': 'Push every opening bracket. When a closing bracket arrives, the top of the stack must be its partner, so pop it. If the partner is wrong, the stack is empty too early, or something is left at the end, the brackets are not balanced.',
     'hi': 'हर खुलने वाला bracket push करें। जब बंद होने वाला bracket आए, stack के ऊपर उसका साथी होना चाहिए, तो उसे pop करें। अगर साथी गलत हो, stack जल्दी ख़ाली हो जाए, या अंत में कुछ बचा रहे, तो brackets balanced नहीं हैं।',
     'kn': 'ಪ್ರತಿ ತೆರೆಯುವ bracket push ಮಾಡಿ. ಮುಚ್ಚುವ bracket ಬಂದಾಗ stack ನ ಮೇಲೆ ಅದರ ಜೋಡಿ ಇರಬೇಕು, ಅದನ್ನು pop ಮಾಡಿ. ಜೋಡಿ ತಪ್ಪಾದರೆ, stack ಬೇಗ ಖಾಲಿಯಾದರೆ, ಅಥವಾ ಕೊನೆಯಲ್ಲಿ ಏನಾದರೂ ಉಳಿದರೆ brackets balanced ಅಲ್ಲ.',
     'or': 'ପ୍ରତ୍ୟେକ ଖୋଲା bracket push କରନ୍ତୁ। ବନ୍ଦ bracket ଆସିଲେ stack ଉପରେ ତାର ସାଥୀ ଥିବା ଦରକାର, ତାକୁ pop କରନ୍ତୁ। ସାଥୀ ଭୁଲ ହେଲେ, stack ଶୀଘ୍ର ଖାଲି ହେଲେ, କିମ୍ବା ଶେଷରେ କିଛି ରହିଗଲେ brackets balanced ନୁହେଁ।',
     'ar': 'ادفع كل قوس فتح. وعندما يصل قوس إغلاق يجب أن يكون شريكه في أعلى المكدس، فاسحبه. إذا كان الشريك خطأ، أو فرغ المكدس مبكرًا، أو بقي شيء في النهاية، فالأقواس غير متوازنة.',
     'de': 'Lege jede öffnende Klammer auf den Stapel. Kommt eine schließende, muss oben ihr Partner liegen, und du nimmst ihn weg. Ist der Partner falsch, der Stapel zu früh leer oder am Ende noch etwas übrig, sind die Klammern nicht ausgeglichen.'},
    {'id': 'expressions', 'h': 'Expressions',
     'en': 'In postfix notation each operator comes after its two numbers, so no parentheses are needed. Push numbers, and for each operator pop two numbers, compute, and push the result. The shunting yard algorithm turns normal infix expressions into postfix with a stack of operators.',
     'hi': 'Postfix notation में हर operator अपने दो numbers के बाद आता है, इसलिए parentheses की ज़रूरत नहीं। Numbers push करें, और हर operator पर दो numbers pop करके हिसाब लगाएँ और परिणाम push करें। Shunting yard algorithm operators के stack से सामान्य infix को postfix में बदलता है।',
     'kn': 'Postfix notation ನಲ್ಲಿ ಪ್ರತಿ operator ತನ್ನ ಎರಡು numbers ನಂತರ ಬರುತ್ತದೆ, ಹಾಗಾಗಿ parentheses ಬೇಡ. Numbers push ಮಾಡಿ, ಪ್ರತಿ operator ಗೆ ಎರಡು numbers pop ಮಾಡಿ ಲೆಕ್ಕಿಸಿ ಫಲಿತಾಂಶ push ಮಾಡಿ. Shunting yard algorithm operators stack ಬಳಸಿ ಸಾಮಾನ್ಯ infix ಅನ್ನು postfix ಮಾಡುತ್ತದೆ.',
     'or': 'Postfix notation ରେ ପ୍ରତ୍ୟେକ operator ତାର ଦୁଇ numbers ପରେ ଆସେ, ତେଣୁ parentheses ଦରକାର ନାହିଁ। Numbers push କରନ୍ତୁ, ଏବଂ ପ୍ରତ୍ୟେକ operator ପାଇଁ ଦୁଇ numbers pop କରି ହିସାବ କରି ଫଳ push କରନ୍ତୁ। Shunting yard algorithm operators stack ଦ୍ୱାରା ସାଧାରଣ infix କୁ postfix କରେ।',
     'ar': 'في الترميز اللاحق يأتي كل عامل بعد عدديه، فلا نحتاج إلى أقواس. ادفع الأعداد، ومع كل عامل اسحب عددين واحسب وادفع النتيجة. وخوارزمية ساحة التحويل تحوّل التعابير العادية إلى لاحقة باستخدام مكدس للعوامل.',
     'de': 'In der Postfix-Schreibweise steht jeder Operator hinter seinen zwei Zahlen, Klammern sind überflüssig. Lege Zahlen auf den Stapel, und bei jedem Operator nimmst du zwei Zahlen, rechnest und legst das Ergebnis zurück. Der Rangierbahnhof-Algorithmus wandelt normale Infix-Ausdrücke mit einem Operatorstapel in Postfix um.'},
    {'id': 'queue', 'h': 'The queue',
     'en': 'A queue adds at the back and removes from the front. Removing the front of a plain array shifts everything, so use a deque or a circular buffer. A circular buffer keeps a head index and a size, and the remainder operator wraps the indexes around.',
     'hi': 'Queue पीछे जोड़ती है और आगे से हटाती है। साधारण array के आगे से हटाने पर सब कुछ खिसकता है, इसलिए deque या circular buffer लें। Circular buffer एक head index और size रखता है, और remainder operator indexes को घुमा कर शुरुआत में ले आता है।',
     'kn': 'Queue ಹಿಂದೆ ಸೇರಿಸುತ್ತದೆ ಮತ್ತು ಮುಂದೆಯಿಂದ ತೆಗೆಯುತ್ತದೆ. ಸಾಮಾನ್ಯ array ಯ ಮುಂದೆಯಿಂದ ತೆಗೆದರೆ ಎಲ್ಲವೂ ಸರಿಯುತ್ತದೆ, ಆದ್ದರಿಂದ deque ಅಥವಾ circular buffer ಬಳಸಿ. Circular buffer ಒಂದು head index ಮತ್ತು size ಇಡುತ್ತದೆ, remainder operator indexes ಅನ್ನು ಸುತ್ತಿ ಮೊದಲಿಗೆ ತರುತ್ತದೆ.',
     'or': 'Queue ପଛରେ ଯୋଡ଼େ ଏବଂ ଆଗରୁ ହଟାଏ। ସାଧାରଣ array ର ଆଗରୁ ହଟାଇଲେ ସବୁ ଘୁଞ୍ଚେ, ତେଣୁ deque କିମ୍ବା circular buffer ବ୍ୟବହାର କରନ୍ତୁ। Circular buffer ଏକ head index ଓ size ରଖେ, ଏବଂ remainder operator indexes କୁ ଘୂରାଇ ଆରମ୍ଭକୁ ଆଣେ।',
     'ar': 'الطابور يضيف من الخلف ويزيل من الأمام. إزالة أول مصفوفة عادية تزيح كل العناصر، لذلك استخدم طابورًا مزدوجًا أو مخزنًا دائريًا. المخزن الدائري يحفظ موضع الرأس والحجم، وعامل الباقي يعيد المواضع إلى البداية.',
     'de': 'Eine Warteschlange fügt hinten an und entfernt vorne. Vorne aus einem normalen Array zu entfernen verschiebt alles, also nimm eine Deque oder einen Ringpuffer. Ein Ringpuffer merkt sich den Kopfindex und die Größe, und der Restoperator lässt die Indizes wieder vorne beginnen.'},
    {'id': 'deque-priority', 'h': 'Deques and priority queues',
     'en': 'A deque allows adding and removing at both ends in one step. A priority queue hands out the smallest or most urgent item first. It is built on a binary heap, which inserts and removes in logarithmic time.',
     'hi': 'Deque दोनों सिरों पर एक कदम में जोड़ने और हटाने देता है। Priority queue सबसे छोटा या सबसे ज़रूरी item पहले देती है। यह binary heap पर बनी होती है, जो logarithmic समय में insert और remove करता है।',
     'kn': 'Deque ಎರಡೂ ತುದಿಗಳಲ್ಲಿ ಒಂದೇ ಹೆಜ್ಜೆಯಲ್ಲಿ ಸೇರಿಸಲು ಮತ್ತು ತೆಗೆಯಲು ಬಿಡುತ್ತದೆ. Priority queue ಅತಿ ಚಿಕ್ಕ ಅಥವಾ ಅತಿ ತುರ್ತು item ಅನ್ನು ಮೊದಲು ಕೊಡುತ್ತದೆ. ಇದು binary heap ಮೇಲೆ ಕಟ್ಟಲಾಗಿದೆ, ಅದು logarithmic ಸಮಯದಲ್ಲಿ insert ಮತ್ತು remove ಮಾಡುತ್ತದೆ.',
     'or': 'Deque ଦୁଇ ମୁଣ୍ଡରେ ଗୋଟିଏ ପାଦରେ ଯୋଡ଼ିବା ଓ ହଟାଇବାକୁ ଦିଏ। Priority queue ସବୁଠୁ ଛୋଟ କିମ୍ବା ଜରୁରୀ item ପ୍ରଥମେ ଦିଏ। ଏହା binary heap ଉପରେ ତିଆରି, ଯାହା logarithmic ସମୟରେ insert ଓ remove କରେ।',
     'ar': 'الطابور المزدوج يسمح بالإضافة والإزالة من الطرفين في خطوة واحدة. وطابور الأولوية يعطي العنصر الأصغر أو الأكثر إلحاحًا أولًا. وهو مبني على كومة ثنائية تُدرج وتزيل في زمن لوغاريتمي.',
     'de': 'Eine Deque erlaubt Hinzufügen und Entfernen an beiden Enden in einem Schritt. Eine Prioritätswarteschlange gibt das kleinste oder dringendste Element zuerst heraus. Sie basiert auf einem binären Heap, der in logarithmischer Zeit einfügt und entfernt.'},
    {'id': 'monotonic', 'h': 'Monotonic stacks',
     'en': 'A monotonic stack keeps its values in order. For the next greater element, every new value pops all the smaller values waiting on the stack, because it is their answer. Each index is pushed and popped once, so the whole pass is linear.',
     'hi': 'Monotonic stack अपनी values क्रम में रखता है। Next greater element के लिए हर नई value stack पर इंतज़ार कर रही सभी छोटी values को pop कर देती है, क्योंकि वही उनका जवाब है। हर index एक बार push और एक बार pop होता है, इसलिए पूरा काम linear है।',
     'kn': 'Monotonic stack ತನ್ನ values ಅನ್ನು ಕ್ರಮದಲ್ಲಿ ಇಡುತ್ತದೆ. Next greater element ಗೆ ಪ್ರತಿ ಹೊಸ value stack ನಲ್ಲಿ ಕಾಯುತ್ತಿರುವ ಎಲ್ಲಾ ಚಿಕ್ಕ values ಅನ್ನು pop ಮಾಡುತ್ತದೆ, ಏಕೆಂದರೆ ಅದೇ ಅವುಗಳ ಉತ್ತರ. ಪ್ರತಿ index ಒಮ್ಮೆ push ಮತ್ತು ಒಮ್ಮೆ pop ಆಗುತ್ತದೆ, ಆದ್ದರಿಂದ linear.',
     'or': 'Monotonic stack ତାର values କୁ କ୍ରମରେ ରଖେ। Next greater element ପାଇଁ ପ୍ରତ୍ୟେକ ନୂଆ value stack ରେ ଅପେକ୍ଷା କରୁଥିବା ସବୁ ଛୋଟ values କୁ pop କରେ, କାରଣ ତାହା ହିଁ ସେମାନଙ୍କ ଉତ୍ତର। ପ୍ରତ୍ୟେକ index ଥରେ push ଓ ଥରେ pop ହୁଏ, ତେଣୁ ପୂରା କାମ linear।',
     'ar': 'المكدس الرتيب يحفظ قيمه بترتيب. لإيجاد العنصر الأكبر التالي تسحب كل قيمة جديدة كل القيم الأصغر المنتظرة في المكدس، لأنها جوابها. كل موضع يُدفع ويُسحب مرة واحدة، فيكون المرور كله خطيًا.',
     'de': 'Ein monotoner Stapel hält seine Werte geordnet. Für das nächstgrößere Element nimmt jeder neue Wert alle kleineren wartenden Werte vom Stapel, denn er ist ihre Antwort. Jeder Index wird einmal hinein und einmal herausgenommen, also ist der Durchlauf linear.'},
    {'id': 'real-world', 'h': 'Everyday uses',
     'en': 'Undo and redo are two stacks. Each change pushes the old state onto the undo stack, undo moves it to the redo stack, and a new change clears redo. Queues run printers and breadth first search, and priority queues run schedulers.',
     'hi': 'Undo और redo दो stacks हैं। हर बदलाव पुरानी स्थिति को undo stack पर push करता है, undo उसे redo stack पर ले जाता है, और नया बदलाव redo को साफ़ कर देता है। Queues printers और breadth first search चलाती हैं, और priority queues schedulers चलाती हैं।',
     'kn': 'Undo ಮತ್ತು redo ಎರಡು stacks. ಪ್ರತಿ ಬದಲಾವಣೆ ಹಳೆಯ ಸ್ಥಿತಿಯನ್ನು undo stack ಗೆ push ಮಾಡುತ್ತದೆ, undo ಅದನ್ನು redo stack ಗೆ ಸರಿಸುತ್ತದೆ, ಹೊಸ ಬದಲಾವಣೆ redo ಅನ್ನು ಖಾಲಿ ಮಾಡುತ್ತದೆ. Queues printers ಮತ್ತು breadth first search ನಡೆಸುತ್ತವೆ, priority queues schedulers ನಡೆಸುತ್ತವೆ.',
     'or': 'Undo ଓ redo ଦୁଇଟି stacks। ପ୍ରତ୍ୟେକ ପରିବର୍ତ୍ତନ ପୁରୁଣା ସ୍ଥିତିକୁ undo stack ରେ push କରେ, undo ତାକୁ redo stack କୁ ନିଏ, ଏବଂ ନୂଆ ପରିବର୍ତ୍ତନ redo କୁ ଖାଲି କରେ। Queues printers ଓ breadth first search ଚଲାନ୍ତି, ଏବଂ priority queues schedulers ଚଲାନ୍ତି।',
     'ar': 'التراجع والإعادة مكدسان. كل تغيير يدفع الحالة القديمة إلى مكدس التراجع، والتراجع ينقلها إلى مكدس الإعادة، والتغيير الجديد يفرغ الإعادة. الطوابير تشغّل الطابعات والبحث بالعرض، وطوابير الأولوية تشغّل المجدولات.',
     'de': 'Rückgängig und Wiederholen sind zwei Stapel. Jede Änderung legt den alten Zustand auf den Rückgängig-Stapel, Rückgängig verschiebt ihn auf den Wiederholen-Stapel, und eine neue Änderung leert Wiederholen. Warteschlangen steuern Drucker und Breitensuche, Prioritätswarteschlangen steuern Planer.'},
    {'id': 'practice', 'h': 'Practice',
     'en': 'Time to practise. For each problem, ask yourself whether the newest item or the oldest item must be handled first. That tells you whether you need a stack or a queue. Every solution runs in Python, JavaScript and Java.',
     'hi': 'अब अभ्यास का समय है। हर सवाल के लिए ख़ुद से पूछें कि सबसे नया item पहले संभालना है या सबसे पुराना। इससे पता चलता है कि stack चाहिए या queue। हर हल Python, JavaScript और Java में चलता है।',
     'kn': 'ಈಗ ಅಭ್ಯಾಸದ ಸಮಯ. ಪ್ರತಿ ಸಮಸ್ಯೆಗೆ ಹೊಸ item ಮೊದಲು ನಿರ್ವಹಿಸಬೇಕೇ ಅಥವಾ ಹಳೆಯದೇ ಎಂದು ಕೇಳಿಕೊಳ್ಳಿ. ಅದು stack ಬೇಕೇ queue ಬೇಕೇ ಎಂದು ಹೇಳುತ್ತದೆ. ಪ್ರತಿ ಪರಿಹಾರ Python, JavaScript ಮತ್ತು Java ದಲ್ಲಿ ಚಲಿಸುತ್ತದೆ.',
     'or': 'ଏବେ ଅଭ୍ୟାସର ସମୟ। ପ୍ରତ୍ୟେକ ସମସ୍ୟା ପାଇଁ ନିଜକୁ ପଚାରନ୍ତୁ ସବୁଠୁ ନୂଆ item ପ୍ରଥମେ ସମ୍ଭାଳିବାକୁ ପଡ଼ିବ ନା ସବୁଠୁ ପୁରୁଣା। ଏହା କହେ stack ଦରକାର ନା queue। ପ୍ରତ୍ୟେକ ସମାଧାନ Python, JavaScript ଓ Java ରେ ଚାଲେ।',
     'ar': 'حان وقت التدريب. في كل مسألة اسأل نفسك هل يجب معالجة أحدث عنصر أولًا أم أقدم عنصر. هذا يخبرك هل تحتاج مكدسًا أم طابورًا. كل حل يعمل بلغات بايثون وجافاسكربت وجافا.',
     'de': 'Zeit zum Üben. Frag dich bei jeder Aufgabe, ob das neueste oder das älteste Element zuerst behandelt werden muss. Das sagt dir, ob du einen Stapel oder eine Warteschlange brauchst. Jede Lösung läuft in Python, JavaScript und Java.'},
]

PRACTICE = [
    {'id': 'remove-adjacent', 'lv': 'e', 'title': 'Remove adjacent duplicates', 'code': 'p_remove_adjacent',
     'statement': '<p>Repeatedly delete two equal letters that stand next to each other until no such pair remains. Return what is left.</p>',
     'example': 'Input: "abbaca"  →  "ca"   (remove bb, then aa)\nInput: "azxxzy"  →  "ay"',
     'hint': 'Removing a pair can bring two new equal letters together. The most recent letter is the only one that can pair with the next.',
     'approach': '<p>Walk the letters with a stack. If the top equals the current letter, pop it, because the pair cancels. Otherwise push. The stack holds the answer from bottom to top.</p>',
     'time': 'O(n)', 'space': 'O(n)'},
    {'id': 'josephus', 'lv': 'e', 'title': 'Hot potato: who is left', 'code': 'p_josephus',
     'statement': '<p>n people stand in a circle numbered 1 to n. Counting starts at person 1, and every k-th person leaves. Print the order in which people leave and the last one standing.</p>',
     'example': 'Input: n = 7, k = 3\nOutput: out: 3 6 2 7 5 1   survivor: 4',
     'hint': 'Passing the potato is the same as taking the front person and putting them at the back.',
     'approach': '<p>Put everyone in a queue. Move k − 1 people from the front to the back, then remove the person at the front. Repeat until one person is left. In JavaScript a head index avoids the O(n) cost of <code>shift()</code>.</p>',
     'time': 'O(n · k)', 'space': 'O(n)'},
    {'id': 'min-stack', 'lv': 'm', 'title': 'A stack that knows its minimum', 'code': 'p_min_stack',
     'statement': '<p>Design a stack with push, pop and <code>getMin</code>, where all three run in O(1).</p>',
     'example': 'push 5, 3, 7, 2  →  getMin = 2\npop               →  getMin = 3\npop, pop          →  getMin = 5',
     'hint': 'Keep a second stack that remembers the minimum at every height of the first stack.',
     'approach': '<p>Every push also pushes <code>min(x, current minimum)</code> onto a second stack. Every pop pops both. The top of the second stack is always the minimum of what is left, so nothing ever needs to be recomputed.</p>',
     'time': 'O(1) per operation', 'space': 'O(n)'},
    {'id': 'simplify-path', 'lv': 'm', 'title': 'Simplify a file path', 'code': 'p_simplify_path',
     'statement': '<p>Turn a Unix style path into its shortest form. "." means the current folder, ".." means go up one folder, and repeated slashes count as one.</p>',
     'example': 'Input: "/home//user/./docs/../music/"  →  "/home/user/music"\nInput: "/../"                          →  "/"',
     'hint': 'Split on "/" and treat the folder names as a stack.',
     'approach': '<p>Skip empty pieces and ".". For "..", pop the last folder if there is one. Push every other name. Join the stack with "/" and put a "/" in front.</p>',
     'time': 'O(n)', 'space': 'O(n)'},
    {'id': 'decode-string', 'lv': 'h', 'title': 'Decode a repeated string', 'code': 'p_decode_string',
     'statement': '<p>A string like <code>3[a2[c]]</code> means "repeat what is inside the brackets that many times". Brackets can be nested. Return the decoded string.</p>',
     'example': 'Input: "3[a2[c]]"   →  "accaccacc"\nInput: "2[ab]3[x]"  →  "ababxxx"',
     'hint': 'When you meet "[", you must remember the count and the text built so far, then start fresh.',
     'approach': '<p>Use two stacks: one for counts and one for the text before each "[". Digits build the count. "[" pushes both and resets. "]" pops the saved text and the count, and the new current text is saved text + current × count.</p>',
     'time': 'O(length of the output)', 'space': 'O(length of the output)'},
    {'id': 'largest-rectangle', 'lv': 'h', 'title': 'Largest rectangle in a histogram', 'code': 'p_largest_rect',
     'statement': '<p>Bars of width 1 have the given heights. Find the area of the largest rectangle that fits inside the histogram.</p>',
     'example': 'Input: [2, 1, 5, 6, 2, 3]  →  10   (heights 5 and 6, width 2)',
     'hint': 'For each bar, the widest rectangle of its height stretches until a lower bar on each side. A monotonic stack finds both.',
     'approach': '<p>Keep indexes of increasing heights on a stack. When a lower bar arrives at i, pop the taller bars. A popped bar of height h stretches from just after the new top of the stack up to i − 1, so its area is h × (i − left). A final bar of height 0 flushes the stack.</p>',
     'time': 'O(n)', 'space': 'O(n)'},
    {'id': 'window-max', 'lv': 'x', 'title': 'Sliding window maximum', 'code': 'p_window_max',
     'statement': '<p>For every window of k consecutive numbers, report the largest one.</p>',
     'example': 'Input: [1, 3, -1, -3, 5, 3, 6, 7], k = 3\nOutput: [3, 3, 5, 5, 6, 7]',
     'hint': 'If a newer value is bigger than an older one, the older one can never be a maximum again.',
     'approach': '<p>Keep a deque of indexes whose values decrease from front to back. Before adding i, pop smaller values from the back. If the front index has left the window, pop it from the front. The front is always the maximum of the current window. Each index enters and leaves once.</p>',
     'time': 'O(n)', 'space': 'O(k)'},
    {'id': 'calculator', 'lv': 'x', 'title': 'A calculator with precedence and parentheses', 'code': 'p_calculator',
     'statement': '<p>Evaluate an expression with non negative integers, + − * /, parentheses and spaces. Division cuts toward zero.</p>',
     'example': 'Input: "3 + 2 * (4 - 1)"   →  9\nInput: "(8 + 4) / 3 - 1"   →  3',
     'hint': 'Combine the shunting yard idea with postfix evaluation: keep one stack of numbers and one stack of operators.',
     'approach': '<p>Numbers go onto the number stack. Before pushing an operator, apply every operator on top with greater or equal precedence. "(" is pushed, and ")" applies operators until the matching "(". At the end, apply what is left. Applying pops two numbers and pushes the result.</p>',
     'time': 'O(n)', 'space': 'O(n)'},
]

QUIZ = [
    {'lv': 'e', 'q': 'A stack follows which rule?', 'o': ['First in, first out', 'Last in, first out', 'Smallest first', 'Random order'], 'a': 1, 'hint': 'Think of a pile of plates.', 'why': 'You can only take the plate on top, which is the one added last.'},
    {'lv': 'e', 'q': 'You push 1, 2, 3 onto a stack and pop once. What comes out?', 'o': ['1', '2', '3', 'Nothing'], 'a': 2, 'hint': 'The newest item is on top.', 'why': '3 was pushed last, so it is popped first.'},
    {'lv': 'e', 'q': 'You enqueue 1, 2, 3 into a queue and dequeue once. What comes out?', 'o': ['1', '2', '3', 'Nothing'], 'a': 0, 'hint': 'Think of a line at a counter.', 'why': '1 joined first, so it leaves first.'},
    {'lv': 'e', 'q': 'What is the cost of push and pop on a stack built on a dynamic array?', 'o': ['O(1) amortized', 'O(log n)', 'O(n)', 'O(n²)'], 'a': 0, 'hint': 'Both work at the end of the array.', 'why': 'The top is the end of the array, so nothing shifts. Growing the array occasionally is paid off over many pushes.'},
    {'lv': 'm', 'q': 'Why is list.pop(0) in Python a bad way to dequeue?', 'o': ['It removes the last item', 'It shifts every other item, which is O(n)', 'It is not allowed', 'It sorts the list'], 'a': 1, 'hint': 'What happens to the remaining items?', 'why': 'All the other items move one place left. collections.deque.popleft() is O(1).'},
    {'lv': 'm', 'q': 'What is the value of the postfix expression 5 1 2 + 4 * + 3 −?', 'o': ['14', '12', '18', '9'], 'a': 0, 'hint': 'Push numbers, apply operators to the top two.', 'why': '1 + 2 = 3, 3 × 4 = 12, 5 + 12 = 17, 17 − 3 = 14.'},
    {'lv': 'm', 'q': 'A circular buffer of capacity 5 has head = 3 and size = 4. Where does the next item go?', 'o': ['Index 7', 'Index 2', 'Index 0', 'It is full'], 'a': 1, 'hint': 'tail = (head + size) mod capacity', 'why': '<span class="eq">(3 + 4) mod 5 = 2</span>'},
    {'lv': 'm', 'q': 'Which structure does breadth first search use?', 'o': ['Stack', 'Queue', 'Priority queue', 'Hash set only'], 'a': 1, 'hint': 'It visits the nearest places first.', 'why': 'Places discovered first are explored first, which is first in, first out.'},
    {'lv': 'h', 'q': 'What is the postfix form of 2 + 3 * 4?', 'o': ['2 3 + 4 *', '2 3 4 * +', '+ 2 * 3 4', '2 3 4 + *'], 'a': 1, 'hint': 'Multiplication binds tighter than addition.', 'why': '3 * 4 must be computed first, so it becomes 3 4 *, and then 2 is added: 2 3 4 * +.'},
    {'lv': 'h', 'q': 'The next greater element loop has a while inside a for. Why is it still O(n)?', 'o': ['The while never runs', 'Each index is pushed once and popped at most once', 'The input is sorted', 'It uses binary search'], 'a': 1, 'hint': 'Count the total number of pops over the whole run.', 'why': 'The while loop can pop at most n items in total, across all iterations of the for loop.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'from collections import deque\nd = deque([1, 2, 3])\nd.rotate(1)\nprint(d[0])', 'o': ['1', '2', '3', 'Error'], 'a': 2, 'hint': 'rotate(1) moves the last item to the front.', 'why': 'After rotate(1) the deque is [3, 1, 2], so d[0] is 3.'},
    {'lv': 'h', 'q': 'Which is the recommended stack class in modern Java?', 'o': ['java.util.Stack', 'java.util.ArrayDeque', 'java.util.Vector', 'java.util.TreeSet'], 'a': 1, 'hint': 'The old one is synchronized.', 'why': 'ArrayDeque is faster than the legacy Stack class and works as both a stack and a queue.'},
    {'lv': 'x', 'q': 'A queue is built from two stacks (in and out). What is the amortized cost of dequeue?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], 'a': 0, 'hint': 'Each item moves from in to out at most once.', 'why': 'An item is pushed and popped at most twice in total, so n operations cost O(n) overall.'},
    {'lv': 'x', 'q': 'In the sliding window maximum, why can a smaller value at the back of the deque be thrown away?', 'o': ['It is out of the window', 'A newer, bigger value will outlive it in every future window', 'It is a duplicate', 'Deques cannot hold small values'], 'a': 1, 'hint': 'Compare how long each value stays in future windows.', 'why': 'The newer value stays at least as long and is bigger, so the older smaller one can never be the maximum.'},
    {'lv': 'x', 'q': 'A min heap holds 1, 3, 5, 8 in an array [1, 3, 5, 8]. Where are the children of index 1?', 'o': ['Indexes 2 and 3', 'Indexes 3 and 4', 'Indexes 1 and 2', 'Index 0'], 'a': 1, 'hint': 'Children of i are 2i + 1 and 2i + 2.', 'why': '<span class="eq">2 × 1 + 1 = 3 and 2 × 1 + 2 = 4</span> Only index 3 exists here, holding 8.'},
    {'lv': 'x', 'q': 'How many times is the largest rectangle stack popped in total for n bars?', 'o': ['Exactly n times', 'At most n times, plus the final flush, so O(n)', 'n² times', 'log n times'], 'a': 1, 'hint': 'Every index is pushed once.', 'why': 'Something can only be popped after being pushed, and each of the n + 1 indexes is pushed once.'},
]

CALC = [
    {'lv': 'e', 'q': 'Start with an empty stack. Push 4, push 9, pop, push 2, push 7, pop, pop. What is on top now?', 'ans': '4', 'hint': 'Write the stack after each step.', 'steps': ['[4] → [4, 9] → [4] → [4, 2] → [4, 2, 7] → [4, 2] → [4]', 'The top is <span class="eq">4</span>']},
    {'lv': 'e', 'q': 'A queue receives enqueue 5, 6, 7, then dequeue twice. How many items are left?', 'ans': '1', 'hint': 'Count in, count out.', 'steps': ['<span class="eq">3 − 2 = 1</span>', 'Only 7 is left.']},
    {'lv': 'm', 'q': 'Evaluate the postfix expression 6 2 / 3 *', 'ans': '9', 'hint': 'Pop the right operand first.', 'steps': ['6 2 / gives <span class="eq">6 ÷ 2 = 3</span>', 'then 3 3 * gives <span class="eq">3 × 3 = 9</span>']},
    {'lv': 'm', 'q': 'A ring buffer has capacity 8, head = 6 and size = 5. At which index is the last item?', 'ans': '2', 'hint': 'The last item is at (head + size − 1) mod capacity.', 'steps': ['<span class="eq">(6 + 5 − 1) mod 8 = 10 mod 8 = 2</span>']},
    {'lv': 'h', 'q': 'What is the largest rectangle area in the histogram [2, 4, 4, 1]?', 'ans': '8', 'hint': 'Try each bar\'s height and see how far it stretches.', 'steps': ['Height 4 stretches over the two 4s: <span class="eq">4 × 2 = 8</span>', 'Height 2 stretches over the first three bars: <span class="eq">2 × 3 = 6</span>', 'Height 1 covers all four: <span class="eq">1 × 4 = 4</span>', 'The largest is 8.']},
    {'lv': 'h', 'q': 'For [2, 7, 3, 5, 4, 6, 8], what is the next greater element of 3?', 'ans': '5', 'hint': 'Look to the right of 3 for the first bigger value.', 'steps': ['To the right of 3 come 5, 4, 6, 8.', 'The first one bigger than 3 is <span class="eq">5</span>']},
    {'lv': 'x', 'q': 'A queue made of two stacks receives 100 enqueues and then 100 dequeues. How many single pushes and pops happen in total?', 'ans': '400', 'hint': 'Each item: push in, pop in, push out, pop out.', 'steps': ['Each item is touched 4 times.', '<span class="eq">100 × 4 = 400</span>', 'That is 2 per operation on average, so O(1) amortized.']},
    {'lv': 'x', 'q': 'How many levels does a binary heap of 100 items have?', 'ans': '7', 'hint': 'A full heap with L levels holds up to 2^L − 1 items.', 'steps': ['<span class="eq">2⁶ − 1 = 63 &lt; 100 ≤ 127 = 2⁷ − 1</span>', 'So the heap needs 7 levels, and insert or remove takes at most about 6 swaps.']},
]

VIZ_JS = r'''
(() => {
  const { esc, $, shell, seg, wireSeg, Player, Seq, cell } = VIZ.kit;
  const W = VIZ.widgets;
  const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
  const plates = (a, hl = {}) => `<div class="vz-stack">${a.map((v, k) => `<div class="vz-plate ${hl[k] || ''}">${esc(v)}${k === a.length - 1 ? '<small>top</small>' : ''}</div>`).join('')}</div>`;

  W.sqplay = el => {
    const b = shell(el, 'Stack, queue and deque side by side', 'Pick a structure and press the buttons. Watch which end each operation uses.');
    b.innerHTML = `<div class="vz-row">${seg('k', [['stack', '🥞 Stack'], ['queue', '🚶 Queue'], ['deque', '↔️ Deque']], 'stack')}</div><div class="vz-ops"></div><div class="vz-stage"></div><div class="vz-msg" aria-live="polite"></div>`;
    const ops = $('.vz-ops', b), stage = $('.vz-stage', b), msg = $('.vz-msg', b), seq = Seq();
    let kind = 'stack', a = [];
    const draw = (hl = {}) => {
      if (kind === 'stack') stage.innerHTML = plates(a, hl);
      else stage.innerHTML = `<div class="vz-q"><span class="vz-tag">front</span><div class="vz-cells vz-big">${a.map((v, k) => cell(v, hl[k] || '')).join('') || '<span class="vz-note">empty</span>'}</div><span class="vz-tag">back</span></div>`;
    };
    const say = h => { msg.innerHTML = h; };
    function open(k) {
      kind = k; seq.stop();
      a = k === 'stack' ? [4, 8] : [3, 9, 1];
      ops.innerHTML = k === 'stack' ? '<button data-op="push">Push</button><button data-op="pop">Pop</button><button data-op="peek">Peek</button>'
        : k === 'queue' ? '<button data-op="pushBack">Enqueue at back</button><button data-op="popFront">Dequeue from front</button><button data-op="peekFront">Peek at front</button>'
        : '<button data-op="pushFront">Add at front</button><button data-op="pushBack">Add at back</button><button data-op="popFront">Remove front</button><button data-op="popBack">Remove back</button>';
      draw();
      say(k === 'stack' ? 'Everything happens at the top: last in, first out.' : k === 'queue' ? 'Join at the back, leave from the front: first in, first out.' : 'A deque works at both ends, so it can be a stack and a queue at once.');
    }
    ops.addEventListener('click', e => {
      const op = (e.target.closest('button') || {}).dataset?.op;
      if (!op) return;
      seq.stop();
      const full = a.length >= 7, v = rand(1, 99);
      if ((op === 'push' || op.startsWith('push')) && full) return say('The demo is full. Remove something first.');
      if ((op === 'pop' || op.startsWith('pop') || op.startsWith('peek')) && !a.length) return say('It is empty. Removing now would be an underflow error.');
      if (op === 'push') { a.push(v); draw({ [a.length - 1]: 'ok' }); say(`Pushed ${v} on top. <b>O(1)</b>.`); }
      if (op === 'pop') { draw({ [a.length - 1]: 'bad' }); seq.run([() => {}, () => { const x = a.pop(); draw(); say(`Popped ${x}, the newest item. <b>O(1)</b>.`); }], 450); }
      if (op === 'peek') { draw({ [a.length - 1]: 'hl' }); say(`The top is ${a[a.length - 1]}. Peeking does not remove it.`); }
      if (op === 'pushBack') { a.push(v); draw({ [a.length - 1]: 'ok' }); say(`${v} joined at the back. <b>O(1)</b>.`); }
      if (op === 'pushFront') { a.unshift(v); draw({ 0: 'ok' }); say(`${v} was added at the front. <b>O(1)</b> in a real deque.`); }
      if (op === 'popFront') { draw({ 0: 'bad' }); seq.run([() => {}, () => { const x = a.shift(); draw(); say(`${x} left from the front${kind === 'queue' ? ', the item that waited longest' : ''}. <b>O(1)</b>.`); }], 450); }
      if (op === 'popBack') { draw({ [a.length - 1]: 'bad' }); seq.run([() => {}, () => { const x = a.pop(); draw(); say(`${x} was removed from the back. <b>O(1)</b>.`); }], 450); }
      if (op === 'peekFront') { draw({ 0: 'hl' }); say(`Next in line: ${a[0]}.`); }
    });
    wireSeg(b, 'k', open);
    open('stack');
  };

  W.brackets = el => {
    const b = shell(el, 'Watch the stack check brackets', 'Openers are pushed. Each closer must find its partner on top of the stack.');
    b.innerHTML = `<div class="vz-row">${seg('w', [['{[()()]}', '{[()()]}'], ['([)]', '([)]'], ['(()', '(()'], ['())', '())']], '{[()()]}')}</div><div class="vz-two"><div><h4>Input</h4><div class="vz-cells vz-big vz-chars"></div></div><div><h4>Stack</h4><div class="vz-sbox"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const PAIR = { ')': '(', ']': '[', '}': '{' };
    let s = '{[()()]}', steps = [];
    const P = Player($('.vz-p', b), show, 750);
    function setup() {
      steps = [{ i: -1, st: [], msg: 'Read the characters one by one.' }];
      const st = [];
      for (let i = 0; i < s.length; i++) {
        const c = s[i];
        if ('([{'.includes(c)) { st.push(c); steps.push({ i, st: st.slice(), push: 1, msg: `"${c}" opens, so push it.` }); }
        else if (!st.length) { steps.push({ i, st: [], bad: 1, msg: `"${c}" closes, but the stack is empty. <b>Not balanced.</b>` }); return P.load(steps.length); }
        else if (st[st.length - 1] !== PAIR[c]) { steps.push({ i, st: st.slice(), bad: 1, msg: `"${c}" needs "${PAIR[c]}" on top, but the top is "${st[st.length - 1]}". <b>Not balanced.</b>` }); return P.load(steps.length); }
        else { st.pop(); steps.push({ i, st: st.slice(), msg: `"${c}" matches the "${PAIR[c]}" on top, so pop it.` }); }
      }
      steps.push({ i: s.length, st: st.slice(), bad: st.length > 0, fin: 1, msg: st.length ? `The input ended with ${st.length} opener${st.length > 1 ? 's' : ''} still waiting. <b>Not balanced.</b>` : 'The input ended and the stack is empty. <b>Balanced!</b>' });
      P.load(steps.length);
    }
    function show(k) {
      const st = steps[k];
      $('.vz-chars', b).innerHTML = [...s].map((c, x) => cell(c, x < st.i ? 'dim' : x === st.i ? (st.bad ? 'bad' : 'hl') : '')).join('');
      $('.vz-sbox', b).innerHTML = plates(st.st, st.push ? { [st.st.length - 1]: 'ok' } : st.bad && st.st.length ? { [st.st.length - 1]: 'bad' } : {});
      $('.vz-msg', b).innerHTML = st.msg;
    }
    wireSeg(b, 'w', v => { s = v; setup(); });
    setup();
  };

  W.ring = el => {
    const b = shell(el, 'A queue in a ring buffer', 'Six slots, a head index and a size. Indexes wrap around with the remainder operator, so slots are reused forever.');
    b.innerHTML = `<div class="vz-ops"><button data-op="enq">Enqueue</button><button data-op="deq">Dequeue</button></div><div class="vz-stage"></div><div class="vz-msg" aria-live="polite"></div>`;
    const N = 6, buf = Array(N).fill(null);
    let head = 0, size = 0, next = 1;
    const stage = $('.vz-stage', b), msg = $('.vz-msg', b);
    function draw(hi = -1, cls = '') {
      let s = '';
      for (let i = 0; i < N; i++) {
        const ang = -Math.PI / 2 + i * 2 * Math.PI / N, x = 150 + 95 * Math.cos(ang), y = 125 + 95 * Math.sin(ang);
        const used = buf[i] !== null;
        const c = i === hi ? cls : used ? (i === head ? 'hl' : 'ok') : '';
        s += `<g class="vz-tn ${c}"><rect x="${x - 24}" y="${y - 18}" width="48" height="36" rx="9"/><text x="${x}" y="${y + 5}">${used ? buf[i] : ''}</text></g><text class="vz-tick" x="${150 + 62 * Math.cos(ang)}" y="${125 + 62 * Math.sin(ang) + 4}" text-anchor="middle">${i}</text>`;
      }
      const tail = (head + size) % N;
      const lab = (i, t, dy) => { const ang = -Math.PI / 2 + i * 2 * Math.PI / N; return `<text class="vz-rl" x="${150 + 140 * Math.cos(ang)}" y="${125 + 140 * Math.sin(ang) + dy}" text-anchor="middle">${t}</text>`; };
      s += lab(head, 'head', 0) + (size < N ? lab(tail, 'tail', head === tail ? 14 : 0) : '');
      stage.innerHTML = `<div class="vz-scroll"><svg class="vz-svg" viewBox="-10 -30 320 310" style="min-width:260px; max-width:360px; margin:0 auto">${s}</svg></div><div class="vz-note">head = ${head} · size = ${size} · tail = (head + size) mod ${N} = ${(head + size) % N}</div>`;
    }
    draw();
    msg.innerHTML = 'Press Enqueue a few times, then Dequeue, then Enqueue again to see the wrap around.';
    b.querySelector('.vz-ops').addEventListener('click', e => {
      const op = (e.target.closest('button') || {}).dataset?.op;
      if (op === 'enq') {
        if (size === N) { draw(); msg.innerHTML = 'All six slots are used. The queue is <b>full</b>.'; return; }
        const t = (head + size) % N;
        buf[t] = next++; size++;
        draw(t, 'mv');
        msg.innerHTML = `New item goes to slot (${head} + ${size - 1}) mod ${N} = <b>${t}</b>. ${t < head ? 'It wrapped around to the start.' : ''}`;
      }
      if (op === 'deq') {
        if (!size) { draw(); msg.innerHTML = 'The queue is empty.'; return; }
        const v = buf[head], old = head;
        buf[head] = null; head = (head + 1) % N; size--;
        draw(old, 'bad');
        msg.innerHTML = `Removed ${v} from slot ${old}. head becomes (${old} + 1) mod ${N} = <b>${head}</b>. Nothing shifted.`;
      }
    });
  };

  W.mono = el => {
    const b = shell(el, 'Next greater element with a monotonic stack', 'Indexes wait on the stack. A bigger value answers every smaller value waiting on top.');
    b.innerHTML = `<div class="vz-two"><div><h4>Array and answers</h4><div class="vz-scroll"><div class="vz-cells vz-big vz-arr"></div><div class="vz-cells vz-big vz-res"></div></div></div><div><h4>Stack (values waiting)</h4><div class="vz-sbox"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const a = [4, 5, 2, 25, 7, 8], steps = [];
    const res = Array(a.length).fill(null), st = [];
    steps.push({ i: -1, st: [], res: res.slice(), msg: 'Walk from left to right with an empty stack.' });
    for (let i = 0; i < a.length; i++) {
      while (st.length && a[st[st.length - 1]] < a[i]) {
        const j = st.pop(); res[j] = a[i];
        steps.push({ i, st: st.slice(), res: res.slice(), pop: j, msg: `${a[i]} is bigger than ${a[j]} waiting on top, so the answer for ${a[j]} is <b>${a[i]}</b>. Pop it.` });
      }
      st.push(i);
      steps.push({ i, st: st.slice(), res: res.slice(), msg: `Push ${a[i]}. It waits for something bigger.` });
    }
    st.forEach(j => { res[j] = -1; });
    steps.push({ i: a.length, st: [], res: res.slice(), msg: 'The end. Whatever is still waiting has no bigger value to its right: −1.' });
    const P = Player($('.vz-p', b), show, 850);
    function show(k) {
      const s = steps[k];
      $('.vz-arr', b).innerHTML = a.map((v, x) => cell(v, x === s.i ? 'hl' : x === s.pop ? 'ok' : s.st.includes(x) ? 'sel' : '', x)).join('');
      $('.vz-res', b).innerHTML = s.res.map(v => cell(v === null ? '' : v, v === null ? 'empty' : v < 0 ? 'dim' : 'ok', ' ')).join('');
      $('.vz-sbox', b).innerHTML = plates(s.st.map(x => a[x]));
      $('.vz-msg', b).innerHTML = s.msg;
    }
    P.load(steps.length);
  };
})();
'''

CSS = r'''
.vz-sbox .vz-stack{margin:0}
.vz-rl{font:800 12px var(--font-mono); fill:var(--accent-deep)}
.vz-res{margin-top:4px}
'''

T = {
    'slug': 'stacks-queues', 'title': 'Stacks and Queues', 'short': 'Stacks and queues', 'emoji': '🥞', 'topic': 'stacks-queues', 'prefix': 'dsasq',
    'module': ('🚃', 'Linear structures'),
    'lead': 'Two of the simplest structures in computing, and two of the most used. A stack hands back the newest item first, a queue hands back the oldest. This page builds both, then uses them to match brackets, evaluate expressions, run ring buffers, find next greater elements and power undo and redo.',
    'desc': 'Stacks and queues in DSA: LIFO and FIFO, balanced brackets, postfix evaluation and the shunting yard algorithm, circular buffers, deques and priority queues, monotonic stacks, and undo and redo, with code in Python, JavaScript and Java.',
    'minutes': 13,
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'practice': PRACTICE, 'quiz': QUIZ, 'calc': CALC,
    'viz': VIZ_JS, 'css': CSS,
    'prev': ('linked-lists', 'linked-lists', '🔗 Linked lists'),
    'next': ('trees', 'trees', '🌲 Trees'),
}
