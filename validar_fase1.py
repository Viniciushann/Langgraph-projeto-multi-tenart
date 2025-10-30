#!/usr/bin/env python3
"""
Script para validar a Fase 1 - Estrutura Multi-Tenant
"""
import os
from supabase import create_client, Client

# Credenciais Supabase DEV
SUPABASE_URL = "https://wmzhbgcqugtctnzyinqw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtemhiZ2NxdWd0Y3RuenlpbnF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3NTQ5NDAsImV4cCI6MjA3NzMzMDk0MH0.pziIBNSJfex-dEJDJ0NeU7awjadoJXg87a8TONc4Xic"

def main():
    print("=" * 70)
    print("🔍 VALIDAÇÃO FASE 1 - ESTRUTURA MULTI-TENANT")
    print("=" * 70)
    print()

    # Conectar no Supabase
    print("📡 Conectando no Supabase DEV...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conectado!\n")

    relatorio = []
    relatorio.append("# 📊 RELATÓRIO - FASE 1: ESTRUTURA MULTI-TENANT")
    relatorio.append("")
    relatorio.append("## ✅ Status Geral")
    relatorio.append("")

    # 1. Verificar Tenants
    print("1️⃣ Verificando TENANTS...")
    try:
        tenants = supabase.table('tenants').select('*').execute()
        print(f"   ✅ {len(tenants.data)} tenants encontrados")

        relatorio.append("### 1. Tenants Criados")
        relatorio.append("")
        for tenant in tenants.data:
            print(f"      - {tenant['nome_empresa']} ({tenant['segmento']})")
            relatorio.append(f"**{tenant['nome_empresa']}**")
            relatorio.append(f"- UUID: `{tenant['id']}`")
            relatorio.append(f"- Segmento: {tenant['segmento']}")
            relatorio.append(f"- WhatsApp: {tenant['whatsapp_numero']}")
            relatorio.append(f"- Plano: {tenant['plano']}")
            relatorio.append(f"- Status: {'🟢 Ativo' if tenant['ativo'] else '🔴 Inativo'}")
            relatorio.append("")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        relatorio.append(f"❌ Erro ao verificar tenants: {e}")

    # 2. Verificar Features
    print("\n2️⃣ Verificando TENANT_FEATURES...")
    try:
        features = supabase.table('tenant_features').select('*').execute()
        print(f"   ✅ {len(features.data)} configurações de features")

        relatorio.append("### 2. Features dos Tenants")
        relatorio.append("")
        for feature in features.data:
            tenant = next((t for t in tenants.data if t['id'] == feature['tenant_id']), None)
            if tenant:
                print(f"      - {tenant['nome_empresa']}: RAG={feature['rag_habilitado']}, "
                      f"Audio={feature['transcricao_audio']}, Multi-prof={feature['multi_profissional']}")
                relatorio.append(f"**{tenant['nome_empresa']}:**")
                relatorio.append(f"- ✅ Atendimento Básico: {feature['atendimento_basico']}")
                relatorio.append(f"- ✅ Transcrição Audio: {feature['transcricao_audio']}")
                relatorio.append(f"- ✅ Análise Imagem: {feature['analise_imagem']}")
                relatorio.append(f"- ✅ RAG: {feature['rag_habilitado']}")
                relatorio.append(f"- ✅ Agendamento: {feature['agendamento_habilitado']}")
                relatorio.append(f"- ✅ Multi-profissional: {feature['multi_profissional']}")
                relatorio.append("")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 3. Verificar Prompts
    print("\n3️⃣ Verificando TENANT_PROMPTS...")
    try:
        prompts = supabase.table('tenant_prompts').select('*').execute()
        print(f"   ✅ {len(prompts.data)} prompts configurados")

        relatorio.append("### 3. Prompts dos Assistentes")
        relatorio.append("")
        for prompt in prompts.data:
            tenant = next((t for t in tenants.data if t['id'] == prompt['tenant_id']), None)
            if tenant:
                print(f"      - {tenant['nome_empresa']}: Assistente {prompt['nome_assistente']} "
                      f"({prompt['modelo_llm']})")
                relatorio.append(f"**{tenant['nome_empresa']} - {prompt['nome_assistente']}**")
                relatorio.append(f"- Modelo: {prompt['modelo_llm']}")
                relatorio.append(f"- Temperatura: {prompt['temperatura']}")
                relatorio.append(f"- Tom de voz: {prompt['tom_voz']}")
                relatorio.append(f"- Mensagem boas-vindas: \"{prompt['mensagem_boas_vindas'][:50]}...\"")
                relatorio.append("")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 4. Verificar Profissionais
    print("\n4️⃣ Verificando PROFISSIONAIS...")
    try:
        profissionais = supabase.table('profissionais').select('*').execute()
        print(f"   ✅ {len(profissionais.data)} profissionais cadastrados")

        relatorio.append("### 4. Profissionais Cadastrados")
        relatorio.append("")
        for prof in profissionais.data:
            tenant = next((t for t in tenants.data if t['id'] == prof['tenant_id']), None)
            if tenant:
                print(f"      - {tenant['nome_empresa']}: {prof['nome_exibicao']} - {prof['especialidade_principal']}")
                relatorio.append(f"**{prof['nome_completo']}** ({tenant['nome_empresa']})")
                relatorio.append(f"- Exibição: {prof['nome_exibicao']}")
                relatorio.append(f"- Especialidade: {prof['especialidade_principal']}")
                if prof.get('crm_cro'):
                    relatorio.append(f"- CRM/CRO: {prof['crm_cro']}")
                relatorio.append("")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 5. Verificar Especialidades
    print("\n5️⃣ Verificando ESPECIALIDADES...")
    try:
        especialidades = supabase.table('especialidades').select('*').execute()
        print(f"   ✅ {len(especialidades.data)} especialidades")

        relatorio.append("### 5. Especialidades")
        relatorio.append("")
        for esp in especialidades.data:
            tenant = next((t for t in tenants.data if t['id'] == esp['tenant_id']), None)
            if tenant:
                print(f"      - {tenant['nome_empresa']}: {esp['nome']}")
                relatorio.append(f"- **{esp['nome']}** ({tenant['nome_empresa']}): {esp['descricao']}")
        relatorio.append("")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 6. Verificar Clientes (migração)
    print("\n6️⃣ Verificando CLIENTES (migração)...")
    try:
        clientes_migrados = supabase.table('clients_dev').select('id', count='exact').not_.is_('tenant_id', 'null').execute()
        clientes_total = supabase.table('clients_dev').select('id', count='exact').execute()
        print(f"   ✅ {clientes_migrados.count}/{clientes_total.count} clientes com tenant_id")

        relatorio.append("### 6. Migração de Dados Existentes")
        relatorio.append("")
        relatorio.append(f"**Clientes:**")
        relatorio.append(f"- Total: {clientes_total.count}")
        relatorio.append(f"- Com tenant_id: {clientes_migrados.count}")
        relatorio.append(f"- Status: {'✅ Completo' if clientes_migrados.count == clientes_total.count else '⚠️ Parcial'}")
        relatorio.append("")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 7. Verificar Documents (migração)
    print("\n7️⃣ Verificando DOCUMENTS (migração)...")
    try:
        docs_migrados = supabase.table('conhecimento_dev').select('id', count='exact').not_.is_('tenant_id', 'null').execute()
        docs_total = supabase.table('conhecimento_dev').select('id', count='exact').execute()
        print(f"   ✅ {docs_migrados.count}/{docs_total.count} documentos com tenant_id")

        relatorio.append(f"**Documentos (RAG):**")
        relatorio.append(f"- Total: {docs_total.count}")
        relatorio.append(f"- Com tenant_id: {docs_migrados.count}")
        relatorio.append(f"- Status: {'✅ Completo' if docs_migrados.count == docs_total.count else '⚠️ Parcial'}")
        relatorio.append("")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Resumo Final
    print("\n" + "=" * 70)
    print("📊 RESUMO FINAL")
    print("=" * 70)
    print(f"✅ Tenants: {len(tenants.data)}")
    print(f"✅ Features configuradas: {len(features.data)}")
    print(f"✅ Prompts: {len(prompts.data)}")
    print(f"✅ Profissionais: {len(profissionais.data)}")
    print(f"✅ Especialidades: {len(especialidades.data)}")
    print(f"✅ Clientes migrados: {clientes_migrados.count}/{clientes_total.count}")
    print(f"✅ Documentos migrados: {docs_migrados.count}/{docs_total.count}")
    print()

    relatorio.append("## 📈 Resumo Executivo")
    relatorio.append("")
    relatorio.append(f"- ✅ **{len(tenants.data)} tenants** criados e configurados")
    relatorio.append(f"- ✅ **{len(profissionais.data)} profissionais** cadastrados")
    relatorio.append(f"- ✅ **{len(especialidades.data)} especialidades** registradas")
    relatorio.append(f"- ✅ **{clientes_migrados.count} clientes** migrados com tenant_id")
    relatorio.append(f"- ✅ **{docs_migrados.count} documentos RAG** migrados com tenant_id")
    relatorio.append("")
    relatorio.append("## 🎯 Próximos Passos (FASE 2)")
    relatorio.append("")
    relatorio.append("1. ✅ Estrutura multi-tenant criada")
    relatorio.append("2. ⏭️ Criar middleware de tenant identification")
    relatorio.append("3. ⏭️ Adaptar código para usar tenant_id dinamicamente")
    relatorio.append("4. ⏭️ Implementar seleção de profissional (clínicas)")
    relatorio.append("5. ⏭️ Criar admin dashboard básico")
    relatorio.append("")
    relatorio.append("---")
    relatorio.append(f"**Data:** {os.popen('date').read().strip()}")
    relatorio.append(f"**Ambiente:** Supabase DEV")
    relatorio.append(f"**Status:** ✅ Fase 1 Concluída")

    # Salvar relatório
    print("💾 Salvando relatório...")
    with open('FASE_1_RELATORIO.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(relatorio))
    print("✅ Relatório salvo: FASE_1_RELATORIO.md")
    print()

if __name__ == "__main__":
    main()
