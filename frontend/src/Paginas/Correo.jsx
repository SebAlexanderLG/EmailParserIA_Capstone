import parse from "html-react-parser";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  obtenerCorreoCompleto,
  descargarAdjunto,
  enviarCorreoRespuesta, // 👈 agregado
} from "../api/gmail";
import { generarRespuestaOllama } from "../api/ollama"; // 👈 agregado
import "./Correo.css";

export default function DetalleCorreo() {
  const { id } = useParams();
  const navegar = useNavigate();
  const [correo, setCorreo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 🔹 Estados nuevos para IA
  const [loadingIA, setLoadingIA] = useState(false);
  const [respuestaIA, setRespuestaIA] = useState("");
  const [enviando, setEnviando] = useState(false);

  // 📩 Cargar correo al abrir
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

  // 🧠 Generar respuesta con Ollama
  const handleGenerarIA = async () => {
    setLoadingIA(true);
    setRespuestaIA("");
    try {
      const data = await generarRespuestaOllama({
        mensaje_id: id,
        prompt_key: "respuesta_ia",
      });
      setRespuestaIA(data.respuesta || "Sin respuesta generada por la IA.");
    } catch (err) {
      console.error(err);
      setError("Error generando respuesta IA.");
    } finally {
      setLoadingIA(false);
    }
  };

  // 🔁 Regenerar respuesta IA
  const handleRegenerar = () => {
    setRespuestaIA("");
    handleGenerarIA();
  };

  // 📤 Enviar correo al remitente (ya con respuesta IA)
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

      alert(
        `📨 Correo enviado correctamente.\nFecha de envío: ${res.fecha_envio}`
      );

      // ✅ Limpiar y volver a la bandeja
      setRespuestaIA("");
      navegar("/bandeja");
    } catch (err) {
      console.error("Error al enviar correo:", err);
      alert("❌ Error al enviar el correo.");
    } finally {
      setEnviando(false);
    }
  };

  // 🌀 Estado de carga del correo
  if (loading)
    return (
      <main className="detalle">
        <div className="loading-box">
          <div className="spinner"></div>
          <p>Cargando correo...</p>
        </div>
      </main>
    );

  // ❌ Estado de error
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

  // ✅ Render principal
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

        {/* 🔹 Si todavía no hay respuesta */}
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

        {/* 🔹 Mientras se genera la respuesta */}
        {loadingIA && (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>🧠 Generando respuesta IA...</p>
          </div>
        )}

        {/* 🔹 Si ya se generó la respuesta (editable) */}
        {respuestaIA && !loadingIA && (
          <div className="respuesta-ia-box">
            <h3>Respuesta generada por IA:</h3>

            {/* 🔹 Campo editable */}
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
                {enviando ? "Enviando..." : "Enviar correo"}
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
