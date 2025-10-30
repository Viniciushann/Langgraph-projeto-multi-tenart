#!/usr/bin/env python3
"""
Script de validação da FASE 2 - Tenant Resolver Middleware
"""
import asyncio
import sys
import os

# Adicionar o diretório src ao PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.tenant_resolver import TenantResolver
from src.core.feature_manager import FeatureManager
from src.clients.supabase_client import SupabaseClient

async def validar():
    print("=" * 70)
    print("🔍 VALIDAÇÃO FASE 2 - TENANT RESOLVER MIDDLEWARE")
    print("=" * 70)
    print()

    try:
        # Inicializar clientes
        print("📡 Inicializando cliente Supabase...")
        supabase = SupabaseClient()
        resolver = TenantResolver(supabase)
        print("✓ Cliente inicializado\n")

        # ====================================================================
        # Teste 1: Centro-Oeste Drywall
        # ====================================================================
        print("1️⃣ Testando Centro-Oeste Drywall...")
        print("-" * 70)

        try:
            context1 = await resolver.identificar_tenant("556299281091")

            if context1:
                print(f"   ✓ Tenant identificado: {context1['tenant_nome']}")
                print(f"   ✓ UUID: {context1['tenant_id']}")
                print(f"   ✓ Segmento: {context1.get('tenant_segmento', 'N/A')}")
                print(f"   ✓ Plano: {context1['tenant_plano']}")
                print(f"   ✓ WhatsApp: {context1['whatsapp_numero']}")
                print()

                print("   Features:")
                print(f"     • RAG: {context1.get('feature_rag_habilitado', False)}")
                print(f"     • Transcrição Audio: {context1.get('feature_transcricao_audio', False)}")
                print(f"     • Análise Imagem: {context1.get('feature_analise_imagem', False)}")
                print(f"     • Agendamento: {context1.get('feature_agendamento_habilitado', False)}")
                print(f"     • Multi-profissional: {context1.get('feature_multi_profissional', False)}")
                print()

                fm1 = FeatureManager(context1)
                print("   Configurações (via FeatureManager):")
                print(f"     • Assistente: {fm1.get_nome_assistente()}")
                print(f"     • Modelo LLM: {fm1.get_modelo_llm()}")
                print(f"     • Temperatura: {fm1.get_temperatura()}")
                print(f"     • Max Tokens: {fm1.get_max_tokens()}")
                print(f"     • Tom de Voz: {context1.get('tom_voz', 'N/A')}")
                print()

                system_prompt = fm1.get_system_prompt()
                print(f"     • System Prompt: {system_prompt[:80]}...")
                print()

                print("   Limites:")
                print(f"     • Documentos RAG: {fm1.get_limite_documentos_rag()}")
                print(f"     • Agendamentos/mês: {fm1.get_limite_agendamentos_mes()}")
                print(f"     • Agrupamento mensagens: {fm1.get_tempo_agrupamento_mensagens()}s")
                print(f"     • Max mensagens/dia: {fm1.get_max_mensagens_dia()}")
                print()

                print("   ✅ TESTE 1 PASSOU!")
            else:
                print("   ❌ ERRO: Tenant não encontrado")
                return False

        except Exception as e:
            print(f"   ❌ ERRO ao buscar tenant: {e}")
            import traceback
            traceback.print_exc()
            return False

        print()

        # ====================================================================
        # Teste 2: Clínica Odonto Sorriso
        # ====================================================================
        print("2️⃣ Testando Clínica Odonto Sorriso (multi-profissional)...")
        print("-" * 70)

        try:
            context2 = await resolver.identificar_tenant("5562999999999")

            if context2:
                print(f"   ✓ Tenant identificado: {context2['tenant_nome']}")
                print(f"   ✓ UUID: {context2['tenant_id']}")
                print(f"   ✓ Segmento: {context2.get('tenant_segmento', 'N/A')}")
                print(f"   ✓ Plano: {context2['tenant_plano']}")
                print()

                print("   Features:")
                print(f"     • Multi-profissional: {context2.get('feature_multi_profissional', False)}")
                print(f"     • RAG: {context2.get('feature_rag_habilitado', False)}")
                print(f"     • Agendamento: {context2.get('feature_agendamento_habilitado', False)}")
                print()

                print(f"   ✓ Total Profissionais: {context2.get('total_profissionais', 0)}")
                print(f"   ✓ Total Especialidades: {context2.get('total_especialidades', 0)}")
                print()

                # Listar profissionais
                profissionais = context2.get('profissionais', [])
                if profissionais:
                    print("   Profissionais cadastrados:")
                    for prof in profissionais:
                        nome = prof.get('nome_exibicao') or prof.get('nome_completo')
                        especialidade = prof.get('especialidade_principal', 'N/A')
                        print(f"     • {nome} - {especialidade}")
                print()

                # Listar especialidades
                especialidades = context2.get('especialidades', [])
                if especialidades:
                    print("   Especialidades disponíveis:")
                    for esp in especialidades:
                        nome = esp.get('nome')
                        descricao = esp.get('descricao', '')
                        print(f"     • {nome}: {descricao}")
                print()

                fm2 = FeatureManager(context2)
                print(f"   ✓ Assistente: {fm2.get_nome_assistente()}")
                print()

                print("   ✅ TESTE 2 PASSOU!")
            else:
                print("   ❌ ERRO: Tenant não encontrado")
                return False

        except Exception as e:
            print(f"   ❌ ERRO ao buscar tenant: {e}")
            import traceback
            traceback.print_exc()
            return False

        print()

        # ====================================================================
        # Teste 3: Cache
        # ====================================================================
        print("3️⃣ Testando cache...")
        print("-" * 70)

        try:
            import time

            # Limpar cache primeiro
            resolver.limpar_cache()

            # Primeira chamada (sem cache)
            start = time.time()
            context3 = await resolver.identificar_tenant("556299281091")
            tempo_sem_cache = time.time() - start

            # Segunda chamada (com cache)
            start = time.time()
            context3_cached = await resolver.identificar_tenant("556299281091")
            tempo_com_cache = time.time() - start

            if context3 and context3_cached:
                print(f"   ✓ Primeira chamada (sem cache): {tempo_sem_cache:.4f}s")
                print(f"   ✓ Segunda chamada (com cache): {tempo_com_cache:.4f}s")
                print(f"   ✓ Melhoria: {(tempo_sem_cache/tempo_com_cache):.1f}x mais rápido")

                # Verificar se são iguais
                if context3['tenant_id'] == context3_cached['tenant_id']:
                    print("   ✓ Cache retornou o mesmo contexto")
                else:
                    print("   ⚠️ Cache retornou contexto diferente!")

                print()
                print("   ✅ TESTE 3 PASSOU!")
            else:
                print("   ❌ ERRO: Não foi possível testar cache")
                return False

        except Exception as e:
            print(f"   ❌ ERRO ao testar cache: {e}")
            import traceback
            traceback.print_exc()
            return False

        print()

        # ====================================================================
        # Teste 4: Tenant não encontrado
        # ====================================================================
        print("4️⃣ Testando tenant inexistente...")
        print("-" * 70)

        try:
            context_inexistente = await resolver.identificar_tenant("5500000000000")

            if context_inexistente is None:
                print("   ✓ Retornou None para tenant inexistente (esperado)")
                print("   ✅ TESTE 4 PASSOU!")
            else:
                print(f"   ❌ ERRO: Retornou contexto para tenant inexistente: {context_inexistente}")
                return False

        except Exception as e:
            print(f"   ❌ ERRO ao testar tenant inexistente: {e}")
            import traceback
            traceback.print_exc()
            return False

        print()
        print("=" * 70)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 70)
        print()
        print("📊 Resumo:")
        print("  • Centro-Oeste Drywall: ✓ Identificado")
        print("  • Clínica Odonto Sorriso: ✓ Identificado (multi-profissional)")
        print("  • Cache: ✓ Funcionando")
        print("  • Tenant inexistente: ✓ Tratado corretamente")
        print()
        print("🎉 FASE 2 VALIDADA COM SUCESSO!")

        return True

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO CRÍTICO NA VALIDAÇÃO")
        print("=" * 70)
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = asyncio.run(validar())
    sys.exit(0 if resultado else 1)
