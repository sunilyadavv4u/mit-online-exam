from django.contrib import admin

from .models import AIRequest


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_type', 'is_success', 'latency_ms', 'created_at')
    list_filter = ('request_type', 'is_success')
    search_fields = ('user__email', 'prompt')
    readonly_fields = ('created_at',)
