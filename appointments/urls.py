from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home, name='home'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('appointments/book/<int:doctor_id>/', views.appointment_book, name='appointment_book'),
    path('appointments/success/<int:pk>/', views.appointment_success, name='appointment_success'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),

    # AJAX API
    path('api/available-slots/', views.api_available_slots, name='api_available_slots'),

    # Auth
    path('login/', views.staff_login, name='login'),
    path('logout/', views.staff_logout, name='logout'),

    # Staff Portal
    path('staff/appointments/', views.staff_appointments, name='staff_appointments'),
    path('staff/appointments/<int:pk>/confirm/', views.staff_appointment_confirm, name='staff_appointment_confirm'),
    path('staff/appointments/<int:pk>/cancel/', views.staff_appointment_cancel, name='staff_appointment_cancel'),
    path('staff/appointments/<int:pk>/complete/', views.staff_appointment_complete, name='staff_appointment_complete'),
    path('staff/appointments/<int:appointment_id>/report/', views.staff_medical_report, name='staff_medical_report'),
]
