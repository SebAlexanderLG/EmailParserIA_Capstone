import { useParams, useNavigate } from 'react-router-dom'
import './Respuesta.css'
import { correos } from '../data/correos.js'
import { useEffect, useState } from 'react'

export default function Respuesta() {
  const { id } = useParams()
  const navegar = useNavigate()
  const correo = correos.find(c => c.id === id)
  const [texto, setTexto] = useState('')

  useEffect(() => {
    if (correo) {
      setTexto(
`Hola ${correo.remitente.split('@')[0]},\n
Gracias por tu mensaje sobre "${correo.asunto}".
Lo revisaré y te respondo con más detalle a la brevedad.\n
Saludos,\nDavid`
      )
    }
  }, [correo])

  if (!correo) {
    return (
      <main className="respuesta">
        <div className="box">
          <p>No se encontró el correo.</p>
          <button className="btn" onClick={() => navegar('/bandeja')}>Volver</button>
        </div>
      </main>
    )
  }

  return (
    <main className="respuesta">
      <div className="box">
        <h2>Respuesta a: {correo.asunto}</h2>
        <textarea
          className="editor"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
        />
        <div className="acciones">
          <button className="btn" onClick={() => navegar(-1)}>Atrás</button>
          <button className="btn primario" onClick={() => alert('Enviado (demo) ✅')}>Enviar</button>
        </div>
      </div>
    </main>
  )
}
