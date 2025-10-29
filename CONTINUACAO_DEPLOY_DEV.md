# 🚀 CONTINUAÇÃO - Deploy DEV e Preparação Multi-Tenant

## 📊 Status Atual

✅ **Completado:**
- Ambiente virtual Python criado
- Dependências instaladas
- Código commitado no GitHub
- Planos de deploy criados
- Tabelas DEV criadas no Supabase (`_dev`)

🔄 **Próximos Passos:**
1. Configurar DNS
2. Build da imagem Docker
3. Deploy no Portainer
4. Criar instância WhatsApp DEV
5. Testar funcionamento

---

## 🎯 ROTEIRO COMPLETO

### **PARTE 1: Deploy do Ambiente DEV** ⏱️ 30 min

#### **Passo 1: Configurar DNS** ⏱️ 2 min

**Acessar painel DNS (GoDaddy/Cloudflare/etc):**
```
Tipo: A
Nome: botdev
Valor: 46.62.155.254
TTL: 3600
```

**Verificar:**
```bash
# Aguardar propagação (1-5 min)
nslookup botdev.automacaovn.shop

# Deve retornar: 46.62.155.254
```

#### **Passo 2: SSH no Servidor** ⏱️ 1 min

```bash
ssh root@46.62.155.254
```

#### **Passo 3: Preparar Diretório** ⏱️ 2 min

```bash
# Criar diretório DEV
mkdir -p /root/whatsapp-bot-dev
cd /root/whatsapp-bot-dev

# Clonar repositório
git clone https://github.com/Viniciushann/Langgraph-projeto-multi-tenart.git .

# Entrar no projeto
cd Langcham-fluxo-atendimento

# Verificar arquivos
ls -la
```

#### **Passo 4: Configurar .env DEV** ⏱️ 3 min

```bash
# Copiar template
cp .env.development .env

# Editar com suas credenciais REAIS
nano .env

# Verificar pontos críticos:
# - REDIS_DB=1  ⚡ CRÍTICO (produção usa 0)
# - PORT=8001
# - ENVIRONMENT=development
# - WHATSAPP_INSTANCE=Landchan-multi-tenant-dev
# - OPENAI_API_KEY=sua-chave-real
```

#### **Passo 5: Build da Imagem** ⏱️ 3 min

```bash
# Build
docker build -t whatsapp-bot-langchain:dev .

# Verificar sucesso
docker images | grep whatsapp-bot

# Deve aparecer:
# whatsapp-bot-langchain   dev     [IMAGE_ID]   [SIZE]
```

#### **Passo 6: Deploy via Docker Stack** ⏱️ 5 min

```bash
# Deploy
docker stack deploy -c docker-compose.dev.final.yml whatsapp-bot-dev

# Aguardar ~30 segundos

# Verificar status
docker stack ps whatsapp-bot-dev

# Ver logs
docker service logs whatsapp-bot-dev_whatsapp-bot-dev --tail 50 -f
```

**Logs esperados:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

#### **Passo 7: Verificar Health** ⏱️ 1 min

```bash
# Health check
curl https://botdev.automacaovn.shop/health

# Resposta esperada:
{
  "status": "healthy",
  "environment": "development",
  "redis": {
    "connected": true,
    "db": 1
  },
  "supabase": {
    "connected": true
  },
  "timestamp": "2025-10-29T..."
}
```

#### **Passo 8: Criar Instância WhatsApp DEV** ⏱️ 3 min

```bash
# Criar instância
curl -X POST https://evolution.centrooestedrywalldry.com.br/instance/create \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "Landchan-multi-tenant-dev",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'

# Resposta deve ter:
# - instance { name: "Landchan-multi-tenant-dev" }
# - qrcode { base64: "..." }
```

**Conectar WhatsApp:**
```bash
# Obter QR Code
curl -X GET https://evolution.centrooestedrywalldry.com.br/instance/qrcode/Landchan-multi-tenant-dev \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"

# Copiar o base64 do QR Code
# Colar em: https://base64.guru/converter/decode/image
# Escanear com WhatsApp do celular
```

#### **Passo 9: Configurar Webhook** ⏱️ 2 min

```bash
# Configurar webhook
curl -X POST https://evolution.centrooestedrywalldry.com.br/webhook/set/Landchan-multi-tenant-dev \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://botdev.automacaovn.shop/webhook",
    "enabled": true,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE"
    ]
  }'

# Verificar configuração
curl -X GET https://evolution.centrooestedrywalldry.com.br/webhook/find/Landchan-multi-tenant-dev \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"
```

#### **Passo 10: Testar Sistema** ⏱️ 5 min

**1. Teste de Webhook:**
```bash
curl -X POST https://botdev.automacaovn.shop/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "Landchan-multi-tenant-dev",
    "data": {
      "key": {
        "remoteJid": "5562999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "TEST123"
      },
      "message": {
        "conversation": "Olá, teste DEV"
      }
    }
  }'
```

**2. Enviar mensagem real:**
- Abra WhatsApp
- Envie mensagem para o número DEV
- Verifique logs:

```bash
docker service logs whatsapp-bot-dev_whatsapp-bot-dev --tail 100 -f
```

**3. Verificar banco de dados:**
```sql
-- No Supabase SQL Editor
SELECT * FROM clients_dev ORDER BY criado_em DESC LIMIT 5;
SELECT * FROM conversation_history_dev ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM stats_dev;
```

---

### **PARTE 2: Preparar Multi-Tenant** ⏱️ 45 min

Agora que o DEV está rodando, vamos implementar a estrutura multi-tenant:

#### **Passo 1: Executar Script Multi-Tenant no Supabase** ⏱️ 10 min

```bash
# No Supabase SQL Editor
# Copiar conteúdo do arquivo FASE_1_ESTRUTURA_MULTI_TENANT.md
# Seções 1, 2, 3 (até RLS)
```

**Script consolidado:**
```sql
-- 1. Criar tabela tenants
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',

    -- Config WhatsApp
    whatsapp_instance TEXT,
    whatsapp_api_url TEXT,
    whatsapp_api_key TEXT,

    -- Config Bot
    config JSONB DEFAULT '{}'::jsonb,
    system_prompt TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Adicionar tenant_id às tabelas existentes
ALTER TABLE clients_dev ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id);
ALTER TABLE conversation_history_dev ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id);
ALTER TABLE conhecimento_dev ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id);

-- 3. Criar índices
CREATE INDEX IF NOT EXISTS idx_clients_dev_tenant ON clients_dev(tenant_id);
CREATE INDEX IF NOT EXISTS idx_conversation_dev_tenant ON conversation_history_dev(tenant_id);
CREATE INDEX IF NOT EXISTS idx_conhecimento_dev_tenant ON conhecimento_dev(tenant_id);

-- 4. Inserir tenant de teste
INSERT INTO tenants (slug, name, whatsapp_instance, config)
VALUES (
    'centro-oeste-dev',
    'Centro Oeste DEV',
    'Landchan-multi-tenant-dev',
    '{
        "message_delay": 10,
        "horario_atendimento": {
            "inicio": "00:00",
            "fim": "23:59"
        }
    }'::jsonb
) RETURNING id;

-- 5. Associar dados existentes ao tenant
UPDATE clients_dev
SET tenant_id = (SELECT id FROM tenants WHERE slug = 'centro-oeste-dev')
WHERE tenant_id IS NULL;

UPDATE conversation_history_dev
SET tenant_id = (SELECT id FROM tenants WHERE slug = 'centro-oeste-dev')
WHERE tenant_id IS NULL;

UPDATE conhecimento_dev
SET tenant_id = (SELECT id FROM tenants WHERE slug = 'centro-oeste-dev')
WHERE tenant_id IS NULL;

-- 6. Verificar
SELECT * FROM tenants;
SELECT tenant_id, COUNT(*) FROM clients_dev GROUP BY tenant_id;
```

#### **Passo 2: Criar Middleware de Tenant** ⏱️ 15 min

**Criar arquivo:** `src/middleware/tenant.py`

```python
"""
Middleware para identificação de tenant
"""

import logging
from typing import Optional
from src.clients.supabase_client import SupabaseClient
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TenantMiddleware:
    """Middleware para identificar tenant por instância WhatsApp"""

    def __init__(self):
        self.supabase = SupabaseClient()
        self._cache = {}

    async def identify_tenant_by_instance(self, instance_name: str) -> Optional[dict]:
        """
        Identifica tenant pela instância WhatsApp

        Args:
            instance_name: Nome da instância (ex: Landchan-multi-tenant-dev)

        Returns:
            Dict com dados do tenant ou None
        """
        # Verificar cache
        if instance_name in self._cache:
            return self._cache[instance_name]

        try:
            # Buscar no banco
            table_name = "tenants" if settings.is_production else "tenants"

            response = self.supabase.client.table(table_name) \
                .select("*") \
                .eq("whatsapp_instance", instance_name) \
                .eq("status", "active") \
                .single() \
                .execute()

            if response.data:
                # Adicionar ao cache
                self._cache[instance_name] = response.data
                logger.info(f"Tenant identificado: {response.data['name']}")
                return response.data

            logger.warning(f"Tenant não encontrado para: {instance_name}")
            return None

        except Exception as e:
            logger.error(f"Erro ao identificar tenant: {e}")
            return None

    def clear_cache(self):
        """Limpa cache de tenants"""
        self._cache.clear()


# Instância global
tenant_middleware = TenantMiddleware()
```

#### **Passo 3: Modificar Nó de Webhook** ⏱️ 10 min

**Editar:** `src/nodes/webhook.py`

```python
# Adicionar import
from src.middleware.tenant import tenant_middleware

async def validar_webhook(state: AgentState) -> AgentState:
    """
    Valida webhook e identifica tenant
    """
    logger.info("="*60)
    logger.info("1️⃣ VALIDAR WEBHOOK")
    logger.info("="*60)

    raw_data = state.get("raw_webhook_data", {})

    # NOVO: Identificar tenant
    instance_name = raw_data.get("instance")
    if instance_name:
        tenant = await tenant_middleware.identify_tenant_by_instance(instance_name)

        if tenant:
            state["tenant_id"] = tenant["id"]
            state["tenant_name"] = tenant["name"]
            state["tenant_config"] = tenant.get("config", {})
            logger.info(f"✅ Tenant: {tenant['name']} ({tenant['slug']})")
        else:
            logger.error(f"❌ Tenant não encontrado: {instance_name}")
            state["next_action"] = AcaoFluxo.END.value
            return state

    # ... resto do código existente ...
```

#### **Passo 4: Atualizar Verificação de Cliente** ⏱️ 5 min

**Editar:** `src/nodes/webhook.py`

```python
async def verificar_cliente(state: AgentState) -> AgentState:
    """
    Verifica se cliente já existe (filtrado por tenant)
    """
    # ... código existente ...

    tenant_id = state.get("tenant_id")
    if not tenant_id:
        logger.error("❌ tenant_id não encontrado no estado")
        state["next_action"] = AcaoFluxo.END.value
        return state

    # Buscar cliente COM filtro de tenant
    cliente = await supabase_client.buscar_cliente(telefone, tenant_id)

    # ... resto do código ...
```

#### **Passo 5: Testar Multi-Tenant** ⏱️ 5 min

**Criar script de teste:**

```bash
# No servidor
cd /root/whatsapp-bot-dev/Langcham-fluxo-atendimento

# Criar test_multi_tenant.py
cat > test_multi_tenant.py << 'EOF'
import asyncio
from src.middleware.tenant import tenant_middleware

async def test():
    print("\n🧪 TESTE MULTI-TENANT\n")

    # Teste 1: Identificar tenant
    tenant = await tenant_middleware.identify_tenant_by_instance(
        "Landchan-multi-tenant-dev"
    )

    if tenant:
        print(f"✅ Tenant: {tenant['name']}")
        print(f"   ID: {tenant['id']}")
        print(f"   Slug: {tenant['slug']}")
        print(f"   Config: {tenant['config']}")
    else:
        print("❌ Tenant não encontrado")

if __name__ == "__main__":
    asyncio.run(test())
EOF

# Executar teste
python test_multi_tenant.py
```

---

## ✅ Checklist Final

### **Deploy DEV:**
- [ ] DNS configurado
- [ ] Código no servidor
- [ ] Imagem Docker buildada
- [ ] Stack deployed
- [ ] Container rodando
- [ ] Instância WhatsApp criada e conectada
- [ ] Webhook configurado
- [ ] Health check OK
- [ ] Teste de mensagem funcionando

### **Multi-Tenant:**
- [ ] Tabela `tenants` criada
- [ ] Coluna `tenant_id` adicionada
- [ ] Tenant de teste inserido
- [ ] Middleware criado
- [ ] Webhook modificado
- [ ] Teste de identificação OK

---

## 🎯 Próximos Passos

1. **Testar isolamento:** Criar 2º tenant e validar separação
2. **Dashboard Admin:** Interface web para gerenciar tenants
3. **API de Gestão:** Endpoints CRUD para tenants
4. **Monitoramento:** Métricas por tenant

---

## 📊 URLs de Acesso

- **DEV Bot:** https://botdev.automacaovn.shop
- **Health:** https://botdev.automacaovn.shop/health
- **API Docs:** https://botdev.automacaovn.shop/docs
- **PROD:** https://bot.automacaovn.shop (não mexer!)

---

**Status:** Em Desenvolvimento
**Última atualização:** Outubro 2025
