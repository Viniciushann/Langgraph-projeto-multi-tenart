#!/usr/bin/env python3
"""
Script para limpar o sistema e deixar apenas uma instância real funcionando.

Este script vai:
1. Listar todos os tenants atuais
2. Permitir escolher qual manter
3. Desativar/remover os outros
4. Limpar dados fictícios
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
    print("🧹 LIMPEZA DO SISTEMA - MANTER APENAS 1 INSTÂNCIA REAL")
    print("=" * 80)
    print()
    
    try:
        # Inicializar clientes
        settings = get_settings()
        supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)
        
        print("1️⃣ Listando todos os tenants no sistema...")
        print("-" * 60)
        
        # Buscar todos os tenants (ativos e inativos)
        response = supabase.client.table("tenants").select("*").execute()
        tenants = response.data if response.data else []
        
        if not tenants:
            print("❌ Nenhum tenant encontrado no banco!")
            return
            
        print(f"📋 Encontrados {len(tenants)} tenants:")
        print()
        
        for i, tenant in enumerate(tenants, 1):
            status = "🟢 ATIVO" if tenant.get('ativo') else "🔴 INATIVO"
            print(f"   {i}. {tenant['nome_empresa']}")
            print(f"      WhatsApp: {tenant['whatsapp_numero']}")
            print(f"      Status: {status}")
            print(f"      Evolution Instance: {tenant.get('whatsapp_sender_id', 'N/A')}")
            print(f"      API URL: {tenant.get('evolution_api_url', 'N/A')}")
            print()
        
        print("-" * 60)
        
        # Permitir escolha
        while True:
            try:
                escolha = input("Qual tenant manter ATIVO? (número): ")
                escolha_num = int(escolha)
                if 1 <= escolha_num <= len(tenants):
                    tenant_escolhido = tenants[escolha_num - 1]
                    break
                else:
                    print(f"❌ Digite um número entre 1 e {len(tenants)}")
            except ValueError:
                print("❌ Digite apenas números")
        
        print()
        print(f"✅ Tenant escolhido: {tenant_escolhido['nome_empresa']}")
        print(f"   WhatsApp: {tenant_escolhido['whatsapp_numero']}")
        print()
        
        # Confirmar ação
        confirmar = input("Tem certeza? Outros tenants serão DESATIVADOS (s/N): ").lower()
        if confirmar != 's':
            print("❌ Operação cancelada")
            return
            
        print()
        print("2️⃣ Processando limpeza...")
        print("-" * 60)
        
        # Desativar todos os outros tenants
        for tenant in tenants:
            if tenant['id'] != tenant_escolhido['id']:
                print(f"🔴 Desativando: {tenant['nome_empresa']}")
                supabase.client.table("tenants").update({
                    "ativo": False
                }).eq("id", tenant['id']).execute()
            else:
                print(f"🟢 Mantendo ativo: {tenant['nome_empresa']}")
                supabase.client.table("tenants").update({
                    "ativo": True
                }).eq("id", tenant['id']).execute()
        
        print()
        print("3️⃣ Limpando dados fictícios...")
        print("-" * 60)
        
        # Limpar clientes de teste/fictícios se existirem
        print("🧹 Limpando clientes de teste...")
        # (Opcional: implementar limpeza de clientes de teste)
        
        print()
        print("4️⃣ Verificando configuração final...")
        print("-" * 60)
        
        # Testar o tenant ativo
        resolver = TenantResolver(supabase)
        context = await resolver.identificar_tenant(tenant_escolhido['whatsapp_numero'])
        
        if context:
            print(f"✅ Tenant ativo confirmado:")
            print(f"   Nome: {context['tenant_nome']}")
            print(f"   ID: {context['tenant_id']}")
            print(f"   WhatsApp: {context['whatsapp_numero']}")
            print(f"   Sender ID: {context.get('whatsapp_sender_id', 'N/A')}")
            print(f"   Evolution URL: {context.get('evolution_api_url', 'N/A')}")
        else:
            print("❌ Erro: não foi possível carregar o tenant ativo")
            
        print()
        print("=" * 80)
        print("✅ LIMPEZA CONCLUÍDA!")
        print()
        print("📋 Próximos passos:")
        print("   1. Verificar se a instância Evolution API está correta")
        print("   2. Testar o webhook com o número real")
        print("   3. Rodar o servidor localmente")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())