from django.contrib import admin

from .models import CodingTestCase, Question, QuestionOption


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 0


class CodingTestCaseInline(admin.TabularInline):
    model = CodingTestCase
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_type', 'subject', 'exam',
                    'difficulty', 'marks', 'is_in_bank')
    list_filter = ('question_type', 'difficulty', 'subject',
                   'is_in_bank', 'coding_language')
    search_fields = ('text', 'tags')
    inlines = [QuestionOptionInline, CodingTestCaseInline]
    autocomplete_fields = ('exam', 'subject', 'created_by')
