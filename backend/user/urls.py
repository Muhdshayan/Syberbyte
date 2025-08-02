from django.urls import path
from .views import LoginAPIView ,UserAccountListCreateView,UserAccountDetailView,JobDetailListCreateView,JobDetailDetailView,UploadCVView,CVListView,CandidateListCreateView,JobApplicationListCreateView ,ResetPasswordView,JobApplicationUpdateView,export_job_applications,FeedbackCreateView

urlpatterns = [
    #Login
    path('login/', LoginAPIView.as_view(), name='login'),
    
    # UserAccount routes
    path('useraccounts/', UserAccountListCreateView.as_view(), name='useraccount-list-create'),
    path('useraccounts/<int:user_id>/', UserAccountDetailView.as_view(), name='useraccount-detail'),
    path('useraccounts/<int:user_id>/reset-password', ResetPasswordView.as_view()),

    # JobDetail routes
    path('jobdetails/', JobDetailListCreateView.as_view(), name='jobdetail-list-create'),
    path('jobdetails/<int:job_id>/', JobDetailDetailView.as_view(), name='jobdetail-detail'),

    # upload the CV
    path('upload-cv/', UploadCVView.as_view(), name='upload-cv'),
    path('list-cvs/', CVListView.as_view(), name='list-cvs'),

    #to retrieve Candidates Data
    path('candidates/', CandidateListCreateView.as_view(), name='candidate-list-create'),

    # to retrieve data for view Candidates 
    path('jobapplication/', JobApplicationListCreateView.as_view(), name='jobapplication-list-create'),
    path('jobapplication/update/', JobApplicationUpdateView.as_view()),
    path('jobapplication/export/', export_job_applications, name='jobapplication-export'),

    path('feedback/', FeedbackCreateView.as_view(), name='feedback-create'),
]
