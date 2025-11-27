import parse from "html-react-parser";
import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  obtenerCorreoCompleto,
  descargarAdjunto,
  enviarCorreoRespuesta,
} from "../api/gmail";
import { generarRespuestaOllama } from "../api/ollama";
import "./Correo.css";

export default function DetalleCorreo() {
  const { id } = useParams();
  const navegar = useNavigate();

  const [correo, setCorreo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [loadingIA, setLoadingIA] = useState(false);
  const [respuestaIA, setRespuestaIA] = useState("");
  const [enviando, setEnviando] = useState(false);

  // Ref para el textarea auto-expandible
  const textareaRef = useRef(null);

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";
  };

  // Cargar el correo al abrir la página (Gmail + BD)
  useEffect(() => {
    setLoading(true);
    setError("");

    obtenerCorreoCompleto(id)
      .then((data) => {
        setCorreo(data);

        // Si en la BD ya hay una respuesta IA, la dejamos lista
        if (data.respuesta_ia) {
          // No la ponemos de inmediato en edición, solo la tenemos disponible
          // Si quisieras que aparezca editable al tiro, usa: setRespuestaIA(data.respuesta_ia);
        }
      })
      .catch(() => setError("No se pudo cargar el correo."))
      .finally(() => setLoading(false));
  }, [id]);

  // Ajustar altura del textarea cuando cambia la respuesta
  useEffect(() => {
    autoResize();
  }, [respuestaIA]);

  const handleGenerarIA = async () => {
    setLoadingIA(true);
    setRespuestaIA("");

    const promptUsuario =
      localStorage.getItem("prompt_ia") ||
      "Por favor, redacta una respuesta profesional y cordial al siguiente correo:";

    try {
      const data = await generarRespuestaOllama({
        mensaje_id: id,
        prompt_key: promptUsuario,
      });

      setRespuestaIA(data.respuesta || "Sin respuesta generada por la IA.");
    } catch (err) {
      setError("Error generando respuesta IA.");
    } finally {
      setLoadingIA(false);
    }
  };

  const handleRegenerar = () => {
    setRespuestaIA("");
    handleGenerarIA();
  };

  const handleEnviar = async () => {
    if (!respuestaIA.trim()) {
      alert("La respuesta no puede estar vacía.");
      return;
    }

    setEnviando(true);
    try {
      const res = await enviarCorreoRespuesta({
        mensaje_id: id,
        respuesta_texto: respuestaIA,
      });

      alert(`📨 Correo enviado correctamente.\nFecha: ${res.fecha_envio}`);
      setRespuestaIA("");
      navegar("/bandeja");
    } catch (err) {
      alert("❌ Error al enviar el correo.");
    } finally {
      setEnviando(false);
    }
  };

  if (loading)
    return (
      <main className="detalle">
        <div className="loading-box">
          <div className="spinner"></div>
          <p>Cargando correo...</p>
        </div>
      </main>
    );

  if (!correo)
    return (
      <main className="detalle">
        <p className="error">{error || "Correo no encontrado."}</p>
      </main>
    );

  return (
    <main className="detalle">
      <div className="box">
        <h2>{correo.subject}</h2>

        <p>
          <b>Fecha:</b> {correo.date}
        </p>
        <p>
          <b>Remitente:</b> {correo.from}
        </p>

        {/* CUERPO DEL MENSAJE SIN SCROLL */}
        {correo.body_text ? (
          <div className="mensaje mensaje-texto">{correo.body_text}</div>
        ) : (
          <div className="mensaje mensaje-html">
            {correo.body_html ? parse(correo.body_html) : null}
          </div>
        )}

        {correo.attachments?.length > 0 && (
          <div className="adjuntos">
            <h4>Archivos Adjuntos</h4>
            <ul>
              {correo.attachments.map((adj, i) => (
                <li key={i}>
                  <button
                    className="btn-secundario"
                    onClick={() =>
                      descargarAdjunto(id, adj.attachmentId, adj.filename)
                    }
                  >
                    {adj.filename} ({Math.round(adj.size / 1024)} KB)
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <hr />

        {/* CASO 1: Ya hay respuesta IA guardada en la BD y no estoy editando nada */}
        {!loadingIA && correo.respuesta_ia && !respuestaIA && (
          <div className="respuesta-ia-box">
            <h3>Respuesta enviada anteriormente:</h3>

            <div className="respuesta-guardada">{correo.respuesta_ia}</div>

            {correo.fecha_envio && (
              <p className="fecha-envio">
                Enviada el <b>{correo.fecha_envio}</b>
              </p>
            )}

            <div className="acciones">
              <button
                className="btn-secundario"
                onClick={() => setRespuestaIA(correo.respuesta_ia)}
              >
                Reutilizar / Editar respuesta
              </button>

              <button className="btn" onClick={() => navegar("/bandeja")}>
                Volver
              </button>
            </div>
          </div>
        )}

        {/* CASO 2: No hay respuesta guardada y no estoy editando → mostrar botones normales */}
        {!respuestaIA && !loadingIA && !correo.respuesta_ia && (
          <div className="acciones">
            <button className="btn" onClick={() => navegar("/bandeja")}>
              Volver
            </button>
            <button className="btn primario" onClick={handleGenerarIA}>
              Generar respuesta IA
            </button>
          </div>
        )}

        {/* Pantalla de carga IA */}
        {loadingIA && (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>🧠 Generando respuesta IA...</p>
          </div>
        )}

        {/* CASO 3: Estoy editando una respuesta (generada o reutilizada) */}
        {respuestaIA && !loadingIA && (
          <div className="respuesta-ia-box">
            <h3>Respuesta generada por IA:</h3>

            <textarea
              ref={textareaRef}
              className="respuesta-ia-editable"
              value={respuestaIA}
              onChange={(e) => {
                setRespuestaIA(e.target.value);
                autoResize();
              }}
              placeholder="Edita la respuesta..."
            />

            <div className="acciones">
              <button className="btn" onClick={() => navegar("/bandeja")}>
                Volver
              </button>

              <button className="btn-secundario" onClick={handleRegenerar}>
                Generar nueva respuesta
              </button>

              <button
                className="btn primario"
                onClick={handleEnviar}
                disabled={enviando}
              >
                {enviando ? "Enviando..." : "Enviar correo"}
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
