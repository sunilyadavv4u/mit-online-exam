"""Question types & question bank models."""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.exams.models import Exam, Subject


class QuestionType(models.TextChoices):
    SINGLE_CHOICE = 'single_choice', _('Single Choice MCQ')
    MULTIPLE_CHOICE = 'multiple_choice', _('Multiple Choice MCQ')
    TRUE_FALSE = 'true_false', _('True / False')
    FILL_BLANK = 'fill_blank', _('Fill in the Blanks')
    DESCRIPTIVE = 'descriptive', _('Descriptive / Written')
    CODING = 'coding', _('Coding')


class DifficultyLevel(models.TextChoices):
    EASY = 'easy', _('Easy')
    MEDIUM = 'medium', _('Medium')
    HARD = 'hard', _('Hard')


class CodingLanguage(models.TextChoices):
    PYTHON = 'python', _('Python')
    SQL = 'sql', _('SQL')
    PYSPARK = 'pyspark', _('PySpark')
    JAVA = 'java', _('Java')


class Question(models.Model):
    """A reusable question stored in a teacher's bank and attached to exams."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name='questions',
        null=True, blank=True,
        help_text='If null, the question lives in the question bank only.',
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name='questions',
    )
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', null=True, blank=True)
    difficulty = models.CharField(
        max_length=10, choices=DifficultyLevel.choices, default=DifficultyLevel.MEDIUM,
    )
    marks = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    negative_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    order = models.PositiveIntegerField(default=0)

    # For fill-in-the-blank or one-line answers
    correct_answer_text = models.TextField(
        blank=True,
        help_text='Used for fill-in-the-blank / one line answer matching.',
    )

    # For coding questions
    coding_language = models.CharField(
        max_length=20, choices=CodingLanguage.choices, blank=True, default='',
    )
    starter_code = models.TextField(blank=True)
    expected_output = models.TextField(
        blank=True,
        help_text='Expected output / reference solution for graders.',
    )

    # Reusable question bank flag
    is_in_bank = models.BooleanField(default=True)
    tags = models.CharField(max_length=255, blank=True,
                            help_text='Comma separated tags')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='questions_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('exam', 'order', 'created_at')
        indexes = [
            models.Index(fields=['exam', 'order']),
            models.Index(fields=['subject', 'question_type']),
        ]

    def __str__(self) -> str:
        snippet = (self.text[:60] + '...') if len(self.text) > 60 else self.text
        return f'[{self.get_question_type_display()}] {snippet}'


class QuestionOption(models.Model):
    """An MCQ option."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='options',
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order',)

    def __str__(self) -> str:
        marker = '✓' if self.is_correct else ' '
        return f'[{marker}] {self.text}'


class CodingTestCase(models.Model):
    """Hidden / visible test cases for coding questions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='test_cases',
    )
    input_data = models.TextField(blank=True)
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order',)

    def __str__(self) -> str:
        kind = 'hidden' if self.is_hidden else 'sample'
        return f'TC#{self.order} ({kind}) for {self.question_id}'
