"""Generate exam question papers from teacher prompts and class notes (Databricks LLM)."""
from __future__ import annotations

import json
import re
from typing import Any, Optional

from .databricks_client import DatabricksLLMClient, DatabricksResponse


def _strip_json_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith('```'):
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned)
    return cleaned.strip()


def parse_question_paper_json(content: str) -> dict[str, Any]:
    """Parse model output as JSON; fall back to markdown wrapper on failure."""
    try:
        return json.loads(_strip_json_fence(content))
    except (json.JSONDecodeError, TypeError):
        return {
            'format': 'markdown',
            'title': 'Generated Question Paper',
            'content': content.strip(),
        }


def generate_question_paper(
    *,
    prompt: str,
    teaching_notes: str,
    subject: str = '',
    total_marks: int = 100,
    duration_minutes: int = 60,
    num_questions: int = 10,
    difficulty: str = 'medium',
    question_types: Optional[list[str]] = None,
) -> DatabricksResponse:
    """Call Databricks Llama-4 Maverick to draft a structured question paper."""
    types = question_types or [
        'single_choice',
        'multiple_choice',
        'fill_blank',
        'descriptive',
        'coding',
    ]
    types_str = ', '.join(types)

    system = (
        'You are an expert teacher and exam paper setter for Mewati Institute of '
        'Technology. Create a complete, fair question paper ONLY from the teacher '
        'prompt and teaching notes provided. Do not invent topics not supported by '
        'the notes unless the prompt explicitly asks for review questions.\n\n'
        'Return ONLY valid JSON (no markdown fences, no commentary) matching this '
        'schema:\n'
        '{\n'
        '  "title": "string",\n'
        '  "instructions": "string",\n'
        '  "subject": "string",\n'
        '  "total_marks": number,\n'
        '  "duration_minutes": number,\n'
        '  "sections": [\n'
        '    {\n'
        '      "name": "string",\n'
        '      "questions": [\n'
        '        {\n'
        '          "number": 1,\n'
        '          "type": "single_choice|multiple_choice|true_false|fill_blank|descriptive|coding",\n'
        '          "text": "string",\n'
        '          "marks": number,\n'
        '          "difficulty": "easy|medium|hard",\n'
        '          "options": ["A", "B"],\n'
        '          "correct_answer": "string or list for multi",\n'
        '          "starter_code": "for coding only",\n'
        '          "expected_output": "for coding only"\n'
        '        }\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        '}'
    )

    user = (
        f'Teacher prompt / requirements:\n{prompt.strip()}\n\n'
        f'Teaching notes (source material):\n{teaching_notes.strip()}\n\n'
        f'Constraints:\n'
        f'- Subject: {subject or "General"}\n'
        f'- Target total marks: {total_marks}\n'
        f'- Exam duration (minutes): {duration_minutes}\n'
        f'- Approximate number of questions: {num_questions}\n'
        f'- Overall difficulty: {difficulty}\n'
        f'- Allowed question types: {types_str}\n'
        f'- Include clear section headings (e.g. Section A: MCQ, Section B: Descriptive).\n'
        f'- Each question must have marks that sum close to {total_marks}.\n'
    )

    client = DatabricksLLMClient(timeout=120)
    return client.chat(
        [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
