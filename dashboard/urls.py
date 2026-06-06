from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard'),
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]
