from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
import tempfile
from .models import Candidate, Appointment
from .forms import (
    AppointmentForm, 
    UpdateAppointmentForm,
    CancelAppointmentForm,
    AdmitCardForm
)
from .services import extract_resume_info

def chat_interface(request):
    # Define options for the welcome screen
    options = [
        {"action": "setAction('book')", "label": "Book Appointment", "description": "Schedule a new interview"},
        {"action": "setAction('update')", "label": "Update Appointment", "description": "Change your interview time"},
        {"action": "setAction('cancel')", "label": "Cancel Appointment", "description": "Cancel your scheduled interview"},
        {"action": "setAction('admit_card')", "label": "Download Admit Card", "description": "Get your interview admit card"},
    ]
    
    context = {
        'action': request.POST.get('action', 'welcome'),
        'options': options
    }
    
    if request.method == 'POST':
        action = request.POST.get('action', 'welcome')
        
        if action == 'book':
            form = AppointmentForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Handle file upload
                    resume = request.FILES['resume']
                    temp_file_path = None
                    
                    # Check if file is in memory or on disk
                    if hasattr(resume, 'temporary_file_path'):
                        # File is on disk
                        file_path = resume.temporary_file_path()
                    else:
                        # File is in memory - save to temp file
                        with tempfile.NamedTemporaryFile(delete=False) as tmp:
                            for chunk in resume.chunks():
                                tmp.write(chunk)
                            file_path = tmp.name
                            temp_file_path = file_path
                    
                    # Extract resume info
                    candidate_info = extract_resume_info(file_path)
                    
                    # Clean up temp file if we created one
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                    
                    # Create candidate
                    candidate = Candidate.objects.create(
                        name=candidate_info['name'],
                        email=candidate_info['email'],
                        phone=candidate_info['phone'],
                        skills=candidate_info['skills'],
                        education=candidate_info['education'],
                        experience=candidate_info['experience'],
                        resume=resume
                    )
                    
                    # Create appointment
                    appointment = form.save(commit=False)
                    appointment.candidate = candidate
                    appointment.save()
                    
                    messages.success(request, 'Appointment booked successfully!')
                    return redirect('chat')
                except Exception as e:
                    messages.error(request, f'Error processing your request: {str(e)}')
            else:
                context['form'] = form
                
        elif action == 'update':
            form = UpdateAppointmentForm(request.POST)
            if form.is_valid():
                try:
                    candidate = Candidate.objects.get(email=form.cleaned_data['email'])
                    appointment = Appointment.objects.get(
                        candidate=candidate,
                        date=form.cleaned_data['date'],
                        is_active=True
                    )
                    appointment.time_slot = form.cleaned_data['new_time_slot']
                    appointment.save()
                    messages.success(request, 'Appointment updated successfully!')
                    return redirect('chat')
                except (Candidate.DoesNotExist, Appointment.DoesNotExist):
                    messages.error(request, 'No active appointment found with these details')
                except Exception as e:
                    messages.error(request, f'Error updating appointment: {str(e)}')
            context['form'] = form
                
        elif action == 'cancel':
            form = CancelAppointmentForm(request.POST)
            if form.is_valid():
                try:
                    candidate = Candidate.objects.get(email=form.cleaned_data['email'])
                    appointment = Appointment.objects.get(
                        candidate=candidate,
                        date=form.cleaned_data['date'],
                        time_slot=form.cleaned_data['time_slot'],
                        is_active=True
                    )
                    appointment.is_active = False
                    appointment.save()
                    messages.success(request, 'Appointment cancelled successfully!')
                    return redirect('chat')
                except (Candidate.DoesNotExist, Appointment.DoesNotExist):
                    messages.error(request, 'No active appointment found with these details')
                except Exception as e:
                    messages.error(request, f'Error cancelling appointment: {str(e)}')
            context['form'] = form
                
        elif action == 'admit_card':
            form = AdmitCardForm(request.POST)
            if form.is_valid():
                try:
                    candidate = Candidate.objects.get(email=form.cleaned_data['email'])
                    appointment = Appointment.objects.get(
                        candidate=candidate,
                        date=form.cleaned_data['date'],
                        time_slot=form.cleaned_data['time_slot'],
                        is_active=True
                    )
                    return generate_admit_card(request, appointment.id)
                except (Candidate.DoesNotExist, Appointment.DoesNotExist):
                    messages.error(request, 'No active appointment found with these details')
                except Exception as e:
                    messages.error(request, f'Error generating admit card: {str(e)}')
            context['form'] = form

    return render(request, 'appointments/chat.html', context)

def generate_admit_card(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Draw admit card
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "INTERVIEW ADMIT CARD")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 700, f"Candidate Name: {appointment.candidate.name}")
    p.drawString(100, 675, f"Email: {appointment.candidate.email}")
    p.drawString(100, 650, f"Phone: {appointment.candidate.phone}")
    p.drawString(100, 625, f"Job Role: {appointment.job_role}")
    p.drawString(100, 600, f"Interview Date: {appointment.date}")
    p.drawString(100, 575, f"Time Slot: {appointment.get_time_slot_display()}")
    
    p.drawString(100, 525, "Instructions:")
    p.drawString(100, 500, "1. Bring this admit card and a government-issued ID")
    p.drawString(100, 475, "2. Arrive 15 minutes before your scheduled time")
    p.drawString(100, 450, "3. Dress professionally")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="admit_card_{appointment.candidate.name}.pdf"'
    return response