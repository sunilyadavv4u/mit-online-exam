import { useState } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useFetch } from '../../hooks/useFetch';
import { subjectsApi } from '../../api/endpoints';
import Spinner from '../../components/common/Spinner';
import Modal from '../../components/common/Modal';

export default function TeacherSubjectsPage() {
  const { data, loading, setData } = useFetch(() => subjectsApi.list(), []);
  const list = data?.results || data || [];
  const [editing, setEditing] = useState(null);

  const refresh = async () => {
    const r = await subjectsApi.list();
    setData(r.data);
  };
  const remove = async (id) => {
    if (!confirm('Delete subject?')) return;
    try {
      await subjectsApi.remove(id);
      refresh();
      toast.success('Deleted');
    } catch {
      toast.error('Could not delete - subject may be in use.');
    }
  };

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Subjects</h1>
          <p className="text-slate-600">Subjects taught at Mewati Institute of Technology.</p>
        </div>
        <button className="btn-primary" onClick={() => setEditing({ name: '', code: '', icon: '', description: '', is_active: true })}>
          <Plus className="h-4 w-4" /> New subject
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {list.map((s) => (
          <div key={s.id} className="card-hover p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-2xl">{s.icon}</p>
                <h3 className="mt-1 font-semibold text-slate-900">{s.name}</h3>
                <p className="text-xs text-slate-500">{s.code}</p>
              </div>
              <div className="flex gap-1">
                <button onClick={() => setEditing(s)} className="btn-ghost p-2"><Edit2 className="h-4 w-4" /></button>
                <button onClick={() => remove(s.id)} className="btn-ghost p-2 text-red-600"><Trash2 className="h-4 w-4" /></button>
              </div>
            </div>
            <p className="mt-3 text-sm text-slate-600 line-clamp-2">{s.description}</p>
            <p className="mt-3 text-xs text-slate-500">{s.exam_count} exams</p>
          </div>
        ))}
      </div>

      {editing && (
        <SubjectModal
          subject={editing}
          onClose={() => setEditing(null)}
          onSaved={() => { setEditing(null); refresh(); }}
        />
      )}
    </div>
  );
}

function SubjectModal({ subject, onClose, onSaved }) {
  const [form, setForm] = useState(subject);
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      if (subject.id) await subjectsApi.update(subject.id, form);
      else await subjectsApi.create(form);
      toast.success('Saved');
      onSaved();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not save');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal open onClose={onClose} title={subject.id ? 'Edit subject' : 'New subject'}
      footer={(
        <>
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={save} disabled={saving}>Save</button>
        </>
      )}>
      <div className="space-y-3">
        <div>
          <label className="label">Name</label>
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </div>
        <div>
          <label className="label">Code</label>
          <input className="input" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
        </div>
        <div>
          <label className="label">Icon (emoji)</label>
          <input className="input" value={form.icon} onChange={(e) => setForm({ ...form, icon: e.target.value })} />
        </div>
        <div>
          <label className="label">Description</label>
          <textarea rows={3} className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={!!form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
          <span>Active</span>
        </label>
      </div>
    </Modal>
  );
}
