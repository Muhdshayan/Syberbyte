import os
import time
import json
import uuid
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

RESUME_DIR = "./candidates"
SCORE_DIR = "./scores"
CANDIDATE_ENDPOINT = "http://localhost:8000/api/candidates/"
JOBAPPLICATION_ENDPOINT = "http://localhost:8000/api/jobapplication/"

sent_candidates = []  # Store candidate names + IDs after successful POSTs


def parse_pdf(data):
    parsed = data.copy()
    parsed['email'] = parsed.get('email', '').lower().strip()
    parsed['name'] = parsed.get('name', 'Unknown').strip()
    parsed['phone'] = parsed.get('phone', '').strip()
    parsed['github'] = parsed.get('github', None)
    parsed['linkedin'] = parsed.get('linkedin', None)

    # Handle education
    if 'education' in parsed:
        education = parsed['education']
        if isinstance(education, dict):
            if isinstance(education.get('degree'), list) and isinstance(education.get('year'), list):
                degrees = education.get('degree', [])
                years = education.get('year', [])
                parsed['educations'] = [{
                    'university_name': education.get('institute', ''),
                    'degree_name': degrees[i] if i < len(degrees) else '',
                    'start_year': years[i] if i < len(years) else '',
                    'end_year': education.get('end_year', '')
                } for i in range(max(len(degrees), len(years)))]
            else:
                parsed['educations'] = [{
                    'university_name': education.get('institute', ''),
                    'degree_name': education.get('degree', ''),
                    'start_year': education.get('year', ''),
                    'end_year': education.get('end_year', '')
                }]
        elif isinstance(education, list):
            parsed['educations'] = [{
                'university_name': edu.get('institute', '') if isinstance(edu, dict) else str(edu),
                'degree_name': edu.get('degree', '') if isinstance(edu, dict) else '',
                'start_year': edu.get('year', '') if isinstance(edu, dict) else '',
                'end_year': edu.get('end_year', '') if isinstance(edu, dict) else ''
            } for edu in education]
        parsed.pop('education', None)
    else:
        parsed['educations'] = []

    # Handle skills
    if parsed.get('skills') == 'Not found':
        parsed['soft_skills'] = ''
        parsed['technical_skills'] = ''
    elif isinstance(parsed.get('skills'), dict):
        parsed['soft_skills'] = json.dumps(parsed['skills'].get('soft_skills', {}))
        parsed['technical_skills'] = json.dumps(parsed['skills'].get('technical_skills', {}))
    else:
        parsed['soft_skills'] = ''
        parsed['technical_skills'] = ''
    parsed.pop('skills', None)

    # Handle years_of_experience
    try:
        parsed['years_of_experience'] = float(parsed.get('years_of_experience', 0.0))
        if parsed['years_of_experience'] > 100:
            parsed['years_of_experience'] = 0.0
    except (ValueError, TypeError):
        parsed['years_of_experience'] = 0.0

    # Phone remap
    parsed['phone_number'] = parsed.pop('phone', None)

    # Defaults
    parsed.pop('file', None)
    parsed['summary'] = parsed.get('summary', '')
    if parsed.get('github') == 'Not found':
        parsed['github'] = None
    if parsed.get('linkedin') == 'Not found':
        parsed['linkedin'] = None
    if parsed.get('name') == 'Name Not Found':
        parsed['name'] = ''
    if parsed.get('email') == 'Not found':
        parsed['email'] = ''
    if parsed.get('phone_number') == 'Not found':
        parsed['phone_number'] = None

    parsed['request_id'] = str(uuid.uuid4())
    return parsed


def post_json_data(endpoint, file_path):
    try:
        if os.path.getsize(file_path) == 0:
            print(f"⚠️ Skipped empty file: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not data:
            print(f"⚠️ Empty or invalid JSON in {file_path}")
            return

        # === CANDIDATES ===
        if endpoint == CANDIDATE_ENDPOINT:
            candidates = data if isinstance(data, list) else [data]

            for raw_candidate in candidates:
                candidate = parse_pdf(raw_candidate)
                name = candidate.get('name')
                print(f"📤 Posting candidate: {name} to {endpoint}")
                resp = requests.post(endpoint, json=candidate)

                if resp.status_code == 201:
                    candidate_id = resp.json().get('candidate_id')
                    print(f"🆔 Created Candidate: {name} → ID {candidate_id}")
                elif resp.status_code == 400:
                    candidate_id = resp.json().get('candidate_id')
                    if candidate_id:
                        print(f"🆔 Existing Candidate: {name} → ID {candidate_id}")
                    else:
                        print(f"❌ Error: {resp.json()}")
                        continue
                else:
                    print(f"❌ Failed: {resp.status_code} → {resp.text}")
                    continue

                # Store in sent_candidates
                sent_candidates.append({
                    "name": name.strip(),
                    "candidate_id": candidate_id
                })

        # === JOB APPLICATIONS ===
        elif endpoint == JOBAPPLICATION_ENDPOINT:
            top_candidates = data.get("top_5_candidates", [])
            if not top_candidates:
                print(f"⚠️ No top_5_candidates found in {file_path}")
                return

            # Build lookup from sent_candidates
            candidate_lookup = {
                entry['name'].strip().lower(): entry['candidate_id']
                for entry in sent_candidates
            }

            for c in top_candidates:
                name_key = c.get("candidate_name", "").strip().lower()
                candidate_id = candidate_lookup.get(name_key)

                if not candidate_id:
                    print(f"❌ Candidate '{name_key}' not found in sent_candidates")
                    continue

                payload = {
                    "candidate_id": candidate_id,
                    "job_id": c.get("job_id"),
                    "media_id": c.get("media_id"),
                    "score": c.get("overall_score"),
                    "ai_recommendation": True,
                    "technical_score": c["component_scores"].get("technical_score"),
                    "experience_score": c["component_scores"].get("experience_score"),
                    "cultural_score": c["component_scores"].get("cultural_score"),
                }

                print(f"📤 Posting application for {name_key} (ID: {candidate_id})")
                resp = requests.post(endpoint, json=payload)
                print(f"✅ Status: {resp.status_code} → {resp.text}")

    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON in: {file_path}")
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")


class ResumeScoreHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            if RESUME_DIR in event.src_path:
                print(f"📥 Resume updated: {event.src_path}")
                post_json_data(CANDIDATE_ENDPOINT, event.src_path)
            elif SCORE_DIR in event.src_path:
                print(f"📥 Score updated: {event.src_path}")
                post_json_data(JOBAPPLICATION_ENDPOINT, event.src_path)


def main():
    os.makedirs(RESUME_DIR, exist_ok=True)
    os.makedirs(SCORE_DIR, exist_ok=True)

    observer = Observer()
    handler = ResumeScoreHandler()
    observer.schedule(handler, path=RESUME_DIR, recursive=False)
    observer.schedule(handler, path=SCORE_DIR, recursive=False)

    observer.start()
    print("👀 Watching for changes in ./candidates and ./scores ... Press CTRL+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping watcher...")
        print("📋 Final sent_candidates list:")
        for entry in sent_candidates:
            print(f"  🔹 {entry['name']} → ID {entry['candidate_id']}")
        observer.stop()
    observer.join()

def main():
    os.makedirs(RESUME_DIR, exist_ok=True)
    os.makedirs(SCORE_DIR, exist_ok=True)

    observer = Observer()
    handler = ResumeScoreHandler()
    observer.schedule(handler, path=RESUME_DIR, recursive=False)
    observer.schedule(handler, path=SCORE_DIR, recursive=False)

    observer.start()
    print("👀 Watching for changes in ./candidates and ./scores ... Press CTRL+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping watcher...")
        print("📋 Final sent_candidates list:")
        for entry in sent_candidates:
            print(f"  🔹 {entry['name']} → ID {entry['candidate_id']}")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()