import sys
import os
import json
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "http://127.0.0.1:8000/api/v1"

def api_call(path, method="GET", data=None, token=None, form_encoded=False):
    url = f"{BASE_URL}{path}"
    headers = {}
    body = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        if form_encoded:
            body = urllib.parse.urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code} on {path}: {err_body}")
        raise e

# 1. Login
login_data = api_call("/auth/login", method="POST", data={"email": "student@college.edu", "password": "Password@123"})
token = login_data["access_token"]
print("Login successful.")

# 2. Get Roadmap Tree
paths = api_call("/roadmap/career-paths", token=token)
print(f"Total Career Paths available: {len(paths)}")
for p in paths:
    p_tree = api_call(f"/roadmap/tree?career_path_id={p['id']}", token=token)
    p_topics = [t for s in p_tree["subjects"] for t in s["topics"]]
    p_with_ass = [t for t in p_topics if t.get("assessment_id")]
    print(f"Path: '{p['title']}' ({p['code']}): {len(p_with_ass)}/{len(p_topics)} topics linked to Assessments")
    if len(p_with_ass) != len(p_topics):
        print(f"ERROR: Not all topics in {p['title']} have assessment_id!")
        sys.exit(1)

all_topics = [t for s in p_tree["subjects"] for t in s["topics"]]

# 3. Test topic detail for topics
for t in all_topics[:4]:
    d = api_call(f"/roadmap/topics/{t['id']}", token=token)
    ass = d.get("assessment")
    if not ass:
        print(f"ERROR: No assessment returned for {t['name']}!")
        sys.exit(1)
    qs = d.get("practice_questions", [])
    print(f"\nTopic: {d['name']}")
    print(f" - Assessment: {ass['title']} ({ass['questions_count']} questions, {ass['duration_minutes']} min)")
    print(f" - Practice Questions Returned: {len(qs)}")
    for q in qs:
        print(f"   * {q['title']} [{q['difficulty']}]")

# 4. Start Practice Session with assessment of first topic
first_ass_id = all_topics[0]["assessment_id"]
session = api_call("/practice/sessions", method="POST", data={
    "assessment_id": first_ass_id,
    "session_type": "PRACTICE"
}, token=token)

print(f"\nSuccessfully started Practice Session: ID {session.get('session_id')}, Assessment: {session.get('assessment_title')}")
print("ALL E2E CHECKS PASSED PERFECTLY!")
