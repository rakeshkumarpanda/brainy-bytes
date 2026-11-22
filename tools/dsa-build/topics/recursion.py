# Recursion: base and recursive cases, the call stack, recursion trees and memoization, thinking recursively,
# the Tower of Hanoi, recursion on nested data and trees, and turning recursion into loops.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('factorial', py=r'''
def factorial(n):
    if n <= 1:                       # base case: the smallest doll, nothing inside
        return 1
    return n * factorial(n - 1)      # recursive case: a smaller copy of the same problem


def countdown(n):
    if n == 0:
        print("liftoff")
        return
    print(n)
    countdown(n - 1)                 # the same job, one step closer to the base case


print("5! =", factorial(5))
countdown(3)
''', js=r'''
function factorial(n) {
  if (n <= 1) return 1;              // base case: the smallest doll, nothing inside
  return n * factorial(n - 1);       // recursive case: a smaller copy of the same problem
}

function countdown(n) {
  if (n === 0) {
    console.log("liftoff");
    return;
  }
  console.log(n);
  countdown(n - 1);                  // the same job, one step closer to the base case
}

console.log("5! =", factorial(5));
countdown(3);
''', java=r'''
public class Factorial {
    static long factorial(int n) {
        if (n <= 1) return 1;                // base case: the smallest doll, nothing inside
        return n * factorial(n - 1);         // recursive case: a smaller copy of the same problem
    }

    static void countdown(int n) {
        if (n == 0) {
            System.out.println("liftoff");
            return;
        }
        System.out.println(n);
        countdown(n - 1);                    // the same job, one step closer to the base case
    }

    public static void main(String[] args) {
        System.out.println("5! = " + factorial(5));
        countdown(3);
    }
}
''', ts=r'''
function factorial(n: number): number {
  if (n <= 1) return 1;              // base case: the smallest doll, nothing inside
  return n * factorial(n - 1);       // recursive case: a smaller copy of the same problem
}

function countdown(n: number): void {
  if (n === 0) {
    console.log("liftoff");
    return;
  }
  console.log(n);
  countdown(n - 1);                  // the same job, one step closer to the base case
}

console.log("5! =", factorial(5));
countdown(3);
''')

t.code('callstack', py=r'''
def total(nums, i, depth):
    pad = "  " * depth                       # indent by how deep the call stack is
    if i == len(nums):
        print(pad + "end of list, return 0")
        return 0
    print(pad + "index " + str(i) + " waits for the rest")
    result = nums[i] + total(nums, i + 1, depth + 1)   # this frame pauses here
    print(pad + "index " + str(i) + " returns " + str(result))
    return result


print("sum =", total([4, 2, 7], 0, 0))
''', js=r'''
function total(nums, i, depth) {
  const pad = "  ".repeat(depth);            // indent by how deep the call stack is
  if (i === nums.length) {
    console.log(pad + "end of list, return 0");
    return 0;
  }
  console.log(pad + "index " + i + " waits for the rest");
  const result = nums[i] + total(nums, i + 1, depth + 1);  // this frame pauses here
  console.log(pad + "index " + i + " returns " + result);
  return result;
}

console.log("sum =", total([4, 2, 7], 0, 0));
''', java=r'''
public class CallStack {
    static int total(int[] nums, int i, int depth) {
        String pad = "  ".repeat(depth);           // indent by how deep the call stack is
        if (i == nums.length) {
            System.out.println(pad + "end of list, return 0");
            return 0;
        }
        System.out.println(pad + "index " + i + " waits for the rest");
        int result = nums[i] + total(nums, i + 1, depth + 1);   // this frame pauses here
        System.out.println(pad + "index " + i + " returns " + result);
        return result;
    }

    public static void main(String[] args) {
        System.out.println("sum = " + total(new int[]{4, 2, 7}, 0, 0));
    }
}
''', ts=r'''
function total(nums: number[], i: number, depth: number): number {
  const pad = "  ".repeat(depth);            // indent by how deep the call stack is
  if (i === nums.length) {
    console.log(pad + "end of list, return 0");
    return 0;
  }
  console.log(pad + "index " + i + " waits for the rest");
  const result = nums[i] + total(nums, i + 1, depth + 1);  // this frame pauses here
  console.log(pad + "index " + i + " returns " + result);
  return result;
}

console.log("sum =", total([4, 2, 7], 0, 0));
''')

t.code('fib_calls', py=r'''
calls = 0


def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)   # two calls, and they repeat each other's work


memo = {}


def fib_memo(n):
    global calls
    calls += 1
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib_memo(n - 1) + fib_memo(n - 2)   # solve each n only once
    return memo[n]


print("plain fib(12) =", fib(12), "with", calls, "calls")
calls = 0
print("memo  fib(12) =", fib_memo(12), "with", calls, "calls")
''', js=r'''
let calls = 0;

function fib(n) {
  calls++;
  if (n < 2) return n;
  return fib(n - 1) + fib(n - 2);    // two calls, and they repeat each other's work
}

const memo = new Map();

function fibMemo(n) {
  calls++;
  if (n < 2) return n;
  if (!memo.has(n)) memo.set(n, fibMemo(n - 1) + fibMemo(n - 2));  // solve each n only once
  return memo.get(n);
}

console.log("plain fib(12) =", fib(12), "with", calls, "calls");
calls = 0;
console.log("memo  fib(12) =", fibMemo(12), "with", calls, "calls");
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class FibCalls {
    static int calls = 0;
    static Map<Integer, Integer> memo = new HashMap<>();

    static int fib(int n) {
        calls++;
        if (n < 2) return n;
        return fib(n - 1) + fib(n - 2);      // two calls, and they repeat each other's work
    }

    static int fibMemo(int n) {
        calls++;
        if (n < 2) return n;
        if (!memo.containsKey(n)) memo.put(n, fibMemo(n - 1) + fibMemo(n - 2));  // solve each n only once
        return memo.get(n);
    }

    public static void main(String[] args) {
        System.out.println("plain fib(12) = " + fib(12) + " with " + calls + " calls");
        calls = 0;
        System.out.println("memo  fib(12) = " + fibMemo(12) + " with " + calls + " calls");
    }
}
''', ts=r'''
let calls: number = 0;

function fib(n: number): number {
  calls++;
  if (n < 2) return n;
  return fib(n - 1) + fib(n - 2);    // two calls, and they repeat each other's work
}

const memo = new Map<number, number>();

function fibMemo(n: number): number {
  calls++;
  if (n < 2) return n;
  if (!memo.has(n)) memo.set(n, fibMemo(n - 1) + fibMemo(n - 2));  // solve each n only once
  return memo.get(n)!;
}

console.log("plain fib(12) =", fib(12), "with", calls, "calls");
calls = 0;
console.log("memo  fib(12) =", fibMemo(12), "with", calls, "calls");
''')

t.code('think', py=r'''
def reverse(s):
    if len(s) <= 1:
        return s
    return reverse(s[1:]) + s[0]          # reverse the rest, then put the first letter last


def is_palindrome(s):
    if len(s) <= 1:
        return True
    if s[0] != s[-1]:
        return False
    return is_palindrome(s[1:-1])         # peel off both ends and check the middle


def power(x, n):
    if n == 0:
        return 1
    half = power(x, n // 2)               # one call on half the problem
    return half * half if n % 2 == 0 else half * half * x


yn = lambda b: "yes" if b else "no"
print(reverse("hello"), yn(is_palindrome("racecar")), yn(is_palindrome("rocket")))
print(power(2, 10), power(3, 5))
''', js=r'''
function reverse(s) {
  if (s.length <= 1) return s;
  return reverse(s.slice(1)) + s[0];      // reverse the rest, then put the first letter last
}

function isPalindrome(s) {
  if (s.length <= 1) return true;
  if (s[0] !== s[s.length - 1]) return false;
  return isPalindrome(s.slice(1, -1));    // peel off both ends and check the middle
}

function power(x, n) {
  if (n === 0) return 1;
  const half = power(x, Math.floor(n / 2));  // one call on half the problem
  return n % 2 === 0 ? half * half : half * half * x;
}

const yn = b => (b ? "yes" : "no");
console.log(reverse("hello"), yn(isPalindrome("racecar")), yn(isPalindrome("rocket")));
console.log(power(2, 10), power(3, 5));
''', java=r'''
public class Think {
    static String reverse(String s) {
        if (s.length() <= 1) return s;
        return reverse(s.substring(1)) + s.charAt(0);   // reverse the rest, then put the first letter last
    }

    static boolean isPalindrome(String s) {
        if (s.length() <= 1) return true;
        if (s.charAt(0) != s.charAt(s.length() - 1)) return false;
        return isPalindrome(s.substring(1, s.length() - 1));  // peel off both ends and check the middle
    }

    static long power(long x, int n) {
        if (n == 0) return 1;
        long half = power(x, n / 2);                     // one call on half the problem
        return n % 2 == 0 ? half * half : half * half * x;
    }

    static String yn(boolean b) { return b ? "yes" : "no"; }

    public static void main(String[] args) {
        System.out.println(reverse("hello") + " " + yn(isPalindrome("racecar")) + " " + yn(isPalindrome("rocket")));
        System.out.println(power(2, 10) + " " + power(3, 5));
    }
}
''', ts=r'''
function reverse(s: string): string {
  if (s.length <= 1) return s;
  return reverse(s.slice(1)) + s[0];      // reverse the rest, then put the first letter last
}

function isPalindrome(s: string): boolean {
  if (s.length <= 1) return true;
  if (s[0] !== s[s.length - 1]) return false;
  return isPalindrome(s.slice(1, -1));    // peel off both ends and check the middle
}

function power(x: number, n: number): number {
  if (n === 0) return 1;
  const half = power(x, Math.floor(n / 2));  // one call on half the problem
  return n % 2 === 0 ? half * half : half * half * x;
}

const yn = (b: boolean): string => (b ? "yes" : "no");
console.log(reverse("hello"), yn(isPalindrome("racecar")), yn(isPalindrome("rocket")));
console.log(power(2, 10), power(3, 5));
''')

t.code('hanoi', py=r'''
def hanoi(n, src, dst, via):
    if n == 0:
        return
    hanoi(n - 1, src, via, dst)       # park the smaller discs on the spare peg
    print("move disc", n, "from", src, "to", dst)
    hanoi(n - 1, via, dst, src)       # bring them back on top of the big disc


def count_moves(n):
    return 0 if n == 0 else 2 * count_moves(n - 1) + 1


hanoi(3, "A", "C", "B")
print("3 discs:", count_moves(3), "moves, 10 discs:", count_moves(10), "moves")
''', js=r'''
function hanoi(n, src, dst, via) {
  if (n === 0) return;
  hanoi(n - 1, src, via, dst);        // park the smaller discs on the spare peg
  console.log("move disc", n, "from", src, "to", dst);
  hanoi(n - 1, via, dst, src);        // bring them back on top of the big disc
}

function countMoves(n) {
  return n === 0 ? 0 : 2 * countMoves(n - 1) + 1;
}

hanoi(3, "A", "C", "B");
console.log("3 discs:", countMoves(3), "moves, 10 discs:", countMoves(10), "moves");
''', java=r'''
public class Hanoi {
    static void hanoi(int n, String src, String dst, String via) {
        if (n == 0) return;
        hanoi(n - 1, src, via, dst);          // park the smaller discs on the spare peg
        System.out.println("move disc " + n + " from " + src + " to " + dst);
        hanoi(n - 1, via, dst, src);          // bring them back on top of the big disc
    }

    static int countMoves(int n) {
        return n == 0 ? 0 : 2 * countMoves(n - 1) + 1;
    }

    public static void main(String[] args) {
        hanoi(3, "A", "C", "B");
        System.out.println("3 discs: " + countMoves(3) + " moves, 10 discs: " + countMoves(10) + " moves");
    }
}
''', ts=r'''
function hanoi(n: number, src: string, dst: string, via: string): void {
  if (n === 0) return;
  hanoi(n - 1, src, via, dst);        // park the smaller discs on the spare peg
  console.log("move disc", n, "from", src, "to", dst);
  hanoi(n - 1, via, dst, src);        // bring them back on top of the big disc
}

function countMoves(n: number): number {
  return n === 0 ? 0 : 2 * countMoves(n - 1) + 1;
}

hanoi(3, "A", "C", "B");
console.log("3 discs:", countMoves(3), "moves, 10 discs:", countMoves(10), "moves");
''')

t.code('structures', py=r'''
def flatten(items):
    out = []
    for x in items:
        if isinstance(x, list):
            out.extend(flatten(x))    # a list inside a list: the same problem, smaller
        else:
            out.append(x)
    return out


class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def depth(node):
    if node is None:                  # an empty tree has depth 0
        return 0
    return 1 + max(depth(node.left), depth(node.right))


print(" ".join(str(x) for x in flatten([1, [2, [3, 4], 5], [[6]]])))
tree = Node(1, Node(2, Node(4), None), Node(3, None, Node(5, Node(6))))
print("depth", depth(tree))
''', js=r'''
function flatten(items) {
  const out = [];
  for (const x of items) {
    if (Array.isArray(x)) out.push(...flatten(x));  // a list inside a list: the same problem, smaller
    else out.push(x);
  }
  return out;
}

class Node {
  constructor(val, left = null, right = null) {
    this.val = val;
    this.left = left;
    this.right = right;
  }
}

function depth(node) {
  if (node === null) return 0;        // an empty tree has depth 0
  return 1 + Math.max(depth(node.left), depth(node.right));
}

console.log(flatten([1, [2, [3, 4], 5], [[6]]]).join(" "));
const tree = new Node(1, new Node(2, new Node(4), null), new Node(3, null, new Node(5, new Node(6))));
console.log("depth", depth(tree));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class Structures {
    static List<Integer> flatten(List<?> items) {
        List<Integer> out = new ArrayList<>();
        for (Object x : items) {
            if (x instanceof List<?> inner) out.addAll(flatten(inner));  // a list inside a list: the same problem, smaller
            else out.add((Integer) x);
        }
        return out;
    }

    record Node(int val, Node left, Node right) {
        Node(int val) { this(val, null, null); }
    }

    static int depth(Node node) {
        if (node == null) return 0;           // an empty tree has depth 0
        return 1 + Math.max(depth(node.left()), depth(node.right()));
    }

    public static void main(String[] args) {
        List<Object> data = List.of(1, List.of(2, List.of(3, 4), 5), List.of(List.of(6)));
        List<String> parts = new ArrayList<>();
        for (int x : flatten(data)) parts.add(String.valueOf(x));
        System.out.println(String.join(" ", parts));
        Node tree = new Node(1, new Node(2, new Node(4), null), new Node(3, null, new Node(5, new Node(6), null)));
        System.out.println("depth " + depth(tree));
    }
}
''', ts=r'''
type Nested = number | Nested[];

function flatten(items: Nested[]): number[] {
  const out: number[] = [];
  for (const x of items) {
    if (Array.isArray(x)) out.push(...flatten(x));  // a list inside a list: the same problem, smaller
    else out.push(x);
  }
  return out;
}

class TreeNode {
  val: number;
  left: TreeNode | null;
  right: TreeNode | null;
  constructor(val: number, left: TreeNode | null = null, right: TreeNode | null = null) {
    this.val = val;
    this.left = left;
    this.right = right;
  }
}

function depth(node: TreeNode | null): number {
  if (node === null) return 0;        // an empty tree has depth 0
  return 1 + Math.max(depth(node.left), depth(node.right));
}

console.log(flatten([1, [2, [3, 4], 5], [[6]]]).join(" "));
const tree = new TreeNode(1, new TreeNode(2, new TreeNode(4), null), new TreeNode(3, null, new TreeNode(5, new TreeNode(6))));
console.log("depth", depth(tree));
''')

t.code('loops', py=r'''
def gcd_rec(a, b):
    if b == 0:
        return a
    return gcd_rec(b, a % b)          # tail call: nothing left to do after it returns


def gcd_loop(a, b):
    while b != 0:                     # the same idea as a loop: no stack frames pile up
        a, b = b, a % b
    return a


def sum_list_stack(nums):
    stack, total = list(nums), 0      # an explicit stack replaces the call stack
    while stack:
        total += stack.pop()
    return total


print(gcd_rec(48, 18), gcd_loop(48, 18), sum_list_stack(range(1, 101)))
''', js=r'''
function gcdRec(a, b) {
  if (b === 0) return a;
  return gcdRec(b, a % b);            // tail call: nothing left to do after it returns
}

function gcdLoop(a, b) {
  while (b !== 0) {                   // the same idea as a loop: no stack frames pile up
    [a, b] = [b, a % b];
  }
  return a;
}

function sumListStack(nums) {
  const stack = [...nums];            // an explicit stack replaces the call stack
  let total = 0;
  while (stack.length) total += stack.pop();
  return total;
}

console.log(gcdRec(48, 18), gcdLoop(48, 18), sumListStack(Array.from({ length: 100 }, (_, i) => i + 1)));
''', java=r'''
import java.util.ArrayDeque;
import java.util.Deque;

public class Loops {
    static int gcdRec(int a, int b) {
        if (b == 0) return a;
        return gcdRec(b, a % b);              // tail call: nothing left to do after it returns
    }

    static int gcdLoop(int a, int b) {
        while (b != 0) {                      // the same idea as a loop: no stack frames pile up
            int t = a % b;
            a = b;
            b = t;
        }
        return a;
    }

    static int sumListStack(int n) {
        Deque<Integer> stack = new ArrayDeque<>();   // an explicit stack replaces the call stack
        for (int i = 1; i <= n; i++) stack.push(i);
        int total = 0;
        while (!stack.isEmpty()) total += stack.pop();
        return total;
    }

    public static void main(String[] args) {
        System.out.println(gcdRec(48, 18) + " " + gcdLoop(48, 18) + " " + sumListStack(100));
    }
}
''', ts=r'''
function gcdRec(a: number, b: number): number {
  if (b === 0) return a;
  return gcdRec(b, a % b);            // tail call: nothing left to do after it returns
}

function gcdLoop(a: number, b: number): number {
  while (b !== 0) {                   // the same idea as a loop: no stack frames pile up
    [a, b] = [b, a % b];
  }
  return a;
}

function sumListStack(nums: number[]): number {
  const stack: number[] = [...nums];  // an explicit stack replaces the call stack
  let total = 0;
  while (stack.length) total += stack.pop()!;
  return total;
}

console.log(gcdRec(48, 18), gcdLoop(48, 18), sumListStack(Array.from({ length: 100 }, (_, i) => i + 1)));
''')

# ---------------------------------------------------------------- LeetCode practice programs
t.code('p_fib', py=r'''
def fib(n, memo={}):
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib(n - 1) + fib(n - 2)   # remember each answer once
    return memo[n]


print(fib(2), fib(3), fib(4), fib(30))
''', js=r'''
const memo = new Map();

function fib(n) {
  if (n < 2) return n;
  if (!memo.has(n)) memo.set(n, fib(n - 1) + fib(n - 2));  // remember each answer once
  return memo.get(n);
}

console.log(fib(2), fib(3), fib(4), fib(30));
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class Fibonacci {
    static Map<Integer, Integer> memo = new HashMap<>();

    static int fib(int n) {
        if (n < 2) return n;
        if (!memo.containsKey(n)) memo.put(n, fib(n - 1) + fib(n - 2));  // remember each answer once
        return memo.get(n);
    }

    public static void main(String[] args) {
        System.out.println(fib(2) + " " + fib(3) + " " + fib(4) + " " + fib(30));
    }
}
''', ts=r'''
const memo = new Map<number, number>();

function fib(n: number): number {
  if (n < 2) return n;
  if (!memo.has(n)) memo.set(n, fib(n - 1) + fib(n - 2));  // remember each answer once
  return memo.get(n)!;
}

console.log(fib(2), fib(3), fib(4), fib(30));
''')

t.code('p_revstr', py=r'''
def reverse_string(s, lo=0, hi=None):
    if hi is None:
        hi = len(s) - 1
    if lo >= hi:                     # the middle is reached, nothing left to swap
        return
    s[lo], s[hi] = s[hi], s[lo]      # swap the outer pair
    reverse_string(s, lo + 1, hi - 1)


for word in [list("hello"), list("Hannah")]:
    reverse_string(word)
    print("".join(word))
''', js=r'''
function reverseString(s, lo = 0, hi = s.length - 1) {
  if (lo >= hi) return;              // the middle is reached, nothing left to swap
  [s[lo], s[hi]] = [s[hi], s[lo]];   // swap the outer pair
  reverseString(s, lo + 1, hi - 1);
}

for (const word of [[..."hello"], [..."Hannah"]]) {
  reverseString(word);
  console.log(word.join(""));
}
''', java=r'''
public class ReverseString {
    static void reverseString(char[] s, int lo, int hi) {
        if (lo >= hi) return;                // the middle is reached, nothing left to swap
        char t = s[lo];                      // swap the outer pair
        s[lo] = s[hi];
        s[hi] = t;
        reverseString(s, lo + 1, hi - 1);
    }

    public static void main(String[] args) {
        for (String w : new String[]{"hello", "Hannah"}) {
            char[] s = w.toCharArray();
            reverseString(s, 0, s.length - 1);
            System.out.println(new String(s));
        }
    }
}
''', ts=r'''
function reverseString(s: string[], lo: number = 0, hi: number = s.length - 1): void {
  if (lo >= hi) return;              // the middle is reached, nothing left to swap
  [s[lo], s[hi]] = [s[hi], s[lo]];   // swap the outer pair
  reverseString(s, lo + 1, hi - 1);
}

for (const word of [[..."hello"], [..."Hannah"]]) {
  reverseString(word);
  console.log(word.join(""));
}
''')

t.code('p_pow', py=r'''
def my_pow(x, n):
    if n < 0:
        return my_pow(1 / x, -n)     # x to a negative power is 1/x to the positive power
    if n == 0:
        return 1.0
    half = my_pow(x, n // 2)         # halve the exponent each call: O(log n) calls
    return half * half if n % 2 == 0 else half * half * x


print(f"{my_pow(2.0, 10):.5f} {my_pow(2.1, 3):.5f} {my_pow(2.0, -2):.5f}")
''', js=r'''
function myPow(x, n) {
  if (n < 0) return myPow(1 / x, -n);   // x to a negative power is 1/x to the positive power
  if (n === 0) return 1;
  const half = myPow(x, Math.floor(n / 2));  // halve the exponent each call: O(log n) calls
  return n % 2 === 0 ? half * half : half * half * x;
}

console.log(myPow(2.0, 10).toFixed(5), myPow(2.1, 3).toFixed(5), myPow(2.0, -2).toFixed(5));
''', java=r'''
public class Pow {
    static double myPow(double x, long n) {
        if (n < 0) return myPow(1 / x, -n);   // x to a negative power is 1/x to the positive power
        if (n == 0) return 1.0;
        double half = myPow(x, n / 2);        // halve the exponent each call: O(log n) calls
        return n % 2 == 0 ? half * half : half * half * x;
    }

    public static void main(String[] args) {
        System.out.println(String.format("%.5f %.5f %.5f", myPow(2.0, 10), myPow(2.1, 3), myPow(2.0, -2)));
    }
}
''', ts=r'''
function myPow(x: number, n: number): number {
  if (n < 0) return myPow(1 / x, -n);   // x to a negative power is 1/x to the positive power
  if (n === 0) return 1;
  const half = myPow(x, Math.floor(n / 2));  // halve the exponent each call: O(log n) calls
  return n % 2 === 0 ? half * half : half * half * x;
}

console.log(myPow(2.0, 10).toFixed(5), myPow(2.1, 3).toFixed(5), myPow(2.0, -2).toFixed(5));
''')

t.code('p_merge', py=r'''
class ListNode:
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt


def merge(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if a.val <= b.val:
        a.next = merge(a.next, b)    # a wins, the rest is the same problem
        return a
    b.next = merge(a, b.next)
    return b


def build(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def show(node):
    out = []
    while node:
        out.append(str(node.val))
        node = node.next
    return " ".join(out) or "(empty)"


print(show(merge(build([1, 2, 4]), build([1, 3, 4]))))
print(show(merge(build([]), build([0]))))
''', js=r'''
class ListNode {
  constructor(val, next = null) {
    this.val = val;
    this.next = next;
  }
}

function merge(a, b) {
  if (a === null) return b;
  if (b === null) return a;
  if (a.val <= b.val) {
    a.next = merge(a.next, b);       // a wins, the rest is the same problem
    return a;
  }
  b.next = merge(a, b.next);
  return b;
}

function build(vals) {
  let head = null;
  for (let i = vals.length - 1; i >= 0; i--) head = new ListNode(vals[i], head);
  return head;
}

function show(node) {
  const out = [];
  for (; node; node = node.next) out.push(node.val);
  return out.join(" ") || "(empty)";
}

console.log(show(merge(build([1, 2, 4]), build([1, 3, 4]))));
console.log(show(merge(build([]), build([0]))));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class MergeLists {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }
    }

    static ListNode merge(ListNode a, ListNode b) {
        if (a == null) return b;
        if (b == null) return a;
        if (a.val <= b.val) {
            a.next = merge(a.next, b);       // a wins, the rest is the same problem
            return a;
        }
        b.next = merge(a, b.next);
        return b;
    }

    static ListNode build(int... vals) {
        ListNode head = null;
        for (int i = vals.length - 1; i >= 0; i--) head = new ListNode(vals[i], head);
        return head;
    }

    static String show(ListNode node) {
        List<String> out = new ArrayList<>();
        for (; node != null; node = node.next) out.add(String.valueOf(node.val));
        return out.isEmpty() ? "(empty)" : String.join(" ", out);
    }

    public static void main(String[] args) {
        System.out.println(show(merge(build(1, 2, 4), build(1, 3, 4))));
        System.out.println(show(merge(build(), build(0))));
    }
}
''', ts=r'''
class ListNode {
  val: number;
  next: ListNode | null;
  constructor(val: number, next: ListNode | null = null) {
    this.val = val;
    this.next = next;
  }
}

function merge(a: ListNode | null, b: ListNode | null): ListNode | null {
  if (a === null) return b;
  if (b === null) return a;
  if (a.val <= b.val) {
    a.next = merge(a.next, b);       // a wins, the rest is the same problem
    return a;
  }
  b.next = merge(a, b.next);
  return b;
}

function build(vals: number[]): ListNode | null {
  let head: ListNode | null = null;
  for (let i = vals.length - 1; i >= 0; i--) head = new ListNode(vals[i], head);
  return head;
}

function show(node: ListNode | null): string {
  const out: number[] = [];
  for (; node; node = node.next) out.push(node.val);
  return out.join(" ") || "(empty)";
}

console.log(show(merge(build([1, 2, 4]), build([1, 3, 4]))));
console.log(show(merge(build([]), build([0]))));
''')

t.code('p_stairs', py=r'''
from functools import lru_cache


@lru_cache(maxsize=None)              # Python's built in memo
def climb(n):
    if n <= 2:
        return n                      # 1 way for one step, 2 ways for two steps
    return climb(n - 1) + climb(n - 2)   # the last move was a 1 step or a 2 step


print(climb(2), climb(3), climb(5), climb(45))
''', js=r'''
const memo = new Map();

function climb(n) {
  if (n <= 2) return n;               // 1 way for one step, 2 ways for two steps
  if (!memo.has(n)) memo.set(n, climb(n - 1) + climb(n - 2));  // the last move was a 1 step or a 2 step
  return memo.get(n);
}

console.log(climb(2), climb(3), climb(5), climb(45));
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class ClimbingStairs {
    static Map<Integer, Integer> memo = new HashMap<>();

    static int climb(int n) {
        if (n <= 2) return n;                 // 1 way for one step, 2 ways for two steps
        if (!memo.containsKey(n)) memo.put(n, climb(n - 1) + climb(n - 2));  // the last move was a 1 step or a 2 step
        return memo.get(n);
    }

    public static void main(String[] args) {
        System.out.println(climb(2) + " " + climb(3) + " " + climb(5) + " " + climb(45));
    }
}
''', ts=r'''
const memo = new Map<number, number>();

function climb(n: number): number {
  if (n <= 2) return n;               // 1 way for one step, 2 ways for two steps
  if (!memo.has(n)) memo.set(n, climb(n - 1) + climb(n - 2));  // the last move was a 1 step or a 2 step
  return memo.get(n)!;
}

console.log(climb(2), climb(3), climb(5), climb(45));
''')

t.code('p_decode', py=r'''
def decode_string(s):
    pos = 0

    def parse():                      # reads text until a ] or the end, and returns it
        nonlocal pos
        out = ""
        while pos < len(s) and s[pos] != "]":
            if s[pos].isdigit():
                k = 0
                while s[pos].isdigit():
                    k = k * 10 + int(s[pos])
                    pos += 1
                pos += 1              # skip [
                inner = parse()       # the part inside the brackets is the same problem
                pos += 1              # skip ]
                out += inner * k
            else:
                out += s[pos]
                pos += 1
        return out

    return parse()


for s in ["3[a]2[bc]", "3[a2[c]]", "2[abc]3[cd]ef"]:
    print(decode_string(s))
''', js=r'''
function decodeString(s) {
  let pos = 0;
  function parse() {                  // reads text until a ] or the end, and returns it
    let out = "";
    while (pos < s.length && s[pos] !== "]") {
      if (s[pos] >= "0" && s[pos] <= "9") {
        let k = 0;
        while (s[pos] >= "0" && s[pos] <= "9") k = k * 10 + Number(s[pos++]);
        pos++;                        // skip [
        const inner = parse();        // the part inside the brackets is the same problem
        pos++;                        // skip ]
        out += inner.repeat(k);
      } else {
        out += s[pos++];
      }
    }
    return out;
  }
  return parse();
}

for (const s of ["3[a]2[bc]", "3[a2[c]]", "2[abc]3[cd]ef"]) console.log(decodeString(s));
''', java=r'''
public class DecodeString {
    static String s;
    static int pos;

    static String parse() {                       // reads text until a ] or the end, and returns it
        StringBuilder out = new StringBuilder();
        while (pos < s.length() && s.charAt(pos) != ']') {
            if (Character.isDigit(s.charAt(pos))) {
                int k = 0;
                while (Character.isDigit(s.charAt(pos))) k = k * 10 + (s.charAt(pos++) - '0');
                pos++;                            // skip [
                String inner = parse();           // the part inside the brackets is the same problem
                pos++;                            // skip ]
                out.append(inner.repeat(k));
            } else {
                out.append(s.charAt(pos++));
            }
        }
        return out.toString();
    }

    static String decodeString(String input) {
        s = input;
        pos = 0;
        return parse();
    }

    public static void main(String[] args) {
        for (String x : new String[]{"3[a]2[bc]", "3[a2[c]]", "2[abc]3[cd]ef"}) System.out.println(decodeString(x));
    }
}
''', ts=r'''
function decodeString(s: string): string {
  let pos = 0;
  function parse(): string {          // reads text until a ] or the end, and returns it
    let out = "";
    while (pos < s.length && s[pos] !== "]") {
      if (s[pos] >= "0" && s[pos] <= "9") {
        let k = 0;
        while (s[pos] >= "0" && s[pos] <= "9") k = k * 10 + Number(s[pos++]);
        pos++;                        // skip [
        const inner = parse();        // the part inside the brackets is the same problem
        pos++;                        // skip ]
        out += inner.repeat(k);
      } else {
        out += s[pos++];
      }
    }
    return out;
  }
  return parse();
}

for (const s of ["3[a]2[bc]", "3[a2[c]]", "2[abc]3[cd]ef"]) console.log(decodeString(s));
''')

t.code('p_kth', py=r'''
def kth_grammar(n, k):
    if n == 1:
        return 0                     # row 1 is just "0"
    parent = kth_grammar(n - 1, (k + 1) // 2)   # each symbol comes from one in the row above
    return parent if k % 2 == 1 else 1 - parent  # 0 -> 01 and 1 -> 10


print(kth_grammar(1, 1), kth_grammar(2, 1), kth_grammar(2, 2), kth_grammar(4, 5), kth_grammar(30, 434991989))
''', js=r'''
function kthGrammar(n, k) {
  if (n === 1) return 0;             // row 1 is just "0"
  const parent = kthGrammar(n - 1, Math.floor((k + 1) / 2));  // each symbol comes from one in the row above
  return k % 2 === 1 ? parent : 1 - parent;                   // 0 -> 01 and 1 -> 10
}

console.log(kthGrammar(1, 1), kthGrammar(2, 1), kthGrammar(2, 2), kthGrammar(4, 5), kthGrammar(30, 434991989));
''', java=r'''
public class KthSymbol {
    static int kthGrammar(int n, int k) {
        if (n == 1) return 0;                     // row 1 is just "0"
        int parent = kthGrammar(n - 1, (k + 1) / 2);   // each symbol comes from one in the row above
        return k % 2 == 1 ? parent : 1 - parent;       // 0 -> 01 and 1 -> 10
    }

    public static void main(String[] args) {
        System.out.println(kthGrammar(1, 1) + " " + kthGrammar(2, 1) + " " + kthGrammar(2, 2) + " " + kthGrammar(4, 5) + " " + kthGrammar(30, 434991989));
    }
}
''', ts=r'''
function kthGrammar(n: number, k: number): number {
  if (n === 1) return 0;             // row 1 is just "0"
  const parent = kthGrammar(n - 1, Math.floor((k + 1) / 2));  // each symbol comes from one in the row above
  return k % 2 === 1 ? parent : 1 - parent;                   // 0 -> 01 and 1 -> 10
}

console.log(kthGrammar(1, 1), kthGrammar(2, 1), kthGrammar(2, 2), kthGrammar(4, 5), kthGrammar(30, 434991989));
''')

t.code('p_regex', py=r'''
from functools import lru_cache


def is_match(s, p):
    @lru_cache(maxsize=None)
    def match(i, j):                  # does s[i:] match p[j:]
        if j == len(p):
            return i == len(s)
        first = i < len(s) and p[j] in (s[i], ".")
        if j + 1 < len(p) and p[j + 1] == "*":
            return match(i, j + 2) or (first and match(i + 1, j))   # use x* zero times, or eat one more
        return first and match(i + 1, j + 1)
    return match(0, 0)


tests = [("aa", "a"), ("aa", "a*"), ("ab", ".*"), ("aab", "c*a*b"), ("mississippi", "mis*is*p*.")]
print(" ".join("yes" if is_match(s, p) else "no" for s, p in tests))
''', js=r'''
function isMatch(s, p) {
  const memo = new Map();
  function match(i, j) {              // does s from i match p from j
    const key = i * 100 + j;
    if (memo.has(key)) return memo.get(key);
    let ans;
    if (j === p.length) ans = i === s.length;
    else {
      const first = i < s.length && (p[j] === s[i] || p[j] === ".");
      if (j + 1 < p.length && p[j + 1] === "*") ans = match(i, j + 2) || (first && match(i + 1, j));  // zero times, or one more
      else ans = first && match(i + 1, j + 1);
    }
    memo.set(key, ans);
    return ans;
  }
  return match(0, 0);
}

const tests = [["aa", "a"], ["aa", "a*"], ["ab", ".*"], ["aab", "c*a*b"], ["mississippi", "mis*is*p*."]];
console.log(tests.map(([s, p]) => (isMatch(s, p) ? "yes" : "no")).join(" "));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class RegexMatch {
    static String s, p;
    static Boolean[][] memo;

    static boolean match(int i, int j) {          // does s from i match p from j
        if (memo[i][j] != null) return memo[i][j];
        boolean ans;
        if (j == p.length()) ans = i == s.length();
        else {
            boolean first = i < s.length() && (p.charAt(j) == s.charAt(i) || p.charAt(j) == '.');
            if (j + 1 < p.length() && p.charAt(j + 1) == '*') ans = match(i, j + 2) || (first && match(i + 1, j));  // zero times, or one more
            else ans = first && match(i + 1, j + 1);
        }
        memo[i][j] = ans;
        return ans;
    }

    static boolean isMatch(String text, String pattern) {
        s = text;
        p = pattern;
        memo = new Boolean[s.length() + 1][p.length() + 1];
        return match(0, 0);
    }

    public static void main(String[] args) {
        String[][] tests = {{"aa", "a"}, {"aa", "a*"}, {"ab", ".*"}, {"aab", "c*a*b"}, {"mississippi", "mis*is*p*."}};
        List<String> out = new ArrayList<>();
        for (String[] t : tests) out.add(isMatch(t[0], t[1]) ? "yes" : "no");
        System.out.println(String.join(" ", out));
    }
}
''', ts=r'''
function isMatch(s: string, p: string): boolean {
  const memo = new Map<number, boolean>();
  function match(i: number, j: number): boolean {  // does s from i match p from j
    const key = i * 100 + j;
    const seen = memo.get(key);
    if (seen !== undefined) return seen;
    let ans: boolean;
    if (j === p.length) ans = i === s.length;
    else {
      const first = i < s.length && (p[j] === s[i] || p[j] === ".");
      if (j + 1 < p.length && p[j + 1] === "*") ans = match(i, j + 2) || (first && match(i + 1, j));  // zero times, or one more
      else ans = first && match(i + 1, j + 1);
    }
    memo.set(key, ans);
    return ans;
  }
  return match(0, 0);
}

const tests: Array<[string, string]> = [["aa", "a"], ["aa", "a*"], ["ab", ".*"], ["aab", "c*a*b"], ["mississippi", "mis*is*p*."]];
console.log(tests.map(([s, p]) => (isMatch(s, p) ? "yes" : "no")).join(" "));
''')

t.leet(509, 'e', 'p_fib',
       statement='<p>The Fibonacci numbers start 0, 1, and each next one is the sum of the two before it. Return the n-th one.</p>',
       example='n = 2  →  1\nn = 3  →  2\nn = 4  →  3\nn = 30 →  832040',
       hint='The plain recursion repeats work. Remember each answer.',
       approach='<p>Write the definition directly, <code>fib(n) = fib(n − 1) + fib(n − 2)</code> with base cases 0 and 1, then add a memo so each n is solved once. That turns about 2<sup>n</sup> calls into about 2n. A loop with two variables does the same in O(1) memory.</p>',
       time='O(n)', space='O(n) for the memo and the call stack')
t.leet(344, 'e', 'p_revstr',
       statement='<p>Reverse a list of characters in place, using O(1) extra memory apart from the call stack.</p>',
       example='h e l l o      →  o l l e h\nH a n n a h    →  h a n n a H',
       hint='Swap the two ends, then reverse what is left in the middle.',
       approach='<p>The recursive step swaps <code>s[lo]</code> and <code>s[hi]</code> and calls itself on <code>lo + 1, hi − 1</code>. The base case is when the two indexes meet or cross. The loop version with two pointers avoids the n / 2 stack frames.</p>',
       time='O(n)', space='O(n) call stack, O(1) for the loop version')
t.leet(50, 'm', 'p_pow',
       statement='<p>Compute x to the power n, where n can be negative and as large as about two billion. Multiplying n times is far too slow.</p>',
       example='x = 2.0, n = 10  →  1024.00000\nx = 2.1, n = 3   →  9.26100\nx = 2.0, n = -2  →  0.25000',
       hint='x^10 = (x^5)^2, and x^5 = x · (x^2)^2.',
       approach='<p>Fast power: compute <code>half = x<sup>n // 2</sup></code> once and square it, multiplying by x once more when n is odd. Each call halves n, so there are only about 31 calls. For negative n use 1 / x. In Java keep n in a <code>long</code>, because negating the smallest int overflows.</p>',
       time='O(log n)', space='O(log n) call stack')
t.leet(21, 'm', 'p_merge',
       statement='<p>Merge two sorted linked lists into one sorted list by relinking their nodes, and return its head.</p>',
       example='1 2 4  and  1 3 4  →  1 1 2 3 4 4\n(empty) and 0      →  0',
       hint='The smaller head comes first. What comes after it is the merge of everything else.',
       approach='<p>If one list is empty, return the other. Otherwise the smaller head wins, and its <code>next</code> becomes the merge of its rest with the other list. The Linked lists chapter shows the loop version with a dummy node, which uses no call stack.</p>',
       time='O(m + n)', space='O(m + n) call stack')
t.leet(70, 'h', 'p_stairs',
       statement='<p>You climb a staircase of n steps, one or two steps at a time. In how many different ways can you reach the top?</p>',
       example='n = 2  →  2   (1+1, 2)\nn = 3  →  3   (1+1+1, 1+2, 2+1)\nn = 5  →  8',
       hint='Think about your very last move.',
       approach='<p>Your last move was either one step from n − 1 or two steps from n − 2, so <code>ways(n) = ways(n − 1) + ways(n − 2)</code>. That is Fibonacci again. Memoize it, here with Python\'s <code>lru_cache</code>, so n = 45 is instant instead of a billion calls. The Dynamic programming chapter turns it into a table.</p>',
       time='O(n)', space='O(n)')
t.leet(394, 'h', 'p_decode',
       statement='<p>Decode a string where <code>k[text]</code> means text repeated k times. Brackets can be nested.</p>',
       example='3[a]2[bc]      →  aaabcbc\n3[a2[c]]       →  accaccacc\n2[abc]3[cd]ef  →  abcabccdcdcdef',
       hint='What is inside a pair of brackets is a smaller encoded string.',
       approach='<p>Recursive descent: <code>parse</code> reads characters until a <code>]</code> or the end. On a number it reads the count, skips <code>[</code>, calls itself for the inside, skips <code>]</code> and repeats the result. A shared position moves forward through the string, so each character is read once. The Stacks and queues chapter solves it with an explicit stack.</p>',
       time='O(length of the output)', space='O(nesting depth) call stack')
t.leet(779, 'x', 'p_kth',
       statement='<p>Row 1 is "0". Each next row replaces every 0 with "01" and every 1 with "10". Return the k-th symbol (counting from 1) of row n, for n up to 30, without building the rows.</p>',
       example='n = 1, k = 1  →  0\nn = 2, k = 2  →  1\nn = 4, k = 5  →  1   (row 4 is 01101001)',
       hint='Symbol k of row n is made from symbol (k + 1) / 2 of row n − 1.',
       approach='<p>Find the parent symbol with one recursive call on row n − 1. An odd k is the first child, which copies the parent. An even k is the second child, which flips it. Row 30 has more than 500 million symbols, but this takes only 30 calls.</p>',
       time='O(n)', space='O(n) call stack')
t.leet(10, 'x', 'p_regex',
       statement='<p>Implement pattern matching with <code>.</code> (any one character) and <code>*</code> (zero or more of the character before it). The whole text must match the whole pattern.</p>',
       example='aa, a          →  no\naa, a*         →  yes\nab, .*         →  yes\naab, c*a*b     →  yes\nmississippi, mis*is*p*.  →  no',
       hint='Ask whether s from i matches p from j. A star gives two choices.',
       approach='<p>Define <code>match(i, j)</code>. If <code>p[j + 1]</code> is a star, either skip <code>x*</code> entirely, or, if the first characters match, eat one character of the text and keep the star. Otherwise the first characters must match and both move on. Memoizing the (i, j) pairs keeps it to O(m · n) instead of exponential.</p>',
       time='O(m · n)', space='O(m · n)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='what-is-recursion', emoji='🪆', title='Recursion: a function that calls itself', html='''
<p>Open a Russian doll and you find a smaller doll that looks the same. Open that one and there is a smaller one again, until you reach a tiny solid doll that does not open. <b>Recursion</b> solves a problem the same way: it hands a <b>smaller copy of the same problem</b> to itself, until the problem is so small that the answer is obvious.</p>
<div class="grid2">
<div class="box"><h4>🛑 Base case</h4><p>The tiny solid doll. A case simple enough to answer directly, such as <code>factorial(1) = 1</code>. Without it the function calls itself forever.</p></div>
<div class="box"><h4>🔁 Recursive case</h4><p>Shrink the problem and trust the smaller call: <code>factorial(n) = n × factorial(n − 1)</code>. Every call must move closer to the base case.</p></div>
</div>
<div class="viz" data-viz="pk" data-pk="fact"></div>
<div class="c3" data-k="factorial" data-label="Factorial and a countdown"></div>
<div class="rule">Two questions for every recursive function: what is the smallest case I can answer straight away, and how do I make the problem one step smaller?</div>
'''),
    dict(id='call-stack', emoji='📚', title='The call stack: who is waiting for whom', html='''
<p>When a function calls another, the computer puts a note on a pile called the <b>call stack</b>. The note, a <b>stack frame</b>, holds the local variables and the place to come back to. The newest call sits on top. When it returns, its frame is popped and the call below carries on from where it paused. That is exactly the last in, first out stack from the previous chapter.</p>
<div class="viz" data-viz="pk" data-pk="sumstack"></div>
<div class="c3" data-k="callstack" data-label="Watch the frames wait and return"></div>
<div class="tw"><table class="jt"><tr><th>Language</th><th>Too deep gives</th><th>Typical limit</th></tr>
<tr><td>Python</td><td><code>RecursionError</code></td><td>1000 frames by default, <code>sys.setrecursionlimit</code> raises it</td></tr>
<tr><td>Java</td><td><code>StackOverflowError</code></td><td>depends on the thread stack size, often around 10,000 frames</td></tr>
<tr><td>JavaScript</td><td><code>RangeError: Maximum call stack size exceeded</code></td><td>roughly 10,000 frames in Node and browsers</td></tr></table></div>
<div class="warn">Recursion uses O(depth) memory for the frames, even when the function itself stores nothing. A recursion that goes n levels deep costs O(n) space.</div>
'''),
    dict(id='recursion-tree', emoji='🌳', title='Recursion trees and repeated work', html='''
<p>When a function calls itself more than once, the calls branch like a family tree. Fibonacci calls itself twice, so <code>fib(5)</code> calls <code>fib(4)</code> and <code>fib(3)</code>, and <code>fib(4)</code> calls <code>fib(3)</code> again. The same small problems are solved over and over, and the tree has about 2<sup>n</sup> nodes.</p>
<div class="viz" data-viz="pk" data-pk="fibtree"></div>
<div class="c3" data-k="fib_calls" data-label="Plain recursion versus memoized recursion"></div>
<div class="grid2">
<div class="box"><h4>🧠 Memoization</h4><p>Keep a map from input to answer. Before working, look it up. Each distinct input is then solved once, and fib(12) drops from 465 calls to 23.</p></div>
<div class="box"><h4>📏 Reading the tree</h4><p>Total work is the number of nodes times the work per node. The depth of the tree is the stack space. The Run time analysis chapter uses the same tree to solve recurrences.</p></div>
</div>
'''),
    dict(id='leap-of-faith', emoji='🙏', title='Thinking recursively: the leap of faith', html='''
<p>Do not try to follow every call in your head. Instead, <b>assume the smaller call already works</b> and ask only how to use its answer. To reverse "hello", trust that <code>reverse("ello")</code> gives "olle", then add "h" at the end. That trust is called the recursive leap of faith.</p>
<div class="tw"><table class="jt"><tr><th>Problem</th><th>Smaller problem</th><th>How to use its answer</th></tr>
<tr><td>Reverse s</td><td>reverse of s without its first letter</td><td>add the first letter at the end</td></tr>
<tr><td>Is s a palindrome</td><td>is the middle (without both ends) a palindrome</td><td>also check the two ends are equal</td></tr>
<tr><td>x to the power n</td><td>x to the power n // 2</td><td>square it, times x if n is odd</td></tr></table></div>
<div class="viz" data-viz="pk" data-pk="pal"></div>
<div class="c3" data-k="think" data-label="Reverse, palindrome and fast power"></div>
<div class="exam">Fast power makes one call on half the exponent, so its recursion has only about log₂ n levels: 2<sup>30</sup> needs 30 calls, not a billion multiplications.</div>
'''),
    dict(id='hanoi', emoji='🗼', title='The Tower of Hanoi', html='''
<p>Three pegs and a pile of discs, biggest at the bottom. Move the whole pile to another peg, one disc at a time, never putting a bigger disc on a smaller one. It looks hard, but recursion makes it three lines: move the top n − 1 discs out of the way, move the biggest disc, then move the n − 1 discs back on top of it.</p>
<div class="viz" data-viz="pk" data-pk="hanoi"></div>
<div class="c3" data-k="hanoi" data-label="Tower of Hanoi and its move count"></div>
<p>The number of moves follows <span class="eq">M(n) = 2 · M(n − 1) + 1</span>, which gives <span class="eq">M(n) = 2ⁿ − 1</span>. A legend tells of monks moving 64 golden discs: at one move per second that is about 585 billion years.</p>
'''),
    dict(id='structures', emoji='🧩', title='Recursion on nested data and trees', html='''
<p>Some data is recursive by nature. A folder holds files and other folders. A JSON document holds lists that hold objects that hold lists. A tree node has children that are trees themselves. For such data, recursion is not a trick but the most natural way to write the code.</p>
<div class="viz" data-viz="pk" data-pk="depth"></div>
<div class="c3" data-k="structures" data-label="Flatten a nested list, measure a tree"></div>
<div class="grid2">
<div class="box"><h4>📁 Folder sizes</h4><p>The size of a folder is the size of its files plus the size of each subfolder, computed the same way. This is how disk usage tools work.</p></div>
<div class="box"><h4>🌲 Trees</h4><p>Height, size, sum and search in a tree are all "do it for the left, do it for the right, combine". The Trees chapter is full of them.</p></div>
</div>
'''),
    dict(id='to-loops', emoji='🔄', title='Tail calls and turning recursion into loops', html='''
<p>A <b>tail call</b> is a recursive call that is the very last thing a function does, like <code>return gcd(b, a % b)</code>. Nothing waits for its answer, so in principle its frame could be reused. Some languages (Scheme, Scala with <code>@tailrec</code>, Safari's JavaScript engine) do that. <b>Python, Java and Node.js do not</b>, so deep recursion still overflows.</p>
<div class="tw"><table class="jt"><tr><th>When</th><th>Do this</th></tr>
<tr><td>The recursion is a tail call</td><td>rewrite it as a <code>while</code> loop that updates the arguments</td></tr>
<tr><td>It branches, like a tree walk</td><td>keep your own stack (a list) of work still to do</td></tr>
<tr><td>It repeats sub problems</td><td>memoize, or build a table from the bottom up (dynamic programming)</td></tr></table></div>
<div class="c3" data-k="loops" data-label="Recursive and loop versions side by side"></div>
<div class="rule">Recursion is a way of thinking. Write the clear recursive version first, then change it to a loop only if the depth could be large.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The recursive idea</th></tr>
<tr><td><a href="#lc509">509. Fibonacci Number</a></td><td>Easy</td><td>the definition plus a memo</td></tr>
<tr><td><a href="#lc344">344. Reverse String</a></td><td>Easy</td><td>swap the ends, recurse on the middle</td></tr>
<tr><td><a href="#lc50">50. Pow(x, n)</a></td><td>Medium</td><td>halve the exponent</td></tr>
<tr><td><a href="#lc21">21. Merge Two Sorted Lists</a></td><td>Medium</td><td>smaller head, then merge the rest</td></tr>
<tr><td><a href="#lc70">70. Climbing Stairs</a></td><td>Hard</td><td>think about the last move</td></tr>
<tr><td><a href="#lc394">394. Decode String</a></td><td>Hard</td><td>recursive descent into brackets</td></tr>
<tr><td><a href="#lc779">779. K-th Symbol in Grammar</a></td><td>Expert</td><td>ask the parent in the row above</td></tr>
<tr><td><a href="#lc10">10. Regular Expression Matching</a></td><td>Expert</td><td>two choices at every star, memoized</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;

  D.fact = el => PK.widget(el, {
    title: 'Open the dolls, then close them', sub: 'factorial(n) waits for factorial(n − 1). Watch the call stack grow, hit the base case, and unwind.',
    inputs: [{ k: 'n', label: 'n', type: 'num', val: 5, min: 1, max: 8 }],
    random: () => ({ n: 2 + Math.floor(Math.random() * 6) }),
    check: v => (Number.isInteger(v.n) && v.n >= 1 && v.n <= 8) ? '' : 'Pick a whole number from 1 to 8 so the stack fits on the screen.',
    frames: ({ n }) => {
      const F = [], st = [];
      for (let k = n; k >= 1; k--) {
        st.push(k === 1 ? 'factorial(1) = 1' : `factorial(${k}) = ${k} × factorial(${k - 1}) ?`);
        F.push(k === 1 ? { mood: 'happy', fx: 'burst', msg: 'factorial(1) is the base case. No more calls. The answer is simply <b>1</b>.', layers: [{ t: 'stack', label: 'Call stack (newest on top)', items: st.slice(), cls: { [st.length - 1]: 'yes' } }] }
                       : { mood: 'look', msg: `factorial(${k}) cannot finish yet. It needs factorial(${k - 1}) first, so a new frame goes on the stack.`, layers: [{ t: 'stack', label: 'Call stack (newest on top)', items: st.slice(), cls: { [st.length - 1]: 'look' } }] });
      }
      let val = 1;
      for (let k = 2; k <= n; k++) {
        st.pop();
        val *= k;
        st[st.length - 1] = `factorial(${k}) = ${k} × ${val / k} = ${val}`;
        F.push({ mood: 'work', msg: `The frame above returned ${val / k}. factorial(${k}) wakes up and computes ${k} × ${val / k} = <b>${val}</b>.`, vars: { 'returned': val }, layers: [{ t: 'stack', label: 'Call stack (newest on top)', items: st.slice(), cls: { [st.length - 1]: 'yes' } }] });
      }
      F.push({ mood: 'wow', fx: 'rain', msg: `The stack is back to one frame. ${n}! = <b>${val}</b>. ${n} frames went down and ${n} came back up.`, layers: [{ t: 'stack', label: 'Call stack', items: [`factorial(${n}) = ${val}`], cls: { 0: 'yes' } }] });
      return F;
    }
  });

  D.sumstack = el => PK.widget(el, {
    title: 'Adding a list, one frame at a time', sub: 'total(i) = nums[i] + total(i + 1). Each frame waits for the one above it to answer.',
    inputs: [{ k: 'nums', label: 'Numbers', type: 'text', val: '4, 2, 7', w: 180 }],
    random: () => ({ nums: Array.from({ length: 2 + Math.floor(Math.random() * 4) }, () => Math.floor(Math.random() * 10)) }),
    check: v => { const a = PK.parseList(v.nums); return a && a.length >= 1 && a.length <= 6 ? '' : 'Give one to six numbers.'; },
    frames: ({ nums }) => {
      const a = PK.parseList(nums), F = [], st = [];
      const row = i => ({ t: 'row', cells: a, cls: Object.fromEntries(a.map((_, j) => [j, j < i ? 'done' : j === i ? 'look' : ''])) });
      for (let i = 0; i <= a.length; i++) {
        st.push(i === a.length ? 'total(' + i + ') = 0, end of list' : `total(${i}) = ${a[i]} + total(${i + 1}) ?`);
        F.push({ mood: i === a.length ? 'happy' : 'look', msg: i === a.length ? 'Index ' + i + ' is past the end. Base case: the sum of nothing is <b>0</b>.' : `Frame for index ${i} holds ${a[i]} and pauses, waiting for the sum of the rest.`, layers: [row(i), { t: 'stack', label: 'Call stack', items: st.slice(), cls: { [st.length - 1]: i === a.length ? 'yes' : 'look' } }] });
      }
      let s = 0;
      for (let i = a.length - 1; i >= 0; i--) {
        st.pop();
        s += a[i];
        st[st.length - 1] = `total(${i}) = ${a[i]} + ${s - a[i]} = ${s}`;
        F.push({ mood: 'work', msg: `Frame ${i} gets ${s - a[i]} back and returns ${a[i]} + ${s - a[i]} = <b>${s}</b>. Its note is popped off.`, layers: [row(i), { t: 'stack', label: 'Call stack', items: st.slice(), cls: { [st.length - 1]: 'yes' } }] });
      }
      F.push({ mood: 'wow', fx: 'burst', msg: `The sum is <b>${s}</b>. At the deepest point there were ${a.length + 1} frames on the stack, which is why recursion costs O(n) memory here.` });
      return F;
    }
  });

  D.fibtree = el => PK.widget(el, {
    title: 'The Fibonacci family tree', sub: 'Every call to fib(n) asks fib(n − 1) and fib(n − 2). Repeated calls glow purple. Switch on the memo to skip them.',
    inputs: [{ k: 'n', label: 'n', type: 'num', val: 5, min: 2, max: 6 }, { k: 'mode', label: 'Mode', type: 'seg', val: 'plain', opts: [['plain', '🐌 Plain'], ['memo', '🧠 With memo']] }],
    check: v => (Number.isInteger(v.n) && v.n >= 2 && v.n <= 6) ? '' : 'Use n from 2 to 6 so the tree fits.',
    frames: ({ n, mode }) => {
      const kids = {}, lab = {}, order = [], memo = {};
      let id = 0;
      const seenN = {};
      (function build(k) {
        const me = 'c' + (id++);
        lab[me] = k;
        order.push(me);
        if (k >= 2 && !(mode === 'memo' && memo[k] !== undefined)) {
          const l = build(k - 1), r = build(k - 2);
          kids[me] = [l, r];
          memo[k] = 1;
        } else if (k >= 2) kids[me] = [null, null];
        return me;
      })(n);
      const T = PK.treeLayout(kids, 'c0', x => 'f' + lab[x], 460, 230);
      const val = {}, fibv = k => (k < 2 ? k : fibv(k - 1) + fibv(k - 2));
      const F = [{ mood: 'think', msg: `Let us call fib(${n}) ${mode === 'memo' ? 'with a memo that remembers answers' : 'the plain way'} and count the calls.`, layers: [{ t: 'graph', w: 460, h: 250, nodes: T.nodes.filter(x => x[0] === 'c0'), edges: [] }] }];
      const shown = new Set(), done = {};
      order.forEach((c, i) => {
        shown.add(c);
        const k = lab[c], rep = seenN[k];
        seenN[k] = (seenN[k] || 0) + 1;
        const hit = mode === 'memo' && rep && k >= 2;
        const ncls = {};
        shown.forEach(x => { ncls[x] = done[x] ? 'done' : ''; });
        ncls[c] = hit ? 'yes' : rep && k >= 2 ? 'mv' : k < 2 ? 'cur' : 'look';
        F.push({ mood: hit ? 'happy' : rep && k >= 2 ? 'sad' : 'look', fx: hit ? 'burst' : '',
          msg: hit ? `fib(${k}) again, but the memo already knows it is ${fibv(k)}. Instant answer, no new calls!` : rep && k >= 2 ? `fib(${k}) again! This exact problem was already solved once. Wasted work.` : k < 2 ? `fib(${k}) is a base case: ${k}.` : `Call fib(${k}). It needs fib(${k - 1}) and fib(${k - 2}).`,
          vars: { calls: i + 1 },
          layers: [{ t: 'graph', w: 460, h: 250, nodes: T.nodes.filter(x => shown.has(x[0])), edges: T.edges.filter(e => shown.has(e[0]) && shown.has(e[1])), ncls }] });
        if (k < 2 || hit) done[c] = 1;
      });
      F.push({ mood: 'wow', fx: mode === 'memo' ? 'rain' : 'shake', msg: `fib(${n}) = ${fibv(n)} after <b>${order.length}</b> calls. ${mode === 'memo' ? 'Each value was computed once.' : 'Try the memo mode and compare the count.'}`, vars: { calls: order.length },
        layers: [{ t: 'graph', w: 460, h: 250, nodes: T.nodes, edges: T.edges, ncls: Object.fromEntries(order.map(c => [c, 'done'])) }] });
      return F;
    }
  });

  D.pal = el => PK.widget(el, {
    title: 'Peel the ends: is it a palindrome', sub: 'Check the first and last letters. If they match, the answer is whatever the middle says.',
    inputs: [{ k: 'w', label: 'Word', type: 'text', val: 'racecar', w: 180 }],
    random: () => ({ w: ['level', 'rotor', 'madam', 'rocket', 'kayak', 'banana', 'noon', 'stats'][Math.floor(Math.random() * 8)] }),
    check: v => /^[A-Za-z]{1,12}$/.test(String(v.w).trim()) ? '' : 'Type one word of 1 to 12 letters.',
    frames: ({ w }) => {
      const s = String(w).trim().toLowerCase().split(''), F = [];
      let lo = 0, hi = s.length - 1, depth = 0;
      F.push({ mood: 'think', msg: `is_palindrome("${s.join('')}"): compare the two ends, then hand the middle to a smaller call.`, layers: [{ t: 'row', cells: s }] });
      while (lo < hi) {
        const cls = Object.fromEntries(s.map((_, i) => [i, i < lo || i > hi ? 'done' : '']));
        if (s[lo] !== s[hi]) {
          F.push({ mood: 'sad', fx: 'shake', msg: `Call ${depth + 1}: "${s[lo]}" and "${s[hi]}" are different. Not a palindrome! This answer travels back up through every waiting call.`, layers: [{ t: 'row', cells: s, cls: Object.assign(cls, { [lo]: 'no', [hi]: 'no' }), ptr: { [lo]: 'lo', [hi]: 'hi' } }] });
          return F;
        }
        F.push({ mood: 'look', msg: `Call ${depth + 1}: "${s[lo]}" and "${s[hi]}" match. Now ask a smaller call about the middle part.`, layers: [{ t: 'row', cells: s, cls: Object.assign(cls, { [lo]: 'yes', [hi]: 'yes' }), ptr: { [lo]: 'lo', [hi]: 'hi' } }] });
        lo++; hi--; depth++;
      }
      F.push({ mood: 'happy', fx: 'rain', msg: `The middle has ${lo === hi ? 'one letter' : 'no letters'} left, which is the base case: yes. So "${s.join('')}" <b>is a palindrome</b>, after ${depth + 1} calls.`, layers: [{ t: 'row', cells: s, cls: Object.fromEntries(s.map((_, i) => [i, 'yes'])) }] });
      return F;
    }
  });

  D.hanoi = el => PK.widget(el, {
    title: 'Move the tower', sub: 'Move all discs from peg A to peg C. Never put a bigger disc on a smaller one. Recursion plans every move.',
    inputs: [{ k: 'n', label: 'Discs', type: 'num', val: 3, min: 1, max: 5 }],
    check: v => (Number.isInteger(v.n) && v.n >= 1 && v.n <= 5) ? '' : 'Use 1 to 5 discs. Six discs already need 63 moves.',
    ms: 900,
    frames: ({ n }) => {
      const P = { A: [], B: [], C: [] };
      for (let d = n; d >= 1; d--) P.A.push(d);
      const disc = d => '▰'.repeat(d) + ' ' + d;
      const pic = (hl = {}) => {
        const rows = [], cls = {};
        for (let r = n - 1; r >= 0; r--) {
          const row = ['A', 'B', 'C'].map(p => P[p][r] !== undefined ? disc(P[p][r]) : '');
          rows.push(row);
          ['A', 'B', 'C'].forEach((p, c) => { if (P[p][r] !== undefined && hl[p] === r) cls[(n - 1 - r) + ',' + c] = hl.cls; });
        }
        return { t: 'grid', rows, cls, clab: ['peg A', 'peg B', 'peg C'] };
      };
      const moves = [];
      (function h(k, s, d, v) { if (!k) return; h(k - 1, s, v, d); moves.push([k, s, d]); h(k - 1, v, d, s); })(n, 'A', 'C', 'B');
      const F = [{ mood: 'think', msg: `To move ${n} disc${n > 1 ? 's' : ''} from A to C: move the top ${n - 1} to B, move disc ${n} to C, then move the ${n - 1} from B onto C. It needs ${moves.length} moves.`, layers: [pic()] }];
      moves.forEach(([k, s, d], i) => {
        P[d].push(P[s].pop());
        F.push({ mood: k === n ? 'wow' : 'work', fx: k === n ? 'burst' : '', msg: `Move ${i + 1}: disc ${k} from ${s} to ${d}.${k === n ? ' The biggest disc moves only once, right in the middle.' : ''}`, vars: { move: (i + 1) + ' of ' + moves.length }, layers: [pic({ [d]: P[d].length - 1, cls: 'yes' })] });
      });
      F.push({ mood: 'happy', fx: 'rain', msg: `Done in <b>${moves.length}</b> moves, exactly 2<sup>${n}</sup> − 1. Every extra disc doubles the work and adds one.`, say: `Done in ${moves.length} moves, exactly 2 to the power ${n} minus 1.` });
      return F;
    }
  });

  D.depth = el => PK.widget(el, {
    title: 'How tall is this tree', sub: 'Type a tree in level order (use null for a missing child). Each node asks its children for their height, adds 1, and reports back.',
    inputs: [{ k: 'lv', label: 'Level order', type: 'text', val: '1, 2, 3, 4, null, null, 5, null, null, 6', w: 300 }],
    check: v => { const a = PK.parseList(v.lv, false); return a.length >= 1 && a.length <= 15 && a[0] !== 'null' ? '' : 'Give 1 to 15 values in level order, starting with a real root.'; },
    frames: ({ lv }) => {
      const a = PK.parseList(lv, false), kids = {}, val = {};
      const q = [];
      let k = 0;
      const mk = v => { if (v === undefined || v === 'null') return null; const id = 'n' + (k++); val[id] = v; kids[id] = [null, null]; return id; };
      const root = mk(a[0]);
      q.push(root);
      let i = 1;
      while (q.length && i < a.length) {
        const cur = q.shift();
        const l = mk(a[i++]); if (l) q.push(l);
        const r = i < a.length ? mk(a[i++]) : null; if (r) q.push(r);
        kids[cur] = [l, r];
      }
      const T = PK.treeLayout(kids, root, id => val[id], 440, 230);
      const tag = {}, ncls = {}, F = [{ mood: 'think', msg: 'depth(node) = 1 + the larger depth of its two children. An empty child has depth 0.', layers: [{ t: 'graph', w: 440, h: 260, nodes: T.nodes, edges: T.edges }] }];
      (function go(id) {
        if (!id) return 0;
        ncls[id] = 'look';
        F.push({ mood: 'look', msg: `Node ${val[id]} asks its children how tall they are, and waits.`, layers: [{ t: 'graph', w: 440, h: 260, nodes: T.nodes, edges: T.edges, ncls: Object.assign({}, ncls), tag: Object.assign({}, tag) }] });
        const l = go(kids[id][0]), r = go(kids[id][1]);
        const d = 1 + Math.max(l, r);
        tag[id] = 'h=' + d;
        ncls[id] = 'yes';
        F.push({ mood: 'work', msg: `Node ${val[id]}: left says ${l}, right says ${r}. So its height is 1 + ${Math.max(l, r)} = <b>${d}</b>.`, layers: [{ t: 'graph', w: 440, h: 260, nodes: T.nodes, edges: T.edges, ncls: Object.assign({}, ncls), tag: Object.assign({}, tag) }] });
        return d;
      })(root);
      F.push({ mood: 'happy', fx: 'burst', msg: `The root reports the answer: the tree has depth <b>${tag[root].slice(2)}</b>. Every node was visited exactly once.` });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Dolls inside dolls',
    'panels': [
        {'s': [['e', '🪆'], ['t', 'f(n) = n × f(n − 1)', {'b': 1}]], 'h': 'Recursion', 't': 'Solve a smaller copy of the same problem.', 'more': 'Every call must move toward a base case that answers directly.'},
        {'s': [['e', '📚'], ['t', 'one frame per waiting call', {'b': 1}]], 'h': 'Call stack', 't': 'Frames wait in a pile.', 'more': 'Too many frames give a stack overflow. Depth n costs O(n) memory.'},
        {'s': [['e', '🌳'], ['t', '465 calls → 23 calls', {'b': 1}]], 'h': 'Memoization', 't': 'Remember answers.', 'more': 'Repeated sub problems make plain recursion exponential. A memo fixes it.'},
        {'s': [['e', '🗼'], ['t', '2ⁿ − 1 moves', {'b': 1}]], 'h': 'Hanoi', 't': 'Three lines, endless moves.', 'more': 'Move n − 1 away, move the biggest, move n − 1 back.'},
    ],
    'remember': 'Base case first, then a step that shrinks the problem. Trust the smaller call, watch the stack depth, and memoize when the same sub problem appears twice.',
}

REAL = [
    ['📁', 'Finding a file on your computer', 'Search looks in a folder, and for every subfolder it runs the very same search again. That is recursion over the folder tree.'],
    ['🪞', 'Two mirrors facing each other', 'Each reflection holds a smaller reflection. The images fade at the edge, which is the natural base case.'],
    ['🧮', 'A calculator reading (2 + 3) × 4', 'It reads an expression, and whenever it meets brackets it reads the inside as a smaller expression first.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to recursion. Recursion means a function solves a problem by asking a smaller copy of itself for help, until the problem is tiny. You will learn base cases, watch the call stack grow and shrink, see why some recursions repeat work and how memoization fixes it, solve the Tower of Hanoi, walk trees, and turn recursion into loops when it gets too deep.'},
    {'id': 'what-is-recursion', 'h': 'Recursion', 'en': 'Every recursive function has two parts. The base case answers a tiny problem directly, like factorial of one is one. The recursive case makes the problem one step smaller and calls the same function on it. If the base case is missing, the function never stops.'},
    {'id': 'call-stack', 'h': 'Call stack', 'en': 'Each call puts a frame on the call stack, holding its variables and where to return. The newest frame is on top. When it returns, it is popped and the frame below carries on. Too many frames cause a stack overflow, a RecursionError in Python, a StackOverflowError in Java and a RangeError in JavaScript.'},
    {'id': 'recursion-tree', 'h': 'Recursion trees', 'en': 'When a function calls itself more than once, the calls form a tree. Plain Fibonacci solves the same small problems again and again, so its tree grows exponentially. Memoization stores each answer the first time, and the number of calls drops from thousands to a few dozen.'},
    {'id': 'leap-of-faith', 'h': 'Thinking recursively', 'en': 'Do not trace every call in your head. Assume the smaller call already works and ask only how to use its answer. To reverse a word, reverse everything after the first letter and put the first letter at the end. To raise x to the power n, raise it to half of n and square the result.'},
    {'id': 'hanoi', 'h': 'Tower of Hanoi', 'en': 'To move a tower of n discs, move the top n minus one discs to the spare peg, move the biggest disc to the target, then move the n minus one discs on top of it. The number of moves is two to the power n, minus one, so every extra disc doubles the work.'},
    {'id': 'structures', 'h': 'Nested data', 'en': 'Folders inside folders, lists inside lists, and trees whose children are trees are all recursive data. For them recursion is the natural tool: handle each child the same way and combine the answers. The depth of a tree is one plus the larger depth of its children.'},
    {'id': 'to-loops', 'h': 'Recursion to loops', 'en': 'A tail call is a recursive call that is the very last step. Python, Java and Node do not reuse its frame, so deep recursion can still overflow. Turn tail calls into while loops, use your own stack for branching recursion, and memoize or build a table when sub problems repeat.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from Fibonacci number up to regular expression matching. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, first name the base case and the smaller problem, then write the code. Open the hint if you are stuck, and tick the box when you solve one.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What stops a recursive function from calling itself forever?', 'o': ['A loop', 'The base case', 'The return type', 'A global variable'], 'a': 1, 'hint': 'The smallest doll does not open.', 'why': 'The base case answers directly without another call.'},
    {'lv': 'e', 'q': 'What is factorial(4)?', 'o': ['10', '16', '24', '4'], 'a': 2, 'hint': '4 × 3 × 2 × 1.', 'why': '4 × 3 × 2 × 1 = 24.'},
    {'lv': 'e', 'q': 'Which structure keeps track of the calls that are waiting?', 'o': ['A queue', 'The call stack', 'A hash map', 'A heap'], 'a': 1, 'hint': 'Last call in, first call out.', 'why': 'Each call pushes a frame. Returning pops it.'},
    {'lv': 'e', 'q': 'How many moves does the Tower of Hanoi need for 4 discs?', 'o': ['8', '15', '16', '7'], 'a': 1, 'hint': '2ⁿ − 1.', 'why': '2⁴ − 1 = 15.'},
    {'lv': 'm', 'q': 'What happens in Python if a recursion goes about 1000 levels deep?', 'o': ['It slows down', 'RecursionError', 'It switches to a loop', 'Nothing'], 'a': 1, 'hint': 'Python has a default recursion limit.', 'why': 'The default limit is 1000 frames, after which Python raises RecursionError.'},
    {'lv': 'm', 'q': 'How much stack space does factorial(n) use?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], 'a': 2, 'hint': 'How many frames wait at the deepest point?', 'why': 'n frames are on the stack at the same time before the base case returns.'},
    {'lv': 'm', 'q': 'Why is plain recursive Fibonacci slow?', 'o': ['Addition is slow', 'It solves the same sub problems many times', 'It uses a loop', 'The base case is wrong'], 'a': 1, 'hint': 'Draw the tree for fib(5).', 'why': 'fib(3) is computed twice, fib(2) three times and so on. The work grows exponentially.'},
    {'lv': 'm', 'q': 'How many recursive calls does fast power make for x to the 64?', 'o': ['64', 'about 7', '32', '1'], 'a': 1, 'hint': 'The exponent halves each time.', 'why': '64, 32, 16, 8, 4, 2, 1, 0: about log₂ 64 + 1 = 7 calls.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'def f(n):\n    if n == 0:\n        return 0\n    return n + f(n - 2)\n\nprint(f(6))', 'o': ['12', '21', '6', 'RecursionError'], 'a': 0, 'hint': '6 + 4 + 2 + 0.', 'why': 'f(6) = 6 + f(4) = 6 + 4 + f(2) = 6 + 4 + 2 + f(0) = 12.'},
    {'lv': 'h', 'q': 'What does f(5) do for the function in the previous question?', 'o': ['Returns 9', 'Returns 15', 'Never reaches the base case and overflows', 'Returns 0'], 'a': 2, 'hint': '5, 3, 1, −1, ...', 'why': 'Odd numbers skip 0, so the calls go negative forever and the stack overflows.'},
    {'lv': 'h', 'q': 'Which of these is a tail call?', 'o': ['return n * f(n - 1)', 'return f(n - 1) + 1', 'return f(b, a % b)', 'x = f(n - 1)'], 'a': 2, 'hint': 'Nothing may happen after the call returns.', 'why': 'In return f(b, a % b) the result is returned as it is. The others still multiply, add or assign.'},
    {'lv': 'h', 'q': 'Does Java reuse the stack frame for tail calls?', 'o': ['Yes, always', 'No', 'Only for static methods', 'Only with -O'], 'a': 1, 'hint': 'Deep tail recursion still overflows in Java.', 'why': 'The JVM does not eliminate tail calls, so rewrite deep ones as loops.'},
    {'lv': 'x', 'q': 'Plain recursive fib(n) makes how many calls, roughly?', 'o': ['n', 'n²', 'about 1.6ⁿ', 'n log n'], 'a': 2, 'hint': 'The number of calls itself grows like Fibonacci numbers.', 'why': 'calls(n) = calls(n − 1) + calls(n − 2) + 1, which grows like φⁿ with φ ≈ 1.618.'},
    {'lv': 'x', 'q': 'K-th Symbol in Grammar, row 3 is 0110. What is row 4?', 'o': ['01101001', '01100110', '10010110', '01101010'], 'a': 0, 'hint': '0 → 01 and 1 → 10.', 'why': '0 → 01, 1 → 10, 1 → 10, 0 → 01 gives 01 10 10 01.'},
    {'lv': 'x', 'q': 'A function makes 3 recursive calls on n − 1 and does O(1) other work. What is its running time?', 'o': ['O(n)', 'O(3n)', 'O(3ⁿ)', 'O(n³)'], 'a': 2, 'hint': 'Each level of the tree has three times as many nodes.', 'why': 'The tree has 1 + 3 + 9 + ... + 3ⁿ nodes, which is O(3ⁿ).'},
    {'lv': 'x', 'q': 'In regular expression matching, why does memoizing match(i, j) make it fast?', 'o': ['It sorts the pattern', 'There are only (m + 1)(n + 1) different pairs to solve', 'It removes the stars', 'It uses a hash of the text'], 'a': 1, 'hint': 'Count the distinct inputs.', 'why': 'Each pair (i, j) is solved once, so the work is O(m · n) instead of exponential.'},
]

CALC = [
    {'lv': 'e', 'q': 'What is factorial(6)?', 'ans': '720', 'hint': '6 × factorial(5) and factorial(5) is 120.', 'steps': ['<span class="eq">6 × 120 = 720</span>']},
    {'lv': 'e', 'q': 'What is fib(10), if fib(0) = 0 and fib(1) = 1?', 'ans': '55', 'hint': '0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55.', 'steps': ['Keep adding the last two: 0 1 1 2 3 5 8 13 21 34 <span class="eq">55</span>']},
    {'lv': 'm', 'q': 'How many moves does the Tower of Hanoi need for 7 discs?', 'ans': '127', 'hint': '2ⁿ − 1.', 'steps': ['<span class="eq">2⁷ − 1 = 128 − 1 = 127</span>']},
    {'lv': 'm', 'q': 'A recursive sum of a list of 50 numbers stops at the empty list. How many frames are on the stack at the deepest moment?', 'ans': '51', 'hint': 'One frame per index, plus the empty list call.', 'steps': ['Indexes 0 to 49 give 50 frames, plus the base case call: <span class="eq">51</span>']},
    {'lv': 'h', 'q': 'How many calls does plain recursive fib(5) make in total?', 'ans': '15', 'hint': 'calls(n) = calls(n − 1) + calls(n − 2) + 1, with calls(0) = calls(1) = 1.', 'steps': ['calls(2) = 3, calls(3) = 5, calls(4) = 9', '<span class="eq">calls(5) = 9 + 5 + 1 = 15</span>']},
    {'lv': 'h', 'q': 'Fast power computes 3 to the 13. How many multiplications does it do? Squaring counts as one, and multiplying by x as one.', 'ans': '6', 'hint': '13 is 1101 in binary.', 'steps': ['Exponents visited: 13, 6, 3, 1, 0.', 'Each of 13, 6, 3, 1 squares once: 4 multiplications.', 'The odd ones, 13, 3 and 1, multiply by x once more, but 1 squares 1 × 1, so count carefully: squares at 6, 3 and 13 give 3, plus x at 13, 3 and 1 gives 3.', 'Total <span class="eq">6</span>, far fewer than 12.']},
    {'lv': 'x', 'q': 'In K-th Symbol in Grammar, what is the 6th symbol of row 4?', 'ans': '0', 'hint': 'Row 4 is 01101001.', 'steps': ['Row 4 = 0 1 1 0 1 0 0 1', 'The 6th symbol is <span class="eq">0</span>']},
    {'lv': 'x', 'q': 'At one move per second, how many days does the Tower of Hanoi with 20 discs take? Round down.', 'ans': '12', 'hint': '2²⁰ − 1 seconds, and a day has 86,400 seconds.', 'steps': ['<span class="eq">2²⁰ − 1 = 1,048,575</span> seconds', '<span class="eq">1,048,575 ÷ 86,400 ≈ 12.1</span>, so 12 full days.']},
]

TALK = {
    'what-is-recursion': 'Have you ever seen Russian dolls? You open the big wooden doll and inside is a smaller doll that looks exactly the same. Inside that is a smaller one again, until you reach a tiny doll that does not open at all. Recursion works just like that. A recursive function solves a big problem by handing a smaller version of the very same problem to itself. It keeps doing this until the problem is so small that the answer is obvious, like the tiny solid doll. That obvious answer is called the base case. Then the answers travel back out, each doll closing around the one inside. Factorial is the classic example. Five factorial means five times four times three times two times one. Recursion says five factorial is just five times four factorial, and one factorial is simply one. Two short rules, and the computer does the rest.',
    'call-stack': 'When you are cooking and the recipe says make the sauce first, you put the main dish aside, make the sauce, and then come back to exactly where you were. Computers do this with something called the call stack. Every time a function calls another function, the computer writes a little note, called a frame, saying what it was doing and what its variables were. It puts that note on top of a pile. The newest note is always on top. When the called function finishes, its note is thrown away and the computer carries on from the note underneath. With recursion this pile can grow tall, one note for every call that is still waiting. If it grows too tall, the computer runs out of room. Python then says RecursionError, Java says StackOverflowError, and the famous website for programmers is named after exactly this crash.',
    'recursion-tree': 'Some recursive functions call themselves more than once. Fibonacci is one of them. Each Fibonacci number is the sum of the two before it, so fib of five asks for fib of four and fib of three. But fib of four also asks for fib of three. Draw all the calls and you get a family tree that branches again and again, and the same small questions appear many times. It is like a class where every student asks the teacher the same question separately instead of writing the answer on the board once. For fib of twenty the plain version makes more than twenty thousand calls. The fix is called memoization. You keep a notebook, and before working out an answer you check whether it is already written down. With the notebook, fib of twenty needs only thirty nine calls. That one idea is the seed of dynamic programming, which you will meet later in this subject.',
    'leap-of-faith': 'Many beginners try to follow every single recursive call in their head, and quickly get lost. Experts do something different. They take a small leap of faith. They simply assume that the smaller call already works correctly, and ask only one question: if I had the answer for the smaller problem, how would I build the answer for the big one? To reverse the word hello, trust that reversing ello gives you olle, and then just stick the h on the end. To check whether racecar reads the same both ways, compare the first and last letters, and trust a smaller call to check the middle part. To work out two to the power ten, trust that two to the power five is thirty two, and square it. Thinking this way makes recursive code short, clear and surprisingly easy to write correctly, as long as the base case is right.',
    'hanoi': 'The Tower of Hanoi is a puzzle with three pegs and a stack of discs of different sizes, biggest at the bottom. You must move the whole stack to another peg, one disc at a time, and you may never put a bigger disc on top of a smaller one. With three discs it takes a little thought. With ten discs it seems impossible to plan. Recursion makes it simple. To move ten discs, first move the top nine out of the way onto the spare peg, then move the biggest disc to the target, and then move the nine back on top of it. Moving nine discs is the same puzzle, only smaller. Every extra disc doubles the number of moves and adds one. An old legend says monks are moving sixty four golden discs. At one move a second they would need hundreds of billions of years.',
    'structures': 'Look around your computer and you will find data that contains smaller copies of itself. A folder holds files and other folders, which hold more files and folders. A family tree has parents whose children have children. A web page is made of boxes inside boxes. For data like this, recursion is the most natural tool, because the code can mirror the shape of the data. To find the size of a folder, add up the sizes of its files and then ask each subfolder for its size the same way. To find how tall a tree is, ask the left child how tall it is, ask the right child, take the bigger answer and add one for yourself. An empty spot answers zero, which is the base case. Every node is visited exactly once, so this is fast as well as short.',
    'to-loops': 'Recursion is a wonderful way to think, but the call stack has limited room. A tail call is a recursive call that is the very last thing a function does, with nothing left to do afterwards, like returning gcd of b and a mod b. In theory the computer could throw away the old note before making the new call, so the pile never grows. Some languages do this, but Python, Java and Node do not. So for very deep recursion, programmers turn the code into a loop. A tail call becomes a simple while loop that updates its variables. A branching recursion, like walking every folder, can keep its own to do list on an explicit stack instead of using the call stack. And when sub problems repeat, a memo or a table of answers removes the extra calls. The good habit is to write the clear recursive version first, then change it only if needed.',
    'leetcode': 'The LeetCode problems in this chapter train your recursive thinking step by step. You start with Fibonacci and reversing a string, where the base case and the smaller problem are easy to see. Then you compute powers super fast by halving the exponent, and merge two sorted linked lists by picking the smaller head and trusting the rest to a smaller call. Next you count the ways to climb stairs by thinking about the very last step, and decode nested strings like three a two c by diving into each pair of brackets. The expert problems ask you to find a symbol in a row with half a billion symbols using only thirty calls, and to build your own pattern matcher with dots and stars. Each one has a hint, a full explanation and code in Python, JavaScript, Java and TypeScript.',
}

T = t.finish({
    'slug': 'recursion', 'title': 'Recursion', 'short': 'Recursion', 'emoji': '🪆', 'topic': 'recursion', 'prefix': 'dsarec',
    'module': ('🔁', 'Recursion and smart searching'),
    'lead': 'A function that solves a problem by asking a smaller copy of itself for help. Learn base cases, watch the call stack grow and unwind, tame repeated work with memoization, crack the Tower of Hanoi, walk nested data and trees, and turn deep recursion into loops.',
    'desc': 'Recursion in DSA: base and recursive cases, the call stack and stack overflow, recursion trees and memoization, the recursive leap of faith, the Tower of Hanoi, recursion on nested lists and trees, tail calls and converting recursion to loops, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 20,
    'summary': 'Base cases and recursive cases, the call stack and stack overflow, recursion trees and memoization, the leap of faith, the Tower of Hanoi, recursion on nested data and trees, and turning recursion into loops. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['recursion', 'base case', 'recursive case', 'call stack', 'stack frame', 'stack overflow', 'recursion tree', 'memoization', 'factorial', 'fibonacci', 'tower of hanoi', 'tail recursion', 'tail call', 'fast power', 'palindrome'],
    'added': '2026-11-22',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('stacks-queues', 'stacks-queues', '🥞 Stacks and queues'),
    'next': ('trees', 'trees', '🌲 Trees'),
})
