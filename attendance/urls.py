from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.client_attendance, name='client_attendance'),
    path('admin/', views.admin_attendance, name='admin_attendance'),
    path('admin/save/', views.save_attendance, name='save_attendance'),
    path('admin/report/', views.attendance_report, name='attendance_report'),
]
