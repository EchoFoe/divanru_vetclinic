from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'appointment_date', 'animal_type']

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date:
            appointment_date = appointment_date.replace(second=0)
            if appointment_date < timezone.now():
                raise ValidationError('Дата и время записи должны быть в будущем времени')
        return appointment_date
