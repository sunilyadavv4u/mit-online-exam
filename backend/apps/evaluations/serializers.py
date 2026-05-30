"""Serializers for evaluations and per-answer manual grading."""
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.submissions.serializers import AnswerReadSerializer

from .models import Evaluation, EvaluationStatus


class EvaluateAnswerSerializer(serializers.Serializer):
    """Body for grading a single answer."""

    answer_id = serializers.UUIDField()
    manual_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    teacher_comment = serializers.CharField(allow_blank=True, required=False)


class EvaluationSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    student_email = serializers.CharField(source='attempt.student.email', read_only=True)
    student_name = serializers.CharField(source='attempt.student.full_name', read_only=True)
    exam_title = serializers.CharField(source='attempt.exam.title', read_only=True)
    total_score = serializers.DecimalField(source='attempt.total_score',
                                            max_digits=8, decimal_places=2, read_only=True)
    objective_score = serializers.DecimalField(
        source='attempt.objective_score', max_digits=8, decimal_places=2, read_only=True,
    )
    descriptive_score = serializers.DecimalField(
        source='attempt.descriptive_score', max_digits=8, decimal_places=2, read_only=True,
    )

    class Meta:
        model = Evaluation
        fields = ('id', 'attempt', 'evaluator', 'status',
                  'overall_comment', 'published_at',
                  'student_email', 'student_name', 'exam_title',
                  'total_score', 'objective_score', 'descriptive_score',
                  'answers', 'created_at', 'updated_at')
        read_only_fields = ('id', 'evaluator', 'published_at',
                            'created_at', 'updated_at')

    def get_answers(self, obj):
        qs = obj.attempt.answers.select_related('question').order_by('question__order')
        return AnswerReadSerializer(qs, many=True).data
    get_answers = extend_schema_field(AnswerReadSerializer(many=True))(get_answers)


class PublishEvaluationSerializer(serializers.Serializer):
    publish = serializers.BooleanField(default=True)
