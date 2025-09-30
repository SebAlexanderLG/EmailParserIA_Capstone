import { useParams, useNavigate } from 'react-router-dom'
import './DetalleCorreo.css'
import { correos } from '../data/correos.js'

export default function DetalleCorreo() {
  const { id } = useParams()
  const navegar = useNavigate()
  const correo = correos.find(c => c.id === id)

  if (!correo) {
    return (
      <main className="detalle">
        <div className="box">
          <p>No se encontró el correo.</p>
          <button className="btn" onClick={() => navegar('/bandeja')}>Volver</button>
        </div>
      </main>
    )
  }

  return (
    <main className="detalle">
      <div className="box">
        <h2>{correo.asunto}</h2>
        <p><b>Fecha:</b> {correo.fecha}</p>
        <p><b>Remitente:</b> {correo.remitente}</p>
        <pre className="mensaje">{correo.mensaje}</pre>

        <div className="acciones">
          <button className="btn" onClick={() => navegar('/bandeja')}>Volver</button>
          <button className="btn primario" onClick={() => navegar(`/respuesta/${correo.id}`)}>
            Generar respuesta
          </button>
        </div>
      </div>
    </main>
  )
}
