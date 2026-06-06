from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import admin_required, client_required
from members.models import Membership
from .models import Payment


@login_required
def checkout(request):
    """Checkout page — shows plan summary and test payment button."""
    plan = request.session.get('selected_plan')
    if not plan:
        messages.error(request, 'Please select a membership plan first.')
        return redirect('join_gym')

    plan_info = {
        '1_MONTH': {'name': '1 Month', 'price': 1199, 'duration': '30 Days'},
        '3_MONTH': {'name': '3 Months', 'price': 3199, 'duration': '90 Days'},
        '6_MONTH': {'name': '6 Months', 'price': 5999, 'duration': '180 Days'},
    }
    selected = plan_info.get(plan)
    if not selected:
        messages.error(request, 'Invalid plan.')
        return redirect('join_gym')

    context = {
        'plan_key': plan,
        'plan': selected,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def process_test_payment(request):
    """Simulate a test payment — always succeeds."""
    if request.method == 'POST':
        plan = request.session.get('selected_plan')
        if not plan:
            messages.error(request, 'No plan selected.')
            return redirect('join_gym')

        # Create membership
        membership = Membership.create_membership(request.user, plan)

        # Create test payment record
        payment = Payment.objects.create(
            user=request.user,
            membership=membership,
            amount=membership.amount,
            transaction_id=Payment.generate_transaction_id(),
            payment_method='Test Payment (Simulated)',
            status='SUCCESS',
            notes=f'Test mode payment for {membership.get_plan_display()}',
        )

        # Clear session
        del request.session['selected_plan']

        messages.success(request, 'Payment successful! Your membership is now active.')
        return redirect('payment_success', payment_id=payment.id)

    return redirect('checkout')


@login_required
def payment_success(request, payment_id):
    """Show payment success page."""
    payment = Payment.objects.filter(id=payment_id, user=request.user).first()
    if not payment:
        return redirect('client_dashboard')
    return render(request, 'payments/success.html', {'payment': payment})


@client_required
def payment_history(request):
    """Client: view payment history."""
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'payments/history.html', {'payments': payments})


@admin_required
def admin_payments(request):
    """Admin: view all payment records."""
    query = request.GET.get('q', '')
    payments = Payment.objects.all().select_related('user', 'membership')
    if query:
        payments = payments.filter(
            user__first_name__icontains=query
        ) | payments.filter(
            user__last_name__icontains=query
        ) | payments.filter(
            transaction_id__icontains=query
        )

    from django.db.models import Sum
    total_revenue = Payment.objects.filter(status='SUCCESS').aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'payments': payments,
        'query': query,
        'total_revenue': total_revenue,
    }
    return render(request, 'payments/admin_list.html', context)
