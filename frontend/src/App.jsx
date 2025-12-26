import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Home from './pages/Home.jsx'
import NewsDetail from './pages/NewsDetail.jsx'
import Login from './pages/Login.jsx'
import { apiFetch, clearTokens, getToken } from './api/client.js'
import './styles/app.css'

export default function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [authError, setAuthError] = useState('')

  const loadCurrentUser = async () => {
    if (!getToken()) {
      setCurrentUser(null)
      return
    }
    try {
      const data = await apiFetch('/auth/me')
      setCurrentUser(data)
      setAuthError('')
    } catch (error) {
      clearTokens()
      setCurrentUser(null)
      setAuthError(error.message)
    }
  }

  useEffect(() => {
    loadCurrentUser()
  }, [])

  const handleLogout = () => {
    clearTokens()
    setCurrentUser(null)
  }

  return (
    <BrowserRouter>
      <header className="header">
        <div className="nav">
          <Link to="/">Новости</Link>
        </div>
        <div className="auth">
          {currentUser ? (
            <>
              <div className="user">
                <span className="user-name">{currentUser.name}</span>
                <span className="badge">
                  {currentUser.is_admin ? 'Администратор' : currentUser.is_verified_author ? 'Автор' : 'Пользователь'}
                </span>
              </div>
              <button type="button" className="button ghost" onClick={handleLogout}>
                Выйти
              </button>
            </>
          ) : (
            <Link to="/login" className="button">
              Войти
            </Link>
          )}
        </div>
      </header>
      <main className="container">
        {authError && <p className="error">{authError}</p>}
        <Routes>
          <Route path="/" element={<Home currentUser={currentUser} />} />
          <Route path="/news/:id" element={<NewsDetail currentUser={currentUser} />} />
          <Route path="/login" element={<Login onAuth={loadCurrentUser} currentUser={currentUser} />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
