# Advanced Python 3.3: logging and debugging. Checked against the Python 3.14 documentation of the logging module,
# the Logging HOWTO and Logging Cookbook, logging.config.dictConfig, logging.handlers (RotatingFileHandler,
# TimedRotatingFileHandler), pdb and breakpoint() (PEP 553), the assert statement and the -O option, and f-string
# self documenting expressions (f"{x=}", Python 3.8). The pdb session below is a real run.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items, show, term

chapter('py-logging')
K = Kit()

K.code('basics', r'''
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, force=True,
                    format="%(levelname)s %(name)s: %(message)s")

logging.debug("hidden: DEBUG is below INFO")
logging.info("app started")
logging.warning("disk is 91% full")
logging.error("could not save the file")
logging.critical("database is down")
print(logging.getLevelName(logging.WARNING), logging.WARNING, logging.getLogger().level)
''')

K.code('loggers', r'''
import logging
import os
import sys
import tempfile

log_path = os.path.join(tempfile.mkdtemp(), "app.log")

logger = logging.getLogger("shop.cart")        # in a module: logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False                       # do not also pass records to the root logger

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.WARNING)              # the screen shows only problems
console.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)           # the file keeps everything
file_handler.setFormatter(logging.Formatter("%(levelname)-8s %(funcName)s:%(lineno)d %(message)s"))

logger.addHandler(console)
logger.addHandler(file_handler)


def checkout(total):
    logger.debug("checkout started with total %s", total)
    if total > 1000:
        logger.warning("large order: %s", total)
    logger.info("order saved")


checkout(1500)
file_handler.close()
print("--- app.log ---")
with open(log_path) as f:
    print(f.read().strip())
print(logging.getLogger("shop").name, logger.parent.name, logger.parent.parent.name)
''')

K.code('habits', r'''
import io
import logging

stream = io.StringIO()
logger = logging.getLogger("payments")
logger.setLevel(logging.INFO)
logger.propagate = False
handler = logging.StreamHandler(stream)
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
logger.addHandler(handler)


class Report:
    def __str__(self):
        print("  (the slow __str__ ran)")
        return "big report"


logger.debug(f"report: {Report()}")            # an f-string is built first, even if dropped
logger.debug("report: %s", Report())           # %s with arguments: never built, DEBUG is off
logger.info("report: %s", Report())            # built now, because INFO passes
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("could not split the bill")   # ERROR level plus the traceback

lines = stream.getvalue().splitlines()
print(lines[0])
print(lines[1])
print(lines[2])
print(lines[-1])
print(logger.isEnabledFor(logging.DEBUG))
''')

K.code('config', r'''
import logging
import logging.config

CONFIG = {
    "version": 1,
    "formatters": {
        "short": {"format": "%(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "screen": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "short",
            "level": "INFO",
        },
    },
    "loggers": {
        "shop": {"level": "DEBUG", "handlers": ["screen"], "propagate": False},
    },
}
logging.config.dictConfig(CONFIG)

cart = logging.getLogger("shop.cart")
cart.info("child loggers use the handlers of their parent")
cart.debug("the handler level still filters this one out")
print(cart.getEffectiveLevel(), cart.handlers, cart.parent.name)
''')

K.code('debugging', r'''
scores = [70, 80, 90]
total = 0
for s in scores:
    total = s                                  # the bug: it should be total += s
    print(f"{s=} {total=}")                    # = prints the name AND the value
print(f"{total / len(scores)=:.1f}")


def apply_discount(price, percent):
    assert 0 <= percent <= 100, f"bad percent: {percent}"
    return price * (100 - percent) / 100


print(apply_discount(200, 10))
try:
    apply_discount(200, 150)
except AssertionError as err:
    print("AssertionError:", err)
print("asserts are on:", __debug__)            # python -O turns them off
''')

BUGGY = '''def average(scores):
    total = 0
    for s in scores:
        total = s
    return total / len(scores)


print(average([70, 80, 90]))'''

K.lesson('idea', 'Logging: a diary for your program', f'''
{src('Python 3.14 documentation of logging, the Logging HOWTO and Cookbook, logging.config, logging.handlers, pdb, breakpoint() (PEP 553) and the assert statement. The pdb session is a real run.')}
{wwh('<b>Logging</b> means your program writes short messages about what it is doing, each with a <b>level</b> that says how important it is: DEBUG, INFO, WARNING, ERROR or CRITICAL. <b>Debugging</b> is finding out why a program does the wrong thing, with tools such as print, logging, assert and the pdb debugger.',
     'When a program runs on a server at 3 am, nobody is watching the screen. print messages vanish, cannot be switched off without editing code, and say nothing about when or where they came from. Logs are kept in files, can be turned up or down without changing code, and carry the time, module and line, so you can find out later what happened.',
     'You ask for a <b>logger</b> by name and call logger.info(...) and friends. The logger drops messages below its level. Passing messages become <b>LogRecords</b> that go to <b>handlers</b> (screen, file, email, network), each with its own level and a <b>formatter</b> that decides the text layout.')}
{viz('pylog')}
{run('basics')}
{table(['Level', 'Number', 'Use it for'], [
    ['DEBUG', '10', 'Details for developers: values, steps'],
    ['INFO', '20', 'Normal events: started, saved, user logged in'],
    ['WARNING', '30', 'Something odd that the program can handle (the default level)'],
    ['ERROR', '40', 'An operation failed'],
    ['CRITICAL', '50', 'The program may not be able to go on']])}
{note('Without basicConfig the root logger shows only WARNING and above, on stderr. basicConfig sets the level, the format and the stream in one call, but only the first time, unless you pass force=True.', 'exam')}
''', kw=['logging', 'log levels', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'basicConfig', 'debugging'])

K.lesson('loggers', 'Loggers, handlers and formatters', f'''
{run('loggers')}
{table(['Part', 'Job', 'Example'], [
    ['Logger', 'Named entry point, first level check, part of a tree split by dots', 'logging.getLogger("shop.cart")'],
    ['Handler', 'Sends records somewhere, with its own level', 'StreamHandler, FileHandler, RotatingFileHandler, SMTPHandler'],
    ['Formatter', 'Turns a record into text', '"%(asctime)s %(levelname)s %(name)s: %(message)s"'],
    ['Filter', 'Extra yes or no rule for a logger or handler', 'Drop records that contain a password']])}
{note('Loggers form a tree by name: shop.cart is a child of shop, which is a child of root. A record goes to the handlers of its logger and then, unless propagate is False, up to the parents. Add handlers in one place (often the root or the top package logger) and just call getLogger(__name__) in every module.', 'tip')}
{table(['Format field', 'Gives'], [
    ['%(asctime)s', 'Date and time'], ['%(levelname)s', 'DEBUG, INFO, ...'], ['%(name)s', 'Logger name'],
    ['%(message)s', 'Your message with its arguments filled in'], ['%(funcName)s, %(lineno)d, %(filename)s', 'Where the call was made'],
    ['%(process)d, %(threadName)s', 'Which process and thread']])}
''', kw=['getLogger', '__name__', 'logger hierarchy', 'propagate', 'StreamHandler', 'FileHandler', 'Formatter', 'Filter', 'format fields'])

K.lesson('practice', 'Good logging habits', f'''
{run('habits')}
{note('Pass values as arguments: logger.debug("total %s", total). The text is only built if the record passes the level checks. An f-string is always built, even when the message is thrown away, as the first slow __str__ line shows.', 'exam')}
{note('Inside except, logger.exception("...") logs at ERROR level and adds the full traceback. Never log passwords, card numbers or personal data: logs are read by many people and kept for a long time.', 'warn')}
{versus('Reporting what a program does', ['', 'print', 'logging'], [
    ['Turn off without editing code', 'No', 'Yes, change the level'],
    ['Time, module and line', 'Only if you add them by hand', 'Yes, from the format'],
    ['Where it goes', 'The screen', 'Screen, files, servers, email, all at once'],
    ['Importance', 'All the same', 'Five levels'],
    ['Good for', 'Quick checks while learning and the normal output of a script', 'Everything in programs that run for real']],
    'print is for the output your user asked for. Messages about how the program is doing belong in logging.')}
''', kw=['lazy formatting', 'f-string in logging', 'logger.exception', 'isEnabledFor', 'sensitive data', 'print vs logging'])

K.lesson('config', 'Configuring logging for a whole app', f'''
{run('config')}
{table(['Handler (logging.handlers)', 'Keeps logs under control by'], [
    ['RotatingFileHandler(path, maxBytes, backupCount)', 'Starting a new file at maxBytes and keeping backupCount old ones'],
    ['TimedRotatingFileHandler(path, when="midnight", backupCount=7)', 'Starting a new file every day (or hour) and keeping a week'],
    ['QueueHandler and QueueListener', 'Writing from a background thread, so slow disks do not slow the program'],
    ['SysLogHandler, HTTPHandler', 'Sending logs to a central server']])}
{note('Configure logging once, at program start, with dictConfig (or a file read into a dict, often YAML or TOML). Libraries must never call basicConfig: they only call getLogger(__name__), and the application decides what to show. dictConfig switches off loggers that already exist unless you set "disable_existing_loggers": False.', 'tip')}
''', kw=['dictConfig', 'logging.config', 'RotatingFileHandler', 'TimedRotatingFileHandler', 'QueueHandler', 'library logging', 'disable_existing_loggers'])

K.lesson('debugging', 'Debugging: print, assert and pdb', f'''
{run('debugging')}
<p>The same bug in a function, found with the pdb debugger. Put <code>breakpoint()</code> in the code, or start the program with <code>python -m pdb</code>, and you can stop on any line and look at the variables:</p>
{show('buggy.py', BUGGY)}
{term(['$ python -m pdb buggy.py',
       '> /tmp/demo/buggy.py(1)<module>()',
       '-> def average(scores):',
       '(Pdb) b 4',
       'Breakpoint 1 at /tmp/demo/buggy.py:4',
       '(Pdb) c',
       '> /tmp/demo/buggy.py(4)average()',
       '-> total = s',
       '(Pdb) p s, total',
       '(70, 0)',
       '(Pdb) c',
       '> /tmp/demo/buggy.py(4)average()',
       '-> total = s',
       '(Pdb) p s, total',
       '(80, 70)',
       '(Pdb) cl 1',
       'Deleted breakpoint 1 at /tmp/demo/buggy.py:4',
       '(Pdb) n',
       '> /tmp/demo/buggy.py(3)average()',
       '-> for s in scores:',
       '(Pdb) n',
       '> /tmp/demo/buggy.py(4)average()',
       '-> total = s',
       '(Pdb) p total',
       '80',
       '(Pdb) q'], 'A pdb session')}
{note('On the second stop total is 70, not 70 + 0: the line replaces total instead of adding to it. The fix is total += s.', 'tip')}
{table(['pdb command', 'Does'], [
    ['b 4 (break)', 'Stop at line 4. b alone lists breakpoints'], ['c (continue)', 'Run until the next breakpoint'],
    ['n (next)', 'Run the current line, stepping over calls'], ['s (step)', 'Step into a function call'],
    ['p expr, pp expr', 'Print (pretty print) a value'], ['l, ll', 'List the code around here, or the whole function'],
    ['w (where), u, d', 'Show the call stack, move up or down in it'], ['r (return)', 'Run until the current function returns'],
    ['cl 1 (clear)', 'Remove breakpoint 1'], ['q (quit)', 'Stop debugging']])}
{versus('Ways to find a bug', ['', 'print / f"{x=}"', 'logging', 'pdb or an IDE debugger'], [
    ['Set up', 'None', 'Once per project', 'One breakpoint() line'],
    ['See values at any line', 'Only where you printed', 'Only where you logged', 'Yes, and change them'],
    ['Works on a server with nobody watching', 'No', 'Yes', 'No'],
    ['Best for', 'Quick checks', 'Problems in running programs', 'Puzzling bugs you can reproduce']],
    'reproduce the bug first, then use a debugger to watch it happen. Keep logging in place for the bugs you cannot reproduce.')}
{note('assert checks a condition you believe is always true and raises AssertionError if not. Python started with -O skips every assert, so never use assert to check user input. Raise ValueError for that.', 'warn')}
''', kw=['debugging', 'print debugging', 'f-string =', 'assert', '__debug__', '-O', 'pdb', 'breakpoint', 'IDE debugger'])

K.lesson('maths', 'The maths: log volume, rotation and bisecting', f'''
{fxs(fx('Log volume', 'bytes = lines per second &times; bytes per line &times; seconds', '50 lines a second of 200 bytes for a day (86,400 s) is 864,000,000 bytes, about 864 MB.', key=True),
     fx('Disk used by a rotating log', 'max size = (backupCount + 1) &times; maxBytes', 'maxBytes 1 MB with backupCount 4: at most 5 MB, for ever.', key=True),
     fx('Levels shown for a given level L', 'shown = levels with number &ge; L', 'With WARNING (30): WARNING, ERROR and CRITICAL, 3 of 5.'),
     fx('Sampling', 'lines kept = events / N when keeping 1 in N', '1 in 100 of 2,000,000 requests: 20,000 lines.'),
     fx('Bisecting a bug (halving the suspect code)', 'checks = &lceil;log<sub>2</sub> n&rceil;', '64 suspect lines: 6 checks with well placed prints or breakpoints.'),
     fx('Error budget', 'allowed failures = requests &times; (1 &minus; target)', '1,000,000 requests at 99.99 % success allow 100 failures. 120 ERROR lines use 120 % of the budget.'))}
{steps('Worked example: how much disk does a month of logs need?', [
    '50 lines per second &times; 200 bytes = 10,000 bytes per second.',
    'One day: 10,000 &times; 86,400 = 864,000,000 bytes = 864 MB.',
    'Thirty days: 864 MB &times; 30.',
    eq('25,920 MB, about 25.9 GB, unless you rotate and delete old files')])}
''', kw=['log volume', 'storage', 'rotation', 'sampling', 'bisect', 'error budget', 'SLO'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Use logging.basicConfig and the five levels, and debug with print and f"{x=}".</p>',
    '<p>Use named loggers with getLogger(__name__), handlers with their own levels and formatters, %s arguments and logger.exception.</p>',
    '<p>Configure a whole app with dictConfig and rotating files, use pdb and breakpoint() with breakpoints, stepping and the call stack, and use assert correctly.</p>',
    '<p>Design logs for machines: structured JSON lines with request ids, central collection (ELK, Loki, CloudWatch), sampling and error budgets. Use QueueHandler for slow sinks, post mortem debugging with pdb.pm(), and remote or conditional breakpoints.</p>')}
{grow('Log with levels and print debug.', 'Build loggers, handlers and formatters.', 'Configure, debug and run logging in production.')}
''', kw=['beginner', 'expert', 'structured logging', 'JSON logs', 'pdb.pm'])

lc(937, 'Reorder Data in Log Files', 'reorder-data-in-log-files', 'm', 'A sort key that splits two kinds of logs', 'Letter logs come first, sorted by content then identifier. Digit logs keep their order: sorted is stable, so give them all the same key.', r'''
def reorder_log_files(logs):
    def key(log):
        ident, rest = log.split(" ", 1)
        if rest[0].isalpha():
            return (0, rest, ident)
        return (1,)
    return sorted(logs, key=key)
''', [('reorder_log_files(["dig1 8 1 5 1", "let1 art can", "dig2 3 6", "let2 own kit dig", "let3 art zero"])', ['let1 art can', 'let3 art zero', 'let2 own kit dig', 'dig1 8 1 5 1', 'dig2 3 6'])])
lc(1598, 'Crawler Log Folder', 'crawler-log-folder', 'e', 'Track the depth', '"../" goes up one level (never above the top), "./" stays, anything else goes one level down.', r'''
def min_operations(logs):
    depth = 0
    for entry in logs:
        if entry == "../":
            depth = max(0, depth - 1)
        elif entry != "./":
            depth += 1
    return depth
''', [('min_operations(["d1/", "d2/", "../", "d21/", "./"])', 2), ('min_operations(["d1/", "../", "../", "../"])', 0)])
lc(2933, 'High-Access Employees', 'high-access-employees', 'm', 'Group times per person, then a window of 3', 'Turn "hhmm" into minutes, sort each person\'s times, and check whether any 3 in a row fit within 59 minutes.', r'''
def find_high_access_employees(access_times):
    times = {}
    for name, hhmm in access_times:
        minutes = int(hhmm[:2]) * 60 + int(hhmm[2:])
        times.setdefault(name, []).append(minutes)
    result = []
    for name, moments in times.items():
        moments.sort()
        for i in range(2, len(moments)):
            if moments[i] - moments[i - 2] < 60:
                result.append(name)
                break
    return sorted(result)
''', [('find_high_access_employees([["a", "0549"], ["b", "0457"], ["a", "0532"], ["a", "0621"], ["b", "0540"]])', ['a']), ('find_high_access_employees([["cd", "1025"], ["ab", "1025"], ["cd", "1046"], ["cd", "1055"], ["ab", "1124"], ["ab", "1120"]])', ['ab', 'cd'])])
lc(1604, 'Alert Using Same Key-Card Three or More Times in a One Hour Period', 'alert-using-same-key-card-three-or-more-times-in-a-one-hour-period', 'm', 'The same window idea on access logs', 'Group by name, sort the minutes, and alert if times[i] &minus; times[i &minus; 2] is at most 60.', r'''
def alert_names(keyName, keyTime):
    times = {}
    for name, clock in zip(keyName, keyTime):
        hours, minutes = clock.split(":")
        times.setdefault(name, []).append(int(hours) * 60 + int(minutes))
    alerts = []
    for name, moments in times.items():
        moments.sort()
        if any(moments[i] - moments[i - 2] <= 60 for i in range(2, len(moments))):
            alerts.append(name)
    return sorted(alerts)
''', [('alert_names(["daniel", "daniel", "daniel", "luis", "luis", "luis", "luis"], ["10:00", "10:40", "11:00", "09:00", "11:00", "13:00", "15:00"])', ['daniel']), ('alert_names(["alice", "alice", "alice", "bob", "bob", "bob", "bob"], ["12:01", "12:00", "18:00", "21:00", "21:20", "21:30", "23:00"])', ['bob'])])
lc(1817, 'Finding the Users Active Minutes', 'finding-the-users-active-minutes', 'm', 'A set of minutes per user', 'Collect each user\'s different minutes in a set. The size of the set is that user\'s active minutes. Count users per size.', r'''
def finding_users_active_minutes(logs, k):
    minutes = {}
    for user, minute in logs:
        minutes.setdefault(user, set()).add(minute)
    answer = [0] * k
    for active in minutes.values():
        answer[len(active) - 1] += 1
    return answer
''', [('finding_users_active_minutes([[0, 5], [1, 2], [0, 2], [0, 5], [1, 3]], 5)', [0, 2, 0, 0, 0]), ('finding_users_active_minutes([[1, 1], [2, 2], [2, 3]], 4)', [1, 1, 0, 0])])
lc(2747, 'Count Zero Request Servers', 'count-zero-request-servers', 'm', 'Sort logs and queries, slide a window', 'Sort logs by time. Answer queries in time order with two pointers that keep only logs inside [q &minus; x, q] and a count per server.', r'''
def count_servers(n, logs, x, queries):
    logs = sorted(logs, key=lambda log: log[1])
    order = sorted(range(len(queries)), key=lambda i: queries[i])
    count = {}
    answer = [0] * len(queries)
    left = right = 0
    for i in order:
        q = queries[i]
        while right < len(logs) and logs[right][1] <= q:
            server = logs[right][0]
            count[server] = count.get(server, 0) + 1
            right += 1
        while left < right and logs[left][1] < q - x:
            server = logs[left][0]
            count[server] -= 1
            if count[server] == 0:
                del count[server]
            left += 1
        answer[i] = n - len(count)
    return answer
''', [('count_servers(3, [[1, 3], [2, 6], [1, 5]], 5, [10, 11])', [1, 2]), ('count_servers(3, [[2, 4], [2, 1], [1, 2], [3, 1]], 2, [3, 4])', [0, 1])])
lc(1169, 'Invalid Transactions', 'invalid-transactions', 'm', 'Parse, then compare every pair', 'A transaction is invalid above 1000, or when the same name has another one in a different city within 60 minutes.', r'''
def invalid_transactions(transactions):
    parsed = []
    for t in transactions:
        name, time, amount, city = t.split(",")
        parsed.append((name, int(time), int(amount), city))
    result = []
    for i, (name, time, amount, city) in enumerate(parsed):
        bad = amount > 1000
        for other_name, other_time, other_amount, other_city in parsed:
            if other_name == name and other_city != city and abs(other_time - time) <= 60:
                bad = True
        if bad:
            result.append(transactions[i])
    return result
''', [('invalid_transactions(["alice,20,800,mtv", "alice,50,100,beijing"])', ['alice,20,800,mtv', 'alice,50,100,beijing']), ('invalid_transactions(["alice,20,800,mtv", "alice,50,1200,mtv"])', ['alice,50,1200,mtv'])])
lc(609, 'Find Duplicate File in System', 'find-duplicate-file-in-system', 'm', 'Parse lines into a dict by content', 'Each line is a folder then files like name(content). Group full paths by content and keep groups with more than one file.', r'''
def find_duplicate(paths):
    by_content = {}
    for line in paths:
        folder, *files = line.split(" ")
        for entry in files:
            name, content = entry[:-1].split("(")
            by_content.setdefault(content, []).append(folder + "/" + name)
    return [group for group in by_content.values() if len(group) > 1]
''', [('sorted(sorted(g) for g in find_duplicate(["root/a 1.txt(abcd) 2.txt(efgh)", "root/c 3.txt(abcd)", "root/c/d 4.txt(efgh)", "root 4.txt(efgh)"]))', [['root/4.txt', 'root/a/2.txt', 'root/c/d/4.txt'], ['root/a/1.txt', 'root/c/3.txt']])])
lc(388, 'Longest Absolute File Path', 'longest-absolute-file-path', 'm', 'A stack of path lengths by depth', 'The number of tabs is the depth. Keep the total length of the path at each depth. A name with a dot is a file.', r'''
def length_longest_path(text):
    length_at = {0: 0}
    best = 0
    for line in text.split("\n"):
        name = line.lstrip("\t")
        depth = len(line) - len(name)
        if "." in name:
            best = max(best, length_at[depth] + len(name))
        else:
            length_at[depth + 1] = length_at[depth] + len(name) + 1
    return best
''', [('length_longest_path("dir\\n\\tsubdir1\\n\\tsubdir2\\n\\t\\tfile.ext")', 20), ('length_longest_path("a")', 0)])
lc(165, 'Compare Version Numbers', 'compare-version-numbers', 'm', 'Compare number by number', 'Split on dots, turn each part into an int (so 01 equals 1) and treat missing parts as 0.', r'''
from itertools import zip_longest


def compare_version(version1, version2):
    parts1 = [int(p) for p in version1.split(".")]
    parts2 = [int(p) for p in version2.split(".")]
    for a, b in zip_longest(parts1, parts2, fillvalue=0):
        if a != b:
            return 1 if a > b else -1
    return 0
''', [('compare_version("1.2", "1.10")', -1), ('compare_version("1.01", "1.001")', 0), ('compare_version("1.0", "1.0.0.0")', 0), ('compare_version("7.5.2.4", "7.5.3")', -1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>These problems are log analysis: sorting log lines, finding three key card swipes inside an hour, active minutes per user, servers with no requests in a time window, and parsing file system listings. It is exactly the code you write to find problems in real logs.</p>'), kw=['LeetCode', 'logs', 'sliding window', 'parsing', 'sorting', 'time windows'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Five levels: DEBUG 10, INFO 20, WARNING 30 (the default), ERROR 40, CRITICAL 50.',
    'basicConfig for small scripts. Named loggers with getLogger(__name__), handlers with their own levels and formatters for real programs.',
    'Records pass the logger level, go to its handlers (each filters again), then propagate to parent loggers.',
    'Pass values as %s arguments so text is only built when needed. Use logger.exception inside except. Never log secrets.',
    'Configure once with dictConfig. Rotate files so logs do not fill the disk. Libraries only call getLogger.',
    'Debug with f"{x=}", assert for things that must always be true (off with -O), and pdb or breakpoint() to stop and look.'],
    'Step 4 is about speed: complexity and the data structures in collections, heapq and bisect.')}
{files('Three tasks: decide whether a level is shown, capture the log lines of a function, and summarise a log file.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is the default level of the root logger?', ['DEBUG', 'INFO', 'WARNING', 'ERROR'], 2, 'Only problems by default.', 'Without configuration only WARNING and above are shown.')
K.quiz('e', 'Which level is the most serious?', ['ERROR', 'WARNING', 'CRITICAL', 'INFO'], 2, 'The highest number.', 'CRITICAL is 50.')
K.quiz('e', 'Which pdb command runs until the next breakpoint?', ['n', 's', 'c', 'q'], 2, 'continue.', 'c (continue) runs on until a breakpoint is hit.')
K.quiz('m', 'Why use logger.info("total %s", total) instead of an f-string?', ['f-strings are not allowed', 'The text is only built if the message passes the level checks', 'It is shorter', 'It prints in colour'], 1, 'Lazy formatting.', 'An f-string is built before the call, even if the message is dropped.')
K.quiz('m', 'A logger has level DEBUG and its console handler has level WARNING. Where does an INFO message go?', ['To the console', 'Nowhere through that handler: it passes the logger but the handler drops it', 'An error is raised', 'To stderr'], 1, 'Two checks.', 'Logger and handler each filter by their own level.')
K.quiz('m', 'What does logger.exception("failed") do inside an except block?', ['Raises the error again', 'Logs at ERROR level with the traceback attached', 'Logs at CRITICAL', 'Ignores the error'], 1, 'Traceback included.', 'It is logger.error with exc_info=True.')
K.quiz('m', 'What is the parent of logging.getLogger("shop.cart") once a "shop" logger exists?', ['root', 'shop', 'cart', 'None'], 1, 'Dots make a tree.', 'Records propagate from shop.cart to shop and then to root.')
K.quiz('m', 'Should a library call logging.basicConfig?', ['Yes, always', 'No, only the application should configure logging', 'Only for errors', 'Only in tests'], 1, 'Who decides.', 'A library only gets its logger. The app decides levels and handlers.')
K.quiz('h', 'What happens to assert statements when Python runs with -O?', ['They become warnings', 'They are removed and never run', 'They run twice', 'They raise SyntaxError'], 1, '__debug__ is False.', 'So never use assert to validate user input.')
K.quiz('h', 'RotatingFileHandler(path, maxBytes=10_000_000, backupCount=3). What is the most disk it uses?', ['10 MB', '30 MB', '40 MB', 'No limit'], 2, '(backupCount + 1) &times; maxBytes.', 'The current file plus 3 old ones: 4 &times; 10 MB.')
K.quiz('h', 'What does print(f"{total=}") print when total is 80?', ['80', 'total=80', '{total=}', 'total = 80'], 1, 'Self documenting f-string.', 'The = after a name prints the expression and its value.')
K.quiz('x', 'In the style of a Google SRE interview: 1,000,000 requests with a 99.99 % success target produced 120 errors. What share of the error budget was used?', ['12 %', '100 %', '120 %', '0.012 %'], 2, 'Budget = requests &times; 0.0001.', 'The budget is 100 failures. 120 / 100 = 120 %, so the target was missed.')
K.quiz('x', 'In the style of a CMU 15-440 exam: why do distributed systems log structured JSON lines with a request id?', ['They are smaller', 'Machines can search and join the lines of one request across many servers', 'JSON is faster to write', 'Text logs are not allowed'], 1, 'Following one request.', 'A shared id ties together everything one request did on every service.')

K.calc('e', 'How many of the 5 standard levels are shown when the level is WARNING?', '3', 'Number &ge; 30.', ['WARNING 30, ERROR 40, CRITICAL 50 pass.', 'DEBUG and INFO do not.', eq('3')], check=3)
K.calc('e', 'RotatingFileHandler with maxBytes 1 MB and backupCount 4. What is the most disk in MB?', '5', '(backupCount + 1) &times; maxBytes.', ['backupCount + 1 = 5 files.', 'Each at most 1 MB.', eq('5 MB')], check=5)
K.calc('e', 'What number is the INFO level?', '20', 'DEBUG is 10.', ['DEBUG = 10.', 'Each level adds 10.', eq('INFO = 20')], check=20)
K.calc('m', '50 log lines a second, 200 bytes each, for one day (86,400 s). How many MB (10<sup>6</sup> bytes)?', '864', 'Lines &times; bytes &times; seconds.', ['50 &times; 200 = 10,000 bytes a second.', '10,000 &times; 86,400 = 864,000,000.', eq('864 MB')], check=50 * 200 * 86400 / 10 ** 6)
K.calc('m', 'Halving the suspect code each time, how many checks find a bug among 64 lines?', '6', 'log<sub>2</sub> 64.', ['2<sup>6</sup> = 64.', 'Each check halves the lines.', eq('6 checks')], check=6)
K.calc('m', 'Keeping 1 log line in 100, how many lines do 2,000,000 requests give?', '20000', 'Events / N.', ['2,000,000 / 100.', 'One line per kept request.', eq('20,000')], check=2_000_000 // 100)
K.calc('m', 'A debug f-string costs 2 microseconds to build and runs 1,000,000 times while DEBUG is off. How many seconds are wasted?', '2', 'Calls &times; cost.', ['1,000,000 &times; 2 &micro;s = 2,000,000 &micro;s.', '1 s = 1,000,000 &micro;s.', eq('2 s, saved by using %s arguments')], check=1_000_000 * 2 / 1_000_000)
K.calc('h', '864 MB of logs a day are kept for 30 days. How many GB (1000 MB) is that?', '25.92', 'Daily &times; days.', ['864 &times; 30 = 25,920 MB.', 'Divide by 1000.', eq('25.92 GB')], check=864 * 30 / 1000)
K.calc('h', 'How many ancestor loggers does "a.b.c" have, counting root?', '3', 'Walk up the dots.', ['a.b is the parent.', 'Then a, then root.', eq('3')], check=3)
K.calc('x', 'In the style of a Google SRE interview: 1,000,000 requests, a 99.99 % success target, and 120 ERROR lines (one per failed request). What percent of the error budget is used?', '120', 'Failures over allowed failures.', ['Allowed: 1,000,000 &times; 0.0001 = 100.', 'Actual: 120.', eq('120 / 100 = 120 %')], check=round(120 / (1_000_000 * (1 - 0.9999)) * 100))

K.assign('shown', 'e', 'Is this message shown?',
         '<p>Write <code>is_shown(logger_level, message_level)</code> where both are level names like "WARNING". Return True if a message at message_level passes a logger at logger_level. Use the numbers from the logging module (getattr(logging, name)) instead of writing your own table.</p>',
         '''
import logging


def is_shown(logger_level, message_level):
    return logger_level == message_level
''', [('is_shown("WARNING", "ERROR")', True), ('is_shown("INFO", "DEBUG")', False), ('is_shown("DEBUG", "DEBUG")', True), ('[is_shown("ERROR", m) for m in ["INFO", "WARNING", "CRITICAL"]]', [False, False, True])],
         '''
import logging


def is_shown(logger_level, message_level):
    return getattr(logging, message_level) >= getattr(logging, logger_level)
''', 'getattr(logging, "WARNING") is 30. A message passes when its number is at least the logger level number.', '<p>Comparing numbers is exactly what Logger.isEnabledFor does inside the logging module.</p>')
K.assign('capture', 'm', 'Capture the log lines of a function',
         '<p>Write <code>log_lines(func, *args)</code>. It attaches a handler to the logger named "app" (level DEBUG), runs func(*args), removes the handler again (even if func raises), and returns (result, lines) where lines are strings like "DEBUG:dividing 6 by 3". divide is a sample function that logs.</p>',
         '''
import logging


def log_lines(func, *args):
    return func(*args), []


def divide(a, b):
    logger = logging.getLogger("app")
    logger.debug("dividing %s by %s", a, b)
    if b == 0:
        logger.error("cannot divide by zero")
        return None
    return a / b
''', [('log_lines(divide, 6, 3)', [2.0, ['DEBUG:dividing 6 by 3']]), ('log_lines(divide, 1, 0)', [None, ['DEBUG:dividing 1 by 0', 'ERROR:cannot divide by zero']]), ('(log_lines(divide, 1, 1), len(logging.getLogger("app").handlers))[1]', 0)],
         '''
import logging


class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(record.levelname + ":" + record.getMessage())


def log_lines(func, *args):
    logger = logging.getLogger("app")
    handler = ListHandler()
    old_level = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    try:
        result = func(*args)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)
    return result, handler.lines


def divide(a, b):
    logger = logging.getLogger("app")
    logger.debug("dividing %s by %s", a, b)
    if b == 0:
        logger.error("cannot divide by zero")
        return None
    return a / b
''', 'Subclass logging.Handler and append in emit. record.getMessage() fills in the %s arguments. Remove the handler in a finally block.', '<p>pytest has this built in as the caplog fixture, and unittest has self.assertLogs. Both work like this ListHandler.</p>')
K.assign('report', 'h', 'Summarise a log file',
         '<p>Lines look like "2026-11-07 10:00:01 ERROR shop.cart: payment failed". Write <code>error_report(lines)</code> that returns a dict with "errors" (how many ERROR lines), "warnings" (how many WARNING lines), "by_logger" (a dict of logger name to its ERROR count) and "first" (the time and message of the first ERROR, like "10:00:01 payment failed", or None). Skip lines that do not have all the parts.</p>',
         '''
def error_report(lines):
    errors = 0
    for line in lines:
        if "ERROR" in line:
            errors += 1
    return {"errors": errors, "warnings": 0, "by_logger": {}, "first": None}


SAMPLE = [
    "2026-11-07 10:00:00 INFO shop.cart: cart opened",
    "2026-11-07 10:00:01 ERROR shop.pay: payment failed",
    "broken line",
    "2026-11-07 10:00:05 WARNING shop.cart: stock low",
    "2026-11-07 10:00:09 ERROR shop.pay: card declined",
    "2026-11-07 10:01:00 ERROR shop.cart: ERROR in totals",
]
''', [('error_report(SAMPLE)', {'errors': 3, 'warnings': 1, 'by_logger': {'shop.pay': 2, 'shop.cart': 1}, 'first': '10:00:01 payment failed'}), ('error_report([])', {'errors': 0, 'warnings': 0, 'by_logger': {}, 'first': None}), ('error_report(["2026-11-07 09:00:00 INFO a: ERROR mentioned"])["errors"]', 0)],
         '''
def error_report(lines):
    errors = 0
    warnings = 0
    by_logger = {}
    first = None
    for line in lines:
        parts = line.split(" ", 4)
        if len(parts) < 5 or not parts[3].endswith(":"):
            continue
        date, time, level, name, message = parts
        name = name[:-1]
        if level == "ERROR":
            errors += 1
            by_logger[name] = by_logger.get(name, 0) + 1
            if first is None:
                first = time + " " + message
        elif level == "WARNING":
            warnings += 1
    return {"errors": errors, "warnings": warnings, "by_logger": by_logger, "first": first}


SAMPLE = [
    "2026-11-07 10:00:00 INFO shop.cart: cart opened",
    "2026-11-07 10:00:01 ERROR shop.pay: payment failed",
    "broken line",
    "2026-11-07 10:00:05 WARNING shop.cart: stock low",
    "2026-11-07 10:00:09 ERROR shop.pay: card declined",
    "2026-11-07 10:01:00 ERROR shop.cart: ERROR in totals",
]
''', 'split(" ", 4) gives date, time, level, "name:" and the message. Check the LEVEL field, not whether the word ERROR appears somewhere in the line.', '<p>Searching for the word ERROR anywhere counts a line whose message happens to say ERROR. Parsing the fields is the reliable way, and the reason structured (JSON) logs are popular.</p>')

K.must('Levels', 'DEBUG 10, INFO 20, WARNING 30 (default), ERROR 40, CRITICAL 50. basicConfig(level=, format=, stream=, force=True).')
K.must('Parts', 'getLogger(__name__), logger and handler levels, Formatter fields (%(asctime)s %(levelname)s %(name)s %(message)s), propagate to parents.')
K.must('Habits', 'logger.info("x %s", x) not f-strings, logger.exception in except, no secrets in logs, libraries never configure logging.')
K.must('Configuration', 'dictConfig once at start, RotatingFileHandler (maxBytes, backupCount), TimedRotatingFileHandler, QueueHandler.')
K.must('Debugging', 'f"{x=}", assert (removed by -O, not for input checks), breakpoint() and python -m pdb: b, c, n, s, p, l, w, q.')

T = K.topic(
    slug='py-logging', topic='py-logging', step=(3, 'Professional code: style, testing and logging', 'py-a3', 'Write code others can read, prove it works with tests, and find problems fast with logging and debugging.', 'Advanced'),
    title='Logging and debugging', short='Logging and debugging', badge='3.3', minutes=70,
    lead='Know what your program is doing and find out why it went wrong. Learn the five log levels, basicConfig, loggers, handlers and formatters, the logger tree, good logging habits, dictConfig and rotating files, and debugging with print, assert and the pdb debugger.',
    desc='logging levels, basicConfig, getLogger and the logger hierarchy, propagate, StreamHandler, FileHandler, Formatter fields, lazy %s formatting, logger.exception, isEnabledFor, logging.config.dictConfig, RotatingFileHandler, TimedRotatingFileHandler, QueueHandler, print versus logging, f-string self documenting expressions, assert and -O, pdb and breakpoint(), log volume, error budgets.',
    summary='log levels, loggers, handlers, formatters, habits, dictConfig, rotation, print, assert and pdb debugging.',
    keywords=['logging', 'logger', 'handler', 'formatter', 'basicConfig', 'dictConfig', 'RotatingFileHandler', 'pdb', 'breakpoint', 'assert', 'debugging'],
    recap='<p>Log with levels through named loggers, configure once, and when something breaks, reproduce it and watch it with a debugger.</p>',
    added='2026-11-07', leet=leet_items())
