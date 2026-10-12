"""
URL configuration for hospital_project.
"""
from django.contrib import admin
from django.urls import path, include

# Customize Django Admin Header and Title
admin.site.site_header = "CarePulse Hospital Admin Portal"
admin.site.site_title = "CarePulse Hospital Management"
admin.site.index_title = "Hospital System Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('appointments.urls')),
]
