from celery import shared_task
import os
import requests
import logging
import json
from collections import defaultdict
from .models import MediaUpload, JobDetail ,Feedback

logger = logging.getLogger(__name__)

@shared_task
def parse_cv_task():
    valid_extensions = ['.pdf', '.docx', '.doc']

    try:
        logger.info("Checking for unprocessed CVs...")
        all_unprocessed = MediaUpload.objects.filter(processed=False)

        # Filter CVs with valid extensions
        unprocessed_cvs = [
            media for media in all_unprocessed
            if os.path.splitext(os.path.basename(media.cv.name))[1].lower() in valid_extensions
        ]
        logger.info(f"Found {len(unprocessed_cvs)} unprocessed valid CV(s)")

        # Group CVs by job_id
        job_groups = defaultdict(list)
        for media in unprocessed_cvs:
            job_groups[media.job_id].append(media)

        for job_id, media_list in job_groups.items():
            logger.info(f"Processing Job ID: {job_id} with {len(media_list)} CV(s)")

            # 1. Send Job Info once
            try:
                job = JobDetail.objects.get(pk=job_id)

                job_json = [{
                    "title": job.role,
                    "level": job.experience_level,
                    "employment_type": job.job_type,
                    "location": job.location,
                    "location_type": "Remote" if job.location.lower() == "remote" else "On-site",
                    "required_skills": {
                        "technical_skills": {
                            skill.strip(): 3 for skill in job.skills.split(",") if skill.strip()
                        },
                        "soft_skills": {
                            "Communication": 5,
                            "Creativity": 4,
                            "Leadership": 4,
                            "Strategic Thinking": 4
                        }
                    },
                    "experience": job.experience_level,
                    "education_level": job.education_level,
                    "salary_range": f"{job.salary_currency} {job.salary}" if job.salary else "Not Disclosed",
                    "important_skills": [s.strip() for s in job.skills.split(",")[:3]]
                }]

                job_response = requests.post(
                    f"http://fastapi:5000/job?jobId={job_id}",
                    json=job_json,
                    timeout=30
                )

                if job_response.status_code == 200:
                    logger.info(f"✅ Job details sent for Job ID {job_id}")
                else:
                    logger.warning(f"⚠️ Failed to send job details for Job ID {job_id}. Response: {job_response.text}")

            except JobDetail.DoesNotExist:
                logger.error(f"❌ JobDetail with ID {job_id} not found. Skipping CVs for this job.")
                continue

            # 2. Send CVs for this job
            for media in media_list:
                try:
                    file_extension = os.path.splitext(os.path.basename(media.cv.name))[1].lower()
                    renamed_file = f"{job_id}_{media.media_id}{file_extension}"

                    with open(media.cv.path, 'rb') as f:
                        files = {'files': (renamed_file, f, media.file_type)}
                        response = requests.post(
                            "http://fastapi:5000/upload",
                            files=files,
                            timeout=30
                        )

                    logger.info(f"Parser response status: {response.status_code}")
                    logger.debug(f"Parser response body: {response.text}")

                    if response.status_code == 200:
                        logger.info(f"✅ CV {media.media_id} sent successfully for Job {job_id}")
                    else:
                        logger.warning(f"⚠️ Failed to send CV {media.media_id} for Job {job_id}. Response: {response.text}")

                except Exception as e:
                    logger.error(f"❌ Error sending CV {media.media_id} for Job {job_id}: {e}")

                media.processed = True
                media.save()
                logger.info(f"CV {media.media_id} marked as processed")

        # 3. Send unprocessed feedbacks
        logger.info("Checking for unprocessed feedback...")
        unprocessed_feedbacks = Feedback.objects.filter(processed=False)
        for fb in unprocessed_feedbacks:
            try:
                response = requests.post(
                    "http://fastapi:5000/feedback",
                    data=json.dumps(fb.text),
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )

                if response.status_code == 200:
                    fb.processed = True
                    fb.save()
                    logger.info(f"✅ Feedback sent and marked as processed: {fb.text}")
                else:
                    logger.warning(f"⚠️ Failed to send feedback: {fb.text}. Response: {response.text}")
            except Exception as e:
                logger.error(f"❌ Error sending feedback: {str(e)}")

    except Exception as e:
        logger.error(f"🔥 Fatal error in parse_cv_task: {str(e)}")