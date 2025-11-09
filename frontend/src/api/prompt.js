const API_URL = import.meta.env.VITE_API_URL;

export async function guardarPromptIA(contexto) {
  const res = await fetch(`${API_URL}/ollama/guardar_prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ contexto }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Error al guardar prompt: ${errText}`);
  }

  return await res.json();
}
