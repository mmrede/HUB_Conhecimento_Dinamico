// Configuração da API
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export const API_ENDPOINTS = {
  parcerias: {
    busca: `${API_BASE_URL}/api/v1/parcerias/busca`,
    detalhe: (id: number) => `${API_BASE_URL}/api/v1/parcerias/${id}`,
    criar: `${API_BASE_URL}/api/v1/parcerias`,
    semanticBusca: `${API_BASE_URL}/api/v1/parcerias/semantic-busca`,
  },
  documento: {
    processar: `${API_BASE_URL}/api/v1/processar-documento`,
  },
};
