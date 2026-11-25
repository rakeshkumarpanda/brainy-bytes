#!/bin/bash
# Compile every program in compile-errors/ with the real compiler and with the playground checker, and compare the
# first error: its line, its first line of text, and the symbol / location / required / found lines that follow.
# Java uses javac, C uses gcc and C++ uses g++ (their "did you mean" spelling suggestions are left out). C# has no compiler here, so each .cs file starts with the expected error as
# a comment:   // expect: 6: CS0266: Cannot implicitly convert type 'int' to 'byte'. ...
# Programs in compile-errors/ok/ are correct and must pass the checker with no error.
# Usage: bash tools/playground-build/errors.sh
H=$(cd "$(dirname "$0")" && pwd); W=$(mktemp -d); pass=0; fail=0
mine() { CHECK_DEBUG=1 node $H/run.js "$1" "$2" '' 2>/dev/null | sed -n '/^\[COMPILE\]/,$p' | sed -E 's/^\[COMPILE\] line ([0-9]+): /\1: /'; }
for f in $H/compile-errors/java/*.java; do
  cp $f $W/Main.java
  real=$(cd $W && javac Main.java 2>&1 | grep -v '^Picked up' | awk '/^Main.java:[0-9]+: error:/{n++} n==1' | grep -E '^Main.java|^  (symbol|location|required|found|reason|first type|second type):|^    method|^      \(|^  \(' | sed -E 's/^Main.java:([0-9]+): error: /\1: /')
  got=$(mine $f java)
  if [ "$real" == "$got" ] && [ -n "$real" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "DIFF $(basename $f)"; diff <(echo "$real") <(echo "$got") | head -8; fi
done
for f in $(ls $H/compile-errors/cpp/*.cpp 2>/dev/null); do
  real=$(g++ -fsyntax-only $f 2>&1 | grep -m1 -E ':[0-9]+:[0-9]+: error:' | sed -E 's/^.*:([0-9]+):[0-9]+: error: /\1: /; s/; did you mean .*$//')
  got=$(mine $f cpp | head -1)
  if [ "$real" == "$got" ] && [ -n "$real" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "DIFF $(basename $f)"; diff <(echo "$real") <(echo "$got") | head -6; fi
done
for f in $(ls $H/compile-errors/c/*.c 2>/dev/null); do
  real=$(gcc -fsyntax-only $f 2>&1 | grep -m1 -E ':[0-9]+:[0-9]+: error:' | sed -E 's/^.*:([0-9]+):[0-9]+: error: /\1: /; s/; did you mean .*$//')
  got=$(mine $f c | head -1)
  if [ "$real" == "$got" ] && [ -n "$real" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "DIFF $(basename $f)"; diff <(echo "$real") <(echo "$got") | head -6; fi
done
for f in $(ls $H/compile-errors/cs/*.cs 2>/dev/null); do
  real=$(head -1 $f | sed -E 's|^// expect: ||')
  got=$(mine $f cs | head -1)
  if [ "$real" == "$got" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "DIFF $(basename $f)"; diff <(echo "$real") <(echo "$got") | head -6; fi
done
# programs that are correct must pass the checker
for f in $H/compile-errors/ok/*; do
  case $f in *.java) l=java;; *.cs) l=cs;; *.cpp) l=cpp;; *.c) l=c;; esac
  got=$(mine $f $l)
  if [ -z "$got" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "WRONGLY REJECTED $(basename $f): $got"; fi
done
echo "$pass match, $fail differ"
rm -rf $W
