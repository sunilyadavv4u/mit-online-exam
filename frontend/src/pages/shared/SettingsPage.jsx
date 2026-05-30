import { useState } from 'react';
import toast from 'react-hot-toast';
import { Lock } from 'lucide-react';
import { authApi } from '../../api/endpoints';

export default function SettingsPage() {
  const [oldPwd, setOldPwd] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [confirmPwd, setConfirmPwd] = useState('');
  const [saving, setSaving] = useState(false);

  const change = async (e) => {
    e.preventDefault();
    if (newPwd !== confirmPwd) return toast.error('Passwords do not match');
    setSaving(true);
    try {
      await authApi.changePassword(oldPwd, newPwd);
      toast.success('Password updated');
      setOldPwd(''); setNewPwd(''); setConfirmPwd('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not change password');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-md space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-600">Update your password.</p>
      </div>
      <form onSubmit={change} className="card p-6 space-y-4">
        <div>
          <label className="label">Old password</label>
          <input type="password" className="input" value={oldPwd} onChange={(e) => setOldPwd(e.target.value)} required />
        </div>
        <div>
          <label className="label">New password</label>
          <input type="password" className="input" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} required minLength={8} />
        </div>
        <div>
          <label className="label">Confirm</label>
          <input type="password" className="input" value={confirmPwd} onChange={(e) => setConfirmPwd(e.target.value)} required />
        </div>
        <button className="btn-primary w-full" disabled={saving}>
          <Lock className="h-4 w-4" /> {saving ? 'Saving...' : 'Update password'}
        </button>
      </form>
    </div>
  );
}
