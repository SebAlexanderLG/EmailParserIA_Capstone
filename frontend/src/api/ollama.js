const API_URL = import.meta.env.VITE_API_URL;

export async function generarRespuestaOllama(payload) {
  const res = await fetch(`${API_URL}/ollama/generar_respuesta_ia`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Error al generar respuesta IA: ${errText}`);
  }

  return await res.json();
}
