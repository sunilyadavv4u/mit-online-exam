from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EvaluationViewSet, StudentEvaluationViewSet

router = DefaultRouter()
router.register('me', StudentEvaluationViewSet, basename='my-evaluation')
router.register('', EvaluationViewSet, basename='evaluation')

urlpatterns = [
    path('', include(router.urls)),
]
