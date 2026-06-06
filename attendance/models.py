from django.db import models
from django.conf import settings
from django.utils import timezone


class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    morning_present = models.BooleanField(default=False)
    evening_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='marked_attendances'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        status = []
        if self.morning_present:
            status.append('Morning')
        if self.evening_present:
            status.append('Evening')
        return f"{self.user.get_full_name()} - {self.date} ({', '.join(status) or 'Absent'})"

    @property
    def status_display(self):
        if self.morning_present and self.evening_present:
            return 'Both Sessions'
        elif self.morning_present:
            return 'Morning Only'
        elif self.evening_present:
            return 'Evening Only'
        return 'Absent'
