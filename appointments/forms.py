from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Doctor, Patient, Appointment, MedicalReport, TIME_SLOT_CHOICES, GENDER_CHOICES, BLOOD_GROUP_CHOICES


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'email', 'phone', 'date_of_birth', 'gender', 'blood_group', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Residential Address'}),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        return dob


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'date', 'time_slot', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for consultation'}),
        }

    def clean_date(self):
        appointment_date = self.cleaned_data.get('date')
        if appointment_date and appointment_date < date.today():
            raise ValidationError("Appointment date cannot be in the past.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')

        if doctor and not doctor.active:
            raise ValidationError(f"Dr. {doctor.name} is currently not accepting new appointments.")

        if doctor and appointment_date and not doctor.is_available_on(appointment_date):
            raise ValidationError(
                f"Dr. {doctor.name} is not available on {appointment_date.strftime('%A')}s. "
                f"Available days are: {doctor.available_days}."
            )

        # Check double booking
        if doctor and appointment_date and time_slot:
            existing_query = Appointment.objects.filter(
                doctor=doctor,
                date=appointment_date,
                time_slot=time_slot
            ).exclude(status='Cancelled')

            if self.instance and self.instance.pk:
                existing_query = existing_query.exclude(pk=self.instance.pk)

            if existing_query.exists():
                raise ValidationError(
                    f"The selected time slot ({time_slot}) is already booked for Dr. {doctor.name} on {appointment_date}. "
                    "Please choose another time slot or date."
                )

        return cleaned_data


class AppointmentBookingForm(forms.Form):
    """
    Combined form for public appointment booking workflow:
    Collects patient details and appointment details seamlessly.
    """
    # Patient fields
    patient_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. John Doe', 'id': 'patient_name'})
    )
    patient_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. john@example.com', 'id': 'patient_email'})
    )
    patient_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +1 234 567 8900', 'id': 'patient_phone'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'date_of_birth'})
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'gender'})
    )
    blood_group = forms.ChoiceField(
        choices=[('', '-- Select Blood Group (Optional) --')] + BLOOD_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'blood_group'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Residential address', 'id': 'address'})
    )

    # Appointment fields
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'appointment_date'})
    )
    time_slot = forms.ChoiceField(
        choices=TIME_SLOT_CHOICES,
        widget=forms.HiddenInput(attrs={'id': 'id_time_slot'})
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your symptoms or reason for visit...', 'id': 'reason'})
    )

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

    def clean_appointment_date(self):
        appt_date = self.cleaned_data.get('appointment_date')
        if appt_date and appt_date < date.today():
            raise ValidationError("Appointment date cannot be in the past.")
        return appt_date

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean(self):
        cleaned_data = super().clean()
        appt_date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')

        if not self.doctor:
            raise ValidationError("Doctor is not specified.")

        if not self.doctor.active:
            raise ValidationError(f"Dr. {self.doctor.name} is currently inactive and not accepting appointments.")

        if appt_date and not self.doctor.is_available_on(appt_date):
            raise ValidationError(
                f"Dr. {self.doctor.name} does not have consultations on {appt_date.strftime('%A')}s. "
                f"Available days: {self.doctor.available_days}."
            )

        if not time_slot:
            raise ValidationError("Please select an appointment time slot.")

        # Double-booking check
        if appt_date and time_slot:
            is_booked = Appointment.objects.filter(
                doctor=self.doctor,
                date=appt_date,
                time_slot=time_slot
            ).exclude(status='Cancelled').exists()

            if is_booked:
                raise ValidationError(
                    f"Dr. {self.doctor.name} is already booked for {time_slot} on {appt_date}. "
                    "Please select a different available slot."
                )

        return cleaned_data


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['diagnosis', 'prescription', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical diagnosis & findings'}),
            'prescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Prescribed medications, dosage & duration'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Follow-up instructions or dietary notes (optional)'}),
        }
