import { Routes, Route, Navigate } from 'react-router-dom'
import Inicio from './Paginas/Inicio.jsx'
import Bandeja from './Paginas/Bandeja.jsx'
import Correo from './Paginas/Correo.jsx'
import Respuesta from './Paginas/Respuesta.jsx'
import Redirect from './Paginas/Redirect.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route path="/bandeja" element={<Bandeja />} />
      <Route path="/correo/:id" element={<Correo />} />
      <Route path="/respuesta/:id" element={<Respuesta />} />
      <Route path="/redirect" element={<Redirect />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
