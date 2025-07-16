# interview_bot/urls.py
from django.contrib import admin
from django.urls import path
from appointments import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.chat_interface, name='chat'),
]