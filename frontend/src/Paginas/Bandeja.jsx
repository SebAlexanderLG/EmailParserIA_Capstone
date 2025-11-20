import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  obtenerPerfil,
  obtenerCorreos,
  marcarComoLeido,
  eliminarCorreo,
} from "../api/gmail";
import "./Bandeja.css";

export default function Bandeja() {
  const [tab, setTab] = useState("no-leidos");
  const [q, setQ] = useState("");
  const [correos, setCorreos] = useState([]);
  const [nombreUsuario, setNombreUsuario] = useState("");
  const [loading, setLoading] = useState(true);
  const [correoAEliminar, setCorreoAEliminar] = useState(null);
  const navegar = useNavigate();

  // Cargar perfil y correos (sin botar al inicio)
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        setLoading(true);

        const perfil = await obtenerPerfil().catch(() => null);
        if (perfil && !perfil.error && perfil.nombre_real) {
          setNombreUsuario(perfil.nombre_real);
        } else {
          setNombreUsuario("Usuario Demo");
        }

        const correosData = await obtenerCorreos(50, "metadata").catch(
          () => []
        );
        setCorreos(correosData);
      } catch (err) {
        console.error("Error cargando datos:", err);
        setNombreUsuario("Usuario Demo");
      } finally {
        setLoading(false);
      }
    };

    cargarDatos();
  }, []);

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
      setCorreos((prev) => prev.filter((c) => c.id !== correoAEliminar.id));
      setCorreoAEliminar(null);
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
        setCorreos((prev) =>
          prev.map((x) => (x.id === c.id ? { ...x, leido: true } : x))
        );
        setTab("leidos");
      } catch (err) {
        console.error("Error marcando como leído:", err);
      }
    }
  };

  return (
    <main className="bandeja-page">
      <div className="bandeja-card">
        {/* Topbar */}
        <header className="bandeja-header">
          <div className="bandeja-title">
            <div className="bandeja-icon">
              <span role="img" aria-label="Inbox">
                📬
              </span>
            </div>
            <div>
              <h2>Bandeja</h2>
              <p>Revisa y organiza tus correos</p>
            </div>
          </div>

          <div className="bandeja-search-wrap">
            <input
              className="bandeja-search"
              placeholder="Buscar correos por remitente, asunto o contenido..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>

          <div className="bandeja-user">
            <span className="bandeja-user-name">{nombreUsuario}</span>
            <button onClick={cerrarSesion} className="btn-logout">
              Cerrar sesión
            </button>
          </div>
        </header>

        {/* Tabs y acciones */}
        <div className="bandeja-controls">
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

          <button className="btn-ia" onClick={() => {}}>
            Cambiar parámetros de IA
          </button>
        </div>

        {/* Tabla */}
        <section className="tabla-wrap">
          {loading ? (
            <div className="cargando-container">
              <div className="cargando">
                Cargando mensajes
                <span className="spinner"></span>
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
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {lista.map((c) => (
                  <tr
                    key={c.id}
                    className={c.leido ? "fila leido" : "fila no-leido"}
                  >
                    <td onClick={() => handleAbrirCorreo(c)}>{c.date}</td>
                    <td onClick={() => handleAbrirCorreo(c)}>{c.from_name}</td>
                    <td onClick={() => handleAbrirCorreo(c)}>{c.subject}</td>
                    <td
                      className="msg"
                      onClick={() => handleAbrirCorreo(c)}
                    >
                      {c.snippet}
                    </td>
                    <td className="col-acciones">
                      <button
                        className="btn-menu"
                        onClick={(e) => {
                          e.stopPropagation();
                          setCorreoAEliminar(c);
                        }}
                        title="Eliminar correo"
                      >
                        ⋮
                      </button>
                    </td>
                  </tr>
                ))}
                {lista.length === 0 && (
                  <tr>
                    <td colSpan="5" className="vacio">
                      Sin resultados
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </section>
      </div>

      {/* Modal eliminar */}
      {correoAEliminar && (
        <div className="modal-overlay">
          <div className="modal">
            <p>
              ¿Eliminar el correo de{" "}
              <strong>{correoAEliminar.from_name}</strong>?
            </p>
            <p className="modal-subject">{correoAEliminar.subject}</p>
            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setCorreoAEliminar(null)}
              >
                Cancelar
              </button>
              <button className="btn-confirm" onClick={handleEliminarConfirmado}>
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
