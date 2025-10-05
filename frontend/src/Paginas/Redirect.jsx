import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Redirect() {
    const navigate = useNavigate()

    useEffect(() => {
        fetch(`${import.meta.env.VITE_API_URL}/perfil_gmail`, {
            method: "POST",
            credentials: "include"
        })
        .then(res => res.json())
        .then(data => {
            console.log("Usuario autenticado", data);
            navigate("/bandeja");
        })
        .catch(() => {
            navigate("/");
        });
    }, []);

    return <p className="redirect"> Redirigiendo...</p>;
}