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
    notifications: { telegram: false, email: false },
    saved_search: {
      keywords: '',
      location: '',
      platforms: ['linkedin', 'indeed'],
      remote_only: false,
      limit: 12,
    },
  })

  useEffect(() => {
    api.get('/automation/status').then((r) => {
      setStatus(r.data)
      const ss = r.data.saved_search || {}
      setForm({
        daily_apply_limit: r.data.daily_limit ?? 20,
        auto_mode: r.data.auto_mode ?? false,
        notifications: r.data.notifications ?? { telegram: false, email: false },
        saved_search: {
          keywords: ss.keywords || '',
          location: ss.location || '',
          platforms: ss.platforms?.length ? ss.platforms : (r.data.platforms ?? ['linkedin', 'indeed']),
          remote_only: !!ss.remote_only,
          limit: ss.limit ?? 12,
        },
      })
    }).catch(() => {})
  }, [])

  function togglePlatform(p) {
    setForm((f) => ({
      ...f,
      saved_search: {
        ...f.saved_search,
        platforms: f.saved_search.platforms.includes(p)
          ? f.saved_search.platforms.filter((x) => x !== p)
          : [...f.saved_search.platforms, p],
      },
    }))
  }

  async function save() {
    setSaving(true)
    try {
      await api.put('/automation/settings', {
        daily_apply_limit: form.daily_apply_limit,
        auto_mode: form.auto_mode,
        notifications: form.notifications,
        platforms: form.saved_search.platforms,
        saved_search: form.saved_search,
      })
      toast.success('Saved')
      const r = await api.get('/automation/status')
      setStatus(r.data)
    } catch {
      toast.error('Save failed')
    } finally {
      setSaving(false)
    }
  }

  async function start() {
    try {
      const r = await api.post('/automation/start')
      if (r.data.status === 'error') {
        toast.error(r.data.message)
        return
      }
      toast.success(r.data.message)
      const s = await api.get('/automation/status')
      setStatus(s.data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Start failed')
    }
  }

  async function stop() {
    try {
      const r = await api.post('/automation/stop')
      toast.success(r.data.message)
      const s = await api.get('/automation/status')
      setStatus(s.data)
    } catch {
      toast.error('Stop failed')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Automation Settings</h1>
        <p className="text-slate-500 mt-1">Configure saved search, daily limits, and optional auto-apply.</p>
      </div>

      <div className="card p-6 space-y-6">
        <div>
          <h2 className="font-semibold text-lg mb-3">Saved search (for Start / daily scheduler)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Keywords</label>
              <input
                className="input"
                value={form.saved_search.keywords}
                onChange={(e) => setForm((f) => ({ ...f, saved_search: { ...f.saved_search, keywords: e.target.value } }))}
                placeholder="Software engineer"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Location</label>
              <input
                className="input"
                value={form.saved_search.location}
                onChange={(e) => setForm((f) => ({ ...f, saved_search: { ...f.saved_search, location: e.target.value } }))}
                placeholder="Remote, India"
              />
            </div>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-4">
            <label className="inline-flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.saved_search.remote_only}
                onChange={(e) => setForm((f) => ({ ...f, saved_search: { ...f.saved_search, remote_only: e.target.checked } }))}
              />
              Remote only
            </label>
            <div className="flex items-center gap-2">
              <label className="text-sm">Max listings / platform</label>
              <input
                type="number"
                min={5}
                max={30}
                className="input w-24"
                value={form.saved_search.limit}
                onChange={(e) => setForm((f) => ({ ...f, saved_search: { ...f.saved_search, limit: Number(e.target.value) || 12 } }))}
              />
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Platforms (saved search)</label>
          <div className="flex flex-wrap gap-2">
            {ALL_PLATFORMS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => togglePlatform(p)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium capitalize ${
                  form.saved_search.platforms.includes(p)
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
          <label className="block text-sm font-medium mb-2">Daily apply limit</label>
          <input
            type="number"
            min={1}
            max={100}
            className="input max-w-xs"
            value={form.daily_apply_limit}
            onChange={(e) => setForm((f) => ({ ...f, daily_apply_limit: Number(e.target.value) }))}
          />
          <p className="text-xs text-slate-500 mt-1">Caps how many successful applies count toward your day.</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Mode</label>
          <div className="space-y-2">
            <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-700 cursor-pointer">
              <input type="radio" checked={!form.auto_mode} onChange={() => setForm((f) => ({ ...f, auto_mode: false }))} className="mt-1" />
              <div>
                <div className="font-medium">Semi-Auto (recommended)</div>
                <div className="text-sm text-slate-500">Saved search runs; you review matches and apply manually from Job Matches.</div>
              </div>
            </label>
            <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-700 cursor-pointer">
              <input type="radio" checked={form.auto_mode} onChange={() => setForm((f) => ({ ...f, auto_mode: true }))} className="mt-1" />
              <div>
                <div className="font-medium">Full Auto</div>
                <div className="text-sm text-slate-500">Start / scheduler can auto-apply to top matches (Playwright). Use responsibly.</div>
              </div>
            </label>
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
              <span>Telegram (configure bot env on server)</span>
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

        <div className="flex flex-wrap gap-3 pt-2">
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
