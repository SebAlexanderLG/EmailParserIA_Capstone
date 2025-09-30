import { Routes, Route, Navigate } from 'react-router-dom'
import Inicio from './Paginas/Inicio.jsx'
import Bandeja from './Paginas/Bandeja.jsx'
import DetalleCorreo from './Paginas/DetalleCorreo.jsx'
import Respuesta from './Paginas/Respuesta.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route path="/bandeja" element={<Bandeja />} />
      <Route path="/correo/:id" element={<DetalleCorreo />} />
      <Route path="/respuesta/:id" element={<Respuesta />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
