# backend/user/tasks.py

from celery import shared_task
import time
from .models import MediaUpload, Candidate

@shared_task
def parse_cv_task(media_id):
    try:
        media = MediaUpload.objects.get(id=media_id)
        file_path = media.cv.path

        # Simulate delay
        time.sleep(5)

        # Fake parsed output
        parsed_data = {
            "name": "Hamza Nadeem",
            "email": "hamzaadeem@gmail.com",
            "phone_number": "+7586926179",
            "linkedin": "http://sampson-foley.com/",
            "github": "https://sanders.com/",
            "soft_skills": "time management, creativity, communication, teamwork",
            "technical_skills": "Docker, Git, Python, React",
            "summary": "Skilled in Docker, Git, Python, and React, with excellent time management, creativity, communication, and teamwork skills."
        }

        Candidate.objects.create(
            name=parsed_data['name'],
            email=parsed_data['email'],
            phone_number=parsed_data['phone_number'],
            linkedin = parsed_data['linkedin'],
            github = parsed_data['github'],
            soft_skills=parsed_data['soft_skills'],
            technical_skills = parsed_data['technical_skills'],
            summary = parsed_data['summary']
        )
    except MediaUpload.DoesNotExist:
        print(f"MediaUpload with ID {media_id} not found.")
