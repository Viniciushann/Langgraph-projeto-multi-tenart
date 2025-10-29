## FASE 1 — Estrutura Multi-Tenant (DEV)

Objetivo: criar o alicerce multi-tenant no Supabase DEV e preparar o backend para isolar dados por `tenant_id`, mantendo a produção intocada.

- Ambiente alvo: desenvolvimento (porta 8001)
- Banco alvo: Supabase DEV (novo projeto)
- Cache alvo: Redis DB 1
- Resultado esperado: tabelas novas criadas, tabelas existentes ajustadas, RLS habilitado e políticas por `tenant_id`, plano de migração, e tenant de teste funcional

---

### 1) Modelo de Dados — Novas Tabelas

Criaremos as tabelas base do multi-tenant. Ajuste os tipos/nomes dos campos conforme seu esquema atual.

```sql
-- 1.1 tenants: cadastro de empresas/contas
create table if not exists public.tenants (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null, -- ex: centro-oeste, clinica-x
  name text not null,
  status text not null default 'active', -- active | inactive
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists tenants_slug_idx on public.tenants (slug);

-- 1.2 tenant_features: feature flags por tenant
create table if not exists public.tenant_features (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  feature_key text not null, -- ex: rag_enabled, multiple_phone_numbers
  enabled boolean not null default true,
  config jsonb not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, feature_key)
);

create index if not exists tenant_features_tenant_feature_idx
  on public.tenant_features (tenant_id, feature_key);

-- 1.3 tenant_prompts: prompts/sistema por tenant
create table if not exists public.tenant_prompts (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  prompt_type text not null default 'system', -- system | tool | fallback | etc
  content text not null,
  version int not null default 1,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists tenant_prompts_tenant_idx on public.tenant_prompts (tenant_id);
create index if not exists tenant_prompts_active_idx on public.tenant_prompts (tenant_id, active);

-- 1.4 tenant_phone_numbers: múltiplos números por tenant (futuro)
create table if not exists public.tenant_phone_numbers (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete cascade,
  phone_e164 text not null, -- ex: +556299999999
  label text,
  is_default boolean not null default false,
  provider text default 'evolution',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, phone_e164)
);

create index if not exists tenant_phone_numbers_tenant_default_idx
  on public.tenant_phone_numbers (tenant_id, is_default);
```

---

### 2) Alterar Tabelas Existentes — Adicionar `tenant_id`

Adicione `tenant_id` como NOT NULL nas tabelas que armazenam dados de negócio. Ajuste nomes conforme seu schema.

```sql
-- 2.1 clientes
alter table if exists public.clientes
  add column if not exists tenant_id uuid;

-- 2.2 documents
alter table if exists public.documents
  add column if not exists tenant_id uuid;

-- 2.3 chat_history
alter table if exists public.chat_history
  add column if not exists tenant_id uuid;

-- 2.4 profissionais (futuro)
alter table if exists public.profissionais
  add column if not exists tenant_id uuid;
```

Defina as FKs e índices compostos para performance.

```sql
-- FKs
alter table if exists public.clientes
  add constraint clientes_tenant_fk foreign key (tenant_id)
  references public.tenants(id) on delete restrict;

alter table if exists public.documents
  add constraint documents_tenant_fk foreign key (tenant_id)
  references public.tenants(id) on delete restrict;

alter table if exists public.chat_history
  add constraint chat_history_tenant_fk foreign key (tenant_id)
  references public.tenants(id) on delete restrict;

alter table if exists public.profissionais
  add constraint profissionais_tenant_fk foreign key (tenant_id)
  references public.tenants(id) on delete restrict;

-- Índices compostos
create index if not exists clientes_tenant_comp_idx on public.clientes (tenant_id, id);
create index if not exists documents_tenant_comp_idx on public.documents (tenant_id, id);
create index if not exists chat_history_tenant_comp_idx on public.chat_history (tenant_id, id);
create index if not exists profissionais_tenant_comp_idx on public.profissionais (tenant_id, id);
```

Após migração de dados (seção 5), torne `tenant_id` NOT NULL:

```sql
alter table if exists public.clientes alter column tenant_id set not null;
alter table if exists public.documents alter column tenant_id set not null;
alter table if exists public.chat_history alter column tenant_id set not null;
alter table if exists public.profissionais alter column tenant_id set not null;
```

---

### 3) Row Level Security (RLS)

Ative RLS nas tabelas multi-tenant e crie políticas. Assumimos o uso de `auth.uid()`/JWT com `tenant_id` incluído nas claims do serviço ou uso de Postgres settings via `set_config('request.tenant_id', ...)` no backend.

```sql
-- Ativar RLS
alter table public.tenants enable row level security;
alter table public.tenant_features enable row level security;
alter table public.tenant_prompts enable row level security;
alter table public.tenant_phone_numbers enable row level security;
alter table public.clientes enable row level security;
alter table public.documents enable row level security;
alter table public.chat_history enable row level security;
alter table public.profissionais enable row level security;

-- Helper: função para ler tenant_id do contexto
create or replace function public.current_tenant_id()
returns uuid language sql stable as $$
  select nullif(current_setting('request.tenant_id', true), '')::uuid
$$;

-- Políticas baseadas em current_tenant_id()
create policy tenants_isolate on public.tenants
  for select using (id = public.current_tenant_id());

create policy tenant_features_isolate on public.tenant_features
  for select using (tenant_id = public.current_tenant_id());

create policy tenant_prompts_isolate on public.tenant_prompts
  for select using (tenant_id = public.current_tenant_id());

create policy tenant_phone_numbers_isolate on public.tenant_phone_numbers
  for select using (tenant_id = public.current_tenant_id());

create policy clientes_isolate on public.clientes
  for select using (tenant_id = public.current_tenant_id());

create policy documents_isolate on public.documents
  for select using (tenant_id = public.current_tenant_id());

create policy chat_history_isolate on public.chat_history
  for select using (tenant_id = public.current_tenant_id());

create policy profissionais_isolate on public.profissionais
  for select using (tenant_id = public.current_tenant_id());

-- Opcionalmente: inserir/atualizar/deletar com mesma restrição
create policy tenants_modify on public.tenants for all
  using (id = public.current_tenant_id())
  with check (id = public.current_tenant_id());

create policy tenant_features_modify on public.tenant_features for all
  using (tenant_id = public.current_tenant_id())
  with check (tenant_id = public.current_tenant_id());

create policy tenant_prompts_modify on public.tenant_prompts for all
  using (tenant_id = public.current_tenant_id())
  with check (tenant_id = public.current_tenant_id());

create policy tenant_phone_numbers_modify on public.tenant_phone_numbers for all
  using (tenant_id = public.current_tenant_id())
  with check (tenant_id = public.current_tenant_id());

create policy clientes_modify on public.clientes for all
  using (tenant_id = public.current_tenant_id())
  with check (tenant_id = public.current_tenant_id());

create policy documents_modify on public.documents for all
  using (tenant_id = public.current_tenant_id())
  with check (tenant_id = public.current_tenant_id());

create policy chat_history_modify on public.chat_history for all
  using (tenant_id = public.current_tenant_id())
  with check (tenant_id = public.current_tenant_id());

create policy profissionais_modify on public.profissionais for all
  using (tenant_id = public.current_tenant_id())
  with check (tenant_id = public.current_tenant_id());
```

No backend (porta 8001), setar o `request.tenant_id` por requisição ao resolver o tenant (ver Fase 2), por exemplo:

```sql
select set_config('request.tenant_id', '<TENANT_UUID>', true);
```

---

### 4) Validações e Constraints

- `slug` único em `tenants`
- `unique (tenant_id, feature_key)` em `tenant_features`
- `unique (tenant_id, phone_e164)` em `tenant_phone_numbers`
- Índices compostos `(tenant_id, id)` nas tabelas principais
- FKs para `tenants(id)` com `on delete restrict` (ou `cascade` conforme regra)

---

### 5) Migração de Dados (DEV)

Passo-a-passo seguro para DEV. Faça backup antes.

```bash
# 5.1 Backup (DEV)
pg_dump --data-only --inserts "$SUPABASE_DEV_URL" > backup_dev_data_$(date +%F).sql
```

Procedimento:

1. Criar um registro em `tenants` para representar o tenant atual único (ex: "Centro-Oeste Drywall").
2. Pegar o `id` desse tenant e popular `tenant_id` em todas as linhas existentes de `clientes`, `documents`, `chat_history`, `profissionais`.
3. Criar prompt default em `tenant_prompts` e features iniciais em `tenant_features`.
4. Verificar contagens por `tenant_id` e consistência.
5. Tornar `tenant_id` NOT NULL nas tabelas (seção 2) após validar tudo.

Exemplo de seed da migração única:

```sql
-- 5.2 Criar tenant inicial
insert into public.tenants (slug, name)
values ('centro-oeste', 'Centro-Oeste Drywall')
returning id;

-- Suponha que retornou X (= tenant_uuid)
-- 5.3 Atribuir tenant_id às tabelas existentes
update public.clientes set tenant_id = 'X' where tenant_id is null;
update public.documents set tenant_id = 'X' where tenant_id is null;
update public.chat_history set tenant_id = 'X' where tenant_id is null;
update public.profissionais set tenant_id = 'X' where tenant_id is null;

-- 5.4 Prompts e features defaults
insert into public.tenant_prompts (tenant_id, prompt_type, content, active)
values ('X', 'system', 'Você é um assistente para a empresa Centro-Oeste...', true);

insert into public.tenant_features (tenant_id, feature_key, enabled)
values
  ('X', 'rag_enabled', true),
  ('X', 'multiple_phone_numbers', false);

-- 5.5 Verificações
select tenant_id, count(*) from public.clientes group by 1;
select tenant_id, count(*) from public.documents group by 1;
select tenant_id, count(*) from public.chat_history group by 1;
select tenant_id, count(*) from public.profissionais group by 1;
```

Após validar, executar o `SET NOT NULL` (seção 2).

Rollback rápido (DEV):

```sql
-- Remover NOT NULL caso necessário
alter table public.clientes alter column tenant_id drop not null;
alter table public.documents alter column tenant_id drop not null;
alter table public.chat_history alter column tenant_id drop not null;
alter table public.profissionais alter column tenant_id drop not null;

-- Opcional: restaurar dados do backup
-- psql "$SUPABASE_DEV_URL" < backup_dev_data_YYYY-MM-DD.sql
```

---

### 6) Tenant de Teste Adicional

Crie um segundo tenant para simular isolamento.

```sql
insert into public.tenants (slug, name)
values ('clinicax', 'Clínica X') returning id;

-- Adicione prompts/features para este tenant
insert into public.tenant_prompts (tenant_id, prompt_type, content)
values ('Y', 'system', 'Você é um assistente da Clínica X...', true);

insert into public.tenant_features (tenant_id, feature_key, enabled)
values
  ('Y', 'rag_enabled', true),
  ('Y', 'multiple_phone_numbers', true);
```

Teste consultas com contexto de tenant diferente:

```sql
select set_config('request.tenant_id', 'X', true);
select count(*) from public.clientes; -- deve ver apenas do tenant X

select set_config('request.tenant_id', 'Y', true);
select count(*) from public.clientes; -- deve ver apenas do tenant Y
```

---

### 7) Ajustes no Backend (porta 8001)

- Adicionar filtro `WHERE tenant_id = :tenantId` em todas as queries de dados.
- Na criação de registros, sempre setar `tenant_id` do contexto.
- Introduzir um `TenantContext` em memória por request com:
  - `tenantId` (uuid)
  - `features` carregadas via `tenant_features`
  - `prompt` ativo via `tenant_prompts`
- Antes das queries, setar `set_config('request.tenant_id', tenantId, true)` para o Supabase/Postgres (quando aplicável).
- Preparar o "Tenant Resolver" (Fase 2) para mapear número de WhatsApp ou header/host → `tenantId`.

Exemplo pseudo-código:

```ts
// request handler
const tenantId = await resolveTenantId(req); // Fase 2
await db.raw("select set_config('request.tenant_id', ?, true)", [tenantId]);

// sempre filtrar por tenantId
const clientes = await db
  .from('clientes')
  .select('*')
  .where('tenant_id', tenantId);
```

---

### 8) Redis (DB 1) — Namespacing

- Use prefixo por tenant nas keys: `tenant:{tenantId}:session:{userId}`
- Separe memórias/chats por tenant: `tenant:{tenantId}:chat:{threadId}`
- TTLs iguais aos do ambiente atual

---

### 9) Checklist de Conclusão (DEV)

- Tabelas novas criadas: `tenants`, `tenant_features`, `tenant_prompts`, `tenant_phone_numbers`
- Tabelas existentes com `tenant_id` e índices compostos
- Dados antigos migrados para o tenant inicial
- RLS ativo e políticas ok
- Seed para tenant de teste criado
- Backend ajustado para filtrar por `tenant_id`
- Testes de isolamento OK em DEV

---

### 10) Riscos e Mitigações

- Esquecimento de filtro por `tenant_id`: reforçar testes automatizados e RLS
- Vazamento por queries agregadas: sempre incluir `tenant_id` e validar RLS
- Performance: garantir índices compostos `(tenant_id, ...)`
- Concurrency: transacionar migração de dados em blocos se necessário

---

### 11) Próximos Passos (Fase 2-3)

- Implementar Tenant Resolver (mapear número de WhatsApp → `tenant_id`)
- Carregar `features` e `prompt` dinâmicos por tenant
- RAG segmentado por `tenant_id`
- Memória segregada no Redis por tenant

---

### 12) Anexos — Script Consolidado (DEV)

Use este script como base para executar a Fase 1 no Supabase DEV. Ajuste nomes/colunas conforme seu schema.

```sql
-- Execute em ordem: criação → alterações → RLS → migração → not null
-- Seções 1, 2, 3, 5 (com X/Y substituídos)
```

---

Se algo divergir do seu schema atual, marque aqui e ajuste antes de rodar em DEV.
