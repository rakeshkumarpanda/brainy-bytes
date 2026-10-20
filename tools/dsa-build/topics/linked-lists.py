# Linked lists: nodes and references, insertion and deletion, doubly and circular lists,
# reversal, fast and slow pointers, merging, and when to choose a list over an array.

CODES = {}


def C(key, py, js, java):
    CODES[key] = {'py': py, 'js': js, 'java': java}


# helpers repeated at the top of most programs, so every program runs on its own
PY_NODE = r'''
class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next


def build(values):
    head = None
    for v in reversed(values):
        head = Node(v, head)
    return head


def show(head):
    parts = []
    while head is not None:
        parts.append(str(head.val))
        head = head.next
    return " -> ".join(parts) if parts else "(empty)"
'''
JS_NODE = r'''
class Node {
  constructor(val, next = null) {
    this.val = val;
    this.next = next;
  }
}

function build(values) {
  let head = null;
  for (let i = values.length - 1; i >= 0; i--) head = new Node(values[i], head);
  return head;
}

function show(head) {
  const parts = [];
  for (let n = head; n !== null; n = n.next) parts.push(n.val);
  return parts.length ? parts.join(" -> ") : "(empty)";
}
'''
JAVA_NODE = r'''
    static class Node {
        int val;
        Node next;
        Node(int val, Node next) { this.val = val; this.next = next; }
    }

    static Node build(int... values) {
        Node head = null;
        for (int i = values.length - 1; i >= 0; i--) head = new Node(values[i], head);
        return head;
    }

    static String show(Node head) {
        StringBuilder sb = new StringBuilder();
        for (Node n = head; n != null; n = n.next) {
            if (sb.length() > 0) sb.append(" -> ");
            sb.append(n.val);
        }
        return sb.length() > 0 ? sb.toString() : "(empty)";
    }
'''


def jv(name, body, imports=''):
    return f'{imports}public class {name} {{{JAVA_NODE}\n{body}}}\n'


# ---------------------------------------------------------------- lesson programs
C('ll_build', py=r'''
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None          # the reference to the next node, None at the end


# three separate nodes, linked by hand: 7 -> 3 -> 9
a = Node(7)
b = Node(3)
c = Node(9)
a.next = b
b.next = c
head = a

# walk from the head, counting as we go
count = 0
node = head
while node is not None:
    print("visit", node.val)
    count += 1
    node = node.next
print("length", count)
''', js=r'''
class Node {
  constructor(val) {
    this.val = val;
    this.next = null;            // the reference to the next node, null at the end
  }
}

// three separate nodes, linked by hand: 7 -> 3 -> 9
const a = new Node(7);
const b = new Node(3);
const c = new Node(9);
a.next = b;
b.next = c;
const head = a;

// walk from the head, counting as we go
let count = 0;
let node = head;
while (node !== null) {
  console.log("visit", node.val);
  count++;
  node = node.next;
}
console.log("length", count);
''', java=r'''
public class BuildList {
    static class Node {
        int val;
        Node next;                 // the reference to the next node, null at the end
        Node(int val) { this.val = val; }
    }

    public static void main(String[] args) {
        // three separate nodes, linked by hand: 7 -> 3 -> 9
        Node a = new Node(7);
        Node b = new Node(3);
        Node c = new Node(9);
        a.next = b;
        b.next = c;
        Node head = a;

        // walk from the head, counting as we go
        int count = 0;
        Node node = head;
        while (node != null) {
            System.out.println("visit " + node.val);
            count++;
            node = node.next;
        }
        System.out.println("length " + count);
    }
}
''')

C('ll_insert_delete', py=PY_NODE + r'''

def insert_after(node, val):
    node.next = Node(val, node.next)   # new node points where node pointed, node points at it


def delete_value(head, val):
    dummy = Node(0, head)              # a fake node before the head removes the special case
    prev = dummy
    while prev.next is not None:
        if prev.next.val == val:
            prev.next = prev.next.next # skip over the node, it is now unreachable
            break
        prev = prev.next
    return dummy.next


head = build([10, 20, 40])
head = Node(5, head)                   # insert at the head: O(1)
print(show(head))
insert_after(head.next.next, 30)       # after the node holding 20
print(show(head))
head = delete_value(head, 5)           # deleting the head works the same way
head = delete_value(head, 30)
print(show(head))
''', js=JS_NODE + r'''
function insertAfter(node, val) {
  node.next = new Node(val, node.next);  // new node points where node pointed, node points at it
}

function deleteValue(head, val) {
  const dummy = new Node(0, head);       // a fake node before the head removes the special case
  let prev = dummy;
  while (prev.next !== null) {
    if (prev.next.val === val) {
      prev.next = prev.next.next;        // skip over the node, it is now unreachable
      break;
    }
    prev = prev.next;
  }
  return dummy.next;
}

let head = build([10, 20, 40]);
head = new Node(5, head);                // insert at the head: O(1)
console.log(show(head));
insertAfter(head.next.next, 30);         // after the node holding 20
console.log(show(head));
head = deleteValue(head, 5);             // deleting the head works the same way
head = deleteValue(head, 30);
console.log(show(head));
''', java=jv('InsertDelete', r'''
    static void insertAfter(Node node, int val) {
        node.next = new Node(val, node.next);  // new node points where node pointed, node points at it
    }

    static Node deleteValue(Node head, int val) {
        Node dummy = new Node(0, head);        // a fake node before the head removes the special case
        Node prev = dummy;
        while (prev.next != null) {
            if (prev.next.val == val) {
                prev.next = prev.next.next;    // skip over the node, it is now unreachable
                break;
            }
            prev = prev.next;
        }
        return dummy.next;
    }

    public static void main(String[] args) {
        Node head = build(10, 20, 40);
        head = new Node(5, head);              // insert at the head: O(1)
        System.out.println(show(head));
        insertAfter(head.next.next, 30);       // after the node holding 20
        System.out.println(show(head));
        head = deleteValue(head, 5);           // deleting the head works the same way
        head = deleteValue(head, 30);
        System.out.println(show(head));
    }
'''))

C('dll', py=r'''
class DNode:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, val):
        node = DNode(val)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        return node

    def remove(self, node):            # O(1): the node knows both neighbours
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

    def forward(self):
        out, n = [], self.head
        while n is not None:
            out.append(str(n.val))
            n = n.next
        return " <-> ".join(out)

    def backward(self):
        out, n = [], self.tail
        while n is not None:
            out.append(str(n.val))
            n = n.prev
        return " <-> ".join(out)


d = DoublyLinkedList()
d.append(1)
middle = d.append(2)
d.append(3)
print(d.forward())
d.remove(middle)
print(d.forward())
print(d.backward())
''', js=r'''
class DNode {
  constructor(val) {
    this.val = val;
    this.prev = null;
    this.next = null;
  }
}

class DoublyLinkedList {
  constructor() {
    this.head = null;
    this.tail = null;
  }

  append(val) {
    const node = new DNode(val);
    if (this.tail === null) {
      this.head = this.tail = node;
    } else {
      node.prev = this.tail;
      this.tail.next = node;
      this.tail = node;
    }
    return node;
  }

  remove(node) {                     // O(1): the node knows both neighbours
    if (node.prev !== null) node.prev.next = node.next;
    else this.head = node.next;
    if (node.next !== null) node.next.prev = node.prev;
    else this.tail = node.prev;
  }

  forward() {
    const out = [];
    for (let n = this.head; n !== null; n = n.next) out.push(n.val);
    return out.join(" <-> ");
  }

  backward() {
    const out = [];
    for (let n = this.tail; n !== null; n = n.prev) out.push(n.val);
    return out.join(" <-> ");
  }
}

const d = new DoublyLinkedList();
d.append(1);
const middle = d.append(2);
d.append(3);
console.log(d.forward());
d.remove(middle);
console.log(d.forward());
console.log(d.backward());
''', java=r'''
public class Doubly {
    static class DNode {
        int val;
        DNode prev, next;
        DNode(int val) { this.val = val; }
    }

    static class DoublyLinkedList {
        DNode head, tail;

        DNode append(int val) {
            DNode node = new DNode(val);
            if (tail == null) {
                head = tail = node;
            } else {
                node.prev = tail;
                tail.next = node;
                tail = node;
            }
            return node;
        }

        void remove(DNode node) {         // O(1): the node knows both neighbours
            if (node.prev != null) node.prev.next = node.next;
            else head = node.next;
            if (node.next != null) node.next.prev = node.prev;
            else tail = node.prev;
        }

        String forward() {
            StringBuilder sb = new StringBuilder();
            for (DNode n = head; n != null; n = n.next) sb.append(sb.length() > 0 ? " <-> " : "").append(n.val);
            return sb.toString();
        }

        String backward() {
            StringBuilder sb = new StringBuilder();
            for (DNode n = tail; n != null; n = n.prev) sb.append(sb.length() > 0 ? " <-> " : "").append(n.val);
            return sb.toString();
        }
    }

    public static void main(String[] args) {
        DoublyLinkedList d = new DoublyLinkedList();
        d.append(1);
        DNode middle = d.append(2);
        d.append(3);
        System.out.println(d.forward());
        d.remove(middle);
        System.out.println(d.forward());
        System.out.println(d.backward());
    }
}
''')

C('ll_reverse', py=PY_NODE + r'''

def reverse(head):
    prev = None
    cur = head
    while cur is not None:
        nxt = cur.next       # remember the rest of the list
        cur.next = prev      # turn this arrow around
        prev = cur           # step both pointers forward
        cur = nxt
    return prev              # the old tail is the new head


def reverse_recursive(head):
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head    # the node after head now points back at head
    head.next = None
    return new_head


head = build([1, 2, 3, 4])
head = reverse(head)
print(show(head))
head = reverse_recursive(head)
print(show(head))
''', js=JS_NODE + r'''
function reverse(head) {
  let prev = null;
  let cur = head;
  while (cur !== null) {
    const nxt = cur.next;  // remember the rest of the list
    cur.next = prev;       // turn this arrow around
    prev = cur;            // step both pointers forward
    cur = nxt;
  }
  return prev;             // the old tail is the new head
}

function reverseRecursive(head) {
  if (head === null || head.next === null) return head;
  const newHead = reverseRecursive(head.next);
  head.next.next = head;   // the node after head now points back at head
  head.next = null;
  return newHead;
}

let head = build([1, 2, 3, 4]);
head = reverse(head);
console.log(show(head));
head = reverseRecursive(head);
console.log(show(head));
''', java=jv('Reverse', r'''
    static Node reverse(Node head) {
        Node prev = null;
        Node cur = head;
        while (cur != null) {
            Node nxt = cur.next;   // remember the rest of the list
            cur.next = prev;       // turn this arrow around
            prev = cur;            // step both pointers forward
            cur = nxt;
        }
        return prev;               // the old tail is the new head
    }

    static Node reverseRecursive(Node head) {
        if (head == null || head.next == null) return head;
        Node newHead = reverseRecursive(head.next);
        head.next.next = head;     // the node after head now points back at head
        head.next = null;
        return newHead;
    }

    public static void main(String[] args) {
        Node head = build(1, 2, 3, 4);
        head = reverse(head);
        System.out.println(show(head));
        head = reverseRecursive(head);
        System.out.println(show(head));
    }
'''))

C('ll_fast_slow', py=PY_NODE + r'''

def middle(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next         # one step
        fast = fast.next.next    # two steps
    return slow


def has_cycle(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:         # the hare lapped the tortoise
            return True
    return False


head = build([1, 2, 3, 4, 5])
print("middle", middle(head).val)
print("cycle" if has_cycle(head) else "no cycle")
head.next.next.next.next.next = head.next.next   # 5 now points back at 3
print("cycle" if has_cycle(head) else "no cycle")
''', js=JS_NODE + r'''
function middle(head) {
  let slow = head, fast = head;
  while (fast !== null && fast.next !== null) {
    slow = slow.next;          // one step
    fast = fast.next.next;     // two steps
  }
  return slow;
}

function hasCycle(head) {
  let slow = head, fast = head;
  while (fast !== null && fast.next !== null) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow === fast) return true;  // the hare lapped the tortoise
  }
  return false;
}

const head = build([1, 2, 3, 4, 5]);
console.log("middle", middle(head).val);
console.log(hasCycle(head) ? "cycle" : "no cycle");
head.next.next.next.next.next = head.next.next;   // 5 now points back at 3
console.log(hasCycle(head) ? "cycle" : "no cycle");
''', java=jv('FastSlow', r'''
    static Node middle(Node head) {
        Node slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;          // one step
            fast = fast.next.next;     // two steps
        }
        return slow;
    }

    static boolean hasCycle(Node head) {
        Node slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;  // the hare lapped the tortoise
        }
        return false;
    }

    public static void main(String[] args) {
        Node head = build(1, 2, 3, 4, 5);
        System.out.println("middle " + middle(head).val);
        System.out.println(hasCycle(head) ? "cycle" : "no cycle");
        head.next.next.next.next.next = head.next.next;   // 5 now points back at 3
        System.out.println(hasCycle(head) ? "cycle" : "no cycle");
    }
'''))

C('ll_merge', py=PY_NODE + r'''

def merge(a, b):
    dummy = Node(0)
    tail = dummy                  # last node of the merged list so far
    while a is not None and b is not None:
        if a.val <= b.val:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a if a is not None else b   # one list is empty, attach the rest of the other
    return dummy.next


print(show(merge(build([1, 4, 7]), build([2, 3, 8, 9]))))
''', js=JS_NODE + r'''
function merge(a, b) {
  const dummy = new Node(0);
  let tail = dummy;               // last node of the merged list so far
  while (a !== null && b !== null) {
    if (a.val <= b.val) {
      tail.next = a;
      a = a.next;
    } else {
      tail.next = b;
      b = b.next;
    }
    tail = tail.next;
  }
  tail.next = a !== null ? a : b; // one list is empty, attach the rest of the other
  return dummy.next;
}

console.log(show(merge(build([1, 4, 7]), build([2, 3, 8, 9]))));
''', java=jv('Merge', r'''
    static Node merge(Node a, Node b) {
        Node dummy = new Node(0, null);
        Node tail = dummy;               // last node of the merged list so far
        while (a != null && b != null) {
            if (a.val <= b.val) {
                tail.next = a;
                a = a.next;
            } else {
                tail.next = b;
                b = b.next;
            }
            tail = tail.next;
        }
        tail.next = a != null ? a : b;   // one list is empty, attach the rest of the other
        return dummy.next;
    }

    public static void main(String[] args) {
        System.out.println(show(merge(build(1, 4, 7), build(2, 3, 8, 9))));
    }
'''))

C('ll_library', py=r'''
from collections import deque

# Python has no built in linked list class. deque is a doubly linked list of blocks:
# O(1) at both ends.
d = deque([2, 3])
d.appendleft(1)
d.append(4)
print(list(d))
print(d.popleft(), d.pop())
print(list(d))
''', js=r'''
// JavaScript has no built in linked list. Arrays are dynamic arrays:
// push and pop at the end are O(1), unshift and shift at the front are O(n).
const d = [2, 3];
d.unshift(1);
d.push(4);
console.log("[" + d.join(", ") + "]");
console.log(d.shift(), d.pop());
console.log("[" + d.join(", ") + "]");
''', java=r'''
import java.util.LinkedList;

public class Library {
    public static void main(String[] args) {
        // java.util.LinkedList is a doubly linked list: O(1) at both ends
        LinkedList<Integer> d = new LinkedList<>();
        d.add(2);
        d.add(3);
        d.addFirst(1);
        d.addLast(4);
        System.out.println(d);
        int first = d.removeFirst();
        int last = d.removeLast();
        System.out.println(first + " " + last);
        System.out.println(d);
    }
}
''')

# ---------------------------------------------------------------- practice solutions
C('p_remove_val', py=PY_NODE + r'''

def remove_all(head, val):
    dummy = Node(0, head)
    prev = dummy
    while prev.next is not None:
        if prev.next.val == val:
            prev.next = prev.next.next   # unlink, but stay put to check the new next
        else:
            prev = prev.next
    return dummy.next


print(show(remove_all(build([6, 1, 6, 2, 6]), 6)))
print(show(remove_all(build([7, 7]), 7)))
''', js=JS_NODE + r'''
function removeAll(head, val) {
  const dummy = new Node(0, head);
  let prev = dummy;
  while (prev.next !== null) {
    if (prev.next.val === val) prev.next = prev.next.next;  // unlink, but stay put to check the new next
    else prev = prev.next;
  }
  return dummy.next;
}

console.log(show(removeAll(build([6, 1, 6, 2, 6]), 6)));
console.log(show(removeAll(build([7, 7]), 7)));
''', java=jv('RemoveAll', r'''
    static Node removeAll(Node head, int val) {
        Node dummy = new Node(0, head);
        Node prev = dummy;
        while (prev.next != null) {
            if (prev.next.val == val) prev.next = prev.next.next;  // unlink, but stay put to check the new next
            else prev = prev.next;
        }
        return dummy.next;
    }

    public static void main(String[] args) {
        System.out.println(show(removeAll(build(6, 1, 6, 2, 6), 6)));
        System.out.println(show(removeAll(build(7, 7), 7)));
    }
'''))

C('p_dedup_sorted', py=PY_NODE + r'''

def dedup(head):
    cur = head
    while cur is not None and cur.next is not None:
        if cur.next.val == cur.val:
            cur.next = cur.next.next     # equal neighbour, skip it
        else:
            cur = cur.next
    return head


print(show(dedup(build([1, 1, 2, 3, 3, 3]))))
''', js=JS_NODE + r'''
function dedup(head) {
  let cur = head;
  while (cur !== null && cur.next !== null) {
    if (cur.next.val === cur.val) cur.next = cur.next.next;  // equal neighbour, skip it
    else cur = cur.next;
  }
  return head;
}

console.log(show(dedup(build([1, 1, 2, 3, 3, 3]))));
''', java=jv('Dedup', r'''
    static Node dedup(Node head) {
        Node cur = head;
        while (cur != null && cur.next != null) {
            if (cur.next.val == cur.val) cur.next = cur.next.next;  // equal neighbour, skip it
            else cur = cur.next;
        }
        return head;
    }

    public static void main(String[] args) {
        System.out.println(show(dedup(build(1, 1, 2, 3, 3, 3))));
    }
'''))

C('p_nth_from_end', py=PY_NODE + r'''

def remove_nth_from_end(head, n):
    dummy = Node(0, head)
    lead = trail = dummy
    for _ in range(n + 1):
        lead = lead.next             # open a gap of n nodes
    while lead is not None:
        lead = lead.next
        trail = trail.next
    trail.next = trail.next.next     # trail sits just before the target
    return dummy.next


print(show(remove_nth_from_end(build([1, 2, 3, 4, 5]), 2)))
print(show(remove_nth_from_end(build([1]), 1)))
''', js=JS_NODE + r'''
function removeNthFromEnd(head, n) {
  const dummy = new Node(0, head);
  let lead = dummy, trail = dummy;
  for (let k = 0; k <= n; k++) lead = lead.next;  // open a gap of n nodes
  while (lead !== null) {
    lead = lead.next;
    trail = trail.next;
  }
  trail.next = trail.next.next;                   // trail sits just before the target
  return dummy.next;
}

console.log(show(removeNthFromEnd(build([1, 2, 3, 4, 5]), 2)));
console.log(show(removeNthFromEnd(build([1]), 1)));
''', java=jv('NthFromEnd', r'''
    static Node removeNthFromEnd(Node head, int n) {
        Node dummy = new Node(0, head);
        Node lead = dummy, trail = dummy;
        for (int k = 0; k <= n; k++) lead = lead.next;   // open a gap of n nodes
        while (lead != null) {
            lead = lead.next;
            trail = trail.next;
        }
        trail.next = trail.next.next;                    // trail sits just before the target
        return dummy.next;
    }

    public static void main(String[] args) {
        System.out.println(show(removeNthFromEnd(build(1, 2, 3, 4, 5), 2)));
        System.out.println(show(removeNthFromEnd(build(1), 1)));
    }
'''))

C('p_ll_palindrome', py=PY_NODE + r'''

def is_palindrome(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    prev = None                      # reverse the second half in place
    while slow is not None:
        nxt = slow.next
        slow.next = prev
        prev = slow
        slow = nxt
    left, right = head, prev
    while right is not None:         # compare the halves from the outside in
        if left.val != right.val:
            return False
        left = left.next
        right = right.next
    return True


print("yes" if is_palindrome(build([1, 2, 2, 1])) else "no")
print("yes" if is_palindrome(build([1, 2, 3])) else "no")
''', js=JS_NODE + r'''
function isPalindrome(head) {
  let slow = head, fast = head;
  while (fast !== null && fast.next !== null) {
    slow = slow.next;
    fast = fast.next.next;
  }
  let prev = null;                 // reverse the second half in place
  while (slow !== null) {
    const nxt = slow.next;
    slow.next = prev;
    prev = slow;
    slow = nxt;
  }
  let left = head, right = prev;
  while (right !== null) {         // compare the halves from the outside in
    if (left.val !== right.val) return false;
    left = left.next;
    right = right.next;
  }
  return true;
}

console.log(isPalindrome(build([1, 2, 2, 1])) ? "yes" : "no");
console.log(isPalindrome(build([1, 2, 3])) ? "yes" : "no");
''', java=jv('ListPalindrome', r'''
    static boolean isPalindrome(Node head) {
        Node slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        Node prev = null;                // reverse the second half in place
        while (slow != null) {
            Node nxt = slow.next;
            slow.next = prev;
            prev = slow;
            slow = nxt;
        }
        Node left = head, right = prev;
        while (right != null) {          // compare the halves from the outside in
            if (left.val != right.val) return false;
            left = left.next;
            right = right.next;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(isPalindrome(build(1, 2, 2, 1)) ? "yes" : "no");
        System.out.println(isPalindrome(build(1, 2, 3)) ? "yes" : "no");
    }
'''))

C('p_add_two', py=PY_NODE + r'''

def add(a, b):
    dummy = Node(0)
    tail = dummy
    carry = 0
    while a is not None or b is not None or carry:
        total = carry
        if a is not None:
            total += a.val
            a = a.next
        if b is not None:
            total += b.val
            b = b.next
        carry = total // 10
        tail.next = Node(total % 10)
        tail = tail.next
    return dummy.next


# digits are stored backwards: 342 is 2 -> 4 -> 3
print(show(add(build([2, 4, 3]), build([5, 6, 4]))))
print(show(add(build([9, 9]), build([1]))))
''', js=JS_NODE + r'''
function add(a, b) {
  const dummy = new Node(0);
  let tail = dummy;
  let carry = 0;
  while (a !== null || b !== null || carry) {
    let total = carry;
    if (a !== null) { total += a.val; a = a.next; }
    if (b !== null) { total += b.val; b = b.next; }
    carry = Math.floor(total / 10);
    tail.next = new Node(total % 10);
    tail = tail.next;
  }
  return dummy.next;
}

// digits are stored backwards: 342 is 2 -> 4 -> 3
console.log(show(add(build([2, 4, 3]), build([5, 6, 4]))));
console.log(show(add(build([9, 9]), build([1]))));
''', java=jv('AddTwo', r'''
    static Node add(Node a, Node b) {
        Node dummy = new Node(0, null);
        Node tail = dummy;
        int carry = 0;
        while (a != null || b != null || carry != 0) {
            int total = carry;
            if (a != null) { total += a.val; a = a.next; }
            if (b != null) { total += b.val; b = b.next; }
            carry = total / 10;
            tail.next = new Node(total % 10, null);
            tail = tail.next;
        }
        return dummy.next;
    }

    public static void main(String[] args) {
        // digits are stored backwards: 342 is 2 -> 4 -> 3
        System.out.println(show(add(build(2, 4, 3), build(5, 6, 4))));
        System.out.println(show(add(build(9, 9), build(1))));
    }
'''))

C('p_intersection', py=PY_NODE + r'''

def intersection(a, b):
    p, q = a, b
    while p is not q:
        # each pointer walks its own list, then the other one: both travel len(a) + len(b)
        p = p.next if p is not None else b
        q = q.next if q is not None else a
    return p


shared = build([8, 4, 5])
a = Node(4, Node(1, shared))
b = Node(5, Node(6, Node(1, shared)))
meet = intersection(a, b)
print("meet at", meet.val if meet is not None else "none")
print("meet at", "none" if intersection(build([1, 2]), build([3])) is None else "somewhere")
''', js=JS_NODE + r'''
function intersection(a, b) {
  let p = a, q = b;
  while (p !== q) {
    // each pointer walks its own list, then the other one: both travel len(a) + len(b)
    p = p !== null ? p.next : b;
    q = q !== null ? q.next : a;
  }
  return p;
}

const shared = build([8, 4, 5]);
const a = new Node(4, new Node(1, shared));
const b = new Node(5, new Node(6, new Node(1, shared)));
const meet = intersection(a, b);
console.log("meet at", meet !== null ? meet.val : "none");
console.log("meet at", intersection(build([1, 2]), build([3])) === null ? "none" : "somewhere");
''', java=jv('Intersection', r'''
    static Node intersection(Node a, Node b) {
        Node p = a, q = b;
        while (p != q) {
            // each pointer walks its own list, then the other one: both travel len(a) + len(b)
            p = p != null ? p.next : b;
            q = q != null ? q.next : a;
        }
        return p;
    }

    public static void main(String[] args) {
        Node shared = build(8, 4, 5);
        Node a = new Node(4, new Node(1, shared));
        Node b = new Node(5, new Node(6, new Node(1, shared)));
        Node meet = intersection(a, b);
        System.out.println("meet at " + (meet != null ? String.valueOf(meet.val) : "none"));
        System.out.println("meet at " + (intersection(build(1, 2), build(3)) == null ? "none" : "somewhere"));
    }
'''))

C('p_reverse_k', py=PY_NODE + r'''

def reverse_k_group(head, k):
    dummy = Node(0, head)
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):               # is there a full group of k ahead?
            kth = kth.next
            if kth is None:
                return dummy.next
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:     # reverse the k nodes, the last one points at group_next
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        first = group_prev.next          # the old first node is now last in the group
        group_prev.next = kth
        group_prev = first


print(show(reverse_k_group(build([1, 2, 3, 4, 5]), 2)))
print(show(reverse_k_group(build([1, 2, 3, 4, 5]), 3)))
''', js=JS_NODE + r'''
function reverseKGroup(head, k) {
  const dummy = new Node(0, head);
  let groupPrev = dummy;
  for (;;) {
    let kth = groupPrev;
    for (let i = 0; i < k; i++) {      // is there a full group of k ahead?
      kth = kth.next;
      if (kth === null) return dummy.next;
    }
    const groupNext = kth.next;
    let prev = groupNext, cur = groupPrev.next;
    while (cur !== groupNext) {        // reverse the k nodes, the last one points at groupNext
      const nxt = cur.next;
      cur.next = prev;
      prev = cur;
      cur = nxt;
    }
    const first = groupPrev.next;      // the old first node is now last in the group
    groupPrev.next = kth;
    groupPrev = first;
  }
}

console.log(show(reverseKGroup(build([1, 2, 3, 4, 5]), 2)));
console.log(show(reverseKGroup(build([1, 2, 3, 4, 5]), 3)));
''', java=jv('ReverseK', r'''
    static Node reverseKGroup(Node head, int k) {
        Node dummy = new Node(0, head);
        Node groupPrev = dummy;
        while (true) {
            Node kth = groupPrev;
            for (int i = 0; i < k; i++) {       // is there a full group of k ahead?
                kth = kth.next;
                if (kth == null) return dummy.next;
            }
            Node groupNext = kth.next;
            Node prev = groupNext, cur = groupPrev.next;
            while (cur != groupNext) {          // reverse the k nodes, the last one points at groupNext
                Node nxt = cur.next;
                cur.next = prev;
                prev = cur;
                cur = nxt;
            }
            Node first = groupPrev.next;        // the old first node is now last in the group
            groupPrev.next = kth;
            groupPrev = first;
        }
    }

    public static void main(String[] args) {
        System.out.println(show(reverseKGroup(build(1, 2, 3, 4, 5), 2)));
        System.out.println(show(reverseKGroup(build(1, 2, 3, 4, 5), 3)));
    }
'''))

C('p_lru', py=r'''
class DNode:
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}                       # key -> node, for O(1) lookup
        self.head, self.tail = DNode(), DNode()   # sentinels: most recent after head
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, n):
        n.prev.next, n.next.prev = n.next, n.prev

    def _push_front(self, n):
        n.prev, n.next = self.head, self.head.next
        self.head.next.prev = n
        self.head.next = n

    def get(self, key):
        if key not in self.map:
            return -1
        n = self.map[key]
        self._unlink(n)
        self._push_front(n)                 # used just now, so it becomes the most recent
        return n.val

    def put(self, key, val):
        if key in self.map:
            self._unlink(self.map[key])
        n = DNode(key, val)
        self.map[key] = n
        self._push_front(n)
        if len(self.map) > self.cap:
            old = self.tail.prev            # least recently used sits before the tail
            self._unlink(old)
            del self.map[old.key]


c = LRUCache(2)
c.put(1, 10)
c.put(2, 20)
print(c.get(1))
c.put(3, 30)       # evicts key 2
print(c.get(2))
print(c.get(3))
''', js=r'''
class DNode {
  constructor(key = 0, val = 0) {
    this.key = key;
    this.val = val;
    this.prev = null;
    this.next = null;
  }
}

class LRUCache {
  constructor(capacity) {
    this.cap = capacity;
    this.map = new Map();                // key -> node, for O(1) lookup
    this.head = new DNode();             // sentinels: most recent after head
    this.tail = new DNode();
    this.head.next = this.tail;
    this.tail.prev = this.head;
  }

  unlink(n) {
    n.prev.next = n.next;
    n.next.prev = n.prev;
  }

  pushFront(n) {
    n.prev = this.head;
    n.next = this.head.next;
    this.head.next.prev = n;
    this.head.next = n;
  }

  get(key) {
    if (!this.map.has(key)) return -1;
    const n = this.map.get(key);
    this.unlink(n);
    this.pushFront(n);                   // used just now, so it becomes the most recent
    return n.val;
  }

  put(key, val) {
    if (this.map.has(key)) this.unlink(this.map.get(key));
    const n = new DNode(key, val);
    this.map.set(key, n);
    this.pushFront(n);
    if (this.map.size > this.cap) {
      const old = this.tail.prev;        // least recently used sits before the tail
      this.unlink(old);
      this.map.delete(old.key);
    }
  }
}

const c = new LRUCache(2);
c.put(1, 10);
c.put(2, 20);
console.log(c.get(1));
c.put(3, 30);      // evicts key 2
console.log(c.get(2));
console.log(c.get(3));
''', java=r'''
import java.util.HashMap;
import java.util.Map;

public class Lru {
    static class DNode {
        int key, val;
        DNode prev, next;
        DNode(int key, int val) { this.key = key; this.val = val; }
    }

    static class LRUCache {
        int cap;
        Map<Integer, DNode> map = new HashMap<>();   // key -> node, for O(1) lookup
        DNode head = new DNode(0, 0), tail = new DNode(0, 0);  // sentinels: most recent after head

        LRUCache(int capacity) {
            cap = capacity;
            head.next = tail;
            tail.prev = head;
        }

        void unlink(DNode n) {
            n.prev.next = n.next;
            n.next.prev = n.prev;
        }

        void pushFront(DNode n) {
            n.prev = head;
            n.next = head.next;
            head.next.prev = n;
            head.next = n;
        }

        int get(int key) {
            if (!map.containsKey(key)) return -1;
            DNode n = map.get(key);
            unlink(n);
            pushFront(n);                        // used just now, so it becomes the most recent
            return n.val;
        }

        void put(int key, int val) {
            if (map.containsKey(key)) unlink(map.get(key));
            DNode n = new DNode(key, val);
            map.put(key, n);
            pushFront(n);
            if (map.size() > cap) {
                DNode old = tail.prev;           // least recently used sits before the tail
                unlink(old);
                map.remove(old.key);
            }
        }
    }

    public static void main(String[] args) {
        LRUCache c = new LRUCache(2);
        c.put(1, 10);
        c.put(2, 20);
        System.out.println(c.get(1));
        c.put(3, 30);      // evicts key 2
        System.out.println(c.get(2));
        System.out.println(c.get(3));
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    dict(id='what-is', emoji='🔗', title='Nodes holding hands', html='''
<p>A <b>linked list</b> is a chain of <b>nodes</b>. Each node holds a value and a <b>reference</b> (a pointer) to the next node. The list itself only remembers the first node, called the <b>head</b>. The last node points at nothing: <code>None</code> in Python, <code>null</code> in JavaScript and Java.</p>
<div class="grid2">
<div class="box"><h4>📦 Array</h4><p>One block of memory, boxes side by side. Box i is found by arithmetic, so reading by position is <b>O(1)</b>. Inserting at the front shifts everything, <b>O(n)</b>.</p></div>
<div class="box"><h4>🔗 Linked list</h4><p>Nodes can live anywhere in memory, joined only by references. Reaching node i means walking i steps, <b>O(n)</b>. Inserting next to a node you already hold is <b>O(1)</b>.</p></div>
</div>
<div class="c3" data-k="ll_build" data-label="Build three nodes and walk them"></div>
<div class="rule">You can only enter a singly linked list through its head and only move forward. Lose the head and the whole list is gone.</div>
<div class="viz" data-viz="llops"></div>
'''),
    dict(id='insert-delete', emoji='✂️', title='Inserting and deleting by rewiring', html='''
<p>Nothing ever moves in a linked list. Inserting or deleting only changes a few references, which is why these operations can be O(1) once you are standing at the right place.</p>
<div class="tw"><table class="jt"><tr><th>Operation</th><th>What changes</th><th>Cost</th></tr>
<tr><td>Insert at head</td><td><code>new.next = head</code>, then <code>head = new</code></td><td class="yes">O(1)</td></tr>
<tr><td>Insert after a known node</td><td><code>new.next = node.next</code>, then <code>node.next = new</code></td><td class="yes">O(1)</td></tr>
<tr><td>Insert at tail</td><td>walk to the end first, or keep a <code>tail</code> reference</td><td>O(n), or O(1) with tail</td></tr>
<tr><td>Delete the node after prev</td><td><code>prev.next = prev.next.next</code></td><td class="yes">O(1)</td></tr>
<tr><td>Delete by value</td><td>walk to find the node before it, then unlink</td><td>O(n)</td></tr>
</table></div>
<div class="warn">Order matters. When inserting after a node, set <code>new.next</code> first. If you set <code>node.next = new</code> first, the rest of the list is lost.</div>
<h3>The dummy node trick</h3>
<p>Deleting the head is usually a special case, because no node comes before it. Put a fake <b>dummy</b> (sentinel) node in front of the head. Now every real node has a node before it, the special case disappears, and the answer is <code>dummy.next</code>.</p>
<div class="c3" data-k="ll_insert_delete" data-label="Insert at the head, insert after, delete with a dummy node"></div>
'''),
    dict(id='doubly', emoji='↔️', title='Doubly linked and circular lists', html='''
<p>A <b>doubly linked list</b> gives every node two references: <code>next</code> and <code>prev</code>. It costs one more reference per node, and in return you can walk backwards and remove a node in O(1) when you hold that node, because it knows both of its neighbours.</p>
<div class="grid2">
<div class="box"><h4>↔️ Doubly linked</h4><p>head and tail at both ends. Browser history, music playlists and text editors use it to move both ways.</p></div>
<div class="box"><h4>🔄 Circular</h4><p>The last node points back at the first instead of null. Round robin schedulers and turn based games loop through players this way.</p></div>
</div>
<div class="c3" data-k="dll" data-label="A doubly linked list with O(1) removal"></div>
<div class="tw"><table class="jt"><tr><th>Kind</th><th>References per node</th><th>Walk backwards</th><th>Remove a held node</th></tr>
<tr><td>Singly linked</td><td>1</td><td class="no">no</td><td>O(n), you must find the node before it</td></tr>
<tr><td>Doubly linked</td><td>2</td><td class="yes">yes</td><td class="yes">O(1)</td></tr>
<tr><td>Circular</td><td>1 or 2</td><td>if doubly</td><td>same as its base kind</td></tr>
</table></div>
'''),
    dict(id='reverse', emoji='🔁', title='Reversing a list in place', html='''
<p>Reversing is the classic linked list exercise, and it trains the most important habit: <b>save the next node before you change a reference</b>.</p>
<ol>
<li><code>nxt = cur.next</code> remembers the rest of the list.</li>
<li><code>cur.next = prev</code> turns one arrow around.</li>
<li><code>prev = cur</code> and <code>cur = nxt</code> step forward.</li>
</ol>
<p>When <code>cur</code> falls off the end, <code>prev</code> is the old tail and the new head. Every node is visited once, so it is <b>O(n)</b> time and <b>O(1)</b> extra space.</p>
<div class="viz" data-viz="llrev"></div>
<div class="c3" data-k="ll_reverse" data-label="Reverse iteratively, then recursively"></div>
<div class="tip">The recursive version is shorter but uses one stack frame per node, so it needs O(n) space and can overflow the call stack on a list of a million nodes.</div>
'''),
    dict(id='fast-slow', emoji='🐢', title='Fast and slow pointers', html='''
<p>Send two pointers down the list at different speeds: the tortoise moves one node per step and the hare moves two. This one idea answers several questions in a single pass with O(1) extra space.</p>
<div class="grid2">
<div class="box"><h4>🎯 Middle node</h4><p>When the hare reaches the end, the tortoise has gone half as far, so it stands in the middle.</p></div>
<div class="box"><h4>🔄 Cycle detection</h4><p>If the list loops, the hare enters the loop and eventually laps the tortoise. If it reaches null, there is no loop. This is <b>Floyd's algorithm</b>.</p></div>
</div>
<div class="viz" data-viz="floyd"></div>
<div class="c3" data-k="ll_fast_slow" data-label="Middle node and cycle detection"></div>
<p>Why must they meet? Inside the loop the hare gains exactly one node on the tortoise every step, so the gap shrinks by one until it is zero. They meet within one lap of the loop.</p>
<span class="eq">gap after each step = gap − 1   so they meet in at most (loop length) steps</span>
<div class="exam">To find where the loop <b>starts</b>, put one pointer back at the head after they meet and move both one step at a time. They meet again exactly at the start of the loop.</div>
'''),
    dict(id='merge', emoji='🤝', title='Merging two sorted lists', html='''
<p>Given two lists that are already sorted, build one sorted list by repeatedly taking the smaller front node. No new nodes are needed: we only rewire the existing ones. A dummy node again saves us from special cases at the start.</p>
<div class="viz" data-viz="llmerge"></div>
<div class="c3" data-k="ll_merge" data-label="Merge two sorted lists with a dummy node"></div>
<p>Each step moves one node into place, so merging lists of length n and m takes <b>O(n + m)</b> time and <b>O(1)</b> extra space. This is the heart of <b>merge sort</b> on linked lists, which sorts a list in O(n log n) without random access.</p>
'''),
    dict(id='when', emoji='⚖️', title='Lists versus arrays in real code', html='''
<p>On paper, linked lists win at inserting and deleting. In real programs, arrays often win anyway, because their boxes sit next to each other and the CPU cache loads many of them at once. Following references jumps around memory.</p>
<div class="tw"><table class="jt"><tr><th>Need</th><th>Better choice</th><th>Why</th></tr>
<tr><td>Read item i often</td><td>array</td><td>O(1) access by index</td></tr>
<tr><td>Add or remove at both ends</td><td>deque or linked list</td><td>O(1) at the front and the back</td></tr>
<tr><td>Remove items you already hold, very often</td><td>doubly linked list</td><td>O(1) unlink without searching</td></tr>
<tr><td>Iterate over everything fast</td><td>array</td><td>cache friendly, no pointer chasing</td></tr>
<tr><td>Least recently used cache</td><td>hash map + doubly linked list</td><td>O(1) lookup and O(1) move to front</td></tr>
</table></div>
<div class="c3" data-k="ll_library" data-label="What each language gives you"></div>
<div class="fun">Your operating system keeps lists of free memory blocks and of waiting processes as linked lists, and the undo history in many editors is a doubly linked list of changes.</div>
'''),
]

INFO = {
    'title': 'A treasure hunt of nodes',
    'panels': [
        {'s': [['e', '🗺️'], ['t', 'head → 7', {'b': 1}]], 'h': 'Start at the head', 't': 'The list only knows its first node.', 'more': 'Like a treasure hunt, each clue tells you where the next one is hidden.'},
        {'s': [['e', '🔗'], ['t', '7 → 3 → 9 → null', {'b': 1}]], 'h': 'Follow the arrows', 't': 'Every node points at the next.', 'more': 'Reaching the k-th node means walking k steps, so access is O(n).'},
        {'s': [['e', '✂️'], ['t', 'prev.next = prev.next.next', {'b': 1, 'size': 11}]], 'h': 'Rewire, never shift', 't': 'Insert and delete change references.', 'more': 'Next to a known node this is O(1), no element moves.'},
        {'s': [['e', '🐢🐇'], ['t', 'slow +1, fast +2', {'b': 1}]], 'h': 'Clever pointers', 't': 'Two speeds find middles and loops.', 'more': 'Floyd\'s tortoise and hare detect a cycle using O(1) memory.'},
    ],
    'remember': 'A linked list trades O(1) access by index for O(1) insert and delete next to a node you hold. Save the next node before you change a reference.',
}

REAL = [
    ['🎵', 'A music playlist', 'Next and previous buttons move along a doubly linked list of songs. Removing the song that is playing only rewires its two neighbours.'],
    ['🌐', 'Browser back and forward', 'Each page you visit is a node with links to the page before and after. Opening a new page from the middle cuts off the forward part.'],
    ['🚂', 'A train of carriages', 'Every carriage is hooked to the next. Adding a carriage in the middle means unhooking one coupling and hooking two, the rest of the train does not move.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome',
     'en': 'Welcome to linked lists. A linked list is a chain of nodes, each holding a value and a reference to the next node. You will learn how to build, insert, delete, reverse and merge lists, and the clever two pointer tricks that find middles and loops.',
     'hi': 'Linked lists में आपका स्वागत है। Linked list nodes की एक श्रृंखला है, हर node में एक value और अगले node का reference होता है। आप lists बनाना, insert, delete, reverse और merge करना सीखेंगे, और वे two pointer तरकीबें जो बीच का node और loop ढूँढती हैं।',
     'kn': 'Linked lists ಗೆ ಸ್ವಾಗತ. Linked list ಎಂದರೆ nodes ಗಳ ಸರಪಳಿ, ಪ್ರತಿ node ನಲ್ಲಿ ಒಂದು value ಮತ್ತು ಮುಂದಿನ node ನ reference ಇರುತ್ತದೆ. Lists ಕಟ್ಟುವುದು, insert, delete, reverse ಮತ್ತು merge ಮಾಡುವುದು, ಹಾಗೂ ಮಧ್ಯದ node ಮತ್ತು loop ಹುಡುಕುವ two pointer ತಂತ್ರಗಳನ್ನು ಕಲಿಯುತ್ತೀರಿ.',
     'or': 'Linked lists କୁ ସ୍ୱାଗତ। Linked list ହେଉଛି nodes ର ଏକ ଶୃଙ୍ଖଳ, ପ୍ରତ୍ୟେକ node ରେ ଗୋଟିଏ value ଏବଂ ପରବର୍ତ୍ତୀ node ର reference ଥାଏ। ଆପଣ lists ତିଆରି, insert, delete, reverse ଓ merge କରିବା ଶିଖିବେ, ଏବଂ ମଝି node ଓ loop ଖୋଜୁଥିବା two pointer କୌଶଳ।',
     'ar': 'مرحبًا بك في القوائم المترابطة. القائمة المترابطة سلسلة من العقد، تحمل كل عقدة قيمة ومرجعًا إلى العقدة التالية. ستتعلم بناء القوائم والإدراج والحذف والعكس والدمج، وحيل المؤشرين التي تجد المنتصف والحلقات.',
     'de': 'Willkommen bei verketteten Listen. Eine verkettete Liste ist eine Kette von Knoten, jeder mit einem Wert und einer Referenz auf den nächsten Knoten. Du lernst Listen zu bauen, einzufügen, zu löschen, umzudrehen und zu verschmelzen, und die Tricks mit zwei Zeigern, die Mitte und Schleifen finden.'},
    {'id': 'what-is', 'h': 'Nodes holding hands',
     'en': 'Each node stores a value and a reference to the next node. The list only remembers the head. Reaching the k-th node means walking k steps, but inserting next to a node you already hold takes a single step.',
     'hi': 'हर node एक value और अगले node का reference रखता है। List सिर्फ़ head को याद रखती है। k-वें node तक पहुँचने के लिए k कदम चलना पड़ता है, लेकिन जिस node पर आप हैं उसके बगल में insert करना एक कदम का काम है।',
     'kn': 'ಪ್ರತಿ node ಒಂದು value ಮತ್ತು ಮುಂದಿನ node ನ reference ಇಡುತ್ತದೆ. List ಕೇವಲ head ಅನ್ನು ನೆನಪಿಡುತ್ತದೆ. k ನೇ node ತಲುಪಲು k ಹೆಜ್ಜೆ ನಡೆಯಬೇಕು, ಆದರೆ ನೀವು ಹಿಡಿದಿರುವ node ಪಕ್ಕ insert ಮಾಡಲು ಒಂದೇ ಹೆಜ್ಜೆ.',
     'or': 'ପ୍ରତ୍ୟେକ node ଗୋଟିଏ value ଏବଂ ପରବର୍ତ୍ତୀ node ର reference ରଖେ। List କେବଳ head କୁ ମନେ ରଖେ। k ତମ node ପର୍ଯ୍ୟନ୍ତ ପହଞ୍ଚିବାକୁ k ପାଦ ଚାଲିବାକୁ ପଡ଼େ, କିନ୍ତୁ ଆପଣ ଧରିଥିବା node ପାଖରେ insert କରିବା ଗୋଟିଏ ପାଦର କାମ।',
     'ar': 'تخزن كل عقدة قيمة ومرجعًا إلى العقدة التالية. لا تتذكر القائمة إلا الرأس. للوصول إلى العقدة رقم k تمشي k خطوة، أما الإدراج بجانب عقدة تمسكها فيحتاج خطوة واحدة.',
     'de': 'Jeder Knoten speichert einen Wert und eine Referenz auf den nächsten. Die Liste merkt sich nur den Kopf. Bis zum k-ten Knoten läufst du k Schritte, aber neben einem Knoten, den du schon hast, fügst du in einem Schritt ein.'},
    {'id': 'insert-delete', 'h': 'Rewiring',
     'en': 'Nothing moves in a linked list. To insert, point the new node at the next node first, then point the previous node at the new one. To delete, make the previous node skip over the target. A dummy node in front of the head removes the special case for the first node.',
     'hi': 'Linked list में कुछ भी खिसकता नहीं। Insert करने के लिए पहले नए node को अगले node की ओर point करें, फिर पिछले node को नए node की ओर। Delete करने के लिए पिछले node को target के ऊपर से छलाँग लगवाएँ। Head के आगे एक dummy node पहले node का विशेष मामला खत्म कर देता है।',
     'kn': 'Linked list ನಲ್ಲಿ ಏನೂ ಸರಿಯುವುದಿಲ್ಲ. Insert ಮಾಡಲು ಮೊದಲು ಹೊಸ node ಅನ್ನು ಮುಂದಿನ node ಕಡೆ point ಮಾಡಿ, ನಂತರ ಹಿಂದಿನ node ಅನ್ನು ಹೊಸದರ ಕಡೆ. Delete ಮಾಡಲು ಹಿಂದಿನ node target ಅನ್ನು ದಾಟುವಂತೆ ಮಾಡಿ. Head ಮುಂದೆ ಒಂದು dummy node ಮೊದಲ node ನ ವಿಶೇಷ ಪ್ರಕರಣವನ್ನು ತೆಗೆದುಹಾಕುತ್ತದೆ.',
     'or': 'Linked list ରେ କିଛି ଘୁଞ୍ଚେ ନାହିଁ। Insert ପାଇଁ ପ୍ରଥମେ ନୂଆ node କୁ ପରବର୍ତ୍ତୀ node ଆଡ଼କୁ point କରନ୍ତୁ, ତାପରେ ପୂର୍ବ node କୁ ନୂଆ node ଆଡ଼କୁ। Delete ପାଇଁ ପୂର୍ବ node କୁ target ଡେଇଁଯିବାକୁ ଦିଅନ୍ତୁ। Head ଆଗରେ ଏକ dummy node ପ୍ରଥମ node ର ବିଶେଷ ପରିସ୍ଥିତି ହଟାଇଦିଏ।',
     'ar': 'لا شيء يتحرك في القائمة المترابطة. للإدراج وجّه العقدة الجديدة أولًا إلى التالية، ثم وجّه السابقة إلى الجديدة. وللحذف اجعل السابقة تتخطى الهدف. وعقدة وهمية أمام الرأس تلغي الحالة الخاصة بالعقدة الأولى.',
     'de': 'In einer verketteten Liste bewegt sich nichts. Zum Einfügen zeigt der neue Knoten zuerst auf den nächsten, dann zeigt der vorige auf den neuen. Zum Löschen überspringt der vorige Knoten das Ziel. Ein Dummy-Knoten vor dem Kopf beseitigt den Sonderfall für den ersten Knoten.'},
    {'id': 'doubly', 'h': 'Doubly and circular',
     'en': 'A doubly linked list gives each node a previous reference as well as a next one. You can walk backwards and remove a node you hold in a single step. In a circular list the last node points back to the first, which is handy for taking turns.',
     'hi': 'Doubly linked list में हर node के पास next के साथ previous reference भी होता है। आप पीछे चल सकते हैं और जिस node पर हैं उसे एक कदम में हटा सकते हैं। Circular list में आख़िरी node पहले की ओर point करता है, जो बारी बारी से काम करने में उपयोगी है।',
     'kn': 'Doubly linked list ನಲ್ಲಿ ಪ್ರತಿ node ಗೆ next ಜೊತೆ previous reference ಕೂಡ ಇರುತ್ತದೆ. ಹಿಂದಕ್ಕೆ ನಡೆಯಬಹುದು ಮತ್ತು ಹಿಡಿದ node ಅನ್ನು ಒಂದೇ ಹೆಜ್ಜೆಯಲ್ಲಿ ತೆಗೆಯಬಹುದು. Circular list ನಲ್ಲಿ ಕೊನೆಯ node ಮೊದಲನೆಯದರ ಕಡೆ point ಮಾಡುತ್ತದೆ, ಸರದಿ ಕೆಲಸಕ್ಕೆ ಉಪಯುಕ್ತ.',
     'or': 'Doubly linked list ରେ ପ୍ରତ୍ୟେକ node ପାଖରେ next ସହ previous reference ବି ଥାଏ। ଆପଣ ପଛକୁ ଚାଲିପାରିବେ ଏବଂ ଧରିଥିବା node କୁ ଗୋଟିଏ ପାଦରେ ହଟାଇପାରିବେ। Circular list ରେ ଶେଷ node ପ୍ରଥମ ଆଡ଼କୁ point କରେ, ଯାହା ପାଳି ପାଳି କାମ ପାଇଁ ଉପଯୋଗୀ।',
     'ar': 'القائمة المزدوجة تعطي كل عقدة مرجعًا للسابقة إلى جانب التالية. يمكنك المشي إلى الخلف وحذف عقدة تمسكها في خطوة واحدة. وفي القائمة الدائرية تشير العقدة الأخيرة إلى الأولى، وهذا مفيد لتبادل الأدوار.',
     'de': 'Eine doppelt verkettete Liste gibt jedem Knoten zusätzlich eine Referenz auf den vorigen. Du kannst rückwärts laufen und einen Knoten, den du hast, in einem Schritt entfernen. In einer Ringliste zeigt der letzte Knoten zurück auf den ersten, praktisch für Reihum-Abläufe.'},
    {'id': 'reverse', 'h': 'Reversing',
     'en': 'To reverse a list, walk it with three pointers. Save the next node, turn the current arrow back to the previous node, then step both forward. When you fall off the end, the previous pointer is the new head. It takes linear time and constant extra space.',
     'hi': 'List उलटने के लिए तीन pointers के साथ चलें। अगला node सँभाल लें, मौजूदा तीर को पिछले node की ओर मोड़ें, फिर दोनों को आगे बढ़ाएँ। अंत पार करते ही previous pointer नया head होता है। इसमें linear समय और constant अतिरिक्त जगह लगती है।',
     'kn': 'List ತಿರುಗಿಸಲು ಮೂರು pointers ಜೊತೆ ನಡೆಯಿರಿ. ಮುಂದಿನ node ಉಳಿಸಿ, ಈಗಿನ ಬಾಣವನ್ನು ಹಿಂದಿನ node ಕಡೆ ತಿರುಗಿಸಿ, ನಂತರ ಎರಡನ್ನೂ ಮುಂದೆ ಸರಿಸಿ. ಕೊನೆ ದಾಟಿದಾಗ previous pointer ಹೊಸ head. ಇದು linear ಸಮಯ ಮತ್ತು constant ಹೆಚ್ಚುವರಿ ಜಾಗ ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ.',
     'or': 'List ଓଲଟାଇବାକୁ ତିନୋଟି pointers ସହ ଚାଲନ୍ତୁ। ପରବର୍ତ୍ତୀ node ସାଇତି ରଖନ୍ତୁ, ବର୍ତ୍ତମାନର ତୀରକୁ ପୂର୍ବ node ଆଡ଼କୁ ବୁଲାନ୍ତୁ, ତାପରେ ଦୁହିଁଙ୍କୁ ଆଗକୁ ନିଅନ୍ତୁ। ଶେଷ ପାର ହେଲେ previous pointer ନୂଆ head। ଏହା linear ସମୟ ଓ constant ଅତିରିକ୍ତ ସ୍ଥାନ ନିଏ।',
     'ar': 'لعكس القائمة امشِ بثلاثة مؤشرات. احفظ العقدة التالية، واقلب السهم الحالي نحو العقدة السابقة، ثم تقدّم بالاثنين. عندما تتجاوز النهاية يصبح المؤشر السابق هو الرأس الجديد. يستغرق ذلك وقتًا خطيًا ومساحة إضافية ثابتة.',
     'de': 'Zum Umdrehen läufst du mit drei Zeigern durch die Liste. Merke dir den nächsten Knoten, dreh den aktuellen Pfeil zum vorigen Knoten um und geh mit beiden weiter. Fällst du hinten heraus, ist der vorige Zeiger der neue Kopf. Das kostet lineare Zeit und konstanten Zusatzspeicher.'},
    {'id': 'fast-slow', 'h': 'Fast and slow pointers',
     'en': 'Move a slow pointer one node at a time and a fast pointer two. When the fast one reaches the end, the slow one is in the middle. If the list has a loop, the fast pointer laps the slow one and they meet. This is Floyd\'s tortoise and hare.',
     'hi': 'एक धीमे pointer को एक node और तेज़ pointer को दो node आगे बढ़ाएँ। जब तेज़ वाला अंत तक पहुँचे, धीमा बीच में होता है। अगर list में loop है, तो तेज़ pointer धीमे को पकड़ लेता है और दोनों मिलते हैं। यह Floyd का tortoise and hare है।',
     'kn': 'ನಿಧಾನ pointer ಅನ್ನು ಒಂದು node ಮತ್ತು ವೇಗದ pointer ಅನ್ನು ಎರಡು node ಸರಿಸಿ. ವೇಗದದು ಕೊನೆ ತಲುಪಿದಾಗ ನಿಧಾನದ್ದು ಮಧ್ಯದಲ್ಲಿರುತ್ತದೆ. List ನಲ್ಲಿ loop ಇದ್ದರೆ ವೇಗದ pointer ನಿಧಾನದ್ದನ್ನು ಹಿಡಿಯುತ್ತದೆ ಮತ್ತು ಅವು ಭೇಟಿಯಾಗುತ್ತವೆ. ಇದು Floyd ನ tortoise and hare.',
     'or': 'ଧୀର pointer କୁ ଗୋଟିଏ node ଏବଂ ଦ୍ରୁତ pointer କୁ ଦୁଇ node ଆଗକୁ ନିଅନ୍ତୁ। ଦ୍ରୁତଟି ଶେଷରେ ପହଞ୍ଚିଲେ ଧୀରଟି ମଝିରେ ଥାଏ। List ରେ loop ଥିଲେ ଦ୍ରୁତ pointer ଧୀରକୁ ଧରିପକାଏ ଏବଂ ସେମାନେ ମିଳନ୍ତି। ଏହା Floyd ଙ୍କ tortoise and hare।',
     'ar': 'حرّك مؤشرًا بطيئًا عقدة واحدة ومؤشرًا سريعًا عقدتين. عندما يصل السريع إلى النهاية يكون البطيء في المنتصف. وإذا كانت في القائمة حلقة فإن السريع يلحق بالبطيء ويلتقيان. هذه هي السلحفاة والأرنب لفلويد.',
     'de': 'Bewege einen langsamen Zeiger um einen Knoten und einen schnellen um zwei. Erreicht der schnelle das Ende, steht der langsame in der Mitte. Hat die Liste eine Schleife, überrundet der schnelle den langsamen und sie treffen sich. Das ist Floyds Hase und Igel.'},
    {'id': 'merge', 'h': 'Merging',
     'en': 'To merge two sorted lists, keep taking the smaller front node and attach it to the end of the result. A dummy node gives you a place to start. No new nodes are created, and the work is the total length of both lists.',
     'hi': 'दो sorted lists को merge करने के लिए बार बार छोटा आगे वाला node लें और परिणाम के अंत में जोड़ें। एक dummy node शुरुआत की जगह देता है। कोई नया node नहीं बनता, और काम दोनों lists की कुल लंबाई जितना है।',
     'kn': 'ಎರಡು sorted lists merge ಮಾಡಲು ಪದೇ ಪದೇ ಚಿಕ್ಕ ಮುಂದಿನ node ತೆಗೆದು ಫಲಿತಾಂಶದ ಕೊನೆಗೆ ಸೇರಿಸಿ. Dummy node ಪ್ರಾರಂಭದ ಸ್ಥಳ ಕೊಡುತ್ತದೆ. ಹೊಸ node ಗಳು ಬೇಕಿಲ್ಲ, ಕೆಲಸ ಎರಡೂ lists ನ ಒಟ್ಟು ಉದ್ದದಷ್ಟು.',
     'or': 'ଦୁଇଟି sorted lists merge କରିବାକୁ ବାରମ୍ବାର ଛୋଟ ଆଗ node ନେଇ ଫଳର ଶେଷରେ ଯୋଡ଼ନ୍ତୁ। Dummy node ଆରମ୍ଭ ପାଇଁ ସ୍ଥାନ ଦିଏ। କୌଣସି ନୂଆ node ତିଆରି ହୁଏ ନାହିଁ, ଏବଂ କାମ ଦୁଇ lists ର ମୋଟ ଲମ୍ବ ଯେତିକି।',
     'ar': 'لدمج قائمتين مرتبتين خذ في كل مرة العقدة الأمامية الأصغر وألحقها بنهاية النتيجة. العقدة الوهمية تعطيك نقطة بداية. لا تُنشأ عقد جديدة، والعمل يساوي مجموع طولي القائمتين.',
     'de': 'Um zwei sortierte Listen zu verschmelzen, nimmst du immer den kleineren vorderen Knoten und hängst ihn ans Ergebnis. Ein Dummy-Knoten gibt dir einen Startpunkt. Es entstehen keine neuen Knoten, und die Arbeit entspricht der Gesamtlänge beider Listen.'},
    {'id': 'when', 'h': 'Lists versus arrays',
     'en': 'Arrays are usually faster in practice because their items sit side by side in memory and the processor cache loves that. Choose a linked list when you insert and delete next to known nodes very often, or combine one with a hash map, as in an LRU cache.',
     'hi': 'व्यवहार में arrays अक्सर तेज़ होते हैं क्योंकि उनके items memory में साथ साथ होते हैं और processor cache को यह पसंद है। Linked list तब चुनें जब आप जाने पहचाने nodes के पास बहुत बार insert और delete करते हैं, या उसे hash map के साथ जोड़ें, जैसे LRU cache में।',
     'kn': 'ವ್ಯವಹಾರದಲ್ಲಿ arrays ಸಾಮಾನ್ಯವಾಗಿ ವೇಗವಾಗಿರುತ್ತವೆ, ಏಕೆಂದರೆ ಅವುಗಳ items memory ಯಲ್ಲಿ ಪಕ್ಕಪಕ್ಕ ಇರುತ್ತವೆ ಮತ್ತು processor cache ಗೆ ಅದು ಇಷ್ಟ. ಗೊತ್ತಿರುವ nodes ಪಕ್ಕ ಆಗಾಗ insert ಮತ್ತು delete ಮಾಡುವಾಗ linked list ಆರಿಸಿ, ಅಥವಾ LRU cache ನಂತೆ hash map ಜೊತೆ ಸೇರಿಸಿ.',
     'or': 'ବ୍ୟବହାରରେ arrays ପ୍ରାୟତଃ ଦ୍ରୁତ, କାରଣ ସେମାନଙ୍କ items memory ରେ ପାଖାପାଖି ଥାଏ ଏବଂ processor cache ତାହା ପସନ୍ଦ କରେ। ଜଣାଶୁଣା nodes ପାଖରେ ବାରମ୍ବାର insert ଓ delete କଲେ linked list ବାଛନ୍ତୁ, କିମ୍ବା LRU cache ଭଳି hash map ସହ ମିଶାନ୍ତୁ।',
     'ar': 'المصفوفات أسرع عادة في الواقع لأن عناصرها متجاورة في الذاكرة وذاكرة المعالج المؤقتة تحب ذلك. اختر القائمة المترابطة عندما تدرج وتحذف كثيرًا بجانب عقد معروفة، أو ادمجها مع جدول تجزئة كما في ذاكرة LRU المؤقتة.',
     'de': 'Arrays sind in der Praxis meist schneller, weil ihre Elemente im Speicher nebeneinander liegen und der Prozessor-Cache das liebt. Nimm eine verkettete Liste, wenn du sehr oft neben bekannten Knoten einfügst und löschst, oder kombiniere sie mit einer Hashtabelle wie in einem LRU-Cache.'},
    {'id': 'practice', 'h': 'Practice',
     'en': 'Time to practise. Draw the boxes and arrows on paper before you code. Each problem has a hint and a full solution in Python, JavaScript and Java that you can replay line by line.',
     'hi': 'अब अभ्यास का समय है। Code लिखने से पहले काग़ज़ पर boxes और तीर बनाइए। हर सवाल के साथ एक hint और Python, JavaScript और Java में पूरा हल है, जिसे आप line by line चला सकते हैं।',
     'kn': 'ಈಗ ಅಭ್ಯಾಸದ ಸಮಯ. Code ಬರೆಯುವ ಮೊದಲು ಕಾಗದದ ಮೇಲೆ boxes ಮತ್ತು ಬಾಣಗಳನ್ನು ಬಿಡಿಸಿ. ಪ್ರತಿ ಸಮಸ್ಯೆಗೆ ಒಂದು hint ಮತ್ತು Python, JavaScript ಮತ್ತು Java ದಲ್ಲಿ line by line ನೋಡಬಹುದಾದ ಪೂರ್ಣ ಪರಿಹಾರವಿದೆ.',
     'or': 'ଏବେ ଅଭ୍ୟାସର ସମୟ। Code ଲେଖିବା ପୂର୍ବରୁ କାଗଜରେ boxes ଓ ତୀର ଆଙ୍କନ୍ତୁ। ପ୍ରତ୍ୟେକ ସମସ୍ୟା ସହ ଏକ hint ଏବଂ Python, JavaScript ଓ Java ରେ line by line ଦେଖିହେବା ଭଳି ପୂରା ସମାଧାନ ଅଛି।',
     'ar': 'حان وقت التدريب. ارسم المربعات والأسهم على الورق قبل أن تكتب الشيفرة. لكل مسألة تلميح وحل كامل بلغات بايثون وجافاسكربت وجافا يمكنك تشغيله سطرًا سطرًا.',
     'de': 'Zeit zum Üben. Zeichne Kästchen und Pfeile auf Papier, bevor du programmierst. Jede Aufgabe hat einen Hinweis und eine vollständige Lösung in Python, JavaScript und Java, die du Zeile für Zeile abspielen kannst.'},
]

PRACTICE = [
    {'id': 'remove-value', 'lv': 'e', 'title': 'Remove every node with a given value', 'code': 'p_remove_val',
     'statement': '<p>Delete every node whose value equals <code>val</code>, including nodes at the head, and return the new head.</p>',
     'example': 'Input: 6 -> 1 -> 6 -> 2 -> 6, val = 6  →  1 -> 2\nInput: 7 -> 7, val = 7                →  (empty)',
     'hint': 'A dummy node in front of the head means the head is no longer special.',
     'approach': '<p>Stand on <code>prev</code> and look at <code>prev.next</code>. If it holds the value, unlink it and stay where you are, because the new <code>prev.next</code> might also match. Otherwise step forward. Return <code>dummy.next</code>.</p>',
     'time': 'O(n)', 'space': 'O(1)'},
    {'id': 'dedup-sorted', 'lv': 'e', 'title': 'Remove duplicates from a sorted list', 'code': 'p_dedup_sorted',
     'statement': '<p>The list is sorted, so equal values sit next to each other. Keep one copy of each value.</p>',
     'example': 'Input: 1 -> 1 -> 2 -> 3 -> 3 -> 3  →  1 -> 2 -> 3',
     'hint': 'Compare each node with the one right after it.',
     'approach': '<p>While <code>cur.next</code> holds the same value as <code>cur</code>, skip it. Only move <code>cur</code> forward when the next value is different.</p>',
     'time': 'O(n)', 'space': 'O(1)'},
    {'id': 'nth-from-end', 'lv': 'm', 'title': 'Remove the n-th node from the end', 'code': 'p_nth_from_end',
     'statement': '<p>Remove the n-th node counting from the end, in one pass, and return the head.</p>',
     'example': 'Input: 1 -> 2 -> 3 -> 4 -> 5, n = 2  →  1 -> 2 -> 3 -> 5\nInput: 1, n = 1                      →  (empty)',
     'hint': 'Move one pointer n + 1 steps ahead, then move both until the leader falls off the end.',
     'approach': '<p>Start both pointers at a dummy node. After the leader is n + 1 nodes ahead, move both together. When the leader is null, the trailer stands just before the node to remove, so <code>trail.next = trail.next.next</code>.</p>',
     'time': 'O(n)', 'space': 'O(1)'},
    {'id': 'list-palindrome', 'lv': 'm', 'title': 'Is the linked list a palindrome', 'code': 'p_ll_palindrome',
     'statement': '<p>Decide whether the values read the same forwards and backwards, using O(1) extra space.</p>',
     'example': 'Input: 1 -> 2 -> 2 -> 1  →  yes\nInput: 1 -> 2 -> 3       →  no',
     'hint': 'Find the middle with fast and slow pointers, then reverse the second half.',
     'approach': '<p>The slow pointer stops at the middle. Reverse from there to the end. Now walk one pointer from the head and one from the new head of the reversed half, comparing values. A careful solution reverses the half back afterwards to leave the list unchanged.</p>',
     'time': 'O(n)', 'space': 'O(1)'},
    {'id': 'add-two', 'lv': 'h', 'title': 'Add two numbers stored as lists', 'code': 'p_add_two',
     'statement': '<p>Each list stores a number with its digits in reverse order, one digit per node. Return the sum as a list in the same form.</p>',
     'example': 'Input: 2 -> 4 -> 3 (342) and 5 -> 6 -> 4 (465)  →  7 -> 0 -> 8 (807)\nInput: 9 -> 9 (99) and 1 (1)                      →  0 -> 0 -> 1 (100)',
     'hint': 'This is column addition from school. The reversed order puts the ones digit first, which is exactly where you start adding.',
     'approach': '<p>Walk both lists together, adding the two digits and the carry. Write <code>total % 10</code> into a new node and carry <code>total / 10</code>. Keep going while either list has nodes or the carry is not zero.</p>',
     'time': 'O(max(n, m))', 'space': 'O(max(n, m)) for the answer'},
    {'id': 'intersection', 'lv': 'h', 'title': 'Where do two lists join', 'code': 'p_intersection',
     'statement': '<p>Two lists may share their tail: from some node on, they are the very same nodes. Return that first shared node, or nothing if they never join. Use O(1) extra space.</p>',
     'example': 'A: 4 -> 1 -> 8 -> 4 -> 5\nB: 5 -> 6 -> 1 -> 8 -> 4 -> 5   (8 -> 4 -> 5 is shared)\nOutput: the node holding 8',
     'hint': 'If each pointer walks its own list and then the other list, both walk the same total distance.',
     'approach': '<p>Pointer p walks A then B, pointer q walks B then A. Both travel len(A) + len(B) steps, so they line up and arrive at the first shared node together. If there is no shared node, both reach null at the same moment.</p>',
     'time': 'O(n + m)', 'space': 'O(1)'},
    {'id': 'reverse-k', 'lv': 'x', 'title': 'Reverse nodes in groups of k', 'code': 'p_reverse_k',
     'statement': '<p>Reverse the list k nodes at a time. If fewer than k nodes remain at the end, leave them as they are.</p>',
     'example': 'Input: 1 -> 2 -> 3 -> 4 -> 5, k = 2  →  2 -> 1 -> 4 -> 3 -> 5\nInput: 1 -> 2 -> 3 -> 4 -> 5, k = 3  →  3 -> 2 -> 1 -> 4 -> 5',
     'hint': 'Keep a pointer to the node just before the current group. Check that k nodes exist before reversing.',
     'approach': '<p>From <code>group_prev</code>, walk k steps to find <code>kth</code>. Reverse the group with the usual three pointer loop, starting <code>prev</code> at the node after the group so the reversed group stays attached. Then connect <code>group_prev</code> to <code>kth</code> and move <code>group_prev</code> to the old first node.</p>',
     'time': 'O(n)', 'space': 'O(1)'},
    {'id': 'lru-cache', 'lv': 'x', 'title': 'Least recently used cache', 'code': 'p_lru',
     'statement': '<p>Design a cache with a fixed capacity. <code>get(key)</code> returns the value or −1. <code>put(key, value)</code> inserts or updates. When the cache is full, it evicts the key that was used least recently. Both operations must be O(1).</p>',
     'example': 'capacity 2: put(1, 10), put(2, 20), get(1) → 10\nput(3, 30) evicts 2, get(2) → −1, get(3) → 30',
     'hint': 'A hash map finds a node in O(1). A doubly linked list moves a node to the front or removes the back in O(1).',
     'approach': '<p>Keep the nodes in a doubly linked list ordered from most recent (after the head sentinel) to least recent (before the tail sentinel), and a map from key to node. Every get or put moves the node to the front. When the size exceeds the capacity, unlink the node before the tail and delete its key from the map.</p>',
     'time': 'O(1) per operation', 'space': 'O(capacity)'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What does each node of a singly linked list hold?', 'o': ['Only a value', 'A value and a reference to the next node', 'A value and its index', 'Two values'], 'a': 1, 'hint': 'Think of the arrow.', 'why': 'A node stores its value and a reference to the next node. The index is not stored anywhere.'},
    {'lv': 'e', 'q': 'How long does it take to insert a new node at the head?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], 'a': 0, 'hint': 'How many references change?', 'why': 'Point the new node at the old head, then move head. Two changes, whatever the length.'},
    {'lv': 'e', 'q': 'What does the last node of a singly linked list point to?', 'o': ['The head', 'Itself', 'null (or None)', 'A random node'], 'a': 2, 'hint': 'There is no next node.', 'why': 'The end is marked by a null reference. In a circular list it would point back at the head instead.'},
    {'lv': 'e', 'q': 'How long does it take to read the 500th element of a linked list?', 'o': ['O(1)', 'O(log n)', 'About 500 steps, O(n)', 'It is impossible'], 'a': 2, 'hint': 'There is no arithmetic shortcut.', 'why': 'You must follow 499 references from the head. Arrays do it in one step.'},
    {'lv': 'm', 'q': 'Inserting after node p, which order of assignments is correct?', 'o': ['p.next = new, then new.next = p.next', 'new.next = p.next, then p.next = new', 'new.next = p, then p.next = new', 'Either order works'], 'a': 1, 'hint': 'Which reference would you lose?', 'why': 'Setting p.next first overwrites the only reference to the rest of the list. Set new.next first.'},
    {'lv': 'm', 'q': 'Why do many linked list solutions start with a dummy node?', 'o': ['It makes the list faster', 'It removes the special case for the head', 'It stores the length', 'It prevents cycles'], 'a': 1, 'hint': 'What is special about deleting the first node?', 'why': 'With a dummy in front, every real node has a node before it, so inserting or deleting at the head works like anywhere else.'},
    {'lv': 'm', 'q': 'What does this print?', 'code': 'head = Node(1, Node(2, Node(3)))\nhead = head.next\nprint(head.val)', 'o': ['1', '2', '3', 'None'], 'a': 1, 'hint': 'Moving head forward drops the first node.', 'why': 'head now refers to the second node, which holds 2.'},
    {'lv': 'm', 'q': 'Removing a node you already hold is O(1) in which kind of list?', 'o': ['Singly linked', 'Doubly linked', 'Both', 'Neither'], 'a': 1, 'hint': 'You need the node before it.', 'why': 'A doubly linked node knows its previous node, so it can unlink itself. A singly linked list must search for the previous node.'},
    {'lv': 'h', 'q': 'In Floyd\'s algorithm, why can the fast pointer not jump over the slow one forever inside a loop?', 'o': ['It moves randomly', 'The gap between them shrinks by exactly one each step', 'The loop gets shorter', 'The slow one stops'], 'a': 1, 'hint': 'Fast moves 2, slow moves 1.', 'why': 'Each step the fast pointer gains one node, so the gap goes 5, 4, 3, 2, 1, 0. It cannot skip zero.'},
    {'lv': 'h', 'q': 'What is the extra space of reversing a list recursively?', 'o': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'], 'a': 2, 'hint': 'Count the stack frames.', 'why': 'Each node waits in its own call frame until the deeper calls return, so n frames are alive at the deepest point.'},
    {'lv': 'h', 'q': 'Merging sorted lists of lengths 4 and 6 makes at most how many comparisons?', 'o': ['4', '6', '9', '24'], 'a': 2, 'hint': 'Each comparison places one node, and the last node needs no comparison.', 'why': 'At most n + m − 1 = 9 comparisons. When one list runs out, the rest is attached without comparing.'},
    {'lv': 'h', 'q': 'Why are arrays often faster than linked lists for a simple loop over all items?', 'o': ['Arrays use less code', 'Array items sit together, so the CPU cache loads many at once', 'Linked lists cannot be looped over', 'Arrays are sorted'], 'a': 1, 'hint': 'Think about memory, not big O.', 'why': 'Both loops are O(n), but following references jumps around memory and misses the cache.'},
    {'lv': 'x', 'q': 'After the tortoise and hare meet inside a loop, how do you find the node where the loop starts?', 'o': ['Count the loop length and divide by two', 'Move one pointer to the head, then step both by one until they meet', 'Reverse the list', 'Keep moving the hare by three'], 'a': 1, 'hint': 'The distance from the head to the start equals the distance from the meeting point to the start, going round.', 'why': 'If the tail has length a and they meet b steps into the loop of length c, then a ≡ c − b (mod c). Both pointers reach the start after a steps.'},
    {'lv': 'x', 'q': 'An LRU cache uses a hash map plus which structure to make get and put O(1)?', 'o': ['A sorted array', 'A binary heap', 'A doubly linked list', 'A stack'], 'a': 2, 'hint': 'You must move any node to the front and drop the back node quickly.', 'why': 'The map finds the node, and the doubly linked list unlinks and reinserts it in O(1).'},
    {'lv': 'x', 'q': 'Two pointers walk list A then B, and list B then A. Why do they meet at the shared node?', 'o': ['They move at different speeds', 'Both have walked the same total length when they reach it', 'The lists are sorted', 'The shared node is always the middle'], 'a': 1, 'hint': 'a + c + b = b + c + a', 'why': 'With private parts a and b and shared part c, both pointers have walked a + b + c when they reach the shared node.'},
    {'lv': 'x', 'q': 'Sorting a linked list with merge sort costs…', 'o': ['O(n) time', 'O(n log n) time', 'O(n²) time', 'It cannot be done'], 'a': 1, 'hint': 'Split with fast and slow pointers, merge in linear time.', 'why': 'log n levels of splitting, and each level merges n nodes in total: O(n log n).'},
]

CALC = [
    {'lv': 'e', 'q': 'A list has 8 nodes. How many references must you follow from the head to reach the last node?', 'ans': '7', 'hint': 'You start already standing on the first node.', 'steps': ['From node 1 to node 8 is 8 − 1 hops.', '<span class="eq">8 − 1 = 7</span>']},
    {'lv': 'e', 'q': 'Each node stores a 4 byte value and an 8 byte reference. How many bytes do 10 nodes use?', 'ans': '120', 'unit': 'bytes', 'hint': 'Add the two parts of one node first.', 'steps': ['One node is <span class="eq">4 + 8 = 12 bytes</span>', '<span class="eq">10 × 12 = 120 bytes</span>']},
    {'lv': 'm', 'q': 'With fast and slow pointers on a list of 9 nodes (no cycle), at which position (1 based) does slow stop?', 'ans': '5', 'hint': 'Fast stops on the last node.', 'steps': ['Fast visits 1, 3, 5, 7, 9 and stops. That is 4 moves.', 'Slow moves 4 times: <span class="eq">1 + 4 = 5</span>']},
    {'lv': 'm', 'q': 'A doubly linked list stores 4 byte values with two 8 byte references. How many extra bytes per node does it need compared with a singly linked one?', 'ans': '8', 'unit': 'bytes', 'hint': 'Only one thing is added.', 'steps': ['The extra field is the prev reference.', '<span class="eq">20 − 12 = 8 bytes</span>']},
    {'lv': 'h', 'q': 'A list has a tail of 3 nodes before a loop of 5 nodes. Slow and fast start at the head. How many steps until they first meet?', 'ans': '5', 'hint': 'Simulate positions, or use the gap argument after slow enters the loop.', 'steps': ['Number the tail 0, 1, 2 and the loop 3 to 7.', 'After 3 steps slow is at 3 and fast is at 6, which is 3 nodes ahead.', 'In the loop fast is 5 − 3 = 2 nodes behind slow, and the gap shrinks by one per step.', '<span class="eq">3 + 2 = 5 steps</span>']},
    {'lv': 'h', 'q': 'Reversing a list of 6 nodes with the three pointer loop changes how many next references?', 'ans': '6', 'hint': 'One per node.', 'steps': ['Each turn of the loop sets cur.next = prev exactly once.', '<span class="eq">6 nodes → 6 changes</span>']},
    {'lv': 'x', 'q': 'Merge sort on a linked list of 16 nodes: how many levels of merging are there?', 'ans': '4', 'hint': 'Halve until single nodes remain.', 'steps': ['16 → 8 → 4 → 2 → 1 takes 4 halvings.', '<span class="eq">log₂ 16 = 4</span>']},
    {'lv': 'x', 'q': 'An LRU cache of capacity 3 receives put(1), put(2), put(3), get(1), put(4). Which key is evicted?', 'ans': '2', 'hint': 'Track the order from most to least recent.', 'steps': ['After the three puts: 3, 2, 1 (most recent first).', 'get(1) moves 1 to the front: 1, 3, 2.', 'put(4) overflows, so the least recent key <span class="eq">2</span> is evicted.']},
]

VIZ_JS = r'''
(() => {
  const { esc, $, shell, seg, wireSeg, Player, Seq } = VIZ.kit;
  const W = VIZ.widgets;
  const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
  const node = (v, cls, tags, back) => `<div class="vz-lw">${tags ? `<span class="vz-ptr">${tags}</span>` : '<span class="vz-ptr"></span>'}<div class="vz-node ${cls || ''}"><b>${esc(v)}</b><i>${back ? 'prev·next' : 'next'}</i></div></div>`;
  const arrow = (dir = '→', cls = '') => `<span class="vz-arrow ${cls}">${dir}</span>`;

  W.llops = el => {
    const b = shell(el, 'Play with a linked list', 'Every button runs a real operation. Watch which arrows change and count the steps.');
    b.innerHTML = `<div class="vz-ops"><button data-op="head">Insert at head</button><button data-op="tail">Insert at tail</button><button data-op="after">Insert after the 2nd node</button><button data-op="find">Search for a value</button><button data-op="del">Delete a value</button><button data-op="reset">Reset</button></div><div class="vz-row"><label class="vz-sl"><input type="checkbox" data-tail checked> keep a tail reference</label></div><div class="vz-stage vz-scroll"></div><div class="vz-msg" aria-live="polite"></div>`;
    const stage = $('.vz-stage', b), msg = $('.vz-msg', b), seq = Seq(), tailBox = $('[data-tail]', b);
    let a = [12, 5, 30, 8];
    const say = h => { msg.innerHTML = h; };
    const draw = (hl = {}, tags = {}) => {
      const useTail = tailBox.checked;
      stage.innerHTML = `<div class="vz-ll">${a.map((v, k) => node(v, hl[k], [k === 0 ? 'head' : '', useTail && k === a.length - 1 ? 'tail' : '', tags[k] || ''].filter(Boolean).join(' · ')) + arrow()).join('')}<span class="vz-null">null</span></div>`;
    };
    draw();
    say('head refers to the first node. Each arrow is a reference to the next node.');
    tailBox.addEventListener('change', () => { draw(); say(tailBox.checked ? 'With a tail reference, adding at the end is O(1).' : 'Without a tail reference, adding at the end means walking the whole list.'); });
    b.querySelector('.vz-ops').addEventListener('click', e => {
      const op = (e.target.closest('button') || {}).dataset?.op;
      if (!op) return;
      seq.stop();
      if (op === 'reset') { a = [12, 5, 30, 8]; draw(); say('Back to the starting list.'); return; }
      if (op === 'head') {
        if (a.length >= 8) return say('The demo list is full. Press Reset.');
        const v = rand(1, 99);
        seq.run([() => { draw(); say(`Make a new node ${v} and point it at the current head (${a[0] ?? 'null'}).`); }, () => { a.unshift(v); draw({ 0: 'ok' }); say(`Move head to the new node. Two references changed, <b>O(1)</b>.`); }], 800);
      }
      if (op === 'tail') {
        if (a.length >= 8) return say('The demo list is full. Press Reset.');
        const v = rand(1, 99), steps = [];
        if (!tailBox.checked) for (let k = 0; k < a.length; k++) steps.push(((kk) => () => { const hl = {}; for (let j = 0; j < kk; j++) hl[j] = 'dim'; hl[kk] = 'hl'; draw(hl, { [kk]: 'cur' }); say(`Walk to node ${kk + 1} looking for the end.`); })(k));
        steps.push(() => { a.push(v); draw({ [a.length - 1]: 'ok' }); say(tailBox.checked ? `tail.next = new node ${v}, then tail moves to it. <b>O(1)</b>.` : `Found the end after ${a.length - 1} steps and linked ${v}. Without a tail reference this is <b>O(n)</b>.`); });
        seq.run(steps, 550);
      }
      if (op === 'after') {
        if (a.length < 2) return say('Add a few nodes first.');
        if (a.length >= 8) return say('The demo list is full. Press Reset.');
        const v = rand(1, 99);
        seq.run([
          () => { draw({ 0: 'dim', 1: 'hl' }, { 1: 'p' }); say(`Walk to the 2nd node (${a[1]}) and call it p.`); },
          () => { draw({ 1: 'hl' }, { 1: 'p' }); say(`Make node ${v}. First set new.next = p.next, so it points at ${a[2] ?? 'null'}.`); },
          () => { a.splice(2, 0, v); draw({ 1: 'hl', 2: 'ok' }, { 1: 'p' }); say(`Then p.next = new. The rest of the list did not move at all.`); }
        ], 900);
      }
      if (op === 'find' || op === 'del') {
        if (!a.length) return say('The list is empty.');
        const target = a[rand(0, a.length - 1)], steps = [];
        let k = 0;
        for (; k < a.length; k++) {
          steps.push(((kk) => () => { const hl = {}; for (let j = 0; j < kk; j++) hl[j] = 'dim'; hl[kk] = a[kk] === target ? 'ok' : 'hl'; draw(hl, { [kk]: 'cur' }); say(`Visit node ${kk + 1}: ${a[kk]}${a[kk] === target ? ` is ${target}! Found after ${kk + 1} visit${kk ? 's' : ''}.` : `, not ${target}, keep walking.`}`); })(k));
          if (a[k] === target) break;
        }
        if (op === 'del') steps.push(((kk) => () => { draw({ [kk]: 'bad' }, kk ? { [kk - 1]: 'prev' } : {}); say(kk ? `prev.next = node.next skips over ${target}.` : `${target} is the head, so head = head.next.`); })(k), ((kk) => () => { a.splice(kk, 1); draw(); say(`Deleted ${target}. Finding it cost ${kk + 1} visits, unlinking it cost <b>O(1)</b>.`); })(k));
        seq.run(steps, 650);
      }
    });
  };

  W.llrev = el => {
    const b = shell(el, 'Reverse a list, one arrow at a time', 'prev, cur and nxt walk along the list. Each step turns exactly one arrow around.');
    b.innerHTML = `<div class="vz-stage vz-scroll"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const vals = [1, 2, 3, 4, 5], n = vals.length;
    const steps = [];
    let prev = -1, cur = 0;
    steps.push({ prev, cur, nxt: null, done: 0, msg: 'Start: prev = null, cur = head.' });
    while (cur < n) {
      const nxt = cur + 1 < n ? cur + 1 : -1;
      steps.push({ prev, cur, nxt, done: cur, msg: `nxt = cur.next saves ${nxt < 0 ? 'null' : vals[nxt]}, so the rest of the list is not lost.` });
      steps.push({ prev, cur, nxt, done: cur + 1, msg: `cur.next = prev: ${vals[cur]} now points back at ${prev < 0 ? 'null' : vals[prev]}.` });
      prev = cur; cur = nxt < 0 ? n : nxt;
      steps.push({ prev, cur: cur < n ? cur : -1, nxt: null, done: prev + 1, msg: `Step forward: prev = ${vals[prev]}, cur = ${cur < n ? vals[cur] : 'null'}.` });
    }
    steps.push({ prev: n - 1, cur: -1, nxt: null, done: n, fin: true, msg: `cur is null, so stop. prev (${vals[n - 1]}) is the new head: ${vals.slice().reverse().join(' → ')} → null.` });
    const P = Player($('.vz-p', b), show, 900);
    function show(k) {
      const st = steps[k];
      let h = '<div class="vz-ll">' + (st.done > 0 ? '<span class="vz-null">null</span>' + arrow('←', 'rev') : '');
      vals.forEach((v, i) => {
        if (i > 0) h += i < st.done ? arrow('←', 'rev') : i === st.done ? arrow('⋯', 'cut') : arrow('→');
        const tags = [st.fin && i === st.prev ? 'new head' : '', !st.fin && i === 0 && st.done === 0 ? 'head' : '', i === st.prev && !st.fin ? 'prev' : '', i === st.cur ? 'cur' : '', i === st.nxt ? 'nxt' : ''].filter(Boolean).join(' · ');
        h += node(v, i === st.cur ? 'hl' : i < st.done ? 'ok' : '', tags);
      });
      if (st.done < n) h += arrow('→') + '<span class="vz-null">null</span>';
      $('.vz-stage', b).innerHTML = h + '</div>';
      $('.vz-msg', b).innerHTML = st.msg;
    }
    P.load(steps.length);
  };

  W.floyd = el => {
    const b = shell(el, 'Tortoise and hare', 'The tortoise 🐢 moves one node per step, the hare 🐇 moves two. With a loop they must meet. Without one, the hare falls off the end.');
    b.innerHTML = `<div class="vz-row">${seg('c', [['loop', 'List with a loop'], ['line', 'List without a loop']], 'loop')}</div><div class="vz-stage"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let mode = 'loop', steps = [];
    const T = 3, L = 6;                       // 3 tail nodes, then a loop of 6
    const N = T + L;
    const next = i => mode === 'loop' ? (i + 1 < N ? i + 1 : T) : (i + 1 < N ? i + 1 : -1);
    const pos = i => {
      if (mode === 'line') return [30 + i * 64, 120];
      if (i < T) return [40 + i * 62, 120];
      const ang = Math.PI - (i - T) * 2 * Math.PI / L;
      return [T * 62 + 40 + 80 + 80 * Math.cos(ang), 120 - 80 * Math.sin(ang)];
    };
    const P = Player($('.vz-p', b), show, 800);
    function setup() {
      steps = [];
      let s = 0, f = 0, k = 0;
      steps.push({ s, f, msg: 'Both start at the head.' });
      for (;;) {
        const f1 = next(f), f2 = f1 < 0 ? -1 : next(f1);
        if (f1 < 0 || f2 < 0) { steps.push({ s, f: -1, msg: `The hare reached null after ${k} steps. <b>No loop.</b> The tortoise is at node ${s}, the middle.`, end: 1 }); break; }
        s = next(s); f = f2; k++;
        if (s === f) { steps.push({ s, f, msg: `Step ${k}: they meet at node ${s}. <b>There is a loop.</b>`, meet: 1 }); break; }
        steps.push({ s, f, msg: `Step ${k}: tortoise at ${s}, hare at ${f}.` });
      }
      if (mode === 'loop') {
        let p = 0, q = s, j = 0;
        steps.push({ s: p, f: q, msg: 'Phase two: put one pointer back at the head. Now both move one step at a time.', two: 1 });
        while (p !== q) { p = next(p); q = next(q); j++; steps.push({ s: p, f: q, two: 1, msg: p === q ? `They meet again at node ${p} after ${j} steps. <b>That is where the loop starts.</b>` : `Both step once: ${p} and ${q}.` }); }
      }
      P.load(steps.length);
    }
    function show(k) {
      const st = steps[k];
      let s = '';
      for (let i = 0; i < N; i++) {
        const j = next(i);
        if (j >= 0) { const [x1, y1] = pos(i), [x2, y2] = pos(j); s += `<line class="vz-edge ${j === T && i === N - 1 ? 'on' : ''}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-end="url(#fa)"/>`; }
      }
      for (let i = 0; i < N; i++) {
        const [x, y] = pos(i);
        const cls = i === st.s && i === st.f ? 'ok' : i === st.s ? 'hl' : i === st.f ? 'mv' : '';
        s += `<g class="vz-tn ${cls}"><circle cx="${x}" cy="${y}" r="17"/><text x="${x}" y="${y + 5}">${i}</text></g>`;
        if (i === st.s) s += `<text class="vz-emo" x="${x - 12}" y="${y - 22}">🐢</text>`;
        if (i === st.f) s += `<text class="vz-emo" x="${x + (i === st.s ? 4 : -12)}" y="${y - 22}">${st.two ? '👣' : '🐇'}</text>`;
      }
      if (mode === 'line') { const [x, y] = pos(N - 1); s += `<text class="vz-tick" x="${x + 26}" y="${y + 4}">null</text>`; }
      $('.vz-stage', b).innerHTML = `<div class="vz-scroll"><svg class="vz-svg" viewBox="0 0 ${mode === 'loop' ? 460 : 620} 230" style="min-width:320px; max-width:620px; margin:0 auto"><defs><marker id="fa" viewBox="0 0 10 10" refX="27" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="var(--box-line)"/></marker></defs>${s}</svg></div>`;
      $('.vz-msg', b).innerHTML = st.msg;
    }
    wireSeg(b, 'c', v => { mode = v; setup(); });
    setup();
  };

  W.llmerge = el => {
    const b = shell(el, 'Merge two sorted lists', 'Compare the two front nodes, attach the smaller one to the result, and move on. The dummy node gives the result a place to start.');
    b.innerHTML = `<div class="vz-stage vz-scroll"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    const A = [1, 4, 7], B = [2, 3, 8, 9];
    const steps = [];
    let i = 0, j = 0;
    const out = [];
    steps.push({ i, j, out: [], msg: 'The result starts as just the dummy node. tail points at it.' });
    while (i < A.length && j < B.length) {
      const pickA = A[i] <= B[j];
      steps.push({ i, j, out: out.slice(), cmp: 1, msg: `Compare ${A[i]} and ${B[j]}: ${pickA ? A[i] : B[j]} is smaller.` });
      if (pickA) out.push(['a', A[i++]]); else out.push(['b', B[j++]]);
      steps.push({ i, j, out: out.slice(), msg: `Attach ${out[out.length - 1][1]} after tail and move tail to it.` });
    }
    const rest = i < A.length ? A.slice(i).map(v => ['a', v]) : B.slice(j).map(v => ['b', v]);
    out.push(...rest);
    steps.push({ i: A.length, j: B.length, out: out.slice(), fin: 1, msg: `One list is empty, so attach the rest (${rest.map(r => r[1]).join(', ')}) in one move. Result: ${out.map(o => o[1]).join(' → ')}.` });
    const P = Player($('.vz-p', b), show, 900);
    function row(label, arr, from, cmp, key) {
      return `<div class="vz-mrow"><span class="vz-tag">${label}</span><div class="vz-ll">${arr.map((v, k) => k < from ? '' : node(v, k === from && cmp ? 'hl' : '', k === from ? 'front' : '') + arrow()).join('')}<span class="vz-null">null</span></div></div>`;
    }
    function show(k) {
      const st = steps[k];
      const res = `<div class="vz-mrow"><span class="vz-tag">result</span><div class="vz-ll">${node('dummy', 'dim', st.out.length ? '' : 'tail')}${st.out.map((o, x) => arrow() + node(o[1], o[0] === 'a' ? 'ok' : 'sel', x === st.out.length - 1 && !st.fin ? 'tail' : '')).join('')}</div></div>`;
      $('.vz-stage', b).innerHTML = row('list a', A, st.i, st.cmp) + row('list b', B, st.j, st.cmp) + res;
      $('.vz-msg', b).innerHTML = st.msg;
    }
    P.load(steps.length);
  };
})();
'''

CSS = r'''
.vz-lw{display:flex; flex-direction:column; align-items:center; gap:2px}
.vz-ptr{font-size:11px; font-weight:800; color:var(--accent-deep); min-height:15px; white-space:nowrap; font-family:var(--font-mono)}
.vz-ll{align-items:flex-end; flex-wrap:nowrap; padding:2px 2px 6px}
.vz-ll .vz-arrow,.vz-ll .vz-null{padding-bottom:9px}
.vz-arrow.rev{color:var(--green)} .vz-arrow.cut{color:var(--ink2)}
.vz-node.sel{background:var(--sel)} .vz-node.mv{background:var(--mv)}
.vz-mrow{display:flex; align-items:center; gap:10px; margin:4px 0}
.vz-mrow>.vz-tag{min-width:56px}
.vz-emo{font-size:18px; font-family:"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif}
.vz-tick{font:700 12px var(--font-mono); fill:var(--ink2)}
'''

T = {
    'slug': 'linked-lists', 'title': 'Linked Lists', 'short': 'Linked lists', 'emoji': '🔗', 'topic': 'linked-lists', 'prefix': 'dsall',
    'module': ('🚃', 'Linear structures'),
    'lead': 'A linked list is a chain of nodes joined by references. It gives up instant access by position, and in return inserting and deleting never move anything. This page builds lists by hand, rewires them, reverses and merges them, and shows the tortoise and hare trick that finds middles and loops.',
    'desc': 'Linked lists in DSA: nodes and references, insertion and deletion with a dummy node, doubly linked and circular lists, in place reversal, fast and slow pointers, cycle detection, merging sorted lists and when to choose a list over an array, with code in Python, JavaScript and Java.',
    'minutes': 13,
    'parts': PARTS, 'codes': CODES, 'info': INFO, 'real': REAL, 'say': SAY, 'practice': PRACTICE, 'quiz': QUIZ, 'calc': CALC,
    'viz': VIZ_JS, 'css': CSS,
    'prev': ('strings', 'strings', '🔤 Strings'),
    'next': ('stacks-queues', 'stacks-queues', '🥞 Stacks and queues'),
}
