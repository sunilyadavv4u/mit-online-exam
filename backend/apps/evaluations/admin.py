from django.contrib import admin

from .models import Evaluation


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'evaluator', 'status', 'published_at')
    list_filter = ('status',)
    search_fields = ('attempt__student__email', 'attempt__exam__title')
    autocomplete_fields = ('attempt', 'evaluator')
