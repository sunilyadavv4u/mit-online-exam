"""Tests for the AI assistant Databricks integration (mocked)."""
import json
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.exams.models import Exam, ExamStatus, Subject
from apps.questions.models import Question


@pytest.mark.django_db
def test_databricks_not_configured_returns_502(auth_client, teacher, settings):
    settings.DATABRICKS_URL = ''
    settings.DATABRICKS_TOKEN = ''
    client = auth_client(teacher, 'Teacher@12345')
    res = client.post(
        '/api/v1/ai/assistant/convert/sql-to-spark-sql/',
        {'code': 'SELECT 1'}, format='json',
    )
    assert res.status_code == 502
    assert 'Databricks' in res.data['detail']


@pytest.mark.django_db
def test_databricks_chat_uses_client(auth_client, teacher, settings):
    settings.DATABRICKS_URL = 'https://example.com'
    settings.DATABRICKS_TOKEN = 'token'
    settings.DATABRICKS_ENDPOINT = 'fake'

    fake_response = {
        'choices': [{'message': {'content': "spark.sql('SELECT * FROM employee LIMIT 100')"}}],
    }

    with patch('apps.ai_assistant.databricks_client.requests.post') as mock_post:
        mock_post.return_value.json.return_value = fake_response
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.status_code = 200

        client = auth_client(teacher, 'Teacher@12345')
        res = client.post(
            '/api/v1/ai/assistant/convert/sql-to-spark-sql/',
            {'code': 'SELECT TOP 100 * FROM employee'}, format='json',
        )

    assert res.status_code == 200, res.data
    assert "spark.sql" in res.data['response']


@pytest.mark.django_db
def test_student_cannot_generate_question_paper(auth_client, student, settings):
    settings.DATABRICKS_URL = 'https://example.com'
    settings.DATABRICKS_TOKEN = 'token'
    settings.DATABRICKS_ENDPOINT = 'fake'
    client = auth_client(student, 'Student@12345')
    res = client.post(
        '/api/v1/ai/question-paper/generate/',
        {'prompt': 'MCQ paper', 'teaching_notes': 'Notes here'},
        format='json',
    )
    assert res.status_code == 403


@pytest.mark.django_db
def test_teacher_question_paper_generate(auth_client, teacher, settings):
    settings.DATABRICKS_URL = 'https://example.com'
    settings.DATABRICKS_TOKEN = 'token'
    settings.DATABRICKS_ENDPOINT = 'fake'

    paper_json = {
        'title': 'Python Quiz',
        'instructions': 'Answer all.',
        'total_marks': 50,
        'duration_minutes': 45,
        'sections': [{'name': 'A', 'questions': [{'number': 1, 'type': 'single_choice', 'text': 'What is list?', 'marks': 5}]}],
    }

    fake_response = {
        'choices': [{'message': {'content': json.dumps(paper_json)}}],
    }

    with patch('apps.ai_assistant.databricks_client.requests.post') as mock_post:
        mock_post.return_value.json.return_value = fake_response
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.status_code = 200

        client = auth_client(teacher, 'Teacher@12345')
        res = client.post(
            '/api/v1/ai/question-paper/generate/',
            {
                'prompt': '5 MCQ from notes',
                'teaching_notes': 'Lists and tuples in Python.',
                'subject': 'Python',
                'total_marks': 50,
            },
            format='json',
        )

    assert res.status_code == 200, res.data
    assert res.data['question_paper']['title'] == 'Python Quiz'
    assert len(res.data['question_paper']['sections'][0]['questions']) == 1


@pytest.mark.django_db
def test_extract_notes_from_py_file(auth_client, teacher):
    client = auth_client(teacher, 'Teacher@12345')
    content = b'def square(n):\n    return n * n\n'
    upload = SimpleUploadedFile('lesson.py', content, content_type='text/x-python')
    res = client.post('/api/v1/ai/question-paper/extract-notes/', {'file': upload}, format='multipart')
    assert res.status_code == 200, res.data
    assert 'def square' in res.data['text']
    assert res.data['filename'] == 'lesson.py'


@pytest.mark.django_db
def test_extract_notes_rejects_unsupported_type(auth_client, teacher):
    client = auth_client(teacher, 'Teacher@12345')
    upload = SimpleUploadedFile('notes.docx', b'fake', content_type='application/octet-stream')
    res = client.post('/api/v1/ai/question-paper/extract-notes/', {'file': upload}, format='multipart')
    assert res.status_code == 400


@pytest.mark.django_db
def test_import_question_paper_to_exam(auth_client, teacher):
    subject = Subject.objects.create(name='AI Import', code='AIIMP', created_by=teacher)
    now = timezone.now()
    exam = Exam.objects.create(
        title='Target Exam',
        slug='target-exam-import',
        subject=subject,
        status=ExamStatus.DRAFT,
        duration_minutes=30,
        total_marks=Decimal('10'),
        passing_marks=Decimal('5'),
        start_time=now,
        end_time=now + timedelta(hours=2),
        created_by=teacher,
    )
    paper = {
        'title': 'Quiz',
        'instructions': 'Answer all.',
        'total_marks': 20,
        'duration_minutes': 45,
        'sections': [{
            'name': 'A',
            'questions': [
                {
                    'number': 1,
                    'type': 'single_choice',
                    'text': 'Capital of France?',
                    'marks': 5,
                    'options': ['London', 'Paris', 'Berlin'],
                    'correct_answer': 'Paris',
                },
                {
                    'number': 2,
                    'type': 'fill_blank',
                    'text': '2+2=___',
                    'marks': 5,
                    'correct_answer': '4',
                },
            ],
        }],
    }
    client = auth_client(teacher, 'Teacher@12345')
    res = client.post(
        '/api/v1/ai/question-paper/import-to-exam/',
        {'exam_id': str(exam.id), 'question_paper': paper, 'set_live': True},
        format='json',
    )
    assert res.status_code == 201, res.data
    assert res.data['created_count'] == 2
    exam.refresh_from_db()
    assert exam.status == ExamStatus.LIVE
    assert exam.instructions == 'Answer all.'
    assert Question.objects.filter(exam=exam).count() == 2


@pytest.mark.django_db
def test_mit_chat_send(auth_client, student, settings):
    settings.DATABRICKS_URL = 'https://example.com'
    settings.DATABRICKS_TOKEN = 'token'
    settings.DATABRICKS_ENDPOINT = 'fake'

    fake_response = {
        'choices': [{'message': {'content': 'Hello! How can I help you study today?'}}],
    }

    with patch('apps.ai_assistant.databricks_client.requests.post') as mock_post:
        mock_post.return_value.json.return_value = fake_response
        mock_post.return_value.raise_for_status.return_value = None

        client = auth_client(student, 'Student@12345')
        res = client.post(
            '/api/v1/ai/mit-chat/send/',
            {'messages': [{'role': 'user', 'content': 'What is a list in Python?'}]},
            format='json',
        )

    assert res.status_code == 200, res.data
    assert res.data['message']['role'] == 'assistant'
    assert 'help' in res.data['message']['content'].lower()
