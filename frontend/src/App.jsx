import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Home from './pages/Home.jsx'
import NewsDetail from './pages/NewsDetail.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import { apiFetch, clearTokens, getToken } from './api/client.js'
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

  const toggleMenu = () => {
    setMenuOpen((prev) => !prev)
  }

  return (
    <BrowserRouter>
      <header className="header">
        <div className="header-left">
          <Link to="/" className="brand" onClick={() => setMenuOpen(false)}>
            <span className="brand-icon">💗</span>
            <span>
              Gossip Garden
              <span className="brand-subtitle">новости с конфетти</span>
            </span>
          </Link>
          <button type="button" className="menu-toggle" onClick={toggleMenu}>
            {menuOpen ? 'Свернуть' : 'Меню'}
          </button>
        </div>
        <nav className={`nav ${menuOpen ? 'open' : ''}`}>
          <Link to="/" className="nav-link" onClick={() => setMenuOpen(false)}>
            Лента
          </Link>
          <Link to="/login" className="nav-link" onClick={() => setMenuOpen(false)}>
            Вход
          </Link>
          <Link to="/register" className="nav-link" onClick={() => setMenuOpen(false)}>
            Регистрация
          </Link>
          <a href="#feedback" className="nav-link" onClick={() => setMenuOpen(false)}>
            Обратная связь
          </a>
        </nav>
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
            <div className="auth-guest">Гостья, добро пожаловать ✨</div>
          )}
        </div>
      </header>
      <main className="container">
        {authError && <p className="error">{authError}</p>}
        <Routes>
          <Route path="/" element={<Home currentUser={currentUser} />} />
          <Route path="/news/:id" element={<NewsDetail currentUser={currentUser} />} />
          <Route path="/login" element={<Login onAuth={loadCurrentUser} currentUser={currentUser} />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="footer-inner">
          <div>
            <h3>Сделана работа Федотовой Анастасией</h3>
            <p>Новости бывают серьезными, но дизайн может быть мягким.</p>
          </div>
          <div className="footer-note">© 2024 Gossip Garden</div>
        </div>
      </footer>
    </BrowserRouter>
  )
}
