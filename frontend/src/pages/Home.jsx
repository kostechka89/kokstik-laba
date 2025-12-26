import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client.js'

export default function Home() {
  const [news, setNews] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch('/news/')
      .then(setNews)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <section>
      <h1>Новости</h1>
      {error && <p className="error">{error}</p>}
      <ul className="list">
        {news.map((item) => (
          <li key={item.id}>
            <Link to={`/news/${item.id}`}>{item.title}</Link>
            <span className="meta">{new Date(item.published_at).toLocaleString()}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
