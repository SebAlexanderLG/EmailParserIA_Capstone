import parse from "html-react-parser";
import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import {
  obtenerCorreoCompleto,
  descargarAdjunto,
  enviarCorreoRespuesta,
} from "../api/gmail";

import { generarRespuestaOllama } from "../api/ollama";
import { obtenerPrompt } from "../api/prompt";

import toast, { Toaster } from "react-hot-toast";

import "./Correo.css";

// CACHE
import { correosCache } from "../api/correosCache";

export default function DetalleCorreo() {
  const { id } = useParams();
  const navegar = useNavigate();

  const [correo, setCorreo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [loadingIA, setLoadingIA] = useState(false);
  const [respuestaIA, setRespuestaIA] = useState("");
  const [enviando, setEnviando] = useState(false);

  const [promptUsuarioBD, setPromptUsuarioBD] = useState("");

  const textareaRef = useRef(null);

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";
  };

  // CARGA CORREO + CACHE
  useEffect(() => {
    const cargarTodo = async () => {
      setLoading(true);
      setError("");

      try {
        // 1) SI YA ESTÁ EN CACHE → carga inmediata
        if (correosCache.detalle[id]) {
          setCorreo(correosCache.detalle[id]);
          setLoading(false);
        }

        // 2) Cargar desde backend (refresco)
        const dataCorreo = await obtenerCorreoCompleto(id);
        setCorreo(dataCorreo);

        // guardar en cache
        correosCache.detalle[id] = dataCorreo;

        // 3) cargar prompt
        const p = await obtenerPrompt();
        setPromptUsuarioBD(
          p?.contexto ||
            "Por favor, redacta una respuesta profesional y cordial al siguiente correo:"
        );

      } catch (err) {
        console.error(err);
        setError("No se pudo cargar el correo.");
      } finally {
        setLoading(false);
      }
    };

    cargarTodo();
  }, [id]);

  useEffect(() => {
    autoResize();
  }, [respuestaIA]);

  // GENERAR RESPUESTA IA
  const handleGenerarIA = async () => {
    setLoadingIA(true);
    setRespuestaIA("");

    try {
      const data = await generarRespuestaOllama({
        mensaje_id: id,
        prompt_key: promptUsuarioBD,
      });

      setRespuestaIA(data.respuesta || "Sin respuesta generada por la IA.");
      toast.success("Respuesta generada correctamente");
    } catch {
      toast.error("Error generando respuesta con IA");
    } finally {
      setLoadingIA(false);
    }
  };

  const handleRegenerar = async () => {
    setRespuestaIA("");
    handleGenerarIA();
  };

  // ENVIAR CORREO
  const handleEnviar = async () => {
    if (!respuestaIA.trim()) {
      toast.error("La respuesta no puede estar vacía");
      return;
    }

    setEnviando(true);

    try {
      await enviarCorreoRespuesta({
        mensaje_id: id,
        respuesta_texto: respuestaIA,
      });

      toast.success("Correo enviado correctamente");
      setRespuestaIA("");

      navegar("/bandeja");
    } catch {
      toast.error("Error al enviar el correo");
    } finally {
      setEnviando(false);
    }
  };

  // LOADING
  if (loading)
    return (
      <main className="detalle">
        <Toaster />
        <div className="loading-box">
          <div className="spinner"></div>
          <p>Cargando correo...</p>
        </div>
      </main>
    );

  if (!correo)
    return (
      <main className="detalle">
        <Toaster />
        <p className="error">{error || "Correo no encontrado."}</p>
      </main>
    );

  return (
    <main className="detalle">
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

      <div className="box">
        <h2>{correo.subject}</h2>

        <p>
          <b>Fecha:</b> {correo.date}
        </p>
        <p>
          <b>Remitente:</b> {correo.from}
        </p>

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

        {/* RESPUESTA PREVIA */}
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

        {/* BOTÓN GENERAR */}
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

        {/* LOADING IA */}
        {loadingIA && (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>🧠 Generando respuesta IA...</p>
          </div>
        )}

        {/* EDITAR RESPUESTA */}
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
