# ✅ Próximos Passos - GitHub Actions

## 🎉 Concluído

- [x] Chave SSH gerada: `~/.ssh/github_actions_deploy`
- [x] Chave pública adicionada no servidor
- [x] Credenciais Supabase DEV atualizadas

---

## 📋 Próximos Passos (15 minutos)

### **1️⃣ Adicionar Secrets no GitHub** ⏱️ 5 min

1. Acesse: https://github.com/Viniciushann/Langgraph-projeto-multi-tenart/settings/secrets/actions

2. Clique em **"New repository secret"** e adicione cada um:

#### **Secret 1: SSH_PRIVATE_KEY**
```
Name: SSH_PRIVATE_KEY
Value:
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAJDrPhNEHrMRKJqJccLZhhc3CtIKU2v84mVk7+2kERzwAAAJi1bhN4tW4T
eAAAAAtzc2gtZWQyNTUxOQAAACAJDrPhNEHrMRKJqJccLZhhc3CtIKU2v84mVk7+2kERzw
AAAEDTdSTPf9BDpPJxB/01cGn+bwAf4CVCPIn/MOLNS0yYAAkOs+E0QesxEomolxwtmGFz
cK0gpTa/ziZWTv7aQRHPAAAAFWdpdGh1Yi1hY3Rpb25zLWRlcGxveQ==
-----END OPENSSH PRIVATE KEY-----
```

#### **Secret 2: SSH_HOST**
```
Name: SSH_HOST
Value: 46.62.155.254
```

#### **Secret 3: SSH_USER**
```
Name: SSH_USER
Value: root
```

#### **Secret 4: SSH_PORT**
```
Name: SSH_PORT
Value: 22
```

#### **Secret 5: OPENAI_API_KEY**
```
Name: OPENAI_API_KEY
Value: [sua-chave-openai-aqui]
# Usar a chave OpenAI do projeto
```

#### **Secret 6: SUPABASE_URL**
```
Name: SUPABASE_URL
Value: https://wmzhbgcqugtctnzyinqw.supabase.co
```

#### **Secret 7: SUPABASE_KEY**
```
Name: SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtemhiZ2NxdWd0Y3RuenlpbnF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3NTQ5NDAsImV4cCI6MjA3NzMzMDk0MH0.pziIBNSJfex-dEJDJ0NeU7awjadoJXg87a8TONc4Xic
```

#### **Secret 8: POSTGRES_CONNECTION_STRING**
```
Name: POSTGRES_CONNECTION_STRING
Value: postgresql://postgres:AcZgZs8oPTFsNQkU@db.wmzhbgcqugtctnzyinqw.supabase.co:5432/postgres?sslmode=require
```

#### **Secret 9: WHATSAPP_API_KEY**
```
Name: WHATSAPP_API_KEY
Value: 8773E1C40430-4626-B896-1302789BA4D9
```

---

### **2️⃣ Criar Branch DEV e Push Workflows** ⏱️ 3 min

```bash
# No repositório local
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Landcham projeto multi-tenant"

# Criar branch dev
git checkout -b dev

# Adicionar workflows e novos arquivos
git add .github/workflows/
git add PROXIMOS_PASSOS_GITHUB_ACTIONS.md

# Commit
git commit -m "ci: configurar GitHub Actions para deploy automático"

# Push branch dev
git push -u origin dev

# Voltar para main e fazer merge
git checkout main
git merge dev
git push origin main
```

---

### **3️⃣ Testar Deploy Automático** ⏱️ 2 min

#### **Opção A: Fazer mudança simples**
```bash
# Criar arquivo de teste
echo "# Deploy Test" >> Langcham-fluxo-atendimento/DEPLOY_TEST.md

# Commit e push para DEV
git checkout dev
git add .
git commit -m "test: testar deploy automático DEV"
git push origin dev
```

#### **Opção B: Deploy manual via GitHub**
1. Acesse: https://github.com/Viniciushann/Langgraph-projeto-multi-tenart/actions
2. Clique em "Deploy DEV"
3. Clique em "Run workflow"
4. Selecione branch "dev"
5. Clique em "Run workflow"

---

### **4️⃣ Acompanhar Execução** ⏱️ 3 min

1. Acesse: https://github.com/Viniciushann/Langgraph-projeto-multi-tenart/actions
2. Clique no workflow em execução
3. Veja os logs em tempo real

**Logs esperados:**
```
✓ Checkout code
✓ Setup SSH
✓ Add server to known_hosts
✓ Deploy to Server
  🔄 Atualizando código...
  🐳 Buildando imagem Docker...
  ♻️ Atualizando serviço...
  ✅ Deploy concluído!
✓ Verificar Deploy
  ✅ Deploy verificado com sucesso!
```

---

### **5️⃣ Configurar DNS (se ainda não configurado)** ⏱️ 2 min

No painel DNS do seu provedor (onde está `automacaovn.shop`):

**Adicionar registro:**
```
Type: A
Name: botdev
Value: 46.62.155.254
TTL: 300
```

**Resultado:**
- `botdev.automacaovn.shop` → servidor DEV (porta 8001)
- `bot.automacaovn.shop` → servidor PROD (porta 8000)

---

## 🎯 Resumo do Fluxo

```
Desenvolvimento:
1. Trabalhar na branch dev
2. git push origin dev
3. GitHub Actions → Deploy automático para DEV
4. Testar em https://botdev.automacaovn.shop

Produção:
1. Merge dev → main
2. git push origin main
3. GitHub Actions → Deploy automático para PROD
4. Disponível em https://bot.automacaovn.shop
```

---

## ✅ Checklist

- [ ] 9 secrets adicionados no GitHub
- [ ] Branch `dev` criada e pushed
- [ ] Workflows commitados (main e dev)
- [ ] DNS `botdev` configurado
- [ ] Deploy manual testado
- [ ] Deploy automático testado
- [ ] Health check validado

---

## 🔧 Testar Conexão SSH Localmente (Opcional)

```bash
# Testar conexão com a nova chave
ssh -i ~/.ssh/github_actions_deploy root@46.62.155.254

# Deve conectar sem pedir senha
# Sair com: exit
```

---

## 📊 Próximos Passos Após Deploy DEV

Depois que o DEV estiver funcionando:

1. **Configurar Evolution API DEV**
   - Criar instância: `Landchan-multi-tenant-dev`
   - Configurar webhook: `https://botdev.automacaovn.shop/webhook`

2. **Executar Scripts Supabase DEV**
   - Rodar `setup_supabase_dev.sql`
   - Criar tabelas com sufixo `_dev`

3. **Iniciar Desenvolvimento Multi-Tenant**
   - Seguir `FASE_1_ESTRUTURA_MULTI_TENANT.md`
   - Implementar tenant_id nas tabelas
   - Criar middleware de tenant identification

---

**Tempo Total Estimado: 15 minutos**
**Status: Pronto para configurar GitHub Actions** ✅
