from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status , generics
from .serializers import LoginSerializer
from .models import UserAccount, JobDetail, MediaUpload , Candidate , JobApplication
from .serializers import UserAccountSerializer, JobDetailSerializer , CVUploadSerializer , CandidateSerializer,JobApplicationSerializer
from rest_framework.permissions import AllowAny
from .tasks import parse_cv_task
import logging
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from django.utils import timezone

# Set up logging
logger = logging.getLogger(__name__)

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']            
            
            # Check if the account is suspended
            if user.status == "Suspended":
                return Response(
                    {"error": "Account suspended"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return Response({
                "message": "Login successful",
                "user_id": user.user_id,
                "email": user.email,
                "role": user.role,
                "permission": user.permission,
                "time": user.time
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadCVView(APIView):
    serializer_class = CVUploadSerializer

    def post(self, request):
        print("=== Raw Request Data ===")
        print("request.data:", request.data)
        print("request.FILES:", request.FILES)

        print("job_id:", request.data.get('jobId'))
        print("file_type:", request.data.getlist('fileTypes'))
        print("cv:", request.FILES.getlist('files'))

        job_id = request.data.get('jobId')                     
        file_types = request.data.getlist('fileTypes')         
        files = request.FILES.getlist('files')                


        if not job_id:
            return Response({"error": "jobId is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not files:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not file_types or len(file_types) != len(files):
            return Response({"error": "Mismatch in number of files and fileTypes"}, status=status.HTTP_400_BAD_REQUEST)

        success_files = []
        error_entries = []
        new_candidates = []  # Placeholder if you want to populate this later

        for file, file_type in zip(files, file_types):
            data = {
                'cv': file,
                'job_id': job_id,
                'file_type': file_type
            }

            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                media = serializer.save()

                # Trigger Celery task
                parse_cv_task.delay(media.id)

                success_files.append({
                    "id": media.id,
                    "url": media.cv.url,
                    "uploaded_at": media.uploaded_at,
                    "file_type": media.file_type
                })
                # Optionally add to newCandidates if you link to Candidate model
                # new_candidates.append(candidate_data)
            else:
                error_entries.append({
                    "fileName": file.name,
                    "error": serializer.errors
                })

        total = len(files)
        success_count = len(success_files)
        error_count = len(error_entries)

        return Response(
            {
                "files": success_files,
                "totalFiles": total,
                "successCount": success_count,
                "errorCount": error_count,
                "errors": error_entries,
                "newCandidates": new_candidates
            },
            status=status.HTTP_207_MULTI_STATUS if error_count else status.HTTP_201_CREATED
        )



class CVListView(generics.ListAPIView):
    queryset = MediaUpload.objects.all()
    serializer_class = CVUploadSerializer

class CandidateListCreateView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer


class JobApplicationListCreateView(generics.ListCreateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer    

class JobApplicationUpdateView(APIView):
    def put(self, request, *args, **kwargs):
        data = request.data  # Should be a list of job application dicts
        logger.info("Received PUT request with data: %s", data)

        if not isinstance(data, list):
            logger.error("Invalid data format: Expected a list, got %s", type(data))
            return Response({"detail": "Expected a list of job applications."}, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        updated = []

        for item in data:
            try:
                app_id = item.get('application_id')
                if app_id is None:
                    logger.error("Missing application_id in item: %s", item)
                    errors.append({"application_id": "Missing application_id"})
                    continue

                app = JobApplication.objects.get(application_id=app_id)
                serializer = JobApplicationSerializer(app, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated.append(serializer.data)
                    logger.info("Successfully updated application_id: %s", app_id)
                else:
                    logger.error("Serializer errors for application_id %s: %s", app_id, serializer.errors)
                    errors.append({str(app_id): serializer.errors})
            except JobApplication.DoesNotExist:
                logger.error("JobApplication not found for application_id: %s", app_id)
                errors.append({str(app_id): "Not found"})
            except Exception as e:
                logger.error("Unexpected error for application_id %s: %s", app_id, str(e))
                errors.append({str(app_id): str(e)})

        response_data = {"updated": updated, "errors": errors}
        logger.info("Response data: %s", response_data)

        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

        return Response({"updated": updated}, status=status.HTTP_200_OK)
                
# UserAccount Views
class UserAccountListCreateView(generics.ListCreateAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UserAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    lookup_field = 'user_id'  # Make sure your frontend sends `user_id`, not `id`

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        print("=== Incoming PUT Request ===")
        print("User ID:", kwargs.get("user_id"))
        print("Incoming Data:", request.data)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            print("=== Validation Errors ===")
            for field, errors in serializer.errors.items():
                print(f"Field: {field} - Errors: {errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        print("=== Update Successful ===")
        print("Updated Data:", serializer.data)

        return Response(serializer.data)

class ResetPasswordView(APIView):
    def post(self, request, user_id):
        try:
            user = UserAccount.objects.get(user_id=user_id)
            new_password = request.data.get('password')
            if not new_password:
                return Response({"error": "Password is required"}, status=400)

            # Directly update the password field
            user.password = new_password
            user.save()

            return Response({"message": "Password reset successful"}, status=200)
        except UserAccount.DoesNotExist:
            return Response({"error": "User not found"}, status=404)    

# JobDetail Views
class JobDetailListCreateView(generics.ListCreateAPIView):
    queryset = JobDetail.objects.all()
    serializer_class = JobDetailSerializer

    def post(self, request, *args, **kwargs):
        logger.debug("Received POST request to /api/admin/job-categories")
        logger.debug("Request payload: %s", request.data)

        try:
            serializer = self.get_serializer(data=request.data)
            logger.debug("Serializer initialized with data: %s", serializer.initial_data)

            if serializer.is_valid():
                logger.debug("Serializer is valid. Saving data...")
                self.perform_create(serializer)
                logger.debug("Data saved successfully. Response: %s", serializer.data)
                return self.get_response(serializer.data)
            else:
                logger.error("Serializer validation failed. Errors: %s", serializer.errors)
                return self.get_response_error(serializer.errors, status=400)

        except Exception as e:
            logger.exception("Unexpected error during POST: %s", str(e))
            return self.get_response_error({"error": "An unexpected error occurred"}, status=500)

    def get_response(self, data):
        from rest_framework.response import Response
        return Response(data, status=201)

    def get_response_error(self, errors, status):
        from rest_framework.response import Response
        return Response(errors, status=status)

class JobDetailDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobDetail.objects.all()
    serializer_class = JobDetailSerializer
    lookup_field = 'job_id'  # important for ID-based lookup

    def update(self, request, *args, **kwargs):
        print("\n===== [DEBUG] Incoming PUT Data =====")
        print(request.data)
        print("===== [DEBUG] URL kwargs =====")
        print(kwargs)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            print("===== [DEBUG] Serializer Errors =====")
            print(serializer.errors)
            return Response(serializer.errors, status=400)

        self.perform_update(serializer)

        print("===== [DEBUG] Successfully Updated =====")
        return Response(serializer.data)

class JobApplicationExportView(APIView):
    def get(self, request):
        try:
            # Fetch all JobApplication data
            applications = JobApplication.objects.select_related('job', 'candidate').all()
            
            # Prepare data for Excel
            data = []
            for app in applications:
                # Convert timezone-aware datetime to naive datetime
                application_date = app.application_date
                if timezone.is_aware(application_date):
                    application_date = timezone.make_naive(application_date)
                
                data.append({
                    'Application ID': app.application_id,
                    'Job ID': app.job.job_id,
                    'Job Role': app.job.role,
                    'Candidate Name': app.candidate.name,
                    'Candidate Email': app.candidate.email,
                    'Application Date': application_date,
                    'Status': app.status,
                    'Score': app.score,
                    'AI Recommendation': app.ai_recommendation,
                    'Technical Score': app.technical_score,
                    'Experience Score': app.experience_score,
                    'Cultural Score': app.cultural_score
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Create Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Job Applications', index=False)
                # Adjust column widths
                worksheet = writer.sheets['Job Applications']
                for idx, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(idx, idx, max_len)
            
            # Prepare response
            output.seek(0)
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                content=output.getvalue()
            )
            response['Content-Disposition'] = 'attachment; filename=job_applications.xlsx'
            
            logger.info("Successfully generated and sent job applications Excel file")
            return response
            
        except Exception as e:
            logger.error("Error generating Excel file: %s", str(e))
            return Response(
                {"error": "Failed to generate Excel file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
