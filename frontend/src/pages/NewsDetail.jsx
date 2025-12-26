import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api/client.js'

export default function NewsDetail() {
  const { id } = useParams()
  const [news, setNews] = useState(null)
  const [comments, setComments] = useState([])
  const [text, setText] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch(`/news/${id}`)
      .then(setNews)
      .catch((err) => setError(err.message))
  }, [id])

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

  if (!news) {
    return <p>Загрузка...</p>
  }

  return (
    <section>
      <h1>{news.title}</h1>
      <p className="meta">{new Date(news.published_at).toLocaleString()}</p>
      <pre className="content">{JSON.stringify(news.content, null, 2)}</pre>
      <h2>Комментарии</h2>
      <ul className="list">
        {comments.map((comment) => (
          <li key={comment.id}>{comment.text}</li>
        ))}
      </ul>
      <form onSubmit={submitComment} className="form">
        <textarea value={text} onChange={(e) => setText(e.target.value)} />
        <button type="submit">Отправить</button>
      </form>
      {error && <p className="error">{error}</p>}
    </section>
  )
}
