# Strings: characters, immutability, two pointers, counting, sliding window and pattern matching.

CODES = {}


def C(key, py, js, java):
    CODES[key] = {'py': py, 'js': js, 'java': java}


# ---------------------------------------------------------------- lesson programs
C('char_codes', py=r'''
word = "Hi!"
for i in range(len(word)):
    ch = word[i]
    code = ord(ch)        # the number the computer really stores
    print(i, ch, code)

back = chr(72) + chr(105)  # numbers back to characters
print(back)
''', js=r'''
const word = "Hi!";
for (let i = 0; i < word.length; i++) {
  const ch = word[i];
  const code = ch.charCodeAt(0);  // the number the computer really stores
  console.log(i, ch, code);
}

const back = String.fromCharCode(72) + String.fromCharCode(105);  // numbers back to characters
console.log(back);
''', java=r'''
public class CharCodes {
    public static void main(String[] args) {
        String word = "Hi!";
        for (int i = 0; i < word.length(); i++) {
            char ch = word.charAt(i);
            int code = ch;           // the number the computer really stores
            System.out.println(i + " " + ch + " " + code);
        }

        String back = "" + (char) 72 + (char) 105;  // numbers back to characters
        System.out.println(back);
    }
}
''')

C('build_join', py=r'''
s = "cat"
t = s.upper()
print(s, t)               # the original is unchanged

# slow: every += copies the whole string built so far
slow = ""
for i in range(5):
    slow += str(i)

# fast: collect the pieces, join once at the end
parts = []
for i in range(5):
    parts.append(str(i))
fast = "".join(parts)
print(slow, fast, "equal" if slow == fast else "different")
''', js=r'''
const s = "cat";
const t = s.toUpperCase();
console.log(s, t);         // the original is unchanged

// slow: every += copies the whole string built so far
let slow = "";
for (let i = 0; i < 5; i++) {
  slow += String(i);
}

// fast: collect the pieces, join once at the end
const parts = [];
for (let i = 0; i < 5; i++) {
  parts.push(String(i));
}
const fast = parts.join("");
console.log(slow, fast, slow === fast ? "equal" : "different");
''', java=r'''
public class BuildStrings {
    public static void main(String[] args) {
        String s = "cat";
        String t = s.toUpperCase();
        System.out.println(s + " " + t);   // the original is unchanged

        // slow: every += copies the whole string built so far
        String slow = "";
        for (int i = 0; i < 5; i++) {
            slow += i;
        }

        // fast: a StringBuilder grows in place, like a dynamic array
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 5; i++) {
            sb.append(i);
        }
        String fast = sb.toString();
        System.out.println(slow + " " + fast + " " + (slow.equals(fast) ? "equal" : "different"));
    }
}
''')

C('ops_tour', py=r'''
text = "data structures"
print(len(text))
print(text[0], text[-1])
print(text[5:10])                 # characters 5, 6, 7, 8, 9
print(text.find("struct"))
print(text.find("xyz"))           # -1 means not found
words = text.split(" ")
print(words[1])
print("-".join(words))
print(text.replace("data", "big data"))
print("smaller" if "apple" < "banana" else "larger")
''', js=r'''
const text = "data structures";
console.log(text.length);
console.log(text[0], text[text.length - 1]);
console.log(text.slice(5, 10));          // characters 5, 6, 7, 8, 9
console.log(text.indexOf("struct"));
console.log(text.indexOf("xyz"));        // -1 means not found
const words = text.split(" ");
console.log(words[1]);
console.log(words.join("-"));
console.log(text.replace("data", "big data"));
console.log("apple" < "banana" ? "smaller" : "larger");
''', java=r'''
public class StringOps {
    public static void main(String[] args) {
        String text = "data structures";
        System.out.println(text.length());
        System.out.println(text.charAt(0) + " " + text.charAt(text.length() - 1));
        System.out.println(text.substring(5, 10));      // characters 5, 6, 7, 8, 9
        System.out.println(text.indexOf("struct"));
        System.out.println(text.indexOf("xyz"));        // -1 means not found
        String[] words = text.split(" ");
        System.out.println(words[1]);
        System.out.println(String.join("-", words));
        System.out.println(text.replace("data", "big data"));
        System.out.println("apple".compareTo("banana") < 0 ? "smaller" : "larger");
    }
}
''')

C('palindrome', py=r'''
def is_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        if not s[i].isalnum():
            i += 1                       # skip spaces and punctuation
        elif not s[j].isalnum():
            j -= 1
        elif s[i].lower() != s[j].lower():
            return False
        else:
            i += 1
            j -= 1
    return True


for s in ["Race car", "Hello"]:
    print(s, "->", "palindrome" if is_palindrome(s) else "not a palindrome")
''', js=r'''
const isAlnum = c => /[A-Za-z0-9]/.test(c);

function isPalindrome(s) {
  let i = 0, j = s.length - 1;
  while (i < j) {
    if (!isAlnum(s[i])) {
      i++;                               // skip spaces and punctuation
    } else if (!isAlnum(s[j])) {
      j--;
    } else if (s[i].toLowerCase() !== s[j].toLowerCase()) {
      return false;
    } else {
      i++;
      j--;
    }
  }
  return true;
}

for (const s of ["Race car", "Hello"]) {
  console.log(s, "->", isPalindrome(s) ? "palindrome" : "not a palindrome");
}
''', java=r'''
public class Palindrome {
    static boolean isPalindrome(String s) {
        int i = 0, j = s.length() - 1;
        while (i < j) {
            if (!Character.isLetterOrDigit(s.charAt(i))) {
                i++;                           // skip spaces and punctuation
            } else if (!Character.isLetterOrDigit(s.charAt(j))) {
                j--;
            } else if (Character.toLowerCase(s.charAt(i)) != Character.toLowerCase(s.charAt(j))) {
                return false;
            } else {
                i++;
                j--;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        for (String s : new String[]{"Race car", "Hello"}) {
            System.out.println(s + " -> " + (isPalindrome(s) ? "palindrome" : "not a palindrome"));
        }
    }
}
''')

C('anagram_count', py=r'''
def same_letters(a, b):
    if len(a) != len(b):
        return False
    count = [0] * 26                  # one counter per letter a to z
    for ch in a:
        count[ord(ch) - ord("a")] += 1
    for ch in b:
        count[ord(ch) - ord("a")] -= 1
    for c in count:
        if c != 0:
            return False
    return True


print("listen, silent:", "anagrams" if same_letters("listen", "silent") else "different")
print("apple, paper:", "anagrams" if same_letters("apple", "paper") else "different")
''', js=r'''
function sameLetters(a, b) {
  if (a.length !== b.length) return false;
  const count = new Array(26).fill(0);  // one counter per letter a to z
  for (const ch of a) count[ch.charCodeAt(0) - 97]++;
  for (const ch of b) count[ch.charCodeAt(0) - 97]--;
  for (const c of count) {
    if (c !== 0) return false;
  }
  return true;
}

console.log("listen, silent:", sameLetters("listen", "silent") ? "anagrams" : "different");
console.log("apple, paper:", sameLetters("apple", "paper") ? "anagrams" : "different");
''', java=r'''
public class Anagram {
    static boolean sameLetters(String a, String b) {
        if (a.length() != b.length()) return false;
        int[] count = new int[26];             // one counter per letter a to z
        for (char ch : a.toCharArray()) count[ch - 'a']++;
        for (char ch : b.toCharArray()) count[ch - 'a']--;
        for (int c : count) {
            if (c != 0) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println("listen, silent: " + (sameLetters("listen", "silent") ? "anagrams" : "different"));
        System.out.println("apple, paper: " + (sameLetters("apple", "paper") ? "anagrams" : "different"));
    }
}
''')

C('longest_unique', py=r'''
def longest_unique(s):
    last = {}                  # character -> index where it was last seen
    start = 0
    best, best_start = 0, 0
    for end in range(len(s)):
        ch = s[end]
        if ch in last and last[ch] >= start:
            start = last[ch] + 1          # jump past the earlier copy
        last[ch] = end
        if end - start + 1 > best:
            best = end - start + 1
            best_start = start
    return s[best_start:best_start + best]


for s in ["abcabcbb", "pwwkew"]:
    w = longest_unique(s)
    print(s, "->", w, len(w))
''', js=r'''
function longestUnique(s) {
  const last = new Map();      // character -> index where it was last seen
  let start = 0;
  let best = 0, bestStart = 0;
  for (let end = 0; end < s.length; end++) {
    const ch = s[end];
    if (last.has(ch) && last.get(ch) >= start) {
      start = last.get(ch) + 1;           // jump past the earlier copy
    }
    last.set(ch, end);
    if (end - start + 1 > best) {
      best = end - start + 1;
      bestStart = start;
    }
  }
  return s.slice(bestStart, bestStart + best);
}

for (const s of ["abcabcbb", "pwwkew"]) {
  const w = longestUnique(s);
  console.log(s, "->", w, w.length);
}
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class LongestUnique {
    static String longestUnique(String s) {
        Map<Character, Integer> last = new HashMap<>();  // character -> index where it was last seen
        int start = 0;
        int best = 0, bestStart = 0;
        for (int end = 0; end < s.length(); end++) {
            char ch = s.charAt(end);
            if (last.containsKey(ch) && last.get(ch) >= start) {
                start = last.get(ch) + 1;               // jump past the earlier copy
            }
            last.put(ch, end);
            if (end - start + 1 > best) {
                best = end - start + 1;
                bestStart = start;
            }
        }
        return s.substring(bestStart, bestStart + best);
    }

    public static void main(String[] args) {
        for (String s : new String[]{"abcabcbb", "pwwkew"}) {
            String w = longestUnique(s);
            System.out.println(s + " -> " + w + " " + w.length());
        }
    }
}
''')

C('kmp_search', py=r'''
def prefix_table(p):
    lps = [0] * len(p)        # lps[i]: longest proper prefix of p[0..i] that is also a suffix
    k = 0
    for i in range(1, len(p)):
        while k > 0 and p[i] != p[k]:
            k = lps[k - 1]
        if p[i] == p[k]:
            k += 1
        lps[i] = k
    return lps


def kmp_search(text, p):
    lps = prefix_table(p)
    hits = []
    k = 0                     # how many pattern characters match right now
    for i in range(len(text)):
        while k > 0 and text[i] != p[k]:
            k = lps[k - 1]    # fall back, never move i backwards
        if text[i] == p[k]:
            k += 1
        if k == len(p):
            hits.append(i - k + 1)
            k = lps[k - 1]
    return hits


print(prefix_table("ababc"))
print(kmp_search("abababcababc", "ababc"))
''', js=r'''
function prefixTable(p) {
  const lps = new Array(p.length).fill(0);  // lps[i]: longest proper prefix of p[0..i] that is also a suffix
  let k = 0;
  for (let i = 1; i < p.length; i++) {
    while (k > 0 && p[i] !== p[k]) k = lps[k - 1];
    if (p[i] === p[k]) k++;
    lps[i] = k;
  }
  return lps;
}

function kmpSearch(text, p) {
  const lps = prefixTable(p);
  const hits = [];
  let k = 0;                  // how many pattern characters match right now
  for (let i = 0; i < text.length; i++) {
    while (k > 0 && text[i] !== p[k]) k = lps[k - 1];  // fall back, never move i backwards
    if (text[i] === p[k]) k++;
    if (k === p.length) {
      hits.push(i - k + 1);
      k = lps[k - 1];
    }
  }
  return hits;
}

console.log("[" + prefixTable("ababc").join(", ") + "]");
console.log("[" + kmpSearch("abababcababc", "ababc").join(", ") + "]");
''', java=r'''
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Kmp {
    static int[] prefixTable(String p) {
        int[] lps = new int[p.length()];  // lps[i]: longest proper prefix of p[0..i] that is also a suffix
        int k = 0;
        for (int i = 1; i < p.length(); i++) {
            while (k > 0 && p.charAt(i) != p.charAt(k)) k = lps[k - 1];
            if (p.charAt(i) == p.charAt(k)) k++;
            lps[i] = k;
        }
        return lps;
    }

    static List<Integer> kmpSearch(String text, String p) {
        int[] lps = prefixTable(p);
        List<Integer> hits = new ArrayList<>();
        int k = 0;                  // how many pattern characters match right now
        for (int i = 0; i < text.length(); i++) {
            while (k > 0 && text.charAt(i) != p.charAt(k)) k = lps[k - 1];  // fall back, never move i backwards
            if (text.charAt(i) == p.charAt(k)) k++;
            if (k == p.length()) {
                hits.add(i - k + 1);
                k = lps[k - 1];
            }
        }
        return hits;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(prefixTable("ababc")));
        System.out.println(kmpSearch("abababcababc", "ababc"));
    }
}
''')

C('rabin_karp', py=r'''
def rabin_karp(text, p):
    B, M = 256, 101
    m = len(p)
    high = 1
    for _ in range(m - 1):
        high = high * B % M          # weight of the first character in a window
    hp = ht = 0
    for i in range(m):
        hp = (hp * B + ord(p[i])) % M
        ht = (ht * B + ord(text[i])) % M
    hits = []
    for i in range(len(text) - m + 1):
        if hp == ht and text[i:i + m] == p:   # equal fingerprints, then confirm
            hits.append(i)
        if i + m < len(text):                 # roll: drop text[i], add text[i + m]
            ht = ((ht - ord(text[i]) * high % M + M) % M * B + ord(text[i + m])) % M
    return hits


print(rabin_karp("the cat sat", "at"))
''', js=r'''
function rabinKarp(text, p) {
  const B = 256, M = 101;
  const m = p.length;
  let high = 1;
  for (let k = 0; k < m - 1; k++) high = high * B % M;   // weight of the first character in a window
  let hp = 0, ht = 0;
  for (let i = 0; i < m; i++) {
    hp = (hp * B + p.charCodeAt(i)) % M;
    ht = (ht * B + text.charCodeAt(i)) % M;
  }
  const hits = [];
  for (let i = 0; i + m <= text.length; i++) {
    if (hp === ht && text.slice(i, i + m) === p) hits.push(i);  // equal fingerprints, then confirm
    if (i + m < text.length) {                                // roll: drop text[i], add text[i + m]
      ht = ((ht - text.charCodeAt(i) * high % M + M) % M * B + text.charCodeAt(i + m)) % M;
    }
  }
  return hits;
}

console.log("[" + rabinKarp("the cat sat", "at").join(", ") + "]");
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class RabinKarp {
    static List<Integer> rabinKarp(String text, String p) {
        int B = 256, M = 101;
        int m = p.length();
        int high = 1;
        for (int k = 0; k < m - 1; k++) high = high * B % M;   // weight of the first character in a window
        int hp = 0, ht = 0;
        for (int i = 0; i < m; i++) {
            hp = (hp * B + p.charAt(i)) % M;
            ht = (ht * B + text.charAt(i)) % M;
        }
        List<Integer> hits = new ArrayList<>();
        for (int i = 0; i + m <= text.length(); i++) {
            if (hp == ht && text.substring(i, i + m).equals(p)) hits.add(i);  // equal fingerprints, then confirm
            if (i + m < text.length()) {                                      // roll: drop text[i], add text[i + m]
                ht = ((ht - text.charAt(i) * high % M + M) % M * B + text.charAt(i + m)) % M;
            }
        }
        return hits;
    }

    public static void main(String[] args) {
        System.out.println(rabinKarp("the cat sat", "at"));
    }
}
''')

# ---------------------------------------------------------------- practice solutions
C('p_reverse_words', py=r'''
def reverse_words(s):
    words = s.split()          # splits on any run of spaces and drops empty pieces
    words.reverse()
    return " ".join(words)


print('"' + reverse_words("  the sky   is blue ") + '"')
print('"' + reverse_words("hello") + '"')
''', js=r'''
function reverseWords(s) {
  const words = s.trim().split(/\s+/);  // splits on any run of spaces
  words.reverse();
  return words.join(" ");
}

console.log('"' + reverseWords("  the sky   is blue ") + '"');
console.log('"' + reverseWords("hello") + '"');
''', java=r'''
public class ReverseWords {
    static String reverseWords(String s) {
        String[] words = s.trim().split("\\s+");  // splits on any run of spaces
        StringBuilder sb = new StringBuilder();
        for (int i = words.length - 1; i >= 0; i--) {
            sb.append(words[i]);
            if (i > 0) sb.append(' ');
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        System.out.println("\"" + reverseWords("  the sky   is blue ") + "\"");
        System.out.println("\"" + reverseWords("hello") + "\"");
    }
}
''')

C('p_rotation', py=r'''
def is_rotation(a, b):
    # every rotation of a sits inside a + a
    return len(a) == len(b) and b in a + a


print("waterbottle, erbottlewat:", "yes" if is_rotation("waterbottle", "erbottlewat") else "no")
print("abcd, acbd:", "yes" if is_rotation("abcd", "acbd") else "no")
''', js=r'''
function isRotation(a, b) {
  // every rotation of a sits inside a + a
  return a.length === b.length && (a + a).includes(b);
}

console.log("waterbottle, erbottlewat:", isRotation("waterbottle", "erbottlewat") ? "yes" : "no");
console.log("abcd, acbd:", isRotation("abcd", "acbd") ? "yes" : "no");
''', java=r'''
public class Rotation {
    static boolean isRotation(String a, String b) {
        // every rotation of a sits inside a + a
        return a.length() == b.length() && (a + a).contains(b);
    }

    public static void main(String[] args) {
        System.out.println("waterbottle, erbottlewat: " + (isRotation("waterbottle", "erbottlewat") ? "yes" : "no"));
        System.out.println("abcd, acbd: " + (isRotation("abcd", "acbd") ? "yes" : "no"));
    }
}
''')

C('p_lcp', py=r'''
def longest_common_prefix(words):
    if not words:
        return ""
    first = words[0]
    for i in range(len(first)):
        ch = first[i]
        for w in words[1:]:
            if i == len(w) or w[i] != ch:
                return first[:i]        # column i is where they disagree
    return first


print('"' + longest_common_prefix(["flower", "flow", "flight"]) + '"')
print('"' + longest_common_prefix(["dog", "racecar", "car"]) + '"')
''', js=r'''
function longestCommonPrefix(words) {
  if (words.length === 0) return "";
  const first = words[0];
  for (let i = 0; i < first.length; i++) {
    const ch = first[i];
    for (let k = 1; k < words.length; k++) {
      const w = words[k];
      if (i === w.length || w[i] !== ch) return first.slice(0, i);  // column i is where they disagree
    }
  }
  return first;
}

console.log('"' + longestCommonPrefix(["flower", "flow", "flight"]) + '"');
console.log('"' + longestCommonPrefix(["dog", "racecar", "car"]) + '"');
''', java=r'''
public class CommonPrefix {
    static String longestCommonPrefix(String[] words) {
        if (words.length == 0) return "";
        String first = words[0];
        for (int i = 0; i < first.length(); i++) {
            char ch = first.charAt(i);
            for (int k = 1; k < words.length; k++) {
                String w = words[k];
                if (i == w.length() || w.charAt(i) != ch) return first.substring(0, i);  // column i is where they disagree
            }
        }
        return first;
    }

    public static void main(String[] args) {
        System.out.println("\"" + longestCommonPrefix(new String[]{"flower", "flow", "flight"}) + "\"");
        System.out.println("\"" + longestCommonPrefix(new String[]{"dog", "racecar", "car"}) + "\"");
    }
}
''')

C('p_compress', py=r'''
def compress(s):
    parts = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1                     # j stops at the end of the run
        parts.append(s[i] + str(j - i))
        i = j
    out = "".join(parts)
    return out if len(out) < len(s) else s


print(compress("aabcccccaaa"))
print(compress("abc"))
''', js=r'''
function compress(s) {
  const parts = [];
  let i = 0;
  while (i < s.length) {
    let j = i;
    while (j < s.length && s[j] === s[i]) j++;  // j stops at the end of the run
    parts.push(s[i] + (j - i));
    i = j;
  }
  const out = parts.join("");
  return out.length < s.length ? out : s;
}

console.log(compress("aabcccccaaa"));
console.log(compress("abc"));
''', java=r'''
public class Compress {
    static String compress(String s) {
        StringBuilder sb = new StringBuilder();
        int i = 0;
        while (i < s.length()) {
            int j = i;
            while (j < s.length() && s.charAt(j) == s.charAt(i)) j++;  // j stops at the end of the run
            sb.append(s.charAt(i)).append(j - i);
            i = j;
        }
        String out = sb.toString();
        return out.length() < s.length() ? out : s;
    }

    public static void main(String[] args) {
        System.out.println(compress("aabcccccaaa"));
        System.out.println(compress("abc"));
    }
}
''')

C('p_long_pal', py=r'''
def longest_palindrome(s):
    best_lo, best_len = 0, 0
    for center in range(2 * len(s) - 1):
        lo = center // 2
        hi = lo + center % 2           # odd centers sit on a letter, even ones between two
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        if hi - lo - 1 > best_len:
            best_lo, best_len = lo + 1, hi - lo - 1
    return s[best_lo:best_lo + best_len]


print(longest_palindrome("babad"))
print(longest_palindrome("cbbd"))
''', js=r'''
function longestPalindrome(s) {
  let bestLo = 0, bestLen = 0;
  for (let center = 0; center < 2 * s.length - 1; center++) {
    let lo = Math.floor(center / 2);
    let hi = lo + center % 2;          // odd centers sit on a letter, even ones between two
    while (lo >= 0 && hi < s.length && s[lo] === s[hi]) {
      lo--;
      hi++;
    }
    if (hi - lo - 1 > bestLen) {
      bestLo = lo + 1;
      bestLen = hi - lo - 1;
    }
  }
  return s.slice(bestLo, bestLo + bestLen);
}

console.log(longestPalindrome("babad"));
console.log(longestPalindrome("cbbd"));
''', java=r'''
public class LongestPalindrome {
    static String longestPalindrome(String s) {
        int bestLo = 0, bestLen = 0;
        for (int center = 0; center < 2 * s.length() - 1; center++) {
            int lo = center / 2;
            int hi = lo + center % 2;          // odd centers sit on a letter, even ones between two
            while (lo >= 0 && hi < s.length() && s.charAt(lo) == s.charAt(hi)) {
                lo--;
                hi++;
            }
            if (hi - lo - 1 > bestLen) {
                bestLo = lo + 1;
                bestLen = hi - lo - 1;
            }
        }
        return s.substring(bestLo, bestLo + bestLen);
    }

    public static void main(String[] args) {
        System.out.println(longestPalindrome("babad"));
        System.out.println(longestPalindrome("cbbd"));
    }
}
''')

C('p_group_anagrams', py=r'''
def group_anagrams(words):
    groups = {}                         # sorted letters -> words with exactly those letters
    for w in words:
        key = "".join(sorted(w))
        if key not in groups:
            groups[key] = []
        groups[key].append(w)
    return list(groups.values())


for g in group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]):
    print(" ".join(g))
''', js=r'''
function groupAnagrams(words) {
  const groups = new Map();             // sorted letters -> words with exactly those letters
  for (const w of words) {
    const key = [...w].sort().join("");
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(w);
  }
  return [...groups.values()];
}

for (const g of groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])) {
  console.log(g.join(" "));
}
''', java=r'''
import java.util.*;

public class GroupAnagrams {
    static Collection<List<String>> groupAnagrams(String[] words) {
        Map<String, List<String>> groups = new LinkedHashMap<>();  // sorted letters -> words with exactly those letters
        for (String w : words) {
            char[] cs = w.toCharArray();
            Arrays.sort(cs);
            String key = new String(cs);
            groups.computeIfAbsent(key, k -> new ArrayList<>()).add(w);
        }
        return groups.values();
    }

    public static void main(String[] args) {
        for (List<String> g : groupAnagrams(new String[]{"eat", "tea", "tan", "ate", "nat", "bat"})) {
            System.out.println(String.join(" ", g));
        }
    }
}
''')

C('p_min_window', py=r'''
def min_window(s, t):
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    missing = len(t)                 # characters of t not yet inside the window
    lo = 0
    best = (0, 0)
    for hi in range(len(s)):
        ch = s[hi]
        if need.get(ch, 0) > 0:
            missing -= 1
        need[ch] = need.get(ch, 0) - 1
        while missing == 0:          # window is valid, try to shrink it from the left
            if best == (0, 0) or hi + 1 - lo < best[1] - best[0]:
                best = (lo, hi + 1)
            need[s[lo]] += 1
            if need[s[lo]] > 0:
                missing += 1
            lo += 1
    return s[best[0]:best[1]]


print(min_window("ADOBECODEBANC", "ABC"))
''', js=r'''
function minWindow(s, t) {
  const need = new Map();
  for (const ch of t) need.set(ch, (need.get(ch) || 0) + 1);
  let missing = t.length;          // characters of t not yet inside the window
  let lo = 0;
  let bestLo = 0, bestHi = 0;
  for (let hi = 0; hi < s.length; hi++) {
    const ch = s[hi];
    if ((need.get(ch) || 0) > 0) missing--;
    need.set(ch, (need.get(ch) || 0) - 1);
    while (missing === 0) {        // window is valid, try to shrink it from the left
      if (bestHi === 0 || hi + 1 - lo < bestHi - bestLo) {
        bestLo = lo;
        bestHi = hi + 1;
      }
      need.set(s[lo], need.get(s[lo]) + 1);
      if (need.get(s[lo]) > 0) missing++;
      lo++;
    }
  }
  return s.slice(bestLo, bestHi);
}

console.log(minWindow("ADOBECODEBANC", "ABC"));
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class MinWindow {
    static String minWindow(String s, String t) {
        Map<Character, Integer> need = new HashMap<>();
        for (char ch : t.toCharArray()) need.merge(ch, 1, Integer::sum);
        int missing = t.length();          // characters of t not yet inside the window
        int lo = 0;
        int bestLo = 0, bestHi = 0;
        for (int hi = 0; hi < s.length(); hi++) {
            char ch = s.charAt(hi);
            if (need.getOrDefault(ch, 0) > 0) missing--;
            need.put(ch, need.getOrDefault(ch, 0) - 1);
            while (missing == 0) {         // window is valid, try to shrink it from the left
                if (bestHi == 0 || hi + 1 - lo < bestHi - bestLo) {
                    bestLo = lo;
                    bestHi = hi + 1;
                }
                char out = s.charAt(lo);
                need.put(out, need.get(out) + 1);
                if (need.get(out) > 0) missing++;
                lo++;
            }
        }
        return s.substring(bestLo, bestHi);
    }

    public static void main(String[] args) {
        System.out.println(minWindow("ADOBECODEBANC", "ABC"));
    }
}
''')

C('p_edit_distance', py=r'''
def edit_distance(a, b):
    # d[i][j] = fewest edits that turn the first i letters of a into the first j letters of b
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = 1 + min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1])
    return d[len(a)][len(b)]


print("cat -> cut:", edit_distance("cat", "cut"))
print("horse -> ros:", edit_distance("horse", "ros"))
''', js=r'''
function editDistance(a, b) {
  // d[i][j] = fewest edits that turn the first i letters of a into the first j letters of b
  const d = [];
  for (let i = 0; i <= a.length; i++) d.push(new Array(b.length + 1).fill(0));
  for (let i = 0; i <= a.length; i++) d[i][0] = i;
  for (let j = 0; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      if (a[i - 1] === b[j - 1]) {
        d[i][j] = d[i - 1][j - 1];
      } else {
        d[i][j] = 1 + Math.min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]);
      }
    }
  }
  return d[a.length][b.length];
}

console.log("cat -> cut:", editDistance("cat", "cut"));
console.log("horse -> ros:", editDistance("horse", "ros"));
''', java=r'''
public class EditDistance {
    static int editDistance(String a, String b) {
        // d[i][j] = fewest edits that turn the first i letters of a into the first j letters of b
        int[][] d = new int[a.length() + 1][b.length() + 1];
        for (int i = 0; i <= a.length(); i++) d[i][0] = i;
        for (int j = 0; j <= b.length(); j++) d[0][j] = j;
        for (int i = 1; i <= a.length(); i++) {
            for (int j = 1; j <= b.length(); j++) {
                if (a.charAt(i - 1) == b.charAt(j - 1)) {
                    d[i][j] = d[i - 1][j - 1];
                } else {
                    d[i][j] = 1 + Math.min(d[i - 1][j], Math.min(d[i][j - 1], d[i - 1][j - 1]));
                }
            }
        }
        return d[a.length()][b.length()];
    }

    public static void main(String[] args) {
        System.out.println("cat -> cut: " + editDistance("cat", "cut"));
        System.out.println("horse -> ros: " + editDistance("horse", "ros"));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    dict(id='what-is', emoji='🔤', title='What a string really is', html='''
<p>A <b>string</b> is a sequence of characters: a name, a sentence, a DNA sequence, a line of a log file. Underneath, the computer does not store letters at all. It stores <b>numbers</b>, one or more per character, and an <b>encoding</b> says which number means which character.</p>
<div class="grid2">
<div class="box"><h4>🔢 Index</h4><p>Characters are numbered from 0. In "cat", c is at index 0, a at 1 and t at 2. The last index is always length minus 1.</p></div>
<div class="box"><h4>📏 Length</h4><p>The number of characters. Reading any single character by its index is one step, <b>O(1)</b>, just like reading an array.</p></div>
</div>
<div class="tw"><table class="jt"><tr><th>Encoding</th><th>What it covers</th><th>Bytes per character</th></tr>
<tr><td><b>ASCII</b></td><td>English letters, digits, punctuation (codes 0 to 127)</td><td>1</td></tr>
<tr><td><b>Unicode</b></td><td>Every writing system, emoji and symbol. Each character gets a <b>code point</b>.</td><td>depends on how it is stored</td></tr>
<tr><td><b>UTF-8</b></td><td>The most common way to store Unicode on disk and on the web</td><td>1 to 4</td></tr>
<tr><td><b>UTF-16</b></td><td>How Java and JavaScript store strings in memory</td><td>2 or 4</td></tr>
</table></div>
<p>The letters A to Z have the codes 65 to 90, and a to z have 97 to 122. Many tricks below depend on this, for example <code>code − 97</code> turns a lowercase letter into a number from 0 to 25.</p>
<div class="viz" data-viz="strmem"></div>
<div class="c3" data-k="char_codes" data-label="Characters are numbers underneath"></div>
<div class="warn">An emoji such as 😀 is one character to you, but two UTF-16 units in Java and JavaScript, so <code>"😀".length</code> is 2 there and 1 in Python. Be careful when you count characters from user input.</div>
'''),
    dict(id='immutable', emoji='🧊', title='Immutable strings and building them fast', html='''
<p>In Python, JavaScript and Java a string is <b>immutable</b>: once made, it never changes. Methods such as <code>upper()</code> or <code>replace()</code> return a <b>new</b> string and leave the old one alone.</p>
<div class="rule">Changing one character of an immutable string means building a whole new string. That costs O(n), not O(1).</div>
<p>This matters inside loops. Writing <code>s += piece</code> a thousand times copies the growing string again and again: 1 + 2 + 3 + … + n characters, which is about n²/2 copies, so <b>O(n²)</b>. Collecting the pieces and joining once copies every character only once, so <b>O(n)</b>.</p>
<span class="eq">1 + 2 + 3 + … + n = n(n + 1) / 2 ≈ n² / 2</span>
<div class="tw"><table class="jt"><tr><th>Language</th><th>Slow way</th><th>Fast way</th></tr>
<tr><td>Python</td><td><code>s += x</code> in a loop</td><td><code>"".join(pieces)</code></td></tr>
<tr><td>JavaScript</td><td><code>s += x</code> in a loop</td><td><code>pieces.join("")</code></td></tr>
<tr><td>Java</td><td><code>s += x</code> in a loop</td><td><code>StringBuilder.append(x)</code></td></tr>
</table></div>
<div class="viz" data-viz="concat"></div>
<div class="c3" data-k="build_join" data-label="Immutable strings, slow and fast building"></div>
<div class="exam">In Java, <code>==</code> compares whether two variables point at the same object. Use <code>a.equals(b)</code> to compare the characters. In Python and JavaScript, <code>==</code> and <code>===</code> compare the characters.</div>
'''),
    dict(id='operations', emoji='🧰', title='Everyday operations and what they cost', html='''
<p>Every language gives you a toolbox for strings. Knowing what each tool costs stops you from hiding an O(n) step inside a loop.</p>
<div class="tw"><table class="jt"><tr><th>Operation</th><th>Python</th><th>JavaScript</th><th>Java</th><th>Cost</th></tr>
<tr><td>Length</td><td><code>len(s)</code></td><td><code>s.length</code></td><td><code>s.length()</code></td><td class="yes">O(1)</td></tr>
<tr><td>Character at i</td><td><code>s[i]</code></td><td><code>s[i]</code></td><td><code>s.charAt(i)</code></td><td class="yes">O(1)</td></tr>
<tr><td>Slice from i to j</td><td><code>s[i:j]</code></td><td><code>s.slice(i, j)</code></td><td><code>s.substring(i, j)</code></td><td>O(j − i)</td></tr>
<tr><td>Find a piece</td><td><code>s.find(p)</code></td><td><code>s.indexOf(p)</code></td><td><code>s.indexOf(p)</code></td><td>O(n · m) worst case</td></tr>
<tr><td>Compare</td><td><code>a == b</code>, <code>a &lt; b</code></td><td><code>a === b</code>, <code>a &lt; b</code></td><td><code>a.equals(b)</code>, <code>a.compareTo(b)</code></td><td>O(n)</td></tr>
<tr><td>Split and join</td><td><code>s.split(" ")</code>, <code>" ".join(w)</code></td><td><code>s.split(" ")</code>, <code>w.join(" ")</code></td><td><code>s.split(" ")</code>, <code>String.join(" ", w)</code></td><td>O(n)</td></tr>
<tr><td>Replace</td><td><code>s.replace(a, b)</code></td><td><code>s.replace(a, b)</code> (first match)</td><td><code>s.replace(a, b)</code> (all matches)</td><td>O(n)</td></tr>
</table></div>
<p>Strings compare in <b>dictionary order</b>: the first position where they differ decides, by character code. That is why "apple" comes before "banana", and also why "Zebra" comes before "apple" (capital letters have smaller codes).</p>
<div class="c3" data-k="ops_tour" data-label="A tour of the string toolbox"></div>
<div class="tip">Slicing is not free. A loop that slices a long string on every turn can quietly turn an O(n) idea into O(n²). Move indexes instead, and slice once at the end.</div>
'''),
    dict(id='two-pointers', emoji='👉', title='Two pointers: reverse and palindromes', html='''
<p>Many string problems become easy with two indexes that walk toward each other: <code>i</code> from the left and <code>j</code> from the right. Each step moves at least one of them, so the whole walk is <b>O(n)</b> with <b>O(1)</b> extra space.</p>
<p>A <b>palindrome</b> reads the same in both directions, like "level" or "Race car" once you ignore case and spaces. Compare <code>s[i]</code> with <code>s[j]</code>. If they match, move both inward. If one is a space or a comma, skip it. The first mismatch proves it is not a palindrome.</p>
<div class="viz" data-viz="palin"></div>
<div class="c3" data-k="palindrome" data-label="Palindrome check with two pointers"></div>
<div class="grid2">
<div class="box"><h4>🔁 Reversing</h4><p>Swap <code>s[i]</code> and <code>s[j]</code>, then move both inward. Because strings are immutable, you first copy the characters into an array (a list in Python, <code>char[]</code> in Java).</p></div>
<div class="box"><h4>🪞 Shortcut versus skill</h4><p><code>s == s[::-1]</code> also works in Python, but it builds a reversed copy, which needs O(n) extra space. Interviewers usually want the two pointer version.</p></div>
</div>
'''),
    dict(id='counting', emoji='🧮', title='Counting characters: anagrams and frequency', html='''
<p>Two words are <b>anagrams</b> when they use exactly the same letters the same number of times, like "listen" and "silent". Sorting both words and comparing works in O(n log n). Counting is faster.</p>
<ol>
<li>Make 26 counters, one per letter, all zero.</li>
<li>Walk the first word and add 1 for each letter.</li>
<li>Walk the second word and subtract 1 for each letter.</li>
<li>If every counter is back to zero, the words are anagrams.</li>
</ol>
<span class="eq">index of a letter = code(letter) − code('a')     for example  code('c') − 97 = 99 − 97 = 2</span>
<div class="c3" data-k="anagram_count" data-label="Anagram check with 26 counters"></div>
<p>The work is <b>O(n)</b> and the 26 counters are <b>O(1)</b> extra space, because 26 never grows with the input. When the alphabet is unknown (any Unicode text), use a hash map from character to count instead.</p>
<div class="tip">Counting shows up everywhere: the first character that does not repeat, the most common word, checking whether a ransom note can be cut out of a magazine. Whenever a problem says "same characters", think of a frequency table.</div>
'''),
    dict(id='window', emoji='🪟', title='Sliding window: the longest run without repeats', html='''
<p>A <b>window</b> is a stretch of the string between two indexes, <code>start</code> and <code>end</code>. Instead of checking every one of the n²/2 substrings, grow the window on the right one character at a time and shrink it on the left only when a rule is broken.</p>
<p>For the longest substring without a repeated character, the rule is "no character twice". Remember where each character was seen last. When the new character was already seen inside the window, jump <code>start</code> just past that earlier copy.</p>
<div class="viz" data-viz="window"></div>
<div class="c3" data-k="longest_unique" data-label="Longest substring without repeating characters"></div>
<div class="tw"><table class="jt"><tr><th>Approach</th><th>Idea</th><th>Time</th></tr>
<tr><td>Brute force</td><td>Check every substring for repeats</td><td class="no">O(n³)</td></tr>
<tr><td>Better brute force</td><td>Grow from each start until a repeat appears</td><td>O(n²)</td></tr>
<tr><td>Sliding window</td><td>Each index enters and leaves the window at most once</td><td class="yes">O(n)</td></tr>
</table></div>
<div class="rule">Both ends of a sliding window only ever move forward. That single fact is the proof that the loop is O(n).</div>
'''),
    dict(id='matching', emoji='🔎', title='Pattern matching: naive search and KMP', html='''
<p>Finding a pattern of length m inside a text of length n is one of the oldest string problems. Your editor's find box, <code>grep</code> and virus scanners all do it.</p>
<h3>The naive way</h3>
<p>Line the pattern up at every position of the text and compare character by character. In the worst case, such as text "aaaa…ab" and pattern "aab", almost every alignment matches for a while and then fails, so the cost is <b>O(n · m)</b>.</p>
<h3>Knuth, Morris and Pratt</h3>
<p>KMP never moves backwards in the text. When a mismatch happens after k characters matched, those k characters are already known. The <b>prefix table</b> (often called <code>lps</code>) says how much of the pattern still lines up, so the pattern slides forward without rechecking.</p>
<span class="eq">lps[i] = length of the longest proper prefix of p[0..i] that is also a suffix of p[0..i]</span>
<div class="tw"><table class="jt"><tr><th>i</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th></tr>
<tr><td>p[i]</td><td>a</td><td>b</td><td>a</td><td>b</td><td>c</td></tr>
<tr><td>lps[i]</td><td>0</td><td>0</td><td>1</td><td>2</td><td>0</td></tr>
</table></div>
<p>At i = 3 the piece is "abab". Its prefix "ab" is also its suffix, so lps[3] = 2. After a mismatch there, the search continues as if 2 characters already matched.</p>
<div class="viz" data-viz="match"></div>
<div class="c3" data-k="kmp_search" data-label="Prefix table and KMP search"></div>
<p>Building the table is O(m) and the search is O(n), so KMP is <b>O(n + m)</b> in every case.</p>
'''),
    dict(id='hashing', emoji='🧬', title='Rolling hash: Rabin and Karp', html='''
<p>Another way to search is to give every window of the text a <b>fingerprint</b>, a number computed from its characters, and compare fingerprints instead of characters. The trick is to update the fingerprint in O(1) as the window slides by one place: remove the leftmost character, shift, add the new character.</p>
<span class="eq">hash(window) = (c₀·B^(m−1) + c₁·B^(m−2) + … + c_(m−1)) mod M</span>
<span class="eq">next = ((hash − c_out · B^(m−1)) · B + c_in) mod M</span>
<p>Two different windows can share a fingerprint by bad luck. That is called a <b>collision</b>, so a match of fingerprints is always confirmed by comparing the characters.</p>
<div class="c3" data-k="rabin_karp" data-label="Rabin and Karp with a rolling hash"></div>
<div class="tw"><table class="jt"><tr><th>Algorithm</th><th>Preparation</th><th>Search</th><th>Shines when</th></tr>
<tr><td>Naive</td><td>none</td><td>O(n · m) worst</td><td>short patterns, simple code</td></tr>
<tr><td>KMP</td><td>O(m) prefix table</td><td>O(n)</td><td>guaranteed linear time</td></tr>
<tr><td>Rabin and Karp</td><td>O(m) first hash</td><td>O(n + m) expected</td><td>many patterns at once, plagiarism checks</td></tr>
</table></div>
<div class="fun">Rolling hashes are how tools spot copied paragraphs between documents: every window of words gets a fingerprint, and equal fingerprints point at shared text.</div>
'''),
]

# ---------------------------------------------------------------- comic, real life, narration
INFO = {
    'title': 'A string is a row of numbered boxes',
    'panels': [
        {'s': [['e', '🔤'], ['c', ['c', 'a', 't']]], 'h': 'Characters in a row', 't': 'Each box has an index from 0.', 'more': 'Reading the box at any index is one step, just like an array.'},
        {'s': [['e', '🔢'], ['c', [99, 97, 116]]], 'h': 'Numbers underneath', 't': 'An encoding maps codes to letters.', 'more': 'ASCII gives a the code 97. Unicode covers every language and emoji.'},
        {'s': [['e', '🧊'], ['t', 's.upper() → new string', {'b': 1, 'size': 12}]], 'h': 'Never changed in place', 't': 'Strings are immutable.', 'more': 'Build with join or StringBuilder, not += in a loop.'},
        {'s': [['e', '🪟'], ['c', ['a', 'b', 'c', 'a', 'b'], {'hl': {1: 'win', 2: 'win', 3: 'win'}}]], 'h': 'Smart scanning', 't': 'Windows, pointers and tables.', 'more': 'Sliding windows, two pointers and KMP turn O(n²) scans into O(n).'},
    ],
    'remember': 'A string is an array of character codes that cannot change. Index in O(1), copy in O(n), and scan cleverly with pointers, windows and tables.',
}

REAL = [
    ['🔍', 'Find in page', 'Pressing Ctrl+F runs a pattern matching algorithm over the whole page. Fast editors use ideas from KMP and Boyer and Moore to skip ahead instead of rechecking letters.'],
    ['🧬', 'Reading DNA', 'A genome is a string of about three billion letters drawn from A, C, G and T. Biologists search it for patterns and measure edit distance between genes to see how species are related.'],
    ['✍️', 'Spell check and autocorrect', 'When you type "teh", your phone finds dictionary words with a small edit distance, such as "the", and offers them as corrections.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome',
     'en': 'Welcome to strings. A string is a row of characters, and underneath every character is a number. In this lesson you will learn how strings are stored, why they never change, and the clever scanning tricks that make string problems fast.',
     'hi': 'Strings में आपका स्वागत है। String characters की एक पंक्ति है, और हर character के पीछे एक संख्या होती है। इस पाठ में आप सीखेंगे कि strings कैसे रखी जाती हैं, वे कभी बदलती क्यों नहीं, और कौन सी चतुर scanning तरकीबें string के सवालों को तेज़ बनाती हैं।',
     'kn': 'Strings ಗೆ ಸ್ವಾಗತ. String ಎಂದರೆ characters ಗಳ ಒಂದು ಸಾಲು, ಮತ್ತು ಪ್ರತಿ character ಹಿಂದೆ ಒಂದು ಸಂಖ್ಯೆ ಇರುತ್ತದೆ. ಈ ಪಾಠದಲ್ಲಿ strings ಹೇಗೆ ಸಂಗ್ರಹವಾಗುತ್ತವೆ, ಅವು ಏಕೆ ಬದಲಾಗುವುದಿಲ್ಲ, ಮತ್ತು string ಸಮಸ್ಯೆಗಳನ್ನು ವೇಗವಾಗಿಸುವ ಜಾಣ scanning ತಂತ್ರಗಳನ್ನು ಕಲಿಯುತ್ತೀರಿ.',
     'or': 'Strings କୁ ସ୍ୱାଗତ। String ହେଉଛି characters ର ଏକ ଧାଡ଼ି, ଏବଂ ପ୍ରତ୍ୟେକ character ପଛରେ ଗୋଟିଏ ସଂଖ୍ୟା ଥାଏ। ଏହି ପାଠରେ ଆପଣ ଶିଖିବେ strings କିପରି ରଖାଯାଏ, ସେମାନେ କାହିଁକି କେବେ ବଦଳନ୍ତି ନାହିଁ, ଏବଂ କେଉଁ ଚତୁର scanning କୌଶଳ string ସମସ୍ୟାକୁ ଦ୍ରୁତ କରେ।',
     'ar': 'مرحبًا بك في درس السلاسل النصية. السلسلة صف من الحروف، وخلف كل حرف رقم. ستتعلم في هذا الدرس كيف تُخزَّن السلاسل، ولماذا لا تتغير أبدًا، وحيل المسح الذكية التي تجعل مسائل النصوص سريعة.',
     'de': 'Willkommen bei Strings. Ein String ist eine Reihe von Zeichen, und hinter jedem Zeichen steht eine Zahl. In dieser Lektion lernst du, wie Strings gespeichert werden, warum sie sich nie ändern, und welche cleveren Suchtricks String-Aufgaben schnell machen.'},
    {'id': 'what-is', 'h': 'What a string is',
     'en': 'A string is a sequence of characters numbered from zero. The computer stores a number for each character, and an encoding such as ASCII or UTF-8 says which number means which letter. Reading one character by its index takes a single step.',
     'hi': 'String characters का एक क्रम है जिनकी गिनती शून्य से होती है। Computer हर character के लिए एक संख्या रखता है, और ASCII या UTF-8 जैसी encoding बताती है कि कौन सी संख्या कौन सा अक्षर है। Index से एक character पढ़ने में बस एक कदम लगता है।',
     'kn': 'String ಎಂದರೆ ಸೊನ್ನೆಯಿಂದ ಎಣಿಸಲಾದ characters ಗಳ ಅನುಕ್ರಮ. Computer ಪ್ರತಿ character ಗೆ ಒಂದು ಸಂಖ್ಯೆ ಇಡುತ್ತದೆ, ಮತ್ತು ASCII ಅಥವಾ UTF-8 ನಂತಹ encoding ಯಾವ ಸಂಖ್ಯೆ ಯಾವ ಅಕ್ಷರ ಎಂದು ಹೇಳುತ್ತದೆ. Index ಮೂಲಕ ಒಂದು character ಓದಲು ಒಂದೇ ಹೆಜ್ಜೆ ಸಾಕು.',
     'or': 'String ହେଉଛି ଶୂନ୍ୟରୁ ଗଣାଯାଉଥିବା characters ର ଏକ କ୍ରମ। Computer ପ୍ରତ୍ୟେକ character ପାଇଁ ଗୋଟିଏ ସଂଖ୍ୟା ରଖେ, ଏବଂ ASCII କିମ୍ବା UTF-8 ଭଳି encoding କହେ କେଉଁ ସଂଖ୍ୟା କେଉଁ ଅକ୍ଷର। Index ଦ୍ୱାରା ଗୋଟିଏ character ପଢ଼ିବାକୁ କେବଳ ଗୋଟିଏ ପାଦ ଲାଗେ।',
     'ar': 'السلسلة تسلسل من الحروف مرقّمة من الصفر. يخزّن الحاسوب رقمًا لكل حرف، ويحدد الترميز مثل ASCII أو UTF-8 أي رقم يعني أي حرف. قراءة حرف واحد من موضعه تحتاج خطوة واحدة.',
     'de': 'Ein String ist eine Folge von Zeichen, gezählt ab null. Der Computer speichert für jedes Zeichen eine Zahl, und eine Kodierung wie ASCII oder UTF-8 legt fest, welche Zahl welcher Buchstabe ist. Ein Zeichen über seinen Index zu lesen dauert nur einen Schritt.'},
    {'id': 'immutable', 'h': 'Immutable strings',
     'en': 'Strings in Python, JavaScript and Java never change after they are made. Adding to a string in a loop copies it every time, which grows to n squared work. Collect the pieces and join them once, or use a StringBuilder in Java, to keep it linear.',
     'hi': 'Python, JavaScript और Java में string बनने के बाद कभी नहीं बदलती। Loop में string में जोड़ने पर हर बार पूरी copy बनती है, जिससे काम n squared तक बढ़ जाता है। टुकड़े इकट्ठा करके एक बार join करें, या Java में StringBuilder लें, तो काम linear रहता है।',
     'kn': 'Python, JavaScript ಮತ್ತು Java ದಲ್ಲಿ string ಒಮ್ಮೆ ಆದ ಮೇಲೆ ಬದಲಾಗುವುದಿಲ್ಲ. Loop ನಲ್ಲಿ string ಗೆ ಸೇರಿಸಿದರೆ ಪ್ರತಿ ಬಾರಿ copy ಆಗುತ್ತದೆ, ಕೆಲಸ n squared ಆಗುತ್ತದೆ. ತುಂಡುಗಳನ್ನು ಸಂಗ್ರಹಿಸಿ ಒಮ್ಮೆ join ಮಾಡಿ, ಅಥವಾ Java ದಲ್ಲಿ StringBuilder ಬಳಸಿ, ಆಗ ಕೆಲಸ linear ಆಗಿರುತ್ತದೆ.',
     'or': 'Python, JavaScript ଓ Java ରେ string ତିଆରି ହେବା ପରେ କେବେ ବଦଳେ ନାହିଁ। Loop ରେ string ରେ ଯୋଡ଼ିଲେ ପ୍ରତିଥର copy ହୁଏ, ଯାହା n squared କାମ ହୋଇଯାଏ। ଖଣ୍ଡଗୁଡ଼ିକ ଏକାଠି କରି ଥରେ join କରନ୍ତୁ, କିମ୍ବା Java ରେ StringBuilder ବ୍ୟବହାର କରନ୍ତୁ, ତେବେ କାମ linear ରହେ।',
     'ar': 'السلاسل في بايثون وجافاسكربت وجافا لا تتغير بعد إنشائها. الإضافة إلى سلسلة داخل حلقة تنسخها في كل مرة، فيصل العمل إلى مربع n. اجمع القطع ثم اربطها مرة واحدة، أو استخدم StringBuilder في جافا، ليبقى العمل خطيًا.',
     'de': 'Strings in Python, JavaScript und Java ändern sich nach dem Erstellen nie. Wer in einer Schleife anhängt, kopiert jedes Mal alles, und die Arbeit wächst auf n zum Quadrat. Sammle die Teile und verbinde sie einmal, oder nimm in Java einen StringBuilder, dann bleibt es linear.'},
    {'id': 'operations', 'h': 'Everyday operations',
     'en': 'Length and reading one character cost a single step. Slicing, searching, comparing, splitting and replacing all walk through the characters, so they cost time in proportion to the length. Avoid hiding these inside a loop.',
     'hi': 'Length और एक character पढ़ना एक कदम का काम है। Slicing, searching, comparing, splitting और replacing सब characters पर चलते हैं, इसलिए उनका समय length के अनुपात में होता है। इन्हें loop के अंदर छिपाने से बचें।',
     'kn': 'Length ಮತ್ತು ಒಂದು character ಓದುವುದು ಒಂದೇ ಹೆಜ್ಜೆ. Slicing, searching, comparing, splitting ಮತ್ತು replacing ಎಲ್ಲವೂ characters ಮೇಲೆ ಸಾಗುತ್ತವೆ, ಆದ್ದರಿಂದ ಅವುಗಳ ಸಮಯ length ಗೆ ಅನುಗುಣವಾಗಿರುತ್ತದೆ. ಇವನ್ನು loop ಒಳಗೆ ಮುಚ್ಚಿಡಬೇಡಿ.',
     'or': 'Length ଏବଂ ଗୋଟିଏ character ପଢ଼ିବା ଗୋଟିଏ ପାଦର କାମ। Slicing, searching, comparing, splitting ଓ replacing ସବୁ characters ଉପରେ ଚାଲନ୍ତି, ତେଣୁ ସେମାନଙ୍କ ସମୟ length ଅନୁପାତରେ ହୁଏ। ଏଗୁଡ଼ିକୁ loop ଭିତରେ ଲୁଚାନ୍ତୁ ନାହିଁ।',
     'ar': 'معرفة الطول وقراءة حرف واحد خطوة واحدة. أما القص والبحث والمقارنة والتقسيم والاستبدال فكلها تمر على الحروف، فيتناسب وقتها مع الطول. تجنب إخفاءها داخل حلقة.',
     'de': 'Die Länge und ein einzelnes Zeichen zu lesen kostet einen Schritt. Ausschneiden, Suchen, Vergleichen, Teilen und Ersetzen gehen durch die Zeichen, ihre Zeit wächst also mit der Länge. Versteck sie nicht in einer Schleife.'},
    {'id': 'two-pointers', 'h': 'Two pointers',
     'en': 'Put one pointer at each end and walk them toward each other. To test a palindrome, compare the two characters, skip spaces and punctuation, and stop at the first mismatch. The walk takes linear time and almost no extra memory.',
     'hi': 'दोनों सिरों पर एक एक pointer रखें और उन्हें एक दूसरे की ओर चलाएँ। Palindrome जाँचने के लिए दोनों characters की तुलना करें, spaces और punctuation छोड़ दें, और पहली गड़बड़ी पर रुक जाएँ। यह linear समय लेता है और लगभग कोई अतिरिक्त memory नहीं।',
     'kn': 'ಎರಡೂ ತುದಿಗಳಲ್ಲಿ ಒಂದೊಂದು pointer ಇಟ್ಟು ಅವುಗಳನ್ನು ಪರಸ್ಪರ ಕಡೆಗೆ ನಡೆಸಿ. Palindrome ಪರೀಕ್ಷಿಸಲು ಎರಡು characters ಹೋಲಿಸಿ, spaces ಮತ್ತು punctuation ಬಿಟ್ಟು, ಮೊದಲ ವ್ಯತ್ಯಾಸದಲ್ಲಿ ನಿಲ್ಲಿಸಿ. ಇದು linear ಸಮಯ ಮತ್ತು ಬಹುತೇಕ ಹೆಚ್ಚುವರಿ memory ಇಲ್ಲದೆ ನಡೆಯುತ್ತದೆ.',
     'or': 'ଦୁଇ ମୁଣ୍ଡରେ ଗୋଟିଏ ଗୋଟିଏ pointer ରଖି ସେମାନଙ୍କୁ ପରସ୍ପର ଆଡ଼କୁ ଚଲାନ୍ତୁ। Palindrome ଯାଞ୍ଚ ପାଇଁ ଦୁଇ characters ତୁଳନା କରନ୍ତୁ, spaces ଓ punctuation ଛାଡ଼ନ୍ତୁ, ଏବଂ ପ୍ରଥମ ଅମେଳରେ ଅଟକନ୍ତୁ। ଏହା linear ସମୟ ନିଏ ଏବଂ ପ୍ରାୟ କୌଣସି ଅତିରିକ୍ତ memory ନୁହେଁ।',
     'ar': 'ضع مؤشرًا عند كل طرف وحرّكهما نحو بعضهما. لاختبار الكلمة المتناظرة قارن الحرفين، وتجاوز المسافات وعلامات الترقيم، وتوقف عند أول اختلاف. يستغرق ذلك وقتًا خطيًا ولا يكاد يحتاج ذاكرة إضافية.',
     'de': 'Setze an jedes Ende einen Zeiger und lass sie aufeinander zulaufen. Für ein Palindrom vergleichst du die beiden Zeichen, überspringst Leerzeichen und Satzzeichen und hörst beim ersten Unterschied auf. Das dauert lineare Zeit und braucht kaum zusätzlichen Speicher.'},
    {'id': 'counting', 'h': 'Counting characters',
     'en': 'Two words are anagrams when they use the same letters the same number of times. Keep twenty six counters, add one for each letter of the first word and subtract one for each letter of the second. If every counter returns to zero, they are anagrams.',
     'hi': 'दो शब्द anagram होते हैं जब उनमें वही अक्षर उतनी ही बार हों। छब्बीस counters रखें, पहले शब्द के हर अक्षर पर एक जोड़ें और दूसरे के हर अक्षर पर एक घटाएँ। अगर हर counter फिर से शून्य हो जाए, तो वे anagram हैं।',
     'kn': 'ಎರಡು ಪದಗಳಲ್ಲಿ ಅದೇ ಅಕ್ಷರಗಳು ಅಷ್ಟೇ ಬಾರಿ ಇದ್ದರೆ ಅವು anagram ಗಳು. ಇಪ್ಪತ್ತಾರು counters ಇಟ್ಟು, ಮೊದಲ ಪದದ ಪ್ರತಿ ಅಕ್ಷರಕ್ಕೆ ಒಂದು ಸೇರಿಸಿ, ಎರಡನೆಯದರ ಪ್ರತಿ ಅಕ್ಷರಕ್ಕೆ ಒಂದು ಕಳೆಯಿರಿ. ಎಲ್ಲಾ counters ಮತ್ತೆ ಸೊನ್ನೆಯಾದರೆ ಅವು anagram ಗಳು.',
     'or': 'ଦୁଇଟି ଶବ୍ଦରେ ସମାନ ଅକ୍ଷର ସମାନ ଥର ଥିଲେ ସେମାନେ anagram। ଛବିଶଟି counters ରଖନ୍ତୁ, ପ୍ରଥମ ଶବ୍ଦର ପ୍ରତ୍ୟେକ ଅକ୍ଷର ପାଇଁ ଏକ ଯୋଡ଼ନ୍ତୁ ଏବଂ ଦ୍ୱିତୀୟର ପ୍ରତ୍ୟେକ ଅକ୍ଷର ପାଇଁ ଏକ ବିୟୋଗ କରନ୍ତୁ। ସବୁ counter ପୁଣି ଶୂନ୍ୟ ହେଲେ ସେମାନେ anagram।',
     'ar': 'تكون الكلمتان جناسًا تامًا عندما تستخدمان الحروف نفسها بالعدد نفسه. احتفظ بستة وعشرين عدادًا، أضف واحدًا لكل حرف من الكلمة الأولى واطرح واحدًا لكل حرف من الثانية. إذا عادت كل العدادات إلى الصفر فهما جناس.',
     'de': 'Zwei Wörter sind Anagramme, wenn sie dieselben Buchstaben gleich oft benutzen. Halte sechsundzwanzig Zähler, zähle für jeden Buchstaben des ersten Wortes eins hoch und für jeden des zweiten eins herunter. Stehen am Ende alle Zähler auf null, sind es Anagramme.'},
    {'id': 'window', 'h': 'Sliding window',
     'en': 'A sliding window is a stretch of the string between a start and an end. Grow it on the right one character at a time, and move the start forward only when a character repeats. Both ends only move forward, so the whole scan is linear.',
     'hi': 'Sliding window string का वह हिस्सा है जो start और end के बीच है। इसे दाईं ओर एक एक character बढ़ाएँ, और start को तभी आगे बढ़ाएँ जब कोई character दोहराए। दोनों सिरे सिर्फ़ आगे बढ़ते हैं, इसलिए पूरा scan linear है।',
     'kn': 'Sliding window ಎಂದರೆ start ಮತ್ತು end ನಡುವಿನ string ಭಾಗ. ಅದನ್ನು ಬಲಕ್ಕೆ ಒಂದೊಂದೇ character ಬೆಳೆಸಿ, ಯಾವುದಾದರೂ character ಪುನರಾವರ್ತನೆಯಾದಾಗ ಮಾತ್ರ start ಮುಂದೆ ಸರಿಸಿ. ಎರಡೂ ತುದಿಗಳು ಮುಂದೆ ಮಾತ್ರ ಹೋಗುತ್ತವೆ, ಆದ್ದರಿಂದ ಸಂಪೂರ್ಣ scan linear.',
     'or': 'Sliding window ହେଉଛି start ଓ end ମଝିରେ ଥିବା string ର ଅଂଶ। ଏହାକୁ ଡାହାଣକୁ ଗୋଟିଏ ଗୋଟିଏ character ବଢ଼ାନ୍ତୁ, ଏବଂ କୌଣସି character ଦୋହରିଲେ ହିଁ start କୁ ଆଗକୁ ନିଅନ୍ତୁ। ଦୁଇ ମୁଣ୍ଡ କେବଳ ଆଗକୁ ଯାଆନ୍ତି, ତେଣୁ ପୂରା scan linear।',
     'ar': 'النافذة المنزلقة جزء من السلسلة بين بداية ونهاية. وسّعها إلى اليمين حرفًا حرفًا، وحرّك البداية إلى الأمام فقط عندما يتكرر حرف. الطرفان يتحركان إلى الأمام فقط، لذلك يكون المسح كله خطيًا.',
     'de': 'Ein gleitendes Fenster ist ein Stück des Strings zwischen Anfang und Ende. Vergrößere es rechts um ein Zeichen nach dem anderen und schiebe den Anfang nur vor, wenn sich ein Zeichen wiederholt. Beide Enden laufen nur vorwärts, also ist der ganze Durchlauf linear.'},
    {'id': 'matching', 'h': 'Pattern matching',
     'en': 'The naive search lines the pattern up at every position, which can cost n times m comparisons. KMP builds a prefix table first. After a mismatch it knows how much of the pattern still lines up, so it never moves backwards in the text and finishes in n plus m steps.',
     'hi': 'Naive search pattern को हर जगह रखकर देखती है, जिसमें n गुणा m तुलनाएँ लग सकती हैं। KMP पहले एक prefix table बनाता है। गड़बड़ी होने पर उसे पता होता है कि pattern का कितना हिस्सा अब भी मेल खाता है, इसलिए वह text में कभी पीछे नहीं जाता और n जमा m कदमों में पूरा होता है।',
     'kn': 'Naive search pattern ಅನ್ನು ಪ್ರತಿ ಸ್ಥಾನದಲ್ಲಿ ಇಟ್ಟು ನೋಡುತ್ತದೆ, ಅದಕ್ಕೆ n ಗುಣಿಸು m ಹೋಲಿಕೆಗಳು ಬೇಕಾಗಬಹುದು. KMP ಮೊದಲು prefix table ಕಟ್ಟುತ್ತದೆ. ವ್ಯತ್ಯಾಸವಾದಾಗ pattern ನ ಎಷ್ಟು ಭಾಗ ಇನ್ನೂ ಹೊಂದುತ್ತದೆ ಎಂದು ತಿಳಿದಿರುತ್ತದೆ, ಹಾಗಾಗಿ text ನಲ್ಲಿ ಹಿಂದೆ ಹೋಗದೆ n ಜೊತೆ m ಹೆಜ್ಜೆಗಳಲ್ಲಿ ಮುಗಿಸುತ್ತದೆ.',
     'or': 'Naive search pattern କୁ ପ୍ରତ୍ୟେକ ସ୍ଥାନରେ ରଖି ଦେଖେ, ଯାହାକୁ n ଗୁଣନ m ତୁଳନା ଲାଗିପାରେ। KMP ପ୍ରଥମେ ଏକ prefix table ତିଆରି କରେ। ଅମେଳ ହେଲେ ଏହା ଜାଣେ pattern ର କେତେ ଅଂଶ ଏବେ ବି ମେଳ ଖାଉଛି, ତେଣୁ text ରେ କେବେ ପଛକୁ ଯାଏ ନାହିଁ ଏବଂ n ଯୋଗ m ପାଦରେ ଶେଷ କରେ।',
     'ar': 'البحث الساذج يضع النمط عند كل موضع، وقد يكلف ذلك n ضرب m مقارنة. أما KMP فيبني أولًا جدول البادئات. وعند الاختلاف يعرف كم من النمط ما زال متطابقًا، فلا يعود أبدًا إلى الوراء في النص وينتهي في n زائد m خطوة.',
     'de': 'Die naive Suche legt das Muster an jede Stelle, was n mal m Vergleiche kosten kann. KMP baut zuerst eine Präfixtabelle. Nach einem Fehlschlag weiß es, wie viel vom Muster noch passt, geht im Text nie zurück und ist nach n plus m Schritten fertig.'},
    {'id': 'hashing', 'h': 'Rolling hash',
     'en': 'Rabin and Karp give every window of the text a fingerprint number and compare fingerprints instead of letters. Sliding the window updates the fingerprint in one step. Equal fingerprints are always confirmed by comparing the characters, because two windows can collide.',
     'hi': 'Rabin और Karp text की हर window को एक fingerprint संख्या देते हैं और अक्षरों की जगह fingerprints की तुलना करते हैं। Window खिसकाने पर fingerprint एक कदम में बदल जाता है। बराबर fingerprints की पुष्टि हमेशा characters मिलाकर की जाती है, क्योंकि दो windows टकरा सकती हैं।',
     'kn': 'Rabin ಮತ್ತು Karp text ನ ಪ್ರತಿ window ಗೆ ಒಂದು fingerprint ಸಂಖ್ಯೆ ಕೊಟ್ಟು, ಅಕ್ಷರಗಳ ಬದಲು fingerprints ಹೋಲಿಸುತ್ತಾರೆ. Window ಸರಿಸಿದಾಗ fingerprint ಒಂದೇ ಹೆಜ್ಜೆಯಲ್ಲಿ ಬದಲಾಗುತ್ತದೆ. ಎರಡು windows ಡಿಕ್ಕಿಯಾಗಬಹುದಾದ್ದರಿಂದ ಸಮಾನ fingerprints ಅನ್ನು characters ಹೋಲಿಸಿ ಖಚಿತಪಡಿಸಲಾಗುತ್ತದೆ.',
     'or': 'Rabin ଓ Karp text ର ପ୍ରତ୍ୟେକ window କୁ ଏକ fingerprint ସଂଖ୍ୟା ଦିଅନ୍ତି ଏବଂ ଅକ୍ଷର ବଦଳରେ fingerprints ତୁଳନା କରନ୍ତି। Window ଘୁଞ୍ଚାଇଲେ fingerprint ଗୋଟିଏ ପାଦରେ ବଦଳେ। ଦୁଇ windows ଧକ୍କା ଖାଇପାରନ୍ତି, ତେଣୁ ସମାନ fingerprints କୁ ସବୁବେଳେ characters ମିଳାଇ ନିଶ୍ଚିତ କରାଯାଏ।',
     'ar': 'يعطي رابين وكارب كل نافذة من النص رقم بصمة، ويقارنان البصمات بدل الحروف. انزلاق النافذة يحدّث البصمة في خطوة واحدة. وتُؤكَّد البصمات المتساوية دائمًا بمقارنة الحروف، لأن نافذتين قد تتصادمان.',
     'de': 'Rabin und Karp geben jedem Fenster des Textes eine Fingerabdruck-Zahl und vergleichen Fingerabdrücke statt Buchstaben. Beim Verschieben wird der Fingerabdruck in einem Schritt aktualisiert. Gleiche Fingerabdrücke werden immer durch Vergleich der Zeichen bestätigt, weil zwei Fenster kollidieren können.'},
    {'id': 'practice', 'h': 'Practice',
     'en': 'Time to practise. Each problem has a hint and a full solution in Python, JavaScript and Java. Try it on paper first, then open the solution and replay it line by line.',
     'hi': 'अब अभ्यास का समय है। हर सवाल के साथ एक hint और Python, JavaScript और Java में पूरा हल है। पहले काग़ज़ पर कोशिश करें, फिर हल खोलें और उसे line by line चलाकर देखें।',
     'kn': 'ಈಗ ಅಭ್ಯಾಸದ ಸಮಯ. ಪ್ರತಿ ಸಮಸ್ಯೆಗೆ ಒಂದು hint ಮತ್ತು Python, JavaScript ಮತ್ತು Java ದಲ್ಲಿ ಪೂರ್ಣ ಪರಿಹಾರವಿದೆ. ಮೊದಲು ಕಾಗದದ ಮೇಲೆ ಪ್ರಯತ್ನಿಸಿ, ನಂತರ ಪರಿಹಾರ ತೆರೆದು line by line ನೋಡಿ.',
     'or': 'ଏବେ ଅଭ୍ୟାସର ସମୟ। ପ୍ରତ୍ୟେକ ସମସ୍ୟା ସହ ଏକ hint ଏବଂ Python, JavaScript ଓ Java ରେ ପୂରା ସମାଧାନ ଅଛି। ପ୍ରଥମେ କାଗଜରେ ଚେଷ୍ଟା କରନ୍ତୁ, ତାପରେ ସମାଧାନ ଖୋଲି line by line ଦେଖନ୍ତୁ।',
     'ar': 'حان وقت التدريب. لكل مسألة تلميح وحل كامل بلغات بايثون وجافاسكربت وجافا. جرّبها على الورق أولًا، ثم افتح الحل وشغّله سطرًا سطرًا.',
     'de': 'Zeit zum Üben. Jede Aufgabe hat einen Hinweis und eine vollständige Lösung in Python, JavaScript und Java. Versuch es zuerst auf Papier, dann öffne die Lösung und spiel sie Zeile für Zeile ab.'},
]

PRACTICE = [
    {'id': 'reverse-words', 'lv': 'e', 'title': 'Reverse the words in a sentence', 'code': 'p_reverse_words',
     'statement': '<p>Given a sentence that may have extra spaces at the ends and between words, return the words in reverse order, separated by exactly one space.</p>',
     'example': 'Input: "  the sky   is blue "  →  "blue is sky the"\nInput: "hello"                 →  "hello"',
     'hint': 'Split the sentence into words first, so the extra spaces disappear. Then reverse the list of words.',
     'approach': '<p>Splitting on runs of whitespace gives the clean list of words. Reverse that list and join it back with single spaces. Every character is touched a constant number of times.</p>',
     'time': 'O(n)', 'space': 'O(n)'},
    {'id': 'rotation', 'lv': 'e', 'title': 'Is one string a rotation of another', 'code': 'p_rotation',
     'statement': '<p>A rotation moves some characters from the front to the back, so "erbottlewat" is a rotation of "waterbottle". Decide whether b is a rotation of a using one search.</p>',
     'example': 'Input: "waterbottle", "erbottlewat"  →  yes\nInput: "abcd", "acbd"                →  no',
     'hint': 'Write a twice in a row. What do you notice about every rotation of a?',
     'approach': '<p>Every rotation of a appears inside a + a. For example "waterbottle" + "waterbottle" contains "erbottlewat". Check that the lengths match, then search for b inside a + a.</p>',
     'time': 'O(n) with KMP, O(n²) with a naive search', 'space': 'O(n)'},
    {'id': 'common-prefix', 'lv': 'm', 'title': 'Longest common prefix', 'code': 'p_lcp',
     'statement': '<p>Given a list of words, return the longest prefix that all of them share. Return an empty string when they share nothing.</p>',
     'example': 'Input: ["flower", "flow", "flight"]  →  "fl"\nInput: ["dog", "racecar", "car"]     →  ""',
     'hint': 'Stack the words on top of each other and read them column by column.',
     'approach': '<p>Take the first word as the reference. For each position i, check that every other word has the same character there. The first column where a word is too short or different ends the prefix.</p>',
     'time': 'O(total characters)', 'space': 'O(1)'},
    {'id': 'compress', 'lv': 'm', 'title': 'Run length compression', 'code': 'p_compress',
     'statement': '<p>Compress a string by replacing each run of the same character with the character and the run length. If the result is not shorter than the original, return the original.</p>',
     'example': 'Input: "aabcccccaaa"  →  "a2b1c5a3"\nInput: "abc"          →  "abc"   (a1b1c1 would be longer)',
     'hint': 'Use two indexes: i marks the start of a run and j walks to its end.',
     'approach': '<p>From i, move j forward while s[j] equals s[i]. The run length is j − i. Append the character and the length to a builder, then jump i to j. Build with a list or StringBuilder, never with += in a loop.</p>',
     'time': 'O(n)', 'space': 'O(n)'},
    {'id': 'longest-palindrome', 'lv': 'h', 'title': 'Longest palindromic substring', 'code': 'p_long_pal',
     'statement': '<p>Return the longest substring that is a palindrome. If several have the same length, return the first one found.</p>',
     'example': 'Input: "babad"  →  "bab"   ("aba" is also correct)\nInput: "cbbd"   →  "bb"',
     'hint': 'Every palindrome has a center. There are 2n − 1 possible centers: on each letter and between each pair of letters.',
     'approach': '<p>For every center, expand outward while the characters on both sides match. Odd length palindromes grow from a letter, even length ones from the gap between two letters. Keep the longest stretch seen. Checking every substring would be O(n³).</p>',
     'time': 'O(n²)', 'space': 'O(1)'},
    {'id': 'group-anagrams', 'lv': 'h', 'title': 'Group anagrams together', 'code': 'p_group_anagrams',
     'statement': '<p>Given a list of words, group the words that are anagrams of each other. Keep the groups in the order their first word appears.</p>',
     'example': 'Input: ["eat", "tea", "tan", "ate", "nat", "bat"]\nOutput:\neat tea ate\ntan nat\nbat',
     'hint': 'Anagrams become identical when you sort their letters. Use that as a key in a hash map.',
     'approach': '<p>For each word, sort its letters to get a key such as "aet". A hash map from key to list collects each family. An insertion ordered map keeps the groups in first appearance order.</p>',
     'time': 'O(n · k log k) for n words of length k', 'space': 'O(n · k)'},
    {'id': 'min-window', 'lv': 'x', 'title': 'Minimum window substring', 'code': 'p_min_window',
     'statement': '<p>Given strings s and t, return the shortest substring of s that contains every character of t, counting repeats. Return an empty string if there is none.</p>',
     'example': 'Input: s = "ADOBECODEBANC", t = "ABC"  →  "BANC"',
     'hint': 'Grow a window on the right until it contains everything, then shrink it from the left while it still does.',
     'approach': '<p>Keep a count of what is still needed and a number <code>missing</code>. Moving <code>hi</code> right adds a character. When <code>missing</code> hits 0 the window is valid, so record it and move <code>lo</code> right until it stops being valid. Each index enters and leaves the window once.</p>',
     'time': 'O(|s| + |t|)', 'space': 'O(alphabet)'},
    {'id': 'edit-distance', 'lv': 'x', 'title': 'Edit distance', 'code': 'p_edit_distance',
     'statement': '<p>Find the fewest single character insertions, deletions and replacements that turn word a into word b.</p>',
     'example': 'Input: "cat", "cut"     →  1   (replace a with u)\nInput: "horse", "ros"   →  3   (horse → rorse → rose → ros)',
     'hint': 'Let d[i][j] be the answer for the first i letters of a and the first j letters of b. Look at the last letters.',
     'approach': '<p>If the last letters match, d[i][j] = d[i − 1][j − 1]. Otherwise it is 1 plus the best of deleting (d[i − 1][j]), inserting (d[i][j − 1]) or replacing (d[i − 1][j − 1]). The first row and column are 0, 1, 2, … because turning a prefix into an empty word needs that many deletions.</p>',
     'time': 'O(n · m)', 'space': 'O(n · m), or O(m) keeping two rows'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What is the index of the last character in a string of length 8?', 'o': ['8', '7', '9', '1'], 'a': 1, 'hint': 'Indexes start at 0.', 'why': 'Indexes run from 0 to length − 1, so the last one is <span class="eq">8 − 1 = 7</span>'},
    {'lv': 'e', 'q': 'What does it mean that strings are immutable?', 'o': ['They cannot be printed', 'Once created, their characters cannot change', 'They are stored on disk', 'They can only hold letters'], 'a': 1, 'hint': 'Think about what upper() returns.', 'why': 'Methods such as upper() or replace() return a new string. The original never changes.'},
    {'lv': 'e', 'q': 'What does this print?', 'code': 's = "hello"\nprint(s[1:4])', 'o': ['hel', 'ell', 'ello', 'llo'], 'a': 1, 'hint': 'The end index is not included.', 'why': 'Slice 1:4 takes indexes 1, 2 and 3: e, l, l.'},
    {'lv': 'e', 'q': 'How long does it take to read the character at index i?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(i²)'], 'a': 0, 'hint': 'A string is stored like an array.', 'why': 'The position of character i is calculated directly, so it is one step.'},
    {'lv': 'm', 'q': 'Building a string with s += piece inside a loop of n steps costs about…', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], 'a': 3, 'hint': 'Each += copies everything built so far.', 'why': 'The copies add up to 1 + 2 + … + n, which is about n²/2. Joining once is O(n).'},
    {'lv': 'm', 'q': 'In Java, which correctly checks whether two strings hold the same characters?', 'o': ['a == b', 'a.equals(b)', 'a = b', 'a.compareTo(b) == 1'], 'a': 1, 'hint': 'One of them compares references.', 'why': '== checks whether both variables point at the same object. equals() compares the characters.'},
    {'lv': 'm', 'q': 'Using 26 counters to check anagrams needs how much extra space?', 'o': ['O(1)', 'O(n)', 'O(n log n)', 'O(26n)'], 'a': 0, 'hint': 'Does 26 grow with the word?', 'why': 'The number of counters is fixed at 26 no matter how long the words are, so the space is constant.'},
    {'lv': 'm', 'q': 'Which comes first in dictionary order by character code?', 'o': ['"apple"', '"Zebra"', 'They are equal', 'It depends on length'], 'a': 1, 'hint': 'Compare the codes of A to Z and a to z.', 'why': 'Capital Z has code 90 and small a has code 97, so "Zebra" is smaller.'},
    {'lv': 'h', 'q': 'What is the prefix table (lps) of the pattern "aabaa"?', 'o': ['[0, 1, 0, 1, 2]', '[0, 0, 1, 2, 3]', '[0, 1, 2, 0, 1]', '[1, 1, 0, 1, 1]'], 'a': 0, 'hint': 'For each prefix, find the longest proper prefix that is also a suffix.', 'why': '"a" → 0, "aa" → 1, "aab" → 0, "aaba" → 1 ("a"), "aabaa" → 2 ("aa").'},
    {'lv': 'h', 'q': 'Why is the sliding window for the longest unique substring O(n)?', 'o': ['It sorts the string first', 'Both ends of the window only move forward', 'It uses binary search', 'It skips half the string'], 'a': 1, 'hint': 'Count how many times each end can move.', 'why': 'start and end each move at most n times in total, so the work is at most 2n steps.'},
    {'lv': 'h', 'q': 'What does this print?', 'code': 'const s = "😀";\nconsole.log(s.length);', 'o': ['1', '2', '4', 'undefined'], 'a': 1, 'hint': 'JavaScript counts UTF-16 units.', 'why': 'An emoji outside the basic plane is stored as two UTF-16 units, so length is 2. Python would say 1.'},
    {'lv': 'h', 'q': 'The naive pattern search on text "aaaaaaab" with pattern "aab" is slow because…', 'o': ['The text has no spaces', 'Most alignments match for a while and then fail', 'The pattern is too short', 'It must sort the text'], 'a': 1, 'hint': 'Count comparisons at each alignment.', 'why': 'Each alignment compares "aa" successfully before failing on "b", and the naive search throws that knowledge away.'},
    {'lv': 'x', 'q': 'What is the worst case time of KMP for a text of length n and pattern of length m?', 'o': ['O(n · m)', 'O(n + m)', 'O(n log m)', 'O(m²)'], 'a': 1, 'hint': 'The table costs O(m) and the text pointer never moves back.', 'why': 'Building lps is O(m), and the scan is O(n) because every fallback is paid for by an earlier step forward.'},
    {'lv': 'x', 'q': 'Why must Rabin and Karp compare characters after the fingerprints match?', 'o': ['To find the next window', 'Different windows can have the same fingerprint', 'Fingerprints change every run', 'It is not needed'], 'a': 1, 'hint': 'Many strings map into only M fingerprints.', 'why': 'A collision gives equal fingerprints for different text, so the match must be confirmed.'},
    {'lv': 'x', 'q': 'What is the edit distance between "sunday" and "saturday"?', 'o': ['2', '3', '4', '5'], 'a': 1, 'hint': 'Insert two letters, then fix one.', 'why': 'Insert a and t after s (s<b>at</b>unday), then replace n with r: saturday. That is 3 edits, and no shorter way exists.'},
    {'lv': 'x', 'q': 'Expanding around every center to find the longest palindrome costs…', 'o': ['O(n)', 'O(n log n)', 'O(n²)', 'O(n³)'], 'a': 2, 'hint': 'There are about 2n centers and each can expand up to n/2 times.', 'why': '2n − 1 centers times up to n/2 expansions is O(n²). Manacher\'s algorithm brings it down to O(n).'},
]

CALC = [
    {'lv': 'e', 'q': 'What is the code of the letter g, if a is 97?', 'ans': '103', 'hint': 'Count from a.', 'steps': ['g is the 7th letter, so it is 6 after a.', '<span class="eq">97 + 6 = 103</span>']},
    {'lv': 'e', 'q': 'How many characters does s[3:9] contain?', 'ans': '6', 'hint': 'End minus start.', 'steps': ['The slice runs from index 3 up to, but not including, 9.', '<span class="eq">9 − 3 = 6</span>']},
    {'lv': 'm', 'q': 'Building a 1,000 character string with += copies about how many characters in total? (Use n(n + 1)/2.)', 'ans': '500500', 'alt': ['500,500'], 'hint': 'Each += copies the whole string so far.', 'steps': ['The copies are 1 + 2 + … + 1000.', '<span class="eq">1000 × 1001 / 2 = 500,500</span>', 'join would copy only 1,000 characters.']},
    {'lv': 'm', 'q': 'How many substrings (contiguous, non empty) does a string of length 10 have?', 'ans': '55', 'hint': 'Choose a start and an end with start ≤ end.', 'steps': ['A substring is fixed by its start and end positions.', '<span class="eq">n(n + 1) / 2 = 10 × 11 / 2 = 55</span>']},
    {'lv': 'h', 'q': 'The naive search compares text "aaaaaaab" (n = 8) with pattern "aab" (m = 3). How many alignments does it try?', 'ans': '6', 'hint': 'The pattern can start at positions 0 to n − m.', 'steps': ['Possible starts are 0, 1, …, n − m.', '<span class="eq">n − m + 1 = 8 − 3 + 1 = 6</span>']},
    {'lv': 'h', 'q': 'What is lps[5] for the pattern "abcabc"?', 'ans': '3', 'hint': 'Look at the whole pattern "abcabc".', 'steps': ['The proper prefixes of "abcabc" that are also suffixes are "abc".', 'Its length is <span class="eq">3</span>']},
    {'lv': 'x', 'q': 'With B = 10 and M = 101, the window "12" has hash 12. What is the hash of the next window "23"? (next = ((h − 1·10) · 10 + 3) mod 101)', 'ans': '23', 'hint': 'Remove the leading 1, shift, add 3.', 'steps': ['<span class="eq">(12 − 1 × 10) = 2</span>', '<span class="eq">2 × 10 + 3 = 23</span>', '<span class="eq">23 mod 101 = 23</span>']},
    {'lv': 'x', 'q': 'How many cells does the edit distance table fill for words of length 6 and 7?', 'ans': '56', 'hint': 'The table has one extra row and column.', 'steps': ['The table is (6 + 1) by (7 + 1).', '<span class="eq">7 × 8 = 56</span>']},
]

# ---------------------------------------------------------------- animations for this page
VIZ_JS = r'''
(() => {
  const { esc, $, shell, seg, wireSeg, Player, cell } = VIZ.kit;
  const W = VIZ.widgets;
  const col = (ch, cls, top, bot) => `<div class="vz-sc"><small>${esc(top)}</small>${cell(ch === ' ' ? '␣' : ch, cls)}<em>${esc(bot)}</em></div>`;

  W.strmem = el => {
    const b = shell(el, 'Inside a string: boxes, indexes and codes', 'Type anything. Every character gets a box and an index, and you can see the number the computer really stores.');
    b.innerHTML = `<div class="vz-row"><label class="vz-sl">Text <input type="text" class="vz-in" maxlength="14" value="Hi café 😀"></label>${seg('enc', [['code', 'Code point'], ['utf8', 'UTF-8 bytes'], ['utf16', 'UTF-16 units']], 'code')}</div><div class="vz-scroll"><div class="vz-cells vz-strip"></div></div><div class="vz-msg" aria-live="polite"></div>`;
    const inp = $('.vz-in', b);
    let enc = 'code';
    const te = new TextEncoder();
    function draw() {
      const chars = Array.from(inp.value);
      let bytes = 0, units = 0;
      $('.vz-strip', b).innerHTML = chars.map((ch, i) => {
        const cp = ch.codePointAt(0), u8 = te.encode(ch), u16 = ch.length;
        bytes += u8.length; units += u16;
        const bot = enc === 'code' ? String(cp) : enc === 'utf8' ? Array.from(u8).map(x => x.toString(16).padStart(2, '0')).join(' ') : Array.from({ length: u16 }, (_, k) => ch.charCodeAt(k).toString(16)).join(' ');
        const cls = u8.length > 1 ? (enc === 'code' ? 'sel' : 'mv') : '';
        return col(ch, cls, i, bot);
      }).join('') || '<span class="vz-note">Type something above.</span>';
      $('.vz-msg', b).innerHTML = `<b>${chars.length}</b> characters, <b>${bytes}</b> bytes in UTF-8 and <b>${units}</b> UTF-16 units. ` + (bytes > chars.length ? 'Coloured boxes need more than one byte. That is why <code>length</code> in Java and JavaScript can differ from what you see.' : 'Plain English text uses exactly one byte per character in UTF-8.');
    }
    inp.addEventListener('input', draw);
    wireSeg(b, 'enc', v => { enc = v; draw(); });
    draw();
  };

  W.concat = el => {
    const b = shell(el, 'Why += in a loop gets slow', 'Each += copies the whole string built so far. join or StringBuilder copies every character once. Slide n and compare the work.');
    b.innerHTML = `<div class="vz-row"><label class="vz-sl">Pieces n <input type="range" min="2" max="40" value="12" data-n> <b data-nv>12</b></label></div><div class="vz-cbars"></div><div class="vz-msg" aria-live="polite"></div>`;
    const s = $('[data-n]', b), v = $('[data-nv]', b);
    function draw() {
      const n = +s.value, slow = n * (n + 1) / 2, fast = n;
      v.textContent = n;
      const W2 = 100 / slow;
      $('.vz-cbars', b).innerHTML = `<div class="vz-cb"><span>s += piece</span><div><i class="bad" style="width:100%"></i></div><b>${slow} copies</b></div><div class="vz-cb"><span>join once</span><div><i class="ok" style="width:${Math.max(2, fast * W2)}%"></i></div><b>${fast} copies</b></div>`;
      $('.vz-msg', b).innerHTML = `With ${n} one character pieces, += copies 1 + 2 + … + ${n} = <b>${slow}</b> characters. join copies <b>${fast}</b>. The gap is ${(slow / fast).toFixed(1)} times, and it keeps growing with n.`;
    }
    s.addEventListener('input', draw);
    draw();
  };

  W.palin = el => {
    const b = shell(el, 'Two pointers check a palindrome', 'i starts on the left and j on the right. Spaces and punctuation are skipped, letters are compared ignoring case.');
    b.innerHTML = `<div class="vz-row">${seg('w', [['Race car', 'Race car'], ['No lemon, no melon', 'No lemon, no melon'], ['Hello', 'Hello']], 'Race car')}</div><div class="vz-scroll"><div class="vz-cells vz-strip"></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let s = 'Race car', steps = [];
    const P = Player($('.vz-p', b), show, 700);
    const ok = c => /[A-Za-z0-9]/.test(c);
    function setup() {
      steps = [];
      let i = 0, j = s.length - 1;
      const matched = new Set(), skipped = new Set();
      const snap = (msg, extra) => steps.push({ i, j, matched: new Set(matched), skipped: new Set(skipped), msg, ...extra });
      snap('Start with i at the first character and j at the last.');
      while (i < j) {
        if (!ok(s[i])) { skipped.add(i); i++; snap(`s[${i - 1}] is not a letter, so i moves right.`); }
        else if (!ok(s[j])) { skipped.add(j); j--; snap(`s[${j + 1}] is not a letter, so j moves left.`); }
        else if (s[i].toLowerCase() !== s[j].toLowerCase()) { snap(`"${s[i]}" and "${s[j]}" differ. <b>Not a palindrome.</b>`, { bad: true }); return P.load(steps.length); }
        else { matched.add(i); matched.add(j); const a = s[i], c = s[j]; i++; j--; snap(`"${a}" matches "${c}". Move both pointers inward.`); }
      }
      snap('The pointers met without a mismatch. <b>It is a palindrome.</b>', { done: true });
      P.load(steps.length);
    }
    function show(k) {
      const st = steps[k];
      $('.vz-strip', b).innerHTML = [...s].map((ch, x) => {
        let cls = st.matched.has(x) ? 'ok' : st.skipped.has(x) ? 'dim' : '';
        if (x === st.i || x === st.j) cls = st.bad ? 'bad' : st.done ? cls : 'hl';
        const lab = x === st.i && x === st.j ? 'i j' : x === st.i ? 'i' : x === st.j ? 'j' : '';
        return col(ch, cls, x, lab);
      }).join('');
      $('.vz-msg', b).innerHTML = st.msg;
    }
    wireSeg(b, 'w', v => { s = v; setup(); });
    setup();
  };

  W.window = el => {
    const b = shell(el, 'Sliding window: longest stretch without a repeat', 'The green boxes are the window. end moves right every step, start jumps only when a character repeats.');
    b.innerHTML = `<div class="vz-row">${seg('w', [['abcabcbb', 'abcabcbb'], ['pwwkew', 'pwwkew'], ['dvdfab', 'dvdfab']], 'abcabcbb')}</div><div class="vz-scroll"><div class="vz-cells vz-strip"></div></div><div class="vz-note vz-seen"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let s = 'abcabcbb', steps = [];
    const P = Player($('.vz-p', b), show, 800);
    function setup() {
      steps = [{ start: 0, end: -1, best: 0, bs: 0, last: {}, msg: 'The window starts empty.' }];
      const last = {};
      let start = 0, best = 0, bs = 0;
      for (let end = 0; end < s.length; end++) {
        const ch = s[end];
        let msg = `Add "${ch}" at index ${end}.`;
        if (ch in last && last[ch] >= start) { msg += ` It was already in the window at ${last[ch]}, so start jumps to ${last[ch] + 1}.`; start = last[ch] + 1; }
        last[ch] = end;
        if (end - start + 1 > best) { best = end - start + 1; bs = start; msg += ` New best length <b>${best}</b>.`; }
        steps.push({ start, end, best, bs, last: { ...last }, msg });
      }
      steps.push({ start: -1, end: -2, best, bs, last: { ...last }, msg: `Done. The longest stretch is "<b>${s.slice(bs, bs + best)}</b>" with length ${best}.`, fin: true });
      P.load(steps.length);
    }
    function show(k) {
      const st = steps[k];
      $('.vz-strip', b).innerHTML = [...s].map((ch, x) => {
        let cls = '';
        if (st.fin) cls = x >= st.bs && x < st.bs + st.best ? 'ok' : 'dim';
        else if (x >= st.start && x <= st.end) cls = x === st.end ? 'hl' : 'win';
        else if (x < st.start) cls = 'dim';
        const lab = !st.fin && x === st.start && x === st.end ? 'start end' : !st.fin && x === st.start ? 'start' : !st.fin && x === st.end ? 'end' : '';
        return col(ch, cls, x, lab);
      }).join('');
      $('.vz-seen', b).innerHTML = 'Last seen: ' + (Object.entries(st.last).map(([c, x]) => `<code>${esc(c)}→${x}</code>`).join(' ') || 'nothing yet');
      $('.vz-msg', b).innerHTML = st.msg;
    }
    wireSeg(b, 'w', v => { s = v; setup(); });
    setup();
  };

  W.match = el => {
    const b = shell(el, 'Naive search versus KMP', 'Watch the pattern slide along the text. The naive search goes back after every mismatch, KMP uses the prefix table and never moves back in the text.');
    b.innerHTML = `<div class="vz-row">${seg('m', [['naive', '🐢 Naive'], ['kmp', '🐇 KMP']], 'naive')}</div><div class="vz-scroll"><div class="vz-mt"></div></div><div class="vz-note vz-lps"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const T = 'abababcababc', Pt = 'ababc';
    const lps = (() => { const l = [0]; let k = 0; for (let i = 1; i < Pt.length; i++) { while (k && Pt[i] !== Pt[k]) k = l[k - 1]; if (Pt[i] === Pt[k]) k++; l.push(k); } return l; })();
    let mode = 'naive', steps = [];
    const P = Player($('.vz-p', b), show, 600);
    function setup() {
      steps = [];
      let cmp = 0;
      const found = [];
      if (mode === 'naive') {
        for (let s = 0; s + Pt.length <= T.length; s++) {
          let j = 0;
          while (j < Pt.length) {
            cmp++;
            const eq = T[s + j] === Pt[j];
            steps.push({ s, j, eq, cmp, found: [...found], msg: `Compare text[${s + j}] "${T[s + j]}" with pattern[${j}] "${Pt[j]}": ${eq ? 'match' : 'mismatch, shift the pattern by one and start over'}.` });
            if (!eq) break;
            j++;
          }
          if (j === Pt.length) { found.push(s); steps.push({ s, j: -1, cmp, found: [...found], msg: `Full match at index <b>${s}</b>.` }); }
        }
      } else {
        let k = 0;
        for (let i = 0; i < T.length; i++) {
          while (k > 0 && T[i] !== Pt[k]) {
            cmp++;
            steps.push({ s: i - k, j: k, eq: false, cmp, found: [...found], msg: `text[${i}] "${T[i]}" differs from pattern[${k}] "${Pt[k]}". lps[${k - 1}] = ${lps[k - 1]}, so slide the pattern and keep ${lps[k - 1]} matched characters.` });
            k = lps[k - 1];
          }
          cmp++;
          const eq = T[i] === Pt[k];
          steps.push({ s: i - k, j: k, eq, cmp, found: [...found], msg: `Compare text[${i}] "${T[i]}" with pattern[${k}] "${Pt[k]}": ${eq ? 'match' : 'mismatch, move on in the text'}.` });
          if (eq) k++;
          if (k === Pt.length) { found.push(i - k + 1); steps.push({ s: i - k + 1, j: -1, cmp, found: [...found], msg: `Full match at index <b>${i - k + 1}</b>. Continue with k = lps[${k - 1}] = ${lps[k - 1]}.` }); k = lps[k - 1]; }
        }
      }
      steps.push({ s: -1, j: -1, cmp, found: [...found], msg: `Finished with <b>${cmp} comparisons</b>. Matches start at ${found.join(' and ')}.`, fin: true });
      P.load(steps.length);
    }
    function show(k) {
      const st = steps[k];
      const row1 = [...T].map((ch, x) => {
        let cls = st.found.some(f => x >= f && x < f + Pt.length) ? 'ok' : '';
        if (!st.fin && st.j >= 0 && x === st.s + st.j) cls = st.eq ? 'hl' : 'bad';
        return col(ch, cls, x, '');
      }).join('');
      const row2 = st.fin ? '' : [...T].map((_, x) => {
        const pj = x - st.s;
        if (pj < 0 || pj >= Pt.length) return '<div class="vz-sc"><small></small><div class="vz-cell empty"></div><em></em></div>';
        let cls = st.j === -1 ? 'ok' : pj < st.j ? 'win' : pj === st.j ? (st.eq ? 'hl' : 'bad') : '';
        return col(Pt[pj], cls, '', pj);
      }).join('');
      $('.vz-mt', b).innerHTML = `<div class="vz-cells vz-strip">${row1}</div><div class="vz-cells vz-strip">${row2}</div>`;
      $('.vz-lps', b).innerHTML = `Pattern "${Pt}", prefix table lps = [${lps.join(', ')}] · comparisons so far: <b>${st.cmp}</b>`;
      $('.vz-msg', b).innerHTML = st.msg;
    }
    wireSeg(b, 'm', v => { mode = v; setup(); });
    setup();
  };
})();
'''

CSS = r'''
.vz-in{font:inherit; font-family:var(--font-mono); font-size:15px; padding:6px 10px; border-radius:10px; border:1.5px solid var(--line); background:var(--surface); color:var(--ink); width:200px}
.vz-strip{flex-wrap:nowrap; gap:3px; padding:4px 2px 2px}
.vz-sc{display:flex; flex-direction:column; align-items:center; gap:2px; min-width:36px}
.vz-sc small{font-size:10.5px; color:var(--ink2); font-weight:700; font-family:var(--font-mono); min-height:14px}
.vz-sc em{font-style:normal; font-size:10.5px; color:var(--accent-deep); font-weight:800; font-family:var(--font-mono); min-height:14px; white-space:nowrap}
.vz-sc .vz-cell{min-width:34px}
.vz-mt .vz-strip + .vz-strip{margin-top:2px}
.vz-cb{display:grid; grid-template-columns:110px 1fr 110px; gap:10px; align-items:center; margin:8px 0; font-weight:800; font-size:14px}
.vz-cb div{height:22px; border-radius:8px; background:var(--surface2); border:1px solid var(--line); overflow:hidden}
.vz-cb i{display:block; height:100%; transition:width .3s}
.vz-cb i.bad{background:var(--red)} .vz-cb i.ok{background:var(--green)}
.vz-cb b{font-family:var(--font-mono); font-size:13px}
'''

T = {
    'slug': 'strings', 'title': 'Strings', 'short': 'Strings', 'emoji': '🔤', 'topic': 'strings', 'prefix': 'dsas',
    'module': ('🧱', 'Core building blocks'),
    'lead': 'Names, messages, web pages and DNA are all strings. This page shows what a string is underneath, why it never changes in place, and the scanning tricks that turn slow string code into fast code: two pointers, counting, sliding windows, KMP and rolling hashes.',
    'desc': 'Strings in DSA: characters and encodings, immutability and fast building, operation costs, two pointers, frequency counting, sliding windows, KMP pattern matching and Rabin Karp rolling hashes, with code in Python, JavaScript and Java.',
    'minutes': 14,
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'practice': PRACTICE, 'quiz': QUIZ, 'calc': CALC,
    'viz': VIZ_JS, 'css': CSS,
    'prev': ('arrays', 'array-adventure', '📦 Arrays'),
    'next': ('linked-lists', 'linked-lists', '🔗 Linked lists'),
}
