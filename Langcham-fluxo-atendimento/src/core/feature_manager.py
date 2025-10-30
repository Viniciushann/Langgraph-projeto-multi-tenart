import logging
from typing import Any
from src.core.tenant_context import TenantContext

logger = logging.getLogger(__name__)

class FeatureManager:
    def __init__(self, tenant_context: TenantContext):
        self.context = tenant_context

    def pode_usar_transcricao_audio(self) -> bool:
        return self.context.get("feature_transcricao_audio", False)

    def pode_usar_analise_imagem(self) -> bool:
        return self.context.get("feature_analise_imagem", False)

    def pode_usar_rag(self) -> bool:
        return self.context.get("feature_rag_habilitado", False)

    def pode_usar_agendamento(self) -> bool:
        return self.context.get("feature_agendamento_habilitado", False)

    def tem_multi_profissional(self) -> bool:
        return self.context.get("feature_multi_profissional", False)

    def tem_multi_numero(self) -> bool:
        return self.context.get("feature_multi_numero", False)

    def tem_analytics_avancado(self) -> bool:
        return self.context.get("feature_analytics_avancado", False)

    def get_limite_documentos_rag(self) -> int:
        return self.context.get("limite_documentos_rag", 100)

    def get_limite_agendamentos_mes(self) -> int:
        return self.context.get("limite_agendamentos_mes", 500)

    def get_tempo_agrupamento_mensagens(self) -> int:
        return self.context.get("tempo_agrupamento_mensagens", 13)

    def get_max_mensagens_dia(self) -> int:
        return self.context.get("max_mensagens_dia", 1000)

    def get_system_prompt(self) -> str:
        return self.context.get("system_prompt", "")

    def get_nome_assistente(self) -> str:
        return self.context.get("nome_assistente", "Assistente")

    def get_modelo_llm(self) -> str:
        return self.context.get("modelo_llm", "gpt-4o")

    def get_temperatura(self) -> float:
        return self.context.get("temperatura", 0.7)

    def get_max_tokens(self) -> int:
        return self.context.get("max_tokens", 1000)

    def get_profissionais(self) -> list:
        return self.context.get("profissionais", [])

    def get_especialidades(self) -> list:
        return self.context.get("especialidades", [])

    def validar_feature(self, feature_name: str) -> bool:
        feature_map = {
            "transcricao_audio": self.pode_usar_transcricao_audio,
            "analise_imagem": self.pode_usar_analise_imagem,
            "rag": self.pode_usar_rag,
            "agendamento": self.pode_usar_agendamento,
            "multi_profissional": self.tem_multi_profissional,
            "multi_numero": self.tem_multi_numero,
            "analytics": self.tem_analytics_avancado,
        }
        validator = feature_map.get(feature_name)
        if validator:
            return validator()
        logger.warning(f"Feature desconhecida: {feature_name}")
        return False

    def get_mensagem_feature_desabilitada(self, feature_name: str) -> str:
        messages = {
            "transcricao_audio": "Desculpe, a transcrição de áudio não está disponível no seu plano.",
            "analise_imagem": "Desculpe, a análise de imagens não está disponível no seu plano.",
            "rag": "Desculpe, a busca na base de conhecimento não está disponível no seu plano.",
            "agendamento": "Desculpe, o agendamento online não está disponível no seu plano.",
            "multi_profissional": "Este recurso requer upgrade de plano.",
            "analytics": "Analytics avançado disponível apenas em planos superiores.",
        }
        return messages.get(feature_name, "Este recurso não está disponível no seu plano atual.")
