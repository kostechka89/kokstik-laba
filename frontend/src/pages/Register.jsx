import { useState } from 'react'
import { apiFetch } from '../api/client.js'
import registerVisual from '../assets/register-visual.svg'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isVerifiedAuthor, setIsVerifiedAuthor] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)
  const [message, setMessage] = useState('')

  const onSubmit = async (event) => {
    event.preventDefault()
    setMessage('')
    try {
      await apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          name,
          email: email.trim().toLowerCase(),
          password,
          is_verified_author: isVerifiedAuthor,
          is_admin: isAdmin,
        }),
      })
      setMessage('Пользователь создан. Теперь можно войти.')
      setName('')
      setEmail('')
      setPassword('')
      setIsVerifiedAuthor(false)
      setIsAdmin(false)
    } catch (err) {
      setMessage(err.message)
    }
  }

  return (
    <section className="page auth-page">
      <div className="auth-card">
        <div>
          <h1>Регистрация</h1>
          <p className="muted">Создайте учебную учетную запись и выберите роль для демонстрации прав.</p>
          <form onSubmit={onSubmit} className="form card">
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Имя" required />
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Пароль"
              required
            />
            <label className="checkbox">
              <input
                type="checkbox"
                checked={isVerifiedAuthor}
                onChange={(e) => setIsVerifiedAuthor(e.target.checked)}
              />
              Верифицированный автор
            </label>
            <label className="checkbox">
              <input type="checkbox" checked={isAdmin} onChange={(e) => setIsAdmin(e.target.checked)} />
              Администратор
            </label>
            <button type="submit" className="button">
              Зарегистрироваться
            </button>
            {message && <p className={message.includes('создан') ? 'success' : 'error'}>{message}</p>}
          </form>
        </div>
        <img src={registerVisual} alt="Регистрация" className="auth-visual" />
      </div>
    </section>
  )
}
