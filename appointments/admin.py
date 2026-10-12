from django.contrib import admin
from .models import Doctor, Patient, Appointment, MedicalReport


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'department',
        'specialization',
        'consultation_fee',
        'available_days',
        'active',
    )
    list_filter = ('department', 'active')
    search_fields = ('name', 'specialization', 'qualification', 'bio')
    list_editable = ('active', 'consultation_fee')
    ordering = ('name',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'email',
        'gender',
        'date_of_birth',
        'blood_group',
        'created_at',
    )
    list_filter = ('gender', 'blood_group')
    search_fields = ('name', 'phone', 'email')
    ordering = ('-created_at',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'patient',
        'doctor',
        'date',
        'time_slot',
        'status',
        'created_date',
    )
    list_filter = ('status', 'doctor', 'date')
    search_fields = ('patient__name', 'doctor__name', 'patient__phone', 'reason')
    list_editable = ('status',)
    ordering = ('-date', 'time_slot')
    date_hierarchy = 'date'


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_patient',
        'get_doctor',
        'get_date',
        'report_date',
    )
    search_fields = (
        'appointment__patient__name',
        'appointment__doctor__name',
        'diagnosis',
        'prescription',
    )
    ordering = ('-report_date',)

    @admin.display(description='Patient')
    def get_patient(self, obj):
        return obj.appointment.patient.name

    @admin.display(description='Doctor')
    def get_doctor(self, obj):
        return obj.appointment.doctor.name

    @admin.display(description='Appointment Date')
    def get_date(self, obj):
        return f"{obj.appointment.date} ({obj.appointment.time_slot})"
