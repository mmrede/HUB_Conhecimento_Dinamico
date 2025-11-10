# Hub de Conhecimento Dinâmico
## Dynamic Knowledge Hub

### 🎯 Visão Geral | Overview

O **Hub de Conhecimento Dinâmico** é uma solução completa de gestão de conhecimento (GC) projetada para organizações complexas, especialmente no setor público. O sistema aborda o desafio crítico de converter vastos repositórios de dados em conhecimento estratégico acionável.

The **Dynamic Knowledge Hub** is a comprehensive knowledge management (KM) solution designed for complex organizations, especially in the public sector. The system addresses the critical challenge of converting vast data repositories into actionable strategic knowledge.

### ✨ Características Principais | Key Features

- **📥 Ingestão Multi-Formato**: Suporte para TXT, PDF, DOCX, CSV, JSON, XML
- **🤖 Processamento Inteligente**: Extração automática de conceitos-chave, entidades e relacionamentos
- **🔍 Busca Avançada**: Motor de busca com suporte fuzzy e busca por conceitos
- **📊 Analytics e Insights**: Geração automática de insights e recomendações estratégicas
- **🏷️ Categorização Automática**: Tags e categorização automática baseada em conteúdo
- **🌐 API REST**: Interface de programação completa para integração
- **💡 Interface CLI**: Ferramenta de linha de comando para operações rápidas

### 🏗️ Arquitetura | Architecture

```
src/hub_conhecimento/
├── core/           # Modelos e configuração centrais
│   ├── models.py   # Modelo de documento de conhecimento
│   └── config.py   # Gerenciamento de configuração
├── data/           # Ingestão de dados
│   └── ingestion.py
├── processing/     # Processamento de conhecimento
│   └── processor.py
├── search/         # Motor de busca
│   └── engine.py
├── analytics/      # Analytics e insights
│   └── insights.py
└── api/            # API REST
    └── app.py
```

### 🚀 Início Rápido | Quick Start

#### Instalação | Installation

```bash
# Clone o repositório
git clone https://github.com/mmrede/HUB_Conhecimento_Dinamico.git
cd HUB_Conhecimento_Dinamico

# Instale as dependências
pip install -r requirements.txt

# Configure o ambiente (opcional)
cp .env.example .env
# Edite .env com suas configurações
```

#### Uso Básico | Basic Usage

**1. Ingestão de Documentos | Document Ingestion**

```bash
# Ingerir um único arquivo
python src/main.py ingest data/raw/documento.txt --category administrative

# Ingerir diretório completo
python src/main.py ingest data/raw/ --recursive
```

**2. Busca de Conhecimento | Knowledge Search**

```bash
# Buscar documentos
python src/main.py search "gestão pública" --category administrative --max-results 10
```

**3. Gerar Analytics | Generate Analytics**

```bash
# Gerar insights
python src/main.py analytics

# Salvar em arquivo
python src/main.py analytics --output analytics.json
```

**4. Iniciar API Server | Start API Server**

```bash
# Iniciar servidor
python src/main.py serve --host 0.0.0.0 --port 5000

# Com debug
python src/main.py serve --debug
```

### 📡 API Endpoints

#### Health Check
```http
GET /health
```

#### Ingestão de Documento | Document Ingestion
```http
POST /api/documents
Content-Type: application/json

{
  "title": "Política de Gestão",
  "content": "Conteúdo do documento...",
  "category": "administrative",
  "tags": ["política", "gestão"],
  "author": "João Silva",
  "department": "Administração"
}
```

#### Busca | Search
```http
GET /api/search?q=gestão&category=administrative&max_results=20
```

#### Busca por Conceito | Concept Search
```http
GET /api/search/concepts?concept=planejamento&max_results=20
```

#### Analytics e Insights
```http
GET /api/analytics/insights
```

#### Obter Documento | Get Document
```http
GET /api/documents/{doc_id}
```

#### Listar Categorias | List Categories
```http
GET /api/categories
```

### ⚙️ Configuração | Configuration

O sistema usa `config.yaml` para configuração centralizada:

```yaml
# Processamento de Conhecimento
processing:
  language: pt  # Portuguese
  confidence_threshold: 0.7
  max_document_size_mb: 50
  supported_formats:
    - pdf
    - docx
    - txt
    - csv
    - json
    - xml

# Categorização
categorization:
  auto_tagging: true
  max_tags_per_document: 10
  categories:
    - administrative
    - legal
    - financial
    - human_resources
    - operations
    - strategic_planning
    - technology
    - compliance
```

### 🎨 Casos de Uso | Use Cases

#### 1. Setor Público | Public Sector
- Organização de regulamentos e políticas
- Gestão de conhecimento legal e compliance
- Análise de documentos administrativos
- Compartilhamento de melhores práticas entre departamentos

#### 2. Organizações Complexas | Complex Organizations
- Centralização de conhecimento distribuído
- Descoberta de expertise interna
- Análise de tendências e padrões
- Tomada de decisão baseada em dados

### 📊 Exemplo de Insights Gerados | Example Generated Insights

```json
{
  "total_documents": 150,
  "categories_distribution": {
    "administrative": 45,
    "legal": 30,
    "financial": 25,
    "strategic_planning": 50
  },
  "top_tags": [
    {"tag": "gestão", "count": 67},
    {"tag": "planejamento", "count": 45},
    {"tag": "orçamento", "count": 38}
  ],
  "knowledge_coverage": {
    "unique_categories": 8,
    "unique_tags": 156,
    "average_confidence_score": 0.82,
    "coverage_score": 0.75
  },
  "recommendations": [
    "Repositório de conhecimento em bom estado.",
    "Continue adicionando e atualizando documentos."
  ]
}
```

### 🔧 Desenvolvimento | Development

#### Estrutura de Dados | Data Structure

O sistema utiliza o modelo `KnowledgeDocument`:

```python
from hub_conhecimento.core.models import KnowledgeDocument, DocumentType

document = KnowledgeDocument(
    id="unique_id",
    title="Título do Documento",
    content="Conteúdo...",
    document_type=DocumentType.POLICY,
    category="administrative",
    tags=["tag1", "tag2"],
    author="Autor",
    department="Departamento"
)
```

#### Processamento Customizado | Custom Processing

```python
from hub_conhecimento.processing.processor import KnowledgeProcessor

processor = KnowledgeProcessor(language='pt', confidence_threshold=0.7)
processed_doc = processor.process_document(document)

print(f"Key Concepts: {processed_doc.key_concepts}")
print(f"Entities: {processed_doc.entities}")
print(f"Confidence: {processed_doc.confidence_score}")
```

### 🤝 Contribuindo | Contributing

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### 📄 Licença | License

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

### 🙏 Agradecimentos | Acknowledgments

- Desenvolvido para resolver desafios reais de gestão de conhecimento no setor público
- Inspirado pelas necessidades de organizações complexas
- Focado em converter dados em conhecimento acionável

### 📞 Suporte | Support

Para questões e suporte:
- Abra uma issue no GitHub
- Entre em contato através do repositório

---

**Transformando dados em conhecimento estratégico acionável.**  
**Transforming data into actionable strategic knowledge.**