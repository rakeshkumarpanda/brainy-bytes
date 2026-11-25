#!/bin/bash
# Run every sample and example with the real compiler (javac, gcc, g++) and with the playground runner,
# and print PASS or the difference. C# has no compiler here, so its expected output is kept in expected/*.cs.out
# and samples/*.out, written by hand from .NET's rules. Usage: bash tools/playground-build/check.sh
# Programs that crash on purpose (bug.c, bug.cpp, stl.cpp) show DIFF: the real program loses output it had not
# flushed, or the shell adds its own "Aborted" line, while the playground shows both the output and a clear message.
H=$(cd "$(dirname "$0")" && pwd); W=$(mktemp -d)
check() { # file stdin
  f=$1; in=$2; ext=${f##*.}; d=$W/$(basename $f).d; mkdir -p $d
  case $ext in
    java) lang=java; cp $f $d/Main.java; (cd $d && javac Main.java 2>/dev/null && printf "%b" "$in" | java Main 2>&1 | grep -v '^Picked up') > $d/real;;
    c) lang=c; gcc -w -o $d/a $f -lm && (printf "%b" "$in" | $d/a > $d/real 2>&1);;
    cpp) lang=cpp; g++ -w -std=c++17 -o $d/a $f && (printf "%b" "$in" | $d/a > $d/real 2>&1);;
    cs) lang=cs; exp=${f%.cs}.out; [ -f $exp ] || exp=$H/expected/$(basename $f).out; cp $exp $d/real;;
  esac
  node $H/run.js $f $lang "$(printf "%b" "$in")" > $d/mine 2>/dev/null
  if diff -q $d/real $d/mine >/dev/null; then echo "PASS $(basename $f)"; else echo "DIFF $(basename $f)"; diff $d/real $d/mine | head -8; fi
}
for f in $H/examples/{java,c,cpp,cs}/*; do check $f 'Asha\n12\n'; done
check $H/samples/Fib.java ''; check $H/samples/Oop.java ''; check $H/samples/Beginner.java 'Ravi Kumar\n5\n9 7 3 8 1'
check $H/samples/basics.c '3 4\n5'; check $H/samples/beginner.c 'Mia 11\nwhole line here'
check $H/samples/stl.cpp 'Ann 21'; check $H/samples/beginner.cpp 'Lee Chan\n3\n70 85 90'
check $H/samples/Program.cs 'Sam\n7'; check $H/samples/Beginner.cs 'Ira\n9'
rm -rf $W
