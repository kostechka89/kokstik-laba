import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client.js'

const heroImages = [
  'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=1200&q=80',
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=1200&q=80',
  'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=1200&q=80',
]

const moodImages = [
  {
    title: 'Лавандовый вайб',
    url: 'https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=900&q=80',
  },
  {
    title: 'Кофе и дедлайны',
    url: 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80',
  },
  {
    title: 'Пудровый закат',
    url: 'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=900&q=80',
  },
]

export default function Home({ currentUser }) {
  const [news, setNews] = useState([])
  const [error, setError] = useState('')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('{\n  "text": ""\n}')
  const [formError, setFormError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [feedbackName, setFeedbackName] = useState('')
  const [feedbackText, setFeedbackText] = useState('')
  const [feedbackMessage, setFeedbackMessage] = useState('')

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
      setContent('{\n  "text": ""\n}')
    } catch (err) {
      setFormError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const submitFeedback = (event) => {
    event.preventDefault()
    if (!feedbackName || !feedbackText) {
      setFeedbackMessage('Заполните имя и сообщение, пожалуйста.')
      return
    }
    setFeedbackMessage('Извините, не успел доделать и прикрутить капчу.')
    setFeedbackName('')
    setFeedbackText('')
  }

  const heroImage = heroImages[Math.floor(Date.now() / 1000) % heroImages.length]

  return (
    <section className="page">
      <div className="hero">
        <div className="hero-text">
          <p className="hero-tag">женский медиа-клуб</p>
          <h1>Сочные новости, мягкие тона и немного юмора</h1>
          <p className="hero-lead">
            Здесь новости появляются быстрее, чем ты успеваешь проверить, не убежал ли кот на кухню.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="button">
              Войти красиво
            </Link>
            <Link to="/register" className="button ghost">
              Создать профиль
            </Link>
          </div>
        </div>
        <div className="hero-image" style={{ backgroundImage: `url(${heroImage})` }} />
      </div>

      <div className="info-strip">
        <div>
          <h3>Живая лента</h3>
          <p>Свежие новости, удобные теги и авторы, которых хочется читать.</p>
        </div>
        <div>
          <h3>Гибкие роли</h3>
          <p>Автор, админ или читательница — всем найдется свое место.</p>
        </div>
        <div>
          <h3>Комментарии</h3>
          <p>Обсуждаем, вдохновляемся и поддерживаем друг друга.</p>
        </div>
      </div>

      {canCreateNews ? (
        <form onSubmit={submitNews} className="card form create-card">
          <div className="card-header">
            <h2>Создать новость</h2>
            <span className="pill">для авторов</span>
          </div>
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
          {formError && <p className="error">{formError}</p>}
          <button type="submit" className="button" disabled={isSubmitting}>
            {isSubmitting ? 'Публикуем...' : 'Опубликовать'}
          </button>
        </form>
      ) : (
        <div className="notice">
          {currentUser
            ? 'Для создания новости нужна верификация автора.'
            : 'Войдите в систему, чтобы оставлять комментарии и создавать новости.'}
        </div>
      )}

      {error && <p className="error">{error}</p>}

      <div className="news-grid">
        {news.map((item) => {
          const cover =
            item.cover ||
            item.cover_url ||
            item.image ||
            'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80'
          return (
            <article key={item.id} className="news-card">
              <div className="news-cover" style={{ backgroundImage: `url(${cover})` }} />
              <div className="news-body">
                <Link to={`/news/${item.id}`} className="title">
                  {item.title}
                </Link>
                <div className="meta">
                  {item.author ? `Автор: ${item.author.name}` : `Автор #${item.author_id}`}
                </div>
                <div className="meta">{new Date(item.published_at).toLocaleString()}</div>
              </div>
            </article>
          )
        })}
      </div>

      <section className="gallery">
        <h2>Настроение недели</h2>
        <div className="gallery-grid">
          {moodImages.map((item) => (
            <div key={item.title} className="gallery-card">
              <div className="gallery-image" style={{ backgroundImage: `url(${item.url})` }} />
              <h4>{item.title}</h4>
            </div>
          ))}
        </div>
      </section>

      <section id="feedback" className="card form feedback">
        <div className="card-header">
          <h2>Обратная связь</h2>
          <span className="pill">для создателя</span>
        </div>
        <input
          value={feedbackName}
          onChange={(e) => setFeedbackName(e.target.value)}
          placeholder="Ваше имя"
        />
        <textarea
          value={feedbackText}
          onChange={(e) => setFeedbackText(e.target.value)}
          placeholder="Сообщение"
        />
        <button type="button" className="button" onClick={submitFeedback}>
          Отправить
        </button>
        {feedbackMessage && <p className="notice">{feedbackMessage}</p>}
      </section>
    </section>
  )
}
