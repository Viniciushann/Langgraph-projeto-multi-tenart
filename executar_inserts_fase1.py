#!/usr/bin/env python3
"""
Script para executar os INSERTs da Fase 1 - Multi-Tenant
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar .env.development
env_path = os.path.join('Langcham-fluxo-atendimento', '.env.development')
load_dotenv(env_path)

# Credenciais Supabase DEV
SUPABASE_URL = "https://wmzhbgcqugtctnzyinqw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtemhiZ2NxdWd0Y3RuenlpbnF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3NTQ5NDAsImV4cCI6MjA3NzMzMDk0MH0.pziIBNSJfex-dEJDJ0NeU7awjadoJXg87a8TONc4Xic"

# Credenciais do .env
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY', '8773E1C40430-4626-B896-1302789BA4D9')

print("=" * 70)
print("🚀 EXECUTANDO INSERTS - FASE 1")
print("=" * 70)
print()

# Conectar
print("📡 Conectando no Supabase DEV...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Conectado!\n")

# ============================================
# PARTE 1: CENTRO-OESTE DRYWALL
# ============================================

print("1️⃣ Inserindo CENTRO-OESTE DRYWALL...")
try:
    tenant_centro_oeste = supabase.table('tenants').insert({
        'nome_empresa': 'Centro-Oeste Drywall',
        'segmento': 'Construção Civil - Drywall',
        'email': 'contato@centrooeste.com.br',
        'telefone': '556299281091',
        'whatsapp_numero': '556299281091',
        'whatsapp_sender_id': 'Centro_oeste_draywal',
        'evolution_api_url': 'https://evolution.centrooestedrywalldry.com.br',
        'evolution_api_key': WHATSAPP_API_KEY,
        'google_calendar_id': 'centrooestedrywalldry@gmail.com',
        'ativo': True,
        'plano': 'pro',
        'preco_mensal': 0.00,
        'metadata': {'cliente_desde': '2024', 'nota': 'Cliente piloto do sistema'}
    }).execute()

    tenant_centro_id = tenant_centro_oeste.data[0]['id']
    print(f"   ✅ Tenant criado: {tenant_centro_id}")

    # Features
    supabase.table('tenant_features').insert({
        'tenant_id': tenant_centro_id,
        'atendimento_basico': True,
        'transcricao_audio': True,
        'analise_imagem': True,
        'rag_habilitado': True,
        'agendamento_habilitado': True,
        'multi_profissional': False,
        'multi_numero': False,
        'analytics_avancado': False,
        'limite_documentos_rag': 500,
        'limite_agendamentos_mes': 1000,
        'tempo_agrupamento_mensagens': 13
    }).execute()
    print("   ✅ Features configuradas")

    # Prompt
    supabase.table('tenant_prompts').insert({
        'tenant_id': tenant_centro_id,
        'nome_assistente': 'Carol',
        'descricao_empresa': 'Centro-Oeste Drywall - Especializada em instalação de Drywall em Goiânia',
        'system_prompt': '''Você é Carol, assistente virtual da Centro-Oeste Drywall, especializada em instalação de Drywall.

Suas responsabilidades:
1. Atender clientes de forma cordial e profissional
2. Agendar visitas técnicas usando a ferramenta de agendamento
3. Responder dúvidas sobre serviços de Drywall
4. Buscar informações na base de conhecimento quando necessário

Diretrizes:
- Seja sempre educada e prestativa
- Use linguagem clara e acessível
- Ao agendar, confirme todos os detalhes
- Se não souber, busque na base de conhecimento ou peça para o cliente aguardar contato do técnico
- Nunca invente informações''',
        'mensagem_boas_vindas': 'Olá! 👋 Eu sou a Carol, assistente virtual da Centro-Oeste Drywall! Como posso ajudar você hoje?',
        'mensagem_fora_horario': 'Nosso horário de atendimento é de segunda a sexta, das 8h às 18h. Deixe sua mensagem que respondemos no próximo dia útil!',
        'mensagem_erro': 'Desculpe, tive um problema técnico. Por favor, tente novamente em alguns instantes.',
        'modelo_llm': 'gpt-4o',
        'temperatura': 0.7,
        'max_tokens': 1000,
        'tom_voz': 'amigavel'
    }).execute()
    print("   ✅ Prompt configurado")

    # Profissional
    supabase.table('profissionais').insert({
        'tenant_id': tenant_centro_id,
        'nome_completo': 'Técnico Centro-Oeste Drywall',
        'nome_exibicao': 'Técnico',
        'especialidade_principal': 'Instalação de Drywall',
        'telefone': '55628540075',
        'whatsapp': '55628540075',
        'google_calendar_id': 'centrooestedrywalldry@gmail.com',
        'horarios_atendimento': {
            'segunda': [{'inicio': '08:00', 'fim': '18:00'}],
            'terca': [{'inicio': '08:00', 'fim': '18:00'}],
            'quarta': [{'inicio': '08:00', 'fim': '18:00'}],
            'quinta': [{'inicio': '08:00', 'fim': '18:00'}],
            'sexta': [{'inicio': '08:00', 'fim': '18:00'}],
            'sabado': [{'inicio': '08:00', 'fim': '12:00'}],
            'domingo': []
        },
        'duracao_consulta_minutos': 120,
        'ativo': True,
        'aceita_novos_pacientes': True,
        'bio': 'Técnico especializado em instalação de Drywall com mais de 10 anos de experiência'
    }).execute()
    print("   ✅ Profissional cadastrado")

    # Migrar clientes
    result = supabase.table('clients_dev').update({
        'tenant_id': tenant_centro_id
    }).is_('tenant_id', 'null').execute()
    print(f"   ✅ {len(result.data) if result.data else 0} clientes migrados")

    # Migrar documentos
    result = supabase.table('conhecimento_dev').update({
        'tenant_id': tenant_centro_id
    }).is_('tenant_id', 'null').execute()
    print(f"   ✅ {len(result.data) if result.data else 0} documentos migrados")

except Exception as e:
    print(f"   ❌ Erro: {e}")

# ============================================
# PARTE 2: CLÍNICA ODONTO SORRISO (TESTE)
# ============================================

print("\n2️⃣ Inserindo CLÍNICA ODONTO SORRISO (teste)...")
try:
    tenant_odonto = supabase.table('tenants').insert({
        'nome_empresa': 'Clínica Odonto Sorriso',
        'segmento': 'Odontologia',
        'email': 'contato@odontosorriso.com.br',
        'telefone': '5562999999999',
        'whatsapp_numero': '5562999999999',
        'whatsapp_sender_id': 'odonto_teste',
        'ativo': True,
        'plano': 'basic',
        'metadata': {'tenant_tipo': 'teste', 'nota': 'Tenant para validação do sistema multi-tenant'}
    }).execute()

    tenant_odonto_id = tenant_odonto.data[0]['id']
    print(f"   ✅ Tenant criado: {tenant_odonto_id}")

    # Features
    supabase.table('tenant_features').insert({
        'tenant_id': tenant_odonto_id,
        'atendimento_basico': True,
        'transcricao_audio': True,
        'analise_imagem': True,
        'rag_habilitado': True,
        'agendamento_habilitado': True,
        'multi_profissional': True,  # Multi-profissional ATIVO
        'multi_numero': False
    }).execute()
    print("   ✅ Features configuradas")

    # Prompt
    supabase.table('tenant_prompts').insert({
        'tenant_id': tenant_odonto_id,
        'nome_assistente': 'Dra. Ana',
        'descricao_empresa': 'Clínica Odonto Sorriso - Atendimento odontológico completo',
        'system_prompt': '''Você é Dra. Ana, assistente virtual da Clínica Odonto Sorriso.

Suas responsabilidades:
1. Atender pacientes de forma acolhedora
2. Agendar consultas com dentistas da clínica
3. Identificar especialidade necessária (implante, ortodontia, etc)
4. Fornecer informações sobre tratamentos

Diretrizes:
- Seja sempre empática e profissional
- Pergunte sobre a especialidade necessária
- Sugira o dentista mais adequado
- Confirme todos detalhes do agendamento''',
        'mensagem_boas_vindas': 'Olá! 😊 Sou a Dra. Ana, assistente da Clínica Odonto Sorriso. Como posso cuidar do seu sorriso hoje?',
        'modelo_llm': 'gpt-4o',
        'temperatura': 0.7,
        'tom_voz': 'profissional'
    }).execute()
    print("   ✅ Prompt configurado")

    # Especialidades
    especialidades_data = [
        {
            'tenant_id': tenant_odonto_id,
            'nome': 'Implantes',
            'descricao': 'Implantes dentários e próteses fixas',
            'keywords': ['implante', 'implante dentário', 'dente fixo', 'prótese fixa'],
            'ativa': True
        },
        {
            'tenant_id': tenant_odonto_id,
            'nome': 'Ortodontia',
            'descricao': 'Aparelhos ortodônticos e alinhadores',
            'keywords': ['aparelho', 'ortodontia', 'alinhar dentes', 'corrigir mordida'],
            'ativa': True
        },
        {
            'tenant_id': tenant_odonto_id,
            'nome': 'Clínico Geral',
            'descricao': 'Atendimento odontológico geral',
            'keywords': ['limpeza', 'canal', 'obturação', 'extração', 'dor de dente'],
            'ativa': True
        }
    ]
    supabase.table('especialidades').insert(especialidades_data).execute()
    print("   ✅ 3 especialidades cadastradas")

    # Profissionais
    profissionais_data = [
        {
            'tenant_id': tenant_odonto_id,
            'nome_completo': 'Dr. João Silva',
            'nome_exibicao': 'Dr. João',
            'crm_cro': 'CRO-GO 12345',
            'especialidade_principal': 'Implantes',
            'email': 'joao@odontosorriso.com.br',
            'telefone': '5562988888888',
            'duracao_consulta_minutos': 60,
            'ativo': True,
            'bio': 'Especialista em implantodontia com 15 anos de experiência'
        },
        {
            'tenant_id': tenant_odonto_id,
            'nome_completo': 'Dra. Maria Santos',
            'nome_exibicao': 'Dra. Maria',
            'crm_cro': 'CRO-GO 54321',
            'especialidade_principal': 'Ortodontia',
            'email': 'maria@odontosorriso.com.br',
            'telefone': '5562977777777',
            'duracao_consulta_minutos': 45,
            'ativo': True,
            'bio': 'Ortodontista especializada em alinhadores invisíveis'
        },
        {
            'tenant_id': tenant_odonto_id,
            'nome_completo': 'Dr. Pedro Costa',
            'nome_exibicao': 'Dr. Pedro',
            'crm_cro': 'CRO-GO 98765',
            'especialidade_principal': 'Clínico Geral',
            'email': 'pedro@odontosorriso.com.br',
            'telefone': '5562966666666',
            'duracao_consulta_minutos': 30,
            'ativo': True,
            'bio': 'Clínico geral com atendimento a todas as idades'
        }
    ]
    supabase.table('profissionais').insert(profissionais_data).execute()
    print("   ✅ 3 profissionais cadastrados")

except Exception as e:
    print(f"   ❌ Erro: {e}")

# ============================================
# VALIDAÇÃO
# ============================================

print("\n" + "=" * 70)
print("📊 VALIDAÇÃO FINAL")
print("=" * 70)

tenants = supabase.table('tenants').select('*').execute()
print(f"\n✅ {len(tenants.data)} tenants criados:")
for t in tenants.data:
    print(f"   • {t['nome_empresa']} ({t['plano']}) - {t['whatsapp_numero']}")

features = supabase.table('tenant_features').select('count', count='exact').execute()
print(f"\n✅ {features.count} configurações de features")

prompts = supabase.table('tenant_prompts').select('count', count='exact').execute()
print(f"✅ {prompts.count} prompts configurados")

profissionais = supabase.table('profissionais').select('count', count='exact').execute()
print(f"✅ {profissionais.count} profissionais cadastrados")

especialidades = supabase.table('especialidades').select('count', count='exact').execute()
print(f"✅ {especialidades.count} especialidades")

clientes = supabase.table('clients_dev').select('id', count='exact').not_.is_('tenant_id', 'null').execute()
print(f"✅ {clientes.count} clientes migrados")

docs = supabase.table('conhecimento_dev').select('id', count='exact').not_.is_('tenant_id', 'null').execute()
print(f"✅ {docs.count} documentos migrados")

print("\n🎉 FASE 1 CONCLUÍDA COM SUCESSO!")
print("=" * 70)
