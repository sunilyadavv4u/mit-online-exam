from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StudentProfileViewSet, TeacherProfileViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('students', StudentProfileViewSet, basename='student-profile')
router.register('teachers', TeacherProfileViewSet, basename='teacher-profile')

urlpatterns = [
    path('', include(router.urls)),
]
