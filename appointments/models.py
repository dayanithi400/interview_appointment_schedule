# appointments/models.py
from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    skills = models.TextField()
    education = models.TextField()
    experience = models.TextField()
    resume = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(['pdf'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    TIME_SLOTS = [
        ('09:00-10:00', '09:00 AM - 10:00 AM'),
        ('10:00-11:00', '10:00 AM - 11:00 AM'),
        ('11:00-12:00', '11:00 AM - 12:00 PM'),
        ('13:00-14:00', '01:00 PM - 02:00 PM'),
        ('14:00-15:00', '02:00 PM - 03:00 PM'),
        ('15:00-16:00', '03:00 PM - 04:00 PM'),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=100)
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'time_slot')

    def __str__(self):
        return f"{self.candidate.name} - {self.job_role} on {self.date} at {self.time_slot}"
    
class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username