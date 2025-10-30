import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from src.clients.supabase_client import SupabaseClient
from src.core.tenant_context import TenantContext
from src.models.tenant import (
    TenantModel, TenantFeaturesModel, TenantPromptsModel, ProfissionalModel, EspecialidadeModel
)

logger = logging.getLogger(__name__)

class TenantResolver:
    """
    Resolve qual tenant enviou a mensagem e carrega suas configurações
    """
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client
        self._cache: Dict[str, TenantContext] = {}

    async def identificar_tenant(self, whatsapp_numero: str, usar_cache: bool = True) -> Optional[TenantContext]:
        """
        Identifica o tenant pelo número de WhatsApp e carrega todo contexto
        """
        try:
            if usar_cache and whatsapp_numero in self._cache:
                return self._cache[whatsapp_numero]
            tenant = await self._buscar_tenant_por_numero(whatsapp_numero)
            if not tenant:
                logger.warning(f"Tenant não encontrado: {whatsapp_numero}")
                return None
            tenant_context = await self._carregar_configuracoes_completas(tenant)
            self._cache[whatsapp_numero] = tenant_context
            return tenant_context
        except Exception as e:
            logger.error(f"Erro ao identificar tenant: {e}", exc_info=True)
            return None

    async def _buscar_tenant_por_numero(self, whatsapp_numero: str) -> Optional[TenantModel]:
        """
        Busca tenant pelo número principal e por números adicionais.
        """
        try:
            # Buscar tenant principal
            response = self.supabase.client.table("tenants").select("*").eq("whatsapp_numero", whatsapp_numero).eq("ativo", True).maybe_single().execute()
            if response.data:
                return TenantModel(**response.data)
            # Buscar em tenant_phone_numbers (não implementado)
            return None
        except Exception as e:
            logger.error(f"Erro buscar tenant: {e}", exc_info=True)
            return None

    async def _carregar_configuracoes_completas(self, tenant: TenantModel) -> TenantContext:
        try:
            features = await self._carregar_features(tenant.id)
            prompts = await self._carregar_prompts(tenant.id)
            profissionais: List[ProfissionalModel] = []
            especialidades: List[EspecialidadeModel] = []
            if features and features.multi_profissional:
                profissionais = await self._carregar_profissionais(tenant.id)
                especialidades = await self._carregar_especialidades(tenant.id)
            tenant.features = features
            tenant.prompts = prompts
            tenant.profissionais = profissionais
            tenant.especialidades = especialidades
            return self._montar_tenant_context(tenant)
        except Exception as e:
            logger.error(f"Erro carregar configurações tenant: {e}", exc_info=True)
            raise

    async def _carregar_features(self, tenant_id: UUID) -> Optional[TenantFeaturesModel]:
        try:
            response = self.supabase.client.table("tenant_features").select("*").eq("tenant_id", str(tenant_id)).maybe_single().execute()
            if response.data:
                return TenantFeaturesModel(**response.data)
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar features: {e}", exc_info=True)
            return None

    async def _carregar_prompts(self, tenant_id: UUID) -> Optional[TenantPromptsModel]:
        try:
            response = self.supabase.client.table("tenant_prompts").select("*").eq("tenant_id", str(tenant_id)).maybe_single().execute()
            if response.data:
                return TenantPromptsModel(**response.data)
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar prompts: {e}", exc_info=True)
            return None

    async def _carregar_profissionais(self, tenant_id: UUID) -> List[ProfissionalModel]:
        try:
            response = self.supabase.client.table("profissionais").select("*").eq("tenant_id", str(tenant_id)).eq("ativo", True).execute()
            if response.data:
                return [ProfissionalModel(**row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar profissionais: {e}", exc_info=True)
            return []

    async def _carregar_especialidades(self, tenant_id: UUID) -> List[EspecialidadeModel]:
        try:
            response = self.supabase.client.table("especialidades").select("*").eq("tenant_id", str(tenant_id)).eq("ativa", True).execute()
            if response.data:
                return [EspecialidadeModel(**row) for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar especialidades: {e}", exc_info=True)
            return []

    def _montar_tenant_context(self, tenant: TenantModel) -> TenantContext:
        context: TenantContext = {
            'tenant_id': tenant.id,
            'tenant_nome': tenant.nome_empresa,
            'tenant_segmento': tenant.segmento,
            'tenant_plano': tenant.plano,
            'whatsapp_numero': tenant.whatsapp_numero,
            'whatsapp_sender_id': tenant.whatsapp_sender_id or "",
            'evolution_api_url': tenant.evolution_api_url or "",
            'evolution_api_key': tenant.evolution_api_key or "",
            'google_calendar_id': tenant.google_calendar_id,
            'metadata': tenant.metadata
        }
        # Features
        if tenant.features:
            context.update({
                'feature_transcricao_audio': tenant.features.transcricao_audio,
                'feature_analise_imagem': tenant.features.analise_imagem,
                'feature_rag_habilitado': tenant.features.rag_habilitado,
                'feature_agendamento_habilitado': tenant.features.agendamento_habilitado,
                'feature_multi_profissional': tenant.features.multi_profissional,
                'feature_multi_numero': tenant.features.multi_numero,
                'feature_analytics_avancado': tenant.features.analytics_avancado,
                'limite_documentos_rag': tenant.features.limite_documentos_rag,
                'limite_agendamentos_mes': tenant.features.limite_agendamentos_mes,
                'tempo_agrupamento_mensagens': tenant.features.tempo_agrupamento_mensagens,
            })
        context['max_mensagens_dia'] = tenant.max_mensagens_dia
        if tenant.prompts:
            context.update({
                'nome_assistente': tenant.prompts.nome_assistente,
                'descricao_empresa': tenant.prompts.descricao_empresa,
                'system_prompt': tenant.prompts.system_prompt,
                'mensagem_boas_vindas': tenant.prompts.mensagem_boas_vindas,
                'mensagem_fora_horario': tenant.prompts.mensagem_fora_horario,
                'mensagem_erro': tenant.prompts.mensagem_erro,
                'modelo_llm': tenant.prompts.modelo_llm,
                'temperatura': tenant.prompts.temperatura,
                'max_tokens': tenant.prompts.max_tokens,
                'tom_voz': tenant.prompts.tom_voz,
            })
        context['profissionais'] = [prof.model_dump() for prof in tenant.profissionais]
        context['total_profissionais'] = len(tenant.profissionais)
        context['especialidades'] = [esp.model_dump() for esp in tenant.especialidades]
        context['total_especialidades'] = len(tenant.especialidades)
        return context

    def limpar_cache(self, whatsapp_numero: Optional[str] = None):
        if whatsapp_numero:
            self._cache.pop(whatsapp_numero, None)
        else:
            self._cache.clear()
