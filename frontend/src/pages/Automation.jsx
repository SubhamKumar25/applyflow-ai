import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { api } from '../api.js'

const ALL_PLATFORMS = ['linkedin', 'indeed', 'naukri', 'internshala', 'wellfound', 'foundit']

export default function Automation() {
  const [status, setStatus] = useState(null)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    daily_apply_limit: 20,
    auto_mode: false,
    platforms: ['linkedin', 'indeed'],
    notifications: { telegram: false, email: false },
  })

  useEffect(() => {
    api.get('/automation/status').then((r) => {
      setStatus(r.data)
      setForm({
        daily_apply_limit: r.data.daily_limit ?? 20,
        auto_mode: r.data.auto_mode ?? false,
        platforms: r.data.platforms ?? ['linkedin', 'indeed'],
        notifications: { telegram: false, email: false },
      })
    }).catch(() => {})
  }, [])

  function togglePlatform(p) {
    setForm((f) => ({
      ...f,
      platforms: f.platforms.includes(p) ? f.platforms.filter((x) => x !== p) : [...f.platforms, p],
    }))
  }

  async function save() {
    setSaving(true)
    try {
      await api.put('/automation/settings', form)
      toast.success('Saved')
    } catch {
      toast.error('Save failed')
    } finally {
      setSaving(false)
    }
  }

  async function start() {
    const r = await api.post('/automation/start')
    toast.success(r.data.message)
  }
  async function stop() {
    const r = await api.post('/automation/stop')
    toast.success(r.data.message)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Automation Settings</h1>
        <p className="text-slate-500 mt-1">Configure how ApplyFlow searches and applies on your behalf.</p>
      </div>

      <div className="card p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">Daily apply limit</label>
          <input
            type="number"
            min={1}
            max={100}
            className="input max-w-xs"
            value={form.daily_apply_limit}
            onChange={(e) => setForm((f) => ({ ...f, daily_apply_limit: Number(e.target.value) }))}
          />
          <p className="text-xs text-slate-500 mt-1">Default: 20. Higher limits increase risk of platform throttling.</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Mode</label>
          <div className="space-y-2">
            <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-700 cursor-pointer">
              <input type="radio" checked={!form.auto_mode} onChange={() => setForm((f) => ({ ...f, auto_mode: false }))} className="mt-1" />
              <div>
                <div className="font-medium">Semi-Auto (recommended)</div>
                <div className="text-sm text-slate-500">Preview every application before submission.</div>
              </div>
            </label>
            <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-700 cursor-pointer">
              <input type="radio" checked={form.auto_mode} onChange={() => setForm((f) => ({ ...f, auto_mode: true }))} className="mt-1" />
              <div>
                <div className="font-medium">Full Auto</div>
                <div className="text-sm text-slate-500">Apply automatically up to your daily limit. Higher risk.</div>
              </div>
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Platforms</label>
          <div className="flex flex-wrap gap-2">
            {ALL_PLATFORMS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => togglePlatform(p)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium capitalize ${
                  form.platforms.includes(p)
                    ? 'bg-brand-600 text-white'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Notifications</label>
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.notifications.telegram}
                onChange={(e) => setForm((f) => ({ ...f, notifications: { ...f.notifications, telegram: e.target.checked } }))}
              />
              <span>Telegram</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.notifications.email}
                onChange={(e) => setForm((f) => ({ ...f, notifications: { ...f.notifications, email: e.target.checked } }))}
              />
              <span>Email</span>
            </label>
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button onClick={save} disabled={saving} className="btn-primary">{saving ? 'Saving…' : 'Save settings'}</button>
          <button onClick={start} className="btn-secondary">Start automation</button>
          <button onClick={stop} className="btn-secondary">Stop</button>
        </div>
      </div>

      {status && (
        <div className="card p-6">
          <div className="font-semibold mb-2">Current status</div>
          <pre className="text-sm bg-slate-50 dark:bg-slate-900 p-3 rounded-xl overflow-x-auto">{JSON.stringify(status, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
