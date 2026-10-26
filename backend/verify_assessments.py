import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.roadmap import RoadmapTopic
from app.models.assessment import Assessment, AssessmentQuestion

db = SessionLocal()
topics = db.query(RoadmapTopic).all()
print(f"Total topics: {len(topics)}")

min_q = 999
all_ok = True
for t in topics:
    if not t.assessment_id:
        print(f"ERROR: Topic {t.name} has no assessment_id!")
        all_ok = False
        continue
    ass = db.query(Assessment).filter(Assessment.id == t.assessment_id).first()
    if not ass:
        print(f"ERROR: Assessment {t.assessment_id} not found for {t.name}!")
        all_ok = False
        continue
    q_count = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == ass.id).count()
    if q_count < 3:
        print(f"WARNING: Topic {t.name} has only {q_count} questions in {ass.title}!")
        all_ok = False
    if q_count < min_q:
        min_q = q_count

print(f"All 35 topics verified: {all_ok}. Minimum questions per topic: {min_q}")
db.close()
