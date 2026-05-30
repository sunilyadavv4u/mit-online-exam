"""MIT DSA coding question bank (original problems, LeetCode/HackerRank-style patterns).

Each problem uses stdin/stdout for the Python sandbox runner.
Tags include a stable `dsa_key:<slug>` for idempotent seeding.
"""
from __future__ import annotations

from apps.questions.models import CodingLanguage, DifficultyLevel

_STDIN_HINT = (
    'Read input from stdin and write the answer to stdout (one line unless noted). '
    'No extra debug prints.'
)

_STARTER = """import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    # TODO: solve using data
    pass

if __name__ == '__main__':
    main()
"""


def _tc(inp: str, out: str, hidden: bool = False) -> dict:
    return {'input_data': inp, 'expected_output': out, 'is_hidden': hidden}


def _problem(
    key: str,
    title: str,
    difficulty: str,
    marks: int,
    text: str,
    starter_code: str,
    test_cases: list[dict],
    extra_tags: str = '',
) -> dict:
    diff = {
        'easy': DifficultyLevel.EASY,
        'medium': DifficultyLevel.MEDIUM,
        'hard': DifficultyLevel.HARD,
    }[difficulty]
    tags = f'dsa_key:{key},dsa,{difficulty}'
    if extra_tags:
        tags += f',{extra_tags}'
    return {
        'key': key,
        'title': title,
        'difficulty': diff,
        'marks': marks,
        'tags': tags,
        'text': text,
        'coding_language': CodingLanguage.PYTHON,
        'starter_code': starter_code,
        'test_cases': test_cases,
    }


DSA_PROBLEMS: list[dict] = [
    _problem(
        'two-sum-indices',
        'Pair With Target Sum (Indices)',
        'easy', 10,
        f"""Find two distinct indices `i j` (0-based, space-separated, `i < j`) such that
`nums[i] + nums[j] = target`.

Input format:
Line 1: integer `n`
Line 2: `n` integers
Line 3: target integer

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('4\n2 7 11 15\n9', '0 1'),
            _tc('3\n3 2 4\n6', '1 2', True),
            _tc('2\n3 3\n6', '0 1', True),
            _tc('5\n1 5 3 7 2\n10', '1 3', True),
        ],
        'array,hash-map',
    ),
    _problem(
        'array-sum',
        'Sum of Array Elements',
        'easy', 5,
        f"""Given `n` then `n` integers on the next line, print their sum.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('5\n1 2 3 4 5', '15'),
            _tc('1\n42', '42', True),
            _tc('4\n-1 2 -3 4', '2', True),
            _tc('3\n1000000 1000000 1000000', '3000000', True),
        ],
    ),
    _problem(
        'max-element',
        'Maximum in Array',
        'easy', 5,
        f"""Print the maximum value in the array.

Input: `n` then `n` integers.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('3\n1 9 3', '9'),
            _tc('5\n-5 -1 -9 -2 -3', '-1', True),
            _tc('1\n0', '0', True),
            _tc('4\n10 10 9 10', '10', True),
        ],
    ),
    _problem(
        'missing-number',
        'Missing Number in 1..n',
        'easy', 8,
        f"""Array contains `n` distinct integers from `1` to `n+1` except one missing value.
Print the missing number.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('3\n1 2 4', '3'),
            _tc('2\n1 3', '2', True),
            _tc('4\n2 3 1 5', '4', True),
            _tc('1\n2', '1', True),
        ],
    ),
    _problem(
        'reverse-string',
        'Reverse a String',
        'easy', 5,
        f"""Print the reverse of the given string (single line input).

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('hello', 'olleh'),
            _tc('a', 'a', True),
            _tc('Mewati', 'itaweM', True),
            _tc('racecar', 'racecar', True),
        ],
    ),
    _problem(
        'palindrome-check',
        'Palindrome Check',
        'easy', 5,
        f"""Print `YES` if the string is a palindrome ignoring case, else `NO`.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('Level', 'YES'),
            _tc('hello', 'NO', True),
            _tc('a', 'YES', True),
            _tc('Noon', 'YES', True),
        ],
    ),
    _problem(
        'valid-parentheses',
        'Valid Parentheses',
        'easy', 8,
        f"""String contains only `()[]{{}}`. Print `YES` if valid, else `NO`.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('()[]{}', 'YES'),
            _tc('(]', 'NO', True),
            _tc('([)]', 'NO', True),
            _tc('{[]}', 'YES', True),
        ],
        'stack,string',
    ),
    _problem(
        'count-vowels',
        'Count Vowels',
        'easy', 5,
        f"""Count vowels `aeiouAEIOU` in the string and print the count.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('Mewati Institute', '6'),
            _tc('xyz', '0', True),
            _tc('AEIOU', '5', True),
            _tc('bba', '0', True),
        ],
    ),
    _problem(
        'fibonacci-n',
        'Nth Fibonacci Number',
        'easy', 8,
        f"""Print F(n) where F(0)=0, F(1)=1. Input: single integer `n` (0 <= n <= 30).

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('10', '55'),
            _tc('0', '0', True),
            _tc('1', '1', True),
            _tc('20', '6765', True),
        ],
        'dp,math',
    ),
    _problem(
        'gcd-two',
        'GCD of Two Numbers',
        'easy', 5,
        f"""Two integers per line (two lines). Print their greatest common divisor.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('12\n18', '6'),
            _tc('7\n13', '1', True),
            _tc('0\n5', '5', True),
            _tc('270\n192', '6', True),
        ],
        'math',
    ),
    _problem(
        'factorial-n',
        'Factorial',
        'easy', 5,
        f"""Print n! for n <= 20.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('5', '120'),
            _tc('0', '1', True),
            _tc('10', '3628800', True),
            _tc('1', '1', True),
        ],
    ),
    _problem(
        'linear-search',
        'First Index of Target',
        'easy', 5,
        f"""Line1: n, Line2: n ints, Line3: target. Print first index or -1.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('5\n2 3 5 5 6\n5', '2'),
            _tc('3\n1 2 3\n4', '-1', True),
            _tc('1\n9\n9', '0', True),
            _tc('4\n7 7 7 7\n7', '0', True),
        ],
    ),
    _problem(
        'even-odd',
        'Even or Odd',
        'easy', 3,
        f"""Print `EVEN` or `ODD` for the integer input.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('4', 'EVEN'),
            _tc('7', 'ODD', True),
            _tc('0', 'EVEN', True),
            _tc('-3', 'ODD', True),
        ],
    ),
    _problem(
        'climbing-stairs',
        'Climbing Stairs',
        'medium', 10,
        f"""You can climb 1 or 2 steps. Given `n` steps, print number of distinct ways.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('3', '3'),
            _tc('1', '1', True),
            _tc('5', '8', True),
            _tc('10', '89', True),
        ],
        'dp',
    ),
    _problem(
        'max-subarray-sum',
        'Maximum Subarray Sum',
        'medium', 10,
        f"""Print maximum sum of any contiguous subarray (Kadane).

Line1: n, Line2: n integers (may be negative).

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('9\n-2 1 -3 4 -1 2 1 -5 4', '6'),
            _tc('1\n-5', '-5', True),
            _tc('5\n5 4 -1 7 8', '23', True),
            _tc('3\n-1 -2 -3', '-1', True),
        ],
        'array,dp',
    ),
    _problem(
        'binary-search',
        'Binary Search Index',
        'medium', 8,
        f"""Sorted array. Print index of target or -1.

Line1: n, Line2: sorted ints, Line3: target.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('6\n-1 0 3 5 9 12\n9', '4'),
            _tc('4\n1 2 3 4\n5', '-1', True),
            _tc('1\n5\n5', '0', True),
            _tc('7\n1 3 5 7 9 11 13\n7', '3', True),
        ],
    ),
    _problem(
        'coin-change',
        'Minimum Coin Change',
        'medium', 12,
        f"""Line1: amount, Line2: k, Line3: k coin denominations (unlimited supply).
Print minimum coins to make amount, or -1 if impossible.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('11\n3\n1 2 5', '3'),
            _tc('3\n1\n2', '-1', True),
            _tc('0\n2\n1 2', '0', True),
            _tc('100\n3\n1 5 10', '10', True),
        ],
        'dp',
    ),
    _problem(
        'longest-substring-no-repeat',
        'Longest Substring Without Repeating',
        'medium', 12,
        f"""Print length of longest substring without repeating characters.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('abcabcbb', '3'),
            _tc('bbbbb', '1', True),
            _tc('pwwkew', '3', True),
            _tc('', '0', True),
        ],
        'string,sliding-window',
    ),
    _problem(
        'rotate-array-k',
        'Rotate Array Right by K',
        'medium', 10,
        f"""Line1: n, Line2: n ints, Line3: k. Right-rotate and print space-separated result.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('7\n1 2 3 4 5 6 7\n3', '5 6 7 1 2 3 4'),
            _tc('4\n1 2 3 4\n0', '1 2 3 4', True),
            _tc('1\n1\n2', '1', True),
            _tc('5\n1 2 3 4 5\n2', '4 5 1 2 3', True),
        ],
    ),
    _problem(
        'product-except-self',
        'Product Except Self',
        'medium', 12,
        f"""Line1: n, Line2: n integers. Print products except self (space-separated).

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('4\n1 2 3 4', '24 12 8 6'),
            _tc('2\n0 0', '0 0', True),
            _tc('3\n-1 1 0', '0 0 -1', True),
            _tc('5\n2 3 4 5 1', '60 40 30 24 120', True),
        ],
    ),
    _problem(
        'merge-intervals-count',
        'Merge Overlapping Intervals Count',
        'medium', 10,
        f"""Line1: n intervals as `start end` pairs on next n lines.
Merge overlaps and print count of merged intervals.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('4\n1 3\n2 6\n8 10\n15 18', '3'),
            _tc('2\n1 4\n4 5', '1', True),
            _tc('1\n1 1', '1', True),
            _tc('3\n1 2\n2 3\n3 4', '1', True),
        ],
        'intervals',
    ),
    _problem(
        'kth-largest',
        'Kth Largest Element',
        'medium', 10,
        f"""Line1: n, Line2: n ints, Line3: k (1-based largest). Print the value.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('6\n3 2 1 5 6 4\n2', '5'),
            _tc('1\n1\n1', '1', True),
            _tc('5\n5 5 5 5 5\n3', '5', True),
            _tc('7\n7 10 4 3 20 15\n3', '7', True),
        ],
        'heap,sorting',
    ),
    _problem(
        'number-of-islands',
        'Count Islands in Grid',
        'medium', 12,
        f"""Line1: rows cols, then grid of 0/1. Print number of islands (4-directional).

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('4 5\n11110\n11010\n11000\n00000', '1'),
            _tc('3 3\n111\n111\n111', '1', True),
            _tc('1 1\n0', '0', True),
            _tc('2 2\n10\n01', '2', True),
        ],
        'graph,bfs',
    ),
    _problem(
        'grid-min-path-sum',
        'Minimum Path Sum in Grid',
        'medium', 12,
        f"""Line1: r c, then r lines of c non-negative ints. Move only right/down from top-left.
Print minimum path sum to bottom-right.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('3 3\n1 3 1\n1 5 1\n4 2 1', '7'),
            _tc('2 2\n1 1\n1 1', '2', True),
            _tc('1 1\n5', '5', True),
            _tc('2 3\n1 2 3\n4 5 6', '12', True),
        ],
        'dp,grid',
    ),
    _problem(
        'lis-length',
        'Longest Increasing Subsequence Length',
        'hard', 15,
        f"""Line1: n, Line2: n integers. Print LIS length.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('8\n10 9 2 5 3 7 101 18', '4'),
            _tc('1\n1', '1', True),
            _tc('5\n5 4 3 2 1', '1', True),
            _tc('8\n0 1 0 3 2 3 4 5', '4', True),
        ],
        'dp',
    ),
    _problem(
        'edit-distance',
        'Edit Distance',
        'hard', 15,
        f"""Two lines: strings word1 and word2. Print minimum edit distance.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('horse\nros', '3'),
            _tc('intention\nexecution', '5', True),
            _tc('a\na', '0', True),
            _tc('abc\n', '3', True),
        ],
        'dp,string',
    ),
    _problem(
        'knapsack-01',
        '0/1 Knapsack Maximum Value',
        'hard', 15,
        f"""Line1: n capacity, Line2: n weights, Line3: n values. Print max value.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('3 4\n1 2 3\n6 10 12', '18'),
            _tc('1 10\n5\n10', '10', True),
            _tc('4 5\n2 1 3 2\n3 2 4 3', '8', True),
            _tc('2 0\n1 2\n3 4', '0', True),
        ],
        'dp',
    ),
    _problem(
        'trapping-rain-water',
        'Trapping Rain Water',
        'hard', 15,
        f"""Line1: n, Line2: n non-negative heights. Print trapped water units.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('12\n0 1 0 2 1 0 1 3 2 1 2 1', '6'),
            _tc('3\n4 2 3', '1', True),
            _tc('1\n5', '0', True),
            _tc('5\n5 4 3 2 1', '0', True),
        ],
        'array,two-pointer',
    ),
    _problem(
        'word-break-possible',
        'Word Break Possible',
        'hard', 12,
        f"""Line1: string s, Line2: k, Line3: k dictionary words (space-separated on one line).
Print YES if s can be segmented into dictionary words, else NO.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('leetcode\n2\nleet code', 'YES'),
            _tc('applepenapple\n2\napple pen', 'YES', True),
            _tc('catsandog\n3\ncats sand dog', 'NO', True),
            _tc('a\n1\na', 'YES', True),
        ],
        'dp,string',
    ),
    _problem(
        'anagram-groups-count',
        'Count Anagram Groups',
        'medium', 8,
        f"""Line1: n words. Print number of anagram equivalence groups.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('6\neat tea tan ate nat bat', '3'),
            _tc('1\na', '1', True),
            _tc('3\nab ba ab', '1', True),
            _tc('4\nlisten silent enlist inlets', '1', True),
        ],
        'hash-map,string',
    ),
    _problem(
        'first-non-repeating',
        'First Non-Repeating Character',
        'easy', 5,
        f"""Print first non-repeating character or `NONE` if none.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('leetcode', 'l'),
            _tc('aabb', 'NONE', True),
            _tc('z', 'z', True),
            _tc('swiss', 'w', True),
        ],
    ),
    _problem(
        'sort-colors-count',
        'Sort 0-1-2 (Count Output)',
        'medium', 8,
        f"""Dutch national flag: n then n values in {{0,1,2}}. Print sorted values space-separated.

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('6\n2 0 2 1 1 0', '0 0 1 1 2 2'),
            _tc('3\n2 0 2', '0 2 2', True),
            _tc('1\n1', '1', True),
            _tc('5\n1 1 1 1 1', '1 1 1 1 1', True),
        ],
    ),
    _problem(
        'bfs-shortest-path-grid',
        'Shortest Path in Binary Maze',
        'hard', 12,
        f"""Line1: r c, grid of 0 (open) / 1 (wall). Start top-left, end bottom-right.
Print shortest steps or -1 if unreachable (4-directional, cannot visit walls).

{_STDIN_HINT}""",
        _STARTER,
        [
            _tc('3 3\n0 0 0\n1 1 0\n1 1 0', '4'),
            _tc('2 2\n0 1\n1 0', '-1', True),
            _tc('1 1\n0', '1', True),
            _tc('4 4\n0 0 0 0\n1 0 0 0\n1 0 1 0\n0 0 0 0', '6', True),
        ],
        'bfs,graph',
    ),
]

# Tiered exam presets (keys reference DSA_PROBLEMS order by key lookup)
EXAM_PRESETS = {
    'easy': [
        'two-sum-indices', 'array-sum', 'max-element', 'missing-number', 'reverse-string',
        'palindrome-check', 'valid-parentheses', 'count-vowels', 'fibonacci-n', 'gcd-two',
        'factorial-n', 'linear-search', 'even-odd', 'first-non-repeating',
    ],
    'medium': [
        'climbing-stairs', 'max-subarray-sum', 'binary-search', 'coin-change',
        'longest-substring-no-repeat', 'rotate-array-k', 'product-except-self',
        'merge-intervals-count', 'kth-largest', 'number-of-islands', 'grid-min-path-sum',
        'anagram-groups-count', 'sort-colors-count',
    ],
    'hard': [
        'lis-length', 'edit-distance', 'knapsack-01', 'trapping-rain-water',
        'word-break-possible', 'bfs-shortest-path-grid',
    ],
    'full': None,  # all problems
}

PROBLEMS_BY_KEY = {p['key']: p for p in DSA_PROBLEMS}
