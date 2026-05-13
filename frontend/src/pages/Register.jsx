import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext.jsx'

const hasGoogle = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID)

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const { register, loginWithGoogle } = useAuth()
  const nav = useNavigate()

  async function onSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await register(name, email, password)
      toast.success('Account created!')
      nav('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setSubmitting(false)
    }
  }

  async function onGoogleSuccess(credential) {
    if (!credential) return
    setSubmitting(true)
    try {
      await loginWithGoogle(credential)
      toast.success('Signed in with Google!')
      nav('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Google sign-in failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-950 dark:via-slate-900 dark:to-blue-950 px-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md card p-8">
        <Link to="/" className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white font-bold">A</div>
          <span className="font-bold text-lg">ApplyFlow AI</span>
        </Link>
        <h1 className="text-2xl font-bold">Create account</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Start applying to jobs on autopilot</p>

        {hasGoogle && (
          <div className="mt-6 flex flex-col items-center gap-3">
            <GoogleLogin
              text="signup_with"
              onSuccess={(res) => onGoogleSuccess(res.credential)}
              onError={() => toast.error('Google sign-in was cancelled or failed')}
              useOneTap={false}
            />
            <div className="flex w-full items-center gap-3 text-xs text-slate-500">
              <span className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
              or with email
              <span className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
            </div>
          </div>
        )}

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <input required className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Subham Kumar" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input type="email" required className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input type="password" required minLength={6} className="input" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 6 characters" />
          </div>
          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>
        <div className="mt-6 text-sm text-center text-slate-500">
          Already have an account?{' '}
          <Link to="/login" className="text-brand-600 hover:underline font-medium">Log in</Link>
        </div>
      </motion.div>
    </div>
  )
}
