# Dynamic programming 2: tables over two strings (LCS and edit distance), longest increasing subsequence,
# interval DP on palindromes, subset sums and bitmask DP for the travelling salesperson.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('lcs', py=r'''
def lcs(a, b):
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]   # L[i][j]: the longest common subsequence of a[:i] and b[:j]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1        # matching letters extend the diagonal
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])   # drop the last letter of one word
    out, i, j = [], n, m                             # walk back to read the letters
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i, j = i - 1, j - 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return L[n][m], "".join(reversed(out))


for a, b in (("ABCBDAB", "BDCABA"), ("kitten", "sitting"), ("abc", "xyz")):
    length, common = lcs(a, b)
    print(f'{a} and {b}: length {length}, for example "{common}"')
''', js=r'''
function lcs(a, b) {
  const n = a.length, m = b.length;
  const L = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));   // L[i][j]: LCS of a[:i] and b[:j]
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (a[i - 1] === b[j - 1]) L[i][j] = L[i - 1][j - 1] + 1;   // matching letters extend the diagonal
      else L[i][j] = Math.max(L[i - 1][j], L[i][j - 1]);          // drop the last letter of one word
    }
  }
  const out = [];                                    // walk back to read the letters
  let i = n, j = m;
  while (i > 0 && j > 0) {
    if (a[i - 1] === b[j - 1]) { out.push(a[i - 1]); i--; j--; }
    else if (L[i - 1][j] >= L[i][j - 1]) i--;
    else j--;
  }
  return [L[n][m], out.reverse().join("")];
}

for (const [a, b] of [["ABCBDAB", "BDCABA"], ["kitten", "sitting"], ["abc", "xyz"]]) {
  const [length, common] = lcs(a, b);
  console.log(`${a} and ${b}: length ${length}, for example "${common}"`);
}
''', java=r'''
public class LCS {
    static int length;

    static String lcs(String a, String b) {
        int n = a.length(), m = b.length();
        int[][] L = new int[n + 1][m + 1];           // L[i][j]: the longest common subsequence of a[:i] and b[:j]
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= m; j++) {
                if (a.charAt(i - 1) == b.charAt(j - 1)) L[i][j] = L[i - 1][j - 1] + 1;   // matching letters extend the diagonal
                else L[i][j] = Math.max(L[i - 1][j], L[i][j - 1]);                       // drop the last letter of one word
            }
        StringBuilder out = new StringBuilder();     // walk back to read the letters
        int i = n, j = m;
        while (i > 0 && j > 0) {
            if (a.charAt(i - 1) == b.charAt(j - 1)) { out.append(a.charAt(i - 1)); i--; j--; }
            else if (L[i - 1][j] >= L[i][j - 1]) i--;
            else j--;
        }
        length = L[n][m];
        return out.reverse().toString();
    }

    public static void main(String[] args) {
        String[][] pairs = {{"ABCBDAB", "BDCABA"}, {"kitten", "sitting"}, {"abc", "xyz"}};
        for (String[] p : pairs) {
            String common = lcs(p[0], p[1]);
            System.out.println(p[0] + " and " + p[1] + ": length " + length + ", for example \"" + common + "\"");
        }
    }
}
''', ts=r'''
function lcs(a: string, b: string): [number, string] {
  const n = a.length, m = b.length;
  const L: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));   // LCS of a[:i] and b[:j]
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (a[i - 1] === b[j - 1]) L[i][j] = L[i - 1][j - 1] + 1;   // matching letters extend the diagonal
      else L[i][j] = Math.max(L[i - 1][j], L[i][j - 1]);          // drop the last letter of one word
    }
  }
  const out: string[] = [];                          // walk back to read the letters
  let i = n, j = m;
  while (i > 0 && j > 0) {
    if (a[i - 1] === b[j - 1]) { out.push(a[i - 1]); i--; j--; }
    else if (L[i - 1][j] >= L[i][j - 1]) i--;
    else j--;
  }
  return [L[n][m], out.reverse().join("")];
}

for (const [a, b] of [["ABCBDAB", "BDCABA"], ["kitten", "sitting"], ["abc", "xyz"]]) {
  const [length, common] = lcs(a, b);
  console.log(`${a} and ${b}: length ${length}, for example "${common}"`);
}
''')

t.code('edit', py=r'''
def edit_distance(a, b):
    n, m = len(a), len(b)
    E = [[0] * (m + 1) for _ in range(n + 1)]   # E[i][j]: the fewest edits to turn a[:i] into b[:j]
    for i in range(n + 1):
        E[i][0] = i                              # delete every letter
    for j in range(m + 1):
        E[0][j] = j                              # insert every letter
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                E[i][j] = E[i - 1][j - 1]        # the same letter costs nothing
            else:
                E[i][j] = 1 + min(E[i - 1][j - 1],   # replace
                                  E[i - 1][j],       # delete from a
                                  E[i][j - 1])       # insert into a
    steps, i, j = [], n, m                       # walk back to list the edits
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and E[i][j] == E[i - 1][j - 1] + 1:
            steps.append(f"replace {a[i - 1]} with {b[j - 1]}")
            i, j = i - 1, j - 1
        elif i > 0 and E[i][j] == E[i - 1][j] + 1:
            steps.append(f"delete {a[i - 1]}")
            i -= 1
        else:
            steps.append(f"insert {b[j - 1]}")
            j -= 1
    return E[n][m], steps[::-1]


for a, b in (("kitten", "sitting"), ("horse", "ros"), ("", "abc")):
    d, steps = edit_distance(a, b)
    print(f'"{a}" to "{b}": {d} edits: ' + ", ".join(steps))
''', js=r'''
function editDistance(a, b) {
  const n = a.length, m = b.length;
  const E = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));   // E[i][j]: edits to turn a[:i] into b[:j]
  for (let i = 0; i <= n; i++) E[i][0] = i;          // delete every letter
  for (let j = 0; j <= m; j++) E[0][j] = j;          // insert every letter
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (a[i - 1] === b[j - 1]) E[i][j] = E[i - 1][j - 1];   // the same letter costs nothing
      else E[i][j] = 1 + Math.min(E[i - 1][j - 1], E[i - 1][j], E[i][j - 1]);   // replace, delete, insert
    }
  }
  const steps = [];                                  // walk back to list the edits
  let i = n, j = m;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i - 1] === b[j - 1]) { i--; j--; }
    else if (i > 0 && j > 0 && E[i][j] === E[i - 1][j - 1] + 1) { steps.push(`replace ${a[i - 1]} with ${b[j - 1]}`); i--; j--; }
    else if (i > 0 && E[i][j] === E[i - 1][j] + 1) { steps.push(`delete ${a[i - 1]}`); i--; }
    else { steps.push(`insert ${b[j - 1]}`); j--; }
  }
  return [E[n][m], steps.reverse()];
}

for (const [a, b] of [["kitten", "sitting"], ["horse", "ros"], ["", "abc"]]) {
  const [d, steps] = editDistance(a, b);
  console.log(`"${a}" to "${b}": ${d} edits: ` + steps.join(", "));
}
''', java=r'''
import java.util.*;

public class EditDistance {
    static List<String> steps;

    static int editDistance(String a, String b) {
        int n = a.length(), m = b.length();
        int[][] E = new int[n + 1][m + 1];           // E[i][j]: the fewest edits to turn a[:i] into b[:j]
        for (int i = 0; i <= n; i++) E[i][0] = i;    // delete every letter
        for (int j = 0; j <= m; j++) E[0][j] = j;    // insert every letter
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= m; j++) {
                if (a.charAt(i - 1) == b.charAt(j - 1)) E[i][j] = E[i - 1][j - 1];   // the same letter costs nothing
                else E[i][j] = 1 + Math.min(E[i - 1][j - 1], Math.min(E[i - 1][j], E[i][j - 1]));   // replace, delete, insert
            }
        steps = new ArrayList<>();                   // walk back to list the edits
        int i = n, j = m;
        while (i > 0 || j > 0) {
            if (i > 0 && j > 0 && a.charAt(i - 1) == b.charAt(j - 1)) { i--; j--; }
            else if (i > 0 && j > 0 && E[i][j] == E[i - 1][j - 1] + 1) { steps.add("replace " + a.charAt(i - 1) + " with " + b.charAt(j - 1)); i--; j--; }
            else if (i > 0 && E[i][j] == E[i - 1][j] + 1) { steps.add("delete " + a.charAt(i - 1)); i--; }
            else { steps.add("insert " + b.charAt(j - 1)); j--; }
        }
        Collections.reverse(steps);
        return E[n][m];
    }

    public static void main(String[] args) {
        String[][] pairs = {{"kitten", "sitting"}, {"horse", "ros"}, {"", "abc"}};
        for (String[] p : pairs) {
            int d = editDistance(p[0], p[1]);
            System.out.println("\"" + p[0] + "\" to \"" + p[1] + "\": " + d + " edits: " + String.join(", ", steps));
        }
    }
}
''', ts=r'''
function editDistance(a: string, b: string): [number, string[]] {
  const n = a.length, m = b.length;
  const E: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));   // edits to turn a[:i] into b[:j]
  for (let i = 0; i <= n; i++) E[i][0] = i;          // delete every letter
  for (let j = 0; j <= m; j++) E[0][j] = j;          // insert every letter
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (a[i - 1] === b[j - 1]) E[i][j] = E[i - 1][j - 1];   // the same letter costs nothing
      else E[i][j] = 1 + Math.min(E[i - 1][j - 1], E[i - 1][j], E[i][j - 1]);   // replace, delete, insert
    }
  }
  const steps: string[] = [];                        // walk back to list the edits
  let i = n, j = m;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i - 1] === b[j - 1]) { i--; j--; }
    else if (i > 0 && j > 0 && E[i][j] === E[i - 1][j - 1] + 1) { steps.push(`replace ${a[i - 1]} with ${b[j - 1]}`); i--; j--; }
    else if (i > 0 && E[i][j] === E[i - 1][j] + 1) { steps.push(`delete ${a[i - 1]}`); i--; }
    else { steps.push(`insert ${b[j - 1]}`); j--; }
  }
  return [E[n][m], steps.reverse()];
}

for (const [a, b] of [["kitten", "sitting"], ["horse", "ros"], ["", "abc"]]) {
  const [d, steps] = editDistance(a, b);
  console.log(`"${a}" to "${b}": ${d} edits: ` + steps.join(", "));
}
''')

t.code('lis', py=r'''
from bisect import bisect_left


def lis_table(nums):
    best = [1] * len(nums)                       # best[i]: the longest increasing run that ends at nums[i]
    prev = [-1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i] and best[j] + 1 > best[i]:
                best[i], prev[i] = best[j] + 1, j
    i = best.index(max(best))
    seq = []
    while i != -1:                               # follow prev back to the start of the run
        seq.append(nums[i])
        i = prev[i]
    return seq[::-1]


def lis_length_fast(nums):
    tails = []                                   # tails[k]: the smallest end of any increasing run of length k + 1
    for x in nums:
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)


for nums in ([10, 9, 2, 5, 3, 7, 101, 18], [0, 1, 0, 3, 2, 3], [7, 7, 7]):
    seq = lis_table(nums)
    print(f"{nums}: longest increasing {seq}, length {len(seq)}, fast method says {lis_length_fast(nums)}")
''', js=r'''
function lisTable(nums) {
  const best = new Array(nums.length).fill(1);       // best[i]: the longest increasing run that ends at nums[i]
  const prev = new Array(nums.length).fill(-1);
  for (let i = 0; i < nums.length; i++) {
    for (let j = 0; j < i; j++) {
      if (nums[j] < nums[i] && best[j] + 1 > best[i]) { best[i] = best[j] + 1; prev[i] = j; }
    }
  }
  let i = best.indexOf(Math.max(...best));
  const seq = [];
  while (i !== -1) { seq.push(nums[i]); i = prev[i]; }   // follow prev back to the start of the run
  return seq.reverse();
}

function lisLengthFast(nums) {
  const tails = [];                                  // tails[k]: the smallest end of a run of length k + 1
  for (const x of nums) {
    let lo = 0, hi = tails.length;                   // binary search for the first tail >= x
    while (lo < hi) { const mid = (lo + hi) >> 1; if (tails[mid] < x) lo = mid + 1; else hi = mid; }
    if (lo === tails.length) tails.push(x); else tails[lo] = x;
  }
  return tails.length;
}

for (const nums of [[10, 9, 2, 5, 3, 7, 101, 18], [0, 1, 0, 3, 2, 3], [7, 7, 7]]) {
  const seq = lisTable(nums);
  console.log(`[${nums.join(", ")}]: longest increasing [${seq.join(", ")}], length ${seq.length}, fast method says ${lisLengthFast(nums)}`);
}
''', java=r'''
import java.util.*;

public class LIS {
    static List<Integer> lisTable(int[] nums) {
        int n = nums.length;
        int[] best = new int[n], prev = new int[n];  // best[i]: the longest increasing run that ends at nums[i]
        Arrays.fill(best, 1);
        Arrays.fill(prev, -1);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < i; j++)
                if (nums[j] < nums[i] && best[j] + 1 > best[i]) { best[i] = best[j] + 1; prev[i] = j; }
        int i = 0;
        for (int k = 1; k < n; k++) if (best[k] > best[i]) i = k;
        List<Integer> seq = new ArrayList<>();
        while (i != -1) { seq.add(nums[i]); i = prev[i]; }   // follow prev back to the start of the run
        Collections.reverse(seq);
        return seq;
    }

    static int lisLengthFast(int[] nums) {
        int[] tails = new int[nums.length];          // tails[k]: the smallest end of a run of length k + 1
        int size = 0;
        for (int x : nums) {
            int lo = 0, hi = size;                   // binary search for the first tail >= x
            while (lo < hi) { int mid = (lo + hi) >> 1; if (tails[mid] < x) lo = mid + 1; else hi = mid; }
            tails[lo] = x;
            if (lo == size) size++;
        }
        return size;
    }

    public static void main(String[] args) {
        for (int[] nums : new int[][]{{10, 9, 2, 5, 3, 7, 101, 18}, {0, 1, 0, 3, 2, 3}, {7, 7, 7}}) {
            List<Integer> seq = lisTable(nums);
            System.out.println(Arrays.toString(nums) + ": longest increasing " + seq + ", length " + seq.size() + ", fast method says " + lisLengthFast(nums));
        }
    }
}
''', ts=r'''
function lisTable(nums: number[]): number[] {
  const best: number[] = new Array(nums.length).fill(1);   // best[i]: the longest increasing run that ends at nums[i]
  const prev: number[] = new Array(nums.length).fill(-1);
  for (let i = 0; i < nums.length; i++) {
    for (let j = 0; j < i; j++) {
      if (nums[j] < nums[i] && best[j] + 1 > best[i]) { best[i] = best[j] + 1; prev[i] = j; }
    }
  }
  let i = best.indexOf(Math.max(...best));
  const seq: number[] = [];
  while (i !== -1) { seq.push(nums[i]); i = prev[i]; }   // follow prev back to the start of the run
  return seq.reverse();
}

function lisLengthFast(nums: number[]): number {
  const tails: number[] = [];                        // tails[k]: the smallest end of a run of length k + 1
  for (const x of nums) {
    let lo = 0, hi = tails.length;                   // binary search for the first tail >= x
    while (lo < hi) { const mid = (lo + hi) >> 1; if (tails[mid] < x) lo = mid + 1; else hi = mid; }
    if (lo === tails.length) tails.push(x); else tails[lo] = x;
  }
  return tails.length;
}

for (const nums of [[10, 9, 2, 5, 3, 7, 101, 18], [0, 1, 0, 3, 2, 3], [7, 7, 7]]) {
  const seq = lisTable(nums);
  console.log(`[${nums.join(", ")}]: longest increasing [${seq.join(", ")}], length ${seq.length}, fast method says ${lisLengthFast(nums)}`);
}
''')

t.code('pal', py=r'''
def longest_palindrome_subseq(s):
    n = len(s)
    P = [[0] * n for _ in range(n)]              # P[i][j]: the longest palindrome you can pick from s[i..j]
    for i in range(n):
        P[i][i] = 1                              # one letter is a palindrome
    for length in range(2, n + 1):               # short pieces first, so the inside is always ready
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                P[i][j] = (P[i + 1][j - 1] if length > 2 else 0) + 2   # both ends match: wrap the inside
            else:
                P[i][j] = max(P[i + 1][j], P[i][j - 1])                # drop one end
    return P[0][n - 1]


for s in ("bbbab", "character", "racecar", "abcd"):
    print(s, longest_palindrome_subseq(s))
''', js=r'''
function longestPalindromeSubseq(s) {
  const n = s.length;
  const P = Array.from({ length: n }, () => new Array(n).fill(0));   // P[i][j]: the longest palindrome in s[i..j]
  for (let i = 0; i < n; i++) P[i][i] = 1;           // one letter is a palindrome
  for (let length = 2; length <= n; length++) {      // short pieces first, so the inside is always ready
    for (let i = 0; i + length - 1 < n; i++) {
      const j = i + length - 1;
      if (s[i] === s[j]) P[i][j] = (length > 2 ? P[i + 1][j - 1] : 0) + 2;   // both ends match: wrap the inside
      else P[i][j] = Math.max(P[i + 1][j], P[i][j - 1]);                    // drop one end
    }
  }
  return P[0][n - 1];
}

for (const s of ["bbbab", "character", "racecar", "abcd"]) console.log(s, longestPalindromeSubseq(s));
''', java=r'''
public class PalindromeSubseq {
    static int longestPalindromeSubseq(String s) {
        int n = s.length();
        int[][] P = new int[n][n];                   // P[i][j]: the longest palindrome you can pick from s[i..j]
        for (int i = 0; i < n; i++) P[i][i] = 1;     // one letter is a palindrome
        for (int length = 2; length <= n; length++)  // short pieces first, so the inside is always ready
            for (int i = 0; i + length - 1 < n; i++) {
                int j = i + length - 1;
                if (s.charAt(i) == s.charAt(j)) P[i][j] = (length > 2 ? P[i + 1][j - 1] : 0) + 2;   // wrap the inside
                else P[i][j] = Math.max(P[i + 1][j], P[i][j - 1]);                                // drop one end
            }
        return P[0][n - 1];
    }

    public static void main(String[] args) {
        for (String s : new String[]{"bbbab", "character", "racecar", "abcd"}) System.out.println(s + " " + longestPalindromeSubseq(s));
    }
}
''', ts=r'''
function longestPalindromeSubseq(s: string): number {
  const n = s.length;
  const P: number[][] = Array.from({ length: n }, () => new Array(n).fill(0));   // the longest palindrome in s[i..j]
  for (let i = 0; i < n; i++) P[i][i] = 1;           // one letter is a palindrome
  for (let length = 2; length <= n; length++) {      // short pieces first, so the inside is always ready
    for (let i = 0; i + length - 1 < n; i++) {
      const j = i + length - 1;
      if (s[i] === s[j]) P[i][j] = (length > 2 ? P[i + 1][j - 1] : 0) + 2;   // both ends match: wrap the inside
      else P[i][j] = Math.max(P[i + 1][j], P[i][j - 1]);                    // drop one end
    }
  }
  return P[0][n - 1];
}

for (const s of ["bbbab", "character", "racecar", "abcd"]) console.log(s, longestPalindromeSubseq(s));
''')

t.code('subset', py=r'''
def subset_sums(nums, target):
    can = [True] + [False] * target              # can[s]: some of the numbers seen so far add up to s
    for x in nums:
        for s in range(target, x - 1, -1):       # go downwards so each number is used at most once
            if can[s - x]:
                can[s] = True
    return can


def count_subsets(nums, target):
    ways = [1] + [0] * target                    # ways[s]: how many groups of numbers add up to s
    for x in nums:
        for s in range(target, x - 1, -1):
            ways[s] += ways[s - x]
    return ways[target]


nums = [3, 34, 4, 12, 5, 2]
can = subset_sums(nums, 9)
print(f"{nums}: sums from 0 to 9 that can be made {[s for s in range(10) if can[s]]}")
print("can make 30:", "yes" if subset_sums(nums, 30)[30] else "no")
print(f"groups from [1, 2, 3, 4, 5] adding up to 5: {count_subsets([1, 2, 3, 4, 5], 5)}")
''', js=r'''
function subsetSums(nums, target) {
  const can = [true, ...new Array(target).fill(false)];   // can[s]: some of the numbers seen so far add up to s
  for (const x of nums) {
    for (let s = target; s >= x; s--) if (can[s - x]) can[s] = true;   // downwards: each number used at most once
  }
  return can;
}

function countSubsets(nums, target) {
  const ways = [1, ...new Array(target).fill(0)];   // ways[s]: how many groups of numbers add up to s
  for (const x of nums) {
    for (let s = target; s >= x; s--) ways[s] += ways[s - x];
  }
  return ways[target];
}

const nums = [3, 34, 4, 12, 5, 2];
const can = subsetSums(nums, 9);
const made = [];
for (let s = 0; s < 10; s++) if (can[s]) made.push(s);
console.log(`[${nums.join(", ")}]: sums from 0 to 9 that can be made [${made.join(", ")}]`);
console.log("can make 30:", subsetSums(nums, 30)[30] ? "yes" : "no");
console.log(`groups from [1, 2, 3, 4, 5] adding up to 5: ${countSubsets([1, 2, 3, 4, 5], 5)}`);
''', java=r'''
import java.util.*;

public class SubsetSum {
    static boolean[] subsetSums(int[] nums, int target) {
        boolean[] can = new boolean[target + 1];     // can[s]: some of the numbers seen so far add up to s
        can[0] = true;
        for (int x : nums)
            for (int s = target; s >= x; s--)        // go downwards so each number is used at most once
                if (can[s - x]) can[s] = true;
        return can;
    }

    static int countSubsets(int[] nums, int target) {
        int[] ways = new int[target + 1];            // ways[s]: how many groups of numbers add up to s
        ways[0] = 1;
        for (int x : nums)
            for (int s = target; s >= x; s--) ways[s] += ways[s - x];
        return ways[target];
    }

    public static void main(String[] args) {
        int[] nums = {3, 34, 4, 12, 5, 2};
        boolean[] can = subsetSums(nums, 9);
        List<Integer> made = new ArrayList<>();
        for (int s = 0; s < 10; s++) if (can[s]) made.add(s);
        System.out.println(Arrays.toString(nums) + ": sums from 0 to 9 that can be made " + made);
        System.out.println("can make 30: " + (subsetSums(nums, 30)[30] ? "yes" : "no"));
        System.out.println("groups from [1, 2, 3, 4, 5] adding up to 5: " + countSubsets(new int[]{1, 2, 3, 4, 5}, 5));
    }
}
''', ts=r'''
function subsetSums(nums: number[], target: number): boolean[] {
  const can: boolean[] = [true, ...new Array(target).fill(false)];   // some of the numbers seen so far add up to s
  for (const x of nums) {
    for (let s = target; s >= x; s--) if (can[s - x]) can[s] = true;   // downwards: each number used at most once
  }
  return can;
}

function countSubsets(nums: number[], target: number): number {
  const ways: number[] = [1, ...new Array(target).fill(0)];   // ways[s]: how many groups of numbers add up to s
  for (const x of nums) {
    for (let s = target; s >= x; s--) ways[s] += ways[s - x];
  }
  return ways[target];
}

const nums = [3, 34, 4, 12, 5, 2];
const can = subsetSums(nums, 9);
const made: number[] = [];
for (let s = 0; s < 10; s++) if (can[s]) made.push(s);
console.log(`[${nums.join(", ")}]: sums from 0 to 9 that can be made [${made.join(", ")}]`);
console.log("can make 30:", subsetSums(nums, 30)[30] ? "yes" : "no");
console.log(`groups from [1, 2, 3, 4, 5] adding up to 5: ${countSubsets([1, 2, 3, 4, 5], 5)}`);
''')

t.code('tsp', py=r'''
def shortest_tour(dist):
    n = len(dist)
    FULL = 1 << n
    NONE = 10 ** 9
    best = [[NONE] * n for _ in range(FULL)]     # best[mask][v]: shortest route from 0 through the cities in mask, ending at v
    came = [[-1] * n for _ in range(FULL)]
    best[1][0] = 0                               # only city 0 visited, standing at city 0
    for mask in range(FULL):
        for v in range(n):
            if best[mask][v] == NONE:
                continue
            for w in range(n):
                if mask & (1 << w) == 0:         # w is not visited yet
                    nxt = mask | (1 << w)
                    if best[mask][v] + dist[v][w] < best[nxt][w]:
                        best[nxt][w] = best[mask][v] + dist[v][w]
                        came[nxt][w] = v
    end = min(range(1, n), key=lambda v: best[FULL - 1][v] + dist[v][0])
    total = best[FULL - 1][end] + dist[end][0]
    route, mask, v = [], FULL - 1, end           # walk back through came
    while v != -1:
        route.append(v)
        mask, v = mask ^ (1 << v), came[mask][v]
    return total, route[::-1] + [0]


dist = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
total, route = shortest_tour(dist)
print(f"shortest tour {total}: " + " ".join(str(c) for c in route))
''', js=r'''
function shortestTour(dist) {
  const n = dist.length, FULL = 1 << n, NONE = 1e9;
  const best = Array.from({ length: FULL }, () => new Array(n).fill(NONE));   // best[mask][v]: route through mask, ending at v
  const came = Array.from({ length: FULL }, () => new Array(n).fill(-1));
  best[1][0] = 0;                                    // only city 0 visited, standing at city 0
  for (let mask = 0; mask < FULL; mask++) {
    for (let v = 0; v < n; v++) {
      if (best[mask][v] === NONE) continue;
      for (let w = 0; w < n; w++) {
        if ((mask & (1 << w)) === 0) {               // w is not visited yet
          const nxt = mask | (1 << w);
          if (best[mask][v] + dist[v][w] < best[nxt][w]) { best[nxt][w] = best[mask][v] + dist[v][w]; came[nxt][w] = v; }
        }
      }
    }
  }
  let end = 1;
  for (let v = 2; v < n; v++) if (best[FULL - 1][v] + dist[v][0] < best[FULL - 1][end] + dist[end][0]) end = v;
  const total = best[FULL - 1][end] + dist[end][0];
  const route = [];                                  // walk back through came
  let mask = FULL - 1, v = end;
  while (v !== -1) { route.push(v); const p = came[mask][v]; mask ^= 1 << v; v = p; }
  return [total, route.reverse().concat([0])];
}

const dist = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]];
const [total, route] = shortestTour(dist);
console.log(`shortest tour ${total}: ` + route.join(" "));
''', java=r'''
import java.util.*;

public class ShortestTour {
    public static void main(String[] args) {
        int[][] dist = {{0, 10, 15, 20}, {10, 0, 35, 25}, {15, 35, 0, 30}, {20, 25, 30, 0}};
        int n = dist.length, FULL = 1 << n, NONE = 1_000_000_000;
        int[][] best = new int[FULL][n], came = new int[FULL][n];   // best[mask][v]: route through mask, ending at v
        for (int[] r : best) Arrays.fill(r, NONE);
        for (int[] r : came) Arrays.fill(r, -1);
        best[1][0] = 0;                              // only city 0 visited, standing at city 0
        for (int mask = 0; mask < FULL; mask++)
            for (int v = 0; v < n; v++) {
                if (best[mask][v] == NONE) continue;
                for (int w = 0; w < n; w++)
                    if ((mask & (1 << w)) == 0) {    // w is not visited yet
                        int nxt = mask | (1 << w);
                        if (best[mask][v] + dist[v][w] < best[nxt][w]) { best[nxt][w] = best[mask][v] + dist[v][w]; came[nxt][w] = v; }
                    }
            }
        int end = 1;
        for (int v = 2; v < n; v++) if (best[FULL - 1][v] + dist[v][0] < best[FULL - 1][end] + dist[end][0]) end = v;
        int total = best[FULL - 1][end] + dist[end][0];
        List<Integer> route = new ArrayList<>();     // walk back through came
        int mask = FULL - 1, v = end;
        while (v != -1) { route.add(v); int p = came[mask][v]; mask ^= 1 << v; v = p; }
        Collections.reverse(route);
        route.add(0);
        StringBuilder sb = new StringBuilder();
        for (int k = 0; k < route.size(); k++) sb.append(k > 0 ? " " : "").append(route.get(k));
        System.out.println("shortest tour " + total + ": " + sb);
    }
}
''', ts=r'''
function shortestTour(dist: number[][]): [number, number[]] {
  const n = dist.length, FULL = 1 << n, NONE = 1e9;
  const best: number[][] = Array.from({ length: FULL }, () => new Array(n).fill(NONE));   // route through mask, ending at v
  const came: number[][] = Array.from({ length: FULL }, () => new Array(n).fill(-1));
  best[1][0] = 0;                                    // only city 0 visited, standing at city 0
  for (let mask = 0; mask < FULL; mask++) {
    for (let v = 0; v < n; v++) {
      if (best[mask][v] === NONE) continue;
      for (let w = 0; w < n; w++) {
        if ((mask & (1 << w)) === 0) {               // w is not visited yet
          const nxt = mask | (1 << w);
          if (best[mask][v] + dist[v][w] < best[nxt][w]) { best[nxt][w] = best[mask][v] + dist[v][w]; came[nxt][w] = v; }
        }
      }
    }
  }
  let end = 1;
  for (let v = 2; v < n; v++) if (best[FULL - 1][v] + dist[v][0] < best[FULL - 1][end] + dist[end][0]) end = v;
  const total = best[FULL - 1][end] + dist[end][0];
  const route: number[] = [];                        // walk back through came
  let mask = FULL - 1, v = end;
  while (v !== -1) { route.push(v); const p = came[mask][v]; mask ^= 1 << v; v = p; }
  return [total, route.reverse().concat([0])];
}

const dist: number[][] = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]];
const [total, route] = shortestTour(dist);
console.log(`shortest tour ${total}: ` + route.join(" "));
''')

# ---------------------------------------------------------------- LeetCode programs
t.code('p_lcs', py=r'''
def longest_common_subsequence(text1, text2):
    prev = [0] * (len(text2) + 1)                # one row of the table is enough
    for a in text1:
        cur = [0]
        for j, b in enumerate(text2, 1):
            cur.append(prev[j - 1] + 1 if a == b else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


print(longest_common_subsequence("abcde", "ace"), longest_common_subsequence("abc", "abc"), longest_common_subsequence("abc", "def"))
''', js=r'''
function longestCommonSubsequence(text1, text2) {
  let prev = new Array(text2.length + 1).fill(0);    // one row of the table is enough
  for (const a of text1) {
    const cur = [0];
    for (let j = 1; j <= text2.length; j++) cur.push(a === text2[j - 1] ? prev[j - 1] + 1 : Math.max(prev[j], cur[j - 1]));
    prev = cur;
  }
  return prev[text2.length];
}

console.log(longestCommonSubsequence("abcde", "ace"), longestCommonSubsequence("abc", "abc"), longestCommonSubsequence("abc", "def"));
''', java=r'''
public class LongestCommonSubsequence {
    static int longestCommonSubsequence(String text1, String text2) {
        int m = text2.length();
        int[] prev = new int[m + 1];                 // one row of the table is enough
        for (int i = 0; i < text1.length(); i++) {
            int[] cur = new int[m + 1];
            for (int j = 1; j <= m; j++)
                cur[j] = text1.charAt(i) == text2.charAt(j - 1) ? prev[j - 1] + 1 : Math.max(prev[j], cur[j - 1]);
            prev = cur;
        }
        return prev[m];
    }

    public static void main(String[] args) {
        System.out.println(longestCommonSubsequence("abcde", "ace") + " " + longestCommonSubsequence("abc", "abc") + " " + longestCommonSubsequence("abc", "def"));
    }
}
''', ts=r'''
function longestCommonSubsequence(text1: string, text2: string): number {
  let prev: number[] = new Array(text2.length + 1).fill(0);   // one row of the table is enough
  for (const a of text1) {
    const cur: number[] = [0];
    for (let j = 1; j <= text2.length; j++) cur.push(a === text2[j - 1] ? prev[j - 1] + 1 : Math.max(prev[j], cur[j - 1]));
    prev = cur;
  }
  return prev[text2.length];
}

console.log(longestCommonSubsequence("abcde", "ace"), longestCommonSubsequence("abc", "abc"), longestCommonSubsequence("abc", "def"));
''')

t.code('p_bst', py=r'''
def num_trees(n):
    count = [1, 1] + [0] * (n - 1)               # count[k]: shapes of a search tree with k keys
    for k in range(2, n + 1):
        for root in range(1, k + 1):             # root splits the keys into a left part and a right part
            count[k] += count[root - 1] * count[k - root]
    return count[n]


print(num_trees(1), num_trees(3), num_trees(5), num_trees(10))
''', js=r'''
function numTrees(n) {
  const count = [1, 1, ...new Array(n - 1).fill(0)]; // count[k]: shapes of a search tree with k keys
  for (let k = 2; k <= n; k++) {
    for (let root = 1; root <= k; root++) count[k] += count[root - 1] * count[k - root];   // left part times right part
  }
  return count[n];
}

console.log(numTrees(1), numTrees(3), numTrees(5), numTrees(10));
''', java=r'''
public class UniqueBSTs {
    static int numTrees(int n) {
        int[] count = new int[Math.max(n + 1, 2)];   // count[k]: shapes of a search tree with k keys
        count[0] = 1;
        count[1] = 1;
        for (int k = 2; k <= n; k++)
            for (int root = 1; root <= k; root++) count[k] += count[root - 1] * count[k - root];   // left part times right part
        return count[n];
    }

    public static void main(String[] args) {
        System.out.println(numTrees(1) + " " + numTrees(3) + " " + numTrees(5) + " " + numTrees(10));
    }
}
''', ts=r'''
function numTrees(n: number): number {
  const count: number[] = [1, 1, ...new Array(Math.max(n - 1, 0)).fill(0)];   // count[k]: shapes with k keys
  for (let k = 2; k <= n; k++) {
    for (let root = 1; root <= k; root++) count[k] += count[root - 1] * count[k - root];   // left part times right part
  }
  return count[n];
}

console.log(numTrees(1), numTrees(3), numTrees(5), numTrees(10));
''')

t.code('p_lis', py=r'''
from bisect import bisect_left


def length_of_lis(nums):
    tails = []                                   # tails[k]: the smallest end of an increasing run of length k + 1
    for x in nums:
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)                      # x makes the longest run one longer
        else:
            tails[k] = x                         # x is a smaller end for runs of length k + 1
    return len(tails)


print(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]), length_of_lis([0, 1, 0, 3, 2, 3]), length_of_lis([7, 7, 7, 7]))
''', js=r'''
function lengthOfLIS(nums) {
  const tails = [];                                  // tails[k]: the smallest end of a run of length k + 1
  for (const x of nums) {
    let lo = 0, hi = tails.length;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (tails[mid] < x) lo = mid + 1; else hi = mid; }
    if (lo === tails.length) tails.push(x);          // x makes the longest run one longer
    else tails[lo] = x;                              // x is a smaller end for runs of length lo + 1
  }
  return tails.length;
}

console.log(lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]), lengthOfLIS([0, 1, 0, 3, 2, 3]), lengthOfLIS([7, 7, 7, 7]));
''', java=r'''
public class LengthOfLIS {
    static int lengthOfLIS(int[] nums) {
        int[] tails = new int[nums.length];          // tails[k]: the smallest end of a run of length k + 1
        int size = 0;
        for (int x : nums) {
            int lo = 0, hi = size;
            while (lo < hi) { int mid = (lo + hi) >> 1; if (tails[mid] < x) lo = mid + 1; else hi = mid; }
            tails[lo] = x;                           // a new longest run, or a smaller end for an old length
            if (lo == size) size++;
        }
        return size;
    }

    public static void main(String[] args) {
        System.out.println(lengthOfLIS(new int[]{10, 9, 2, 5, 3, 7, 101, 18}) + " " + lengthOfLIS(new int[]{0, 1, 0, 3, 2, 3}) + " " + lengthOfLIS(new int[]{7, 7, 7, 7}));
    }
}
''', ts=r'''
function lengthOfLIS(nums: number[]): number {
  const tails: number[] = [];                        // tails[k]: the smallest end of a run of length k + 1
  for (const x of nums) {
    let lo = 0, hi = tails.length;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (tails[mid] < x) lo = mid + 1; else hi = mid; }
    if (lo === tails.length) tails.push(x);          // x makes the longest run one longer
    else tails[lo] = x;                              // x is a smaller end for runs of length lo + 1
  }
  return tails.length;
}

console.log(lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]), lengthOfLIS([0, 1, 0, 3, 2, 3]), lengthOfLIS([7, 7, 7, 7]));
''')

t.code('p_square', py=r'''
def maximal_square(matrix):
    rows, cols = len(matrix), len(matrix[0])
    side = [[0] * (cols + 1) for _ in range(rows + 1)]   # side[r + 1][c + 1]: the biggest square of 1s ending at (r, c)
    biggest = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == "1":
                side[r + 1][c + 1] = 1 + min(side[r][c + 1], side[r + 1][c], side[r][c])   # up, left, diagonal
                biggest = max(biggest, side[r + 1][c + 1])
    return biggest * biggest


m = [["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]]
print(maximal_square(m), maximal_square([["0", "1"], ["1", "0"]]), maximal_square([["0"]]))
''', js=r'''
function maximalSquare(matrix) {
  const rows = matrix.length, cols = matrix[0].length;
  const side = Array.from({ length: rows + 1 }, () => new Array(cols + 1).fill(0));   // biggest square ending at (r, c)
  let biggest = 0;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (matrix[r][c] === "1") {
        side[r + 1][c + 1] = 1 + Math.min(side[r][c + 1], side[r + 1][c], side[r][c]);   // up, left, diagonal
        biggest = Math.max(biggest, side[r + 1][c + 1]);
      }
    }
  }
  return biggest * biggest;
}

const m = [["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]];
console.log(maximalSquare(m), maximalSquare([["0", "1"], ["1", "0"]]), maximalSquare([["0"]]));
''', java=r'''
public class MaximalSquare {
    static int maximalSquare(char[][] matrix) {
        int rows = matrix.length, cols = matrix[0].length, biggest = 0;
        int[][] side = new int[rows + 1][cols + 1];  // side[r + 1][c + 1]: the biggest square of 1s ending at (r, c)
        for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
                if (matrix[r][c] == '1') {
                    side[r + 1][c + 1] = 1 + Math.min(side[r][c + 1], Math.min(side[r + 1][c], side[r][c]));   // up, left, diagonal
                    biggest = Math.max(biggest, side[r + 1][c + 1]);
                }
        return biggest * biggest;
    }

    public static void main(String[] args) {
        char[][] m = {"10100".toCharArray(), "10111".toCharArray(), "11111".toCharArray(), "10010".toCharArray()};
        System.out.println(maximalSquare(m) + " " + maximalSquare(new char[][]{"01".toCharArray(), "10".toCharArray()}) + " " + maximalSquare(new char[][]{"0".toCharArray()}));
    }
}
''', ts=r'''
function maximalSquare(matrix: string[][]): number {
  const rows = matrix.length, cols = matrix[0].length;
  const side: number[][] = Array.from({ length: rows + 1 }, () => new Array(cols + 1).fill(0));   // biggest square ending at (r, c)
  let biggest = 0;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (matrix[r][c] === "1") {
        side[r + 1][c + 1] = 1 + Math.min(side[r][c + 1], side[r + 1][c], side[r][c]);   // up, left, diagonal
        biggest = Math.max(biggest, side[r + 1][c + 1]);
      }
    }
  }
  return biggest * biggest;
}

const m: string[][] = [["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]];
console.log(maximalSquare(m), maximalSquare([["0", "1"], ["1", "0"]]), maximalSquare([["0"]]));
''')

t.code('p_palin', py=r'''
def longest_palindrome(s):
    start, size = 0, 1
    for mid in range(len(s)):
        for lo, hi in ((mid, mid), (mid, mid + 1)):   # odd length around a letter, even length between two
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo, hi = lo - 1, hi + 1
            if hi - lo - 1 > size:
                start, size = lo + 1, hi - lo - 1
    return s[start:start + size]


for s in ("babad", "cbbd", "forgeeksskeegfor", "a"):
    print(s, longest_palindrome(s))
''', js=r'''
function longestPalindrome(s) {
  let start = 0, size = 1;
  for (let mid = 0; mid < s.length; mid++) {
    for (const [a, b] of [[mid, mid], [mid, mid + 1]]) {   // odd length around a letter, even length between two
      let lo = a, hi = b;
      while (lo >= 0 && hi < s.length && s[lo] === s[hi]) { lo--; hi++; }
      if (hi - lo - 1 > size) { start = lo + 1; size = hi - lo - 1; }
    }
  }
  return s.slice(start, start + size);
}

for (const s of ["babad", "cbbd", "forgeeksskeegfor", "a"]) console.log(s, longestPalindrome(s));
''', java=r'''
public class LongestPalindrome {
    static String longestPalindrome(String s) {
        int start = 0, size = 1;
        for (int mid = 0; mid < s.length(); mid++)
            for (int[] p : new int[][]{{mid, mid}, {mid, mid + 1}}) {   // odd length around a letter, even length between two
                int lo = p[0], hi = p[1];
                while (lo >= 0 && hi < s.length() && s.charAt(lo) == s.charAt(hi)) { lo--; hi++; }
                if (hi - lo - 1 > size) { start = lo + 1; size = hi - lo - 1; }
            }
        return s.substring(start, start + size);
    }

    public static void main(String[] args) {
        for (String s : new String[]{"babad", "cbbd", "forgeeksskeegfor", "a"}) System.out.println(s + " " + longestPalindrome(s));
    }
}
''', ts=r'''
function longestPalindrome(s: string): string {
  let start = 0, size = 1;
  for (let mid = 0; mid < s.length; mid++) {
    for (const [a, b] of [[mid, mid], [mid, mid + 1]]) {   // odd length around a letter, even length between two
      let lo = a, hi = b;
      while (lo >= 0 && hi < s.length && s[lo] === s[hi]) { lo--; hi++; }
      if (hi - lo - 1 > size) { start = lo + 1; size = hi - lo - 1; }
    }
  }
  return s.slice(start, start + size);
}

for (const s of ["babad", "cbbd", "forgeeksskeegfor", "a"]) console.log(s, longestPalindrome(s));
''')

t.code('p_target', py=r'''
def find_target_sum_ways(nums, target):
    total = sum(nums)
    if abs(target) > total or (total + target) % 2:
        return 0
    want = (total + target) // 2                 # the numbers given a plus sign must add up to this
    ways = [1] + [0] * want
    for x in nums:
        for s in range(want, x - 1, -1):         # downwards, so each number is used once
            ways[s] += ways[s - x]
    return ways[want]


print(find_target_sum_ways([1, 1, 1, 1, 1], 3), find_target_sum_ways([1], 1), find_target_sum_ways([1, 2, 3], 7))
''', js=r'''
function findTargetSumWays(nums, target) {
  const total = nums.reduce((a, b) => a + b, 0);
  if (Math.abs(target) > total || (total + target) % 2) return 0;
  const want = (total + target) / 2;                 // the numbers given a plus sign must add up to this
  const ways = [1, ...new Array(want).fill(0)];
  for (const x of nums) {
    for (let s = want; s >= x; s--) ways[s] += ways[s - x];   // downwards, so each number is used once
  }
  return ways[want];
}

console.log(findTargetSumWays([1, 1, 1, 1, 1], 3), findTargetSumWays([1], 1), findTargetSumWays([1, 2, 3], 7));
''', java=r'''
public class TargetSum {
    static int findTargetSumWays(int[] nums, int target) {
        int total = 0;
        for (int x : nums) total += x;
        if (Math.abs(target) > total || (total + target) % 2 != 0) return 0;
        int want = (total + target) / 2;             // the numbers given a plus sign must add up to this
        int[] ways = new int[want + 1];
        ways[0] = 1;
        for (int x : nums)
            for (int s = want; s >= x; s--) ways[s] += ways[s - x];   // downwards, so each number is used once
        return ways[want];
    }

    public static void main(String[] args) {
        System.out.println(findTargetSumWays(new int[]{1, 1, 1, 1, 1}, 3) + " " + findTargetSumWays(new int[]{1}, 1) + " " + findTargetSumWays(new int[]{1, 2, 3}, 7));
    }
}
''', ts=r'''
function findTargetSumWays(nums: number[], target: number): number {
  const total = nums.reduce((a, b) => a + b, 0);
  if (Math.abs(target) > total || (total + target) % 2) return 0;
  const want = (total + target) / 2;                 // the numbers given a plus sign must add up to this
  const ways: number[] = [1, ...new Array(want).fill(0)];
  for (const x of nums) {
    for (let s = want; s >= x; s--) ways[s] += ways[s - x];   // downwards, so each number is used once
  }
  return ways[want];
}

console.log(findTargetSumWays([1, 1, 1, 1, 1], 3), findTargetSumWays([1], 1), findTargetSumWays([1, 2, 3], 7));
''')

t.code('p_jobs', py=r'''
from bisect import bisect_right


def job_scheduling(start_time, end_time, profit):
    jobs = sorted(zip(end_time, start_time, profit))   # by end time
    ends = [e for e, _, _ in jobs]
    best = [0] * (len(jobs) + 1)                 # best[i]: the most profit from the first i jobs
    for i, (e, s, p) in enumerate(jobs):
        k = bisect_right(ends, s, 0, i)          # jobs that end by the time this one starts
        best[i + 1] = max(best[i], best[k] + p)  # skip this job, or take it after those
    return best[-1]


print(job_scheduling([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]))
print(job_scheduling([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60]))
print(job_scheduling([1, 1, 1], [2, 3, 4], [5, 6, 4]))
''', js=r'''
function jobScheduling(startTime, endTime, profit) {
  const jobs = startTime.map((s, i) => [endTime[i], s, profit[i]]).sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);   // by end time
  const best = new Array(jobs.length + 1).fill(0);   // best[i]: the most profit from the first i jobs
  jobs.forEach(([e, s, p], i) => {
    let lo = 0, hi = i;                              // count the jobs that end by the time this one starts
    while (lo < hi) { const mid = (lo + hi) >> 1; if (jobs[mid][0] <= s) lo = mid + 1; else hi = mid; }
    best[i + 1] = Math.max(best[i], best[lo] + p);   // skip this job, or take it after those
  });
  return best[jobs.length];
}

console.log(jobScheduling([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]));
console.log(jobScheduling([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60]));
console.log(jobScheduling([1, 1, 1], [2, 3, 4], [5, 6, 4]));
''', java=r'''
import java.util.*;

public class JobScheduling {
    static int jobScheduling(int[] startTime, int[] endTime, int[] profit) {
        int n = startTime.length;
        int[][] jobs = new int[n][];
        for (int i = 0; i < n; i++) jobs[i] = new int[]{endTime[i], startTime[i], profit[i]};
        Arrays.sort(jobs, (a, b) -> a[0] != b[0] ? a[0] - b[0] : a[1] != b[1] ? a[1] - b[1] : a[2] - b[2]);   // by end time
        int[] best = new int[n + 1];                 // best[i]: the most profit from the first i jobs
        for (int i = 0; i < n; i++) {
            int s = jobs[i][1], lo = 0, hi = i;      // count the jobs that end by the time this one starts
            while (lo < hi) { int mid = (lo + hi) >> 1; if (jobs[mid][0] <= s) lo = mid + 1; else hi = mid; }
            best[i + 1] = Math.max(best[i], best[lo] + jobs[i][2]);   // skip this job, or take it after those
        }
        return best[n];
    }

    public static void main(String[] args) {
        System.out.println(jobScheduling(new int[]{1, 2, 3, 3}, new int[]{3, 4, 5, 6}, new int[]{50, 10, 40, 70}));
        System.out.println(jobScheduling(new int[]{1, 2, 3, 4, 6}, new int[]{3, 5, 10, 6, 9}, new int[]{20, 20, 100, 70, 60}));
        System.out.println(jobScheduling(new int[]{1, 1, 1}, new int[]{2, 3, 4}, new int[]{5, 6, 4}));
    }
}
''', ts=r'''
function jobScheduling(startTime: number[], endTime: number[], profit: number[]): number {
  const jobs: number[][] = startTime.map((s, i) => [endTime[i], s, profit[i]]).sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);   // by end time
  const best: number[] = new Array(jobs.length + 1).fill(0);   // best[i]: the most profit from the first i jobs
  jobs.forEach(([e, s, p], i) => {
    let lo = 0, hi = i;                              // count the jobs that end by the time this one starts
    while (lo < hi) { const mid = (lo + hi) >> 1; if (jobs[mid][0] <= s) lo = mid + 1; else hi = mid; }
    best[i + 1] = Math.max(best[i], best[lo] + p);   // skip this job, or take it after those
  });
  return best[jobs.length];
}

console.log(jobScheduling([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]));
console.log(jobScheduling([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60]));
console.log(jobScheduling([1, 1, 1], [2, 3, 4], [5, 6, 4]));
''')

t.code('p_regex', py=r'''
def is_match(s, p):
    n, m = len(s), len(p)
    ok = [[False] * (m + 1) for _ in range(n + 1)]   # ok[i][j]: s[:i] matches p[:j]
    ok[0][0] = True
    for j in range(2, m + 1):
        ok[0][j] = p[j - 1] == "*" and ok[0][j - 2]  # x* can match nothing
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                same = p[j - 2] in (s[i - 1], ".")
                ok[i][j] = ok[i][j - 2] or (same and ok[i - 1][j])   # use x* zero times, or once more
            else:
                ok[i][j] = p[j - 1] in (s[i - 1], ".") and ok[i - 1][j - 1]
    return ok[n][m]


for s, p in (("aa", "a"), ("aa", "a*"), ("ab", ".*"), ("aab", "c*a*b"), ("mississippi", "mis*is*p*.")):
    print(s, p, "true" if is_match(s, p) else "false")
''', js=r'''
function isMatch(s, p) {
  const n = s.length, m = p.length;
  const ok = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(false));   // ok[i][j]: s[:i] matches p[:j]
  ok[0][0] = true;
  for (let j = 2; j <= m; j++) ok[0][j] = p[j - 1] === "*" && ok[0][j - 2];   // x* can match nothing
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (p[j - 1] === "*") {
        const same = p[j - 2] === s[i - 1] || p[j - 2] === ".";
        ok[i][j] = ok[i][j - 2] || (same && ok[i - 1][j]);   // use x* zero times, or once more
      } else {
        ok[i][j] = (p[j - 1] === s[i - 1] || p[j - 1] === ".") && ok[i - 1][j - 1];
      }
    }
  }
  return ok[n][m];
}

for (const [s, p] of [["aa", "a"], ["aa", "a*"], ["ab", ".*"], ["aab", "c*a*b"], ["mississippi", "mis*is*p*."]]) console.log(s, p, isMatch(s, p));
''', java=r'''
public class RegexMatch {
    static boolean isMatch(String s, String p) {
        int n = s.length(), m = p.length();
        boolean[][] ok = new boolean[n + 1][m + 1];  // ok[i][j]: s[:i] matches p[:j]
        ok[0][0] = true;
        for (int j = 2; j <= m; j++) ok[0][j] = p.charAt(j - 1) == '*' && ok[0][j - 2];   // x* can match nothing
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= m; j++) {
                char pc = p.charAt(j - 1), sc = s.charAt(i - 1);
                if (pc == '*') {
                    boolean same = p.charAt(j - 2) == sc || p.charAt(j - 2) == '.';
                    ok[i][j] = ok[i][j - 2] || (same && ok[i - 1][j]);   // use x* zero times, or once more
                } else {
                    ok[i][j] = (pc == sc || pc == '.') && ok[i - 1][j - 1];
                }
            }
        return ok[n][m];
    }

    public static void main(String[] args) {
        String[][] cases = {{"aa", "a"}, {"aa", "a*"}, {"ab", ".*"}, {"aab", "c*a*b"}, {"mississippi", "mis*is*p*."}};
        for (String[] c : cases) System.out.println(c[0] + " " + c[1] + " " + isMatch(c[0], c[1]));
    }
}
''', ts=r'''
function isMatch(s: string, p: string): boolean {
  const n = s.length, m = p.length;
  const ok: boolean[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(false));   // s[:i] matches p[:j]
  ok[0][0] = true;
  for (let j = 2; j <= m; j++) ok[0][j] = p[j - 1] === "*" && ok[0][j - 2];   // x* can match nothing
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (p[j - 1] === "*") {
        const same = p[j - 2] === s[i - 1] || p[j - 2] === ".";
        ok[i][j] = ok[i][j - 2] || (same && ok[i - 1][j]);   // use x* zero times, or once more
      } else {
        ok[i][j] = (p[j - 1] === s[i - 1] || p[j - 1] === ".") && ok[i - 1][j - 1];
      }
    }
  }
  return ok[n][m];
}

for (const [s, p] of [["aa", "a"], ["aa", "a*"], ["ab", ".*"], ["aab", "c*a*b"], ["mississippi", "mis*is*p*."]]) console.log(s, p, isMatch(s, p));
''')

# ---------------------------------------------------------------- practice
t.leet(1143, 'e', 'p_lcs',
       statement='<p>Return the length of the longest common subsequence of two strings: letters that appear in both, in the same order, though not necessarily next to each other.</p>',
       example='"abcde", "ace"  →  3\n"abc", "abc"    →  3\n"abc", "def"    →  0',
       hint='Same table as the lesson. Each row only needs the row above.',
       approach='<p>Fill the table one row at a time. If the letters match, take the diagonal plus 1. Otherwise take the bigger of the box above and the box on the left. Only the previous row is needed, so the space drops to one row.</p>',
       time='O(n × m)', space='O(m)')
t.leet(96, 'e', 'p_bst',
       statement='<p>Return how many differently shaped binary search trees can hold the keys 1 to n.</p>',
       example='n = 1   →  1\nn = 3   →  5\nn = 5   →  42',
       hint='Pick the root. The keys below it form the left tree and the keys above it form the right tree.',
       approach='<p>If key r is the root, the r − 1 smaller keys form the left tree and the k − r larger keys form the right tree. Any left shape can pair with any right shape, so multiply the two counts and add them up over every root. These are the Catalan numbers 1, 1, 2, 5, 14, 42.</p>',
       time='O(n²)', space='O(n)')
t.leet(300, 'm', 'p_lis',
       statement='<p>Return the length of the longest strictly increasing subsequence of an array.</p>',
       example='[10,9,2,5,3,7,101,18]  →  4\n[0,1,0,3,2,3]          →  4\n[7,7,7,7]              →  1',
       hint='Keep the smallest possible end for each length.',
       approach='<p>The O(n²) table works, but the fast method keeps a sorted list of the smallest ending value for every length. For each number, binary search for the first end that is not smaller. Replace it, or append when the number beats every end. The list length is the answer.</p>',
       time='O(n log n)', space='O(n)')
t.leet(221, 'm', 'p_square',
       statement='<p>In a grid of "0" and "1", return the area of the largest square that contains only "1".</p>',
       example='["10100","10111","11111","10010"]  →  4\n["01","10"]                        →  1\n["0"]                              →  0',
       hint='A square ending at a cell is limited by the squares ending above, on the left and on the diagonal.',
       approach='<p>Let side(r, c) be the side of the biggest square of 1s whose bottom right corner is (r, c). For a 1, it is 1 + min of the three neighbours above, left and diagonal, because the square can only grow as far as the smallest of them allows. A border of zeros avoids edge checks.</p>',
       time='O(rows × cols)', space='O(rows × cols)')
t.leet(5, 'h', 'p_palin',
       statement='<p>Return the longest substring of s that reads the same forwards and backwards.</p>',
       example='"babad"             →  "bab" (or "aba")\n"cbbd"              →  "bb"\n"forgeeksskeegfor"  →  "geeksskeeg"',
       hint='Every palindrome has a centre: one letter, or the gap between two letters.',
       approach='<p>An interval table works in O(n²) space. Expanding around each centre is simpler and uses O(1) space: from each letter and each gap, grow outwards while both ends match, and remember the longest stretch found. There are 2n − 1 centres.</p>',
       time='O(n²)', space='O(1)')
t.leet(494, 'h', 'p_target',
       statement='<p>Put a + or a − in front of every number so that the total equals target. Return how many ways there are.</p>',
       example='[1,1,1,1,1], 3  →  5\n[1], 1          →  1',
       hint='The plus numbers P and the minus numbers M satisfy P − M = target and P + M = total.',
       approach='<p>Adding the two equations gives P = (total + target) ÷ 2. So the question becomes: how many groups of numbers add up to P? That is the subset count from the lesson. If total + target is odd or the target is too big, the answer is 0.</p>',
       time='O(n × P)', space='O(P)')
t.leet(1235, 'x', 'p_jobs',
       statement='<p>Each job has a start time, an end time and a profit. Jobs that overlap cannot both be taken, though one may start exactly when another ends. Return the most profit.</p>',
       example='start [1,2,3,3], end [3,4,5,6], profit [50,10,40,70]  →  120\nstart [1,2,3,4,6], end [3,5,10,6,9], profit [20,20,100,70,60]  →  150',
       hint='Sort by end time. Taking a job means adding it to the best of the jobs that end before it starts.',
       approach='<p>This is take or skip with a binary search. After sorting by end time, best[i + 1] = max(best[i], best[k] + profit), where k counts the jobs that end by the time job i starts. Binary search finds k because the end times are sorted.</p>',
       time='O(n log n)', space='O(n)')
t.leet(10, 'x', 'p_regex',
       statement='<p>Match a whole string against a pattern where . matches any one letter and x* matches zero or more copies of x.</p>',
       example='"aa", "a"                    →  false\n"aa", "a*"                   →  true\n"aab", "c*a*b"               →  true\n"mississippi", "mis*is*p*."  →  false',
       hint='ok[i][j] says whether the first i letters match the first j pattern characters. A star has two choices.',
       approach='<p>For a normal character or a dot, the last letters must match and ok[i − 1][j − 1] must be true. For x*, either use it zero times, which looks at ok[i][j − 2], or use it once more when x matches the letter, which looks at ok[i − 1][j]. The first row handles patterns like a*b* that match the empty string.</p>',
       time='O(n × m)', space='O(n × m)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='two-strings', emoji='🔤', title='Two strings, one table', html='''
<p>Many string problems compare two words letter by letter. Put one word down the side and the other across the top. Box (i, j) answers the question for the first i letters of one word and the first j letters of the other. The <b>longest common subsequence</b> is the longest run of letters found in both words in the same order, with gaps allowed.</p>
<div class="viz" data-viz="pk" data-pk="lcs"></div>
<div class="c3" data-k="lcs" data-label="Longest common subsequence with the letters"></div>
<span class="eq">equal letters: L(i, j) = L(i − 1, j − 1) + 1 &nbsp;&nbsp; different: L(i, j) = max( L(i − 1, j), L(i, j − 1) )</span>
<div class="tip">A subsequence may skip letters, a substring may not. "ONE" is a subsequence of "LONGEST" but not a substring.</div>
'''),
    dict(id='edit-distance', emoji='✏️', title='Edit distance', html='''
<p>How many single letter changes turn one word into another? Each change is an insert, a delete or a replace. This is the <b>edit distance</b>, also called the Levenshtein distance. Each box looks at three neighbours, one for each kind of edit, and matching letters cost nothing.</p>
<div class="viz" data-viz="pk" data-pk="edit"></div>
<div class="c3" data-k="edit" data-label="Edit distance with the list of edits"></div>
<span class="eq">E(i, j) = E(i − 1, j − 1) if the letters match, else 1 + min( replace E(i − 1, j − 1), delete E(i − 1, j), insert E(i, j − 1) )</span>
<div class="exam">The first row and column are the base cases: turning i letters into nothing takes i deletes, and turning nothing into j letters takes j inserts.</div>
'''),
    dict(id='increasing-subsequence', emoji='🧗', title='The longest increasing subsequence', html='''
<p>Pick numbers from a list, keeping their order, so that each one is bigger than the last. How long can that climb be? The table method gives each number the longest climb that ends there, by looking back at every smaller number before it. A faster method keeps, for each length, the smallest number that can end a climb of that length, and uses binary search.</p>
<div class="viz" data-viz="pk" data-pk="lis"></div>
<div class="c3" data-k="lis" data-label="Longest increasing subsequence, two ways"></div>
<div class="tw"><table class="jt"><tr><th>Method</th><th>Time</th><th>Gives the climb itself</th></tr>
<tr><td>Table with links back</td><td>O(n²)</td><td class="yes">yes</td></tr>
<tr><td>Smallest ends with binary search</td><td>O(n log n)</td><td>length only, unless extra links are kept</td></tr></table></div>
'''),
    dict(id='interval-dp', emoji='🪞', title='Interval DP: palindromes from the inside out', html='''
<p>Some problems are about a piece of the input from position i to position j. The answer for a piece depends on shorter pieces inside it, so the table is filled by length: all pieces of length 1, then length 2, and so on. For the longest palindrome you can pick from a word, matching end letters wrap the best inside palindrome and add 2.</p>
<div class="viz" data-viz="pk" data-pk="pal"></div>
<div class="c3" data-k="pal" data-label="Longest palindromic subsequence by interval length"></div>
<span class="eq">ends match: P(i, j) = P(i + 1, j − 1) + 2 &nbsp;&nbsp; otherwise: P(i, j) = max( P(i + 1, j), P(i, j − 1) )</span>
<div class="tip">Matrix chain multiplication, bursting balloons and cutting a stick all use the same pattern: loop over the length of the piece first, then over where it starts.</div>
'''),
    dict(id='subset-sum', emoji='➕', title='Subset sums', html='''
<p>Given some numbers, which totals can you make by choosing a group of them, each used at most once? Keep a row of yes or no for every total up to the target. Each new number x turns every reachable total s into a reachable s + x. Going through the totals from the top down makes sure x is used only once.</p>
<div class="viz" data-viz="pk" data-pk="subset"></div>
<div class="c3" data-k="subset" data-label="Which totals can be made, and how many groups"></div>
<div class="warn">Going upwards instead would let the same number be added again and again, which is the coin change problem from part 1. The loop direction is the only difference.</div>
<div class="tip">Splitting numbers into two groups with equal sums is a subset sum with target total ÷ 2. Target Sum in the Practice section uses the same trick.</div>
'''),
    dict(id='bitmask-dp', emoji='🧭', title='Bitmask DP: visiting every city', html='''
<p>The travelling salesperson wants the shortest round trip that visits every city once. Trying every order takes n! steps. Dynamic programming remembers less: just which cities have been visited and where you stand now. The visited set is stored as a number whose bits mark the cities, so 1011 means cities 0, 1 and 3.</p>
<div class="viz" data-viz="pk" data-pk="tsp"></div>
<div class="c3" data-k="tsp" data-label="Shortest tour with a bitmask table"></div>
<span class="eq">best(mask | bit w, w) = min( best(mask | bit w, w), best(mask, v) + dist(v, w) )</span>
<div class="warn">The table still has 2ⁿ × n boxes, so this works for about 20 cities. Beyond that, the problem is NP hard and real route planners use clever approximations.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. As in part 1, start by saying what one box means.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>One box means</th></tr>
<tr><td><a href="#lc1143">1143. Longest Common Subsequence</a></td><td>Easy</td><td>shared letters of two prefixes</td></tr>
<tr><td><a href="#lc96">96. Unique Binary Search Trees</a></td><td>Easy</td><td>tree shapes with k keys</td></tr>
<tr><td><a href="#lc300">300. Longest Increasing Subsequence</a></td><td>Medium</td><td>smallest end for each length</td></tr>
<tr><td><a href="#lc221">221. Maximal Square</a></td><td>Medium</td><td>biggest square ending at a cell</td></tr>
<tr><td><a href="#lc5">5. Longest Palindromic Substring</a></td><td>Hard</td><td>grow around each centre</td></tr>
<tr><td><a href="#lc494">494. Target Sum</a></td><td>Hard</td><td>groups that add up to s</td></tr>
<tr><td><a href="#lc1235">1235. Maximum Profit in Job Scheduling</a></td><td>Expert</td><td>best profit from the first i jobs</td></tr>
<tr><td><a href="#lc10">10. Regular Expression Matching</a></td><td>Expert</td><td>does a prefix match a pattern prefix</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const ints = (s, lo, hi, min, max) => { const a = PK.parseList(s); return a && a.length >= lo && a.length <= hi && a.every(x => Number.isInteger(x) && x >= min && x <= max) ? a : null; };
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const rnd = (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1));
  const word = (s, max) => { const w = String(s).trim(); return /^[A-Za-z]{0,20}$/.test(w) && w.length <= max ? w : null; };

  /* ---------- longest common subsequence ---------- */
  D.lcs = el => PK.widget(el, {
    title: 'Letters two words share, in order', sub: 'Equal letters step down the diagonal and add 1. Different letters keep the bigger of the box above and the box on the left.',
    inputs: [{ k: 'a', label: 'Word 1', type: 'text', val: 'STONE', w: 110 }, { k: 'b', label: 'Word 2', type: 'text', val: 'LONGEST', w: 110 }],
    random: () => pick([{ a: 'STONE', b: 'LONGEST' }, { a: 'HUMAN', b: 'CHIMP' }, { a: 'ABCBDA', b: 'BDCABA' }, { a: 'APPLE', b: 'MAPLE' }, { a: 'TIGER', b: 'RIVER' }]),
    check: v => { const a = word(v.a, 7), b = word(v.b, 7); return a && b && a.length && b.length ? '' : 'Give two words of 1 to 7 letters, letters only.'; },
    frames: ({ a, b }) => {
      a = a.trim().toUpperCase(); b = b.trim().toUpperCase();
      const n = a.length, m = b.length, L = Array.from({ length: n + 1 }, (_, i) => new Array(m + 1).fill(i === 0 ? 0 : '')), F = [];
      for (let i = 0; i <= n; i++) L[i][0] = 0;
      const rlab = ['·'].concat([...a]), clab = ['·'].concat([...b]);
      const pic = cls => [{ t: 'grid', label: `Rows: ${a}, columns: ${b}. Each box: the longest shared run so far`, rows: L.map(r => r.slice()), rlab, clab, cls, sq: true }];
      const done = {};
      for (let i = 0; i <= n; i++) done[i + ',0'] = 'done';
      for (let j = 0; j <= m; j++) done['0,' + j] = 'done';
      F.push({ mood: 'think', msg: `An empty word shares nothing, so the top row and the left column are 0.`, vars: {}, layers: pic(Object.assign({}, done)) });
      for (let i = 1; i <= n; i++) for (let j = 1; j <= m; j++) {
        const cls = Object.assign({}, done);
        if (a[i - 1] === b[j - 1]) {
          L[i][j] = L[i - 1][j - 1] + 1;
          cls[(i - 1) + ',' + (j - 1)] = 'yes'; cls[i + ',' + j] = 'win';
          F.push({ mood: 'happy', fx: 'burst', msg: `${a[i - 1]} = ${b[j - 1]}! Take the diagonal ${L[i - 1][j - 1]} and add 1: <b>${L[i][j]}</b>.`, vars: { row: a[i - 1], col: b[j - 1], here: L[i][j] }, layers: pic(cls) });
        } else {
          L[i][j] = Math.max(L[i - 1][j], L[i][j - 1]);
          cls[(i - 1) + ',' + j] = 'look'; cls[i + ',' + (j - 1)] = 'look'; cls[i + ',' + j] = 'cur';
          F.push({ mood: 'look', msg: `${a[i - 1]} and ${b[j - 1]} differ. Keep the bigger of above ${L[i - 1][j]} and left ${L[i][j - 1]}: <b>${L[i][j]}</b>.`, vars: { row: a[i - 1], col: b[j - 1], here: L[i][j] }, layers: pic(cls) });
        }
        done[i + ',' + j] = a[i - 1] === b[j - 1] ? 'sel' : 'done';
      }
      const cls = Object.assign({}, done), out = [];
      let i = n, j = m;
      while (i > 0 && j > 0) {
        if (a[i - 1] === b[j - 1]) { cls[i + ',' + j] = 'win'; out.push(a[i - 1]); i--; j--; }
        else { cls[i + ',' + j] = 'look'; if (L[i - 1][j] >= L[i][j - 1]) i--; else j--; }
      }
      const common = out.reverse().join('');
      F.push(common.length
        ? { mood: 'wow', fx: 'rain', msg: `Length <b>${L[n][m]}</b>. Walking back from the corner, the green boxes spell <b>${common}</b>, letters that appear in both words in the same order.`, vars: { length: L[n][m] }, layers: pic(cls) }
        : { mood: 'sad', fx: 'shake', msg: `${a} and ${b} share no letters at all, so the answer is 0. Not even one letter in common.`, vars: { length: 0 }, layers: pic(cls) });
      return F;
    }
  });

  /* ---------- edit distance ---------- */
  D.edit = el => PK.widget(el, {
    title: 'Fewest edits from one word to another', sub: 'Each box picks the cheapest of three moves: replace (diagonal), delete (above) or insert (left). Matching letters are free.',
    inputs: [{ k: 'a', label: 'From', type: 'text', val: 'horse', w: 110 }, { k: 'b', label: 'To', type: 'text', val: 'ros', w: 110 }],
    random: () => pick([{ a: 'horse', b: 'ros' }, { a: 'cat', b: 'cut' }, { a: 'sunday', b: 'saturday' }, { a: 'kitten', b: 'sitting' }, { a: 'flaw', b: 'lawn' }]),
    check: v => { const a = word(v.a, 8), b = word(v.b, 8); return a !== null && b !== null && (a.length || b.length) ? '' : 'Give two words of up to 8 letters, letters only.'; },
    frames: ({ a, b }) => {
      a = a.trim().toLowerCase(); b = b.trim().toLowerCase();
      const n = a.length, m = b.length, E = Array.from({ length: n + 1 }, () => new Array(m + 1).fill('')), F = [];
      for (let i = 0; i <= n; i++) E[i][0] = i;
      for (let j = 0; j <= m; j++) E[0][j] = j;
      const rlab = ['·'].concat([...a]), clab = ['·'].concat([...b]);
      const pic = cls => [{ t: 'grid', label: `Turn "${a}" (rows) into "${b}" (columns)`, rows: E.map(r => r.slice()), rlab, clab, cls, sq: true }];
      const done = {};
      for (let i = 0; i <= n; i++) done[i + ',0'] = 'done';
      for (let j = 0; j <= m; j++) done['0,' + j] = 'done';
      F.push({ mood: 'think', msg: 'Reaching an empty word takes one delete per letter. Starting from an empty word takes one insert per letter.', vars: {}, layers: pic(Object.assign({}, done)) });
      for (let i = 1; i <= n; i++) for (let j = 1; j <= m; j++) {
        const cls = Object.assign({}, done);
        if (a[i - 1] === b[j - 1]) {
          E[i][j] = E[i - 1][j - 1];
          cls[(i - 1) + ',' + (j - 1)] = 'yes'; cls[i + ',' + j] = 'win';
          F.push({ mood: 'happy', msg: `${a[i - 1]} = ${b[j - 1]}, a free step: copy the diagonal, <b>${E[i][j]}</b>.`, vars: { edits: E[i][j] }, layers: pic(cls) });
        } else {
          const r = E[i - 1][j - 1], d = E[i - 1][j], ins = E[i][j - 1], lo = Math.min(r, d, ins);
          E[i][j] = 1 + lo;
          const move = lo === r ? `replace ${a[i - 1]} with ${b[j - 1]}` : lo === d ? `delete ${a[i - 1]}` : `insert ${b[j - 1]}`;
          cls[(i - 1) + ',' + (j - 1)] = lo === r ? 'yes' : 'look'; cls[(i - 1) + ',' + j] = lo === d && lo !== r ? 'yes' : 'look'; cls[i + ',' + (j - 1)] = lo === ins && lo !== r && lo !== d ? 'yes' : 'look'; cls[i + ',' + j] = 'cur';
          F.push({ mood: 'work', msg: `${a[i - 1]} ≠ ${b[j - 1]}. Replace ${r}, delete ${d}, insert ${ins}. Cheapest: ${move}, 1 + ${lo} = <b>${E[i][j]}</b>.`, vars: { edits: E[i][j] }, layers: pic(cls) });
        }
        done[i + ',' + j] = 'done';
      }
      const cls = Object.assign({}, done), steps = [];
      let i = n, j = m;
      while (i > 0 || j > 0) {
        cls[i + ',' + j] = 'win';
        if (i > 0 && j > 0 && a[i - 1] === b[j - 1]) { i--; j--; }
        else if (i > 0 && j > 0 && E[i][j] === E[i - 1][j - 1] + 1) { steps.push(`replace ${a[i - 1]} with ${b[j - 1]}`); i--; j--; }
        else if (i > 0 && E[i][j] === E[i - 1][j] + 1) { steps.push(`delete ${a[i - 1]}`); i--; }
        else { steps.push(`insert ${b[j - 1]}`); j--; }
      }
      cls['0,0'] = 'win';
      F.push(E[n][m] === 0
        ? { mood: 'wow', fx: 'rain', msg: 'The words are already the same. Zero edits, nothing to do.', vars: { edits: 0 }, layers: pic(cls) }
        : { mood: 'wow', fx: 'rain', msg: `<b>${E[n][m]}</b> edit${E[n][m] > 1 ? 's' : ''}: ${steps.reverse().join(', ')}. The green boxes show the path back to the corner.`, vars: { edits: E[n][m] }, layers: pic(cls) });
      return F;
    }
  });

  /* ---------- longest increasing subsequence ---------- */
  D.lis = el => PK.widget(el, {
    title: 'The longest climb', sub: 'Table: each number looks back at every smaller number before it. Fast: keep the smallest end for each length and find the spot with binary search.',
    inputs: [{ k: 'v', label: 'Numbers', type: 'text', val: '10, 9, 2, 5, 3, 7, 101, 18', w: 220 }, { k: 'mode', label: 'Method', type: 'seg', val: 'table', opts: [['table', '📋 Table, O(n²)'], ['tails', '⚡ Smallest ends, O(n log n)']] }],
    random: () => ({ v: Array.from({ length: rnd(6, 9) }, () => rnd(1, 30)).join(', '), mode: pick(['table', 'tails']) }),
    check: v => ints(v.v, 2, 10, -99, 999) ? '' : 'Give 2 to 10 whole numbers.',
    frames: ({ v, mode }) => {
      const A = ints(v, 2, 10, -99, 999), n = A.length, F = [];
      if (mode === 'table') {
        const best = new Array(n).fill(''), prev = new Array(n).fill(-1);
        const pic = (cls = {}, bcls = {}, ptr = {}) => [
          { t: 'row', label: 'Numbers', cells: A, cls, ptr },
          { t: 'row', label: 'Longest climb that ends here', cells: best.slice(), cls: bcls },
        ];
        F.push({ mood: 'think', msg: 'Every number on its own is a climb of length 1. Can it extend a climb that ends at a smaller number before it?', vars: {}, layers: pic() });
        for (let i = 0; i < n; i++) {
          best[i] = 1;
          const smaller = [];
          for (let j = 0; j < i; j++) if (A[j] < A[i]) { smaller.push(j); if (best[j] + 1 > best[i]) { best[i] = best[j] + 1; prev[i] = j; } }
          const cls = { [i]: 'cur' }, bcls = { [i]: 'yes' };
          smaller.forEach(j => { cls[j] = 'look'; bcls[j] = j === prev[i] ? 'sel' : 'look'; });
          F.push({ mood: smaller.length ? 'work' : 'look',
            msg: smaller.length ? `${A[i]}: smaller numbers before it are ${smaller.map(j => A[j]).join(', ')}. The best one to follow is ${A[prev[i]]} with a climb of ${best[prev[i]]}, so <b>${best[i]}</b>.` : `${A[i]}: nothing smaller before it, so it starts a new climb of <b>1</b>.`,
            vars: { at: A[i], length: best[i] }, layers: pic(cls, bcls, { [i]: '🧗' }) });
        }
        let i = best.indexOf(Math.max(...best));
        const seq = [], cls = {};
        while (i !== -1) { seq.push(A[i]); cls[i] = 'win'; i = prev[i]; }
        F.push({ mood: 'wow', fx: 'rain', msg: `Longest climb: <b>${seq.reverse().join(', ')}</b>, length ${seq.length}. Follow the links back from the biggest box.`, vars: { length: seq.length }, layers: pic(cls, Object.fromEntries(Object.keys(cls).map(k => [k, 'win']))) });
        return F;
      }
      const tails = [];
      const pic = (i, k, how) => [
        { t: 'row', label: 'Numbers', cells: A, cls: i >= 0 ? { [i]: 'cur' } : {}, ptr: i >= 0 ? { [i]: 'x' } : {} },
        { t: 'row', label: 'Smallest end of a climb of each length', cells: tails.slice(), cls: k >= 0 ? { [k]: how } : {}, tag: Object.fromEntries(tails.map((_, t) => [t, 'len ' + (t + 1)])) },
      ];
      F.push({ mood: 'think', msg: 'Keep one list: the smallest number that can end a climb of length 1, of length 2, and so on. The list always stays sorted.', vars: {}, layers: pic(-1, -1) });
      A.forEach((x, i) => {
        let lo = 0, hi = tails.length;
        while (lo < hi) { const mid = (lo + hi) >> 1; if (tails[mid] < x) lo = mid + 1; else hi = mid; }
        if (lo === tails.length) {
          tails.push(x);
          F.push({ mood: 'happy', fx: 'burst', msg: `${x} is bigger than every end, so it makes a climb of length <b>${tails.length}</b>. Add it at the end.`, vars: { x, longest: tails.length }, layers: pic(i, lo, 'yes') });
        } else {
          const old = tails[lo];
          tails[lo] = x;
          F.push({ mood: 'work', msg: `Binary search: ${x} replaces ${old} as the end for length ${lo + 1}. A smaller end leaves more room to climb later.`, vars: { x, longest: tails.length }, layers: pic(i, lo, 'mv') });
        }
      });
      F.push({ mood: 'wow', fx: 'rain', msg: `The list has ${tails.length} entries, so the longest climb has length <b>${tails.length}</b>. The list itself is not always a real climb, only its length is guaranteed.`, vars: { longest: tails.length }, layers: pic(-1, -1) });
      return F;
    }
  });

  /* ---------- interval DP: longest palindromic subsequence ---------- */
  D.pal = el => PK.widget(el, {
    title: 'Grow palindromes from the inside out', sub: 'Box (i, j) covers letters i to j. Short pieces are solved first. Matching ends wrap the inside and add 2.',
    inputs: [{ k: 's', label: 'Word', type: 'text', val: 'bbbab', w: 120 }],
    random: () => ({ s: pick(['bbbab', 'abcba', 'character', 'level', 'banana', 'abcd', 'racecar']) }),
    check: v => { const w = word(v.s, 9); return w && w.length >= 2 ? '' : 'Give a word of 2 to 9 letters.'; },
    frames: ({ s }) => {
      s = s.trim().toLowerCase();
      const n = s.length, P = Array.from({ length: n }, () => new Array(n).fill(null)), F = [];
      const lab = [...s].map((c, i) => i + ' ' + c);
      const pic = cls => [{ t: 'grid', label: 'Box (row i, column j): the longest palindrome you can pick from letters i to j', rows: P.map(r => r.map(v => v === null ? '' : v)), rlab: lab, clab: lab, cls, sq: true }];
      const done = {};
      for (let i = 0; i < n; i++) for (let j = 0; j < i; j++) done[i + ',' + j] = 'wall';
      for (let i = 0; i < n; i++) { P[i][i] = 1; done[i + ',' + i] = 'done'; }
      F.push({ mood: 'think', msg: 'One letter is a palindrome of length 1, so the diagonal is all 1s. The bottom left half is never used.', vars: { length: 1 }, layers: pic(Object.assign({}, done)) });
      for (let len = 2; len <= n; len++) for (let i = 0; i + len - 1 < n; i++) {
        const j = i + len - 1, cls = Object.assign({}, done);
        if (s[i] === s[j]) {
          const inside = len > 2 ? P[i + 1][j - 1] : 0;
          P[i][j] = inside + 2;
          if (len > 2) cls[(i + 1) + ',' + (j - 1)] = 'yes';
          cls[i + ',' + j] = 'win';
          F.push({ mood: 'happy', msg: `"${s.slice(i, j + 1)}": both ends are ${s[i]}. Wrap the inside ${len > 2 ? '(' + inside + ')' : '(empty)'} and add 2: <b>${P[i][j]}</b>.`, vars: { piece: s.slice(i, j + 1), best: P[i][j] }, layers: pic(cls) });
        } else {
          P[i][j] = Math.max(P[i + 1][j], P[i][j - 1]);
          cls[(i + 1) + ',' + j] = 'look'; cls[i + ',' + (j - 1)] = 'look'; cls[i + ',' + j] = 'cur';
          F.push({ mood: 'look', msg: `"${s.slice(i, j + 1)}": ends ${s[i]} and ${s[j]} differ. Drop one end: max(${P[i + 1][j]}, ${P[i][j - 1]}) = <b>${P[i][j]}</b>.`, vars: { piece: s.slice(i, j + 1), best: P[i][j] }, layers: pic(cls) });
        }
        done[i + ',' + j] = 'done';
      }
      F.push({ mood: P[0][n - 1] === n ? 'wow' : 'happy', fx: 'rain', msg: P[0][n - 1] === n ? `<b>${n}</b>: the whole word "${s}" reads the same both ways!` : `The top right box covers the whole word: the longest palindrome you can pick from "${s}" has <b>${P[0][n - 1]}</b> letters.`, vars: { best: P[0][n - 1] }, layers: pic(Object.assign({}, done, { ['0,' + (n - 1)]: 'win' })) });
      return F;
    }
  });

  /* ---------- subset sum ---------- */
  D.subset = el => PK.widget(el, {
    title: 'Which totals can you make?', sub: 'Add the numbers one at a time. Each new number turns every reachable total s into a reachable s + x. Go from the top down so it is used only once.',
    inputs: [{ k: 'v', label: 'Numbers', type: 'text', val: '3, 4, 5, 2', w: 150 }, { k: 'target', label: 'Target', type: 'num', val: 9, min: 1, max: 15, w: 70 }],
    random: () => pick([{ v: '3, 4, 5, 2', target: 9 }, { v: '2, 6, 8', target: 7 }, { v: '1, 5, 11, 5', target: 11 }, { v: '4, 7', target: rnd(8, 15) }, { v: '3, 34, 4, 12, 5, 2', target: 9 }]),
    check: v => ints(v.v, 1, 6, 1, 50) && Number.isInteger(v.target) && v.target >= 1 && v.target <= 15 ? '' : 'Give one to six numbers from 1 to 50 and a target from 1 to 15.',
    frames: ({ v, target }) => {
      const A = ints(v, 1, 6, 1, 50), can = new Array(target + 1).fill(false), from = new Array(target + 1).fill(-1), F = [];
      can[0] = true;
      const pic = (cls = {}, label = 'Totals that can be made') => [{ t: 'row', label, cells: can.map(c => c ? '✓' : '·'), cls: Object.assign(Object.fromEntries(can.map((c, s) => [s, c ? 'done' : ''])), cls) }];
      F.push({ mood: 'think', msg: 'With no numbers chosen, only the total 0 is possible.', vars: { target }, layers: pic({ 0: 'yes' }) });
      A.forEach((x, k) => {
        const added = [];
        for (let s = target; s >= x; s--) if (can[s - x] && !can[s]) { can[s] = true; from[s] = k; added.push(s); }
        const cls = {};
        added.forEach(s => { cls[s] = 'yes'; });
        F.push(added.length
          ? { mood: 'happy', msg: `Add ${x}: new totals <b>${added.slice().reverse().join(', ')}</b>, each one an old total plus ${x}.`, vars: { number: x, target }, layers: pic(cls) }
          : { mood: 'look', msg: `Add ${x}: ${x > target ? 'it is bigger than the target, so ' : ''}no new totals up to ${target}.`, vars: { number: x, target }, layers: pic(cls) });
      });
      if (!can[target]) {
        F.push({ mood: 'sad', fx: 'shake', msg: `No group of ${A.join(', ')} adds up to ${target}. The box stays empty. Try another target.`, vars: { target }, layers: pic({ [target]: 'no' }) });
        return F;
      }
      const used = [], cls = {};
      for (let s = target; s > 0;) { cls[s] = 'win'; used.push(A[from[s]]); s -= A[from[s]]; }
      cls[0] = 'win';
      F.push({ mood: 'wow', fx: 'rain', msg: `Yes! <b>${target} = ${used.reverse().join(' + ')}</b>. Each green box was reached by adding one more number.`, vars: { target }, layers: pic(cls) });
      return F;
    }
  });

  /* ---------- bitmask DP: shortest tour ---------- */
  const CITY = ['🏠', '🏫', '🏥', '🏪'];
  const DIST = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]];
  D.tsp = el => PK.widget(el, {
    title: 'Visit every city once, as short as possible', sub: 'A state is the set of cities visited plus where you stand now. The set fits in 4 bits, one bit per city.',
    inputs: [],
    frames: () => {
      const n = 4, FULL = 1 << n, NONE = Infinity, best = Array.from({ length: FULL }, () => new Array(n).fill(NONE)), came = Array.from({ length: FULL }, () => new Array(n).fill(-1)), F = [];
      best[1][0] = 0;
      const masks = [];
      for (let m = 1; m < FULL; m += 2) masks.push(m);
      masks.sort((x, y) => x.toString(2).split('1').length - y.toString(2).split('1').length || x - y);
      const bits = m => m.toString(2).padStart(n, '0');
      const nodes = [[0, 60, 40, CITY[0]], [1, 300, 40, CITY[1]], [2, 60, 190, CITY[2]], [3, 300, 190, CITY[3]]];
      const edges = [];
      for (let a = 0; a < n; a++) for (let b = a + 1; b < n; b++) edges.push([a, b, DIST[a][b]]);
      const pic = (cls = {}, ncls = {}, ecls = {}) => [
        { t: 'graph', label: 'Cities and distances, start at home', w: 360, h: 230, nodes, edges, ncls, ecls, r: 18 },
        { t: 'grid', label: 'Shortest route: rows are visited sets (bit 0 is home), columns are where you stand', rows: masks.map(m => best[m].map(v => v === NONE ? '' : v)), rlab: masks.map(bits), clab: CITY, cls },
      ];
      F.push({ mood: 'think', msg: 'Start at home with only home visited: set 0001, distance 0.', vars: {}, layers: pic({ '0,0': 'yes' }, { 0: 'cur' }) });
      masks.forEach((m, r) => {
        for (let v = 0; v < n; v++) {
          if (best[m][v] === NONE) continue;
          const ups = [];
          for (let w = 0; w < n; w++) if (!(m & (1 << w))) {
            const nx = m | (1 << w), d = best[m][v] + DIST[v][w];
            if (d < best[nx][w]) { best[nx][w] = d; came[nx][w] = v; ups.push([nx, w, d]); }
          }
          if (!ups.length) continue;
          const cls = { [r + ',' + v]: 'cur' }, ecls = {};
          ups.forEach(([nx, w]) => { cls[masks.indexOf(nx) + ',' + w] = 'yes'; ecls[Math.min(v, w) + '-' + Math.max(v, w)] = 'look'; });
          F.push({ mood: 'work', msg: `From set ${bits(m)} standing at ${CITY[v]} (${best[m][v]}): go to ${ups.map(([nx, w, d]) => `${CITY[w]} for ${d}`).join(', ')}.`, vars: { set: bits(m), at: CITY[v] }, layers: pic(cls, { [v]: 'cur' }, ecls) });
        }
      });
      let end = 1;
      for (let v = 2; v < n; v++) if (best[FULL - 1][v] + DIST[v][0] < best[FULL - 1][end] + DIST[end][0]) end = v;
      const total = best[FULL - 1][end] + DIST[end][0], route = [], cls = {}, ecls = {};
      for (let m = FULL - 1, v = end; v !== -1;) { route.push(v); cls[masks.indexOf(m) + ',' + v] = 'win'; const p = came[m][v]; m ^= 1 << v; v = p; }
      route.reverse(); route.push(0);
      for (let k = 0; k + 1 < route.length; k++) ecls[Math.min(route[k], route[k + 1]) + '-' + Math.max(route[k], route[k + 1])] = 'win';
      F.push({ mood: 'look', msg: `All four visited (1111). Add the way home: ${[1, 2, 3].map(v => `${CITY[v]} ${best[FULL - 1][v]} + ${DIST[v][0]} = ${best[FULL - 1][v] + DIST[v][0]}`).join(', ')}.`, vars: {}, layers: pic({ [(masks.length - 1) + ',1']: 'look', [(masks.length - 1) + ',2']: 'look', [(masks.length - 1) + ',3']: 'look' }) });
      F.push({ mood: 'wow', fx: 'rain', msg: `Shortest tour: <b>${route.map(v => CITY[v]).join(' ')}</b>, length <b>${total}</b>. The table grows like 2ⁿ × n. For 20 cities that is about 21 million boxes, while trying every order would mean more than 100 million billion routes.`, vars: { tour: total }, layers: pic(cls, Object.fromEntries(route.map(v => [v, 'yes'])), ecls) });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Bigger tables for strings, sequences and sets',
    'panels': [
        {'s': [['e', '🔤'], ['t', 'i × j', {'b': 1}]], 'h': 'Two strings', 't': 'Prefix against prefix.', 'more': 'LCS and edit distance.'},
        {'s': [['e', '🧗'], ['t', 'smallest ends', {'b': 1}]], 'h': 'Increasing runs', 't': 'O(n log n) with binary search.', 'more': 'Patience sorting idea.'},
        {'s': [['e', '🪞'], ['t', 'by length', {'b': 1}]], 'h': 'Interval DP', 't': 'Short pieces first.', 'more': 'Palindromes, matrix chains.'},
        {'s': [['e', '🧭'], ['t', '2ⁿ × n', {'b': 1}]], 'h': 'Bitmask DP', 't': 'A set stored in bits.', 'more': 'Good up to about 20 items.'},
    ],
    'remember': 'Choose the state carefully: two prefixes for two strings, a piece from i to j for intervals, a total for subsets and a set of bits for visiting everything. Then fill the table in an order where every box it needs is already done.',
}

REAL = [
    ['🧬', 'DNA and protein alignment', 'The Needleman and Wunsch method that lines up genes is an edit distance table with scores for matches and gaps.'],
    ['🗂️', 'git diff and file comparison', 'Showing what changed between two versions of a file is built on the longest common subsequence of their lines.'],
    ['⌨️', 'Autocorrect', 'A phone suggests the dictionary word with the smallest edit distance from what you typed.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to dynamic programming, part two. The tables get bigger and the states get smarter. You will compare two words to find the letters they share, count the fewest edits from one word to another, find the longest increasing climb in a list, grow palindromes from the inside out, find which totals a set of numbers can make, and plan the shortest trip through every city with a bitmask.'},
    {'id': 'two-strings', 'h': 'Longest common subsequence', 'en': 'Put one word down the side and the other across the top. When two letters match, take the diagonal and add one. When they differ, keep the bigger of the box above and the box on the left. Walk back from the corner to read the shared letters.'},
    {'id': 'edit-distance', 'h': 'Edit distance', 'en': 'Edit distance counts the fewest inserts, deletes and replaces that turn one word into another. Matching letters are free and copy the diagonal. Otherwise take one plus the cheapest of the three neighbours: diagonal for replace, above for delete, left for insert.'},
    {'id': 'increasing-subsequence', 'h': 'Longest increasing subsequence', 'en': 'The table method gives each number the longest climb ending there, by checking every smaller number before it. The fast method keeps the smallest end for each climb length and places each new number with binary search, in n log n time.'},
    {'id': 'interval-dp', 'h': 'Interval DP', 'en': 'In interval problems, a box covers the letters from i to j. Shorter pieces are solved first. For palindromes, if both end letters match, wrap the inside answer and add two. If not, drop one end and keep the better result.'},
    {'id': 'subset-sum', 'h': 'Subset sums', 'en': 'To see which totals a group of numbers can make, keep a row of yes or no. Each new number turns every reachable total into a new total that is bigger by that number. Going from the top down uses each number only once.'},
    {'id': 'bitmask-dp', 'h': 'Bitmask DP', 'en': 'For the shortest trip through every city, the state is the set of visited cities and the city you stand in. The set is stored as bits in one number. From each state, try every unvisited city next, and keep the shortest distance.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from the longest common subsequence to regular expression matching. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. Decide what one box means, which boxes it depends on and in what order to fill them. Try a tiny example by hand before you code. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What is the longest common subsequence of "STONE" and "LONGEST"?', 'o': ['"ST"', '"ONE"', '"STONE"', '"LONG"'], 'a': 1, 'hint': 'Letters in order, gaps allowed.', 'why': 'O, N and E appear in that order in both words, and no four letters do.'},
    {'lv': 'e', 'q': 'Which three edits does edit distance allow?', 'o': ['Sort, swap, delete', 'Insert, delete, replace', 'Copy, paste, cut', 'Reverse, insert, delete'], 'a': 1, 'hint': 'Single letter changes.', 'why': 'The Levenshtein distance counts inserts, deletes and replaces of one letter at a time.'},
    {'lv': 'e', 'q': 'What is the edit distance from "cat" to "cut"?', 'o': ['0', '1', '2', '3'], 'a': 1, 'hint': 'Only one letter differs.', 'why': 'Replace a with u, one edit.'},
    {'lv': 'e', 'q': 'How long is the longest increasing subsequence of [10, 9, 2, 5, 3, 7, 101, 18]?', 'o': ['3', '4', '5', '8'], 'a': 1, 'hint': 'Try 2, 5, 7, ...', 'why': '2, 5, 7, 101 is a climb of length 4, and none is longer.'},
    {'lv': 'm', 'q': 'In the LCS table, what happens when the two letters are different?', 'o': ['The box is 0', 'Take the diagonal plus 1', 'Take the bigger of the box above and the box on the left', 'Take the smaller of the two'], 'a': 2, 'hint': 'Drop the last letter of one word.', 'why': 'If the letters differ, at least one of them is not in the answer, so drop it from one word and keep the better result.'},
    {'lv': 'm', 'q': 'In which order is an interval DP table filled?', 'o': ['Row by row from the top', 'By the length of the piece, short ones first', 'At random', 'From the longest piece down'], 'a': 1, 'hint': 'A piece depends on the pieces inside it.', 'why': 'Every box depends on shorter pieces, so all shorter pieces must be done first.'},
    {'lv': 'm', 'q': 'In subset sum, why do the totals go from the top down?', 'o': ['It is faster', 'So that each number is used at most once', 'So that the list stays sorted', 'It makes no difference'], 'a': 1, 'hint': 'What happens if you go upwards with the number 2?', 'why': 'Going upwards, a total made with x can be extended by x again in the same pass, so x would be reused.'},
    {'lv': 'm', 'q': 'In bitmask DP with 4 cities, what does the mask 1011 mean?', 'o': ['Cities 1, 0, 1, 1', 'Cities 0, 1 and 3 have been visited', 'The route has length 11', 'City 2 is the start'], 'a': 1, 'hint': 'Bit 0 is on the right.', 'why': 'Reading from the right, bits 0, 1 and 3 are set, so those cities are visited.'},
    {'lv': 'h', 'q': 'What is the edit distance from "horse" to "ros"?', 'o': ['2', '3', '4', '5'], 'a': 1, 'hint': 'Run the animation.', 'why': 'Replace h with r, delete r, delete e: three edits.'},
    {'lv': 'h', 'q': 'How long is the longest palindrome you can pick from "bbbab", keeping order?', 'o': ['3', '4', '5', '2'], 'a': 1, 'hint': 'Skip the a.', 'why': 'Removing the a leaves bbbb, a palindrome of length 4.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'a, b = "abc", "ac"\nL = [[0] * 3 for _ in range(4)]\nfor i in range(1, 4):\n    for j in range(1, 3):\n        L[i][j] = L[i-1][j-1] + 1 if a[i-1] == b[j-1] else max(L[i-1][j], L[i][j-1])\nprint(L[3][2])', 'o': ['1', '2', '3', '0'], 'a': 1, 'hint': 'Which letters of "ac" appear in "abc" in order?', 'why': 'a and c both appear in order, so the LCS length is 2.'},
    {'lv': 'h', 'q': 'In the fast LIS method, what does tails[k] hold?', 'o': ['The k-th number of the list', 'The smallest number that can end an increasing run of length k + 1', 'The length of the run ending at k', 'The largest number so far'], 'a': 1, 'hint': 'A smaller end leaves more room to climb.', 'why': 'Keeping the smallest possible end for each length lets later numbers extend runs as easily as possible.'},
    {'lv': 'x', 'q': 'How many boxes does the bitmask table have for n cities?', 'o': ['n²', '2ⁿ × n', 'n!', 'n log n'], 'a': 1, 'hint': 'Every set of cities, times every city you can stand in.', 'why': 'There are 2ⁿ sets and n end cities, so 2ⁿ × n boxes.'},
    {'lv': 'x', 'q': 'How many binary search tree shapes hold 3 keys?', 'o': ['3', '4', '5', '6'], 'a': 2, 'hint': 'Root 1, 2 or 3, then count each side.', 'why': 'Root 1: 2 shapes, root 2: 1 shape, root 3: 2 shapes. Total 5.'},
    {'lv': 'x', 'q': 'In Target Sum, why is the plus group total equal to (total + target) ÷ 2?', 'o': ['It is a guess', 'P − M = target and P + M = total, so adding them gives 2P = total + target', 'Because half the numbers are positive', 'Because the target is even'], 'a': 1, 'hint': 'Write two equations.', 'why': 'The plus group P and minus group M satisfy both equations, and adding them removes M.'},
    {'lv': 'x', 'q': 'In regular expression matching, the pattern has x* at position j. Which two boxes can make ok[i][j] true?', 'o': ['ok[i − 1][j − 1] and ok[i][j − 1]', 'ok[i][j − 2] for zero copies, and ok[i − 1][j] when x matches the letter', 'Only ok[i − 1][j − 1]', 'ok[0][0] only'], 'a': 1, 'hint': 'Zero copies, or one more copy.', 'why': 'Skipping x* entirely looks two pattern characters back. Using one more copy keeps the star and drops one letter of the string.'},
]

CALC = [
    {'lv': 'e', 'q': 'What is the length of the longest common subsequence of "abcde" and "ace"?', 'ans': '3', 'hint': 'All of ace appears in order.', 'steps': ['a, c and e appear in "abcde" in the same order.', 'Length 3.']},
    {'lv': 'e', 'q': 'What is the edit distance from "" to "abc"?', 'ans': '3', 'hint': 'The first row of the table.', 'steps': ['Insert a, b and c: three edits.']},
    {'lv': 'm', 'q': 'What is the edit distance from "kitten" to "sitting"?', 'ans': '3', 'hint': 'Two replaces and one insert.', 'steps': ['Replace k with s, replace e with i, insert g.', 'Three edits.']},
    {'lv': 'm', 'q': 'How long is the longest increasing subsequence of [0, 1, 0, 3, 2, 3]?', 'ans': '4', 'hint': 'Try 0, 1, 2, 3.', 'steps': ['0, 1, 2, 3 is strictly increasing and keeps the order.', 'Length 4.']},
    {'lv': 'h', 'q': 'How many groups of numbers from [1, 2, 3, 4, 5] add up to 5?', 'ans': '3', 'hint': 'List them.', 'steps': ['{5}, {1, 4} and {2, 3}.', 'Three groups.']},
    {'lv': 'h', 'q': 'How long is the longest palindrome you can pick from "character", keeping order?', 'ans': '5', 'hint': 'Look for c, a, r, a, c.', 'steps': ['c h a r a c t e r: pick c, a, r, a, c.', '"carac" reads the same both ways, length 5.']},
    {'lv': 'x', 'q': 'Cities with distances 0-1: 10, 0-2: 15, 0-3: 20, 1-2: 35, 1-3: 25, 2-3: 30. What is the shortest round trip from 0?', 'ans': '80', 'hint': 'Run the bitmask animation.', 'steps': ['0 1 3 2 0: <span class="eq">10 + 25 + 30 + 15 = 80</span>', 'Every other order is at least as long.']},
    {'lv': 'x', 'q': 'How many binary search tree shapes hold 4 keys?', 'ans': '14', 'hint': 'Counts for 0 to 3 keys: 1, 1, 2, 5.', 'steps': ['<span class="eq">1×5 + 1×2 + 2×1 + 5×1 = 14</span>', 'Roots 1, 2, 3 and 4 in turn.']},
]

TALK = {
    'two-strings': 'Many problems compare two strings, and dynamic programming handles them with a grid. Write one word down the left side and the other word across the top. Each box answers the question for the first few letters of one word and the first few letters of the other. Take the longest common subsequence, which is the longest run of letters found in both words in the same order, with gaps allowed. For stone and longest, the answer is O N E. The rule for each box is short. If the two letters at this row and column match, that letter can join the answer, so take the box on the diagonal and add one. If they differ, one of them is not part of the answer, so drop the last letter from one word or the other and keep the bigger of the box above and the box on the left. To read the actual letters, walk back from the bottom right corner.',
    'edit-distance': 'Edit distance measures how different two words are, by counting the fewest single letter changes that turn one into the other. Each change is an insert, a delete or a replace. For example, horse becomes ros in three edits: replace h with r, delete the r, then delete the e. Build the same kind of grid as before, with one word down the side and the other across the top. The first column is easy, because turning several letters into an empty word takes one delete per letter. The first row is easy too, because building a word from nothing takes one insert per letter. For any other box, if the two letters match, no edit is needed and you copy the diagonal. If they differ, try all three edits and keep the cheapest. The diagonal means replace, the box above means delete, and the box on the left means insert. Spell checkers use exactly this table.',
    'increasing-subsequence': 'Given a list of numbers, pick some of them, keeping their order, so that every number is bigger than the one before. How long can that climb be? The table method is natural. For each number, look back at every smaller number earlier in the list. The longest climb ending here is one more than the best climb ending at any of those smaller numbers. Keep a link to the number you followed, and at the end, follow the links back to read the climb. That takes n squared steps. There is a faster method. Keep a list where position k holds the smallest number that can end a climb of length k plus one. This list is always sorted, so for each new number, binary search finds where it belongs. If it is bigger than everything, the longest climb grows by one. Otherwise it replaces a bigger end, which leaves more room for later numbers. The final list length is the answer.',
    'interval-dp': 'Some problems are about a piece of the input, from one position to another, and the answer for a piece depends on the smaller pieces inside it. This is called interval dynamic programming. The important rule is the order: solve all pieces of length one, then all pieces of length two, and keep growing. Here is an example. From a word, pick some letters, keeping their order, to form the longest possible palindrome. Every single letter is a palindrome of length one, which fills the diagonal of the table. Now look at a longer piece. If its first and last letters are the same, they can wrap around the best palindrome inside, so take the inside answer and add two. If the end letters differ, at least one of them must go, so drop either end and keep the better of the two smaller pieces. The answer for the whole word sits in the top right box.',
    'subset-sum': 'Here is a question that looks simple. Given a handful of numbers, which totals can you make by choosing some of them, using each number at most once? Keep a row of boxes, one for every total from zero up to the target, each marked yes or no. At the start only zero is reachable, since choosing nothing gives zero. Now bring in the numbers one at a time. A new number x turns every reachable total s into another reachable total, s plus x. There is one trap. If you go through the totals from small to large, you might reach s plus x and then, in the same pass, reach s plus two x, using the number twice. Going from the top down avoids this, because you only build on totals from before x arrived. Change yes or no into a count, and the same loop counts how many groups add up to each total.',
    'bitmask-dp': 'The travelling salesperson problem asks for the shortest round trip that visits every city exactly once. Trying every order works for a few cities, but the number of orders grows as n factorial, which explodes very fast. Dynamic programming notices that the past only matters in two ways: which cities you have already visited, and which city you stand in now. The exact order you used to get there does not matter for the rest of the trip. The visited set is stored as a number, with one bit for each city. So for four cities, one zero one one means cities zero, one and three are done. From every state, try each city you have not visited yet, and update the state that includes it. When every bit is set, add the way home and keep the shortest. The table has two to the n times n boxes, which is fine for about twenty cities.',
    'leetcode': 'The LeetCode problems in this chapter use the bigger tables from the lessons. The easy problems find the longest common subsequence of two strings using a single row, and count how many shapes a binary search tree with n keys can have, which gives the Catalan numbers. The medium problems find the longest increasing subsequence in n log n time with binary search, and the largest square of ones in a grid, where each cell looks at three neighbours. The hard problems find the longest palindromic substring by growing around every centre, and count the ways to put plus and minus signs in front of numbers to hit a target, which turns into a subset count. The expert problems pick jobs that do not overlap for the most profit, using take or skip with binary search, and match strings against patterns with dots and stars.',
}

T = t.finish({
    'slug': 'dynamic-programming-2', 'title': 'Dynamic Programming 2: Strings, Sequences and Sets', 'short': 'Dynamic programming 2', 'emoji': '🧬', 'topic': 'dynamic-programming-2', 'prefix': 'dsadp2',
    'module': ('🧠', 'Greedy and dynamic programming'),
    'lead': 'Bigger tables and smarter states. Find the letters two words share, count the fewest edits between words, find the longest climb in a list, grow palindromes from the inside out, see which totals some numbers can make and plan the shortest trip through every city with a bitmask.',
    'desc': 'Dynamic programming in DSA, part 2: longest common subsequence, edit distance, longest increasing subsequence in O(n log n), interval DP with palindromes, subset sum and bitmask DP for the travelling salesperson, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 26,
    'summary': 'Longest common subsequence and edit distance on two strings, the longest increasing subsequence with a table and with binary search, interval DP for palindromes, subset sums and the travelling salesperson with a bitmask. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['dynamic programming', 'longest common subsequence', 'lcs', 'edit distance', 'levenshtein', 'longest increasing subsequence', 'lis', 'patience sorting', 'interval dp', 'palindromic subsequence', 'subset sum', 'partition', 'bitmask dp', 'travelling salesman', 'tsp', 'catalan numbers', 'regular expression matching'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('dynamic-programming', 'dynamic-programming', '🧠 Dynamic programming 1'),
    'next': None,
})
