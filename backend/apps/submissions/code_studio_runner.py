"""Code Studio runners: Python, Java, SQL (SQLite / optional SQL Server), PySpark."""
from __future__ import annotations

import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings

MAX_OUTPUT_CHARS = 50_000
JAVA_TIMEOUT = 25
SQL_TIMEOUT = 20
PYSPARK_TIMEOUT = 120


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + '\n... (output truncated)'


def run_python_freeform(code: str, stdin: str = '', timeout_seconds: int = 15) -> dict:
    """Run Python code and return stdout/stderr."""
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / 'playground.py'
        script.write_text(code, encoding='utf-8')
        try:
            proc = subprocess.run(
                [sys.executable, str(script)],
                input=stdin or '',
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return {
                'stdout': _truncate(proc.stdout or ''),
                'stderr': _truncate(proc.stderr or ''),
                'exit_code': proc.returncode,
                'timed_out': False,
                'runtime': 'python',
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': f'Execution timed out after {timeout_seconds}s.',
                'exit_code': -1,
                'timed_out': True,
                'runtime': 'python',
            }


def _java_public_class(code: str) -> str | None:
    match = re.search(r'public\s+class\s+(\w+)', code)
    return match.group(1) if match else None


def run_java_freeform(code: str, stdin: str = '', timeout_seconds: int = JAVA_TIMEOUT) -> dict:
    """Compile and run Java if JDK (javac/java) is on PATH."""
    if not shutil.which('javac') or not shutil.which('java'):
        return {
            'stdout': '',
            'stderr': (
                'Java JDK not found on the server. Install JDK 17+ and ensure '
                'javac and java are on the system PATH, then restart Django.'
            ),
            'exit_code': -1,
            'timed_out': False,
            'runtime': 'java',
        }

    class_name = _java_public_class(code)
    if not class_name:
        code = (
            'public class Main {\n'
            '  public static void main(String[] args) throws Exception {\n'
            + '\n'.join(f'    {line}' for line in code.splitlines())
            + '\n  }\n}\n'
        )
        class_name = 'Main'

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        src = root / f'{class_name}.java'
        src.write_text(code, encoding='utf-8')
        try:
            compile_proc = subprocess.run(
                ['javac', str(src)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=str(root),
            )
            if compile_proc.returncode != 0:
                return {
                    'stdout': _truncate(compile_proc.stdout or ''),
                    'stderr': _truncate(compile_proc.stderr or 'Compilation failed.'),
                    'exit_code': compile_proc.returncode,
                    'timed_out': False,
                    'runtime': 'java',
                }
            run_proc = subprocess.run(
                ['java', '-cp', str(root), class_name],
                input=stdin or '',
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=str(root),
            )
            return {
                'stdout': _truncate(run_proc.stdout or ''),
                'stderr': _truncate(run_proc.stderr or ''),
                'exit_code': run_proc.returncode,
                'timed_out': False,
                'runtime': 'java',
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': f'Java execution timed out after {timeout_seconds}s.',
                'exit_code': -1,
                'timed_out': True,
                'runtime': 'java',
            }


def _split_sql_batches(sql: str) -> list[str]:
    batches: list[str] = []
    current: list[str] = []
    for line in sql.splitlines():
        if re.match(r'^\s*GO\s*$', line, re.IGNORECASE):
            chunk = '\n'.join(current).strip()
            if chunk:
                batches.append(chunk)
            current = []
        else:
            current.append(line)
    chunk = '\n'.join(current).strip()
    if chunk:
        batches.append(chunk)
    return batches or [sql.strip()]


def _tsql_to_sqlite(stmt: str) -> str:
    s = stmt.strip().rstrip(';')
    if not s:
        return s
    s = re.sub(r'--[^\n]*', '', s)
    s = re.sub(r'\bdbo\.', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\[([^\]]+)\]', r'\1', s)
    top_match = re.search(
        r'^(\s*SELECT\s+)TOP\s+(\d+)\s+(.*)$',
        s,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if top_match:
        s = f'{top_match.group(1)}{top_match.group(3)} LIMIT {top_match.group(2)}'
    return s


def _seed_sqlite_demo(conn: sqlite3.Connection) -> None:
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS Employee (
            EmployeeID INTEGER PRIMARY KEY,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Department TEXT
        )'''
    )
    row = conn.execute('SELECT COUNT(*) FROM Employee').fetchone()
    if row and row[0] == 0:
        conn.executemany(
            'INSERT INTO Employee (EmployeeID, FirstName, LastName, Department) VALUES (?,?,?,?)',
            [
                (1, 'Ada', 'Lovelace', 'Engineering'),
                (2, 'Grace', 'Hopper', 'Engineering'),
                (3, 'Alan', 'Turing', 'Research'),
                (4, 'Katherine', 'Johnson', 'Mathematics'),
            ],
        )
        conn.commit()


def _run_sqlite(sql: str) -> dict:
    """Run SQL against in-memory SQLite (T-SQL-ish syntax normalized)."""
    forbidden = re.compile(
        r'\b(ATTACH|DETACH|PRAGMA\s+key|readfile|writefile)\b',
        re.IGNORECASE,
    )
    lines_out: list[str] = []
    errors: list[str] = []

    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    try:
        _seed_sqlite_demo(conn)
        for batch in _split_sql_batches(sql):
            for raw_stmt in batch.split(';'):
                stmt = _tsql_to_sqlite(raw_stmt)
                if not stmt:
                    continue
                if forbidden.search(stmt):
                    errors.append(f'Blocked for safety: {stmt[:80]}...')
                    continue
                try:
                    cur = conn.execute(stmt)
                    if stmt.strip().upper().startswith('SELECT') or stmt.strip().upper().startswith('WITH'):
                        rows = cur.fetchall()
                        if not rows:
                            lines_out.append('(0 rows)')
                        else:
                            cols = rows[0].keys()
                            lines_out.append(' | '.join(cols))
                            lines_out.append('-' * min(60, len(cols) * 12))
                            for row in rows[:100]:
                                lines_out.append(' | '.join(str(row[c]) for c in cols))
                            if len(rows) > 100:
                                lines_out.append(f'... {len(rows) - 100} more rows')
                    else:
                        conn.commit()
                        lines_out.append(f'OK ({cur.rowcount} row(s) affected)')
                except sqlite3.Error as exc:
                    errors.append(f'Error: {exc}\n  Statement: {stmt[:200]}')
    finally:
        conn.close()

    stdout = '\n'.join(lines_out)
    stderr = '\n'.join(errors)
    note = (
        'Ran on in-memory SQLite (demo Employee table seeded). '
        'TOP/dbo. normalized for practice. For real SQL Server, set '
        'CODE_STUDIO_MSSQL_CONNECTION in backend .env.'
    )
    return {
        'stdout': _truncate((note + '\n\n' + stdout).strip()),
        'stderr': _truncate(stderr),
        'exit_code': 0 if not errors else 1,
        'timed_out': False,
        'runtime': 'sqlite',
    }


def _run_sqlserver_odbc(sql: str, connection_string: str) -> dict | None:
    try:
        import pyodbc  # noqa: WPS433
    except ImportError:
        return None

    if not connection_string:
        return None

    lines_out: list[str] = []
    errors: list[str] = []
    try:
        with pyodbc.connect(connection_string, timeout=SQL_TIMEOUT) as conn:
            conn.autocommit = True
            cursor = conn.cursor()
            for batch in _split_sql_batches(sql):
                for raw_stmt in batch.split(';'):
                    stmt = raw_stmt.strip()
                    if not stmt or stmt.startswith('--'):
                        continue
                    upper = stmt.upper()
                    if not upper.startswith('SELECT') and not upper.startswith('WITH'):
                        errors.append('Only SELECT / WITH queries allowed on SQL Server connection.')
                        continue
                    try:
                        cursor.execute(stmt)
                        if cursor.description:
                            cols = [d[0] for d in cursor.description]
                            lines_out.append(' | '.join(cols))
                            rows = cursor.fetchmany(100)
                            for row in rows:
                                lines_out.append(' | '.join(str(v) for v in row))
                        else:
                            lines_out.append('OK')
                    except Exception as exc:
                        errors.append(str(exc))
    except Exception as exc:
        return {
            'stdout': '',
            'stderr': f'SQL Server connection failed: {exc}',
            'exit_code': 1,
            'timed_out': False,
            'runtime': 'sqlserver',
        }

    return {
        'stdout': _truncate('\n'.join(lines_out)),
        'stderr': _truncate('\n'.join(errors)),
        'exit_code': 0 if not errors else 1,
        'timed_out': False,
        'runtime': 'sqlserver',
    }


def run_sql_freeform(code: str) -> dict:
    """SQL Server playground: try ODBC if configured, else SQLite practice engine."""
    conn_str = getattr(settings, 'CODE_STUDIO_MSSQL_CONNECTION', '') or ''
    if conn_str:
        odbc_result = _run_sqlserver_odbc(code, conn_str)
        if odbc_result is not None:
            return odbc_result
    return _run_sqlite(code)


def run_pyspark_freeform(code: str, timeout_seconds: int = PYSPARK_TIMEOUT) -> dict:
    """Run PySpark script via Python (requires pyspark + Java on server)."""
    try:
        import pyspark  # noqa: F401, WPS433
    except ImportError:
        return {
            'stdout': '',
            'stderr': (
                'PySpark is not installed on the server. Run: pip install pyspark\n'
                'Also install Java 11+ (JDK) and set JAVA_HOME. Then restart Django.'
            ),
            'exit_code': -1,
            'timed_out': False,
            'runtime': 'pyspark',
        }

    if 'SparkSession' not in code:
        code = (
            'from pyspark.sql import SparkSession\n'
            'spark = SparkSession.builder.master("local[*]").appName("MIT_Code_Studio").getOrCreate()\n'
            'sc = spark.sparkContext\n'
            'sc.setLogLevel("WARN")\n'
            f'{code}\n'
            'spark.stop()\n'
        )

    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / 'playground_pyspark.py'
        script.write_text(code, encoding='utf-8')
        env = os.environ.copy()
        env['PYSPARK_PYTHON'] = sys.executable
        env['PYSPARK_DRIVER_PYTHON'] = sys.executable
        env.setdefault('SPARK_LOCAL_IP', '127.0.0.1')
        try:
            proc = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=env,
            )
            return {
                'stdout': _truncate(proc.stdout or ''),
                'stderr': _truncate(proc.stderr or ''),
                'exit_code': proc.returncode,
                'timed_out': False,
                'runtime': 'pyspark',
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': f'PySpark timed out after {timeout_seconds}s. First run may take 1–2 minutes.',
                'exit_code': -1,
                'timed_out': True,
                'runtime': 'pyspark',
            }
