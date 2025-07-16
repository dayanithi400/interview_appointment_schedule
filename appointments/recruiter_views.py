# appointments/recruiter_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Candidate, Appointment
from django.db.models import Q
from datetime import date, timedelta


def recruiter_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('recruiter_dashboard')
        else:
            return render(request, 'appointments/recruiter_login.html', {'error': 'Invalid credentials'})
    return render(request, 'appointments/recruiter_login.html')

@login_required
def recruiter_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    # Get all booked appointments
    appointments = Appointment.objects.filter(is_active=True).select_related('candidate')
    
    # Get available time slots (excluding booked ones)
    from datetime import date
    booked_slots = Appointment.objects.filter(
        date__gte=date.today(),
        is_active=True
    ).values_list('date', 'time_slot')
    
    # Generate available slots data structure
    time_slots = [
        ('09:00-10:00', '09:00 AM - 10:00 AM'),
        ('10:00-11:00', '10:00 AM - 11:00 AM'),
        # ... other time slots ...
    ]
    
    available_slots = []
    for days_ahead in range(0, 30):  # Next 30 days
        current_date = date.today() + timedelta(days=days_ahead)
        for value, display in time_slots:
            if not Appointment.objects.filter(date=current_date, time_slot=value, is_active=True).exists():
                available_slots.append({
                    'date': current_date,
                    'time_slot': value,
                    'display': f"{current_date.strftime('%Y-%m-%d')} - {display}"
                })
    
    context = {
        'appointments': appointments,
        'available_slots': available_slots[:10],  # Show first 10 available
    }
    return render(request, 'appointments/recruiter_dashboard.html', context)

@login_required
def candidate_detail(request, candidate_id):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    candidate = Candidate.objects.get(id=candidate_id)
    appointments = Appointment.objects.filter(candidate=candidate)
    return render(request, 'appointments/candidate_detail.html', {
        'candidate': candidate,
        'appointments': appointments
    })