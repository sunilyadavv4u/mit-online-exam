"""Sandboxed code runner used by coding question answers.

Currently supports a *very* simple Python runner using subprocess with a
short timeout. For SQL/PySpark we just record the code; teachers can grade
manually or use the AI assistant for partial automation.

This is intentionally conservative - in production you should replace this
with a Docker-based isolated runner or a service like Judge0.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestRunResult:
    passed: int
    total: int
    details: list[dict]


def run_python_against_tests(code: str, test_cases: list[dict],
                             timeout_seconds: int = 5) -> TestRunResult:
    """Execute student Python code against simple stdin/stdout test cases."""
    details: list[dict] = []
    passed = 0
    total = len(test_cases)

    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / 'student.py'
        script.write_text(code, encoding='utf-8')

        for tc in test_cases:
            input_data = tc.get('input_data', '') or ''
            expected = (tc.get('expected_output', '') or '').strip()
            try:
                proc = subprocess.run(
                    [sys.executable, str(script)],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
                actual = (proc.stdout or '').strip()
                ok = actual == expected and proc.returncode == 0
                if ok:
                    passed += 1
                details.append({
                    'input': input_data,
                    'expected': expected,
                    'actual': actual,
                    'stderr': (proc.stderr or '')[:1000],
                    'passed': ok,
                })
            except subprocess.TimeoutExpired:
                details.append({
                    'input': input_data,
                    'expected': expected,
                    'actual': '',
                    'stderr': 'Timeout exceeded',
                    'passed': False,
                })

    return TestRunResult(passed=passed, total=total, details=details)
