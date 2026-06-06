from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


def home(request):
    plans = [
        {'key': '1_MONTH', 'name': '1 Month', 'price': 1199, 'duration': '30 Days', 'popular': False},
        {'key': '3_MONTH', 'name': '3 Months', 'price': 3199, 'duration': '90 Days', 'popular': True},
        {'key': '6_MONTH', 'name': '6 Months', 'price': 5999, 'duration': '180 Days', 'popular': False},
    ]
    return render(request, 'public/home.html', {'plans': plans})


urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('members/', include('members.urls')),
    path('attendance/', include('attendance.urls')),
    path('payments/', include('payments.urls')),
    path('reminders/', include('reminders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
