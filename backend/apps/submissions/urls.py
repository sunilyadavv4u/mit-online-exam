from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .code_studio_api import CodeStudioRunView
from .views import ExamAttemptViewSet

router = DefaultRouter()
router.register('attempts', ExamAttemptViewSet, basename='attempt')

urlpatterns = [
    path('code-studio/run/', CodeStudioRunView.as_view(), name='code-studio-run'),
    path('', include(router.urls)),
]
