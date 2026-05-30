import { useState } from 'react';
import toast from 'react-hot-toast';
import { Save } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { authApi } from '../../api/endpoints';

export default function ProfilePage() {
  const { user, setUser } = useAuth();
  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone: user?.phone || '',
    bio: user?.bio || '',
  });
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      const r = await authApi.updateMe(form);
      setUser(r.data);
      toast.success('Profile updated');
    } catch {
      toast.error('Could not save');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Profile</h1>
        <p className="text-slate-600">Update your basic information.</p>
      </div>
      <div className="card p-6 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">First name</label>
            <input className="input" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          </div>
          <div>
            <label className="label">Last name</label>
            <input className="input" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          </div>
        </div>
        <div>
          <label className="label">Email</label>
          <input className="input bg-slate-50" value={user?.email} disabled />
        </div>
        <div>
          <label className="label">Phone</label>
          <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        </div>
        <div>
          <label className="label">Bio</label>
          <textarea rows={3} className="input" value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} />
        </div>
        <button className="btn-primary" onClick={save} disabled={saving}>
          <Save className="h-4 w-4" /> Save profile
        </button>
      </div>
    </div>
  );
}
