# Advanced strings: the Z algorithm, Manacher's palindromes, suffix arrays with LCP, Aho-Corasick for many patterns,
# and rolling hashes with binary search.
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('zfunc', py=r'''
def z_array(s):
    n = len(s)
    z = [0] * n
    l = r = 0                                    # s[l:r] is the rightmost window known to match the start of s
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])          # reuse what the window already tells us
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1                            # compare letter by letter past what is known
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def find_all(text, pattern):
    z = z_array(pattern + "$" + text)            # $ never appears, so no match runs across it
    return [i - len(pattern) - 1 for i in range(len(z)) if z[i] == len(pattern)]


print("z of aabxaab:", z_array("aabxaab"))
print("abra in abracadabra at", find_all("abracadabra", "abra"))
print("aa in aaaa at", find_all("aaaa", "aa"))
''', js=r'''
function zArray(s) {
  const n = s.length, z = new Array(n).fill(0);
  let l = 0, r = 0;                                  // s[l:r] is the rightmost window known to match the start
  for (let i = 1; i < n; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);     // reuse what the window already tells us
    while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;   // compare past what is known
    if (i + z[i] > r) { l = i; r = i + z[i]; }
  }
  return z;
}

function findAll(text, pattern) {
  const z = zArray(pattern + "$" + text);            // $ never appears, so no match runs across it
  const out = [];
  for (let i = 0; i < z.length; i++) if (z[i] === pattern.length) out.push(i - pattern.length - 1);
  return out;
}

console.log(`z of aabxaab: [${zArray("aabxaab").join(", ")}]`);
console.log(`abra in abracadabra at [${findAll("abracadabra", "abra").join(", ")}]`);
console.log(`aa in aaaa at [${findAll("aaaa", "aa").join(", ")}]`);
''', java=r'''
import java.util.*;

public class ZAlgorithm {
    static int[] zArray(String s) {
        int n = s.length(), l = 0, r = 0;            // s[l:r] is the rightmost window known to match the start
        int[] z = new int[n];
        for (int i = 1; i < n; i++) {
            if (i < r) z[i] = Math.min(r - i, z[i - l]);   // reuse what the window already tells us
            while (i + z[i] < n && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;   // compare past what is known
            if (i + z[i] > r) { l = i; r = i + z[i]; }
        }
        return z;
    }

    static List<Integer> findAll(String text, String pattern) {
        int[] z = zArray(pattern + "$" + text);      // $ never appears, so no match runs across it
        List<Integer> out = new ArrayList<>();
        for (int i = 0; i < z.length; i++) if (z[i] == pattern.length()) out.add(i - pattern.length() - 1);
        return out;
    }

    public static void main(String[] args) {
        System.out.println("z of aabxaab: " + Arrays.toString(zArray("aabxaab")));
        System.out.println("abra in abracadabra at " + findAll("abracadabra", "abra"));
        System.out.println("aa in aaaa at " + findAll("aaaa", "aa"));
    }
}
''', ts=r'''
function zArray(s: string): number[] {
  const n = s.length, z: number[] = new Array(n).fill(0);
  let l = 0, r = 0;                                  // s[l:r] is the rightmost window known to match the start
  for (let i = 1; i < n; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);     // reuse what the window already tells us
    while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;   // compare past what is known
    if (i + z[i] > r) { l = i; r = i + z[i]; }
  }
  return z;
}

function findAll(text: string, pattern: string): number[] {
  const z = zArray(pattern + "$" + text);            // $ never appears, so no match runs across it
  const out: number[] = [];
  for (let i = 0; i < z.length; i++) if (z[i] === pattern.length) out.push(i - pattern.length - 1);
  return out;
}

console.log(`z of aabxaab: [${zArray("aabxaab").join(", ")}]`);
console.log(`abra in abracadabra at [${findAll("abracadabra", "abra").join(", ")}]`);
console.log(`aa in aaaa at [${findAll("aaaa", "aa").join(", ")}]`);
''')

t.code('manacher', py=r'''
def longest_palindrome(s):
    t = "^#" + "#".join(s) + "#$"               # a # between letters makes every palindrome odd, ^ and $ stop the loop
    p = [0] * len(t)                             # p[i]: how far the palindrome centred at i reaches
    c = r = 0                                    # centre and right edge of the palindrome reaching furthest
    for i in range(1, len(t) - 1):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])      # copy from the mirror position around c
        while t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1                            # grow past what the mirror promised
        if i + p[i] > r:
            c, r = i, i + p[i]
    k = 0
    for i in range(len(t)):
        if p[i] > p[k]:
            k = i
    start = (k - p[k]) // 2                      # map back to a position in s
    return s[start:start + p[k]]


for s in ("babad", "cbbd", "abacdfgdcaba", "forgeeksskeegfor"):
    print(s, longest_palindrome(s))
''', js=r'''
function longestPalindrome(s) {
  const t = "^#" + s.split("").join("#") + "#$";    // a # between letters makes every palindrome odd
  const p = new Array(t.length).fill(0);             // p[i]: how far the palindrome centred at i reaches
  let c = 0, r = 0;                                  // centre and right edge of the one reaching furthest
  for (let i = 1; i < t.length - 1; i++) {
    if (i < r) p[i] = Math.min(r - i, p[2 * c - i]); // copy from the mirror position around c
    while (t[i + p[i] + 1] === t[i - p[i] - 1]) p[i]++;   // grow past what the mirror promised
    if (i + p[i] > r) { c = i; r = i + p[i]; }
  }
  let k = 0;
  for (let i = 0; i < t.length; i++) if (p[i] > p[k]) k = i;
  const start = (k - p[k]) >> 1;                     // map back to a position in s
  return s.slice(start, start + p[k]);
}

for (const s of ["babad", "cbbd", "abacdfgdcaba", "forgeeksskeegfor"]) console.log(s, longestPalindrome(s));
''', java=r'''
public class Manacher {
    static String longestPalindrome(String s) {
        StringBuilder sb = new StringBuilder("^#");  // a # between letters makes every palindrome odd
        for (char ch : s.toCharArray()) sb.append(ch).append('#');
        String t = sb.append('$').toString();
        int[] p = new int[t.length()];               // p[i]: how far the palindrome centred at i reaches
        int c = 0, r = 0;                            // centre and right edge of the one reaching furthest
        for (int i = 1; i < t.length() - 1; i++) {
            if (i < r) p[i] = Math.min(r - i, p[2 * c - i]);   // copy from the mirror position around c
            while (t.charAt(i + p[i] + 1) == t.charAt(i - p[i] - 1)) p[i]++;   // grow past what the mirror promised
            if (i + p[i] > r) { c = i; r = i + p[i]; }
        }
        int k = 0;
        for (int i = 0; i < t.length(); i++) if (p[i] > p[k]) k = i;
        int start = (k - p[k]) / 2;                  // map back to a position in s
        return s.substring(start, start + p[k]);
    }

    public static void main(String[] args) {
        for (String s : new String[]{"babad", "cbbd", "abacdfgdcaba", "forgeeksskeegfor"}) System.out.println(s + " " + longestPalindrome(s));
    }
}
''', ts=r'''
function longestPalindrome(s: string): string {
  const t = "^#" + s.split("").join("#") + "#$";    // a # between letters makes every palindrome odd
  const p: number[] = new Array(t.length).fill(0);   // p[i]: how far the palindrome centred at i reaches
  let c = 0, r = 0;                                  // centre and right edge of the one reaching furthest
  for (let i = 1; i < t.length - 1; i++) {
    if (i < r) p[i] = Math.min(r - i, p[2 * c - i]); // copy from the mirror position around c
    while (t[i + p[i] + 1] === t[i - p[i] - 1]) p[i]++;   // grow past what the mirror promised
    if (i + p[i] > r) { c = i; r = i + p[i]; }
  }
  let k = 0;
  for (let i = 0; i < t.length; i++) if (p[i] > p[k]) k = i;
  const start = (k - p[k]) >> 1;                     // map back to a position in s
  return s.slice(start, start + p[k]);
}

for (const s of ["babad", "cbbd", "abacdfgdcaba", "forgeeksskeegfor"]) console.log(s, longestPalindrome(s));
''')

t.code('suffix', py=r'''
def suffix_array(s):
    n = len(s)
    rank = [ord(ch) for ch in s]                 # start by ranking single letters
    sa = list(range(n))
    k = 1
    while True:
        key = lambda i: (rank[i], rank[i + k] if i + k < n else -1)   # first 2k letters as two ranks
        sa.sort(key=key)
        new = [0] * n
        for j in range(1, n):
            new[sa[j]] = new[sa[j - 1]] + (key(sa[j]) != key(sa[j - 1]))
        rank = new
        if rank[sa[-1]] == n - 1:                # every suffix has its own rank: done
            return sa
        k *= 2


def lcp_array(s, sa):
    n = len(s)
    rank = [0] * n
    for i, p in enumerate(sa):
        rank[p] = i
    lcp, h = [0] * n, 0                          # lcp[i]: common start of suffixes sa[i - 1] and sa[i]
    for p in range(n):                           # Kasai: h drops by at most 1 from one suffix to the next
        if rank[p] > 0:
            q = sa[rank[p] - 1]
            while p + h < n and q + h < n and s[p + h] == s[q + h]:
                h += 1
            lcp[rank[p]] = h
            h = max(h - 1, 0)
        else:
            h = 0
    return lcp


s = "banana"
sa = suffix_array(s)
lcp = lcp_array(s, sa)
for i, p in enumerate(sa):
    print(p, lcp[i], s[p:])
best = max(range(len(s)), key=lambda i: lcp[i])
print("longest repeated substring:", s[sa[best]:sa[best] + lcp[best]])
''', js=r'''
function suffixArray(s) {
  const n = s.length;
  let rank = [...s].map(ch => ch.charCodeAt(0));     // start by ranking single letters
  const sa = [...Array(n).keys()];
  for (let k = 1; ; k *= 2) {
    const key = i => [rank[i], i + k < n ? rank[i + k] : -1];   // first 2k letters as two ranks
    const cmp = (a, b) => { const x = key(a), y = key(b); return x[0] - y[0] || x[1] - y[1]; };
    sa.sort(cmp);
    const next = new Array(n).fill(0);
    for (let j = 1; j < n; j++) next[sa[j]] = next[sa[j - 1]] + (cmp(sa[j], sa[j - 1]) !== 0 ? 1 : 0);
    rank = next;
    if (rank[sa[n - 1]] === n - 1) return sa;        // every suffix has its own rank: done
  }
}

function lcpArray(s, sa) {
  const n = s.length, rank = new Array(n).fill(0), lcp = new Array(n).fill(0);
  sa.forEach((p, i) => { rank[p] = i; });
  let h = 0;                                         // Kasai: h drops by at most 1 from one suffix to the next
  for (let p = 0; p < n; p++) {
    if (rank[p] > 0) {
      const q = sa[rank[p] - 1];
      while (p + h < n && q + h < n && s[p + h] === s[q + h]) h++;
      lcp[rank[p]] = h;
      h = Math.max(h - 1, 0);
    } else h = 0;
  }
  return lcp;
}

const s = "banana";
const sa = suffixArray(s), lcp = lcpArray(s, sa);
sa.forEach((p, i) => console.log(p, lcp[i], s.slice(p)));
let best = 0;
for (let i = 0; i < s.length; i++) if (lcp[i] > lcp[best]) best = i;
console.log("longest repeated substring:", s.slice(sa[best], sa[best] + lcp[best]));
''', java=r'''
import java.util.*;

public class SuffixArray {
    static int[] rank;
    static int n, k;

    static int cmp(int a, int b) {
        if (rank[a] != rank[b]) return rank[a] - rank[b];
        int ra = a + k < n ? rank[a + k] : -1, rb = b + k < n ? rank[b + k] : -1;   // first 2k letters as two ranks
        return ra - rb;
    }

    static Integer[] suffixArray(String s) {
        n = s.length();
        rank = new int[n];
        Integer[] sa = new Integer[n];
        for (int i = 0; i < n; i++) { rank[i] = s.charAt(i); sa[i] = i; }   // start by ranking single letters
        for (k = 1; ; k *= 2) {
            Arrays.sort(sa, SuffixArray::cmp);
            int[] next = new int[n];
            for (int j = 1; j < n; j++) next[sa[j]] = next[sa[j - 1]] + (cmp(sa[j], sa[j - 1]) != 0 ? 1 : 0);
            rank = next;
            if (rank[sa[n - 1]] == n - 1) return sa;   // every suffix has its own rank: done
        }
    }

    static int[] lcpArray(String s, Integer[] sa) {
        int[] pos = new int[n], lcp = new int[n];
        for (int i = 0; i < n; i++) pos[sa[i]] = i;
        int h = 0;                                   // Kasai: h drops by at most 1 from one suffix to the next
        for (int p = 0; p < n; p++) {
            if (pos[p] > 0) {
                int q = sa[pos[p] - 1];
                while (p + h < n && q + h < n && s.charAt(p + h) == s.charAt(q + h)) h++;
                lcp[pos[p]] = h;
                h = Math.max(h - 1, 0);
            } else h = 0;
        }
        return lcp;
    }

    public static void main(String[] args) {
        String s = "banana";
        Integer[] sa = suffixArray(s);
        int[] lcp = lcpArray(s, sa);
        for (int i = 0; i < n; i++) System.out.println(sa[i] + " " + lcp[i] + " " + s.substring(sa[i]));
        int best = 0;
        for (int i = 0; i < n; i++) if (lcp[i] > lcp[best]) best = i;
        System.out.println("longest repeated substring: " + s.substring(sa[best], sa[best] + lcp[best]));
    }
}
''', ts=r'''
function suffixArray(s: string): number[] {
  const n = s.length;
  let rank: number[] = [...s].map(ch => ch.charCodeAt(0));   // start by ranking single letters
  const sa: number[] = [...Array(n).keys()];
  for (let k = 1; ; k *= 2) {
    const key = (i: number): [number, number] => [rank[i], i + k < n ? rank[i + k] : -1];   // first 2k letters as two ranks
    const cmp = (a: number, b: number): number => { const x = key(a), y = key(b); return x[0] - y[0] || x[1] - y[1]; };
    sa.sort(cmp);
    const next: number[] = new Array(n).fill(0);
    for (let j = 1; j < n; j++) next[sa[j]] = next[sa[j - 1]] + (cmp(sa[j], sa[j - 1]) !== 0 ? 1 : 0);
    rank = next;
    if (rank[sa[n - 1]] === n - 1) return sa;        // every suffix has its own rank: done
  }
}

function lcpArray(s: string, sa: number[]): number[] {
  const n = s.length, rank: number[] = new Array(n).fill(0), lcp: number[] = new Array(n).fill(0);
  sa.forEach((p, i) => { rank[p] = i; });
  let h = 0;                                         // Kasai: h drops by at most 1 from one suffix to the next
  for (let p = 0; p < n; p++) {
    if (rank[p] > 0) {
      const q = sa[rank[p] - 1];
      while (p + h < n && q + h < n && s[p + h] === s[q + h]) h++;
      lcp[rank[p]] = h;
      h = Math.max(h - 1, 0);
    } else h = 0;
  }
  return lcp;
}

const s = "banana";
const sa = suffixArray(s), lcp = lcpArray(s, sa);
sa.forEach((p, i) => console.log(p, lcp[i], s.slice(p)));
let best = 0;
for (let i = 0; i < s.length; i++) if (lcp[i] > lcp[best]) best = i;
console.log("longest repeated substring:", s.slice(sa[best], sa[best] + lcp[best]));
''')

t.code('aho', py=r'''
from collections import deque


def build(words):
    goto, fail, out = [{}], [0], [[]]            # node 0 is the root of a trie of all the words
    for w in words:
        node = 0
        for ch in w:
            if ch not in goto[node]:
                goto.append({})
                fail.append(0)
                out.append([])
                goto[node][ch] = len(goto) - 1
            node = goto[node][ch]
        out[node].append(w)
    queue = deque(goto[0].values())
    while queue:                                 # breadth first, so shallower nodes get their links first
        node = queue.popleft()
        for ch, nxt in goto[node].items():
            f = fail[node]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[nxt] = goto[f].get(ch, 0)       # the longest proper suffix that is also in the trie
            out[nxt] += out[fail[nxt]]           # words that end inside this one end here too
            queue.append(nxt)
    return goto, fail, out


def search(text, words):
    goto, fail, out = build(words)
    node, found = 0, []
    for i, ch in enumerate(text):
        while node and ch not in goto[node]:
            node = fail[node]                    # fall back instead of starting again
        node = goto[node].get(ch, 0)
        for w in out[node]:
            found.append((i - len(w) + 1, w))
    return found


for pos, w in search("ushers", ["he", "she", "his", "hers"]):
    print(pos, w)
''', js=r'''
function build(words) {
  const go = [new Map()], fail = [0], out = [[]];    // node 0 is the root of a trie of all the words
  for (const w of words) {
    let node = 0;
    for (const ch of w) {
      if (!go[node].has(ch)) { go.push(new Map()); fail.push(0); out.push([]); go[node].set(ch, go.length - 1); }
      node = go[node].get(ch);
    }
    out[node].push(w);
  }
  const queue = [...go[0].values()];
  for (let qi = 0; qi < queue.length; qi++) {        // breadth first, so shallower nodes get their links first
    const node = queue[qi];
    for (const [ch, nxt] of go[node]) {
      let f = fail[node];
      while (f && !go[f].has(ch)) f = fail[f];
      fail[nxt] = go[f].has(ch) ? go[f].get(ch) : 0; // the longest proper suffix that is also in the trie
      out[nxt] = out[nxt].concat(out[fail[nxt]]);    // words that end inside this one end here too
      queue.push(nxt);
    }
  }
  return [go, fail, out];
}

function search(text, words) {
  const [go, fail, out] = build(words), found = [];
  let node = 0;
  [...text].forEach((ch, i) => {
    while (node && !go[node].has(ch)) node = fail[node];   // fall back instead of starting again
    node = go[node].has(ch) ? go[node].get(ch) : 0;
    for (const w of out[node]) found.push([i - w.length + 1, w]);
  });
  return found;
}

for (const [pos, w] of search("ushers", ["he", "she", "his", "hers"])) console.log(pos, w);
''', java=r'''
import java.util.*;

public class AhoCorasick {
    static List<Map<Character, Integer>> go = new ArrayList<>();
    static List<Integer> fail = new ArrayList<>();
    static List<List<String>> out = new ArrayList<>();

    static void build(String[] words) {
        go.add(new LinkedHashMap<>()); fail.add(0); out.add(new ArrayList<>());   // node 0 is the root of a trie
        for (String w : words) {
            int node = 0;
            for (char ch : w.toCharArray()) {
                if (!go.get(node).containsKey(ch)) {
                    go.add(new LinkedHashMap<>()); fail.add(0); out.add(new ArrayList<>());
                    go.get(node).put(ch, go.size() - 1);
                }
                node = go.get(node).get(ch);
            }
            out.get(node).add(w);
        }
        ArrayDeque<Integer> queue = new ArrayDeque<>(go.get(0).values());
        while (!queue.isEmpty()) {                   // breadth first, so shallower nodes get their links first
            int node = queue.poll();
            for (Map.Entry<Character, Integer> e : go.get(node).entrySet()) {
                char ch = e.getKey();
                int nxt = e.getValue(), f = fail.get(node);
                while (f != 0 && !go.get(f).containsKey(ch)) f = fail.get(f);
                fail.set(nxt, go.get(f).getOrDefault(ch, 0));   // the longest proper suffix that is also in the trie
                out.get(nxt).addAll(out.get(fail.get(nxt)));    // words that end inside this one end here too
                queue.add(nxt);
            }
        }
    }

    public static void main(String[] args) {
        build(new String[]{"he", "she", "his", "hers"});
        String text = "ushers";
        int node = 0;
        for (int i = 0; i < text.length(); i++) {
            char ch = text.charAt(i);
            while (node != 0 && !go.get(node).containsKey(ch)) node = fail.get(node);   // fall back instead of starting again
            node = go.get(node).getOrDefault(ch, 0);
            for (String w : out.get(node)) System.out.println((i - w.length() + 1) + " " + w);
        }
    }
}
''', ts=r'''
function build(words: string[]): [Map<string, number>[], number[], string[][]] {
  const go: Map<string, number>[] = [new Map()], fail: number[] = [0], out: string[][] = [[]];   // node 0 is the root
  for (const w of words) {
    let node = 0;
    for (const ch of w) {
      if (!go[node].has(ch)) { go.push(new Map()); fail.push(0); out.push([]); go[node].set(ch, go.length - 1); }
      node = go[node].get(ch) as number;
    }
    out[node].push(w);
  }
  const queue: number[] = [...go[0].values()];
  for (let qi = 0; qi < queue.length; qi++) {        // breadth first, so shallower nodes get their links first
    const node = queue[qi];
    for (const [ch, nxt] of go[node]) {
      let f = fail[node];
      while (f && !go[f].has(ch)) f = fail[f];
      fail[nxt] = go[f].has(ch) ? go[f].get(ch) as number : 0;   // the longest proper suffix also in the trie
      out[nxt] = out[nxt].concat(out[fail[nxt]]);    // words that end inside this one end here too
      queue.push(nxt);
    }
  }
  return [go, fail, out];
}

function search(text: string, words: string[]): [number, string][] {
  const [go, fail, out] = build(words), found: [number, string][] = [];
  let node = 0;
  [...text].forEach((ch, i) => {
    while (node && !go[node].has(ch)) node = fail[node];   // fall back instead of starting again
    node = go[node].has(ch) ? go[node].get(ch) as number : 0;
    for (const w of out[node]) found.push([i - w.length + 1, w]);
  });
  return found;
}

for (const [pos, w] of search("ushers", ["he", "she", "his", "hers"])) console.log(pos, w);
''')

t.code('rolling', py=r'''
MOD, BASE = 1_000_003, 131                       # small enough that every product fits in a double in JavaScript


def prefix_hashes(s):
    h, pw = [0] * (len(s) + 1), [1] * (len(s) + 1)
    for i, ch in enumerate(s):
        h[i + 1] = (h[i] * BASE + ord(ch)) % MOD
        pw[i + 1] = pw[i] * BASE % MOD
    return h, pw


def sub_hash(h, pw, i, j):                       # the hash of s[i:j] in O(1)
    return (h[j] - h[i] * pw[j - i]) % MOD


def repeat_of_length(s, h, pw, size):
    seen = {}
    for i in range(len(s) - size + 1):
        x = sub_hash(h, pw, i, i + size)
        if x in seen and s[seen[x]:seen[x] + size] == s[i:i + size]:   # compare letters to rule out a collision
            return seen[x]
        seen.setdefault(x, i)
    return -1


def longest_repeat(s):
    h, pw = prefix_hashes(s)
    lo, hi, best = 1, len(s) - 1, ""
    while lo <= hi:                              # if some length repeats, every shorter length repeats too
        mid = (lo + hi) // 2
        at = repeat_of_length(s, h, pw, mid)
        if at >= 0:
            best, lo = s[at:at + mid], mid + 1
        else:
            hi = mid - 1
    return best


for s in ("banana", "mississippi", "abcd"):
    print(f'{s}: "{longest_repeat(s)}"')
''', js=r'''
const MOD = 1000003, BASE = 131;                     // small enough that every product fits in a double

function prefixHashes(s) {
  const h = new Array(s.length + 1).fill(0), pw = new Array(s.length + 1).fill(1);
  for (let i = 0; i < s.length; i++) {
    h[i + 1] = (h[i] * BASE + s.charCodeAt(i)) % MOD;
    pw[i + 1] = pw[i] * BASE % MOD;
  }
  return [h, pw];
}

function subHash(h, pw, i, j) {                      // the hash of s[i:j] in O(1)
  return ((h[j] - h[i] * pw[j - i]) % MOD + MOD) % MOD;
}

function repeatOfLength(s, h, pw, size) {
  const seen = new Map();
  for (let i = 0; i + size <= s.length; i++) {
    const x = subHash(h, pw, i, i + size);
    if (seen.has(x) && s.slice(seen.get(x), seen.get(x) + size) === s.slice(i, i + size)) return seen.get(x);   // rule out a collision
    if (!seen.has(x)) seen.set(x, i);
  }
  return -1;
}

function longestRepeat(s) {
  const [h, pw] = prefixHashes(s);
  let lo = 1, hi = s.length - 1, best = "";
  while (lo <= hi) {                                 // if some length repeats, every shorter length repeats too
    const mid = (lo + hi) >> 1, at = repeatOfLength(s, h, pw, mid);
    if (at >= 0) { best = s.slice(at, at + mid); lo = mid + 1; }
    else hi = mid - 1;
  }
  return best;
}

for (const s of ["banana", "mississippi", "abcd"]) console.log(`${s}: "${longestRepeat(s)}"`);
''', java=r'''
import java.util.*;

public class RollingHash {
    static final long MOD = 1_000_003, BASE = 131;
    static long[] h, pw;

    static void prefixHashes(String s) {
        h = new long[s.length() + 1];
        pw = new long[s.length() + 1];
        pw[0] = 1;
        for (int i = 0; i < s.length(); i++) {
            h[i + 1] = (h[i] * BASE + s.charAt(i)) % MOD;
            pw[i + 1] = pw[i] * BASE % MOD;
        }
    }

    static long subHash(int i, int j) {              // the hash of s[i:j] in O(1)
        return ((h[j] - h[i] * pw[j - i]) % MOD + MOD) % MOD;
    }

    static int repeatOfLength(String s, int size) {
        Map<Long, Integer> seen = new HashMap<>();
        for (int i = 0; i + size <= s.length(); i++) {
            long x = subHash(i, i + size);
            Integer at = seen.get(x);
            if (at != null && s.substring(at, at + size).equals(s.substring(i, i + size))) return at;   // rule out a collision
            seen.putIfAbsent(x, i);
        }
        return -1;
    }

    static String longestRepeat(String s) {
        prefixHashes(s);
        int lo = 1, hi = s.length() - 1;
        String best = "";
        while (lo <= hi) {                           // if some length repeats, every shorter length repeats too
            int mid = (lo + hi) / 2, at = repeatOfLength(s, mid);
            if (at >= 0) { best = s.substring(at, at + mid); lo = mid + 1; }
            else hi = mid - 1;
        }
        return best;
    }

    public static void main(String[] args) {
        for (String s : new String[]{"banana", "mississippi", "abcd"}) System.out.println(s + ": \"" + longestRepeat(s) + "\"");
    }
}
''', ts=r'''
const MOD = 1000003, BASE = 131;                     // small enough that every product fits in a double

function prefixHashes(s: string): [number[], number[]] {
  const h: number[] = new Array(s.length + 1).fill(0), pw: number[] = new Array(s.length + 1).fill(1);
  for (let i = 0; i < s.length; i++) {
    h[i + 1] = (h[i] * BASE + s.charCodeAt(i)) % MOD;
    pw[i + 1] = pw[i] * BASE % MOD;
  }
  return [h, pw];
}

function subHash(h: number[], pw: number[], i: number, j: number): number {   // the hash of s[i:j] in O(1)
  return ((h[j] - h[i] * pw[j - i]) % MOD + MOD) % MOD;
}

function repeatOfLength(s: string, h: number[], pw: number[], size: number): number {
  const seen = new Map<number, number>();
  for (let i = 0; i + size <= s.length; i++) {
    const x = subHash(h, pw, i, i + size);
    const at = seen.get(x);
    if (at !== undefined && s.slice(at, at + size) === s.slice(i, i + size)) return at;   // rule out a collision
    if (at === undefined) seen.set(x, i);
  }
  return -1;
}

function longestRepeat(s: string): string {
  const [h, pw] = prefixHashes(s);
  let lo = 1, hi = s.length - 1, best = "";
  while (lo <= hi) {                                 // if some length repeats, every shorter length repeats too
    const mid = (lo + hi) >> 1, at = repeatOfLength(s, h, pw, mid);
    if (at >= 0) { best = s.slice(at, at + mid); lo = mid + 1; }
    else hi = mid - 1;
  }
  return best;
}

for (const s of ["banana", "mississippi", "abcd"]) console.log(`${s}: "${longestRepeat(s)}"`);
''')

# ---------------------------------------------------------------- LeetCode programs
t.code('p_strstr', py=r'''
def str_str(haystack, needle):
    s = needle + "\0" + haystack                 # a separator that never appears in either string
    z, l, r = [0] * len(s), 0, 0
    for i in range(1, len(s)):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < len(s) and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
        if z[i] == len(needle):                  # the needle starts here in the haystack
            return i - len(needle) - 1
    return -1


print(str_str("sadbutsad", "sad"), str_str("leetcode", "leeto"), str_str("hello", "ll"))
''', js=r'''
function strStr(haystack, needle) {
  const s = needle + "\0" + haystack;               // a separator that never appears in either string
  const z = new Array(s.length).fill(0);
  let l = 0, r = 0;
  for (let i = 1; i < s.length; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);
    while (i + z[i] < s.length && s[z[i]] === s[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
    if (z[i] === needle.length) return i - needle.length - 1;   // the needle starts here
  }
  return -1;
}

console.log(strStr("sadbutsad", "sad"), strStr("leetcode", "leeto"), strStr("hello", "ll"));
''', java=r'''
public class StrStr {
    static int strStr(String haystack, String needle) {
        String s = needle + "\0" + haystack;         // a separator that never appears in either string
        int[] z = new int[s.length()];
        int l = 0, r = 0;
        for (int i = 1; i < s.length(); i++) {
            if (i < r) z[i] = Math.min(r - i, z[i - l]);
            while (i + z[i] < s.length() && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;
            if (i + z[i] > r) { l = i; r = i + z[i]; }
            if (z[i] == needle.length()) return i - needle.length() - 1;   // the needle starts here
        }
        return -1;
    }

    public static void main(String[] args) {
        System.out.println(strStr("sadbutsad", "sad") + " " + strStr("leetcode", "leeto") + " " + strStr("hello", "ll"));
    }
}
''', ts=r'''
function strStr(haystack: string, needle: string): number {
  const s = needle + "\0" + haystack;               // a separator that never appears in either string
  const z: number[] = new Array(s.length).fill(0);
  let l = 0, r = 0;
  for (let i = 1; i < s.length; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);
    while (i + z[i] < s.length && s[z[i]] === s[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
    if (z[i] === needle.length) return i - needle.length - 1;   // the needle starts here
  }
  return -1;
}

console.log(strStr("sadbutsad", "sad"), strStr("leetcode", "leeto"), strStr("hello", "ll"));
''')

t.code('p_rotate', py=r'''
def z_array(s):
    z, l, r = [0] * len(s), 0, 0
    for i in range(1, len(s)):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < len(s) and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def rotate_string(s, goal):
    if len(s) != len(goal):
        return False
    z = z_array(goal + "\0" + s + s)             # every rotation of s sits inside s + s
    return any(v == len(goal) for v in z[len(goal) + 1:])


print("true" if rotate_string("abcde", "cdeab") else "false")
print("true" if rotate_string("abcde", "abced") else "false")
''', js=r'''
function zArray(s) {
  const z = new Array(s.length).fill(0);
  let l = 0, r = 0;
  for (let i = 1; i < s.length; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);
    while (i + z[i] < s.length && s[z[i]] === s[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
  }
  return z;
}

function rotateString(s, goal) {
  if (s.length !== goal.length) return false;
  const z = zArray(goal + "\0" + s + s);             // every rotation of s sits inside s + s
  return z.slice(goal.length + 1).some(v => v === goal.length);
}

console.log(rotateString("abcde", "cdeab"));
console.log(rotateString("abcde", "abced"));
''', java=r'''
public class RotateString {
    static int[] zArray(String s) {
        int[] z = new int[s.length()];
        int l = 0, r = 0;
        for (int i = 1; i < s.length(); i++) {
            if (i < r) z[i] = Math.min(r - i, z[i - l]);
            while (i + z[i] < s.length() && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;
            if (i + z[i] > r) { l = i; r = i + z[i]; }
        }
        return z;
    }

    static boolean rotateString(String s, String goal) {
        if (s.length() != goal.length()) return false;
        int[] z = zArray(goal + "\0" + s + s);       // every rotation of s sits inside s + s
        for (int i = goal.length() + 1; i < z.length; i++) if (z[i] == goal.length()) return true;
        return false;
    }

    public static void main(String[] args) {
        System.out.println(rotateString("abcde", "cdeab"));
        System.out.println(rotateString("abcde", "abced"));
    }
}
''', ts=r'''
function zArray(s: string): number[] {
  const z: number[] = new Array(s.length).fill(0);
  let l = 0, r = 0;
  for (let i = 1; i < s.length; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);
    while (i + z[i] < s.length && s[z[i]] === s[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
  }
  return z;
}

function rotateString(s: string, goal: string): boolean {
  if (s.length !== goal.length) return false;
  const z = zArray(goal + "\0" + s + s);             // every rotation of s sits inside s + s
  return z.slice(goal.length + 1).some(v => v === goal.length);
}

console.log(rotateString("abcde", "cdeab"));
console.log(rotateString("abcde", "abced"));
''')

t.code('p_countpal', py=r'''
def count_substrings(s):
    t = "^#" + "#".join(s) + "#$"
    p, c, r = [0] * len(t), 0, 0
    for i in range(1, len(t) - 1):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])
        while t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1
        if i + p[i] > r:
            c, r = i, i + p[i]
    return sum((x + 1) // 2 for x in p)          # a palindrome of radius x holds (x + 1) // 2 palindromes with the same centre


print(count_substrings("abc"), count_substrings("aaa"), count_substrings("abba"))
''', js=r'''
function countSubstrings(s) {
  const t = "^#" + s.split("").join("#") + "#$";
  const p = new Array(t.length).fill(0);
  let c = 0, r = 0;
  for (let i = 1; i < t.length - 1; i++) {
    if (i < r) p[i] = Math.min(r - i, p[2 * c - i]);
    while (t[i + p[i] + 1] === t[i - p[i] - 1]) p[i]++;
    if (i + p[i] > r) { c = i; r = i + p[i]; }
  }
  return p.reduce((sum, x) => sum + ((x + 1) >> 1), 0);   // radius x holds (x + 1) / 2 palindromes on that centre
}

console.log(countSubstrings("abc"), countSubstrings("aaa"), countSubstrings("abba"));
''', java=r'''
public class PalindromicSubstrings {
    static int countSubstrings(String s) {
        StringBuilder sb = new StringBuilder("^#");
        for (char ch : s.toCharArray()) sb.append(ch).append('#');
        String t = sb.append('$').toString();
        int[] p = new int[t.length()];
        int c = 0, r = 0, total = 0;
        for (int i = 1; i < t.length() - 1; i++) {
            if (i < r) p[i] = Math.min(r - i, p[2 * c - i]);
            while (t.charAt(i + p[i] + 1) == t.charAt(i - p[i] - 1)) p[i]++;
            if (i + p[i] > r) { c = i; r = i + p[i]; }
        }
        for (int x : p) total += (x + 1) / 2;        // radius x holds (x + 1) / 2 palindromes on that centre
        return total;
    }

    public static void main(String[] args) {
        System.out.println(countSubstrings("abc") + " " + countSubstrings("aaa") + " " + countSubstrings("abba"));
    }
}
''', ts=r'''
function countSubstrings(s: string): number {
  const t = "^#" + s.split("").join("#") + "#$";
  const p: number[] = new Array(t.length).fill(0);
  let c = 0, r = 0;
  for (let i = 1; i < t.length - 1; i++) {
    if (i < r) p[i] = Math.min(r - i, p[2 * c - i]);
    while (t[i + p[i] + 1] === t[i - p[i] - 1]) p[i]++;
    if (i + p[i] > r) { c = i; r = i + p[i]; }
  }
  return p.reduce((sum, x) => sum + ((x + 1) >> 1), 0);   // radius x holds (x + 1) / 2 palindromes on that centre
}

console.log(countSubstrings("abc"), countSubstrings("aaa"), countSubstrings("abba"));
''')

t.code('p_inarray', py=r'''
def string_matching(words):
    text = "#".join(words)                       # every word once, kept apart by #
    return [w for w in words if text.find(w) != text.rfind(w)]   # found twice means it sits inside another word


print(string_matching(["mass", "as", "hero", "superhero"]))
print(string_matching(["leetcode", "et", "code"]))
print(string_matching(["blue", "green", "bu"]))
''', js=r'''
function stringMatching(words) {
  const text = words.join("#");                      // every word once, kept apart by #
  return words.filter(w => text.indexOf(w) !== text.lastIndexOf(w));   // found twice: it sits inside another word
}

for (const words of [["mass", "as", "hero", "superhero"], ["leetcode", "et", "code"], ["blue", "green", "bu"]]) {
  console.log(`[${stringMatching(words).map(w => `'${w}'`).join(", ")}]`);
}
''', java=r'''
import java.util.*;

public class StringMatching {
    static List<String> stringMatching(String[] words) {
        String text = String.join("#", words);       // every word once, kept apart by #
        List<String> out = new ArrayList<>();
        for (String w : words) if (text.indexOf(w) != text.lastIndexOf(w)) out.add("'" + w + "'");   // found twice
        return out;
    }

    public static void main(String[] args) {
        System.out.println(stringMatching(new String[]{"mass", "as", "hero", "superhero"}));
        System.out.println(stringMatching(new String[]{"leetcode", "et", "code"}));
        System.out.println(stringMatching(new String[]{"blue", "green", "bu"}));
    }
}
''', ts=r'''
function stringMatching(words: string[]): string[] {
  const text = words.join("#");                      // every word once, kept apart by #
  return words.filter(w => text.indexOf(w) !== text.lastIndexOf(w));   // found twice: it sits inside another word
}

for (const words of [["mass", "as", "hero", "superhero"], ["leetcode", "et", "code"], ["blue", "green", "bu"]]) {
  console.log(`[${stringMatching(words).map(w => `'${w}'`).join(", ")}]`);
}
''')

t.code('p_happy', py=r'''
def longest_prefix(s):
    n = len(s)
    z, l, r = [0] * n, 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    for i in range(1, n):                        # the first i whose match runs to the very end
        if i + z[i] == n:
            return s[i:]
    return ""


for s in ("level", "ababab", "abc"):
    print(f'{s}: "{longest_prefix(s)}"')
''', js=r'''
function longestPrefix(s) {
  const n = s.length, z = new Array(n).fill(0);
  let l = 0, r = 0;
  for (let i = 1; i < n; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);
    while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
  }
  for (let i = 1; i < n; i++) if (i + z[i] === n) return s.slice(i);   // the first match that runs to the end
  return "";
}

for (const s of ["level", "ababab", "abc"]) console.log(`${s}: "${longestPrefix(s)}"`);
''', java=r'''
public class HappyPrefix {
    static String longestPrefix(String s) {
        int n = s.length(), l = 0, r = 0;
        int[] z = new int[n];
        for (int i = 1; i < n; i++) {
            if (i < r) z[i] = Math.min(r - i, z[i - l]);
            while (i + z[i] < n && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;
            if (i + z[i] > r) { l = i; r = i + z[i]; }
        }
        for (int i = 1; i < n; i++) if (i + z[i] == n) return s.substring(i);   // the first match that runs to the end
        return "";
    }

    public static void main(String[] args) {
        for (String s : new String[]{"level", "ababab", "abc"}) System.out.println(s + ": \"" + longestPrefix(s) + "\"");
    }
}
''', ts=r'''
function longestPrefix(s: string): string {
  const n = s.length, z: number[] = new Array(n).fill(0);
  let l = 0, r = 0;
  for (let i = 1; i < n; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);
    while (i + z[i] < n && s[z[i]] === s[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
  }
  for (let i = 1; i < n; i++) if (i + z[i] === n) return s.slice(i);   // the first match that runs to the end
  return "";
}

for (const s of ["level", "ababab", "abc"]) console.log(`${s}: "${longestPrefix(s)}"`);
''')

t.code('p_shortpal', py=r'''
def shortest_palindrome(s):
    t = s + "#" + s[::-1]
    pi = [0] * len(t)                            # pi[i]: the longest proper prefix of t[:i + 1] that is also its suffix
    for i in range(1, len(t)):
        k = pi[i - 1]
        while k and t[i] != t[k]:
            k = pi[k - 1]
        if t[i] == t[k]:
            k += 1
        pi[i] = k
    keep = pi[-1]                                # the longest palindrome at the start of s
    return s[keep:][::-1] + s


for s in ("aacecaaa", "abcd", "abab"):
    print(s, shortest_palindrome(s))
''', js=r'''
function shortestPalindrome(s) {
  const rev = s.split("").reverse().join(""), t = s + "#" + rev;
  const pi = new Array(t.length).fill(0);            // pi[i]: longest proper prefix of t[:i + 1] that is also its suffix
  for (let i = 1; i < t.length; i++) {
    let k = pi[i - 1];
    while (k && t[i] !== t[k]) k = pi[k - 1];
    if (t[i] === t[k]) k++;
    pi[i] = k;
  }
  const keep = pi[t.length - 1];                     // the longest palindrome at the start of s
  return s.slice(keep).split("").reverse().join("") + s;
}

for (const s of ["aacecaaa", "abcd", "abab"]) console.log(s, shortestPalindrome(s));
''', java=r'''
public class ShortestPalindrome {
    static String shortestPalindrome(String s) {
        String t = s + "#" + new StringBuilder(s).reverse();
        int[] pi = new int[t.length()];              // pi[i]: longest proper prefix of t[:i + 1] that is also its suffix
        for (int i = 1; i < t.length(); i++) {
            int k = pi[i - 1];
            while (k > 0 && t.charAt(i) != t.charAt(k)) k = pi[k - 1];
            if (t.charAt(i) == t.charAt(k)) k++;
            pi[i] = k;
        }
        int keep = pi[t.length() - 1];               // the longest palindrome at the start of s
        return new StringBuilder(s.substring(keep)).reverse() + s;
    }

    public static void main(String[] args) {
        for (String s : new String[]{"aacecaaa", "abcd", "abab"}) System.out.println(s + " " + shortestPalindrome(s));
    }
}
''', ts=r'''
function shortestPalindrome(s: string): string {
  const rev = s.split("").reverse().join(""), t = s + "#" + rev;
  const pi: number[] = new Array(t.length).fill(0);  // longest proper prefix of t[:i + 1] that is also its suffix
  for (let i = 1; i < t.length; i++) {
    let k = pi[i - 1];
    while (k && t[i] !== t[k]) k = pi[k - 1];
    if (t[i] === t[k]) k++;
    pi[i] = k;
  }
  const keep = pi[t.length - 1];                     // the longest palindrome at the start of s
  return s.slice(keep).split("").reverse().join("") + s;
}

for (const s of ["aacecaaa", "abcd", "abab"]) console.log(s, shortestPalindrome(s));
''')

t.code('p_dupsub', py=r'''
MOD, BASE = 1_000_003, 131


def longest_dup_substring(s):
    n = len(s)
    h, pw = [0] * (n + 1), [1] * (n + 1)
    for i, ch in enumerate(s):
        h[i + 1] = (h[i] * BASE + ord(ch)) % MOD
        pw[i + 1] = pw[i] * BASE % MOD

    def find(size):                              # start of a repeated piece of this size, or -1
        seen = {}
        for i in range(n - size + 1):
            x = (h[i + size] - h[i] * pw[size]) % MOD
            for j in seen.get(x, []):            # same hash: check the letters, since hashes can collide
                if s[j:j + size] == s[i:i + size]:
                    return i
            seen.setdefault(x, []).append(i)
        return -1

    lo, hi, best = 1, n - 1, ""
    while lo <= hi:
        mid = (lo + hi) // 2
        at = find(mid)
        if at >= 0:
            best, lo = s[at:at + mid], mid + 1
        else:
            hi = mid - 1
    return best


for s in ("banana", "abcd", "aaaaa"):
    print(f'{s}: "{longest_dup_substring(s)}"')
''', js=r'''
const MOD = 1000003, BASE = 131;

function longestDupSubstring(s) {
  const n = s.length, h = new Array(n + 1).fill(0), pw = new Array(n + 1).fill(1);
  for (let i = 0; i < n; i++) { h[i + 1] = (h[i] * BASE + s.charCodeAt(i)) % MOD; pw[i + 1] = pw[i] * BASE % MOD; }
  const find = size => {                             // start of a repeated piece of this size, or -1
    const seen = new Map();
    for (let i = 0; i + size <= n; i++) {
      const x = ((h[i + size] - h[i] * pw[size]) % MOD + MOD) % MOD;
      for (const j of seen.get(x) || []) if (s.slice(j, j + size) === s.slice(i, i + size)) return i;   // hashes can collide
      if (!seen.has(x)) seen.set(x, []);
      seen.get(x).push(i);
    }
    return -1;
  };
  let lo = 1, hi = n - 1, best = "";
  while (lo <= hi) {
    const mid = (lo + hi) >> 1, at = find(mid);
    if (at >= 0) { best = s.slice(at, at + mid); lo = mid + 1; } else hi = mid - 1;
  }
  return best;
}

for (const s of ["banana", "abcd", "aaaaa"]) console.log(`${s}: "${longestDupSubstring(s)}"`);
''', java=r'''
import java.util.*;

public class DuplicateSubstring {
    static final long MOD = 1_000_003, BASE = 131;
    static long[] h, pw;
    static String s;

    static int find(int size) {                      // start of a repeated piece of this size, or -1
        Map<Long, List<Integer>> seen = new HashMap<>();
        for (int i = 0; i + size <= s.length(); i++) {
            long x = ((h[i + size] - h[i] * pw[size]) % MOD + MOD) % MOD;
            for (int j : seen.getOrDefault(x, List.of()))
                if (s.substring(j, j + size).equals(s.substring(i, i + size))) return i;   // hashes can collide
            seen.computeIfAbsent(x, key -> new ArrayList<>()).add(i);
        }
        return -1;
    }

    static String longestDupSubstring(String str) {
        s = str;
        int n = s.length();
        h = new long[n + 1];
        pw = new long[n + 1];
        pw[0] = 1;
        for (int i = 0; i < n; i++) { h[i + 1] = (h[i] * BASE + s.charAt(i)) % MOD; pw[i + 1] = pw[i] * BASE % MOD; }
        int lo = 1, hi = n - 1;
        String best = "";
        while (lo <= hi) {
            int mid = (lo + hi) / 2, at = find(mid);
            if (at >= 0) { best = s.substring(at, at + mid); lo = mid + 1; } else hi = mid - 1;
        }
        return best;
    }

    public static void main(String[] args) {
        for (String w : new String[]{"banana", "abcd", "aaaaa"}) System.out.println(w + ": \"" + longestDupSubstring(w) + "\"");
    }
}
''', ts=r'''
const MOD = 1000003, BASE = 131;

function longestDupSubstring(s: string): string {
  const n = s.length, h: number[] = new Array(n + 1).fill(0), pw: number[] = new Array(n + 1).fill(1);
  for (let i = 0; i < n; i++) { h[i + 1] = (h[i] * BASE + s.charCodeAt(i)) % MOD; pw[i + 1] = pw[i] * BASE % MOD; }
  const find = (size: number): number => {           // start of a repeated piece of this size, or -1
    const seen = new Map<number, number[]>();
    for (let i = 0; i + size <= n; i++) {
      const x = ((h[i + size] - h[i] * pw[size]) % MOD + MOD) % MOD;
      for (const j of seen.get(x) || []) if (s.slice(j, j + size) === s.slice(i, i + size)) return i;   // hashes can collide
      if (!seen.has(x)) seen.set(x, []);
      (seen.get(x) as number[]).push(i);
    }
    return -1;
  };
  let lo = 1, hi = n - 1, best = "";
  while (lo <= hi) {
    const mid = (lo + hi) >> 1, at = find(mid);
    if (at >= 0) { best = s.slice(at, at + mid); lo = mid + 1; } else hi = mid - 1;
  }
  return best;
}

for (const s of ["banana", "abcd", "aaaaa"]) console.log(`${s}: "${longestDupSubstring(s)}"`);
''')

t.code('p_echo', py=r'''
MOD, BASE = 1_000_003, 131


def distinct_echo_substrings(text):
    n = len(text)
    h, pw = [0] * (n + 1), [1] * (n + 1)
    for i, ch in enumerate(text):
        h[i + 1] = (h[i] * BASE + ord(ch)) % MOD
        pw[i + 1] = pw[i] * BASE % MOD

    def piece(i, j):                             # the hash of text[i:j]
        return (h[j] - h[i] * pw[j - i]) % MOD

    found = set()
    for size in range(1, n // 2 + 1):
        for i in range(n - 2 * size + 1):
            if piece(i, i + size) == piece(i + size, i + 2 * size) and text[i:i + size] == text[i + size:i + 2 * size]:
                found.add(text[i:i + 2 * size])  # the hashes say maybe, the letters confirm
    return len(found)


print(distinct_echo_substrings("abcabcabc"), distinct_echo_substrings("leetcodeleetcode"), distinct_echo_substrings("aaaa"))
''', js=r'''
const MOD = 1000003, BASE = 131;

function distinctEchoSubstrings(text) {
  const n = text.length, h = new Array(n + 1).fill(0), pw = new Array(n + 1).fill(1);
  for (let i = 0; i < n; i++) { h[i + 1] = (h[i] * BASE + text.charCodeAt(i)) % MOD; pw[i + 1] = pw[i] * BASE % MOD; }
  const piece = (i, j) => ((h[j] - h[i] * pw[j - i]) % MOD + MOD) % MOD;   // the hash of text[i:j]
  const found = new Set();
  for (let size = 1; 2 * size <= n; size++) {
    for (let i = 0; i + 2 * size <= n; i++) {
      if (piece(i, i + size) === piece(i + size, i + 2 * size) && text.slice(i, i + size) === text.slice(i + size, i + 2 * size)) {
        found.add(text.slice(i, i + 2 * size));      // the hashes say maybe, the letters confirm
      }
    }
  }
  return found.size;
}

console.log(distinctEchoSubstrings("abcabcabc"), distinctEchoSubstrings("leetcodeleetcode"), distinctEchoSubstrings("aaaa"));
''', java=r'''
import java.util.*;

public class EchoSubstrings {
    static final long MOD = 1_000_003, BASE = 131;
    static long[] h, pw;

    static long piece(int i, int j) {                // the hash of text[i:j]
        return ((h[j] - h[i] * pw[j - i]) % MOD + MOD) % MOD;
    }

    static int distinctEchoSubstrings(String text) {
        int n = text.length();
        h = new long[n + 1];
        pw = new long[n + 1];
        pw[0] = 1;
        for (int i = 0; i < n; i++) { h[i + 1] = (h[i] * BASE + text.charAt(i)) % MOD; pw[i + 1] = pw[i] * BASE % MOD; }
        Set<String> found = new HashSet<>();
        for (int size = 1; 2 * size <= n; size++)
            for (int i = 0; i + 2 * size <= n; i++)
                if (piece(i, i + size) == piece(i + size, i + 2 * size) && text.substring(i, i + size).equals(text.substring(i + size, i + 2 * size)))
                    found.add(text.substring(i, i + 2 * size));   // the hashes say maybe, the letters confirm
        return found.size();
    }

    public static void main(String[] args) {
        System.out.println(distinctEchoSubstrings("abcabcabc") + " " + distinctEchoSubstrings("leetcodeleetcode") + " " + distinctEchoSubstrings("aaaa"));
    }
}
''', ts=r'''
const MOD = 1000003, BASE = 131;

function distinctEchoSubstrings(text: string): number {
  const n = text.length, h: number[] = new Array(n + 1).fill(0), pw: number[] = new Array(n + 1).fill(1);
  for (let i = 0; i < n; i++) { h[i + 1] = (h[i] * BASE + text.charCodeAt(i)) % MOD; pw[i + 1] = pw[i] * BASE % MOD; }
  const piece = (i: number, j: number): number => ((h[j] - h[i] * pw[j - i]) % MOD + MOD) % MOD;   // the hash of text[i:j]
  const found = new Set<string>();
  for (let size = 1; 2 * size <= n; size++) {
    for (let i = 0; i + 2 * size <= n; i++) {
      if (piece(i, i + size) === piece(i + size, i + 2 * size) && text.slice(i, i + size) === text.slice(i + size, i + 2 * size)) {
        found.add(text.slice(i, i + 2 * size));      // the hashes say maybe, the letters confirm
      }
    }
  }
  return found.size;
}

console.log(distinctEchoSubstrings("abcabcabc"), distinctEchoSubstrings("leetcodeleetcode"), distinctEchoSubstrings("aaaa"));
''')

# ---------------------------------------------------------------- practice
t.leet(28, 'e', 'p_strstr',
       statement='<p>Return the index of the first place where needle appears in haystack, or −1 if it does not appear.</p>',
       example='"sadbutsad", "sad"  →  0\n"leetcode", "leeto"  →  −1\n"hello", "ll"        →  2',
       hint='Glue the needle, a separator and the haystack, then run the Z algorithm.',
       approach='<p>Build needle + separator + haystack and fill the Z array. The first position after the separator whose z value equals the needle length is a match. Subtract the needle length and 1 to get the index in the haystack. The separator stops any match from running across the join.</p>',
       time='O(n + m)', space='O(n + m)')
t.leet(796, 'e', 'p_rotate', title='Rotate String', url='https://leetcode.com/problems/rotate-string/', diff='Easy',
       statement='<p>Return true if goal can be made by moving letters from the front of s to the back, any number of times.</p>',
       example='"abcde", "cdeab"  →  true\n"abcde", "abced"  →  false',
       hint='Every rotation of s appears inside s + s.',
       approach='<p>If the lengths differ, the answer is false. Otherwise goal is a rotation exactly when it appears inside s + s, so search for it with the Z algorithm on goal + separator + s + s.</p>',
       time='O(n)', space='O(n)')
t.leet(647, 'm', 'p_countpal', title='Palindromic Substrings', url='https://leetcode.com/problems/palindromic-substrings/', diff='Medium',
       statement='<p>Count the substrings of s that are palindromes. Substrings at different positions count separately, even if they have the same letters.</p>',
       example='"abc"   →  3\n"aaa"   →  6\n"abba"  →  6',
       hint='A palindrome of radius r around a centre contains smaller palindromes around the same centre.',
       approach='<p>Run Manacher to get the radius of the biggest palindrome around every centre of the # string. A radius r at one centre gives (r + 1) ÷ 2 palindromes in the original string, rounded down, one for each smaller radius with a letter at both ends. Add them up.</p>',
       time='O(n)', space='O(n)')
t.leet(1408, 'm', 'p_inarray',
       statement='<p>Return every word in the list that appears inside another word of the list.</p>',
       example='["mass","as","hero","superhero"]  →  ["as","hero"]\n["leetcode","et","code"]         →  ["et","code"]\n["blue","green","bu"]            →  []',
       hint='Join all the words with a separator. A word inside another word appears at least twice.',
       approach='<p>Join every word with #. Each word appears once on its own, so if a search finds it at two different places, the second copy is inside another word. Comparing the first and the last place found is enough. Aho-Corasick could find every word in one pass for very large lists.</p>',
       time='O(n × L) with built in search', space='O(L) for the joined text')
t.leet(1392, 'h', 'p_happy',
       statement='<p>A happy prefix is a prefix of s, not the whole string, that is also a suffix. Return the longest one, or an empty string.</p>',
       example='"level"   →  "l"\n"ababab"  →  "abab"\n"abc"     →  ""',
       hint='A suffix starting at i matches the start of s when i + z[i] reaches the end.',
       approach='<p>Fill the Z array. Walk i from 1 upwards and return s[i:] at the first i where i + z[i] equals the length, since that suffix matches the start and it is the longest such suffix. The KMP prefix function gives the same answer as its last value.</p>',
       time='O(n)', space='O(n)')
t.leet(214, 'h', 'p_shortpal', title='Shortest Palindrome', url='https://leetcode.com/problems/shortest-palindrome/', diff='Hard',
       statement='<p>Add letters only in front of s to make the shortest possible palindrome.</p>',
       example='"aacecaaa"  →  "aaacecaaa"\n"abcd"      →  "dcbabcd"',
       hint='Find the longest palindrome that starts at the beginning of s.',
       approach='<p>Build s + # + reverse(s) and compute the KMP prefix function. Its last value is the length of the longest prefix of s that equals a suffix of reverse(s), which is the longest palindrome at the start of s. The rest of s, reversed, goes in front.</p>',
       time='O(n)', space='O(n)')
t.leet(1044, 'x', 'p_dupsub', title='Longest Duplicate Substring', url='https://leetcode.com/problems/longest-duplicate-substring/', diff='Hard',
       statement='<p>Return any longest substring that appears at least twice in s, possibly overlapping, or an empty string.</p>',
       example='"banana"  →  "ana"\n"abcd"    →  ""',
       hint='If a length repeats, every shorter length repeats too.',
       approach='<p>Binary search the length. For one length, slide a rolling hash along the string and keep the start positions for each hash. When a hash appears again, compare the letters to rule out a collision. A suffix array with the LCP array solves it too, as in the lesson.</p>',
       time='O(n log n) on average', space='O(n)')
t.leet(1316, 'x', 'p_echo', title='Distinct Echo Substrings', url='https://leetcode.com/problems/distinct-echo-substrings/', diff='Hard',
       statement='<p>Count the distinct non empty substrings that can be written as some string joined to itself, like "abcabc".</p>',
       example='"abcabcabc"         →  3\n"leetcodeleetcode"  →  2',
       hint='Compare the two halves with hashes in O(1).',
       approach='<p>For every half length and every start, compare the hash of the first half with the hash of the second half. When they are equal, confirm the letters and put the substring in a set so each one is counted once. The hashes make most comparisons O(1).</p>',
       time='O(n²) hash checks', space='O(n²) in the worst case for the set')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='z-algorithm', emoji='📦', title='The Z algorithm', html='''
<p>The Strings chapter matched one pattern with KMP. The <b>Z algorithm</b> does the same job with an idea that is easy to picture. For every position i, z[i] is how many letters starting at i match the start of the string. The trick is the <b>Z box</b>: the rightmost stretch already known to match the start. Inside it, a new position copies what it already knows from earlier, and only compares letters past the edge.</p>
<div class="viz" data-viz="pk" data-pk="zbox"></div>
<div class="c3" data-k="zfunc" data-label="Z array and pattern search"></div>
<span class="eq">search: build pattern + $ + text, and report every i with z[i] = length of pattern</span>
<div class="tip">The right edge of the Z box only moves forward, so the total number of letter comparisons is at most about 2n. That makes the whole algorithm O(n).</div>
'''),
    dict(id='manacher', emoji='🪞', title='Manacher: every palindrome in linear time', html='''
<p>Growing a palindrome around every centre takes O(n²) in the worst case. <b>Manacher's algorithm</b> brings that down to O(n). First put a # between letters, so every palindrome has a single middle. Then remember the palindrome that reaches furthest to the right. A position inside it has a mirror on the other side of the centre, and the mirror already knows a radius to start from.</p>
<div class="viz" data-viz="pk" data-pk="manacher"></div>
<div class="c3" data-k="manacher" data-label="Manacher's longest palindrome"></div>
<span class="eq">inside the furthest palindrome: p[i] starts at min( r − i, p[2c − i] ), then grows</span>
<div class="warn">The radius in the # string is exactly the length of the palindrome in the original word, which is why the # trick works so neatly.</div>
'''),
    dict(id='suffix-array', emoji='🗂️', title='Suffix arrays and the LCP array', html='''
<p>A <b>suffix array</b> lists the start of every suffix of a string in sorted order. Sorting by doubling compares the first 1, 2, 4, 8 and more letters, reusing the ranks from the round before, so each round is one sort of pairs. The <b>LCP array</b> then stores how many letters each suffix shares with the one before it in sorted order.</p>
<div class="viz" data-viz="pk" data-pk="suffix"></div>
<div class="c3" data-k="suffix" data-label="Suffix array, LCP array and the longest repeat"></div>
<div class="tw"><table class="jt"><tr><th>Question</th><th>Answer from the arrays</th></tr>
<tr><td>Does a pattern appear?</td><td>Binary search the sorted suffixes</td></tr>
<tr><td>Longest repeated substring</td><td>The biggest LCP value</td></tr>
<tr><td>Number of distinct substrings</td><td>n(n + 1) ÷ 2 minus the sum of the LCP values</td></tr></table></div>
<div class="tip">Kasai's method builds the LCP array in O(n) because the shared length drops by at most 1 when you move from one suffix to the next shorter one.</div>
'''),
    dict(id='aho-corasick', emoji='🕸️', title='Aho-Corasick: many patterns at once', html='''
<p>To look for many words in one text, put all the words into one trie. Then add a <b>fail link</b> to every node: it points to the longest ending of that node's letters that is also somewhere in the trie. While reading the text, a missing branch sends you along the fail link instead of back to the start, so the text is read exactly once.</p>
<div class="viz" data-viz="pk" data-pk="aho"></div>
<div class="c3" data-k="aho" data-label="Aho-Corasick with fail links"></div>
<div class="exam">Fail links are built breadth first, so the link of every shorter node is ready before it is needed. A node also reports every word that ends at its fail link, which is how "she" also reports "he".</div>
<div class="tip">The original Unix fgrep tool was built on this algorithm, and virus scanners such as ClamAV use it to look for thousands of patterns in one pass.</div>
'''),
    dict(id='rolling-hash', emoji='🧮', title='Rolling hashes and binary search', html='''
<p>A <b>rolling hash</b> turns a window of letters into a number, and slides to the next window with one subtraction, one multiplication and one addition. With prefix hashes, the hash of any substring takes O(1). Two equal hashes mean the letters are probably equal, so a final letter check rules out a <b>collision</b>.</p>
<div class="viz" data-viz="pk" data-pk="rolling"></div>
<div class="c3" data-k="rolling" data-label="Longest repeated substring with hashing and binary search"></div>
<span class="eq">hash(s[i:j]) = h[j] − h[i] × base<sup>j − i</sup> &nbsp; (mod a prime)</span>
<div class="warn">With a small modulus, as in the animation, collisions are common. Real code uses a large prime, or two different hashes at once, so that a collision is very unlikely.</div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem is solved in the Practice section in Python, JavaScript, Java and TypeScript, with line by line replay. Each one uses one of the tools from this chapter.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>Tool</th></tr>
<tr><td><a href="#lc28">28. Find the Index of the First Occurrence in a String</a></td><td>Easy</td><td>Z algorithm</td></tr>
<tr><td><a href="#lc796">796. Rotate String</a></td><td>Easy</td><td>Z search in s + s</td></tr>
<tr><td><a href="#lc647">647. Palindromic Substrings</a></td><td>Medium</td><td>Manacher</td></tr>
<tr><td><a href="#lc1408">1408. String Matching in an Array</a></td><td>Medium</td><td>search in one joined text</td></tr>
<tr><td><a href="#lc1392">1392. Longest Happy Prefix</a></td><td>Hard</td><td>Z algorithm</td></tr>
<tr><td><a href="#lc214">214. Shortest Palindrome</a></td><td>Hard</td><td>KMP prefix function</td></tr>
<tr><td><a href="#lc1044">1044. Longest Duplicate Substring</a></td><td>Expert</td><td>rolling hash and binary search</td></tr>
<tr><td><a href="#lc1316">1316. Distinct Echo Substrings</a></td><td>Expert</td><td>rolling hash</td></tr></table></div>
'''),
]

VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const word = (s, lo, max) => { const w = String(s).trim().toLowerCase(); return /^[a-z]*$/.test(w) && w.length >= lo && w.length <= max ? w : null; };

  /* ---------- Z algorithm ---------- */
  D.zbox = el => PK.widget(el, {
    title: 'Find a pattern with the Z box', sub: 'Glue pattern + $ + text. z[i] is how many letters from i match the start. A z value equal to the pattern length is a match.',
    inputs: [{ k: 'p', label: 'Pattern', type: 'text', val: 'aba', w: 90 }, { k: 't', label: 'Text', type: 'text', val: 'abacaba', w: 150 }],
    random: () => pick([{ p: 'aba', t: 'abacaba' }, { p: 'aa', t: 'aaaba' }, { p: 'ab', t: 'babab' }, { p: 'cat', t: 'concat' }, { p: 'xyz', t: 'abcabc' }]),
    check: v => { const p = word(v.p, 1, 4), t = word(v.t, 1, 9); return p && t ? '' : 'Give a pattern of 1 to 4 letters and a text of 1 to 9 letters, a to z only.'; },
    frames: ({ p, t }) => {
      p = p.trim().toLowerCase(); t = t.trim().toLowerCase();
      const s = p + '$' + t, n = s.length, z = new Array(n).fill(''), F = [];
      z[0] = '·';
      let l = 0, r = 0;
      const pic = (cls = {}, ptr = {}) => [
        { t: 'row', label: 'pattern $ text', cells: [...s], cls, ptr },
        { t: 'row', label: 'z: letters matching the start', cells: z.slice(), cls: Object.fromEntries(z.map((v, i) => [i, v === p.length && i > p.length ? 'win' : v === '' || v === '·' ? '' : 'done'])) },
      ];
      F.push({ mood: 'think', msg: `"${s}". The $ never matches anything, so no run can cross from the pattern into the text.`, vars: {}, layers: pic() });
      for (let i = 1; i < n; i++) {
        let v = 0, reused = 0;
        if (i < r) { v = Math.min(r - i, z[i - l]); reused = v; }
        const before = v;
        while (i + v < n && s[v] === s[i + v]) v++;
        z[i] = v;
        const cls = {}, ptr = { [i]: 'i' };
        for (let k = l; k < r; k++) cls[k] = 'sel';
        for (let k = i; k < i + v; k++) cls[k] = 'yes';
        for (let k = 0; k < v; k++) if (!cls[k]) cls[k] = 'look';
        if (i + v < n) cls[i + v] = 'no';
        let msg;
        if (reused) msg = `i = ${i} is inside the Z box [${l}, ${r}), so ${reused} letter${reused > 1 ? 's are' : ' is'} known for free from z[${i - l}]. ${v > before ? `Compared on and found ${v - before} more.` : 'No new letters match.'} z = <b>${v}</b>.`;
        else msg = v ? `i = ${i}: ${v} letter${v > 1 ? 's match' : ' matches'} the start "${s.slice(0, v)}". z = <b>${v}</b>.` : `i = ${i}: "${s[i]}" is not "${s[0]}". z = <b>0</b>.`;
        if (i + v > r) { l = i; r = i + v; }
        const hit = v === p.length && i > p.length;
        F.push({ mood: hit ? 'happy' : reused ? 'wow' : 'look', fx: hit ? 'burst' : undefined, msg: hit ? msg + ` That is the whole pattern: a match at text position ${i - p.length - 1}!` : msg, vars: { i, z: v, box: `[${l}, ${r})` }, layers: pic(cls, ptr) });
      }
      const hits = [];
      for (let i = p.length + 1; i < n; i++) if (z[i] === p.length) hits.push(i - p.length - 1);
      F.push(hits.length
        ? { mood: 'wow', fx: 'rain', msg: `"${p}" appears in "${t}" at position${hits.length > 1 ? 's' : ''} <b>${hits.join(', ')}</b>. Every letter was compared only a few times, so the whole search is O(n + m).`, vars: { matches: hits.length }, layers: pic() }
        : { mood: 'sad', fx: 'shake', msg: `No z value reaches ${p.length}, so "${p}" is nowhere in "${t}". The Z box looked everywhere in one pass.`, vars: { matches: 0 }, layers: pic() });
      return F;
    }
  });

  /* ---------- Manacher ---------- */
  D.manacher = el => PK.widget(el, {
    title: 'Mirror, mirror: Manacher\'s palindromes', sub: 'A # between letters makes every palindrome odd. Inside the furthest palindrome, a position copies the radius of its mirror, then grows.',
    inputs: [{ k: 's', label: 'Word', type: 'text', val: 'abacaba', w: 130 }],
    random: () => ({ s: pick(['abacaba', 'babad', 'cbbd', 'abaaba', 'banana', 'noonday', 'abcd']) }),
    check: v => word(v.s, 1, 8) ? '' : 'Give a word of 1 to 8 letters, a to z only.',
    frames: ({ s }) => {
      s = s.trim().toLowerCase();
      const T = ['^', '#'];
      for (const ch of s) T.push(ch, '#');
      T.push('$');
      const n = T.length, P = new Array(n).fill(''), F = [];
      let c = 0, r = 0;
      const pic = (cls = {}, ptr = {}) => [
        { t: 'row', label: 'Word with # between letters', cells: T, cls, ptr, small: true },
        { t: 'row', label: 'Radius: letters on each side that mirror', cells: P.slice(), small: true, cls: Object.fromEntries(P.map((v, i) => [i, v === '' ? '' : 'done'])) },
      ];
      F.push({ mood: 'think', msg: `"${s}" becomes "${T.join('')}". ^ and $ are walls that never match, so the growing loop always stops.`, vars: {}, layers: pic() });
      for (let i = 1; i < n - 1; i++) {
        let v = 0, mirror = -1;
        if (i < r) { mirror = 2 * c - i; v = Math.min(r - i, P[mirror]); }
        const start = v;
        while (T[i + v + 1] === T[i - v - 1]) v++;
        P[i] = v;
        const cls = {}, ptr = { [i]: 'i' };
        for (let k = i - v; k <= i + v; k++) cls[k] = 'yes';
        cls[i] = 'cur';
        if (mirror >= 0) { ptr[mirror] = 'mirror'; ptr[c] = ptr[c] || 'c'; if (!cls[mirror]) cls[mirror] = 'sel'; }
        if (i + v > r) { c = i; r = i + v; }
        if (T[i] === '#' && v === 0) continue;
        const word2 = T.slice(i - v, i + v + 1).filter(x => x !== '#').join('');
        F.push({ mood: start ? 'wow' : v ? 'happy' : 'look',
          msg: `${start ? `This spot sits inside a bigger palindrome, and its mirror on the other side says the radius is at least ${start}. ` : ''}${v > start ? `Grew to radius ${v}` : `Radius ${v}`}${v ? `: "${word2}"` : ''}.`,
          vars: { i, radius: v, right: r }, layers: pic(cls, ptr) });
      }
      let k = 0;
      for (let i = 0; i < n; i++) if (P[i] !== '' && P[i] > (P[k] === '' ? -1 : P[k])) k = i;
      const best = T.slice(k - P[k], k + P[k] + 1).filter(x => x !== '#').join(''), cls = {};
      for (let i = k - P[k]; i <= k + P[k]; i++) cls[i] = 'win';
      F.push({ mood: 'wow', fx: 'rain', msg: `The biggest radius is ${P[k]}, so the longest palindrome is <b>"${best}"</b>. The right edge only ever moved forward, which makes this O(n).`, vars: { longest: best.length }, layers: pic(cls) });
      return F;
    }
  });

  /* ---------- suffix array and LCP ---------- */
  D.suffix = el => PK.widget(el, {
    title: 'Sort every ending of a word', sub: 'List every suffix, sort them, then compare neighbours. The biggest shared start is the longest repeated piece.',
    inputs: [{ k: 's', label: 'Word', type: 'text', val: 'banana', w: 120 }],
    random: () => ({ s: pick(['banana', 'mississip', 'abracad', 'papaya', 'aaaa', 'abcd']) }),
    check: v => word(v.s, 2, 9) ? '' : 'Give a word of 2 to 9 letters, a to z only.',
    frames: ({ s }) => {
      s = s.trim().toLowerCase();
      const n = s.length, F = [];
      let rank = [...s].map(ch => ch.charCodeAt(0) - 96), sa = [...Array(n).keys()];
      const pic = (order, extra, cls = {}, head = 'rank') => [{ t: 'grid', label: 'Suffixes', rows: order.map((p, r) => [p, s.slice(p), extra[r]]), clab: ['start', 'suffix', head], cls }];
      F.push({ mood: 'think', msg: `"${s}" has ${n} suffixes, one starting at every position. Here they are in their original order.`, vars: {}, layers: pic(sa, sa.map(() => ''), {}, '') });
      for (let k = 1; ; k *= 2) {
        const key = i => [rank[i], i + k < n ? rank[i + k] : 0];
        const cmp = (a, b) => { const x = key(a), y = key(b); return x[0] - y[0] || x[1] - y[1]; };
        sa.sort(cmp);
        const next = new Array(n).fill(1);
        for (let j = 1; j < n; j++) next[sa[j]] = next[sa[j - 1]] + (cmp(sa[j], sa[j - 1]) ? 1 : 0);
        rank = next;
        const done = rank[sa[n - 1]] === n;
        const cls = {};
        for (let j = 1; j < n; j++) if (rank[sa[j]] === rank[sa[j - 1]]) { cls[j + ',2'] = 'no'; cls[(j - 1) + ',2'] = 'no'; }
        F.push({ mood: done ? 'happy' : 'work', msg: `Sorted by the first ${2 * k > n ? 'all' : 2 * k} letter${2 * k > 1 ? 's' : ''}, using pairs of ranks from the last round. ${done ? 'Every suffix now has its own rank, so the order is final.' : 'Red ranks are still tied, so double the length and sort again.'}`, vars: { 'letters compared': Math.min(2 * k, n) }, layers: pic(sa, sa.map(p => rank[p]), cls) });
        if (done) break;
      }
      const pos = new Array(n), lcp = new Array(n).fill('');
      sa.forEach((p, i) => { pos[p] = i; });
      lcp[0] = 0;
      for (let i = 1; i < n; i++) {
        const a = s.slice(sa[i - 1]), b = s.slice(sa[i]);
        let h = 0;
        while (h < a.length && h < b.length && a[h] === b[h]) h++;
        lcp[i] = h;
        F.push({ mood: h ? 'happy' : 'look', msg: `"${a}" and "${b}" share ${h ? `"${b.slice(0, h)}", ${h} letter${h > 1 ? 's' : ''}` : 'nothing at the start'}.`, vars: { lcp: h }, layers: pic(sa, lcp.slice(), { [(i - 1) + ',1']: 'look', [i + ',1']: 'cur', [i + ',2']: h ? 'yes' : '' }, 'LCP') });
      }
      let best = 0;
      for (let i = 1; i < n; i++) if (lcp[i] > lcp[best]) best = i;
      F.push(lcp[best]
        ? { mood: 'wow', fx: 'rain', msg: `The biggest LCP is ${lcp[best]}, so <b>"${s.slice(sa[best], sa[best] + lcp[best])}"</b> is the longest piece that appears twice. Sorting put the two copies next to each other.`, vars: { longest: lcp[best] }, layers: pic(sa, lcp, { [best + ',2']: 'win', [best + ',1']: 'win', [(best - 1) + ',1']: 'win' }, 'LCP') }
        : { mood: 'sad', fx: 'shake', msg: `Every LCP is 0, so no letter appears twice in "${s}". Nothing repeats.`, vars: { longest: 0 }, layers: pic(sa, lcp, {}, 'LCP') });
      return F;
    }
  });

  /* ---------- Aho-Corasick ---------- */
  const SETS = { she: [['he', 'she', 'his', 'hers'], 'ushers'], cat: [['a', 'ab', 'bab', 'bc', 'bca', 'c', 'caa'], 'abccab'], dna: [['acg', 'cg', 'gt', 'cgt'], 'tacgtacg'] };
  D.aho = el => PK.widget(el, {
    title: 'Search for many words at once', sub: 'All the words share one trie. When the next letter has no branch, follow the fail link to the longest ending that is still in the trie, instead of starting over.',
    inputs: [{ k: 'set', label: 'Words', type: 'seg', val: 'she', opts: [['she', 'he she his hers'], ['cat', 'a ab bab bc …'], ['dna', 'DNA bits']] }],
    frames: ({ set }) => {
      const [words, text] = SETS[set], go = [{}], fail = [0], out = [[]], label = [''], depth = [0], paths = ['root'], F = [];
      for (const w of words) {
        let node = 0;
        for (const ch of w) {
          if (go[node][ch] === undefined) { go.push({}); fail.push(0); out.push([]); label.push(ch); depth.push(depth[node] + 1); paths.push((node ? paths[node] : '') + ch); go[node][ch] = go.length - 1; }
          node = go[node][ch];
        }
        out[node].push(w);
      }
      const queue = Object.values(go[0]);
      for (let qi = 0; qi < queue.length; qi++) {
        const node = queue[qi];
        for (const [ch, nx] of Object.entries(go[node])) {
          let f = fail[node];
          while (f && go[f][ch] === undefined) f = fail[f];
          fail[nx] = go[f][ch] !== undefined ? go[f][ch] : 0;
          out[nx] = out[nx].concat(out[fail[nx]]);
          queue.push(nx);
        }
      }
      const maxd = Math.max(...depth), byD = {};
      depth.forEach((d, id) => { (byD[d] = byD[d] || []).push(id); });
      Object.values(byD).forEach(row => row.sort((x, y) => (paths[x] < paths[y] ? -1 : 1)));   /* parents in order, so no edges cross */
      const W = 460, H = 60 + maxd * 55;
      const nodes = go.map((_, id) => { const row = byD[depth[id]], k = row.indexOf(id); return [id, Math.round(30 + (k + 0.5) * (W - 60) / row.length), 28 + depth[id] * 55, id ? label[id] : '•']; });
      const edges = [];
      go.forEach((m, id) => Object.values(m).forEach(nx => edges.push([id, nx])));
      const found = [];
      const pic = (ti, node, ncls = {}) => [
        { t: 'graph', label: 'Trie of all the words, read from the top', w: W, h: H, r: 15, nodes, edges, ncls: Object.assign(Object.fromEntries(out.map((o, id) => [id, o.length ? 'sel' : ''])), ncls), tag: Object.fromEntries(go.map((_, id) => [id, fail[id] && id === node ? 'fail: ' + paths[fail[id]] : ''])) },
        { t: 'row', label: 'Text', cells: [...text], cls: ti >= 0 ? { [ti]: 'cur' } : {}, ptr: ti >= 0 ? { [ti]: '👀' } : {} },
        { t: 'row', label: 'Found so far', cells: found.slice(), idx: false, cls: Object.fromEntries(found.map((_, k) => [k, 'yes'])) },
      ];
      F.push({ mood: 'think', msg: `Words: ${words.join(', ')}. Read "${text}" once, one letter at a time, walking down the trie.`, vars: {}, layers: pic(-1, 0, { 0: 'cur' }) });
      let node = 0;
      [...text].forEach((ch, i) => {
        const fell = [];
        while (node && go[node][ch] === undefined) { fell.push(paths[node]); node = fail[node]; }
        node = go[node][ch] !== undefined ? go[node][ch] : 0;
        const hits = out[node];
        hits.forEach(w => found.push(`${w}@${i - w.length + 1}`));
        const ncls = { [node]: hits.length ? 'win' : 'cur' };
        const msg = `${fell.length ? `No "${ch}" after ${fell.map(x => '"' + x + '"').join(', then ')}. Follow the fail link. ` : ''}${node ? `Read "${ch}": now at "${paths[node]}".` : `"${ch}" starts no word, back to the root.`}${hits.length ? ` Found <b>${hits.join(' and ')}</b>!` : ''}`;
        F.push({ mood: hits.length ? 'happy' : fell.length ? 'think' : 'look', fx: hits.length ? 'burst' : undefined, msg, vars: { letter: ch, at: paths[node], found: found.length }, layers: pic(i, node, ncls) });
      });
      F.push(found.length
        ? { mood: 'wow', fx: 'rain', msg: `${found.length} match${found.length > 1 ? 'es' : ''} in one pass: ${found.join(', ')}. The text was read once, however many words there are.`, vars: { found: found.length }, layers: pic(-1, -1) }
        : { mood: 'sad', fx: 'shake', msg: 'Not a single word was found. The trie was ready, but the text did not play along.', vars: { found: 0 }, layers: pic(-1, -1) });
      return F;
    }
  });

  /* ---------- rolling hash ---------- */
  const MOD = 97, BASE = 31;
  D.rolling = el => PK.widget(el, {
    title: 'Slide a window, compare fingerprints', sub: 'Each window of letters gets a number. Sliding by one updates it in one step. Equal numbers mean maybe equal, so the letters get a final check.',
    inputs: [{ k: 's', label: 'Text', type: 'text', val: 'banana', w: 140 }, { k: 'mode', label: 'Mode', type: 'seg', val: 'one', opts: [['one', '🪟 Windows of 3'], ['bin', '🔍 Binary search the length']] }],
    random: () => ({ s: pick(['banana', 'mississippi', 'abcabd', 'papaya', 'abcdef', 'aaaaa']), mode: pick(['one', 'bin']) }),
    check: v => word(v.s, 2, 11) ? '' : 'Give 2 to 11 letters, a to z only.',
    frames: ({ s, mode }) => {
      s = s.trim().toLowerCase();
      const n = s.length, F = [];
      const code = ch => ch.charCodeAt(0) - 96;
      const scan = (size, emit) => {
        const seen = new Map();
        let x = 0, pw = 1;
        for (let k = 0; k < size - 1; k++) pw = pw * BASE % MOD;
        for (let k = 0; k < size; k++) x = (x * BASE + code(s[k])) % MOD;
        for (let i = 0; i + size <= n; i++) {
          if (i) x = ((x - code(s[i - 1]) * pw % MOD + MOD) % MOD * BASE + code(s[i + size - 1])) % MOD;
          const old = seen.get(x);
          if (old !== undefined) {
            const same = s.slice(old, old + size) === s.slice(i, i + size);
            if (emit) emit(i, size, x, old, same, seen);
            if (same) return [old, i];
          } else { seen.set(x, i); if (emit) emit(i, size, x, -1, false, seen); }
        }
        return null;
      };
      const pic = (i, size, cls = {}, seen) => [
        { t: 'row', label: 'Text', cells: [...s], cls: Object.assign(i >= 0 ? Object.fromEntries(Array.from({ length: size }, (_, k) => [i + k, 'sel'])) : {}, cls) },
        { t: 'row', label: 'Fingerprints seen so far (window start: hash)', cells: seen ? [...seen.entries()].map(([h, st]) => `${st}:${h}`) : [], idx: false },
      ];
      if (mode === 'one') {
        const size = Math.min(3, n - 1);
        F.push({ mood: 'think', msg: `Hash every window of ${size} letters, with a = 1, b = 2 and so on, base ${BASE}, kept below ${MOD}. Look for a fingerprint seen before.`, vars: { size }, layers: pic(-1, size) });
        const res = scan(size, (i, sz, x, old, same, seen) => {
          if (old < 0) F.push({ mood: 'look', msg: `Window "${s.slice(i, i + sz)}" at ${i}: hash <b>${x}</b>, new. Remember it.`, vars: { hash: x }, layers: pic(i, sz, {}, new Map(seen)) });
          else if (same) F.push({ mood: 'happy', fx: 'burst', msg: `"${s.slice(i, i + sz)}" at ${i} has hash ${x}, the same as position ${old}, and the letters match too. A repeat!`, vars: { hash: x }, layers: pic(i, sz, Object.fromEntries(Array.from({ length: sz }, (_, k) => [old + k, 'win'])), new Map(seen)) });
          else F.push({ mood: 'wow', fx: 'shake', msg: `"${s.slice(i, i + sz)}" has hash ${x}, just like "${s.slice(old, old + sz)}" at ${old}, but the letters differ. A collision! That is why the letters are always checked.`, vars: { hash: x }, layers: pic(i, sz, Object.fromEntries(Array.from({ length: sz }, (_, k) => [old + k, 'no'])), new Map(seen)) });
        });
        F.push(res
          ? { mood: 'wow', fx: 'rain', msg: `"${s.slice(res[0], res[0] + size)}" appears at ${res[0]} and ${res[1]}. Each slide cost one subtract, one multiply and one add, whatever the window size.`, vars: {}, layers: pic(res[1], size, Object.fromEntries(Array.from({ length: size }, (_, k) => [res[0] + k, 'win']))) }
          : { mood: 'sad', msg: `No window of ${size} letters repeats in "${s}".`, vars: {}, layers: pic(-1, size) });
        return F;
      }
      let lo = 1, hi = n - 1, best = '';
      F.push({ mood: 'think', msg: `If some piece of length L repeats, a piece of every shorter length repeats too. So binary search the length from 1 to ${hi}.`, vars: { lo, hi }, layers: pic(-1, 1) });
      while (lo <= hi) {
        const mid = (lo + hi) >> 1, res = scan(mid);
        if (res) {
          best = s.slice(res[0], res[0] + mid);
          F.push({ mood: 'happy', msg: `Length ${mid}: "${best}" repeats at ${res[0]} and ${res[1]}. Try longer.`, vars: { lo, hi, try: mid }, layers: pic(res[1], mid, Object.fromEntries(Array.from({ length: mid }, (_, k) => [res[0] + k, 'win']))) });
          lo = mid + 1;
        } else {
          F.push({ mood: 'look', msg: `Length ${mid}: no window repeats. Try shorter.`, vars: { lo, hi, try: mid }, layers: pic(-1, mid) });
          hi = mid - 1;
        }
      }
      F.push(best
        ? { mood: 'wow', fx: 'rain', msg: `The longest repeated piece is <b>"${best}"</b>. Binary search needed only about log n rounds of sliding windows.`, vars: { longest: best.length }, layers: pic(-1, 1) }
        : { mood: 'sad', fx: 'shake', msg: `No letter repeats in "${s}", so there is no repeated piece at all.`, vars: { longest: 0 }, layers: pic(-1, 1) });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Read the text once, reuse what you already know',
    'panels': [
        {'s': [['e', '📦'], ['t', 'Z box', {'b': 1}]], 'h': 'Z algorithm', 't': 'Matches with the start.', 'more': 'O(n + m) search.'},
        {'s': [['e', '🪞'], ['t', 'mirror', {'b': 1}]], 'h': 'Manacher', 't': 'All palindromes in O(n).', 'more': 'Put # between letters.'},
        {'s': [['e', '🗂️'], ['t', 'sorted suffixes', {'b': 1}]], 'h': 'Suffix array', 't': 'Plus the LCP array.', 'more': 'Repeats sit side by side.'},
        {'s': [['e', '🕸️'], ['t', 'fail links', {'b': 1}]], 'h': 'Aho-Corasick', 't': 'Many words, one pass.', 'more': 'A trie with shortcuts.'},
    ],
    'remember': 'Each of these methods keeps something it already learned, a Z box, a mirror, a sorted order or a fail link, so that no letter has to be compared over and over.',
}

REAL = [
    ['🛡️', 'Virus and spam scanners', 'Aho-Corasick checks every file or message against thousands of known patterns in one pass.'],
    ['🧬', 'Genome search', 'Suffix arrays and their compressed cousins let tools find a DNA read among billions of letters quickly.'],
    ['📚', 'Plagiarism and duplicate finders', 'Rolling hashes fingerprint every window of text so matching passages are spotted fast.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to advanced strings. These methods read text once and reuse what they already know. You will find patterns with the Z box, find every palindrome with Manacher\'s mirror, sort every suffix of a word, search for many words at once with Aho-Corasick, and compare pieces of text with rolling hashes.'},
    {'id': 'z-algorithm', 'h': 'Z algorithm', 'en': 'For every position, the Z array counts how many letters match the start of the string. The Z box remembers the rightmost stretch already known to match, so a position inside it starts from a known value. Glue the pattern, a separator and the text, and every z value equal to the pattern length is a match.'},
    {'id': 'manacher', 'h': 'Manacher', 'en': 'Manacher puts a separator between letters so every palindrome has one middle. It remembers the palindrome that reaches furthest right. A position inside it copies the radius of its mirror, then tries to grow. The right edge only moves forward, so the whole method is linear.'},
    {'id': 'suffix-array', 'h': 'Suffix arrays', 'en': 'A suffix array lists every suffix of a string in sorted order. Sorting by doubling compares one, two, four and more letters using ranks from the round before. The LCP array then counts the letters each suffix shares with the one before it. The biggest value gives the longest repeated piece.'},
    {'id': 'aho-corasick', 'h': 'Aho-Corasick', 'en': 'Aho-Corasick puts every word into one trie and gives each node a fail link to the longest ending that is also in the trie. When the next letter has no branch, it follows the fail link instead of starting over, so the text is read only once.'},
    {'id': 'rolling-hash', 'h': 'Rolling hash', 'en': 'A rolling hash gives each window of letters a number, and updates it in one step when the window slides. Equal numbers mean the letters are probably equal, so a quick letter check rules out a collision. With binary search on the length, it finds the longest repeated piece.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from finding a word in a string to counting echo substrings. Each one is solved in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. For each problem, decide which tool fits: the Z box for matching the start, Manacher for palindromes, or a rolling hash for comparing pieces. Open the hint if you are stuck.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What does z[i] hold in the Z array?', 'o': ['The letter at i', 'How many letters from i match the start of the string', 'The number of times i appears', 'The index of the next match'], 'a': 1, 'hint': 'Compare with the start.', 'why': 'z[i] is the length of the longest stretch starting at i that equals a prefix of the string.'},
    {'lv': 'e', 'q': 'Why is a $ put between the pattern and the text in Z search?', 'o': ['For decoration', 'So that no match can run across from the pattern into the text', 'To make the string longer', 'To sort the letters'], 'a': 1, 'hint': 'It never matches.', 'why': 'A letter that appears nowhere else stops every match at the join.'},
    {'lv': 'e', 'q': 'What does Manacher put between letters?', 'o': ['Spaces', 'A separator like #', 'Numbers', 'Nothing'], 'a': 1, 'hint': 'It makes every palindrome odd.', 'why': 'With a # between letters, even and odd palindromes both get a single middle.'},
    {'lv': 'e', 'q': 'In Aho-Corasick, what is stored in the trie?', 'o': ['The text', 'All the words being searched for', 'The answers', 'The hashes'], 'a': 1, 'hint': 'One trie for every pattern.', 'why': 'All the patterns share one trie, so they are searched together.'},
    {'lv': 'm', 'q': 'What is the Z array of "aabxaab"?', 'o': ['0 1 0 0 3 1 0', '0 1 0 0 2 1 0', '0 2 0 0 3 1 0', '0 1 1 0 3 1 0'], 'a': 0, 'hint': 'Position 4 starts "aab" again.', 'why': 'z[1] = 1 for "a", z[4] = 3 for "aab", z[5] = 1 for "a". The rest are 0.'},
    {'lv': 'm', 'q': 'What is the suffix array of "banana"?', 'o': ['0 1 2 3 4 5', '5 3 1 0 4 2', '5 4 3 2 1 0', '1 3 5 0 2 4'], 'a': 1, 'hint': 'Sorted suffixes: a, ana, anana, banana, na, nana.', 'why': 'Those suffixes start at 5, 3, 1, 0, 4 and 2.'},
    {'lv': 'm', 'q': 'What does the biggest value in the LCP array tell you?', 'o': ['The number of suffixes', 'The length of the longest substring that appears at least twice', 'The longest palindrome', 'The number of distinct letters'], 'a': 1, 'hint': 'Neighbours in sorted order share a start.', 'why': 'A shared start of two different suffixes is a substring that appears twice, and the longest one shows up between sorted neighbours.'},
    {'lv': 'm', 'q': 'Why does a rolling hash need a final letter check?', 'o': ['To make it faster', 'Because two different windows can have the same hash', 'Because hashes change over time', 'It does not need one'], 'a': 1, 'hint': 'Think about collisions.', 'why': 'Hashing maps many windows to fewer numbers, so equal hashes only mean probably equal.'},
    {'lv': 'h', 'q': 'In Aho-Corasick, where does the fail link of "she" point when "he" is a word?', 'o': ['To the root', 'To "he"', 'To "s"', 'To "sh"'], 'a': 1, 'hint': 'The longest ending of "she" that is in the trie.', 'why': '"he" is the longest proper ending of "she" that is also a path in the trie.'},
    {'lv': 'h', 'q': 'Why are Aho-Corasick fail links built breadth first?', 'o': ['It uses less memory', 'So that every shorter node has its link ready before a deeper node needs it', 'It is random', 'To sort the words'], 'a': 1, 'hint': 'A fail link always points to a shallower node.', 'why': 'Building a link follows the links of shallower nodes, so those must be finished first.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 's = "abab"\nz = [0] * 4\nfor i in range(1, 4):\n    while i + z[i] < 4 and s[z[i]] == s[i + z[i]]:\n        z[i] += 1\nprint(z)', 'o': ['[0, 0, 2, 0]', '[0, 1, 2, 1]', '[0, 0, 1, 0]', '[0, 2, 0, 0]'], 'a': 0, 'hint': 'Only position 2 starts with "a".', 'why': 'Position 2 matches "ab", positions 1 and 3 start with b, so z is 0 0 2 0.'},
    {'lv': 'h', 'q': 'How many palindromic substrings does "aaa" have?', 'o': ['3', '4', '6', '7'], 'a': 2, 'hint': 'Three singles, two pairs and one triple.', 'why': 'a, a, a, aa, aa and aaa: six.'},
    {'lv': 'x', 'q': 'Why is the Z algorithm O(n)?', 'o': ['It uses a hash', 'Every successful comparison moves the right edge of the Z box forward, and it never moves back', 'It sorts first', 'It only looks at half the string'], 'a': 1, 'hint': 'Count how far the box edge can travel.', 'why': 'The edge moves at most n times in total, and each position makes at most one failed comparison.'},
    {'lv': 'x', 'q': 'How many distinct substrings does "aaa" have?', 'o': ['3', '4', '6', '7'], 'a': 0, 'hint': 'n(n + 1) ÷ 2 minus the sum of the LCP values.', 'why': '6 substrings minus LCP values 1 + 2 = 3 leaves 3: a, aa and aaa.'},
    {'lv': 'x', 'q': 'How does sorting by doubling compare the first 2k letters of two suffixes?', 'o': ['Letter by letter', 'By the pair (rank of the first k letters, rank of the next k letters)', 'By their hashes only', 'By their lengths'], 'a': 1, 'hint': 'Reuse the last round.', 'why': 'Two ranks from the previous round describe 2k letters, so each round is one sort of pairs.'},
    {'lv': 'x', 'q': 'In Shortest Palindrome, what does the last prefix function value of s + # + reverse(s) give?', 'o': ['The length of s', 'The length of the longest palindrome at the start of s', 'The number of palindromes', 'The middle of s'], 'a': 1, 'hint': 'A prefix of s that equals a suffix of its reverse.', 'why': 'A prefix of s that also ends reverse(s) reads the same both ways, so it is the longest palindromic prefix.'},
]

CALC = [
    {'lv': 'e', 'q': 'Where does "abra" appear in "abracadabra"? Give the second position.', 'ans': '7', 'hint': 'The first is 0.', 'steps': ['Z search finds z values of 4 at text positions 0 and 7.']},
    {'lv': 'e', 'q': 'What is the longest palindrome in "babad"? Give its length.', 'ans': '3', 'hint': 'bab or aba.', 'steps': ['"bab" and "aba" both have 3 letters, and no longer palindrome exists.']},
    {'lv': 'm', 'q': 'What is the LCP of "ana" and "anana"?', 'ans': '3', 'hint': 'Compare from the start.', 'steps': ['a = a, n = n, a = a, then "ana" ends.', 'They share 3 letters.']},
    {'lv': 'm', 'q': 'How many palindromic substrings does "abba" have?', 'ans': '6', 'hint': 'Four singles, then look for pairs.', 'steps': ['a, b, b, a, bb and abba.', 'Six in total.']},
    {'lv': 'h', 'q': 'With a = 1, b = 2, base 31 and modulus 97, what is the hash of "ab"?', 'ans': '33', 'hint': '1 × 31 + 2.', 'steps': ['<span class="eq">1 × 31 + 2 = 33</span>, which is already below 97.']},
    {'lv': 'h', 'q': 'How many matches does Aho-Corasick report for words he, she, his, hers in "ushers"?', 'ans': '3', 'hint': 'Run the animation.', 'steps': ['"she" at 1, "he" at 2 and "hers" at 2.']},
    {'lv': 'x', 'q': 'How many distinct substrings does "banana" have?', 'ans': '15', 'hint': 'n(n + 1) ÷ 2 minus the sum of the LCP values 0 1 3 0 0 2.', 'steps': ['<span class="eq">6 × 7 ÷ 2 = 21</span>', '<span class="eq">21 − (1 + 3 + 2) = 15</span>']},
    {'lv': 'x', 'q': 'What is the shortest palindrome made by adding letters in front of "abcd"? Give its length.', 'ans': '7', 'hint': 'Only "a" is a palindrome at the start.', 'steps': ['Add "dcb" in front: "dcbabcd".', 'Length 7.']},
]

TALK = {
    'z-algorithm': 'The Z algorithm answers one question for every position in a string: how many letters starting here match the very start of the string? That number is called z of i. To find a pattern in a text, glue them together as pattern, then a dollar sign, then text. Any position in the text part whose z value equals the pattern length is a match. The dollar sign never matches anything, so no match can spill over from the pattern into the text. The clever part is speed. The algorithm keeps a Z box, which is the rightmost stretch it has already proved matches the start. When a new position falls inside the box, its first few letters are already known, because they copy an earlier part of the string. So it starts from that known value and only compares letters past the right edge. The edge never moves backwards, so the total work is linear.',
    'manacher': 'Finding every palindrome by growing around each centre can take n squared steps on a string like a a a a a. Manacher found a way to do it in linear time. First, put a hash sign between every pair of letters and at both ends. Now every palindrome, odd or even, has a single middle position, which keeps the code simple. Next, remember the palindrome found so far that reaches furthest to the right, with its centre and its right edge. When you visit a new position inside that palindrome, look at its mirror position on the other side of the centre. Because the big palindrome reads the same both ways, the mirror already tells you a radius you can start from, as long as it stays inside the right edge. Then try to grow further. Each time a palindrome grows past the right edge, the edge moves forward, and it never moves back.',
    'suffix-array': 'A suffix is the end part of a string, starting from some position. Banana has six suffixes: banana, anana, nana, ana, na and a. A suffix array is simply the list of their starting positions in sorted order. Sorting them one letter at a time would be slow for long strings, so we sort by doubling. First rank the suffixes by their first letter. Then rank them by their first two letters, using a pair of ranks from the round before. Then four letters, then eight, until every suffix has its own rank. Next comes the LCP array, which stores how many letters each suffix shares with the one just before it in sorted order. Sorting puts similar suffixes next to each other, so the biggest LCP value reveals the longest piece that appears twice. In banana, that piece is ana, shared by anana and ana.',
    'aho-corasick': 'Suppose you must find several words in a text at once, such as he, she, his and hers. Searching for each word separately reads the text again and again. Aho-Corasick reads it only once. First, put all the words into a single trie, so words with the same beginning share a path. Then give every node a fail link. The fail link points to the longest ending of that node\'s letters that is also a path in the trie. For example, the node for s h e has a fail link to h e. Now walk through the text. If the next letter has a branch, follow it. If not, follow fail links until a branch exists, or you reach the root. Whenever you arrive at a node, report every word that ends there or along its fail links. In ushers, this finds she, then he, then hers.',
    'rolling-hash': 'Comparing two pieces of text letter by letter takes time proportional to their length. A rolling hash makes it almost instant. Treat the letters of a window as digits in some base, and take the remainder after dividing by a prime. That number is the window\'s fingerprint. When the window slides one step to the right, subtract the letter leaving on the left, multiply by the base, and add the letter arriving on the right. With prefix hashes, the fingerprint of any piece takes constant time. Two equal fingerprints mean the pieces are probably the same, but different pieces can collide, so always confirm with a real letter check. To find the longest repeated piece, notice that if some length repeats, every shorter length repeats too. So binary search the length, and for each length slide a window and look for a fingerprint seen before.',
    'leetcode': 'The LeetCode problems in this chapter each use one of the tools from the lessons. The easy problems find the first place a word appears in a string with the Z algorithm, and decide whether one string is a rotation of another by searching inside the string written twice. The medium problems count every palindromic substring using Manacher\'s radii, and find the words in a list that sit inside other words. The hard problems find the longest prefix that is also a suffix, and build the shortest palindrome by adding letters at the front, using the KMP prefix function. The expert problems find the longest substring that appears twice, with rolling hashes and binary search, and count the distinct substrings that are some string written twice in a row. Each one is solved in four languages, and you can replay every line.',
}

T = t.finish({
    'slug': 'advanced-strings', 'title': 'Advanced Strings', 'short': 'Advanced strings', 'emoji': '🧵', 'topic': 'advanced-strings', 'prefix': 'dsaadvs',
    'module': ('🚀', 'Expert topics'),
    'lead': 'Read the text once and reuse what you already know. Find patterns with the Z box, find every palindrome with Manacher\'s mirror, sort every suffix of a word, search for many words at once with Aho-Corasick and compare pieces of text with rolling hashes.',
    'desc': 'Advanced string algorithms in DSA: the Z algorithm, Manacher\'s algorithm for palindromes, suffix arrays with the LCP array, Aho-Corasick multi pattern search and rolling hashes with binary search, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 26,
    'summary': 'The Z algorithm for pattern search, Manacher\'s linear time palindromes, suffix arrays by doubling with Kasai\'s LCP array, Aho-Corasick with fail links for many patterns and rolling hashes with binary search. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['z algorithm', 'z function', 'manacher', 'palindrome', 'suffix array', 'lcp array', 'kasai', 'aho-corasick', 'fail link', 'multi pattern search', 'rolling hash', 'polynomial hash', 'rabin karp', 'longest repeated substring', 'string matching'],
    'added': '2026-11-23',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('dynamic-programming-2', 'dynamic-programming-2', '🧬 Dynamic programming 2'),
    'next': ('special-structures', 'special-structures', '🛗 Special structures'),
})
