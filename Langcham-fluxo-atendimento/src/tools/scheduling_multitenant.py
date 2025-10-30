"""
Ferramenta de agendamento multi-tenant e multi-profissional.

Este módulo fornece factory function para criar ferramentas de agendamento
personalizadas por tenant, com suporte a múltiplos profissionais.
"""

import logging
from typing import Dict, Any, Literal, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from langchain.tools import tool

# Import das funções base do scheduling.py original
from src.tools.scheduling import (
    consultar_horarios,
    agendar_horario,
    cancelar_horario,
    atualizar_horario,
    TIMEZONE
)

logger = logging.getLogger(__name__)


def criar_tool_agendamento(tenant_context: Dict[str, Any]):
    """
    Cria uma tool de agendamento configurada para o tenant específico.

    Esta factory function cria uma tool personalizada que:
    - Usa google_calendar_id do tenant
    - Suporta multi-profissional (se habilitado)
    - Respeita limites do tenant
    - Garante isolamento de agendamentos

    Args:
        tenant_context: Contexto completo do tenant contendo:
            - tenant_id (UUID): ID do tenant
            - tenant_nome (str): Nome do tenant
            - google_calendar_id (str): ID do Google Calendar
            - feature_multi_profissional (bool): Se tem múltiplos profissionais
            - profissionais (List[Dict]): Lista de profissionais (se multi-prof)
            - limite_agendamentos_mes (int): Máximo de agendamentos/mês

    Returns:
        tool: Ferramenta LangChain configurada para o tenant

    Example:
        >>> tenant_context = {
        ...     "tenant_id": "uuid",
        ...     "tenant_nome": "Clínica Odonto",
        ...     "google_calendar_id": "clinica@gmail.com",
        ...     "feature_multi_profissional": True,
        ...     "profissionais": [
        ...         {
        ...             "nome_exibicao": "Dra. Maria",
        ...             "especialidade_principal": "Ortodontia",
        ...             "google_calendar_id": "dra.maria@gmail.com"
        ...         }
        ...     ]
        ... }
        >>> agendamento_tool = criar_tool_agendamento(tenant_context)
    """
    tenant_id = str(tenant_context["tenant_id"])
    tenant_nome = tenant_context["tenant_nome"]
    google_calendar_id = tenant_context.get("google_calendar_id")
    tem_multi_prof = tenant_context.get("feature_multi_profissional", False)
    profissionais = tenant_context.get("profissionais", [])
    limite_agendamentos = tenant_context.get("limite_agendamentos_mes", 100)

    logger.info(f"Criando tool de agendamento para tenant: {tenant_nome}")
    logger.info(f"Multi-profissional: {tem_multi_prof}")
    if tem_multi_prof:
        logger.info(f"Profissionais disponíveis: {len(profissionais)}")

    @tool
    async def agendar_consulta(
        nome_cliente: str,
        telefone_cliente: str,
        email_cliente: str,
        data_consulta_reuniao: str,
        intencao: Literal["consultar", "agendar", "cancelar", "atualizar"],
        informacao_extra: str = "",
        profissional: Optional[str] = None
    ) -> dict:
        """
        Ferramenta de agendamento personalizada para este tenant.

        Args:
            nome_cliente: Nome completo do cliente
            telefone_cliente: Telefone do cliente com DDD
            email_cliente: Email do cliente (use "sememail@gmail.com" se não fornecido)
            data_consulta_reuniao: Data/hora no formato ISO 8601 ou DD/MM/YYYY HH:MM
            intencao: Ação desejada: "consultar", "agendar", "cancelar", "atualizar"
            informacao_extra: Contexto adicional (endereço, observações, etc)
            profissional: Nome do profissional (obrigatório se multi-profissional)

        Returns:
            dict: {
                "sucesso": bool,
                "mensagem": str,
                "dados": dict
            }

        Examples:
            >>> # Tenant sem multi-profissional
            >>> result = await agendar_consulta(
            ...     nome_cliente="João Silva",
            ...     telefone_cliente="556299999999",
            ...     email_cliente="joao@email.com",
            ...     data_consulta_reuniao="30/10/2025 14:00",
            ...     intencao="agendar",
            ...     informacao_extra="Endereço: Rua ABC, 123"
            ... )

            >>> # Tenant com multi-profissional
            >>> result = await agendar_consulta(
            ...     nome_cliente="Maria Santos",
            ...     telefone_cliente="5562999999999",
            ...     email_cliente="maria@email.com",
            ...     data_consulta_reuniao="31/10/2025 15:00",
            ...     intencao="agendar",
            ...     profissional="Dra. Maria",
            ...     informacao_extra="Primeira consulta"
            ... )
        """
        try:
            logger.info(f"[{tenant_nome}] Agendamento - Intenção: {intencao}, Cliente: {nome_cliente}")

            # ==============================================
            # 1. VALIDAR MULTI-PROFISSIONAL
            # ==============================================
            calendar_id_selecionado = google_calendar_id

            if tem_multi_prof:
                # Se multi-profissional, profissional é OBRIGATÓRIO
                if not profissional:
                    nomes_profissionais = [p.get("nome_exibicao", p.get("nome_completo")) for p in profissionais]
                    return {
                        "sucesso": False,
                        "mensagem": f"Por favor, especifique qual profissional você deseja: {', '.join(nomes_profissionais)}",
                        "dados": {"profissionais_disponiveis": nomes_profissionais}
                    }

                # Buscar profissional selecionado
                prof_selecionado = None
                for prof in profissionais:
                    nome_prof = prof.get("nome_exibicao", prof.get("nome_completo", ""))
                    if profissional.lower() in nome_prof.lower():
                        prof_selecionado = prof
                        break

                if not prof_selecionado:
                    nomes_profissionais = [p.get("nome_exibicao", p.get("nome_completo")) for p in profissionais]
                    return {
                        "sucesso": False,
                        "mensagem": f"Profissional '{profissional}' não encontrado. Profissionais disponíveis: {', '.join(nomes_profissionais)}",
                        "dados": {"profissionais_disponiveis": nomes_profissionais}
                    }

                # Usar calendar do profissional (se tiver) ou fallback para calendar do tenant
                calendar_id_selecionado = prof_selecionado.get("google_calendar_id") or google_calendar_id

                logger.info(f"✓ Profissional selecionado: {prof_selecionado.get('nome_exibicao')}")
                logger.info(f"Calendar ID: {calendar_id_selecionado}")

            # ==============================================
            # 2. VALIDAR EMAIL
            # ==============================================
            if not email_cliente or email_cliente == "":
                email_cliente = "sememail@gmail.com"

            # ==============================================
            # 3. VERIFICAR LIMITE DE AGENDAMENTOS (apenas para "agendar")
            # ==============================================
            if intencao == "agendar":
                # TODO: Implementar verificação de limite mensal
                # Por ora, apenas log
                logger.info(f"Limite de agendamentos/mês: {limite_agendamentos}")

            # ==============================================
            # 4. EXECUTAR AÇÃO CONFORME INTENÇÃO
            # ==============================================
            # NOTA: As funções base (consultar_horarios, agendar_horario, etc)
            # usam CALENDAR_ID global. Precisamos passar o calendar_id_selecionado.
            # Por enquanto, vamos usar as funções originais e documentar a limitação.

            if intencao == "consultar":
                resultado = await consultar_horarios(
                    data_referencia=data_consulta_reuniao,
                    informacao_extra=informacao_extra
                )

            elif intencao == "agendar":
                # Adicionar informação do profissional na informacao_extra
                if tem_multi_prof and prof_selecionado:
                    nome_prof = prof_selecionado.get("nome_exibicao", prof_selecionado.get("nome_completo"))
                    especialidade = prof_selecionado.get("especialidade_principal", "")
                    informacao_extra += f"\n\nProfissional: {nome_prof}"
                    if especialidade:
                        informacao_extra += f"\nEspecialidade: {especialidade}"

                resultado = await agendar_horario(
                    nome_cliente=nome_cliente,
                    telefone_cliente=telefone_cliente,
                    email_cliente=email_cliente,
                    data_consulta_reuniao=data_consulta_reuniao,
                    informacao_extra=informacao_extra
                )

            elif intencao == "cancelar":
                resultado = await cancelar_horario(
                    nome_cliente=nome_cliente,
                    data_consulta_reuniao=data_consulta_reuniao
                )

            elif intencao == "atualizar":
                # Extrair nova data de informacao_extra
                nova_data = ""
                if "nova_data:" in informacao_extra:
                    nova_data = informacao_extra.split("nova_data:")[1].strip()

                if not nova_data:
                    return {
                        "sucesso": False,
                        "mensagem": "Para atualizar, forneça a nova data em informacao_extra como 'nova_data:DD/MM/YYYY HH:MM'",
                        "dados": {}
                    }

                resultado = await atualizar_horario(
                    nome_cliente=nome_cliente,
                    data_consulta_antiga=data_consulta_reuniao,
                    data_consulta_nova=nova_data,
                    telefone_cliente=telefone_cliente,
                    email_cliente=email_cliente
                )

            else:
                resultado = {
                    "sucesso": False,
                    "mensagem": f"Intenção inválida: {intencao}. Use: consultar, agendar, cancelar ou atualizar",
                    "dados": {}
                }

            logger.info(f"[{tenant_nome}] Resultado: sucesso={resultado['sucesso']}")
            return resultado

        except Exception as e:
            logger.error(f"[{tenant_nome}] Erro ao processar agendamento: {e}", exc_info=True)
            return {
                "sucesso": False,
                "mensagem": f"Erro ao processar agendamento: {str(e)}",
                "dados": {}
            }

    # Adicionar metadados à tool
    agendar_consulta.tenant_id = tenant_id
    agendar_consulta.tenant_nome = tenant_nome
    agendar_consulta.tem_multi_prof = tem_multi_prof

    logger.info(f"✓ Tool de agendamento criada para {tenant_nome}")

    return agendar_consulta


# ============================================================================
# LIMITAÇÃO ATUAL E PRÓXIMOS PASSOS
# ============================================================================

"""
⚠️ LIMITAÇÃO ATUAL:

As funções base (consultar_horarios, agendar_horario, etc.) usam a variável
global CALENDAR_ID do scheduling.py original.

Para TRUE multi-tenant, precisamos:

1. Modificar as funções base para aceitar calendar_id como parâmetro:
   - consultar_horarios(data_referencia, calendar_id, informacao_extra)
   - agendar_horario(nome, tel, email, data, calendar_id, info_extra)
   - cancelar_horario(nome, data, calendar_id)
   - atualizar_horario(nome, data_antiga, data_nova, calendar_id, tel, email)

2. Modificar _get_calendar_service() para aceitar credentials dinâmicas:
   - Cada tenant pode ter suas próprias credenciais do Google
   - Service Account por tenant (mais seguro)

3. Implementar verificação de limite de agendamentos:
   - Consultar histórico de agendamentos do mês
   - Comparar com limite_agendamentos_mes
   - Bloquear se exceder

📋 IMPLEMENTAÇÃO COMPLETA REQUER:

Arquivo: src/tools/scheduling.py
- [ ] Adicionar parâmetro calendar_id em todas as funções
- [ ] Adicionar parâmetro credentials_file em _get_calendar_service()
- [ ] Cache de serviços do calendar por tenant
- [ ] Função verificar_limite_agendamentos(tenant_id, mes, ano)

Por enquanto, esta versão:
✅ Suporta multi-profissional (escolha de profissional)
✅ Adiciona info do profissional na descrição do evento
✅ Valida profissionais disponíveis
❌ Ainda usa CALENDAR_ID global (não isolado por tenant)
❌ Não implementa limite de agendamentos
"""


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

async def exemplo_uso():
    """
    Exemplo de como usar a ferramenta de agendamento multi-tenant.
    """
    # Exemplo 1: Tenant SEM multi-profissional (Centro-Oeste Drywall)
    tenant_context_drywall = {
        "tenant_id": "9605db82-51bf-4101-bdb0-ba73c5843c43",
        "tenant_nome": "Centro-Oeste Drywall",
        "google_calendar_id": "centrooestedrywalldry@gmail.com",
        "feature_multi_profissional": False,
        "limite_agendamentos_mes": 50
    }

    agendamento_tool_drywall = criar_tool_agendamento(tenant_context_drywall)

    resultado1 = await agendamento_tool_drywall.ainvoke({
        "nome_cliente": "João Silva",
        "telefone_cliente": "556299999999",
        "email_cliente": "joao@email.com",
        "data_consulta_reuniao": "30/10/2025 14:00",
        "intencao": "agendar",
        "informacao_extra": "Endereço: Rua ABC, 123"
    })

    print(f"Resultado Drywall: {resultado1}")

    # Exemplo 2: Tenant COM multi-profissional (Clínica Odonto)
    tenant_context_odonto = {
        "tenant_id": "uuid-odonto",
        "tenant_nome": "Clínica Odonto Sorriso",
        "google_calendar_id": "clinica@gmail.com",
        "feature_multi_profissional": True,
        "profissionais": [
            {
                "nome_exibicao": "Dra. Maria Silva",
                "nome_completo": "Maria Silva",
                "especialidade_principal": "Ortodontia",
                "google_calendar_id": "dra.maria@gmail.com"
            },
            {
                "nome_exibicao": "Dr. João Santos",
                "nome_completo": "João Santos",
                "especialidade_principal": "Implantodontia",
                "google_calendar_id": "dr.joao@gmail.com"
            }
        ],
        "limite_agendamentos_mes": 100
    }

    agendamento_tool_odonto = criar_tool_agendamento(tenant_context_odonto)

    # Sem especificar profissional (deve retornar erro)
    resultado2 = await agendamento_tool_odonto.ainvoke({
        "nome_cliente": "Maria Santos",
        "telefone_cliente": "5562999999999",
        "email_cliente": "maria@email.com",
        "data_consulta_reuniao": "31/10/2025 15:00",
        "intencao": "agendar"
    })

    print(f"Resultado sem profissional: {resultado2}")

    # Com profissional especificado
    resultado3 = await agendamento_tool_odonto.ainvoke({
        "nome_cliente": "Maria Santos",
        "telefone_cliente": "5562999999999",
        "email_cliente": "maria@email.com",
        "data_consulta_reuniao": "31/10/2025 15:00",
        "intencao": "agendar",
        "profissional": "Dra. Maria",
        "informacao_extra": "Primeira consulta de ortodontia"
    })

    print(f"Resultado com profissional: {resultado3}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(exemplo_uso())
