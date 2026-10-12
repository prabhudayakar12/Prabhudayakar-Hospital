import json
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count
from django.utils import timezone

from .models import (
    Doctor,
    Patient,
    Appointment,
    MedicalReport,
    DEPARTMENT_CHOICES,
    TIME_SLOT_CHOICES,
    STATUS_CHOICES,
)
from .forms import (
    PatientForm,
    AppointmentForm,
    AppointmentBookingForm,
    MedicalReportForm,
)


def is_staff_check(user):
    return user.is_authenticated and user.is_staff


# -------------------------------------------------------------
# Public Views
# -------------------------------------------------------------

def home(request):
    """
    Hospital Home Page:
    Hero section, statistics, department cards, featured doctors,
    services, why choose us, CTA.
    """
    total_doctors = Doctor.objects.filter(active=True).count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='Completed').count()

    # Department counts
    department_counts = (
        Doctor.objects.filter(active=True)
        .values('department')
        .annotate(count=Count('id'))
    )
    dept_map = {item['department']: item['count'] for item in department_counts}
    departments_data = [
        {
            'name': code,
            'label': name,
            'count': dept_map.get(code, 0),
            'icon': {
                'Cardiology': 'fa-heart-pulse',
                'Pediatrics': 'fa-baby',
                'Orthopedics': 'fa-bone',
                'Neurology': 'fa-brain',
                'General Medicine': 'fa-stethoscope',
                'Dermatology': 'fa-hand-dots',
            }.get(code, 'fa-user-md')
        }
        for code, name in DEPARTMENT_CHOICES
    ]

    featured_doctors = Doctor.objects.filter(active=True).order_by('-experience_years')[:4]

    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'departments_data': departments_data,
        'featured_doctors': featured_doctors,
    }
    return render(request, 'home.html', context)


def doctor_list(request):
    """
    Doctor Listing Page with Department filtering & Search via Django ORM.
    """
    selected_dept = request.GET.get('department', '').strip()
    search_query = request.GET.get('q', '').strip()

    doctors = Doctor.objects.filter(active=True)

    if selected_dept and selected_dept != 'All':
        doctors = doctors.filter(department=selected_dept)

    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(qualification__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    # Counts for filter pills
    dept_stats = (
        Doctor.objects.filter(active=True)
        .values('department')
        .annotate(total=Count('id'))
    )
    dept_count_map = {item['department']: item['total'] for item in dept_stats}

    filter_options = [
        {'id': 'All', 'label': 'All Specialists', 'count': Doctor.objects.filter(active=True).count()},
        {'id': 'Cardiology', 'label': 'Cardiology', 'count': dept_count_map.get('Cardiology', 0)},
        {'id': 'Pediatrics', 'label': 'Pediatrics', 'count': dept_count_map.get('Pediatrics', 0)},
        {'id': 'Orthopedics', 'label': 'Orthopedics', 'count': dept_count_map.get('Orthopedics', 0)},
        {'id': 'Neurology', 'label': 'Neurology', 'count': dept_count_map.get('Neurology', 0)},
        {'id': 'General Medicine', 'label': 'General Medicine', 'count': dept_count_map.get('General Medicine', 0)},
        {'id': 'Dermatology', 'label': 'Dermatology', 'count': dept_count_map.get('Dermatology', 0)},
    ]

    context = {
        'doctors': doctors,
        'selected_dept': selected_dept or 'All',
        'search_query': search_query,
        'filter_options': filter_options,
    }
    return render(request, 'doctors/doctor_list.html', context)


def doctor_detail(request, pk):
    """
    Detailed Doctor Profile Page.
    """
    doctor = get_object_or_404(Doctor, pk=pk)
    related_doctors = Doctor.objects.filter(department=doctor.department, active=True).exclude(pk=doctor.pk)[:3]

    context = {
        'doctor': doctor,
        'related_doctors': related_doctors,
    }
    return render(request, 'doctors/doctor_detail.html', context)


def appointment_book(request, doctor_id):
    """
    Interactive Appointment Booking Page for a Doctor.
    Validates availability, dates, and double-booking on the server side.
    """
    doctor = get_object_or_404(Doctor, pk=doctor_id)

    if not doctor.active:
        messages.error(request, f"Dr. {doctor.name} is currently inactive and cannot accept appointments.")
        return redirect('doctor_list')

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, doctor=doctor)
        if form.is_valid():
            # Find or create patient by phone or email
            patient_phone = form.cleaned_data['patient_phone'].strip()
            patient_email = form.cleaned_data['patient_email'].strip()

            patient, created = Patient.objects.get_or_create(
                phone=patient_phone,
                defaults={
                    'name': form.cleaned_data['patient_name'].strip(),
                    'email': patient_email,
                    'date_of_birth': form.cleaned_data['date_of_birth'],
                    'gender': form.cleaned_data['gender'],
                    'blood_group': form.cleaned_data.get('blood_group', ''),
                    'address': form.cleaned_data.get('address', ''),
                }
            )

            if not created:
                # Update existing patient info if provided
                patient.name = form.cleaned_data['patient_name'].strip()
                patient.email = patient_email
                patient.date_of_birth = form.cleaned_data['date_of_birth']
                patient.gender = form.cleaned_data['gender']
                if form.cleaned_data.get('blood_group'):
                    patient.blood_group = form.cleaned_data['blood_group']
                if form.cleaned_data.get('address'):
                    patient.address = form.cleaned_data['address']
                patient.save()

            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=form.cleaned_data['appointment_date'],
                time_slot=form.cleaned_data['time_slot'],
                reason=form.cleaned_data['reason'],
                status='Pending',
            )

            # Store patient phone in session for effortless dashboard access
            request.session['patient_phone'] = patient.phone
            request.session['patient_email'] = patient.email

            messages.success(
                request,
                f"Appointment booked successfully for Dr. {doctor.name} on {appointment.date} at {appointment.time_slot}!"
            )
            return redirect('appointment_success', pk=appointment.pk)
        else:
            messages.error(request, "Please correct the highlighted errors in the appointment form.")
    else:
        # Prepopulate with today's date or tomorrow
        initial_date = date.today()
        # If doctor is not available today, find next available date
        for offset in range(7):
            candidate = date.fromordinal(initial_date.toordinal() + offset)
            if doctor.is_available_on(candidate):
                initial_date = candidate
                break

        form = AppointmentBookingForm(
            doctor=doctor,
            initial={
                'appointment_date': initial_date.isoformat(),
                'patient_phone': request.session.get('patient_phone', ''),
                'patient_email': request.session.get('patient_email', ''),
            }
        )

    context = {
        'doctor': doctor,
        'form': form,
        'time_slots': [slot[0] for slot in TIME_SLOT_CHOICES],
        'today': date.today().isoformat(),
    }
    return render(request, 'appointments/appointment_form.html', context)


def appointment_success(request, pk):
    """
    Appointment Confirmation & Receipt Slip.
    """
    appointment = get_object_or_404(Appointment, pk=pk)
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_success.html', context)


def patient_dashboard(request):
    """
    Patient Dashboard:
    Lookup appointments by session or phone/email input.
    Summary counters, upcoming appointments, past appointments, medical reports.
    """
    query = request.GET.get('patient_query', '').strip()
    session_phone = request.session.get('patient_phone', '')
    session_email = request.session.get('patient_email', '')

    active_query = query or session_phone or session_email

    patient = None
    appointments = Appointment.objects.none()

    if active_query:
        # Match phone with or without '+' prefix (since '+' can decode as space in URLs)
        clean_query = active_query.strip()
        patient = Patient.objects.filter(
            Q(phone__iexact=clean_query) |
            Q(phone__iexact='+' + clean_query) |
            Q(phone__icontains=clean_query.replace(' ', '')) |
            Q(email__iexact=clean_query)
        ).first()

        if patient:
            appointments = Appointment.objects.filter(patient=patient).select_related('doctor', 'medical_report')
            # Update session
            request.session['patient_phone'] = patient.phone
            request.session['patient_email'] = patient.email
        elif query:
            messages.warning(request, f"No patient records found matching '{query}'. Please check the phone number or email.")

    today = date.today()
    upcoming_appointments = appointments.filter(
        Q(date__gte=today) & ~Q(status__in=['Completed', 'Cancelled'])
    ).order_by('date', 'time_slot')

    past_appointments = appointments.filter(
        Q(date__lt=today) | Q(status__in=['Completed', 'Cancelled'])
    ).order_by('-date', '-time_slot')

    # Summary counts
    total_count = appointments.count()
    upcoming_count = upcoming_appointments.count()
    completed_count = appointments.filter(status='Completed').count()
    cancelled_count = appointments.filter(status='Cancelled').count()

    context = {
        'patient': patient,
        'active_query': active_query,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'total_count': total_count,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'today': today,
    }
    return render(request, 'dashboard/patient_dashboard.html', context)


def api_available_slots(request):
    """
    AJAX API endpoint returning real-time availability for a doctor on a specific date.
    Used by interactive appointment slot picker.
    """
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'error': 'doctor_id and date parameters are required.'}, status=400)

    try:
        doctor = Doctor.objects.get(pk=doctor_id)
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (Doctor.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid doctor ID or date format.'}, status=400)

    # Check if date is in past
    is_past_date = target_date < date.today()

    # Check doctor availability for weekday
    is_doctor_available_day = doctor.is_available_on(target_date)

    # Booked slots for this doctor on this date (excluding Cancelled)
    booked_slots = set(
        Appointment.objects.filter(
            doctor=doctor,
            date=target_date
        ).exclude(status='Cancelled').values_list('time_slot', flat=True)
    )

    slots_data = []
    for slot_code, slot_label in TIME_SLOT_CHOICES:
        is_booked = slot_code in booked_slots
        is_disabled = is_past_date or (not is_doctor_available_day) or is_booked

        slots_data.append({
            'slot': slot_code,
            'label': slot_label,
            'is_booked': is_booked,
            'is_available': not is_booked and not is_past_date and is_doctor_available_day,
            'is_disabled': is_disabled,
        })

    return JsonResponse({
        'doctor_name': doctor.name,
        'date': date_str,
        'is_past_date': is_past_date,
        'is_doctor_available_day': is_doctor_available_day,
        'available_days_str': doctor.available_days,
        'slots': slots_data,
    })


# -------------------------------------------------------------
# Staff / Admin Portal Views
# -------------------------------------------------------------

def staff_login(request):
    """
    Medical Staff Login View.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('staff_appointments')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next', 'staff_appointments')
                return redirect(next_url)
            else:
                messages.error(request, "Access denied. Only hospital staff and administrators are authorized.")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


def staff_logout(request):
    """
    Medical Staff Logout View.
    """
    logout(request)
    messages.info(request, "You have been logged out of the staff management portal.")
    return redirect('home')


@login_required(login_url='login')
def staff_appointments(request):
    """
    Staff / Admin Appointment Management Portal:
    Only authenticated staff users can access.
    Lists all appointments with filters by Status, Doctor, Date, Search.
    Allows Confirm, Cancel, Complete, and Medical Report actions.
    """
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to view the hospital staff portal.")
        return redirect('home')

    status_filter = request.GET.get('status', '').strip()
    doctor_filter = request.GET.get('doctor', '').strip()
    date_filter = request.GET.get('date', '').strip()
    search_query = request.GET.get('q', '').strip()

    appointments = Appointment.objects.select_related('patient', 'doctor', 'medical_report').all()

    if status_filter and status_filter != 'All':
        appointments = appointments.filter(status=status_filter)

    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)

    if date_filter:
        appointments = appointments.filter(date=date_filter)

    if search_query:
        appointments = appointments.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__phone__icontains=search_query) |
            Q(doctor__name__icontains=search_query) |
            Q(reason__icontains=search_query)
        )

    # Metrics
    today = date.today()
    all_appointments = Appointment.objects.all()
    today_count = all_appointments.filter(date=today).count()
    pending_count = all_appointments.filter(status='Pending').count()
    confirmed_count = all_appointments.filter(status='Confirmed').count()
    completed_count = all_appointments.filter(status='Completed').count()
    cancelled_count = all_appointments.filter(status='Cancelled').count()

    doctors_list = Doctor.objects.filter(active=True)

    context = {
        'appointments': appointments,
        'doctors_list': doctors_list,
        'status_filter': status_filter or 'All',
        'doctor_filter': doctor_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        'today': today,
        'metrics': {
            'today': today_count,
            'pending': pending_count,
            'confirmed': confirmed_count,
            'completed': completed_count,
            'cancelled': cancelled_count,
            'total': all_appointments.count(),
        }
    }
    return render(request, 'staff/appointment_management.html', context)


@login_required(login_url='login')
def staff_appointment_confirm(request, pk):
    """
    Staff Action: Confirm an appointment.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden("Unauthorized")

    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Confirmed'
    appointment.save()

    messages.success(
        request,
        f"Appointment #{appointment.id} for {appointment.patient.name} has been CONFIRMED."
    )
    return redirect('staff_appointments')


@login_required(login_url='login')
def staff_appointment_cancel(request, pk):
    """
    Staff Action: Cancel an appointment.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden("Unauthorized")

    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Cancelled'
    appointment.save()

    messages.warning(
        request,
        f"Appointment #{appointment.id} for {appointment.patient.name} has been CANCELLED."
    )
    return redirect('staff_appointments')


@login_required(login_url='login')
def staff_appointment_complete(request, pk):
    """
    Staff Action: Mark appointment as Completed.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden("Unauthorized")

    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Completed'
    appointment.save()

    messages.success(
        request,
        f"Appointment #{appointment.id} for {appointment.patient.name} marked as COMPLETED. You can now issue a medical report."
    )
    return redirect('staff_appointments')


@login_required(login_url='login')
def staff_medical_report(request, appointment_id):
    """
    Staff Action: Create or edit medical report for an appointment.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden("Unauthorized")

    appointment = get_object_or_404(Appointment, pk=appointment_id)
    report = getattr(appointment, 'medical_report', None)

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, instance=report)
        if form.is_valid():
            new_report = form.save(commit=False)
            new_report.appointment = appointment
            new_report.save()

            # Ensure appointment status is Completed
            if appointment.status != 'Completed':
                appointment.status = 'Completed'
                appointment.save()

            messages.success(request, f"Medical report for {appointment.patient.name} saved successfully!")
            return redirect('staff_appointments')
    else:
        form = MedicalReportForm(instance=report)

    context = {
        'appointment': appointment,
        'form': form,
        'report': report,
    }
    return render(request, 'staff/medical_report_form.html', context)
