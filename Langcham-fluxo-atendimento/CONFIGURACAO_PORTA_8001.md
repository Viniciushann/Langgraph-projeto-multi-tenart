# Configuração de Porta 8001 - WhatsApp Bot

## 🎯 Objetivo

Garantir que o WhatsApp Bot rode na porta **8001** para evitar conflito com outros serviços na porta 8000.

## ✅ Alterações Realizadas

### 1. Configuração do FastAPI (`src/config/settings.py`)

```python
port: int = Field(
    default=8001,  # ✅ Alterado de 8000 para 8001
    description="Porta da aplicação FastAPI",
    ge=1000,
    le=65535
)
```

### 2. Docker Compose (`docker-compose.dev.yml`)

```yaml
environment:
  - PORT=8001 # ✅ Variável de ambiente definida

ports:
  - "8001:8001" # ✅ Mapeamento correto da porta

healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"] # ✅ Health check na porta correta

labels:
  - "traefik.http.services.whatsapp-bot-dev.loadbalancer.server.port=8001" # ✅ Traefik configurado
```

### 3. Scripts de Teste

- ✅ `testar_webhook.py` - já configurado para porta 8001
- ✅ `testar_clinica_odonto.py` - atualizado para porta 8001
- ✅ `iniciar_bot_8001.py` - novo script para iniciar localmente

## 🔧 Como Executar

### Localmente (Desenvolvimento)

```bash
# Método 1: Script personalizado
python iniciar_bot_8001.py

# Método 2: Uvicorn direto
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker (Produção)

```bash
# O docker-compose já está configurado
docker-compose -f docker-compose.dev.yml up -d
```

## 🧪 Como Testar

### 1. Health Check

```bash
curl http://localhost:8001/health
```

### 2. Teste Completo

```bash
python testar_webhook.py
```

### 3. Teste Específico da Clínica

```bash
python testar_clinica_odonto.py
```

## 📡 URLs de Produção

- **Health Check**: https://whatsapp-bot-dev.centrooestedrywalldry.com.br/health
- **Webhook**: https://whatsapp-bot-dev.centrooestedrywalldry.com.br/webhook/whatsapp
- **Docs**: https://whatsapp-bot-dev.centrooestedrywalldry.com.br/docs

## 🚨 Resolução de Problemas

### Erro "All connection attempts failed"

1. Verificar se o bot está rodando: `docker ps | grep whatsapp-bot`
2. Verificar logs: `docker logs whatsapp-bot-dev`
3. Reiniciar serviço: `docker-compose restart whatsapp-bot-dev`

### Conflito de Porta

- ✅ Porta 8000: Outro bot
- ✅ Porta 8001: Este bot (Clínica Odonto Sorriso)

### Verificar Status dos Logs

```bash
# Verificar se está usando porta 8001
docker service logs -f whatsapp-bot-dev_whatsapp-bot-dev --tail 10 | grep "Host:"
```

## 📋 Configuração da Clínica Odonto Sorriso

- **WhatsApp**: 556292935358
- **Evolution Instance**: Landchan-multi-tenant-dev
- **Porta**: 8001
- **Status**: 🟢 ATIVO

## ✅ Confirmação Final

Após as alterações, o sistema deve:

1. Iniciar na porta 8001 ✅
2. Responder health check em `/health` ✅
3. Processar webhooks em `/webhook/whatsapp` ✅
4. Não conflitar com serviços na porta 8000 ✅
