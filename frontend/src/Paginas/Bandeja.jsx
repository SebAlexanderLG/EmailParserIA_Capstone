import { useMemo, useState } from 'react'
import './Bandeja.css'
import { correos } from '../data/correos.js'
import { useNavigate } from 'react-router-dom'

export default function Bandeja() {
  const [tab, setTab] = useState('no-leidos') // 'no-leidos' | 'leidos'
  const [q, setQ] = useState('')
  const navegar = useNavigate()

  const lista = useMemo(() => {
    const base = correos.filter(c => tab === 'leidos' ? c.leido : !c.leido)
    const term = q.trim().toLowerCase()
    if (!term) return base
    return base.filter(c =>
      (c.remitente + ' ' + c.asunto + ' ' + c.mensaje).toLowerCase().includes(term)
    )
  }, [tab, q])

  return (
    <main className="bandeja">
      <header className="topbar">
        <h2>📬 Bandeja</h2>
        <input
          className="buscar"
          placeholder="Buscar (remitente, asunto, texto)…"
          value={q}
          onChange={e => setQ(e.target.value)}
        />
        <div className="tabs">
          <button className={`tab ${tab==='no-leidos' ? 'activa' : ''}`} onClick={() => setTab('no-leidos')}>No leídos</button>
          <button className={`tab ${tab==='leidos' ? 'activa' : ''}`} onClick={() => setTab('leidos')}>Leídos</button>
        </div>
      </header>

      <section className="tabla-wrap">
        <table className="tabla">
          <thead>
            <tr>
              <th>Fecha</th><th>Remitente</th><th>Asunto</th><th>Mensaje</th>
            </tr>
          </thead>
          <tbody>
            {lista.map(c => (
              <tr key={c.id} onClick={() => navegar(`/correo/${c.id}`)} style={{cursor:'pointer'}}>
                <td>{c.fecha}</td>
                <td>{c.remitente}</td>
                <td>{c.asunto}</td>
                <td className="msg">{c.mensaje}</td>
              </tr>
            ))}
            {lista.length === 0 && (
              <tr><td colSpan="4" className="vacio">Sin resultados</td></tr>
            )}
          </tbody>
        </table>
      </section>
    </main>
  )
}
