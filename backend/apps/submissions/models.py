"""Exam attempt + answer models."""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.exams.models import Exam
from apps.questions.models import Question, QuestionOption


class AttemptStatus(models.TextChoices):
    IN_PROGRESS = 'in_progress', _('In Progress')
    SUBMITTED = 'submitted', _('Submitted')
    AUTO_SUBMITTED = 'auto_submitted', _('Auto-Submitted')
    EVALUATED = 'evaluated', _('Evaluated')
    PUBLISHED = 'published', _('Published')


class ExamAttempt(models.Model):
    """A single student's attempt at an exam."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='exam_attempts',
    )
    status = models.CharField(
        max_length=20, choices=AttemptStatus.choices,
        default=AttemptStatus.IN_PROGRESS, db_index=True,
    )

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    # Auto-graded objective score (computed at submit time)
    objective_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Score added by teacher for descriptive/coding answers
    descriptive_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_passed = models.BooleanField(default=False)

    # Anti-cheating
    tab_switch_count = models.PositiveIntegerField(default=0)
    fullscreen_exit_count = models.PositiveIntegerField(default=0)
    proctor_flags = models.JSONField(default=list, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    # Random ordering of questions/options for this attempt
    question_order = models.JSONField(
        default=list, blank=True,
        help_text='List of question IDs in the order shown to the student.',
    )

    class Meta:
        unique_together = ('exam', 'student', 'started_at')
        ordering = ('-started_at',)
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['exam', 'status']),
        ]

    def __str__(self) -> str:
        return f'{self.student} -> {self.exam} [{self.status}]'

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            AttemptStatus.SUBMITTED,
            AttemptStatus.AUTO_SUBMITTED,
            AttemptStatus.EVALUATED,
            AttemptStatus.PUBLISHED,
        }


class Answer(models.Model):
    """A student's answer to a single question within an attempt."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(
        ExamAttempt, on_delete=models.CASCADE, related_name='answers',
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers',
    )

    # Objective answers
    selected_options = models.ManyToManyField(
        QuestionOption, blank=True, related_name='selected_in_answers',
    )
    # Free-form / fill-in-the-blank
    text_answer = models.TextField(blank=True)
    # Coding answers
    code_answer = models.TextField(blank=True)
    code_language = models.CharField(max_length=20, blank=True)
    code_run_results = models.JSONField(default=dict, blank=True)
    # File uploads (PDF/DOC/Image for descriptive)
    uploaded_file = models.FileField(upload_to='answers/', null=True, blank=True)

    # Auto / manual evaluation
    is_correct = models.BooleanField(null=True, blank=True)
    auto_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    manual_score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
    )
    teacher_comment = models.TextField(blank=True)

    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('attempt', 'question')
        ordering = ('attempt', 'question__order')

    def __str__(self) -> str:
        return f'Answer({self.attempt_id}, q={self.question_id})'

    @property
    def final_score(self):
        return self.manual_score if self.manual_score is not None else self.auto_score


class ProctorEvent(models.Model):
    """Granular log of proctoring events (tab switch, fullscreen exit, etc.)."""

    class EventType(models.TextChoices):
        TAB_SWITCH = 'tab_switch', _('Tab Switch')
        FULLSCREEN_EXIT = 'fullscreen_exit', _('Fullscreen Exit')
        COPY_PASTE = 'copy_paste', _('Copy/Paste')
        RIGHT_CLICK = 'right_click', _('Right Click')
        KEYBOARD_SHORTCUT = 'keyboard_shortcut', _('Keyboard Shortcut')
        DEV_TOOLS = 'dev_tools', _('Dev Tools Detected')
        WEBCAM_VIOLATION = 'webcam_violation', _('Webcam Violation')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(
        ExamAttempt, on_delete=models.CASCADE, related_name='proctor_events',
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
