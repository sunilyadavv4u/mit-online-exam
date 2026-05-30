"""Auth helper utilities (email senders)."""
from django.conf import settings
from django.core.mail import send_mail


def send_verification_email(user) -> None:
    verify_url = f'{settings.FRONTEND_URL}/verify-email/{user.email_verification_token}'
    subject = 'Verify your Mewati Institute of Technology account'
    message = (
        f'Hello {user.full_name},\n\n'
        f'Please verify your email address by clicking the link below:\n{verify_url}\n\n'
        'If you did not create an account, please ignore this email.\n\n'
        'Mewati Institute of Technology'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)


def send_password_reset_email(user, token: str) -> None:
    reset_url = f'{settings.FRONTEND_URL}/reset-password?token={token}'
    subject = 'Mewati Institute of Technology - Password Reset'
    message = (
        f'Hello {user.full_name},\n\n'
        f'You requested a password reset. Click the link below within 1 hour:\n{reset_url}\n\n'
        'If this was not you, please ignore this email.\n\n'
        'Mewati Institute of Technology'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
