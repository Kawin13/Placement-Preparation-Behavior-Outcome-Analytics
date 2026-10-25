"""
Ingestion script for authentic question banks and practice assessments:
- Quantitative Aptitude
- Logical Reasoning
- Verbal Ability
All questions include verified mathematical/logical steps, distractor rationales, and proper skill links.
"""

from app.core.database import SessionLocal
from app.models.institution import Institution
from app.models.skill import Skill
from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentQuestion

def seed_practice_banks():
    db = SessionLocal()
    try:
        inst = db.query(Institution).filter(Institution.code == "AIET").first()
        if not inst:
            print("Creating default accredited institution AIET for development seed data...")
            inst = Institution(
                name="Apex Institute of Engineering & Technology",
                code="AIET",
                is_active=True,
            )
            db.add(inst)
            db.flush()

        print("Ingesting Skills hierarchy...")
        # 1. Skills
        skill_quant = db.query(Skill).filter(Skill.domain == "QUANT", Skill.name == "Arithmetic & Algebra").first()
        if not skill_quant:
            skill_quant = Skill(
                name="Arithmetic & Algebra",
                domain="QUANT",
                description="Time-work, ratios, percentages, numbers, and basic algebra.",
            )
            db.add(skill_quant)
            db.flush()

        skill_logical = db.query(Skill).filter(Skill.domain == "LOGICAL", Skill.name == "Deduction & Arrangements").first()
        if not skill_logical:
            skill_logical = Skill(
                name="Deduction & Arrangements",
                domain="LOGICAL",
                description="Syllogisms, seating arrangements, and logical deductions.",
            )
            db.add(skill_logical)
            db.flush()

        skill_verbal = db.query(Skill).filter(Skill.domain == "VERBAL", Skill.name == "Comprehension & Syntax").first()
        if not skill_verbal:
            skill_verbal = Skill(
                name="Comprehension & Syntax",
                domain="VERBAL",
                description="Sentence correction, inference, vocabulary, and para jumbles.",
            )
            db.add(skill_verbal)
            db.flush()

        skill_prog = db.query(Skill).filter(Skill.domain == "PROGRAMMING", Skill.name == "Algorithms & Data Structures").first()
        if not skill_prog:
            skill_prog = Skill(
                name="Algorithms & Data Structures",
                domain="PROGRAMMING",
                description="Time complexity, recursion, dynamic programming, stacks, queues, and tree structures.",
            )
            db.add(skill_prog)
            db.flush()

        skill_sql = db.query(Skill).filter(Skill.domain == "SQL", Skill.name == "Relational Queries & SQL").first()
        if not skill_sql:
            skill_sql = Skill(
                name="Relational Queries & SQL",
                domain="SQL",
                description="Relational schema, aggregations, anti-joins, window functions, and set operations.",
            )
            db.add(skill_sql)
            db.flush()

        # -------------------------------------------------------------
        # Curated Questions: Quantitative Aptitude
        # -------------------------------------------------------------
        quant_questions_data = [
            {
                "title": "Time and Work: Combined Efficiency",
                "content": "A can complete a piece of work in 12 days, and B can complete the same work in 18 days. If they work together for 4 days, what fraction of the total work remains to be completed?",
                "difficulty": "MEDIUM",
                "explanation": "Step 1: Total work = LCM(12, 18) = 36 units.\nStep 2: A's efficiency = 36 / 12 = 3 units/day; B's efficiency = 36 / 18 = 2 units/day.\nStep 3: Combined efficiency = 3 + 2 = 5 units/day.\nStep 4: In 4 days, work completed = 5 * 4 = 20 units.\nStep 5: Remaining work = 36 - 20 = 16 units.\nStep 6: Fraction remaining = 16 / 36 = 4 / 9.",
                "options": [
                    {"text": "4/9", "is_correct": True, "feedback": "Correct. Total units = 36; combined rate = 5 units/day; remaining = 16/36 = 4/9."},
                    {"text": "5/9", "is_correct": False, "feedback": "Incorrect. 5/9 represents the completed portion (20/36), not the remaining fraction."},
                    {"text": "1/3", "is_correct": False, "feedback": "Incorrect. 1/3 would correspond to 12 remaining units instead of 16."},
                    {"text": "2/5", "is_correct": False, "feedback": "Incorrect. 2/5 assumes an incorrect total units model."},
                ],
            },
            {
                "title": "Percentage and Profit Calculation",
                "content": "A retailer marks an article 30% above its cost price and offers a 10% cash discount. If the retailer makes a profit of Rs. 170, what was the original cost price of the article?",
                "difficulty": "MEDIUM",
                "explanation": "Step 1: Let Cost Price (CP) = 100x.\nStep 2: Marked Price (MP) = 100x * 1.30 = 130x.\nStep 3: Selling Price (SP) = 130x * (1 - 0.10) = 117x.\nStep 4: Profit = SP - CP = 117x - 100x = 17x.\nStep 5: 17x = 170 => x = 10.\nStep 6: CP = 100x = 100 * 10 = Rs. 1,000.",
                "options": [
                    {"text": "Rs. 1,000", "is_correct": True, "feedback": "Correct. Profit is 17% of CP, which yields CP = 170 / 0.17 = 1,000."},
                    {"text": "Rs. 1,200", "is_correct": False, "feedback": "Incorrect. 17% profit on 1,200 would equal 204, not 170."},
                    {"text": "Rs. 850", "is_correct": False, "feedback": "Incorrect. Does not account for the compounding marked up price."},
                    {"text": "Rs. 1,150", "is_correct": False, "feedback": "Incorrect. Calculation omitted the discount from marked price."},
                ],
            },
            {
                "title": "Speed, Distance, and Relative Motion",
                "content": "Two trains 140 m and 160 m long are running towards each other on parallel tracks at 60 km/h and 48 km/h respectively. How many seconds will they take to completely cross each other?",
                "difficulty": "EASY",
                "explanation": "Step 1: Total distance to cover = Sum of lengths = 140 + 160 = 300 m.\nStep 2: Opposite direction => Relative speed = 60 + 48 = 108 km/h.\nStep 3: Convert speed to m/s: 108 * (5/18) = 6 * 5 = 30 m/s.\nStep 4: Time taken = Distance / Speed = 300 / 30 = 10 seconds.",
                "options": [
                    {"text": "10 seconds", "is_correct": True, "feedback": "Correct. Distance = 300m, Relative Speed = 30 m/s => 300 / 30 = 10s."},
                    {"text": "12 seconds", "is_correct": False, "feedback": "Incorrect. Corresponds to 25 m/s, which miscalculates speed conversion."},
                    {"text": "8 seconds", "is_correct": False, "feedback": "Incorrect. Underestimates crossing time."},
                    {"text": "15 seconds", "is_correct": False, "feedback": "Incorrect. Assumed same direction relative speed."},
                ],
            },
            {
                "title": "Ratio and Mixtures",
                "content": "A vessel contains 60 litres of milk and water in the ratio 3:1. How much water must be added so that the ratio of milk to water becomes 1:1?",
                "difficulty": "EASY",
                "explanation": "Step 1: Total volume = 60 litres in 3:1 ratio => Milk = (3/4)*60 = 45 litres, Water = (1/4)*60 = 15 litres.\nStep 2: To make ratio 1:1, quantity of water must equal milk = 45 litres.\nStep 3: Water to add = 45 - 15 = 30 litres.",
                "options": [
                    {"text": "30 litres", "is_correct": True, "feedback": "Correct. Initial water = 15L, initial milk = 45L. Adding 30L makes both 45L."},
                    {"text": "20 litres", "is_correct": False, "feedback": "Incorrect. Adding 20L results in 35L water, ratio 45:35 != 1:1."},
                    {"text": "15 litres", "is_correct": False, "feedback": "Incorrect. 15L was the initial volume of water."},
                    {"text": "25 litres", "is_correct": False, "feedback": "Incorrect. Leaves milk:water at 45:40."},
                ],
            },
            {
                "title": "Number Systems: Remainder Theorem",
                "content": "What is the remainder when (7^101 + 5) is divided by 8?",
                "difficulty": "HARD",
                "explanation": "Step 1: 7 mod 8 = -1.\nStep 2: 7^101 mod 8 = (-1)^101 mod 8 = -1 mod 8.\nStep 3: Therefore, (7^101 + 5) mod 8 = (-1 + 5) mod 8 = 4 mod 8.\nStep 4: The remainder is 4.",
                "options": [
                    {"text": "4", "is_correct": True, "feedback": "Correct. Using modular arithmetic: (-1)^101 + 5 = -1 + 5 = 4."},
                    {"text": "6", "is_correct": False, "feedback": "Incorrect. (-1)^101 evaluates to -1, not +1."},
                    {"text": "2", "is_correct": False, "feedback": "Incorrect. Miscalculated residue."},
                    {"text": "0", "is_correct": False, "feedback": "Incorrect. The term is not divisible by 8."},
                ],
            },
        ]

        # -------------------------------------------------------------
        # Curated Questions: Logical Reasoning
        # -------------------------------------------------------------
        logical_questions_data = [
            {
                "title": "Syllogism: Universal and Particular Statements",
                "content": "Statements:\n1. All engineers are innovators.\n2. Some innovators are entrepreneurs.\nConclusions:\nI. Some engineers are entrepreneurs.\nII. Some innovators are engineers.",
                "difficulty": "MEDIUM",
                "explanation": "Step 1: From Statement 1 (All engineers are innovators), the converse 'Some innovators are engineers' is always valid by immediate conversion. Hence Conclusion II follows.\nStep 2: In Statement 2, 'Some innovators are entrepreneurs' has an undistributed middle term between engineers and entrepreneurs. We cannot conclude that some engineers are entrepreneurs. Hence Conclusion I does not necessarily follow.\nTherefore, only Conclusion II follows.",
                "options": [
                    {"text": "Only Conclusion II follows", "is_correct": True, "feedback": "Correct. Immediate conversion of 'All A are B' yields 'Some B are A'. Undistributed middle prevents Conclusion I."},
                    {"text": "Only Conclusion I follows", "is_correct": False, "feedback": "Incorrect. There is no direct chain between engineers and entrepreneurs."},
                    {"text": "Both Conclusions I and II follow", "is_correct": False, "feedback": "Incorrect. Syllogism rules require distributed middle term to link subjects."},
                    {"text": "Neither Conclusion follows", "is_correct": False, "feedback": "Incorrect. Conclusion II is an unconditionally valid converse."},
                ],
            },
            {
                "title": "Circular Seating Arrangement",
                "content": "Six friends (P, Q, R, S, T, U) are sitting around a circular table facing the centre. P is between Q and R. S is to the immediate left of U. T is to the immediate right of R. Who is sitting opposite to P?",
                "difficulty": "HARD",
                "explanation": "Step 1: Arrange around circular table clockwise. Let R be at 12 o'clock.\nStep 2: T is immediate right of R (facing center, right is anti-clockwise, so T is at 10 o'clock).\nStep 3: P is between Q and R, so P is at 2 o'clock and Q is at 4 o'clock.\nStep 4: Remaining spots are 6 o'clock and 8 o'clock. S is immediate left of U, so U is at 8 o'clock and S is at 6 o'clock.\nStep 5: Opposite to P (at 2 o'clock) is the position at 8 o'clock, which is occupied by U.",
                "options": [
                    {"text": "U", "is_correct": True, "feedback": "Correct. Based on the position matrix, U sits directly opposite P."},
                    {"text": "S", "is_correct": False, "feedback": "Incorrect. S sits opposite to R."},
                    {"text": "T", "is_correct": False, "feedback": "Incorrect. T sits opposite to Q."},
                    {"text": "Q", "is_correct": False, "feedback": "Incorrect. Q is adjacent to P."},
                ],
            },
            {
                "title": "Coding-Decoding: Pattern Shift",
                "content": "In a certain code language, if 'SYSTEM' is coded as 'SYSMET' and 'NEARER' is coded as 'AENRER', how will 'FRACTION' be coded?",
                "difficulty": "EASY",
                "explanation": "Step 1: Observe rule: The word is divided into two equal halves. Each half is reversed independently.\nStep 2: 'FRACTION' has 8 letters: First half 'FRAC', Second half 'TION'.\nStep 3: Reverse 'FRAC' => 'CARF'.\nStep 4: Reverse 'TION' => 'NOIT'.\nStep 5: Combined = 'CARFNOIT'.",
                "options": [
                    {"text": "CARFNOIT", "is_correct": True, "feedback": "Correct. Splitting in half and reversing each yields CARF + NOIT = CARFNOIT."},
                    {"text": "CARFNOTI", "is_correct": False, "feedback": "Incorrect. Last two letters are improperly ordered."},
                    {"text": "CRAFNION", "is_correct": False, "feedback": "Incorrect. Does not follow strict reflection symmetry."},
                    {"text": "FRACNOIT", "is_correct": False, "feedback": "Incorrect. Only reversed the second half."},
                ],
            },
            {
                "title": "Blood Relations: Indirect Statement",
                "content": "Pointing to a photograph, Rohit said, 'She is the daughter of the only son of my grandfather.' How is Rohit related to the girl in the photograph?",
                "difficulty": "EASY",
                "explanation": "Step 1: 'My grandfather's only son' = Rohit's father.\nStep 2: 'Daughter of Rohit's father' = Rohit's sister.\nStep 3: Therefore, Rohit is the brother of the girl in the photograph.",
                "options": [
                    {"text": "Brother", "is_correct": True, "feedback": "Correct. Grandfather's only son is father; father's daughter is sister, making Rohit her brother."},
                    {"text": "Cousin", "is_correct": False, "feedback": "Incorrect. The problem explicitly specifies 'only son', precluding uncles."},
                    {"text": "Uncle", "is_correct": False, "feedback": "Incorrect. Generational rank is identical."},
                    {"text": "Father", "is_correct": False, "feedback": "Incorrect. Generation leap does not match the statement."},
                ],
            },
            {
                "title": "Logical Sequence & Number Series",
                "content": "Identify the missing number in the following sequence: 4, 18, 48, 100, 180, ?",
                "difficulty": "MEDIUM",
                "explanation": "Step 1: Check pattern based on cubes and squares: n^3 - n^2.\nFor n=2: 2^3 - 2^2 = 8 - 4 = 4.\nFor n=3: 3^3 - 3^2 = 27 - 9 = 18.\nFor n=4: 4^3 - 4^2 = 64 - 16 = 48.\nFor n=5: 5^3 - 5^2 = 125 - 25 = 100.\nFor n=6: 6^3 - 6^2 = 216 - 36 = 180.\nStep 2: For n=7: 7^3 - 7^2 = 343 - 49 = 294.",
                "options": [
                    {"text": "294", "is_correct": True, "feedback": "Correct. Follows polynomial pattern n^3 - n^2 for n=7 (343 - 49 = 294)."},
                    {"text": "280", "is_correct": False, "feedback": "Incorrect. Arithmetic progression difference does not fit."},
                    {"text": "310", "is_correct": False, "feedback": "Incorrect. Overestimates second derivative growth."},
                    {"text": "256", "is_correct": False, "feedback": "Incorrect. 256 is 4^4, not part of the n^3 - n^2 series."},
                ],
            },
        ]

        # -------------------------------------------------------------
        # Curated Questions: Verbal Ability
        # -------------------------------------------------------------
        verbal_questions_data = [
            {
                "title": "Sentence Correction: Subject-Verb Agreement",
                "content": "Choose the grammatically correct option to replace the underlined phrase:\n'Neither the placement officer nor the candidates was aware of the change in schedule.'",
                "difficulty": "EASY",
                "explanation": "Rule: When subjects are connected by 'neither... nor', the verb agrees in number with the subject closer to it. 'The candidates' is plural and is closest to the verb, so the plural verb 'were' is required.",
                "options": [
                    {"text": "were aware of the change in schedule", "is_correct": True, "feedback": "Correct. Proximity rule: 'candidates' is plural, requiring 'were'."},
                    {"text": "was aware of the change in schedule", "is_correct": False, "feedback": "Incorrect. Violates the proximity agreement rule."},
                    {"text": "are aware on the change in schedule", "is_correct": False, "feedback": "Incorrect. Preposition 'on' is unidiomatic."},
                    {"text": "were being aware of the change in schedule", "is_correct": False, "feedback": "Incorrect. Stative verb 'aware' does not take progressive aspect."},
                ],
            },
            {
                "title": "Contextual Vocabulary: Precision",
                "content": "Select the word that best completes the sentence:\n'The executive committee's decision to dissolve the unperforming branch was __________, taking into account exhaustive financial audits.'",
                "difficulty": "MEDIUM",
                "explanation": "'Judicious' means having, showing, or done with good judgment or sense, fitting the context of extensive auditing. 'Arbitrary' is opposite (random); 'spurious' means counterfeit; 'tentative' means uncertain.",
                "options": [
                    {"text": "Judicious", "is_correct": True, "feedback": "Correct. 'Judicious' indicates prudent, well-considered decision based on audit evidence."},
                    {"text": "Arbitrary", "is_correct": False, "feedback": "Incorrect. Arbitrary implies capricious decision without basis."},
                    {"text": "Spurious", "is_correct": False, "feedback": "Incorrect. Spurious means false or illegitimate."},
                    {"text": "Tentative", "is_correct": False, "feedback": "Incorrect. Context describes a finalized, well-audited resolution."},
                ],
            },
            {
                "title": "Critical Reasoning: Assumption Identification",
                "content": "Premise: 'Institutions that mandate daily algorithmic problem-solving achieve a 35% higher interview conversion rate for technical roles.'\nWhich of the following is an underlying assumption required by the argument?",
                "difficulty": "HARD",
                "explanation": "The conclusion attributes higher interview conversion to the daily algorithmic practice. For this causal inference to hold, it assumes that the candidates participating in the mandatory practice did not already possess superior programming proficiency prior to the mandate.",
                "options": [
                    {"text": "The higher conversion rate is not merely the result of initially enrolling pre-qualified students.", "is_correct": True, "feedback": "Correct. Negation test: if practice cohorts simply had higher initial ability, the mandate itself wasn't the causal factor."},
                    {"text": "All tech companies ask exclusively algorithmic questions during on-campus interviews.", "is_correct": False, "feedback": "Incorrect. Extreme statement; not required for the general correlation to hold."},
                    {"text": "Students who solve problems independently never pass technical interviews.", "is_correct": False, "feedback": "Incorrect. Outside the logical scope of the institutional policy comparison."},
                    {"text": "Interviewers are informed in advance whether candidates completed daily problem sets.", "is_correct": False, "feedback": "Incorrect. Irrelevant to whether the skill improvement drove conversion."},
                ],
            },
            {
                "title": "Para Jumbles: Logical Coherence",
                "content": "Arrange the following sentences in a logically coherent paragraph:\nP. This latency reduction directly decreases abandoned checkout operations.\nQ. Cloud-native databases now replicate partition states within microseconds.\nR. Consequently, high-frequency e-commerce platforms can guarantee atomic consistency.\nS. In competitive consumer retail, responsive transactions remain the primary retention driver.",
                "difficulty": "MEDIUM",
                "explanation": "Opening statement: S establishes the general premise of consumer retail and responsiveness. Q introduces the technical breakthrough (cloud-native database microsecond replication). R follows with the consequence for e-commerce. P concludes by linking the latency reduction back to abandoned checkouts.",
                "options": [
                    {"text": "S - Q - R - P", "is_correct": True, "feedback": "Correct. S introduces the problem domain, Q introduces technology, R states architectural consequence, P concludes with operational impact."},
                    {"text": "Q - R - P - S", "is_correct": False, "feedback": "Incorrect. Leaves the overarching theme disconnected at the end."},
                    {"text": "P - S - Q - R", "is_correct": False, "feedback": "Incorrect. Pronoun 'This' in P lacks antecedent."},
                    {"text": "S - P - Q - R", "is_correct": False, "feedback": "Incorrect. P cannot precede the description of latency reduction in Q."},
                ],
            },
            {
                "title": "Reading Comprehension: Tone & Purpose",
                "content": "Passage: 'While proponents argue that automated resume filtering accelerates recruitment throughput, empirical studies reveal systematic exclusion of non-traditional candidates whose credentials deviate from standard keyword taxonomies.'\nWhat is the author's primary attitude towards current automated resume filtering?",
                "difficulty": "EASY",
                "explanation": "The author contrasts proponents' throughput claims with empirical exclusion evidence, displaying a critical and cautionary perspective.",
                "options": [
                    {"text": "Critical and cautionary", "is_correct": True, "feedback": "Correct. The author highlights empirical shortcomings and systematic biases."},
                    {"text": "Unreservedly enthusiastic", "is_correct": False, "feedback": "Incorrect. Directly contradicted by the empirical exclusion findings."},
                    {"text": "Indifferent and detached", "is_correct": False, "feedback": "Incorrect. The focus on systematic exclusion demonstrates active critique."},
                    {"text": "Nostalgic and dismissive", "is_correct": False, "feedback": "Incorrect. The author does not invoke nostalgia for legacy methods."},
                ],
            },
        ]

        # -------------------------------------------------------------
        # Curated Questions: Programming & Data Structures
        # -------------------------------------------------------------
        prog_questions_data = [
            {
                "title": "Time Complexity: Recursive Divide-and-Conquer",
                "content": "Given the recurrence relation T(n) = 2T(n/2) + O(n), what is the asymptotic worst-case time complexity by the Master Theorem?",
                "difficulty": "MEDIUM",
                "explanation": "By Case 2 of the Master Theorem: a=2, b=2, log_b(a) = log_2(2) = 1. Since f(n) = Theta(n^1), T(n) = Theta(n log n).",
                "options": [
                    {"text": "O(n log n)", "is_correct": True, "feedback": "Correct. Matches Master Theorem Case 2 where f(n) = Theta(n^(log_b a))."},
                    {"text": "O(n^2)", "is_correct": False, "feedback": "Incorrect. O(n^2) would apply if work per step was quadratic."},
                    {"text": "O(n)", "is_correct": False, "feedback": "Incorrect. O(n) would apply if a < b (e.g., T(n/2) + O(n))."},
                    {"text": "O(log n)", "is_correct": False, "feedback": "Incorrect. Fails to account for O(n) merge work across levels."},
                ],
            },
            {
                "title": "Data Structures: Minimum Stack Operations",
                "content": "What is the optimal time and auxiliary space complexity to implement a Stack supporting push(), pop(), and getMin() operations?",
                "difficulty": "EASY",
                "explanation": "Using an auxiliary stack or value encoding (2x - min), all three operations (push, pop, getMin) can be executed in O(1) worst-case time with O(n) auxiliary space.",
                "options": [
                    {"text": "O(1) time and O(n) space", "is_correct": True, "feedback": "Correct. Auxiliary stack or difference tracking achieves O(1) time across all operations with linear space."},
                    {"text": "O(log n) time and O(1) space", "is_correct": False, "feedback": "Incorrect. Logarithmic time is unnecessary and space cannot be O(1) without bounds."},
                    {"text": "O(n) time and O(1) space", "is_correct": False, "feedback": "Incorrect. O(n) getMin() defeats the purpose of an optimized min-stack."},
                    {"text": "O(1) time and O(1) space", "is_correct": False, "feedback": "Incorrect. Storing n elements requires at least O(n) total space."},
                ],
            },
            {
                "title": "Binary Search Tree: Inorder Traversal Property",
                "content": "Performing an Inorder traversal (Left, Root, Right) on any valid Binary Search Tree (BST) without duplicate keys yields:",
                "difficulty": "EASY",
                "explanation": "In a BST, all keys in the left subtree are strictly less than the root, and all keys in the right subtree are strictly greater. Inorder traversal visits left, root, right, producing keys in strictly ascending sorted order.",
                "options": [
                    {"text": "Keys in strictly ascending sorted order", "is_correct": True, "feedback": "Correct. By BST invariant, Left < Root < Right yields sorted non-decreasing sequence."},
                    {"text": "Keys in level-order breadth-first order", "is_correct": False, "feedback": "Incorrect. Level-order requires a queue, not an inorder DFS traversal."},
                    {"text": "Keys in reverse topological order", "is_correct": False, "feedback": "Incorrect. Reversed order corresponds to Right-Root-Left traversal."},
                    {"text": "Keys grouped by subtree height", "is_correct": False, "feedback": "Incorrect. Inorder traversal is independent of node height."},
                ],
            },
            {
                "title": "Graph Theory: Cycle Detection in Directed Graphs",
                "content": "Which algorithmic approach detects cycles in a directed graph in linear O(V + E) time?",
                "difficulty": "MEDIUM",
                "explanation": "Depth-First Search (DFS) with a 3-color vertex marking scheme (White = unvisited, Gray = visiting / on recursion stack, Black = completely visited). Detecting a Gray vertex during traversal indicates a back-edge and hence a directed cycle.",
                "options": [
                    {"text": "DFS with recursion stack (3-color back-edge detection)", "is_correct": True, "feedback": "Correct. A back-edge to an active vertex on the recursion stack proves a cycle in O(V + E)."},
                    {"text": "Dijkstra's Shortest Path Algorithm", "is_correct": False, "feedback": "Incorrect. Dijkstra finds shortest paths and does not directly classify cycle back-edges."},
                    {"text": "Kruskal's Disjoint Set Union without path compression", "is_correct": False, "feedback": "Incorrect. Kruskal applies to undirected minimum spanning trees."},
                    {"text": "Prim's Minimum Spanning Tree traversal", "is_correct": False, "feedback": "Incorrect. Prim builds undirected trees, not directed cycle classification."},
                ],
            },
            {
                "title": "Dynamic Programming: 0/1 Knapsack Subproblem State",
                "content": "In the standard bottom-up dynamic programming table dp[i][w] for the 0/1 Knapsack problem with n items and capacity W, what does dp[i][w] represent?",
                "difficulty": "HARD",
                "explanation": "Step 1: In 0/1 Knapsack, dp[i][w] denotes the maximum value achievable considering a subset of the first i items with total weight at most w.\nStep 2: State transition: dp[i][w] = max(dp[i-1][w], val[i] + dp[i-1][w - wt[i]]) if wt[i] <= w.",
                "options": [
                    {"text": "Maximum value obtainable considering the first i items with weight limit w", "is_correct": True, "feedback": "Correct. Represents optimal value bounded by subset prefix i and current capacity w."},
                    {"text": "Minimum weight required to obtain value exactly w using i items", "is_correct": False, "feedback": "Incorrect. That defines the dual unbounded problem, not standard knapsack."},
                    {"text": "Total number of combinations to fill exactly capacity w", "is_correct": False, "feedback": "Incorrect. Counting combinations corresponds to coin change combination counting."},
                    {"text": "Optimal profit ratio of remaining unassigned items", "is_correct": False, "feedback": "Incorrect. DP state tracks scalar total value, not fractional ratios."},
                ],
            },
        ]

        # -------------------------------------------------------------
        # Curated Questions: Relational Queries & SQL
        # -------------------------------------------------------------
        sql_questions_data = [
            {
                "title": "SQL Anti-Join: Identifying Unmatched Records",
                "content": "To retrieve all employees from the employees table who have never been assigned any projects in the project_assignments table, which SQL pattern is standard and optimal?",
                "difficulty": "MEDIUM",
                "explanation": "A LEFT JOIN from employees to project_assignments on employee_id, coupled with a WHERE project_assignments.employee_id IS NULL clause, efficiently identifies unassigned records (anti-join pattern).",
                "options": [
                    {"text": "LEFT JOIN on employee_id WHERE project_assignments.employee_id IS NULL", "is_correct": True, "feedback": "Correct. Preserves all employees and filters for unmatched NULL foreign keys."},
                    {"text": "INNER JOIN on employee_id WHERE project_assignments.project_id = 0", "is_correct": False, "feedback": "Incorrect. Unassigned employees have no corresponding rows, so inner join eliminates them."},
                    {"text": "CROSS JOIN on employee_id GROUP BY project_id HAVING COUNT(*) = 0", "is_correct": False, "feedback": "Incorrect. Cross joins generate cartesian products and cannot filter unassigned keys."},
                    {"text": "FULL OUTER JOIN on employee_id WHERE employees.employee_id IS NULL", "is_correct": False, "feedback": "Incorrect. This filters for missing employees instead of missing assignments."},
                ],
            },
            {
                "title": "Aggregations: WHERE vs HAVING Clause",
                "content": "In SQL, what is the fundamental functional difference between the WHERE clause and the HAVING clause?",
                "difficulty": "EASY",
                "explanation": "The WHERE clause filters rows before aggregation occurs, whereas the HAVING clause filters aggregated group results produced by GROUP BY.",
                "options": [
                    {"text": "WHERE filters raw rows prior to aggregation; HAVING filters aggregated groups", "is_correct": True, "feedback": "Correct. WHERE operates on individual tuples; HAVING evaluates aggregate functions like COUNT/AVG."},
                    {"text": "WHERE applies only to subqueries; HAVING applies only to joins", "is_correct": False, "feedback": "Incorrect. Both can be applied across joined or subquery result sets."},
                    {"text": "WHERE cannot contain comparison operators; HAVING requires regex", "is_correct": False, "feedback": "Incorrect. Both accept standard SQL predicates and comparison operators."},
                    {"text": "HAVING is mandatory for all SELECT statements with multiple columns", "is_correct": False, "feedback": "Incorrect. HAVING is only required when filtering grouped aggregate expressions."},
                ],
            },
            {
                "title": "Relational Operations: UNION vs UNION ALL",
                "content": "When combining result sets from two SELECT statements with identical schemas, what is the key behavioral and performance distinction of UNION ALL compared to UNION?",
                "difficulty": "EASY",
                "explanation": "UNION performs an implicit DISTINCT sort operation to eliminate duplicate rows across both result sets. UNION ALL concatenates both sets directly without deduplication, executing faster.",
                "options": [
                    {"text": "UNION ALL preserves duplicate rows and executes faster without sort-deduplication", "is_correct": True, "feedback": "Correct. UNION ALL avoids the overhead of sorting and deduplicating rows."},
                    {"text": "UNION ALL rejects mismatched data types while UNION automatically coerces them", "is_correct": False, "feedback": "Incorrect. Both require union-compatible column types."},
                    {"text": "UNION preserves duplicates while UNION ALL keeps only unique tuples", "is_correct": False, "feedback": "Incorrect. The behavior is inverted; UNION deduplicates, UNION ALL preserves."},
                    {"text": "UNION ALL is restricted to single-table queries only", "is_correct": False, "feedback": "Incorrect. Both can combine arbitrary compatible queries."},
                ],
            },
            {
                "title": "Window Functions: DENSE_RANK vs RANK",
                "content": "Given scores [100, 90, 90, 80], what ranks are assigned to these four rows respectively by DENSE_RANK() vs RANK() ordered by score DESC?",
                "difficulty": "MEDIUM",
                "explanation": "For ties: RANK() assigns tied rows the same rank and skips subsequent numbers: [1, 2, 2, 4]. DENSE_RANK() assigns tied rows the same rank without gaps: [1, 2, 2, 3].",
                "options": [
                    {"text": "DENSE_RANK: 1, 2, 2, 3 | RANK: 1, 2, 2, 4", "is_correct": True, "feedback": "Correct. DENSE_RANK does not skip ranks after ties, whereas RANK leaves gaps for tied elements."},
                    {"text": "DENSE_RANK: 1, 2, 3, 4 | RANK: 1, 2, 2, 3", "is_correct": False, "feedback": "Incorrect. DENSE_RANK assigns the same rank to identical scores."},
                    {"text": "DENSE_RANK: 1, 2, 2, 4 | RANK: 1, 2, 2, 3", "is_correct": False, "feedback": "Incorrect. Inverted ranking behavior."},
                    {"text": "DENSE_RANK: 1, 1, 2, 3 | RANK: 1, 2, 3, 4", "is_correct": False, "feedback": "Incorrect. Rank starts at 1 for the highest score 100."},
                ],
            },
            {
                "title": "Null Handling: COUNT(column) vs COUNT(*)",
                "content": "In an employee table with 10 rows, where 2 rows have a NULL value in the bonus column, what are the outputs of SELECT COUNT(*), COUNT(bonus) FROM employees?",
                "difficulty": "MEDIUM",
                "explanation": "COUNT(*) counts the total number of rows in the table (10). COUNT(column_name) counts non-NULL values only in the specified column (10 - 2 = 8).",
                "options": [
                    {"text": "COUNT(*) = 10, COUNT(bonus) = 8", "is_correct": True, "feedback": "Correct. COUNT(*) counts all rows; COUNT(column) ignores NULL entries."},
                    {"text": "COUNT(*) = 10, COUNT(bonus) = 10", "is_correct": False, "feedback": "Incorrect. COUNT(column) excludes NULL values."},
                    {"text": "COUNT(*) = 8, COUNT(bonus) = 8", "is_correct": False, "feedback": "Incorrect. COUNT(*) includes all 10 tuples regardless of column NULLs."},
                    {"text": "COUNT(*) = 10, COUNT(bonus) = NULL", "is_correct": False, "feedback": "Incorrect. COUNT never returns NULL; it returns 0 if all values are NULL."},
                ],
            },
        ]

        def ingest_set(skill, questions_data):
            q_ids = []
            for item in questions_data:
                q = db.query(Question).filter(Question.title == item["title"]).first()
                if not q:
                    q = Question(
                        skill_id=skill.id,
                        title=item["title"],
                        content=item["content"],
                        question_type="MCQ_SINGLE",
                        difficulty=item["difficulty"],
                        default_points=1,
                        explanation=item["explanation"],
                        is_verified=True,
                        version=1,
                        status="PUBLISHED",
                    )
                    db.add(q)
                    db.flush()
                    for opt in item["options"]:
                        db.add(QuestionOption(
                            question_id=q.id,
                            option_text=opt["text"],
                            is_correct=opt["is_correct"],
                            feedback=opt["feedback"],
                        ))
                    print(f"  Ingested question: {q.title}")
                q_ids.append(q.id)
            return q_ids

        print("Ingesting Quantitative questions...")
        quant_ids = ingest_set(skill_quant, quant_questions_data)

        print("Ingesting Logical Reasoning questions...")
        logical_ids = ingest_set(skill_logical, logical_questions_data)

        print("Ingesting Verbal Ability questions...")
        verbal_ids = ingest_set(skill_verbal, verbal_questions_data)

        print("Ingesting Programming & DSA questions...")
        prog_ids = ingest_set(skill_prog, prog_questions_data)

        print("Ingesting SQL questions...")
        sql_ids = ingest_set(skill_sql, sql_questions_data)

        # -------------------------------------------------------------
        # Published Assessments
        # -------------------------------------------------------------
        assessments_spec = [
            {
                "title": "Quantitative Aptitude Diagnostic: Core Arithmetic & Algebra",
                "desc": "Baseline diagnostic covering Time-Work, Relative Speed, Percentages, and Modular Arithmetic.",
                "instructions": "Answer all 5 questions. Standard practice time limit: 15 minutes. Step-by-step mathematical proofs will be available immediately post-submission.",
                "category": "QUANTITATIVE_APTITUDE",
                "duration": 15,
                "passing": 3.0,
                "question_ids": quant_ids,
            },
            {
                "title": "Logical Reasoning Diagnostic: Syllogisms & Seating Matrices",
                "desc": "Placement exam readiness diagnostic for formal deduction, circular arrangements, and sequence series.",
                "instructions": "Each question carries 1 point. Incorrect answers do not incur penalties (Formative Mastery Pattern). Take your time to diagram arrangements before selecting.",
                "category": "LOGICAL_REASONING",
                "duration": 15,
                "passing": 3.0,
                "question_ids": logical_ids,
            },
            {
                "title": "Verbal Ability Diagnostic: Precision & Critical Reasoning",
                "desc": "Corporate placement diagnostic evaluating subject-verb agreement, contextual diction, and argumentative assumptions.",
                "instructions": "5 questions testing precision grammar and critical reading. Review feedback post-submission to inspect grammatical rules.",
                "category": "VERBAL_ABILITY",
                "duration": 15,
                "passing": 3.0,
                "question_ids": verbal_ids,
            },
            {
                "title": "Programming & DSA Diagnostic: Algorithms & Complexity",
                "desc": "Technical recruitment diagnostic evaluating recurrence relations, dynamic programming, stacks, and tree invariants.",
                "instructions": "5 algorithmic questions designed to benchmark core software engineering fundamentals. Step-by-step proofs provided upon submission.",
                "category": "PROGRAMMING_DSA",
                "duration": 15,
                "passing": 3.0,
                "question_ids": prog_ids,
            },
            {
                "title": "SQL & Relational Logic Diagnostic: Aggregations & Joins",
                "desc": "Database querying diagnostic testing anti-joins, aggregation predicates, set operations, and ranking window functions.",
                "instructions": "5 SQL questions assessing relational problem solving. Immediate distractor feedback available post-submission.",
                "category": "SQL_DATABASE",
                "duration": 15,
                "passing": 3.0,
                "question_ids": sql_ids,
            },
        ]

        print("Creating and publishing assessments...")
        for spec in assessments_spec:
            asm = db.query(Assessment).filter(Assessment.title == spec["title"]).first()
            if not asm:
                asm = Assessment(
                    institution_id=inst.id,
                    title=spec["title"],
                    description=spec["desc"],
                    instructions=spec["instructions"],
                    category=spec["category"],
                    duration_minutes=spec["duration"],
                    passing_score=spec["passing"],
                    is_published=True,
                    version=1,
                )
                db.add(asm)
                db.flush()

                for order, qid in enumerate(spec["question_ids"], start=1):
                    db.add(AssessmentQuestion(
                        assessment_id=asm.id,
                        question_id=qid,
                        order_index=order,
                        points=1,
                    ))
                print(f"Created and published assessment: {asm.title}")
            else:
                asm.is_published = True
                print(f"Assessment already exists: {asm.title}")

        db.commit()
        print("Curated question banks and assessments seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding practice banks: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_practice_banks()
