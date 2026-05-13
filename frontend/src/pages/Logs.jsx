import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Logs() {
  const [apps, setApps] = useState([])
  const [filter, setFilter] = useState('')

  useEffect(() => {
    api.get('/jobs/applications', { params: { limit: 200 } }).then((r) => setApps(r.data)).catch(() => {})
  }, [])

  const filtered = apps.filter((a) => !filter || a.status === filter)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Application Logs</h1>
          <p className="text-slate-500 mt-1">Complete history of every job application attempt.</p>
        </div>
        <select className="input max-w-xs" value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="">All statuses</option>
          <option value="applied">Applied</option>
          <option value="pending">Pending</option>
          <option value="interview">Interview</option>
          <option value="rejected">Rejected</option>
          <option value="offered">Offered</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left bg-slate-50 dark:bg-slate-900 text-slate-500">
            <tr>
              <th className="px-6 py-3 font-medium">Date</th>
              <th className="px-6 py-3 font-medium">Job</th>
              <th className="px-6 py-3 font-medium">Company</th>
              <th className="px-6 py-3 font-medium">Platform</th>
              <th className="px-6 py-3 font-medium">Status</th>
              <th className="px-6 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
            {filtered.length === 0 ? (
              <tr><td colSpan="6" className="px-6 py-12 text-center text-slate-500">No logs yet.</td></tr>
            ) : filtered.map((a) => (
              <tr key={a.id} className="hover:bg-slate-50 dark:hover:bg-slate-900">
                <td className="px-6 py-3 text-slate-500">{new Date(a.applied_at).toLocaleString()}</td>
                <td className="px-6 py-3 font-medium">{a.job_title}</td>
                <td className="px-6 py-3">{a.company}</td>
                <td className="px-6 py-3 capitalize">{a.platform}</td>
                <td className="px-6 py-3">
                  <span className={`badge ${
                    a.status === 'applied' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                    a.status === 'interview' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' :
                    a.status === 'rejected' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' :
                    a.status === 'offered' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' :
                    'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                  }`}>{a.status}</span>
                </td>
                <td className="px-6 py-3">{a.url && <a href={a.url} target="_blank" rel="noreferrer" className="text-brand-600 hover:underline">Open ↗</a>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
