import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { obtenerPerfil, obtenerCorreos, marcarComoLeido, eliminarCorreo } from "../api/gmail";
import "./Bandeja.css";

export default function Bandeja() {
  const [tab, setTab] = useState("no-leidos");
  const [q, setQ] = useState("");
  const [correos, setCorreos] = useState([]);
  const [nombreUsuario, setNombreUsuario] = useState("");
  const [loading, setLoading] = useState(true);
  const [correoAEliminar, setCorreoAEliminar] = useState(null); // ✅ Estado para el modal
  const navegar = useNavigate();

  // Cargar perfil y correos
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const perfil = await obtenerPerfil();
        if (perfil.error) {
          navegar("/");
          return;
        }
        setNombreUsuario(perfil.nombre_real);

        setLoading(true);
        const correosData = await obtenerCorreos(50, "metadata");
        setCorreos(correosData);
      } catch (err) {
        console.error("Error cargando datos:", err);
        navegar("/");
      } finally {
        setLoading(false);
      }
    };

    cargarDatos();
  }, [navegar]);

  // Filtrar lista según tab y búsqueda
  const lista = useMemo(() => {
    const base = correos.filter((c) => (tab === "leidos" ? c.leido : !c.leido));
    const term = q.trim().toLowerCase();
    if (!term) return base;
    return base.filter((c) =>
      (c.from_name + " " + c.subject + " " + c.snippet)
        .toLowerCase()
        .includes(term)
    );
  }, [tab, q, correos]);

  const cerrarSesion = () => navegar("/");

  const handleEliminarConfirmado = async () => {
    if (!correoAEliminar) return;
    try {
      await eliminarCorreo(correoAEliminar.id);
      setCorreos(prev => prev.filter(c => c.id !== correoAEliminar.id));
      setCorreoAEliminar(null); // cerrar modal
    } catch (err) {
      console.error("Error eliminando correo:", err);
      alert("No se pudo eliminar el correo.");
    }
  };

  const handleAbrirCorreo = async (c) => {
    navegar(`/correo/${c.id}`);
    if (!c.leido) {
      try {
        await marcarComoLeido(c.id);
        setCorreos(prev =>
          prev.map(x => (x.id === c.id ? { ...x, leido: true } : x))
        );
        setTab("leidos");
      } catch (err) {
        console.error("Error marcando como leído:", err);
      }
    }
  };

  return (
    <main className="bandeja">
      <header className="topbar">
        <h2>📬 Bandeja</h2>
        <input
          className="buscar"
          placeholder="Buscar..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <div className="usuario">
          <span>{nombreUsuario}</span>
          <button onClick={cerrarSesion} className="btn-cerrar">Cerrar sesión</button>
        </div>
        <div className="tabs">
          <button
            className={`tab ${tab === "no-leidos" ? "activa" : ""}`}
            onClick={() => setTab("no-leidos")}
          >
            No leídos
          </button>
          <button
            className={`tab ${tab === "leidos" ? "activa" : ""}`}
            onClick={() => setTab("leidos")}
          >
            Leídos
          </button>
        </div>
        <div className="prompts">
          <button className="prompt" onClick={() => {}}>Cambiar parámetros de IA</button>
        </div>
      </header>

      <section className="tabla-wrap">
        {loading ? (
          <div className="cargando-container">
            <div className="cargando">
              Cargando mensajes<span className="spinner"></span>
            </div>
          </div>
        ) : (
          <table className="tabla">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Remitente</th>
                <th>Asunto</th>
                <th>Mensaje</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {lista.map((c) => (
                <tr key={c.id} style={{ cursor: "pointer" }}>
                  <td onClick={() => handleAbrirCorreo(c)}>{c.date}</td>
                  <td onClick={() => handleAbrirCorreo(c)}>{c.from_name}</td>
                  <td onClick={() => handleAbrirCorreo(c)}>{c.subject}</td>
                  <td className="msg" onClick={() => handleAbrirCorreo(c)}>{c.snippet}</td>
                  <td>
                    <button
                      className="btn-menu"
                      onClick={(e) => {
                        e.stopPropagation();
                        setCorreoAEliminar(c); // ✅ Abre modal en lugar de confirmar directo
                      }}
                    >
                      ⋮
                    </button>
                  </td>
                </tr>
              ))}
              {lista.length === 0 && (
                <tr>
                  <td colSpan="5" className="vacio">Sin resultados</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </section>
      {correoAEliminar && (
        <div className="modal-overlay">
          <div className="modal">
            <p>¿Eliminar el correo de <strong>{correoAEliminar.from_name}</strong>?</p>
            <p className="modal-subject">{correoAEliminar.subject}</p>
            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setCorreoAEliminar(null)}
              >
                Cancelar
              </button>
              <button
                className="btn-confirm"
                onClick={handleEliminarConfirmado}
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
