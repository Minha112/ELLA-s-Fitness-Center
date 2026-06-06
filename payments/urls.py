from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('process/', views.process_test_payment, name='process_payment'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('history/', views.payment_history, name='payment_history'),
    path('admin/', views.admin_payments, name='admin_payments'),
]
