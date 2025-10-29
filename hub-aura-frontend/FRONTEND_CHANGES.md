# Mudanças no Frontend - Migração para API na porta 8001

## Arquivos Modificados

### 1. Novo arquivo de configuração
- **`src/config/api.ts`** - Configuração centralizada da API com suporte a variáveis de ambiente

### 2. Arquivos atualizados
- **`vite.config.ts`** - Proxy atualizado de 8000 para 8001
- **`.env`** - Configuração da URL da API
- **`src/App.tsx`** - Importa e usa API_BASE_URL
- **`src/PaginaBusca.tsx`** - Usa API_BASE_URL
- **`src/components/PaginaUpload.tsx`** - Usa API_BASE_URL

## Como usar

### Ambiente de desenvolvimento
O frontend agora usa a variável de ambiente `VITE_API_URL` definida no arquivo `.env`:
```
VITE_API_URL=http://localhost:8001
```

### Para alterar a URL da API
Edite o arquivo `.env` na raiz do projeto frontend:
```env
VITE_API_URL=http://localhost:8001  # Desenvolvimento
# VITE_API_URL=https://api.producao.com  # Produção
```

### Iniciar o frontend
```bash
cd hub-aura-frontend
npm run dev
```

O frontend estará disponível em: http://localhost:5173

## Estrutura da configuração

```typescript
// src/config/api.ts
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
```

## Benefícios

✅ Configuração centralizada  
✅ Fácil migração entre ambientes  
✅ Suporte a variáveis de ambiente  
✅ Menos duplicação de código  
✅ Manutenção simplificada
