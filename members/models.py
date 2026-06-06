from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Membership(models.Model):
    PLAN_CHOICES = [
        ('1_MONTH', '1 Month'),
        ('3_MONTH', '3 Months'),
        ('6_MONTH', '6 Months'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('PENDING', 'Pending Payment'),
    ]
    PLAN_PRICES = {
        '1_MONTH': 1199,
        '3_MONTH': 3199,
        '6_MONTH': 5999,
    }
    PLAN_DAYS = {
        '1_MONTH': 30,
        '3_MONTH': 90,
        '6_MONTH': 180,
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_plan_display()} ({self.status})"

    @property
    def days_remaining(self):
        if self.status != 'ACTIVE':
            return 0
        remaining = (self.end_date - timezone.now().date()).days
        return max(0, remaining)

    @property
    def total_days(self):
        return self.PLAN_DAYS.get(self.plan, 30)

    @property
    def progress_percentage(self):
        if self.total_days == 0:
            return 0
        elapsed = self.total_days - self.days_remaining
        return min(100, int((elapsed / self.total_days) * 100))

    @property
    def is_expiring_soon(self):
        return self.status == 'ACTIVE' and self.days_remaining <= 7

    def check_and_update_status(self):
        if self.status == 'ACTIVE' and self.end_date < timezone.now().date():
            self.status = 'EXPIRED'
            self.save()

    @classmethod
    def get_price(cls, plan):
        return cls.PLAN_PRICES.get(plan, 0)

    @classmethod
    def create_membership(cls, user, plan):
        start_date = timezone.now().date()
        days = cls.PLAN_DAYS.get(plan, 30)
        end_date = start_date + timedelta(days=days)
        amount = cls.PLAN_PRICES.get(plan, 0)
        return cls.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            amount=amount,
            status='ACTIVE',
        )
