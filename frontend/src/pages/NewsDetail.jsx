import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { apiFetch } from '../api/client.js'
import coverOne from '../assets/cover-1.svg'
import coverTwo from '../assets/cover-2.svg'
import coverThree from '../assets/cover-3.svg'

const coverOptions = [coverOne, coverTwo, coverThree]

const formatContent = (content) => {
  if (!content) return ''
  if (typeof content === 'string') return content
  if (content.text) return content.text
  return JSON.stringify(content, null, 2)
}

export default function NewsDetail({ currentUser }) {
  const { id } = useParams()
  const navigate = useNavigate()
  const [news, setNews] = useState(null)
  const [comments, setComments] = useState([])
  const [text, setText] = useState('')
  const [error, setError] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [editingCommentId, setEditingCommentId] = useState(null)
  const [editingCommentText, setEditingCommentText] = useState('')

  useEffect(() => {
    apiFetch(`/news/${id}`)
      .then((data) => {
        setNews(data)
        setTitle(data.title)
        setContent(JSON.stringify(data.content, null, 2))
      })
      .catch((err) => setError(err.message))
  }, [id])

  useEffect(() => {
    apiFetch(`/news/${id}/comments`)
      .then(setComments)
      .catch((err) => setError(err.message))
  }, [id])

  const canEditNews = useMemo(() => {
    if (!currentUser || !news) return false
    return currentUser.is_admin || currentUser.id === news.author_id
  }, [currentUser, news])

  const submitComment = async (event) => {
    event.preventDefault()
    try {
      const comment = await apiFetch('/comments/', {
        method: 'POST',
        body: JSON.stringify({ text, news_id: Number(id) }),
      })
      setComments((prev) => [...prev, comment])
      setText('')
    } catch (err) {
      setError(err.message)
    }
  }

  const submitNewsUpdate = async (event) => {
    event.preventDefault()
    try {
      const updated = await apiFetch(`/news/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          title,
          content: JSON.parse(content),
        }),
      })
      setNews(updated)
      setIsEditing(false)
    } catch (err) {
      setError(err.message)
    }
  }

  const deleteNews = async () => {
    if (!window.confirm('Удалить новость?')) return
    try {
      await apiFetch(`/news/${id}`, { method: 'DELETE' })
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  const startEditComment = (comment) => {
    setEditingCommentId(comment.id)
    setEditingCommentText(comment.text)
  }

  const submitCommentUpdate = async (commentId) => {
    try {
      const updated = await apiFetch(`/comments/${commentId}`, {
        method: 'PATCH',
        body: JSON.stringify({ text: editingCommentText }),
      })
      setComments((prev) => prev.map((item) => (item.id === commentId ? updated : item)))
      setEditingCommentId(null)
      setEditingCommentText('')
    } catch (err) {
      setError(err.message)
    }
  }

  const deleteComment = async (commentId) => {
    if (!window.confirm('Удалить комментарий?')) return
    try {
      await apiFetch(`/comments/${commentId}`, { method: 'DELETE' })
      setComments((prev) => prev.filter((item) => item.id !== commentId))
    } catch (err) {
      setError(err.message)
    }
  }

  if (!news) {
    return <p>Загрузка...</p>
  }

  return (
    <section className="page">
      <Link to="/" className="button ghost back-link">
        Назад к ленте
      </Link>
      <div className="news-hero">
        <img
          src={coverOptions[news.id % coverOptions.length]}
          alt="Обложка новости"
          className="news-hero-cover"
        />
        <div>
          <h1>{news.title}</h1>
          <p className="meta">
            {new Date(news.published_at).toLocaleString()} ·{' '}
            {news.author ? news.author.name : `Автор #${news.author_id}`}
          </p>
          <p className="muted">ID новости: {news.id}</p>
        </div>
        {canEditNews && (
          <div className="actions">
            <button type="button" className="button ghost" onClick={() => setIsEditing((prev) => !prev)}>
              {isEditing ? 'Отмена' : 'Редактировать'}
            </button>
            <button type="button" className="button danger" onClick={deleteNews}>
              Удалить
            </button>
          </div>
        )}
      </div>
      {isEditing ? (
        <form onSubmit={submitNewsUpdate} className="form card">
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
          <textarea value={content} onChange={(e) => setContent(e.target.value)} />
          <button type="submit" className="button">
            Сохранить
          </button>
        </form>
      ) : (
        <div className="content-card">
          <p>{formatContent(news.content)}</p>
        </div>
      )}

      <section className="comments">
        <h2>Комментарии</h2>
        <ul className="list">
          {comments.map((comment) => (
            <li key={comment.id} className="comment">
              <div className="comment-body">
                <div className="comment-meta">
                  {comment.author ? comment.author.name : `Автор #${comment.author_id}`}
                  <span className="meta">{new Date(comment.published_at).toLocaleString()}</span>
                </div>
                {editingCommentId === comment.id ? (
                  <textarea
                    value={editingCommentText}
                    onChange={(e) => setEditingCommentText(e.target.value)}
                  />
                ) : (
                  <p>{comment.text}</p>
                )}
              </div>
              {currentUser && (currentUser.is_admin || currentUser.id === comment.author_id) && (
                <div className="actions">
                  {editingCommentId === comment.id ? (
                    <button
                      type="button"
                      className="button ghost"
                      onClick={() => submitCommentUpdate(comment.id)}
                    >
                      Сохранить
                    </button>
                  ) : (
                    <button type="button" className="button ghost" onClick={() => startEditComment(comment)}>
                      Редактировать
                    </button>
                  )}
                  <button type="button" className="button danger" onClick={() => deleteComment(comment.id)}>
                    Удалить
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
        {currentUser ? (
          <form onSubmit={submitComment} className="form card">
            <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Комментарий" />
            <button type="submit" className="button">
              Отправить
            </button>
          </form>
        ) : (
          <p className="notice">Войдите, чтобы оставить комментарий.</p>
        )}
      </section>
      {error && <p className="error">{error}</p>}
    </section>
  )
}
