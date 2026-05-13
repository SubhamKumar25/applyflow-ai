import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import { ThemeProvider } from './context/ThemeContext.jsx'
import './index.css'

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

const appTree = (
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <App />
          <Toaster
            position="top-right"
            toastOptions={{
              className: 'dark:bg-slate-800 dark:text-white',
            }}
          />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
)

ReactDOM.createRoot(document.getElementById('root')).render(
  googleClientId ? (
    <GoogleOAuthProvider clientId={googleClientId}>{appTree}</GoogleOAuthProvider>
  ) : (
    appTree
  ),
)
