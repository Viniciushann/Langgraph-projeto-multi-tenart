# 🚀 PLANO DE DEPLOY - Ambiente DEV no Portainer

## 📊 Análise da Infraestrutura Atual

### ✅ Recursos Disponíveis no Servidor Hetzner

**Sistema:**
- OS: Ubuntu Linux (Kernel 5.15.0-151)
- Uptime: 19 dias
- Load: 0.55 (saudável)

**Armazenamento:**
- Total: 38GB
- Usado: 12GB (34%)
- **Disponível: 24GB** ✅ Suficiente

**Memória RAM:**
- Total: 3.7GB
- Usada: 1.8GB (49%)
- **Disponível: 1.4GB** ⚠️ Moderado
- Swap: Não configurado

**Containers Ativos:**
1. **whatsapp-bot** (PRODUÇÃO) - porta 8000
2. **Evolution API** - porta 8080
3. **n8n** (3 instâncias)
4. **Traefik** (Reverse Proxy) - portas 80/443
5. **PostgreSQL** (Banco de dados)
6. **Redis** (Cache)
7. **Portainer**

---

## 🎯 Estratégia de Deploy DEV

### **Objetivo:** Subir ambiente DEV sem conflitar com produção

### **Princípios:**
1. ✅ **Isolamento completo** de dados
2. ✅ **Usar recursos compartilhados** (Redis, Traefik) com configuração diferente
3. ✅ **Domínio separado** para DEV
4. ✅ **Banco de dados isolado** no Supabase
5. ✅ **Instância WhatsApp separada** (se possível)

---

## 🔧 Configuração Recomendada

### **Opção 1: Usar Mesmo Redis com DB Diferente** ⭐ **RECOMENDADO**

#### **Por que funciona:**
- Redis tem **16 bancos de dados** (0-15)
- **Produção** usa `REDIS_DB=0`
- **DEV** usa `REDIS_DB=1`
- **Isolamento total** de dados
- **Zero conflito**

#### **Vantagens:**
✅ Não precisa criar nova stack Redis
✅ Economia de recursos (RAM)
✅ Mesma rede Docker
✅ Configuração simples

#### **Desvantagens:**
⚠️ Se Redis cair, ambos ambientes param
⚠️ Compartilham limite de memória do Redis

---

### **Opção 2: Criar Stack Redis Separada**

#### **Por que funciona:**
- Redis isolado para DEV
- Independência total
- Mais segurança

#### **Vantagens:**
✅ Isolamento completo
✅ DEV não afeta produção
✅ Pode ter configurações diferentes

#### **Desvantagens:**
⚠️ Consome mais RAM (~50-100MB)
⚠️ Mais uma stack no Portainer
⚠️ Configuração de rede adicional

---

## 📋 PLANO DE DEPLOY - PASSO A PASSO

### **FASE 1: Preparação no Supabase** ⏱️ 15 minutos

#### 1.1 Criar Banco de Dados DEV no Supabase

**Opção A: Usar mesmo projeto com sufixo `_dev`**
```sql
-- Criar tabelas com sufixo _dev
CREATE TABLE clients_dev (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT,
    telefone TEXT UNIQUE NOT NULL,
    email TEXT,
    empresa TEXT,
    dados_adicionais JSONB,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conversation_history_dev (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients_dev(id),
    mensagem TEXT,
    role TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

CREATE TABLE conhecimento_dev (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titulo TEXT,
    conteudo TEXT,
    embedding VECTOR(1536),
    metadata JSONB,
    criado_em TIMESTAMP DEFAULT NOW()
);
```

**Opção B: Criar projeto Supabase separado** (Recomendado para isolamento total)
- Criar novo projeto: `langcham-dev`
- Rodar migrations completas
- Novo URL e KEY

#### 1.2 Gerar Embeddings DEV (se necessário)
```bash
# Conectar no servidor e rodar script
python gerar_embeddings.py --env dev
```

---

### **FASE 2: Configurar Variáveis de Ambiente** ⏱️ 10 minutos

Criar arquivo `.env.development`:

```env
# ========================================
# AMBIENTE DE DESENVOLVIMENTO
# ========================================

# ========== EVOLUTION API ==========
# OPÇÃO 1: Usar mesma instância (cuidado!)
WHATSAPP_API_URL=https://evolution.centrooestedrywalldry.com.br
WHATSAPP_API_KEY=8773E1C40430-4626-B896-1302789BA4D9
WHATSAPP_INSTANCE=Centro_oeste_draywal_DEV  # ⚠️ Criar nova instância!

# OPÇÃO 2: Usar Evolution API separada (recomendado)
# WHATSAPP_API_URL=https://evolution-dev.seu-dominio.com
# WHATSAPP_API_KEY=sua-chave-dev
# WHATSAPP_INSTANCE=bot_dev

# ========== OPENAI API ==========
OPENAI_API_KEY=sua-chave-openai-aqui

# ========== SUPABASE DEV ==========
# Usar projeto separado ou mesmo com tabelas _dev
SUPABASE_URL=https://seu-projeto-dev.supabase.co
SUPABASE_KEY=sua-chave-dev

# ========== REDIS (Mesmo servidor, DB diferente) ==========
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=1  # ⭐ DIFERENTE DE PRODUÇÃO (que usa 0)

# ========== POSTGRESQL (Supabase DEV) ==========
POSTGRES_CONNECTION_STRING=postgresql://postgres:senha@db.seu-projeto-dev.supabase.co:5432/postgres?sslmode=require

# ========== GOOGLE CALENDAR ==========
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=seu-calendario-dev@gmail.com

# ========== CONFIGURAÇÕES DO BOT ==========
BOT_PHONE_NUMBER=5562999999999  # Número de teste
MESSAGE_GROUP_DELAY=10  # Menor delay para testes
MAX_FRAGMENT_SIZE=300

# ========== CONFIGURAÇÕES DO AGENTE ==========
AGENT_TIMEOUT=60
MAX_RETRIES=3
ENABLE_MEMORY_PERSISTENCE=True

# ========== APLICAÇÃO ==========
ENVIRONMENT=development  # ⚠️ IMPORTANTE
PORT=8001  # ⚠️ PORTA DIFERENTE DE PRODUÇÃO
HOST=0.0.0.0
LOG_LEVEL=DEBUG  # Mais verboso para debug

# ========== SEGURANÇA ==========
SECRET_KEY=dev-secret-key-apenas-para-desenvolvimento
CORS_ORIGINS=*

# ========== TRAEFIK (para SSL) ==========
DOMAIN=botdev.automacaovn.shop  # ⚠️ DOMÍNIO DIFERENTE
```

---

### **FASE 3: Criar docker-compose para DEV** ⏱️ 15 minutos

Criar `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  whatsapp-bot-dev:
    image: whatsapp-bot-langchain:dev
    build:
      context: .
      dockerfile: Dockerfile
    container_name: whatsapp-bot-dev
    restart: unless-stopped

    # Variáveis de ambiente
    environment:
      # Evolution API
      - WHATSAPP_API_URL=${WHATSAPP_API_URL}
      - WHATSAPP_API_KEY=${WHATSAPP_API_KEY}
      - WHATSAPP_INSTANCE=${WHATSAPP_INSTANCE}

      # OpenAI
      - OPENAI_API_KEY=${OPENAI_API_KEY}

      # Supabase DEV
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}

      # Redis (mesmo servidor, DB diferente)
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD:-}
      - REDIS_DB=1  # ⭐ DEV usa DB 1

      # PostgreSQL (Supabase DEV)
      - POSTGRES_CONNECTION_STRING=${POSTGRES_CONNECTION_STRING}

      # Google Calendar
      - GOOGLE_CALENDAR_CREDENTIALS_FILE=/app/credentials.json

      # Configurações do Bot
      - BOT_PHONE_NUMBER=${BOT_PHONE_NUMBER}
      - MESSAGE_GROUP_DELAY=${MESSAGE_GROUP_DELAY:-10}
      - MAX_FRAGMENT_SIZE=${MAX_FRAGMENT_SIZE:-300}

      # Configurações do Agente
      - AGENT_TIMEOUT=${AGENT_TIMEOUT:-60}
      - MAX_RETRIES=${MAX_RETRIES:-3}
      - ENABLE_MEMORY_PERSISTENCE=${ENABLE_MEMORY_PERSISTENCE:-True}

      # Aplicação
      - ENVIRONMENT=development
      - PORT=8001  # ⚠️ Porta diferente
      - HOST=0.0.0.0
      - LOG_LEVEL=DEBUG

      # Segurança
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS:-*}

    # Volumes
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./token.json:/app/token.json
      - whatsapp-bot-dev-logs:/app/logs

    # Portas
    ports:
      - "8001:8001"  # ⚠️ Porta diferente de produção

    # Networks (usar as mesmas do servidor)
    networks:
      - traefik-public
      - redis_default

    # Labels para Traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whatsapp-bot-dev.rule=Host(`botdev.${DOMAIN}`)"
      - "traefik.http.routers.whatsapp-bot-dev.entrypoints=websecure"
      - "traefik.http.routers.whatsapp-bot-dev.tls.certresolver=letsencrypt"
      - "traefik.http.services.whatsapp-bot-dev.loadbalancer.server.port=8001"
      - "traefik.docker.network=traefik-public"

    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    # Recursos (menores que produção)
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

# Networks (usar as existentes)
networks:
  traefik-public:
    external: true
  redis_default:
    external: true

# Volumes
volumes:
  whatsapp-bot-dev-logs:
    driver: local
```

---

### **FASE 4: Configurar DNS** ⏱️ 5 minutos

Adicionar registro DNS:

```
Tipo: A
Nome: botdev
Valor: 46.62.155.254
TTL: 3600
```

Resultado: `botdev.automacaovn.shop` → `46.62.155.254`

---

### **FASE 5: Build e Deploy no Portainer** ⏱️ 20 minutos

#### 5.1 Preparar arquivos no servidor

```bash
# SSH no servidor
ssh root@46.62.155.254

# Criar diretório para DEV
mkdir -p /root/whatsapp-bot-dev
cd /root/whatsapp-bot-dev

# Clonar ou copiar código
git clone https://github.com/Viniciushann/Langgraph-projeto-multi-tenart.git .
cd Langcham-fluxo-atendimento

# Copiar .env.development para .env
cp .env.development .env

# Editar variáveis reais
nano .env
```

#### 5.2 Build da imagem

```bash
# Build da imagem DEV
docker build -t whatsapp-bot-langchain:dev .

# Verificar imagem
docker images | grep whatsapp-bot
```

#### 5.3 Deploy via Portainer

**Opção A: Via Portainer Web UI**
1. Acessar Portainer
2. Stacks → Add Stack
3. Nome: `whatsapp-bot-dev`
4. Colar conteúdo de `docker-compose.dev.yml`
5. Environment variables: colar `.env`
6. Deploy

**Opção B: Via Docker Swarm (CLI)**
```bash
# Deploy
docker stack deploy -c docker-compose.dev.yml whatsapp-bot-dev

# Verificar
docker stack ps whatsapp-bot-dev
docker service logs whatsapp-bot-dev_whatsapp-bot-dev -f
```

---

### **FASE 6: Configurar Webhook Evolution API** ⏱️ 10 minutos

#### 6.1 Criar nova instância DEV (recomendado)

```bash
# Criar instância via Evolution API
curl -X POST https://evolution.centrooestedrywalldry.com.br/instance/create \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "Centro_oeste_draywal_DEV",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

#### 6.2 Configurar webhook

```bash
# Configurar webhook para DEV
curl -X POST https://evolution.centrooestedrywalldry.com.br/webhook/set/Centro_oeste_draywal_DEV \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://botdev.automacaovn.shop/webhook",
    "enabled": true,
    "events": [
      "QRCODE_UPDATED",
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "SEND_MESSAGE"
    ]
  }'
```

---

### **FASE 7: Testes e Validação** ⏱️ 15 minutos

#### 7.1 Health Check

```bash
# Verificar se está rodando
curl https://botdev.automacaovn.shop/health

# Resposta esperada:
{
  "status": "healthy",
  "environment": "development",
  "redis_db": 1,
  "timestamp": "2025-10-29..."
}
```

#### 7.2 Testar endpoint de teste

```bash
# Enviar mensagem de teste
curl -X POST https://botdev.automacaovn.shop/test/message \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5562999999999",
    "message": "Teste DEV"
  }'
```

#### 7.3 Verificar logs

```bash
# Ver logs do container
docker service logs whatsapp-bot-dev_whatsapp-bot-dev -f

# Ou via Portainer
# Logs → whatsapp-bot-dev
```

#### 7.4 Testar webhook real

Enviar mensagem WhatsApp para o número DEV e verificar:
- ✅ Webhook recebido
- ✅ Processamento no grafo
- ✅ Resposta enviada
- ✅ Dados salvos no Supabase DEV
- ✅ Não afetou produção

---

## 🔒 Checklist de Segurança e Isolamento

### **Dados Isolados:**
- [ ] Supabase DEV separado ou tabelas `_dev`
- [ ] Redis DB 1 (produção usa 0)
- [ ] PostgreSQL connection string DEV
- [ ] Knowledge base separada

### **Infraestrutura Isolada:**
- [ ] Domínio diferente: `botdev.automacaovn.shop`
- [ ] Porta diferente: 8001 (produção usa 8000)
- [ ] Container name diferente: `whatsapp-bot-dev`
- [ ] Stack/Service diferente no Portainer

### **Configurações Diferentes:**
- [ ] ENVIRONMENT=development
- [ ] LOG_LEVEL=DEBUG
- [ ] Delays menores para testes
- [ ] CORS mais permissivo

### **Instância WhatsApp:**
- [ ] Criar instância separada: `Centro_oeste_draywal_DEV`
- [ ] Webhook apontando para DEV
- [ ] Número de teste diferente

---

## 📊 Comparação: PROD vs DEV

| Aspecto | PRODUÇÃO | DESENVOLVIMENTO |
|---------|----------|-----------------|
| **Domínio** | bot.automacaovn.shop | botdev.automacaovn.shop |
| **Porta** | 8000 | 8001 |
| **Container** | whatsapp-bot | whatsapp-bot-dev |
| **Redis DB** | 0 | 1 |
| **Supabase** | Projeto PROD | Projeto DEV |
| **Evolution Instance** | Centro_oeste_draywal | Centro_oeste_draywal_DEV |
| **LOG_LEVEL** | INFO | DEBUG |
| **MESSAGE_DELAY** | 25s | 10s |
| **Recursos CPU** | 1 core | 0.5 core |
| **Recursos RAM** | 1GB | 512MB |
| **ENVIRONMENT** | production | development |

---

## ⚠️ Alertas e Cuidados

### **Recursos do Servidor:**
- ⚠️ RAM disponível: **1.4GB**
- ⚠️ DEV vai consumir: **~512MB**
- ⚠️ **Restará ~900MB** para sistema
- ✅ **Recomendação:** Monitorar uso de RAM
- 💡 **Solução:** Se precisar, reduzir workers ou aumentar RAM

### **Redis Compartilhado:**
- ⚠️ Se Redis cair, **ambos ambientes param**
- ✅ **Mitigação:** Redis é estável, baixo risco
- 💡 **Alternativa:** Criar Redis separado se necessário

### **Custos OpenAI:**
- ⚠️ DEV usará **mesma API Key** que produção
- ⚠️ **Custos somados** na mesma conta
- 💡 **Solução:** Usar API Key separada para DEV com rate limits

### **Evolution API:**
- ⚠️ Criar instância DEV **consome licença**
- ✅ Verificar se plano suporta múltiplas instâncias
- 💡 Alternativa: Usar mesma instância (não recomendado)

---

## 🚀 Comandos Rápidos

### **Deploy completo:**
```bash
# 1. SSH
ssh root@46.62.155.254

# 2. Ir para diretório DEV
cd /root/whatsapp-bot-dev/Langcham-fluxo-atendimento

# 3. Pull latest
git pull origin main

# 4. Build
docker build -t whatsapp-bot-langchain:dev .

# 5. Deploy
docker stack deploy -c docker-compose.dev.yml whatsapp-bot-dev

# 6. Ver logs
docker service logs whatsapp-bot-dev_whatsapp-bot-dev -f
```

### **Atualizar DEV:**
```bash
cd /root/whatsapp-bot-dev/Langcham-fluxo-atendimento
git pull
docker build -t whatsapp-bot-langchain:dev .
docker service update --force whatsapp-bot-dev_whatsapp-bot-dev
```

### **Ver status:**
```bash
# Serviços
docker service ls | grep whatsapp-bot

# Logs
docker service logs whatsapp-bot-dev_whatsapp-bot-dev --tail 100

# Health
curl https://botdev.automacaovn.shop/health
```

### **Remover DEV:**
```bash
# Remove stack completo
docker stack rm whatsapp-bot-dev

# Limpar volumes (cuidado!)
docker volume rm whatsapp-bot-dev_whatsapp-bot-dev-logs
```

---

## ✅ Checklist Final de Deploy

### **Pré-Deploy:**
- [ ] Supabase DEV configurado
- [ ] Tabelas criadas
- [ ] Embeddings gerados (se necessário)
- [ ] DNS configurado (botdev.automacaovn.shop)
- [ ] .env.development criado e validado
- [ ] docker-compose.dev.yml criado

### **Deploy:**
- [ ] Código no servidor
- [ ] Imagem Docker buildada
- [ ] Stack deployed no Portainer
- [ ] Container rodando (healthy)
- [ ] Health check passando

### **Pós-Deploy:**
- [ ] Webhook Evolution configurado
- [ ] Teste de mensagem funcionando
- [ ] Logs sem erros
- [ ] Produção não afetada
- [ ] Monitoramento ativo

---

## 📞 Suporte e Troubleshooting

### **Problema: Container não inicia**
```bash
# Ver logs
docker service logs whatsapp-bot-dev_whatsapp-bot-dev

# Verificar recursos
docker stats

# Testar localmente
docker run --rm -it whatsapp-bot-langchain:dev /bin/bash
```

### **Problema: Webhook não recebe mensagens**
```bash
# Verificar webhook configurado
curl -X GET https://evolution.centrooestedrywalldry.com.br/webhook/find/Centro_oeste_draywal_DEV \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"

# Testar endpoint diretamente
curl -X POST https://botdev.automacaovn.shop/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

### **Problema: Redis não conecta**
```bash
# Testar conexão Redis
docker exec -it $(docker ps -q -f name=redis) redis-cli

# Dentro do redis-cli:
SELECT 1  # Trocar para DB 1 (DEV)
KEYS *    # Ver chaves
```

### **Problema: SSL/HTTPS não funciona**
```bash
# Verificar Traefik
docker service logs traefik_traefik | grep botdev

# Forçar renovação certificado
docker exec -it $(docker ps -q -f name=traefik) traefik healthcheck
```

---

## 🎯 Próximos Passos Após Deploy

1. **Testar Funcionalidades:**
   - [ ] Processamento de texto
   - [ ] Transcrição de áudio
   - [ ] Análise de imagem
   - [ ] Agendamento Google Calendar
   - [ ] RAG com base de conhecimento
   - [ ] Notificação de técnicos

2. **Monitoramento:**
   - [ ] Configurar alertas
   - [ ] Dashboard Grafana (opcional)
   - [ ] Logs centralizados

3. **Documentação:**
   - [ ] Atualizar README com URLs DEV
   - [ ] Documentar diferenças PROD/DEV
   - [ ] Criar guia de testes

---

**Tempo Total Estimado:** ~90 minutos (1h30min)

**Desenvolvido por:** Vinícius Soutenio
**Data:** Outubro 2025
**Versão:** 1.0
