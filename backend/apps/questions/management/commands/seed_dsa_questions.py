"""Seed MIT DSA coding question bank with hidden test cases (HackerRank / LeetCode style).

Usage:
    python manage.py seed_dsa_questions
    python manage.py seed_dsa_questions --exams          # also create tiered live exams
    python manage.py seed_dsa_questions --reset          # delete prior dsa_key:* questions first
"""
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.exams.models import Exam, ExamEnrollment, ExamStatus, ExamType, Subject
from apps.questions.dsa_question_bank import DSA_PROBLEMS, EXAM_PRESETS, PROBLEMS_BY_KEY
from apps.questions.models import CodingTestCase, Question, QuestionType
from apps.users.models import User, UserRole


class Command(BaseCommand):
    help = 'Seed DSA subject question bank with visible + hidden Python test cases.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exams',
            action='store_true',
            help='Create Easy / Medium / Hard / Full Assessment live exams and enroll students.',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove existing questions tagged dsa_key:* before seeding.',
        )
        parser.add_argument(
            '--teacher-email',
            default='teacher@mewatitech.edu',
            help='Teacher account that owns seeded content.',
        )

    def _teacher(self, email: str):
        teacher = User.objects.filter(email=email, role=UserRole.TEACHER).first()
        if not teacher:
            teacher = User.objects.filter(role=UserRole.TEACHER).first()
        if not teacher:
            raise SystemExit(
                'No teacher user found. Run seed_demo_data first or pass --teacher-email.'
            )
        return teacher

    def _subject(self, teacher):
        subject, _ = Subject.objects.get_or_create(
            code='DSA101',
            defaults={
                'name': 'DSA',
                'icon': '🧮',
                'description': 'Data Structures & Algorithms — MIT coding practice bank.',
                'created_by': teacher,
            },
        )
        return subject

    def _reset_bank(self):
        qs = Question.objects.filter(tags__icontains='dsa_key:')
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.WARNING(f'  Removed {count} existing DSA bank questions.'))

    def _seed_question(self, teacher, subject, spec: dict, order: int, exam=None) -> Question:
        tag_key = f'dsa_key:{spec["key"]}'
        existing = Question.objects.filter(tags__icontains=tag_key, exam=exam).first()
        if existing:
            return existing

        q = Question.objects.create(
            exam=exam,
            subject=subject,
            question_type=QuestionType.CODING,
            text=spec['text'],
            coding_language=spec['coding_language'],
            starter_code=spec['starter_code'],
            marks=Decimal(str(spec['marks'])),
            difficulty=spec['difficulty'],
            created_by=teacher,
            order=order,
            is_in_bank=exam is None,
            tags=spec['tags'],
        )
        CodingTestCase.objects.bulk_create([
            CodingTestCase(
                question=q,
                input_data=tc['input_data'],
                expected_output=tc['expected_output'],
                is_hidden=tc.get('is_hidden', False),
                order=i + 1,
                weight=1,
            )
            for i, tc in enumerate(spec['test_cases'])
        ])
        return q

    def _create_exam(self, teacher, subject, title, keys: list[str], duration: int):
        slug = slugify(title)
        now = timezone.now()
        total_marks = sum(PROBLEMS_BY_KEY[k]['marks'] for k in keys)
        exam, created = Exam.objects.get_or_create(
            slug=slug,
            defaults={
                'title': title,
                'description': (
                    'Auto-generated DSA coding assessment for Mewati Institute of Technology. '
                    'Sample tests are visible when you click Run; hidden tests run on final submit.'
                ),
                'instructions': (
                    'Solve each problem in Python using stdin/stdout. '
                    'Use "Run sample tests" to debug. Hidden tests run when you submit the exam.'
                ),
                'subject': subject,
                'exam_type': ExamType.CODING,
                'status': ExamStatus.LIVE,
                'duration_minutes': duration,
                'total_marks': Decimal(str(total_marks)),
                'passing_marks': Decimal(str(max(1, int(total_marks * 0.4)))),
                'negative_marking': Decimal('0'),
                'randomize_questions': False,
                'randomize_options': False,
                'show_results_immediately': False,
                'allow_retake': True,
                'enable_proctoring': True,
                'start_time': now - timedelta(minutes=5),
                'end_time': now + timedelta(days=90),
                'created_by': teacher,
            },
        )
        if not created and exam.questions.exists():
            self.stdout.write(self.style.NOTICE(f'  Exam exists (skipped attach): {title}'))
            return exam

        if not created:
            exam.questions.all().delete()

        for order, key in enumerate(keys, start=1):
            self._seed_question(teacher, subject, PROBLEMS_BY_KEY[key], order, exam=exam)

        students = User.objects.filter(role=UserRole.STUDENT, is_active=True)
        ExamEnrollment.objects.bulk_create(
            [
                ExamEnrollment(exam=exam, student=s, enrolled_by=teacher)
                for s in students
            ],
            ignore_conflicts=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'  Exam: {title} ({len(keys)} questions, {total_marks} marks, slug={slug})'
        ))
        return exam

    @transaction.atomic
    def handle(self, *args, **opts):
        teacher = self._teacher(opts['teacher_email'])
        subject = self._subject(teacher)

        if opts['reset']:
            self._reset_bank()

        self.stdout.write(self.style.NOTICE(
            f'Seeding {len(DSA_PROBLEMS)} DSA problems for {subject.name}...'
        ))

        bank_count = 0
        for order, spec in enumerate(DSA_PROBLEMS, start=1):
            q = self._seed_question(teacher, subject, spec, order, exam=None)
            if q.exam is None:
                bank_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'  Question bank: {bank_count} coding problems (visible + hidden tests each).'
        ))

        if opts['exams']:
            self._create_exam(
                teacher, subject,
                'MIT DSA — Easy Practice',
                EXAM_PRESETS['easy'],
                duration=90,
            )
            self._create_exam(
                teacher, subject,
                'MIT DSA — Medium Challenge',
                EXAM_PRESETS['medium'],
                duration=120,
            )
            self._create_exam(
                teacher, subject,
                'MIT DSA — Hard Assessment',
                EXAM_PRESETS['hard'],
                duration=150,
            )
            all_keys = [p['key'] for p in DSA_PROBLEMS]
            self._create_exam(
                teacher, subject,
                'MIT DSA — Full Coding Assessment',
                all_keys,
                duration=240,
            )

        self.stdout.write(self.style.SUCCESS('DSA seed complete.'))
        self.stdout.write(self.style.NOTICE(
            '\nNote: Problems are MIT-original practice items inspired by common DSA patterns. '
            'They are not copied from LeetCode or HackerRank.\n'
            'Run with --exams to publish tiered live exams for all enrolled students.\n'
        ))
