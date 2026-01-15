import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client.js'
import heroImage from '../assets/hero.svg'
import cardOne from '../assets/card-one.svg'
import cardTwo from '../assets/card-two.svg'
import cardThree from '../assets/card-three.svg'

export default function Home({ currentUser }) {
  const [news, setNews] = useState([])
  const [error, setError] = useState('')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('{
  "text": ""
}')
  const [formError, setFormError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [feedbackName, setFeedbackName] = useState('')
  const [feedbackEmail, setFeedbackEmail] = useState('')
  const [feedbackText, setFeedbackText] = useState('')
  const [feedbackStatus, setFeedbackStatus] = useState('')

  const canCreateNews = useMemo(() => {
    return Boolean(currentUser && (currentUser.is_admin || currentUser.is_verified_author))
  }, [currentUser])

  const stats = useMemo(() => {
    const authorIds = new Set(news.map((item) => item.author_id))
    const todayCount = news.filter((item) => {
      if (!item.published_at) return false
      const date = new Date(item.published_at)
      const now = new Date()
      return date.toDateString() === now.toDateString()
    }).length
    return {
      total: news.length,
      authors: authorIds.size,
      today: todayCount,
    }
  }, [news])

  useEffect(() => {
    apiFetch('/news/')
      .then(setNews)
      .catch((err) => setError(err.message))
  }, [])

  const submitNews = async (event) => {
    event.preventDefault()
    setFormError('')
    setIsSubmitting(true)
    try {
      const payload = {
        title,
        content: JSON.parse(content),
      }
      const created = await apiFetch('/news/', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      setNews((prev) => [created, ...prev])
      setTitle('')
      setContent('{
  "text": ""
}')
    } catch (err) {
      setFormError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const submitFeedback = (event) => {
    event.preventDefault()
    setFeedbackStatus('Извините, не успел доделать и прикрутить капчу')
    setFeedbackName('')
    setFeedbackEmail('')
    setFeedbackText('')
  }

  const images = [cardOne, cardTwo, cardThree]

  return (
    <section className="home">
      <div className="hero">
        <div>
          <p className="eyebrow">Новостной центр</p>
          <h1>Главная лента событий и мнений</h1>
          <p className="lead">
            Платформа объединяет публикации, комментарии и роли пользователей. Авторизуйтесь,
            чтобы участвовать в обсуждениях и управлять новостями.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="button">
              Войти в кабинет
            </Link>
            <Link to="/register" className="button ghost">
              Создать аккаунт
            </Link>
          </div>
        </div>
        <img src={heroImage} alt="Иллюстрация новостной ленты" />
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Всего новостей</span>
          <strong>{stats.total}</strong>
        </div>
        <div className="stat-card">
          <span>Активных авторов</span>
          <strong>{stats.authors}</strong>
        </div>
        <div className="stat-card">
          <span>Сегодня опубликовано</span>
          <strong>{stats.today}</strong>
        </div>
      </div>

      {canCreateNews ? (
        <form onSubmit={submitNews} className="card form create-form">
          <div>
            <h2>Создать новость</h2>
            <p className="muted">Проверьте права автора перед публикацией.</p>
          </div>
          <div className="form-grid">
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Заголовок"
              required
            />
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder='{"text":"..."}'
            />
          </div>
          {formError && <p className="error">{formError}</p>}
          <button type="submit" className="button" disabled={isSubmitting}>
            {isSubmitting ? 'Публикуем...' : 'Опубликовать'}
          </button>
        </form>
      ) : (
        <div className="notice">
          {currentUser
            ? 'Для публикации новости нужна верификация автора.'
            : 'Войдите в систему, чтобы оставлять комментарии и создавать новости.'}
        </div>
      )}

      <div className="section-heading">
        <div>
          <h2>Свежие публикации</h2>
          <p className="muted">Последние новости из базы данных и ручек API.</p>
        </div>
        <span className="pill">Подключение к API активное</span>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="news-grid">
        {news.map((item, index) => (
          <article key={item.id} className="news-card">
            <div className="news-cover">
              <img src={images[index % images.length]} alt="Обложка новости" />
            </div>
            <div className="news-body">
              <div>
                <p className="news-meta">
                  {new Date(item.published_at).toLocaleString()} ·{' '}
                  {item.author ? item.author.name : `Автор #${item.author_id}`}
                </p>
                <h3>{item.title}</h3>
                <p className="muted">Новость содержит структурированный контент JSON.</p>
              </div>
              <Link to={`/news/${item.id}`} className="button ghost">
                Открыть
              </Link>
            </div>
          </article>
        ))}
      </div>

      <div className="split">
        <div className="card callout">
          <h2>Роли и доступ</h2>
          <ul>
            <li>Гости читают новости и комментарии.</li>
            <li>Пользователи могут оставлять комментарии.</li>
            <li>Авторизованные авторы публикуют новости.</li>
            <li>Администраторы управляют всем контентом.</li>
          </ul>
        </div>
        <div className="card feedback">
          <h2>Обратная связь</h2>
          <p className="muted">Сообщение уходит создателю проекта.</p>
          <form onSubmit={submitFeedback} className="form">
            <input
              value={feedbackName}
              onChange={(e) => setFeedbackName(e.target.value)}
              placeholder="Имя"
              required
            />
            <input
              type="email"
              value={feedbackEmail}
              onChange={(e) => setFeedbackEmail(e.target.value)}
              placeholder="Email"
              required
            />
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Сообщение"
              required
            />
            <button type="submit" className="button">
              Отправить
            </button>
            {feedbackStatus && <p className="notice muted">{feedbackStatus}</p>}
          </form>
        </div>
      </div>
    </section>
  )
}
