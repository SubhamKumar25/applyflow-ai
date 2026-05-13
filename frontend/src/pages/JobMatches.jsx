import { useState } from 'react'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import { api } from '../api.js'

const ALL_PLATFORMS = ['linkedin', 'indeed', 'naukri', 'internshala', 'wellfound', 'foundit']

export default function JobMatches() {
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('')
  const [platforms, setPlatforms] = useState(['linkedin', 'indeed'])
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)

  function togglePlatform(p) {
    setPlatforms((cur) => (cur.includes(p) ? cur.filter((x) => x !== p) : [...cur, p]))
  }

  async function onSearch(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const r = await api.post('/jobs/search', {
        keywords,
        location,
        platforms,
        remote_only: remoteOnly,
        limit: 20,
      })
      setMatches(r.data.sort((a, b) => b.match_score - a.match_score))
      toast.success(`Found ${r.data.length} matches`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Job Matches</h1>
        <p className="text-slate-500 mt-1">AI-ranked jobs across multiple platforms based on your resume.</p>
      </div>

      <form onSubmit={onSearch} className="card p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Keywords</label>
            <input className="input" value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder="Software engineer" required />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Location</label>
            <input className="input" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Bangalore, India" />
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
                className={`px-3 py-1.5 rounded-full text-sm font-medium capitalize transition-colors ${
                  platforms.includes(p)
                    ? 'bg-brand-600 text-white'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <label className="inline-flex items-center gap-2 text-sm">
            <input type="checkbox" checked={remoteOnly} onChange={(e) => setRemoteOnly(e.target.checked)} />
            Remote only
          </label>
          <button type="submit" disabled={loading || platforms.length === 0} className="btn-primary">
            {loading ? 'Searching…' : 'Search jobs'}
          </button>
        </div>
      </form>

      <div className="space-y-4">
        {matches.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.02 }}
            className="card p-6"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-semibold text-lg">{m.job.title}</h3>
                  <span className="badge bg-slate-100 dark:bg-slate-800 capitalize">{m.job.platform}</span>
                  {m.job.is_remote && <span className="badge bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">Remote</span>}
                  {m.job.easy_apply && <span className="badge bg-brand-100 text-brand-700 dark:bg-brand-900/30 dark:text-brand-200">Easy Apply</span>}
                </div>
                <div className="text-slate-600 dark:text-slate-400 mt-1">{m.job.company} · {m.job.location}</div>
                {m.relevance_reasons.length > 0 && (
                  <div className="mt-3 text-sm text-slate-600 dark:text-slate-400">
                    <strong>Why a match:</strong> {m.relevance_reasons.join(' · ')}
                  </div>
                )}
                <div className="mt-3 flex flex-wrap gap-1">
                  {m.matching_skills.slice(0, 8).map((s) => (
                    <span key={s} className="badge bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 text-xs">{s}</span>
                  ))}
                  {m.missing_skills.slice(0, 5).map((s) => (
                    <span key={s} className="badge bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 text-xs">missing: {s}</span>
                  ))}
                </div>
              </div>
              <div className="text-right shrink-0">
                <div className="text-xs text-slate-500">Match</div>
                <div className={`text-4xl font-bold ${
                  m.match_score >= 75 ? 'text-green-600' :
                  m.match_score >= 50 ? 'text-amber-600' : 'text-slate-500'
                }`}>{Math.round(m.match_score)}<span className="text-base text-slate-400">%</span></div>
                <a href={m.job.url} target="_blank" rel="noreferrer" className="btn-primary text-sm mt-3 inline-flex">View</a>
              </div>
            </div>
          </motion.div>
        ))}
        {matches.length === 0 && !loading && (
          <div className="card p-12 text-center text-slate-500">No matches yet — run a search above.</div>
        )}
      </div>
    </div>
  )
}
