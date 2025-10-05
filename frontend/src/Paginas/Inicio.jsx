import logoGmail from '../img/logoGmail.png'
import './Inicio.css'
import { iniciarSesionGmail } from '../api/auth'
import { useNavigate } from 'react-router-dom'


export default function Inicio() {
  const navegar = useNavigate()
  const irABandeja = () => navegar('/bandeja')

  return (
    <main className="inicio">
      <h1 className="titulo">AI Email Parser</h1>
      <p className="subtitulo">Organiza y responde tus correos con IA</p>

      <div className="botones">
        <button className="btn" onClick={iniciarSesionGmail}>Iniciar sesión con Gmail<img src={logoGmail} alt='Gmail' className='logoGmail'/></button>
        <button className="btn secundario" onClick={() => alert('Demo 👋')}>Ver demo</button>
      </div>
    </main>
  )
}
