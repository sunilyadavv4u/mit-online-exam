"""Signals to keep user profiles in sync with role changes."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

from .models import StudentProfile, TeacherProfile, User, UserRole


@receiver(post_save, sender=User)
def create_role_profile(sender, instance: User, created: bool, **kwargs):
    """Auto-create the appropriate profile object when a new user is created."""
    if not created:
        return

    if instance.role == UserRole.STUDENT:
        StudentProfile.objects.get_or_create(
            user=instance,
            defaults={
                'enrollment_id': f'MIT-S-{get_random_string(8).upper()}',
            },
        )
    elif instance.role == UserRole.TEACHER:
        TeacherProfile.objects.get_or_create(
            user=instance,
            defaults={
                'employee_id': f'MIT-T-{get_random_string(8).upper()}',
            },
        )
