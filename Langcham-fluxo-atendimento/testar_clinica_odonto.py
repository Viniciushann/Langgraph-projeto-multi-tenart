#!/usr/bin/env python3
"""
Testador específico para a Clínica Odonto Sorriso
Verifica se o webhook está funcionando com a nova configuração
"""

import os
import sys
import asyncio
import httpx
from datetime import datetime

# Configurações da Clínica Odonto Sorriso  
WEBHOOK_URL = "http://localhost:8001/webhook/whatsapp"
HEALTH_URL = "http://localhost:8001/health"
TENANT_PHONE = "556292935358"
EVOLUTION_INSTANCE = "Landchan-multi-tenant-dev"

def print_header(title):
    print("=" * 80)
    print(f"{title}")
    print("=" * 80)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

async def test_webhook_health():
    """Testa se o webhook está respondendo"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(HEALTH_URL)
            if response.status_code == 200:
                print_success(f"Webhook está online - Status: {response.status_code}")
                try:
                    data = response.json()
                    print_info(f"Environment: {data.get('environment', 'unknown')}")
                    print_info(f"Instance: {data.get('whatsapp_instance', 'unknown')}")
                except:
                    pass
                return True
            else:
                print_error(f"Webhook retornou status: {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Erro ao conectar com webhook: {e}")
        return False

def create_test_message():
    """Cria uma mensagem de teste simulando Evolution API"""
    return {
        "event": "messages.upsert",
        "instance": EVOLUTION_INSTANCE,
        "data": {
            "key": {
                "remoteJid": f"{TENANT_PHONE}@s.whatsapp.net",
                "fromMe": False,
                "id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            },
            "pushName": "Teste Sistema",
            "message": {
                "conversation": "🔧 Teste de configuração - Clínica Odonto Sorriso"
            },
            "messageTimestamp": int(datetime.now().timestamp()),
            "status": "RECEIVED"
        }
    }

async def test_webhook_message():
    """Envia mensagem de teste para o webhook"""
    try:
        message_data = create_test_message()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                WEBHOOK_URL,
                json=message_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print_success(f"Webhook processou mensagem - Status: {response.status_code}")
                try:
                    result = response.json()
                    print_info(f"Resposta: {result}")
                except:
                    print_info(f"Resposta (texto): {response.text[:200]}...")
                return True
            else:
                print_error(f"Webhook retornou erro: {response.status_code}")
                print_error(f"Resposta: {response.text}")
                return False
                
    except Exception as e:
        print_error(f"Erro ao enviar mensagem de teste: {e}")
        return False

def check_configuration():
    """Verifica a configuração atual"""
    print_info(f"Webhook URL: {WEBHOOK_URL}")
    print_info(f"Telefone Clínica: {TENANT_PHONE}")
    print_info(f"Instância Evolution: {EVOLUTION_INSTANCE}")
    print_info(f"Data/Hora do teste: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

async def main():
    print_header("TESTE CLÍNICA ODONTO SORRISO - CONFIGURAÇÃO LIMPA")
    
    print("\n🔧 Configuração Atual:")
    print("-" * 50)
    check_configuration()
    
    print("\n📡 Teste 1: Verificar se webhook está online")
    print("-" * 50)
    webhook_ok = await test_webhook_health()
    
    if not webhook_ok:
        print_error("Webhook não está respondendo. Verifique o serviço Docker.")
        return
    
    print("\n📨 Teste 2: Enviar mensagem de teste")
    print("-" * 50)
    message_ok = await test_webhook_message()
    
    print("\n📋 RESUMO DOS TESTES")
    print("=" * 80)
    
    if webhook_ok and message_ok:
        print_success("✅ TODOS OS TESTES PASSARAM!")
        print_success("🎉 Clínica Odonto Sorriso está configurada e funcionando!")
        print_info("📱 Agora você pode enviar mensagens para 556292935358")
    elif webhook_ok:
        print_error("⚠️  Webhook está online mas houve erro no processamento")
        print_info("🔍 Verifique os logs do Docker para mais detalhes")
    else:
        print_error("❌ Webhook não está respondendo")
        print_info("🐳 Verifique se o serviço Docker está rodando")

if __name__ == "__main__":
    asyncio.run(main())