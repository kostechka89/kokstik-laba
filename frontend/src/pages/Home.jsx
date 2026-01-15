import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client.js'
import heroImage from '../assets/hero-news.svg'
import coverOne from '../assets/cover-1.svg'
import coverTwo from '../assets/cover-2.svg'
import coverThree from '../assets/cover-3.svg'

const coverOptions = [coverOne, coverTwo, coverThree]

export default function Home({ currentUser }) {
  const [news, setNews] = useState([])
  const [error, setError] = useState('')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('{
  "text": ""
}')
  const [formError, setFormError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const canCreateNews = useMemo(() => {
    return Boolean(currentUser && (currentUser.is_admin || currentUser.is_verified_author))
  }, [currentUser])

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

  return (
    <section className="page">
      <div className="hero">
        <div className="hero-content">
          <h1>Лента лабораторных новостей</h1>
          <p>
            Платформа показывает новости, роли авторов и работу с комментариями. Авторизуйтесь,
            чтобы управлять публикациями и оставлять обсуждения.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="button">
              Авторизоваться
            </Link>
            <Link to="/register" className="button ghost">
              Создать аккаунт
            </Link>
          </div>
        </div>
        <img src={heroImage} alt="Иллюстрация новостей" className="hero-image" />
      </div>

      <div className="stats">
        <div className="stat-card">
          <span className="stat-value">{news.length}</span>
          <span className="stat-label">Всего новостей</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{news.filter((item) => item.comments_count).length}</span>
          <span className="stat-label">Новости с комментариями</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{currentUser ? 'В сети' : 'Гость'}</span>
          <span className="stat-label">Статус пользователя</span>
        </div>
      </div>

      {canCreateNews ? (
        <form onSubmit={submitNews} className="card form create-panel">
          <div>
            <h2>Создать новость</h2>
            <p className="muted">Введите заголовок и JSON-контент.</p>
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
        <p className="notice">
          {currentUser
            ? 'Для создания новости нужна верификация автора.'
            : 'Войдите в систему, чтобы оставлять комментарии и создавать новости.'}
        </p>
      )}

      {error && <p className="error">{error}</p>}

      <div className="news-grid">
        {news.map((item, index) => (
          <article className="news-card" key={item.id}>
            <img
              src={coverOptions[index % coverOptions.length]}
              alt="Обложка новости"
              className="news-cover"
            />
            <div className="news-body">
              <Link to={`/news/${item.id}`} className="title">
                {item.title}
              </Link>
              <p className="meta">
                {item.author ? `Автор: ${item.author.name}` : `Автор #${item.author_id}`}
              </p>
              <p className="meta">{new Date(item.published_at).toLocaleString()}</p>
              <Link to={`/news/${item.id}`} className="button ghost">
                Читать
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
