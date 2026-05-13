import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '🏠' },
  { to: '/resume', label: 'Resume', icon: '📄' },
  { to: '/jobs', label: 'Job Matches', icon: '🎯' },
  { to: '/automation', label: 'Automation', icon: '🤖' },
  { to: '/analytics', label: 'Analytics', icon: '📊' },
  { to: '/logs', label: 'Logs', icon: '📜' },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()
  const nav = useNavigate()

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-950">
      <aside className="w-64 shrink-0 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
        <div className="px-6 py-5 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white font-bold">A</div>
            <div>
              <div className="font-bold text-lg leading-none">ApplyFlow</div>
              <div className="text-xs text-slate-500">AI Auto Apply</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-50 dark:bg-brand-900/40 text-brand-700 dark:text-brand-200'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-slate-200 dark:border-slate-800 space-y-2">
          <button
            onClick={toggle}
            className="w-full text-left px-3 py-2 rounded-xl text-sm hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            {theme === 'dark' ? '☀️  Light mode' : '🌙 Dark mode'}
          </button>
          <div className="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800">
            <div className="text-xs text-slate-500">Signed in as</div>
            <div className="text-sm font-medium truncate">{user?.email}</div>
          </div>
          <button
            onClick={() => { logout(); nav('/login') }}
            className="w-full text-left px-3 py-2 rounded-xl text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
          >
            Log out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-8 animate-fade-in">{children}</div>
      </main>
    </div>
  )
}
