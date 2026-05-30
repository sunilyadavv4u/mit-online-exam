"""Coding grading: hidden test cases run on exam submit."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.exams.models import Exam, ExamEnrollment, ExamStatus, Subject
from apps.questions.models import (
    CodingLanguage,
    CodingTestCase,
    Question,
    QuestionType,
)
from apps.submissions.coding_grading import grade_coding_answer
from apps.submissions.models import Answer, ExamAttempt


@pytest.fixture
def coding_exam(db, teacher, student):
    subject = Subject.objects.create(name='DSA', code='DSA-T', created_by=teacher)
    now = timezone.now()
    exam = Exam.objects.create(
        title='DSA Test',
        slug='dsa-coding-test',
        subject=subject,
        status=ExamStatus.LIVE,
        duration_minutes=30,
        total_marks=Decimal('10'),
        passing_marks=Decimal('5'),
        start_time=now - timedelta(minutes=1),
        end_time=now + timedelta(hours=1),
        created_by=teacher,
    )
    q = Question.objects.create(
        exam=exam,
        subject=subject,
        question_type=QuestionType.CODING,
        text='Print double the integer from stdin.',
        coding_language=CodingLanguage.PYTHON,
        marks=Decimal('10'),
        created_by=teacher,
    )
    CodingTestCase.objects.create(
        question=q, input_data='3', expected_output='6', is_hidden=False, order=1,
    )
    CodingTestCase.objects.create(
        question=q, input_data='9', expected_output='18', is_hidden=True, order=2,
    )
    ExamEnrollment.objects.create(exam=exam, student=student, enrolled_by=teacher)
    return exam, q


@pytest.mark.django_db
def test_grade_coding_runs_hidden_tests(student, coding_exam):
    exam, question = coding_exam
    attempt = ExamAttempt.objects.create(exam=exam, student=student)
    answer = Answer.objects.create(
        attempt=attempt,
        question=question,
        code_answer='import sys\nprint(int(sys.stdin.read())*2)',
        code_language='python',
    )
    data = grade_coding_answer(answer)
    assert data['passed'] == 2
    assert data['total'] == 2
    hidden_rows = [d for d in data['details'] if d.get('hidden')]
    assert len(hidden_rows) == 1
    assert 'input' not in hidden_rows[0]


@pytest.mark.django_db
def test_submit_runs_hidden_and_scores(auth_client, student, coding_exam):
    exam, question = coding_exam
    client = auth_client(student, 'Student@12345')
    start = client.post('/api/v1/submissions/attempts/start/', {'exam_id': str(exam.id)}, format='json')
    assert start.status_code == 201
    attempt_id = start.data['id']

    client.post(
        f'/api/v1/submissions/attempts/{attempt_id}/answer/',
        {
            'question': str(question.id),
            'code_answer': 'import sys\nprint(int(sys.stdin.read())*2)',
            'code_language': 'python',
        },
        format='json',
    )

    submit = client.post(f'/api/v1/submissions/attempts/{attempt_id}/submit/', {}, format='json')
    assert submit.status_code == 200
    assert float(submit.data['total_score']) == float(question.marks)
