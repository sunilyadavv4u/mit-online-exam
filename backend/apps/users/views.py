"""User and profile API views."""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StudentProfile, TeacherProfile, User, UserRole
from .permissions import IsSuperAdmin, IsTeacher
from .serializers import (
    ChangePasswordSerializer,
    StudentProfileSerializer,
    TeacherProfileSerializer,
    UserAdminSerializer,
    UserSerializer,
)


class UserListPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """User management. Teachers list students; super admins list all users."""

    queryset = User.objects.all().select_related('student_profile', 'teacher_profile')
    pagination_class = UserListPagination
    filterset_fields = ('role', 'is_active', 'is_email_verified')
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'phone',
        'student_profile__enrollment_id',
        'student_profile__batch',
        'student_profile__course',
    )
    ordering_fields = ('created_at', 'email', 'role')

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.is_super_admin:
            return UserAdminSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsSuperAdmin()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsSuperAdmin()]
        if self.action == 'list':
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_super_admin:
            return qs
        if user.is_teacher:
            return qs.filter(role=UserRole.STUDENT)
        return qs.filter(pk=user.pk)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """Return / update the currently authenticated user."""
        user = request.user
        if request.method == 'GET':
            return Response(UserSerializer(user).data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'detail': 'Old password is incorrect.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password updated successfully.'})


class StudentProfileViewSet(viewsets.ModelViewSet):
    """Manage student profile information."""

    queryset = StudentProfile.objects.select_related('user').all()
    serializer_class = StudentProfileSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_super_admin or user.is_teacher:
            return qs
        return qs.filter(user=user)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        profile = get_object_or_404(StudentProfile, user=request.user)
        if request.method == 'GET':
            return Response(StudentProfileSerializer(profile).data)
        serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TeacherProfileViewSet(viewsets.ModelViewSet):
    """Manage teacher profile information."""

    queryset = TeacherProfile.objects.select_related('user').all()
    serializer_class = TeacherProfileSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_super_admin:
            return qs
        return qs.filter(user=user)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        profile = get_object_or_404(TeacherProfile, user=request.user)
        if request.method == 'GET':
            return Response(TeacherProfileSerializer(profile).data)
        serializer = TeacherProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
