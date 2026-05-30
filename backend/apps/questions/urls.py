from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CodingTestCaseViewSet, QuestionOptionViewSet, QuestionViewSet

router = DefaultRouter()
router.register('options', QuestionOptionViewSet, basename='question-option')
router.register('test-cases', CodingTestCaseViewSet, basename='question-test-case')
router.register('', QuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
]
