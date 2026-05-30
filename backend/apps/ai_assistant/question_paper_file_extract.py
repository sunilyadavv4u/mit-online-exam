"""Extract plain text from uploaded teaching-notes files (PDF, text, Python, etc.)."""
from __future__ import annotations

import os
from typing import Any

from django.core.exceptions import ValidationError

MAX_UPLOAD_BYTES = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = frozenset({
    '.pdf', '.txt', '.text', '.py', '.md', '.markdown', '.sql', '.json',
})


def _read_text_file(uploaded_file) -> str:
    raw = uploaded_file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValidationError(f'File is too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB).')
    for encoding in ('utf-8', 'utf-8-sig', 'latin-1'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValidationError('Could not decode file as text. Save as UTF-8 .txt or .py.')


def _read_pdf(uploaded_file) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValidationError(
            'PDF support is not installed on the server (missing pypdf). '
            'Use a .txt or .py file, or paste notes manually.'
        ) from exc

    uploaded_file.seek(0)
    reader = PdfReader(uploaded_file)
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text.strip())
    combined = '\n\n'.join(parts).strip()
    if not combined:
        raise ValidationError(
            'No readable text found in this PDF. It may be scanned images — '
            'try exporting as .txt or paste the notes manually.'
        )
    return combined


def extract_notes_from_upload(uploaded_file) -> tuple[str, dict[str, Any]]:
    """Return (text, metadata) for a teacher-uploaded notes file."""
    if not uploaded_file:
        raise ValidationError('No file was uploaded.')

    name = getattr(uploaded_file, 'name', '') or 'upload'
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ', '.join(sorted(ALLOWED_EXTENSIONS))
        raise ValidationError(f'Unsupported file type "{ext}". Allowed: {allowed}')

    size = getattr(uploaded_file, 'size', None)
    if size is None:
        uploaded_file.seek(0, os.SEEK_END)
        size = uploaded_file.tell()
        uploaded_file.seek(0)
    if size > MAX_UPLOAD_BYTES:
        raise ValidationError(f'File is too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB).')

    if ext == '.pdf':
        text = _read_pdf(uploaded_file)
    else:
        text = _read_text_file(uploaded_file)

    text = text.strip()
    if not text:
        raise ValidationError('The file appears to be empty.')

    return text, {
        'filename': name,
        'extension': ext,
        'char_count': len(text),
    }
