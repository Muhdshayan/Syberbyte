
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    UserAccount,
    JobDetail,
    Candidate,
    Education,
    JobApplication,
    MediaUpload,
    Feedback
)
import logging
import re
import json


# Set up logging
logger = logging.getLogger(__name__)

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




class EducationSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    degree_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    start_year = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    end_year = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Education
        fields = ['university_name', 'degree_name', 'start_year', 'end_year']

    def validate_start_year(self, value):
        logger.info("Validating start_year: %s", value)
        if value is None or value == '':
            logger.info("start_year is None or empty, returning as is")
            return value
        if value.lower() == 'present':
            logger.info("start_year is 'Present', returning as is")
            return value
        match = re.search(r'\b(\d{4})\b', value)
        if match:
            year = match.group(1)
            logger.info("Extracted year %s from %s", year, value)
            return year
        logger.warning("No valid year found in start_year: %s, returning as is", value)
        return value

    def validate_end_year(self, value):
        logger.info("Validating end_year: %s", value)
        if value is None or value.lower() == 'ongoing':
            logger.info("end_year is None or 'Ongoing', returning as is")
            return value
        match = re.search(r'\b(\d{4})\b', value)
        if match:
            year = match.group(1)
            logger.info("Extracted year %s from %s", year, value)
            return year
        logger.warning("No valid year found in end_year: %s, returning as is", value)
        return value

    def validate(self, data):
        logger.info("=== EducationSerializer validate ===")
        logger.info("Education data: %s", data)
        # Convert None to empty string
        for field in ['university_name', 'degree_name', 'start_year', 'end_year']:
            if data.get(field) is None:
                data[field] = ''
        return data

class CandidateSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True, required=False)
    github = serializers.URLField(allow_null=True, allow_blank=True, required=False)
    linkedin = serializers.URLField(allow_null=True, allow_blank=True, required=False)
    soft_skills = serializers.CharField(required=False, allow_blank=True)
    technical_skills = serializers.CharField(required=False, allow_blank=True)
    summary = serializers.CharField(allow_blank=True, required=False)
    years_of_experience = serializers.FloatField(required=False, allow_null=True, default=0.0)

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
            'years_of_experience',
            'educations',
        ]

    def to_internal_value(self, data):
        logger.info("=== CandidateSerializer to_internal_value ===")
        logger.info("Raw input data: %s", data)

        # Preprocess data to handle mismatches
        processed_data = data.copy()

        # Remove unexpected fields like 'file'
        processed_data.pop('file', None)

        # Handle 'Not found' for github, linkedin, and other fields
        if processed_data.get('github') == 'Not found':
            processed_data['github'] = None
            logger.info("Converted github 'Not found' to None")
        if processed_data.get('linkedin') == 'Not found':
            processed_data['linkedin'] = None
            logger.info("Converted linkedin 'Not found' to None")
        if processed_data.get('phone') == 'Not found':
            processed_data['phone_number'] = None
            logger.info("Converted phone 'Not found' to None")
        if processed_data.get('name') == 'Name Not Found':
            processed_data['name'] = ''
            logger.info("Converted name 'Name Not Found' to empty string")
        if processed_data.get('email') == 'Not found':
            processed_data['email'] = ''
            logger.info("Converted email 'Not found' to empty string")

        # Handle education (singular) to educations (plural)
        if 'education' in processed_data and 'educations' not in processed_data:
            education = processed_data.pop('education')
            logger.info("Found 'education' field: %s", education)
            if isinstance(education, dict):
                if isinstance(education.get('degree'), list) and isinstance(education.get('year'), list):
                    # Handle lists for degree and year
                    degrees = education.get('degree', [])
                    years = education.get('year', [])
                    processed_data['educations'] = [{
                        'university_name': education.get('institute', '') or '',
                        'degree_name': degrees[i] if i < len(degrees) else '',
                        'start_year': years[i] if i < len(years) else '',
                        'end_year': education.get('end_year', '') or ''
                    } for i in range(max(len(degrees), len(years)))]
                else:
                    processed_data['educations'] = [{
                        'university_name': education.get('institute', '') or '',
                        'degree_name': education.get('degree', '') or '',
                        'start_year': education.get('year', '') or '',
                        'end_year': education.get('end_year', '') or ''
                    }]
                logger.info("Mapped 'education' to 'educations': %s", processed_data['educations'])
            elif isinstance(education, list):
                processed_data['educations'] = [{
                    'university_name': edu.get('institute', '') or '' if isinstance(edu, dict) else str(edu),
                    'degree_name': edu.get('degree', '') or '' if isinstance(edu, dict) else '',
                    'start_year': edu.get('year', '') or '' if isinstance(edu, dict) else '',
                    'end_year': edu.get('end_year', '') or '' if isinstance(edu, dict) else ''
                } for edu in education]
                logger.info("Mapped 'education' list to 'educations': %s", processed_data['educations'])
            else:
                processed_data['educations'] = []
                logger.warning("Invalid 'education' format, setting educations to empty: %s", education)
        elif 'educations' not in processed_data or processed_data['educations'] is None:
            processed_data['educations'] = []
            logger.info("No education/educations provided or educations is None, defaulting to empty list")

        # Handle skills as string 'Not found' or dictionary
        if processed_data.get('skills') == 'Not found':
            processed_data['soft_skills'] = ''
            processed_data['technical_skills'] = ''
            processed_data.pop('skills', None)
            logger.info("Converted skills 'Not found' to empty soft_skills and technical_skills")
        elif 'skills' in processed_data:
            skills = processed_data.pop('skills')
            if isinstance(skills, dict):
                processed_data['soft_skills'] = json.dumps(skills.get('soft_skills', {}))
                processed_data['technical_skills'] = json.dumps(skills.get('technical_skills', {}))
                logger.info("Converted skills dict to strings - soft_skills: %s, technical_skills: %s",
                            processed_data['soft_skills'], processed_data['technical_skills'])
            else:
                processed_data['soft_skills'] = ''
                processed_data['technical_skills'] = ''
                logger.warning("Invalid skills format, setting to empty strings: %s", skills)

        # Handle years_of_experience
        if 'years_of_experience' in processed_data:
            if processed_data['years_of_experience'] == '':
                processed_data['years_of_experience'] = None
                logger.info("Converted empty years_of_experience to None")
            elif isinstance(processed_data['years_of_experience'], str):
                try:
                    processed_data['years_of_experience'] = float(processed_data['years_of_experience'])
                    if processed_data['years_of_experience'] > 100:  # Likely a year like 2022.0
                        logger.warning("Invalid years_of_experience: %s, setting to 0.0", processed_data['years_of_experience'])
                        processed_data['years_of_experience'] = 0.0
                except ValueError:
                    logger.warning("Invalid years_of_experience format，正確な文字列でない: %s, setting to None", processed_data['years_of_experience'])
                    processed_data['years_of_experience'] = None
        else:
            processed_data['years_of_experience'] = None
            logger.info("No years_of_experience provided, defaulting to None")

        # Handle phone_number
        if 'phone' in processed_data:
            processed_data['phone_number'] = processed_data.pop('phone')
            logger.info("Mapped 'phone' to 'phone_number': %s", processed_data['phone_number'])

        # Add default values for missing fields
        if 'summary' not in processed_data:
            processed_data['summary'] = ''
            logger.info("Added default empty summary")

        logger.info("Processed data: %s", processed_data)

        # Call parent to_internal_value to continue validation
        try:
            ret = super().to_internal_value(processed_data)
            logger.info("Validated internal value: %s", ret)
            return ret
        except serializers.ValidationError as e:
            logger.error("Validation error in to_internal_value: %s", e)
            raise

    def validate(self, data):
        logger.info("=== CandidateSerializer validate ===")
        logger.info("Validated data: %s", data)

        # Log individual field validation
        for field in self.fields:
            logger.info("Field '%s': %s", field, data.get(field))

        return data

    def create(self, validated_data):
        logger.info("=== CandidateSerializer create ===")
        logger.info("Creating Candidate with:")
        logger.info("✔️ Basic Info: %s", validated_data)
        educations_data = validated_data.pop('educations', [])
        logger.info("🎓 Educations: %s", educations_data)

        try:
            candidate = Candidate.objects.create(**validated_data)
            logger.info("Created candidate with ID: %s", candidate.candidate_id)
        except Exception as e:
            logger.error("Error creating candidate: %s", str(e))
            raise serializers.ValidationError({"email": f"Error creating candidate: {str(e)}"})

        for edu in educations_data:
            try:
                Education.objects.create(candidate=candidate, **edu)
                logger.info("Created education: %s", edu)
            except Exception as e:
                logger.error("Error creating education: %s", str(e))
                raise serializers.ValidationError({"educations": f"Error creating education: {str(e)}"})

        logger.info("Candidate creation completed: %s", candidate)
        return candidate    

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
    media_id = serializers.IntegerField(required=False, default=0, write_only=True)
    cv = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'application_id', 'job', 'candidate', 'candidate_id', 'job_id',
            'application_date', 'status', 'score', 'ai_recommendation',
            'technical_score', 'experience_score', 'cultural_score', 'media_id', 'cv'
        ]

    def get_cv(self, obj):
        # Fetch the MediaUpload object using media_id and return the cv URL
        if obj.media_id:
            try:
                media = MediaUpload.objects.get(media_id=obj.media_id)
                return media.cv.url  # Returns the URL of the CV file
            except MediaUpload.DoesNotExist:
                return None
        return None

    def to_internal_value(self, data):
        print("=== JobApplicationSerializer to_internal_value ===")
        print("Raw input data: %s", data)
        print("media_id in raw data: %s", data.get('media_id'))
        print("Type of media_id in raw data: %s", type(data.get('media_id')))

        processed_data = data.copy()
        if 'media_id' in processed_data and processed_data['media_id'] is not None:
            try:
                # Ensure media_id is an integer and corresponds to an existing MediaUpload
                media_id = int(processed_data['media_id'])
                if media_id != 0:  # Only validate if media_id is non-zero
                    MediaUpload.objects.get(media_id=media_id)
                print("Validated media_id: %s", media_id)
            except (ValueError, TypeError):
                print("Invalid media_id format: %s, setting to 0", processed_data['media_id'])
                processed_data['media_id'] = 0
            except MediaUpload.DoesNotExist:
                print("MediaUpload with media_id=%s does not exist, setting to 0", processed_data['media_id'])
                processed_data['media_id'] = 0
        else:
            print("media_id missing or None in input, setting to 0")
            processed_data['media_id'] = 0

        print("Processed data: %s", processed_data)
        ret = super().to_internal_value(processed_data)
        print("Validated internal value: %s", ret)
        print("media_id in internal value: %s", ret.get('media_id'))
        print("Type of media_id in internal value: %s", type(ret.get('media_id')))
        return ret

    def validate(self, data):
        print("=== JobApplicationSerializer validate ===")
        print("Validated data: %s", data)
        print("media_id in validated data: %s", data.get('media_id'))
        print("Type of media_id in validated data: %s", type(data.get('media_id')))
        return data

    def create(self, validated_data):
        print("=== JobApplicationSerializer create ===")
        print("Creating JobApplication with validated data: %s", validated_data)
        print("media_id in validated data: %s", validated_data.get('media_id'))
        print("Type of media_id in validated data: %s", type(validated_data.get('media_id')))
        try:
            instance = super().create(validated_data)
            print("Created JobApplication: %s", instance)
            print("media_id in created instance: %s", instance.media_id)
            return instance
        except Exception as e:
            print("Error creating JobApplication: %s", str(e))
            raise
                
class FeedbackSerializer(serializers.ModelSerializer):
    candidate_id = serializers.PrimaryKeyRelatedField(
        queryset=Candidate.objects.all(), source='candidate', write_only=True
    )
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=JobDetail.objects.all(), source='job', write_only=True
    )
    feedback_text = serializers.CharField(source='feedback', write_only=True)
    suggested_score = serializers.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    candidate = CandidateSerializer(read_only=True)
    job = JobDetailSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'feedback_id', 'job', 'candidate', 'candidate_id', 'job_id',
            'suggested_score', 'feedback_text', 'created_at'
        ]

    def validate(self, data):
        candidate = data.get('candidate')
        job = data.get('job')
        if Feedback.objects.filter(candidate=candidate, job=job).exists():
            raise serializers.ValidationError("Feedback for this candidate and job already exists.")
        return data