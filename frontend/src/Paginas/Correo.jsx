import parse from "html-react-parser";
import { useEffect, useState } from "react";
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

  // Estados principales
  const [correo, setCorreo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Estados para IA
  const [loadingIA, setLoadingIA] = useState(false);
  const [respuestaIA, setRespuestaIA] = useState("");
  const [enviando, setEnviando] = useState(false);

  // Carga correo completo al abrir
  useEffect(() => {
    setLoading(true);
    setError("");
    obtenerCorreoCompleto(id)
      .then((data) => setCorreo(data))
      .catch((err) => {
        console.error("Error obteniendo correo completo:", err);
        setError("No se pudo cargar el correo.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  // Genera respuesta con Ollama (usando prompt personalizado)
  const handleGenerarIA = async () => {
    setLoadingIA(true);
    setRespuestaIA("");

    // Lee el prompt personalizado guardado por el usuario
    const promptUsuario =
      localStorage.getItem("prompt_ia") ||
      "Por favor, redacta una respuesta profesional y cordial al siguiente correo:";

    try {
      const data = await generarRespuestaOllama({
        mensaje_id: id,
        prompt_key: promptUsuario, // texto por defecto
      });

      setRespuestaIA(data.respuesta || "Sin respuesta generada por la IA.");
    } catch (err) {
      console.error("Error generando respuesta IA:", err);
      setError("Error generando respuesta IA.");
    } finally {
      setLoadingIA(false);
    }
  };

  // Regenera respuesta IA
  const handleRegenerar = () => {
    setRespuestaIA("");
    handleGenerarIA();
  };

  // Enviar correo al remitente (guarda respuesta y fecha en BD)
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

      alert(`📨 Correo enviado correctamente.\nFecha de envío: ${res.fecha_envio}`);
      setRespuestaIA("");
      navegar("/bandeja");
    } catch (err) {
      console.error("Error al enviar correo:", err);
      alert("❌ Error al enviar el correo.");
    } finally {
      setEnviando(false);
    }
  };

  // Estado de carga inicial
  if (loading)
    return (
      <main className="detalle">
        <div className="loading-box">
          <div className="spinner"></div>
          <p>Cargando correo...</p>
        </div>
      </main>
    );

  // Estado de error
  if (error || !correo)
    return (
      <main className="detalle">
        <div className="box">
          <p>{error || "No se encontró el correo."}</p>
          <button className="btn" onClick={() => navegar("/bandeja")}>
            Volver
          </button>
        </div>
      </main>
    );

  // Render principal
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

        {correo.body_text ? (
          <pre className="mensaje">{correo.body_text}</pre>
        ) : (
          <div className="mensaje">{parse(correo.body_html)}</div>
        )}

        {correo.attachments && correo.attachments.length > 0 && (
          <div className="adjuntos">
            <h4>Archivos adjuntos:</h4>
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

        {/* Si aún no hay respuesta generada */}
        {!respuestaIA && !loadingIA && (
          <div className="acciones">
            <button className="btn" onClick={() => navegar("/bandeja")}>
              Volver
            </button>
            <button className="btn primario" onClick={handleGenerarIA}>
              Generar respuesta IA
            </button>
          </div>
        )}

        {loadingIA && (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>🧠 Generando respuesta IA...</p>
          </div>
        )}

        {/* Si ya se generó la respuesta (campo editable antes de enviar) */}
        {respuestaIA && !loadingIA && (
          <div className="respuesta-ia-box">
            <h3>Respuesta generada por IA:</h3>

            <textarea
              className="respuesta-ia-editable"
              value={respuestaIA}
              onChange={(e) => setRespuestaIA(e.target.value)}
              placeholder="Edita la respuesta antes de enviar..."
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
                {enviando ? "Enviando mensaje..." : "Enviar correo"}
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
