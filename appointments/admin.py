# appointments/admin.py
from django.contrib import admin
from .models import Candidate, Appointment

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job_role', 'date', 'time_slot', 'is_active')
    list_filter = ('date', 'is_active')
    search_fields = ('candidate__name', 'job_role')