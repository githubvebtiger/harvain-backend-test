from datetime import timedelta

from django.db import models
from django.utils import timezone

from user.user.models import User


class HistoryLog(models.Model):
    action_time = models.DateTimeField()
    type = models.CharField(max_length=255)
    change_message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.CharField(max_length=255, default="None")
    salesman = models.ForeignKey(
        on_delete=models.SET_NULL,
        related_name="histories",
        blank=True,
        null=True,
        to="user.Salesman",
    )
    additional_info = models.TextField(default="", null=True, blank=True)

    def save(self, *args, **kwargs):
        self.action_time = timezone.now() + timedelta(hours=3)
        super().save(*args, **kwargs)
