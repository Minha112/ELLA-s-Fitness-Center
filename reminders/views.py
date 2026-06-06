from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import admin_required
from accounts.models import User
from members.models import Membership
from .models import Notification


@login_required
def my_notifications(request):
    """Client: view their notifications."""
    notifications = Notification.objects.filter(user=request.user)
    # Mark all as read
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'reminders/my_notifications.html', {'notifications': notifications})


@admin_required
def admin_reminders(request):
    """Admin: view and manage reminders."""
    today = timezone.now().date()

    # Expiring within 7 days
    expiring = Membership.objects.filter(
        status='ACTIVE',
        end_date__lte=today + timezone.timedelta(days=7),
        end_date__gte=today,
    ).select_related('user')

    # Already expired (overdue)
    overdue = Membership.objects.filter(
        status='EXPIRED',
    ).select_related('user').order_by('-end_date')[:20]

    # Recent notifications sent
    recent = Notification.objects.all().select_related('user')[:20]

    context = {
        'expiring': expiring,
        'overdue': overdue,
        'recent_notifications': recent,
        'today': today,
    }
    return render(request, 'reminders/admin_list.html', context)


@admin_required
def send_reminder(request, user_id, reminder_type):
    """Admin: send a test reminder to a member."""
    user = User.objects.filter(id=user_id, role='CLIENT').first()
    if not user:
        messages.error(request, 'Member not found.')
        return redirect('admin_reminders')

    type_map = {
        'fee': ('FEE_REMINDER', 'Monthly Fee Reminder',
                f'Hi {user.first_name}, your monthly fee is due. Please make your payment at ELLA\'s Fitness Center.'),
        'expiry': ('EXPIRY_WARNING', 'Membership Expiring Soon',
                   f'Hi {user.first_name}, your membership is expiring soon. Renew now to continue your fitness journey!'),
        'overdue': ('OVERDUE', 'Overdue Payment Notice',
                    f'Hi {user.first_name}, your membership has expired. Please renew to continue accessing the gym.'),
    }

    if reminder_type not in type_map:
        messages.error(request, 'Invalid reminder type.')
        return redirect('admin_reminders')

    notif_type, title, message = type_map[reminder_type]
    Notification.objects.create(
        user=user,
        notification_type=notif_type,
        title=title,
        message=message,
        channel='IN_APP',
    )
    messages.success(request, f'Reminder sent to {user.get_full_name()} (Test Mode - In-App)')
    return redirect('admin_reminders')


@admin_required
def send_bulk_reminders(request):
    """Admin: send reminders to all expiring/overdue members."""
    if request.method == 'POST':
        today = timezone.now().date()
        count = 0

        # Expiring soon
        expiring = Membership.objects.filter(
            status='ACTIVE',
            end_date__lte=today + timezone.timedelta(days=7),
            end_date__gte=today,
        ).select_related('user')

        for m in expiring:
            Notification.objects.create(
                user=m.user,
                notification_type='EXPIRY_WARNING',
                title='Membership Expiring Soon',
                message=f'Hi {m.user.first_name}, your membership expires on {m.end_date.strftime("%d %b %Y")}. Renew now!',
                channel='IN_APP',
            )
            count += 1

        # Overdue
        overdue = Membership.objects.filter(status='EXPIRED').select_related('user')
        for m in overdue:
            Notification.objects.create(
                user=m.user,
                notification_type='OVERDUE',
                title='Membership Expired',
                message=f'Hi {m.user.first_name}, your membership expired on {m.end_date.strftime("%d %b %Y")}. Please renew.',
                channel='IN_APP',
            )
            count += 1

        messages.success(request, f'Sent {count} reminder(s) in test mode.')
        return redirect('admin_reminders')

    return redirect('admin_reminders')
