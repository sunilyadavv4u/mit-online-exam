"""Serializers for subjects, exams and enrollments."""
from django.utils.text import slugify
from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Exam, ExamEnrollment, ExamStatus, Subject


class SubjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    exam_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Subject
        fields = ('id', 'name', 'code', 'description', 'icon',
                  'is_active', 'created_by', 'exam_count',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')


class ExamEnrollmentSerializer(serializers.ModelSerializer):
    student_detail = UserSerializer(source='student', read_only=True)

    class Meta:
        model = ExamEnrollment
        fields = ('id', 'exam', 'student', 'student_detail',
                  'enrolled_at', 'enrolled_by')
        read_only_fields = ('id', 'enrolled_at', 'enrolled_by')


class ExamListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    question_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Exam
        fields = ('id', 'title', 'slug', 'subject', 'subject_name', 'subject_code',
                  'exam_type', 'status', 'duration_minutes', 'total_marks',
                  'passing_marks', 'start_time', 'end_time',
                  'created_by_name', 'question_count', 'created_at')


class ExamSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    subject_detail = SubjectSerializer(source='subject', read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True, default=0)
    question_count = serializers.IntegerField(read_only=True, default=0)
    slug = serializers.SlugField(required=False, allow_blank=True, max_length=220)

    class Meta:
        model = Exam
        fields = (
            'id', 'title', 'slug', 'description', 'instructions',
            'subject', 'subject_detail',
            'exam_type', 'status',
            'duration_minutes', 'total_marks', 'passing_marks', 'negative_marking',
            'randomize_questions', 'randomize_options',
            'show_results_immediately', 'allow_retake', 'enable_proctoring',
            'start_time', 'end_time',
            'created_by', 'enrolled_count', 'question_count',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'enrolled_count', 'question_count',
                            'created_at', 'updated_at')

    def validate(self, attrs):
        start = attrs.get('start_time') or getattr(self.instance, 'start_time', None)
        end = attrs.get('end_time') or getattr(self.instance, 'end_time', None)
        if start and end and end <= start:
            raise serializers.ValidationError('end_time must be after start_time.')

        passing = attrs.get('passing_marks',
                             getattr(self.instance, 'passing_marks', 0) or 0)
        total = attrs.get('total_marks',
                           getattr(self.instance, 'total_marks', 0) or 0)
        if passing and total and passing > total:
            raise serializers.ValidationError(
                'passing_marks cannot be greater than total_marks.'
            )
        return attrs

    def create(self, validated_data):
        if 'slug' not in validated_data or not validated_data['slug']:
            base = slugify(validated_data['title'])[:200]
            slug = base
            i = 1
            while Exam.objects.filter(slug=slug).exists():
                slug = f'{base}-{i}'
                i += 1
            validated_data['slug'] = slug
        return super().create(validated_data)


class ExamPublishSerializer(serializers.Serializer):
    """Body for publishing/changing exam status."""

    status = serializers.ChoiceField(choices=ExamStatus.choices)
