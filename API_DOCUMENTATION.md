# API Documentation
# Documentação da API

## Hub de Conhecimento Dinâmico

Base URL: `http://localhost:5000` (development)  
Production: `https://api.knowledge-hub.example.com`

### Authentication

A API usa autenticação por chave API (API Key). Inclua a chave no header de cada requisição:

```http
X-API-Key: your_api_key_here
```

---

## Endpoints

### 1. Health Check

Verifica o status da API.

**Endpoint:** `GET /health`

**Resposta de Sucesso (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Exemplo:**
```bash
curl http://localhost:5000/health
```

---

### 2. Ingerir Documento

Adiciona um novo documento ao sistema.

**Endpoint:** `POST /api/documents`

**Headers:**
```
Content-Type: application/json
X-API-Key: your_api_key
```

**Body:**
```json
{
  "title": "Política de Gestão de Documentos",
  "content": "Esta política estabelece diretrizes para...",
  "category": "administrative",
  "tags": ["política", "documentos", "gestão"],
  "author": "João Silva",
  "department": "Administração"
}
```

**Parâmetros:**
- `title` (string, obrigatório): Título do documento
- `content` (string, obrigatório): Conteúdo do documento
- `category` (string, opcional): Categoria do documento
- `tags` (array, opcional): Lista de tags
- `author` (string, opcional): Autor do documento
- `department` (string, opcional): Departamento de origem

**Resposta de Sucesso (201):**
```json
{
  "message": "Document ingested successfully",
  "document_id": "a1b2c3d4e5f6g7h8i9j0",
  "status": "processed",
  "confidence_score": 0.85
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:5000/api/documents \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "title": "Manual de Procedimentos",
    "content": "Este manual descreve os procedimentos...",
    "category": "operations",
    "tags": ["manual", "procedimentos"],
    "author": "Maria Santos"
  }'
```

---

### 3. Buscar Documentos

Busca documentos por texto, categoria ou tags.

**Endpoint:** `GET /api/search`

**Parâmetros de Query:**
- `q` (string, obrigatório): Texto de busca
- `category` (string, opcional): Filtrar por categoria
- `tag` (string, opcional, múltiplo): Filtrar por tags
- `max_results` (integer, opcional): Número máximo de resultados (padrão: 20)

**Resposta de Sucesso (200):**
```json
{
  "query": "gestão pública",
  "total_results": 15,
  "results": [
    {
      "id": "doc123",
      "title": "Manual de Gestão Pública",
      "category": "administrative",
      "tags": ["gestão", "público", "manual"],
      "score": 0.95,
      "snippet": "...gestão pública eficiente requer...",
      "created_at": "2025-01-10T10:30:00",
      "author": "João Silva",
      "department": "Administração"
    }
  ]
}
```

**Exemplos:**
```bash
# Busca simples
curl "http://localhost:5000/api/search?q=gestão"

# Busca com filtros
curl "http://localhost:5000/api/search?q=orçamento&category=financial&max_results=10"

# Busca com múltiplas tags
curl "http://localhost:5000/api/search?q=política&tag=gestão&tag=estratégia"
```

---

### 4. Buscar por Conceito

Busca documentos que contêm um conceito específico.

**Endpoint:** `GET /api/search/concepts`

**Parâmetros de Query:**
- `concept` (string, obrigatório): Conceito a buscar
- `max_results` (integer, opcional): Número máximo de resultados (padrão: 20)

**Resposta de Sucesso (200):**
```json
{
  "concept": "planejamento",
  "total_results": 8,
  "results": [
    {
      "id": "doc456",
      "title": "Planejamento Estratégico 2025",
      "category": "strategic_planning",
      "tags": ["planejamento", "estratégia", "2025"],
      "key_concepts": ["planejamento", "estratégia", "metas", "objetivos"],
      "created_at": "2025-01-05T14:20:00"
    }
  ]
}
```

**Exemplo:**
```bash
curl "http://localhost:5000/api/search/concepts?concept=inovação&max_results=5"
```

---

### 5. Obter Documento Específico

Retorna detalhes completos de um documento.

**Endpoint:** `GET /api/documents/{doc_id}`

**Parâmetros de URL:**
- `doc_id` (string): ID do documento

**Resposta de Sucesso (200):**
```json
{
  "id": "doc123",
  "title": "Manual de Procedimentos",
  "content": "Conteúdo completo do documento...",
  "document_type": "guideline",
  "category": "operations",
  "tags": ["manual", "procedimentos", "operações"],
  "source": "/path/to/source.txt",
  "author": "Maria Santos",
  "department": "Operações",
  "created_at": "2025-01-10T10:00:00",
  "updated_at": "2025-01-10T10:30:00",
  "status": "processed",
  "confidence_score": 0.88,
  "key_concepts": ["procedimento", "operação", "processo"],
  "entities": [
    {"type": "DATE", "value": "10/01/2025"},
    {"type": "ORGANIZATION", "value": "Departamento Operações"}
  ]
}
```

**Resposta de Erro (404):**
```json
{
  "error": "Document not found"
}
```

**Exemplo:**
```bash
curl http://localhost:5000/api/documents/doc123
```

---

### 6. Obter Insights Analíticos

Retorna análises e insights do repositório de conhecimento.

**Endpoint:** `GET /api/analytics/insights`

**Resposta de Sucesso (200):**
```json
{
  "total_documents": 150,
  "categories_distribution": {
    "administrative": 45,
    "legal": 30,
    "financial": 25,
    "operations": 20,
    "strategic_planning": 30
  },
  "top_tags": [
    {"tag": "gestão", "count": 67},
    {"tag": "planejamento", "count": 45},
    {"tag": "orçamento", "count": 38}
  ],
  "top_concepts": [
    {"concept": "processo", "count": 89},
    {"concept": "sistema", "count": 76},
    {"concept": "gestão", "count": 65}
  ],
  "document_types_distribution": {
    "policy": 40,
    "procedure": 35,
    "guideline": 30,
    "report": 25,
    "analysis": 20
  },
  "temporal_distribution": {
    "earliest_document": "2024-01-15T00:00:00",
    "latest_document": "2025-01-10T15:30:00",
    "monthly_distribution": {
      "2024-12": 15,
      "2025-01": 25
    }
  },
  "department_distribution": {
    "Administração": 50,
    "Operações": 40,
    "Financeiro": 30,
    "TI": 30
  },
  "knowledge_coverage": {
    "unique_categories": 8,
    "unique_tags": 156,
    "average_confidence_score": 0.82,
    "documents_with_high_confidence": 120,
    "coverage_score": 0.75
  },
  "recommendations": [
    "Repositório de conhecimento em bom estado.",
    "Continue adicionando e atualizando documentos."
  ]
}
```

**Exemplo:**
```bash
curl http://localhost:5000/api/analytics/insights
```

---

### 7. Listar Categorias Disponíveis

Retorna lista de categorias disponíveis no sistema.

**Endpoint:** `GET /api/categories`

**Resposta de Sucesso (200):**
```json
{
  "categories": [
    "administrative",
    "legal",
    "financial",
    "human_resources",
    "operations",
    "strategic_planning",
    "technology",
    "compliance"
  ]
}
```

**Exemplo:**
```bash
curl http://localhost:5000/api/categories
```

---

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Parâmetros inválidos ou ausentes
- `401 Unauthorized`: Autenticação falhou
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno do servidor

---

## Exemplos de Uso Completos

### Python

```python
import requests

API_URL = "http://localhost:5000"
API_KEY = "your_api_key"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Ingerir documento
document = {
    "title": "Política de Segurança",
    "content": "Esta política define diretrizes de segurança...",
    "category": "compliance",
    "tags": ["segurança", "política"],
    "author": "Carlos Souza"
}

response = requests.post(
    f"{API_URL}/api/documents",
    json=document,
    headers=headers
)
print(response.json())

# Buscar documentos
response = requests.get(
    f"{API_URL}/api/search",
    params={"q": "segurança", "category": "compliance"}
)
print(response.json())

# Obter insights
response = requests.get(f"{API_URL}/api/analytics/insights")
print(response.json())
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:5000';
const API_KEY = 'your_api_key';

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY
};

// Ingerir documento
async function ingestDocument() {
  const document = {
    title: 'Manual de Processos',
    content: 'Este manual descreve...',
    category: 'operations',
    tags: ['manual', 'processos'],
    author: 'Ana Lima'
  };

  const response = await axios.post(
    `${API_URL}/api/documents`,
    document,
    { headers }
  );
  console.log(response.data);
}

// Buscar documentos
async function searchDocuments() {
  const response = await axios.get(
    `${API_URL}/api/search`,
    { params: { q: 'processos', max_results: 10 } }
  );
  console.log(response.data);
}

ingestDocument();
searchDocuments();
```

---

## Rate Limiting

Para proteger o serviço, implementamos rate limiting:

- **Limite**: 100 requisições por minuto por API key
- **Header de resposta**: `X-RateLimit-Remaining`
- **Código de erro**: `429 Too Many Requests`

---

## Suporte

Para questões sobre a API:
- Documentação completa: README.md
- Issues: GitHub Issues
- Email: support@example.com
