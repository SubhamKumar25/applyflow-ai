import { useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import { api } from '../api.js'

export default function ResumeAnalyzer() {
  const [resume, setResume] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef(null)

  useEffect(() => { fetchActive() }, [])

  async function fetchActive() {
    try {
      const r = await api.get('/resume/active')
      setResume(r.data)
    } catch { /* none yet */ }
  }

  async function onUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const r = await api.post('/resume/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResume(r.data)
      toast.success('Resume analyzed!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Resume Analyzer</h1>
        <p className="text-slate-500 mt-1">Upload your resume (PDF or DOCX). AI will extract skills, score it, and suggest improvements.</p>
      </div>

      <div className="card p-8">
        <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-10 text-center">
          <div className="text-5xl">📄</div>
          <div className="mt-4 font-medium">Drop your resume or click to browse</div>
          <div className="text-sm text-slate-500 mt-1">PDF or DOCX, max 10 MB</div>
          <input ref={fileRef} type="file" accept=".pdf,.docx" onChange={onUpload} className="hidden" />
          <button
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            className="btn-primary mt-5"
          >
            {uploading ? 'Analyzing…' : 'Choose file'}
          </button>
        </div>
      </div>

      {resume && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold text-lg">{resume.filename}</div>
                <div className="text-sm text-slate-500">Uploaded {new Date(resume.uploaded_at).toLocaleString()}</div>
              </div>
              <div className="text-right">
                <div className="text-xs text-slate-500">ATS Score</div>
                <div className={`text-4xl font-bold ${
                  resume.ats_score >= 75 ? 'text-green-600' :
                  resume.ats_score >= 50 ? 'text-amber-600' : 'text-red-600'
                }`}>{Math.round(resume.ats_score)}<span className="text-base text-slate-400">/100</span></div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card p-6">
              <div className="font-semibold mb-3">Extracted skills ({resume.skills.length})</div>
              <div className="flex flex-wrap gap-2">
                {resume.skills.map((s) => (
                  <span key={s} className="badge bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-200">{s}</span>
                ))}
              </div>
            </div>
            <div className="card p-6">
              <div className="font-semibold mb-3">AI Suggestions</div>
              <ul className="space-y-2 text-sm">
                {resume.suggestions.map((s, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-brand-600">→</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {resume.experience.length > 0 && (
            <div className="card p-6">
              <div className="font-semibold mb-3">Experience</div>
              <div className="space-y-3">
                {resume.experience.map((e, i) => (
                  <div key={i} className="border-l-2 border-brand-500 pl-4">
                    <div className="font-medium">{e.role}</div>
                    <div className="text-sm text-slate-500">{e.company} · {e.duration}</div>
                    {e.description && <div className="text-sm mt-1 text-slate-600 dark:text-slate-400">{e.description}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {resume.projects?.length > 0 && (
            <div className="card p-6">
              <div className="font-semibold mb-3">Projects</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {resume.projects.map((p, i) => (
                  <div key={i} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
                    <div className="font-medium">{p.name}</div>
                    <div className="text-sm text-slate-600 dark:text-slate-400 mt-1">{p.description}</div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {(p.tech || []).map((t) => (
                        <span key={t} className="badge bg-slate-200 dark:bg-slate-700 text-xs">{t}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}
