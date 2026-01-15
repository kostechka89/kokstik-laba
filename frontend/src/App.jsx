import { BrowserRouter, Routes, Route, Link, NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Home from './pages/Home.jsx'
import NewsDetail from './pages/NewsDetail.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import { apiFetch, clearTokens, getToken } from './api/client.js'
import heroMark from './assets/hero-mark.svg'
import './styles/app.css'

export default function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [authError, setAuthError] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)

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

  const closeMenu = () => setMenuOpen(false)

  return (
    <BrowserRouter>
      <div className="app-shell">
        <aside className={`sidebar ${menuOpen ? 'open' : ''}`}>
          <div className="brand">
            <img src={heroMark} alt="" />
            <div>
              <strong>Novus</strong>
              <span>Лента API</span>
            </div>
          </div>
          <nav className="sidebar-nav">
            <NavLink to="/" onClick={closeMenu}>
              Новости
            </NavLink>
            <NavLink to="/login" onClick={closeMenu}>
              Авторизация
            </NavLink>
            <NavLink to="/register" onClick={closeMenu}>
              Регистрация
            </NavLink>
          </nav>
          <div className="sidebar-card">
            <p>Панель автора</p>
            <p className="muted">Управляйте новостями и комментариями через права.</p>
          </div>
        </aside>
        <div className="main-area">
          <header className="topbar">
            <button type="button" className="menu-toggle" onClick={() => setMenuOpen((prev) => !prev)}>
              Меню
            </button>
            <Link to="/" className="topbar-title">
              Витрина новостей
            </Link>
            <div className="topbar-actions">
              {currentUser ? (
                <>
                  <div className="user-card">
                    <span className="user-name">{currentUser.name}</span>
                    <span className="badge">
                      {currentUser.is_admin
                        ? 'Администратор'
                        : currentUser.is_verified_author
                          ? 'Автор'
                          : 'Пользователь'}
                    </span>
                  </div>
                  <button type="button" className="button ghost" onClick={handleLogout}>
                    Выйти
                  </button>
                </>
              ) : (
                <div className="topbar-links">
                  <Link to="/login" className="button">
                    Войти
                  </Link>
                  <Link to="/register" className="button ghost">
                    Регистрация
                  </Link>
                </div>
              )}
            </div>
          </header>
          <main className="content">
            {authError && <p className="error banner">{authError}</p>}
            <Routes>
              <Route path="/" element={<Home currentUser={currentUser} />} />
              <Route path="/news/:id" element={<NewsDetail currentUser={currentUser} />} />
              <Route path="/login" element={<Login onAuth={loadCurrentUser} currentUser={currentUser} />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </main>
          <footer className="footer">
            <div className="footer-inner">
              <span>Сделана работа Приходько Константином</span>
              <span className="muted">Интерфейс подключен к API новостей и комментариев.</span>
            </div>
          </footer>
        </div>
      </div>
    </BrowserRouter>
  )
}
