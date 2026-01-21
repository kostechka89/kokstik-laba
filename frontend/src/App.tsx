import { FormEvent, useMemo, useState } from "react"
import "./App.css"

const bazovyiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

const sluchaynoeImya = () => {
  const prifs = ["tihiy", "snezh", "byst", "lamp", "krist", "soln"]
  const suf = ["kot", "lis", "volk", "grom", "sten", "ogon"]
  const nomer = Math.floor(Math.random() * 900 + 100)
  const prif = prifs[Math.floor(Math.random() * prifs.length)]
  const sufiks = suf[Math.floor(Math.random() * suf.length)]
  return `${prif}_${sufiks}${nomer}`
}

const raspakovatOshibku = async (otvet: Response) => {
  try {
    const dannye = await otvet.json()
    if (Array.isArray(dannye?.detail)) {
      return dannye.detail.map((item: { msg?: string }) => item.msg ?? "ошибка")
    }
    if (typeof dannye?.detail === "string") {
      return [dannye.detail]
    }
    return ["неизвестная ошибка"]
  } catch {
    return ["не удалось разобрать ответ"]
  }
}

function App() {
  const [login, setLogin] = useState("")
  const [parol, setParol] = useState("")
  const [loginVhod, setLoginVhod] = useState("")
  const [parolVhod, setParolVhod] = useState("")
  const [status, setStatus] = useState("")
  const [statusVhod, setStatusVhod] = useState("")
  const [oshibki, setOshibki] = useState<string[]>([])
  const [oshibkiVhod, setOshibkiVhod] = useState<string[]>([])
  const [posledniy, setPosledniy] = useState("")
  const urlRegistr = useMemo(() => `${bazovyiUrl}/api/register`, [])
  const urlVhod = useMemo(() => `${bazovyiUrl}/api/vhod`, [])

  const otpravitRegistr = async (e: FormEvent) => {
    e.preventDefault()
    setStatus("отправка...")
    setOshibki([])
    const otvet = await fetch(urlRegistr, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, parol })
    })
    if (otvet.ok) {
      const dannye = await otvet.json()
      setStatus(dannye.message)
      setPosledniy(login)
      setLogin("")
      setParol("")
    } else {
      setStatus("ошибка")
      const spisok = await raspakovatOshibku(otvet)
      setOshibki(spisok)
    }
  }

  const otpravitVhod = async (e: FormEvent) => {
    e.preventDefault()
    setStatusVhod("проверка...")
    setOshibkiVhod([])
    const otvet = await fetch(urlVhod, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login: loginVhod, parol: parolVhod })
    })
    if (otvet.ok) {
      const dannye = await otvet.json()
      setStatusVhod(dannye.message)
      setLoginVhod("")
      setParolVhod("")
    } else {
      setStatusVhod("ошибка")
      const spisok = await raspakovatOshibku(otvet)
      setOshibkiVhod(spisok)
    }
  }

  return (
    <div className="obolochka">
      <header className="shapka">
        <div className="znak">◇</div>
        <div>
          <h1>Registratsiya MVP</h1>
          <p>форма регистрации с живыми ответами и проверками</p>
        </div>
      </header>

      <section className="panel">
        <div className="karta">
          <h2>Registratsiya</h2>
          <form className="forma" onSubmit={otpravitRegistr}>
            <label>
              login
              <input
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                placeholder="tihiy_kot777"
                autoComplete="username"
              />
            </label>
            <label>
              parol
              <input
                value={parol}
                onChange={(e) => setParol(e.target.value)}
                placeholder="Super#123"
                type="password"
                autoComplete="new-password"
              />
            </label>
            <div className="stroka-knopok">
              <button type="submit">создать</button>
              <button
                type="button"
                className="vtora"
                onClick={() => setLogin(sluchaynoeImya())}
              >
                случайный логин
              </button>
            </div>
          </form>
          {status && <div className="status">{status}</div>}
          {oshibki.length > 0 && (
            <ul className="oshibki">
              {oshibki.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          )}
          {posledniy && (
            <div className="posledniy">
              последний созданный: <strong>{posledniy}</strong>
            </div>
          )}
        </div>

        <div className="karta">
          <h2>Vhod</h2>
          <form className="forma" onSubmit={otpravitVhod}>
            <label>
              login
              <input
                value={loginVhod}
                onChange={(e) => setLoginVhod(e.target.value)}
                placeholder="tihiy_kot777"
                autoComplete="username"
              />
            </label>
            <label>
              parol
              <input
                value={parolVhod}
                onChange={(e) => setParolVhod(e.target.value)}
                placeholder="Super#123"
                type="password"
                autoComplete="current-password"
              />
            </label>
            <button type="submit">войти</button>
          </form>
          {statusVhod && <div className="status">{statusVhod}</div>}
          {oshibkiVhod.length > 0 && (
            <ul className="oshibki">
              {oshibkiVhod.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="pravila">
        <h3>Reglament</h3>
        <div className="pravila-setka">
          <div className="chips">login 3-32 символа</div>
          <div className="chips">только латиница/цифры/._-</div>
          <div className="chips">parol минимум 8 символов</div>
          <div className="chips">строчная + заглавная + цифра + спецсимвол</div>
        </div>
      </section>

      <footer className="niz">
        <span>Backend: FastAPI</span>
        <span>DB: PostgreSQL</span>
        <span>Hash: Argon2id</span>
      </footer>
    </div>
  )
}

export default App
