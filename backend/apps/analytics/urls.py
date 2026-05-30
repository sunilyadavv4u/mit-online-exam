from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LeaderboardView,
    ReportsViewSet,
    StudentDashboardView,
    SuperAdminDashboardView,
    TeacherDashboardView,
)

router = DefaultRouter()
router.register('reports', ReportsViewSet, basename='reports')

urlpatterns = [
    path('teacher-dashboard/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('student-dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('super-admin-dashboard/', SuperAdminDashboardView.as_view(), name='super-admin-dashboard'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('', include(router.urls)),
]
