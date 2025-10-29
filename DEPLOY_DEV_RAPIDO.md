# 🚀 GUIA RÁPIDO - Deploy DEV no Portainer

## ⚡ Deploy em 10 Passos Rápidos

### **Pré-requisitos:**

- ✅ Acesso SSH ao servidor: `ssh root@46.62.155.254`
- ✅ Acesso ao Portainer
- ✅ DNS configurado: `botdev.automacaovn.shop` → `46.62.155.254`

---

## 📋 PASSO A PASSO

### **1️⃣ Configurar DNS** ⏱️ 2 min

```
Adicionar registro DNS:
Tipo: A
Nome: botdev
Valor: 46.62.155.254
TTL: 3600

Resultado: botdev.automacaovn.shop
```

### **2️⃣ SSH no Servidor** ⏱️ 1 min

```bash
ssh root@46.62.155.254
```

### **3️⃣ Criar Diretório DEV** ⏱️ 1 min

```bash
mkdir -p /root/whatsapp-bot-dev
cd /root/whatsapp-bot-dev
```

### **4️⃣ Clonar/Copiar Código** ⏱️ 2 min

```bash
# Opção A: Clonar do GitHub
git clone https://github.com/Viniciushann/Langgraph-projeto-multi-tenart.git .
cd Langcham-fluxo-atendimento

# Opção B: Copiar da produção
cp -r /root/Langcham-fluxo-atendimento /root/whatsapp-bot-dev/
cd /root/whatsapp-bot-dev
```

### **5️⃣ Configurar Supabase DEV** ⏱️ 5 min

```bash
# Acessar Supabase SQL Editor
# Copiar conteúdo de setup_supabase_dev.sql
# Executar no Supabase

# OU usar mesmo Supabase com tabelas _dev (já criadas no script)
```

### **6️⃣ Build da Imagem** ⏱️ 3 min

```bash
cd /root/whatsapp-bot-dev/Langcham-fluxo-atendimento

# Build
docker build -t whatsapp-bot-langchain:dev .

# Verificar
docker images | grep whatsapp-bot
```

### **7️⃣ Criar Stack no Portainer** ⏱️ 5 min

**Via Portainer Web UI:**

1. Acessar Portainer: `https://portainer.seu-dominio.com`
2. Stacks → Add Stack
3. Nome: `whatsapp-bot-dev`
4. Build method: **Web editor**
5. Colar conteúdo de `docker-compose.dev.final.yml`
6. Deploy

**Via CLI (mais rápido):**

```bash
cd /root/whatsapp-bot-dev/Langcham-fluxo-atendimento

# Deploy
docker stack deploy -c docker-compose.dev.final.yml whatsapp-bot-dev

# Verificar
docker stack ps whatsapp-bot-dev
docker service logs whatsapp-bot-dev_whatsapp-bot-dev -f
```

### **8️⃣ Criar Instância WhatsApp DEV** ⏱️ 3 min

```bash
# Criar instância via Evolution API
curl -X POST https://evolution.centrooestedrywalldry.com.br/instance/create \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "Landchan-multi-tenant-dev",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'

# Configurar webhook
curl -X POST https://evolution.centrooestedrywalldry.com.br/webhook/set/Centro_oeste_draywal_DEV \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://botdev.automacaovn.shop/webhook",
    "enabled": true,
    "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE"]
  }'
```

### **9️⃣ Verificar Health** ⏱️ 1 min

```bash
# Health check
curl https://botdev.automacaovn.shop/health

# Resposta esperada:
{
  "status": "healthy",
  "environment": "development",
  "redis_db": 1
}
```

### **🔟 Testar Webhook** ⏱️ 2 min

```bash
# Teste básico
curl -X POST https://botdev.automacaovn.shop/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'

# Enviar mensagem real via WhatsApp
# Verificar logs
docker service logs whatsapp-bot-dev_whatsapp-bot-dev --tail 50
```

---

## ✅ Checklist Rápido

- [ ] DNS configurado (botdev.automacaovn.shop)
- [ ] Código no servidor (/root/whatsapp-bot-dev)
- [ ] Supabase DEV configurado (tabelas \_dev)
- [ ] Imagem buildada (whatsapp-bot-langchain:dev)
- [ ] Stack deployed (whatsapp-bot-dev)
- [ ] Container rodando (verificar Portainer)
- [ ] Instância WhatsApp DEV criada
- [ ] Webhook configurado
- [ ] Health check OK
- [ ] Teste de mensagem OK

---

## 🎯 Diferenças Críticas (PROD vs DEV)

| Item                  | Produção             | Desenvolvimento          |
| --------------------- | -------------------- | ------------------------ |
| **Container**         | whatsapp-bot         | whatsapp-bot-dev         |
| **Porta**             | 8000                 | 8001                     |
| **Domínio**           | bot.automacaovn.shop | botdev.automacaovn.shop  |
| **Redis DB**          | 0                    | **1** ⚡ CRÍTICO         |
| **Supabase**          | Tabelas normais      | Tabelas \_dev            |
| **WhatsApp Instance** | Centro_oeste_draywal | Centro_oeste_draywal_DEV |
| **ENVIRONMENT**       | production           | development              |
| **LOG_LEVEL**         | INFO                 | DEBUG                    |
| **MESSAGE_DELAY**     | 25s                  | 10s                      |
| **CPU**               | 1 core               | 0.5 core                 |
| **RAM**               | 1GB                  | 512MB                    |

---

## 🔧 Comandos Úteis

### **Ver Logs:**

```bash
# Logs em tempo real
docker service logs whatsapp-bot-dev_whatsapp-bot-dev -f

# Últimas 100 linhas
docker service logs whatsapp-bot-dev_whatsapp-bot-dev --tail 100

# Filtrar erros
docker service logs whatsapp-bot-dev_whatsapp-bot-dev 2>&1 | grep ERROR
```

### **Status:**

```bash
# Ver serviços
docker service ls | grep whatsapp-bot

# Ver containers
docker ps | grep whatsapp-bot

# Health check
curl https://botdev.automacaovn.shop/health
```

### **Atualizar DEV:**

```bash
cd /root/whatsapp-bot-dev/Langcham-fluxo-atendimento
git pull
docker build -t whatsapp-bot-langchain:dev .
docker service update --force whatsapp-bot-dev_whatsapp-bot-dev
```

### **Remover DEV:**

```bash
# Remove stack
docker stack rm whatsapp-bot-dev

# Limpar volumes
docker volume rm whatsapp-bot-dev_whatsapp-bot-dev-logs
```

---

## 🐛 Troubleshooting Rápido

### **Container não inicia:**

```bash
# Ver logs de erro
docker service logs whatsapp-bot-dev_whatsapp-bot-dev

# Verificar recursos
docker stats

# Ver eventos
docker service ps whatsapp-bot-dev_whatsapp-bot-dev --no-trunc
```

### **Redis não conecta:**

```bash
# Testar Redis
docker exec -it $(docker ps -q -f name=redis) redis-cli

# Dentro do redis-cli:
SELECT 1   # Trocar para DB 1 (DEV)
KEYS *     # Ver chaves
```

### **SSL não funciona:**

```bash
# Ver logs Traefik
docker service logs traefik_traefik | grep botdev

# Forçar renovação certificado
# (Traefik faz automaticamente em ~1-2 minutos)
```

### **Webhook não recebe:**

```bash
# Verificar webhook configurado
curl -X GET https://evolution.centrooestedrywalldry.com.br/webhook/find/Centro_oeste_draywal_DEV \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"

# Testar endpoint
curl -X POST https://botdev.automacaovn.shop/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

---

## 📊 Monitoramento

### **URLs Importantes:**

- **DEV Bot:** https://botdev.automacaovn.shop
- **Health:** https://botdev.automacaovn.shop/health
- **API Docs:** https://botdev.automacaovn.shop/docs
- **PROD Bot:** https://bot.automacaovn.shop (não mexer!)

### **Portainer:**

Acessar via Portainer para ver:

- Logs em tempo real
- Uso de recursos (CPU/RAM)
- Status do container
- Restart automático

---

## ⚠️ IMPORTANTE

### **NÃO Fazer:**

- ❌ Usar `REDIS_DB=0` no DEV (conflita com PROD)
- ❌ Usar mesma instância WhatsApp
- ❌ Usar mesmo domínio
- ❌ Usar porta 8000
- ❌ Modificar produção acidentalmente

### **SEMPRE Fazer:**

- ✅ Verificar que está em DEV antes de testar
- ✅ Usar `REDIS_DB=1` no DEV
- ✅ Verificar logs após deploy
- ✅ Testar health check
- ✅ Confirmar isolamento de dados

---

## 🎉 Pronto!

**Tempo total:** ~25-30 minutos

**URLs:**

- DEV: https://botdev.automacaovn.shop
- PROD: https://bot.automacaovn.shop

**Próximos passos:**

1. Testar todas as funcionalidades
2. Validar isolamento de dados
3. Desenvolver features no DEV
4. Testar antes de aplicar em PROD

---

**Desenvolvido por:** Vinícius Soutenio
**Data:** Outubro 2025
**Versão:** 1.0
