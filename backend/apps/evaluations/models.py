"""Models for evaluations and result publication tracking."""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.submissions.models import ExamAttempt


class EvaluationStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    SUBMITTED = 'submitted', _('Submitted')
    PUBLISHED = 'published', _('Published')


class Evaluation(models.Model):
    """Top-level wrapper for the manual evaluation of a single attempt."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.OneToOneField(
        ExamAttempt, on_delete=models.CASCADE, related_name='evaluation',
    )
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='evaluations',
    )
    status = models.CharField(
        max_length=20, choices=EvaluationStatus.choices,
        default=EvaluationStatus.DRAFT, db_index=True,
    )
    overall_comment = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return f'Eval({self.attempt_id}) [{self.status}]'
