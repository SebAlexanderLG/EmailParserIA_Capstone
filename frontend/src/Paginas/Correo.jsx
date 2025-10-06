import parse from "html-react-parser"
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { obtenerCorreoCompleto } from "../api/gmail";
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
        <p>Cargando correo...</p>
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
        </div>+
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
            <div
            className="mensaje"
            >{ parse(correo.body_html )}
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
