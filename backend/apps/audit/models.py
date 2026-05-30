"""Audit log model - records every authenticated state-changing API call."""
import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='audit_logs',
    )
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    status_code = models.PositiveIntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['method', 'path']),
        ]

    def __str__(self) -> str:
        return f'{self.method} {self.path} -> {self.status_code} ({self.user_id})'
