from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from appointments.models import Doctor, Patient, Appointment, MedicalReport

User = get_user_model()


class HospitalPortalTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff_test',
            password='testpassword123',
            is_staff=True
        )

        # Create normal user
        self.regular_user = User.objects.create_user(
            username='patient_user',
            password='testpassword123',
            is_staff=False
        )

        # Create test Doctor
        self.doctor = Doctor.objects.create(
            name='Arthur Stone',
            department='Cardiology',
            specialization='Electrophysiology & Heart Rhythm',
            qualification='MD, FACC',
            experience_years=15,
            consultation_fee=Decimal('150.00'),
            available_days='Mon, Tue, Wed, Thu, Fri',
            active=True,
            email='a.stone@hospital.com',
            phone='+1 555-1010',
            bio='Experienced cardiologist specializing in arrhythmia disorders.'
        )

        # Inactive Doctor
        self.inactive_doctor = Doctor.objects.create(
            name='Retired Doctor',
            department='Neurology',
            specialization='Neuroscience',
            qualification='MD',
            experience_years=30,
            consultation_fee=Decimal('200.00'),
            available_days='Mon, Tue, Wed, Thu, Fri',
            active=False
        )

        # Create test Patient
        self.patient = Patient.objects.create(
            name='Alice Johnson',
            email='alice@example.com',
            phone='+1 555-2020',
            date_of_birth=date(1995, 5, 20),
            gender='Female',
            blood_group='O+',
            address='123 Test St, NY'
        )

    def test_01_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CarePulse')
        self.assertContains(response, 'Dr. Arthur Stone')

    def test_02_doctor_list_and_search(self):
        response = self.client.get(reverse('doctor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Arthur Stone')
        # Inactive doctor should not appear in active doctor list
        self.assertNotContains(response, 'Retired Doctor')

        # Department filter
        response_cardio = self.client.get(reverse('doctor_list') + '?department=Cardiology')
        self.assertEqual(response_cardio.status_code, 200)
        self.assertContains(response_cardio, 'Dr. Arthur Stone')

        # Search filter
        response_search = self.client.get(reverse('doctor_list') + '?q=Stone')
        self.assertEqual(response_search.status_code, 200)
        self.assertContains(response_search, 'Dr. Arthur Stone')

        # Non-matching search
        response_empty = self.client.get(reverse('doctor_list') + '?q=NonExistentSpecialist999')
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, 'No Doctors Found')

    def test_03_doctor_detail_page(self):
        response = self.client.get(reverse('doctor_detail', kwargs={'pk': self.doctor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Arthur Stone')
        self.assertContains(response, '$150.00')

    def test_04_appointment_booking_and_double_booking_prevention(self):
        # Choose upcoming weekday
        today = date.today()
        target_date = today + timedelta(days=1)
        while not self.doctor.is_available_on(target_date):
            target_date += timedelta(days=1)

        post_data = {
            'patient_name': 'Alice Johnson',
            'patient_email': 'alice@example.com',
            'patient_phone': '+1 555-2020',
            'date_of_birth': '1995-05-20',
            'gender': 'Female',
            'blood_group': 'O+',
            'address': '123 Test St, NY',
            'appointment_date': target_date.strftime('%Y-%m-%d'),
            'time_slot': '10:00 AM',
            'reason': 'Palpitations and shortness of breath during morning jogs.',
        }

        # 1. First booking should succeed
        response = self.client.post(
            reverse('appointment_book', kwargs={'doctor_id': self.doctor.id}),
            data=post_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect to appointment_success

        appointment = Appointment.objects.filter(
            doctor=self.doctor,
            date=target_date,
            time_slot='10:00 AM'
        ).first()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.status, 'Pending')

        # 2. Duplicate booking for the SAME doctor, SAME date, and SAME time slot MUST FAIL!
        duplicate_data = {
            'patient_name': 'Bob Williams',
            'patient_email': 'bob@example.com',
            'patient_phone': '+1 555-3030',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'blood_group': 'A+',
            'address': '456 Elm St',
            'appointment_date': target_date.strftime('%Y-%m-%d'),
            'time_slot': '10:00 AM',  # Same slot
            'reason': 'Routine heart checkup.',
        }

        response_dup = self.client.post(
            reverse('appointment_book', kwargs={'doctor_id': self.doctor.id}),
            data=duplicate_data
        )
        # Form should re-render with validation error (status 200, not 302 redirect)
        self.assertEqual(response_dup.status_code, 200)
        self.assertContains(response_dup, 'already booked for 10:00 AM')

    def test_05_past_date_rejection(self):
        past_date = date.today() - timedelta(days=2)
        post_data = {
            'patient_name': 'Alice Johnson',
            'patient_email': 'alice@example.com',
            'patient_phone': '+1 555-2020',
            'date_of_birth': '1995-05-20',
            'gender': 'Female',
            'appointment_date': past_date.strftime('%Y-%m-%d'),
            'time_slot': '10:00 AM',
            'reason': 'Past date test.',
        }

        response = self.client.post(
            reverse('appointment_book', kwargs={'doctor_id': self.doctor.id}),
            data=post_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cannot be in the past')

    def test_06_available_slots_api(self):
        today = date.today()
        target_date = today + timedelta(days=1)
        while not self.doctor.is_available_on(target_date):
            target_date += timedelta(days=1)

        # Create a booked appointment on 09:30 AM
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=target_date,
            time_slot='09:30 AM',
            reason='Testing slot api',
            status='Pending'
        )

        api_url = reverse('api_available_slots') + f'?doctor_id={self.doctor.id}&date={target_date.strftime("%Y-%m-%d")}'
        response = self.client.get(api_url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['is_doctor_available_day'])

        # Verify 09:30 AM is marked is_booked: True
        slot_930 = next(s for s in data['slots'] if s['slot'] == '09:30 AM')
        self.assertTrue(slot_930['is_booked'])
        self.assertFalse(slot_930['is_available'])

        # Verify 10:00 AM is available
        slot_1000 = next(s for s in data['slots'] if s['slot'] == '10:00 AM')
        self.assertFalse(slot_1000['is_booked'])
        self.assertTrue(slot_1000['is_available'])

    def test_07_patient_dashboard(self):
        # Create an upcoming appointment
        today = date.today()
        target_date = today + timedelta(days=2)
        while not self.doctor.is_available_on(target_date):
            target_date += timedelta(days=1)

        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=target_date,
            time_slot='11:00 AM',
            reason='Checkup',
            status='Confirmed'
        )

        # Look up by phone
        response = self.client.get(reverse('patient_dashboard') + f'?patient_query={self.patient.phone}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Johnson')
        self.assertContains(response, 'Confirmed')

    def test_08_staff_authorization_and_workflow(self):
        # 1. Unauthenticated request to staff management should redirect to login
        response_unauth = self.client.get(reverse('staff_appointments'))
        self.assertEqual(response_unauth.status_code, 302)
        self.assertIn('/login/', response_unauth.url)

        # 2. Regular non-staff user should be denied access
        self.client.login(username='patient_user', password='testpassword123')
        response_nonstaff = self.client.get(reverse('staff_appointments'))
        # Should redirect to home or reject
        self.assertEqual(response_nonstaff.status_code, 302)
        self.client.logout()

        # 3. Staff user can access dashboard
        self.client.login(username='staff_test', password='testpassword123')
        response_staff = self.client.get(reverse('staff_appointments'))
        self.assertEqual(response_staff.status_code, 200)
        self.assertContains(response_staff, 'Hospital Appointment Management')

        # Create appointment to test actions
        today = date.today()
        target_date = today + timedelta(days=2)
        while not self.doctor.is_available_on(target_date):
            target_date += timedelta(days=1)

        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=target_date,
            time_slot='02:00 PM',
            reason='Action test',
            status='Pending'
        )

        # Action: Confirm
        confirm_url = reverse('staff_appointment_confirm', kwargs={'pk': appt.pk})
        res_conf = self.client.get(confirm_url)
        self.assertEqual(res_conf.status_code, 302)
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'Confirmed')

        # Action: Complete
        complete_url = reverse('staff_appointment_complete', kwargs={'pk': appt.pk})
        res_comp = self.client.get(complete_url)
        self.assertEqual(res_comp.status_code, 302)
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'Completed')

        # Action: Create Medical Report
        report_url = reverse('staff_medical_report', kwargs={'appointment_id': appt.pk})
        res_report_get = self.client.get(report_url)
        self.assertEqual(res_report_get.status_code, 200)

        res_report_post = self.client.post(report_url, {
            'diagnosis': 'Arrhythmia resolved. Normal sinus rhythm.',
            'prescription': 'Tab Metoprolol 25mg OD',
            'notes': 'Follow up in 3 months',
        })
        self.assertEqual(res_report_post.status_code, 302)
        self.assertTrue(MedicalReport.objects.filter(appointment=appt).exists())
