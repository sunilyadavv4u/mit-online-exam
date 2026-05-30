"""Serializers for questions, options and test cases."""
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import CodingTestCase, Question, QuestionOption, QuestionType


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('id', 'text', 'is_correct', 'order')


class StudentOptionSerializer(serializers.ModelSerializer):
    """Serializer used while a student is attempting the exam (no is_correct)."""

    class Meta:
        model = QuestionOption
        fields = ('id', 'text', 'order')


class CodingTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingTestCase
        fields = ('id', 'input_data', 'expected_output', 'is_hidden', 'weight', 'order')


class StudentTestCaseSerializer(serializers.ModelSerializer):
    """Visible test cases only - hidden ones are filtered out at the view layer."""

    class Meta:
        model = CodingTestCase
        fields = ('id', 'input_data', 'expected_output', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    """Full serializer for teachers (includes correct answers)."""

    options = QuestionOptionSerializer(many=True, required=False)
    test_cases = CodingTestCaseSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'exam', 'subject', 'question_type', 'text', 'image',
                  'difficulty', 'marks', 'negative_marks', 'order',
                  'correct_answer_text', 'coding_language', 'starter_code',
                  'expected_output', 'is_in_bank', 'tags',
                  'options', 'test_cases',
                  'created_by', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        test_cases_data = validated_data.pop('test_cases', [])
        question = Question.objects.create(**validated_data)
        for opt in options_data:
            QuestionOption.objects.create(question=question, **opt)
        for tc in test_cases_data:
            CodingTestCase.objects.create(question=question, **tc)
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        test_cases_data = validated_data.pop('test_cases', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if options_data is not None:
            instance.options.all().delete()
            for opt in options_data:
                QuestionOption.objects.create(question=instance, **opt)
        if test_cases_data is not None:
            instance.test_cases.all().delete()
            for tc in test_cases_data:
                CodingTestCase.objects.create(question=instance, **tc)
        return instance


class StudentQuestionSerializer(serializers.ModelSerializer):
    """Serializer used while a student is attempting an exam.

    Hides correct answers, hidden test cases and grading-only fields.
    """

    options = serializers.SerializerMethodField()
    test_cases = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'exam', 'subject', 'question_type', 'text', 'image',
                  'difficulty', 'marks', 'negative_marks', 'order',
                  'coding_language', 'starter_code', 'options', 'test_cases')

    def get_options(self, obj):
        if obj.question_type in {QuestionType.SINGLE_CHOICE,
                                  QuestionType.MULTIPLE_CHOICE,
                                  QuestionType.TRUE_FALSE}:
            return StudentOptionSerializer(obj.options.all(), many=True).data
        return []
    get_options = extend_schema_field(StudentOptionSerializer(many=True))(get_options)

    def get_test_cases(self, obj):
        if obj.question_type == QuestionType.CODING:
            return StudentTestCaseSerializer(
                obj.test_cases.filter(is_hidden=False), many=True,
            ).data
        return []
    get_test_cases = extend_schema_field(StudentTestCaseSerializer(many=True))(get_test_cases)
