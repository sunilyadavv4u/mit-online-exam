"""Email + in-app notifications via Celery."""
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_result_published_email(attempt_id: str) -> str:
    """Notify a student that their result has been published."""
    from apps.submissions.models import ExamAttempt
    from .models import Notification

    attempt = (ExamAttempt.objects
               .select_related('student', 'exam')
               .filter(id=attempt_id).first())
    if not attempt:
        return f'No attempt {attempt_id}'

    Notification.objects.create(
        user=attempt.student,
        notification_type=Notification.NotificationType.RESULT_PUBLISHED,
        title='Your exam result has been published',
        message=(f'Your result for "{attempt.exam.title}" is now available. '
                 f'Score: {attempt.total_score} / {attempt.exam.total_marks}.'),
        link=f'/results/{attempt.id}',
        metadata={'attempt_id': str(attempt.id)},
    )

    if attempt.student.email:
        send_mail(
            subject=f'Your result for {attempt.exam.title} is published',
            message=(
                f'Hello {attempt.student.full_name},\n\n'
                f'Your result for "{attempt.exam.title}" has been published.\n'
                f'Score: {attempt.total_score} / {attempt.exam.total_marks}\n'
                f'Status: {"Passed" if attempt.is_passed else "Not Passed"}\n\n'
                f'Login at {settings.FRONTEND_URL} to see full feedback.\n\n'
                f'Mewati Institute of Technology'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[attempt.student.email],
            fail_silently=True,
        )
    return 'ok'


@shared_task
def send_exam_reminder_email(exam_id: str) -> str:
    from apps.exams.models import Exam
    from .models import Notification

    exam = Exam.objects.filter(id=exam_id).prefetch_related('enrollments__student').first()
    if not exam:
        return f'No exam {exam_id}'

    for enrollment in exam.enrollments.select_related('student').all():
        student = enrollment.student
        Notification.objects.create(
            user=student,
            notification_type=Notification.NotificationType.EXAM_REMINDER,
            title=f'Reminder: {exam.title} starts soon',
            message=f'Your exam "{exam.title}" begins at {exam.start_time}.',
            link=f'/exams/{exam.slug}',
            metadata={'exam_id': str(exam.id)},
        )
    return 'ok'
