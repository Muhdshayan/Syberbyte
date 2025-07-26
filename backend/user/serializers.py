
from rest_framework import serializers
from .models import (
    UserAccount,
    JobDetail,
    Candidate,
    WorkExperience,
    Education,
    JobApplication,
    MediaUpload
)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if password != user.password:
            raise serializers.ValidationError("Invalid email or password.")

        data['user'] = user
        return data

class CVUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaUpload
        fields = ['job_id', 'cv', 'file_type']
        

    def validate_file_type(self, value):
        allowed_types = ['pdf', 'doc', 'docx']
        if value.lower() not in allowed_types:
            raise serializers.ValidationError("Unsupported file type.")
        return value


class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    permission = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = UserAccount
        fields = '__all__'


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class CandidateSerializer(serializers.ModelSerializer):

    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'candidate_id',
            'name',
            'email',
            'phone_number',
            'linkedin',
            'github',
            'soft_skills',
            'technical_skills',
            'summary',
            'work_experiences',
            'educations',
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDetail
        fields = '__all__'

class JobApplicationSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer(read_only=True)
    candidate_id = serializers.PrimaryKeyRelatedField(
        queryset=Candidate.objects.all(), source='candidate', write_only=True
    )
    job = JobDetailSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=JobDetail.objects.all(), source='job', write_only=True
    )

    class Meta:
        model = JobApplication
        fields = [
            'application_id', 'job', 'candidate', 'candidate_id', 'job_id',
            'application_date', 'status', 'score', 'ai_recommendation','technical_score','experience_score','cultural_score'
        ]
