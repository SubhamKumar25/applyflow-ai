import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('applyflow_token')
    if (!token) {
      setLoading(false)
      return
    }
    api
      .get('/auth/me')
      .then((r) => setUser(r.data))
      .catch(() => localStorage.removeItem('applyflow_token'))
      .finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    const r = await api.post('/auth/login', { email, password })
    localStorage.setItem('applyflow_token', r.data.access_token)
    setUser(r.data.user)
    return r.data.user
  }

  async function register(name, email, password) {
    const r = await api.post('/auth/register', { name, email, password })
    localStorage.setItem('applyflow_token', r.data.access_token)
    setUser(r.data.user)
    return r.data.user
  }

  function logout() {
    localStorage.removeItem('applyflow_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
