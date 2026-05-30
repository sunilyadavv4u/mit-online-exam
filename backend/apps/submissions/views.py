"""Submissions / exam attempt API views."""
import random
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.exams.models import Exam, ExamEnrollment, ExamStatus
from apps.questions.models import QuestionType
from apps.users.models import UserRole
from apps.users.permissions import IsTeacher

from .coding_grading import grade_coding_answer
from .evaluation import evaluate_answer
from .models import Answer, AttemptStatus, ExamAttempt, ProctorEvent
from .serializers import (
    AnswerReadSerializer,
    AnswerWriteSerializer,
    AttemptDetailSerializer,
    ExamAttemptSerializer,
    ProctorEventSerializer,
)


def _client_ip(request) -> str | None:
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class ExamAttemptViewSet(viewsets.ModelViewSet):
    """The primary student exam-taking endpoint + teacher inspection."""

    queryset = ExamAttempt.objects.select_related('exam', 'student').all()
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('exam', 'student', 'status')
    search_fields = ('exam__title', 'student__email')
    ordering_fields = ('started_at', 'submitted_at', 'total_score')

    def get_serializer_class(self):
        if self.action in {'retrieve', 'detail'}:
            return AttemptDetailSerializer
        return ExamAttemptSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_super_admin or user.is_teacher:
            return qs
        return qs.filter(student=user)

    def perform_destroy(self, instance):
        # Students can't delete attempts.
        if not self.request.user.is_super_admin:
            raise PermissionError('Only super-admins can delete attempts.')
        super().perform_destroy(instance)

    # -------------------- Student lifecycle actions --------------------
    @action(detail=False, methods=['post'], url_path='start')
    def start(self, request):
        """Start a new attempt for the given exam.

        Body: {"exam_id": "..."}
        Returns the attempt + the questions in the order to be shown.
        """
        exam_id = request.data.get('exam_id')
        if not exam_id:
            return Response({'detail': 'exam_id is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        exam = get_object_or_404(Exam, id=exam_id)

        if not exam.is_open_for_attempt:
            return Response({'detail': 'Exam is not open for attempts.'},
                            status=status.HTTP_400_BAD_REQUEST)

        is_enrolled = ExamEnrollment.objects.filter(
            exam=exam, student=request.user,
        ).exists()
        if not is_enrolled and request.user.role == UserRole.STUDENT:
            return Response({'detail': 'You are not enrolled in this exam.'},
                            status=status.HTTP_403_FORBIDDEN)

        existing = ExamAttempt.objects.filter(
            exam=exam, student=request.user,
            status=AttemptStatus.IN_PROGRESS,
        ).first()
        if existing:
            attempt = existing
        else:
            if not exam.allow_retake and ExamAttempt.objects.filter(
                exam=exam, student=request.user,
            ).exclude(status=AttemptStatus.IN_PROGRESS).exists():
                return Response({'detail': 'Retakes are not allowed.'},
                                status=status.HTTP_400_BAD_REQUEST)

            question_ids = list(
                exam.questions.order_by('order', 'created_at')
                              .values_list('id', flat=True)
            )
            if exam.randomize_questions:
                random.shuffle(question_ids)

            attempt = ExamAttempt.objects.create(
                exam=exam,
                student=request.user,
                ip_address=_client_ip(request),
                user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:255],
                question_order=[str(qid) for qid in question_ids],
            )

        return Response(AttemptDetailSerializer(attempt).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='answer')
    def answer(self, request, pk=None):
        """Save / update the student's answer to a single question."""
        attempt = self.get_object()
        if attempt.student != request.user:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if attempt.is_terminal:
            return Response({'detail': 'Attempt already submitted.'},
                            status=status.HTTP_400_BAD_REQUEST)

        question_id = request.data.get('question')
        if not question_id:
            return Response({'detail': 'question is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        answer = Answer.objects.filter(attempt=attempt, question_id=question_id).first()
        serializer = AnswerWriteSerializer(answer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        answer = serializer.save(attempt=attempt)
        return Response(AnswerReadSerializer(answer).data)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """Final submit. Triggers auto-evaluation of objective answers."""
        attempt = self.get_object()
        if attempt.student != request.user and not request.user.is_teacher:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if attempt.is_terminal:
            return Response({'detail': 'Already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        attempt.submitted_at = timezone.now()
        attempt.time_spent_seconds = int(
            (attempt.submitted_at - attempt.started_at).total_seconds()
        )
        attempt.status = AttemptStatus.AUTO_SUBMITTED if request.data.get('auto') \
            else AttemptStatus.SUBMITTED

        objective_total = Decimal('0')
        descriptive_total = Decimal('0')

        for answer in attempt.answers.select_related('question'):
            if answer.question.question_type == QuestionType.CODING and answer.code_answer:
                grade_coding_answer(answer)
            score = evaluate_answer(answer)
            if answer.question.question_type in {
                QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE,
                QuestionType.TRUE_FALSE, QuestionType.FILL_BLANK,
                QuestionType.CODING,
            }:
                objective_total += score
            else:
                descriptive_total += score

        attempt.objective_score = objective_total
        attempt.descriptive_score = descriptive_total
        attempt.total_score = objective_total + descriptive_total
        attempt.is_passed = (attempt.exam.passing_marks
                             and attempt.total_score >= attempt.exam.passing_marks) or False
        attempt.save()

        # Trigger async background evaluation/result emails (when celery is wired)
        from apps.evaluations.tasks import process_attempt_post_submit
        try:
            process_attempt_post_submit.delay(str(attempt.id))
        except Exception:
            process_attempt_post_submit(str(attempt.id))

        return Response(AttemptDetailSerializer(attempt).data)

    # -------------------- Anti-cheating events --------------------
    @action(detail=True, methods=['post'], url_path='proctor-event')
    def proctor_event(self, request, pk=None):
        attempt = self.get_object()
        if attempt.student != request.user:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProctorEventSerializer(data={
            'attempt': str(attempt.id),
            'event_type': request.data.get('event_type'),
            'metadata': request.data.get('metadata') or {},
        })
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        if event.event_type == ProctorEvent.EventType.TAB_SWITCH:
            attempt.tab_switch_count += 1
        elif event.event_type == ProctorEvent.EventType.FULLSCREEN_EXIT:
            attempt.fullscreen_exit_count += 1

        attempt.proctor_flags = (attempt.proctor_flags or [])[-49:] + [
            {'type': event.event_type, 'at': event.created_at.isoformat()}
        ]
        attempt.save(update_fields=['tab_switch_count', 'fullscreen_exit_count',
                                     'proctor_flags'])
        return Response(ProctorEventSerializer(event).data, status=status.HTTP_201_CREATED)

    # -------------------- Convenience actions --------------------
    @action(detail=False, methods=['get'], url_path='my-attempts')
    def my_attempts(self, request):
        qs = ExamAttempt.objects.filter(student=request.user)\
                                 .select_related('exam')\
                                 .order_by('-started_at')
        page = self.paginate_queryset(qs)
        ser = ExamAttemptSerializer(page or qs, many=True)
        return self.get_paginated_response(ser.data) if page else Response(ser.data)

    @action(detail=False, methods=['get'], url_path='pending-evaluation',
            permission_classes=[IsAuthenticated, IsTeacher])
    def pending_evaluation(self, request):
        """Attempts that have descriptive answers awaiting manual evaluation."""
        qs = ExamAttempt.objects.filter(
            status__in=[AttemptStatus.SUBMITTED, AttemptStatus.AUTO_SUBMITTED],
        ).select_related('exam', 'student').order_by('-submitted_at')
        page = self.paginate_queryset(qs)
        ser = ExamAttemptSerializer(page or qs, many=True)
        return self.get_paginated_response(ser.data) if page else Response(ser.data)

    @action(detail=True, methods=['post'], url_path='run-code')
    def run_code(self, request, pk=None):
        """Execute student code for a coding question against visible test cases."""
        attempt = self.get_object()
        if attempt.student != request.user:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        question_id = request.data.get('question_id')
        code = request.data.get('code', '')
        language = (request.data.get('language') or '').lower()
        if not question_id or not code:
            return Response({'detail': 'question_id and code are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        from apps.questions.models import Question

        question = Question.objects.filter(id=question_id).prefetch_related('test_cases').first()
        if not question:
            return Response({'detail': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Visible (sample) test cases only when running interactively
        cases = [
            {'input_data': tc.input_data, 'expected_output': tc.expected_output}
            for tc in question.test_cases.filter(is_hidden=False).order_by('order')
        ]
        if language == 'python':
            from .code_runner import run_python_against_tests
            result = run_python_against_tests(code, cases)
            data = {'passed': result.passed, 'total': result.total,
                    'details': result.details}
        else:
            data = {
                'passed': 0,
                'total': len(cases),
                'details': [],
                'message': (
                    f'Interactive run for {language} is not available in the '
                    'sandbox. Your final answer will be evaluated by the teacher.'
                ),
            }

        # Persist code in the answer (auto-save)
        answer, _ = Answer.objects.get_or_create(
            attempt=attempt, question=question,
            defaults={'code_answer': code, 'code_language': language},
        )
        answer.code_answer = code
        answer.code_language = language
        answer.code_run_results = data
        answer.save(update_fields=['code_answer', 'code_language', 'code_run_results'])
        return Response(data)
