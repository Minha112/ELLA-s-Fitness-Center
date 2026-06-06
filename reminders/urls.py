from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.my_notifications, name='my_notifications'),
    path('admin/', views.admin_reminders, name='admin_reminders'),
    path('admin/send/<int:user_id>/<str:reminder_type>/', views.send_reminder, name='send_reminder'),
    path('admin/send-bulk/', views.send_bulk_reminders, name='send_bulk_reminders'),
]
