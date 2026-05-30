from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsSuperAdmin

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = (IsAuthenticated, IsSuperAdmin)
    filterset_fields = ('user', 'method', 'status_code')
    search_fields = ('path', 'user__email', 'ip_address')
    ordering_fields = ('created_at',)
