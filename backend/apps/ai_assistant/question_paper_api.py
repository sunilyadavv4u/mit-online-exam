"""Teacher-only API: AI question paper generator (isolated from AIAssistantViewSet)."""
import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsTeacher

from .models import AIRequest, AIRequestType
from apps.exams.models import Exam

from .question_paper_file_extract import extract_notes_from_upload
from .question_paper_import import import_question_paper_to_exam
from .question_paper_service import generate_question_paper, parse_question_paper_json
from .serializers import AIRequestSerializer

logger = logging.getLogger(__name__)


class QuestionPaperGenerateSerializer(serializers.Serializer):
    prompt = serializers.CharField(
        help_text='What you want in the paper (topics, mix of types, difficulty, etc.).',
    )
    teaching_notes = serializers.CharField(
        help_text='Your class notes / slides text the questions should be based on.',
    )
    subject = serializers.CharField(required=False, allow_blank=True, default='')
    total_marks = serializers.IntegerField(required=False, default=100, min_value=1, max_value=500)
    duration_minutes = serializers.IntegerField(required=False, default=60, min_value=5, max_value=300)
    num_questions = serializers.IntegerField(required=False, default=10, min_value=1, max_value=50)
    difficulty = serializers.ChoiceField(
        required=False,
        default='medium',
        choices=['easy', 'medium', 'hard'],
    )
    question_types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )


class QuestionPaperGenerateView(APIView):
    """POST /api/v1/ai/question-paper/generate/ — teachers and super admins only."""

    permission_classes = (IsAuthenticated, IsTeacher)

    @extend_schema(request=QuestionPaperGenerateSerializer, responses=AIRequestSerializer)
    def post(self, request):
        serializer = QuestionPaperGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        prompt_summary = (
            f'prompt={data["prompt"][:500]}; notes_len={len(data["teaching_notes"])}'
        )

        try:
            result = generate_question_paper(
                prompt=data['prompt'],
                teaching_notes=data['teaching_notes'],
                subject=data.get('subject', ''),
                total_marks=data.get('total_marks', 100),
                duration_minutes=data.get('duration_minutes', 60),
                num_questions=data.get('num_questions', 10),
                difficulty=data.get('difficulty', 'medium'),
                question_types=data.get('question_types') or None,
            )
            paper = parse_question_paper_json(result.content)
            ai = AIRequest.objects.create(
                user=request.user,
                request_type=AIRequestType.GENERATE_QUESTION,
                prompt=prompt_summary,
                response=result.content,
                is_success=True,
                latency_ms=result.latency_ms,
                metadata={
                    'feature': 'question_paper',
                    'subject': data.get('subject', ''),
                    'total_marks': data.get('total_marks'),
                },
            )
            return Response({
                'id': str(ai.id),
                'request_type': ai.request_type,
                'question_paper': paper,
                'raw_response': result.content,
                'latency_ms': result.latency_ms,
                'created_at': ai.created_at,
            })
        except RuntimeError as exc:
            logger.exception('Question paper generation failed (Databricks)')
            AIRequest.objects.create(
                user=request.user,
                request_type=AIRequestType.GENERATE_QUESTION,
                prompt=prompt_summary,
                is_success=False,
                error=str(exc),
                metadata={'feature': 'question_paper'},
            )
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as exc:
            logger.exception('Question paper generation failed')
            return Response({'detail': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotesFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        help_text='Teaching notes file: .pdf, .txt, .py, .md, .sql (max 100 MB).',
    )


class QuestionPaperExtractNotesView(APIView):
    """POST /api/v1/ai/question-paper/extract-notes/ — upload file, get text for notes field."""

    permission_classes = (IsAuthenticated, IsTeacher)
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(request=NotesFileUploadSerializer)
    def post(self, request):
        serializer = NotesFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded = serializer.validated_data['file']
        try:
            text, meta = extract_notes_from_upload(uploaded)
            return Response({
                'text': text,
                'filename': meta['filename'],
                'char_count': meta['char_count'],
            })
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0] if exc.messages else str(exc)},
                            status=status.HTTP_400_BAD_REQUEST)


class ImportToExamSerializer(serializers.Serializer):
    exam_id = serializers.UUIDField(help_text='Target exam UUID.')
    question_paper = serializers.DictField(help_text='Structured question_paper from AI generate.')
    set_live = serializers.BooleanField(
        required=False,
        default=False,
        help_text='Set exam status to live after import.',
    )
    update_exam_metadata = serializers.BooleanField(
        required=False,
        default=True,
        help_text='Apply instructions, duration, total marks from the paper to the exam.',
    )


class QuestionPaperImportToExamView(APIView):
    """POST /api/v1/ai/question-paper/import-to-exam/ — add AI questions to an exam."""

    permission_classes = (IsAuthenticated, IsTeacher)

    @extend_schema(request=ImportToExamSerializer)
    def post(self, request):
        serializer = ImportToExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        exam = get_object_or_404(Exam, pk=data['exam_id'])

        try:
            result = import_question_paper_to_exam(
                exam=exam,
                paper=data['question_paper'],
                user=request.user,
                set_live=data.get('set_live', False),
                update_exam_metadata=data.get('update_exam_metadata', True),
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except PermissionDenied as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except DjangoValidationError as exc:
            return Response({'detail': exc.messages[0] if exc.messages else str(exc)},
                            status=status.HTTP_400_BAD_REQUEST)
