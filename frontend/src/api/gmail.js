const API_URL = import.meta.env.VITE_API_URL;

/* Función para obtener el nombre real del usuario gmail del backend */
export const obtenerPerfil = async () => {
  const response = await fetch(`${API_URL}/gmail/perfil_gmail`, {
    method: "GET",
    credentials: "include", // 👈 esto envía la cookie al backend
  });
  return response.json();
};

/* Función para obtener los correos en vista previa */
export const obtenerCorreos = async (limit = 10, formato = "metadata") => {
  const response = await fetch(`${API_URL}/gmail/correosPreview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // 👈 también envía la cookie
    body: JSON.stringify({ limit, formato }),
  });
  return response.json();
};

/* Función que llama al endpoint de cerrar sesión */
export async function cerrarSesion() {
  await fetch(`${API_URL}/gmail/logout`, {
    method: "POST",
    credentials: "include",
  });
}

/* Función para obtener el correo completo */

export async function obtenerCorreoCompleto(id) {
  const res = await fetch(`${API_URL}/gmail/correos?mensaje_id=${id}`, {
    method: "GET",
    credentials: "include", // importante para enviar cookies HttpOnly
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Error al obtener correo completo: ${errText}`);
  }

  return await res.json();
}
