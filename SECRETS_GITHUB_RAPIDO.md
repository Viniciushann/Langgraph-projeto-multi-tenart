# 🔐 GUIA RÁPIDO - Configurar Secrets no GitHub

## ⚡ 5 Minutos para Configurar

### **Passo 1: Acessar Settings** (30 segundos)

1. Acesse: https://github.com/Viniciushann/Langgraph-projeto-multi-tenart
2. Clique em **"Settings"** (aba superior)
3. Menu lateral → **"Secrets and variables"** → **"Actions"**

---

### **Passo 2: Gerar Chave SSH** (2 minutos)

**No seu computador:**

```bash
# Gerar chave SSH para GitHub Actions
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions -N ""

# Ver chave PRIVADA (copiar TODO)
cat ~/.ssh/github_actions

# Ver chave PÚBLICA (copiar TODO)
cat ~/.ssh/github_actions.pub
```

**Adicionar chave pública no servidor:**

```bash
# SSH no servidor
ssh root@46.62.155.254

# Adicionar chave pública
echo "COLAR_CHAVE_PUBLICA_AQUI" >> ~/.ssh/authorized_keys

# Ajustar permissões
chmod 600 ~/.ssh/authorized_keys

# Sair
exit
```

**Testar conexão:**

```bash
ssh -i ~/.ssh/github_actions root@46.62.155.254
# Deve conectar sem pedir senha
```

---

### **Passo 3: Adicionar Secrets** (2 minutos)

Na página de Secrets do GitHub, clique em **"New repository secret"** e adicione:

#### **Secret 1: SSH_PRIVATE_KEY**

```
Name: SSH_PRIVATE_KEY
Value: [Colar conteúdo de: cat ~/.ssh/github_actions]

Incluir TUDO:
-----BEGIN OPENSSH PRIVATE KEY-----
...
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

### **Passo 4: Criar Branch DEV e Push** (1 minuto)

```bash
# No repositório local
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Landcham projeto multi-tenant"

# Criar branch dev
git checkout -b dev

# Adicionar workflows
git add .github/

# Commit
git commit -m "ci: adicionar GitHub Actions"

# Push
git push -u origin dev


# Voltar para main
git checkout main
git add .github/
git commit -m "ci: adicionar GitHub Actions"
git push origin main
```

---

## ✅ Checklist Rápido

- [ ] Chave SSH gerada
- [ ] Chave pública adicionada no servidor
- [ ] Testado conexão SSH
- [ ] 9 secrets adicionados no GitHub
- [ ] Workflows commitados
- [ ] Branch `dev` criada e pushed

---

## 🚀 Testar Deploy

```bash
# Fazer mudança simples
echo "# Test" >> README.md

# Commit e push para dev
git checkout dev
git add .
git commit -m "test: deploy automático"
git push origin dev

# Ver execução em:
# https://github.com/Viniciushann/Langgraph-projeto-multi-tenart/actions
```

---

## 🎯 Lista de Secrets (Copiar e Colar)

```
SSH_PRIVATE_KEY = [conteúdo de ~/.ssh/github_actions]
SSH_HOST = 46.62.155.254
SSH_USER = root
SSH_PORT = 22
OPENAI_API_KEY = [sua-chave-openai-aqui]
SUPABASE_URL = https://wmzhbgcqugtctnzyinqw.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtemhiZ2NxdWd0Y3RuenlpbnF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3NTQ5NDAsImV4cCI6MjA3NzMzMDk0MH0.pziIBNSJfex-dEJDJ0NeU7awjadoJXg87a8TONc4Xic
POSTGRES_CONNECTION_STRING = postgresql://postgres:AcZgZs8oPTFsNQkU@db.wmzhbgcqugtctnzyinqw.supabase.co:5432/postgres?sslmode=require
WHATSAPP_API_KEY = 8773E1C40430-4626-B896-1302789BA4D9
```

---

**Tempo Total: 5 minutos** ⚡
**Resultado: Deploy automático funcionando!** 🚀
