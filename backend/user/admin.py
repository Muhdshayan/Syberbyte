from django.contrib import admin
from .models import UserAccount, JobDetail, Candidate, WorkExperience, Education, JobApplication , MediaUpload ,Feedback

class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    fields = ('role', 'company_name', 'start_year', 'end_year', 'summary')
    ordering = ('-start_year',)

class EducationInline(admin.TabularInline):
    model = Education
    extra = 1
    fields = ('degree_name', 'university_name', 'start_year', 'end_year')
    ordering = ('-start_year',)

class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 1
    fields = ('candidate', 'application_date', 'status')
    readonly_fields = ('application_date',)
    ordering = ('-application_date',)

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'permission', 'time' , 'status' )
    list_filter = ('role', 'permission' , 'status')
    search_fields = ('email', 'name')

@admin.register(JobDetail)
class JobDetailAdmin(admin.ModelAdmin):
    list_display = ('posted_by','assigned_to','role', 'industry', 'location', 'job_type', 'date_posted', 'is_active' , 'status')
    list_filter = ('posted_by','assigned_to','industry', 'job_type', 'is_active' , 'status')
    search_fields = ('role', 'industry', 'description')
    
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'display_work_experiences', 'display_educations')
    search_fields = ('name', 'email', 'phone_number', 'soft_skills', 'technical_skills')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone_number', 'linkedin', 'github')
        }),
        ('Skills', {
            'fields': ('soft_skills', 'technical_skills')
        }),
    )
    inlines = [WorkExperienceInline, EducationInline]

    def display_work_experiences(self, obj):
        return ", ".join([f"{exp.role} at {exp.company_name} ({exp.start_year}-{exp.end_year or 'Present'})" for exp in obj.work_experiences.all()])
    display_work_experiences.short_description = 'Work Experiences'

    def display_educations(self, obj):
        return ", ".join([f"{edu.degree_name} at {edu.university_name} ({edu.start_year}-{edu.end_year or 'Ongoing'})" for edu in obj.educations.all()])
    display_educations.short_description = 'Educations'

    
@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('role', 'company_name', 'candidate', 'start_year', 'end_year')
    list_filter = ('start_year', 'end_year')
    search_fields = ('role', 'company_name', 'candidate__name')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree_name', 'university_name', 'candidate', 'start_year', 'end_year')
    list_filter = ('start_year', 'end_year')
    search_fields = ('degree_name', 'university_name', 'candidate__name')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'candidate_name', 
        'candidate_id', 
        'job_role', 
        'job_id', 
        'application_date', 
        'status',
        'score',
        'ai_recommendation'
    )
    list_filter = ('status', 'application_date', 'job')
    search_fields = ('candidate__name', 'job__role')
    actions = ['mark_all_under_review']

    @admin.action(description="Mark selected as 'Not Selected', Score=90, Recommendation='0'")
    def mark_all_under_review(self, request, queryset):
        updated = queryset.update(
            status='not_selected',
            score=90,
            ai_recommendation= 0,
            technical_score = 50.0,
            experience_score = 70.0,
            cultural_score = 90.0,
        )
        self.message_user(request, f"{updated} application(s) updated.")

    # Display helpers
    def candidate_name(self, obj):
        return obj.candidate.name

    def candidate_id(self, obj):
        return obj.candidate.candidate_id

    def job_role(self, obj):
        return obj.job.role

    def job_id(self, obj):
        return obj.job.job_id

    def ai_recommendation(self, obj):
        return obj.ai_recommendation or "—"




@admin.register(MediaUpload)
class MediaUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_id', 'file_name', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('job_id', 'cv')
    ordering = ('-uploaded_at',)

    def file_name(self, obj):
        return obj.cv.name.split('/')[-1]
    file_name.short_description = 'File Name'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_id', 'job_role', 'candidate_name', 'suggested_score', 'created_at')
    list_filter = ('suggested_score', 'created_at')
    search_fields = ('job__role', 'candidate__name', 'feedback')
    ordering = ('-created_at',)

    def job_role(self, obj):
        return obj.job.role
    job_role.short_description = 'Job Role'

    def candidate_name(self, obj):
        return obj.candidate.name
    candidate_name.short_description = 'Candidate Name'