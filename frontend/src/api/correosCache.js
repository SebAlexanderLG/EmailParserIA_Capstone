// Cache global para correos (se mantiene mientras la app está abierta)
export const correosCache = {
  lista: null, // Lista completa de correos (bandeja)
  detalle: {}, // Cache por mensaje individual { id: correo }
  timestamp: null, // Marca temporal por si quieres invalidar cache más adelante
};
