"""AI Assistant endpoints (Databricks-backed code conversion + grading)."""
import functools
import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .databricks_client import (
    DatabricksLLMClient,
    convert_python_to_pyspark,
    convert_sql_to_pyspark,
    convert_sql_to_spark_sql,
    explain_code,
    grade_descriptive_answer,
)
from .models import AIRequest, AIRequestType
from .serializers import (
    AIRequestSerializer,
    ChatSerializer,
    CodeConversionSerializer,
    CodeExplainSerializer,
    GradeDescriptiveSerializer,
)

logger = logging.getLogger(__name__)


def _record_request(user, request_type: str, prompt: str,
                     response: str = '', success: bool = True,
                     error: str = '', latency_ms: int = 0,
                     metadata: dict | None = None):
    return AIRequest.objects.create(
        user=user,
        request_type=request_type,
        prompt=prompt,
        response=response,
        is_success=success,
        error=error,
        latency_ms=latency_ms,
        metadata=metadata or {},
    )


def _ai_action(request_type: str):
    """Combine error-handling + AIRequest persistence around an action."""

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            try:
                return view_func(self, request, *args, **kwargs)
            except RuntimeError as exc:
                logger.exception('Databricks call failed')
                _record_request(
                    request.user,
                    request_type=request_type,
                    prompt=str(request.data),
                    success=False,
                    error=str(exc),
                )
                return Response({'detail': str(exc)},
                                 status=status.HTTP_502_BAD_GATEWAY)
            except Exception as exc:
                logger.exception('Unexpected AI assistant error')
                return Response({'detail': str(exc)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return wrapper

    return decorator


class AIAssistantViewSet(viewsets.ViewSet):
    """All AI helpers in a single ViewSet under /api/v1/ai/assistant/."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(request=CodeConversionSerializer, responses=AIRequestSerializer)
    @action(detail=False, methods=['post'], url_path='convert/sql-to-spark-sql')
    @_ai_action(AIRequestType.CONVERT_SQL_TO_SPARK)
    def sql_to_spark_sql(self, request):
        serializer = CodeConversionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        result = convert_sql_to_spark_sql(code)
        ai = _record_request(request.user, AIRequestType.CONVERT_SQL_TO_SPARK,
                              prompt=code, response=result.content,
                              latency_ms=result.latency_ms)
        return Response(AIRequestSerializer(ai).data)

    @extend_schema(request=CodeConversionSerializer, responses=AIRequestSerializer)
    @action(detail=False, methods=['post'], url_path='convert/sql-to-pyspark')
    @_ai_action(AIRequestType.CONVERT_SQL_TO_PYSPARK)
    def sql_to_pyspark(self, request):
        serializer = CodeConversionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        result = convert_sql_to_pyspark(code)
        ai = _record_request(request.user, AIRequestType.CONVERT_SQL_TO_PYSPARK,
                              prompt=code, response=result.content,
                              latency_ms=result.latency_ms)
        return Response(AIRequestSerializer(ai).data)

    @extend_schema(request=CodeConversionSerializer, responses=AIRequestSerializer)
    @action(detail=False, methods=['post'], url_path='convert/python-to-pyspark')
    @_ai_action(AIRequestType.CONVERT_PYTHON_TO_PYSPARK)
    def python_to_pyspark(self, request):
        serializer = CodeConversionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        result = convert_python_to_pyspark(code)
        ai = _record_request(request.user, AIRequestType.CONVERT_PYTHON_TO_PYSPARK,
                              prompt=code, response=result.content,
                              latency_ms=result.latency_ms)
        return Response(AIRequestSerializer(ai).data)

    @extend_schema(request=CodeExplainSerializer, responses=AIRequestSerializer)
    @action(detail=False, methods=['post'], url_path='explain')
    @_ai_action(AIRequestType.EXPLAIN_CODE)
    def explain(self, request):
        serializer = CodeExplainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        language = serializer.validated_data['language']
        result = explain_code(code, language=language)
        ai = _record_request(request.user, AIRequestType.EXPLAIN_CODE,
                              prompt=code, response=result.content,
                              latency_ms=result.latency_ms,
                              metadata={'language': language})
        return Response(AIRequestSerializer(ai).data)

    @extend_schema(request=GradeDescriptiveSerializer, responses=AIRequestSerializer)
    @action(detail=False, methods=['post'], url_path='grade-descriptive')
    @_ai_action(AIRequestType.GRADE_DESCRIPTIVE)
    def grade(self, request):
        if not request.user.is_teacher and not request.user.is_super_admin:
            return Response({'detail': 'Only teachers can grade.'},
                             status=status.HTTP_403_FORBIDDEN)
        serializer = GradeDescriptiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = grade_descriptive_answer(
            question=serializer.validated_data['question'],
            answer=serializer.validated_data['answer'],
            max_marks=float(serializer.validated_data['max_marks']),
        )
        ai = _record_request(request.user, AIRequestType.GRADE_DESCRIPTIVE,
                              prompt=str(serializer.validated_data),
                              response=result.content,
                              latency_ms=result.latency_ms)
        return Response(AIRequestSerializer(ai).data)

    @extend_schema(request=ChatSerializer, responses=AIRequestSerializer)
    @action(detail=False, methods=['post'], url_path='chat')
    @_ai_action(AIRequestType.CHAT)
    def chat(self, request):
        serializer = ChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = DatabricksLLMClient()
        result = client.chat(serializer.validated_data['messages'])
        ai = _record_request(request.user, AIRequestType.CHAT,
                              prompt=str(serializer.validated_data['messages']),
                              response=result.content,
                              latency_ms=result.latency_ms)
        return Response(AIRequestSerializer(ai).data)


@extend_schema(responses=AIRequestSerializer(many=True))
class AIRequestHistoryView(APIView):
    """List the current user's AI request history."""

    permission_classes = (IsAuthenticated,)
    serializer_class = AIRequestSerializer

    def get(self, request):
        qs = AIRequest.objects.filter(user=request.user)[:200]
        return Response(AIRequestSerializer(qs, many=True).data)
