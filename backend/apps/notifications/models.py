"""In-app notification model."""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        EXAM_SCHEDULED = 'exam_scheduled', _('Exam Scheduled')
        EXAM_REMINDER = 'exam_reminder', _('Exam Reminder')
        RESULT_PUBLISHED = 'result_published', _('Result Published')
        EVALUATION_PENDING = 'evaluation_pending', _('Evaluation Pending')
        SYSTEM = 'system', _('System')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(
        max_length=30, choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self) -> str:
        return f'{self.title} -> {self.user_id}'
