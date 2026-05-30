"""Models supporting password reset & email verification."""
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class PasswordResetToken(models.Model):
    """Single-use token issued for password reset."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    @property
    def is_valid(self) -> bool:
        return (not self.is_used) and self.expires_at > timezone.now()
