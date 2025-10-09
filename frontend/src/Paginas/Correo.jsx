import parse from "html-react-parser";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { obtenerCorreoCompleto, descargarAdjunto } from "../api/gmail";
import "./Correo.css";

export default function DetalleCorreo() {
const { id } = useParams();
const navegar = useNavigate();
const [correo, setCorreo] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

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

if (loading)
    return (
    <main className="detalle">
        <div className="loading-box">
        <div className="spinner"></div>
        <p>Cargando correo...</p>
        </div>
    </main>
    );

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

return (
    <main className="detalle">
    <div className="box">
        <h2>{correo.subject}</h2>
        <p><b>Fecha:</b> {correo.date}</p>
        <p><b>Remitente:</b> {correo.from}</p>

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

        <div className="acciones">
        <button className="btn" onClick={() => navegar("/bandeja")}>
            Volver
        </button>
        <button
            className="btn primario"
            onClick={() => navegar(`/respuesta/${id}`)}
        >
            Generar respuesta
        </button>
        </div>
    </div>
    </main>
);
}
