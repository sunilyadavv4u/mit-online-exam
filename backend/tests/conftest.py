"""Pytest fixtures shared across tests."""
import pytest
from rest_framework.test import APIClient

from apps.users.models import User, UserRole


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def super_admin(db):
    return User.objects.create_user(
        email='admin@test.com', password='Admin@12345',
        role=UserRole.SUPER_ADMIN, is_staff=True, is_superuser=True,
        is_active=True, is_email_verified=True,
    )


@pytest.fixture
def teacher(db):
    return User.objects.create_user(
        email='teacher@test.com', password='Teacher@12345',
        role=UserRole.TEACHER, is_active=True, is_email_verified=True,
        first_name='T', last_name='One',
    )


@pytest.fixture
def student(db):
    return User.objects.create_user(
        email='student@test.com', password='Student@12345',
        role=UserRole.STUDENT, is_active=True, is_email_verified=True,
        first_name='S', last_name='One',
    )


@pytest.fixture
def auth_client(api_client):
    def _login(user, password):
        res = api_client.post(
            '/api/v1/auth/login/',
            {'email': user.email, 'password': password},
            format='json',
        )
        token = res.data.get('access')
        if token:
            api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return api_client
    return _login
