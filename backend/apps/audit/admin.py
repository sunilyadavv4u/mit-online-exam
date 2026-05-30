from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'method', 'path', 'status_code', 'ip_address')
    list_filter = ('method', 'status_code')
    search_fields = ('user__email', 'path', 'ip_address')
    readonly_fields = ('id', 'user', 'method', 'path', 'status_code',
                       'ip_address', 'user_agent', 'payload', 'created_at')
