"""
Seed script for Career Paths, Roadmaps, Subjects, Topics, Subtopics, and Learning Materials.
Provides database-backed curriculum for:
- Software Development Engineer (SDE)
- Full-Stack Developer (FULLSTACK)
- AI/ML Engineer (AIML)
- Data Analyst (DATA_ANALYST)
"""

from app.core.database import SessionLocal
from app.models.roadmap import (
    CareerPath,
    RoadmapSubject,
    RoadmapTopic,
    RoadmapSubtopic,
    LearningResource,
)
from app.models.dsa import DSATopic
from app.models.skill import Skill


def seed_roadmaps():
    db = SessionLocal()
    try:
        print("Seeding Career Paths and Structured Roadmaps...")

        # -------------------------------------------------------------
        # 1. Career Paths
        # -------------------------------------------------------------
        career_paths_data = [
            {
                "code": "SDE",
                "title": "Software Development Engineer (SDE)",
                "description": "Comprehensive interview curriculum covering algorithms, system structures, computer science fundamentals, and quantitative drills.",
                "target_role": "Software Development Engineer",
                "display_order": 1,
            },
            {
                "code": "FULLSTACK",
                "title": "Full-Stack Web Developer",
                "description": "Full-stack web engineering pathway focusing on frontend, backend APIs, relational databases, distributed state, and modern software design.",
                "target_role": "Full-Stack Developer",
                "display_order": 2,
            },
            {
                "code": "AIML",
                "title": "AI & Machine Learning Engineer",
                "description": "Applied intelligence track emphasizing mathematical foundations, data processing pipelines, neural architectures, and LLM integrations.",
                "target_role": "AI/ML Engineer",
                "display_order": 3,
            },
            {
                "code": "DATA_ANALYST",
                "title": "Data Analyst & Business Intelligence",
                "description": "Analytical pathway covering SQL queries, statistical reasoning, data modeling, visualization dashboards, and metric analysis.",
                "target_role": "Data Analyst",
                "display_order": 4,
            },
        ]

        paths_by_code = {}
        for cp_data in career_paths_data:
            cp = db.query(CareerPath).filter(CareerPath.code == cp_data["code"]).first()
            if not cp:
                cp = CareerPath(**cp_data)
                db.add(cp)
                db.flush()
                print(f"Created Career Path: {cp.title}")
            else:
                paths_by_code[cp.code] = cp
                print(f"Career Path already exists: {cp.title}")
            paths_by_code[cp_data["code"]] = cp

        # Cache DSA Topics for linking
        dsa_topics = {t.slug: t.id for t in db.query(DSATopic).all()}

        # Cache Skills for linking
        skills = {s.domain: s.id for s in db.query(Skill).all()}

        # -------------------------------------------------------------
        # 2. SDE Roadmap Structure
        # -------------------------------------------------------------
        sde_path = paths_by_code["SDE"]

        subjects_data = [
            {
                "code": "PROG",
                "name": "Programming Fundamentals & OOP",
                "description": "Variables, types, control flow, functions, recursion, and object-oriented paradigms.",
                "icon": "Code",
                "display_order": 1,
                "topics": [
                    {
                        "slug": "prog-fundamentals",
                        "name": "Variables, Types & Control Flow",
                        "description": "Primitive data types, type casting, condition branches, and iteration mechanics.",
                        "learning_objectives": "Master memory allocation of primitive types, scope rules, and short-circuit boolean evaluation.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 90,
                        "display_order": 1,
                        "subtopics": [
                            {"name": "Primitive & Reference Types", "description": "Memory layout, values vs pointers"},
                            {"name": "Branching & Looping Constructs", "description": "if-else, switch-case, for/while optimization"},
                        ],
                        "resources": [
                            {
                                "title": "Comprehensive Guide to Memory Models & Type Systems",
                                "description": "How the stack and heap manage variables in Python and Java during runtime execution.",
                                "resource_type": "ARTICLE",
                                "difficulty": "EASY",
                                "estimated_duration_min": 20,
                                "content": (
                                    "# Memory Models and Type Systems\n\n"
                                    "Understanding how values reside in memory is the foundation of high-performance programming.\n\n"
                                    "### Stack vs. Heap Allocation\n"
                                    "- **Stack**: Manages local variables, primitive values, and function call frames with LIFO discipline.\n"
                                    "- **Heap**: Stores dynamically allocated objects, lists, and reference instances managed by garbage collection.\n\n"
                                    "### Best Practices for Interview Coding\n"
                                    "1. Avoid unnecessary object allocation inside tight loops.\n"
                                    "2. Recognize pass-by-value vs pass-by-reference semantics in chosen languages."
                                ),
                            }
                        ],
                    },
                    {
                        "slug": "prog-functions-recursion",
                        "name": "Functions, Scope & Recursion",
                        "description": "Function signatures, parameter passing, call stack frames, and recursive decomposition.",
                        "learning_objectives": "Construct recursive mathematical models and analyze recursive call stack memory limits.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 120,
                        "display_order": 2,
                        "subtopics": [
                            {"name": "Call Stack Frame Lifecycle", "description": "Activation records, return address, local frames"},
                            {"name": "Recursive Invariants & Base Cases", "description": "Avoiding stack overflow errors, tail call recursion"},
                        ],
                        "resources": [
                            {
                                "title": "Recursion Foundations & Call Stack Invariants",
                                "description": "Deconstructing recursive algorithms with inductive proofs and call stack diagrams.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": (
                                    "# Demystifying Recursion\n\n"
                                    "Every recursive solution relies on two essential parts:\n"
                                    "1. **The Base Case**: Stops recursion before stack overflow.\n"
                                    "2. **The Recurrence Step**: Reduces the problem to a strictly smaller subproblem.\n\n"
                                    "```python\n"
                                    "def factorial(n: int) -> int:\n"
                                    "    if n <= 1: return 1\n"
                                    "    return n * factorial(n - 1)\n"
                                    "```"
                                ),
                            }
                        ],
                    },
                    {
                        "slug": "prog-oop",
                        "name": "Object-Oriented Programming (OOP)",
                        "description": "Encapsulation, inheritance, polymorphism, and abstraction principles.",
                        "learning_objectives": "Implement decoupled object-oriented systems following SOLID architectural principles.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 120,
                        "display_order": 3,
                        "subtopics": [
                            {"name": "Encapsulation & Abstraction", "description": "Access modifiers, interface contracts"},
                            {"name": "Inheritance & Dynamic Polymorphism", "description": "Method overriding, vtables, abstract classes"},
                        ],
                        "resources": [
                            {
                                "title": "SOLID Principles & Object-Oriented Architecture",
                                "description": "Architecting maintainable object hierarchies and interface design for technical evaluations.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": (
                                    "# SOLID Principles in Software Engineering\n\n"
                                    "- **S**: Single Responsibility Principle\n"
                                    "- **O**: Open/Closed Principle\n"
                                    "- **L**: Liskov Substitution Principle\n"
                                    "- **I**: Interface Segregation Principle\n"
                                    "- **D**: Dependency Inversion Principle"
                                ),
                            }
                        ],
                    },
                ],
            },
            {
                "code": "DSA",
                "name": "Data Structures & Algorithms",
                "description": "LeetCode-style problem solving across arrays, lists, trees, graphs, and dynamic programming.",
                "icon": "Binary",
                "display_order": 2,
                "topics": [
                    {
                        "slug": "dsa-arrays-strings",
                        "name": "Arrays & Strings",
                        "description": "Contiguous memory layout, prefix sums, two pointers, and sliding window patterns.",
                        "learning_objectives": "Solve linear search, partition, and window substring problems in O(N) time.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 180,
                        "display_order": 1,
                        "dsa_topic_slug": "arrays-and-strings",
                        "subtopics": [
                            {"name": "Prefix Sums & Range Queries", "description": "O(1) range sums via preprocessing"},
                            {"name": "Two Pointers Technique", "description": "Opposite ends, fast/slow runners"},
                            {"name": "Sliding Window Pattern", "description": "Fixed and dynamic window substring problems"},
                        ],
                        "resources": [
                            {
                                "title": "The Two Pointers & Sliding Window Masterclass",
                                "description": "Step-by-step algorithmic blueprints for two pointers and dynamic sliding windows.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 35,
                                "content": (
                                    "# Two Pointers and Sliding Window Patterns\n\n"
                                    "When searching for pairs or subarrays satisfying a monotonic condition, Two Pointers reduces O(N^2) brute force to O(N).\n\n"
                                    "### Template: Opposite Direction Two Pointers\n"
                                    "```python\n"
                                    "left, right = 0, len(nums) - 1\n"
                                    "while left < right:\n"
                                    "    curr_sum = nums[left] + nums[right]\n"
                                    "    if curr_sum == target: return [left, right]\n"
                                    "    elif curr_sum < target: left += 1\n"
                                    "    else: right -= 1\n"
                                    "```"
                                ),
                            }
                        ],
                    },
                    {
                        "slug": "dsa-linked-lists",
                        "name": "Linked Lists",
                        "description": "Pointer manipulation, cycle detection, list reversal, and merge patterns.",
                        "learning_objectives": "Safely reorder nodes and detect cycles in O(1) auxiliary space.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 150,
                        "display_order": 2,
                        "dsa_topic_slug": "linked-lists",
                        "subtopics": [
                            {"name": "In-Place List Reversal", "description": "Three-pointer iterative pointer redirection"},
                            {"name": "Floyd's Cycle Finding Algorithm", "description": "Tortoise and Hare fast/slow pointers"},
                        ],
                        "resources": [
                            {
                                "title": "Pointer Invariants & Cycle Detection Proof",
                                "description": "Mathematical proof and implementation of Floyd's Tortoise and Hare algorithm.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": (
                                    "# Floyd's Cycle Detection Algorithm\n\n"
                                    "Fast pointer moves 2 steps, Slow pointer moves 1 step.\n"
                                    "If a cycle exists, distance between them decreases by 1 each iteration, guaranteeing meeting in O(N) time."
                                ),
                            }
                        ],
                    },
                    {
                        "slug": "dsa-trees-bst",
                        "name": "Trees & Binary Search Trees",
                        "description": "Hierarchical structures, BFS level-order, DFS traversals, and BST properties.",
                        "learning_objectives": "Implement tree depth calculations, lowest common ancestor, and BST validations.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 200,
                        "display_order": 3,
                        "dsa_topic_slug": "trees-bst-heaps",
                        "subtopics": [
                            {"name": "DFS Recursive Traversals", "description": "Pre-order, in-order, post-order invariants"},
                            {"name": "BFS Level-Order Traversals", "description": "Queue-based breadth first expansion"},
                            {"name": "BST Search & Insertion", "description": "Logarithmic search invariants and validation"},
                        ],
                        "resources": [
                            {
                                "title": "Tree Traversals & Recursive Invariants",
                                "description": "Complete guide to binary tree recursive properties and iterative conversions.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": (
                                    "# Binary Tree Traversals\n\n"
                                    "- **Inorder (Left, Root, Right)**: Yields sorted sequence for BSTs.\n"
                                    "- **Preorder (Root, Left, Right)**: Useful for serialization.\n"
                                    "- **Postorder (Left, Right, Root)**: Ideal for subtree deletion and bottom-up metric propagation."
                                ),
                            }
                        ],
                    },
                    {
                        "slug": "dsa-dynamic-programming",
                        "name": "Dynamic Programming",
                        "description": "Optimal substructure, overlapping subproblems, memoization, and bottom-up tabulation.",
                        "learning_objectives": "Formulate 1D and 2D state transition equations and optimize space complexity.",
                        "difficulty": "ADVANCED",
                        "estimated_minutes": 240,
                        "display_order": 4,
                        "dsa_topic_slug": "dynamic-programming",
                        "subtopics": [
                            {"name": "Memoization (Top-Down)", "description": "Recursive state caching"},
                            {"name": "Tabulation (Bottom-Up)", "description": "Iterative table computation and space optimization"},
                            {"name": "0/1 Knapsack & Subset Sum", "description": "Standard combinatorial DP models"},
                        ],
                        "resources": [
                            {
                                "title": "Dynamic Programming: State Formulation Guide",
                                "description": "How to identify recurrence relations and boundary conditions in interview problems.",
                                "resource_type": "ARTICLE",
                                "difficulty": "HARD",
                                "estimated_duration_min": 40,
                                "content": (
                                    "# Dynamic Programming Mastery\n\n"
                                    "1. **Define State**: What parameters uniquely describe a subproblem? (e.g. `dp[i]` = max profit up to index `i`).\n"
                                    "2. **Find Transition**: How does state `i` depend on previous states?\n"
                                    "3. **Identify Base Cases**: Smallest valid states (e.g. `dp[0] = 0`).\n"
                                    "4. **Compute Order**: Ensure prerequisites are computed before current state."
                                ),
                            }
                        ],
                    },
                ],
            },
            {
                "code": "CORE_CS",
                "name": "Core Computer Science Fundamentals",
                "description": "Operating systems, relational databases, computer networks, and system design essentials.",
                "icon": "Cpu",
                "display_order": 3,
                "topics": [
                    {
                        "slug": "core-dbms-sql",
                        "name": "DBMS, SQL & Indexing",
                        "description": "ACID properties, transactions, normalization, indexing structures, and complex SQL joins.",
                        "learning_objectives": "Analyze query execution plans, design normalized schemas, and ensure transactional consistency.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 150,
                        "display_order": 1,
                        "subtopics": [
                            {"name": "ACID Properties & Concurrency", "description": "Atomicity, Consistency, Isolation, Durability"},
                            {"name": "B-Tree Indexes & Query Optimization", "description": "Clustered vs non-clustered indexes, scan vs seek"},
                        ],
                        "resources": [
                            {
                                "title": "Database Internals: Storage Engines & Indexing",
                                "description": "How relational database engines execute joins and utilize B+ Trees for O(log N) searches.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": (
                                    "# Database Internals & Query Optimization\n\n"
                                    "### Why B+ Trees?\n"
                                    "B+ Trees maximize fan-out, reducing disk I/O operations by storing data records strictly in leaf nodes while keeping internal nodes lightweight for fast branching."
                                ),
                            }
                        ],
                    },
                    {
                        "slug": "core-os",
                        "name": "Operating Systems & Concurrency",
                        "description": "Processes, threads, CPU scheduling algorithms, virtual memory, paging, and deadlocks.",
                        "learning_objectives": "Evaluate synchronization primitives, prevent deadlocks, and calculate paging address translations.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 150,
                        "display_order": 2,
                        "subtopics": [
                            {"name": "Process Scheduling & Synchronization", "description": "Mutexes, semaphores, critical section problems"},
                            {"name": "Virtual Memory & Page Replacement", "description": "TLB, demand paging, FIFO, LRU, Optimal algorithms"},
                        ],
                        "resources": [
                            {
                                "title": "Operating Systems: Concurrency, Deadlocks & Virtual Memory",
                                "description": "Core concepts in synchronization, Coffman's deadlock conditions, and page replacement.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": (
                                    "# OS Concurrency & Deadlocks\n\n"
                                    "### Coffman's 4 Conditions for Deadlock\n"
                                    "1. Mutual Exclusion\n"
                                    "2. Hold and Wait\n"
                                    "3. No Preemption\n"
                                    "4. Circular Wait\n"
                                    "Breaking any ONE condition guarantees prevention of deadlock."
                                ),
                            }
                        ],
                    },
                ],
            },
            {
                "code": "APTITUDE",
                "name": "Quantitative Aptitude & Placement Drills",
                "description": "Percentages, ratios, time and work, speed, distance, probability, and permutations.",
                "icon": "Calculator",
                "display_order": 4,
                "topics": [
                    {
                        "slug": "quant-percentages-ratios",
                        "name": "Percentages, Ratios & Commercial Math",
                        "description": "Fraction-to-percentage conversions, profit and loss, compound interest, and mixture problems.",
                        "learning_objectives": "Solve commercial mathematics problems in under 60 seconds using mental math shortcuts.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 120,
                        "display_order": 1,
                        "subtopics": [
                            {"name": "Percentage Fractional Equivalents", "description": "Speed calculation tricks for 1/2 to 1/16"},
                            {"name": "Successive Percentage Changes", "description": "Formula: A + B + (AB / 100)"},
                        ],
                        "resources": [
                            {
                                "title": "Speed Math Shortcuts for Quantitative Aptitude",
                                "description": "Fast mental arithmetic formulas for campus recruitment assessments.",
                                "resource_type": "ARTICLE",
                                "difficulty": "EASY",
                                "estimated_duration_min": 20,
                                "content": (
                                    "# Quantitative Aptitude Speed Formulas\n\n"
                                    "### Successive Percentage Formula\n"
                                    "Net Change = A + B + (A * B) / 100\n\n"
                                    "### Common Fractions\n"
                                    "- 1/6 = 16.66%\n"
                                    "- 1/7 = 14.28%\n"
                                    "- 1/8 = 12.5%\n"
                                    "- 1/9 = 11.11%\n"
                                    "- 1/11 = 9.09%"
                                ),
                            }
                        ],
                    },
                    {
                        "slug": "quant-time-work-speed",
                        "name": "Time, Work, Speed & Distance",
                        "description": "Efficiency method for time and work, pipe and cisterns, relative speed, and trains.",
                        "learning_objectives": "Formulate LCM work units and relative speed equations for aptitude exams.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 150,
                        "display_order": 2,
                        "subtopics": [
                            {"name": "LCM Method for Work", "description": "Convert days to total units of work"},
                            {"name": "Relative Speed for Moving Objects", "description": "Opposite directions: S1 + S2, Same direction: S1 - S2"},
                        ],
                        "resources": [
                            {
                                "title": "The LCM Unit Method for Time & Work",
                                "description": "Solving work and pipe problems cleanly without handling complex fractions.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 20,
                                "content": (
                                    "# The Unit Work Technique\n\n"
                                    "If A completes work in 10 days and B in 15 days:\n"
                                    "1. Let Total Work = LCM(10, 15) = 30 units.\n"
                                    "2. Efficiency of A = 3 units/day.\n"
                                    "3. Efficiency of B = 2 units/day.\n"
                                    "4. Combined Efficiency = 5 units/day.\n"
                                    "5. Days required = 30 / 5 = 6 days."
                                ),
                            }
                        ],
                    },
                ],
            },
        ]

        # Insert subjects, topics, subtopics, and learning resources
        for s_idx, subj_spec in enumerate(subjects_data, start=1):
            subj = (
                db.query(RoadmapSubject)
                .filter(RoadmapSubject.career_path_id == sde_path.id, RoadmapSubject.code == subj_spec["code"])
                .first()
            )
            if not subj:
                subj = RoadmapSubject(
                    career_path_id=sde_path.id,
                    code=subj_spec["code"],
                    name=subj_spec["name"],
                    description=subj_spec["description"],
                    icon=subj_spec["icon"],
                    display_order=subj_spec["display_order"],
                )
                db.add(subj)
                db.flush()
                print(f"Created Subject: {subj.name}")

            for t_idx, topic_spec in enumerate(subj_spec["topics"], start=1):
                dsa_t_id = dsa_topics.get(topic_spec.get("dsa_topic_slug"))
                topic = (
                    db.query(RoadmapTopic)
                    .filter(RoadmapTopic.subject_id == subj.id, RoadmapTopic.slug == topic_spec["slug"])
                    .first()
                )
                if not topic:
                    topic = RoadmapTopic(
                        subject_id=subj.id,
                        slug=topic_spec["slug"],
                        name=topic_spec["name"],
                        description=topic_spec["description"],
                        learning_objectives=topic_spec["learning_objectives"],
                        difficulty=topic_spec["difficulty"],
                        estimated_minutes=topic_spec["estimated_minutes"],
                        display_order=topic_spec["display_order"],
                        dsa_topic_id=dsa_t_id,
                    )
                    db.add(topic)
                    db.flush()
                    print(f"  Created Topic: {topic.name}")

                    for st_spec in topic_spec.get("subtopics", []):
                        subtopic = RoadmapSubtopic(
                            topic_id=topic.id,
                            name=st_spec["name"],
                            description=st_spec["description"],
                            display_order=0,
                        )
                        db.add(subtopic)

                    for res_spec in topic_spec.get("resources", []):
                        resource = LearningResource(
                            topic_id=topic.id,
                            title=res_spec["title"],
                            description=res_spec["description"],
                            resource_type=res_spec["resource_type"],
                            content=res_spec["content"],
                            difficulty=res_spec["difficulty"],
                            estimated_duration_min=res_spec["estimated_duration_min"],
                            status="PUBLISHED",
                        )
                        db.add(resource)

        db.commit()
        print("Career Path and Preparation Roadmaps successfully seeded!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding roadmap: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_roadmaps()
