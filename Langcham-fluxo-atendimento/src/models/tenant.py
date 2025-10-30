from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class TenantFeaturesModel(BaseModel):
    atendimento_basico: bool = True
    transcricao_audio: bool = True
    analise_imagem: bool = True
    rag_habilitado: bool = True
    agendamento_habilitado: bool = True
    multi_profissional: bool = False
    multi_numero: bool = False
    analytics_avancado: bool = False
    api_externa: bool = False
    webhooks_customizados: bool = False
    limite_documentos_rag: int = 100
    limite_agendamentos_mes: int = 500
    tempo_agrupamento_mensagens: int = 13

class TenantPromptsModel(BaseModel):
    nome_assistente: str = "Carol"
    descricao_empresa: Optional[str] = None
    system_prompt: str
    mensagem_boas_vindas: Optional[str] = None
    mensagem_fora_horario: Optional[str] = None
    mensagem_erro: Optional[str] = None
    mensagem_despedida: Optional[str] = None
    modelo_llm: str = "gpt-4o"
    temperatura: float = 0.7
    max_tokens: int = 1000
    idioma: str = "pt-BR"
    tom_voz: str = "amigavel"

class ProfissionalModel(BaseModel):
    id: UUID
    tenant_id: UUID
    nome_completo: str
    nome_exibicao: Optional[str] = None
    crm_cro: Optional[str] = None
    especialidade_principal: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    google_calendar_id: Optional[str] = None
    horarios_atendimento: Dict[str, Any] = {}
    duracao_consulta_minutos: int = 60
    intervalo_entre_consultas: int = 0
    prioridade: int = 1
    ativo: bool = True
    aceita_novos_pacientes: bool = True
    bio: Optional[str] = None
    observacoes: Optional[str] = None

class EspecialidadeModel(BaseModel):
    id: UUID
    tenant_id: UUID
    nome: str
    descricao: Optional[str] = None
    keywords: List[str] = []
    cor_hex: str = "#3B82F6"
    ativa: bool = True

class TenantModel(BaseModel):
    id: UUID
    nome_empresa: str
    segmento: Optional[str] = None
    email: str
    telefone: Optional[str] = None
    whatsapp_numero: str
    whatsapp_sender_id: Optional[str] = None
    evolution_api_url: Optional[str] = None
    evolution_api_key: Optional[str] = None
    google_calendar_id: Optional[str] = None
    ativo: bool = True
    plano: str = "free"
    preco_mensal: float = 0.00
    max_mensagens_dia: int = 1000
    max_conversas_simultaneas: int = 50
    data_cadastro: datetime
    data_ativacao: Optional[datetime] = None
    data_cancelamento: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    features: Optional[TenantFeaturesModel] = None
    prompts: Optional[TenantPromptsModel] = None
    profissionais: List[ProfissionalModel] = []
    especialidades: List[EspecialidadeModel] = []
    class Config:
        from_attributes = True
