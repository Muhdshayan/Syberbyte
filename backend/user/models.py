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
    

class WorkExperience(models.Model):
    work_experience_id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='work_experiences')
    role = models.CharField(max_length=255, help_text="Job title or role")
    company_name = models.CharField(max_length=255, help_text="Name of the company")
    start_year = models.PositiveIntegerField(help_text="Start year of employment")
    end_year = models.PositiveIntegerField(null=True, blank=True, help_text="End year of employment (null if current)")
    summary = models.TextField(help_text="Summary of responsibilities and achievements")

    def __str__(self):
        return f"{self.role} at {self.company_name} ({self.start_year} - {self.end_year or 'Present'})"

class Education(models.Model):
    education_id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='educations')
    degree_name = models.CharField(max_length=255, help_text="Name of the degree (e.g., Bachelor's in Computer Science)")
    university_name = models.CharField(max_length=255, help_text="Name of the university or institution")
    start_year = models.PositiveIntegerField(help_text="Start year of education")
    end_year = models.PositiveIntegerField(null=True, blank=True, help_text="End year of education (null if ongoing)")

    def __str__(self):
        return f"{self.degree_name} at {self.university_name} ({self.start_year} - {self.end_year or 'Ongoing'})"
       
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

    def __str__(self):
        return self.name
    
class JobApplication(models.Model):
    application_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobDetail, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
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

    # New fields
    score = models.FloatField(null=True, blank=True)
    ai_recommendation = models.BooleanField(null=True, blank=True)
    technical_score = models.FloatField(null=True, blank=True)
    experience_score = models.FloatField(null=True, blank=True)
    cultural_score = models.FloatField(null=True, blank=True)
    class Meta:
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"{self.candidate.name} - {self.job.role} ({self.status})"    

def cv_upload_path(instance, filename):
    try:
        # Look up the job title
        job = JobDetail.objects.get(job_id=instance.job_id)
        title_slug = slugify(job.role)
        return os.path.join('cvs', title_slug, filename)
    except JobDetail.DoesNotExist:
        # Fallback to generic path
        return os.path.join('cvs', 'unknown', filename)

class MediaUpload(models.Model):
    job_id = models.CharField(max_length=100)
    cv = models.FileField(upload_to=cv_upload_path)  # <- updated here
    file_type = models.CharField(max_length=10)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cv.name} for Job {self.job_id}"

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobDetail, on_delete=models.CASCADE, related_name='feedback')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='feedback')
    suggested_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"Feedback for {self.candidate.name} - {self.job.role}"