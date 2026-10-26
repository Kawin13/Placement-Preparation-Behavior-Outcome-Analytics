"""
Seed script to assign exactly three GeeksforGeeks (GFG) classic interview problems
to each of the 12 DSA topics in the Placement Portal DSA Studio.

Total topics: 12
Problems per topic: 3
Total problems: 36
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.dsa import DSATopic, DSAProblem, DSATestCase

GFG_NEW_PROBLEMS = [
    # -------------------------------------------------------------
    # 1. Programming Fundamentals and Complexity Analysis (Need 2: #16, #17)
    # -------------------------------------------------------------
    {
        "problem_number": 16,
        "slug": "palindrome-number",
        "title": "Palindrome Number",
        "topic_slug": "fundamentals-complexity",
        "difficulty": "EASY",
        "description": "Given an integer `x`, return `true` if `x` is a **palindrome**, and `false` otherwise.\n\nAn integer is a palindrome when it reads the same forward and backward.\n- For example, `121` is a palindrome while `123` and `-121` are not.\n\nOutput `true` or `false` on a single line.",
        "constraints": "-2^31 <= x <= 2^31 - 1",
        "input_format": "A single line containing the integer x.",
        "output_format": "true or false.",
        "examples": [
            {
                "input": "121",
                "output": "true",
                "explanation": "121 reads as 121 from left to right and from right to left.",
            },
            {
                "input": "-121",
                "output": "false",
                "explanation": "From left to right, it reads -121. From right to left it becomes 121-, so false.",
            },
            {
                "input": "10",
                "output": "false",
                "explanation": "Reads 01 from right to left. Therefore it is not a palindrome.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def is_palindrome(x: int) -> bool:
    # Write your solution here without converting to string if possible
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    rev = 0
    while x > rev:
        rev = rev * 10 + x % 10
        x //= 10
    return x == rev or x == rev // 10

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        x = int(line)
        print("true" if is_palindrome(x) else "false")
''',
            "java": '''import java.util.*;

public class Main {
    public static boolean isPalindrome(int x) {
        if (x < 0 || (x % 10 == 0 && x != 0)) return false;
        int rev = 0;
        while (x > rev) {
            rev = rev * 10 + x % 10;
            x /= 10;
        }
        return x == rev || x == rev / 10;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int x = sc.nextInt();
            System.out.println(isPalindrome(x) ? "true" : "false");
        }
    }
}
''',
        },
        "expected_time_complexity": "O(log10(N))",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Negative numbers can never be palindromes due to the leading minus sign.",
            "Instead of reversing the whole number (which could overflow 32-bit int), reverse only half of the digits.",
            "Compare the reversed half with the remaining half.",
        ],
        "editorial": """### Intuition & Approach
To determine whether an integer is a palindrome without string conversion:
1. All negative numbers are not palindromes (e.g. `-121` != `121-`).
2. Numbers ending with `0` cannot be palindromes unless the number is `0` itself.
3. We reverse the second half of the digits until `x <= rev`. Then compare `x == rev` (for even length) or `x == rev // 10` (for odd length).

### Complexity Analysis
- **Time Complexity**: `O(log10(N))` because we divide by 10 in every step.
- **Space Complexity**: `O(1)` auxiliary space.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "121", "output": "true", "is_hidden": False, "order_index": 1},
            {"input": "-121", "output": "false", "is_hidden": False, "order_index": 2},
            {"input": "10", "output": "false", "is_hidden": False, "order_index": 3},
            {"input": "0", "output": "true", "is_hidden": True, "order_index": 4},
            {"input": "12321", "output": "true", "is_hidden": True, "order_index": 5},
            {"input": "123321", "output": "true", "is_hidden": True, "order_index": 6},
        ],
    },
    {
        "problem_number": 17,
        "slug": "powx-n",
        "title": "Power of Numbers (Pow(x, n))",
        "topic_slug": "fundamentals-complexity",
        "difficulty": "MEDIUM",
        "description": "Implement **pow(x, n)**, which calculates `x` raised to the power `n` (`x^n`) modulo `10^9 + 7` using binary exponentiation.\n\nInput consists of two integers `x` and `n` separated by a space on one line.",
        "constraints": "1 <= x <= 10^9\n0 <= n <= 10^9",
        "input_format": "A single line with two space-separated integers x and n.",
        "output_format": "Single integer representing (x^n) % 1000000007.",
        "examples": [
            {
                "input": "2 10",
                "output": "1024",
                "explanation": "2^10 = 1024.",
            },
            {
                "input": "2 0",
                "output": "1",
                "explanation": "Any non-zero number to power 0 is 1.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def power(x: int, n: int) -> int:
    MOD = 1_000_000_007
    res = 1
    x = x % MOD
    while n > 0:
        if n % 2 == 1:
            res = (res * x) % MOD
        x = (x * x) % MOD
        n //= 2
    return res

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        parts = line.split()
        if len(parts) >= 2:
            x, n = int(parts[0]), int(parts[1])
            print(power(x, n))
''',
            "java": '''import java.util.*;

public class Main {
    public static long power(long x, long n) {
        long MOD = 1000000007L;
        long res = 1;
        x = x % MOD;
        while (n > 0) {
            if (n % 2 == 1) res = (res * x) % MOD;
            x = (x * x) % MOD;
            n /= 2;
        }
        return res;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLong()) {
            long x = sc.nextLong();
            long n = sc.nextLong();
            System.out.println(power(x, n));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(log n)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Multiplying x by itself n times takes O(n) which will TLE for n=10^9.",
            "Use binary exponentiation: if n is even, x^n = (x^2)^(n/2). If odd, x^n = x * x^(n-1).",
            "Remember to apply modulo at each intermediate multiplication.",
        ],
        "editorial": """### Intuition & Approach
Binary Exponentiation (also known as exponentiation by squaring) allows computing `x^n` in `O(log n)` multiplications instead of `O(n)`.
By checking the lowest bit of `n` (`n & 1`), we multiply the running product whenever the bit is 1, and square `x` while halving `n`.

### Complexity Analysis
- **Time Complexity**: `O(log n)` bit operations.
- **Space Complexity**: `O(1)` auxiliary space.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75"],
        "test_cases": [
            {"input": "2 10", "output": "1024", "is_hidden": False, "order_index": 1},
            {"input": "2 0", "output": "1", "is_hidden": False, "order_index": 2},
            {"input": "3 5", "output": "243", "is_hidden": True, "order_index": 3},
            {"input": "5 100000", "output": "713423871", "is_hidden": True, "order_index": 4},
        ],
    },

    # -------------------------------------------------------------
    # 2. Arrays and Strings (Need 1: #18)
    # -------------------------------------------------------------
    {
        "problem_number": 18,
        "slug": "maximum-subarray-kadanes",
        "title": "Kadane's Algorithm (Maximum Subarray Sum)",
        "topic_slug": "arrays-strings",
        "difficulty": "MEDIUM",
        "description": "Given an integer array `nums`, find the subarray with the largest sum, and return **its sum**.\n\nA **subarray** is a contiguous non-empty sequence of elements within an array.",
        "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
        "input_format": "A single line containing space-separated integers representing nums.",
        "output_format": "A single integer representing the maximum subarray sum.",
        "examples": [
            {
                "input": "-2 1 -3 4 -1 2 1 -5 4",
                "output": "6",
                "explanation": "The subarray [4, -1, 2, 1] has the largest sum 6.",
            },
            {
                "input": "1",
                "output": "1",
                "explanation": "The subarray [1] has the largest sum 1.",
            },
            {
                "input": "5 4 -1 7 8",
                "output": "23",
                "explanation": "The subarray [5, 4, -1, 7, 8] has the largest sum 23.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def max_sub_array(nums: list[int]) -> int:
    # Kadane's Algorithm
    max_so_far = nums[0]
    curr_max = nums[0]
    for x in nums[1:]:
        curr_max = max(x, curr_max + x)
        max_so_far = max(max_so_far, curr_max)
    return max_so_far

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        nums = list(map(int, line.split()))
        print(max_sub_array(nums))
''',
            "java": '''import java.util.*;

public class Main {
    public static int maxSubArray(int[] nums) {
        int maxSoFar = nums[0];
        int currMax = nums[0];
        for (int i = 1; i < nums.length; i++) {
            currMax = Math.max(nums[i], currMax + nums[i]);
            maxSoFar = Math.max(maxSoFar, currMax);
        }
        return maxSoFar;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] nums = new int[parts.length];
            for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i]);
            System.out.println(maxSubArray(nums));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "At each index i, we decide whether to extend the previous subarray or start a fresh subarray at nums[i].",
            "curr_max = max(nums[i], curr_max + nums[i]).",
            "Keep track of the global maximum seen across all indices.",
        ],
        "editorial": """### Intuition & Approach
Kadane's Algorithm solves the Maximum Subarray problem in linear time `O(N)` and constant auxiliary space `O(1)`.
At each position `i`, the maximum contiguous sum ending at `i` is either `nums[i]` itself or `curr_max + nums[i]`. If `curr_max` becomes negative, extending it will only reduce the sum of subsequent elements, so we reset to `nums[i]`.

### Complexity Analysis
- **Time Complexity**: `O(N)` single pass through the array.
- **Space Complexity**: `O(1)` auxiliary memory.
""",
        "is_problem_of_the_day": True,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "-2 1 -3 4 -1 2 1 -5 4", "output": "6", "is_hidden": False, "order_index": 1},
            {"input": "1", "output": "1", "is_hidden": False, "order_index": 2},
            {"input": "5 4 -1 7 8", "output": "23", "is_hidden": False, "order_index": 3},
            {"input": "-5 -2 -8 -1", "output": "-1", "is_hidden": True, "order_index": 4},
            {"input": "-1 2 3 -4 5 10", "output": "16", "is_hidden": True, "order_index": 5},
        ],
    },

    # -------------------------------------------------------------
    # 3. Searching and Sorting (Need 2: #19, #20)
    # -------------------------------------------------------------
    {
        "problem_number": 19,
        "slug": "search-in-rotated-sorted-array",
        "title": "Search in Rotated Sorted Array",
        "topic_slug": "searching-sorting",
        "difficulty": "MEDIUM",
        "description": "Given a sorted array `nums` of distinct integers that is possibly rotated at an unknown pivot index, and an integer `target`, return the 0-indexed position of `target` if it is in `nums`, or `-1` if it is not in `nums`.\n\nYou must write an algorithm with `O(log n)` runtime complexity.",
        "constraints": "1 <= nums.length <= 5000\n-10^4 <= nums[i], target <= 10^4\nAll values of nums are unique.",
        "input_format": "Line 1: Space-separated integers representing nums.\nLine 2: Single integer target.",
        "output_format": "Single integer representing the index or -1.",
        "examples": [
            {
                "input": "4 5 6 7 0 1 2\n0",
                "output": "4",
                "explanation": "Target 0 is found at index 4.",
            },
            {
                "input": "4 5 6 7 0 1 2\n3",
                "output": "-1",
                "explanation": "Target 3 is not present in nums, so return -1.",
            },
            {
                "input": "1\n0",
                "output": "-1",
                "explanation": "Single element array not matching target returns -1.",
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
        # Check if left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else: # Right half is sorted
            if nums[mid] < target <= nums[right]:
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
            if (nums[left] <= nums[mid]) {
                if (nums[left] <= target && target < nums[mid]) right = mid - 1;
                else left = mid + 1;
            } else {
                if (nums[mid] < target && target <= nums[right]) left = mid + 1;
                else right = mid - 1;
            }
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
            "Even when rotated, at least one half (left or right) of the array is guaranteed to be sorted.",
            "Identify which half is sorted by comparing nums[left] and nums[mid].",
            "Check if target falls within the boundaries of the sorted half to decide which way to branch.",
        ],
        "editorial": """### Intuition & Approach
In any rotated sorted array, dividing the array into two halves at `mid` guarantees that at least one of the two halves is sorted in ascending order.
1. If `nums[left] <= nums[mid]`, the left subarray is normally sorted. If `nums[left] <= target < nums[mid]`, search left; otherwise search right.
2. If `nums[left] > nums[mid]`, the right subarray is sorted. If `nums[mid] < target <= nums[right]`, search right; otherwise search left.

### Complexity Analysis
- **Time Complexity**: `O(log N)` binary search.
- **Space Complexity**: `O(1)` memory.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "4 5 6 7 0 1 2\n0", "output": "4", "is_hidden": False, "order_index": 1},
            {"input": "4 5 6 7 0 1 2\n3", "output": "-1", "is_hidden": False, "order_index": 2},
            {"input": "1\n0", "output": "-1", "is_hidden": False, "order_index": 3},
            {"input": "1 3\n3", "output": "1", "is_hidden": True, "order_index": 4},
            {"input": "5 1 3\n5", "output": "0", "is_hidden": True, "order_index": 5},
        ],
    },
    {
        "problem_number": 20,
        "slug": "sort-an-array-of-0s-1s-and-2s",
        "title": "Sort an Array of 0s, 1s, and 2s (Dutch National Flag)",
        "topic_slug": "searching-sorting",
        "difficulty": "MEDIUM",
        "description": "Given an array `nums` with `n` objects colored red, white, or blue, sort them **in-place** so that objects of the same color are adjacent, with the colors in the order red, white, and blue.\n\nWe will use the integers `0`, `1`, and `2` to represent the color red, white, and blue, respectively.\n\nYou must solve this problem without using the library's sort function and in `O(N)` one-pass.",
        "constraints": "1 <= nums.length <= 300\nnums[i] is either 0, 1, or 2.",
        "input_format": "A single line of space-separated integers representing nums.",
        "output_format": "Space-separated sorted integers.",
        "examples": [
            {
                "input": "2 0 2 1 1 0",
                "output": "0 0 1 1 2 2",
                "explanation": "Array contains two 0s, two 1s, and two 2s.",
            },
            {
                "input": "2 0 1",
                "output": "0 1 2",
                "explanation": "Sorted order is 0 1 2.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def sort_colors(nums: list[int]) -> list[int]:
    # Dutch National Flag Algorithm (3 pointers)
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
    return nums

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        nums = list(map(int, line.split()))
        sorted_nums = sort_colors(nums)
        print(" ".join(map(str, sorted_nums)))
''',
            "java": '''import java.util.*;

public class Main {
    public static void sortColors(int[] nums) {
        int low = 0, mid = 0, high = nums.length - 1;
        while (mid <= high) {
            if (nums[mid] == 0) {
                int tmp = nums[low]; nums[low] = nums[mid]; nums[mid] = tmp;
                low++; mid++;
            } else if (nums[mid] == 1) {
                mid++;
            } else {
                int tmp = nums[mid]; nums[mid] = nums[high]; nums[high] = tmp;
                high--;
            }
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] nums = new int[parts.length];
            for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i]);
            sortColors(nums);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < nums.length; i++) {
                if (i > 0) sb.append(" ");
                sb.append(nums[i]);
            }
            System.out.println(sb.toString());
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Use three pointers: low, mid, and high.",
            "Maintain invariants: elements before low are 0s, elements after high are 2s, and elements between low and mid-1 are 1s.",
            "When swapping with high, do not advance mid immediately because the swapped element hasn't been inspected yet.",
        ],
        "editorial": """### Intuition & Approach
Dijkstra's Dutch National Flag algorithm partitions the array into three regions using three pointers: `low`, `mid`, and `high`.
- Elements `0` to `low - 1` are `0`.
- Elements `low` to `mid - 1` are `1`.
- Elements `mid` to `high` are unclassified.
- Elements `high + 1` to `N - 1` are `2`.

In a single pass `mid <= high`, each element is placed in its designated partition.

### Complexity Analysis
- **Time Complexity**: `O(N)` exactly one pass.
- **Space Complexity**: `O(1)` in-place partitioning.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "2 0 2 1 1 0", "output": "0 0 1 1 2 2", "is_hidden": False, "order_index": 1},
            {"input": "2 0 1", "output": "0 1 2", "is_hidden": False, "order_index": 2},
            {"input": "0", "output": "0", "is_hidden": True, "order_index": 3},
            {"input": "1 1 0 0 2 2", "output": "0 0 1 1 2 2", "is_hidden": True, "order_index": 4},
        ],
    },

    # -------------------------------------------------------------
    # 4. Hashing, Two Pointers, and Sliding Window (Need 1: #21)
    # -------------------------------------------------------------
    {
        "problem_number": 21,
        "slug": "trapping-rain-water",
        "title": "Trapping Rain Water",
        "topic_slug": "hashing-two-pointers",
        "difficulty": "HARD",
        "description": "Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.\n\nPrint the total trapped units of water as an integer on a single line.",
        "constraints": "n == height.length\n1 <= n <= 2 * 10^4\n0 <= height[i] <= 10^5",
        "input_format": "A single line containing space-separated integers representing the elevation heights.",
        "output_format": "A single integer denoting total units of trapped rain water.",
        "examples": [
            {
                "input": "0 1 0 2 1 0 1 3 2 1 2 1",
                "output": "6",
                "explanation": "The elevation map traps 6 units of rain water.",
            },
            {
                "input": "4 2 0 3 2 5",
                "output": "9",
                "explanation": "Total 9 units of rain water trapped between the bars.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def trap(height: list[int]) -> int:
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    return water

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        height = list(map(int, line.split()))
        print(trap(height))
''',
            "java": '''import java.util.*;

public class Main {
    public static int trap(int[] height) {
        if (height.length == 0) return 0;
        int left = 0, right = height.length - 1;
        int leftMax = height[left], rightMax = height[right];
        int water = 0;
        while (left < right) {
            if (leftMax < rightMax) {
                left++;
                leftMax = Math.max(leftMax, height[left]);
                water += leftMax - height[left];
            } else {
                right--;
                rightMax = Math.max(rightMax, height[right]);
                water += rightMax - height[right];
            }
        }
        return water;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] height = new int[parts.length];
            for (int i = 0; i < parts.length; i++) height[i] = Integer.parseInt(parts[i]);
            System.out.println(trap(height));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "At any bar i, trapped water is determined by min(max_left, max_right) - height[i].",
            "Instead of precomputing prefix and suffix max arrays, use two pointers from both ends.",
            "Advance the pointer with the smaller maximum height because it acts as the limiting factor.",
        ],
        "editorial": """### Intuition & Approach
The water trapped above bar `i` is determined by `min(max_left, max_right) - height[i]`.
Using two pointers (`left` and `right`) converging inwards:
- If `left_max < right_max`, we know that the water level at `left` is strictly bounded by `left_max` regardless of future bars to the right. We process `left` and advance.
- Otherwise, the water level at `right` is bounded by `right_max`. We process `right` and advance.

### Complexity Analysis
- **Time Complexity**: `O(N)` two pointers meet in one pass.
- **Space Complexity**: `O(1)` auxiliary space.
""",
        "is_problem_of_the_day": True,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "0 1 0 2 1 0 1 3 2 1 2 1", "output": "6", "is_hidden": False, "order_index": 1},
            {"input": "4 2 0 3 2 5", "output": "9", "is_hidden": False, "order_index": 2},
            {"input": "3 0 2 0 4", "output": "7", "is_hidden": True, "order_index": 3},
            {"input": "1 2 3 4 5", "output": "0", "is_hidden": True, "order_index": 4},
        ],
    },

    # -------------------------------------------------------------
    # 5. Recursion and Backtracking (Need 2: #22, #23)
    # -------------------------------------------------------------
    {
        "problem_number": 22,
        "slug": "rat-in-a-maze",
        "title": "Rat in a Maze",
        "topic_slug": "recursion-backtracking",
        "difficulty": "MEDIUM",
        "description": "Consider a rat placed at `(0, 0)` in a square matrix `mat` of order `n * n`. It has to reach the destination at `(n - 1, n - 1)`.\n\nThe rat can move in four directions: `'U'` (up), `'D'` (down), `'L'` (left), and `'R'` (right). The value of cell `mat[i][j]` is `1` if the rat can pass through it, and `0` if it cannot. No cell can be visited more than once in the same path.\n\nFind all possible paths from source to destination in lexicographical order. Print the space-separated paths, or `-1` if no path exists.",
        "constraints": "2 <= n <= 5\nmat[i][j] is either 0 or 1.",
        "input_format": "Line 1: Single integer n.\nNext n lines: n space-separated integers (0 or 1) representing each row of the maze.",
        "output_format": "Space-separated sorted path strings, or -1.",
        "examples": [
            {
                "input": "4\n1 0 0 0\n1 1 0 1\n1 1 0 0\n0 1 1 1",
                "output": "DDRDRR DRDDRR",
                "explanation": "Two valid paths exist to reach (3,3): \"DDRDRR\" and \"DRDDRR\".",
            },
            {
                "input": "2\n1 0\n1 0",
                "output": "-1",
                "explanation": "Destination (1,1) is 0 and cannot be reached.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def find_paths(n: int, mat: list[list[int]]) -> list[str]:
    if mat[0][0] == 0 or mat[n - 1][n - 1] == 0:
        return []
    res = []
    visited = [[False] * n for _ in range(n)]
    
    # Directions in lexicographical order: D, L, R, U
    dirs = [('D', 1, 0), ('L', 0, -1), ('R', 0, 1), ('U', -1, 0)]
    
    def backtrack(r, c, path):
        if r == n - 1 and c == n - 1:
            res.append(path)
            return
        visited[r][c] = True
        for move, dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc] and mat[nr][nc] == 1:
                backtrack(nr, nc, path + move)
        visited[r][c] = False

    backtrack(0, 0, "")
    return sorted(res)

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if lines:
        n = int(lines[0].strip())
        mat = []
        for i in range(1, 1 + n):
            mat.append(list(map(int, lines[i].strip().split())))
        paths = find_paths(n, mat)
        if paths:
            print(" ".join(paths))
        else:
            print("-1")
''',
            "java": '''import java.util.*;

public class Main {
    static ArrayList<String> res = new ArrayList<>();
    static int[] dr = {1, 0, 0, -1};
    static int[] dc = {0, -1, 1, 0};
    static char[] moves = {'D', 'L', 'R', 'U'};

    public static void backtrack(int r, int c, int n, int[][] mat, boolean[][] vis, StringBuilder path) {
        if (r == n - 1 && c == n - 1) {
            res.add(path.toString());
            return;
        }
        vis[r][c] = true;
        for (int i = 0; i < 4; i++) {
            int nr = r + dr[i], nc = c + dc[i];
            if (nr >= 0 && nr < n && nc >= 0 && nc < n && !vis[nr][nc] && mat[nr][nc] == 1) {
                path.append(moves[i]);
                backtrack(nr, nc, n, mat, vis, path);
                path.deleteCharAt(path.length() - 1);
            }
        }
        vis[r][c] = false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int n = sc.nextInt();
            int[][] mat = new int[n][n];
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++) mat[i][j] = sc.nextInt();
            if (mat[0][0] == 1 && mat[n - 1][n - 1] == 1) {
                boolean[][] vis = new boolean[n][n];
                backtrack(0, 0, n, mat, vis, new StringBuilder());
            }
            if (res.isEmpty()) System.out.println("-1");
            else {
                Collections.sort(res);
                System.out.println(String.join(" ", res));
            }
        }
    }
}
''',
        },
        "expected_time_complexity": "O(4^(N^2))",
        "expected_space_complexity": "O(N^2)",
        "hints": [
            "Check if starting cell (0,0) or destination (n-1,n-1) is blocked (0).",
            "Use recursion with a visited 2D boolean array to avoid cycles.",
            "Explore moves in order 'D', 'L', 'R', 'U' to naturally produce lexicographical order.",
        ],
        "editorial": """### Intuition & Approach
The Rat in a Maze problem is a classical backtracking puzzle.
From any cell `(r, c)`:
1. Mark `visited[r][c] = True`.
2. Try moving to all valid unvisited adjacent cells with `mat[nr][nc] == 1`.
3. When reaching `(n-1, n-1)`, save the accumulated direction sequence.
4. Backtrack by resetting `visited[r][c] = False` to allow other paths.

### Complexity Analysis
- **Time Complexity**: `O(4^(N^2))` upper bound.
- **Space Complexity**: `O(N^2)` recursion depth and visited matrix.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75"],
        "test_cases": [
            {"input": "4\n1 0 0 0\n1 1 0 1\n1 1 0 0\n0 1 1 1", "output": "DDRDRR DRDDRR", "is_hidden": False, "order_index": 1},
            {"input": "2\n1 0\n1 0", "output": "-1", "is_hidden": False, "order_index": 2},
            {"input": "2\n1 1\n1 1", "output": "DR RD", "is_hidden": True, "order_index": 3},
        ],
    },
    {
        "problem_number": 23,
        "slug": "n-queens",
        "title": "N-Queens",
        "topic_slug": "recursion-backtracking",
        "difficulty": "HARD",
        "description": "The **n-queens** puzzle is the problem of placing `n` queens on an `n x n` chessboard such that no two queens attack each other.\n\nGiven an integer `n`, return the **total number of distinct solutions** to the n-queens puzzle.",
        "constraints": "1 <= n <= 9",
        "input_format": "A single line containing the integer n.",
        "output_format": "A single integer denoting the number of distinct valid queen placements.",
        "examples": [
            {
                "input": "4",
                "output": "2",
                "explanation": "There are two distinct solutions to the 4-queens puzzle.",
            },
            {
                "input": "1",
                "output": "1",
                "explanation": "A single queen on 1x1 board has 1 solution.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def total_n_queens(n: int) -> int:
    cols = set()
    pos_diag = set() # (r + c)
    neg_diag = set() # (r - c)
    count = 0

    def backtrack(r):
        nonlocal count
        if r == n:
            count += 1
            return
        for c in range(n):
            if c in cols or (r + c) in pos_diag or (r - c) in neg_diag:
                continue
            cols.add(c)
            pos_diag.add(r + c)
            neg_diag.add(r - c)
            backtrack(r + 1)
            cols.remove(c)
            pos_diag.remove(r + c)
            neg_diag.remove(r - c)

    backtrack(0)
    return count

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        n = int(line)
        print(total_n_queens(n))
''',
            "java": '''import java.util.*;

public class Main {
    static int count = 0;
    static Set<Integer> cols = new HashSet<>();
    static Set<Integer> posDiag = new HashSet<>();
    static Set<Integer> negDiag = new HashSet<>();

    public static void backtrack(int r, int n) {
        if (r == n) { count++; return; }
        for (int c = 0; c < n; c++) {
            if (cols.contains(c) || posDiag.contains(r + c) || negDiag.contains(r - c)) continue;
            cols.add(c); posDiag.add(r + c); negDiag.add(r - c);
            backtrack(r + 1, n);
            cols.remove(c); posDiag.remove(r + c); negDiag.remove(r - c);
        }
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int n = sc.nextInt();
            count = 0;
            backtrack(0, n);
            System.out.println(count);
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N!)",
        "expected_space_complexity": "O(N)",
        "hints": [
            "Since each row must have exactly one queen, place row by row from r=0 to n-1.",
            "Use hash sets to track occupied columns, positive diagonals (r + c), and negative diagonals (r - c) in O(1).",
            "When row reaches n, increment solution count and backtrack.",
        ],
        "editorial": """### Intuition & Approach
We place one queen per row. For each cell `(r, c)` in row `r`:
- Column conflict: `c` is already in `cols`.
- Diagonal conflict: `(r + c)` is in `pos_diag` (anti-diagonal) or `(r - c)` is in `neg_diag` (main diagonal).
By recording occupied lines in hash sets, conflict detection takes `O(1)` time.

### Complexity Analysis
- **Time Complexity**: `O(N!)` branching.
- **Space Complexity**: `O(N)` for hash sets and recursion stack.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "4", "output": "2", "is_hidden": False, "order_index": 1},
            {"input": "1", "output": "1", "is_hidden": False, "order_index": 2},
            {"input": "2", "output": "0", "is_hidden": True, "order_index": 3},
            {"input": "8", "output": "92", "is_hidden": True, "order_index": 4},
        ],
    },

    # -------------------------------------------------------------
    # 6. Linked Lists (Need 2: #24, #25)
    # -------------------------------------------------------------
    {
        "problem_number": 24,
        "slug": "detect-cycle-in-a-linked-list",
        "title": "Detect Cycle in a Linked List",
        "topic_slug": "linked-lists",
        "difficulty": "EASY",
        "description": "Given head, the head of a linked list, determine if the linked list has a cycle in it.\n\nThere is a cycle in a linked list if there is some node in the list that can be reached again by continuously following the `next` pointer.\n\nInput representation:\n- Line 1: Space-separated node values.\n- Line 2: 0-indexed position `pos` to which the tail's next pointer connects (-1 if no cycle).\n\nOutput `true` if there is a cycle, otherwise `false`.",
        "constraints": "The number of nodes in the list is in the range [0, 10^4].\n-10^5 <= Node.val <= 10^5\npos is -1 or a valid index in the linked-list.",
        "input_format": "Line 1: Space-separated integers representing node values.\nLine 2: Single integer pos.",
        "output_format": "true or false.",
        "examples": [
            {
                "input": "3 2 0 -4\n1",
                "output": "true",
                "explanation": "There is a cycle in the linked list where tail connects to the 1st node (0-indexed).",
            },
            {
                "input": "1 2\n0",
                "output": "true",
                "explanation": "Tail connects to the 0th node, forming a cycle.",
            },
            {
                "input": "1\n-1",
                "output": "false",
                "explanation": "There is no cycle in the linked list.",
            },
        ],
        "starter_code": {
            "python": '''import sys

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def has_cycle(head: ListNode) -> bool:
    # Floyd's Cycle-Finding Algorithm (Tortoise and Hare)
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if lines:
        vals = list(map(int, lines[0].strip().split())) if lines[0].strip() else []
        pos = int(lines[1].strip()) if len(lines) > 1 and lines[1].strip() else -1
        
        nodes = [ListNode(v) for v in vals]
        for i in range(len(nodes) - 1):
            nodes[i].next = nodes[i + 1]
        if pos != -1 and nodes and pos < len(nodes):
            nodes[-1].next = nodes[pos]
            
        head = nodes[0] if nodes else None
        print("true" if has_cycle(head) else "false")
''',
            "java": '''import java.util.*;

class ListNode {
    int val;
    ListNode next;
    ListNode(int x) { val = x; next = null; }
}

public class Main {
    public static boolean hasCycle(ListNode head) {
        ListNode slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        return false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String l1 = sc.nextLine().trim();
            if (l1.isEmpty()) { System.out.println("false"); return; }
            String[] parts = l1.split("\\s+");
            ListNode[] nodes = new ListNode[parts.length];
            for (int i = 0; i < parts.length; i++) nodes[i] = new ListNode(Integer.parseInt(parts[i]));
            for (int i = 0; i < nodes.length - 1; i++) nodes[i].next = nodes[i + 1];
            int pos = sc.hasNextInt() ? sc.nextInt() : -1;
            if (pos != -1 && pos < nodes.length) nodes[nodes.length - 1].next = nodes[pos];
            System.out.println(hasCycle(nodes.length > 0 ? nodes[0] : null) ? "true" : "false");
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Use two pointers advancing at different speeds: slow moves 1 step, fast moves 2 steps.",
            "If a cycle exists, the fast pointer will eventually lap the slow pointer and they will point to the same node.",
            "If fast reaches null, no cycle exists.",
        ],
        "editorial": """### Intuition & Approach
Floyd's Tortoise and the Hare algorithm uses two pointers moving at speeds 1 and 2 respectively.
If the linked list is acyclic, `fast` reaches the end in `O(N/2)` steps.
If a loop exists, inside the cycle of length `C`, each step reduces the distance between `fast` and `slow` by 1. Therefore, they must meet within at most `C` steps.

### Complexity Analysis
- **Time Complexity**: `O(N)`.
- **Space Complexity**: `O(1)` auxiliary pointers.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "3 2 0 -4\n1", "output": "true", "is_hidden": False, "order_index": 1},
            {"input": "1 2\n0", "output": "true", "is_hidden": False, "order_index": 2},
            {"input": "1\n-1", "output": "false", "is_hidden": False, "order_index": 3},
            {"input": "5 10 15 20\n-1", "output": "false", "is_hidden": True, "order_index": 4},
        ],
    },
    {
        "problem_number": 25,
        "slug": "merge-two-sorted-lists",
        "title": "Merge Two Sorted Lists",
        "topic_slug": "linked-lists",
        "difficulty": "EASY",
        "description": "You are given the heads of two sorted linked lists `list1` and `list2`.\n\nMerge the two lists into one **sorted** list. The list should be made by splicing together the nodes of the first two lists.\n\nOutput the space-separated values of the merged linked list.",
        "constraints": "The number of nodes in both lists is in the range [0, 50].\n-100 <= Node.val <= 100\nBoth list1 and list2 are sorted in non-decreasing order.",
        "input_format": "Line 1: Space-separated integers for list1.\nLine 2: Space-separated integers for list2.",
        "output_format": "Space-separated merged sorted integers.",
        "examples": [
            {
                "input": "1 2 4\n1 3 4",
                "output": "1 1 2 3 4 4",
                "explanation": "Merged list contains elements from both lists in ascending order.",
            },
            {
                "input": "\n0",
                "output": "0",
                "explanation": "Merging empty list with [0] yields 0.",
            },
        ],
        "starter_code": {
            "python": '''import sys

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_two_lists(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(-1)
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 if l1 else l2
    return dummy.next

def build_list(vals):
    dummy = ListNode(0)
    curr = dummy
    for v in vals:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    v1 = list(map(int, lines[0].strip().split())) if len(lines) > 0 and lines[0].strip() else []
    v2 = list(map(int, lines[1].strip().split())) if len(lines) > 1 and lines[1].strip() else []
    merged = merge_two_lists(build_list(v1), build_list(v2))
    res = []
    while merged:
        res.append(str(merged.val))
        merged = merged.next
    print(" ".join(res))
''',
            "java": '''import java.util.*;

class ListNode {
    int val; ListNode next;
    ListNode(int val) { this.val = val; }
}

public class Main {
    public static ListNode mergeTwoLists(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(-1);
        ListNode curr = dummy;
        while (l1 != null && l2 != null) {
            if (l1.val <= l2.val) { curr.next = l1; l1 = l1.next; }
            else { curr.next = l2; l2 = l2.next; }
            curr = curr.next;
        }
        curr.next = (l1 != null) ? l1 : l2;
        return dummy.next;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s1 = sc.hasNextLine() ? sc.nextLine().trim() : "";
        String s2 = sc.hasNextLine() ? sc.nextLine().trim() : "";
        ListNode d1 = new ListNode(0), c1 = d1;
        if (!s1.isEmpty()) {
            for (String p : s1.split("\\s+")) { c1.next = new ListNode(Integer.parseInt(p)); c1 = c1.next; }
        }
        ListNode d2 = new ListNode(0), c2 = d2;
        if (!s2.isEmpty()) {
            for (String p : s2.split("\\s+")) { c2.next = new ListNode(Integer.parseInt(p)); c2 = c2.next; }
        }
        ListNode merged = mergeTwoLists(d1.next, d2.next);
        List<String> res = new ArrayList<>();
        while (merged != null) { res.add(String.valueOf(merged.val)); merged = merged.next; }
        System.out.println(String.join(" ", res));
    }
}
''',
        },
        "expected_time_complexity": "O(N + M)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Use a dummy head node to simplify pointer rewiring without edge cases for head selection.",
            "Compare the current nodes of both lists and link the smaller one to curr.next.",
            "Attach any remaining non-null list directly at the end.",
        ],
        "editorial": """### Intuition & Approach
Using a dummy node simplifies edge cases where the head of the merged list could originate from either `list1` or `list2`.
At each step, we connect `curr.next` to the smaller node and advance that list's pointer. When one list is exhausted, we link the remainder of the other list in `O(1)`.

### Complexity Analysis
- **Time Complexity**: `O(N + M)` where N and M are lengths of the lists.
- **Space Complexity**: `O(1)` auxiliary space.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "1 2 4\n1 3 4", "output": "1 1 2 3 4 4", "is_hidden": False, "order_index": 1},
            {"input": "\n0", "output": "0", "is_hidden": False, "order_index": 2},
            {"input": "5 10 15\n2 3 20", "output": "2 3 5 10 15 20", "is_hidden": True, "order_index": 3},
        ],
    },

    # -------------------------------------------------------------
    # 7. Stacks and Queues (Need 2: #26, #27)
    # -------------------------------------------------------------
    {
        "problem_number": 26,
        "slug": "next-greater-element",
        "title": "Next Greater Element",
        "topic_slug": "stacks-queues",
        "difficulty": "MEDIUM",
        "description": "Given an array `arr` of size `N`, for each element in the array, find the **next greater element** (NGE) to its right.\n\nThe next greater element of an element `x` is the first greater element to its right. If it does not exist, output `-1` for this number.\n\nPrint the space-separated next greater elements for each index.",
        "constraints": "1 <= N <= 10^5\n1 <= arr[i] <= 10^9",
        "input_format": "A single line containing space-separated integers representing arr.",
        "output_format": "Space-separated integers denoting the NGE for each element.",
        "examples": [
            {
                "input": "4 5 2 25",
                "output": "5 25 25 -1",
                "explanation": "Next greater for 4 is 5, for 5 is 25, for 2 is 25, and for 25 is -1.",
            },
            {
                "input": "13 7 6 12",
                "output": "-1 12 12 -1",
                "explanation": "Next greater for 13 is -1, for 7 is 12, for 6 is 12, and for 12 is -1.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def next_greater_elements(arr: list[int]) -> list[int]:
    # Monotonic decreasing stack (stores elements or indices)
    n = len(arr)
    res = [-1] * n
    stack = []  # store indices
    for i in range(n):
        while stack and arr[stack[-1]] < arr[i]:
            idx = stack.pop()
            res[idx] = arr[i]
        stack.append(i)
    return res

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        arr = list(map(int, line.split()))
        ans = next_greater_elements(arr)
        print(" ".join(map(str, ans)))
''',
            "java": '''import java.util.*;

public class Main {
    public static int[] nextGreater(int[] arr) {
        int n = arr.length;
        int[] res = new int[n];
        Arrays.fill(res, -1);
        Stack<Integer> stack = new Stack<>();
        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() && arr[stack.peek()] < arr[i]) {
                res[stack.pop()] = arr[i];
            }
            stack.push(i);
        }
        return res;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] arr = new int[parts.length];
            for (int i = 0; i < parts.length; i++) arr[i] = Integer.parseInt(parts[i]);
            int[] ans = nextGreater(arr);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < ans.length; i++) {
                if (i > 0) sb.append(" ");
                sb.append(ans[i]);
            }
            System.out.println(sb.toString());
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(N)",
        "hints": [
            "A brute force approach checks all rightward elements in O(N^2).",
            "Use a monotonic decreasing stack that holds elements waiting for their next greater element.",
            "When the current number is greater than stack.top(), pop and resolve the top element's NGE.",
        ],
        "editorial": """### Intuition & Approach
By iterating through the array and keeping a monotonic decreasing stack of unresolved indices:
Each time we encounter `arr[i]` greater than `arr[stack.top()]`, `arr[i]` is the immediate first greater element to the right of `stack.top()`. We pop and assign `res[top] = arr[i]`.
Each element is pushed and popped at most once.

### Complexity Analysis
- **Time Complexity**: `O(N)` since each element enters and leaves the stack once.
- **Space Complexity**: `O(N)` auxiliary stack.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "4 5 2 25", "output": "5 25 25 -1", "is_hidden": False, "order_index": 1},
            {"input": "13 7 6 12", "output": "-1 12 12 -1", "is_hidden": False, "order_index": 2},
            {"input": "1 2 3 4 5", "output": "2 3 4 5 -1", "is_hidden": True, "order_index": 3},
            {"input": "5 4 3 2 1", "output": "-1 -1 -1 -1 -1", "is_hidden": True, "order_index": 4},
        ],
    },
    {
        "problem_number": 27,
        "slug": "implement-queue-using-stacks",
        "title": "Implement Queue using Stacks",
        "topic_slug": "stacks-queues",
        "difficulty": "EASY",
        "description": "Implement a first in first out (FIFO) queue using only two stacks. The implemented queue should support `push`, `pop`, `peek`, and `empty`.\n\nInput format is a single line with comma-separated operations:\n- `push X`\n- `pop`\n- `peek`\n- `empty`\n\nOutput space-separated results of the `pop`, `peek`, and `empty` operations.",
        "constraints": "At most 100 calls to push, pop, peek, and empty.\nAll calls to pop and peek are valid.",
        "input_format": "A comma-separated string of operations e.g. push 1, push 2, peek, pop, empty",
        "output_format": "Space-separated outputs of non-push operations.",
        "examples": [
            {
                "input": "push 1, push 2, peek, pop, empty",
                "output": "1 1 false",
                "explanation": "peek returns 1, pop returns 1, queue still has 2 so empty returns false.",
            },
        ],
        "starter_code": {
            "python": '''import sys

class MyQueue:
    def __init__(self):
        self.in_stack = []
        self.out_stack = []

    def push(self, x: int) -> None:
        self.in_stack.append(x)

    def pop(self) -> int:
        self.peek()
        return self.out_stack.pop()

    def peek(self) -> int:
        if not self.out_stack:
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())
        return self.out_stack[-1]

    def empty(self) -> bool:
        return not self.in_stack and not self.out_stack

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        ops = [op.strip() for op in line.split(",") if op.strip()]
        q = MyQueue()
        res = []
        for op in ops:
            parts = op.split()
            cmd = parts[0]
            if cmd == "push":
                q.push(int(parts[1]))
            elif cmd == "pop":
                res.append(str(q.pop()))
            elif cmd == "peek":
                res.append(str(q.peek()))
            elif cmd == "empty":
                res.append("true" if q.empty() else "false")
        print(" ".join(res))
''',
            "java": '''import java.util.*;

class MyQueue {
    Stack<Integer> inStack = new Stack<>();
    Stack<Integer> outStack = new Stack<>();

    public void push(int x) { inStack.push(x); }
    public int pop() { peek(); return outStack.pop(); }
    public int peek() {
        if (outStack.isEmpty()) {
            while (!inStack.isEmpty()) outStack.push(inStack.pop());
        }
        return outStack.peek();
    }
    public boolean empty() { return inStack.isEmpty() && outStack.isEmpty(); }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] ops = sc.nextLine().trim().split(",");
            MyQueue q = new MyQueue();
            List<String> res = new ArrayList<>();
            for (String raw : ops) {
                String op = raw.trim();
                String[] p = op.split("\\s+");
                if (p[0].equals("push")) q.push(Integer.parseInt(p[1]));
                else if (p[0].equals("pop")) res.add(String.valueOf(q.pop()));
                else if (p[0].equals("peek")) res.add(String.valueOf(q.peek()));
                else if (p[0].equals("empty")) res.add(q.empty() ? "true" : "false");
            }
            System.out.println(String.join(" ", res));
        }
    }
}
''',
        },
        "expected_time_complexity": "Amortized O(1)",
        "expected_space_complexity": "O(N)",
        "hints": [
            "Use two stacks: in_stack for push, out_stack for pop/peek.",
            "Transfer elements from in_stack to out_stack ONLY when out_stack is empty.",
            "Each element is transferred at most once, providing amortized O(1) performance.",
        ],
        "editorial": """### Intuition & Approach
Two stacks simulate FIFO ordering:
- `push(x)`: Append to `in_stack`.
- `pop()` / `peek()`: If `out_stack` is empty, pour all elements from `in_stack` to `out_stack`. This reverses their order back to FIFO.
- Each element is moved between stacks at most once throughout its lifecycle, leading to amortized `O(1)` per operation.

### Complexity Analysis
- **Time Complexity**: Amortized `O(1)` for pop/peek, `O(1)` for push.
- **Space Complexity**: `O(N)` elements stored in the two stacks.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75"],
        "test_cases": [
            {"input": "push 1, push 2, peek, pop, empty", "output": "1 1 false", "is_hidden": False, "order_index": 1},
            {"input": "push 10, pop, empty", "output": "10 true", "is_hidden": False, "order_index": 2},
            {"input": "push 1, push 2, push 3, pop, pop, peek", "output": "1 2 3", "is_hidden": True, "order_index": 3},
        ],
    },

    # -------------------------------------------------------------
    # 8. Trees, BSTs, and Heaps (Need 2: #28, #29)
    # -------------------------------------------------------------
    {
        "problem_number": 28,
        "slug": "lowest-common-ancestor-bst",
        "title": "Lowest Common Ancestor in a BST",
        "topic_slug": "trees-heaps",
        "difficulty": "MEDIUM",
        "description": "Given a Binary Search Tree (BST) and two node values `p` and `q`, find the **Lowest Common Ancestor (LCA)** of the two nodes.\n\nAccording to the definition of LCA on Wikipedia: “The lowest common ancestor is defined between two nodes `p` and `q` as the lowest node in `T` that has both `p` and `q` as descendants (where we allow a node to be a descendant of itself).”\n\nInput:\n- Line 1: Space-separated integers representing BST nodes in level order ('null' for missing nodes).\n- Line 2: Two space-separated integers `p` and `q`.\n\nOutput the value of the LCA node as a single integer.",
        "constraints": "The number of nodes in the tree is in the range [2, 10^5].\n-10^9 <= Node.val <= 10^9\nAll Node.val are unique.\np and q will exist in the BST and p != q.",
        "input_format": "Line 1: Space-separated integers in level order (e.g. 6 2 8 0 4 7 9)\nLine 2: Two integers p and q.",
        "output_format": "Single integer representing LCA value.",
        "examples": [
            {
                "input": "6 2 8 0 4 7 9\n2 8",
                "output": "6",
                "explanation": "The LCA of nodes 2 and 8 is 6.",
            },
            {
                "input": "6 2 8 0 4 7 9\n2 4",
                "output": "2",
                "explanation": "The LCA of nodes 2 and 4 is 2, since a node can be a descendant of itself.",
            },
        ],
        "starter_code": {
            "python": '''import sys

class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

def lowest_common_ancestor(root: TreeNode, p: int, q: int) -> int:
    curr = root
    while curr:
        if p < curr.val and q < curr.val:
            curr = curr.left
        elif p > curr.val and q > curr.val:
            curr = curr.right
        else:
            return curr.val
    return -1

def build_bst(vals):
    if not vals:
        return None
    root = TreeNode(int(vals[0]))
    for v in vals[1:]:
        if v == "null": continue
        val = int(v)
        curr = root
        while True:
            if val < curr.val:
                if not curr.left:
                    curr.left = TreeNode(val)
                    break
                curr = curr.left
            else:
                if not curr.right:
                    curr.right = TreeNode(val)
                    break
                curr = curr.right
    return root

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        vals = lines[0].strip().split()
        p, q = map(int, lines[1].strip().split())
        root = build_bst(vals)
        print(lowest_common_ancestor(root, p, q))
''',
            "java": '''import java.util.*;

class TreeNode {
    int val; TreeNode left, right;
    TreeNode(int x) { val = x; }
}

public class Main {
    public static int lowestCommonAncestor(TreeNode root, int p, int q) {
        TreeNode curr = root;
        while (curr != null) {
            if (p < curr.val && q < curr.val) curr = curr.left;
            else if (p > curr.val && q > curr.val) curr = curr.right;
            else return curr.val;
        }
        return -1;
    }

    public static TreeNode buildBST(String[] vals) {
        if (vals.length == 0 || vals[0].equals("null")) return null;
        TreeNode root = new TreeNode(Integer.parseInt(vals[0]));
        for (int i = 1; i < vals.length; i++) {
            if (vals[i].equals("null")) continue;
            int val = Integer.parseInt(vals[i]);
            TreeNode curr = root;
            while (true) {
                if (val < curr.val) {
                    if (curr.left == null) { curr.left = new TreeNode(val); break; }
                    curr = curr.left;
                } else {
                    if (curr.right == null) { curr.right = new TreeNode(val); break; }
                    curr = curr.right;
                }
            }
        }
        return root;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] vals = sc.nextLine().trim().split("\\s+");
            int p = sc.nextInt(), q = sc.nextInt();
            TreeNode root = buildBST(vals);
            System.out.println(lowestCommonAncestor(root, p, q));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(H) where H is tree height",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Take advantage of the BST property: left subtree < root < right subtree.",
            "If both p and q are strictly less than root, LCA must be in the left subtree.",
            "If both p and q are strictly greater than root, LCA must be in the right subtree.",
            "Otherwise, the current root is the split point, which is the LCA.",
        ],
        "editorial": """### Intuition & Approach
Because the tree is a Binary Search Tree:
- If `p` and `q` are both smaller than `curr.val`, the split point lies in `curr.left`.
- If `p` and `q` are both larger than `curr.val`, the split point lies in `curr.right`.
- The first node where `p` and `q` diverge (or one equals `curr.val`) is the Lowest Common Ancestor.

### Complexity Analysis
- **Time Complexity**: `O(H)` where `H` is the height of the BST (`O(log N)` for balanced BST, `O(N)` worst case).
- **Space Complexity**: `O(1)` iterative traversal.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "6 2 8 0 4 7 9\n2 8", "output": "6", "is_hidden": False, "order_index": 1},
            {"input": "6 2 8 0 4 7 9\n2 4", "output": "2", "is_hidden": False, "order_index": 2},
            {"input": "2 1\n2 1", "output": "2", "is_hidden": True, "order_index": 3},
            {"input": "5 3 6 2 4\n4 2", "output": "3", "is_hidden": True, "order_index": 4},
        ],
    },
    {
        "problem_number": 29,
        "slug": "kth-largest-element-in-an-array",
        "title": "Kth Largest Element in an Array",
        "topic_slug": "trees-heaps",
        "difficulty": "MEDIUM",
        "description": "Given an integer array `nums` and an integer `k`, return the `k`th largest element in the array.\n\nNote that it is the `k`th largest element in sorted order, not the `k`th distinct element.\n\nCan you solve it without sorting in `O(N log k)` time using a min-heap?",
        "constraints": "1 <= k <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
        "input_format": "Line 1: Space-separated integers representing nums.\nLine 2: Single integer k.",
        "output_format": "A single integer denoting the kth largest element.",
        "examples": [
            {
                "input": "3 2 1 5 6 4\n2",
                "output": "5",
                "explanation": "Sorted order is [6, 5, 4, 3, 2, 1]. The 2nd largest element is 5.",
            },
            {
                "input": "3 2 3 1 2 4 5 5 6\n4",
                "output": "4",
                "explanation": "Sorted order is [6, 5, 5, 4, 3, 3, 2, 2, 1]. The 4th largest element is 4.",
            },
        ],
        "starter_code": {
            "python": '''import sys
import heapq

def find_kth_largest(nums: list[int], k: int) -> int:
    # Min-heap of size k
    min_heap = []
    for x in nums:
        heapq.heappush(min_heap, x)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
    return min_heap[0]

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        nums = list(map(int, lines[0].strip().split()))
        k = int(lines[1].strip())
        print(find_kth_largest(nums, k))
''',
            "java": '''import java.util.*;

public class Main {
    public static int findKthLargest(int[] nums, int k) {
        PriorityQueue<Integer> minHeap = new PriorityQueue<>();
        for (int x : nums) {
            minHeap.offer(x);
            if (minHeap.size() > k) minHeap.poll();
        }
        return minHeap.peek();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] parts = sc.nextLine().trim().split("\\s+");
            int[] nums = new int[parts.length];
            for (int i = 0; i < parts.length; i++) nums[i] = Integer.parseInt(parts[i]);
            int k = sc.nextInt();
            System.out.println(findKthLargest(nums, k));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N log K)",
        "expected_space_complexity": "O(K)",
        "hints": [
            "Maintaining a min-heap of size k stores the k largest elements seen so far.",
            "The top of the min-heap is the smallest of the k largest elements, which is the kth largest.",
            "For each incoming number, push and if heap size exceeds k, pop.",
        ],
        "editorial": """### Intuition & Approach
Using a min-heap of capacity `k`:
1. Push each element from `nums` into the min-heap.
2. If the heap size exceeds `k`, remove the smallest element (`heappop()`).
3. After processing all elements, the min-heap contains the `k` largest elements in the array, and the top element is the `k`th largest.

### Complexity Analysis
- **Time Complexity**: `O(N log K)` because each heap operation costs `O(log K)`.
- **Space Complexity**: `O(K)` to store the min-heap.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "3 2 1 5 6 4\n2", "output": "5", "is_hidden": False, "order_index": 1},
            {"input": "3 2 3 1 2 4 5 5 6\n4", "output": "4", "is_hidden": False, "order_index": 2},
            {"input": "1\n1", "output": "1", "is_hidden": True, "order_index": 3},
            {"input": "-1 -2 -3 -4\n2", "output": "-2", "is_hidden": True, "order_index": 4},
        ],
    },

    # -------------------------------------------------------------
    # 9. Graphs and Graph Algorithms (Need 2: #30, #31)
    # -------------------------------------------------------------
    {
        "problem_number": 30,
        "slug": "bfs-traversal-of-graph",
        "title": "Breadth First Search (BFS) of Graph",
        "topic_slug": "graphs",
        "difficulty": "EASY",
        "description": "Given a connected undirected graph represented by an adjacency list and number of vertices `V`, perform a **Breadth First Traversal** starting from vertex `0`.\n\nVisit neighbors in ascending numerical order.\n\nPrint the space-separated vertex sequence visited during BFS.",
        "constraints": "1 <= V, E <= 10^4",
        "input_format": "Line 1: Two integers V and E representing vertices and edges.\nNext E lines: Two integers u and v denoting an undirected edge between u and v.",
        "output_format": "Space-separated sequence of vertices in BFS traversal order.",
        "examples": [
            {
                "input": "5 4\n0 1\n0 2\n0 3\n2 4",
                "output": "0 1 2 3 4",
                "explanation": "Starting at 0: visit 1, 2, 3. From 2: visit 4. Output: 0 1 2 3 4.",
            },
        ],
        "starter_code": {
            "python": '''import sys
from collections import deque

def bfs_of_graph(V: int, adj: list[list[int]]) -> list[int]:
    visited = [False] * V
    queue = deque([0])
    visited[0] = True
    traversal = []
    
    while queue:
        node = queue.popleft()
        traversal.append(node)
        for neighbor in sorted(adj[node]):
            if not visited[neighbor]:
                visited[neighbor] = True
                queue.append(neighbor)
    return traversal

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if lines:
        V, E = map(int, lines[0].strip().split())
        adj = [[] for _ in range(V)]
        for i in range(1, 1 + E):
            if i < len(lines) and lines[i].strip():
                u, v = map(int, lines[i].strip().split())
                adj[u].append(v)
                adj[v].append(u)
        res = bfs_of_graph(V, adj)
        print(" ".join(map(str, res)))
''',
            "java": '''import java.util.*;

public class Main {
    public static List<Integer> bfs(int V, List<List<Integer>> adj) {
        boolean[] vis = new boolean[V];
        Queue<Integer> q = new LinkedList<>();
        List<Integer> ans = new ArrayList<>();
        vis[0] = true;
        q.offer(0);
        while (!q.isEmpty()) {
            int node = q.poll();
            ans.add(node);
            List<Integer> neighbors = new ArrayList<>(adj.get(node));
            Collections.sort(neighbors);
            for (int nxt : neighbors) {
                if (!vis[nxt]) {
                    vis[nxt] = true;
                    q.offer(nxt);
                }
            }
        }
        return ans;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int V = sc.nextInt(), E = sc.nextInt();
            List<List<Integer>> adj = new ArrayList<>();
            for (int i = 0; i < V; i++) adj.add(new ArrayList<>());
            for (int i = 0; i < E; i++) {
                int u = sc.nextInt(), v = sc.nextInt();
                adj.get(u).add(v);
                adj.get(v).add(u);
            }
            List<Integer> ans = bfs(V, adj);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < ans.size(); i++) {
                if (i > 0) sb.append(" ");
                sb.append(ans.get(i));
            }
            System.out.println(sb.toString());
        }
    }
}
''',
        },
        "expected_time_complexity": "O(V + E)",
        "expected_space_complexity": "O(V)",
        "hints": [
            "Use a FIFO queue and a boolean visited array initialized to false.",
            "Mark vertex 0 as visited and enqueue it.",
            "Dequeue the current node, record it, and enqueue all its unvisited neighbors.",
        ],
        "editorial": """### Intuition & Approach
Breadth First Search explores the graph level-by-level using a FIFO queue.
We mark vertices as visited upon enqueuing to prevent duplicate additions.
Processing each vertex takes `O(1)` and each edge is examined once in adjacency list representation.

### Complexity Analysis
- **Time Complexity**: `O(V + E)` where V is vertices and E is edges.
- **Space Complexity**: `O(V)` queue and visited tracking.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75"],
        "test_cases": [
            {"input": "5 4\n0 1\n0 2\n0 3\n2 4", "output": "0 1 2 3 4", "is_hidden": False, "order_index": 1},
            {"input": "3 2\n0 1\n0 2", "output": "0 1 2", "is_hidden": False, "order_index": 2},
            {"input": "4 3\n0 1\n1 2\n2 3", "output": "0 1 2 3", "is_hidden": True, "order_index": 3},
        ],
    },
    {
        "problem_number": 31,
        "slug": "detect-cycle-in-an-undirected-graph",
        "title": "Detect Cycle in an Undirected Graph",
        "topic_slug": "graphs",
        "difficulty": "MEDIUM",
        "description": "Given an undirected graph with `V` vertices and `E` edges, determine whether the graph contains a **cycle** or not.\n\nOutput `true` if a cycle exists, and `false` otherwise.",
        "constraints": "1 <= V <= 10^5\n0 <= E <= 10^5",
        "input_format": "Line 1: Two space-separated integers V and E.\nNext E lines: Two space-separated integers u and v denoting an edge.",
        "output_format": "true or false.",
        "examples": [
            {
                "input": "5 5\n0 1\n1 2\n2 3\n3 4\n4 1",
                "output": "true",
                "explanation": "Vertices 1-2-3-4-1 form a cycle.",
            },
            {
                "input": "4 3\n0 1\n1 2\n2 3",
                "output": "false",
                "explanation": "The graph is a linear tree with no cycles.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def is_cycle(V: int, adj: list[list[int]]) -> bool:
    visited = [False] * V
    
    def dfs(node, parent):
        visited[node] = True
        for nxt in adj[node]:
            if not visited[nxt]:
                if dfs(nxt, node):
                    return True
            elif nxt != parent:
                return True
        return False

    for i in range(V):
        if not visited[i]:
            if dfs(i, -1):
                return True
    return False

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if lines:
        V, E = map(int, lines[0].strip().split())
        adj = [[] for _ in range(V)]
        for i in range(1, 1 + E):
            if i < len(lines) and lines[i].strip():
                u, v = map(int, lines[i].strip().split())
                adj[u].append(v)
                adj[v].append(u)
        print("true" if is_cycle(V, adj) else "false")
''',
            "java": '''import java.util.*;

public class Main {
    public static boolean dfs(int node, int parent, boolean[] vis, List<List<Integer>> adj) {
        vis[node] = true;
        for (int nxt : adj.get(node)) {
            if (!vis[nxt]) {
                if (dfs(nxt, node, vis, adj)) return true;
            } else if (nxt != parent) {
                return true;
            }
        }
        return false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int V = sc.nextInt(), E = sc.nextInt();
            List<List<Integer>> adj = new ArrayList<>();
            for (int i = 0; i < V; i++) adj.add(new ArrayList<>());
            for (int i = 0; i < E; i++) {
                int u = sc.nextInt(), v = sc.nextInt();
                adj.get(u).add(v);
                adj.get(v).add(u);
            }
            boolean[] vis = new boolean[V];
            boolean hasCycle = false;
            for (int i = 0; i < V; i++) {
                if (!vis[i]) {
                    if (dfs(i, -1, vis, adj)) { hasCycle = true; break; }
                }
            }
            System.out.println(hasCycle ? "true" : "false");
        }
    }
}
''',
        },
        "expected_time_complexity": "O(V + E)",
        "expected_space_complexity": "O(V)",
        "hints": [
            "In an undirected graph, an edge leads back to the parent by default; disregard the immediate parent.",
            "If an adjacent vertex is already visited and is NOT the parent of the current node, a cycle exists.",
            "Be sure to loop through all disconnected components from 0 to V-1.",
        ],
        "editorial": """### Intuition & Approach
Using DFS or BFS with parent tracking:
For each unvisited component, we traverse neighbors.
If neighbor `nxt` has already been visited and `nxt != parent`, then `nxt` was reached via another branch, completing a cycle.

### Complexity Analysis
- **Time Complexity**: `O(V + E)` standard traversal.
- **Space Complexity**: `O(V)` visited array and call stack.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "5 5\n0 1\n1 2\n2 3\n3 4\n4 1", "output": "true", "is_hidden": False, "order_index": 1},
            {"input": "4 3\n0 1\n1 2\n2 3", "output": "false", "is_hidden": False, "order_index": 2},
            {"input": "3 3\n0 1\n1 2\n2 0", "output": "true", "is_hidden": True, "order_index": 3},
            {"input": "1 0", "output": "false", "is_hidden": True, "order_index": 4},
        ],
    },

    # -------------------------------------------------------------
    # 10. Greedy Algorithms (Need 2: #32, #33)
    # -------------------------------------------------------------
    {
        "problem_number": 32,
        "slug": "activity-selection-problem",
        "title": "Activity Selection Problem",
        "topic_slug": "greedy",
        "difficulty": "MEDIUM",
        "description": "You are given `n` activities with their start and finish times. Select the **maximum number of activities** that can be performed by a single person, assuming that a person can only work on a single activity at a time.\n\nInput format:\n- Line 1: Space-separated integers representing start times.\n- Line 2: Space-separated integers representing finish times.\n\nOutput a single integer representing the maximum count of non-overlapping activities.",
        "constraints": "1 <= n <= 10^5\n1 <= start[i] <= finish[i] <= 10^9",
        "input_format": "Line 1: Space-separated start times.\nLine 2: Space-separated finish times.",
        "output_format": "Single integer denoting max activities.",
        "examples": [
            {
                "input": "1 3 0 5 8 5\n2 4 6 7 9 9",
                "output": "4",
                "explanation": "Activities selected: (1, 2), (3, 4), (5, 7), (8, 9). Total 4 activities.",
            },
            {
                "input": "10 12 20\n20 25 30",
                "output": "2",
                "explanation": "Activities (10, 20) and (20, 30) can be performed. Total 2 activities.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def max_activities(start: list[int], finish: list[int]) -> int:
    # Pair and sort by finish time
    activities = sorted(zip(start, finish), key=lambda x: x[1])
    count = 0
    last_finish = -1
    for s, f in activities:
        if s >= last_finish:
            count += 1
            last_finish = f
    return count

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        start = list(map(int, lines[0].strip().split()))
        finish = list(map(int, lines[1].strip().split()))
        print(max_activities(start, finish))
''',
            "java": '''import java.util.*;

public class Main {
    static class Activity {
        int start, finish;
        Activity(int s, int f) { start = s; finish = f; }
    }

    public static int maxActivities(int[] start, int[] finish) {
        int n = start.length;
        Activity[] arr = new Activity[n];
        for (int i = 0; i < n; i++) arr[i] = new Activity(start[i], finish[i]);
        Arrays.sort(arr, (a, b) -> Integer.compare(a.finish, b.finish));
        int count = 0, lastFinish = -1;
        for (Activity act : arr) {
            if (act.start >= lastFinish) {
                count++;
                lastFinish = act.finish;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] s1 = sc.nextLine().trim().split("\\s+");
            String[] s2 = sc.nextLine().trim().split("\\s+");
            int[] start = new int[s1.length], finish = new int[s2.length];
            for (int i = 0; i < s1.length; i++) start[i] = Integer.parseInt(s1[i]);
            for (int i = 0; i < s2.length; i++) finish[i] = Integer.parseInt(s2[i]);
            System.out.println(maxActivities(start, finish));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N log N)",
        "expected_space_complexity": "O(N)",
        "hints": [
            "Greedy choice: always select the activity that finishes earliest, leaving maximum time for remaining tasks.",
            "Sort all activities primarily by their finish times.",
            "Iterate through sorted intervals: pick activity if start >= last_finish_time.",
        ],
        "editorial": """### Intuition & Approach
The Activity Selection problem demonstrates the greedy choice property:
Choosing the activity with the earliest finish time leaves the maximal remaining time window for future activities.
By sorting intervals by finish time in `O(N log N)`, a single linear scan yields the globally optimal count.

### Complexity Analysis
- **Time Complexity**: `O(N log N)` due to sorting.
- **Space Complexity**: `O(N)` for paired interval representations.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "1 3 0 5 8 5\n2 4 6 7 9 9", "output": "4", "is_hidden": False, "order_index": 1},
            {"input": "10 12 20\n20 25 30", "output": "2", "is_hidden": False, "order_index": 2},
            {"input": "1 2 3\n2 3 4", "output": "3", "is_hidden": True, "order_index": 3},
        ],
    },
    {
        "problem_number": 33,
        "slug": "gas-station-circular-tour",
        "title": "Gas Station (Circular Tour)",
        "topic_slug": "greedy",
        "difficulty": "MEDIUM",
        "description": "There are `n` gas stations along a circular route, where the amount of gas at the `i`th station is `gas[i]`.\n\nYou have a car with an unlimited gas tank and it costs `cost[i]` of gas to travel from the `i`th station to its next `(i + 1)`th station. You begin the journey with an empty tank at one of the gas stations.\n\nGiven two integer arrays `gas` and `cost`, return the **starting gas station's index** if you can travel around the circuit once in the clockwise direction, otherwise return `-1`. If there exists a solution, it is guaranteed to be unique.",
        "constraints": "n == gas.length == cost.length\n1 <= n <= 10^5\n0 <= gas[i], cost[i] <= 10^4",
        "input_format": "Line 1: Space-separated integers representing gas.\nLine 2: Space-separated integers representing cost.",
        "output_format": "Single integer denoting starting index or -1.",
        "examples": [
            {
                "input": "1 2 3 4 5\n3 4 5 1 2",
                "output": "3",
                "explanation": "Start at station 3 (index 3). Tank = 0 + 4 = 4. Cost to st 4 is 1. Tank = 4 - 1 + 5 = 8. Continue circular tour successfully.",
            },
            {
                "input": "2 3 4\n3 4 3",
                "output": "-1",
                "explanation": "Total gas (9) is less than total cost (10), so no starting station can complete the circuit.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
    if sum(gas) < sum(cost):
        return -1
    total_tank = 0
    curr_tank = 0
    start_idx = 0
    for i in range(len(gas)):
        net = gas[i] - cost[i]
        total_tank += net
        curr_tank += net
        if curr_tank < 0:
            start_idx = i + 1
            curr_tank = 0
    return start_idx if total_tank >= 0 else -1

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        gas = list(map(int, lines[0].strip().split()))
        cost = list(map(int, lines[1].strip().split()))
        print(can_complete_circuit(gas, cost))
''',
            "java": '''import java.util.*;

public class Main {
    public static int canCompleteCircuit(int[] gas, int[] cost) {
        int totalTank = 0, currTank = 0, startIdx = 0;
        for (int i = 0; i < gas.length; i++) {
            int net = gas[i] - cost[i];
            totalTank += net;
            currTank += net;
            if (currTank < 0) {
                startIdx = i + 1;
                currTank = 0;
            }
        }
        return totalTank >= 0 ? startIdx : -1;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] s1 = sc.nextLine().trim().split("\\s+");
            String[] s2 = sc.nextLine().trim().split("\\s+");
            int[] gas = new int[s1.length], cost = new int[s2.length];
            for (int i = 0; i < s1.length; i++) gas[i] = Integer.parseInt(s1[i]);
            for (int i = 0; i < s2.length; i++) cost[i] = Integer.parseInt(s2[i]);
            System.out.println(canCompleteCircuit(gas, cost));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(N)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "If sum(gas) < sum(cost), it is mathematically impossible to complete the circuit regardless of starting point.",
            "If you start at A and fail at B, no station between A and B can reach B either.",
            "Reset your starting station to B + 1 and reset current tank to 0.",
        ],
        "editorial": """### Intuition & Approach
1. If the total gas across all stations is less than the total cost, completing the circuit is impossible (`return -1`).
2. If starting at index `A` leads to a negative tank at station `B`, then no station between `A` and `B` could have completed the circuit either because entering them with surplus gas was already insufficient. Thus, the next possible start is `B + 1`.

### Complexity Analysis
- **Time Complexity**: `O(N)` one pass.
- **Space Complexity**: `O(1)` memory.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "1 2 3 4 5\n3 4 5 1 2", "output": "3", "is_hidden": False, "order_index": 1},
            {"input": "2 3 4\n3 4 3", "output": "-1", "is_hidden": False, "order_index": 2},
            {"input": "5 1 2 3 4\n4 4 1 5 1", "output": "4", "is_hidden": True, "order_index": 3},
        ],
    },

    # -------------------------------------------------------------
    # 11. Dynamic Programming (Need 1: #34)
    # -------------------------------------------------------------
    {
        "problem_number": 34,
        "slug": "longest-common-subsequence",
        "title": "Longest Common Subsequence (LCS)",
        "topic_slug": "dynamic-programming",
        "difficulty": "MEDIUM",
        "description": "Given two strings `text1` and `text2`, return the length of their **longest common subsequence**. If there is no common subsequence, return `0`.\n\nA **subsequence** of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.\n\nA **common subsequence** of two strings is a subsequence that is common to both strings.",
        "constraints": "1 <= text1.length, text2.length <= 1000\ntext1 and text2 consist of only lowercase English characters.",
        "input_format": "Line 1: String text1.\nLine 2: String text2.",
        "output_format": "Single integer denoting the length of the LCS.",
        "examples": [
            {
                "input": "abcde\nace",
                "output": "3",
                "explanation": "The longest common subsequence is \"ace\" and its length is 3.",
            },
            {
                "input": "abc\nabc",
                "output": "3",
                "explanation": "The longest common subsequence is \"abc\" and its length is 3.",
            },
            {
                "input": "abc\ndef",
                "output": "0",
                "explanation": "There is no such common subsequence, so the result is 0.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def longest_common_subsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    # 2D DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        t1 = lines[0].strip()
        t2 = lines[1].strip()
        print(longest_common_subsequence(t1, t2))
''',
            "java": '''import java.util.*;

public class Main {
    public static int longestCommonSubsequence(String text1, String text2) {
        int m = text1.length(), n = text2.length();
        int[][] dp = new int[m + 1][n + 1];
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (text1.charAt(i - 1) == text2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                }
            }
        }
        return dp[m][n];
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String t1 = sc.nextLine().trim();
            String t2 = sc.hasNextLine() ? sc.nextLine().trim() : "";
            System.out.println(longestCommonSubsequence(t1, t2));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(M * N)",
        "expected_space_complexity": "O(M * N) or O(min(M, N))",
        "hints": [
            "Let dp[i][j] represent the length of the LCS of text1[0..i-1] and text2[0..j-1].",
            "If text1[i-1] == text2[j-1], then dp[i][j] = dp[i-1][j-1] + 1.",
            "Otherwise, dp[i][j] = max(dp[i-1][j], dp[i][j-1]).",
        ],
        "editorial": """### Intuition & Approach
For two strings `text1` of length `M` and `text2` of length `N`:
- If current characters match (`text1[i-1] == text2[j-1]`), they contribute 1 to the LCS of prefixes: `dp[i][j] = dp[i-1][j-1] + 1`.
- If they do not match, the LCS is the best achieved by omitting either character: `max(dp[i-1][j], dp[i][j-1])`.

### Complexity Analysis
- **Time Complexity**: `O(M * N)`.
- **Space Complexity**: `O(M * N)` table (reducible to `O(min(M, N))` space).
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "abcde\nace", "output": "3", "is_hidden": False, "order_index": 1},
            {"input": "abc\nabc", "output": "3", "is_hidden": False, "order_index": 2},
            {"input": "abc\ndef", "output": "0", "is_hidden": False, "order_index": 3},
            {"input": "oxcp\nyozxco", "output": "2", "is_hidden": True, "order_index": 4},
        ],
    },

    # -------------------------------------------------------------
    # 12. Tries and Bit Manipulation (Need 2: #35, #36)
    # -------------------------------------------------------------
    {
        "problem_number": 35,
        "slug": "number-of-1-bits",
        "title": "Number of 1 Bits (Brian Kernighan's Algorithm)",
        "topic_slug": "tries-bit-manipulation",
        "difficulty": "EASY",
        "description": "Write a function that takes the binary representation of a positive integer `n` and returns the number of set bits (`'1'`s) it has (also known as the **Hamming weight**).\n\nSolve it in `O(set_bits)` time using Brian Kernighan's bit-clearing trick (`n & (n - 1)`).",
        "constraints": "1 <= n <= 2^31 - 1",
        "input_format": "A single line containing the positive integer n.",
        "output_format": "Single integer denoting the count of set bits.",
        "examples": [
            {
                "input": "11",
                "output": "3",
                "explanation": "Binary of 11 is 1011, which has 3 set bits.",
            },
            {
                "input": "128",
                "output": "1",
                "explanation": "Binary of 128 is 10000000, which has 1 set bit.",
            },
            {
                "input": "2147483645",
                "output": "30",
                "explanation": "Binary representation has 30 set bits.",
            },
        ],
        "starter_code": {
            "python": '''import sys

def hamming_weight(n: int) -> int:
    # Brian Kernighan's Algorithm: n & (n - 1) unsets the lowest set bit
    count = 0
    while n:
        n &= (n - 1)
        count += 1
    return count

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        n = int(line)
        print(hamming_weight(n))
''',
            "java": '''import java.util.*;

public class Main {
    public static int hammingWeight(int n) {
        int count = 0;
        while (n != 0) {
            n &= (n - 1);
            count++;
        }
        return count;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int n = sc.nextInt();
            System.out.println(hammingWeight(n));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(number of set bits)",
        "expected_space_complexity": "O(1)",
        "hints": [
            "Subtracting 1 from a number flips all the bits after the rightmost set bit, including the rightmost set bit itself.",
            "Therefore, n & (n - 1) clears the lowest set bit in O(1).",
            "Count how many times you can clear the lowest set bit before n becomes 0.",
        ],
        "editorial": """### Intuition & Approach
Brian Kernighan's Algorithm runs in time proportional to the number of set bits (rather than all 32 bits):
In each step, `n = n & (n - 1)` flips the least significant set bit of `n` to `0`.
We increment the counter until `n == 0`.

### Complexity Analysis
- **Time Complexity**: `O(k)` where `k` is the count of set bits (at most 32).
- **Space Complexity**: `O(1)` constant memory.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "11", "output": "3", "is_hidden": False, "order_index": 1},
            {"input": "128", "output": "1", "is_hidden": False, "order_index": 2},
            {"input": "2147483645", "output": "30", "is_hidden": False, "order_index": 3},
            {"input": "1", "output": "1", "is_hidden": True, "order_index": 4},
            {"input": "7", "output": "3", "is_hidden": True, "order_index": 5},
        ],
    },
    {
        "problem_number": 36,
        "slug": "implement-trie-prefix-tree",
        "title": "Implement Trie (Prefix Tree)",
        "topic_slug": "tries-bit-manipulation",
        "difficulty": "MEDIUM",
        "description": "A **trie** (pronounced as \"try\") or **prefix tree** is a tree data structure used to efficiently store and retrieve keys in a dataset of strings. There are various applications of this data structure, such as autocomplete and spellchecker.\n\nImplement the Trie with `insert`, `search`, and `startsWith` methods.\n\nInput format is comma-separated commands:\n- `insert word`\n- `search word`\n- `startsWith prefix`\n\nOutput space-separated results of the `search` and `startsWith` queries (`true` or `false`).",
        "constraints": "1 <= word.length, prefix.length <= 2000\nword and prefix consist only of lowercase English letters.\nAt most 10^4 calls in total will be made to insert, search, and startsWith.",
        "input_format": "A comma-separated list of commands e.g. insert apple, search apple, search app, startsWith app, insert app, search app",
        "output_format": "Space-separated true/false values.",
        "examples": [
            {
                "input": "insert apple, search apple, search app, startsWith app, insert app, search app",
                "output": "true false true true",
                "explanation": "search(apple)->true, search(app)->false, startsWith(app)->true, after insert(app), search(app)->true.",
            },
        ],
        "starter_code": {
            "python": '''import sys

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        curr = self.root
        for char in word:
            if char not in curr.children:
                curr.children[char] = TrieNode()
            curr = curr.children[char]
        curr.is_end_of_word = True

    def search(self, word: str) -> bool:
        curr = self.root
        for char in word:
            if char not in curr.children:
                return False
            curr = curr.children[char]
        return curr.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        curr = self.root
        for char in prefix:
            if char not in curr.children:
                return False
            curr = curr.children[char]
        return True

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if line:
        ops = [op.strip() for op in line.split(",") if op.strip()]
        trie = Trie()
        res = []
        for op in ops:
            parts = op.split()
            cmd = parts[0]
            arg = parts[1]
            if cmd == "insert":
                trie.insert(arg)
            elif cmd == "search":
                res.append("true" if trie.search(arg) else "false")
            elif cmd == "startsWith":
                res.append("true" if trie.starts_with(arg) else "false")
        print(" ".join(res))
''',
            "java": '''import java.util.*;

class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    boolean isEndOfWord = false;
}

class Trie {
    TrieNode root = new TrieNode();
    public void insert(String word) {
        TrieNode curr = root;
        for (char c : word.toCharArray()) {
            curr.children.putIfAbsent(c, new TrieNode());
            curr = curr.children.get(c);
        }
        curr.isEndOfWord = true;
    }
    public boolean search(String word) {
        TrieNode curr = root;
        for (char c : word.toCharArray()) {
            if (!curr.children.containsKey(c)) return false;
            curr = curr.children.get(c);
        }
        return curr.isEndOfWord;
    }
    public boolean startsWith(String prefix) {
        TrieNode curr = root;
        for (char c : prefix.toCharArray()) {
            if (!curr.children.containsKey(c)) return false;
            curr = curr.children.get(c);
        }
        return true;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextLine()) {
            String[] ops = sc.nextLine().trim().split(",");
            Trie trie = new Trie();
            List<String> res = new ArrayList<>();
            for (String raw : ops) {
                String[] p = raw.trim().split("\\s+");
                if (p[0].equals("insert")) trie.insert(p[1]);
                else if (p[0].equals("search")) res.add(trie.search(p[1]) ? "true" : "false");
                else if (p[0].equals("startsWith")) res.add(trie.startsWith(p[1]) ? "true" : "false");
            }
            System.out.println(String.join(" ", res));
        }
    }
}
''',
        },
        "expected_time_complexity": "O(L) per operation where L is word/prefix length",
        "expected_space_complexity": "O(Total characters inserted)",
        "hints": [
            "A Trie node contains a map/array of child nodes and a boolean flag is_end_of_word.",
            "For insert, traverse or instantiate child nodes character by character and mark is_end_of_word = true on the final node.",
            "For search, all characters must match and is_end_of_word must be true.",
            "For startsWith, all prefix characters must match regardless of is_end_of_word.",
        ],
        "editorial": """### Intuition & Approach
A Trie stores strings character by character down a tree where each node represents a character transition.
- `insert(word)`: Traverses or creates nodes for each character and sets `is_end_of_word = true` at the leaf.
- `search(word)`: Traverses each character. Returns `true` only if all nodes exist and the terminal node has `is_end_of_word == true`.
- `startsWith(prefix)`: Traverses prefix characters. If all nodes exist, returns `true`.

### Complexity Analysis
- **Time Complexity**: `O(L)` where L is the length of the string queried or inserted.
- **Space Complexity**: `O(N * L)` in the worst case for N distinct strings of length L.
""",
        "is_problem_of_the_day": False,
        "sheet_tags": ["Core 75", "Blind 50"],
        "test_cases": [
            {"input": "insert apple, search apple, search app, startsWith app, insert app, search app", "output": "true false true true", "is_hidden": False, "order_index": 1},
            {"input": "insert placement, search place, startsWith place", "output": "false true", "is_hidden": False, "order_index": 2},
            {"input": "insert cat, insert car, search cat, search car, search can", "output": "true true false", "is_hidden": True, "order_index": 3},
        ],
    },
]


def seed_gfg_problems():
    db = SessionLocal()
    try:
        # Load topic map
        topics = db.query(DSATopic).all()
        topic_map = {t.slug: t for t in topics}

        print(f"Upserting {len(GFG_NEW_PROBLEMS)} GeeksforGeeks placement problems...")
        for p in GFG_NEW_PROBLEMS:
            topic = topic_map.get(p["topic_slug"])
            if not topic:
                print(f"Warning: Topic slug {p['topic_slug']} not found! Skipping {p['title']}")
                continue

            existing_p = db.query(DSAProblem).filter(DSAProblem.slug == p["slug"]).first()
            if not existing_p:
                existing_p = DSAProblem(
                    problem_number=p["problem_number"],
                    slug=p["slug"],
                    title=p["title"],
                    topic_id=topic.id,
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
                print(f"Added Problem #{p['problem_number']}: {p['title']} [{p['difficulty']}] to topic '{topic.name}'")
            else:
                existing_p.problem_number = p["problem_number"]
                existing_p.title = p["title"]
                existing_p.topic_id = topic.id
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
                print(f"Updated Problem #{p['problem_number']}: {p['title']}")

            # Refresh test cases
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
        print("Successfully committed all GFG problems and test cases!")

        # Validation per topic
        print("\n--- DSA TOPIC PROBLEM DISTRIBUTION AUDIT ---")
        all_topics = db.query(DSATopic).order_by(DSATopic.order_index).all()
        total_p = 0
        for t in all_topics:
            t_probs = db.query(DSAProblem).filter(DSAProblem.topic_id == t.id).order_by(DSAProblem.problem_number).all()
            total_p += len(t_probs)
            prob_names = [f"#{p.problem_number} {p.title} ({p.difficulty})" for p in t_probs]
            status_flag = "OK (3)" if len(t_probs) == 3 else f"MISMATCH ({len(t_probs)})"
            print(f"[{status_flag}] {t.name}:")
            for pn in prob_names:
                print(f"    - {pn}")

        print(f"\nTotal Problems in Database: {total_p} across {len(all_topics)} topics.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_gfg_problems()
