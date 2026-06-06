import os
import django
import random
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ellas_fitness.settings')
django.setup()

from django.utils import timezone
from accounts.models import User
from members.models import Membership
from payments.models import Payment
from attendance.models import Attendance
from reminders.models import Notification

def seed_db():
    print("Starting database seeding...")
    
    # 1. Create default Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@ellasfitness.com',
            'first_name': 'Ella',
            'last_name': 'Fitness Manager',
            'role': 'ADMIN',
            'is_superuser': True,
            'is_staff': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Created default admin account: admin / admin123")
    else:
        print("Admin account already exists.")

    # 2. Create sample Client members
    clients_data = [
        {
            'username': 'rahul',
            'first_name': 'Rahul',
            'last_name': 'Kumar',
            'email': 'rahul@gmail.com',
            'phone': '9876543210',
            'address': 'Sector 62, Noida, UP',
            'emergency_contact': '9988776655'
        },
        {
            'username': 'amit',
            'first_name': 'Amit',
            'last_name': 'Singh',
            'email': 'amit@gmail.com',
            'phone': '9812345670',
            'address': 'Indiranagar, Bangalore, KA',
            'emergency_contact': '9876501234'
        },
        {
            'username': 'neha',
            'first_name': 'Neha',
            'last_name': 'Sharma',
            'email': 'neha@gmail.com',
            'phone': '9000112233',
            'address': 'Andheri West, Mumbai, MH',
            'emergency_contact': '9112233445'
        }
    ]

    users = {}
    for c in clients_data:
        user, created = User.objects.get_or_create(
            username=c['username'],
            defaults={
                'email': c['email'],
                'first_name': c['first_name'],
                'last_name': c['last_name'],
                'phone': c['phone'],
                'address': c['address'],
                'emergency_contact': c['emergency_contact'],
                'role': 'CLIENT'
            }
        )
        if created:
            user.set_password('member123')
            user.save()
            print(f"Created member: {user.username} / member123")
        users[c['username']] = user

    # 3. Create memberships & payments
    today = timezone.now().date()

    # Rahul: Active 3 Months plan (started 20 days ago)
    rahul_user = users['rahul']
    if not Membership.objects.filter(user=rahul_user).exists():
        start = today - timedelta(days=22)
        end = start + timedelta(days=90)
        m = Membership.objects.create(
            user=rahul_user,
            plan='3_MONTH',
            start_date=start,
            end_date=end,
            amount=3199,
            status='ACTIVE'
        )
        Payment.objects.create(
            user=rahul_user,
            membership=m,
            amount=3199,
            transaction_id=Payment.generate_transaction_id(),
            payment_method='UPI',
            status='SUCCESS',
            created_at=timezone.now() - timedelta(days=22)
        )
        print("Created Active 3-Month membership for Rahul")

    # Amit: Expired 1 Month plan (started 45 days ago, expired 15 days ago)
    amit_user = users['amit']
    if not Membership.objects.filter(user=amit_user).exists():
        start = today - timedelta(days=45)
        end = start + timedelta(days=30)
        m = Membership.objects.create(
            user=amit_user,
            plan='1_MONTH',
            start_date=start,
            end_date=end,
            amount=1199,
            status='EXPIRED'
        )
        Payment.objects.create(
            user=amit_user,
            membership=m,
            amount=1199,
            transaction_id=Payment.generate_transaction_id(),
            payment_method='Credit Card',
            status='SUCCESS',
            created_at=timezone.now() - timedelta(days=45)
        )
        print("Created Expired 1-Month membership for Amit")

    # Neha: Active 6 Months plan (started 5 days ago)
    neha_user = users['neha']
    if not Membership.objects.filter(user=neha_user).exists():
        start = today - timedelta(days=5)
        end = start + timedelta(days=180)
        m = Membership.objects.create(
            user=neha_user,
            plan='6_MONTH',
            start_date=start,
            end_date=end,
            amount=5999,
            status='ACTIVE'
        )
        Payment.objects.create(
            user=neha_user,
            membership=m,
            amount=5999,
            transaction_id=Payment.generate_transaction_id(),
            payment_method='Net Banking',
            status='SUCCESS',
            created_at=timezone.now() - timedelta(days=5)
        )
        print("Created Active 6-Month membership for Neha")

    # 4. Generate random attendance records over the last 15 days
    print("Generating attendance logs...")
    for i in range(15):
        date_offset = today - timedelta(days=i)
        for username, user in users.items():
            # Only generate attendance if they had an active plan on that date
            active_m = Membership.objects.filter(
                user=user,
                start_date__lte=date_offset,
                end_date__gte=date_offset
            ).exists()
            
            if active_m:
                # 70% chance of attending
                if random.random() < 0.7:
                    morning = random.random() < 0.6
                    evening = random.random() < 0.5
                    if not morning and not evening:
                        morning = True  # Ensure at least one session if marked present
                    
                    Attendance.objects.get_or_create(
                        user=user,
                        date=date_offset,
                        defaults={
                            'morning_present': morning,
                            'evening_present': evening,
                            'marked_by': admin_user
                        }
                    )

    # 5. Create notifications
    Notification.objects.get_or_create(
        user=rahul_user,
        notification_type='WELCOME',
        defaults={
            'title': 'Welcome to ELLA\'s Fitness Center!',
            'message': 'Hi Rahul, we are thrilled to have you join us. Feel free to check out the cardio section.',
            'channel': 'IN_APP'
        }
    )
    Notification.objects.get_or_create(
        user=amit_user,
        notification_type='OVERDUE',
        defaults={
            'title': 'Overdue Fee Reminder',
            'message': 'Hi Amit, your 1 Month membership has expired. Renew your plan to continue gym access.',
            'channel': 'IN_APP'
        }
    )
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_db()
