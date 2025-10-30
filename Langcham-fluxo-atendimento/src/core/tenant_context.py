from typing import TypedDict, Optional, List, Dict, Any
from uuid import UUID

class TenantContext(TypedDict, total=False):
    tenant_id: UUID
    tenant_nome: str
    tenant_segmento: Optional[str]
    tenant_plano: str
    whatsapp_numero: str
    whatsapp_sender_id: str
    evolution_api_url: str
    evolution_api_key: str
    google_calendar_id: Optional[str]
    feature_transcricao_audio: bool
    feature_analise_imagem: bool
    feature_rag_habilitado: bool
    feature_agendamento_habilitado: bool
    feature_multi_profissional: bool
    feature_multi_numero: bool
    feature_analytics_avancado: bool
    limite_documentos_rag: int
    limite_agendamentos_mes: int
    tempo_agrupamento_mensagens: int
    max_mensagens_dia: int
    nome_assistente: str
    descricao_empresa: Optional[str]
    system_prompt: str
    mensagem_boas_vindas: Optional[str]
    mensagem_fora_horario: Optional[str]
    mensagem_erro: Optional[str]
    modelo_llm: str
    temperatura: float
    max_tokens: int
    tom_voz: str
    profissionais: List[Dict[str, Any]]
    total_profissionais: int
    especialidades: List[Dict[str, Any]]
    total_especialidades: int
    metadata: Dict[str, Any]
