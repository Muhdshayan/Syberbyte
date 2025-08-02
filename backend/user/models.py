from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator,RegexValidator
import os
from django.utils.text import slugify

class UserAccount(models.Model):
    ROLE_CHOICES = [
        ('full_admin', 'Full Admin'),
        ('basic_admin', 'Basic Admin'),
        ('advanced_admin', 'Advanced Admin'),
        ('hr_manager', 'HR Manager'),
        ('recruiter', 'Recruiter'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Suspended', 'Suspended'),
    ]
    PERMISSION_CHOICES = [(i, str(i)) for i in range(1, 11)]  # 1 to 10

    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permission = models.IntegerField(choices=PERMISSION_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(10)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}"
    


class JobDetail(models.Model):

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Suspended', 'Suspended'),
    ]

    job_id = models.AutoField(primary_key=True)
    industry = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    description = models.TextField(help_text="Description of Role")
    location = models.CharField(max_length=100, default="Remote")
    job_type = models.CharField(max_length=50, choices=[("Full-time", "Full-time"), ("Part-time", "Part-time"), ("Contract", "Contract")])
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default="USD")
    salary_period = models.CharField(max_length=20, choices=[("year", "Per Year"), ("month", "Per Month")], default="year")
    
    education_level = models.CharField(max_length=255, help_text="Education Level Requirement")
    skills = models.TextField(help_text="Skills, Technologies and Certifications Requirement")  # comma-separated or JSON
    experience_level = models.CharField(max_length=255, help_text="Experience Level Requirement")

    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')


    posted_by = models.ForeignKey(
        'UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'hr_manager'},
        related_name='posted_by',
        help_text="Assign this job to an HR Manager"
    )

    assigned_to = models.ForeignKey(
        'UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'recruiter'},
        related_name='assigned_jobs',
        help_text="Assign this job to a Recruiter"
    )

    def __str__(self):
        return self.role
    

class Education(models.Model):
    education_id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='educations')
    degree_name = models.CharField(max_length=255, blank=True, help_text="Name of the degree (e.g., Bachelor's in Computer Science)")
    university_name = models.CharField(max_length=255, blank=True, help_text="Name of the university or institution")
    start_year = models.CharField(max_length=50, blank=True, help_text="Start year of education (e.g., '2020' or 'Present')")
    end_year = models.CharField(max_length=50, blank=True, null=True, help_text="End year of education (e.g., '2024' or 'Ongoing')")

    def __str__(self):
        return f"{self.degree_name} at {self.university_name} ({self.start_year} - {self.end_year or 'Ongoing'})"
    

def cv_upload_path(instance, filename):
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"[cv_upload_path] Raw filename: {filename} (type: {type(filename)})")

    if callable(filename):
        logger.warning(f"[cv_upload_path] filename is callable. Converting to string.")
        filename = str(filename())

    if not isinstance(filename, str):
        logger.warning(f"[cv_upload_path] filename is not a string. Forcing to str.")
        filename = str(filename)

    try:
        job = JobDetail.objects.get(job_id=instance.job_id)
        title_slug = slugify(job.role)
    except JobDetail.DoesNotExist:
        logger.warning(f"[cv_upload_path] JobDetail with job_id={instance.job_id} not found. Using 'unknown'")
        title_slug = "unknown"

    path = os.path.join('cvs', title_slug, filename)
    logger.info(f"[cv_upload_path] Final upload path: {path}")
    return path


class MediaUpload(models.Model):
    media_id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=100)
    cv = models.FileField(upload_to=cv_upload_path) 
    file_type = models.CharField(max_length=10)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.cv.name} for Job {self.job_id}"


class Candidate(models.Model):
    candidate_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+1234567890'. Up to 15 digits allowed."
            )
        ],
        help_text="Phone number in format: +1234567890"
    )
    linkedin = models.URLField(max_length=200, blank=True, null=True, help_text="LinkedIn URL of Candidate")
    github = models.URLField(max_length=200, blank=True, null=True, help_text="Github URL of Candidate")
    soft_skills = models.TextField(help_text="Communication skills")  
    technical_skills = models.TextField(help_text="Technical skills")  
    summary = models.TextField(help_text="Introduction of Candidate")
    years_of_experience = models.FloatField(default=0.0, help_text="Total years of professional experience")
    def __str__(self):
        return self.name
    
class JobApplication(models.Model):
    application_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobDetail, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    media_id = models.IntegerField(null=True, blank=True)
    cv = models.FileField(upload_to='job_applications/', null=True, blank=True)  # <== NEW
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('rejected', 'Rejected'),
            ('not_selected', 'Not Selected'),
            ('initial_screening', 'Initial Screening'),
            ('final_screening', 'Final Screening'),
            ('rejected_by_hr','Rejected by HR')
        ],
        default='not_selected'
    )

    score = models.FloatField(null=True, blank=True)
    ai_recommendation = models.BooleanField(null=True, blank=True)
    technical_score = models.FloatField(null=True, blank=True)
    experience_score = models.FloatField(null=True, blank=True)
    cultural_score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('job', 'candidate')

    def save(self, *args, **kwargs):
        if self.media_id and not self.cv:
            try:
                media = MediaUpload.objects.get(media_id=self.media_id)
                self.cv = media.cv
            except MediaUpload.DoesNotExist:
                pass  # Optionally log warning here

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.candidate.name} - {self.job.role} ({self.status})"

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobDetail, on_delete=models.CASCADE, related_name='feedback')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='feedback')
    suggested_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)   #1

    class Meta:
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"Feedback for {self.candidate.name} - {self.job.role}"