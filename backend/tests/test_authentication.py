"""Authentication tests: register, login, token refresh, role separation."""
import pytest

from apps.users.models import User, UserRole


@pytest.mark.django_db
def test_register_creates_student(api_client):
    res = api_client.post(
        '/api/v1/auth/register/',
        {
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'Student',
            'password': 'Strong@12345',
            'password_confirm': 'Strong@12345',
            'role': 'student',
        },
        format='json',
    )
    assert res.status_code == 201, res.data
    assert 'access' in res.data
    user = User.objects.get(email='new@test.com')
    assert user.role == UserRole.STUDENT
    assert hasattr(user, 'student_profile')


@pytest.mark.django_db
def test_login_returns_user_payload(api_client, student):
    res = api_client.post(
        '/api/v1/auth/login/',
        {'email': student.email, 'password': 'Student@12345'},
        format='json',
    )
    assert res.status_code == 200, res.data
    assert res.data['user']['role'] == 'student'
    assert 'access' in res.data and 'refresh' in res.data


@pytest.mark.django_db
def test_me_endpoint_returns_current_user(auth_client, student):
    client = auth_client(student, 'Student@12345')
    res = client.get('/api/v1/users/users/me/')
    assert res.status_code == 200, res.data
    assert res.data['email'] == student.email


@pytest.mark.django_db
def test_student_cannot_list_users(auth_client, student):
    client = auth_client(student, 'Student@12345')
    res = client.get('/api/v1/users/users/')
    assert res.status_code in {403, 401}


@pytest.mark.django_db
def test_super_admin_can_list_users(auth_client, super_admin, student, teacher):
    client = auth_client(super_admin, 'Admin@12345')
    res = client.get('/api/v1/users/users/')
    assert res.status_code == 200
    emails = {u['email'] for u in res.data['results']}
    assert {super_admin.email, student.email, teacher.email}.issubset(emails)


@pytest.mark.django_db
def test_teacher_can_list_students_only(auth_client, teacher, student, super_admin):
    client = auth_client(teacher, 'Teacher@12345')
    res = client.get('/api/v1/users/users/')
    assert res.status_code == 200, res.data
    emails = {u['email'] for u in res.data['results']}
    assert student.email in emails
    assert super_admin.email not in emails
    assert teacher.email not in emails


@pytest.mark.django_db
def test_teacher_can_search_students_by_enrollment(auth_client, teacher, student):
    client = auth_client(teacher, 'Teacher@12345')
    enrollment = student.student_profile.enrollment_id
    res = client.get('/api/v1/users/users/', {'search': enrollment})
    assert res.status_code == 200, res.data
    emails = {u['email'] for u in res.data['results']}
    assert student.email in emails
