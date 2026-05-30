"""Stores history of AI chat / conversion requests."""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AIRequestType(models.TextChoices):
    CONVERT_SQL_TO_SPARK = 'sql_to_spark', _('SQL → Spark SQL')
    CONVERT_SQL_TO_PYSPARK = 'sql_to_pyspark', _('SQL → PySpark')
    CONVERT_PYTHON_TO_PYSPARK = 'python_to_pyspark', _('Python → PySpark')
    EXPLAIN_CODE = 'explain_code', _('Explain Code')
    GENERATE_QUESTION = 'generate_question', _('Generate Question')
    GRADE_DESCRIPTIVE = 'grade_descriptive', _('Grade Descriptive Answer')
    CHAT = 'chat', _('General Chat')


class AIRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='ai_requests',
    )
    request_type = models.CharField(
        max_length=40, choices=AIRequestType.choices, default=AIRequestType.CHAT,
    )
    prompt = models.TextField()
    response = models.TextField(blank=True)
    is_success = models.BooleanField(default=False)
    error = models.TextField(blank=True)
    latency_ms = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [models.Index(fields=['user', 'request_type'])]

    def __str__(self) -> str:
        return f'AIRequest({self.request_type}, user={self.user_id})'
