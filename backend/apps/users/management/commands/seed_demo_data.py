"""Management command: create a complete set of demo data.

Usage:
    python manage.py seed_demo_data
"""
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from apps.exams.models import Exam, ExamEnrollment, ExamStatus, ExamType, Subject
from apps.questions.models import (
    CodingLanguage,
    CodingTestCase,
    DifficultyLevel,
    Question,
    QuestionOption,
    QuestionType,
)
from apps.users.models import StudentProfile, TeacherProfile, User, UserRole

fake = Faker()


SUBJECTS = [
    ('Python', 'PY101', '🐍'),
    ('PySpark', 'SPK201', '⚡'),
    ('SQL', 'SQL101', '🗄️'),
    ('Azure Databricks', 'AZD301', '☁️'),
    ('SQL Server', 'MSS101', '💼'),
    ('Azure Data Factory', 'ADF301', '🏭'),
    ('Microsoft Fabric', 'FAB301', '🧵'),
    ('Azure Synapse Analytics', 'SYN301', '🔗'),
    ('Azure Data Lake Gen2', 'ADL301', '🌊'),
    ('Azure Event Hubs', 'EVT301', '📡'),
    ('Spark Streaming', 'SPS301', '🌀'),
    ('Data Engineering', 'DE401', '🛠️'),
    ('Architect Designing', 'ARCH401', '🏛️'),
    ('DSA', 'DSA101', '🧮'),
    ('Java', 'JAVA101', '☕'),
]


class Command(BaseCommand):
    help = 'Seed the database with demo users, subjects, exams, and questions.'

    def add_arguments(self, parser):
        parser.add_argument('--students', type=int, default=15)

    @transaction.atomic
    def handle(self, *args, **opts):
        self.stdout.write(self.style.NOTICE('Seeding demo data...'))

        admin, created = User.objects.get_or_create(
            email='admin@mewatitech.edu',
            defaults={
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': UserRole.SUPER_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'is_email_verified': True,
            },
        )
        if created:
            admin.set_password('Admin@12345')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'  Created super admin: {admin.email} / Admin@12345'))

        teacher, created = User.objects.get_or_create(
            email='teacher@mewatitech.edu',
            defaults={
                'first_name': 'Demo',
                'last_name': 'Teacher',
                'role': UserRole.TEACHER,
                'is_active': True,
                'is_email_verified': True,
            },
        )
        if created:
            teacher.set_password('Teacher@12345')
            teacher.save()
            self.stdout.write(self.style.SUCCESS(f'  Created teacher: {teacher.email} / Teacher@12345'))

        TeacherProfile.objects.get_or_create(
            user=teacher,
            defaults={
                'employee_id': 'MIT-T-DEMO01',
                'designation': 'Senior Trainer',
                'department': 'Data Engineering',
                'expertise': 'Python, PySpark, SQL, Azure Databricks',
                'years_of_experience': 12,
            },
        )

        students = []
        n_students = opts['students']
        for i in range(n_students):
            email = f'student{i+1}@mewatitech.edu'
            student, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'role': UserRole.STUDENT,
                    'is_active': True,
                    'is_email_verified': True,
                    'phone': fake.phone_number()[:20],
                },
            )
            if created:
                student.set_password('Student@12345')
                student.save()
            students.append(student)

            StudentProfile.objects.get_or_create(
                user=student,
                defaults={
                    'enrollment_id': f'MIT-S-{i+1:05d}',
                    'course': 'Data Engineering Bootcamp',
                    'batch': 'Batch-2026',
                },
            )
        self.stdout.write(self.style.SUCCESS(
            f'  Created {len(students)} demo students (password: Student@12345)'
        ))

        subject_objs = {}
        for name, code, icon in SUBJECTS:
            subject, _ = Subject.objects.get_or_create(
                code=code,
                defaults={'name': name, 'icon': icon, 'created_by': teacher,
                          'description': f'{name} - taught by Mewati Institute of Technology.'},
            )
            subject_objs[name] = subject
        self.stdout.write(self.style.SUCCESS(f'  Subjects: {len(subject_objs)}'))

        now = timezone.now()
        for sub_name in ('Python', 'SQL', 'PySpark'):
            subject = subject_objs[sub_name]
            title = f'{sub_name} Fundamentals - Demo Exam'
            slug = slugify(title)
            exam, _ = Exam.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'description': f'A demo exam covering {sub_name} fundamentals.',
                    'instructions': ('Read each question carefully. You may not switch '
                                      'tabs or exit fullscreen. Auto-submit on time-up.'),
                    'subject': subject,
                    'exam_type': ExamType.MIXED,
                    'status': ExamStatus.LIVE,
                    'duration_minutes': 60,
                    'total_marks': Decimal('20.00'),
                    'passing_marks': Decimal('10.00'),
                    'negative_marking': Decimal('0.25'),
                    'randomize_questions': True,
                    'randomize_options': True,
                    'show_results_immediately': False,
                    'allow_retake': False,
                    'enable_proctoring': True,
                    'start_time': now - timedelta(minutes=10),
                    'end_time': now + timedelta(days=7),
                    'created_by': teacher,
                },
            )

            # MCQ
            mcq = Question.objects.create(
                exam=exam, subject=subject,
                question_type=QuestionType.SINGLE_CHOICE,
                text=f'Which of these is a feature of {sub_name}?',
                marks=Decimal('2'), negative_marks=Decimal('0.5'),
                created_by=teacher, order=1, is_in_bank=True,
                difficulty=DifficultyLevel.EASY,
            )
            QuestionOption.objects.bulk_create([
                QuestionOption(question=mcq, text='Distributed processing',
                                is_correct=(sub_name == 'PySpark'), order=1),
                QuestionOption(question=mcq, text='Dynamic typing',
                                is_correct=(sub_name == 'Python'), order=2),
                QuestionOption(question=mcq, text='ACID transactions',
                                is_correct=(sub_name == 'SQL'), order=3),
                QuestionOption(question=mcq, text='None of these', is_correct=False, order=4),
            ])

            # True/False
            tf = Question.objects.create(
                exam=exam, subject=subject,
                question_type=QuestionType.TRUE_FALSE,
                text=f'{sub_name} is open-source.',
                marks=Decimal('1'),
                created_by=teacher, order=2, is_in_bank=True,
                difficulty=DifficultyLevel.EASY,
            )
            QuestionOption.objects.bulk_create([
                QuestionOption(question=tf, text='True', is_correct=True, order=1),
                QuestionOption(question=tf, text='False', is_correct=False, order=2),
            ])

            # Fill blank
            fb = Question.objects.create(
                exam=exam, subject=subject,
                question_type=QuestionType.FILL_BLANK,
                text=f'The official documentation site of {sub_name} typically lives under ____.',
                correct_answer_text='docs',
                marks=Decimal('1'),
                created_by=teacher, order=3, is_in_bank=True,
                difficulty=DifficultyLevel.MEDIUM,
            )

            # Descriptive
            Question.objects.create(
                exam=exam, subject=subject,
                question_type=QuestionType.DESCRIPTIVE,
                text=f'Briefly explain what makes {sub_name} suitable for data engineering.',
                marks=Decimal('8'),
                created_by=teacher, order=4, is_in_bank=True,
                difficulty=DifficultyLevel.HARD,
            )

            # Coding
            coding_lang = {
                'Python': CodingLanguage.PYTHON,
                'SQL': CodingLanguage.SQL,
                'PySpark': CodingLanguage.PYSPARK,
            }[sub_name]
            coding = Question.objects.create(
                exam=exam, subject=subject,
                question_type=QuestionType.CODING,
                text=f'Write a function in {sub_name} that returns the square of the input.',
                coding_language=coding_lang,
                starter_code='def square(x):\n    pass' if sub_name == 'Python'
                              else 'SELECT * FROM ...' if sub_name == 'SQL'
                              else 'def square(x):\n    return ...',
                marks=Decimal('8'),
                created_by=teacher, order=5, is_in_bank=True,
                difficulty=DifficultyLevel.HARD,
            )
            CodingTestCase.objects.bulk_create([
                CodingTestCase(question=coding, input_data='2', expected_output='4',
                                is_hidden=False, order=1, weight=1),
                CodingTestCase(question=coding, input_data='5', expected_output='25',
                                is_hidden=True, order=2, weight=1),
                CodingTestCase(question=coding, input_data='10', expected_output='100',
                                is_hidden=True, order=3, weight=1),
            ])

            # Enroll all students
            ExamEnrollment.objects.bulk_create(
                [ExamEnrollment(exam=exam, student=s, enrolled_by=teacher) for s in students],
                ignore_conflicts=True,
            )
            self.stdout.write(self.style.SUCCESS(
                f'  Exam ready: {exam.title} (slug={exam.slug})'
            ))

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
        self.stdout.write(self.style.NOTICE(
            '\nLogins:\n'
            '  Super Admin -> admin@mewatitech.edu / Admin@12345\n'
            '  Teacher     -> teacher@mewatitech.edu / Teacher@12345\n'
            '  Student     -> student1@mewatitech.edu / Student@12345  (and student2..studentN)\n'
        ))
