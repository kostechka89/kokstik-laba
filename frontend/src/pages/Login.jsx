import { useEffect, useState } from 'react'
import { apiFetch, setTokens } from '../api/client.js'
import authImage from '../assets/auth.svg'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Login({ onAuth, currentUser }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const url = new URL(window.location.href)
    const params = new URLSearchParams(url.search)
    const hashParams = new URLSearchParams(window.location.hash.replace('#', ''))
    const access = params.get('access_token') || hashParams.get('access_token')
    const refresh = params.get('refresh_token') || hashParams.get('refresh_token')
    if (access) {
      setTokens({ accessToken: access, refreshToken: refresh })
      setMessage('Успешно (GitHub)')
      onAuth?.()
      params.delete('access_token')
      params.delete('refresh_token')
      url.search = params.toString()
      window.history.replaceState({}, '', url.toString())
      if (window.location.hash) {
        window.history.replaceState({}, '', window.location.pathname)
      }
    }
  }, [onAuth])

  const onSubmit = async (event) => {
    event.preventDefault()
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      setTokens({ accessToken: data.access_token, refreshToken: data.refresh_token })
      setMessage('Успешно')
      onAuth?.()
    } catch (err) {
      setMessage(err.message)
    }
  }

  return (
    <section className="auth-page">
      <div className="card auth-card">
        <div>
          <p className="eyebrow">Доступ к системе</p>
          <h1>Авторизация</h1>
          <p className="muted">
            Вход открывает возможность оставлять комментарии и управлять новостями в зависимости от роли.
          </p>
          {currentUser && (
            <div className="notice">
              Вы уже вошли как <strong>{currentUser.name}</strong>. Можно выйти и войти под другим пользователем.
            </div>
          )}
          <form onSubmit={onSubmit} className="form">
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Пароль"
              required
            />
            <button type="submit" className="button">
              Войти
            </button>
          </form>
          <div className="oauth">
            <a className="button ghost" href={`${API_BASE}/auth/github`}>
              Войти через GitHub
            </a>
          </div>
          {message && <p className="meta">{message}</p>}
        </div>
        <img src={authImage} alt="Иллюстрация авторизации" />
      </div>
    </section>
  )
}
