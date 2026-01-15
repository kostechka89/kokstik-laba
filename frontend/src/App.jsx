import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import Home from './pages/Home.jsx'
import NewsDetail from './pages/NewsDetail.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import { apiFetch, clearTokens, getToken } from './api/client.js'
import './styles/app.css'

export default function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [authError, setAuthError] = useState('')
  const [feedbackText, setFeedbackText] = useState('')
  const [feedbackMessage, setFeedbackMessage] = useState('')

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

  const roleLabel = useMemo(() => {
    if (!currentUser) return ''
    if (currentUser.is_admin) return 'Администратор'
    if (currentUser.is_verified_author) return 'Автор'
    return 'Пользователь'
  }, [currentUser])

  const handleFeedbackSubmit = (event) => {
    event.preventDefault()
    setFeedbackMessage('Извините, не успел доделать и прикрутить капчу')
    setFeedbackText('')
  }

  return (
    <BrowserRouter>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            <span className="brand-mark">NW</span>
            <div>
              <p className="brand-title">NewsWave</p>
              <p className="brand-subtitle">Учебный портал</p>
            </div>
          </div>
          <nav className="side-nav">
            <Link to="/">Лента новостей</Link>
            <Link to="/login">Авторизация</Link>
            <Link to="/register">Регистрация</Link>
          </nav>
          <div className="side-card">
            <p className="side-card-title">Профиль</p>
            {currentUser ? (
              <div className="side-user">
                <span className="side-user-name">{currentUser.name}</span>
                <span className="badge">{roleLabel}</span>
                <button type="button" className="button ghost" onClick={handleLogout}>
                  Выйти
                </button>
              </div>
            ) : (
              <p className="side-user-hint">Войдите, чтобы управлять новостями и комментариями.</p>
            )}
          </div>
          <div className="side-card">
            <p className="side-card-title">Обратная связь</p>
            <form onSubmit={handleFeedbackSubmit} className="form">
              <textarea
                value={feedbackText}
                onChange={(event) => setFeedbackText(event.target.value)}
                placeholder="Ваше сообщение"
                required
              />
              <button type="submit" className="button">
                Отправить
              </button>
            </form>
            {feedbackMessage && <p className="notice slim">{feedbackMessage}</p>}
          </div>
        </aside>
        <div className="main-area">
          <header className="topbar">
            <div>
              <p className="topbar-title">Лабораторный портал новостей</p>
              <p className="topbar-subtitle">Новости, роли, комментарии и авторизация в одном месте</p>
            </div>
            <div className="topbar-actions">
              <Link to="/" className="button ghost">
                Главная
              </Link>
              {currentUser ? (
                <span className="chip">{currentUser.email}</span>
              ) : (
                <Link to="/login" className="button">
                  Войти
                </Link>
              )}
            </div>
          </header>
          <main className="content">
            {authError && <p className="error">{authError}</p>}
            <Routes>
              <Route path="/" element={<Home currentUser={currentUser} />} />
              <Route path="/news/:id" element={<NewsDetail currentUser={currentUser} />} />
              <Route path="/login" element={<Login onAuth={loadCurrentUser} currentUser={currentUser} />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </main>
          <footer className="footer">СДЕЛАНА РАБОТА ПРИХОДЬКО КОНСТАНТИНОМ</footer>
        </div>
      </div>
    </BrowserRouter>
  )
}
