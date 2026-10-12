# 🏥 CarePulse Hospital & Patient Appointment Management Portal

A full-stack, production-ready Django hospital appointment management platform built for outpatient consultation scheduling, real-time doctor availability checking, patient health records, and medical staff administration.

---

## 🌟 Key Features

### For Patients
- **Doctor Discovery & Search**: Filter doctors by clinical department (Cardiology, Pediatrics, Orthopedics, Neurology, General Medicine, Dermatology) or search by doctor name and specialization.
- **Doctor Profiles**: Detailed physician credentials, qualifications, experience, consultation fees, and available days.
- **Interactive Time Slot Selector**: Live slot availability checking via AJAX endpoint. Slots visually indicate **Available** or **Booked** (disabled) with double-booking prevention.
- **Instant Booking**: Simple appointment scheduling with server-side validation against past dates and duplicate bookings.
- **Printable Confirmation Vouchers**: Digital appointment slip with token ID, physician details, schedule, and patient guidelines.
- **Patient Portal (`/dashboard/`)**: Easy lookup by phone number or email to view metrics, upcoming visits, past appointments, and clinical medical reports.

### For Medical Staff & Administrators
- **Protected Staff Portal (`/staff/appointments/`)**: Restricted to authenticated staff and administrators (`is_staff=True`).
- **Comprehensive Workflow Actions**:
  - **Confirm**: Confirm pending appointment requests.
  - **Cancel**: Cancel appointments with confirmation alerts.
  - **Complete**: Mark consultations as completed.
  - **Issue Medical Reports**: Record clinical diagnosis, medication prescriptions, and follow-up directives.
- **Django Admin Interface (`/admin/`)**: Full administration of Doctors, Patients, Appointments, and Medical Reports with list filters, search fields, and date hierarchy.

---

## 🛠️ Mandatory Technology Stack

- **Backend**: Python 3.10 / 3.11+ & Django 5.2 / 6.x
- **Database**: SQLite (`db.sqlite3`) with Django ORM
- **Frontend**: HTML5, Vanilla CSS3, JavaScript ES6+, Bootstrap 5.3, Font Awesome 6
- **Production Web Server**: Gunicorn
- **Static Assets**: WhiteNoise (`CompressedManifestStaticFilesStorage`)
- **Deployment**: Render Blueprint (`render.yaml`)

---

## 📂 Project Structure

```text
hospital-appointment-portal/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── render.yaml
├── create_superuser.py
├── README.md
│
├── hospital_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── appointments/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_data.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── auth/
│   │   └── login.html
│   ├── doctors/
│   │   ├── doctor_list.html
│   │   └── doctor_detail.html
│   ├── appointments/
│   │   ├── appointment_form.html
│   │   └── appointment_success.html
│   ├── dashboard/
│   │   └── patient_dashboard.html
│   └── staff/
│       ├── appointment_management.html
│       └── medical_report_form.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── main.js
        └── appointments.js
```

---

## 🚀 Getting Started Locally

### 1. Clone & Set Up Virtual Environment

```bash
python -m venv venv
```

Activate the environment:
- **Windows (PowerShell)**: `venv\Scripts\Activate.ps1`
- **Windows (CMD)**: `venv\Scripts\activate.bat`
- **Linux/macOS**: `source venv/bin/activate`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Realistic Sample Data & Create Staff User

```bash
python manage.py seed_data
```

This populates:
- 10 Specialist doctors across Cardiology, Pediatrics, Orthopedics, Neurology, General Medicine, and Dermatology.
- 5 Sample patients.
- Appointments across all 4 statuses (**Pending**, **Confirmed**, **Completed**, **Cancelled**).
- Clinical medical reports with prescriptions.
- Admin staff credentials:
  - **Username**: `admin`
  - **Password**: `admin123`

### 5. Run the Local Development Server

```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

---

## 🌐 URLs & Endpoints

| URL Pattern | View Name | Description |
| :--- | :--- | :--- |
| `/` | `home` | Hospital home page with hero, statistics, departments, and doctors |
| `/doctors/` | `doctor_list` | Specialists directory with department filters and search |
| `/doctors/<id>/` | `doctor_detail` | Detailed physician profile and schedule |
| `/appointments/book/<id>/` | `appointment_book` | Interactive time slot booking page |
| `/appointments/success/<id>/` | `appointment_success` | Printable appointment confirmation slip |
| `/dashboard/` | `patient_dashboard` | Patient appointments dashboard and medical reports modal |
| `/api/available-slots/` | `api_available_slots` | AJAX API returning real-time slot availability for a date |
| `/login/` | `login` | Medical staff and admin authentication |
| `/logout/` | `logout` | Staff logout |
| `/staff/appointments/` | `staff_appointments` | Protected staff appointment management dashboard |
| `/staff/appointments/<id>/confirm/` | `staff_appointment_confirm` | Staff action: Confirm appointment |
| `/staff/appointments/<id>/cancel/` | `staff_appointment_cancel` | Staff action: Cancel appointment |
| `/staff/appointments/<id>/complete/` | `staff_appointment_complete` | Staff action: Mark consultation completed |
| `/staff/appointments/<id>/report/` | `staff_medical_report` | Issue or update clinical medical report |
| `/admin/` | Django Admin | Django Admin panel for Doctors, Patients, Appointments, Reports |

---

## 🔒 Security & Double-Booking Protection

1. **Database-Level Constraint**:
   ```python
   models.UniqueConstraint(
       fields=['doctor', 'date', 'time_slot'],
       condition=~models.Q(status='Cancelled'),
       name='unique_doctor_date_timeslot_active'
   )
   ```
2. **Server-Side Validation**: Every appointment submission is checked inside `AppointmentBookingForm.clean()` and `views.appointment_book` before saving.
3. **Past Date Rejection**: Dates prior to `date.today()` are rejected on both client and server sides.
4. **Staff Authorization**: Staff actions and management views are guarded by `@login_required` and `user.is_staff` checks.
5. **CSRF Protection**: All POST forms include `{% csrf_token %}`.

---

## ☁️ Render Deployment

The repository includes a ready-to-deploy `render.yaml` configuration:

- **Build Command**:
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python manage.py seed_data
  ```
- **Start Command**:
  ```bash
  gunicorn hospital_project.wsgi:application
  ```
- **Environment Variables**:
  - `PYTHON_VERSION`: `3.11.8`
  - `DEBUG`: `False`
  - `SECRET_KEY`: Automatically generated by Render
  - `DJANGO_SUPERUSER_USERNAME`: `admin`
  - `DJANGO_SUPERUSER_PASSWORD`: Automatically generated or custom

---

## 🧪 Automated Test Suite

Run the test suite covering models, views, slot API, double-booking prevention, and staff authorization:

```bash
python manage.py test
```
