from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from appointments.models import Doctor, Patient, Appointment, MedicalReport

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds realistic sample doctors, patients, appointments, and medical reports for CarePulse Hospital'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting CarePulse Hospital data seeding...'))

        # 1. Create Staff / Superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@carepulse.hospital',
                'first_name': 'Chief Medical',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created staff user 'admin' with password 'admin123'."))
        else:
            self.stdout.write(self.style.SUCCESS("Updated staff user 'admin' password to 'admin123'."))

        # 2. Seed Doctors
        doctors_data = [
            # Cardiology
            {
                'name': 'Robert Harrison',
                'department': 'Cardiology',
                'specialization': 'Interventional Cardiology, Coronary Angioplasty & Heart Failure',
                'qualification': 'MD, FACC, FSCAI (Harvard Medical)',
                'experience_years': 18,
                'consultation_fee': Decimal('180.00'),
                'available_days': 'Mon, Tue, Wed, Thu, Fri',
                'active': True,
                'email': 'r.harrison@carepulse.hospital',
                'phone': '+1 (555) 201-1001',
                'bio': 'Dr. Robert Harrison has over 18 years of clinical experience in interventional cardiology and preventive cardiovascular therapies. He has performed over 2,500 cardiac procedures.',
            },
            {
                'name': 'Priya Patel',
                'department': 'Cardiology',
                'specialization': 'Pediatric Cardiology & Cardiac Electrophysiology',
                'qualification': 'MBBS, MD, DM Cardiology (Johns Hopkins)',
                'experience_years': 12,
                'consultation_fee': Decimal('160.00'),
                'available_days': 'Mon, Wed, Fri, Sat',
                'active': True,
                'email': 'p.patel@carepulse.hospital',
                'phone': '+1 (555) 201-1002',
                'bio': 'Dr. Priya Patel specializes in arrhythmias, cardiac pacing, and pediatric congenital cardiology with extensive published research in cardiac imaging.',
            },
            # Pediatrics
            {
                'name': 'Sarah Jenkins',
                'department': 'Pediatrics',
                'specialization': 'General Pediatrics, Neonatal Care & Child Immunization',
                'qualification': 'MD Pediatrics, FAAP (Stanford Medicine)',
                'experience_years': 14,
                'consultation_fee': Decimal('130.00'),
                'available_days': 'Mon, Tue, Wed, Thu, Fri',
                'active': True,
                'email': 's.jenkins@carepulse.hospital',
                'phone': '+1 (555) 201-1003',
                'bio': 'Dr. Sarah Jenkins is renowned for compassionate, family-centered infant and adolescent healthcare, developmental evaluations, and childhood allergy management.',
            },
            {
                'name': 'David Mitchell',
                'department': 'Pediatrics',
                'specialization': 'Pediatric Pulmonology & Asthma Management',
                'qualification': 'MBBS, MD Pediatrics (Columbia University)',
                'experience_years': 10,
                'consultation_fee': Decimal('140.00'),
                'available_days': 'Tue, Thu, Sat',
                'active': True,
                'email': 'd.mitchell@carepulse.hospital',
                'phone': '+1 (555) 201-1004',
                'bio': 'Dr. David Mitchell leads pediatric respiratory wellness, specializing in childhood chronic asthma and pulmonary diagnostics.',
            },
            # Orthopedics
            {
                'name': 'Marcus Vance',
                'department': 'Orthopedics',
                'specialization': 'Joint Replacement, Arthroscopy & Sports Medicine',
                'qualification': 'MS Ortho, FRCS Orth (Oxford University)',
                'experience_years': 20,
                'consultation_fee': Decimal('200.00'),
                'available_days': 'Mon, Tue, Wed, Thu, Fri',
                'active': True,
                'email': 'm.vance@carepulse.hospital',
                'phone': '+1 (555) 201-1005',
                'bio': 'Dr. Marcus Vance is a master orthopedic surgeon who has performed over 3,000 robotic knee and hip replacements for athletes and seniors.',
            },
            {
                'name': 'Elena Rostova',
                'department': 'Orthopedics',
                'specialization': 'Spine Surgery & Musculoskeletal Rehabilitation',
                'qualification': 'MD Orthopedics, Fellowship Spine (Mayo Clinic)',
                'experience_years': 15,
                'consultation_fee': Decimal('190.00'),
                'available_days': 'Mon, Wed, Fri',
                'active': True,
                'email': 'e.rostova@carepulse.hospital',
                'phone': '+1 (555) 201-1006',
                'bio': 'Dr. Elena Rostova provides minimally invasive spine corrections, disc replacement, and comprehensive back pain management.',
            },
            # Neurology
            {
                'name': 'Alistair Chen',
                'department': 'Neurology',
                'specialization': 'Stroke Neuropathy, Epilepsy & Cognitive Disorders',
                'qualification': 'MD, PhD Neurology (UCSF)',
                'experience_years': 16,
                'consultation_fee': Decimal('210.00'),
                'available_days': 'Mon, Tue, Wed, Thu, Fri',
                'active': True,
                'email': 'a.chen@carepulse.hospital',
                'phone': '+1 (555) 201-1007',
                'bio': 'Dr. Alistair Chen is Chief of Neurosciences with expertise in acute ischemic stroke intervention, migraine management, and neurological EEG analysis.',
            },
            {
                'name': 'Catherine Ross',
                'department': 'Neurology',
                'specialization': 'Movement Disorders, Parkinsonism & Multiple Sclerosis',
                'qualification': 'MD Neurology (Yale School of Medicine)',
                'experience_years': 11,
                'consultation_fee': Decimal('175.00'),
                'available_days': 'Tue, Thu, Sat',
                'active': True,
                'email': 'c.ross@carepulse.hospital',
                'phone': '+1 (555) 201-1008',
                'bio': 'Dr. Catherine Ross specializes in neurodegenerative therapeutic trials, botulinum therapy for dystonia, and neuro-immunology.',
            },
            # General Medicine
            {
                'name': 'James O\'Connor',
                'department': 'General Medicine',
                'specialization': 'Internal Medicine, Hypertension & Metabolic Health',
                'qualification': 'MBBS, MD Internal Medicine (Edinburgh)',
                'experience_years': 17,
                'consultation_fee': Decimal('110.00'),
                'available_days': 'Mon, Tue, Wed, Thu, Fri',
                'active': True,
                'email': 'j.oconnor@carepulse.hospital',
                'phone': '+1 (555) 201-1009',
                'bio': 'Dr. James O\'Connor manages comprehensive adult internal diseases, chronic lifestyle health conditions, and preventive geriatric care.',
            },
            # Dermatology
            {
                'name': 'Maya Lin',
                'department': 'Dermatology',
                'specialization': 'Clinical Dermatology, Skin Oncology & Laser Aesthetics',
                'qualification': 'MD Dermatology, FAAD (NYU Grossman)',
                'experience_years': 9,
                'consultation_fee': Decimal('145.00'),
                'available_days': 'Mon, Wed, Thu, Sat',
                'active': True,
                'email': 'm.lin@carepulse.hospital',
                'phone': '+1 (555) 201-1010',
                'bio': 'Dr. Maya Lin focuses on autoimmune dermatological conditions, eczema, skin cancer screening, and therapeutic dermatosurgery.',
            },
        ]

        doctors = []
        for doc_info in doctors_data:
            doc, _ = Doctor.objects.update_or_create(
                name=doc_info['name'],
                defaults=doc_info
            )
            doctors.append(doc)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(doctors)} doctors across all departments."))

        # 3. Seed Patients
        patients_data = [
            {
                'name': 'Johnathan Smith',
                'email': 'john.smith@example.com',
                'phone': '+1 555-0101',
                'date_of_birth': date(1985, 4, 12),
                'gender': 'Male',
                'blood_group': 'O+',
                'address': '742 Evergreen Terrace, Springfield',
            },
            {
                'name': 'Emily Davis',
                'email': 'emily.davis@example.com',
                'phone': '+1 555-0102',
                'date_of_birth': date(1992, 8, 24),
                'gender': 'Female',
                'blood_group': 'A+',
                'address': '124 Conch Street, Riverdale',
            },
            {
                'name': 'Michael Brown',
                'email': 'michael.b@example.com',
                'phone': '+1 555-0103',
                'date_of_birth': date(1978, 11, 3),
                'gender': 'Male',
                'blood_group': 'B+',
                'address': '55 Maple Avenue, Brooklyn, NY',
            },
            {
                'name': 'Sophia Wilson',
                'email': 'sophia.w@example.com',
                'phone': '+1 555-0104',
                'date_of_birth': date(2018, 5, 19),
                'gender': 'Female',
                'blood_group': 'AB+',
                'address': '890 Park Boulevard, Queens, NY',
            },
            {
                'name': 'Lucas Garcia',
                'email': 'lucas.g@example.com',
                'phone': '+1 555-0105',
                'date_of_birth': date(1990, 1, 15),
                'gender': 'Male',
                'blood_group': 'O-',
                'address': '312 Ocean View Lane, Jersey City',
            },
        ]

        patients = []
        for p_data in patients_data:
            patient, _ = Patient.objects.update_or_create(
                phone=p_data['phone'],
                defaults=p_data
            )
            patients.append(patient)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(patients)} sample patients."))

        # 4. Helper to pick valid dates
        today = date.today()

        def find_valid_day(doctor, base_date, forward=True):
            direction = 1 if forward else -1
            candidate = base_date
            for _ in range(14):
                if doctor.is_available_on(candidate):
                    return candidate
                candidate += timedelta(days=direction)
            return base_date

        # Clear existing seed appointments to avoid constraint collisions on re-seed
        Appointment.objects.all().delete()

        # Seed sample appointments demonstrating all statuses: Pending, Confirmed, Completed, Cancelled
        harrison = Doctor.objects.get(name='Robert Harrison')
        jenkins = Doctor.objects.get(name='Sarah Jenkins')
        vance = Doctor.objects.get(name='Marcus Vance')
        chen = Doctor.objects.get(name='Alistair Chen')
        oconnor = Doctor.objects.get(name='James O\'Connor')

        p_john = Patient.objects.get(phone='+1 555-0101')
        p_emily = Patient.objects.get(phone='+1 555-0102')
        p_michael = Patient.objects.get(phone='+1 555-0103')
        p_sophia = Patient.objects.get(phone='+1 555-0104')
        p_lucas = Patient.objects.get(phone='+1 555-0105')

        # 1. Upcoming Pending Appointment
        upcoming_date_1 = find_valid_day(harrison, today + timedelta(days=2), forward=True)
        appt1 = Appointment.objects.create(
            patient=p_john,
            doctor=harrison,
            date=upcoming_date_1,
            time_slot='10:00 AM',
            reason='Mild chest tightness on exertion and follow-up on echocardiogram test.',
            status='Pending',
        )

        # 2. Upcoming Confirmed Appointment
        upcoming_date_2 = find_valid_day(jenkins, today + timedelta(days=3), forward=True)
        appt2 = Appointment.objects.create(
            patient=p_sophia,
            doctor=jenkins,
            date=upcoming_date_2,
            time_slot='09:30 AM',
            reason='Routine child growth milestone evaluation and seasonal MMR vaccination.',
            status='Confirmed',
        )

        # 3. Upcoming Confirmed Appointment 2
        upcoming_date_3 = find_valid_day(vance, today + timedelta(days=4), forward=True)
        appt3 = Appointment.objects.create(
            patient=p_michael,
            doctor=vance,
            date=upcoming_date_3,
            time_slot='02:30 PM',
            reason='Severe right knee pain and mobility stiffness after tennis match.',
            status='Confirmed',
        )

        # 4. Past Completed Appointment with Medical Report
        past_date_1 = find_valid_day(harrison, today - timedelta(days=5), forward=False)
        appt4 = Appointment.objects.create(
            patient=p_john,
            doctor=harrison,
            date=past_date_1,
            time_slot='11:00 AM',
            reason='Initial cardiology consultation for irregular resting heart pulse and fatigue.',
            status='Completed',
        )
        MedicalReport.objects.create(
            appointment=appt4,
            diagnosis='Benign sinus tachycardia with mild Grade-1 Essential Hypertension. Resting ECG demonstrates normal QTc and ST segments. Troponin-I levels within physiological limits.',
            prescription='1. Tab Metoprolol Succinate 25mg - 1 tablet once daily morning after breakfast (30 days)\n2. Tab Telmisartan 40mg - 1 tablet daily (30 days)\n3. Tab CoQ10 100mg - 1 capsule daily after dinner',
            notes='Advised 30 minutes of brisk walking daily. Reduce dietary sodium to under 2,000mg/day. Return for 24-hour Holter monitoring in 4 weeks.',
        )

        # 5. Past Completed Appointment with Medical Report 2
        past_date_2 = find_valid_day(chen, today - timedelta(days=8), forward=False)
        appt5 = Appointment.objects.create(
            patient=p_emily,
            doctor=chen,
            date=past_date_2,
            time_slot='03:00 PM',
            reason='Recurrent migraine episodes with photophobia and aura occurring twice weekly.',
            status='Completed',
        )
        MedicalReport.objects.create(
            appointment=appt5,
            diagnosis='Chronic vestibular migraine without acute focal neuro-deficit. Cranial MRI reveals no intracranial space-occupying lesion.',
            prescription='1. Tab Rizatriptan 10mg - Take 1 tablet at earliest onset of headache aura (max 2/day)\n2. Tab Topiramate 25mg - 1 tablet at bedtime for prophylactic prevention\n3. Tab Magnesium Glycinate 400mg - 1 capsule daily',
            notes='Maintain a headache diary logging triggers (sleep deficit, caffeine intake, screen time). Follow-up in 6 weeks.',
        )

        # 6. Past Cancelled Appointment
        past_date_3 = find_valid_day(oconnor, today - timedelta(days=3), forward=False)
        appt6 = Appointment.objects.create(
            patient=p_lucas,
            doctor=oconnor,
            date=past_date_3,
            time_slot='04:00 PM',
            reason='Seasonal viral flu symptoms and throat discomfort.',
            status='Cancelled',
        )

        self.stdout.write(self.style.SUCCESS(
            "Seeded appointments: Pending, Confirmed, Completed (with reports), and Cancelled."
        ))
        self.stdout.write(self.style.SUCCESS('CarePulse Hospital database successfully seeded!'))
