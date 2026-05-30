from django.contrib import admin

from .models import Answer, ExamAttempt, ProctorEvent


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'status', 'total_score',
                    'is_passed', 'started_at', 'submitted_at')
    list_filter = ('status', 'is_passed', 'exam__subject')
    search_fields = ('exam__title', 'student__email')
    autocomplete_fields = ('exam', 'student')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct',
                    'auto_score', 'manual_score')
    search_fields = ('attempt__student__email', 'question__text')


@admin.register(ProctorEvent)
class ProctorEventAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'event_type', 'created_at')
    list_filter = ('event_type',)
    search_fields = ('attempt__student__email',)
