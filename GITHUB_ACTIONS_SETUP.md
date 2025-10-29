# 🚀 GitHub Actions - Deploy Automático

## 🎯 Objetivo
Configurar CI/CD automático para fazer deploy no servidor Hetzner via GitHub Actions sempre que houver push na branch `main` ou `dev`.

---

## 📋 Passo a Passo Completo

### **PARTE 1: Configurar Secrets no GitHub** ⏱️ 10 min

#### **1.1 Acessar Configurações do Repositório**

1. Acesse: https://github.com/Viniciushann/Langgraph-projeto-multi-tenart
2. Clique em **"Settings"** (no menu superior do repositório)
3. No menu lateral esquerdo, clique em **"Secrets and variables"**
4. Clique em **"Actions"**

#### **1.2 Adicionar Secrets**

Clique em **"New repository secret"** e adicione cada um:

##### **Secret 1: SSH_PRIVATE_KEY**
```
Name: SSH_PRIVATE_KEY
Value: [sua chave SSH privada]
```

**Como obter a chave SSH:**

**Opção A: Gerar nova chave SSH (Recomendado)**
```bash
# No seu computador local
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# Ver a chave PRIVADA (copiar TODO o conteúdo)
cat ~/.ssh/github_actions_deploy

# Ver a chave PÚBLICA
cat ~/.ssh/github_actions_deploy.pub
```

**Opção B: Usar chave existente**
```bash
# Ver sua chave privada atual
cat ~/.ssh/id_rsa
# ou
cat ~/.ssh/id_ed25519
```

**IMPORTANTE:** Copie TODO o conteúdo incluindo:
```
-----BEGIN OPENSSH PRIVATE KEY-----
...todo o conteúdo...
-----END OPENSSH PRIVATE KEY-----
```

##### **Secret 2: SSH_HOST**
```
Name: SSH_HOST
Value: 46.62.155.254
```

##### **Secret 3: SSH_USER**
```
Name: SSH_USER
Value: root
```

##### **Secret 4: SSH_PORT**
```
Name: SSH_PORT
Value: 22
```

##### **Secret 5: OPENAI_API_KEY**
```
Name: OPENAI_API_KEY
Value: [sua-chave-openai-aqui]
# Usar a chave OpenAI do projeto
```

##### **Secret 6: SUPABASE_URL**
```
Name: SUPABASE_URL
Value: https://wmzhbgcqugtctnzyinqw.supabase.co
```

##### **Secret 7: SUPABASE_KEY**
```
Name: SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtemhiZ2NxdWd0Y3RuenlpbnF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3NTQ5NDAsImV4cCI6MjA3NzMzMDk0MH0.pziIBNSJfex-dEJDJ0NeU7awjadoJXg87a8TONc4Xic
```

##### **Secret 8: POSTGRES_CONNECTION_STRING**
```
Name: POSTGRES_CONNECTION_STRING
Value: postgresql://postgres:AcZgZs8oPTFsNQkU@db.wmzhbgcqugtctnzyinqw.supabase.co:5432/postgres?sslmode=require
```

##### **Secret 9: WHATSAPP_API_KEY**
```
Name: WHATSAPP_API_KEY
Value: 8773E1C40430-4626-B896-1302789BA4D9
```

---

### **PARTE 2: Adicionar Chave Pública no Servidor** ⏱️ 5 min

#### **2.1 Copiar Chave Pública**

Se você gerou uma nova chave (Opção A acima):
```bash
# Copiar conteúdo da chave pública
cat ~/.ssh/github_actions_deploy.pub
```

#### **2.2 Adicionar no Servidor**

```bash
# SSH no servidor
ssh root@46.62.155.254

# Adicionar chave ao authorized_keys
echo "ssh-ed25519 AAAAC3... github-actions-deploy" >> ~/.ssh/authorized_keys

# Verificar permissões
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

#### **2.3 Testar Conexão**

No seu computador local:
```bash
# Testar com a nova chave
ssh -i ~/.ssh/github_actions_deploy root@46.62.155.254

# Deve conectar sem pedir senha
```

---

### **PARTE 3: Criar Workflow do GitHub Actions** ⏱️ 15 min

#### **3.1 Criar Estrutura de Diretórios**

```bash
# No seu repositório local
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Landcham projeto multi-tenant"
mkdir -p .github/workflows
```

#### **3.2 Criar Workflow para DEV**

Criar arquivo: `.github/workflows/deploy-dev.yml`

```yaml
name: Deploy DEV

on:
  push:
    branches:
      - dev
    paths:
      - 'Langcham-fluxo-atendimento/**'
      - '.github/workflows/deploy-dev.yml'

  workflow_dispatch:  # Permite executar manualmente

env:
  DEPLOY_PATH: /root/whatsapp-bot-dev/Langcham-fluxo-atendimento

jobs:
  deploy:
    name: Deploy to DEV Server
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      - name: 🔑 Setup SSH
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: 📝 Add server to known_hosts
        run: |
          mkdir -p ~/.ssh
          ssh-keyscan -H ${{ secrets.SSH_HOST }} >> ~/.ssh/known_hosts

      - name: 🚀 Deploy to Server
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} -p ${{ secrets.SSH_PORT }} << 'ENDSSH'
            set -e

            echo "🔄 Atualizando código..."
            cd ${{ env.DEPLOY_PATH }}

            # Pull latest changes
            git fetch origin
            git reset --hard origin/dev

            echo "🐳 Buildando imagem Docker..."
            docker build -t whatsapp-bot-langchain:dev .

            echo "♻️ Atualizando serviço..."
            docker service update --force whatsapp-bot-dev_whatsapp-bot-dev

            echo "✅ Deploy concluído!"

            # Aguardar serviço subir
            sleep 10

            # Verificar saúde
            curl -f http://localhost:8001/health || echo "⚠️ Health check falhou"
          ENDSSH

      - name: 🔍 Verificar Deploy
        run: |
          sleep 5
          response=$(curl -s https://botdev.automacaovn.shop/health)
          echo "Health check response: $response"

          if echo "$response" | grep -q "healthy"; then
            echo "✅ Deploy verificado com sucesso!"
          else
            echo "❌ Health check falhou"
            exit 1
          fi

      - name: 📊 Slack/Discord Notification (Opcional)
        if: always()
        run: |
          if [ "${{ job.status }}" == "success" ]; then
            echo "✅ Deploy DEV bem-sucedido!"
          else
            echo "❌ Deploy DEV falhou!"
          fi
```

#### **3.3 Criar Workflow para PROD**

Criar arquivo: `.github/workflows/deploy-prod.yml`

```yaml
name: Deploy PROD

on:
  push:
    branches:
      - main
    paths:
      - 'Langcham-fluxo-atendimento/**'
      - '.github/workflows/deploy-prod.yml'

  workflow_dispatch:  # Permite executar manualmente

env:
  DEPLOY_PATH: /root/Langcham-fluxo-atendimento

jobs:
  deploy:
    name: Deploy to PROD Server
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      - name: 🔑 Setup SSH
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: 📝 Add server to known_hosts
        run: |
          mkdir -p ~/.ssh
          ssh-keyscan -H ${{ secrets.SSH_HOST }} >> ~/.ssh/known_hosts

      - name: 🚀 Deploy to Server
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} -p ${{ secrets.SSH_PORT }} << 'ENDSSH'
            set -e

            echo "🔄 Atualizando código PROD..."
            cd ${{ env.DEPLOY_PATH }}

            # Pull latest changes
            git fetch origin
            git reset --hard origin/main

            echo "🐳 Buildando imagem Docker..."
            docker build -t whatsapp-bot-langchain:latest .

            echo "♻️ Atualizando serviço..."
            docker service update --force whatsapp-bot_whatsapp-bot

            echo "✅ Deploy PROD concluído!"

            # Aguardar serviço subir
            sleep 15

            # Verificar saúde
            curl -f http://localhost:8000/health || echo "⚠️ Health check falhou"
          ENDSSH

      - name: 🔍 Verificar Deploy
        run: |
          sleep 10
          response=$(curl -s https://bot.automacaovn.shop/health)
          echo "Health check response: $response"

          if echo "$response" | grep -q "healthy"; then
            echo "✅ Deploy PROD verificado com sucesso!"
          else
            echo "❌ Health check PROD falhou"
            exit 1
          fi

      - name: 📊 Notificação
        if: always()
        run: |
          if [ "${{ job.status }}" == "success" ]; then
            echo "✅ Deploy PROD bem-sucedido!"
          else
            echo "❌ Deploy PROD falhou!"
          fi
```

---

### **PARTE 4: Criar Branch DEV** ⏱️ 2 min

```bash
# No repositório local
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Landcham projeto multi-tenant"

# Criar branch dev
git checkout -b dev

# Adicionar workflows
git add .github/workflows/

# Commit
git commit -m "ci: adicionar GitHub Actions para deploy automático"

# Push branch dev
git push -u origin dev

# Voltar para main e adicionar workflows também
git checkout main
git add .github/workflows/
git commit -m "ci: adicionar GitHub Actions para deploy automático"
git push origin main
```

---

### **PARTE 5: Testar Deploy Automático** ⏱️ 5 min

#### **5.1 Fazer Mudança Simples**

```bash
# Editar algum arquivo
cd Langcham-fluxo-atendimento
echo "# Deploy test" >> README.md

# Commit e push para DEV
git checkout dev
git add .
git commit -m "test: testar deploy automático"
git push origin dev
```

#### **5.2 Acompanhar Execução**

1. Acesse: https://github.com/Viniciushann/Langgraph-projeto-multi-tenart/actions
2. Você verá o workflow "Deploy DEV" executando
3. Clique nele para ver os logs em tempo real

**Logs esperados:**
```
📥 Checkout code ✓
🔑 Setup SSH ✓
📝 Add server to known_hosts ✓
🚀 Deploy to Server
   🔄 Atualizando código...
   🐳 Buildando imagem Docker...
   ♻️ Atualizando serviço...
   ✅ Deploy concluído!
🔍 Verificar Deploy
   ✅ Deploy verificado com sucesso!
```

---

## 📊 Estrutura Final de Branches

```
main (PROD)
  ├── .github/workflows/deploy-prod.yml
  └── Langcham-fluxo-atendimento/

dev (DEV)
  ├── .github/workflows/deploy-dev.yml
  └── Langcham-fluxo-atendimento/
```

**Fluxo de Trabalho:**
1. Desenvolver em `dev`
2. Push para `dev` → Deploy automático em DEV
3. Testar em DEV
4. Merge `dev` → `main` → Deploy automático em PROD

---

## 🔐 Secrets Configurados

Verifique se todos estão adicionados:

- [ ] `SSH_PRIVATE_KEY`
- [ ] `SSH_HOST`
- [ ] `SSH_USER`
- [ ] `SSH_PORT`
- [ ] `OPENAI_API_KEY`
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `POSTGRES_CONNECTION_STRING`
- [ ] `WHATSAPP_API_KEY`

---

## 🎯 Workflows Criados

### **Deploy DEV:**
- **Trigger:** Push na branch `dev`
- **Servidor:** DEV (porta 8001)
- **Domínio:** botdev.automacaovn.shop
- **Container:** whatsapp-bot-dev

### **Deploy PROD:**
- **Trigger:** Push na branch `main`
- **Servidor:** PROD (porta 8000)
- **Domínio:** bot.automacaovn.shop
- **Container:** whatsapp-bot

---

## 🚀 Deploy Manual via GitHub

Para fazer deploy manualmente:

1. Acesse: https://github.com/Viniciushann/Langgraph-projeto-multi-tenart/actions
2. Clique em "Deploy DEV" ou "Deploy PROD"
3. Clique em "Run workflow"
4. Selecione a branch
5. Clique em "Run workflow"

---

## 🐛 Troubleshooting

### **Erro: Permission denied (publickey)**

```bash
# Verificar se a chave foi adicionada corretamente
ssh -i ~/.ssh/github_actions_deploy root@46.62.155.254
```

Se falhar:
```bash
# Adicionar novamente
ssh root@46.62.155.254
cat >> ~/.ssh/authorized_keys << 'EOF'
ssh-ed25519 AAAAC3... github-actions-deploy
EOF
chmod 600 ~/.ssh/authorized_keys
```

### **Erro: Health check falhou**

```bash
# SSH no servidor
ssh root@46.62.155.254

# Ver logs
docker service logs whatsapp-bot-dev_whatsapp-bot-dev --tail 100
```

### **Erro: Git reset failed**

```bash
# SSH no servidor
cd /root/whatsapp-bot-dev/Langcham-fluxo-atendimento

# Resolver conflitos
git fetch origin
git reset --hard origin/dev
```

---

## 📈 Melhorias Futuras

### **Adicionar Testes Automáticos:**

```yaml
- name: 🧪 Run Tests
  run: |
    cd Langcham-fluxo-atendimento
    python -m pytest tests/ -v
```

### **Notificações Slack:**

```yaml
- name: 📱 Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deploy DEV ${{ job.status }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

### **Rollback Automático:**

```yaml
- name: 🔄 Rollback on Failure
  if: failure()
  run: |
    ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} << 'ENDSSH'
      docker service rollback whatsapp-bot-dev_whatsapp-bot-dev
    ENDSSH
```

---

## ✅ Checklist de Configuração

### **GitHub:**
- [ ] Secrets adicionados
- [ ] Workflows criados
- [ ] Branch `dev` criada
- [ ] Push inicial feito

### **Servidor:**
- [ ] Chave SSH pública adicionada
- [ ] Repositório Git configurado
- [ ] Permissões corretas

### **Teste:**
- [ ] Deploy manual executado
- [ ] Deploy automático testado
- [ ] Health check validado
- [ ] Logs verificados

---

## 🎉 Resultado Final

Após configuração completa:

1. **Push para `dev`** → Deploy automático em DEV
2. **Push para `main`** → Deploy automático em PROD
3. **Zero downtime** - Docker service update
4. **Health checks** automáticos
5. **Rollback** fácil se necessário

**Tempo de deploy:** ~2-3 minutos após push

---

**Desenvolvido por:** Vinícius Soutenio
**Data:** Outubro 2025
**Status:** Pronto para usar
