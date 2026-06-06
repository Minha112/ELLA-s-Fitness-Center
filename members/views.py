from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import admin_required
from accounts.models import User
from accounts.forms import AdminMemberForm
from .models import Membership


def join_gym(request):
    """Public page to show membership plans. If logged in, allows selection."""
    plans = [
        {'key': '1_MONTH', 'name': '1 Month', 'price': 1199, 'duration': '30 Days'},
        {'key': '3_MONTH', 'name': '3 Months', 'price': 3199, 'duration': '90 Days'},
        {'key': '6_MONTH', 'name': '6 Months', 'price': 5999, 'duration': '180 Days'},
    ]
    return render(request, 'members/join.html', {'plans': plans})


@login_required
def select_plan(request, plan):
    """After selecting a plan, redirect to checkout."""
    if plan not in ['1_MONTH', '3_MONTH', '6_MONTH']:
        messages.error(request, 'Invalid plan selected.')
        return redirect('join_gym')
    request.session['selected_plan'] = plan
    return redirect('checkout')


@login_required
def my_membership(request):
    """Client views their membership details."""
    memberships = Membership.objects.filter(user=request.user)
    active = memberships.filter(status='ACTIVE').first()
    if active:
        active.check_and_update_status()
    return render(request, 'members/my_membership.html', {
        'active_membership': active,
        'past_memberships': memberships.exclude(status='ACTIVE'),
    })


# --- Admin views ---

@admin_required
def member_list(request):
    """Admin: list all members with search."""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    members = User.objects.filter(role='CLIENT').order_by('-date_joined')

    if query:
        members = members.filter(
            first_name__icontains=query
        ) | members.filter(
            last_name__icontains=query
        ) | members.filter(
            email__icontains=query
        ) | members.filter(
            phone__icontains=query
        )
        members = members.filter(role='CLIENT')

    # Annotate with membership status
    member_data = []
    for member in members:
        active_membership = Membership.objects.filter(user=member, status='ACTIVE').first()
        if active_membership:
            active_membership.check_and_update_status()
            active_membership = Membership.objects.filter(user=member, status='ACTIVE').first()

        if status_filter == 'active' and not active_membership:
            continue
        if status_filter == 'expired' and active_membership:
            continue

        member_data.append({
            'user': member,
            'membership': active_membership,
        })

    return render(request, 'members/list.html', {
        'members': member_data,
        'query': query,
        'status_filter': status_filter,
    })


@admin_required
def member_detail(request, user_id):
    """Admin: view individual member details."""
    member = get_object_or_404(User, id=user_id, role='CLIENT')
    memberships = Membership.objects.filter(user=member)
    active = memberships.filter(status='ACTIVE').first()
    from payments.models import Payment
    payments = Payment.objects.filter(user=member)
    from attendance.models import Attendance
    recent_attendance = Attendance.objects.filter(user=member)[:30]

    return render(request, 'members/detail.html', {
        'member': member,
        'active_membership': active,
        'memberships': memberships,
        'payments': payments,
        'recent_attendance': recent_attendance,
    })


@admin_required
def member_add(request):
    """Admin: add a new member."""
    if request.method == 'POST':
        form = AdminMemberForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'CLIENT'
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                user.set_password('member123')  # Default password
            user.save()
            messages.success(request, f'Member {user.get_full_name()} added successfully!')
            return redirect('member_list')
    else:
        form = AdminMemberForm()
    return render(request, 'members/form.html', {'form': form, 'title': 'Add New Member'})


@admin_required
def member_edit(request, user_id):
    """Admin: edit a member."""
    member = get_object_or_404(User, id=user_id, role='CLIENT')
    if request.method == 'POST':
        form = AdminMemberForm(request.POST, instance=member)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'Member {user.get_full_name()} updated!')
            return redirect('member_detail', user_id=user.id)
    else:
        form = AdminMemberForm(instance=member)
    return render(request, 'members/form.html', {'form': form, 'title': f'Edit {member.get_full_name()}'})


@admin_required
def member_delete(request, user_id):
    """Admin: delete a member."""
    member = get_object_or_404(User, id=user_id, role='CLIENT')
    if request.method == 'POST':
        name = member.get_full_name()
        member.delete()
        messages.success(request, f'Member {name} has been removed.')
        return redirect('member_list')
    return render(request, 'members/confirm_delete.html', {'member': member})
