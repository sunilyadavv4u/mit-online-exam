"""Subject + exam models."""
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    """A teaching subject e.g. Python, PySpark, SQL."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=80, blank=True,
                            help_text='Optional icon class / emoji for the UI')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='subjects_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} ({self.code})'


class ExamStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    SCHEDULED = 'scheduled', _('Scheduled')
    LIVE = 'live', _('Live')
    COMPLETED = 'completed', _('Completed')
    ARCHIVED = 'archived', _('Archived')


class ExamType(models.TextChoices):
    OBJECTIVE = 'objective', _('Objective')
    DESCRIPTIVE = 'descriptive', _('Descriptive')
    CODING = 'coding', _('Coding')
    MIXED = 'mixed', _('Mixed')


class Exam(models.Model):
    """An exam/test instance owned by a teacher."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name='exams',
    )
    exam_type = models.CharField(
        max_length=20, choices=ExamType.choices, default=ExamType.MIXED,
    )
    status = models.CharField(
        max_length=20, choices=ExamStatus.choices, default=ExamStatus.DRAFT,
        db_index=True,
    )
    duration_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    passing_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    negative_marking = models.DecimalField(
        max_digits=4, decimal_places=2, default=0,
        help_text='Marks deducted per wrong objective answer (0 to disable).',
    )
    randomize_questions = models.BooleanField(default=False)
    randomize_options = models.BooleanField(default=False)
    show_results_immediately = models.BooleanField(
        default=False,
        help_text='If true, students see their objective score immediately. '
                  'Descriptive results always wait for teacher publication.',
    )
    allow_retake = models.BooleanField(default=False)
    enable_proctoring = models.BooleanField(
        default=True,
        help_text='Enable client side anti-cheat (fullscreen, tab switching, etc).',
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='exams_created',
    )
    enrolled_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ExamEnrollment',
        through_fields=('exam', 'student'),
        related_name='enrolled_exams',
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-start_time',)
        indexes = [
            models.Index(fields=['status', 'start_time']),
            models.Index(fields=['subject', 'status']),
        ]

    def __str__(self) -> str:
        return f'{self.title} ({self.subject.code})'

    @property
    def is_live(self) -> bool:
        now = timezone.now()
        return self.status == ExamStatus.LIVE and self.start_time <= now <= self.end_time

    @property
    def is_open_for_attempt(self) -> bool:
        now = timezone.now()
        return self.status in {ExamStatus.LIVE, ExamStatus.SCHEDULED} and now <= self.end_time


class ExamEnrollment(models.Model):
    """Mapping of which students are eligible to attempt which exam."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='exam_enrollments',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    enrolled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enrollments_created',
    )

    class Meta:
        unique_together = ('exam', 'student')
        ordering = ('-enrolled_at',)

    def __str__(self) -> str:
        return f'{self.student} -> {self.exam}'
