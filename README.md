# Sistema de Segurança Inteligente

Sistema completo de monitoramento de perímetros e detecção automática de intrusões que integra IA, Big Data, Backend, Frontend e Engenharia de Software.

## 🏗️ Arquitetura do Sistema

```
security-cam/
├── backend/                 # API FastAPI + MLOps
├── frontend/               # Dashboard React
├── ai-engine/              # Modelos de Deep Learning
├── big-data/               # Processamento e armazenamento
├── infrastructure/         # Docker, CI/CD, Monitoramento
├── docs/                   # Documentação técnica
└── tests/                  # Testes automatizados
```

## 🚀 Tecnologias Utilizadas

### Backend
- **FastAPI**: API RESTful de alta performance
- **PostgreSQL**: Banco relacional para metadados
- **MongoDB**: Armazenamento de documentos e logs
- **Redis**: Cache e filas de processamento
- **Celery**: Processamento assíncrono

### Inteligência Artificial
- **PyTorch**: Framework de deep learning
- **OpenCV**: Processamento de vídeo
- **YOLO**: Detecção de objetos
- **MLflow**: Versionamento e experimentos
- **Autoencoders**: Detecção de anomalias

### Frontend
- **React 18**: Interface moderna e responsiva
- **TypeScript**: Tipagem estática
- **Material-UI**: Componentes visuais
- **WebSocket**: Comunicação em tempo real
- **Chart.js**: Visualizações de dados

### Big Data
- **Apache Kafka**: Streaming de dados
- **Apache Spark**: Processamento distribuído
- **MinIO**: Armazenamento de objetos
- **Elasticsearch**: Busca e análise

### DevOps & MLOps
- **Docker**: Containerização
- **GitHub Actions**: CI/CD
- **Prometheus**: Monitoramento
- **Grafana**: Dashboards de métricas

## ✨ Funcionalidades Principais

### 🎯 Detecção Inteligente
- Detecção de anomalias em tempo real usando deep learning
- Redução de falsos positivos com autoaprendizagem
- Suporte a multimodalidade (vídeo + sensores)
- Alertas contextuais com explicações

### 📊 Dashboard Operacional
- Feed de vídeo em tempo real
- Timeline de eventos com replay
- Mapas de calor de atividade
- Análise preditiva de padrões

### 🔧 MLOps Integrado
- Versionamento automático de modelos
- Monitoramento de performance
- Retreinamento contínuo
- Governança de dados

## 🛠️ Instalação e Execução

### Pré-requisitos
- Docker e Docker Compose
- Python 3.11+
- Node.js 18+
- CUDA (opcional, para GPU)

### 🚀 Execução Rápida com Docker

1. **Clone o repositório**
```bash
git clone <repository-url>
cd security-cam
```

2. **Configure as variáveis de ambiente**
```bash
# Copie os arquivos de exemplo
cp backend/env.example backend/.env
cp ai-engine/env.example ai-engine/.env

# Edite as configurações conforme necessário
nano backend/.env
nano ai-engine/.env
```

3. **Execute com Docker Compose**
```bash
# Inicie todos os serviços
docker-compose up -d

# Verifique o status dos serviços
docker-compose ps

# Visualize os logs
docker-compose logs -f
```

4. **Acesse as aplicações**
- **Dashboard**: http://localhost:3000
- **API Backend**: http://localhost:8000/docs
- **AI Engine**: http://localhost:8001/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **MLflow**: http://localhost:5000

### 🔧 Desenvolvimento Local

#### Backend
```bash
cd backend

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados
# Certifique-se de que PostgreSQL, MongoDB e Redis estão rodando

# Execute a aplicação
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Instale as dependências
npm install

# Execute a aplicação
npm start
```

#### AI Engine
```bash
cd ai-engine

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python main.py
```

### 📊 Monitoramento

O sistema inclui monitoramento completo com:

- **Prometheus**: Coleta de métricas
- **Grafana**: Dashboards visuais
- **MLflow**: Tracking de experimentos de ML
- **Logs centralizados**: Todos os serviços

### 🔐 Autenticação

Por padrão, o sistema vem com um usuário de demonstração:
- **Usuário**: admin
- **Senha**: admin123

### 📱 API Endpoints Principais

#### Backend API (Porta 8000)
- `GET /api/v1/cameras` - Listar câmeras
- `GET /api/v1/detections` - Listar detecções
- `GET /api/v1/alerts` - Listar alertas
- `POST /api/v1/auth/login` - Autenticação
- `WebSocket /ws/live-feed` - Feed de vídeo em tempo real

#### AI Engine (Porta 8001)
- `POST /detection/process-frame` - Processar frame
- `GET /models/` - Listar modelos
- `GET /health/` - Status de saúde

### 🗄️ Bancos de Dados

- **PostgreSQL** (Porta 5432): Metadados principais
- **MongoDB** (Porta 27017): Logs e documentos
- **Redis** (Porta 6379): Cache e sessões
- **MinIO** (Porta 9000): Armazenamento de objetos
- **Elasticsearch** (Porta 9200): Busca e análise

### 🔄 Processamento de Dados

O sistema processa dados em tempo real usando:

1. **Kafka** para streaming de eventos
2. **Spark** para processamento batch
3. **Redis** para cache de alta velocidade
4. **Elasticsearch** para busca e análise

### 🧪 Testes

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test

# AI Engine
cd ai-engine
pytest tests/ -v
```

### 🚀 Deploy em Produção

1. **Configure variáveis de ambiente de produção**
2. **Use Docker Swarm ou Kubernetes**
3. **Configure SSL/TLS**
4. **Configure backup automático**
5. **Monitore com Prometheus/Grafana**

### 📈 Escalabilidade

O sistema foi projetado para escalar horizontalmente:

- **Backend**: Múltiplas instâncias com load balancer
- **AI Engine**: Processamento distribuído
- **Banco de dados**: Replicação e sharding
- **Cache**: Cluster Redis
- **Armazenamento**: MinIO distribuído

### 🔧 Configurações Avançadas

#### GPU para AI Engine
```bash
# Para usar GPU com CUDA
docker-compose -f docker-compose.gpu.yml up -d
```

#### Clustering
```bash
# Para ambiente de produção com múltiplos nós
docker stack deploy -c docker-compose.prod.yml security-cam
```

### 🐛 Troubleshooting

#### Problemas Comuns

1. **Porta já em uso**
```bash
# Verifique quais portas estão em uso
netstat -tulpn | grep :8000
```

2. **Banco de dados não conecta**
```bash
# Verifique se os containers estão rodando
docker-compose ps
```

3. **AI Engine não inicia**
```bash
# Verifique os logs
docker-compose logs ai-engine
```

### 📚 Documentação Adicional

- [Arquitetura Detalhada](docs/architecture.md)
- [API Reference](docs/api.md)
- [Modelos de IA](docs/ai-models.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing](docs/contributing.md)

### 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

### 🆘 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação
- Verifique os logs do sistema

---

**Desenvolvido com ❤️ para segurança inteligente**
