import { useEffect, useMemo, useState } from "react";
import "./Bandeja.css";
import { useNavigate } from "react-router-dom";
import { obtenerPerfil, obtenerCorreos } from "../api/gmail"; // 👈 importa tus nuevas funciones

export default function Bandeja() {
  const [tab, setTab] = useState("no-leidos");
  const [q, setQ] = useState("");
  const [correos, setCorreos] = useState([]);
  const [nombreUsuario, setNombreUsuario] = useState("");
  const navegar = useNavigate();

  useEffect(() => {
    // ✅ El backend obtiene el email desde la cookie automáticamente
    obtenerPerfil()
      .then((data) => {
        if (data.error) {
          navegar("/");
        } else {
          setNombreUsuario(data.nombre_usuario);
        }
      })
      .catch((err) => {
        console.error("Error obteniendo perfil:", err);
        navegar("/");
      });

    // ✅ Traer correos
    obtenerCorreos(20, "metadata")
      .then((data) => {
        console.log("Correos recibidos:", data);
        setCorreos(data);
      })
      .catch((err) => console.error("Error obteniendo correos:", err));
  }, []);

  const lista = useMemo(() => {
    const base = correos.filter((c) =>
      tab === "leidos" ? c.leido : !c.leido
    );
    const term = q.trim().toLowerCase();
    if (!term) return base;
    return base.filter((c) =>
      (c.remitente + " " + c.asunto + " " + c.mensaje)
        .toLowerCase()
        .includes(term)
    );
  }, [tab, q, correos]);

  const cerrarSesion = () => {
    // ✅ elimina la cookie del backend (opcionalmente podrías tener endpoint /logout)
    document.cookie = "email=; max-age=0; path=/";
    navegar("/");
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
          <button onClick={cerrarSesion} className="btn-cerrar">
            Cerrar sesión
          </button>
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
      </header>

      <section className="tabla-wrap">
        <table className="tabla">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Remitente</th>
              <th>Asunto</th>
              <th>Mensaje</th>
            </tr>
          </thead>
          <tbody>
            {lista.map((c) => (
              <tr
                key={c.id}
                onClick={() => navegar(`/correo/${c.id}`)}
                style={{ cursor: "pointer" }}
              >
                <td>{c.date}</td>
                <td>{c.from_name}</td>
                <td>{c.subject}</td>
                <td className="msg">{c.snippet}</td>
              </tr>
            ))}
            {lista.length === 0 && (
              <tr>
                <td colSpan="4" className="vacio">
                  Sin resultados
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </main>
  );
}
