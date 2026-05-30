"""Subject and exam ViewSets."""
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.models import User, UserRole
from apps.users.permissions import IsTeacher, IsTeacherOrReadOnly

from .models import Exam, ExamEnrollment, ExamStatus, Subject
from .serializers import (
    ExamEnrollmentSerializer,
    ExamListSerializer,
    ExamPublishSerializer,
    ExamSerializer,
    SubjectSerializer,
)


class SubjectViewSet(viewsets.ModelViewSet):
    """Manage subjects. Teachers/admins can create/edit, students read-only."""

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = (IsAuthenticated, IsTeacherOrReadOnly)
    filterset_fields = ('is_active',)
    search_fields = ('name', 'code', 'description')
    ordering_fields = ('name', 'created_at')

    def get_queryset(self):
        return super().get_queryset().annotate(exam_count=Count('exams'))

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExamViewSet(viewsets.ModelViewSet):
    """Exams CRUD + lifecycle actions."""

    queryset = Exam.objects.select_related('subject', 'created_by').all()
    permission_classes = (IsAuthenticated, IsTeacherOrReadOnly)
    filterset_fields = ('status', 'subject', 'exam_type', 'created_by')
    search_fields = ('title', 'slug', 'description', 'subject__name')
    ordering_fields = ('start_time', 'created_at', 'title')
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ExamListSerializer
        return ExamSerializer

    def get_queryset(self):
        qs = super().get_queryset().annotate(
            enrolled_count=Count('enrollments', distinct=True),
            question_count=Count('questions', distinct=True),
        )
        user = self.request.user
        if user.is_super_admin or user.is_teacher:
            return qs
        return qs.filter(
            enrollments__student=user,
            status__in=[ExamStatus.SCHEDULED, ExamStatus.LIVE,
                        ExamStatus.COMPLETED],
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, slug=None):
        """Move exam between lifecycle stages."""
        exam = self.get_object()
        serializer = ExamPublishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        exam.status = new_status
        exam.save(update_fields=['status'])
        return Response({'status': exam.status})

    @action(detail=True, methods=['post'], url_path='enroll',
            permission_classes=[IsAuthenticated, IsTeacher])
    def enroll(self, request, slug=None):
        """Enroll one or many students. Body: {"student_ids": [...]}"""
        exam = self.get_object()
        student_ids = request.data.get('student_ids') or []
        if not student_ids:
            return Response({'detail': 'student_ids is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        students = User.objects.filter(id__in=student_ids, role=UserRole.STUDENT)
        enrollments = [
            ExamEnrollment(exam=exam, student=s, enrolled_by=request.user)
            for s in students
        ]
        ExamEnrollment.objects.bulk_create(enrollments, ignore_conflicts=True)
        return Response({'enrolled': students.count()})

    @action(detail=True, methods=['post'], url_path='enroll-all',
            permission_classes=[IsAuthenticated, IsTeacher])
    def enroll_all(self, request, slug=None):
        """Enroll every active student in the system."""
        exam = self.get_object()
        students = User.objects.filter(role=UserRole.STUDENT, is_active=True)
        enrollments = [
            ExamEnrollment(exam=exam, student=s, enrolled_by=request.user)
            for s in students
        ]
        ExamEnrollment.objects.bulk_create(enrollments, ignore_conflicts=True)
        return Response({'enrolled': students.count()})

    @action(detail=True, methods=['get'], url_path='enrollments')
    def enrollments(self, request, slug=None):
        exam = self.get_object()
        qs = exam.enrollments.select_related('student').all()
        return Response(ExamEnrollmentSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='my-upcoming',
            permission_classes=[IsAuthenticated])
    def my_upcoming(self, request):
        """Upcoming/live exams for the requesting student."""
        from django.utils import timezone
        now = timezone.now()
        qs = (Exam.objects
              .filter(enrollments__student=request.user, end_time__gte=now,
                      status__in=[ExamStatus.SCHEDULED, ExamStatus.LIVE])
              .annotate(
                  enrolled_count=Count('enrollments', distinct=True),
                  question_count=Count('questions', distinct=True),
              )
              .order_by('start_time')
              .distinct())
        return Response(ExamListSerializer(qs, many=True).data)
