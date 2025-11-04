import parse from "html-react-parser";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { obtenerCorreoCompleto } from "../api/gmail";
import { generarRespuestaOllama } from "../api/ollama";
import "./Correo.css";

export default function RespuestaCorreo() {
  const { id } = useParams();
  const navegar = useNavigate();
  const [correo, setCorreo] = useState(null);
  const [respuestaIA, setRespuestaIA] = useState("");
  const [loadingCorreo, setLoadingCorreo] = useState(true);
  const [loadingIA, setLoadingIA] = useState(false);
  const [error, setError] = useState("");

  // 🔹 1. Cargar el correo original
  useEffect(() => {
    setLoadingCorreo(true);
    obtenerCorreoCompleto(id)
      .then((data) => setCorreo(data))
      .catch(() => setError("No se pudo cargar el correo."))
      .finally(() => setLoadingCorreo(false));
  }, [id]);

  // 🔹 2. Generar respuesta IA
  const handleGenerar = async () => {
    setLoadingIA(true);
    try {
      const data = await generarRespuestaOllama({
        mensaje_id: id,
        prompt_key: "respuesta_ia",
      });
      setRespuestaIA(data.respuesta || "Sin respuesta de IA.");
    } catch (err) {
      console.error(err);
      setError("Error generando respuesta IA.");
    } finally {
      setLoadingIA(false);
    }
  };

  // 🔹 3. Mostrar distintos estados de carga
  if (loadingCorreo)
    return (
      <main className="detalle">
        <div className="loading-box">
          <div className="spinner"></div>
          <p>Cargando correo...</p>
        </div>
      </main>
    );

  if (loadingIA)
    return (
      <main className="detalle">
        <div className="loading-box">
          <div className="spinner"></div>
          <p>🧠 Generando respuesta IA...</p>
        </div>
      </main>
    );

  return (
    <main className="detalle">
      <div className="box">
        <h2>{correo.subject}</h2>
        <p>
          <b>Remitente:</b> {correo.from}
        </p>
        <p>
          <b>Fecha:</b> {correo.date}
        </p>

        <div className="mensaje">
          {correo.body_text ? (
            <pre>{correo.body_text}</pre>
          ) : (
            parse(correo.body_html)
          )}
        </div>

        <hr />

        {!respuestaIA ? (
          <div className="acciones">
            <button
              className="btn primario"
              onClick={handleGenerar}
              disabled={loadingIA}
            >
              {loadingIA ? "Generando..." : "Generar respuesta IA"}
            </button>
            <button className="btn" onClick={() => navegar(-1)}>
              Volver
            </button>
          </div>
        ) : (
          <div className="respuesta-ia-box">
            <h3>Respuesta generada:</h3>
            <pre className="respuesta-ia">{respuestaIA}</pre>
            <div className="acciones">
              <button className="btn" onClick={() => navegar(-1)}>
                Volver
              </button>
              <button
                className="btn primario"
                onClick={() => alert("Aquí se enviará el correo")}
              >
                Enviar correo
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
