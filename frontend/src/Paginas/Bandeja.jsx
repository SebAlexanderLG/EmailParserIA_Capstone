import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  obtenerPerfil,
  obtenerCorreos,
  marcarComoLeido,
  marcarComoNoLeido,
  eliminarCorreo,
} from "../api/gmail";

import { obtenerPrompt, guardarPromptIA } from "../api/prompt";

import toast, { Toaster } from "react-hot-toast";

import "./Bandeja.css";

const CORREOS_POR_PAGINA = 20;

export default function Bandeja() {
  const [tab, setTab] = useState("no-leidos");
  const [q, setQ] = useState("");
  const [correos, setCorreos] = useState([]);
  const [nombreUsuario, setNombreUsuario] = useState("");
  const [loading, setLoading] = useState(true);
  const [pagina, setPagina] = useState(1);
  const [correoAEliminar, setCorreoAEliminar] = useState(null);

  const [mostrarModalPrompt, setMostrarModalPrompt] = useState(false);
  const [promptIA, setPromptIA] = useState("");

  const navegar = useNavigate();

  // CARGA INICIAL
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

        // CORREOS DEL API
        const data = await obtenerCorreos(50, "metadata");
        const listaCorreos = Array.isArray(data)
          ? data
          : data.correos || [];

        setCorreos(listaCorreos);

        // PROMPT PERSONALIZADO
        const promptData = await obtenerPrompt();
        if (promptData?.contexto) {
          setPromptIA(promptData.contexto);
        }

      } catch (err) {
        console.error("Error cargando datos:", err);
        navegar("/");
      } finally {
        setLoading(false);
      }
    };

    cargarDatos();
  }, [navegar]);

  // Reset de paginación al cambiar filtro
  useEffect(() => {
    setPagina(1);
  }, [tab, q]);

  // FILTRO
  const listaFiltrada = useMemo(() => {
    const base = correos.filter((c) =>
      tab === "leidos" ? c.leido : !c.leido
    );

    const term = q.trim().toLowerCase();
    if (!term) return base;

    return base.filter((c) =>
      (c.from_name + " " + c.subject + " " + c.snippet)
        .toLowerCase()
        .includes(term)
    );
  }, [tab, q, correos]);

  // PAGINACIÓN
  const totalPaginas = Math.max(
    1,
    Math.ceil(listaFiltrada.length / CORREOS_POR_PAGINA)
  );

  const indiceInicio = (pagina - 1) * CORREOS_POR_PAGINA;
  const listaPaginada = listaFiltrada.slice(
    indiceInicio,
    indiceInicio + CORREOS_POR_PAGINA
  );

  const paginaAnterior = () => pagina > 1 && setPagina(pagina - 1);
  const paginaSiguiente = () =>
    pagina < totalPaginas && setPagina(pagina + 1);

  // ABRIR CORREO
  const handleAbrirCorreo = async (c) => {
    navegar(`/correo/${c.id}`);

    if (!c.leido) {
      try {
        await marcarComoLeido(c.id);

        setCorreos((prev) =>
          prev.map((x) =>
            x.id === c.id ? { ...x, leido: true } : x
          )
        );

        setTab("leidos");
      } catch {
        toast.error("Error marcando como leído");
      }
    }
  };

  // TOGGLE LEÍDO
  const toggleLeido = async (c) => {
    try {
      if (c.leido) await marcarComoNoLeido(c.id);
      else await marcarComoLeido(c.id);

      setCorreos((prev) =>
        prev.map((x) =>
          x.id === c.id ? { ...x, leido: !c.leido } : x
        )
      );
    } catch {
      toast.error("Error cambiando estado del correo");
    }
  };

  // ELIMINAR
  const handleEliminarConfirmado = async () => {
    if (!correoAEliminar) return;

    try {
      await eliminarCorreo(correoAEliminar.id);

      setCorreos((prev) =>
        prev.filter((c) => c.id !== correoAEliminar.id)
      );

      toast.success("Correo eliminado");
      setCorreoAEliminar(null);

    } catch {
      toast.error("No se pudo eliminar el correo");
    }
  };

  const cerrarSesion = () => navegar("/");

  // GUARDAR PROMPT
  const handleGuardarPrompt = async () => {
    try {
      const res = await guardarPromptIA(promptIA);
      toast.success(res.mensaje || "Prompt guardado correctamente");
      setMostrarModalPrompt(false);
    } catch {
      toast.error("No se pudo guardar el prompt");
    }
  };

  return (
    <main className="bandeja-page">

      <Toaster
        position="bottom-right"
        toastOptions={{
          success: {
            duration: 2300,
            style: { background: "#2563eb", color: "white" },
          },
          error: {
            duration: 2600,
            style: { background: "#dc2626", color: "white" },
          },
        }}
      />

      <div className="bandeja-card">

        {/* HEADER */}
        <header className="bandeja-header">
          <div className="bandeja-title">
            <div className="bandeja-icon">📬</div>
            <div>
              <h2>Bandeja</h2>
              <p>Revisa y organiza tus correos</p>
            </div>
          </div>

          {/* BUSCADOR */}
          <div className="bandeja-search-wrap">
            <input
              className="bandeja-search"
              placeholder="Buscar correos..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>

          {/* USER */}
          <div className="bandeja-user">
            <span className="bandeja-user-name">{nombreUsuario}</span>
            <button onClick={cerrarSesion} className="btn-logout">
              Cerrar sesión
            </button>
          </div>
        </header>

        {/* TABS */}
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

          <button className="btn-ia" onClick={() => setMostrarModalPrompt(true)}>
            Cambiar parámetros de IA
          </button>
        </div>

        {/* TABLA */}
        <section className="tabla-wrap">

          {loading ? (
            <div className="cargando-container">
              <div className="cargando">
                Cargando mensajes <span className="spinner"></span>
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

                {listaPaginada.map((c) => (
                  <tr
                    key={c.id}
                    className={c.leido ? "fila leido" : "fila no-leido"}
                  >
                    <td onClick={() => handleAbrirCorreo(c)}>{c.date}</td>

                    <td onClick={() => handleAbrirCorreo(c)}>{c.from_name}</td>

                    <td onClick={() => handleAbrirCorreo(c)}>
                      {c.subject}

                      {/* CHECK PROCESADO */}
                      {c.respuesta_ia && (
                        <span className="tag-procesado">✔ Procesado</span>
                      )}
                    </td>

                    <td
                      className="msg"
                      onClick={() => handleAbrirCorreo(c)}
                    >
                      {c.snippet}
                    </td>

                    <td className="col-acciones acciones-inline">
                      <div className="acciones-wrap">
                        <button
                          className="btn-toggle"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleLeido(c);
                          }}
                        >
                          {c.leido ? "↩ No leído" : "✓ Leído"}
                        </button>

                        <button
                          className="btn-menu"
                          onClick={(e) => {
                            e.stopPropagation();
                            setCorreoAEliminar(c);
                          }}
                        >
                          ⋮
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {listaPaginada.length === 0 && (
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

        {/* PAGINACIÓN */}
        <div className="paginacion">
          <button
            className="btn-pag"
            disabled={pagina === 1}
            onClick={paginaAnterior}
          >
            ⬅ Anterior
          </button>

          <span className="info-pagina">
            Página {pagina} de {totalPaginas}
          </span>

          <button
            className="btn-pag"
            disabled={pagina === totalPaginas}
            onClick={paginaSiguiente}
          >
            Siguiente ➡
          </button>
        </div>
      </div>

      {/* MODAL ELIMINAR */}
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

      {/* MODAL IA */}
      {mostrarModalPrompt && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>🧠 Parámetros de IA</h3>
            <p>Define cómo deseas que la IA redacte tus respuestas:</p>

            <textarea
              className={`prompt-textarea ${
                promptIA.length === 600 ? "limite" : ""
              }`}
              value={promptIA}
              onChange={(e) => {
                if (e.target.value.length <= 600) {
                  setPromptIA(e.target.value);
                }
              }}
            />

            <p
              className={`prompt-count ${
                promptIA.length === 600
                  ? "error"
                  : promptIA.length > 480
                  ? "warning"
                  : ""
              }`}
            >
              {promptIA.length} / 600 caracteres
            </p>

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setMostrarModalPrompt(false)}
              >
                Cancelar
              </button>

              <button className="btn-confirm" onClick={handleGuardarPrompt}>
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}

    </main>
  );
}
