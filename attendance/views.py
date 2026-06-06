from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from accounts.decorators import admin_required, client_required
from accounts.models import User
from members.models import Membership
from .models import Attendance


@client_required
def client_attendance(request):
    """Client: view their attendance history."""
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    attendances = Attendance.objects.filter(
        user=request.user,
        date__month=month,
        date__year=year,
    ).order_by('date')

    # Build calendar data
    import calendar
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    attendance_map = {}
    for att in attendances:
        attendance_map[att.date.day] = att

    total_present = attendances.filter(
        Q(morning_present=True) | Q(evening_present=True)
    ).count()

    context = {
        'calendar': cal,
        'month': month,
        'year': year,
        'month_name': month_name,
        'attendance_map': attendance_map,
        'total_present': total_present,
        'total_days': len([d for week in cal for d in week if d != 0]),
        'today': today,
    }
    return render(request, 'attendance/client_view.html', context)


@admin_required
def admin_attendance(request):
    """Admin: mark attendance for all members."""
    today = timezone.now().date()
    selected_date = request.GET.get('date', today.isoformat())
    try:
        from datetime import date as dt_date
        parts = selected_date.split('-')
        selected_date = dt_date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        selected_date = today

    # Get all active members
    active_member_ids = Membership.objects.filter(
        status='ACTIVE'
    ).values_list('user_id', flat=True).distinct()
    members = User.objects.filter(role='CLIENT', id__in=active_member_ids).order_by('first_name')

    # Get existing attendance for the date
    existing = Attendance.objects.filter(date=selected_date)
    attendance_map = {att.user_id: att for att in existing}

    member_data = []
    for member in members:
        att = attendance_map.get(member.id)
        member_data.append({
            'user': member,
            'morning': att.morning_present if att else False,
            'evening': att.evening_present if att else False,
        })

    context = {
        'members': member_data,
        'selected_date': selected_date,
        'today': today,
    }
    return render(request, 'attendance/admin_mark.html', context)


@admin_required
def save_attendance(request):
    """Admin: save attendance records."""
    if request.method == 'POST':
        date_str = request.POST.get('attendance_date')
        try:
            from datetime import date as dt_date
            parts = date_str.split('-')
            att_date = dt_date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError, TypeError):
            att_date = timezone.now().date()

        members = User.objects.filter(role='CLIENT')
        for member in members:
            morning = request.POST.get(f'morning_{member.id}') == 'on'
            evening = request.POST.get(f'evening_{member.id}') == 'on'

            if morning or evening:
                att, created = Attendance.objects.update_or_create(
                    user=member,
                    date=att_date,
                    defaults={
                        'morning_present': morning,
                        'evening_present': evening,
                        'marked_by': request.user,
                    }
                )
            else:
                # Remove attendance record if both unchecked
                Attendance.objects.filter(user=member, date=att_date).delete()

        messages.success(request, f'Attendance saved for {att_date.strftime("%d %b %Y")}!')
        return redirect(f'/attendance/admin/?date={att_date.isoformat()}')

    return redirect('admin_attendance')


@admin_required
def attendance_report(request):
    """Admin: view attendance reports."""
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    import calendar
    month_name = calendar.month_name[month]

    members = User.objects.filter(role='CLIENT').order_by('first_name')
    report_data = []
    for member in members:
        total = Attendance.objects.filter(
            user=member, date__month=month, date__year=year
        ).filter(Q(morning_present=True) | Q(evening_present=True)).count()
        report_data.append({'user': member, 'total': total})

    context = {
        'report': report_data,
        'month': month,
        'year': year,
        'month_name': month_name,
    }
    return render(request, 'attendance/report.html', context)
