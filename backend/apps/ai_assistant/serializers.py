"""Serializers for AI assistant requests."""
from rest_framework import serializers

from .models import AIRequest


class AIRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRequest
        fields = ('id', 'request_type', 'prompt', 'response',
                  'is_success', 'error', 'latency_ms', 'metadata',
                  'created_at')
        read_only_fields = ('id', 'response', 'is_success', 'error',
                            'latency_ms', 'metadata', 'created_at')


class CodeConversionSerializer(serializers.Serializer):
    code = serializers.CharField()


class CodeExplainSerializer(serializers.Serializer):
    code = serializers.CharField()
    language = serializers.CharField(default='python')


class GradeDescriptiveSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()
    max_marks = serializers.DecimalField(max_digits=6, decimal_places=2)


class ChatSerializer(serializers.Serializer):
    messages = serializers.ListField(child=serializers.DictField())
