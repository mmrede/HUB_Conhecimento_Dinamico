# Guia de Implantação | Deployment Guide

## Hub de Conhecimento Dinâmico

### Pré-requisitos | Prerequisites

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- PostgreSQL (opcional, para persistência)
- Elasticsearch (opcional, para busca avançada)

### Instalação em Produção | Production Installation

#### 1. Preparação do Ambiente | Environment Setup

```bash
# Criar diretório de aplicação
mkdir -p /opt/knowledge-hub
cd /opt/knowledge-hub

# Clonar repositório
git clone https://github.com/mmrede/HUB_Conhecimento_Dinamico.git .

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

#### 2. Configuração | Configuration

```bash
# Copiar arquivo de configuração
cp config.yaml config.prod.yaml

# Editar configuração de produção
nano config.prod.yaml
```

**Configurações importantes para produção:**

```yaml
database:
  type: postgresql
  host: db.example.com
  port: 5432
  name: knowledge_hub_prod
  user: khub_user

elasticsearch:
  host: es.example.com
  port: 9200
  index_prefix: khub_prod

api:
  host: 0.0.0.0
  port: 8080
  debug: false
```

#### 3. Variáveis de Ambiente | Environment Variables

```bash
# Criar arquivo .env
cat > .env << EOF
DB_PASSWORD=sua_senha_segura
ES_API_KEY=sua_chave_elasticsearch
API_KEY=sua_chave_api
CONFIG_PATH=/opt/knowledge-hub/config.prod.yaml
EOF

# Proteger arquivo .env
chmod 600 .env
```

#### 4. Inicialização do Banco de Dados | Database Initialization

```bash
# Executar migrations (se disponível)
# python scripts/migrate.py

# Criar índices
# python scripts/create_indexes.py
```

### Opções de Deployment

#### Opção 1: systemd Service

Criar arquivo de serviço:

```bash
sudo nano /etc/systemd/system/knowledge-hub.service
```

Conteúdo:

```ini
[Unit]
Description=Knowledge Hub API Server
After=network.target postgresql.service

[Service]
Type=simple
User=khub
Group=khub
WorkingDirectory=/opt/knowledge-hub
Environment="PATH=/opt/knowledge-hub/venv/bin"
EnvironmentFile=/opt/knowledge-hub/.env
ExecStart=/opt/knowledge-hub/venv/bin/python src/main.py serve --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable knowledge-hub
sudo systemctl start knowledge-hub
sudo systemctl status knowledge-hub
```

#### Opção 2: Docker

Criar `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "src/main.py", "serve", "--host", "0.0.0.0", "--port", "8080"]
```

Criar `docker-compose.yml`:

```yaml
version: '3.8'

services:
  knowledge-hub:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_PASSWORD=${DB_PASSWORD}
      - ES_API_KEY=${ES_API_KEY}
      - API_KEY=${API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=knowledge_hub
      - POSTGRES_USER=khub_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    restart: unless-stopped

volumes:
  postgres_data:
  es_data:
```

Executar:

```bash
docker-compose up -d
```

#### Opção 3: Kubernetes

Criar deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-hub
spec:
  replicas: 3
  selector:
    matchLabels:
      app: knowledge-hub
  template:
    metadata:
      labels:
        app: knowledge-hub
    spec:
      containers:
      - name: knowledge-hub
        image: knowledge-hub:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: khub-secrets
              key: db-password
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: khub-secrets
              key: api-key
```

### Configuração de Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name knowledge-hub.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSL configuration (recommended)
    # listen 443 ssl;
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;
}
```

### Monitoramento | Monitoring

#### Logs

```bash
# Systemd logs
sudo journalctl -u knowledge-hub -f

# Docker logs
docker-compose logs -f knowledge-hub

# Application logs
tail -f logs/application.log
```

#### Health Check

```bash
# Verificar saúde da API
curl http://localhost:8080/health

# Resposta esperada:
# {"status": "healthy", "version": "1.0.0"}
```

### Backup e Recuperação | Backup and Recovery

#### Backup de Dados

```bash
# Backup do banco de dados
pg_dump -U khub_user knowledge_hub > backup_$(date +%Y%m%d).sql

# Backup de documentos
tar -czf documents_$(date +%Y%m%d).tar.gz data/

# Backup de índices Elasticsearch
curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_$(date +%Y%m%d)"
```

#### Restauração

```bash
# Restaurar banco de dados
psql -U khub_user knowledge_hub < backup_20250110.sql

# Restaurar documentos
tar -xzf documents_20250110.tar.gz
```

### Segurança | Security

1. **Autenticação API**: Configure `API_KEY` nas variáveis de ambiente
2. **HTTPS**: Use certificados SSL em produção
3. **Firewall**: Restrinja acesso às portas necessárias
4. **Backups**: Faça backups regulares e teste restauração
5. **Updates**: Mantenha dependências atualizadas

### Manutenção | Maintenance

#### Atualização do Sistema

```bash
# Parar serviço
sudo systemctl stop knowledge-hub

# Atualizar código
git pull origin main

# Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Reiniciar serviço
sudo systemctl start knowledge-hub
```

#### Limpeza de Dados Antigos

```bash
# Remover logs antigos (> 90 dias)
find logs/ -name "*.log" -mtime +90 -delete

# Limpar cache
rm -rf data/cache/*
```

### Troubleshooting

#### Problema: API não inicia

```bash
# Verificar logs
sudo journalctl -u knowledge-hub -n 50

# Verificar configuração
python -c "from src.hub_conhecimento.core.config import get_config; print(get_config())"

# Verificar portas
sudo netstat -tulpn | grep 8080
```

#### Problema: Baixa Performance

```bash
# Verificar recursos
htop

# Verificar conexões de banco
psql -U khub_user -c "SELECT count(*) FROM pg_stat_activity;"

# Otimizar índices
python scripts/optimize_indexes.py
```

### Suporte

Para assistência adicional:
- Documentação: README.md
- Issues: GitHub Issues
- Logs: `/var/log/knowledge-hub/`
