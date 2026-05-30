"""Custom user model and supporting profile models."""
import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', _('Super Admin')
    TEACHER = 'teacher', _('Teacher / Admin')
    STUDENT = 'student', _('Student')


class UserManager(BaseUserManager):
    """Manager that uses email as the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', UserRole.STUDENT)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        extra_fields.setdefault('is_email_verified', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User authenticated by email and segmented by role."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        db_index=True,
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)

    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=128, blank=True)

    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active', 'role']),
        ]

    def __str__(self) -> str:
        return f'{self.full_name} <{self.email}>'

    @property
    def full_name(self) -> str:
        name = f'{self.first_name} {self.last_name}'.strip()
        return name or self.email

    @property
    def is_super_admin(self) -> bool:
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_teacher(self) -> bool:
        return self.role == UserRole.TEACHER

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT


class StudentProfile(models.Model):
    """Additional fields specific to students."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        primary_key=True,
    )
    enrollment_id = models.CharField(max_length=40, unique=True, db_index=True)
    course = models.CharField(max_length=120, blank=True)
    batch = models.CharField(max_length=40, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=120, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    def __str__(self) -> str:
        return f'Student: {self.user.full_name}'


class TeacherProfile(models.Model):
    """Additional fields specific to teachers."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        primary_key=True,
    )
    employee_id = models.CharField(max_length=40, unique=True, db_index=True)
    designation = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=120, blank=True)
    expertise = models.TextField(
        blank=True,
        help_text='Comma separated list of subjects/technologies',
    )
    years_of_experience = models.PositiveIntegerField(default=0)
    linkedin = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'

    def __str__(self) -> str:
        return f'Teacher: {self.user.full_name}'
