"""
Seed script to create and publish comprehensive Topic-Wise Assessments
for all 6 curriculum tracks (24 key focus topics total).

Categories:
1. QUANTITATIVE_APTITUDE (Percentages & Ratios, Time, Speed & Distance, Permutations & Probability, Data Interpretation)
2. LOGICAL_REASONING (Syllogisms & Seating, Blood Relations & Direction, Critical Thinking, Pattern Deduction)
3. VERBAL_ABILITY (Reading Comprehension, Sentence Correction, Para Jumbles, Vocabulary in Context)
4. SQL_DATABASES (Joins & Subqueries, Window Functions, Query Optimization, Schema Design)
5. HR_BEHAVIORAL (Situation Identification, Task Breakdown, Action Articulation, Result Quantification)
6. PROGRAMMING_DSA (Arrays & Strings, Linked Lists & Trees, Dynamic Programming, Graph Traversal)
"""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.institution import Institution
from app.models.skill import Skill
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.question import Question, QuestionOption

TOPIC_DATA = [
    # -------------------------------------------------------------
    # 1. QUANTITATIVE APTITUDE
    # -------------------------------------------------------------
    {
        "category": "QUANTITATIVE_APTITUDE",
        "domain": "QUANT",
        "topic": "Percentages & Ratios",
        "title": "Percentages & Ratios Diagnostic Drill",
        "description": "Standard placement diagnostic covering ratio proportionality, successive percentage shifts, and profit-margin optimizations.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Successive Percentage Change",
                "content": "The price of an item is first increased by 20% and then decreased by 15%. What is the net percentage change in the price?",
                "difficulty": "EASY",
                "explanation": "Let initial price be 100. After +20%, price = 120. After -15%, price = 120 - (0.15 * 120) = 120 - 18 = 102. Net increase = 2%.",
                "options": [
                    {"text": "2% increase", "is_correct": True, "feedback": "Correct: 1.20 * 0.85 = 1.02, representing a net 2% increase."},
                    {"text": "5% increase", "is_correct": False, "feedback": "Incorrect: Percentages cannot simply be added (20 - 15 = 5 is incorrect for successive shifts)."},
                    {"text": "2% decrease", "is_correct": False, "feedback": "Incorrect: The final value is 102, which is above 100."},
                    {"text": "No change (0%)", "is_correct": False, "feedback": "Incorrect: 20% of 100 is different from 15% of 120."}
                ]
            },
            {
                "title": "Ratio Division and Distribution",
                "content": "A sum of $1,400 is divided among A, B, and C in the ratio 2 : 3 : 5. What is the difference between the share of C and the share of A?",
                "difficulty": "EASY",
                "explanation": "Total parts = 2 + 3 + 5 = 10 parts. 1 part = 1400 / 10 = $140. A's share = 2 * 140 = $280. C's share = 5 * 140 = $700. Difference = 700 - 280 = $420.",
                "options": [
                    {"text": "$420", "is_correct": True, "feedback": "Correct: (5 - 2) * 140 = 3 * 140 = $420."},
                    {"text": "$280", "is_correct": False, "feedback": "Incorrect: $280 is A's individual share."},
                    {"text": "$350", "is_correct": False, "feedback": "Incorrect: Verify part allocation: 10 total parts."},
                    {"text": "$560", "is_correct": False, "feedback": "Incorrect: Difference is 3 parts, which equals $420."}
                ]
            },
            {
                "title": "Profit and Loss Markup",
                "content": "A retailer marks his goods at 25% above the cost price and allows a discount of 10% on the marked price. What is his profit percentage?",
                "difficulty": "MEDIUM",
                "explanation": "Let CP = 100. MP = 125. SP = 125 - 10% of 125 = 125 - 12.5 = 112.5. Profit = 112.5 - 100 = 12.5%.",
                "options": [
                    {"text": "12.5%", "is_correct": True, "feedback": "Correct: Effective selling price is 112.5% of CP, yielding 12.5% profit."},
                    {"text": "15.0%", "is_correct": False, "feedback": "Incorrect: The discount applies to MP (125), not CP."},
                    {"text": "10.0%", "is_correct": False, "feedback": "Incorrect: The net multiplier is 1.25 * 0.90 = 1.125."},
                    {"text": "17.5%", "is_correct": False, "feedback": "Incorrect: Subtracting 10 from 25 directly is invalid."}
                ]
            },
            {
                "title": "Mixture and Replacement Ratio",
                "content": "A container contains 40 liters of milk. From this, 4 liters of milk is taken out and replaced with water. This process was repeated further two times. How much milk is now contained in the container?",
                "difficulty": "HARD",
                "explanation": "Remaining liquid ratio formula: Final = Initial * (1 - x/V)^n = 40 * (1 - 4/40)^3 = 40 * (9/10)^3 = 40 * 0.729 = 29.16 liters.",
                "options": [
                    {"text": "29.16 liters", "is_correct": True, "feedback": "Correct: Using formula V * (1 - x/V)^n = 40 * (0.9)^3 = 29.16 L."},
                    {"text": "28.00 liters", "is_correct": False, "feedback": "Incorrect: Account for compounding milk depletion."},
                    {"text": "30.42 liters", "is_correct": False, "feedback": "Incorrect: That would only be 2 replacement cycles."},
                    {"text": "26.84 liters", "is_correct": False, "feedback": "Incorrect: Check (0.9)^3 * 40."}
                ]
            }
        ]
    },
    {
        "category": "QUANTITATIVE_APTITUDE",
        "domain": "QUANT",
        "topic": "Time, Speed & Distance",
        "title": "Time, Speed & Distance Diagnostic Drill",
        "description": "Evaluation of relative speed, trains, circular tracks, and boat/stream mechanics.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Relative Speed of Two Trains",
                "content": "Two trains of lengths 120m and 180m are traveling towards each other on parallel tracks at speeds of 54 km/h and 36 km/h. How many seconds will they take to completely pass each other?",
                "difficulty": "EASY",
                "explanation": "Total distance = 120 + 180 = 300m. Relative speed = 54 + 36 = 90 km/h = 90 * (5/18) = 25 m/s. Time = 300 / 25 = 12 seconds.",
                "options": [
                    {"text": "12 seconds", "is_correct": True, "feedback": "Correct: Relative speed = 25 m/s, total length = 300 m. Time = 300/25 = 12s."},
                    {"text": "15 seconds", "is_correct": False, "feedback": "Incorrect: Remember to convert 90 km/h to m/s by multiplying by 5/18."},
                    {"text": "10 seconds", "is_correct": False, "feedback": "Incorrect: 300 / 25 is exactly 12."},
                    {"text": "18 seconds", "is_correct": False, "feedback": "Incorrect: Check relative speed calculation."}
                ]
            },
            {
                "title": "Average Speed for Round Trip",
                "content": "A person travels from city A to city B at 60 km/h and returns at 40 km/h. What is his average speed for the whole journey?",
                "difficulty": "MEDIUM",
                "explanation": "Harmonic mean for equal distances: Avg Speed = 2xy / (x + y) = 2 * 60 * 40 / (60 + 40) = 4800 / 100 = 48 km/h.",
                "options": [
                    {"text": "48 km/h", "is_correct": True, "feedback": "Correct: 2 * 60 * 40 / (60 + 40) = 48 km/h."},
                    {"text": "50 km/h", "is_correct": False, "feedback": "Incorrect: Arithmetic mean (60+40)/2 is a classic trap because more time is spent at the lower speed."},
                    {"text": "45 km/h", "is_correct": False, "feedback": "Incorrect: Use 2*v1*v2 / (v1 + v2)."},
                    {"text": "52 km/h", "is_correct": False, "feedback": "Incorrect: Average speed must be lower than arithmetic mean 50."}
                ]
            },
            {
                "title": "Upstream and Downstream Motion",
                "content": "A boat can travel with a speed of 13 km/h in still water. If the speed of the stream is 4 km/h, find the time taken by the boat to go 68 km downstream.",
                "difficulty": "EASY",
                "explanation": "Downstream speed = Speed of boat + Speed of stream = 13 + 4 = 17 km/h. Time = 68 / 17 = 4 hours.",
                "options": [
                    {"text": "4 hours", "is_correct": True, "feedback": "Correct: 68 / (13 + 4) = 4 hours."},
                    {"text": "5 hours", "is_correct": False, "feedback": "Incorrect: Downstream speed adds stream velocity."},
                    {"text": "3.5 hours", "is_correct": False, "feedback": "Incorrect: 68 / 17 = 4."},
                    {"text": "6 hours", "is_correct": False, "feedback": "Incorrect: Check downstream addition."}
                ]
            },
            {
                "title": "Circular Track Meeting Point",
                "content": "Two runners A and B start simultaneously from the same point on a 400m circular track in opposite directions with speeds of 6 m/s and 4 m/s. When will they meet for the first time?",
                "difficulty": "MEDIUM",
                "explanation": "Relative speed in opposite directions = 6 + 4 = 10 m/s. Distance = 400m. Time = 400 / 10 = 40 seconds.",
                "options": [
                    {"text": "40 seconds", "is_correct": True, "feedback": "Correct: Relative speed = 10 m/s. 400 / 10 = 40s."},
                    {"text": "50 seconds", "is_correct": False, "feedback": "Incorrect: Speeds add when traveling in opposite directions."},
                    {"text": "30 seconds", "is_correct": False, "feedback": "Incorrect: 400 / (6 + 4) = 40."},
                    {"text": "200 seconds", "is_correct": False, "feedback": "Incorrect: That would be same-direction relative speed (400 / 2)."}
                ]
            }
        ]
    },
    {
        "category": "QUANTITATIVE_APTITUDE",
        "domain": "QUANT",
        "topic": "Permutations & Probability",
        "title": "Permutations & Probability Diagnostic Drill",
        "description": "Combinatorics, conditional probability, dice roll distributions, and deck selections.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Two Dice Sum Probability",
                "content": "Two unbiased dice are thrown simultaneously. What is the probability of getting two numbers whose sum is greater than 9?",
                "difficulty": "EASY",
                "explanation": "Total outcomes = 36. Favorable outcomes for sum > 9: Sum=10: (4,6), (5,5), (6,4) [3]. Sum=11: (5,6), (6,5) [2]. Sum=12: (6,6) [1]. Total favorable = 6. Probability = 6/36 = 1/6.",
                "options": [
                    {"text": "1/6", "is_correct": True, "feedback": "Correct: 6 favorable outcomes out of 36 gives 1/6."},
                    {"text": "1/9", "is_correct": False, "feedback": "Incorrect: There are 6 outcomes, not 4."},
                    {"text": "5/36", "is_correct": False, "feedback": "Incorrect: Count (4,6), (5,5), (6,4), (5,6), (6,5), (6,6)."},
                    {"text": "1/4", "is_correct": False, "feedback": "Incorrect: 9/36 would be 1/4; favorable is 6."}
                ]
            },
            {
                "title": "Word Letter Arrangements",
                "content": "In how many different ways can the letters of the word 'CORPORATION' be arranged so that the vowels always come together?",
                "difficulty": "HARD",
                "explanation": "Word: C-O-R-P-O-R-A-T-I-O-N. Total letters = 11. Vowels = O, O, A, I, O (5 vowels: 3 O's, 1 A, 1 I). Consonants = C, R, P, R, T, N (6 consonants: 2 R's). Treat 5 vowels as 1 unit: 6 + 1 = 7 units. Ways to arrange units = 7! / 2! = 2520. Ways to arrange vowels = 5! / 3! = 20. Total ways = 2520 * 20 = 50,400.",
                "options": [
                    {"text": "50,400", "is_correct": True, "feedback": "Correct: (7! / 2!) * (5! / 3!) = 2520 * 20 = 50,400."},
                    {"text": "42,000", "is_correct": False, "feedback": "Incorrect: Account for 3 identical O's in vowels."},
                    {"text": "120,000", "is_correct": False, "feedback": "Incorrect: Account for identical R's and O's."},
                    {"text": "25,200", "is_correct": False, "feedback": "Incorrect: You missed multiplying by the vowel arrangement (5!/3!)."}
                ]
            },
            {
                "title": "Ball Extraction Probability",
                "content": "A bag contains 6 red, 4 white, and 5 blue balls. If two balls are drawn at random without replacement, what is the probability that both are red?",
                "difficulty": "MEDIUM",
                "explanation": "Total balls = 6 + 4 + 5 = 15. Probability of first red = 6/15. Probability of second red = 5/14. P(Both Red) = (6/15) * (5/14) = 30 / 210 = 1/7.",
                "options": [
                    {"text": "1/7", "is_correct": True, "feedback": "Correct: (6/15) * (5/14) = 30/210 = 1/7."},
                    {"text": "2/15", "is_correct": False, "feedback": "Incorrect: Account for without-replacement denominator 14."},
                    {"text": "4/35", "is_correct": False, "feedback": "Incorrect: Check (6 * 5) / (15 * 14)."},
                    {"text": "1/5", "is_correct": False, "feedback": "Incorrect: 1/5 is 3/15."}
                ]
            }
        ]
    },
    {
        "category": "QUANTITATIVE_APTITUDE",
        "domain": "QUANT",
        "topic": "Data Interpretation",
        "title": "Data Interpretation Diagnostic Drill",
        "description": "Tabular data, bar graphs, pie chart percentage shares, and trend extrapolation.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Pie Chart Angle to Percentage",
                "content": "In a pie chart representing college operational expenses, the central angle corresponding to 'Laboratory Infrastructure' is 72 degrees. What percentage of total expenditure is spent on laboratory infrastructure?",
                "difficulty": "EASY",
                "explanation": "Full circle = 360 degrees. Percentage = (72 / 360) * 100 = (1/5) * 100 = 20%.",
                "options": [
                    {"text": "20%", "is_correct": True, "feedback": "Correct: (72 / 360) * 100 = 20%."},
                    {"text": "25%", "is_correct": False, "feedback": "Incorrect: 25% corresponds to 90 degrees."},
                    {"text": "18%", "is_correct": False, "feedback": "Incorrect: 72 / 360 = 0.20."},
                    {"text": "15%", "is_correct": False, "feedback": "Incorrect: 15% is 54 degrees."}
                ]
            },
            {
                "title": "Tabular Growth Rate Calculation",
                "content": "Company revenue grew from $40M in 2024 to $54M in 2026. What was the absolute percentage growth over this 2-year period?",
                "difficulty": "EASY",
                "explanation": "Growth = (54 - 40) / 40 * 100 = 14 / 40 * 100 = 35%.",
                "options": [
                    {"text": "35%", "is_correct": True, "feedback": "Correct: (14 / 40) * 100 = 35%."},
                    {"text": "30%", "is_correct": False, "feedback": "Incorrect: 14/40 = 0.35."},
                    {"text": "25%", "is_correct": False, "feedback": "Incorrect: 10/40 would be 25%."},
                    {"text": "40%", "is_correct": False, "feedback": "Incorrect: 16/40 would be 40%."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # 2. LOGICAL REASONING
    # -------------------------------------------------------------
    {
        "category": "LOGICAL_REASONING",
        "domain": "LOGICAL",
        "topic": "Syllogisms & Seating",
        "title": "Syllogisms & Seating Diagnostic Drill",
        "description": "Venn-diagram deductive validity, circular arrangements, and linear seating orders.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Categorical Syllogism Deduction",
                "content": "Statements:\n1. All engineers are problem solvers.\n2. Some problem solvers are designers.\n\nConclusions:\nI. Some engineers are designers.\nII. Some problem solvers are engineers.",
                "difficulty": "MEDIUM",
                "explanation": "Statement 1: Engineers ⊆ Problem Solvers. Therefore, Problem Solvers ∩ Engineers ≠ ∅ (Conclusion II is valid). However, Designers may intersect Problem Solvers outside of Engineers, so Conclusion I is not necessarily true.",
                "options": [
                    {"text": "Only Conclusion II follows", "is_correct": True, "feedback": "Correct: If all A are B, then some B must be A. The overlap with C is indefinite."},
                    {"text": "Only Conclusion I follows", "is_correct": False, "feedback": "Incorrect: There is no guarantee that designers overlap with engineers."},
                    {"text": "Both I and II follow", "is_correct": False, "feedback": "Incorrect: Conclusion I does not necessarily follow from the Venn model."},
                    {"text": "Neither I nor II follows", "is_correct": False, "feedback": "Incorrect: Conclusion II is a valid conversion of Statement 1."}
                ]
            },
            {
                "title": "Circular Seating Arrangement",
                "content": "Six friends (A, B, C, D, E, F) sit around a circular table facing the center. A is opposite D. B is to the immediate right of A. C is between A and E. Who is sitting to the immediate left of D?",
                "difficulty": "MEDIUM",
                "explanation": "Circle has 6 spots. Place A at bottom (spot 1). D is opposite (spot 4). Facing center, A's right is spot 2: B is at spot 2. C is between A and E: spot 6 is C, spot 5 is E. Remaining spot 3 is F. D is at spot 4 facing center: D's right is spot 3 (F), D's left is spot 5 (E). So E is to the immediate left of D.",
                "options": [
                    {"text": "E", "is_correct": True, "feedback": "Correct: D faces center; immediate left corresponds to spot 5 occupied by E."},
                    {"text": "B", "is_correct": False, "feedback": "Incorrect: B is next to A, not D."},
                    {"text": "F", "is_correct": False, "feedback": "Incorrect: F is to the immediate right of D."},
                    {"text": "C", "is_correct": False, "feedback": "Incorrect: C is adjacent to A and E."}
                ]
            }
        ]
    },
    {
        "category": "LOGICAL_REASONING",
        "domain": "LOGICAL",
        "topic": "Blood Relations & Direction",
        "title": "Blood Relations & Direction Diagnostic Drill",
        "description": "Kinship tree decoding and 2D vector coordinate displacement tests.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Kinship Tree Identification",
                "content": "Pointing to a photograph, a woman says: 'His mother's only son is my father.' How is the woman related to the man in the photograph?",
                "difficulty": "EASY",
                "explanation": "'His mother's only son' refers to the man himself. '...is my father' means the man in the photo is her father. Therefore, the woman is his daughter.",
                "options": [
                    {"text": "Daughter", "is_correct": True, "feedback": "Correct: His mother's only son = the man. The man = woman's father. Thus, woman = daughter."},
                    {"text": "Sister", "is_correct": False, "feedback": "Incorrect: 'My father' indicates parent-child relationship."},
                    {"text": "Mother", "is_correct": False, "feedback": "Incorrect: Man is the father, not child."},
                    {"text": "Niece", "is_correct": False, "feedback": "Incorrect: Note the keyword 'only son'."}
                ]
            },
            {
                "title": "Compass Displacement Vectors",
                "content": "A person walks 10 meters North, turns right and walks 6 meters, then turns right again and walks 18 meters. How far and in which direction is he from his starting point?",
                "difficulty": "MEDIUM",
                "explanation": "Initial point (0, 0). North 10m -> (0, 10). Turn right (East) 6m -> (6, 10). Turn right (South) 18m -> (6, -8). Distance = sqrt(6^2 + (-8)^2) = sqrt(36 + 64) = 10 meters. Vector is East and South -> South-East.",
                "options": [
                    {"text": "10 meters South-East", "is_correct": True, "feedback": "Correct: dx = +6, dy = -8. Hypotenuse = 10m in the South-East quadrant."},
                    {"text": "10 meters North-East", "is_correct": False, "feedback": "Incorrect: The final Y-coordinate is negative (South)."},
                    {"text": "14 meters South-East", "is_correct": False, "feedback": "Incorrect: 6-8-10 Pythagorean triple applies."},
                    {"text": "8 meters South", "is_correct": False, "feedback": "Incorrect: Don't ignore the 6 meters East displacement."}
                ]
            }
        ]
    },
    {
        "category": "LOGICAL_REASONING",
        "domain": "LOGICAL",
        "topic": "Critical Thinking",
        "title": "Critical Thinking Diagnostic Drill",
        "description": "Statement-assumption validity, course of action, and cause-and-effect evaluation.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Implicit Assumption Evaluation",
                "content": "Statement: 'Enroll in our 8-week bootcamp to guarantee an interview call at top tech firms.'\n\nAssumptions:\nI. Students desire to secure interview calls at top tech firms.\nII. The bootcamp provides skills or partnerships aligned with tech recruitment requirements.",
                "difficulty": "MEDIUM",
                "explanation": "Any advertising proposition assumes target audience demand (Assumption I) and that the offering possesses the efficacy/means to deliver the promised outcome (Assumption II). Both are implicitly assumed.",
                "options": [
                    {"text": "Both I and II are implicit", "is_correct": True, "feedback": "Correct: The statement hinges on both market demand and the bootcamp's capability."},
                    {"text": "Only I is implicit", "is_correct": False, "feedback": "Incorrect: The promise also assumes operational effectiveness (II)."},
                    {"text": "Only II is implicit", "is_correct": False, "feedback": "Incorrect: Assumption I is also required for the advertisement to be relevant."},
                    {"text": "Neither is implicit", "is_correct": False, "feedback": "Incorrect: Both assumptions logically underpin the marketing statement."}
                ]
            }
        ]
    },
    {
        "category": "LOGICAL_REASONING",
        "domain": "LOGICAL",
        "topic": "Pattern Deduction",
        "title": "Pattern Deduction Diagnostic Drill",
        "description": "Alphanumeric series shifts, matrix reasoning, and symmetry logic.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Geometric Sequence Shift",
                "content": "Find the next number in the series: 3, 7, 15, 31, 63, ?",
                "difficulty": "EASY",
                "explanation": "Pattern: multiply by 2 and add 1. 3*2+1 = 7, 7*2+1 = 15, 15*2+1 = 31, 31*2+1 = 63, 63*2+1 = 127. Alternatively, differences are 4, 8, 16, 32, 64.",
                "options": [
                    {"text": "127", "is_correct": True, "feedback": "Correct: 63 * 2 + 1 = 127."},
                    {"text": "126", "is_correct": False, "feedback": "Incorrect: Remember to add 1."},
                    {"text": "125", "is_correct": False, "feedback": "Incorrect: Check the powers of 2 minus 1 pattern (2^7 - 1 = 127)."},
                    {"text": "131", "is_correct": False, "feedback": "Incorrect: Difference step is 64; 63 + 64 = 127."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # 3. VERBAL ABILITY & READING
    # -------------------------------------------------------------
    {
        "category": "VERBAL_ABILITY",
        "domain": "VERBAL",
        "topic": "Reading Comprehension",
        "title": "Reading Comprehension Placement Drill",
        "description": "Short editorial passages, central premise extraction, and author tone evaluation.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Central Thesis Identification",
                "content": "Passage: 'While artificial intelligence accelerates automation across data pipelines, corporate leadership increasingly values qualitative traits—such as ambiguity tolerance, ethical stewardship, and interdisciplinary collaboration—that deterministic models cannot replicate.'\n\nWhat is the author's primary assertion?",
                "difficulty": "MEDIUM",
                "explanation": "The author contrasts automated technical pipelines with irreplaceable qualitative human traits, arguing that AI adoption elevates the demand for non-deterministic human competencies.",
                "options": [
                    {"text": "AI adoption increases the strategic value of human qualitative skills", "is_correct": True, "feedback": "Correct: The passage highlights that automation elevates the uniqueness of human leadership traits."},
                    {"text": "Automation will soon replace all corporate leadership roles", "is_correct": False, "feedback": "Incorrect: The author asserts the exact opposite regarding qualitative traits."},
                    {"text": "Deterministic models are superior in ethical stewardship", "is_correct": False, "feedback": "Incorrect: The passage notes models cannot replicate ethical stewardship."},
                    {"text": "Data pipelines should not be automated", "is_correct": False, "feedback": "Incorrect: No opposition to pipeline automation is stated."}
                ]
            }
        ]
    },
    {
        "category": "VERBAL_ABILITY",
        "domain": "VERBAL",
        "topic": "Sentence Correction",
        "title": "Sentence Correction & Grammar Diagnostic Drill",
        "description": "Subject-verb agreement, modifier placement, parallelism, and subjunctive moods.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Subject-Verb Agreement with Collective Phrase",
                "content": "Identify the grammatically correct sentence:",
                "difficulty": "MEDIUM",
                "explanation": "'Neither the software engineer nor the product managers were available...' When 'neither...nor' connects subjects of different number, the verb agrees with the closer subject ('product managers' is plural -> 'were').",
                "options": [
                    {"text": "Neither the software engineer nor the product managers were available for the retrospective.", "is_correct": True, "feedback": "Correct: With 'neither...nor', the verb agrees with the closer subject ('product managers' -> 'were')."},
                    {"text": "Neither the software engineer nor the product managers was available for the retrospective.", "is_correct": False, "feedback": "Incorrect: 'Managers' is plural and is closest to the verb."},
                    {"text": "Neither the software engineer nor the product managers is available for the retrospective.", "is_correct": False, "feedback": "Incorrect: Singular verb 'is' disagrees with plural 'managers'."},
                    {"text": "Neither of the product managers were available for the retrospective.", "is_correct": False, "feedback": "Incorrect: 'Neither of' takes a singular verb ('was')."}
                ]
            }
        ]
    },
    {
        "category": "VERBAL_ABILITY",
        "domain": "VERBAL",
        "topic": "Para Jumbles",
        "title": "Para Jumbles & Coherence Drill",
        "description": "Logical sequencing of disordered corporate and academic arguments.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Narrative Sequence Reordering",
                "content": "Arrange the sentences in logical sequence:\nP: This rapid transition created sudden demand for distributed cloud infrastructure.\nQ: Historically, organizations maintained centralized on-premise computing servers.\nR: Consequently, cybersecurity architectures were overhauled to support remote endpoints.\nS: However, the shift toward hybrid remote work disrupted traditional hardware models.",
                "difficulty": "MEDIUM",
                "explanation": "Q establishes the historical baseline (centralized servers). S introduces the disruption (hybrid work). P details the immediate consequence (demand for distributed cloud). R concludes with the secondary ripple effect (cybersecurity overhaul). Order: Q - S - P - R.",
                "options": [
                    {"text": "Q - S - P - R", "is_correct": True, "feedback": "Correct: Chronological & causal sequence: Historical baseline (Q) -> Disruption (S) -> Immediate demand (P) -> Consequence (R)."},
                    {"text": "S - Q - P - R", "is_correct": False, "feedback": "Incorrect: Q must precede S to establish what was shifted away from."},
                    {"text": "Q - P - S - R", "is_correct": False, "feedback": "Incorrect: S provides the reason for the transition mentioned in P."},
                    {"text": "P - R - Q - S", "is_correct": False, "feedback": "Incorrect: 'This rapid transition' cannot open the paragraph without antecedent."}
                ]
            }
        ]
    },
    {
        "category": "VERBAL_ABILITY",
        "domain": "VERBAL",
        "topic": "Vocabulary in Context",
        "title": "Vocabulary in Context Diagnostic Drill",
        "description": "Nuanced contextual vocabulary, tone connotations, and high-frequency corporate idioms.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Contextual Definition Selection",
                "content": "Select the word that best completes the sentence:\n'The engineering team conducted a/an ______ audit to ensure zero telemetry leakage before deploying the financial gateway.'",
                "difficulty": "EASY",
                "explanation": "'Exhaustive' means thorough, comprehensive, and all-inclusive, which aligns with 'ensure zero leakage'.",
                "options": [
                    {"text": "exhaustive", "is_correct": True, "feedback": "Correct: 'Exhaustive' denotes comprehensive scrutiny suitable for financial compliance."},
                    {"text": "ephemeral", "is_correct": False, "feedback": "Incorrect: 'Ephemeral' means short-lived or fleeting."},
                    {"text": "perfunctory", "is_correct": False, "feedback": "Incorrect: 'Perfunctory' means careless or minimal, opposite of the intended rigor."},
                    {"text": "ambiguous", "is_correct": False, "feedback": "Incorrect: 'Ambiguous' means open to multiple interpretations."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # 4. DATABASE & SQL SYSTEMS
    # -------------------------------------------------------------
    {
        "category": "SQL_DATABASES",
        "domain": "SQL",
        "topic": "Joins & Subqueries",
        "title": "SQL Joins & Subqueries Diagnostic Drill",
        "description": "Inner, outer, and cross joins, correlated subqueries, and set operations.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "LEFT JOIN Null Handling",
                "content": "Given tables `students` (id, name) and `internships` (id, student_id, company), which query returns all students who have NOT secured any internship?",
                "difficulty": "EASY",
                "explanation": "A LEFT JOIN with a `WHERE internships.student_id IS NULL` filter preserves all students and discards rows where an internship match was found.",
                "options": [
                    {"text": "SELECT s.name FROM students s LEFT JOIN internships i ON s.id = i.student_id WHERE i.student_id IS NULL;", "is_correct": True, "feedback": "Correct: Left join anti-pattern identifies unmatched left table records."},
                    {"text": "SELECT s.name FROM students s INNER JOIN internships i ON s.id = i.student_id WHERE i.company IS NULL;", "is_correct": False, "feedback": "Incorrect: Inner join will filter out students without internships entirely."},
                    {"text": "SELECT s.name FROM students s WHERE s.id = (SELECT student_id FROM internships);", "is_correct": False, "feedback": "Incorrect: Subquery returns multiple rows and tests for existence, not absence."},
                    {"text": "SELECT s.name FROM students s RIGHT JOIN internships i ON s.id = i.student_id;", "is_correct": False, "feedback": "Incorrect: Right join preserves internships, not students."}
                ]
            },
            {
                "title": "Correlated Subquery Efficiency",
                "content": "What is the primary operational characteristic of a correlated subquery in SQL?",
                "difficulty": "MEDIUM",
                "explanation": "A correlated subquery references columns from the outer query, causing the database engine to evaluate it row-by-row for every candidate row of the outer query unless transformed by the query optimizer.",
                "options": [
                    {"text": "It references columns from the outer query and executes once for each candidate row.", "is_correct": True, "feedback": "Correct: Correlated subqueries depend on the outer row context for execution."},
                    {"text": "It executes strictly once before the outer query runs.", "is_correct": False, "feedback": "Incorrect: That describes an uncorrelated (independent) subquery."},
                    {"text": "It can only be used inside the HAVING clause.", "is_correct": False, "feedback": "Incorrect: Correlated subqueries can reside in SELECT, WHERE, and FROM clauses."},
                    {"text": "It always bypasses database indexes.", "is_correct": False, "feedback": "Incorrect: Inner queries can leverage indexes on the correlated predicate."}
                ]
            }
        ]
    },
    {
        "category": "SQL_DATABASES",
        "domain": "SQL",
        "topic": "Window Functions",
        "title": "SQL Window Functions & Aggregations Drill",
        "description": "ROW_NUMBER, RANK, DENSE_RANK, PARTITION BY, and running totals.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "RANK vs DENSE_RANK Behavior",
                "content": "If three students tie for 1st place with identical assessment scores, what rank will the student with the next highest score receive under DENSE_RANK() vs RANK()?",
                "difficulty": "MEDIUM",
                "explanation": "RANK() skips subsequent rank numbers according to the tie count (1, 1, 1, 4). DENSE_RANK() never skips numbers (1, 1, 1, 2).",
                "options": [
                    {"text": "DENSE_RANK() yields 2; RANK() yields 4", "is_correct": True, "feedback": "Correct: DENSE_RANK does not produce gaps (next is 2), whereas RANK skips 2 and 3 to produce 4."},
                    {"text": "DENSE_RANK() yields 4; RANK() yields 2", "is_correct": False, "feedback": "Incorrect: RANK creates gaps; DENSE_RANK stays consecutive."},
                    {"text": "Both functions yield 2", "is_correct": False, "feedback": "Incorrect: RANK accounts for preceding tied rows."},
                    {"text": "Both functions yield 4", "is_correct": False, "feedback": "Incorrect: DENSE_RANK is consecutive."}
                ]
            }
        ]
    },
    {
        "category": "SQL_DATABASES",
        "domain": "SQL",
        "topic": "Query Optimization",
        "title": "SQL Query Optimization Diagnostic Drill",
        "description": "B-Tree index utilization, EXPLAIN plan interpretation, and sargability.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Sargable Query Predicates",
                "content": "Which of the following WHERE clause filters is non-sargable (cannot efficiently utilize a standard B-tree index on `created_at`)?",
                "difficulty": "MEDIUM",
                "explanation": "Wrapping the indexed column in a function like `YEAR(created_at) = 2026` prevents index range scans. Using `created_at >= '2026-01-01' AND created_at < '2027-01-01'` is sargable.",
                "options": [
                    {"text": "WHERE YEAR(created_at) = 2026", "is_correct": True, "feedback": "Correct: Applying a function directly to the indexed column prevents direct B-Tree index lookup."},
                    {"text": "WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01'", "is_correct": False, "feedback": "Incorrect: This is a sargable range scan that efficiently leverages the index."},
                    {"text": "WHERE created_at = '2026-10-26 00:00:00'", "is_correct": False, "feedback": "Incorrect: Exact match is fully sargable."},
                    {"text": "WHERE created_at > '2026-06-01'", "is_correct": False, "feedback": "Incorrect: Open-ended range is sargable."}
                ]
            }
        ]
    },
    {
        "category": "SQL_DATABASES",
        "domain": "SQL",
        "topic": "Schema Design",
        "title": "Database Schema Design & Normalization Drill",
        "description": "Third Normal Form (3NF), BCNF, foreign key cascades, and surrogate vs natural keys.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Third Normal Form (3NF) Violations",
                "content": "A table `student_placements` contains: (student_id, student_name, company_id, company_name, company_headquarters). Why does this table violate 3NF?",
                "difficulty": "EASY",
                "explanation": "3NF requires that no non-prime attribute is transitively dependent on the primary key. `company_headquarters` depends on `company_id`, which in turn depends on `student_id`.",
                "options": [
                    {"text": "Transitive dependency: company_headquarters depends on company_id, not directly on the primary key.", "is_correct": True, "feedback": "Correct: Transitive dependencies must be isolated into a separate company table to satisfy 3NF."},
                    {"text": "It contains composite primary keys.", "is_correct": False, "feedback": "Incorrect: Composite keys alone do not violate 3NF."},
                    {"text": "The table lacks a foreign key constraint.", "is_correct": False, "feedback": "Incorrect: 3NF is a functional dependency property, not constraint syntax."},
                    {"text": "Student name depends on company headquarters.", "is_correct": False, "feedback": "Incorrect: That dependency does not exist."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # 5. HR & STAR BEHAVIORAL FRAMEWORK
    # -------------------------------------------------------------
    {
        "category": "HR_BEHAVIORAL",
        "domain": "HR",
        "topic": "Situation Identification",
        "title": "STAR: Situation Identification Diagnostic Drill",
        "description": "Setting context, defining business constraints, and avoiding narrative scope creep.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "STAR Situation Opening Quality",
                "content": "When framing the 'Situation' component in a behavioral placement interview, what is the optimal narrative approach?",
                "difficulty": "EASY",
                "explanation": "The Situation should be concise (1-2 sentences), establishing the organizational context, stakes, and constraints without getting bogged down in implementation details.",
                "options": [
                    {"text": "Provide crisp, concise context stating the project setting, timeline, and high-level stakes in 1-2 sentences.", "is_correct": True, "feedback": "Correct: The Situation sets the stage quickly so the majority of time is allocated to your Actions and Results."},
                    {"text": "Spend 5 minutes explaining all technical architecture diagrams and database schemas.", "is_correct": False, "feedback": "Incorrect: Over-indexing on background details causes the interviewer to lose interest."},
                    {"text": "Skip the situation and jump directly to what code you wrote.", "is_correct": False, "feedback": "Incorrect: Without context, the interviewer cannot calibrate the difficulty of your challenge."},
                    {"text": "Attribute all project difficulties to incompetent former team members.", "is_correct": False, "feedback": "Incorrect: Blaming teammates indicates poor emotional intelligence and teamwork."}
                ]
            }
        ]
    },
    {
        "category": "HR_BEHAVIORAL",
        "domain": "HR",
        "topic": "Task Breakdown",
        "title": "STAR: Task Breakdown Diagnostic Drill",
        "description": "Differentiating personal ownership from team goals and articulating specific deliverables.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Defining Individual Task vs Team Mandate",
                "content": "In the STAR framework, how should a candidate differentiate 'Task' from 'Situation'?",
                "difficulty": "MEDIUM",
                "explanation": "The Situation describes the overall team/company problem; the Task defines the candidate's explicit personal responsibility and success criteria within that problem.",
                "options": [
                    {"text": "The Task isolates the candidate's specific individual assignment and success criteria within the broader situation.", "is_correct": True, "feedback": "Correct: Interviewers need to know what YOU were personally responsible for delivering."},
                    {"text": "The Task describes what external competitors were doing.", "is_correct": False, "feedback": "Incorrect: Competitors are market background, not your internal assignment."},
                    {"text": "The Task is identical to the Result.", "is_correct": False, "feedback": "Incorrect: Task is the objective prior to execution; Result is the measured outcome afterward."},
                    {"text": "The Task is a list of tools you installed on your workstation.", "is_correct": False, "feedback": "Incorrect: Tools belong in Action, not the core responsibility mandate."}
                ]
            }
        ]
    },
    {
        "category": "HR_BEHAVIORAL",
        "domain": "HR",
        "topic": "Action Articulation",
        "title": "STAR: Action Articulation Diagnostic Drill",
        "description": "Highlighting personal agency, technical trade-offs, and collaborative leadership.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Active Voice and Personal Ownership",
                "content": "Why do corporate recruiters caution against using 'We did...' excessively during the Action phase of STAR responses?",
                "difficulty": "EASY",
                "explanation": "Exclusive use of 'we' obscures what the candidate individually contributed, making it difficult for the interviewer to evaluate their standalone capabilities.",
                "options": [
                    {"text": "It obscures the candidate's individual contributions, decisions, and problem-solving agency.", "is_correct": True, "feedback": "Correct: Candidates should balance team acknowledgement with clear 'I decided...', 'I engineered...' ownership."},
                    {"text": "Using 'we' is a violation of non-disclosure agreements.", "is_correct": False, "feedback": "Incorrect: It is an evaluation issue, not an NDA violation."},
                    {"text": "Engineers are strictly forbidden from working in teams.", "is_correct": False, "feedback": "Incorrect: Teamwork is valued, but interview grading is individual."},
                    {"text": "Recruiters only evaluate individual freelance contributors.", "is_correct": False, "feedback": "Incorrect: Most placements are for corporate team roles."}
                ]
            }
        ]
    },
    {
        "category": "HR_BEHAVIORAL",
        "domain": "HR",
        "topic": "Result Quantification",
        "title": "STAR: Result Quantification Diagnostic Drill",
        "description": "Metric benchmarking, business impact articulation, and reflective learnings.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Quantified Outcome Formulation",
                "content": "Which of the following statements represents the strongest 'Result' articulation in a placement interview?",
                "difficulty": "EASY",
                "explanation": "Specific, quantified metrics (e.g. latency reduced by 42%, zero downtime deployment) provide undeniable proof of impact compared to vague assertions.",
                "options": [
                    {"text": "'The pipeline optimization reduced batch execution time by 42% (from 48 min to 28 min) and eliminated production memory timeouts.'", "is_correct": True, "feedback": "Correct: Concrete percentage and time-delta metrics provide tangible proof of engineering impact."},
                    {"text": "'Everyone on the team was very happy with my hard work.'", "is_correct": False, "feedback": "Incorrect: Subjective sentiment lacks objective metric evidence."},
                    {"text": "'The project finished and we went out for team dinner.'", "is_correct": False, "feedback": "Incorrect: Irrelevant to engineering outcome."},
                    {"text": "'I think the system became faster but we didn't measure it.'", "is_correct": False, "feedback": "Incorrect: Unmeasured claims undermine credibility."}
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # 6. PROGRAMMING & DATA STRUCTURES
    # -------------------------------------------------------------
    {
        "category": "PROGRAMMING_DSA",
        "domain": "PROGRAMMING",
        "topic": "Arrays & Strings",
        "title": "Arrays & Strings Diagnostic Drill",
        "description": "Array manipulation, prefix sums, two-pointer scanning, and string tokenization.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Two-Pointer Sorted Array Sum",
                "content": "Given a sorted array of N integers and a target sum T, what is the optimal time complexity to determine if any two elements sum to T using two pointers?",
                "difficulty": "EASY",
                "explanation": "Since the array is already sorted, placing one pointer at index 0 and another at N-1 allows us to find the pair in a single pass of O(N) time and O(1) space.",
                "options": [
                    {"text": "O(N) time and O(1) auxiliary space", "is_correct": True, "feedback": "Correct: Two pointers moving inwards across a sorted array inspect each element at most once."},
                    {"text": "O(N log N) time and O(N) auxiliary space", "is_correct": False, "feedback": "Incorrect: The array is already sorted, so no sorting step is required."},
                    {"text": "O(N^2) time and O(1) auxiliary space", "is_correct": False, "feedback": "Incorrect: That is the brute-force nested loop approach."},
                    {"text": "O(log N) time and O(1) auxiliary space", "is_correct": False, "feedback": "Incorrect: You cannot guarantee finding the pair with simple binary search without iterating."}
                ]
            }
        ]
    },
    {
        "category": "PROGRAMMING_DSA",
        "domain": "PROGRAMMING",
        "topic": "Linked Lists & Trees",
        "title": "Linked Lists & Trees Diagnostic Drill",
        "description": "Pointer mutation, Floyd cycle finding, BST invariants, and tree height.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Floyd's Cycle Detection Algorithm",
                "content": "In Floyd's Tortoise and Hare algorithm for linked list cycle detection, if a cycle exists, what is the maximum time complexity before the two pointers meet?",
                "difficulty": "EASY",
                "explanation": "The fast pointer advances by 2 while the slow pointer advances by 1. The relative speed difference is 1 node per step. Within at most N steps, the fast pointer catches up to the slow pointer, yielding O(N) time.",
                "options": [
                    {"text": "O(N) time where N is the number of nodes", "is_correct": True, "feedback": "Correct: The relative distance between pointers decreases by 1 on every iteration, bounded by O(N)."},
                    {"text": "O(N^2) time", "is_correct": False, "feedback": "Incorrect: The fast pointer catches up in linear time."},
                    {"text": "O(log N) time", "is_correct": False, "feedback": "Incorrect: Linked lists do not allow random pointer access."},
                    {"text": "O(1) time", "is_correct": False, "feedback": "Incorrect: Pointers must traverse the non-cyclic and cyclic portions."}
                ]
            }
        ]
    },
    {
        "category": "PROGRAMMING_DSA",
        "domain": "PROGRAMMING",
        "topic": "Dynamic Programming",
        "title": "Dynamic Programming Diagnostic Drill",
        "description": "Optimal substructure, overlapping subproblems, memoization, and tabulations.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "0/1 Knapsack State Formulation",
                "content": "In the standard 0/1 Knapsack problem with N items and maximum weight capacity W, what are the dimensions of the dynamic programming memoization table?",
                "difficulty": "MEDIUM",
                "explanation": "State dp[i][w] represents the maximum value achievable considering the first `i` items with remaining weight capacity `w`. Dimensions are (N + 1) x (W + 1).",
                "options": [
                    {"text": "(N + 1) x (W + 1)", "is_correct": True, "feedback": "Correct: Row index 0..N represents items considered; column index 0..W represents available capacity."},
                    {"text": "N x N", "is_correct": False, "feedback": "Incorrect: Capacity W is an independent constraint variable."},
                    {"text": "2^N x W", "is_correct": False, "feedback": "Incorrect: 2^N would be the unmemoized recursion tree space."},
                    {"text": "W x W", "is_correct": False, "feedback": "Incorrect: Table depends on both item count N and capacity W."}
                ]
            }
        ]
    },
    {
        "category": "PROGRAMMING_DSA",
        "domain": "PROGRAMMING",
        "topic": "Graph Traversal",
        "title": "Graph Traversal Diagnostic Drill",
        "description": "BFS shortest paths, DFS topological sorting, and cycle detection.",
        "duration_minutes": 15,
        "questions": [
            {
                "title": "Breadth-First Search Shortest Path Guarantee",
                "content": "Under what condition is Breadth-First Search (BFS) guaranteed to find the shortest path between two vertices in a graph?",
                "difficulty": "EASY",
                "explanation": "BFS explores vertices in concentric distance layers, guaranteeing the fewest edges traversed. This represents the minimal path cost if and only if all edge weights are uniform (unweighted graph).",
                "options": [
                    {"text": "When all edge weights are equal (or unweighted)", "is_correct": True, "feedback": "Correct: BFS level-by-level exploration guarantees minimal hops, which equates to shortest path when weights are uniform."},
                    {"text": "For any weighted graph with positive weights", "is_correct": False, "feedback": "Incorrect: Graphs with non-uniform positive weights require Dijkstra's algorithm."},
                    {"text": "Only when the graph is a Directed Acyclic Graph (DAG)", "is_correct": False, "feedback": "Incorrect: BFS operates on general unweighted graphs with cycles."},
                    {"text": "Only when the graph has no cycles", "is_correct": False, "feedback": "Incorrect: Visited arrays handle cycles safely."}
                ]
            }
        ]
    }
]

def seed_topic_wise():
    db = SessionLocal()
    print("Beginning Topic-Wise Assessment Seeding...")

    # Identify student institution
    inst = db.query(Institution).filter(Institution.id == "e5703059-fc33-4d55-8716-f6e321bb39c0").first()
    if not inst:
        inst = db.query(Institution).first()
    print(f"Target Institution: {inst.name} ({inst.id})")

    created_assessments = 0
    created_questions = 0

    for track in TOPIC_DATA:
        category = track["category"]
        domain = track["domain"]
        topic = track["topic"]
        title = track["title"]
        description = track["description"]
        duration = track["duration_minutes"]

        # Ensure skill exists
        skill = db.query(Skill).filter(Skill.name == topic, Skill.domain == domain).first()
        if not skill:
            skill = Skill(
                name=topic,
                domain=domain,
                description=f"Curriculum skill module for {topic} in {category}"
            )
            db.add(skill)
            db.commit()
            db.refresh(skill)

        # Check if assessment exists for this topic
        assessment = db.query(Assessment).filter(
            Assessment.topic == topic,
            Assessment.institution_id == inst.id
        ).first()

        if not assessment:
            # Also check by title
            assessment = db.query(Assessment).filter(
                Assessment.title == title,
                Assessment.institution_id == inst.id
            ).first()

        if not assessment:
            assessment = Assessment(
                institution_id=inst.id,
                title=title,
                description=description,
                instructions="Read each problem carefully. This diagnostic counts towards topic mastery analytics and syncs incorrect items directly into your Mistake Notebook.",
                category=category,
                topic=topic,
                duration_minutes=duration,
                passing_score=60.0,
                version=1,
                is_published=True
            )
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            created_assessments += 1
            print(f"  + Created Assessment: {title} [Topic: {topic}]")
        else:
            assessment.topic = topic
            assessment.is_published = True
            assessment.category = category
            db.commit()
            print(f"  ~ Updated Assessment: {title} [Topic: {topic}]")

        # Now link questions
        for idx, q_data in enumerate(track["questions"]):
            # Check if question exists
            existing_q = db.query(Question).filter(
                Question.title == q_data["title"],
                Question.skill_id == skill.id
            ).first()

            if not existing_q:
                q = Question(
                    skill_id=skill.id,
                    title=q_data["title"],
                    content=q_data["content"],
                    question_type="MCQ_SINGLE",
                    difficulty=q_data["difficulty"],
                    default_points=2,
                    explanation=q_data["explanation"],
                    is_verified=True,
                    version=1,
                    status="PUBLISHED"
                )
                db.add(q)
                db.commit()
                db.refresh(q)
                created_questions += 1

                for opt_idx, opt_data in enumerate(q_data["options"]):
                    opt = QuestionOption(
                        question_id=q.id,
                        option_text=opt_data["text"],
                        is_correct=opt_data["is_correct"],
                        feedback=opt_data.get("feedback")
                    )
                    db.add(opt)
                db.commit()
            else:
                q = existing_q

            # Link question to assessment if not already linked
            link = db.query(AssessmentQuestion).filter(
                AssessmentQuestion.assessment_id == assessment.id,
                AssessmentQuestion.question_id == q.id
            ).first()
            if not link:
                link = AssessmentQuestion(
                    assessment_id=assessment.id,
                    question_id=q.id,
                    order_index=idx + 1,
                    points=2
                )
                db.add(link)
                db.commit()

    print("\n-----------------------------------------------------------")
    print(f"Summary: Seeded topic-wise assessments.")
    print(f"New Assessments Created: {created_assessments}")
    print(f"New Questions Created: {created_questions}")

    # Total check
    assessments_with_topics = db.query(Assessment).filter(
        Assessment.institution_id == inst.id,
        Assessment.is_published == True
    ).all()
    print(f"Total Published Assessments for Institution: {len(assessments_with_topics)}")
    for a in assessments_with_topics:
        q_count = len(a.questions)
        print(f"  - [{a.category}] {a.title} | Topic: '{a.topic}' | Questions: {q_count}")

    db.close()

if __name__ == "__main__":
    seed_topic_wise()
