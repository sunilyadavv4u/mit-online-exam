"""Serializers for exam attempts, answers, and proctor events."""
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.exams.serializers import ExamListSerializer
from apps.questions.serializers import StudentQuestionSerializer

from .models import Answer, ExamAttempt, ProctorEvent


class AnswerWriteSerializer(serializers.ModelSerializer):
    """Used by students when saving / updating their answer for a question."""

    class Meta:
        model = Answer
        fields = ('id', 'question', 'selected_options', 'text_answer',
                  'code_answer', 'code_language', 'uploaded_file')
        read_only_fields = ('id',)


class AnswerReadSerializer(serializers.ModelSerializer):
    """Used by teachers/students to read answers (with grading info)."""

    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    question_marks = serializers.DecimalField(source='question.marks',
                                              max_digits=6, decimal_places=2,
                                              read_only=True)
    final_score = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Answer
        fields = ('id', 'attempt', 'question', 'question_text', 'question_type',
                  'question_marks', 'selected_options', 'text_answer',
                  'code_answer', 'code_language', 'code_run_results',
                  'uploaded_file', 'is_correct',
                  'auto_score', 'manual_score', 'final_score',
                  'teacher_comment', 'answered_at')


class ProctorEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProctorEvent
        fields = ('id', 'attempt', 'event_type', 'metadata', 'created_at')
        read_only_fields = ('id', 'created_at')


class ExamAttemptSerializer(serializers.ModelSerializer):
    exam_detail = ExamListSerializer(source='exam', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = ExamAttempt
        fields = (
            'id', 'exam', 'exam_detail', 'student', 'student_email', 'student_name',
            'status', 'started_at', 'submitted_at', 'time_spent_seconds',
            'objective_score', 'descriptive_score', 'total_score', 'is_passed',
            'tab_switch_count', 'fullscreen_exit_count', 'proctor_flags',
            'ip_address', 'user_agent', 'question_order',
        )
        read_only_fields = (
            'id', 'student', 'started_at', 'submitted_at', 'time_spent_seconds',
            'objective_score', 'descriptive_score', 'total_score', 'is_passed',
            'tab_switch_count', 'fullscreen_exit_count', 'proctor_flags',
            'ip_address', 'user_agent',
        )


class AttemptDetailSerializer(ExamAttemptSerializer):
    answers = AnswerReadSerializer(many=True, read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta(ExamAttemptSerializer.Meta):
        fields = ExamAttemptSerializer.Meta.fields + ('answers', 'questions')

    def get_questions(self, obj):
        # Return questions in the order the student saw them (or default order)
        question_ids = obj.question_order or list(
            obj.exam.questions.order_by('order', 'created_at').values_list('id', flat=True)
        )
        questions_by_id = {str(q.id): q for q in obj.exam.questions.all()}
        ordered = [questions_by_id[str(qid)] for qid in question_ids if str(qid) in questions_by_id]
        return StudentQuestionSerializer(ordered, many=True).data
    get_questions = extend_schema_field(StudentQuestionSerializer(many=True))(get_questions)
