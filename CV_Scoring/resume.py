import os
import time
import json
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import uuid

PARSED_RESUMES_PATH = "./candidates/parsed_resumes.json"
API_ENDPOINT = "http://localhost:8000/api/candidates/"

def parse_pdf(data):
    parsed = data.copy()  # Create a copy to avoid modifying original data
    parsed['email'] = parsed.get('email', '').lower().strip()  # Normalize email
    parsed['name'] = parsed.get('name', 'Unknown').strip()
    parsed['phone'] = parsed.get('phone', '').strip()
    parsed['github'] = parsed.get('github', None)
    parsed['linkedin'] = parsed.get('linkedin', None)

    # Handle education
    if 'education' in parsed:
        education = parsed['education']
        if isinstance(education, dict):
            if isinstance(education.get('degree'), list) and isinstance(education.get('year'), list):
                # Handle lists for degree and year
                degrees = education.get('degree', [])
                years = education.get('year', [])
                parsed['educations'] = [{
                    'university_name': education.get('institute', '') or '',
                    'degree_name': degrees[i] if i < len(degrees) else '',
                    'start_year': years[i] if i < len(years) else '',
                    'end_year': education.get('end_year', '') or ''
                } for i in range(max(len(degrees), len(years)))]
            else:
                parsed['educations'] = [{
                    'university_name': education.get('institute', '') or '',
                    'degree_name': education.get('degree', '') or '',
                    'start_year': education.get('year', '') or '',
                    'end_year': education.get('end_year', '') or ''
                }]
        elif isinstance(education, list):
            parsed['educations'] = [{
                'university_name': edu.get('institute', '') or '' if isinstance(edu, dict) else str(edu),
                'degree_name': edu.get('degree', '') or '' if isinstance(edu, dict) else '',
                'start_year': edu.get('year', '') or '' if isinstance(edu, dict) else '',
                'end_year': edu.get('end_year', '') or '' if isinstance(edu, dict) else ''
            } for edu in education]
        else:
            parsed['educations'] = []
        parsed.pop('education', None)
    else:
        parsed['educations'] = []

    # Handle skills
    if parsed.get('skills') == 'Not found':
        parsed['soft_skills'] = ''
        parsed['technical_skills'] = ''
        parsed.pop('skills', None)
    elif isinstance(parsed.get('skills'), dict):
        parsed['soft_skills'] = json.dumps(parsed['skills'].get('soft_skills', {}))
        parsed['technical_skills'] = json.dumps(parsed['skills'].get('technical_skills', {}))
        parsed.pop('skills', None)
    else:
        parsed['soft_skills'] = ''
        parsed['technical_skills'] = ''
        parsed.pop('skills', None)

    # Handle years_of_experience
    try:
        parsed['years_of_experience'] = float(parsed.get('years_of_experience', 0.0))
        if parsed['years_of_experience'] > 100:  # Likely a year like 2022.0
            print(f"⚠️ Invalid years_of_experience {parsed['years_of_experience']} for {parsed['email']}, setting to 0.0")
            parsed['years_of_experience'] = 0.0
    except (ValueError, TypeError):
        print(f"⚠️ Invalid years_of_experience format for {parsed['email']}, setting to 0.0")
        parsed['years_of_experience'] = 0.0

    # Map phone to phone_number
    if 'phone' in parsed:
        parsed['phone_number'] = parsed['phone']
        parsed.pop('phone', None)

    # Remove file field
    parsed.pop('file', None)

    # Add default summary if missing
    if 'summary' not in parsed:
        parsed['summary'] = ''

    # Handle 'Not found' values
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

    # Add unique request_id
    parsed['request_id'] = str(uuid.uuid4())

    return parsed

class ResumeChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified_time = None

    def on_modified(self, event):
        if event.src_path.endswith("parsed_resumes.json"):
            current_time = os.path.getmtime(event.src_path)
            if self.last_modified_time is None or current_time != self.last_modified_time:
                print(f"📄 Detected change in {event.src_path}")
                self.last_modified_time = current_time
                self.process_file()

    def process_file(self):
        try:
            with open(PARSED_RESUMES_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                print("❌ Invalid format: Expected list of candidates")
                return

            for candidate in data:
                parsed = parse_pdf(candidate)
                email = parsed.get('email', '').strip().lower()
                if not email or email == '':
                    print(f"⚠️ Skipping candidate without valid email: {parsed.get('name', 'Unknown')}")
                    continue

                print(f"📤 Sending candidate: {parsed.get('name', 'Unknown')} ({email})")
                response = requests.post(API_ENDPOINT, json=parsed)
                if response.status_code in (200, 201):
                    print(f"✅ Successfully posted: {parsed.get('name')} ({email})")
                else:
                    print(f"❌ Failed to post {parsed.get('name')} ({email}): {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Error reading/sending JSON: {e}")

if __name__ == "__main__":
    path = os.path.dirname(PARSED_RESUMES_PATH)
    event_handler = ResumeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()

    print(f"👀 Watching for changes in: {PARSED_RESUMES_PATH}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping watcher...")
        observer.stop()
    observer.join()