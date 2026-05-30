"""Auto-evaluation logic for objective answers and coding answers."""
from decimal import Decimal

from apps.questions.models import Question, QuestionType


def _is_textual_match(submitted: str, correct: str) -> bool:
    return (submitted or '').strip().lower() == (correct or '').strip().lower()


def evaluate_answer(answer) -> Decimal:
    """Auto-evaluate an answer and update its is_correct/auto_score fields.

    Returns the auto score awarded (Decimal).
    """
    question: Question = answer.question
    qt = question.question_type
    marks = Decimal(question.marks)
    negative = Decimal(question.negative_marks or 0)

    score = Decimal('0')
    is_correct: bool | None = None

    if qt in {QuestionType.SINGLE_CHOICE, QuestionType.TRUE_FALSE}:
        selected_ids = set(answer.selected_options.values_list('id', flat=True))
        correct_ids = set(question.options.filter(is_correct=True).values_list('id', flat=True))
        is_correct = bool(selected_ids) and selected_ids == correct_ids
        score = marks if is_correct else (-negative if selected_ids else Decimal('0'))

    elif qt == QuestionType.MULTIPLE_CHOICE:
        selected_ids = set(answer.selected_options.values_list('id', flat=True))
        correct_ids = set(question.options.filter(is_correct=True).values_list('id', flat=True))
        if not selected_ids:
            is_correct = None
            score = Decimal('0')
        elif selected_ids == correct_ids:
            is_correct = True
            score = marks
        elif selected_ids.issubset(correct_ids):
            partial = Decimal(len(selected_ids)) / Decimal(len(correct_ids) or 1)
            is_correct = False
            score = (marks * partial).quantize(Decimal('0.01'))
        else:
            is_correct = False
            score = -negative

    elif qt == QuestionType.FILL_BLANK:
        if _is_textual_match(answer.text_answer, question.correct_answer_text):
            is_correct = True
            score = marks
        else:
            is_correct = False
            score = -negative if (answer.text_answer or '').strip() else Decimal('0')

    elif qt == QuestionType.CODING:
        results = answer.code_run_results or {}
        passed = int(results.get('passed', 0))
        total = int(results.get('total', 0))
        if total > 0:
            ratio = Decimal(passed) / Decimal(total)
            score = (marks * ratio).quantize(Decimal('0.01'))
            is_correct = passed == total

    answer.auto_score = score
    answer.is_correct = is_correct
    answer.save(update_fields=['auto_score', 'is_correct'])
    return score
