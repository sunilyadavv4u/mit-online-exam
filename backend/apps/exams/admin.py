from django.contrib import admin

from .models import Exam, ExamEnrollment, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'exam_type', 'status',
                    'start_time', 'end_time', 'total_marks')
    list_filter = ('status', 'exam_type', 'subject')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('subject', 'created_by')


@admin.register(ExamEnrollment)
class ExamEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'enrolled_at')
    search_fields = ('exam__title', 'student__email')
    autocomplete_fields = ('exam', 'student', 'enrolled_by')
