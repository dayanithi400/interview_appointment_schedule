from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from appointments.models import Recruiter
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Creates a recruiter account'

    def handle(self, *args, **options):
        self.stdout.write("Creating recruiter account...")
        
        while True:
            username = input("Enter username: ")
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR(f"Username '{username}' already exists. Please choose another."))
                continue
                
            password = input("Enter password: ")
            email = input("Enter email: ")
            
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    is_staff=True
                )
                
                Recruiter.objects.create(
                    user=user,
                    password=password  # Note: In production, don't store plain text passwords
                )
                
                self.stdout.write(self.style.SUCCESS(f'Successfully created recruiter {username}'))
                break
                
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Error creating user: {e}"))
                self.stdout.write("Please try again with different credentials.")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
                break