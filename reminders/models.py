from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    TYPE_CHOICES = [
        ('FEE_REMINDER', 'Monthly Fee Reminder'),
        ('EXPIRY_WARNING', 'Membership Expiry Warning'),
        ('OVERDUE', 'Overdue Payment'),
        ('WELCOME', 'Welcome Message'),
        ('RENEWAL', 'Renewal Confirmation'),
    ]
    CHANNEL_CHOICES = [
        ('IN_APP', 'In-App'),
        ('WHATSAPP', 'WhatsApp (Test)'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='IN_APP')
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.title} → {self.user.get_full_name()}"
