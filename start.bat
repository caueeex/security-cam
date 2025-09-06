@echo off
REM Script para iniciar o Sistema de Segurança Inteligente no Windows

echo 🚀 Iniciando Sistema de Segurança Inteligente...

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está instalado. Por favor, instale o Docker primeiro.
    pause
    exit /b 1
)

REM Verificar se Docker Compose está instalado
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro.
    pause
    exit /b 1
)

REM Criar diretórios necessários
echo 📁 Criando diretórios necessários...
if not exist models mkdir models
if not exist data mkdir data
if not exist logs mkdir logs

REM Copiar arquivos de configuração se não existirem
if not exist backend\.env (
    echo 📋 Copiando configurações do backend...
    copy backend\env.example backend\.env
)

if not exist ai-engine\.env (
    echo 📋 Copiando configurações do AI Engine...
    copy ai-engine\env.example ai-engine\.env
)

REM Parar containers existentes
echo 🛑 Parando containers existentes...
docker-compose down

REM Construir e iniciar os serviços
echo 🔨 Construindo e iniciando serviços...
docker-compose up -d --build

REM Aguardar os serviços iniciarem
echo ⏳ Aguardando serviços iniciarem...
timeout /t 30 /nobreak >nul

REM Verificar status dos serviços
echo 📊 Verificando status dos serviços...
docker-compose ps

REM Mostrar URLs de acesso
echo.
echo ✅ Sistema iniciado com sucesso!
echo.
echo 🌐 URLs de acesso:
echo    Dashboard:     http://localhost:3000
echo    API Backend:  http://localhost:8000/docs
echo    AI Engine:    http://localhost:8001/docs
echo    Grafana:      http://localhost:3001 (admin/admin)
echo    MLflow:       http://localhost:5000
echo.
echo 🔐 Credenciais padrão:
echo    Usuário: admin
echo    Senha:   admin123
echo.
echo 📋 Para visualizar logs:
echo    docker-compose logs -f
echo.
echo 🛑 Para parar o sistema:
echo    docker-compose down
echo.
pause
