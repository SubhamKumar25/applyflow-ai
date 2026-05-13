import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext.jsx'

const hasGoogle = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID)

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const { login, loginWithGoogle } = useAuth()
  const nav = useNavigate()

  async function onSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await login(email, password)
      toast.success('Welcome back!')
      nav('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setSubmitting(false)
    }
  }

  async function onGoogleSuccess(credential) {
    if (!credential) return
    setSubmitting(true)
    try {
      await loginWithGoogle(credential)
      toast.success('Welcome back!')
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
        <h1 className="text-2xl font-bold">Welcome back</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Log in to continue your job hunt</p>

        {hasGoogle && (
          <div className="mt-6 flex flex-col items-center gap-3">
            <GoogleLogin
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
            <label className="block text-sm font-medium mb-1">Email</label>
            <input type="email" required className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input type="password" required className="input" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
          </div>
          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? 'Logging in…' : 'Log in'}
          </button>
        </form>
        <div className="mt-6 text-sm text-center text-slate-500">
          Don&apos;t have an account?{' '}
          <Link to="/register" className="text-brand-600 hover:underline font-medium">Sign up</Link>
        </div>
      </motion.div>
    </div>
  )
}
