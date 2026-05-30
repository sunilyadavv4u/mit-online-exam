from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExamViewSet, SubjectViewSet

router = DefaultRouter()
router.register('subjects', SubjectViewSet, basename='subject')
router.register('', ExamViewSet, basename='exam')

urlpatterns = [
    path('', include(router.urls)),
]
