"""Import AI-generated question paper JSON into an exam."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from apps.exams.models import Exam, ExamStatus
from apps.questions.models import CodingTestCase, Question, QuestionOption, QuestionType

VALID_TYPES = {c.value for c in QuestionType}
VALID_DIFFICULTY = {'easy', 'medium', 'hard'}

TYPE_ALIASES = {
    'mcq': QuestionType.SINGLE_CHOICE,
    'single_mcq': QuestionType.SINGLE_CHOICE,
    'multi_mcq': QuestionType.MULTIPLE_CHOICE,
    'true/false': QuestionType.TRUE_FALSE,
    'truefalse': QuestionType.TRUE_FALSE,
    'fill_in_the_blank': QuestionType.FILL_BLANK,
    'fill-in-the-blank': QuestionType.FILL_BLANK,
    'short_answer': QuestionType.DESCRIPTIVE,
    'essay': QuestionType.DESCRIPTIVE,
    'code': QuestionType.CODING,
    'programming': QuestionType.CODING,
}


def flatten_questions_from_paper(paper: dict[str, Any]) -> list[dict[str, Any]]:
    if paper.get('format') == 'markdown':
        raise ValidationError(
            'This paper is plain text only. Generate again or edit JSON before importing.'
        )
    questions: list[dict[str, Any]] = []
    for section in paper.get('sections') or []:
        for q in section.get('questions') or []:
            if q.get('text'):
                questions.append(q)
    if not questions:
        raise ValidationError('No questions found in the generated paper to import.')
    return questions


def _normalize_type(raw: str | None) -> str:
    key = (raw or 'descriptive').lower().strip().replace(' ', '_').replace('-', '_')
    if key in VALID_TYPES:
        return key
    return TYPE_ALIASES.get(key, QuestionType.DESCRIPTIVE)


def _normalize_difficulty(raw: str | None) -> str:
    d = (raw or 'medium').lower().strip()
    return d if d in VALID_DIFFICULTY else 'medium'


def _option_text(opt: Any) -> str:
    if isinstance(opt, str):
        return opt.strip()
    if isinstance(opt, dict):
        return str(opt.get('text') or opt.get('label') or '').strip()
    return str(opt).strip()


def _answer_matches_option(correct: Any, text: str, index: int) -> bool:
    if correct is None:
        return False
    text_l = text.lower()
    if isinstance(correct, list):
        for c in correct:
            c_s = str(c).strip().lower()
            if c_s == text_l or c_s == str(index + 1):
                return True
            if len(c_s) == 1 and ord(c_s) - ord('a') == index:
                return True
        return False
    c_s = str(correct).strip().lower()
    if c_s == text_l:
        return True
    if c_s == str(index + 1):
        return True
    if len(c_s) == 1 and ord(c_s) - ord('a') == index:
        return True
    return False


def _build_options(q: dict[str, Any], qtype: str) -> list[dict[str, Any]]:
    correct = q.get('correct_answer')
    raw_opts = q.get('options') or []

    if qtype == QuestionType.TRUE_FALSE:
        truthy = {'true', 't', 'yes', '1'}
        correct_s = str(correct).strip().lower() if correct is not None else 'true'
        is_true = correct_s in truthy
        return [
            {'text': 'True', 'is_correct': is_true, 'order': 0},
            {'text': 'False', 'is_correct': not is_true, 'order': 1},
        ]

    if not raw_opts and qtype in {QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE}:
        if correct:
            return [
                {'text': str(correct), 'is_correct': True, 'order': 0},
                {'text': 'Other', 'is_correct': False, 'order': 1},
            ]
        return []

    options = []
    for i, opt in enumerate(raw_opts):
        text = _option_text(opt)[:500]
        if not text:
            continue
        options.append({
            'text': text,
            'is_correct': _answer_matches_option(correct, text, i),
            'order': i,
        })

    if qtype == QuestionType.SINGLE_CHOICE and options:
        correct_count = sum(1 for o in options if o['is_correct'])
        if correct_count == 0 and correct is not None:
            for o in options:
                if _answer_matches_option(correct, o['text'], o['order']):
                    o['is_correct'] = True
                    break
        if correct_count > 1:
            first = next((o for o in options if o['is_correct']), options[0])
            for o in options:
                o['is_correct'] = o is first

    return options


def _build_test_cases(q: dict[str, Any]) -> list[dict[str, Any]]:
    cases = []
    for i, tc in enumerate(q.get('test_cases') or []):
        if isinstance(tc, dict) and tc.get('expected_output'):
            cases.append({
                'input_data': str(tc.get('input_data') or ''),
                'expected_output': str(tc['expected_output']),
                'is_hidden': bool(tc.get('is_hidden', False)),
                'weight': Decimal(str(tc.get('weight', 1))),
                'order': i,
            })
    if not cases and q.get('expected_output'):
        cases.append({
            'input_data': str(q.get('input_data') or ''),
            'expected_output': str(q['expected_output']),
            'is_hidden': False,
            'weight': Decimal('1'),
            'order': 0,
        })
    return cases


def _question_payload(
    aq: dict[str, Any],
    exam: Exam,
    order: int,
) -> dict[str, Any]:
    qtype = _normalize_type(aq.get('type') or aq.get('question_type'))
    marks = aq.get('marks', 1)
    try:
        marks = Decimal(str(marks))
    except Exception:
        marks = Decimal('1')

    payload: dict[str, Any] = {
        'exam': exam.pk,
        'subject': exam.subject_id,
        'question_type': qtype,
        'text': str(aq.get('text', '')).strip(),
        'difficulty': _normalize_difficulty(aq.get('difficulty')),
        'marks': marks,
        'negative_marks': Decimal('0'),
        'order': order,
        'is_in_bank': True,
        'correct_answer_text': '',
        'coding_language': '',
        'starter_code': '',
        'expected_output': '',
        'options': [],
        'test_cases': [],
    }

    if qtype == QuestionType.FILL_BLANK:
        ans = aq.get('correct_answer')
        payload['correct_answer_text'] = (
            ', '.join(str(a) for a in ans) if isinstance(ans, list) else str(ans or '')
        )
    elif qtype == QuestionType.CODING:
        payload['coding_language'] = (aq.get('coding_language') or 'python').lower()[:20]
        payload['starter_code'] = str(aq.get('starter_code') or '')
        payload['expected_output'] = str(aq.get('expected_output') or '')
        payload['test_cases'] = _build_test_cases(aq)
    elif qtype in {
        QuestionType.SINGLE_CHOICE,
        QuestionType.MULTIPLE_CHOICE,
        QuestionType.TRUE_FALSE,
    }:
        payload['options'] = _build_options(aq, qtype)

    return payload


@transaction.atomic
def import_question_paper_to_exam(
    *,
    exam: Exam,
    paper: dict[str, Any],
    user,
    set_live: bool = False,
    update_exam_metadata: bool = True,
) -> dict[str, Any]:
    if not user.is_super_admin and exam.created_by_id != user.id:
        raise PermissionDenied('You can only import questions into exams you created.')

    ai_questions = flatten_questions_from_paper(paper)
    start_order = exam.questions.count()
    created_ids: list[str] = []

    for offset, aq in enumerate(ai_questions):
        data = _question_payload(aq, exam, start_order + offset)
        question = Question.objects.create(
            exam=exam,
            subject_id=data['subject'],
            question_type=data['question_type'],
            text=data['text'],
            difficulty=data['difficulty'],
            marks=data['marks'],
            negative_marks=data['negative_marks'],
            order=data['order'],
            is_in_bank=data['is_in_bank'],
            correct_answer_text=data['correct_answer_text'],
            coding_language=data['coding_language'],
            starter_code=data['starter_code'],
            expected_output=data['expected_output'],
            created_by=user,
        )
        for opt in data['options']:
            QuestionOption.objects.create(question=question, **opt)
        for tc in data['test_cases']:
            CodingTestCase.objects.create(question=question, **tc)
        created_ids.append(str(question.id))

    update_fields = []
    if update_exam_metadata:
        if paper.get('instructions'):
            exam.instructions = str(paper['instructions'])
            update_fields.append('instructions')
        if paper.get('duration_minutes'):
            exam.duration_minutes = int(paper['duration_minutes'])
            update_fields.append('duration_minutes')
        if paper.get('total_marks') is not None:
            exam.total_marks = Decimal(str(paper['total_marks']))
            update_fields.append('total_marks')
        if update_fields:
            exam.save(update_fields=update_fields)

    if set_live:
        exam.status = ExamStatus.LIVE
        exam.save(update_fields=['status'])

    return {
        'created_count': len(created_ids),
        'question_ids': created_ids,
        'exam_id': str(exam.id),
        'exam_slug': exam.slug,
        'exam_title': exam.title,
        'exam_status': exam.status,
    }
