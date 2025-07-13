from django.urls import path
from .views import LoginAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
]
