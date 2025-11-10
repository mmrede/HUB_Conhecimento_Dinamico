# HUB de Conhecimento Dinâmico

Sistema de gestão e busca semântica de parcerias e instrumentos jurídicos, desenvolvido com FastAPI (backend) e React (frontend).

## 🚀 Funcionalidades

- **Busca Semântica Avançada**: Utiliza spaCy e sentence-transformers para busca por similaridade semântica
- **Gestão de Parcerias**: CRUD completo de instrumentos de parceria
- **Dashboard de Qualidade**: Análise e visualização da qualidade das buscas semânticas
- **Exportação de Relatórios**: Geração de relatórios em HTML e PDF

## 🛠️ Tecnologias

### Backend
- Python 3.12+
- FastAPI + Uvicorn
- PostgreSQL 15
- SQLAlchemy 2.0
- spaCy 3.8 (pt_core_news_lg)
- sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- Alembic (migrations)

### Frontend
- React + TypeScript
- Vite
- Material-UI (MUI)
- Axios

## 📋 Pré-requisitos

- Python 3.12 ou superior
- Node.js 18+ e npm
- PostgreSQL 15
- Git

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/mmrede/HUB_Conhecimento_Dinamico.git
cd HUB_Conhecimento_Dinamico
```

### 2. Configure o Backend

```powershell
# Crie e ative o ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instale as dependências
pip install -r requirements.txt

# Baixe o modelo spaCy em português
python -m spacy download pt_core_news_lg

# Configure as variáveis de ambiente
# Crie um arquivo .env com:
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/hub_aura
# SECRET_KEY=sua_chave_secreta_aqui
```

### 3. Configure o Frontend

```powershell
cd hub-aura-frontend
npm install
cd ..
```

### 4. Execute as Migrações

```powershell
alembic upgrade head
```

## ▶️ Execução

### Backend (Terminal 1)

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8002
```

### Frontend (Terminal 2)

```powershell
cd hub-aura-frontend
npm run dev
```

Acesse: http://localhost:5173

## 📊 Scripts Úteis

- `analyze_semantic_search.py`: Análise detalhada de buscas semânticas
- `dashboard_semantic_quality.py`: Dashboard de qualidade com múltiplas consultas
- `generate_pdf.py`: Geração de relatórios em PDF
- `scripts/export_project.ps1`: Exportar projeto para migração
- `scripts/bootstrap_new_machine.ps1`: Bootstrap em nova máquina

## 📁 Estrutura do Projeto

```
hub_aura/
├── app/                    # Código da aplicação backend
├── hub-aura-frontend/      # Código do frontend React
├── migrations/             # Migrações Alembic
├── scripts/                # Scripts utilitários
├── backups/                # Backups de banco e código
├── main.py                 # Ponto de entrada do backend
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```

## 🔐 Segurança

- Nunca commite o arquivo `.env` (já incluído no `.gitignore`)
- Use variáveis de ambiente para credenciais sensíveis
- Configure SECRET_KEY aleatória em produção

## 📝 Licença

[Incluir informação de licença]

## 👥 Contribuição

[Incluir guidelines de contribuição]

## 📧 Contato

[Incluir informações de contato]