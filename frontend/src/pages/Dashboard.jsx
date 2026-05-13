import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../context/AuthContext.jsx'
import StatCard from '../components/StatCard.jsx'

export default function Dashboard() {
  const { user } = useAuth()
  const [analytics, setAnalytics] = useState(null)
  const [resume, setResume] = useState(null)
  const [recent, setRecent] = useState([])

  useEffect(() => {
    api.get('/jobs/analytics').then((r) => setAnalytics(r.data)).catch(() => {})
    api.get('/resume/active').then((r) => setResume(r.data)).catch(() => {})
    api.get('/jobs/applications', { params: { limit: 5 } }).then((r) => setRecent(r.data)).catch(() => {})
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.name?.split(' ')[0]} 👋</h1>
          <p className="text-slate-500 mt-1">Here&apos;s your job-hunt snapshot.</p>
        </div>
        <Link to="/jobs" className="btn-primary">Find new jobs</Link>
      </div>

      {!resume && (
        <div className="card p-6 border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-900/20">
          <div className="font-medium">No resume uploaded yet</div>
          <div className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Upload your resume to start matching with jobs and applying automatically.
          </div>
          <Link to="/resume" className="btn-primary mt-3 inline-flex">Upload resume</Link>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Applications" value={analytics?.total_applications ?? 0} icon="📨" />
        <StatCard label="Applied" value={analytics?.applied ?? 0} icon="✅" />
        <StatCard label="Interviews" value={analytics?.interview ?? 0} icon="🎙️" />
        <StatCard label="Pending" value={analytics?.pending ?? 0} icon="⏳" />
      </div>

      {resume && (
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-semibold text-lg">Active resume</div>
              <div className="text-sm text-slate-500">{resume.filename}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-500">ATS Score</div>
              <div className="text-3xl font-bold text-brand-600">{Math.round(resume.ats_score)}<span className="text-base text-slate-400">/100</span></div>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {resume.skills.slice(0, 12).map((s) => (
              <span key={s} className="badge bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">{s}</span>
            ))}
          </div>
        </div>
      )}

      <div className="card p-6">
        <div className="font-semibold text-lg mb-4">Recent applications</div>
        {recent.length === 0 ? (
          <div className="text-sm text-slate-500">No applications yet.</div>
        ) : (
          <div className="divide-y divide-slate-200 dark:divide-slate-800">
            {recent.map((a) => (
              <div key={a.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="font-medium">{a.job_title}</div>
                  <div className="text-sm text-slate-500">{a.company} · {a.platform}</div>
                </div>
                <span className={`badge ${
                  a.status === 'applied' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                  a.status === 'interview' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' :
                  a.status === 'rejected' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' :
                  'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                }`}>{a.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
