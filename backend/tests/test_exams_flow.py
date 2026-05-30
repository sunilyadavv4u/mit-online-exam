"""Exam + question flow tests: create, attempt, submit, auto-grade."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.exams.models import Exam, ExamEnrollment, ExamStatus
from apps.exams.models import Subject
from apps.questions.models import Question, QuestionOption, QuestionType
from apps.submissions.models import AttemptStatus, ExamAttempt


@pytest.fixture
def subject(db, teacher):
    return Subject.objects.create(name='Python', code='PY', created_by=teacher)


@pytest.fixture
def exam_with_mcq(db, teacher, student, subject):
    now = timezone.now()
    exam = Exam.objects.create(
        title='Sample Exam',
        slug='sample-exam',
        subject=subject,
        status=ExamStatus.LIVE,
        duration_minutes=30,
        total_marks=Decimal('2'),
        passing_marks=Decimal('1'),
        start_time=now - timedelta(minutes=5),
        end_time=now + timedelta(hours=1),
        created_by=teacher,
    )
    q = Question.objects.create(
        exam=exam, subject=subject,
        question_type=QuestionType.SINGLE_CHOICE,
        text='2 + 2 = ?',
        marks=Decimal('2'),
        created_by=teacher,
    )
    QuestionOption.objects.create(question=q, text='3', is_correct=False, order=0)
    QuestionOption.objects.create(question=q, text='4', is_correct=True, order=1)
    QuestionOption.objects.create(question=q, text='5', is_correct=False, order=2)

    ExamEnrollment.objects.create(exam=exam, student=student, enrolled_by=teacher)
    return exam, q


@pytest.mark.django_db
def test_student_can_start_attempt(auth_client, student, exam_with_mcq):
    exam, _ = exam_with_mcq
    client = auth_client(student, 'Student@12345')
    res = client.post('/api/v1/submissions/attempts/start/', {'exam_id': str(exam.id)}, format='json')
    assert res.status_code == 201, res.data
    assert res.data['status'] == AttemptStatus.IN_PROGRESS


@pytest.mark.django_db
def test_student_submit_correct_mcq_gets_full_marks(auth_client, student, exam_with_mcq):
    exam, question = exam_with_mcq
    client = auth_client(student, 'Student@12345')

    start = client.post('/api/v1/submissions/attempts/start/', {'exam_id': str(exam.id)}, format='json')
    attempt_id = start.data['id']
    correct_option = question.options.get(is_correct=True)

    save = client.post(
        f'/api/v1/submissions/attempts/{attempt_id}/answer/',
        {'question': str(question.id), 'selected_options': [str(correct_option.id)]},
        format='json',
    )
    assert save.status_code == 200, save.data

    submit = client.post(f'/api/v1/submissions/attempts/{attempt_id}/submit/', {}, format='json')
    assert submit.status_code == 200, submit.data
    assert float(submit.data['total_score']) == float(question.marks)
    assert submit.data['status'] in {AttemptStatus.SUBMITTED, AttemptStatus.PUBLISHED}


@pytest.mark.django_db
def test_student_cannot_attempt_without_enrollment(auth_client, student, teacher, subject):
    now = timezone.now()
    exam = Exam.objects.create(
        title='Restricted', slug='restricted',
        subject=subject, status=ExamStatus.LIVE,
        duration_minutes=30, total_marks=Decimal('1'),
        start_time=now - timedelta(minutes=1),
        end_time=now + timedelta(hours=1),
        created_by=teacher,
    )
    client = auth_client(student, 'Student@12345')
    res = client.post('/api/v1/submissions/attempts/start/', {'exam_id': str(exam.id)}, format='json')
    assert res.status_code == 403


@pytest.mark.django_db
def test_proctor_event_increments_counter(auth_client, student, exam_with_mcq):
    exam, _ = exam_with_mcq
    client = auth_client(student, 'Student@12345')
    start = client.post('/api/v1/submissions/attempts/start/', {'exam_id': str(exam.id)}, format='json')
    attempt_id = start.data['id']

    res = client.post(
        f'/api/v1/submissions/attempts/{attempt_id}/proctor-event/',
        {'event_type': 'tab_switch'}, format='json',
    )
    assert res.status_code == 201

    attempt = ExamAttempt.objects.get(id=attempt_id)
    assert attempt.tab_switch_count == 1
