"""Databricks model serving client.

Wraps the `databricks-llama-4-maverick` (or any other) endpoint into a
single chat-style helper used across the AI assistant features.

Example:

    >>> from apps.ai_assistant.databricks_client import DatabricksLLMClient
    >>> client = DatabricksLLMClient()
    >>> client.chat([
    ...     {"role": "system", "content": "You are a code converter..."},
    ...     {"role": "user", "content": "select top 100 from employee"},
    ... ])
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Iterable, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class DatabricksResponse:
    content: str
    raw: dict
    latency_ms: int


class DatabricksLLMClient:
    """Thin wrapper around Databricks Model Serving REST API.

    Configuration is read from Django settings:
      - settings.DATABRICKS_URL
      - settings.DATABRICKS_TOKEN
      - settings.DATABRICKS_ENDPOINT
    """

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 60,
    ) -> None:
        self.url = (url or settings.DATABRICKS_URL or '').rstrip('/')
        self.token = token or settings.DATABRICKS_TOKEN
        self.endpoint = endpoint or settings.DATABRICKS_ENDPOINT
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.token and self.endpoint)

    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }

    def chat(
        self,
        messages: Iterable[dict],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> DatabricksResponse:
        if not self.is_configured:
            raise RuntimeError(
                'Databricks AI is not configured. Set DATABRICKS_URL, '
                'DATABRICKS_TOKEN and DATABRICKS_ENDPOINT in your environment.'
            )

        endpoint_url = (
            f'{self.url}/serving-endpoints/{self.endpoint}/invocations'
        )
        payload = {
            'messages': list(messages),
            'temperature': temperature,
            'max_tokens': max_tokens,
        }

        start = time.perf_counter()
        response = requests.post(
            endpoint_url, json=payload, headers=self._headers(), timeout=self.timeout,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        response.raise_for_status()

        data = response.json()
        try:
            content = data['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError) as exc:
            logger.error('Unexpected Databricks response: %s', data)
            raise RuntimeError(
                f'Unexpected response format from Databricks endpoint: {exc}'
            ) from exc
        return DatabricksResponse(content=content.strip(), raw=data, latency_ms=latency_ms)


# ----------------------------------------------------------------------------
# High level helpers used by the AI assistant views
# ----------------------------------------------------------------------------


def convert_sql_to_spark_sql(sql: str) -> DatabricksResponse:
    """Convert a piece of plain SQL into a Databricks Spark SQL `spark.sql('')` call."""
    client = DatabricksLLMClient()
    return client.chat([
        {
            'role': 'system',
            'content': (
                'You are a code converter. Only return converted Spark SQL '
                "code wrapped in spark.sql('''  '''). No explanation, no extra "
                'text, no markdown formatting.'
            ),
        },
        {
            'role': 'user',
            'content': (
                'Convert this SQL code into a Databricks notebook spark-sql '
                f"call written as spark.sql('''...'''). Code -> {sql}"
            ),
        },
    ])


def convert_sql_to_pyspark(sql: str) -> DatabricksResponse:
    client = DatabricksLLMClient()
    return client.chat([
        {
            'role': 'system',
            'content': (
                'You are a code converter. Convert SQL queries into idiomatic '
                'PySpark DataFrame API code. Only return the PySpark code, '
                'no explanations, no markdown.'
            ),
        },
        {'role': 'user', 'content': f'Convert this SQL into PySpark: {sql}'},
    ])


def convert_python_to_pyspark(python_code: str) -> DatabricksResponse:
    client = DatabricksLLMClient()
    return client.chat([
        {
            'role': 'system',
            'content': (
                'You are a code converter. Convert pandas / vanilla Python data '
                'manipulation code into equivalent PySpark code. Only return '
                'the PySpark code, no explanations.'
            ),
        },
        {'role': 'user', 'content': python_code},
    ])


def explain_code(code: str, language: str = 'python') -> DatabricksResponse:
    client = DatabricksLLMClient()
    return client.chat([
        {
            'role': 'system',
            'content': (
                'You are a senior teacher. Explain the given code clearly in '
                'simple paragraphs, suitable for a student. Use bullet points '
                'when listing steps.'
            ),
        },
        {'role': 'user', 'content': f'Explain this {language} code:\n\n{code}'},
    ])


def grade_descriptive_answer(question: str, answer: str, max_marks: float) -> DatabricksResponse:
    client = DatabricksLLMClient()
    return client.chat([
        {
            'role': 'system',
            'content': (
                'You are an exam evaluator. Given the question, the student '
                "answer and maximum marks, return JSON with keys 'suggested_marks' "
                "(number) and 'feedback' (string). Only return JSON, no markdown."
            ),
        },
        {
            'role': 'user',
            'content': (
                f'Question: {question}\n\nStudent Answer: {answer}\n\n'
                f'Max marks: {max_marks}'
            ),
        },
    ])
