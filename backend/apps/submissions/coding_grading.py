"""Grade coding answers against visible and hidden test cases."""
from __future__ import annotations

from apps.questions.models import CodingTestCase, QuestionType

from .code_runner import run_python_against_tests


def _sanitize_details(test_cases: list[CodingTestCase], raw_details: list[dict]) -> list[dict]:
    """Return result details safe for students (no hidden inputs/outputs)."""
    sanitized: list[dict] = []
    hidden_n = 0
    for tc, detail in zip(test_cases, raw_details):
        if tc.is_hidden:
            hidden_n += 1
            sanitized.append({
                'label': f'Hidden test {hidden_n}',
                'passed': detail.get('passed', False),
                'hidden': True,
            })
        else:
            sanitized.append({
                'input': detail.get('input', ''),
                'expected': detail.get('expected', ''),
                'actual': detail.get('actual', ''),
                'stderr': detail.get('stderr', ''),
                'passed': detail.get('passed', False),
                'hidden': False,
            })
    return sanitized


def grade_coding_answer(answer, *, language: str = 'python') -> dict:
    """Run all test cases (including hidden) and persist results on the answer."""
    question = answer.question
    if question.question_type != QuestionType.CODING:
        return answer.code_run_results or {}

    code = (answer.code_answer or '').strip()
    test_cases = list(question.test_cases.order_by('order'))
    total = len(test_cases)

    if not code or not total:
        data = {'passed': 0, 'total': total, 'details': []}
        answer.code_run_results = data
        answer.save(update_fields=['code_run_results'])
        return data

    cases = [
        {'input_data': tc.input_data, 'expected_output': tc.expected_output}
        for tc in test_cases
    ]

    lang = (language or answer.code_language or question.coding_language or 'python').lower()
    if lang == 'python':
        result = run_python_against_tests(code, cases)
        data = {
            'passed': result.passed,
            'total': result.total,
            'details': _sanitize_details(test_cases, result.details),
        }
    else:
        data = {
            'passed': 0,
            'total': total,
            'details': [],
            'message': f'Auto-grading for {lang} is not enabled; teacher review required.',
        }

    answer.code_run_results = data
    answer.save(update_fields=['code_run_results'])
    return data
