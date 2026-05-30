"""Code Studio playground API — run/edit code without an exam attempt."""
import logging

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .code_runner import run_python_against_tests
from .code_studio_runner import (
    run_java_freeform,
    run_pyspark_freeform,
    run_python_freeform,
    run_sql_freeform,
)

logger = logging.getLogger(__name__)


class CodeStudioRunSerializer(serializers.Serializer):
    code = serializers.CharField()
    language = serializers.ChoiceField(
        choices=['python', 'sql', 'sqlserver', 'pyspark', 'java'],
    )
    stdin = serializers.CharField(required=False, allow_blank=True, default='')
    expected_output = serializers.CharField(required=False, allow_blank=True, default='')


class CodeStudioRunView(APIView):
    """POST /api/v1/submissions/code-studio/run/ — run Python, Java, SQL, PySpark."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(request=CodeStudioRunSerializer)
    def post(self, request):
        serializer = CodeStudioRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        language = serializer.validated_data['language'].lower()
        if language == 'sqlserver':
            language = 'sql'
        stdin = serializer.validated_data.get('stdin') or ''
        expected = (serializer.validated_data.get('expected_output') or '').strip()

        if language == 'python':
            if expected:
                result = run_python_against_tests(
                    code,
                    [{'input_data': stdin, 'expected_output': expected}],
                    timeout_seconds=15,
                )
                return Response({
                    'language': 'python',
                    'mode': 'test',
                    'passed': result.passed,
                    'total': result.total,
                    'details': result.details,
                })
            free = run_python_freeform(code, stdin=stdin)
            return Response({'language': 'python', 'mode': 'freeform', **free})

        if language == 'java':
            free = run_java_freeform(code, stdin=stdin)
            return Response({'language': 'java', 'mode': 'freeform', **free})

        if language == 'sql':
            free = run_sql_freeform(code)
            return Response({'language': 'sql', 'mode': 'freeform', **free})

        if language == 'pyspark':
            free = run_pyspark_freeform(code)
            return Response({'language': 'pyspark', 'mode': 'freeform', **free})

        return Response({'detail': f'Unsupported language: {language}'}, status=400)
