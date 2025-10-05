export const obtenerPerfil = async () => {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/gmail/perfil_gmail`,
    {
      method: "GET",
      credentials: "include", // 👈 esto envía la cookie al backend
    }
  );
  return response.json();
};

export const obtenerCorreos = async (limit = 10, formato = "metadata") => {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/gmail/correosPreview`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // 👈 también envía la cookie
      body: JSON.stringify({ limit, formato }),
    }
  );
  return response.json();
};

export async function cerrarSesion() {
  await fetch(`${API_URL}/gmail/logout`, {
    method: "POST",
    credentials: "include",
  });
}
