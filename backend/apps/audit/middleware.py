"""Middleware that records audit logs for state-changing API calls."""
import logging

logger = logging.getLogger(__name__)


class AuditLogMiddleware:
    """Logs every non-GET request under /api/ that has an authenticated user."""

    SAFE_PATHS = ('/api/schema/', '/api/docs/', '/api/redoc/', '/admin/jsi18n/')
    AUDITED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._log(request, response)
        except Exception:
            logger.exception('Failed to record audit log')
        return response

    @staticmethod
    def _client_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def _log(self, request, response):
        path = request.path
        if request.method not in self.AUDITED_METHODS:
            return
        if not path.startswith('/api/'):
            return
        if any(path.startswith(p) for p in self.SAFE_PATHS):
            return
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return

        from .models import AuditLog

        payload = {}
        if request.content_type and 'json' in request.content_type:
            try:
                payload = {k: ('***' if 'password' in k.lower() else v)
                            for k, v in (request.data.items() if hasattr(request, 'data')
                                         else {}).items()}
            except Exception:
                payload = {}

        AuditLog.objects.create(
            user=user,
            method=request.method,
            path=path[:500],
            status_code=getattr(response, 'status_code', 0),
            ip_address=self._client_ip(request),
            user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:255],
            payload=payload,
        )
