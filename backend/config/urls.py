"""Top-level URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def healthcheck(_request):
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok', 'service': 'mit-exam-backend'})


def root_redirect(_request):
    """Friendly redirect for anyone hitting the bare backend URL."""
    return redirect('swagger-ui')


def favicon(_request):
    """Return an empty 204 so browsers stop spamming /favicon.ico 404s in dev."""
    return HttpResponse(status=204)


api_v1_patterns = [
    path('auth/', include('apps.authentication.urls')),
    path('users/', include('apps.users.urls')),
    path('exams/', include('apps.exams.urls')),
    path('questions/', include('apps.questions.urls')),
    path('submissions/', include('apps.submissions.urls')),
    path('evaluations/', include('apps.evaluations.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('ai/', include('apps.ai_assistant.urls')),
    path('audit/', include('apps.audit.urls')),
]

urlpatterns = [
    path('', root_redirect, name='root'),
    path('favicon.ico', favicon),
    path('admin/', admin.site.urls),
    path('health/', healthcheck, name='health'),
    path('api/v1/', include(api_v1_patterns)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
