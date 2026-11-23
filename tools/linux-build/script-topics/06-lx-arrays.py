# Shell scripting 3.2: arrays and command-line options. Indexed arrays (create, read, length, indexes, append, unset,
# slices, negative indexes, "${a[@]}" versus "${a[*]}"), associative arrays with declare -A, filling arrays with
# globs, mapfile and read -a, per-element expansion, passing arrays to functions, getopts with OPTARG, OPTIND and a
# leading colon, long options with while and case, and the usage function. Sources: bash(1) sections Arrays,
# Parameter Expansion, SHELL BUILTIN COMMANDS (declare, mapfile, read, getopts, unset), POSIX getopts, the GNU Bash
# Reference Manual 6.7 and 4.2.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, eq
from lxkit import run, sample, lab, play, talk, cmdtable, shape

K = Kit()

K.lesson('indexed', 'Indexed arrays: many values under one name', f'''
<p>An <b>array</b> holds a list of values under one name. Each value has an <b>index</b>, starting at 0. Arrays keep values with spaces intact, which plain strings cannot do.</p>
{cmdtable([
    ('a=(x "y z" w)', 'Create an array with three elements', 'colours=(red "dark green" blue)'),
    ('${a[i]}', 'One element (index from 0, negative counts from the end)', 'echo "${colours[-1]}"'),
    ('"${a[@]}"', 'All elements, each as its own word', 'for c in "${colours[@]}"; do ...'),
    ('${#a[@]}', 'Number of elements', 'echo ${#colours[@]}'),
    ('${!a[@]}', 'The indexes that exist', 'echo ${!colours[@]}'),
    ('a+=(v)', 'Append one or more elements', 'colours+=(pink)'),
    ('a[i]=v', 'Set one element', 'colours[0]=crimson'),
    ('unset "a[i]"', 'Remove one element (the others keep their index)', 'unset "colours[1]"'),
    ('"${a[@]:s:n}"', 'A slice: n elements from index s', 'echo "${colours[@]:1:2}"')])}
{play('lx-array')}
{run('Indexed arrays, run for real', """colours=(red "dark green" blue)
echo "count: ${#colours[@]}, first: ${colours[0]}, last: ${colours[-1]}"
for c in "${colours[@]}"; do echo "[$c]"; done
for c in ${colours[@]}; do echo "<$c>"; done
colours+=(pink)
colours[9]=black
echo "indexes: ${!colours[@]}"
unset "colours[1]"
echo "after unset: ${#colours[@]} elements, indexes ${!colours[@]}"
echo "slice: ${colours[@]:1:2}"
packed=("${colours[@]}")
echo "packed indexes: ${!packed[@]}"
declare -p packed""", note='Quoted "${colours[@]}" kept dark green as one item, the unquoted form split it. Index 9 was allowed even though 4 to 8 do not exist. After unset the other indexes stayed where they were. Copying into a new array packed the values into 0, 1, 2 and 3. declare -p prints an array in a form you could paste back into bash.')}
{note('${#a[@]} counts elements, it is not the highest index plus one. Loop over "${a[@]}" for values or over "${!a[@]}" for indexes, never from 0 to the length minus 1, because arrays can have gaps.', 'warn')}
{talk('An array stores a list of values under a single name. You create one with an equals sign and round brackets around the values, and quotes keep a value with spaces as one element. Each element has a number called its index, and the first index is zero. To read one element, write dollar, a brace, the name, the index in square brackets, and a closing brace. A negative index counts from the end, so minus one is the last element. Dollar brace name, square brackets with an at sign, all inside double quotes, gives every element as a separate word, which is the safe way to loop. A hash in front gives the number of elements, and an exclamation mark gives the indexes. Plus equals appends, and unset removes one element. Bash arrays can have gaps: removing an element does not move the others, and you may set index nine on a four element array. The animation draws the boxes so you can watch this happen.')}
''', kw=['array', 'indexed array', 'array index', '"${a[@]}"', '${#a[@]}', '${!a[@]}', 'append to array', 'unset element', 'array slice', 'negative index', 'sparse array', 'declare -p'])

K.lesson('assoc', 'Associative arrays: values looked up by name', f'''
<p>An <b>associative array</b> uses text keys instead of numbers, like a dictionary. It must be declared with <code>declare -A</code> first. bash does not keep the keys in any particular order.</p>
{run('A phone book and a word counter', """declare -A phone=([asha]=98450 [ravi]=99001)
phone[meera]=97300
echo "Ravi: ${phone[ravi]}"
echo "${#phone[@]} entries"
for name in "${!phone[@]}"; do echo "$name -> ${phone[$name]}"; done | sort
[[ -v phone[john] ]] || echo "no number for john"
unset "phone[asha]"
echo "keys now: $(printf '%s\\n' "${!phone[@]}" | sort | tr '\\n' ' ')"
declare -A count=()
while read -r fruit; do (( count[$fruit]++ )); done < fruits.txt
for f in "${!count[@]}"; do echo "${count[$f]} $f"; done | sort -rn""", note='Keys can be any text. The loop over keys was piped into sort because bash returns keys in its own order. [[ -v ]] tests whether a key exists. (( count[$fruit]++ )) counts every word, starting from nothing, which is the classic way to tally items in bash.')}
{note('Without declare -A, phone[asha]=1 creates an indexed array, and the text asha is read as arithmetic, which gives index 0. Every key then overwrites the same element.', 'warn')}
{talk('An associative array works like a dictionary or a phone book. Instead of numbers, the keys are words, so you can look up a value by name. You must create it with declare dash capital A before using it. Then you set a value with the name, the key in square brackets and an equals sign, and read it back with dollar and braces. Exclamation mark with the at sign lists the keys, and a hash counts them. Keys come back in no particular order, so pipe the output to sort when order matters. To check if a key exists, use double brackets with dash v. A classic use is counting. Read words one by one and add one to the count for that word, and at the end you have a tally of every word, which you can sort to find the most common. If you forget declare dash capital A, bash quietly makes a normal indexed array and all your keys land in the same box.')}
''', kw=['associative array', 'declare -A', 'dictionary', 'hash map', 'keys', '${!a[@]}', '-v key exists', 'word count', 'count items', 'key order'])

K.lesson('fill', 'Filling, joining and passing arrays', f'''
{cmdtable([
    ('files=(*.log)', 'Fill from a glob (add shopt -s nullglob for none)', 'logs=(/var/log/*.log)'),
    ('mapfile -t lines < file', 'One element per line (-t removes the newline). readarray is the same', 'mapfile -t hosts < hosts.txt'),
    ('read -ra parts <<< "$s"', 'Split one line into words', 'IFS=, read -ra f <<< "$row"'),
    ('"${a[*]}"', 'All elements joined with the first character of IFS', '(IFS=,; echo "${a[*]}")'),
    ('"${a[@]/old/new}"', 'Change every element, also # % ^^ and ,,', 'echo "${files[@]%.log}"'),
    ('fn "${a[@]}"', 'Pass an array to a function as its arguments', 'sum "${nums[@]}"')])}
{run('Arrays from files, commands and functions', """mapfile -t lines < poem.txt
echo "${#lines[@]} lines, line 2 is: ${lines[1]}"
row="Asha,maths,91"
IFS=, read -ra field <<< "$row"
echo "name=${field[0]} score=${field[2]}"
txt=(*.txt)
echo "${#txt[@]} text files: ${txt[*]}"
echo "without extension: ${txt[@]%.txt}"
nums=(4 8 15 16 23 42)
joined=$(IFS=+; echo "${nums[*]}")
echo "$joined = $(( $joined ))"
sum() { local t=0 n; for n in "$@"; do (( t += n )); done; echo "$t"; }
echo "sum: $(sum "${nums[@]}")"
mapfile -t sorted < <(printf '%s\\n' "${nums[@]}" | sort -rn)
echo "largest first: ${sorted[*]}"
words=($(echo "one two  three"))
echo "${#words[@]} words\"""", note='mapfile read the poem into one element per line. read -ra split the CSV row at commas. With IFS set to a plus sign inside the $( ) subshell, "${nums[*]}" became 4+8+15+16+23+42, and $(( )) added it up. The script’s own IFS was not touched. A function receives an array as its normal arguments. Sorting goes through printf, sort and mapfile.')}
{talk('There are several ways to fill an array. A wildcard pattern in round brackets gives the matching file names. Mapfile dash t reads a whole file, one line per element, and is the fastest and safest way to load lines. Read dash r a splits a single line into words, and with IFS set to a comma it splits a CSV row into fields. To join an array into one string, use the star form in double quotes. It puts the first character of IFS between the elements, so with IFS set to a plus sign you get a sum you can hand to arithmetic. Most parameter expansion tricks work on every element at once, for example percent dot t x t removes the extension from every file name. Bash cannot pass an array to a function as a single thing, so you pass its elements as the arguments and the function reads them with dollar at sign. To sort an array, print it one per line, sort it, and read it back with mapfile.')}
''', kw=['mapfile', 'readarray', 'read -a', 'array from file', 'array from glob', 'join array', '"${a[*]}"', 'IFS join', 'sort an array', 'pass array to function', 'split string into array'])

K.lesson('options', 'Command-line options with getopts', f'''
<p>Real tools accept options such as <code>-v</code> or <code>-n 5</code>. The builtin <code>getopts</code> reads them one at a time, following the POSIX rules: options come first, can be grouped as <code>-vn5</code>, and <code>--</code> ends them.</p>
{shape('The getopts loop', """usage() { echo "usage: ${0##*/} [-v] [-n COUNT] FILE..." >&2; exit 2; }
verbose=0 count=10
while getopts ":vn:" opt; do     # n: means -n takes a value
  case $opt in
    v)  verbose=1 ;;
    n)  count=$OPTARG ;;
    :)  echo "-$OPTARG needs a value" >&2; usage ;;
    \\?) echo "unknown option -$OPTARG" >&2; usage ;;
  esac
done
shift $(( OPTIND - 1 ))          # now "$@" holds only the files""")}
{table(['Part', 'Meaning'], [
    ['<code>":vn:"</code>', 'the option letters. A colon after a letter means it takes a value. A leading colon means you print the errors yourself'],
    ['<code>$opt</code>', 'the letter found, : when a value is missing, ? for an unknown option'],
    ['<code>$OPTARG</code>', 'the value of an option, or the bad letter in the : and ? cases'],
    ['<code>$OPTIND</code>', 'the index of the next argument to read, so shift $(( OPTIND - 1 )) drops the options']])}
{run('getopts in a real script', """cat > head2.sh <<'EOF'
#!/bin/bash
usage() { echo "usage: ${0##*/} [-v] [-n COUNT] FILE..." >&2; exit 2; }
verbose=0 count=3
while getopts ":vn:" opt; do
  case $opt in
    v)  verbose=1 ;;
    n)  [[ $OPTARG =~ ^[0-9]+$ ]] || { echo "-n needs a number" >&2; usage; }
        count=$OPTARG ;;
    :)  echo "-$OPTARG needs a value" >&2; usage ;;
    \\?) echo "unknown option -$OPTARG" >&2; usage ;;
  esac
done
shift $(( OPTIND - 1 ))
(( $# )) || usage
for f in "$@"; do
  (( verbose )) && echo "== $f (first $count lines) =="
  head -n "$count" -- "$f"
done
EOF
bash head2.sh -v -n 2 fruits.txt poem.txt
bash head2.sh -vn1 notes.txt
bash head2.sh -n; echo "status $?"
bash head2.sh -x notes.txt; echo "status $?"
bash head2.sh -n two notes.txt; echo "status $?"
bash head2.sh -- -v 2>&1 | head -1""", note='-v and -n 2 were read in order, then shift left only the two files. Grouped -vn1 worked as well. A missing value, an unknown letter and a non-number each gave a clear message and status 2. After --, getopts stopped, so -v was treated as a file name.')}
{shape('Long options with a while and case loop', """while (( $# )); do
  case $1 in
    -v|--verbose)   verbose=1 ;;
    -n|--count)     count=$2; shift ;;
    --count=*)      count=${1#*=} ;;
    --)             shift; break ;;
    -*)             echo "unknown option $1" >&2; exit 2 ;;
    *)              break ;;
  esac
  shift
done""", note='getopts reads only one-letter options. For --long options, scripts loop over the arguments with case and shift, as here. The external getopt program from util-linux can also parse long options.')}
{lab('Arrays and options', [
    ('Create an array <code>pets</code> with the values cat, dog and "guinea pig".', 'pets=(cat dog "guinea pig")', [{'cmd': r'pets=\('}]),
    ('Print the number of elements in pets.', 'echo ${#pets[@]}', [{'cmd': r'\$\{#pets\[@\]\}'}, {'out': '^3$'}]),
    ('Print the last element of pets with a negative index.', 'echo "${pets[-1]}"', [{'cmd': r'-1'}, {'out': '^guinea pig$'}]),
    ('Append fish to pets, then print all indexes.', 'pets+=(fish); echo ${!pets[@]}', [{'cmd': r'\+=\('}, {'out': '^0 1 2 3$'}]),
    ('Read the lines of fruits.txt into the array f with mapfile, then print how many there are.', 'mapfile -t f < fruits.txt; echo ${#f[@]}', [{'cmd': r'mapfile|readarray'}, {'out': '^8$'}]),
    ('Make an associative array <code>cap</code> with India mapped to Delhi, then print cap[India].', 'declare -A cap=([India]=Delhi); echo ${cap[India]}', [{'cmd': r'declare\s+-A'}, {'out': '^Delhi$'}]),
    ('Set the arguments with set -- -v -n 7 file, then run a getopts loop for "vn:" that prints n=7 for the -n option.', 'set -- -v -n 7 file; while getopts "vn:" o; do [ "$o" = n ] && echo "n=$OPTARG"; done', [{'cmd': r'getopts'}, {'out': '^n=7$'}])])}
{talk('Professional tools take options, such as dash v for verbose or dash n five for a count. Bash has a builtin called getopts that reads them one at a time inside a while loop. You give it a string of option letters, and a colon after a letter means that option needs a value. Each time round the loop, getopts puts the letter it found in your variable, and the value, if there is one, in OPTARG. A colon at the very start of the string tells getopts to stay quiet, so your script can print its own friendly error messages: the variable then holds a colon when a value is missing, and a question mark for an unknown option. After the loop, shift by OPTIND minus one removes all the options, and dollar at sign holds just the file names. Getopts only knows single letters, so for double dash long options, scripts loop over the arguments themselves with a case statement and shift.')}
''', kw=['getopts', 'command-line options', 'OPTARG', 'OPTIND', 'shift', 'option string', 'leading colon', 'usage function', 'long options', '--', 'getopt'])

K.lesson('levels', 'Arrays and options from school to research', f'''
{ladder(
    '<p>An array is a numbered list of values under one name, starting at 0. An associative array uses words as keys. getopts reads options such as -v and -n 5 so a script behaves like a real tool.</p>',
    '<p>bash arrays are one-dimensional and sparse: indexes need not be consecutive, and ${#a[@]} counts only the elements that exist. Arrays cannot be exported to child processes, and a function receives an array only as its arguments. "${a[@]}" expands to one word per element, exactly like "$@".</p>',
    '<p>Associative arrays need bash 4.0 or later (macOS still ships bash 3.2, so scripts there use other tools or a newer bash). local -n gives a function a reference to the caller’s array. mapfile -d "" with find -print0 reads any file name safely, and -C with -c runs a callback every few lines. getopts follows POSIX: options before operands, -- ends them, and OPTIND must be reset to 1 before parsing a second list.</p>',
    '<p>Arrays in bash came from the Korn shell, and POSIX sh still has no arrays, so portable scripts use "$@" with set -- as their only list. Command-line conventions themselves are standardised in the POSIX Utility Syntax Guidelines (XBD chapter 12), and the GNU Coding Standards add long options. Research tools that generate argument parsers and shell completions from one description, such as docopt and argbash, aim to keep usage text, parsing and documentation in sync.</p>')}
{scene('the log summary tool', '<p>An operations team needed a tool to summarise error counts per service. <code>logsum.sh -s 2026-11-20 -t 10 /var/log/app/*.log</code> parses <code>-s</code> for the start date and <code>-t</code> for the top N with getopts, reads every log with mapfile, counts errors per service in an associative array, and prints the top entries through sort. A usage function and status 2 for bad options make it safe to call from cron and CI jobs.</p>')}
{talk('Here is the deeper view. Bash arrays have one dimension and can have gaps, so the count of elements is not the same as the highest index. Arrays cannot travel to child processes through the environment, and a function only sees an array if you pass its elements as arguments or give it a name reference with local dash n. Associative arrays arrived in bash four, so the very old bash three point two on macOS does not have them. For truly safe file name handling, mapfile can split on the zero byte that find dash print zero writes. Getopts follows the POSIX rules: options come before other arguments, and a double dash ends them. Interestingly, POSIX sh has no arrays at all, so portable scripts use dollar at sign together with set double dash as their only list. Researchers and tool builders have created generators such as docopt and argbash, which build the option parser, the help text and shell completion from a single description.')}
''', kw=['sparse arrays', 'bash 4 associative arrays', 'macOS bash 3.2', 'local -n', 'mapfile -d', 'POSIX utility syntax', 'OPTIND reset', 'docopt', 'argbash', 'Korn shell arrays'])

K.quiz('e', 'Which index does the first element of a bash array have?', ['1', '0', '-1', 'a'], 1, 'Count from zero.', 'Arrays start at index 0.')
K.quiz('e', 'a=(x y z). What is ${#a[@]}?', ['2', '3', 'z', '0'], 1, 'Count the elements.', 'Three elements.')
K.quiz('e', 'How do you append the value w to the array a?', ['a=w', 'a+=(w)', 'a[w]', 'push a w'], 1, 'Plus equals with brackets.', 'a+=(w) appends.')
K.quiz('e', 'Which must come before using text keys in an array?', ['declare -a', 'declare -A', 'local', 'export'], 1, 'Capital A.', 'declare -A makes an associative array.')
K.quiz('m', 'a=(one "two three"). How many words does "${a[@]}" give?', ['3', '2', '1', '4'], 1, 'Quoted at sign.', 'Each element stays one word.')
K.quiz('m', 'a=(p q r s), then unset "a[1]". What is ${!a[@]}?', ['0 1 2', '0 2 3', '1 2 3', '0 1 2 3'], 1, 'Gaps stay.', 'The other indexes do not move.')
K.quiz('m', 'Which reads every line of hosts.txt into the array h?', ['h=$(cat hosts.txt)', 'mapfile -t h < hosts.txt', 'read h < hosts.txt', 'h=(hosts.txt)'], 1, 'mapfile.', 'mapfile -t gives one element per line.')
K.quiz('m', 'In getopts ":ab:c", which option takes a value?', ['a', 'b', 'c', 'none'], 1, 'Colon after the letter.', 'b: means -b needs a value.')
K.quiz('m', 'After the getopts loop, why run shift $(( OPTIND - 1 ))?', ['To reset getopts', 'To remove the options so "$@" holds only the remaining arguments', 'To count options', 'It is not needed'], 1, 'Drop what was read.', 'OPTIND points past the last option.')
K.quiz('h', 'With a leading colon in the option string, what is $opt when -n is given without its value?', ['n', '?', ':', 'empty'], 2, 'Silent mode.', 'A colon means a missing value, and OPTARG holds n.')
K.quiz('h', 'a=(1 2 3) and IFS=, in a subshell. What does echo "${a[*]}" print?', ['1 2 3', '1,2,3', '123', '1, 2, 3'], 1, 'Star joins with IFS.', 'The first character of IFS joins the elements.')
K.quiz('h', 'Without declare -A, what does m[asha]=1 m[ravi]=2 do?', ['Makes two keys', 'Treats both keys as arithmetic 0, so m[0] ends up as 2', 'Gives an error', 'Exports m'], 1, 'Index arithmetic.', 'In an indexed array the subscript is arithmetic, and an unset name is 0.')
K.quiz('x', 'Which bash version first had associative arrays?', ['2.0', '3.2', '4.0', '5.1'], 2, 'Not on old macOS bash.', 'They arrived in bash 4.0.')

K.calc('e', 'a=(10 20 30 40). What is ${a[2]}?', '30', 'Count from 0.', ['Index 0 is 10, index 1 is 20.', 'Index 2 is the third value.', eq('30')], check=30)
K.calc('e', 'a=(10 20 30 40). What is ${a[-1]} + ${a[0]}?', '50', 'Last plus first.', ['${a[-1]} is 40.', '${a[0]} is 10.', eq('40 + 10 = 50')], check=50)
K.calc('m', 'a=(a b c d e f). How many elements does "${a[@]:2:3}" give, and which is first?', '3', 'Start at index 2.', ['Index 2 is c.', 'Take 3: c, d, e.', eq('3 elements, starting with c')], check=3)
K.calc('m', 'a=(x y z), then a[7]=w. What is ${#a[@]}?', '4', 'Only existing elements count.', ['Indexes 0, 1, 2 and 7 exist.', '3 to 6 do not exist.', eq('4 elements')], check=4)
K.calc('m', 'nums=(4 8 15 16 23 42). With IFS=+, what does $(( ${nums[*]} )) give?', '108', 'Add them up.', ['4 + 8 + 15 = 27.', '27 + 16 + 23 = 66.', eq('66 + 42 = 108')], check=108)
K.calc('h', 'The script gets -v -n 5 a.txt b.txt. After the getopts loop for "vn:", what is OPTIND?', '4', 'Index of the next argument.', ['-v is argument 1, -n is 2, 5 is 3.', 'a.txt is argument 4.', eq('OPTIND = 4, so shift 3')], check=4)

K.must('Indexed arrays', 'a=(x "y z"), ${a[i]} from 0, ${a[-1]} last, "${a[@]}" all as words, ${#a[@]} count, ${!a[@]} indexes, a+=(v), unset "a[i]".')
K.must('Associative arrays', 'declare -A m first. m[key]=v, ${m[key]}, "${!m[@]}" keys in no order, [[ -v m[key] ]] to test.')
K.must('Filling and joining', 'files=(*.txt), mapfile -t lines < file, read -ra parts <<< "$s". "${a[*]}" joins with the first character of IFS.')
K.must('getopts', 'while getopts ":vn:" opt with case, $OPTARG for values, : and ? for errors, then shift $(( OPTIND - 1 )).')
K.must('Usage', 'A usage function that prints to stderr and exits with 2. Long options need a while and case loop.')

T = K.topic(
    slug='arrays-options', topic='arrays-options',
    step=(3, 'Functions and data', 'lx-script-3', 'Build scripts from named, tested pieces: functions with local variables, libraries, arrays and option parsing with getopts.', 'Intermediate'),
    title='Arrays and command-line options', short='Arrays and options', badge='3.2', minutes=55, added='2026-11-23',
    lead='Keep lists safely in arrays, look values up by name with associative arrays, fill and join arrays, and give your scripts real options with getopts.',
    desc='Indexed arrays with indexes, length, appends, unset, slices, negative indexes and gaps, "${a[@]}" versus "${a[*]}", associative arrays with declare -A and word counting, filling arrays from globs, mapfile and read -a, per-element expansion, passing arrays to functions, sorting, getopts with OPTARG, OPTIND, the leading colon and usage messages, and long options with while and case.',
    summary='Indexed and associative arrays, mapfile and read -a, and getopts.',
    keywords=['array', 'associative array', 'declare -A', 'mapfile', 'readarray', 'read -a', 'getopts', 'OPTARG', 'OPTIND', 'options', 'usage'],
    recap='<p>Arrays hold lists with spaces intact: "${a[@]}" gives every element, ${#a[@]} counts them and indexes can have gaps. declare -A gives text keys. mapfile and read -a fill arrays, and getopts with case and shift turns a script into a tool with real options.</p>')
