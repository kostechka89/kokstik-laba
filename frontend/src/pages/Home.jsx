import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client.js'

export default function Home({ currentUser }) {
  const [news, setNews] = useState([])
  const [error, setError] = useState('')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('{\n  "text": ""\n}')
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
      setContent('{\n  "text": ""\n}')
    } catch (err) {
      setFormError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section>
      <h1>Новости</h1>
      {canCreateNews ? (
        <form onSubmit={submitNews} className="card form">
          <h2>Создать новость</h2>
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
        <p className="notice">
          {currentUser
            ? 'Для создания новости нужна верификация автора.'
            : 'Войдите в систему, чтобы оставлять комментарии и создавать новости.'}
        </p>
      )}
      {error && <p className="error">{error}</p>}
      <ul className="list">
        {news.map((item) => (
          <li key={item.id}>
            <div className="list-row">
              <div>
                <Link to={`/news/${item.id}`} className="title">
                  {item.title}
                </Link>
                <div className="meta">
                  {item.author ? `Автор: ${item.author.name}` : `Автор #${item.author_id}`}
                </div>
              </div>
              <span className="meta">{new Date(item.published_at).toLocaleString()}</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
