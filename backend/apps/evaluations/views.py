"""Evaluation API views (teacher manual grading + publish)."""
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.submissions.models import Answer, AttemptStatus, ExamAttempt
from apps.users.permissions import IsTeacher

from .models import Evaluation, EvaluationStatus
from .serializers import (
    EvaluateAnswerSerializer,
    EvaluationSerializer,
    PublishEvaluationSerializer,
)


class EvaluationViewSet(viewsets.ModelViewSet):
    """Teacher-side manual grading + result publication."""

    queryset = Evaluation.objects.select_related(
        'attempt', 'attempt__exam', 'attempt__student', 'evaluator',
    ).all()
    serializer_class = EvaluationSerializer
    permission_classes = (IsAuthenticated, IsTeacher)
    filterset_fields = ('status', 'attempt__exam', 'attempt__student')
    search_fields = ('attempt__student__email', 'attempt__exam__title')
    ordering_fields = ('updated_at', 'created_at', 'published_at')

    def perform_create(self, serializer):
        serializer.save(evaluator=self.request.user)

    @action(detail=False, methods=['post'], url_path='from-attempt')
    def from_attempt(self, request):
        """Create or fetch the evaluation wrapper for an attempt."""
        attempt_id = request.data.get('attempt_id')
        if not attempt_id:
            return Response({'detail': 'attempt_id is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        attempt = get_object_or_404(ExamAttempt, id=attempt_id)
        evaluation, _ = Evaluation.objects.get_or_create(
            attempt=attempt,
            defaults={'evaluator': request.user},
        )
        return Response(EvaluationSerializer(evaluation).data)

    @action(detail=True, methods=['post'], url_path='grade-answer')
    def grade_answer(self, request, pk=None):
        evaluation = self.get_object()
        serializer = EvaluateAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        answer = get_object_or_404(
            Answer, id=data['answer_id'], attempt=evaluation.attempt,
        )
        answer.manual_score = data['manual_score']
        if 'teacher_comment' in data:
            answer.teacher_comment = data.get('teacher_comment') or ''
        answer.save(update_fields=['manual_score', 'teacher_comment'])

        # Recompute total score after manual grading
        descriptive = sum(
            (Decimal(a.manual_score) if a.manual_score is not None else Decimal(a.auto_score))
            for a in evaluation.attempt.answers.all()
        )
        attempt = evaluation.attempt
        attempt.descriptive_score = descriptive - Decimal(attempt.objective_score)
        attempt.total_score = descriptive
        attempt.save(update_fields=['descriptive_score', 'total_score'])
        return Response({'status': 'ok', 'total_score': str(attempt.total_score)})

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        evaluation = self.get_object()
        serializer = PublishEvaluationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['publish']:
            evaluation.status = EvaluationStatus.PUBLISHED
            evaluation.published_at = timezone.now()
            evaluation.save(update_fields=['status', 'published_at'])

            attempt = evaluation.attempt
            attempt.status = AttemptStatus.PUBLISHED
            attempt.is_passed = (
                attempt.exam.passing_marks
                and attempt.total_score >= attempt.exam.passing_marks
            ) or False
            attempt.save(update_fields=['status', 'is_passed'])

            from apps.notifications.tasks import send_result_published_email
            try:
                send_result_published_email.delay(str(attempt.id))
            except Exception:
                send_result_published_email(str(attempt.id))
        else:
            evaluation.status = EvaluationStatus.DRAFT
            evaluation.published_at = None
            evaluation.save(update_fields=['status', 'published_at'])
        return Response({'status': evaluation.status})


class StudentEvaluationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only endpoint students use to fetch their published evaluations."""

    serializer_class = EvaluationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('attempt__exam',)
    ordering_fields = ('updated_at', 'published_at')
    queryset = Evaluation.objects.none()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Evaluation.objects.none()
        return Evaluation.objects.filter(
            attempt__student=self.request.user,
            status=EvaluationStatus.PUBLISHED,
        ).select_related('attempt', 'attempt__exam')
