"""Code Studio runner tests."""
import pytest

from apps.submissions.code_studio_runner import run_python_freeform, run_sql_freeform


@pytest.mark.django_db
def test_sqlite_employee_query():
    result = run_sql_freeform(
        "SELECT TOP 2 FirstName, Department FROM dbo.Employee ORDER BY EmployeeID;"
    )
    assert result['exit_code'] == 0
    assert 'Ada' in result['stdout']
    assert 'sqlite' in result['runtime']


@pytest.mark.django_db
def test_python_hello():
    result = run_python_freeform('print("mit-ok")')
    assert result['exit_code'] == 0
    assert 'mit-ok' in result['stdout']
