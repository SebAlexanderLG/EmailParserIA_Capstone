export const obtenerPerfil = async (email) => {
  const response = await fetch(`${import.meta.env.VITE_API_URL}/perfil_gmail`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return response.json();
};

export const obtenerCorreos = async (
  email,
  limit = 10,
  formato = "metadata"
) => {
  const response = await fetch(`${import.meta.env.VITE_API_URL}/correos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, limit, formato }),
  });
  return response.json();
};
