from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from accounts.decorators import admin_required, client_required
from accounts.models import User
from members.models import Membership
from payments.models import Payment
from attendance.models import Attendance
from reminders.models import Notification


@login_required
def dashboard_redirect(request):
    if request.user.is_admin_user:
        return admin_dashboard(request)
    return client_dashboard(request)


@client_required
def client_dashboard(request):
    user = request.user
    today = timezone.now().date()

    # Get active membership
    active_membership = Membership.objects.filter(
        user=user, status='ACTIVE'
    ).first()

    # Check and update expired
    if active_membership:
        active_membership.check_and_update_status()
        if active_membership.status == 'EXPIRED':
            active_membership = None

    # Get last payment
    last_payment = Payment.objects.filter(user=user, status='SUCCESS').first()

    # Get attendance stats for current month
    month_start = today.replace(day=1)
    month_attendance = Attendance.objects.filter(
        user=user, date__gte=month_start, date__lte=today
    ).filter(Q(morning_present=True) | Q(evening_present=True)).count()

    # Unread notifications count
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()

    context = {
        'membership': active_membership,
        'last_payment': last_payment,
        'month_attendance': month_attendance,
        'today': today,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'dashboard/client.html', context)


@admin_required
def admin_dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Update expired memberships
    expired = Membership.objects.filter(status='ACTIVE', end_date__lt=today)
    expired.update(status='EXPIRED')

    # Stats
    total_members = User.objects.filter(role='CLIENT').count()
    active_members = Membership.objects.filter(status='ACTIVE').values('user').distinct().count()
    expired_members = total_members - active_members
    monthly_revenue = Payment.objects.filter(
        status='SUCCESS', created_at__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Today's attendance
    today_attendance = Attendance.objects.filter(date=today).filter(
        Q(morning_present=True) | Q(evening_present=True)
    ).count()

    # Recent payments
    recent_payments = Payment.objects.filter(status='SUCCESS').select_related('user')[:5]

    # Expiring soon (within 7 days)
    expiring_soon = Membership.objects.filter(
        status='ACTIVE',
        end_date__lte=today + timezone.timedelta(days=7),
        end_date__gte=today,
    ).select_related('user')

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'expired_members': expired_members,
        'monthly_revenue': monthly_revenue,
        'today_attendance': today_attendance,
        'recent_payments': recent_payments,
        'expiring_soon': expiring_soon,
        'today': today,
    }
    return render(request, 'dashboard/admin.html', context)
