import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const features = [
  { icon: '🎯', title: 'AI Job Matching', desc: 'Resume scored against every job. Match %, missing skills, remote fit.' },
  { icon: '✍️', title: 'AI Cover Letters', desc: 'Personalized cover letters generated per role in seconds.' },
  { icon: '🤖', title: 'Auto Apply', desc: 'Playwright-powered application across LinkedIn, Indeed, Naukri & more.' },
  { icon: '📄', title: 'ATS Score', desc: 'Get your ATS rating with concrete improvement suggestions.' },
  { icon: '🔔', title: 'Smart Notifications', desc: 'Telegram + Email alerts when interviews or top matches arrive.' },
  { icon: '🛡️', title: 'Human-like Safety', desc: 'Random delays, typing simulation, anti-ban behavior built-in.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-950 dark:via-slate-900 dark:to-blue-950">
      <header className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white font-bold">A</div>
          <span className="font-bold text-lg">ApplyFlow AI</span>
        </div>
        <div className="flex gap-3">
          <Link to="/login" className="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-brand-600">Login</Link>
          <Link to="/register" className="btn-primary text-sm">Get Started</Link>
        </div>
      </header>

      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="badge bg-brand-100 text-brand-700 dark:bg-brand-900/50 dark:text-brand-200">
            ⚡ Powered by OpenAI & Gemini
          </span>
          <h1 className="mt-6 text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Apply to <span className="text-brand-600">100s of jobs</span><br />on autopilot.
          </h1>
          <p className="mt-6 text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
            AI-powered universal job auto-apply across LinkedIn, Indeed, Naukri, Internshala, Wellfound, and Foundit. Resume parsing, cover letter generation, ATS scoring — all in one place.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Link to="/register" className="btn-primary">Start applying free</Link>
            <Link to="/login" className="btn-secondary">I have an account</Link>
          </div>
        </motion.div>
      </section>

      <section className="max-w-6xl mx-auto px-6 pb-24">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="card p-6"
            >
              <div className="text-3xl">{f.icon}</div>
              <div className="mt-3 font-semibold text-lg">{f.title}</div>
              <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">{f.desc}</div>
            </motion.div>
          ))}
        </div>
      </section>

      <footer className="border-t border-slate-200 dark:border-slate-800 py-6 text-center text-sm text-slate-500">
        Built with FastAPI · React · Playwright · MongoDB · OpenAI / Gemini
      </footer>
    </div>
  )
}
