"""
Seed script for DSA Preparation Module:
Populates 12 DSA topics and comprehensive, interview-grade DSA problems with:
- Rich markdown problem descriptions, constraints, I/O formats
- Realistic examples and starter code for Python and Java
- Public and hidden test cases with edge cases
- Progressive hints and full editorial solutions with complexity proofs
- Curated sheet tags ("Core 75", "Blind 50") and Problem of the Day
"""

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.dsa import DSATopic, DSAProblem, DSATestCase

TOPICS_DATA = [
    {
        "slug": "fundamentals-complexity",
        "name": "Programming Fundamentals and Complexity Analysis",
        "order_index": 1,
        "summary": "Big-O notation, time and space complexity analysis, recurrence relations, basic arithmetic simulation.",
    },
    {
        "slug": "arrays-strings",
        "name": "Arrays and Strings",
        "order_index": 2,
        "summary": "In-place array manipulations, prefix sums, matrix transformations, string matching and anagram algorithms.",
    },
    {
        "slug": "searching-sorting",
        "name": "Searching and Sorting",
        "order_index": 3,
        "summary": "Binary search variants, rotated arrays, merge sort, quick sort, Dutch national flag partitioning.",
    },
    {
        "slug": "hashing-two-pointers",
        "name": "Hashing, Two Pointers, and Sliding Window",
        "order_index": 4,
        "summary": "Hash map lookups, frequency tables, two-pointer inward/outward convergence, variable/fixed sliding windows.",
    },
    {
        "slug": "recursion-backtracking",
        "name": "Recursion and Backtracking",
        "order_index": 5,
        "summary": "Combinatorial generation, permutations, subsets, board constraint satisfaction (N-Queens, Sudoku).",
    },
    {
        "slug": "linked-lists",
        "name": "Linked Lists",
        "order_index": 6,
        "summary": "Singly/doubly linked lists, pointer reversal, Floyd's cycle detection, merge sort on lists.",
    },
    {
        "slug": "stacks-queues",
        "name": "Stacks and Queues",
        "order_index": 7,
        "summary": "Monotonic stacks, next greater element, parenthesis matching, circular queues, deque sliding window.",
    },
    {
        "slug": "trees-heaps",
        "name": "Trees, BSTs, and Heaps",
        "order_index": 8,
        "summary": "Tree traversals (DFS/BFS), binary search tree properties, lowest common ancestor, priority queues and min/max heaps.",
    },
    {
        "slug": "graphs",
        "name": "Graphs and Graph Algorithms",
        "order_index": 9,
        "summary": "Adjacency lists, BFS shortest paths, DFS connected components, cycle detection, topological sort (Kahn's), Dijkstra's.",
    },
    {
        "slug": "greedy",
        "name": "Greedy Algorithms",
        "order_index": 10,
        "summary": "Interval scheduling, jump game, fractional knapsack, gas station, Huffman coding intuition.",
    },
    {
        "slug": "dynamic-programming",
        "name": "Dynamic Programming",
        "order_index": 11,
        "summary": "1D and 2D memoization / tabulation, knapsack variants, longest common subsequence, edit distance, coin change.",
    },
    {
        "slug": "tries-bit-manipulation",
        "name": "Tries and Bit Manipulation",
        "order_index": 12,
        "summary": "Prefix trees for fast retrieval, XOR cancellations, bitwise shifts, two's complement, Brian Kernighan's algorithm.",
    },
]

PROBLEMS_DATA = [
    # 1. Fundamentals: Fizz Buzz Variant
    {
        "problem_number": 1,
        "slug": "fizz-buzz-multiplier",
        "title": "Fizz Buzz Multiplier",
        "topic_slug": "fundamentals-complexity",
        "difficulty": "EASY",
        "description": "Given an integer `n`, return a string array answer (1-indexed) where:\n- `answer[i] == \"FizzBuzz\"` if `i` is divisible by 3 and 5.\n- `answer[i] == \"Fizz\"` if `i` is divisible by 3.\n- `answer[i] == \"Buzz\"` if `i` is divisible by 5.\n- `answer[i] == str(i)` (as a string) if none of the above conditions are true.\n\nPrint the output space-separated on a single line.",
        "constraints": "1 <= n <= 10^4",
        "input_format": "A single line containing the integer n.",
        "output_format": "Space-separated sequence of strings from 1 to n.",
        "examples": [
            {
                "input": "5",
                "output": "1 2 Fizz 4 Buzz",
                "explanation": "1 is not div by 3 or 5, 2 is not, 3 -> Fizz, 4 is not, 5 -> Buzz.",
            },
            {
                "input": "15",
                "output": "1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz",
                "explanation": "15 is divisible by both 3 and 5, producing FizzBuzz.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def fizz_buzz(n: int) -> list[str]:
    # Write your solution here
    res = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            res.append("FizzBuzz")
        elif i % 3 == 0:
            res.append("Fizz")
        elif i % 5 == 0:
            res.append("Buzz")
        else:
            res.append(str(i))
    return res

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        n = int(line)
        print(" ".join(fizz_buzz(n)))
''',
            "java": '''import java.util.*;

public class Main {
    public static List<String> fizzBuzz(int n) {
        List<String> res = new ArrayList<>();
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0) res.add("FizzBuzz");
            else if (i % 3 == 0) res.add("Fizz");
            else if (i % 5 == 0) res.add("Buzz");
            else res.add(String.valueOf(i));
        }
        return res;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int n = sc.nextInt();
            List<String> ans = fizzBuzz(n);
            System.out.println(String.join(" ", ans));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1) auxiliary",
        "hints": [
            "Check for divisibility by 15 (both 3 and 5) first before checking individual numbers.",
            "A single loop from 1 to n is sufficient.",
        ],
        "editorial": """### Intuition & Approach
The problem requires standard conditional evaluation per integer from 1 to n.
Since numbers divisible by both 3 and 5 are also divisible by 15 (as 3 and 5 are coprime), we check `i % 15 == 0` first.

### Complexity Analysis
- **Time Complexity**: `O(N)` since we iterate once through all integers up to n.
- **Space Complexity**: `O(1)` auxiliary space beyond storing the answer strings.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75"],
        "test_cases": [
            {"input": "3", "output": "1 2 Fizz", "is_hidden": False, "order_index": 1},
            {"input": "5", "output": "1 2 Fizz 4 Buzz", "is_hidden": False, "order_index": 2},
            {"input": "15", "output": "1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz", "is_hidden": True, "order_index": 3},
            {"input": "1", "output": "1", "is_hidden": True, "order_index": 4},
            {"input": "20", "output": "1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz 16 17 Fizz 19 Buzz", "is_hidden": True, "order_index": 5},
        ],
    },

    # 2. Arrays: Two Sum
    {
        "problem_number": 2,
        "slug": "two-sum",
        "title": "Two Sum",
        "topic_slug": "arrays-strings",
        "difficulty": "EASY",
        "description": "Given an array of integers `nums` and an integer `target`, return the 0-indexed positions of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nOutput the two indices sorted in ascending order separated by a space.",
        "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9",
        "input_format": "Line 1: Space-separated integers representing nums.\nLine 2: Single integer target.",
        "output_format": "Two space-separated integers representing the 0-indexed indices.",
        "examples": [
            {
                "input": "2 7 11 15\n9",
                "output": "0 1",
                "explanation": "Because nums[0] + nums[1] == 2 + 7 == 9, we return 0 1.",
            },
            {
                "input": "3 2 4\n6",
                "output": "1 2",
                "explanation": "nums[1] + nums[2] == 2 + 4 == 6, so we return 1 2.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def two_sum(nums: list[int], target: int) -> list[int]:
    # Write your solution here
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return sorted([seen[diff], i])
        seen[num] = i
    return []

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        nums = list(map(int, lines[0].strip().split()))
        target = int(lines[1].strip())
        ans = two_sum(nums, target)
        print(f"{ans[0]} {ans[1]}")
''',
            "java": '''import java.util.*;

public class Main {
    public static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int comp = target - nums[i];
            if (map.containsKey(comp)) {
                return new int[] { map.get(comp), i };
            }
            map.put(nums[i], i);
        }
        return new int[0];
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String line = sc.nextLine().trim();
            String[] parts = line.split("\\s+");
            int[] nums = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                nums[i] = Integer.parseInt(parts[i]);
            }
            int target = sc.nextInt();
            int[] res = twoSum(nums, target);
            Arrays.sort(res);
            System.out.println(res[0] + " " + res[1]);
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(N)",
        "hints": [
            "A brute force approach compares every pair in O(N^2) time.",
            "Can you trade space for time using a hash map to look up complements in O(1)?",
            "As you traverse the array, check if (target - current_number) is already in the map.",
        ],
        "editorial": """### Problem Overview
Find two indices in an unsorted array whose values sum to a specific target.

### Optimal Hash Map Approach
Instead of looping over pairs, we can store elements we have seen so far in a hash table mapping `value -> index`.
For each element `nums[i]`, we calculate `complement = target - nums[i]`. If `complement` is already in the hash map, we have found our answer pair: `[map[complement], i]`.

### Complexity
- **Time Complexity**: `O(N)` — Single pass with `O(1)` average lookup time in hash map.
- **Space Complexity**: `O(N)` — At most N entries stored in the hash map.
""",
        "is_problem_of_the_day": True,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "2 7 11 15\n9", "output": "0 1", "is_hidden": False, "order_index": 1},
            {"input": "3 2 4\n6", "output": "1 2", "is_hidden": False, "order_index": 2},
            {"input": "3 3\n6", "output": "0 1", "is_hidden": True, "order_index": 3},
            {"input": "-1 -2 -3 -4 -5\n-8", "output": "2 4", "is_hidden": True, "order_index": 4},
            {"input": "100000 500 200 400 300\n700", "output": "1 2", "is_hidden": True, "order_index": 5},
        ],
    },

    # 3. Strings: Valid Anagram
    {
        "problem_number": 3,
        "slug": "valid-anagram",
        "title": "Valid Anagram",
        "topic_slug": "arrays-strings",
        "difficulty": "EASY",
        "description": "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.\n\nAn Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.",
        "constraints": "1 <= s.length, t.length <= 5 * 10^4\ns and t consist of lowercase English letters.",
        "input_format": "Line 1: string s\nLine 2: string t",
        "output_format": "'true' or 'false'",
        "examples": [
            {
                "input": "anagram\nnagaram",
                "output": "true",
                "explanation": "Both strings contain 3 'a's, 1 'n', 1 'g', 1 'r', and 1 'm'.",
            },
            {
                "input": "rat\ncar",
                "output": "false",
                "explanation": "'rat' has 't' while 'car' has 'c'.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    for char in t:
        if char not in counts or counts[char] == 0:
            return False
        counts[char] -= 1
    return True

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        s = lines[0].strip()
        t = lines[1].strip()
        print("true" if is_anagram(s, t) else "false")
''',
            "java": '''import java.util.*;

public class Main {
    public static boolean isAnagram(String s, String t) {
        if (s.length() != t.length()) return false;
        int[] freq = new int[26];
        for (int i = 0; i < s.length(); i++) {
            freq[s.charAt(i) - 'a']++;
            freq[t.charAt(i) - 'a']--;
        }
        for (int c : freq) {
            if (c != 0) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String s = sc.nextLine().trim();
            String t = sc.hasNextLine() ? sc.nextLine().trim() : "";
            System.out.println(isAnagram(s, t) ? "true" : "false");
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1) (26 characters)",
        "hints": [
            "If lengths differ, they cannot be anagrams.",
            "Can you count the frequency of each character in both strings?",
        ],
        "editorial": """### Algorithm
We use a fixed-size frequency array of 26 integers since the alphabet is lowercase English letters.
Increment the count for each character in `s` and decrement for each in `t`. If all counts remain 0, `t` is an anagram.

### Complexity
- **Time Complexity**: `O(N)` where N is length of string.
- **Space Complexity**: `O(1)` since array size is fixed at 26.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Blind 50", "Core 75"],
        "test_cases": [
            {"input": "anagram\nnagaram", "output": "true", "is_hidden": False, "order_index": 1},
            {"input": "rat\ncar", "output": "false", "is_hidden": False, "order_index": 2},
            {"input": "a\nab", "output": "false", "is_hidden": True, "order_index": 3},
            {"input": "listen\nsilent", "output": "true", "is_hidden": True, "order_index": 4},
            {"input": "aacc\nccac", "output": "false", "is_hidden": True, "order_index": 5},
        ],
    },

    # 4. Searching: Binary Search
    {
        "problem_number": 4,
        "slug": "binary-search",
        "title": "Binary Search",
        "topic_slug": "searching-sorting",
        "difficulty": "EASY",
        "description": "Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, then return its index. Otherwise, return `-1`.\n\nYou must write an algorithm with `O(log n)` runtime complexity.",
        "constraints": "1 <= nums.length <= 10^4\n-10^4 < nums[i], target < 10^4\nAll the integers in nums are unique.\nnums is sorted in ascending order.",
        "input_format": "Line 1: Space-separated sorted integers (nums)\nLine 2: Single integer target",
        "output_format": "A single integer denoting the target's index or -1.",
        "examples": [
            {
                "input": "-1 0 3 5 9 12\n9",
                "output": "4",
                "explanation": "9 exists in nums and its index is 4.",
            },
            {
                "input": "-1 0 3 5 9 12\n2",
                "output": "-1",
                "explanation": "2 does not exist in nums so return -1.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        nums = list(map(int, lines[0].strip().split()))
        target = int(lines[1].strip())
        print(search(nums, target))
''',
            "java": '''import java.util.*;

public class Main {
    public static int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) return mid;
            else if (nums[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return -1;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] nums = new int[parts.length];
            for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i]);
            int target = sc.nextInt();
            System.out.println(search(nums, target));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(log N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Maintain search boundaries `left` and `right`.",
            "Calculate mid point avoiding potential overflow: `left + (right - left) // 2`.",
            "Halve the search space at every comparison step.",
        ],
        "editorial": """### Binary Search Fundamentals
Because the input is sorted, we can test the middle element.
If `nums[mid] == target`, we return `mid`.
If `nums[mid] < target`, the target must reside in the right half `[mid + 1, right]`.
If `nums[mid] > target`, the target must reside in the left half `[left, mid - 1]`.

### Complexity
- **Time Complexity**: `O(log N)` since each iteration divides search space by 2.
- **Space Complexity**: `O(1)` iterative state.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75"],
        "test_cases": [
            {"input": "-1 0 3 5 9 12\n9", "output": "4", "is_hidden": False, "order_index": 1},
            {"input": "-1 0 3 5 9 12\n2", "output": "-1", "is_hidden": False, "order_index": 2},
            {"input": "5\n5", "output": "0", "is_hidden": True, "order_index": 3},
            {"input": "1 3 5 7 9 11 13 15\n15", "output": "7", "is_hidden": True, "order_index": 4},
            {"input": "2 4 6 8 10\n1", "output": "-1", "is_hidden": True, "order_index": 5},
        ],
    },

    # 5. Two Pointers: Container With Most Water
    {
        "problem_number": 5,
        "slug": "container-with-most-water",
        "title": "Container With Most Water",
        "topic_slug": "hashing-two-pointers",
        "difficulty": "MEDIUM",
        "description": "You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that the two endpoints of the `i-th` line are `(i, 0)` and `(i, height[i])`.\n\nFind two lines that together with the x-axis form a container, such that the container contains the most water.\n\nReturn the maximum amount of water a container can store.",
        "constraints": "n == height.length\n2 <= n <= 10^5\n0 <= height[i] <= 10^4",
        "input_format": "A single line containing space-separated integers representing the height array.",
        "output_format": "A single integer denoting the maximum area.",
        "examples": [
            {
                "input": "1 8 6 2 5 4 8 3 7",
                "output": "49",
                "explanation": "Max area between index 1 (height 8) and index 8 (height 7) is min(8, 7) * (8 - 1) = 7 * 7 = 49.",
            },
            {
                "input": "1 1",
                "output": "1",
                "explanation": "min(1, 1) * (1 - 0) = 1.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        width = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, width * h)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        heights = list(map(int, line.split()))
        print(max_area(heights))
''',
            "java": '''import java.util.*;

public class Main {
    public static int maxArea(int[] height) {
        int left = 0, right = height.length - 1;
        int maxWater = 0;
        while (left < right) {
            int width = right - left;
            int h = Math.min(height[left], height[right]);
            maxWater = Math.max(maxWater, width * h);
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }
        return maxWater;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] height = new int[parts.length];
            for (int i = 0; i < parts.length; i++) height[i] = Integer.parseInt(parts[i]);
            System.out.println(maxArea(height));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Start with the widest container: one pointer at the start and one at the end.",
            "The area is limited by the shorter line.",
            "Moving the taller line inward can only decrease area because width decreases and height is bounded by the shorter line.",
            "Hence, always advance the shorter line's pointer inward.",
        ],
        "editorial": """### Two Pointer Greedy Inward Convergence
Let `left = 0` and `right = n - 1`. The current water is `min(height[left], height[right]) * (right - left)`.
To find a potentially larger area with a smaller width, we must find a greater height. The shorter boundary will never form a larger area with any inner bar than it does with the current outer boundary, because the width is smaller and height is capped by `height[shorter]`.
Thus, it is safe to discard the shorter boundary and move its pointer inward.

### Complexity
- **Time Complexity**: `O(N)` since each step decrements distance between left and right.
- **Space Complexity**: `O(1)`.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "1 8 6 2 5 4 8 3 7", "output": "49", "is_hidden": False, "order_index": 1},
            {"input": "1 1", "output": "1", "is_hidden": False, "order_index": 2},
            {"input": "4 3 2 1 4", "output": "16", "is_hidden": True, "order_index": 3},
            {"input": "1 2 1", "output": "2", "is_hidden": True, "order_index": 4},
            {"input": "1 2 4 3", "output": "4", "is_hidden": True, "order_index": 5},
        ],
    },

    # 6. Sliding Window: Longest Substring Without Repeating Characters
    {
        "problem_number": 6,
        "slug": "longest-substring-without-repeating-characters",
        "title": "Longest Substring Without Repeating Characters",
        "topic_slug": "hashing-two-pointers",
        "difficulty": "MEDIUM",
        "description": "Given a string `s`, find the length of the longest substring without repeating characters.",
        "constraints": "0 <= s.length <= 5 * 10^4\ns consists of English letters, digits, symbols and spaces.",
        "input_format": "A single line containing the string s.",
        "output_format": "A single integer denoting the length of the longest substring.",
        "examples": [
            {
                "input": "abcabcbb",
                "output": "3",
                "explanation": "The answer is 'abc', with the length of 3.",
            },
            {
                "input": "bbbbb",
                "output": "1",
                "explanation": "The answer is 'b', with the length of 1.",
            },
            {
                "input": "pwwkew",
                "output": "3",
                "explanation": "The answer is 'wke', with the length of 3.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def length_of_longest_substring(s: str) -> int:
    char_index = {}
    max_len = 0
    left = 0
    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            left = char_index[ch] + 1
        char_index[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len

if __name__ == "__main__":
    line = sys.stdin.readline()
    if line.endswith("\\n"):
        line = line[:-1]
    print(length_of_longest_substring(line))
''',
            "java": '''import java.util.*;

public class Main {
    public static int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> map = new HashMap<>();
        int maxLen = 0, left = 0;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            if (map.containsKey(c) && map.get(c) >= left) {
                left = map.get(c) + 1;
            }
            map.put(c, right);
            maxLen = Math.max(maxLen, right - left + 1);
        }
        return maxLen;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.hasNextLine() ? sc.nextLine() : "";
        System.out.println(lengthOfLongestSubstring(s));
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(min(N, M)) where M is alphabet size",
        "hints": [
            "Use a sliding window bounded by [left, right].",
            "Store the last seen index of each character in a hash map.",
            "When encountering a duplicate character within the current window, move the left boundary past its last occurrence.",
        ],
        "editorial": """### Sliding Window with Hash Map Indexing
We maintain a window `[left, right]`. As `right` iterates from 0 to `N - 1`:
If `s[right]` was seen previously at index `idx` such that `idx >= left`, we slide `left = idx + 1` to skip the duplicate.
Update `char_index[s[right]] = right` and calculate window size `right - left + 1`.

### Complexity
- **Time Complexity**: `O(N)` — Single traversal of string.
- **Space Complexity**: `O(min(N, M))` — where M is the distinct characters in the alphabet.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "abcabcbb", "output": "3", "is_hidden": False, "order_index": 1},
            {"input": "bbbbb", "output": "1", "is_hidden": False, "order_index": 2},
            {"input": "pwwkew", "output": "3", "is_hidden": True, "order_index": 3},
            {"input": "", "output": "0", "is_hidden": True, "order_index": 4},
            {"input": "dvdf", "output": "3", "is_hidden": True, "order_index": 5},
        ],
    },

    # 7. Stack: Valid Parentheses
    {
        "problem_number": 7,
        "slug": "valid-parentheses",
        "title": "Valid Parentheses",
        "topic_slug": "stacks-queues",
        "difficulty": "EASY",
        "description": "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.",
        "constraints": "1 <= s.length <= 10^4\ns consists of parentheses only '()[]{}'.",
        "input_format": "A single line containing the string s.",
        "output_format": "'true' or 'false'",
        "examples": [
            {
                "input": "()[]{}",
                "output": "true",
                "explanation": "All brackets open and close in matched pairs.",
            },
            {
                "input": "(]",
                "output": "false",
                "explanation": "Open '(' closed by mismatching ']'.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def is_valid(s: str) -> bool:
    stack = []
    mapping = {")": "(", "}": "{", "]": "["}
    for char in s:
        if char in mapping:
            if not stack or stack[-1] != mapping[char]:
                return False
            stack.pop()
        else:
            stack.append(char)
    return len(stack) == 0

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    print("true" if is_valid(line) else "false")
''',
            "java": '''import java.util.*;

public class Main {
    public static boolean isValid(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        Map<Character, Character> map = Map.of(')', '(', '}', '{', ']', '[');
        for (char c : s.toCharArray()) {
            if (map.containsKey(c)) {
                if (stack.isEmpty() || stack.pop() != map.get(c)) return false;
            } else {
                stack.push(c);
            }
        }
        return stack.isEmpty();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s = sc.hasNext() ? sc.next().trim() : "";
        System.out.println(isValid(s) ? "true" : "false");
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(N)",
        "hints": [
            "Use a LIFO (Stack) data structure.",
            "Push opening brackets onto the stack.",
            "When encountering a closing bracket, verify that the top of the stack matches its corresponding opening pair.",
        ],
        "editorial": """### Stack Verification Algorithm
As we parse characters, every opening bracket expects to be matched by its corresponding closing bracket in reverse order of appearance.
A stack perfectly captures this LIFO constraint. If a closing bracket has no corresponding opening bracket on top of the stack, or if unclosed opening brackets remain at the end, the string is invalid.

### Complexity
- **Time Complexity**: `O(N)` — Single pass over string length.
- **Space Complexity**: `O(N)` — Worst case where all characters are opening brackets.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "()[]{}", "output": "true", "is_hidden": False, "order_index": 1},
            {"input": "(]", "output": "false", "is_hidden": False, "order_index": 2},
            {"input": "([)]", "output": "false", "is_hidden": True, "order_index": 3},
            {"input": "{[]}", "output": "true", "is_hidden": True, "order_index": 4},
            {"input": "(((((", "output": "false", "is_hidden": True, "order_index": 5},
        ],
    },

    # 8. Linked Lists: Reverse Linked List
    {
        "problem_number": 8,
        "slug": "reverse-linked-list",
        "title": "Reverse Linked List",
        "topic_slug": "linked-lists",
        "difficulty": "EASY",
        "description": "Given the `head` of a singly linked list represented as space-separated integers, reverse the list, and print the reversed list values space-separated.\n\nIf the list is empty, output an empty line.",
        "constraints": "The number of nodes in the list is the range [0, 5000].\n-5000 <= Node.val <= 5000",
        "input_format": "A single line containing space-separated integers representing the node values.",
        "output_format": "Space-separated integers representing the reversed list values.",
        "examples": [
            {
                "input": "1 2 3 4 5",
                "output": "5 4 3 2 1",
                "explanation": "1->2->3->4->5 reversed becomes 5->4->3->2->1.",
            },
            {
                "input": "1 2",
                "output": "2 1",
                "explanation": "1->2 reversed is 2->1.",
            },
        ],
        "starter_code": {
            "python": '''import sys

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if not line:
        print("")
        sys.exit(0)
    vals = list(map(int, line.split()))
    dummy = ListNode(0)
    tail = dummy
    for v in vals:
        tail.next = ListNode(v)
        tail = tail.next
    
    rev = reverse_list(dummy.next)
    out = []
    while rev:
        out.append(str(rev.val))
        rev = rev.next
    print(" ".join(out))
''',
            "java": '''import java.util.*;

class ListNode {
    int val;
    ListNode next;
    ListNode(int val) { this.val = val; }
}

public class Main {
    public static ListNode reverseList(ListNode head) {
        ListNode prev = null;
        ListNode curr = head;
        while (curr != null) {
            ListNode nxt = curr.next;
            curr.next = prev;
            prev = curr;
            curr = nxt;
        }
        return prev;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextLine()) {
            System.out.println("");
            return;
        }
        String line = sc.nextLine().trim();
        if (line.isEmpty()) {
            System.out.println("");
            return;
        }
        String[] parts = line.split("\\s+");
        ListNode dummy = new ListNode(0);
        ListNode curr = dummy;
        for (String p : parts) {
            curr.next = new ListNode(Integer.parseInt(p));
            curr = curr.next;
        }
        ListNode rev = reverseList(dummy.next);
        List<String> res = new ArrayList<>();
        while (rev != null) {
            res.add(String.valueOf(rev.val));
            rev = rev.next;
        }
        System.out.println(String.join(" ", res));
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Maintain three pointers: `prev`, `curr`, and `nxt`.",
            "Before redirecting `curr.next` to `prev`, save the original `curr.next`.",
        ],
        "editorial": """### In-Place Pointer Inversion
Iterate through the list. For each node `curr`, store `curr.next` in temporary `nxt`.
Set `curr.next = prev`.
Advance `prev = curr` and `curr = nxt`.
When `curr` becomes null, `prev` points to the new head.

### Complexity
- **Time Complexity**: `O(N)` — Single pass through nodes.
- **Space Complexity**: `O(1)` — In-place pointer mutation.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "1 2 3 4 5", "output": "5 4 3 2 1", "is_hidden": False, "order_index": 1},
            {"input": "1 2", "output": "2 1", "is_hidden": False, "order_index": 2},
            {"input": "42", "output": "42", "is_hidden": True, "order_index": 3},
            {"input": "10 20 30 40 50 60 70", "output": "70 60 50 40 30 20 10", "is_hidden": True, "order_index": 4},
        ],
    },

    # 9. Dynamic Programming: Coin Change
    {
        "problem_number": 9,
        "slug": "coin-change",
        "title": "Coin Change",
        "topic_slug": "dynamic-programming",
        "difficulty": "MEDIUM",
        "description": "You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.\n\nReturn the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.\n\nYou may assume that you have an infinite number of each kind of coin.",
        "constraints": "1 <= coins.length <= 12\n1 <= coins[i] <= 2^31 - 1\n0 <= amount <= 10^4",
        "input_format": "Line 1: Space-separated coin denominations\nLine 2: Single integer amount",
        "output_format": "A single integer denoting the minimum coins needed or -1.",
        "examples": [
            {
                "input": "1 2 5\n11",
                "output": "3",
                "explanation": "11 = 5 + 5 + 1 (3 coins).",
            },
            {
                "input": "2\n3",
                "output": "-1",
                "explanation": "3 cannot be formed using only coins of denomination 2.",
            },
            {
                "input": "1\n0",
                "output": "0",
                "explanation": "Amount 0 requires 0 coins.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def coin_change(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        coins = list(map(int, lines[0].strip().split()))
        amount = int(lines[1].strip())
        print(coin_change(coins, amount))
''',
            "java": '''import java.util.*;

public class Main {
    public static int coinChange(int[] coins, int amount) {
        int max = amount + 1;
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, max);
        dp[0] = 0;
        for (int coin : coins) {
            for (int i = coin; i <= amount; i++) {
                dp[i] = Math.min(dp[i], dp[i - coin] + 1);
            }
        }
        return dp[amount] > amount ? -1 : dp[amount];
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] coins = new int[parts.length];
            for (int i = 0; i < parts.length; i++) coins[i] = Integer.parseInt(parts[i]);
            int amount = sc.nextInt();
            System.out.println(coinChange(coins, amount));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(amount * coins.length)",
        "expected_space_complexity": "O(amount)",
        "hints": [
            "Let dp[i] be the minimum coins required to make sum i.",
            "Base case: dp[0] = 0.",
            "For each coin c and amount i >= c, dp[i] = min(dp[i], dp[i - c] + 1).",
        ],
        "editorial": """### Bottom-Up Dynamic Programming
We define `dp[x]` as the minimum number of coins needed to make amount `x`.
Initialize `dp[0] = 0` and all other `dp[x] = infinity`.
For every coin denomination `c`, we update all reachable amounts `x` from `c` to `amount`:
`dp[x] = min(dp[x], dp[x - c] + 1)`.

### Complexity
- **Time Complexity**: `O(amount * len(coins))`
- **Space Complexity**: `O(amount)`
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "1 2 5\n11", "output": "3", "is_hidden": False, "order_index": 1},
            {"input": "2\n3", "output": "-1", "is_hidden": False, "order_index": 2},
            {"input": "1\n0", "output": "0", "is_hidden": True, "order_index": 3},
            {"input": "186 419 83 408\n6249", "output": "20", "is_hidden": True, "order_index": 4},
            {"input": "2 5 10 1\n27", "output": "4", "is_hidden": True, "order_index": 5},
        ],
    },

    # 10. Graphs: Number of Islands
    {
        "problem_number": 10,
        "slug": "number-of-islands",
        "title": "Number of Islands",
        "topic_slug": "graphs",
        "difficulty": "MEDIUM",
        "description": "Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.\n\nAn island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.",
        "constraints": "m == grid.length\nn == grid[i].length\n1 <= m, n <= 300\ngrid[i][j] is '0' or '1'.",
        "input_format": "Line 1: Two integers m and n denoting rows and columns.\nNext m lines: n space-separated characters ('0' or '1').",
        "output_format": "A single integer denoting the number of islands.",
        "examples": [
            {
                "input": "4 5\n1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0",
                "output": "1",
                "explanation": "All 1s are connected horizontally or vertically into a single island.",
            },
            {
                "input": "4 5\n1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1",
                "output": "3",
                "explanation": "There are 3 isolated connected components of 1s.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def num_islands(grid: list[list[str]]) -> int:
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    islands = 0

    def dfs(r, c):
        if r < 0 or r >= m or c < 0 or c >= n or grid[r][c] != '1':
            return
        grid[r][c] = '0'  # mark visited in-place
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1':
                islands += 1
                dfs(i, j)
    return islands

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if lines:
        first = lines[0].strip().split()
        m, n = int(first[0]), int(first[1])
        grid = []
        for i in range(1, m + 1):
            grid.append(lines[i].strip().split())
        print(num_islands(grid))
''',
            "java": '''import java.util.*;

public class Main {
    private static void dfs(char[][] grid, int r, int c) {
        int m = grid.length, n = grid[0].length;
        if (r < 0 || r >= m || c < 0 || c >= n || grid[r][c] != '1') return;
        grid[r][c] = '0';
        dfs(grid, r + 1, c);
        dfs(grid, r - 1, c);
        dfs(grid, r, c + 1);
        dfs(grid, r, c - 1);
    }

    public static int numIslands(char[][] grid) {
        if (grid == null || grid.length == 0) return 0;
        int m = grid.length, n = grid[0].length;
        int count = 0;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == '1') {
                    count++;
                    dfs(grid, i, j);
                }
            }
        }
        return count;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int m = sc.nextInt();
            int n = sc.nextInt();
            char[][] grid = new char[m][n];
            for (int i = 0; i < m; i++) {
                for (int j = 0; j < n; j++) {
                    grid[i][j] = sc.next().charAt(0);
                }
            }
            System.out.println(numIslands(grid));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(M * N)",
        "expected_space_complexity": "O(M * N) call stack worst-case",
        "hints": [
            "Treat the grid as an undirected graph where cells with value '1' have edges to their 4 orthogonal neighbors.",
            "Traverse cells; when you encounter '1', increment your island count and flood-fill (DFS/BFS) all connected '1's to '0'.",
        ],
        "editorial": """### Connected Components via DFS / BFS
Iterate through every cell `(i, j)`. When `grid[i][j] == '1'`, we have discovered a new connected component.
Increment our island counter and execute Depth First Search (or BFS) to mark all adjacent lands as visited (by overwriting them to `'0'`).

### Complexity
- **Time Complexity**: `O(M * N)` since each cell is visited at most once.
- **Space Complexity**: `O(M * N)` in the worst case of grid completely filled with land due to recursion call stack.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {
                "input": "4 5\n1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0",
                "output": "1",
                "is_hidden": False,
                "order_index": 1,
            },
            {
                "input": "4 5\n1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1",
                "output": "3",
                "is_hidden": False,
                "order_index": 2,
            },
            {
                "input": "1 1\n0",
                "output": "0",
                "is_hidden": True,
                "order_index": 3,
            },
            {
                "input": "3 3\n1 0 1\n0 1 0\n1 0 1",
                "output": "5",
                "is_hidden": True,
                "order_index": 4,
            },
        ],
    },

    # 11. Trees: Maximum Depth of Binary Tree
    {
        "problem_number": 11,
        "slug": "maximum-depth-of-binary-tree",
        "title": "Maximum Depth of Binary Tree",
        "topic_slug": "trees-heaps",
        "difficulty": "EASY",
        "description": "Given a binary tree serialized in level-order format (with `null` for missing nodes), return its maximum depth.\n\nA binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.",
        "constraints": "The number of nodes in the tree is in the range [0, 10^4].\n-100 <= Node.val <= 100",
        "input_format": "A single line containing space-separated level-order node values, where missing nodes are denoted as 'null'.",
        "output_format": "A single integer representing the maximum depth.",
        "examples": [
            {
                "input": "3 9 20 null null 15 7",
                "output": "3",
                "explanation": "The longest path is 3 -> 20 -> 15 (depth 3).",
            },
            {
                "input": "1 null 2",
                "output": "2",
                "explanation": "Root 1 has right child 2 (depth 2).",
            },
        ],
        "starter_code": {
            "python": '''import sys
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_depth(root: TreeNode) -> int:
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

def build_tree(tokens: list[str]) -> TreeNode:
    if not tokens or tokens[0] == "null":
        return None
    root = TreeNode(int(tokens[0]))
    queue = deque([root])
    i = 1
    while queue and i < len(tokens):
        node = queue.popleft()
        if i < len(tokens) and tokens[i] != "null":
            node.left = TreeNode(int(tokens[i]))
            queue.append(node.left)
        i += 1
        if i < len(tokens) and tokens[i] != "null":
            node.right = TreeNode(int(tokens[i]))
            queue.append(node.right)
        i += 1
    return root

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if not line:
        print(0)
    else:
        tokens = line.split()
        root = build_tree(tokens)
        print(max_depth(root))
''',
            "java": '''import java.util.*;

class TreeNode {
    int val;
    TreeNode left, right;
    TreeNode(int val) { this.val = val; }
}

public class Main {
    public static int maxDepth(TreeNode root) {
        if (root == null) return 0;
        return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
    }

    public static TreeNode buildTree(String[] tokens) {
        if (tokens.length == 0 || tokens[0].equals("null")) return null;
        TreeNode root = new TreeNode(Integer.parseInt(tokens[0]));
        Queue<TreeNode> q = new LinkedList<>();
        q.offer(root);
        int i = 1;
        while (!q.isEmpty() && i < tokens.length) {
            TreeNode node = q.poll();
            if (i < tokens.length && !tokens[i].equals("null")) {
                node.left = new TreeNode(Integer.parseInt(tokens[i]));
                q.offer(node.left);
            }
            i++;
            if (i < tokens.length && !tokens[i].equals("null")) {
                node.right = new TreeNode(Integer.parseInt(tokens[i]));
                q.offer(node.right);
            }
            i++;
        }
        return root;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextLine()) {
            System.out.println(0);
            return;
        }
        String line = sc.nextLine().trim();
        if (line.isEmpty()) {
            System.out.println(0);
            return;
        }
        String[] tokens = line.split("\\s+");
        TreeNode root = buildTree(tokens);
        System.out.println(maxDepth(root));
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(H) recursion stack where H is tree height",
        "hints": [
            "Use recursion: depth of a node is 1 + max(depth(left), depth(right)).",
            "Base case: an empty subtree has depth 0.",
        ],
        "editorial": """### Recursive DFS Depth
A tree's maximum depth is recursively defined as 1 + the maximum depth between its left and right subtrees.
Base case: `if not root: return 0`.

### Complexity
- **Time Complexity**: `O(N)` since each node in the tree is visited once.
- **Space Complexity**: `O(H)` where H is tree height (`O(log N)` balanced, `O(N)` degenerate skew).
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "3 9 20 null null 15 7", "output": "3", "is_hidden": False, "order_index": 1},
            {"input": "1 null 2", "output": "2", "is_hidden": False, "order_index": 2},
            {"input": "", "output": "0", "is_hidden": True, "order_index": 3},
            {"input": "0", "output": "1", "is_hidden": True, "order_index": 4},
            {"input": "1 2 3 4 5 null null 6", "output": "4", "is_hidden": True, "order_index": 5},
        ],
    },

    # 12. Greedy: Jump Game
    {
        "problem_number": 12,
        "slug": "jump-game",
        "title": "Jump Game",
        "topic_slug": "greedy",
        "difficulty": "MEDIUM",
        "description": "You are given an integer array `nums`. You are initially positioned at the array's first index, and each element in the array represents your maximum jump length at that position.\n\nReturn `true` if you can reach the last index, or `false` otherwise.",
        "constraints": "1 <= nums.length <= 10^4\n0 <= nums[i] <= 10^5",
        "input_format": "A single line containing space-separated integers representing nums.",
        "output_format": "'true' or 'false'",
        "examples": [
            {
                "input": "2 3 1 1 4",
                "output": "true",
                "explanation": "Jump 1 step from index 0 to 1, then 3 steps to the last index.",
            },
            {
                "input": "3 2 1 0 4",
                "output": "false",
                "explanation": "You will always arrive at index 3 no matter what. Its maximum jump length is 0, which makes it impossible to reach the last index.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def can_jump(nums: list[int]) -> bool:
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + jump)
    return True

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        nums = list(map(int, line.split()))
        print("true" if can_jump(nums) else "false")
''',
            "java": '''import java.util.*;

public class Main {
    public static boolean canJump(int[] nums) {
        int maxReach = 0;
        for (int i = 0; i < nums.length; i++) {
            if (i > maxReach) return false;
            maxReach = Math.max(maxReach, i + nums[i]);
        }
        return true;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] nums = new int[parts.length];
            for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i]);
            System.out.println(canJump(nums) ? "true" : "false");
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Think about the furthest index reachable at any step.",
            "If your current index exceeds the max reachable index, you are stuck.",
        ],
        "editorial": """### Greedy Max Reach Tracking
Keep track of `max_reach`, which stores the furthest index reachable so far.
Iterate through index `i`. If `i > max_reach`, we cannot even reach index `i`, so return `false`.
Otherwise, update `max_reach = max(max_reach, i + nums[i])`.
If the loop completes, the last index is reachable, so return `true`.

### Complexity
- **Time Complexity**: `O(N)`
- **Space Complexity**: `O(1)`
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "2 3 1 1 4", "output": "true", "is_hidden": False, "order_index": 1},
            {"input": "3 2 1 0 4", "output": "false", "is_hidden": False, "order_index": 2},
            {"input": "0", "output": "true", "is_hidden": True, "order_index": 3},
            {"input": "2 0 0", "output": "true", "is_hidden": True, "order_index": 4},
            {"input": "1 0 1 0", "output": "false", "is_hidden": True, "order_index": 5},
        ],
    },

    # 13. Bit Manipulation: Single Number
    {
        "problem_number": 13,
        "slug": "single-number",
        "title": "Single Number",
        "topic_slug": "tries-bit-manipulation",
        "difficulty": "EASY",
        "description": "Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one.\n\nYou must implement a solution with a linear runtime complexity and use only constant extra space.",
        "constraints": "1 <= nums.length <= 3 * 10^4\n-3 * 10^4 <= nums[i] <= 3 * 10^4\nEach element in the array appears twice except for one element which appears only once.",
        "input_format": "A single line containing space-separated integers representing nums.",
        "output_format": "A single integer denoting the unique element.",
        "examples": [
            {
                "input": "2 2 1",
                "output": "1",
                "explanation": "2 appears twice, 1 appears once.",
            },
            {
                "input": "4 1 2 1 2",
                "output": "4",
                "explanation": "1 and 2 appear twice, 4 appears once.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def single_number(nums: list[int]) -> int:
    res = 0
    for num in nums:
        res ^= num
    return res

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        nums = list(map(int, line.split()))
        print(single_number(nums))
''',
            "java": '''import java.util.*;

public class Main {
    public static int singleNumber(int[] nums) {
        int res = 0;
        for (int num : nums) {
            res ^= num;
        }
        return res;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] nums = new int[parts.length];
            for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i]);
            System.out.println(singleNumber(nums));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Consider properties of the bitwise XOR (^) operator.",
            "a ^ a = 0 and a ^ 0 = a.",
            "XOR is commutative and associative.",
        ],
        "editorial": """### Bitwise XOR Property
XORing any number with itself cancels it to 0 (`x ^ x = 0`).
XORing 0 with any number leaves it unchanged (`0 ^ x = x`).
Since every duplicate element appears exactly twice, XORing all elements together will cancel all duplicates and leave only the single unique number.

### Complexity
- **Time Complexity**: `O(N)`
- **Space Complexity**: `O(1)`
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "2 2 1", "output": "1", "is_hidden": False, "order_index": 1},
            {"input": "4 1 2 1 2", "output": "4", "is_hidden": False, "order_index": 2},
            {"input": "1", "output": "1", "is_hidden": True, "order_index": 3},
            {"input": "-1 -1 -2", "output": "-2", "is_hidden": True, "order_index": 4},
        ],
    },

    # 14. Recursion: Subsets
    {
        "problem_number": 14,
        "slug": "subsets",
        "title": "Subsets",
        "topic_slug": "recursion-backtracking",
        "difficulty": "MEDIUM",
        "description": "Given an integer array `nums` of unique elements, return all possible subsets (the power set).\n\nThe solution set must not contain duplicate subsets. Output the subsets formatted with one subset per line, each subset's elements space-separated in sorted order. Output the subsets sorted lexicographically.",
        "constraints": "1 <= nums.length <= 10\n-10 <= nums[i] <= 10\nAll numbers of nums are unique.",
        "input_format": "A single line containing space-separated unique integers.",
        "output_format": "Subsets printed one per line, with elements space-separated. The empty subset is represented by an empty line.",
        "examples": [
            {
                "input": "1 2 3",
                "output": "\n1\n1 2\n1 2 3\n1 3\n2\n2 3\n3",
                "explanation": "All 8 subsets of [1, 2, 3].",
            },
        ],
        "starter_code": {
            "python": '''import sys

def subsets(nums: list[int]) -> list[list[int]]:
    nums.sort()
    res = []
    def backtrack(start, path):
        res.append(list(path))
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return res

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        nums = list(map(int, line.split()))
        ans = subsets(nums)
        ans.sort()
        for s in ans:
            print(" ".join(map(str, s)))
''',
            "java": '''import java.util.*;

public class Main {
    public static List<List<Integer>> subsets(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> res = new ArrayList<>();
        backtrack(nums, 0, new ArrayList<>(), res);
        return res;
    }

    private static void backtrack(int[] nums, int start, List<Integer> path, List<List<Integer>> res) {
        res.add(new ArrayList<>(path));
        for (int i = start; i < nums.length; i++) {
            path.add(nums[i]);
            backtrack(nums, i + 1, path, res);
            path.remove(path.size() - 1);
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] nums = new int[parts.length];
            for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i]);
            List<List<Integer>> ans = subsets(nums);
            // sort list of lists lexicographically
            ans.sort((a, b) -> {
                int len = Math.min(a.size(), b.size());
                for (int i = 0; i < len; i++) {
                    int cmp = a.get(i).compareTo(b.get(i));
                    if (cmp != 0) return cmp;
                }
                return Integer.compare(a.size(), b.size());
            });
            for (List<Integer> s : ans) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < s.size(); i++) {
                    if (i > 0) sb.append(" ");
                    sb.append(s.get(i));
                }
                System.out.println(sb.toString());
            }
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N * 2^N)",
        "expected_space_complexity": "O(N) recursion depth",
        "hints": [
            "At each index, you have two choices: include nums[i] or exclude it.",
            "A backtracking DFS helper explores every branch.",
        ],
        "editorial": """### Backtracking Power Set Generation
Sort the input so subsets naturally produce elements in ascending order.
Define `backtrack(start, path)`. At each state, append the current `path` to the result list.
Then loop from `start` to `len(nums) - 1`, pushing `nums[i]` to `path`, recursing with `i + 1`, and popping `nums[i]`.

### Complexity
- **Time Complexity**: `O(N * 2^N)` because there are `2^N` subsets and each takes `O(N)` to copy.
- **Space Complexity**: `O(N)` recursion stack.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75"],
        "test_cases": [
            {"input": "1 2 3", "output": "\n1\n1 2\n1 2 3\n1 3\n2\n2 3\n3", "is_hidden": False, "order_index": 1},
            {"input": "0", "output": "\n0", "is_hidden": False, "order_index": 2},
            {"input": "4 5", "output": "\n4\n4 5\n5", "is_hidden": True, "order_index": 3},
        ],
    },

    # 15. Dynamic Programming: Climbing Stairs
    {
        "problem_number": 15,
        "slug": "climbing-stairs",
        "title": "Climbing Stairs",
        "topic_slug": "dynamic-programming",
        "difficulty": "EASY",
        "description": "You are climbing a staircase. It takes `n` steps to reach the top.\n\nEach time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "constraints": "1 <= n <= 45",
        "input_format": "A single line containing the integer n.",
        "output_format": "A single integer denoting the number of distinct ways.",
        "examples": [
            {
                "input": "2",
                "output": "2",
                "explanation": "There are two ways: 1 step + 1 step, or 2 steps.",
            },
            {
                "input": "3",
                "output": "3",
                "explanation": "Three ways: (1+1+1), (1+2), (2+1).",
            },
        ],
        "starter_code": {
            "python": '''import sys

def climb_stairs(n: int) -> int:
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        print(climb_stairs(int(line)))
''',
            "java": '''import java.util.*;

public class Main {
    public static int climbStairs(int n) {
        if (n <= 2) return n;
        int a = 1, b = 2;
        for (int i = 3; i <= n; i++) {
            int c = a + b;
            a = b;
            b = c;
        }
        return b;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            System.out.println(climbStairs(sc.nextInt()));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "To reach step n, you must arrive from either step n - 1 (1-step jump) or step n - 2 (2-step jump).",
            "This matches the Fibonacci sequence: ways(n) = ways(n - 1) + ways(n - 2).",
        ],
        "editorial": """### Fibonacci Recurrence Relation
To reach step `n`, one must have either jumped from `n - 1` or `n - 2`.
Therefore, `ways(n) = ways(n - 1) + ways(n - 2)`.
Base cases:
- `ways(1) = 1`
- `ways(2) = 2`
Using two rolling variables computes this in `O(1)` memory.

### Complexity
- **Time Complexity**: `O(N)`
- **Space Complexity**: `O(1)`
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "2", "output": "2", "is_hidden": False, "order_index": 1},
            {"input": "3", "output": "3", "is_hidden": False, "order_index": 2},
            {"input": "4", "output": "5", "is_hidden": True, "order_index": 3},
            {"input": "10", "output": "89", "is_hidden": True, "order_index": 4},
            {"input": "30", "output": "1346269", "is_hidden": True, "order_index": 5},
        ],
    },
]


def seed_dsa():
    print("Connecting to database...")
    db = SessionLocal()
    try:
        print("Ensuring tables are initialized...")
        Base.metadata.create_all(bind=engine)

        # 1. Ingest Topics
        print("Upserting 12 DSA Topics...")
        topic_map = {}
        for t in TOPICS_DATA:
            existing = db.query(DSATopic).filter(DSATopic.slug == t["slug"]).first()
            if not existing:
                existing = DSATopic(
                    slug=t["slug"],
                    name=t["name"],
                    order_index=t["order_index"],
                    summary=t["summary"],
                )
                db.add(existing)
                db.flush()
            else:
                existing.name = t["name"]
                existing.order_index = t["order_index"]
                existing.summary = t["summary"]
            topic_map[t["slug"]] = existing

        # 2. Ingest Problems & Test Cases
        print(f"Upserting {len(PROBLEMS_DATA)} authentic DSA problems with test cases...")
        for p in PROBLEMS_DATA:
            topic = topic_map.get(p["topic_slug"])
            existing_p = db.query(DSAProblem).filter(DSAProblem.slug == p["slug"]).first()
            if not existing_p:
                existing_p = DSAProblem(
                    problem_number=p["problem_number"],
                    slug=p["slug"],
                    title=p["title"],
                    topic_id=topic.id if topic else None,
                    difficulty=p["difficulty"],
                    description=p["description"],
                    constraints=p["constraints"],
                    input_format=p["input_format"],
                    output_format=p["output_format"],
                    examples=p["examples"],
                    starter_code=p["starter_code"],
                    expected_time_complexity=p["expected_time_complexity"],
                    expected_space_complexity=p["expected_space_complexity"],
                    hints=p["hints"],
                    editorial=p["editorial"],
                    status="PUBLISHED",
                    is_problem_of_the_day=p["is_problem_of_the_day"],
                    sheet_tags=p["sheet_tags"],
                )
                db.add(existing_p)
                db.flush()
            else:
                existing_p.problem_number = p["problem_number"]
                existing_p.title = p["title"]
                existing_p.topic_id = topic.id if topic else None
                existing_p.difficulty = p["difficulty"]
                existing_p.description = p["description"]
                existing_p.constraints = p["constraints"]
                existing_p.input_format = p["input_format"]
                existing_p.output_format = p["output_format"]
                existing_p.examples = p["examples"]
                existing_p.starter_code = p["starter_code"]
                existing_p.expected_time_complexity = p["expected_time_complexity"]
                existing_p.expected_space_complexity = p["expected_space_complexity"]
                existing_p.hints = p["hints"]
                existing_p.editorial = p["editorial"]
                existing_p.is_problem_of_the_day = p["is_problem_of_the_day"]
                existing_p.sheet_tags = p["sheet_tags"]
                db.flush()

            # Delete old test cases and re-insert fresh authentic test cases
            db.query(DSATestCase).filter(DSATestCase.problem_id == existing_p.id).delete()
            db.flush()

            for tc in p["test_cases"]:
                test_case = DSATestCase(
                    problem_id=existing_p.id,
                    input_data=tc["input"],
                    expected_output=tc["output"],
                    is_hidden=tc["is_hidden"],
                    order_index=tc["order_index"],
                    time_limit_ms=2000,
                    memory_limit_mb=256,
                )
                db.add(test_case)

        db.commit()
        print("DSA Data Seeding completed successfully!")
        
        # Verify counts
        topic_count = db.query(DSATopic).count()
        problem_count = db.query(DSAProblem).count()
        test_case_count = db.query(DSATestCase).count()
        print(f"Verification: {topic_count} topics, {problem_count} problems, {test_case_count} test cases.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding DSA data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_dsa()
