export function formatDate(value) {
  if (!value) return '';
  try {
    return new Date(value).toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return value;
  }
}

export function formatDateOnly(value) {
  if (!value) return '';
  try {
    return new Date(value).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return value;
  }
}

export function timeRemaining(end) {
  const ms = new Date(end).getTime() - Date.now();
  if (Number.isNaN(ms) || ms < 0) return '00:00:00';
  const totalSeconds = Math.floor(ms / 1000);
  const h = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
  const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
  const s = String(totalSeconds % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => window.URL.revokeObjectURL(url), 0);
}

/**
 * Convert an axios error from a DRF backend into a readable string.
 * Handles {detail: '...'}, {field: ['msg1', 'msg2']}, plain strings, and arrays.
 */
export function formatApiError(error, fallback = 'Something went wrong') {
  const data = error?.response?.data;
  if (!data) return error?.message || fallback;

  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;

  if (typeof data === 'object') {
    const parts = [];
    for (const [key, value] of Object.entries(data)) {
      const messages = Array.isArray(value) ? value : [value];
      const text = messages.map((m) => (typeof m === 'string' ? m : JSON.stringify(m))).join(' ');
      parts.push(key === 'non_field_errors' ? text : `${key}: ${text}`);
    }
    if (parts.length) return parts.join('\n');
  }

  return fallback;
}
