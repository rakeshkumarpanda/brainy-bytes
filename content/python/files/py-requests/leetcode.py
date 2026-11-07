# 2.1 Calling web APIs with requests
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== 2418. Sort the People (Easy)
# https://leetcode.com/problems/sort-the-people/
# Pattern: Sort pairs by one field
# Idea: Like sorting API records by a field. Zip names with heights and sort by height, largest
# first.

def sort_people(names, heights):
    pairs = sorted(zip(heights, names), reverse=True)
    return [name for height, name in pairs]


# ================================================================== 1854. Maximum Population Year (Easy)
# https://leetcode.com/problems/maximum-population-year/
# Pattern: Count people alive in each year
# Idea: Records with a start and an end, like user sessions in logs. Years are only 1950 to 2050, so
# count each year directly.

def maximum_population(logs):
    alive = [0] * 101
    for birth, death in logs:
        for year in range(birth, death):
            alive[year - 1950] += 1
    best = max(alive)
    return alive.index(best) + 1950


# ================================================================== 1700. Number of Students Unable to Eat Lunch (Easy)
# https://leetcode.com/problems/number-of-students-unable-to-eat-lunch/
# Pattern: Only the counts matter
# Idea: A queue of requests waiting for a matching resource. Count how many want each kind, then
# serve the stack until no one wants the top item.

def count_students(students, sandwiches):
    wants = [students.count(0), students.count(1)]
    for sandwich in sandwiches:
        if wants[sandwich] == 0:
            break
        wants[sandwich] -= 1
    return wants[0] + wants[1]


# ================================================================== 2456. Most Popular Video Creator (Medium)
# https://leetcode.com/problems/most-popular-video-creator/
# Pattern: Group records by creator
# Idea: Typical API analytics: total views per creator, and each creator's best video (most views,
# then the smallest id).

def most_popular_creator(creators, ids, views):
    total = {}
    best = {}
    for creator, video, count in zip(creators, ids, views):
        total[creator] = total.get(creator, 0) + count
        if creator not in best or (-count, video) < (-best[creator][1], best[creator][0]):
            best[creator] = (video, count)
    top = max(total.values())
    return sorted([creator, best[creator][0]] for creator in total if total[creator] == top)


# ================================================================== 1366. Rank Teams by Votes (Medium)
# https://leetcode.com/problems/rank-teams-by-votes/
# Pattern: Sort by a tuple of vote counts
# Idea: Count how often each team gets each place. Sort by the counts, most first, and by the letter
# on a tie.

def rank_teams(votes):
    places = len(votes[0])
    counts = {team: [0] * places for team in votes[0]}
    for vote in votes:
        for place, team in enumerate(vote):
            counts[team][place] += 1
    ranked = sorted(counts, key=lambda team: ([-c for c in counts[team]], team))
    return "".join(ranked)


# ================================================================== 355. Design Twitter (Medium)
# https://leetcode.com/problems/design-twitter/
# Pattern: Dicts of lists and sets, heapq.nlargest
# Idea: A small social API. Store each user's tweets with a counter as the time. The feed is the 10
# newest tweets of the user and the people they follow.

import heapq
from itertools import count


class Twitter:
    def __init__(self):
        self.clock = count()
        self.tweets = {}
        self.follows = {}

    def postTweet(self, userId, tweetId):
        self.tweets.setdefault(userId, []).append((next(self.clock), tweetId))

    def getNewsFeed(self, userId):
        people = self.follows.get(userId, set()) | {userId}
        candidates = []
        for person in people:
            candidates.extend(self.tweets.get(person, [])[-10:])
        newest = heapq.nlargest(10, candidates)
        return [tweet_id for time, tweet_id in newest]

    def follow(self, followerId, followeeId):
        self.follows.setdefault(followerId, set()).add(followeeId)

    def unfollow(self, followerId, followeeId):
        self.follows.get(followerId, set()).discard(followeeId)


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 1348. Tweet Counts Per Frequency (Medium)
# https://leetcode.com/problems/tweet-counts-per-frequency/
# Pattern: Put each time into a bucket
# Idea: API dashboards count events per minute, hour or day. The bucket of a time t is (t − start)
# // size.

class TweetCounts:
    SIZE = {"minute": 60, "hour": 3600, "day": 86400}

    def __init__(self):
        self.times = {}

    def recordTweet(self, tweetName, time):
        self.times.setdefault(tweetName, []).append(time)

    def getTweetCountsPerFrequency(self, freq, tweetName, startTime, endTime):
        size = self.SIZE[freq]
        counts = [0] * ((endTime - startTime) // size + 1)
        for t in self.times.get(tweetName, []):
            if startTime <= t <= endTime:
                counts[(t - startTime) // size] += 1
        return counts


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 1606. Find Servers That Handled Most Number of Requests (Hard)
# https://leetcode.com/problems/find-servers-that-handled-most-number-of-requests/
# Pattern: Two heaps: busy servers and free servers
# Idea: A load balancer. Request i prefers server i % k, or the next free one after it. Store a free
# server j as i + (j − i) % k so the smallest number in the heap is the right server.

import heapq


def busiest_servers(k, arrival, load):
    handled = [0] * k
    busy = []
    free = list(range(k))
    for i, (start, length) in enumerate(zip(arrival, load)):
        while busy and busy[0][0] <= start:
            finish, server = heapq.heappop(busy)
            heapq.heappush(free, i + (server - i) % k)
        if free:
            server = heapq.heappop(free) % k
            handled[server] += 1
            heapq.heappush(busy, (start + length, server))
    most = max(handled)
    return [server for server in range(k) if handled[server] == most]


# ================================================================== 2102. Sequentially Ordinal Rank Tracker (Hard)
# https://leetcode.com/problems/sequentially-ordinal-rank-tracker/
# Pattern: Two heaps split at the i-th best
# Idea: Keep the places already returned in one heap with the worst on top, and the rest in another
# with the best on top. get() moves one place across.

import heapq


class Worst:
    """Orders places so the WORST comes first: a lower score, then the later name."""

    def __init__(self, score, name):
        self.score = score
        self.name = name

    def __lt__(self, other):
        if self.score != other.score:
            return self.score < other.score
        return self.name > other.name


class SORTracker:
    def __init__(self):
        self.best = []
        self.rest = []

    def add(self, name, score):
        heapq.heappush(self.best, Worst(score, name))
        worst = heapq.heappop(self.best)
        heapq.heappush(self.rest, (-worst.score, worst.name))

    def get(self):
        score, name = heapq.heappop(self.rest)
        heapq.heappush(self.best, Worst(-score, name))
        return name


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


# ================================================================== 352. Data Stream as Disjoint Intervals (Hard)
# https://leetcode.com/problems/data-stream-as-disjoint-intervals/
# Pattern: A set of numbers, joined into runs when asked
# Idea: Like tracking which parts of a file have arrived. Keep the numbers in a set, and on
# getIntervals walk them in order and join neighbours into ranges.

class SummaryRanges:
    def __init__(self):
        self.numbers = set()

    def addNum(self, value):
        self.numbers.add(value)

    def getIntervals(self):
        result = []
        for number in sorted(self.numbers):
            if result and number == result[-1][1] + 1:
                result[-1][1] = number
            else:
                result.append([number, number])
        return result


def play(cls, ops, args):
    """Run LeetCode style commands: make the object, then call each method by its name."""
    obj = cls(*args[0])
    results = [None]
    for name, arg in zip(ops[1:], args[1:]):
        results.append(getattr(obj, name)(*arg))
    return results


if __name__ == "__main__":
    results = []
    results.append(check("2418. Sort the People", [('sort_people(["Mary", "John", "Emma"], [180, 165, 170])', ['Mary', 'Emma', 'John']), ('sort_people(["Alice", "Bob", "Bob"], [155, 185, 150])', ['Bob', 'Alice', 'Bob'])]))
    results.append(check("1854. Maximum Population Year", [('maximum_population([[1993, 1999], [2000, 2010]])', 1993), ('maximum_population([[1950, 1961], [1960, 1971], [1970, 1981]])', 1960)]))
    results.append(check("1700. Number of Students Unable to Eat Lunch", [('count_students([1, 1, 0, 0], [0, 1, 0, 1])', 0), ('count_students([1, 1, 1, 0, 0, 1], [1, 0, 0, 0, 1, 1])', 3)]))
    results.append(check("2456. Most Popular Video Creator", [('most_popular_creator(["alice", "bob", "alice", "chris"], ["one", "two", "three", "four"], [5, 10, 5, 4])', [['alice', 'one'], ['bob', 'two']]), ('most_popular_creator(["alice", "alice", "alice"], ["a", "b", "c"], [1, 2, 2])', [['alice', 'b']])]))
    results.append(check("1366. Rank Teams by Votes", [('rank_teams(["ABC", "ACB", "ABC", "ACB", "ACB"])', 'ACB'), ('rank_teams(["WXYZ", "XYZW"])', 'XWYZ'), ('rank_teams(["ZMNAGUEDSJYLBOPHRQICWFXTVK"])', 'ZMNAGUEDSJYLBOPHRQICWFXTVK')]))
    results.append(check("355. Design Twitter", [('play(Twitter, ["Twitter", "postTweet", "getNewsFeed", "follow", "postTweet", "getNewsFeed", "unfollow", "getNewsFeed"], [[], [1, 5], [1], [1, 2], [2, 6], [1], [1, 2], [1]])', [None, None, [5], None, None, [6, 5], None, [5]])]))
    results.append(check("1348. Tweet Counts Per Frequency", [('play(TweetCounts, ["TweetCounts", "recordTweet", "recordTweet", "recordTweet", "getTweetCountsPerFrequency", "getTweetCountsPerFrequency", "recordTweet", "getTweetCountsPerFrequency"], [[], ["tweet3", 0], ["tweet3", 60], ["tweet3", 10], ["minute", "tweet3", 0, 59], ["minute", "tweet3", 0, 60], ["tweet3", 120], ["hour", "tweet3", 0, 210]])', [None, None, None, None, [2], [2, 1], None, [4]])]))
    results.append(check("1606. Find Servers That Handled Most Number of Requests", [('busiest_servers(3, [1, 2, 3, 4, 5], [5, 2, 3, 3, 3])', [1]), ('busiest_servers(3, [1, 2, 3, 4], [1, 2, 1, 2])', [0]), ('busiest_servers(3, [1, 2, 3], [10, 12, 11])', [0, 1, 2])]))
    results.append(check("2102. Sequentially Ordinal Rank Tracker", [('play(SORTracker, ["SORTracker", "add", "add", "get", "add", "get", "add", "get", "add", "get", "add", "get", "get"], [[], ["bradford", 2], ["branford", 3], [], ["alps", 2], [], ["orland", 2], [], ["orangered", 10], [], ["alpine", 2], [], []])', [None, None, None, 'branford', None, 'alps', None, 'bradford', None, 'bradford', None, 'bradford', 'orland'])]))
    results.append(check("352. Data Stream as Disjoint Intervals", [('play(SummaryRanges, ["SummaryRanges", "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals"], [[], [1], [], [3], [], [7], [], [2], [], [6], []])', [None, None, [[1, 1]], None, [[1, 1], [3, 3]], None, [[1, 1], [3, 3], [7, 7]], None, [[1, 3], [7, 7]], None, [[1, 3], [6, 7]]])]))
    if all(results):
        print("Every solution passes its tests.")
