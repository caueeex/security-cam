#!/bin/bash

# Script para iniciar o Sistema de Segurança Inteligente

echo "🚀 Iniciando Sistema de Segurança Inteligente..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p models data logs

# Copiar arquivos de configuração se não existirem
if [ ! -f backend/.env ]; then
    echo "📋 Copiando configurações do backend..."
    cp backend/env.example backend/.env
fi

if [ ! -f ai-engine/.env ]; then
    echo "📋 Copiando configurações do AI Engine..."
    cp ai-engine/env.example ai-engine/.env
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar os serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose up -d --build

# Aguardar os serviços iniciarem
echo "⏳ Aguardando serviços iniciarem..."
sleep 30

# Verificar status dos serviços
echo "📊 Verificando status dos serviços..."
docker-compose ps

# Mostrar URLs de acesso
echo ""
echo "✅ Sistema iniciado com sucesso!"
echo ""
echo "🌐 URLs de acesso:"
echo "   Dashboard:     http://localhost:3000"
echo "   API Backend:  http://localhost:8000/docs"
echo "   AI Engine:    http://localhost:8001/docs"
echo "   Grafana:      http://localhost:3001 (admin/admin)"
echo "   MLflow:       http://localhost:5000"
echo ""
echo "🔐 Credenciais padrão:"
echo "   Usuário: admin"
echo "   Senha:   admin123"
echo ""
echo "📋 Para visualizar logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para parar o sistema:"
echo "   docker-compose down"
echo ""
