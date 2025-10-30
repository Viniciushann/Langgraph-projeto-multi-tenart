"""
Ferramenta de busca RAG com filtro multi-tenant.

Este módulo fornece uma ferramenta dinâmica para busca na base de conhecimento
que respeita isolamento de dados entre tenants.
"""

import logging
from typing import Dict, Any
from langchain.tools import tool

from src.clients.supabase_client import criar_supabase_client
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def criar_tool_busca_rag(tenant_context: Dict[str, Any]):
    """
    Cria uma tool de busca RAG configurada para o tenant específico.

    Esta factory function cria uma tool personalizada que:
    - Filtra documentos apenas do tenant especificado
    - Respeita limites configurados no tenant_features
    - Garante isolamento de dados (segurança crítica!)

    Args:
        tenant_context: Contexto completo do tenant contendo:
            - tenant_id (UUID): ID do tenant
            - tenant_nome (str): Nome do tenant
            - limite_documentos_rag (int): Máximo de docs a retornar

    Returns:
        tool: Ferramenta LangChain configurada para o tenant

    Example:
        >>> tenant_context = {
        ...     "tenant_id": "9605db82-51bf-4101-bdb0-ba73c5843c43",
        ...     "tenant_nome": "Centro-Oeste Drywall",
        ...     "limite_documentos_rag": 5
        ... }
        >>> rag_tool = criar_tool_busca_rag(tenant_context)
        >>> # Usar com agent
        >>> tools = [rag_tool, agendamento_tool]
    """
    tenant_id = str(tenant_context["tenant_id"])
    tenant_nome = tenant_context["tenant_nome"]
    limite_docs = tenant_context.get("limite_documentos_rag", 5)

    logger.info(f"Criando tool de busca RAG para tenant: {tenant_nome} (limit={limite_docs})")

    @tool
    async def buscar_na_base_conhecimento(query: str) -> str:
        """
        Busca informações na base de conhecimento da empresa sobre serviços, preços e FAQ.

        Use esta ferramenta SEMPRE que o cliente perguntar sobre:
        - Serviços oferecidos ("Vocês fazem...?", "Tem serviço de...?")
        - Preços e orçamentos ("Quanto custa...?", "Qual o valor de...?")
        - Processos e procedimentos ("Como funciona...?", "Qual o prazo...?")
        - Garantias e políticas ("Tem garantia...?", "Qual a política de...?")
        - Área de atendimento ("Atendem em...?", "Cobrem qual região?")
        - Qualquer dúvida técnica ou específica sobre produtos/serviços

        Args:
            query: Pergunta ou termo de busca do cliente

        Returns:
            str: Informações encontradas na base de conhecimento ou mensagem
                indicando que não foi encontrado

        Example:
            >>> result = await buscar_na_base_conhecimento("preço de drywall")
            >>> print(result)
            "Informações encontradas:\n\n1. Instalação de drywall..."
        """
        try:
            logger.info(f"[{tenant_nome}] Buscando na base: '{query[:50]}...'")

            # Criar cliente Supabase
            supabase = criar_supabase_client(
                url=settings.supabase_url,
                key=settings.supabase_key
            )

            # Buscar documentos FILTRADOS por tenant_id (CRÍTICO!)
            docs = await supabase.buscar_documentos_relevantes(
                query=query,
                tenant_id=tenant_id,
                limit=limite_docs,
                similarity_threshold=0.7
            )

            if not docs or len(docs) == 0:
                logger.info(f"[{tenant_nome}] Nenhum documento encontrado para: '{query}'")
                return (
                    "Não encontrei informações específicas sobre isso na minha base de conhecimento. "
                    "Para te dar uma resposta precisa e detalhada, o ideal seria agendar uma "
                    "visita técnica ou conversar diretamente com nossa equipe."
                )

            # Formatar resultado
            resultado = "Informações encontradas na base de conhecimento:\n\n"

            for i, doc in enumerate(docs, 1):
                content = doc.get("content", "")
                similarity = doc.get("similarity", 0)

                # Adicionar conteúdo do documento
                resultado += f"{i}. {content}\n\n"

                # Log de similaridade (para debug)
                logger.debug(f"  Documento {i}: similaridade={similarity:.2f}")

            logger.info(f"[{tenant_nome}] ✓ Retornados {len(docs)} documentos relevantes")

            return resultado.strip()

        except Exception as e:
            logger.error(f"[{tenant_nome}] Erro ao buscar na base: {e}", exc_info=True)
            return (
                "Desculpe, tive um problema ao consultar a base de conhecimento no momento. "
                "Mas posso te ajudar de outras formas! Podemos agendar uma visita técnica "
                "ou você pode me fazer perguntas gerais sobre nossos serviços."
            )

    # Adicionar metadados à tool
    buscar_na_base_conhecimento.tenant_id = tenant_id
    buscar_na_base_conhecimento.tenant_nome = tenant_nome

    logger.info(f"✓ Tool de busca RAG criada para {tenant_nome}")

    return buscar_na_base_conhecimento


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

async def exemplo_uso():
    """
    Exemplo de como usar a ferramenta de busca RAG.
    """
    from src.core.tenant_resolver import TenantResolver
    from src.clients.supabase_client import criar_supabase_client

    # 1. Identificar tenant
    supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)
    resolver = TenantResolver(supabase)
    tenant_context = await resolver.identificar_tenant("556299281091")

    if not tenant_context:
        print("Tenant não encontrado")
        return

    # 2. Criar tool de busca
    rag_tool = criar_tool_busca_rag(tenant_context)

    # 3. Usar tool
    resultado = await rag_tool.ainvoke({"query": "preços de drywall"})
    print(resultado)


if __name__ == "__main__":
    import asyncio
    asyncio.run(exemplo_uso())
