"""Question ViewSets."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsTeacher

from .models import CodingTestCase, Question, QuestionOption
from .serializers import (
    CodingTestCaseSerializer,
    QuestionOptionSerializer,
    QuestionSerializer,
)


class QuestionViewSet(viewsets.ModelViewSet):
    """Manage exam questions and the question bank.

    Students never hit this endpoint directly when attempting; they get
    questions via the submissions/attempt API which uses the
    StudentQuestionSerializer.
    """

    queryset = Question.objects.select_related('subject', 'exam', 'created_by')\
                               .prefetch_related('options', 'test_cases').all()
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated, IsTeacher)
    filterset_fields = ('exam', 'subject', 'question_type', 'difficulty',
                        'is_in_bank', 'coding_language', 'created_by')
    search_fields = ('text', 'tags', 'subject__name')
    ordering_fields = ('created_at', 'order', 'difficulty', 'marks')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    permission_classes = (IsAuthenticated, IsTeacher)
    filterset_fields = ('question',)


class CodingTestCaseViewSet(viewsets.ModelViewSet):
    queryset = CodingTestCase.objects.all()
    serializer_class = CodingTestCaseSerializer
    permission_classes = (IsAuthenticated, IsTeacher)
    filterset_fields = ('question', 'is_hidden')
