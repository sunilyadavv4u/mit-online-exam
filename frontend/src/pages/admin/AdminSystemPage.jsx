export default function AdminSystemPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">System</h1>
        <p className="text-slate-600">High level information about the deployment.</p>
      </div>

      <div className="card p-6 grid gap-3 md:grid-cols-2">
        <Info label="Backend" value="Django + DRF + SimpleJWT" />
        <Info label="Async tasks" value="Celery + Redis" />
        <Info label="Database" value="SQLite (dev) / PostgreSQL (prod)" />
        <Info label="AI" value="Databricks Llama 4 Maverick" />
        <Info label="Frontend" value="React + Vite + Tailwind" />
        <Info label="Storage" value="Local / Cloudinary (toggleable)" />
      </div>

      <div className="card p-6">
        <h2 className="font-semibold text-slate-900 mb-2">Useful links</h2>
        <ul className="text-sm space-y-1 text-primary-600">
          <li><a href="/admin/" target="_blank" rel="noreferrer">Django Admin</a></li>
          <li><a href="/api/docs/" target="_blank" rel="noreferrer">Swagger / API docs</a></li>
          <li><a href="/api/redoc/" target="_blank" rel="noreferrer">Redoc / API reference</a></li>
          <li><a href="/api/schema/" target="_blank" rel="noreferrer">OpenAPI Schema (JSON)</a></li>
        </ul>
      </div>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-50 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-900">{value}</p>
    </div>
  );
}
