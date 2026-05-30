"""Background tasks for post-submission processing."""
from celery import shared_task

from apps.questions.models import QuestionType
from apps.submissions.models import ExamAttempt


@shared_task
def process_attempt_post_submit(attempt_id: str) -> str:
    """Compute final scores after a student submits.

    Auto-creates a draft Evaluation row when descriptive answers exist so that
    teachers can immediately see the attempt in their pending evaluation queue.
    """
    from .models import Evaluation, EvaluationStatus

    attempt = ExamAttempt.objects.filter(id=attempt_id).first()
    if not attempt:
        return f'Attempt {attempt_id} not found'

    has_descriptive = attempt.answers.filter(
        question__question_type=QuestionType.DESCRIPTIVE,
    ).exists()
    has_coding = attempt.answers.filter(
        question__question_type=QuestionType.CODING,
    ).exists()

    teacher = attempt.exam.created_by
    if has_descriptive or has_coding:
        Evaluation.objects.get_or_create(
            attempt=attempt,
            defaults={
                'evaluator': teacher,
                'status': EvaluationStatus.DRAFT,
            },
        )
    return f'Processed {attempt_id}'
