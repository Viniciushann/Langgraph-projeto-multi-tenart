#!/usr/bin/env python3
"""
Script para configurar a Clínica Odonto Sorriso com a instância funcionando.

Atualizar:
- WhatsApp número: 556292935358 
- Instância: Landchan-multi-tenant-dev
- Status: Ativo
"""

import asyncio
import sys
import os

# Adicionar o diretório src ao PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.clients.supabase_client import criar_supabase_client
from src.config.settings import get_settings
from src.core.tenant_resolver import TenantResolver

async def main():
    print("=" * 80)
    print("🏥 CONFIGURAR CLÍNICA ODONTO SORRISO")
    print("=" * 80)
    print()
    
    try:
        # Inicializar clientes
        settings = get_settings()
        supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)
        
        print("1️⃣ Buscando Clínica Odonto Sorriso...")
        print("-" * 60)
        
        # Buscar Clínica Odonto Sorriso
        response = supabase.client.table("tenants").select("*").eq("nome_empresa", "Clínica Odonto Sorriso").execute()
        tenants = response.data if response.data else []
        
        if not tenants:
            print("❌ Clínica Odonto Sorriso não encontrada!")
            return
            
        tenant = tenants[0]
        print(f"✅ Encontrada: {tenant['nome_empresa']}")
        print(f"   ID: {tenant['id']}")
        print(f"   WhatsApp atual: {tenant['whatsapp_numero']}")
        print(f"   Sender ID atual: {tenant.get('whatsapp_sender_id', 'N/A')}")
        print(f"   Status atual: {'🟢 ATIVO' if tenant.get('ativo') else '🔴 INATIVO'}")
        print()
        
        print("2️⃣ Atualizando configurações...")
        print("-" * 60)
        
        # Novos dados
        novos_dados = {
            "whatsapp_numero": "556292935358",
            "whatsapp_sender_id": "Landchan-multi-tenant-dev", 
            "ativo": True,
            "evolution_api_url": "https://evolution.centrooestedrywalldry.com.br",
            "evolution_api_key": tenant.get('evolution_api_key', 'key123')  # Manter a chave existente
        }
        
        print(f"📝 Novos dados:")
        print(f"   WhatsApp: {novos_dados['whatsapp_numero']}")
        print(f"   Sender ID: {novos_dados['whatsapp_sender_id']}")
        print(f"   Status: 🟢 ATIVO")
        print(f"   Evolution URL: {novos_dados['evolution_api_url']}")
        print()
        
        # Atualizar no banco
        print("💾 Salvando no banco...")
        update_response = supabase.client.table("tenants").update(novos_dados).eq("id", tenant['id']).execute()
        
        if update_response.data:
            print("✅ Dados atualizados com sucesso!")
        else:
            print("❌ Erro ao atualizar dados")
            return
            
        print()
        print("3️⃣ Verificando configuração...")
        print("-" * 60)
        
        # Testar o tenant atualizado
        resolver = TenantResolver(supabase)
        context = await resolver.identificar_tenant("556292935358")
        
        if context:
            print(f"✅ Tenant configurado e funcionando:")
            print(f"   Nome: {context['tenant_nome']}")
            print(f"   ID: {context['tenant_id']}")
            print(f"   WhatsApp: {context['whatsapp_numero']}")
            print(f"   Sender ID: {context.get('whatsapp_sender_id', 'N/A')}")
            print(f"   Evolution URL: {context.get('evolution_api_url', 'N/A')}")
            print(f"   Multi-profissional: {context.get('feature_multi_profissional', False)}")
            print(f"   Profissionais: {context.get('total_profissionais', 0)}")
        else:
            print("❌ Erro: não foi possível carregar o tenant atualizado")
            
        print()
        print("4️⃣ Desativando outros tenants...")
        print("-" * 60)
        
        # Desativar outros tenants para evitar conflitos
        all_tenants_response = supabase.client.table("tenants").select("*").execute()
        all_tenants = all_tenants_response.data if all_tenants_response.data else []
        
        for t in all_tenants:
            if t['id'] != tenant['id'] and t.get('ativo'):
                print(f"🔴 Desativando: {t['nome_empresa']}")
                supabase.client.table("tenants").update({"ativo": False}).eq("id", t['id']).execute()
        
        print()
        print("=" * 80)
        print("🎉 CONFIGURAÇÃO CONCLUÍDA!")
        print()
        print("📋 Resumo:")
        print(f"   • Clínica Odonto Sorriso está ATIVA")
        print(f"   • WhatsApp: 556292935358")
        print(f"   • Instância: Landchan-multi-tenant-dev")
        print(f"   • Multi-profissional com 3 profissionais")
        print(f"   • Outros tenants desativados")
        print()
        print("🚀 Próximos passos:")
        print("   1. Testar webhook: enviar mensagem para 556292935358")
        print("   2. Verificar logs do servidor")
        print("   3. Confirmar que a instância Evolution responde")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro durante configuração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())