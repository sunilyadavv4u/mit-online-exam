"""MIT AI Chat — ChatGPT-style tutor powered by Databricks Llama-4 Maverick."""
from __future__ import annotations

from typing import Iterable

from .databricks_client import DatabricksLLMClient, DatabricksResponse

MAX_HISTORY_MESSAGES = 24
MAX_MESSAGE_CHARS = 12_000

ROLE_SYSTEM_PROMPTS = {
    'student': (
        'You are MIT AI Chat, a friendly study assistant for students at Mewati '
        'Institute of Technology. Help explain Python, SQL, PySpark, Azure data '
        'engineering, DSA, Java, and related topics clearly. Use examples and '
        'step-by-step reasoning. Do not provide direct answers to active exam '
        'questions if the student asks for cheating help — guide them to learn instead.'
    ),
    'teacher': (
        'You are MIT AI Chat, a teaching assistant for faculty at Mewati Institute '
        'of Technology. Help with lesson plans, question ideas, rubrics, explaining '
        'concepts to students, and data-engineering curriculum topics. Be practical '
        'and concise.'
    ),
    'super_admin': (
        'You are MIT AI Chat, an assistant for platform administrators at Mewati '
        'Institute of Technology. Help with exam platform workflows, user roles, '
        'best practices for online exams, and technical topics (Django, React, data '
        'engineering education). Stay professional and accurate.'
    ),
}


def _sanitize_messages(messages: Iterable[dict]) -> list[dict]:
    """Keep only user/assistant turns, trim size, cap count."""
    cleaned: list[dict] = []
    for msg in messages:
        role = (msg.get('role') or '').lower()
        if role not in {'user', 'assistant'}:
            continue
        content = str(msg.get('content') or '').strip()
        if not content:
            continue
        if len(content) > MAX_MESSAGE_CHARS:
            content = content[:MAX_MESSAGE_CHARS]
        cleaned.append({'role': role, 'content': content})
    return cleaned[-MAX_HISTORY_MESSAGES:]


def mit_chat_completion(*, messages: Iterable[dict], user_role: str) -> DatabricksResponse:
    """Send conversation to Llama-4 Maverick with a role-specific system prompt."""
    history = _sanitize_messages(messages)
    if not history or history[-1]['role'] != 'user':
        raise ValueError('The last message must be a non-empty user message.')

    system_prompt = ROLE_SYSTEM_PROMPTS.get(
        user_role,
        ROLE_SYSTEM_PROMPTS['student'],
    )
    payload = [{'role': 'system', 'content': system_prompt}, *history]

    client = DatabricksLLMClient(timeout=120)
    return client.chat(payload, temperature=0.7, max_tokens=2048)
