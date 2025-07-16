# interview_bot/urls.py
from django.contrib import admin
from django.urls import path
from appointments import views,recruiter_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.chat_interface, name='chat'),
    path('recruiter/login/', recruiter_views.recruiter_login, name='recruiter_login'),
    path('recruiter/dashboard/', recruiter_views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiter/candidate/<int:candidate_id>/', recruiter_views.candidate_detail, name='candidate_detail'),
]