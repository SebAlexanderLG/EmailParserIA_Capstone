import './Inicio.css'
import logoGmail from '../img/logoGmail.png'
import { iniciarSesionGmail } from '../api/auth'
import { useNavigate } from 'react-router-dom'

export default function Inicio() {
  const navegar = useNavigate()

  return (
    <main className="inicio">
      <div className="inicio-card">

        {/* Icono */}
        <div className="inicio-icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
            className="icon-envelope"
          >
            <path
              d="M3 7.5C3 6.12 4.12 5 5.5 5h13A2.5 2.5 0 0 1 21 7.5v9A2.5 2.5 0 0 1 18.5 19h-13A2.5 2.5 0 0 1 3 16.5v-9Z"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M4 8l8 5 8-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        {/* Título con AI estilizado */}
        <h1 className="inicio-titulo">
          <span className="ai">AI</span> Email Parser
        </h1>

        <p className="inicio-subtitulo">Organiza y responde tus correos con IA</p>

        {/* Botones */}
        <div className="inicio-botones">
          <button className="btn gmail" onClick={iniciarSesionGmail}>
            Iniciar sesión con Gmail
            <img src={logoGmail} alt="Gmail" className="logoGmail" />
          </button>

          <button
            className="btn secundario"
            onClick={() => navegar('/bandeja')}
          >
            Entrar al sitio
          </button>
        </div>
      </div>
    </main>
  )
}
