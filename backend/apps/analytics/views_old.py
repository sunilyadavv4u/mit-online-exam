"""Dashboard / analytics endpoints + report exports."""
import csv
from datetime import timedelta
from decimal import Decimal
from io import BytesIO

from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from openpyxl import Workbook
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from apps.exams.models import Exam, ExamStatus
from apps.submissions.models import AttemptStatus, ExamAttempt
from apps.users.models import User, UserRole
from apps.users.permissions import IsTeacher


# ----- Lightweight serializers used purely for OpenAPI docs -------------------
class TeacherDashboardSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_exams = serializers.IntegerField()
    active_exams = serializers.IntegerField()
    pending_evaluations = serializers.IntegerField()
    recent_attempts = serializers.IntegerField()
    pass_percentage = serializers.FloatField()
    average_score = serializers.FloatField()
    upcoming_exams = serializers.ListField(child=serializers.DictField())
    attempts_by_day = serializers.ListField(child=serializers.DictField())


class StudentDashboardSerializer(serializers.Serializer):
    upcoming_exams = serializers.ListField(child=serializers.DictField())
    completed_exams = serializers.IntegerField()
    in_progress_exams = serializers.IntegerField()
    passed_exams = serializers.IntegerField()
    average_score = serializers.FloatField()
    recent_results = serializers.ListField(child=serializers.DictField())


class SuperAdminDashboardSerializer(serializers.Serializer):
    users_by_role = serializers.ListField(child=serializers.DictField())
    active_users = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_attempts = serializers.IntegerField()
    live_exams = serializers.IntegerField()
    registrations_last_30_days = serializers.IntegerField()


class LeaderboardRowSerializer(serializers.Serializer):
    student__id = serializers.UUIDField()
    student__email = serializers.EmailField()
    student__first_name = serializers.CharField()
    student__last_name = serializers.CharField()
    score = serializers.FloatField()
    attempts = serializers.IntegerField()
    passed = serializers.IntegerField()


@extend_schema(responses=TeacherDashboardSerializer)
class TeacherDashboardView(APIView):
    permission_classes = (IsAuthenticated, IsTeacher)
    serializer_class = TeacherDashboardSerializer

    def get(self, request):
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)

        total_students = User.objects.filter(role=UserRole.STUDENT, is_active=True).count()
        total_exams = Exam.objects.count()
        active_exams = Exam.objects.filter(
            status__in=[ExamStatus.SCHEDULED, ExamStatus.LIVE],
            end_time__gte=now,
        ).count()
        pending_evaluations = ExamAttempt.objects.filter(
            status__in=[AttemptStatus.SUBMITTED, AttemptStatus.AUTO_SUBMITTED],
        ).count()
        recent_attempts = ExamAttempt.objects.filter(submitted_at__gte=seven_days_ago).count()

        passed = ExamAttempt.objects.filter(
            status=AttemptStatus.PUBLISHED, is_passed=True,
        ).count()
        published_total = ExamAttempt.objects.filter(status=AttemptStatus.PUBLISHED).count()
        pass_pct = (passed / published_total * 100) if published_total else 0

        avg_score = (ExamAttempt.objects
                     .filter(status=AttemptStatus.PUBLISHED)
                     .aggregate(avg=Avg('total_score'))['avg']) or 0

        upcoming_exams = (Exam.objects
                          .filter(status__in=[ExamStatus.SCHEDULED, ExamStatus.LIVE],
                                  start_time__gte=now)
                          .order_by('start_time')[:5]
                          .values('id', 'title', 'subject__name', 'start_time'))

        attempts_by_day = (ExamAttempt.objects
                           .filter(submitted_at__gte=seven_days_ago)
                           .extra({'day': "strftime('%%Y-%%m-%%d', submitted_at)"})
                           .values('day')
                           .annotate(count=Count('id'))
                           .order_by('day'))

        return Response({
            'total_students': total_students,
            'total_exams': total_exams,
            'active_exams': active_exams,
            'pending_evaluations': pending_evaluations,
            'recent_attempts': recent_attempts,
            'pass_percentage': round(pass_pct, 2),
            'average_score': float(avg_score) if avg_score else 0,
            'upcoming_exams': list(upcoming_exams),
            'attempts_by_day': list(attempts_by_day),
        })


@extend_schema(responses=StudentDashboardSerializer)
class StudentDashboardView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentDashboardSerializer

    def get(self, request):
        user = request.user
        now = timezone.now()

        upcoming = (Exam.objects
                    .filter(enrollments__student=user,
                            status__in=[ExamStatus.SCHEDULED, ExamStatus.LIVE],
                            end_time__gte=now)
                    .distinct()
                    .order_by('start_time')[:5]
                    .values('id', 'title', 'subject__name',
                            'start_time', 'end_time', 'duration_minutes'))

        attempts = ExamAttempt.objects.filter(student=user)
        completed = attempts.filter(
            status__in=[AttemptStatus.PUBLISHED, AttemptStatus.EVALUATED],
        ).count()
        in_progress = attempts.filter(status=AttemptStatus.IN_PROGRESS).count()
        avg_score = attempts.filter(
            status=AttemptStatus.PUBLISHED,
        ).aggregate(avg=Avg('total_score'))['avg'] or 0
        passed = attempts.filter(status=AttemptStatus.PUBLISHED, is_passed=True).count()

        recent_results = (attempts.filter(status=AttemptStatus.PUBLISHED)
                          .order_by('-submitted_at')[:5]
                          .values('id', 'exam__title', 'exam__subject__name',
                                  'total_score', 'is_passed', 'submitted_at'))

        return Response({
            'upcoming_exams': list(upcoming),
            'completed_exams': completed,
            'in_progress_exams': in_progress,
            'passed_exams': passed,
            'average_score': float(avg_score),
            'recent_results': list(recent_results),
        })


@extend_schema(responses=SuperAdminDashboardSerializer)
class SuperAdminDashboardView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SuperAdminDashboardSerializer

    def get(self, request):
        if not request.user.is_super_admin:
            return Response({'detail': 'Forbidden'}, status=403)
        now = timezone.now()

        users_by_role = (User.objects.values('role')
                         .annotate(count=Count('id')).order_by('role'))
        active_users = User.objects.filter(is_active=True).count()
        total_users = User.objects.count()
        total_attempts = ExamAttempt.objects.count()
        live_exams = Exam.objects.filter(status=ExamStatus.LIVE).count()
        registrations_30d = User.objects.filter(
            created_at__gte=now - timedelta(days=30),
        ).count()

        return Response({
            'users_by_role': list(users_by_role),
            'active_users': active_users,
            'total_users': total_users,
            'total_attempts': total_attempts,
            'live_exams': live_exams,
            'registrations_last_30_days': registrations_30d,
        })


@extend_schema(
    parameters=[OpenApiParameter('exam_id', OpenApiTypes.UUID, required=False)],
    responses=LeaderboardRowSerializer(many=True),
)
class LeaderboardView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeaderboardRowSerializer

    def get(self, request):
        exam_id = request.query_params.get('exam_id')
        qs = ExamAttempt.objects.filter(status=AttemptStatus.PUBLISHED)
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        qs = (qs.values('student__id', 'student__email', 'student__first_name',
                        'student__last_name')
                .annotate(score=Avg('total_score'),
                          attempts=Count('id'),
                          passed=Count('id', filter=Q(is_passed=True)))
                .order_by('-score')[:50])
        return Response(list(qs))


class ReportsViewSet(ViewSet):
    permission_classes = (IsAuthenticated, IsTeacher)

    @extend_schema(
        parameters=[OpenApiParameter('exam_id', OpenApiTypes.UUID, required=False)],
        responses={200: OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=['get'], url_path='attempts-csv')
    def attempts_csv(self, request):
        exam_id = request.query_params.get('exam_id')
        qs = ExamAttempt.objects.select_related('student', 'exam')
        if exam_id:
            qs = qs.filter(exam_id=exam_id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attempts.csv"'
        writer = csv.writer(response)
        writer.writerow(['Exam', 'Student', 'Email', 'Status', 'Total Score',
                          'Is Passed', 'Submitted At'])
        for a in qs:
            writer.writerow([
                a.exam.title, a.student.full_name, a.student.email,
                a.status, a.total_score, a.is_passed,
                a.submitted_at.isoformat() if a.submitted_at else '',
            ])
        return response

    @extend_schema(
        parameters=[OpenApiParameter('exam_id', OpenApiTypes.UUID, required=False)],
        responses={200: OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=['get'], url_path='attempts-xlsx')
    def attempts_xlsx(self, request):
        exam_id = request.query_params.get('exam_id')
        qs = ExamAttempt.objects.select_related('student', 'exam')
        if exam_id:
            qs = qs.filter(exam_id=exam_id)

        wb = Workbook()
        ws = wb.active
        ws.title = 'Attempts'
        ws.append(['Exam', 'Student', 'Email', 'Status',
                   'Objective', 'Descriptive', 'Total', 'Passed', 'Submitted At'])
        for a in qs:
            ws.append([
                a.exam.title, a.student.full_name, a.student.email,
                a.status, float(a.objective_score), float(a.descriptive_score),
                float(a.total_score), 'Yes' if a.is_passed else 'No',
                a.submitted_at.isoformat() if a.submitted_at else '',
            ])

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        response = HttpResponse(
            buf.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="attempts.xlsx"'
        return response

    @extend_schema(
        parameters=[OpenApiParameter('attempt_id', OpenApiTypes.UUID, OpenApiParameter.PATH)],
        responses={200: OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=['get'], url_path='attempt-pdf/(?P<attempt_id>[^/.]+)')
    def attempt_pdf(self, request, attempt_id=None):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas

        attempt = ExamAttempt.objects.select_related('student', 'exam')\
                                      .filter(id=attempt_id).first()
        if not attempt:
            return Response({'detail': 'Not found'}, status=404)

        buf = BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        c.setFont('Helvetica-Bold', 16)
        c.drawString(40, height - 60, 'Mewati Institute of Technology')
        c.setFont('Helvetica', 12)
        c.drawString(40, height - 80, f'Result: {attempt.exam.title}')
        c.drawString(40, height - 100, f'Student: {attempt.student.full_name} <{attempt.student.email}>')
        c.drawString(40, height - 120, f'Status: {attempt.status}')
        c.drawString(40, height - 140, f'Score: {attempt.total_score} / {attempt.exam.total_marks}')
        c.drawString(40, height - 160, f'Passed: {"Yes" if attempt.is_passed else "No"}')
        if attempt.submitted_at:
            c.drawString(40, height - 180, f'Submitted: {attempt.submitted_at}')
        c.showPage()
        c.save()
        buf.seek(0)
        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="result-{attempt_id}.pdf"'
        return response
