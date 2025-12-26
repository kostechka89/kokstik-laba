import { useEffect, useState } from 'react'
import { apiFetch } from '../api/client.js'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    // GitHub OAuth callback: tokens are returned as query params
    const url = new URL(window.location.href)
    const access = url.searchParams.get('access_token')
    const refresh = url.searchParams.get('refresh_token')
    if (access) {
      localStorage.setItem('access_token', access)
      if (refresh) localStorage.setItem('refresh_token', refresh)
      setMessage('Успешно (GitHub)')
      // clean url
      url.searchParams.delete('access_token')
      url.searchParams.delete('refresh_token')
      window.history.replaceState({}, '', url.toString())
    }
  }, [])

  const onSubmit = async (event) => {
    event.preventDefault()
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      setMessage('Успешно')
    } catch (err) {
      setMessage(err.message)
    }
  }

  return (
    <section>
      <h1>Авторизация</h1>
      <form onSubmit={onSubmit} className="form">
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Пароль"
        />
        <button type="submit">Войти</button>
      </form>

      <div className="oauth">
        <a className="button" href={`${API_BASE}/auth/github`}>Войти через GitHub</a>
      </div>
      {message && <p className="meta">{message}</p>}
    </section>
  )
}
