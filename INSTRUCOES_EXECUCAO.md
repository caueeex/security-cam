# 🚀 Instruções de Execução - Sistema de Segurança Inteligente

## 📋 Pré-requisitos

Antes de executar o sistema, certifique-se de ter instalado:

- **Docker Desktop** (versão mais recente)
- **Docker Compose** (incluído no Docker Desktop)
- **Git** (para clonar o repositório)

## 🖥️ Execução no Windows

### Método 1: Script Automático (Recomendado)

1. **Execute o script de inicialização**
```cmd
start.bat
```

2. **Aguarde a inicialização completa** (pode levar alguns minutos na primeira execução)

3. **Acesse o dashboard** em http://localhost:3000

### Método 2: Comandos Manuais

1. **Abra o PowerShell como Administrador**

2. **Navegue até o diretório do projeto**
```powershell
cd C:\caminho\para\security-cam
```

3. **Copie os arquivos de configuração**
```powershell
copy backend\env.example backend\.env
copy ai-engine\env.example ai-engine\.env
```

4. **Inicie os serviços**
```powershell
docker-compose up -d --build
```

5. **Verifique o status**
```powershell
docker-compose ps
```

## 🐧 Execução no Linux/macOS

### Método 1: Script Automático

1. **Torne o script executável**
```bash
chmod +x start.sh
```

2. **Execute o script**
```bash
./start.sh
```

### Método 2: Comandos Manuais

1. **Copie os arquivos de configuração**
```bash
cp backend/env.example backend/.env
cp ai-engine/env.example ai-engine/.env
```

2. **Inicie os serviços**
```bash
docker-compose up -d --build
```

## 🌐 URLs de Acesso

Após a inicialização, você pode acessar:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Dashboard** | http://localhost:3000 | Interface principal do sistema |
| **API Backend** | http://localhost:8000/docs | Documentação da API |
| **AI Engine** | http://localhost:8001/docs | Documentação do motor de IA |
| **Grafana** | http://localhost:3001 | Dashboards de monitoramento |
| **MLflow** | http://localhost:5000 | Tracking de experimentos ML |

## 🔐 Credenciais Padrão

- **Usuário**: `admin`
- **Senha**: `admin123`

## 📊 Monitoramento

### Verificar Logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ai-engine
```

### Status dos Serviços
```bash
docker-compose ps
```

### Uso de Recursos
```bash
docker stats
```

## 🛠️ Comandos Úteis

### Parar o Sistema
```bash
docker-compose down
```

### Reiniciar um Serviço
```bash
docker-compose restart backend
```

### Reconstruir um Serviço
```bash
docker-compose up -d --build backend
```

### Limpar Volumes (CUIDADO: Remove dados)
```bash
docker-compose down -v
```

## 🐛 Solução de Problemas

### Problema: Porta já em uso
```bash
# Verificar portas em uso
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Parar processo específico (Windows)
taskkill /PID <PID> /F
```

### Problema: Container não inicia
```bash
# Verificar logs detalhados
docker-compose logs backend

# Verificar espaço em disco
docker system df
```

### Problema: Banco de dados não conecta
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Verificar logs do PostgreSQL
docker-compose logs postgres
```

### Problema: AI Engine não carrega modelos
```bash
# Verificar logs do AI Engine
docker-compose logs ai-engine

# Verificar se há espaço suficiente
docker system df
```

## 🔧 Configurações Avançadas

### Modificar Configurações

1. **Edite os arquivos de configuração**
```bash
# Backend
nano backend/.env

# AI Engine
nano ai-engine/.env
```

2. **Reinicie os serviços**
```bash
docker-compose restart backend ai-engine
```

### Adicionar Câmeras

1. **Acesse o dashboard** em http://localhost:3000
2. **Faça login** com as credenciais padrão
3. **Vá para a seção Câmeras**
4. **Adicione uma nova câmera** com URL RTSP/IP

### Configurar GPU (Opcional)

Se você tem uma GPU NVIDIA com CUDA:

1. **Instale NVIDIA Container Toolkit**
2. **Modifique o docker-compose.yml** para usar GPU
3. **Reinicie os serviços**

## 📈 Performance

### Recursos Recomendados

- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recomendado)
- **Disco**: 50GB+ de espaço livre
- **GPU**: NVIDIA com CUDA (opcional, mas recomendado)

### Otimizações

1. **Ajuste o número de workers** no AI Engine
2. **Configure limites de memória** nos containers
3. **Use SSD** para melhor performance de I/O

## 🚀 Deploy em Produção

Para ambiente de produção:

1. **Configure variáveis de ambiente de produção**
2. **Use HTTPS/TLS**
3. **Configure backup automático**
4. **Monitore com Prometheus/Grafana**
5. **Use Docker Swarm ou Kubernetes**

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** dos serviços
2. **Consulte a documentação** no README.md
3. **Abra uma issue** no GitHub
4. **Verifique os requisitos** do sistema

---

**🎉 Parabéns! Seu Sistema de Segurança Inteligente está rodando!**
