# Comandos Docker Swarm - WhatsApp Bot Dev

## 🐳 Comandos para Gerenciar o Serviço no Docker Swarm

### 📋 Verificar Status do Serviço
```bash
# Listar todos os serviços
docker service ls

# Verificar status específico do bot
docker service ps whatsapp-bot-dev_whatsapp-bot-dev

# Ver logs em tempo real
docker service logs -f whatsapp-bot-dev_whatsapp-bot-dev --tail 50
```

### 🔄 Atualizar/Reiniciar o Serviço

#### Opção 1: Update do Serviço (Recomendado)
```bash
# Força rebuild e restart
docker service update --force whatsapp-bot-dev_whatsapp-bot-dev
```

#### Opção 2: Remover e Recriar Stack
```bash
# Remover stack completa
docker stack rm whatsapp-bot-dev

# Aguardar limpeza completa (30-60 segundos)
sleep 60

# Recriar stack
docker stack deploy -c docker-compose.dev.yml whatsapp-bot-dev
```

#### Opção 3: Scale Down/Up
```bash
# Parar todas as instâncias
docker service scale whatsapp-bot-dev_whatsapp-bot-dev=0

# Aguardar parar
sleep 10

# Restartar
docker service scale whatsapp-bot-dev_whatsapp-bot-dev=1
```

### 🔍 Diagnóstico e Debug

```bash
# Verificar se serviço existe
docker service inspect whatsapp-bot-dev_whatsapp-bot-dev

# Ver configurações detalhadas
docker service inspect whatsapp-bot-dev_whatsapp-bot-dev --format='{{json .Spec.TaskTemplate.ContainerSpec.Env}}'

# Verificar rede
docker network ls | grep whatsapp

# Verificar volumes
docker volume ls | grep whatsapp
```

### 📦 Rebuild da Imagem (se necessário)

```bash
# Se precisar rebuildar a imagem
cd /path/to/project
docker build -t whatsapp-bot-langchain:dev .

# Atualizar serviço com nova imagem
docker service update --image whatsapp-bot-langchain:dev whatsapp-bot-dev_whatsapp-bot-dev
```

### 🚨 Comandos de Emergência

```bash
# Parar TUDO relacionado ao bot
docker service rm whatsapp-bot-dev_whatsapp-bot-dev

# Limpar containers órfãos
docker container prune -f

# Limpar redes não utilizadas
docker network prune -f

# Recriar do zero
docker stack deploy -c docker-compose.dev.yml whatsapp-bot-dev
```

## 🎯 Para Aplicar as Mudanças da Porta 8001

### Comando Recomendado:
```bash
# Atualizar serviço forçando nova configuração
docker service update --force whatsapp-bot-dev_whatsapp-bot-dev
```

### Verificar se Aplicou:
```bash
# Ver logs para confirmar porta 8001
docker service logs whatsapp-bot-dev_whatsapp-bot-dev --tail 20 | grep "Host:"

# Deve mostrar: "Host: 0.0.0.0:8001"
```

### Health Check:
```bash
# Testar se está respondendo na porta 8001
curl -f http://localhost:8001/health

# Ou via container
docker exec $(docker ps -q -f name=whatsapp-bot-dev) curl -f http://localhost:8001/health
```

## 📝 Troubleshooting

### Se o service update não funcionar:
1. Verificar se a imagem foi atualizada
2. Remover e recriar a stack
3. Verificar logs para erros

### Se não conseguir conectar:
1. Verificar se a porta 8001 está exposta
2. Verificar firewall
3. Verificar proxy/traefik

### Se logs mostram erro:
1. Verificar variáveis de ambiente
2. Verificar conectividade com Supabase
3. Verificar Evolution API
