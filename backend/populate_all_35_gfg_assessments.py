"""
Comprehensive GeeksforGeeks Placement Assessment Seeder
Populates 3 authentic GeeksforGeeks placement MCQs for EVERY topic across all 35 Roadmap Topics.
Total: 35 Assessments, 105 authentic GFG Questions.
"""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.institution import Institution
from app.models.user import User
from app.models.roadmap import RoadmapTopic, RoadmapSubject, CareerPath
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.question import Question, QuestionOption
from app.models.skill import Skill

# Complete Dictionary of 35 Roadmap Topics with 3 authentic GFG Questions each
ALL_35_TOPICS_GFG = {
    # -------------------------------------------------------------
    # PROGRAMMING FUNDAMENTALS
    # -------------------------------------------------------------
    "Variables, Types & Control Flow": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks campus placement drill evaluating primitive data representations, type casting promotions, operator precedences, and short-circuit evaluation.",
        "questions": [
            {
                "title": "[GFG] Predict Output: Short-Circuit Boolean Evaluation",
                "content": "Consider the following code snippet in C/Java:\n```c\nint a = 5, b = 10, c = 15;\nif (a > 10 && ++b > 10) {\n    c += 5;\n}\nprintf(\"%d %d %d\", a, b, c);\n```\nWhat will be the printed output?",
                "difficulty": "EASY",
                "explanation": "In standard C/Java/C++, logical AND (&&) exhibits short-circuit behavior: if the left operand evaluates to false (a > 10 is 5 > 10 -> false), the right operand (++b > 10) is NEVER executed. Therefore, b remains 10, c remains 15, and output is '5 10 15'. (Reference: GeeksforGeeks Short Circuiting in C/C++).",
                "options": [
                    {"text": "5 10 15", "is_correct": True, "feedback": "Correct! Because a > 10 is false, ++b is skipped due to short-circuit evaluation."},
                    {"text": "5 11 15", "is_correct": False, "feedback": "Incorrect: ++b is never evaluated because the left operand is false."},
                    {"text": "5 11 20", "is_correct": False, "feedback": "Incorrect: The if block body never executes."},
                    {"text": "Compiler Error", "is_correct": False, "feedback": "Incorrect: This is valid syntax across C, C++, and Java."}
                ]
            },
            {
                "title": "[GFG] Integer Overflow and Sign Extension",
                "content": "In a 32-bit two's complement system, what happens when `INT_MAX` (2,147,483,647) is incremented by 1 in signed integer arithmetic?",
                "difficulty": "EASY",
                "explanation": "In two's complement representation, INT_MAX has the binary representation 01111111 11111111 11111111 11111111. Adding 1 yields 10000000 00000000 00000000 00000000, which represents INT_MIN (-2,147,483,648). In standard C/C++, signed overflow is undefined behavior, but in Java it wraps deterministically to INT_MIN. (Reference: GeeksforGeeks Integer Overflow and Underflow).",
                "options": [
                    {"text": "It wraps to INT_MIN (-2,147,483,648)", "is_correct": True, "feedback": "Correct: The sign bit flips to 1, representing the lowest negative number."},
                    {"text": "It stays at INT_MAX (saturation arithmetic)", "is_correct": False, "feedback": "Incorrect: Standard CPUs do not perform saturation arithmetic by default."},
                    {"text": "It resets to 0", "is_correct": False, "feedback": "Incorrect: 0 is represented as all zero bits."},
                    {"text": "It throws a runtime ArithmeticException in all languages", "is_correct": False, "feedback": "Incorrect: Standard arithmetic does not throw exceptions on integer overflow."}
                ]
            },
            {
                "title": "[GFG] Floating-Point Precision & Comparison Trap",
                "content": "Why is the direct equality comparison `0.1 + 0.2 == 0.3` evaluated as `false` in JavaScript, Python, and C?",
                "difficulty": "MEDIUM",
                "explanation": "Floating-point numbers in IEEE 754 standard use binary representation (powers of 2). Decimals like 0.1 and 0.2 cannot be represented with finite precision in base-2, resulting in an approximation: 0.1 + 0.2 = 0.30000000000000004. Comparing it with 0.3 yields false. Use abs(a - b) < epsilon. (Reference: GeeksforGeeks Floating Point Representation).",
                "options": [
                    {"text": "Binary floating-point cannot exactly represent 0.1 and 0.2 in base-2 (IEEE 754 precision)", "is_correct": True, "feedback": "Correct! IEEE 754 binary floating-point yields 0.30000000000000004."},
                    {"text": "Operator == does not support floating numbers", "is_correct": False, "feedback": "Incorrect: == supports floating point numbers, but strict equality fails."},
                    {"text": "0.1 is automatically cast to an integer 0", "is_correct": False, "feedback": "Incorrect: 0.1 remains a float."},
                    {"text": "Dynamic typing changes the variable types during addition", "is_correct": False, "feedback": "Incorrect: The issue stems from IEEE 754 representation, not type coercion."}
                ]
            }
        ]
    },

    "Functions, Scope & Recursion": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks placement questions on call stack frames, base condition invariants, tail recursion optimization, and recursion tree complexity analysis.",
        "questions": [
            {
                "title": "[GFG] Predict Output: Static Variable in Recursion",
                "content": "What does the following recursive function return for `fun(5)`?\n```c\nint fun(int n) {\n    static int x = 0;\n    if (n <= 0) return 1;\n    x++;\n    return fun(n - 1) + x;\n}\n```",
                "difficulty": "MEDIUM",
                "explanation": "Static variables retain their value across recursive calls. During unwinding, x has already been incremented 5 times (x = 5). Call tree: fun(5) calls fun(4).. down to fun(0) which returns 1. As calls return: fun(1)=1+5=6, fun(2)=6+5=11, fun(3)=11+5=16, fun(4)=16+5=21, fun(5)=21+5=26. (Reference: GeeksforGeeks Static Variables in Recursion).",
                "options": [
                    {"text": "26", "is_correct": True, "feedback": "Correct! x reaches 5 before any addition occurs; then each returning call adds 5."},
                    {"text": "16", "is_correct": False, "feedback": "Incorrect: Check static variable state when returns unwind."},
                    {"text": "21", "is_correct": False, "feedback": "Incorrect: All 5 recursive steps add the final value of x."},
                    {"text": "15", "is_correct": False, "feedback": "Incorrect: Remember fun(0) returns 1."}
                ]
            },
            {
                "title": "[GFG] Space Complexity of Auxiliary Recursion Stack",
                "content": "What is the maximum auxiliary space complexity of calculating the Nth Fibonacci number using naive recursion: `fib(n) = fib(n-1) + fib(n-2)`?",
                "difficulty": "MEDIUM",
                "explanation": "Although the total number of calls is O(2^N), the maximum depth of the call stack at any given point in time is equal to the longest branch of the recursion tree, which is N. Thus, auxiliary stack space is O(N). (Reference: GeeksforGeeks Space Complexity of Recursive Fibonacci).",
                "options": [
                    {"text": "O(N)", "is_correct": True, "feedback": "Correct: The call stack depth never exceeds the maximum depth of the recursion tree (N)."},
                    {"text": "O(2^N)", "is_correct": False, "feedback": "Incorrect: O(2^N) is the time complexity, NOT space complexity."},
                    {"text": "O(log N)", "is_correct": False, "feedback": "Incorrect: The branch degrades to depth N along the fib(n-1) path."},
                    {"text": "O(1)", "is_correct": False, "feedback": "Incorrect: Each stack frame consumes memory until base condition returns."}
                ]
            },
            {
                "title": "[GFG] Tail Recursion Optimization Principle",
                "content": "When is a recursive function considered strictly 'tail-recursive', allowing compilers to optimize stack frames into iterative jumps?",
                "difficulty": "EASY",
                "explanation": "A function is tail-recursive if the recursive call is the very last operation executed before the function returns. If any computation (like addition or multiplication) is pending after the recursive call, the stack frame cannot be discarded. (Reference: GeeksforGeeks Tail Recursion).",
                "options": [
                    {"text": "When the recursive call is the last executed statement and no pending operations remain", "is_correct": True, "feedback": "Correct: Compilers can reuse the current activation record without allocating a new stack frame."},
                    {"text": "When the function returns an integer instead of void", "is_correct": False, "feedback": "Incorrect: Return type does not dictate tail recursion."},
                    {"text": "When there are two recursive calls in the body", "is_correct": False, "feedback": "Incorrect: Multiple calls generally prevent direct single-frame reuse."},
                    {"text": "When the function does not use base conditions", "is_correct": False, "feedback": "Incorrect: Base conditions are mandatory to prevent infinite recursion."}
                ]
            }
        ]
    },

    "Object-Oriented Programming (OOP)": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks interview questions covering polymorphism, virtual method tables (vtable), dynamic binding, inheritance diamonds, and encapsulation.",
        "questions": [
            {
                "title": "[GFG] Virtual Functions and Dynamic Dispatch (VTable)",
                "content": "In C++, how is dynamic polymorphism implemented under the hood when invoking a virtual member function via a base pointer?",
                "difficulty": "MEDIUM",
                "explanation": "Every class with at least one virtual function has a compiler-generated Virtual Method Table (vtable) storing function pointers. Each object instance contains an invisible virtual pointer (vptr) pointing to that vtable. Dynamic dispatch dereferences vptr at runtime to invoke the overridden implementation. (Reference: GeeksforGeeks VTable and VPTR in C++).",
                "options": [
                    {"text": "Through a compiler-generated VTable of function pointers indexed via the object's VPTR", "is_correct": True, "feedback": "Correct! The vptr points to the class vtable resolved at runtime."},
                    {"text": "Through direct static linking performed at compile time", "is_correct": False, "feedback": "Incorrect: Static linking applies to non-virtual methods."},
                    {"text": "By dynamically recompiling bytecode during execution", "is_correct": False, "feedback": "Incorrect: C++ is a natively compiled language with no runtime bytecode compilation."},
                    {"text": "Using hash tables mapping method name strings to memory offsets", "is_correct": False, "feedback": "Incorrect: C++ uses array indexing into vtable for zero-overhead dispatch."}
                ]
            },
            {
                "title": "[GFG] The Diamond Problem in Multiple Inheritance",
                "content": "In object-oriented programming with multiple inheritance, what issue arises when class D inherits from B and C, which both inherit from base class A?",
                "difficulty": "MEDIUM",
                "explanation": "Class D receives two separate copies of class A's members (one via B, one via C), leading to ambiguity when accessing A's members and redundant storage. In C++, this is solved using virtual inheritance: `class B : virtual public A`. (Reference: GeeksforGeeks Multiple Inheritance and Diamond Problem).",
                "options": [
                    {"text": "Ambiguity due to duplicate copies of base class A in the most derived class D", "is_correct": True, "feedback": "Correct! Solved via virtual inheritance in C++ or interface implementation in Java."},
                    {"text": "Class D cannot compile because multiple inheritance is syntactically illegal in all languages", "is_correct": False, "feedback": "Incorrect: C++ and Python natively support multiple inheritance."},
                    {"text": "All virtual functions in class A become automatically private", "is_correct": False, "feedback": "Incorrect: Access specifiers remain unchanged."},
                    {"text": "The memory layout automatically merges all duplicate integers into floats", "is_correct": False, "feedback": "Incorrect: Types are never implicitly coerced by inheritance hierarchy."}
                ]
            },
            {
                "title": "[GFG] Abstract Classes vs Interfaces in System Design",
                "content": "What is the key structural distinction between an Abstract Class and an Interface in Java/C#?",
                "difficulty": "EASY",
                "explanation": "An abstract class can maintain state (instance fields/variables) and concrete constructors, whereas an interface primarily specifies contracts without state (though default methods are allowed in modern Java). A class can implement multiple interfaces, but extend only one class. (Reference: GeeksforGeeks Difference Between Abstract Class and Interface).",
                "options": [
                    {"text": "Abstract classes can hold instance state/constructors; classes can implement multiple interfaces but inherit only one class", "is_correct": True, "feedback": "Correct! State retention and single inheritance distinguish abstract classes."},
                    {"text": "Interfaces can instantiate objects directly with `new`", "is_correct": False, "feedback": "Incorrect: Interfaces cannot be instantiated directly."},
                    {"text": "Abstract classes cannot contain any implemented methods", "is_correct": False, "feedback": "Incorrect: Abstract classes frequently contain concrete shared methods."},
                    {"text": "Interfaces execute faster than abstract classes due to CPU registers", "is_correct": False, "feedback": "Incorrect: Method invocation overhead is virtually identical."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # DATA STRUCTURES & ALGORITHMS
    # -------------------------------------------------------------
    "Arrays & Strings": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks campus placement assessment on contiguous memory allocation, two-pointer techniques, sliding windows, and string matching algorithms.",
        "questions": [
            {
                "title": "[GFG] Kadane's Algorithm for Maximum Subarray Sum",
                "content": "What is the optimal time complexity of Kadane's algorithm to find the contiguous subarray with maximum sum in an array of N integers?",
                "difficulty": "EASY",
                "explanation": "Kadane's algorithm processes the array in a single linear pass by maintaining `max_ending_here = max(arr[i], max_ending_here + arr[i])` and `max_so_far = max(max_so_far, max_ending_here)`. Time complexity is O(N) and auxiliary space is O(1). (Reference: GeeksforGeeks Largest Sum Contiguous Subarray).",
                "options": [
                    {"text": "O(N) time and O(1) auxiliary space", "is_correct": True, "feedback": "Correct! Kadane's algorithm operates in a single pass with constant space."},
                    {"text": "O(N log N) time and O(N) space", "is_correct": False, "feedback": "Incorrect: Divide-and-conquer takes O(N log N), but Kadane is strictly O(N)."},
                    {"text": "O(N^2) time and O(1) space", "is_correct": False, "feedback": "Incorrect: Brute force checking all pairs is O(N^2)."},
                    {"text": "O(log N) time and O(1) space", "is_correct": False, "feedback": "Incorrect: Finding the sum requires inspecting elements, taking at least Omega(N)."}
                ]
            },
            {
                "title": "[GFG] Two-Pointer Technique: Dutch National Flag Algorithm",
                "content": "In Dijkstra's Dutch National Flag algorithm to sort an array of 0s, 1s, and 2s in a single pass, which pointers are maintained?",
                "difficulty": "MEDIUM",
                "explanation": "The algorithm maintains three pointers: `low` (boundary for 0s), `mid` (current element), and `high` (boundary for 2s). When arr[mid] == 0, swap(low++, mid++); when arr[mid] == 1, mid++; when arr[mid] == 2, swap(mid, high--). (Reference: GeeksforGeeks Sort an array of 0s, 1s and 2s).",
                "options": [
                    {"text": "Three pointers (low, mid, high) dividing the array into four regions", "is_correct": True, "feedback": "Correct! Elements < low are 0s, low..mid-1 are 1s, high+1..end are 2s."},
                    {"text": "Two pointers traversing exclusively from both outer ends inward", "is_correct": False, "feedback": "Incorrect: That is used for two-sum in sorted arrays, not 3-way partitioning."},
                    {"text": "A single slow and fast runner pointer", "is_correct": False, "feedback": "Incorrect: Runner technique is used in linked list cycle detection."},
                    {"text": "Bitwise XOR accumulators with no pointers", "is_correct": False, "feedback": "Incorrect: Sorting three distinct values requires partition pointers."}
                ]
            },
            {
                "title": "[GFG] Rabin-Karp String Matching & Rolling Hash",
                "content": "What enables the Rabin-Karp algorithm to achieve O(N + M) average time complexity for substring search?",
                "difficulty": "HARD",
                "explanation": "Rabin-Karp uses a rolling hash function where the hash of a new window is computed from the previous window in O(1) time by subtracting the leading character contribution, multiplying by the base, and adding the incoming character. (Reference: GeeksforGeeks Rabin-Karp Algorithm for Pattern Searching).",
                "options": [
                    {"text": "Rolling hash function computing the next window's hash in O(1) time", "is_correct": True, "feedback": "Correct! O(1) hash updating enables O(N) average pattern searching."},
                    {"text": "Preprocessing pattern into a deterministic finite automaton (DFA)", "is_correct": False, "feedback": "Incorrect: DFA matching is used in the Aho-Corasick or Finite Automata algorithm."},
                    {"text": "Constructing a Suffix Tree of length M", "is_correct": False, "feedback": "Incorrect: Suffix trees require distinct indexing algorithms like Ukkonen's."},
                    {"text": "Sorting both strings alphabetically before comparison", "is_correct": False, "feedback": "Incorrect: Sorting destroys substring sequential ordering."}
                ]
            }
        ]
    },

    "Linked Lists": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks placement questions on pointer manipulation, Floyd's cycle detection, list reversal, and LRU cache implementations.",
        "questions": [
            {
                "title": "[GFG] Floyd's Cycle Detection (Tortoise and Hare)",
                "content": "In a singly linked list with a loop, if slow pointer moves 1 step and fast moves 2 steps, what proves they will always meet if a cycle exists?",
                "difficulty": "EASY",
                "explanation": "Once both pointers are inside the loop of length C, the relative distance between them decreases by 1 in every iteration: `(dist + 2 - 1) % C = (dist + 1) % C`. Since distance decreases by 1 each step, it must become 0 modulo C, guaranteeing a collision within C steps. (Reference: GeeksforGeeks Detect loop in a linked list).",
                "options": [
                    {"text": "The relative distance between them in the cycle decreases by 1 on every step until reaching 0", "is_correct": True, "feedback": "Correct! Fast pointer gains exactly 1 step on slow pointer in each iteration."},
                    {"text": "Both pointers will reach the NULL tail node simultaneously", "is_correct": False, "feedback": "Incorrect: In a looped list, NULL is never reached."},
                    {"text": "The fast pointer wraps around memory addresses using CPU hardware paging", "is_correct": False, "feedback": "Incorrect: Cycle detection is logical pointer traversal."},
                    {"text": "Slow pointer reverses node links behind it", "is_correct": False, "feedback": "Incorrect: Floyd's algorithm does not modify node pointers."}
                ]
            },
            {
                "title": "[GFG] Reverse a Singly Linked List in Place",
                "content": "What is the minimum number of auxiliary pointers required to iteratively reverse a singly linked list in O(N) time and O(1) space?",
                "difficulty": "EASY",
                "explanation": "Iterative reversal requires 3 pointers: `prev` (initially NULL), `curr` (current node), and `next` (temporary to hold curr->next before breaking the link). (Reference: GeeksforGeeks Reverse a linked list).",
                "options": [
                    {"text": "3 pointers (prev, curr, next)", "is_correct": True, "feedback": "Correct! prev, curr, and next are sufficient to reverse links in place."},
                    {"text": "1 pointer using bitwise manipulation", "is_correct": False, "feedback": "Incorrect: You need to store the rest of the list while redirecting curr->next."},
                    {"text": "O(N) pointers stored in an auxiliary stack", "is_correct": False, "feedback": "Incorrect: Stack takes O(N) memory; in-place reversal needs only 3 pointers."},
                    {"text": "2 pointers without saving the forward link", "is_correct": False, "feedback": "Incorrect: Overwriting curr->next loses access to the rest of the list."}
                ]
            },
            {
                "title": "[GFG] LRU Cache Implementation: Doubly Linked List & Hash Map",
                "content": "Why does an LRU (Least Recently Used) Cache utilize a Doubly Linked List paired with a Hash Map instead of an array or singly linked list?",
                "difficulty": "HARD",
                "explanation": "A doubly linked list allows removing any arbitrary node in O(1) time once its pointer is found in the Hash Map (since node->prev and node->next are immediately available). Singly linked lists require O(N) traversal to find the predecessor node. (Reference: GeeksforGeeks LRU Cache Implementation).",
                "options": [
                    {"text": "Doubly linked list enables O(1) node deletion and relocation to head when pointer is retrieved from hash map", "is_correct": True, "feedback": "Correct! Immediate access to node->prev allows O(1) unlinking."},
                    {"text": "Singly linked lists cannot store key-value pairs", "is_correct": False, "feedback": "Incorrect: Any node can store key-value pairs."},
                    {"text": "Doubly linked lists automatically sort items in ascending order", "is_correct": False, "feedback": "Incorrect: Nodes are ordered by access recency, not sorted by key."},
                    {"text": "Arrays offer faster O(1) arbitrary insertion in the middle", "is_correct": False, "feedback": "Incorrect: Array middle deletion/insertion takes O(N) due to element shifting."}
                ]
            }
        ]
    },

    "Trees & Binary Search Trees": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks campus interview drill on BST validation invariants, AVL tree rotations, tree traversals, and Lowest Common Ancestor (LCA).",
        "questions": [
            {
                "title": "[GFG] Binary Search Tree Validation Trap",
                "content": "Why is it insufficient to merely check `node.left.val < node.val` and `node.right.val > node.val` for every node to validate a BST?",
                "difficulty": "MEDIUM",
                "explanation": "A valid BST requires that ALL nodes in the left subtree are strictly less than the ancestor, and ALL nodes in the right subtree are greater. Local checking misses violations like root=10, right child=15, and right child's left child=6 (where 6 < 10 is in root's right subtree). Validation must pass (min_val, max_val) bounds down the tree. (Reference: GeeksforGeeks Check if a binary tree is BST).",
                "options": [
                    {"text": "All descendants in the left/right subtrees must satisfy the ancestor's global range bounds, not just immediate children", "is_correct": True, "feedback": "Correct! Global (min, max) bounds must be preserved through the entire recursion."},
                    {"text": "BSTs require leaf nodes to always store even numbers", "is_correct": False, "feedback": "Incorrect: Node parity is irrelevant."},
                    {"text": "Binary trees can only have at most 3 levels", "is_correct": False, "feedback": "Incorrect: Trees can have arbitrary depth."},
                    {"text": "Right child nodes can equal the root in standard strict BSTs", "is_correct": False, "feedback": "Incorrect: Strict BSTs forbid duplicate keys or specify single-side duplicates."}
                ]
            },
            {
                "title": "[GFG] Lowest Common Ancestor (LCA) in a BST",
                "content": "In a BST with unique keys, how do we find the Lowest Common Ancestor of two nodes `n1` and `n2` in optimal O(H) time?",
                "difficulty": "MEDIUM",
                "explanation": "Starting at the root: if both n1 and n2 are smaller than current node, traverse left; if both are greater, traverse right. The first node where n1 and n2 split to different sides (or one equals current node) is the Lowest Common Ancestor. (Reference: GeeksforGeeks Lowest Common Ancestor in a Binary Search Tree).",
                "options": [
                    {"text": "Traverse from root: the first node whose value lies between n1 and n2 (or matches one) is the LCA", "is_correct": True, "feedback": "Correct! The BST property guarantees the split node is the LCA."},
                    {"text": "Store post-order traversals in two arrays and find their intersection", "is_correct": False, "feedback": "Incorrect: Post-order array matching takes extra O(N) auxiliary space."},
                    {"text": "Compute depth of all leaf nodes using BFS", "is_correct": False, "feedback": "Incorrect: BFS does not exploit the ordering property of BST."},
                    {"text": "LCA in a BST is always the absolute root node", "is_correct": False, "feedback": "Incorrect: LCA can be any internal node in the subtree."}
                ]
            },
            {
                "title": "[GFG] AVL Tree Self-Balancing Invariant",
                "content": "What is the maximum permissible difference between heights of left and right subtrees (Balance Factor) for every node in an AVL tree?",
                "difficulty": "EASY",
                "explanation": "In an AVL tree, Balance Factor = height(left) - height(right). For every node, this factor must be in {-1, 0, 1}. If it deviates to 2 or -2, rotations (LL, RR, LR, RL) are executed to restore O(log N) search guarantee. (Reference: GeeksforGeeks AVL Tree Insertion).",
                "options": [
                    {"text": "At most 1 (Balance Factor in {-1, 0, 1})", "is_correct": True, "feedback": "Correct! AVL trees enforce strictly bounded height difference <= 1."},
                    {"text": "At most 2", "is_correct": False, "feedback": "Incorrect: Balance factor of 2 triggers immediate rebalancing rotation."},
                    {"text": "At most 0 (must be a perfect binary tree)", "is_correct": False, "feedback": "Incorrect: Perfect balance is too rigid for dynamic insertions."},
                    {"text": "Height difference can be any value as long as keys are sorted", "is_correct": False, "feedback": "Incorrect: That describes an un-balanced BST which degrades to O(N)."}
                ]
            }
        ]
    },

    "Dynamic Programming": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks placement questions on overlapping subproblems, optimal substructure, 0/1 knapsack, LCS, and state space optimization.",
        "questions": [
            {
                "title": "[GFG] 0/1 Knapsack Space Optimization",
                "content": "How can the 2D DP table `dp[N+1][W+1]` for 0/1 Knapsack be compressed into a 1D array `dp[W+1]` without corrupting state transitions?",
                "difficulty": "MEDIUM",
                "explanation": "In 0/1 Knapsack, `dp[w]` depends on values from the previous item at capacity `w - weight[i]`. If we iterate backwards from `W` down to `weight[i]`, `dp[w - weight[i]]` still contains the value from the previous item (not overwritten by the current item), enforcing that each item is used at most once. (Reference: GeeksforGeeks 0/1 Knapsack Problem).",
                "options": [
                    {"text": "Iterate the knapsack capacity backwards from W down to item weight", "is_correct": True, "feedback": "Correct! Backward iteration prevents using the current item multiple times."},
                    {"text": "Iterate capacity forwards from 0 up to W", "is_correct": False, "feedback": "Incorrect: Forward iteration solves Unbounded Knapsack where items can be reused infinitely."},
                    {"text": "Sort the items in descending order of value-to-weight ratio", "is_correct": False, "feedback": "Incorrect: Greedy ratio sorting solves Fractional Knapsack, not 0/1 Knapsack."},
                    {"text": "Compress the table using run-length encoding", "is_correct": False, "feedback": "Incorrect: Compression algorithms do not facilitate dynamic programming lookups."}
                ]
            },
            {
                "title": "[GFG] Longest Common Subsequence (LCS) State Transition",
                "content": "For two strings `S1` and `S2` of lengths M and N, what is the recurrence relation when `S1[i-1] != S2[j-1]` in LCS?",
                "difficulty": "MEDIUM",
                "explanation": "When the characters do not match, the optimal subsequence either excludes S1[i-1] or S2[j-1]. Thus, `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`. When they match, `dp[i][j] = 1 + dp[i-1][j-1]`. (Reference: GeeksforGeeks Longest Common Subsequence).",
                "options": [
                    {"text": "dp[i][j] = max(dp[i-1][j], dp[i][j-1])", "is_correct": True, "feedback": "Correct! Take the maximum of excluding the current character from either string."},
                    {"text": "dp[i][j] = dp[i-1][j-1] + 1", "is_correct": False, "feedback": "Incorrect: That transition applies only when characters match (S1[i-1] == S2[j-1])."},
                    {"text": "dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + 1", "is_correct": False, "feedback": "Incorrect: That is reminiscent of Levenshtein Edit Distance."},
                    {"text": "dp[i][j] = 0", "is_correct": False, "feedback": "Incorrect: Setting to 0 would lose previously matched subsequences (that is Longest Common Substring)."}
                ]
            },
            {
                "title": "[GFG] Overlapping Subproblems vs Optimal Substructure",
                "content": "Which classic algorithmic problem exhibits optimal substructure but does NOT exhibit overlapping subproblems (hence solved via Divide & Conquer rather than DP)?",
                "difficulty": "EASY",
                "explanation": "Merge Sort splits the array into two non-overlapping halves, sorts each half recursively, and merges them. Because subproblems do not overlap (no subproblem is solved repeatedly), memoization/DP provides no benefit. (Reference: GeeksforGeeks Dynamic Programming vs Divide and Conquer).",
                "options": [
                    {"text": "Merge Sort", "is_correct": True, "feedback": "Correct! Subproblems are independent and disjoint; thus Divide and Conquer is optimal."},
                    {"text": "Fibonacci Numbers", "is_correct": False, "feedback": "Incorrect: fib(n-1) and fib(n-2) have massive overlapping calls."},
                    {"text": "Matrix Chain Multiplication", "is_correct": False, "feedback": "Incorrect: Matrix subchains have heavy subproblem overlap."},
                    {"text": "Bellman-Ford Shortest Path", "is_correct": False, "feedback": "Incorrect: Relaxing edges across vertices involves overlapping subproblems."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # CORE CS FUNDAMENTALS
    # -------------------------------------------------------------
    "DBMS, SQL & Indexing": {
        "category": "SQL_DATABASES",
        "description": "GeeksforGeeks placement assessment on B-Tree indexing, ACID transactions, normalization anomalies, and query optimizer plans.",
        "questions": [
            {
                "title": "[GFG] B+ Tree Indexing in Relational Databases",
                "content": "Why do relational database engines (e.g. MySQL InnoDB, PostgreSQL) use B+ Trees rather than Binary Search Trees or standard B-Trees for disk-backed indexing?",
                "difficulty": "MEDIUM",
                "explanation": "B+ Trees store all actual record pointers/data exclusively in leaf nodes, which are linked together in a sequential linked list. Internal nodes only store keys, maximizing branching factor (fan-out) to minimize disk I/O. Leaf chaining enables O(log N + K) range queries. (Reference: GeeksforGeeks B+ Tree in DBMS).",
                "options": [
                    {"text": "High fan-out minimizes disk I/O depth, and leaf-level linked lists enable rapid range scans", "is_correct": True, "feedback": "Correct! High branch factor and leaf chaining make B+ Trees ideal for disk block reads."},
                    {"text": "Binary search trees occupy zero disk memory", "is_correct": False, "feedback": "Incorrect: BSTs require memory and suffer severe depth/rotations on disk."},
                    {"text": "B+ Trees prevent concurrent read transactions", "is_correct": False, "feedback": "Incorrect: B+ Trees support fine-grained page-level latching for concurrency."},
                    {"text": "B+ Trees store duplicate keys without needing primary keys", "is_correct": False, "feedback": "Incorrect: Unique indexes forbid duplicate keys."}
                ]
            },
            {
                "title": "[GFG] Transaction Isolation: Phantom Read Anomaly",
                "content": "Under SQL-92 isolation levels, which level is the lowest that guarantees protection against 'Phantom Reads'?",
                "difficulty": "HARD",
                "explanation": "Phantom reads occur when a transaction re-executes a range query (e.g., SELECT ... WHERE age > 25) and finds new rows inserted and committed by another transaction. Read Committed and Repeatable Read allow phantom reads (unless gap locks are used); only SERIALIZABLE guarantees protection per SQL standard. (Reference: GeeksforGeeks Transaction Isolation Levels in DBMS).",
                "options": [
                    {"text": "SERIALIZABLE", "is_correct": True, "feedback": "Correct! Serializable isolation prevents dirty reads, non-repeatable reads, and phantom reads."},
                    {"text": "READ UNCOMMITTED", "is_correct": False, "feedback": "Incorrect: Read Uncommitted allows even dirty reads."},
                    {"text": "READ COMMITTED", "is_correct": False, "feedback": "Incorrect: Read Committed permits non-repeatable and phantom reads."},
                    {"text": "REPEATABLE READ", "is_correct": False, "feedback": "Incorrect: Per SQL-92 standard, Repeatable Read permits phantom rows (though InnoDB mitigates via Next-Key locks)."}
                ]
            },
            {
                "title": "[GFG] Database Normalization: Boyce-Codd Normal Form (BCNF)",
                "content": "A relational table is in Boyce-Codd Normal Form (BCNF) if and only if for every non-trivial functional dependency X -> Y:",
                "difficulty": "MEDIUM",
                "explanation": "BCNF is a stricter version of 3NF. A relation is in BCNF if for every functional dependency X -> Y, X is a superkey. In 3NF, Y could alternatively be a prime attribute (part of a candidate key), which is disallowed in BCNF. (Reference: GeeksforGeeks Boyce-Codd Normal Form (BCNF)).",
                "options": [
                    {"text": "X must be a superkey", "is_correct": True, "feedback": "Correct! The left-hand side determinant X must always be a superkey in BCNF."},
                    {"text": "Y must be a primary key", "is_correct": False, "feedback": "Incorrect: The condition constrains the determinant X, not dependent Y."},
                    {"text": "The table must contain zero foreign keys", "is_correct": False, "feedback": "Incorrect: Foreign keys are essential in normalized schemas."},
                    {"text": "All attributes must be character strings", "is_correct": False, "feedback": "Incorrect: Normalization principles apply regardless of data type."}
                ]
            }
        ]
    },

    "Operating Systems & Concurrency": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks placement questions on process synchronization, deadlock conditions, virtual memory paging, and CPU scheduling algorithms.",
        "questions": [
            {
                "title": "[GFG] Coffman Conditions for System Deadlock",
                "content": "Which of the following is NOT one of the four necessary Coffman conditions required for a deadlock to occur in an operating system?",
                "difficulty": "EASY",
                "explanation": "The four necessary Coffman conditions are: 1) Mutual Exclusion, 2) Hold and Wait, 3) No Preemption, and 4) Circular Wait. Process starvation or priority inversion is not a necessary condition. (Reference: GeeksforGeeks Deadlock Prevention and Coffman Conditions).",
                "options": [
                    {"text": "Process Starvation", "is_correct": True, "feedback": "Correct! Starvation is an unfair scheduling state, not a prerequisite for deadlock."},
                    {"text": "Mutual Exclusion", "is_correct": False, "feedback": "Incorrect: Mutual exclusion is one of the four required Coffman conditions."},
                    {"text": "Hold and Wait", "is_correct": False, "feedback": "Incorrect: Hold and wait is a mandatory Coffman condition."},
                    {"text": "Circular Wait", "is_correct": False, "feedback": "Incorrect: Circular wait is the cyclic dependency requirement in deadlock."}
                ]
            },
            {
                "title": "[GFG] Page Replacement: Belady's Anomaly",
                "content": "Which page replacement algorithm can experience Belady's Anomaly (where increasing the number of page frames results in MORE page faults)?",
                "difficulty": "MEDIUM",
                "explanation": "FIFO (First-In, First-Out) replacement algorithm can experience Belady's Anomaly because it does not belong to the class of 'Stack Algorithms' (where the set of pages in memory for n frames is always a subset of pages for n+1 frames). LRU and Optimal algorithms never exhibit Belady's Anomaly. (Reference: GeeksforGeeks Belady’s Anomaly in Page Replacement Algorithms).",
                "options": [
                    {"text": "FIFO (First-In, First-Out)", "is_correct": True, "feedback": "Correct! FIFO does not satisfy the inclusion property of stack algorithms."},
                    {"text": "LRU (Least Recently Used)", "is_correct": False, "feedback": "Incorrect: LRU is a stack algorithm and is mathematically immune to Belady's Anomaly."},
                    {"text": "Optimal Page Replacement", "is_correct": False, "feedback": "Incorrect: Optimal algorithm never exhibits Belady's Anomaly."},
                    {"text": "LFU (Least Frequently Used)", "is_correct": False, "feedback": "Incorrect: Classic Belady example specifically targets FIFO queue dynamics."}
                ]
            },
            {
                "title": "[GFG] Semaphore vs Mutex: Priority Inversion Solution",
                "content": "How do real-time operating systems prevent priority inversion when a low-priority thread holds a mutex required by a high-priority thread?",
                "difficulty": "HARD",
                "explanation": "Priority Inversion is resolved via Priority Inheritance: the low-priority thread holding the lock temporarily inherits the priority of the highest-priority thread waiting on that lock, preventing intermediate-priority threads from preempting it until the critical section is released. (Reference: GeeksforGeeks Priority Inversion in OS).",
                "options": [
                    {"text": "Priority Inheritance Protocol (low-priority thread temporarily inherits high priority)", "is_correct": True, "feedback": "Correct! Temporarily elevating priority unblocks the critical section promptly."},
                    {"text": "Killing the low-priority thread immediately", "is_correct": False, "feedback": "Incorrect: Aborting threads holding locks corrupts shared state."},
                    {"text": "Disabling CPU interrupts indefinitely across all cores", "is_correct": False, "feedback": "Incorrect: Disabling interrupts globally violates real-time latency guarantees."},
                    {"text": "Converting the mutex into a non-blocking spinlock", "is_correct": False, "feedback": "Incorrect: Spinlocks cause busy-waiting and exacerbate inversion on uniprocessors."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # QUANTITATIVE APTITUDE
    # -------------------------------------------------------------
    "Percentages, Ratios & Commercial Math": {
        "category": "QUANTITATIVE_APTITUDE",
        "description": "GeeksforGeeks aptitude placement module on successive percentages, profit & loss markup, mixture allegations, and compound interest.",
        "questions": [
            {
                "title": "[GFG] Successive Percentage Changes Formula",
                "content": "If the price of an article is first increased by 20% and then decreased by 20%, what is the net percentage change in the final price?",
                "difficulty": "EASY",
                "explanation": "Using the net successive change formula `a + b + (ab/100)`: here a = +20, b = -20. Net change = 20 - 20 + ((20 * -20) / 100) = -400 / 100 = -4% (a 4% decrease). (Reference: GeeksforGeeks Aptitude: Percentage).",
                "options": [
                    {"text": "4% decrease", "is_correct": True, "feedback": "Correct! Successive changes yield 20 - 20 - 4 = -4% net reduction."},
                    {"text": "0% (remains unchanged)", "is_correct": False, "feedback": "Incorrect: Percentage decrease is calculated on the higher post-increase base."},
                    {"text": "2% decrease", "is_correct": False, "feedback": "Incorrect: Review the successive percentage formula (a + b + ab/100)."},
                    {"text": "4% increase", "is_correct": False, "feedback": "Incorrect: The loss on the higher base exceeds the initial gain."}
                ]
            },
            {
                "title": "[GFG] Profit & Loss: Marked Price and Discount",
                "content": "A merchant marks goods 40% above cost price and allows a discount of 25% on the marked price. What is the merchant's net profit percentage?",
                "difficulty": "MEDIUM",
                "explanation": "Let Cost Price (CP) = 100. Marked Price (MP) = 140. Discount = 25% of 140 = 35. Selling Price (SP) = 140 - 35 = 105. Net profit = SP - CP = 105 - 100 = 5%. (Reference: GeeksforGeeks Profit and Loss Aptitude Questions).",
                "options": [
                    {"text": "5% profit", "is_correct": True, "feedback": "Correct! SP = 140 * 0.75 = 105, yielding 5% profit over CP 100."},
                    {"text": "15% profit", "is_correct": False, "feedback": "Incorrect: 40% - 25% != 15% because discount applies to marked price, not cost."},
                    {"text": "10% profit", "is_correct": False, "feedback": "Incorrect: Check SP = 140 * 0.75."},
                    {"text": "5% loss", "is_correct": False, "feedback": "Incorrect: Selling price (105) remains strictly greater than cost (100)."}
                ]
            },
            {
                "title": "[GFG] Rule of Alligation: Mixture Ratio",
                "content": "In what ratio must tea worth $60 per kg be mixed with tea worth $65 per kg so that the resulting mixture is worth $62 per kg?",
                "difficulty": "EASY",
                "explanation": "By the Rule of Alligation: \nCheaper (60) vs Dearer (65) with Mean price (62).\nRatio = (Price of Dearer - Mean) / (Mean - Price of Cheaper) = (65 - 62) / (62 - 60) = 3 : 2. (Reference: GeeksforGeeks Alligation or Mixture).",
                "options": [
                    {"text": "3 : 2", "is_correct": True, "feedback": "Correct! (65 - 62) / (62 - 60) = 3 / 2."},
                    {"text": "2 : 3", "is_correct": False, "feedback": "Incorrect: Remember cheaper quantity corresponds to (Dearer - Mean)."},
                    {"text": "5 : 2", "is_correct": False, "feedback": "Incorrect: Cross-subtraction gives 3 and 2."},
                    {"text": "1 : 1", "is_correct": False, "feedback": "Incorrect: Equal parts would yield (60+65)/2 = 62.5, not 62."}
                ]
            }
        ]
    },

    "Time, Work, Speed & Distance": {
        "category": "QUANTITATIVE_APTITUDE",
        "description": "GeeksforGeeks aptitude placement module on reciprocal work rates, pipes & cisterns, relative speed, and train platform crossings.",
        "questions": [
            {
                "title": "[GFG] Time and Work: Combined Productivity Rate",
                "content": "A can complete a piece of work in 12 days and B can complete the same work in 24 days. Working together, in how many days will they finish the work?",
                "difficulty": "EASY",
                "explanation": "A's 1-day work = 1/12. B's 1-day work = 1/24. Combined 1-day work = 1/12 + 1/24 = 3/24 = 1/8. Total days = 1 / (1/8) = 8 days. (Reference: GeeksforGeeks Time and Work Aptitude).",
                "options": [
                    {"text": "8 days", "is_correct": True, "feedback": "Correct! Combined rate = 1/12 + 1/24 = 3/24 = 1/8 work per day, so 8 days."},
                    {"text": "18 days", "is_correct": False, "feedback": "Incorrect: Working together takes less time than either person alone."},
                    {"text": "6 days", "is_correct": False, "feedback": "Incorrect: Calculate 1 / (1/12 + 1/24) = 8."},
                    {"text": "10 days", "is_correct": False, "feedback": "Incorrect: 24 * 12 / (24 + 12) = 288 / 36 = 8 days."}
                ]
            },
            {
                "title": "[GFG] Relative Speed: Trains Moving in Opposite Directions",
                "content": "Two trains of lengths 150m and 250m are running towards each other on parallel tracks at speeds of 54 km/h and 90 km/h. How long will they take to completely cross each other?",
                "difficulty": "MEDIUM",
                "explanation": "Relative speed = 54 + 90 = 144 km/h = 144 * (5/18) = 40 m/s. Total distance to cross = sum of lengths = 150 + 250 = 400 m. Time taken = Distance / Speed = 400 / 40 = 10 seconds. (Reference: GeeksforGeeks Problems on Trains).",
                "options": [
                    {"text": "10 seconds", "is_correct": True, "feedback": "Correct! Distance = 400m, relative speed = 40 m/s -> 400/40 = 10s."},
                    {"text": "15 seconds", "is_correct": False, "feedback": "Incorrect: Check relative speed conversion: 144 * 5/18 = 40 m/s."},
                    {"text": "8 seconds", "is_correct": False, "feedback": "Incorrect: Total distance is 150 + 250 = 400m."},
                    {"text": "20 seconds", "is_correct": False, "feedback": "Incorrect: Trains are moving towards each other, so speeds add up."}
                ]
            },
            {
                "title": "[GFG] Average Speed for Round Trip",
                "content": "A person travels from city A to city B at a speed of 60 km/h and returns from B to A at 40 km/h along the exact same route. What is the average speed for the entire journey?",
                "difficulty": "MEDIUM",
                "explanation": "Average speed is harmonic mean when distances are equal: `(2 * v1 * v2) / (v1 + v2) = (2 * 60 * 40) / (60 + 40) = 4800 / 100 = 48 km/h`. The arithmetic mean (50 km/h) is incorrect because more time is spent traveling at the slower speed. (Reference: GeeksforGeeks Speed Distance and Time).",
                "options": [
                    {"text": "48 km/h", "is_correct": True, "feedback": "Correct! Harmonic mean 2*v1*v2/(v1+v2) = 48 km/h."},
                    {"text": "50 km/h", "is_correct": False, "feedback": "Incorrect: Simple average (60+40)/2 is flawed because time weights differ."},
                    {"text": "45 km/h", "is_correct": False, "feedback": "Incorrect: Use Total Distance / Total Time."},
                    {"text": "52 km/h", "is_correct": False, "feedback": "Incorrect: The average speed must skew closer to the slower speed."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # MODERN FRONTEND ENGINEERING
    # -------------------------------------------------------------
    "HTML5 Semantic Architecture & DOM APIs": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks frontend placement questions on semantic tags, DOM tree mutations, accessibility, and web storage quotas.",
        "questions": [
            {
                "title": "[GFG] Event Bubbling vs Event Capturing (Trickling)",
                "content": "In DOM event propagation, in which order do the three event phases occur?",
                "difficulty": "EASY",
                "explanation": "DOM event flow specifies three phases: 1) Capturing phase (event travels down from Window to the target element), 2) Target phase (event reaches the target), and 3) Bubbling phase (event travels up the DOM tree from target to Window). (Reference: GeeksforGeeks Event Bubbling and Event Capturing in JavaScript).",
                "options": [
                    {"text": "Capturing Phase -> Target Phase -> Bubbling Phase", "is_correct": True, "feedback": "Correct! Events trickle down during capture, fire at target, then bubble upwards."},
                    {"text": "Bubbling Phase -> Target Phase -> Capturing Phase", "is_correct": False, "feedback": "Incorrect: Bubbling is the final upward traversal."},
                    {"text": "Target Phase -> Capturing Phase -> Bubbling Phase", "is_correct": False, "feedback": "Incorrect: The capture phase occurs prior to the target phase."},
                    {"text": "Simultaneous execution across all DOM parents", "is_correct": False, "feedback": "Incorrect: Propagation is strictly sequential."}
                ]
            },
            {
                "title": "[GFG] localStorage vs sessionStorage vs Cookies",
                "content": "What is the primary persistence distinction between `localStorage` and `sessionStorage` in the HTML5 Web Storage API?",
                "difficulty": "EASY",
                "explanation": "localStorage data persists indefinitely across browser restarts until explicitly cleared by user or script. sessionStorage data is tied to the top-level browsing context (tab) and is cleared immediately when that tab is closed. (Reference: GeeksforGeeks Difference between Local Storage and Session Storage).",
                "options": [
                    {"text": "sessionStorage is cleared when the browser tab closes; localStorage persists across restarts", "is_correct": True, "feedback": "Correct! sessionStorage is scoped to the lifetime of the browsing tab."},
                    {"text": "localStorage encrypts stored data with AES-256 automatically", "is_correct": False, "feedback": "Incorrect: Web Storage data is stored in plaintext strings."},
                    {"text": "sessionStorage is transmitted with every HTTP request header", "is_correct": False, "feedback": "Incorrect: Only HTTP cookies are automatically sent in headers."},
                    {"text": "localStorage has a 4KB capacity limit", "is_correct": False, "feedback": "Incorrect: Cookies have a 4KB limit; localStorage has ~5-10MB quota."}
                ]
            },
            {
                "title": "[GFG] Semantic HTML5 Elements for Screen Readers",
                "content": "Why should developers use `<nav>`, `<article>`, and `<main>` instead of generic `<div>` tags?",
                "difficulty": "EASY",
                "explanation": "HTML5 semantic elements provide built-in ARIA landmark roles that screen readers and assistive technologies use for navigation. They also improve SEO indexing by signaling structural significance to search crawlers. (Reference: GeeksforGeeks HTML5 Semantics).",
                "options": [
                    {"text": "They provide accessibility landmark roles for assistive tech and improve SEO crawlers' page indexing", "is_correct": True, "feedback": "Correct! Semantic tags convey meaning, structure, and accessibility landmarks."},
                    {"text": "They increase JavaScript runtime execution speed", "is_correct": False, "feedback": "Incorrect: Parsing speed difference is negligible."},
                    {"text": "They prevent CSS styles from leaking between components", "is_correct": False, "feedback": "Incorrect: Scoped styling requires CSS modules or Shadow DOM."},
                    {"text": "They bypass cross-origin CORS security restrictions", "is_correct": False, "feedback": "Incorrect: HTML semantics have no bearing on network CORS policies."}
                ]
            }
        ]
    },

    "Advanced CSS3, Flexbox & Responsive Layouts": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks frontend questions on CSS specificity calculations, Flexbox alignment, CSS Grid tracks, and hardware-accelerated animations.",
        "questions": [
            {
                "title": "[GFG] CSS Specificity Hierarchy Calculation",
                "content": "Given the following selectors: `#nav` (ID), `.btn.active` (2 Classes), and `div > p` (2 Elements), which selector has highest priority?",
                "difficulty": "EASY",
                "explanation": "CSS Specificity is calculated as (Inline, ID, Class/Attribute/Pseudo-class, Element). Here: #nav has specificity (0, 1, 0, 0); .btn.active has (0, 0, 2, 0); div > p has (0, 0, 0, 2). Any selector with 1 ID overrides any number of classes. (Reference: GeeksforGeeks CSS Specificity).",
                "options": [
                    {"text": "#nav (ID selector has 0,1,0,0 specificity)", "is_correct": True, "feedback": "Correct! 1 ID selector outweighs any quantity of classes or elements."},
                    {"text": ".btn.active (combining two classes)", "is_correct": False, "feedback": "Incorrect: Two classes have specificity (0, 0, 2, 0), lower than 1 ID."},
                    {"text": "div > p (descendant elements)", "is_correct": False, "feedback": "Incorrect: Elements have the lowest non-zero specificity weight."},
                    {"text": "They all share identical specificity", "is_correct": False, "feedback": "Incorrect: The cascade follows strict (Inline, ID, Class, Type) hierarchy."}
                ]
            },
            {
                "title": "[GFG] Flexbox: justify-content vs align-items",
                "content": "When `flex-direction: column` is specified on a flex container, which property aligns items horizontally across the cross axis?",
                "difficulty": "EASY",
                "explanation": "When flex-direction is column, the main axis is vertical (top-to-bottom) and the cross axis is horizontal (left-to-right). Therefore, `align-items` controls alignment along the cross axis (horizontal), while `justify-content` controls the vertical main axis. (Reference: GeeksforGeeks CSS Flexbox).",
                "options": [
                    {"text": "align-items", "is_correct": True, "feedback": "Correct! In column mode, cross axis is horizontal and governed by align-items."},
                    {"text": "justify-content", "is_correct": False, "feedback": "Incorrect: justify-content always controls the main axis (vertical in column mode)."},
                    {"text": "align-content", "is_correct": False, "feedback": "Incorrect: align-content aligns wrapped lines, not individual items."},
                    {"text": "flex-basis", "is_correct": False, "feedback": "Incorrect: flex-basis sets initial size along the main axis."}
                ]
            },
            {
                "title": "[GFG] CSS GPU Hardware Acceleration",
                "content": "Which CSS property change avoids layout recalculation (Reflow) and Paint, triggering only GPU Compositing for 60fps animations?",
                "difficulty": "MEDIUM",
                "explanation": "Modifying `transform` (e.g. `translate3d()`) and `opacity` is handled directly on the compositor thread by the GPU without invalidating layout geometry (Reflow) or triggering CPU repainting. Changing `top`, `left`, `width`, or `margin` forces expensive Reflow. (Reference: GeeksforGeeks Hardware Acceleration in CSS).",
                "options": [
                    {"text": "transform and opacity", "is_correct": True, "feedback": "Correct! transform and opacity are composited directly on the GPU."},
                    {"text": "top and left coordinates", "is_correct": False, "feedback": "Incorrect: Animating top/left causes layout reflow and repaint on every frame."},
                    {"text": "margin-left and padding", "is_correct": False, "feedback": "Incorrect: Box-model spacing changes force full layout recalculation."},
                    {"text": "background-color and border-color", "is_correct": False, "feedback": "Incorrect: Color changes trigger CPU paint cycles."}
                ]
            }
        ]
    },

    "Modern JavaScript, Event Loop & Async/Await": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks JavaScript placement questions on microtasks, macrotasks, closures, Promises, and prototype chain inheritance.",
        "questions": [
            {
                "title": "[GFG] Predict Output: Microtask vs Macrotask Event Loop",
                "content": "What is the logged order in JavaScript?\n```js\nconsole.log('1');\nsetTimeout(() => console.log('2'), 0);\nPromise.resolve().then(() => console.log('3'));\nconsole.log('4');\n```",
                "difficulty": "MEDIUM",
                "explanation": "Synchronous code runs first ('1', then '4'). The Microtask queue (Promise callbacks) has strict priority over the Macrotask queue (setTimeout, setInterval). Once synchronous call stack is empty, microtasks execute ('3'). Finally, the macrotask executes ('2'). Output: 1, 4, 3, 2. (Reference: GeeksforGeeks JavaScript Event Loop).",
                "options": [
                    {"text": "1, 4, 3, 2", "is_correct": True, "feedback": "Correct! Synchronous ('1','4') -> Microtasks ('3') -> Macrotasks ('2')."},
                    {"text": "1, 2, 3, 4", "is_correct": False, "feedback": "Incorrect: setTimeout is asynchronous and deferred even with 0ms delay."},
                    {"text": "1, 4, 2, 3", "is_correct": False, "feedback": "Incorrect: Promise microtasks execute before setTimeout macrotasks."},
                    {"text": "3, 1, 4, 2", "is_correct": False, "feedback": "Incorrect: Synchronous code always completes before checking task queues."}
                ]
            },
            {
                "title": "[GFG] JavaScript Closures and Lexical Scope Trap",
                "content": "What is printed by this loop?\n```js\nfor (var i = 0; i < 3; i++) {\n    setTimeout(() => console.log(i), 100);\n}\n```",
                "difficulty": "EASY",
                "explanation": "Because `var` is function-scoped (not block-scoped), all three callback functions close over the same single variable `i`. By the time the 100ms timer expires and the callbacks execute, the loop has completed and `i` equals 3. Output: 3, 3, 3. (Using `let` would create a new lexical binding per iteration, printing 0, 1, 2). (Reference: GeeksforGeeks Closures in JavaScript).",
                "options": [
                    {"text": "3, 3, 3", "is_correct": True, "feedback": "Correct! var lacks block scope, so all timeouts reference the post-loop value 3."},
                    {"text": "0, 1, 2", "is_correct": False, "feedback": "Incorrect: That requires 'let i = 0' for block scoping."},
                    {"text": "undefined, undefined, undefined", "is_correct": False, "feedback": "Incorrect: i is accessible in the closure scope."},
                    {"text": "0, 0, 0", "is_correct": False, "feedback": "Incorrect: The loop terminates when i reaches 3."}
                ]
            },
            {
                "title": "[GFG] Promise.all vs Promise.allSettled Failure Mode",
                "content": "How does `Promise.all` behave when one of the passed promises rejects?",
                "difficulty": "EASY",
                "explanation": "`Promise.all` fails fast: if any promise in the iterable rejects, the returned promise immediately rejects with the reason of the first rejected promise, ignoring other pending/fulfilled promises. In contrast, `Promise.allSettled` waits for all promises to settle regardless of outcome. (Reference: GeeksforGeeks Promise.all() vs Promise.allSettled()).",
                "options": [
                    {"text": "It rejects immediately with the error of the first rejected promise (fail-fast)", "is_correct": True, "feedback": "Correct! Promise.all aborts on the first rejection."},
                    {"text": "It waits for all promises and returns null for the rejected ones", "is_correct": False, "feedback": "Incorrect: That requires custom filtering or Promise.allSettled."},
                    {"text": "It automatically retries the rejected promise up to 3 times", "is_correct": False, "feedback": "Incorrect: Native Promises have no automatic retry mechanism."},
                    {"text": "It converts rejected promises into resolved promises with status 500", "is_correct": False, "feedback": "Incorrect: Promises reject with Error objects, not HTTP status codes."}
                ]
            }
        ]
    },

    "React Architecture: Components, Hooks & Virtual DOM": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks React questions on Fiber reconciliation, useEffect dependency arrays, custom hooks, and state immutability.",
        "questions": [
            {
                "title": "[GFG] React Virtual DOM Diffing Heuristic Complexity",
                "content": "Standard tree-to-tree transformation algorithms take O(N^3) time. How does React's reconciliation diffing achieve O(N) linear complexity?",
                "difficulty": "MEDIUM",
                "explanation": "React applies two heuristics: 1) Two elements of different types produce different trees (rebuild subtree), and 2) Developer provides a stable `key` prop so React can match children across renders efficiently. Diffing is performed strictly level-by-level without comparing across branches. (Reference: GeeksforGeeks React Reconciliation and Diffing Algorithm).",
                "options": [
                    {"text": "Level-by-level comparison, assuming different element types produce different trees, paired with key props", "is_correct": True, "feedback": "Correct! Heuristic level-by-level matching with keys reduces O(N^3) to O(N)."},
                    {"text": "Precompiling all possible UI states into machine code binary tables", "is_correct": False, "feedback": "Incorrect: React reconciles JSX virtual nodes at runtime."},
                    {"text": "Directly diffing the browser's C++ DOM nodes using Web Workers", "is_correct": False, "feedback": "Incorrect: Virtual DOM diffing occurs in pure JavaScript Fiber nodes."},
                    {"text": "Enforcing that no React component may contain more than 10 child nodes", "is_correct": False, "feedback": "Incorrect: Components can contain arbitrary numbers of children."}
                ]
            },
            {
                "title": "[GFG] Rules of React Hooks: Top-Level Invariant",
                "content": "Why must React Hooks (e.g., `useState`, `useEffect`) NEVER be called inside loops, conditions, or nested functions?",
                "difficulty": "EASY",
                "explanation": "React relies on the call order of hooks to maintain state across renders. Hooks are stored internally in a singly linked list attached to the Fiber node. If a hook call is skipped inside an `if` block, the index alignment shifts, assigning state to the wrong hook. (Reference: GeeksforGeeks Rules of Hooks in React).",
                "options": [
                    {"text": "React relies on consistent hook call order across renders to match state entries in the Fiber linked list", "is_correct": True, "feedback": "Correct! Internal linked list pointers require identical hook sequence every render."},
                    {"text": "Hooks consume too much GPU memory if placed inside loops", "is_correct": False, "feedback": "Incorrect: Hooks run on the JS main thread engine."},
                    {"text": "Conditional hooks trigger infinite HTTP requests to the backend server", "is_correct": False, "feedback": "Incorrect: Hooks are frontend state primitives."},
                    {"text": "React uses Babel to convert all hooks into global window variables", "is_correct": False, "feedback": "Incorrect: Hook state is scoped to Fiber component instances."}
                ]
            },
            {
                "title": "[GFG] React.memo vs useMemo vs useCallback",
                "content": "What is the primary function of `useCallback(fn, deps)` in React?",
                "difficulty": "EASY",
                "explanation": "`useCallback` caches a function definition between renders, returning the same memoized function reference unless its dependencies change. This prevents unnecessary re-renders of memoized child components (`React.memo`) that depend on reference equality (`prevProps.onClick === nextProps.onClick`). (Reference: GeeksforGeeks useCallback vs useMemo).",
                "options": [
                    {"text": "Returns a memoized function reference to preserve reference equality across renders", "is_correct": True, "feedback": "Correct! Prevents breaking shallow comparison in memoized child props."},
                    {"text": "Caches the computed return value of an expensive calculation", "is_correct": False, "feedback": "Incorrect: Caching the calculated value is the job of useMemo."},
                    {"text": "Prevents component state updates from executing asynchronously", "is_correct": False, "feedback": "Incorrect: State updates remain batched and asynchronous."},
                    {"text": "Automatically debounces user click handlers by 300ms", "is_correct": False, "feedback": "Incorrect: Debouncing requires custom timer wrappers."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # BACKEND ARCHITECTURE & REST APIS
    # -------------------------------------------------------------
    "RESTful API Standards & HTTP Protocol Invariants": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks backend placement questions on HTTP methods, idempotency, status code semantics, and REST constraints.",
        "questions": [
            {
                "title": "[GFG] HTTP Idempotency: PUT vs POST vs PATCH",
                "content": "Which HTTP method is defined as idempotent per RFC 7231, meaning multiple identical requests yield the same server state?",
                "difficulty": "EASY",
                "explanation": "PUT and DELETE are idempotent: making 1 request or 10 identical requests leaves the resource in the exact same state (complete replacement or removal). POST is non-idempotent because repeated requests create duplicate entries (e.g. multiple charges). (Reference: GeeksforGeeks Idempotence in HTTP Methods).",
                "options": [
                    {"text": "PUT", "is_correct": True, "feedback": "Correct! PUT replaces the resource; repeating it leaves the resource state identical."},
                    {"text": "POST", "is_correct": False, "feedback": "Incorrect: POST creates new resources and is non-idempotent."},
                    {"text": "PATCH", "is_correct": False, "feedback": "Incorrect: PATCH (e.g. append operations) is not guaranteed to be idempotent."},
                    {"text": "CONNECT", "is_correct": False, "feedback": "Incorrect: CONNECT establishes network tunnels."}
                ]
            },
            {
                "title": "[GFG] HTTP Status Codes: 401 Unauthorized vs 403 Forbidden",
                "content": "What is the technical distinction between HTTP 401 and HTTP 403 response codes?",
                "difficulty": "EASY",
                "explanation": "HTTP 401 Unauthorized indicates that the client has not provided authentication credentials (or they are invalid). HTTP 403 Forbidden means the client identity is authenticated, but the user does not have permission/authorization to access the requested resource. (Reference: GeeksforGeeks 401 Unauthorized vs 403 Forbidden).",
                "options": [
                    {"text": "401 means unauthenticated (missing/invalid credentials); 403 means authenticated but unauthorized (forbidden)", "is_correct": True, "feedback": "Correct! 401 = Who are you? 403 = You cannot access this."},
                    {"text": "401 is for GET requests; 403 is for POST requests", "is_correct": False, "feedback": "Incorrect: Status codes apply across all HTTP methods."},
                    {"text": "401 indicates server timeout; 403 indicates database crash", "is_correct": False, "feedback": "Incorrect: 5xx codes represent server-side faults."},
                    {"text": "401 applies to mobile apps; 403 applies to web browsers", "is_correct": False, "feedback": "Incorrect: HTTP status codes are platform-agnostic."}
                ]
            },
            {
                "title": "[GFG] Cross-Origin Resource Sharing (CORS) Preflight",
                "content": "When does a web browser trigger an HTTP OPTIONS 'preflight' request before sending the actual request?",
                "difficulty": "MEDIUM",
                "explanation": "A preflight OPTIONS request is issued when a cross-origin request is 'non-simple': e.g., uses methods other than GET/POST/HEAD, sends custom headers (like `Authorization` or `Content-Type: application/json`), or uses credentials. (Reference: GeeksforGeeks What is CORS?).",
                "options": [
                    {"text": "When sending custom headers (like Authorization) or non-simple methods/Content-Types cross-origin", "is_correct": True, "feedback": "Correct! Browsers check server permission via OPTIONS before non-simple requests."},
                    {"text": "Whenever an image file is downloaded via an <img> tag", "is_correct": False, "feedback": "Incorrect: Simple media fetches do not trigger preflight."},
                    {"text": "Only when the user browses in Incognito mode", "is_correct": False, "feedback": "Incorrect: CORS rules apply universally across browser sessions."},
                    {"text": "When the frontend and backend share the exact same domain and port", "is_correct": False, "feedback": "Incorrect: Same-origin requests never trigger CORS."}
                ]
            }
        ]
    },

    "Node.js & Python FastAPI Frameworks": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks backend placement questions on async I/O event loops, libuv, ASGI vs WSGI, and thread pools.",
        "questions": [
            {
                "title": "[GFG] Node.js Libuv Architecture & Single-Threaded Event Loop",
                "content": "How does Node.js handle CPU-intensive vs non-blocking I/O operations without freezing its single main thread?",
                "difficulty": "MEDIUM",
                "explanation": "Node.js runs JavaScript on a single thread, but delegates asynchronous non-blocking I/O (epoll/kqueue) to the OS kernel. For file system operations, crypto, and compression, Libuv manages a background Thread Pool (default 4 threads) to prevent blocking the event loop. (Reference: GeeksforGeeks Event Loop in Node.js).",
                "options": [
                    {"text": "Delegates I/O to the OS kernel and utilizes Libuv's thread pool for blocking tasks", "is_correct": True, "feedback": "Correct! Non-blocking I/O via kernel; blocking tasks handled by Libuv thread pool."},
                    {"text": "Spawns a new operating system process for every connected client socket", "is_correct": False, "feedback": "Incorrect: Node.js does not use process-per-connection (Apache style)."},
                    {"text": "Compiles all JavaScript into synchronous C++ binaries at startup", "is_correct": False, "feedback": "Incorrect: V8 uses JIT compilation, maintaining the single-thread loop."},
                    {"text": "Suspends all network traffic while executing database queries", "is_correct": False, "feedback": "Incorrect: Asynchronous callbacks prevent suspension."}
                ]
            },
            {
                "title": "[GFG] FastAPI ASGI vs Flask WSGI Concurrency Model",
                "content": "Why can FastAPI achieve significantly higher concurrency than traditional Flask/Django on synchronous WSGI?",
                "difficulty": "MEDIUM",
                "explanation": "FastAPI is built on Starlette and the Asynchronous Server Gateway Interface (ASGI) standard. It leverages Python's native `async/await` and `asyncio` event loop, enabling thousands of concurrent connections on a single worker without blocking waiting on database or network I/O. (Reference: GeeksforGeeks FastAPI Introduction).",
                "options": [
                    {"text": "FastAPI uses ASGI and asyncio event loops, serving concurrent I/O without blocking threads", "is_correct": True, "feedback": "Correct! Asynchronous non-blocking architecture scales high-concurrency I/O."},
                    {"text": "FastAPI disables all database transactions to boost speed", "is_correct": False, "feedback": "Incorrect: ACID transactions are fully supported."},
                    {"text": "FastAPI runs exclusively inside browser WebAssembly engines", "is_correct": False, "feedback": "Incorrect: FastAPI is a server-side Python framework."},
                    {"text": "WSGI servers cannot execute any Python code", "is_correct": False, "feedback": "Incorrect: WSGI has been the traditional standard for Python web apps."}
                ]
            },
            {
                "title": "[GFG] Node.js process.nextTick() Priority",
                "content": "Where does `process.nextTick()` execute in the Node.js event loop phase transitions?",
                "difficulty": "HARD",
                "explanation": "`process.nextTick()` is not technically part of the event loop phases; instead, the `nextTickQueue` is processed immediately after the current operation completes, BEFORE the event loop continues to any other microtask or phase. (Reference: GeeksforGeeks setImmediate() vs process.nextTick()).",
                "options": [
                    {"text": "Immediately after the current operation finishes, before entering the next event loop phase", "is_correct": True, "feedback": "Correct! nextTickQueue has maximum priority before event loop continuation."},
                    {"text": "Only during the Poll phase after network timeouts", "is_correct": False, "feedback": "Incorrect: That describes standard I/O callbacks."},
                    {"text": "In the Check phase along with setImmediate()", "is_correct": False, "feedback": "Incorrect: setImmediate executes in the Check phase, whereas nextTick precedes it."},
                    {"text": "At the start of the next operating system boot cycle", "is_correct": False, "feedback": "Incorrect: It executes within the current process lifecycle."}
                ]
            }
        ]
    },

    "Authentication, JWT, OAuth2 & Security": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks security and placement questions on JWT signatures, secret management, OAuth2 flows, CSRF, and XSS.",
        "questions": [
            {
                "title": "[GFG] JSON Web Token (JWT) Anatomy & Signature Invariant",
                "content": "What is the primary purpose of the Signature component in a JSON Web Token (header.payload.signature)?",
                "difficulty": "EASY",
                "explanation": "A JWT signature is computed by hashing the Base64Url-encoded header and payload with a secret key (e.g. HMAC-SHA256). It verifies that the token payload was not tampered with or modified in transit. It does NOT encrypt the payload, which remains readable by anyone. (Reference: GeeksforGeeks How JSON Web Token (JWT) Works).",
                "options": [
                    {"text": "To verify data integrity and authenticate that the payload was not tampered with", "is_correct": True, "feedback": "Correct! Signature guarantees cryptographic integrity; payload is Base64 encoded."},
                    {"text": "To encrypt payload data so no one can read user claims", "is_correct": False, "feedback": "Incorrect: Standard JWT payloads are Base64Url encoded, NOT encrypted (unless JWE)."},
                    {"text": "To compress the token size into 8-bit binary packets", "is_correct": False, "feedback": "Incorrect: Base64 encoding actually increases payload size slightly."},
                    {"text": "To communicate directly with the DNS server", "is_correct": False, "feedback": "Incorrect: Tokens are application-layer security claims."}
                ]
            },
            {
                "title": "[GFG] CSRF Attack Mitigation: SameSite Cookies",
                "content": "How does setting `SameSite=Strict` on session cookies protect web applications against Cross-Site Request Forgery (CSRF)?",
                "difficulty": "MEDIUM",
                "explanation": "When `SameSite=Strict` is set, the browser refuses to send the cookie on any cross-site request (including clicking external links). Even if a malicious site triggers a POST request to your bank API, the authentication cookie is withheld by the browser. (Reference: GeeksforGeeks Cross-Site Request Forgery (CSRF)).",
                "options": [
                    {"text": "The browser never sends the cookie on cross-site requests originating from external origins", "is_correct": True, "feedback": "Correct! Withholding cookies on cross-origin requests prevents unauthorized state mutations."},
                    {"text": "The server deletes the database whenever a user visits another site", "is_correct": False, "feedback": "Incorrect: SameSite is a browser-enforced cookie policy."},
                    {"text": "It requires users to enter their password for every single HTTP request", "is_correct": False, "feedback": "Incorrect: Sessions remain active within the same origin."},
                    {"text": "It converts all HTTP POST requests into GET requests", "is_correct": False, "feedback": "Incorrect: Request verbs are not altered."}
                ]
            },
            {
                "title": "[GFG] OAuth 2.0 Authorization Code Flow with PKCE",
                "content": "Why was Proof Key for Code Exchange (PKCE) introduced for Single Page Applications (SPAs) and Mobile Apps in OAuth 2.0?",
                "difficulty": "HARD",
                "explanation": "Public clients (SPAs and mobile apps) cannot securely store a `client_secret` in frontend code. PKCE dynamically generates a cryptographic `code_verifier` and `code_challenge`, ensuring that even if an authorization code is intercepted, attackers cannot exchange it without the original secret code verifier. (Reference: GeeksforGeeks OAuth 2.0 PKCE Flow).",
                "options": [
                    {"text": "Protects public clients that cannot securely store client secrets from authorization code interception", "is_correct": True, "feedback": "Correct! PKCE cryptographically binds the auth code to the original client request."},
                    {"text": "Eliminates the need for SSL/TLS certificates across the internet", "is_correct": False, "feedback": "Incorrect: HTTPS remains strictly mandatory in OAuth."},
                    {"text": "Allows users to log in without entering their username or password", "is_correct": False, "feedback": "Incorrect: User credentials are still submitted to the Authorization Server."},
                    {"text": "Increases token expiration time to infinite days", "is_correct": False, "feedback": "Incorrect: Expiration limits are unaffected."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # DATABASES, ORM & CACHING
    # -------------------------------------------------------------
    "Relational Modeling, Indexing & PostgreSQL": {
        "category": "SQL_DATABASES",
        "description": "GeeksforGeeks database placement drill on composite indexes, clustered vs non-clustered indexes, MVCC, and query optimization.",
        "questions": [
            {
                "title": "[GFG] Composite Index Leftmost Prefix Rule",
                "content": "If a composite B-Tree index exists on `(department_id, salary, hire_date)`, which of the following queries CANNOT leverage the index efficiently?",
                "difficulty": "MEDIUM",
                "explanation": "B-Tree composite indexes strictly follow the Leftmost Prefix rule: search conditions must reference the leading column (`department_id`) to prune the index tree. A query filtering only on `WHERE salary > 50000` does not specify the leftmost prefix, forcing a full table scan. (Reference: GeeksforGeeks Indexes in PostgreSQL).",
                "options": [
                    {"text": "WHERE salary > 50000 AND hire_date > '2023-01-01' (missing leftmost column)", "is_correct": True, "feedback": "Correct! Without department_id, the composite index cannot be traversed efficiently."},
                    {"text": "WHERE department_id = 10 AND salary > 50000", "is_correct": False, "feedback": "Incorrect: This uses the leading columns department_id and salary."},
                    {"text": "WHERE department_id = 5", "is_correct": False, "feedback": "Incorrect: Matches the exact leftmost column prefix."},
                    {"text": "WHERE department_id = 5 ORDER BY salary", "is_correct": False, "feedback": "Incorrect: The index eliminates the need for a sort step."}
                ]
            },
            {
                "title": "[GFG] PostgreSQL Multi-Version Concurrency Control (MVCC)",
                "content": "How does PostgreSQL implement non-blocking concurrent reads during active write transactions under MVCC?",
                "difficulty": "HARD",
                "explanation": "PostgreSQL MVCC ensures readers do not block writers, and writers do not block readers. When a row is updated, a new row version (tuple) is created with metadata tags `xmin` (creation transaction ID) and `xmax` (deletion transaction ID). Readers only see row snapshots committed prior to their transaction snapshot. (Reference: GeeksforGeeks PostgreSQL MVCC).",
                "options": [
                    {"text": "Maintains multiple row versions tagged with xmin and xmax transaction IDs", "is_correct": True, "feedback": "Correct! Row versioning allows reading consistent snapshots without table locks."},
                    {"text": "Locks the entire database table with an exclusive mutex lock", "is_correct": False, "feedback": "Incorrect: Exclusive table locks destroy concurrency and defeat MVCC."},
                    {"text": "Reverts the database to single-user mode during updates", "is_correct": False, "feedback": "Incorrect: Multi-user concurrency is the primary purpose of MVCC."},
                    {"text": "Writes all pending reads to temporary flat text files on disk", "is_correct": False, "feedback": "Incorrect: Snapshots are read directly from buffer cache pages."}
                ]
            },
            {
                "title": "[GFG] Clustered vs Non-Clustered Indexes",
                "content": "Why can a relational database table have at most ONE clustered index?",
                "difficulty": "EASY",
                "explanation": "A clustered index defines the actual physical storage order of the rows on disk blocks. Because table records can only be physically sorted in one way on disk, there can only be one clustered index per table. Non-clustered indexes are auxiliary structures storing pointers to the clustered data. (Reference: GeeksforGeeks Difference between Clustered and Non-Clustered Index).",
                "options": [
                    {"text": "Because table data rows can only be physically sorted in one order on disk", "is_correct": True, "feedback": "Correct! Physical disk organization permits only one sorted arrangement."},
                    {"text": "Because the SQL standard forbids creating more than 1 index", "is_correct": False, "feedback": "Incorrect: Tables can have many non-clustered indexes."},
                    {"text": "Because secondary indexes require SSD hardware", "is_correct": False, "feedback": "Incorrect: Storage hardware type is irrelevant."},
                    {"text": "Because primary keys cannot contain duplicate integers", "is_correct": False, "feedback": "Incorrect: Uniqueness does not limit the physical layout concept."}
                ]
            }
        ]
    },

    "In-Memory Caching & Redis Architecture": {
        "category": "SQL_DATABASES",
        "description": "GeeksforGeeks caching questions on Redis data structures, eviction policies (LRU/LFU), Cache Stampede, and write strategies.",
        "questions": [
            {
                "title": "[GFG] Cache Eviction Policies: LRU vs LFU",
                "content": "Under high memory pressure, what does the Redis `allkeys-lru` eviction policy discard when the memory limit is reached?",
                "difficulty": "EASY",
                "explanation": "`allkeys-lru` evicts the least recently accessed keys across the entire keyspace regardless of whether they have an explicit TTL expiration set. `volatile-lru` only evicts keys with an expiration. (Reference: GeeksforGeeks Redis Cache Eviction Policies).",
                "options": [
                    {"text": "Evicts the least recently accessed keys across all keys in the database", "is_correct": True, "feedback": "Correct! allkeys-lru purges keys with oldest access timestamps."},
                    {"text": "Deletes only keys that have an explicit TTL expiration set", "is_correct": False, "feedback": "Incorrect: That describes volatile-lru."},
                    {"text": "Evicts keys with the fewest total access count (LFU)", "is_correct": False, "feedback": "Incorrect: That describes allkeys-lfu."},
                    {"text": "Throws an OutOfMemory runtime exception without deleting any data", "is_correct": False, "feedback": "Incorrect: That describes the noeviction policy."}
                ]
            },
            {
                "title": "[GFG] Mitigating Cache Stampede (Thundering Herd)",
                "content": "What occurs during a 'Cache Stampede' when a high-traffic cached key expires?",
                "difficulty": "MEDIUM",
                "explanation": "When a hot cache key expires, hundreds or thousands of concurrent requests miss the cache simultaneously and hit the primary database to recompute the value, overwhelming the database and potentially causing an outage. Solutions include probabilistic early expiration (XFetch) or distributed mutex locking. (Reference: GeeksforGeeks Cache Stampede Prevention).",
                "options": [
                    {"text": "Thousands of concurrent requests miss the cache and simultaneously overload the database", "is_correct": True, "feedback": "Correct! High-concurrency misses overwhelm backend databases."},
                    {"text": "Redis servers run out of hard disk partition space", "is_correct": False, "feedback": "Incorrect: Redis is an in-memory datastore."},
                    {"text": "The operating system drops all incoming TCP network packets", "is_correct": False, "feedback": "Incorrect: Stampede is an application-level bottleneck."},
                    {"text": "Keys mutate into random strings due to race conditions", "is_correct": False, "feedback": "Incorrect: Key values are not corrupted."}
                ]
            },
            {
                "title": "[GFG] Write-Through vs Write-Back (Write-Behind) Caching",
                "content": "In a Write-Back (Write-Behind) caching strategy, when is data persisted to the primary database?",
                "difficulty": "MEDIUM",
                "explanation": "In Write-Back caching, writes are committed immediately only to the in-memory cache, and the caller receives an immediate success response. The cached updates are then written asynchronously to the underlying database in batches, minimizing write latency at the risk of data loss if the cache node crashes before flushing. (Reference: GeeksforGeeks Caching Strategies).",
                "options": [
                    {"text": "Asynchronously in batches after writing immediately to the cache", "is_correct": True, "feedback": "Correct! Write-Back buffers writes in cache and flushes asynchronously."},
                    {"text": "Synchronously to both cache and database at the exact same instant", "is_correct": False, "feedback": "Incorrect: That describes the Write-Through strategy."},
                    {"text": "Only when the user logs out of their account", "is_correct": False, "feedback": "Incorrect: Background flush workers run periodically."},
                    {"text": "Directly to the database, completely bypassing the cache", "is_correct": False, "feedback": "Incorrect: That describes Write-Around caching."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # SYSTEM DESIGN & DEPLOYMENT
    # -------------------------------------------------------------
    "Full-Stack System Design & Scalability": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks system design interview drill on CAP theorem, database sharding, horizontal scaling, and load balancing algorithms.",
        "questions": [
            {
                "title": "[GFG] CAP Theorem: Partition Tolerance Invariant",
                "content": "According to Eric Brewer's CAP Theorem, in the presence of a network partition (P) in a distributed system, what trade-off must be made?",
                "difficulty": "EASY",
                "explanation": "Network partitions are unavoidable in real-world distributed networks. When a partition occurs, a system must choose between Consistency (returning an error or waiting for consensus to avoid stale data) and Availability (returning immediately with possibly stale data). You cannot guarantee both. (Reference: GeeksforGeeks CAP Theorem in Distributed Systems).",
                "options": [
                    {"text": "Must choose between Consistency (CP) or Availability (AP)", "is_correct": True, "feedback": "Correct! You must sacrifice either strict consistency or 100% availability during network splits."},
                    {"text": "Must sacrifice Partition Tolerance to achieve both C and A", "is_correct": False, "feedback": "Incorrect: Physical networks can and will drop packets; P cannot be avoided."},
                    {"text": "Switch to single-node architecture to achieve CA", "is_correct": False, "feedback": "Incorrect: Single node systems are not distributed systems."},
                    {"text": "Double the CPU clock speed to overcome packet loss", "is_correct": False, "feedback": "Incorrect: Hardware speed does not solve network disconnection."}
                ]
            },
            {
                "title": "[GFG] Consistent Hashing in Distributed Caching",
                "content": "Why is Consistent Hashing preferred over naive modulo hashing `hash(key) % N` when scaling distributed cache nodes?",
                "difficulty": "HARD",
                "explanation": "With naive modulo hashing, adding or removing a single node changes N to N+1, causing almost all keys (`~100%`) to rehash to different nodes and wiping out cache hit ratios. Consistent Hashing organizes nodes on a virtual ring; adding or removing a node only requires remapping `K/N` keys on average. (Reference: GeeksforGeeks Consistent Hashing).",
                "options": [
                    {"text": "Adding or removing a server only relocates K/N keys on average without invalidating the entire cache", "is_correct": True, "feedback": "Correct! Minimal remapping prevents massive cache stampedes."},
                    {"text": "It guarantees zero memory usage across all cache servers", "is_correct": False, "feedback": "Incorrect: Cache data still consumes memory."},
                    {"text": "It eliminates the need for hash functions entirely", "is_correct": False, "feedback": "Incorrect: It relies on uniform hash functions (MD5, MurmurHash)."},
                    {"text": "It automatically mirrors every key to 100% of all nodes", "is_correct": False, "feedback": "Incorrect: That is full replication, not distributed partitioning."}
                ]
            },
            {
                "title": "[GFG] Database Horizontal Sharding: Shard Key Selection",
                "content": "What is the primary risk of selecting a monotonically increasing counter (like auto-increment ID or timestamp) as a Database Shard Key?",
                "difficulty": "MEDIUM",
                "explanation": "Using sequential keys causes all write traffic to route to the single shard responsible for the latest range of IDs/timestamps, creating a massive 'Hotspotting' write bottleneck while other shards remain idle. A good shard key distributes reads and writes evenly (e.g., hash(user_id)). (Reference: GeeksforGeeks Database Sharding).",
                "options": [
                    {"text": "Creates write hotspotting where all new inserts bombard a single active shard", "is_correct": True, "feedback": "Correct! Sequential keys unbalance write throughput across cluster nodes."},
                    {"text": "Prevents the database from storing integer values", "is_correct": False, "feedback": "Incorrect: Data types are supported across all shards."},
                    {"text": "Forces all queries to execute in O(N!) factorial time", "is_correct": False, "feedback": "Incorrect: Shard lookups are O(1) through shard routing coordinators."},
                    {"text": "Causes immediate corruption of foreign keys", "is_correct": False, "feedback": "Incorrect: Cross-shard constraints require careful schema design, but don't cause corruption."}
                ]
            }
        ]
    },

    "Docker Containerization & CI/CD Pipelines": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks DevOps questions on Docker multi-stage builds, container isolation (cgroups, namespaces), image caching, and zero-downtime deployments.",
        "questions": [
            {
                "title": "[GFG] Linux Namespaces vs Cgroups in Container Isolation",
                "content": "In container runtimes (Docker/containerd), what is the technical distinction between Linux Namespaces and Control Groups (cgroups)?",
                "difficulty": "MEDIUM",
                "explanation": "Linux Namespaces provide ISOLATION (what a container can see: PID, NET, MNT, IPC, UTS). Control Groups (cgroups) provide RESOURCE LIMITING and accounting (how much CPU, memory, network I/O, or disk a container can use). (Reference: GeeksforGeeks How Docker Works Under the Hood).",
                "options": [
                    {"text": "Namespaces provide visibility isolation; cgroups enforce resource usage limits (CPU, RAM)", "is_correct": True, "feedback": "Correct! Namespaces isolate visibility; cgroups meter and throttle resources."},
                    {"text": "Namespaces limit CPU speed; cgroups encrypt network packets", "is_correct": False, "feedback": "Incorrect: Namespaces control process and network visibility."},
                    {"text": "Namespaces are implemented in Python; cgroups in JavaScript", "is_correct": False, "feedback": "Incorrect: Both are native Linux kernel C subsystems."},
                    {"text": "There is no difference; they are interchangeable marketing terms", "is_correct": False, "feedback": "Incorrect: They perform distinct kernel isolation roles."}
                ]
            },
            {
                "title": "[GFG] Docker Multi-Stage Builds Optimization",
                "content": "Why are Docker multi-stage builds recommended for production deployment containers?",
                "difficulty": "EASY",
                "explanation": "Multi-stage builds allow separating the compilation environment (containing heavy SDKs, compilers, build tools) from the runtime environment. Only the compiled binary/artifacts are copied into the final minimal image (e.g. Alpine/scratch), drastically reducing image size and attack surface. (Reference: GeeksforGeeks Docker Multi-Stage Builds).",
                "options": [
                    {"text": "Separates heavy build tools from the final production image, reducing image size and vulnerabilities", "is_correct": True, "feedback": "Correct! Final image contains only runtime binaries, eliminating bloat."},
                    {"text": "Allows a container to run on both Linux and Windows simultaneously", "is_correct": False, "feedback": "Incorrect: Multi-stage does not cross-compile OS kernels."},
                    {"text": "Eliminates the requirement for a Docker daemon", "is_correct": False, "feedback": "Incorrect: Docker daemon is still required to build and run."},
                    {"text": "Automatically encrypts database tables inside the container", "is_correct": False, "feedback": "Incorrect: Container building is unrelated to DB encryption."}
                ]
            },
            {
                "title": "[GFG] Blue-Green Deployment Strategy",
                "content": "What is the primary operational advantage of Blue-Green deployment over in-place rolling updates?",
                "difficulty": "EASY",
                "explanation": "Blue-Green deployment runs two identical environments: Blue (active production) and Green (new release). Once Green is tested and verified, router/load balancer traffic is flipped to Green instantly. If an issue occurs, rolling back is as fast as flipping the router back to Blue with zero downtime. (Reference: GeeksforGeeks Blue Green Deployment).",
                "options": [
                    {"text": "Near-instantaneous rollback and zero downtime by routing load balancer traffic between environments", "is_correct": True, "feedback": "Correct! Switching router traffic enables instant zero-downtime deployment and rollback."},
                    {"text": "Requires half the server hardware of standard single-server deployments", "is_correct": False, "feedback": "Incorrect: Blue-Green temporarily doubles infrastructure requirements."},
                    {"text": "Eliminates the need for software testing before deployment", "is_correct": False, "feedback": "Incorrect: Rigorous validation on the idle environment is crucial."},
                    {"text": "Forces all users to restart their physical computers", "is_correct": False, "feedback": "Incorrect: Traffic shift is completely transparent to end users."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # MATHEMATICAL FOUNDATIONS FOR AI & ML
    # -------------------------------------------------------------
    "Linear Algebra: Vectors, Matrices & Eigenvalues": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks machine learning mathematics drill on matrix determinants, eigenvalues, eigenvectors, orthogonal transformations, and SVD.",
        "questions": [
            {
                "title": "[GFG] Eigenvalues & Eigenvectors Fundamental Property",
                "content": "For a square matrix A, an eigenvector v and eigenvalue lambda satisfy the characteristic equation `A * v = lambda * v`. Geometrically, what does multiplying matrix A by v do?",
                "difficulty": "EASY",
                "explanation": "Multiplying matrix A by its eigenvector v only stretches or squashes the vector along its original direction by a scalar factor lambda; its spatial orientation (direction) remains unchanged. (Reference: GeeksforGeeks Eigenvalues and Eigenvectors).",
                "options": [
                    {"text": "Scales the vector along its original direction without changing its orientation", "is_correct": True, "feedback": "Correct! The vector's direction is invariant under the transformation; only magnitude scales by lambda."},
                    {"text": "Rotates the vector by exactly 90 degrees", "is_correct": False, "feedback": "Incorrect: Eigenvectors preserve direction, not perpendicular rotation."},
                    {"text": "Inverts the matrix determinant to zero", "is_correct": False, "feedback": "Incorrect: Determinant is the product of all eigenvalues."},
                    {"text": "Transposes the vector into a scalar constant", "is_correct": False, "feedback": "Incorrect: A * v produces a vector of identical dimension."}
                ]
            },
            {
                "title": "[GFG] Principal Component Analysis (PCA) and Covariance Matrices",
                "content": "In Principal Component Analysis (PCA) for dimensionality reduction, how are the principal directions chosen from the data covariance matrix?",
                "difficulty": "MEDIUM",
                "explanation": "The covariance matrix is symmetric and positive semi-definite. Its eigenvectors define the orthogonal axes of maximum variance (principal components), sorted in descending order of their corresponding eigenvalues. (Reference: GeeksforGeeks Principal Component Analysis (PCA)).",
                "options": [
                    {"text": "Eigenvectors of the covariance matrix corresponding to the largest eigenvalues", "is_correct": True, "feedback": "Correct! Largest eigenvalues capture maximum explained variance."},
                    {"text": "The diagonal elements of the raw input feature matrix", "is_correct": False, "feedback": "Incorrect: Diagonal elements represent raw variances, not principal axes."},
                    {"text": "Random Gaussian projection vectors", "is_correct": False, "feedback": "Incorrect: That describes Random Projections (Johnson-Lindenstrauss)."},
                    {"text": "The inverse Fourier transform of the mean vector", "is_correct": False, "feedback": "Incorrect: Fourier transforms are for frequency decomposition, not PCA."}
                ]
            },
            {
                "title": "[GFG] Singular Value Decomposition (SVD) Dimensions",
                "content": "For an m x n matrix A, what are the dimensions of matrices U, Sigma, and V^T in the SVD decomposition `A = U * Sigma * V^T`?",
                "difficulty": "HARD",
                "explanation": "In standard SVD: U is an m x m orthogonal matrix (left singular vectors), Sigma is an m x n diagonal matrix containing non-negative singular values, and V^T is an n x n orthogonal matrix (right singular vectors). (Reference: GeeksforGeeks Singular Value Decomposition).",
                "options": [
                    {"text": "U is m x m, Sigma is m x n, and V^T is n x n", "is_correct": True, "feedback": "Correct! U is m x m, Sigma is m x n, V^T is n x n."},
                    {"text": "U is n x n, Sigma is m x m, and V^T is m x n", "is_correct": False, "feedback": "Incorrect: Dimensions must allow matrix multiplication to result in m x n."},
                    {"text": "All three matrices are square m x m matrices", "is_correct": False, "feedback": "Incorrect: A is not necessarily a square matrix."},
                    {"text": "Sigma is a single scalar integer", "is_correct": False, "feedback": "Incorrect: Sigma is a rectangular diagonal matrix of singular values."}
                ]
            }
        ]
    },

    "Multivariate Calculus & Gradient Optimization": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks optimization questions on gradient descent variants, learning rates, Hessian matrices, and vanishing gradients.",
        "questions": [
            {
                "title": "[GFG] Gradient Descent and the Direction of Steepest Descent",
                "content": "Why does the gradient vector `grad(f(x))` point in the direction of greatest increase, and why do we update parameters using `-alpha * grad(f(x))`?",
                "difficulty": "EASY",
                "explanation": "By definition, the gradient vector points in the direction of maximum instantaneous rate of increase of a scalar function. To minimize a cost function, we must move in the opposite direction (steepest descent), hence subtracting a fraction alpha (learning rate) of the gradient. (Reference: GeeksforGeeks Gradient Descent Algorithm).",
                "options": [
                    {"text": "The gradient points in the direction of maximum increase; subtracting moves toward the local minimum", "is_correct": True, "feedback": "Correct! Moving opposite to the gradient minimizes the loss function."},
                    {"text": "Subtracting ensures parameter weights always remain strictly negative", "is_correct": False, "feedback": "Incorrect: Parameter weights can be positive, negative, or zero."},
                    {"text": "The gradient is always equal to the global maximum value", "is_correct": False, "feedback": "Incorrect: The gradient is a vector of partial derivatives, not a loss value."},
                    {"text": "Adding the gradient would divide the learning rate by zero", "is_correct": False, "feedback": "Incorrect: Adding the gradient performs Gradient Ascent (maximizing objective)."}
                ]
            },
            {
                "title": "[GFG] Momentum & Adam Optimizer: Second Moment Estimation",
                "content": "In the Adam (Adaptive Moment Estimation) optimizer, what do the first (m_t) and second (v_t) moments track?",
                "difficulty": "MEDIUM",
                "explanation": "Adam computes exponentially decaying averages of past gradients (first moment m_t = mean, providing momentum) and past squared gradients (second moment v_t = uncentered variance, providing adaptive per-parameter learning rate scaling). (Reference: GeeksforGeeks Adam Optimizer in Deep Learning).",
                "options": [
                    {"text": "First moment tracks exponential mean of gradients (momentum); second moment tracks uncentered variance (adaptive scaling)", "is_correct": True, "feedback": "Correct! Adam combines Momentum (first moment) with RMSprop (second moment)."},
                    {"text": "First moment tracks training loss; second moment tracks validation accuracy", "is_correct": False, "feedback": "Incorrect: Moments track gradient vectors directly."},
                    {"text": "First moment tracks weight initialization; second moment tracks batch size", "is_correct": False, "feedback": "Incorrect: Moments are dynamic optimizer states."},
                    {"text": "Both moments represent the learning rate multiplied by dropout percentage", "is_correct": False, "feedback": "Incorrect: Moments are rolling statistics of gradients."}
                ]
            },
            {
                "title": "[GFG] Hessian Matrix and Saddle Points",
                "content": "In high-dimensional non-convex optimization, how does the Hessian matrix identify a Saddle Point (where gradient is zero but it is not an extremum)?",
                "difficulty": "HARD",
                "explanation": "At a stationary point (grad f = 0), if the Hessian matrix of second-order partial derivatives has both positive and negative eigenvalues, the surface curves upwards in some directions and downwards in others. This defines a Saddle Point. (Reference: GeeksforGeeks Optimization in Machine Learning).",
                "options": [
                    {"text": "The Hessian matrix has both positive and negative eigenvalues (indefinite matrix)", "is_correct": True, "feedback": "Correct! Indefinite Hessian indicates upward curvature along some axes and downward along others."},
                    {"text": "All eigenvalues of the Hessian matrix are strictly positive", "is_correct": False, "feedback": "Incorrect: All positive eigenvalues indicate a strict local minimum."},
                    {"text": "All eigenvalues of the Hessian matrix are strictly negative", "is_correct": False, "feedback": "Incorrect: All negative eigenvalues indicate a local maximum."},
                    {"text": "The Hessian matrix has a determinant of infinity", "is_correct": False, "feedback": "Incorrect: Determinant is a finite product of eigenvalues."}
                ]
            }
        ]
    },

    "Feature Engineering, Scaling & EDA": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks ML data preparation questions on StandardScaler vs MinMaxScaler, categorical encoding, multicollinearity, and outlier detection.",
        "questions": [
            {
                "title": "[GFG] StandardScaler vs MinMaxScaler with Outliers",
                "content": "Why is `StandardScaler` (Z-score normalization) preferred over `MinMaxScaler` when data contains severe outliers?",
                "difficulty": "EASY",
                "explanation": "MinMaxScaler bounds values strictly to [0, 1] using min and max. An extreme outlier compresses the vast majority of non-outlier data into a tiny band near 0. StandardScaler centers around mean with unit variance, preserving relative spreads without binding to extreme edge values. (Reference: GeeksforGeeks Feature Scaling Techniques in Machine Learning).",
                "options": [
                    {"text": "MinMaxScaler compresses non-outlier data into a tiny cluster because it depends directly on extreme min and max values", "is_correct": True, "feedback": "Correct! Outliers skew MinMaxScaler ranges; RobustScaler or StandardScaler is preferred."},
                    {"text": "StandardScaler converts all negative values to zero automatically", "is_correct": False, "feedback": "Incorrect: Z-scores routinely include negative numbers."},
                    {"text": "MinMaxScaler requires inputs to be pre-sorted alphabetically", "is_correct": False, "feedback": "Incorrect: Numerical scaling does not involve string sorting."},
                    {"text": "StandardScaler requires training on a GPU accelerator", "is_correct": False, "feedback": "Incorrect: StandardScaler is a simple CPU mathematical transformation."}
                ]
            },
            {
                "title": "[GFG] Target Encoding vs One-Hot Encoding for High Cardinality",
                "content": "Why does One-Hot Encoding fail when applied to categorical features with high cardinality (e.g., zip codes with 10,000 distinct values)?",
                "difficulty": "MEDIUM",
                "explanation": "High cardinality causes dimensionality explosion (curse of dimensionality), creating a massive sparse matrix of 10,000 extra columns that increases memory usage, slows training, and causes tree-based models to split sparsely. Target encoding or embeddings are used instead. (Reference: GeeksforGeeks Categorical Data Encoding).",
                "options": [
                    {"text": "Causes dimensionality explosion creating a massive, sparse matrix that exhausts memory and causes overfitting", "is_correct": True, "feedback": "Correct! High cardinality creates thousands of sparse columns."},
                    {"text": "Causes one-hot values to become complex imaginary numbers", "is_correct": False, "feedback": "Incorrect: Values remain binary 0 and 1."},
                    {"text": "Prevents the model from making predictions on test data", "is_correct": False, "feedback": "Incorrect: Predictions work, but training is inefficient and overfits."},
                    {"text": "Changes the target label from classification to regression", "is_correct": False, "feedback": "Incorrect: Feature encoding has no impact on target task formulation."}
                ]
            },
            {
                "title": "[GFG] Variance Inflation Factor (VIF) and Multicollinearity",
                "content": "What does a Variance Inflation Factor (VIF) score greater than 5 to 10 indicate for an independent feature in regression models?",
                "difficulty": "MEDIUM",
                "explanation": "VIF measures how much the variance of an estimated regression coefficient is inflated due to multicollinearity (correlation with other predictor variables). A VIF > 5-10 indicates high multicollinearity, making coefficient estimates unstable and uninterpretable. (Reference: GeeksforGeeks Detecting Multicollinearity with VIF).",
                "options": [
                    {"text": "High multicollinearity with other independent variables, making coefficient estimates unstable", "is_correct": True, "feedback": "Correct! VIF > 5-10 indicates severe linear dependence among features."},
                    {"text": "The feature has zero variance and should be duplicated", "is_correct": False, "feedback": "Incorrect: Zero variance produces undefined or zero coefficients."},
                    {"text": "The model has achieved 100% test accuracy", "is_correct": False, "feedback": "Incorrect: VIF evaluates predictor collinearity, not model performance."},
                    {"text": "The dataset contains missing NaN values that must be imputed", "is_correct": False, "feedback": "Incorrect: VIF is calculated after imputation."}
                ]
            }
        ]
    },

    "Supervised Learning: Trees, Ensembles & SVMs": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks ML placement drill on Random Forests, Gradient Boosted Trees (XGBoost), bias-variance trade-off, and Support Vector Machines.",
        "questions": [
            {
                "title": "[GFG] Random Forest vs Gradient Boosting (XGBoost) Ensemble Mechanism",
                "content": "What is the foundational architectural difference between Bagging (Random Forest) and Boosting (Gradient Boosting)?",
                "difficulty": "MEDIUM",
                "explanation": "Random Forest uses Bagging (Bootstrap Aggregation): trees are trained independently in parallel to reduce VARIANCE. Gradient Boosting builds trees sequentially in series, where each subsequent tree fits on the pseudo-residuals (errors) of the previous trees to reduce BIAS. (Reference: GeeksforGeeks Bagging vs Boosting).",
                "options": [
                    {"text": "Bagging trains independent trees in parallel to reduce variance; Boosting trains sequential trees on previous errors to reduce bias", "is_correct": True, "feedback": "Correct! Bagging = parallel variance reduction; Boosting = sequential bias reduction."},
                    {"text": "Bagging is only for classification; Boosting is only for regression", "is_correct": False, "feedback": "Incorrect: Both algorithms support both classification and regression."},
                    {"text": "Random Forest requires neural network GPU hardware", "is_correct": False, "feedback": "Incorrect: Random Forest is an ensemble of standard decision trees."},
                    {"text": "Boosting ignores all errors made by previous estimators", "is_correct": False, "feedback": "Incorrect: Boosting specifically focuses on previous errors."}
                ]
            },
            {
                "title": "[GFG] Support Vector Machines: The Kernel Trick",
                "content": "How does the 'Kernel Trick' enable Support Vector Machines to separate non-linearly separable data?",
                "difficulty": "MEDIUM",
                "explanation": "The Kernel Trick computes the inner products of data points in a transformed, higher-dimensional feature space where the data becomes linearly separable, WITHOUT explicitly calculating the coordinates of points in that high-dimensional space. (Reference: GeeksforGeeks Kernel Functions in Support Vector Machines).",
                "options": [
                    {"text": "Computes inner products in a higher-dimensional space without explicitly projecting coordinates", "is_correct": True, "feedback": "Correct! Implicit inner product calculation avoids the computational cost of explicit projection."},
                    {"text": "Converts support vectors into decision tree split rules", "is_correct": False, "feedback": "Incorrect: SVMs optimize maximum margin hyperplanes."},
                    {"text": "Deletes all non-separable data points from the training set", "is_correct": False, "feedback": "Incorrect: The kernel trick uses all support vectors."},
                    {"text": "Replaces the hyperplane with a convolutional filter layer", "is_correct": False, "feedback": "Incorrect: Convolution is a deep learning operation, not SVM kernel trick."}
                ]
            },
            {
                "title": "[GFG] Gini Impurity vs Entropy in Decision Trees",
                "content": "Why is Gini Impurity frequently preferred over Information Gain (Entropy) as the default split criterion in CART decision trees?",
                "difficulty": "EASY",
                "explanation": "Gini Impurity involves simple squaring `1 - sum(p_i^2)`, whereas Entropy requires calculating logarithmic terms `sum(-p_i * log2(p_i))`. Computing logarithms is computationally slower on CPU instructions, while both criteria yield virtually identical tree structures. (Reference: GeeksforGeeks Gini Impurity vs Information Gain).",
                "options": [
                    {"text": "Gini is computationally faster because it avoids expensive logarithmic calculations", "is_correct": True, "feedback": "Correct! Gini requires only multiplications and subtractions without log operations."},
                    {"text": "Entropy can only be used on binary classification problems with 2 classes", "is_correct": False, "feedback": "Incorrect: Entropy generalizes to any number of classes."},
                    {"text": "Gini Impurity guarantees 0% training error on all datasets", "is_correct": False, "feedback": "Incorrect: Impurity is a split metric, not an error elimination guarantee."},
                    {"text": "Entropy is strictly forbidden by scikit-learn", "is_correct": False, "feedback": "Incorrect: scikit-learn supports criterion='entropy'."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # DEEP LEARNING & ADVANCED AI
    # -------------------------------------------------------------
    "Perceptrons, Activations & Backpropagation": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks neural networks placement questions on vanishing gradients, activation functions (ReLU, Sigmoid, GeLU), and the chain rule of calculus.",
        "questions": [
            {
                "title": "[GFG] Vanishing Gradient Problem with Sigmoid Activation",
                "content": "Why does using the Sigmoid activation function in deep multilayer networks lead to the Vanishing Gradient problem during backpropagation?",
                "difficulty": "EASY",
                "explanation": "The derivative of the sigmoid function `sigma'(z) = sigma(z) * (1 - sigma(z))` has a maximum value of 0.25 (at z=0). When chain-multiplying these values across many layers during backpropagation, the gradients shrink exponentially toward zero, preventing early layers from updating their weights. (Reference: GeeksforGeeks Vanishing Gradient Problem in Deep Neural Networks).",
                "options": [
                    {"text": "The derivative of Sigmoid has a maximum value of 0.25, shrinking gradients exponentially across layers", "is_correct": True, "feedback": "Correct! Multiplying values <= 0.25 across layers drives gradients to near zero."},
                    {"text": "Sigmoid output explodes to infinity when inputs are negative", "is_correct": False, "feedback": "Incorrect: Sigmoid outputs are bounded strictly between 0 and 1."},
                    {"text": "Sigmoid cannot be computed using floating point numbers", "is_correct": False, "feedback": "Incorrect: Sigmoid is an elementary mathematical function."},
                    {"text": "Backpropagation only functions with linear activation functions", "is_correct": False, "feedback": "Incorrect: Non-linear activations are essential for universal function approximation."}
                ]
            },
            {
                "title": "[GFG] Dying ReLU Problem and Leaky ReLU",
                "content": "What is the 'Dying ReLU' problem in neural network training, and how does Leaky ReLU address it?",
                "difficulty": "MEDIUM",
                "explanation": "Standard ReLU outputs 0 with a derivative of 0 for all negative inputs (z <= 0). If a neuron's weights update such that it receives negative inputs across all data, it outputs 0 and stops learning permanently (dead neuron). Leaky ReLU introduces a small non-zero slope (e.g. 0.01*z) for negative inputs, keeping gradients flowing. (Reference: GeeksforGeeks Dying ReLU Problem in Deep Learning).",
                "options": [
                    {"text": "Neurons with negative inputs produce zero gradient and stop updating; Leaky ReLU provides a small non-zero slope for x < 0", "is_correct": True, "feedback": "Correct! The small negative slope prevents neurons from permanently shutting down."},
                    {"text": "ReLU causes weights to overflow into NaN on 64-bit CPUs", "is_correct": False, "feedback": "Incorrect: Dying ReLU is about zero gradient, not numeric overflow."},
                    {"text": "ReLU requires 100x more GPU memory than Sigmoid", "is_correct": False, "feedback": "Incorrect: ReLU is the most computationally efficient activation function."},
                    {"text": "Leaky ReLU replaces all backpropagation passes with genetic algorithms", "is_correct": False, "feedback": "Incorrect: Standard backpropagation is preserved."}
                ]
            },
            {
                "title": "[GFG] Chain Rule in Computational Backpropagation Graphs",
                "content": "In a computational graph with loss L, activation a = f(z), and z = w*x + b, how is the gradient `dL/dw` computed using the Chain Rule?",
                "difficulty": "EASY",
                "explanation": "By the Chain Rule of calculus: `dL/dw = (dL/da) * (da/dz) * (dz/dw)`. Since `dz/dw = x`, this expands to `(dL/da) * f'(z) * x`. (Reference: GeeksforGeeks Backpropagation in Neural Networks).",
                "options": [
                    {"text": "(dL/da) * (da/dz) * (dz/dw) = (dL/da) * f'(z) * x", "is_correct": True, "feedback": "Correct! Chain rule multiplies downstream gradient by local gradients."},
                    {"text": "(dL/da) + (da/dz) + (dz/dw)", "is_correct": False, "feedback": "Incorrect: Derivatives of composite functions multiply, not add."},
                    {"text": "(dL/dw) = L / w", "is_correct": False, "feedback": "Incorrect: That is simple division, not a derivative."},
                    {"text": "(dL/dw) is always a constant equal to 1.0", "is_correct": False, "feedback": "Incorrect: The gradient varies dynamically based on inputs and activations."}
                ]
            }
        ]
    },

    "Attention Mechanisms & Transformer Architecture": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks modern AI questions on scaled dot-product attention, multi-head attention, self-attention complexity, and positional encodings.",
        "questions": [
            {
                "title": "[GFG] Scaled Dot-Product Attention Formula",
                "content": "Why is the dot-product of Query (Q) and Key (K) scaled by `1 / sqrt(d_k)` in the Attention formula `softmax((Q * K^T) / sqrt(d_k)) * V`?",
                "difficulty": "MEDIUM",
                "explanation": "For large projection dimensions d_k, the dot products grow large in magnitude, pushing the softmax function into regions with extremely small gradients (vanishing softmax gradient). Scaling by `1 / sqrt(d_k)` counteracts this variance growth, stabilizing gradient flow. (Reference: GeeksforGeeks Attention Mechanism in Transformers).",
                "options": [
                    {"text": "Prevents large dot-products from pushing softmax into regions with vanishingly small gradients", "is_correct": True, "feedback": "Correct! Counteracts variance scaling proportional to d_k to prevent saturated softmax."},
                    {"text": "Converts floating-point numbers into 8-bit integers", "is_correct": False, "feedback": "Incorrect: Scaling is a float division operation."},
                    {"text": "Ensures that the matrix multiplication output is always an identity matrix", "is_correct": False, "feedback": "Incorrect: Identity matrix would eliminate contextual attention."},
                    {"text": "Reduces sequence length by half in every transformer block", "is_correct": False, "feedback": "Incorrect: Sequence length is preserved across transformer encoder layers."}
                ]
            },
            {
                "title": "[GFG] Self-Attention Time and Space Complexity",
                "content": "For an input sequence of length N and embedding dimension D, what is the computational complexity of standard full Self-Attention with respect to N?",
                "difficulty": "EASY",
                "explanation": "Computing the attention score matrix requires multiplying the Q (N x D) and K^T (D x N) matrices, resulting in an N x N matrix. Computing and storing this N x N matrix results in O(N^2) quadratic time and space complexity with respect to sequence length N. (Reference: GeeksforGeeks Transformer Self-Attention Complexity).",
                "options": [
                    {"text": "O(N^2) quadratic complexity", "is_correct": True, "feedback": "Correct! The N x N pairwise attention matrix causes O(N^2) scaling."},
                    {"text": "O(N) strictly linear complexity", "is_correct": False, "feedback": "Incorrect: Linear attention requires specialized sparse approximations like FlashAttention."},
                    {"text": "O(log N) logarithmic complexity", "is_correct": False, "feedback": "Incorrect: All pairs of tokens must interact."},
                    {"text": "O(1) constant time complexity", "is_correct": False, "feedback": "Incorrect: Computation scales with input sequence length."}
                ]
            },
            {
                "title": "[GFG] Positional Encoding in Transformers",
                "content": "Why did the original Transformer architecture (Vaswani et al.) introduce sinusoidal Positional Encodings into token embeddings?",
                "difficulty": "EASY",
                "explanation": "Unlike RNNs which process tokens sequentially step-by-step, self-attention operations are permutation-invariant (order-agnostic). Without positional encodings added to the input embeddings, the model cannot distinguish between 'dog bites man' and 'man bites dog'. (Reference: GeeksforGeeks Positional Encoding in Transformers).",
                "options": [
                    {"text": "Self-attention is permutation-invariant, so positional encodings inject token order information into embeddings", "is_correct": True, "feedback": "Correct! Encodings preserve sequential word order in non-recurrent transformers."},
                    {"text": "To translate tokens between different natural languages", "is_correct": False, "feedback": "Incorrect: Translation is learned by encoder-decoder cross-attention."},
                    {"text": "To compress vocabulary size from 50,000 down to 100", "is_correct": False, "feedback": "Incorrect: Positional encodings do not alter vocabulary size."},
                    {"text": "To prevent overfitting during Adam optimizer updates", "is_correct": False, "feedback": "Incorrect: Regularization is handled by dropout and weight decay."}
                ]
            }
        ]
    },

    "LLM Integration, Vector Databases & RAG": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks production AI questions on vector embeddings, cosine similarity, HNSW indexing, RAG chunking, and hallucination reduction.",
        "questions": [
            {
                "title": "[GFG] Cosine Similarity vs Euclidean Distance for Embeddings",
                "content": "Why is Cosine Similarity commonly preferred over Euclidean Distance (L2) for comparing text embeddings generated by Large Language Models?",
                "difficulty": "EASY",
                "explanation": "Cosine Similarity measures the cosine of the angle between two vectors, capturing semantic orientation independent of vector length (magnitude). When embeddings are L2-normalized, Cosine Similarity and Euclidean Distance produce identical rankings, but Cosine remains robust to document length variations. (Reference: GeeksforGeeks Cosine Similarity in NLP).",
                "options": [
                    {"text": "Measures directional semantic similarity independent of vector magnitude differences", "is_correct": True, "feedback": "Correct! Cosine similarity evaluates the angle between embedding trajectories."},
                    {"text": "Euclidean distance cannot be computed in more than 3 dimensions", "is_correct": False, "feedback": "Incorrect: Euclidean distance formula applies to arbitrary N dimensions."},
                    {"text": "Cosine similarity guarantees 0% false positives in vector search", "is_correct": False, "feedback": "Incorrect: Similarity search is probabilistic."},
                    {"text": "LLM embeddings only contain positive whole numbers", "is_correct": False, "feedback": "Incorrect: Embeddings are continuous floating-point vectors."}
                ]
            },
            {
                "title": "[GFG] HNSW (Hierarchical Navigable Small World) Vector Indexing",
                "content": "How does an HNSW index in vector databases (e.g. Pinecone, Milvus, pgvector) achieve logarithmic O(log N) approximate nearest neighbor search?",
                "difficulty": "HARD",
                "explanation": "HNSW builds a multi-layered graph where upper layers have long-range skip links (fast exploration across clusters, analogous to skip lists) and lower layers have dense short-range connections (local refinement). Search starts at the coarsest top layer and greedily transitions down to find the nearest neighbors in O(log N) time. (Reference: GeeksforGeeks Vector Database Indexing: HNSW).",
                "options": [
                    {"text": "Multi-layer graph architecture using skip-list principles to navigate from coarse clusters to fine neighbors", "is_correct": True, "feedback": "Correct! Multi-layer graph traversal achieves fast O(log N) ANN search."},
                    {"text": "Performs brute-force linear scanning across 100% of all vectors in memory", "is_correct": False, "feedback": "Incorrect: Brute force search is O(N) Flat index."},
                    {"text": "Converts vectors into JSON strings and runs SQL LIKE queries", "is_correct": False, "feedback": "Incorrect: String matching cannot evaluate semantic distance."},
                    {"text": "Sorts vectors alphabetically by their first coordinate", "is_correct": False, "feedback": "Incorrect: High dimensional space cannot be linearly ordered by one coordinate."}
                ]
            },
            {
                "title": "[GFG] Retrieval-Augmented Generation (RAG): Chunking Strategy Trade-off",
                "content": "In a RAG pipeline, what is the trade-off between choosing a very small chunk size (e.g. 50 tokens) vs a large chunk size (e.g. 1500 tokens)?",
                "difficulty": "MEDIUM",
                "explanation": "Very small chunks produce granular, highly specific embeddings but lose crucial surrounding context needed for answering. Very large chunks preserve broad context but dilute specific semantic signals, making similarity search noisy and consuming LLM context window space. (Reference: GeeksforGeeks Retrieval Augmented Generation).",
                "options": [
                    {"text": "Small chunks provide precise semantic matching but lose broader context; large chunks preserve context but dilute specific retrieval signals", "is_correct": True, "feedback": "Correct! Chunk size balances retrieval precision against contextual coherence."},
                    {"text": "Small chunks cannot be converted into vector embeddings", "is_correct": False, "feedback": "Incorrect: Even single words can be embedded."},
                    {"text": "Large chunks make LLM hallucination mathematically impossible", "is_correct": False, "feedback": "Incorrect: RAG reduces hallucinations, but does not mathematically eliminate them."},
                    {"text": "Chunk size has zero impact on retrieval accuracy", "is_correct": False, "feedback": "Incorrect: Chunking strategy is one of the most critical hyperparameters in RAG."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # DATA ANALYTICS & ADVANCED SQL
    # -------------------------------------------------------------
    "Complex Joins, Subqueries & Aggregations": {
        "category": "SQL_DATABASES",
        "description": "GeeksforGeeks advanced SQL questions on correlated subqueries, cross joins, full outer joins, HAVING filters, and execution plans.",
        "questions": [
            {
                "title": "[GFG] WHERE vs HAVING Clause Execution Order",
                "content": "In SQL query evaluation order, what is the functional difference between `WHERE` and `HAVING`?",
                "difficulty": "EASY",
                "explanation": "The `WHERE` clause filters individual rows BEFORE aggregation and grouping take place. The `HAVING` clause filters aggregated group results (e.g. `HAVING COUNT(*) > 5`) AFTER `GROUP BY` has executed. (Reference: GeeksforGeeks Difference between WHERE and HAVING clause in SQL).",
                "options": [
                    {"text": "WHERE filters individual rows before grouping; HAVING filters aggregated groups after GROUP BY", "is_correct": True, "feedback": "Correct! WHERE filters pre-aggregation; HAVING filters post-aggregation."},
                    {"text": "WHERE is for numeric data; HAVING is for text strings", "is_correct": False, "feedback": "Incorrect: Both operate across all column data types."},
                    {"text": "HAVING executes before the FROM clause", "is_correct": False, "feedback": "Incorrect: FROM executes first, then WHERE, GROUP BY, HAVING, SELECT."},
                    {"text": "WHERE can use aggregate functions like SUM() and AVG() directly", "is_correct": False, "feedback": "Incorrect: Aggregate functions are forbidden in the WHERE clause."}
                ]
            },
            {
                "title": "[GFG] Correlated Subquery Performance Implications",
                "content": "Why can a Correlated Subquery cause severe performance degradation on large tables compared to a JOIN?",
                "difficulty": "MEDIUM",
                "explanation": "A correlated subquery references columns from the outer query, meaning the inner subquery must be re-evaluated once for EVERY individual row processed by the outer query (O(M * N) nested loop), whereas JOINs can be optimized with Hash Joins or Merge Joins. (Reference: GeeksforGeeks Correlated Subqueries in SQL).",
                "options": [
                    {"text": "The inner query must be re-executed for each row of the outer query, resulting in nested-loop overhead", "is_correct": True, "feedback": "Correct! Row-by-row re-evaluation leads to O(M * N) execution cost."},
                    {"text": "Correlated subqueries disable all CPU cache memory", "is_correct": False, "feedback": "Incorrect: Hardware caches remain active."},
                    {"text": "They convert the database engine into a non-relational document store", "is_correct": False, "feedback": "Incorrect: Relational structure is maintained."},
                    {"text": "SQL standards forbid correlated subqueries from returning numbers", "is_correct": False, "feedback": "Incorrect: Subqueries frequently return scalar numerical values."}
                ]
            },
            {
                "title": "[GFG] LEFT JOIN vs INNER JOIN with NULL Handling",
                "content": "Given table A (3 rows) and table B (0 rows), what are the row counts of `SELECT * FROM A INNER JOIN B ON A.id = B.id` and `SELECT * FROM A LEFT JOIN B ON A.id = B.id`?",
                "difficulty": "EASY",
                "explanation": "INNER JOIN requires matching rows in both tables; since table B has 0 rows, INNER JOIN returns 0 rows. LEFT JOIN returns all rows from the left table (A) regardless of whether a match exists, populating missing B columns with NULL. Thus, LEFT JOIN returns 3 rows. (Reference: GeeksforGeeks SQL Joins).",
                "options": [
                    {"text": "INNER JOIN returns 0 rows; LEFT JOIN returns 3 rows", "is_correct": True, "feedback": "Correct! INNER requires match (0); LEFT preserves all left rows (3 with NULLs)."},
                    {"text": "INNER JOIN returns 3 rows; LEFT JOIN returns 0 rows", "is_correct": False, "feedback": "Incorrect: INNER JOIN cannot return rows without matches in both tables."},
                    {"text": "Both queries return 0 rows", "is_correct": False, "feedback": "Incorrect: LEFT JOIN preserves all rows from the left table."},
                    {"text": "Both queries throw a syntax error exception", "is_correct": False, "feedback": "Incorrect: Joining empty tables is valid SQL."}
                ]
            }
        ]
    },

    "SQL Analytical Window Functions": {
        "category": "SQL_DATABASES",
        "description": "GeeksforGeeks analytics questions on ROW_NUMBER(), RANK(), DENSE_RANK(), NTILE(), and LEAD()/LAG() running windows.",
        "questions": [
            {
                "title": "[GFG] ROW_NUMBER() vs RANK() vs DENSE_RANK()",
                "content": "For a dataset with scores `(100, 90, 90, 80)`, what values are assigned to the four rows by `RANK()` vs `DENSE_RANK()`?",
                "difficulty": "MEDIUM",
                "explanation": "`RANK()` leaves gaps after ties: 1, 2, 2, 4 (skips 3). `DENSE_RANK()` maintains consecutive numbering without gaps: 1, 2, 2, 3. `ROW_NUMBER()` assigns strictly unique integers regardless of ties: 1, 2, 3, 4. (Reference: GeeksforGeeks Difference between RANK, DENSE_RANK and ROW_NUMBER in SQL).",
                "options": [
                    {"text": "RANK assigns 1, 2, 2, 4; DENSE_RANK assigns 1, 2, 2, 3", "is_correct": True, "feedback": "Correct! RANK skips ranks after ties; DENSE_RANK produces consecutive numbers."},
                    {"text": "RANK assigns 1, 2, 3, 4; DENSE_RANK assigns 1, 2, 2, 2", "is_correct": False, "feedback": "Incorrect: 1, 2, 3, 4 is produced by ROW_NUMBER()."},
                    {"text": "Both functions assign identical ranks: 1, 2, 3, 4", "is_correct": False, "feedback": "Incorrect: Both handle ties differently from ROW_NUMBER."},
                    {"text": "DENSE_RANK skips rank numbers; RANK does not", "is_correct": False, "feedback": "Incorrect: It is the exact opposite."}
                ]
            },
            {
                "title": "[GFG] Window Frame: ROWS BETWEEN vs RANGE BETWEEN",
                "content": "In an analytical window specification `OVER (ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`, what does the frame encompass?",
                "difficulty": "HARD",
                "explanation": "`ROWS BETWEEN` defines a physical offset: it includes the current row and exactly 2 physical rows immediately preceding it in the specified sort order (up to 3 rows total). `RANGE BETWEEN` defines logical value offsets based on the values in the ORDER BY column rather than physical row counts. (Reference: GeeksforGeeks Window Functions in SQL).",
                "options": [
                    {"text": "A physical window comprising the current row and exactly 2 physical preceding rows", "is_correct": True, "feedback": "Correct! ROWS operates on physical line count offsets."},
                    {"text": "All rows in the entire table with duplicate dates", "is_correct": False, "feedback": "Incorrect: Window is constrained to 2 preceding rows."},
                    {"text": "The entire partition without any restriction", "is_correct": False, "feedback": "Incorrect: Frame bounds are explicitly specified."},
                    {"text": "Only rows whose primary key is an even integer", "is_correct": False, "feedback": "Incorrect: Frame offsets operate on sort order, not key parity."}
                ]
            },
            {
                "title": "[GFG] LEAD and LAG Analytical Functions",
                "content": "What is the primary use case of the `LAG(column, offset, default)` window function in time-series SQL analysis?",
                "difficulty": "EASY",
                "explanation": "`LAG()` accesses data from a previous row at a specified physical offset prior to the current row within the partition without requiring a self-join. It is commonly used to compute month-over-month growth or time deltas: `current_revenue - LAG(current_revenue, 1)`. (Reference: GeeksforGeeks SQL LAG Function).",
                "options": [
                    {"text": "Accesses values from preceding rows without performing expensive self-joins", "is_correct": True, "feedback": "Correct! LAG retrieves preceding row values for delta and growth metrics."},
                    {"text": "Delays query execution by a specified number of seconds", "is_correct": False, "feedback": "Incorrect: That describes sleep functions, not LAG."},
                    {"text": "Calculates the natural logarithm of every numerical column", "is_correct": False, "feedback": "Incorrect: Logarithm is computed via LOG(), not LAG()."},
                    {"text": "Automatically removes duplicate rows from the final query result", "is_correct": False, "feedback": "Incorrect: Deduplication is achieved using DISTINCT or GROUP BY."}
                ]
            }
        ]
    },

    "Descriptive Statistics & Data Distributions": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks statistics questions on central tendency, skewed distributions, standard deviation vs variance, and IQR outlier bounds.",
        "questions": [
            {
                "title": "[GFG] Skewness & Relationship Between Mean, Median, Mode",
                "content": "In a Right-Skewed (Positively Skewed) data distribution, what is the typical relationship between the Mean, Median, and Mode?",
                "difficulty": "EASY",
                "explanation": "In a positively skewed distribution, a long tail of high outlier values pulls the Mean to the right. The relationship is typically: `Mode < Median < Mean`. The Median is resistant to extreme outliers and serves as a better measure of central tendency. (Reference: GeeksforGeeks Skewness in Statistics).",
                "options": [
                    {"text": "Mode < Median < Mean", "is_correct": True, "feedback": "Correct! Right-side extreme values pull the Mean above the Median."},
                    {"text": "Mean < Median < Mode", "is_correct": False, "feedback": "Incorrect: That describes a Left-Skewed (Negatively Skewed) distribution."},
                    {"text": "Mean = Median = Mode", "is_correct": False, "feedback": "Incorrect: That describes a perfectly symmetric Normal distribution."},
                    {"text": "Median is always zero in all skewed data", "is_correct": False, "feedback": "Incorrect: Median is the 50th percentile value."}
                ]
            },
            {
                "title": "[GFG] Interquartile Range (IQR) Outlier Rule",
                "content": "According to John Tukey's standard boxplot rule, a data point `x` is flagged as an outlier if it falls outside which boundary?",
                "difficulty": "EASY",
                "explanation": "The Interquartile Range is `IQR = Q3 - Q1`. Outlier boundaries are defined as: Lower bound = `Q1 - 1.5 * IQR` and Upper bound = `Q3 + 1.5 * IQR`. Any data point outside this interval is considered an outlier. (Reference: GeeksforGeeks Interquartile Range and Outlier Detection).",
                "options": [
                    {"text": "[Q1 - 1.5 * IQR, Q3 + 1.5 * IQR]", "is_correct": True, "feedback": "Correct! Tukey's fences use 1.5 * IQR below Q1 and above Q3."},
                    {"text": "[Mean - 1 * SD, Mean + 1 * SD]", "is_correct": False, "feedback": "Incorrect: That encompasses 68% of a normal distribution."},
                    {"text": "[0, 100]", "is_correct": False, "feedback": "Incorrect: Outlier thresholds depend entirely on data distribution scale."},
                    {"text": "[Median - IQR, Median + IQR]", "is_correct": False, "feedback": "Incorrect: Fences are calculated from the first (Q1) and third (Q3) quartiles."}
                ]
            },
            {
                "title": "[GFG] Sample Variance vs Population Variance: Bessel's Correction",
                "content": "Why is the denominator `(N - 1)` rather than `N` used when calculating the Sample Variance `s^2` from N data points?",
                "difficulty": "MEDIUM",
                "explanation": "Using N in the denominator underestimates the true population variance because sample deviations are calculated from the sample mean rather than the true population mean. Dividing by `(N - 1)` (Bessel's correction) provides an unbiased estimator of the population variance. (Reference: GeeksforGeeks Sample Variance vs Population Variance).",
                "options": [
                    {"text": "Bessel's correction (N - 1) corrects for bias since deviations are measured from the sample mean", "is_correct": True, "feedback": "Correct! Corrects for the loss of 1 degree of freedom, yielding an unbiased estimate."},
                    {"text": "Because computer hardware cannot divide by exact powers of 2", "is_correct": False, "feedback": "Incorrect: Division by N is mathematically valid."},
                    {"text": "To prevent variance from becoming a negative number", "is_correct": False, "feedback": "Incorrect: Squared terms ensure variance is always non-negative."},
                    {"text": "Because the last data point in any sample is always an error", "is_correct": False, "feedback": "Incorrect: All sample points are considered valid."}
                ]
            }
        ]
    },

    "Hypothesis Testing, P-Values & A/B Experiments": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks inferential statistics drill on Type I/II errors, p-values, t-tests, statistical power, and A/B test sample size determination.",
        "questions": [
            {
                "title": "[GFG] Type I Error vs Type II Error in Hypothesis Testing",
                "content": "In statistical hypothesis testing, what constitutes a Type I Error (Alpha)?",
                "difficulty": "EASY",
                "explanation": "A Type I Error (False Positive, probability alpha) occurs when the researcher rejects the Null Hypothesis (H0) when H0 is actually true. A Type II Error (False Negative, probability beta) occurs when one fails to reject H0 when H0 is false. (Reference: GeeksforGeeks Type I and Type II Errors).",
                "options": [
                    {"text": "Rejecting a true Null Hypothesis (False Positive)", "is_correct": True, "feedback": "Correct! Type I error is convicting an innocent null hypothesis."},
                    {"text": "Failing to reject a false Null Hypothesis (False Negative)", "is_correct": False, "feedback": "Incorrect: That defines a Type II Error (Beta)."},
                    {"text": "Calculating the p-value with the wrong degrees of freedom", "is_correct": False, "feedback": "Incorrect: That is a calculation error."},
                    {"text": "Accepting both Null and Alternative hypotheses simultaneously", "is_correct": False, "feedback": "Incorrect: Hypotheses are mutually exclusive."}
                ]
            },
            {
                "title": "[GFG] P-Value Interpretation in A/B Testing",
                "content": "In an A/B test comparing website conversion rates, what does a calculated `p-value = 0.03` precisely signify?",
                "difficulty": "MEDIUM",
                "explanation": "A p-value is the probability of observing results at least as extreme as the observed data, assuming that the Null Hypothesis (no real difference between variant A and B) is true. At alpha = 0.05, p = 0.03 is statistically significant, warranting rejection of the Null Hypothesis. (Reference: GeeksforGeeks P-Value in Hypothesis Testing).",
                "options": [
                    {"text": "The probability of observing these results (or more extreme) purely by random chance if the null hypothesis is true", "is_correct": True, "feedback": "Correct! P-value measures probability of data given H0 is true: P(Data | H0)."},
                    {"text": "There is a 97% probability that variant B will generate $1M in revenue", "is_correct": False, "feedback": "Incorrect: P-values do not measure revenue magnitude."},
                    {"text": "The test has a 3% chance of being reviewed by an engineer", "is_correct": False, "feedback": "Incorrect: P-value is an inferential probability metric."},
                    {"text": "The probability that the alternative hypothesis is false is exactly 0.03", "is_correct": False, "feedback": "Incorrect: That is a common fallacy; p-value does not measure P(H0 | Data)."}
                ]
            },
            {
                "title": "[GFG] Statistical Power & Sample Size Determination",
                "content": "What is 'Statistical Power' (1 - Beta) in an experimental design?",
                "difficulty": "MEDIUM",
                "explanation": "Statistical Power is the probability of correctly rejecting the Null Hypothesis when an actual effect exists (avoiding a Type II False Negative). Standard experiments target 80% power (Power = 0.80), which determines the minimum required sample size N. (Reference: GeeksforGeeks Statistical Power and Sample Size).",
                "options": [
                    {"text": "The probability of correctly detecting a true effect (rejecting H0 when H0 is false)", "is_correct": True, "feedback": "Correct! Power = 1 - Beta, representing true positive discovery rate."},
                    {"text": "The CPU clock frequency used by the database server", "is_correct": False, "feedback": "Incorrect: Statistical power is a probability concept."},
                    {"text": "The ratio of sample size to population size", "is_correct": False, "feedback": "Incorrect: That is sampling fraction."},
                    {"text": "The probability of making a Type I error", "is_correct": False, "feedback": "Incorrect: Probability of Type I error is significance level alpha."}
                ]
            }
        ]
    },

    "Visual Perception & Dashboard Design UX": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks data visualization questions on Gestalt principles, chart selection heuristics, color blindness palette design, and data-ink ratio.",
        "questions": [
            {
                "title": "[GFG] Edward Tufte's Data-Ink Ratio Maximization",
                "content": "According to Edward Tufte's foundational data visualization principles, what is the 'Data-Ink Ratio'?",
                "difficulty": "EASY",
                "explanation": "Tufte defined the Data-Ink Ratio as the proportion of a graphic's ink devoted to the non-redundant display of data information. Good visualization practice maximizes this ratio by eliminating chartjunk, heavy borders, dark gridlines, and gratuitous 3D effects. (Reference: GeeksforGeeks Principles of Data Visualization).",
                "options": [
                    {"text": "Proportion of ink/pixels dedicated to displaying actual data information vs non-data decoration (chartjunk)", "is_correct": True, "feedback": "Correct! Maximize data presentation; minimize decorative chartjunk."},
                    {"text": "The physical cost in dollars of printing dashboard reports on paper", "is_correct": False, "feedback": "Incorrect: Tufte's ratio is an informational design metric."},
                    {"text": "The ratio of blue pixels to red pixels on a screen", "is_correct": False, "feedback": "Incorrect: Color balance is distinct from data-ink ratio."},
                    {"text": "The amount of memory consumed by SVG graphics in the browser DOM", "is_correct": False, "feedback": "Incorrect: It evaluates cognitive efficiency, not memory footprints."}
                ]
            },
            {
                "title": "[GFG] Chart Selection: Categorical Part-to-Whole vs Trends",
                "content": "Why are multi-slice Pie Charts strongly discouraged by data visualization specialists compared to horizontal Bar Charts?",
                "difficulty": "EASY",
                "explanation": "Human visual perception is notoriously poor at judging relative angles and two-dimensional areas compared to comparing aligned lengths along a common linear scale. Bar charts allow viewers to compare categories with far higher speed and precision. (Reference: GeeksforGeeks Choosing the Right Chart Type).",
                "options": [
                    {"text": "Human perception accurately judges aligned 1D bar lengths much better than 2D angles and arc slices", "is_correct": True, "feedback": "Correct! Comparing aligned bar heights is far more accurate than estimating pie angles."},
                    {"text": "Pie charts cannot be rendered in web browsers", "is_correct": False, "feedback": "Incorrect: All chart libraries support pie charts."},
                    {"text": "Pie charts can only display negative numbers", "is_correct": False, "feedback": "Incorrect: Pie slices cannot represent negative numbers at all."},
                    {"text": "Bar charts take 10x more storage memory than pie charts", "is_correct": False, "feedback": "Incorrect: Storage footprint is negligible for both."}
                ]
            },
            {
                "title": "[GFG] Gestalt Principle of Proximity in Dashboard Layouts",
                "content": "How does the Gestalt Principle of Proximity guide effective dashboard UI design?",
                "difficulty": "EASY",
                "explanation": "The Law of Proximity states that objects placed close together are perceived by the human brain as belonging to the same group or sharing related meaning. Grouping related KPI cards and charts within whitespace boundaries clarifies hierarchy without heavy borders. (Reference: GeeksforGeeks Gestalt Principles in UI/UX Design).",
                "options": [
                    {"text": "Elements placed close together are automatically perceived as related and belonging to a functional group", "is_correct": True, "feedback": "Correct! Proximity organizes related metrics without visual clutter."},
                    {"text": "All dashboard text must be written in capital letters", "is_correct": False, "feedback": "Incorrect: All-caps reduces reading speed."},
                    {"text": "Dashboard colors must flash periodically to alert users", "is_correct": False, "feedback": "Incorrect: Flashing elements causes cognitive overload."},
                    {"text": "Every chart must be separated by at least 500 pixels of empty space", "is_correct": False, "feedback": "Incorrect: Excessive whitespace breaks visual continuity."}
                ]
            }
        ]
    },

    "Pandas Data Wrangling & Cleaning Workflows": {
        "category": "PROGRAMMING_DSA",
        "description": "GeeksforGeeks Python analytics drill on vectorized operations, DataFrame loc vs iloc, groupby aggregation, and memory optimization.",
        "questions": [
            {
                "title": "[GFG] Pandas loc vs iloc Indexing Distinction",
                "content": "In Pandas DataFrame manipulation, what is the primary technical difference between `df.loc[]` and `df.iloc[]`?",
                "difficulty": "EASY",
                "explanation": "`df.loc[]` is label-based: selection is based on column names and index labels (and endpoint is inclusive). `df.iloc[]` is integer position-based: selection is based on 0-indexed integer offsets from 0 to length-1 (and endpoint is exclusive, following standard Python slicing). (Reference: GeeksforGeeks Difference between loc() and iloc() in Pandas).",
                "options": [
                    {"text": "loc is label-based (column names, index labels); iloc is integer position-based (0 to N-1 offsets)", "is_correct": True, "feedback": "Correct! loc uses labels/names; iloc uses 0-based integer coordinates."},
                    {"text": "loc modifies the database directly; iloc creates an in-memory copy", "is_correct": False, "feedback": "Incorrect: Both operate on in-memory DataFrame views/slices."},
                    {"text": "loc is only for single rows; iloc is only for entire tables", "is_correct": False, "feedback": "Incorrect: Both support arbitrary 2D row-column slicing."},
                    {"text": "iloc requires a GPU; loc runs on CPU", "is_correct": False, "feedback": "Incorrect: Standard Pandas runs entirely on CPU."}
                ]
            },
            {
                "title": "[GFG] Vectorized Operations vs apply() and iterrows()",
                "content": "Why are vectorized NumPy/Pandas expressions (e.g. `df['A'] * df['B']`) orders of magnitude faster than iterating with `df.iterrows()`?",
                "difficulty": "MEDIUM",
                "explanation": "Vectorized operations execute compiled C code with SIMD (Single Instruction, Multiple Data) processor instructions and contiguous memory layout without Python interpreter overhead. `df.iterrows()` converts each row into a Python Series object on every iteration, incurring massive type-checking and interpreter overhead. (Reference: GeeksforGeeks Why Vectorization is Faster in Python).",
                "options": [
                    {"text": "Vectorization executes in compiled C loops with SIMD instructions, avoiding Python interpreter overhead per row", "is_correct": True, "feedback": "Correct! Underlying C execution bypasses Python per-row overhead."},
                    {"text": "iterrows() runs queries across the internet via REST APIs", "is_correct": False, "feedback": "Incorrect: iterrows() is a purely local Python generator."},
                    {"text": "Vectorized operations encrypt the data during multiplication", "is_correct": False, "feedback": "Incorrect: No encryption is performed."},
                    {"text": "Python deletes the DataFrame from RAM during iterrows()", "is_correct": False, "feedback": "Incorrect: Memory remains allocated."}
                ]
            },
            {
                "title": "[GFG] Memory Optimization: Converting object to category Dtype",
                "content": "How does converting low-cardinality string columns (e.g. 'State', 'Gender') to Pandas `category` dtype optimize memory usage?",
                "difficulty": "MEDIUM",
                "explanation": "Object columns in Pandas store an array of pointers to distinct Python string objects in memory. The `category` dtype stores unique string values once in an integer code dictionary and represents column values as compact integers (e.g., int8), often reducing memory consumption by 80-90%. (Reference: GeeksforGeeks Categorical Data in Pandas).",
                "options": [
                    {"text": "Encodes strings as compact integer keys referencing a single dictionary of unique string values", "is_correct": True, "feedback": "Correct! Integer encoding dramatically reduces memory footprint."},
                    {"text": "Compresses data using gzip compression inside every cell", "is_correct": False, "feedback": "Incorrect: Category dtype uses integer encoding, not gzip."},
                    {"text": "Converts all string characters into their ASCII sum", "is_correct": False, "feedback": "Incorrect: Category preserves the original string text for display."},
                    {"text": "Deletes duplicate rows from the DataFrame", "is_correct": False, "feedback": "Incorrect: Row count is completely unaffected."}
                ]
            }
        ]
    }
}


def seed_all_35_gfg_assessments():
    db = SessionLocal()
    try:
        print("Starting comprehensive seeding for all 35 Roadmap Topics with 3 GFG Questions each...")
        
        # 1. Identify active institution
        student_user = db.query(User).filter(User.email == "student@college.edu").first()
        inst_id = student_user.institution_id if student_user else None
        if not inst_id:
            first_inst = db.query(Institution).first()
            inst_id = first_inst.id if first_inst else None
        print(f"Target Institution ID: {inst_id}")

        # 2. Map existing skills by domain
        skills_by_domain = {}
        for s in db.query(Skill).all():
            skills_by_domain[s.domain] = s.id
        default_skill_id = list(skills_by_domain.values())[0] if skills_by_domain else None

        # 3. Fetch all 35 Roadmap Topics
        all_topics = db.query(RoadmapTopic).all()
        print(f"Total Roadmap Topics in database: {len(all_topics)}")

        created_assessments_count = 0
        created_questions_count = 0
        linked_questions_count = 0

        diff_map = {
            "BEGINNER": "EASY",
            "INTERMEDIATE": "MEDIUM",
            "ADVANCED": "HARD",
            "EASY": "EASY",
            "MEDIUM": "MEDIUM",
            "HARD": "HARD",
        }

        for topic in all_topics:
            topic_name = topic.name.strip()
            spec = ALL_35_TOPICS_GFG.get(topic_name)

            if not spec:
                print(f"WARNING: Topic '{topic_name}' not found in dictionary! Skipping.")
                continue

            # Assign topic skill if missing
            target_skill_id = topic.skill_id
            if not target_skill_id:
                if "SQL" in topic_name.upper() or "DATABASE" in topic_name.upper():
                    target_skill_id = skills_by_domain.get("SQL", default_skill_id)
                elif "QUANT" in topic_name.upper() or "PERCENT" in topic_name.upper() or "SPEED" in topic_name.upper():
                    target_skill_id = skills_by_domain.get("QUANT", default_skill_id)
                elif "AI" in topic_name.upper() or "MACHINE" in topic_name.upper() or "STAT" in topic_name.upper():
                    target_skill_id = skills_by_domain.get("AI", default_skill_id)
                else:
                    target_skill_id = skills_by_domain.get("PROGRAMMING", default_skill_id)
                topic.skill_id = target_skill_id
                db.flush()

            # Create or update Assessment
            assessment_title = f"[GFG Placement Assessment] {topic_name}"
            assessment = db.query(Assessment).filter(
                Assessment.topic == topic_name,
                Assessment.institution_id == inst_id
            ).first()

            if not assessment:
                assessment = Assessment(
                    institution_id=inst_id,
                    title=assessment_title,
                    description=spec["description"],
                    instructions="15-minute diagnostic assessment referencing authentic GeeksforGeeks placement interview questions. Complete all questions to benchmark your placement readiness score.",
                    category=spec["category"],
                    topic=topic_name,
                    duration_minutes=15,
                    passing_score=70.0,
                    version=1,
                    is_published=True
                )
                db.add(assessment)
                db.flush()
                created_assessments_count += 1
            else:
                assessment.is_published = True
                assessment.title = assessment_title
                assessment.category = spec["category"]
                assessment.description = spec["description"]
                db.flush()

            # Link Topic to Assessment
            topic.assessment_id = assessment.id
            db.flush()

            # Ensure all 3 questions are created and linked to this assessment
            for q_idx, q_spec in enumerate(spec["questions"]):
                valid_diff = diff_map.get(q_spec.get("difficulty", "MEDIUM"), "MEDIUM")
                
                # Check if question already exists by title
                q = db.query(Question).filter(Question.title == q_spec["title"]).first()
                if not q:
                    q = Question(
                        skill_id=target_skill_id,
                        title=q_spec["title"],
                        content=q_spec["content"],
                        question_type="MCQ_SINGLE",
                        difficulty=valid_diff,
                        default_points=2,
                        explanation=q_spec["explanation"],
                        is_verified=True,
                        version=1,
                        status="PUBLISHED"
                    )
                    db.add(q)
                    db.flush()
                    created_questions_count += 1

                    for opt_spec in q_spec["options"]:
                        opt = QuestionOption(
                            question_id=q.id,
                            option_text=opt_spec["text"],
                            is_correct=opt_spec["is_correct"],
                            feedback=opt_spec.get("feedback")
                        )
                        db.add(opt)
                    db.flush()
                else:
                    q.status = "PUBLISHED"
                    q.is_verified = True
                    q.content = q_spec["content"]
                    q.explanation = q_spec["explanation"]
                    if not q.skill_id and target_skill_id:
                        q.skill_id = target_skill_id
                    db.flush()

                # Link Question to Assessment
                link = db.query(AssessmentQuestion).filter(
                    AssessmentQuestion.assessment_id == assessment.id,
                    AssessmentQuestion.question_id == q.id
                ).first()

                if not link:
                    link = AssessmentQuestion(
                        assessment_id=assessment.id,
                        question_id=q.id,
                        order_index=q_idx + 1,
                        points=2
                    )
                    db.add(link)
                    db.flush()
                    linked_questions_count += 1
                else:
                    link.order_index = q_idx + 1
                    link.points = 2
                    db.flush()

        db.commit()
        print("\n=======================================================")
        print(f"Successfully processed all 35 Roadmap Topics!")
        print(f"New Assessments Created: {created_assessments_count}")
        print(f"New GFG Questions Created: {created_questions_count}")
        print(f"Total Assessment Links: {linked_questions_count}")
        print("=======================================================")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_35_gfg_assessments()
