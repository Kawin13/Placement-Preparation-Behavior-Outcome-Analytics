"""
Script to populate rich, authentic student records across all portals:
- Student Workspace (Activities, Goals, Profile)
- Career Roadmap & Topic Progress
- DSA Coding Studio (Submissions, Solved Problems, User Progress)
- Practice Assessments & Attempt Records
- Mistake Notebook (With personal notes and revision statuses)
- Behavioral Telemetry Events (Cadence, regularity, session events)
- Role Readiness & Skill Mastery
- Placement Outcomes & Offers
- Training Programs & Cohort Performance
"""

import uuid
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, StudentProfile
from app.models.institution import Institution, Department, Cohort
from app.models.skill import Skill
from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.practice import AttemptRecord, MistakeNotebookEntry, PreparationActivity, LearningGoal, PracticeSession
from app.models.dsa import DSATopic, DSAProblem, DSASubmission, DSAUserProgress
from app.models.roadmap import CareerPath, RoadmapSubject, RoadmapTopic, LearningResource, StudentCareerGoal, StudentTopicProgress, StudentBehaviorEvent
from app.models.placement import PlacementOutcome
from app.models.training import TrainingProgram, TrainingSession, TrainingAttendance

def seed_rich_data():
    db = SessionLocal()
    try:
        print("Finding student@college.edu...")
        student = db.query(User).filter(User.email == "student@college.edu").first()
        if not student:
            print("student@college.edu not found, querying any active student...")
            student = db.query(User).filter(User.role == "STUDENT").first()

        if not student:
            print("No student found! Exiting.")
            return

        print(f"Enriching records for student: {student.full_name} ({student.email}), ID: {student.id}")
        inst_id = student.institution_id

        # 1. Ensure StudentProfile is rich and complete
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == student.id).first()
        cohort = db.query(Cohort).filter(Cohort.id == profile.cohort_id).first() if profile and profile.cohort_id else None
        if not cohort:
            cohort = db.query(Cohort).join(Department).filter(Department.institution_id == inst_id).first()
            if not cohort:
                cohort = db.query(Cohort).first()

        if not profile:
            profile = StudentProfile(
                user_id=student.id,
                cohort_id=cohort.id if cohort else None,
                roll_number="26CSE001",
                cgpa=8.85,
                placement_status="IN_PROCESS",
            )
            db.add(profile)
        else:
            profile.roll_number = "26CSE001"
            profile.cgpa = 8.85
            profile.placement_status = "IN_PROCESS"
            if cohort and not profile.cohort_id:
                profile.cohort_id = cohort.id
        db.flush()

        # 2. Preparation Activities (Weekly and daily log)
        existing_act_topics = {a.topic for a in db.query(PreparationActivity.topic).filter(PreparationActivity.user_id == student.id).all()}
        activities_data = [
            ("PRACTICE_SESSION", "PROGRAMMING", "Mastered Prefix Sums & Two Pointers", 90, "Studied range queries and solved LeetCode subarray problems.", 5),
            ("MOCK_TEST", "QUANTITATIVE_APTITUDE", "Quantitative Diagnostic: Time & Work", 45, "Solved 15 questions on combined work efficiency with 85% accuracy.", 4),
            ("SELF_STUDY", "PROGRAMMING", "Binary Trees Inorder & Preorder Traversal", 120, "Implemented recursive and iterative traversals in Python and analyzed stack trace.", 3),
            ("CONCEPT_REVISION", "CORE_TECHNICAL", "Database Normalization & Indexing", 60, "Reviewed B-Tree indexes, composite keys, and 3NF vs BCNF trade-offs.", 2),
            ("PRACTICE_SESSION", "PROGRAMMING", "Dynamic Programming: 0/1 Knapsack", 150, "Wrote bottom-up table memoization for knapsack variants and bounded sums.", 1),
            ("MISTAKE_REVIEW", "VERBAL_ABILITY", "Verbal Logic & Reading Comprehension Drill", 40, "Completed paragraph completion and syntax analysis exercises.", 0),
        ]

        now = datetime.now(timezone.utc)
        for act_type, cat, topic, duration, notes, days_ago in activities_data:
            if topic not in existing_act_topics:
                act = PreparationActivity(
                    user_id=student.id,
                    activity_type=act_type,
                    category=cat,
                    topic=topic,
                    duration_minutes=duration,
                    completion_state="COMPLETED",
                    provenance="STUDENT_LOGGED",
                    notes=notes,
                    activity_date=now - timedelta(days=days_ago),
                )
                db.add(act)
        db.flush()

        # 3. Learning Goals
        existing_goals = {g.title for g in db.query(LearningGoal.title).filter(LearningGoal.user_id == student.id).all()}
        goals_data = [
            ("Solve 50 Medium DSA Problems", "PROGRAMMING", "QUESTIONS_COUNT", 50, 32, "IN_PROGRESS", 30),
            ("Master Quantitative Aptitude for Day-1 Drives", "QUANTITATIVE_APTITUDE", "QUESTIONS_COUNT", 100, 78, "IN_PROGRESS", 45),
            ("Complete Core CS Interview Syllabus", "CORE_TECHNICAL", "MINUTES_PRACTICED", 1200, 1200, "COMPLETED", -5),
            ("Revise All Mistake Notebook Items", "GENERAL", "QUESTIONS_COUNT", 15, 12, "IN_PROGRESS", 14),
        ]
        for title, category, t_type, target, current, status, target_days in goals_data:
            if title not in existing_goals:
                goal = LearningGoal(
                    user_id=student.id,
                    title=title,
                    category=category,
                    target_type=t_type,
                    target_value=target,
                    current_value=current,
                    status=status,
                    deadline=now + timedelta(days=target_days),
                )
                db.add(goal)
        db.flush()

        # 4. Roadmap Career Goal & Topic Progress
        sde_path = db.query(CareerPath).filter(CareerPath.code == "SDE").first()
        if sde_path:
            cgoal = db.query(StudentCareerGoal).filter(StudentCareerGoal.user_id == student.id).first()
            if not cgoal:
                cgoal = StudentCareerGoal(
                    user_id=student.id,
                    career_path_id=sde_path.id,
                    status="ACTIVE",
                    target_date=now + timedelta(days=90),
                )
                db.add(cgoal)
            db.flush()

            topics = db.query(RoadmapTopic).join(RoadmapSubject).filter(RoadmapSubject.career_path_id == sde_path.id).all()
            for idx, top in enumerate(topics):
                prog = db.query(StudentTopicProgress).filter(
                    StudentTopicProgress.user_id == student.id,
                    StudentTopicProgress.topic_id == top.id,
                ).first()
                if not prog:
                    if idx == 0:  # Variables & Control Flow
                        pct, status_val, attempted, correct, dsa_s, res_c = 100, "COMPLETED", 15, 14, 2, 1
                    elif idx == 1:  # Functions & Recursion
                        pct, status_val, attempted, correct, dsa_s, res_c = 75, "IN_PROGRESS", 12, 10, 2, 1
                    elif idx == 2:  # OOP
                        pct, status_val, attempted, correct, dsa_s, res_c = 50, "IN_PROGRESS", 8, 6, 1, 0
                    elif idx == 3:  # Arrays & Strings
                        pct, status_val, attempted, correct, dsa_s, res_c = 85, "IN_PROGRESS", 20, 17, 3, 1
                    else:
                        pct, status_val, attempted, correct, dsa_s, res_c = 0, "NOT_STARTED", 0, 0, 0, 0

                    prog = StudentTopicProgress(
                        user_id=student.id,
                        topic_id=top.id,
                        status=status_val,
                        completion_percentage=pct,
                        questions_attempted=attempted,
                        questions_correct=correct,
                        coding_problems_solved=dsa_s,
                        resources_completed=res_c,
                        last_activity_at=now - timedelta(days=idx),
                    )
                    db.add(prog)
            db.flush()

        # 5. DSA Problem User Progress & Submissions
        dsa_problems = db.query(DSAProblem).all()
        for i, prob in enumerate(dsa_problems):
            prog = db.query(DSAUserProgress).filter(
                DSAUserProgress.user_id == student.id,
                DSAUserProgress.problem_id == prob.id,
            ).first()
            if not prog:
                if i in [0, 1, 2]:  # Solved problems
                    status_val = "SOLVED"
                    solved_at = now - timedelta(days=3 - i)
                    attempts = i + 1
                    prog = DSAUserProgress(
                        user_id=student.id,
                        problem_id=prob.id,
                        status=status_val,
                        attempts_count=attempts,
                        solved_at=solved_at,
                        last_attempted_at=solved_at,
                        best_runtime_ms=35 + (i * 12),
                    )
                    db.add(prog)

                    py_code = prob.starter_code.get('python') if isinstance(prob.starter_code, dict) else (prob.starter_code or "def solve():\n    return True\n")
                    # Add submission record
                    sub = DSASubmission(
                        user_id=student.id,
                        problem_id=prob.id,
                        language="python",
                        code=py_code,
                        verdict="ACCEPTED",
                        test_cases_passed=3,
                        total_test_cases=3,
                        runtime_ms=35 + (i * 12),
                        memory_kb=16400,
                        submitted_at=solved_at,
                    )
                    db.add(sub)
                elif i == 3:  # Attempted problem
                    prog = DSAUserProgress(
                        user_id=student.id,
                        problem_id=prob.id,
                        status="ATTEMPTED",
                        attempts_count=2,
                        last_attempted_at=now - timedelta(hours=5),
                    )
                    db.add(prog)
                    py_code = prob.starter_code.get('python') if isinstance(prob.starter_code, dict) else (prob.starter_code or "def solve():\n    pass\n")
                    sub = DSASubmission(
                        user_id=student.id,
                        problem_id=prob.id,
                        language="python",
                        code=py_code,
                        verdict="WRONG_ANSWER",
                        test_cases_passed=1,
                        total_test_cases=3,
                        error_message="Output mismatch on Test Case 2: Expected [0,1], Got []",
                        submitted_at=now - timedelta(hours=5),
                    )
                    db.add(sub)
            db.flush()

        # 6. Mistake Notebook Entries
        sess = db.query(PracticeSession).filter(PracticeSession.user_id == student.id).first()
        if not sess:
            sess = PracticeSession(
                user_id=student.id,
                session_type="PRACTICE",
                status="SUBMITTED",
                time_spent_seconds=1200,
                total_score=60.0,
                max_score=100.0,
                started_at=now - timedelta(days=6),
                completed_at=now - timedelta(days=6, minutes=-20),
            )
            db.add(sess)
            db.flush()

        questions = db.query(Question).limit(6).all()
        for idx, q in enumerate(questions):
            m_entry = db.query(MistakeNotebookEntry).filter(
                MistakeNotebookEntry.user_id == student.id,
                MistakeNotebookEntry.question_id == q.id,
            ).first()
            if not m_entry:
                if idx == 0:
                    status_val = "UNRESOLVED"
                    notes = "Confused between O(N) auxiliary space and in-place swapping."
                    tag = "CONCEPTUAL"
                elif idx == 1:
                    status_val = "REVIEWED"
                    notes = "Remember to handle null head and single node edge case."
                    tag = "EDGE_CASE"
                elif idx == 2:
                    status_val = "MASTERED"
                    notes = "Solved correctly on second attempt. LCM technique works cleanly."
                    tag = "CALCULATION"
                else:
                    status_val = "UNRESOLVED"
                    notes = "Misread question constraint: 1-indexed vs 0-indexed."
                    tag = "INTERPRETATION"

                wrong_opt = next((o.option_text for o in q.options if not o.is_correct), "B")
                
                # Check for attempt record or create one
                attempt = db.query(AttemptRecord).filter(
                    AttemptRecord.session_id == sess.id,
                    AttemptRecord.question_id == q.id,
                ).first()
                if not attempt:
                    attempt = AttemptRecord(
                        session_id=sess.id,
                        user_id=student.id,
                        question_id=q.id,
                        submitted_answer=wrong_opt,
                        is_correct=False,
                        score_awarded=0.0,
                        time_spent_ms=45000,
                        submitted_at=now - timedelta(days=5 - idx),
                    )
                    db.add(attempt)
                    db.flush()

                m_entry = MistakeNotebookEntry(
                    user_id=student.id,
                    attempt_id=attempt.id,
                    question_id=q.id,
                    student_notes=notes,
                    error_tag=tag,
                    mastery_status=status_val,
                    created_at=now - timedelta(days=5 - idx),
                    resolved_at=now - timedelta(days=1) if status_val == "MASTERED" else None,
                )
                db.add(m_entry)
        db.flush()

        # 7. Auditable Student Behavior Events (Cadence & Regularity)
        existing_event_count = db.query(StudentBehaviorEvent).filter(StudentBehaviorEvent.user_id == student.id).count()
        if existing_event_count < 10:
            events_data = [
                ("SESSION_START", "PREPARATION_PORTAL", 0, 7),
                ("RESOURCE_OPENED", "LEARNING_MATERIAL", 120, 7),
                ("RESOURCE_COMPLETED", "LEARNING_MATERIAL", 300, 7),
                ("SESSION_COMPLETE", "PREPARATION_PORTAL", 1800, 7),
                ("SESSION_START", "PREPARATION_PORTAL", 0, 5),
                ("PRACTICE_ATTEMPT", "DIAGNOSTIC_ASSESSMENT", 600, 5),
                ("SESSION_COMPLETE", "PREPARATION_PORTAL", 2400, 5),
                ("SESSION_START", "PREPARATION_PORTAL", 0, 3),
                ("CODING_SUBMIT", "DSA_STUDIO", 900, 3),
                ("MISTAKE_REVIEWED", "REVISION", 400, 2),
                ("SESSION_START", "PREPARATION_PORTAL", 0, 1),
                ("TOPIC_SWITCH", "ROADMAP", 60, 1),
                ("RESOURCE_COMPLETED", "LEARNING_MATERIAL", 450, 1),
                ("CODING_SUBMIT", "DSA_STUDIO", 750, 1),
                ("SESSION_COMPLETE", "PREPARATION_PORTAL", 3600, 1),
            ]
            for ev_type, cat, dur, days_ago in events_data:
                ev = StudentBehaviorEvent(
                    user_id=student.id,
                    event_type=ev_type,
                    category=cat,
                    duration_seconds=dur,
                    created_at=now - timedelta(days=days_ago, minutes=dur // 60),
                )
                db.add(ev)
            db.flush()

        # 8. Placement Outcome & Company Offers
        existing_outcome = db.query(PlacementOutcome).filter(PlacementOutcome.user_id == student.id).first()
        if not existing_outcome:
            outcome = PlacementOutcome(
                user_id=student.id,
                company_name="Amazon Web Services",
                job_title="Associate Cloud Engineer",
                tier="TIER_1_PRODUCT",
                ctc_lpa=14.50,
                verification_status="OFFICIALLY_VERIFIED",
                offer_date=(now - timedelta(days=14)).date(),
            )
            db.add(outcome)
            db.flush()

        # 9. Training Program Attendance
        trainings = db.query(TrainingProgram).limit(3).all()
        for idx, tr in enumerate(trainings):
            sess = db.query(TrainingSession).filter(TrainingSession.program_id == tr.id).first()
            if not sess:
                sess = TrainingSession(
                    program_id=tr.id,
                    session_date=(now - timedelta(days=7 * (idx + 1))).date(),
                    start_time="10:00 AM",
                    duration_minutes=90,
                    topic_covered=f"{tr.domain} Intensive Masterclass",
                    trainer_notes="Active student participation and problem-solving practice.",
                )
                db.add(sess)
                db.flush()

            att = db.query(TrainingAttendance).filter(
                TrainingAttendance.session_id == sess.id,
                TrainingAttendance.user_id == student.id,
            ).first()
            if not att:
                att = TrainingAttendance(
                    session_id=sess.id,
                    user_id=student.id,
                    attendance_status="PRESENT",
                )
                db.add(att)
        # 10. Cohort-Wide Enrichment (Populate profiles & outcomes for other students in college)
        all_students = db.query(User).filter(User.institution_id == inst_id, User.role == "STUDENT").all()
        print(f"Enriching cohort data for {len(all_students)} students in institution...")

        companies = [
            ("Microsoft IDC", "Software Engineer", "TIER_1_PRODUCT", 21.5),
            ("Google Cloud", "Associate Cloud Consultant", "TIER_1_PRODUCT", 24.0),
            ("Oracle Systems", "Server Technology Intern / MTS", "TIER_1_PRODUCT", 18.0),
            ("Cisco Systems", "Software Engineer - Networking", "TIER_1_PRODUCT", 16.5),
            ("Zoho Corporation", "Software Developer", "TIER_2_TECH", 8.5),
            ("ThoughtWorks", "Application Developer", "TIER_2_TECH", 10.0),
            ("TCS Digital", "Systems Engineer", "TIER_2_TECH", 7.5),
            ("Infosys Specialist Programmer", "Power Programmer", "TIER_2_TECH", 9.5),
            ("Cognizant GenC Next", "Associate Software Engineer", "TIER_2_TECH", 6.8),
            ("Wipro Turbo", "Project Engineer", "MASS_IT", 6.5),
            ("Accenture Solutions", "Advanced Associate Software Engineer", "TIER_2_TECH", 6.5),
            ("LTIMindtree", "Software Engineer", "MASS_IT", 5.0),
        ]

        for s_idx, st in enumerate(all_students):
            st_prof = db.query(StudentProfile).filter(StudentProfile.user_id == st.id).first()
            cgpa_val = round(7.0 + ((s_idx * 17) % 28) * 0.1, 2)
            roll_no = f"26CSE{str(s_idx + 1).zfill(3)}"
            pl_status = "PLACED" if (s_idx % 3 != 0) else ("IN_PROCESS" if s_idx % 2 == 0 else "NOT_PLACED")

            if not st_prof:
                st_prof = StudentProfile(
                    user_id=st.id,
                    cohort_id=cohort.id if cohort else None,
                    roll_number=roll_no,
                    cgpa=cgpa_val,
                    placement_status=pl_status,
                )
                db.add(st_prof)
            else:
                if not st_prof.cohort_id and cohort:
                    st_prof.cohort_id = cohort.id
                st_prof.cgpa = cgpa_val
                st_prof.placement_status = pl_status

            # If placed, ensure a verified placement outcome exists
            if pl_status == "PLACED":
                c_info = companies[s_idx % len(companies)]
                p_out = db.query(PlacementOutcome).filter(PlacementOutcome.user_id == st.id).first()
                if not p_out:
                    p_out = PlacementOutcome(
                        user_id=st.id,
                        company_name=c_info[0],
                        job_title=c_info[1],
                        tier=c_info[2],
                        ctc_lpa=c_info[3],
                        verification_status="OFFICIALLY_VERIFIED",
                        offer_date=(now - timedelta(days=10 + (s_idx % 60))).date(),
                    )
                    db.add(p_out)

            # Ensure student has preparation activity
            act_count = db.query(PreparationActivity).filter(PreparationActivity.user_id == st.id).count()
            if act_count == 0:
                act = PreparationActivity(
                    user_id=st.id,
                    activity_type="PRACTICE_SESSION",
                    category="PROGRAMMING",
                    topic="Coding Problem Solving Drills",
                    duration_minutes=45 + ((s_idx * 15) % 90),
                    completion_state="COMPLETED",
                    provenance="SYSTEM_EVALUATED",
                    notes="Completed algorithmic practice problem sets.",
                    activity_date=now - timedelta(days=(s_idx % 14)),
                )
                db.add(act)

        db.flush()
        db.commit()
        print("Rich cohort & student data populated successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error populating rich student data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_rich_data()
