# appointments/forms.py
from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['job_role', 'date', 'time_slot']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    resume = forms.FileField(
        label='Resume (PDF)',
        widget=forms.FileInput(attrs={'accept': '.pdf'}),
        required=True
    )

class UpdateAppointmentForm(forms.Form):
    email = forms.EmailField()
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    new_time_slot = forms.ChoiceField(choices=Appointment.TIME_SLOTS)

class CancelAppointmentForm(forms.Form):
    email = forms.EmailField()
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time_slot = forms.ChoiceField(choices=Appointment.TIME_SLOTS)

class AdmitCardForm(forms.Form):
    email = forms.EmailField()
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time_slot = forms.ChoiceField(choices=Appointment.TIME_SLOTS)