"""Custom DRF permissions for role based access control."""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import UserRole


class IsSuperAdmin(BasePermission):
    """Allow access only to super admin users."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == UserRole.SUPER_ADMIN)


class IsTeacher(BasePermission):
    """Allow access only to teacher users (or super admins)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role in {UserRole.TEACHER, UserRole.SUPER_ADMIN}
        )


class IsStudent(BasePermission):
    """Allow access only to student users."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == UserRole.STUDENT)


class IsTeacherOrReadOnly(BasePermission):
    """Read for everyone authenticated, write only for teachers/admins."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.role in {UserRole.TEACHER, UserRole.SUPER_ADMIN}


class IsOwnerOrTeacher(BasePermission):
    """Object-level permission for student-owned objects, with teacher fallback."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role in {UserRole.TEACHER, UserRole.SUPER_ADMIN}:
            return True
        owner = getattr(obj, 'student', None) or getattr(obj, 'user', None)
        return owner == user
