from django.db import models
from django.utils import timezone
from datetime import date


DEPARTMENT_CHOICES = [
    ('Cardiology', 'Cardiology'),
    ('Pediatrics', 'Pediatrics'),
    ('Orthopedics', 'Orthopedics'),
    ('Neurology', 'Neurology'),
    ('General Medicine', 'General Medicine'),
    ('Dermatology', 'Dermatology'),
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
]

TIME_SLOT_CHOICES = [
    ('09:00 AM', '09:00 AM'),
    ('09:30 AM', '09:30 AM'),
    ('10:00 AM', '10:00 AM'),
    ('10:30 AM', '10:30 AM'),
    ('11:00 AM', '11:00 AM'),
    ('11:30 AM', '11:30 AM'),
    ('02:00 PM', '02:00 PM'),
    ('02:30 PM', '02:30 PM'),
    ('03:00 PM', '03:00 PM'),
    ('03:30 PM', '03:30 PM'),
    ('04:00 PM', '04:00 PM'),
    ('04:30 PM', '04:30 PM'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
]


class Doctor(models.Model):
    name = models.CharField(max_length=150)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    specialization = models.CharField(max_length=200)
    qualification = models.CharField(max_length=100, default='MBBS, MD')
    experience_years = models.PositiveIntegerField(default=5)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available_days = models.CharField(
        max_length=150,
        help_text="Comma-separated days, e.g. Mon, Tue, Wed, Thu, Fri"
    )
    active = models.BooleanField(default=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"Dr. {self.name} - {self.department}"

    def get_days_list(self):
        """Returns list of clean trimmed available days."""
        if not self.available_days:
            return []
        return [d.strip() for d in self.available_days.split(',') if d.strip()]

    def is_available_on(self, target_date):
        """Check if doctor is available on a specific date based on weekday."""
        if not self.available_days:
            return True
        weekday_map = {
            0: 'Mon',
            1: 'Tue',
            2: 'Wed',
            3: 'Thu',
            4: 'Fri',
            5: 'Sat',
            6: 'Sun',
        }
        day_abbr = weekday_map.get(target_date.weekday())
        available_days_clean = [d.upper()[:3] for d in self.get_days_list()]
        return day_abbr.upper() in available_days_clean

    def get_badge_class(self):
        """Returns appropriate Bootstrap badge color class based on department."""
        badge_map = {
            'Cardiology': 'danger',
            'Pediatrics': 'success',
            'Orthopedics': 'warning',
            'Neurology': 'primary',
            'General Medicine': 'info',
            'Dermatology': 'secondary',
        }
        return badge_map.get(self.department, 'primary')


class Patient(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def get_age(self):
        """Calculate age in years."""
        today = date.today()
        if self.date_of_birth:
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'time_slot']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date', 'time_slot'],
                condition=~models.Q(status='Cancelled'),
                name='unique_doctor_date_timeslot_active'
            )
        ]

    def __str__(self):
        return f"Appt #{self.id}: {self.patient.name} with Dr. {self.doctor.name} on {self.date} at {self.time_slot}"

    @property
    def is_upcoming(self):
        today = date.today()
        return self.date >= today and self.status in ['Pending', 'Confirmed']

    def get_status_badge(self):
        status_map = {
            'Pending': 'warning text-dark',
            'Confirmed': 'primary',
            'Completed': 'success',
            'Cancelled': 'danger',
        }
        return status_map.get(self.status, 'secondary')


class MedicalReport(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='medical_report'
    )
    diagnosis = models.TextField()
    prescription = models.TextField()
    notes = models.TextField(blank=True)
    report_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-report_date']

    def __str__(self):
        return f"Report #{self.id} for Appt #{self.appointment_id} - {self.appointment.patient.name}"
